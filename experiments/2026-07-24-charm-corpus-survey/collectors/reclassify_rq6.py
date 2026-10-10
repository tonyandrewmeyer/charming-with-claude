"""One-off: reclassify all raw RQ-6 records with the current CATEGORIES.

Rewrites classified.jsonl from raw/*.jsonl (deterministic; safe to re-run).
Used after category-set changes (e.g. adding 'chore').
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import rq6_issues as m


def main() -> None:
    total = 0
    counts = collections.Counter()
    with (m.OUT / "classified.jsonl").open("w") as f:
        for path in sorted(m.RAW.glob("*.jsonl")):
            for line in path.read_text(errors="replace").splitlines():
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                cats = m.classify(rec.get("title") or "", rec.get("labels") or [])
                rec["categories"] = sorted(cats)
                rec["cross_cutting"] = sorted(cats & m.PLATFORM_KEYS)
                f.write(json.dumps(rec, separators=(",", ":")) + "\n")
                for c in cats:
                    counts[c] += 1
                total += 1
    print(f"reclassified {total} records")
    print(counts.most_common(16))


if __name__ == "__main__":
    main()
