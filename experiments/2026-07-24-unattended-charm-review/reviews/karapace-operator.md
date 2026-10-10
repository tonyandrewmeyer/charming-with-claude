# karapace-operator

A machine charm that wraps Karapace (a Kafka schema registry) as a Juju charm. It exposes a `karapace_client` interface for client applications to register schemas, integrates with Kafka for storage, and supports TLS via `tls-certificates`.

**Verdict**: broken as tested. Three independent root causes compound into a charm that cannot reliably serve schemas or survive a TLS integration: (1) the Kafka relation carries a bare-port endpoint (`:9092`) that Karapace resolves to `localhost:9092`, so it never reaches the real broker; (2) Karapace's `host` resolution has no fallback to `ingress-address` once Juju stops guaranteeing legacy peer-data keys, and an empty host feeds into TLS SAN generation; (3) integrating TLS crashes the `certificates-relation-created` hook with an uncaught `ValueError`, wedging the unit in `error` state with no self-recovery path — `juju resolve` just re-runs the same failing hook. Two actions (`get-password`, `set-tls-private-key`) also raise uncaught exceptions on unexceptional inputs. A maintainer should first fix the TLS SAN crash (filter empty strings before calling `generate_csr`) since it is the one bug that produces a permanently stuck unit, then chase down why the Kafka relation endpoint has no host, before touching anything else.

| | |
|---|---|
| Repo | canonical/karapace-operator @ `b901637` (2026-05-14) |
| Charms | karapace (machine), application (integration test helper) |
| Substrate | machine (LXD) |
| Deployed | yes — `concierge-lxd-4`, karapace `latest/edge` rev 26; deployment log below shows install through blocked/active/error transitions |
| Reviewed | 2026-08-21 |

## What it does

Karapace is a Kafka schema registry. This charm installs the `charmed-karapace` snap, creates an `operator` admin user, configures Karapace to connect to Kafka (with optional TLS), and exposes a `karapace_client` interface for client applications to get credentials and endpoints. It also integrates with `tls-certificates` providers for TLS and `grafana-agent` (subordinate) for COS observability.

## Deployment log

### Environment
- Controller: `concierge-lxd-4` (Juju 4.0.12, LXD)
- Model: `rv-karapace-machine`
- Base: Ubuntu 24.04 (karapace), Ubuntu 22.04 (kafka, zookeeper)

### Commands
```bash
juju add-model rv-karapace-machine --controller concierge-lxd-4
juju deploy karapace --channel edge              # rev 26
juju deploy zookeeper --channel 3/stable -n 3    # rev 163
juju deploy kafka --channel 3/stable -n 1        # rev 240
juju integrate kafka zookeeper
juju integrate karapace kafka
```

### Timeline
| Time | Event |
|---|---|
| +0:00 | karapace machine 0 pending |
| +4:00 | karapace install hook starts |
| +9:00 | install hook completes; snap installed; leader-elected/config-changed/start run; blocked "missing required kafka relation" |
| +20:00 | kafka machines pending |
| +25:00 | kafka machine started; zookeeper machines started |
| +27:00 | zookeeper active (3 units); `juju integrate kafka zookeeper` |
| +28:00 | kafka broker not running (blocked); `juju integrate karapace kafka` |
| +28:20 | kafka becomes active; karapace briefly **active** (~20s window) |
| +29:00 | karapace blocked "unit not connected to kafka" — caught by `update-status` |
| — | `juju remove-relation karapace kafka` → blocked "missing required kafka relation" ✓ |
| — | `juju integrate karapace kafka` → brief active → blocked again ✓ |
| — | `snap stop charmed-karapace` → status stays active for ~5min, then blocked "service not running" ✓ |
| — | `snap start charmed-karapace` → active ~5min later, then blocked "kafka not connected" ✓ |
| — | `juju integrate karapace:cos-agent grafana-agent:cos-agent` → grafana-agent active ✓; COS pipeline broken (no OTELCol) |
| +21:11 | `set-password username=operator password=short` — **accepted** (5-char password) ✗ |
| +21:11 | `get-password` action raised uncaught `KeyError: 'operator'` (logged WARNING) ✗ |
| +21:25 | `juju integrate karapace:certificates self-signed-certificates:certificates` → **ERROR**: `certificates-relation-created` hook crashed with `ValueError: '' does not appear to be an IPv4 or IPv6 address` ✗ |
| +21:26 | karapace/0 stuck in `error`, hook retried every ~10s, never recovers |
| +21:27 | `juju add-unit karapace -n 1` → karapace/1 / machine 6 created |
| +21:30 | `juju remove-relation karapace:certificates self-signed-certificates` — relation removed, karapace/0 still `error` ✗ |
| +21:32 | karapace/1 comes up: `cos-agent`/`restart`/`kafka` hooks fire; `waiting: internal credentials not yet added` |
| +21:32 | karapace/1 peer unit data confirmed: only `egress-subnets` + `ingress-address`, no `private-address` ✗ |
| — | `juju run karapace/0 set-tls-private-key internal-key="invalid-base64-key-!!!"` → `UnicodeDecodeError` ✗ |
| — | `juju run karapace/0 set-password username=operator password=x` — correctly blocked, "Unit is not healthy" (unit was in error state) ✓ |

## Observed behaviour

### Snap installed and running
```bash
juju exec --unit karapace/0 -- snap services
# charmed-karapace.daemon           disabled  active
# charmed-karapace.statsd-exporter  disabled  active
```
Snap revision 16, held.

### Karapace config
Read live from `/snap/charmed-karapace/16/etc/karapace/karapace.config.json` (karapace/0, after the TLS hook crash):
```json
{
  "host": "127.0.0.1",
  "advertised_hostname": "localhost",
  "bootstrap_uri": "localhost:9092",
  "sasl_bootstrap_uri": "localhost:9092",
  "statsd_host": "127.0.0.1"
}
```
Karapace log (repeating, pre-TLS-crash):
```
aiokafka Thread-1 (_start_loop) ERROR Unable connect to ":9092": [Errno -2] Name or service not known
karapace.core.coordinator.master_coordinator Thread-1 (_start_loop) WARNING Kafka client bootstrap failed.
KafkaError{code=_ALL_BROKERS_DOWN, ...sasl_plaintext://localhost:9092/bootstrap: Connection refused}
```
The Kafka broker is at `10.5.87.189:9092`, confirmed from `juju show-unit kafka/0` (`ingress-address: 10.5.87.189`, relation data `endpoints: :9092`). The relation carries a bare-port endpoint with no host, and Karapace resolves that to `localhost:9092`.

**Note on host resolution (unverified detail):** peer relation unit data for both units was repeatedly confirmed to lack `private-address`/`hostname`/`ip` (only `ingress-address` + `egress-subnets` present), consistent with `KarapaceServer.host` (`src/core/models.py:107`) returning `""`. However, the live config snapshot above shows `host: "127.0.0.1"`, not an empty string — the working notes flag this as an unresolved inconsistency and could not confirm whether the rendered config falls back to a localhost default when `host` is empty, or whether the peer-data read genuinely differs from what `juju show-unit` displays. Independent of this, the TLS crash (below) demonstrates that an empty string does reach `TLSHandler._sans` at the point the CSR is generated, so the empty-host condition is real for at least that code path even if its effect on `bootstrap_uri`/`host` in the rendered config is not fully nailed down. Treat the "config host is empty" framing as **(unverified)**; the "empty string reaches SAN generation" framing is directly confirmed by the crash traceback.

### Peer relation unit data — Juju 4.x change
**karapace/0** (leader, machine 0):
```json
{"egress-subnets": "10.5.87.200/32", "ingress-address": "10.5.87.200"}
```
**karapace/1** (scale-up, machine 6):
```json
{"egress-subnets": "10.5.87.89/32", "ingress-address": "10.5.87.89"}
```
No `private-address`, `hostname`, or `ip` in either. Peer **app data** is `{}` on both units — no `operator-password` stored, because karapace never got far enough to receive credentials from Kafka before entering error state. `KarapaceServer.host` at `src/core/models.py:107` iterates `["hostname", "ip", "private-address"]` — none present.

### TLS integration causes unrecoverable hook crash
```
ValueError: '' does not appear to be an IPv4 or IPv6 address
  File ".../tls_certificates_interface/v4/tls_certificates.py", line 848, in generate_csr
    _sans.extend([x509.IPAddress(ipaddress.ip_address(san)) for san in sans_ip])
```
Chain: empty `host` → `TLSHandler._sans["sans_ip"] = [""]` (`src/events/tls.py:150`) → `TLSCertificatesRequiresV4.generate_csr` → `ipaddress.ip_address("")` raises. The `certificates-relation-created` hook exits 1; the unit enters `error` and Juju retries every ~10s indefinitely.

### Recovery from error state
Removing the TLS relation does not clear the error state — the uniter keeps retrying the same failing hook. `juju resolve karapace/0` was run; it re-triggered the hook, which failed again with the identical `ValueError`. The unit stayed in `error`. There is no operator-side recovery short of fixing the code and refreshing the charm.

### Scale-down and machine cleanup
`juju remove-unit karapace/1 --force`:
- karapace/1 → `terminated lost` (not `dead`)
- machine 6 → `stopped` (not destroyed)
- grafana-agent/1 remains in the model, `error idle` from an earlier `cos-agent-relation-joined` crash
- karapace/0 still `error`, hook still retrying

Stopped-but-not-destroyed machines are expected Juju behaviour for machine charms, but they accumulate in the model unless separately destroyed.

### `set-tls-private-key` with invalid input
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8a in position 0: invalid start byte
  File "src/events/tls.py", line 138, in _set_tls_private_key
    else base64.b64decode(key).decode("utf-8")
```
The action tests the input against a PEM regex; if it doesn't match, it tries a base64 decode. The decode succeeds (base64 is permissive) but the result isn't valid UTF-8, and the crash is uncaught.

### `get-password` raises uncaught KeyError
```
unit-karapace-0: 21:11:35 WARNING unit.karapace/0.get-password Uncaught KeyError in charm code: 'operator'
```
`src/events/password_actions.py:90` indexes `internal_user_credentials[ADMIN_USER]` directly; when peer app data has no `operator-password` (confirmed empty via `juju show-unit`), this raises.

### Update-status interval: ~5 minutes
All detection of service failure, Kafka disconnects, and recovery depends on this periodic check — no hooks fire on snap restart or Kafka recovery outside of it.

### COS / grafana-agent integration
- grafana-agent subordinate deployed and active on machine 0
- Karapace metrics reachable at `localhost:8081/metrics` (confirmed via curl)
- OTelCol not installed: ports 14317 (OTLP) and 8082 (OTELCol Prometheus exporter) both closed
- `log_slots` config (`charmed-karapace:logs`) would forward logs through grafana-agent, but requires OTELCol, which is absent
- Prometheus alert rules are structured correctly and would be served if OTELCol worked
- On scale-up, grafana-agent/1 (subordinate on machine 6) crashed in `cos-agent-relation-joined` with `ValueError: subordinate relation cos-agent:12 should have exactly one unit` and stayed `error idle`. The `cos-agent` interface has `limit: 1` in metadata, which conflicts with multiple karapace units each getting their own grafana-agent subordinate.
- COS metrics pipeline is non-functional without the OTELCollector snap

### Actions tested
| Action | Result |
|---|---|
| `get-password` | ✗ uncaught `KeyError: 'operator'` when peer credentials unavailable |
| `set-password username=operator` | ✓ username enum validation works |
| `set-password username=baduser` | ✓ correctly rejected |
| `set-password username=operator password=short` | ✗ accepted a 5-char password (health guard blocked the actual test run, but no length check exists) |
| `set-tls-private-key` (auto-generated) | ✓ generates key, stores in peer data, emits `RefreshTLSCertificatesEvent` |
| `set-tls-private-key internal-key="invalid-base64-key-!!!"` | ✗ `UnicodeDecodeError`, action crashes instead of failing gracefully |

### Scale-up observation
`juju add-unit karapace -n 1` created machine 6 (~4 min to "Running", same as initial deploy). karapace/1 ran its full lifecycle (install → cos-agent → restart → kafka → config-changed → start → kafka-changed → kafka-joined) and landed on `waiting: internal credentials not yet added` — same state as the leader, and with the same missing-`private-address` peer data.

### Subordinate charm follows main unit state
grafana-agent/1 tracked machine provisioning correctly (`maintenance: (install) Installing grafana-agent snap`). grafana-agent/0 went to `error` when karapace/0 entered error state — hook failure on the principal propagated to the subordinate.

## Findings

### Kafka charm reports malformed broker endpoint `:9092`
- **Severity**: critical
- **Kind**: bug
- **Where**: Kafka relation data (bug in the Kafka charm, not this repo); consumed at `src/managers/config.py:74`
- **Evidence**: `juju show-unit kafka/0` shows relation `endpoints: ":9092"` (bare port). Karapace resolves this to `localhost:9092`, confirmed in the live config (`bootstrap_uri`/`sasl_bootstrap_uri: "localhost:9092"`). The real broker is at `10.5.87.189:9092` (kafka's `ingress-address`).
- **Impact**: Even if the host bug is fixed, Karapace tries to reach a Kafka on its own machine that isn't there — connection refused, repeating in the log. This is the only failure mode that reproduces cleanly and directly explains why the ~20s active window closed.
- **Fix**: Report the correct host from the Kafka charm. As a workaround in this charm, detect a bare-port endpoint and substitute the peer unit's ingress address:
  ```python
  if endpoint.startswith(':'):
      endpoint = f"{kafka_unit_address}{endpoint}"
  ```
- **Linter rule**: not established (relation data used without validation; not mechanically checkable).

### TLS integration crashes hook → unrecoverable error state
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/events/tls.py:150` (`TLSHandler._sans` builds `sans_ip: [self.charm.context.server.host]` with an empty string)
- **Evidence**: `juju integrate karapace:certificates self-signed-certificates:certificates` crashed `certificates-relation-created` with `ValueError: '' does not appear to be an IPv4 or IPv6 address` (traceback through `tls_certificates_interface/v4/tls_certificates.py:848`). Unit enters `error`, hook retried every ~10s indefinitely. `juju resolve karapace/0` and removing the relation both failed to clear it.
- **Impact**: A single, ordinary integration command permanently breaks the unit; no operator recovery path exists short of a code fix and `juju refresh`.
- **Fix**: Filter empty strings before building the SAN list:
  ```python
  "sans_ip": [ip for ip in [self.charm.context.server.host] if ip],
  ```
- **Linter rule**: "SAN list built from potentially-empty string without filtering" — not mechanically checkable.

### Empty `host` feeds cascading failures (host lookup lacks `ingress-address` fallback)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/core/models.py:107` (`KarapaceServer.host` fallback chain `["hostname", "ip", "private-address"]`)
- **Evidence**: Peer relation unit data for both karapace/0 and karapace/1 lacks `private-address`/`hostname`/`ip` under Juju 4.0.12, leaving only `ingress-address`/`egress-subnets`. This directly explains the empty string observed reaching `TLSHandler._sans`. **(unverified)**: whether this also produces an empty `host` in the rendered Karapace config is not confirmed — the live config snapshot shows `host: "127.0.0.1"`, and the notes flag this discrepancy as unresolved.
- **Impact**: Feeds directly into the TLS SAN crash above; may or may not also affect Karapace's bind address.
- **Fix**: Add `ingress-address` to the fallback chain, or write `private-address`/an FQDN into peer unit data explicitly on `relation-created`:
  ```python
  for key in ["hostname", "ip", "private-address", "ingress-address"]:
  ```
- **Linter rule**: "Peer relation unit data read without `ingress-address` in fallback lookup" — not mechanically checkable without runtime observation.

### `set-tls-private-key` crashes with UnicodeDecodeError on invalid key
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/events/tls.py:138` (`base64.b64decode(key).decode("utf-8")`)
- **Evidence**: `juju run karapace/0 set-tls-private-key internal-key="invalid-base64-key-!!!"` → `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8a in position 0: invalid start byte`.
- **Impact**: A typo or a non-PEM/non-UTF8 base64 string crashes the action instead of returning a clear error.
- **Fix**:
  ```python
  try:
      decoded = base64.b64decode(key).decode("utf-8")
  except (binascii.Error, UnicodeDecodeError):
      event.fail("Invalid key: must be a valid PEM-formatted or base64-encoded private key.")
      return
  ```
- **Linter rule**: "base64 decode without Unicode error handling" — mechanically checkable with a custom ruff rule.

### `get-password` raises uncaught KeyError
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/events/password_actions.py:90` (indexes `internal_user_credentials[ADMIN_USER]` without a guard)
- **Evidence**: Debug log 21:11:35: `WARNING unit.karapace/0.get-password Uncaught KeyError in charm code: 'operator'`, reproduced when peer app data has no `operator-password` (confirmed empty via `juju show-unit`).
- **Impact**: Any situation where internal credentials aren't yet set (fresh deploy, secret rotation gap, corrupted state) turns a normal action call into an unhandled exception instead of a clear failure message.
- **Fix**:
  ```python
  credentials = self.charm.context.cluster.internal_user_credentials
  if ADMIN_USER not in credentials:
      event.fail("Internal credentials not yet available.")
      return
  event.set_results({"username": ADMIN_USER, "password": credentials[ADMIN_USER]})
  ```
- **Linter rule**: "Dict indexed without existence check in action handler" — mechanically checkable with ruff/custom rule.

### `_on_config_changed` unconditionally sets ActiveStatus, masking Kafka connectivity failures
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:132`
- **Evidence**: Status history shows the unit active for ~20s between `kafka-relation-changed` and the next `update-status`, during which Karapace was already failing to connect to Kafka.
- **Impact**: A ~20s (until the next `update-status`) misleading Active window on every Kafka relation change.
- **Fix**: Check `kafka_manager.brokers_active()` before setting `ActiveStatus()` at the end of the handler.
- **Linter rule**: not established (not mechanically checkable).

### `planned_units` compared as a method reference instead of called
- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/provider.py:79`
- **Evidence**: `if self.charm.app.planned_units == 0:` compares a bound method to `int`, always `False`.
- **Impact**: The intended early-exit guard on relation-broken (skip cleanup when the app is scaling to zero) never fires; cleanup always runs, including during `remove-application`.
- **Fix**: `if self.charm.app.planned_units() == 0:`
- **Linter rule**: mechanically checkable, e.g. ruff `E713`/custom rule for bound-method-vs-literal comparisons.

### `healthy` property doesn't check Kafka connectivity
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:201`
- **Evidence**: `healthy` only checks `workload.active()` and `ready_to_start` (credentials present); it never checks `kafka_manager.brokers_active()`.
- **Impact**: `on_subject_requested` defers when `healthy` is False, but `healthy` returns True while Karapace is running yet unable to reach Kafka — the handler proceeds to create users/ACLs that Karapace can't actually serve.
- **Fix**: Include a Kafka reachability check in `healthy`.
- **Linter rule**: not established.

### Unit stuck in unrecoverable error state after TLS crash
- **Severity**: high
- **Kind**: ux
- **Where**: Juju unit lifecycle (root cause `src/events/tls.py:150`)
- **Evidence**: After the TLS hook crash, `juju remove-relation karapace:certificates self-signed-certificates` removed the relation but the unit stayed `error`; Juju kept retrying the hook every ~10s indefinitely.
- **Impact**: The only recovery path is a code fix and `juju refresh` — a single integration mistake permanently breaks the unit.
- **Fix**: Same as the TLS SAN fix above.
- **Linter rule**: not applicable.

### `juju resolve` does not clear the error state
- **Severity**: high
- **Kind**: ux
- **Where**: Juju unit lifecycle
- **Evidence**: `juju resolve karapace/0` re-ran the hook, which failed again with the identical `ValueError`; the unit remained in `error`.
- **Impact**: Even an operator who understands the problem and follows the documented recovery command cannot recover the unit without a code fix.
- **Fix**: Same as the TLS SAN fix above.
- **Linter rule**: not applicable.

### COS observability pipeline broken — OTELCol not installed
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:113-121` (OTelCol setup code present, but the `opentelemetry-collector` snap is not installed)
- **Evidence**: Ports 14317 (OTLP) and 8082 (OTELCol Prometheus exporter) closed after integrating grafana-agent. Karapace's own metrics are reachable at `localhost:8081/metrics`. `metrics_endpoints` in `COSAgentProvider` advertises port 8082, where nothing listens. Separately, scale-up crashed grafana-agent/1 with `ValueError: subordinate relation cos-agent:12 should have exactly one unit`, tied to `limit: 1` on the `cos-agent` interface.
- **Impact**: COS integration is non-functional out of the box, and scaling the principal charm breaks the subordinate.
- **Fix**: Install `opentelemetry-collector` in the install hook, or point `metrics_endpoints` at port 8081 directly. Investigate `cos-agent` `limit: 1` interaction with multi-unit deployments.
- **Linter rule**: not established.

### Scale-down leaves karapace/1 `terminated lost`; machine stopped but not destroyed
- **Severity**: medium
- **Kind**: ux
- **Where**: Juju machine lifecycle
- **Evidence**: `juju remove-unit karapace/1 --force` left karapace/1 as `terminated lost` and machine 6 as `stopped` (not destroyed); grafana-agent/1 also lingered in `error`.
- **Impact**: Stopped machines and stuck subordinates accumulate in the model after routine scale-down.
- **Fix**: Document that a separate `juju destroy-machine` is required; consider surfacing this in charm docs.
- **Linter rule**: not applicable.

### `set-password` accepts trivially short passwords
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/events/password_actions.py:42-43`
- **Evidence**: `set-password username=operator password=short` (5 chars) was accepted in the deployment log; no length/complexity check exists in the handler. In the actual test run this was later masked by the `healthy` guard failing for an unrelated reason (unit in error state).
- **Impact**: Weak passwords can be set into the Karapace authfile with no pushback.
- **Fix**:
  ```python
  if len(new_password) < 16:
      event.fail("Password must be at least 16 characters.")
      return
  ```
- **Linter rule**: "Action handler accepts password parameter without length validation" — not mechanically checkable.

### `remove_stores` uses a shell glob in a non-shell subprocess call
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/tls.py:66` (`self.workload.exec(command="rm -rf *.pem *.key", ...)`, executed with `shell=False`)
- **Evidence**: `workload.exec()` calls `subprocess.check_output(command, shell=False, ...)`; with `shell=False` the `*` glob is passed literally, so no files match. Code has a `FIXME` acknowledging this.
- **Impact**: Old TLS certs/keys are never cleaned up after `tls-relation-broken`.
- **Fix**: Use Python's `glob` + `os.remove()`, or run with `shell=True` and proper quoting.
- **Linter rule**: "Shell glob pattern used with `shell=False` in subprocess" — mechanically checkable.

### Unit test fixtures mask the `private-address` gap
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py:33,43` (`peer_relation` fixture always sets `local_unit_data={"private-address": "treebeard"}`)
- **Evidence**: The `peer_relation_no_data` fixture omits `private-address` but is only exercised in missing-credentials tests, not config rendering. No test covers "credentials present, host empty".
- **Impact**: Unit tests pass while the production scenario (Juju 4.x with no `private-address`) fails.
- **Fix**: Add a fixture with credentials present but `private-address` absent, and assert on the rendered config/SANs.
- **Linter rule**: not applicable.

### `KafkaManager.brokers_active()` may fail silently when TLS is enabled
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/kafka.py:29` (`cafile_path=self.workload.paths.ssl_cafile`)
- **Evidence**: `ssl_cafile` may be `None` before the CA file exists; the client may fail to connect without a clear signal.
- **Impact**: False `KAFKA_NOT_CONNECTED` blocks with an unclear cause when TLS is being set up.
- **Fix**: Guard: if TLS is enabled and the CA file doesn't exist yet, return `False` with a specific status message.
- **Linter rule**: not established.

### `cluster-relation-created` observer missing
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:88-93`
- **Evidence**: No observer registered for the peer relation's `relation-created` event; `_on_start` checks `self.context.peer_relation` but by then the relation already exists, and nothing writes an address into peer unit data.
- **Impact**: Any fix limited to leader startup won't help scale-up units, which hit the same missing-address condition on their own `relation-created`.
- **Fix**:
  ```python
  self.framework.observe(self.on[PEER].relation_created, self._on_peer_created)

  def _on_peer_created(self, event):
      self.context.server.update({"private-address": socket.getfqdn()})
  ```
- **Linter rule**: "Peer relation exists in metadata but no `relation_created` observer registered" — not mechanically checkable without metadata inspection.

### `extra_user_roles` passed as raw string to `add_acl`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/events/provider.py:62`
- **Evidence**: `pyright src/events/provider.py` reports `Argument of type "str" cannot be assigned to parameter "role" of type "Role"` (`Role = Literal["admin", "user"]`).
- **Impact**: An unexpected role value from a requirer is passed through untyped/unvalidated.
- **Fix**: `role = extra_user_roles if extra_user_roles in ("admin", "user") else "user"`
- **Linter rule**: pyright `reportArgumentType`.

### `CharmConfig` is empty — no structured user configuration
- **Severity**: low
- **Kind**: docs
- **Where**: `src/core/structured_config.py:15` (`class CharmConfig(BaseConfigModel): pass`)
- **Evidence**: No `config.yaml` options beyond relation lifecycle.
- **Impact**: No operator-facing tunables currently exist.
- **Fix**: Add structured config as needed.
- **Linter rule**: not applicable.

### Dead commented-out code in `literals.py`
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/literals.py:41-42` (`METRICS_RULES_DIR`, `LOGS_RULES_DIR` commented out)
- **Evidence**: confirmed by inspection.
- **Fix**: Delete the two lines.
- **Linter rule**: not mechanically checkable without a "no commented-out code" rule.

## Worth copying

- **Status enum with log levels** (`src/literals.py`): `Status` dataclass pairs a Juju status with a `DebugLevel`; `_set_status` uses `getattr(logger, log_level.lower())` to pick the log call. Clean way to tie status severity to log verbosity.
- **Event handler decomposition** (`src/events/`): handlers split by domain (`kafka.py`, `tls.py`, `provider.py`, `password_actions.py`), each a separate `Object`. Keeps `charm.py` small and eases unit testing.
- **`WorkloadBase` abstract interface** (`src/core/workload.py`): explicit `start`/`stop`/`restart`/`read`/`write`/`exec`/`active`/`get_version`/`mkpasswd` methods, implemented concretely via the snap library. Makes mocking easy and would ease a k8s port.
- **Parsed authfile as in-memory state** (`src/managers/auth.py`): loads the authfile into an `auth_dict` once, mutates in memory, writes it back atomically. Simple and idempotent.
- **Config diff logging** (`src/charm.py:139`):
  ```python
  logger.info(
      f"OLD CONFIG = {set(rendered_file.items()) - set(self.config_manager.config.items())}, "
      f"NEW CONFIG = {set(self.config_manager.config.items()) - set(rendered_file.items())}"
  )
  ```
  Useful for debugging config changes; worth copying to other charms.

## Common-practice notes

| Practice | Status | Notes |
|---|---|---|
| `src/` layout | ✓ | Well structured |
| `lib/charms/` versioning | ✓ | `v0` libraries correctly versioned |
| `charmcraft.yaml` with `poetry` plugin | ✓ | Modern build system |
| Structured config (`TypedCharmBase`) | ✗ | Empty model, no value provided |
| `tox.ini` test environments | ✓ | Correct lint/unit/integration separation |
| Scenario/state-transition unit tests | ✓ | `ops.testing.Context` + `State` |
| Secret handling via `DataPeerData` | ✓ | Uses `additional_secret_fields=SECRETS_UNIT` |
| Lifecycle event coverage | ✗ | Missing `cluster-relation-created` observer |
| `peer_relation_created` handler | ✗ | No handler writes `private-address` |
| Status precedence in `_on_config_changed` | ✗ | Unconditional `ActiveStatus` skips Kafka connectivity check |
| Deprecation warnings in libs | ⚠ | `JujuVersion.from_environ()` deprecated in data-platform-libs and tls-certificates-libs |
| Snap-based workload | ⚠ | Revision pinned and held, no auto-updates |
| No `config.yaml` | ⚠ | No user-facing configuration |
| Commented-out code | ✗ | Stray METRICS/LOGS constants in `literals.py` |
| Subordinate charm for COS | ⚠ | grafana-agent deployed; pipeline broken (OTELCol missing) |
| k8s substrate | ✗ | Machine-only charm; no k8s version in this repo |

## Tests

### Unit tests — 21/21 pass
```bash
PYTHONPATH=lib:src poetry run coverage run --source=src -m pytest tests/unit/ -vv
```
Coverage: 71% overall.

| File | Coverage | Uncovered risk |
|---|---|---|
| `src/events/password_actions.py` | 24% | `_set_password_action` (no length check), `_get_password_action` (no KeyError guard) |
| `src/events/tls.py` | 42% | `_on_certificate_available`, `_set_tls_private_key` (UnicodeDecodeError path), `_sans` (empty-host case) |
| `src/managers/tls.py` | 34% | `remove_stores` (broken glob), `set_ca`, `set_certificate` |
| `src/events/provider.py` | 65% | `_on_relation_broken` (`planned_units() == 0` never true), `on_subject_requested` (healthy doesn't check Kafka) |
| `src/managers/kafka.py` | 60% | `brokers_active` with TLS enabled |

The `peer_relation` fixture always sets `private-address`, masking the Juju 4.x gap; the scenario "credentials present, host empty" is untested.

### Integration tests — not run
Located in `tests/integration/`; require a separate model and full deploy cycle, not executed in this review. Based on code review:
- `test_charm.py` (deploy + kafka integration, scale up/down) — would likely surface the Kafka endpoint and host bugs.
- `test_tls.py` (TLS with `self-signed-certificates`, expects active after TLS integration) — would fail at that step given the TLS hook crash reproduced here.
- `test_password_rotation.py` (`get-password` → `set-password` → `get-password`) — would hit the `KeyError` reproduced here.
- `test_provider.py` (`karapace_client` interface) — `on_subject_requested` defers on `healthy`, which doesn't check Kafka connectivity.
- `test_terraform.py` — smoke test to `blocked: kafka not related`, likely unaffected by the above bugs.

### Linting
- ruff: 0 errors, 0 warnings
- codespell: no issues
- pyright: 1 error — `src/events/provider.py:62`, `Argument of type "str" cannot be assigned to parameter "role" of type "Role"`

## Docs

### README.md
Covers deploy steps for Zookeeper/Kafka/Karapace, relations, TLS enable/disable, schema registration example. Issues found:
- References `latest/edge` for all charms; stable channels exist for Kafka/Zookeeper but not Karapace.
- The TLS section's `juju integrate tls-certificates-operator zookeeper` command is a red herring — zookeeper has no `certificates` interface in this integration pattern; only `kafka` and `karapace` should be shown.
- `juju run karapace/leader set-password password=<password>` omits the required `username=operator` parameter (`required: true` in `actions.yaml`); would fail with a param-missing error as written.
- References `/src/relations/karapace.py` for the `karapace_client` interface — this file does not exist in the repo.

### CONTRIBUTING.md
Practical SDK guidance, refers to Juju SDK docs.

### Charmhub description
Accurate one-paragraph summary of Karapace.

## Open questions

1. Why does Juju 4.x not write `private-address` to peer relation unit data — a regression or an intentional deprecation? Confirmed absent for both initial deploy and scale-up units.
2. Why is peer relation app data `{}` after the TLS hook failure — a consequence of the error state, or a separate Juju 4.x secrets interaction?
3. Is the `:9092` malformed Kafka endpoint specific to the machine substrate, to Juju 4.x, or a known bug in this Kafka charm revision (ch:amd64/kafka-240)?
4. Is grafana-agent/1 crashing on scale-up (`cos-agent:12 should have exactly one unit`) expected behaviour for a principal charm with a `limit: 1` cos-agent relation?
5. Is `limit: 1` on the `karapace` client interface intentional, given Karapace can serve multiple clients?
6. The `restart` peer relation is declared (`rolling_op` interface) but never handled in code — is it planned or dead?
7. Should the charm install `opentelemetry-collector` itself, or should COS integration be documented as requiring it separately?
8. TLS integration end-to-end: both the integration test (`test_tls.py`, code-review inspection) and the live reproduction here fail at/around the same point — confirm both must be fixed together once the SAN-filtering fix lands.
9. The discrepancy between "peer data has no `private-address`" and "rendered config shows `host: 127.0.0.1`" is unresolved — needs a maintainer with access to the charm's config-rendering code path to confirm whether a default masks the empty-host condition for `bootstrap_uri`/bind address, or whether the two data points are inconsistent for another reason.
