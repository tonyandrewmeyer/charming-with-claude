# prometheus-pushgateway-k8s

A compact K8s charm (~220 lines of core logic) for Prometheus Pushgateway, using a reconciler pattern and integrating cleanly with the observability ecosystem. It ships with a **critical, confirmed bug**: `_certs_available` in `src/charm.py` crashes the charm whenever the `certificates` relation is removed, present identically on all three published tracks (1/stable rev 27, 2/stable rev 30, 1.11/stable rev 33). The crash cascades — stale certificates stay on disk, the scrape-job spec and push-endpoint URL are never corrected back to HTTP, and peer relation data retains stale TLS material. Separately, a Pebble layer-comparison bug restarts the workload on every hook, confirmed via Pebble logs to recur every 5 minutes in steady state — an ongoing outage, not just a deploy-time blip. A zombie `prometheus-pushgateway` Pebble service baked into the OCI image sits alongside the real one as a latent port-9091 conflict. No actions are defined. Test coverage on the TLS code paths (`_certs_available`, `_update_certs`) is 0%.

A maintainer should fix `_certs_available` first (one-line change, trivially reproducible, affects every deployed track), then fix the Pebble layer comparison to stop the every-5-minute restart, then clean up the zombie Pebble service on upgrade.

| | |
|---|---|
| Repo | canonical/prometheus-pushgateway-k8s-operator @ `1bdb316` (2026-06-30) |
| Charms | prometheus-pushgateway-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (juju 3.6.25) and concierge-k8s-4 (juju 4.0.5). Tested 1/stable rev 27, 2/stable rev 30 (blocked on refresh, not fully exercised), 1.11/stable rev 33. Plus scale, restart, catalogue-integration, and repeat TLS-cycle testing. |
| Reviewed | 2026-07-28 |

## What it does

Deploys Prometheus Pushgateway on Kubernetes. Provides a `push-endpoint` relation for clients to discover the push URL and push metrics via HTTP/HTTPS. Optionally integrates with Prometheus (`metrics-endpoint`), Loki (`log-proxy`), TLS certificates, Traefik ingress, the Juju catalogue, and charm tracing (Tempo). The workload writes metrics to `/data/metrics` backed by Juju storage.

## Deployment log

### Juju 3.6 (concierge-k8s-3, Kubernetes v1.32.13)

```
$ juju add-model rv-pushgw-36
$ juju deploy prometheus-pushgateway-k8s --channel 1/stable
Deployed "prometheus-pushgateway-k8s" from charm-hub charm "prometheus-pushgateway-k8s",
  revision 27 in channel 1/stable on ubuntu@22.04/stable
```

Active in ~70 seconds. Workload version 1.11.1. Then deployed integrations: self-signed-certificates (TLS), traefik-k8s (ingress), prometheus-k8s (metrics-endpoint), loki-k8s (log-proxy).

### Juju 4.0.5 (concierge-k8s-4, Kubernetes v1.32.13)

```
$ juju add-model rv-test-k4
$ juju deploy prometheus-pushgateway-k8s --channel 1/stable
Deployed "prometheus-pushgateway-k8s" from charm-hub charm "prometheus-pushgateway-k8s",
  revision 27 in channel 1/stable on ubuntu@22.04/stable
```

Same behaviour as Juju 3.6: active in ~70 seconds, same zombie Pebble service, same restart-every-hook issue. (A first attempt at this model, `rv-pushgw-int`, had a repeatedly timing-out deploy on an apparently corrupted model and was abandoned in favour of a fresh model.)

**Gap vs HEAD**: The deployed rev 27 corresponds to git sha `ef128db` (2025-05-14). Local HEAD is `1bdb316` (2026-06-30, matches `_context/head.txt`), 24 commits ahead. The only change to `src/charm.py` between them is the addition of `ops_tracing` (charm tracing). The `_certs_available` bug, Pebble comparison bug, and zombie service issue exist identically in both.

### Second deployment (rv-pg-deepen, concierge-k8s-3, for deeper testing)

```
$ juju add-model rv-pg-deepen
$ juju deploy prometheus-pushgateway-k8s --channel 1/stable
$ juju deploy self-signed-certificates --channel 1/edge
$ juju deploy grafana-agent-k8s --channel 2/edge
$ juju integrate prometheus-pushgateway-k8s:certificates self-signed-certificates:certificates
$ juju integrate prometheus-pushgateway-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
$ juju integrate prometheus-pushgateway-k8s:log-proxy grafana-agent-k8s:logging-provider
```

Active in ~20s after deploy. TLS enabled after relation. Repeated the TLS removal test to capture the full traceback (finding #1). `grafana-agent-k8s` stayed blocked (missing cloud-config/send-remote-write), as expected — it needs more integrations to function.

**Scale up/down** (2 → 1 units): both units reached active/idle; scale-down was a clean teardown, no issues.

**Refresh attempt**: `juju refresh --channel 2/stable` failed because rev 27 is on ubuntu@22.04 and rev 30 is on ubuntu@24.04 (cross-base refresh not supported). The only same-base refresh available is a no-op to the same revision.

**Cross-channel availability**: three tracks — 1 (ubuntu@22.04, rev 27), 2 (ubuntu@24.04, rev 30), 1.11 (ubuntu@26.04, rev 33).

### Third deployment (rv-deep-pushgw, concierge-k8s-3, catalogue/tracing testing)

```
$ juju add-model rv-deep-pushgw
$ juju deploy prometheus-pushgateway-k8s --channel 1/stable
$ juju deploy catalogue-k8s --channel 3.0/edge
$ juju deploy tempo-k8s --channel latest/edge
$ juju integrate prometheus-pushgateway-k8s:catalogue catalogue-k8s:catalogue
```

Catalogue integration succeeded immediately; the pushgateway appeared with URL `prometheus-pushgateway-k8s-0.prometheus-pushgateway-k8s-endpoints.rv-deep-pushgw.svc.cluster.local:9091` — no scheme prefix (see finding #17).

**Pod restart test**: `kubectl delete pod`. New pod came up, charm reached active/idle within ~30 seconds. The zombie `prometheus-pushgateway` service returned (baked into the OCI image). Workload version preserved.

### Fourth deployment (rv-deep-pushgw3, concierge-k8s-3, 1.11/stable rev 33 on ubuntu@26.04)

```
$ juju add-model rv-deep-pushgw3
$ juju deploy prometheus-pushgateway-k8s --channel 1.11/stable
$ juju deploy self-signed-certificates --channel 1/edge
$ juju integrate prometheus-pushgateway-k8s:certificates self-signed-certificates:certificates
```

TLS enabled. Removing the certificates relation reproduced the **same crash** as rev 27 — `AttributeError: 'NoneType' object has no attribute 'read'`, error state, retry every ~10 seconds. Stale certs left on disk. Confirms the `_certs_available` bug on all three published tracks.

## Observed behaviour

### Restart on every hook, confirmed continuous every 5 minutes
On Juju 3.6: restarted at pebble-ready (16:15:57) and config-changed (16:15:59). On Juju 4.0.5: restarted at pebble-ready (04:30:52) and config-changed (04:30:54) — two restarts per deploy for a single unit, no config changes. The restart continues on every subsequent update-status hook (default 5-minute interval): Pebble logs from a long-running unit show `"TLS is disabled"` logged fresh at 04:57, 05:02, 05:06, 05:12, 05:14 — exactly every 5 minutes, each a new process start. Cause: `_set_pebble_layer` compares the full merged Pebble plan (which includes the zombie `prometheus-pushgateway` service) against the new single-service layer, so the two are never equal.

### Zombie Pebble service survives everything
The `prometheus-pushgateway` service (inactive, `startup: enabled`, command `/bin/pushgateway`) is present in the Pebble plan on both Juju versions. It survives pod deletion because it's baked into the container image, not created by the charm. It is never cleaned up.

### TLS lifecycle: crash on relation removal, stale certs left on disk
1. Related `self-signed-certificates` to pushgateway. CertHandler obtained certs, `_update_certs` pushed them to the container, `web-config.yml` created, pushgateway restarted with TLS enabled.
2. Verified HTTPS: `curl -sk https://10.152.183.232:9091/metrics` returned metrics; a test metric pushed over HTTPS succeeded.
3. Removed the certificates relation. `certificates-relation-broken` crashed with `AttributeError: 'NoneType' object has no attribute 'read'`. Error state, retried every ~10 seconds, failing each time.
4. `juju resolve --no-retry` recovered the charm to active, but `server.cert`, `server.key`, `cos-ca.crt`, `web-config.yml` remained on disk. The pushgateway kept serving HTTPS with stale certificates.
5. Deleting the pod gave a fresh filesystem with no stale certs; the pushgateway then started with TLS disabled as expected.

### Kill workload process: Pebble auto-recovers
`kill $(pgrep pushgateway)` inside the container. Pebble auto-restarted the service within ~1 second; the process logged a graceful `SIGINT`/`SIGTERM` shutdown first.

### Prometheus and Loki integrations: blocked by cluster RBAC
Both `prometheus-k8s` and `loki-k8s` entered `blocked` with "Failed to apply resource limit patch: statefulsets.apps is forbidden" — a cluster RBAC limitation, not a charm bug. The relations were established but the remote workloads never started. Promtail did start and repeatedly logged "connection refused" trying to reach the blocked Loki.

### Memory and CPU
67 MiB for the full pod (charm + pushgateway + promtail containers), ~3 mcores idle. Very lean. In the first deployment (no promtail) it was 38 MiB.

### Catalogue integration
Integrated successfully, publishing URL `prometheus-pushgateway-k8s-0.prometheus-pushgateway-k8s-endpoints.rv-deep-pushgw.svc.cluster.local:9091` — no `http://`/`https://` prefix, so catalogue consumers can't tell which scheme to use (finding #17).

### Pod restart
`kubectl delete pod` → Kubernetes recreated it within seconds; charm hooks re-ran (install, leader-elected, config-changed, pebble-ready) and reached active/idle within ~30 seconds. The zombie Pebble service returned; workload version was correctly restored; no data loss since the persistence file lives on a separate storage volume.

### 18+ config options visible, only `trust` belongs to the charm
`juju config prometheus-pushgateway-k8s` showed 18 options (`kubernetes-ingress-class`, `kubernetes-service-annotations`, etc.), all injected by the Traefik ingress library at runtime — none declared in `charmcraft.yaml`. Only `trust` (a Juju built-in) is genuinely the charm's own. Standard for this pattern, but clutters the operator's config view.

### Peer relation data retains stale certificates after TLS removal
After TLS removal and error resolution, the `pushgateway-peers` peer relation's local unit data still contained `ca` and `certificate`. `_on_all_certificates_invalidated` (`cert_handler.py:433-437`) attempts to clear them before emitting `cert_changed`, but the crash in `_update_certs` interrupts the synchronous event chain, and the peer data was observed intact after resolution.

### Metrics-endpoint scrape job spec and push-endpoint URL never updated after TLS removal
`_on_server_cert_changed` (`src/charm.py:215-218`) calls `_update_certs()`, then `_scraping.update_scrape_job_spec()`, then `pushgateway_provider.update_endpoint()`. Because `_update_certs()` crashes, the latter two are never reached, and `_configure()` (run on update-status) does not call them either. After TLS removal and error resolution, the scrape job spec and push-endpoint URL still advertise `https://` even though the pushgateway is serving plain HTTP — only a pod restart or another cert_changed event corrects it.

## Findings

### 1. `_certs_available` boolean-expression bug causes crash on TLS relation removal
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:193-200`
- **Evidence**:
  ```python
  @property
  def _certs_available(self) -> bool:
      return (
          self._cert_handler.enabled
          and self._cert_handler.cert
          and self._cert_handler.key
          and self._cert_handler.ca
      ) is not None
  ```
  `A and B and C and D` returns either `False` or the value of `D`, never `None`. When TLS is not configured, `self._cert_handler.enabled` is `False`, the whole expression evaluates to `False`, and `False is not None` → `True`. So `_certs_available` is `True` precisely when TLS is *not* configured.

  Confirmed traceback from `certificates-relation-broken`:
  ```
  tls_certificates.py:1863 _on_relation_broken → all_certificates_invalidated.emit()
  cert_handler.py:437    _on_all_certificates_invalidated → cert_changed.emit()
  charm.py:215           _on_server_cert_changed → self._update_certs()
  charm.py:271           self._container.push(f, None)   # content is None
  pebble.py:2756         source_io.read(self._chunk_size)
  AttributeError: 'NoneType' object has no attribute 'read'
  ```
- **Impact**: Any operator who removes TLS from a running pushgateway hits a crash and error state the charm cannot recover from unassisted (`hook failed: certificates-relation-broken`, retried every ~10 seconds; required manual `juju resolve --no-retry`). Because the "clear certs" branch of `_update_certs` is never reached, stale TLS material is left on disk.
- **Fix**:
  ```python
  return bool(
      self._cert_handler.enabled
      and self._cert_handler.cert
      and self._cert_handler.key
      and self._cert_handler.ca
  )
  ```
- **Linter rule**: "Boolean expression built only from `and`/`or` compared with `is not None`" — mechanically checkable.

### 2. Pebble layer comparison causes restart on every hook, continuing every 5 minutes in steady state
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:304-318`
- **Evidence**:
  ```python
  def _set_pebble_layer(self) -> bool:
      current_layer = self._container.get_plan()
      new_layer = self._build_pebble_layer()
      if "services" not in current_layer.to_dict() or (
          current_layer.services != new_layer.services
      ):
  ```
  `current_layer.services` is the full merged plan (`pushgateway` + the zombie `prometheus-pushgateway`); `new_layer.services` is only the charm's single service. They are never equal.
- **Impact**: The pushgateway process is killed and restarted on every hook. Confirmed with Pebble logs from a long-running unit: `"TLS is disabled"` freshly logged at 04:57, 05:02, 05:06, 05:12, 05:14 — a new process every 5 minutes, matching the default `update-status-hook-interval`. This is a steady-state outage window on every interval, not just at deploy time (two restarts were also seen at deploy: pebble-ready then config-changed). In-memory metrics not yet persisted, and any push in flight during the restart window, are lost/refused.
- **Fix**: Compare only the charm's own layer by name/service, e.g.
  ```python
  current_services = current_layer.to_dict().get("services", {})
  new_services = new_layer.to_dict().get("services", {})
  if current_services != new_services:
      self._container.add_layer(self._name, new_layer, combine=True)
      return True
  ```
  or compare only the specific service's command/override.
- **Linter rule**: "`!=` between `container.get_plan().services` and a single-layer `Layer.services`" — mechanically checkable.

### 3. Stale TLS certificates left on disk after relation removal
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:265-291`
- **Evidence**: After removing the certificates relation and resolving the error, `server.cert`, `server.key`, `cos-ca.crt`, `web-config.yml` all remained under `/etc/pushgateway/`; the pushgateway kept serving HTTPS with the old certificates until the pod was deleted (fresh filesystem cleared them). The cleanup branch of `_update_certs`:
  ```python
          else:
              for f in certs:
                  self._container.remove_path(f, recursive=True)
  ```
  is never reached because `_certs_available` (finding #1) is `True` on removal, so the `push(..., None)` branch runs instead and crashes before cleanup can happen.
- **Impact**: The charm cannot clean up TLS state on its own. `_tls_ready` checks file existence on disk and still returns `True`, so the endpoint keeps advertising `https://` with certificates that may eventually expire or no longer be trusted for scraping. Direct consequence of finding #1.
- **Fix**: Fix finding #1 — with `_certs_available` correctly `False` on removal, the `else` branch will run and remove the files.
- **Linter rule**: same as finding #1.

### 4. Scrape job spec and push-endpoint URL frozen at HTTPS after TLS crash
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:215-218`
- **Evidence**:
  ```python
  def _on_server_cert_changed(self, _) -> None:
      self._update_certs()
      self._scraping.update_scrape_job_spec(self._self_metrics_jobs)
      self.pushgateway_provider.update_endpoint(self._endpoint)
      self._configure()
  ```
  `_update_certs()` crashes (finding #1), so the two calls after it never run, and `_configure()` (called on update-status) does not call either of them either.
- **Impact**: After TLS removal and error resolution, the metrics-endpoint scrape job spec still advertises `"scheme": "https"` and the push-endpoint URL still advertises `https://` while the pushgateway is actually serving HTTP. Prometheus scraping via `metrics-endpoint` will attempt HTTPS and fail; `push-endpoint` consumers get a wrong URL. Persists until a pod restart or another cert_changed event.
- **Fix**: Fix finding #1; also consider moving these two calls into `_configure()` so the endpoint stays consistent on every hook, even after error recovery.
- **Linter rule**: not mechanically checkable.

### 5. `_pushgateway_url` accesses `relation.app` without a null guard
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/prometheus_pushgateway_k8s/v0/pushgateway.py:211`
- **Evidence**:
  ```python
  raw_data = relation.data[relation.app].get(RELATION_KEY)
  ```
  `relation.app` can be `None` briefly during relation lifecycle; this raises instead of behaving like "not ready".
- **Impact**: A requirer charm calling `is_ready()` during `relation-created` (before the remote app appears) crashes rather than returning `False`.
- **Fix**: `if relation.app is None: return None`
- **Linter rule**: "`relation.data[relation.app]` without a null check on `relation.app`" — mechanically checkable.

### 6. No `actions.yaml` — no Juju-native way to push metrics or inspect endpoint
- **Severity**: medium
- **Kind**: ux
- **Where**: missing `actions.yaml`
- **Evidence**: `juju actions prometheus-pushgateway-k8s` returns "No actions defined". Open issue #17 requests exactly this. The testingcharm (test-only) defines a `send-metric` action; the production charm does not.
- **Impact**: Operators without a separate client charm cannot script metric pushes or retrieve the endpoint URL from Juju alone.
- **Fix**: Add `actions.yaml` with `get-endpoint` and `push-metric` actions.
- **Linter rule**: "Charm provides `push-endpoint` relation but no matching action" — heuristic, not fully mechanical.

### 7. Ingress scheme lambda checks `_cert_handler.enabled` instead of `_tls_ready`
- **Severity**: low-to-medium
- **Kind**: bug
- **Where**: `src/charm.py:82`
- **Evidence**:
  ```python
  self._ingress = IngressPerAppRequirer(
      self, port=9091, scheme=lambda: "https" if self._cert_handler.enabled else "http"
  )
  ```
  `_cert_handler.enabled` is `True` as soon as a `certificates` relation exists, even before certs are issued and written to disk; `_tls_ready` checks actual file existence.
- **Impact**: During the (usually short) gap between relation creation and certs landing on disk, ingress can advertise HTTPS before the service can serve it, causing client-side connection failures. (Observed in reverse on removal: `_cert_handler.enabled` correctly went `False` and ingress showed `http://` even while stale certs meant the pushgateway was still serving HTTPS — correct by accident.)
- **Fix**: `lambda: "https" if self._tls_ready else "http"`
- **Linter rule**: heuristic — "ingress scheme lambda keyed off cert-enabled flag rather than a TLS-ready check".

### 8. `send_metric` hardcodes label-less body; no labels, type, or timestamp support
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/prometheus_pushgateway_k8s/v0/pushgateway.py:270-273`
- **Evidence**:
  ```python
  payload = f"{name} {value}\n".encode("ascii")
  post_url = f"{pushgateway_url}metrics/job/{job_name}"
  ```
  Only supports `name value`, no labels/type/timestamp. `# TODO: support the more complex cases` (lines 268-269). Tracked in open issue #11.
- **Impact**: Requirer charms cannot push properly labelled Prometheus metrics; all metrics under the same job/name are indistinguishable in queries.
- **Fix**: Extend the API to accept a labels dict, type string, and optional timestamp.
- **Linter rule**: not mechanically checkable.

### 9. Zombie `prometheus-pushgateway` Pebble service from OCI image never cleaned up
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:304-318`; OCI image `ubuntu/prometheus-pushgateway`
- **Evidence**: The Pebble plan contains three services: `pushgateway` (charm-managed), `prometheus-pushgateway` (from the OCI image's default layer, `startup: enabled`, bare `/bin/pushgateway`), and `promtail` (from LogProxyConsumer). The charm's `add_layer(..., combine=True)` merges but never removes old layers. The old service stays `inactive` only because `pushgateway`'s `override: replace` grabs port 9091 first.
- **Impact**: If Pebble ever restarts and the charm's service doesn't win the race for port 9091, the zombie service (no `--persistence.file`, no TLS config) could start instead, causing data loss and a TLS misconfiguration. Also adds noise/confusion when debugging the Pebble plan. Confirmed present on every deploy and every pod restart on both Juju versions (baked into the image).
- **Fix**: In `_on_upgrade_charm`, remove unexpected services from the plan, or switch to `combine=False` to replace the layer wholesale.
- **Linter rule**: not mechanically checkable.

### 10. No upgrade-path testing
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/` (absence)
- **Evidence**: No integration test covers `juju refresh`, scale, or upgrade from an older revision. `_on_upgrade_charm` exists but is untested — the zombie Pebble service demonstrates layer cleanup on upgrade was never exercised.
- **Impact**: The zombie service, the restart-every-hook bug, and the `_certs_available` crash could all have been caught by an upgrade/refresh test.
- **Fix**: Add an integration test that deploys an older revision, refreshes to current, and asserts the old Pebble layer is gone, TLS keeps working, and the charm stays active.
- **Linter rule**: not mechanically checkable.

### 11. TLS integration test uses fixed `asyncio.sleep(100)` instead of polling
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_prometheus_integration_tls.py:67,78`
- **Evidence**: Two hard-coded `await asyncio.sleep(100)` calls, versus the non-TLS test (`test_prometheus_integration.py`) which polls with `for i in range(20): await asyncio.sleep(5)` for the same wait.
- **Impact**: Flaky if setup is slower than 100s, wastes CI time if faster; inconsistent with the sibling test.
- **Fix**: Use the same polling pattern as `test_prometheus_integration.py`.
- **Linter rule**: "`asyncio.sleep` with hard-coded duration > 30s in an integration test with no polling fallback" — mechanically checkable.

### 12. Testingcharm hardcodes `verify_ssl=False`; TLS integration tests never verify certificates
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/testingcharm/src/charm.py:56`
- **Evidence**:
  ```python
  self.pushgateway_requirer.send_metric(name, value, verify_ssl=False)
  ```
  The TLS integration test relates pushgateway and prometheus to self-signed-certificates and sends a metric, but disables SSL verification, so it only proves the pushgateway accepts HTTPS with an invalid cert chain, not that the chain is actually valid end-to-end. It also never removes the relation, so it would never catch finding #1.
- **Impact**: A certificate-issuance or CA-trust failure would go undetected.
- **Fix**: Set `verify_ssl=True` and supply the CA cert to the requirer when a certificates relation is present.
- **Linter rule**: not mechanically checkable.

### 13. `_service_version` execs into the container on every hook
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:162-191`
- **Evidence**: `_set_service_version()` runs `self._container.exec([PUSHGATEWAY_BINARY, "--version"])` on every `_configure()` call (i.e. every hook), though the version never changes during the unit's life. Confirmed run on pebble-ready, config-changed, and update-status.
- **Impact**: Unnecessary subprocess exec on every hook, adding latency and log noise.
- **Fix**: Cache the version string after the first successful retrieval.
- **Linter rule**: "`container.exec` called unconditionally in the reconciler hot path with no caching" — mechanically checkable.

### 14. `_handle_web_config` calls `remove_path` on every hook when TLS is off
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:257-263`
- **Evidence**:
  ```python
  def _handle_web_config(self) -> None:
      if web_config := self._web_config:
          self._container.push(...)
      else:
          self._container.remove_path(WEB_CONFIG_PATH, recursive=True)
  ```
  When TLS is off (the common case), `remove_path` runs every hook even though there's nothing to remove after the first time. Confirmed hitting this path on every hook when TLS is unconfigured.
- **Impact**: Minor wasted work every hook; Pebble handles the missing-path case gracefully so no functional issue.
- **Fix**: Track whether the file was previously written, or check `container.exists()` first.
- **Linter rule**: not mechanically checkable.

### 15. pyright `pythonVersion` set to `"3.8"` but project requires Python 3.14
- **Severity**: low
- **Kind**: lint
- **Where**: `pyproject.toml:62`
- **Evidence**:
  ```toml
  [tool.pyright]
  pythonVersion = "3.8"
  ```
  while `requires-python = "~=3.14.0"`.
- **Impact**: Pyright type-checks against the wrong Python version, potentially missing 3.14-specific issues.
- **Fix**: Change to `"3.14"`.
- **Linter rule**: "pyright `pythonVersion` disagrees with `requires-python`" — mechanically checkable.

### 16. Prometheus and Loki charms could not start due to cluster RBAC
- **Severity**: low (environment issue, not charm)
- **Kind**: ux
- **Where**: deployment environment
- **Evidence**: `prometheus-k8s` and `loki-k8s` both entered `blocked` with "Failed to apply resource limit patch: statefulsets.apps is forbidden".
- **Impact**: Prevented full end-to-end verification of the `metrics-endpoint` and `log-proxy` integrations.
- **Fix**: not a charm fix — cluster RBAC configuration.

### 17. Catalogue URL published without scheme (http/https)
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:87-90`
- **Evidence**:
  ```python
  self._catalogue = CatalogueConsumer(
      self,
      item=CatalogueItem(
          "Prometheus Pushgateway",
          self._ingress.url or self._hostname + ":9091",
  ```
  With no ingress relation, the catalogue URL is `_hostname + ":9091"` with no `http://`/`https://` prefix. Confirmed in the `rv-deep-pushgw` deployment (pushgateway serving HTTP with no indication in the catalogue entry).
- **Impact**: Operators clicking the catalogue link, or scripts consuming the catalogue API, cannot tell which scheme to use.
- **Fix**: `f"{scheme}://{self._hostname}:9091"`.
- **Linter rule**: heuristic — "`CatalogueConsumer`/`CatalogueItem` URL does not start with `http://` or `https://`".

### 18. Spelling errors in library
- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/prometheus_pushgateway_k8s/v0/pushgateway.py:104,139`
- **Evidence**: `codespell` reports `succesfully` → `successfully` (line 104), `bulding` → `building` (line 139).
- **Fix**: Correct the spellings.
- **Linter rule**: `codespell`.

### 19. Dead code: `_instance_addr` defined but never used
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:51`
- **Evidence**:
  ```python
  _instance_addr = "127.0.0.1"
  ```
  Assigned but never referenced anywhere in `src/charm.py` or elsewhere; the charm uses `socket.getfqdn()` for the actual hostname. Appears to be leftover from an earlier iteration.
- **Impact**: Confuses future maintainers into thinking it's used somewhere.
- **Fix**: Remove the line.
- **Linter rule**: "Class attribute never read" — mechanically checkable (ruff F811 / pyright `reportUnusedVariable`).

## Worth copying

1. **Single reconciler pattern** (`src/charm.py:243-255`): all hooks delegate to `_configure()`, which checks preconditions, does the work, and sets status — avoids hook-ordering bugs.
2. **Clean status handling** (`src/charm.py:243-246`): `if not self._container.can_connect(): return WaitingStatus(...)` is concise and correct, no leaking intermediate states.
3. **Port reconciliation** (`src/charm.py:337-348`): `_set_ports` diffs planned vs actual ports (open/close) rather than blindly opening — handles upgrades correctly.
4. **Version-from-workload pattern** (`src/charm.py:162-191`): running `--version` on the actual binary and reporting that as workload version reflects reality rather than assumption.
5. **Good use of scenario tests** (`tests/unit/test_tracing.py`, `tests/unit/test_version_parser.py`): both legacy `Harness` and modern `scenario`/`Context` tests present; tracing tests assert on actual relation-databag content, not just active/idle.
6. **OCI image pinned with a renovate hint** (`charmcraft.yaml:41`): `upstream-source` includes a digest plus `# renovate: oci-image tag: 1.11-26.04_edge`.
7. **CI uses reusable workflows** (`.github/workflows/`): delegates to `canonical/observability/.github/workflows/charm-pull-request.yaml@v2`, keeping CI DRY.
8. **Graceful workload shutdown on kill**: process logs "received SIGINT/SIGTERM; exiting gracefully..." on kill, Pebble restarts within 1 second, persistence file survives.

## Common-practice notes

- **Follows**: single `charmcraft.yaml` (no separate `metadata.yaml`), modern charmcraft 3.x convention; single `src/charm.py` entry point; `uv` for build/dependency management; standard observability integration set (Loki, Prometheus, catalogue, ingress, tracing) matching other canonical observability charms.
- **Follows**: CertHandler for TLS, IngressPerAppRequirer for ingress, MetricsEndpointProvider for self-scraping — all standard library choices.
- **Drifts**: no `actions.yaml` — most canonical observability charms define at least a `get-credentials`/`show-endpoint` action.
- **Drifts**: the pushgateway v0 library is minimal versus other observability charm libraries — only the simple push API. `PrometheusPushgatewayProvider` doesn't observe `relation-departed`/`relation-broken` (arguably fine given the interface, but unconventional).
- **Notable**: uses the `parse` library for version extraction, unusual versus regex/string-splitting elsewhere, but works.
- **Config noise**: 18 config options visible in `juju config` come from the Traefik ingress library, not the charm, which itself only has `trust`.

## Tests

### What exists
- 27 unit tests, all passing; mix of legacy `Harness`-based (`test_charm.py`, `test_lib.py`) and modern `scenario`/`Context`-based (`test_tracing.py`, `test_version_parser.py`).
- `tox -e unit`: 27 passed, 0 failed (0.14s). Coverage: 79% overall (src: 74%, lib: 88%).
- `tox -e lint` (ruff): all checks passed.
- `tox -e static` (pyright): 0 errors, 0 warnings on `src/`, `tests/`, `lib/charms/prometheus_pushgateway_k8s/`.
- `codespell`: 2 spelling errors in the pushgateway library.
- Integration tests: 5 files covering deploy-and-active, Prometheus integration (with/without TLS), Loki integration, and charm tracing (Tempo). Not run in this review due to resource constraints.
- Testingcharm (`tests/testingcharm/`): companion requirer charm with a `send-metric` action, used for integration testing only.
- Jubilant-based tracing test (`test_charm_tracing.py`): uses `pytest-jubilant` + `tenacity` retry, deploys a monolithic Tempo cluster, asserts the charm's hook spans reach Tempo — good end-to-end test.

### Coverage report detail
```
lib/charms/prometheus_pushgateway_k8s/v0/pushgateway.py      78      7     18      1    88%   176-181, 271-272
src/charm.py                                                154     29     32     11    74%   132, 154, 165, 187, 195, 218, 223-226, 232, 235, 238, 245-246, 251->255, 259, 266-288, 295-299, 318, 347
```
Key uncovered lines: 195 (`_certs_available` — the critical bug, completely untested), 203-208 (`_tls_ready`), 266-288 (entire `_update_certs` method, 0%), 318 (`_set_pebble_layer` return-False path), 245-246 (guard clause in `_configure`).

### Coverage gaps
- No unit test for `_certs_available` (`src/charm.py:193-200`) — 0% coverage of the critical bug.
- No unit test for `_tls_ready` (lines 203-208).
- No unit test for Pebble layer idempotency (would be caught by calling `_configure()` twice and asserting no restart the second time).
- No unit test for `_update_certs` (lines 266-288, 0% coverage).
- No upgrade test (deploy old revision, then refresh).
- No failure-mode tests: TLS relation removal, bad config, killed workload, certificate misconfiguration.
- TLS integration test gaps: fixed sleeps instead of polling; `verify_ssl=False` in the testingcharm disables real TLS validation.
- No scale/multi-unit test.

### Linter results
- ruff: all checks passed on `src/`, `lib/charms/prometheus_pushgateway_k8s/`, `tests/`.
- pyright: 0 errors, 0 warnings.
- codespell: `succesfully` → `successfully` (`pushgateway.py:104`), `bulding` → `building` (`pushgateway.py:139`).

## Docs

- **README.md** (1057 bytes): brief description plus a persistence note. The command shown (`--persistence.file=/data/metrics`) omits the shell wrapper and log redirection actually used in the Pebble plan (see doc/reality mismatch below). No deployment instructions, relation examples, config reference, or actions reference — an operator landing here would not know how to deploy or use the charm. Links to Discourse for full docs.
- **CONTRIBUTING.md** (818 bytes): clear instructions for `tox -e fmt/lint/unit/integration` and building the charm.
- **Discourse docs**: linked at `https://discourse.charmhub.io/t/prometheus-pushgateway-operator-k8s-docs-index/11980` — not reviewed here.
- **Testingcharm README** (528 bytes): instructions for packing/deploying the testingcharm, including relation and action commands. Useful for developers.
- **Doc/reality mismatch**: README states the service "is started with the `--persistence.file=/data/metrics` parameter." Observed Pebble plan command: `/bin/sh -c '/bin/pushgateway --persistence.file=/data/metrics 2>&1 | tee /var/log/pushgateway.log'`. Docs omit the shell wrapper and log redirection.
- **`charmcraft.yaml` has no `config` section**: no custom config options declared. `trust` (visible in `juju config`) is a Juju built-in; the other 17 ingress-related options are dynamically injected by `IngressPerAppRequirer` at runtime. Operators unfamiliar with this library pattern may be confused that these don't appear in `charmcraft.yaml`.

## Open questions

1. **Can the zombie `prometheus-pushgateway` Pebble service actually be triggered to start?** It is `startup: enabled` but stays `inactive` only because `pushgateway`'s `override: replace` wins the port-9091 race. Not triggered in this review's testing. Settled by: simulating a Pebble daemon restart or an image upgrade.
2. **Does `socket.getfqdn()` always return the correct K8s service FQDN?** Returned `prometheus-pushgateway-k8s-0.prometheus-pushgateway-k8s-endpoints.rv-pushgw-36.svc.cluster.local` on this cluster; behaviour on other distributions/custom DNS is unverified. Settled by: testing on additional K8s distributions.
3. **Source of the zombie Pebble layer**: confirmed to come from the OCI image `ubuntu/prometheus-pushgateway`, which ships a default Pebble layer (`prometheus-pushgateway: /bin/pushgateway`, `startup: enabled`). The charm has always used `_name = "pushgateway"`, so the old service was never charm-created. The fix is to remove it from the plan in `_on_upgrade_charm`.
