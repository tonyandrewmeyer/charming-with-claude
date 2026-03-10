# Methodology

## Overview

This document details the experimental protocol for the ops upgrade experiment.

## Independent Variables

### 1. Guidance Level (3 conditions)

| Condition | Description |
|-----------|-------------|
| **Dedicated skill** | Structured skill file with context, before/after examples, step-by-step instructions, exemplar references, and verification steps |
| **Simple prompt (feature-specific)** | Feature name and description only; no examples, no instructions beyond "learn about this and apply it" |
| **Simple prompt + exemplar** | Feature name plus a pointer to a charm that already uses the feature |
| **Generic release-notes prompt** | A reusable, feature-agnostic prompt that asks the agent to read the release notes, analyse the impact on the charm, and prepare an upgrade branch. Requires zero per-release human effort. |

### 2. Feature Type

Each ops change is categorised by:

* **Type**: feature / deprecation / breaking change / improvement / bug fix
* **Complexity**: trivial / moderate / significant
* **Domain**: core ops / testing (ops-scenario) / tracing (ops-tracing)

### 3. Target Charm

~5 charms selected to provide diversity in complexity, domain, and ops version. Ideally, a variety of types of charm (infrastructure and user-facing, different domains), teams that own the charm (observability, data, analytics, platform engineering, and so on), age (well established through to very new), ideally published (meaning findable via search in charmhub, see https://github.com/canonical/operator/blob/main/.github/workflows/published-charms-tests.yaml for a list of those), within the ~5 constraint

## Dependent Variables

Scored per the [evaluation rubric](./evaluation-rubric.md):

1. **Correctness** (30%) -- APIs used correctly, code works
2. **Completeness** (25%) -- all instances of the pattern found and updated
3. **Code quality** (15%) -- idiomatic, clean, follows the new pattern well
4. **Minimal diff** (15%) -- no unnecessary changes
5. **Human review needed** (15%) -- merge-readiness

Additional metrics tracked but not scored:

* Changes correctly identified as applicable (for the "single skill" approach)
* False positives (changes attempted that don't apply)
* Observable use of exemplar references
* Approximate time and token usage

## Controls

* **Same Copilot version** for all runs
* **Same charm commit** pinned for each target charm across all conditions
* **Light supervision only** -- accept Copilot's output without steering, unless it gets stuck in a loop
* **Same evaluation rubric** and evaluator for all runs

## Execution Protocol

### Phase 1: Change Catalogue

1. Clone or fetch the latest ops, ops-scenario, and ops-tracing repositories
2. Review CHANGES.md / CHANGELOG.md / release notes for the past year
3. For each significant change, create a file in `changes/` using the template:

```markdown
# [Change ID]

## Version
ops X.Y / ops-scenario X.Y / ops-tracing X.Y

## Type
Feature / deprecation / breaking change / improvement

## Summary
One-line description.

## Before
[Code example showing the old way]

## After
[Code example showing the new way]

## Why Upgrade
Why a charmer should adopt this.

## Complexity
Trivial / moderate / significant

## Detection
How to detect whether a charm would benefit from this change.
(e.g. "grep for `self.unit.status =`" or "check if the charm defines `collect_unit_status`")

## Exemplar Charms
- [charm-name](link) -- brief note on how they use it

## Pitfalls
Known edge cases or common mistakes when adopting this change.
```

4. Create `changes/index.md` summarising all changes in a table

### Phase 2: Exemplar Search

For each change in the catalogue:

1. Search GitHub for the new API/pattern across `canonical/` repos
2. Filter for charms (look for `metadata.yaml` or `charmcraft.yaml` in the repo)
3. Evaluate whether the usage looks intentional and well-implemented
4. Record the best 1-3 exemplars per change

Search strategies:
* GitHub code search for specific API calls (e.g. `collect_unit_status`)
* GitHub code search for import patterns (e.g. `from ops.tracing import`)
* Review known well-maintained charms (tempo-k8s, traefik-k8s, grafana-k8s, etc.)

### Phase 3: Skill Construction

Build skills in both formats:

**Per-feature skills**: One SKILL.md per change, in `skills/[change-id]/SKILL.md`

**Single upgrade skill**: One comprehensive `skills/ops-upgrade/SKILL.md` that:
1. Instructs the agent to analyse the charm's ops usage
2. Identifies applicable upgrades from the catalogue
3. Applies them in dependency order
4. Verifies the result

### Phase 4: Charm Selection

1. Assemble a candidate list of ~15-20 charms
2. For each, check:
   * Current ops version (from `requirements.txt` / `pyproject.toml`)
   * Number of applicable changes from the catalogue
   * Test coverage (unit and integration)
   * Whether it uses or could use ops-tracing
   * Last ops-related update
3. Select ~5 that maximise diversity and coverage of the change catalogue

### Phase 5: Evaluation Runs

For each target charm × each applicable change:

1. **Prepare**: Clone the charm at the pinned commit into a fresh Copilot workspace
2. **Run Condition 1** (Dedicated skill):
   * Install the skill
   * Prompt: "Upgrade this charm's ops usage. There is a skill available for this." (or feature-specific variant)
   * Record output (diff, transcript, time)
3. **Run Condition 2** (Simple prompt, feature-specific):
   * No skill installed
   * Prompt: "ops [version] added [feature]. Learn how to use that and update this charm to make use of it."
   * Record output
4. **Run Condition 3** (Simple prompt + exemplar):
   * No skill installed
   * Prompt: "ops [version] added [feature]. [exemplar-charm] already uses this -- look at how they did it and update this charm similarly."
   * Record output
5. **Run Condition 4** (Generic release-notes prompt):
   * No skill installed
   * Prompt: "There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis."
   * Record output
   * **Additionally record**: which changes the agent identified, which it missed, and any false positives
6. **Evaluate** each run against the rubric

### Sequencing

Not every change needs to be tested against every charm. Prioritise:

* At least 2 charms per change (to avoid charm-specific quirks dominating)
* At least 3 changes per charm (to test the "single upgrade skill" approach)
* All 3 conditions for each charm×change pair tested

## Limitations

* **Evaluator bias**: The same person (likely the experiment author) evaluates all runs. Mitigated by using a structured rubric and scoring before comparing across conditions.
* **Copilot variability**: Copilot may produce different results on different runs of the same condition. We run each condition once per charm×change pair, which means individual results may not be representative. The aggregate across all pairs is more reliable.
* **Exemplar quality**: The "gold standard" exemplar charms may themselves have imperfect implementations. We mitigate this by reviewing exemplars before using them.
* **Feature selection**: The catalogue may miss changes or overweight certain types. We mitigate by systematic review of changelogs rather than relying on memory.
* **Charm selection**: With only ~5 charms, results may not generalise to the full ecosystem. We mitigate by selecting for diversity.
