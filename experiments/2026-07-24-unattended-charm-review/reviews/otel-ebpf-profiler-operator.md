# otel-ebpf-profiler-operator

A machine charm that installs the `otel-ebpf-profiler` classic snap (OpenTelemetry eBPF Profiler v0.135.0) on bare-metal or VM units, forwards CPU profiles to a Pyroscope backend or OTel Collector via the `profiling` relation, and exposes self-monitoring via `cos-agent`. It was deployed live against Juju 3.6.27 and Juju 4.0.12 for this review. The core relations (`cos-agent` provides, `profiling` requires) work correctly in practice. The charm is not production-ready as shipped: TLS via `receive-ca-cert` is completely non-functional due to a v1/v0 library mismatch, and the machine-exclusivity lock does not do what its own comment says it does — it fails to block a second unit of the same application from co-residing on the same machine. A maintainer should fix the TLS library mismatch and the lock fingerprint first; both are one-line-scope fixes with outsized correctness impact.

| | |
|---|---|
| Repo | canonical/otel-ebpf-profiler-operator @ `d04fadd` (2026-07-10) |
| Charms | otel-ebpf-profiler |
| Substrate | machine |
| Deployed | yes — two models: `rv-otel-ebpf` on `concierge-lxd-4` (Juju 4.0.12); `rv-otel-ebpf-juju3` on `concierge-lxd` (Juju 3.6.27); channel 2/edge, rev 19 |
| Reviewed | 2026-08-22 |

## What it does

Installs the `otel-ebpf-profiler` classic snap (pinned rev 6 amd64 / rev 5 arm64, both v0.135.0), starts it, holds it against auto-refresh, and writes a per-machine YAML config to `/etc/otel-ebpf-profiler/config.yaml`. Exposes Prometheus metrics on port 9999 and injects Juju topology labels (`juju_model`, `juju_application`, etc.) into emitted profiles. Relations:

- **profiling** (requires): receives OTLP-gRPC endpoint(s) from a `receive-profiles` provider; writes `otlp/profiling/<N>` exporters into the collector config.
- **receive-ca-cert** (requires): receives CA certificates via `certificate_transfer`; writes to `/etc/otel-ebpf-profiler/receive-ca-cert.crt`; sets `insecure=false` in exporter TLS config.
- **cos-agent** (provides): advertises the metrics endpoint (`localhost:9999/metrics`) and log alert rules to a Grafana Agent / OTel Collector subordinate.

No charm config options are defined; all configuration is through relations. Only one unit per machine is intended to be allowed, enforced by a file-based machine lock (`src/machine_lock.py`).

## Deployment log

### Juju 4.x (`concierge-lxd-4`, model `rv-otel-ebpf`)

```
juju add-model rv-otel-ebpf --controller concierge-lxd-4
juju set-model-constraints virt-type=virtual-machine
juju deploy otel-ebpf-profiler --channel 2/edge
```

- Machine provisioning: ~3 min (container creation → agent install → charm start)
- Snap install hook: 04:06:11–04:07:20 UTC (69 s)
- Post-install hooks: leader-elected + config-changed + start (~5 s total)
- Snap held (`snap.hold`) to prevent auto-refresh
- Machine lock acquired at `/etc/otel-ebpf-profiler/machine.lock`

Related `self-signed-certificates` (rev 633, `latest/edge`) on machine 1: provisioned successfully, relation created to `receive-ca-cert`.

`juju add-unit otel-ebpf-profiler --to 0`: unit 2 became `active` on machine 0 alongside unit 0 — machine lock did **not** block it.

`juju add-unit otel-ebpf-profiler` (new machine): unit 1 became `active` on machine 2.

`juju remove-application otel-ebpf-profiler --force`: machines 0 and 2 were destroyed by LXD cleanup; machine 1 (self-signed-certificates) remained. Post-teardown state on machines 0/2 could not be inspected.

### Juju 3.6 (`concierge-lxd`, model `rv-otel-ebpf-juju3`)

```
juju add-model rv-otel-ebpf-juju3 --controller concierge-lxd
juju set-model-constraints virt-type=virtual-machine
juju deploy otel-ebpf-profiler --channel 2/edge
```

- Machine provisioning: ~5 min (`juju-b2b112-0`, ubuntu@24.04, virt-type=virtual-machine)
- Unit became active ~4 min after deploy
- Related `self-signed-certificates` on machine 1 (`juju-b2b112-1`, ubuntu@22.04)
- TLS bug confirmed identical to Juju 4.x

## Observed behaviour

**cos-agent provides — confirmed working.** After relating `otel-ebpf-profiler:cos-agent` to `opentelemetry-collector:cos-agent` (subordinate on the same machine), `juju show-unit otel-ebpf-profiler/0` showed the correct scrape config:
```json
{"config": "...\"metrics_scrape_jobs\": [{\"metrics_path\": \"/metrics\", \"static_configs\": [{\"targets\": [\"localhost:9999\"]}]}]...", ...}
```
The subordinate deployed automatically on machine 0 and became `active`. Alert rules (HostDown, HostMetricsMissing), log alert rules (HighPercentageError), and `tracing_protocols: ["otlp_http"]` were correctly advertised. `otel-ebpf-profiler` stayed `active` throughout with no hook errors.

**profiling requires — confirmed working** (with `opentelemetry-collector` as provider). After integrating `otel-ebpf-profiler:profiling` with `opentelemetry-collector:receive-profiles`, the collector advertised:
```json
{"otlp_grpc_endpoint_url": "juju-b2b112-0.lxd:4317", "insecure": "true"}
```
The charm wrote the exporter config (`otlp/profiling/0` → `juju-b2b112-0.lxd:4317`), reloaded the snap, and status moved from "profiling machine 0, no profiling ingester/backend connected" to "profiling machine 0". Hook sequence: `profiling-relation-created` (05:13:23, triggers reload via `_reconcile_config`) → `-changed` (05:13:27) → `-joined` (05:13:28) → `-changed` (05:13:29). The `opentelemetry-collector` subordinate itself went into `error` (`hook failed: receive-profiles-relation-joined`) because it lacked a `send-profiles` backend — expected in this minimal setup and did not affect `otel-ebpf-profiler`, which stayed `active`.

**Install/hook timing:** snap install ~69 s; start and subsequent hooks <2 s each. Fresh-deploy sequence on both Juju versions: install → leader-elected → config-changed → start (`leader-elected` is a reconcilable event on machines, so `_reconcile()` fires there too).

**Agent restart differs by Juju version:** on Juju 4.x the unit agent restarts between some hooks, re-initializing the charm instance and resetting `_should_reload_snap` to `False`. On Juju 3.6 the agent does not restart between hooks; one process handles all hooks. This is the root of the `_should_reload_snap` bug below.

**SIGHUP behaviour, Juju 4.x:** exactly 3 SIGHUPs observed — install/start, profiling relation joined (exporter added), profiling relation broken (exporter removed) — all correct.

**SIGHUP behaviour, Juju 3.6:** after the receive-ca-cert relation hooks (`-created`, `-joined`, `-changed`), no SIGHUP was observed, because the flag was never set to `True` (no certs received due to the TLS bug; no config change). The latent flag-never-reset bug is confirmed in code but did not manifest in this scenario.

**TLS/certificate integration — broken (confirmed on both Juju 3.6 and 4.x).** Despite a successful relation to `self-signed-certificates`, `/etc/otel-ebpf-profiler/receive-ca-cert.crt` is never created. Every unit shows on every `receive-ca-cert` hook:
```
ERROR receive-ca-cert:5: invalid databag contents: expecting json. {'ca': '-----BEGIN CERTIFICATE-----\n...', 'chain': '[]', ...}
ERROR ... 'Make sure not to interact with the databags except using the public methods in the provider library and use version V1.'
```

**Status staleness:** `sudo systemctl stop snap.otel-ebpf-profiler.otel-ebpf-profiler.service` while the snap is running leaves status `active` until a hook re-evaluates it. After triggering a hook (removing the receive-ca-cert relation), status correctly moved to `blocked` with message `"The otel-ebpf-profiler snap is not running. Check sudo snap logs otel-ebpf-profiler for errors."`. After restarting the snap and re-adding the relation, status correctly returned to `active`.

**update-status:** fires every 5 min, runs `_reconcile()` in <1 s.

**Remove-application destroys machines:** `juju remove-application otel-ebpf-profiler --force` destroyed the LXD VMs for machines 0 and 2; machine 1 (self-signed-certificates) remained. Post-teardown snap/lock state on 0/2 could not be inspected — expected Juju behaviour for managed containers.

**No config options:** `charmcraft.yaml` defines no `options:`; `juju config` has no effect.

**No actions:** `juju actions otel-ebpf-profiler` returns "No actions defined."

**Refresh:** `juju refresh` reports "charm already up-to-date" on both models — no newer revision than rev 19 on 2/edge.

**Multiple units, same machine — both active.** After `juju add-unit otel-ebpf-profiler --to 0`, unit 0 and unit 2 were both `active` on machine 0, both running the snap. The machine lock did not block the second unit.

**Upgrade path (code review):** `UpgradeCharmEvent` triggers `_setup()` → `install_snap()` → `snap.ensure(state=SnapState.Present, ...)`, correctly reinstalling the pinned revision. The lock fingerprint is stable across revisions, so the lock is preserved (not released) on upgrade. Config is rewritten on the `config-changed` hook that follows `upgrade-charm`.

## Findings

### TLS/certificate integration permanently broken — v1 library cannot parse provider's v0 data
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:97-100` (`_reconcile_certs`) + `lib/charms/certificate_transfer_interface/v1/certificate_transfer.py:478-494`
- **Evidence**: On every `receive-ca-cert` hook, on all units on both Juju 3.6 and 4.x:
  ```
  ERROR receive-ca-cert:5: invalid databag contents: expecting json. {'ca': '-----BEGIN CERTIFICATE-----\n...', 'chain': '[]', ...}
  ```
  `CertificateTransferRequires._get_relation_data()` checks `relation.data[relation.app]["version"] == "1"`, finds `"1"`, and tries to parse the app databag with `ProviderApplicationData` (expects `certificates: Set[str]`). But `self-signed-certificates` sends `ca`/`chain` (v0 format) to the **unit** databag, not the app databag — the v0 fallback branch is unreachable because the version check passes. `DataValidationError` is caught and an empty `set()` returned silently.
- **Impact**: TLS is completely non-functional. The CA cert file is never written, so the exporter TLS config can never populate `ca_file`. Operators integrating with `self-signed-certificates` get no TLS.
- **Fix**: Vendor and use `certificate_transfer_interface/v0` (compatible with the provider's actual data format), or patch v1 to fall back to v0 parsing when v1 parsing raises `DataValidationError`.
- **Linter rule**: not mechanically checkable without integration testing against the real provider.

### Machine lock fingerprint excludes unit name — same-app multi-unit co-residence is not blocked
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:41` + `src/machine_lock.py:22`
- **Evidence**: `MachineLock` fingerprints on `JujuTopology.from_charm(self).identifier`, which is `{model}_{model_uuid_short}_{app}` — `deps/cosl/juju_topology.py:236` explicitly excludes `unit` and `charm_name` from the identifier. Confirmed live: after `juju add-unit otel-ebpf-profiler --to 0`:
  ```
  Unit                         Workload  Machine  Message
  otel-ebpf-profiler/0*        active    0        profiling machine 0
  otel-ebpf-profiler/2         active    0        profiling machine 0
  ```
  Both units share the same lock file/fingerprint on machine 0 and both run the snap.
- **Impact**: The lock's stated purpose (`machine_lock.py` comment: prevent multiple instances on the same machine) is defeated for the same-application, multi-unit case. `test_colocated_profilers.py` only tests two *different* applications on one machine, which correctly blocks — it does not catch this bug. Two co-resident eBPF tracer snaps would compete for the same kernel resources.
- **Fix**: Include the unit name in the fingerprint, e.g. `JujuTopology.from_charm(self).identifier + "_" + self.unit.name` — wait, per-unit fingerprints would defeat the lock's purpose entirely; the fix must instead key the lock on machine identity and check for *any other unit* holding it (compare currently-held fingerprint against the requesting unit's own name, blocking any mismatch). At minimum, the lock content should store the acquiring unit name so a second unit's `add-unit` to the same machine can be detected and blocked.
- **Linter rule**: not mechanically checkable.

### `reload()` silently swallows SIGHUP failures
- **Severity**: high
- **Kind**: bug
- **Where**: `src/snap_management.py:175-181`
- **Evidence**: `subprocess.run(shlex.split(cmd))` has no `check=True`. `CalledProcessError` is only raised if the command itself fails to execute; a non-zero exit from `systemctl kill -s SIGHUP` (service not running, permission denied, snap not yet started) is logged and swallowed, and the charm proceeds as if the reload succeeded.
- **Impact**: Operator sees `active` while the collector may still be running stale config.
- **Fix**: `subprocess.run(..., check=True)`, catching `CalledProcessError` and re-raising as `ConfigReloadError`.
- **Linter rule**: `ruff S603` ("subprocess.run without check=True for state-modifying commands") — mechanically checkable.

### Terraform module channel validation blocks the charm's own published channels
- **Severity**: high
- **Kind**: bug
- **Where**: `terraform/variables.tf:8-11`
- **Evidence**:
  ```terraform
  validation {
    condition     = startswith(var.channel, "dev/")
    error_message = "The track of the channel must be 'dev/'. e.g. 'dev/edge'."
  }
  ```
  CI passes `--channel=2/edge`; the terraform test job is commented out in `pull-request.yaml` ("terraform test ... always failing").
- **Impact**: Terraform users cannot use the module with the `2/edge`/`2/stable` tracks the charm actually publishes to. The module is effectively unusable as shipped.
- **Fix**: `startswith(var.channel, "2/") || startswith(var.channel, "dev/") || startswith(var.channel, "latest/")`, or a regex.
- **Linter rule**: not mechanically checkable.

### `snap_management` mocked at module level in unit tests — real reload/config-write code never runs, and the reload assertion is a no-op
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/charm/conftest.py:31` (`patch("charm.snap_management", MagicMock())`) and `tests/unit/charm/test_lifecycle.py:143`
- **Evidence**: All 47 charm unit tests use this fixture, so `reload()`, `_write_config()`, `check_status()`, `install_snap()` and the retry-start branch are all `MagicMock` objects, never the real code. Coverage confirms `src/snap_management.py` lines 175-181 (`reload()` body) and 150-156 (`_write_config()`) are entirely uncovered. `test_lifecycle.py:143` additionally asserts `snap_mocks.snap_mgmt.reload.called_with_args(...)` — `MagicMock.called_with_args(...)` returns another `MagicMock`, so calling it always "succeeds" without checking anything; the test passes regardless of what `reload` was actually called with.
- **Impact**: The silent-SIGHUP-failure bug above would be caught by a real `subprocess.run` test but currently cannot regress-test against it. Non-atomic writes and retry-start logic are similarly untested.
- **Fix**: Add `test_reload_success` / `test_reload_failure` in `tests/unit/test_snap_mgmt.py` mocking `subprocess.run` directly (not the whole module). Fix `test_config_reload` to `snap_mocks.snap_mgmt.reload.assert_called_once_with(OtelEbpfProfilerCharm._snap_name, OtelEbpfProfilerCharm._service_name)`. Make the `conftest.py` fixture more surgical (mock `snap.SnapCache()`/`snap.Snap`, not the whole module).
- **Linter rule**: not mechanically checkable.

### Pydantic `__fields__` deprecation in vendored and dependency code
- **Severity**: medium
- **Kind**: lint/maintenance
- **Where**: `lib/charms/grafana_agent/v0/cos_agent.py:427` and `deps/cosl/interfaces/utils.py:55`
- **Evidence**: Both use `cls.__fields__` instead of `cls.model_fields`. The `cos_agent.py` usage is in a pydantic-v1 code path not taken under the installed Pydantic 2.13.4, but `cosl/interfaces/utils.py:55` is on the live path and fires 6 `PydanticDeprecatedSince20` warnings during the unit test run (triggered by `CosAgentRequirerUnitData.load()` in `test_charm_tracing_configured`). The installed `cosl` package under `~/.local/lib/python3.12/site-packages/cosl/` has the identical issue.
- **Impact**: When Pydantic v3 removes `__fields__`, both the vendored `cos_agent.py` and the `cosl` dependency will fail at runtime, breaking `cos-agent` and other cosl-based integrations.
- **Fix**: Replace `__fields__` with `model_fields` in both locations; bump the `cosl` dependency once upstream fixes it.
- **Linter rule**: `ruff check --select=Pydantic lib/ deps/` — mechanically checkable.

### `_should_reload_snap` flag never reset — latent SIGHUP-spam bug, hard to trigger in normal operation
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:47, 95, 108, 133`
- **Evidence**: Initialized `False`, set `True` in `_reconcile_certs` and `_reconcile_config`, never reset to `False`. In practice the flag is set and consumed within the same `_reconcile()` call: once the reload runs, `update_config()`'s hash check returns `False` on subsequent reconciles, so `_reload_snap()` is not re-triggered. On Juju 4.x, agent restarts between hooks additionally reset the charm instance (and the flag) outright. On Juju 3.6, where the agent persists across hooks, the flag is confirmed to persist in code, but in the observed test scenario it was never set `True` during the relevant hooks, so no spurious SIGHUP occurred. The bug could still manifest if `_reload_snap()` throws before completing, or if rapid successive relation changes overlap the flag's set/consume window.
- **Impact**: Under the right timing, spurious SIGHUP reloads waste CPU and briefly disrupt profiling; on `update-status` (every 5 min) a stuck flag would reload every cycle.
- **Fix**: Explicitly reset `self._should_reload_snap = False` at the end of `_reload_snap()`, or at the start of `_reconcile()`.
- **Linter rule**: not mechanically checkable.

### Non-atomic config write in `_write_config`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/snap_management.py:150-156`
- **Evidence**:
  ```python
  CONFIG_PATH.write_text(config)
  HASH_LOCK_PATH.write_text(hash)
  ```
  Two separate, non-atomic `write_text()` calls; a crash between them leaves a mismatched config/hash pair.
- **Impact**: Short window of inconsistent on-disk state; self-corrects on the next reconcile, but leaves the snap briefly running against an unhashed config.
- **Fix**: Write to temp files, fsync, then atomically rename both into place.
- **Linter rule**: not mechanically checkable without filesystem-level instrumentation.

### Machine lock file world-readable
- **Severity**: low
- **Kind**: security/ux
- **Where**: `src/machine_lock.py:22`, `MACHINE_LOCK_PATH`
- **Evidence**: Deployed permissions `-rw-r--r-- 1 root root 40 /etc/otel-ebpf-profiler/machine.lock`. Any local user can read the model name, model UUID prefix, and application name embedded in the fingerprint.
- **Impact**: Minor information exposure; the content is not secret but need not be world-readable.
- **Fix**: Write with `mode=0o600`.
- **Linter rule**: not currently checkable.

### `ops_tracing.set_destination` unguarded in `_reconcile_charm_tracing`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:117-119`
- **Evidence**: `charm_tracing_config` (`lib/charms/grafana_agent/v0/cos_agent.py:1380`) correctly returns `(None, None)` when the relation/cert is missing, but if it returns a real endpoint and the subsequent `ops_tracing.set_destination()` call raises, the exception is unguarded and propagates out of `_reconcile()`.
- **Impact**: An optional self-monitoring feature can put the charm into error state.
- **Fix**: Wrap the call in `try/except Exception: logger.warning(...)`.
- **Linter rule**: not currently checkable.

### Snap revision map hardcoded
- **Severity**: low
- **Kind**: maintenance
- **Where**: `src/snap_management.py:49-52`
- **Evidence**:
  ```python
  snap_maps = {
      "otel-ebpf-profiler": {
          ("classic", "amd64"): 6,   # 0.135.0
          ("classic", "arm64"): 5,   # 0.135.0
      },
  }
  ```
- **Impact**: Requires manual bump on every upstream snap release; the repo added a Renovate config at HEAD, which should help.
- **Fix**: Confirm Renovate monitors the snap store; consider a CI staleness check.
- **Linter rule**: not mechanically checkable.

### Ruff RET505 in vendored libraries
- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/certificate_transfer_interface/v1/certificate_transfer.py:483`, `lib/charms/operator_libs_linux/v2/snap.py:1255`
- **Evidence**: Unnecessary `else` after `return`; `tox -e lint` only checks `src/` and `tests/`, not `lib/`.
- **Fix**: `ruff check --fix lib/`.
- **Linter rule**: RET505 — mechanically checkable with `ruff check lib/`.

### Codespell typo in test comment
- **Severity**: nit
- **Kind**: lint
- **Where**: `tests/unit/charm/test_config.py:70`
- **Evidence**: `# AND the updated config contains the profling otlp exporter` ("profling" → "profiling").
- **Fix**: `codespell --write-changes tests/`.
- **Linter rule**: codespell SPELLING — mechanically checkable.

## Worth copying

- **Reconciler pattern** (`cosl.reconciler.observe_events`, `src/charm.py:42-47`): cleanly separates setup/teardown/reconcile without per-event handler sprawl.
- **Machine-level exclusive lock design intent** (`src/machine_lock.py`): the mechanism is simple and race-free within Juju's hook execution model, even though the fingerprint choice is buggy (see finding above).
- **Snap revision pinning with `snap.hold()`** (`src/snap_management.py:96`): prevents unwanted refreshes; good for reproducibility.
- **Config hash tracking for idempotent restarts** (`src/snap_management.py:161-167`): only SIGHUPs when config actually changed.
- **Topology label injection** (`src/config_builder.py:112-122`): `resource/profiling-topology-injector` adds `juju_*` labels to emitted profiles for multi-tenant attribution.
- **Status precedence with early startup polling** (`src/charm.py:136-142`): 5× poll with 0.1 s sleep avoids false-blocked during snap startup; correct use of `CollectStatusEvent.add_status()` priority.
- **`check_status` LXC detection** (`src/snap_management.py:188-198`): detects LXC and advises redeploying with `virt-type=virtual-machine`.
- **`charm_tracing_config` pattern** (`lib/charms/grafana_agent/v0/cos_agent.py:1380-1418`): guards correctly against missing relations/certs, returning `(None, None)` — a good reference for optional-integration handling.
- **Unit test structure**: good use of `ops.testing.Context` (ops_scenario) for state-transition testing.

## Common-practice notes

- Correct use of the reconciler pattern, `JujuTopology`, and `COSAgentProvider`; follows ecosystem conventions.
- Charm libraries fetched at build time under `lib/charms/<charm>/v0|v1/`, with correct LIBID/LIBAPI/LIBPATCH.
- `charmcraft.yaml` uses the `uv` plugin; version generated via `git describe`; assumes `juju >= 3.6`; no `dispatch` override. `charmcraft analyse` reports a cosmetic ENTRYPOINT error (unexpanded variable in the error message) but the charm deploys and runs correctly.
- Terraform module is present and well-documented (defaults `arch=amd64`, `virt-type=virtual-machine`), but the channel validation is broken (see findings).
- CI uses canonical `charm-pull-request.yaml`/`charm-quality-gates.yaml`; Terraform tests are disabled.
- No charm config options — deliberate, relation-driven design; means no runtime tuning of sampling/debug exporter settings without a new relation.
- Machine-only substrate; a Kubernetes port is tracked in open issue #46 but not started.
- Upgrade path: `UpgradeCharmEvent` handled via `_setup()`/`install_snap()`, correctly reinstalling the pinned snap revision; lock fingerprint stable across upgrades.

## Tests

**Unit tests** (`tox -e unit`): 47 tests, 88% line coverage, all pass. 6 `PydanticDeprecatedSince20` warnings (see finding above).

Coverage gaps (from `coverage report`):
- `src/charm.py:79-80` — `except snap.SnapError` branch in `_setup()`, not exercised
- `src/charm.py:87-88` — `_should_reload_snap` retry-start branch, not exercised
- `src/charm.py:104` — retry-loop exit path after 5 failures
- `src/charm.py:142` — polling loop completing all 5 iterations
- `src/snap_management.py:32-33, 58-59, 64` — `SnapMap` static methods, trivially untested
- `src/snap_management.py:175-181` — `reload()` body, entirely uncovered
- `src/snap_management.py:150-156` — `_write_config()`, entirely uncovered
- `src/snap_management.py:207` — install_snap path

**Static analysis**:
- pyright on `src/` + `tests/`: 0 errors, 0 warnings
- ruff on `src/` + `tests/`: 0 errors
- ruff on `lib/`: 2 RET505 (auto-fixable), not in `tox -e lint` scope
- codespell on `src/` + `tests/`: 1 typo (`tests/unit/charm/test_config.py:70`)
- `tox -e lint` and `tox -e static` pass

**Integration tests** (pytest-bdd + jubilant, real assertions against snap logs):
- `test_profiling_integration.py` — end-to-end profiler → collector; asserts `"otelcol.signal": "profiles"`, `"sample records"` in snap logs
- `test_profiling_integration_tls.py` — same with self-signed-certificates; **expected to fail** given the v1/v0 TLS bug
- `test_self_monitoring.py` — cos-agent integration: log/metric scraping, loki alerts, charm traces
- `test_colocated_profilers.py` — machine lock enforcement; asserts second deploy goes `blocked` with `"is already being profiled"`, but uses a **different application name**, so it does not catch the same-app co-residence bug

Integration tests were not run in this review (require physical machines/VMs with eBPF support).

**Terraform tests**: disabled in CI; `tests/terraform/test_terraform_module.py` exists but fails on the channel-validation mismatch.

## Docs

- **README.md**: minimal (128 bytes) — "Deploys and operates otel-ebpf-profiler-snap on machine Juju models."
- **CONTRIBUTING.md**: good — documents `tox` workflow, `charmcraft pack`, dev setup.
- **charmcraft.yaml description**: strong — full feature list, COS docs link, supported languages.
- **terraform/README.md**: good input/output docs, clearly documents the `virt-type=virtual-machine` constraint.
- **Open issue #46**: confirms a Kubernetes port is planned but not started.

## Open questions

1. Does `certificate_transfer_interface/v0` work with `self-signed-certificates`? Only v1 is vendored; the fix requires either vendoring v0, patching v1's fallback, or reading the unit databag directly.
2. Can the `_should_reload_snap` bug actually be triggered on Juju 3.6 in production? The most plausible trigger is `_reload_snap()` throwing before completing, leaving the flag `True` into the next hook — not exercised in this review.
3. `test_colocated_profilers.py` uses a different application name and so does not catch the same-app/same-machine lock bug — should it be extended to cover that case?
4. Is the crash-window in `_write_config`'s non-atomic writes actually reachable in practice (e.g. via SIGKILL mid-write), and does the next reconcile reliably correct it? Not tested here.
5. When `opentelemetry-collector` (the profiling provider in this test) is itself in `error` state for lack of a `send-profiles` backend, is that the intended degraded mode, or should `otel-ebpf-profiler` surface the subordinate's error rather than staying silently `active`? *(unverified — not established whether this is by design)*
