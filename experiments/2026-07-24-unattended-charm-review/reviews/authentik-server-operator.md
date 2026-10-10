# authentik-server-operator

A well-structured Kubernetes charm that deploys Authentik Server 2026.5.x — a flexible open-source identity provider supporting OAuth2/OIDC, SAML, and LDAP. The codebase is solid: centralized reconciliation, thorough scenario tests (151 unit tests, all passing), proper ops patterns, and careful API correctness work. Three findings demand immediate attention: a `_restart_service()` that silently fails to restart the workload after pebble layer changes (env vars stale), a traefik-k8s behaviour that marks HTTPS as available before TLS cert arrives (a traefik-k8s bug with direct consequences for this charm), and an unvalidated `log_level` config that causes a silent service crash loop. The library code also has 4 Ruff formatting violations. All are fixable without architectural change.

| | |
|---|---|
| Repo | canonical/authentik-server-operator @ ea2a0e9 (2026-07-24) |
| Charms | authentik-server |
| Substrate | k8s |
| Deployed | yes — `concierge-k8s-3`, channel `latest/edge` rev 29 |
| Reviewed | 2026-08-17 |

## What it does

Manages the Authentik Server application lifecycle on Kubernetes. Required relations: PostgreSQL (data), Traefik (ingress), Authentik Worker (cluster). Optional: SMTP, Loki/Prometheus/Grafana/Tempo (observability), self-signed-certificates (TLS CA), OAuth clients (provider). Exposes `metrics-endpoint`, `grafana-dashboard`, `authentik-cluster` (provider), `authentik-server-info` (provider), and `oauth` (provider). Actions: `get-bootstrap-admin-credentials` and `create-recovery-link`. The charm generates bootstrap credentials on first leader election and stores them in a Juju secret whose ID lives in the peer relation app databag.

## Deployment log

**Deployment 3 (model `rv-authentik-full`, controller `concierge-k8s-3`):**

```bash
# Created model, deployed all charms, integrated everything
juju add-model rv-authentik-full --controller concierge-k8s-3 k8s
juju deploy authentik-server --channel latest/edge --trust
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy traefik-k8s --channel latest/stable --trust
juju deploy authentik-worker --channel latest/edge --trust
juju deploy self-signed-certificates --channel latest/stable --trust
juju deploy grafana-agent-k8s --channel 1/stable --trust
juju config traefik-k8s juju-external-hostname=10.43.45.0
juju integrate postgresql-k8s authentik-server
juju integrate self-signed-certificates:certificates traefik-k8s:certificates
juju integrate traefik-k8s authentik-server:traefik-route
juju integrate authentik-server:authentik-cluster authentik-worker:authentik-cluster
juju integrate grafana-agent-k8s:metrics-endpoint authentik-server:metrics-endpoint
```

Sequence observed:
- 04:50 — Agents installing
- 04:51 — postgresql-k8s doing rolling restart; authentik-server waiting for database creation
- 04:54 — Database ready; authentik-server migrations running; pebble check DOWN (503)
- 04:55 — Pebble check recovered; charm active
- 04:58 — Manual `pebble stop authentik-server` → `waiting / waiting for the service to start`
- 05:05 — `juju config log_level=NOT_A_VALID_LEVEL` → service crash loop
- 05:06 — Reverted config to `info` → self-recovery via pebble check recovered
- 05:09 — Service stopped again → `waiting / waiting for the service to start`
- 05:10 — Manual `pebble start` → pebble check recovered → `active`
- 05:11 — Application removed → authentik-worker correctly blocked "missing authentik-cluster relation"

**Deployment 4 (model `rv-ak-deep`, same controller, extended tests):**

Full integration stack: authentik-server + postgresql-k8s + traefik-k8s + authentik-worker + self-signed-certificates + grafana-agent-k8s.

```bash
# Service stop/recovery cycle
kubectl exec ... -- pebble stop authentik-server
# → authentik-pebble-check-failed fires; _on_pebble_check_failed logs warning; unit transitions
#   to waiting via periodic collect_unit_status; manual pebble start required

# DB relation removal while running
juju remove-relation authentik-server:pg-database postgresql-k8s:database
# → immediately blocked "missing pg-database relation"; service stopped; re-integrate works

# Scale to 3 units
juju scale-application authentik-server 3
# → all 3 units active within 60s

# Scale down
juju scale-application authentik-server 1
# → clean scale-down, units terminated cleanly

# create-recovery-link action
juju run authentik-server/0 create-recovery-link
# → returns https://10.43.45.0/recovery/use-token/... (HTTPS despite no TLS cert)
```

## Observed behaviour

**Lifecycle sequence (new deployment):**
1. 04:50:16 — Agents downloading
2. 04:51:25 — authentik-server: traefik-route-relation-changed → Maintenance → Blocked (traefik not HTTPS)
3. 04:52:44 — pg-database-relation-joined
4. 04:52:47 — pg-database-relation-changed → Maintenance → waiting for database creation
5. 04:53:07 — waiting for database creation
6. 04:54:20 — pg-database-relation-changed → Maintenance → waiting for the service to start
7. 04:54:24 — authentik-peers-relation-changed → Maintenance → waiting for the service to start
8. 04:54:52 — authentik-pebble-check-failed → waiting / "running database migrations"
9. 04:54:56 — `/-/health/ready/` returning 503 during migrations
10. 04:55:33 — authentik-pebble-check-recovered → Maintenance → active
11. 04:56:25 — `get-bootstrap-admin-credentials` action succeeds
12. 04:56:26 — `create-recovery-link` action succeeds, returns `https://10.43.45.0/recovery/use-token/...` (broken URL — see finding)

**Service stop and recovery (extended from Deployment 4):**
- `pebble stop authentik-server` → `authentik-pebble-check-failed` fires → unit stays `active` for a period via `collect_unit_status` caching → eventually transitions to `waiting / waiting for the service to start` via periodic status collection
- `_on_pebble_check_failed` only logs "The authentik service is not running" (a warning, no status change)
- `authentik-pebble-check-recovered` fires after manual `pebble start` → `_on_holistic_handler` re-runs full reconciliation (service was already started manually, so the reconciliation just re-applies the pebble layer)
- Charm has no automatic restart mechanism — manual `pebble start` is required

**Traefik HTTPS without TLS certificate (Deployment 4):**
- traefik-k8s status: `active` with "Certificate not available yet"
- traefik debug log shows entry points `["web","websecure"]` and router TLS config `{"domains":[{"main":"10.43.45.0"}]}`
- traefik is listening on HTTPS but has no valid certificate
- `create-recovery-link` returns `https://10.43.45.0/recovery/use-token/...` — the URL is inaccessible
- This confirms the traefik-k8s bug: `scheme: https` is published before the certificate is available

**Database removal while running (Deployment 4):**
- `juju remove-relation` → immediately `blocked / missing pg-database relation` ✓
- Pebble service stops (inactive) via `_on_database_relation_broken` → `container.stop()`
- `juju integrate postgresql-k8s authentik-server` → clean re-integration → migrations → `active` ✓

**grafana-agent-k8s integration (Deployment 4):**
- `metrics-endpoint` relation IS established (confirmed in `juju status --relations`)
- grafana-agent-k8s status: `blocked / Missing ['grafana-cloud-config']|['send-remote-write'] for metrics-endpoint`
- The `metrics-endpoint` integration alone is not sufficient — grafana-agent-k8s additionally requires either a `grafana-cloud-config` integration or `send-remote-write` to become active
- This is expected — the relation provides the scrape target, but the agent needs somewhere to send the data

**Scale up and down (Deployment 4):**
- `juju scale-application authentik-server 3` → all 3 units `active` within 60s ✓
- `juju scale-application authentik-server 1` → units terminated cleanly ✓
- Each unit has its own pebble layer with identical credentials (shared via peer relation) ✓

**Actions (all verified in Deployment 4):**
- `get-bootstrap-admin-credentials` → returns username, password, bootstrap-token, warning ✓
- `create-recovery-link` → returns URL with HTTPS scheme (broken — no TLS cert) ✓

**Application removal:**
- `juju remove-application authentik-server --force` → authentik-worker correctly goes `blocked / missing authentik-cluster relation` ✓

**Pebble layer structure (observed from all units):**
- `authentik-server` service: `startup: disabled`, `override: replace`, command `/lifecycle/ak server`
- `server` and `worker` services from the rock layer: `startup: disabled`, same commands
- The charm's `authentik-server` service overrides the rock's `server` service with a combined layer containing all env vars
- The `ready` check: `/-/health/ready/`, threshold 3 (30s grace), timeout 10s
- The `alive` check: `/-/health/live/`, threshold 15 (150s grace)

## Findings

### Service does not self-recover from pebble-check-failed
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:503` — `_on_pebble_check_failed`
- **Evidence**:
  ```python
  def _on_pebble_check_failed(self, event: ops.PebbleCheckFailedEvent) -> None:
      if event.info.name == PEBBLE_READY_CHECK_NAME:
          logger.warning("The authentik service is not running")
  ```
  The handler only logs a warning and takes no action. Observed: after `pebble stop authentik-server`, the `authentik-pebble-check-failed` hook fires, the handler logs "The authentik service is not running", the unit stays `active` briefly via status collection caching, then transitions to `waiting / waiting for the service to start` via the periodic `collect_unit_status` tick. Manual `pebble start` was required to recover. After the manual start, `_on_pebble_check_recovered` fires and `_on_holistic_handler` re-runs full reconciliation (service was already running, so the reconciliation just re-applies the pebble layer with no restart needed).
- **Why it matters**: Any process crash, SIGKILL from OOM, or manual service stop leaves the charm stuck in `waiting` indefinitely. The operator must intervene manually. This breaks self-healing for the charm's core workload.
- **Fix**: Add `self._container.start(WORKLOAD_SERVICE)` inside `_on_pebble_check_failed`. The pebble layer is already applied; starting the service is sufficient.
- **Linter rule**: not mechanically checkable

### `_restart_service()` calls `replan()` instead of `restart()` for non-TLS env changes
- **Severity**: high
- **Kind**: bug
- **Where**: `src/services.py:213` — `_restart_service`
- **Evidence**:
  ```python
  def _restart_service(self, restart: bool = False) -> None:
      if restart:
          self._container.restart(WORKLOAD_SERVICE)
      elif not self._container.get_service(WORKLOAD_SERVICE).is_running():
          self._container.start(WORKLOAD_SERVICE)
      else:
          self._container.replan()
  ```
  `plan()` at `services.py:220` calls `self._restart_service(restart=force_restart)` where `force_restart=self._tls_cert_changed`. From `src/charm.py:385-430`, `_tls_cert_changed` is only set True when CA certificates change. For all other env var updates (database credentials, config, secrets), `force_restart=False` and `_restart_service(False)` falls to `replan()`. Per Pebble semantics, `replan()` only restarts services whose command or user changed — environment variable changes in the pebble layer are not considered "changed", so `replan()` does not restart the service. The service continues running with old environment variables.
- **Why it matters**: Any pebble-layer env-var update (DB password rotation, config changes, new secrets) does not take effect unless TLS also changed. The service crashes because it has stale credentials while pebble believes everything is healthy. This caused the migration restart loop observed in Deployment 2.
- **Fix**: Change the `else` branch at `services.py:213` from `self._container.replan()` to `self._container.restart(WORKLOAD_SERVICE)`. `add_layer(..., combine=True)` in `plan()` is idempotent, so a full restart is safe regardless of whether the layer changed.
- **Linter rule**: A rule flagging `container.replan()` in restart contexts where the layer may contain env var changes would catch this.

### "running database migrations" shown for non-migration failures
- **Severity**: high
- **Kind**: bug
- **Where**: `src/services.py:162` — `WorkloadService.check_health`
- **Evidence**: When `ready_check.status == CheckStatus.DOWN`, `check_health()` unconditionally calls `self._cli.check_migrations()`:
  ```python
  if ready_check.status == CheckStatus.DOWN:
      self._cli.check_migrations()
  if ready_check.status != CheckStatus.UP or (ready_check.successes or 0) == 0:
      raise WorkloadNotRunningError("Service is starting up")
  ```
  `check_migrations()` runs `manage.py migrate --check` with `service_context=WORKLOAD_SERVICE`. When the service is stopped or crashed, this command fails with "Secret key missing" (no env vars in context) and exits with code 1. The charm interprets this as "migrations pending":
  ```python
  except ExecError as e:
      if e.exit_code == 1:
          raise MigrationPendingError("running database migrations") from e
  ```
  Result: operator sees "running database migrations" with no indication of the real cause.
- **Observed**: After `juju config log_level=NOT_A_VALID_LEVEL`, the service crashed and the status became `waiting / running database migrations`. No migrations were running.
- **Why it matters**: The operator wastes time investigating migrations when the real problem is a bad config or service crash. The misleading status delays diagnosis.
- **Fix**: Move the `check_migrations()` call to only run when the service is actually running (`is_running()` check before the call). Add a message distinguishing "migrations running" from "service not responding".
- **Linter rule**: not mechanically checkable

### Traefik-k8s marks HTTPS scheme before TLS certificate is available
- **Severity**: high
- **Kind**: bug
- **Where**: traefik-k8s `src/charm.py` `_is_tls_enabled()` (external, but observable in this charm)
- **Evidence**: The `traefik-route` relation data shows `scheme: https` while traefik-k8s still reports "Certificate not available yet". traefik debug log confirms entry points `["web","websecure"]` with no valid certificate. `create-recovery-link` returns `https://10.43.45.0/recovery/use-token/...` — a URL that the operator cannot access. The traefik-k8s code: `if self.model.relations.get(CERTIFICATES_RELATION_NAME): return True` (any certificates relation → TLS enabled, regardless of cert issuance state).
- **Why it matters**: In any deployment where a `certificates` relation is established before the certificate is issued, the authentik charm publishes HTTPS URLs that are inaccessible. Consumers get broken OAuth endpoints and recovery links.
- **Fix**: The authentik charm should independently verify that HTTPS is functional before publishing `https://` URLs. Probe the traefik endpoint with `curl -k https://<external_host>/` or rely on the `certificate_transfer` integration for TLS verification. Document that a TLS cert must be available before traefik-route integration is considered secure.
- **Linter rule**: not mechanically checkable (requires runtime verification)

### Invalid `log_level` config causes silent service crash with no error status
- **Severity**: medium
- **Kind**: bug
- **Where**: `charmcraft.yaml` (no schema validator) and `src/configs.py:18`
- **Evidence**: `charmcraft.yaml` describes valid values (`debug`, `info`, `warning`, `error`, `trace`) but specifies no `enum` validator. Any string is accepted via `juju config`. `AUTHENTIK_LOG_LEVEL=NOT_A_VALID_LEVEL` → Authentik's Django startup raises `ValueError: Unable to configure logger ''` → `/lifecycle/ak server` exits with status 1 → crash loop. No `PebbleError` is raised, so the charm stays in `waiting / "running database migrations"` (misleading) with no indication of the root cause.
- **Why it matters**: An operator who mistypes `log_level` will not be alerted. The service silently fails and restarts indefinitely.
- **Fix**: Add an `enum` validator to `charmcraft.yaml` for `log_level` accepting only the documented values. Alternatively, catch the `ValueError` in the pebble layer command wrapper and surface it as a `BlockedStatus`.
- **Linter rule**: A charmcraft.yaml validator (or a lint rule checking `type: string` with no `enum` where the description enumerates values) would catch this.

### No unit test for "traefik-route not secure" blocking pebble layer application
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py` and `tests/unit/conftest.py:133`
- **Evidence**: The `all_satisfied_conditions` autouse fixture mocks `traefik_route_is_secure` to `True`, so the critical path where `_ensure_traefik_route` returns `False` → `can_plan=False` → pebble layer not applied is never exercised in scenario tests. No test variant exists with `traefik_route_is_secure` mocked to `False`.
- **Why it matters**: This is the exact scenario that caused the workload to remain inactive in the first deployment. Without a test, a future code change that accidentally removes this gate would not be caught.
- **Fix**: Add `test_traefik_not_secure_blocks_pebble_layer` with `traefik_route_is_secure` mocked `False` and assert that `pebble.plan()` is not called.
- **Linter rule**: not mechanically checkable

### `authentik_pebble_check_recovered` re-runs full reconciliation
- **Severity**: medium
- **Kind**: performance / correctness
- **Where**: `src/charm.py:506` — `_on_pebble_check_recovered`
- **Evidence**:
  ```python
  def _on_pebble_check_recovered(self, event: ops.PebbleCheckRecoveredEvent) -> None:
      if event.info.name == PEBBLE_READY_CHECK_NAME:
          logger.info("The authentik service is online again")
          self._on_holistic_handler(event)
  ```
  Calls `_on_holistic_handler` which re-runs the full reconciliation (secrets, cluster relation, traefik, server-info, TLS, OAuth). On a normal service restart, all relations are already established and the pebble layer is unchanged. The only thing that genuinely needs re-running is the server-info publication (gated on API readiness).
- **Why it matters**: On every recovery, full reconciliation runs again. This is expensive and causes unnecessary hook executions.
- **Fix**: Replace the full `_on_holistic_handler` call with a targeted `_ensure_server_info_relation` call, or document why full reconciliation is needed on every recovery.
- **Linter rule**: not mechanically checkable

### Ruff formatting violations in owned library files
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/authentik_server/v0/authentik_cluster.py:100,346` and `lib/charms/authentik_server/v0/authentik_server_info.py:97,165`
- **Evidence**: `ruff check lib/` reports:
  - `authentik_cluster.py:100`: "Expected 2 blank lines, found 1" before `AuthentikClusterReadyEvent`
  - `authentik_cluster.py:346`: "No newline at end of file"
  - `authentik_server_info.py:97`: "Expected 2 blank lines, found 1" before `AuthentikServerInfoReadyEvent`
  - `authentik_server_info.py:165`: "Too many blank lines (2)" before `_delete_secrets`
- **Why it matters**: Libraries ship independently; CI lint runs fail. Fixable with `ruff check --fix`.
- **Fix**: Run `ruff check --fix lib/` or fix blank-line counts manually.
- **Linter rule**: `ruff (E3/W2)` — mechanically checkable with `ruff check`

### `PebbleError` swallowed without propagating status
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:277` — `_holistic_handler`
- **Evidence**:
  ```python
  try:
      self._pebble.plan(self._pebble_layer, force_restart=self._tls_cert_changed)
  except PebbleError:
      logger.error("Failed to plan pebble layer, ...")
  ```
  The exception is caught and logged. The unit stays in whatever status was set before (typically `Maintenance("Configuring resources")`) indefinitely without a clear operator-visible status.
- **Why it matters**: If pebble fails (layer syntax error, socket error), the operator sees "Configuring resources" forever with no indication of what to do.
- **Fix**: Add `self.unit.status = ops.BlockedStatus("Pebble layer planning failed, check container logs")` inside the except block.
- **Linter rule**: A rule checking for caught exceptions that don't update unit status would catch this.

### `CharmConfig.get_missing_config_keys` always returns empty list
- **Severity**: low
- **Kind**: bug
- **Where**: `src/configs.py:35`
- **Evidence**: Method is a no-op stub. `charmcraft.yaml` has no required config options (all have defaults), so this is not causing practical failures — but if a required option is added in future, this method will silently not work.
- **Why it matters**: Adding a required config option will not trigger the blocked status.
- **Fix**: Implement `get_missing_config_keys` or remove the dead code block from `_on_collect_status`.
- **Linter rule**: A rule flagging `return []` in methods called from event handlers would catch this.

### `_authentik_host` returns internal URL when traefik is not yet ready
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:221` — `_authentik_host`
- **Evidence**: Returns `self._internal_url` = `http://authentik-server.{model}.svc.cluster.local:9000` when traefik is not ready. `_publish_provider_info` uses this for all OAuth endpoints. `_ensure_oauth_relation` is gated on `is_running()`, so OAuth reconciliation is gated, but `_authentik_host` itself is not guarded on traefik-route being ready.
- **Why it matters**: If `create-recovery-link` is called before traefik is ready, the returned URL uses the internal HTTP URL. OAuth endpoints published to the relation would be `http://` if the traefik scheme is ever `http`.
- **Fix**: Gate `_authentik_host` on `traefik_route_is_ready`, or return `None` when traefik is not ready and have callers handle that case. Add a unit test for this scenario.
- **Linter rule**: not mechanically checkable

### grafana-agent-k8s blocked despite established metrics-endpoint relation
- **Severity**: info
- **Kind**: ux
- **Where**: grafana-agent-k8s integration (external charm)
- **Evidence**: `juju status` confirms `metrics-endpoint` relation IS established between authentik-server and grafana-agent-k8s. grafana-agent-k8s is `blocked / Missing ['grafana-cloud-config']|['send-remote-write'] for metrics-endpoint`. This means the `metrics-endpoint` integration alone is insufficient — grafana-agent-k8s additionally requires a `grafana-cloud-config` or `send-remote-write` integration to become active.
- **Why it matters**: An operator might expect grafana-agent-k8s to become active after integrating the `metrics-endpoint` relation. The additional requirement is not visible from the authentik-server side. This is expected behavior for grafana-agent-k8s, but the documentation could make this clearer.
- **Linter rule**: not applicable (external charm behaviour)

### No upgrade path defined
- **Severity**: info
- **Kind**: test-gap / docs
- **Where**: `charmcraft.yaml` (no `upgrade-path` key)
- **Evidence**: `charmcraft.yaml` has no `upgrade-path` key. The charm has no `on_upgrade_charm` handler. A `juju refresh` would trigger a full charm re-install without any special handling.
- **Why it matters**: While this may be intentional (stateless reconciliation handles upgrades), it means the upgrade path has not been explicitly tested or documented. The pebble layer would be re-applied on every refresh, which should work — but the upgrade scenario has not been verified.
- **Linter rule**: not mechanically checkable

### Database relation removal immediately goes `blocked`, services stop cleanly
- **Severity**: info
- **Kind**: ux
- **Where**: `src/charm.py:513` — `_on_database_relation_broken`
- **Evidence**: `juju remove-relation authentik-server:pg-database postgresql-k8s:database` → `blocked / missing pg-database relation` appears within seconds. `_on_database_relation_broken` calls `self._container.stop(WORKLOAD_SERVICE)`. Re-integration: migrations run → `active`. Correct behaviour.
- **Why it matters**: This is the intended behaviour — the operator is immediately informed of the broken dependency. The graceful stop of the pebble service is also correct.
- **Linter rule**: not applicable (this is a positive finding)

### Service start-up state with `startup: disabled`
- **Severity**: info
- **Kind**: ux
- **Where**: `src/services.py:41` — `PEBBLE_LAYER_DICT`
- **Evidence**: The pebble layer defines `authentik-server` with `startup: disabled`. The service is started by the charm via `pebble start`. When the charm is not reconciling (between status collection ticks), the pebble layer is not re-applied and the service stays in whatever state it was last set to. After `pebble stop`, the service remains stopped.
- **Why it matters**: This is the correct design for a charm-managed service, but the lack of self-recovery after a service stop is the consequence of this design choice combined with the `_on_pebble_check_failed` handler doing nothing.
- **Linter rule**: not applicable (this is a design note)

## Worth copying

- **Centralized reconciliation handler** (`_holistic_handler` in `src/charm.py:257`): A single method that all events funnel into, with explicit NOOP conditions and per-step error handling. `AuthentikTransientError` re-raise ensures Juju retries on transient failures.
- **NOOP conditions as explicit callable list** (`src/utils.py:38`): `NOOP_CONDITIONS` as a tuple of callables checked before reconciliation — clean and extensible.
- **AuthentikAPI client with typed errors and bounded retries** (`src/authentik_api.py`): `_do_request` → `_raise_for_terminal_status` with `RETRYABLE_SERVER_STATUSES`. Bounded retry with exponential backoff.
- **OAuth reconciler with deterministic identity** (`src/oauth.py`): `config_hash` approach for change detection, discover-by-exact-name recovery for 409 errors.
- **Scenario/state-transition unit tests** (`tests/unit/`): All 151 tests use `ops.testing.Context` with direct assertions on output state. `create_state` factory with per-fixture overrides is excellent for readability.
- **Library tests with minimal test charm classes** (`tests/unit/test_libs.py`): Each library tested through purpose-built test charm classes.
- **Server-info publication gated on API readiness** (`src/charm.py:354`): Only published once `api.is_service_available()` returns True.
- **`AuthentikClusterProvider._on_relation_broken` preserves secrets while relations remain** (`lib/charms/.../authentik_cluster.py:178`): Secret revoked per-relation while others remain; fully deleted only when the last relation is removed.
- **`remove_integration` fixture with tenacity retry** (`tests/integration/utils.py`): Handles the "dying relation" edge case during re-integration in integration tests.
- **Peer relation for secret ID sharing** (`src/integrations.py:156`): `PeerData` class provides a clean abstraction for JSON-serialized app-level peer data, used to store the Juju secret ID without relying on label lookups.

## Common-practice notes

- **`charmcraft.yaml` layout**: Follows canonical convention. `charm-user: non-root` is set. No `upgrade-path` key (note: this is common but means upgrades are implicit, not explicitly tested).
- **Library versioning**: Libraries under `lib/charms/authentik_server/v0/` with appropriate LIBPATCH values. Uses Pydantic `BaseModel` with `Field(exclude=True)` for non-serialized fields.
- **`src/` layout**: Each module has single responsibility. Cleaner than flat structure.
- **Secret management**: Single Juju app secret with ID in peer app databag. Standard pattern. Both `authentik_cluster.py` and `authentik_server_info.py` use this pattern independently.
- **`__main__` guard**: Present with `# pragma: nocover`. Convention followed.
- **grafana-agent-k8s integration**: The `metrics-endpoint` relation uses the standard `prometheus_scrape` interface, but grafana-agent-k8s additionally requires a `grafana-cloud-config` or `send-remote-write` integration to become active. This is not specific to this charm but is worth knowing.
- **Traefik `scheme: https` before cert**: The traefik-k8s bug (reporting HTTPS before cert is available) is a common integration issue across charms that use traefik-route. This charm correctly blocks on `traefik_route_is_secure`, but the `create-recovery-link` action bypasses this gate since it uses `_authentik_host` which returns the traefik URL regardless.

## Tests

**Unit tests (151 passed, 77 warnings):**
All tests use `ops.testing.Context` (scenario/state-transition style). Coverage:
- `test_charm.py` (40 tests): Holistic handler, status collection, database events, SMTP, traefik-route, pebble checks, cluster relation, server info relation, TLS, actions
- `test_oauth.py`: OAuth reconciliation with cache, legacy slug handling, idempotent create, garbage collection
- `test_authentik_api.py`: API client with mocked responses, retry logic, typed errors
- `test_services.py`: WorkloadService.is_running, is_failing, check_health
- Per-module tests: `test_configs.py`, `test_integrations.py`, `test_secret.py`, `test_cli.py`
- `test_libs.py`: Library tests via minimal test charm classes

**Gaps in unit test coverage (relative to risks found):**
- "Traefik not secure" → `can_plan=False` → pebble layer not applied (critical path, not tested)
- `_authentik_host` returning internal URL when traefik not ready (not tested)
- `_on_pebble_check_failed` not triggering service restart (not tested)
- `_restart_service()` with `force_restart=False` → `replan()` not `restart()` (theoretically untested, Pebble semantics prevent the restart)
- `check_health()` calling `check_migrations()` when service is down (shows misleading "migrations running" message, not tested)
- TLS `update-ca-certificates` failure path (no unit test with mocked subprocess failure)
- `PebbleError` from `pebble.plan()` (swallowed, not tested)
- `CharmConfig.get_missing_config_keys` always returning empty list (no test with required config)

**Integration tests** (`tests/integration/test_charm.py`):
Uses `jubilant` + pytest with spread. Tests: deploy, health, traefik route YAML, scale up/down, admin actions, remove integration (3 variants: DB, cluster, traefik), remove application. Not runnable in this environment (requires full Juju + Kubernetes). Tests assert actual behaviour (OAuth action return fields, traefik route YAML content) not just `active/idle` waits.

## Docs

- **README.md**: Excellent — covers basic deployment, Terraform, integrations, bootstrap credentials. Matches what is actually deployed.
- **docs/**: Comprehensive guides: getting-started, bootstrap, admin tasks, OIDC/OAuth protection, LDAP, user/group management, architecture, config reference. All accurate from code cross-reference.
- **AGENTS.md**: Detailed testing instructions including concierge setup, tox commands, pre-commit.
- **CHANGELOG.md**: Conventional-commits based, thorough.
- **terraform/**: Terraform module with README, tutorial, MODULE_SPECS. Properly defines all required inputs/outputs.

**Docs gaps:**
- The architecture doc mentions `bootstrap-token` but open issue #62 confirms this is the bootstrap admin token, not a least-privilege automation token. Consumers use it for all API calls.
- No docs on what to do when `blocked / "Requires a secure (HTTPS) public ingress."` — an operator hitting this for the first time would not know to set `juju-external-hostname` on traefik-k8s.
- The `log_level` config description enumerates valid values but does not warn that invalid values cause a silent crash loop.
- grafana-agent-k8s additionally requires a `grafana-cloud-config` or `send-remote-write` integration — the README's observability section should note this.

## Open questions

- **HTTP 418 from Authentik readiness check during first boot**: In the first deployment, `/-/health/ready/` returned 418 (HTTP 418 is an Authentik-specific response). The pebble check threshold of 3 correctly handled this. Is HTTP 418 a known Authentik behaviour during initial startup, or a bug to report upstream?
- **Service self-recovery**: The charm cannot recover from a service stop without manual intervention. Is this intentional (charm relies on Kubernetes restart policy or Pebble auto-restart for crashes)? The `startup: disabled` design suggests the charm expects to control the service lifecycle, but `_on_pebble_check_failed` does nothing.
- **Bootstrap admin token used for server-info**: Open issue #62 is aware of this. The `api_token` in `authentik-server-info` relation is the bootstrap admin token. This is a deliberate tradeoff deferred to a future improvement.
- **`_restart_service()` failure after DB re-integration**: After removing and re-adding the database relation in the earlier deployment, the `authentik-server` service entered a migration restart loop. The root cause appears to be postgresql-k8s rotating the database password during its rolling restart, combined with `_restart_service()` not restarting the service after env var changes.
- **HTTP 503 from `/-/health/ready/` during migrations**: Expected behaviour but the "running database migrations" message is shown when the real cause is a service not responding (not necessarily migrations).
- **`_authentik_host` publishes internal URL to server-info relation**: `server_info_provider.update_relations_app_data(authentik_host=self._internal_url, ...)` at `src/charm.py:358` publishes `http://authentik-server...svc.cluster.local:9000` as the `authentik_host`. This is correct for internal worker→server communication but the `authentik-server-info` relation interface name suggests it could be used by consumers who need the public URL. The traefik-route relation provides the external URL separately, but the interface contract is ambiguous.
- **Traefik HTTPS before cert**: The traefik-k8s bug of publishing `scheme: https` before the TLS certificate is available is confirmed by traefik logs showing `entryPoints: ["web","websecure"]` with "Certificate not available yet". This affects all charms using traefik-k8s, not just this one.
