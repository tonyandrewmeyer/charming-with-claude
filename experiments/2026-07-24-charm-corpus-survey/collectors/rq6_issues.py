"""RQ-6: exhaustive issue & PR history mining.

Two phases, both state-tracked, run alternately on the same cron slot:
  Phase A (fetch): paginate ALL issues+PRs (all states) for each repo via
    `gh api repos/{owner}/{name}/issues?state=all&since=<checkpoint>`,
    ~35-40 repos/day. Raw items land in raw/<owner>--<name>.jsonl.
  Phase B (classify): heuristic classification of unclassified raw items into
    classified.jsonl; cross-cutting pattern counting; label-scheme capture.

Labels on items include "bug"/"enhancement" etc. when the repo uses them;
the classifier adds its own category from title/body keywords.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from corpus import RESULTS, iter_repos, load_state, rate_limits, save_state

OUT = RESULTS / "rq6-issues"
RAW = OUT / "raw"
STATE = OUT / "state.json"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
FETCH_BATCH = 38
CLASSIFY_BATCH = 4000
MIN_REMAINING = 300

# regex patterns, matched case-insensitively against title (body excluded:
# too noisy for keyword classification)
CATEGORIES = {
    "bug": (r"\bbug\b|\bbugs\b|traceback|\bexception\b|\bregression\b|\bcrash"
            r"|\bbroken\b|\bfails?\b|\bfailed\b|\bfix\b|\bhotfix\b"),
    "feature": (r"\bfeature\b|\bfeat\b|\brequest\b|\bproposal\b|\brfc\b|\bsupport for\b"
                r"|\badd(ing|s)?\b|\bimplement\b|\benable\b|\ballow\b"),
    "docs": (r"\bdocs?\b|\bdocumentation\b|\breadme\b|\btutorial\b|\bhow[- ]?to\b|\btypo\b"
             r"|\bspelling\b"),
    "ci": (r"\bci\b|\bworkflow\b|\bgithub actions?\b|\btox\b|\blint(ing)?\b|\bpipeline\b"
           r"|\bscheduled (workflow|tests?)\b|\brelease (workflow|process|ci)\b"),
    "deps": (r"\bdependenc(y|ies)\b|\bupgrade\b|\bbump\b|\bpyproject\b|\brequirements\b"
             r"|\brenovate\b|\bdependabot\b|\bpackaging\b|\bpin(ning|ned)?\b|\buv\b"
             r"|\block(file)?\b|supply-chain"),
    "testing": (r"\btests?\b|\btesting\b|\bintegration tests?\b|\bunit tests?\b"
                r"|\bscenario\b|\bjubilant\b|\bharness\b|\bcoverage\b|\bflaky\b"),
    "security": (r"\bsecurity\b|\bcve[-\d]*\b|\bvulnerabilit(y|ies)\b|\brbac\b"
                 r"|\bhardening\b|\bpenetration\b|\bexploit\b"),
    "platform-arm64": (r"\barm64\b|\baarch64\b|\barm\b(?!.*\bcharm\b)"),
    "platform-terraform": (r"\bterraform\b"),
    "platform-cos": (r"\bcos\b|\bgrafana\b|\bprometheus\b|\bloki\b|\balertmanager\b"
                     r"|\bobservability\b|\bmonitoring\b"),
    "platform-backup": (r"\bbackups?\b|\brestore\b|\bsnapshots?\b"),
    "platform-airgap": (r"\bair[- ]?gap(ped)?\b|\boffline\b|\bproxy\b|\bproxied\b"),
    "platform-tls": (r"\btls\b|\bcertificates?\b|\bself-signed\b|\bca cert\b|\bmtls\b"),
    # housekeeping: releases, version bumps, renames — honest category for
    # much of what would otherwise be "uncategorised"
    "chore": (r"\bchore\b|\bprepare (for )?v?[\d.]|\brelease v?[\d.]|\bbump(ing)? version\b"
              r"|\bversion bump\b|\bpre-release\b|\bpost-release\b"),
}
PLATFORM_KEYS = {k for k in CATEGORIES if k.startswith("platform-")}
_COMPILED = {k: re.compile(v, re.IGNORECASE) for k, v in CATEGORIES.items()}

# GitHub labels that override/augment keyword classification
LABEL_MAP = {
    "bug": "bug", "type: bug": "bug", "kind/bug": "bug",
    "enhancement": "feature", "type: enhancement": "feature", "kind/enhancement": "feature",
    "feature": "feature", "feature request": "feature", "type: feature": "feature",
    "documentation": "docs", "docs": "docs", "type: docs": "docs",
    "ci": "ci", "testing": "testing", "tests": "testing",
    "dependencies": "deps", "security": "security",
}


def classify(title: str, labels: list[str]) -> set[str]:
    hits = set()
    for lab in labels:
        mapped = LABEL_MAP.get(lab.lower())
        if mapped:
            hits.add(mapped)
    for cat, rx in _COMPILED.items():
        if rx.search(title):
            hits.add(cat)
    return hits or {"uncategorised"}


def fetch_repo(owner: str, name: str, checkpoint: str | None) -> tuple[int, str]:
    """Fetch issues+PRs (all states) since checkpoint. Returns (count, today).

    Uses `gh api --paginate` with --slurp so each page arrives as a JSON array;
    404s (renamed/deleted/private repos) return 0 items without retrying.
    """
    url = (f"repos/{owner}/{name}/issues?state=all&per_page=100"
           + (f"&since={checkpoint}" if checkpoint else ""))
    out_file = RAW / f"{owner}--{name}.jsonl"
    RAW.mkdir(parents=True, exist_ok=True)
    mode = "a" if checkpoint and out_file.exists() else "w"
    count = 0
    try:
        p = subprocess.run(["gh", "api", "--paginate", url],
                           capture_output=True, text=True, timeout=600)
        if p.returncode != 0:
            return 0, TODAY  # 404 / gone repo — nothing to record
        # --paginate concatenates page JSON arrays back-to-back; decode sequentially
        pages = []
        dec = json.JSONDecoder()
        buf = p.stdout
        idx = 0
        while idx < len(buf):
            while idx < len(buf) and buf[idx] in " \n\r\t":
                idx += 1
            if idx >= len(buf):
                break
            obj, end = dec.raw_decode(buf, idx)
            pages.append(obj)
            idx = end
    except Exception:
        return 0, TODAY
    with out_file.open(mode) as f:
        for items in pages:
            if not isinstance(items, list):
                continue
            for it in items:
                rec = {"repo": f"{owner}/{name}",
                       "number": it.get("number"),
                       "is_pr": "pull_request" in it,
                       "title": it.get("title"),
                       "state": it.get("state"),
                       "state_reason": it.get("state_reason"),
                       "labels": [l.get("name") for l in it.get("labels", []) if isinstance(l, dict)],
                       "comments": it.get("comments"),
                       "created_at": it.get("created_at"),
                       "closed_at": it.get("closed_at"),
                       "author": (it.get("user") or {}).get("login"),
                       "reactions": (it.get("reactions") or {}).get("total_count")}
                f.write(json.dumps(rec, separators=(",", ":")) + "\n")
                count += 1
    return count, TODAY


def phase_fetch(state: dict) -> None:
    rl = rate_limits()
    if rl.get("core", 0) < MIN_REMAINING:
        print(f"rq6: rate limit low ({rl}); skipping fetch")
        return
    universe = [f"{o}/{n}" for o, n, _ in iter_repos()]
    done = state.setdefault("fetched", {})
    pending = [r for r in universe if done.get(r) is None]
    start = state.get("fetch_cursor", 0) % max(len(universe), 1)
    ordered = [universe[(start + i) % len(universe)] for i in range(len(universe))]
    batch = [r for r in ordered if done.get(r) is None][:FETCH_BATCH]
    if not batch:  # full sweep done; start incremental re-sweep
        state["fetched"] = {}
        state["fetch_cursor"] = 0
        print("rq6: sweep complete; restarting incremental fetch next run")
        save_state(STATE, state)
        return
    total = 0
    for full in batch:
        owner, name = full.split("/", 1)
        n, stamp = fetch_repo(owner, name, state.get("last_sweep_start"))
        state["fetched"][full] = stamp
        total += n
    state["fetch_cursor"] = (start + len(batch)) % len(universe)
    save_state(STATE, state)
    remaining = len([r for r in universe if state["fetched"].get(r) is None])
    print(f"rq6: fetched {total} items from {len(batch)} repos; {remaining} repos left this sweep; rate {rate_limits()}")


def phase_classify(state: dict) -> None:
    # watermark = file mtime high-water mark; only re-read files touched since
    # last classify run. Within a file we re-scan and dedupe via the per-run
    # seen-set persisted as repo#number ids (bounded: capped at 200k).
    wm = state.get("classify_watermark", 0.0)
    seen = set(state.get("classified_ids", []))
    new_seen = set()
    counts = {}
    catted = 0
    newest = wm
    classed_out = OUT / "classified.jsonl"
    with classed_out.open("a") as out:
        for f in sorted(RAW.glob("*.jsonl")):
            mt = f.stat().st_mtime
            if mt <= wm and seen:
                continue
            newest = max(newest, mt)
            for line in f.read_text(errors="replace").splitlines():
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                rid = f"{rec['repo']}#{rec['number']}"
                if rid in seen or rid in new_seen:
                    continue
                if catted >= CLASSIFY_BATCH:
                    break
                cats = classify(rec.get("title") or "", rec.get("labels") or [])
                rec["categories"] = sorted(cats)
                rec["cross_cutting"] = sorted(cats & PLATFORM_KEYS)
                out.write(json.dumps(rec, separators=(",", ":")) + "\n")
                for c in cats:
                    counts[c] = counts.get(c, 0) + 1
                new_seen.add(rid)
                catted += 1
    state["classify_watermark"] = newest
    # keep the id set bounded; old ids only matter when a file's mtime is
    # still under the watermark, which means it won't be re-read anyway
    state["classified_ids"] = list(new_seen | (seen if catted < CLASSIFY_BATCH else set()))[-200000:]
    save_state(STATE, state)
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:12]
    print(f"rq6: classified {catted} items; category hits this run: {top}")


def main() -> None:
    state = load_state(STATE, {"fetched": {}, "fetch_cursor": 0, "classified_ids": []})
    phase = state.get("phase", "fetch")
    if phase == "fetch":
        phase_fetch(state)
        state["phase"] = "classify"
    else:
        phase_classify(state)
        state["phase"] = "fetch"
    save_state(STATE, state)


if __name__ == "__main__":
    main()
