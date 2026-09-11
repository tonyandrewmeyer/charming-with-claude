# identity-platform-login-ui-operator

A Kubernetes charm deploying the Identity Platform Login UI — a Go HTTP service that proxies Ory Kratos/Hydra self-service flows and serves the login UI frontend. The charm code is a cleanly-architected thin integration layer (frozen dataclasses, a single holistic reconciler, well-separated `PebbleService`), but it has serious correctness problems in production-critical paths: a critical `BASE_URL` corruption bug on Juju 4.x re-integration, caused by the charm bypassing the `traefik_route` library's stored-state properties and reading raw relation data instead; the workload can die and stay `ActiveStatus` indefinitely (Pebble `startup: disabled` combined with a health check that can never trigger a restart); `BlockedStatus` from resource-patch failures is silently overwritten by `_holistic_handler`; the charm emits broken URLs (`https:///ui/login`, or bare `/ui/login`) via `ui-endpoint-info` to downstream charms when `BASE_URL` is corrupted or absent; there is no `log_level` config validation; and pyright reports 24 type errors, several of which are live crash risks (`BlockedStatus(None)`, `.get()` on `None`). A maintainer should fix the `BASE_URL`/`is_ready()` race first (findings #1–#3) since it corrupts data sent to every downstream identity-platform charm, then fix the dead-workload-stays-active and status-overwrite bugs (#4–#5), before turning to the type errors and test gaps.

| | |
|---|---|
| Repo | canonical/identity-platform-login-ui-operator @ `7d3f101` (2026-07-21) |
| Charms | identity-platform-login-ui-operator |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5): edge rev 205, stable rev 197; concierge-k8s-3 (Juju 3.6.25): edge rev 205. Also tested with traefik-k8s, self-signed-certificates, grafana-agent-k8s, kratos, hydra, postgresql-k8s, tempo-k8s. **Pebble note**: the workload pebble daemon listens at `/charm/containers/login-ui/pebble.socket`, not the default `/var/lib/pebble/default/.pebble.socket`; all pebble commands in this review used `PEBBLE_SOCKET` to target the correct daemon. |
| Reviewed | 2026-08-10 |

## What it does

The charm runs a single container (`login-ui`) based on `ghcr.io/canonical/identity-platform-login-ui`. It:

- Exposes a login/consent/registration/settings/verification UI over port 8080
- Proxies requests to Kratos and Hydra backends (via `kratos-info` and `hydra-endpoint-info` relations)
- Configures a Traefik `traefik_route` (raw mode) with a Jinja2 template including TLS domain routing for `/ui`, `/api/*`, and `/self-service`
- Provides `ui-endpoint-info` to downstream charms
- Integrates with COS (metrics, grafana dashboards, loki log forwarding), Tempo tracing, certificate transfer, and tenant-service multitenancy
- Has config options for `log_level`, `cpu`/`memory` resource limits, and `support_email`
- Stores a cookie encryption key in peer relation data
- Patches Kubernetes resource requests/limits via `KubernetesComputeResourcesPatch`

## Deployment log

### Juju 4.0.5 (concierge-k8s-4) — round 1: basic lifecycle

```
$ juju add-model rv-login-ui-k8s4 --controller concierge-k8s-4
$ juju deploy identity-platform-login-ui-operator --channel edge --trust
$ juju deploy traefik-k8s traefik-public --channel latest/stable --trust \
    --config external_hostname=public.test
$ juju integrate identity-platform-login-ui-operator:public-route traefik-public
```

**First integration**: both charms reached active/idle within ~40s. `BASE_URL = https://public.test`. Pebble plan correct. Workload version 0.28.0. Workload logged errors every 10s: `Get "/health/ready": unsupported protocol scheme ""` — `KRATOS_ADMIN_URL`/`HYDRA_ADMIN_URL` empty (no Kratos/Hydra relations).

**Re-integration on 4.x**: removed `public-route` → charm stayed active. Re-integrated → charm stayed active, BUT `BASE_URL` became `https://` (empty hostname). Traefik remained active (the stale config still routes).

**Scale-up**: scaled to 2 units → both active. Cookie encryption key shared via peer data.

**Kill workload**: `pebble stop login-ui` → charm stayed `ActiveStatus` with dead workload. `startup: disabled` prevents Pebble auto-restart. Recovered on next config change.

**Config change**: `juju config log_level=debug` → 2 `config-changed` hooks fired. `juju config log_level=INVALID_VALUE` → accepted without rejection, `LOG_LEVEL: INVALID_VALUE` in pebble env. `juju config cpu=100m memory=256Mi` → pod restarted. `juju config log_level=critical` → applied correctly.

**Actions**: none defined.

### Juju 4.0.5 (concierge-k8s-4) — round 2: deeper integrations and failure testing

```
$ juju add-model rv-login-ui-deep --controller concierge-k8s-4
$ juju deploy identity-platform-login-ui-operator --channel edge --trust
$ juju deploy traefik-k8s traefik --channel latest/stable --trust --config external_hostname=deep.test
$ juju deploy self-signed-certificates --channel latest/stable
$ juju deploy grafana-agent-k8s --channel 1/stable --trust
$ juju integrate identity-platform-login-ui-operator:public-route traefik
$ juju integrate identity-platform-login-ui-operator:logging grafana-agent-k8s:logging-provider
$ juju integrate identity-platform-login-ui-operator:metrics-endpoint grafana-agent-k8s:metrics-endpoint
$ juju integrate identity-platform-login-ui-operator:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
$ juju integrate identity-platform-login-ui-operator:receive-ca-cert self-signed-certificates
```

**First integration**: `BASE_URL = https://deep.test`. Log forwarding to grafana-agent configured in the pebble plan (loki target URL). Metrics and grafana-dashboard relations connected. Cert transfer succeeded — `update-ca-certificates` exists in the workload container's base image (Ubuntu 22.04).

**Re-integration on 4.x (confirmed)**: removed `public-route` → `BASE_URL` became `https://`. Re-integrated → `BASE_URL` stayed `https://`, not recovered. Traefik config submitted as empty `{}`. Error logged 8 times: "External hostname is not set on the ingress provider".

**Re-integration after pod restart**: deleted the pod → new pod started, charm recovered peer data (cookie key preserved), pebble layer re-rendered, but `BASE_URL` remained `https://`.

**Invalid config**: `cpu=notacpu` → resource-patch failure logged `BlockedStatus` at 08:34:19 and 08:34:22, but final status was `ActiveStatus` — the blocked status was overwritten by `_holistic_handler`.

**Downgrade refresh**: `juju refresh --channel latest/stable` (rev 205→197, workload 0.28.0→0.24.1) on 2 units → completed cleanly. Cookie key preserved. Both units active.

**Scale-down then remove**: scale 2→1 clean. `remove-application --force --no-wait` removed cleanly, no orphaned resources.

### Juju 3.6.25 (concierge-k8s-3)

```
$ juju add-model rv-login-ui-k8s3 --controller concierge-k8s-3
$ juju deploy identity-platform-login-ui-operator --channel edge --trust
$ juju deploy traefik-k8s traefik-public3 --channel latest/stable --trust \
    --config external_hostname=public3.test
$ juju integrate identity-platform-login-ui-operator:public-route traefik-public3
```

**First integration**: same as 4.x — `BASE_URL = https://public3.test`.

**Re-integration on 3.6**: removed the relation, re-integrated — **`BASE_URL` remained `https://public3.test`** (NOT corrupted). Event ordering on 3.6 allows Traefik to set `external_host` before the charm's handler reads it.

**Config changes and kill workload**: same as 4.x — no `log_level` validation, `startup: disabled`, `ActiveStatus` with dead workload. `cpu=notacpu` → same `BlockedStatus`-overwrite pattern.

### Juju 4.0.5 — full-stack deployment with Kratos and Hydra

```
$ juju add-model rv-login-ui-full --controller concierge-k8s-4
$ juju deploy identity-platform-login-ui-operator --channel edge --trust
$ juju deploy traefik-k8s traefik --channel latest/stable --trust --config external_hostname=full.test
$ juju deploy kratos --channel latest/edge --trust
$ juju deploy hydra --channel latest/edge --trust
$ juju deploy postgresql-k8s --channel latest/stable --trust
$ juju deploy tempo-k8s --channel latest/edge --trust
$ juju integrate identity-platform-login-ui-operator:public-route traefik
$ juju integrate identity-platform-login-ui-operator:kratos-info kratos
$ juju integrate identity-platform-login-ui-operator:hydra-endpoint-info hydra
$ juju integrate identity-platform-login-ui-operator:tracing tempo-k8s
```

**Results**: Kratos and Hydra both went to `BlockedStatus("Missing integration pg-database")` — postgresql-k8s failed with `hook failed: "leader-elected"` (Juju 4.x incompatibility, rev 20). Kratos published empty `application-data: {}` on `kratos-info`. The login-ui charm stayed `ActiveStatus` despite `KRATOS_ADMIN_URL: ""` and `KRATOS_PUBLIC_URL: ""` in the pebble env. `HYDRA_ADMIN_URL` was correctly populated (Hydra publishes its endpoint data even when blocked). Tempo tracing succeeded — `OTEL_HTTP_ENDPOINT`, `OTEL_GRPC_ENDPOINT`, `TRACING_ENABLED: true` all set. However, `OTEL_GRPC_ENDPOINT` was `tempo-k8s-0...:4317` **without an `http://` scheme prefix**, while `OTEL_HTTP_ENDPOINT` had one.

**Workload errors (every 10s)**:
- `Get "/health/ready": unsupported protocol scheme ""` — `KRATOS_ADMIN_URL` empty
- `Get "http://hydra...:4445/health/ready": connect: connection refused` — Hydra not running
- `traces export: ... dial tcp 10.1.0.92:4317: connect: connection refused` — Tempo not ready yet

| Metric | Value |
|---|---|
| Charm size (from charmhub) | ~208 KB (charm file) |
| Memory (workload pod) | 46 Mi |
| CPU (workload pod) | ~1m idle, 91m at startup |
| Deploy to active (first) | ~30-40s |
| Deploy to active (re-integration Juju 3.6) | ~10s |
| Hooks per config change | 2 (`config-changed` fires twice) |
| Juju 4.x vs 3.6 difference | `BASE_URL` corrupted on 4.x re-integration, correct on 3.6 |
| Pebble socket | `/charm/containers/login-ui/pebble.socket` (not default `/var/lib/pebble/default/.pebble.socket`) |

### Juju 4.0.5 — `ui-endpoint-info` data observation (rv-login-ui-final model)

```
$ juju add-model rv-login-ui-final --controller concierge-k8s-4
$ juju deploy identity-platform-login-ui-operator --channel edge --trust
$ juju deploy kratos --channel latest/edge --trust
$ juju integrate identity-platform-login-ui-operator:ui-endpoint-info kratos
```

**Without public-route**: Kratos went to `BlockedStatus("Missing integration pg-database")`. Login-ui stayed `ActiveStatus`. `ui-endpoint-info` databag contained **relative URLs only**: `/ui/login`, `/ui/consent`, `/ui/error`, etc. — no scheme or hostname, broken for any downstream charm that constructs redirect URIs.

**After adding traefik** (`external_hostname=final.test`, `public-route` integrated): `ui-endpoint-info` databag updated to **fully-qualified URLs**: `https://final.test/ui/login`, `https://final.test/ui/consent`, etc. Correct.

**`LoginUIEndpointsProvider` behaviour**: uses `model_dump(exclude_none=True)` (`lib/charms/identity_platform_login_ui_operator/v0/login_ui_endpoints.py:95`), which would drop `None` values — but the charm sends empty strings, not `None`, so all 12 URL keys are always present, including when they contain broken relative paths.

## Observed behaviour

- **`BASE_URL` corruption on Juju 4.x re-integration**: after removing and re-adding the `public-route` relation on Juju 4.0.5, `BASE_URL` becomes `https://` (empty hostname). This does NOT happen on Juju 3.6.25. Root cause: (1) `TraefikRouteRequirer.is_ready()` only checks `_relation is not None` (`lib/charms/traefik_k8s/v0/traefik_route.py:413`); (2) `_on_public_route_changed` assigns `event.relation` before Traefik publishes `external_host` (`src/charm.py:248`); (3) the charm's `_external_host()`/`_scheme()` (`src/integrations.py:112-127`) read raw relation data instead of the library's stored-state-backed `requirer.external_host`/`requirer.scheme` properties. Confirmed in three separate Juju 4.x deployments.
- **Pebble `startup: disabled` + health check**: the service has `startup: disabled` (`src/services.py:83`) but also a health check. Pebble won't auto-restart a disabled service even if it fails the check. When the process was killed, `pebble services` showed `inactive` while the charm showed `ActiveStatus`.
- **Persistent ERROR logs from health probes**: every 10 seconds the workload logs errors for empty backend URLs and unreachable backends; the charm reports `ActiveStatus` throughout.
- **`ActiveStatus` despite missing backends**: when Kratos is blocked (no postgresql) and publishes empty `application-data: {}` on `kratos-info`, `KratosInfoRequirer.is_ready()` returns `False` (`lib/charms/kratos/v0/kratos_info.py:148`), and `KratosInfoData.load()` returns defaults with empty strings. The charm stays `ActiveStatus` with `KRATOS_ADMIN_URL: ""`.
- **Workload restarted on every relation/config change**: multiple "Instance stopped"/"New instance spawned" cycles in pebble logs during a single config change — `_restart_service` (`src/services.py:57-63`) always replays the pebble layer, causing a restart even when the layer is unchanged.
- **Resource-patch failure `BlockedStatus` overwritten**: setting `cpu=notacpu` triggered `_on_resource_patch_failed` → `BlockedStatus` (`src/charm.py:268-270`), but `_holistic_handler` (called from `_on_config_changed`) ended with `ActiveStatus()` (`src/charm.py:246`), overwriting it. The operator sees `ActiveStatus` despite broken resource config.
- **`TraefikRouteRequirer.is_ready()` is just `_relation is not None`** (`lib/charms/traefik_k8s/v0/traefik_route.py:413`): does NOT validate that the remote side has provided data. The charm gates `_domain_url` on this (`src/charm.py:295`), trusting it means data is available. The library's own `external_host`/`scheme` properties use StoredState with fallback to preserve last known values — the charm bypasses them.
- **Template rendered with empty `external_host`**: when the race triggers, `PublicRouteData.load()` logs an error and returns `cls()` with empty config (`src/integrations.py:150`). But `_domain_url` separately calls `normalise_url(str(URL()))`, which produces `"https://"` (`src/charm.py:293-299`).
- **Cert transfer pushes empty CA bundle**: `push_ca_certs()` (`src/certificate_transfer_integration.py:57-65`) writes the bundle file and calls `container.push()` even when the bundle is empty — unnecessary I/O on every hook event.
- **`_update_login_ui_endpoint_relation_data` sends garbled or relative URLs**: when `_domain_url` returns `"https://"` (corrupted), URLs like `"https:///ui/login"` are sent via `ui-endpoint-info` (`src/charm.py:296-312`). When `_domain_url` returns `None` (no `public-route` relation), relative URLs like `/ui/login` are sent. Confirmed in deployment: without a `public-route` relation the `ui-endpoint-info` databag contained only relative paths.
- **`OTEL_GRPC_ENDPOINT` missing scheme**: tracing integration produces `OTEL_GRPC_ENDPOINT: tempo-k8s-0...:4317` without an `http://` prefix, while `OTEL_HTTP_ENDPOINT` has it. Caused by `urlparse()` on a schemeless URL in `TracingData.load()` (`src/integrations.py:100-101`).
- **Pod restart recovers cleanly**: after deleting the pod, the charm recovered peer data (cookie key preserved), pebble layer re-rendered correctly.
- **Downgrade refresh clean**: `edge` rev 205 → `stable` rev 197 completed on 2 units without errors. Cookie key preserved. Workload restarted with new image.
- **Ruff clean, codespell clean**: no lint violations. pyright reports 24 type errors.
- **Unit tests pass via tox**: all 21 pass with 88% line coverage under `tox -e unit` (the `conftest.py` autouse fixture patches `subprocess.run`). Running outside tox may fail because `update-ca-certificates` is not present. Coverage gaps map directly onto several findings below.

## Findings

### 1. `BASE_URL` silently becomes `https://` when public-route data is missing (Juju 4.x specific)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:293-299`, `src/integrations.py:129-150`, `src/utils.py:14-35`
- **Evidence**: `_domain_url` computes `normalise_url(str(PublicRouteData.load(self.public_route).url))`. When `is_ready()` is `True` but `external_host` is empty, `PublicRouteData.load()` returns `cls()` (`src/integrations.py:150`) with `url=URL()` (empty). `str(URL())` is `""`, and `normalise_url("")` produces `"https://"`. Observed in three Juju 4.x deployments; does NOT happen on Juju 3.6.
- **Impact**: A broken `BASE_URL` corrupts all redirects, CORS origins, OAuth2 callback URLs, and cookie domains, and propagates garbled URLs (`https:///ui/login`) via `ui-endpoint-info` to downstream charms.
- **Fix**: `_domain_url` should validate the URL has a non-empty host. `PublicRouteData.load()` should not return a usable object when `external_host` is empty. The charm should go to `WaitingStatus("Waiting for Traefik external hostname")` until the host is available.
- **Linter rule**: not mechanically checkable.

### 2. `TraefikRouteRequirer.is_ready()` is a trivial `_relation is not None` check — root cause of the BASE_URL bug
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/traefik_k8s/v0/traefik_route.py:413`
- **Evidence**: `is_ready()` returns `self._relation is not None` — nothing about whether Traefik has published `external_host`. The charm gates on `is_ready()` (`src/charm.py:295`), trusting it means "data is available." When `_on_public_route_changed` sets `_relation = event.relation` (`src/charm.py:248`), `is_ready()` returns `True` immediately, before Traefik populates the databag.
- **Impact**: Direct root cause of finding #1. The library's own `external_host` property (`traefik_route.py:357`) uses StoredState with fallback to preserve the last known value across relation churn — the charm bypasses it entirely.
- **Fix**: use `requirer.external_host` and `requirer.scheme` instead of relying on `is_ready()` alone. The library's `is_ready()` should also validate that data exists, or at minimum document that it does not mean data is available.
- **Linter rule**: not mechanically checkable.

### 3. `_external_host()` and `_scheme()` bypass library stored state, reading raw relation data
- **Severity**: high
- **Kind**: bug
- **Where**: `src/integrations.py:112-127`
- **Evidence**: `_external_host` and `_scheme` read directly from `relation.data[relation.app]` instead of using `requirer.external_host`/`requirer.scheme`, which are backed by `_stored` state (`traefik_route.py:342-350`) with fallback. The raw reads are racy and return empty strings during early relation lifecycle on Juju 4.x.
- **Impact**: Direct trigger of finding #1 on Juju 4.x — the library already solved this with StoredState, but the charm reimplements it incorrectly.
- **Fix**: replace `cls._external_host(requirer)` with `requirer.external_host`, and `cls._scheme(requirer)` with `requirer.scheme`.
- **Linter rule**: "duplicate implementation of library-provided property" — not mechanically checkable.

### 4. Resource-patch failure `BlockedStatus` is overwritten by `_holistic_handler`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:268` (`_on_resource_patch_failed`), `src/charm.py:246` (`_holistic_handler` final status)
- **Evidence**: `_on_resource_patch_failed` sets `self.unit.status = BlockedStatus(event.message)`. `_holistic_handler` always ends with `self.unit.status = ActiveStatus()`. Setting `cpu=notacpu` caused `BlockedStatus` at 08:34:19/08:34:22 in debug-log, but final status was `active`.
- **Impact**: Operators see `ActiveStatus` despite a broken resource configuration, with no indication the `cpu=notacpu` value was rejected.
- **Fix**: `_holistic_handler` should not unconditionally set `ActiveStatus`; it should check for a resource-patch failure flag or preserve the last error status.
- **Linter rule**: not mechanically checkable.

### 5. Workload process death is not detected or recovered — `startup: disabled` with health check
- **Severity**: high
- **Kind**: bug
- **Where**: `src/services.py:83` (`startup: disabled`), `src/services.py:125` (`login-ui-alive` check), `src/services.py:57-63` (`_restart_service`)
- **Evidence**: killing the login-ui pebble service left the charm `ActiveStatus`. The pebble layer defines a `login-ui-alive` health check, but `startup: disabled` means Pebble won't restart a stopped service even if the check fails. `_holistic_handler` runs on `update-status` every 5 min, which would restart it — but until then the workload stays dead with `ActiveStatus`.
- **Impact**: A crashed workload can stay dead for up to 5 minutes with no status signal.
- **Fix**: change `startup` to `enabled` so Pebble auto-restarts on check failure, or have `_holistic_handler` set `WaitingStatus`/`BlockedStatus` when the service is not running.
- **Linter rule**: "Pebble service has health check but `startup: disabled`" — mechanically checkable.

### 6. `push_ca_certs()` calls `subprocess.run("update-ca-certificates")` unconditionally
- **Severity**: high
- **Kind**: bug
- **Where**: `src/certificate_transfer_integration.py:62`
- **Evidence**: `subprocess.run(["update-ca-certificates", "--fresh"], capture_output=True)`, called from `_holistic_handler` (`src/charm.py:236`) on every hook event. `update-ca-certificates` is part of the `ca-certificates` package, present in the workload base image but not guaranteed elsewhere. The `conftest.py` autouse fixture patches `subprocess.run`, so `tox -e unit` passes; running outside tox or with a different base image would crash every hook with `FileNotFoundError`.
- **Impact**: an unhandled `FileNotFoundError` in `_holistic_handler` would crash every hook; the `except PebbleServiceError` guard only catches pebble errors, not subprocess failures.
- **Fix**: catch `FileNotFoundError`/`subprocess.CalledProcessError` around the call, or skip the write/subprocess/push entirely when the CA bundle is empty.
- **Linter rule**: "subprocess.run called without explicit error handling" — mechanically checkable.

### 7. `push_ca_certs()` calls `container.push()` without a `can_connect()` guard from the cert event path
- **Severity**: high
- **Kind**: bug
- **Where**: `src/certificate_transfer_integration.py:63,73`, `src/charm.py:131`
- **Evidence**: `push_ca_certs()` is called both from `_holistic_handler` (which checks `can_connect()`) and from `_on_certificate_event` (`src/certificate_transfer_integration.py:73`), which calls `self.push_ca_certs()` before `self.callback_fn(event)` (`_holistic_handler`). The `container.push()` inside `push_ca_certs()` therefore runs before any `can_connect()` check on this path.
- **Impact**: an uncaught `ConnectionError` instead of a deferred event or `WaitingStatus`.
- **Fix**: add a `can_connect()` check at the start of `push_ca_certs()`, or reorder `_on_certificate_event` to call `callback_fn` first.
- **Linter rule**: "hook handler calls `container.push()` without `can_connect()` guard" — mechanically checkable.

### 8. Pyright type errors, several of which can crash at runtime
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py`, `src/integrations.py`, `src/services.py` (24 errors total)
- **Evidence**: crash-capable issues include: `src/charm.py:92` (`Relation | None` passed where `Relation` expected); `src/charm.py:270` (`event.message` could be `None` — `BlockedStatus(None)` would crash); `src/charm.py:286,290` (`config.get()` returns `bool | int | float | str | None`, not `str`); `src/charm.py:303-304` (`Optional[str]` passed where `str` required in `render_pebble_layer`); `src/integrations.py:72-78` (`.get()` on possibly `None` from `get_kratos_info()`); `src/integrations.py:100-101` (`urlparse().geturl()` returns `bytes | str`, not `str`); `src/integrations.py:114,116,122,124` (`None` returned where `str` expected).
- **Impact**: several of these can crash at runtime — `BlockedStatus(None)`, `.get()` on `None`, `None` passed into `render_pebble_layer`.
- **Fix**: add explicit `None` guards or adjust type annotations.
- **Linter rule**: mechanically checkable by pyright.

### 9. Integration test only validates `ActiveStatus`, not data correctness — testing the bug
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py:167-172` (`public_route_relation` fixture, no `remote_app_data`), `tests/unit/conftest.py:100-104` (autouse fixture patches `subprocess.run`), `tests/unit/test_charm.py:241-247` (`test_traefik_route_integration`)
- **Evidence**: `public_route_relation` has no `remote_app_data` (no `external_host`, no `scheme`). The test only asserts `state_out.unit_status == ActiveStatus()`. `external_host` is empty, `PublicRouteData.load()` returns empty config, and the test treats this as "working" because status is `ActiveStatus`. `test_public_route_changed`/`test_public_route_broken` do the same.
- **Impact**: the most dangerous code path (missing `external_host`) passes the test suite; realistic `remote_app_data` and env-var assertions would have caught findings #1 and #3 in CI.
- **Fix**: add realistic `remote_app_data` with `external_host`/`scheme`. Assert on `BASE_URL` in the pebble layer env. Add a separate test for missing `external_host` asserting `WaitingStatus`.
- **Linter rule**: not mechanically checkable.

### 10. Integration tests do not exercise kratos or hydra relations
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py`, `tests/integration/conftest.py` (`integrate_dependencies`)
- **Evidence**: `integrate_dependencies()` only wires up `public-route` to traefik; no kratos, hydra, or other backend. `test_has_ingress` only checks `/ui/login` returns 200, not that it proxies to any backend. The charm's core proxying function is never tested.
- **Impact**: integration tests can't catch issues like empty `KRATOS_ADMIN_URL` when Kratos is blocked, missing status transitions, or incorrect backend URL construction.
- **Fix**: add kratos and hydra to integration test dependencies; test with both available and unavailable backends.
- **Linter rule**: not mechanically checkable.

### 11. `ui-endpoint-info` sends relative URLs when no `public-route` relation exists
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:324`
- **Evidence**: `endpoint = self._domain_url or ""`. When `_domain_url` is `None` (no `public-route` relation), `endpoint` is `""`, so all URLs in `send_endpoints_relation_data()` become relative paths. Confirmed in deployment: with only `ui-endpoint-info` connected to kratos and no `public-route`, the databag contained `login_url: /ui/login`, `consent_url: /ui/consent`, etc.
- **Impact**: downstream charms (kratos, hydra, admin-ui) receive unusable relative URLs before ingress is configured. `LoginUIEndpointsProvider`'s `model_dump(exclude_none=True)` (`lib/charms/identity_platform_login_ui_operator/v0/login_ui_endpoints.py:95`) would drop `None` values, but the charm sends `""` instead.
- **Fix**: skip sending data when `_domain_url` is empty/`None`, or send `None` instead of `""` so `exclude_none=True` drops the keys.
- **Linter rule**: not mechanically checkable.

### 12. `_update_login_ui_endpoint_relation_data` sends garbled URLs when `_domain_url` is corrupted
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:296-312`
- **Evidence**: when `_domain_url` returns `"https://"` (finding #1), URLs like `https:///ui/login` are sent via `ui-endpoint-info`.
- **Impact**: downstream charms (Kratos, Hydra, Admin UI) receive broken redirect URLs, breaking login flows platform-wide.
- **Fix**: guard on the URL having a non-empty host before sending; don't send relative or scheme-only URLs.
- **Linter rule**: not mechanically checkable.

### 13. No config validation for `log_level`
- **Severity**: medium
- **Kind**: ux
- **Where**: `charmcraft.yaml:100-104`, `src/charm.py:282-283`
- **Evidence**: description says "Acceptable values are: info, debug, warning, error and critical" but there's no `enum` constraint. `juju config log_level=INVALID_VALUE` was accepted; `LOG_LEVEL: INVALID_VALUE` appeared in the pebble env.
- **Impact**: operators get no feedback on misconfiguration; the workload may behave unpredictably.
- **Fix**: add `enum: [info, debug, warning, error, critical]` in `charmcraft.yaml`.
- **Linter rule**: "config option describes allowed values in prose but has no `enum` constraint" — mechanically checkable.

### 14. `ActiveStatus` with empty backend URLs — no distinction between "no relation" and "backend not ready"
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:246` (unconditional `ActiveStatus()`), `src/integrations.py:61-81` (`KratosInfoData.load` empty defaults)
- **Evidence**: when Kratos is blocked (no pg-database) it publishes empty `application-data: {}` on `kratos-info`. `KratosInfoRequirer.is_ready()` returns `False` (`lib/charms/kratos/v0/kratos_info.py:148`), `KratosInfoData.load()` returns all-empty defaults, and the workload logs `Get "/health/ready": unsupported protocol scheme ""` every 10s while the charm stays `ActiveStatus`.
- **Impact**: operators can't tell from `juju status` whether the login UI is actually functional.
- **Fix**: go to `BlockedStatus` or at least `WaitingStatus` when backend relations exist but backends aren't ready.
- **Linter rule**: not mechanically checkable.

### 15. `OTEL_GRPC_ENDPOINT` missing `http://` scheme
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/integrations.py:100-101`
- **Evidence**: `urlparse(requirer.get_endpoint("otlp_grpc"))` is called on a schemeless URL (`tempo-k8s-0...:4317`); the result lacks `http://`, while `OTEL_HTTP_ENDPOINT` has it (observed in pebble env).
- **Impact**: the gRPC client may fail to connect if it requires a scheme; at minimum this is an inconsistency between the two endpoint env vars.
- **Fix**: ensure the gRPC endpoint has a scheme before calling `urlparse()`; default to `http://` if absent.
- **Linter rule**: not mechanically checkable.

### 16. `push_ca_certs()` pushes empty CA bundle to container on every hook
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/certificate_transfer_integration.py:57-65`
- **Evidence**: `push_ca_certs()` writes the bundle to disk and calls `container.push()`/`subprocess.run()` even when the bundle is empty (no certificate-transfer relations); `_holistic_handler` calls this on every hook.
- **Impact**: unnecessary disk I/O, subprocess call, and container interaction on every hook.
- **Fix**: skip the write, subprocess call, and push when the bundle is empty.
- **Linter rule**: not mechanically checkable.

### 17. `_on_public_route_changed` manually assigns to a library private attribute
- **Severity**: medium
- **Kind**: lint
- **Where**: `src/charm.py:252`
- **Evidence**: `self.public_route._relation = event.relation` — direct assignment to a private attribute of the library object, with a comment noting it's a workaround for how the library handles the event.
- **Impact**: fragile coupling to library internals; a library update could break this. This pattern is also what enables finding #1 by bypassing the library's lifecycle management.
- **Fix**: upstream a fix to `traefik_route` for relation-joined handling, or use the public API only.
- **Linter rule**: "access to private member of library object" — mechanically checkable.

### 18. README documents stale `ingress` relation instead of `public-route`
- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md:50-61`
- **Evidence**: documents `juju integrate traefik-admin identity-platform-login-ui-operator:ingress` — the `ingress` relation was replaced by `public-route` in v2.0.0 (per `CHANGELOG.md`).
- **Impact**: operators following the README get a relation-not-found error.
- **Fix**: update to `juju integrate identity-platform-login-ui-operator:public-route traefik-k8s`.
- **Linter rule**: not mechanically checkable.

### 19. Terraform module has `resources` attribute commented out
- **Severity**: medium
- **Kind**: bug
- **Where**: `terraform/main.tf:21`
- **Evidence**: `# resources   = local.resources` is commented out. `local.resources` correctly merges `local.oci_image` (from `charmcraft.yaml`) with `var.resources`, but the result is never passed to `juju_application`. Charmhub-based deploys auto-resolve OCI image resources, but local deployments or custom-image deployments would fail without this.
- **Impact**: operators deploying via terraform with a locally-built charm or custom image get a resource-not-found error.
- **Fix**: uncomment the line, or document why it's commented out and how resources are resolved instead.
- **Linter rule**: not mechanically checkable.

### 20. Template file opened with relative path
- **Severity**: low
- **Kind**: bug
- **Where**: `src/integrations.py:136`
- **Evidence**: `with open("templates/public-route.json.j2", "r") as file:` — relative to CWD, not `__file__`.
- **Impact**: fragile in non-standard environments; works today because Juju sets CWD to the charm root.
- **Fix**: use `Path(__file__).parent.parent / "templates" / ...`.
- **Linter rule**: "file open with relative path not anchored to `__file__`" — mechanically checkable.

### 21. `_restart_service` has dead code for `restart=True` parameter
- **Severity**: low
- **Kind**: bug
- **Where**: `src/services.py:57-63`
- **Evidence**: the `restart` parameter is never passed as `True` by any caller; `plan()` calls `_restart_service()` with no arguments. The `restart` branch has 0% coverage.
- **Impact**: dead code obscuring intended behaviour.
- **Fix**: remove the parameter and dead branch, or wire it up.
- **Linter rule**: "function parameter never passed by callers" — mechanically checkable (pyright/vulture).

### 22. `leader_unit` decorator defined but never used
- **Severity**: low
- **Kind**: lint
- **Where**: `src/utils.py:45-55`
- **Evidence**: defined but not imported or used anywhere; 0% coverage.
- **Impact**: dead code.
- **Fix**: remove or use it.
- **Linter rule**: "unused function" — mechanically checkable (pyright/ruff).

### 23. No config validation for `cpu` and `memory`
- **Severity**: low
- **Kind**: ux
- **Where**: `charmcraft.yaml:84-95`
- **Evidence**: `cpu`/`memory` accept arbitrary strings; `cpu=notacpu` was accepted and caused a resource-patch failure whose status was subsequently overwritten (finding #4). No `pattern` constraint in `charmcraft.yaml`.
- **Impact**: invalid values reach the Kubernetes patch layer with no upfront validation.
- **Fix**: add regex `pattern` constraints (e.g. `\d+m` for cpu, `\d+[KMG]i` for memory).
- **Linter rule**: "config option with resource semantics has no `pattern` constraint" — mechanically checkable.

### 24. No actions defined
- **Severity**: low
- **Kind**: ux
- **Where**: `charmcraft.yaml` — no `actions` section
- **Evidence**: `juju actions` returns nothing; no way to restart the workload without a config change or `kubectl exec`.
- **Fix**: add at minimum a `restart` action.
- **Linter rule**: "charm has no actions defined" — mechanically checkable.

### 25. Workload restarts on every hook even when config unchanged
- **Severity**: low
- **Kind**: performance
- **Where**: `src/services.py:57-63` (`_restart_service`), `src/services.py:133-138` (`plan`)
- **Evidence**: every `_holistic_handler` call goes through `plan()` → `_restart_service()` → `replan()` even when the layer hasn't changed. Multiple "Instance stopped"/"New instance spawned" cycles observed per config change.
- **Impact**: brief service disruption on every hook event; with `startup: disabled` there's a window where the service is stopped between replan cycles.
- **Fix**: diff old vs new pebble layer before replanning, or set `startup: enabled` so Pebble handles restarts gracefully.
- **Linter rule**: not mechanically checkable.

### 26. `config-changed` fires twice per `juju config` call on Juju 4.x
- **Severity**: low
- **Kind**: ux
- **Where**: observed behaviour on Juju 4.0.5 (unverified root cause)
- **Evidence**: `juju config log_level=debug` fired 2 `config-changed` hooks, observed consistently across multiple config changes. Possibly a Juju 4.x behaviour or an interaction with `KubernetesComputeResourcesPatch` re-emitting the event (unverified).
- **Impact**: doubles hook workload; the charm re-renders and replans the pebble layer twice per change.
- **Fix**: investigate whether `KubernetesComputeResourcesPatch` re-emits `config-changed`; consider debouncing in `_on_config_changed`.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Clean dataclass-based integration data loading**: `src/integrations.py` uses frozen `@dataclass` types with `classmethod load()` to extract and validate relation data — `HydraEndpointData`, `KratosInfoData`, `TracingData`, `TenantServiceInfoData`, `PublicRouteData` each encapsulate messy relation-data parsing behind a clean interface.
- **Holistic handler pattern**: `src/charm.py:178` — a single `_holistic_handler` reconciles all state on every relevant event. Combined with `PebbleService.render_pebble_layer()`, this makes state reconciliation easy to reason about.
- **Well-structured service abstraction**: `src/services.py` separates `WorkloadService` (version, ports) from `PebbleService` (layer rendering, restart logic). Layer rendering is a pure function of integration data.
- **Terraform module**: `terraform/` has a complete TF module with variables, outputs, `required_providers` — though see finding #19 for the missing `resources` wiring.
- **Comprehensive CI**: 13 GitHub Actions workflows covering lint, unit, integration, CVE scanning, release, promote, publish, terraform validation, and TIOBE scanning.
- **Scenario-based unit tests**: migrated from `Harness` to `ops.testing` (Scenario), well-factored with a `create_state()` factory and per-relation-type fixtures.
- **`secrets.token_hex(16)` for cookie encryption key**: `src/charm.py:172` — correct use of stdlib for cryptographic key generation.
- **Changelog discipline**: `CHANGELOG.md` follows conventional-commits format with clear version-to-version summaries.

## Common-practice notes

- **Follows**: standard charm layout (`src/`, `lib/`, `templates/`, `tests/unit`, `tests/integration`); `charmcraft.yaml` as single metadata source; `lib/charms/<name>/v<N>/` library convention.
- **Follows**: observability integration pattern — `MetricsEndpointProvider`, `GrafanaDashboardProvider`, `LogForwarder`, `TracingEndpointRequirer`.
- **Follows**: resource patching via `KubernetesComputeResourcesPatch` with `adjust_resource_requirements`.
- **Drifts**: manually sets `_relation` on a library object (`src/charm.py:252`) — anti-pattern. Library's stored-state-backed `external_host` property is ignored in favor of raw relation-data reads (`src/integrations.py:112-127`).
- **Drifts**: calls `open_port()` imperatively (`src/services.py:47-48`) rather than declaratively in `charmcraft.yaml` — still common in practice.
- **Drifts**: no `actions.yaml` — sibling identity-platform charms define at least `restart`.
- **Notable**: uses `traefik_route` in `raw=True` mode with a manually maintained JSON template instead of the `ingress` relation, motivated by security — `/api/v0/metrics` should not be public (IAM-1403, commit `52bd694`).
- **Notable**: heavy use of `logger.error()` for conditions that should be `BlockedStatus`/`WaitingStatus` — error logs go to `debug-log` but operators looking at `juju status` get no signal.

## Tests

### Unit tests

- **Framework**: `ops.testing` (Scenario), 21 tests across 7 test classes.
- **Run results**: all 21/21 pass via `tox -e unit` with 88% line coverage. The `conftest.py` autouse fixture `patch_certificate_transfer_integration_file_open` patches both `open` and `subprocess.run`. Outside tox, tests may fail if `update-ca-certificates` is not installed.
- **Coverage gaps** (mapped to findings):
  - `certificate_transfer_integration.py:50-52,74-75` — `CertificateAvailableEvent`/`CertificateRemovedEvent` handlers untested; `_on_certificate_event` path never exercised (finding #7)
  - `charm.py:255` — `_on_public_route_changed` early return when `is_ready()` is `False` untested
  - `charm.py:269-270` — `_on_resource_patch_failed` handler untested (finding #4)
  - `src/integrations.py:117,125` — `_external_host`/`_scheme` `None` paths untested
  - `src/integrations.py:150` — the `not external_host` early return in `PublicRouteData.load()` untested (finding #1)
  - `services.py:59` — `_restart_service` with `restart=True` dead code (finding #21)
  - `utils.py:48-55` — `leader_unit` decorator dead code (finding #22)
- **Assertion quality**: tests assert on pebble layer env vars and unit status but do NOT verify traefik config content, `ui-endpoint-info` data, cookie key propagation, or recovery from error states. The `public_route_relation` fixture has no `remote_app_data`, so tests validate the empty-data bug path as "passing" (finding #9).

### Integration tests

- **Framework**: Jubilant, 6 tests: deploy, health (`/api/v0/status`), ingress (`/ui/login`), scale up, remove/re-add integration, scale down, app removal.
- **Assertions**: `test_app_health` checks `/api/v0/status` returns 200; `test_has_ingress` checks `/ui/login` returns 200 via traefik; the rest check status predicates.
- **Gaps**:
  - no kratos or hydra integration — the charm's core proxying function is never verified (finding #10)
  - no config-change test
  - no upgrade/refresh test
  - `test_remove_integration` only tests `public-route` removal, and likely passes because CI uses Juju 3.x where finding #1 doesn't manifest
  - no observability integration tests (metrics, logging, grafana, tracing)
  - no non-happy-path tests (missing backends, invalid config, kill workload)

## Docs

- **README**: covers deploy, integrations, OCI images, security, contributing. Bug: the "Ingress" section documents the old `ingress` relation instead of `public-route` (stale since v2.0.0, finding #18). Missing: doesn't mention `ui-endpoint-info` provided relation, `tenant-service-info`, or `tracing` relations.
- **CONTRIBUTING.md**: clear dev-environment (`tox devenv`), test-running, build, and deploy instructions.
- **Charmhub page**: links to canonical-identity readthedocs; one-line summary.
- **Terraform docs**: `terraform/MODULE_SPECS.md` describes the module.
- **CHANGELOG.md**: comprehensive, conventional-commits format, clear version summaries.
- **Doc/reality mismatch**: README "Ingress" section; several undocumented integrations.

## Open questions

1. **Is the Juju 4.x vs 3.6 BASE_URL difference a known issue?** Confirmed in three deployments: the re-integration bug manifests on Juju 4.0.5 but not 3.6.25, due to `traefik_route`'s `is_ready()` and event-ordering differences. Open issue #266 ("Consider introducing IngressData class") suggests the team already recognizes this area needs work.
2. **Why does `config-changed` fire twice for a single `juju config` call?** Observed consistently on Juju 4.0.5. May be a Juju 4.x behaviour or an interaction with `KubernetesComputeResourcesPatch` re-emitting the event (unverified).
3. **Is the `normalise_url` hack still needed?** The docstring says it forces https as a workaround. The `traefik_route` interface now has a `scheme` property, read in `_scheme()` (`src/integrations.py:122-125`), but `normalise_url` always overrides to `https` (`src/utils.py:31`) — may be unnecessary now.
4. **Open issue #481**: "Registration won't work if enabled at the same time as user-verification-service" — inter-charm coordination problem where user-verification-service overrides the registration URL.
5. **Open issue #334**: `LoginUIProxyingError` alert firing without recent 5XX — the alert uses `increase(...[2m]) > bool 0`, which triggers on deployment-time errors that persist in the query window.
6. **Terraform module doesn't pass the OCI image resource**: `terraform/main.tf` has `resources` commented out (finding #19). Likely intentional for charmhub-based deploys but should be documented.
7. **Should `KratosInfoRequirer.is_ready()` handle blocked backends?** Currently returns `False` when the kratos app databag is empty (`lib/charms/kratos/v0/kratos_info.py:148`), which happens both when there's no relation and when Kratos is blocked. The login-ui charm treats both cases identically — a `WaitingStatus("Waiting for Kratos to become ready")` would be more informative.
8. **Pebble socket location**: the workload pebble daemon socket is at `/charm/containers/login-ui/pebble.socket`, not the default `/var/lib/pebble/default/.pebble.socket`. Running `pebble services` via `juju exec` without `PEBBLE_SOCKET` points at the system pebble daemon (running only `container-agent`) rather than the workload daemon.
