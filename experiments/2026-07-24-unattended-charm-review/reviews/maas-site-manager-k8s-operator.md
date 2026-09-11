# maas-site-manager-k8s

A Juju sidecar charm deploying MAAS Site Manager (a FastAPI/uvicorn service) on Kubernetes, backed by PostgreSQL, S3, and Temporal. The charm is structurally sound — clean Pebble layer convergence, a well-factored custom exception hierarchy, and a config-driven environment allowlist. But it has multiple correctness defects that will bite operators in normal operation, not just edge cases: certificate transfer is completely broken against `self-signed-certificates` (confirmed in four separate deployments), a scale-up path reports `ActiveStatus` for a crash-looping unit, malformed environment config crashes the charm into an unrecoverable `error` hook, and refreshing from the deployed latest/edge revision to 1.1/beta silently drops Temporal configuration with no migration guidance — and is outright rejected by Juju 4.x controllers. A maintainer should first fix the `pebble-check-failed` status gap and the certificate-transfer v0 fallback, since both produce silently wrong operator-facing state; then add an `upgrade-charm` handler before shipping the next relation-breaking config change.

| | |
|---|---|
| Repo | canonical/maas-site-manager-k8s-operator @ `c0d9ebb` (2026-07-13) |
| Charms | maas-site-manager-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3, latest/edge rev 50 and 1.1/beta rev 53; concierge-k8s-4, latest/edge rev 50 (standalone only, full stack not deployable) |
| Reviewed | 2026-08-04 |

## What it does

MAAS Site Manager centralises image management and monitoring for multiple MAAS installations ("sites"). The charm deploys the MSM FastAPI application in a Kubernetes sidecar container (Pebble-managed). It requires PostgreSQL for metadata, S3-compatible object storage for images, and Temporal for workflow orchestration. Optional integrations include Traefik ingress, Loki logging (via grafana-agent-k8s), Prometheus metrics, Grafana dashboards, Tempo tracing, and certificate transfer for custom CAs. It provides a `maas-site-manager` relation that issues enrollment tokens to MAAS region charms.

The charm has undergone a significant architecture change between the deployed revision 50 (latest/edge) and revision 53 (1.1/beta) / HEAD. Rev 50 uses config options (`temporal-server-address`, `temporal-namespace`, `temporal-task-queue`) for Temporal; rev 53 and HEAD replace these with dedicated relations (`temporal-host-info`, `temporal-worker-info`). There is no `upgrade-charm` event handler to migrate between the two models.

## Deployment log

### Round 1: initial deploy (Juju 3.6 + 4.x)

**Attempt 1 — latest/edge rev 50 on Juju 4.x (concierge-k8s-4):**
```bash
juju add-model rv-msm-deploy
juju deploy maas-site-manager-k8s --channel latest/edge
```
Rev 50 deployed, pod 2/2 Running, charm reached `WaitingStatus("Waiting for database relation")` as expected. `juju deploy postgresql-k8s --channel 14/stable --trust` (and `14/edge`) failed: "charm requires Juju version < 4.0.0". **Finding**: the charm's required dependency is not deployable on Juju 4.x.

**Attempt 2 — latest/edge rev 50 on Juju 3.6:**
```bash
juju add-model rv-msm-k3
juju deploy maas-site-manager-k8s --channel latest/edge   # rev 50
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy s3-integrator --channel latest/stable
juju deploy temporal-k8s --channel 1.23/stable
juju deploy temporal-admin-k8s --channel 1.23/stable
```
Database integrated → "Waiting for s3 integration". S3 integrated → `BlockedStatus("temporal-server-address configuration is required")`, confirming rev 50's config-based Temporal model. Setting `temporal-server-address`/`temporal-namespace`/`temporal-task-queue` produced a service crash-loop (`RuntimeError: Failed client connect … dns error`, then `UnboundLocalError: cannot access local variable 'backoff'` in temporallib's `reconnect_loop` — an upstream workload bug). `msm-admin create-user` also failed, connecting to `localhost:5432` instead of the PostgreSQL service host (rev 50 image bug). Charm ended in `BlockedStatus("Failed to create operator user")`.

**Attempt 3 — 1.1/beta rev 53 on Juju 3.6:** PostgreSQL cluster initialization failed (not attributable to this charm); never reached active.

### Round 2: failure injection (Juju 3.6, rev 50, model `rv-msm-deep`)

```bash
juju add-model rv-msm-deep --controller concierge-k8s-3
juju deploy maas-site-manager-k8s --channel latest/edge      # rev 50
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy s3-integrator --channel latest/stable
juju deploy self-signed-certificates --channel latest/stable
juju deploy traefik-k8s --channel latest/stable --trust
juju deploy grafana-agent-k8s --channel 2/stable
```

Progress through required integrations matched Round 1 (database → s3 → Temporal-config-blocked → crash-loop → "Failed to create operator user"). Additional injections:

- **Bad config**: `log-level=invalid` → `BlockedStatus("invalid log level: '{log_level}'")` — missing f-string prefix, variable name printed literally.
- **Valid config recovery**: `log-level=info` → recovers to `WaitingStatus("Waiting for msm service to become available")`.
- **Certificate transfer**: `self-signed-certificates:send-ca-cert` integrated — relation established, `ca` cert present in unit relation data, but `/usr/local/share/ca-certificates/` **never created** in the workload container. Confirmed in four separate deployments (Rounds 2–3 on Juju 3.6, Juju 4.x standalone test).
- **Ingress**: `traefik-k8s` integrated → URL `http://10.43.45.0/rv-msm-deep-maas-site-manager-k8s` correctly appeared as `MSM_BASE_PATH` in the Pebble layer environment.
- **Observability**: `grafana-agent-k8s` integrated on `metrics-endpoint`, `grafana-dashboard`, `logging-consumer` — all established cleanly, Loki log-targets appeared in the pebble plan.
- **Remove/re-integrate database relation**: clean transitions to/from `WaitingStatus("Waiting for database relation")`, no crash.
- **Scale up to 2 units**: unit 1 reached `ActiveStatus` with an empty message at `16:52:34`, despite `pebble services` showing `msm: backoff` and `pebble checks` showing `http-test: down, 5/3 failures`. The `pebble-check-failed` event fired at `16:53:03` but the charm only handles `pebble-check-recovered` — status was never corrected. Confirmed status-reporting bug.
- **`create-admin` action**: fails with a reasonable error message ("Failed to create user testuser").
- **Malformed `environment` config**: `'[{value: foo}]'` (missing `name` key) → `KeyError` crashes the hook, charm reaches `error` state ("hook failed: config-changed").
- **Invalid variable name**: `'[{name: BAD_VAR, value: foo}]'` → correctly blocked ("Invalid environment variable: BAD_VAR").
- **Empty/non-list/invalid YAML `environment` values** → all correctly blocked with clear messages.
- **Rapid config flips**: five `log-level` changes (info→debug→info→debug→info) all processed, charm settled at `WaitingStatus`.

### Round 3: refresh and deeper failure injection (Juju 3.6, rev 50→53, model `rv-msm-deep2`)

Rev 50 baseline reproduced Round 2's crash-loop/"Failed to create operator user" state; `/usr/local/share/ca-certificates/` confirmed still absent.

**Refresh rev 50 → rev 53 (1.1/beta):**
```bash
juju refresh maas-site-manager-k8s --channel 1.1/beta
```
- Two new endpoints added: `temporal-host-info`, `temporal-worker-info`.
- `upgrade-charm` hook ran successfully — no handler, so no side effects.
- Charm transitioned to `WaitingStatus("Waiting for temporal-host-info relation")`.
- Previously-set Temporal config values were **silently dropped** — rev 53's `charmcraft.yaml` removes those config options.
- `msm` service went from crash-looping (rev 50) to **disabled** (rev 53) until the new relations are established.
- `/usr/local/share/ca-certificates/` still absent after refresh (library bug, persists across revisions).
- No migration guidance is given to the operator about the obsolete config values.

**`KeyError` crash on rev 53 (full traceback):**
```bash
juju config maas-site-manager-k8s environment='[{value: foo}]'
```
```
  File "src/charm.py", line 421, in _get_environment_config
KeyError: 'name'
```
Confirmed call chain: `_get_environment_config` → `app_environment` → `_pebble_layer` → `_update_layer_and_restart`. The `KeyError` is **not caught** by that method's try/except (which only catches `ValueError` and five custom exceptions), so the hook crashes to `error`. Recovery requires `juju resolve --no-retry` followed immediately by resetting `environment` before the next hook re-fires with the stored bad value — a fragile race.

### Round 4: deep runtime experiments (Juju 3.6, rev 50, model `rv-msm-deep3`)

- **Pod restart recovery**: `kubectl delete pod` → charm recovers to the same "Failed to create operator user" state with a new pod IP; all relations re-establish, no hook errors or state corruption.
- **Remove/re-integrate database relation** from crash-loop state → clean transitions both ways.
- **Application teardown**: `juju remove-application maas-site-manager-k8s --force` — application and unit removed completely, no orphaned Kubernetes secrets, no dangling Juju secrets (`kubectl get secrets -n rv-msm-deep3` verified).

### Round 5: Juju 4.x tests (models `rv-msm-j4deep`, `rv-msm-j4b`)

- Charm deploys and reaches `WaitingStatus("Waiting for database relation")` on Juju 4.0.5.
- **postgresql-k8s cannot be deployed** on Juju 4.x (both `14/stable` and `14/edge`): "charm requires Juju version < 4.0.0, model has version 4.0.5".
- Certificate transfer bug reconfirmed on Juju 4.x.
- **`juju refresh` rev 50 → rev 53 on Juju 4.x**: rejected.
  ```
  ERROR setting application "maas-site-manager-k8s" charm: one or more of the provided
  endpoints "database, grafana-dashboard, ingress, juju-info, logging-consumer,
  maas-site-manager, metrics-endpoint, receive-ca-cert, s3, site-manager-cluster,
  temporal-host-info, temporal-worker-info, tracing" do not exist
  ```
  Juju 4.x rejects the new-endpoint mismatch that Juju 3.x accepts silently. The charm reverted to rev 50 after the failed attempt.

## Observed behaviour

- **Container image ships two Pebble services**: `msm` (`/bin/msm-api`, charm-managed) and `temporal-worker` (`./app/scripts/start-worker.sh`, always disabled, hardcoded `TEMPORAL_HOST=localhost:7233`, `TEMPORAL_QUEUE=test-queue`). The charm never enables or configures the latter — likely a vestige of an earlier architecture.
- **Service restart on every hook**: `_update_layer_and_restart` calls `container.restart()` unconditionally after `add_layer`. The initial deploy sequence for unit 1 generated at least 5 (later measured 8+) full restarts across config-changed, pebble-ready, relation, and observability events. `update-ca-certificates --fresh` is also exec'd in the container on every such hook, even with zero certificate relations.
- **Temporal crash loop**: DNS failure against the fake Temporal hostname produces `RuntimeError: Failed client connect …`, followed by an upstream `UnboundLocalError: cannot access local variable 'backoff'` in temporallib's `reconnect_loop` (observed in the workload container, not reviewable source). Pebble restarts the service in a backoff loop; the charm's status stays `Waiting`/`Blocked` and never reflects true health beyond that.
- **Scale-up status race (exact timestamps)**: unit 1 status log showed `active` repeatedly between `16:52:34` and `16:53:01` across ~10 hooks, while `pebble services` showed `msm: backoff` and `pebble checks` showed `http-test: down, 5/3 failures`. `pebble-check-failed` fired at `16:53:03` but is unhandled; final observed state at `16:53:05` was still `active`.
- **Certificate transfer entirely broken**: `/usr/local/share/ca-certificates/` never exists in the workload container, confirmed in four deployments (Juju 3.6 rounds 2/3/4, Juju 4.x round 5). The `certificate_transfer` v1 library's v0 fallback requires `ca`, `certificate`, and `chain`; `self-signed-certificates` provides only `ca` and `chain: '[]'`. The resulting `DataValidationError` on the missing `certificate` field is silently caught and an empty set is returned.
- **Bad-config recovery is otherwise clean**: `log-level=invalid` → blocked → `log-level=info` → recovers to waiting; the status message bug (missing f-string) is cosmetic but confusing.
- **Hook volume**: roughly 20+ hooks for a full deployment with 4 optional integrations, each triggering `_update_layer_and_restart` and a `container.restart()`.
- **Ingress URL** correctly propagated as `MSM_BASE_PATH=http://10.43.45.0/rv-msm-deep-maas-site-manager-k8s` in the Pebble layer environment.
- **Tear-down is clean**: no orphaned Kubernetes secrets or Juju resources after `remove-application`.
- **Pod restart recovery is clean**: relations re-establish, status returns to the pre-restart state, no hook errors.
- **Post-refresh (rev 53) Pebble plan**: full DB/S3/Temporal env vars and ingress URL present; no `log-targets` section (grafana-agent-k8s was blocked so Loki was never established); `/usr/local/share/ca-certificates/` still absent.
- **Plaintext secrets in the Pebble plan**: `MSM_DB_PASSWORD`, S3 access key and secret key are visible in plain text via `pebble plan` — inherent to the Pebble env-var model, but worth flagging for operators who assume `pebble plan` output is safe to share.
- **Rev 50→53 refresh recovery**: `upgrade-charm` hook ran with no side effects (no handler); `msm` transitioned from crash-looping to `disabled`; charm reached a stable `WaitingStatus("Waiting for temporal-host-info relation")` — a clean but unexplained outcome.
- **`KeyError` recovery fragility**: recovery required `juju resolve --no-retry` immediately followed by a valid `environment` value; the hook kept re-firing with the stored bad value in between, confirmed via repeated tracebacks in `juju debug-log`.
- **Juju 4.x**: charm's own `assumes: juju >= 3.6` is satisfied and it deploys standalone, but the required `postgresql-k8s` dependency blocks full-stack deployment, and `juju refresh` rev 50→53 is rejected outright due to the new required endpoints.

## Findings

### Certificate transfer library v0 fallback is incompatible with `self-signed-certificates`
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/certificate_transfer_interface/v1/certificate_transfer.py:667-676`; `ProviderUnitDataV0` at line 294
- **Evidence**: Confirmed in four separate deployments (Rounds 2, 3 on Juju 3.6; Round 5 on Juju 4.x). `self-signed-certificates` provides only `ca` and `chain: '[]'` in unit relation data; `application-data` is `{"version": "1"}` with no `certificates` key. The requires-side `_get_relation_data` (line 667) tries v1 first (empty result since the app-databag key is missing), then falls back to `ProviderUnitDataV0.load(databag)`. `ProviderUnitDataV0` requires both `ca: str` and `certificate: str`; the missing `certificate` field raises `DataValidationError`, which is caught silently and `return set()`. Certificates are never pushed to the container. Persists after refresh from rev 50 to rev 53, since the bug is in the library, not the charm.
- **Impact**: Certificate transfer is broken for the most common CA provider. No CA certificates reach the workload (`/usr/local/share/ca-certificates/` confirmed absent in all deployments). TLS connections requiring those CAs fail silently, with no charm-level error.
- **Fix**: Update the library to handle `ca`-only data, or make `ProviderUnitDataV0.certificate` `Optional[str] = None`; document the v1-provider requirement in the meantime.
- **Linter rule**: not mechanically checkable (requires runtime integration testing).

### `ActiveStatus` set despite failing Pebble check — no `pebble-check-failed` handler
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:238-244`; missing handler for `pebble-check-failed`
- **Evidence**: Unit 1 reached `ActiveStatus` (empty message) 8 times across 45 seconds while `pebble checks` showed `http-test: down, 5/3 failures` and `pebble services` showed `msm: backoff`. `pebble-check-failed` fired at `16:53:03` but the charm only observes `pebble-check-recovered`; status was never corrected.
- **Impact**: Operators see `active` for a unit whose workload is crash-looping — the most misleading status bug found.
- **Fix**: Add a `_on_pebble_check_failed` handler that sets `WaitingStatus`/`BlockedStatus`; in `_update_layer_and_restart`, wait for the check to actually pass before reporting status.
- **Linter rule**: "`pebble-check-recovered` observed but `pebble-check-failed` not observed" — mechanically checkable.

### `_on_cert_transfer_removed` lists the charm filesystem instead of the workload container
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:495-500`
- **Evidence**:
  ```python
  certs_to_remove = [
      filename
      for filename in os.listdir(self._ca_folder_path)
      if filename.startswith(f"receive-ca-cert-{self.model.uuid}-{event.relation_id}")
  ]
  for cert in certs_to_remove:
      self.container.remove_path(cert)
  ```
  `os.listdir()` runs in the charm process, not the workload container. Since certs are only ever `container.push()`ed into the workload, `os.listdir()` here always returns an empty list, so `container.remove_path()` is never called with a real path.
- **Impact**: Stale CA certificates are never cleaned up from the workload container when a certificate transfer relation is removed; the MSM application keeps trusting certificates from departed CAs indefinitely.
- **Fix**: Use `container.list_files(self._ca_folder_path)`, or track pushed filenames in peer data.
- **Linter rule**: "`os.listdir` called with a path used elsewhere in a `container.push`" — mechanically checkable.

### `juju refresh` rev 50→53 rejected on Juju 4.x
- **Severity**: critical
- **Kind**: bug
- **Where**: `charmcraft.yaml` (new required endpoints); Juju 4.x controller behaviour
- **Evidence**: `juju refresh maas-site-manager-k8s --channel 1.1/beta` on Juju 4.0.5 fails with "one or more of the provided endpoints … temporal-host-info, temporal-worker-info … do not exist"; the charm reverted to rev 50. Confirmed on model `rv-msm-j4b`.
- **Impact**: Operators on Juju 4.x cannot upgrade in place from latest/edge to any revision that adds new required relations; the only workaround is destroy-and-recreate, losing state.
- **Fix**: Document the limitation; consider making new relations optional until a migration path exists, or backport an `upgrade-charm` handler that detects the old config model and provides guidance before the refresh.
- **Linter rule**: not mechanically checkable.

### Certificate handlers lack `can_connect()` guards
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:488-491, 495-500, 506-516`
- **Evidence**: `_on_cert_transfer_available` (line 489) and `_on_cert_transfer_removed` (line 495) call `container.push()`/`container.exec()`/`container.remove_path()` without a `can_connect()` check. `_dump_all_certificates` (lines 506-516) also lacks its own guard; it is called both from `_update_layer_and_restart` (which does check `can_connect()` first, line 205) and from `_on_cert_transfer_available` (which does not).
- **Impact**: If a certificate-transfer event fires before Pebble is ready, the hook crashes with `ops.pebble.ConnectionError`.
- **Fix**: Add `if not self.container.can_connect(): event.defer(); return` at the top of each handler.
- **Linter rule**: "`container.<method>` called outside a `can_connect()` guard" — mechanically checkable.

### `_on_maas_enroll_broken` accesses remote app data on relation-broken without guarding for missing data
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:661`
- **Evidence**:
  ```python
  def _on_maas_enroll_broken(self, event: ops.RelationEvent) -> None:
      if not self.unit.is_leader():
          return
      if client := self._get_site_manager_client():
          return client.remove_site(event.relation.data[event.relation.app]["uuid"])
  ```
  On `relation-broken`, the departing unit's app data may already be empty (`KeyError` on `["uuid"]`), and in edge cases `event.relation.app` can be `None` (ops issue #1960934), causing `TypeError`.
- **Impact**: Every MAAS region disconnection can crash the hook instead of gracefully skipping the removal call; the site is never cleaned up on the MSM API side.
- **Fix**: Read the UUID from local peer data cached at relation-joined time instead of remote app data on relation-broken; guard for `event.relation.app is None`.
- **Linter rule**: "direct key access on `event.relation.data[event.relation.app]` in a `relation_broken` handler" — mechanically checkable.

### `_ensure_operator_user` uses a different readiness check than `_create_operator_user`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:237` (`_update_layer_and_restart`), `src/charm.py:537` (`_create_operator_user`)
- **Evidence**: `_update_layer_and_restart` gates on `self.container.get_check("http-test").status == CheckStatus.UP`; `_create_operator_user` gates on `self.container.get_services(self.pebble_service_name)` — a different, weaker condition (Pebble knowing about the service, not it being healthy).
- **Impact**: Confirmed at runtime — `msm-admin create-user` was invoked against a service about to crash (Temporal unreachable), leading to `BlockedStatus("Failed to create operator user")`.
- **Fix**: Align both checks on the Pebble health check, or add a retry loop with timeout in `_create_operator_user`.
- **Linter rule**: not mechanically checkable (requires semantic understanding of readiness).

### Environment config parsing crashes on malformed YAML items — `KeyError` uncaught
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:419-422`
- **Evidence**:
  ```python
  for item in env_config:
      if item["name"] not in ALLOWABLE_ENV_VARS:
  ```
  No guard for `item` lacking `"name"`. `juju config maas-site-manager-k8s environment='[{value: foo}]'` raises `KeyError: 'name'`, uncaught by `_update_layer_and_restart`'s try/except (which only catches `ValueError` and five custom exceptions). Confirmed traceback on both rev 50 and rev 53. Recovery requires `juju resolve --no-retry` followed by an immediate valid config change before the hook re-fires with the bad stored value — a race the operator can lose.
- **Impact**: Charm goes to `error` state ("hook failed: config-changed") instead of a clear `BlockedStatus`; the charm cannot self-recover.
- **Fix**: Wrap the key access (`try: name = item["name"] except KeyError: raise ValueError(...)`), which `_update_layer_and_restart` already catches.
- **Linter rule**: "dict key access `[]` on user-supplied YAML item without `.get()` or try/except" — mechanically checkable.

### `invalid log level: '{log_level}'` — missing f-string prefix
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:200`
- **Evidence**: `self.unit.status = ops.BlockedStatus("invalid log level: '{log_level}'")`. Confirmed: `log-level=invalid` produces this literal string, not the substituted value.
- **Impact**: Operator cannot tell what value was rejected.
- **Fix**: `f"invalid log level: '{log_level}'"`.
- **Linter rule**: "string literal contains curly braces but is not an f-string" — mechanically checkable (ruff `F541`-adjacent).

### `_update_layer_and_restart` restarts the service on every hook
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:234`
- **Evidence**: `container.restart()` is called unconditionally after `add_layer`, firing on config-changed, pebble-ready, database-created, endpoints-changed, Loki, ingress, Temporal, s3-credentials-changed, and metrics/grafana events. 8+ restarts confirmed for unit 1's initial hook sequence. `_dump_all_certificates()` (line 210) additionally execs `update-ca-certificates --fresh` on every hook regardless of whether any certificate relation exists.
- **Impact**: Each restart runs Alembic migrations and interrupts in-flight operations — destructive for a service handling image uploads. The extraneous exec adds latency to every hook.
- **Fix**: Compare the new layer against the existing plan and only restart if it changed; skip cert-dumping work when there are no active certificate relations.
- **Linter rule**: "`container.restart` called unconditionally after `add_layer`" — mechanically checkable.

### `_request_version` crashes on non-JSON or missing-key responses
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:430-431`
- **Evidence**: `resp.json()["version"]` — non-JSON responses raise `requests.JSONDecodeError`, a missing `"version"` key raises `KeyError`. Both are swallowed by a generic `except Exception` in `version()` (line 361), silently returning `""`.
- **Impact**: Workload version silently blanks out when the API returns an unexpected format, with no diagnostic.
- **Fix**: Catch `requests.JSONDecodeError` and `KeyError` explicitly; log the response body at warning level.
- **Linter rule**: "`.json()` result accessed with `[]` without `KeyError` handling" — mechanically checkable.

### `_create_operator_user` can orphan MSM user accounts if Juju secret operations fail
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:569-583`
- **Evidence**: `msm-admin create-user` runs first; the Juju secret is created/updated afterward. If `secret.set_content()` or `app.add_secret()` fails after a successful user creation, the credentials are lost from memory, `MSM_CREDS_ID` is never stored in peer data, and the next hook's `_ensure_operator_user` creates a new operator user, orphaning the old one.
- **Impact**: Repeated failures could accumulate orphaned operator user accounts with no cleanup path.
- **Fix**: Stage credentials in peer data before creating the secret, or make the `msm-admin` call the last step.
- **Linter rule**: not mechanically checkable.

### `set_peer_data` converts falsy values to `{}`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:596`
- **Evidence**: `self.peers.data[app_or_unit][key] = json.dumps(data or {})` — `data or {}` becomes `{}` for `0`, `False`, `""`, `[]`. Not currently triggered (`MSM_CREDS_ID` is always non-empty) but fragile against future callers.
- **Fix**: `json.dumps(data) if data is not None else "{}"`.
- **Linter rule**: "`or {}` used on non-Optional parameter passed to `json.dumps`" — mechanically checkable with type inference.

### `_on_maas_enroll_joined` defers indefinitely with no back-off
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:651-655`
- **Evidence**:
  ```python
  if enroll_token := self._get_enroll_token():
      self._enroll.publish_enroll_token(event.relation, enroll_token)
  else:
      event.defer()
  ```
  No retry limit, back-off, or eventual failure path if the operator user is never created.
- **Fix**: Add a retry counter in peer data; fail the relation with a clear status after N attempts.
- **Linter rule**: "`event.defer()` called unconditionally without a retry guard" — mechanically checkable.

### `_create_msm_user` catches only `ops.pebble.ExecError`, not other Pebble exceptions
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:542-545`
- **Evidence**:
  ```python
  try:
      proc = self.container.exec(...)
      proc.wait()
      return True
  except ops.pebble.ExecError:
      return False
  ```
  `container.exec()` can also raise `ops.pebble.ChangeError`, `ConnectionError`, and `APIError`, none of which are caught here.
- **Impact**: If the Pebble connection drops mid-exec, the hook crashes instead of returning a handled failure.
- **Fix**: Catch `ops.pebble.Error` (the base class).
- **Linter rule**: "specific Pebble exception caught where base `Error` should be caught" — mechanically checkable.

### `_on_pebble_check_recovered` sets `ActiveStatus` without verifying required relations
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:247-253`
- **Evidence**: The handler sets `ActiveStatus` directly after `_set_workload_version` and `_ensure_operator_user` succeed, without re-checking database/S3/Temporal relation health the way `_update_layer_and_restart` does.
- **Impact**: A timing window exists where a required relation is missing but a Pebble check recovery still reports `active`.
- **Fix**: Delegate to `_update_layer_and_restart` instead of duplicating status logic.
- **Linter rule**: "multiple code paths set `ActiveStatus` directly" — mechanically checkable.

### `juju refresh` rev 50→53 silently drops Temporal config with no migration guidance
- **Severity**: medium
- **Kind**: ux
- **Where**: `charmcraft.yaml` (config removal); `src/charm.py` (no `upgrade-charm` handler)
- **Evidence**: Refreshing from rev 50 to rev 53 removes `temporal-server-address`/`temporal-namespace`/`temporal-task-queue` and adds `temporal-host-info`/`temporal-worker-info` as required relations. `upgrade-charm` fires but has no handler; the old config values are dropped silently and the charm just shows `WaitingStatus("Waiting for temporal-host-info relation")` — the `msm` service goes from crash-looping to `disabled` with no explanation.
- **Impact**: An operator upgrading from the deployed latest/edge track to 1.1 is confused by the status change with no documentation of the migration.
- **Fix**: Add an `upgrade-charm` handler that detects the old config keys and emits an explicit `BlockedStatus` explaining the required relation changes; document the migration path.
- **Linter rule**: not mechanically checkable.

### Library version debt: `loki_push_api` and `data_interfaces` stuck on v0
- **Severity**: medium
- **Kind**: lint
- **Where**: GitHub issue [#12](https://github.com/canonical/maas-site-manager-k8s-operator/issues/12)
- **Evidence**: `charms.loki_k8s.v0.loki_push_api` and `charms.data_platform_libs.v0.data_interfaces` should be updated to v1 (automated issue, 2026-07-16).
- **Fix**: Update library imports to v1, validate compatibility.
- **Linter rule**: not established.

### Enrollment tokens stored indefinitely, never cleaned up
- **Severity**: medium
- **Kind**: bug
- **Where**: GitHub issue [#43](https://github.com/canonical/maas-site-manager-k8s-operator/issues/43); `lib/charms/maas_site_manager_k8s/v0/enroll.py:222`
- **Evidence**: `EnrollProvider._update_secret` creates a Juju secret (`enroll-{relation.name}-{relation.id}.secret`) per relation and never revokes or removes it, even though tokens are single-use.
- **Impact**: Secret storage grows unboundedly with each enrollment relation.
- **Fix**: Remove the secret in the `relation-broken` handler or once the token is confirmed used.
- **Linter rule**: not established.

### `v0/enroll.py` and `v1/enrol.py` are separate libraries with different LIBIDs
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/maas_site_manager_k8s/v0/enroll.py` (LIBID `f20c42b…`) vs `lib/charms/maas_site_manager_k8s/v1/enrol.py` (LIBID `c232507f…`)
- **Evidence**: v1 is functionally identical to v0 but uses British spelling and a different LIBID, making it a separate Charmhub library rather than an upgrade; secret labels also differ (`enroll-` vs `enrol-`), breaking compatibility.
- **Impact**: Confusing for library consumers — two libraries doing the same thing with different spelling, LIBIDs, and secret labels.
- **Fix**: Deprecate v0 in favor of v1, or unify under one LIBID with an API version bump.
- **Linter rule**: not mechanically checkable.

### `_get_relation_data` mutates the relation unit set with `pop()`
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/certificate_transfer_interface/v1/certificate_transfer.py:672`
- **Evidence**: `databag = relation.data.get(relation.units.pop(), {})` mutates the relation's units set; repeated calls on the same relation object return different units. In practice the set is rebuilt per event, but the pattern is fragile.
- **Fix**: not established beyond noting the fragility.
- **Linter rule**: not mechanically checkable.

### Operator user secret stores email as `"username"`
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:578`
- **Evidence**: `content = {"username": email, "password": password}` — works because `SiteManagerClient._login()` sends it as the `username` POST parameter, but is misleading during debugging.
- **Fix**: Name the field `"email"` or add a clarifying comment.
- **Linter rule**: not established.

### Pebble health check URL hardcodes port
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:340`
- **Evidence**: `"url": "http://localhost:8000/version"` uses the literal `8000` instead of the `SERVICE_PORT` constant.
- **Fix**: `f"http://localhost:{SERVICE_PORT}/version"`.
- **Linter rule**: "integer literal matches module-level constant" — mechanically checkable.

### `pyproject.toml` comment mislabels a test-tool section
- **Severity**: nit
- **Kind**: lint
- **Where**: `pyproject.toml:57`
- **Evidence**: A comment reading "Formatting tools configuration" sits directly above `[tool.coverage]`, a test tool, not a formatting tool.
- **Fix**: Correct or relocate the comment.
- **Linter rule**: not mechanically checkable.

### `temporal-tls-root-cas` config option has no validation
- **Severity**: low
- **Kind**: ux
- **Where**: `charmcraft.yaml` config section; `src/charm.py:400`
- **Evidence**: The free-text config value is passed directly into the `MSM_TEMPORAL_TLS_ROOT_CAS` environment variable with no validation of PEM structure or content.
- **Fix**: Add basic validation, or document the expected format.
- **Linter rule**: not established.

## Worth copying

1. **Unified convergence point**: nearly every event handler delegates to `_update_layer_and_restart` (`src/charm.py:145-195`), giving all config/relation changes a single code path.
2. **Custom exception hierarchy**: `DatabaseNotReadyError`, `OperatorUserError`, `S3IntegrationNotReadyError`, `TemporalNotConfiguredError`, `TemporalWorkerNotConfiguredError` each map directly to a status message (`src/charm.py:170-183`).
3. **Config-driven environment allowlist**: `ALLOWABLE_ENV_VARS` (`src/charm.py:59-63`) prevents arbitrary environment injection into the workload.
4. **Clean relation-removal recovery**: `_on_database_relation_removed` transitions cleanly to `WaitingStatus`, and re-integration recovers correctly — confirmed at runtime across multiple rounds.
5. **Graceful bad-config handling**: invalid env var names and invalid log levels are rejected with clear (if occasionally broken) `BlockedStatus` messages; valid follow-up config recovers cleanly in all observed cases.
6. **Enrollment secret management**: per-relation Juju secrets with GRANT to the relation (`lib/charms/maas_site_manager_k8s/v0/enroll.py:222`), clean dataclass serialization.
7. **Clean application teardown**: `remove-application` leaves no orphaned Kubernetes secrets or Juju resources (confirmed with `kubectl get secrets`).
8. **Pod restart resilience**: after `kubectl delete pod`, all relations re-establish and the unit reaches the same state with no hook errors.
9. **`_add_log_targets` departed-endpoint handling**: sets `services: []` for departed Loki endpoints and correctly detects new ones, merging from the existing Pebble plan rather than rebuilding blindly (`src/charm.py:284-315`).
10. **Type-cast Pebble layer**: `_pebble_layer` returns `cast(ops.pebble.LayerDict, layer)`, a small but useful pyright-friendly practice.

## Common-practice notes

- **Follows**: standard `src/charm.py` + `src/api.py` layout, `ops >= 2.5`, Pebble layer management via `container.add_layer(combine=True)`, library versioning under `lib/charms/<name>/v<N>/`, standard `tox.ini`, uses `charm_tracing`.
- **Drifts**: no `StoredState` usage — peer relation data and Juju secrets carry all persistent state (modern and correct). Does not use `observability_libs`'s standard COS pattern; directly wires `MetricsEndpointProvider`, `GrafanaDashboardProvider`, `LokiPushApiConsumer`.
- **No `upgrade-charm` handler**: upgrades rely on `config-changed` + `_update_layer_and_restart`. The rev 50 → rev 53 Temporal model change had no migration handling — confirmed at runtime, the hook ran successfully but did nothing.
- **postgresql-k8s blocks Juju 4.x deployment**: the charm's own `assumes: juju >= 3.6` is satisfied, but its required dependency requires Juju < 4.0.0, making the full stack undeployable on Juju 4.x controllers today.
- **`juju refresh` unsupported on Juju 4.x when endpoints change**: Juju 3.x silently accepts new required endpoints on refresh; Juju 4.x rejects them. Operators need to be aware of this version-specific behaviour difference.
- **Both `v0/enroll.py` (American) and `v1/enrol.py` (British) exist** with different LIBIDs and secret labels — effectively separate libraries on Charmhub. The charm imports v0.
- **Pre-defined `temporal-worker` service in the container image** is never enabled or configured by the charm and appears to be architectural debt; it should be removed from the image or documented.

## Tests

**Unit tests**: 36 pass, 0 fail, 76% coverage (`tox -e unit`, confirmed re-run).

Coverage gaps:
- `_on_cert_transfer_available` (lines 488-491): 0%
- `_on_cert_transfer_removed` (lines 493-504): 0%
- `_dump_all_certificates` (lines 506-516): 0%
- `_on_maas_enroll_joined` (lines 651-655): 0%
- `_on_maas_enroll_broken` (lines 663-669): 0%
- `_request_version`: excluded via `# pragma: nocover`
- `_on_loki_push_api_endpoint_departed` (lines 248-254): uncovered branches
- `_get_environment_config` malformed input paths (lines 418-427): 0%
- `_get_site_manager_client` (lines 577, 595): partial
- `_create_msm_user` failure paths (lines 545-546): partial

**Key gaps**: no tests for the certificate transfer handlers (would have caught the `os.listdir` and library-compatibility bugs), the enrollment-broken `KeyError`/`TypeError` crash, malformed `environment` input, `pebble-check-failed` handling, `set_peer_data` falsy values, `_request_version` non-JSON responses, or scale-up/leadership-change behaviour. The suite still uses `ops.testing.Harness` (deprecated in favor of `ops.testing.Scenario`) — 40 `PendingDeprecationWarning`s observed.

**Lint**: `ruff check` passes, `codespell` passes, `pyright` (static-charm and static-lib) passes, `pyproject-fmt --check` fails (key ordering, confirmed in tox lint output).

**Integration tests**: one file (`tests/integration/test_charm.py`), 4 async tests, none reach active/idle for the full stack:
- `test_build_and_deploy` ✓
- `test_database_integration` ✓ — asserts "Waiting for s3 integration"
- `test_s3_integration` ✓ — asserts "Waiting for temporal-host-info relation" (HEAD behaviour; would fail against rev 50)
- `test_temporal_integrations`: `temporal-worker-k8s` deployment is commented out due to a python-libjuju bug; test never reaches active
- Tracing and COS tests entirely commented out (pending canonical/observability#210)

Integration tests assert only status messages — no `/version` endpoint check, pebble check verification, or enrollment token issuance verification.

## Docs

- **README.md**: 357 bytes, points to Charmhub and CONTRIBUTING.md; no architecture overview or quickstart.
- **docs/overview.md**: good high-level description with an integration diagram.
- **docs/installation.md**: Terraform-only, plan lives in a separate repo.
- **docs/tutorial/**: 7-step tutorial covering full deployment with cross-model relations, correctly using `juju offer` for the relation-based Temporal model at HEAD — but it does not explain the rev 50 → rev 53 migration, so an operator on rev 50 would be confused by `BlockedStatus("temporal-server-address configuration is required")` against the tutorial's relation-based instructions.
- **CONTRIBUTING.md**: adequate, covers `tox -e format/lint/static/unit/integration`.

## Open questions

1. Why do `v0/enroll.py` and `v1/enrol.py` both exist as separate Charmhub libraries with different LIBIDs, spelling, and secret labels — should they be unified?
2. Does the charm ever recover if Temporal is unreachable at startup, beyond the observed permanent `WaitingStatus`/crash-loop? On rev 53 the service simply stays `disabled` until relations are established — cleaner, but still leaves no eventual failure signal.
3. Was the `msm-admin` `localhost:5432` bug fixed in the rev 53 container image? Could not verify — rev 53 never reaches the operator-user-creation stage without Temporal relations.
4. Do enrollment secrets ever get cleaned up? No `relation-broken` cleanup was found, matching open issue #43.
5. Is the pre-defined `temporal-worker` Pebble service in the container image intentional, or should it be removed?
6. Will the charm work on Juju 4.x once postgresql-k8s supports it? Given the observed refresh rejection when endpoints change, operators on Juju 4.x risk being stuck on their initial revision for any upgrade that adds relations.
