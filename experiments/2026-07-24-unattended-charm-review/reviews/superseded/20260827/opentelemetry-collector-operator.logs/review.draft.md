# opentelemetry-collector

A mature machine subordinate charm that deploys the OpenTelemetry Collector via snaps, managing a complex web of integrations (metrics, logs, traces, profiles, dashboards, TLS) and building otelcol config from them. Code quality is high with a clean config-building architecture, comprehensive unit tests (171 passing), and thorough integration tests covering multi-unit removal, log rotation, and snap refresh. Deployed and observed on Juju 3.6.23 (Juju 4.0.5 subordinate deployment failed — both charms stuck at "agent initialising"). The charm installs cleanly and goes to sensible blocked status when missing outgoing data sinks. However, the holistic "`_reconcile` on every hook" pattern causes systemic garbage-collection of ops library objects (COSAgentRequirer, TLSCertificatesRequiresV4, OtlpRequirer, ProfilingEndpointRequirer/Provider). TLS works despite this — server cert, key, and CA cert all reach disk — but only via a fragile manual `_configure(None)` workaround; the event-based CSR lifecycle and certificate renewal are broken. On Juju 3.6 the stop hook is clean; on Juju 4.x a `config-get` traceback fires because `_reconcile` doesn't skip stop. Scale-up can trigger a snap-start failure loop when a new subordinate joins a machine where the snap is already installed. Status precedence overwrites blocked messages, hiding config errors. The `_reconcile` method (~450 lines) is overdue for the planned refactoring (issue #79).

| | |
|---|---|
| Repo | canonical/opentelemetry-collector-operator @ 9fa23d2 (2026-07-15) |
| Charms | opentelemetry-collector |
| Substrate | machine (subordinate) |
| Deployed | yes — concierge-lxd (Juju 3.6.23), charmhub 2/edge rev 347. concierge-lxd-4 (Juju 4.0.5) deployment FAILED (subordinates stuck at "agent initialising") |
| Reviewed | 2026-08-09 |

## What it does

Deploys and manages the OpenTelemetry Collector snap (and node-exporter snap) on machine substrates. As a subordinate charm, it attaches to a principal charm via `juju-info` or `cos-agent` and provides a full telemetry pipeline: metrics scraping/remote-write, log collection, trace ingestion (OTLP/Jaeger/Zipkin), profiling, dashboard forwarding, TLS, external config merging, and Grafana Cloud integration. Uses a file-based `SingletonSnapManager` to coordinate snap lifecycle when multiple subordinate units share a machine.

## Deployment log

### Round 1 — Juju 4.x (concierge-lxd-4, rv-otel-deep) — DEFINITIVE FAILURE

Three separate deploy attempts on Juju 4.0.5 all failed: subordinate charms (`opentelemetry-collector`, `grafana-agent`) remained permanently stuck at `agent initialising` / `allocating`. The principal `ubuntu` and standalone `self-signed-certificates` deployed fine. This is a Juju 4.x / LXD subordinate provisioning issue — not the charm's fault but means the charm cannot be deployed on Juju 4.x with LXD as of 2026-08-09.

### Round 2 — Juju 3.6 (concierge-lxd, rv-otel-36d): ubuntu + otelcol + grafana-agent + self-signed-certificates

```bash
juju add-model rv-otel-36d localhost/localhost --controller concierge-lxd
juju deploy ubuntu --channel stable --base ubuntu@24.04
juju deploy opentelemetry-collector --channel 2/edge
juju deploy grafana-agent --channel edge
juju deploy self-signed-certificates --channel edge
juju integrate ubuntu opentelemetry-collector
juju integrate ubuntu grafana-agent
juju integrate opentelemetry-collector:receive-ca-cert self-signed-certificates:send-ca-cert
juju integrate opentelemetry-collector:receive-server-cert self-signed-certificates:certificates
```
- Both subordinates installed on the same machine ✓
- otelcol: `blocked: ['cloud-config']|['send-loki-logs']|['send-remote-write'] for juju-info`
- grafana-agent: `blocked: Missing ['grafana-cloud-config']|['logging-consumer']|['send-remote-write']`
- Attempted `juju integrate opentelemetry-collector:cos-agent grafana-agent:cos-agent` — failed with `ERROR no relations found` (subordinate-to-subordinate cross-model integration not supported)
- Install times: otelcol snap ~70s, node-exporter ~11s
- Workload version: 0.130.0, otelcol ~100 MB RSS, 24 threads
- Observed COSAgentRequirer GC warning on every hook

### Round 3 — Juju 3.6 (concierge-lxd, rv-otel-d2): 3-unit scale + config + failure testing

```bash
juju add-model rv-otel-d2 localhost/localhost --controller concierge-lxd
juju deploy ubuntu --channel stable --base ubuntu@24.04 -n 3
juju deploy opentelemetry-collector --channel 2/edge
juju deploy self-signed-certificates --channel edge
juju integrate ubuntu opentelemetry-collector
juju integrate opentelemetry-collector:receive-ca-cert self-signed-certificates:send-ca-cert
juju integrate opentelemetry-collector:receive-server-cert self-signed-certificates:certificates
```
- All 3 subordinate units reached blocked (missing outgoing relations) after ~120s ✓
- Scale down (`juju remove-unit ubuntu/2`): clean stop hook, no traceback, otelcol/1 removed cleanly ✓
- Scale up (`juju add-unit ubuntu -n 1`): new otelcol/4 unit entered **error state** — snap start failed repeatedly (see finding #17)
- `juju remove-application opentelemetry-collector`: removal stuck because hooks were already failing; required `--force`

### Juju 3.6 versus 4.x summary

| Aspect | Juju 3.6.23 | Juju 4.0.5 |
|---|---|---|
| Subordinate deployment | ✓ works | ✗ subordinates stuck at "agent initialising" |
| Stop hook crash | ✗ No traceback (clean stop on `remove-unit`) | ✗ Traceback: `config-get` unavailable |
| Server cert + key on disk | ✓ Yes | ✗ Deployment failed |
| Server CA cert on disk | ✓ Yes (at `.../cos-ca.crt`) | ✗ Deployment failed |
| COSAgentRequirer GC warning | Observed | Not tested |

### Config changes tested

| Config change | Result |
|---|---|
| `ports="loki_http=3501"` | Port 3501 bound, snap restarted ✓ |
| `ports="invalid_port=1234"` | `BlockedStatus: Invalid ports config: Unknown port name` ✓ |
| `global_scrape_interval="invalid"` | `BlockedStatus: format requires '\d+[ywdhms]'` ✓ |
| `memory_limit_percentage="-5"` | BlockedStatus set but overwritten by missing-relations blocked (finding #4) |
| `debug_exporter_for_metrics=true` | Debug exporter added to metrics pipeline ✓ |
| `always_enable_zipkin=true` | Port 9411 opened, zipkin receiver enabled ✓ |
| `tracing_sampling_rate_workload=200` | Accepted without validation (valid range is 0-100) ✗ |
| `queue_size=-10` | Accepted without validation ✗ |
| `processors` with YAML file | Custom processors merged correctly ✓ |
| `batch_timeout` / `send_batch_size` | Unknown option (these config keys don't exist) — expected |

### Actions

Only one action: `reconcile`. Ran it — runs `update-ca-certificates`, rebuilds config, restarts snap if hash changed. Worked ✓.

### Failure injection

| Injection | Result |
|---|---|
| `kill -9 otelcol` | systemd restarted within 2s (PID changed) ✓ |
| Remove `receive-ca-cert` relation | No crash, CA cert files cleaned ✓ |
| Remove `receive-server-cert` relation | No crash, server cert + key files cleaned ✓ |
| Re-add `receive-server-cert` | Certs reappeared on disk after 15s ✓ |
| Remove `receive-server-cert`, re-add | No errors, certs materialised correctly ✓ |
| Scale up from 2→3 units | New unit hit snap-start failure loop (finding #17) ✗ |

## Observed behaviour

### Ruff results in library code (corrected from earlier claim)

The original review's first draft incorrectly claimed `All checks passed!` for Ruff based on a limited check. Running `ruff check src/ lib/ tests/` on the full codebase finds **11 fixable style violations** (RET505/RET502/RET507). All are in library code under `lib/charms/` (tls_certificates_interface v4, tempo_coordinator_k8s, certificate_transfer_interface, operator_libs_linux). The charm's own `src/` code is clean. The 11 issues are: unnecessary `else`/`elif` after `return`/`continue` (9 occurrences), implicit `None` return (2 occurrences). Pyright remains `0 errors, 0 warnings, 0 informations`.

### YAML parsing failure in bundled alert rules

The `cosl` rules parser emits an ERROR for `mdadm.rules` on every hook invocation (visible in unit test output): `ERROR cosl.rules:rules.py:374 Failed to read rules from mdadm.rules`. This means RAID-related alerts are silently dropped. The cause is three lines in the file where `description:` follows the `summary:` closing quote on the same line. This could not be seen from reading the charm code alone — it requires running the tests and watching stderr, or manually parsing the .rules files.

### Library deprecation warnings

The test output shows 118 warnings, including: `JujuVersion.from_environ()` is deprecated (tls_certificates v4), `PydanticDeprecatedSince20: The json method is deprecated` (cos_agent library, tracing library), `generate_private_key() is deprecated` (tls_certificates v4). These are in library code and will become errors when the respective packages drop the deprecated APIs.

### TLS works on Juju 3.6 — all three cert files reach disk

Despite the `TLSCertificatesRequiresV4` being garbage-collected on every hook, TLS works because:
1. `receive_server_cert()` manually calls `certificates._configure(None)` to send the CSR and read the provider response.
2. On the first reconcile, no cert is available → charm enters `WaitingStatus: CSR sent; otelcol down while waiting for a cert`.
3. On the second reconcile (triggered by a subsequent hook), the provider's cert data is in relation data, `get_assigned_certificate()` returns the cert, and all three files are written to disk:
   - `otelcol-server-cert.crt` → `/var/snap/opentelemetry-collector/common/otelcol-server-cert.crt` (1329 bytes) ✓
   - `otelcol-private-key.key` → `/var/snap/opentelemetry-collector/common/otelcol-private-key.key` (1678 bytes) ✓
   - `cos-ca.crt` → `/usr/local/share/ca-certificates/juju_receive-ca-cert/cos-ca.crt` (1280 bytes, the root CA from the server cert) ✓
4. `receive_ca_cert()` separately writes the trust-store CA certs from the `receive-ca-cert` relation:
   - `0.crt` → `/usr/local/share/ca-certificates/juju_receive-ca-cert/0.crt` (1280 bytes) ✓

The CA cert path is `SERVER_CA_CERT_PATH = "/usr/local/share/ca-certificates/juju_receive-ca-cert/cos-ca.crt"` (`src/constants.py:12`) — it lives in the system trust store, where `update-ca-certificates` picks it up. This is correct design. The `otelcol-server-ca.crt` filename does not appear in any constant and was never part of the design.

**However**, the event-based lifecycle is broken: the `TLSCertificatesRequiresV4` library emits `certificate_available` events when certs are found, but because the object is GC'd, these events are never dispatched to the charm. Certificate renewal (expired cert → new cert) depends on these events, so cert rotation is likely broken.

### COSAgentRequirer garbage collection on every hook

```
WARNING unit.opentelemetry-collector/0.juju-log Reference to ops.Object at path
OpenTelemetryCollectorCharm/COSAgentRequirer[cos-agent] has been garbage collected
between when the charm was initialised and when the event was emitted.
```
Logged on every hook. The COSAgentRequirer is created as a local variable at `src/charm.py:280` and never stored. The charm works around this by calling `cos_agent._on_relation_data_changed()` (a private method) on every reconcile, which causes hook amplification.

### Six library objects not stored — systemic GC pattern

Objects created as local variables and GC-vulnerable:
- `COSAgentRequirer` (`src/charm.py:280`) — COS Agent data
- `TLSCertificatesRequiresV4` (`src/integrations.py:574`) — TLS server certs
- `OtlpRequirer` × 2 (`src/integrations.py:508,517`) — OTLP forwarding
- `ProfilingEndpointProvider` (`src/integrations.py:332`) — profiling
- `ProfilingEndpointRequirer` (`src/integrations.py:343`) — profiling

Ten other library objects are correctly stored via `charm.__setattr__()`.

### Status precedence hides real blocked messages

On every reconcile, status flips `active` → `blocked(memory)` → `blocked(missing-relations)`. If both conditions exist, only the last survives. Confirmed via `juju show-status-log`: setting `memory_limit_percentage="-5"` on a charm missing outgoing relations produces:
```
workload   active
workload   blocked  Invalid memory_limit_percentage config value: defaulting to 100, see debug-log
workload   blocked  ['cloud-config']|['send-loki-logs']|['send-remote-write'] for juju-info
```
`juju status` shows only the last blocked message. An operator fixing the missing relations would suddenly see a different blocked message they never knew existed.

### Per-hook status flip chain

Every hook transitions through `active` → `blocked(missing-relations)`. The `juju show-status-log` shows this pair on every hook (peer-relation-created, leader-elected, config-changed, start, each relation-changed). `ActiveStatus()` is set at `src/charm.py:584`, then overwritten at line 592 by the mandatory-relations check.

### Scale-up snap-start failure loop on new subordinate units

When a new subordinate unit (e.g., otelcol/4) joins a machine that already has the snap installed (from otelcol/0 or otelcol/2), the reconcile hook at line 564 calls `self.snap("opentelemetry-collector").start()`. This fails with:
```
subprocess.CalledProcessError: Command '['snap', 'start', 'opentelemetry-collector']' returned non-zero exit status 1.
```
The hook retries, fails again, and the unit enters `error` state. After 7 repeated failures over ~90 seconds, the unit remains in error. This prevents clean scale-up on machines with existing otelcol instances. The `snap start` call is intended to resume the snap after stopping it while waiting for certs, but is called unconditionally on every reconcile.

### Hook amplification

Each config-changed triggers **two** config-changed hook runs. Root cause: `_reconcile` calls `cos_agent._on_relation_data_changed()` which writes to peer relation data, queuing another config-changed.

### Stop hook — clean on Juju 3.6, traceback on Juju 4.x

On Juju 3.6: `remove-unit ubuntu/2` → otelcol/1 stop hook ran cleanly (`INFO juju.worker.uniter.operation ran "stop" hook`). No traceback.

On Juju 4.x (observed in previous review round): `ops.hookcmds._utils.Error: command ('config-get', '--format=json') exited with status 1`. The stop hook falls through to `_reconcile()` which calls `self.config.get(...)`. The difference is Juju-version-specific availability of `config-get` during stop.

### Process recovery — systemd restarts within 2 seconds

`sudo kill -9` on the otelcol process caused systemd to restart it automatically. The snap service remained `active` throughout.

### TLS relation removal correctly cleans up cert files

When `receive-server-cert` was removed, `otelcol-server-cert.crt` and `otelcol-private-key.key` were correctly deleted. Re-adding the relation restored them within 15s.

### Resource usage

- otelcol: ~100 MB RSS, 24 threads, snap revision 80
- node-exporter: ~20 MB RSS
- grafana-agent: ~200 MB RSS (when deployed alongside)
- Unit agent: ~124 MB RSS
- Snap install: ~70s otelcol, ~11s node-exporter

## Findings

### 1. TLSCertificatesRequiresV4 garbage collected — certificate renewal broken
- **Severity**: high (corrected from critical — TLS data does reach disk)
- **Kind**: bug
- **Where**: `src/integrations.py:574-584`
- **Evidence**: `certificates = TLSCertificatesRequiresV4(...)` at line 574 is a local variable. The code acknowledges this at line 582: `# TLSCertificatesRequiresV4 is garbage collected`. A manual `_configure(None)` call at line 584 forces CSR submission and certificate retrieval. On Juju 3.6, all three TLS files reach disk (cert, key, and CA cert at `SERVER_CA_CERT_PATH`). **However**, the library's event-based lifecycle is broken: `_find_available_certificates()` stores certs in Juju secrets and emits `certificate_available` events, but because the observer object is GC'd, these events are never dispatched to the charm. Certificate renewal (expired → new) depends on these events.
- **Why it matters**: While initial TLS setup works (via the manual workaround), certificate rotation is likely broken. When the provider issues a renewed certificate, the charm will never receive the `certificate_available` event and won't update the on-disk certs. The manual `_configure(None)` hack also bypasses the Juju secrets storage path, meaning certs are not persisted across charm upgrades.
- **Fix**: Store the object: `charm.__setattr__("tls_certificates", certificates)`. Remove the manual `_configure(None)` call — the library's observers will handle the CSR lifecycle naturally.
- **Linter rule**: "ops.Object subclass created in integration function without storing as charm attribute" — mechanically checkable: flag `SomeLibrary(self, ...)` calls in `src/` whose return value is not assigned or passed to `charm.__setattr__`.

### 2. Stop hook crashes on Juju 4.x — config-get unavailable
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:182-188`
- **Evidence**: The `stop` event is not handled in `__init__` — it falls through to `self._reconcile()` at line 188, which calls `self.config.get(...)` at line 192. On Juju 4.0.5, `config-get` is unavailable during stop, producing `ops.hookcmds._utils.Error: command ('config-get', '--format=json') exited with status 1`. On Juju 3.6.23, the stop hook runs cleanly — `config-get` appears to be available.
- **Why it matters**: On Juju 4.x, every charm removal produces an ERROR-level traceback. Although the remove hook still runs and completes cleanup, the error is avoidable and alarming for operators.
- **Fix**: Add `elif event() == "stop": return` to `__init__` alongside the existing remove handler. The comment at lines 178-181 explains why cleanup is deferred to remove — add a one-line stop handler to prevent the crash on Juju 4.x.
- **Linter rule**: "`_reconcile` called during stop hook without checking config-get availability" — partially checkable: flag `self.config` access when `event() == "stop"`.

### 3. COSAgentRequirer, OtlpRequirer, ProfilingEndpointRequirer/Provider garbage collected
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:280`, `src/integrations.py:508,517,332,343`
- **Evidence**: All five library objects are created as local variables, never stored. Observed GC warning for COSAgentRequirer on every hook. The charm works around the COS Agent issue by calling `cos_agent._on_relation_data_changed()` (a private method) on every reconcile.
- **Why it matters**: These libraries register `framework.observe()` callbacks that are lost when the objects are GC'd. For COSAgentRequirer, the manual private-method call mitigates this (at the cost of doubled hook work and using private APIs). For OtlpRequirer and ProfilingEndpoint*, the immediate data extraction works on the first call but subsequent relation-changed events won't fire the library handlers — leading to stale data, missed updates, or dropped alert rules.
- **Fix**: Store all five objects via `charm.__setattr__()` following the pattern used by the 10 properly-stored integrations. Remove the manual `_on_relation_data_changed()` call.
- **Linter rule**: Same rule as finding #1.

### 4. Scale-up snap-start failure loop
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:564`
- **Evidence**: `self.snap("opentelemetry-collector").start()` is called unconditionally near the end of `_reconcile`. When a new subordinate unit joins a machine that already has the snap running, `snap start` fails with exit status 1. The hook retries, fails again repeatedly (7+ times observed), and the unit enters `error` state permanently. Observed in rv-otel-d2 when scaling from 2→3 ubuntu units.
- **Why it matters**: Operators cannot scale up otelcol subordinate units on machines that already have the snap installed. The "add more ubuntu units + let otelcol subordinate attach" workflow is broken.
- **Fix**: Only call `snap start` when the snap is actually stopped — either track state or check `snap services opentelemetry-collector` before starting. The intent of line 564 is "resume after CSR waiting state" but the call is unconditional. Gate it behind the same condition that stops the snap (the CSR waiting block at line 556-558).
- **Linter rule**: Not mechanically checkable.

### 5. Status precedence: blocked messages overwrite each other
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/charm.py:584-593`
- **Evidence**: Sequential `self.unit.status =` assignments: `ActiveStatus()` at line 584, `BlockedStatus(memory)` at line 587, `BlockedStatus(missing-relations)` at line 593. Verified in deployment: setting `memory_limit_percentage="-5"` on a charm already blocked on missing relations produces three status changes in one hook; `juju status` shows only the last.
- **Why it matters**: An operator fixing the missing-relations issue would suddenly see a different blocked message (invalid memory limit) and have no idea it had been there all along. The status history shows all three but `juju status` only shows the last.
- **Fix**: Accumulate conditions in priority order and set the highest-priority status at the end, or concatenate blocked messages.
- **Linter rule**: "Multiple `self.unit.status =` assignments in same method without early return or conditional prioritisation" — mechanically checkable.

### 6. Calling private method `_on_relation_data_changed` on COSAgentRequirer
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:298`
- **Evidence**: `cos_agent._on_relation_data_changed(changed_event)` — calling a private method with a synthetic `RelationChangedEvent`. A TODO comment acknowledges this.
- **Why it matters**: Private methods can change or disappear without notice. The synthetic event construction (`RelationChangedEvent(handle=self.handle, ...)`) uses the charm's handle, not the framework's event queue.
- **Fix**: If the COSAgentRequirer GC issue (finding #3) is fixed, the library's own event handlers fire naturally; the manual call becomes unnecessary. Short-term: work with COS Agent library maintainers to add a public `sync_data()` method.
- **Linter rule**: "Call to private method on a charm library object" — mechanically checkable.

### 7. Config options `queue_size`, `tracing_sampling_rate_*`, `max_elapsed_time_min` accept invalid values
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:192-256` (config reading); no validation in `src/config_manager.py` for these options
- **Evidence**: `juju config opentelemetry-collector queue_size=-10` and `tracing_sampling_rate_workload=200` were accepted without error. The charm validates `global_scrape_interval`, `global_scrape_timeout`, `memory_limit_percentage`, and `ports`, but passes `queue_size`, `max_elapsed_time_min`, and `tracing_sampling_rate_*` directly into the otelcol config without validation. Negative queue sizes or sampling rates outside 0-100 could cause otelcol runtime errors or undefined behaviour.
- **Why it matters**: Operators can deploy with silently broken config. otelcol may fail to start or drop all telemetry without a clear Juju-level error.
- **Fix**: Add validation in ConfigManager or `_reconcile` for ranges: `queue_size >= 1`, `tracing_sampling_rate_*` in 0-100, `max_elapsed_time_min >= 1`.
- **Linter rule**: Not mechanically checkable (requires semantic knowledge of valid ranges).

### 8. Logrotate postrotate signals all otelcol processes on the machine
- **Severity**: low
- **Kind**: bug
- **Where**: `src/logrotate.d/otelcol:14-16`
- **Evidence**: `kill -HUP $(pidof otelcol)` signals ALL PIDs matching "otelcol". With multiple subordinate units on one machine, rotating one unit's log signals every unit's process.
- **Why it matters**: Unnecessary config reloads across all co-located units. If one unit has a broken config from a failed write, the HUP could cause another unit's process to pick it up.
- **Fix**: Use `systemctl kill -s HUP snap.opentelemetry-collector.opentelemetry-collector`.
- **Linter rule**: Not mechanically checkable.

### 9. `_reconcile` runs subprocess for workload version on every hook
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:594-612`
- **Evidence**: `self.unit.set_workload_version(self._otelcol_version or "")` runs `/snap/opentelemetry-collector/current/bin/otelcol --version` as a subprocess on every hook.
- **Why it matters**: ~100-200ms per hook. In multi-unit deployments, this multiplies across all units on every config/relation change.
- **Fix**: Cache the version after snap install/refresh; only re-query on upgrade-charm or snap refresh.
- **Linter rule**: "subprocess call in hook handler not guarded by event-type check" — partially checkable.

### 10. `add_log_forwarding` unconditionally adds log processors
- **Severity**: low
- **Kind**: performance
- **Where**: `src/config_manager.py:257-284`
- **Evidence**: The `resource/send-loki-logs` and `attributes/send-loki-logs` processors are always added to the logs pipeline. Code has a `# TODO: Luca: this was gated by having outgoing logs. Do we need that?` comment.
- **Why it matters**: Unnecessary CPU on every log entry when no Loki backend is configured.
- **Fix**: Gate on `endpoints` being non-empty, or remove the TODO with reasoning.
- **Linter rule**: Not mechanically checkable.

### 11. Terraform module channel validation prevents non-dev tracks
- **Severity**: low
- **Kind**: ux / docs
- **Where**: `terraform/variables.tf:10-13`
- **Evidence**: `validation { condition = startswith(var.channel, "dev/") ... }` rejects `latest/edge`, `2/stable`, etc.
- **Why it matters**: Operators cannot deploy stable releases via the terraform module.
- **Fix**: Remove or relax the validation, or document the restriction explicitly.
- **Linter rule**: Not mechanically checkable.

### 12. Terraform module sets `units` on a subordinate charm
- **Severity**: nit
- **Kind**: lint
- **Where**: `terraform/main.tf:6`
- **Evidence**: `units = var.units` with default of 1. Subordinate charms don't have independent unit counts.
- **Why it matters**: Harmless in practice (Juju ignores it), but confusing.
- **Fix**: Remove the `units` variable or document it has no effect.
- **Linter rule**: "`units` variable on subordinate charm terraform module" — mechanically checkable.

### 13. Bundled mdadm alert rules file has YAML syntax error — rules silently dropped
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/prometheus_alert_rules/mdadm.rules:10` (also lines 22, 33)
- **Evidence**: The `description:` key appears on the same line as the closing quote of `summary:`, e.g.: `summary: "{{ $value }} disks failed..."        description: >-`. Python's `yaml.safe_load()` rejects this with `expected <block end>, but found '<scalar>'`. Confirmed in unit test output: `ERROR cosl.rules:rules.py:374 Failed to read rules from mdadm.rules`. All other 14 .rules files parse correctly.
- **Why it matters**: The mdadm alert rules (RAID disk failure, spare, inactive, and recovering alerts) are silently dropped by cosl on every hook. Operators monitoring machines with mdadm RAID will never see alerts for disk failures. The ERROR is logged but the charm continues — no BlockedStatus or other operator-visible signal.
- **Fix**: Add a newline between the `summary` closing quote and `description:` on lines 10, 22, and 33.
- **Linter rule**: "YAML parsing failure on bundled alert rule files" — mechanically checkable: `yaml.safe_load()` all `.rules` files in `src/prometheus_alert_rules/` and `src/loki_alert_rules/`.

### 14. `send_otlp` creates two OtlpRequirer instances, neither stored, one used only for publish()
- **Severity**: medium
- **Kind**: performance / bug
- **Where**: `src/integrations.py:508-520`
- **Evidence**: First `OtlpRequirer` at line 508 is created with `aggregator_peer_relation_name="peers"` and `rules=rules`, then `.publish()` is called on it for side effects only. Second `OtlpRequirer` at line 517 is created independently and used for `.endpoints`. Neither instance is stored via `charm.__setattr__()`, so both are GC'd (same pattern as findings #1, #3).
- **Why it matters**: Both instances register `framework.observe()` callbacks that are lost. The second instance's o11y rule bundling (which reads from `*_RULES_DEST_PATH` directories) depends on the o11y library's observation of relation events to trigger rule updates. When the instance is GC'd, subsequent rule changes from related applications are never forwarded over OTLP. Additionally, creating two separate instances means the charm talks to the same OTLP relation twice per reconcile, doubling the chance of race conditions between rule publish and endpoint retrieval.
- **Fix**: Create a single OtlpRequirer, store it, call `.publish()` then read `.endpoints` from the same instance.
- **Linter rule**: "Multiple instantiations of same ops library class for same relation within one method" — partially checkable.

### 15. `send_profiles` and `receive_profiles` don't store ProfilingEndpointRequirer/Provider
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/integrations.py:332,343`
- **Evidence**: `ProfilingEndpointProvider(...)` at line 332 and `ProfilingEndpointRequirer(...)` at line 343 are both local variables, created and consumed immediately (provider calls `.publish_endpoint()`, requirer calls `.get_endpoints()`). Neither is stored. This is the same GC pattern as findings #1 and #3.
- **Why it matters**: The profiling library instances register observers that are immediately GC'd. While the immediate data extraction works on the first call, subsequent relation-changed events will not dispatch to the library's handlers. Any application that updates its profiling endpoint after the first relation-joined will have its new endpoint silently ignored.
- **Fix**: Store both via `charm.__setattr__()`.
- **Linter rule**: Same as finding #1.

### 16. Unit test conftest patches hide real bugs
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py`
- **Evidence**: Multiple autouse fixtures mask real code paths:
  - `mock_singleton_snap_manager` (line 158): `get_revisions` hardcoded to `{1, 2}` — snap revision mismatch detection (charm.py:563-573) is never tested.
  - `mock_snap_map` (line 165): `get_revision` hardcoded to `2` — architecture-specific snap revision selection is never tested.
  - `juju_hook_name` (line 123): `JUJU_HOOK_NAME` set to `"fake"` — the charm's `event()` dispatch logic (charm.py:126-133), including the TLS cert refresh gating, is never tested with real hook names.
  - `refresh_certs` (line 62): patched to no-op lambda — TLS cert refresh behaviour is never tested.
  - `mock_cleanup_certificates_on_remove` (line 189): auto-applied except when test name includes `cleanup_certificates_on_remove` — the remove-hook cert cleanup path is never tested (and no test has that name).
- **Why it matters**: The largest test gaps (stop/remove hooks, TLS event lifecycle, snap revision mismatch, cert cleanup, architecture variation) are systematically hidden by conftest fixtures. New bugs in these paths will not be caught. The scale-up snap-start failure (finding #4) exists because this code path has zero test coverage.
- **Fix**: These should be opt-in fixtures, not autouse. Tests that need the real path should use it; tests that don't should explicitly opt out.
- **Linter rule**: "Autouse fixture that patches a charm method to a no-op" — mechanically checkable.

### 17. Subordinate deployment fails on Juju 4.0.5 / LXD
- **Severity**: high
- **Kind**: bug / environment
- **Where**: Deploy-time, no specific code line
- **Evidence**: Three deploy attempts on Juju 4.0.5 with LXD all failed: subordinates permanently stuck at `agent initialising` / `allocating`. Principals and standalone charms deployed fine. This affects any subordinate charm on Juju 4.x + LXD.
- **Why it matters**: The charm's `assumes: juju >= 3.6` is misleading — the charm cannot deploy on Juju 4.x with LXD.
- **Fix**: Document the known incompatibility in README and charmhub description. Consider `assumes: juju >= 3.6, < 4.0` until resolved.
- **Linter rule**: Not mechanically checkable.

### 18. TLS unit tests mock the entire TLSCertificatesRequiresV4 library — GC/event bug invisible to tests
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_tls_certificates.py:93-96`
- **Evidence**: Tests patch `_find_available_certificates` and `get_assigned_certificate` on `TLSCertificatesRequiresV4`, completely bypassing the relation-data reading path and event system. One test (`test_https_endpoint_is_provided`) is SKIPPED.
- **Why it matters**: The TLS GC issue and broken event lifecycle cannot be caught by the test suite because tests replace the buggy code path with mocks.
- **Fix**: Add a multi-state Scenario test that runs multiple hook cycles with a real TLS relation, verifying certs materialize on disk after the provider writes to relation data, without mocking library internals.
- **Linter rule**: Not mechanically checkable.

## Worth copying

### ConfigBuilder/ConfigManager separation
`src/config_builder.py` provides a low-level builder; `src/config_manager.py` provides a high-level API with semantic methods. Clean separation makes config construction testable at both levels. Other charms with complex config generation should adopt this pattern.

### Hash-based restart gating
`src/charm.py:538-551` — stable hash of config + CA certs + server cert hash. Only restarts the snap when the hash changes. Includes on-disk CA file content (not relation data) to stay aligned with what the snap actually loads.

### Snap revision mismatch detection
`src/charm.py:563-573` — Checks installed snap revision against `SnapMap` expectations. If another co-located unit installed a different revision, goes to `BlockedStatus` with a clear message.

### SingletonSnapManager for subordinate snap coordination
`src/singleton_snap.py` — File-based lockfiles under `/opt/singleton_snaps/`. Clean implementation with comprehensive unit tests (15 tests covering registration, unregistration, revision tracking, malformed file handling, multi-unit scenarios).

### Comprehensive Juju config validation (where it exists)
The charm validates port format, scrape interval/timeout format, memory limit percentages, and returns `BlockedStatus` with actionable messages. `build_port_map()` in `config_builder.py` provides detailed error messages listing valid port names.

### charmlibs.pathops — clean path-abstraction library
`deps/charmlibs/pathops/` (shipped as a PyPI dependency) provides `LocalPath` and `ContainerPath` with a shared `PathProtocol`. The `LocalPath` implementation extends `pathlib.PosixPath` with ownership and mode arguments on `write_text`/`write_bytes`/`mkdir`, validated against actual users/groups before writes. Well-typed, thoroughly documented. Other charms using the pathops library should follow this pattern.

## Common-practice notes

### Follows conventions
- `charmcraft.yaml` with `type: charm`, `subordinate: true`, `assumes: juju >= 3.6` — standard for modern machine subordinates
- `pyproject.toml` with uv, ruff, pyright, coverage — matches current ecosystem standards
- Charm libraries under `lib/charms/<name>/v<N>/`
- Uses `cosl` for `JujuTopology`, `MandatoryRelationPairs`
- Integration tests use `jubilant` + `pytest-jubilant`
- `ops[testing]` (Scenario) for unit tests
- Broad architecture support: ubuntu@22.04 and 24.04 across amd64, arm64, s390x, ppc64el

### Drifts from convention
- **No `self.framework.observe()` calls** — the "holistic" pattern runs `_reconcile()` from `__init__` on every hook. This causes systemic GC issues and prevents the ops framework from optimizing hook dispatch. It requires manual workarounds (private method calls) for standard library behaviour.
- **`_reconcile` at ~450 lines** — unusually long; most modern charms split reconciliation into smaller methods or use a reconciler class (issue #79).
- **Uses `charm.__setattr__()`** to store integration objects rather than `self.attr = ...`. Stylistic choice; both work.

## Tests

### Unit tests
171 passed, 1 skipped (`test_https_endpoint_is_provided`), 118 deprecation warnings (mostly from tls_certificates_interface v4 and Pydantic V2). Ran with `PYTHONPATH=.:lib:src uv run --frozen --isolated --extra=dev pytest tests/unit/`. All tests use `ops.testing` (Scenario).

### What the unit tests actually verify (and what they don't)

Test-worthy behaviour asserted:
- **ConfigBuilder port parsing, $ escaping, TLS injection, nopexporter insertion** — `test_config_builder.py` (thorough, 14 tests)
- **ConfigManager semantic methods** (log ingestion/forwarding, traces, OTLP, cloud integrator, profiling, custom processors, memory limiter) — `test_config_manager.py` (thorough, 15 tests)
- **SingletonSnapManager file-based coordination** (register, unregister, revision tracking, malformed files, multi-unit) — `test_singleton_snap.py` (excellent, 15 tests)
- **hash-based restart gating** (CA cert dir changes trigger restart, config changes trigger restart) — `test_ca_cert_restart.py` (8 tests)
- **Mandatory relation pair checking** — `test_mandatory_relation_pairs.py` (4 tests)
- **Node exporter info metric** — `test_node_exporter_info_metric.py` (3 tests)

Important behaviours hidden by autouse conftest mocks:
- **Hook dispatch**: `JUJU_HOOK_NAME` is set to `"fake"` globally, so the charm's `event()` branching (install/upgrade-charm/remove vs `_reconcile`) is only tested where explicitly overridden (3 tests in `test_charm_lifecycle.py`). The stop hook crash (finding #2) and TLS cert refresh gating are invisible.
- **Snap revision mismatch**: `SingletonSnapManager.get_revisions` returns `{1, 2}` and `SnapMap.get_revision` returns `2` — the revision-mismatch `BlockedStatus` branch at charm.py:563-573 is never reached.
- **TLS certificate lifecycle**: `_find_available_certificates` and `get_assigned_certificate` are patched; `Certificate.from_string` is patched. The real CSR submission → provider response → cert-on-disk flow is mocked end-to-end. The GC event lifecycle bug (finding #1) cannot be caught.
- **snap lifecycle**: All snap operations (`install`, `start`, `stop`, `restart`, `ensure`) are mocked to no-ops.
- **cert cleanup on remove**: `_cleanup_certificates_on_remove` is patched to no-op for all tests.
- **refresh_certs**: patched to `lambda: True`.
- **logrotate timer**: `ensure_logrotate_timer` patched to `lambda: True`.

### Static analysis
- **Ruff**: 11 fixable style violations, all in library code under `lib/charms/` (none in `src/`). Issues: unnecessary `else`/`elif` after `return`/`continue`, implicit `None` return. The charm's own `src/` code is clean.
- **Pyright**: 0 errors, 0 warnings, 0 informations — excellent.
- **Codespell**: configured with `ignore-words-list = "assertIn"`.

### Coverage gaps (critical)
- **Stop hook crash not tested**: `tests/unit/test_charm_lifecycle.py` tests install, upgrade-charm, and update-status, but not stop or remove hooks.
- **Remove hook cleanup not tested**: No test verifying snap removal, config cleanup, or cert directory cleanup on remove.
- **TLS end-to-end not tested**: Unit tests mock `TLSCertificatesRequiresV4` entirely. No test exercises the real relation-data → cert-on-disk flow across multiple hooks.
- **GC lifecycle not tested**: No test verifies library objects survive across hook invocations.
- **Status precedence not tested**: No test for the active→blocked(memory)→blocked(relations) overwrite chain.
- **Scale-up not tested**: No test for the snap-start failure when a new subordinate joins a machine with the snap already installed.
- **Snap revision mismatch not tested**: Hidden by autouse mock.
- **Config validation gaps not tested**: `queue_size`, `tracing_sampling_rate_*`, `max_elapsed_time_min` accept invalid values.
- **No TLS integration test**: None of the 7 integration test files covers `receive-ca-cert` or `receive-server-cert` relations.
- **Alert rule file validation not tested**: The `mdadm.rules` YAML error (finding #13) would have been caught by a simple `yaml.safe_load()` loop over all bundled `.rules` files.
- **Profile lifecycle not tested**: `send_profiles` and `receive_profiles` GC issues (finding #15) not covered.

### Integration tests
7 files using `jubilant`: `test_principal.py`, `test_cos_agent.py`, `test_tracing.py`, `test_external_config.py`, `test_log_rotation.py`, `test_snap_refresh.py`, `test_removal_hooks.py`. Thorough — they assert on actual behaviour (debug log contents, process arguments, file presence, metrics exposure), test multi-unit co-location, and verify cleanup after removal. Not run here (requires full LXD test environment, and the Juju controller was unreachable during this review session).

## Docs

### README
`README.md` (2KB): Concise — covers what, how to deploy, snap backend. Missing: relation inventory, config reference, known limitations (GC/TLS, scale-up snap-start failure), scaling guidance for co-located units (issue #260).

### charmcraft.yaml description
Comprehensive — key features, known limitations, config option summary. Good example.

### Terraform module
`terraform/README.md`: Standard terraform-docs output. Channel validation only accepts `dev/*` tracks (finding #11).

### Charmhub listing
Published on 0.130/stable (rev 326), 2/stable, 2/edge, dev/edge. `2/edge` rev 347 used for testing is 21 revisions ahead of stable.

## Open questions

1. **Is cert renewal working?** The `_configure(None)` workaround gets the initial cert, but the `certificate_available` event path (which handles renewal) is broken because `TLSCertificatesRequiresV4` is GC'd. To settle: deploy with short-lived certs and observe whether they rotate.

2. **Should the holistic pattern be replaced with explicit observers?** The GC issues (findings #1, #3, #6) all stem from this pattern. Registering specific observers would let library objects live for the charm's lifetime. Issue #79 tracks this.

3. **Why does `snap start` fail on a machine that already has the snap running?** (Finding #4) The `snap start` command should be idempotent. The failure (exit status 1) may be related to the specific snap version, systemd state, or a race between the new unit's config write and the already-running snap. Investigate the snap daemon logs.

4. **Does the `dev/*` terraform channel restriction serve a purpose?** The charm is published on stable channels but the terraform module rejects them.

5. **What happens when multiple otelcol applications deploy to the same machine with different snap revisions?** The `SingletonSnapManager` handles tracking, and the charm goes to BlockedStatus on mismatch. Issue #260 asks for documentation.

6. **Is the Juju 4.x LXD subordinate hang a known issue?** Check Juju issue tracker for subordinate provisioning bugs on 4.x.

7. **Why does `juju integrate opentelemetry-collector:cos-agent grafana-agent:cos-agent` fail?** Both charms have the `cos-agent` endpoint, but subordinate-to-subordinate integration reports "no relations found."
