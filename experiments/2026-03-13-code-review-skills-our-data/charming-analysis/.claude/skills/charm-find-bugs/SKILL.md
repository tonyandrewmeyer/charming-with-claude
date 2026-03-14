---
name: charm-find-bugs
description: Find bugs in Juju charm operator repositories. Use when asked to "find bugs", "audit code", "review for bugs", "check for issues", "security review", or review Python code in any Juju charm. Specialized for charm-specific bug patterns including Pebble container management, relation data handling, TLS certificate lifecycle, status management, config handling, ingress/networking, Grafana dashboard wiring, and Juju interaction. Built from analysis of 6,116 historical bug fixes across 134 charm repositories spanning 10 teams (Data, Observability, MLOps, IS, Identity, Telco, Commercial Systems, K8s, BootStack, Charm-Tech).
---

# Charm Bug Finder

Find bugs in Juju charm codebases using domain-specific knowledge from 6,116 historical bug fixes across 134 repositories.

## Scope

Report on: only the files or diff the user specifies.
Research: the entire codebase to build confidence before reporting.

Do not report issues based solely on pattern matching. Investigate data flow and confirm the bug is real before reporting.

## Step 1: Determine review scope

Identify what code areas are being reviewed and load the relevant reference sections:

| Code Area | Indicators | Reference Section |
|-----------|-----------|-------------------|
| Pebble / containers | `Container`, `Layer`, `can_connect`, `replan`, `push`, `pull`, `exec` | `references/bug-patterns.md` -- Pebble |
| Relation data | `relation_get`, `relation_set`, `RelationData`, `relation_joined`, `relation_changed`, `relation_broken` | `references/bug-patterns.md` -- Relations |
| TLS / certificates | `tls`, `certificate`, `csr`, `ca_chain`, `private_key`, `x509` | `references/bug-patterns.md` -- TLS |
| Config handling | `self.config`, `config_changed`, `config.yaml` | `references/bug-patterns.md` -- Configuration |
| Status management | `ActiveStatus`, `BlockedStatus`, `WaitingStatus`, `MaintenanceStatus`, `collect_unit_status` | `references/bug-patterns.md` -- Status |
| Ingress / networking | `ingress`, `traefik`, `nginx`, `external_url`, `proxy` | `references/bug-patterns.md` -- Ingress |
| Grafana / observability | dashboard JSON, `datasource`, `prometheusds`, alert rules, `scrape_jobs` | `references/bug-patterns.md` -- Observability |
| Database interaction | connection strings, `postgresql`, `mysql`, `mongodb`, `kafka`, `dsn` | `references/bug-patterns.md` -- Database |
| Auth / identity | `oauth`, `oidc`, `saml`, `ldap`, `credentials`, `password`, `token` | `references/bug-patterns.md` -- Auth |
| Upgrade / migration | `upgrade`, `rollback`, `pre-upgrade-check` | `references/bug-patterns.md` -- Upgrade |
| Juju interaction | `model.`, `unit.`, `app.`, `leader`, `peer`, secrets, actions | `references/bug-patterns.md` -- Juju |
| Broad review / full audit | Multiple areas or unspecified | Read full `references/bug-patterns.md` |

Always read `references/anti-patterns.md` for concrete code patterns to search for.

## Step 2: Search for known bug patterns

For each relevant code area, search the codebase for the anti-patterns listed in `references/anti-patterns.md`. Use Grep with the provided search patterns.

For each match:
1. Read surrounding context (at least 20 lines around the match).
2. Trace data flow to determine if the pattern is actually buggy.
3. Check if there is an existing fix, test, or guard.
4. Only report if the bug is confirmed after investigation.

## Step 3: Hunt for novel bugs

After searching for known patterns, actively look for new bugs:

1. **Read each file in scope end-to-end** -- do not rely solely on grep matches.
2. **Trace data through call chains**: pick 3-5 public API methods and trace inputs from caller to callee. Look for:
   - Assumptions about input types that callers can violate
   - Missing validation at API boundaries
   - State changes not rolled back on error
3. **Compare parallel implementations**: for operations with both K8s and VM variants, or with multiple relation providers, diff the logic side by side. Divergences are likely bugs.
4. **Check recent commits** (`git log --oneline -20 -- <file>`): recently changed code is more likely to contain bugs.
5. **Look for incomplete fixes**: when a bug was fixed in one place, search for the same pattern in analogous code. Charms commonly share patterns across handlers -- a fix in `_on_config_changed` may be missing from `_on_upgrade_charm`.

## Step 4: Check cross-cutting concerns

Always check these regardless of code area:

1. **Pebble readiness**: Are `container.push()`, `container.restart()`, `container.replan()`, or `container.exec()` calls guarded by `container.can_connect()`?
2. **Truthiness vs explicit comparison**: Are `if value` or `if not value` checks used where `value is not None` is needed? Especially for config values that can be 0, empty string, or False.
3. **None guards on relation data**: Are relation data values checked for None before access? Check `model.get_relation()` return values. Note: `event.relation.app` and `relation.app` are always non-None in modern ops -- do NOT flag missing None guards on `.app`.
4. **Leader guards**: Are leader-only operations (app relation data writes, peer data writes) guarded by `self.unit.is_leader()`?
5. **Missing relation-broken handler**: If `relation_joined`/`relation_changed` is handled, is there a corresponding `relation_broken` handler for cleanup? Also check if the handler is *registered* with `framework.observe()` -- dead code handlers are a common bug.
6. **Status coherence**: Does every exit path from event handlers set an appropriate status? Are unit and app statuses consistent (not contradicting each other with Blocked vs Waiting for the same condition)?
7. **Credential exposure**: Are passwords, tokens, or secrets logged, written to world-readable files, or passed as CLI arguments?
8. **Operator precedence in ternary expressions**: Are `or ... if ... else` expressions on a single line missing parentheses? `value or 443 if tls else 80` parses as `(value or 443) if tls else 80`, not `value or (443 if tls else 80)`.
9. **URL construction**: Are URLs built with string concatenation instead of `urllib.parse.urljoin`? Does `urljoin` lose path segments?
10. **f-string omission**: Are format strings missing the `f` prefix, producing literal `{variable}` in output? Also check for shell-style `$VAR` mixed with Python f-strings.
11. **Missing return after event.fail()**: Do action handlers `return` after calling `event.fail()`? Falling through executes the success path.
12. **next() without default**: Are `next()` calls on generators over relation data, config, or parsed output protected with a default value? Unprotected `next()` raises `StopIteration`.
13. **Non-string Pebble environment values**: Are Python `bool` or `int` values used directly in Pebble environment dicts? Pebble expects all values to be strings.
14. **exec() without wait()**: Are `container.exec()` return values discarded without calling `.wait()` or `.wait_output()`? The command runs asynchronously and may race with subsequent file operations.
15. **Status set by helper overwritten by caller**: Do helper methods set `BlockedStatus` or `WaitingStatus` and return, only for the calling `_update()` method to overwrite the status and continue processing?
16. **Wrong config key name**: Do `self.config.get()` or `self.config[]` calls use key names that don't match `config.yaml` / `charmcraft.yaml`? `.get()` silently returns None for nonexistent keys, bypassing validation.
17. **Inverted boolean condition**: Do boolean checks (`if flag is False:`, `if not flag:`) match their associated log messages and actions? Inverted conditions produce warnings when the safe path is taken and silence when the dangerous path is taken.
18. **String comparison of numeric relation data**: Are counter/sequence values from relation data compared with `>` / `<` without `int()` conversion? All relation data is strings, so `"9" > "10"` is True lexicographically.
19. **None in f-string URL construction**: Do f-strings like `f"{self.external_url}/path"` use properties that can return `None`? This produces `"None/path"` -- a valid-looking but broken URL.
20. **Action handler missing event.fail()**: Do action error paths only `logger.error()` without calling `event.fail()`? The action silently succeeds with empty results.
21. **os.path.join for URLs**: Is `os.path.join()` used to construct URLs? It works on Linux by coincidence but is semantically wrong and breaks if the second arg starts with `/`.
22. **lstrip/rstrip as removeprefix/removesuffix**: Are `lstrip()` or `rstrip()` called with multi-character strings to strip path prefixes or suffixes? `lstrip("s3://bucket/")` removes individual characters, not the prefix string.
23. **Missing initialisation guard in early-lifecycle handlers**: Do `leader_elected`, `relation_created`, or `relation_joined` handlers call workload methods without checking that the workload/cluster is fully initialised?
24. **Config-derived relation data not re-sent on config_changed**: Are relation data providers that set data from config values also called from `_on_config_changed`? Config changes may silently leave related apps with stale data.
25. **Exception messages leaking credentials**: Does `logger.exception()` or `exc_info=` log tracebacks from external tool calls that may contain credentials in command lines or connection strings?

## Step 5: Verify each finding

For each potential bug:
- Confirm the input is actually reachable (trace callers).
- Check if another code path already handles the case.
- Search for existing tests that cover the scenario.
- Check git blame to see if the code was recently changed.
- Look for comments or documentation explaining the design choice.

## Step 6: Report findings

### Severity classification

| Severity | Criteria | Examples |
|----------|----------|----------|
| **Critical** | Security issue or data corruption | Credential leak, world-readable credential files, TLS bypass, data loss |
| **High** | Runtime crash or silent wrong behavior | Unhandled exception crashing charm, missing leader guard causing split-brain, stale TLS flags |
| **Medium** | Edge case, config error, or operational issue | Truthiness check on rare zero value, unnecessary restarts, missing relation-broken handler |
| **Low** | Code quality or unlikely edge case | Missing f-string prefix in debug log, container name assumption, cosmetic status message |

### Output format

```markdown
## Bug Review: [Scope Description]

### Summary
- **Findings**: X (Y Critical, Z High, ...)
- **Code areas reviewed**: [list]
- **Charm name**: [name]

### Findings

#### [BUG-001] [Category] -- [Brief description] (Severity)
- **Location**: `file.py:123`
- **Pattern**: [Which known pattern this matches, or "novel"]
- **Issue**: [What the bug is]
- **Impact**: [What goes wrong at runtime]
- **Evidence**:
  ```python
  [Buggy code snippet]
  ```
- **Recommended fix**:
  ```python
  [Fixed code snippet]
  ```
- **Historical precedent**: [Similar bugs found in other charms, if applicable]

### Confirmed Safe
[Patterns that looked suspicious but were verified as correct]
```

### False-positive controls

Do NOT flag:
- Pebble operations inside `try/except (ConnectionError, ChangeError)`
- `if value` checks where the value genuinely cannot be 0, empty string, or False
- `event.relation.app` or `relation.app` without None guard -- modern ops guarantees non-None
- Status-setting code that is part of a `collect_unit_status` handler (reconciles all subsystems)
- Config values with explicit type declarations in `config.yaml` that match code usage
- `container.replan()` without preceding plan comparison -- Pebble only restarts services when the plan has actually changed; charm-side comparison is unnecessary
- Dashboard JSON from upstream projects that uses non-COS conventions intentionally
- `container.exec()` on the workload binary crashing the hook -- it is acceptable to expect the workload is running

### Known false-positive patterns

| Pattern | Why it's safe |
|---------|--------------|
| `if not self.unit.is_leader(): return` at handler start | Correct leader guard |
| `container.can_connect()` check before Pebble ops | Correct readiness guard |
| `self.model.get_relation(name)` returning None, checked | Correct None guard |
| `event.relation.data[self.app]` in leader-guarded block | Leader verified, app data access is safe |
| `try: container.restart(...) except ChangeError` | Handles Pebble restart failures |
| Config `.get()` with explicit default value | Default prevents None issues |
| `relation_broken` handler that only sets BlockedStatus | Minimal but correct cleanup |
| `container.exec()` called from action handler that checks `can_connect()` at entry | Guard is in the caller |
| `if self.config["string_field"]` truthiness check | Valid when field is type: string and empty means "not configured" |
| `except Exception` in best-effort existence checks (e.g., `is_created()`) | Intentional broad catch for resilience |
| `collect_unit_status` handler reconciling statuses from multiple subsystems | Centralized status is the correct pattern |
| Library method with internal leader guard called without caller guard | Guard is in the library |
| `datetime.utcnow()` paired with naive-UTC `not_valid_after` | Both are naive UTC, subtraction is consistent |
| `shell=True` with internally generated inputs (no user data flows in) | No injection risk when inputs are controlled |
| Passwords in `keytool`/`openssl` CLI args inside containers with `mask_sensitive_information()` in logging | Mitigated by short command lifetime and log masking |
| `exec()` without `wait()` for read-only / diagnostic commands (e.g., `cat`, `ls`) | No side effects to race with |
| `VaultClient(ca_cert_path=None)` in remove handlers | TLS certs may be unavailable during removal; intentional |
| Test helper code (in `tests/`) with type mismatches or missing guards | Test code has different reliability requirements |
| `event.relation.app` or `relation.app` accessed without None guard | Modern ops guarantees `.app` is always non-None, even during relation teardown |
| `container.replan()` without preceding plan comparison | Pebble internally compares plans and only restarts when something has changed |
| `container.exec(["workload-binary", ...])` without ExecError handling | Acceptable to let the hook crash if the workload is expected to be running |
| `@cached_property` on charm instance attributes | Ops creates a fresh charm instance per hook invocation, so the cache never persists across events |
| Short busy-wait loops waiting for external resources (e.g. ingress IP, K8s readiness) | Juju lacks built-in retry/backoff for non-event-driven waiting; loops under ~100s are acceptable |
