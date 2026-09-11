# temporal-admin-k8s

A small Kubernetes sidecar charm that provides Temporal admin tools (tctl-style CLI, schema setup) to a Temporal server deployment. The code is compact (~250 lines), uses modern `ops.testing` (Scenario) for unit tests, and follows current ops idioms with a custom relation-data library. However, it has a critical leadership bug that makes scaling beyond 1 unit impossible: both `_on_admin_relation_changed` and `_on_admin_relation_broken` write to peer relation app data without a leadership guard, crashing non-leader units and deadlocking scale-down (`juju remove-unit --force` is unavailable on k8s, so the only escape is `remove-application --force`, which destroys the whole app). There's also a wrong `--address` flag placement in the CLI action that produces misleading errors, and the `setup-schema` action can complete "successfully" with no results when database connections aren't available. Test coverage is thin (56% line coverage, 3 scenario tests, all happy-path) and does not catch either bug. **Priority fix**: add `if not self.model.unit.is_leader(): return` to both admin-relation handlers before any peer-data write.

| | |
|---|---|
| Repo | canonical/temporal-admin-k8s-operator @ `82b0b1e` (2026-04-30) |
| Charms | temporal-admin-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25): full stack deploy, 1.23/stable rev 28, refreshed to 1.31/edge rev 30; concierge-k8s-4 (Juju 4.0.5): standalone deploy only (postgresql-k8s has no Juju 4.x-compatible channel) |
| Reviewed | 2026-07-27 |

## What it does

- **Actions**: `cli` (run arbitrary tctl-style commands against the Temporal server), `setup-schema` (initialize PostgreSQL database schemas)
- **Relations**:
  - `admin` (interface: temporal, limit: 4) — receives database connection info from the temporal-k8s server charm, reports schema readiness back
  - `temporal-host-info` (interface: temporal-host-info, limit: 1) — receives Temporal server host/port for CLI commands
  - `peer` — stores charm state (database connections, schema readiness flag) as JSON in peer relation app data
- **Config**: `log-level` (unused — dead option), `server-name` (deprecated fallback for server address when the `temporal-host-info` relation is absent)
- **Workload**: `ubuntu/temporal-server` OCI image, used only via `container.exec()` for `temporal` CLI / `temporal-sql-tool`; no Pebble layers or long-running workload process added by the charm.

## Deployment log

### Juju 3.6.25 (concierge-k8s-3)

```bash
juju deploy temporal-k8s --channel 1.23/edge --config num-history-shards=1
juju deploy temporal-admin-k8s --channel 1.23/stable    # revision 28 on ubuntu@24.04
juju deploy postgresql-k8s --channel 14/stable --trust
# ...integrate all relations...
# → admin charm active in ~45s; server charm briefly "schema not ready" then active
```

Note: `juju info temporal-admin-k8s` listed `1.23/stable` as revision 27 on `ubuntu@22.04`, but `juju deploy` actually pulled revision 28 on `ubuntu@24.04` — a channel metadata inconsistency.

Refresh test:

```bash
juju refresh temporal-admin-k8s --channel 1.31/edge     # revision 28 → 30
# → charm entered maintenance, pod recreated (new IP), active after ~5 minutes total
# PodInitializing phase: ~2.5 min. Workload version stayed at 1.23.1 after refresh (hardcoded bug).
```

### Juju 4.0.5 (concierge-k8s-4)

```bash
juju deploy temporal-admin-k8s --channel 1.23/stable    # revision 28
# → blocked: "admin:temporal relation: database connections info not available"
```

Charm deploys and runs correctly on Juju 4.x. Full stack could not be tested — postgresql-k8s has no Juju 4.x-compatible channel (16/stable requires Juju < 4.0 per its `assumes` block).

- **Deploy to active**: ~45s (Juju 3.6, full stack)
- **Deploy to blocked**: ~15s (Juju 4.x standalone)
- **Memory**: 32Mi (pod), very lightweight — only Pebble runs in the container, no persistent workload
- **Workload version reported**: 1.23.1 (hardcoded `WORKLOAD_VERSION` constant)

### Actions tested

```bash
juju run temporal-admin-k8s/0 cli args="operator namespace list"
# → success, output includes temporal-system namespace

juju run temporal-admin-k8s/0 cli args="operator namespace --namespace charm-review-test create"
# → "Namespace charm-review-test successfully registered."

juju run temporal-admin-k8s/0 setup-schema     # with admin relation
# → completed, return-code: 0

juju run temporal-admin-k8s/0 setup-schema     # without admin relation, Juju 4.x
# → completed with no results — action handler does not report failure
```

### Failure injection (spanning both deploys)

1. Remove `temporal-host-info` relation, no `server-name` config: CLI action fails with clear message ✅
2. Set `server-name` config, no relation: CLI action succeeds via deprecated fallback (port 7236) ✅
3. Remove `admin` relation: charm goes `blocked` with clear message ✅
4. Re-add `admin` relation: charm recovers to `active` ✅
5. Config change (`log-level`): config-changed hook fires, no handler, no crash, no effect ✅
6. Empty CLI args: `args=""` → `Error: unknown flag: --address` at top level ❌
7. Invalid CLI subcommand: `args="nonexistent command"` → same misleading `--address` error ❌
8. Bad `server-name` config (localhost, no server): `"connection refused"` — technically correct ⚠️
9. Delete pod (Juju 3.6): recovers to `active` within ~10s ✅
10. Delete pod (Juju 4.x): recovers to `blocked` within ~15s ✅
11. Scale up 1→2 on rev 28 (1.23/stable): unit 1 enters `error` — `RelationDataAccessError` ❌
12. Scale up 1→2 on rev 30 (1.31/edge): same crash, bug persists in latest code ❌
13. Scale down 2→1: deadlock — error unit stuck, hooks retry `admin-relation-changed`, broken handler never reached, scale shows 2/1 indefinitely, `juju resolve` just retriggers the same error ❌
14. Remove application with `--force`: succeeds — bypasses the error unit and removes everything ✅ (requires operator knowledge of the flag)
15. User passes their own `--address` in CLI args: charm prepends its own `--address`, resulting in duplicate flags; the user's flag wins — confusing but doesn't crash ⚠️
16. Setup-schema action without DB connections (standalone deploy): completes with no results — silent success ❌ (confirmed on both Juju 3.6 and 4.x)
17. Manual peer relation corruption (hypothetical, not tested live — risk assessed from code): if `database_connections` is invalid JSON, `json.loads()` in `State.__getattr__` would raise `JSONDecodeError` on every state access, cascading across all hooks that touch state ❌ (unverified)
18. Kill pebble process (Juju 3.6): pod restarts (1 restart in ~9s), charm recovers to `active` ✅ — confirmed via `kubectl exec ... -- pkill pebble`
19. Kill pebble process (Juju 4.x): pod restarts, charm recovers to `blocked` within ~10s ✅
20. `juju resolve` on stuck error unit: retriggers `admin-relation-changed`, crashes again with `RelationDataAccessError`; `admin-relation-broken` never dequeues because `admin-relation-changed` is ahead of it in the queue ❌

## Observed behaviour

### Container internals

The `ubuntu/temporal-server` OCI image has a built-in Pebble layer with a `temporal-server` service (enabled but inactive — not used by this charm). The charm adds no Pebble layers; it only uses `container.exec()` to run `temporal` and `temporal-sql-tool`. The container runs only Pebble itself. Tools live at `/usr/bin/temporal` and `/usr/bin/temporal-sql-tool`; schema files are under `/etc/temporal/schema/postgresql/v12/` (versioned subdirectories v1.0–v1.11).

### Pebble crash recovery

Killing pebble (`kubectl exec ... -- pkill pebble`) causes a pod restart (1 restart in ~9s on Juju 3.6, similar on Juju 4.x). The charm returns to its previous state (`active` with full stack on Juju 3.6, `blocked` standalone on Juju 4.x) within ~10–15s without operator intervention — clean recovery, no brittle in-memory state.

### Hook sequence (initial deploy)

```
install → peer-relation-created → temporal-host-info-relation-created → admin-relation-created
→ leader-elected → config-changed → start → temporal-admin-pebble-ready (blocked)
→ admin-relation-joined → temporal-host-info-relation-joined → temporal-host-info-relation-changed
→ admin-relation-changed → peer-relation-changed → temporal-host-info-relation-changed
→ temporal-admin-pebble-check-failed → admin-relation-changed (active)
```

`temporal-admin-pebble-check-failed` fires because the image ships a built-in health check for `temporal-server`, which this charm never starts. Harmless but noisy — visible in `kubectl logs` as repeated check failures.

### Config change behaviour

A `config-changed` hook fires on `log-level`/`server-name` changes, but the charm itself does not observe `config_changed` — only the `TemporalHostInfoRequirer` library does (for `external-hostname` on the provider side). No workload restart or re-render occurs. Exactly 1 hook fires per config change.

### Scale-up crash (observed directly)

Scaling 1→2, the non-leader unit (`temporal-admin-k8s/1`) hits `admin-relation-changed` and tries to write `database_connections` to peer relation app data via `State.__setattr__` → `self._get_relation().data[self._app].update(...)`. Non-leader units cannot write app data, raising `ops.model.RelationDataAccessError`. The unit enters `error`.

After `juju resolve`, the unit triggers `admin-relation-broken` (from the prior admin relation), which ALSO crashes — `_on_admin_relation_broken` writes `self._state.database_connections = None` to peer app data, same error.

Scale-down deadlocks: the error unit can't be removed because every hook retry hits the same error, and the broken-handler crash prevents Juju from removing the unit. On k8s models `juju remove-unit --force` is unsupported; the only escape is `juju remove-application --force`, tearing down the entire application including the healthy unit.

Debug-log:
```
unit-temporal-admin-k8s/1: ERROR unit.temporal-admin-k8s/1.juju-log admin:10: Uncaught exception while in charm code:
    ops.model.RelationDataAccessError: temporal-admin-k8s/1 is not leader and cannot write application data.
unit-temporal-admin-k8s/1: ERROR juju.worker.uniter.operation hook "admin-relation-changed" (via hook dispatching script: dispatch) failed: exit status 1
unit-temporal-admin-k8s/1: INFO juju.worker.uniter awaiting error resolution for "relation-changed" hook
```
Retry loop repeats every ~5 seconds indefinitely. Juju's exponential backoff gives up after ~5 minutes on Juju 3.6, leaving the unit in `error` and scale stuck at `2/1`.

### `--address` flag placement (observed directly)

The charm builds `temporal --address host:port <user args>`. This works when `<user args>` starts with a subcommand that accepts `--address` (e.g. `operator`, `workflow`), but fails when args are empty or start with an unrecognised subcommand:

```
$ juju run temporal-admin-k8s/0 cli args=""
Error: unknown flag: --address
Usage:
  temporal [command]
Available Commands:
  activity    Complete, update, pause, unpause, reset or fail an Activity
  ...
  operator    Manage Temporal deployments
  ...
```

Same error for `args="nonexistent command"`. Correct placement is after the subcommand: `temporal operator --address host:port ...`.

### User-supplied `--address` flag

`args="--address 10.0.0.1:7233 operator namespace list"` produces `temporal --address charm-host:7236 --address 10.0.0.1:7233 operator ...`. The Temporal CLI uses the last `--address`, so the user's value silently wins over the charm's resolved address; no warning is logged.

### Juju 4.x specific behaviour

The charm runs identically on Juju 4.0.5 vs 3.6.25. No Juju 4.x-specific issues found. `setup-schema` completes silently (no results, no error) with no database connections on both Juju versions.

### Refresh behaviour (1.23/stable rev 28 → 1.31/edge rev 30)

- Duration: ~5 minutes total (pod recreation + PodInitializing ~2.5 min + charm startup ~2.5 min)
- Pod recreated with new IP (10.1.0.114 → 10.1.0.227)
- Workload version stayed `1.23.1` after refresh — hardcoded `WORKLOAD_VERSION` not updated in rev 30
- CLI and setup-schema actions worked correctly post-refresh
- No status message during refresh — charm shows `maintenance` with no detail

### Container binary versions

```
$ kubectl exec temporal-admin-k8s-0 -c temporal-admin -- temporal --version
temporal version 1.3.0 (Server 1.27.1, UI 2.36.0)
```

The CLI binary reports 1.3.0; the charm reports `WORKLOAD_VERSION = "1.23.1"` (the charm track name, not any real binary version).

## Findings

### 1. Scale-up and scale-down crash non-leader units — admin relation handlers write peer app data without a leadership guard
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:132` (`_on_admin_relation_changed`), `src/charm.py:146` (`_on_admin_relation_broken`); leadership check in `_setup_db_schemas` (`src/charm.py:208`) comes too late
- **Evidence**: `self._state.database_connections = json.loads(database_connections)` writes to peer app data with no leadership check. Same pattern in the broken handler (`self._state.database_connections = None`). Observed: scaling 1→2 units, unit 1 crashed with `RelationDataAccessError: temporal-admin-k8s/1 is not leader and cannot write application data`; resolving retriggers `admin-relation-broken`, which crashes the same way; scale-down then deadlocks.
- **Impact**: Charm cannot scale past 1 unit. Metadata allows up to 4 `admin` relations and the terraform module exposes an unguarded `units` variable, but any non-leader unit crashes on relation-changed/broken. Recovery from a single bad unit requires `juju remove-application --force` (k8s has no `remove-unit --force`), destroying the whole app.
- **Fix**: Add `if not self.model.unit.is_leader(): return` at the top of both handlers (after the existing `is_ready` check), before any state mutation.
- **Linter rule**: "All peer relation app data writes must be guarded by `is_leader()`" — mechanically checkable.

### 2. Unguarded `relation.data[event.app]` access can raise `KeyError`
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:131`
- **Evidence**: `database_connections = event.relation.data[event.app].get("database_connections")` subscripts `event.relation.data[event.app]` without checking membership. The `is_ready()` guard on line 126 only checks the peer relation, not remote app data.
- **Impact**: Race condition — if `admin-relation-changed` fires before the remote app has populated its databag, this raises `KeyError` instead of deferring.
- **Fix**: `(event.relation.data.get(event.app) or {}).get("database_connections")`.
- **Linter rule**: "All `relation.data[app]` subscript accesses must be guarded by `app in relation.data`" — mechanically checkable.

### 3. `--address` flag placed before the subcommand — confusing errors on empty/invalid CLI args
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:176`
- **Evidence**: `args = ["--address", f"{server_name}:{server_port}", *event.params["args"].split()]`. `--address` is only accepted by Temporal subcommands, not the top-level command. Observed: `cli args=""` → `Error: unknown flag: --address`; `cli args="nonexistent command"` → same error.
- **Impact**: Operators with empty args or a typo'd subcommand get an error suggesting `--address` is wrong, obscuring the real problem (no valid subcommand given).
- **Fix**: Insert `--address host:port` after the subcommand token, or validate `args` is non-empty/well-formed before constructing the command.
- **Linter rule**: not mechanically checkable — requires CLI flag semantics.

### 4. `setup-schema` action completes silently when no database connections are available
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:220` (`_setup_db_schemas`), action handler `src/charm.py:193-196`
- **Evidence**: `_setup_db_schemas` returns early with `BlockedStatus` when connections are absent, but `_on_setup_schema_action`'s try/except only catches exceptions, not this early return. Observed: on Juju 4.x standalone, `juju run temporal-admin-k8s/0 setup-schema` → `status: completed`, no results, not even `return-code`. On Juju 3.6 without connections, same silent completion.
- **Impact**: Operator has no way to know whether the schema was actually set up.
- **Fix**: After calling `_setup_db_schemas(event)`, check `self.unit.status`; if it's `BlockedStatus`, call `event.fail(str(self.unit.status.message))`.
- **Linter rule**: "Action handlers must set results or call `event.fail()` on all code paths" — mechanically checkable.

### 5. Broad `except Exception` swallows errors without actionable messages
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:113-114`, `src/charm.py:180-181`, `src/charm.py:195-196`, `src/charm.py:279-281`
- **Evidence**: Four blind catches: line 113 sets `BlockedStatus("error setting up schema. remove relation and try again.")` regardless of actual cause; line 180 does `event.fail(f"command failed: {err}")`; line 195 `event.fail(err)`; lines 279-281 re-raise as a generic `Exception`, losing the original type.
- **Impact**: Operators can't diagnose failures — original error type/traceback discarded. The "remove relation and try again" message is misleading for unrelated errors (network timeout, auth failure, etc.).
- **Fix**: Catch specific types (`json.JSONDecodeError`, `ops.pebble.ConnectionError`, `ops.pebble.ExecError`), log full tracebacks, give actionable status messages.
- **Linter rule**: Ruff `BLE001` already flags this.

### 6. `TemporalHostInfoRequirer` library has the same unguarded `relation.data[app]` access pattern
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/temporal_k8s/v0/temporal_host_info.py:146-147`, `:163-164`
- **Evidence**: `.host`/`.port` properties subscript `relation.data[relation.app]` without checking membership; `_on_host_info_relation_changed` (line 163) does the same on `event.relation.data[event.relation.app]`. The inner `try/except KeyError` only catches the nested key lookup, not the outer subscript.
- **Impact**: Same race condition as finding 2 — if `temporal-host-info-relation-changed` fires before the remote side writes `host`/`port`, the charm tracebacks.
- **Fix**: Use `relation.data.get(relation.app, {})` / `event.relation.data.get(event.relation.app, {})`.
- **Linter rule**: same as finding 2 — mechanically checkable.

### 7. Terraform module exposes `units` variable but charm crashes on scale > 1
- **Severity**: high
- **Kind**: bug
- **Where**: `terraform/variables.tf:10-14`, `src/charm.py:132,146`
- **Evidence**: `var.units` (default 1) is passed straight to `juju_application.temporal_admin_k8s.units` with no validation, while the charm has the scale-up/down bugs in finding 1.
- **Impact**: An operator setting `units = 2` via terraform gets a broken deployment requiring forced pod/app deletion to recover.
- **Fix**: Fix the charm's leadership guard (preferred), or add a terraform `validation` block restricting `units <= 1` until fixed.
- **Linter rule**: not mechanically checkable.

### 8. Terraform README documents `model` input but variables.tf uses `model_uuid`
- **Severity**: high
- **Kind**: docs
- **Where**: `terraform/README.md`, `terraform/variables.tf`
- **Evidence**: README's input table and usage example show `model = juju_model.testing.name`; `terraform/variables.tf` defines a required `model_uuid` string, used in `terraform/main.tf` as `model_uuid = var.model_uuid`.
- **Impact**: Following the README produces a Terraform error about an undeclared `model` variable.
- **Fix**: Update the README to `model_uuid` throughout, or rename the variable to `model`.
- **Linter rule**: "Terraform variable names in README must match variables.tf" — mechanically checkable.

### 9. `log-level` config option is declared but never read by the charm
- **Severity**: medium
- **Kind**: bug
- **Where**: `config.yaml:5-7`
- **Evidence**: `log-level` (string, default `"info"`, "Temporal server logging level") has no reference anywhere in `src/` (only Python `logging.getLogger`). The admin-tools container runs no server process to configure. Observed: `juju config temporal-admin-k8s log-level=debug` fires config-changed with no effect.
- **Impact**: Misleading config option erodes operator trust.
- **Fix**: Implement propagation to the `temporal` CLI's `--log-level` flag, or remove the option.
- **Linter rule**: "All config.yaml options must be referenced in charm source" — mechanically checkable.

### 10. No `config-changed` handler — charm ignores runtime config changes
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:55-77`
- **Evidence**: `__init__` never observes `self.on.config_changed`; only the `TemporalHostInfoRequirer` library observes it, for the provider's `external-hostname`. Changing `server-name` at runtime produces no status update or log message.
- **Impact**: Operators may assume a config change took effect when the charm gave no feedback.
- **Fix**: Add a config-changed handler that at minimum logs new values and updates status if the `server-name` fallback is in use.
- **Linter rule**: "Charms with non-empty config.yaml should observe config-changed" — mechanically checkable.

### 11. JSON parse failure in admin relation data is not caught
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:132`
- **Evidence**: `self._state.database_connections = json.loads(database_connections)` — malformed JSON from the remote side propagates a bare `json.JSONDecodeError`; this call path doesn't go through the broad except in `_on_temporal_admin_pebble_ready`.
- **Impact**: A buggy or manually-edited remote relation databag crashes the admin charm with an uncaught traceback instead of a clean `BlockedStatus`.
- **Fix**: Catch `json.JSONDecodeError` and set `BlockedStatus("admin:temporal relation: invalid database connection data")`.
- **Linter rule**: "Catch `JSONDecodeError` when calling `json.loads` on relation data" — mechanically checkable.

### 12. Hand-rolled `State` class raises unhelpful `AttributeError` when peer relation is absent
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/state.py:44`
- **Evidence**: `self._get_relation().data[self._app].get(name, "null")` raises `AttributeError: 'NoneType' object has no attribute 'data'` if `_get_relation()` returns `None`. `_on_temporal_admin_pebble_ready` (`src/charm.py:107`) reads `self._state.is_initial_schema_ready` before any `is_ready()` check.
- **Impact**: If pebble-ready fires before peer-relation-created, the charm crashes with a cryptic error rather than deferring.
- **Fix**: Guard `__getattr__`/`__setattr__` with `if not self._get_relation(): raise RuntimeError("peer relation not ready")`.
- **Linter rule**: "Custom state storage must guard relation access in `__getattr__`/`__setattr__`" — mechanically checkable.

### 13. WORKLOAD_VERSION hardcoded and confirmed wrong against the actual binary
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:21`
- **Evidence**: `WORKLOAD_VERSION = "1.23.1"`, reported via `set_workload_version`. `kubectl exec ... -- temporal --version` returns `temporal version 1.3.0 (Server 1.27.1, UI 2.36.0)`. After refresh to rev 30 the reported version stayed 1.23.1.
- **Impact**: Fleet-wide version monitoring shows stale/wrong numbers.
- **Fix**: Probe the binary at runtime (`container.exec(["temporal", "--version"])`) and parse the output instead of hardcoding.
- **Linter rule**: "`WORKLOAD_VERSION` constants should be derived from the container, not hardcoded" — not mechanically checkable.

### 14. `_setup_db_schemas` is 9+ branches, complexity-warning suppression is a no-op under ruff
- **Severity**: medium
- **Kind**: lint
- **Where**: `src/charm.py:198`
- **Evidence**: `# flake8: noqa: C901` on the method; ruff reports `RUF100` because it doesn't use flake8's `C901` code, so the suppression currently has no effect. Method mixes leader/peer/container/connection validation, TLS conditional, admin-relations iteration, and per-relation write.
- **Impact**: Hard to unit-test individual paths; the suppression gives false confidence that complexity is handled.
- **Fix**: Extract `_validate_prerequisites()` and `_execute_schema_setup(connection)` into separate methods; drop the stale noqa.
- **Linter rule**: "No `# noqa: C901` on methods" — mechanically checkable.

### 15. `admin` relation `limit: 4` is misleading given the scale-1 constraint
- **Severity**: medium
- **Kind**: ux
- **Where**: `metadata.yaml:28`
- **Evidence**: `provides: admin: interface: temporal, limit: 4`, but the charm can only run 1 unit (finding 1) and the terraform module exposes `units` unguarded. Observed: scaling to 2 units crashes.
- **Impact**: Operators/orchestration tooling reading metadata would assume multi-unit support that doesn't exist.
- **Fix**: Fix leadership guards (preferred), or reduce `limit` to 1 with an explanatory comment.
- **Linter rule**: "Relation `limit > 1` requires scale testing or documented single-unit limitation" — not mechanically checkable.

### 16. Hand-rolled `State` class duplicates `ops` patterns with no consistent readiness guard
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/state.py:1-59`
- **Evidence**: State is stored as JSON strings in peer app data via `__getattr__`/`__setattr__`; `is_ready()` exists but callers don't consistently call it before accessing state. Compounds finding 12 and the non-leader write issue (finding 1).
- **Impact**: Early-lifecycle state access before peer relation exists will crash with an unhelpful `AttributeError`.
- **Fix**: Replace with `ops.StoredState`, or guard all accesses with `is_ready()` and raise a meaningful error otherwise.
- **Linter rule**: same as finding 12 — mechanically checkable.

### 17. Jubilant integration test conftest deploys on `ubuntu@22.04`, charm only supports `ubuntu@24.04`
- **Severity**: medium
- **Kind**: bug
- **Where**: `tests/integration/conftest.py:77`
- **Evidence**: `base="ubuntu@22.04"` in `deploy_temporal_stack`; `charmcraft.yaml` declares `platforms: ubuntu@24.04:amd64`. Test is currently already broken/skipped per issue #57 (closed `latest/stable` channel), so this base mismatch may not have surfaced yet.
- **Impact**: Once #57 is fixed, `test_refresh` will fail on a base mismatch instead of exercising the refresh path.
- **Fix**: Change to `base="ubuntu@24.04"`.
- **Linter rule**: "Charm deploy base in tests must match `charmcraft.yaml` platforms" — mechanically checkable.

### 18. `run_setup_schema_action` test helper doesn't assert on action results
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/helpers.py:46-56`
- **Evidence**: The helper runs the action and logs results but only asserts workload status is `active`; it never checks `result`. The silent-completion bug (finding 4) would pass this test unnoticed.
- **Impact**: False confidence — integration suite can't distinguish "schema set up" from "action silently did nothing".
- **Fix**: Assert on expected result keys or `return-code == 0`.
- **Linter rule**: "Action test helpers must assert on action results, not just charm status" — not mechanically checkable.

### 19. `TemporalHostInfoProvider._resolve_host` returns `""` on failure with only a log warning
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/temporal_k8s/v0/temporal_host_info.py:99-102`
- **Evidence**: When neither `external-hostname` config nor a binding address is available, `_resolve_host` logs a warning and returns `""`, which is then written to relation data as `host=""`.
- **Impact**: Requirer charms build invalid connection URIs; the failure surfaces as a connection error rather than a configuration error.
- **Fix**: Raise or set `BlockedStatus` on the provider instead of returning an empty string.
- **Linter rule**: not mechanically checkable.

### 20. `juju info` channel metadata disagrees with actual `juju deploy` result
- **Severity**: low
- **Kind**: ux
- **Where**: Charmhub channel listing
- **Evidence**: `juju info temporal-admin-k8s` shows `1.23/stable: 27 2026-04-30 (27) ... ubuntu@22.04`; `juju deploy --channel 1.23/stable` actually installs revision 28 on `ubuntu@24.04`.
- **Impact**: Operators checking `juju info` before deploying get inaccurate expectations of base/revision.
- **Fix**: Refresh/correct Charmhub channel metadata.
- **Linter rule**: not mechanically checkable (external service).

### 21. Duplicate `--address` flag when the operator supplies their own
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:176`
- **Evidence**: `args="--address 10.0.0.1:7233 operator namespace list"` → charm builds `["--address", "charm-host:7236", "--address", "10.0.0.1:7233", ...]`; Temporal CLI uses the last value, so the operator's address silently wins. Observed connection went to the user's address.
- **Impact**: Operators who explicitly set `--address` may not realize the charm also injects one, and may be surprised where the connection actually goes.
- **Fix**: Document that `--address` is auto-injected and should be omitted, or detect and skip the automatic one when the user supplies it.
- **Linter rule**: not mechanically checkable.

### 22. `_on_install` sets `MaintenanceStatus` and does nothing else
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:98`
- **Evidence**: The handler's only line is `self.unit.status = MaintenanceStatus("installing temporal admin tools")`. In a k8s sidecar charm the container isn't available at install time, so nothing is actually installed.
- **Impact**: Status is immediately overwritten by the next hook — pure noise.
- **Fix**: Remove the handler or give it real work.
- **Linter rule**: not mechanically checkable.

### 23. `_setup_db_schemas` called from `_on_admin_relation_broken` is semantically wrong
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:148`
- **Evidence**: Called after clearing `database_connections`/`is_initial_schema_ready`; currently safe because `_setup_db_schemas` immediately hits its `BlockedStatus` early return, but calling a "setup" method from a "broken" handler is a logic smell.
- **Impact**: Currently harmless by accident; a future refactor of `_setup_db_schemas` could silently reintroduce a bug here.
- **Fix**: Don't call `_setup_db_schemas` from the broken handler — just clear state.
- **Linter rule**: "Do not call setup/configuration methods from relation-broken handlers" — not mechanically checkable.

### 24. `server-name` config is described as deprecated but not marked `deprecated: true`
- **Severity**: low
- **Kind**: lint
- **Where**: `config.yaml:8-15`
- **Evidence**: Description text is prefixed `[DEPRECATED]`, but there is no `deprecated: true` field.
- **Impact**: `juju config` output and the Charmhub page don't render this as deprecated; no machine-readable signal.
- **Fix**: Add `deprecated: true`.
- **Linter rule**: "Config options with '[DEPRECATED]' in description should have `deprecated: true`" — mechanically checkable.

### 25. Ruff reports 7 issues, including blind exceptions and an unused noqa
- **Severity**: low
- **Kind**: lint
- **Where**: multiple locations
- **Evidence**: `ruff check src/ tests/` → 3× `BLE001` (blind exception), 1× `RUF100` (unused `noqa: C901`), 1× `TRY002` (raise generic Exception), 2× `ASYNC*` in integration tests.
- **Impact**: Mix of real issues (finding 5) and tool-config drift (`RUF100` confirms the complexity suppression from finding 14 is dead).
- **Fix**: Fix `BLE001` violations, remove the stale noqa, refactor the flagged method.
- **Linter rule**: already caught by ruff.

### 26. `setup-schema` action calls `event.defer()` on a non-deferrable `ActionEvent`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:212,217`
- **Evidence**: `_setup_db_schemas` calls `event.defer()` when peer relation or container isn't ready. When invoked from `_on_setup_schema_action`, `event` is an `ActionEvent`, which doesn't support `defer()`.
- **Impact**: If prerequisites aren't ready at action time, the action returns without results and the operator gets no feedback (compounds finding 4).
- **Fix**: Check prerequisites in `_on_setup_schema_action` before calling `_setup_db_schemas`, and call `event.fail(...)` instead of relying on deferral.
- **Linter rule**: "`event.defer()` must not be called from action handlers" — mechanically checkable.

## Worth copying

- **Clean relation library**: `lib/charms/temporal_k8s/v0/temporal_host_info.py` has separate Provider/Requirer classes, proper event emission with snapshot/restore, good docstrings, and a `TooManyRelatedAppsError` guard — a good template for custom relation interfaces (modulo finding 6).
- **Scenario tests**: uses `ops.testing.Context` (Scenario) rather than legacy `Harness`; fixtures (`context`, `temporal_admin_container`, `peer_relation`, `admin_relation`) are clean and composable.
- **UV-based build**: `charmcraft.yaml` uses the `uv` plugin with the `astral-uv` build-snap.
- **Deprecation path with clear messaging**: `server-name` → `temporal-host-info` migration is documented in README, config description, code comments, and action error messages; fallback chain (relation → config → fail) is clean.
- **Compact, focused charm**: ~250 lines, does one job.
- **Startup error handling**: charm goes to `blocked` with a descriptive message rather than crashing or hanging in `waiting` when DB connections aren't available.
- **Recovery from failure**: pod crashes and relation flapping recover cleanly without operator intervention.

## Common-practice notes

- **Follows**: standard ops layout (`src/charm.py`, `lib/`, `tests/scenario/`, `tests/integration/`); UV-based `charmcraft.yaml`; CI uses `canonical/operator-workflows` shared workflows; pinned dependencies in `pyproject.toml` (`ops==2.21.1`, etc.) with separate `charm`/`unit`/`integration`/`lint`/`fmt` extras.
- **Drift**: hand-rolled `State` class (`src/state.py`) instead of `ops.StoredState` — see finding 16.
- **Drift**: integration tests split between `pytest-operator` (`test_charm.py`, `helpers.py`) and `jubilant` (`test_refresh.py`, `conftest.py`); open issue #55 confirms this is known tech debt.
- **Drift**: no `deprecated: true` on the deprecated `server-name` option — see finding 24.
- **Drift**: database connection info (including passwords) passes through relation data as plaintext JSON rather than via `ops` Secrets — standard for cross-charm communication in this ecosystem but means passwords appear in `juju show-unit` output.
- **Drift**: `metadata.yaml` names the resource image `ubuntu/temporal-server` while Charmhub description/README refer to `temporalio/admin-tools` — appear to be the same image under different names (unverified which name is authoritative).

## Tests

### Unit/scenario tests: 3 tests, all pass

```
tests/scenario/test_charm.py::test_missing_admin_relation PASSED
tests/scenario/test_charm.py::test_missing_admin_relation_data PASSED
tests/scenario/test_charm.py::test_ready PASSED
```

Run with `tox -e unit` (3 passed in 0.30s).

Coverage (`tox -e unit` → `coverage report`):

```
Name           Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------
src/charm.py     149     72     60      8    53%   84-88, 97, 108-109, 113-114, 126-133, 142-148, 157-184, 193-196, 209, 212-213, 217-218, 250-251, 275-276, 279-281, 287-289, 313-321, 325
src/state.py      16      1      2      0    94%   58
----------------------------------------------------------
TOTAL            165     73     62      8    56%
```

56% line coverage overall. Untested: `_on_admin_relation_changed` (126-133), `_on_admin_relation_broken` (142-148), `_on_cli_action` (157-184), `_on_setup_schema_action` (193-196), most of `_setup_db_schemas` (209-281).

| Untested path | Risk |
|---|---|
| `_on_admin_relation_changed` on non-leader unit | Hook crash, error state |
| `_on_admin_relation_broken` on non-leader unit | Hook crash + scale-down deadlock |
| `_on_admin_relation_changed` with missing `event.app` in remote data | `KeyError` crash |
| `_on_admin_relation_changed` with malformed JSON | `JSONDecodeError` crash |
| `_on_admin_relation_broken` → `_setup_db_schemas` call path | Logic error |
| `_on_cli_action` with no host-info and no server-name | Error message path |
| `_on_cli_action` with empty args or invalid subcommand | Misleading `--address` error |
| `_on_cli_action` with container not connectable | Action failure path |
| `_on_setup_schema_action` exception path | Action failure path |
| `_on_setup_schema_action` with `database_connections` None | Silent completion (no results) |
| `_setup_db_schemas` with TLS-enabled connections | TLS flag insertion |
| `_setup_db_schemas` with empty `admin_relations` | Race-condition path |
| `_setup_db_schemas` called from action handler | No-op defer |
| Multiple admin relations (limit: 4) | Multi-relation write path |
| Scale-up 1→2 | Non-leader crash (observed) |
| Scale-down 2→1 | Non-leader crash + deadlock (observed) |

`test_ready` mocks `charm.execute` and only asserts call count (4), not arguments — TLS-enabled connections pass through untested.

### Integration tests

- `test_charm.py` (pytest-operator): full stack deploy with temporal-k8s, postgresql-k8s, openfga-k8s; tests CLI action, host-info relation, relation removal fallback, schema setup, OpenFGA auth model, server removal. Asserts real output (CLI strings, status codes), not just idle/active — good. Uses the deprecated `pytest-operator` framework.
- `test_refresh.py` (jubilant): tests refresh from `latest/stable` to `1.23/stable`. Open issue #57 confirms this will fail because `latest/stable` was closed (2026-07-15). The jubilant conftest also deploys on `base="ubuntu@22.04"` against a charm that only supports `ubuntu@24.04` (finding 17).

Neither integration test exercises scale-up — both deploy 1 unit only, so the critical finding-1 crash isn't caught by CI.

### Static analysis

- `ruff check src/ tests/`: 7 issues (finding 25).
- `codespell . --skip .git,.tox,.venv,build,lib,uv.lock,icon.svg,.mypy_cache`: clean.
- `mypy`, `pylint`, `pydocstyle`, `bandit`: listed as tox/lint dependencies but not run in this review (not installed in the review venv).
- `charmcraft analyse`: crashed with `IsADirectoryError` — appears to be a charmcraft tooling issue, not a charm issue (unverified).

## Docs

- **README.md**: brief but functional; links to temporal-k8s for deployment; documents the `server-name` deprecation path. Missing: action documentation, config option documentation, relation details.
- **CONTRIBUTING.md**: standard tox-based workflow, accurate.
- **terraform/README.md**: documents `model` as an input, but the actual variable is `model_uuid` (finding 8) — following the README produces an error.
- **Charmhub description**: one-paragraph, no action/relation documentation on the page itself.
- **Doc/reality match**: `server-name` deprecation path in the README matches observed behaviour. `log-level` is documented as "Temporal server logging level" but has no effect (finding 9).
- **Gap**: a new operator wouldn't learn from the README that they need the `cli` action (rather than a direct `tctl` invocation), or the `args` parameter's space-separated-string format. Charmhub page doesn't list available actions.

## Open questions

1. Why is `WORKLOAD_VERSION` hardcoded to `"1.23.1"` when the container's actual `temporal --version` reports `1.3.0 (Server 1.27.1)`, and why does it stay `1.23.1` even after refreshing to rev 30 (1.31/edge)?
2. Is `log-level` a leftover config option from an earlier version that configured a running Temporal server? The admin-tools container runs no server, so the option makes no sense as-is.
3. Why does the `temporal-admin-image` resource reference `ubuntu/temporal-server` while docs describe `temporalio/admin-tools` — are these confirmed to be the same image under different names?
4. The image's Pebble layer defines a `temporal-server` service the charm never starts, producing repeated `temporal-admin-pebble-check-failed` events — is this image shared with the temporal-k8s charm, and is the health check expected to be ignored?
5. Why does the `admin` relation have `limit: 4` in metadata when the charm can only run 1 unit? A `limit: 1` (with a comment) would be more honest until multi-leader support exists.
6. Is `is_initial_schema_ready` ever reset other than via relation removal? If the database is wiped/recreated without touching the admin relation, would the charm wrongly believe the schema already exists?
7. Is the `juju info` / `juju deploy` channel/revision/base discrepancy (finding 20) a Charmhub caching issue or a misconfigured channel release?

