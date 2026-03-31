# Ops Upgrade: AI-Assisted Charm Modernisation

In this experiment, I explored whether AI can reliably upgrade charms to use newer ops features -- the kind of maintenance work that's important but rarely urgent enough to actually happen (and that we see happen very slowly in charming). Tools like [pyupgrade](https://github.com/asottile/pyupgrade) and [django-upgrade](https://github.com/adamchainz/django-upgrade) solve this for Python itself, but ops changes are too semantic for AST transforms. You often need to understand *why* a charm should use a new feature, not just *how* the API changed. That felt like a potential fit for AI.

In addition, I also wanted to know whether investing in detailed upgrade skills actually pays off, or whether a simple "hey, there's a new feature, go use it" (or even "there's a new release, go look at the features") prompt is good enough.

(All evaluation runs used GitHub Copilot rather than Claude Code, since that's where Canonical is currently focused. Claude helped with the design and analysis side.)

## Goals

* **Catalogue** the significant changes in `ops`, `ops-scenario`, and `ops-tracing` over the past year (this seemed somewhat interesting in itself).
* **Build skills** -- structured guides that walk an AI agent through each upgrade.
* **Find exemplar charms** already using each feature, to serve as reference material.
* **Compare four approaches** to AI-assisted upgrading, from detailed skills down to a bare "read the release notes" prompt.
* **Answer the practical question**: can a generic, zero-effort prompt match a curated skill?
* **Use a moderately scientific approach**: rather than just try something on a charm or two as with most of the earlier experiments, build up a proper test methodology.

## Setup

I catalogued changes across `ops`, `ops[testing]`, and `ops[tracing]`, then built skills in two flavours: one per feature and a single comprehensive "upgrade ops" skill. Phase 5 ran 21 evaluation runs across 3 charms (discourse-k8s, alertmanager-k8s, loki-k8s), 3 features, and 4 conditions using Copilot CLI (claude-sonnet-4.6) in non-interactive mode. The remaining two target charms (indico and traefik-k8s) were kept for follow-up and exploratory runs and were not included in the 21 scored Phase 5 evaluations.

### The Four Conditions

| Condition | What the agent gets |
|-----------|-------------------|
| **C1pf** (per-feature skill) | Structured skill with context, examples, step-by-step guidance |
| **C2** (simple prompt) | Just the feature name and "learn how to use it" |
| **C3** (exemplar) | Simple prompt + pointer to a charm already using the feature |
| **C4** (generic release-notes) | "Read the release notes and upgrade" -- zero per-release effort |

The single comprehensive skill (C1s) was also tested but with fewer runs.

### Target Charms

| Charm | Ops Version | Domain | Complexity |
|-------|-------------|--------|------------|
| [discourse-k8s](https://github.com/canonical/discourse-k8s-operator) | 2.23.2 (hard-pinned) | Web Apps | Medium |
| [alertmanager-k8s](https://github.com/canonical/alertmanager-k8s-operator) | 2.21.1 | Observability | High |
| [loki-k8s](https://github.com/canonical/loki-k8s-operator) | 2.21.1 | Observability | High |
| [indico](https://github.com/canonical/indico-operator) | >=2.0.0,<3.0.0 | Events Platform | Medium |
| [traefik-k8s](https://github.com/canonical/traefik-k8s-operator) | >=2.10.0 | Networking | High |

All with ops 2.x in their supported range and significant upgrade room, none using the newer features, and a mix of domains and complexity levels.

(I provided the selection rationale and let Claude do the picking, which seemed fairest, although there does seem to be a tendency towards certain charms.)

## Results

Full results are in [results/results.md](results/results.md) and [results/evaluation.md](results/evaluation.md). The detailed experimental design, phase descriptions, and methodology are in [WRITE-UP.md](WRITE-UP.md).

### Headline Numbers

| Condition | Mean Score (/25) | N |
|-----------|:---:|:---:|
| C1s (single upgrade skill) | 22.00 | 2 |
| C4 (generic release-notes) | 21.17 | 3 |
| C1pf (per-feature skill) | 21.04 | 6 |
| C3 (exemplar) | 20.44 | 4 |
| C2 (simple prompt) | 18.43 | 8 |

### What I Found

**Skills prevent some mistakes.** The biggest quality gap showed up with relation-data-classes, where the skill's instruction to "only convert charm-owned data" prevented scope errors. The per-feature skill averaged 21.25 there versus the simple prompt's 10.25. For simpler, more mechanical features, the simple prompt was competitive.

**Exemplars are a double-edged sword.** The exemplar condition produced both the single best result in the entire experiment (alertmanager relation-data, 23.5/25 -- the agent created a backwards-compatible decoder inspired by the exemplar) *and* poor results when the exemplar had gaps (discourse action-classes, 19.0/25 -- missing `errors="fail"`).

**The generic prompt works but is unreliable.** The discourse C4 run scored 23.5/25, finding nearly everything with zero upfront effort. But the indico C4 run scored 19.0/25, fixating on cosmetic namespace migration while missing config-classes and action-classes entirely. When it works, it's brilliant; when it doesn't, you don't know until you review the output.

**Relation-data-classes is the hardest feature for AI** (mean 17.30/25). It requires understanding ownership boundaries between charm code and charm libraries -- the kind of semantic understanding that models still struggle with. Config-classes and action-classes are much more mechanical and consistently done well.

**Charms still using Harness is a problem.** 5 of 9 config-classes runs hit the same issue: storing config in `__init__` breaks Harness tests. All eventually self-corrected, but it consumed significant agent time.

### The Practical Recommendation

A single comprehensive skill is the best overall approach (mean 22.00), supplemented by per-feature skills for genuinely complex features like relation-data-classes. The generic release-notes prompt is surprisingly competitive and costs nothing to maintain -- worth using as a first pass, with targeted skills for the hard bits.

## Emerging Findings

### Poor Feature Adoption Limits Exemplar-Based Approaches

Phase 2 revealed (well, "confirmed" is probably more accurate) that many recent `ops` features have very low adoption:

| Feature | Exemplar Charms Found |
|---------|-----------------------|
| `load_config()` | ~5 (all Pydantic, mostly newer charms) |
| `load_params()` | ~2 production charms |
| `Relation.save()`/`.load()` | ~5 (all Pydantic, mostly in charm libraries) |
| `layer_from_rockcraft()` | **0** (only in ops' own tests/docs) |

This has a practical implication: the "simple prompt + exemplar" approach is untestable for some features because there are no good exemplars to point the agent at.

### Recommendation: Exemplar PRs as Part of the Release Process

If we want AI-assisted upgrades to work well (and human-driven ones, for that matter), we should be **opening exemplar PRs with each ops release** -- one per significant feature, against a well-known charm. These serve as gold standard references for AI and humans alike, adoption catalysts, additional validation, and documentation supplements.

Even 2-3 exemplar PRs per release would dramatically improve the quality of both AI-assisted and human-driven feature adoption.

(We've had this goal for some time, and we do it -- but infrequently. Perhaps it should really be part of the definition of done for most or all features?)

## Notes

* All runs used GitHub Copilot to align with Canonical's current tooling focus.
* Skills could be upstreamed to [copilot-collections](https://github.com/canonical/copilot-collections), or perhaps the `charmcraft` profiles should include them, or Charm Tech should have its own storage location.
* The "simple prompt" condition is intentionally minimal -- the question is whether the model's existing knowledge plus a feature name is sufficient, not whether a carefully crafted prompt can match a skill.

## Files of Interest

* [WRITE-UP.md](WRITE-UP.md) -- Full experimental design, methodology, and phase-by-phase details
* [results/results.md](results/results.md) -- Quantitative results
* [results/evaluation.md](results/evaluation.md) -- Detailed per-run evaluation
