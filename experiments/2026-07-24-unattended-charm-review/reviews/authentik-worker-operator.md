# authentik-worker-operator

A k8s charm managing the Authentik worker background-process component. It receives database credentials and the encryption key via the `authentik-cluster` relation from `authentik-server`, exposes a Prometheus scrape endpoint, forwards logs to Loki, sends traces to Tempo, and follows the ops framework idiomatically.

**The local source is 44 commits behind the deployed charm** (`origin/main` at `e0fac03`, v1.1.0, vs local HEAD `11d4b61`, v1.0.0+2) **and has a broken `MetricsEndpointProvider` configuration** — it targets port 9000, but the rockcraft OCI image exposes metrics on port 9300. Building and deploying from local source today would silently break Prometheus scraping. Other gaps versus deployed: missing Grafana dashboards, empty alert-rule placeholders, no PgBouncer/read-replica support, `mypy` configured but not run in CI, 5782 lines of dead `data_platform_libs` code, an untested tracing edge case, and a unit-test suite that fails to collect under ops 3.8.1. A maintainer's first move should be rebasing/cherry-picking onto `origin/main` — the metrics port bug alone makes the local tree unfit to build from.

| | |
|---|---|
| Repo | `canonical/authentik-worker-operator` @ `11d4b61` (2026-07-23); tip of `origin/main` is `e0fac03` (v1.1.0), 44 commits ahead |
| Charms | `authentik-worker` |
| Substrate | k8s |
| Deployed | yes — `concierge-k8s-3`, `authentik-worker` rev 7 from `latest/edge` |
| Reviewed | 2026-08-24 |
| Gap to deployed | 44 commits behind `origin/main` (see Findings) |

## What it does

The charm runs a Pebble-defined workload container on the upstream `ghcr.io/canonical/authentik-server` image, invoking it as a worker process (`/lifecycle/ak worker`). It:
- Pulls `AUTHENTIK_SECRET_KEY` and PostgreSQL credentials from the `authentik-cluster` relation (app-owned Juju secret)
- Exposes a Prometheus scrape endpoint via `MetricsEndpointProvider` — verified live at `10.1.0.253:9300/metrics` returning `authentik_tasks_duration_milliseconds`. The local source at `11d4b61` incorrectly targets port 9000; the deployed charm (rev 7, built from `origin/main`) has `METRICS_PORT = 9300`, introduced in commit `21cc013`, 44 commits ahead of local HEAD
- Forwards logs to Loki (`LogForwarder`) and traces to Tempo (`TracingEndpointRequirer`) when those relations exist
- Reports version match/mismatch between worker and server via the cluster relation's `server_version`
- Runs `collect_unit_status` with named checks: pebble connectivity, database config presence, cluster data readiness, version match, service running, resource-patch status
- Uses a `NOOP_CONDITIONS`-guarded reconciler (`_holistic_handler`) that plans the Pebble layer only when all guards pass

## Deployment log

### Setup
- Model `rv-authentik-worker-k8s3` created on `concierge-k8s-3` (Juju 3.6.25) — note: `concierge-k8s-4` (Juju 4.0.12) rejected `postgresql-k8s 16/stable` with "requires Juju < 4.0"
- Deployed `authentik-worker` rev 7 from `latest/edge` → `blocked: missing authentik-cluster relation` ✓
- Deployed `postgresql-k8s` rev 927 from `16/stable` → active ✓
- Deployed `authentik-server` rev 30 from `latest/edge` → needed traefik-route to become active
- Deployed `traefik-k8s` rev 413 and `self-signed-certificates` rev 264 for ingress/TLS
- Deployed `grafana-agent-k8s` rev 168 from `1/edge` for metrics collection
- Deployed `loki-k8s` rev 244 from `3.7/stable` for log forwarding
- Deployed `tempo-coordinator-k8s` rev 162 from `2.10/stable` for tracing
- Integrated: `postgresql-k8s → authentik-server`, `traefik-k8s:certificates → self-signed-certificates`, `authentik-server:traefik-route → traefik-k8s`, `authentik-server:authentik-cluster → authentik-worker:authentik-cluster`
- Integrated: `authentik-worker:metrics-endpoint → grafana-agent-k8s:metrics-endpoint`
- Integrated: `authentik-worker:logging → loki-k8s:logging`
- Integrated: `authentik-worker:tracing → tempo-coordinator-k8s:tracing`
- Worker became `active` after all integrations established ✓
- `loki-k8s`: active ✓ (`LogForwarder` auto-configured)
- `tempo-coordinator-k8s`: blocked — "Missing any worker relation" (needs a separate worker provider; not a charm bug)
- `grafana-agent-k8s`: blocked — "Missing ['grafana-cloud-config']|['send-remote-write'] for metrics-endpoint" (expected; no outgoing sink)

### Timing
- Service start: ~25 seconds from pebble-ready hook to Pebble checks showing `up`
- Pebble `alive` check hits `http://localhost:9000/-/health/live/` ✓
- Pebble `ready` check hits `http://localhost:9000/-/health/ready/` ✓
- Both checks return HTTP 200 while the service is running

## Observed behaviour

**Scale (3 units):** Unit 1 became `active` ~40s after `juju scale-application authentik-worker 2`; unit 2 became `active` ~60s after scaling to 3. All 3 units independently `active`, serving health checks on port 9000 and metrics on port 9300. Scale to 1 completed in seconds (units 1 and 2 terminated, unit 0 remained). Scale from 1 back to 3 was not re-tested, but unit 1 was re-deployed successfully. Notable: during the 1→3 scale, `grafana-agent-k8s` briefly lost its metrics-endpoint/logging/tracing relations (`blocked: "Missing incoming ('requires') relation: metrics-endpoint|logging-provider|tracing-provider|grafana-dashboards-consumer"`). Re-integrating restored it to the expected blocked state. No data loss observed.

**grafana-agent-k8s integration:** `juju integrate grafana-agent-k8s:metrics-endpoint authentik-worker:metrics-endpoint` established the relation; grafana-agent's Pebble plan shows a scrape job for `authentik-worker/0` at `10.1.0.253:9300`. `GET http://10.1.0.253:9300/metrics` returned real `authentik_tasks_duration_milliseconds` data ✓. grafana-agent stayed blocked on `"Missing ['grafana-cloud-config']|['send-remote-write'] for metrics-endpoint"` — expected, no outgoing sink configured. Alert rules loaded into grafana-agent's config are placeholder `# Add...` comments in local source, but the deployed charm has real rules from commit `21cc013`.

**Loki/logging integration:** `juju integrate authentik-worker:logging loki-k8s:logging` → `loki-k8s` active within ~30s. `logging-relation-created/joined/changed` all fired on the worker unit, which stayed `active` throughout ✓. `LogForwarder` auto-configured the Pebble layer's Loki push API settings.

**Tempo/tracing integration:** `juju integrate authentik-worker:tracing tempo-coordinator-k8s:tracing` established the relation. `tracing-relation-created/joined/changed` all fired; worker stayed `active` ✓. `_holistic_handler` re-rendered the Pebble layer on each relation change. `tempo-coordinator-k8s` itself stayed blocked ("Missing any worker relation") — it needs a separate Tempo worker backend not provided by `authentik-worker`; this is a COS topology issue, not a charm defect. No OTEL env var appeared in the Pebble layer: the tracing relation's app data was `{}` (empty), so `TracingEndpointRequirer.is_ready()` returned `False` and `TracingData.load()` returned `TracingData(is_ready=False, endpoint="")`, giving an empty `to_env_vars()` dict.

**Kubernetes service ports:** the `authentik-worker` K8s Service exposes only `9000/TCP`, though both 9000 and 9300 are bound to `0.0.0.0` inside the container. grafana-agent scrapes pod IPs directly (`10.1.0.253:9300`), bypassing the Service. Port 9300 is only reachable via pod IP, not via the ClusterIP.

**Config change (`log_level` warning):** `config-changed` fired; `_holistic_handler` called `pebble.plan()` → `replan()`; the service restarted (Pebble `Since` timestamp advanced). ✓ Correct.

**Config change with invalid value (`log_level=invalid_value`):** Accepted silently by the charm. Service restarted with the invalid value, Python raised `ValueError: Unable to configure logger ''` on startup, and the service crashed into Pebble backoff. The charm correctly detected the crash via `is_failing()` → `BlockedStatus("failed to start service, check container logs")`. ✓ Recovered once `log_level` was fixed.

**Multiple invalid int configs (`worker_processes=0, worker_threads=0, task_expiration_days=0, task_default_time_limit=0` set together):** All four accepted by Juju (type `int`) and passed to the upstream binary simultaneously. The Rust binary rejected `task_default_time_limit=0` with `invalid value: integer '0', expected a nonzero usize`. Service crashed (exit 1), backoff restart, charm detected it via `is_failing()` → `blocked: "failed to start service, check container logs"`. ✓ Recovered after setting `worker_processes=1, worker_threads=2, task_expiration_days=30, task_default_time_limit=600`. Same crash confirmed for `worker_processes=0` alone and for `worker_processes=-1` (`invalid value: integer '-1', expected a nonzero usize`).

**`worker_threads=0`:** Accepted silently; service stayed `active` with `AUTHENTIK_WORKER__THREADS: "0"` in the Pebble layer, despite the README recommending "a value below 2 is not recommended." Not a crash, but undocumented behaviour.

**Relation removal:** `juju remove-relation authentik-server:authentik-cluster authentik-worker:authentik-cluster` → worker `blocked: missing authentik-cluster relation`, `pebble.stop()` called. ✓

**Relation re-add:** worker recovered to `active`. ✓

**Service manually stopped (`pebble stop`):** service went `inactive`; `collect_unit_status` set `WaitingStatus("waiting for service to start")` (priority 2) over `ActiveStatus()` (priority 1) correctly. The `update_status` hook fired ~5 minutes later, called `_holistic_handler` → `pebble.plan()`, and the service restarted, returning to `active`. ✓

**Scale to 0:** completed in seconds. `authentik-server`, previously blocked on "missing authentik-worker relation", recovered to `active` when the worker scaled to 0.

**Scale back from 0:** new unit deployed with a new pod IP (`10.1.0.253` vs old `10.1.0.42`); reached `active` within ~45s, Pebble `alive`/`ready` checks both `up`. ✓ Charm handles scaling from zero correctly.

**Pod restart (`kubectl delete pod`):** Juju recreated the pod with a new IP; unit recovered to `active` within ~60s, no hook errors in debug-log. ✓

**`juju refresh authentik-worker --channel latest/edge`:** "charm authentik-worker: already up-to-date" (rev 7 is current on that channel). ✓

**`juju remove-application`:** not tested — would require full teardown, destroying the model for later verification runs.

**Actions:** none defined (`charmcraft.yaml actions:` is empty); confirmed via `juju actions authentik-worker` → "No actions defined for authentik-worker."

**TLS via traefik-k8s:** deployed and integrated with `self-signed-certificates`, but traefik remained `active` with "Certificate not available yet" — the certificate provider did not auto-issue. Not a charm defect (a CSR flow is required); this side of the stack was not fully exercised.

**`AUTHENTIK_POSTGRESQL__USE_PGBOUNCER` in the Pebble plan:** the deployed charm's combined plan sets this env var to `"false"` for the `authentik-worker` service. It is not in the local source's `DEFAULT_WORKER_ENV` (`env_vars.py` line 33 does not contain it). It was added in commit `246de2f` ("consume PostgreSQL read replicas and PgBouncer flag"), 44 commits ahead of local HEAD. `juju show-unit authentik-worker/0` confirms `db_use_pgbouncer: "false"` is published by `authentik-server` on the relation; the deployed charm reads and uses it, the local source ignores it.

## Findings

### Local source targets the wrong metrics port — 44 commits behind deployed charm
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:63`, `src/constants.py` (local source at `11d4b61`)
- **Evidence**: the rockcraft OCI image serves Prometheus metrics on port 9300 (verified: `curl 10.1.0.253:9300/metrics` returns `authentik_tasks_duration_milliseconds`; port 9000 returns empty). The deployed charm (rev 7, built from `origin/main`) has `METRICS_PORT = 9300` and `targets: [f"*:{METRICS_PORT}"]` = `["*:9300"]`, added in commit `21cc013`. Local source has `WORKLOAD_PORT = 9000` and uses it for `MetricsEndpointProvider` targets (`["*:9000"]`). `juju show-unit grafana-agent-k8s/0` confirms the deployed charm publishes `scrape_jobs = [{"job_name": "authentik_worker_metrics", "metrics_path": "/metrics", "static_configs": [{"targets": ["*:9300"]}]}]`. Gap confirmed via `git log --oneline 11d4b61..origin/main | wc -l` = 44. `origin/main` also adds, in the same or nearby commits: `src/grafana_dashboards/authentik-worker.json.tmpl` and real alert-rule files (`21cc013`); `AUTHENTIK_POSTGRESQL__USE_PGBOUNCER` in `DEFAULT_WORKER_ENV` and read-replica support (`246de2f`); `GrafanaDashboardProvider` in `charm.py` (`21cc013`); `add_layer` wrapped in try/except in `PebbleService.plan()` (`f76e6ec`); visible version-mismatch status messages (`5f3060c`); `test_services.py` and `TestPebbleCheckRecovered` unit tests.
- **Impact**: building the charm from local source ships `targets: ["*:9000"]`; grafana-agent scrapes an empty endpoint on that port and COS silently receives no worker metrics. Also absent: Grafana dashboards, real alert rules, PgBouncer/read-replica support.
- **Fix**: rebase local source onto `origin/main` or cherry-pick the 44 commits, at minimum `21cc013` (metrics port, dashboards, alert rules), `f76e6ec`, `5f3060c`, `d288f8a` (read replicas), `246de2f` (PgBouncer), `c18adba` (terraform fixes).
- **Linter rule**: not established — requires comparing deployed charm against source or running the integration.

### Multiple int config values not validated before being passed to the binary
- **Severity**: high
- **Kind**: bug
- **Where**: `charmcraft.yaml` config options, `src/configs.py`
- **Evidence**: `worker_processes`, `task_default_time_limit`, `task_expiration_days`, `consumer_listen_timeout` are `int`-typed and accept `0` (or negative, for `worker_processes`) at the charm level. The upstream Rust binary uses a `nonzero usize` type and rejects `0`: `worker_processes=0` and `worker_processes=-1` both errored with `invalid value: integer '0'|'−1', expected a nonzero usize` (verified live); `task_default_time_limit=0` produced the same error when all four were set together (verified live). `task_expiration_days=0` and `consumer_listen_timeout=0` follow the same constraint but weren't individually re-verified. `worker_threads=0` and `postgresql_conn_max_age=0` are accepted without crashing (worker_threads verified live staying `active`).
- **Impact**: an operator setting `task_default_time_limit=0` or `worker_processes=0` via `juju config` gets no charm-level feedback; the service crashes and the operator must read container logs to diagnose the cause.
- **Fix**: add validators in `CharmConfig` requiring `task_default_time_limit > 0`, `worker_processes > 0`, `consumer_listen_timeout > 0`, `task_expiration_days > 0`; set `BlockedStatus` on invalid values. At minimum, document the positive-integer constraint in `charmcraft.yaml`.
- **Linter rule**: not established — requires running the binary or cross-referencing config descriptions against binary constraints.

### `log_level` config value not validated
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/configs.py:18–43`
- **Evidence**: `charmcraft.yaml` documents `log_level`'s acceptable values as `"info", "debug", "warning", "error"` and `"critical"` but declares it `type: string` with no `enum:` constraint; any string is passed through to `AUTHENTIK_LOG_LEVEL`. Setting `log_level=invalid_value` was accepted, passed to the worker, and caused `ValueError: Unable to configure logger ''` on startup, crashing the service into Pebble backoff. Charm recovered once `log_level` was fixed.
- **Impact**: an operator who mistypes the value gets no charm-level feedback; the service crashes and the mistake must be diagnosed from container logs.
- **Fix**: add a validator in `CharmConfig` checking `log_level` against the documented allowed set, and set `BlockedStatus`/raise on invalid values.
- **Linter rule**: not established — requires cross-referencing `charmcraft.yaml` descriptions against code.

### `mypy` configured in `pyproject.toml` but not run in CI
- **Severity**: medium
- **Kind**: lint
- **Where**: `tox.ini:lint`, `pyproject.toml:[tool.mypy]`
- **Evidence**: `pyproject.toml` has a full `[tool.mypy]` strict configuration and lists `mypy` as a dev dependency, but the `lint` tox environment runs only `codespell`, `isort --check-only`, and `ruff`. `mypy src/` (run manually) returns 5 errors:
  - `src/services.py:104`: `dict[str, str | bool]` assigned where Pebble's `environment` TypedDict requires `dict[str, str]`
  - `src/configs.py:24,44,46,48`: `config.get()` returns `int | float | str` assigned into a `dict[str, str]`-typed env-vars structure
- **Impact**: type errors that the project's own strict configuration is designed to catch go unnoticed because CI never runs `mypy`.
- **Fix**: add `mypy src/` to the `lint` tox environment; the existing mypy config would catch these 5 errors immediately.
- **Linter rule**: mechanically checkable — `mypy src/` returns non-zero exit with the errors above.

### `TracingData.to_env_vars()` can emit an empty OTEL endpoint if relation data is valid but incomplete
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/integrations.py:21–24`
- **Evidence**: `TracingData.load()` calls `requirer.is_ready()` then `requirer.get_endpoint("otlp_http")`. In `lib/charms/tempo_coordinator_k8s/v0/tracing.py`, `is_ready()` (line ~850) only checks that the relation data parses as `TracingProviderAppData`, not that an `otlp_http` receiver is present; `get_endpoint("otlp_http")` (line ~920) returns `None` if that receiver is absent. If a provider publishes a structurally valid but incomplete payload, `is_ready()` returns `True` while `get_endpoint()` returns `None`, and `to_env_vars()` would return `{"OTEL_EXPORTER_OTLP_ENDPOINT": ""}`. In this deployment `tempo-coordinator-k8s` was blocked and published empty relation data, so `is_ready()` returned `False` and the edge case was not triggered; it remains theoretical, reachable only with a partially-configured tracing provider. The library itself notes at line ~909 that this "can happen if the charm requests tracing protocols, but the relay ... isn't yet connected to the tracing backend."
- **Impact**: an empty `OTEL_EXPORTER_OTLP_ENDPOINT` could reach the Pebble layer undetected, and unnecessary layer re-renders/restarts could occur on tracing relation events even before the endpoint is available.
- **Fix**: change `to_env_vars()` to check `bool(self.endpoint)` as well as `is_ready`: `if not self.is_ready or not self.endpoint: return {}`.
- **Linter rule**: not established — requires a partial tracing provider to reproduce.

### Unit tests fail to collect under ops 3.8.1
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:188–208` (and likely elsewhere)
- **Evidence**: tests import `ops.testing.WaitingStatus`, `BlockedStatus`, `ActiveStatus`, `MaintenanceStatus`, which are available in `ops.testing` under ops 3.8.0 but not 3.8.1 (moved to top-level `ops`). System Python (ops 3.8.0): `python3 -m pytest tests/unit/` → 32 passed. After `uv pip install pytest pytest-mock` upgraded ops to 3.8.1, `uv run pytest tests/unit/` fails collection with `AttributeError: module 'ops.testing' has no attribute 'WaitingStatus'`.
- **Impact**: developers using `uv sync`/`uv pip install` for a fresh environment get a broken test suite; CI likely masks this with a pinned ops version.
- **Fix**: import status classes from `ops` rather than `ops.testing`, and pin `ops` in `pyproject.toml` (or skip on incompatible versions).
- **Linter rule**: not established — requires running tests against the current ops release.

### `PebbleError` caught in the reconciler without a status change
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:138`
- **Evidence**: `_holistic_handler` wraps `self._pebble.plan(layer)` in `try/except PebbleError`, logs an error, and returns. If `plan()` fails, the workload config goes stale but the charm proceeds; `collect_unit_status` may still report `ActiveStatus` if the service is already running. The same pattern persists in `origin/main`, which merely moved `add_layer`'s try/except into `PebbleService.plan()` without changing the charm-level handling.
- **Impact**: a failed Pebble plan leaves the operator seeing `active` while the workload configuration may be wrong.
- **Fix**: set `self.unit.status = ops.BlockedStatus("pebble plan failed, check container logs")` before returning from the except block.
- **Linter rule**: "exception caught in a reconciler handler must not return without setting a named status" — not established, not mechanically checkable.

### Empty alert-rules placeholders
- **Severity**: low
- **Kind**: docs
- **Where**: `src/prometheus_alert_rules/rules.yaml`, `src/loki_alert_rules/rules.yaml`
- **Evidence**: both files contain only `# Add Prometheus/Loki alerting rules for authentik-worker in this file.` — no rules defined. The deployed charm (rev 7) carries real rules (`authentik_worker_unavailable.rule`, `authentik_worker_task_backlog.rule`) added in commit `21cc013`, confirmed loaded into grafana-agent's config.
- **Impact**: operators integrating with Grafana on local source get metrics but no pre-defined alerts for worker-specific conditions.
- **Fix**: adopt the real alert rules from `21cc013`.
- **Linter rule**: mechanically checkable — file must contain at least one rule entry.

### Dead `data_platform_libs` library shipped with the charm
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/data_platform_libs/v0/` (5782 lines)
- **Evidence**: `data_interfaces.py` (5782 lines) is present but never imported; `grep -rn "data_platform" src/ tests/ --include="*.py"` returns nothing. It still ships inside the charm binary.
- **Impact**: bloats the packaged charm and signals an unused/unmaintained dependency.
- **Fix**: remove `lib/charms/data_platform_libs/` unless it is planned for a near-term feature, in which case document why it's retained.
- **Linter rule**: not established — requires cross-referencing lib vs. src imports.

### `worker_threads` semantically unvalidated despite documented recommendation
- **Severity**: low
- **Kind**: ux
- **Where**: `charmcraft.yaml` config, `src/configs.py:31`
- **Evidence**: `worker_threads` is `type: int`; Juju enforces only the type. README states "a value below 2 is not recommended unless you have multiple worker replicas." `worker_threads=0` was accepted, passed through as `AUTHENTIK_WORKER__THREADS: "0"`, and the service stayed `active`.
- **Impact**: documentation signals a recommendation that is not enforced; operators may set 0 expecting rejection.
- **Fix**: validate in `CharmConfig.to_env_vars()`, or add an enum-style constraint if Juju config supports it.
- **Linter rule**: not established.

### Charmhub links typo
- **Severity**: low
- **Kind**: docs
- **Where**: `charmcraft.yaml:6–7`
- **Evidence**: `links.source` and `links.issues` both read `https://github.com/canonical/authenik-worker-operator` (missing the "t"). Correct URL is `.../authentik-worker-operator`.
- **Impact**: source/issue links from Charmhub 404.
- **Fix**: correct the spelling in both URLs.
- **Linter rule**: not established — requires human review of links.

### Untested code paths
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/charm.py:153` (`_on_resource_patch_failed`), `src/charm.py:164` (`_on_pebble_check_failed`), `src/charm.py:169` (`_on_pebble_check_recovered`)
- **Evidence**: these handlers, plus `_holistic_handler`'s `PebbleError` catch and `TracingData.load()` with `is_ready=True`/`get_endpoint=None`, have no unit tests in local source. `origin/main` adds `tests/unit/test_services.py` (4 classes covering `PebbleService.plan()`, including `PebbleError` wrapping) and `TestPebbleCheckRecovered` in `test_charm.py` (2 tests).
- **Impact**: these paths handle edge conditions that could produce unexpected behaviour without test coverage to catch regressions.
- **Fix**: add unit tests verifying logging and any status changes for each handler.
- **Linter rule**: not established.

### Scaling triggers a transient relation disconnect for grafana-agent-k8s
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py` (relation management on scale)
- **Evidence**: scaling `authentik-worker` from 1 to 3 units briefly put `grafana-agent-k8s` into `blocked: "Missing incoming ('requires') relation: metrics-endpoint|logging-provider|tracing-provider|grafana-dashboards-consumer"`. Re-integrating restored it to the expected `blocked: "Missing ['grafana-cloud-config']|['send-remote-write'] for metrics-endpoint"` state; no data loss observed. Not reproduced consistently; could be Juju uniter timing rather than a charm defect.
- **Impact**: could cause longer-lived disruption on slower substrates, and produces confusing status messages during routine scale operations.
- **Fix**: investigate whether the disconnect is uniter timing or an expected transient scale-event state; document in the README if expected.
- **Linter rule**: not established — requires live scale testing.

## Worth copying

- **`NOOP_CONDITIONS` pattern** (`src/utils.py`): composable, named boolean conditions checked at the top of the reconciler — easier to extend and test than conditions buried inside handlers.
- **`AuthentikClusterIntegration` wrapper** (`src/integrations.py`): isolates the library interface from charm business logic, making `create_autospec`-based testing clean.
- **`TracingData` frozen dataclass** (`src/integrations.py`): immutable, testable relation-data DTO with a `load()` classmethod.
- **`EnvVarConvertible` Protocol** (`env_vars.py`): makes explicit which objects can contribute env vars to the Pebble layer; `EnvVars` type alias keeps signatures clean.
- **`is_running()` double-check** (`src/services.py`): checks both `service.is_running()` and the Pebble `ready` check status.
- **`create_state()` factory** (`tests/unit/conftest.py`): module-level factory with named kwargs, cleaner than nested fixtures.
- **`is_failing()` string comparison** (`src/services.py`): handles both enum and string forms of `ServiceStatus.current` via `str(current_str).lower()`.
- **Split status computation** (`_check_db_status`, `_check_cluster_status`): each returns a single `StatusBase`, so `_on_collect_status` reads as a composition of named checks.
- **Pydantic `ProviderData`** (`lib/charms/authentik_server/v0/authentik_cluster.py`): validates relation data and uses `Field(exclude=True)` to keep secrets out of relation databags.
- **`LogForwarder`/`TracingEndpointRequirer` auto-configuration**: both libraries update the Pebble layer automatically on relation changes; the charm only observes events and re-renders.
- **App-owned Juju secrets for secret transport**: the library creates an app-owned secret for `secret_key`/`db_password`, grants it to the worker, and reads it back with `Field(exclude=True)` protecting the databag.

## Common-practice notes

- ops 3.x, Scenario testing, `pytest` — standard Juju SDK pattern. ✓
- Libraries under `lib/charms/<charm>/v<N>/`; `authentik_cluster` at v0, `LIBPATCH` 2. ✓
- `charmcraft.yaml` modern layout, `parts.charm.charm-binary-python-packages`, `assumes: juju >= 3.0.2`, `charm-user: non-root`. ✓
- Container gid/uid `584792` hardcoded, non-root, consistent with rockcraft OCI images. ✓
- No custom actions defined. ✓
- CI via shared workflow `canonical/identity-team/.github/workflows/charm-pull-request.yaml`, common in identity-team repos. ✓
- `collect_unit_status` with named checks; `ops._get_highest_priority()` correctly handles `blocked` (4) > `waiting` (2) > `active` (1). ✓
- `update_status` observes `_on_holistic_handler` every 5 minutes. ✓
- Two-port architecture: health checks on 9000 (Pebble checks), Prometheus metrics on 9300; both bound to `0.0.0.0`. K8s Service exposes only 9000; scrape targets use pod IPs directly.
- `version_is_matched` NOOP condition delays startup until both sides publish their version; commit `5f3060c` (ahead of local HEAD) adds visible status for this state.
- `AUTHENTIK_POSTGRESQL__USE_PGBOUNCER` in `origin/main`'s `DEFAULT_WORKER_ENV`: the server owns this flag and publishes it over the cluster relation (`246de2f`); the charm no longer needs a local `postgresql_use_pgbouncer` config option. Local source lacks this.
- Unit tests import from `ops.testing`, which works on ops 3.8.0 but fails to collect on ops 3.8.1 (see findings).
- Tracing relation events (`created`/`joined`/`changed`) all fire `_on_holistic_handler`, re-rendering the Pebble layer — standard relation-triggered reconciliation.

## Tests

### Unit tests: 32/32 pass (local source); 56/56 pass (origin/main)
- **Location**: `tests/unit/`
- **Local source**: `python3 -m pytest tests/unit -v` (system Python, ops 3.8.0) → 32 passed in 0.49s, 20 deprecation warnings
- **origin/main**: same command after checkout → 56 passed in 0.90s, 27 deprecation warnings
- **Coverage gaps in local source vs. origin/main**:
  - `test_services.py` entirely missing (origin/main has 8 tests across 4 classes covering `PebbleService.plan()` and `WorkloadService`)
  - `test_integrations.py`: 9 tests vs. origin/main's 13 — missing read-replica tests (`test_to_env_vars_no_replicas_when_key_absent`, `test_to_env_vars_indexes_multiple_replicas`, `test_to_env_vars_replicas_split_on_last_colon`, `test_to_env_vars_replicas_skip_blank_and_malformed_entries`) and PgBouncer tests (`test_use_pgbouncer_inherited_from_databag`, `test_use_pgbouncer_defaults_false_when_key_absent`)
  - `test_charm.py` missing `TestPebbleCheckRecovered` (2 tests) and `TestVersionMismatchStopsWorkload`
  - No test for `_on_pebble_check_failed` (logs a warning only — low risk), `_on_resource_patch_failed` retry path, `_holistic_handler`'s `PebbleError` catch, or `TracingData.load()` with `is_ready=True`/`get_endpoint=None`
  - `test_configs.py` doesn't test proxy env vars, `postgresql_*` bool-to-string conversion beyond existing cases, or `task_default_time_limit=0`/`task_expiration_days=0` (would fail at binary level, not charm level, but a test would document expected crash behaviour)
- **Ops version issue**: fails to collect under ops 3.8.1 (`AttributeError: module 'ops.testing' has no attribute 'WaitingStatus'`); `uv pip install pytest pytest-mock` upgrades ops to 3.8.1 and breaks the suite. System Python (ops 3.8.0) works.
- **Framework**: `ops.testing` Scenario API, clean mocking via `pytest-mock`, `create_state()` factory.

### Integration tests: could not run in this environment
- **Location**: `tests/integration/test_charm.py`
- **Framework**: `jubilant` + `pytest-jubilant` (via `uv sync --extra integration`)
- **Result**: `ModuleNotFoundError: No module named 'jubilant'` without extras; `ImportError: No module named 'src'` with extras due to a pytest `pythonpath` issue not applying when run from a subdirectory. Running via `pytest.main()` with working directory at repo root works around it.
- **Tests defined**: `test_build_and_deploy`, `test_workload_is_running`, `test_scale_up`, `test_remove_integration`, `test_scale_down`, `test_remove_application`
- **Assertions**: use `jubilant.wait()` with `StatusPredicate` functions, asserting on status transitions rather than just "wait for active."
- **Coverage**: `test_remove_integration` covers cluster relation removal (blocked → active); `test_scale_up`/`test_scale_down` cover lifecycle; `test_remove_application` covers teardown. Missing: config-change with bad values, tracing integration, TLS.

### Linter output
```
$ ruff check src/
All checks passed!

$ codespell -S .git,__pycache__,*.charm,lib/charms -L te,ans,ansync,bu,hist,parm,py:
(no output)

$ mypy src/
src/services.py:104: error: Value of "environment" has incompatible type "dict[str, str | bool]"
src/configs.py:24: error: Dict entry 0 has incompatible type "str": "int | float | str"
src/configs.py:44: error: Incompatible types in assignment (expression has type "int | float | str")
src/configs.py:46: error: Incompatible types in assignment (expression has type "int | float | str")
src/configs.py:48: error: Incompatible types in assignment (expression has type "int | float | str")
Found 5 errors in 2 files (checked 8 source files)
```

## Docs

- `README.md`: good usage examples, deployment instructions, logging/metrics/tracing integration examples, security section. Matches observed behaviour. ✓
- `CONTRIBUTING.md`: standard Juju SDK contributing guide. ✓
- `SECURITY.md`: one-paragraph security reporting policy. ✓
- `charmcraft.yaml description`: "Operator for Authentik Worker" — minimal but accurate; Charmhub description gives no detail on background tasks, email delivery, or outposts.
- `charmcraft.yaml config.options.log_level.description` documents valid values that aren't enforced in code (see findings).
- `charmcraft.yaml links` — `authenik` typo, both `source` and `issues` (see findings).
- `terraform/MODULE_SPECS.md`: auto-generated terraform-docs output, correct. ✓
- Gap: no `docs/` directory, no architecture diagram, no runbook for blocked scenarios.
- Gap: no documentation that `tempo-coordinator-k8s` needs a separate worker provider — operators may deploy it expecting it to work directly with `authentik-worker`, only to find it blocked.

## Open questions

1. **Is `AUTHENTIK_POSTGRESQL__USE_PGBOUNCER` meant to be a local config or server-provided?** Commit `246de2f`'s message says "the declaration belongs to the server, which owns the pg-database relation," but local source still has `postgresql_disable_server_side_cursors` as a local config. Does the server need to also publish `db-use-pgbouncer` for the worker to use it, and are these two options related?
2. **`postgresql-k8s` incompatible with Juju 4.x**: CI uses `concierge-k8s-3` (Juju 3.6), but `concierge-k8s-4` (Juju 4.0.12) rejects `postgresql-k8s 16/stable`. The charm cannot be tested against Juju 4.x with the full integration stack.
3. **`tempo-coordinator-k8s`'s "worker relation" requirement**: after connecting to `authentik-worker`, the coordinator stays blocked with "Missing any worker relation." Does it need a separate Tempo worker backend (e.g., `tempo-k8s`)? The `authentik-worker` tracing integration connects but doesn't satisfy the coordinator's worker requirement.
4. **What else is in the 44 commits ahead?** Key commits between local HEAD (`11d4b61`) and `origin/main` (`e0fac03`): `baa390c` (cache workload version), `f76e6ec` (add_layer try/except, version status visibility), `21cc013` (METRICS_PORT=9300, COS metrics, dashboard, alert rules), `d288f8a` (read replicas), `5f3060c` (prompt worker status on version mismatch), `246de2f` (PgBouncer flag), `c18adba` (terraform fixes), `14c411b` (release 1.1.0). Local source is not deployable as-is.
5. **Tracing `is_ready` edge case**: could not be reproduced live because `tempo-coordinator-k8s` was blocked with empty relation data, forcing `is_ready() == False`. Reproducing it would require a tracing provider that publishes structurally valid but incomplete data (a `receivers` list lacking `otlp_http`). Currently a theoretical edge case grounded in reading the tracing library, marked `(unverified)` in the live deployment.
6. **Scale relation disconnect**: was the transient `grafana-agent-k8s` blocked state during the 1→3 scale expected Juju behaviour, or a timing issue in the charm's or library's relation handling? Not reproduced consistently.
</content>
