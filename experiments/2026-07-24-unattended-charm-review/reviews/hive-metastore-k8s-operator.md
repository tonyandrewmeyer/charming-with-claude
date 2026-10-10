# hive-metastore-k8s

A thin, well-structured k8s charm that deploys Apache Hive Metastore 4.2.0 via Pebble, integrating
with PostgreSQL over the `postgresql_client` interface. The reconciliation pattern (single reconciler,
clear status precedence) and the `TypedCharmBase[CharmConfig]` Pydantic config model are good designs,
but the charm is not production-ready: `self.config` is never read, so all six declared config options
are dead code; the published rock image is not reachable from Charmhub (404); and the fallback
`apache/hive` image cannot work with this charm at all (no Pebble, no PostgreSQL JDBC driver). A
crash bug in `_stop_service()` that put units in permanent error state was found and fixed during
this review. A maintainer's first priority should be: (1) get the rock image actually published to
GHCR and fix the `promote_charm.yaml` CI gap, (2) wire `self.config` into the code paths that need it,
(3) add exception handling around the unguarded `schematool.info()` call.

| | |
|---|---|
| Repo | canonical/hive-metastore-k8s-operator @ 127daa0 (2026-01-16) |
| Charms | hive-metastore-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3, local charm rev 1 (fixed), postgresql-k8s/14/stable. The charmhub edge release could not be deployed as-is (image 404); a locally-patched charm was packed and deployed instead. |
| Reviewed | 2026-08-18 |

## What it does

Deploys Apache Hive Metastore 4.2.0 (standalone) on Kubernetes using a Pebble-managed workload
container. Integrates with PostgreSQL via the `postgresql_client` interface, renders `hive-site.xml`
from a Jinja2 template, and runs `schematool -initSchema` on first boot to create the metadata schema.
Five config options control thread pools, JVM args, and K8s resource requests/limits. No other
integrations (TLS/ingress/observability) are declared or supported by the charm itself, though
PostgreSQL TLS is passed through.

## Deployment log

- Deployed `hive-metastore-k8s` from charmhub (edge rev 2) on `concierge-k8s-3` (Juju 3.6.25) with
  resource `ghcr.io/canonical/hive-metastore:4.2.0` → `ImagePullBackOff` (image not found)
- Deployed `postgresql-k8s` channel `14/stable` on the same model
- `juju attach-resource hive-metastore-k8s hive-metastore-image=apache/hive:standalone-metastore-4.2.0`
  → pod started but has no Pebble socket
- `pebble-ready` fired and called `_reconcile()` → `_stop_service()` → uncaught `APIError`
- Unit went to error state with `hook "update-status" failed: exit status 1`; hooks crashed every ~5 min
- Fixed `_stop_service()` in local code (`src/charm.py:198`), packed with `charmcraft pack`, applied
  via `juju refresh hive-metastore-k8s --path hive-metastore-k8s_amd64.charm`
- Unit recovered: error → blocked (`schematool (info) is broken`)
- Built rock from `hive_metastore_rock/rockcraft.yaml` (`hive-metastore_4.2.0_amd64.rock`)
- Pushed rock to a local TLS registry (`registry:2`, NodePort 30420) via skopeo
- containerd refused to pull without insecure-registry config — rock not deployable in this environment
- Re-deployed the fixed local charm (rev 1) to a fresh model; re-integrated with `postgresql-k8s`
- `juju remove-application --destroy-storage` → unit shut down cleanly, storage destroyed
- Attempted on `concierge-k8s-4` (Juju 4.0.12): `postgresql-k8s` refuses (requires Juju < 4.0)

## Observed behaviour

### TLS integration (postgresql-k8s + self-signed-certificates)
`juju integrate postgresql-k8s:certificates self-signed-certificates:certificates` was applied.
`postgresql-k8s` performed a rolling restart and reached `ActiveStatus`. Relation data to
`hive-metastore-k8s` now includes `secret-tls: secret://...` alongside `secret-user: secret://...`.
`PostgresRelationModel.decode()` correctly fetches both via `model.get_secret(id=...).get_content(refresh=True)`.
`_build_jdbc_url` builds `sslmode=verify-ca&sslrootcert=/etc/hive-conf/postgresql-ca.crt` when a CA is present.

### Actions are not defined
`juju actions hive-metastore-k8s` returns "No actions defined for hive-metastore-k8s". All five actions
mentioned in the README (`clear-init-flag`, `restart`, `restore-schema-dirs`, `schematool-info`,
`schematool-validate`) are commented out in `charmcraft.yaml` (lines 82–95). Running any of them fails
with "action not found".

### Hook sequence (from debug-log)
Fresh deploy: `install → leader-elected → storage-attached → config-changed → start → pebble-ready →
postgresql-relation-created → postgresql-relation-joined → postgresql-relation-changed (×2)`. Correct.

After `juju refresh --path`: `upgrade-charm → config-changed → start → pebble-ready`. All hooks run to
completion without crashing.

After `juju remove-relation`: `postgresql-relation-departed → postgresql-relation-broken`. Unit goes to
blocked "waiting for postgresql relation". A brief "unknown relation N resolving next op" message
appears in the uniter log — normal Juju behaviour during relation cleanup.

After `juju remove-application`: `stop → remove`. Unit shut down cleanly, storage destroyed.

### Hook failures before fix (k8s-3, with apache/hive image)
`pebble-ready` and `update-status` both crashed with `APIError: cannot stop services: service
"hive-metastore" does not exist`. The exception escaped the handler. The unit went to error state
permanently; `update-status` re-fired every ~5 min, crashing each time. Confirmed by repeated
`hook "update-status" failed: exit status 1` in debug-log.

### Hook behaviour after fix
All hooks run to completion. The unit reaches `blocked` (not error), which is expected for a
schematool failure. `update-status` fires and exits cleanly every ~5 min.

### Reconciliation flow (observed)
- No PostgreSQL relation: `_stop_service()` called, unit → `BlockedStatus("waiting for postgresql relation")`
- PostgreSQL relation present, schematool info fails with "Failed to get schema version":
  `do_init=True`, `schematool.initialize()` called
- Schematool init fails (no PostgreSQL JDBC driver in `apache/hive` image):
  `BlockedStatus("schematool (initSchema) is broken")`
- Schematool info fails with a non-schema error:
  `BlockedStatus("schematool (info) is broken; run 'juju debug-log' for details")`

### In-container verification (apache/hive image)
- schematool without `HIVE_CONF_DIR`: reads `/opt/hive/conf/metastore-site.xml` (Derby default) → wrong DB
- schematool with `HIVE_CONF_DIR=/etc/hive-conf`: reads `/etc/hive-conf/hive-site.xml` → correct PostgreSQL URL
- `apache/hive` lacks `/opt/hive/lib/postgresql-42.7.7.jar` → `ClassNotFoundException: org.postgresql.Driver`
- After manually adding the JDBC driver: schematool connects to PostgreSQL, reports "VERSION table does not exist"
- Pebble layer sets `JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64` (rock path); `apache/hive` has Java at `/opt/java/openjdk`
- `pebble services` inside the container: "Plan has no services." — the layer is never applied because
  `schematool.info` always fails first, before `_apply_pebble_layer` is reached

### schematool info subprocess on every hook
`schematool -info` fires on every `pebble-ready`, `config-changed`, and `update-status` hook. Each
`update-status` (~5 min interval) takes ~10–15 seconds because of this subprocess.

### Failure injection results

| Scenario | Observed | Correct? |
|---|---|---|
| `hms-max-threads=-9999` (negative int) | `juju config` accepted it; `config-changed` ran cleanly; config silently ignored | ⚠️ silent no-op |
| `hms-max-threads=abc` (wrong type) | `juju config` rejected it: "expected int, got 'abc'" | ✅ (Juju-level validation) |
| `additional-jvm-options="-Xmx999g; rm -rf /"` | accepted by `juju config`; `config-changed` ran cleanly; config silently ignored | ⚠️ silent no-op |
| `juju remove-relation` | `postgresql-relation-broken` → blocked "waiting for postgresql relation" | ✅ |
| `juju integrate` (re-add) | `postgresql-relation-changed` → blocked "schematool (info) is broken" | ✅ |
| Pod restart (`kill 1` in container) | RESTARTS: 1, unit recovered to blocked status | ✅ |
| `juju add-unit -n 1` | Second unit deployed, both blocked | ✅ |
| `juju remove-unit --num-units 1` | Unit removed | ✅ |
| `juju config hms-max-threads=500` | `config-changed` ran cleanly, `hive-site.xml` unchanged (config never read) | ⚠️ |
| `juju remove-application --destroy-storage` | `stop → remove` hooks fired, unit shut down, storage destroyed | ✅ |

## Findings

### `apache/hive` fallback image is incompatible with this charm
- **Severity**: critical
- **Kind**: bug
- **Where**: deployment observation; `hive_metastore_rock/rockcraft.yaml`
- **Evidence**: `apache/hive:standalone-metastore-4.2.0` has no Pebble socket, so `container.can_connect()`
  returns True but Pebble operations fail. It also lacks `/opt/hive/lib/postgresql-42.7.7.jar`, causing
  `ClassNotFoundException: org.postgresql.Driver` when schematool connects to PostgreSQL. Confirmed
  in-container.
- **Impact**: when the primary GHCR image is unreachable (see below), the natural workaround — using
  the upstream `apache/hive` image — fails silently. The charm renders correct config pointing at
  PostgreSQL, but schematool can never connect, and the unit sits in blocked state with no indication
  the image itself is the problem.
- **Fix**: document prominently that this charm requires its own rock image; add a pre-flight check
  that the container has a Pebble socket and the PostgreSQL JDBC driver.
- **Linter rule**: not established

### `_stop_service()` exception handler mismatch crashed the unit (CONFIRMED, FIXED DURING REVIEW)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:207-218`
- **Evidence**: the except clause checked `e.message == f"cannot stop services: service {SERVICE_NAME} does not exist"`,
  but Pebble's actual error is `cannot stop services: service "hive-metastore" does not exist` (quoted).
  The strings never matched, `else: raise` fired, and the exception propagated. Observed repeatedly as
  `hook "update-status" failed: exit status 1` in debug-log.
- **Impact**: every `update-status` and `pebble-ready` crashed the hook, leaving the unit permanently
  unrecoverable without a code fix.
- **Fix applied**: changed to a substring check, `if "does not exist" in e.message and constants.SERVICE_NAME in e.message`.
  Verified by unit test `test_stop_service_service_not_exist_fix_verified` and by observing recovery
  from error state after `juju refresh`.
- **Linter rule**: not mechanically checkable — requires understanding of Pebble's error message format

### Config validators are dead code — `self.config` is never read
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py` (no reference to `self.config` anywhere in the file)
- **Evidence**: `grep -rn "self\.config" src/` returns nothing. `TypedCharmBase[CharmConfig]` is declared
  (`config_type = CharmConfig` at `src/charm.py:32`) but never read. `juju config hms-max-threads=-9999`
  was accepted by Juju (valid integer) and `config-changed` ran cleanly — the Pydantic validator for
  negative values never runs because config is never parsed. `src/config.py` has 15% line coverage;
  the three validator methods (`validate_jvm_options` 50–95, `validate_positive_ints` 107–117,
  `validate_kubernetes_resources` 131–168) are completely untested.
- **Impact**: all five declared config options are silently ignored. Setting `hms-max-threads=500` or
  `additional-jvm-options="-Xmx4g"` has zero effect; the config section in `charmcraft.yaml` is actively
  misleading.
- **Fix**: read `self.config` in `_pebble_layer()` (JVM options), `_render_hive_site()` (thread pool /
  pool size), and wherever Kubernetes resource requests/limits should be applied.
- **Linter rule**: "hook handler never accesses `self.config`" — mechanically checkable by static analysis

### `promote_charm.yaml` is missing `secrets: inherit`
- **Severity**: critical
- **Kind**: bug
- **Where**: `.github/workflows/promote_charm.yaml:23` (`promote-charm` job)
- **Evidence**: the job block lacks `secrets: inherit`, unlike `test.yaml`, `integration_test.yaml`,
  and `publish_charm.yaml`. The job calls `canonical/operator-workflows/.github/workflows/promote_charm.yaml@main`,
  which needs `CHARMHUB_TOKEN` to write to Charmhub.
- **Impact**: promotion from edge to stable will fail at runtime for lack of the token.
- **Fix**: add `secrets: inherit` to the `promote-charm` job block.
- **Linter rule**: not mechanically checkable without understanding the workflow dependency

### No CI step publishes the rock image to GHCR
- **Severity**: critical
- **Kind**: bug
- **Where**: `.github/workflows/publish_charm.yaml`; no `build-rock.yaml` exists
- **Evidence**: `publish_charm.yaml` maps `hive-metastore → hive-metastore-image`, telling Charmhub to
  associate the rock with that resource, but no workflow builds and pushes
  `ghcr.io/canonical/hive-metastore:4.2.0`. `integration_test.yaml` builds the rock locally and pushes
  it only to the microk8s embedded registry, never to GHCR. `ghcr.io/canonical/hive-metastore:4.2.0`
  returned HTTP 404 when this review tried to deploy from charmhub.
- **Impact**: deploying from charmhub is impossible without a pre-existing rock image; publication is
  an untracked, manual step.
- **Fix**: add a `build-rock.yaml` workflow that builds with rockcraft and pushes to GHCR, with
  `publish_charm.yaml` depending on it.
- **Linter rule**: not mechanically checkable without understanding the rock lifecycle

### Config options for thread pools, JVM args, and K8s resources are validated but never used
- **Severity**: high
- **Kind**: bug
- **Where**: `src/hive_metastore.py:164-175` (`_render_hive_site` properties dict); `src/charm.py:175-184` (`_pebble_layer` environment dict)
- **Evidence**: `hms_min_threads`, `hms_max_threads`, `sql_connection_pool_max_size` are validated in
  `CharmConfig` but never appear in the properties passed to the Jinja template. `additional_jvm_options`
  is validated but never passed to the Pebble layer's `environment`. `kubernetes_requests`/
  `kubernetes_limits` are validated but nothing applies them to the container spec.
- **Impact**: the four config options that tune core Hive Metastore behaviour are no-ops.
- **Fix**: add config-derived properties to `_render_hive_site()` and pass JVM options through the
  pebble layer environment.
- **Linter rule**: not established

### `schematool.info()` has no exception handler — transient disconnects crash the hook
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:118`
- **Evidence**: `res = schematool.info(container, env)` is not wrapped in `try/except`. The two other
  Pebble calls in `_reconcile()` (`manage_configuration_files` at line 114, `_apply_pebble_layer` at
  line 149) each catch `ConnectionError`. Only `schematool.info()` is unguarded. If `container.exec()`
  raises `ops.pebble.ConnectionError` (transient network blip, container restart mid-exec, API
  timeout), the exception propagates and the hook exits with code 1. The unit does not crash
  permanently, but the reconciliation for that hook does not complete.
- **Impact**: given schematool's 10–15 second run time, a transient disconnect is a non-trivial
  probability. A hook crash is worse than a deferred `WaitingStatus`.
- **Fix**: wrap the call: `try: ... except ConnectionError: self.unit.status = WaitingStatus("waiting for container"); return`.
- **Linter rule**: "Pebble exec/wait call without surrounding try/except ConnectionError" — mechanically checkable with AST analysis

### `schematool.initialize()` return value is never checked
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:141-142`
- **Evidence**: `res = schematool.initialize(container, env)` is called but `res` is never referenced.
  In `src/schematool.py:55-56`, when init fails with "already"/"exist" in the output (schema tables
  already exist), it returns `SchematoolOperation(..., False)` instead of raising
  `SchemaInitializationError`. The charm proceeds as if init succeeded — calls `_apply_pebble_layer()`
  and sets `ActiveStatus()` — with no way to distinguish "schema already exists, fine" from "schema
  exists but is corrupted."
- **Impact**: possible silent operation on an inconsistent database with no operator indication.
- **Fix**: check `if not res.success: logger.warning(...)` after `initialize()`.
- **Linter rule**: "function return value assigned to a variable but never used" — requires taint analysis, no off-the-shelf ruff rule

### Integration tests assert only status, not behaviour
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py`
- **Evidence**: `test_deploy` asserts `jubilant.all_blocked`; `test_integrate` asserts
  `jubilant.all_active`. Neither verifies `hive-site.xml` content, that `schematool.initialize` was
  called, that the Pebble layer was applied, that config changes propagate, or any failure scenario.
  With the rock image these tests would pass while the config-dead-code bug remained undetected.
- **Impact**: the integration suite provides no protection against regressions in core behaviour.
- **Fix**: add assertions on `hive-site.xml` content, Pebble service state, schematool success, and
  config-driven restarts.
- **Linter rule**: not mechanically checkable

### JAVA_HOME hardcoded to the rock-specific path
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:192` (`_service_environment`); `hive_metastore_rock/rockcraft.yaml:77`
- **Evidence**: `JAVA_HOME` is set to `/usr/lib/jvm/java-21-openjdk-amd64` (rock path). `apache/hive`
  has Java at `/opt/java/openjdk`. Any Pebble exec that relies on `JAVA_HOME` fails with a non-rock image.
- **Impact**: charm only works with the rock; silently breaks Java tooling with any other image.
- **Fix**: make `JAVA_HOME` a `constants.py` value overridable via config, or detect it at runtime from the container.
- **Linter rule**: not established

### `_stop_service()` silently swallows `ConnectionError` and `ChangeError`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:170`
- **Evidence**: the except clause for `ConnectionError`/`ChangeError` logs at debug level and returns
  normally without re-raising. The subsequent `_apply_pebble_layer()` call (with `combine=True`) and
  `container.replan()` usually restart the service anyway, but that outcome is incidental, not
  intentional. A persistent stop failure is never surfaced.
- **Impact**: reconciliation continues without the charm knowing whether the old process actually stopped.
- **Fix**: log a warning and either force-kill or set `MaintenanceStatus("stopping service...")` and defer.
- **Linter rule**: not mechanically checkable

### `_apply_pebble_layer()` only catches `ConnectionError` — `ChangeError` propagates
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:149-154`
- **Evidence**: `container.add_layer()` can raise `ops.pebble.ChangeError` (invalid layer YAML, missing
  command, unknown service key), but only `ConnectionError` is caught. `ChangeError` propagates,
  crashing the hook and putting the unit into error state. No top-level try/except in `_on_pebble_ready` either.
- **Impact**: a misconfigured Pebble layer causes an unrecoverable error state.
- **Fix**: catch `ChangeError` alongside `ConnectionError` and set `BlockedStatus`.
- **Linter rule**: "add_layer call without ChangeError handler" — mechanically checkable with AST analysis

### Schema init failure leaves service in an unrecoverable state
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:140-149`
- **Evidence**: when `schematool.initialize()` raises `SchemaInitializationError`, `_stop_service()`
  has already run (because `do_restart=True`), `BlockedStatus` is set, and the function returns at line
  148 before `_apply_pebble_layer()` is ever called. Pebble is left with no plan. The next hook re-runs
  `schematool.info` and hits the same failure, cycling forever. Recovery requires a manual charm
  refresh. No unit test covers this path.
- **Impact**: a schema init failure permanently stops the service with no automatic recovery.
- **Fix**: after an init failure, either attempt a restart anyway or set a flag that prevents infinite retry.
- **Linter rule**: coverage analysis flags this path as untested

### Storage declared but never used in code
- **Severity**: medium
- **Kind**: bug
- **Where**: `charmcraft.yaml` (storage declaration); `src/charm.py` — no references
- **Evidence**: `hive-metastore-warehouse` storage is declared and mounted at `/user/hive/warehouse`,
  but nothing in `src/` reads, writes, or checks it. Whether Hive Metastore actually needs this
  directory is unconfirmed.
- **Impact**: if required, silent failure risk when storage is unavailable; if optional, the
  declaration is misleading.
- **Fix**: remove the storage declaration if unneeded, or use it explicitly (create/check the directory).
- **Linter rule**: "storage declared but never accessed in code" — mechanically checkable

### `hive-metastore-warehouse-storage-attached` hook has no handler
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` — no observer for `storage-attached`
- **Evidence**: the `storage-attached` hook fires (confirmed in debug-log) but no observer is
  registered in `__init__`; ops auto-discovery runs it as a no-op.
- **Impact**: no modelled dependency between storage readiness and metastore startup, which could
  cause hard-to-diagnose startup failures if the directory is required.
- **Fix**: register a handler that ensures the storage directory exists before the service starts.
- **Linter rule**: "storage declared but no matching hook handler" — mechanically checkable

### TLS CA normalization is a documented no-op
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/hive_metastore.py:207-217` (`_normalize_ca`)
- **Evidence**: `# TODO (mertalpt): This is currently a no-op but we will probably need it.` The
  function returns its input unchanged; a malformed CA is written verbatim to
  `/etc/hive-conf/postgresql-ca.crt`.
- **Impact**: a technically-present but malformed CA causes silent TLS verification failures.
- **Fix**: implement normalization — detect PEM format, strip non-PEM wrappers, normalize line endings.
- **Linter rule**: "TODO comment marking a live no-op" — `grep -n "currently a no-op"`

### `schematool -info` subprocess runs on every hook without caching
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:119` (`_reconcile`); `src/schematool.py:61-78`
- **Evidence**: `schematool.info()` runs on every `pebble-ready`, `config-changed`, and
  `update-status` (600s subprocess timeout). Each `update-status` (~5 min) takes ~10–15s because of it.
- **Impact**: unnecessary subprocess overhead every hook; a hung schematool could block a hook for up to 600s.
- **Fix**: cache schema-initialized state in a file or `StoredState`; skip the info call once known-initialized.
- **Linter rule**: not established

### No explicit `upgrade-charm` handler
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` — no `upgrade-charm` handler
- **Evidence**: `juju refresh` dispatched `upgrade-charm → config-changed → start → pebble-ready`; the
  charm survived because the reconciler is idempotent, not because of an explicit handler.
- **Impact**: relies on implicit idempotency; fragile if future changes require state migration on upgrade.
- **Fix**: implement `_on_upgrade_charm` that calls `_reconcile()` and sets an informative status.
- **Linter rule**: not established

### Unit test coverage run fails under the system Python
- **Severity**: medium
- **Kind**: test-gap
- **Where**: test environment; `.venv` vs system Python
- **Evidence**: `uv run pytest tests/unit/ -v` → 6/6 passing. `coverage run --source=src -m pytest
  tests/unit/` → 5/6 failed with `AttributeError: type object 'TraceFlags' has no attribute
  'RANDOM_TRACE_ID'`. Cause: `coverage run` uses the system Python's `opentelemetry.sdk`, whose
  `TraceFlags` API differs from what the scenario mock expects; `uv run` uses the project `.venv`
  (ops 3.4.0), which doesn't include open-telemetry. CI passes because it uses `with-uv: true`.
- **Impact**: `tox -e unit` fails wherever the system Python has a conflicting `opentelemetry.sdk`.
- **Fix**: run with the project venv (`uv run tox -e unit`), or pin `opentelemetry-sdk`.
- **Linter rule**: not mechanically checkable — environmental

### postgresql-k8s incompatible with Juju 4.x
- **Severity**: medium
- **Kind**: bug
- **Where**: concierge-k8s-4 environment
- **Evidence**: `juju deploy postgresql-k8s --channel 14/stable` on Juju 4.0.12 fails with "Juju
  version not supported"; `postgresql-k8s` requires Juju < 4.0.
- **Impact**: this charm's only integration partner cannot be tested on Juju 4.x.
- **Fix**: test against a newer `postgresql-k8s` channel, or wait for Juju 4.x support upstream.
- **Linter rule**: not established

### Actions documented in README but commented out in charmcraft.yaml
- **Severity**: low
- **Kind**: docs
- **Where**: `charmcraft.yaml` lines 82-95 (commented out); README
- **Evidence**: README lists five actions; none are implemented. Confirmed with `juju actions`.
- **Impact**: misleading documentation.
- **Fix**: uncomment and implement the actions, or remove the actions section from the README.
- **Linter rule**: not established

### Blocked-status message lacks actionable detail
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:105-142`
- **Evidence**: `BlockedStatus("schematool (info) is broken; run 'juju debug-log' for details")` gives
  no specific error text, even though the debug log contains a concrete cause (e.g. missing `JAVA_HOME`).
- **Impact**: operators must dig through logs for information the charm already has.
- **Fix**: include the (truncated) error text in the status message.
- **Linter rule**: not established

### Pydantic v1-style `@validator` is deprecated
- **Severity**: low
- **Kind**: lint
- **Where**: `src/config.py:37, 97, 119`
- **Evidence**: all three validators use `@validator` (v1 style), emitting `PydanticDeprecatedSince20`
  warnings during tests. `pydantic>=1.10,<2` is declared.
- **Impact**: will break on a future Pydantic v3 upgrade.
- **Fix**: migrate to `@field_validator`, or pin `pydantic<3`.
- **Linter rule**: `PYTHONWARNINGS=error pytest` catches this

### `JujuVersion.from_environ()` deprecated in vendored library
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/data_platform_libs/v0/data_interfaces.py:1160`
- **Evidence**: `self._jujuversion = JujuVersion.from_environ()` is deprecated in favour of
  `self.model.juju_version`; emits a `DeprecationWarning`.
- **Impact**: not directly actionable in this repo (vendored library).
- **Fix**: file a bug against `data-platform-libs`.
- **Linter rule**: not established

## Worth copying

- **`TypedCharmBase[CharmConfig]` pattern**: Pydantic-based config with a dedicated `CharmConfig`
  class and validators for every option, including a well-built `additional-jvm-options` validator
  using `shlex.split`. Excellent pattern for other charms to adopt — provided `self.config` is
  actually read (this charm doesn't).
- **Single reconciler with clear status precedence**: `_reconcile()` is the only place that sets unit
  status (Waiting → Blocked → Maintenance → Active), making the code easy to audit.
- **Secrets decoder pattern**: `PostgresRelationModel.decode()` returns a closure that transparently
  handles both JSON-encoded values and `secret:*` URIs.
- **Constants module**: all paths, ports, timeouts, and names centralized in one file.
- **schematool wrapper with typed return**: `SchematoolOperation` dataclass (`stdout`, `stderr`,
  `success`) is a clean abstraction.
- **File permission awareness**: `0o640` for `hive-site.xml`, `0o600` for the CA cert.
- **Jinja2 XML escaping**: template uses `{{ name | e }}` / `{{ value | e }}`, preventing XML injection.
- **Unit tests use `ops.testing.Context`** rather than scenario's `Ops`, avoiding the
  open-telemetry compatibility issue seen with `coverage run`.

## Common-practice notes

- **Two-commit repo, single contributor**: extremely early-stage charm; the initial commit introduced
  the whole codebase with no iteration since.
- **`lib/charms` naming**: `data_platform_libs.v0` (LIBAPI=0) — current canonical convention, correctly followed.
- **tox with uv**: `runner = uv-venv-runner` with dependency groups — matches current ecosystem convention.
- **CI**: uses `canonical/operator-workflows/.github/workflows/test.yaml@main` — currently recommended approach.
- **Pydantic v1, not v2**: `pydantic>=1.10,<2`; `@validator` already emits `PydanticDeprecatedSince20` warnings.
- **ops version inconsistency**: `ops>=3.4.0,<4` declared but the lib dependency says `ops>=2.0.0` — minor mismatch.
- **codespell hits**: all 300+ hits are in `hive_metastore_rock/parts/hadoop/src/share/hadoop/common/lib/jdiff/`
  (Apache Hadoop third-party jdiff XML). Not actionable.

## Tests

**Unit tests**: 6/6 passing via `PYTHONPATH=src:lib python3 -m pytest tests/unit/ -v` (0.13s).
`coverage run -m pytest` (system Python) fails with `AttributeError: type object 'TraceFlags' has no
attribute 'RANDOM_TRACE_ID'` due to an open-telemetry version mismatch. CI uses `uv`, so CI tests pass.

**Coverage**: 60% overall.

| File | Coverage | Key untested lines |
|---|---|---|
| `src/charm.py` | 73% | 57-58 (`PathError` catch), 61-65 (version check), 118 (`schematool.info` — no exception handler), 137-149 (schema init error), 149-154 (`_apply_pebble_layer` `ConnectionError`), 213-215 (`_stop_service` `ConnectionError`/`ChangeError`) |
| `src/config.py` | 15% | 50-95 (`validate_jvm_options`), 107-117 (`validate_positive_ints`), 131-168 (`validate_kubernetes_resources`) — all three validators completely untested, and never called at runtime |
| `src/hive_metastore.py` | 97% | 134 (CA file removal), 199-203 (`_normalize_ca`, the no-op) |
| `src/schematool.py` | 74% | 54-58 (`initialize` success path), 60-66 (`initialize` "already exists" path) |

**Linter** (charm's own `src/` and `tests/`, not vendored `lib/`):
- `ruff check src/` — clean.
- `ruff check tests/` — 8 errors in `tests/unit/test_charm.py`: unused imports `MagicMock`, `ops`
  (F401); uppercase constant `SERVICE_NAME` in function scope (N806); two docstring issues (D205,
  D209); line too long (E501); missing final newline (W292).
- `ruff format --check` — `tests/unit/test_charm.py` would be reformatted.
- `codespell` — hits only in `hive_metastore_rock/parts/hadoop/src/.../jdiff/` (Apache third-party).
  `tox -e lint` FAILS because codespell scans the whole `{tox_root}`, including rock parts.
- `pyright src/` (with `PYTHONPATH=src:lib`) — 0 errors, 0 warnings.

**Vendored library lint debt**: `lib/charms/data_platform_libs/v0/data_interfaces.py` (5743 lines) has
121 ruff violations (all E501) in docstrings/examples. Not actionable from this repo.

**Integration tests**: `tests/integration/test_charm.py` has two tests, both asserting status only
(`all_blocked`, `all_active`). Not run in this review (rock image not deployable). Would not catch:
config dead-code, schematool error paths, Pebble layer correctness, config propagation, or schema-init
failure recovery.

**Critical test gaps**:
1. Schema initialization error path (`src/charm.py:137-149`): after `SchemaInitializationError`,
   `_apply_pebble_layer()` is never called and reconciliation cycles forever. Completely untested.
2. Schema-already-exists path (`src/schematool.py:60-66`): `initialize()` returns
   `SchematoolOperation(success=False)` but the return value at `src/charm.py:141` is never checked.
   Completely untested.

## Docs

README.md is short (2.9KB) but covers deployment, a configuration table, and actions. CONTRIBUTING.md
is detailed with a full local dev environment setup. The Makefile covers common operations.

**Doc/reality mismatches**:
1. README claims five actions exist; none are implemented (commented out in `charmcraft.yaml`).
2. `ghcr.io/canonical/hive-metastore:4.2.0` is not documented as requiring a separate rock build step.
3. No mention that the charm needs a Pebble-compatible OCI image (not the plain `apache/hive` image).
4. The configuration table lists six options, all of which are dead code.
5. CONTRIBUTING.md's `deploy-local` make target uses `localhost:32000` (MicroK8s registry), unavailable
   in this review environment.

## Open questions

1. How should the rock image be published to GHCR? No CI workflow does this today.
2. Does `promote_charm.yaml` actually fail without `secrets: inherit`? Should be dry-run tested before the next promotion.
3. Does `hive-metastore-warehouse` storage need to be used explicitly, or is the declaration vestigial?
4. Is the schema-already-exists path (`schematool.initialize()` returning `success=False`) ever hit in
   practice, or does `initSchema` always succeed on a fresh database?
5. Could a transient `ConnectionError` during the 10–15s `schematool.info()` call realistically crash
   a hook in production? Plausible but not confirmed in this review (unverified).
6. Juju 4.x compatibility for this charm cannot be tested until `postgresql-k8s` supports Juju ≥ 4.0.
