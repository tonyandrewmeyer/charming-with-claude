# I read ~7000 charming bug fixes so you didn't have to

Ok, not really, Claude Code read them. And even then, it was actually a sample of 15-20%.

In this experiment, I took [David Cramer's skill synthesis idea](https://cra.mr/skill-synthesis) — mine your project's actual bug history instead of relying on generic guidelines — and applied it to charm development. Rather than one repository, I progressively scaled from a single repo (canonical/operator: 235 fixes) through the Charm Tech team's 10 repos (452 fixes) to 134 charm repositories across 10 Canonical teams (6,116 fixes). The end product is a [bug-finding skill](charming-analysis/.claude/skills/charm-find-bugs/) that found 166 confirmed bugs (of varying severity) across 41 test repos, built entirely from our ecosystem's own mistakes.

The work happened in three stages, each its own directory with a detailed write-up. This README covers the arc and the interesting bits; the write-ups have all the methodology and data.

## Goals

* Test whether skill synthesis — learning bug patterns from a project's own history — works for charm development.
* Scale the approach from one repo to an entire ecosystem and see what changes.
* Produce a reusable bug-finding skill that catches real bugs with a low false-positive rate.
* Understand what kinds of bugs recur across charm teams and where the patterns differ. Even if the AI piece is not useful, perhaps this would show where Charm Tech can help, with improved documentation, charm libraries, helper functions, and so on.

## The Three Stages

### Stage 1: [Operator Framework](operator-analysis/) (1 repo, 235 fixes)

The [operator](https://github.com/canonical/operator) repository has ~2,000 commits. Of those, ~235 are bug fixes. Claude classified them all (leaning heavily on the use of conventional commits in recent years), produced a pattern catalogue of 13 categories, and built an initial skill. Running it against the current HEAD found 10 real bugs, including data mutability issues that had been fixed six separate times already but kept recurring.

A takeaway was that false-positive controls matter as much as the patterns themselves. Without them, every `return self._data[key]` gets flagged as a mutability bug even when the values are immutable primitives.

### Stage 2: [Charm Tech Team](charm-tech-analysis/) (10 repos, 452 fixes)

Scaling to the whole team revealed that (for us) **Python and Go bug patterns have almost zero overlap**. The Go repos (Pebble and Concierge) are dominated by concurrency bugs — deadlocks, nil maps, error wrapping — while the Python repos share patterns around data mutability, falsy values, and relation data handling. This meant splitting into two separate skills.

Validation against four held-out repos found six novel bugs with no false positives, including a password exposure in charmlibs where CLI arguments were visible in the process list.

### Stage 3: [Full Ecosystem](charming-analysis/) (134 repos, 6,116 fixes)

This was the big one. 134 charm repositories (from a list Charm Tech maintains internally, used to evaluate the impact of changes and make data-driven decisions), spanning Data, Observability, MLOps, IS, Identity, Telco, Commercial Systems, K8s, and BootStack. The extraction used both conventional commit parsing and keyword scoring, which was important, as expected — the K8s team has only 35% conventional commit adoption, so keyword scoring recovered 37% of their fixes that would otherwise have been missed entirely.

The skill was validated over 10 rounds against 41 repos:

| Rounds | Repos | Confirmed Bugs | False Positives | FP Rate |
|--------|-------|---------------|-----------------|---------|
| 1–4 (automated) | 14 | 59 | 0 | 0% |
| 5 (first human review) | 8 | 28 | 10 | 26.3% |
| 6–10 (human-reviewed) | 16 | 63 | 2 | 1.6% |
| **Total** | **41** | **166** | **12** | **6.7%** |

Round 5 was where the interesting learning happened. Adding human (unfortunately, only me) review for the first time caught ten false positives that the automated rounds had missed, and they fell into just three systematic categories: `relation.app` is never `None` in modern `ops` (5 FPs), unconditional `container.replan()` is fine because Pebble handles idempotency (3 FPs), and `ExecError` on workload binaries is sometimes acceptable (1 FP). Fixing those three categories dropped the FP rate to 1.6% for the remaining rounds.

The final skill catalogues **69 anti-patterns** (AP-001 through AP-069, minus AP-008 and AP-014 which were removed as false positives) and **25 cross-cutting concerns**.

## What Bugs Look Like at (Current) Ecosystem Scale

The most pervasive patterns, by how many of the 41 validation repos they appeared in:

| Pattern | Repos | What It Is |
|---------|-------|-----------|
| Non-string Pebble env values | 14/41 | Pebble expects string environment variables |
| Restart without ChangeError handling | 8/41 | Pebble restart can raise ChangeError if the service is already stopped |
| Missing `can_connect()` guard | 7/41 | Pebble operations before the container is ready (mixed feelings on this one) |
| Missing return/fail in actions | 7/41 | Action handler runs to completion without calling `event.fail()` on error paths |
| Credential exposure | 7/41 | Passwords in log messages, Pebble CLI args, or exception tracebacks |
| Missing `relation_broken` handler | 5/41 | Cleanup logic defined but never wired up with `framework.observe()` |
| Truthiness on config values | 4/41 | `if self.config['key']:` treats 0 as "not configured" |

Interestingly, many of these are domain-specific. A generic code review — human or AI — would catch the credential exposure, probably the truthiness bug. But "Pebble environment variables must be strings" or "you need a `can_connect()` guard" are things you only know from experience with the charm ecosystem. That's the whole point of mining the history rather than starting from general principles.

Each team also has its own distinctive patterns. The Data team hits TLS toggle race conditions because coordinating TLS state between charm and database requires a two-phase handshake. The Observability team repeatedly fixes wrong datasource variable names in Grafana dashboards (`${DS_PROMETHEUS}` vs `${prometheusds}`). The IS team gets bitten by Pebble lifecycle ordering because web app charms need config files pushed before the service starts. These are patterns that emerge when you look at enough repos and fixes from the same team.

## The Review Tool

By round 5, reviewing findings in markdown files wasn't scaling. I needed to track which findings were true positives, record domain knowledge from each review, and feed that back into the skill. So I had Claude built a [review tool](charming-analysis/review-tool/) — a SQLite-backed web/TUI/CLI (I thought web would be nice, then figured out TUI is actually more convenient) app for triaging findings. FastAPI + htmx for the web interface, Textual for the terminal, keyboard shortcuts for rapid review (`j`/`k` navigate, `r` reviewed, `f` false positive). The export feeds directly back into skill improvement.

(Despite multiple attempts at Claude fixing it, there's still an annoying bug in the TUI version where it will sometimes show the first item's findings instead of the selected one, but I gave up trying to get that solved for now.)

It's not a complicated tool, but it closed the feedback loop that made rounds 6–10 much more efficient than the earlier rounds.

## What I Learned

**Skills built from real data are probably better than generic ones.** This isn't thst surprising -- Cramer's team found the same thing at Sentry -- but the margin is larger than I expected. A generic "check for bugs" prompt would likely miss things in the top patterns list above.

**Scale changes what you see.** At single-repo scale, data mutability was the most significant pattern. At team scale, the Python/Go split was the story. At ecosystem scale, per-team patterns and the sheer pervasiveness of things like non-string Pebble env values became visible. The methodology works at all these scales, but you get qualitatively different insights at each level.

**Human review is essential but doesn't need to be exhaustive.** The automated rounds were valuable for building the initial catalogue, but the first human review round caught systematic FP categories that automated validation couldn't. After fixing those, the remaining rounds were mostly clean. The investment was a few hours over a few days of reviewing findings, not weeks.

**Conventional commit adoption is very convenient for this kind of analysis.** Teams with high adoption (Identity at 96%) are trivial to collect data from. Teams with low adoption (K8s at 35%) need keyword scoring to avoid missing many of their fixes. This might be worth evangelising independently of the skill synthesis work - I see three conventional commit specs; we could add one to cover charming engineering.

**The iteration story is the real story.** The skill at the end of round ten is substantially different from the one at the end of round one. Anti-patterns were added, removed, and refined. False-positive controls were tightened. Domain knowledge captured in reviewer notes shaped the skill's evolution. Without a structured iteration process (and the review tool to support it), the skill would likely have plateaued much earlier.

## Filing Bugs Upstream

After completing the analysis and building the skills, I went back through the audit findings and reviewed them in detail to determine which were genuine bugs worth fixing. This turned out to be a significant filtering step — of the 52 findings across the operator and charm-tech analyses, only 11 survived human review as worth PRing (plus one that was opened and closed after closer inspection).

### operator (stages 1 and 2 combined)

From the operator-specific analysis (13 findings) and the charm-tech supplementary analysis (7 more), detailed review produced **4 merged-worthy PRs** and closed 1:

| PR | Description |
|----|-------------|
| [#2376](https://github.com/canonical/operator/pull/2376) | Harness `relation_get()` returns copy instead of direct reference |
| [#2378](https://github.com/canonical/operator/pull/2378) | Timezone-aware datetimes in expiry calculation and file info |
| [#2379](https://github.com/canonical/operator/pull/2379) | Scenario `secret_get()` and `action_get()` return copies |
| [#2380](https://github.com/canonical/operator/pull/2380) | Scenario deep-copies layer objects during plan rendering |
| [#2377](https://github.com/canonical/operator/pull/2377) | *(Closed)* Secret temp file permissions — false positive (`TemporaryDirectory` already provides `0o700` protection) |

Key false positives caught during review: `secret-set` does accept `--owner` (retracted), `Service.to_dict()` dropping `user-id: 0` is not a real bug (Pebble runs as root), `_event_context()` missing `try/finally` only affects Harness (mostly unmaintained, Scenario has its own mechanism).

### charm-tech (stage 2)

From the broader team analysis, review produced **5 PRs** across 3 repos:

| Repo | PR | Description |
|------|-----|-------------|
| charmlibs | [#363](https://github.com/canonical/charmlibs/pull/363) | passwd `TypeError` with printf-style formatting |
| pytest-jubilant | [#25](https://github.com/canonical/pytest-jubilant/pull/25) | Wrong exception attribute in model-exists check |
| concierge | [#166](https://github.com/canonical/concierge/pull/166) | MicroK8s copy-paste bug using Google's config |
| concierge | [#163](https://github.com/canonical/concierge/pull/163) | `writeCredentials` overwrites map instead of merging |
| concierge | [#164](https://github.com/canonical/concierge/pull/164) | `RunWithRetries` retries permanent errors for 5 minutes |
| concierge | [#165](https://github.com/canonical/concierge/pull/165) | Disabled snaps treated as uninstalled |

Key false positives caught: `lxd init --minimal` is idempotent (tested directly — it succeeds on re-run), UID/GID 0 falsy checks in passwd are not real bugs (UID 0 already exists as root), all snap library findings skipped (rewrite pending). All 5 pebble findings skipped as too narrow, documented workarounds, or design-level concerns.

Full details in the coda sections of [operator-analysis/WRITEUP.md](operator-analysis/WRITEUP.md#coda-filing-the-bugs-upstream) and [charm-tech-analysis/WRITEUP.md](charm-tech-analysis/WRITEUP.md#coda-filing-the-bugs-upstream).

## Files

Each stage has its own directory with a detailed write-up:

* **[operator-analysis/](operator-analysis/)** — Single-repo analysis, initial skill, methodology proof. Start here for the approach (I didn't know I would go further than this when starting it).
* **[charm-tech-analysis/](charm-tech-analysis/)** — Team-scale analysis, Python/Go split, cross-repo patterns.
* **[charming-analysis/](charming-analysis/)** — Full ecosystem analysis, 10 validation rounds, review tool, final skill. The bulk of the data and findings are here.

The final skill itself is at [`charming-analysis/.claude/skills/charm-find-bugs/`](charming-analysis/.claude/skills/charm-find-bugs/). I might put it in [copilot-collections](https://github.com/canonical/copilot-collections) or some other more visible place later.
