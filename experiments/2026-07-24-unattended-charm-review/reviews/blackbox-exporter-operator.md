# blackbox-exporter-operator

A Juju machine subordinate charm that deploys the `prometheus-blackbox-exporter` snap, generates Prometheus scrape jobs (self-monitoring, cross-unit ICMP connectivity checks, and user-provided probes), and exposes them over the `cos-agent` interface to an `opentelemetry-collector` or `grafana-agent`. The core reconciler pattern is clean and unit tests pass (19/19 via tox), but this review found three critical, reproducible runtime bugs: an uncaught `TypeError` from malformed `probes_file` YAML that puts the unit in `ErrorStatus` instead of `BlockedStatus`; an infinite unit-spawning cascade when `cos-agent` is related between two `juju-info` subordinates (the exact topology the README recommends); and a stuck `BlockedStatus` that never clears once the underlying config is fixed. A maintainer should fix the cascade first — it destroys models and matches the shipped example bundle — then the two status-handling bugs, before adding any new features.

| | |
|---|---|
| Repo | canonical/blackbox-exporter-operator @ 7e2dc3d (2026-07-07) |
| Charms | blackbox-exporter (machine, subordinate) |
| Substrate | machine (LXD) |
| Deployed | yes — packed locally and deployed to concierge-lxd-4 (rev 1, local charm) across three models; also charmhub 0.28/stable (rev 36) |
| Reviewed | 2026-08-22 |

## What it does

Deploys the `prometheus-blackbox-exporter` snap (strict confinement, pinned per-architecture revisions), writes a YAML config to `/var/snap/prometheus-blackbox-exporter/current/blackbox.yml`, generates three classes of Prometheus scrape jobs (self-monitoring at `:9115/metrics`, cross-unit ICMP connectivity checks, and user-supplied probes via `probes_file` config), and writes them over the `cos-agent` relation to an OpenTelemetry Collector or Grafana Agent on the same machine. Subordinate to any principal charm via `juju-info`. Uses a file-based singleton lock manager (`/opt/singleton_snaps/`) so multiple units on the same machine share one snap installation.

## Deployment log

### Model 1: `rv-blackbox-01` (first deployment, 1 unit)

```
juju add-model rv-blackbox-01 --controller concierge-lxd-4          # OK
juju deploy ./blackbox-exporter_ubuntu@24.04-amd64.charm blackbox-exporter-local
juju relate blackbox-exporter-local:juju-info ubuntu:juju-info
# Wait ~3 min — unit became active/idle
# Snap installed: prometheus-blackbox-exporter rev 35 (amd64), held
# Hook sequence: install → peers-relation-created → start → config-changed

# Valid probes_file set: unit stayed active   ✓
# Invalid probes_file (YAML scalar "not even yaml"):
#   → config-changed hook fired → TypeError uncaught → ErrorStatus
#   → debug-log: "TypeError: models.ProbesFile() argument after ** must be a mapping, not list"
#   → both blackbox-exporter-local units went to ErrorStatus
#   → charm never reached BlockedStatus — hook kept retrying

# cos-agent relation between blackbox-exporter-local and opentelemetry-collector:
#   → INFINITE CASCADE — new units spawned recursively
#   → blackbox-exporter-local/0 spawned opentelemetry-collector/1 subordinate
#   → opentelemetry-collector/1 spawned blackbox-exporter-local/2 subordinate ... (loop)
#   → Model destroyed to recover

# Corrected config (valid probes YAML) restored active state ✓
```

### Model 2: `rv-blackbox-02` (clean deployment, 2 units)

```
juju add-model rv-blackbox-02 --controller concierge-lxd-4          # OK
juju deploy --channel stable ubuntu   # 2 units
# Wait for both ubuntu units active

juju deploy ./blackbox-exporter_ubuntu@24.04-amd64.charm blackbox-exporter
juju relate blackbox-exporter:juju-info ubuntu:juju-info
juju deploy --channel 2/edge opentelemetry-collector
juju relate opentelemetry-collector:juju-info ubuntu:juju-info
# Both blackbox-exporter units active within ~3 min
# Both opentelemetry-collector units blocked (missing backend config)

# cos-agent relation between blackbox-exporter and opentelemetry-collector:
#   → SAME CASCADE confirmed on clean 2-unit deployment
#   → blackbox-exporter/1 (on machine 0) spawned opentelemetry-collector/2 subordinate
#   → opentelemetry-collector/2 spawned blackbox-exporter/3 subordinate ... (loop)
#   → opentelemetry-collector/0 went to ErrorStatus
#   → "ValueError: unexpected error: subordinate relation cos-agent:X should have exactly one unit"
#   → Relation removed to stop cascade

# Invalid probes_file: same TypeError → ErrorStatus on both units   ✓ CONFIRMED
# Valid probes_file: active restored ✓
# Bad config_file (invalid YAML): BlockedStatus "Config file is invalid" ✓ CORRECT
# Bad config_file (valid YAML, missing modules): BlockedStatus ✓ CORRECT
# Config cleared to empty after bad config:
#   → units remained Blocked "Config file is invalid" (status NOT recovered) ← BUG
#   → config was already correct but stored status not reset
# juju-info relation removed:
#   → units went terminated/lost ✓ CORRECT
# juju remove-application:
#   → snap uninstalled from machines ✓ CORRECT
# Scale up (add ubuntu/2 → blackbox-exporter/10 on machine 2):
#   → snap installed on machine 2, unit active ✓ CORRECT
# juju refresh: not testable from local charm (requires --path flag)
```

### Model 3: `rv-blackbox-03` (charmhub version)

```
juju deploy blackbox-exporter --channel stable   # rev 36 from charmhub
# Installed and activated correctly, same as local
# charmhub 0.28/stable is rev 36; default-release in metadata is rev 38
# Local code 7e2dc3d is 1 commit ahead of rev36, 3 commits behind rev38
```

**Local HEAD vs deployed**: local is at `7e2dc3d` (2026-07-07, confirmed against `_context/head.txt`), charmhub 0.28/stable is rev 36. The code is broadly equivalent; the commits between rev36 and rev38 are CI/blueprint refresh changes only.

## Observed behaviour

- Install hook fires and correctly installs the snap (rev 35 for amd64), starts it with `--enable`, sets `ActiveStatus`. Timeline: ~3 minutes.
- Unit status transitions: `waiting: installing agent` → `maintenance: Installing snap` → `maintenance: Starting snap` → `active: idle`.
- The `juju-info` relation joined successfully; the `juju-info-relation-changed` hook fired on the principal side.
- The `peers-relation-created` hook fires but defers since there are no peers yet.
- **Valid `probes_file` config** → unit stays `Active`. **Invalid `probes_file`** → `ErrorStatus` with uncaught `TypeError`, not `BlockedStatus`.
- **Bad `config_file`** (invalid YAML or valid YAML missing `modules`) → `BlockedStatus` "Config file is invalid; see debug-log" ✓ CORRECT.
- **Config cleared to empty after bad config** → units remained `Blocked` despite the config now being valid. The `_push_config` early-return path does not reset `_stored.status["config"]` to `ActiveStatus`.
- **`cos-agent` relation between two `juju-info` subordinates** → infinite scaling cascade (see Findings).
- **`_restart_snap` failure** — unit status stays `Active` even when snap restart fails (only a warning is logged). The `CollectStatusEvent` handler checks `is_snap_active()` and would surface a blocked status if the snap is inactive, but only at the next update-status, not immediately after the failed restart.
- **`juju-info` relation removed** → subordinate units correctly went `terminated/lost`.
- **`juju remove-application`** → remove hook fired, snap uninstalled from all machines.
- **Scale up** (adding a new principal unit) → new blackbox-exporter subordinate unit installed and activated on the new machine, singleton lock correctly managed.
- **No actions defined** — confirmed by `juju actions blackbox-exporter`: "No actions defined".
- The bundled `cos_agent.py` library (`LIBPATCH=25`) uses deprecated `data.json()` instead of `data.model_dump_json()` (3 occurrences). The system `cosl` is version 1.10.2.

## Findings

### `TypeError` from non-mapping YAML probes input causes hook crash and `ErrorStatus`, not `BlockedStatus`

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:348–358`
- **Evidence** (runtime):
  ```
  TypeError: models.ProbesFile() argument after ** must be a mapping, not list
  unit-blackbox-exporter-0: ERROR juju.worker.uniter.operation hook "config-changed" failed: exit status 1
  ```
  Injected by setting `probes_file="not even yaml"` (a valid YAML scalar string). `yaml.safe_load("not even yaml")` returns the string `"not even yaml"` unchanged; `ProbesFile(**"not even yaml")` then raises `TypeError` because `**` requires a mapping, not a string. Confirmed multiple non-mapping YAML inputs trigger the same path: scalar strings, YAML lists (`'[job1, job2]'`), numbers, booleans. The `except Exception` only catches `yaml.YAMLError`; the `except ValidationError` only catches pydantic validation failures. Neither catches this `TypeError`.
- **Impact**: The hook exits with code 1 and the unit enters `ErrorStatus`. Both units on both machines went to `ErrorStatus` simultaneously in testing. The charm never reaches `BlockedStatus` — it keeps retrying the failed hook indefinitely, and operators see a bare "hook failed: config-changed" with no indication of the cause.
- **Fix**: Catch `TypeError` alongside `yaml.YAMLError`:
  ```python
  except (yaml.YAMLError, TypeError, ValidationError) as e:
      logger.warning("Error validating probes file: %s", e)
      self._stored.status["probes_file"] = to_tuple(
          BlockedStatus("Invalid probes file; see debug-log")
      )
      return []
  ```
- **Linter rule**: not mechanically checkable; requires knowing `yaml.safe_load` can return non-dict values for scalar YAML input.

### `cos-agent` relation between two `juju-info` subordinates causes infinite scaling cascade

- **Severity**: critical
- **Kind**: bug (resource exhaustion / design)
- **Where**: `lib/charms/grafana_agent/v0/cos_agent.py:1052–1054` (crash site); design issue in charm topology and missing `limit: 1` in `charmcraft.yaml`
- **Evidence** (runtime, reproduced on both `rv-blackbox-01` and `rv-blackbox-02`):
  ```
  juju relate blackbox-exporter:cos-agent opentelemetry-collector:cos-agent
  # blackbox-exporter/0  → opentelemetry-collector/1 (juju-info subordinate)
  # opentelemetry-collector/1 → blackbox-exporter/2 (juju-info subordinate)
  # blackbox-exporter/2  → opentelemetry-collector/3 ... [loop]
  # opentelemetry-collector/0 ERROR: "ValueError: unexpected error: subordinate relation
  #    cos-agent:X should have exactly one unit"
  ```
  Both charms are `juju-info` subordinates (`scope: container`). When related via `cos-agent`, Juju treats each unit of one charm as a principal for the other. Each new principal creates a subordinate of the other charm via `juju-info`, which creates another principal, and so on. `COSAgentRequirer._on_relation_data_changed` (`cos_agent.py:1049`) raises an unhandled `ValueError` when it sees more than one unit in the subordinate cos-agent relation, propagating as an uncaught hook failure.

  `charmcraft.yaml` does not set `limit: 1` on the `cos-agent` provides relation, which the `COSAgentProvider` library documentation explicitly requires to prevent multiple grafana-agent apps on the same VM.

  The README bundle (lines 60–82) shows `be:cos-agent → otel:cos-agent` as a valid integration — exactly the topology that triggers the cascade.
- **Impact**: Operators following the README sample topology have their model consumed by the cascade. Removing the relation stops new spawns but does not clean up existing cascade units; recovery in this review required destroying the model.
- **Fix**: (a) Add `limit: 1` to the `cos-agent` provides relation in `charmcraft.yaml`. (b) Guard `cos_agent.py` against the multi-unit case instead of raising an unhandled `ValueError`. (c) Until fixed, document the incompatibility in the README, or change the recommended topology so opentelemetry-collector is deployed as a standalone principal rather than a `juju-info` subordinate.
- **Linter rule**: not mechanically checkable without understanding Juju's subordinate relation model.

### `_push_config` does not reset `BlockedStatus` when returning early with a valid config

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:142–148`
- **Evidence** (runtime):
  ```
  # Step 1: bad config_file → units go Blocked "Config file is invalid"
  juju config blackbox-exporter config_file="targets: [charmhub.io]"
  # units: blocked ✓

  # Step 2: clear config to empty (valid) → units SHOULD recover
  juju config blackbox-exporter config_file=""
  # After 60s: units STILL blocked "Config file is invalid" ← BUG
  ```
  `_push_config` returns `False` early when `current_config == DEFAULT_CONFIG_FILE and not config`. This branch performs no status update, so `_stored.status["config"]` remains at its previous `BlockedStatus`. `_reconcile` only calls `_restart_snap` when `_push_config()` returns `True`, so no action fires that would surface the fix.
- **Impact**: After fixing a bad `config_file`, the charm does not recover automatically; the unit stays `Blocked` until an unrelated hook re-evaluates status.
- **Fix**:
  ```python
  if current_config == config or (current_config == DEFAULT_CONFIG_FILE and not config):
      self._stored.status["config"] = to_tuple(ActiveStatus())
      return False
  ```
- **Linter rule**: general rule — "early-return paths that short-circuit a status-computation method must still set the status".

### `SnapNotFoundError` not caught during snap start (Issue #36 partially fixed)

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:217–219`
- **Evidence**:
  ```python
  except snap.SnapError:           # does NOT cover SnapNotFoundError
      logger.warning(f"Failed to start snap {snap_name}")
  ```
  `snap.SnapNotFoundError` inherits from `Error` directly, not from `SnapError` (confirmed at `snap.py:290` and `snap.py:312` in the bundled library). Issue #36 reported this exact symptom; the earlier fix added `except snap.SnapError` but missed `SnapNotFoundError`.
- **Impact**: Transient or permanent snap-store unavailability causes the charm to loop in error rather than reaching `BlockedStatus` with an actionable message.
- **Fix**:
  ```python
  except (snap.SnapError, snap.SnapNotFoundError) as e:
      logger.warning("Failed to start snap %s: %s", snap_name, e)
      self._stored.status["snap"] = to_tuple(
          BlockedStatus(f"Snap {snap_name} unavailable; see debug-log")
      )
  ```
- **Linter rule**: not mechanically checkable without semantic knowledge of the exception hierarchy.

### Non-idempotent `relabel_configs` injection into custom scrape jobs

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:382` (inside the `for static_config` loop at `src/charm.py:379`)
- **Evidence**: `job['relabel_configs'] = self._relabel_configs` is assigned inside the `for static_config in job.get("static_configs", [])` loop, so it runs once per `static_config` (N times for N static configs) and silently overwrites any user-supplied `relabel_configs` without warning.
- **Impact**: An operator supplying `relabel_configs` in `probes_file` finds those configs silently discarded; their labels never apply, and this is hard to debug from the outside.
- **Fix**: Move the assignment outside the loop and merge instead of overwriting:
  ```python
  existing = job.get('relabel_configs', [])
  if existing:
      logger.warning("User-supplied relabel_configs in probes_file will be overwritten")
  job['relabel_configs'] = self._relabel_configs
  ```
- **Linter rule**: not mechanically checkable without semantic analysis of the YAML content.

### `limit: 1` missing from `cos-agent` provides relation

- **Severity**: high
- **Kind**: bug
- **Where**: `charmcraft.yaml` (`provides.cos-agent`)
- **Evidence**: The `cos-agent` provides relation has no `limit` set. The `COSAgentProvider` library documentation (`lib/charms/grafana_agent/v0/cos_agent.py:38–40`) explicitly requires `limit: 1` to prevent two grafana-agent-style apps on the same VM.
- **Impact**: When multiple cos-agent requirers are deployed on the same machine, they conflict silently; this is also a contributing factor to the cascade finding above.
- **Fix**: Add `limit: 1` to the `cos-agent` provides relation in `charmcraft.yaml`.
- **Linter rule**: not mechanically checkable without library-specific documentation knowledge.

### `cos_agent.py` uses deprecated Pydantic API (`data.json()`)

- **Severity**: medium
- **Kind**: lint
- **Where**: `lib/charms/grafana_agent/v0/cos_agent.py:702, 1033, 1082`
- **Evidence**:
  ```
  PydanticDeprecatedSince20: The `json` method is deprecated; use `model_dump_json` instead.
  ```
  Three calls to `data.json()` observed at runtime during unit tests. The bundled library is `LIBPATCH=25`; the system `cosl` is 1.10.2 — the bundled copy is stale.
- **Impact**: Deprecation warning at runtime now; will break outright when Pydantic V3 lands. Bug fixes present in newer library versions are also missing.
- **Fix**: Refresh the bundled library with `charmcraft fetch-lib`, or replace `.json()` calls with `.model_dump_json()`.
- **Linter rule**: `ruff` custom rule to detect `.json()` calls on pydantic model instances.

### Dead log placeholders in snap install and restart

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:207`, `src/charm.py:162`
- **Evidence**:
  ```python
  logger.info("Installing snap {snap_name}")   # plain string, literal text
  logger.info(f"Restarting snap {snap_name}")   # f-string, correct
  ```
  At line 207 the literal `{snap_name}` is logged verbatim; line 162 does the equivalent correctly.
- **Impact**: Diagnosing slow or failed installs from debug-log is harder when messages are opaque.
- **Fix**: `logger.info("Installing snap %s", snap_name)` or use an f-string as at line 162.
- **Linter rule**: custom rule to detect string literals containing `{...}` not inside an f-string.

### `_restart_snap` failure is invisible to operators

- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:160–163`
- **Evidence**: Restart failure logs a warning but does not update `_stored.status["snap"]`, so the charm appears `Active` while the snap is not running. `CollectStatusEvent` would surface this at the next update-status, not immediately.
- **Impact**: After a config change that requires a restart, the operator has no immediate signal that the restart failed.
- **Fix**: Set `_stored.status["snap"]` to `BlockedStatus` on restart failure.
- **Linter rule**: "exception handler that catches an exception must update status or re-raise" — mechanically checkable.

### `_remove_snap` log message uses literal placeholders, not interpolated values

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:254`
- **Evidence**:
  ```python
  except (snap.SnapError, SnapSpecError):
      logger.error("Failed to uninstall {snap_name} snap: {e}")  # plain string
  ```
  Also, `snap.SnapNotFoundError` is not included in this `except` clause.
- **Fix**:
  ```python
  except (snap.SnapError, snap.SnapNotFoundError, SnapSpecError):
      logger.error("Failed to uninstall %s snap: %s", snap_name, e)
  ```
- **Linter rule**: same as dead-log-placeholder finding above.

### README documents the topology that triggers the cascade

- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md:60–82`
- **Evidence**: Sample bundle relates `be:cos-agent → otel:cos-agent`, the exact topology confirmed (twice) to trigger the infinite cascade bug described above.
- **Impact**: Following the documented example destroys the model.
- **Fix**: Correct or annotate the sample bundle until the underlying cascade bug is fixed.
- **Linter rule**: not mechanically checkable.

### `is_snap_active` has two dead log placeholders

- **Severity**: low
- **Kind**: bug
- **Where**: `src/utils.py:98, 100`
- **Evidence**:
  ```python
  logger.warning("Snap {snap_name} is not active. Ensure provided config is valid.")
  logger.info("Unable to determine the activeness status of snap {snap_name}: %s", e)
  ```
  Both have literal `{snap_name}`; the first is a plain string, the second mixes `%s` formatting with a literal placeholder.
- **Fix**: `logger.warning("Snap %s is not active...", snap_name)` and `logger.info("Unable to determine...snap %s: %s", snap_name, e)`.
- **Linter rule**: same as dead-log-placeholder finding above.

### `min_items` deprecated in Pydantic V2

- **Severity**: low
- **Kind**: lint
- **Where**: `src/models.py:16, 23, 44`
- **Evidence**:
  ```python
  targets: List[str] = Field(..., min_items=1)  # type: ignore
  ```
  Emits `PydanticDeprecatedSince20` at runtime.
- **Fix**: Replace `min_items=1` with `min_length=1`.
- **Linter rule**: checkable with `pyright` or a `ruff` custom rule.

### `requires-python = "~=3.10"` is ambiguous

- **Severity**: low
- **Kind**: lint
- **Where**: `pyproject.toml:9`
- **Evidence**: Charmcraft warns this will be interpreted as `>=3.10, <4`. The build environment uses Python 3.12.
- **Fix**: Use `requires-python = ">=3.10"` or `~=3.10.0`.
- **Linter rule**: custom rule to flag ambiguous tilde specifiers.

### Snap revision pinned with no auto-update mechanism

- **Severity**: low
- **Kind**: ux
- **Where**: `src/snap_management.py:36–44`
- **Evidence**: Revisions 35/36/37/38 for snap version 0.28.0, pinned per architecture. No Renovate rule tracks the upstream snap.
- **Fix**: Consider a Renovate rule or channel-based pinning.
- **Linter rule**: not established.

### Missing terraform module

- **Severity**: medium
- **Kind**: docs
- **Where**: project root
- **Evidence**: No `.tf` files present. `charms.just` references a `tf-0.28.0` tag but no terraform module is bundled.
- **Fix**: Add a terraform module under `terraform/`.
- **Linter rule**: not established.

### `cosl`/library dependencies bundled instead of fetched at build time

- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/grafana_agent/v0/cos_agent.py`, `lib/charms/operator_libs_linux/v2/snap.py`
- **Evidence**: Libraries are committed to the repo rather than fetched via tooling.
- **Fix**: Use `charmcraft fetch-lib` at build time to keep libraries current.
- **Linter rule**: not established.

## Worth copying

- **CompositeStatus pattern with StoredState** (`src/charm.py:45–83`): `CompositeStatus` TypedDict stored in `StoredState` as `{snap, config, probes_file}` with `to_tuple`/`to_status` helpers. Clean and idiomatic.
- **`cosl.reconciler.observe_events` for event-driven reconciliation** (`src/charm.py:119`): `observe_events(self, all_events, self._reconcile)` is a clean, modern reconciler pattern (push config, restart if needed, update peer data).
- **Singleton snap manager** (`src/singleton_snap.py`): File-based locks at `/opt/singleton_snaps/` handle the multi-unit snap-sharing race condition robustly.
- **`file_contents` sentinel** (`src/utils.py:74–78`): Returns `None` for absent files; `_push_config` uses this as a "never written" sentinel. Clean.
- **Dashboard template with Loki integration** (`src/grafana_dashboards/blackbox.json.tmpl`): Prometheus datasource plus a Loki logs panel, with `${prometheusds}` and `${lokids}` populated by `COSAgentProvider`.
- **`_machine_ip` binding for network bind address** (`src/charm.py:418–425`): Uses `model.get_binding("juju-info").network.bind_address` — the correct way to get a machine's network address for self-monitoring.

## Common-practice notes

| Convention | This charm | Notes |
|---|---|---|
| `lib/charms/` bundled libs | Yes | Should use `charmcraft fetch-lib` |
| `src/` layout | Yes | Clean |
| `StoredState` + `CollectStatusEvent` | Yes | CompositeStatus pattern is excellent |
| Pydantic models for validation | Yes | `Config`, `ProbesFile` well-designed |
| scenario-based unit tests | Yes | 19/19 pass via tox |
| tox as test runner | Yes | Correct |
| Renovate bot | Yes | Active |
| terraform module | No | Tag `tf-0.28.0` exists but no module |
| `cosl` reconciler | Yes | Good modern pattern |
| pydantic `min_items` | Yes, but deprecated | Should be `min_length` |
| `provides: cos-agent` optional | Yes | Correct |
| `provides: cos-agent limit: 1` | No | Required by `COSAgentProvider` docs; missing |

## Tests

| Suite | Result | Notes |
|---|---|---|
| `tox -e unit` | 19/19 pass | All tests pass |
| `tox -e lint` | 0 errors | Ruff passes cleanly |
| `tox -e static` | 0 errors | Pyright passes cleanly (0 errors, 0 warnings) |
| `tests/integration/test_charm_and_scaling.py` | not run | Requires local charm path; runtime observation used instead |

**Coverage report** (from `tox -e unit`):

| File | Coverage | Notes |
|---|---|---|
| `src/charm.py` | 72% | Missing: install/upgrade hook paths, snap management errors, probes_file `TypeError` path, `relabel_configs` overwrite, `_restart_snap` failure, `_remove_snap` errors |
| `src/singleton_snap.py` | 40% | — |
| `src/snap_management.py` | 52% | — |
| `src/utils.py` | 64% | Missing: `is_snap_active` error paths, `file_contents` error paths |
| `lib/charms/grafana_agent/v0/cos_agent.py` | 30% | — |
| `lib/charms/operator_libs_linux/v2/snap.py` | 23% | — |

**Coverage gaps relative to findings**:
- No test for `SnapNotFoundError` during snap start → `ErrorStatus`
- No test for `TypeError` from non-mapping YAML input
- No test for `_restart_snap` failure → status
- No test for `_push_config` early-return with valid config → status recovery
- No test exercising the `cos-agent` relation with a real consumer (cascade not testable in isolation)
- No test for `relabel_configs` overwrite

## Docs

**README.md** (6668 bytes) is otherwise strong — sample deployment bundle, `probes_file` config walkthrough, Prometheus remote-write setup, Loki log forwarding, mermaid COS topology diagram, clear explanation of the three job types. **Doc/reality mismatch**: the README sample bundle relates `be:cos-agent → otel:cos-agent`, the topology that causes the infinite scaling cascade when both charms are `juju-info` subordinates (as in the bundle). The cascade was reproduced twice on clean deployments in this review. Either the bundle is wrong, `cos_agent.py` has a bug handling subordinate-to-subordinate `cos-agent` relations, or blackbox-exporter should not be deployed as a `juju-info` subordinate when related to opentelemetry-collector via `cos-agent`.

**No terraform module**: despite the `tf-0.28.0` git tag existing.

**SECURITY.md**: placeholder only, no actual security contact.

**CONTRIBUTING.md**: minimal (983 bytes), no project-specific guidance.

## Open questions

1. **cos-agent cascade topology**: is the README bundle wrong, is there a code bug in `cos_agent.py` (`COSAgentRequirer` can't handle subordinate-to-subordinate `cos-agent` relations), or is this a design limitation that needs documenting? Reproduced on two clean deployments.
2. **TypeError path**: confirmed scalar strings, YAML lists, numbers, and booleans all trigger the `TypeError` from non-mapping `probes_file` YAML — are there other input shapes that also trigger it?
3. **Issue #36**: root cause confirmed (`SnapNotFoundError` not caught). Fix needed in both `_install_snaps` and `_restart_snap`.
4. **scrape_configs mismatch**: the TODO at `src/charm.py:93` notes that `_all_scrape_jobs` must stay in sync with the `scrape_configs` passed to `COSAgentProvider`. Is there a test verifying this? (unverified — not confirmed either way in this review)
5. **Bundled library staleness**: bundled `cos_agent.py` is `LIBPATCH=25`, system `cosl` is 1.10.2. A newer library may fix the cascade issue and the `data.json()` deprecation; should be updated and re-tested.
