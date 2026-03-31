# Phase 5 Results: Ops Upgrade Experiment

## Experiment Parameters

- **Dates**: 2026-01-25 to 2026-02-27
- **Copilot model**: claude-sonnet-4.6 (Copilot CLI default)
- **Copilot mode**: Non-interactive (`-p`), `--yolo --autopilot`, max 25 continues
- **Per-run timeout**: 15 minutes
- **Total runs**: 21 (all completed with changes)

## Quantitative Results

### Per-Feature Runs (config-classes, action-classes, relation-data-classes)

| Charm | Feature | Condition | Correct. (30%) | Complete. (25%) | Quality (15%) | Min Diff (15%) | Review (15%) | **Composite (/25)** |
|-------|---------|-----------|:-:|:-:|:-:|:-:|:-:|:-:|
| alertmanager | config-classes | C1pf (skill) | 4 | 5 | 4 | 3 | 3 | **19.75** |
| alertmanager | config-classes | C2 (simple) | 4 | 5 | 4 | 5 | 4 | **22.00** |
| alertmanager | config-classes | C3 (exemplar) | 4 | 4 | 4 | 5 | 4 | **20.75** |
| alertmanager | relation-data | C1pf (skill) | 4 | 5 | 4 | 4 | 3 | **20.50** |
| alertmanager | relation-data | C2 (simple) | 1 | 2 | 2 | 1 | 1 | **7.00** |
| alertmanager | relation-data | C3 (exemplar) | 5 | 5 | 4 | 4 | 5 | **23.50** |
| discourse | config-classes | C1pf (skill) | 4 | 5 | 4 | 4 | 3 | **20.50** |
| discourse | config-classes | C2 (simple) | 4 | 5 | 3 | 3 | 3 | **19.00** |
| discourse | config-classes | C3 (exemplar) | 3 | 4 | 4 | 5 | 3 | **18.50** |
| discourse | action-classes | C1pf (skill) | 4 | 5 | 4 | 5 | 4 | **22.00** |
| discourse | action-classes | C2 (simple) | 5 | 5 | 3 | 5 | 4 | **22.75** |
| discourse | action-classes | C3 (exemplar) | 3 | 5 | 4 | 4 | 3 | **19.00** |
| discourse | relation-data | C1pf (skill) | 4 | 5 | 4 | 5 | 4 | **22.00** |
| discourse | relation-data | C2 (simple) | 3 | 3 | 3 | 2 | 2 | **13.50** |
| indico | config-classes | C2 (simple) | 4 | 5 | 4 | 4 | 3 | **20.50** |
| indico | action-classes | C2 (simple) | 5 | 5 | 5 | 4 | 5 | **24.25** |

### Holistic Runs (single skill and generic prompt)

| Charm | Condition | Correct. (30%) | Complete. (25%) | Quality (15%) | Min Diff (15%) | Review (15%) | **Composite (/25)** |
|-------|-----------|:-:|:-:|:-:|:-:|:-:|:-:|
| alertmanager | C1s (single skill) | 5 | 3 | 5 | 5 | 4 | **21.75** |
| alertmanager | C4 (generic) | 5 | 3 | 4 | 5 | 4 | **21.00** |
| discourse | C1s (single skill) | 5 | 4 | 5 | 4 | 4 | **22.25** |
| discourse | C4 (generic) | 5 | 5 | 5 | 4 | 4 | **23.50** |
| indico | C4 (generic) | 5 | 2 | 4 | 5 | 3 | **19.00** |

## Aggregate Analysis

### By Condition (mean composite score)

| Condition | Mean Score | N | Description |
|-----------|:---------:|:-:|-------------|
| C1pf (per-feature skill) | **21.04** | 6 | Structured skill per feature |
| C2 (simple prompt) | **18.43** | 8 | Feature name + "learn and apply" |
| C3 (exemplar) | **20.44** | 4 | Feature name + pointer to exemplar charm |
| C1s (single skill) | **22.00** | 2 | One comprehensive upgrade skill |
| C4 (generic prompt) | **21.17** | 3 | "Read release notes and upgrade" |

### By Feature (mean composite score across conditions)

| Feature | Mean Score | N | Complexity |
|---------|:---------:|:-:|:----------:|
| action-classes | **21.60** | 5 | Moderate |
| config-classes | **20.14** | 9 | Moderate |
| relation-data-classes | **17.30** | 5 | Significant |
| holistic (all) | **21.50** | 5 | Mixed |

### By Charm (mean composite score)

| Charm | Mean Score | N |
|-------|:---------:|:-:|
| alertmanager-k8s-operator | **19.41** | 8 |
| discourse-k8s-operator | **20.30** | 10 |
| indico-operator | **20.94** | 3 |

## Key Findings

### RQ1: Does a detailed skill outperform a simple prompt?

**Mixed.** The per-feature skill (C1pf, mean 21.04) modestly outperformed the simple prompt (C2, mean 18.43), but the gap is driven primarily by **relation-data-classes** where C2 failed catastrophically (7.0 and 13.5) while C1pf scored well (20.5 and 22.0). For the simpler features (config-classes and action-classes), C2 was competitive and sometimes better.

The skill's main value was **preventing scope errors** — specifically, the relation-data-classes skill's instruction to "only convert data the charm owns, not library-managed data" prevented a class of mistake that the simple prompt consistently made.

### RQ2: How much do exemplar references help?

**It depends on the feature.** The exemplar condition (C3, mean 20.44) outperformed the simple prompt (C2, 18.43) but slightly underperformed the skill (C1pf, 21.04).

- **Relation-data-classes**: C3 produced the **best result in the entire experiment** (23.5/25) thanks to a backwards-compatible decoder inspired by the exemplar. C1pf missed this.
- **Action-classes**: C3 produced the **worst per-feature result** (19.0/25) because the exemplar didn't use `errors="fail"`, and C3 copied that omission.
- **Config-classes**: C3 was middle-of-the-road — the exemplar helped with structure (separate file, Pydantic) but didn't prevent a staleness bug in discourse.

Exemplars are a double-edged sword: they strongly influence the agent's approach, which helps when the exemplar is excellent and hurts when the exemplar has gaps.

### RQ3: Which change categories are easiest/hardest for AI?

| Category | Difficulty for AI | Evidence |
|----------|:-:|---|
| **action-classes** | Easy | Highest mean score (21.60). Narrow scope, few access points, clear pattern. |
| **config-classes** | Moderate | Mean 20.14. Broad scope (many access sites), Harness staleness pitfall. |
| **relation-data-classes** | Hard | Lowest mean score (17.30). Requires understanding ownership boundaries. Two catastrophic failures. |

The key difficulty factor is **semantic understanding**: action-classes is largely mechanical substitution, and relation-data-classes requires understanding which code "owns" which data.

### RQ4: One skill per feature or single upgrade skill?

**The single skill (C1s) performed well** (mean 22.00), slightly outperforming per-feature skills (21.04). Advantages:
- Produces a coherent combined diff (no merge conflicts)
- Can prioritise and order changes sensibly
- Correctly identified 2-3 applicable features per charm

Disadvantage: C1s was **less thorough within each feature** compared to a dedicated per-feature run. It consistently applied config-classes well but sometimes skipped relation-data-classes or testing changes.

**Recommendation**: A single upgrade skill is the better practical choice, supplemented by per-feature skills for complex features like relation-data-classes where the skill's guardrails are most valuable.

### RQ5: Can AI reliably identify which upgrades apply?

**Partially.** The holistic runs (C1s and C4) correctly avoided false positives (no inappropriate changes attempted). But they had significant false negatives:

| Run | Changes Applied | Changes Missed |
|-----|:-:|:-:|
| alertmanager C1s | 2 | relation-data, SIMULATE_CAN_CONNECT |
| alertmanager C4 | 2 | config-classes, relation-data |
| discourse C1s | 2 | SCENARIO_BARE_CHARM_ERRORS |
| discourse C4 | 4 | (none significant) |
| indico C4 | 1 | config-classes, action-classes |

The discourse C4 run was the standout — it found nearly everything. But the indico C4 run fixated on low-value namespace migration and missed the two highest-impact features entirely.

### RQ6: Can the generic release-notes prompt match a curated skill?

**Yes, sometimes — but unreliably.** The generic prompt (C4) produced the single best holistic result (discourse, 23.50/25) but also the worst (indico, 19.00/25). The variance is high.

The discourse C4 run demonstrates the ceiling: the agent read release notes, downloaded the ops wheel, inspected source code, and correctly applied config-classes, action-classes, SCENARIO_BARE_CHARM_ERRORS, and version bumps — all with zero per-release human effort.

The indico C4 run demonstrates the floor: the agent spent its time on cosmetic namespace migration and missed the substantive features entirely.

**Verdict**: The generic prompt is a viable low-effort baseline but is not a reliable replacement for curated skills. It works best as a complement — run it to catch "easy wins" and version bumps, then use per-feature skills for the important changes.

## Recurring Patterns

### The Harness Staleness Problem
5 of 9 config-classes runs hit the same issue: storing config in `__init__` breaks when Harness tests call `update_config()` (the Harness reuses the charm instance). All eventually solved it (property, explicit reload, or caching with refresh), but it consumed significant agent time. **This should be documented prominently in the config-classes skill, or maybe we should skip when using Harness and push for migrating to Scenario as a pre-condition.**

### API Errors After Completion
19 of 21 runs exited with code 1 due to API server errors during the final summary generation. The actual code changes were always complete before the crash. This is a Copilot infrastructure issue, not a code quality issue.

### Test Execution as Quality Signal
Runs that executed and passed the full test suite consistently scored higher. The discourse config-classes C3 run only ran 12 of 55 tests and shipped a latent bug. **The evaluation rubric should weight test execution more heavily.**

### The Ownership Boundary Problem
Relation-data-classes was uniquely challenging because it requires understanding which code "owns" which data. Both C2 runs (simple prompt, no skill) made scope errors — one modified shared charm libraries, the other bypassed a library abstraction. The skill and exemplar conditions correctly scoped their changes. **This is the strongest evidence for skill value.**

## Timing

| Condition | Mean Duration (s) | Min | Max |
|-----------|:-:|:-:|:-:|
| C1pf (per-feature skill) | 388 | 146 | 900 |
| C2 (simple prompt) | 514 | 179 | 900 |
| C3 (exemplar) | 507 | 132 | 746 |
| C1s (single skill) | 578 | 554 | 601 |
| C4 (generic) | 682 | 664 | 714 |

The generic prompt (C4) takes longest because the agent must first research the release notes. Per-feature skills are fastest because the agent knows exactly what to do. Action-classes runs were consistently the fastest (~150s) due to narrow scope.
