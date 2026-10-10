# alertmanager-k8s-operator

A mature, well-structured Kubernetes charm for Prometheus Alertmanager, a core component of the Canonical Observability Stack. It uses a clean reconciler pattern (`_common_exit_hook`), extensive charm-library integration, and has good unit test coverage (77 passed, 3 skipped, 4 xfailed; ruff/pyright clean). Runtime testing across two Juju versions, failure injections, a scale lifecycle, and TLS integration surfaced a consistent theme: config validation failures land the charm in `error` state instead of `BlockedStatus`, forcing operators to run `juju resolve`; several values passed into `WorkloadManager` (`peer_netlocs`, `web_external_url`, `cafile`) are frozen at `__init__` time instead of recomputed, causing stale cluster peers after scale-down, wrong URL scheme after TLS arrives, and no CA verification once TLS is enabled; TLS private key material is written world-readable (0644), persists after the certificates relation is removed, and leaks through the `show-config` action — including, most seriously, on fresh deploys with **no** TLS relation configured at all; and the integration test suite has real gaps (all rescale tests `xfail`, upgrade and persistence tests entirely skipped). A maintainer should first fix the two config-validation bugs (unhandled `yaml.YAMLError`, discarded `amtool` check-config result) so bad config produces `BlockedStatus` instead of `error`, then investigate why key material is generated before any TLS relation exists — that is a live secrets-hygiene issue, not just a lifecycle bug. The charm is production-ready for a single unit running a valid, static config; HA clustering, TLS churn, and cross-track upgrades are all under-tested and buggy.

| | |
|---|---|
| Repo | canonical/alertmanager-k8s-operator @ `5272150` (2026-07-13) |
| Charms | alertmanager-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5) and concierge-k8s-3 (Juju 3.6.25), charmhub `1/edge` rev 180 (alertmanager 0.27.0) |
| Reviewed | 2026-07-27 |

## What it does

Deploys Prometheus Alertmanager (0.27.0–0.31 depending on track) on Kubernetes. Supports:
- HA clustering via Juju scale-out (peer relation with `--cluster.peer` arguments)
- Configuration via local `config_file`/`templates_file` config options, or a remote-configuration relation
- TLS via the `certificates` relation (tls-certificates v4)
- Ingress via traefik (`IngressPerAppRequirer` v2)
- Self-monitoring: Prometheus scrape jobs, Grafana dashboards, Prometheus alert rules
- Grafana source, Karma dashboard, and Catalogue integrations
- Workload tracing via Tempo (OTLP HTTP), charm tracing via `ops_tracing`
- Log forwarding via Loki (`LogForwarder`)
- Service mesh via istio-beacon
- K8s resource limits on CPU/memory

## Deployment log

**First deployment — Juju 4.0.5**
Controller: `concierge-k8s-4` (Juju 4.0.5, k8s cloud). Model: `rv-alertmanager-k8s`. Channel: charmhub `1/edge`, revision 180 (alertmanager 0.27.0, base ubuntu@20.04).

```
juju switch concierge-k8s-4
juju add-model rv-alertmanager-k8s
juju deploy alertmanager-k8s --channel 1/edge --trust
```
Deployed successfully, reached active/idle in ~2 minutes. Deploying `0.31/edge` (the HEAD track, ubuntu@26.04) failed: "the charm defined bases ubuntu@26.04 not supported" — neither controller supports 26.04.

**Second deployment — Juju 3.6.25**
Controller: `concierge-k8s-3` (Juju 3.6.25, k8s cloud). Model: `rv-am-36`. Same channel/revision. Reached active/idle in ~1 minute.

Local HEAD is track 0.31 on ubuntu@26.04; behaviour differences could exist between tracks, but the core code structure is shared and all bugs below reproduced identically on both Juju versions and across several fresh deploys.

**Cross-channel refresh:** `juju refresh --channel 1/stable` reports "already up-to-date" (rev 180 is the only revision published on all `1/` channels). Refresh to `2/edge` or `0.31/edge` is rejected on base mismatch (20.04 vs 24.04/26.04). Operators on the `1/` track (20.04) have no upgrade path.

**Application removal (Juju 3.6):** `juju remove-application alertmanager-k8s --force --no-wait --destroy-storage` completed cleanly — pod, PVC, and namespace removed without the charm needing an explicit `_on_remove` handler. No stuck resources or orphaned secrets observed.

**Fresh-deploy key-file investigation (Juju 4.x and 3.6, three separate deploys):** On every fresh deploy with **no TLS relation ever configured**, the workload container had `/etc/alertmanager/alertmanager.key.pem` (1675 bytes, mode 0644) containing a real RSA private key, plus `alertmanager-web-config.yml` referencing non-existent cert/key files. A Juju secret labeled `cert-handler-private-vault` was created on the unit (via `juju secrets`) despite the TLS library logging "No 'certificates' relation found. Cannot generate csr." The Pebble command correctly omitted `--web.config.file=`.

**grafana-agent-k8s integration (self-metrics-endpoint):** Related `grafana-agent-k8s` (0.40/edge rev 233, ubuntu@24.04). Relation data was correctly populated: `scrape_jobs` (single target on the alertmanager unit), `alert_rules` (Watchdog, AlertmanagerConfigurationReloadFailure, AlertmanagerJobMissing, AlertmanagerNotificationsFailed, HostDown, HostMetricsMissing), and `scrape_metadata`. grafana-agent-k8s itself sat in `blocked` without a `send-remote-write` relation, unrelated to alertmanager-k8s.

**self-signed-certificates TLS test:** `juju relate alertmanager-k8s self-signed-certificates` enabled TLS correctly (`--web.config.file=` appeared in the Pebble command). But: `--web.external-url` stayed `http://`; key file was 0644; `show-config` returned the full private key; `cos-ca.crt` was written to `/usr/local/share/ca-certificates/`; cert file 1402 bytes, key file 1679 bytes, both root:root 0644.

**TLS relation removal:** `juju remove-relation self-signed-certificates alertmanager-k8s` — cert and CA cert (`cos-ca.crt`) were correctly deleted; `alertmanager.key.pem` (1675 bytes, 0644) and `alertmanager-web-config.yml` persisted; `show-config` continued to return the private key. A new Juju secret created during the relation lifecycle could not be confirmed as cleaned up (access restricted).

**Workload process kill:** `kill -TERM` on the alertmanager PID — Pebble auto-restarted within ~5 seconds (PID 8660 → 8744). The charm remained `active` throughout with no detection of the crash/restart.

**3-unit cluster scale test (Juju 3.6):** Deployed 3 units; all correctly formed a cluster (each with `--cluster.peer=` for the other two). After `juju scale-application alertmanager-k8s 1`: unit 0's Pebble plan still showed `--cluster.peer=` for both departed units; alertmanager logged `cluster.go:263 msg="failed to join cluster"` then `cluster.go:473 msg=refresh result=failure` every 10–15 seconds per departed peer, indefinitely; `--cluster.listen-address=0.0.0.0:9094` persisted on the single unit; gossip took 14 seconds to settle before the refresh failures began. No self-healing — only a subsequent `config-changed` cleared the stale peers.

**Config changes:**
- Valid `config_file` → reloaded correctly via HTTP POST, verified via `kubectl exec ... cat /etc/alertmanager/alertmanager.yml`.
- Bad YAML (`config_file="this: is: not: valid: [yaml"`) → hook error (`yaml.scanner.ScannerError`), charm went to `error` status on both Juju versions. Recovery required `juju resolve` after fixing the config.
- Valid YAML, invalid Alertmanager route (undefined receiver) → also a hook error, not `BlockedStatus`. `amtool check-config` correctly flags it, but the charm discards the result (see finding below).
- Invalid Go template (`templates_file='{{ define "test" }}unclosed'`) → hook error; alertmanager logged `failed to parse templates: template: templates.tmpl:1: unexpected "}" in define clause`; recovery required clearing the template and `juju resolve`.
- Empty `config_file` and a large 33KB/100-route config were both accepted without issue.
- Duplicate YAML keys in the route section also produced a hook/error state.

**Scale-out/back (both Juju versions):**
```
juju add-unit alertmanager-k8s --num-units 1   # → 2 units, cluster formed correctly
juju scale-application alertmanager-k8s 1      # → 1 unit, stale --cluster.peer left
```
Stale peer references self-correct only on the next unrelated event that triggers `_common_exit_hook` (e.g. a config change). Self-metrics-endpoint scrape targets also continued to list the departed unit.

**Pod kill and service stop:**
- `kubectl delete pod`: pod recreated, charm recovered to active/idle in ~40 seconds, no operator action needed. The stale `--cluster.peer=` reference survived pod deletion (it comes from Juju peer-relation data, not pod state); only a later `config-changed` cleared it.
- `pebble stop alertmanager`: service went `inactive`; charm continued reporting `active/idle` for 30+ seconds with no sign of detecting the outage.

**Ingress relation:** `traefik-k8s` itself failed to start (unrelated resource issue), but the alertmanager-side ingress relation data (`host`, `ip`, `model`, `name`, `port`, `strip-prefix`, `redirect-https`) was populated correctly.

**Actions:** `show-config` returns all manifest file contents including private key material, both while TLS is active and after removal (because the key file persists), and even on a fresh deploy with no TLS relation at all. `check-config` runs `amtool check-config` correctly and reported SUCCESS/FAILURE as expected in testing.

**karma-k8s / loki-k8s:** could not be deployed on the 20.04 controllers (require ubuntu@24.04); not tested.

## Observed behaviour

1. Startup time: ~2 minutes to active/idle on Juju 4.x, ~1 minute on Juju 3.6.
2. Pebble service `alertmanager` starts `enabled`, startup only.
3. Resource usage not measured (`kubectl top pod` unavailable on these clusters).
4. Config hot-reload uses HTTP POST to `/-/reload`; when TLS arrived after startup, the reload failed because the client still used `http://` against a now-HTTPS server.
5. Each config/relation change triggered one `config-changed` hook; no hook storms observed. Pebble logs did show 4 config reloads during initial startup (wasteful, not harmful).
6. Default config uses a `placeholder` receiver — active but non-functional until the operator supplies real config. Documented behaviour.
7. TLS private key permissions: 0644 (world-readable) on both Juju versions.
8. `show-config` leaks the private key in its output, including after TLS removal (file persists) and on deploys with no TLS relation configured at all.
9. Juju 4 shows ports (9093-9094/tcp) in `juju status`; Juju 3.6 does not — expected framework difference, no charm-level behaviour difference.
10. Dead workload not detected: `pebble stop alertmanager` leaves the charm reporting `active` indefinitely; no health check exists.
11. Stale self-scraping targets after 2→1 scale-down persist until the next event that rebuilds the peer list.
12. `--cluster.listen-address=0.0.0.0:9094` stays open on the single surviving unit after the last peer departs.
13. Recovering from a config-induced `error` state requires a manual `juju resolve` even after the underlying config is fixed.
14. Reload-over-HTTPS failure after TLS arrives is caused by two frozen values: `cafile` (no CA verification) and `web_external_url` (wrong scheme).
15. `grafana-agent-k8s` self-metrics-endpoint integration populates `scrape_jobs`, `alert_rules`, `scrape_metadata` correctly.
16. Stale-peer log spam: `cluster.go:473` warnings fire every ~15 seconds indefinitely after scale-down, until a `config-changed` (or similar) event rebuilds the Pebble layer.
17. Pod recreation does not clear stale peers — the address comes from Juju peer-relation data, which is only refreshed on a relation event.
18. After a config-changed fix clears the stale peer, `--cluster.listen-address=` is emitted with an empty value rather than omitted — alertmanager tolerates it, but it is untidy.
19. Key file and web-config file exist on disk on fresh single-unit deploys with no TLS relation at all; a Juju secret `cert-handler-private-vault` is created despite the TLS library logging that no `certificates` relation exists.
20. No cross-channel upgrade path exists from the `1/` (ubuntu@20.04) track to `2/` or `0.31/` (24.04/26.04).
21. Pebble auto-restarts the workload within ~5 seconds of a `SIGTERM`; the charm neither detects the crash nor the restart.
22. `RemoteConfigurationRequirer._alertmanager_config` (`lib/charms/alertmanager_k8s/v0/alertmanager_remote_configuration.py:207`) calls `yaml.safe_load()` without catching `yaml.YAMLError`, while `RemoteConfigurationProvider.load_config_file()` (line 389, same file) does catch it — an inconsistency within the same library.

Items 2, 3, 7, 8, 9–21 could not be established from code alone; they required live deployment.

## Findings

### Unhandled YAML parse exception causes hook error instead of `BlockedStatus`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:422` (`_get_local_config`)
- **Evidence**: `local_config = yaml.safe_load(cast(str, config))` has no try/except for `yaml.YAMLError`. Setting `config_file="this: is: not: valid: [yaml"` propagates an unhandled exception through `_get_raw_config_and_templates()` → `_render_manifest()` → `_update_workload_config()` → `_common_exit_hook()`, causing a hook failure and `error` status. Observed live on both Juju versions: `yaml.scanner.ScannerError: mapping values are not allowed here`.
- **Impact**: Invalid YAML should produce `BlockedStatus("Invalid YAML in config_file: ...")`. Instead the charm crashes into `error` state, requiring `juju debug-log` to diagnose and `juju resolve` to recover even after the config is fixed.
- **Fix**: Wrap `yaml.safe_load()` in try/except, catch `yaml.YAMLError`, and raise `ConfigUpdateFailure` (already caught and converted to `BlockedStatus` by `_update_workload_config`).
- **Linter rule**: "hook handler calls `yaml.safe_load()` on user-supplied config without try/except for `YAMLError`" — mechanically checkable by tracing `self.config[...]` through `yaml.safe_load()`.

### `check_config()` silently swallows `amtool` validation failures
- **Severity**: high
- **Kind**: bug
- **Where**: `src/alertmanager.py:177` (`check_config`), `src/alertmanager.py:276`/`297` (`update_config`)
- **Evidence**: `check_config()` runs `amtool check-config`, catches `ExecError`, and returns `(stdout, stderr)` as a tuple instead of raising. `update_config()` calls `check_config()` and **discards the return value**; it only catches `WorkloadManagerError`, which `check_config()` never raises for a validation failure (only `ContainerNotReady`). With valid YAML but an invalid Alertmanager route (e.g. undefined receiver), `amtool` returns exit 1 with the exact error, but the charm never sees it — the config is pushed to disk, alertmanager crashes at runtime, the reload POST fails, and the charm ends in `error` state. Confirmed live on both Juju versions.
- **Impact**: Same class of harm as the YAML bug, arguably worse since `amtool` already hands the charm the precise error message and it is thrown away.
- **Fix**: Raise `WorkloadManagerError` from `check_config()` when stderr is non-empty, or check the return value in `update_config()` and raise `ConfigUpdateFailure` when stderr is present.
- **Linter rule**: "result of `check_config()` is discarded without inspecting stderr" — mechanically checkable by tracking call sites.

### Stale peer references after scale-down — no `relation_departed` handler on the peer relation
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:264-267` (peer `relation_joined`/`relation_changed` observers, no `relation_departed`), `src/alertmanager.py:196-215` (layer generation uses frozen `_peer_netlocs`)
- **Evidence**: After scaling 2→1 (and 3→1), the surviving unit's Pebble plan still shows `--cluster.peer=` for departed units. Alertmanager continuously tries to reach the dead peer(s); confirmed on both Juju versions and with a 3-unit cluster. Log spam (`cluster.go:473 refresh result=failure`) recurs every 10-15 seconds indefinitely until an unrelated event (e.g. `config-changed`) rebuilds the layer. `kubectl delete pod` does not clear it — the address is sourced from Juju peer-relation data, not pod state.
- **Impact**: Continuous failed connection attempts, warn-level log spam causing alert fatigue in monitoring systems, wasted network resources, and (via the same missing handler) stale self-metrics-endpoint scrape targets and an open `--cluster.listen-address=0.0.0.0:9094` on single-unit deployments.
- **Fix**: Observe `relation_departed` on the peer relation and trigger the same layer-rebuild path as `relation_joined`/`relation_changed`.
- **Linter rule**: "charm observes `relation_joined`/`relation_changed` on a peer relation without also observing `relation_departed`" — mechanically checkable.

### TLS private key material generated and pushed to the workload even with no TLS relation configured
- **Severity**: high
- **Kind**: security / bug
- **Where**: `src/charm.py:96` (key path constant), `src/charm.py:463-466` (unconditional `set_tls_server_config` call in `_render_manifest`)
- **Evidence**: On three separate fresh deployments (two Juju 4.x, one Juju 3.6) with zero TLS relations, `/etc/alertmanager/alertmanager.key.pem` existed (1675 bytes, mode 0644) containing a real `-----BEGIN RSA PRIVATE KEY-----`. A Juju secret labeled `cert-handler-private-vault` was created despite the TLS library logging "No 'certificates' relation found. Cannot generate csr." `alertmanager-web-config.yml` also existed, referencing the non-existent cert file. `ConfigBuilder.set_tls_server_config()` is called unconditionally regardless of whether `_tls_config` is set.
- **Impact**: Private key material is created and persisted (both on disk, world-readable, and in Juju secret storage) before TLS is ever configured, violating least-privilege. If TLS is later enabled and this key is superseded, the original key remains in secret storage indefinitely.
- **Fix**: Make `set_tls_server_config()` conditional on `self._tls_config` being set; only push key/cert/web-config files when TLS is actually available. Investigate whether the TLS library or `CertificateTransferRequires` is creating the secret unconditionally.
- **Linter rule**: not mechanically checkable (requires runtime observation).

### `show-config` action leaks private key material
- **Severity**: high
- **Kind**: security / bug
- **Where**: `src/charm.py:368-395` (`_on_show_config_action`)
- **Evidence**: The action iterates over all manifest files and returns their contents unfiltered. Confirmed leaking the RSA private key: (a) while TLS is active, (b) after the certificates relation is removed (key file persists — see next finding), and (c) on a fresh deploy with no TLS relation at all (see key-generation finding above). Confirmed on both Juju versions.
- **Impact**: Any operator or automation with `juju run` access can retrieve the private key at essentially any point in the charm's lifecycle. Action output may be logged to syslog or chatops integrations, widening the exposure.
- **Fix**: Filter files matching `*.key.pem` or containing `PRIVATE KEY` from the action output (or return a placeholder/hash), in addition to fixing the underlying key-persistence and unconditional-key-generation bugs.
- **Linter rule**: "action handler returns content from paths matching `*.key.*` without redaction" — mechanically checkable.

### TLS private key not deleted when the certificates relation is removed
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:472-480` (key path mapping in `_render_manifest`), `src/charm.py:96`, `src/charm.py:630` (`_update_ca_certs`)
- **Evidence**: After `juju remove-relation`, `alertmanager.cert.pem` was correctly deleted, but `alertmanager.key.pem` (1675 bytes, mode 0644) remained on disk on both Juju versions. The manifest correctly maps the key path to `None`, but `apply()` fails to remove the file. The TLS v4 library only exposes a `certificate_available` event — no removal/revocation event — so cleanup relies on a `config-changed` side effect that appears incomplete for the key specifically.
- **Impact**: Private key material persists indefinitely on disk after TLS is de-provisioned, remains world-readable, and continues to leak via `show-config`.
- **Fix**: Investigate why `container.remove_path()` for the key path doesn't take effect (Pebble timing, or the key being re-created elsewhere). Add a `relation_broken` observer on the certificates relation to force cleanup explicitly rather than relying on the `config-changed` side effect.
- **Linter rule**: not mechanically checkable (requires runtime observation).

### Entire upgrade and persistence integration test suites are skipped
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/integration/test_upgrade_charm.py:24`, `tests/integration/test_persistence.py:20`
- **Evidence**: Both files set `pytestmark = pytest.mark.skip(reason="Cross-base upgrade from 24.04 to 26.04 not supported")`, skipping every test in the module — including tests that would exercise same-base `juju refresh` and silence persistence across upgrades. No automated test verifies the upgrade path at all.
- **Impact**: The charm publishes 4 tracks across different bases; operators may need to move between them, but `juju refresh` behaviour (including within a track, per the manual cross-channel-refresh test above) is completely untested.
- **Fix**: Add a same-base upgrade test (e.g. refresh within one track on a matching-base controller), or implement/document cross-base upgrade support and its limitations.
- **Linter rule**: not mechanically checkable.

### `--web.external-url` scheme doesn't update when TLS becomes available after startup
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:225` (WorkloadManager constructed with frozen `_external_url`), `src/alertmanager.py:98-131` (`WorkloadManager.__init__` stores `web_external_url` as a frozen string)
- **Evidence**: `WorkloadManager` receives `web_external_url=self._external_url`, computed once at `AlertmanagerCharm.__init__` time, when TLS is not yet available (`_tls_available` is False at init, so the property returns `http://...`). When TLS later arrives, the Pebble layer is rebuilt but the frozen string is unchanged. Observed in the Pebble plan: `--web.external-url=http://alertmanager-k8s-0...` alongside `--web.config.file=`.
- **Impact**: Alertmanager's generated links (notifications, web UI, `--web.route-prefix`) use the wrong scheme once TLS is enabled; the reload-over-HTTP-vs-HTTPS mismatch also caused reload POST failures in testing.
- **Fix**: Pass a callable for `web_external_url` to `WorkloadManager`, matching the pattern already used for `tls_enabled`, or recompute it in `_alertmanager_layer()` from current charm state.
- **Linter rule**: "`WorkloadManager` receives a computed property value at construction time that can change during the charm lifecycle" — partially checkable by looking for `self._<property>` values passed as constructor args.

### `Alertmanager` HTTP client `cafile` frozen at `WorkloadManager` init time
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:225`, `src/alertmanager.py:98-131` (`cafile` stored at `alertmanager.py:127`)
- **Evidence**: `cafile=self._ca_cert_path if Path(self._ca_cert_path).exists() else None` is evaluated eagerly at charm `__init__` time, before the certificates relation typically forms. The resulting `Alertmanager` client's SSL context is created with `cafile=None` and never updated, so it does not verify the server certificate even once TLS is enabled. Same frozen-value-at-init pattern as `web_external_url` and `peer_netlocs`.
- **Impact**: The HTTP client used for reload/status/config calls performs no certificate verification against an HTTPS Alertmanager, undermining the point of enabling TLS.
- **Fix**: Recreate the `Alertmanager` client when TLS configuration changes, or pass `cafile` as a callable.
- **Linter rule**: same as the `web_external_url` finding.

### Missing peer `relation_departed` also leaves stale self-scraping targets
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:322-332` (`self_scraping_job`), `src/charm.py:664-679` (`_get_peer_hostnames`)
- **Evidence**: `self_scraping_job` calls `_get_peer_hostnames(include_this_unit=True)`, reading `pr.data[unit].get("private_address")` from peer relation data. Confirmed live: after scaling 2→1, `juju show-unit` showed `scrape_jobs` on `self-metrics-endpoint` still listing both units.
- **Impact**: Prometheus attempts to scrape a departed unit and fails, generating false-positive `HostDown`/`HostMetricsMissing` alerts.
- **Fix**: Same fix as the stale-peer finding — add the `relation_departed` handler.
- **Linter rule**: same as the stale-peer finding.

### TLS private key has world-readable permissions (0644)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/alertmanager.py:45-48` (`ConfigFileSystemState.apply`)
- **Evidence**: The key file at `/etc/alertmanager/alertmanager.key.pem` was written with mode 0644 on every deploy tested, confirmed via `kubectl exec ... -- stat`. `container.push()` is called without restricting permissions on the key.
- **Impact**: Any process in the workload container (or a shared volume) can read the TLS private key.
- **Fix**: `chmod 600` the key file after pushing it, e.g. via `container.exec(['chmod', '600', path])` in `ConfigFileSystemState.apply()` for paths matching a key pattern.
- **Linter rule**: "`container.push()` for files matching `*.key.pem` without a subsequent `chmod 600`" — mechanically checkable.

### Manual `juju resolve` required to recover from `error` state even after fixing config
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:508-558` (`_common_exit_hook`), Juju error-state semantics
- **Evidence**: When the charm enters `error` state (bad YAML, invalid template, or bad Alertmanager config), a valid `juju config` change does not trigger a new hook — Juju holds hooks on error-state units until `juju resolve` is run. Confirmed on both Juju versions; a typo requires two commands (`juju config` + `juju resolve`) to recover.
- **Impact**: Partly Juju framework behaviour, but the charm's own config-validation bugs are the root cause of entering `error` state in the first place.
- **Fix**: Primary fix is the YAML/template/`amtool` validation fixes above, so the charm produces `BlockedStatus` instead of crashing.
- **Linter rule**: not mechanically checkable.

### Invalid Go template syntax causes a hook error, not `BlockedStatus`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:436-449` (`_get_raw_config_and_templates`), `src/config_builder.py:71-76` (`set_templates` called unconditionally)
- **Evidence**: Setting `templates_file='{{ define "test" }}unclosed'` writes the template to disk unvalidated; alertmanager fails to parse it at runtime (`failed to parse templates: template: templates.tmpl:1: unexpected "}" in define clause`), the reload POST fails, and the hook crashes via the same `_common_exit_hook` → `_update_workload_config` → `reload()` path as the YAML bug. Confirmed live on Juju 4.x.
- **Impact**: Same class as the YAML/`amtool` bugs — a config validation failure should produce `BlockedStatus`, not a hook error requiring `juju resolve`.
- **Fix**: Run `amtool check-config` before reloading and reject invalid configs (fixing this and the amtool-discard bug together), or validate Go template syntax in Python before pushing.
- **Linter rule**: not mechanically checkable.

### Dead workload not detected — charm reports active while service is stopped
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:508-558` (`_common_exit_hook`)
- **Evidence**: After `pebble stop alertmanager`, the Pebble service went `inactive` but the charm continued reporting `active/idle` for 30+ seconds (and presumably indefinitely). `_common_exit_hook` sets `ActiveStatus` unconditionally without checking whether the service is running. Killing the process directly (`kill -TERM`) produced the same result: Pebble auto-restarted within ~5 seconds and the charm never noticed either the crash or the restart.
- **Impact**: If alertmanager crashes silently or Pebble exhausts its restart budget, `juju status` still shows `active` and operators are not alerted.
- **Fix**: Check `container.get_service(self._service_name).is_running()` in `_common_exit_hook` and set `BlockedStatus` if the service is not running.
- **Linter rule**: not mechanically checkable.

### Remote-configuration library has an unguarded `yaml.safe_load()`
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/alertmanager_k8s/v0/alertmanager_remote_configuration.py:207-230` (`_alertmanager_config`, `yaml.safe_load` at line 225)
- **Evidence**: The try/except around `yaml.safe_load(config_raw)` catches `KeyError` but not `yaml.YAMLError`. `RemoteConfigurationProvider.load_config_file()` (line 389, same file) does catch `yaml.YAMLError` — an inconsistency within the same library.
- **Impact**: A misconfigured remote-configuration provider charm sending invalid YAML over the relation can crash the alertmanager-k8s requirer with an uncaught exception, producing the same class of hook-error/`error`-state problem as the local config bug.
- **Fix**: Catch `yaml.YAMLError` in `_alertmanager_config` and return `None` (or raise a library-specific exception) instead of letting it propagate.
- **Linter rule**: "`yaml.safe_load()` called on relation data without try/except for `YAMLError`" — mechanically checkable by tracing relation-data reads through `yaml.safe_load()`.

### `_render_manifest` always writes a web config referencing cert/key paths even without TLS
- **Severity**: low
- **Kind**: bug / correctness
- **Where**: `src/config_builder.py:140-150`, `src/charm.py:387-391`/`463-466`
- **Evidence**: `ConfigBuilder.set_tls_server_config()` is always called with cert/key paths regardless of whether TLS is configured, so `_web_config` is always non-None and the manifest always includes `alertmanager-web-config.yml`. When TLS is disabled the cert/key files don't exist, but the web-config file does, referencing them. Pebble correctly omits `--web.config.file=` in this case, so it is currently harmless, but ties directly into the unconditional key-generation finding above.
- **Impact**: Confusing artifact for operators inspecting the container; a future change that starts using `--web.config.file=` unconditionally would break startup.
- **Fix**: Only generate the web config when `self._tls_config` is set.
- **Linter rule**: not mechanically checkable.

### `--cluster.listen-address=0.0.0.0:9094` left open, or emitted empty, on single-unit deployments
- **Severity**: low
- **Kind**: bug
- **Where**: `src/alertmanager.py:200-215` (`_command` inner function, `listen_netloc_arg`)
- **Evidence**: Because `peer_netlocs` is frozen at init from a stale peer list, the cluster port remains open after scale-down until a layer rebuild. Once rebuilt, `listen_netloc_arg` becomes `""` for zero peers, producing `--cluster.listen-address=` (empty value) instead of omitting the flag — observed in the Pebble plan. Alertmanager 0.27.0 tolerates the empty value but this is fragile.
- **Impact**: Minor security-hygiene issue (port left listening) and untidy command line that could break on a future alertmanager version.
- **Fix**: Pass `peer_netlocs` as a callable (same fix as the stale-peer finding) and make the flag conditional at the template level so it's omitted entirely when there are no peers.
- **Linter rule**: same as the stale-peer finding.

### All rescale integration tests are `xfail`
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_rescale_charm.py` (all 4 tests)
- **Evidence**: `test_deploy`, `test_scale_down_to_single_unit`, `test_scale_up_by_two`, and `test_scale_down_by_two` are all decorated `@pytest.mark.xfail`.
- **Impact**: Rescale is a basic lifecycle operation; xfailing the whole suite means the stale-peer bug is acknowledged but not fixed, and there is no regression guard.
- **Fix**: Fix the missing `relation_departed` handler, then remove the `xfail` marks.
- **Linter rule**: not mechanically checkable.

### `alertmanager_client.py` helper methods silently swallow all HTTP errors
- **Severity**: low
- **Kind**: bug
- **Where**: `src/alertmanager_client.py:169-243` (`_post`, `_delete`, `_get`)
- **Evidence**: `_post()`, `_delete()`, and `_get()` catch `urllib.error.HTTPError`, `URLError`, and `TimeoutError`, log at DEBUG, and return empty bytes on failure. `_open()` (used by `reload()`, `status()`, `config()`) properly raises `AlertmanagerBadResponse` instead. `set_alerts()`, `get_alerts()`, `set_silences()`, `get_silences()`, and `delete_silence()` all silently return empty results on any HTTP error.
- **Impact**: Callers cannot distinguish "no alerts" from "failed to contact alertmanager"; e.g. the alerting provider library's `set_alerts()` gives no signal if alertmanager is unreachable.
- **Fix**: Follow the `_open()` pattern — raise on failure, or return a result type that distinguishes success from failure.
- **Linter rule**: not mechanically checkable.

### TLS v4 library does not observe `relation_broken` on the certificates relation
- **Severity**: low
- **Kind**: design note
- **Where**: `lib/charms/tls_certificates_interface/v4/tls_certificates.py:1758-1761`
- **Evidence**: The v4 requirer library observes `relation_created`, `relation_changed`, `secret_expired`, and `secret_remove`, but not `relation_broken`/`relation_departed`. The charm itself also does not observe these on the certificates relation, relying on a `config-changed` side effect for cleanup.
- **Impact**: Likely root cause of the key-persistence-after-removal bug — cleanup timing/ordering is not guaranteed.
- **Fix**: Add a `relation_broken` observer on the certificates relation that explicitly triggers cleanup, or request that the TLS library emit a `certificate_removed` event.
- **Linter rule**: not mechanically checkable.

### Flapping risk: unordered iteration over `ca_certs` (open issue #449)
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:640`
- **Evidence**: `ca_certs = self._cert_transfer.get_all_certificates()` returns an unordered collection; `for i, cert in enumerate(ca_certs)` assigns position-dependent file names, so `has_changes()` can return True on order changes alone, triggering unnecessary reloads. Open issue #449 confirms this.
- **Impact**: Config churn (reload on every hook) when certificates arrive in different order.
- **Fix**: Sort certificates before enumerating.
- **Linter rule**: "position-dependent value from unordered data" — flaplint already checks this.

### Inconsistency: `relation_departed` observed for `ingress` but not for the peer relation
- **Severity**: low
- **Kind**: correctness
- **Where**: `src/charm.py:185` (ingress `relation_departed`), `src/charm.py:264-267` (peer relation observers without `relation_departed`)
- **Evidence**: The charm observes `self.on["ingress"].relation_departed` and `self.on["tracing"].relation_broken`, but not the equivalent on the peer relation.
- **Impact**: Confirms the missing peer handler is an oversight rather than a deliberate design choice.
- **Fix**: Add the peer `relation_departed` observer (same fix as the stale-peer finding).
- **Linter rule**: same as the stale-peer finding.

### 4 xfailed unit tests nominally cover the `web-external-url` scheme bug, but the mock data is broken
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_server_scheme.py:51` (3 parametrized cases), `:93` (1 case)
- **Evidence**: `test_pebble_layer_scheme_becomes_https_if_tls_relation_added` is `xfail` for 3 of 4 parameter combinations, plus one case of `test_alerting_relation_data_scheme`. Test logs show the failures are actually due to a `MalformedFraming` error loading the mock certificate in the TLS library, not the scheme-switching code the test intends to exercise — the test never reaches the charm code under test.
- **Impact**: The `xfail` gives false confidence: it looks like the scheme bug is tracked and test-guarded, but fixing the mock cert alone (without fixing the real bug) would make the test start passing — a false negative.
- **Fix**: Fix the mock certificate data so the test actually parses and reaches the scheme-switching code; only then should it be genuinely `xfail`ed pending the real fix.
- **Linter rule**: not mechanically checkable.

### README documents deprecated `juju run-action ... --wait`
- **Severity**: low
- **Kind**: docs
- **Where**: `README.md` (rendered ~line 91), open issue #429
- **Evidence**: README says `juju run-action alertmanager-k8s/0 show-config --wait`; `juju run-action` and `--wait` were removed in Juju 3.x. Correct form is `juju run alertmanager-k8s/0 show-config`. Issue #429 (filed 2026-06-21) confirms this is known but unfixed.
- **Impact**: New operators on Juju 3.x/4.x get an unrecognized-command error on their first `show-config` attempt.
- **Fix**: Update the README to `juju run alertmanager-k8s/0 show-config`.
- **Linter rule**: "README contains `juju run-action`" — mechanically checkable via grep.

### CONTRIBUTING.md references a non-existent `tox -e integration-lma`
- **Severity**: low
- **Kind**: docs
- **Where**: `CONTRIBUTING.md:57`
- **Evidence**: Says `tox -e integration-lma  # integration tests for the lma-light bundle`, but `tox.ini` has no such environment (grep confirms zero matches).
- **Impact**: Contributor confusion.
- **Fix**: Remove the line or add the environment.
- **Linter rule**: not established.

### codespell: typo in docstring (`interal` → `internal`)
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:717`
- **Evidence**: `codespell` flags `src/charm.py:717: interal ==> internal` in the `_service_url` docstring ("the interal FQDN for the socket").
- **Impact**: Trivial but caught by tooling not yet integrated into CI.
- **Fix**: Correct the spelling.
- **Linter rule**: `codespell` already catches this — add it to CI.

## Worth copying

1. **Clean reconciler pattern** (`src/charm.py:508-558`): `_common_exit_hook()` is the single reconciliation entry point called by every event handler — guard checks, relation-data updates, config re-render, Pebble layer update, reload, status, all in one ordered sequence. Worth adopting over scattered per-event logic.
2. **`ConfigFileSystemState`** (`src/alertmanager.py:30-69`): a small class representing desired filesystem state as `path → content` (`None` = delete), with `has_changes()` and `apply()`. Clean idempotent config-file management pattern.
3. **`ConfigBuilder` fluent API** (`src/config_builder.py`): builder pattern with chained `.set_config().set_tls_server_config().set_templates().build()` and a frozen `ConfigSuite` dataclass output. Clean separation of config generation from lifecycle.
4. **`WorkloadManager` as an `ops.Object`** (`src/alertmanager.py:85`): registers its own Pebble-ready/stop observers and is independently testable from the charm.
5. **`Alertmanager` HTTP client** (`src/alertmanager_client.py`): focused client with retry logic (3 attempts, 200ms sleep) and a clean `_open()` implementation (`reversed(range(3))`).
6. **Action design**: `show-config` and `check-config` are genuinely useful diagnostic actions (security issues aside).
7. **Comprehensive relation integrations**: tracing, logging, service mesh, catalogue, ingress, TLS — each handled via a dedicated library object rather than inline code.
8. **`justfile` for developer workflow**: minimal, with `import? 'charms.just'` for shared recipes.

## Common-practice notes

- Follows convention: `src/` layout (`charm.py`, `<workload>.py`, `<workload>_client.py`, `config_builder.py`) matches the observability team's standard.
- Follows convention: libraries under `lib/charms/<charm>/v<N>/` with proper LIBAPI/LIBPATCH versioning.
- Follows convention: `uv` for packaging, `tox` for test environments, `just` for recipes.
- Follows convention: `charmcraft.yaml` declares `assumes: [k8s-api, juju >= 3.6]` with proper container/resource/storage declarations.
- Drifts from convention: mixes `ops` Harness (deprecated, e.g. `test_charm.py`, `test_consumer.py`) with newer Scenario-based tests (`test_server_scheme.py`, `test_workload_tracing.py`) — understandable mid-migration.
- Drifts from convention: `TLSConfig` is a dataclass defined in `src/charm.py:54` rather than in a separate types module.
- Drifts from convention: the charm passes computed values, not callables, to `WorkloadManager` for things that change over the lifecycle (`peer_netlocs`, `web_external_url`, `cafile`), while `tls_enabled` correctly uses a lambda. This single inconsistency is the root cause of five distinct runtime defects: stale peers, wrong URL scheme, stale scrape targets, cluster port left open, and no CA verification.

## Tests

**Unit tests:** 77 passed, 3 skipped, 4 xfailed. Run with `PYTHONPATH=.:lib:src uv run pytest tests/unit` after `uv sync --extra dev`. Re-run consistently across all review rounds with the same result.

- Skipped (3): `test_cluster_addresses`, `test_traefik_overrides_fqdn`, `test_multi_unit_cluster` — all skip due to upstream `ops` issue #736, not a charm bug. Notably, `test_multi_unit_cluster` would have exercised the buggy peer relation handling.
- Xfailed (4): 3 parametrized cases of `test_pebble_layer_scheme_becomes_https_if_tls_relation_added` and 1 case of `test_alerting_relation_data_scheme`, both in `test_server_scheme.py` — see the mock-cert finding above regarding whether these actually exercise the real bug.

Coverage by module: `test_charm.py` (core behaviour, pebble layer, relation data, actions — Harness), `test_server_scheme.py` (TLS/scheme, scrape jobs — Scenario), `test_workload_tracing.py` (tracing config — Scenario), `test_config_changes.py`, `test_alertmanager_client.py`, `test_consumer.py`, `test_remote_configuration_provider.py`/`_requirer.py`, `test_push_config_to_workload_on_startup.py`, `test_self_scrape_jobs.py`, `test_log_forwarding.py`, `test_external_url.py`, `test_brute_isolated.py`.

**Coverage gaps identified:**
- No test for `config_file` containing invalid YAML (the unhandled `yaml.YAMLError`); `TestInvalidConfig` in `test_push_config_to_workload_on_startup.py` uses valid YAML with an `amtool` failure and mocks `check_config` to always succeed, so the real `amtool` validation path is never exercised.
- No test for the `amtool` result being discarded in `update_config()`.
- No test for invalid Go template syntax causing hook errors.
- No test for the peer `relation_departed` handler (because there is no handler).
- No test for TLS key cleanup after relation removal.
- No test for `show-config` redacting or leaking key material.
- No test for dead-workload detection.
- No test for `cafile`/`peer_netlocs` being recomputed on relation changes.

**Integration tests:** 13 files; not run (time/infrastructure constraints), but read in full.
- `test_rescale_charm.py`: all 4 tests `@pytest.mark.xfail` — rescale behaviour is known-broken.
- `test_upgrade_charm.py`, `test_persistence.py`: entirely `pytest.mark.skip` — no upgrade or cross-upgrade persistence testing exists.
- `test_tls_web.py`: covers cert existence, SAN, HTTPS reachability, post-refresh reachability — does not test TLS removal/cleanup.
- `test_kubectl_delete.py`: pod-deletion recovery, passes per code review (matches the live pod-kill test above).
- `test_logging.py`, `test_remote_configuration.py`, `test_templates.py`, `test_workload_tracing_http.py`, `test_workload_tracing_tls.py`, `test_grafana_source.py`: additional coverage, not run.
- The suite covers 8 of 12 relation types but has zero coverage for upgrade paths, rescale (xfailed), persistence across upgrades, TLS relation removal, peer departure, and `show-config` in a live setting.

**Linting:** `ruff check src/ lib/charms/alertmanager_k8s/` — 0 issues. `pyright src/` — 0 errors, 0 warnings. `codespell src/` — 1 finding (`interal` → `internal`, `src/charm.py:717`).

## Docs

- **README.md**: well-written, covers deployment, configuration, clustering, OCI images. Documents a deprecated `juju run-action ... --wait` command (issue #429).
- **INTEGRATING.md**: comprehensive integration guide with YAML snippets and `juju relate` examples for every relation.
- **CONTRIBUTING.md**: standard guide; references a non-existent `tox -e integration-lma`.
- **RELEASE.md**: release process documented with `charmcraft` and `git tag` steps.
- **terraform/README.md**: documented module with example usage, inputs, outputs.
- **charmhub description**: good feature list in `charmcraft.yaml`.
- **Doc/reality mismatch**: INTEGRATING.md and charmcraft.yaml assume HEAD (0.31 on 26.04), while the deployed/tested charm (`1/edge` rev 180) is 20.04 with alertmanager 0.27.0 — operators following current docs on older tracks may hit version differences.

## Corrections to initial review

- An earlier finding claimed `_update_ca_certs` writes CA certs outside the manifest, conflicting with `_render_manifest()`. On closer inspection, `_update_ca_certs` writes to the **charm** container filesystem (via `Path`) while `_render_manifest()` writes to the **workload** container (via `ConfigFileSystemState`) — separate filesystems, no conflict. Finding removed.
- The xfailed `test_pebble_layer_scheme_becomes_https_if_tls_relation_added` was initially described as confirming the web-external-url scheme bug. Test logs show the actual failure is a `MalformedFraming` error in the TLS library's mock-cert parsing — the test never reaches the scheme-switching code. Reclassified as a test-gap finding about the mock data, separate from (though related to) the real scheme bug, which is independently confirmed live.
- The `check_config()` finding was refined: `check_config()` catches `ExecError` and returns strings without raising; `update_config()` calls it inside a try/except for `WorkloadManagerError`, which `check_config()` only raises via `ContainerNotReady` — never for a validation failure. So the except block never fires for invalid configs, and the returned tuple is simply discarded (unassigned). Config is pushed to disk regardless of validation result.

## Open questions

1. Why does `container.remove_path()` not delete the key file when the cert file in the same manifest is cleaned up correctly? Root cause unconfirmed — would need `logger.debug` instrumentation in `ConfigFileSystemState.apply()` to settle definitively.
2. Does the TLS v4 library emit any certificate-revocation/removal event? Confirmed it only declares `certificate_available` — no revocation event exists.
3. Is the stale-peer issue also present on the `0.31/edge` track (26.04)? Only tested on `1/edge` (0.27.0, 20.04); the missing `relation_departed` handler is visible in HEAD at the same lines, but not verified on a 26.04-capable controller.
4. Should `show-config` redact sensitive values? Open issue #450 (accepting `config_file` from relation data) partially relates but doesn't resolve this.
5. Why does a real RSA private key exist on disk (and a Juju secret get created) even when TLS is never configured? Confirmed across three separate fresh deployments; the actual code path that generates the key content before any `certificates` relation exists was not pinned down — needs `logger.debug` on every `container.push()` call path in the TLS/cert-transfer libraries.
