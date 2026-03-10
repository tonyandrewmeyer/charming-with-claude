# Ops Upgrade: AI-Assisted Charm Modernisation

## Background

The [ops](https://github.com/canonical/operator) library (and its companions [ops-scenario](https://github.com/canonical/ops-scenario)/`ops[testing]` and [ops-tracing](https://github.com/canonical/ops-tracing)/`ops[tracing]`) have evolved significantly over the past year. New features, deprecations, and API improvements land regularly, but many charms in the ecosystem lag behind -- they work, but they don't take advantage of newer capabilities that would make the code cleaner, more correct, or more maintainable.

Tools like [pyupgrade](https://github.com/asottile/pyupgrade) and [django-upgrade](https://github.com/adamchainz/django-upgrade) solve this problem for Python and Django respectively, using AST transformations to mechanically update code. For ops, the changes are often too semantic for pure AST rewriting -- understanding *why* a charm should use a new feature requires context about Juju concepts, charm architecture, and the intent behind the code. This makes it a natural fit for AI assistance.

This experiment builds a skill (or set of skills) that upgrades charms to take advantage of recent ops changes, then evaluates whether a dedicated skill outperforms a simple prompt-based approach.

## Goals

* **Catalogue** the significant changes in ops, ops-scenario, and ops-tracing over the past year (roughly ops 2.x → 3.x, plus ops[testing] and ops[tracing] evolution).
* **Build skills** that guide an AI agent through upgrading a charm to use each new feature or adapt to each breaking change.
* **Find exemplars** -- charms that already use each feature, to serve as "gold standard" references for what a good adoption looks like.
* **Evaluate** the skills against a set of target charms, comparing:
  1. **Dedicated skill** -- a structured skill with context, examples, and step-by-step guidance.
  2. **Simple prompt** -- a bare instruction like "ops 3.x added feature Y; learn how to use that and update the charm to make use of it".
* **Run on Copilot** -- since Canonical is currently focused on GitHub Copilot, all evaluation runs will use Copilot rather than Claude Code.

## Research Questions

1. Does a detailed, feature-specific skill produce meaningfully better upgrades than a simple prompt naming the feature?
2. How much does the availability of "gold standard" exemplar charms (referenced in the skill or prompt) improve quality?
3. Which categories of ops changes are easiest/hardest for AI to apply correctly?
4. Is it better to have one skill per feature or a single "upgrade ops" skill that covers everything?
5. Can an AI agent reliably identify *which* ops upgrades are applicable to a given charm, or does it need to be told?
6. Can a generic "read the release notes and upgrade" prompt -- requiring no per-release human effort -- match the quality of a curated skill?

## Phase 1: Catalogue Ops Changes

### Scope

Review the changelogs, release notes, and commit history for the past year of:

* **ops** (core library) -- [changelog](https://github.com/canonical/operator/blob/main/CHANGES.md)
* **ops[testing]** / ops-scenario -- testing framework changes
* **ops[tracing]** / ops-tracing -- tracing integration changes

### What to Capture

For each significant change, document:

| Field | Description |
|-------|-------------|
| **Change ID** | Short identifier (e.g. `ops-collect-unit-status`) |
| **Version** | The ops version that introduced it |
| **Type** | Feature / deprecation / breaking change / improvement |
| **Summary** | One-line description |
| **Before** | What charm code looks like without this change |
| **After** | What charm code looks like with this change |
| **Why** | Why a charmer should adopt this (cleaner code, correctness, performance, etc.) |
| **Complexity** | How hard it is to apply (trivial / moderate / significant) |
| **Exemplar charms** | Charms already using this feature (found via GitHub search or known examples) |

### Deliverable

A `changes/` directory with one markdown file per change, plus a `changes/index.md` summary table.

## Phase 2: Find Exemplar Charms

For each catalogued change, search for charms that already use the new feature or pattern. Sources:

* **GitHub search** across `canonical/` and `charmed-kubernetes/` organisations
* **Known well-maintained charms** (e.g. tempo-k8s, traefik-k8s, grafana-k8s, etc.)
* **User-provided list** of charms to check

For each exemplar found, note:

* The charm and the relevant file(s)/commit(s)
* Whether the adoption looks intentional and well-done (vs. accidental or partial)
* Any patterns worth highlighting in the skill

These exemplars serve two purposes:
1. **Validation** -- confirming our "before/after" understanding is correct
2. **Reference material** -- the skill can point the agent to real-world examples

## Phase 3: Build Skills

### Approach

Based on the catalogue, build skills in two formats to test:

#### Option A: One Skill Per Feature

Each change gets its own skill file (e.g. `skills/ops-collect-unit-status/SKILL.md`) containing:

* Context on the change and why it matters
* Before/after code examples
* Step-by-step instructions for applying the change
* Links to exemplar charms
* Common pitfalls and edge cases
* Verification steps (what to check after applying)

#### Option B: Single "Upgrade Ops" Skill

One comprehensive skill that:

1. Analyses the charm's current ops version and usage patterns
2. Identifies applicable upgrades
3. Applies them in a sensible order
4. Verifies the result

The experiment should test both approaches to answer research question 4.

### Skill Format

Skills should follow the copilot-collections format so they work with GitHub Copilot. They should also be compatible with Claude Code's `.claude/skills/` structure.

## Phase 4: Select Target Charms

Choose ~5 charms for evaluation, balancing:

| Criterion | Why it matters |
|-----------|---------------|
| **Ops version** | Should be on an older ops version with room to upgrade |
| **Complexity** | Mix of simple and complex charms |
| **Test coverage** | Ideally has both unit and integration tests (to evaluate testing-related changes) |
| **Tracing** | At least one charm should use or be a candidate for ops-tracing |
| **Maintenance status** | Active enough that the upgrade would be welcome, but not so active that it's already up to date |

### Candidate Charms (to be refined)

*These are starting suggestions; the final list should be confirmed after the change catalogue is complete, so we can ensure each charm has meaningful upgrades to apply.*

| Charm | Rationale |
|-------|-----------|
| TBD | Needs to be determined after Phase 1 |
| TBD | |
| TBD | |
| TBD | |
| TBD | |

Selection criteria to apply:
* Scan `requirements.txt` / `pyproject.toml` for pinned ops version
* Check when the charm last updated its ops dependency
* Confirm there are at least 2-3 applicable changes from the catalogue
* Prefer charms from different teams/domains for diversity

## Phase 5: Evaluation

### Experimental Design

For each target charm × each applicable change (or set of changes), run three conditions:

#### Condition 1: Dedicated Skill

Prompt Copilot with the skill available and a simple instruction to use it:

> Upgrade this charm's ops usage. There is a skill available for this.

Or, for per-feature skills:

> This charm could benefit from [feature X]. There is a skill available for applying this change.

#### Condition 2: Simple Prompt (Feature-Specific)

Prompt Copilot with only a description of the feature:

> ops [version] added [feature description]. Learn how to use that feature and update this charm to make use of it.

No skill, no examples, no step-by-step guidance -- just the feature name and a nudge.

#### Condition 3: Simple Prompt + Exemplar Reference

Same as Condition 2, but with a pointer to an exemplar charm:

> ops [version] added [feature description]. The [exemplar-charm] charm already uses this feature -- look at how they did it and update this charm similarly.

This isolates the value of exemplar references from the rest of the skill.

#### Condition 4: Generic Release-Notes Prompt

A reusable, feature-agnostic prompt that asks the agent to do its own analysis:

> There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

This condition is the most practically interesting because it requires **zero per-release human effort** -- the same prompt works for every ops release without anyone needing to read the changelog first. If this approach performs comparably to the dedicated skill, it dramatically changes the cost-benefit calculation: instead of building and maintaining skills for each release, teams could simply re-run this prompt whenever ops is updated.

The trade-off is that the agent must do its own feature discovery, which introduces risk of missing changes or misunderstanding their relevance. This condition directly tests research question 5 (can an AI agent reliably identify which upgrades are applicable?).

### Evaluation Criteria

Adapt the rubric from the [Jubilant migration experiment](../2026-02-17-jubilant-migration-experiment/evaluation-rubric.md):

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Correctness** | 30% | Does the upgraded code work? Are APIs used correctly? |
| **Completeness** | 25% | Were all instances of the pattern found and updated? |
| **Code quality** | 15% | Is the result idiomatic? Does it follow the new pattern well? |
| **Minimal diff** | 15% | Were unnecessary changes avoided? |
| **Human review needed** | 15% | How much work remains for a human reviewer? |

Each dimension scored 1-5; composite score is weighted average on a 25-point scale.

### Additional Metrics

* **Applicable changes identified** -- for the "single upgrade skill" approach, did the agent correctly identify which changes apply?
* **False positives** -- did the agent try to apply changes that don't apply?
* **Exemplar influence** -- when given an exemplar, did the agent visibly use it? Did it help or introduce copy-paste issues?
* **Time/tokens** -- rough cost comparison between approaches

## Phase 6: Analysis and Write-Up

### Deliverables

1. **results/** -- raw output from each run (diffs, transcripts)
2. **results.md** -- quantitative results table and analysis
3. **evaluation.md** -- detailed evaluation of each run
4. **skills/** -- the final skill files (usable by others)
5. **guidance.md** -- practical recommendations for charm teams wanting to use the skills
6. Updated **README.md** with findings

### Key Comparisons

* Skill vs. simple prompt (per feature and overall)
* Skill vs. simple prompt + exemplar (isolating the value of structured guidance beyond just "look at this example")
* Per-feature skills vs. single upgrade skill
* Generic release-notes prompt vs. all other conditions (the "zero-effort" baseline)
* Difficulty by change category (are some types of ops changes inherently harder for AI?)
* Feature discovery accuracy: which conditions correctly identify applicable changes, and which miss or hallucinate?

## Execution Plan

| Phase | Description | Depends on |
|-------|-------------|------------|
| 1 | Catalogue ops changes | -- |
| 2 | Find exemplar charms | Phase 1 |
| 3 | Build skills | Phase 1, Phase 2 |
| 4 | Select target charms | Phase 1 |
| 5 | Run evaluations | Phase 3, Phase 4 |
| 6 | Analyse and write up | Phase 5 |

## Differences from Previous Experiments

This experiment differs from the [Jubilant migration](../2026-02-17-jubilant-migration-experiment/) and [Harness to Scenario](../2026-03-05-harness-to-scenario-migration/) experiments in several ways:

| Aspect | Previous experiments | This experiment |
|--------|---------------------|-----------------|
| **Skill** | Used an existing skill | Building the skill is part of the experiment |
| **Task scope** | Single migration task | Multiple independent upgrade tasks per charm |
| **Gold standard** | Defined by the target API (Jubilant/Scenario) | Defined by exemplar charms already using the feature |
| **Prompt comparison** | Levels of guidance (bare → recipe) | Skill vs. prompt vs. prompt+exemplar |
| **Feature discovery** | Task is given | Agent may need to identify applicable changes |

## Notes

* The experiment folder date (2026-01-25) reflects when the idea was conceived, not when execution began.
* All runs use GitHub Copilot to align with Canonical's current tooling focus.
* Skills should be designed to be upstreamed to [copilot-collections](https://github.com/canonical/copilot-collections) if they prove useful.
* The "simple prompt" condition is intentionally minimal -- the question is whether the model's existing knowledge plus a feature name is sufficient, not whether a carefully crafted prompt can match a skill.
