# The collectors

Verbatim copies of the scripts as they ran on the cron host, so the write-up describes the code that actually produced the data. They are excluded from this repository's ruff configuration for that reason; they would not pass it, and reformatting them would make them a description of the collectors rather than the collectors.

They expect a corpus of git clones at `~/.cache/hyrum/charms/<owner>/<repo>` and write JSONL to `~/charm-research/results/`. Both paths are hardcoded in `lib/corpus.py`.

| Script | RQ | API? | Output |
|---|---|---|---|
| `rq2_supply_chain.py` | RQ-2 | no | `rq2-supply-chain/posture.jsonl` |
| `rq4_health.py` | RQ-4 | yes | `rq4-health/health.jsonl` |
| `rq6_issues.py` | RQ-6 | yes | `rq6-issues/raw/*.jsonl`, `classified.jsonl` |
| `rq6_llm_classify.py` | RQ-6 | no | batch/write helper for the agent job |
| `rq7_docs_audit.py` | RQ-7 | no | `rq7-docs/docs-audit.jsonl` |
| `rq9_config_actions.py` | RQ-9 | no | `rq9-config-actions/surface.jsonl` |
| `rq11_substrate.py` | RQ-11 | no | `rq11-substrate/substrate.jsonl` |
| `reclassify_rq6.py` | RQ-6 | no | rebuilds `classified.jsonl` from `raw/` |

`lib/corpus.py` holds everything shared: the corpus walk and charm-root detection, the `charmcraft.yaml` over `metadata.yaml` merge, the dependency-constraint parsers, a `gh api` wrapper with backoff, and the append-only JSONL and state helpers.

Two notes on reading the code rather than the write-up.

`rq6_issues.py` runs one of two phases per invocation and flips a flag in its state file, so fetch and classify alternate days. That is the design decision that let classification fall a whole corpus behind fetch: nothing compares the two cursors, and nothing complains when the gap grows. `reclassify_rq6.py` exists to close it, is deterministic, takes about a minute over 100,544 items, and nobody ran it for five weeks because nothing said it needed running.

`rq11_substrate.py` has a real bug in `extract_archs`. Charms using shorthand platform keys (`ubuntu-24.04-arm64`) produce `build-for` values like `ubuntu@24.04:arm64`, and the `arm64` field tests for a bare `arm64` in the arch set, so it misses them: 149 recorded against 173 actual. `analysis/analyse.py` recounts off the suffix and reports both figures. The collector is left as it ran.
