# Bug Fix Commit Index — canonical/operator

Total bug fix commits analyzed: **235**

This index covers all bug fixes identified in the canonical/operator repository,
from the initial commit to the latest on main. Fixes include source code, test,
documentation, CI, and build fixes.

## Summary Statistics

### By Severity

| Severity | Count |
|----------|-------|
| high | 15 |
| medium | 184 |
| low | 36 |

### By Fix Category

| Category | Count |
|----------|-------|
| test-fix | 165 |
| source-fix | 104 |
| docs-fix | 36 |
| build-fix | 35 |
| ci-fix | 17 |

### By Area

| Area | Count |
|------|-------|
| tests | 158 |
| scenario | 82 |
| testing-framework | 60 |
| model | 43 |
| relations | 36 |
| pebble | 35 |
| docs | 33 |
| packaging/build | 32 |
| secrets | 21 |
| ci | 18 |
| framework | 16 |
| storage | 13 |
| charm | 12 |
| main/dispatch | 11 |
| config | 8 |
| actions | 7 |
| networking | 6 |
| type-annotations | 4 |
| status | 4 |
| general | 3 |

### By Year

| Year | Count |
|------|-------|
| 2019 | 6 |
| 2020 | 15 |
| 2021 | 13 |
| 2022 | 20 |
| 2023 | 87 |
| 2024 | 41 |
| 2025 | 40 |
| 2026 | 13 |

### By Bug Type

| Bug Type | Count |
|----------|-------|
| logic-error | 132 |
| juju-api-interaction | 46 |
| event-dispatch | 19 |
| import-issue | 14 |
| compatibility | 13 |
| resource-management | 12 |
| type-annotation | 10 |
| missing-handling | 10 |
| security | 10 |
| parsing | 9 |
| exception-handling | 8 |
| mutability | 6 |
| incorrect-result | 6 |
| caching | 6 |
| concurrency | 5 |
| crash | 5 |

## High Severity Fixes

These are the most critical bug fixes — security issues, crashes, and data integrity problems.

### [0ce8a0fd](https://github.com/canonical/operator/commit/0ce8a0fdbe89ce4d55b7f23fd245366d4d83698f) — fix: only show executable in ExecError.__str__, not full command line (#2336)

- **Date**: 2026-02-23
- **Areas**: docs, pebble, tests
- **Categories**: docs-fix, source-fix, test-fix
- **Pattern**: Information Leak in Error Messages
- **Security Relevant**: Yes
- **Could Cause Crash**: No

**Root Cause**: The ExecError.__str__ method was formatting the entire command list (self.command) into the exception message string. When commands included sensitive data such as credentials or tokens passed as command-line arguments, this information would be exposed in exception messages, log files, and potentially error reporting systems. The code used `self.command!r` which would repr the full list of command arguments, including any secrets embedded in them.

**Fix**: The fix changes ExecError.__str__ to only include the executable name (self.command[0]) rather than the full command list. This mirrors the existing approach used in tracing, where only the executable name is sent for pebble exec operations. The change is a single-line modification from `self.command!r` to `self.command[0]!r`, and accompanying test updates verify that multi-argument commands only show the first element. Documentation was also updated to reflect the new output format.

**Lesson**: Error messages and log output should never include full command lines, as they may contain embedded credentials or sensitive arguments.

[View detailed summary](2026-02-23_0ce8a0fd.md)

---

### [d6d1746b](https://github.com/canonical/operator/commit/d6d1746b812f1a64d91248cff95cf2d53b43fa58) — fix: credential-get is available on k8s in newer Juju (#2307)

- **Date**: 2026-02-09
- **Areas**: scenario, testing-framework, tests
- **Categories**: test-fix
- **Pattern**: Hardcoded Version Assumption
- **Security Relevant**: No
- **Could Cause Crash**: No

**Root Cause**: The Scenario consistency checker had a hard-coded assumption that the Juju credential-get hook command was never available for Kubernetes models. However, starting with Juju 3.6.10, credential-get became available on K8s models. This caused the consistency checker to incorrectly report an error when charms running on K8s with Juju >= 3.6.10 attempted to use CloudSpec, blocking valid test scenarios.

**Fix**: The fix updates the check_cloudspec_consistency function to accept a juju_version parameter and only flag CloudSpec on Kubernetes as an error when the Juju version is less than 3.6.10. The error message was also updated to suggest either upgrading the juju_version or simulating a machine substrate. A new test case was added to verify that CloudSpec on k8s is consistent with Juju >= 3.6.10.

**Lesson**: Feature availability checks should be version-aware rather than using blanket restrictions that may become stale as the underlying platform evolves.

[View detailed summary](2026-02-09_d6d1746b.md)

---

### [85e677ef](https://github.com/canonical/operator/commit/85e677ef38856f54978a70a6341b2b544aa2547e) — fix: replace git reference injection with wheel artifacts in charm test workflows (#2252)

- **Date**: 2026-01-23
- **Areas**: ci
- **Categories**: ci-fix, test-fix
- **Pattern**: CI Race Condition / Injection Risk
- **Security Relevant**: Yes
- **Could Cause Crash**: No

**Root Cause**: The CI charm test workflows injected git references (e.g., git+$GITHUB_SERVER_URL/$GITHUB_REPOSITORY@$GITHUB_SHA#egg=ops) into dependency files to test the branch's version of ops. This approach suffered from race conditions where the appropriate revision of the branch was not yet available from the CI runner when the dependency resolution step ran, causing intermittent CI failures. The git references also created a potential injection vector in the workflow configuration.

**Fix**: The fix introduces a reusable workflow (_build-wheels.yaml) that pre-builds local wheel artifacts (ops, ops-scenario, ops-tracing) from the branch. All four charm test workflows (db-charm-tests, hello-charm-tests, observability-charm-tests, published-charms-tests) were updated to depend on the build-wheels job, download the wheel artifacts, and use them directly in place of git references. This eliminates the race condition by ensuring the exact code from the branch is packaged and available before any test job starts.

**Lesson**: CI workflows should use pre-built, immutable artifacts rather than live git references to avoid race conditions and reduce the attack surface of dependency resolution.

[View detailed summary](2026-01-23_85e677ef.md)

---

### [d7473832](https://github.com/canonical/operator/commit/d7473832343c46f4f5c534162d4f1505161529a4) — fix: prevent `KeyError` on `auth-type` when creating `CloudCredential` object (#2268)

- **Date**: 2026-01-14
- **Areas**: model, tests
- **Categories**: source-fix, test-fix
- **Pattern**: Naming Convention Mismatch
- **Security Relevant**: No
- **Could Cause Crash**: Yes

**Root Cause**: When model.get_cloud_spec() called the credential-get hook command, it used dataclasses.asdict() to convert the hookcmds.CloudSpec dataclass into a dictionary, and then passed that dictionary to CloudSpec.from_dict(). However, the hookcmds dataclasses used Python-style attribute names with underscores (e.g., auth_type, identity_endpoint), while the from_dict() methods expected Juju-style hyphenated keys (e.g., auth-type, identity-endpoint). The dataclasses.asdict() call preserved the underscore naming, causing KeyError when from_dict() looked up keys like 'auth-type'.

**Fix**: The fix removes the use of dataclasses.asdict() entirely and instead adds private _from_hookcmds() class methods to both CloudCredential and CloudSpec. These methods directly read from the hookcmds dataclass attributes (which use underscores) and construct the model objects without any dictionary intermediary. The relation_model_get method was also changed to explicitly build a dict rather than using asdict(). Tests were added that create hookcmds objects directly and verify round-trip conversion.

**Lesson**: When converting between data representations with different naming conventions (e.g., Python underscores vs. JSON/YAML hyphens), avoid generic serialization like dataclasses.asdict() and use explicit conversion methods that handle the mapping.

[View detailed summary](2026-01-14_d7473832.md)

---

### [04224917](https://github.com/canonical/operator/commit/0422491787a573de4b2ac527c5b85a32521f2bef) — fix: detect categories with an explanation mark indicating breaking changes (#2132)

- **Date**: 2025-10-22
- **Areas**: general
- **Categories**: source-fix
- **Pattern**: Incomplete Regex Parsing
- **Security Relevant**: No
- **Could Cause Crash**: No

**Root Cause**: The release script's regular expression for parsing changelog entries from GitHub release notes did not account for the conventional commit '!' breaking change indicator (e.g., 'feat!: some change'). The regex pattern `r'^\* (\w+): (.*) by [^ ]+ in (.*)'` would fail to match lines containing the '!' character after the category, causing breaking changes to be silently dropped from both the changelog and release notes. Additionally, the version parsing did not support pre-release suffixes (alpha, beta, rc).

**Fix**: The fix updates the regex to use named groups and adds an optional `(?P<breaking>!?)` capture group after the category. Breaking changes are now collected into a separate 'breaking' category and rendered with their own 'Breaking Changes' section in both the release notes and changelog. The script also logs a warning when breaking changes are detected. Version parsing was extended to support pre-release suffixes via the pattern `(?:(?:a|b|rc)\d+)?`.

**Lesson**: Release tooling should be tested against all conventional commit formats including breaking change indicators, as silently dropping important entries undermines the value of changelogs.

[View detailed summary](2025-10-22_04224917.md)

---

### [6aaacfdf](https://github.com/canonical/operator/commit/6aaacfdf7322ccc258c6fcdf19d74a3b3e25ade4) — fix: raise ActionFailed when using Context as a context manager (#2121)

- **Date**: 2025-10-21
- **Areas**: actions, scenario, testing-framework, tests
- **Categories**: test-fix
- **Pattern**: Inconsistent Code Paths
- **Security Relevant**: No
- **Could Cause Crash**: No

**Root Cause**: The Scenario testing framework's Context class had two ways to run events: Context.run() and using Context as a context manager via Manager.run(). Both paths used the internal Context._run() method, but the code that handled ActionFailed (resetting action logs, checking failure status, and raising the exception) was only implemented in Context.run(). When using the context manager path, a failed action would silently succeed, returning a State without raising ActionFailed, which violated the expected behavior and could hide test failures.

**Fix**: The fix moves the action failure handling code (clearing logs/results, resetting failure message, and raising ActionFailed) from Context.run() into the shared Context._run() context manager method. This ensures that both Context.run() and the context manager path execute the same action failure logic. The action state reset is done before yielding, and the ActionFailed check is done after the yield, ensuring it fires in both usage patterns. Tests were added for both the direct run and context manager paths.

**Lesson**: When providing multiple API entry points that should behave identically, the shared logic must be in a common method rather than duplicated in only one path.

[View detailed summary](2025-10-21_6aaacfdf.md)

---

### [5a63e01e](https://github.com/canonical/operator/commit/5a63e01e2b2eec9e23f226f08f9c47c6ddeb3e0a) — fix: only add the remote unit for departed and broken relation events, fix ordering (#1918)

- **Date**: 2025-07-28
- **Areas**: main/dispatch, model, relations, tests
- **Categories**: source-fix, test-fix
- **Pattern**: Overly Broad Event Handling
- **Security Relevant**: No
- **Could Cause Crash**: Yes

**Root Cause**: When adding support for accessing the departing unit's databag during relation-departed events (PR #1364), the remote unit injection from JUJU_REMOTE_UNIT was applied unconditionally to all relation events for simplicity. However, this was incorrect: in relation-joined events, the remote unit should not yet be in the relation's units set because the relation has not been fully established. Furthermore, the remote unit was being inserted into the relation *after* RelationData was initialized, which meant the inserted unit's databag was not accessible because it wasn't present when the data mapping was created.

**Fix**: The fix restricts the remote unit injection to only relation-departed and relation-broken events by checking the dispatcher's event_name suffix. For all other relation events, remote_unit_name is set to None, relying on the normal relation-list mechanism. Additionally, the ordering in the Relation constructor was fixed: the unit insertion now happens before RelationData initialization, so that the inserted unit's databag is properly included. Tests verify both the correct injection in departed events and the absence of injection in joined events.

**Lesson**: When injecting state for specific event types, always gate the injection on the actual event type rather than applying it broadly for simplicity, as other events may have different invariants.

[View detailed summary](2025-07-28_5a63e01e.md)

---

### [a93d6763](https://github.com/canonical/operator/commit/a93d676363efb269d7459a27a17fd35804fb47e5) — fix: if self.app is not actually set avoid a new crash location (#1897)

- **Date**: 2025-07-08
- **Areas**: model
- **Categories**: source-fix
[View detailed summary](2025-07-08_a93d6763.md)

---

### [31091898](https://github.com/canonical/operator/commit/31091898e169032f7165afe77157be982da521ea) — fix: in meter-status-changed JUJU_VERSION is not set (#1840)

- **Date**: 2025-06-24
- **Areas**: juju-context, main/dispatch, status, tests
- **Categories**: source-fix, test-fix
- **Pattern**: Missing Environment Variable Fallback
- **Security Relevant**: No
- **Could Cause Crash**: Yes

**Root Cause**: The JUJU_VERSION environment variable is documented as being set for all hooks, but Juju does not actually set it for meter-status-changed and collect-metrics events. After PR #1313 removed the fallback behavior that handled missing JUJU_VERSION, the JujuContext.from_dict() method began crashing with a KeyError when dispatched for meter-status-changed. Additionally, the collect-status evaluation (which calls is-leader) would also crash in the restricted context of these events where is-leader is not available.

**Fix**: The fix restores the fallback behavior by using env.get('JUJU_VERSION', '0.0.0') instead of env['JUJU_VERSION']. It adds meter-status-changed to the list of restricted context events alongside collect-metrics, which prevents deferred event re-emission and Juju storage usage during these events. The collect-status evaluation is also skipped in restricted contexts since the is-leader hook tool is unavailable. Tests were expanded to parameterize the restricted event handling for both collect-metrics and meter-status-changed.

**Lesson**: Never trust that environment variables documented as 'always set' actually are -- always provide sensible defaults, especially when the behavior varies across event types or platform versions.

[View detailed summary](2025-06-24_31091898.md)

---

### [668701b4](https://github.com/canonical/operator/commit/668701b4396098b3e7a93288cd272c11dd2a8af6) — fix: turn on databag access validation in __init__ (#1737)

- **Date**: 2025-05-28
- **Areas**: main/dispatch, relations, testing-framework, tests
- **Categories**: source-fix, test-fix
- **Pattern**: Validation Gap in Initialization
- **Security Relevant**: No
- **Could Cause Crash**: No

**Root Cause**: Relation data access validation (which checks whether a unit has permission to read or write a specific databag) was only active during event observer execution, not during charm __init__. The validation is gated on having a non-falsey event context name, but no event context was set during charm initialization. This meant that during __init__, accessing a databag without proper permissions would either silently succeed (in test frameworks) or fail with a generic ModelError from Juju hook tools (at runtime) rather than raising the more specific and pre-emptive RelationDataAccessError.

**Fix**: The fix wraps the charm class instantiation in both _Manager (runtime) and Harness with `framework._event_context('__init__')`, setting a dummy event name that enables the validation logic. This ensures that RelationDataAccessError is raised consistently during __init__ just as it is during event observers. Comprehensive tests were added for both Harness and Scenario covering leader and non-leader access to local and remote app databags in both __init__ and event handler contexts.

**Lesson**: Access control validation should be active during all phases of object lifecycle including initialization, not just during specific event handling phases.

[View detailed summary](2025-05-28_668701b4.md)

---

### [3dda5b5f](https://github.com/canonical/operator/commit/3dda5b5f64bdea21d43a42431edcca62669c3173) — fix: assorted fixes for Pebble layer merging in Harness and Scenario (#1627)

- **Date**: 2025-03-14
- **Areas**: pebble, scenario, testing-framework, tests
- **Categories**: source-fix, test-fix
- **Pattern**: Incorrect Merge Semantics
- **Security Relevant**: No
- **Could Cause Crash**: No

**Root Cause**: Multiple interrelated bugs existed in how Harness and Scenario handled Pebble layer merging. (1) When merging Check objects, an unset startup value would incorrectly override a previously set startup. (2) Services, checks, and log targets were being sorted by name before merging, but Pebble only sorts by filename for initial layers -- API-added layers should preserve insertion order. (3) When same-named items appeared across differently named layers with override='merge', they were replaced instead of merged (merging only worked within same-named layers in add_layer). (4) Scenario's Container.plan property ignored checks and log targets entirely. (5) CheckInfo objects were not updated when the plan changed via add_layer.

**Fix**: The fix addresses all five issues: (1) Check._merge now skips CheckStartup.UNSET to avoid overriding a set value. (2) The _render_services/checks/log_targets methods now iterate self._layers.values() in insertion order instead of sorted(self._layers.keys()). (3) The render methods now check for override='merge' and call the _merge method instead of replacing. (4) Scenario's Container.plan property now includes checks and log targets via new _render_checks and _render_log_targets methods. (5) A new _update_check_infos_from_plan method syncs CheckInfo metadata after plan changes. A __repr__ was also added to pebble.Plan for debugging.

**Lesson**: Test framework simulations of complex stateful systems like Pebble must faithfully replicate the merge, ordering, and override semantics of the real system, as subtle differences lead to tests that pass but production that fails.

[View detailed summary](2025-03-14_3dda5b5f.md)

---

### [d14c3033](https://github.com/canonical/operator/commit/d14c30331bc4fdde0d5a880475ace04fe6b5d455) — fix: maintain transaction integrity on first run (#1558)

- **Date**: 2025-02-03
- **Areas**: actions, storage
- **Categories**: source-fix
- **Pattern**: Premature Transaction Commit
- **Security Relevant**: No
- **Could Cause Crash**: No

**Root Cause**: When the SQLite storage database was first created, the _setup() method ran DDL (CREATE TABLE IF NOT EXISTS) and then called self._db.commit(). Because the connection uses isolation_level=None (autocommit mode management), this early commit ended the implicit transaction started by the DDL statements. All subsequent operations within the same dispatch then ran in autocommit mode rather than within a transaction, breaking the transactional guarantees that the rest of the code relied upon. This meant that partial state could be written to disk if a hook failed partway through, corrupting the unit state.

**Fix**: The fix removes the single self._db.commit() call after the DDL statements in _setup(). Since SQLite safely allows DDL within transactions, the table creation becomes part of the overall transaction that is committed later by the on_commit() handler. This preserves transactional integrity from the very first run, ensuring that either all state changes are committed atomically or none are.

**Lesson**: In transaction-based storage systems, DDL statements should not be committed separately from the data they enable, as this can break the transactional guarantees that subsequent code depends upon.

[View detailed summary](2025-02-03_d14c3033.md)

---

### [79706f40](https://github.com/canonical/operator/commit/79706f401d93a4e85b729de52a81367f6d3f6451) — fix: adjust Harness secret behaviour to align with Juju (#1248)

- **Date**: 2024-06-25
- **Areas**: charm, framework, model, secrets, testing-framework, tests
- **Categories**: source-fix, test-fix
- **Pattern**: Test Double Behavior Mismatch
- **Security Relevant**: No
- **Could Cause Crash**: No

**Root Cause**: The Harness testing backend's secret handling did not match Juju's actual error behavior. The _ensure_secret_owner method unconditionally raised SecretNotFoundError for all permission failures, but real Juju returns different errors depending on the operation: 'not found' messages for info/grant operations (which should raise SecretNotFoundError), and other error messages for set/revoke/remove operations (which should raise ModelError or RuntimeError). Additionally, set_content() was invalidating the local content cache, forcing an unnecessary re-fetch, even though the tracked content doesn't change until refresh() is called.

**Fix**: The fix refactors _ensure_secret_owner into _has_secret_owner_permission returning a boolean. Each calling method now raises the appropriate exception type: SecretNotFoundError for secret_info_get and secret_grant (matching Juju's 'not found' response), and RuntimeError for secret_set, secret_revoke, and secret_remove (matching Juju's behavior where these succeed at call time but fail at hook completion). The content cache invalidation in set_content was removed. Documentation across charm.py and model.py was extensively updated to clarify caching behavior and which exceptions are raised.

**Lesson**: Test doubles must faithfully reproduce the error types and error conditions of the real system, as charms that catch specific exception types will behave differently if the test framework raises wrong ones.

[View detailed summary](2024-06-25_79706f40.md)

---

### [e4b0f9d4](https://github.com/canonical/operator/commit/e4b0f9d4e232d384745a9823bcf0e481b222a006) — fix: reduce mode of SQLite storage file to 0o600 (#1057)

- **Date**: 2023-11-16
- **Areas**: security, storage, tests
- **Categories**: source-fix, test-fix
- **Pattern**: Insecure File Permissions
- **Security Relevant**: Yes
- **Could Cause Crash**: No

**Root Cause**: The SQLite storage file (.unit-state.db) was created by sqlite3.connect() with the default file permissions (typically 0o644 on Linux), which makes it world-readable. This file stores the charm's unit state including potentially sensitive data like stored state, deferred events, and relation data. Any user or process on the machine could read this file, creating a local information disclosure vulnerability.

**Fix**: The fix adds a _ensure_db_permissions method that enforces 0o600 (owner read/write only) permissions on the SQLite database file. For new files, it uses os.open with O_CREAT|O_EXCL and explicit mode=0o600 to atomically create the file with restricted permissions before sqlite3.connect opens it. For existing files, it calls os.chmod to restrict permissions. The method also handles race conditions (file created between exists check and open) and permission change failures by raising RuntimeError. An in-memory database (":memory:") skips the permission check.

**Lesson**: Files containing application state or secrets must be created with restrictive permissions (0o600) from the start, not relying on the default umask which typically allows world-read access.

[View detailed summary](2023-11-16_e4b0f9d4.md)

---

### [6fcda007](https://github.com/canonical/operator/commit/6fcda007bff2671fa97924fbf70f480753f862d6) — Avoid error in FileInfo repr due to permissions being None (#956)

- **Date**: 2023-06-16
- **Areas**: security, testing-framework, tests
- **Categories**: test-fix
- **Pattern**: Unhandled None in Format String
- **Security Relevant**: No
- **Could Cause Crash**: Yes

**Root Cause**: The FileInfo.__repr__ method used an octal format string (`:o`) to display the permissions field, but the permissions value could be None when retrieved via dict.get('permissions'). The `:o` format specifier does not support NoneType, causing a TypeError: 'unsupported format string passed to NoneType.__format__'. The static type checker (Pyright) did not catch this because the _FileKwargs TypedDict defined 'permissions' as a non-optional int field, hiding the fact that dict.get() could return None.

**Fix**: The fix makes two changes: (1) The _FileKwargs TypedDict definition is corrected to declare 'permissions' as Optional[int], accurately reflecting that the value can be None. (2) The code that retrieves permissions uses `file.kwargs.get('permissions') or 0` to provide a fallback value of 0 when permissions is None, preventing the TypeError in __repr__. This ensures FileInfo objects can always be safely repr'd regardless of whether permissions data was provided.

**Lesson**: TypedDict definitions must accurately reflect optional fields so that static type checkers can catch format string incompatibilities with None values.

[View detailed summary](2023-06-16_6fcda007.md)

---

## All Bug Fix Commits

| Date | Commit | Severity | Categories | Subject | Areas |
|------|--------|----------|------------|---------|-------|
| 2026-03-11 | [3f8fb9b9](https://github.com/canonical/operator/commit/3f8fb9b91ec28f2330df663c8f068de46260e75a) | medium | test-fix | fix: hold only copies of user provided dicts in testing.Context (#2349 | scenario, testing-framework, tests |
| 2026-03-03 | [d6325d05](https://github.com/canonical/operator/commit/d6325d054f438294f94e8c442e693e08a5b62c34) | low | test-fix | fix: Move the testing.Container compatibility import so that mypy styl | pebble, testing-framework, tests |
| 2026-02-26 | [aa06bf54](https://github.com/canonical/operator/commit/aa06bf54b286c435d7d889146ba209a0920620dd) | medium | source-fix | fix: correct type annotation for StorageMeta.properties (#2348) | charm, storage, type-annotations |
| 2026-02-25 | [38eab2ba](https://github.com/canonical/operator/commit/38eab2ba06670ae925e209d73509e9be98ac0cce) | medium | source-fix, test-fix | fix: support Pydantic MISSING sentinel in ops.Relation.save (#2306) | model, relations, tests |
| 2026-02-23 | [0ce8a0fd](https://github.com/canonical/operator/commit/0ce8a0fdbe89ce4d55b7f23fd245366d4d83698f) | high | docs-fix, source-fix, test-fix | fix: only show executable in ExecError.__str__, not full command line  | docs, pebble, tests |
| 2026-02-17 | [3df8ae9c](https://github.com/canonical/operator/commit/3df8ae9c665256d36f60e835ece4b4ac4ae22cef) | medium | source-fix | fix: correct the `Model.get_binding()` return type (#2329) | model, networking |
| 2026-02-09 | [d6d1746b](https://github.com/canonical/operator/commit/d6d1746b812f1a64d91248cff95cf2d53b43fa58) | high | test-fix | fix: credential-get is available on k8s in newer Juju (#2307) | scenario, testing-framework, tests |
| 2026-01-29 | [3d59df81](https://github.com/canonical/operator/commit/3d59df81a6344648708a35ca8c731d84b47180d1) | medium | test-fix | fix: make testing.CheckInfo level arg type match pebble.CheckInfo.leve | pebble, scenario, testing-framework, tes |
| 2026-01-23 | [85e677ef](https://github.com/canonical/operator/commit/85e677ef38856f54978a70a6341b2b544aa2547e) | high | ci-fix, test-fix | fix: replace git reference injection with wheel artifacts in charm tes | ci |
| 2026-01-15 | [379d0132](https://github.com/canonical/operator/commit/379d01322b02119a6110094495ea3bacca39b0f5) | medium | source-fix, test-fix | fix: _checks_action should return empty list when there are no changes | actions, pebble, tests |
| 2026-01-14 | [d7473832](https://github.com/canonical/operator/commit/d7473832343c46f4f5c534162d4f1505161529a4) | high | source-fix, test-fix | fix: prevent `KeyError` on `auth-type` when creating `CloudCredential` | model, tests |
| 2026-01-13 | [337ce1db](https://github.com/canonical/operator/commit/337ce1db9fff89b9f143390a4924e9c1a7189424) | medium | source-fix, test-fix | fix: correct the value of `additional_properties` in the action meta i | actions, charm, tests |
| 2026-01-12 | [8e94a4c9](https://github.com/canonical/operator/commit/8e94a4c92b9e2097e223a3368764e43e8562f2e4) | low | source-fix, test-fix | fix: use parse_rfc3339 for datetime parsing to support Python 3.10 (#2 | secrets, tests |
| 2025-11-17 | [4529b3ff](https://github.com/canonical/operator/commit/4529b3ffea58e8b5a966bd863aaa119eb806becb) | medium | source-fix, test-fix | fix: minor hookcmds fixes (#2175) | actions, relations, tests |
| 2025-11-17 | [3ce1c7f3](https://github.com/canonical/operator/commit/3ce1c7f3ec52b5d6fa1648e585ee5fd466f35360) | medium | source-fix, test-fix | fix: secret-info-get cannot be provided with both an ID and a label (# | model, secrets, tests |
| 2025-10-27 | [9323eadc](https://github.com/canonical/operator/commit/9323eadc17b76a1e34a5625fb8e19a839fd0a5c1) | medium | source-fix, test-fix | fix: don't cache secrets in Ops (#2143) | charm, model, secrets, tests |
| 2025-10-23 | [e7e2c8d7](https://github.com/canonical/operator/commit/e7e2c8d7cbba9f48f3a62ca59adaa1f47b4058bc) | medium | test-fix | fix: normalise Secret.owner to 'app' for ops[testing] output state (#2 | scenario, secrets, testing-framework, te |
| 2025-10-22 | [04224917](https://github.com/canonical/operator/commit/0422491787a573de4b2ac527c5b85a32521f2bef) | high | source-fix | fix: detect categories with an explanation mark indicating breaking ch | general |
| 2025-10-21 | [6aaacfdf](https://github.com/canonical/operator/commit/6aaacfdf7322ccc258c6fcdf19d74a3b3e25ade4) | high | test-fix | fix: raise ActionFailed when using Context as a context manager (#2121 | actions, scenario, testing-framework, te |
| 2025-10-20 | [3ac3706b](https://github.com/canonical/operator/commit/3ac3706b0dda0c0139e9d565c376bde8cb5c4b54) | medium | test-fix | fix!: ensure that the testing context manager is exited when an except | scenario, testing-framework, tests |
| 2025-10-17 | [0fa4497c](https://github.com/canonical/operator/commit/0fa4497c8689d514c4cc79df2d8fa32fe67a2d46) | medium | test-fix | fix: make secret info description visible to the charm in ops[testing] | scenario, secrets, testing-framework, te |
| 2025-10-16 | [f646fc87](https://github.com/canonical/operator/commit/f646fc870fe03335f946d0138abe9114ccfa482a) | medium | source-fix, test-fix | fix!: change JujuContext.machine_id from int to str (#2108) | juju-context, scenario, testing-framewor |
| 2025-10-10 | [a1574f43](https://github.com/canonical/operator/commit/a1574f4339f75cf196835a55e17a1eec4d103cdf) | medium | source-fix, test-fix | fix: ensure `ops.Pebble.pull` cleans up temporary files if it errors ( | pebble, tests |
| 2025-10-08 | [733cd511](https://github.com/canonical/operator/commit/733cd511f53a78e58121b4d27b3de8ce29a49fd4) | medium | test-fix | fix: allow actions without params or descriptions in ops[testing] (#20 | actions, scenario, testing-framework, te |
| 2025-09-26 | [be090122](https://github.com/canonical/operator/commit/be0901227c1ba534f5948c1047377dd4c8638c87) | medium | test-fix | fix: `_MockModelBackend.relation_get` will return a copy of the relati | relations, scenario, testing-framework,  |
| 2025-07-29 | [5a999fa4](https://github.com/canonical/operator/commit/5a999fa49e34afec21c1bf2906343473f15702a5) | medium | source-fix, test-fix | fix: add the remote unit to Relation.data but not Relation.units (#192 | model, relations, tests |
| 2025-07-28 | [5a63e01e](https://github.com/canonical/operator/commit/5a63e01e2b2eec9e23f226f08f9c47c6ddeb3e0a) | high | source-fix, test-fix | fix: only add the remote unit for departed and broken relation events, | main/dispatch, model, relations, tests |
| 2025-07-08 | [a93d6763](https://github.com/canonical/operator/commit/a93d676363efb269d7459a27a17fd35804fb47e5) | high | source-fix | fix: if self.app is not actually set avoid a new crash location (#1897 | model |
| 2025-07-04 | [23986fd8](https://github.com/canonical/operator/commit/23986fd88ffcd488462b6009cede136f38c11351) | medium | test-fix | fix: if an event ends with _Abort(0) tests should behave as if it ende | scenario, testing-framework, tests |
| 2025-06-24 | [366d46d5](https://github.com/canonical/operator/commit/366d46d52f24c1fbdf8263549e04bd6c0211c458) | medium | build-fix, ci-fix, source-fix, test-fix | fix: only provide the units belonging to the app in Relation.units (#1 | ci, model, packaging/build, relations, t |
| 2025-06-24 | [31091898](https://github.com/canonical/operator/commit/31091898e169032f7165afe77157be982da521ea) | high | source-fix, test-fix | fix: in meter-status-changed JUJU_VERSION is not set (#1840) | juju-context, main/dispatch, status, tes |
| 2025-06-18 | [25f38f33](https://github.com/canonical/operator/commit/25f38f33b2944543a404c7161f8df8c7d3beb654) | medium | test-fix | fix: testing.PeerRelation properly defaults to no peers (#1832) | relations, scenario, testing-framework,  |
| 2025-06-16 | [ef35afc5](https://github.com/canonical/operator/commit/ef35afc5824e74ccd58aac24b26072f63ea578a7) | medium | test-fix | fix: do not return current unit in a mocked peer relation (#1828) | relations, scenario, testing-framework,  |
| 2025-06-09 | [aa2bc7c3](https://github.com/canonical/operator/commit/aa2bc7c35edb9ee2da60cea5cdc19bf13ed1704b) | medium | build-fix, ci-fix, test-fix | fix: don't use private OpenTelemetry API (#1798) | packaging/build, storage, tests |
| 2025-06-06 | [cb720c85](https://github.com/canonical/operator/commit/cb720c85818a776cb1cf6db419130ccc0f192fbc) | medium | source-fix | fix: Juju allows access to the remote app databag in relation-broken,  | relations, testing-framework |
| 2025-06-06 | [794e0e1a](https://github.com/canonical/operator/commit/794e0e1a720d54f8eb5feee2f15c93e3a6be1177) | medium | source-fix, test-fix | fix: remote unit data is available in relation-departed (#1364) | main/dispatch, model, relations, tests |
| 2025-06-06 | [fb5a1608](https://github.com/canonical/operator/commit/fb5a160808c8c8bf4ed4e2c0e1b1e54fc1a54608) | medium | build-fix, ci-fix | fix: restrict the version of a dependency, opentelemetry-sdk (#1794) | packaging/build |
| 2025-06-04 | [b1b55461](https://github.com/canonical/operator/commit/b1b55461d5a89b93a95bfe507fadfeb522c06a17) | low | test-fix | fix: fix type annotation of container check_infos in ops.testing (#178 | pebble, scenario, testing-framework, tes |
| 2025-06-04 | [f005747b](https://github.com/canonical/operator/commit/f005747b95fe35a1f37b5a53be349487770f8ada) | medium | source-fix, test-fix | fix: correctly load an empty Juju config options map (#1778) | charm, config, tests |
| 2025-05-29 | [983b7c71](https://github.com/canonical/operator/commit/983b7c7152c7c1399cb2414e79ad2e5de14aa270) | medium | test-fix | fix: correctly remove suffix from event string in ops.testing (#1754) | scenario, testing-framework, tests |
| 2025-05-28 | [668701b4](https://github.com/canonical/operator/commit/668701b4396098b3e7a93288cd272c11dd2a8af6) | high | source-fix, test-fix | fix: turn on databag access validation in __init__ (#1737) | main/dispatch, relations, testing-framew |
| 2025-05-15 | [0bb37f62](https://github.com/canonical/operator/commit/0bb37f62adcd705189094208d7e7b50617e53faa) | medium | source-fix | fix: remove apparently unused class in harness (#1733) | testing-framework |
| 2025-05-15 | [1baaba82](https://github.com/canonical/operator/commit/1baaba821a509c5cb45ac6ad09b27ffe1910b22c) | medium | source-fix | fix: fix link in breakpoint output, remove link from Harness error mes | framework, testing-framework |
| 2025-04-28 | [0bf21814](https://github.com/canonical/operator/commit/0bf21814d273ef63b0be04d5b41727c04ee97297) | low | ci-fix, docs-fix | fix: allow TLS 1.2 in ops-tracing (#1705) | ci, docs |
| 2025-04-09 | [a7cfea6e](https://github.com/canonical/operator/commit/a7cfea6e69e0234f6834cd2168437fcf28886b37) | medium | test-fix | fix: try to fix flaky pebble exec test (#1664) | pebble, tests |
| 2025-03-14 | [3dda5b5f](https://github.com/canonical/operator/commit/3dda5b5f64bdea21d43a42431edcca62669c3173) | high | source-fix, test-fix | fix: assorted fixes for Pebble layer merging in Harness and Scenario ( | pebble, scenario, testing-framework, tes |
| 2025-03-04 | [1b10db40](https://github.com/canonical/operator/commit/1b10db4035f92588de59eaf9a506119adfc93f61) | medium | source-fix, test-fix | fix: in tests, raise the same error as Pebble when an invalid service  | pebble, testing-framework, tests |
| 2025-02-13 | [101997e6](https://github.com/canonical/operator/commit/101997e615bd82ed7d599038b9cbcc0518db912b) | medium | test-fix | fix: expose the mocked Juju environment variables via os.environ again | scenario, testing-framework, tests |
| 2025-02-05 | [d0f9f501](https://github.com/canonical/operator/commit/d0f9f50195d9bcb2631c9f28d3efaaaddc0595af) | medium | source-fix, test-fix | fix: ensure that the event snapshot is available when one observer def | framework, tests |
| 2025-02-04 | [427aaf33](https://github.com/canonical/operator/commit/427aaf3339099c3ad584d9f7683926dfa2549e3c) | medium | test-fix | fix: put the Juju version in the environment as well as the JujuContex | scenario, testing-framework, tests |
| 2025-02-03 | [d14c3033](https://github.com/canonical/operator/commit/d14c30331bc4fdde0d5a880475ace04fe6b5d455) | high | source-fix | fix: maintain transaction integrity on first run (#1558) | actions, storage |
| 2025-01-31 | [4911b064](https://github.com/canonical/operator/commit/4911b0641b2c12580f97c22362cc0683dfd9f8a0) | medium | build-fix, docs-fix, test-fix | fix: require today's ops for today's ops-scenario (#1551) | docs, packaging/build, testing-framework |
| 2025-01-23 | [758ee436](https://github.com/canonical/operator/commit/758ee43698c59a0eda34c23e8de89b3dc61c8c5c) | low | source-fix, test-fix | fix: remove ops.main.main deprecation warning, and avoid warnings in a | actions, logging, main/dispatch, scenari |
| 2024-11-28 | [5ecee69c](https://github.com/canonical/operator/commit/5ecee69c203c617603f3c5c2af5297530f8a677f) | medium | test-fix | fix: require the same object to be in the testing state as in the even | scenario, testing-framework, tests |
| 2024-11-20 | [6a17bf93](https://github.com/canonical/operator/commit/6a17bf933114959a968fe65502f429a0dab4452c) | low | source-fix, test-fix | fix: make push_path open in binary mode so it works on non-text files  | model, tests |
| 2024-10-11 | [68cf2d7c](https://github.com/canonical/operator/commit/68cf2d7ce03865e4b23091ac8dbc3757aae4d4b7) | medium | test-fix | fix: raise ModelError on unknown/error status set in Scenario (#1417) | status, testing-framework, tests |
| 2024-10-08 | [18e62cde](https://github.com/canonical/operator/commit/18e62cde967df8082f233c5292d6d620e80cff5a) | medium | source-fix, test-fix | fix: remove enum \| str unions in private TypedDicts (#1400) | pebble, tests |
| 2024-09-25 | [7dec772d](https://github.com/canonical/operator/commit/7dec772d7903f03c33cd5524a7b595db93014908) | medium | source-fix, test-fix | fix: Secret.set_info and Secret.set_content can be called in the same  | charm, model, secrets, tests |
| 2024-09-23 | [20c96236](https://github.com/canonical/operator/commit/20c962360d19f0802c98bbf1878631e4f9122bcb) | medium | source-fix, test-fix | fix: use StatusBase.__init_subclass__ instead of decorator to avoid ob | model, status, testing-framework, tests |
| 2024-09-19 | [2433c1cb](https://github.com/canonical/operator/commit/2433c1cbbd52e8f46ee181a2c8067309bcd98e17) | low | docs-fix | Minor doc fixes. | docs, scenario |
| 2024-09-18 | [97501fd7](https://github.com/canonical/operator/commit/97501fd7dcef41a009a5ed2f3f3af63a541f40b1) | medium | build-fix, test-fix | Catch the correct error when a relation doesn't exist. | packaging/build, relations, scenario, te |
| 2024-09-05 | [8578bdd5](https://github.com/canonical/operator/commit/8578bdd5cf007aab4e86a81bddd66360ce02bff2) | low | test-fix | fix: avoid changing os.environ in Harness (#1359) | testing-framework, tests |
| 2024-09-03 | [cdfd10f3](https://github.com/canonical/operator/commit/cdfd10f34f2d8338fb18dea1185cdd70ea082252) | low | build-fix, docs-fix, source-fix, test-fix | fix: rework ops.main type hints to allow different flavours (callable  | docs, main/dispatch, packaging/build, te |
| 2024-09-02 | [537cc0d0](https://github.com/canonical/operator/commit/537cc0d02ceadc85a1b682289b53283520ad0f3a) | medium | build-fix, test-fix | Fix merge. | packaging/build, scenario, secrets, test |
| 2024-08-26 | [79691874](https://github.com/canonical/operator/commit/796918744ef259df0a449a4366b2c184da732029) | medium | source-fix | fix: correct the signature of .events() (#1342) | framework, main/dispatch |
| 2024-08-16 | [43b5af9f](https://github.com/canonical/operator/commit/43b5af9f8cf9452ab66766e412bf37dc92d359b4) | medium | source-fix, test-fix | fix: Juju passes the expiry in a field 'expiry', not 'expires' (#1317) | model, tests |
| 2024-08-13 | [62fdfc03](https://github.com/canonical/operator/commit/62fdfc03471c2569c704607868bc62c3771389fc) | medium | test-fix | fix: update secret label when getting with both id and label (#172) | scenario, secrets, tests |
| 2024-08-13 | [00ce9b0d](https://github.com/canonical/operator/commit/00ce9b0d8a99f0a24cfafea9e6a89d4eb9f87d46) | medium | docs-fix, test-fix | fixed comma and test-pebble-push example | docs, pebble |
| 2024-07-31 | [de641eca](https://github.com/canonical/operator/commit/de641ecaeae225233b4782e6e37916262476804e) | medium | build-fix, test-fix | ulterior fix | packaging/build, scenario, tests |
| 2024-07-31 | [1d7987fe](https://github.com/canonical/operator/commit/1d7987fe4880cbf8ebd11a1c5beade57711421d4) | medium | test-fix | fixed juju-info network | networking, scenario, tests |
| 2024-07-22 | [fea6d207](https://github.com/canonical/operator/commit/fea6d2072435a62170d4c01272572f1a7e916e61) | medium | source-fix, test-fix | fix: use temp dir for secret data (#1290) | model, secrets, tests |
| 2024-07-17 | [58e514e7](https://github.com/canonical/operator/commit/58e514e7342996acf26adc2627d615dfc17553aa) | medium | build-fix, test-fix | fix: minimal secret fixing, so that secret-remove and secret-expired e | packaging/build, scenario, secrets, test |
| 2024-07-02 | [5a21cd28](https://github.com/canonical/operator/commit/5a21cd28a47b8d5f1142d794130ae70f23b5cd26) | medium | source-fix, test-fix | fix: add checks and log_targets to ops.testing (#1268) | pebble, testing-framework, tests |
| 2024-07-02 | [8c62a1ea](https://github.com/canonical/operator/commit/8c62a1ea2d663df001c43e8e5c8b6c9252dabf16) | medium | docs-fix, test-fix | Fix merging. | docs, pebble, relations, scenario, secre |
| 2024-06-25 | [79706f40](https://github.com/canonical/operator/commit/79706f401d93a4e85b729de52a81367f6d3f6451) | high | source-fix, test-fix | fix: adjust Harness secret behaviour to align with Juju (#1248) | charm, framework, model, secrets, testin |
| 2024-06-21 | [385bdf03](https://github.com/canonical/operator/commit/385bdf036a68d3a6005fe08b910807af5123d392) | medium | test-fix | fixed config mutation in state | config, scenario, tests |
| 2024-06-12 | [2a648c7f](https://github.com/canonical/operator/commit/2a648c7fa2119cfa55670995c1396f78adc2ca43) | medium | test-fix | fix: properly clean up after running setup_root_logging in test_log (# | tests |
| 2024-06-11 | [a49ea4d1](https://github.com/canonical/operator/commit/a49ea4d1fde789d623505e25814fc9041ac3e32d) | medium | build-fix | fix: correct email address in PyPI project metadata (#1257) | packaging/build |
| 2024-06-07 | [d8c98070](https://github.com/canonical/operator/commit/d8c98070e24707092de82f2942506a6157ef58b3) | medium | source-fix | fix: add connect timeout for exec websockets to avoid hanging (#1247) | pebble |
| 2024-06-05 | [dcbe21bd](https://github.com/canonical/operator/commit/dcbe21bd3ffd21255cdb5e7ae5b4664fcbec3da1) | medium | test-fix | fix: fix TypeError when running test.pebble_cli (#1245) | pebble, tests |
| 2024-05-24 | [7e7a18bd](https://github.com/canonical/operator/commit/7e7a18bdb3eb0e44a43e7f0618e0278ce7b17052) | low | source-fix | fix: don't use f-strings in logging calls (#1227) | model, pebble, storage |
| 2024-05-23 | [0dd27df3](https://github.com/canonical/operator/commit/0dd27df3d828b2d62e0a396667466a8f0263e45e) | medium | source-fix, test-fix | fix: the `other` argument to `RelatationDataContent.update(...)` shoul | model, tests |
| 2024-04-17 | [fa185b48](https://github.com/canonical/operator/commit/fa185b48563b4b67c20a8b46dbae03c71efc8fe9) | medium | ci-fix, docs-fix, source-fix, test-fix | fix!: correct the model config types (#1183) | ci, config, docs, model, testing-framewo |
| 2024-04-17 | [d4a48fdf](https://github.com/canonical/operator/commit/d4a48fdf28511546ca939dc10d49f0e803a4472e) | medium | test-fix | fix (harness): only inspect the source file if it will be used (#1181) | testing-framework, tests |
| 2024-04-12 | [dbb843eb](https://github.com/canonical/operator/commit/dbb843ebf9a91cf040ed8900e8a8b7f870501a82) | medium | source-fix, test-fix | fix: revert support of change-update notice due to Juju reversion (#11 | charm, pebble, testing-framework, tests |
| 2024-03-28 | [92de04cd](https://github.com/canonical/operator/commit/92de04cd803afc3e344c2fd0dbcf4782e3712271) | medium | test-fix | Fix the config consistency checker type checking. | config, scenario, tests |
| 2024-03-18 | [58046522](https://github.com/canonical/operator/commit/5804652253926fea5c2aae5952d3032cea12ca5f) | medium | test-fix | fix: add_relation consistency check and default network (#1138) | networking, relations, testing-framework |
| 2024-03-15 | [13a178af](https://github.com/canonical/operator/commit/13a178afccdd7c2167749e113956e54cc7dae614) | medium | source-fix, test-fix | fix: inspect the correct signature when validating observe arguments ( | framework, tests |
| 2024-02-07 | [761b18bb](https://github.com/canonical/operator/commit/761b18bbf0dfc034be2dca8df4dae521d0f80f35) | medium | test-fix | fixed utest | tests |
| 2024-01-30 | [46781308](https://github.com/canonical/operator/commit/467813081c45c5280cecf55d728215ba9b5dcd8f) | medium | test-fix | fix: add pebble log targets and checks to testing plan (#1111) | pebble, testing-framework, tests |
| 2024-01-17 | [a1e99ca3](https://github.com/canonical/operator/commit/a1e99ca3173cc8b829b853fc3ff477dd3da9b126) | medium | source-fix | static fixes | scenario |
| 2024-01-10 | [4360c204](https://github.com/canonical/operator/commit/4360c204599800ce52ee499998db92d12be2f7e3) | medium | build-fix | fix: revert macaroonbakery exception now that underlying issue is fixe | general |
| 2024-01-09 | [ba7972ee](https://github.com/canonical/operator/commit/ba7972eef67fd00b539cac862b86448e661397aa) | medium | test-fix | fixed once more jujuv check | scenario, secrets, tests |
| 2024-01-03 | [b88efdc4](https://github.com/canonical/operator/commit/b88efdc4875b868dd267d5a4d729b6317e872270) | medium | test-fix | added test fixes | secrets, tests |
| 2023-12-12 | [09b2d8f8](https://github.com/canonical/operator/commit/09b2d8f8e80f02b7cc80375bd0f92865ec6fb686) | medium | build-fix, ci-fix, test-fix | fix: pin macaroonbakery version (#1090) | ci |
| 2023-12-05 | [3af35d0e](https://github.com/canonical/operator/commit/3af35d0e44a77b96999c872da9cb3e0fc906e201) | medium | test-fix | fixed network tests | networking, tests |
| 2023-12-05 | [4669fc1f](https://github.com/canonical/operator/commit/4669fc1f5563c59897d9a8baec6d9e6ab44f5407) | medium | test-fix | fixed tests | tests |
| 2023-12-05 | [175b9107](https://github.com/canonical/operator/commit/175b91070837774657cca7e1467a686efc762130) | medium | test-fix | fixed tests | tests |
| 2023-11-29 | [18abc170](https://github.com/canonical/operator/commit/18abc170a8179212596be2655b5b49078562bc71) | medium | source-fix, test-fix | fix: handle users/groups with no names in push_path (#1082) | model, testing-framework, tests |
| 2023-11-29 | [681bce21](https://github.com/canonical/operator/commit/681bce21ebbc89cb511ace0d39139b622e5bf903) | medium | source-fix, test-fix | fix: handle parsing ISO datetimes where the microseconds round up to 1 | tests |
| 2023-11-24 | [889c78ec](https://github.com/canonical/operator/commit/889c78ecb02fee854540a2f457f55ad14b3ba9ce) | medium | test-fix | fix: non-leaders can only view app secrets (#1076) | secrets, testing-framework, tests |
| 2023-11-22 | [0b895434](https://github.com/canonical/operator/commit/0b895434b7069b84263d187dce37ccdcb5504883) | low | docs-fix | Doc fixes | docs |
| 2023-11-21 | [0aab2af5](https://github.com/canonical/operator/commit/0aab2af523f248d6a7ac4c6c6ef282f6b125ccb7) | medium | test-fix | some more tests and metadata rule fixes | scenario, secrets, tests |
| 2023-11-17 | [89bc81a7](https://github.com/canonical/operator/commit/89bc81a7d73b832f7affa8df448041382f0102b2) | medium | test-fix | fix secret id canonicalization | scenario, secrets, tests |
| 2023-11-16 | [e4b0f9d4](https://github.com/canonical/operator/commit/e4b0f9d4e232d384745a9823bcf0e481b222a006) | high | source-fix, test-fix | fix: reduce mode of SQLite storage file to 0o600 (#1057) | security, storage, tests |
| 2023-11-16 | [1c0ff40d](https://github.com/canonical/operator/commit/1c0ff40dd5a40445b6d8c22c76f066ecbf45995e) | medium | build-fix, test-fix | fix falsy config defaults | config, packaging/build, scenario, tests |
| 2023-10-24 | [90f7cc62](https://github.com/canonical/operator/commit/90f7cc62a29d0edf0f3cf3fd96851a23b3c9c816) | medium | source-fix | fixed type | scenario |
| 2023-10-23 | [e03c0847](https://github.com/canonical/operator/commit/e03c08471049af3f741ab0038f02105fb6bb01db) | medium | docs-fix, test-fix | fixed deferred bug | docs, scenario, tests |
| 2023-10-23 | [c83bd8aa](https://github.com/canonical/operator/commit/c83bd8aae2ebc5f8395d589f3ebfe1513ccbc8db) | medium | docs-fix | docs fix | docs, scenario |
| 2023-10-20 | [379738cc](https://github.com/canonical/operator/commit/379738ccfa660d78a496c3adeee4e00379dceba2) | medium | test-fix | fixed bug with event names | scenario, tests |
| 2023-10-20 | [29e47ab9](https://github.com/canonical/operator/commit/29e47ab9d0b51f81c01f825e53a5d795e0fb2986) | medium | build-fix, docs-fix, test-fix | fixed error types and added resource mocks | docs, packaging/build, scenario, storage |
| 2023-10-19 | [a899d6d6](https://github.com/canonical/operator/commit/a899d6d60e05db9e8c33efae29339beacb495774) | medium | test-fix | SecretNotFoundError should be raised when a secret is not found | scenario, secrets, tests |
| 2023-10-16 | [a88cd4fc](https://github.com/canonical/operator/commit/a88cd4fcf945f08fab94f44eaf4d937b15df5a04) | medium | ci-fix, test-fix | Remove the temporary fix, which shouldn't be required any more. (#1046 | ci |
| 2023-10-04 | [942bd236](https://github.com/canonical/operator/commit/942bd23675a8926630051b2b005ce38f80f5339b) | medium | source-fix, test-fix | fix: push_path and pull_path include empty directories (#1024) | model, testing-framework, tests |
| 2023-09-22 | [62a46d35](https://github.com/canonical/operator/commit/62a46d35b33c61627822a199e793ef05d553a407) | medium | docs-fix | fixed some outdated docs | docs |
| 2023-09-11 | [e4d0e9dc](https://github.com/canonical/operator/commit/e4d0e9dccb33fea6b951be7f5772c7b159e78a47) | medium | test-fix | fixed test name conflict | tests |
| 2023-09-08 | [fb9ce8de](https://github.com/canonical/operator/commit/fb9ce8de5ffa46212210f9d9d2a2b82627be1fb5) | medium | source-fix | fixed error because pathlib.Path.rmdir will bork on nonempty dir | scenario |
| 2023-09-06 | [47fc752b](https://github.com/canonical/operator/commit/47fc752b20efc7e4cdd04f70f13d0199019d0081) | medium | build-fix | bugfix | packaging/build, scenario |
| 2023-09-04 | [ba433a2f](https://github.com/canonical/operator/commit/ba433a2ffbac9526c901312fb79a40b9c06df189) | medium | test-fix | better error on meta not found | scenario, tests |
| 2023-09-01 | [7932b126](https://github.com/canonical/operator/commit/7932b12698073207bfee9cc5aa00988f99134d14) | medium | build-fix | fixed tox env | packaging/build |
| 2023-08-28 | [c9bba5b0](https://github.com/canonical/operator/commit/c9bba5b00bc99cab1c679dfd0814c1f2d0294b5c) | medium | source-fix, test-fix | Raise error in wait_output if stdout is already being consumed (#998) | pebble, tests |
| 2023-07-28 | [2e2aca9b](https://github.com/canonical/operator/commit/2e2aca9b62f1504c08102d701df3098e13a8bccc) | medium | test-fix | fixed env cleanup on charm error | scenario, tests |
| 2023-07-27 | [fad95d7d](https://github.com/canonical/operator/commit/fad95d7d91f7b51738e127a6314f4718ad52f987) | medium | source-fix | Fix type of StatusBase.name (#980) | model, status |
| 2023-07-21 | [7ad5df1f](https://github.com/canonical/operator/commit/7ad5df1fdd65a895febb98e7121b6ef275168cf6) | medium | test-fix | relation id staticmethod fix | relations, scenario, tests |
| 2023-07-20 | [7d4208dc](https://github.com/canonical/operator/commit/7d4208dcbee9df85fa04d6f92d9ceae9876cfde1) | medium | test-fix | fixed itest | tests |
| 2023-07-11 | [528d915f](https://github.com/canonical/operator/commit/528d915f424313e9b3b9de112127ce7ddac37495) | medium | build-fix, source-fix, test-fix | Remove workaround for non-unique consumer labels bug (juju/juju#14916) | model, packaging/build, tests |
| 2023-07-11 | [617be0a2](https://github.com/canonical/operator/commit/617be0a27dc373c10f689ae239c19059104a4c1d) | medium | test-fix | public next_relation_id and fix succession | relations, scenario, tests |
| 2023-06-28 | [530faea8](https://github.com/canonical/operator/commit/530faea856f6ca7f0effe8e7d21b078becdfdb7c) | medium | build-fix | fixed tox env, python 3.8 compat fix | packaging/build, scenario |
| 2023-06-23 | [9dbb6b66](https://github.com/canonical/operator/commit/9dbb6b6643609590566037d3f0a4a28dfc9fa25a) | medium | source-fix | type error in __init__.__all__ | scenario |
| 2023-06-22 | [1b68e559](https://github.com/canonical/operator/commit/1b68e559d34a23aa81d2e5c945ebdf1205b487d0) | low | test-fix | fixed spacing | ci, scenario, tests |
| 2023-06-16 | [6fcda007](https://github.com/canonical/operator/commit/6fcda007bff2671fa97924fbf70f480753f862d6) | high | test-fix | Avoid error in FileInfo repr due to permissions being None (#956) | security, testing-framework, tests |
| 2023-06-16 | [cbaec52e](https://github.com/canonical/operator/commit/cbaec52e6af2543dc0a24f917e8eea0d93232f1c) | medium | source-fix, test-fix | Fix issue with relative paths in Container.push_path (#949) | model, pebble, tests |
| 2023-06-14 | [c18f9d40](https://github.com/canonical/operator/commit/c18f9d40eec9a994d9960af76911c09500417c6d) | low | ci-fix, test-fix | Reinstate alertmanager-k8s-operator CI tests now that issue is fixed ( | ci |
| 2023-06-13 | [78ec6d57](https://github.com/canonical/operator/commit/78ec6d576c969eeecacbfd71d7940d43950b7731) | medium | build-fix, docs-fix, source-fix, test-fix | Fix sphinx-build warnings and turn warnings into errors (#942) | charm, docs, framework, main/dispatch, m |
| 2023-06-08 | [91c1ea12](https://github.com/canonical/operator/commit/91c1ea1253f9cdaa637619170b2e62bffa85bb66) | medium | docs-fix | out.logs type fix | docs |
| 2023-06-07 | [6ad9f3a1](https://github.com/canonical/operator/commit/6ad9f3a1ad79d03381cd025f01aab6120151adc1) | low | ci-fix | fix ci | ci, scenario |
| 2023-06-05 | [a4019cee](https://github.com/canonical/operator/commit/a4019cee8ba37c7ca1ff23aea03b9eea30a2669b) | medium | test-fix | fixed itest | tests |
| 2023-05-11 | [cc51f046](https://github.com/canonical/operator/commit/cc51f0468e41971ea106517500d4c19985fec6d3) | medium | docs-fix, test-fix | fixed consistency checker | docs, scenario, tests |
| 2023-05-10 | [cb75672b](https://github.com/canonical/operator/commit/cb75672b924f55214764d18af54554eeb916ff66) | low | docs-fix | fixed badge | docs |
| 2023-05-09 | [47743cb3](https://github.com/canonical/operator/commit/47743cb3280d4ce648c5a67832d8c48044f50e74) | medium | build-fix | fixed links, vbump | packaging/build |
| 2023-05-09 | [2eab49d3](https://github.com/canonical/operator/commit/2eab49d3a0e934f0ed39a3408707a064ca6a139e) | low | build-fix, docs-fix | fixed badges | docs, packaging/build |
| 2023-05-04 | [9ba7ec6b](https://github.com/canonical/operator/commit/9ba7ec6b6018cb6fdf384de74ddfca8f642e918c) | medium | source-fix | fixed bug in snapshot | scenario |
| 2023-05-04 | [977822b5](https://github.com/canonical/operator/commit/977822b56abb345e712c95b95566d57036b871e5) | medium | source-fix | fixed bug in snapshot | scenario |
| 2023-05-03 | [cc984f67](https://github.com/canonical/operator/commit/cc984f67f3979081914fe8ccb59a3f701bf4afba) | medium | test-fix | fixed pytest template for snapshot | scenario |
| 2023-05-03 | [ebfc2fb3](https://github.com/canonical/operator/commit/ebfc2fb358f079b9f0748d9c80d70e546371e473) | medium | source-fix | better error message on charm error | scenario |
| 2023-04-24 | [32318607](https://github.com/canonical/operator/commit/3231860787708980cb0c144db5d19df6d35bc51c) | medium | source-fix | fixed dataclass error | scenario |
| 2023-04-24 | [734e12dc](https://github.com/canonical/operator/commit/734e12dcfde93d7081aed5573e011128d98fd84a) | medium | test-fix | Fixing the function signature of send_signal in _TestingPebbleClient ( | pebble, testing-framework, tests |
| 2023-04-21 | [2ac131c8](https://github.com/canonical/operator/commit/2ac131c8a432838bcac51e43044d760d4ab30903) | medium | source-fix | fixed snapshot if no relations | relations, scenario |
| 2023-04-21 | [d53e0763](https://github.com/canonical/operator/commit/d53e0763962c8934da0c2bb3aac79f94f6fcdf7f) | medium | source-fix | fixed main | scenario |
| 2023-04-20 | [27f2c9cc](https://github.com/canonical/operator/commit/27f2c9cc1f16113aa9ad1b1078dc449787b50403) | medium | build-fix | fixed loglevel | packaging/build, scenario |
| 2023-04-05 | [14f3baf5](https://github.com/canonical/operator/commit/14f3baf50daab59f98c16273aea95bca9edabbb9) | medium | test-fix | cyclic imports fixed | relations, scenario, tests |
| 2023-03-30 | [007facdd](https://github.com/canonical/operator/commit/007facdda55203285b15367c393ddb3e1ad35181) | medium | source-fix | fixed relation-list for subs | relations, scenario |
| 2023-03-30 | [80ba3438](https://github.com/canonical/operator/commit/80ba34386687265326b02db6eda7f54159710243) | medium | test-fix | fixed emission for peer/sub | relations, scenario, tests |
| 2023-03-29 | [e9b0b3e2](https://github.com/canonical/operator/commit/e9b0b3e254d89c56d3c547511bda36a9e6740dfc) | medium | test-fix | utest fix | relations, tests |
| 2023-03-29 | [e640ec9e](https://github.com/canonical/operator/commit/e640ec9edbeb981b4016547a7466e43c26f3a69a) | medium | test-fix | fixed truthiness | relations, scenario, tests |
| 2023-03-28 | [54d0d9af](https://github.com/canonical/operator/commit/54d0d9af7f63fc080072607c4ebcbba9344a1191) | medium | build-fix | fixed tox | packaging/build |
| 2023-03-28 | [91675734](https://github.com/canonical/operator/commit/91675734c8ece417af61ba18b3ff6e4e9142b734) | low | build-fix, test-fix | lint and fix tests | packaging/build, pebble, tests |
| 2023-03-16 | [9feabfba](https://github.com/canonical/operator/commit/9feabfba32f4e2a04e8f6febc47662e30456ba01) | medium | build-fix | mount meta bugfix | packaging/build, scenario |
| 2023-03-16 | [77aab0bf](https://github.com/canonical/operator/commit/77aab0bf4e60a96b568ab7e6773d1700b3266f67) | medium | source-fix | fixed stored state and deferred events | scenario |
| 2023-03-10 | [3ad495a0](https://github.com/canonical/operator/commit/3ad495a00d5d3a909e1875f39d8f60009910ffe9) | medium | test-fix | fixed bug in config-get | config, scenario, tests |
| 2023-03-10 | [bb8e7d18](https://github.com/canonical/operator/commit/bb8e7d183975f1ffae6552ebb3bc3750bbdd721b) | medium | docs-fix, test-fix | fixed tests, added docs | docs, relations, scenario, tests |
| 2023-03-07 | [f134d578](https://github.com/canonical/operator/commit/f134d578b9253fab80d3b58178ba4d3398898c80) | medium | source-fix | bindaddr fix | scenario |
| 2023-02-21 | [68b7b7ce](https://github.com/canonical/operator/commit/68b7b7ce04bec7c8c59290141ab01a10d97dbc3c) | medium | build-fix, docs-fix, test-fix | fixed some pebble model and network model issues | docs, networking, packaging/build, pebbl |
| 2023-02-17 | [206d501a](https://github.com/canonical/operator/commit/206d501a894bca1229f3e71b3ca6d93ba9f643b5) | medium | source-fix | fixed pebble plan | pebble, scenario |
| 2023-02-17 | [50a3867d](https://github.com/canonical/operator/commit/50a3867d6084f16ec130646e20508aa08daa7ce7) | low | docs-fix | fixed some typos in network-get | networking, scenario |
| 2023-02-13 | [6bccee69](https://github.com/canonical/operator/commit/6bccee69b37ed24a189c1148d1384a3f400a23b6) | medium | test-fix | fixed secret tests | scenario, secrets, tests |
| 2023-02-13 | [6f1323d7](https://github.com/canonical/operator/commit/6f1323d72f4f6ab90598e2a748549204ca892229) | medium | test-fix | fixed tests | relations, scenario, secrets, tests |
| 2023-02-07 | [5afc2842](https://github.com/canonical/operator/commit/5afc2842e72a0d84eca6dc4fbd420e656ac9bb54) | low | source-fix, test-fix | Don't call secret-info-get with both ID and label (it's a Juju error)  | framework, model, secrets, testing-frame |
| 2023-02-07 | [08f8ee18](https://github.com/canonical/operator/commit/08f8ee186f6e918b0f805a6716de1d9a92b247aa) | medium | test-fix | fixed relation events | relations, scenario, tests |
| 2023-02-02 | [f6daaab3](https://github.com/canonical/operator/commit/f6daaab3c66906b197a866677b0c6962d2087510) | medium | ci-fix | fixed builder again | ci |
| 2023-02-02 | [4c7ac115](https://github.com/canonical/operator/commit/4c7ac1158c2510efadf1650db0419ac1a3889104) | medium | build-fix, ci-fix | fixed builder | ci, packaging/build |
| 2023-02-02 | [fe61cb5f](https://github.com/canonical/operator/commit/fe61cb5fbca3d1a9aada62898d0a9b913c18e933) | medium | build-fix | fixed decompose | packaging/build, scenario |
| 2023-02-02 | [dee0a94b](https://github.com/canonical/operator/commit/dee0a94b1c693f3dfb0aeb45b53fe2ec130683fa) | medium | ci-fix | fixed asset paths | ci |
| 2023-02-02 | [65cbd567](https://github.com/canonical/operator/commit/65cbd5679dbcaa4aa9d473cfedfb1ae24a227408) | medium | build-fix, ci-fix | fixed relation-meta | ci, packaging/build, relations, scenario |
| 2023-01-26 | [caed680b](https://github.com/canonical/operator/commit/caed680b933c6c62e1305ec7773a9bf0c81e5661) | medium | test-fix | fix TypeError: CharmBase.__init__() takes 2 positional arguments but 3 | tests |
| 2023-01-25 | [49aaa0a0](https://github.com/canonical/operator/commit/49aaa0a0ecd5c8832b718929a4e4cddf88cf138b) | medium | source-fix | fixed bug in relation_ids | relations, scenario |
| 2023-01-25 | [d2b4ff59](https://github.com/canonical/operator/commit/d2b4ff5998e7d7931cdbdb3c4679fdb76ef68994) | medium | test-fix | relation test for relation-ids fix | relations, tests |
| 2023-01-20 | [7faa5a24](https://github.com/canonical/operator/commit/7faa5a2451e4531492d4513feaea0617512f6e9d) | medium | ci-fix, test-fix | Reenable alertmanager-operator tests now that charm is fixed on ops 2. | ci |
| 2023-01-18 | [5f79a65e](https://github.com/canonical/operator/commit/5f79a65e10099baf0fc146e3c8c52afce5f0e387) | medium | source-fix | config_get fix | config, scenario |
| 2023-01-17 | [dc8e0f3e](https://github.com/canonical/operator/commit/dc8e0f3ee5cc35ff0da3bfafa7d45d6a9737307e) | medium | docs-fix | Fix URLs in HACKING.md (#892) | docs |
| 2023-01-02 | [d5909c81](https://github.com/canonical/operator/commit/d5909c81930f360fd5f187a46377af088087c627) | medium | test-fix | fixed play_until_complete | scenario, tests |
| 2022-12-02 | [bd5c9f32](https://github.com/canonical/operator/commit/bd5c9f324d8107f6aa841a23657d25b0edb1ce2f) | medium | build-fix, test-fix | some import fixes and utilities | packaging/build, scenario, tests |
| 2022-12-01 | [320e7e04](https://github.com/canonical/operator/commit/320e7e04e737000abc1d25729ccd29d6e783e6df) | medium | build-fix, docs-fix, source-fix | Clarify what Container.get_plan actually returns (#864) | docs, model, pebble |
| 2022-11-30 | [516abffb](https://github.com/canonical/operator/commit/516abffb8c60af8de4d4ef7efb5671fd52cdd872) | medium | source-fix, test-fix | Fix logging in can_connect, add tests; remove pebble.Error methods (#8 | model, pebble, testing-framework, tests |
| 2022-11-29 | [81348196](https://github.com/canonical/operator/commit/81348196949138d43b40f98708808b52d8b758a8) | medium | build-fix, docs-fix, test-fix | fixed some bugs and testing setup | docs, packaging/build, scenario, testing |
| 2022-11-28 | [870cdeff](https://github.com/canonical/operator/commit/870cdeff229f7331cc8b40d6fa44a675e50992cd) | low | build-fix, ci-fix | fix fmt tox env | packaging/build |
| 2022-11-14 | [da4a0ecc](https://github.com/canonical/operator/commit/da4a0eccdadf3539b04441154a5f1bcc56aa5480) | low | docs-fix, source-fix | Fix typo (#841) | charm |
| 2022-08-30 | [deccdd6f](https://github.com/canonical/operator/commit/deccdd6fd72f4cf728e07a2aab960edba8b69a95) | medium | source-fix, test-fix | Fix incorrect kwarg handling in testing backend storage_list (#820) | framework, storage, testing-framework, t |
| 2022-08-15 | [ac7b9f09](https://github.com/canonical/operator/commit/ac7b9f0944d7a313234b43ebda95df483dd17329) | medium | source-fix | fixed issue with pebble imports (#810) | model, pebble |
| 2022-08-09 | [fff92e46](https://github.com/canonical/operator/commit/fff92e46b800ea7be0a768d0431f27abe7c29766) | low | source-fix, test-fix | fixed issues with relation data read (#795) | framework, model, relations, testing-fra |
| 2022-07-20 | [8f1c207b](https://github.com/canonical/operator/commit/8f1c207b54675f7bab95095876f521c47ab991bd) | low | docs-fix, source-fix | doc fix for config-changed (#804) | charm, config, docs |
| 2022-07-15 | [1ed81e19](https://github.com/canonical/operator/commit/1ed81e198e6285a1bc9bdc98e95de94d77c14d3b) | low | docs-fix, test-fix | Fix docstring (#802) | docs, testing-framework, tests |
| 2022-07-06 | [4ffc1256](https://github.com/canonical/operator/commit/4ffc12569dc576d2a9f9f44269b77616b15dc430) | medium | source-fix, test-fix | Fixed bug in ops.Model where non-string keys could be used to write re | model, relations, testing-framework, tes |
| 2022-06-23 | [ad82d375](https://github.com/canonical/operator/commit/ad82d375dd8b26f7f751fe7ff5f1d8db4dc86719) | low | test-fix | Remove overzealous Harness.add_storage error check. (#781) | storage, testing-framework, tests |
| 2022-06-13 | [1b086258](https://github.com/canonical/operator/commit/1b086258eab810f2edfca12fc3bae292b500873b) | medium | source-fix, test-fix | Better error for relation data access in relation-broken events (#765) | model, relations, testing-framework, tes |
| 2022-06-08 | [8df3d2f1](https://github.com/canonical/operator/commit/8df3d2f104477de7467d4f87d1f8691de124e518) | medium | source-fix, test-fix | Improved error message for invalid storage key (#771) | model, storage, tests |
| 2022-05-23 | [23bf543c](https://github.com/canonical/operator/commit/23bf543c1f1c704a4ee6fe8af3c71d5e18a058f7) | medium | source-fix | Fixes address info value getter (#757) | model |
| 2022-03-15 | [45e1e5a9](https://github.com/canonical/operator/commit/45e1e5a9e4e99492d09423436b8378f955c4f0a3) | low | docs-fix, source-fix | Fixing updated link in docstrings (#722) | docs, framework |
| 2022-03-02 | [6340f8a4](https://github.com/canonical/operator/commit/6340f8a4cd7cbf3ac4b52dbe14a8a1414c95e8a9) | medium | build-fix, ci-fix | skip broken ipython version to fix CI (#710) | ci, packaging/build |
| 2022-02-22 | [46cf8425](https://github.com/canonical/operator/commit/46cf84253ff52dd5ce40b1b108b883302f8ef152) | medium | source-fix, test-fix | Fix incorrect variadic arg wrangling in get_services (#702) | model, tests |
| 2022-02-21 | [88529c95](https://github.com/canonical/operator/commit/88529c95575301f47a1b420dc29394c1a1b9b50b) | low | docs-fix, source-fix | FIX remove_path docstring to relfect current behaviour. (#698) | docs, pebble |
| 2021-11-05 | [824aa2d8](https://github.com/canonical/operator/commit/824aa2d8996ea548c913317c2df6bac258f0737b) | low | source-fix | fix observer type hint (#664) | framework, type-annotations |
| 2021-11-03 | [91b6551a](https://github.com/canonical/operator/commit/91b6551ac2cdda5ade84e2fd2bddd14b198cae71) | medium | source-fix, test-fix | Exec test fixes and "for line in process.stdout" fix (#655) | pebble, tests |
| 2021-11-03 | [626527f9](https://github.com/canonical/operator/commit/626527f988c007316218891830b1265fc936295e) | low | source-fix, test-fix | Fix storage events with multiple hyphens (#663) | main/dispatch, storage, tests |
| 2021-10-25 | [4bacd77f](https://github.com/canonical/operator/commit/4bacd77f819c409ef844fbec568735b64ef4f646) | medium | source-fix | Fix for container.restart in older versions of Pebble (#657) | model, pebble |
| 2021-10-15 | [c25db1f3](https://github.com/canonical/operator/commit/c25db1f3164d1ed793b8edd5111fe80dd5ebf7ad) | medium | test-fix | Fix harness remove relation unit (#640) | relations, testing-framework, tests |
| 2021-09-25 | [e39f011a](https://github.com/canonical/operator/commit/e39f011ae93d2c940a4b59d96a8d39719ee03c6e) | low | docs-fix, source-fix, test-fix | Spelling fixes found by codespell. (#625) | charm, framework, model, pebble, tests |
| 2021-09-09 | [8c0d17af](https://github.com/canonical/operator/commit/8c0d17afb49cae56b4b1d2911f98f7eee3437d2d) | medium | test-fix | Fix storage harness tests -- don't try to look up set items by key (#6 | storage, testing-framework, tests |
| 2021-08-25 | [37fdcbaf](https://github.com/canonical/operator/commit/37fdcbaf8cf56f639c02de12685941bf9319a773) | low | source-fix, test-fix | Fix Container.restart() accidentally operating on strings, add a testc | ci, model, pebble, tests |
| 2021-08-18 | [8aea6bc3](https://github.com/canonical/operator/commit/8aea6bc31b5f8bf5fad3271b62b73a432dc5e067) | medium | test-fix | Fix desynch of charm model on Harness.remove_relation (#581) | relations, testing-framework, tests |
| 2021-07-24 | [5943a59c](https://github.com/canonical/operator/commit/5943a59ccde766c832d59229f3ac431587799f34) | medium | source-fix, test-fix | Fix Pebble push() handling of binary files (#574) | pebble, tests |
| 2021-05-06 | [ef26d3d0](https://github.com/canonical/operator/commit/ef26d3d0f39ec18d14b229e7a1576e1e5baa69b3) | medium | test-fix | Fix test_lib on Python 3.8.10 due to importlib relative path changes ( | tests |
| 2021-05-06 | [178b6d84](https://github.com/canonical/operator/commit/178b6d84770faa87e0edc20a5f5d5521ad378c4b) | medium | test-fix | Make test CLI show error type for clarity (#523) | pebble, tests |
| 2021-04-23 | [be1fdf06](https://github.com/canonical/operator/commit/be1fdf0698e33ed2274eb417da5b64f2656239fb) | medium | source-fix | Attempt to fix model.py for Python 3.5.2 (default on Xenial) (#520) | model |
| 2020-10-16 | [8eb29775](https://github.com/canonical/operator/commit/8eb297753c23177fdddfcdabfe3700c90e433942) | medium | test-fix | Fixed environment in the import tests. (#426) | tests |
| 2020-10-16 | [9d3ae020](https://github.com/canonical/operator/commit/9d3ae020d7d89a83f9f2797a70156cba2faa10a9) | low | build-fix, docs-fix, source-fix, test-fix | Fixed several small details in lot of docstrings. (#425) | docs, framework, main/dispatch, model, p |
| 2020-10-02 | [d5a8b6b4](https://github.com/canonical/operator/commit/d5a8b6b4b27abb450b119a2b60e054e5603d4fd0) | medium | docs-fix, test-fix | Fix tests when PyYAML is missing libyaml extensions (#420) | docs, tests |
| 2020-09-15 | [7ef5543f](https://github.com/canonical/operator/commit/7ef5543f8d0ef767c4531c2ae002e04bad1e3af3) | low | docs-fix, test-fix | fix docstring on Harness.add_relation_unit WRT events (#401) | docs, relations, testing-framework, test |
| 2020-09-09 | [9e2b1f8f](https://github.com/canonical/operator/commit/9e2b1f8f76b61b45cf67f65e791ae8be3bdcf886) | low | docs-fix, source-fix | Fix trivial typo in docstring (#400) | docs, main/dispatch |
| 2020-08-24 | [abeec5d1](https://github.com/canonical/operator/commit/abeec5d16c03d79b28c383a00580eee809375830) | medium | docs-fix, source-fix | minor docs fix (#389) | docs, model |
| 2020-08-13 | [55158e3d](https://github.com/canonical/operator/commit/55158e3d1963106702222454c1cb8912c30dd077) | medium | test-fix | fix up logging tests impacting global state so much (#373) | tests |
| 2020-05-06 | [47af0fc9](https://github.com/canonical/operator/commit/47af0fc9f86dc5b16e88a83a00377864a1541734) | medium | test-fix | ops/testing.py: Harness fixes (#253) | testing-framework, tests |
| 2020-05-05 | [daea7094](https://github.com/canonical/operator/commit/daea70944013481fe4620038a5b02dcc4de9eaa3) | medium | docs-fix, test-fix | Fix doctrings for add_relation_unit in ops.testing (#251) | docs, relations, testing-framework, test |
| 2020-05-05 | [1d5994f9](https://github.com/canonical/operator/commit/1d5994f920eb3d25a68784dbd893bf892a95d5ac) | medium | source-fix, test-fix | Import internal modules in a controlled way. Fixes #247. (#248) | tests |
| 2020-04-20 | [7c22e4c6](https://github.com/canonical/operator/commit/7c22e4c602a1232035c333f013630cc12fb0e978) | medium | test-fix | test/test_harness.py: Fix the ordering to assume actual/expected. (#23 | testing-framework, tests |
| 2020-04-02 | [a825b60a](https://github.com/canonical/operator/commit/a825b60a6e73211bb09d2a2500e86fb9fc63b20e) | medium | source-fix, test-fix | Test event marshalling, and improved its error message. Fixes #194. (# | framework, tests |
| 2020-02-29 | [67254df6](https://github.com/canonical/operator/commit/67254df6458e78e53f0f85ce80c1af3d7cff3205) | medium | source-fix, test-fix | Fixes for the test suite on Mac OSX. (#147) | model, tests |
| 2020-02-10 | [45f5ffe8](https://github.com/canonical/operator/commit/45f5ffe8875b7f3b54d420f419c1ff9fb83aed52) | medium | source-fix, test-fix | Fix .app population for single-unit peer relations (#107) | model, relations, tests |
| 2020-01-17 | [740e09cf](https://github.com/canonical/operator/commit/740e09cfffde370d6ba26197505ddd81d28e7a7a) | medium | source-fix, test-fix | Cache EventsBase and BoundEvent instances to prevent error (#99) | framework, tests |
| 2019-12-19 | [eaf5ebe7](https://github.com/canonical/operator/commit/eaf5ebe7e8aa61457c0bd2a8a217a78316f6f337) | low | source-fix | Fix ResourceMeta for oci-image type resources (#93) | charm, ci |
| 2019-12-11 | [82d570e8](https://github.com/canonical/operator/commit/82d570e80faa14e9f8c586c58507b34283acba96) | medium | test-fix | Storage tests: add a missing test_ method prefix (#80) | storage, tests |
| 2019-12-05 | [4fc4cfdb](https://github.com/canonical/operator/commit/4fc4cfdbb91819c2695816e18456dbd33a6cf238) | medium | test-fix | Use TypeError for invalid argument type errors (#68) | tests |
| 2019-12-04 | [710b4e6a](https://github.com/canonical/operator/commit/710b4e6a418e3462c64c72ba82f668799a4b84ac) | low | test-fix | Fix spacing in different files (#65) | ci, framework, tests |
| 2019-11-28 | [e112a25d](https://github.com/canonical/operator/commit/e112a25de54582a7388ab5673d2f44fd0ffdab41) | medium | test-fix | Rework error handling in the model module (#60) | tests |
| 2019-10-01 | [d9428bbd](https://github.com/canonical/operator/commit/d9428bbd33db0c7933fe451297e9653f5f130721) | medium | source-fix | Fix stop event attribute (#1) | general |
