# oathkeeper-operator

Charmed Ory Oathkeeper (Identity & Access Proxy) for k8s, with library-mediated integrations for auth-proxy, forward-auth (Traefik), Kratos, TLS, and COS observability. The charm deploys cleanly and its integration tests exercise a real end-to-end proxy flow (200/401, header mutation), but it has serious status- and lifecycle-reporting gaps: `juju status` reports `active` even when the workload is dead, and the currently published **stable** revision (rev 39) enters an irrecoverable error state when the TLS relation is removed — a regression not present on edge (rev 99). A hardcoded `http://` URL also breaks the `list-rules`/`get-rule` actions whenever TLS is enabled. A maintainer should first fix the stable TLS-removal crash (it bricks running deployments), then wire up pebble-check/`_on_update_status` health reporting, then fix the CLI scheme hardcoding.

| | |
|---|---|
| Repo | canonical/oathkeeper-operator @ `76c3448` (2026-01-23) |
| Charms | oathkeeper, auth-proxy-requirer (test-only) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (4.0.5) edge rev 99 + concierge-k8s-3 (3.6.25) edge rev 99, then refreshed to stable rev 39 on 3.6; also exercised TLS on both revisions, ingress, kratos-info, metrics/logging/grafana via grafana-agent-k8s, forward-auth, scale up→2→1, downgrade rev 99→39, SIGKILL, pebble stop/start, pebble restart, action breakage with TLS (both controllers), action recovery after TLS removal (4.x), irrecoverable error state on TLS removal (stable rev 39), trust-absent error, force-removal ConfigMap leak, and container-agent SIGTERM on 4.x deploy |
| Reviewed | 2026-08-12 |

## What it does

Oathkeeper authenticates, authorizes, and mutates incoming HTTP requests. The charm runs the Oathkeeper workload via a minimal rock image, manages configuration through two Kubernetes ConfigMaps (oathkeeper YAML config, access rules), patches the StatefulSet to mount them, and exposes integration points for downstream protected charms (auth-proxy), API gateways (forward-auth via Traefik), Kratos (kratos-info), TLS (certificates), COS observability (metrics, logging, grafana, tracing), ingress (Traefik), and admin UI discovery (oathkeeper-info). It provides `list-rules` and `get-rule` actions via the Oathkeeper CLI.

## Deployment log

### Juju 4.x (concierge-k8s-4, model rv-oathkeeper-4-deep)

```shell
juju switch concierge-k8s-4
juju add-model rv-oathkeeper-4-deep
juju deploy oathkeeper --channel edge --trust -m rv-oathkeeper-4-deep
```

- Deployed from charmhub edge, revision 99, on ubuntu@22.04/stable.
- `waiting(allocating)` → `maintenance(installing charm software)` → `blocked(Failed to restart the container)` → `active`, in ~90 seconds.
- The transient `blocked` is documented in issue #63 and confirmed in `juju show-status-log`.
- Memory: 54 MiB pod, under 10 MiB for the oathkeeper container.
- 2 containers in pod: `charm` (`ghcr.io/juju/charm-base:ubuntu-22.04`) and `oathkeeper` (registry.jujucharms.com OCI image, minimal rock with no shell).

Actions:
```shell
juju run oathkeeper/0 list-rules          # returns empty, success
juju run oathkeeper/0 get-rule rule-id="nonexistent"  # "Rule not found", success
juju config oathkeeper dev=true           # accepted, status stayed active
```

### Juju 3.6 (concierge-k8s-3, model rv-oathkeeper-3-deep)

```shell
juju switch concierge-k8s-3
juju add-model rv-oathkeeper-3-deep
juju deploy oathkeeper --channel edge --trust -m rv-oathkeeper-3-deep
```

- Same rev 99, same ubuntu@22.04/stable.
- Became active in ~60 seconds. No transient blocked observed on this controller.

### TLS integration (both environments)

```shell
juju deploy self-signed-certificates --channel edge
juju integrate oathkeeper:certificates self-signed-certificates:certificates
```

- CSR created for `oathkeeper.<model>.svc.cluster.local`.
- Pebble layer updated with `SERVE_API_TLS_CERT_BASE64` and `SERVE_API_TLS_KEY_BASE64` env vars.
- Health check URL changed to `https://oathkeeper.<model>.svc.cluster.local:4456/health/alive`.
- `certificates-relation-changed` fired 3 times (created → changed → joined → changed → changed). Two early events logged "Provider relation data did not pass JSON Schema validation" warnings (normal for initial CSR flow).
- Removing the certificates relation reverted to HTTP correctly (on edge rev 99 — see stable-rev regression below).

### Ingress integration (3.6)

```shell
juju deploy traefik-k8s --channel edge
juju integrate oathkeeper:ingress traefik-k8s
```

- `ingress-relation-created` hook ran. Traefik went to `error` (no LoadBalancer IP in this cluster — expected).
- Despite the traefik error, the ingress relation was established and the charm stayed `active`.

### Kratos integration (4.x)

```shell
juju deploy kratos --channel edge --trust
juju integrate oathkeeper:kratos-info kratos:kratos-info
```

- Kratos deployed to `blocked` (missing pg-database — expected without a full identity bundle).
- `kratos-info` relation established with empty application data (Kratos hasn't published info yet).
- Oathkeeper config rendered with defaults (Jinja2 `| d(...)` filters) — graceful degradation confirmed.
- Oathkeeper stayed `active` throughout; no restart needed since config already used defaults.

### Observability integration (4.x)

```shell
juju deploy grafana-agent-k8s --channel 0.40/edge
juju integrate oathkeeper:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate oathkeeper:logging grafana-agent-k8s:logging-provider
juju integrate oathkeeper:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
```

- All three integrations established successfully. grafana-agent-k8s remained `blocked` (needs grafana-cloud-config/dashboards-provider — expected without a full COS stack).
- oathkeeper correctly exposes `prometheus_scrape`, `loki_push_api`, and `grafana_dashboard` interfaces.

### Downgrade refresh (3.6)

```shell
juju refresh oathkeeper --channel latest/stable  # rev 99 → rev 39
```

- Refreshed edge rev 99 → stable rev 39. Unit IP changed, went through maintenance, recovered to `active` in ~30s. ConfigMaps survived; pebble layer re-applied correctly; no data loss.

### Trust check

```shell
juju deploy oathkeeper --channel edge  # no --trust
```

- Charm goes to `error`: `hook failed: "install"`.
- Root cause: `ApiError` (403 Forbidden) on ConfigMap creation via lightkube. Known issue #39.

## Observed behaviour

### Service kill → status not updated
`pebble stop oathkeeper` → pebble reports `inactive`; `juju status` continued to show `active` for 35+ seconds through an update-status cycle. `_on_update_status` (`src/charm.py:463-465`) only calls `_update_oathkeeper_info_relation_data` and never checks service health. `_oathkeeper_service_is_running` (`src/charm.py:271-278`) exists but is used only for action guards.

### SIGKILL → Pebble auto-restarts, Juju status unchanged
`pebble signal SIGKILL oathkeeper` → Pebble restarted the service within seconds via the `alive` health check. Juju status remained `active` throughout. `oathkeeper-pebble-check-failed` and `oathkeeper-pebble-check-recovered` hooks fired (visible in `juju show-status-log` with timestamps), but `src/charm.py` has zero observers for either event.

### TLS actions broken
With TLS certs present, `list-rules` fails:
```
Action id 1 failed: Something went wrong when trying to run the command: non-zero exit code 1
executing ['oathkeeper', 'rules', 'list', '--endpoint', 'http://localhost:4456', ...]
stderr='response status code does not match any response statuses defined for this endpoint in the swagger spec (status 400)'
```
The `OathkeeperCLI` constructor (`src/charm.py:166-169`) hardcodes `http://localhost:4456` even when the API requires HTTPS. Removing the certificates relation restores action functionality. Confirmed on both 3.6 and 4.x.

### Auth-proxy config change does not restart the workload
`_on_auth_proxy_config_changed` (`src/charm.py:642-679`) patches the access-rules and oathkeeper-config ConfigMaps but never calls `_restart_service()`, unlike `_handle_status_update_config` (used by pebble-ready, kratos-relation-changed, oathkeeper-info-ready) which does. Access rule changes from `juju integrate` take effect only after the next unrelated restart or kubelet ConfigMap mount propagation (~60-90s).

### Scale-up: non-leader unit patches the StatefulSet
Scaling 1→2: unit 1 (`oathkeeper/1`), confirmed non-leader (`oathkeeper leadership for oathkeeper/1 denied` in debug-log), still issues `PATCH /statefulsets/oathkeeper` from `_on_oathkeeper_pebble_ready` → `_patch_statefulset()`. Unit 0 also patches during its own pebble-ready. Both succeed (200 OK) because lightkube's field-manager pattern makes identical patches idempotent, but this is semantically wrong. Confirmed on both controllers.

### Transient BlockedStatus on initial deploy (4.x only)
`_restart_service` (`src/charm.py:549-561`) emits `BlockedStatus("Failed to restart the container, please consult the logs")` when `container.restart()` raises `ChangeError`. This fires momentarily and is immediately overwritten by `ActiveStatus` from `_handle_status_update_config`. Visible in `show-status-log`, no hook error recorded.

### Two config-changed hooks for one config change
Changing `dev=true` fired config-changed twice. Likely an ops/Juju interaction rather than a charm bug, but `forward_auth.update_forward_auth_config` runs twice redundantly as a result.

### Juju version differences
- **3.6**: deploy ~60s, no transient blocked status, container agent stable.
- **4.x**: deploy ~90s, transient `blocked(Failed to restart the container)` → `active` blink. Container agent may SIGTERM mid-hook during initial pebble-ready, causing a ~30s recovery delay. Both versions reach active and operate identically thereafter.
- **Downgrade**: rev 99→39 on 3.6 succeeded; ConfigMaps and pebble layer survived; ~30s maintenance window.

### Stable rev 39: removing TLS relation causes an irrecoverable error state
After refreshing to stable rev 39 on Juju 3.6, `juju remove-relation oathkeeper self-signed-certificates` puts the charm into `error`: `hook failed: "certificates-relation-broken"`, repeating every ~11s:
```
RuntimeError: Relation certificates does not exist - The certificate request can't be completed
```
`juju resolved` does not fix it. The charm never recovers without `juju remove-application --force`. On edge rev 99 (Juju 4.x and 3.6), the same operation completes cleanly, reverting to HTTP and staying `active`. This is a regression between the stable and edge releases. The error originates in `lib/charms/tls_certificates_interface/v2/tls_certificates.py` (via `CertHandler`) — the relation-broken handler tries to access relation data on a relation that no longer exists.

### Force-removal on stable leaves ConfigMaps behind
From the irrecoverable error state above, `juju remove-application --force` skips the remove hook. Both `oathkeeper-config` and `access-rules` ConfigMaps were left in the namespace. A normal (non-error) removal on edge rev 99 ran the remove hook and cleaned both up correctly.

### Pebble restart → service recovers, status unchanged
`pebble restart oathkeeper` restarted the service in ~2s; Juju status remained `active`. The pebble-check-failed/recovered hooks fired with no handlers registered.

### Minimal workload container
The Oathkeeper rock image has no shell, `cat`, `ls`, or `sh` — only the `oathkeeper` binary and Pebble. `kubectl exec` into the workload can only run `pebble` and `oathkeeper` commands, limiting debugging. The charm container (ubuntu-based) has a full shell.

### TLS: dual certificate delivery mechanism
1. **Environment variables**: `SERVE_API_TLS_CERT_BASE64` / `SERVE_API_TLS_KEY_BASE64` in the pebble layer (`src/charm.py:230-237`) — clean, works correctly.
2. **Local filesystem + CA bundle**: `update_cert_configuration` (`src/charm.py:529-546`) writes cert/key/CA to `/usr/local/share/ca-certificates/` on the charm container's filesystem, runs `update-ca-certificates --fresh`, then pushes `/etc/ssl/certs/ca-certificates.crt` to the workload container. `--fresh` rebuilds the entire CA trust store, which could race with other processes on the charm container.

## Findings

### Stable rev 39: removing the TLS relation causes an irrecoverable error state
- **Severity**: high (critical on stable)
- **Kind**: bug
- **Where**: `lib/charms/tls_certificates_interface/v2/tls_certificates.py` (via `CertHandler`), triggered from `src/charm.py:518-526` (`_on_cert_changed`)
- **Evidence**: On Juju 3.6 with stable rev 39, `juju remove-relation oathkeeper self-signed-certificates` causes `hook failed: "certificates-relation-broken"` with `RuntimeError: Relation certificates does not exist - The certificate request can't be completed`, repeating every ~11s. `juju resolved` does not clear it; the charm is permanently stuck in `error`. On edge rev 99 the same operation completes cleanly.
- **Impact**: On the published stable channel, deploying TLS and later removing it bricks the charm; operators must force-remove and redeploy. Shipping regression versus edge.
- **Fix**: Backport the edge fix (likely in `cert_handler.py` / `tls_certificates_interface`) to stable and publish a new stable revision.
- **Linter rule**: not mechanically checkable — integration-level library interaction bug.

### Unit status stays Active when the workload is dead
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:463-465` (`_on_update_status`); no pebble-check handlers anywhere in `src/charm.py`
- **Evidence**: `pebble stop oathkeeper` → pebble `inactive`, `juju status` still `active` after 30+ seconds through an update-status cycle. SIGKILL to the workload triggers `oathkeeper-pebble-check-failed`/`recovered` hooks (seen in `juju show-status-log`), but the charm registers zero observers for either event. `_on_update_status` only calls `_update_oathkeeper_info_relation_data`.
- **Impact**: An operator cannot tell from `juju status` whether the workload is running. Pebble's `alive` check auto-restarts the process, but there's a window with no Juju-level signal of failure.
- **Fix**: (1) In `_on_update_status`, check `_oathkeeper_service_is_running` and set `BlockedStatus` if down. (2) Add observers for `pebble-check-failed`/`pebble-check-recovered`.
- **Linter rule**: flag `_on_update_status` handlers with no workload health check; flag missing pebble-check handlers when pebble health checks are defined — mechanically checkable.

### OathkeeperCLI hardcoded to `http://`, breaks actions under TLS
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:166-169`
- **Evidence**: `self._oathkeeper_cli = OathkeeperCLI(f"http://localhost:{OATHKEEPER_API_PORT}", self._container)`. With TLS active, the API serves HTTPS only; `juju run oathkeeper/0 list-rules` fails with `status 400`. Removing the certificates relation restores action success. Confirmed on both 3.6 and 4.x.
- **Impact**: With TLS in production, `list-rules`/`get-rule` are unusable, despite the charm otherwise handling TLS correctly (pebble env vars, health check URL).
- **Fix**: Build the CLI URL from `self._scheme`, e.g. `f"{self._scheme}://localhost:{OATHKEEPER_API_PORT}"`, or detect TLS readiness in the constructor.
- **Linter rule**: flag string literals containing `http://` in k8s charm constructors that also reference TLS configuration — partially checkable.

### URL regex replacement corrupts URLs containing "https" in path
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:711` (notes: `src/charm.py:717`; kept as reported, unverified line)
- **Evidence**: `url = url.replace("https", "<^(https|http)>")` uses `str.replace` on the full URL string, not just the scheme. `https://example.com/use-https-endpoint` becomes `<^(https|http)>://example.com/use-<^(https|http)>-endpoint`.
- **Impact**: Protected URLs with a literal "https" substring in path/query/host produce corrupted regex patterns that won't match, silently breaking access control for those endpoints.
- **Fix**: Replace only the scheme, e.g. `re.sub(r'^https', '<^(https|http)>', url)`.
- **Linter rule**: flag `str.replace` calls on URL strings where the needle is a scheme name — mechanically checkable.

### Deploy without `--trust` causes a traceback, not BlockedStatus
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:453` (`_on_install`)
- **Evidence**: `juju deploy oathkeeper --channel edge` (no `--trust`) → `hook failed: "install"` with `ApiError: 403 Forbidden` on `config_map.create_all()` via lightkube. No try/except around the call. Open issue #39.
- **Impact**: Charm goes to `error` with a generic hook failure; operator must dig through logs to find the 403.
- **Fix**: Wrap `config_map.create_all()` in try/except `ApiError`, check for 403, set `BlockedStatus("Missing trust; deploy with --trust")`.
- **Linter rule**: flag lightkube calls in `_on_install` without a try/except that sets `BlockedStatus` — mechanically checkable.

### Missing pebble-check-failed / pebble-check-recovered handlers
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` — no observers for pebble check events
- **Evidence**: `juju show-status-log` shows `oathkeeper-pebble-check-failed`/`-recovered` firing (timestamps 20:17:28 / 20:17:58); `grep -n "pebble-check\|check_failed\|check_recovered" src/charm.py` returns zero matches. The `alive` check is defined in `_oathkeeper_layer` (`src/charm.py:266-269`) but its events are never observed.
- **Impact**: When the workload dies and Pebble restarts it, Juju status never reflects the transient failure — compounds the update-status gap above.
- **Fix**: Add observers for pebble-check-failed (set `MaintenanceStatus`/`WaitingStatus`) and pebble-check-recovered (restore `ActiveStatus`).
- **Linter rule**: flag pebble health checks without corresponding pebble-check event observers — mechanically checkable.

### `_patch_statefulset` not guarded by leadership
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:418-451` (`_patch_statefulset`), called from `src/charm.py:459` (`_on_oathkeeper_pebble_ready`)
- **Evidence**: Fires on every unit's pebble-ready with no `if not self.unit.is_leader()` guard. Confirmed at runtime on both controllers: non-leader `oathkeeper/1` issued `PATCH /statefulsets/oathkeeper` during scale-up. Compare `_on_install` (`src/charm.py:453`), which does guard on leadership.
- **Impact**: In a scaled deployment, every unit independently patches the StatefulSet — unnecessary k8s API load and potential races if patches ever diverge.
- **Fix**: Guard with `if not self.unit.is_leader(): return`.
- **Linter rule**: flag `client.patch(StatefulSet, ...)` calls without a preceding leadership check — mechanically checkable.

### Unit tests cannot be collected in CI: `httpx` missing from `unit-requirements.txt`
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_config_map.py:7`; `unit-requirements.txt`
- **Evidence**: `test_config_map.py` imports `from httpx import Response` to build mock `ApiError` objects. `httpx` is listed only in `integration-requirements.txt`. `tox -e unit --recreate` (clean env) fails at collection with `ModuleNotFoundError: No module named 'httpx'`. A prior successful run only worked because a stale `.tox/unit` cache had httpx pre-installed. With httpx installed manually, all 81 tests pass (81/81, 79% coverage).
- **Impact**: `config_map` tests are dead code in CI (CI uses `tox -e unit`); `ConfigMapManager`, `create_all`, `delete_all`, and all ConfigMap CRUD have zero effective coverage in CI.
- **Fix**: Add `httpx` to `unit-requirements.txt`, or refactor tests to use `unittest.mock.MagicMock` for ApiError construction.
- **Linter rule**: check that all imports under `tests/unit/` are satisfied by `unit-requirements.txt` — mechanically checkable.

### `update_cert_configuration` writes to local filesystem in a k8s charm
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:529-546`
- **Evidence**: Calls `os.makedirs()`, three `open(..., "w+")` calls, and `subprocess.run(["update-ca-certificates", "--fresh"])` on the charm container's local filesystem; `--fresh` rebuilds the entire CA trust store. Carries `TODO @shipperizer we need to refactor this into separate steps so it's more reusable` at line 525.
- **Impact**: Local writes don't persist across pod restarts and couple the charm to `update-ca-certificates` in the charm image; the workload already gets TLS material via env vars, so this path only exists for the CA bundle.
- **Fix**: Push the CA cert directly to the workload container via `container.push()`, dropping the local-file + `update-ca-certificates` step.
- **Linter rule**: flag `os.makedirs`/`open()`/`subprocess.run` in k8s charms writing to non-tmp paths — partially checkable.

### Auth-proxy config change does not restart the workload
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:642-679` (`_on_auth_proxy_config_changed`)
- **Evidence**: Calls `_update_config()` and `forward_auth.update_forward_auth_config()` but never `_restart_service()`, unlike `_handle_status_update_config` (`src/charm.py:563-576`), which calls both. ConfigMap mounts may take 60-90s for kubelet propagation.
- **Impact**: Access rule changes from `juju integrate` may not take effect until the next unrelated restart or ConfigMap propagation completes — unpredictable latency between integration and enforcement.
- **Fix**: Add `_restart_service()` after `_update_config()`.
- **Linter rule**: not mechanically checkable.

### `_remove_auth_proxy_configuration` does not restart the workload
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:752-776`
- **Evidence**: Same pattern as above — calls `_update_config()` but never `_restart_service()` when an auth-proxy relation is removed.
- **Impact**: Removed access rules may remain active for 60-90s, leaving a removed protected charm temporarily accessible.
- **Fix**: Add `_restart_service()` after `_update_config()`.
- **Linter rule**: not mechanically checkable.

### `forward_auth.py`: `_compare_apps` uses string `in` on JSON-encoded data
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/oathkeeper/v0/forward_auth.py:529-556` (notes: `:391-399`; both cited, unverified exact lines)
- **Evidence**: `_compare_apps` reads `requirer_data = relation.data[relation.app]` (raw string dict); `ingress_apps = requirer_data["ingress_app_names"]` is a JSON string like `'["traefik-k8s"]'`, not a parsed list, because the requirer JSON-encodes lists via `_dump_data`. The comparison `app not in ingress_apps` uses Python string `in` (substring match), so `"app" in '["app-other"]'` would incorrectly return True.
- **Impact**: Apps could be incorrectly accepted or rejected for IAP protection when names overlap with JSON syntax or other app names. Unlikely to trigger given typical Juju app naming, but semantically wrong.
- **Fix**: Parse `ingress_apps` with `json.loads()` before comparison, or use `_load_data(requirer_data, FORWARD_AUTH_REQUIRER_JSON_SCHEMA)`.
- **Linter rule**: flag bare `in` comparisons on relation-data fields known to be JSON-encoded — partially checkable with type analysis.

### Unsafe `json.loads` on peer relation data
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:400-401`
- **Evidence**: `_get_peer_data` does `return json.loads(data) if data else {}` with no try/except.
- **Impact**: A single corrupted peer-data entry would raise `json.JSONDecodeError` and crash every hook that reads peer data.
- **Fix**: Wrap in try/except `json.JSONDecodeError`, log, return `{}`.
- **Linter rule**: flag bare `json.loads()` calls on relation data without try/except — mechanically checkable.

### `_on_config_changed` does not reconcile the workload
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:465-467` (`_on_config_changed`)
- **Evidence**: Only calls `forward_auth.update_forward_auth_config(self._forward_auth_config)`; never calls `_update_config()` or `_restart_service()`. Toggling `dev` updates forward-auth relation data (via `_scheme`) but never reconfigures the workload.
- **Impact**: The `dev` config option has incomplete runtime effect — the workload keeps running with the pre-change configuration indefinitely.
- **Fix**: `_on_config_changed` should call `_handle_status_update_config(event)`.
- **Linter rule**: not mechanically checkable.

### `_on_forward_auth_relation_removed` unconditionally sets ActiveStatus
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:626-627`
- **Evidence**: `self.unit.status = ActiveStatus()` overwrites any previously set status, including `BlockedStatus` set by `_on_invalid_forward_auth_config` (`src/charm.py:613-614`).
- **Impact**: Fixing a forward-auth misconfiguration by removing the relation can silently flip a `BlockedStatus` to `ActiveStatus` even if the underlying problem (e.g. unhealthy workload) persists.
- **Fix**: Only set `ActiveStatus` if not already active, or delegate to `_handle_status_update_config`.
- **Linter rule**: flag unconditional `self.unit.status = ActiveStatus()` in relation-broken/unset handlers — mechanically checkable.

### `ConfigMap.delete()` raises `ValueError` on ApiError, crashes remove hook
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/config_map.py:136-141`
- **Evidence**: `delete()` catches `ApiError` and unconditionally `raise ValueError`. `_on_remove` (`src/charm.py:472-476`) calls `config_map.delete_all()` → `cm.delete()` with no try/except.
- **Impact**: If a ConfigMap was already deleted, the remove hook crashes with a traceback; the re-raised `ValueError` also loses the original `ApiError` context.
- **Fix**: Return instead of raising, or catch `ValueError` in `_on_remove` and log a warning.
- **Linter rule**: flag `raise` from within an `except` block that replaces the exception type — mechanically checkable.

### Juju 4.x container agent SIGTERM during pebble-ready
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:458-462` (`_on_oathkeeper_pebble_ready`)
- **Evidence**: On a fresh 4.x deploy, the container agent received SIGTERM mid-hook (`juju.worker.caasunitterminationworker terminating due to SIGTERM`), interrupting `_on_oathkeeper_pebble_ready`. Juju re-ran the hook on next agent start; ~30s delay and a `pebble poll failed` log entry.
- **Impact**: Cosmetic/log-noise on 4.x initial deploy; the charm recovers because `_handle_status_update_config` is idempotent.
- **Fix**: No charm-level fix required; document the transient log messages for operators.
- **Linter rule**: not mechanically checkable.

### `_on_auth_proxy_config_changed` catches only `ops.pebble.Error`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:670-675`
- **Evidence**: `try: self._update_config() except Error as e: ...` where `Error` is `ops.pebble.Error`. The body also calls `_render_conf_file()` (Jinja2), `oathkeeper_configmap.update()` (lightkube), and conditionally `update_cert_configuration()` (filesystem/subprocess), none of which raise `ops.pebble.Error`.
- **Impact**: A lightkube `ApiError` or template error tracebacks instead of transitioning to `BlockedStatus`.
- **Fix**: Catch the exception types the call chain can actually raise (or a broader `Exception`).
- **Linter rule**: flag try/except blocks where the caught type doesn't match the call chain — partially checkable with type analysis.

### Retry logic masks persistent failures
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:346-357` (`_update_config`), `src/charm.py:634-638` (`_patch_access_rules`)
- **Evidence**: Both use `@retry(wait=wait_exponential(multiplier=3, min=1, max=10), stop=stop_after_attempt(5), reraise=True)`, adding ~121s of delay (1+3+9+27+81) before a persistent error (e.g. RBAC denial) surfaces.
- **Impact**: No distinction between transient and permanent errors; an operator with an RBAC misconfiguration waits ~2 minutes for a traceback.
- **Fix**: Only retry on transient error types (e.g. `ApiError` with 429/503); fail fast otherwise.
- **Linter rule**: not mechanically checkable.

### Misleading `_scheme`: `dev` flag silently disables TLS for URL generation
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:283-285`
- **Evidence**: `scheme = "https" if self._is_tls_ready() and not self.config["dev"] else "http"`. With `dev=True`, TLS is suppressed for scheme calculation even when certificates are present.
- **Impact**: An operator who set `dev=True` during setup and later added certificates won't see TLS reflected in decisions/public URLs, while the workload itself still gets TLS env vars — a mismatch.
- **Fix**: Warn when TLS and `dev` are both active, or narrow the scope of `dev`.
- **Linter rule**: not mechanically checkable.

### Test suite uses deprecated `Harness`
- **Severity**: nit
- **Kind**: lint
- **Where**: `tests/unit/test_config_map.py` and all other unit test files
- **Evidence**: All 81 unit tests use `ops.testing.Harness`; 156 deprecation warnings emitted, including `PendingDeprecationWarning: Harness is deprecated` per file.
- **Impact**: `Harness` will be removed from `ops`.
- **Fix**: Migrate to `ops.testing.Scenario`.
- **Linter rule**: flag imports of `ops.testing.Harness` — mechanically checkable.

### ruff: property docstrings start with a verb
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:223`, `src/charm.py:383`
- **Evidence**: `ruff check` reports 2 `property-docstring-starts-with-verb` errors.
- **Impact**: minor lint noise.
- **Fix**: Rephrase as "A pre-configured Pebble layer" / "The peer relation".
- **Linter rule**: mechanically checkable (ruff already does).

### Third-party charm libraries use deprecated APIs
- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/tls_certificates_interface/v2/tls_certificates.py:1512`, `lib/charms/loki_k8s/v1/loki_push_api.py:2436`, `lib/charms/traefik_k8s/v2/ingress.py:255-286`, `lib/charms/tempo_k8s/v2/tracing.py:267`
- **Evidence**: `JujuVersion.from_environ()` deprecation warnings (41 occurrences each), Pydantic V1 `@validator`/`__fields__`/`.dict()` usage — 156 warnings total in test output.
- **Impact**: third-party code, but adds noise and future breakage risk.
- **Fix**: Refresh via `charmcraft fetch-lib` to versions using `self.model.juju_version` and Pydantic V2 APIs.
- **Linter rule**: not mechanically checkable (upstream libs).

## Worth copying

- **Library interfaces**: `auth_proxy.py`, `forward_auth.py`, `oathkeeper_info.py` under `lib/charms/oathkeeper/v0/` cleanly separate provider/requirer classes with JSON schema validation and typed events (`AuthProxyConfigChangedEvent`, `ForwardAuthProxySet`, etc.) instead of raw relation-data parsing in the charm.
- **ConfigMap abstraction**: `config_map.py`'s `ConfigMapBase` with CRUD and a `ConfigMapManager` registry (`register()`, `create_all`/`delete_all`) is a clean pattern for charms managing multiple k8s resources.
- **Graceful degradation**: `_get_kratos_info` (`src/charm.py:379-385`) catches `KratosInfoRelationDataMissingError` and returns `{}` with an info log; the Jinja2 template uses `| d(...)` defaults.
- **Pebble health check with auto-restart**: the `alive` check in `_oathkeeper_layer` (`src/charm.py:266-269`) lets Pebble restart the workload on failure — confirmed via SIGKILL test.
- **Clean action error handling**: actions check `_oathkeeper_service_is_running` before running CLI commands and use `event.fail()` with specific messages; `get-rule` distinguishes "rule not found" from other errors.
- **TLS via environment variables**: `SERVE_API_TLS_CERT_BASE64`/`SERVE_API_TLS_KEY_BASE64` in the pebble layer avoids config-file latency for TLS changes.

## Common-practice notes

- **charmcraft.yaml**: v2 format with `assumes: [juju >= 3.0.2, k8s-api]`, typed config, containers, resources — follows current ecosystem guidance.
- **Library versioning**: own libraries under `lib/charms/oathkeeper/v0/` follow `LIBAPI`/`LIBPATCH`; third-party libraries vary, some stale (e.g. `tls_certificates_interface/v2` uses deprecated `JujuVersion.from_environ()`).
- **No terraform module**: `paths-ignore: ["terraform/**"]` in CI is a no-op — no `terraform/` directory exists.
- **No `docs/` directory**: only `README.md`/`CONTRIBUTING.md` — no architecture doc, troubleshooting guide, or config reference.
- **README doc drift**: README says `juju integrate oathkeeper kratos`, but the endpoint in `charmcraft.yaml` is `kratos-info` (interface `kratos_info`); may need `juju integrate oathkeeper:kratos-info kratos:<endpoint>` depending on the Kratos charm's metadata.

## Tests

### Unit tests (broken in CI; 81 pass with fix)
- **Framework**: `ops.testing.Harness` (deprecated), pytest, pytest-mock, coverage.
- **With httpx fix**: 81 passed, 0 failed, 156 warnings, 79% coverage.
- **Without the fix (i.e. as CI runs it)**: `tox -e unit --recreate` fails at collection with `ModuleNotFoundError: No module named 'httpx'`. A stale `.tox/unit` cache masked this during earlier testing.
- **Coverage gaps**: `src/oathkeeper_cli.py` 55% (`list_rules`/`get_rule` barely tested); `lib/charms/oathkeeper/v0/oathkeeper_info.py` 58%; `lib/charms/oathkeeper/v0/forward_auth.py` 72%; `src/charm.py` 82% with `update_cert_configuration` (530-544), `_restart_service` except block (557-562), `_on_install` (453-457), `_on_invalid_forward_auth_config` (612-614), `_on_forward_auth_proxy_set` (620-623), `_on_forward_auth_relation_removed` (626-627), `_on_auth_proxy_config_changed` except block (675-679), and `_remove_auth_proxy_configuration` (756, 765-766, 776) all at 0%; `src/config_map.py` 93%, with `create()` ApiError handling (93-94, 99-100) and `delete()`'s ValueError raise (136, 141) uncovered.
- **Deprecation warnings**: `Harness` (every test), `JujuVersion.from_environ()` (82 instances), Pydantic V1 APIs (ingress, tracing libs).

### Integration tests
- **Framework**: pytest-operator, lightkube.
- **Covered**: deploy oathkeeper + traefik + auth-proxy-requirer → relate auth-proxy → set up forward-auth → HTTP requests to allowed (200) and denied (401) paths → header mutation → scale up/down → remove relations → `list-rules` → TLS certificates. Tests assert on real HTTP response codes and headers.
- **Gaps**: no `get-rule` action test, no kratos-info integration test, no tracing/tempo test, no grafana dashboard test, no chaos/failure testing (kill pod, corrupt config, fill disk, deploy without `--trust`).

### Linting
- `ruff check`: 2 errors (property docstring verb tense).
- `codespell`: clean.
- Pre-commit: ruff, isort, mypy, codespell, markdownlint, conventional-pre-commit.

## Docs

- **README.md**: usage, integrations, actions, OCI images, security, contributing — adequate for developers.
- **CONTRIBUTING.md**: standard tox/devenv instructions, thin but functional.
- **No `docs/` directory**: no architecture doc, troubleshooting guide, or configuration reference.
- **Charmhub description**: single line ("Charmed Ory Oathkeeper").
- **Doc/reality mismatch**: README's `juju integrate oathkeeper kratos` may not work without an explicit endpoint depending on the Kratos charm's metadata.

## Open questions

1. **Does the Oathkeeper workload hot-reload access rules from ConfigMap mounts?** The auth-proxy handlers patch ConfigMaps without restarting the service. If the workload hot-reloads, the missing restarts are correct; if not, access rules go stale until the next restart. Not settled — the test environment lacked external IPs for a full LoadBalancer/Traefik ingress test.
2. **Are there multi-unit correctness issues beyond the StatefulSet patch?** `_set_peer_data`/`_get_peer_data` use app-scoped peer data (`self._peers.data[self.app][key]`). Leadership guards cover most writes, but concurrent reads/writes during leadership transitions weren't stress-tested.
3. **Why does `update_cert_configuration` exist at all?** TLS cert/key already arrive via env vars; the filesystem path appears to only carry the CA bundle. If the CA cert could also be delivered as an env var, the whole method could be removed — the TODO at line 525 supports this.
4. **What exact change between stable rev 39 and edge rev 99 fixes the TLS-removal crash?** Likely in `cert_handler.py` or `tls_certificates_interface/v2`. Until a new stable revision is published, operators should stay on edge or avoid TLS on stable.
5. **Is the transient BlockedStatus on Juju 4.x deploy harmful?** Documented in issue #63; appears to be a cosmetic race between `_restart_service` and workload container readiness on first deploy, immediately self-corrected.
