# Round 2 Results: Ops Upgrade Experiment

## Experiment Parameters

- **Dates**: 2026-03-15 to 2026-04-03
- **Tool**: GitHub Copilot CLI (non-interactive, `--autopilot`)
- **Model**: claude-sonnet-4.6 (same as round 1)
- **Max continues**: 25
- **Per-run timeout**: 15 minutes
- **Planned runs**: 67
- **Runs with changes**: 28 (42%)
- **Timeouts with no changes**: 33 (49%)
- **Correct no-ops**: 2 (3%)
- **Diff capture failure**: 1 (1.5%)
- **Missing**: 1 (indico C1s not executed)
- **C4 scored in round 1 only**: 2 (alertmanager, discourse C4 with `__all__` from round 1)

## The Timeout Problem

The most striking round 2 finding is the **49% timeout rate** — 33 of 67 runs produced zero changes within 15 minutes. This is dramatically worse than round 1 (0% timeouts, all 21 runs completed with changes).

### Timeout distribution

| Category | Runs | Timed out | Rate |
|----------|:----:|:---------:|:----:|
| set-ports (C1pf/C2/C3) | 9 | 0 | 0% |
| set-ports (C4) | 3 | 2 | 67% |
| ops-tracing (alertmanager/loki) | 8 | 0* | 0% |
| ops-tracing (tempo/traefik) | 8 | **8** | **100%** |
| pebble-check-events (content-cache/wordpress) | 8 | 2 | 25% |
| pebble-check-events (discourse/indico) | 8 | **8** | **100%** |
| action-testing | 4 | 0 | 0% |
| ops-testing-migration | 4 | **4** | **100%** |
| Holistic C1s | 5 | 2 | 40% |
| Holistic C4 | 10 | 8† | 80% |

*Loki C1pf completed but diff not captured. †Excludes round 1 scores for alertmanager/discourse.

**Entire charms where the agent failed to produce any changes:**
- **tempo-k8s**: 0/5 runs produced changes (4 ops-tracing + 1 C4)
- **traefik-k8s**: 0/5 runs produced changes
- **discourse-k8s** (round 2 features only): 0/6 runs produced changes (4 pebble-check-events + C1s + C4)
- **indico** (round 2 features only): 0/6 runs produced changes (4 pebble-check-events + action-testing correct no-ops are separate)

### Why so many timeouts?

Analysis of the output logs for timed-out runs reveals three patterns:

1. **Scope paralysis** (C4 runs): the generic prompt triggers extensive release note reading, web fetching, and source exploration. The agent spends the full 15 minutes researching without committing to any changes.

2. **Environment complexity** (tempo, traefik, discourse): these charms have complex dependency trees, multiple charm libraries, and intricate test setups. The agent spent time trying to install dependencies or run tests and never reached the code change phase.

3. **Feature difficulty** (ops-testing-migration): the Harness → Scenario paradigm shift is too complex for a 15-minute window. All 4 runs timed out, confirming round 1's finding about this being the hardest category.

## Quantitative Results

### Per-Feature Runs

| Charm | Feature | Condition | Correct. (30%) | Complete. (25%) | Quality (15%) | Min Diff (15%) | Review (15%) | **Composite (/25)** |
|-------|---------|-----------|:-:|:-:|:-:|:-:|:-:|:-:|
| alertmanager | set-ports | C1pf (skill) | 5 | 5 | 4 | 5 | 5 | **24.25** |
| alertmanager | set-ports | C2 (simple) | 5 | 5 | 5 | 5 | 5 | **25.00** |
| alertmanager | set-ports | C3 (exemplar) | 5 | 5 | 4 | 4 | 5 | **23.50** |
| alertmanager | set-ports | C4 (generic) | — | — | — | — | — | **N/S** |
| grafana | set-ports | C1pf (skill) | 5 | 5 | 4 | 5 | 5 | **24.25** |
| grafana | set-ports | C2 (simple) | 5 | 5 | 5 | 5 | 5 | **25.00** |
| grafana | set-ports | C3 (exemplar) | 5 | 5 | 3 | 5 | 4 | **22.75** |
| grafana | set-ports | C4 (generic) | — | — | — | — | — | **N/S** |
| zinc | set-ports | C1pf (skill) | 5 | 5 | 4 | 5 | 5 | **24.25** |
| zinc | set-ports | C2 (simple) | 5 | 5 | 5 | 5 | 5 | **25.00** |
| zinc | set-ports | C3 (exemplar) | 5 | 5 | 5 | 5 | 5 | **25.00** |
| zinc | set-ports | C4 (generic) | 4 | 1 | 3 | 2 | 2 | **12.50** |
| alertmanager | ops-tracing | C1pf (skill) | 5 | 5 | 4 | 3 | 4 | **22.00** |
| alertmanager | ops-tracing | C2 (simple) | 5 | 4 | 5 | 5 | 4 | **23.00** |
| alertmanager | ops-tracing | C3 (exemplar) | 5 | 3 | 4 | 5 | 3 | **20.25** |
| alertmanager | ops-tracing | C4 (generic) | 5 | 5 | 4 | 3 | 4 | **22.00** |
| loki | ops-tracing | C1pf (skill) | — | — | — | — | — | **N/S** |
| loki | ops-tracing | C2 (simple) | 5 | 4 | 5 | 5 | 4 | **23.00** |
| loki | ops-tracing | C3 (exemplar) | 3 | 5 | 3 | 5 | 2 | **18.25** |
| loki | ops-tracing | C4 (generic) | 4 | 4 | 4 | 2 | 3 | **17.75** |
| content-cache | pebble-chk | C1pf (skill) | 4 | 4 | 4 | 5 | 4 | **20.75** |
| content-cache | pebble-chk | C2 (simple) | 4 | 4 | 4 | 4 | 4 | **20.00** |
| content-cache | pebble-chk | C3 (exemplar) | 4 | 2 | 3 | 5 | 2 | **16.00** |
| content-cache | pebble-chk | C4 (generic) | — | — | — | — | — | **N/S** |
| wordpress | pebble-chk | C1pf (skill) | 5 | 5 | 5 | 5 | 4 | **24.25** |
| wordpress | pebble-chk | C2 (simple) | 4 | 5 | 4 | 4 | 4 | **21.25** |
| wordpress | pebble-chk | C3 (exemplar) | 4 | 2 | 4 | 5 | 2 | **16.75** |
| wordpress | pebble-chk | C4 (generic) | — | — | — | — | — | **N/S** |
| wordpress | action-test | C1pf (skill) | 5 | 5 | 5 | 5 | 5 | **25.00** |
| wordpress | action-test | C2 (simple) | 5 | 5 | 5 | 4 | 4 | **23.50** |

### Holistic Runs

| Charm | Condition | Correct. (30%) | Complete. (25%) | Quality (15%) | Min Diff (15%) | Review (15%) | **Composite (/25)** |
|-------|-----------|:-:|:-:|:-:|:-:|:-:|:-:|
| content-cache | C1s (single skill) | 5 | 4 | 5 | 5 | 4 | **23.00** |
| wordpress | C1s (single skill) | 5 | 4 | 4 | 2 | 3 | **19.25** |
| wordpress | C4 (generic) | 5 | 1 | 4 | 5 | 2 | **17.00** |
| zinc | C4 (generic) | 5 | 2 | 4 | 3 | 3 | **17.50** |

## Aggregate Analysis

### By Condition (scored runs only)

| Condition | Mean Score | N | Round 1 Mean | Δ |
|-----------|:---------:|:-:|:---:|:---:|
| C1pf (per-feature skill) | **23.47** | 8 | 21.04 | +2.43 |
| C2 (simple prompt) | **23.22** | 8 | 18.43 | +4.79 |
| C3 (exemplar) | **20.72** | 7 | 20.44 | +0.28 |
| C4 (generic prompt) | **17.57** | 4* | 21.17 | −3.60 |
| C1s (single skill) | **21.13** | 2 | 22.00 | −0.87 |

*C4 per-feature only; excludes holistic C4 timeouts (shown in holistic table).

**Caution**: these means are computed only over runs that produced changes. The high timeout rate (especially for C4, where 10 of 13 per-feature runs timed out) severely biases the averages upward — the "scored" C4 runs are survivors.

### By Feature (mean composite score, scored runs only)

| Feature | Mean Score | N Scored | N Timeout | Completion Rate |
|---------|:---------:|:-:|:-:|:-:|
| set-ports | **23.68** | 10 | 2 | 83% |
| action-testing | **24.25** | 2 | 0 | 100%* |
| ops-tracing | **21.04** | 7 | 9 | 44% |
| pebble-check-events | **20.50** | 6 | 10 | 38% |
| ops-testing-migration | — | 0 | 4 | 0% |
| holistic (C1s + C4) | **19.19** | 4 | 12 | 25% |

*Excluding indico's correct no-ops.

### By Charm (mean composite score, scored runs only)

| Charm | Mean Score | N Scored | N Total | Completion Rate |
|-------|:---------:|:-:|:-:|:-:|
| zinc-k8s | **22.96** | 5 | 6 | 83% |
| alertmanager-k8s | **22.91** | 7 | 12 | 58% |
| wordpress-k8s | **21.28** | 8 | 14 | 57% |
| grafana-k8s | **24.00** | 3 | 5 | 60% |
| content-cache-k8s | **19.94** | 4 | 8 | 50% |
| loki-k8s | **19.67** | 3 | 5 | 60% |
| tempo-k8s | — | 0 | 5 | **0%** |
| traefik-k8s | — | 0 | 5 | **0%** |
| discourse-k8s (R2 only) | — | 0 | 6 | **0%** |
| indico (R2 only) | — | 0 | 6† | **0%** |

†Excluding action-testing correct no-ops.

## Key Findings

### RQ7: Does feature age affect AI upgrade quality?

**Yes — older, simpler features get near-perfect scores.** Set-ports (ops 2.7.0, September 2023) achieved a mean of 23.68/25, the highest of any feature in either round. Action-testing (ops 2.9.0) scored 24.25/25. Both are 2+ years old with extensive documentation and training data.

However, age alone doesn't explain the difference. Set-ports and action-testing are also **mechanically simple** — direct API substitution with clear before/after patterns. The newer ops-tracing (2.21.0, June 2025) is a more complex migration (library removal, relation changes, dependency updates) and scored lower (21.04).

**Verdict**: feature age correlates with quality, but feature complexity is the stronger predictor.

### RQ8: Does charm complexity affect upgrade quality?

**Yes, dramatically — but through timeouts rather than quality degradation.** When the agent successfully made changes, quality was consistent regardless of charm complexity. But complex charms were far more likely to time out:

| Complexity | Examples | Completion Rate | Mean Score (when scored) |
|------------|---------|:-:|:-:|
| Simple | zinc-k8s | 83% | 22.96 |
| Moderate | alertmanager-k8s, grafana-k8s | 58-60% | 22.91-24.00 |
| Complex | tempo-k8s, traefik-k8s | **0%** | — |

Complex charms (tempo, traefik) have intricate dependency trees, multiple charm libraries, and layered test infrastructure that consumed the agent's entire time budget before any changes could be made.

### RQ9: How does AI handle paradigm-shift migrations?

**It cannot — within a 15-minute window.** All 4 ops-testing-migration runs (Harness → Scenario) timed out with no changes. This confirms and strengthens the round 1 finding that paradigm shifts require fundamentally different treatment: either longer sessions, pre-migration scaffolding, or a different approach entirely (perhaps interactive rather than autonomous).

### RQ10: Does team/codebase style affect upgrade quality?

**Codebase structure matters more than team style.** The Observability team's charms (alertmanager, grafana, loki) scored well when they completed, but tempo and traefik (also Observability) failed entirely. IS DevOps charms (discourse, indico) failed on round 2 features but succeeded on round 1 features. The community charm (zinc) had the highest completion rate.

The real differentiator is **codebase complexity**, not team style. Charms with simpler dependency trees and fewer charm libraries completed reliably. The agent's ability to navigate `lib/charms/*/` directories and understand which libraries to modify vs. leave alone was the key challenge.

### RQ11: Can AI identify and add reactive patterns?

**Partially.** Pebble-check-events tests whether the AI can add new event handlers for existing health checks. Results were mixed:

- **wordpress C1pf** (24.25/25): excellent — added handlers with reconciliation-based recovery, demonstrating genuine understanding of the charm's architecture
- **content-cache C1pf/C2** (20.0-20.75): adequate — handlers work but use naive status management
- **C3 runs** (16.0-16.75): poor — copied the exemplar's log-only pattern, providing minimal operational value
- **discourse/indico**: failed entirely (all timeouts)

The skill (C1pf) provided crucial guidance on status management and reconciliation. Without it, the agent either copied the exemplar's minimal pattern (C3) or invented a reasonable but imperfect approach (C2).

### Cross-Round Comparison

| Metric | Round 1 | Round 2 |
|--------|:-------:|:-------:|
| Runs | 21 | 67 |
| Completion rate | 100% | 42% |
| Mean score (scored runs) | 20.52 | 21.55 |
| Per-feature skill (C1pf) | 21.04 | 23.47 |
| Simple prompt (C2) | 18.43 | 23.22 |
| Exemplar (C3) | 20.44 | 20.72 |
| Single skill (C1s) | 22.00 | 21.13 |
| Generic prompt (C4) | 21.17 | 17.57* |

*Per-feature C4 only; 10 of 13 timed out.

**When the agent completes, quality is higher in round 2** — likely because the features are older and more mechanical. But the completion rate collapse (100% → 42%) means the overall utility is much lower. A tool that produces excellent output 42% of the time and nothing 49% of the time is less useful than one that produces good output 100% of the time.

## Condition Ranking (Revised)

Combining round 1 and round 2 results:

| Condition | Best For | Worst For | Recommendation |
|-----------|----------|-----------|----------------|
| **C1pf** (per-feature skill) | Complex features requiring guardrails (pebble-check-events, ops-tracing) | Simple mechanical changes (overkill) | Use for features requiring architectural judgement |
| **C2** (simple prompt) | Simple mechanical changes (set-ports, action-testing) | Complex features with ownership boundaries | Use for well-documented, mechanical API changes |
| **C3** (exemplar) | Features where the exemplar is excellent | Features where the exemplar has gaps (pebble-check-events) | Vet exemplars carefully; only use when exemplar is known-excellent |
| **C4** (generic prompt) | Nothing — too high a timeout rate | Everything in round 2 | Not recommended as primary approach |
| **C1s** (single skill) | Multi-feature upgrades on moderate charms | Complex charms that cause timeouts | Best practical choice for production upgrade tooling |

## Recurring Patterns

### The C3 Exemplar Trap (Strengthened)

Round 1 found exemplars are a "double-edged sword." Round 2 confirms and sharpens this:

- **set-ports C3**: sometimes made questionable style choices (inlining methods, unreadable one-liners) influenced by the minio exemplar
- **ops-tracing C3**: left dead library code (alertmanager) or renamed a relation breaking backwards compatibility (loki)
- **pebble-check-events C3**: copied the kratos exemplar's log-only pattern both times, producing the lowest-scoring runs

The pebble-check-events case is the strongest evidence. The kratos exemplar is technically correct but uses a minimal log-only pattern. Both C3 runs faithfully copied this pattern, producing handlers that add almost no operational value. The skill (C1pf) and simple prompt (C2) both produced better results because they weren't anchored to a specific implementation.

**Revised recommendation**: exemplars should only be used when they are **known to represent best practice**, not just "a charm that uses the feature." Three out of four exemplar features in round 2 had this problem.

### The Skill File Leak

Two C1pf/C1s runs left the `.github/copilot-instructions.md` skill file in the repository. This inflated their diffs (+175 and +386 lines) and would need to be removed before merging. The evaluation script should clean up this file post-run.

### Lockfile Churn

Several runs regenerated `uv.lock` (up to 1319 lines of changes), creating massive diffs that obscure the actual code changes. C2 runs consistently failed to update the lockfile at all. Neither extreme is ideal.

## Timing

| Condition | Mean Duration (s) | Min | Max | Timeouts |
|-----------|:-:|:-:|:-:|:-:|
| C1pf (per-feature skill) | 581 | 97 | 1500 | 4/12 |
| C2 (simple prompt) | 543 | 160 | 1501 | 4/12 |
| C3 (exemplar) | 526 | 155 | 1501 | 4/10 |
| C4 (per-feature) | 901 | 333 | 1501 | 10/12 |
| C1s (single skill) | 794 | 585 | 902 | 2/5 |
| C4 (holistic) | 869 | 380 | 901 | 8/10 |

Set-ports and action-testing were consistently the fastest to complete, reflecting their mechanical simplicity.
