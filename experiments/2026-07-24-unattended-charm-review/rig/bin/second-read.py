#!/usr/bin/env python3
"""Second reader: adjudicate every finding in the corpus against the cited source.

WHY THIS EXISTS
The rig has always checked that a citation *resolves* (verify-citations.py: does the
cited line exist, does the quote appear near it). It has never checked whether the
claim built on that citation is *true*. Those are different questions, and only the
second one decides whether a review is worth anything to a maintainer.

The 2026-08-09 corpus audit quantified the gap and then stopped: of 152 flagged
citation residuals only ~35 looked like real errors, because verify-citations.py tests
every citation against every quote within a finding, so a `**Where**` line naming
several locations flags all but one. Nobody ever adjudicated those 35. This does.

WHAT IT IS NOT
It does not re-review the charm. It reads the finding and the code the finding points
at, and asks one question: does this code support this claim? That is deliberately
narrower than a review, and it is the part that can be done without a juju controller,
without the run lock, and therefore without a cron slot -- which is the whole reason
this can run while the main queue is still working through its tail.

DESIGN NOTES
* Direct HTTPS to OpenRouter, not `pi`. The model gets no tools and no filesystem: it
  sees only the excerpts this script chose. That makes the cost per review predictable
  (no agent loop) and means a second reader cannot mutate the shared source cache that
  prepare.sh clones from.
* Source comes from /home/ubuntu/.cache/hyrum/charms (depth-1 clones, `path` column of
  queue.tsv), never from work/ -- run-review.sh does `rm -rf "$WS"` on that directory
  at the top of every slot.
* Resumable by construction: one JSON per repo, skipped if present. Kill it at any
  point and re-run.
* Spend is read back from OpenRouter's own `usage.cost` on each reply, not estimated.
  Same lesson as pricing a model: bill a real request and read what it says.

Usage:
  second-read.py            [--max-spend 25] [--model ...] [--workers 4] [--limit N]
  second-read.py --report   write ERRATA.md from whatever JSON exists so far
"""
import argparse
import concurrent.futures
import csv
import json

import pathlib
import re
import sys
import threading
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path("/home/ubuntu/charm-review")
OUT = ROOT / "audit" / "20260830"
AUTH = pathlib.Path("/home/ubuntu/.pi/agent/auth.json")
API = "https://openrouter.ai/api/v1/chat/completions"
KEY_API = "https://openrouter.ai/api/v1/key"

# Citations look like `src/charm.py:72-84`. Same shape verify-citations.py matches, kept
# separate on purpose: that script is load-bearing for the review loop and this one is not.
CITE = re.compile(r"`([\w./-]+\.(?:py|yaml|yml|ini|toml|cfg|md|sh|tf)):(\d+)(?:[-–](\d+))?`")
CONTEXT = 35  # lines either side of a cited line to show the adjudicator

VERDICTS = ("supported", "contradicted", "miscited", "runtime", "unverifiable")

# `| Repo | canonical/foo @ `abc1234` (2026-07-21) |` -- the backticks are present in most
# reviews and absent in ~25, so they are optional here.
HEADER_REV = re.compile(r"\|\s*Repo\s*\|[^|]*?@\s*`?([0-9a-f]{7,40})`?")


def cache_matches_review(text, repo_root):
    """Is the checkout we are about to read the same code the reviewer read?

    This is the assumption the whole pass rests on, so it is measured rather than
    trusted: if the cache had moved on since the review was written, every line number
    would have drifted and honest findings would come back `miscited` in bulk -- a
    confident, systematic, completely wrong result. Returns "yes"/"no"/"unknown".
    """
    m = HEADER_REV.search(text[:4000])
    if not m:
        return "unknown", None
    rev = m.group(1)
    try:
        import subprocess
        head = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=30
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown", rev
    if not head:
        return "unknown", rev
    n = min(len(rev), len(head))
    return ("yes" if rev[:n] == head[:n] else "no"), rev


# ---- parsing -----------------------------------------------------------------
def parse_review(text):
    """-> (verdict_paragraph, [finding dicts]).

    The corpus is machine-written to a fixed template, so this is a parser rather than
    a heuristic: `## Findings`, then `### title` per finding, then `- **Field**: value`
    bullets. A review that does not match returns no findings and is reported as such
    rather than silently counted as clean -- an empty result that looks like a pass is
    the exact failure shape RESUME.md keeps warning about.
    """
    head = text.split("## Findings", 1)
    verdict = ""
    m = re.search(r"\*\*Verdict\*\*:(.+?)(?:\n\n|\n\|)", head[0], re.S)
    if m:
        verdict = " ".join(m.group(1).split())
    if len(head) < 2:
        return verdict, []
    # Stop at the next level-2 heading. All 136 reviews carry `## Findings` followed by
    # `## Tests`/`## Docs`/etc, so the section is well delimited -- but splitting on the
    # `---` rules *between* findings is not safe, because only some reviews use them, and
    # doing that silently returned one finding per review (159 across the corpus instead
    # of ~1250). Split on the `###` headings themselves, which every review does have.
    body = re.split(r"\n## ", head[1], 1)[0]
    findings = []
    for chunk in re.split(r"\n(?=###\s)", body):
        m = re.match(r"###\s+(.+?)\s*$", chunk.strip().split("\n", 1)[0])
        if not m:
            continue
        f = {"title": m.group(1).strip(), "raw": chunk.strip()}
        for field in ("Severity", "Kind", "Where", "Evidence", "Impact", "Fix"):
            fm = re.search(
                r"^-\s+\*\*%s\*\*:\s*(.+?)(?=\n-\s+\*\*|\Z)" % field, chunk, re.M | re.S
            )
            f[field.lower()] = " ".join(fm.group(1).split()) if fm else ""
        findings.append(f)
    return verdict, findings


_IDX_SKIP = ("/.git/", "/.tox/", "/venv/", "/.venv/", "site-packages", "node_modules", "/build/")
_idx_cache = {}
_idx_lock = threading.Lock()


def _file_index(repo_root):
    key = str(repo_root)
    with _idx_lock:
        if key in _idx_cache:
            return _idx_cache[key]
    m = {}
    for p in repo_root.rglob("*"):
        s = str(p)
        if any(k in s for k in _IDX_SKIP):
            continue
        if p.is_file():
            m.setdefault(p.name, []).append(p)
    with _idx_lock:
        _idx_cache[key] = m
    return m


def find_by_suffix(repo_root, rel):
    """Resolve a citation whose path is written relative to the charm, not the repo root.

    Reviews cite what the reviewer was looking at, and inside a charm directory that is
    `charm.py:89`, not `src/charm.py:89`. Resolving only from the repo root made 250
    citations read as "no such file", and because the adjudicator then had no excerpt it
    called them *miscited* -- 11 of sloth-k8s-operator's 15 findings, a review whose
    citations are in fact fine. That is a systematic false positive manufactured entirely
    by this script, and exactly the failure this audit was built to catch in others.

    Prefer a path-suffix match (`src/charm.py` for `charm.py`), then a unique basename.
    Where several candidates remain -- 40 citations, nearly all in monorepos like
    mysql-operators and pyroscope-operators -- this PICKS the shallowest rather than
    abstaining, so it can hand the adjudicator the wrong `charm.py` and manufacture a
    verdict. That is the one way this fix can make things worse, so the excerpt is
    labelled `charm.py -> charms/foo/src/charm.py` and the adjudicator can see what it
    actually got. Treat an error in a multi-charm repo as needing a human before acting.
    """
    idx = _file_index(repo_root)
    cands = idx.get(pathlib.PurePath(rel).name, [])
    if not cands:
        return None
    suffix = [c for c in cands if str(c).endswith("/" + rel)]
    pool = suffix or cands
    if len(pool) == 1:
        return pool[0]
    return sorted(pool, key=lambda c: (len(c.parts), str(c)))[0]


def excerpts_for(finding, repo_root):
    """Resolve the finding's citations to real source, with context.

    Returns (list of excerpt strings, list of unresolved citation strings). A citation
    under deps/ is expected to be unresolved: fetch-deps.py unpacks PyPI distributions
    into the per-run workspace, which is deleted after the run, so the dependency source
    a thin-wrapper charm actually cites is simply not retained anywhere. That is a real
    limit of this pass and is reported, not papered over.
    """
    seen, out, missing = set(), [], []
    for field in ("where", "evidence"):
        for m in CITE.finditer(finding.get(field, "")):
            rel, start = m.group(1), int(m.group(2))
            end = int(m.group(3)) if m.group(3) else start
            if (rel, start, end) in seen:
                continue
            seen.add((rel, start, end))
            p = (repo_root / rel).resolve()
            try:
                p.relative_to(repo_root.resolve())
            except ValueError:
                missing.append(f"{rel}:{start} (path escapes the repo)")
                continue
            if not p.is_file():
                p = find_by_suffix(repo_root, rel)
                if p is None:
                    missing.append(f"{rel}:{start} (no such file in the checkout)")
                    continue
            try:
                lines = p.read_text(errors="replace").splitlines()
            except OSError as e:
                missing.append(f"{rel}:{start} ({e})")
                continue
            lo, hi = max(1, start - CONTEXT), min(len(lines), end + CONTEXT)
            if start > len(lines):
                missing.append(f"{rel}:{start} (file has only {len(lines)} lines)")
                continue
            numbered = "\n".join(
                f"{i:>5}| {lines[i - 1]}" for i in range(lo, hi + 1)
            )
            try:
                shown_as = str(p.relative_to(repo_root.resolve()))
            except ValueError:
                shown_as = rel
            label = rel if shown_as == rel else f"{rel} -> {shown_as}"
            out.append(f"--- {label}  (cited {start}-{end}, showing {lo}-{hi}) ---\n{numbered}")
    return out, missing


# ---- prompting ---------------------------------------------------------------
SYSTEM = """You are a second reader auditing an automated code review of a Juju charm.

For each finding you are given the finding text and the source the finding cites, with
real line numbers. Decide whether the cited code supports the claim.

Answer for every finding with exactly one verdict:
  supported     - the cited code says what the finding says it says
  contradicted  - the cited code shows the finding is wrong
  miscited      - the claim may well be true, but this citation points somewhere that
                  does not show it (wrong line, wrong file, or the quoted code is absent)
  runtime       - the claim rests on observed deployment behaviour (juju status, hook
                  errors, debug-log output, timings), which source code cannot settle
  unverifiable  - no usable excerpt was supplied, so you cannot judge

Rules that matter more than being decisive:
* Judge ONLY from the excerpts given. You have no other access to this repository.
* If an excerpt is missing or too small to settle the point, say unverifiable. Do not
  reason from the plausibility of the claim -- a confident guess is the failure mode
  this audit exists to catch.
* A finding about a missing test, missing handler, or absent code is checkable only if
  the excerpt would have contained the thing said to be missing. Otherwise: unverifiable.
* "runtime" is not a criticism. Most deployment findings are legitimately runtime.
* Reserve "contradicted" for a claim the excerpt actually refutes.

Return ONLY a JSON object, no prose and no code fences:
{"findings":[{"n":1,"verdict":"supported","confidence":"high|medium|low",
              "note":"one sentence, <=200 chars, what the code shows"}],
 "review_note":"one sentence on the review's overall reliability, <=300 chars"}
Use the same "n" numbers you were given, one entry per finding, in order."""


# Source budget for one request, in characters. Reviews carry a mean of 17.8 findings and
# some carry 34, each with up to four cited excerpts of ~70 numbered lines -- unbudgeted
# that is a quarter of a million characters and the request stops being cheap or reliable.
# The budget is shared across the whole review and spent in finding order, so an
# over-large review loses context off its tail rather than failing; anything squeezed out
# arrives at the adjudicator as "NONE AVAILABLE" and comes back `unverifiable`, which is
# the honest answer rather than a guess. TAIL_MIN keeps a floor for the last findings.
SRC_BUDGET = 90_000
PER_FINDING_MAX = 12_000


def build_user(repo, verdict, findings, packs):
    parts = [f"Charm repo: {repo}", f"Review verdict: {verdict[:1200]}", ""]
    budget = SRC_BUDGET
    share = max(1500, SRC_BUDGET // max(1, len(findings)))
    for i, (f, (exs, missing)) in enumerate(zip(findings, packs), 1):
        parts.append(f"=== FINDING {i} ===")
        parts.append(f"Title: {f['title']}")
        parts.append(f"Severity: {f.get('severity','')}   Kind: {f.get('kind','')}")
        parts.append(f"Where: {f.get('where','')[:800]}")
        parts.append(f"Evidence: {f.get('evidence','')[:2500]}")
        if f.get("impact"):
            parts.append(f"Impact: {f['impact'][:600]}")
        if missing:
            parts.append("Citations that could not be resolved: " + "; ".join(missing[:6]))
        allow = min(PER_FINDING_MAX, max(share, budget // 2) if budget > 0 else 0)
        shown = []
        for e in exs[:4]:
            if allow <= 0:
                break
            piece = e[:allow]
            shown.append(piece)
            allow -= len(piece)
            budget -= len(piece)
        if shown:
            parts.append("Cited source:")
            parts.extend(shown)
        else:
            parts.append("Cited source: NONE AVAILABLE")
        parts.append("")
    return "\n".join(parts)


# ---- api ---------------------------------------------------------------------
_spend_lock = threading.Lock()
_spend = 0.0


def api_key():
    d = json.loads(AUTH.read_text())
    return d["openrouter"]["key"]


def key_remaining(key):
    req = urllib.request.Request(KEY_API, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["data"].get("limit_remaining")


def call(key, model, system, user, max_tokens=6000):
    """One chat completion. Returns (text, cost). Raises on a hard refusal.

    Retries only what is worth retrying: 429 and 5xx. A 403 carrying a budget message is
    reraised immediately -- the same distinction run-review.sh draws, because moderation
    also answers 403 and that one is not about money.
    """
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": 0,
            "usage": {"include": True},
        }
    ).encode()
    last = None
    for attempt in range(4):
        req = urllib.request.Request(
            API,
            data=payload,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.load(r)
            ch = (d.get("choices") or [{}])[0]
            txt = (ch.get("message") or {}).get("content") or ""
            fin = ch.get("finish_reason") or ""
            cost = float((d.get("usage") or {}).get("cost") or 0.0)
            return txt, cost, fin
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:400]
            last = f"{e.code}: {body}"
            if e.code == 403 or e.code == 402:
                raise RuntimeError(f"provider refused: {last}")
            if e.code not in (408, 409, 429) and e.code < 500:
                raise RuntimeError(last)
        except Exception as e:  # noqa: BLE001 - transport, retried below
            last = repr(e)
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"gave up after retries: {last}")


def extract_json(txt):
    """Models sometimes fence the JSON despite being told not to."""
    t = txt.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n", "", t)
        t = re.sub(r"\n```\s*$", "", t)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", t, re.S)
        if m:
            return json.loads(m.group(0))
        raise


# ---- driver ------------------------------------------------------------------
def repo_paths():
    paths = {}
    with open(ROOT / "queue.tsv") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            paths[row["repo"]] = pathlib.Path(row["path"])
    return paths


def audit_one(review_path, paths, key, model, max_spend):
    global _spend
    repo = review_path.stem
    dest = OUT / f"{repo}.json"
    if dest.exists():
        return ("skip", repo, 0.0)
    src = paths.get(repo)
    text = review_path.read_text(errors="replace")
    verdict, findings = parse_review(text)
    if not findings:
        dest.write_text(json.dumps(
            {"repo": repo, "status": "no-findings-parsed", "bytes": len(text)}, indent=2))
        return ("noparse", repo, 0.0)
    if src is None or not src.is_dir():
        dest.write_text(json.dumps(
            {"repo": repo, "status": "no-source-checkout", "findings": len(findings)},
            indent=2))
        return ("nosrc", repo, 0.0)

    match, rev = cache_matches_review(text, src)
    packs = [excerpts_for(f, src) for f in findings]
    with _spend_lock:
        if _spend >= max_spend:
            return ("budget", repo, 0.0)
    user = build_user(repo, verdict, findings, packs)
    # One entry of JSON per finding, and the corpus runs to 34 findings on its worst
    # review. The first pilot lost data-integrator (23 findings) to an EMPTY reply that
    # still billed $0.14 -- `finish_reason: length`, the answer cut off before any content
    # survived. Size the ceiling off the finding count and record finish_reason, so a
    # truncated answer is visible as truncation rather than as an unparseable model.
    want = min(24000, 2000 + 260 * len(findings))
    txt, cost, fin = call(key, model, SYSTEM, user, max_tokens=want)
    if (not txt.strip() or fin == "length") and want < 24000:
        txt2, cost2, fin = call(key, model, SYSTEM, user, max_tokens=24000)
        txt, cost = txt2, cost + cost2
    with _spend_lock:
        _spend += cost
    try:
        parsed = extract_json(txt)
    except Exception as e:  # noqa: BLE001
        dest.write_text(json.dumps(
            {"repo": repo, "status": "unparseable-reply", "error": repr(e),
             "finish_reason": fin, "findings": len(findings),
             "reply": txt[:4000], "cost": cost}, indent=2))
        return ("badreply", repo, cost)

    verdicts = {v["n"]: v for v in parsed.get("findings", []) if isinstance(v, dict) and "n" in v}
    out = {
        "repo": repo, "status": "ok", "model": model, "cost": round(cost, 5),
        "review_bytes": len(text), "findings_total": len(findings),
        "reviewed_commit": rev, "cache_matches_review": match,
        "review_note": parsed.get("review_note", ""),
        "findings": [],
    }
    for i, (f, (exs, missing)) in enumerate(zip(findings, packs), 1):
        v = verdicts.get(i, {})
        ver = v.get("verdict", "unverifiable")
        # The prompt says "no usable excerpt -> unverifiable" and the model does not always
        # obey it: 54 findings came back `miscited` with nothing to miscite against. A rule
        # this important is enforced in code, not asked for in a prompt.
        if not exs and ver in ("miscited", "contradicted", "supported"):
            ver = "unverifiable"
        out["findings"].append({
            "n": i, "title": f["title"], "severity": f.get("severity", ""),
            "kind": f.get("kind", ""), "where": f.get("where", "")[:400],
            "verdict": ver if ver in VERDICTS else "unverifiable",
            "confidence": v.get("confidence", ""),
            "note": (v.get("note") or "")[:400],
            "excerpts": len(exs), "unresolved": missing[:6],
        })
    dest.write_text(json.dumps(out, indent=2))
    return ("ok", repo, cost)


def write_report():
    rows = []
    for p in sorted(OUT.glob("*.json")):
        try:
            rows.append(json.loads(p.read_text()))
        except Exception:  # noqa: BLE001
            continue
    ok = [r for r in rows if r.get("status") == "ok"]
    for r in ok:
        for f in r["findings"]:
            if not f.get("excerpts") and f["verdict"] in ("miscited", "contradicted", "supported"):
                f["verdict"] = "unverifiable"
                f["note"] = "[no excerpt was resolved; verdict forced] " + f.get("note", "")
    counts = {v: 0 for v in VERDICTS}
    for r in ok:
        for f in r["findings"]:
            counts[f["verdict"]] = counts.get(f["verdict"], 0) + 1
    total = sum(counts.values())

    def bad(r):
        return [f for f in r["findings"] if f["verdict"] in ("contradicted", "miscited")]

    ranked = sorted(ok, key=lambda r: (-len(bad(r)), r["repo"]))
    L = []
    L.append("# Second-reader errata — corpus audit 2026-08-30\n")
    L.append(
        "Every finding in the corpus re-read against the source it cites. This asks one\n"
        "question only — *does the cited code support the claim* — and deliberately not\n"
        "whether the review found everything it should have. Judged from the cited\n"
        "excerpts alone, with no other access to the repository, so a finding whose\n"
        "excerpt could not settle the point is marked `unverifiable` rather than guessed.\n"
    )
    L.append(f"\n**{len(ok)} reviews adjudicated, {total} findings.**\n")
    L.append("| verdict | findings | share |")
    L.append("|---|---:|---:|")
    for v in VERDICTS:
        c = counts.get(v, 0)
        L.append(f"| {v} | {c} | {(100.0 * c / total if total else 0):.1f}% |")
    L.append("")
    other = [r for r in rows if r.get("status") != "ok"]
    if other:
        L.append("## Reviews not adjudicated\n")
        for r in other:
            L.append(f"- `{r['repo']}` — {r.get('status')}")
        L.append("")
    L.append("## Reviews ranked by adjudicated errors\n")
    L.append("| repo | findings | contradicted | miscited | runtime | unverifiable |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for r in ranked:
        c = {v: 0 for v in VERDICTS}
        for f in r["findings"]:
            c[f["verdict"]] = c.get(f["verdict"], 0) + 1
        L.append(
            f"| {r['repo']} | {r['findings_total']} | {c['contradicted']} | "
            f"{c['miscited']} | {c['runtime']} | {c['unverifiable']} |"
        )
    L.append("\n## Every contradicted or miscited finding\n")
    for r in ranked:
        b = bad(r)
        if not b:
            continue
        L.append(f"### {r['repo']}\n")
        if r.get("review_note"):
            L.append(f"*{r['review_note']}*\n")
        for f in b:
            L.append(f"- **{f['verdict']}** ({f['confidence']}) — {f['title']}")
            L.append(f"  - Where: {f['where']}")
            L.append(f"  - Second reader: {f['note']}")
            if f["unresolved"]:
                L.append(f"  - Unresolved citations: {'; '.join(f['unresolved'])}")
        L.append("")
    (OUT / "ERRATA.md").write_text("\n".join(L) + "\n")
    return len(ok), total, counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="anthropic/claude-sonnet-5")
    ap.add_argument("--max-spend", type=float, default=25.0)
    ap.add_argument("--floor", type=float, default=60.0,
                    help="stop if the key drops below this, so the review queue's tail is never at risk")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    if a.report:
        n, t, c = write_report()
        print(f"report: {n} reviews, {t} findings, {c}")
        return 0

    key = api_key()
    start = key_remaining(key)
    print(f"key limit_remaining ${start:.2f}; spending at most ${a.max_spend:.2f}, floor ${a.floor:.2f}")
    if start is not None and start - a.max_spend < a.floor:
        print("refusing to start: max-spend would take the key below the floor", file=sys.stderr)
        return 2

    paths = repo_paths()
    reviews = sorted((ROOT / "reviews").glob("*.md"))
    if a.only:
        want = set(a.only.split(","))
        reviews = [p for p in reviews if p.stem in want]
    todo = [p for p in reviews if not (OUT / f"{p.stem}.json").exists()]
    if a.limit:
        todo = todo[: a.limit]
    print(f"{len(reviews)} reviews, {len(todo)} to do")

    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(audit_one, p, paths, key, a.model, a.max_spend): p for p in todo}
        for fut in concurrent.futures.as_completed(futs):
            p = futs[fut]
            try:
                kind, repo, cost = fut.result()
            except Exception as e:  # noqa: BLE001
                print(f"  ERROR {p.stem}: {e}", file=sys.stderr)
                continue
            done += 1
            print(f"  [{done}/{len(todo)}] {kind:<8} {repo:<45} ${cost:.4f}  (spent ${_spend:.2f})")
            if _spend >= a.max_spend:
                print("hit max-spend, stopping", file=sys.stderr)
                for f2 in futs:
                    f2.cancel()
                break

    end = key_remaining(key)
    print(f"spent ${_spend:.2f} (key ${start:.2f} -> ${end:.2f})")
    n, t, c = write_report()
    print(f"report: {n} reviews, {t} findings, {c}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
