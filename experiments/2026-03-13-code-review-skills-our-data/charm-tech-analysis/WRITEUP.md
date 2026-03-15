# Scaling Skill Synthesis Across an Entire Team's Repositories

The [previous experiment](../operator-analysis/WRITEUP.md) took one repository — [canonical/operator](https://github.com/canonical/operator) — and turned 235 historical bug fixes into a Claude Code skill that found 11 bugs (1-2 worth fixing). The natural question was: what happens when you do the same thing across an entire team's codebase? Will the results be more useful?

The Canonical [Charm Tech team](https://github.com/orgs/canonical/teams/charm-tech/repositories) maintains around fifteen repositories (it was 2-3 just a few years ago when I joined!). Most are Python, but two — [Pebble](https://github.com/canonical/pebble) (a lightweight service manager) and [Concierge](https://github.com/canonical/concierge) (a provisioning tool) — are Go. They range from the 2,000-commit `operator` repository down to small utility repos with a few dozen commits. The question was whether a broader analysis would produce more compelling skills, and whether the patterns that recur within one repo also recur across repos of the same team — or whether each codebase has its own distinct screw-ups.

## The dataset

After excluding archived repos, demos, and one repo that isn't really ours, I ended up with ten repositories to analyse:

| Repository | Language | Commits | Fix candidates |
|------------|----------|---------|---------------|
| operator | Python | 2,000 | 218 |
| pebble | Go | 564 | 108 |
| concierge | Go | 211 | 35 |
| operator-libs-linux | Python | 230 | 29 |
| charmlibs | Python | 284 | 19 |
| jubilant | Python | 177 | 18 |
| charmcraft-profile-tools | Python | 59 | 7 |
| charm-ubuntu | Python | 58 | 7 |
| charmhub-listing-review | Python | 33 | 6 |
| pytest-jubilant | Python | 77 | 5 |

The extraction followed the same methodology as before: conventional `fix:` commits pulled directly, older commits scored by keyword and classified by threshold. The total came to 452 fix candidates across all repos. Six parallel agents classified them — one per repo group — producing per-commit summaries with bug area, type, severity, and fix category.

The severity (again I let Claude pick this) breakdown across the full dataset: 102 high (23%), 233 medium (52%), 117 low (26%). Logic errors dominate at 32% of all fixes, which is both unsurprising and unhelpful — "logic error" is too broad a category to turn into a searchable pattern. The interesting findings are in the more specific categories.

## What patterns recur across repos?

Eight patterns appeared in three or more repositories. The ones that matter most for skill-building are the ones that are both frequent and detectable:

**Falsy value confusion** turned out to be the single most pervasive pattern in the current code audits — more so than I expected. The bug is always the same: using `if value` where `if value is not None` is needed, causing 0, empty string, or False to be silently treated as "not provided". It shows up a lot: UID 0 dropped in passwd operations, `user-id: 0` dropped in Pebble service configs (although would this really happen, given who UID 0 is?), `num_lines=0` returning all logs instead of zero (unless rhis is the design pattern I dislike where 0 means 'off'). The fix is trivially simple every time, which is probably why the pattern persists — it's easy to write `if uid:` and not think twice.

**Data mutability** continues to be the highest severity-to-frequency ratio pattern in Python. Every instance is high severity (says Claude), and the fix is typically adding `.copy()` or `dict()`. The cross-repo analysis revealed something I failed to think about: charmlibs has a migration of libraries from operator-libs-linux  — meaning 8 of the 15 bugs I found in the Python repos audit exist in *both* repos, faithfully copied. Claude saw something meaningful in this, but really I should just have excluded one from the analysis.

**Testing/production divergence** remains the largest single area at 51 fixes, but it's essentially unique to `operator` (which maintains both Harness (kinda) and Scenario testing frameworks). The cross-repo perspective didn't add much here — it's an operator-specific problem.

The most interesting cross-repo finding was probably the **Juju CLI argument formatting** pattern. Every single wrapper around the `juju` or `snap` CLI — across `operator`, `jubilant`, and `operator-libs-linux` — has had argument formatting bugs. `--bind` uses spaces not commas. `juju offer` doesn't accept `--model`. Snap CLI args have literal `"` characters embedded because someone wrote `f'--channel="{channel}"'` in a subprocess argument list. The pattern is clear: whatever the CLI documentation says, you will get the argument format wrong on the first try.

## Python and Go have almost no overlap

This was the key finding that shaped the skill design. I went into the analysis wondering if I could build one skill, maybe with language-conditional sections. The data (and Claude) said otherwise.

The Python patterns are about mutability, falsy values, dict access, testing parity, and Juju domain semantics. The Go patterns are about concurrency, nil maps, error wrapping, and resource lifecycle. The overlap is limited to genuinely universal things like "check edge cases" and "handle errors" — too broad to be useful as searchable patterns.

Pebble's dominant bug pattern is **concurrency** — specifically deadlocks from inconsistent lock ordering across its `servicesLock`, `state lock`, and `planLock`. Nineteen instances, 76% high severity. This is the most dangerous pattern in the entire dataset, and it's entirely Go-specific. The sub-patterns are interesting (Claude is helping out this novice Go developer here): `net/http` panic recovery while a lock is held (leaving the lock permanently held, deadlocking the entire daemon), `sync.Cond.Broadcast()` called outside the Cond's lock (signal missed), and `tomb.Tomb` created without a goroutine started on it (blocking forever on `Wait()`).

Concierge's dominant pattern (if a repository so new can have one) is **idempotency** — operations that work fine the first time but fail on re-run. `lxd init --minimal` without checking if LXD is already initialised. Stopping a service for refresh but never restarting it. Removing a directory when the thing using it is already running. These are the kinds of bugs you only find in production or in CI, and they're hard to catch in review because the happy path looks correct.

So: two skills.

## Building the skills

Both skills follow the Domain Expert pattern from the [first experiment](../operator-analysis/WRITEUP.md) — a main `SKILL.md` orchestrating conditional loading of reference material:

**charm-python-find-bugs** covers the 8 Python repos:
- `SKILL.md` (144 lines) — 6-step workflow: scope → search → hunt → cross-cutting → verify → report
- `references/bug-patterns.md` (525 lines) — 16 pattern categories with before/after code and commit precedents
- `references/anti-patterns.md` (288 lines) — 29 grep-able search patterns with false-positive guidance

**charm-go-find-bugs** covers Pebble and Concierge:
- `SKILL.md` (141 lines) — same workflow, adapted for Go-specific concerns (lock tracing, nil map checks)
- `references/bug-patterns.md` (492 lines) — 14 pattern categories
- `references/anti-patterns.md` (215 lines) — 21 grep-able search patterns

The Python skill's cross-cutting concerns section checks for mutability, falsy values, None guards, context manager safety, testing parity, type confusion, and exception constructors. The Go skill checks for lock ordering, nil map guards, error wrapping, deferred cleanup, idempotency, retry discrimination, and symlink safety in ownership operations.

Both skills include false-positive controls — tables of patterns that look suspicious but are confirmed safe. These were important in the first experiment and remain so here.

## Current code audit

Before building the skills, I ran pattern-based audits against all 10 repos. The agents found 39 bugs across the codebase:

| Repo | High | Medium | Low | Total |
|------|------|--------|-----|-------|
| Concierge | 2 | 7 | 3 | 12 |
| Python repos (4) | 2 | 9 | 4 | 15 |
| Operator | 2 | 3 | 2 | 7 |
| Pebble | 0 | 3 | 2 | 5 |
| **Total** | **6** | **22** | **11** | **39** |

The findings, which argue that a skill is not needed:

In **Concierge**, a copy-paste bug where the MicroK8s provider reads Google's `ModelDefaults` and `BootstrapConstraints` instead of its own. Also, `writeCredentials` replaces the entire credentials map on each loop iteration, so if two providers have credentials, only the last one survives.

In **charmlibs and operator-libs-linux**, the falsy value pattern is everywhere: `if uid` drops UID 0, `if gid` drops GID 0, `if num_lines` drops zero. And snap CLI arguments have literal `"` characters embedded in six call sites across both repos.

## Testing the skills

The real test: do the skills actually work? I ran each skill against the repos it was designed for, using fresh agents that had never seen the audit results.

### Recall

| Repo | Known bugs | Found | Recall |
|------|-----------|-------|--------|
| Operator | 7 | 6 | 86% |
| Pebble | 5 | 5 | 100% |
| Concierge | 12 | 10 | 83% |
| Charmlibs | 7 | 6 | 86% |
| **Total** | **31** | **27** | **87%** |

All four missed bugs were low severity. The skills achieved **100% recall on high and medium severity findings**.

### Novel bugs

More interesting than recall (and serving as the pro-skill argument) is whether the skills find things the original audit *didn't*. They found six:

| Repo | Bug | Severity |
|------|-----|----------|
| Charmlibs | Password passed as CLI arg to `useradd`, visible in `/proc` and `ps` | **Critical** |
| Pebble | `mkdir` temp dir leak on Chown/Chmod/Rename failure | Medium |
| Pebble | `FchownAt` with `flags=0` follows symlinks | Medium |
| Operator | Falsy value pattern in `Check.to_dict()` and `LogTarget.to_dict()` | Medium |
| Operator | `datetime.now()` without timezone in 6+ locations | Low |
| Concierge | `credentials.yaml` written with 0644 permissions | Low |

(At time of writing I have not manually confirmed these. I will add a coda where I do so.)

The charmlibs finding is the best one. The `add_user()` function passes the password as a command-line argument to `useradd`, which means it's visible to any process on the system via `/proc` or `ps`. This is a genuine security vulnerability that wasn't in any of the historical bug fixes — the skill found it through its security pattern checks (looking for credential exposure in CLI argument construction). It's exactly the kind of thing that generic code review misses because the code *works correctly*; the problem is purely about information exposure.

### Precision

Zero false positives Isubjedt to final human review) across 33 findings in four test runs. The false-positive controls are earning their keep.

## What scaling up taught me

**The two-skill split was the right call.** Python and Go bug patterns have essentially zero overlap. A single combined skill would have been larger, loaded irrelevant patterns, and produced worse results. The data made this obvious — I didn't have to guess.

**Cross-repo patterns are more interesting than within-repo patterns.** The falsy value pattern appeared in the single-repo analysis (the `Service._merge` dropping `user_id=0` finding was in the first writeup), but I didn't appreciate how pervasive it was until I saw it independently in `passwd`, `snap`, and Pebble config across multiple repos. The same is true for the Juju CLI formatting pattern — each individual instance looks like a one-off mistake, but across repos it's clearly a systematic problem with how the team wraps CLI tools.

**The novel findings may justify the effort.** If the skills only found what the audits already found, they'd be a nice-to-have verification tool. The six novel bugs — especially the security issue in charmlibs — demonstrate that the skills (and LLMs) can find things that careful manual analysis misses. The skills encode the patterns in a way that's more systematic and less likely to overlook a call site than a human doing a targeted audit.

**Scale helps pattern quality but not proportionally.** Going from 235 fixes (`operator` only) to 452 fixes (all repos) roughly doubled the input data, but the pattern catalogue didn't double — it went from thirteen categories to sixteen for Python and fourteen for Go. The additional data mostly added evidence and examples to existing patterns rather than revealing entirely new ones. The exceptions were the Go-specific patterns (concurrency, nil maps, tomb lifecycle) which were invisible in a Python-only analysis, and the snap/Juju CLI patterns which needed multiple repos to recognise as systematic.

## What's next

(The actual next step can be found in the folder above this one. When I did the write-up I hadn't decided to go charming wide.)

This analysis produced two things: the skills themselves, and some bugs that should be carefully reviewed and fixed if needed.

For the skills, the directions from the [first writeup](../operator-analysis/WRITEUP.md) still apply: running against diffs rather than full codebases, integrating into CI, and feeding new bugs back into the pattern catalogue.

The Go skill also opens up something the Python-only analysis couldn't do: **architectural pattern detection**. The concurrency patterns in Pebble aren't individual bugs so much as symptoms of an architecture that makes certain classes of bugs easy to write. A skill that understands the lock ordering constraints could flag new code that acquires locks in a novel order, before it deadlocks in production. That's more of a linter than a bug finder, but the line between the two has always been blurry.

The broader point is the same one from last time, just with more evidence behind it: domain-specific skills that encode your project's actual history of mistakes are more effective than generic code review prompts. Scaling from one repo to ten made the skills better — not dramatically better, but measurably better, with broader pattern coverage, cross-repo validation, and the ability to catch bugs that propagate between codebases. The effort of building the skills is itself largely automated, which means the main bottleneck is having a history of bugs to learn from. Fortunately, most projects have plenty!
