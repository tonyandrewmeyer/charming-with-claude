# falco-operators

`falcosidekick-k8s` (k8s) and `falco` (machine subordinate) are both active, well-tested charms
with clean architecture (`src/charm.py` + `state.py` + `workload.py`, pydantic-backed state,
no `StoredState`). But neither one can be trusted to report its own health: both hide a
crash-looping or misconfigured workload behind `active` status, and the k8s charm's Prometheus
and Grafana integrations are silently dead after a redeploy because they're wired inside an
idempotency guard. A maintainer should fix the TLS/health-check port mismatch and the missing
`update_status` handlers first — those two issues mean `juju status` cannot currently be trusted
for either charm.

| | |
|---|---|
| Repo | canonical/falco-operators @ `03c81e2` (2026-07-23) |
| Charms | falco, falcosidekick-k8s |
| Substrate | k8s (falcosidekick-k8s) / machine (falco) |
| Deployed | yes — `concierge-k8s-3:rv-falco-k8s3` (Juju 3.6.25, succeeded), `concierge-lxd:rv-falco-lxd` (Juju 3.6.27, succeeded); `concierge-k8s-4:rv-falco-k8s` (Juju 4.0.12) attempted but **failed** during certificates relation setup |
| Reviewed | 2026-08-25 |

## What it does

`falcosidekick-k8s` deploys a Falcosidekick sidecar container. It requires either a
`certificates` relation (mutually exclusive with `ingress`) and a `send-loki-logs` Loki relation.
On startup it renders a YAML config, pushes TLS certs into the container, sets up a Pebble health
check, and starts the service. It provides `http-endpoint` (for Falco to send events),
`grafana-dashboard`, and `metrics-endpoint`.

`falco` is a machine subordinate charm. It installs the Falco binary, manages a systemd service,
and optionally syncs custom rules/config from a git repository over SSH.

## Deployment log

### concierge-k8s-3 (Juju 3.6.25) — primary deployment

1. `juju deploy falcosidekick-k8s --channel 2/edge` → blocked "Required one of: [certificates|ingress]"
2. `juju integrate falcosidekick-k8s:send-loki-logs grafana-agent-k8s:logging-provider`
3. `juju integrate falcosidekick-k8s:certificates self-signed-certificates:certificates`
4. After ~2 min: active ✓

### Integration tests

- **metrics-endpoint → prometheus-k8s**: relation established (ID 16), but `application-data` is
  empty. `update_scrape_job_spec` was never called because it lives inside the
  `if not changed and not cert_changed: return` block — see Finding "idempotency guard".
- **grafana-dashboard → grafana-agent-k8s**: relation established (ID 14), but
  `application-data` is empty. The `relation-created` hook was not observed by the provider
  after charm redeployment — see Finding "Grafana dashboard".

### Config-change tests (k8s-3)

- `juju config falcosidekick-k8s port=2802` → active, pebble plan updated to port 2802 ✓
  (health check now hits `http://localhost:2802/healthz` — still wrong port, should be 2810)
- `juju config falcosidekick-k8s port=2801` → active, reverted ✓
- `juju config falcosidekick-k8s port=65536` → blocked "Invalid charm configuration: port" ✓
- `juju config falcosidekick-k8s --reset port` → active ✓

### Relation removal tests (k8s-3)

- `juju remove-relation falcosidekick-k8s:send-loki-logs grafana-agent-k8s:logging-provider` →
  blocked "Required relations: [send-loki-logs]" ✓; re-integrating → active in ~20s ✓
- `juju remove-relation falcosidekick-k8s:certificates self-signed-certificates:certificates` →
  blocked "Required one of: [certificates|ingress]" ✓; re-integrating → active in ~20s ✓

### Pod restart test (k8s-3)

- `kubectl delete pod falcosidekick-k8s-0` → Juju reschedules the pod automatically ✓
- Charm briefly shows `blocked "Workload failed to start"` → active after ~20s ✓

### Scale lifecycle (k8s-3)

- `juju add-unit falcosidekick-k8s -n 2` → 3 units active ✓
- `juju scale-application falcosidekick-k8s 1` → scaled to single unit ✓

### `juju remove-application` (k8s-3)

- `juju remove-application falcosidekick-k8s --destroy-storage` → unit enters
  `terminated/executing (remove)`, pod deleted ✓ (no `on.remove` handler — teardown is handled by
  Juju's k8s cleanup)

### concierge-k8s-4 (Juju 4.0.12) — FAILED

`certificates-relation-created` hook hung for ~3 minutes then failed with:
```
ops.model.ModelError: ERROR permission denied (unauthorized access)
  File ".../certificates.py", line 115, in _get_certificate_request_attributes
    if binding and binding.network.bind_address:
```
`juju resolve` does not recover it — the hook fails on every retry because
`TLSCertificatesRequiresV4.__init__()` calls this code at charm initialisation time, before any
hook body runs.

### concierge-lxd (Juju 3.6.27) — machine charm deployment

1. `juju deploy falco --channel 0.42/edge` → scale 0 (subordinate needs principal)
2. `juju integrate falco:general-info ubuntu:juju-info` → `falco/1` subordinate active ✓
3. Falco service in a crash loop (`systemctl is-active falco` → `activating (auto-restart)`) but
   `juju status` shows `active` — no `update_status` handler (see Finding "machine charm active
   while crashing")
4. `juju config falco custom-config-repository="git+ssh://nonexistent@example.com/test/repo"` →
   blocked "Failed configuring Falco" ✓
5. `juju config falco --reset custom-config-repository` → active ✓
6. `yes | juju remove-application falco` → unit removed, `systemctl is-active falco` →
   `inactive` (generic Juju cleanup; `_on_remove` was NOT called since `on.remove` is unwired) ✓

### Other k8s-3 observations

- `juju debug-log` shows `falcosidekick-pebble-check-failed` firing periodically when Pebble
  detects the health check failing. The charm does not observe this hook — it's handled silently
  by Pebble's restart policy.

## Observed behaviour

**Container readiness (k8s)**: pod `2/2 Running` in ~2 minutes after deploy.

**Pebble services (k8s)**: `falcosidekick` service shows `active`, but the Pebble health check is
`down` (8+ failures / threshold 3). From `pebble plan`:
```yaml
checks:
  health:
    override: replace
    threshold: 3
    http:
      url: http://localhost:2801/healthz
```
Port 2801 is the TLS port; `/healthz` is in `notlspaths` and actually served on 2810. The service
is restarted repeatedly by Pebble's `on-check-failure: restart` policy and recovers before Juju
polls, so `juju status` shows `active`. From live logs, repeating every ~10s:
```
http: TLS handshake error from [::1]:49364: client sent an HTTP request to an HTTPS server
```

**Metrics scrape target (k8s)**: `juju show-unit falcosidekick-k8s/0` shows empty
`application-data` on `metrics-endpoint`. `update_scrape_job_spec` was never called because it's
inside the `if not changed and not cert_changed:` early-return. If the config file or TLS certs
haven't changed since the last reconcile, the metrics scrape data is never (re)written.

**Grafana dashboard (k8s)**: `application-data` on `grafana-dashboard` is empty. The `falco.json`
dashboard file exists in the charm directory at
`/var/lib/juju/agents/<unit>/charm/src/grafana_dashboards/falco.json`, but
`GrafanaDashboardProvider` never wrote it to the relation after charm redeployment.

**Config idempotency**: when template content and certs haven't changed, the charm returns early
without calling `update_scrape_job_spec` or `_configure_healthchecks`. Confirmed from logs:
`"Configuration or certificate not changed; skipping reconfiguration"`.

**TLS certs**: both `server.crt` and `server.key` are world-readable (`0644`):
```
$ stat -c "%a %n" /etc/falcosidekick/certs/server/server.key
644 /etc/falcosidekick/certs/server/server.key
```

**Generated config (k8s, certificates relation, no ingress)**:
```yaml
listenport: 2801
tlsserver:
  deploy: true
  keyfile: "/etc/falcosidekick/certs/server/server.key"
  certfile: "/etc/falcosidekick/certs/server/server.crt"
  notlsport: 2810
  notlspaths: ["/ping", "/healthz", "/metrics"]
loki:
  endpoint: "/loki/api/v1/push"
  hostport: "http://grafana-agent-k8s-0.grafana-agent-k8s-endpoints...:3500"
```

**Machine charm service state (LXD)**:
```
$ juju status falco
falco  active  1  falco  0.42/edge  116  no
  falco/1*  active  idle  ubuntu/0

$ juju ssh ubuntu/0 -- sudo systemctl is-active falco
activating (auto-restart) (Result: exit-code)
```
Falco crashes because LXD containers lack the kernel eBPF capabilities it needs. The charm
remains `active` because it has no `update_status` handler, and `check_active()` is only called
during hooks.

**No `update_status` observer (both charms)**: confirmed from code — neither charm handles
`update_status`. Open issue #12 ("periodic health check") remains open.

**No actions defined**: `juju actions falcosidekick-k8s` and `juju actions falco` both return
"No actions defined". The machine charm's `docs/reference/actions.md` documents
`flush-falco-logs` and `reload-falco` actions that are not implemented.

## Findings

Ordered by severity.

### 1. Health check and Prometheus scrape use the wrong port when TLS is enabled

- **Severity**: high
- **Kind**: bug
- **Where**: `falcosidekick-k8s-operator/src/workload.py:226–231`
- **Evidence**:
  ```python
  listen_port = (
      NO_TLS_PORT if charm_state.ingress_relation else charm_state.falcosidekick_listenport
  )
  metrics_endpoint_provider.update_scrape_job_spec(
      [{"static_configs": [{"targets": [f"*:{listen_port}"]}]}]
  )
  self._configure_healthchecks(listen_port)
  ```
  When `tls_relation=True` and `ingress_relation=False` (certificates relation), `listen_port` is
  set to `falcosidekick_listenport` (2801, the TLS port). But `/healthz` and `/metrics` are
  `notlspaths`, served on port **2810** (non-TLS). Confirmed live: `pebble plan` shows
  `url: http://localhost:2801/healthz`; logs show `"TLS handshake error from [::1]..."` every
  ~10s; `pebble checks` shows `health down 0/3 8/3 non-2xx status code 400`.
- **Impact**: health check constantly fails and the service is restarted in a loop; Prometheus
  metrics are unreachable when TLS is configured. Both issues are invisible in `juju status`
  because the service recovers before Juju polls.
- **Fix**: always use `NO_TLS_PORT` (2810) for both the health check URL and the metrics scrape
  target, regardless of TLS/ingress configuration.
- **Linter rule**: not mechanically checkable — requires understanding Falcosidekick's
  `notlspaths` convention.

### 2. `update_scrape_job_spec` and `_configure_healthchecks` sit inside the idempotency early-return

- **Severity**: high
- **Kind**: bug
- **Where**: `falcosidekick-k8s-operator/src/workload.py:220–223`
- **Evidence**:
  ```python
  changed = self.config_file.install(context={"charm_state": charm_state})
  if not changed and not cert_changed:
      logger.warning("Configuration or certificate not changed; skipping reconfiguration")
      return   # ← early return

  listen_port = (...)
  metrics_endpoint_provider.update_scrape_job_spec(...)
  self._configure_healthchecks(listen_port)
  ```
  Both calls are skipped if neither the config file nor the TLS certs changed since the last
  reconcile. Confirmed live: `juju show-unit falcosidekick-k8s/0` on the `metrics-endpoint`
  relation shows empty `application-data` — `update_scrape_job_spec` was never invoked because
  the template content and certs hadn't changed between redeploys.
- **Impact**: after a charm redeploy, metrics scrape targets are never written to the Prometheus
  relation, so Prometheus never receives scrape configuration. The health check also fails to
  update if it needs to change (e.g. after a port change is reverted).
- **Fix**: move `update_scrape_job_spec()` and `_configure_healthchecks()` above the
  `if not changed and not cert_changed: return` guard, or restrict the guard to
  `container.replan()`/`container.restart()` only.
- **Linter rule**: "relation data provider methods called after an idempotency guard that could
  skip them" — mechanically checkable by static analysis.

### 3. Grafana dashboard relation data is empty — `GrafanaDashboardProvider` not serving dashboards

- **Severity**: high
- **Kind**: bug
- **Where**: `falcosidekick-k8s-operator/src/charm.py:78–80`,
  `falcosidekick-k8s-operator/lib/charms/grafana_k8s/v0/grafana_dashboard.py`
- **Evidence**: `juju show-unit falcosidekick-k8s/0` shows the `grafana-dashboard` relation
  (ID 14) with `application-data: {}`. `falco.json` exists at
  `/var/lib/juju/agents/<unit>/charm/src/grafana_dashboards/falco.json` inside the running pod.
  `GrafanaDashboardProvider` observes `relation_created` and `config_changed`, but the
  `relation-created` hook for this relation was not fired in the review session — the relation
  was re-established from model state after `remove-application` + `deploy` without a fresh
  `relation-created` dispatch (confirmed absent from `juju debug-log`). `MetricsEndpointProvider`
  has an analogous gap: `relation_joined` fires and calls `set_scrape_job_spec()`, but
  `_scrape_jobs` is only populated by `update_scrape_job_spec()` (Finding 2), so nothing is
  written even though the hook fired.
- **Impact**: the grafana-dashboard integration is non-functional after this kind of
  redeploy/re-relate cycle. Operators expecting the pre-built Falco dashboard in Grafana get
  nothing.
- **Fix**: have the charm's reconcile loop explicitly call
  `grafana_dashboard_provider._update_all_dashboards_from_dir()` on every reconcile, not just on
  `relation-created`.
- **Linter rule**: "charm provides a `GrafanaDashboardProvider` but does not observe any hook
  that re-triggers it after charm restart" — mechanically checkable.

### 4. `certificates` relation crashes on `network-get` permission denied

- **Severity**: high
- **Kind**: bug
- **Where**: `falcosidekick-k8s-operator/src/certificates.py:111–115`
- **Evidence**: on `concierge-k8s-4` (Juju 4.0.12), the `certificates-relation-created` hook hung
  for 2m55s then failed with:
  ```
  ops.model.ModelError: ERROR permission denied (unauthorized access)
    File ".../certificates.py", line 115, in _get_certificate_request_attributes
      if binding and binding.network.bind_address:
    File ".../ops/model.py", line 3895, in network_get
      raise ModelError(e.stderr) from e
  ```
  `TLSCertificatesRequiresV4.__init__()` calls `_get_certificate_request_attributes()` at charm
  initialisation time, so the charm becomes unloadable whenever `network-get` is forbidden by
  the RBAC in place. `juju resolve` does not break the loop.
- **Impact**: on K8s operators where the Juju operator service account lacks the required
  network-related RBAC, the charm can never establish a TLS certificates relation, and the unit
  enters an error-resolve loop the operator cannot break.
- **Fix**: guard the `network.bind_address` access with a try/except on `ModelError` and fall
  back to an empty SAN list; the charm can still function with a self-signed cert that omits
  SANs.
- **Linter rule**: "calls `model.get_binding().network` without catching `ModelError`" —
  mechanically checkable with ops API analysis.

### 5. Machine charm shows `active` while the service is crash-looping

- **Severity**: high
- **Kind**: bug
- **Where**: `falco-operator/src/charm.py` — no `update_status` observer
- **Evidence**: on `concierge-lxd:rv-falco-lxd`:
  ```
  $ juju status falco
  falco  active  1  falco  0.42/edge  116  no

  $ juju ssh ubuntu/0 -- sudo systemctl is-active falco
  activating (auto-restart) (Result: exit-code)
  ```
  From `journalctl -u falco`:
  ```
  Opening 'syscall' source with modern BPF probe.
  An error occurred in an event source, forcing termination...
  ```
  `grep "update_status" src/charm.py` returns no results. `check_active()` is only called from
  hook handlers, not periodically.
- **Impact**: operators trust `juju status` to reflect reality. When Falco is crash-looping
  (e.g. no eBPF support, bad config), the charm still reports `active`.
- **Fix**: observe `self.on.update_status` with a handler that calls `check_active()` and sets
  `ErrorStatus` if the service is not running.
- **Linter rule**: "charm has a workload that can crash without detection and does not observe
  `update_status`" — mechanically checkable.

### 6. `update_status` never handled — open issue #12 unaddressed (both charms)

- **Severity**: medium
- **Kind**: test-gap / ux
- **Where**: `falcosidekick-k8s-operator/src/charm.py`, `falco-operator/src/charm.py`
- **Evidence**: `grep -n "update_status" src/charm.py` returns no results in either charm. Open
  issue #12 explicitly requests a periodic health-check mechanism. Live confirmation: Pebble
  health check `down` while charm is `active` (k8s); Falco `activating (auto-restart)` while
  `juju status` shows `active` (machine).
- **Impact**: if the workload crashes without Pebble detecting it, or relation data goes stale
  without a hook firing, the charm stays `active` indefinitely — `update_status` is the only
  periodic reconcile point available.
- **Fix**: add `update_status` handlers to both charms that verify workload health and set
  `WaitingStatus`/`ErrorStatus` when unhealthy.
- **Linter rule**: "charm has a workload that can crash without detection and does not observe
  `update_status`" — mechanically checkable.

### 7. TLS private key written world-readable

- **Severity**: medium
- **Kind**: bug
- **Where**: `falcosidekick-k8s-operator/src/certificates.py:157–167`
- **Evidence**: live deployment:
  ```
  $ stat -c "%a %n" /etc/falcosidekick/certs/server/server.key
  644 /etc/falcosidekick/certs/server/server.key
  ```
  The container runs as root (`uid=0`). The charm uses
  `container.push(path=KEY, source=str(key))` without explicit permissions or a subsequent
  `chmod`.
- **Impact**: world-readable private keys violate least privilege even inside a root-only
  container; if any non-root process escapes its sandbox the key is exposed. Security scanners
  (Trivy, Dockle) flag this.
- **Fix**: `container.exec(["chmod", "0600", str(KEY)])` after pushing the key, or set explicit
  `permissions=0o700` on the parent directory via `container.make_dir()`.
- **Linter rule**: "file written to container path containing 'key' with no matching `chmod`
  call in the same function" — mechanically checkable.

### 8. TLS certs temporarily absent after pod restart — Falcosidekick starts without TLS

- **Severity**: medium
- **Kind**: bug
- **Where**: `falcosidekick-k8s-operator/src/workload.py:196–237`,
  `falcosidekick-k8s-operator/src/certificates.py:58–68`
- **Evidence**: after `kubectl delete pod`, from live Pebble logs:
  ```
  21:09:45: open /etc/falcosidekick/certs/server/server.crt: no such file or directory
  21:09:53: cert files written (timestamped)
  21:10:13: service restarted after cert write
  ```
  `config_changed` fires → `reconcile()` → `tls_certificate_requirer.configure()` returns
  `False` (cert not ready) → config file written with a TLS section but no certs →
  Falcosidekick starts with missing certs → `certificates-relation-joined` fires separately →
  cert pushed → restart. The charm briefly shows `blocked "Workload failed to start"` before
  recovering.
- **Impact**: every pod restart causes a window with missing TLS certs; Falcosidekick logs TLS
  handshake errors for any clients connecting during that window.
- **Fix**: in `configure()`, check the return value of `tls_certificate_requirer.configure()`.
  If no cert was pushed and TLS is required, defer `replan()`/`restart()` until the cert is
  available.
- **Linter rule**: "calls `container.replan()`/`container.restart()` without checking required
  resources are present" — mechanically checkable.

### 9. Unit tests don't verify the health check port with TLS enabled

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `falcosidekick-k8s-operator/tests/unit/test_workload.py:159–206`
- **Evidence**: `test_configure_with_changes` sets `tls_relation=True, ingress_relation=False,
  falcosidekick_listenport=2801` and asserts `mock_container.add_layer.assert_called_once()` but
  never asserts the `port` argument passed to `_configure_healthchecks()` or the layer content.
  Finding 1 would not be caught by this test.
- **Fix**: assert the layer content and confirm the health check URL uses port 2810.
- **Linter rule**: not applicable (test gap).

### 10. Machine charm: no test for `check_active()` returning `False`

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `falco-operator/tests/unit/test_charm.py`
- **Evidence**: every test that calls `reconcile()` sets
  `mock_service.check_active.return_value = True` (lines 152, 174, 198, 296, 322). There is no
  test for `check_active()` returning `False`, though `reconcile()` raises
  `RuntimeError("Falco service is not running")` in that branch. This branch is untested, and
  the underlying scenario was observed live on the LXD deployment.
- **Fix**: add a test with `check_active.return_value = False` asserting the `RuntimeError`.
- **Linter rule**: not applicable (test gap).

### 11. Machine charm doesn't observe `general-info` relation events

- **Severity**: medium
- **Kind**: bug
- **Where**: `falco-operator/src/charm.py:73–77`
- **Evidence**: the charm observes `http-endpoint.relation_changed`/`relation_broken` but no
  `general-info` relation events:
  ```python
  self.framework.observe(
      self.on[HTTP_ENDPOINT_RELATION_NAME].relation_broken, self.reconcile
  )
  self.framework.observe(
      self.on[HTTP_ENDPOINT_RELATION_NAME].relation_changed, self.reconcile
  )
  ```
- **Impact**: `general-info` (`scope: container`) auto-establishes with the principal, so
  currently this is dead code; but if machine-level metadata changes, nothing reconciles.
- **Fix**: `self.framework.observe(self.on["general-info"].relation_changed, self.reconcile)`.
- **Linter rule**: "subordinate charm observes principal relation but doesn't observe its
  events" — mechanically checkable.

### 12. `logging` relation wires Pebble log forwarding, not reconcile — undocumented split

- **Severity**: low
- **Kind**: bug
- **Where**: `falcosidekick-k8s-operator/src/charm.py:84`
- **Evidence**: `self.logging_forwarder = LogForwarder(self, relation_name=LOGGING_RELATION_NAME)`
  is instantiated but, unlike `loki_push_api_consumer`, is not connected to `reconcile()`.
  `LogForwarder` wires its own framework observers independently
  (`lib/charms/loki_k8s/v1/loki_push_api.py:2385`), so `logging` relation events are handled —
  they just never trigger `reconcile()`, so the Falcosidekick YAML config is not re-rendered
  when a `logging` Loki relation changes. `charmcraft.yaml` declares
  `logging: interface: loki_push_api, limit: 1`. If both `send-loki-logs` and `logging` Loki
  relations exist, the YAML config only reflects `send-loki-logs`, while `LogForwarder` handles
  Pebble log forwarding for `logging` separately.
- **Impact**: a user relating a Loki provider to `logging` instead of `send-loki-logs` gets
  Pebble log forwarding but no Falcosidekick YAML config update — functional but undocumented.
- **Fix**: observe the `LogForwarder`'s relevant event in `reconcile()`, or document clearly
  that `logging` provides only Pebble log forwarding.
- **Linter rule**: not mechanically checkable.

### 13. Neither charm defines an `on.remove` handler

- **Severity**: low
- **Kind**: bug / ux
- **Where**: `falcosidekick-k8s-operator/src/charm.py`, `falco-operator/src/charm.py`
- **Evidence**: `grep "remove" src/charm.py` returns no results in either charm. The machine
  charm defines `_on_remove()` and `falco_service.remove()` but never observes
  `self.on.remove`. On `juju remove-application falco` (LXD), Juju's generic teardown stops the
  service (`systemctl is-active` → `inactive`), but the charm's own `remove()` cleanup (git
  clone dirs, SSH keys) is never invoked.
- **Fix**: add `self.framework.observe(self.on.remove, self._on_remove)` to both charms.
- **Linter rule**: "charm defines a `remove()` method on a managed service but has no `on.remove`
  observer" — mechanically checkable.

### 14. `general-info` relation is declared but never read

- **Severity**: low
- **Kind**: bug / design
- **Where**: `falco-operator/charmcraft.yaml:108–110`, `falco-operator/src/charm.py`
- **Evidence**: `general-info` is declared with `scope: container` but never read; the
  `http_endpoint_requirer` is the actual data source. `grep -n "general" src/service.py` returns
  no results.
- **Fix**: remove the relation, or wire it up to trigger reconcile even if unused, to document
  intent.
- **Linter rule**: "charm declares a relation interface that is never read or acted on" —
  mechanically checkable.

### 15. `Falcosidekick.restart` restarts all container services, not just its own

- **Severity**: low
- **Kind**: bug
- **Where**: `falcosidekick-k8s-operator/src/workload.py:239–241`
- **Evidence**:
  ```python
  for service_name in self.container.get_services():
      self.container.restart(service_name)
  ```
  The loop restarts everything returned by `container.get_services()`, not just
  `falcosidekick`. Harmless today since the rock defines only that one service, but fragile if
  the rock ever adds another.
- **Fix**: `self.container.restart(Falcosidekick.service_name)`.
- **Linter rule**: "calls `container.restart()` in a loop over `get_services()` without
  filtering" — mechanically checkable.

### 16. `no_reload_on_change` is always `False` — reload never attempted

- **Severity**: low
- **Kind**: bug / performance
- **Where**: `falcosidekick-k8s-operator/src/workload.py:58–65`
- **Evidence**: `Template.install()` always does a full restart when content changes; it never
  sends a reload signal (e.g. SIGHUP) to the running process.
- **Fix**: implement `container.exec(["kill", "-HUP", pid])` as an alternative to restart when
  `reload=True`.
- **Linter rule**: not mechanically checkable.

### 17. Config validation error messages lose specificity

- **Severity**: low
- **Kind**: ux / bug
- **Where**: `falcosidekick-k8s-operator/src/state.py:77–81`, `config.py:40–41`
- **Evidence**: the pydantic validator raises
  `ValueError(f"Port number {value} is out of valid range [1-65535].")`, but this is caught and
  re-raised as `InvalidCharmConfigError("port")`. The operator only sees
  `"Invalid charm configuration: port"` — no range, no offending value.
- **Fix**: `raise InvalidCharmConfigError(f"Invalid charm configuration: {error_field_str}: {e}")`.
- **Linter rule**: not mechanically checkable.

### 18. `logging_forwarder` uses deprecated `JujuVersion.from_environ()` in vendored charm libs

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/loki_k8s/v1/loki_push_api.py:2251`,
  `lib/charms/tls_certificates/_tls_certificates.py:1754`
- **Evidence**:
  ```python
  juju_version = JujuVersion.from_environ()  # deprecated
  ```
  and a `DeprecationWarning: JujuVersion.from_environ() is deprecated, use
  self.model.juju_version instead`.
- **Impact**: the vendored lib will break silently when the deprecated API is removed.
- **Fix**: run `charmcraft update-lib` and pick up an upstream fix.
- **Linter rule**: "charm library uses deprecated `JujuVersion.from_environ()`" — mechanically
  checkable with grep.

### 19. k8s charm has no explicit `upgrade_charm` handler

- **Severity**: low
- **Kind**: design
- **Where**: `falcosidekick-k8s-operator/src/charm.py`
- **Evidence**: `grep "upgrade_charm" src/charm.py` returns no results. `config_changed` fires
  on `juju refresh` and calls `reconcile()`, which works but relies on undocumented assumptions
  about hook ordering.
- **Fix**: add an explicit `upgrade_charm` handler that calls `reconcile()`.
- **Linter rule**: not mechanically checkable.

### 20. Documented actions don't exist

- **Severity**: low
- **Kind**: docs / bug
- **Where**: `falco-operator/docs/reference/actions.md`
- **Evidence**: the docs describe `flush-falco-logs` and `reload-falco` actions;
  `juju actions falco` returns "No actions defined for falco."
- **Impact**: documentation describes functionality that doesn't exist; an operator following
  the docs finds nothing to run.
- **Fix**: implement the actions or remove the docs.
- **Linter rule**: "charm documentation lists actions not present in `charmcraft.yaml`" —
  mechanically checkable.

### 21. k8s charm does not observe `secret_changed`

- **Severity**: low
- **Kind**: design
- **Where**: `falcosidekick-k8s-operator/src/charm.py`
- **Evidence**: `grep "secret_changed" src/charm.py` returns no results. The machine charm
  observes `secret_changed` and reconciles; the k8s charm does not. Not currently triggered
  since the charm doesn't use Juju secrets.
- **Fix**: add `self.framework.observe(self.on.secret_changed, self.reconcile)` if secrets are
  ever used.
- **Linter rule**: not mechanically checkable (charm doesn't currently use secrets).

### 22. Class attribute typo: `sevice_name`

- **Severity**: nit
- **Kind**: lint
- **Where**: `falcosidekick-k8s-operator/src/workload.py:108`
- **Evidence**: `sevice_name: str = "falcosidekick"` — never referenced anywhere in the codebase.
- **Fix**: rename to `service_name`.
- **Linter rule**: not mechanically checkable without a dictionary lookup.

## Worth copying

- **Lazy-cached state property**: `state` returns a cached `_state`, recomputed from
  `CharmState.from_charm()` on first access. Clean and idiomatic. (`state.py:49`)
- **Idempotent template rendering**: `Template.install()` compares old/new content byte-for-byte
  before pushing, returning `False` when unchanged to avoid unnecessary restarts.
  (`workload.py:53–65`)
- **Status precedence with explicit exceptions**: each reconcile error maps to a specific,
  actionable `BlockedStatus` message. (`charm.py:140–156`)
- **Combined health check + restart policy**: `rockcraft.yaml` defines
  `on-check-failure: health: restart`, so Pebble handles crash-loop protection without charm
  code. (`falcosidekick-k8s-operator/rock/rockcraft.yaml:18`)
- **XOR constraint on ingress/TLS**: enforced at `CharmState.from_charm()` creation time with a
  clear error message, covered by unit tests for all 8 combinations. (`state.py:79–81`)
- **Comprehensive unit test coverage**: 53 tests for falcosidekick-k8s, 56 for falco-operator,
  all passing, using `ops.testing` scenario testing extensively.
- **`CharmBaseWithState` ABC pattern**: a shared abstract base enforcing the `state` property and
  `reconcile()` method across both charms — a clean pattern worth promoting. (`state.py:109–123`)
- **Pydantic for state models**: `CharmState`/`CharmConfig` use pydantic for config validation.
- **Machine charm `check_active()`**: calls `systemd.service_running()` to verify the service
  before setting `ActiveStatus` — the right approach, the problem is it only runs during hooks.
  (`service.py:353–355`)

## Common-practice notes

- **`src/` layout**: both charms follow `src/charm.py` + `src/state.py` + `src/workload.py`.
- **`lib/charms/` vendoring**: grafana_dashboard, loki_push_api, prometheus_scrape,
  traefikingress, tls_certificates vendored under `lib/charms/`, standard practice.
- **No `StoredState`**: all state is derived from config/relations, avoiding a common bug source.
- **`upgrade_charm` handling**: falco-operator handles it properly (calls `install()` again);
  falcosidekick-k8s does not (see Finding 19).
- **Machine charm uses `systemd` library** (`charmlibs.systemd`) for standard service management.
- **`systemd.daemon_reload()`/`service_restart()` on every configure**: correct for idempotency
  but slightly wasteful.
- **`start` hook not observed in machine charm**: relies on Juju's hook ordering (`config-changed`
  after `start`) to trigger the initial reconcile — works in practice but is implicit.
- **Rock-based k8s charm**: the falcosidekick container runs from a rock image; the Juju agent
  downloads the charm code separately — correct pattern for k8s charms.

## Tests

Both suites pass in CI (53 for falcosidekick-k8s, 56 for falco). Locally, tests require
installing the charm to pick up vendored interfaces/deps:
```bash
uv pip install -e falcosidekick-k8s-operator/ --python .venv/bin/python
uv pip install -e falco-operator/ --python .venv/bin/python
```
Result: **53 passed** (k8s), **56 passed** (machine).

**Warnings** (both suites): `JujuVersion.from_environ() is deprecated`
(`loki_push_api.py:2251`, `tls_certificates.py:1754`); `generate_private_key() is deprecated`
(`tls_certificates.py:1323`).

**Coverage gaps relative to risks found**:
- No test asserts the health check port with TLS enabled (Finding 1/9).
- No test for the `logging` relation / `LogForwarder` reconcile gap (Finding 12).
- No test for `secret_changed` in the k8s charm (Finding 21).
- No test reproducing the `network-get` failure (Finding 4).
- No integration test for `metrics-endpoint` with TLS enabled after redeploy (Finding 2).
- No test for either charm's `on.remove` path (Finding 13).
- No test for transient TLS cert loss on pod restart (Finding 8).
- No test for `check_active()` returning `False` in the machine charm (Finding 10).
- No test for the idempotency-guard interaction that skips `update_scrape_job_spec` (Finding 2).

**Linting**: `ruff check src/` and `ruff format --check` pass cleanly on both charms; `codespell`
finds no issues.

## Docs

- **README**: brief, links to RTD, no inline deployment instructions.
- **RTD docs**: structured with Diátaxis (tutorial/how-to/reference/explanation); good coverage.
  `docs/how-to/troubleshoot.md` exists; `docs/how-to/configure-tls-ingress.md` explains the
  mutual exclusivity of TLS and ingress.
- **Charmcraft descriptions match reality**: falcosidekick-k8s describes the Loki/metrics/Grafana
  integration; falco describes itself as a machine subordinate.
- **Doc/reality mismatch**: `docs/how-to/integrate-with-cos.md` shows a `grafana-agent-k8s`
  integration requiring `trust: true` — confirmed necessary in this deployment — but overstates
  COS integration quality since the grafana-dashboard relation is non-functional (Finding 3).
- **`CONTRIBUTING.md`** in each charm dir is thin; the root-level one is more complete.
- **No documentation of the missing `update_status`** limitation — open issue #12 is the only
  record.
- **`docs/reference/actions.md`** for falco-operator lists actions that don't exist
  (Finding 20).
- **README for machine charm**: very brief (777 bytes), only useful as a pointer to RTD.

## Open questions

1. **Health check port bug**: the fix is clear — always use port 2810 for health check and
   metrics scrape. The charm should document that Prometheus scrapes 2810 even when TLS is
   configured on 2801.
2. **`logging` relation**: functional but undocumented split between Pebble log forwarding and
   YAML config output — should this be documented or wired into reconcile?
3. **TLS certificate SANs on k8s**: requesting SANs via `network-get` fails under some K8s RBAC
   configurations. Should the charm fall back gracefully, or should this be a documented
   requirement?
4. **Upgrade charm path (k8s)**: acceptable today for a rock-based charm, but an explicit handler
   would be safer and more testable.
5. **`general-info` relation in machine charm**: declared but unused — remove, or wire up for
   future-proofing?
6. **Machine charm in LXD**: Falco needs kernel eBPF, which LXD containers typically lack. This
   is partly an environment constraint and partly the `update_status` gap.
7. **Transient TLS cert loss on pod restart**: should the charm defer starting/restarting
   Falcosidekick until certs are available, rather than starting without TLS and recovering
   later?
8. **`update_scrape_job_spec` idempotency fix**: moving the calls before the early-return means
   they run on every reconcile even when nothing changed; the provider itself should probably add
   its own idempotency check.
9. **Grafana dashboard empty**: the fix (calling `_update_all_dashboards_from_dir()` on every
   reconcile) needs to be checked against `relation_joined` timing for `metrics-endpoint`, which
   has an analogous gap (Finding 3).
</content>
