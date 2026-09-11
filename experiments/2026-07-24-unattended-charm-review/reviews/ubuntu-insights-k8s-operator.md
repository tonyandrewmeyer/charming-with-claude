# ubuntu-insights-server-k8s

A Kubernetes charm wrapping two Go binaries (`ubuntu-insights-web-service` and `ubuntu-insights-ingest-service`): the web service accepts HTTP report uploads and caches them; the ingest service validates and inserts them into PostgreSQL. The charm's structure is solid — clean `DatabaseHandler`, idiomatic status precedence, correct `RollingOpsManager` use for rolling upgrades — and it deployed and ran successfully on both Juju 3.6 and Juju 4.0. But config-input handling is weak: an operator can silently corrupt the Pebble layer (`web-port=0` with `migrate: false` leaves the charm reporting `active` while the service is unreachable), and a hardcoded `max_body_size=1` on the nginx-route integration will reject every real upload once that integration is trusted. Fix the port validation and the nginx body-size bug before anything else; the rest is polish.

| | |
|---|---|
| Repo | canonical/ubuntu-insights-k8s-operator @ `3e4c722` (2026-07-22) |
| Charms | ubuntu-insights-server-k8s |
| Substrate | k8s |
| Deployed | yes — fresh deploy on concierge-k8s-3 (Juju 3.6.25); on concierge-k8s-4 (Juju 4.0.12) the charm was already deployed (edge rev 109) when the reviewer arrived, so the Juju 4.0 checks were against a pre-existing install, not a fresh deployment |
| Reviewed | 2026-08-23 |

## What it does

The charm deploys two Go services inside a Kubernetes StatefulSet container named `ubuntu-insights-server`:

- **web-service**: HTTP server (default port 8080) accepting report uploads (`/upload/<app>`, `/ubuntu/desktop/<version>`), caches to `reports-cache` filesystem storage, exposes Prometheus metrics on port 2112 (`http_endpoint_requests_total`, `http_endpoint_request_duration_seconds_bucket`, `http_mux_requests_total`) and a `/version` endpoint.
- **ingest-service**: background processor reading cached reports, validating against an allowlist, inserting into PostgreSQL. Exposes Prometheus metrics on port 2113 (`ingest_processor_files_processed_total`, `ingest_processor_cache_size`, `ingest_processor_cache_size_bytes`, `ingest_processor_errors_total`, `ingest_processor_process_duration_seconds_bucket`).

The rock image is a distroless/chainguard minimal image: no shell, no standard Unix utilities, not even `ls`. Only Pebble and the two Go binaries are present. All container interaction must use the Pebble API (`pebble exec`, `pebble pull`, `pebble push`); `kubectl cp` fails because it requires `tar`.

Key integrations:
- **PostgreSQL** (required): connection credentials via `data_platform_libs`; runs migrations on startup and on relation changes.
- **nginx-route** (optional): exposes the web service externally via `nginx-ingress-integrator`. Requires `juju trust`.
- **Grafana dashboards** (optional): pre-built monitoring dashboard via `grafana_k8s`.
- **Prometheus metrics** (optional): web/ingest metrics on ports 2112/2113 via `prometheus_k8s`.
- **Loki log forwarding** (optional): Pebble log forwarding via `LogForwarder` from `loki_k8s`.

## Deployment log

### concierge-k8s-3 (Juju 3.6.25)

- **Initial deployment**: charmhub edge rev 109, `--resource ubuntu-insights-server-image=ghcr.io/canonical/ubuntu-insights-server:f34236738373dac669e835f0852fb09a4e8a572f-_0.9.5_amd64`. Charm reached `blocked/Waiting for database relation` immediately.
- **PostgreSQL integration**: deployed `postgresql-k8s` (rev 927, channel `16/stable`), `juju trust postgresql-k8s --scope=cluster`. After the rolling restart, both charms reached `active`. Charm briefly showed `maintenance/Waiting for the ingest service to start up` during startup.
- **nginx-route integration**: deployed `nginx-ingress-integrator` (rev 203), related to the insights charm. Integrator sat `blocked/Insufficient permissions` (needs `juju trust`). The `max_body_size=1` bug (see findings) applies once trusted.
- **Config change (invalid app)**: `web-apps=invalid_app_that_doesnt_exist` — hook fired, allowlist re-rendered, both services reloaded via file watching, charm stayed `active`.
- **Config change (invalid port)**: `web-port=99999` — hook failed with an unhandled exception. Charm went `error/hook failed: "config-changed"`. Recovery via `web-port=8080`. Status log shows **4 consecutive `config-changed` hook failures** before recovery succeeded.
- **Config change (port=0, migrate=true)**: `web-port=0` — hook failed with the same unhandled exception (`_execute_migrations()` does not suppress it). Charm went `error/hook failed: "config-changed"`.
- **Config change (port=0, migrate=false)**: `migrate: false` then `web-port=0` — hook completed without error (Juju API accepted `set_ports(0)`). Pebble layer updated with `--listen-port=0`. Health check now hits `http://localhost:0/version` and fails, but charm still showed `active` — no `collect_unit_status` cycle had fired since the check went down. **Silent failure.**
- **Recovery**: `web-port=8080 migrate=true` — hook succeeded, Pebble layer corrected, service recovered.
- **Database relation removal/restoration**: `juju remove-relation postgresql-k8s:database ubuntu-insights-server-k8s:database` → immediately `blocked/Waiting for database relation`; ingest stopped gracefully, web continued. `juju relate` restored → `active`.
- **Ingest service stop (manual)**: `pebble stop ingest-service` → charm went `maintenance/Waiting for the ingest service to start up` after ~2–3 min (one status collection cycle). Recovered after `pebble start ingest-service`.
- **Web service stop (manual)**: `pebble stop web-service` → Pebble health check went `down` (4/3 failures). Charm showed `maintenance/Waiting for the web service to start up` after ~3 minutes. After `pebble start web-service`, still `maintenance` for ~20s, then `active`.
- **Scaling**: `juju add-unit` → second unit active within ~2 min; Prometheus created a separate scrape job per unit. `juju remove-unit --num-units 1` scaled back down.
- **`juju refresh`**: packaged local charm (rev 0), `juju refresh --path <charm>`. Hook sequence: `stop` → `upgrade_charm` → `config_changed` → `start` → `pebble_ready` → `restart-relation-changed`. Database migrations ran 4 times (once per hook calling `_on_config_changed`). Settled to `active` in ~90 seconds.
- **COS**:
  - `prometheus-k8s` (rev 301, `2/stable`) related via `metrics-endpoint`. Scrape targets `10.1.0.153:2112` and `10.1.0.153:2113` confirmed `UP` for both units.
  - `grafana-k8s` (rev 180, `2/candidate`) related to Prometheus's `grafana-source`. Dashboard "Ubuntu Insights Monitoring" provisioned; Grafana queries confirmed live data (`up=1`, `http_endpoint_requests_total=224/230/236`).
  - `loki-k8s` (rev 217, `2/stable`) related via `logging`. Pebble plan updated with a `log-targets` section pointing at Loki; confirmed ready with Juju topology labels.

### concierge-k8s-4 (Juju 4.0.12)

- **Existing deployment**: model `rv-insights-k8s` already had `ubuntu-insights-server-k8s` deployed (edge rev 109) before the reviewer began — this was not a fresh deployment. Web-service running and healthy (504 health check successes). Charm was `blocked/Waiting for database relation`.
- **PostgreSQL incompatibility**: `postgresql-k8s` (`16/stable`) requires `juju < 4.0`. No compatible channel exists for Juju 4.0 on Ubuntu 24.04, so the full PostgreSQL integration could not be tested on this controller.

## Observed behaviour

- **`/version` confirmed working**: `curl http://<svc>:8080/version` → `{"version":"0.9.5"}`. `/healthz` and `/metrics` return 404 (expected on the main port).
- **Prometheus reaches metrics ports via pod IP, not the k8s service**: targets `http://10.1.0.153:2112/metrics` and `.../2113/metrics` show `health: up`, but this is direct pod-IP access. The k8s service only exposes port 8080, so external Prometheus using k8s service discovery would not find the metrics endpoints.
- **`web-port=99999` recovery required 4 failed hooks**: `juju show-status-log` shows `config-changed` failing at 04:41:48, 04:41:54, 04:42:05, 04:42:26 — four consecutive failures — before the recovery hook at 04:43:06 succeeded. Unit sat in `error/hook failed` for ~1.5 minutes with no backoff between retries.
- **`web-port=0` + `migrate: true`**: same failure mode as `web-port=99999` — `set_ports(0)` raises via the Juju API.
- **`web-port=0` + `migrate: false` is a silent failure**: `set_ports(0)` does not raise here; the Pebble layer is written with `--listen-port=0` and `url: http://localhost:0/version` while `juju status` still shows `active`, because no `collect_unit_status` fired after the health check went down. Confirmed via `pebble plan` while the unit showed `active`. This is the most dangerous failure mode observed — service unreachable, charm green.
- **Go binary has `--listen-host` but the charm never passes it**: confirmed via `ubuntu-insights-web-service --help` inside the container. The Pebble layer command uses `--listen-port` only. Setting `web-host=127.0.0.1` had zero effect on the rendered command.
- **Metrics confirmed at runtime**: Grafana query returned `up=1`, `http_endpoint_requests_total=224/230/236`; dashboard metric names match the Go binary's exposed metric names exactly.
- **Grafana dashboard UID differs from the template's hardcoded ID**: template has `"id": 19`; after import Grafana assigns UID `428b1a0c5cdaeca6fb21843f5e02036b3f282a44`. Low practical risk.
- **Status detection latency**: charm detects a stopped service after ~2–3 minutes (one `collect_unit_status` cycle), even though the Pebble health check itself fails within seconds. `pebble_check_fired`/`pebble_check_recovered` events fire but the charm has no handlers for them.
- **`startup: enabled` does not restart manually stopped services**: confirmed — `pebble stop web-service` leaves it stopped despite `startup: enabled`; by design, not a bug.
- **`migrate: true` runs on every `config_changed`**: status log shows `workload maintenance Running database migrations` on each such hook. No migration output appears in the debug log, so an operator cannot tell whether migrations actually ran.
- **`juju refresh` runs migrations 4 times**: once per hook in the refresh sequence that calls `_on_config_changed`.
- **Loki log targets confirmed**: `pebble plan` shows `log-targets: loki-k8s/0: {type: loki, location: ..., services: [all]}` after relating Loki. Go binaries use `--json-logs`.
- **Scaling**: adding a unit created a new Prometheus scrape job with the new unit's pod IP; ingest metrics showed `unknown` briefly while starting, web showed `up`.
- **Rolling upgrade sequence correct**: `acquire_lock.emit()` → `_on_restart` → `_on_config_changed` via `RollingOpsManager`: stop → upgrade_charm → config_changed → start → pebble_ready → restart-relation-changed.
- **No Prometheus/Loki alert rules**: `src/prometheus_alert_rules/` and `src/loki_alert_rules/` are empty.
- **Go version**: metrics report `go_info{version="go1.25.12"}`.
- **`_stop_service` untested**: present in code but never exercised by unit tests, nor is the `_on_storage_state_changed` path that calls it.
- **`web-service-ready` check threshold=3**: `pebble checks` shows `Successes: 172, Failures: 0/3`; a restarted service needs ~3× the 5s check period (~15s) before the unit shows `active`.
- **`rollingops` deprecation warning**: emitted on every hook using the restart manager — "The 'rollingops' v0 library is deprecated and no longer maintained. Please migrate to ... charmlibs/tree/main/rollingops".
- **Distroless container limits introspection**: no shell, no `ls`, `python3`, `wget`, `curl`, `dd`, `tar`. Only `pebble exec/pull/push` work; `kubectl cp` fails (needs `tar`).
- **`postgresql-k8s` incompatible with Juju 4.0**: confirmed — `16/stable` requires `juju < 4.0`.
- **Pebble layer correct on the pre-existing Juju 4.0 deployment**: `--listen-port=8080`, health check at `http://localhost:8080/version`, 504 successes.

## Findings

### `migrate: false` + `web-port=0` silently corrupts the Pebble layer

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:185-205` (layer write at `src/charm.py:354`)
- **Evidence**: `juju config migrate=false`, then `juju config web-port=0`. Hook completed without error. `pebble plan` confirmed the layer contains `--listen-port=0` and `url: http://localhost:0/version`. The health check went to `13/3` failures, yet `juju status` showed `active` because no `collect_unit_status` event had fired since the check went down. `set_ports(0)` apparently succeeds via the Juju API here (no exception raised), unlike the `open-port` hook-tool path exercised when `migrate: true`.
- **Impact**: setting `migrate: false` for any reason and then misconfiguring `web-port` silently corrupts the Pebble layer — the service becomes unreachable while the charm reports `active`. Completely invisible without manually inspecting the Pebble plan.
- **Fix**: validate the port range in `_on_config_changed` before any other operation, e.g. `if not (1 <= port <= 65535): self.unit.status = ops.BlockedStatus(...); return`.
- **Linter rule**: "Config option used in `set_ports` without range validation" — mechanically checkable.

### `_on_config_changed` has no validation of `web-port` range

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:185-205` (call at line ~202)
- **Evidence**: `self.unit.set_ports(typing.cast(int, self.config["web-port"]))` is called with no validation. `web-port=99999` raises `ModelError` from the `open-port` hook tool (uncaught). `web-port=0` with `migrate: true` fails the same way; with `migrate: false` it silently corrupts the layer (see above). `charmcraft.yaml` has no schema-level bound on the value.
- **Impact**: two distinct failure modes — noisy hook failure (`migrate: true`) or invisible service outage (`migrate: false`) — both preventable with input validation.
- **Fix**: add port range validation at the start of `_on_config_changed`.
- **Linter rule**: "Integer config option with no range validation before use in `set_ports`" — mechanically checkable.

### `max_body_size=1` in nginx-route will block all report uploads

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:277` (`max_body_size=1` argument, referenced elsewhere in the file as line 283)
- **Evidence**: `require_nginx_route(charm=self, ..., max_body_size=1)`. `nginx-ingress-integrator` translates this into the annotation `nginx.ingress.kubernetes.io/proxy-body-size: "1"` — 1 byte. The web service's default max upload is 131072 bytes (`--max-upload-bytes` in the Go binary, not exposed as charm config). `nginx-ingress-integrator` in the test model was `blocked/Insufficient permissions` (not yet trusted), so the bug is latent until `juju trust` is run and the Ingress resource is created.
- **Impact**: once the integrator is trusted, every real upload above 1 byte returns 413. This blocks the charm's primary function silently and permanently.
- **Fix**: raise `max_body_size` to at least 131072, or expose it as a charm config option.
- **Linter rule**: "Hardcoded `max_body_size` not derived from the Go binary's `--max-upload-bytes` default" — not mechanically checkable.

### `web-host` config option declared but never used

- **Severity**: high
- **Kind**: bug
- **Where**: `charmcraft.yaml:31-33`; no reference in `src/charm.py`
- **Evidence**: `web-host` is declared (default `""`, described as "The host on which the web service will listen for HTTP requests"). The binary supports `--listen-host` (confirmed via `ubuntu-insights-web-service --help`), but the Pebble layer command only passes `--listen-port`. Setting `web-host=127.0.0.1` had zero effect on the rendered command (confirmed via `pebble plan`); `grep -n "web.host\|web_host\|web-host" src/charm.py` returns nothing.
- **Impact**: operators setting `web-host` to bind a specific interface get no effect — the option is documented but inert.
- **Fix**: wire `web-host` into the command as `--listen-host={self.config['web-host']}` when non-empty.
- **Linter rule**: "Config option declared but never read in code" — mechanically checkable.

### "Assembling Pebble layers" status never set

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:264`
- **Evidence**:
  ```python
  def _update_layer_and_replan(self) -> None:
      ops.MaintenanceStatus("Assembling Pebble layers")   # result discarded
      try:
          self.container.add_layer(self.container.name, self._pebble_layer, combine=True)
  ```
  The `MaintenanceStatus` object is constructed and immediately discarded — never assigned to `self.unit.status`.
- **Impact**: on every config change, pebble-ready, storage change, or database event, the operator gets no intermediate feedback during layer assembly.
- **Fix**: `self.unit.status = ops.MaintenanceStatus("Assembling Pebble layers")`.
- **Linter rule**: not currently mechanically checkable ("result of a `Status` constructor is not assigned").

### Dead code: allowlist checks silently defeated in `_pebble_layer`

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:373-394`
- **Evidence**: lines 373–389 set `web_startup`/`ingest_startup` to `"disabled"` when the allowlist isn't rendered or the database isn't ready, logging warnings in the process — then lines 391–394 unconditionally overwrite both variables based only on `report_cache_path` and `is_relation_ready()`. The allowlist checks can never take effect.
- **Impact**: the charm's documented intent — disable services when the allowlist isn't rendered — is not implemented. The `logger.warning` calls fire on every `_pebble_layer` call with no effect, adding log noise.
- **Fix**: remove lines 373–389, or merge the allowlist condition into the final assignment at 391–394.
- **Linter rule**: not currently mechanically checkable ("subsequent assignment overrides all prior conditional assignments to the same variable").

### `_request_version` silently returns empty/errors on HTTP failure

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:436-439`
- **Evidence**:
  ```python
  def _request_version(self) -> str:
      resp = requests.get(f"http://localhost:{self.config['web-port']}/version", timeout=10)
      return resp.json()["version"]
  ```
  No `raise_for_status()`, no status-code check, no exception handling around `resp.json()["version"]`.
- **Impact**: on a non-200 response (e.g. during a rolling restart), `resp.json()["version"]` can raise `KeyError`; this is masked by a bare `except Exception` in the calling `version` property, so the unit doesn't crash but the workload version is never updated — `juju status` continues showing the stale app version.
- **Fix**: check `resp.status_code` or call `resp.raise_for_status()` before parsing the body.
- **Linter rule**: "HTTP response not checked for error status before parsing body" — mechanically checkable.

### Metrics ports 2112/2113 not exposed via Kubernetes service

- **Severity**: medium
- **Kind**: bug/ops
- **Where**: `charmcraft.yaml:115-120`, `src/charm.py:121-135`
- **Evidence**: the k8s service definition only lists `{"name":"juju-8080-tcp","port":8080,...}` — ports 2112/2113 are absent. In-cluster Prometheus works because it scrapes pod IPs directly (`10.1.0.153:2112`/`2113`, both `health: up`), not via the service.
- **Impact**: in-cluster COS integration functions, but external Prometheus using k8s service discovery would not find the metrics endpoints, and the service definition itself is misleading.
- **Fix**: expose the metrics ports via the k8s service (Pebble/charm support permitting), or document that Prometheus must scrape pod IPs directly.
- **Linter rule**: "Prometheus scrape targets use ports not exposed by the k8s service" — not mechanically checkable without cluster access.

### `_on_collect_status` calls `container.get_service()` without a `can_connect()` guard

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:167-168`
- **Evidence**:
  ```python
  try:
      web_status = self.container.get_service(ServiceType.WEB.value)
      ingest_status = self.container.get_service(ServiceType.INGEST.value)
  except (ops.pebble.APIError, ops.pebble.ConnectionError, ops.ModelError):
      event.add_status(ops.MaintenanceStatus("Waiting for Pebble in workload container"))
  ```
  `ConnectionError` is caught, but `get_service()` still attempts the connection before raising.
- **Impact**: on a k8s charm where the workload container may not yet be ready, this causes repeated failed connection attempts and log noise on every `collect_unit_status` cycle (~5 min).
- **Fix**: guard with `if self.container.can_connect():` before calling `get_service`.
- **Linter rule**: "Pebble API call without `can_connect()` guard" — mechanically checkable.

### `rollingops` v0 library is deprecated

- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/rolling_ops/v0/rollingops.py:306`
- **Evidence**: `RollingOpsManager.__init__` emits "The 'rollingops' v0 library is deprecated and no longer maintained. Please migrate to ... charmlibs/tree/main/rollingops" — visible on every hook that uses the restart manager.
- **Impact**: unmaintained dependency; noisy debug log.
- **Fix**: migrate to the new `rollingops` implementation at `https://github.com/canonical/charmlibs/tree/main/rollingops`.
- **Linter rule**: "Deprecated charm library in use" — mechanically checkable by scanning `lib/charms/` for known deprecated versions.

### `postgresql-k8s` incompatible with Juju 4.0 (blocks full integration testing)

- **Severity**: medium
- **Kind**: test-gap / ops
- **Where**: n/a (external dependency)
- **Evidence**: `postgresql-k8s` channel `16/stable` requires `juju < 4.0`; no compatible channel exists for Juju 4.0 on Ubuntu 24.04, confirmed by attempted deploy on concierge-k8s-4.
- **Impact**: the charm itself deploys and runs correctly on Juju 4.0 (pre-existing deployment observed healthy), but full database integration cannot be verified there — this is a `postgresql-k8s` limitation, not an insights-charm bug.
- **Fix**: none available from this charm; track upstream `postgresql-k8s` Juju 4.0 support.
- **Linter rule**: not mechanically checkable.

### `_on_config_changed` always replans even when nothing changed

- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:185-208`
- **Evidence**: registered on `pebble_ready`, `upgrade_charm`, `config_changed`, and storage events; unconditionally re-renders allowlists, re-runs migrations (if `migrate: true`), updates nginx-route, and calls `_update_layer_and_replan` regardless of whether anything actually changed.
- **Impact**: a trivial config change triggers a full allowlist re-render and Pebble layer push even though allowlist changes already propagate via file watching without a layer push.
- **Fix**: hash the current layer and only push if it differs from the last-pushed layer.
- **Linter rule**: not mechanically checkable.

### Migration re-run on every `config_changed` when `migrate: true`

- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:199-200`
- **Evidence**: status log shows `workload maintenance Running database migrations` on each `config-changed` hook; after `juju refresh` migrations ran 4 times in a row (once per hook calling `_on_config_changed`). No migration output appears in the debug log.
- **Impact**: if the Go migration tool is not idempotent, repeated config changes could fail; as-is, the operator cannot tell from logs whether migrations actually ran or were skipped.
- **Fix**: track applied migration state (e.g. via `StoredState` or a container-side flag) and only run when needed.
- **Linter rule**: not mechanically checkable.

### `ingest_environment` TOCTOU between `is_relation_ready()` and `get_relation_data()`

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:209-222`
- **Evidence**: `is_relation_ready()` is checked, then `get_relation_data()` is called separately — relation data could change between the two calls.
- **Impact**: `_pebble_layer` could be built with stale or incomplete credentials, causing the ingest service to fail at startup.
- **Fix**: combine both checks into one method returning `None` if not ready.
- **Linter rule**: not mechanically checkable.

### Migration failure logging loses context

- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:460-469`
- **Evidence**: on `ExecError`, stderr lines are logged individually at exception level, but the migration command/arguments and environment are not included.
- **Impact**: diagnosing a migration failure requires matching stderr to a specific migration script without that context.
- **Fix**: include the migration command/args in the log message and log the exit code as a structured field.
- **Linter rule**: not mechanically checkable.

### `conftest.py` `--model` option collides with the `jubilant` plugin

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/conftest.py:9` vs `jubilant` pytest plugin
- **Evidence**: both register a `--model` CLI option. Running `pytest tests/unit` directly raises `ValueError: option names {'--model'} already added`. `tox.ini` avoids this via `coverage run -m pytest`, which isolates the environment.
- **Impact**: developers running `pytest tests/unit` directly hit an opaque import-time error and must know to use `tox` instead.
- **Fix**: rename the project's option to `--juju-model`, or guard registration with `pytest_load_initial_conftests`.
- **Linter rule**: not mechanically checkable.

### Grafana dashboard has a hardcoded numeric ID — low practical risk

- **Severity**: low
- **Kind**: bug
- **Where**: `src/grafana_dashboards/Ubuntu-Insights-Monitoring.json.tmpl:27`
- **Evidence**: `"id": 19` hardcoded; Grafana assigns its own UID on import (`428b1a0c5cdaeca6fb21843f5e02036b3f282a44`), overriding it.
- **Impact**: in environments where the dashboard is re-imported by a different tool, the hardcoded ID could collide with an existing dashboard at ID 19.
- **Fix**: remove `"id": 19,` or set it to `null`.
- **Linter rule**: "Dashboard JSON contains a hardcoded numeric ID" — mechanically checkable.

### `assert type(x) is str` instead of `isinstance`

- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:185`
- **Evidence**: `assert type(self.restart_manager.name) is str`.
- **Impact**: stricter than `isinstance` (excludes subclasses); no practical risk since `str` has no relevant subclasses here, but unusual style.
- **Fix**: `assert isinstance(self.restart_manager.name, str)`.
- **Linter rule**: "Use `isinstance()` for type checks" — mechanically checkable.

## Worth copying

- **`DatabaseHandler`** (`src/database.py`): clean encapsulation of relation logic, `DBData` dataclass, `is_relation_ready()` returns `bool`.
- **`CollectStatusEvent` handler** (`src/charm.py:160-180`): idiomatic multi-layered status precedence (blocked → waiting → maintenance → active) with `event.add_status()`; thorough container/storage-mount checks.
- **Go service file watching**: web and ingest services watch `/etc/ubuntu-insights-service/` for allowlist changes and reload without restart — no charm-side restart needed.
- **Pebble health check** (`src/charm.py:419-421`): `web-service-ready` with `level=ready`, `threshold=3` drives status based on real workload health, not just process liveness.
- **Graceful ingest shutdown**: shuts down cleanly and visibly in logs when the database relation is removed.
- **`LEGACY_VERSIONS`**: well-documented set extending the allowlist for Ubuntu Report compatibility.
- **Grafana dashboard**: comprehensive (request counts, P95 latency, error rates, cache metrics, Loki log viewer); metric names match the Go binary exactly (confirmed at runtime).
- **`_stop_service` guard** (`src/charm.py:470-479`): checks `can_connect()`, service presence in the plan, and `is_running()` before calling `container.stop()`.
- **`tests/unit/test_database.py`**: comprehensive edge-case coverage — malformed endpoints, missing fields, fetch exceptions; clean reusable `handler_with_mocked_relation` context manager.
- **Integration tests** (`tests/integration/test_charm.py`): `test_db_state` queries PostgreSQL directly to verify inserted records; `test_web_service_running` asserts real HTTP status codes (403 bad app, 400 bad payload); `test_upgrade` adds a unit, refreshes, and checks survival.
- **Rolling upgrade via `RollingOpsManager`**: controlled restart sequence rather than an immediate service bounce.
- **`LogForwarder` integration**: correctly adds Pebble log targets when Loki is related (confirmed via `pebble plan`).

## Common-practice notes

- **`src/` layout**: source files live directly in `src/`, not `src/<charmname>/`. Accepted but not what most Canonical charms do. No functional impact.
- **`ops` 3.8.0** in use; latest is 3.9.x. No functional gap, worth keeping current.
- **Charm libs**: `data_platform_libs` v0, `grafana_k8s` v0, `loki_k8s` v1, `prometheus_k8s` v0, `nginx_route` v0, `rolling_ops` v0, mostly pinned as `version: "0"` in `charmcraft.yaml`, resolving to latest compatible — makes exact lib version harder to audit.
- **Rock**: built from `ubuntu-insights` at `server/v0.9.5` (Go 1.25.12); not bundled in the charm, must be supplied as a resource or from a trusted registry.
- **No `upstream-source`** on the OCI image resource in `charmcraft.yaml` — fine for production, harder for local testing.
- **`assumes: juju >= 3.1`**: correctly declared; compatible with Juju 4.0.
- **Ruff/pyright**: 193 ruff errors, all in `lib/charms/` (vendored libraries), none in `src/`. Pyright: 0 errors in `src/`. Charm's own code is clean.
- **Distroless rock image**: security best practice, but limits debuggability — no shell, no `tar`, `kubectl cp` fails; only Pebble API works.
- **`startup: enabled` semantics**: only restarts services that fail at startup, not manually stopped ones — by design.
- **No Terraform module** in the repo.
- **Alert rules absent**: `src/prometheus_alert_rules/` and `src/loki_alert_rules/` empty; COS alerting must be configured separately.
- **Juju 4.0**: charm runs correctly on the pre-existing deployment observed; the `postgresql-k8s` incompatibility is external, not an insights-charm issue.

## Tests

### Unit tests (16 total, all pass via `tox -e unit`)
- `tests/unit/test_charm.py` (8 tests): `test_pebble_layer`, `test_config_changed`, `test_relation_data`, `test_database_relation_broken`, `test_no_database_blocked`, `test_storage_attached`, `test_open_port`. Does **not** cover the `can_connect=False` path, `upgrade_charm` hook, `web-host` config effect, `_request_version` error path, `_stop_service`, `_on_restart`, or the `_on_storage_state_changed` detach path.
- `tests/unit/test_database.py` (8 tests): no-relation, no-endpoints, fetch exception, malformed endpoint, missing fields, valid data, `is_relation_ready` true/false.

### Integration tests (not run in this environment)
- `test_active`, `test_web_service_running` (checks 403/400/202/200 response codes), `test_db_state` (direct PostgreSQL query), `test_database_relations` (remove/re-add), `test_config_changed` (allowlist), `test_upgrade` (add unit + refresh).

### Test gaps
- No test for invalid `web-port` config (out-of-range or `migrate: false` corruption).
- No test for `can_connect=False` in `_update_layer_and_replan` or `_on_collect_status`.
- No isolated `upgrade_charm` hook test.
- No test for `web-host` config having any effect.
- No test for `_request_version` on non-200 response.
- No test for storage detach (only attach covered).
- No test for migration idempotency across repeated config changes.
- No test for Loki integration.
- No test asserting Grafana dashboard metrics against the Go binary (verified at runtime instead).
- No test for `_stop_service`.
- Coverage: 83% for `charm.py` (missing lines include 153, 157, 162, 171, 185-186, 198-202, 219, 238-239, 242-243, 252-253, 261, 271-273, 296-301, 315-316, 330-333, 341-343, 430-434, 439, 454-455, 461, 474-479, 483); 100% for `database.py`.

## Docs

- **README.md**: minimal — links to contribution guidelines, discourse, and GitHub, but doesn't explain what the charm does, its relations, or how to deploy it.
- **CONTRIBUTING.md**: thorough — commit conventions, PR process, testing, CI.
- **SECURITY.md**: standard policy, fine.
- **`charmcraft.yaml` config descriptions**: mostly present and useful. `web-host` is described but unused (bug, see Findings); `web-port` description omits the valid range.
- **Charmhub description**: accurate one-paragraph summary.
- **No Terraform module.**
- **No alert rules shipped** — COS alerting must be configured separately.

## Open questions

1. **Migration idempotency**: `migrate: true` re-runs on every `config_changed`; whether the Go migration tool tolerates repeated invocation is presumed but not confirmed. Verify by running `migrate` twice against the same database.
2. **`set_ports(0)` behaviour with `migrate: false`**: the Juju API appears to accept port 0 silently in this path while the `open-port` hook tool rejects it elsewhere — worth confirming directly against the `ops`/Juju backend rather than inferring from charm behaviour.
3. **`web-port=99999` recovery error spam**: confirmed 4 consecutive failed hooks over ~1.5 minutes with no backoff — worth deciding whether that's acceptable operator experience.
4. **Metrics ports and k8s service exposure**: in-cluster Prometheus works via pod IP; confirm whether external/service-discovery-based Prometheus setups are an intended use case before treating this as low priority.
