# parca-agent-operator

A machine subordinate charm that installs and manages the Parca Agent eBPF continuous-profiling snap on a principal machine. The code is clean and well-separated (workload logic vs. charm logic), but the charm has a systemic reconciliation gap: it observes only `install`, `upgrade_charm`, `start`, `remove`, and `collect_unit_status`, and relies on `config-changed` to pick up relation changes that Juju does not actually route through `config-changed`. As a result, store-address changes/removals and certificate rotations are silently ignored, and `juju refresh` stops the snap service without restarting it. The pinned snap revision also carries a known upstream memory leak. A maintainer should first add the missing relation-event observers (`parca_store` endpoints/removal, `receive-ca-cert` updates/removal) and make `_on_upgrade_charm` restart the service, then bump the pinned snap revision past the leak fix.

| | |
|---|---|
| Repo | canonical/parca-agent-operator @ e4e7602 (2026-07-01) |
| Charms | parca-agent |
| Substrate | machine (LXD) |
| Deployed | yes — concierge-lxd-4 (Juju 4.0.12) and concierge-lxd (Juju 3.6.27); parca-agent 0.35/stable rev 124, later refreshed to 0.35/candidate rev 140; parca-agent snap v0.35.3 rev 2587 |
| Reviewed | 2026-08-21 |

## What it does

Parca Agent is a subordinate charm (requires `juju-info`) that installs and manages the `parca-agent` snap in classic confinement, on amd64 Ubuntu 22.04/24.04. It sends profiles to a Parca store via the `parca_store` relation, can trust CA certificates via `receive-ca-cert`, and exposes Prometheus metrics/OTLP traces via `cos-agent`. Workload version comes from `git describe --always` baked in at build time. No config options, no actions — all behaviour is relation-driven.

## Deployment log

### Setup — Juju 4.x (concierge-lxd-4)
```
juju add-model rv-parca-lxd localhost -c concierge-lxd-4
juju deploy ubuntu-lite --base ubuntu@22.04        # principal machine
juju deploy parca-agent --base ubuntu@22.04 --channel 0.35/stable
juju integrate ubuntu-lite parca-agent
```
Machine provisioning took ~3 minutes. Subordinate came up `blocked` (expected: no store configured).

### Setup — Juju 3.6 (concierge-lxd)
Same sequence on a separate controller/model (`rv-parca-lxd3`). Hook ordering, timing, and status sequence were identical to Juju 4.x.

### Verification (Juju 4.x)
- `juju status`: parca-agent `blocked` with correct message, port 7071/tcp open, workload version `HEAD-7375d8db`
- `snap list parca-agent`: `v0.35.3 rev 2587 classic,held` — held forever, won't auto-refresh
- `snap services parca-agent`: `parca-agent-svc enabled active`
- `snap logs parca-agent`: repeated crash: `"Failed to load eBPF tracer: failed to read kernel symbols: all addresses from kallsyms are zero"` — expected in LXD containers, systemd keeps restarting the service
- Removing the `juju-info` relation destroyed the subordinate unit cleanly (`juju-info-relation-departed`); re-integrating created a fresh unit (`parca-agent/1`), blocked again

### Certificate integration test
```
juju integrate parca-agent:receive-ca-cert self-signed-certificates:send-ca-cert
```
- `receive-ca-cert-relation-created` fired; `config-changed` did **not** follow (confirmed from debug-log)
- `/usr/local/share/ca-certificates/receive-ca-cert-parca-agent-ca.crt` was never created

### Failure injection — workload kill
```
sudo killall -9 parca-agent
```
- Service restarted within 3 seconds; no Juju hook fired; `juju status` unchanged (`blocked`); no operator notification

### cos-agent + grafana-agent integration
```
juju deploy grafana-agent --base ubuntu@22.04 --channel stable
juju integrate parca-agent:cos-agent grafana-agent:cos-agent
```
- `cos-agent` relation formed; grafana-agent auto-created subordinates under ubuntu-lite
- grafana-agent went `blocked`: *"Missing ['grafana-cloud-config']|['grafana-dashboards-provider']|['logging-consumer']|['send-remote-write']|['tracing...'"*
- Confirmed `COSAgentProvider` writes relation data on `relation_joined`/`relation_changed`; `localhost:7071/metrics` is exposed to grafana-agent, but metrics are stranded without a downstream sink

### parca-k8s store integration test
```
juju deploy parca-k8s --base ubuntu@22.04 --channel 1/stable
juju integrate parca-k8s:parca-store-endpoint parca-agent:parca-store-endpoint
```
- parca-k8s wrote `remote-store-address: juju-10be7a-2.lxd:7993` to relation data; parca-agent snap config picked it up and went `active`
- `parca-store-endpoint-relation-created` fired; `config-changed` did **not** follow it (same pattern as the CA-cert relation)

### Store relation removal test
```
juju remove-relation parca-agent parca-k8s
```
- `parca-store-endpoint-relation-broken` fired at 05:00:04; `config-changed` did not follow; `reconcile()` was not called
- parca-agent stayed `active` for ~9 seconds until `update_status` ran, then went `blocked`
- **Snap config still had the stale address** `remote-store-address: juju-10be7a-2.lxd:7993`; journal showed `"Failed to setup gRPC connection (try 2 of 5): connection refused"` — profiles silently sent to a dead endpoint with no operator notification

### Certificate rotation test
```
juju integrate parca-agent:receive-ca-cert self-signed-certificates:send-ca-cert
```
- `receive-ca-cert-relation-joined` at 05:00:52, `relation-changed` at 05:00:53 (self-signed-certificates wrote certs); `config-changed` did not follow
- `/usr/local/share/ca-certificates/receive-ca-cert-parca-agent-ca.crt` did not exist afterward — the charm never observes `certificate_set_updated`, and even if it did, `_reconcile_certs()` is gated behind `_store_config` being non-empty

### juju refresh to 0.35/candidate (rev 140)
```
juju refresh parca-agent --channel 0.35/candidate
```
- `upgrade-charm` fired at 17:02:07, `config-changed` followed at 17:02:09 (expected for a charm refresh, but the charm doesn't observe `config-changed`)
- Snap stayed at rev 2587 (`_snap_revisions` unchanged in new charm code)
- Snap service went `inactive` at 17:02:07 as part of the refresh and was never restarted; status became `blocked: The parca-agent snap is not running`, detected only at the next `update_status` (17:06:21)
- CA cert file still did not exist after the refresh

### Store relation re-formation
- `parca-store-endpoint-relation-created/changed/joined` fired; `config-changed` did not follow
- Status moved from `blocked: No store` to `blocked: snap not running` (store config non-empty, but snap service dead)
- Snap config still carried the stale pre-removal address

### Scale-up / scale-down tests
- Adding a unit to `ubuntu-lite` auto-created `parca-agent/1` and `grafana-agent/1`; both converged to `blocked`
- Removing the principal unit destroyed both subordinates cleanly along with the machine

### juju refresh — bad edge-channel revision
```
juju refresh parca-agent --channel 0.35/edge
```
- rev 140 on `0.35/edge` has a malformed charmhub archive; both units errored: *"download request with archiveSha256 length 0 not valid"* and went into `failed` agent state
- Units self-recovered ~30 seconds after refreshing back to `0.35/stable`
- Charmhub infrastructure issue, not a code bug, but it demonstrates a bad revision can put subordinate units into a retry loop

### Application removal
- `juju remove-application parca-agent` destroyed the unit cleanly, removed port 7071/tcp, no errors

### Linting / tests
```
uv run ruff check src/    # 2 E501 (line too long) at charm.py:140, :151 — silenced by pyproject.toml
uv run pyright src/       # 0 errors, 0 warnings
PYTHONPATH=src:lib:. uv run --extra dev pytest tests/unit   # 22 passed
```
The lock file pins `ops==3.7.1`, which lacks `ops.testing.Context`; tests only pass with `--extra dev`.

## Observed behaviour

- **Install timing**: install hook runs ~48s after machine provisioning starts (snap download + install + hold).
- **Snap "active" while crash-looping**: `parca-agent-svc` reports `active` in snap terms even while it restarts every ~10s from the eBPF failure in LXD; the charm's `running` property is a systemd-state check, not a functional check, so this does not trigger `blocked`.
- **Port opened unconditionally**: 7071/tcp is opened on the `start` hook regardless of workload health.
- **Version string**: `HEAD-7375d8db` — a git-describe string, not a real semver.
- **Subordinate lifecycle**: clean create/destroy tracking principal scale, on both Juju 4.x and 3.6.27; behaviour was identical across both Juju versions.
- **`config-changed` does not follow relation lifecycle events**: confirmed for `receive-ca-cert-relation-created`, `receive-ca-cert-relation-changed`, `parca-store-endpoint-relation-created`, and `parca-store-endpoint-relation-broken`. The charm relies entirely on `config-changed` for reconciliation, so none of these trigger `reconcile()`.
- **Default store address active**: the parca-agent snap defaults to `grpc.polarsignals.com:443` on every service start (snap hook `configure` runs `snapctl set remote-store-address=...`); journal showed `"report sent successfully"` to Polarsignals cloud even without a store relation configured.
- **`upgrade-charm` → `config-changed` ordering confirmed**: debug log shows `upgrade-charm` at 17:02:07, `config-changed` at 17:02:09; the charm does not observe `config-changed`, so nothing runs from it.
- **`relation_departed` fires before `relation_broken`**: exercised during store-relation removal; the library's `remove_store` event path fires but the charm never observes it.
- **`update_status` interval is the only recovery path**: hooks observed roughly every 5 minutes (05:01:26, 05:06:21, 05:09:56); this is the sole mechanism that eventually detects a stopped service or stale config.
- **HTTP endpoint unreachable even when snap reports "active"**: after manually starting the service, `snap services` showed `active`, but `curl localhost:7071/metrics` returned connection refused and `ss -tlnp | grep 7071` showed nothing listening — the health check is process-based, not HTTP-based.
- **No actions, no config options**: `juju actions parca-agent` and `juju config parca-agent` both return empty, appropriate for a relation-driven subordinate.

## Findings

### `juju refresh` stops the snap service and never restarts it (Critical)

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/parca_agent.py:123–136` (`install()`), `src/charm.py:96–103` (`_on_upgrade_charm`)
- **Evidence**: `install()` calls `self._snap.ensure(state=SnapState.Present, revision=target_rev, classic=True)` unconditionally, then `hold()`. `ensure()` always stops and reinstalls the snap, even at the same revision, and `_on_upgrade_charm` never calls `start()` afterward. `_reconcile()` is invoked in `_on_upgrade_charm` but only restarts the service if config changed — it hadn't. Observed on the deployed unit: after `juju refresh parca-agent --channel 0.35/candidate`, `snap services parca-agent` → `inactive` at 17:02:07, with the snap still at the correct revision (2587). Status went to `blocked: The parca-agent snap is not running`, only detected at the next `update_status` (17:06:21). Hook trace: `upgrade-charm` (17:02:07) → `config-changed` (17:02:09, not observed by the charm) → `update-status` (17:06:21, detects the stopped service).
- **Impact**: every `juju refresh` — whether or not it changes the snap revision — stops profiling silently until the next `update_status` cycle (up to 5 minutes), with no indication that the refresh caused it.
- **Fix**: call `self.parca_agent.start()` at the end of `_on_upgrade_charm`, and/or make `install()` a no-op when the snap is already at the target revision.
- **Linter rule**: not mechanically checkable without modeling snap lifecycle semantics.

### `install()` is not idempotent for the same-revision case (High)

- **Severity**: high
- **Kind**: bug / performance
- **Where**: `src/parca_agent.py:123–136`
- **Evidence**:
  ```python
  def install(self):
      try:
          self._snap.ensure(
              state=snap.SnapState.Present, revision=self.target_revision, classic=True
          )
      except snap.SnapError as e:
          raise e
      self._snap.hold()
  ```
  `ensure(state=Present, revision=X)` is unconditional; snapd removes and reinstalls the snap even when already at `X`, stopping the service with no corresponding start. This is the underlying mechanism behind the `juju refresh` bug above.
- **Impact**: any code path that calls `install()` at the current revision (e.g. `refresh()` when `_snap_revisions` hasn't changed) stops the service with no automatic restart.
- **Fix**:
  ```python
  if self._snap.present and self._snap.revision == self.target_revision:
      self._snap.hold()
      return
  self._snap.ensure(state=snap.SnapState.Present, revision=self.target_revision, classic=True)
  self._snap.hold()
  ```
- **Linter rule**: not mechanically checkable without modeling snap lifecycle semantics.

### `parca_store` relation events are never observed — store changes and removals are silently missed (Critical)

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:57–62`
- **Evidence**: The charm only observes `install`, `upgrade_charm`, `start`, `remove`, `collect_unit_status`. `ParcaStoreEndpointRequirer` fires `endpoints_changed` (on `relation_changed`) and `remove_store` (on `relation_departed`) — `lib/charms/parca_k8s/v0/parca_store.py:238–296` — but the charm registers no observer for either. `_store_config` is read once in `__init__` from `self._store_requirer.config` and never refreshed by an event handler. Confirmed live: `parca-store-endpoint-relation-created`, `-changed`, `-broken` all fired without a following `config-changed`, and `reconcile()` was not called in any of those cases.
- **Impact**: when a Parca store's address or token changes (DNS migration, token rotation, failover), or a provider unit departs, the agent keeps sending profiles to the stale address with no error signal. See the two deployment findings below for the concrete on-disk consequence.
- **Fix**: add `self.framework.observe(self._store_requirer.on.endpoints_changed, self._on_store_endpoints_changed)` and `self.framework.observe(self._store_requirer.on.remove_store, self._on_store_removed)`, both calling `self._reconcile()`.
- **Linter rule**: "charm uses a library that emits events but registers no observers for those events" — mechanically checkable by comparing `framework.observe` calls against the library's `on` attribute.

### Store relation removal leaves a stale snap config — profiles sent to a dead address (Critical)

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:57–62` (missing observer), `src/parca_agent.py:58–62` (reconcile gate)
- **Evidence**: `juju remove-relation parca-agent parca-k8s` fired `parca-store-endpoint-relation-broken` at 05:00:04; `config-changed` did not follow; `reconcile()` was not called. `snap get parca-agent remote-store-address` still showed `juju-10be7a-2.lxd:7993` (the removed provider's address). The journal showed repeated `"Failed to setup gRPC connection (try 2 of 5): connection refused"`. Status stayed `active` for ~9 seconds until `update_status` fired and `collect_unit_status` detected an empty `_store_config`.
- **Impact**: profiles are silently lost for the gap between relation removal and the next `update_status` (observed ~9s here, up to 5 minutes in general), with no error surfaced to the operator. The same gap applies to mid-flight address changes.
- **Fix**: same observers as above; when the store is removed, `reconcile()` should clear `remote-store-address` from the snap config.
- **Linter rule**: "charm uses a library that emits events but registers no observers for those events" — mechanically checkable.

### parca-agent snap is pinned to a version with a known memory leak (Critical)

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/parca_agent.py:47`
- **Evidence**:
  ```python
  _snap_revisions: Dict[Tuple[str, str], int] = {
      ("classic", "amd64"): 2587,  # v0.35.3
  }
  ```
  `install()` calls `ensure(..., revision=self.target_revision, classic=True)` then `hold()`, permanently pinning the snap to rev 2587. Upstream issue #114 (open) states the pinned v0.35.3 has memory leaks fixed in v0.39.2; upstream is currently at v0.48.0. Deployed unit confirms `snap info parca-agent` → `installed: v0.35.3 (2587) hold: forever`.
- **Impact**: every user of this charm runs a version roughly 13 minor releases behind with a known, confirmed memory leak, and the charm actively prevents upgrades via `snap.hold()`. Under sustained profiling load the agent leaks memory until OOM.
- **Fix**: bump `_snap_revisions[("classic", "amd64")]` to a revision at/after v0.39.2, or drop `hold()` and allow the snap to track a channel.
- **Linter rule**: not mechanically checkable — requires knowledge of upstream release notes.

### Certificate rotation is never observed, and application is gated behind an unrelated store check (High)

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:52`, `src/charm.py:57–62`, `src/parca_agent.py:58–62`
- **Evidence**: `get_all_certificates()` is called once, in `__init__`, before any relation hooks fire (returns `set()` at that point) and is stored in `ParcaAgent._certificates`, never refreshed. `CertificateTransferRequires` fires `certificate_set_updated` (on `relation_changed`) and `certificates_removed` (on `relation_broken`) — `lib/charms/certificate_transfer_interface/v1/certificate_transfer.py:488–494, 548–562` — but the charm observes neither. Even when `reconcile()` does run, `_reconcile_certs()` is only called `if self._store_config:`, so certificates are ignored whenever no store relation is active. Confirmed live: relating `self-signed-certificates:send-ca-cert` fired `receive-ca-cert-relation-joined`/`-changed` with no following `config-changed`, and `/usr/local/share/ca-certificates/receive-ca-cert-parca-agent-ca.crt` was never created — both with and without an active store relation.
- **Impact**: TLS certificate rotation silently fails; the charm keeps trusting an old or absent CA indefinitely, and any downstream system that rotates its certificate breaks the connection without warning.
- **Fix**: observe `self._cert_transfer.on.certificate_set_updated` and `.on.certificates_removed`, calling `self._reconcile()`; and make `_reconcile()` always call `_reconcile_certs()` regardless of store configuration.
- **Linter rule**: "charm registers a library that emits events but observes none of them" — mechanically checkable by static analysis of `framework.observe` calls vs. the library's `on` attribute.

### Snap defaults to the external Polarsignals cloud endpoint when no store is configured (High, unverified body)

- **Severity**: high
- **Kind**: bug / privacy
- **Where**: parca-agent snap default configuration (`snap/parca-agent/2587/meta/hooks/configure`, per notes; not charm code)
- **Evidence**: the snap's `configure` hook runs `snapctl set remote-store-address="grpc.polarsignals.com:443"` on every service start. The charm never overrides this when no `parca_store` relation exists. Journal on the deployed unit showed `"report sent successfully"` to the Polarsignals address while no store relation was configured.
- **Impact**: in air-gapped or privacy-sensitive environments, an operator deploying this charm without a store relation may unknowingly send profiling data to an external cloud endpoint.
- **Fix**: have the charm explicitly clear/override `remote-store-address` when no store relation is present, rather than leaving the snap's shipped default in place.
- **Linter rule**: not established.

### eBPF crash loop invisible to the operator — service reports "active" while repeatedly crashing (Medium)

- **Severity**: medium
- **Kind**: ux
- **Where**: `src/parca_agent.py:171–179` (`running` property)
- **Evidence**: `running` checks `services["parca-agent-svc"]["active"]` — a systemd-state check. In LXD containers the snap crashes with `"Failed to load eBPF tracer: failed to read kernel symbols"` (exit code 2); systemd restarts it roughly every second (`journalctl` showed a restart counter over 100). `snap services parca-agent` still reports `active`; `curl localhost:7071/metrics` returns connection refused.
- **Impact**: if a store were configured while in this state, the charm would report `Active` while the workload is crash-looping and serving nothing, with no indication to the operator short of reading the systemd journal.
- **Fix**: check service health more robustly — probe `localhost:7071/metrics` in `_on_collect_unit_status` and report `BlockedStatus` if unreachable, or detect repeated restarts across `update_status` invocations.
- **Linter rule**: not mechanically checkable.

### Snap service reports "active" while the HTTP endpoint is unreachable — health check is process-based, not HTTP-based (Medium)

- **Severity**: medium
- **Kind**: ux / bug
- **Where**: `src/parca_agent.py:164–171`
- **Evidence**: after manually starting the service, `snap services` showed `active`, but `curl localhost:7071/metrics` returned connection refused and `ss -tlnp | grep 7071` showed nothing listening. `running` only checks the snap-service state, not whether the HTTP server actually came up.
- **Impact**: operators or monitoring probes relying on Juju's Active status as a health signal will be misled; `collect_unit_status` would report `Active` while metrics are unreachable.
- **Fix**: add an HTTP health check (e.g. `curl -f --connect-timeout 2 localhost:7071/metrics`) to `collect_unit_status` and escalate to `BlockedStatus` on failure.
- **Linter rule**: not mechanically checkable without modeling workload health semantics.

### Unit tests verify internal state but not side effects — `reconcile()` calls unverified (Medium)

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm/test_charm.py:127–151, 202`
- **Evidence**: `test_parca_external_store_relation_join` asserts `charm.parca_agent._store_config == store_config` but never checks that `reconcile()` was called or that the snap config was actually applied (`_store_config` is set in `__init__`, not by `reconcile()`). `test_parca_external_store_relation_removed` fires `relation_broken`, not `relation_departed`, so the `remove_store` path is never exercised. `test_parca_receive_ca_cert` fires `relation_changed` on the *store* relation rather than the CA-cert relation, so the CA-file assertion passes through the wrong code path. `test_update_status_refreshes_snap_hold` only checks that `hold()` is called, not that a changed revision triggers an actual refresh.
- **Impact**: the test suite gives false confidence — it can pass even though the reconciliation bugs above (missing observers, stale config, silent CA ignoring) are present, because it never checks external side effects.
- **Fix**: assert on `reconcile()` invocation and its downstream effects (snap config written, service restarted, CA file present) for each relevant event, and fire the actual events the library emits (`relation_departed`, the CA-cert relation's `relation_changed`).
- **Linter rule**: not mechanically checkable — requires test-quality review.

### `receive-ca-cert` relation without a store relation: CA file is never written (High)

- **Severity**: high
- **Kind**: bug
- **Where**: `src/parca_agent.py:58–62`
- **Evidence**:
  ```python
  def reconcile(self):
      if self._store_config:
          self._reconcile_certs()
          self._reconcile_config()
      else:
          logger.error("no store configured: cannot reconcile parca_agent")
  ```
  When `receive-ca-cert` is related without `parca_store`, `reconcile()` logs an error and returns without calling `_reconcile_certs()`. Confirmed on the deployed unit: relating `self-signed-certificates:send-ca-cert` without a store relation left `/usr/local/share/ca-certificates/receive-ca-cert-parca-agent-ca.crt` absent even after `upgrade-charm` triggered `config-changed`, because `_store_config` was still empty at that point.
- **Impact**: TLS certificates from a `receive-ca-cert` provider are silently ignored unless a `parca_store` relation is simultaneously active — an operator may believe the CA is configured when it is not.
- **Fix**: always call `_reconcile_certs()` regardless of store configuration, or add explicit certificate-relation observers independent of the store gate.
- **Linter rule**: "side effect (CA file write) gated behind an unrelated precondition (store config exists)" — not mechanically checkable.

### `_snap` property creates a new SnapCache on every access (Medium)

- **Severity**: medium
- **Kind**: performance
- **Where**: `src/parca_agent.py:184`
- **Evidence**:
  ```python
  @property
  def _snap(self):
      cache = snap.SnapCache()
      return cache["parca-agent"]
  ```
  `SnapCache.__init__` makes HTTP calls to the local snapd socket on every construction. `_snap` is accessed repeatedly within a single `reconcile()` (in `_reconcile_config`, `restart()`, and possibly `_reconcile_certs`), and again in `running`, `installed`, `revision`, `version`, `hold()`, `ensure()`.
- **Impact**: redundant HTTP round-trips to snapd on every hook; on a busy system this adds latency and load.
- **Fix**: cache the reference once, e.g. `self._snap = snap.SnapCache()["parca-agent"]`, and reuse it.
- **Linter rule**: "property with side effects (network I/O) used repeatedly without caching" — not mechanically checkable without modeling `SnapCache` semantics.

### `operator_libs_linux.v1.snap` needs v2 migration (Medium)

- **Severity**: medium
- **Kind**: maintenance
- **Where**: `lib/charms/operator_libs_linux/v1/snap.py` (LIBAPI=1, LIBPATCH=12)
- **Evidence**: upstream issues #110 and #41 (both open) flag that v2 of the library is available with breaking changes, and Renovate has been blocked from updating it automatically.
- **Impact**: the charm misses whatever API changes, performance improvements, or bug fixes v2 carries, and dependency updates stay blocked.
- **Fix**: review the v2 changelog, migrate, and test.
- **Linter rule**: not mechanically checkable.

### `charm_tracing_config` runs on every `_reconcile` even when nothing changed (Medium)

- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:67–79`
- **Evidence**:
  ```python
  def _reconcile(self):
      self._reconcile_charm_tracing()
      if self.parca_agent.installed:
          self.parca_agent.reconcile()
          self.unit.set_workload_version(...)

  def _reconcile_charm_tracing(self):
      endpoint, ca_cert_path = charm_tracing_config(self._cos_agent, _CA_CERT_PATH)
      if not endpoint:
          return
      ops_tracing.set_destination(url=endpoint + "/v1/traces", ca=ca_cert_path)
  ```
  `_reconcile()` runs on `__init__`, `config_changed`, and `upgrade_charm`; each time it re-reads relation data and calls `ops_tracing.set_destination`, which sets up OTLP exporters — a relatively expensive call for an endpoint that rarely changes.
- **Impact**: wasted work on every hook, particularly on trivial config touches. No user-visible misbehaviour observed.
- **Fix**: cache the last-seen endpoint and only call `set_destination` when it changes.
- **Linter rule**: "expensive call in hot path without result caching" — not mechanically checkable without modeling the cost of `set_destination`.

### Workload process kill is invisible to Juju — no hook fires, no status change (Medium)

- **Severity**: medium
- **Kind**: bug
- **Where**: deployment observation
- **Evidence**: `killall -9 parca-agent` on the deployed machine; the snap's systemd service restarted within 3 seconds; `juju status` showed no change and no hook fired (checked against `juju debug-log --include-module juju.worker.uniter`); `blocked` status persisted unchanged.
- **Impact**: operators relying on Juju status as a health signal are not alerted when the profiling agent dies between `update_status` intervals (default 5 minutes).
- **Fix**: add a liveness probe in `collect_unit_status` (metrics endpoint check or snap restart-counter check) that escalates to `BlockedStatus`.
- **Linter rule**: not mechanically checkable without modeling workload semantics.

### grafana-agent blocks on `cos-agent` without a downstream sink — parca-agent metrics stranded (Low)

- **Severity**: low
- **Kind**: ux
- **Where**: deployment observation, grafana-agent 0.44/stable
- **Evidence**: relating `parca-agent:cos-agent` to `grafana-agent:cos-agent` correctly delivered the scrape config (`localhost:7071/metrics`) via `COSAgentProvider._on_refresh`. grafana-agent immediately went `blocked`: *"Missing ['grafana-cloud-config']|['grafana-dashboards-provider']|['logging-consumer']|['send-remote-write']|['tracing...'"* — it needs a sink relation to forward telemetry anywhere.
- **Impact**: parca-agent cannot be validated end-to-end with just grafana-agent — operators may think the metrics integration works when data is only received, not forwarded.
- **Fix**: document the need to also relate grafana-agent to a sink; consider a `BlockedStatus` hint on parca-agent when `cos-agent` is related but the peer has no sink.
- **Linter rule**: not mechanically checkable.

### `parse_version` assumes exactly 5 space-separated tokens (Low)

- **Severity**: low
- **Kind**: bug
- **Where**: `src/parca_agent.py:195–204`
- **Evidence**:
  ```python
  def parse_version(vstr: str) -> str:
      parts = vstr.split(" ")
      if "-next" in parts[2]:
          return f"{parts[2]}+{parts[4][:6]}"
      return parts[2]
  ```
  Accesses `parts[2]` and `parts[4]` without bounds checking. Current output (`"parca-agent, version v0.12.0 (commit: e888718...)"`) has enough tokens, but a format change would raise `IndexError`.
- **Impact**: an `IndexError` is caught as `snap.SnapError` upstream, so the unit still goes `Active` with no version set — low impact, but fragile.
- **Fix**: use `vstr.split(maxsplit=4)` and validate indices before accessing.
- **Linter rule**: "unbounded list index access after split without guard" — mechanically checkable with ruff.

### `_update_ca_certs` swallows subprocess failures (Low)

- **Severity**: low
- **Kind**: bug
- **Where**: `src/parca_agent.py:103–106`
- **Evidence**:
  ```python
  def _update_ca_certs(self):
      try:
          subprocess.run(["update-ca-certificates", "--fresh"])
      except CalledProcessError as e:
          logger.warning(f"Failed to run update-ca-certificates: {e}")
  ```
  Failure is logged as a warning with no escalation and no remediation detail.
- **Impact**: if `update-ca-certificates` fails (permissions, disk full), TLS silently breaks — profiles stop reaching the store with no indication of why.
- **Fix**: escalate to charm status, or at minimum log return code and stderr.
- **Linter rule**: "caught exception re-logged without escalating to charm status" — mechanically checkable.

### `remove_store` / `relation_departed` path never exercised in tests (Low)

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm/test_charm.py:202`, `lib/charms/parca_k8s/v0/parca_store.py:270`
- **Evidence**: the library emits `remove_store` on `relation_departed` (`parca_store.py:270–296`); `test_parca_external_store_relation_removed` only fires `relation_broken`. In a multi-unit provider, one unit departing fires `relation_departed` while the relation stays intact — a path the tests never touch.
- **Impact**: in a scaled parca-k8s deployment, a departing provider unit is invisible to the charm's test coverage, even though the charm already fails to observe `remove_store` in production code (see the critical `parca_store` finding above).
- **Fix**: add a test firing `context.on.relation_departed(store_relation)` and assert `reconcile()`/deconfiguration behaviour.
- **Linter rule**: not mechanically checkable.

### `collect_unit_status` correctly avoids setting status elsewhere, but recovery still depends on the 5-minute `update_status` interval (Low)

- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:114–157`
- **Evidence**: status is only ever set inside `collect_unit_status` (good pattern), but that handler is only invoked by `update_status` (default 5 minutes) unless another hook fires. After `juju refresh`, no other hook fires to detect the dead service, so the operator waits up to 5 minutes before `blocked: snap not running` appears.
- **Impact**: recovery/detection time for a stopped service is bounded only by the `update_status` interval — a Juju limitation compounded by the charm's other gaps above.
- **Fix**: no simple in-charm fix; could add an external liveness signal (e.g. systemd unit poking the agent), but this is secondary to fixing the missing observers.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Clean `collect_unit_status` pattern** (`src/charm.py:114–157`): status is set only via `CollectStatusEvent`, never directly in handlers, with an explicit precedence chain (store not configured → snap not installed → snap not running → revision mismatch → active).
- **Separation of workload and charm concerns**: `ParcaAgent` (`src/parca_agent.py`) encapsulates all snap operations; `charm.py` has no direct snap imports.
- **Idempotent-looking reconciler**: `ParcaAgent.reconcile()`/`_reconcile_config` compare current snap config before writing, avoiding unnecessary restarts when nothing changed (though see the `install()` idempotency finding above for the exception).
- **Actionable status messages**: `BlockedStatus` text includes concrete remediation commands (`sudo snap logs parca-agent`, `juju integrate ... parca-agent`).
- **Correct subordinate declaration**: `subordinate: true` and `scope: container` on `juju-info` in `charmcraft.yaml`.
- **Explicit port management**: `self.unit.set_ports(7071)` called explicitly in `_on_start`.
- **`COSAgentProvider` auto-registers its own relation observers** (`lib/charms/grafana_agent/v0/cos_agent.py:671–672`), so the charm doesn't need to observe `cos-agent` events for relation data to be written — a better library design than `ParcaStoreEndpointRequirer`'s partial observer set.

## Common-practice notes

- Subordinate lifecycle (create/destroy tracking the principal, correct scale behaviour) works correctly on both Juju 4.0.12 and 3.6.27, with identical hook ordering and timing.
- The charm registers no observers for `parca-store-endpoint`, `receive-ca-cert`, or `cos-agent` relation events, relying on Juju's implicit `config-changed` — confirmed not to fire after `relation-created`/`-changed`/`-broken` for these relations, making this reliance a real gap rather than a benign style choice.
- Uses `cos_agent` library v0 (LIBPATCH 25), the standard machine-charm library for Grafana Agent integration; it uses the deprecated Pydantic v1 `__fields__` API, producing `PydanticDeprecatedSince20` warnings under Pydantic v2.
- `charmcraft.yaml` is a modern layout (`parts.charm.override-build` injects git version, `platforms` lists `ubuntu@22.04:amd64` and `ubuntu@24.04:amd64`, `assumes juju >= 3.6`).
- No charm config options — all behaviour is relation-driven, appropriate for a subordinate snap-management charm.
- `tox.ini` uses `uv` for dependency management.
- `snap.hold()` after install is a deliberate stability choice, but combined with the hard-coded revision it means the snap never gets security or bug fixes unless a maintainer bumps `_snap_revisions` and cuts a new charm release.
- `ParcaStoreEndpointRequirer` registers only `relation_changed` and `relation_departed` (no `relation_joined`), so `endpoints_changed` only fires on data changes after the relation is already up — an asymmetry with `cos_agent`'s more complete observer set that makes `parca_store` integration require more explicit charm-side code than the charm currently has.

## Tests

- **Unit** (`tests/unit`, 22 tests, all passing): covers install, refresh, start, remove, relation join/leave, CA cert merging, charm tracing config, using `ops_scenario.Context`.
  - Coverage gap: no test asserts `reconcile()` was called (or not) after any event — only internal state (`_store_config`, `_certificates`) is checked, so none of the missing-observer bugs above can be caught by this suite.
  - Coverage gap: `test_parca_external_store_relation_removed` fires `relation_broken`, not `relation_departed`, so `remove_store` is never exercised.
  - Coverage gap: `test_parca_receive_ca_cert` fires `relation_changed` on the store relation, not the `receive-ca-cert` relation, so certificate event handling is not actually tested.
  - Coverage gap: `test_update_status_refreshes_snap_hold` verifies `hold()` is called but not that a changed revision triggers an actual snap refresh.
  - Coverage gap: `_snap`'s SnapCache-per-access behaviour is masked by mocking at the `MagicMock` level.
  - Running the full `tests/` tree fails on an `__pycache__` import conflict; clear `__pycache__` first.
  - `ruff check src/` reports 2 real E501 violations (`src/charm.py:140`, `:151`) that are masked because `pyproject.toml` globally ignores E501.
  - `lib/charms/grafana_agent/v0/cos_agent.py:439` triggers `PydanticDeprecatedSince20` warnings from `__fields__` usage.
- **Integration** (`tests/integration`): deploys on real LXD machines (noble with `virt-type=virtual-machine`, and jammy container); asserts only status values, no snap config/relation data/log assertions.
  - `test_tracing.py` is the one integration test that asserts a numeric value (OTLP metric count via `_get_otelcol_metric()`), a good pattern, but it doesn't test the full COS stack.
  - Coverage gaps: no integration test for the full `parca_store` lifecycle (join → configured → address change → removed), no CA-cert-to-disk assertion, no `cos-agent`-with-sink test, no `juju refresh` test, no failure-injection test, no scale test.
  - Could not be run directly in this review environment (requires `charmcraft pack` + `jubilant` harness).

## Docs

- `README.md` (953 bytes): explains what parca-agent is and the basic integrate command; adequate but minimal.
- `CONTRIBUTING.md` (3106 bytes): good dev setup instructions (tox, charmcraft pack, deploy).
- `charmcraft.yaml` description: detailed and accurate, covers all three relation interfaces; matches the Charmhub page.
- Docs/reality mismatch: Charmhub showed `parca-agent rev 126` on `0.35/stable`; the deployed charm was `rev 124` — two revisions behind, with no obvious way for an operator to notice without `juju show-application`.
- Documentation gap: the README does not mention `receive-ca-cert`, the `parca_store` relation requirement, or `cos-agent` — that information lives only in `charmcraft.yaml`, not the operator-facing README.

## Open questions

1. Is bumping `_snap_revisions` past the memory-leak fix (issue #114, open since 2026-07-13) blocked on something, or just unscheduled?
2. Should `_on_upgrade_charm` call `start()` explicitly, and should `install()` be made idempotent for same-revision calls?
3. Is the missing `config_changed` observer intentional, or an oversight — given that `_reconcile()` already depends on it firing?
4. What's blocking the `operator_libs_linux` v1→v2 migration (issues #110, #41, open over a year)?
5. Is `snap.hold()` intentional for all environments, or should it be configurable, given it currently pins to a version well behind upstream security/bug fixes?
6. Should the charm detect and report the eBPF crash loop in containerized environments rather than reporting Active/blocked purely on relation state?
7. What is the intended use case for relating `receive-ca-cert` without a `parca_store` relation, given the charm currently silently ignores the certificates in that case?
8. Is the Polarsignals-cloud default store address intentional "demo mode," or should the charm suppress it for air-gapped/privacy-sensitive deployments? (unverified: exact mechanism by which the snap sets this default was not confirmed against upstream source, only observed behaviourally and via reviewer notes.)
9. Should the test suite be restructured to assert on `reconcile()` invocation and its side effects rather than only internal state?
10. Should charm maintainers report the `0.35/edge` rev 140 malformed-archive issue to the Charmhub team?
