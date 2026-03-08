# Results

## Overview

**22 Copilot migration experiments** in total:
- **12 runs** on saml-integrator-operator (6 levels x 2 models) — the full comparison matrix
- **5 runs** on s3-integrator (L1, L3, L5, L6 with Sonnet; L1 with Opus) — medium complexity confirmation
- **5 runs** on diverse charms (L3 with Sonnet) — the broader sample for example PRs

All runs used GitHub Copilot CLI v0.0.411. Charms were pinned to specific commits for reproducibility.

Note that there was some earlier experimentation not covered in the above, but this is what the *systematic* evaluation included.

## Full Matrix: saml-integrator-operator

A simple charm with 2 integration tests, 1 conftest, and no helper files. Ideal for isolating the effect of assistance level and model choice.

### Scores

| Level | Sonnet 4.6 | Opus 4.6 | Delta |
|-------|:----------:|:--------:|:-----:|
| L1: Bare prompt | **24** | 20 | +4 |
| L2: + Docs pointer | 17 | 17 | 0 |
| L3: + Source inspection | **25** | 18 | +7 |
| L4: + Example charm | **24** | 18 | +6 |
| L5: Detailed recipe | 18 | 12 | +6 |
| L6: Recipe + example | 22 | 14 | +8 |
| **Average** | **21.7** | **16.5** | **+5.2** |

### Timing

| Level | Sonnet Time | Opus Time |
|-------|:-----------:|:---------:|
| L1: Bare prompt | 3m 25s | 3m 37s |
| L2: + Docs pointer | 2m 50s | 2m 34s |
| L3: + Source inspection | 5m 20s | 3m 49s |
| L4: + Example charm | 10m 09s | 7m 38s |
| L5: Detailed recipe | 3m 29s | 4m 30s |
| L6: Recipe + example | 6m 20s | 5m 05s |

### Analysis by Level

#### Level 1: Bare Prompt (Sonnet: 24/25)

Perhaps surprisingly strong. Sonnet proactively searched the web for Jubilant documentation and the migration guide, then produced a clean migration. It correctly used the built-in `juju` fixture from `pytest-jubilant` and generated minimal, focused changes.

**What it got right:** All API calls correct, proper fixture design, minimal diff.
**What it missed:** Did not use `pack()` for charm building (retained `--charm-file` option). This is arguable, since the Ops and Jubilant docs don't currently recommend `pytest-jubilant`, but it is the direction we are heading. I suspect after the forthcoming updates to `pytest-jubilant` this will improve, although it is unclear how long it would take for models to adjust.

#### Level 2: Docs Pointer (Sonnet: 17/25)

Paradoxically, pointing to the docs produced *worse* results than the bare prompt. Both models read the migration guide and then created their own `juju` fixture using `temp_model()` instead of relying on pytest-jubilant's built-in fixture (again, understandable at the moment). They also added `--keep-models` infrastructure manually.

**Likely explanation:** The Jubilant docs describe the low-level API (`temp_model`, etc.) without emphasising `pytest-jubilant`'s higher-level fixtures. The models followed the docs too literally.

#### Level 3: Source Inspection (Sonnet: 25/25 — Perfect)

The best result. By reading the actual source code of `jubilant` and `pytest-jubilant`, Sonnet understood both the low-level API and the pytest fixtures. It correctly used `pack()`, the built-in `juju` fixture, and produced the cleanest possible migration.

**Why it works:** Source code provides up-to-date, accurate, detailed API data. The model can see exactly what parameters exist, what fixtures are available, and how they interact. Minimal hallucination risk.

#### Level 4: Example Charm (Sonnet: 24/25)

Nearly as good as L3. Studying the `wordpress-k8s-operator` tests gave the model a working template to follow. It correctly used `pack()` and the built-in fixtures, and added some nice touches (extracting config constants).

Given further time, an interesting extension would be providing different examples, and/or multiple examples, and seeing how much improvement that makes.

**Trade-off:** Took the longest (10 minutes) because it had to clone and study a separate repository.

#### Level 5: Detailed Recipe (Sonnet: 18/25)

The recipe introduced issues that didn't exist in simpler approaches:
- Hallucinated `successes=3` parameter in `juju.wait()` (copied from recipe examples which were slightly wrong)
- Created `.agent/state/jubilant-migration.md` files (recipe feature, but shouldn't be committed)
- Used `@pytest.mark.setup` marker (from the recipe, but non-standard)
- Opus literally stopped at the first "STOP and wait for user input" instruction in non-interactive mode

In hindsight, perhaps I should have tested this and also a recipe that I created myself (particularly one more to my taste).

**Key insight:** A recipe designed for interactive human-supervised use doesn't work well in autonomous mode.

#### Level 6: Recipe + Example (Sonnet: 22/25)

Better than recipe alone thanks to the example, but still carried recipe-specific issues (state files, `successes` parameter). The example helped ground some of the recipe's patterns in reality.

### Model Comparison

**Sonnet 4.6 outperformed Opus 4.6 in every single comparison.** Average scores:
- Sonnet: 21.7/25 (range: 17-25)
- Opus: 16.5/25 (range: 12-20)

Opus consistently exhibited these issues:
1. **Over-engineering**: Added logging, CHARM_PATH env vars, renamed fixtures, redundant assertions
2. **Unnecessary lambda wrapping**: `lambda status: jubilant.all_active(status, app)` instead of just `jubilant.all_active`
3. **Shadowing built-in fixtures**: Created custom `juju` fixtures with `temp_model()` instead of using pytest-jubilant's
4. **Redundant assertions**: Added `assert status.apps[app].units[...].is_active` after `juju.wait(all_active)`
5. **Structural changes**: In L5, moved deployment from conftest fixtures to test functions

This is interesting because Opus is generally considered the more capable model, and so probably one that a charmer would naturally reach for. For this specific task — a well-defined mechanical migration — Sonnet's tendency toward simpler, more direct solutions was actually an advantage.

## Medium Complexity: s3-integrator

A charm with 5 test functions, a helpers.py with 10 functions, and custom action/relation helpers. Tests the model's ability to handle non-trivial patterns.

| Run | Score | Time | Notes |
|-----|:-----:|:----:|-------|
| L1-bare-sonnet | 22 | 12m 34s | Good overall; created custom juju fixture with temp_model() |
| L1-bare-opus | 20 | 15m 43s | Similar to sonnet but more verbose; didn't run poetry lock |
| L3-source-sonnet | 24 | ~8m | Best result; used pack() and built-in fixtures correctly |
| L5-recipe-sonnet | 17 | 8m 09s | Hallucinated successes param; created .agent/state files |
| L6-recipe-example-sonnet | 17 | 7m 37s | Same issues as L5 |

Confirms the saml-integrator findings: L3 > L1 > L5/L6 for Sonnet.

## Broader Sample: Diverse Charms with L3 + Sonnet

All scored 21-25, confirming L3's reliability across different complexities and domains.

| Charm | Domain | Complexity | Files | Lines +/- | Time | Score |
|-------|--------|:----------:|:-----:|:---------:|:----:|:-----:|
| content-cache-k8s | Web Infra | Simple | 4 | +104/-147 | 7m | **25** |
| nginx-ingress-integrator | Networking | Medium | 5 | +220/-262 | 10m | 22 |
| indico | Web App | Complex | 7 | +149/-231 | 10m | 21 |
| loki-k8s | Observability | Large | 18 | +396/-680 | 17m | 21 |
| hockeypuck-k8s | Security | Complex | 4 | +176/-224 | 9m | 21 |

### Interesting Achievements

- **Multi-model testing** (hockeypuck): Correctly used `temp_model_factory.get_juju("secondary")` for cross-model tests
- **Large-scale migration** (loki): 18 files, -1038 net lines, completed in 17 minutes
- **Complex fixtures** (indico): Correctly migrated multi-charm deployment (PostgreSQL, Redis x2, Nginx)
- **Action migration** (all): Correctly converted `run_action().wait()` to `juju.run()` returning `Task`
- **Container SSH** (indico): Correctly used `juju.ssh(unit, cmd, container=app)`

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total experiments | 22 |
| Best approach | L3 (source inspection) + Sonnet 4.6 |
| Average score (L3 + Sonnet) | 24.0/25 |
| Worst approach | L5 (recipe) + Opus 4.6 |
| Average score (L5 + Opus) | 12.0/25 |
| Fastest run | 2m 34s (L2 + Opus, saml-integrator) |
| Slowest run | 16m 45s (L3 + Sonnet, loki-k8s — 18 files) |
| Perfect scores (25/25) | 2 (L3-source-sonnet on saml, L3-source-sonnet on content-cache) |
| Runs scoring 21+ (merge-ready) | 11 out of 22 (50%) |
| Runs scoring 21+ with L3+Sonnet | 7 out of 7 (100%) |
