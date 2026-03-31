# Detailed Evaluation: Per-Run Scoring

## Scoring Rubric

Each dimension scored 1-5 per the [evaluation rubric](../evaluation-rubric.md). Composite = weighted average × 5.

- **Correctness** (30%): APIs correct, code works, tests pass
- **Completeness** (25%): All instances found and updated, deps updated
- **Code quality** (15%): Idiomatic, clean, follows the new pattern well
- **Minimal diff** (15%): No unnecessary changes
- **Human review needed** (15%): Merge-readiness

---

## alertmanager-k8s-operator × config-classes

### C1pf (Per-Feature Skill) — 19.75/25

Created `src/config.py` with Pydantic `AlertmanagerCharmConfig` model. Added `@property typed_config` calling `load_config(errors="blocked")`. Replaced all 4 config access sites. Removed `cast` import. Updated ops to `>=2.23.0`.

- Initially stored in `__init__`, self-corrected to property after test failures (Harness staleness)
- 57/57 tests passed
- **Penalty**: Copilot-instructions skill file leaked into the repo as `.github/copilot-instructions.md`

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 5 | 4 | 3 | 3 | **19.75** |

### C2 (Simple Prompt) — 22.00/25

Defined `CharmConfig` dataclass inline in `charm.py`. Called `load_config(CharmConfig)` locally in each method (no caching, no property). Replaced all 4 access sites. Updated ops to `>=2.23.0`.

- Used dataclass (simpler than Pydantic, appropriate for this charm)
- No `errors="blocked"` — less user-friendly but valid
- 57/57 tests passed
- Cleanest, most focused diff

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 5 | 4 | 5 | 4 | **22.00** |

### C3 (Exemplar) — 20.75/25

Created `src/config.py` with Pydantic `AlertmanagerConfig`. Added `@property typed_config` with `errors="blocked"`. Replaced all 4 access sites. Visibly influenced by conserver-charm exemplar.

- Left a redundant `cast(str, config)` call that other runs cleaned up
- 57/57 tests passed
- Exemplar clearly influenced the Pydantic + separate file + `errors="blocked"` pattern

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 4 | 4 | 5 | 4 | **20.75** |

---

## alertmanager-k8s-operator × relation-data-classes

Baseline: 2 charm-owned `relation.data[]` access sites (peer unit's `private_address`). All other relation data managed by charm libraries.

### C1pf (Per-Feature Skill) — 20.50/25

Added `ReplicasUnitData` dataclass. Converted both write and read paths. Updated 3 test files to use JSON-encoded values. Updated ops to `>=2.23.0`.

- Correctly scoped to charm-owned data only
- **Issue**: Serialisation format change breaks backwards compatibility during rolling upgrades (tests needed JSON-quoted strings)
- 57/57 tests passed (after test modifications)

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 5 | 4 | 4 | 3 | **20.50** |

### C2 (Simple Prompt) — 7.00/25

Added `_PeerUnitData` dataclass. **Also modified two shared charm libraries** (`alertmanager_dispatch.py`, `alertmanager_remote_configuration.py`), converting their internal relation data handling and bumping LIBPATCH versions. Removed backwards-compatibility fields from `_ProviderSchemaV1`.

- **Critical error**: Modified library-managed relation data — these are shared libraries consumed by other charms
- Removed V0 backwards-compatibility fallback in the dispatch library
- No ops version upgrade in the diff
- Session crashed before tests could run

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2 | 2 | 1 | 1 | **7.00** |

### C3 (Exemplar) — 23.50/25

Added `PeerRelationUnitData` Pydantic model. Added `_decode_relation_str()` backwards-compatible decoder (tries JSON, falls back to raw string). Converted both paths. Updated ops to `>=2.23.0`.

- **Best result in the entire experiment**
- Backwards-compatible decoder means no test changes needed, rolling upgrades work
- Correctly scoped to charm-owned data only
- 57/57 tests passed without modification

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 4 | 4 | 5 | **23.50** |

---

## discourse-k8s-operator × config-classes

Baseline: ~52 `self.config[...]` accesses across a large charm with 30 config options.

### C1pf (Per-Feature Skill) — 20.50/25

Created `src/config.py` with `DiscourseConfig` frozen dataclass. Added `@property typed_config`. Replaced all 52 config accesses. Self-corrected from `__init__` to property after Harness staleness issue.

- No `errors="blocked"` — validation errors raise exceptions
- 55/55 tests passed, lint passed
- Clean separation into config.py

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 5 | 4 | 4 | 3 | **20.50** |

### C2 (Simple Prompt) — 19.00/25

Defined `DiscourseConfig` Pydantic model inline in charm.py. Stored in `__init__`, reloaded in `_on_config_changed`. Used `errors="blocked"`. Initially removed validation checks (thinking Pydantic would handle them), had to restore them.

- Longest session (~15 min API time)
- Unnecessary reordering of validation checks
- 55/55 tests passed

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 5 | 3 | 3 | 3 | **19.00** |

### C3 (Exemplar) — 18.50/25

Created `src/config.py` with Pydantic `DiscourseConfig`. Stored in `__init__` with `errors="blocked"`. Replaced all config accesses. **Did not reload config in `_on_config_changed`.**

- **Latent bug**: Stale config after `config-changed` events (not caught because only 12 of 55 tests were run)
- Cleanest diff of the three
- Exemplar helped with structure but not with Harness compatibility

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 3 | 4 | 4 | 5 | 3 | **18.50** |

---

## discourse-k8s-operator × action-classes

Baseline: 3 action handlers with 6 `event.params` access sites.

### C1pf (Per-Feature Skill) — 22.00/25

Created `src/action_types.py` with 3 frozen dataclasses. Used `errors="fail"`. Added defensive `if params is None: return` guard (technically dead code with `errors="fail"`).

- Well-organised separate file with docstrings
- 55/55 tests passed
- The `None` guard is unnecessary but harmless

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 5 | 4 | 5 | 4 | **22.00** |

### C2 (Simple Prompt) — 22.75/25

Defined 3 dataclasses inline in charm.py. Used `errors="fail"`. No unnecessary `None` guard. Smallest diff.

- Correctly trusted the `_Abort` mechanism (no dead-code guard)
- 55/55 tests passed after extensive test infrastructure debugging
- Inline placement is less clean but functionally correct

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 3 | 5 | 4 | **22.75** |

### C3 (Exemplar) — 19.00/25

Created `src/action_types.py` with 3 Pydantic models using `Field(description=...)`. **Used default `errors="raise"` instead of `errors="fail"`**. Influenced by autopkgtest exemplar.

- Well-structured Pydantic models with descriptions
- **Missing `errors="fail"`** means invalid params cause unhandled exceptions instead of clean action failure
- 43/55 tests passed (not all tests run)

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 3 | 5 | 4 | 4 | 3 | **19.00** |

---

## discourse-k8s-operator × relation-data-classes

Baseline: 1 charm-owned `relation.data[]` access (redis app data). Other relation data library-managed.

### C1pf (Per-Feature Skill) — 22.00/25

Added `RedisAppData` dataclass with alias metadata. Converted the single access site. Left library-managed data alone.

- Precisely scoped to the one charm-owned access
- 55/55 tests passed
- Used `decoder=str` (appropriate for string relation data)

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 5 | 4 | 5 | 4 | **22.00** |

### C2 (Simple Prompt) — 13.50/25

Added `_RedisAppRelationData` and `_RedisUnitRelationData` Pydantic models. Converted both app and unit data. **Bypassed the RedisRequires library** by replacing `self.redis.relation_data` with direct `relation.load()`.

- Over-scoped: converted library-managed unit data
- `next(iter(relation.units))` is fragile (picks arbitrary unit)
- Pydantic dependency not added to requirements
- 12/55 tests passed

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 3 | 3 | 3 | 2 | 2 | **13.50** |

---

## indico-operator × config-classes

### C2 (Simple Prompt) — 20.50/25

Created `CharmConfig` Pydantic model in `src/state.py`. Added `@property typed_config`. Replaced all 21 config accesses. Removed `_is_configuration_valid` method, migrated its logic to a Pydantic `@validator`.

- All 42 tests passed after extensive iteration
- Navigated the Harness/`_Abort` incompatibility by using `try/except` with manual error handling
- Did not bump ops version in requirements.txt

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 5 | 4 | 4 | 3 | **20.50** |

---

## indico-operator × action-classes

### C2 (Simple Prompt) — 24.25/25

Added 2 dataclasses for the 2 actions with params. Refactored `_execute_anonymize_cmd` to accept a params object. Updated all test mocks. Bumped ops in requirements.txt and tox.ini.

- **Highest per-feature score in the experiment**
- Genuine code quality improvement (params as explicit argument)
- All 42 tests passed
- Version bumps correctly applied to both requirements.txt and tox.ini

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 5 | 4 | 5 | **24.25** |

---

## Holistic Runs

### alertmanager C1s (Single Upgrade Skill) — 21.75/25

Applied: config-classes, SCENARIO_BARE_CHARM_ERRORS, version bumps. Missed: relation-data, SIMULATE_CAN_CONNECT.

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 3 | 5 | 5 | 4 | **21.75** |

### alertmanager C4 (Generic Prompt) — 21.00/25

Applied: SIMULATE_CAN_CONNECT removal (6 files), SCENARIO_BARE_CHARM_ERRORS, stale comment cleanup, version bumps. Missed: config-classes, relation-data.

- Read release notes and ops wheel source code
- Found SIMULATE_CAN_CONNECT (which C1s missed) but missed config-classes (which C1s found)
- Complementary to C1s in coverage

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 3 | 4 | 5 | 4 | **21.00** |

### discourse C1s (Single Upgrade Skill) — 22.25/25

Applied: config-classes (Pydantic, separate file), action-classes (dataclasses, `errors="fail"`). Missed: SCENARIO_BARE_CHARM_ERRORS.

- Coherent combined diff covering both features
- Self-corrected from `__init__` to `@property` for config
- 55/55 tests passed, lint passed

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 4 | 5 | 4 | 4 | **22.25** |

### discourse C4 (Generic Prompt) — 23.50/25

Applied: config-classes, action-classes (`errors="fail"`), SCENARIO_BARE_CHARM_ERRORS, Python version bumps, classifier cleanup. **Most complete holistic run.**

- Read release notes, downloaded ops wheel, inspected source
- Found nearly everything applicable
- 55/55 tests passed, lint passed
- Pinned ops to `==3.6.0` (exact pin, not minimum)

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 5 | 5 | 4 | 4 | **23.50** |

### indico C4 (Generic Prompt) — 19.00/25

Applied: flat `ops.*` namespace migration, SCENARIO_BARE_CHARM_ERRORS, charmcraft base bump (20.04→22.04), version bumps. **Missed config-classes and action-classes entirely.**

- Thorough namespace migration across all files
- All 42 tests passed
- Fixated on low-value cosmetic changes, missed high-value feature adoption

| Correct. | Complete. | Quality | Min Diff | Review | **Score** |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 2 | 4 | 5 | 3 | **19.00** |
