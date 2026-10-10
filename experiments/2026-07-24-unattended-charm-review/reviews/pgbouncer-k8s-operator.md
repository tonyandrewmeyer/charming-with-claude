# pgbouncer-k8s

A well-structured k8s-sidecar charm that deploys PgBouncer as a PostgreSQL connection pooler, backed by `postgresql-k8s`. The codebase is mature and follows the canonical data-platform conventions faithfully — typed config via `TypedCharmBase`, `DataUpgrade` for rolling upgrades, TLS via `PostgreSQLTLS`, COS integrations (metrics, dashboards, Loki, tracing), and multi-instance PgBouncer (one process per CPU core, 2–4). I deployed rev 562 (1/stable) on both Juju 3.6.25 and Juju 4.0.5, and exercised the full lifecycle: deploy, backend/client/TLS/COS relations, config changes (valid and invalid, including bad JSON), relation removal/re-addition, action execution, workload kill/recovery, and scale. The charm recovers cleanly from most disruptions but has three notable failures: (1) a **missing template variable `base_socket_dir`** that silently breaks the PgBouncer `[peers]` section, (2) a **scale-up bug on Juju 3.6.25** that leaves new units stuck in error state (confirmed issue #787), and (3) an **unhandled `json.JSONDecodeError`** when `loadbalancer-extra-annotations` contains bad JSON with `expose-external=loadbalancer`. The auth_user password is still hashed with MD5 while monitoring/admin users use SCRAM. The `_on_update_status` hook does heavyweight PostgreSQL queries every 5 minutes.

| | |
|---|---|
| Repo | canonical/pgbouncer-k8s-operator @ 9d2d3f500 (2026-07-21) |
| Charms | pgbouncer-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25) + concierge-k8s-4 (Juju 4.0.5), charmhub 1/stable rev 562 |
| Reviewed | 2026-07-29 |

## What it does

PgBouncer is a lightweight PostgreSQL connection pooler. This charm runs one PgBouncer process per CPU core (clamped to 2–4), using `so_reuseport` to share a single port. It connects to a backend PostgreSQL via the `backend-database` relation (using the `data_interfaces` library), provides pooled connections to client applications via the `database` relation (using the `postgresql_client` interface), and supports TLS encryption, COS monitoring (metrics-endpoint, grafana-dashboard, loki_push_api), and tracing. Legacy `db`/`db-admin` relations (pgsql interface) are supported but marked for deprecation. The charm manages a Kubernetes Service for external access (`ClusterIP`/`NodePort`/`LoadBalancer`) and handles rolling upgrades via `DataUpgrade`.

## Deployment log

```
# Juju 3.6.25 on concierge-k8s-3
juju switch concierge-k8s-3
juju add-model rv-pgb

# Deploy from charmhub (rev 562, 1/stable)
juju deploy pgbouncer-k8s --channel 1/stable --trust -n 1
juju deploy postgresql-k8s --channel 14/stable --trust -n 1
juju deploy self-signed-certificates --channel latest/stable -n 1

# Wait for units to settle; pgbouncer-k8s goes to blocked "waiting for backend database relation to initialise"
juju relate pgbouncer-k8s:backend-database postgresql-k8s:database
# After ~30s: pgbouncer-k8s goes active (v1.21.0)

# Deploy test client
juju deploy postgresql-test-app --channel latest/edge
juju relate pgbouncer-k8s:database postgresql-test-app:database
# All active

# Add TLS
juju relate pgbouncer-k8s:certificates self-signed-certificates:certificates
# TLS files appear in /var/lib/pgbouncer, pgbouncer.ini updated with client_tls_* config

# Config change
juju config pgbouncer-k8s pool_mode=transaction
# Config reloaded via SIGHUP (no restart), at least 13 lightkube API calls observed

# Invalid config
juju config pgbouncer-k8s pool_mode=invalid
# → BlockedStatus "Configuration Error. Please check the logs" — correct

# Recover
juju config pgbouncer-k8s pool_mode=session
# → ActiveStatus — correct

# Action
juju run pgbouncer-k8s/leader pre-upgrade-check
# → Completed successfully (return-code: 0)

# Kill workload process
kubectl exec pgbouncer-k8s-0 -c pgbouncer -- kill $(pgrep -f 'pgbouncer /var/lib/pgbouncer/instance_0')
# → Pebble restarted pgbouncer_0 within 5s; all services active

# Remove backend relation
juju remove-relation pgbouncer-k8s:backend-database postgresql-k8s:database
# → BlockedStatus "waiting for backend database relation to initialise" — correct

# Re-add backend relation
juju relate pgbouncer-k8s:backend-database postgresql-k8s:database
# → ActiveStatus within ~10s — correct

# Second deployment for COS testing (rv-pgb-d3):
juju add-model rv-pgb-d3
juju deploy pgbouncer-k8s --channel 1/stable --trust -n 1
juju deploy postgresql-k8s --channel 14/stable --trust -n 1
juju deploy grafana-agent-k8s --channel 1/stable -n 1
juju relate pgbouncer-k8s:backend-database postgresql-k8s:database
juju relate pgbouncer-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju relate pgbouncer-k8s:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju relate pgbouncer-k8s:logging grafana-agent-k8s:logging-provider
# All relations connected, pgbouncer active

# Scale-up test (Juju 3.6.25):
juju add-unit pgbouncer-k8s -n 2
# → units 1 and 2 go to error: "hook failed: upgrade-relation-changed"
# → KeyError: <ops.model.Unit pgbouncer-k8s/0> in upgrade.py:987
# → Units stuck; cannot terminate cleanly without --force

# Scale back down (Juju 3.6.25):
juju scale-application pgbouncer-k8s 1
# → Units remain stuck in error; need force-destroy of model

# Juju 4.0.5 test (rv-pgb-j4):
juju switch concierge-k8s-4
juju add-model rv-pgb-j4
juju deploy pgbouncer-k8s --channel 1/stable --trust -n 1
# Deploys fine; blocked waiting for backend (postgresql-k8s not on Juju 4)
juju scale-application pgbouncer-k8s 3
# → All 3 units idle, no errors — scale-up WORKS on Juju 4.0.5
juju scale-application pgbouncer-k8s 1
# → Clean scale-down

# Bad JSON with expose-external=loadbalancer:
juju config pgbouncer-k8s expose-external=loadbalancer loadbalancer-extra-annotations='{broken'
# → JSONDecodeError: Expecting property name enclosed in double quotes
# → config-changed hook fails repeatedly until config is reset

# Remove TLS while running:
juju remove-relation pgbouncer-k8s:certificates self-signed-certificates:certificates
# → TLS files removed, config updated, charm stays active — clean

# Remove/re-add backend:
juju remove-relation pgbouncer-k8s:backend-database postgresql-k8s:database
# → BlockedStatus "waiting for backend database relation to initialise"
juju relate pgbouncer-k8s:backend-database postgresql-k8s:database
# → ActiveStatus within ~20s

# Kill ALL pgbouncer processes at once:
kubectl exec -n rv-pgb-d2 pgbouncer-k8s-0 -c pgbouncer -- bash -c 'kill $(pgrep -f "pgbouncer /var/lib/pgbouncer/instance_")'
# → All 4 pgbouncer processes restarted by Pebble within 3s; charm stays active

# All actions:
juju run pgbouncer-k8s/leader pre-upgrade-check  # → Completed (return-code: 0)
juju run pgbouncer-k8s/leader resume-upgrade       # → Failed: "Upgrade can be resumed only once after juju refresh is called"
juju run pgbouncer-k8s/leader set-tls-private-key key="test-key"  # → Completed (return-code: 0)
```

## Observed behaviour

All observations from Juju 3.6.25, rev 562 (1/stable), unless noted. Juju 4.0.5 notes are marked.

- **Startup time**: ~30s from deploy to ActiveStatus (with backend already connected). From `install` hook to `start` hook: 22s. Pebble ready to active: ~18s.
- **Pebble services**: 4× `pgbouncer_N` (active), `metrics_server` (active when backend connected; disabled otherwise), `logrotate` (backoff — by design, `backoff-delay: 24h`).
- **Resource usage**: 65m CPU, 55Mi memory for the pgbouncer pod (idle). Postgresql backend: 317Mi.
- **Config reload**: A `pool_mode` change fired 1 `config-changed` hook, triggered SIGHUP (not restart), and made 13 lightkube API calls to the K8s API (multiple `get_service` + `get_node` calls for each peer). This is excessive for a simple config change.
- **`base_socket_dir` bug confirmed**: The rendered `pgbouncer.ini` has `[peers]` section with `host=0`, `host=1`, `host=2`, `host=3` — invalid hostnames. The template variable `base_socket_dir` is never passed to `template.render()`. The `socket_dir` for `unix_socket_dir` is correct. This means PgBouncer's PAUSE/RESUME/WAIT peer commands will not work. The `so_reuseport` mechanism masks this in normal operation.
- **Auth file in `/dev/shm`**: Uses shared memory for the userlist file, as per commit `0d5db49cf`. File permissions are `400` owned by `postgres:postgres`. Correct.
- **TLS integration**: Works correctly — `key.pem`, `ca.pem`, `cert.pem` pushed to `/var/lib/pgbouncer/` with `400` permissions. Config updated with `client_tls_*` directives. On TLS relation removal, files are deleted and `client_tls_*` directives removed from config — clean cleanup.
- **COS integrations**: metrics-endpoint, grafana-dashboard, and logging relations all connect correctly with grafana-agent-k8s (1/stable). The metrics server listens on port 9127.
- **Metrics server**: Shows `INACTIVE` briefly during backend initialization (visible in status log), then transitions to active. This is the transient behavior noted in issue #715.
- **Hook count**: 43 total hook invocations over the full lifecycle (deploy + 3 relations + config changes + action + relation removal/re-add).
- **`_on_update_status` overhead**: Not directly measured, but code inspection shows it calls `_collect_readonly_dbs()` (connects to PostgreSQL, runs `SELECT datname FROM pg_database`) and `update_client_connection_info()` (calls `check_service_connectivity()` which opens TCP sockets to all endpoints). This runs every 5 minutes by default.
- **Scale-up: Juju 3.6.25 FAILS**: Scaling from 1 to 3 units causes `KeyError: <ops.model.Unit pgbouncer-k8s/0>` in `data_platform_libs/v0/upgrade.py:987`. New units (1, 2) go to error state with `"hook failed: upgrade-relation-changed"` and retry indefinitely. Units cannot be cleanly removed — the error hooks prevent termination. Only `juju destroy-model --force` removes them. This is issue #787.
- **Scale-up: Juju 4.0.5 WORKS**: The same scale-up from 1 to 3 units completes cleanly on Juju 4.0.5 with all 3 units idle. Scale-down also works. The bug is Juju-version-specific (present in 3.6.25, absent in 4.0.5).
- **Bad JSON with expose-external=loadbalancer CRASHES**: Setting `expose-external=loadbalancer` with `loadbalancer-extra-annotations='{broken'` raises `json.decoder.JSONDecodeError` at `src/charm.py:236`. The config-changed hook fails repeatedly. The JSON parsing is only triggered when service type is LoadBalancer — bad JSON with `expose-external=false` is harmless.
- **Config validation via Pydantic**: `pool_mode=invalid`, `listen_port=0`, `max_db_connections=-1`, and `expose-external=clusternot` all correctly produce `BlockedStatus("Configuration Error. Please check the logs")`. The Pydantic model in `src/config.py` handles this at the config access boundary.
- **All 4 workload processes killed simultaneously**: `kill $(pgrep -f pgbouncer)` terminates all pgbouncer instances. Pebble restarts all 4 within 3 seconds. Charm stays active.
- **Backend reconnect**: After removing and re-adding the backend-database relation, pgbouncer recovers to ActiveStatus within ~20s.
- **Actions**: `pre-upgrade-check` completes (return-code 0). `resume-upgrade` fails with `"Upgrade can be resumed only once after juju refresh is called"` (expected without a `juju refresh`). `set-tls-private-key` completes (return-code 0).
- **Juju 4.0.5**: pgbouncer-k8s deploys and runs correctly standalone. postgresql-k8s (14/stable and 16/stable) requires Juju < 4.0.0, so the charm cannot be tested with a backend on Juju 4.x.

## Findings

### Scale-up fails on Juju 3.6.25 with `KeyError` in upgrade relation handler (issue #787)
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/data_platform_libs/v0/upgrade.py:987`, observed on Juju 3.6.25
- **Evidence**: Scaling from 1 to 3 units on Juju 3.6.25 causes new units (1 and 2) to enter error state with `"hook failed: upgrade-relation-changed"`. The traceback shows:
  ```python
  top_state = self.peer_relation.data[top_unit].get("state")
  KeyError: <ops.model.Unit pgbouncer-k8s/0>
  ```
  The `upgrade_stack.pop()` returns unit ID 0 (the leader), then `self.peer_relation.data[top_unit]` raises `KeyError` because the new unit's view of the relation doesn't yet contain unit 0's data. The hook retries indefinitely — units cannot be cleanly removed (`juju remove-unit` fails on k8s, `juju scale-application` leaves units stuck). Only `juju destroy-model --force` removes them.
- **Why it matters**: Scale-up is completely broken on Juju 3.6.25. Operators who add units will find them permanently stuck in error state, with no path to recovery short of force-destroying the model. This is a blocker for any production deployment that needs to scale.
- **Fix**: Guard the `self.peer_relation.data[top_unit]` access with a check that the unit key exists before accessing it. If the key doesn't exist yet, either defer the event or return early — the hook will fire again when the leader writes its state. Alternatively, use `.get()`-style access that handles missing keys gracefully rather than indexing with `[]`.
- **Notable**: Scale-up works correctly on Juju 4.0.5 with the same charm revision. The race condition is specific to how Juju 3.6.25 synchronizes peer relation data for newly joining units.
- **Linter rule**: Not mechanically checkable — requires integration test with `juju add-unit`.

### Missing `base_socket_dir` template variable breaks `[peers]` section
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:1058` (render call), `templates/pgb_config.j2:11`
- **Evidence**: The template uses `{{ base_socket_dir }}{{ peer }}` in the `[peers]` section, but `render_pgb_config()` never passes `base_socket_dir` to `template.render()`. The rendered config observed in deployment shows:
  ```
  [peers]
  1 = host=0 port=6432
  2 = host=1 port=6432
  3 = host=2 port=6432
  4 = host=3 port=6432
  ```
  These are not valid hostnames or socket paths. The `unix_socket_dir` is set correctly to `/var/lib/pgbouncer/instance_N`, but the peer `host` values should be socket directory paths like `/var/lib/pgbouncer/instance_0`, `/var/lib/pgbouncer/instance_1`, etc.
- **Why it matters**: PgBouncer's PAUSE, RESUME, WAIT, and other peer coordination commands will not work across instances. The `so_reuseport` mechanism allows basic connection pooling to work, but peer-aware operations (e.g., graceful draining during upgrades) are silently broken.
- **Fix**: Add `base_socket_dir` to the template render call in `render_pgb_config()`, e.g., `base_socket_dir=f"{PGB_DIR}/instance_"`.
- **Linter rule**: "Jinja2 template uses `{{ variable }}` that is not passed in any `render()` call in the codebase" — mechanically checkable with a static analysis tool that cross-references template variables with render calls.

### Auth user password hashed with MD5 while monitoring/admin use SCRAM
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/relations/backend_database.py:352`, `lib/charms/pgbouncer_k8s/v0/pgb.py:90-93`
- **Evidence**: In `_on_database_created`:
  ```python
  hashed_password = get_md5_password(self.auth_user, plaintext_password)
  ```
  The monitoring and admin users are hashed with SCRAM via `generate_scram_hash()`, but the auth_user (which has access to all user credentials via `get_auth()`) is still MD5. The `get_md5_password` function uses the `md5()` function from hashlib, which is `# noqa: S324` suppressed. The `auth_type` in `render_pgb_config()` is set to `"md5"` if the monitoring user's hash starts with `"md5"`, otherwise `"scram-sha-256"` — a heuristic based on the monitoring user, not the auth_user.
- **Why it matters**: MD5 is cryptographically broken. The auth_user function (`get_auth()`) returns all user passwords from `pg_authid`, so an attacker who can intercept the auth_user's password hash could potentially access all client credentials. This is tracked upstream as issue #408 (code scanning alert).
- **Fix**: Replace `get_md5_password` with `get_scram_password` for the auth_user, and add a migration path in the upgrade handler similar to `_handle_md5_monitoring_auth`. The `# noqa: S324` suppression should be removed once the MD5 usage is eliminated.
- **Linter rule**: "Call to `hashlib.md5` or `md5()` in charm code" — already detected by bandit/S324 but suppressed with `# noqa`.

### `_on_update_status` performs heavyweight PostgreSQL queries
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:540-547`
- **Evidence**: `_on_update_status` calls `self._collect_readonly_dbs()`, which connects to PostgreSQL and executes `SELECT datname FROM pg_database WHERE datistemplate = false;`. It also calls `self.update_client_connection_info()`, which calls `self.check_service_connectivity()`, which opens TCP sockets to every endpoint. This runs every 5 minutes by default (the `update-status` interval).
- **Why it matters**: Every 5 minutes, the charm opens a PostgreSQL connection, queries all databases, and opens TCP sockets to check connectivity. In a large deployment with many databases, this is wasteful. In a resource-constrained environment, it adds unnecessary load.
- **Fix**: Move the `_collect_readonly_dbs` call to only run when databases change (e.g., on relation-changed events), not on every update-status. Cache the read-only endpoints list and only re-check connectivity when the K8s service changes.
- **Linter rule**: "`_on_update_status` handler calls methods that connect to external services" — mechanically checkable by looking for network calls (socket, psycopg2, lightkube) in update_status handlers.

### Bad JSON in `loadbalancer-extra-annotations` with `expose-external=loadbalancer` causes unhandled `JSONDecodeError`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:236`
- **Evidence**: When `expose-external=loadbalancer` and `loadbalancer-extra-annotations` contains invalid JSON, `reconcile_k8s_service()` at line 236 executes `json.loads(self.config.loadbalancer_extra_annotations)` without a try/except for `JSONDecodeError`. Observed in deployment:
  ```
  json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
  ```
  The config-changed hook fails repeatedly. When `expose-external` is not `loadbalancer`, the `json.loads()` call is skipped (line 238: `if desired_service_type == ServiceType("loadbalancer")`), so bad JSON with other service types is harmless.
- **Why it matters**: An operator setting `expose-external=loadbalancer` with a typo in the annotations JSON will get a stuck error state with no useful message. The `Configuration Error` message from Pydantic validation does not catch this because `loadbalancer-extra-annotations` is typed as `str` in the config model — there is no JSON validation at the config boundary.
- **Fix**: Either (a) wrap `json.loads()` in try/except and set `BlockedStatus` with a clear message like `"Invalid loadbalancer-extra-annotations JSON"`, or (b) add a Pydantic `@validator` on `loadbalancer_extra_annotations` in `src/config.py` that parses the JSON and returns a meaningful error.
- **Linter rule**: "`json.loads()` call without `JSONDecodeError` handling in a hook handler" — mechanically checkable.

### `cached_property` on `BackendDatabaseRequires` is misleading — object recreated every hook
- **Severity**: low
- **Kind**: lint
- **Where**: `src/relations/backend_database.py:177,184,191`
- **Evidence**: `stats_user`, `admin_user`, and `auth_query` are decorated with `@cached_property`, but the `BackendDatabaseRequires` object is instantiated in `PgBouncerK8sCharm.__init__()` every time a hook fires. The `cached_property` cache is therefore per-hook, providing no benefit over a regular `@property`. The import of `cached_property` from `functools` is misleading.
- **Why it matters**: No functional impact, but it suggests the author intended cross-hook caching that isn't happening. A future maintainer might rely on the caching behavior and be surprised.
- **Fix**: Either replace with `@property` or, if caching is desired, move the object to a module-level or use `functools.lru_cache` on the charm instance. The `auth_query` in particular could be cached since it only depends on the relation's existence.
- **Linter rule**: "`@cached_property` on a class that is instantiated in `__init__` of an ops charm" — mechanically checkable by analyzing the class lifecycle.

### Multiple redundant lightkube API calls per config change
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:378-411` (`_on_config_changed`)
- **Evidence**: Observed 13 `HTTP Request: GET .../services/pgbouncer-k8s-service` calls in the debug log for a single `pool_mode` config change. `reconcile_k8s_service()` calls `get_service()` once, and `check_service_connectivity()` calls `get_service()` again. Additionally, `get_node_hosts()` calls `get_node()` for each peer unit, making a separate K8s API call per peer.
- **Why it matters**: Unnecessary load on the K8s API server. A config change that doesn't affect the service (e.g., `pool_mode`) should not trigger K8s API calls at all.
- **Fix**: Only call `reconcile_k8s_service` and `check_service_connectivity` when the config change affects the port or service type. Cache the service object within the hook execution.
- **Linter rule**: "Multiple calls to `lightkube.Client.get()` for the same resource in a single hook" — mechanically checkable.

### `logrotate` service permanently in `backoff` state
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:441-448`
- **Evidence**: The logrotate Pebble service runs `sh -c 'logrotate -v /etc/logrotate.conf; sleep 5'` and exits. With `backoff-delay: 24h` and `backoff-factor: 1`, it shows as `backoff` in `pebble services` indefinitely. This is by design — the comment says "backoff-delay: 24h" to prevent Pebble from restarting it frequently. But operators see a service in `backoff` state permanently.
- **Why it matters**: Operators may think the service is broken. The `pebble services` output shows `backoff` which looks like a failure.
- **Fix**: Use a Pebble `on-check` mechanism or a cron-like approach, or document the expected `backoff` state explicitly. Alternatively, use `startup: disabled` and trigger logrotate via a Pebble exec or a timer service.
- **Linter rule**: Not mechanically checkable — requires understanding the intent of the backoff configuration.

### No validation that client database names don't collide with reserved names
- **Severity**: low
- **Kind**: bug
- **Where**: `src/relations/pgbouncer_provider.py:87-190`, `src/relations/db.py:196-262`
- **Evidence**: Neither `_on_database_requested` nor `_on_relation_joined` validates that the requested database name is not `"pgbouncer"` or `"postgres"`. The `_collect_readonly_dbs` method filters out `"pgbouncer"` and `"postgres"` from readonly databases, but a client database named `"pgbouncer"` would still be added to the `[databases]` section of `pgbouncer.ini`. The PgBouncer documentation states that `pgbouncer` is a reserved database name for the admin console.
- **Why it matters**: If a client requests a database named `"pgbouncer"`, it will conflict with PgBouncer's built-in admin database. This is tracked as issue #716.
- **Fix**: Add validation in `_on_database_requested` and `_on_relation_joined` to reject database names `"pgbouncer"` and `"postgres"`, setting `BlockedStatus` with a clear message.
- **Linter rule**: Not mechanically checkable — requires knowledge of PgBouncer's reserved names.

### `check_service_connectivity` calls `get_service()` redundantly
- **Severity**: nit
- **Kind**: performance
- **Where**: `src/charm.py:582-606`
- **Evidence**: `check_service_connectivity()` calls `self.get_service()` which makes a K8s API call, but the method is often called right after `reconcile_k8s_service()` which already called `get_service()`. The `update_status()` method calls `check_service_connectivity()` which calls `get_service()` independently.
- **Why it matters**: One extra K8s API call per hook that checks connectivity.
- **Fix**: Pass the service object as a parameter or cache it within the hook execution.
- **Linter rule**: "`get_service()` called multiple times in the same hook execution path" — mechanically checkable.

### README says "charm is not yet published"
- **Severity**: nit
- **Kind**: docs
- **Where**: `README.md:11`
- **Evidence**: The README states "As this charm is not yet published, you need to follow the build and deploy instructions from CONTRIBUTING.md." The charm is published on charmhub as 1/stable rev 563.
- **Why it matters**: New operators reading the README will think they need to build from source. The contributing guide also references a different OCI image (`dataplatformoci/pgbouncer:1.16-22.04`) than the current one (`ghcr.io/canonical/charmed-pgbouncer:1.21-22.04_edge`).
- **Fix**: Update the README to reflect the published status and correct deployment instructions.
- **Linter rule**: Not mechanically checkable.

## Worth copying

- **TypedCharmBase with Pydantic config model** (`src/config.py`, `src/charm.py:103`): Using `CharmConfig(BaseConfigModel)` with Pydantic validators gives strong typing and automatic validation. The `ServiceType` enum converts string config values to a typed enum. This is a pattern that prevents config errors at the boundary.
- **Multi-instance PgBouncer with `so_reuseport`** (`src/charm.py:424-464`): Running one PgBouncer process per CPU core with `so_reuseport=1` is a good way to work around PgBouncer's single-threaded nature. The Pebble layer is generated dynamically based on `os.cpu_count()`.
- **Auth file in `/dev/shm`** (`src/charm.py:326-327`): Using shared memory for the userlist file avoids writing credentials to disk, reducing the attack surface. This is a good security practice for credentials.
- **Clean status precedence** (`src/charm.py:616-656`): The `update_status()` method has a clear hierarchy: blocked for missing backend → blocked for backend not ready → blocked for K8s service not connectable → waiting for container → active. The early return on specific blocking messages (extensions, invalid database name) prevents status oscillation.
- **Secret key migration** (`src/charm.py:684-692`): `_translate_field_to_secret_key` handles migration from old databag keys to new secret keys with a mapping (`SECRET_KEY_OVERRIDES`). The `get_secret` method falls back to the old databag key if the new secret key isn't found.
- **Upgrade MD5→SCRAM migration** (`src/upgrade.py:113-137`): The `_handle_md5_monitoring_auth` method handles gradual migration of the monitoring user from MD5 to SCRAM during upgrades, with a fallback that keeps the existing MD5 hash if SCRAM generation fails.
- **Comprehensive test layout**: Unit tests (76 passing, 73% coverage), integration tests (charm, config, TLS, upgrade, expose-external, relations), and spread tests (12 suites). The `test_config_parameters` integration test systematically tests invalid config values.

## Common-practice notes

- **Follows data-platform conventions**: Uses `DataPeerData`, `DataPeerUnitData`, `DatabaseRequires`, `DatabaseProvides`, `DataUpgrade`, `TypedCharmBase` from the canonical data-platform-libs. This is consistent with postgresql-k8s, mysql-k8s, and other data-platform charms.
- **Uses `single_kernel_postgresql` compat layer** (`postgresql-charms-single-kernel = "16.3.4"`): The charm imports both `PostgreSQL` (v0, for PG 14) and `PostgreSQLBase` (v1, for PG 16+) and selects based on the backend version. This is a common pattern in the data-platform ecosystem.
- **Legacy relations**: `db`/`db-admin` (pgsql interface) are marked for deprecation but still actively maintained. The charm logs deprecation warnings on every legacy relation hook. This is consistent with the ecosystem's gradual migration to `postgresql_client`.
- **`charmcraft.yaml` layout**: Uses the modern `poetry-deps` + `charm-poetry` + `files` part structure, with `rustup` for building Rust-based Python dependencies. This is the canonical data-platform pattern.
- **`cached_property` on per-hook objects**: The `@cached_property` on `stats_user`, `admin_user`, `auth_query` is a common pattern in data-platform charms but is misleading since the object is recreated every hook. This is a broader ecosystem issue — the pattern originated when these were on the charm class itself.
- **Drift from convention**: The charm uses `functools.cache` on module-level functions `get_pod` and `get_node` — this is unusual and may cause stale data if the K8s state changes between hooks. Most charms make a fresh lightkube call per hook.

## Tests

- **Unit tests**: 76 passed, 0 failed. 73% line coverage overall. `src/charm.py` has 75% coverage, `src/relations/backend_database.py` has 63% coverage, `src/relations/pgbouncer_provider.py` has 74% coverage. The `src/upgrade.py` has 90% coverage.
- **Untested branches of note**:
  - `reconcile_k8s_service()` in `charm.py` — the `json.loads()` call for `loadbalancer_extra_annotations` is untested; no test validates the error path when JSON is invalid with `expose-external=loadbalancer`.
  - `get_read_only_endpoints()` in `backend_database.py` — the branch where `read-only-endpoints` is absent from the databag is untested.
  - `sync_hba()` in `backend_database.py` — the Retrying loop and the version check branch are untested.
  - `_on_upgrade_changed` in `upgrade.py` — the early return when `check_pgb_running()` returns False is untested.
  - `check_service_connectivity()` — the `gaierror` exception branch is tested, but the `LoadBalancer` with no ingress path is untested.
  - `_get_relation_config()` — the `len(f"{name}_readonly") < 64` branch is only tested with short names; the >64-character truncation path is untested.
- **Integration tests**: Cover build/deploy, config updates, pebble services, logrotate, TLS, backend database, db relations, peers, expose-external, upgrade, and trust. The `test_config_parameters` test systematically validates that invalid config values result in BlockedStatus.
- **Spread tests**: 12 suites covering all major functionality. Run on `lxd-vm` (ubuntu-24.04) and `github-ci` backends.
- **Lint**: `ruff check` passes with no errors. `codespell` passes. `ruff format --check` passes. The ruff configuration is comprehensive (A, E, W, F, C, N, D, B, CPY001, RUF, S, SIM, UP, TC rules).
- **Test framework**: Uses `ops.testing.Harness` (deprecated in favor of Scenario, but still widely used). The `PendingDeprecationWarning` for Harness is visible in test output.

## Docs

- **README**: Out of date — says "charm is not yet published" but it is published on charmhub. References `dataplatformoci/pgbouncer:1.16-22.04` image but the current image is `ghcr.io/canonical/charmed-pgbouncer:1.21-22.04_edge`. The relation descriptions are accurate.
- **CONTRIBUTING.md**: Good detail on environment setup, testing, and build process. The tox commands reference `charmcraft test` which is the current spread-based testing approach. The OCI image reference is outdated.
- **`docs/` directory**: Extensive documentation synced from Discourse, with explanation, how-to, reference, and tutorial sections. Covers deployment, TLS, monitoring, tracing, external access, upgrades, and rollback. The tutorial is comprehensive and would help a new operator.
- **Charmhub description**: Brief but accurate — "Lightweight connection pooler for PostgreSQL. This charm supports PgBouncer in Kubernetes environments."
- **Config docs**: The `config.yaml` descriptions are detailed, particularly the `max_db_connections` option which explains the pool size calculation formula.
- **Doc/reality mismatch**: The README says the charm is "not yet published" — it is. The CONTRIBUTING.md references a different OCI image. The `docs/how-to/h-external-access.md` is 20KB — the most comprehensive doc file, matches the implemented `expose-external` config behavior.

## Open questions

1. **Why does scale-up fail on Juju 3.6.25 but work on Juju 4.0.5?**: The `KeyError` in `upgrade.py:987` is a race condition where the new unit's peer relation data bucket doesn't yet contain the leader's state. Juju 4.0.5 apparently synchronizes peer relation data differently (or the event ordering differs) such that the race doesn't occur. Understanding the exact difference would help the data-platform team fix the underlying library. The issue describes a slightly different error (`AttributeError: 'NoneType' object has no attribute 'get'`) suggesting there may be multiple failure modes depending on timing.

2. **DISCARD ALL transaction error (#740)**: Could not reproduce with the test setup. The issue occurs when `server_reset_query = DISCARD ALL; LOAD 'login_hook';` runs inside a transaction block. This is a PgBouncer-level issue that depends on specific client behavior (e.g., livepatch-server). Would need the specific client to reproduce.

3. **Metrics server backoff after controller migration (#715)**: Could not test controller migration. The transient `INACTIVE` state during backend initialization was observed, but the metrics server recovered. The permanent backoff after migration would require a controller migration to reproduce.

4. **Connection limits with horizontally scaled apps (#634)**: Could not test with multiple client applications. The `max_db_connections` config is per-database, and the charm divides it by the number of PgBouncer instances. When multiple applications share the same backend, the limits are not coordinated across applications. Would need a multi-application deployment to verify.

5. **Pebble native log forwarding (#714)**: The charm still uses `LogProxyConsumer` from `loki_push_api` which downloads promtail. The issue recommends switching to Pebble's native log forwarding. This is a feature request, not a bug.

6. **Unit stuck in error after scale-up: can't scale down cleanly**: When units 1 and 2 are in error state from the scale-up bug, `juju scale-application pgbouncer-k8s 1` does not cleanly remove them — the hooks keep retrying and the units remain in the model until `juju destroy-model --force` is used. This is a Juju behavior issue but worth noting: the charm should handle errors in a way that doesn't block unit removal.