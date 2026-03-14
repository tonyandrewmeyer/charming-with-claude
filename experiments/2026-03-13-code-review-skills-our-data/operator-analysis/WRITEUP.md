# Synthesising a Bug-Finding Skill for the Operator Framework

I came across David Cramer's [Skill Synthesis](https://cra.mr/skill-synthesis) post a few weeks ago and found the core idea compelling: rather than giving an LLM generic security guidelines and hoping for the best, feed it your project's actual history of mistakes and let it learn your specific patterns. Cramer's team at Sentry did this for security vulnerabilities and found 8 genuine issues that had survived years of human review. I wanted to try the same approach with [ops](https://github.com/canonical/operator) — the Python framework I work on for building Juju charms.

The question was straightforward: can you take 7 years of bug fixes, distil them into something an AI agent can use, and have it find real bugs in the current code?

## The raw material

The operator repository has around 2,000 commits on main. Of those, 235 are bug fixes — some tagged with conventional commit `fix:` prefixes, others from the pre-conventional era that required a bit more digging to identify. I used Claude Code to classify and analyse all of them, producing three things:

1. **Individual commit summaries** — a markdown file per fix, with the diff, root cause analysis, and categorisation by severity, area, and bug type.
2. **A bug patterns document** — a synthesis of recurring patterns across all 235 fixes, grouped into 13 categories.
3. **A current code audit** — the patterns applied against the current HEAD to see what's still lurking.

The whole data collection phase ran in about 23 minutes wall-clock time, with several agents working in parallel on different severity bands. The classification broke down to 15 high severity, 184 medium, and 36 low, spread across the expected areas: relation data handling, Pebble containers, secrets management, the testing frameworks, and so on.

What struck me most during the analysis was how persistent certain patterns are. Data mutability bugs — passing dicts around without copying them — have been fixed at least 6 separate times across the codebase's history. Each time the fix is straightforward (add `.copy()`), but the pattern keeps recurring because it's subtle and easy to miss in review.

## Building the skill

Cramer's approach uses Claude Code's "skills" system — essentially structured instruction sets that get injected into the agent's context when triggered. The skill framework supports a "Domain Expert" pattern where a main `SKILL.md` file orchestrates conditional loading of reference material, so the agent only loads what's relevant to the code it's reviewing rather than stuffing everything into context at once.

I structured the operator bug-finding skill as:

- **SKILL.md** (~140 lines) — the core workflow: determine what code area is being reviewed, search for known anti-patterns, check cross-cutting concerns, verify findings, and report in a structured format.
- **references/bug-patterns.md** (~370 lines) — the full pattern catalogue derived from the 235 fixes, organised by category (security, data mutability, relation data, secrets, Pebble, testing divergence, etc.) with before/after code examples and links to the commits that fixed each pattern.
- **references/anti-patterns.md** (~300 lines) — concrete grep-able code patterns, each with what to search for, how to distinguish a true bug from a false positive, and the correct fix.

The false-positive controls turned out to be just as important as the patterns themselves. Without them, the agent flags every `return self._data[key]` as a potential mutability bug, even when the values are immutable primitives. The skill includes a table of known-safe patterns specific to this codebase — things like `ConfigData.__getitem__` returning strings, or the `on` event emitter attribute being intentionally returned by reference.

## First test run

The first run targeted the areas covered by the existing code audit: `ops/hookcmds/`, `ops/_private/harness.py`, `ops/model.py`, and `testing/src/scenario/mocking.py`.

It found 4 bugs (1 high, 2 medium, 1 low) and correctly dismissed 5 suspicious patterns as false positives. (A fifth finding — `--owner` being passed to `secret-set` — was initially reported as a high-severity bug, but human review against the [Juju documentation](https://documentation.ubuntu.com/juju/latest/reference/hook-command/list-of-hook-commands/secret-set/) confirmed that `secret-set` does accept `--owner`, making this a false positive.) The findings were accurate — they matched the code audit exactly. But that was also the problem: they *only* matched the code audit. The skill was good at confirming known issues but wasn't finding anything new. It was essentially pattern-matching against the reference material rather than genuinely investigating the code.

## Iterating

The fix was twofold.

First, I added a "hunt for novel bugs" step to the workflow — explicit instructions to go beyond pattern matching:

- Read each file end-to-end rather than only looking at grep matches.
- Trace 3–5 public API call chains from caller to callee and look for assumption violations.
- Diff parallel implementations side-by-side (if something is implemented in both ops and the Harness testing backend and the Scenario testing backend, compare all three).
- Check recent commits, since recently changed code is statistically more likely to contain bugs.
- Look for incomplete fixes — when a bug was fixed in one place, search for the same pattern in analogous code.

Second, I expanded the anti-patterns reference from 13 searchable patterns to 24, adding categories that the first run had no guidance for: event framework issues, import cycles, `__all__` completeness, incomplete mutation guards (where a class overrides `__setitem__` but forgets `update()` and `pop()`), and more.

## Second test run

The second run targeted different files: `ops/pebble.py`, `ops/framework.py`, `ops/charm.py`, `ops/jujucontext.py`, and `testing/src/scenario/state.py`. I explicitly excluded the 5 known bugs from the first run to force it to find new things.

It found 6 new bugs:

| Severity | Description |
|----------|-------------|
| **High** | `_event_context` context manager doesn't wrap its `yield` in `try/finally` — if an event handler raises, `_hook_is_running` stays stale for subsequent dispatches |
| Medium | Scenario `secret_get` returns internal dict without `.copy()` (the relation equivalent was fixed, but nobody applied the same fix to secrets) |
| Medium | Scenario `Secret._update_metadata` uses naive `datetime.now()` despite the same file defining a `_now_utc()` helper |
| Medium | `Secret._update_metadata` uses `if content:` instead of `if content is not None:`, silently skipping empty dicts and empty strings |
| Medium | `PebbleNoticeEvent.restore()` uses `snapshot.pop()` (destructive) while every other `restore` method in the codebase uses non-destructive access |
| Low | `Service._merge` drops `user_id=0` during layer merging because `not 0` is `True` |

The high-severity finding — the missing `try/finally` in `_event_context` — is particularly interesting because it's not a pattern from any of the 235 historical bugs. It was found by the "read the file end-to-end" instruction rather than by grep-matching against known anti-patterns. The "incomplete fix" strategy also paid off: the Scenario `secret_get` copy bug (BUG-007) is the exact same class of issue as the `relation_get` copy bug that was fixed in commit `be090122`, just in a different method that nobody thought to check at the time.

## Is this actually useful?

Across both test runs, the skill found 10 confirmed bugs — 1 high, 7 medium, 2 low (an eleventh finding was retracted after human review — see below). Several of these are genuine issues that could cause real problems in production charms (the `_event_context` one being the most impactful). That's a meaningful result for what amounted to a few hours of work, most of it automated.

But I want to be honest about the limitations:

**It's strongest at finding pattern variants.** The best finds were cases where a known bug class existed in analogous code — the secret copy bug mirroring the relation copy bug, the naive datetime in Scenario mirroring the one in ops. This makes sense: the skill has a catalogue of patterns and is good at finding instances of those patterns that humans missed. It's weaker at finding genuinely novel bug classes, though the end-to-end reading step did surface the `try/finally` issue.

**False-positive control matters enormously.** Without the known-safe patterns table, the signal-to-noise ratio would be poor. Every `return self._something` would be flagged. The domain-specific knowledge about what's immutable, what's intentionally returned by reference, and what's protected by other mechanisms is what makes the output actionable rather than overwhelming.

**It confirms what the Skill Synthesis post argued.** Generic security review skills (the existing `find-bugs` and `security-review` skills in the same repo) would not have found most of these issues. They don't know that Juju relation data is `Dict[str, str]`, or that the Harness and Scenario backends need to behave identically to real Juju. (That said, domain-specific skills are not immune to false positives either — the initial audit incorrectly flagged `secret-set` as not accepting `--owner`, which human review against the [Juju documentation](https://documentation.ubuntu.com/juju/latest/reference/hook-command/list-of-hook-commands/secret-set/) confirmed was wrong.) The domain specificity is doing the heavy lifting.

## What's next

A few directions seem worth exploring:

**Running against diffs rather than the full codebase.** The skill currently audits files end-to-end, but the more natural use case is reviewing a PR. The cross-cutting concern checks (did you mirror this fix in Harness? in Scenario?) would be particularly valuable during code review.

**Expanding to charm code.** The skill currently targets the ops framework itself, but the bug patterns are equally relevant to charms *using* ops. A charm-focused variant could check for common mistakes like mutating relation data returned by `relation_get`, accessing data after `relation-broken`, or using falsy checks on config values.

**Connecting to CI.** Cramer's team built their skill into a GitHub integration that comments on PRs. The same approach would work here — run the skill on every PR to the operator repo and flag any matches for human review.

**Feeding back new bugs.** Each bug the skill finds (or misses) is training data for the next iteration. The anti-patterns reference should grow over time as new bug classes are discovered and fixed.

The broader takeaway, for me, is that LLMs are genuinely useful for this kind of work when you give them the right context. A generic "find bugs" prompt produces generic results. Two hundred and thirty-five analysed bug fixes, distilled into searchable patterns with false-positive controls, produces something that finds real issues that humans have been missing. The effort of building the domain-specific skill is what makes the difference — and that effort is, itself, largely automatable.
