# snmp-exporter-operator

A thin, well-structured machine charm wrapping the `prometheus-snmp-exporter` snap, exposing metrics via `cos-agent`. The config model (simple targets vs custom config files) is clear, status precedence is correct, and the `cos-agent`/tracing integration works end-to-end on LXD. It is not production-ready as-is: the charm crashes unrecoverably in `__init__` on any non-snapd substrate (e.g. k8s), several hook handlers propagate uncaught exceptions into `error` state, a dead workload service is not auto-recovered, and the `receive-ca-cert` relation cannot actually receive certificates from `self-signed-certificates` due to a v0/v1 protocol mismatch. A maintainer should first guard `SnapCache()` in `__init__` and wrap the install/start/yaml-parsing paths in `try/except`, then fix or document the certificate-transfer incompatibility.

| | |
|---|---|
| Repo | `canonical/snmp-exporter-operator` @ `da31f4c` (2026-06-29) |
| Charms | `snmp-exporter` |
| Substrate | machine (LXD); k8s attempt failed with `SnapError` in `__init__` |
| Deployed | yes — `concierge-lxd` (Juju 3.6.27), channel `0.24/edge` rev 26; k8s (`concierge-k8s-4`, Juju 4.0.12) failed in install hook |
| Reviewed | 2026-08-24 |

## What it does

**Deployed vs local code**: deployed from charmhub channel `0.24/edge` rev 26. Local `HEAD` is rev 25 (`da31f4c`, 2026-06-29), one revision behind. All live observations are of rev 26 from charmhub. A locally packed rev 25 (`snmp-exporter_ubuntu@24.04-amd64.charm`, 6.2 MB) was also deployed to k8s and showed the identical `SnapError` crash.

**Two config modes**:
1. **Simple targets mode**: operator sets `targets` (comma-separated IPs/hostnames); charm generates a default SNMP scrape config using the `if_mib` module with community `public_v2`.
2. **Custom files mode**: operator supplies both `config_file` (SNMP MIB config) and `scrape_config_file` (Prometheus scrape jobs); charm writes the SNMP file into the snap data directory and restarts the service.

**`cos-agent` is a bidirectional data channel**: `COSAgentProvider` (snmp-exporter as PROVIDER) writes `metrics_scrape_jobs` into snmp-exporter's own **unit databag** on the `cos-agent` relation (`relation.data[self._charm.unit][data.KEY] = data.json()`, `lib/charms/grafana_agent/v0/cos_agent.py:695`) — correct for this interface, which stores per-unit data in the unit databag rather than the app databag. `grafana-agent` (as `CosAgentRequirer`) reads these scrape configs. The same relation carries `receivers` (tracing endpoints) from grafana-agent's unit databag, read via `CosAgentRequirer.get_all_endpoints()` to configure OTLP HTTP tracing — only works when grafana-agent is itself related to a tracing backend (tempo).

**`receive-ca-cert` relation**: uses `CertificateTransferRequires` (requirer side of `certificate_transfer`) to receive CA certificates, writing them to `/etc/snmp-exporter/receive-ca-cert.crt`. Against `self-signed-certificates` this never works — see Findings.

**Snap staleness**: open issue #15 confirms the snap is significantly outdated (rev 10, v0.24.1) vs upstream. `SNAP_CHANNEL` is hardcoded, not operator-configurable.

## Deployment log

**LXD substrate** (`concierge-lxd`, Juju 3.6.27):

```
juju add-model rv-snmp-exporter localhost --controller concierge-lxd
juju deploy snmp-exporter --channel edge  # → rev 26, ubuntu@24.04
```

Machine provisioning took ~6 min (container bootstrap + cloud-init apt dist-upgrade + snap install). Charm correctly entered `blocked` (no config) after deploy.

```
juju config snmp-exporter targets="192.168.1.1"
```

→ `active` within seconds. Snap service (`prometheus-snmp-exporter.snmp-exporter`) running, listening on `:9116`. Metrics endpoint responds.

Tested transitions:
- `targets` + `config_file` (conflicting) → `blocked` "Cannot set both 'targets' and config files"
- `config_file` only (no `scrape_config_file`) → `blocked` "Please set either targets or both config files"
- both config files set → `active`; `snmp.yml` written to `/var/snap/prometheus-snmp-exporter/10/snmp.yml`; service restarted
- switch from config-file mode back to targets mode → `active`; `snmp.yml` NOT written (no restart needed)
- no-op config change (same targets) → `config-changed` hook does NOT fire (Juju correctly skips it)

**Extended lifecycle tests**:

- Scale up (`juju add-unit snmp-exporter -n 1`) → machine 1 provisioned in ~90s, both units `active`. Hook sequence on new unit: `install` → `start` → `config-changed` → `update-status` (idle).
- Scale-down (`juju remove-unit`) works correctly.
- `juju refresh snmp-exporter` → "already up-to-date". No newer revision on charmhub.
- `juju resolved` after error state → re-runs the same failing hook with the same bad config → fails again. Recovery requires a config change, not `juju resolved`.
- Unit restart (`systemctl restart snap...`) → metrics briefly interrupted, charm reports `active` throughout (no hook fires, no status change needed).

**k8s substrate** (`concierge-k8s-4`, Juju 4.0.12):

```
juju deploy snmp-exporter --channel edge  # → rev 26, ubuntu@24.04
```

The charm (machine type, no `containers:` in `charmcraft.yaml`) is installed into a k8s pod. The `install` hook fires but `__init__` crashes immediately:

```
charms.operator_libs_linux.v2.snap.SnapError: snapd is not installed or not in /usr/bin
```

`SnapCache.__init__()` raises `SnapError` when snapd is absent. The crash happens before any handler runs; the unit goes to `error` state: `hook failed: "install"`. Unit log shows the full traceback ending at `src/charm.py:33`:
```python
self.snap = snap.SnapCache()["prometheus-snmp-exporter"]
```
No graceful degradation; the unit remains in error state indefinitely. Locally packed rev 25 produces the identical crash.

**`grafana-agent` machine charm** (`concierge-lxd`):
- Deployed alone (`juju deploy grafana-agent --channel 0.44/stable`) → 0 units, machine never provisioned.
- After `juju relate snmp-exporter grafana-agent` → grafana-agent unit provisions immediately on the same machine as snmp-exporter (machine 0). The `cos-agent` relation bootstraps grafana-agent's machine provisioning.
- grafana-agent enters `blocked` with "Missing ['grafana-cloud-config']|['grafana-dashboards-provider']|['logging-consumer']|['send-remote-write']|['tracing...'" — expected, needs at least one telemetry integration.
- `juju relate snmp-exporter grafana-agent` succeeds even while grafana-agent is `blocked`.
- `juju remove-application snmp-exporter --force` while `cos-agent` is active → grafana-agent subordinate is also removed (correct subordinate cleanup).

**cert_transfer integration** (`self-signed-certificates` from charmhub rev 264):

```
juju deploy self-signed-certificates --channel latest/stable
juju relate snmp-exporter self-signed-certificates
```

- `receive-ca-cert-relation-created` fires at 12:32:35. `_on_relation_changed` tries `ProviderApplicationData().load()` on the app databag, which contains only Juju infrastructure fields (`egress-subnets`, `ingress-address`, `private-address`), not JSON certificate data. `DataValidationError` is raised, caught, and an empty set returned. `_on_cert_transfer_available` writes a 1-byte file (`\n`). Log: `Error parsing relation databag: {'egress-subnets': '...', 'ingress-address': '...', 'private-address': '...'}`.
- `receive-ca-cert-relation-joined` fires at 12:35:39: same error, same 1-byte file.
- `receive-ca-cert-relation-changed` fires at 12:35:42 (self-signed-certificates wrote CA to unit databag): v1 code tries to parse the unit databag (`ca`, `certificate`, `chain` — v0 format) as v1 JSON (`certificates` set). Fails with `invalid databag contents: expecting json`. `DataValidationError` is caught; v0 fallback does not run because the exception fires before `if not certificates`. File stays 1 byte.
- `receive-ca-cert-relation-changed` fires again at 12:35:43: no error logged, but cert file still 1 byte. v0 fallback may have returned a CA from the unit databag but `_reconcile_charm_tracing()` did nothing since no `cos-agent` relation exists → no harm.
- `juju remove-relation snmp-exporter self-signed-certificates` → `receive-ca-cert-relation-broken` fires; `_on_cert_transfer_removed` correctly deletes the cert file; `/etc/snmp-exporter/` is now empty.

Root cause is in `charmlibs-interfaces-certificate-transfer`: the v0 fallback (`if not certificates and relation.units:`) sits inside the `try` block after the failing v1 parse, so when v1 raises `DataValidationError` the fallback never runs. snmp-exporter is using the library correctly; the library/provider combination is the problem.

**`cos-agent` integration end-to-end** (new model `rv-snmp-cos-agent`):
- `juju relate snmp-exporter grafana-agent` → both hooks fire correctly.
- snmp-exporter log on `cos-agent-relation-changed`: `WARNING cos-agent:1: Endpoint for tracing wasn't provided as tracing backend isn't ready yet.` — correct, grafana-agent has no tracing backend.
- grafana-agent log: `WARNING cos-agent:1: <class '__main__.GrafanaAgentMachineCharm'>._server_cert is None; sending traces over INSECURE connection.` — correct, no tracing backend.
- `juju show-unit grafana-agent/0`: snmp-exporter writes `metrics_scrape_jobs` with 2 jobs (`snmp-exporter_0_snmp` targeting `192.168.1.1`, `snmp-exporter_1_snmp-exporter` self-scraping `localhost:9116`), `metrics_alert_rules` (`HostDown`, `HostMetricsMissing`), `tracing_protocols: ["otlp_http"]` — all in the **unit databag** (`relation.data[snmp-exporter/0]`). grafana-agent reads this from its side.
- grafana-agent writes `receivers: [{"protocol": {"name": "otlp_http", "type": "http"}, "url": null}]` to its own unit databag — null URL because no tracing backend is related.

## Observed behaviour

**Invalid targets accepted silently**: `juju config snmp-exporter targets="not-an-ip!!!"` is accepted without validation; `config-changed` fires and the charm stays `active`. The exporter will fail at the network level, but the charm gives no in-charm feedback. Defensible (the exporter itself handles resolution) but means typos produce no signal.

**Tracing endpoint absent handled correctly**: when grafana-agent has no tracing backend related, it writes `{}` to its unit databag; `CosAgentRequirerUnitData.load({})` defaults to `receivers: []`; `_get_tracing_endpoint` raises `ProtocolNotFoundError`; `charm_tracing_config` catches it and logs the expected warning. `ops_tracing.set_destination(url=None)` is a safe no-op (skips saving if destination already `None`). No crash, no broken state.

**cert_transfer relation with no cos-agent present**: with cert_transfer related but `cos-agent` absent, `_reconcile_charm_tracing` returns `(None, None)`. `_on_cert_transfer_available` still writes a 1-byte file on relation-created; `_on_cert_transfer_removed` correctly deletes it on relation-broken. Cleanup is correct, but the transient empty file matters when the provider actually has data (see below).

**`CertificateTransferRequires` vs `self-signed-certificates`: protocol mismatch**: `self-signed-certificates` implements `send-ca-cert` (provider side of `certificate_transfer`) and writes v0 data (`{'ca': ..., 'chain': '[]'}`) to the **app databag**. `receive-ca-cert` uses `CertificateTransferRequires`, the v1 requirer, which reads JSON from the **unit databag**. `ProviderApplicationData().load()` raises `DataValidationError` on the v0 app-databag data; the v0 fallback never runs because it is inside the same `try` block. Result: snmp-exporter can never read CA certificates from `self-signed-certificates` through this library — not just a library bug but a version incompatibility between the two sides. Confirmed log (01:13:24):
```
ERROR ... invalid databag contents: expecting json. {'ca': '-----BEGIN CERTIFICATE-----...', 'chain': '[]', 'egress-subnets': '...', ...}
```
1-byte `/etc/snmp-exporter/receive-ca-cert.crt` confirmed; file correctly deleted on `relation-broken`.

**Timing**:
- LXD machine bootstrap: ~6 min (container + cloud-init + snap)
- Charm install hook: ~80s (dominated by snap install)
- Config change → active: ~5s
- Scale-up (add unit): ~90s from `add-unit` to `active`
- `update-status`: every 5 min (standard interval)
- k8s install hook failure: instant crash in `__init__` (~1s)
- grafana-agent machine provisioning (triggered by `cos-agent`): ~30s from `juju relate` to unit in maintenance installing snap

**Resource use**:
- snmp-exporter snap service: ~30 MB RSS (LXD container)
- `prometheus-snmp-exporter` snap: rev 10, version 0.24.1
- Port 9116 TCP listening confirmed
- No additional resource use from the charm itself

**Hook firing**:
- `config-changed` fires on real changes; Juju correctly skips no-op changes
- `update-status` every 5 min — the only hook detecting external state changes (service killed, network change, etc.)
- `receive-ca-cert-relation-created`/`-joined`/`-changed` fire correctly through the relation lifecycle
- `receive-ca-cert-relation-broken` fires on removal
- Scale-up unit: `install` → `start` → `config-changed` → idle
- Scale-down unit: `stop` fires on removed unit
- `cos-agent-relation-joined` fires on grafana-agent when it joins
- `cos-agent-relation-changed` fires on snmp-exporter both when grafana-agent joins and when grafana-agent's own `relation-changed` fires

**grafana-agent relation**: works correctly end-to-end. `COSAgentProvider` writes `metrics_scrape_jobs`, `metrics_alert_rules`, `tracing_protocols` to snmp-exporter's own unit databag (correct for this interface). grafana-agent reads these and goes `blocked` waiting for further integrations (expected). Tracing endpoint is `null` because grafana-agent has no tracing backend; snmp-exporter correctly warns and disables tracing. `_on_cos_agent_relation_changed` reconciles tracing on every relation change.

**Snap channel**: pinned to `0.24/stable`. Open issue #15 confirms it is significantly outdated vs upstream (rev 10 ships v0.24.1).

**No actions**: the charm defines no Juju actions; all operator interaction is via config.

**grafana-agent standalone provisioning**: the `grafana-agent` machine charm (rev 827, `0.44/stable`) does not provision a machine when deployed standalone — only when a `cos-agent` relation is established. Expected for a subordinate.

## Findings

### `SnapCache()` in `__init__` crashes on non-snapd systems
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:33`
- **Evidence**: `self.snap = snap.SnapCache()["prometheus-snmp-exporter"]` with no `try/except`. Deployed on k8s (`concierge-k8s-4`, Juju 4.0.12): install hook fires, `SnapCache.__init__()` raises `SnapError("snapd is not installed or not in /usr/bin")`. Exception propagates, crashing the charm before any handler runs; unit enters `error` state: `hook failed: "install"`. Confirmed identical with a locally packed rev 25 charm. Traceback ends at `src/charm.py:33`.
- **Impact**: Deploying to a non-snapd substrate (e.g. k8s) leaves the unit unrecoverable without remove/re-deploy, with no actionable message.
- **Fix**: Wrap `SnapCache()` in `try/except snap.SnapError`; on failure store a sentinel (e.g. `None`) and have handlers check it, setting `BlockedStatus("snapd is required but not installed on this substrate")`.
- **Linter rule**: unconditional external-system call in `__init__` without try/except — mechanically checkable.

### `yaml.safe_load` in `snmp_config` property raises uncaught on malformed input
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:94`
- **Evidence**:
  ```python
  if config_file := cast(str, self.config["config_file"]):
      snmp_config = yaml.safe_load(config_file)  # can raise yaml.YAMLError
  ```
  Injected `juju config snmp-exporter config_file="not: [yaml"` → hook failed with `yaml.parser.ParserError`; unit went to `error` (`hook failed: "config-changed"`). `juju resolved` re-runs the same failing hook and fails again; only a valid config change recovers.
- **Impact**: Malformed YAML gives the operator a raw traceback instead of a `BlockedStatus` message, and the unit is stuck in `error` until a valid config is supplied.
- **Fix**: Wrap `yaml.safe_load()` in `try/except yaml.YAMLError`, returning `None` on failure — `set_status()` already handles `None` by setting `BlockedStatus`.
- **Linter rule**: `yaml.safe_load` without try/except — mechanically checkable.

### `CertificateTransferRequires` v1 library vs `send-ca-cert` v0 provider: protocol incompatibility
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:24` (`CA_CERT_PATH`); `deps/charmlibs/interfaces/certificate_transfer/_certificate_transfer.py:577-595` (v1 try block swallows v0 fallback)
- **Evidence**: Related to `self-signed-certificates` (rev 264). Unit log at 01:13:24:
  ```
  ERROR invalid databag contents: expecting json. {'ca': '-----BEGIN CERTIFICATE-----\n  ...\n-----END CERTIFICATE-----\n', 'chain': '[]', 'egress-subnets': '10.5.87.108/32', 'ingress-address': '10.5.87.108', 'private-address': '10.5.87.108'}
  ```
  `/etc/snmp-exporter/receive-ca-cert.crt` confirmed 1 byte (`\n`). `self-signed-certificates` writes v0 (`ca`/`chain`) to the app databag; `CertificateTransferRequires` expects v1 JSON in the unit databag. `ProviderApplicationData().load()` raises `DataValidationError` on the v0 data; the v0 fallback sits inside the same `try` block and never runs.
- **Impact**: snmp-exporter can never read CA certificates from `self-signed-certificates` via this library. TLS validation of the tracing endpoint would fail silently (or fall back to unvalidated HTTP). Any charm pairing `CertificateTransferRequires` with a `send-ca-cert` v0 provider hits the same wall.
- **Fix**: (a) use the `send-ca-cert` provider-side library on the requirer, or (b) document the incompatibility and recommend a v1-compatible TLS provider (e.g. `vault-k8s`, `tls-certificates-operator`), or (c) move the v0 fallback in the library out of the `try` block. Defensively, guard `_on_cert_transfer_available` with `if not event.certificates: return`.
- **Linter rule**: requires-library expects v1 protocol but charm relates to v0 provider — not mechanically checkable without knowing the provider's protocol version.

### External service kill not detected until next hook fires
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:163-168` (`set_status` service check)
- **Evidence**: killed the service via `systemctl stop snap.prometheus-snmp-exporter.snmp-exporter.service`. `juju status` continued to show `active` for ~4 minutes until the next `config-changed`/`update-status` hook. `set_status()` correctly detects `self.snap.services["snmp-exporter"]["active"] is False` and sets `MaintenanceStatus()`, but only runs inside a hook.
- **Impact**: If the service dies for any reason (OOM kill, segfault, external `SIGKILL`), the charm continues reporting `active` for up to ~5 minutes, and does not restart the service — an operator must wait or force a hook with a dummy config change.
- **Fix**: Have `start` attempt `snap.start()` periodically, or add a periodic service-check/recovery loop; be careful not to create a restart loop.
- **Linter rule**: no recovery action on service death — not mechanically checkable.

### Service auto-restart not attempted after dead service detected
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:163-168`
- **Evidence**: when `set_status()` detects `self.snap.services["snmp-exporter"]["active"] is False`, it sets `MaintenanceStatus()` and returns without calling `snap.start()`. After a manual `systemctl start`, the charm still showed `MaintenanceStatus` until the next `config-changed`.
- **Impact**: the charm detects the dead workload but never fixes it — for a metrics exporter, sitting in `MaintenanceStatus` indefinitely is unacceptable in most deployments.
- **Fix**: in `set_status`, when the service is inactive, attempt `self.snap.start(enable=True)` inside `try/except`, then re-check status.
- **Linter rule**: service health check does not attempt recovery — not mechanically checkable.

### Empty certificate set written to disk when relation forms before certs are available
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:231-236`
- **Evidence**:
  ```python
  def _on_cert_transfer_available(self, event):
      CA_CERT_PATH.parent.mkdir(parents=True, exist_ok=True)
      certs = "\n\n".join(event.certificates)  # empty on relation-created before provider writes data
      CA_CERT_PATH.write_text(certs + "\n")    # writes 1-byte file ("\n")
      self._reconcile_charm_tracing()
  ```
  Observed: `relation-created` fires before the provider has written certs, producing a 1-byte file. Even after the provider writes data, the v1/v0 library bug above may prevent the cert from ever being read.
- **Impact**: writing an empty CA file is misleading. With an HTTPS tracing endpoint, `charm_tracing_config()` would see the file exists and pass an empty CA, causing TLS failures. In the observed test no harm occurred because no `cos-agent` relation existed at the time.
- **Fix**: guard with `if not event.certificates: return` before writing.
- **Linter rule**: writes event data to file without checking data is non-empty — mechanically checkable.

### `_write_snmp_config_file` swallows restart failure and returns success
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:128-130`
- **Evidence**:
  ```python
  except (snap.SnapError, OSError, AttributeError) as e:
      logger.warning(f"Failed to restart SNMP exporter service: {e}")
  return True  # returns True even on restart failure
  ```
- **Impact**: the caller (`on_config_changed`) ignores the return value, so the charm reports `active` while the service still runs the old config, with no way for the operator to know.
- **Fix**: return `False` on restart failure; have `on_config_changed` rely on `set_status()` for the actual health check.
- **Linter rule**: method returns success indicator but always returns `True` on the error path — mechanically checkable.

### `on_install` does not handle snap install failure
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:63-66`
- **Evidence**: `self.snap.ensure(state=snap.SnapState.Latest, channel=SNAP_CHANNEL)` with no `try/except`.
- **Impact**: a `snap.SnapError` (network failure, missing snap, permission denied) propagates uncaught, failing the install hook. Juju retries indefinitely with no actionable message.
- **Fix**: wrap in `try/except`; set `MaintenanceStatus("Installing snap...")` on start and `BlockedStatus` with a message on failure.
- **Linter rule**: hook handler performs side-effect operation without try/except — mechanically checkable for install/upgrade-charm/start/stop handlers.

### `start` handler does not handle snap start failure
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:68-71`
- **Evidence**:
  ```python
  def on_start(self, event: ops.StartEvent):
      self.snap.start(enable=True)
      self.set_status()
  ```
- **Impact**: same pattern as install — an uncaught `snap.SnapError` produces a traceback and error state instead of letting `set_status()` report `MaintenanceStatus`.
- **Fix**: wrap `snap.start()` in `try/except`; on failure fall through to `set_status()`.
- **Linter rule**: same as above.

### `set_status` reads `self.snap.services` directly without error handling
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:165`
- **Evidence**: `if self.snap.services["snmp-exporter"]["active"] is False:` — direct dict access.
- **Impact**: raises `KeyError` if the snap is not installed or the service name changes (e.g. externally removed snap).
- **Fix**: use `.get("snmp-exporter", {}).get("active")` with a safe default, or catch `KeyError` and set `MaintenanceStatus`.
- **Linter rule**: dict access on unvalidated external state without fallback — mechanically checkable.

### `scrape_configs()` has the same uncaught `yaml.YAMLError` path
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:172-178`
- **Evidence**: `scrape_config = yaml.safe_load(config_file)` with no `try/except`, same pattern as `snmp_config`. Not reached in default targets mode since `scrape_config_file` is empty then.
- **Impact**: malformed `scrape_config_file` YAML raises uncaught, taking the unit into `error`.
- **Fix**: same as `snmp_config` — wrap in `try/except`.
- **Linter rule**: `yaml.safe_load` without try/except — mechanically checkable.

### `relation.units.pop()` permanently mutates the relation in cert_transfer library
- **Severity**: medium
- **Kind**: bug (library)
- **Where**: `deps/charmlibs/interfaces/certificate_transfer/_certificate_transfer.py:577-578`
- **Evidence**:
  ```python
  if not certificates and relation.units:
      databag = relation.data.get(relation.units.pop(), {})  # destructive
  ```
  `.pop()` permanently removes a unit from the relation's remote-units set.
- **Impact**: with multiple remote units on the provider side, the v0 fallback only ever reads the first popped unit; subsequent calls never try the others.
- **Fix**: use `next(iter(relation.units))` instead of `.pop()`.
- **Linter rule**: calls `.pop()` on a shared mutable collection without making a copy — mechanically checkable.

### Config-change hook restarts service even when config has not changed
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:81-85` (`on_config_changed`)
- **Evidence**: `on_config_changed` unconditionally calls `_write_snmp_config_file` whenever `self.snmp_config` is truthy, without comparing to the existing file content.
- **Impact**: unnecessary restarts cause brief metric gaps and add latency on every config-change event; Juju already skips no-op hook firing so impact is limited to genuine config changes that don't affect the SNMP config file itself.
- **Fix**: compare `yaml.dump(snmp_config)` to existing file content before writing/restarting; skip if identical.
- **Linter rule**: hook handler calls restart/restart-service without content-diff check — mechanically checkable.

### `cos_agent` relation: redundant charm observer
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:40-48`
- **Evidence**: the charm's `_on_cos_agent_relation_changed`, registered on `cos_agent_relation_joined` and `cos_agent_relation_changed`, only calls `_reconcile_charm_tracing()` — it does not write `metrics_scrape_jobs`. That data is written by `COSAgentProvider._on_refresh()` (`lib/charms/grafana_agent/v0/cos_agent.py:672-693`), which the library itself registers on `relation_joined`, `relation_changed`, and `config_changed`. The charm's `relation_joined` observer is therefore redundant with the library's own handling.
- **Fix**: remove the `relation_joined` observer; keep `relation_changed` for explicit tracing reconciliation if desired (though `config_changed` via `refresh_events` already covers most cases). Replace `# pyright: ignore` comments with explicit type annotations where possible.
- **Linter rule**: charm handler registered on event that library also handles without additional action — not mechanically checkable.

### No `upgrade-charm` handler
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/charm.py`
- **Evidence**: no `self.framework.observe(self.on.upgrade_charm, ...)` registration exists.
- **Impact**: `juju refresh`/`juju upgrade-charm` does not re-run `snap.ensure()`, so a snap update bundled with a charm refresh is not applied until the next config change or reboot.
- **Fix**: add `self.framework.observe(self.on.upgrade_charm, ...)` calling `self.snap.ensure(state=snap.SnapState.Latest, channel=SNAP_CHANNEL)`.
- **Linter rule**: `upgrade-charm` handler missing when snap/package install is in the install handler — mechanically checkable.

### `SNAP_CHANNEL` hardcoded, not configurable
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:26`
- **Evidence**: `SNAP_CHANNEL = "0.24/stable"`. Open issue #15 notes the snap is significantly outdated. No `snap-channel` config option exists.
- **Impact**: operators cannot pin to a newer snap channel without a charm update.
- **Fix**: add a `snap_channel` config option, default `"0.24/stable"`.
- **Linter rule**: not mechanically checkable.

### `ruff format` would reformat test files
- **Severity**: low
- **Kind**: lint
- **Where**: `tests/unit/test_charm.py`, `tests/integration/test_placeholder.py`
- **Evidence**: `ruff format --check src/ tests/` exits 1; 3 files would be reformatted (2 tests + 1 integration placeholder). The `tox.ini` `lint` target and `justfile` `lint` recipe only run `ruff check`, not `ruff format --check`.
- **Fix**: add `ruff format --check` to the lint target.
- **Linter rule**: format check not in lint target — not mechanically checkable.

## Worth copying

- **`set_status` method** (`src/charm.py:136`): clear, correctly ordered status precedence (conflicting config → missing config → service not running) with actionable `BlockedStatus` messages; called at the end of every handler.
- **Two-mode config model**: "simple targets" vs "custom config files" is well-designed and clearly communicated in `BlockedStatus` messages.
- **`_write_snmp_config_file` docstring** (`src/charm.py:103`): explicit `Returns True if successful, False otherwise.` — good practice many charms skip (even though the return value isn't always honest, see Findings).
- **`ops_tracing` integration**: use of `charm_tracing_config()` (from `cos_agent`) and `ops_tracing.set_destination()` for self-instrumentation is the modern canonical pattern.
- **`charm_tracing_config` safe HTTPS handling** (`lib/charms/grafana_agent/v0/cos_agent.py:1410-1417`): if the tracing endpoint is HTTPS but the CA cert file doesn't exist yet, returns `(None, None)` and disables tracing rather than raising TLS errors.
- **Relation-broken cleanup**: `_on_cert_transfer_removed` checks `CA_CERT_PATH.exists()` before deleting, and correctly removes the file when the relation breaks.
- **Test structure** (`tests/unit/test_charm.py`): `ops.testing.State`/`Context` scenario testing with snap library mocks is clean and avoids needing a real snap in CI.

## Common-practice notes

**What this charm does better than average**:
- Uses `ops_tracing` (OTLP HTTP) for self-instrumentation.
- Clean separation between `set_status()` (calculation) and handlers (actions).
- No `StoredState` — all state derived from config and relations.
- `CertificateTransferRequires` used from PyPI (`charmlibs-interfaces-certificate-transfer`), not hand-rolled.

**Where this charm drifts from convention**:
- `src/charm.py` as module name, imported via `from charm import SNMPExporterCharm`, requires `src` in `PYTHONPATH`; more common is `src/<charm_name>/__init__.py`.
- No `src/__init__.py` — relies on `PYTHONPATH` rather than a proper package import.
- Libraries live correctly under `lib/charms/<name>/v<N>/`, but the interface library is a separate PyPI package (`charmlibs-interfaces-certificate-transfer`) rather than a bundled `lib/` module — a documented but potentially confusing split.
- CI (`pull-request.yaml`, `quality-gates.yaml`) delegates to shared `canonical/observability` workflows, appropriate for this charm's ecosystem but keeps local CI configuration opaque.
- `tox.ini` uses `min_version = 4.0.0` and `uv` — standard practice.

## Tests

**Unit tests** (`tests/unit/test_charm.py`): 8 tests, all passing, using `ops.testing.Context` (scenario testing); snap library fully mocked via `conftest.py`.

Run: `PYTHONPATH="$(pwd)/lib:$(pwd)/src" uv run pytest tests/unit/ -v` — all 8 passed in 0.08–0.11s. With `pytest-cov`: 82% coverage, 20/112 statements missed.

```
Name           Stmts   Miss Branch BrPart  Cover   Missing
src/charm.py     112     20     22      2    82%   69, 73-74, 78-79, 112-115, 129-130, 166, 221-222, 233-236, 240-242
```

Coverage gaps: `on_install`, `on_start`, `on_stop` are never exercised; `_write_snmp_config_file` restart-failure path untested; `set_status` `MaintenanceStatus` branch untested; `_reconcile_charm_tracing`, `_on_cert_transfer_available`, `_on_cert_transfer_removed` untested; `scrape_config_file` non-Dict YAML parse failure untested (only `config_file`'s failure path is tested); `_on_cos_agent_relation_changed` behaviour not verified.

Notable behaviour: `test_cos_agent_relation_data_is_set` confirms `metrics_scrape_jobs` land in `local_unit_data` (correct for `cos_agent`). `test_scrape_job_with_config` logs an expected INFO `failed validating relation data` before grafana-agent joins. The job-name prefix `snmp-exporter_0_snmp` matches between the test and the actual deployed unit (`juju show-unit grafana-agent/0`). The `_scrape_jobs` property copies before mutating, so `scrape_configs()`'s original output is not mutated between calls.

**Integration tests** (`tests/integration/test_charm_tracing.py`): tests charm tracing via `cos-agent` with `opentelemetry-collector`, using `pytest-bdd`. `conftest.py` uses a `jubilant` fixture for a temporary model; `pack()` uses `charmcraft pack`. Requires SSH access to units for patching collector config — not runnable in this environment. Also needs a fully provisioned machine for the `grafana-agent` principal charm.

**CI**:
- `pull-request.yaml`: shared `canonical/observability` PR workflow on `main`
- `quality-gates.yaml`: manual dispatch, shared quality-gates workflow
- `tiobe-scan.yaml`: periodic security scan
- `update-libs.yaml`: automated library updates via Renovate

**Static checks**:
- `ruff check`: clean (`src/`, `tests/`, `lib/`)
- `pyright` on `src/` + `tests/unit/` with `--extra=dev`: 0 errors, 0 warnings
- `pyright` on `lib/` (no extras): 3 errors (`Argument to class must be a base class`), suppressed via `pyproject.toml extraPaths`
- `ruff format --check`: would reformat 3 files (2 test files + 1 integration placeholder)

## Docs

- **README.md**: adequate; documents both config modes with examples, including the `@FILENAME` notation for config files.
- **`charmcraft.yaml` description**: good overview, bulleted key features, links to COS documentation.
- **charmhub description**: very short ("Exporter that exposes information gathered from SNMP for use by a Prometheus compatible monitoring system."), lacking detail on the two config modes and the snap dependency.
- **No `CONTRIBUTING.md`**: no guidance for new contributors on dev setup or running tests.
- **No `docs/` directory**: project docs live only on charmhub/discourse.

## Open questions

1. Is `SNAP_CHANNEL` staleness (issue #15) being actively tracked upstream? Has the snap been updated to track newer `prometheus-snmp-exporter` releases?
2. Is the missing `upgrade-charm` handler a deliberate decision (relying on `config-changed` to pick up snap changes) or an oversight?
3. Given the confirmed `CertificateTransferRequires`/`self-signed-certificates` incompatibility, is there a known v1 `receive-ca-cert` provider the charm should document/recommend, or should the charm switch to the v0 library directly?
4. Is grafana-agent's standalone provisioning behavior (0 units until related) documented/expected, or a quirk worth flagging upstream?
5. Is k8s deployment officially unsupported for this charm? If so, should `__init__` fail with a clear `BlockedStatus` rather than an unhandled crash?
6. Is the `cos_agent_relation_joined` observer (`src/charm.py:40-43`) intentionally redundant with the library's own `_on_refresh`, or should it be removed?
