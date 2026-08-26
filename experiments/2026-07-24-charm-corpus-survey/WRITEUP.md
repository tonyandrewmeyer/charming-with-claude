# Experiment: a daily survey of the charm corpus

**Dates:** 2026-07-24 to 2026-08-26 (34 daily runs)
**Corpus:** 529 repositories / 584 charms cloned locally, plus 100,544 GitHub issues and PRs
**Status:** RQ-2, RQ-6, RQ-7, RQ-9 and RQ-11 stopped and written up here. RQ-4 (maintenance health) is still collecting.
**Not Claude:** the collectors are plain Python on a cron scheduler, and the two agent jobs ran on Hermes with an open-weights model, not on Claude Code. It lands in this repository because the questions and the mistakes are the same ones the other experiments here are about.

## Summary

I wanted a factual base for arguments about charm ecosystem health, so I put five research questions on a daily cron and let them run for five weeks. Four of them (RQ-2 supply chain, RQ-7 documentation, RQ-9 config and action surface, RQ-11 charmcraft substrate) are static passes over local clones. The fifth (RQ-6) mines every issue and PR in the corpus from the GitHub API and classifies it.

The headline result is not one of the five questions. It is that **the daily cadence was the wrong instrument for four of them, and I could have known that from the first week's data**. Over the nine days where the corpus was actually being refreshed, the static passes saw between 0 and 9 changed repositories per day out of ~500 - about 0.4%. Structural properties of a charm (its base, its pinning style, whether it has docs) move on a scale of months. Thirty-four days of daily sampling produced one useful cross-section and 33 copies of it.

The cross-section itself is worth having, and most of this document is that. Six findings I did not expect:

| | Finding |
|---|---|
| 1 | Config options are essentially fully documented (100% typed, 98.9% described), but `type: secret` is used on 117 options while 209 secret-shaped options across 103 charms still take a plain string. |
| 2 | 225 of 529 repos (43%) have no discoverable documentation at all, and 376 (71%) have no `links` block in their metadata. |
| 3 | A third of all issue and PR traffic in charm repos (22,779 of 69,190 items) is bot-authored, and `renovate[bot]` alone accounts for 15,248 of it. |
| 4 | Zero repositories in the corpus run OpenSSF Scorecard. Not "few". Zero, out of 529. |
| 5 | Action naming is *conventionally* consistent (439 of 491 names are hyphenated, no case or separator collisions at all) and *lexically* fragmented: 362 of 491 names are used exactly once, and the same operation splits across generations - `pre-upgrade-check` (16 charms) against `pre-refresh-check` (15). |
| 6 | Every cross-cutting concern is wider than any plausible "worth fixing centrally" bar: observability touches 183 repos, TLS 163, Terraform 147. |

## Why these questions

The team argues about charm ecosystem quality fairly often, and the arguments are usually conducted on anecdote - the charms someone has looked at recently, or the ones that generated a support case. I wanted a corpus-wide answer to a small number of questions where the answer is mechanically checkable from the repository contents.

The five reported here:

| RQ | Question | Method |
|---|---|---|
| RQ-2 | What does dependency and supply-chain posture look like across charms? | static pass over dependency files and hygiene files |
| RQ-6 | What do charm maintainers actually spend issues and PRs on, and which concerns cut across many repos? | GitHub API mining plus classification |
| RQ-7 | How discoverable is charm documentation? | static pass over metadata, README and `docs/` |
| RQ-9 | How ergonomic are charm config and action surfaces? | static pass over `charmcraft.yaml` / `config.yaml` / `actions.yaml` |
| RQ-11 | How far has the charmcraft substrate migration got? | static pass over bases, platforms, plugins, and extensions |

RQ-4 (maintenance health: staleness, CI state, backlog growth, bus factor) is deliberately not in this write-up. It is the one question where the daily cadence earns its keep, so it is still running.

## Setup

### Corpus

`~/.cache/hyrum/charms/<owner>/<repo>`, a set of git clones driven by [hyrum](https://github.com/canonical/hyrum)'s charm list. A "repo" is a top-level `owner/repo` directory that contains at least one charm; a "charm root" is a directory with a `charmcraft.yaml` (or a `metadata.yaml` at the repo root). One repo can hold several charms, and 26 of them do - which is why the repo-level passes report 529 and the charm-level passes report 584.

`lib/corpus.py` holds the shared walk, the YAML merge (`charmcraft.yaml` wins, `metadata.yaml` fills gaps), the dependency-constraint parsers, and a `gh api` wrapper with backoff. Eight owner-level names are excluded as not-really-charms: the Launchpad mirrors, `+source`, the bundle repositories, and `ubuntu-repository-cache`.

### Schedule

Five jobs on the Hermes cron scheduler, staggered to keep the GitHub API calls apart:

| Job | Schedule | Agent? | What it does |
|---|---|---|---|
| `rq-static-daily` | 05:00 NZ | no | refresh clones, then run RQ-2, RQ-9, RQ-11, RQ-7 |
| `rq4-health-daily` | 06:00 NZ | no | ~60-repo round-robin batch of GitHub health sampling |
| `rq6-issues-daily` | 07:00 NZ | no | alternate fetch (GitHub API) and classify (local) phases |
| `rq6-llm-classify` | 07:30 NZ | yes | re-classify the heuristic classifier's residue |
| `rq-digest-weekly` | Sundays 09:00 NZ | yes | write a prose digest of the last 7 days |

The wrappers are in `cron/` and the two agent prompts in `cron/prompts/`. Everything appends JSONL, one record per repo (or charm) per day, and every record carries a `date`.

### The two agent jobs

`rq6-llm-classify` exists because the deterministic classifier is a title regex, and a title regex leaves about a third of everything as `uncategorised`. The prompt (`cron/prompts/rq6-llm-classify.md`) hands the agent a batch of 80 items, a closed category vocabulary, and a rule that matters more than the rest: *use `platform-*` only when the item is specifically about that concern, not as a casual mention*. It writes to a separate file and is forbidden from touching the deterministic output, so a bad run degrades recall rather than corrupting the dataset.

`rq-digest-weekly` writes the weekly prose summary. Its prompt is mostly budget discipline and honesty rules, both of which were added after failures: an early run burned its entire tool budget on unrequested analysis and produced nothing, and a later one reported the frozen-corpus flat line as ecosystem stability. The rule that fixed the second one - *a metric that did not move is only a trend if it was actually collected* - is the single most useful line in either prompt.

## What went wrong, and how much of it mattered

More of this experiment's lessons are in the plumbing than in the findings, so they go before the findings rather than in an appendix.

**The corpus sat frozen for 24 days.** `rq-static-daily` originally ran the four passes without refreshing the clones first. The passes re-derive whatever is on disk, so they cheerfully produced byte-identical rows every night from 2026-07-10 to 2026-08-16. Nothing in the data says "not collected" - a flat line and a frozen line look the same. This is the failure I would most want to design out of the next one: a collector that cannot tell you whether it observed *no change* or *nothing*.

**Another tool was writing to the shared corpus.** hyrum's `ops` patcher rewrites `pyproject.toml`, `uv.lock`, `poetry.lock` and `requirements.txt` in place, and does not always revert. Those are exactly the files RQ-2 reads. `canonical/charm-ubuntu` was recorded as `ops===3.7.1` / `exact-pins` for 25 consecutive days, where upstream declares `ops>=1.0,<2.0`. At least 18 repos were affected. Eight of them also blocked `git pull`, which is how I found it; the other ten merged cleanly and so failed silently, which is the worrying half. The wrapper now reverts dependency files before each run, but rows dated 2026-08-17 and earlier still carry it, and that is why every RQ-2 number below comes from the final day only.

**UTC dating against a local schedule duplicated days.** The passes stamp rows with the UTC date; cron fires at 05:00 NZ, which is 17:00 UTC the day before. A manual run and a cron fire land on the same UTC date and both append. 2026-07-23 is five times too wide as a result. Everything in `analysis/analyse.py` dedupes on `(date, repo)` before it counts anything.

**The RQ-6 classify phase silently fell half a corpus behind.** Fetch and classify alternate days, fetch pulls ~38 repos and classify processes 4,000 items. Fetch won. By the time I stopped it, `classified.jsonl` held 50,504 items from 303 repos while `raw/` held 100,544 items from 461, and the shortfall was not random: `canonical` was over-represented at 57,057 items while all of `openstack` contributed 209. Every RQ-6 number the weekly digests reported was computed on that skewed half. The fix was free, because classification is deterministic and local - `reclassify_rq6.py` rebuilds the whole file from `raw/` in about a minute - but nothing was watching the gap, so nobody ran it.

None of these are subtle bugs. They are all "the pipeline lied quietly", and all four were found by looking at the data rather than by anything in the pipeline noticing.

## The cadence result

`data/churn.csv` has the full series. Restricting to the days after the corpus refresh was fixed, which is the only stretch where a daily comparison means anything:

| Date | RQ-2 changed | RQ-7 | RQ-9 | RQ-11 | rows |
|---|---|---|---|---|---|
| 2026-08-18 | 9 | 3 | 6 | 1 | ~500 |
| 2026-08-19 | 1 | 3 | 2 | 0 | ~500 |
| 2026-08-20 | 6 | 0 | 0 | 1 | ~500 |
| 2026-08-21 | 3 | 3 | 1 | 1 | ~500 |
| 2026-08-22 | 0 | 0 | 0 | 0 | ~500 |
| 2026-08-23 | 0 | 0 | 1 | 0 | ~500 |
| 2026-08-24 | 1 | 0 | 0 | 1 | ~500 |
| 2026-08-25 | 2 | 9 | 2 | 0 | ~530 |

The 2026-08-17 row is excluded because it absorbed five weeks of upstream change in one step (235 changed repos in RQ-2 alone), which is an artefact of the freeze rather than a day's movement.

RQ-11 is the extreme case: at most one changed charm per day, and the arm64 share sat flat all week. To see a migration curve in that data you would need to sample for a year, and at that point you may as well sample quarterly and save 360 runs. I do not think the answer is "the questions were bad" - it is that a *rate* question and a *state* question want different instruments, and I put a state question on a rate instrument because a daily cron was the easy thing to build.

## Findings

All numbers below are the 2026-08-25 snapshot, deduped, from `data/snapshot-2026-08-25/`. Percentages are of the relevant denominator (529 repos or 584 charms) unless stated.

### RQ-2: supply-chain posture (529 repos)

**Pinning style**

| Style | Repos | |
|---|---|---|
| mostly-unpinned | 182 | 34.4% |
| uv.lock | 143 | 27.0% |
| none-declared | 82 | 15.5% |
| poetry.lock | 78 | 14.7% |
| mixed | 41 | 7.8% |
| exact-pins | 3 | 0.6% |

221 repos (42%) have a real lockfile, and uv has passed poetry by nearly two to one. That is a faster migration than I expected, and it is the one place in this whole survey where something is visibly moving.

**`ops` constraints**

270 repos (51%) do not declare `ops` anywhere the pass can see it. Most of those are reactive-era charms and charms whose only dependency declaration is a lockfile, so this is a floor on "declares ops", not a claim that half the corpus does not depend on it. Of the 259 that do declare it:

| Form | Repos |
|---|---|
| lower bound (`>=`) | 64 |
| exact (`==`) | 57 |
| compatible (`~=`) | 50 |
| unpinned (bare `ops`) | 42 |
| caret (`^`, poetry) | 41 |
| upper bound only (`<`) | 4 |
| unparsed (`2.2.0`, no operator) | 1 |

The most common single constraint is `~=2.17` (30 repos), and there is a visible 3.8 cohort (`^3.8.1`, `==3.8.1`, `~=3.8.1`, `==3.8.0`) at 25 repos. 57 repos exact-pin `ops`, which is the group that will not get a patch release without a bot or a human noticing.

**Hygiene**

| Signal | Repos | |
|---|---|---|
| Renovate | 135 | 25.5% |
| Dependabot | 22 | 4.2% |
| either | 155 | 29.3% |
| SECURITY.md | 174 | 32.9% |
| OpenSSF Scorecard | **0** | 0% |

Only two repos run both bots, so the Renovate/Dependabot split is close to a clean choice rather than an accumulation. 374 repos (71%) run neither, which sets up the RQ-6 finding below: the bot load is enormous *and* concentrated in a quarter of the corpus.

The Scorecard zero surprised me enough that I went and checked the collector. It greps every workflow file for the string `scorecard`, so a false zero would need every repo to spell it differently. I think the zero is real.

### RQ-7: documentation discoverability (529 repos)

The pass scores each repo on a four-rung ladder: 1 = `links.documentation` in metadata, 2 = a `docs/` directory, 3 = a docs URL in the README, 4 = nothing found.

| Rung | Repos | |
|---|---|---|
| 1 - documentation link in metadata | 252 | 47.6% |
| 2 - `docs/` directory | 27 | 5.1% |
| 3 - docs URL in README | 25 | 4.7% |
| 4 - nothing | 225 | **42.5%** |

The ladder is deliberately generous: rung 3 counts *any* link to Discourse, Read the Docs, `documentation.ubuntu.com` or a Charmhub docs page anywhere in the README. 225 repos clear none of those bars.

It splits sharply by owner:

| Owner | Repos | Rung 4 | |
|---|---|---|---|
| canonical | 362 | 121 | 33% |
| openstack | 74 | 49 | 66% |
| charmed-kubernetes | 44 | 17 | 39% |
| openstack-charmers | 26 | 25 | 96% |

Two supporting numbers. 376 repos (71%) have no `links` block at all in their metadata; among those that do, `source` (142) and `issues` (139) are more common than `documentation` (114), so the block is being used as a contact card rather than as the documentation pointer Charmhub reads. And READMEs are thin: median 2,253 bytes, 80 repos under 500 bytes, 27 completely empty.

One genuinely good result: only 4 repos still carry `charmcraft init` boilerplate text in the README, and zero have a templated description. Whatever was done about template residue worked.

### RQ-9: config and action surface (584 charms)

This is the pass whose premise turned out to be wrong, which makes it my favourite.

**Config**

5,262 options across 434 charms (150 charms declare no config at all).

| | Count | |
|---|---|---|
| options with an explicit `type` | 5,262 | **100%** |
| options with a `description` | 5,203 | 98.9% |

Every single config option in the corpus declares a type, and all but 59 have a description. I built this pass expecting to find an undocumented-config problem and there is not one. Only 13 charms have even one undescribed option.

The real gap is secrets:

| | Count |
|---|---|
| options using `type: secret` | 117 (across 59 charms) |
| secret-shaped options with a non-secret type | **209 (across 103 charms)** |

"Secret-shaped" means the option name contains `password`, `token`, `secret`, `apikey`, `private-key`, `credential` or `passphrase`. So the secret type is used on 117 options while 209 options that look like they want it take a plain string instead. The worst offenders carry ten each: `livepatch-k8s-operator`, `ceph-charms/ceph-dashboard`, `canonical.com/charm`. The commonest names are unglamorous - `password` (7), `san-password` (6), `tls-secret-name` (6), `github-token` (3), `oidc-client-secret` (3).

This is a heuristic and it will have false positives (`tls-secret-name` is a Kubernetes object name, not a secret). But 209 across 103 charms is a big enough number that the false-positive rate would have to be extraordinary for there to be no real problem underneath, and the list is small enough to check by hand.

**Actions**

973 actions across 242 charms; 342 charms (59%) declare none.

| | Count | |
|---|---|---|
| described | 970 | 99.7% |
| with params | 492 | 50.6% |

Documentation is again close to total. The interesting part is naming: 491 distinct names for 973 uses, and 362 of those names are used exactly once.

Convention is not the problem. 439 of 491 names are hyphenated and the remaining 52 are single words; there is not one pair of names in the entire corpus that differs only in separator or case. Vocabulary is the problem, and it splits along the upgrade/refresh generational line:

| Operation | Name A | Name B |
|---|---|---|
| pre-flight check | `pre-upgrade-check` (16) | `pre-refresh-check` (15) |
| continue after pause | `resume-upgrade` (9) | `resume-refresh` (15) |
| fetch a credential | `get-password` (11) | `get-admin-password` (6) |

The most-used names overall are `resume` (27), `pause` (25), `list-resources` (20), `list-versions` (20), `create-backup` (19) and `list-backups` (19), which is a sensible core vocabulary that a good chunk of the corpus already shares.

### RQ-11: charmcraft substrate (584 charms)

**Base declaration**

| Form | Charms | |
|---|---|---|
| `platforms` only (no base) | 256 | 43.8% |
| explicit `base:` (24.04 ×96, 22.04 ×15, 26.04 ×1) | 112 | 19.2% |
| legacy `bases[]` | 173 | 29.6% |
| none declared | 43 | 7.4% |

368 charms (63%) are on the modern form and 173 (30%) are still on legacy `bases[]`, of which 96 are 22.04-only. 551 of 584 have a `charmcraft.yaml` at all, so the 33 without are the genuinely ancient tail.

**Architectures**

| Arch | Charms |
|---|---|
| amd64 | 317 |
| arm64 | 173 (recounted - see below) |
| s390x | 120 |
| ppc64el | 105 |
| riscv64 | 2 |

370 charms declare any platforms at all, so arm64 is 46% of the charms that have made an explicit architecture choice, and 29% of the corpus.

**A collector bug, reported here because the digests quoted the wrong number for a month.** The `arm64` field checks whether the extracted arch set contains a bare `arm64`. Charms that use shorthand platform keys (`ubuntu-24.04-arm64`) end up with `build-for` values like `ubuntu@24.04:arm64`, which is not a bare match. That undercounts arm64 by 24 charms: 149 recorded against 173 actual, a 16% miss. `analysis/analyse.py` recounts off the suffix and reports both. Any arm64 figure in `data/digests/` is the low one.

**Plugins and extensions**

| Plugin | Charms |
|---|---|
| dump | 162 |
| uv | 148 |
| nil | 121 |
| poetry | 73 |
| reactive | 57 |
| charm | 44 |

`uv` at 148 against `poetry` at 73 matches the lockfile picture in RQ-2, from an independent file, which is a reassuring cross-check. 57 charms still build with the reactive plugin.

The 12-factor framework extensions are still small: 34 charms total (flask 20, go 6, django 4, fastapi 2, expressjs 2).

### RQ-6: issues and PRs

**Coverage first, because every number below is bounded by it.**

| | |
|---|---|
| repos in the corpus at the snapshot | 529 |
| repos attempted | 499 |
| repos that returned anything | 461 (38 empty: renamed, private, or genuinely issue-free) |
| items fetched | 100,544 |
| items in the shipped `classified.jsonl` | 50,504 (303 repos) |
| items after re-running the classifier over everything | 100,544 (461 repos) |
| LLM overlay records | 14,047 |

The tables below use the full re-classification. The LLM overlay only ever saw the residue of the 303 repos the classify phase had reached, so anything it contributes is a floor.

I report two cuts. 23 of the 461 repos are web properties or shared tooling that happen to contain a charm - `canonical/ubuntu.com` alone is 16% of every item fetched - and they swamp the charm signal. **Charm-only is the headline; full-corpus is in `data/rq6/rq6-summary.json`.**

**Shape of the charm-only corpus:** 69,190 items across 437 repos, 2015 to 2026, 57,595 PRs against 11,595 issues. That 5:1 PR-to-issue ratio is the first surprise. Charm repos are places where changes land, not places where problems get reported.

**Categories** (multi-label, so these sum to more than 100%):

| Category | Items | |
|---|---|---|
| deps | 19,042 | 27.5% |
| chore | 18,361 | 26.5% |
| feature | 15,110 | 21.8% |
| bug | 12,707 | 18.4% |
| ci | 6,142 | 8.9% |
| testing | 5,889 | 8.5% |
| docs | 3,921 | 5.7% |
| security | 992 | 1.4% |
| uncategorised (after the LLM overlay) | 6,200 | 9.0% |

Dependency work is the single largest thing charm repos do, and `chore` (releases, version bumps, renames) is a close second. Between them, more than half of all traffic is maintenance that produces no user-visible change.

**Bots.** 22,779 of 69,190 items (32.9%) are bot-authored:

| Account | Items |
|---|---|
| renovate[bot] | 15,248 |
| dependabot[bot] | 2,578 |
| observability-noctua-bot | 1,771 |
| github-actions[bot] | 1,382 |
| soleng-terraform[bot] | 531 |

Put that against RQ-2: only 155 of 529 repos (29%) run a dependency bot at all. So a third of all charm repository traffic is generated by robots operating in under a third of the repositories. Whatever the median maintainer experience is, it is not the experience of someone in a Renovate repo.

**Backlog.** 4,030 open items (2,430 issues, 1,600 PRs).

| | |
|---|---|
| median age of an open item | 231 days |
| open more than 1 year | 1,581 (39%) |
| open more than 2 years | 852 (21%) |
| median close latency, PRs | 1 day (p90 24) |
| median close latency, issues | 20 days (p90 329) |

PRs move fast and issues do not. The p90 for issue closure being 329 days against 24 for PRs is the clearest single statement of where the ecosystem's attention goes. 54.7% of items carry no label at all, and 57.3% never received a comment.

The largest open backlogs, after folding `juju-solutions/bundle-kubeflow` into `canonical/bundle-kubeflow` (the same repo, fetched twice under both owners):

| Repo | Open |
|---|---|
| canonical/bundle-kubeflow | 374 |
| canonical/postgresql-operator | 134 |
| canonical/traefik-k8s-operator | 90 |
| canonical/mysql-operators | 71 |
| canonical/opentelemetry-collector-operator | 63 |
| canonical/operator | 63 |

**Cross-cutting concerns.** The reason RQ-6 exists: how many distinct repos hit the same wall.

| Concern | Items | Repos | Items/repo | Open | Recovered by the LLM pass |
|---|---|---|---|---|---|
| observability (COS) | 1,653 | 183 | 9.0 | 151 | 22 items, 1 new repo |
| TLS / certificates | 1,282 | 163 | 7.9 | 121 | 12 items |
| Terraform | 978 | 147 | 6.7 | 50 | 2 items |
| air-gap / proxy | 506 | 117 | 4.3 | 66 | 5 items |
| arm64 | 199 | 83 | 2.4 | 8 | **24 items, 7 new repos** |
| backup / restore | 482 | 70 | 6.9 | 44 | 14 items |

Repo spread is the honest measure here, not item count - item counts grow with fetch depth, spread does not. Every one of these is over 70 repos. If the bar for "fix this once, centrally, rather than 100 times" is anything under 70 repos, all six clear it.

arm64 is the interesting row, for two reasons. It has the lowest per-repo density (2.4), which fits a concern that gets raised once per repo and then either done or dropped - and only 8 of 199 are still open, so it mostly gets resolved. And it is the one category where the title regex is systematically weak: the LLM pass recovered 24 items in 7 repos it had missed, against 2 for Terraform. "Add arm64 support" is easy to match; "support Ampere" and "build for aarch64 runners" are not.

**Labels.** 337 distinct labels across the corpus, and no shared scheme. Seven spellings of bug (`bug`, `Type: Bug`, `Bug 🐛`, `good-first-bug`, `application bug`, `CI bug`, and `not bug or enhancement`), six of documentation. The four most-used labels corpus-wide are all from one team's review workflow (`Review: Code +1`, `Review: QA +1`, `Libraries: Out of sync`, `Libraries: OK`). Cross-repo label queries are not going to work.

### What the LLM classification pass was worth

It ran 34 times, drained a 14,047-item backlog, and then kept firing against an empty queue until it started failing on an org budget limit.

Judged on recall it did its job: it took the heuristic residue and assigned real categories, 96% of them one category per item, with `chore` (3,851), `bug` (3,018), `other` (2,055) and `deps` (2,046) leading. `other` at 2,055 is the honest part - the prompt told it not to guess when a title is too vague, and it didn't.

Judged on what it changed, it bought exactly one thing: arm64 recall. 24 items in 7 repos. Everywhere else it moved counts within categories that were already far past any decision threshold. If I ran this again I would not put an LLM on the whole residue. I would put it on the six `platform-*` categories only, where a regex over titles is provably lossy, and leave the bug/feature/chore split to the cheap classifier that is already good enough for the use the numbers get put to.

## Rejected alternatives

**Sampling instead of a full sweep.** For RQ-6 I considered fetching a random 100 repos rather than all 499. Full sweep won because the whole point was cross-repo spread, and a sample undercounts spread in exactly the way that matters. That was right, but it cost the classify phase falling behind fetch, which cost a month of digests computed on a skewed half of the data. A sample that stayed complete might have been the better trade.

**Classifying issue bodies as well as titles.** Tested early and dropped: bodies are full of stack traces, templates and CI output, and keyword matching against them produced far more false positives than the extra recall was worth. Titles plus GitHub labels is a worse classifier with a much better precision floor, and the LLM pass exists to recover what that costs.

**Committing the full time series.** It is ~90 MB of mostly-identical rows. Given the churn result, the honest artefact is the final-day snapshot plus the churn series that shows why the rest is not interesting. `analysis/analyse.py` regenerates every table here from a live results directory.

## Reproducing

```
python3 analysis/analyse.py --results ~/charm-research/results --out data
```

Deterministic: same results directory in, byte-identical `data/` out. `AS_OF` in the script pins the reference date for every age calculation, so the backlog numbers do not drift when it is re-run.

- `collectors/` - the five collectors, `reclassify_rq6.py`, and `lib/corpus.py`, as they ran
- `cron/` - the three shell wrappers and the two agent prompts
- `data/DATA-DICTIONARY.md` - field-by-field schema and the caveats, as it stood at the end of collection
- `data/snapshot-2026-08-25/` - the final-day rows for all four static passes, deduped
- `data/rq6/` - `rq6-summary.json` (both cuts) and `rq6-per-repo.csv` (460 repos)
- `data/churn.csv` - day-over-day changed-row counts for all four static passes
- `data/digests/` - the six digests the agent job produced (five scheduled Sunday runs plus a manual first one on the day the jobs were created), including the ones with the numbers this write-up corrects
