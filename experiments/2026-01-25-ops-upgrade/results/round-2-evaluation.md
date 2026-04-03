# Round 2 Detailed Evaluation: Per-Run Scoring

## Scoring Rubric

Same rubric as round 1, per the [evaluation rubric](../evaluation-rubric.md). Composite = weighted average × 5.

- **Correctness** (30%): APIs correct, code works, tests pass
- **Completeness** (25%): All instances found and updated, deps updated
- **Code quality** (15%): Idiomatic, clean, follows the new pattern well
- **Minimal diff** (15%): No unnecessary changes
- **Human review needed** (15%): Merge-readiness

Runs that timed out with no changes (+0 -0) are noted as **N/S** (not scored).

---

## set-ports

Baseline: all three charms used `open_port()`/`close_port()` (or manual port diffing) and needed converting to the declarative `Unit.set_ports()` API.

### alertmanager-k8s × set-ports

#### C1pf (Per-Feature Skill) — 24.25/25

Replaced the 14-line manual diff body of `set_ports()` with `self.unit.set_ports(ops.Port("tcp", self._ports.api), ops.Port("tcp", self._ports.ha))`. Removed `OpenedPort` import. 57/57 tests passed.

- Slightly verbose (`ops.Port("tcp", ...)` instead of bare integers) but functionally correct
- Preserved the `set_ports()` method wrapper

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 4 | 5 | 5 | **24.25** |

#### C2 (Simple Prompt) — 25.00/25

Replaced method body with `self.unit.set_ports(self._ports.api, self._ports.ha)`. Removed `OpenedPort` import. Bare integers default to TCP. 57/57 tests passed.

- Cleanest solution across all set-ports runs
- Minimal, idiomatic, nothing unnecessary

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 5 | 5 | 5 | **25.00** |

#### C3 (Exemplar) — 23.50/25

Removed the entire `set_ports()` method and inlined `self.unit.set_ports(self._ports.api, self._ports.ha)` at the single call site. Removed `OpenedPort` import. 57/57 tests passed.

- Inlining the method eliminates a named abstraction that had a docstring
- Functionally correct but debatable style choice

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 4 | 4 | 5 | **23.50** |

#### C4 (Generic Prompt) — N/S (TIMEOUT)

Spent 15 minutes reading release notes, exploring source, and running tests. Never made any changes. Classic scope paralysis from the open-ended prompt.

---

### grafana-k8s × set-ports

#### C1pf (Per-Feature Skill) — 24.25/25

Replaced `_set_ports()` body with leader/non-leader branching: leader calls `self.unit.set_ports(Port(protocol="tcp", port=WORKLOAD_PORT))`, non-leader calls `self.unit.set_ports()`. Kept existing `Port` import. 122/122 tests passed.

- Leader/non-leader logic correctly preserved
- `Port` import was already present, so keeping it is appropriate

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 4 | 5 | 5 | **24.25** |

#### C2 (Simple Prompt) — 25.00/25

Same logic as C1pf but also removed the `from ops.model import Port` since bare integers suffice. Leader: `self.unit.set_ports(WORKLOAD_PORT)`, non-leader: `self.unit.set_ports()`. 122/122 tests passed.

- Cleanest solution — removed unnecessary import
- Correct use of bare integer (defaults to TCP)

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 5 | 5 | 5 | **25.00** |

#### C3 (Exemplar) — 22.75/25

Same conversion but compressed into a one-liner: `self.unit.set_ports(*([WORKLOAD_PORT] if self.unit.is_leader() else []))`. 122/122 tests passed.

- Functionally correct but less readable than the if/else approach
- A reviewer would ask to expand this

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 3 | 5 | 4 | **22.75** |

#### C4 (Generic Prompt) — N/S (TIMEOUT)

Same pattern as alertmanager C4. Spent all time reading release notes and exploring source without making changes.

---

### zinc-k8s × set-ports

#### C1pf (Per-Feature Skill) — 24.25/25

Replaced `self.unit.open_port(protocol="tcp", port=self._zinc.port)` with `self.unit.set_ports(ops.Port("tcp", self._zinc.port))`. 11/11 tests passed.

- Slightly verbose (`ops.Port`) but correct
- Single port, single call — simplest possible conversion

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 4 | 5 | 5 | **24.25** |

#### C2 (Simple Prompt) — 25.00/25

Replaced with `self.unit.set_ports(self._zinc.port)`. Bare integer, cleanest possible. 11/11 tests passed.

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 5 | 5 | 5 | **25.00** |

#### C3 (Exemplar) — 25.00/25

Identical to C2: `self.unit.set_ports(self._zinc.port)`. 11/11 tests passed.

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 5 | 5 | 5 | **25.00** |

#### C4 (Generic Prompt) — 12.50/25

Did NOT make the set-ports conversion. Instead: bumped `requires-python` to `>=3.10`, added `SCENARIO_BARE_CHARM_ERRORS` conftest, and ran `uv lock --upgrade-package ops` regenerating the lockfile (+52 -810, mostly lock churn).

- Missed the actual target feature entirely
- Changes made are reasonable for a general upgrade but not what was needed
- `open_port()` call left untouched

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 1 | 3 | 2 | 2 | **12.50** |

---

## ops-tracing

Baseline: alertmanager and loki both use the community `charm_tracing` library with `@trace_charm` decorator, `TracingEndpointRequirer`, and `charm_tracing_config()`. The target migration replaces these with `ops.tracing.Tracing()`.

Note: **tempo-k8s** and **traefik-k8s** timed out with no changes across all 4 conditions (8 runs total). These are more complex charms where the migration proved too difficult for the agent within the 15-minute window.

### alertmanager-k8s × ops-tracing

#### C1pf (Per-Feature Skill) — 22.00/25

Deleted both `charm_tracing.py` and `tracing.py` library files (~1981 lines). Updated `pyproject.toml` to `ops[tracing]`. Removed `@trace_charm` decorator. Added `self.tracing = ops.tracing.Tracing(self, "tracing")`. Updated test conftest. Updated `uv.lock`.

- Correct and complete migration
- **Penalty**: copilot-instructions.md skill file leaked into the repo (+175 lines)
- Spent time debugging `import ops.tracing` vs `from ops import tracing` namespace issues

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 4 | 3 | 4 | **22.00** |

#### C2 (Simple Prompt) — 23.00/25

Same core migration plus added `receive-ca-cert` relation to `charmcraft.yaml` (recommended for TLS support). Did not update `uv.lock`.

- The `receive-ca-cert` addition is a quality touch that other conditions missed
- Missing lockfile update is a gap but not a correctness issue

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 4 | 5 | 5 | 4 | **23.00** |

#### C3 (Exemplar) — 20.25/25

Updated imports and added `ops.tracing.Tracing()`. Updated deps and lockfile. But **did NOT delete the community library files** (~2000 lines of dead code remain).

- Charm code migration is correct
- Fastest run (7 minutes)
- Significant cleanup gap — dead library code

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 3 | 4 | 5 | 3 | **20.25** |

#### C4 (Generic Prompt) — 22.00/25

Complete migration: deleted both libraries, updated deps, added `receive-ca-cert`, updated `tox.ini`. Most thorough run, but massive lockfile regeneration (1319 lines).

- Most complete of the alertmanager ops-tracing runs
- Excessive lockfile churn from dependency resolver re-run
- Spent significant time on web research (many 404s fetching release pages)

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 4 | 3 | 4 | **22.00** |

---

### loki-k8s × ops-tracing

Loki is more complex: it has **two** tracing relations — `charm-tracing` (charm code traces, the one to migrate) and workload tracing via `TracingEndpointRequirer` (must be preserved). The `charm-tracing` relation name differs from the default `tracing`, requiring `tracing_relation_name="charm-tracing"` in the constructor.

#### C1pf (Per-Feature Skill) — N/S (diff not captured)

The run completed and the output indicates a correct migration: updated deps, removed decorator, added `ops.tracing.Tracing(self, tracing_relation_name="charm-tracing")`, deleted `charm_tracing.py` while preserving `tracing.py` for workload tracing. 71/71 tests passed. However, the agent committed its changes during the run, so the post-run `git diff` captured +0 -0. **Cannot be reliably scored from output alone.**

#### C2 (Simple Prompt) — 23.00/25

Correct migration: deleted `charm_tracing.py`, kept `tracing.py` for workload tracing. Added `receive-ca-cert` relation. Used correct `tracing_relation_name="charm-tracing"`. Missing lockfile update.

- Properly handled the dual-tracing complexity
- The `receive-ca-cert` addition shows good migration knowledge

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 4 | 5 | 5 | 4 | **23.00** |

#### C3 (Exemplar) — 18.25/25

Correct code migration but **renamed the `charm-tracing` relation to `tracing`** in `charmcraft.yaml`. This is a **breaking change** — existing relations would fail on upgrade. Tests pass because they don't catch relation renames.

- Core migration code is correct
- Breaking relation rename is the most significant error across all ops-tracing runs
- Correctly preserved `tracing.py` for workload tracing

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 3 | 5 | 3 | 5 | 2 | **18.25** |

#### C4 (Generic Prompt) — 17.75/25

Correct core migration with the **best relation name handling** (`tracing_relation_name="charm-tracing"`). But significant scope creep: changed `requires-python` to `>=3.10`, migrated test imports from `scenario` to `ops.testing`, updated `black`/`pyright` configs. Aggressive version pin (`ops[tracing]>=3.6.0`). Did NOT delete `charm_tracing.py`.

- Best relation handling of all loki runs
- Scope creep: Python version bump, test framework migration, tooling configs
- Used `ops_tracing._mock.patch_tracing()` — private API, fragile
- Dead library code remains

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 4 | 4 | 2 | 3 | **17.75** |

---

## pebble-check-events

Baseline: charms have Pebble-managed containers with existing health check definitions (or should add them). The task is to add `pebble-check-failed` and `pebble-check-recovered` event handlers with appropriate status management.

Note: **discourse-k8s** and **indico-operator** timed out with no changes across all 4 conditions (8 runs total).

### content-cache-k8s × pebble-check-events

#### C1pf (Per-Feature Skill) — 20.75/25

Added `pebble_check_failed` and `pebble_check_recovered` observers on the `content-cache` container. Failed handler sets `BlockedStatus`; recovered handler sets `ActiveStatus()`. Added 2 unit tests.

- Handlers work but recovered blindly sets `ActiveStatus()` — could mask other problems
- No check definitions added (relies on pre-existing checks — acceptable)
- Uses `self.on["content-cache"]` bracket syntax (valid but less conventional)

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 4 | 4 | 5 | 4 | **20.75** |

#### C2 (Simple Prompt) — 20.00/25

Added handlers with check-name routing: distinguishes critical `content-cache` check from non-critical `exporter` check. Added 4 unit tests covering both check names for both events.

- Good differentiation of critical vs non-critical checks
- Check-name comparison logic is slightly odd (compares to container name)
- Same blind `ActiveStatus()` on recovery
- Most comprehensive tests of the content-cache runs

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 4 | 4 | 4 | 4 | **20.00** |

#### C3 (Exemplar) — 16.00/25

Added handlers that **only log** — no status changes on failure or recovery. No tests written. Followed the kratos exemplar too literally (kratos uses log-only handlers).

- Handlers are essentially no-ops beyond logging
- No tests, no status management — minimal operational value
- The exemplar was a poor guide here (kratos's log-only pattern is not best practice)

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 2 | 3 | 5 | 2 | **16.00** |

#### C4 (Generic Prompt) — N/S (TIMEOUT)

No changes produced. Spent entire session on research.

---

### wordpress-k8s × pebble-check-events

#### C1pf (Per-Feature Skill) — 24.25/25

Added handlers for the `wordpress` container. Failed sets `BlockedStatus`. **Recovered calls `self._reconciliation(event)`** — the only run across all pebble-check-events to use reconciliation on recovery instead of blindly setting status. Added 2 tests: one checks BlockedStatus on failure, one verifies reconciliation triggers on recovery.

- **Best pebble-check-events result** across all runs
- Reconciliation on recovery is the correct charm pattern
- Minor: uses `ops.BlockedStatus` while the rest of the charm uses `BlockedStatus` directly

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 5 | 5 | 4 | **24.25** |

#### C2 (Simple Prompt) — 21.25/25

Added handlers with check-name routing for `wordpress-ready` and `apache-exporter-up`. Uses `MaintenanceStatus` on failure (debatable — `BlockedStatus` is more conventional). Blind `ActiveStatus()` on recovery. 4 comprehensive tests. Timed out but all changes were already committed.

- Most comprehensive tests (4 tests, both check names, both events)
- `MaintenanceStatus` choice is unconventional for a check failure
- Recovery doesn't use reconciliation

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 5 | 4 | 4 | 4 | **21.25** |

#### C3 (Exemplar) — 16.75/25

Added handlers that **only log**. No tests. Did refactor check names to constants and imported `_APACHE_EXPORTER_PEBBLE_CHECK` from `cos.py` (nice touch).

- Log-only handlers following the kratos exemplar — minimal value
- Good constant usage but no functional impact
- Same exemplar problem as content-cache C3

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 2 | 4 | 5 | 2 | **16.75** |

#### C4 (Generic Prompt) — N/S (TIMEOUT)

No changes produced.

---

## action-testing

Baseline: wordpress-k8s uses the old pattern of mocking action events via fixtures in conftest.py rather than the modern `Harness.run_action()` API.

Note: **indico-operator** C1pf and C2 both completed with +0 -0. This is correct behaviour — indico's test suite does not use the old action mock pattern, so there was nothing to upgrade.

### wordpress-k8s × action-testing

#### C1pf (Per-Feature Skill) — 25.00/25

Converted all 8 action tests to `harness.run_action()`. Removed `action_event_mock` fixture from conftest. Success cases use `output = harness.run_action(...)` with `assert output.results == {...}`. Failure cases use `pytest.raises(ActionFailed)`. Added `@pytest.mark.usefixtures("attach_storage")` to prevent defer-on-action-event bug. 43/43 tests passed.

- Test-only change, perfectly focused
- All 8 tests converted correctly
- The `attach_storage` fixture addition was necessary (genuine bug prevention)

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 5 | 5 | 5 | **25.00** |

#### C2 (Simple Prompt) — 23.50/25

Same test conversions as C1pf, plus refactored `src/charm.py`: extracted `_do_reconciliation()` to fix the root cause of action events being passed to `_reconciliation()` (which calls `defer()`).

- Also fixed the root cause in production code — more thorough than C1pf
- The charm code change goes beyond "action-testing" scope
- 43/43 tests passed

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 5 | 4 | 4 | **23.50** |

---

## ops-testing-migration

All 4 runs (wordpress C1pf, wordpress C2, content-cache C1pf, content-cache C2) timed out with +0 -0 changes.

This confirms the round 1 finding: Harness → Scenario migration is the hardest category, requiring paradigm-level understanding. The 15-minute window was insufficient.

---

## Holistic Runs

### content-cache-k8s C1s (Single Upgrade Skill) — 23.00/25

Applied three upgrade patterns:
1. **Typed config**: created `src/config.py` with `ContentCacheConfig` dataclass, replaced all `self.config[...]` accesses with `self.typed_config.xxx` via a `@property` using `load_config(errors="blocked")`
2. **Lifecycle defer fix**: removed `event.defer()` from `configure_workload_container()` (called from `_on_upgrade_charm`, a non-deferrable event), replaced with `WaitingStatus`
3. **Action testing**: added `test_report_visits_by_ip_action` using `harness.run_action()`

Did NOT bump ops version in `pyproject.toml` — an oversight.

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 4 | 5 | 5 | 4 | **23.00** |

### wordpress-k8s C1s (Single Upgrade Skill) — 19.25/25

Applied:
1. **Typed config**: created `src/charm_config.py` with `WordpressConfig` Pydantic model (13 fields), replaced all config accesses
2. **Action params**: used `event.load_params(UpdateDatabaseParams, errors="fail")` for action parameter loading
3. **SCENARIO_BARE_CHARM_ERRORS**: added to `tox.toml`
4. **Version bump**: ops from `==3.5.1` to `>=3.6`

But: copilot-instructions.md skill file leaked into repo (+386 lines), missed action-testing migration, missed lifecycle defer fix.

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 4 | 4 | 2 | 3 | **19.25** |

### wordpress-k8s C4 (Generic Prompt) — 17.00/25

Version bump only: ops from `==3.5.1` to `==3.7.0` in `pyproject.toml` and `uv.lock`. No feature upgrades applied despite many applicable patterns.

- Spent ~9 minutes reading release notes for a 5-line version bump
- Considered test migration but decided complexity was too high
- Did not attempt typed config, action testing, or any feature

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 1 | 4 | 5 | 2 | **17.00** |

### zinc-k8s C4 (Generic Prompt) — 17.50/25

Bumped ops to `>=3.7.0`. Changed `requires-python` to `>=3.10`. Changed `pebble_layer()` return type to `ops.pebble.Layer`. Added `SCENARIO_BARE_CHARM_ERRORS` via conftest. Regenerated `uv.lock` (-833 lines, mostly resolution marker cleanup).

- Did NOT find or apply set-ports (the only feature applicable to zinc)
- Real code changes are small (+16 -6 excluding lockfile)
- The `pebble.Layer` typing improvement is nice but minor

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 2 | 4 | 3 | 3 | **17.50** |

### Holistic Timeouts (N/S)

The following holistic runs all timed out with no changes:

| Charm | C1s | C4 |
|-------|-----|-----|
| alertmanager-k8s | TIMEOUT | TIMEOUT |
| discourse-k8s | TIMEOUT | TIMEOUT |
| content-cache-k8s | — | TIMEOUT |
| grafana-k8s | — | TIMEOUT |
| loki-k8s | — | TIMEOUT |
| tempo-k8s | — | TIMEOUT |
| traefik-k8s | — | TIMEOUT |

Note: alertmanager and discourse C1s/C4 were scored successfully in round 1 (21.75, 21.00, 22.25, 23.50) but failed as timeouts when re-run in round 2. This may indicate a regression in the tooling or model behaviour between rounds. The round 2 metadata notes the model was "TBC (pin before starting runs)" — if a different model was used, this could explain the regression.

Missing run: **indico-operator C1s** was in the run schedule but no result directory exists.
