# I Read ~7000 Charming Bug Fixes So You Didn't Have To

Ok, not really. Claude Code read them, and only a sample of 15-20%. But the resulting bug-finding skill caught 166 confirmed bugs across 41 charm repositories, built entirely from patterns mined out of our own ecosystem's history.

## TL;DR

I took [David Cramer's skill synthesis idea](https://cra.mr/skill-synthesis) — mine your project's actual bug history instead of relying on generic guidelines — and applied it to charm development. Scaling from a single repo (235 fixes) to the Charm Tech team (452 fixes) to 134 charm repositories across 10 Canonical teams (6,116 fixes) produced a [skill](https://github.com/tonyandrewmeyer/charming-with-claude/tree/main/experiments/2026-03-13-code-review-skills-our-data/charming-analysis/.claude/skills/charm-find-bugs) that catalogues 69 anti-patterns and 25 cross-cutting concerns, with a 6.7% false-positive rate (1.6% after the first human review round).

## The Three Stages

**Stage 1: The operator repo.** ~235 bug fixes, Claude classified them all (leaning heavily on conventional commits), produced a pattern catalogue, and an initial skill. Running it against current HEAD found 10 real (minor) bugs, including data mutability issues that had been fixed six separate times already but kept recurring. Lesson: false-positive controls matter as much as the patterns themselves.

**Stage 2: Charm Tech's 10 repos.** Scaling to the whole team revealed that **Python and Go bug patterns have almost zero overlap in our repos**. The Go repos (Pebble, Concierge) are dominated by concurrency bugs — deadlocks, nil maps, error wrapping — while the Python repos cluster around data mutability, falsy values, and relation data handling. So we split into two skills. Validation against four held-out repos found six novel (again minor) bugs with no false positives, including a password exposure in `charmlibs` where CLI arguments were visible in the process list.

**Stage 3: The full ecosystem.** 134 repos, spanning Data, Observability, MLOps, IS, Identity, Telco, Commercial Systems, K8s, and BootStack. Extraction used both conventional commit parsing *and* keyword scoring — important, because the K8s team has only 35% conventional commit adoption, and keyword scoring recovered 37% of their fixes that would otherwise have been missed entirely.

Validation ran over 10 rounds against 41 repos:

| Rounds | Repos | Confirmed Bugs | False Positives | FP Rate |
|--------|-------|----------------|-----------------|---------|
| 1–4 (automated) | 14 | 59 | 0 | 0% |
| 5 (first human review) | 8 | 28 | 10 | 26.3% |
| 6–10 (human-reviewed) | 16 | 63 | 2 | 1.6% |
| **Total** | **41** | **166** | **12** | **6.7%** |

Round 5 is where the interesting bit happened. The automated rounds looked clean, but the first human review caught ten false positives — and they fell into just three systematic categories (for example, `relation.app` is never `None` in modern `ops`, unconditional `container.replan()` is fine because Pebble handles idempotency). Fixing those dropped the FP rate to 1.6% for the remaining rounds.

## What Bugs Look Like at Ecosystem Scale

The most pervasive patterns, by how many of the 41 validation repos they appeared in:

| Pattern | Repos | What It Is |
|---------|-------|-----------|
| Non-string Pebble env values | 14/41 | Pebble env dicts should contain only strings |
| Restart without `ChangeError` handling | 8/41 | Pebble restart can raise if the service is already stopped |
| Missing `can_connect()` guard | 7/41 | Pebble operations before the container is ready |
| Missing return/fail in actions | 7/41 | Handler runs to completion without `event.fail()` on errors |
| Credential exposure | 7/41 | Passwords in logs, Pebble CLI args, or tracebacks |
| Missing `relation_broken` handler | 5/41 | Cleanup logic defined but never wired up |
| Truthiness on config values | 4/41 | `if self.config['key']:` treats 0 as "not configured" |

A generic code review — human or AI — would catch the credential exposure, probably the truthiness bug. But "Pebble env vars should be strings" or "you need a `can_connect()` guard" (to be fair, you maybe do not) are things you only know from experience with our ecosystem. That's the whole point of mining the history rather than starting from general principles.

Each team also has its own flavour: the Data team hits TLS toggle race conditions, Observability repeatedly fixes wrong Grafana datasource variable names (`${DS_PROMETHEUS}` vs `${prometheusds}`), IS gets bitten by Pebble lifecycle ordering. Patterns that only emerge when you look across enough repos from the same team.

## Filing Bugs Upstream

Of the 52 findings across the operator and charm-tech stages, **11 survived human review as worth PRing** (and one was opened, closed after closer inspection): 4 merged-worthy PRs against `operator`, 5 across `charmlibs`/`pytest-jubilant`/`concierge`. Human review remains a significant filtering step — automated FP rates undersell how much triage you still need.

It's worth noting that there was some debate within Charm Tech about the merit of these fixes. Partly, that happened because I was loose in my language and Claude opened PRs for me, which I would normally do myself, and the fixes had leaked into each other's branch. However, several were also more theoretical than likely to really happen, and also quite minor. Most did end up landing.

## Is This Still Worth Doing?

I'd be remiss not to mention that Mythos and similar dedicated bug-finder models/agents are landing around now (I did this experiment back in March and have been slow at writing it up), and they may make this kind of targeted, hand-rolled synthesis less interesting at the frontier. If you have a model that can read your codebase and find bugs without you mining commits first, why bother?

The possible answer: **small local models**. A frontier bug-finder costs real money per scan and can't run on an air-gapped or sensitive repo. A focused skill — 69 anti-patterns, well-described, with concrete examples and false-positive controls — is the kind of context that *might* let a much smaller model (something you could run locally, in CI, on every PR) get useful results in a specific domain. That's the experiment I'd want to run next.

## Full Write-Up

All three stages, the methodology, the review tool, and the 10-round validation data are in the [experiment directory](https://github.com/tonyandrewmeyer/charming-with-claude/tree/main/experiments/2026-03-13-code-review-skills-our-data). Try [the `charm-find-bugs` skill](https://github.com/tonyandrewmeyer/charming-with-claude/tree/main/experiments/2026-03-13-code-review-skills-our-data/charming-analysis/.claude/skills/charm-find-bugs) against your charm, and let me know what it finds (and what it gets wrong).
