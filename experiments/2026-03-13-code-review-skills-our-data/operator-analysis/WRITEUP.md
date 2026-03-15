# Synthesising a Bug-Finding Skill for the Operator Repository

I came across David Cramer's [Skill Synthesis](https://cra.mr/skill-synthesis) post a while back and found the core idea compelling: rather than giving an LLM generic guidelines and hoping for the best, feed it your project's actual history of mistakes and let it learn your specific patterns. Cramer's team at Sentry did this for security vulnerabilities and found eight genuine issues that had survived years of human review. I wanted to try the same approach with [ops](https://github.com/canonical/operator) — the Python framework I work on at Canonical for building Juju charms.

The question was straightforward: can you take seven years of bug fixes, distil them into something an AI agent can use, and have it find real bugs in the current code?

## The raw material

The operator repository has around 2,000 commits on main. Of those, 235 are bug fixes — some tagged with conventional commit `fix:` (or `fix!:`) prefixes, others from the pre-conventional era that required a bit more digging to identify. I used Claude Code to classify and analyse all of them, producing three things:

1. **Individual commit summaries** — a markdown file per fix, with the diff, root cause analysis, and categorisation by severity, area, and bug type.
2. **A bug patterns document** — a synthesis of recurring patterns across all 235 fixes, grouped into 13 categories.
3. **A current code audit** — the patterns applied against the current HEAD to see what might be still lurking.

The whole data collection phase ran in about 23 minutes wall-clock time, with several agents working in parallel on different severity bands. The classification broke down to 15 high severity, 184 medium, and 36 low (those are Claude's classifications), spread across the expected areas: relation data handling (I'm probably personally responsible for many of these), Pebble containers, secrets management, the testing frameworks, and so on.

Something I noticed during the analysis was how persistent certain patterns are (basically: we keep making similar mistakes). Data mutability bugs — passing dicts around without copying them — have been fixed at least six separate times across the codebase's history. Each time the fix is straightforward (often: add `.copy()`), but the pattern keeps recurring, maybe because it's subtle and easy to miss in review.

## Building the skill

Cramer's approach uses Claude Code's "skills" system — essentially structured instruction sets that get injected into the agent's context when triggered. The skill framework supports a "Domain Expert" pattern where a main `SKILL.md` file orchestrates conditional loading of reference material, so the agent only loads what's relevant to the code it's reviewing rather than stuffing everything into context at once.

(And yes, I was very keen on skills a few months back, and recently have been increasingly skeptical, but it does seem like something very focused and local like this might be a good fit.)

I structured the operator bug-finding skill as:

- **SKILL.md** (~140 lines) — the core workflow: determine what code area is being reviewed, search for known anti-patterns, check cross-cutting concerns, verify findings, and report in a structured format.
- **references/bug-patterns.md** (~370 lines) — the full pattern catalogue derived from the 235 fixes, organised by category (security, data mutability, relation data, secrets, Pebble, testing divergence, etc.) with before/after code examples and links to the commits that fixed each pattern.
- **references/anti-patterns.md** (~300 lines) — concrete grep-able code patterns, each with what to search for, how to distinguish a true bug from a false positive, and the correct fix.

The false-positive controls turned out to be just as important as the patterns themselves. Without them, the agent flags every `return self._data[key]` as a potential mutability bug, even when the values are immutable primitives. The skill includes a table of known-safe patterns specific to this repo — things like `ConfigData.__getitem__` returning strings, or the `on` event emitter attribute being intentionally returned by reference.

## First test run

The first run targeted the areas covered by the existing code audit: `ops/hookcmds/`, `ops/_private/harness.py`, `ops/model.py`, and `testing/src/scenario/mocking.py`.

It found four bugs (1 high, 2 medium, 1 low) and correctly dismissed five suspicious patterns as false positives. (A fifth finding — `--owner` being passed to `secret-set` — was initially reported as a high-severity bug, but human (me!) review against the [Juju documentation](https://documentation.ubuntu.com/juju/latest/reference/hook-command/list-of-hook-commands/secret-set/) confirmed that `secret-set` does accept `--owner`, making this a false positive.) The findings were accurate — they matched the code audit exactly. But that was also the problem: they *only* matched the code audit. The skill was good at confirming known issues but wasn't finding anything new. It was essentially pattern-matching against the reference material rather than genuinely investigating the code.

## Iterating

First, I added a "hunt for novel bugs" step to the workflow — explicit instructions to go beyond pattern matching:

- Read each file end-to-end rather than only looking at grep matches. (If you're reading this James, this one is dedicated to you.)
- Trace 3–5 public API call chains from caller to callee and look for assumption violations.
- Diff parallel implementations side-by-side (if something is implemented in both ops and the Harness testing backend and the Scenario testing backend, compare all three).
- Check recent commits, since recently changed code is statistically more likely to contain bugs (because it hasn't been exercised as much, not a comment on team members).
- Look for incomplete fixes — when a bug was fixed in one place, search for the same pattern in analogous code.

Second, I expanded the anti-patterns reference from thirteen searchable patterns to 24, adding categories that the first run had no guidance for: event framework issues, import cycles, `__all__` completeness, incomplete mutation guards (where a class overrides `__setitem__` but forgets `update()` and `pop()`), and more.

## Second test run

The second run targeted different files: `ops/pebble.py`, `ops/framework.py`, `ops/charm.py`, `ops/jujucontext.py`, and `testing/src/scenario/state.py`. I explicitly excluded the five known bugs from the first run to force it to find new things.

It found six new bugs:

| Severity | Description |
|----------|-------------|
| **High** | `_event_context` context manager doesn't wrap its `yield` in `try/finally` — if an event handler raises, `_hook_is_running` stays stale for subsequent dispatches |
| Medium | Scenario `secret_get` returns internal dict without `.copy()` (the relation equivalent was fixed, but nobody applied the same fix to secrets) |
| Medium | Scenario `Secret._update_metadata` uses naive `datetime.now()` despite the same file defining a `_now_utc()` helper |
| Medium | `Secret._update_metadata` uses `if content:` instead of `if content is not None:`, silently skipping empty dicts and empty strings |
| Medium | `PebbleNoticeEvent.restore()` uses `snapshot.pop()` (destructive) while every other `restore` method in the codebase uses non-destructive access |
| Low | `Service._merge` drops `user_id=0` during layer merging because `not 0` is `True` |

(Severity is again a Claude choice. A couple of these I'm suspicious of, so will investigate further to verify they are real problems.)

The high-severity finding — the missing `try/finally` in `_event_context` — is particularly interesting because it's not a pattern from any of the 235 historical bugs. It was found by the "read the file end-to-end" instruction rather than by grep-matching against known anti-patterns (so in many ways is evidence on the "we don't need a skill" side). The "incomplete fix" strategy also paid off: the Scenario `secret_get` copy bug (BUG-007) is the exact same class of issue as the `relation_get` copy bug that was fixed in commit `be090122`, just in a different method that nobody thought to check at the time.

## Is this actually useful?

Across both test runs, the skill found ten bugs — one high, seven medium, two low (an eleventh finding was retracted after initial human (me again, :waves:) review — see below). Several of these are issues that could cause real problems in production charms (assuming detailed review confirms them). That's a potentially meaningful result for what amounted to a few hours of work, most of it automated.

But let's be honest about the limitations:

**It's strongest at finding pattern variants.** The best finds were cases where a known bug class existed in analogous code — the secret copy bug mirroring the relation copy bug, the naive datetime in Scenario mirroring the one in ops. This makes sense: the skill has a catalogue of patterns and is good at finding instances of those patterns that humans missed. It's weaker at finding genuinely novel bug classes (and would likely perform equally well without the skill), though the end-to-end reading step did surface the `try/finally` issue.

**False-positive control matters enormously.** Without the known-safe patterns table, the signal-to-noise ratio would be poor. Every `return self._something` would be flagged. The domain-specific knowledge about what's immutable, what's intentionally returned by reference, and what's protected by other mechanisms is what makes the output actionable rather than overwhelming.

**It mostly confirms what the Skill Synthesis post argued.** Generic review skills (such as the `find-bugs` and `security-review` skills in the Sentry repo) would not have found most of these issues. They don't know that Juju relation data is `dict[str, str]`, or that the Harness and Scenario backends need to behave identically to real Juju. (That said, domain-specific skills are not immune to false positives either — the initial audit incorrectly flagged `secret-set` as not accepting `--owner`, which human review confirmed was wrong.) The domain specificity is doing the heavy lifting.

## What's next

(The actual next step is in the parent directory: at the time I wrote this I didn't know I would go broader.)

A few directions seem worth exploring:

**Running against diffs rather than the full codebase.** The skill currently audits files end-to-end, but the more natural use case is reviewing a PR. The cross-cutting concern checks (did you mirror this fix in Harness? in Scenario?) would be particularly valuable during code review. [Looking into Warden](https://warden.sentry.dev/), maybe.

**Expanding to charm code.** The skill currently targets the `ops` framework itself, but the bug patterns are possibly relevant to charms *using* ops. A charm-focused variant could check for common mistakes like mutating relation data returned by `relation_get`, accessing data after `relation-broken`, or using falsy checks on config values.

**Connecting to CI.** Cramer's team built their skill into a GitHub integration that comments on PRs. The same approach could work here — run the skill on every PR to the operator repo and flag any matches for human review. GitHub Copilot reviews, but targetted to complement the generic.

**Feeding back new bugs.** Each bug the skill finds (or misses) is training data for the next iteration. The anti-patterns reference should grow over time as new bug classes are discovered and fixed.

I think my two main conclusions are (a) skills may still have some value, and (b) this feels less "AI"y and more like automating of the past, so immediately more approachable (excepting the training part, that's where LLMs have sped things up). A generic "find bugs" prompt produces generic results. Two hundred and thirty-five analysed bug fixes, distilled into searchable patterns with false-positive controls, produces something that finds issues that humans have been missing. The effort of building the domain-specific skill is what makes the difference — and that effort is, itself, largely automatable.

## Coda: Filing the bugs upstream

After the analysis and skill development, I reviewed the current code audit findings in detail to determine which were genuine bugs worth fixing. Of the 13 findings (2 high, 6 medium, 5 low), the breakdown was:

### PRs opened

**[fix: return copy of relation data from Harness backend (#2376)](https://github.com/canonical/operator/pull/2376)** — Finding H-2. The Harness `relation_get()` method returns a direct reference to internal `_relation_data_raw` dict state, meaning charm mutations silently corrupt the Harness's data. The Scenario mock backend had the exact same bug and it was already fixed (commit `be090122` — `data.copy()`). One-line fix applying the same pattern. This is the most clear-cut bug from the audit, but is in Harness, which is mostly unmaintained at this point.

**[fix: use timezone-aware datetimes in expiry calculation and file info (#2378)](https://github.com/canonical/operator/pull/2378)** — Findings M-2 and M-3, bundled together. `_calculate_expiry()` uses `datetime.datetime.now()` (naive) when computing secret expiry from a timedelta, and `Container._build_fileinfo()` uses `datetime.fromtimestamp()` (also naive). Both should use UTC-aware datetimes: the expiry gets serialised to RFC 3339 for Juju, and naive datetimes omit timezone information, which Juju may misinterpret. Fixed to `datetime.datetime.now(tz=datetime.timezone.utc)` and `datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)` respectively.

**[fix: restrict permissions on secret temporary files (#2377)](https://github.com/canonical/operator/pull/2377)** — Finding H-3. `secret_add()` and `secret_set()` write secret content to temporary files with default permissions (typically `0o644`). The audit flagged this as a security risk based on the precedent of commit `e4b0f9d4` (restricting SQLite storage file permissions to `0o600`). However, on closer inspection this turned out to be a false positive: `tempfile.TemporaryDirectory()` creates the parent directory with `0o700` permissions, so the files inside are already inaccessible to other users regardless of individual file permissions. **Closed without merging.** I was skeptical about this all along, but Claude mistook my "let's review the findings and open PRs with fixes" for something non-interactive, and opened PRs before I reviewed and before I had a chance to pause it.

### Findings not worth a PR

Seven of the remaining findings were confirmed as false positives or too minor to warrant changes:

- **H-1** (retracted): `secret-set` passing `--owner` was flagged as an invalid argument, but [Juju's documentation](https://documentation.ubuntu.com/juju/latest/reference/hook-command/list-of-hook-commands/secret-set/) confirms `secret-set` does accept `--owner`.
- **M-1** (speculative): `dataclasses.asdict()` deep-converting nested dataclasses with aliased fields is a theoretical concern — the current code handles flat dataclasses correctly and no charm has hit this edge case.
- **M-4** (charm-side bug): Harness `config_get()` returns `_TestingConfig` directly, and inherited `dict.update()`/`pop()`/`clear()` bypass the `__setitem__` override. But a charm calling these methods would also fail in production — `ConfigData` is read-only. The Harness not catching the error is a minor testing fidelity issue, not a framework bug.
- **M-5** (documented limitation): Scenario `relation_set()` operating on the same dict as `RelationDataContent` is explicitly acknowledged in the code comments as a known deviation from production behaviour. A proper fix would require rearchitecting Scenario's data storage.
- **M-6** (too minor): `_ModelCache` storing `meta` without copying is technically a shared-state concern, but `CharmMeta` is treated as immutable everywhere. Defensive copying would add overhead for no practical benefit.
- **L-1** (by design): Pebble `_MultipartParser.get_file()` opens a file without a context manager, but this is intentional (marked with `# noqa: SIM115`) — the caller manages the lifecycle.
- **L-2, L-3, L-5** (false positives): Static analysis flags on immutable return values (`bool | int | float | str`), safe `.get()` chains with non-`None` defaults, and the `on` event emitter attribute being returned by reference (required for event observation to work).
- **L-4** (too minor): `_TestingConfig` storing the config spec without copying — the spec is parsed once and never modified.

### Observations

The end-to-end process — from audit findings to merged PRs — surfaced an important filtering step that the skill alone doesn't provide. Of the thirteen findings, only two survived detailed human review as genuinely worth fixing (only one depending on how you view Harness). The skill's false-positive controls help at the detection stage, but there's a second layer of judgement needed: understanding the broader context (like `TemporaryDirectory` providing directory-level protection) that a pattern-matching approach can miss. This is consistent with the write-up's broader conclusion that domain-specific skills are valuable but not a substitute for human review.
