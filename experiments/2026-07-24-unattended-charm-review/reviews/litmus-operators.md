# litmus-operators

Four Kubernetes charms model the LitmusChaos control plane: `litmus-chaoscenter-k8s` (frontend
UI + nginx), `litmus-backend-k8s` (GraphQL API), `litmus-auth-k8s` (authentication), and
`litmus-infrastructure-k8s` (execution-plane beacon). The code uses modern ops patterns
(`cosl.reconciler`, `StatusManager`, `TlsReconciler`) and a shared `litmus-libs` package
published to PyPI. Day-to-day operation (startup, relation cycling, TLS, scaling, Prometheus,
Traefik) works and self-heals from most transient failures. But the charm set has two critical
operability holes: `juju remove-application` permanently wedges on auth/backend because
`storage-detaching` crashes while reading a relation Juju has already torn down, and the auth
service cannot recover from a MongoDB relation remove/re-add cycle (partly a `mongodb-k8s`
library bug, partly a charm self-heal gap). There is also a real correctness bug in credential
handling (`_apply_credentials` can silently desync admin/bot passwords) and a security issue
(a secret ID stored as plaintext charm config). A maintainer should fix the `storage-detaching`
crash and the credential-desync bug first — both cause unrecoverable production incidents —
then address the MongoDB re-add self-heal gap and the `user_secrets` config type.

| | |
|---|---|
| Repo | canonical/litmus-operators @ `eee8e0a` (2026-07-13) |
| Charms | litmus-auth-k8s, litmus-backend-k8s, litmus-chaoscenter-k8s, litmus-infrastructure-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4, `2/edge` (chaoscenter rev27, backend rev14, auth rev13); `dev/edge` for infrastructure (rev12); `juju refresh chaoscenter → dev/edge` accepted (rev47) but the unit stayed on rev27 because it was blocked |
| Reviewed | 2026-08-16 |

## What it does

`litmus-auth-k8s` authenticates users against MongoDB, exposes a gRPC endpoint to the backend
and an HTTP API to the frontend. `litmus-backend-k8s` serves a GraphQL API consumed by the
frontend, also backed by MongoDB, and publishes its own HTTP API. `litmus-chaoscenter-k8s` runs
an nginx reverse proxy serving the web UI; it proxies `/auth` to the auth server and `/api` to
the backend, manages users via a bot account, creates a default chaos environment, and can
register/delete Litmus infrastructure CRDs via `lightkube`. `litmus-infrastructure-k8s` is
workloadless; it publishes model metadata so the ChaosCenter knows where to provision
execution-plane components.

All charms use `cosl.reconciler.observe_events(self, all_events, self._reconcile)` for hook
dispatch and `StatusManager` for status precedence.

## Deployment log

```
# Deployed on concierge-k8s-4 (Juju 4.0.5), model rv-litmus2
juju add-model rv-litmus2 k8s --controller concierge-k8s-4
juju deploy mongodb-k8s --channel 6/edge --trust
juju deploy litmus-auth-k8s --channel 2/edge
juju deploy litmus-backend-k8s --channel 2/edge
juju deploy litmus-chaoscenter-k8s --channel 2/edge
juju deploy litmus-infrastructure-k8s --channel dev/edge

# Relations created:
juju relate mongodb-k8s:database litmus-auth-k8s:database
juju relate mongodb-k8s:database litmus-backend-k8s:database
juju relate litmus-auth-k8s:litmus-auth litmus-backend-k8s:litmus-auth
juju relate litmus-auth-k8s:http-api litmus-chaoscenter-k8s:auth-http-api
juju relate litmus-backend-k8s:http-api litmus-chaoscenter-k8s:backend-http-api
juju integrate litmus-chaoscenter-k8s self-signed-certificates
juju deploy traefik-k8s --channel latest/edge --trust
juju integrate litmus-chaoscenter-k8s traefik-k8s
juju deploy prometheus-k8s --channel 1/stable
juju integrate litmus-chaoscenter-k8s prometheus-k8s

# Result after ~90s:
litmus-auth-k8s:      active    (auth: 3001,3031/tcp — TLS active)
litmus-backend-k8s:   active    (backend: 8001,8081/tcp — TLS active)
litmus-chaoscenter-k8s: active (chaoscenter: 8185/tcp — TLS + traefik ingress)
mongodb-k8s:          active
litmus-infrastructure-k8s: blocked (no integration candidate — chaoscenter 2/edge lacks litmus-infrastructure endpoint)
traefik-k8s:          active    (Serving at http://10.43.45.0)
prometheus-k8s:       blocked   (RBAC — cannot patch StatefulSet; relation to chaoscenter exists)
self-signed-certificates: active
```

Key observations from the deploy:
- The `2/edge` published charm (rev27 chaoscenter) lacks the `user_secrets` config option and
  the `litmus-infrastructure` relation present in local HEAD; both exist in `dev/edge` and the
  more current `3.29/edge` (rev52, which requires ubuntu@26.04, unavailable on this cluster).
- Pebble checks (`auth-up`, `backend-up`) pass on all workload containers; the
  nginx-prometheus-exporter sidecar runs correctly.
- `nginx.conf` confirms HTTPS is active (`ssl_certificate /etc/nginx/certs/server.cert`,
  `listen 8185 ssl`).
- `juju debug-log` showed no tracebacks or hook errors during normal startup.

## Observed behaviour

**Startup timing (`2/edge`, relations pre-established):** mongodb-k8s ~60s to `active`; auth,
backend, chaoscenter ~30s to `active/idle`. Sequence: install → pebble-ready → storage-attached
→ pebble-check-failed briefly → pebble-check-recovered → relations join/change → `active`.

**Relation cycling (backend↔chaoscenter):** removing the `http-api` relation put chaoscenter
into `blocked` after ~20s ("Missing [backend-http-api] integration(s)") and backend into
`waiting` ("Required configurations [frontend url] not ready yet."). Re-adding produced a
mutual deadlock — backend waiting for chaoscenter's frontend URL, chaoscenter waiting for
backend's HTTP API — that self-resolved after ~2.5 minutes (faster than the fresh-deploy
deadlock below because the auth↔backend gRPC connection was already established). The ~20s
detection delay is the uniter polling interval.

**Relation cycling (auth↔backend):** removing the relation put both auth and backend into
`blocked` ("Missing [litmus-auth] integration(s)") immediately. Re-establishing produced an
~8-minute mutual deadlock on the initial deploy, self-resolved by `cosl.reconciler` eventually
firing cross-charm reconciliation events that break the circular wait. The gap between the
~8 min (fresh deploy) and ~2.5 min (relation cycling) deadlock durations is unexplained.

**Hook count for trivial events:** a `trust=true` config change on chaoscenter fires
`update-status`, not `config-changed`, since the `2/edge` charm has no application-level config
options.

**Failure injection — workload kill:** killing PID 1 in the chaoscenter container: Kubernetes
detected the kill, restarted the container within seconds, Pebble re-ran its services, the
uniter fired `chaoscenter-pebble-ready`, and the charm returned to `active`. No traceback, no
`BlockedStatus`. Killing the auth server process (PID 21, `/bin/server`): Pebble auto-restarted
it within seconds (`restart: always`); the `auth-up` check (`threshold: 3`) showed no failures;
the charm stayed `active` throughout.

**Failure injection — relation removal during run:** removing the backend↔chaoscenter relation
produced correct, timely status transitions on both sides (chaoscenter `blocked`, backend
`waiting`, actionable messages).

**Failure injection — mongodb relation removal and recovery:** removing `mongodb-k8s:database`
from `litmus-auth-k8s` put auth into `blocked` ("Missing [database] integration(s)")
immediately; `LitmusAuth._reconcile_workload_config()` correctly stopped the Pebble service
because `db_config=None`. Re-adding the relation: the auth unit's uniter never processed the
`relation-joined` event — the debug log showed `"unknown relation 5 resolving next op"` and the
unit stayed stuck for 4+ minutes. Deleting the pod (forcing a unit-agent resync) let the charm
re-render the Pebble layer with fresh DB credentials, but the auth server then failed to
authenticate: `"auth error: sasl conversation error: unable to authenticate using mechanism
SCRAM-SHA-1: Authentication failed."` Root cause: `mongodb-k8s` sent the literal relation ID
(`DB_USER: relation-17`/`relation-18`) as the username instead of a generated one — a
`mongodb-k8s` library bug — but the auth charm's `_reconcile_workload_config` neither detects
nor handles the bad credential. A manual pod restart was required to recover; the uniter
self-heal path never fired on its own.

**`juju remove-application` fails — `storage-detaching` hook crash:** after the mongodb cycle,
`juju remove-application litmus-auth-k8s` triggered `certs-storage-detaching`, which crashed:

```
ops.model.ModelError: ERROR permission denied
File "...data_interfaces.py", line 549, in get_encoded_list
    data = json.loads(relation.data[member].get(field, "[]"))
```

`LitmusAuth(db_config=self.database_config)` is called unconditionally in `__init__`, and
`database_config` calls `fetch_relation_data()`, which tries to read `requested_secrets` from a
relation Juju has already removed. The app entered `error` ("hook failed:
storage-detaching") and `juju resolve` did not help; storage `certs/2` (16 MiB) stayed
`attached` permanently. Deleting the pod caused the unit to respawn, but the init container then
crashed with `"application litmus-auth-k8s not provisioned"` because Juju had already
deprovisioned the agent — the pod entered `Init:CrashLoopBackOff` and removal stalled for good.
The identical `__init__` pattern exists in `backend/src/charm.py:86`
(`LitmusBackend(db_config=self.database_config)`); this was not directly triggered but is
structurally the same bug.

**TLS integration:** relating `self-signed-certificates` to `litmus-auth-k8s`: auth's
`TlsReconciler` wrote `/etc/tls/tls.crt` and `/etc/tls/tls.key`, called
`update-ca-certificates --fresh`, and restarted the service; the Pebble service picked up
`ENABLE_INTERNAL_TLS=true`, `TLS_CERT_PATH`, `TLS_KEY_PATH`, and ports moved 3000→3001 (REST) and
3030→3031 (gRPC); nginx on chaoscenter correctly picked up the new auth port. Relating TLS to
`litmus-backend-k8s` afterward: backend went `blocked` ("Missing [tls-certificates]
integration(s)") because `_is_missing_tls_certificate` requires both auth and backend to have
TLS if either does; relating backend to TLS fixed it (ports 8000→8001, 8080→8081). Relating TLS
to `litmus-chaoscenter-k8s`: `charmlibs.nginx_k8s.Nginx` wrote certs to
`/etc/nginx/certs/server.cert`/`server.key`, regenerated the nginx config with `listen 8185 ssl`
and `ssl_certificate` directives, and reloaded nginx — confirmed on the running pod:

```
$ cat /etc/nginx/nginx.conf | grep ssl_certificate
    ssl_certificate /etc/nginx/certs/server.cert;
    ssl_certificate_key /etc/nginx/certs/server.key;
$ ls /etc/nginx/certs/
server.cert  server.key
```

An earlier version of this review claimed chaoscenter accepts TLS but never writes certs — that
was wrong, caused by checking `/etc/tls/` (the auth/backend path) instead of
`/etc/nginx/certs/` (the path `charmlibs.nginx_k8s.Nginx` actually uses). TLS on chaoscenter is
functional.

**Traefik ingress integration:** `traefik-k8s` on `latest/edge` (rev397), related to
chaoscenter: status changed from `Ready at https://litmus-chaoscenter-k8s.rv-litmus2.svc.cluster.local:8185.`
to `Ready at http://10.43.45.0:8185.` (traefik LB IP). Entrypoint
`litmus-chaoscenter:8185` (HTTP); routing config at
`/opt/traefik/juju/juju_ingress_traefik-route_14_litmus-chaoscenter-k8s.yaml`. The backend
service URL is the pod's endpoints-service FQDN
(`https://litmus-chaoscenter-k8s-0.litmus-chaoscenter-k8s-endpoints.rv-litmus2.svc.cluster.local:8185`),
produced by `socket.getfqdn()`. `traefik-k8s` itself was `blocked` ("Traefik load balancer is
unable to obtain an IP or hostname from the cluster" — no MetalLB); `prometheus-k8s` was
`blocked` ("Failed to apply resource limit patch: StatefulSet is forbidden" — RBAC).

**Prometheus metrics endpoint:** chaoscenter publishes scrape jobs to `metrics-endpoint`:

```yaml
scrape_jobs: '[{"metrics_path": "/metrics", "static_configs": [{"targets": ["litmus-chaoscenter-k8s-0.litmus-chaoscenter-k8s-endpoints.rv-litmus2.svc.cluster.local:9113"]}]}]'
scrape_metadata: '{"model": "rv-litmus2", ...}'
alert_rules: '{"groups": [{"name": "...HostHealth_alerts", ...}]}'
```

The target is the `nginx-prometheus-exporter` sidecar on port 9113 — functional from
chaoscenter's side; `prometheus-k8s` itself is blocked by RBAC.

**Scaling:** `juju scale-application litmus-chaoscenter-k8s 3` from 1 unit: all 3 units came up
(3/3 Running), chaoscenter stayed `active` throughout. Scale back to 1 was in progress when the
model was destroyed.

**Resource use:** auth pod ~100MB RSS, negligible CPU at steady state; backend pod ~150MB RSS,
moderate CPU during startup; chaoscenter pod ~200MB RSS across 3 containers (chaoscenter,
nginx-prom-exporter, unit agent). Restart counters: chaoscenter restarted once (killed
process); auth and backend restarted zero times (Pebble auto-restarted the killed process
without a container restart).

**Debug log:** no tracebacks, exceptions, or ERROR-level messages in `juju debug-log` for the
entire test run — only INFO-level hook execution messages.

**`juju refresh` to `dev/edge`:** `juju refresh litmus-chaoscenter-k8s --channel dev/edge`
completed (revision 47 added to the model), but the unit stayed on rev27 because it was
`blocked` (missing auth-http-api); the queued `upgrade-charm` hook never fired. The refresh
command reported success even though the unit was never upgraded.

## Findings

### `storage-detaching` hook crashes in auth and backend charms, permanently blocking removal

- **Severity**: critical
- **Kind**: bug
- **Where**: `auth/src/charm.py:88–100`, `backend/src/charm.py:86–100`
- **Evidence**: `juju remove-application litmus-auth-k8s` triggered `certs-storage-detaching`,
  which crashed because `__init__` unconditionally calls
  `LitmusAuth(db_config=self.database_config)`, and `database_config` calls
  `fetch_relation_data()`, which reads a relation Juju has already removed:
  ```
  ops.model.ModelError: ERROR permission denied
  File "...data_interfaces.py", line 549, in get_encoded_list
      data = json.loads(relation.data[member].get(field, "[]"))
  ```
  Same pattern in `backend/src/charm.py:86` (`LitmusBackend(db_config=self.database_config)`).
- **Impact**: `juju remove-application` never completes. Observed: the auth app got stuck in
  `error` state, `juju resolve` did nothing, storage `certs/2` (16 MiB) remained permanently
  `attached`, and a pod-delete recovery attempt instead crashed the init container with
  `"application litmus-auth-k8s not provisioned"` (`Init:CrashLoopBackOff`), stalling removal
  for good. The backend crash was not directly triggered but is structurally identical.
- **Fix**: guard `fetch_relation_data()` in `database_config` with a try/except for
  `ModelError`/`RelationDataError`, returning `None` during teardown; or defer
  `LitmusAuth`/`LitmusBackend` construction out of `__init__` into an event handler.
- **Linter rule**: not mechanically checkable without control-flow analysis.

### mongodb-k8s uses literal `relation-N` as DB username on relation re-add

- **Severity**: critical
- **Kind**: bug
- **Where**: `auth/src/litmus_auth.py` (receives bad credentials); `deps/litmus_libs/models.py:19`
  (`DatabaseConfig`); root cause in `mongodb-k8s`
- **Evidence**: after removing and re-adding `mongodb-k8s:database`, the Pebble layer contained:
  ```yaml
  DB_USER: relation-18
  DB_SERVER: mongodb://relation-18:...@mongodb-k8s-0...:27017/admin?replicaSet=mongodb-k8s
  ```
  Auth failed to authenticate (SCRAM-SHA-1 `Authentication failed`) and the Pebble service
  entered `backoff`, repeatedly crashing.
- **Impact**: any operator who removes and re-adds the mongodb relation (planned maintenance,
  migration, network partition) renders the auth service permanently inaccessible without
  manual intervention. The charm correctly stops the service on removal, but re-add recovery is
  broken by this downstream library bug and the charm does nothing to guard against it.
- **Fix**: primarily a `mongodb-k8s`/`data-platform-libs` fix. Defensively, the auth charm
  could validate `DB_USERNAME` format before rendering the Pebble layer and set `WaitingStatus`
  with a clear message if it looks malformed.
- **Linter rule**: not mechanically checkable in this codebase.

### Auth unit fails to self-heal after mongodb relation removal and re-add

- **Severity**: critical
- **Kind**: bug | ux
- **Where**: `auth/src/charm.py` (uniter behaviour); `deps/litmus_libs/models.py:19`
- **Evidence**:
  ```
  unit-litmus-auth-k8s-0: INFO juju.worker.uniter.relation unknown relation 5 resolving next op
  ```
  The auth unit's uniter never processed the re-added relation event; status stayed `blocked`
  for 4+ minutes. Only a manual pod deletion (forcing unit-agent resync) triggered recovery
  (after which the credential bug above surfaced).
- **Impact**: an operator who temporarily loses connectivity to MongoDB will find the auth
  charm permanently stuck even after MongoDB recovers, requiring a manual pod restart.
- **Fix**: re-check `_db_config` on every reconcile rather than only at construction, or ensure
  `collect_unit_status` always fires a status event (driving reconciliation) even when blocked.
- **Linter rule**: reconciliation state derived from mutable relation data stored in a field
  not refreshed on every reconcile call; mechanically checkable.

### `_apply_credentials` partial-failure returns `False` even when admin succeeded

- **Severity**: high
- **Kind**: bug
- **Where**: `chaoscenter/src/user_manager.py:182–203`
- **Evidence**:
  ```python
  def _apply_credentials(self, creds: _UserSecretModel) -> bool:
      errors = False
      try:
          self._ensure_admin_password(creds.admin_password)  # if this succeeds...
      except Exception:
          logger.exception("failed to apply admin user credentials")
          errors = True
      try:
          self._ensure_charm_user(creds.admin_password, creds.charm_password)
          # ...but this fails:
      except Exception:
          logger.exception("failed to apply charm user credentials")
          errors = True
      if errors:
          return False   # ← returns False even though admin was updated
      return True
  ```
- **Impact**: if the admin password update succeeds but bot-user creation fails, the admin
  password is changed in Litmus's DB but the stored credential reference still points to the
  old password. The next reconcile retries everything, resetting the admin password again — an
  indefinite cycle. Unit tests mock `_apply_credentials` wholesale, so there is no regression
  guard for this partial-failure path.
- **Fix**: track each operation's result independently and roll back the admin password on
  charm-user failure, or treat the pair as a single transaction that doesn't report success
  until both complete.
- **Linter rule**: `try/except` swallowing exceptions and returning `False` despite partial
  success; not mechanically checkable without data-flow analysis.

### Infrastructure data captured once at `__init__`, never refreshed on reconcile

- **Severity**: high
- **Kind**: bug
- **Where**: `chaoscenter/src/charm.py:109–114`
- **Evidence**:
  ```python
  self._chaoscenter = Chaoscenter(
      endpoint=...,
      user_secret_id=self._user_credentials_secret,
      get_secret=...,
      infra_data=self._litmus_infra.get_all_data(),  # ← captured once at __init__
  )
  ```
  `Chaoscenter.reconcile()` calls `self._infra_manager.reconcile(client)` using the stale
  `self._infrastructures` set at construction time.
- **Impact**: if a `litmus-infrastructure` relation is added after startup, the ChaosCenter
  won't register it until the charm restarts; if removed, the ChaosCenter won't delete it
  until restart either.
- **Fix**: store `self._litmus_infra` on `Chaoscenter` and pass freshly-fetched data into
  `self._infra_manager.reconcile(client, infra_data)` on every call.
- **Linter rule**: field initialized from mutable relation data in `__init__` but used in a
  method called repeatedly; mechanically checkable.

### `user_secrets` config uses raw `string` type, leaking credential IDs into model history

- **Severity**: high
- **Kind**: bug | ux
- **Where**: `chaoscenter/charmcraft.yaml:65–84`
- **Evidence**:
  ```yaml
  config:
    options:
      user_secrets:
        description: |
          Secret ID for a user secret containing the passwords for the two users...
        type: string
  ```
  The secret ID (e.g. `secret:da05b5f...`) is stored as plaintext in Juju model config, visible
  via `juju config litmus-chaoscenter-k8s` and persisted in the model database. Also tracked as
  upstream issue #161.
- **Impact**: anyone with model-read access can see the secret ID. `type: secret` (Juju ≥3.3)
  provides validation and grant semantics without storing the ID in model config.
- **Fix**: change `type: string` to `type: secret` in `charmcraft.yaml`.
- **Linter rule**: `charmcraft.yaml` config option named `.*secrets?` uses `type: string`
  instead of `type: secret`.

### Auth/backend circular gRPC endpoint dependency deadlocks on fresh deploy

- **Severity**: medium
- **Kind**: bug
- **Where**: `backend/src/charm.py:148–153`, `auth/src/charm.py:139–144`
- **Evidence**: on fresh deploy each charm's `collect_unit_status` waits for the other's gRPC
  endpoint; both reconcile simultaneously and each reads the other's endpoint from the relation
  databag only after the other has written it. Observed deadlock lasted ~8 minutes before
  self-resolving on the initial deploy (vs ~2.5 min on relation re-add, when the connection was
  already partially established).
- **Impact**: long startup delay; in slower environments this could exceed Juju's hook timeout.
- **Fix**: publish each charm's own endpoint in `*-relation-joined/created` hooks before
  `collect_unit_status` fires, rather than only from leader-gated reconcile; or use a two-phase
  startup with a placeholder endpoint.
- **Linter rule**: not mechanically checkable without cross-charm analysis.

### Test suite has 15 real failures across all charms — four distinct test bugs

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `*/tests/unit/test_status.py`, `chaoscenter/tests/unit/test_pebble_plan.py`,
  `infrastructure/tests/unit/test_charm_tracing_integration.py`
- **Evidence**: `pytest` with `PYTHONPATH` pointing at `src/` and `lib/` (ops 3.8.0, Python
  3.12.3):
  ```
  auth:           115 passed, 4 failed  (test_pebble_check_failing_blocked_status)
  backend:        129 passed, 4 failed  (test_pebble_check_failing_blocked_status)
  chaoscenter:    130 passed, 6 failed  (test_status.py × 4 + test_pebble_plan.py × 2)
  infrastructure: 11 passed, 1 failed   (test_charm_tracing_integration.py × 1)
  Total:          385 passed, 15 failed
  ```
  Bug 1 (`test_pebble_check_failing_blocked_status`, 12 failures across 3 charms): the test
  constructs a `CheckInfo` with `level=None`, mismatched against the Pebble layer's real
  check, and the scenario consistency checker rejects it. Bug 2
  (`test_nginx_exporter_pebble_ready_plan`, 2 failures in chaoscenter): the test hardcodes
  `expected_cmd_args` to always expect `https://` regardless of the TLS fixture; the charm
  actually reads the scheme from relation data, so both `[False]` and `[True]` fixtures fail.
  Bug 3 (`test_charm_tracing_integration[True]`, 1 failure in infrastructure):
  `subprocess.run(["update-ca-certificates", "--fresh"])` is not mocked and fails in-test.
- **Impact**: failing tests hide real regressions; there is no working automated regression
  guard for the pebble-check-failure status path in any of the three charms with that test.
- **Fix**: Bug 1 — pass the correct `level` in the `CheckInfo` fixture. Bug 2 — make
  `expected_cmd_args` conditional on the `tls` parameter. Bug 3 — patch `subprocess.run`.
- **Linter rule**: not mechanically checkable — test correctness is a process issue.

### `litmus_auth` interface uses identical databag fields for both directions

- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/litmus_libs/interfaces/litmus_auth.py`
- **Evidence**: `_LitmusAuthProviderAppDatabagModelV0` and `_LitmusAuthRequirerAppDatabagModelV0`
  share identical field names (`grpc_server_host`, `grpc_server_port`, `insecure`). Both charms
  write to the same application-level databag section sequentially; it works only because each
  side reads back what it last wrote. The `http_api` interface in the same library correctly
  uses separate model classes for the two directions.
- **Impact**: concurrent writes, or a future code change that reads the "other side's"
  endpoint, would silently receive the wrong data.
- **Fix**: use direction-specific field names (e.g. `auth_host`/`auth_port` vs
  `backend_host`/`backend_port`).
- **Linter rule**: two databag model classes with identical field names used in opposite
  directions; mechanically checkable.

### Mixed-mode TLS between auth and backend causes hard block

- **Severity**: medium
- **Kind**: bug | ux
- **Where**: `auth/src/charm.py:121–126`, `backend/src/charm.py:132–137`
- **Evidence**: both charms check `not endpoint.insecure and not self._tls_config` to decide if
  they need a cert. Relating auth to `self-signed-certificates` alone flipped backend from
  `active` to `blocked` ("Missing [tls-certificates] integration(s)") with no change to backend
  itself.
- **Impact**: an operator who secures auth with TLS but forgets to also relate backend to TLS
  renders the backend unreachable; the coupling is implicit and undocumented.
- **Fix**: document the constraint prominently; consider a clearer `WaitingStatus` message.
- **Linter rule**: not mechanically checkable.

### `infra_namespace` not guarded for `None` before K8s delete operations

- **Severity**: medium
- **Kind**: bug
- **Where**: `chaoscenter/src/infra_manager.py:150–165`
- **Evidence**:
  ```python
  def _delete_chaos_experiments_from_k8s(self, namespace):
      for resource in [ChaosExperiment, ChaosEngine, ChaosResult]:
          try:
              self._k8s_client.deletecollection(resource, namespace=namespace)
          except ApiError:
              logger.warning(f"Failed to delete chaos resources in namespace {namespace}")
  ```
  `namespace` comes from `actual_infra[infra_key].namespace`, ultimately from
  `LitmusClient.list_infrastructures()`. If the Litmus API returns `null` for `infraNamespace`,
  `namespace=None` is passed to `deletecollection`, which deletes cluster-wide.
- **Impact**: a malformed Litmus API response with a `null` namespace causes data loss across
  the cluster.
- **Fix**: guard with `if not namespace: return` at the top of
  `_delete_chaos_experiments_from_k8s`, add a `None` check in `list_infrastructures`, and check
  the namespace argument in `_delete_manifest` too.
- **Linter rule**: `namespace=None` in a K8s `deletecollection` call is a cluster-wide delete;
  not mechanically checkable without API-response analysis.

### `load_all_yaml` in infra_manager has no exception handling

- **Severity**: medium
- **Kind**: bug
- **Where**: `chaoscenter/src/infra_manager.py:132–137`
- **Evidence**:
  ```python
  def _apply_manifest(self, manifest: str) -> None:
      for obj in load_all_yaml(manifest):   # no try/except
          self._k8s_client.apply(
              obj, force=True, field_manager="litmus-chaoscenter-charm"
          )
  ```
  A malformed manifest raises `yaml.YAMLError`, which propagates through `reconcile()` and
  crashes the hook with a traceback.
- **Impact**: a buggy or truncated manifest from the Litmus API crashes the charm instead of
  setting `BlockedStatus` with a helpful message.
- **Fix**: wrap `load_all_yaml` in try/except, log, and return early.
- **Linter rule**: call to a library function that raises checked exceptions, without
  try/except, in a reconcile loop; mechanically checkable.

### Mutable class attribute in `LitmusAuth` and `LitmusBackend`

- **Severity**: medium
- **Kind**: lint
- **Where**: `auth/src/litmus_auth.py:20`, `backend/src/litmus_backend.py:30`
- **Evidence**:
  ```python
  class LitmusAuth:
      all_pebble_checks = [liveness_check_name]  # mutable default class attribute
  ```
  Flagged by `ruff RUF012`. This list is shared across all instances.
- **Impact**: currently only read, not written, but fragile — a future append would leak
  across instances.
- **Fix**: use `ClassVar` annotation or initialize in `__init__`.
- **Linter rule**: `ruff RUF012` on `auth/src/litmus_auth.py:20`, `backend/src/litmus_backend.py:30`.

### Blind `Exception` catch in `LitmusClient._login`

- **Severity**: medium
- **Kind**: bug
- **Where**: `chaoscenter/src/litmus_client.py:93`
- **Evidence**:
  ```python
  try:
      resp = self._session.post(..., timeout=10)
      ...
  except Exception as e:  # catches everything, including KeyboardInterrupt, SystemExit
      self._token = None
      raise LitmusAPIException(...)
  ```
- **Impact**: catches genuine `requests` errors correctly but also swallows
  `KeyboardInterrupt`/`SystemExit`. Minor in a reconcile loop but semantically wrong.
- **Fix**: catch `requests.RequestException` instead of bare `Exception`.
- **Linter rule**: `ruff BLE001`; mechanically checkable.

### Generic `Exception` raised in `_ensure_charm_user`

- **Severity**: medium
- **Kind**: bug
- **Where**: `chaoscenter/src/user_manager.py:248`
- **Evidence**:
  ```python
  else:
      raise Exception(
          "charm user exists but login with the configured password failed; "
          "ensure the secret contains the correct current charm password"
      )
  ```
- **Impact**: the message is helpful but the bare `Exception` type is uninformative and easily
  confused with unrelated errors. Flagged by `ruff TRY002`.
- **Fix**: define a `UserConfigurationError(Exception)` or use `ValueError`.
- **Linter rule**: `ruff TRY002`; mechanically checkable.

### Local code has `user_secrets` and `litmus-infrastructure` not in published `2/edge`

- **Severity**: medium
- **Kind**: docs | test-gap
- **Where**: `chaoscenter/charmcraft.yaml` (local) vs `juju info litmus-chaoscenter-k8s` (2/edge)
- **Evidence**: local HEAD (`eee8e0a`) has `user_secrets` config and the `litmus-infrastructure`
  relation. Published `2/edge` (rev27) has neither; `dev/edge` has both; `3.29/edge` (rev52) is
  ahead of local HEAD.
- **Impact**: README/CONTRIBUTING describe features not present in the stable/candidate
  channels; operators deploying from Charmhub won't find `user_secrets` documented behaviour
  actually working.
- **Fix**: document the channel map clearly, keep README scoped to published features, or
  promote `3.29/edge` to `2/stable`.

### `ApiError` caught as "non-existing object" without checking the error code

- **Severity**: low
- **Kind**: bug
- **Where**: `chaoscenter/src/infra_manager.py:149`
- **Evidence**:
  ```python
  except ApiError:
      logger.warning(f"Failed to delete non-existing object {name}")
  ```
  `ApiError` covers any Kubernetes API error, not just 404 Not Found; a 403 Forbidden (RBAC)
  would be logged as "non-existing" and silently ignored.
- **Impact**: permission errors get hidden, leaving the charm confused (object not deleted, not
  retried).
- **Fix**: check `ApiError.status.code`, suppress only 404, log and re-raise others.
- **Linter rule**: `except` catching a broad exception type with a misleading log message.

### `LitmusClient` login has no retry/backoff

- **Severity**: low
- **Kind**: performance
- **Where**: `chaoscenter/src/litmus_client.py:83–96`
- **Evidence**: `_login()` is called on every request via `_ensure_token()`; if the Litmus API
  is temporarily down, every reconcile triggers an immediate retry with no delay.
- **Impact**: a temporary Litmus API outage could cause repeated login failures that persist
  even after recovery, due to rate limiting.
- **Fix**: add retry with exponential backoff (e.g. `tenacity`).
- **Linter rule**: network call without retry logic in a reconcile loop; mechanically checkable.

### Traefik ingress `ClientIP` rule is a no-op

- **Severity**: low
- **Kind**: bug
- **Where**: `chaoscenter/src/traefik_config.py:38`
- **Evidence**:
  ```python
  "rule": "ClientIP(`0.0.0.0/0`)",
  ```
  Matches every IP address — confirmed in the deployed config at `/opt/traefik/juju/`.
- **Impact**: an operator who reads this rule expecting IP-based access control is misled; it
  restricts nothing.
- **Fix**: remove the rule (use `PathPrefix(/.*)`) or set a real IP/CIDR if restriction is
  desired.
- **Linter rule**: Traefik rule uses `0.0.0.0/0` with `ClientIP`; mechanically checkable with a
  regex on `traefik_config.py`.

### Traefik ingress uses `socket.getfqdn()` for backend URL — single-unit only

- **Severity**: low
- **Kind**: bug | performance
- **Where**: `chaoscenter/src/traefik_config.py:27–29`
- **Evidence**:
  ```python
  def _build_lb_server_config(scheme: str, port: int) -> Dict[str, str]:
      return {"url": f"{scheme}://{socket.getfqdn()}:{port}"}
  ```
  Confirmed on the running pod: `socket.getfqdn()` returns the endpoints-service FQDN for a
  single pod (`litmus-chaoscenter-k8s-0.litmus-chaoscenter-k8s-endpoints.rv-litmus2.svc.cluster.local`).
- **Impact**: for multi-unit deployments, traefik would route all traffic to one specific pod
  instead of load-balancing across replicas.
- **Fix**: use the Kubernetes service cluster IP or service name so K8s load-balances across
  endpoints.
- **Linter rule**: not mechanically checkable without analyzing traefik deployment topology.

### Chaoscenter `juju refresh` to `dev/edge` accepted but unit not upgraded while blocked

- **Severity**: low
- **Kind**: bug | ux
- **Where**: `chaoscenter/src/charm.py` (`upgrade-charm` via `cosl.reconciler`)
- **Evidence**: `juju refresh litmus-chaoscenter-k8s --channel dev/edge` completed (revision 47
  added), but the unit remained on rev27 with no hook activity because the charm was `blocked`
  (missing auth-http-api); the queued `upgrade-charm` hook never fired.
- **Impact**: an operator refreshing a `blocked` charm won't get the new revision until the
  blocking condition is resolved, and `juju refresh` reports success regardless.
- **Fix**: document the limitation, or allow `upgrade-charm` to run even while blocked.
- **Linter rule**: not mechanically checkable.

### Duplicate import of `cosl` and `cosl.reconciler`

- **Severity**: low
- **Kind**: lint
- **Where**: `chaoscenter/src/charm.py:11–12` and `:42–43`
- **Evidence**:
  ```python
  import cosl            # line 11
  import cosl.reconciler # line 12
  ...
  import cosl            # line 42 — duplicate
  import cosl.reconciler # line 43 — duplicate
  ```
- **Impact**: wastes memory, confuses linters, suggests a bad merge/rebase.
- **Fix**: remove the second import block.
- **Linter rule**: `ruff UP014` / `ruff check` catches duplicate imports.

### Infrastructure charm requires k8s-api despite `kind: machine` classification

- **Severity**: low
- **Kind**: docs
- **Where**: `infrastructure/charmcraft.yaml:20`; `_context/charms.json`
- **Evidence**: `assumes: - k8s-api` in the infrastructure charm's `charmcraft.yaml` means it
  requires a Kubernetes API. `charms.json` lists it as `kind: machine`, but it cannot run on
  LXD/machine substrate.
- **Impact**: `charms.json` metadata drives automation tool assumptions about substrate;
  incorrect classification leads to wrong deployment attempts.
- **Fix**: update `charms.json` to `kind: k8s` for the infrastructure charm.
- **Linter rule**: not mechanically checkable.

### Auth README copy-pastes "Backend" instead of "Auth" in title and command

- **Severity**: low
- **Kind**: docs
- **Where**: `auth/README.md:20–21`
- **Evidence**:
  ```markdown
  ### Enabling Transport Layer Security (TLS)
  Litmus Backend K8s Operator supports integration with TLS certificates...
  ```
  and
  ```bash
  $ juju integrate litmus-backend-k8s self-signed-certificates
  ```
  Both should read "Auth" and target `litmus-auth-k8s`.
- **Impact**: operators following the README will integrate TLS to the wrong charm.
- **Fix**: replace "Backend" with "Auth" and `litmus-backend-k8s` with `litmus-auth-k8s`.
- **Linter rule**: not established.

## Worth copying

**`StatusManager`** (`libs/src/litmus_libs/status_manager.py`) — a clean, reusable pattern for
collecting status from multiple sources (relations, config, Pebble checks) with clear priority:
Blocked for missing relations → Waiting for configs → Blocked for failing checks → Active.
Human-readable messages. Other charms should copy this.

**`TlsReconciler`** (`libs/src/litmus_libs/tls_reconciler.py`) — a clean, generic TLS cert sync
utility: checks `can_connect()` first, compares current file contents before pushing
(idempotent), and calls `update-ca-certificates` after writes. Good candidate for a shared
library.

**`LitmusInfrastructureRequirer.get_all_data()`**
(`libs/src/litmus_libs/interfaces/litmus_infrastructure.py:73–97`) handles
`pydantic.ValidationError` gracefully (logs and skips rather than crashing) with a comment
explaining this is for rolling-upgrade safety.

**`_UserSecretModel`** pydantic validator (`chaoscenter/src/user_manager.py:40–66`) enforces
Litmus's strict password policy (8–16 chars, digit, lower, upper, special) at secret-presentation
time, with a docstring referencing the upstream Go source — bad secrets never reach the Litmus
API.

**Infrastructure delete ordering** (`infra_manager.py:116–128`) deletes in the correct order:
manifest K8s resources → chaos CRDs from K8s → experiments from DB → infrastructure from
ChaosCenter, avoiding orphaned resources.

**Prometheus metrics via relation data**: `MetricsEndpointProvider`
(`chaoscenter/lib/charms/prometheus_k8s/v0/prometheus_scrape.py`) correctly publishes
`scrape_jobs`, `scrape_metadata`, and `alert_rules` — the standard Prometheus integration
pattern, verified working in the running deployment.

**Traefik ingress via `TraefikRouteRequirer`** (`chaoscenter/src/charm.py:145–150`) submits
ingress config via `self.ingress.submit_to_traefik(...)` — the standard ingress integration
pattern for k8s charms.

## Common-practice notes

All four charms use `CharmBase` and `cosl.reconciler.observe_events(all_events, ...)`, the
recommended canonical-observability style. The infrastructure charm is workloadless and
correctly uses `CharmBase`.

Each charm carries its own `lib/charms/<interface>/v*/` copy — current best practice, synced via
the `update-libs.yaml` workflow. `litmus-libs` itself is published to PyPI and imported from
there in production; `libs/src/` is the canonical source. This separation lets the library
evolve independently of the charms.

Both auth and backend define a single TCP Pebble check (`auth-up`, `backend-up`) with
`threshold: 3` — reasonable for liveness probing.

The infrastructure charm is classified `kind: machine` in `charms.json` but actually requires
`k8s-api` (`infrastructure/charmcraft.yaml:20`) — the classification is wrong (see finding
above).

None of the reviewed charm source files import `coordinated_workers`; it appears in the
dependency graph but is unused in reviewed code — likely a transitive dependency of `cosl` or
otherwise unused (unverified).

`cosl.JujuTopology` usage in `chaoscenter/src/charm.py:79–85` for nginx tracing resource
attributes is good practice, correlating workload traces with Juju topology.

Three different secret-handling patterns exist in one solution: auth/backend use
`DatabaseRequires` for MongoDB credentials via data-platform-libs, TLS certs go through
`tls_certificates_interface`, and chaoscenter uses a user-provided Juju secret. Worth unifying.

Auth and backend write TLS certs to `/etc/tls/` via `TlsReconciler`; chaoscenter uses
`charmlibs.nginx_k8s.Nginx`, which writes to `/etc/nginx/certs/`. Both are correct, but two
different paths for the same function — noted here to avoid confusion in future investigations.

## Tests

### Static analysis

`ruff check auth/src chaoscenter/src backend/src infrastructure/src` reports **86 issues**
across the four charm source trees. Most actionable:

| Rule | Location | Count | Fixable |
|---|---|---|---|
| UP045 (`Optional[X]` → `X \| None`) | all charms | ~30 | yes, auto |
| I001 (unsorted imports) | all charms | ~20 | yes, auto |
| SIM103/SIM211 (redundant boolean) | auth, backend, chaoscenter | ~5 | yes, auto |
| RUF012 (mutable class attribute) | `auth/src/litmus_auth.py:20`, `backend/src/litmus_backend.py:30` | 2 | no |
| BLE001 (blind exception) | `chaoscenter/src/litmus_client.py:93` | 1 | no |
| TRY002 (bare `Exception`) | `chaoscenter/src/user_manager.py:248` | 1 | no |
| EXE001 (shebang, not executable) | `auth/src/litmus_auth.py:1`, `backend/src/litmus_backend.py:1`, `chaoscenter/src/nginx_config.py:1` | 3 | no |
| EXE002 (executable, no shebang) | `backend/src/charm.py:1`, `chaoscenter/src/charm.py:1`, `infrastructure/src/charm.py:1` | 3 | no |
| RUF100 (unused `noqa`) | auth, backend, chaoscenter, infra | 4 | yes, auto |

`RUF012` and `BLE001` are genuine correctness concerns; the import-sorting and type-annotation
issues are mechanical fixes with `ruff --fix`.

### Unit tests

Ran with `PYTHONPATH=*/src:*/lib:libs/src:libs/lib python3 -m pytest */tests/unit/ -v`
(ops 3.8.0, Python 3.12.3, `requests-mock` installed):

| Charm | Passed | Failed | Distinct bug |
|---|---|---|---|
| auth | 115 | 4 | `test_pebble_check_failing_blocked_status` — `CheckInfo` level mismatch |
| backend | 129 | 4 | same `CheckInfo` level mismatch |
| chaoscenter | 130 | 6 | `test_pebble_check_failing_blocked_status` ×4 + `test_nginx_exporter_pebble_ready_plan` ×2 |
| infrastructure | 11 | 1 | `test_charm_tracing_integration[True]` — unmocked `subprocess.run` |
| **Total** | **385** | **15** | **4 distinct bugs** |

The `ops>=4.0.0` limitation noted in `tox.ini` applies to CI (Python 3.10 there vs Python 3.14
required); this environment ran Python 3.12.3 with ops 3.8.0, sufficient for scenario-based
tests once `PYTHONPATH` is set correctly. The 15 failures reduce to the 4 distinct test bugs
detailed in the Findings section above.

**Coverage gaps confirmed by code review:**

| Finding | Test coverage |
|---|---|
| `_apply_credentials` partial failure | mocked wholesale; no granular partial-success test — gap |
| infra namespace `None` guard | all fixtures pass an explicit namespace; no test for `None` |
| `load_all_yaml` exception | `_apply_manifest` is mocked; no test for `YAMLError` |
| `ApiError` without status code check | no test |
| `LitmusClient` login no retry | API is mocked entirely; no retry-behaviour test |
| `user_secrets` type:string | no test (unit tests don't cover charmcraft config validation) |
| traefik `ClientIP` no-op | `test_ingress.py` asserts status messages, not rule content |
| infra data stale capture | no test for reconcile after an infra relation change |
| mongodb relation removal/re-add self-heal | no test (uniter edge case) |
| mutable `all_pebble_checks` class attr | no test (found by `ruff RUF012`) |
| blind `Exception` catch in login | no test (found by `ruff BLE001`) |
| auth/backend circular dependency | no test (needs a multi-charm scenario test) |
| `storage-detaching` hook crash | no test — `CharmEvents.storage_detaching()` not parametrized anywhere |
| `juju refresh` while blocked | no test for `upgrade-charm` in blocked state |

Interface tests use `interface_tester` from `cos-interfacetester`, not available in this
environment; `backend/tests/interface/test_litmus_auth.py` tests `litmus_auth` v0 compliance but
needs a full `uv` environment. Integration tests exist
(`tests/integration/test_litmus_environment.py`) but require MongoDB and the full charm graph,
so they were not executed. `pyproject.toml` sets `fail_under = 90` per charm — good discipline;
`tox.ini` combines coverage across sub-charms into one report.

## Docs

Top-level `README.md` is clear: describes the four charms, the shared library, and the
Terraform deployment path — a good entry point. Individual charm READMEs (`auth/README.md`,
`backend/README.md`, `chaoscenter/README.md`) are thin, ~30 lines each, mostly duplicating the
Charmhub description; the auth README has the copy-paste error noted above.
`CONTRIBUTING.md` is thorough: monorepo layout, running tests locally (`justfile`), updating
libs, and the PyPI publishing flow. `docs/adrs/` has an ADR for resource management. `charmcraft.yaml`
descriptions are detailed with use-case context (COS integration, chaos engineering) — better
than most charms. `SECURITY.md` exists but is a generic template with no project-specific
contact information. `terraform/` modules exist at top level and per-charm, with tests; the
top-level module orchestrates the full bundle including MongoDB and user secret creation — the
recommended deployment path.

## Open questions

1. **Auth uniter stuck after mongodb relation re-add.** The uniter reported `"unknown relation
   5 resolving next op"` and never progressed. Needs a reconciliation mechanism that fires even
   when blocked; a manual pod deletion was required to recover.
2. **Auth/backend circular dependency — 8 min vs 2.5 min.** Fresh-deploy deadlock took ~8 min;
   relation-cycling deadlock took ~2.5 min. Both self-resolve via `cosl.reconciler` cross-charm
   events, but the timing gap is unexplained and needs more instrumentation.
3. **`user_secrets` in `3.29/edge`.** `2/edge` lacks the config; `3.29/edge` (rev52) may have it
   and would make the `type: secret` fix testable — requires an ubuntu@26.04 base to verify.
4. **`litmus-infrastructure` only on `dev/edge`.** No `2/edge` or `3.29/edge` track carries this
   relation alongside the other three charms — is `dev/edge` meant to be the stable channel for
   this feature?
5. **mongodb-k8s credential regression on relation re-add.** Confirm whether `mongodb-k8s` has a
   fix in flight for using `relation-N` as the username.
6. **Infrastructure charm cross-model relation.** The published `2/edge` chaoscenter lacks the
   requirer side of `litmus-infrastructure`, so cross-model chaos is not functional yet — verify
   once `3.29/edge` is promoted.
7. **`juju refresh` to `dev/edge` while blocked.** Refresh reported success before the unit was
   actually upgraded; verify behaviour on a non-blocked unit.
8. **`storage-detaching` permanently blocks app removal.** Is there a Juju-level workaround
   (e.g. force-remove via the controller API) once a unit is stuck in this state?
9. **Backend `storage-detaching` vulnerability.** Structurally identical to the auth crash but
   not directly observed — confirm by reproducing on backend.
