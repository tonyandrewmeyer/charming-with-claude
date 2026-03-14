# Bug Patterns in canonical/operator

A systematic analysis of **235 bug fixes** in the [canonical/operator](https://github.com/canonical/operator) repository, identifying the most common and significant patterns of bugs. This document is intended for developers and AI agents working in this repository, to help them avoid known pitfalls.

## Executive Summary

The most impactful bug patterns fall into these categories:

1. **Data mutability & sharing** — Dicts and lists passed around without copying, leading to unexpected mutation side effects
2. **Missing guards for None/missing data** — KeyError, AttributeError, TypeError from unhandled optional values
3. **Testing framework / production divergence** — The Harness and Scenario testing tools behaving differently from real Juju
4. **Juju API interaction errors** — Wrong tool arguments, naming convention mismatches, version assumption failures
5. **Security issues** — Information leaks in error messages, insecure file permissions, CI injection risks

The codebase has improved significantly over time: earlier bugs (2019-2022) tend to be more fundamental (missing features, wrong API usage), while later bugs (2023-2026) are more subtle (edge cases, test-production parity, type annotations).

---

## 1. Security Issues

**Priority: CRITICAL — always review carefully**

### 1.1 Information Leaks in Error Messages

The `ExecError.__str__` method exposed full command lines, including potentially sensitive arguments like credentials or secrets passed to Pebble exec commands.

**Example**: [`0ce8a0fd`](https://github.com/canonical/operator/commit/0ce8a0fd) — `ExecError.__str__` included the full command line. The fix changed it to only show the executable name, not arguments.

**How to avoid**: Never include full command arguments, environment variables, or request bodies in error messages or logs. Use `repr()` on just the command name, not the full argument list.

### 1.2 Insecure File Permissions

The SQLite storage file was created with default permissions (0o644, world-readable), exposing charm state data to other processes on the system.

**Example**: [`e4b0f9d4`](https://github.com/canonical/operator/commit/e4b0f9d4) — Changed SQLite storage file mode to 0o600.

**How to avoid**: Always set explicit restrictive permissions when creating files that contain state, credentials, or configuration. Use `os.open()` with explicit mode rather than relying on umask.

### 1.3 CI/Workflow Injection

CI workflows used git references in ways that could be exploited for injection attacks.

**Example**: [`85e677ef`](https://github.com/canonical/operator/commit/85e677ef) — Replaced git reference injection with wheel artifacts in charm test workflows.

**How to avoid**: In CI workflows, never use git refs or PR data directly in shell commands. Use environment variables or intermediate artifacts.

---

## 2. Crash-Causing Bugs

**Priority: HIGH — these cause charm failures at runtime**

### 2.1 Missing None/Optional Guards

Several crashes were caused by accessing attributes on values that could be `None` — particularly in code paths triggered by specific Juju versions or unusual charm configurations.

**Examples**:
- [`a93d676`](https://github.com/canonical/operator/commit/a93d676) — `self.app` could be `None` due to an upstream Juju bug, causing AttributeError during event dispatch
- [`6fcda007`](https://github.com/canonical/operator/commit/6fcda007) — `FileInfo.permissions` could be `None`, causing `TypeError` in `__repr__`
- [`31091898`](https://github.com/canonical/operator/commit/31091898) — `JUJU_VERSION` env var not set during `meter-status-changed` events, causing KeyError

**How to avoid**:
- Always handle the case where Juju-provided data may be missing or None
- Use `.get()` with defaults for environment variables and dict lookups
- Add None checks before attribute access on values from external sources

### 2.2 KeyError from Naming Convention Mismatches

Juju uses hyphens in identifiers (e.g., `auth-type`) while Python typically uses underscores. This mismatch has caused KeyErrors.

**Example**: [`d7473832`](https://github.com/canonical/operator/commit/d7473832) — `CloudCredential` construction failed with KeyError because the code looked for `auth-type` but the data used underscores (or vice versa).

**How to avoid**: When interacting with Juju API responses, be aware that field names may use hyphens. Always use `.get()` with a fallback, or normalize field names at the boundary.

### 2.3 Event Dispatch Issues

Wrong event ordering or incorrect remote unit injection can cause crashes when charms try to access data that isn't yet available.

**Example**: [`5a63e01e`](https://github.com/canonical/operator/commit/5a63e01e) — Remote units were added for all relation events, but should only be added for `departed` and `broken` events. The ordering was also wrong, causing inaccessible databags.

**How to avoid**: Carefully model the lifecycle of Juju events. Only make data available that would actually be present at that point in the lifecycle.

---

## 3. Data Mutability & Sharing Bugs

**Priority: HIGH — subtle and often missed in code review**

This is one of the most persistent bug patterns in the codebase. It occurs when dicts or lists are stored or returned by reference rather than by copy.

### Pattern

```python
# BUG: user's dict is stored directly — mutations to either side leak
class Context:
    def __init__(self, meta: dict):
        self._meta = meta  # Should be: dict(meta) or meta.copy()

# BUG: internal state returned without copy — caller can mutate internal state
def get_config(self):
    return self._config  # Should be: dict(self._config)
```

### Examples

- [`3f8fb9b9`](https://github.com/canonical/operator/commit/3f8fb9b9) — `testing.Context` held direct references to user-provided dicts for `meta`, `config`, and `actions`. Fix: copy on store.
- [`be09012`](https://github.com/canonical/operator/commit/be09012) — `_MockModelBackend.relation_get` returned the actual stored relation data dict. Callers could mutate it and corrupt the test state.
- [`4ffc1256`](https://github.com/canonical/operator/commit/4ffc1256) — Non-string keys could be used to write relation data because validation wasn't applied.
- [`668701b4`](https://github.com/canonical/operator/commit/668701b4) — Databag access validation was not enabled during `__init__`, allowing invalid operations.

### How to Avoid

- **Copy on store**: When accepting dicts from users/callers, always copy them: `self._data = dict(data)` or `copy.deepcopy(data)` for nested structures
- **Copy on return**: When returning internal state, return a copy: `return dict(self._config)`
- **Use frozen/immutable types**: Where possible, use `MappingProxyType`, frozen dataclasses, or `tuple` instead of `dict`/`list`
- **Model.config was made immutable** in [`6cd5d6c`](https://github.com/canonical/operator/commit/6cd5d6c) — this is the gold standard approach

---

## 4. Relation Data Handling Bugs

**Priority: HIGH — 25+ fixes in this area**

Relations are one of the most complex parts of the Juju model, and a major source of bugs.

### Common Issues

1. **Accessing relation data after relation-broken**: Data bags are not available after a relation is broken, but code often tries to access them.
   - [`1b086258`](https://github.com/canonical/operator/commit/1b086258) — Better error message for relation data access in relation-broken events

2. **Non-string keys/values in relation data**: Juju relation data is strictly `Dict[str, str]`, but Python code can accidentally write non-string types.
   - [`4ffc1256`](https://github.com/canonical/operator/commit/4ffc1256) — Fixed allowing non-string keys in relation data

3. **Shell argument length limits with large relation data**: Using command-line arguments for relation-set can exceed shell limits.
   - [`9fe65c7c`](https://github.com/canonical/operator/commit/9fe65c7c) — Switched to `--file` for relation-set to avoid shell argument length limits

4. **Incorrect relation ID handling**: Static method vs instance method confusion, wrong IDs in events.
   - [`49aaa0a0`](https://github.com/canonical/operator/commit/49aaa0a0) — Bug in `relation_ids` implementation

5. **Relation data change detection**: Issuing relation_changed events when there's no actual data delta.
   - [`16434141`](https://github.com/canonical/operator/commit/16434141) — Avoided issuing relation_changed events with no data delta

### How to Avoid

- Always validate that relation data keys and values are strings before writing
- Check if a relation still exists before accessing its data
- Use `--file` for large data transfers to Juju CLI tools
- In testing, ensure relation events include the correct relation ID and remote unit

---

## 5. Secrets Management Bugs

**Priority: HIGH — 13+ fixes in this area**

Secrets are a relatively new Juju feature, and their handling in ops has been a frequent source of bugs.

### Common Issues

1. **Secret ID canonicalization**: Juju uses `secret:<id>` format but code sometimes omits the prefix.
   - [`7670b59c`](https://github.com/canonical/operator/commit/7670b59c) — Made secret-get consistently use `secret:<id>` format

2. **Secret info visibility**: Secret info not being properly exposed to charms in testing.
   - [`0fa4497`](https://github.com/canonical/operator/commit/0fa4497) — Made secret info description visible in ops[testing]

3. **Caching issues**: Secrets were being cached in Ops, leading to stale data.
   - [`9323ead`](https://github.com/canonical/operator/commit/9323ead) — Don't cache secrets in Ops

4. **API argument conflicts**: `secret-info-get` cannot accept both ID and label simultaneously.
   - [`3ce1c7f`](https://github.com/canonical/operator/commit/3ce1c7f) — Prevent passing both ID and label to `secret-info-get`
   - [`5afc2842`](https://github.com/canonical/operator/commit/5afc2842) — Earlier fix for the same issue

5. **Owner normalization**: Secret owner field inconsistencies between ops and testing.
   - [`e7e2c8d`](https://github.com/canonical/operator/commit/e7e2c8d) — Normalise Secret.owner to 'app' for ops[testing]

### How to Avoid

- Always canonicalize secret IDs with the `secret:` prefix
- Never cache secret content — always fetch fresh from Juju
- Validate that API calls don't include conflicting arguments
- Test with both app-owned and unit-owned secrets

---

## 6. Pebble / Container Interaction Bugs

**Priority: MEDIUM — 16+ fixes**

### Common Issues

1. **Path handling**: Relative paths, empty directories, and path traversal issues in `push_path`/`pull_path`.
   - [`cbaec52e`](https://github.com/canonical/operator/commit/cbaec52e) — Fix issue with relative paths in Container.push_path
   - [`942bd23`](https://github.com/canonical/operator/commit/942bd23) — push_path and pull_path include empty directories

2. **Binary file handling**: `push()` not correctly handling binary files.
   - [`5943a59c`](https://github.com/canonical/operator/commit/5943a59c) — Fix Pebble push() handling of binary files

3. **Exec process stdout iteration**: The `for line in process.stdout` pattern didn't work correctly.
   - [`91b6551a`](https://github.com/canonical/operator/commit/91b6551a) — Fix "for line in process.stdout" behavior

4. **Temporary file cleanup**: `ops.Pebble.pull` not cleaning up temp files on error.
   - [`a1574f4`](https://github.com/canonical/operator/commit/a1574f4) — Ensure ops.Pebble.pull cleans up temporary files on error

5. **Layer merging**: Incorrect merge semantics for Pebble layers in testing.
   - [`3dda5b5f`](https://github.com/canonical/operator/commit/3dda5b5f) — Assorted fixes for Pebble layer merging in Harness and Scenario

6. **restart() operating on strings**: Container.restart() accidentally iterated over service name characters instead of treating it as a single service.
   - [`37fdcbaf`](https://github.com/canonical/operator/commit/37fdcbaf) — Fix Container.restart() accidentally operating on strings

### How to Avoid

- Always use `pathlib.Path` for path operations, and test with absolute, relative, and edge-case paths
- Handle both text and binary modes explicitly in file operations
- Use context managers for temporary files to ensure cleanup
- When accepting `str | list[str]` arguments, always normalize to list before iterating

---

## 7. Testing Framework / Production Divergence

**Priority: MEDIUM — 32+ fixes (test-framework + test-fix patterns)**

The Harness and Scenario testing frameworks must faithfully replicate Juju behavior. Divergences are a major bug source.

### Common Issues

1. **Event emission differences**: Testing frameworks emitting events in wrong order or with wrong data.
   - [`5a63e01e`](https://github.com/canonical/operator/commit/5a63e01e) — Wrong remote unit handling in relation events

2. **Secret behavior divergence**: Harness secrets not matching Juju behavior.
   - [`79706f40`](https://github.com/canonical/operator/commit/79706f40) — Adjust Harness secret behaviour to align with Juju

3. **Missing validation in tests**: Testing backends allowing operations that Juju would reject.
   - [`668701b4`](https://github.com/canonical/operator/commit/668701b4) — Turn on databag access validation in __init__

4. **Incorrect storage/config mocking**: Testing backends not correctly simulating Juju storage or config behavior.
   - [`deccdd6f`](https://github.com/canonical/operator/commit/deccdd6f) — Fix incorrect kwarg handling in testing backend storage_list

### How to Avoid

- When fixing a bug in ops, always check if the same fix needs to apply to Harness and Scenario
- Add integration tests that verify testing framework behavior matches real Juju
- Keep a mapping of Juju CLI tool behavior to testing backend behavior

---

## 8. Juju Version Compatibility

**Priority: MEDIUM — 13+ fixes**

### Common Issues

1. **Hardcoded version assumptions**: Code assuming a Juju feature is always available.
   - [`d6d1746b`](https://github.com/canonical/operator/commit/d6d1746b) — `credential-get` is available on k8s in newer Juju
   - [`5151a1e`](https://github.com/canonical/operator/commit/5151a1e) — Don't use `--app` for relation-get/-set before Juju 2.7.0

2. **Python version compatibility**: Using features not available in all supported Python versions.
   - [`8e94a4c9`](https://github.com/canonical/operator/commit/8e94a4c9) — Use parse_rfc3339 for datetime parsing to support Python 3.10
   - [`be1fdf06`](https://github.com/canonical/operator/commit/be1fdf06) — Fix model.py for Python 3.5.2 on Xenial

### How to Avoid

- Check `JujuVersion` before using version-dependent features
- Test on all supported Python versions
- Use `sys.version_info` checks for Python-version-specific code paths

---

## 9. Error Handling Gaps

**Priority: MEDIUM — 16+ fixes**

### Common Issues

1. **Wrong exception types**: Catching or raising the wrong exception class.
   - [`97501fd7`](https://github.com/canonical/operator/commit/97501fd7) — Catch the correct error when a relation doesn't exist
   - [`4fc4cfdb`](https://github.com/canonical/operator/commit/4fc4cfdb) — Use TypeError for invalid argument type errors

2. **Missing error handling for edge cases**: Not handling unusual but valid states.
   - [`c1661cae`](https://github.com/canonical/operator/commit/c1661cae) — Allow for missing fields in network-get response
   - [`c9bba5b0`](https://github.com/canonical/operator/commit/c9bba5b0) — Raise error in wait_output if stdout is already being consumed

3. **Poor error messages**: Error messages that don't help diagnose the problem.
   - [`8df3d2f1`](https://github.com/canonical/operator/commit/8df3d2f1) — Improved error message for invalid storage key
   - [`1b086258`](https://github.com/canonical/operator/commit/1b086258) — Better error for relation data access in relation-broken events

### How to Avoid

- Test error paths, not just happy paths
- Include relevant context in error messages (what was expected, what was found)
- Use specific exception types, not generic Exception or bare except

---

## 10. Type Annotation Errors

**Priority: LOW — 10+ fixes**

### Common Issues

1. **Wrong return type annotations**: Functions annotated with incorrect types.
   - [`3df8ae9`](https://github.com/canonical/operator/commit/3df8ae9) — Correct the `Model.get_binding()` return type
   - [`fad95d7d`](https://github.com/canonical/operator/commit/fad95d7d) — Fix type of StatusBase.name

2. **Assignment vs annotation syntax**: Using `=` instead of `:` for type annotations.
   - [`aa06bf54`](https://github.com/canonical/operator/commit/aa06bf54) — StorageMeta.properties had `= list[str]` instead of `: list[str]`

3. **Import compatibility with type checkers**: Type checkers like mypy not understanding conditional imports.
   - [`d6325d05`](https://github.com/canonical/operator/commit/d6325d05) — Move testing.Container import for mypy compatibility

### How to Avoid

- Run mypy and pyright in CI on all source files
- Review type annotations carefully — a typo can silently break type checking

---

## 11. Import and Module Issues

**Priority: LOW — 6+ fixes**

Circular imports, wrong import paths, and missing `__all__` entries.

- [`14f3baf5`](https://github.com/canonical/operator/commit/14f3baf5) — Cyclic imports fixed
- [`9dbb6b66`](https://github.com/canonical/operator/commit/9dbb6b66) — Type error in `__init__.__all__`
- [`ac7b9f09`](https://github.com/canonical/operator/commit/ac7b9f09) — Fixed issue with pebble imports

---

## 12. Configuration Handling Bugs

**Priority: MEDIUM — 7+ fixes**

- [`1c0ff40d`](https://github.com/canonical/operator/commit/1c0ff40d) — Fix falsy config defaults (empty string, 0, False treated as missing)
- [`6cd5d6c`](https://github.com/canonical/operator/commit/6cd5d6c) — Make model.config immutable to prevent accidental mutation

---

## 13. Event Framework / Stored State Bugs

**Priority: MEDIUM**

- [`d0f9f501`](https://github.com/canonical/operator/commit/d0f9f501) — Event snapshot not available when one observer defers and another doesn't
- [`d14c3033`](https://github.com/canonical/operator/commit/d14c3033) — Transaction integrity lost on first run
- [`f36e90b9`](https://github.com/canonical/operator/commit/f36e90b9) — Event count not persisted, causing reused event handles

---

## Summary Table

| Pattern | Count | Severity | Key Risk |
|---------|-------|----------|----------|
| Relation data handling | 25+ | High | Data corruption, crashes |
| Testing/production divergence | 32+ | Medium | False test passes |
| Pebble/container bugs | 16+ | Medium | Container interaction failures |
| Error handling gaps | 16+ | Medium | Poor diagnostics, crashes |
| Secrets management | 13+ | High | Stale data, API errors |
| Juju version compat | 13+ | Medium | Crashes on specific versions |
| CI/build issues | 12+ | Low | Build failures |
| Configuration handling | 7+ | Medium | Wrong config values |
| Import/module issues | 6+ | Low | Import errors |
| Type annotations | 10+ | Low | Type checker failures |
| Data mutability | 6+ | High | Silent data corruption |
| Security | 3 | Critical | Info leaks, permissions |
| Crash on None/missing | 5+ | High | Runtime crashes |

---

## Key Takeaways for Developers

1. **Always copy dicts/lists** at API boundaries — both when accepting and returning
2. **Use `.get()` with defaults** when reading Juju environment variables or API responses
3. **Check Juju version** before using version-specific features
4. **Test error paths** — most high-severity bugs were in untested edge cases
5. **Keep testing frameworks in sync** — every ops fix should be reflected in Harness/Scenario
6. **Never expose full commands or credentials** in error messages or logs
7. **Set explicit file permissions** for any files containing state or credentials
8. **Normalize naming conventions** (hyphens vs underscores) at boundaries with Juju
9. **Don't cache secrets** — always fetch fresh from Juju
10. **Handle None everywhere** Juju might provide it — especially in newer/older version edge cases
