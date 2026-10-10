# opensearch-dashboards-operator

This repo ships two charms — `opensearch-dashboards` (machine) and `opensearch-dashboards-k8s` (k8s) — that delegate all business logic to a shared pip package, `opensearch-dashboards-charms-single-kernel`. The k8s charm was merged recently (PR #275, July 2026) and is only published to `2/edge` (rev 3); the machine charm is on `2/stable` (rev 66) and `2/edge` (rev 76). Architecture is clean and follows current Data Platform conventions (`TypedCharmBase`, `data-platform-helpers` StatusHandler, single-kernel pattern, `pathops`).

The charm has a critical timing bug: it renders a config referencing a CA file that OpenSearch hasn't written yet, so the workload crash-loops for the entire duration of backend startup/TLS setup (confirmed on both substrates, both Juju 4.x and 3.6, across multiple independent deployments). It recovers automatically once the backend supplies the CA, but the crash-loop window can last minutes with no unit tests to catch it. There's also a real but juju-version-sensitive scale-up `KeyError` on Juju 3.6 K8s, and a health-check gap where the charm can't tell its own workload is dead if there's no backend relation. A maintainer should fix the CA-file guard first (it's a one-line condition change with a clear reproduction), then chase the scale-up KeyError and the health-check blind spot. The `status-detail` action's structured, per-component status output is the best of its kind seen in this series of reviews and should be treated as a model for other charms.

| | |
|---|---|
| Repo | canonical/opensearch-dashboards-operator @ `186da44` (2026-07-23) |
| Charms | `opensearch-dashboards` (machine), `opensearch-dashboards-k8s` (k8s) |
| Substrate | k8s and machine |
| Deployed | yes — Juju 4.x K8s: concierge-k8s-4, `opensearch-dashboards-k8s` 2/edge rev 3 (+ traefik-k8s, self-signed-certificates); Juju 4.x LXD: concierge-lxd-4, `opensearch-dashboards` 2/edge rev 76 (+ opensearch, self-signed-certificates); Juju 3.6 K8s: concierge-k8s-3, `opensearch-dashboards-k8s` 2/edge rev 3 (scaled 1→2, reproduced and failed to reproduce a KeyError across two attempts); Juju 3.6 LXD: concierge-lxd, `opensearch-dashboards` 2/edge rev 76 (opensearch snap install did not finish in time to reach active) |
| Reviewed | 2026-08-02 |

## What it does

Deploys OpenSearch Dashboards, the web UI for OpenSearch. Supports:
- HTTP (default) and HTTPS (via `certificates` relation)
- `opensearch-client` relation to the OpenSearch backend
- OAuth via `oauth` relation (hydra)
- JWT authentication via `jwt-configuration` relation
- COS observability: `metrics-endpoint`, `grafana-dashboard`, `logging` (`loki_push_api` on k8s, `cos-agent` on VM)
- Ingress via `ingress` relation (traefik-k8s, k8s only)
- Rolling restart via `rollingops` v0
- Upgrade orchestration via `upgrade` peer relation
- Structured multi-component status reporting via the `status-detail` action

## Deployment log

### Juju 4.x LXD + K8s cross-model (concierge-lxd-4 / concierge-k8s-4, juju 4.0.5)

```
juju add-model -c concierge-lxd-4 rv-osd-lxd2
juju deploy opensearch --channel 2/edge --constraints "mem=4G"
juju deploy self-signed-certificates --channel latest/stable
juju integrate opensearch self-signed-certificates
# ~14 min for opensearch snap install + TLS setup
juju offer opensearch:opensearch-client opensearch

juju add-model -c concierge-k8s-4 rv-osd-k8s3
juju deploy opensearch-dashboards-k8s --channel 2/edge --trust
juju consume concierge-lxd-4:admin/rv-osd-lxd2.opensearch
juju integrate opensearch-dashboards-k8s opensearch
```

- Opensearch on LXD took ~14 minutes to install (snap download); ran single-node (blocked on unassigned replicas, expected).
- K8s dashboards pod running, Pebble showed `opensearch-dashboards` service in `backoff`.
- Pebble logs: `FATAL Error: ENOENT: no such file or directory, open '/etc/opensearch-dashboards/certificates/opensearch_ca.pem'`.
- The `certificates/` directory in the container was empty while the config referenced `opensearch_ca.pem`.
- `status-detail` returned: cluster_manager blocked "OpenSearch connection is missing", ingress_manager blocked "Ingress relation missing", health_manager blocked "Service is not alive".
- Reproducing this via a cross-model relation confirms it's a code issue, not an environmental one — the crash-loop happened *after* the relation was created, before CA data arrived through the cross-model relay.

### Juju 3.6 LXD (concierge-lxd, juju 3.6.23)

```
juju add-model -c concierge-lxd rv-osd36
juju deploy opensearch-dashboards --channel 2/edge      # rev 76, ubuntu@24.04
juju deploy opensearch --channel 2/edge --constraints "mem=4G"  # rev 356, ubuntu@24.04
juju deploy self-signed-certificates --channel latest/stable    # rev 264, ubuntu@22.04
juju integrate opensearch self-signed-certificates
juju integrate opensearch-dashboards opensearch
```

- Self-signed-certificates agent (ubuntu@22.04, machine 1) took ~6 minutes to start, pending on controller provisioning delay.
- Opensearch snap install was still in progress after 8+ minutes.
- Dashboards snap install completed at ~4 minutes, then blocked "OpenSearch connection is missing".
- Same CA-file crash-loop observed: config referenced `opensearch_ca.pem` before the certs directory had any files. Snap logs confirmed `FATAL ENOENT opensearch_ca.pem`, restart counter reached 1+.
- Exporter daemon remained active despite the main daemon crash-looping.
- Port 5601 was open despite the service not being healthy.
- Opensearch never finished installing during this run, so full recovery on this substrate/juju combination was not directly observed (it was observed on the equivalent juju 4.x LXD run below).

### Juju 3.6 K8s (concierge-k8s-3, juju 3.6.25)

```
juju add-model -c concierge-k8s-3 rv-osd-k36
juju deploy opensearch-dashboards-k8s --channel 2/edge --trust      # rev 3
```

- Pod running, both Pebble services (`opensearch-dashboards` + prometheus-exporter) active.
- No opensearch relation, so config had no CA reference — service started successfully.
- Blocked "OpenSearch connection is missing" and "Ingress relation missing" — correct.
- `status-detail`: structured JSON, app-scope vs unit-scope distinction verified.
- `pre-upgrade-check`: completed successfully (no upgrade in progress).
- `resume-upgrade`: failed with "Upgrade can be resumed only once after juju refresh is called" — correct.
- `set-tls-private-key`: failed with "Relation certificates does not exist" — expected, no TLS relation.
- Bad config (`log_level=DEBUG`): correctly blocked "Config options are invalid".
- Killed workload process: Pebble restarted within 5 seconds; charm stayed blocked.
- Scale up 1→2: unit 1 entered error state with `KeyError: <ops.model.Unit opensearch-dashboards-k8s/0>` in `upgrade-relation-changed`.
- Scale back to 1: unit removed successfully, but the error state persisted until a manual `juju resolve`.

### Juju 4.x LXD (concierge-lxd-4, juju 4.0.5) — second run

```
juju add-model -c concierge-lxd-4 rv-osd-lxd2
juju deploy opensearch-dashboards --channel 2/edge      # rev 76, ubuntu@24.04
juju deploy opensearch --channel 2/edge --constraints "mem=4G"  # rev 356, ubuntu@24.04
juju deploy self-signed-certificates --channel latest/stable    # rev 264, ubuntu@22.04
juju integrate opensearch self-signed-certificates
juju integrate opensearch-dashboards opensearch
```

- Opensearch snap install took ~14 minutes; self-signed-certificates became active at ~4 min.
- Dashboards snap install completed at ~4 minutes, then blocked "OpenSearch connection is missing".
- During the ~6-minute gap between dashboards-ready and opensearch providing CA data, the service crash-looped.
- Snap logs: `FATAL Error: ENOENT: no such file or directory, open '/var/snap/opensearch-dashboards/current/etc/opensearch-dashboards/certificates/opensearch_ca.pem'`, restart counter reached at least 5.
- At ~20:42 UTC opensearch reached active; at ~20:43 UTC dashboards became **active** — the CA file (2456 bytes) was written and the config updated with hosts, username, and password. Full recovery confirmed.
- Config during crash-loop had `opensearch.ssl.certificateAuthorities` but no hosts/credentials; after recovery it had `opensearch.hosts`, `opensearch.username`, `opensearch.password`, and `opensearch.ssl.certificateAuthorities`.
- Exporter daemon remained active throughout, including the crash-loop.
- Port 5601 was open before the service was healthy.

#### Failure injections (after reaching active)

1. **Invalid config** (`log_level=DEBUG`, not in allowed set): blocked "One or more config options are invalid" with action guidance to use `juju config`. `config_manager` status showed blocked while other managers stayed active. Restoring `log_level=INFO` returned to active. Pass.
2. **Remove/re-add opensearch relation**: after `juju remove-relation`, blocked "OpenSearch connection is missing" within seconds, no traceback. After re-adding, went through the same blocked→CA-file-written→active path observed in the previous run; the re-add on this run was still mid-flight (relation-changed not yet fired) at time of check. Pass for the remove path.
3. **Kill workload process** (`pkill -f "node.*cli/dist"`): snap/systemd auto-restarted the daemon within 30 seconds; the charm did not detect the outage and stayed "active" throughout. Exporter kept running. System-level recovery works, charm status lags.
4. **Config change while healthy** (`log_level=ERROR`): config re-rendered with `logging.silent: true` and restarted the service; status went restarting→active; debug log lines stopped. Pass.

### Fresh Juju 4.x K8s with TLS + ingress (rv-osd-k8s-deep)

```
juju add-model -c concierge-k8s-4 rv-osd-k8s-deep
juju deploy opensearch-dashboards-k8s --channel 2/edge --trust
juju deploy self-signed-certificates --channel latest/stable
juju deploy traefik-k8s --channel latest/stable --trust
juju integrate opensearch-dashboards-k8s self-signed-certificates
juju integrate opensearch-dashboards-k8s traefik-k8s
```

- All apps reached active/blocked (dashboards blocked "OpenSearch connection is missing"; traefik and certs active).
- Both Pebble services active — no crash-loop because no opensearch relation means no CA reference in config.
- Pod restart (`kubectl delete pod`): recovered through `upgrade-charm` → rolling restart → blocked within ~40 seconds.
- Scale up 1→2: both units settled blocked, no KeyError on juju 4.x.
- Invalid config (`log_level=INVALID`): both units correctly blocked "Config options are invalid".
- `status-detail`: clean multi-component table with Action guidance for both missing integrations.
- Stopped the Pebble service directly (`pebble stop`): the charm did not detect it — `health_manager` stayed "active" and status remained blocked "OpenSearch connection is missing" for over 10 minutes.

### Fresh Juju 4.x LXD (rv-osd-deep)

```
juju add-model -c concierge-lxd-4 rv-osd-deep
juju deploy opensearch --channel 2/edge --constraints "mem=4G"
juju deploy opensearch-dashboards --channel 2/edge
juju deploy self-signed-certificates --channel latest/stable
juju integrate opensearch self-signed-certificates
juju integrate opensearch-dashboards opensearch
```

- Dashboards snap install completed at ~4 min; opensearch snap install was still in progress (7+ min) at last check.
- Config written with a non-existent CA path:
  ```yaml
  opensearch.ssl.certificateAuthorities:
  - /var/snap/opensearch-dashboards/current/etc/opensearch-dashboards/certificates/opensearch_ca.pem
  ```
- Snap logs confirmed the same crash-loop: `FATAL Error: ENOENT: no such file or directory, open '...opensearch_ca.pem'`.
- Main daemon inactive, exporter daemon active; port 5601/tcp reported open despite the service not listening.
- Recovery expected once opensearch provides credentials (confirmed on the prior LXD run).

### Fresh Juju 3.6 K8s (rv-osd-k36-deep)

```
juju add-model -c concierge-k8s-3 rv-osd-k36-deep
juju deploy opensearch-dashboards-k8s --channel 2/edge --trust
```

- Single unit reached blocked "OpenSearch connection is missing" + "Ingress relation missing".
- Scale up 1→2: both units settled blocked — KeyError did **not** reproduce on this attempt.
- Scale down 2→1: clean removal.
- Actions all correct: `status-detail` (structured table), `pre-upgrade-check` (completed), `resume-upgrade` (correctly rejected, no refresh pending).
- Application removed successfully.

## Observed behaviour

1. **Workload crash-loop on missing CA file** — confirmed on multiple fresh deployments, both substrates, both juju versions. When an `opensearch-client` relation exists but the backend hasn't yet provided TLS CA data, the config manager writes `opensearch.ssl.certificateAuthorities` pointing to a path that doesn't exist on disk. The process fails to open the CA file at startup and exits fatally; Pebble/systemd restarts it, creating a crash loop. The `certificates/` directory is empty at this point. This is only visible through runtime observation of the timing gap between relation creation and CA delivery — not from code alone. The charm recovers automatically once CA data arrives (confirmed on VM).
2. **Config references CA path even when credentials are missing**: `dashboard_properties()` adds `opensearch.ssl.certificateAuthorities` based on `self.state.opensearch_server` being truthy (relation exists), without checking whether CA data is actually available. `TLSManager.set_ca_opensearch()` only writes the file once `password`, `endpoints`, and `tls_ca` are all present. The charm shows blocked "OpenSearch connection is missing" (password absent) but still writes a config referencing the non-existent CA file.
3. **Scale-up causes permanent error state on juju 3.6 K8s**: scaling 1→2 triggers a `KeyError` in `upgrade-relation-changed` on the new unit. The DataUpgrade library's `on_upgrade_changed()` accesses `peer_relation.data[top_unit]` for a unit whose state isn't yet in the new unit's view of the relation. The hook fails repeatedly and needs manual `juju resolve`.
4. **Excellent structured status output**: `status-detail` returns per-component status JSON with Status, Component Name, Message, Action, and Reason fields, distinguishing app-scope from unit-scope statuses and giving concrete operator guidance (e.g. "Integrate OpenSearch and OpenSearch Dashboards charms"). Strong UX pattern.
5. **Deprecated `rollingops` v0 warnings**: logs repeat `The 'rollingops' v0 library is deprecated and no longer maintained` on every restart/status-peers event.
6. **"Redirect URL uses http scheme" warnings**: logged on every status-peers and restart event even when TLS is not configured — noisy and potentially confusing.
7. **Exporter stays up when the main service is down**: the prometheus-exporter service (systemd on VM, Pebble on K8s) remains active even when the dashboards service is crash-looping, so it reports metrics for a dead service.
8. **Port 5601 reported open before the service is healthy**: `juju status` shows 5601/tcp open even while the dashboards service is crashing; `open_port()` is called during restart regardless of whether the service actually starts.
9. **Charm status lags after workload process death**: killing the workload process (e.g. `pkill node`) gets it restarted by Pebble/systemd within 5-30 seconds, but the charm stays at its previous status until the next `update-status`.
10. **Service starts fine on K8s with no opensearch relation**: with no relation, config has no `opensearch.ssl.certificateAuthorities` key and the dashboards service starts and runs — confirming the crash is caused entirely by the config referencing a non-existent file.
11. **Blocking hook execution during restart/health-check cycle**: `restart_server()` (30s sleep loop) plus `wait_for_unit_health()` (90s sleep loop) can block a single hook for up to 120 seconds, serializing event processing during the crash-loop.
12. **Workload health not checked when no opensearch relation exists**: `check_unit_health()` short-circuits to `return True` when `not self.state.opensearch_server`. Stopping the dashboards Pebble service directly left the charm blocked "OpenSearch connection is missing" with `health_manager` showing "active" — the charm never detected its own workload was down.
13. **Port remains open after workload process dies** on both substrates — opened unconditionally before the health check, never closed on failure.
14. **Pod restart recovery works but is suboptimal**: on `kubectl delete pod`, recovery goes through `upgrade-charm` → `pebble-ready` → a deferred `start`/`update-status` before restarting, taking ~40 seconds rather than the ~5 seconds achievable if `_on_pebble_ready` triggered `emit_restart()` directly.
15. **Scale-up KeyError not reproducible on juju 4.x K8s**: two separate scale-up attempts (with and without an opensearch relation) both succeeded on juju 4.x. The earlier juju 3.6 finding suggests a juju-version-specific race; the unguarded `peer_relation.data[unit]` access remains in the code regardless.

## Findings

### Config references CA file before it exists, causing crash-loop
- **Severity**: critical
- **Kind**: bug
- **Where**: `single_kernel_opensearch_dashboards/managers/config.py:101,116-118`, `dashboard_properties()`
- **Evidence**:
  ```python
  opensearch_ca = self.workload.paths.opensearch_ca if self.state.opensearch_server else None
  ...
  if opensearch_ca:
      properties["opensearch.ssl.certificateAuthorities"] = [opensearch_ca.as_posix()]
  ```
  This adds the CA path based only on `self.state.opensearch_server` being truthy (relation exists), not on whether the CA file exists. `TLSManager.set_ca_opensearch()` only writes the file once `password`, `endpoints`, and `tls_ca` are all present, creating a timing gap where every render in that window references a non-existent file. Confirmed on VM (snap restart counter 5+) and K8s (Pebble backoff). VM config during the crash: `opensearch.ssl.certificateAuthorities: [/var/snap/opensearch-dashboards/current/etc/opensearch-dashboards/certificates/opensearch_ca.pem]` with no hosts/creds.
- **Impact**: The dashboards service cannot start until the OpenSearch backend is fully operational and has delivered its CA certificate. Backend install can take 14+ minutes, during which the dashboards charm crash-loops instead of sitting in a clean blocked/idle state. Re-adding a removed relation triggers the same crash-loop until CA data arrives again. Recovery is automatic once CA data arrives (confirmed on VM).
- **Fix**: Guard the CA config addition with the actual CA data, not just relation existence, e.g. `opensearch_ca = self.workload.paths.opensearch_ca if self.state.opensearch_server and self.state.opensearch_server.tls_ca else None`.
- **Linter rule**: Not mechanically checkable — requires understanding the dependency between config generation and file creation timing. A runtime test that relates the charm to opensearch and checks workload status during the gap would catch it.

### Workload health not checked when no opensearch relation exists
- **Severity**: high
- **Kind**: bug
- **Where**: `single_kernel_opensearch_dashboards/managers/health.py:100-110`, `check_unit_health()`
- **Evidence**:
  ```python
  def check_unit_health(self) -> bool:
      if not self.workload.healthy():
          return False
      if not self.state.opensearch_server or not self.workload.exists(
          self.workload.paths.opensearch_ca
      ):
          return True  # returns healthy even if workload is dead
  ```
  If the workload is healthy at call time and later dies, subsequent calls hit the second branch: `not self.state.opensearch_server` is true with no backend, so it returns True regardless. Confirmed at runtime: stopping the K8s Pebble service directly left the charm blocked "OpenSearch connection is missing", with `health_manager` showing "active", for over 10 minutes.
- **Impact**: Operators without an OpenSearch backend (initial setup, or backend temporarily removed) have no visibility into whether the dashboards workload itself is running. The charm reports the missing-backend problem but never reports that the process has crashed.
- **Fix**: Keep `self.workload.healthy()` as a prerequisite check that always runs, independent of backend presence, e.g. only short-circuit to `return True` for "no backend to check against" after confirming the workload process itself is alive.
- **Linter rule**: Not mechanically checkable — requires understanding the semantics of the short-circuit conditions.

### Scale-up causes KeyError in upgrade-relation-changed hook (juju 3.6 only)
- **Severity**: high
- **Kind**: bug
- **Where**: `single_kernel_opensearch_dashboards/lib/charms/data_platform_libs/v1/upgrade.py:681` (`_get_unit_state`, called from `on_upgrade_changed` at line 1030) and `single_kernel_opensearch_dashboards/core/cluster.py:315-316` (`upgrade_unit_states`)
- **Evidence**: Scaling the k8s charm 1→2 on juju 3.6 put unit 1 into error state with `KeyError: <ops.model.Unit opensearch-dashboards-k8s/0>`, originating from `self.peer_relation.data[top_unit]` in `_get_unit_state()` when unit 1 tries to read unit 0's state before it's synced. Not reproducible on juju 4.x K8s across two separate scale-up attempts. `core/cluster.py:315-316` has the same unguarded access pattern (`self.upgrade_relation.data[unit].get(...)`).
  ```
  File ".../ops/main.py", line 39, in main
      return _main.main(charm_class=charm_class, ...)
  KeyError: <ops.model.Unit opensearch-dashboards-k8s/0>
  ```
- **Impact**: Scale-up (including recovery from pod eviction) can leave a new unit in error state until manually resolved, blocking scaling without operator intervention.
- **Fix**: Guard `_get_unit_state()` with a check for whether the unit exists in the relation data, or use `.get()` instead of direct dict access; ensure `build_upgrade_stack()` doesn't include units whose state isn't yet known to the joining unit.
- **Linter rule**: Mechanically checkable — flag bare `self.peer_relation.data[unit]` access without a preceding membership guard.

### Port opened before service is confirmed healthy
- **Severity**: medium
- **Kind**: bug
- **Where**: `single_kernel_opensearch_dashboards/charms/base.py:177`, `restart_on_lock_acquired()`
- **Evidence**: `self.unit.open_port(protocol="tcp", port=SERVER_PORT)` is called before `self.health_manager.check_osd_health()` at line 186. Observed: `juju status` showed 5601/tcp open while the dashboards service was crash-looping and not listening.
- **Impact**: Load balancers or operators may route traffic, or health-check, a port that's nominally open but has no listener, causing connection refusals/timeouts and potential false alerts or failovers.
- **Fix**: Move `open_port()` to after the health check confirms the service is running.
- **Linter rule**: Not mechanically checkable — requires tracing operation order relative to health checks.

### `restart_server()` blocks hook with synchronous sleep loop
- **Severity**: medium
- **Kind**: performance
- **Where**: `single_kernel_opensearch_dashboards/managers/cluster.py:43-44`, `restart_server()`
- **Evidence**: `while not self.workload.healthy() and time.time() - start_time < RESTART_TIMEOUT: time.sleep(5)` blocks the hook for up to `RESTART_TIMEOUT` (30s) with a 5-second sleep loop.
- **Impact**: During the crash-loop, every restart attempt blocks the hook for the full 30 seconds, then crashes again after ~3 seconds, repeating. This serializes all event processing while the backend isn't ready.
- **Fix**: Use exponential backoff, or split restart verification into a deferred event chain so the hook returns quickly and re-checks later.
- **Linter rule**: Mechanically checkable — flag `time.sleep()` inside a synchronous charm hook path (e.g. within a while loop in a hook handler).

### `wait_for_unit_health()` blocks hook for up to 90 seconds
- **Severity**: medium
- **Kind**: performance
- **Where**: `single_kernel_opensearch_dashboards/managers/health.py:115-138`, `wait_for_unit_health()`
- **Evidence**:
  ```python
  while unit_healthy is not True and time.time() - start_time < SERVICE_AVAILABLE_TIMEOUT:
      time.sleep(5)
      unit_healthy, unit_message = self.dashboards_status()
  ```
  `SERVICE_AVAILABLE_TIMEOUT` is 90 seconds. Combined with `restart_server()`'s 30-second timeout, one restart cycle can block a hook for up to 120 seconds.
- **Impact**: During the observed crash-loop, config render → `restart_server()` (30s) → `wait_for_unit_health()` (up to 90s) totals up to 120 seconds of blocked hook execution per cycle; other queued events pile up behind it.
- **Fix**: Same as `restart_server()` — exponential backoff or a deferred event chain.
- **Linter rule**: Mechanically checkable — same rule as `restart_server()`.

### Sync blocking HTTP call in `OAuth.uses_trusted_ca`
- **Severity**: medium
- **Kind**: performance
- **Where**: `single_kernel_opensearch_dashboards/core/models.py`, `OAuth.uses_trusted_ca`
- **Evidence**:
  ```python
  @property
  def uses_trusted_ca(self) -> bool:
      try:
          requests.get(self.issuer_url, timeout=10)
          return True
      except requests.exceptions.SSLError:
          return False
      except requests.exceptions.RequestException:
          return True
  ```
  Called from `OAuthEvents._on_oauth_relation_changed()` (`events/oauth.py`, ~line 75), a synchronous handler.
- **Impact**: When OAuth is configured, every `relation-changed` event can block for up to 10 seconds if the IDP is slow or unreachable. Neither JWT nor OAuth was exercised against a real backend in this review, so this is verified from code, not runtime.
- **Fix**: Cache the result after first call, reduce the timeout, or move the check off the hook path.
- **Linter rule**: Mechanically checkable — flag `requests.get()`/`requests.post()` calls inside charm hook paths.

### Unguarded pathops calls in health checks may propagate exceptions
- **Severity**: medium
- **Kind**: bug
- **Where**: `single_kernel_opensearch_dashboards/managers/health.py:147-148, 200-202`, `check_opensearch_health()` / `get_statuses()`
- **Evidence**:
  ```python
  def check_opensearch_health(self) -> None:
      if self.state.opensearch_server and (
          self.workload.paths.opensearch_ca.exists()
          and self.workload.paths.opensearch_ca.read_text()
      ):
  ```
  `.exists()`/`.read_text()` on `pathops.PathProtocol` can raise `OSDFileOperationError`. `check_osd_health()` wraps this in try/except (`base.py:185`), but `get_statuses(recompute=True)` (`health.py:183`) calls it without one.
- **Impact**: If `get_statuses(recompute=True)` runs while Pebble is momentarily unreachable, this could surface as an unhandled exception rather than a clean status message. Not observed directly in this review; verified from code (unverified in practice).
- **Fix**: Wrap the pathops calls in try/except `OSDFileOperationError`, or catch it at the top of `get_statuses(recompute=True)`.
- **Linter rule**: Mechanically checkable — flag `pathops.PathProtocol.exists()`/`.read_text()`/`.write_text()` outside a try/except catching `OSDFileOperationError`.

### `_on_pebble_ready` does not trigger workload start
- **Severity**: medium
- **Kind**: bug
- **Where**: `single_kernel_opensearch_dashboards/events/opensearch_dashboards.py:89-98`, `_on_pebble_ready()`
- **Evidence**: The handler checks container readiness and defers if not ready; if ready, it adds status and returns without calling `emit_restart()`. Actual start depends on a deferred `_on_start` being re-emitted later.
- **Impact**: Matches the observed ~40-second pod-restart recovery time (rather than the ~5 seconds achievable by triggering restart directly). Also means the TLS-file-recovery path isn't triggered from `pebble-ready`.
- **Fix**: In `_on_pebble_ready`, call `self.tls_manager.write_tls_files()` then `self.charm.emit_restart(event)` once the container is confirmed connectable.
- **Linter rule**: Not mechanically checkable — requires understanding lifecycle event ordering.

### Upgrade functionality silently disabled when not trusted
- **Severity**: medium
- **Kind**: ux
- **Where**: `single_kernel_opensearch_dashboards/charms/base.py:110-115`
- **Evidence**: `__init__()` wraps `UpgradeEvents` in try/except `OSDNotTrusted`; log shows `OpenSearch Dashboards charm is not trusted, upgrade functionality is not possible`. `metadata.yaml` sets `charm-user: non-root`. If the exception is caught, `self.upgrade_events` is never set, but status output doesn't reflect this.
- **Impact**: Operators deploying without `--trust` won't know upgrade is disabled until they try it. The README doesn't mention `--trust` prominently.
- **Fix**: Add a status indicator for upgrade-disabled-due-to-trust in `UpgradeManager.get_statuses()`, and document the `--trust` requirement in the README.
- **Linter rule**: Not mechanically checkable.

### No unit tests in the repo
- **Severity**: medium
- **Kind**: test-gap
- **Where**: No `tests/unit/` directory; `tox.ini` has `lint` and `integration` environments only.
- **Evidence**: All test coverage is integration-level (`tests/integration/test_charm.py`). Business logic lives in the pip-installed single-kernel package.
- **Impact**: Issues like the CA-file timing bug could be caught with scenario-based tests simulating relation lifecycle, without needing a full backend deployment.
- **Fix**: Add scenario tests for the charm's integration points, especially config generation and relation data flow.
- **Linter rule**: Not mechanically checkable.

### Deprecated `rollingops` v0 library in use
- **Severity**: low
- **Kind**: lint
- **Where**: `single_kernel_opensearch_dashboards/charms/base.py` — uses `RollingOpsManager` from `charms.rolling_ops.v0.rollingops`
- **Evidence**: Logs show `The 'rollingops' v0 library is deprecated and no longer maintained. Please migrate to the new implementation: https://github.com/canonical/charmlibs/tree/main/rollingops`, repeated on every restart and status-peers event.
- **Impact**: Dependency on an unmaintained library; future compatibility risk and log noise.
- **Fix**: Migrate to the charmlibs rollingops library.
- **Linter rule**: Mechanically checkable — grep for `charms.rolling_ops.v0` imports.

### Repeated log warning for HTTP redirect URL
- **Severity**: low
- **Kind**: lint
- **Where**: Upgrade library dependency (`data_platform_libs.v1.upgrade`)
- **Evidence**: `Provided Redirect URL uses http scheme. Don't do this in production` logged on every status-peers/restart event, even when TLS is not configured and HTTP is the only valid scheme in that state.
- **Impact**: Log spam that may alarm operators or obscure real issues.
- **Fix**: Suppress the warning, or make it conditional on TLS being enabled.
- **Linter rule**: Not mechanically checkable.

### Juju 3.6 LXD controller provisioning delay
- **Severity**: low
- **Kind**: ux
- **Where**: Observed on concierge-lxd (juju 3.6.23)
- **Evidence**: Machine 1 (self-signed-certificates, ubuntu@22.04) stayed "pending" for ~6 minutes after provisioning while machines 0 and 2 (ubuntu@24.04) connected within ~3 minutes.
- **Impact**: Operators on juju 3.6 LXD mixing bases may see slow deployments. Not charm-specific.
- **Fix**: Not applicable to this charm; worth documenting for support.
- **Linter rule**: Not mechanically checkable.

## What's good

1. **Multi-component structured status via `status-detail`**: `StatusHandler` from `data_platform_helpers` plus the `status-detail` action produce per-component status with Action guidance — the best status UX seen in this review series. (`core/cluster.py`, `managers/*.py`)
2. **Single-kernel pattern**: sharing logic between VM and K8s charms via a pip-installed package is clean; substrate-specific code per charm is minimal (`workload`, `substrate`, logger setup). (`kubernetes/src/charm.py`, `machine/src/charm.py`)
3. **Pathops for container-agnostic file operations**: `charmlibs.pathops`/`PathProtocol` abstracts Pebble vs. local filesystem cleanly, with consistent error handling in `WorkloadBase`. (`workload/base.py`)
4. **`TypedCharmBase` with Pydantic config**: type-safe config access via `data_platform_libs.v1.data_models`; `ConfigManager.get_statuses()` validates `log_level` against allowed values. (`charms/base.py:38`, `managers/config.py`)
5. **Clean separation of managers and events**: managers handle state mutations, events handle hook dispatch; each manager exposes `get_statuses()` returning `StatusObject`s — consistent, testable pattern. (`managers/`)
6. **CI validates prometheus alert rules** with `promtool check rules`. (`ci.yaml:promtool`)

## Common-practice notes

- Follows convention: `data_platform_helpers`, `data_platform_libs`, `charmlibs.pathops`, `pytest-operator`, spread, concierge, standard `tox.ini`/`pyproject.toml` layout — fully aligned with the Data Platform team's current practices.
- Metadata is complete: both charms declare `charm-user: non-root`, relations with proper interfaces/limits, OCI resource with `upstream-source`, links to docs/source/issues. The k8s charm correctly has `ingress`, `logging`, `metrics-endpoint`, `grafana-dashboard` that the VM charm lacks.
- `concierge-k8s.yaml` present for both LXD and k8s substrates, easing test environment setup.
- Drift from convention: uses deprecated `rollingops` v0; most newer Data Platform charms have migrated to charmlibs rollingops.
- Library versioning: all libraries are bundled inside the single-kernel pip package rather than under `lib/charms/...`. Consistent with the single-kernel pattern, but library updates require a new pip release rather than `charmcraft fetch-lib`.
- Terraform module present under `terraform/` with its own README; supports configurable units, TLS, and channel selection.

## Tests

- **Integration tests** (`tests/integration/test_charm.py`): six/seven tests covering deployment, dashboard access, TLS lifecycle, client data access, COS relations, log-level changes, and status changes on backend failure. Parameterized by substrate (vm/k8s) and feature flags (TLS, traefik, transfer_traefik_ca). Tests exercise real HTTP requests against dashboards, not just active/idle waits.
- **Spread orchestration** (`spread.yaml`): seven tasks covering VM and K8s with various TLS/traefik combinations, using concierge.
- **CI** (`.github/workflows/ci.yaml`): lint, promtool validation, terraform lint+deploy, build of all charms, integration tests, using `data-platform-workflows@v50.0.0`.
- **No unit tests**: no `tests/unit/` directory; all business logic lives in the pip package. The CA-file timing bug, the scale-up KeyError, and config re-render logic could all be caught with scenario-based state-transition tests.
- **Coverage gaps**: no tests for upgrade flow, OAuth/JWT integration, the `status-detail` action, the CA-file timing bug, or scale-up. Integration tests assume a fully working OpenSearch backend at deploy time, so the dashboards-start-before-opensearch-ready gap is never exercised.
- **Linter results** (reproduced during this review): `ruff check` clean; `codespell` clean; `poetry check --lock` clean; `ruff format --check` fails on `tests/integration/test_charm.py:535` (line exceeds 99 chars; 1 file needs reformatting, 10 already formatted); `pyright` on the repo's own code reports only expected import-resolution errors for the single-kernel package, no type errors or logic issues.

## Docs

- **README.md**: covers prerequisites, install, TLS enablement, interactive access testing — but references the machine charm only (`juju deploy opensearch-dashboards`); no mention of `opensearch-dashboards-k8s`. The k8s charm has no README of its own. The "Usage" section mentions `data-integrator`, which is an OpenSearch concern, not a dashboards one.
- **docs/ directory**: comprehensive tutorial, how-to guides (deploy-connect-scale, access-using-oauth, enable-jwt-authentication, enable-monitoring, manage-security), and reference (monitoring), published to ReadTheDocs — but entirely targeted at the machine charm; the k8s charm is undocumented.
- **Charmhub description**: same one-liner as `metadata.yaml`. `opensearch-dashboards` is on `2/stable` (rev 66, ubuntu 22.04); `opensearch-dashboards-k8s` is only on `2/edge` (rev 3, ubuntu 24.04).
- **Terraform README** (`terraform/README.md`): clear, with deployment examples.
- **Doc/reality mismatch**: README instructions (`juju deploy opensearch-dashboards --channel=2/edge`, integrate with `opensearch`) work for the machine charm but the k8s charm isn't mentioned anywhere user-facing. Docs claim port 5601 exposure — confirmed correct on both substrates.

## Open questions

1. Why is the scale-up KeyError reproducible on juju 3.6 but not juju 4.x? Two juju 3.6 K8s attempts gave different results (one KeyError, one clean), while both juju 4.x attempts succeeded. The unguarded `relation.data[unit]` access is present in the code at both `upgrade.py:681` and `core/cluster.py:315-316`; the difference may be in how eagerly juju syncs relation databags for newly joined units.
2. Does JWT/OAuth integration work end-to-end? No integration test covers either; code paths exist in `events/jwt_auth.py` and `events/oauth.py` but neither was exercised against a real backend in this review, and `OAuth.uses_trusted_ca` blocks synchronously for up to 10 seconds (see finding above).
3. What is the actual upgrade behavior across revisions? `juju refresh` could not be tested — only one revision exists for the K8s charm (rev 3 on 2/edge). The VM charm has multiple revisions (2/stable rev 66, 2/edge rev 76), but the LXD run in this review never reached active with opensearch in time to test refresh. `pre-upgrade-check`/`resume-upgrade` returned correct results in isolation only.
4. Does config re-render when nothing changed? `config_changed()` (`config.py:62`) compares loaded vs. computed dashboard properties, and `emit_restart()` returns early if identical (`base.py:171`, "OpenSearch Dashboards is healthy and config is same, not restarting") — confirmed correct on the VM deployment, where repeated identical `juju config` calls didn't trigger unnecessary restarts.
5. Does the juju 3.6 LXD deployment eventually recover? Opensearch snap install was still in progress when that run ended. Based on the equivalent juju 4.x LXD observation, recovery is expected once opensearch provides CA data, but the full cycle was never directly observed on juju 3.6 LXD (unverified for that specific combination).
