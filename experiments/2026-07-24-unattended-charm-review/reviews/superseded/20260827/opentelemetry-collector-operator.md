# opentelemetry-collector

A mature machine subordinate charm that deploys the OpenTelemetry Collector via snaps, managing a wide web of integrations (metrics, logs, traces, profiles, dashboards, TLS) and building otelcol config from them. Code quality is high — a clean config-building architecture, 171 passing unit tests, and integration tests covering multi-unit removal, log rotation, and snap refresh. But the "`_reconcile`-on-every-hook, no `framework.observe()`" pattern causes systemic garbage collection of library objects (`COSAgentRequirer`, `TLSCertificatesRequiresV4`, `OtlpRequirer` ×2, `ProfilingEndpointRequirer`/`Provider`), which breaks their event-driven lifecycles. TLS still gets certs to disk via a manual `_configure(None)` workaround, but certificate renewal depends on the broken event path and is likely non-functional. A new subordinate unit joining a machine that already has the snap running hits a `snap start` failure loop and lands in `error` state — a real scale-up blocker. Status precedence also silently drops earlier blocked messages. A maintainer should first: (1) store the five GC'd library objects as charm attributes instead of local variables, removing the private-method workarounds; (2) gate the unconditional `snap start` call so it only fires when the snap was actually stopped; (3) fix the stop-hook crash on Juju 4.x. The larger architectural fix — replacing the holistic reconcile pattern with explicit observers — is already tracked as issue #79 and would resolve most of the GC findings at once.

| | |
|---|---|
| Repo | canonical/opentelemetry-collector-operator @ `9fa23d2` (2026-07-15) |
| Charms | opentelemetry-collector |
| Substrate | machine (subordinate) |
| Deployed | yes — concierge-lxd (Juju 3.6.23), charmhub 2/edge rev 347. concierge-lxd-4 (Juju 4.0.5) deployment FAILED (subordinates stuck at "agent initialising") |
| Reviewed | 2026-08-09 |

## What it does

Deploys and manages the OpenTelemetry Collector snap (and node-exporter snap) on machine substrates. As a subordinate charm, it attaches to a principal via `juju-info` or `cos-agent` and provides a telemetry pipeline: metrics scraping/remote-write, log collection, trace ingestion (OTLP/Jaeger/Zipkin), profiling, dashboard forwarding, TLS, external config merging, and Grafana Cloud integration. A file-based `SingletonSnapManager` coordinates snap lifecycle when multiple subordinate units share a machine.

## Deployment log

### Round 1 — Juju 4.x (concierge-lxd-4) — deployment failure

Three separate deploy attempts on Juju 4.0.5 all failed: the subordinate charms (`opentelemetry-collector`, `grafana-agent`) remained permanently stuck at `agent initialising` / `allocating`. The principal `ubuntu` and standalone `self-signed-certificates` deployed fine. This looks like a Juju 4.x / LXD subordinate-provisioning issue rather than a charm bug, but it means the charm could not be deployed on Juju 4.x with LXD as of 2026-08-09.

### Round 2 — Juju 3.6 (concierge-lxd): ubuntu + otelcol + grafana-agent + self-signed-certificates

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
- Attempted `juju integrate opentelemetry-collector:cos-agent grafana-agent:cos-agent` — failed with `ERROR no relations found` (subordinate-to-subordinate cross-application integration not supported)
- Install times: otelcol snap ~70s, node-exporter ~11s
- Workload version 0.130.0, otelcol ~100 MB RSS, 24 threads
- `COSAgentRequirer` GC warning observed on every hook

### Round 3 — Juju 3.6 (concierge-lxd): 3-unit scale + config + failure testing

```bash
juju add-model rv-otel-d2 localhost/localhost --controller concierge-lxd
juju deploy ubuntu --channel stable --base ubuntu@24.04 -n 3
juju deploy opentelemetry-collector --channel 2/edge
juju deploy self-signed-certificates --channel edge
juju integrate ubuntu opentelemetry-collector
juju integrate opentelemetry-collector:receive-ca-cert self-signed-certificates:send-ca-cert
juju integrate opentelemetry-collector:receive-server-cert self-signed-certificates:certificates
```

- All 3 subordinate units reached `blocked` (missing outgoing relations) after ~120s ✓
- Scale down (`juju remove-unit ubuntu/2`): clean stop hook, no traceback, otelcol/1 removed cleanly ✓
- Scale up (`juju add-unit ubuntu -n 1`): new unit otelcol/4 entered **error state** — repeated `snap start` failure (finding #4)
- `juju remove-application opentelemetry-collector`: removal stuck because hooks were already failing; required `--force`

### Juju 3.6 versus 4.x summary

| Aspect | Juju 3.6.23 | Juju 4.0.5 |
|---|---|---|
| Subordinate deployment | works | subordinates stuck at "agent initialising" |
| Stop hook crash | no traceback (clean stop on `remove-unit`) | traceback — `config-get` unavailable |
| Server cert + key on disk | yes | deployment failed (not reached) |
| Server CA cert on disk | yes (at `.../cos-ca.crt`) | deployment failed (not reached) |
| `COSAgentRequirer` GC warning | observed | not tested |

### Config changes tested

| Config change | Result |
|---|---|
| `ports="loki_http=3501"` | Port 3501 bound, snap restarted ✓ |
| `ports="invalid_port=1234"` | `BlockedStatus: Invalid ports config: Unknown port name` ✓ |
| `global_scrape_interval="invalid"` | `BlockedStatus: format requires '\d+[ywdhms]'` ✓ |
| `memory_limit_percentage="-5"` | `BlockedStatus` set but overwritten by missing-relations blocked (finding #5) |
| `debug_exporter_for_metrics=true` | Debug exporter added to metrics pipeline ✓ |
| `always_enable_zipkin=true` | Port 9411 opened, zipkin receiver enabled ✓ |
| `tracing_sampling_rate_workload=200` | Accepted without validation (valid range is 0-100) ✗ |
| `queue_size=-10` | Accepted without validation ✗ |
| `processors` with YAML file | Custom processors merged correctly ✓ |
| `batch_timeout` / `send_batch_size` | Unknown option (keys don't exist) — expected |

### Actions

Only one action: `reconcile`. Runs `update-ca-certificates`, rebuilds config, restarts snap if hash changed. Worked ✓.

### Failure injection

| Injection | Result |
|---|---|
| `kill -9 otelcol` | systemd restarted within 2s (PID changed) ✓ |
| Remove `receive-ca-cert` relation | No crash, CA cert files cleaned ✓ |
| Remove `receive-server-cert` relation | No crash, server cert + key files cleaned ✓ |
| Re-add `receive-server-cert` | Certs reappeared on disk after 15s ✓ |
| Remove `receive-server-cert`, re-add | No errors, certs materialised correctly ✓ |
| Scale up from 2→3 units | New unit hit snap-start failure loop (finding #4) ✗ |

## Observed behaviour

### Ruff findings corrected — library code has 11 violations

An earlier pass wrongly reported `All checks passed!` from a limited check. Running `ruff check src/ lib/ tests/` on the full codebase finds 11 fixable style violations (RET505/RET502/RET507), all in `lib/charms/` (tls_certificates_interface v4, tempo_coordinator_k8s, certificate_transfer_interface, operator_libs_linux). The charm's own `src/` is clean. Breakdown: unnecessary `else`/`elif` after `return`/`continue` (9), implicit `None` return (2). Pyright remains `0 errors, 0 warnings, 0 informations`.

### YAML parsing failure in bundled alert rules

The `cosl` rules parser logs `ERROR cosl.rules:rules.py:374 Failed to read rules from mdadm.rules` on every hook invocation (visible in unit test output). RAID-related alerts are silently dropped. Cause: three lines in `mdadm.rules` where `description:` follows the closing quote of `summary:` on the same line. Only discoverable by running the tests and watching stderr, or by manually parsing the `.rules` files.

### Library deprecation warnings

118 warnings in test output, including: `JujuVersion.from_environ()` deprecated (tls_certificates v4), `PydanticDeprecatedSince20: The json method is deprecated` (cos_agent and tracing libraries), `generate_private_key()` deprecated (tls_certificates v4). All in library code; will become hard errors once upstream drops the deprecated APIs.

### TLS works on Juju 3.6 — all three cert files reach disk

Despite `TLSCertificatesRequiresV4` being garbage collected every hook, TLS works because:

1. `receive_server_cert()` manually calls `certificates._configure(None)` to send the CSR and read the provider response.
2. First reconcile: no cert yet → `WaitingStatus: CSR sent; otelcol down while waiting for a cert`.
3. Second reconcile (triggered by a later hook): the provider's cert data is now in relation data, `get_assigned_certificate()` returns it, and all three files are written:
   - `otelcol-server-cert.crt` → `/var/snap/opentelemetry-collector/common/otelcol-server-cert.crt` (1329 bytes) ✓
   - `otelcol-private-key.key` → `/var/snap/opentelemetry-collector/common/otelcol-private-key.key` (1678 bytes) ✓
   - `cos-ca.crt` → `/usr/local/share/ca-certificates/juju_receive-ca-cert/cos-ca.crt` (1280 bytes, root CA from the server cert) ✓
4. `receive_ca_cert()` separately writes the trust-store CA certs from the `receive-ca-cert` relation: `0.crt` → `/usr/local/share/ca-certificates/juju_receive-ca-cert/0.crt` (1280 bytes) ✓

`SERVER_CA_CERT_PATH = "/usr/local/share/ca-certificates/juju_receive-ca-cert/cos-ca.crt"` (`src/constants.py:12`) lives in the system trust store, where `update-ca-certificates` picks it up — correct by design. (An earlier draft of this review wrongly flagged a missing `otelcol-server-ca.crt` file; that filename was never part of the design.)

**However**, the event-based lifecycle is broken: `TLSCertificatesRequiresV4` emits `certificate_available` events when certs are found, but because the object is GC'd, these events are never dispatched to the charm. Certificate renewal (expired cert → new cert) depends on those events, so cert rotation is likely broken (unverified — not directly observed, since testing would require a short-lived cert and waiting for rotation).

### `COSAgentRequirer` garbage collection on every hook

```
WARNING unit.opentelemetry-collector/0.juju-log Reference to ops.Object at path
OpenTelemetryCollectorCharm/COSAgentRequirer[cos-agent] has been garbage collected
between when the charm was initialised and when the event was emitted.
```

Logged on every hook. `COSAgentRequirer` is created as a local variable at `src/charm.py:280` and never stored. The charm works around this by calling the private method `cos_agent._on_relation_data_changed()` on every reconcile, which causes hook amplification.

### Six library objects not stored — systemic GC pattern

Created as local variables, never stored, and therefore GC-vulnerable:

- `COSAgentRequirer` — `src/charm.py:280`
- `TLSCertificatesRequiresV4` — `src/integrations.py:574`
- `OtlpRequirer` ×2 — `src/integrations.py:508,517`
- `ProfilingEndpointProvider` — `src/integrations.py:332`
- `ProfilingEndpointRequirer` — `src/integrations.py:343`

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

Every hook transitions `active` → `blocked(missing-relations)`, visible in `juju show-status-log` on every hook (peer-relation-created, leader-elected, config-changed, start, each relation-changed). `ActiveStatus()` is set at `src/charm.py:584`, then overwritten at line 592 by the mandatory-relations check.

### Scale-up snap-start failure loop on new subordinate units

When a new subordinate unit (e.g. otelcol/4) joins a machine that already has the snap installed (from otelcol/0 or otelcol/2), the reconcile hook at `src/charm.py:564` calls `self.snap("opentelemetry-collector").start()` unconditionally. This fails:

```
subprocess.CalledProcessError: Command '['snap', 'start', 'opentelemetry-collector']' returned non-zero exit status 1.
```

The hook retries, fails again, and the unit enters `error` state. After 7 repeated failures over ~90 seconds the unit remains in error. This blocks clean scale-up on machines with an existing otelcol instance. The `snap start` call is meant to resume the snap after it was stopped while waiting for certs, but is called unconditionally on every reconcile.

### Hook amplification

Each config-changed triggers two config-changed hook runs. Root cause: `_reconcile` calls `cos_agent._on_relation_data_changed()`, which writes to peer relation data, queuing another config-changed.

### Stop hook — clean on Juju 3.6, traceback on Juju 4.x

Juju 3.6: `remove-unit ubuntu/2` → otelcol/1 stop hook ran cleanly (`INFO juju.worker.uniter.operation ran "stop" hook`), no traceback.

Juju 4.x (unverified directly this session — deployment on 4.x failed before reaching this test; carried over from a previous review round): `ops.hookcmds._utils.Error: command ('config-get', '--format=json') exited with status 1`. The stop hook falls through to `_reconcile()`, which calls `self.config.get(...)`. Availability of `config-get` during stop differs between Juju versions.

### Process recovery — systemd restarts within 2 seconds

`sudo kill -9` on the otelcol process caused systemd to restart it automatically; the snap service remained `active` throughout.

### TLS relation removal correctly cleans up cert files

Removing `receive-server-cert` correctly deleted `otelcol-server-cert.crt` and `otelcol-private-key.key`. Re-adding the relation restored them within 15s.

### Resource usage

- otelcol: ~100 MB RSS, 24 threads, snap revision 80
- node-exporter: ~20 MB RSS
- grafana-agent: ~200 MB RSS (deployed alongside)
- Unit agent: ~124 MB RSS
- Snap install: ~70s otelcol, ~11s node-exporter

## Findings

### 1. `TLSCertificatesRequiresV4` garbage collected — certificate renewal broken
- **Severity**: high
- **Kind**: bug
- **Where**: `src/integrations.py:574-584`
- **Evidence**: `certificates = TLSCertificatesRequiresV4(...)` at line 574 is a local variable; a comment at line 582 acknowledges "TLSCertificatesRequiresV4 is garbage collected." A manual `_configure(None)` call at line 584 forces CSR submission and cert retrieval. On Juju 3.6, all three TLS files reach disk (cert, key, CA cert at `SERVER_CA_CERT_PATH`). But the library's event-based lifecycle is broken: `_find_available_certificates()` emits `certificate_available` events, which are never dispatched because the observer object is GC'd.
- **Impact**: Initial TLS setup works via the manual workaround, but certificate rotation is likely broken (unverified — not directly tested with a renewing cert). The manual `_configure(None)` call also bypasses the library's Juju-secrets storage path, so certs may not persist correctly across charm upgrades (unverified).
- **Fix**: Store the object (`charm.__setattr__("tls_certificates", certificates)`); remove the manual `_configure(None)` call and let the library's own observers handle the CSR lifecycle.
- **Linter rule**: "ops.Object subclass created in integration function without storing as charm attribute" — mechanically checkable: flag `SomeLibrary(self, ...)` calls in `src/` whose return value is not assigned or passed to `charm.__setattr__`.

### 2. Stop hook crashes on Juju 4.x — `config-get` unavailable
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:182-188`
- **Evidence**: `stop` is not handled in `__init__`; it falls through to `self._reconcile()` (line 188), which calls `self.config.get(...)` (line 192). On Juju 4.0.5, `config-get` is unavailable during stop, producing `ops.hookcmds._utils.Error: command ('config-get', '--format=json') exited with status 1`. On Juju 3.6.23 the stop hook runs cleanly. (Juju 4.x behaviour carried over from a prior review round — this session's Juju 4.x deployment failed before the stop hook could be re-exercised.)
- **Impact**: Every charm removal on Juju 4.x produces an ERROR-level traceback. The remove hook still completes cleanup, but the error is avoidable and alarming.
- **Fix**: Add `elif event() == "stop": return` in `__init__` alongside the existing remove handler.
- **Linter rule**: "`_reconcile` called during stop hook without checking config-get availability" — partially checkable: flag `self.config` access when `event() == "stop"`.

### 3. `COSAgentRequirer`, `OtlpRequirer` ×2, `ProfilingEndpointRequirer`/`Provider` garbage collected
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:280`; `src/integrations.py:508,517,332,343`
- **Evidence**: All five library objects are created as local variables, never stored. GC warning for `COSAgentRequirer` observed on every hook. The charm mitigates the COS Agent case by calling the private method `cos_agent._on_relation_data_changed()` on every reconcile.
- **Impact**: These libraries register `framework.observe()` callbacks lost on GC. For `COSAgentRequirer` the private-method call mitigates the loss (at the cost of doubled hook work and reliance on a private API). For `OtlpRequirer` and the profiling objects, first-call data extraction works but subsequent relation-changed events won't reach the library handlers — stale data, missed updates, or dropped rules.
- **Fix**: Store all five objects via `charm.__setattr__()`, matching the pattern used for the 10 correctly-stored integrations; remove the manual `_on_relation_data_changed()` call.
- **Linter rule**: Same as finding #1.

### 4. Scale-up snap-start failure loop
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:564`
- **Evidence**: `self.snap("opentelemetry-collector").start()` is called unconditionally near the end of `_reconcile`. When a new subordinate joins a machine that already has the snap running, `snap start` fails (exit status 1); the hook retries and fails repeatedly (7+ times observed), and the unit enters `error` state permanently. Reproduced in rv-otel-d2 when scaling from 2→3 ubuntu units.
- **Impact**: Operators cannot scale up otelcol subordinate units on machines that already have the snap installed — the "add more principal units, let the subordinate attach" workflow is broken.
- **Fix**: Only call `snap start` when the snap is actually stopped — track state, or check `snap services opentelemetry-collector` first. Gate the call behind the same condition that stops the snap (the CSR-waiting block around lines 556-558).
- **Linter rule**: not mechanically checkable.

### 5. Status precedence: blocked messages overwrite each other
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/charm.py:584-593`
- **Evidence**: Sequential `self.unit.status = ` assignments — `ActiveStatus()` (line 584), `BlockedStatus(memory)` (line 587), `BlockedStatus(missing-relations)` (line 593). Confirmed in deployment: setting `memory_limit_percentage="-5"` on a charm already blocked on missing relations produces three status changes in one hook; `juju status` shows only the last.
- **Impact**: An operator fixing the missing-relations issue would suddenly see a different, previously-hidden blocked message (invalid memory limit) and have no idea it had been present all along. `juju show-status-log` shows all three; `juju status` shows only the last.
- **Fix**: Accumulate conditions in priority order and set a single highest-priority status at the end, or concatenate blocked messages.
- **Linter rule**: "Multiple `self.unit.status =` assignments in same method without early return or conditional prioritisation" — mechanically checkable.

### 6. Bundled `mdadm.rules` file has a YAML syntax error — rules silently dropped
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/prometheus_alert_rules/mdadm.rules:10` (also lines 22, 33)
- **Evidence**: `description:` appears on the same line as the closing quote of `summary:`, e.g. `summary: "{{ $value }} disks failed..."        description: >-`. `yaml.safe_load()` rejects this with `expected <block end>, but found '<scalar>'`. Confirmed in unit test output: `ERROR cosl.rules:rules.py:374 Failed to read rules from mdadm.rules`. All other 14 `.rules` files parse correctly.
- **Impact**: mdadm alert rules (RAID disk failure, spare, inactive, recovering) are silently dropped by `cosl` on every hook — no `BlockedStatus` or other operator-visible signal. Operators monitoring machines with mdadm RAID never see these alerts.
- **Fix**: Add a newline between the `summary` closing quote and `description:` on lines 10, 22, and 33.
- **Linter rule**: "YAML parsing failure on bundled alert rule files" — mechanically checkable: `yaml.safe_load()` all `.rules` files in `src/prometheus_alert_rules/` and `src/loki_alert_rules/`.

### 7. Calling private method `_on_relation_data_changed` on `COSAgentRequirer`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:298`
- **Evidence**: `cos_agent._on_relation_data_changed(changed_event)` calls a private method with a synthetic `RelationChangedEvent`; a TODO comment acknowledges this.
- **Impact**: Private methods can change or disappear without notice. The synthetic event is built from the charm's handle, not the framework's event queue.
- **Fix**: Fixing finding #3 (storing `COSAgentRequirer`) lets the library's own handlers fire naturally, making this call unnecessary. Short-term, coordinate with COS Agent library maintainers to add a public `sync_data()` method.
- **Linter rule**: "Call to private method on a charm library object" — mechanically checkable.

### 8. `queue_size`, `tracing_sampling_rate_*`, `max_elapsed_time_min` accept invalid values
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:192-256` (config reading); no validation in `src/config_manager.py` for these options
- **Evidence**: `queue_size=-10` and `tracing_sampling_rate_workload=200` were both accepted without error. The charm validates `global_scrape_interval`, `global_scrape_timeout`, `memory_limit_percentage`, and `ports`, but passes `queue_size`, `max_elapsed_time_min`, and `tracing_sampling_rate_*` straight into the otelcol config unvalidated.
- **Impact**: Operators can deploy with silently broken config; otelcol may fail to start or drop telemetry without a clear Juju-level error.
- **Fix**: Validate ranges in `ConfigManager` or `_reconcile`: `queue_size >= 1`, `tracing_sampling_rate_*` in 0-100, `max_elapsed_time_min >= 1`.
- **Linter rule**: not mechanically checkable (requires semantic knowledge of valid ranges).

### 9. `send_otlp` creates two `OtlpRequirer` instances, neither stored
- **Severity**: medium
- **Kind**: performance / bug
- **Where**: `src/integrations.py:508-520`
- **Evidence**: The first `OtlpRequirer` (line 508, `aggregator_peer_relation_name="peers"`, `rules=rules`) is used only for `.publish()`; the second (line 517) is created independently and used for `.endpoints`. Neither is stored (same GC pattern as findings #1 and #3).
- **Impact**: Both instances register `framework.observe()` callbacks that are lost on GC. The second instance's rule-bundling depends on observing relation events; when GC'd, subsequent rule changes from related applications are never forwarded over OTLP. Two separate instances also mean the charm talks to the same relation twice per reconcile, increasing the chance of a race between rule publish and endpoint retrieval.
- **Fix**: Create a single `OtlpRequirer`, store it, call `.publish()` then read `.endpoints` from the same instance.
- **Linter rule**: "Multiple instantiations of same ops library class for same relation within one method" — partially checkable.

### 10. `send_profiles`/`receive_profiles` don't store `ProfilingEndpointRequirer`/`Provider`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/integrations.py:332,343`
- **Evidence**: `ProfilingEndpointProvider` (line 332) and `ProfilingEndpointRequirer` (line 343) are local variables, created and consumed immediately (`.publish_endpoint()` / `.get_endpoints()`). Same GC pattern as findings #1 and #3.
- **Impact**: Observers registered by these objects are immediately GC'd. First-call data extraction works, but any application updating its profiling endpoint after the first relation-joined will have its new endpoint silently ignored.
- **Fix**: Store both via `charm.__setattr__()`.
- **Linter rule**: same as finding #1.

### 11. Unit test conftest patches hide real bugs
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py`
- **Evidence**: Autouse fixtures mask real code paths:
  - `mock_singleton_snap_manager` (line 158): `get_revisions` hardcoded to `{1, 2}` — the snap revision-mismatch branch (`src/charm.py:563-573`) is never exercised.
  - `mock_snap_map` (line 165): `get_revision` hardcoded to `2` — architecture-specific snap revision selection is never tested.
  - `juju_hook_name` (line 123): `JUJU_HOOK_NAME` set to `"fake"` — the charm's `event()` dispatch logic (`src/charm.py:126-133`), including TLS cert refresh gating, is only tested where explicitly overridden.
  - `refresh_certs` (line 62): patched to a no-op — TLS cert refresh is never tested.
  - `mock_cleanup_certificates_on_remove` (line 189): auto-applied except when the test name includes `cleanup_certificates_on_remove` — no test has that name, so the remove-hook cert cleanup path is never tested.
- **Impact**: The largest test gaps (stop/remove hooks, TLS event lifecycle, snap revision mismatch, cert cleanup, architecture variation) are systematically hidden by these fixtures. The scale-up snap-start failure (finding #4) exists in a code path with zero test coverage.
- **Fix**: Make these fixtures opt-in rather than autouse.
- **Linter rule**: "Autouse fixture that patches a charm method to a no-op" — mechanically checkable.

### 12. TLS unit tests mock the entire `TLSCertificatesRequiresV4` library
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_tls_certificates.py:93-96`
- **Evidence**: Tests patch `_find_available_certificates` and `get_assigned_certificate` on `TLSCertificatesRequiresV4`, bypassing the relation-data reading path and event system entirely. One test (`test_https_endpoint_is_provided`) is skipped.
- **Impact**: The GC/event-lifecycle bug (finding #1) cannot be caught by the test suite because tests replace the buggy code path with mocks.
- **Fix**: Add a multi-state Scenario test that runs multiple hook cycles against a real TLS relation and verifies certs materialise on disk after the provider writes relation data, without mocking library internals.
- **Linter rule**: not mechanically checkable.

### 13. Subordinate deployment fails on Juju 4.0.5 / LXD
- **Severity**: high
- **Kind**: bug / environment
- **Where**: deploy-time, no specific code line
- **Evidence**: Three deploy attempts on Juju 4.0.5 with LXD all failed: subordinates permanently stuck at `agent initialising` / `allocating`. Principals and standalone charms deployed fine.
- **Impact**: `assumes: juju >= 3.6` is misleading — the charm cannot actually deploy on Juju 4.x with LXD as observed here. This likely affects any subordinate charm on Juju 4.x + LXD, not just this one.
- **Fix**: Document the known incompatibility in README/charmhub. Consider `assumes: juju >= 3.6, < 4.0` until resolved.
- **Linter rule**: not mechanically checkable.

### 14. Logrotate postrotate signals all otelcol processes on the machine
- **Severity**: low
- **Kind**: bug
- **Where**: `src/logrotate.d/otelcol:14-16`
- **Evidence**: `kill -HUP $(pidof otelcol)` signals every PID matching "otelcol." With multiple co-located subordinates, rotating one unit's log signals every unit's process.
- **Impact**: Unnecessary config reloads across co-located units; a broken config write from one unit could HUP-trigger reload in another.
- **Fix**: Use `systemctl kill -s HUP snap.opentelemetry-collector.opentelemetry-collector`.
- **Linter rule**: not mechanically checkable.

### 15. `_reconcile` runs a subprocess for workload version on every hook
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:594-612`
- **Evidence**: `self.unit.set_workload_version(...)` runs `/snap/opentelemetry-collector/current/bin/otelcol --version` as a subprocess on every hook.
- **Impact**: ~100-200ms per hook, multiplying across all units in multi-unit deployments on every config/relation change.
- **Fix**: Cache the version after install/refresh; re-query only on `upgrade-charm` or snap refresh.
- **Linter rule**: "subprocess call in hook handler not guarded by event-type check" — partially checkable.

### 16. `add_log_forwarding` unconditionally adds log processors
- **Severity**: low
- **Kind**: performance
- **Where**: `src/config_manager.py:257-284`
- **Evidence**: `resource/send-loki-logs` and `attributes/send-loki-logs` processors are always added to the logs pipeline; a `# TODO: Luca: this was gated by having outgoing logs. Do we need that?` comment remains.
- **Impact**: Unnecessary CPU on every log entry when no Loki backend is configured.
- **Fix**: Gate on non-empty `endpoints`, or remove the TODO with a documented rationale.
- **Linter rule**: not mechanically checkable.

### 17. Terraform module channel validation prevents non-dev tracks
- **Severity**: low
- **Kind**: ux / docs
- **Where**: `terraform/variables.tf:10-13`
- **Evidence**: `validation { condition = startswith(var.channel, "dev/") ... }` rejects `latest/edge`, `2/stable`, etc.
- **Impact**: Operators cannot deploy stable releases via the terraform module.
- **Fix**: Remove or relax the validation, or document the restriction explicitly.
- **Linter rule**: not mechanically checkable.

### 18. Terraform module sets `units` on a subordinate charm
- **Severity**: nit
- **Kind**: lint
- **Where**: `terraform/main.tf:6`
- **Evidence**: `units = var.units` (default 1). Subordinate charms don't have independent unit counts.
- **Impact**: Harmless (Juju ignores it), but confusing to module users.
- **Fix**: Remove the `units` variable, or document that it has no effect.
- **Linter rule**: "`units` variable on subordinate charm terraform module" — mechanically checkable.

## Worth copying

**ConfigBuilder/ConfigManager separation** — `src/config_builder.py` provides a low-level builder; `src/config_manager.py` provides a high-level API with semantic methods. Clean separation, testable at both levels.

**Hash-based restart gating** — `src/charm.py:538-551` uses a stable hash of config + CA certs + server cert hash, restarting the snap only when the hash changes; includes on-disk CA file content (not relation data) to stay aligned with what the snap actually loads.

**Snap revision mismatch detection** — `src/charm.py:563-573` checks the installed snap revision against `SnapMap` expectations, and goes `BlockedStatus` with a clear message if a co-located unit installed a different revision.

**SingletonSnapManager** — `src/singleton_snap.py` uses file-based lockfiles under `/opt/singleton_snaps/`, with comprehensive unit tests (15 tests: registration, unregistration, revision tracking, malformed-file handling, multi-unit scenarios).

**Config validation (where it exists)** — port format, scrape interval/timeout format, and memory limit percentage all get `BlockedStatus` with actionable messages; `build_port_map()` gives detailed errors listing valid port names.

**`charmlibs.pathops`** — `deps/charmlibs/pathops/` provides `LocalPath`/`ContainerPath` with a shared `PathProtocol`; `LocalPath` extends `pathlib.PosixPath` with ownership/mode arguments on `write_text`/`write_bytes`/`mkdir`, validated against actual users/groups before writes. Well-typed and documented.

## Common-practice notes

**Follows convention**: `charmcraft.yaml` with `type: charm`, `subordinate: true`, `assumes: juju >= 3.6`; `pyproject.toml` with uv/ruff/pyright/coverage; charm libraries under `lib/charms/<name>/v<N>/`; uses `cosl` for `JujuTopology`/`MandatoryRelationPairs`; integration tests via `jubilant`/`pytest-jubilant`; `ops[testing]` (Scenario) for unit tests; broad architecture support (ubuntu@22.04/24.04 × amd64/arm64/s390x/ppc64el).

**Drifts from convention**:
- No `self.framework.observe()` calls anywhere — the holistic pattern runs `_reconcile()` from `__init__` on every hook, causing the systemic GC issues above and forcing private-method workarounds.
- `_reconcile` is ~450 lines — unusually long; issue #79 tracks splitting it into a smaller reconciler.
- Uses `charm.__setattr__()` to store integration objects rather than `self.attr = ...` — a stylistic choice, both work.

## Tests

### Unit tests
171 passed, 1 skipped (`test_https_endpoint_is_provided`), 118 deprecation warnings (mostly `tls_certificates_interface` v4 and Pydantic V2). Run with `PYTHONPATH=.:lib:src uv run --frozen --isolated --extra=dev pytest tests/unit/`. All use `ops.testing` (Scenario).

**Well covered**: `ConfigBuilder` port parsing/`$`-escaping/TLS injection/nopexporter insertion (`test_config_builder.py`, 14 tests); `ConfigManager` semantic methods (`test_config_manager.py`, 15 tests); `SingletonSnapManager` (`test_singleton_snap.py`, 15 tests); hash-based restart gating (`test_ca_cert_restart.py`, 8 tests); mandatory relation pairs (4 tests); node exporter info metric (3 tests).

**Hidden by autouse conftest mocks** (see finding #11): hook dispatch/`event()` branching (only 3 tests in `test_charm_lifecycle.py` override the fake hook name), snap revision mismatch branch, real TLS CSR/cert-on-disk flow, all snap operations (mocked to no-ops), cert cleanup on remove, `refresh_certs`, logrotate timer setup.

### Static analysis
- Ruff: 11 fixable violations, all in `lib/charms/` (none in `src/`).
- Pyright: 0 errors, 0 warnings, 0 informations.
- Codespell: configured (`ignore-words-list = "assertIn"`).

### Coverage gaps
- Stop/remove hooks not tested (`test_charm_lifecycle.py` covers install, upgrade-charm, update-status only).
- No remove-hook cleanup test (snap removal, config cleanup, cert directory cleanup).
- No end-to-end TLS test — library entirely mocked.
- No test verifies library objects survive across hook invocations (the GC bugs).
- No test for the active→blocked(memory)→blocked(relations) status-overwrite chain.
- No test for the scale-up snap-start failure.
- Snap revision mismatch hidden by autouse mock.
- `queue_size`/`tracing_sampling_rate_*`/`max_elapsed_time_min` validation gaps not tested.
- No integration test covers `receive-ca-cert` or `receive-server-cert` relations.
- `mdadm.rules` YAML error would have been caught by a simple `yaml.safe_load()` loop over bundled `.rules` files.
- Profile-lifecycle GC issues (finding #10) not covered.

### Integration tests
7 files using `jubilant`: `test_principal.py`, `test_cos_agent.py`, `test_tracing.py`, `test_external_config.py`, `test_log_rotation.py`, `test_snap_refresh.py`, `test_removal_hooks.py`. Thorough — assert on actual behaviour (debug log contents, process arguments, file presence, metrics exposure), cover multi-unit co-location, and verify cleanup after removal. Not run in this review session (the LXD controller became unresponsive partway through — see below).

## Docs

**README** (~2KB): concise on what/how-to-deploy/snap backend. Missing: relation inventory, config reference, known limitations (GC/TLS, scale-up snap-start failure), scaling guidance for co-located units (issue #260).

**charmcraft.yaml description**: comprehensive — key features, known limitations, config option summary. Good example.

**Terraform module README**: standard terraform-docs output; channel validation only accepts `dev/*` tracks (finding #17).

**Charmhub listing**: published on 0.130/stable (rev 326), 2/stable, 2/edge, dev/edge. `2/edge` rev 347 (used for testing) is 21 revisions ahead of stable.

## Open questions

1. Is cert renewal actually working? The `_configure(None)` workaround gets the initial cert, but the `certificate_available` renewal path is broken by the GC issue. Settle by deploying with short-lived certs and observing whether they rotate.
2. Should the holistic reconcile pattern be replaced with explicit observers? All GC findings (#1, #3, #7) stem from it; issue #79 tracks this.
3. Why does `snap start` fail on a machine that already has the snap running? Should be idempotent — investigate snap daemon logs for the specific failure mode.
4. Does the `dev/*` terraform channel restriction serve a purpose, given the charm is published on stable channels?
5. What happens with multiple otelcol applications on the same machine with different snap revisions? `SingletonSnapManager` tracks this and blocks on mismatch; issue #260 asks for documentation.
6. Is the Juju 4.x LXD subordinate-provisioning hang a known Juju issue? Worth checking the Juju tracker.
7. Why does `juju integrate opentelemetry-collector:cos-agent grafana-agent:cos-agent` fail with "no relations found" when both charms provide `cos-agent`?

## Session notes

The concierge-lxd controller became unresponsive after the first two deployment rounds (both `juju` 4.0.12 and `juju_3` 3.6.27 controllers timed out despite visible processes). The remainder of the review (findings #6, #9, #10, #11, #12, #17, #18) was completed via static code review rather than further live deployment.
