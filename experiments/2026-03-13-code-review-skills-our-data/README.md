# Code Review Skills from Our Own Data

In this experiment, I took [David Cramer's skill synthesis idea](https://cra.mr/skill-synthesis) — mine your project's actual bug history instead of relying on generic guidelines — and applied it to Juju charm development. Rather than one repository, I progressively scaled from a single repo (235 fixes) through the Charm Tech team's 10 repos (452 fixes) to 134 charm repositories across 10 Canonical teams (6,116 fixes). The end product is a [bug-finding skill](charming-analysis/.claude/skills/charm-find-bugs/) that found 166 confirmed bugs across 41 test repos, built entirely from the ecosystem's own mistakes.

The work happened in three stages, each its own directory with a detailed write-up. This README covers the arc and the interesting bits; the write-ups have all the methodology and data.

## Goals

* Test whether skill synthesis — learning bug patterns from a project's own history — works for charm development.
* Scale the approach from one repo to an entire ecosystem and see what changes.
* Produce a reusable bug-finding skill that catches real bugs with a low false-positive rate.
* Understand what kinds of bugs recur across charm teams and where the patterns differ.

## The Three Stages

### Stage 1: [Operator Framework](operator-analysis/) (1 repo, 235 fixes)

The [operator](https://github.com/canonical/operator) repository has ~2,000 commits. Of those, 235 are bug fixes. Claude classified them all, produced a pattern catalogue of 13 categories, and built an initial skill. Running it against the current HEAD found 10 real bugs, including data mutability issues that had been fixed six separate times already but kept recurring.

The main takeaway was that false-positive controls matter as much as the patterns themselves. Without them, every `return self._data[key]` gets flagged as a mutability bug even when the values are immutable primitives.

### Stage 2: [Charm Tech Team](charm-tech-analysis/) (10 repos, 452 fixes)

Scaling to the whole team immediately revealed that **Python and Go bug patterns have almost zero overlap**. The Go repos (Pebble and Concierge) are dominated by concurrency bugs — deadlocks, nil maps, error wrapping — while the Python repos share patterns around data mutability, falsy values, and relation data handling. This meant splitting into two separate skills.

Validation against 4 held-out repos found 6 novel bugs with 0 false positives, including a password exposure in charmlibs where CLI arguments were visible in the process list. The more interesting finding was that "bug-for-bug compatible" migrations faithfully copy bugs across codebases — the skills catch them immediately because they're looking for the exact patterns that produced the original fixes.

### Stage 3: [Full Ecosystem](charming-analysis/) (134 repos, 6,116 fixes)

This was the big one. All 134 charm repositories from `charms.csv`, spanning Data, Observability, MLOps, IS, Identity, Telco, Commercial Systems, K8s, BootStack, and Charm-Tech. The extraction used both conventional commit parsing and keyword scoring, which turned out to be critical — the K8s team has only 35% conventional commit adoption, so keyword scoring recovered 37% of their fixes that would otherwise have been missed entirely.

The skill was validated over 10 rounds against 41 repos:

| Rounds | Repos | Confirmed Bugs | False Positives | FP Rate |
|--------|-------|---------------|-----------------|---------|
| 1–4 (automated) | 14 | 59 | 0 | 0% |
| 5 (first human review) | 8 | 28 | 10 | 26.3% |
| 6–10 (human-reviewed) | 16 | 63 | 2 | 1.6% |
| **Total** | **41** | **166** | **12** | **6.7%** |

Round 5 was where the interesting learning happened. Adding human review for the first time caught 10 false positives that the automated rounds had missed, and they fell into just three systematic categories: `relation.app` is never None in modern ops (5 FPs), unconditional `container.replan()` is fine because Pebble handles idempotency (3 FPs), and `ExecError` on workload binaries is acceptable (1 FP). Fixing those three categories dropped the FP rate to 1.6% for the remaining rounds.

The final skill catalogues **69 anti-patterns** (AP-001 through AP-069, minus AP-008 and AP-014 which were removed as false positives) and **25 cross-cutting concerns**.

## What Bugs Look Like at Ecosystem Scale

The most pervasive patterns, by how many of the 41 validation repos they appeared in:

| Pattern | Repos | What It Is |
|---------|-------|-----------|
| Non-string Pebble env values | 14/41 | Pebble requires string environment variables; passing ints silently breaks |
| Restart without ChangeError handling | 8/41 | Pebble restart can raise ChangeError if the service is already stopped |
| Missing `can_connect()` guard | 7/41 | Pebble operations before the container is ready |
| Missing return/fail in actions | 7/41 | Action handler runs to completion without calling `event.fail()` on error paths |
| Credential exposure | 7/41 | Passwords in log messages, Pebble CLI args, or exception tracebacks |
| Missing `relation_broken` handler | 5/41 | Cleanup logic defined but never wired up with `framework.observe()` |
| Truthiness on config values | 4/41 | `if self.config['port']:` treats 0 as "not configured" |

What I find striking is how many of these are domain-specific. A generic code review — human or AI — would catch the credential exposure, maybe the truthiness bug. But "Pebble environment variables must be strings" or "you need a `can_connect()` guard" are things you only know from experience with the charm ecosystem. That's the whole point of mining the history rather than starting from general principles.

Each team also has its own distinctive patterns. The Data team hits TLS toggle race conditions because coordinating TLS state between charm and database requires a two-phase handshake. The Observability team repeatedly fixes wrong datasource variable names in Grafana dashboards (`${DS_PROMETHEUS}` vs `${prometheusds}`). The IS team gets bitten by Pebble lifecycle ordering because web app charms need config files pushed before the service starts. These are patterns that only emerge when you look at enough repos from the same team.

## The Review Tool

By round 5, reviewing findings in markdown files wasn't scaling. I needed to track which findings were true positives, record domain knowledge from each review, and feed that back into the skill. So Claude built a [review tool](charming-analysis/review-tool/) — a SQLite-backed web/TUI/CLI app for triaging findings. FastAPI + htmx for the web interface, Textual for the terminal, keyboard shortcuts for rapid review (`j`/`k` navigate, `r` reviewed, `f` false positive). The export feeds directly back into skill improvement.

It's not a complicated tool, but it closed the feedback loop that made rounds 6–10 much more efficient than the earlier rounds.

## What I Learned

**Skills built from real data are dramatically better than generic ones.** This isn't surprising in retrospect — Cramer's team found the same thing at Sentry — but the margin is larger than I expected. A generic "check for security issues" prompt would miss almost everything in the top patterns list above.

**Scale changes what you see.** At single-repo scale, data mutability was the headline pattern. At team scale, the Python/Go split was the story. At ecosystem scale, per-team patterns and the sheer pervasiveness of things like non-string Pebble env values became visible. The methodology works at any scale, but you get qualitatively different insights at each level.

**Human review is essential but doesn't need to be exhaustive.** The automated rounds were valuable for building the initial catalogue, but the first human review round caught systematic FP categories that automated validation couldn't. After fixing those, the remaining rounds were very clean. The investment was roughly one afternoon of reviewing findings, not weeks.

**Conventional commit adoption matters for this kind of analysis.** Teams with high adoption (Identity at 96%) are trivial to analyse. Teams with low adoption (K8s at 35%) need keyword scoring to avoid missing a third of their fixes. This might be worth evangelising independently of the skill synthesis work.

**The iteration story is the real story.** The skill at the end of round 10 is substantially different from the one at the end of round 1. Anti-patterns were added, removed, and refined. False-positive controls were tightened. Domain knowledge captured in reviewer notes shaped the skill's evolution. Without a structured iteration process (and the review tool to support it), the skill would have plateaued much earlier.

## Files

Each stage has its own directory with a detailed write-up:

* **[operator-analysis/](operator-analysis/)** — Single-repo analysis, initial skill, methodology proof. Start here for the approach.
* **[charm-tech-analysis/](charm-tech-analysis/)** — Team-scale analysis, Python/Go split, cross-repo patterns.
* **[charming-analysis/](charming-analysis/)** — Full ecosystem analysis, 10 validation rounds, review tool, final skill. The bulk of the data and findings are here.

The final skill itself is at [`charming-analysis/.claude/skills/charm-find-bugs/`](charming-analysis/.claude/skills/charm-find-bugs/).
