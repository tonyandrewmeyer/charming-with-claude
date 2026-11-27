# Charm corpus research — results directory

Daily cron jobs (scripts in `~/charm-research/`, wrappers in `~/.hermes/scripts/`)
accumulate time-series data over the local charm corpus (`~/.cache/hyrum/charms`).
Newest data is appended; every record carries a `date` field (UTC day).

The corpus is refreshed by `hyrum get-charms` at the top of `rq-static-daily.sh`,
from the checkout at `/w/hyrum` — **not** `~/multipass-mounts/hyrum`, which is a
separate tree stuck at 2026-07-04 with an old charm list and a `get-charms` whose
CLI rejects `--workers`. Read "Known data caveats" below before analysing anything.

## Layout

| Dir | RQ | Main artifact | Cadence | gh API? |
|---|---|---|---|---|
| `rq2-supply-chain/` | RQ-2' | `posture.jsonl` | daily full sweep | no |
| `rq4-health/` | RQ-4 | `health.jsonl` | daily ~60-repo batch, round-robin sweep | yes (REST+GraphQL) |
| `rq6-issues/` | RQ-6 | `raw/*.jsonl`, `classified.jsonl` | daily, alternating fetch/classify | yes (REST) |
| `rq7-docs/` | RQ-7 | `docs-audit.jsonl` | daily full sweep | no |
| `rq9-config-actions/` | RQ-9 | `surface.jsonl`, `action-names.json` | daily full sweep | no |
| `rq11-substrate/` | RQ-11 | `substrate.jsonl` | daily full sweep | no |

## Schemas (one JSON object per line)

**rq2 posture.jsonl** — `date, repo, charms, ops, pydantic, style, decl_files[], base,
platforms[], meta_source, dependabot, renovate, security_md, scorecard, head_date`
- `ops`/`pydantic`: version constraint string ("~=2.17", "==3.7.1", "unpinned", null)
- `style`: pylock | uv.lock | poetry.lock | exact-pins | mixed | mostly-unpinned | none-declared

**rq4 health.jsonl** — `date, repo, pushed_at, archived, stars, contributors_sample,
ci_default, issues_open, issues_90d, issues_180d, prs_open, last_commit`
- `issues_90d`/`issues_180d`: open issues created in the last 90/180 days (activity proxy)
- `contributors_sample`: lower bound (per_page=1)
- `ci_default`: conclusion of latest default-branch workflow run

**rq6 raw/<owner>--<name>.jsonl** — one record per issue/PR (all states):
`repo, number, is_pr, title, state, state_reason, labels[], comments, created_at,
closed_at, author, reactions`

**rq6 classified.jsonl** — raw fields + `categories[]` (bug/feature/docs/ci/deps/testing/
security/platform-*) and `cross_cutting[]` (the platform-* subset). Classification is
title-only regex + GitHub-label mapping; bodies excluded as too noisy.

**rq6 llm-classified.jsonl** — LLM re-classification of items the heuristic pass
left `uncategorised`: `date, repo, number, categories[], cross_cutting[], rationale`.
Written by the `rq6-llm-classify` agent cron (not the deterministic collector);
heuristic data is never modified. Progress tracked in `rq6-issues/llm-state.json`.

**rq7 docs-audit.jsonl** — `date, repo, rung (1-4), doc_link, docs_dir,
docs_url_in_readme, readme_bytes, readme_boilerplate, contributing,
contributing_bytes, has_description, has_summary, desc_is_templated, links[], charm_name`
- rung 1 = links.documentation in metadata; 2 = docs/ dir; 3 = docs URL in README; 4 = nothing

**rq9 surface.jsonl** — `date, charm, config_options, config_typed, config_described,
config_secret_typed, secretish_plain[], actions, actions_described,
actions_with_params, action_names[]`
- `secretish_plain`: config keys matching password/token/etc with non-secret type

**rq9 action-names.json** — cumulative `{name: {count, variants[], users[]}}` for the
naming-inconsistency table. Cumulative across runs (counts grow until the file is reset).

**rq11 substrate.jsonl** — `date, charm, base, has_charmcraft_yaml, platforms[], archs[],
arm64, plugins[], framework_ext, other_exts[], type`

## State files

`rq4-health/state.json` (sweep cursor), `rq6-issues/state.json` (fetch cursor +
fetched checkpoints + classify watermark + bounded id set). Deleting a state file
restarts that sweep from scratch; data files are append-only and safe.

## Known data caveats

**The corpus was frozen 2026-07-10 → 2026-08-16.** The static passes only re-derive
what is on disk, and nothing refreshed the clones, so `rq2/rq7/rq9/rq11` rows are
byte-identical across those 24 days — a flat line there means "not collected", not
"ecosystem stable". `rq-static-daily.sh` now runs `hyrum get-charms` first. The
2026-08-17 rows therefore contain ~5 weeks of accumulated change in a single
day-over-day step (235 repos changed in rq2 alone); do not read that as one day's
movement.

**RQ-2 is contaminated by hyrum patcher leftovers.** hyrum's `ops` patcher rewrites
`pyproject.toml` / `uv.lock` / `poetry.lock` / `requirements.txt` in the shared corpus
and does not always revert them — the exact files rq2 reads. Affected repos recorded
hyrum's patch as if it were the charm's own declaration: `canonical/charm-ubuntu` was
logged `ops===3.7.1` / `exact-pins` for the full 25 days, where upstream declares
`ops>=1.0,<2.0`. At least 18 repos were affected (8 that blocked `git pull` — the
mongodb/mongos family, pgbouncer, mlflow, charm-ubuntu, charm-rolling-ops — plus 10+
that merged cleanly and so failed silently: alertmanager-k8s, loki-k8s, charm-microk8s,
mlmd, mlops-libs, mysql-test-app, azure-auth-integrator, charm-simple-streams,
charm-juju-backup-all, charmed-5g-upf-interface). The wrapper now reverts these before
each run, but rows dated 2026-08-17 and earlier still carry the contamination.

**Duplicate dates.** The passes stamp rows with the *UTC* date and blindly append,
while cron fires 05:00 NZ (= 17:00 UTC the day before). Two runs landing on one UTC
date duplicate it — this is why 2026-07-23 is 5x wide. Always dedupe on
`(date, repo)` / `(date, charm)` before analysis. The wrapper now skips a pass that
already has rows for the current UTC date; delete the day's rows first to force a redo.

**git.launchpad.net is unreachable** from this host (plain `curl` times out), so its
119 clones are stale. They are excluded from the research corpus anyway by
`NON_CHARM_OWNERS` in `lib/corpus.py`. The wrapper probes each host and skips rows for
whichever ones do not answer, so they resume automatically if connectivity returns.

## Analysis

There is deliberately no analysis layer baked into the collectors. Read the JSONL
directly (`jq`, pandas) or ask an agent session to summarise — the weekly digest
cron (`rq-digest`, Sundays) writes prose summaries into `digests/`.
