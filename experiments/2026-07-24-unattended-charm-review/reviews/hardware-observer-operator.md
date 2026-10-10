# hardware-observer-operator review

A machine-subordinate charm that monitors bare-metal hardware (BMCs via IPMI/Redfish, RAID
controllers, NVIDIA GPUs, SMART disks) and exposes Prometheus metrics via three exporters
(hardware-exporter, smartctl-exporter, dcgm-exporter). It relates to a principal via
`juju-info` and to a COS consumer via `cos-agent`. Config validation (Pydantic) is solid,
lint is clean, and unit tests pass with 100% coverage, but the charm has **no relation
event handlers at all** — it never reacts to `cos-agent-relation-joined/changed/departed` —
which causes stale blocked status after relation creation and leaves a downstream consumer
(opentelemetry-collector) stuck in an error state. There are also several high-severity
alerting problems (all `for: 0m` in the RAID-collector rule files) and an unhandled
`ValueError` in the DCGM channel-selection path that will error the unit on newer CUDA. A
maintainer should first fix the missing relation handlers and the `for: 0m` alert pattern,
then address the DCGM `ValueError` and the `upgrade_charm` short-circuit.

| | |
|---|---|
| Repo | canonical/hardware-observer-operator @ `3d870611` (2026-07-22) |
| Charms | hardware-observer |
| Substrate | machine (LXD) |
| Deployed | yes — concierge-lxd-4, model rv-ho3, rev 891 → 909 (latest/stable → latest/edge) |
| Reviewed | 2026-09-01 |

## What it does

The charm detects available hardware tools (IPMI sensors/SEL/DCMI, Redfish, Dell PERC, HPE
SSA, LSI SAS-2/3, Broadcom MegaRAID/StorCLI, NVIDIA DCGM, SMART) and installs the matching
exporters: hardware-exporter (systemd Python service, via `prometheus-hardware-exporter` git
package v1.2.1), smartctl-exporter (snap), dcgm-exporter (snap). It provides scrape configs
and alert rules to a `cos-agent` consumer and ships Grafana dashboards. Config options
control ports, log levels, Redfish enable/disable, DCGM snap channel, and IPMI driver type.
The `redetect-hardware` action re-detects hardware and optionally applies the new toolset.
The charm requires a `juju-info` relation from its principal and a `cos-agent` relation from
a COS consumer (grafana-agent, opentelemetry-collector-k8s, etc.).

## Deployment log

**rv-ho2** (first deployment, rev 891 stable):
```
juju add-model rv-ho2 localhost --controller concierge-lxd-4
juju deploy ubuntu --channel=stable
juju deploy hardware-observer --channel=latest/stable  # rev 891
juju deploy opentelemetry-collector --channel=2/stable
juju integrate ubuntu:juju-info hardware-observer:general-info
juju integrate hardware-observer:cos-agent opentelemetry-collector:cos-agent
juju integrate ubuntu:juju-info opentelemetry-collector:juju-info
```
Lifecycle: install → blocked "Missing relation: [cos-agent]" → cos-agent relation created →
recovery via periodic `update_status` timer (~5 min after relation creation) → active "Unit
is ready". LXD has no hardware, so no exporters install — nothing to break.

**rv-ho3** (second deployment, rev 891 → 909 edge):
```
juju add-model rv-ho3 localhost --controller concierge-lxd-4
juju deploy ubuntu --channel=stable
juju deploy grafana-agent --channel=0.44/stable
juju deploy hardware-observer --channel=latest/stable
juju deploy opentelemetry-collector --channel=2/stable
juju integrate ubuntu:juju-info hardware-observer:general-info
juju integrate hardware-observer:cos-agent opentelemetry-collector:cos-agent
juju refresh --channel=latest/edge hardware-observer  # rev 909
```
Lifecycle: hardware-observer/0 (rev 891) → blocked "Missing relation: [cos-agent]"
immediately after install → cos-agent relation created at 01:39:33 →
`cos-agent-relation-joined`/`cos-agent-relation-changed` fire repeatedly between 01:40:52 and
01:43:21 on hardware-observer/0 with **no handlers** (no-ops, confirmed in `juju debug-log`)
→ unit stays blocked → periodic `update_status` fires at 01:43:55 (~4 min after relation
creation) → unit goes active. `juju refresh` to edge rev 909: `upgrade_charm` fires on
hardware-observer/0 at 01:48:51 → maintenance "Installing resources..." → full install
sequence re-runs → active "Unit is ready" by ~01:48:57 (~3-6s). New subordinate units
(hardware-observer/7, /8, /9) appear as a result of the refresh.

For a subordinate created alongside a machine that already had a cos-agent relation
(hardware-observer/1), `num_cos_agent_relations` was already 1 at `__init__` time, so the
unit went active immediately with no stuck period — confirming the bug is specifically
about relations created *after* the unit starts.

**grafana-agent machine charm**: requires `juju-info` or `cos-agent` as a **requirer** — it
cannot stand alone as a cos-agent provider. Observed message: `blocked "Missing incoming
('requires') relation: cos-agent|juju-info"`. hardware-observer therefore cannot integrate
with a standalone grafana-agent machine charm; it can only integrate with charms that
provide cos-agent as a requirer (e.g. opentelemetry-collector).

**opentelemetry-collector cos-agent integration**: hardware-observer subordinate units
created alongside opentelemetry-collector machines go `active "Unit is ready"` immediately,
because the cos-agent relation already existed when the subordinate was created. The
opentelemetry-collector units themselves go `error "hook failed: 'cos-agent-relation-joined'"`
— because hardware-observer's own relation hooks are no-ops and never set any relation data,
leaving the collector's hook waiting on data that never appears.

## Observed behaviour

- **Relation hooks are no-ops.** `cos-agent-relation-joined`/`changed` fire on
  hardware-observer (confirmed in `juju debug-log`) but no handler is registered — `src/charm.py`
  only observes `config_changed`, `install`, `remove`, `update_status`, `upgrade_charm`, and
  `redetect_hardware_action`. hardware-observer/0 stayed `blocked "Missing relation:
  [cos-agent]"` for ~3-4 minutes after the relation was created, until `update_status` fired.
- **`num_cos_agent_relations` is a stale snapshot**, set once in `__init__`
  (`self.num_cos_agent_relations = self.get_num_cos_agent_relations("cos-agent")`) and never
  updated by any handler. `cos_agent_related` reads this cached value.
- **Recovery only via periodic `update_status`**, whose handler calls
  `get_num_cos_agent_relations()` dynamically rather than reading the cache — explaining the
  ~3-5 minute lag before the unit self-corrects.
- **Subordinates created alongside a pre-existing relation are unaffected** — the relation
  count is already correct at `__init__` time, so no stuck period occurs (confirmed for
  hardware-observer/1, /3, /5 alongside opentelemetry-collector machines).
- **`upgrade_charm` re-runs full installation unconditionally.** `_on_install_or_upgrade` sets
  `maintenance "Installing resources..."` and re-installs all exporters/services even though
  `resource_installed` is already True. Observed: after `juju refresh` to edge rev 909,
  hardware-observer/0 briefly went to maintenance for a few seconds before returning to active.
- **No services installed on LXD** — no hardware detected, `stored_tools`/`exporters` empty,
  no systemd services or snaps installed. Alert rules are still pushed to cos-agent via
  `COSAgentProvider._on_refresh` regardless.
- **`hwinfo()` and `get_bmc_address()` apt-install on every call** — `src/hardware.py:76` and
  `:101` call `apt.add_package` unconditionally; `src/hw_tools.py:659` calls
  `apt_helpers.add_pkg_with_candidate_version("freeipmi-tools")` unconditionally. All three
  run on every hardware re-detection (i.e. every hook), even on machines with no relevant
  hardware.
- **`redfish_disable=True` logs a WARNING on every hook** — the Pydantic validator warns on
  every config load (install, config_changed, upgrade_charm), even though `True` is the
  (safe) default.
- **Lint completely clean** (`tox -e lint`): ruff check, ruff format, codespell, mypy all
  pass; `ruff format --check` confirms all 11 source files are formatted.
- **Unit tests: 324 passed, 100% coverage** (`tox -e unit`).
- **promtool: all 55 alert rules valid.**
- **Many subordinate units** — a machine with multiple cos-agent relations creates one
  hardware-observer subordinate per machine per cos-agent peer; rv-ho3 accumulated
  hardware-observer/0 through /9 for one ubuntu machine plus its opentelemetry-collector peers.

## Findings

### No relation event handlers — stale BlockedStatus for minutes after cos-agent relation is created
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:51-56` (registered handlers), `src/charm.py:69`
  (`num_cos_agent_relations` assignment), `src/charm.py:340` (`cos_agent_related` property)
- **Evidence**:
```python
# Only handlers registered — no relation-joined/departed/broken:
self.framework.observe(self.on.config_changed, self._on_config_changed)
self.framework.observe(self.on.install, self._on_install_or_upgrade)
self.framework.observe(self.on.remove, self._on_remove)
self.framework.observe(self.on.update_status, self._on_update_status)
self.framework.observe(self.on.upgrade_charm, self._on_install_or_upgrade)
self.framework.observe(self.on.redetect_hardware_action, self._on_redetect_hardware)

# set once at __init__, never updated:
self.num_cos_agent_relations = self.get_num_cos_agent_relations("cos-agent")

# reads the stale snapshot:
@property
def cos_agent_related(self) -> bool:
    return self.num_cos_agent_relations != 0
```
  `cos-agent-relation-joined`/`changed` fire on the unit (confirmed via `juju debug-log`) but
  run as no-ops since no handler is registered. Observed: hardware-observer/0 stayed blocked
  "Missing relation: [cos-agent]" for ~3-4 minutes after the relation was created, recovering
  only when the periodic `update_status` timer fired.
- **Impact**: Operators see a misleading BlockedStatus for up to several minutes after `juju
  integrate`. The charm also cannot detect relation removal (the opposite direction is
  equally unhandled), and downstream consumers (e.g. opentelemetry-collector) can be left
  waiting on relation data that hardware-observer never sets, going into their own error state.
- **Fix**: Register handlers for `on.cos_agent_relation_joined`, `_changed`, and `_departed`
  that update `num_cos_agent_relations` (or call `_on_update_status` directly). Alternatively,
  make `cos_agent_related` call `get_num_cos_agent_relations()` dynamically instead of reading
  the cached value.
- **Linter rule**: charm must register handlers for all relation-joined/changed/departed
  events on relations it defines — mechanically checkable by diffing `framework.observe`
  calls against `metadata.yaml` relations.

### `_set_prometheus_alert_rules` only runs at `__init__`, never on later hardware changes
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:61` (only call site), `src/charm.py:343-350` (definition)
- **Evidence**:
```python
# __init__ line 61 — the only call site
self._set_prometheus_alert_rules()

def _set_prometheus_alert_rules(self) -> None:
    if HWTool.REDFISH in self.stored_tools and self.typed_config.redfish_disable is False:
        logger.info("Enabling Redfish alert rules.")
        shutil.copy(PROM_RULES_REDFISH, PROM_RULES)  # mutates shipped dir
    else:
        logger.info("Disabling Redfish alert rules.")
        PROM_RULES_REDFISH.unlink(missing_ok=True)  # removes source file!
```
  Not called from `config_changed`, `upgrade_charm`, or after `redetect-hardware`. If a BMC
  appears after the unit has started, Redfish alert rules are not copied in until the unit
  restarts and `__init__` re-runs. When Redfish is disabled, the source file
  `prometheus_alert_rules_dynamic/redfish.yaml` is permanently deleted, so a future restart
  depends on it being restored from the charm payload.
- **Impact**: Redfish alert rules go stale on hardware change; file mutation is
  non-idempotent; deleting the source file makes future restarts fragile.
- **Fix**: Call `_set_prometheus_alert_rules` from `config_changed` and `upgrade_charm` too.
  Move the mutable copy to `$CHARM_DIR/.local/` rather than mutating shipped `src/` files, and
  stop `unlink`ing the source.
- **Linter rule**: hook handler must not mutate files under `$CHARM_DIR/src/` except under
  `$CHARM_DIR/.local/` — mechanically checkable by flagging `shutil.copy`/`write_text`/`open(...,
  'w')` against paths under `src/` excluding `src/.local/`.

### DCGM `_automatic_channel_selection` raises unhandled `ValueError` for CUDA >= 14
- **Severity**: high
- **Kind**: bug
- **Where**: `src/service.py:465` (`_automatic_channel_selection`), `src/service.py:503` (call site)
- **Evidence**:
```python
def _automatic_channel_selection(self, cuda_version: int) -> str:
    if cuda_version >= 11 and cuda_version <= 13:
        return f"v4-cuda{cuda_version}/stable"
    elif cuda_version < 11:
        return "v3/stable"
    else:
        raise ValueError(
            f"No compatible DCGM snap channel found for CUDA version {cuda_version}."
        )
```
  When CUDA >= 14, `ValueError` propagates unhandled; the only exception caught anywhere in
  the install path is `ExporterError`. A test (`test_automatic_channel_selection_unsupported_cuda`)
  only asserts the raise, not graceful handling.
- **Impact**: Any principal that upgrades NVIDIA drivers past CUDA 13 (e.g. driver 580+)
  puts the unit into ErrorStatus on install. Related issue #525 tracks a DCGM helm conflict
  on k8s.
- **Fix**: Catch `ValueError` in `_automatic_channel_selection` and fall back to `"v4/stable"`,
  or wrap it as `ExporterError` so the charm's existing error handling applies.
- **Linter rule**: not mechanically checkable without semantic understanding.

### All `for: 0m` alerts across the RAID/BMC collector rule files — systemic false-positive pattern
- **Severity**: high
- **Kind**: bug
- **Where**: `lsi_sas.yaml`, `mega_raid.yaml`, `perccli.yaml`, `ssacli.yaml`, `ipmi_sel.yaml`
- **Evidence**: `for: 0m` (fires on the first Prometheus evaluation cycle, no settling time)
  appears across all five collector alert files:
  - `lsi_sas.yaml` (5/5): `SasircuCommandFailed`, `LSISASControllerNotFound`,
    `LSISASIRVolumeNotFound`, `LSISASIRVolumeUnready`, `LSISASPhysicalDiskUnready` — all `for: 0m`
  - `mega_raid.yaml` (3/4): `StorcliCommandFailed`, `MegaRAIDControllerNotFound`,
    `MegaRAIDVirtualDriveNotOptimal` — `for: 0m`; only `MegaRaidPhysicalDriveCritical` has `for: 5m`
  - `perccli.yaml` (4/5): `PerccliCommandFailed`, `PowerEdgeRAIDControllerNotFound`,
    `PowerEdgeRAIDControllerSuccess`, `PowerEdgeRAIDVirtualDriveNotOptimal` — `for: 0m`; only
    `PowerEdgeRAIDPhysicalDriveCritical` has `for: 5m`
  - `ssacli.yaml` (5/5): all `for: 0m`
  - `ipmi_sel.yaml` (2/5): `IPMISELStateWarning`, `IPMISELStateCritical` — no `for:` (equivalent to 0m)
  Issues #539 (SAS false positives) and #534 (`IPMISELStateCritical` fires on every reboot)
  corroborate real-world impact; issue #522 reports `PowerEdgeRAIDControllerNotFound` firing
  immediately on a Dell PowerEdge R770.
- **Impact**: any transient scrape failure or controller-not-found blip triggers an immediate
  alert, with no settling window.
- **Fix**: Add `for: 2m` to command-failure/controller-not-found alerts and `for: 5m` to
  state-based alerts; add `keep_firing_for: 30m` to immediately-firing critical alerts.
- **Linter rule**: alert rules in `prometheus_alert_rules/` must have `for:` >= 2m for
  controller-found/command-failure alerts and >= 5m for state-based alerts — mechanically checkable.

### `upgrade_charm` re-runs full installation with visible maintenance status — no short-circuit
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:140-181` (`_on_install_or_upgrade`)
- **Evidence**: the `upgrade_charm` hook fires `_on_install_or_upgrade` (`src/charm.py:55`),
  which unconditionally sets `MaintenanceStatus("Installing resources...")` and re-runs
  `hw_tool_helper.install(...)` plus exporter install/restart, regardless of whether
  `resource_installed` is already True. Observed: after `juju refresh` to edge rev 909,
  hardware-observer/0 briefly went to maintenance for a few seconds before returning to active.
- **Impact**: every charm refresh causes a visible maintenance blip and unnecessary
  re-installation of packages/snaps and service restarts.
- **Fix**: Check `resource_installed` at the top of `_on_install_or_upgrade`; skip the
  install step if already True and no relevant config/version has changed.
- **Linter rule**: not established.

### `bmc_hw_verifier`, `get_bmc_address`, and `hwinfo` run `apt install` on every call
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/hw_tools.py:659` (`bmc_hw_verifier`), `src/hardware.py:76`
  (`get_bmc_address`), `src/hardware.py:101` (`hwinfo`)
- **Evidence**:
```python
apt.add_package("ipmitool", update_cache=False)             # get_bmc_address, every call
apt_helpers.add_pkg_with_candidate_version("freeipmi-tools")  # bmc_hw_verifier, every call
apt.add_package("hwinfo", update_cache=False)                # hwinfo, every call
```
  All three run unconditionally on every hardware re-detection (every hook), even on machines
  with no IPMI or RAID hardware.
- **Impact**: unnecessary apt overhead on every hook.
- **Fix**: Guard each call with a `check_deb_pkg_installed(pkg)` check before invoking
  `apt.add_package`.
- **Linter rule**: hook handler must not call `apt.add_package` without an installed-check
  guard — mechanically checkable.

### `CollectorFailed` and all immediately-firing alerts lack `keep_firing_for`, causing flapping
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/prometheus_alert_rules/general.yaml` and all files with `for: 0m` alerts
- **Evidence**: `CollectorFailed` has `for: 30m` but no `keep_firing_for`; issue #476 documents
  BMC flakiness causing this alert to flap. None of the 55 alert rules has a
  `keep_firing_for` clause.
- **Impact**: alerts flap on transient BMC unavailability.
- **Fix**: Add `keep_firing_for: 1h` to `CollectorFailed` and to all `for: 0m` critical alerts.
- **Linter rule**: alert rules with `for:` > 10m should have `keep_firing_for` — mechanically checkable.

### SSACLIStrategy uses EOL Debian stretch repo
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/hw_tools.py:454`
- **Evidence**: `repo_line = "deb https://downloads.linux.hpe.com/SDR/repo/mcp stretch/current non-free"`
  — Debian stretch is end-of-life. Tracked as open issue #297.
- **Impact**: package installs may break as HPE's stretch mirror ages out.
- **Fix**: Switch to an Ubuntu-specific HPE repo line.
- **Linter rule**: not established.

### `stored_tools` property mutates `StoredState` on every read
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:99-107`
- **Evidence**:
```python
@property
def stored_tools(self) -> Set[HWTool]:
    if not self._stored.stored_tools:
        self._stored.stored_tools = {tool.value for tool in detect_available_tools(...)}
    self._stored.stored_tools.discard("smartctl")  # mutates on every read
    return {HWTool(value) for value in self._stored.stored_tools}
```
  Every access calls `.discard("smartctl")`, writing to StoredState. Idempotent but wasteful.
- **Impact**: unnecessary StoredState I/O on every hook that reads `stored_tools`.
- **Fix**: Perform the discard once, at write time, rather than on every read.
- **Linter rule**: property with a side-effecting StoredState mutation should be flagged —
  mechanically checkable.

### Config changes deferred during install are silently dropped
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:225-230`
- **Evidence**:
```python
def _on_config_changed(self, event: EventBase) -> None:
    if not self._stored.resource_installed:
        event.defer()
        return
```
  If `config_changed` fires before install completes, it's deferred, but nothing
  re-schedules it once install finishes — it's only re-applied if the user makes another
  config change.
- **Impact**: a config change made during install can be silently lost.
- **Fix**: Store the pending config in StoredState during deferral and apply it once install
  completes.
- **Linter rule**: not established.

### `get_bmc_address` returns `None`, which renders literally as the string "none" in exporter config
- **Severity**: low
- **Kind**: ux
- **Where**: `src/hardware.py:58-62` and the exporter config template
- **Evidence**: when the BMC is unavailable, `get_bmc_address()` returns `None`; the
  hardware-exporter config template renders this and the exporter then attempts
  `https://none:443/...`, logging `ERROR "Failed to resolve 'none'"`.
- **Impact**: confusing error message on any machine without a BMC.
- **Fix**: Handle `None` explicitly in the template/config renderer rather than relying on
  its string coercion.
- **Linter rule**: not established.

## Worth copying

- **Pydantic config with cross-field validation** (`src/literals.py`): the `HWObserverConfig`
  model's `check_ipmi_redfish_compatibility` root validator prevents conflicting config
  combinations, with clear error messages, confirmed working by failure injection.
- **`ExporterError` as charm-level signalling** (`src/service.py`): raised from `install()`,
  propagates cleanly to `_on_install_or_upgrade`, which sets `resource_installed = False` and
  re-raises into ErrorStatus.
- **Strategy pattern for hardware tools** (`src/hw_tools.py`): `StrategyABC`,
  `TPRStrategyABC`, `APTStrategyABC`, `SnapStrategy` hierarchy is clean and extensible.
- **Resource checksum validation** (`src/checksum.py`): each resource version has an explicit
  SHA256 checksum, architecture, and Ubuntu series compatibility list.
- **SSDLC event logging** (`src/ssdlc.py`): consistent structured, machine-parseable JSON logging.
- **Config-driven exporter factory** (`src/charm.py`): the `exporters` property cleanly
  builds the right exporter set from detected tools.
- **Retry loop in restart** (`src/service.py:240-254`): configurable retry count/timeout
  before declaring restart failure.
- **`check_deb_pkg_installed` utility** (`src/hw_tools.py`): reusable pre-install check — not
  consistently used elsewhere (see the apt-on-every-call finding above).

## Common-practice notes

- StoredState for persistence is the standard machine-charm pattern, with the mutation-on-read
  caveat noted above.
- Subordinate with `scope: container` on `juju-info` works correctly with machine principals.
- `cos-agent` has `limit: 1` in metadata.
- Uses `COSAgentProvider` from `charms.grafana_agent.v0` (v0 library). `refresh_events=[config_changed,
  upgrade_charm]` correctly triggers `_on_refresh`. `v1` of the library is available; a
  migration path should be evaluated.
- Mixed `operator_libs_linux` versions: `v0` for apt, `v1` for systemd, `v2` for snap
  (`src/hw_tools.py:22-24`) — non-ideal but no functional issue observed.
- Uses the legacy `snap.add(self.snap_name, channel=self.channel)` API rather than the
  modern `snap.Snap.ensure(...)` pattern from `operator_libs_linux` v2.
- Mixed systemd/snap exporters (hardware-exporter under systemd; smartctl/dcgm as snaps) —
  contributes to the DCGM snap conflict in issue #525.
- Module-level `shutil.copy` mutating shipped files at runtime is an unusual pattern (see
  `_set_prometheus_alert_rules` finding above).
- `charmcraft.yaml` uses the `uv` plugin with `parts.charm.source = "."` — flat `src` layout,
  not nested.
- Multi-arch: amd64, arm64, s390x, ppc64el across Ubuntu 20.04, 22.04, 24.04.
- Lint is completely clean: ruff, ruff format, codespell, mypy all pass with zero issues.

## Tests

**Unit tests** (`tests/unit/`): 324 pass, 0 fail, 100% line coverage (`tox -e unit`).

**Coverage gaps**:
- No test for the post-init relation-add scenario: `test_charm.py:302` adds the cos-agent
  relation *before* `harness.begin()`, so `num_cos_agent_relations` is correct at init and
  the stale-status bug is never exercised.
- No test that `_set_prometheus_alert_rules` should also run on `config_changed` or after
  `redetect-hardware`.
- No test for graceful DCGM auto-channel handling at CUDA >= 14 (existing test only asserts
  the `ValueError` is raised).
- No test for `stored_tools` mutation-on-read.
- No test for `hwinfo()`/`get_bmc_address` calling `apt.add_package` on every invocation.
- No test for the SSACLIStrategy Debian stretch repo issue (#297).
- No test for PercCLIStrategy with newer Dell controllers (#522).
- No test for the `upgrade_charm` path re-running full installation unnecessarily.
- No test for `cos_agent_related` returning a stale value after a relation change.

**Functional tests** (`tests/functional/`): Juju bundle with cos-lite + hardware-observer;
covers exporter health, config file permissions, config changes, metrics availability, snap
installation, collector-specific metrics, resource attachment/cleanup. Uses `pytest-operator`.
Marked `@realhw` — requires real hardware, could not be run in this environment.

**Integration tests** (`tests/integration/test_cos_integration.py`): cross-controller
hardware-observer + opentelemetry-collector on LXD → COS Lite on k8s, verifying alert rules
fire. Requires cross-controller setup not available here.

**CI lint** (`tox -e lint`): clean. `ruff format --check` confirms all 11 `src/` files formatted.

**promtool**: all 55 alert rules across 11 files (10 static, 1 dynamic redfish) pass `promtool check rules`.

## Docs

- **README.md**: clean overview of the three exporters and hardware types. Missing:
  explanation of what "Unit is ready" means when no hardware is detected, and the requirement
  for both `juju-info` and `cos-agent` relations.
- **DEVELOPMENT.md** / **dev-environment.md**: thorough setup instructions, including
  `charmcraft.yaml` explanation and `uv` setup.
- **tests/functional/README.md**: explains the `@realhw` marker and test setup.
- **Charmhub description**: "Subordinate charm for monitoring hardware resources." — not
  informative; should describe the exporters and COS integration.
- **Resource descriptions** in `metadata.yaml`: excellent — detailed download URLs and
  instructions per resource.

## Open questions

- Issue #522: Dell PowerEdge R770 needs perccli2 support — no code exists yet.
- Issue #525: DCGM helm conflict (helm-installed dcgm-exporter vs. snap's `hostNetwork`) —
  unresolved.
- Issue #527: Ubuntu 26.04 LTS not yet in the supported platforms list.
- Issues #476 and #534/#539: flapping/false-positive alerts (`keep_firing_for` missing,
  `IPMISELStateCritical` firing on every reboot, LSI SAS false positives) — all open.
- What should happen for DCGM channel selection when NVIDIA driver >= 580 (CUDA >= 14) is
  installed? Currently raises an unhandled `ValueError`.
- Should the charm migrate from `grafana_agent` v0 to v1?
- Is the `redfish_disable=True` WARNING on every hook intentional, given it's the safe default?
- If a BMC appears after the unit has started, `_set_prometheus_alert_rules` never re-runs,
  so Redfish alert rules won't be pushed until the unit restarts.
</content>
