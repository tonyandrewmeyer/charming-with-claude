# airflow-coordinator-k8s

A coordinating charm for the Charmed Airflow ecosystem: it aggregates metadata from core Airflow charms, renders `airflow.cfg`, runs `airflow db migrate` once, manages S3/git connections, and distributes config and secrets to related core charms via Juju secrets. Architecture is clean (single reconciler, no `defer()`, secrets used properly throughout, above-average integration test suite), but the charm has a **confirmed hard crash in production-relevant conditions**: any S3 relation without TLS (MinIO, MicroCeph, plain S3) throws an uncaught `KeyError` and wedges the unit in `error` status indefinitely. There is also a stray `print()` that leaks connection credentials (S3 keys, git PATs) to hook stdout on every reconciliation. A maintainer should fix the S3 `KeyError` first (`connection_manager.py:81`, one-line fix, already tracked as issue #65) and remove the `print()` in `command_executor.py:72` before this charm is used with any non-TLS object storage backend. Everything else — bad config, missing relations, pod kills, junk secrets — recovers cleanly and quickly.

| | |
|---|---|
| Repo | `canonical/airflow-coordinator-k8s-operator` @ `bcf008d` (2026-06-17) |
| Charms | airflow-coordinator-k8s, mock-core-charm |
| Substrate | k8s |
| Deployed | yes — `concierge-k8s-3` (Juju 3.6.25), rev 36 from `3.1/edge`; also attempted `concierge-k8s-4` (Juju 4.0.5), blocked by `postgresql-k8s` Juju-version constraint |
| Reviewed | 2026-07-31 |

## What it does

- **Gathers metadata** from related Airflow core charms (scheduler, API server, triggerer, DAG processor) via the `airflow-coordinator` relation, checking Airflow version and workload image hash consistency.
- **Generates a unified `airflow.cfg`** Jinja2 template merging charm config, core charm metadata, S3/git DAG bundle configs, executor config, and OAuth auth-manager settings.
- **Runs `airflow db migrate`** once against the related PostgreSQL database.
- **Manages Airflow connections** for S3 and git DAG bundles, including TLS CA chain deployment, credential handling, and stale-connection cleanup.
- **Distributes** the rendered config, Kubernetes executor pod spec, webserver config, sensitive data (DB connection string, secret keys, fernet key), and TLS CA chains to core charms via Juju secrets.
- **Validates** config (fernet key, timezone, numeric ranges), relation health, and OAuth provider data.
- No actions are defined.

## Deployment log

All deployments on controller `concierge-k8s-3` (Juju 3.6.25) unless noted.

### Attempt 1 (`rv-airflow-review`) — abandoned, image pull timeout

```
juju deploy airflow-coordinator-k8s --channel 3.1/edge      # rev 36
juju deploy postgresql-k8s --channel 14/stable --trust       # rev 925
juju relate airflow-coordinator-k8s postgresql-k8s
juju add-secret rv-fernet-key "fernet-key=<generated>"
juju grant-secret rv-fernet-key airflow-coordinator-k8s
juju config airflow-coordinator-k8s fernet_key_secret=secret:<id>
# → BlockedStatus("Fernet key secret not valid") — secret not yet granted
# recreated with grant first → charm advanced past fernet check
```
Packed and deployed `mock-core-charm` for the `airflow-api-server` relation. Relations established, postgres active, but the coordinator workload image from `registry.jujucharms.com` was still pulling after >13 minutes. The same-size image from Docker Hub took 5.5 minutes. Model abandoned.

### Attempt 2 (`rv-airflow2`) — fully successful

```
juju add-model rv-airflow2
juju deploy airflow-coordinator-k8s --channel 3.1/edge      # rev 36, 6.9MB .charm
juju deploy postgresql-k8s --channel 14/stable --trust       # rev 925
juju relate airflow-coordinator-k8s postgresql-k8s
juju add-secret rv-fernet-key2 "fernet-key=<generated>"
juju grant-secret rv-fernet-key2 airflow-coordinator-k8s
juju config airflow-coordinator-k8s fernet_key_secret=secret:<id>
# → BlockedStatus("Waiting for airflow database to be created") at 08:20:22
juju deploy ./mock-core-charm_amd64.charm mock-api-server \
  --resource workload-container=ubuntu/airflow:3.1-24.04_edge \
  --config component=api-server
# ... (scheduler, triggerer, dag-processor similarly)
juju relate airflow-coordinator-k8s:airflow-coordinator {mock-api-server,mock-scheduler,mock-triggerer,mock-dag-processor}:airflow-coordinator
juju relate airflow-coordinator-k8s:airflow-api-server mock-api-server:airflow-api-server
# → database created at 08:21:52 → ActiveStatus at 08:23:48
```
Final status: all 6 apps active.

### Attempt 3 (`rv-airflow3`) — scale, kill, S3 crash, relation cycling, teardown

```
juju add-model rv-airflow3
juju deploy airflow-coordinator-k8s --channel 3.1/edge      # rev 36
juju deploy postgresql-k8s --channel 14/stable --trust       # rev 925
juju relate airflow-coordinator-k8s postgresql-k8s
# fernet key secret setup as above
# deployed 4 mock core charms, related airflow-coordinator + airflow-api-server
# → reached Active at 08:43:49 (all 6 apps active)
```

**Scale up**: `juju scale-application airflow-coordinator-k8s 2` — unit 1 started, settled at `unknown/idle`. Leader remained Active. Non-leader ran hooks (`relation-joined`, `relation-changed`, `pebble-check-failed`) but never set status because `_reconcile` returns immediately for non-leader without setting status.

**Kill pebble in container**: `kubectl exec ... -- kill -9 1` — pod restarted, charm recovered to Active in ~10s. `pebble-checks-failed` fired, hook retried, container came back, reconciliation passed.

**S3 crash test**: Deployed `s3-integrator` (rev 601, 1/edge), configured bucket + endpoint + credentials (no TLS), related to coordinator. Charm crashed: `ErrorStatus: hook failed: "s3-relation-changed"`. Traceback confirmed path: `s3-relation-changed → _reconcile → _perform_checks → _perform_dag_bundle_connection_checks → s3_relation_connections → S3ConnectionInfo.from_s3_info → connection_manager.py:81 KeyError: 'tls_ca_chain'`. Removing the S3 relation left the charm in error state; required `juju resolved --no-retry` to recover. Charm then returned to Active.

**Relation removal/re-add**: Removed `airflow-api-server` relation → `BlockedStatus("Waiting for airflow_api_server interface integration")`, core charms reported validation failures. Re-adding the relation → Active in ~10s.

**Teardown**: Removed the coordinator application; it cleaned up cleanly. Mock core charms went to `ErrorStatus` on `relation-departed` — a `mock-core-charm` defect, not the coordinator's.

### Attempt 4 (`rv-airflow-deep`) — git integration success, S3 crash confirmed with traceback

```
juju add-model rv-airflow-deep (pre-existing from earlier review session)
# Coordinator + postgresql + 4 mock core charms already active
```

Full S3 traceback captured:
```
  File "/var/lib/juju/agents/unit-airflow-coordinator-k8s-0/charm/src/charm.py", line 590, in _reconcile
  File "/var/lib/juju/agents/unit-airflow-coordinator-k8s-0/charm/src/charm.py", line 513, in _perform_checks
  File "/var/lib/juju/agents/unit-airflow-coordinator-k8s-0/charm/src/charm.py", line 409, in _perform_dag_bundle_connection_checks
  File "/var/lib/juju/agents/unit-airflow-coordinator-k8s-0/charm/src/charm.py", line 264, in s3_relation_connections
  File "/var/lib/juju/agents/unit-airflow-coordinator-k8s-0/charm/src/connection_manager.py", line 81, in from_s3_info
    if isinstance(normalized_data["tls_ca_chain"], str):
KeyError: 'tls_ca_chain'
```
Recovery: `juju resolved --no-retry`, then removed S3 relation (`--force`).

**Git integration success**: Deployed `git-integrator` (rev 5, 1.0/edge), configured `repository_url`, related to coordinator. Coordinator remained Active. Debug-log:
```
unit-airflow-coordinator-k8s/0: git:12: Successfully wrote Airflow config
unit-airflow-coordinator-k8s/0: git:12: Adding `git_default` Airflow connection
```
No authentication was configured on git-integrator, so `git_default` was added with the repository URL only, no credentials.

**S3 TLS attempt**: Deployed `self-signed-certificates` and tried to configure TLS on `s3-integrator`. `s3-integrator` has no `certificates` consumer endpoint, so the two charms could not be related. Setting `tls-ca-chain` config directly on `s3-integrator` instead crashed `s3-integrator` itself (`ErrorStatus: hook failed: "config-changed"`). Relation data from a non-TLS S3 relation never contains `tls-ca-chain`.

### Juju 4.x attempt (`rv-airflow-juju4`) — blocked by postgresql-k8s

```
juju add-model rv-airflow-juju4 (controller concierge-k8s-4, Juju 4.0.5)
juju deploy airflow-coordinator-k8s --channel 3.1/edge      # rev 36 — OK
juju deploy postgresql-k8s --channel 14/stable --trust       # FAILED
# → ERROR: charm requires Juju version < 4.0.0, model has version 4.0.5
```
Tried `14/edge` and `16/stable` — same result; `postgresql-k8s` does not support Juju 4.x. The coordinator itself deployed and passed fernet-key validation correctly but could not advance past "Missing integration with postgres".

## Observed behaviour

### Timings
- Coordinator charm size: 6.9 MB (charmcraft pack, amd64)
- Charm download: ~3s from charmhub on Juju 3.6
- `postgresql-k8s` → Active: ~90s
- Coordinator → Active (all relations): ~3.5 minutes from deploy, ~90s from database creation
- Image pull (coordinator rock, `registry.jujucharms.com`): >13 minutes, never completed (attempt 1)
- Image pull (mock-core-charm, Docker Hub, ~750MB): 5m31s
- Config change → Active: ~3s (config-changed + 4 relation-changed hooks to core charms)
- Kill pebble → Active recovery: ~10s
- Relation re-add → Active recovery: ~10s
- S3 crash → stuck in error: indefinite (hook retried every ~5s, never self-recovered; required `juju resolved --no-retry` even after relation removal)

### Resource usage at steady state
```
airflow-coordinator-k8s-0    407m CPU   125Mi memory
mock-api-server-0            121m CPU   72Mi  memory
mock-dag-processor-0          59m CPU   34Mi  memory
mock-scheduler-0              56m CPU   74Mi  memory
mock-triggerer-0              61m CPU   46Mi  memory
postgresql-k8s-0                4m CPU   326Mi memory
modeloperator                  27m CPU   54Mi  memory
```

### Pebble state (verified in rv-airflow3, leader unit)
```
Service  Startup   Current   Since
airflow  disabled  inactive  -
```
Check `airflow-running` is overridden to `/bin/true` (always alive). The rock's base layer (`001-rockcraft-airflow.yaml`) defines `airflow standalone` with `override: replace`. The charm's layer uses `override: merge, startup: disabled`, disabling that service. Only pebble runs in the container (`ps aux` confirms). Non-leader units may have unconfigured pebble layers — see finding on scale-up, and open question below.

### Generated airflow.cfg content
Written to `/opt/airflow/airflow.cfg` in the workload container. Contains `[core]`, `[database]` (with connection string), `[api]`, `[api_auth]`, `[scheduler]`, `[dag_processor]`, `[triggerer]`. `[database]` includes the full PostgreSQL connection string, guarded by `{% if render_sensitive_data %}`. Sensitive values (fernet key, secret keys, JWT secret, DB credentials) are rendered locally and distributed to core charms via a separate Juju secret, not embedded in the shared template.

### Hook count per trivial config change
Setting `core_max_active_runs_per_dag` from 16→32 fired 10 hook events: 1 `config-changed` + 4 `relation-changed` on the coordinator (one per core charm) + 4 `secret-remove` events + 1 `relation-changed` on each core charm. `_reconcile` ran once per event but only re-renders and redistributes config; no redundant restart since the airflow service is disabled.

### Non-leader behaviour at scale 2
Unit 1 (non-leader) ran 6 hooks: `coordinator-peers-relation-joined`, `coordinator-peers-relation-changed`, `postgres-relation-changed`, `airflow-api-server-relation-changed`, `airflow-coordinator-pebble-check-failed`, and others. `_reconcile` returned immediately at `if not self.unit.is_leader(): return` without setting status. Unit 1 remained `unknown/idle` indefinitely; the leader stayed `active/idle`.

### Git relation behaviour
`git-integrator` related with only `repository_url` (no auth) → coordinator logged "Adding `git_default` Airflow connection" and stayed Active. The connection is created with repo URL only, no credentials — the unauthenticated branch of `create_or_update_git_connections()` works correctly.

### Failure injection results

| Injection | Result | Recovery |
|---|---|---|
| `core_default_timezone="Not/A/Real/Timezone"` | `BlockedStatus("Invalid value for core_default_timezone config")` | Reverted config → Active |
| `core_parallelism=-1` | `BlockedStatus("Invalid value for core_parallelism config")` | Reverted config → Active |
| Remove postgres relation | `BlockedStatus("Missing integration with postgres")` | Re-relate → Active (25s) |
| Remove airflow-api-server relation | `BlockedStatus("Waiting for airflow_api_server interface integration")` | Re-relate → Active (10s) |
| Delete pod (forced restart) | New pod started, charm regained Active | ~15s |
| Kill pebble process in container (`kill -9 1`) | Pod restarted, charm regained Active | ~10s |
| Junk fernet key in secret | `BlockedStatus("Fernet key secret not valid")` | Switched back → Active |
| S3 relation without TLS | **`ErrorStatus` — `KeyError: 'tls_ca_chain'` in `connection_manager.py:81`** — retried indefinitely | Only recovered after `juju resolved --no-retry` + force-remove S3 relation |
| S3 relation broken while in error | Charm remained in error, hook still retried; `relation-departed`/`relation-broken` ran but did not clear the error | Required `juju resolved --no-retry` |
| Git relation (unauthenticated) | `ActiveStatus` — "Adding `git_default` Airflow connection" | N/A — succeeded first try |
| `s3-integrator` with `tls-ca-chain` config set | `s3-integrator` crashed with `ErrorStatus: hook failed: "config-changed"` — upstream charm defect, not coordinator's | N/A |

The S3 crash is the only failure that takes the charm to error state rather than a graceful `BlockedStatus`. All config/relation failures produce clear, actionable status messages.

## Findings

### 1. S3 TLS CA chain `KeyError` crash — confirmed in three live deploys, open issue #65
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/connection_manager.py:81`
- **Evidence**: `if isinstance(normalized_data["tls_ca_chain"], str):` where `normalized_data = {key.replace("-", "_"): value for key, value in data.items()}`. Any non-TLS S3 relation (MinIO, MicroCeph, plain S3) omits `tls-ca-chain`, so the key access raises `KeyError`. `S3ConnectionInfo` declares `tls_ca_chain: list[str] = Field(default_factory=list)`, but the crash happens before that default is ever consulted. Live traceback (rv-airflow-deep): `_reconcile → _perform_checks → _perform_dag_bundle_connection_checks → s3_relation_connections → S3ConnectionInfo.from_s3_info → connection_manager.py:81`.
- **Impact**: `_reconcile`'s except clauses catch only `ExceptionWithStatusError`, `WebserverConfigError`, `CommandExecutionError` — `KeyError` is not one of them, so it escapes to the framework and marks the unit `error`. The hook retries every ~5s indefinitely, blocking config distribution to all core charms. Even removing the S3 relation does not clear the error; `juju resolved --no-retry` is required.
- **Fix**: `normalized_data.get("tls_ca_chain")` (or `"tls_ca_chain" in normalized_data`) on line 81; the pydantic default handles the absent case.
- **Linter rule**: flag `dict_literal["key"]` where `dict_literal` is built by a comprehension from external/relation data without a `.get()` guard.

### 2. Stray `print(stdout)` leaks sensitive command output to hook stdout
- **Severity**: high
- **Kind**: bug / security
- **Where**: `src/command_executor.py:72`
- **Evidence**: `print(stdout)` in the `execute_pebble_exec_process` decorator, after `process.wait_output()`. Every Airflow CLI invocation — including `airflow connections list --output json` — prints its stdout. Connection-list output includes `password`/`login` fields for S3 and git connections. `list_airflow_connections()` is invoked via the `airflow_connections` cached property, accessed on every reconciliation by `delete_stale_connections`, `create_or_update_s3_connections`, and `create_or_update_git_connections`.
- **Impact**: S3 keys, git PATs, and other connection credentials get written to hook stdout, which in Juju 3.x may end up captured in debug-log/agent log storage — readable by anyone with model `read` access. Introduced in commit `93135ef` (2026-04-14), "Add relation with s3 interface". (Note: in this review's git-only test with no credentials configured, nothing sensitive was actually visible in `juju debug-log --replay`; whether/at what log level authenticated credentials surface was not directly verified — unverified.)
- **Fix**: delete line 72; use `logger.debug(stdout)` if needed.
- **Linter rule**: flag bare `print()` calls in library/production modules.

### 3. Database name collision between multiple coordinators (open issue #42)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:64`
- **Evidence**: `database_name=f"{self.app.name}_{self.model.uuid}".replace("-", "_")[:63]` — derived only from app name and model UUID.
- **Impact**: Two coordinators in different models sharing one PostgreSQL cluster would request the same database name.
- **Fix**: Add a `database_name` config option, defaulting to the current formula.
- **Linter rule**: not mechanically checkable.

### 4. No coordinated DB migration on upgrade (open issue #47)
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/charm.py:596-600`, `src/templates/airflow_config.j2:6`
- **Evidence**: template sets `check_migrations = False`; `_run_db_migrate()` is gated by `if not self._db_migration_ran:`, keyed off peer relation data, so `airflow db migrate` runs exactly once. A TODO at `charm.py:596-597` acknowledges the gap.
- **Impact**: Airflow version upgrades that require schema migrations will not trigger a re-migration, risking stale schema.
- **Fix**: Track Airflow version in peer data; re-trigger migration on version change.
- **Linter rule**: not mechanically checkable.

### 5. Unit test gap: `from_s3_info` `KeyError` path not exercised
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_connection_manager.py`, `tests/unit/conftest.py` (`S3_INTEGRATOR_DATA`)
- **Evidence**: all S3 fixtures include `"tls-ca-chain": '["test-ca-chain1","test-ca-chain2"]'`; no fixture omits the key.
- **Impact**: this test gap is directly why the critical live crash shipped — a fixture without `tls-ca-chain` would have caught it before release.
- **Fix**: add a fixture lacking `tls-ca-chain` and assert `from_s3_info` returns an empty `tls_ca_chain` list.
- **Linter rule**: not mechanically checkable.

### 6. S3 crash is not caught by any exception handler in `_reconcile`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:619-633`
- **Evidence**: `_reconcile`'s try/except catches only `ExceptionWithStatusError`, `WebserverConfigError`, `CommandExecutionError` — no catch-all for `Exception`.
- **Impact**: any future unanticipated exception (not just the S3 `KeyError`) will bypass the charm's status machinery and land the unit directly in `error`, with indefinite hook retries, instead of a recoverable `BlockedStatus`.
- **Fix**: add `except Exception as e: logger.exception(...); self.unit.status = ops.BlockedStatus(f"Internal error: {e}")` after the existing clauses.
- **Linter rule**: flag hook handlers with specific except clauses but no catch-all `Exception` guard.

### 7. Fernet key secret label collision on secret switch
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/charm.py:222-224`
- **Evidence**: `self.model.get_secret(id=..., label=constants.FERNET_KEY)` — switching the fernet key config to a different secret triggers `ModelError: secret label "fernet-key" for consumer "unit-..." already exists` because the old label is still registered. Caught generically and reported as `BlockedStatus("Fernet key secret not valid")`.
- **Impact**: operator rotating the fernet key sees a message indistinguishable from "invalid secret" and has no clue the fix is a label conflict.
- **Fix**: distinguish label-collision errors and report a more specific message.
- **Linter rule**: not mechanically checkable.

### 8. Non-leader units never set status (confirmed live at scale 2)
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:617-618`
- **Evidence**: `if not self.unit.is_leader(): return` — confirmed live: unit 1 stayed `unknown/idle` with no message while leader was `active/idle`. Non-leader ran ~6 hooks (including `pebble-check-failed`) but none set status.
- **Impact**: operators see leader Active but non-leaders in `unknown` state with no explanation — looks broken even when it isn't.
- **Fix**: set `ops.ActiveStatus("non-leader unit")` (or similar) in the non-leader branch.
- **Linter rule**: flag non-leader branches of hook handlers that don't set unit status.

### 9. `_api_server_base_url` accessed as private attribute from a different module
- **Severity**: low
- **Kind**: bug
- **Where**: `src/webserver_config_generator.py:111`
- **Evidence**: `api_base_url = self._charm._config_generator._api_server_base_url` — underscore-prefixed property accessed cross-module.
- **Impact**: low today; a future refactor of `AirflowConfigGenerator` would silently break `WebserverConfigGenerator`.
- **Fix**: make the property public or expose it on the charm.
- **Linter rule**: flag access to underscore-prefixed attributes from a different module.

### 10. `RawConfigParser` silently corrupts Jinja2 condition-wrapped options
- **Severity**: low
- **Kind**: bug
- **Where**: `src/config_generator.py:82-95`
- **Evidence**: code comment explains `RawConfigParser` treats `{% if x %}key = val{% endif %}` as an option literally named that string; overriding via `extra_config` would add a duplicate rather than replace. "Acceptable today because no collision exists" — fragile.
- **Fix**: add a runtime assertion/warning when an `extra_config` key collides with a condition-wrapped option name.
- **Linter rule**: not mechanically checkable.

### 11. Juju 4.x deployment blocked by `postgresql-k8s` incompatibility
- **Severity**: low (ecosystem finding, not this charm's defect)
- **Kind**: ux
- **Where**: deployment dependency
- **Evidence**: `postgresql-k8s` channels `14/stable`, `14/edge`, `16/stable` all declare `juju_version < 4.0.0`. The coordinator itself deployed correctly on Juju 4.0.5 and passed fernet-key validation.
- **Impact**: teams on Juju 4.x cannot fully deploy this charm until `postgresql-k8s` supports it.
- **Fix**: none needed on this charm; tracked as an ecosystem dependency.
- **Linter rule**: not applicable.

### 12. Mock core charms error on coordinator `relation-departed`
- **Severity**: low (test infrastructure, not the coordinator)
- **Kind**: bug (test infra)
- **Where**: `tests/integration/mock-core-charm/src/charm.py`
- **Evidence**: removing the coordinator application sent all four mock core charms to `ErrorStatus: hook failed: "airflow-coordinator-relation-departed"`. The coordinator's own teardown was clean.
- **Impact**: automated tests that tear down the coordinator may show spurious errors from the mocks.
- **Fix**: fix the mock charm's `relation-departed` handler.
- **Linter rule**: not applicable.

### 13. `AirflowCoordinatorCoreRequires` hardcodes Airflow version
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/airflow_coordinator_k8s/v0/airflow_coordinator.py:885-886`
- **Evidence**: `airflow_version = "3.1.0"` and `workload_image_hash = "somehash"` hardcoded, with a TODO referencing an upstream rock issue (#13).
- **Impact**: version/image-hash consistency checks across core charms are effectively disabled since every charm using the library reports the same hardcoded values.
- **Fix**: resolve the upstream rock issue and read real values from the container.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Clean reconciler pattern, no `defer()`**: `src/charm.py:617-670` — entire charm logic funneled through a single `_reconcile()`. Canonical sidecar pattern.
- **`ExceptionWithStatusError` for flow control**: `src/charm.py:35-46` — custom exception carrying message + `StatusBase`; early exit via `raise ExceptionWithStatusError(...)` without a catch-then-status antipattern.
- **Juju secrets used throughout**: internally generated keys via `app.add_secret()`, user-provided fernet key via `model.get_secret()`; sensitive data to core charms goes through the `data_interfaces` secret abstraction, never plaintext relation databags.
- **Structured status precedence**: config → container connectivity → database → OAuth → API server → core components → version/hash consistency → DAG bundle connections, first failure wins, no later overwrite.
- **Thorough integration test assertions**: `tests/integration/test_charm.py` verifies identical config across core charms, correct base_url, sensitive value types/lengths, key persistence across relation cycles, and validation failures post relation-removal — above-average for the ecosystem.
- **`functools.cached_property` with explicit `refresh()`**: `src/connection_manager.py:104-110` — cached `airflow_connections`, invalidated explicitly after mutation, cleaner than dirty-flag approaches.
- **`@execute_pebble_exec_process` decorator**: `src/command_executor.py:37-98` — standardized Pebble execution with `can_connect()` guard, structured result type, JSON parsing, consistent errors (marred only by the `print()` at line 72).
- **`config_template_with_extra_config` pattern**: `src/config_generator.py:66-95` — merges extra config into the Jinja2 template via `RawConfigParser` without string manipulation; the documented caveat shows awareness of the limitation.
- **Good recovery from most injected failures**: bad config, missing relations, pod restart, kill-pebble, junk secrets all recover cleanly within 5–25s. Only the S3 crash requires manual intervention.

## Common-practice notes

- Modern `charmcraft.yaml` with no separate `metadata.yaml`.
- `uv` plugin (`parts.charm.plugin: uv`, `build-snaps: [astral-uv]`) — early adopter.
- `ops.testing` scenario tests (`Context`/`State`) rather than the older `Harness` pattern.
- Conventional `src/` layout: `charm.py` entry plus config/connection/command/webserver modules.
- Library `airflow_coordinator.py` at LIBPATCH 8, 1264 lines, actively maintained with thorough docstrings.
- Terraform module present, updated for the OAuth endpoint in `bcf008d`.
- Drift: database name is a hardcoded formula rather than a config option, unlike most data-platform charms.
- Drift: two requirer variants (`AirflowCoordinatorRequires`, `AirflowCoordinatorCoreRequires`) in one library file — documented but unusual.
- No actions defined, where many coordinating charms expose at least `pre-upgrade-check` or `restart`.
- `ops>=3,<4` pin in `pyproject.toml`, reasonable for a Juju 3.6 charm.
- Deprecated API usage in dependencies: `data_interfaces` and `object_storage` use `JujuVersion.from_environ()` (103 warnings in unit tests) — not this charm's fault, but worth tracking.
- No catch-all guard in `_reconcile`'s try/except — a deliberate "fail hard" choice, but the S3 crash shows it produces a worse operator experience for a known-possible input (see finding #6).

## Tests

**Unit tests**: 136 passed, 0 failed, 87% coverage. `tox -e unit`, 2.83s. Uses `ops.testing` scenario framework.

Coverage gaps:
- `src/webserver_config_generator.py`: 83% — lines 49-50, 105-109, 113-114, 145-147 (missing provider fields, empty api_base_url, template errors)
- `src/charm.py`: 88% — lines 111, 160, 190-202 (exception handlers), 315-336 (`_perform_dag_bundle_connection_checks` error paths), 365 (executor-config JSON decode), 450, 518, 579-580, 626-632
- `src/connection_manager.py`: 89% — lines 45, 84-85, 139-140, 155, 177-181 (`has_connection_for_git_changed` branches), 207, 237, 275. Line 81 (the crash site) is covered only with data that includes `tls-ca-chain` — the missing-key path is not exercised.
- `src/command_executor.py`: 94% — lines 53, 213-218
- `lib/charms/airflow_coordinator_k8s/v0/airflow_coordinator.py`: 81% — `can_write_*`/`write_*`/`webserver_config_*` methods mostly untested at unit level; `AirflowCoordinatorCoreRequires` (~400 lines) exercised only via `mock-core-charm` in integration.

**Integration tests**: `tests/integration/test_charm.py`, 6 Jubilant-based tests — deploy, relate+validate config consistency, remove/recreate all integrations, remove/recreate limited integrations, break/recreate postgres, verify keys persist across relation cycles. Not run during this review (require 6 apps, ~2GB memory), but assertions are well-structured and above-average for the ecosystem.

**Lint**: `ruff check` passes, `codespell` passes. `pyright` reports 47 errors, all false positives from attribute access on `ops.CharmBase` subclasses without explicit annotation. 103 deprecation warnings from `data_interfaces`/`object_storage` using `JujuVersion.from_environ()`.

## Docs

- `README.md`: 99 bytes, one sentence ("A Charmed Operator for coordinating Charmed Airflow operators."). No deployment instructions, relation guidance, config docs, or architecture overview — the single biggest documentation gap.
- `CONTRIBUTING.md`: standard tox workflow, adequate.
- `SECURITY.md`: 2261 bytes, comprehensive SSDLC policy.
- `terraform/README.md`: 2365 bytes, well-written.
- Charmhub description: minimal two-sentence summary, no doc links.
- Doc/reality mismatch: `charmcraft.yaml` description claims the charm "orchestrates pre-flight checks", but it does not run `airflow test-connection` for S3/git connections (open issue #46) — aspirational claim.

## Open questions

1. Does the `object_storage` typed `S3Info` interface mask the missing key? The live crash confirms the current library returns dicts without `tls-ca-chain` for non-TLS connections; the fix belongs in `connection_manager.py:81`, not the library.
2. Did `airflow db migrate` actually succeed? The charm reached `ActiveStatus`, implying success, but the real migration output was not directly inspected, and integration tests mock `_run_db_migrate` rather than verify it.
3. Does the non-leader unit's pebble layer get configured? `_configure_pebble_layer` runs after the leader guard in `_reconcile`, so non-leaders may never apply the "airflow disabled" layer — if the rock's default layer starts `airflow standalone`, non-leader pods might run an unintended Airflow process. Not verified (would require `kubectl exec` into the non-leader container).
4. Could the git-integrator relation leak credentials via the `print(stdout)` bug? Not directly observed in this review's unauthenticated git test since there were no credentials to leak; behavior with authenticated git/S3 connections and the exact log-capture level in Juju 3.6 needs separate verification (unverified).
5. Are there races between `_reconcile` and `secret-removed` events? The 10-hook cascade on a trivial config change includes 4 `secret-remove` events; `_reconcile` re-evaluates full state on each, so no race was observed, but the hook count is high — inherent to the secret-driven design, not treated as a defect.
