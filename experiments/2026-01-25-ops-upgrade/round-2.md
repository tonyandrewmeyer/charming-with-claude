# Round 2: Expanded Scope

## Changes from Round 1

Round 1 catalogued changes from ops 2.23.0 (June 2025) through 3.6.0 (February 2026) and tested 3 charms across 3 features and 4 conditions (21 scored runs).

Round 2 makes two changes:

1. **Expanded date range**: the change catalogue now extends back to ops 2.7.0 (September 2023), adding 12 new changes spanning roughly 20 months of ops development.
2. **More target charms**: the evaluation tests against 10 charms (up from 3 scored in round 1), covering more teams, domains, and complexity levels.

Everything else — the 4 conditions, the evaluation rubric, the execution protocol — remains the same as round 1.

## New Changes Catalogued

The 12 new changes cover the period from September 2023 to May 2025. See [changes/index.md](changes/index.md) for the full catalogue. The most impactful for testing are:

| Change ID | Version | Complexity | Why it's interesting |
|-----------|---------|------------|---------------------|
| [set-ports](changes/set-ports.md) | 2.7.0 | Moderate | Mechanical transformation from imperative to declarative port management |
| [ops-tracing-adoption](changes/ops-tracing-adoption.md) | 2.21.0 | Moderate | First-party tracing adoption; charms migrating from community charm_tracing library |
| [pebble-check-events](changes/pebble-check-events.md) | 2.15.0 | Moderate | Tests whether AI can add reactive health monitoring to charms with existing Pebble checks |
| [ops-testing-migration](changes/ops-testing-migration.md) | 2.17.0 | Significant | Paradigm shift from Harness to Scenario; covered in depth by a [dedicated experiment](../2026-03-05-harness-to-scenario-migration/) |

### Features dropped after charm verification

- **non-deferrable-lifecycle** (2.11.0): catalogued and a skill was built, but **none of the 10 target charms defer lifecycle events**. This feature cannot be tested. The breaking change appears to have been addressed early in most maintained charms, or was never triggered (most charms never deferred lifecycle events in the first place).
- **pebble-notices** (2.10.0): only traefik-k8s has a marginal polling pattern (version string in update-status), and notices also require workload changes, making this impractical to test in the current format.

### Features to test in round 2

**Primary features** (test all 4 conditions: C1pf, C2, C3, C4):
1. **set-ports** — declarative port management, mechanical transformation
2. **ops-tracing-adoption** — community charm_tracing → ops[tracing] migration
3. **pebble-check-events** — adding reactive health monitoring to charms with existing Pebble checks

**Secondary features** (test C1pf and C2 only):
4. **action-testing** — modernising action tests from mock patterns to `harness.run_action()`

**Exploratory** (C1pf and C2 only, 2–3 charms):
5. **ops-testing-migration** — Harness → Scenario. Demoted from primary because a [dedicated experiment](../2026-03-05-harness-to-scenario-migration/) already studied this in depth. Round 2 adds breadth (more charms) using the existing skill from that experiment.

## Target Charms

### Confirmed charm list

All ops versions and feature applicability verified against local clones (~/charm-clones) on 2026-03-15.

| # | Charm | Ops Version | Commit | Domain | Team | Applicable features |
|---|-------|-------------|--------|--------|------|-------------------|
| 1 | [discourse-k8s](https://github.com/canonical/discourse-k8s-operator) | 2.23.2 | `74aec21` | Web Apps | IS DevOps | pebble-check-events |
| 2 | [alertmanager-k8s](https://github.com/canonical/alertmanager-k8s-operator) | 2.21.1 | `6101e73` | Observability | Observability | set-ports, ops-tracing |
| 3 | [loki-k8s](https://github.com/canonical/loki-k8s-operator) | 2.21.1 | `767ba3d` | Observability | Observability | ops-tracing |
| 4 | [indico](https://github.com/canonical/indico-operator) | <3.0.0 | `c055e37` | Events Platform | IS DevOps | pebble-check-events, action-testing |
| 5 | [traefik-k8s](https://github.com/canonical/traefik-k8s-operator) | >=2.10.0 | `759165b` | Networking | Observability | ops-tracing |
| 6 | [grafana-k8s](https://github.com/canonical/grafana-k8s-operator) | >=2.17 | `382e463` | Dashboards | Observability | set-ports |
| 7 | [tempo-k8s](https://github.com/canonical/tempo-k8s-operator) | unpinned | `16d9d06` | Tracing | Observability | ops-tracing |
| 8 | [wordpress-k8s](https://github.com/canonical/wordpress-k8s-operator) | 3.5.1 | `367d6c7` | Web Apps | IS DevOps | pebble-check-events, action-testing, ops-testing-migration |
| 9 | [content-cache-k8s](https://github.com/canonical/content-cache-k8s-operator) | 3.6.0 | `c32e9d6` | Infrastructure | IS DevOps | pebble-check-events, ops-testing-migration |
| 10 | [zinc-k8s](https://github.com/jnsgruk/zinc-k8s-operator) | 2.23.2 | `d3bb738` | Search | Community | set-ports |

### Selection notes

- **postgresql-k8s** dropped: already on ops 3.6.0 with set_ports() and ops.tracing adopted. No upgrade surface.
- **mongodb-k8s** dropped: no unit tests at all, mono-kernel architecture (thin wrapper over `single_kernel_mongo`). Not suitable for per-feature testing.
- **zinc-k8s** lives at `jnsgruk/zinc-k8s-operator`, not canonical/. Simple charm, only applicable for set-ports — provides the "simple charm" data point.
- **tempo-k8s** is interesting because it *provides* tracing (it's the Tempo charm), not just consumes it. Tests how AI handles the "wrong side" of the relation.
- Several charms (alertmanager, loki, traefik, indico, wordpress, content-cache) have **relation data access in `__init__`**, which is the databag-init-validation anti-pattern. This isn't tested as a separate feature but will be noted if the AI addresses it during C1s/C4 runs.

### Team diversity

| Team | Charms |
|------|--------|
| Observability | alertmanager-k8s, loki-k8s, traefik-k8s, grafana-k8s, tempo-k8s |
| IS DevOps | discourse-k8s, indico, wordpress-k8s, content-cache-k8s |
| Community | zinc-k8s |

Observability is over-represented (5 of 10) because that team's charms happen to be the best candidates for ops-tracing migration. IS DevOps provides balance via a different set of applicable features (pebble-check-events, action-testing).

## Experimental Design

### Feature applicability matrix

| Charm | set-ports | ops-tracing | pebble-chk-ev | action-testing | ops-test-mig | C1s | C4 |
|-------|:---------:|:-----------:|:-------------:|:--------------:|:------------:|:---:|:--:|
| discourse-k8s | | | ✓ | | | | ✓ |
| alertmanager-k8s | ✓ | ✓ | | | | ✓ | ✓ |
| loki-k8s | | ✓ | | | | | ✓ |
| indico | | | ✓ | ✓ | | ✓ | ✓ |
| traefik-k8s | | ✓ | | | | | ✓ |
| grafana-k8s | ✓ | | | | | | ✓ |
| tempo-k8s | | ✓ | | | | | ✓ |
| wordpress-k8s | | | ✓ | ✓ | ✓ | ✓ | ✓ |
| content-cache-k8s | | | ✓ | | ✓ | ✓ | ✓ |
| zinc-k8s | ✓ | | | | | | ✓ |

### Run count

**Primary features (4 conditions: C1pf, C2, C3, C4):**

| Feature | Charms | × Conditions | = Runs |
|---------|:------:|:------------:|:------:|
| set-ports | 3 | 4 | 12 |
| ops-tracing | 4 | 4 | 16 |
| pebble-check-events | 4 | 4 | 16 |
| **Subtotal** | | | **44** |

**Secondary features (2 conditions: C1pf, C2):**

| Feature | Charms | × Conditions | = Runs |
|---------|:------:|:------------:|:------:|
| action-testing | 2 | 2 | 4 |
| **Subtotal** | | | **4** |

**Exploratory (2 conditions: C1pf, C2):**

| Feature | Charms | × Conditions | = Runs |
|---------|:------:|:------------:|:------:|
| ops-testing-migration | 2 | 2 | 4 |
| **Subtotal** | | | **4** |

**All-features runs (C1s + C4):**

C1s (single upgrade skill): 5 charms with ≥2 applicable features (alertmanager, indico, wordpress, content-cache, + discourse as a single-feature baseline) = **5 runs**

C4 (generic release-notes): all 10 charms = **10 runs**

(C4 is run on every charm because it tests feature *discovery* — even charms with only one applicable feature provide data on whether the AI finds it.)

| Category | Runs |
|----------|:----:|
| Primary features | 44 |
| Secondary features | 4 |
| Exploratory | 4 |
| C1s (single skill) | 5 |
| C4 (generic prompt) | 10 |
| **Total** | **67** |

### What's different from round 1

| Aspect | Round 1 | Round 2 |
|--------|---------|---------|
| Change catalogue scope | 2.23.0–3.6.0 (9 months) | 2.7.0–2.22.0 (20 months) + round 1 |
| Charms scored | 3 | 10 |
| Features tested | 3 (config-classes, action-classes, relation-data-classes) | 5 (set-ports, ops-tracing, pebble-check-events, action-testing, ops-testing-migration) |
| Scored runs | 21 | 67 |
| Team diversity | 2 teams (IS DevOps, Observability) | 3 teams + community |
| Complexity range | Medium–High | Low–High |

### Research questions for round 2

In addition to the original 6 research questions from round 1, round 2 adds:

7. **Does feature age affect AI upgrade quality?** The round 2 features (2023–2025) have had more time to appear in training data and documentation than round 1's (2025–2026). Do older, better-documented features get applied more reliably?
8. **Does charm complexity affect upgrade quality?** Simple charms (zinc-k8s, content-cache-k8s) vs complex ones (traefik-k8s, alertmanager-k8s) — does the AI struggle more with complex codebases?
9. **How does AI handle paradigm-shift migrations?** ops-testing-migration (Harness → Scenario) is a fundamentally different kind of change from the mechanical API upgrades. Can a skill guide the AI through a paradigm shift?
10. **Does team/codebase style affect upgrade quality?** Testing across IS DevOps, Observability, and community charms reveals whether the AI's performance generalises or is sensitive to coding conventions.
11. **Can AI identify and add reactive patterns?** pebble-check-events tests whether the AI can recognise that existing Pebble checks should have event handlers, even when the charm works without them.

Note: the original question 9 ("Can AI handle breaking changes?") is dropped because no target charms have the non-deferrable-lifecycle issue.

## Skills Built

All skills have been built and are ready for use.

### Per-feature skills (C1pf condition)

| Skill | Status | Notes |
|-------|--------|-------|
| `skills/set-ports/SKILL.md` | ✅ Ready | Covers consolidation patterns, multiple-handler cases |
| `skills/ops-tracing-adoption/SKILL.md` | ✅ Ready | Both migration from charm_tracing and adding from scratch |
| `skills/pebble-check-events/SKILL.md` | ✅ Ready | Including collect-status integration pattern |
| `skills/action-testing/SKILL.md` | ✅ Ready | Harness.run_action() / ActionOutput / ActionFailed |
| `skills/ops-testing-migration/SKILL.md` | ✅ Ready | Lightweight, references dedicated experiment |
| `skills/non-deferrable-lifecycle/SKILL.md` | ✅ Built | Not testable (no applicable charms) — retained for reference |
| `skills/pebble-notices/SKILL.md` | ✅ Built | Not testable (insufficient applicable charms) — retained for reference |

### Single upgrade skill (C1s condition)

`skills/ops-upgrade/SKILL.md` — updated to cover ops 2.7.0–3.6.0, including set-ports, ops-tracing, pebble-check-events, pebble-notices, and action-testing alongside the existing round 1 content.

## Execution Plan

| Step | Description | Status |
|------|-------------|--------|
| 1 | Catalogue round 2 changes | ✅ Done (12 new changes) |
| 2 | Build per-feature skills | ✅ Done (7 skills) |
| 3 | Update single upgrade skill | ✅ Done |
| 4 | Confirm charm selection | ✅ Done (10 charms, 67 runs) |
| 5 | Find exemplars for C3 condition | **Next** |
| 6 | Run evaluation (phase 5) | Pending |
| 7 | Score and analyse | Pending |
| 8 | Update README with round 2 findings | Pending |

## Notes

- Round 2 runs will be stored in `results/` alongside round 1, following the same naming convention: `{charm}__{feature}__{condition}`.
- The same Copilot version should be used for all round 2 runs (pin it at the start and record in `experiment-metadata.json`).
- If a charm has already adopted a feature, that feature is skipped for that charm (no need to test upgrading something already upgraded).
- Local charm clones are available at `~/charm-clones/` — use these for exemplar searches and to avoid GitHub API rate limits.
