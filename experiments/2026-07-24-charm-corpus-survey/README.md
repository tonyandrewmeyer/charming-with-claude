# What Five Weeks of Watching Every Charm Actually Told Me

We argue about charm ecosystem quality a lot, and almost always from anecdote - whichever charms someone looked at last week, or whichever one generated a support case. So I put five research questions on a daily cron over the whole corpus (529 repositories, 584 charms, 100,544 issues and PRs) and let it run for 34 days.

The most useful thing it told me was about the instrument rather than the ecosystem, so that goes first.

## The daily cadence was wrong, and one week of data said so

Four of the five questions are static passes: dependency posture, documentation, config and action surface, charmcraft substrate. Once the corpus was actually being refreshed, they saw **between 0 and 9 changed repositories per day out of about 500**. Roughly 0.4%. RQ-11 (substrate) peaked at one changed charm in a day.

That is not a surprise in hindsight. A charm's base, its pinning style and whether it has documentation move on a scale of months. I had a *state* question and I put it on a *rate* instrument, because a daily cron was the easy thing to build. Thirty-four runs produced one useful cross-section and 33 copies of it.

(The cross-section is genuinely worth having, which is why the rest of this exists. But quarterly sampling would have produced the same answer.)

## Six things I did not expect

**Config documentation is a solved problem, and secrets are not.** All 5,262 config options in the corpus declare a type, and 98.9% have a description. I built the pass expecting to find an undocumented-config problem and there isn't one. What there is: 117 options use `type: secret`, while **209 secret-shaped options across 103 charms** (names containing `password`, `token`, `secret`, `apikey`, `private-key`) still take a plain string. That is a heuristic and it will have false positives, but the list is 103 charms long and checkable by hand.

**43% of repos have no discoverable documentation at all.** 225 of 529 clear none of the four rungs - no `links.documentation`, no `docs/` directory, not even a Discourse or Read the Docs link anywhere in the README. 376 repos (71%) have no `links` block at all, and among those that do, `source` and `issues` both beat `documentation`. The block is being used as a contact card rather than as the pointer Charmhub reads.

**A third of all charm repo traffic is robots, in under a third of the repos.** 22,779 of 69,190 issues and PRs are bot-authored, `renovate[bot]` alone accounting for 15,248. Meanwhile only 155 of 529 repos (29%) run a dependency bot at all. Whatever the median maintainer experience is, it is not the experience of someone working in a Renovate repo.

**Zero repositories run OpenSSF Scorecard.** Not few. Zero, out of 529. I went and checked the collector, because that is the kind of number that is usually a bug; it greps every workflow file for the string, so a false zero would need every repo to spell it differently.

**Action naming is conventionally tidy and lexically fragmented.** 439 of 491 distinct action names are hyphenated, and there is not one pair in the whole corpus that differs only in separator or case - so the convention has landed. But 362 names are used exactly once, and the same operation splits along the upgrade/refresh generational line: `pre-upgrade-check` (16 charms) against `pre-refresh-check` (15), `resume-upgrade` (9) against `resume-refresh` (15).

**Every cross-cutting concern is wider than any plausible fix-it-centrally bar.** Counting distinct repositories rather than raw items: observability 183, TLS 163, Terraform 147, air-gap 117, arm64 83, backup 70. If the threshold for "solve this once rather than 100 times" is anything under 70 repos, all six clear it.

## The plumbing failed more interestingly than the analysis did

Four bugs, and all four have the same shape: **the pipeline lied quietly, and only looking at the data found it.**

- The corpus sat frozen for 24 days because the wrapper didn't refresh the clones. The passes happily re-derived what was on disk. A flat line and a frozen line look identical in the output - nothing distinguishes "observed no change" from "observed nothing".
- Another tool (hyrum's `ops` patcher) was writing to the shared corpus, rewriting exactly the dependency files RQ-2 reads. `canonical/charm-ubuntu` was logged as `ops===3.7.1` for 25 days against an upstream `ops>=1.0,<2.0`. 18 repos affected; the 8 that also blocked `git pull` are how I found it, and the other 10 failed silently.
- UTC row stamps against a 05:00 NZ schedule duplicated whole days.
- RQ-6's classify phase fell half a corpus behind its fetch phase and nothing was watching. `classified.jsonl` held 50,504 items from 303 repos while `raw/` held 100,544 from 461, and the shortfall wasn't random - `canonical` was over-represented at 57,057 items while all of `openstack` contributed 209. Every number in the weekly digests was computed on that skewed half. Fixing it was free (classification is deterministic and local, so re-running it takes a minute), which is the annoying part.

## What I'd do next

In roughly the order I think they're worth doing:

1. **File the secret-type findings.** 209 config options across 103 charms is a concrete, checkable list, and it's the one finding here with an obvious action attached. Ideally as a `charmcraft` lint rule rather than 103 issues.
2. **Fix the arm64 undercount before quoting any arm64 number.** The collector misses charms using shorthand platform keys, because their `build-for` arrives as `ubuntu@24.04:arm64` rather than a bare arch. 149 recorded against 173 actual, a 16% miss, and every arm64 figure in the weekly digests is the low one.
3. **Move the static passes to quarterly**, and give each one a "corpus last refreshed" field so a flat line can be told apart from a dead collector.
4. **Propose the small action vocabulary that already exists.** `resume`, `pause`, `list-resources`, `create-backup`, `list-backups` are shared by 19 to 27 charms each. The refresh-generation names look like the intended direction; saying so somewhere authoritative would stop the split widening.
5. **Point the LLM classifier only at the `platform-*` categories.** Over 34 runs it drained a 14,047-item backlog and bought exactly one thing: arm64 recall (24 items across 7 repos the title regex missed, against 2 for Terraform). Everywhere else it moved counts inside categories that were already miles past any decision threshold. The regex is provably lossy on cross-cutting concerns and good enough on everything else.
6. **Decide whether the 225 rung-4 repos are a campaign or a policy.** Adding `links.documentation` is a one-line change; doing it 225 times by hand is not, and 96% of `openstack-charmers` sits in that bucket.

RQ-4 (maintenance health: staleness, CI state, backlog growth, bus factor) is still running, because it's the one question where the daily cadence earns its keep - 57% of consecutive snapshots differ, with CI state flipping in 15% of them. That one gets its own write-up when it has enough sweeps.

## Details

- [WRITEUP.md](WRITEUP.md) - full report: setup, all five questions, every table, what went wrong and what I'd reject next time
- [collectors/](collectors/) - the collectors and the shared corpus library, verbatim as they ran
- [cron/](cron/) - the shell wrappers and both agent prompts
- [data/](data/) - final-day snapshots, the RQ-6 summary and per-repo table, the churn series, and the six weekly digests
- [analysis/analyse.py](analysis/analyse.py) - regenerates every table in the write-up from a live results directory

The collectors are plain Python on a cron scheduler and the two agent jobs ran on Hermes with an open-weights model, so despite the repository this one wasn't Claude. The mistakes are the same ones though.
