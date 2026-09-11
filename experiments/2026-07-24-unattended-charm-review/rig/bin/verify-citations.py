#!/usr/bin/env python3
"""Check every `file:line` citation in a review against the actual source.

Both smoke tests produced reviews whose findings were substantively right but whose
line numbers were wrong (catalogue-k8s cited charm.py:348 for a json.loads that is
at 325). Asking the model to be more careful is not a control; checking is.

Two checks:
  1. the cited line exists in the cited file at all
  2. where the finding quotes the offending code, that quote actually appears at or
     near the cited line — this is the check that catches a plausible-but-wrong
     line number, which check 1 cannot

Usage: verify-citations.py <review.md> <repo-root> [dep-root ...]
Prints a report; exits 1 if anything is wrong, so the caller can feed it back.

Extra roots hold the charm's declared dependencies, unpacked by bin/fetch-deps.py. They
matter because a thin-wrapper charm keeps its logic in a PyPI distribution rather than in
the checkout, so citations into the code worth reviewing land outside the repo. Indexing
only the repo made those read as "no such file in the repo" — opensearch-dashboards
scored `citations checked: 0, problems: 9` on 2026-08-02 with all nine citations correct,
and the correction passes were spent re-deriving line numbers rather than fixing errors.
The repo is searched first so a file present in both resolves to the reviewed copy.
"""
import re
import sys
import pathlib

CITE = re.compile(r"`([\w./-]+\.(?:py|yaml|yml|ini|toml|cfg|md|sh|tf)):(\d+)(?:-(\d+))?`")
# A citation names a *construct* — "`src/charm.py:277` — `_holistic_handler`" — and the
# Evidence then quotes a line from inside it. A tolerance of 5 assumed the citation named a
# line, so it flagged the ordinary case: across the 141-review corpus the false positives
# cluster 6-10 lines out (authentik `charm.py:277` vs its `except PebbleError:` at 283,
# kserve `charm.py:204` vs `return self._resource_handler` at 214), all of them citations a
# reader would follow and land in the right place. The error this check exists to catch is
# a plausible-but-wrong line number, and the founding example — catalogue-k8s citing 348
# for a json.loads at 325 — is 23 lines out, so 15 forgives the construct-body pattern and
# still catches that with margin. It is the one tuned number here: raising it toward 23
# trades missed errors for quieter reports, lowering it back toward 5 does the reverse.
NEAR = 15
# A lone `some_method()`/`some_name` is the *name* of a thing, not evidence that it
# lives on a particular line, and treating it as evidence produced a systematic false
# positive: `foo()` substring-matches the call site `self.foo()` but NOT the definition
# `def foo(self, ...)`, so a finding that correctly cited where a method is DEFINED was
# reported as wrong and pointed at its caller instead. Six of postgresql-k8s's eight
# reported problems were this, all correct citations; the fix agents on prometheus-k8s
# and alertmanager-k8s independently worked out the checker was at fault and said so in
# their logs. Only undotted names are excluded — the def/call asymmetry that causes this
# cannot arise for a dotted chain like `self.ingress.on.ready`, so those stay checked.
BARE_NAME = re.compile(r"[A-Za-z_]\w*(\(\))?")


def index_root(root):
    by_path, by_name = {}, {}
    for p in root.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        by_path[str(p.relative_to(root))] = p
        by_name.setdefault(p.name, []).append(p)
    return {"root": root, "by_path": by_path, "by_name": by_name}


def resolve(ref, indexes):
    """Resolve a citation against each root in turn. Returns (path, index) or (None, None).

    Roots are tried in order and the repo is first, so a name that exists both in the
    checkout and in a vendored dependency resolves to the copy under review.
    """
    name = pathlib.Path(ref).name
    for idx in indexes:
        if ref in idx["by_path"]:
            return idx["by_path"][ref], idx
        # reviewers often cite a bare or partial path; accept it when unambiguous
        cands = idx["by_name"].get(name, [])
        if len(cands) == 1:
            return cands[0], idx
        tail = [p for p in cands if str(p).endswith(ref)]
        if len(tail) == 1:
            return tail[0], idx
    return None, None


def shown(target, idx):
    """Path as the reader should see it: dependency files are labelled as such."""
    rel = target.relative_to(idx["root"])
    return f"{rel} (dependency)" if idx.get("is_dep") else str(rel)


def quotes_in(block):
    """Code the finding quotes as evidence: fenced blocks and inline backticks."""
    out = []
    for fence in re.findall(r"```[\w]*\n(.*?)```", block, re.S):
        out += [ln.strip() for ln in fence.splitlines()]
    for span in re.findall(r"`([^`\n]{12,})`", block):
        out.append(span.strip())
    # a bare identifier or a path is not evidence of a line
    return [
        q
        for q in out
        if len(q) >= 12 and not CITE.fullmatch(f"`{q}`") and not BARE_NAME.fullmatch(q)
    ]


def main() -> int:
    review, repo = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    if not review.exists():
        print(f"no review at {review}")
        return 1
    text = review.read_text(errors="replace")
    indexes = [index_root(repo)]
    for extra in sys.argv[3:]:
        p = pathlib.Path(extra)
        if p.is_dir():
            idx = index_root(p)
            idx["is_dep"] = True
            indexes.append(idx)

    problems, checked = [], 0
    # Walk finding blocks. Attribution has to be precise or the report cries wolf:
    # pair the `**Where**` citation with the `**Evidence**` quote of the SAME finding.
    # Only fall back to whole-block matching when the block has a single citation.
    blocks = re.split(r"\n(?=### )", text)
    for block in blocks:
        # `(.*)` without re.S stops at the newline, and a Where field with three or four
        # labelled citations wraps. hardware-observer-operator's wrapped onto a second line
        # and its `src/charm.py:340` was simply never parsed, so the quote that belonged to
        # it could not be accounted for by any citation the checker could see. Bound it the
        # same way Evidence is bounded, at the next bullet or the next finding.
        where = re.search(r"\*\*Where\*\*:(.*?)(?=\n- \*\*|\n### |\Z)", block, re.S)
        evidence = re.search(r"\*\*Evidence\*\*:(.*?)(?=\n- \*\*|\n### |\Z)", block, re.S)
        if where and evidence:
            cites = list(CITE.finditer(where.group(1)))
            qs = quotes_in(evidence.group(1))
        else:
            cites = list(CITE.finditer(block))
            qs = quotes_in(block) if len(cites) == 1 else []
        if not cites:
            continue
        # check 1 is per citation: a cited line either exists in the cited file or does
        # not, and no other citation can excuse it.
        resolved = []  # (match, start, end, path, index, lines) for the ones worth check 2
        for m in cites:
            ref, start = m.group(1), int(m.group(2))
            end = int(m.group(3) or start)
            target, idx = resolve(ref, indexes)
            if target is None:
                if not any(pathlib.Path(ref).name in i["by_name"] for i in indexes):
                    problems.append(f"{m.group(0)} — no such file in the repo")
                continue
            try:
                lines = target.read_text(errors="replace").splitlines()
            except Exception as e:
                problems.append(f"{m.group(0)} — unreadable ({e})")
                continue
            checked += 1
            if start < 1 or end > len(lines):
                problems.append(
                    f"{m.group(0)} — {shown(target, idx)} has {len(lines)} lines"
                )
                continue
            resolved.append((m, start, end, target, idx, lines))

        # check 2 is per *finding*, not per citation. A finding routinely cites several
        # places and labels each one — hardware-observer-operator (2026-09-01) had
        # `charm.py:51-56` (registered handlers), `charm.py:69` (the assignment) and
        # `charm.py:340` (the property), all three correct. Judging every citation against
        # the same Evidence quote reported two of them wrong for not containing a line they
        # never claimed, and the fix pass was then asked to "correct" citations that were
        # already right. That is the same cry-wolf failure the BARE_NAME rule above exists
        # to stop, one level up: there the unit of evidence was too small, here the unit of
        # attribution is too narrow. So ask the question the finding actually answers —
        # does *any* citation in this finding account for this quote? — and only flag the
        # quote when none of them does. A single-citation finding is the original case and
        # behaves exactly as before: one citation, one window, quote at 325 vs cite at 348
        # still fires.
        # Citations into the same file delimit the region of it the finding is about, and
        # evidence quoted from inside that region is attributed to the finding. A finding
        # that cites `service.py:465` (a function) and `service.py:503` (its call site) and
        # quotes the `raise` at 472 from inside that function is doing the ordinary thing;
        # NEAR alone, measured from each citation separately, called that wrong. A finding
        # with one citation gets no widening at all — the span is a point — so the original
        # catch (cite 348, json.loads at 325) still fires exactly as it did.
        spans = {}
        for m, start, end, target, idx, lines in resolved:
            lo, hi = spans.get(target, (start, end))
            spans[target] = (min(lo, start), max(hi, end))
        for q in qs:
            hits, where_seen, accounted = [], [], False
            for m, start, end, target, idx, lines in resolved:
                h = [i + 1 for i, ln in enumerate(lines) if q and q in ln]
                if not h:
                    continue
                lo, hi = spans[target]
                if any(lo - NEAR <= x <= hi + NEAR for x in h):
                    accounted = True
                    break
                hits += h
                where_seen.append(f"{m.group(0)} → {shown(target, idx)}")
            if accounted or not hits:
                continue  # attributed, or the quote is paraphrased and not judgeable
            problems.append(
                f"{', '.join(dict.fromkeys(where_seen))} — quoted code {q[:48]!r} is at "
                f"line(s) {sorted(set(hits))[:4]}, outside every line this finding cites"
            )
            break  # one report per finding: the fix pass re-reads the whole block anyway

    print(f"citations checked: {checked}, problems: {len(problems)}")
    for p in problems:
        print(f"  BAD  {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
