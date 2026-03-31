# Ops Upgrade: AI-Assisted Charm Modernisation

## Background

The [ops](https://github.com/canonical/operator) library (and its companions ops-scenario/`ops[testing]` and ops-tracing/`ops[tracing]`) continually evolve, with new releases each month, often containing new features while remaining backwards compatible. However, many charms lag behind -- they work, but they don't take advantage of newer capabilities that would make the code cleaner, more correct, or more maintainable.

Tools like [pyupgrade](https://github.com/asottile/pyupgrade) and [django-upgrade](https://github.com/adamchainz/django-upgrade) aim to solve this problem for Python and Django respectively, using AST transformations to mechanically update code. For ops, the changes are often too semantic for pure AST rewriting -- understanding *why* a charm should use a new feature requires context about Juju concepts, charm architecture, and the intent behind the code. This makes it a natural fit for AI assistance. In addition, the complexity of doing this in an AST transform style seems very likely to outweigh the benefits, but (conveniently ignoring the sustainability aspects), AI can likely do this with few resources.

This experiment builds a skill (or set of skills) that upgrades charms to take advantage of recent ops changes, then evaluates whether a dedicated skill outperforms a simple prompt-based approach.

## Goals

* **Catalogue** the significant changes in ops, ops-scenario, and ops-tracing over the past year or so.
* **Build skills** that guide an AI agent through upgrading a charm to use each new feature or adapt to each breaking change.
* **Find exemplars** -- charms that already use each feature, to serve as "gold standard" references for what a good adoption looks like.
* **Evaluate** the skills against a set of target charms, comparing:
  1. **Dedicated skill** -- a structured skill with context, examples, and step-by-step guidance.
  2. **Simple prompt** -- a bare instruction like "ops 3.x added feature Y; learn how to use that and update the charm to make use of it".
* **Run on Copilot** -- since Canonical is currently focused on GitHub Copilot, all evaluation runs will use Copilot rather than Claude Code. (Claude helped a bit with collating results, design, and so forth.)

## Research Questions

1. Does a detailed, feature-specific skill produce meaningfully better upgrades than a simple prompt naming the feature?
2. How much does the availability of "gold standard" exemplar charms (referenced in the skill or prompt) improve quality?
3. Which categories of ops changes are easiest/hardest for AI to apply correctly?
4. Is it better to have one skill per feature or a single "upgrade ops" skill that covers everything?
5. Can an AI agent reliably identify *which* ops upgrades are applicable to a given charm, or does it need to be told?
6. Can a generic "read the release notes and upgrade" prompt -- requiring no per-release human effort -- match the quality of a curated skill?

## Phase 1: Catalogue Ops Changes

To be done by Claude Code with review (by me) of the deliverables.

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

* **GitHub search** across the `canonical` organisation
* **Known well-maintained charms** (e.g. tempo-k8s, traefik-k8s, grafana-k8s, etc.)
* **User-provided list** of charms to check

For each exemplar found, note:

* The charm and the relevant file(s)/commit(s)
* Whether the adoption looks intentional and well-done (vs. accidental or partial)
* Any patterns worth highlighting in the skill

These exemplars serve two purposes:
1. **Validation** -- confirming our "before/after" understanding is correct
2. **Reference material** -- the skill can point the agent to real-world examples

Again, to be done by Claude Code with validation by me.

## Phase 3: Build Skills

As above, drafted by Claude Code, reviewed by me.

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

Skills should follow the copilot-collections format (design to work with GitHub Copilot, but also likely where they would live). They should also be compatible with Claude Code's `.claude/skills/` structure.

## Phase 4: Select Target Charms

Choose ~5 charms for evaluation, balancing:

| Criterion | Why it matters |
|-----------|---------------|
| **Ops version** | Should be on an older ops version with room to upgrade |
| **Complexity** | Mix of simple and complex charms |
| **Test coverage** | Has both unit tests (to evaluate testing-related changes) |
| **Tracing** | At least one charm should use or be a candidate for ops-tracing |
| **Maintenance status** | Active enough that the upgrade would be welcome, but not so active that it's already up to date |

### Selected Target Charms

| Charm | Ops Version | Domain | Tests (Unit/Integ) | Tracing | Complexity |
|-------|-------------|--------|-------------------|---------|------------|
| [discourse-k8s-operator](https://github.com/canonical/discourse-k8s-operator) | `==2.23.2` (hard-pinned) | Web Apps (IS DevOps) | 2/8 | No (candidate to add) | Medium (29 config, 9 relations, 3 actions) |
| [alertmanager-k8s-operator](https://github.com/canonical/alertmanager-k8s-operator) | `2.21.1` (locked) | Observability | 13/12 | Yes (charm_tracing lib, candidate to migrate to ops-tracing) | High (7 config, 14 relations, 1 action) |
| [loki-k8s-operator](https://github.com/canonical/loki-k8s-operator) | `2.21.1` (locked) | Observability / Logging | 13/19 | Yes (charm_tracing lib, candidate to migrate) | High (6 config, 12 relations) |
| [indico-operator](https://github.com/canonical/indico-operator) | `>=2.0.0,<3.0.0` (blocks 3.x) | Events Platform | 3/7 | No (candidate to add) | Medium (8 config, 11 relations, 3 actions) |
| [traefik-k8s-operator](https://github.com/canonical/traefik-k8s-operator) | `>=2.10.0` (loose, verify lock) | Networking / Ingress | 31/17 | Yes (charm + workload tracing) | High (13 relations, 2 actions) |

**Backup**: if traefik-k8s already resolves to ops 3.x in its lock file, substitute [wordpress-k8s-operator](https://github.com/canonical/wordpress-k8s-operator) (`ops==3.5.1`, IS DevOps, 4/12 tests, no tracing).

Selection rationale:
* **All on ops 2.x** with significant upgrade room to 3.6.0
* **None use new ops features** (load_config, load_params, relation.save/load), maximising the upgrade surface
* **Domain diversity**: web apps, observability (×2), events, networking
* **Tracing mix**: 2 without (candidates to add), 3 with existing library-based tracing (candidates to migrate)
* **Complexity mix**: 2 medium, 3 high
* **All published** on Charmhub and in the canonical/operator published charms CI
* **All actively maintained** with commits within the last 1-3 months

(I provided the rationale (except the ops version, for some reason Claude added that), and let Claude do the selection, as that seemed most fair, although there does seem to be a tendency towards picking certain charms.)

## Phase 5: Evaluation

### Experimental Design

For each target charm × each applicable change (or set of changes), run four conditions:

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

## Results (Phase 5)

Phase 5 was run using GitHub Copilot CLI (claude-sonnet-4.6) in non-interactive mode. 21 runs across 3 charms (CHARM_A, CHARM_B, and CHARM_C), 3 features, and 4 conditions. Of the five charms shortlisted in Phase 4, CHARM_D and CHARM_E were excluded from the evaluation because their upgrade paths were blocked by unresolved CI/test issues at the time of running Phase 5. Full results in [results/results.md](results/results.md) and [results/evaluation.md](results/evaluation.md).

### Headline Numbers

| Condition | Mean Score (/25) | N |
|-----------|:---:|:---:|
| C1pf (per-feature skill) | 21.04 | 6 |
| C2 (simple prompt) | 18.43 | 8 |
| C3 (exemplar) | 20.44 | 4 |
| C1s (single upgrade skill) | 22.00 | 2 |
| C4 (generic release-notes) | 21.17 | 3 |

### Key Findings

1. **Skills prevent scope errors.** The biggest quality gap was in relation-data-classes, where the skill's instruction to "only convert charm-owned data" prevented catastrophic mistakes (C1pf: 21.25 avg vs C2: 10.25 avg). For simpler features, the simple prompt was competitive.

2. **Exemplars are a double-edged sword.** C3 produced the single best result in the experiment (alertmanager relation-data, 23.5/25 — a backwards-compatible decoder inspired by the exemplar) but also poor results when the exemplar had gaps (discourse action-classes, 19.0/25 — missing `errors="fail"`).

3. **The generic prompt works but is unreliable.** discourse C4 scored 23.5/25 (finding nearly everything), but indico C4 scored 19.0/25 (fixating on cosmetic namespace migration, missing config-classes and action-classes entirely).

4. **Relation-data-classes is the hardest feature for AI** (mean 17.30/25) because it requires understanding ownership boundaries between charm code and charm libraries. Config-classes and action-classes are much more mechanical.

5. **The Harness staleness problem is universal.** 5 of 9 config-classes runs hit the same issue: storing config in `__init__` breaks Harness tests. All eventually self-corrected, but it consumed significant agent time.

6. **A single comprehensive skill is the best practical approach** (mean 22.00), supplemented by per-feature skills for complex features like relation-data-classes.

## Emerging Findings

### Poor feature adoption limits exemplar-based approaches

Phase 2 (exemplar search) revealed that many ops features introduced in the past year have very low adoption across the charm ecosystem:

| Feature | Version | Exemplar charms found |
|---------|---------|-----------------------|
| `load_config()` | 2.23.0 | ~5 (all Pydantic, mostly newer charms) |
| `load_params()` | 2.23.0 | ~2 production charms + official examples |
| `Relation.save()`/`.load()` | 2.23.0 | ~5 (all Pydantic, mostly in charm libraries) |
| `layer_from_rockcraft()` | 2.23.0 | **0** (only in ops' own tests/docs) |
| `SCENARIO_BARE_CHARM_ERRORS` | 3.5.0 | **0** (only in ops' own tests) |
| `JujuContext.from_environ()` | 3.3.0 | 1 (blackbox-exporter-operator) |
| `Context(app_name=, unit_id=)` | 3.1.0 | ~5 (most adopted of the testing features) |

This has two implications for the experiment:

1. **Condition 3 (simple prompt + exemplar) may be untestable** for some features, because there are no good exemplars to point the agent at.
2. **The "generic release-notes prompt" (Condition 4) is testing a realistic scenario** -- in practice, most charms *haven't* adopted these features, so any upgrade process would be starting from scratch. Charm Tech could work to make this better, by more regularly opening PRs post-release, for upstream adoption.

### Recommendation: exemplar PRs as part of the release process

If we (Charm Tech) want AI-assisted upgrades to work well, we should significantly improve the ecosystem by **opening exemplar PRs with each ops release** -- one per significant feature, against a well-known charm (e.g. one of the published charms used in CI). These PRs would serve as:

- **Gold standard references** for AI agents (and humans) to learn the intended usage pattern
- **Adoption catalysts** -- a merged PR is a real-world example that shows up in GitHub search
- **Additional Validation** that the feature works in practice, not just in the ops test suite and simple charms we used in development
- **Documentation supplements** -- a diff showing before/after in a real charm is often clearer than API docs

Even 2-3 exemplar PRs per release would dramatically improve the quality of both AI-assisted and human-driven feature adoption. Without them, the "prompt + exemplar" approach degrades to "prompt + official docs", which is a weaker signal.

(We've really had this goal already for some time, and we do it -- but infrequently. Perhaps it should really be part of the definition of done for most or all features, or at least all features that are done through roadmap planning?)

## Notes

* All runs use GitHub Copilot to align with Canonical's current tooling focus.
* Skills could be designed to be upstreamed to [copilot-collections](https://github.com/canonical/copilot-collections) if they prove useful. Alternatively, perhaps the `charmcraft` profiles should have some instructions and skills (there's an existing ticket suggesting that), or perhaps Charm Tech should have a storage location itself?
* The "simple prompt" condition is intentionally minimal -- the question is whether the model's existing knowledge plus a feature name is sufficient, not whether a carefully crafted prompt can match a skill.
