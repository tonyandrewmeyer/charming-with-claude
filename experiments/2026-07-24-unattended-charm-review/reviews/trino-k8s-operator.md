# trino-k8s-operator

A well-built k8s charm for Trino: clean single-reconciler pattern, thorough Pydantic config validation, broad integration surface (catalogs, Ranger, OpenSearch, COS, ingress), and solid docs. Code quality is high — the reconciler, per-file content hashing for Pebble restart decisions, truststore reconciliation with sidecar manifests, and the peer-state-to-Juju-secrets migration are all worth copying elsewhere.

The charm is not production-hardened against operator typos: a malformed secret ID (`ModelError`, four separate call sites) or an unknown catalog backend (`KeyError`) crashes the hook into error state instead of BlockedStatus, and a single bad catalog aborts configuration of every other catalog. A restart action reports success even when it did nothing. `pyright` is disabled project-wide. Edge rev 71 deployed cleanly on both juju 4.0.5 and 3.6.25, but refreshing from edge to stable is blocked because the `nginx-route` relation was renamed to `ingress` with no migration path.

**First thing a maintainer should do**: wrap `model.get_secret()` call sites in a handler that also catches `ModelError` (four locations, one finding), and stop `_configure_catalogs` from letting one bad catalog kill the rest.

| | |
|---|---|
| Repo | canonical/trino-k8s-operator @ `49db31f` (2026-07-20) |
| Charms | trino-k8s, requirer-charm (test helper) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4, latest/edge rev 71 (`479-24.04-edge`); also on concierge-k8s-3 (juju 3.6.25); traefik-k8s, grafana-agent-k8s, self-signed-certificates, postgresql-k8s integrations tested |
| Reviewed | 2026-07-29 |

## What it does

Deploys Trino (distributed SQL query engine) on Kubernetes in three modes: `all` (single-node), `coordinator`, or `worker`. Manages Trino config files, catalog connectors (postgresql, mysql, redshift, bigquery, gsheets, hive), authentication (file-based password and Google OAuth2), Ranger policy integration, OpenSearch audit logging, COS observability (Prometheus, Loki, Grafana), ingress (traefik-k8s or gateway-api-integrator), PostgreSQL dynamic catalog management via SQL (CREATE/DROP CATALOG), and a `trino-catalog` relation for sharing catalog metadata with requirer apps across models.

## Deployment log

### Primary deployment (juju 4.0.5, concierge-k8s-4)

```
juju switch concierge-k8s-4
juju add-model rv-trino-tls
juju deploy trino-k8s --channel=latest/edge --trust --config charm-function=all
```

- Image pull: ~1.2 GB, took ~9 minutes. Version: `479-24.04-edge`.
- Active ~30s after Pebble plan application.

**Config validation (BlockedStatus, recovers on fix):**
- `juju config charm-function=invalid` → BlockedStatus: `Invalid charm-function 'invalid'; must be one of: coordinator, worker, all`. Recovered on revert.
- `juju config google-client-id=test` → BlockedStatus: `google-client-id is deprecated...`. Recovered after `--reset`.
- `juju config postgresql-catalog-config="bad yaml: ["` → BlockedStatus with YAML parse error.
- `juju config log-level=debug` → stayed active, service restarted (Pebble detected `HASH_CONFIG_PROPERTIES` change).

**Actions:**
- `juju run trino-k8s/0 list-system-users` → `configured-users: trino`, `relation-users: (none)`
- `juju run trino-k8s/0 restart` → `trino successfully restarted`

**Failure injections:**
- `kubectl exec ... -c trino -- kill -9 <trino-pid>` → Pebble auto-restarted within seconds, `juju status` went `active`→`maintenance`→`active`. `on-check-failure: {up: restart}` in the Pebble layer worked correctly.
- `juju config oidc-secret-id=not:a:real:secret` → **ERROR state**: `hook failed: "config-changed"`, `ModelError: ERROR secret URI not valid`, because `_get_secret_content` only catches `SecretNotFoundError`, not `ModelError`. Recovered after `juju config oidc-secret-id=""` and `juju resolve`.
- `juju config catalog-config='catalogs:\n  mycat:\n    backend: nonexistent\nbackends:\n  postgresql:\n    connector: postgresql'` → **ERROR state**: `hook failed: "config-changed"`, `KeyError: 'nonexistent'` at `src/charm.py:650`. Config validation does not cross-validate catalog backends against declared backends.

**Scale and lifecycle:**
- `juju scale-application trino-k8s 2` → second unit went active within ~30s.
- `juju scale-application trino-k8s 1` → scaled down cleanly.
- Both units in `charm-function=all` run independently; no coordination between them at this scale.
- `juju config acl-mode-default=none` → `rules.json` updated, service restarted.

### Comparison deployment (juju 3.6.25, concierge-k8s-3)

```
juju switch concierge-k8s-3
juju add-model rv-trino-3
juju deploy trino-k8s --channel=latest/edge --trust --config charm-function=all
```

Deployed identically. Active within 30s. Same version, same behaviour. No juju-version-specific differences observed.

### PostgreSQL relation test (juju 3.6.25, rv-trino-36)

```
juju switch concierge-k8s-3
juju add-model rv-trino-36
juju deploy trino-k8s --channel=latest/edge --trust --config charm-function=all
juju deploy postgresql-k8s --channel=14/edge --trust -n 1
juju config trino-k8s postgresql-catalog-config='postgresql-k8s:\n  database_prefix: trino*\n  ro_catalog_name: pg_catalog\n  rw_catalog_name: pg_catalog_rw'
juju relate trino-k8s:postgresql postgresql-k8s:database
```

- Relation established. trino-k8s wrote `database: trino*` and `requested-secrets` to the databag.
- PostgreSQL provider published `database`, `endpoints`, `secret-user`, `secret-tls`, `uris`, `version` but not `prefix-databases` (database creation still in progress within the test window).
- trino-k8s handler correctly logged `PG relation postgresql-k8s databag incomplete; provider keys present=[...] error=1 validation error for PostgresqlRelationModel` and returned early — graceful degradation, no crash.
- Designed to converge once `prefix-databases` appears; the incomplete-databag scenario is handled correctly.

### Observability integration test (juju 4.0.5, rv-trino-deep)

```
juju add-model rv-trino-deep
juju deploy trino-k8s --channel=latest/edge --trust --config charm-function=all
juju deploy traefik-k8s --channel=latest/edge --trust
juju deploy grafana-agent-k8s --channel=1/stable --trust
juju deploy self-signed-certificates --channel=latest/edge
juju relate trino-k8s:ingress traefik-k8s:ingress
juju relate trino-k8s:logging grafana-agent-k8s:logging-provider
juju relate trino-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
```

- All relations formed. trino-k8s published `alert_rules` and `scrape_jobs` on `metrics-endpoint` (correctly formatted).
- Ingress: trino-k8s application-data was `{}` — `IngressPerAppRequirer` publishes data only after the provider publishes a URL. traefik-k8s was `blocked` (no TLS certificate relation), so no URL was published. Expected library behaviour, not a charm defect.
- Logging: grafana-agent-k8s published the Loki push endpoint; trino-k8s's Pebble plan correctly included a `log-targets` section. The LogForwarder library initially logged "No Loki endpoints available" (provider data not yet published at pebble-ready time) but converged on the next relation-changed event — expected handshake sequence.
- `grafana-dashboard` relation was not tested (no grafana-k8s deployed).

### `juju refresh` between revisions

```
juju refresh trino-k8s --channel=latest/stable  # from edge rev 71 → stable rev 39
```

- **Blocked**: `ERROR setting application "trino-k8s" charm: charm has no corresponding relation "ingress"`.
- The relation was renamed from `nginx-route` (stable rev 39) to `ingress` (edge rev 71). Juju correctly refuses the downgrade because the model has an active `ingress` relation stable rev 39 doesn't declare.
- No migration path or deprecation period for this rename.
- The failed refresh triggered a Pod restart; recovery was normal (image pull ~9 min, `pebble-ready` fired, charm reconverged), but the unit spent ~10 minutes in `maintenance` before returning to `active`.

### Restart action during container outage

While the trino workload container was still pulling the image after the failed refresh (`container.can_connect()` returned `False`):

```
juju run trino-k8s/0 restart
```

- Returned `trino successfully restarted` even though `_restart_trino()` silently returned without restarting anything. The action handler at `src/charm.py:408-411` unconditionally reports success regardless of whether the container was reachable.

## Observed behaviour

- **Resource usage** (idle, single-node): 567–581 MiB memory, 62–138m CPU. Trino is memory-heavy; expected.
- **Pebble plan**: single `trino` service, `startup: enabled`, `on-check-failure: {up: restart}`, 30s HTTP health check against `http://localhost:8080/`. The rock's `trino-server` entry is disabled (overridden by the charm).
- **Config file layout** (`/usr/lib/trino/etc/`): `config.properties`, `jvm.config`, `log.properties`, `password-authenticator.properties`, `access-control.properties`, `rules.json`, `password.db`. `conf/` holds truststore sidecar manifests.
- **Catalog directory**: `/usr/lib/trino/etc/catalog/` does not exist until a catalog is configured.
- **Port**: 8080 opened by the coordinator (`open-port` in the Pebble layer).
- **`config.properties`** (via `kubectl exec`): `discovery.uri=http://localhost:8080` (correct for `all` mode), `catalog.management=dynamic`, `http-server.authentication.allow-insecure-over-http=true`, `internal-communication.shared-secret=<32-char>`.
- **Per-file hashing**: every managed file gets a `HASH_<NAME>` env var in the Pebble plan; restarts trigger only on real content changes. Confirmed: `log-level=debug` changed `HASH_CONFIG_PROPERTIES` but not `HASH_LOG_PROPERTIES`.
- **Truststore**: two truststores reconciled — `conf/truststore.jks` (catalog certs) and JVM `cacerts` (OpenSearch), tracked via `.truststore-manifest.json` / `.cacerts-manifest.json`. Password is a stable app-owned Juju secret.
- **Internal comms secret**: `INT_COMMS_SECRET` env var visible in the Pebble plan, backed by app-owned secret `trino-int-comms-secret`. Not regenerated on restart.
- **Hook count** for `log-level=info`→`debug`: 1 config-changed hook, no unnecessary deferral or churn.
- **Both environments**: juju 4.0.5 and 3.6.25 behave identically for basic deployment, config changes, and actions.
- **Noisy traceback on every reconcile when no catalogs are configured**: `src/relations/postgresql_catalog.py:258-266` catches `pebble.PathError` (dead code — `list_files` actually raises `APIError`) and falls through to `except pebble.Error`, which logs a full traceback at `WARNING` level. Fires on every reconcile until a catalog exists. Observed live in both juju 4 and 3.6 deployments.
- **Workload crash recovery**: when Trino crashed at startup (JMX config parsing error, this build), Pebble's `on-check-failure: {up: restart}` restarted the service, but `juju status` showed only `"Status check: DOWN"` with no reason. Diagnosing requires `kubectl exec` + `pebble logs` in the workload container.

## Findings

### 1. Bad secret ID format crashes the hook with `ModelError` instead of `BlockedStatus`
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:548-556` (`_get_secret_content`), `src/charm.py:572-574` (`_resolve_oidc_credentials`), `src/charm.py:600-601` (`_compute_credentials`), `src/catalog_manager.py:97-106` (`_get_secret_content`), `src/relations/trino_worker.py:64-77` (`_resolve_int_comms_secret`)
- **Evidence**: `_get_secret_content` calls `self.model.get_secret(id=secret_id)` inside a `try/except SecretNotFoundError` block only. When the secret ID is not a valid Juju secret URI, `model.get_secret()` raises `ModelError`, which propagates uncaught up through `_resolve_oidc_credentials`/`_compute_credentials`/`_reconcile()` and crashes the hook. `catalog_manager.py`'s duplicate `_get_secret_content` has the identical gap, and `trino_worker.py:_resolve_int_comms_secret` has the same gap for the internal comms secret published by the coordinator. **Observed live**: `juju config oidc-secret-id=not:a:real:secret` crashed config-changed with `ModelError: ERROR secret URI not valid`.
- **Impact**: An operator typo in `oidc-secret-id`, `user-secret-id`, any catalog secret-id, or a malformed comms secret ID from a related coordinator puts the charm in Juju error state (traceback, manual `resolve` required) instead of a clear `BlockedStatus`. `_on_list_system_users` survives because it catches `Exception` broadly, but the reconciler paths do not. No unit test covers this path.
- **Fix**: Catch `ModelError` alongside `SecretNotFoundError` in every `_get_secret_content` implementation (and in `_resolve_int_comms_secret`), converting it to a `ValueError`/status the reconciler can turn into `BlockedStatus`.
- **Linter rule**: "`model.get_secret(id=...)` must be wrapped in a handler that catches both `SecretNotFoundError` and `ModelError`" — mechanically checkable by AST pattern match.

### 2. Catalog backend `KeyError` crashes the reconciler (confirmed live)
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:650`
- **Evidence**: `backend = backends[info["backend"]]` raises `KeyError` if a catalog references a backend name absent from the `backends` dict; the call is not wrapped in try/except. **Observed live**: `catalog-config` referencing backend `nonexistent` (not declared in `backends`) crashed the hook with `KeyError: 'nonexistent'`. `validate_catalog_config` only checks that `catalogs`/`backends` top-level keys exist; it never cross-validates references.
- **Impact**: A typo in a catalog's `backend` field yields a cryptic traceback and error state instead of `BlockedStatus("catalog 'foo' references unknown backend 'typo'")`.
- **Fix**: Add a cross-field validator in `CharmConfig` checking `set(catalogs[].backend) <= set(backends.keys())`, and wrap the `backends[info["backend"]]` lookup in try/except in `_configure_catalogs`.
- **Linter rule**: "catalog backend references must be validated against declared backends" — mechanically checkable by a static config validator.

### 3. Single catalog failure aborts all catalog configuration
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:645-657`, `src/catalog_manager.py:130-136`
- **Evidence**: `_configure_catalogs` iterates over catalogs calling `configure_catalogs()`. Each `configure_catalogs()` catches `Exception`, logs, and re-raises (`src/catalog_manager.py:136`). The re-raised exception propagates uncaught through `_configure_catalogs`, crashing the whole reconcile hook.
- **Impact**: With N catalogs, one bad secret ID or malformed backend config means zero catalogs configured — the workload runs with no catalogs at all. Compounds finding #1: a single secret typo is doubly dangerous.
- **Fix**: Catch exceptions per-catalog in `_configure_catalogs` and continue to the next; only fail the whole reconcile if the container is unreachable.
- **Linter rule**: "exception re-raised unguarded in a loop body" — mechanically checkable by AST pattern (`for ...: try: ... except: log; raise`).

### 4. Unguarded `relation.app` access in PostgreSQL catalog handler
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/relations/postgresql_catalog.py:323, 332, 342, 358, 365, 369, 389, 397, 402, 409`
- **Evidence**: `_write_databag` and `_compute_wanted_catalogs` iterate `self.charm.model.relations[self.relation_name]` and access `relation.app.name` without checking `relation.app is not None` (e.g. `entry = config.get(relation.app.name)` at line 365). `_load_relation_data` (line 450) correctly guards this; the callers don't.
- **Impact**: During relation teardown or CMR, `relation.app` can be `None`, causing `AttributeError` and a crashed hook.
- **Fix**: Add `if relation.app is None: continue` at the top of each loop body.
- **Linter rule**: "access to `relation.app.X` without a preceding None guard" — mechanically checkable.

### 5. `set_java_truststore_password` swallows real keytool errors
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:477-499`
- **Evidence**: Catches `(subprocess.CalledProcessError, ExecError)`, treats `"password was incorrect"` and `"Warning"` in stderr as benign, but any other keytool error falls through to `logger.debug(...)` and is silently discarded.
- **Impact**: A missing or corrupted JVM cacerts file is invisible at default `INFO` log level; TLS failures on catalog connections become undiagnosable.
- **Fix**: Log non-ignorable errors at `logger.error`; raise or set status for persistent failures.
- **Linter rule**: not established — requires semantic analysis of stderr patterns.

### 6. Relation rename from `nginx-route` to `ingress` blocks cross-revision refresh
- **Severity**: medium
- **Kind**: bug
- **Where**: `charmcraft.yaml:18` (current metadata), `metadata.yaml` of stable rev 39
- **Evidence**: Stable rev 39 declares `nginx-route`; edge rev 71 declares `ingress`. `juju refresh trino-k8s --channel=latest/stable` fails: `ERROR setting application "trino-k8s" charm: charm has no corresponding relation "ingress"`. **Observed live.**
- **Impact**: Operators cannot downgrade from edge to stable even after removing ingress relations — the relation name is baked into charm metadata. No deprecation period was provided for the rename.
- **Fix**: Keep both `nginx-route` and `ingress` in metadata for one release cycle, or document the breaking change prominently in release notes.
- **Linter rule**: "charm metadata relation rename without backward-compatible alias" — mechanically checkable by comparing metadata across published revisions.

### 7. Restart action reports success when it silently does nothing
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:393-411`
- **Evidence**: `_restart_trino()` checks `if not container.can_connect(): return` and silently returns; `_on_restart` unconditionally sets `event.set_results({"result": "trino successfully restarted"})` regardless. **Observed live**: after a failed `juju refresh`, while the workload container was still pulling the image, `juju run trino-k8s/0 restart` returned `trino successfully restarted` with no restart having occurred.
- **Impact**: An operator running the restart action during an outage gets a false "success" and no signal that nothing happened.
- **Fix**: Have `_restart_trino` return a boolean (or raise), and set the action result from the actual outcome.
- **Linter rule**: "action handler sets result without checking the operation outcome" — not mechanically checkable without flow analysis.

### 8. `_resolve_int_comms_secret` doesn't catch `ModelError`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/relations/trino_worker.py:64-77`
- **Evidence**: Calls `self.charm.model.get_secret(id=secret_id)`, catching only `SecretNotFoundError`. Note: this is the same underlying gap as finding #1, listed there for consolidation, but called out here as it sits in a different subsystem (worker's consumption of a coordinator-published secret ID).
- **Impact**: A malformed internal comms secret ID published by the coordinator — however unlikely — crashes the worker hook instead of producing `WaitingStatus`.
- **Fix**: Add `except ModelError` alongside `SecretNotFoundError`.
- **Linter rule**: same as finding #1.

### 9. `pyright` static type checking is disabled
- **Severity**: medium
- **Kind**: lint
- **Where**: `tox.ini:42-44`
- **Evidence**: Commented out with the rationale `"pyright is new but stricter than bandit and there is planned tasks for a proper refactor later."`
- **Impact**: Would catch finding #10 (return type mismatch) and similar type drift. This is a mature, published project (99 tests, 71% coverage) — worth prioritising.
- **Fix**: Uncomment and fix violations, or add a baseline file.
- **Linter rule**: not established.

### 10. `_get_url` return type is `Optional[str]` but always returns a string
- **Severity**: low
- **Kind**: lint
- **Where**: `src/relations/trino_catalog.py:79-97`
- **Evidence**: Declared `-> Optional[str]` but every path returns a real URL (ingress URL or fallback internal service URL) — no `return None` path. The caller at line 307 checks `if not url: return`, which is dead code.
- **Fix**: Change return type to `str` and remove the dead check, or add an actual `None` path.
- **Linter rule**: "return type annotation does not match actual return paths" — mechanically checkable by pyright.

### 11. Excessive `# nosec` annotations mask real security review surface
- **Severity**: low
- **Kind**: lint
- **Where**: `src/literals.py:45,54,73-79,97-99`, `src/relations/trino_worker.py:51,53`, `src/relations/postgresql_catalog.py:20`
- **Evidence**: Identifiers like `PASSWORD_DB = "password.db"` (a filename) and `SECRET_LABEL = "catalog-config"` (a Juju label) are annotated `# nosec B105`, while `DEFAULT_CREDENTIALS = {"trino": "trinoR0cks!"}` — a genuine hardcoded default password — has no annotation. 44 `# nosec` annotations total in the project.
- **Fix**: Remove `# nosec B105` from non-password identifiers; add it (or document rationale) on `DEFAULT_CREDENTIALS`.
- **Linter rule**: "nosec B105 on non-password string literals" — mechanically checkable by grep.

### 12. `log-level=debug` enables verbose HTTP request logging from ops
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py` (no explicit log-level filter for the ops HTTP client)
- **Evidence**: Setting `log-level=debug` causes the ops framework's HTTP client to log every Kubernetes API request (headers, body) — ~30+ lines per reconcile in `debug-log`, mostly not operator-relevant.
- **Impact**: Operators enabling debug logging for Trino diagnostics get flooded with ops HTTP trace. An ops-framework side effect, not strictly a charm bug, but worth fixing at the charm level.
- **Fix**: Set the `httpx`/`httpcore` logger levels independently of `log-level`, to `WARNING` or `INFO`.
- **Linter rule**: not established.

### 13. `trino_worker`/`trino_coordinator` `_validate` error messages are misleading
- **Severity**: low
- **Kind**: ux
- **Where**: `src/relations/trino_worker.py:115`, `src/relations/trino_coordinator.py:150`
- **Evidence**: `trino_worker._validate` raises `ValueError("Missing Trino coordinator relation.")` even though the worker's own endpoint is `trino-worker`. Symmetrically, `trino_coordinator._validate` raises `"Missing Trino worker relation"` for the `trino-coordinator` endpoint.
- **Impact**: Operators following the error message may try to relate the wrong endpoint.
- **Fix**: Include the correct endpoint name in each message, e.g. `"Missing coordinator relation. Relate via the trino-worker endpoint."`
- **Linter rule**: not established.

### 14. `catalog_manager.py` duplicates `_get_secret_content` from `charm.py`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:537-556`, `src/catalog_manager.py:88-107`
- **Evidence**: Two identical implementations of `_get_secret_content`, both sharing the `ModelError` gap in finding #1. The `catalog_manager` copy depends on `self.charm.model.get_secret()`. `postgresql_catalog.py:122` also has an inline `charm.model.get_secret(id=v)` call without a `ModelError` catch (though its own caller handles it).
- **Impact**: Bug fixes (e.g. finding #1) must be applied in multiple places, and have already drifted out of sync once.
- **Fix**: Consolidate into a shared utility, or have `catalog_manager` call the charm's method.
- **Linter rule**: "duplicate method across modules" — mechanically checkable by AST similarity.

### 15. Noisy traceback from `list_files` on nonexistent catalog directory on every reconcile
- **Severity**: low
- **Kind**: bug
- **Where**: `src/relations/postgresql_catalog.py:256-266`
- **Evidence**: `_read_tracked_catalogs` catches `pebble.PathError` (line 259) as the expected case for a missing catalog directory, but `Container.list_files()` actually raises `pebble.APIError` when the directory is absent — the `PathError` catch is dead code. The `APIError` falls through to `except pebble.Error` at line 263, which logs a full traceback at `WARNING` with `exc_info=True`. **Observed live** on every config-changed/pebble-ready hook in both juju 4 and 3.6 deployments, which is the default state for a fresh deployment with no catalogs configured.
- **Impact**: `debug-log` is polluted with a spurious traceback on every reconcile by default; operators diagnosing real issues must sift through noise.
- **Fix**: Catch `pebble.APIError` (or catch `pebble.Error` first and inspect the message), keeping `PathError` as a secondary catch for forward compatibility.
- **Linter rule**: "except clause for exception type not raised by the called method" — mechanically checkable if the linter has access to the ops library's actual raise sites.

### 16. No `start`, `upgrade-charm`, `install`, or `stop` hook handlers
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py` (absent handlers)
- **Evidence**: The charm only observes `pebble-ready`, `config-changed`, relation events, and action events. Recovery after a charm upgrade depends entirely on `pebble-ready` firing, which currently happens because K8s charms always recreate the Pod on refresh.
- **Impact**: Lifecycle is implicitly coupled to Pod-recreation-on-upgrade behaviour. If a future Juju version reuses the Pod across charm upgrades (as machine charms do), the trino service could never be re-layered into the Pebble plan.
- **Fix**: Observe `self.on.upgrade_charm` and call `_reconcile()` from it; optionally observe `self.on.start` as a secondary recovery path.
- **Linter rule**: "charm does not observe `on.start` or `on.upgrade_charm`" — mechanically checkable.

### 17. Config template hardcodes `openmetrics.jmx-object-names` with pipe separator
- **Severity**: low
- **Kind**: bug
- **Where**: `templates/config.jinja:63`
- **Evidence**: `openmetrics.jmx-object-names=trino.metadata:name=NodeManager|trino.execution:name=InternalNodeManager` uses `|` as a separator. In one observed deployment this crashed Trino at startup with `Error invoking configuration method [... MetricsConfig.setJmxObjectNames(java.util.List<java.lang.String>)]`. The same config worked, with the same image SHA, on a different Pod (unverified whether this is a Trino parser bug, JVM difference, or environment sensitivity).
- **Impact**: Intermittent startup failures from a hardcoded config value, with only a generic "Status check: DOWN" visible from `juju status`.
- **Fix**: Verify the correct JMX object name separator for the bundled Trino version; consider making it configurable or testing across Trino versions.
- **Linter rule**: not established.

## Worth copying

- **Single reconciler pattern** (`src/charm.py:_reconcile`): every hook routes through one idempotent method; status derived separately in `_on_collect_unit_status`. Cleanest pattern seen for complex charms.
- **Per-file content hashing for Pebble** (`src/charm.py`, `content_hash` in `utils.py`): every managed file gets a `HASH_<NAME>` env var; restarts trigger only on real content changes, avoiding the "restart on every hook" anti-pattern.
- **Truststore reconciliation with sidecar manifests** (`src/utils.py:reconcile_truststore`): tracks managed aliases in a JSON manifest, diffs against desired set, only adds/removes what changed. More careful than the common delete-and-recreate pattern.
- **Pydantic config validation** (`src/config.py:CharmConfig`): validates every config option at the type level with custom validators for durations, memory quantities, YAML/JSON, regex, and cross-field constraints, with operator-readable error messages.
- **Migration from peer state to Juju secrets** (`src/charm.py:_purge_legacy_state_values`, `_ensure_truststore_password`): fallback values preserved, secret created once by the leader, legacy keys purged only after the secret is confirmed.
- **`collect_unit_status` as single status derivation point** (`src/charm.py:_on_collect_unit_status`): all status logic in one method, ordered by precedence; the reconciler never sets status directly.
- **`trino-catalog` relation library** (`lib/charms/trino_k8s/v0/trino_catalog.py`): clean provider/requirer with change detection and per-relation app-owned secrets for CMR compatibility.
- **Integration test helpers** (`tests/integration/helpers.py`): `wait_for_apps` with `fast_forward`, `grace_period`, `error_grace` — solid replacement for `ops_test.wait_for_idle` using jubilant.

## Common-practice notes

- **Follows**: `src/` layout with `charm.py`, `config.py`, `literals.py`, `state.py`, `utils.py`; `relations/` subpackage; `lib/charms/` for vendored libraries. Standard ecosystem pattern.
- **Follows**: `tox.ini` with `format`, `lint`, `static`, `unit`, `integration`, using `uv-venv-runner` and `dependency_groups` from `pyproject.toml`.
- **Follows**: `charmcraft.yaml` with `charm-libs`, `uv` plugin, `build-snaps` for `astral-uv`.
- **Drifts**: uses pydantic v1 (`>=1.10,<2`) via `data_platform_libs.BaseConfigModel`; most newer charms have migrated to pydantic v2.
- **Drifts**: `pyright` disabled — most ecosystem charms now run it in CI (TODO acknowledged in `tox.ini`).
- **Leads**: truststore reconciliation with sidecar manifests is more sophisticated than what most charms do; worth adopting elsewhere for Java-keystore management.
- **Leads**: config validation is unusually thorough, including cross-field validators for catalog name conflicts between `postgresql-catalog-config` and `catalog-config`.

## Tests

- **Unit**: 99 tests across 5 files, all pass. Coverage 71% overall (`charm.py` 88%, `config.py` 78%, `postgresql_catalog.py` 40%, `trino_catalog.py` 43%).
- **Integration**: 9 test files covering deployment, policy, resources, scaling, upgrades, catalog updates, managers, `trino-catalog` relation, pg-catalog relation. Run on Canonical K8s with juju 3/stable in CI.
- **Lint**: `ruff` and `codespell` pass clean. `bandit`: 0 issues (44 `# nosec` annotations). `pyright`: disabled.
- **Coverage gaps**: `PostgresqlCatalogRelationHandler` (40%) and `TrinoCatalogRelationHandler` (43%) are the least-tested, most complex handlers — `_write_databag`, `_compute_wanted_catalogs`, `_build_catalog_sql`, `_execute_sql`, `_create_catalog`, `_drop_catalog` have no unit tests. The `ModelError` gap (finding #1) has zero test coverage — no unit test passes a malformed secret ID to any handler.
- **Integration assertions**: tests assert real behaviour — catalog creation via SQL, query execution with the `trino` client library, scaling, upgrade from edge to a local build, crash recovery — not just "wait for active/idle."

## Docs

- **README**: 24 KB, comprehensive; covers all deployment modes, catalog connectors, secrets, users, Ranger, OpenSearch, observability, PostgreSQL integration, resource groups, session property manager. Matches observed behaviour.
- **CONTRIBUTING.md**: 6.6 KB, covers build/test/deploy with `make` targets.
- **Charmhub**: published with stable (rev 39), beta (rev 33), edge (rev 71) channels.
- **Missing**: no terraform module, no architecture diagram (though `trino-tls.svg` is present), no performance tuning guide beyond config option descriptions.

## Open questions

1. **Issue #112 — policy-relation-broken fails when scaling to 0**: filed against rev 33 on `latest/beta`. Current edge rev 71 may have fixed this; confirming requires a multi-unit deployment with the policy relation and a scale-to-0 test.
2. **Catalog secret rotation**: README claims PostgreSQL credential rotation is auto-detected. Static catalogs read secrets via `secret.get_content(refresh=True)` on every reconcile, so new credentials should be picked up and trigger a restart via the content hash — plausible from code review but not tested live (unverified).
3. **Upgrade path correctness**: `test_upgrades.py` covers deploy-edge-then-refresh-to-local-build, but the peer-state→secret migration path in `_purge_legacy_state_values` was only verified by code review (fallback values preserved, secret created once by leader, legacy keys purged only after confirmation) — a live upgrade from a pre-secret revision would settle this definitively.
4. **Discovery URI transition from `all` to `coordinator`**: changing `charm-function` from `all` to `coordinator` changes the discovery URI from `http://localhost:8080` to `http://<app>.<model>.svc.cluster.local:8080`. Not tested.
5. **Trino JMX config compatibility** (see finding #17): root cause of the intermittent startup crash (Trino config parser, JVM version, or environment difference) was not determined; warrants a compatibility check across the Trino versions the charm ships.
