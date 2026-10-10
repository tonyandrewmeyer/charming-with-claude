# superset-k8s

Charmed Superset is a well-structured k8s charm for Apache Superset 6.1.0, with clean code
(pylint 10/10, 124 unit tests passing at 65% coverage), good status management, and clear
error messages under most failure modes. It deploys and runs correctly on Juju 3.6 with
PostgreSQL, Redis, and full observability (Grafana, Prometheus, Loki). It does not reach a
working state on Juju 4.x, because its required dependency `postgresql-k8s` (14/stable) is
not yet Juju-4-compatible — this is an ecosystem gap, not a charm defect. The most serious
in-charm bug is a confirmed crash: Kubernetes' automatic `SUPERSET_PORT` env-var injection
breaks gunicorn's bind address whenever another `superset`-named service exists in the
namespace (open issue #108, root cause traced to `run-server.sh`). A maintainer should fix
that first — it's a one-line change — then address the non-idempotent `k8s-init.sh` startup
sequence and the stale nginx-route config-changed handling.

| | |
|---|---|
| Repo | canonical/superset-k8s-operator @ `3625211` (2026-07-09) |
| Charms | superset-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), latest/edge rev 69; concierge-k8s-4 (Juju 4.0.5), latest/edge rev 69 |
| Reviewed | 2026-08-01 |

## What it does

Charmed Superset deploys Apache Superset v6.1.0 on k8s. It supports four `charm-function`
modes (`app-gunicorn`, `app`, `worker`, `beat`) for separately scaling the UI, Celery workers,
and beat scheduler. Requires PostgreSQL (metadata DB) and Redis (cache + message broker).
Optional integrations: Trino catalog auto-discovery, Google OAuth, SMTP alert emails with
Playwright+Chromium rendering, Sentry, Prometheus metrics, Grafana dashboards, Loki logging,
and nginx ingress. Uses pydantic-v1 structured config with extensive validators.

## Deployment log

### Juju 3.6 — primary deploy (rv-superset-int)
```shell
juju add-model -c concierge-k8s-3 rv-superset-int
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy redis-k8s --channel latest/edge --trust
juju deploy superset-k8s --channel latest/edge
juju deploy traefik-k8s --channel latest/edge --trust
juju deploy self-signed-certificates --channel latest/edge
juju deploy grafana-agent-k8s --channel 1/stable --trust

juju relate superset-k8s postgresql-k8s
juju relate superset-k8s redis-k8s
juju relate superset-k8s:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
juju relate superset-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju relate superset-k8s:logging grafana-agent-k8s:logging-provider

# Unit reached "blocked: missing required config: superset-secret-key"
juju config superset-k8s superset-secret-key='test-key-1234567890abcdef' admin-password='admin123'

# → "maintenance: replanning application" within ~5s
# Superset health check returning 200 within ~10s
# Charm stayed in maintenance until update-status hook (~5 minutes later)
# → "active: Status check: UP", workload version v6.1.0
```

**Image pull time**: cold-cache first deploy exceeded 18 minutes (multi-GB rock image).
Subsequent deploys used the cached image and pods came up in ~14s.

Versions used: `postgresql-k8s` 14/stable rev 925, `redis-k8s` latest/edge rev 42,
`traefik-k8s` latest/edge rev 393, `self-signed-certificates` latest/edge rev 633,
`grafana-agent-k8s` 1/stable rev 164.

### Juju 4.0 — limited deploy (rv-superset-4)
```shell
juju add-model -c concierge-k8s-4 rv-superset-4
juju deploy redis-k8s --channel latest/edge --trust
# postgresql-k8s FAILED: "charm requires Juju version < 4.0.0, model has version 4.0.5"
juju deploy superset-k8s --channel latest/edge
juju deploy nginx-ingress-integrator --channel latest/edge
juju relate superset-k8s nginx-ingress-integrator
juju trust nginx-ingress-integrator --scope=cluster

juju config superset-k8s superset-secret-key='test-key' admin-password='admin123'
# → "blocked: Needs a PostgreSQL relation"
# nginx-route relation data written: service-hostname, service-name, service-port all present
```
`nginx-ingress-integrator` latest/edge rev 490; after trust, it reported "Waiting for ingress
IP availability" (no LoadBalancer in this cluster).

The charm deploys and runs on Juju 4.0 but cannot proceed past `blocked` because
`postgresql-k8s` (14/stable) is constrained to Juju < 4.0.

### Integration attempts

**nginx-route (Juju 3.6)**: the charm uses the `nginx-route` interface from the
`nginx_ingress_integrator` library. Works with `nginx-ingress-integrator`, not with
`traefik-k8s` (`ingress` interface). `juju relate superset-k8s:nginx-route traefik-k8s`
failed with "no relations found".

**Observability (Juju 3.6)**: all three relations worked:
- `grafana-dashboard` → grafana-agent received dashboards
- `metrics-endpoint` → statsd_exporter on port 9102 exposed Go runtime metrics
- `logging` → Loki push API configured in the Pebble plan, forwarding all services' logs
- grafana-agent went `blocked` only because no COS Lite backend was deployed (expected)

## Observed behaviour

### Startup and resource usage
- Deploy to pod Running: ~14s (image pre-cached); 18+ minutes cold cache.
- Config to Superset serving: ~40s (includes `superset db upgrade` migrations).
- Config to charm `ActiveStatus`: ~5 minutes (waiting on update-status interval).
- `superset-k8s-0` pod: 2/2 containers, ~350MB RAM total, ~2m CPU idle.
  - Charm container: pebble + container-agent.
  - Superset container: pebble + gunicorn (1 worker, ~268MB) + statsd_exporter.
- `redis-k8s-0`: 48MB RAM. `postgresql-k8s-0`: 333MB RAM.

### Pebble plan (Juju 3.6, superset container)
- `superset`: enabled, `k8s-bootstrap.sh` → `k8s-init.sh` → `run-server.sh` → gunicorn.
- `metrics-exporter`: enabled, `statsd_exporter`.
- `superset-ui`, `statsd-exporter`: disabled (rock defaults overridden by charm).
- Health check `up`: `GET /health`, period 10s, threshold 3, `on-check-failure: ignore`.
  Observed 24-25 successes, 1 failure recorded during a kill-test restart.
- Loki log forwarding configured, pushing to grafana-agent endpoint.
- All env vars populated from config/relations. `REDIS_HOST` resolves to a FQDN
  (`redis-k8s-0.redis-k8s-endpoints.rv-superset-int.svc.cluster.local`); `SQL_ALCHEMY_URI`
  holds a full PostgreSQL connection string.

### Pebble plan (Juju 4.0, superset container)
- Only rock-default services visible: `statsd-exporter` (disabled), `superset-ui` (disabled).
- No `superset`/`metrics-exporter` service: `_update` exits early because `ready_to_start()`
  is `False` (no PostgreSQL relation).

### Process ownership
All processes run as `root` — gunicorn, statsd_exporter, the bootstrap scripts.
`rockcraft.yaml` specifies `run_user: _daemon_` (UID 584792) and sets file ownership to
584792, but the Juju Pebble container runtime ignores `run_user` entirely. Config files
pushed by the charm are `root:root`, permissions `744`.

### Hook behaviour
- Deploy sequence (7 hooks): install → peer-relation-created → leader-elected →
  pebble-ready → config-changed → start → relation-created (postgresql_db).
- ~60 hooks total across the test session (deploys, config changes, relation add/remove,
  restart).
- Every config-changed triggers a full `_update` cycle, including pebble replan and service
  restart — no diffing against the current plan.

### All failure injections

| Injection | Result | Recovery |
|---|---|---|
| `charm-function=invalid-value` | `BlockedStatus` with enum values listed | Immediate on fix |
| Remove redis relation, re-add | `BlockedStatus` "Needs a Redis relation" → maintenance → active | ~10s |
| `feature-flags=NONEXISTENT_FLAG` | `BlockedStatus` naming the unsupported flag | Immediate on fix |
| `sqlalchemy-pool-size=500` | `BlockedStatus` "Value out of range" (0-300) | Immediate on fix |
| `log-retention-days=-1` | `BlockedStatus` "Value must be non-negative" | Immediate on fix |
| `smtp-secret-id=secret:nonexistent` | `BlockedStatus` (misleading "cannot be accessed") | — |
| SMTP secret with missing keys | `BlockedStatus` listing every missing key (excellent) | — |
| SMTP secret with all keys | `MaintenanceStatus`, env vars correctly injected | — |
| `redis-timeout=301` (non-structural) | Full gunicorn restart + `k8s-init.sh` re-run (db upgrade, create-admin, init) | ~30s |
| Restart action (`juju run restart`) | "superset successfully restarted" | ~3s |
| `kill -9` gunicorn master (PID 247) | Pebble auto-restarted within ~3s; full `k8s-init.sh` re-run | Charm stayed in maintenance, health check recovered to UP |
| Scale 1→2 units | Unit 1 reached maintenance in ~45s | — |
| Scale 2→1 | Unit 1 terminated cleanly in ~10s | — |
| Remove postgresql relation, re-add | `BlockedStatus` "Needs a PostgreSQL relation" → maintenance → active | ~45s |
| Remove application (`juju remove-application`) | Clean teardown, no errors | — |
| `juju config superset-k8s external-hostname=new.example.com` | Superset workload restarted, but nginx-route relation data NOT updated | — |

Note: on postgresql relation removal, the Pebble plan correctly dropped the `superset`
service, but the running service continued to show as "active" in `pebble services` until
the next replan — the plan update and the actual process state were briefly out of sync.

### Juju 4.0 behaviour
- Charm deployed successfully on Juju 4.0.5, rev 69, ubuntu@22.04 base, no errors.
- `redis-k8s` works on 4.0; `postgresql-k8s` (14/stable) does not (Juju version constraint).
- `nginx-ingress-integrator` deploys and the `nginx-route` relation establishes correctly.
- Juju 4.0 uniter logs show the new containeragent architecture, but charm hooks execute
  identically to 3.6.

### nginx-route detail (Juju 4.0, rv-superset-4)
Relation data after relating and trusting `nginx-ingress-integrator`:
```
backend-protocol: HTTP
service-hostname: superset-k8s
service-name: superset-k8s
service-namespace: rv-superset-4
service-port: "8088"
tls-secret-name: superset-tls
```
The charm code passes `tls_secret_name=""` by default. The `superset-tls` value's origin
(nginx-ingress-integrator side, library default, or Juju 4.x behaviour) was not conclusively
determined before model destruction *(unverified)*. Regardless, the underlying bug — that
`external-hostname`/`tls-secret-name` config changes after initial deploy are silently
ignored — is confirmed (finding 5).

## Findings

### 1. Kubernetes `SUPERSET_PORT` injection crashes the workload (open issue #108)
- **Severity**: medium
- **Kind**: bug (confirmed by open issue)
- **Where**: `superset_rock/startup-scripts/k8s-bootstrap.sh`; upstream Superset config parsing
- **Evidence**: Open issue #108 (2026-06-16): when a Kubernetes `superset` service exists in
  the namespace, K8s injects `SUPERSET_PORT=tcp://10.152.183.90:8088`. Superset's config
  parser tries to read this as a port number and crashes: `Error: 'tcp' is not a valid port
  number`. The Pebble service loops indefinitely.
- **Impact**: deploying superset-k8s alongside any other app that creates a service named
  `superset` in the same namespace crash-loops the Superset workload.
- **Fix**: explicitly set `SUPERSET_PORT` in the Pebble layer environment to override the
  K8s-injected value (see finding 2 for exact location).
- **Linter rule**: not mechanically checkable — requires runtime env inspection.

### 2. Root cause confirmed in `run-server.sh`
- **Severity**: medium
- **Kind**: bug (root cause of finding 1)
- **Where**: `superset_rock/startup-scripts/run-server.sh:26-27`
- **Evidence**: gunicorn's bind address is built as
  ```bash
  --bind "${SUPERSET_BIND_ADDRESS:-0.0.0.0}:${SUPERSET_PORT:-8088}"
  ```
  When K8s injects `SUPERSET_PORT=tcp://10.152.183.90:8088`, gunicorn receives
  `--bind 0.0.0.0:tcp://10.152.183.90:8088`, an invalid bind address.
- **Impact**: confirms finding 1 has a simple, charm-side fix rather than needing an upstream
  or rock change.
- **Fix**: add `SUPERSET_PORT: "8088"` (or the configured `APPLICATION_PORT`) to the env dict
  in `_create_env()` (`src/charm.py:430-489`), overriding the K8s-injected value.
- **Linter rule**: "`SUPERSET_PORT` not explicitly set in Pebble layer environment for a k8s
  charm" — mechanically checkable.

### 3. `k8s-init.sh` is non-idempotent — full DB init on every restart
- **Severity**: medium
- **Kind**: bug (design)
- **Where**: `superset_rock/startup-scripts/k8s-init.sh:1-56`
- **Evidence**: runs `superset db upgrade`, `superset fab create-admin`,
  `superset fab reset-password`, and `superset init` on every service restart. Observed live:
  after `kill -9` on gunicorn, Pebble restarted the service and the full init sequence ran
  again, including `create-admin` against an already-provisioned admin user. The script uses
  `set -e`, so a future non-idempotent `create-admin` failure would abort startup entirely.
  In practice Superset 6.1.0's `create-admin` tolerates a pre-existing user, but this is an
  undocumented implementation detail being relied on.
- **Impact**: every restart (Pebble auto-restart, config change, restart action, upgrade)
  re-runs a full DB migration and re-initialises roles/permissions — ~30s wasted per restart,
  and fragile against future upstream changes.
- **Fix**: guard the init steps with a sentinel file or existing-admin check; at minimum wrap
  `create-admin`/`init` so a "already exists" failure doesn't abort startup.
- **Linter rule**: not mechanically checkable — requires shell-script analysis.

### 4. Juju 4.x dependency chain broken (`postgresql-k8s`)
- **Severity**: medium
- **Kind**: bug / ecosystem gap
- **Where**: N/A — deployment constraint
- **Evidence**: superset-k8s rev 69 deployed on Juju 4.0.5 (concierge-k8s-4) and reached
  `blocked: "Needs a PostgreSQL relation"` because `postgresql-k8s` (14/stable rev 925) fails
  to deploy: `charm requires Juju version < 4.0.0, model has version 4.0.5`. `redis-k8s`
  works on 4.0.
- **Impact**: operators on Juju 4.0 cannot get a working superset-k8s deployment even though
  the charm itself runs fine on 4.0 — the whole dependency chain must be 4.x-compatible.
- **Fix**: track `postgresql-k8s` Juju 4.x support and update charm documentation.
- **Linter rule**: not mechanically checkable.

### 5. nginx-route config not propagated on config-changed
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:109` (call site in `__init__`), `src/charm.py:164-172`
  (`_on_config_changed`)
- **Evidence**: `_require_nginx_route()` is called once in `__init__`:
  ```python
  self._require_nginx_route()  # line 109
  ```
  `_on_config_changed` only calls `self._update(event)` (line 172), never re-invoking
  `_require_nginx_route()`. Tested live: changing `external-hostname` restarted the Superset
  workload but did not refresh the nginx-route relation data.
- **Impact**: an operator changing external hostname or TLS secret name expects ingress to
  reconfigure; instead old values persist until the nginx-route relation itself re-fires,
  which may never happen if the relation is stable.
- **Fix**: call `self._require_nginx_route()` from `_on_config_changed` as well.
- **Linter rule**: "`require_nginx_route` called in `__init__` but never re-called on
  config-changed" — mechanically checkable.

### 6. `app` charm-function mode runs Flask in development mode
- **Severity**: low
- **Kind**: bug (security)
- **Where**: `superset_rock/startup-scripts/k8s-bootstrap.sh:55-56`
- **Evidence**:
  ```bash
  elif [[ "${CHARM_FUNCTION}" == "app" ]]; then
    flask run -p 8088 --with-threads --reload --debugger --host=0.0.0.0
  ```
  `--debugger` enables Werkzeug's interactive debugger (arbitrary code execution via PIN);
  `--reload` adds unnecessary CPU overhead watching for file changes.
- **Impact**: an operator selecting the documented, supported `app` mode gets a
  production-facing Flask app with the Werkzeug debugger exposed — a serious risk if
  internet-facing.
- **Fix**: remove `--reload --debugger` from the `app` mode, or clearly document it as
  development-only with a config warning.
- **Linter rule**: "`flask run` with `--reload` or `--debugger` in a production script" —
  mechanically checkable.

### 7. `container.get_check()` called without a connection guard
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:206`
- **Evidence**:
  ```python
  if self.config["charm-function"] in UI_FUNCTIONS:
      check = container.get_check("up")  # line 206
  ```
  `_validate_pebble_plan` catches `pebble.ConnectionError` elsewhere (line 237), but this
  call does not.
- **Impact**: a transient Pebble restart or socket blip during update-status crashes the hook
  into error state, requiring `juju resolved`.
- **Fix**: wrap in try/except for `pebble.ConnectionError`, or guard with
  `container.can_connect()`.
- **Linter rule**: "`container.get_check()` called without preceding `can_connect()` or
  `ConnectionError` handling" — mechanically checkable.

### 8. Charm stays "maintenance" for up to 5 minutes after becoming healthy
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:518` (`MaintenanceStatus("replanning application")`)
- **Evidence**: observed on two separate models — after a successful `_update`, the charm
  sets `MaintenanceStatus` and only transitions to `ActiveStatus` on the next update-status
  hook (5-minute default interval on Juju 3.6), even though the Superset health check
  returned 200 within 10s of startup.
- **Impact**: operators see "maintenance" for up to 5 minutes on a charm that is already
  healthy and serving traffic.
- **Fix**: run the health check immediately after `container.replan()` and set `ActiveStatus`
  if UP, rather than waiting for update-status.
- **Linter rule**: not mechanically checkable.

### 9. Workload restarted on every config-changed, even non-structural changes
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:514-515` (`_update`)
- **Evidence**: changing `redis-timeout` from 300 to 301 triggered a full gunicorn restart
  (new PID confirmed in Pebble logs). `_update` always calls `container.add_layer()` +
  `container.replan()`; since the Pebble layer is rebuilt from config every time, any config
  change produces a different env dict, causing Pebble to restart even for values the running
  process wouldn't otherwise need to reload.
- **Impact**: a config change to e.g. `log-retention-days` or `sqlalchemy-pool-timeout` kills
  in-flight HTTP requests and active Celery tasks unnecessarily.
- **Fix**: compare the new layer against `container.get_plan()` before calling `replan()`, or
  checksum the env dict to decide whether a restart is needed.
- **Linter rule**: "`container.replan()` called unconditionally after `add_layer` without
  comparing against the current plan" — mechanically checkable.

### 10. `_on_update_status` re-runs Trino sync and self-registration checks every 5 minutes
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:215-217` (`_on_update_status`), `src/relations/trino_catalog.py:115-117`
- **Evidence**: `_on_update_status` calls `sync_databases()` on every update-status interval,
  which queries the Superset API and can create/update connections. Even absent a Trino
  relation, `_should_sync()`'s `ready_to_start()` guard re-runs `_validate_config()` every
  interval.
- **Impact**: unnecessary API/DB load every 5 minutes; a failing Trino connection produces
  log spam at the same cadence.
- **Fix**: cache the last sync result and only re-sync on relation-changed events, or track
  whether relation data changed since the last sync.
- **Linter rule**: not mechanically checkable.

### 11. `_validate_self_registration_role` silently swallows all DB errors
- **Severity**: low
- **Kind**: bug (design)
- **Where**: `src/utils.py:74-81` (`query_metadata_database`), `src/charm.py:245-267`
  (`_validate_self_registration_role`), `src/literals.py:31` (`SQL_AB_ROLE`)
- **Evidence**: on first deploy, before the DB is initialised:
  ```
  ERROR unit.superset-k8s/0.juju-log: Error accessing database:
  (psycopg2.errors.UndefinedTable) relation "ab_role" does not exist
  ```
  caught in `query_metadata_database` (line 81: `return []`), causing
  `_validate_self_registration_role` to fall back to `DEFAULT_ROLES`.
- **Impact**: an operator who sets an invalid `self-registration-role` on first deploy gets no
  error — it's silently replaced by defaults, and only surfaces on a later config-changed
  after Superset initialises. A genuine connection error (not just an uninitialised table)
  would be swallowed the same way.
- **Fix**: distinguish `psycopg2.errors.UndefinedTable` (acceptable, return defaults) from
  other database errors (should raise).
- **Linter rule**: not mechanically checkable.

### 12. SMTP secret access errors rely on message substring matching
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:348-355`
- **Evidence**:
  ```python
  except SecretNotFoundError as e:
      msg = str(e)
      if "not granted access" in msg:
          raise ValueError(f"SMTP secret with ID '{secret_id}' cannot be accessed.")
      raise ValueError(f"SMTP secret with ID '{secret_id}' cannot be found.")
  ```
  Observed live: a non-existent secret ID produced "cannot be accessed" instead of "cannot be
  found".
- **Impact**: an operator who typos a secret ID gets the same message as one who forgot to
  grant access, making the error misleading.
- **Fix**: call `model.get_secret(id=secret_id)` separately from `get_content()` to
  distinguish the failure modes.
- **Linter rule**: not mechanically checkable.

### 13. `_on_secret_changed` fires for all secrets, triggering unnecessary replan
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:184-189`
- **Evidence**:
  ```python
  def _on_secret_changed(self, event):
      self._update(event)
  ```
  Fires for every secret change; the Trino catalog handler correctly filters by secret ID
  elsewhere, but this charm-level handler does not.
- **Impact**: rotating Trino credentials causes an unnecessary Superset restart.
- **Fix**: only call `self._update(event)` when the changed secret matches
  `self.config["smtp-secret-id"]`.
- **Linter rule**: not mechanically checkable.

### 14. Celery worker explicitly runs as root (`--uid 0`)
- **Severity**: low
- **Kind**: ux (security)
- **Where**: `superset_rock/startup-scripts/k8s-bootstrap.sh:49`
- **Evidence**:
  ```bash
  celery --app=superset.tasks.celery_app:app worker -O fair -l INFO --uid 0 --without-mingle "${celery_worker_args[@]}"
  ```
- **Impact**: `--uid 0` is redundant (already root) and unnecessarily explicit; combined with
  the rock's ignored `run_user: _daemon_`, it creates a confusing privilege story that would
  break if Pebble ever started honouring `run_user`.
- **Fix**: remove `--uid 0`; fix the Pebble service user context instead if non-root
  operation is desired.
- **Linter rule**: "`--uid 0` or `--user root` in container command" — mechanically checkable.

### 15. Config file permissions inconsistent with `run_user`
- **Severity**: low
- **Kind**: ux
- **Where**: `src/utils.py:56` (`0o744`), `superset_rock/rockcraft.yaml` (`run_user: _daemon_`)
- **Evidence**: observed live: `/app/pythonpath/superset_config.py` is `root:root`, mode
  `744`. The rock declares `run_user: _daemon_` (UID 584792) but processes run as root; if
  the container runtime ever honoured `run_user`, these files would be unreadable.
- **Fix**: set permissions to `755`, or remove the misleading `run_user` from
  `rockcraft.yaml`.
- **Linter rule**: not mechanically checkable.

### 16. Inconsistent `self.model` vs `self.charm.model` in Redis handler
- **Severity**: low
- **Kind**: bug (fragility)
- **Where**: `src/relations/redis.py:51,54`
- **Evidence**:
  ```python
  if self.charm.model.get_relation(REDIS_RELATION_NAME) is None:  # line 51
      ...
  relation = self.model.get_relation(REDIS_RELATION_NAME)          # line 54
  ```
  Both resolve to the same model via the `Object` base class, but the inconsistency obscures
  intent.
- **Fix**: unify on `self.charm.model`.
- **Linter rule**: "`Object` subclass accesses both `self.model` and `self.charm.model` in
  the same method" — mechanically checkable.

### 17. `nginx-route` interface incompatible with `traefik-k8s`
- **Severity**: low
- **Kind**: ux / ecosystem
- **Where**: `charmcraft.yaml:29` (`nginx_ingress_integrator.v0.nginx_route`),
  `src/charm.py:132-140`
- **Evidence**: `juju relate superset-k8s:nginx-route traefik-k8s` fails with "no relations
  found" — traefik-k8s uses the `ingress` interface, not `nginx-route`.
- **Impact**: operators standardised on traefik-k8s must deploy a separate
  `nginx-ingress-integrator` charm (and cluster-trust it) just to route traffic to Superset.
- **Fix**: adopt `traefik_route` or `ingress` to work directly with traefik-k8s.
- **Linter rule**: not mechanically checkable.

### 18. `upgrade-charm` event not handled
- **Severity**: low
- **Kind**: bug (gap)
- **Where**: `src/charm.py:96-107` (event observers)
- **Evidence**: no observer registered for `self.on.upgrade_charm`. Integration tests
  (`test_upgrades.py`, `test_major_upgrades.py`) rely on `config-changed` (which fires after
  `upgrade-charm`) triggering `_update` implicitly.
- **Impact**: no dedicated hook for future migrations or config-format changes on upgrade;
  currently compensated for by `db upgrade` running on every restart (see finding 3).
- **Fix**: add an `_on_upgrade_charm` handler that at minimum logs the event and validates
  version compatibility.
- **Linter rule**: "No `upgrade-charm` event observer registered" — mechanically checkable.

### 19. `superset_api.py` hardcodes port 8088 and admin username
- **Severity**: nit
- **Kind**: ux
- **Where**: `src/superset_api.py:70`, `src/relations/trino_catalog.py:240`
- **Evidence**:
  ```python
  base_url: str = "http://localhost:8088"
  # and
  return SupersetApiClient(admin_username="admin", admin_password=...)
  ```
- **Fix**: derive the base URL from `APPLICATION_PORT`; make admin username configurable.
- **Linter rule**: "Hardcoded `localhost:8088` in API client constructor" — mechanically
  checkable.

### 20. README links to the wrong repository
- **Severity**: nit
- **Kind**: docs
- **Where**: `README.md:27-28`
- **Evidence**:
  ```markdown
  - [Join the Discourse forum](https://discourse.charmhub.io/tag/trino).
  - [Contribute and report bugs](https://github.com/canonical/trino-k8s-operator).
  ```
  Both links reference `trino` instead of `superset`.
- **Fix**: correct to `.../tag/superset` and `.../canonical/superset-k8s-operator`.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Structured config with pydantic validators** (`src/structured_config.py`): extensive
  per-field validation with clear range checks and error messages. The `feature-flags`
  validator reads supported flags from the template file at import time, keeping validation
  in sync with the real Superset config. Tested live with out-of-range, negative, and invalid
  enum values — all produced clear, specific errors.
- **SMTP secret schema validation** (`src/charm.py:_get_smtp_config`): lists every missing
  key individually — an operator knows exactly what to fix.
- **Failure behaviour**: every failure injection produced a clear `BlockedStatus` with a
  human-actionable message; no tracebacks reached the user; all config errors recovered
  immediately on fix.
- **QueryObject cache-key SQL normalisation** (`templates/superset_config.py`): a carefully
  documented, hash-only patch for upstream Superset bug #37114, with comments explaining
  what it does, why, and when to remove it. Handles string literals, quoted identifiers, and
  comments safely — a model for monkey-patching an upstream bug.
- **Permission error message rewriting** (`templates/permission_error_messages.py`):
  intercepts Trino/Ranger JSON error responses and rewrites them into readable messages with
  optional access-request URLs; never blocks responses on error.
- **Logging decorator** (`src/log.py`): `@log_event_handler` traces hook start/completion,
  used consistently across all handlers.
- **Makefile**: comprehensive build/deploy/test/lint/clean targets; `make help` is genuinely
  useful.
- **Integration test coverage**: UI health, crash recovery (destroy + redeploy, verifying
  statelessness), restart action, relation removal/recovery, scaling with Celery worker
  verification, upgrades from previous stable and previous major, and a thorough Trino
  catalog create/add/remove/relation-broken suite (including verifying the "no deletion on
  catalog removal" design decision).

## Common-practice notes

- Follows convention: `src/` layout, `lib/charms/` libraries, `TypedCharmBase` from
  `data_platform_libs`, structured config, standard relation names.
- 8 external charm libraries — heavy but all standard.
- No `StoredState`: state derived from config and relations, the correct modern pattern.
- Pydantic v1 (`pydantic==1.10.12`) while the ecosystem moves to v2; `data_platform_libs`'
  `BaseConfigModel` is still v1-based. Technical debt, not a defect.
- No `upgrade-charm` handler — drift from convention (finding 18).
- Charm base (22.04) vs rock base (24.04) mismatch: the rock was migrated to 24.04 in PR #75
  but `charmcraft.yaml` was not updated.
- `nginx-route` vs traefik ingress — older interface choice, worth noting for operators
  standardised on traefik.
- Single `_update` reconciler always runs to completion and always replans — no short-circuit
  for unchanged state (finding 9).
- Only one action (`restart`) registered — no `get-admin-password`, `pre-upgrade-check`, or
  `health` actions, which the ecosystem is trending toward.

## Tests

### Unit tests
`tox -e unit`: **124 passed, 0 failed, 185 warnings, 1.03s**. Coverage: 65%.
`uv run pytest tests/unit` fails in this environment due to a `scenario`/`ops` version
incompatibility:
```
ImportError: cannot import name '_JujuContext' from 'ops.jujucontext'
```
`tox.ini` pins compatible versions; contributors running outside tox would hit the same
failure. The suite uses `Harness` (deprecated) rather than `Scenario`.

| Module | Stmts | Miss | Cover | Key untested paths |
|---|---|---|---|---|
| `charm.py` | 200 | 25 | 86% | SMTP error paths, `_on_update_status` branches, `_on_restart` body, nginx-route reconfig, `_on_secret_changed` filter, `_validate_self_registration_role` error path, `ready_to_start` redis/DB absent branches |
| `superset_api.py` | 193 | 150 | 23% | Entire file — only exercised by integration tests |
| `trino_catalog.py` | 158 | 104 | 34% | `_should_sync`, `_get_credentials`, `_prepare_sync_config`, `_sync_catalogs`, `_update_existing_connections`, `_create_new_connection`, `_grant_database_access` |
| `redis.py` | 26 | 9 | 66% | `get_redis_relation_data` fallback chain (application_data vs unit_data) |
| `utils.py` | 40 | 8 | 75% | `query_metadata_database` error path (database connection failure) |
| `structured_config.py` | 154 | 6 | 96% | `blank_string` validator None-swallowing, `sentry_sample_rate` / `non_negative_number_validator` edge cases |
| `literals.py` | 17 | 0 | 100% | — |
| `log.py` | 12 | 0 | 100% | — |
| `postgresql.py` | 42 | 6 | 83% | `get_db_info` error paths (no relation, resource not created, empty relation data) |

Coverage gaps most relevant to the findings above: `superset_api.py` (23%, entire file
untested by unit tests) and `trino_catalog.py` (34%, most of the sync logic untested).

### Integration tests
5 test files with good behavioural assertions:
- `test_charm.py`: UI health, crash recovery with chart count verification, restart action.
- `test_scaling.py`: separate UI/worker apps, scale up/down, active Celery worker count.
- `test_upgrades.py`: `5/edge` → local build, UI health.
- `test_major_upgrades.py`: `5/stable` → local build, UI health.
- `test_trino_catalog.py`: full Trino catalog lifecycle (create, add, remove,
  relation-broken) with database count assertions.

Not run in this review due to time constraints — they require a full Juju model, packed
charm, and supporting charms.

### Lint/static analysis
pylint 10.00/10, mypy 0 issues, flake8 0 issues, bandit 0 issues. Ruff found 1 error: missing
`self` argument description in `log.py:30` docstring.

## Docs

- **Discourse**: extensive Diátaxis-structured docs (tutorial, how-to, reference,
  explanation), with good step-by-step coverage of Trino integration, alerts/reports,
  metrics, and security features.
- **README.md**: wrong Discourse tag and Contribute link, both pointing at `trino` instead
  of `superset` (finding 20).
- **CONTRIBUTING.md**: comprehensive — environment setup, building, testing, local
  deployment, relations, Superset version upgrades.
- **Charmhub description**: a single sentence, thin compared to the Discourse docs.
- **In-code docs**: Google-style docstrings throughout; template files have strong inline
  comments, especially the QueryObject patch.

## Open questions

1. **Image size**: the rock image is multiple GB and pull exceeded 18 minutes cold-cache on
   this VM. Is this acceptable for the target audience, or should optional components
   (Playwright/Chromium) be split into a separate image variant?
2. **Juju 4.x dependency chain**: when will `postgresql-k8s` support Juju 4.x? This blocks
   Juju-4.x operators entirely.
3. **SUPERSET_PORT (#108)**: root cause confirmed in `run-server.sh:26-27`; fix is a one-line
   env override. Is there a timeline?
4. **Charm base vs rock base divergence**: why wasn't `charmcraft.yaml` updated to 24.04 when
   the rock moved in PR #75? Is this tracked?
5. **Missing upgrade handler**: is relying on `config-changed` after `upgrade-charm` an
   intentional design decision, or a gap?
6. **nginx-route vs traefik**: any plan to support the traefik `ingress` interface directly?
7. **Unit test environment**: is the suite regularly run outside tox, given the
   `scenario`/`ops` incompatibility with `uv run pytest`?
8. **`app` charm-function mode**: is `flask run --reload --debugger` intentionally left as a
   dev aid? The config field has no warning about its security implications.
9. **`k8s-init.sh` idempotency**: should init be guarded with a sentinel, or is "always run"
   intentional for crash-consistency?
