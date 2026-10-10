"""RQ-6 LLM pass helper: batch reader + result writer.

Two subcommands, invoked by the agent cron job (and by hand for testing):
  python3 rq6_llm_classify.py batch [--size 80]
      Print the next batch of uncategorised items as JSON lines
      (repo, number, is_pr, title, labels) and advance the cursor in state.
  python3 rq6_llm_classify.py write < results.json
      Read agent-produced JSON from stdin and append to llm-classified.jsonl.
      Expected input: a JSON array of {"repo","number","categories":[...]}.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path.home() / "charm-research/results/rq6-issues"
CLASSIFIED = OUT / "classified.jsonl"
LLM_OUT = OUT / "llm-classified.jsonl"
STATE = OUT / "llm-state.json"

VALID = {"bug", "feature", "docs", "ci", "deps", "testing", "security", "chore",
         "platform-arm64", "platform-terraform", "platform-cos", "platform-backup",
         "platform-airgap", "platform-tls", "other"}


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {"done": []}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state))


def pending_items() -> list[dict]:
    done = set(load_state()["done"])
    items = []
    for line in CLASSIFIED.read_text(errors="replace").splitlines():
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if "uncategorised" not in (rec.get("categories") or []):
            continue
        rid = f"{rec['repo']}#{rec['number']}"
        if rid in done:
            continue
        items.append({"repo": rec["repo"], "number": rec["number"],
                      "is_pr": rec["is_pr"], "title": rec.get("title") or "",
                      "labels": rec.get("labels") or []})
    return items


def cmd_batch(size: int) -> None:
    items = pending_items()
    batch = items[:size]
    for it in batch:
        print(json.dumps(it, separators=(",", ":")))
    print(f"# batch of {len(batch)} ({len(items)} total pending)", file=sys.stderr)


def cmd_write() -> None:
    raw = sys.stdin.read()
    try:
        results = json.loads(raw)
        if not isinstance(results, list):
            raise ValueError("expected a JSON array")
    except Exception as e:
        print(f"write: bad input: {e}", file=sys.stderr)
        sys.exit(1)
    state = load_state()
    done = set(state["done"])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    n = 0
    with LLM_OUT.open("a") as f:
        for r in results:
            repo, number = r.get("repo"), r.get("number")
            cats = sorted({c for c in (r.get("categories") or []) if c in VALID})
            if not repo or number is None or not cats:
                continue
            rid = f"{repo}#{number}"
            rec = {"date": today, "repo": repo, "number": number,
                   "categories": cats,
                   "cross_cutting": sorted(c for c in cats if c.startswith("platform-")),
                   "rationale": r.get("rationale", "")[:200]}
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")
            done.add(rid)
            n += 1
    state["done"] = sorted(done)
    save_state(state)
    print(f"write: appended {n} records, {len(done)} total done")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == "batch":
        size = 80
        if "--size" in sys.argv:
            size = int(sys.argv[sys.argv.index("--size") + 1])
        cmd_batch(size)
    elif sys.argv[1] == "write":
        cmd_write()
    else:
        print(__doc__)
        sys.exit(2)
