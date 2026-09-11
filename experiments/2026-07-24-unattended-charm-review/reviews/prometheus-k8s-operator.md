# prometheus-k8s-operator

A mature, actively maintained k8s charm for Prometheus 3.11 that anchors the COS Lite observability ecosystem. Day-to-day operation is solid — deploy, scale, config changes, and most relation lifecycles work cleanly, and the hash-based change-detection scheme that avoids unnecessary workload restarts is exemplary. But TLS lifecycle handling is broken: removing the `certificates` relation leaves the workload one restart away from a permanent crash-loop while the charm keeps reporting `active`, and ingress through Traefik simply does not work once TLS is enabled. A maintainer should fix the missing `certificates-relation-broken`/`-departed` observers first (Finding 1), then wire the CA cert through to Traefik for ingress (Finding 2). Everything else is secondary.

| | |
|---|---|
| Repo | canonical/prometheus-k8s-operator @ `ecdb918` (2026-07-13) |
| Charms | prometheus-k8s, prometheus-tester |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), prometheus-k8s rev 311 from 3.11/edge; also concierge-k8s-4 (Juju 4.0.5), prometheus-k8s rev 301 from 2/stable |
| Reviewed | 2026-07-27 |

## What it does

The prometheus-k8s charm deploys Prometheus 3.11 on Kubernetes via a single workload container (`ubuntu/prometheus` on ubuntu@26.04). It manages the workload exclusively through Pebble, with config-only changes triggering hot-reload and command-line changes (e.g. TLS toggle) triggering a full restart. The charm participates in 15+ relation endpoints:

- **Provides**: self-metrics-endpoint, grafana-source, grafana-dashboard, receive-remote-write, send-datasource, prometheus-api
- **Requires**: metrics-endpoint, alertmanager, ingress, catalogue, certificates, charm-tracing, workload-tracing, receive-ca-cert, logging

Key features: alert rule forwarding from scrape targets and remote-write providers, automatic TLS via `self-signed-certificates`, ingress per unit via Traefik, Grafana datasource and dashboard provisioning, workload tracing via Tempo, log forwarding to Loki, cross-charm Prometheus API exposure, and Kubernetes resource-limit patching.

## Deployment log

```
=== Session 1: rv-prom-deep on concierge-k8s-3 (Juju 3.6.25) ===

juju switch concierge-k8s-3
juju add-model rv-prom-deep

# Primary deployment
juju deploy prometheus-k8s --channel=3.11/edge --trust
# Rev 311; ~2 min to active/idle, version 3.11.3, 71Mi RSS

# Partner deploys
juju deploy alertmanager-k8s --channel=1/stable --trust
juju deploy self-signed-certificates --channel=1/stable
juju deploy traefik-k8s --channel=latest/stable --trust
# traefik-k8s 1/stable does not support ubuntu@26.04; latest/stable (rev 377) works

# Relations
juju relate prometheus-k8s:alertmanager alertmanager-k8s:alerting
juju relate prometheus-k8s:certificates self-signed-certificates:certificates

# Scale
juju scale-application prometheus-k8s 2 → both active/idle
juju scale-application prometheus-k8s 1 → clean teardown

# Config changes
juju config prometheus-k8s log_level=warn → hot-reload (no restart)
juju config prometheus-k8s log_level=invalid → BlockedStatus "Invalid loglevel"
juju config prometheus-k8s metrics_retention_time=invalid → BlockedStatus "Invalid time spec"
juju config prometheus-k8s maximum_retention_size=not_ok → BlockedStatus "Must be a number followed by '%'..."

# Actions
juju run prometheus-k8s/0 validate-configuration → SUCCESS (valid=True)

# Kill workload
kubectl exec ... -- pkill -9 prometheus → Pebble auto-restart within seconds

# TLS removal (bug observed — Finding 1)
juju remove-relation prometheus-k8s:certificates self-signed-certificates:certificates
# Cert files removed within 5s, but web-config and pebble layer NOT updated.
# Prometheus stayed running but HTTPS was broken.
# Subsequent `juju config` change triggered _configure() and full recovery.

# Ingress test
curl "http://10.43.45.0/rv-prom-deep-prometheus-k8s-0/-/healthy" → 500


=== Session 3B: rv-deep3 deeper testing on concierge-k8s-3 (Juju 3.6.25) ===

# Model already existed with prometheus-k8s, alertmanager, self-signed-cert,
# traefik, grafana, loki, catalogue-k8s, grafana-agent-k8s
# prometheus-k8s rev 311, scale=1, already active with TLS + ingress + other relations

# Added alertmanager and certificates relations
# Both settled to active within ~30s
# TLS active on unit 0: web config, certs, HTTPS 200, HTTP 400
# Ingress returns 500 (Finding 2, third reproduction)

# validate-configuration action on both unit 0 and unit 1 → SUCCESS on both
# Both show promtool "SUCCESS" output and valid=True

# Scale up to 2 units: both active/idle, TLS configured on both
# Unit 1 self-scrape also https, certs in place

# TLS removal (third reproduction of Finding 1):
# 1. Cert files deleted by __init__ → _update_cert() in certificates-relation-broken hook
# 2. Web config file (/etc/prometheus/prometheus-web-config.yml) still present with TLS config
# 3. Pebble plan still has --web.config.file=...
# 4. Charm status: active
# 5. HTTPS to pod: 000 (TLS broken — cert files gone, server rejects)
# 6. HTTP to pod: 400 (rejects plain HTTP — web config requires TLS)
# 7. Killed workload (pkill -9 prometheus)
# 8. Prometheus entered permanent backoff state:
#    Pebble logs: "Unable to validate web configuration file"
#    err="failed to read cert_file (/etc/prometheus/server.cert): no such file or directory"
# 9. Charm status: active (WRONG — workload is crash-looping)
# 10. Two more Pebble restart attempts confirmed same crash
# 11. Recovery: juju config log_level=warn → _configure() →
#     web config file removed, Pebble layer updated (no more --web.config.file),
#     Prometheus back to active/running
# 12. Confirmed: ingress without TLS works again (HTTP 200)

# Re-added TLS → both units (now scale=1) configured correctly, HTTPS 200
# Removed alertmanager relation → clean config update (alerting section removed)
# Removed grafana-source relation → handled cleanly
# Removed TLS again (fourth reproduction of Finding 1) → same stale state
# Killed workload → same crash-loop, same charm active status
# Recovered via config change

# Surviving at end: catalogue, ingress relations. All active.


=== Session 2: rv-deep2 on concierge-k8s-3 (Juju 3.6.25) ===

# Full partner deployment
juju deploy prometheus-k8s --channel=3.11/edge --trust
juju deploy alertmanager-k8s --channel=1/stable --trust
juju deploy self-signed-certificates --channel=1/stable
juju deploy traefik-k8s --channel=latest/stable --trust
juju deploy grafana-k8s --channel=2/edge --trust
juju deploy loki-k8s --channel=dev/edge --trust
juju deploy catalogue-k8s --channel=dev/edge --trust
juju deploy grafana-agent-k8s --channel=dev/edge --trust

# Multi-relation test
juju relate prometheus-k8s:alertmanager alertmanager-k8s:alerting
juju relate prometheus-k8s:certificates self-signed-certificates:certificates
juju relate prometheus-k8s:catalogue catalogue-k8s:catalogue
juju relate prometheus-k8s:grafana-source grafana-k8s:grafana-source
juju relate prometheus-k8s:grafana-dashboard grafana-k8s:grafana-dashboard
juju relate prometheus-k8s:logging loki-k8s:logging
# traefik-k8s auto-related via ingress_per_unit

# All relations settled to active within ~2 min

# Bad config values
juju config prometheus-k8s maximum_retention_size=99999GB → BlockedStatus "Invalid retention size: ..."
juju config prometheus-k8s metrics_retention_time="" → BlockedStatus "Invalid time spec : " (empty value)
juju config prometheus-k8s log_level="" → BlockedStatus "Invalid loglevel:  given, ..." (empty value)

# Scale up
juju scale-application prometheus-k8s 2 → both active; unit 1 took ~5 min to fully configure

# TLS removal (confirmed Finding 1, second reproduction)
juju remove-relation prometheus-k8s:certificates self-signed-certificates:certificates
# certificates-relation-departed fired at +55s, certificates-relation-broken at +105s
# Hook queue backlog: grafana-dashboard-relation-joined, ingress-relation-joined,
#   catalogue-relation-changed, logging-relation-joined all ran before certificates hooks
# After broken: cert files deleted, web-config and pebble layer still stale, status: active
# Recovery: juju config prometheus-k8s log_level=info → _configure() → full recovery

# Ingress + TLS (confirmed Finding 2, second reproduction)
# Traefik config: service URL = https://prometheus-k8s-0...svc.cluster.local:9090
# serversTransport: {} (no CA certs, no insecureSkipVerify)
# curl → 500: "tls: failed to verify certificate: x509: certificate signed by unknown authority"

# Kill workload during TLS
kubectl exec ... -- pkill -9 prometheus → Pebble auto-restart in ~5s, charm stayed active


=== Session 3: rv-prom-j4 on concierge-k8s-4 (Juju 4.0.5) ===

juju switch concierge-k8s-4
# Model already existed from earlier session

# Deployed prometheus-k8s rev 301 from 2/stable (3.11/edge blocked: ubuntu@26.04 not supported)
# Prometheus 2.55.1, 82Mi RSS

# Partners
juju deploy self-signed-certificates --channel=1/stable
juju deploy alertmanager-k8s --channel=1/stable --trust

# Relations
juju relate prometheus-k8s:certificates self-signed-certificates:certificates
juju relate prometheus-k8s:alertmanager alertmanager-k8s:alerting

# TLS works correctly, certs in place, web-config properly configured
# TLS removal (confirmed Finding 1 on Juju 4):
#   Cert files deleted, web-config and pebble layer not updated, status: active

# juju status fails on Juju 4.0.5 with client 4.0.12:
#   "patterns are not implemented" → use --format yaml workaround
```

## Observed behaviour

- **Startup time**: ~2 min from deploy to active/idle (single unit). `Waiting for resource limit patch to apply` appears for ~30s in the transitional status. On Juju 4 with the 2/stable track, startup is similar.
- **Memory**: 71Mi RSS at idle for Prometheus 3.11.3; 82Mi RSS for Prometheus 2.55.1 on Juju 4. The workload is lean in both cases.
- **Pebble layer**: Uses `override: replace`, `startup: enabled`. No health check configured. The `command` includes `--web.enable-lifecycle` for hot-reload (rev 311; rev 301 on Juju 4 also includes it).
- **Config hash optimisation**: SHA256 hashes of config and alerts are stored in `/etc/prometheus/config.sha256` and `alerts.sha256` to avoid unnecessary pushes. A no-op config change triggers `_configure` but correctly skips file generation and reload.
- **TLS toggle**: When TLS is added, cert/key/CA files are pushed to `/etc/prometheus/`, `web.config.file` is added to the Pebble layer with TLS config, the self-scrape scheme switches to `https`, and `internal_url` returns `https://...`. When TLS is removed, cert files are deleted (by `__init__` → `_update_cert()` when `certificates-relation-broken` fires) but the Pebble layer and web config file are **not** updated — see Finding 1. If the workload is then killed or restarted (node eviction, pod reschedule, `juju refresh`), Prometheus enters a permanent crash-loop (`backoff` state) with error `failed to read cert_file...no such file or directory` while the charm reports `active`. Recovery only happens via an unrelated `juju config` change that triggers `_configure()`. Confirmed four times on Juju 3.6 (rev 311) and once on Juju 4 (rev 301).
- **Ingress + TLS**: With TLS enabled, ingress via Traefik returns HTTP 500. Traefik logs show `tls: failed to verify certificate: x509: certificate signed by unknown authority`. The Traefik config shows the service URL is correctly `https://prometheus-k8s-0...svc.cluster.local:9090`, but Traefik's `serversTransport` lacks `rootCAs` or `insecureSkipVerify` — the CA cert is not forwarded to Traefik. The charm sends `scheme: https` but `mode: http` (the default), and more fundamentally, the CA cert is not shared with Traefik to verify the backend — see Finding 2.
- **Self-scraping**: Each Prometheus unit scrapes only itself (localhost target) at 5s interval. The scrape job uses FQDN with proper Juju topology labels.
- **Remote write receiver**: Always enabled (`--web.enable-remote-write-receiver`) in the Pebble layer, regardless of whether any remote-write consumer is related. Wasteful but harmless.
- **Alertmanager config**: Properly renders when relation is added and cleanly disappears when removed.
- **Pebble WebSocket noise**: Actions and hooks produce `WebSocketConnectionClosedException` tracebacks in logs from the ops Pebble client. This is an ops library issue, not charm-specific, but it pollutes debug-log output.
- **Hook queue backlog**: When multiple relations are added in quick succession, the `certificates-relation-broken` hook can be queued behind `grafana-dashboard-relation-joined`, `ingress-relation-joined`, `catalogue-relation-changed`, and other hooks. `certificates-relation-departed` fired ~55s after the `juju remove-relation` command, and `certificates-relation-broken` fired ~105s after. This amplifies the window for Finding 1 — the stale config persists for ~2 minutes before the broken hook even runs.
- **Scale behaviour**: Both units are independently scraped. Self-scrape targets are localhost only — each Prometheus only scrapes itself, not its peer. Unit 1's initial config was the container image default until all hooks fired (expected but briefly non-configured).
- **Kill-recovery (without TLS)**: Pebble auto-restarts the workload process within seconds. The charm returns to active/idle without intervention. **With TLS removed** (stale web config), killing the workload causes a permanent crash-loop (Pebble `backoff` state) with the charm still reporting `active` — see Finding 1. Recovery requires an unrelated `juju config` change to trigger `_configure()`.
- **`_update_status` recovery**: The charm's `_update_status` handler (`src/charm.py:806-808`) calls `_configure()` whenever the unit status is not `ActiveStatus`. This allows automatic recovery from some failure modes (e.g. config reload timeout), but it does **not** help with Finding 1 because after TLS removal the unit status IS `active` — the charm never detects the workload crash-loop.
- **Empty config values**: Setting config options to empty string (`""`) produces inconsistent error messages: `metrics_retention_time=""` → `"Invalid time spec : "` (trailing space), `log_level=""` → `"Invalid loglevel:  given, ..."` (double space before "given"). Both are valid BlockedStatus messages but the formatting is inconsistent — see Finding 15.
- **Juju 4 client compatibility**: `juju status` without `--format` fails on Juju 4.0.5 with client 4.0.12: `"patterns are not implemented"`. `juju status --format yaml` works. This is a Juju CLI issue, not charm-specific, but affects operators using the 4.x client.
- **Catalogue relation data**: The catalogue relation's `application-data` from prometheus-k8s was observed as `{}` (empty) in one deployment (without ingress present), suggesting `_catalogue_item` may fail silently. The `catalogue.update_item()` call is inside `_configure()` and the `_catalogue_item` property accesses `self.external_url`, which can be `None` — see Finding 6.

## Findings

Ordered by severity. All were verified against the deployed revision (311) or by reading the specific code paths noted.

### 1. TLS removal does not trigger full reconfiguration — workload enters crash-loop while charm reports active
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:290-292` (observer list), `src/charm.py:203` (`__init__` calls `_update_cert`), `src/charm.py:567` (`_on_certificate_available`), `src/charm.py:890` (`_generate_command`)
- **Evidence**: The only TLS-related observer is on `certificate_available` (`src/charm.py:290-292`). There is no observer for `certificates-relation-broken` or `certificates-relation-departed`. `__init__` runs on every hook and calls `self._update_cert()` (line 203), which sees `_tls_config` is `None` and deletes the cert files from the workload container — but `_configure()` is never called, so the web config file (`/etc/prometheus/prometheus-web-config.yml`) still references the deleted `server.cert`/`server.key`, the Pebble plan still has `--web.config.file=...`, and the charm reports `active`. When the workload process is then killed (tested by `pkill -9 prometheus`), Pebble restarts it but Prometheus immediately exits with `"Unable to validate web configuration file" err="failed to read cert_file (/etc/prometheus/server.cert): no such file or directory"`, and Pebble enters permanent `backoff` retry state while the charm status stays `active`. Recovery only happens when an unrelated config change triggers `_configure()`, which removes the stale web config and updates the Pebble layer. Reproduced 4 times across three models (rv-prom-deep, rv-deep2, rv-deep3) and two Juju versions (3.6 rev 311, 4.0.5 rev 301). Also observed: when multiple relations are active, the `certificates-relation-broken` hook can be queued behind other hooks, extending the stale-config window to ~2 minutes after `juju remove-relation`.
- **Impact**: If Prometheus restarts for any reason (node eviction, pod reschedule, `juju refresh`) after TLS removal, it fails to start and stays down indefinitely, while the operator sees `active` status the whole time.
- **Fix**: Observe `certificates-relation-broken` and `certificates-relation-departed` and call `_configure()`:
  ```python
  self.framework.observe(self.on.certificates_relation_broken, self._configure)
  self.framework.observe(self.on.certificates_relation_departed, self._configure)
  ```
  Alternatively, have `_configure()` call `_update_cert()` at the start so cert cleanup and Pebble/web-config updates happen atomically.
- **Linter rule**: "a charm using `tls_certificates_interface` must observe `*-relation-broken` on the certificates endpoint" — mechanically checkable by confirming presence of both the TLS requirer import and an observer for `certificates_relation_broken`.

### 2. Ingress via Traefik is broken when TLS is enabled
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:696-698` (`provide_ingress_requirements`), `src/charm.py:205-213` (`IngressPerUnitRequirer` constructor)
- **Evidence**: `IngressPerUnitRequirer` is constructed with `mode` defaulting to `"http"` (never overridden) and `scheme=lambda: "https" if self._tls_available else "http"`. `_configure()` calls `provide_ingress_requirements(scheme=..., port=...)` with `scheme=https` when TLS is on. Traefik correctly sets the service URL to `https://prometheus-k8s-0...svc.cluster.local:9090`, but its `serversTransport` config lacks `rootCAs`/`insecureSkipVerify`, so it cannot verify the self-signed cert. Traefik logs: `'500 Internal Server Error' caused by: tls: failed to verify certificate: x509: certificate signed by unknown authority`. Confirmed 3 times: `curl http://.../rv-*-prometheus-k8s-0/-/healthy` → 500; direct pod access shows HTTPS 200, HTTP 400 as expected. Related to open issues #725 and #735.
- **Impact**: Operators who deploy Prometheus with both TLS and ingress — a common production pattern — get a non-functional ingress endpoint with no charm-level indication of the problem; the charm still shows `active`.
- **Fix**: Forward the CA cert to Traefik so it can verify the backend, e.g. via ingress relation data (requires coordination with the Traefik charm), configure `insecureSkipVerify` on the backend transport (less secure), or serve Prometheus on both HTTP and HTTPS and use `mode: http` for ingress.
- **Linter rule**: not established — requires semantic understanding of the TLS+ingress interaction.

### 3. `_update_ca_certs` unconditionally restarts Prometheus
- **Severity**: medium
- **Kind**: performance / bug
- **Where**: `src/charm.py:645`
- **Evidence**: `self.container.restart("prometheus")` is the final line of `_update_ca_certs()`. After writing new CA certificates and running `update-ca-certificates --fresh`, the method always restarts Prometheus, even though CA changes only affect outgoing scrape connections and could be handled by a hot-reload.
- **Impact**: Every `receive-ca-cert` relation change causes a full restart, resetting WAL replay and creating a metrics-ingestion gap. Costly in environments with frequent CA rotation or many related charms.
- **Fix**: Replace the restart with `self._configure(None)` or `self._prometheus_client.reload_configuration()`.
- **Linter rule**: "`container.restart()` in a hot-path observer that does not change Pebble layer args" — checkable with flow analysis.

### 4. `subprocess.run` for `update-ca-certificates` on the charm unit is unguarded — breaks 35 scenario tests
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:626`
- **Evidence**: `subprocess.run(["update-ca-certificates", "--fresh"])` runs on the charm unit (not the workload container), with no `try/except` or `shutil.which()` guard. This binary may not exist on minimal or non-Debian bases. All 35 scenario-based unit tests fail with `scenario.errors.UncaughtCharmError: Uncaught FileNotFoundError` because the test environment lacks it.
- **Impact**: Alert rule filtering, datasource exchange, CA cert handling, server scheme, exemplars, logging, Prometheus API integration, and remote write have no scenario-test coverage as a result. On a charm unit without the binary, any hook reaching this code would crash.
- **Fix**: Guard with `shutil.which("update-ca-certificates")` or wrap in `try/except FileNotFoundError`. The same command already runs inside the workload container at line 625; consider whether the charm-unit invocation is needed at all.
- **Linter rule**: "any `subprocess.run` call in charm code must be wrapped for `FileNotFoundError`" — mechanically checkable.

### 5. `Prometheus` client class uses `verify=False` for all HTTPS requests
- **Severity**: medium
- **Kind**: bug / security
- **Where**: `src/prometheus_client.py:45,69`
- **Evidence**: `reload_configuration()` and `_build_info()` both call `requests.*(url, timeout=..., verify=False)`. `_update_cert()` (`src/charm.py:610-614`) writes the CA cert to the charm unit and runs `update-ca-certificates --fresh` specifically so TLS verification against the workload would work — but `verify=False` bypasses this entirely.
- **Impact**: The charm cannot detect a MITM or a misconfigured cert between itself and the Prometheus workload. Low practical risk (intra-pod traffic) but a defense-in-depth gap, and it makes the `update-ca-certificates` call on the charm unit (Finding 4) arguably pointless.
- **Fix**: Remove `verify=False` and rely on the system trust store (already updated with the charm-installed CA), or fall back to `verify=False` with a logged warning only if the trust-store update is unavailable.
- **Linter rule**: "`requests.*(verify=False)` in charm code should be justified with a comment" — mechanically checkable.

### 6. Integration tests heavily xfailed/skipped — upgrade and multi-unit behaviour untested
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_upgrade_charm.py:22`, `tests/integration/test_prometheus_scrape_multiunit.py:49`, `tests/integration/test_remote_write_with_zinc.py:23`
- **Evidence**: `test_upgrade_charm.py` is entirely xfailed (`"pytest-operator does not support 26.04 bases yet"`). `test_prometheus_scrape_multiunit.py` has all 7 tests skipped (`"xfail"`). `test_remote_write_with_zinc.py` has all 3 tests skipped (`"This fails forever in GH right now."`). One test in `test_remote_write_grafana_agent.py` is also skipped. ~15 integration tests total are inactive.
- **Impact**: Upgrade paths, multi-unit scrape behaviour, and zinc remote-write integration are not validated at all. The upgrade test in particular (`juju refresh` restarts the workload) or the multiunit test could have caught Finding 1's crash-loop behaviour had they run.
- **Fix**: Update `pytest-operator` to support 26.04 bases, fix the zinc test, re-enable the multiunit test.
- **Linter rule**: not established.

### 7. `self_scraping_job` `ca_file` uses raw PEM content rather than a file path
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:403`
- **Evidence**: `"ca_file": tls_config.ca_cert` sets the raw PEM content, not a filesystem path. The Prometheus scrape config spec defines `ca_file` as a path. `_process_tls_config` (`src/charm.py:1172-1197`) writes the content to a file internally, so it works within this charm's own ecosystem, but any external consumer of this scrape job that follows the Prometheus spec will misinterpret the value. Open issue #670 tracks this.
- **Impact**: Interoperability problem — other charms consuming scrape jobs from prometheus-k8s without the same convention will break.
- **Fix**: Rename the key (e.g. to `ca`) to signal content rather than path, or have `self_scraping_job` write to a temp file and reference it by path.
- **Linter rule**: not established.

### 8. Catalogue API endpoints use `external_url` (can be `None`) instead of `most_external_url`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:385`
- **Evidence**: `api_endpoints={key: f"{self.external_url}{path}" ...}` uses `external_url`, which is `None` without an ingress relation. `catalogue_item` correctly uses `most_external_url` for the top-level URL, but the API endpoint URIs don't. When ingress IS present, `external_url` resolves and the data is correct (observed working in rv-deep3). The bug manifests only with catalogue-but-no-ingress.
- **Impact**: Without ingress, the catalogue receives API endpoint URIs like `None/api/v1/query` — broken links on the COS catalogue page.
- **Fix**: Use `self.most_external_url` on line 385.
- **Linter rule**: not established.

### 9. `api_timeout=2.0` hardcoded in Prometheus client — causes false "Waiting for prometheus to start"
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/prometheus_client.py:21`
- **Evidence**: `def __init__(self, endpoint_url=..., api_timeout=2.0)`, never overridden by `PrometheusCharm` (`self.internal_url` instantiation at line 243). Open issue #700 reports indefinite "Waiting for prometheus to start" in resource-constrained or high-latency environments.
- **Impact**: Operators see indefinite maintenance status for a functional Prometheus whose config reload just took >2s.
- **Fix**: Make the timeout configurable, or raise the default to 5-10s.
- **Linter rule**: not established.

### 10. Juju 4 deployment blocked for the 3.11 track
- **Severity**: medium
- **Kind**: ux
- **Where**: `charmcraft.yaml:42-46`
- **Evidence**: `3.11/*` channels use `ubuntu@26.04` as their base, which Juju 4.0.5 rejects ("charm defined bases ubuntu@26.04 not supported"). The `2/stable` track (rev 301, `ubuntu@24.04`) deploys successfully on Juju 4 with Prometheus 2.55.1.
- **Impact**: Operators on Juju 4.x cannot deploy Prometheus 3.11 via any published channel; stuck on 2.x. Primarily a Juju limitation, not a charm bug, but the practical effect is the same.
- **Fix**: No charm-side fix possible until Juju 4 supports `ubuntu@26.04`; document the 2/stable workaround for Juju 4 users in the interim.
- **Linter rule**: not applicable.

### 11. No Pebble health check configured
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:519-546` (`_prometheus_layer`)
- **Evidence**: The Pebble layer defines `override`, `summary`, `command`, `startup`, `environment` but no health check. A hung-but-alive Prometheus process would not be detected or restarted by Pebble.
- **Impact**: A deadlocked Prometheus would show `active` indefinitely.
- **Fix**: Add an HTTP or exec health check, e.g. probing `/-/healthy`.
- **Linter rule**: "Pebble services should define a health check" — mechanically checkable.

### 12. `assert` used for production logic in `_get_pvc_capacity`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:989`
- **Evidence**: `assert "database" in self.model.storages, "..."` — assertions are compiled out under `python -O`.
- **Impact**: If run with optimizations enabled, the guard silently disappears.
- **Fix**: Replace with an explicit `if`/`raise` or status guard. Ruff rule S101 flags this.
- **Linter rule**: "`assert` used outside test code" — mechanically checkable (ruff S101).

### 13. `rehash` warning noise in logs on every hook
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:625`
- **Evidence**: Every hook calling `_update_cert()` produces `rehash: warning: skipping ca-certificates.crt, it does not contain exactly one certificate or CRL` in debug-log — benign but repeated.
- **Impact**: Trains operators to ignore debug-log warnings, masking real issues over time.
- **Fix**: Ensure the CA cert file ends with a newline, or suppress stderr for this command.
- **Linter rule**: not established.

### 14. `GrafanaSourceProvider` instantiated with `external_url` then re-pointed to `internal_url`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:251` and `src/charm.py:695`
- **Evidence**: Instantiated with `source_url=self.external_url` (can be `None`), then re-pointed to `self.internal_url` during `_configure()`. Open issue #686 tracks it.
- **Impact**: Short-lived window where Grafana may receive a `None`/broken URL. Low practical impact.
- **Fix**: Use `self.internal_url` or `most_external_url` as the initial value.
- **Linter rule**: not established.

### 15. Empty-string config values produce inconsistent error messages
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:340-342,396-408`
- **Evidence**: `metrics_retention_time=""` → `"Invalid time spec : "` (trailing space); `log_level=""` → `"Invalid loglevel:  given, ..."` (double space). Empty strings aren't special-cased before validation.
- **Impact**: Confusing error text for operators trying to reset config via empty string; also awkward to parse programmatically.
- **Fix**: Special-case the empty string before validation with a clear, consistent message.
- **Linter rule**: not established.

### 16. `juju status` fails on Juju 4 with client 4.0.12
- **Severity**: low
- **Kind**: ux
- **Where**: N/A (Juju client/server issue, not charm code)
- **Evidence**: `juju status` on a Juju 4.0.5 controller with client 4.0.12 fails: `ERROR juju client not compatible with server: patterns are not implemented`. `juju status --format yaml` works.
- **Impact**: Affects any operator deploying this charm on Juju 4 with a mismatched client, but is not a charm defect.
- **Fix**: Upgrade the controller to 4.1+ or match the client version.
- **Linter rule**: not applicable.

### 17. CONTRIBUTING.md links to the wrong repository
- **Severity**: low
- **Kind**: docs
- **Where**: `CONTRIBUTING.md:~17`
- **Evidence**: Links point to `canonical/prometheus-operator` instead of `canonical/prometheus-k8s-operator`.
- **Impact**: New contributors open issues on the wrong repo.
- **Fix**: Update URLs.
- **Linter rule**: not applicable.

### 18. Remote write receiver always enabled
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:900`
- **Evidence**: `--web.enable-remote-write-receiver` is always in the Pebble command, regardless of whether any `receive-remote-write` consumer is related.
- **Impact**: Minor unnecessary attack surface; low severity since the port is cluster-internal.
- **Fix**: Conditionally include the flag based on active `receive-remote-write` relations, or document the design choice.
- **Linter rule**: not established.

## Worth copying

- **Hash-based config/alert change detection** (`src/charm.py:1116-1165`): SHA256 of the full config dict + web config + certs, compared against a stored hash before pushing. Combined with Pebble layer comparison (`_update_layer()`, `src/charm.py:790-801`), the charm only restarts when the command line changes and only reloads when the config file changed. Gold standard for reconciliation efficiency.
- **Composite pull/push status pattern** (`src/charm.py:147-169`, `334-345`): `StoredState` tracks push-style statuses (e.g. k8s patch failure) alongside `collect_unit_status` pull-style statuses. Clean pattern for statuses surviving across events.
- **Pebble layer comparison** (`src/charm.py:790-801`): Combines plan-equality with `all(svc.is_running())` before deciding whether to replan — catches both drift and crashes. Many charms only check one.
- **`promtool check config` validation** (`src/charm.py:955-966`): Validates generated config before replanning; `validate-configuration` action wraps this for operators. Distinct status messages for invalid config vs. validation failure vs. replan failure.
- **Rich `charmcraft.yaml` description** (`charmcraft.yaml:10-33`): Full paragraph on the charm's role plus a feature bullet list — far better than the typical one-liner.
- **Terraform module** (`terraform/`): Complete, with `variables.tf`, `outputs.tf`, and auto-generated README via `terraform-docs`.
- **`uv` packaging** (`charmcraft.yaml`): Uses the `uv` plugin with `uv.lock`, ahead of the curve.
- **`ops_tracing` integration**: Uses the newer `ops[tracing]` integration rather than the older `charm_tracing` library (migrated in commit `3e64be7`).

## Common-practice notes

- Single-file metadata (`charmcraft.yaml` only, no `metadata.yaml`) — modern Canonical convention.
- Uses TLS v4 (`v4.tls_certificates`), correctly handling `CertificateRequestAttributes` with `frozenset` for `sans_dns`.
- `KubernetesComputeResourcesPatch` with `adhere_to_requests=True` — standard across COS charms.
- Owns `lib/charms/prometheus_k8s/v0/prometheus_scrape.py` (1889 lines, LIBPATCH 62) and `v1/prometheus_remote_write.py` (784 lines, LIBPATCH 16) — the canonical libraries used across dozens of other charms.
- `justfile` imports `charms.just`, the team's shared task-runner convention.
- `PrometheusRemoteWriteConsumer.endpoints()` (library line 545) extracts only `url` from relation data, with no TLS passthrough — remote-write to TLS-enabled backends is not supported through the library.
- `ca_file` semantics divergence (content vs. path, see Finding 7) is an accepted-but-known ecosystem quirk (#670).

## Tests

| Layer | Framework | Count | Status | Notes |
|-------|-----------|-------|--------|-------|
| Lint | ruff | — | ✅ All pass | `tox -e lint`, 0 errors |
| Static | pyright | — | ✅ All pass | `tox -e static`: 0 errors, 0 warnings, 0 informations |
| Unit (Harness) | `ops.testing.Harness` | 32 | ✅ All pass | `test_charm.py`, `test_transform.py` |
| Unit (Scenario) | `scenario` | ~145 | ❌ 35 fail, 4 error | All fail with `FileNotFoundError` (Finding 4) |
| Integration | pytest-operator | 13 files | Not run | Requires k8s + substantial time; several files xfailed/skipped (Finding 6) |
| Interface | interface-tester | not established | Not run | `tests/interface/` |

**Observations**:

- Harness tests (`tests/unit/test_charm.py`, 35KB) give solid coverage of config validation, retention size, alert filenames, TLS config, and Pebble plan generation, asserting on generated content rather than just status.
- Scenario tests are well-structured (alert filtering, datasource exchange, CA cert forwarding, server scheme, exemplars, logging, remote write) but all dead due to the unmocked `subprocess.run` (Finding 4). Simplest fix: mock `subprocess.run` at the fixture level.
- Integration tests (`tests/integration/test_charm.py`) deploy a local `prometheus-tester` charm and assert on generated scrape config/alert rules — substantial where they run. But `test_upgrade_charm.py` is fully xfailed, `test_prometheus_scrape_multiunit.py` fully skipped (7 tests), `test_remote_write_with_zinc.py` fully skipped (3 tests) — see Finding 6.
- Coverage gaps relative to findings: no integration test removes the certificates relation to verify recovery (Finding 1); no ingress integration test at all (Finding 2, issue #735); no test for `_update_ca_certs` restart behaviour (Finding 3); no regression test for `api_timeout` (Finding 9); no scenario test for `ca_file` content-vs-path (Finding 7).

## Docs

| Document | Assessment |
|----------|------------|
| `README.md` | Comprehensive (11KB), covers all relations and deployment. Example shows outdated version "2.33.5" — should show v3.11.x. |
| `INTEGRATING.md` | Short (2.2KB). Open issue #711: should recommend Grafana Agent over a direct Prometheus relation. |
| `CONTRIBUTING.md` | Dead links to `canonical/prometheus-operator` (wrong repo, Finding 17). Otherwise thorough (7KB). |
| `SECURITY.md` | Standard Canonical template. |
| `RELEASE.md` | Clear release process steps. |
| `charmcraft.yaml` | Excellent description with feature bullets (see Worth copying). |
| `terraform/README.md` | Auto-generated, complete and accurate. |
| `release-notes/` | Detailed notes for 2.53→2.55 and 2.55→3.11 upgrade paths. |
| `docs/` | No `docs/` directory — links to the COS documentation site instead. |

## Open questions

1. **#832** — "Introduction of TLS causes agent to return maintenance status": not reproduced here (charm went active immediately after TLS was configured). Possibly specific to `manual-tls-certificates` or the COS 2/stable environment; needs reproducing with those exact charms (unverified).
2. **#845** — "flapping issues: position-dependent value from unordered data": `ca_certs` from `get_all_certificates()` is unordered/position-dependent (confirmed in code at line 640) but not observed in single-unit testing. Would need repeated deployments with multiple CA cert providers, diffing resulting config files.
3. **#796** — "ModelError: permission denied when setting remote_write endpoint during relation-created": not reproduced on rev 311; may be fixed or specific to older Juju.
4. Juju 4 deployment lock-out for the 3.11 track — see Finding 10.
5. Scenario test cleanup (Finding 4): mocking `subprocess.run` vs. guarding with `shutil.which` both work; open question whether the charm-unit `update-ca-certificates` call is needed at all given the workload-container invocation.
6. Catalogue data observed as `{}` in one deployment even after `_configure()` ran (rv-deep2, without ingress) — could be transient, or the catalogue library's `update_item()` silently discarding a `None` URL from `_catalogue_item` (Finding 8).
