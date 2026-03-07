# SAML Integrator Evaluation Results

## Scores (all 12 runs)

| Run | Correctness | Completeness | Quality | Min Diff | Review | Total /25 |
|-----|:-----------:|:------------:|:-------:|:--------:|:------:|:---------:|
| L1-bare-sonnet | 5 | 4 | 5 | 5 | 5 | **24** |
| L1-bare-opus | 4 | 4 | 4 | 4 | 4 | 20 |
| L2-docs-sonnet | 4 | 3 | 4 | 3 | 3 | 17 |
| L2-docs-opus | 4 | 3 | 4 | 3 | 3 | 17 |
| L3-source-sonnet | 5 | 5 | 5 | 5 | 5 | **25** |
| L3-source-opus | 4 | 4 | 4 | 3 | 3 | 18 |
| L4-example-sonnet | 5 | 5 | 5 | 4 | 5 | **24** |
| L4-example-opus | 4 | 4 | 4 | 3 | 3 | 18 |
| L5-recipe-sonnet | 4 | 4 | 4 | 3 | 3 | 18 |
| L5-recipe-opus | 3 | 2 | 3 | 2 | 2 | **12** |
| L6-recipe-example-sonnet | 4 | 5 | 5 | 4 | 4 | 22 |
| L6-recipe-example-opus | 3 | 3 | 4 | 2 | 2 | 14 |

## Timing

| Run | API Time | Session Time |
|-----|----------|--------------|
| L1-bare-sonnet | 2m 33s | 3m 25s |
| L1-bare-opus | 2m 34s | 3m 37s |
| L2-docs-sonnet | 2m 21s | 2m 50s |
| L2-docs-opus | 2m 39s | 2m 34s |
| L3-source-sonnet | 4m 26s | 5m 20s |
| L3-source-opus | 2m 57s | 3m 49s |
| L4-example-sonnet | 7m 39s | 10m 9s |
| L4-example-opus | 7m 41s | 7m 38s |
| L5-recipe-sonnet | 3m 12s | 3m 29s |
| L5-recipe-opus (first attempt) | 0m 39s | 0m 46s |
| L5-recipe-opus (retry) | 4m 11s | 4m 30s |
| L6-recipe-example-sonnet | 4m 43s | 6m 20s |
| L6-recipe-example-opus | 4m 56s | 5m 05s |

## Key Patterns

1. **Sonnet consistently outperforms Opus** across all levels (+4-6 points on average)
2. **L3 (source inspection) + Sonnet scored perfect 25/25** — the best result
3. **L1 (bare prompt) + Sonnet scored 24/25** — surprisingly strong baseline
4. **L4 (example) + Sonnet scored 24/25** — learning from example works well
5. **More guidance doesn't always help**: L5/L6 recipe levels scored lower than L1/L3/L4
6. **L5-recipe-opus stopped at first decision point** in non-interactive mode (recipe says "STOP and wait")
7. **Opus over-engineers**: adds logging, CHARM_PATH env vars, renames fixtures, redundant assertions
8. **Sonnet uses built-in pytest-jubilant fixtures** correctly; Opus tends to shadow them with custom temp_model()
9. **Level 2 (docs pointer) performed worst for Sonnet** — reading docs led to rolling own fixtures instead of using pytest-jubilant
10. **Recipe levels introduced hallucinated parameters**: `successes=3` in juju.wait() doesn't exist

## Common Issues by Level

- **L1/L2**: Don't use pack() from pytest-jubilant (no guidance to do so)
- **L2**: Shadows built-in juju fixture with custom temp_model()
- **L5/L6**: Hallucinate `successes` parameter; create .agent/state files that shouldn't be committed
- **L5-opus**: Major structural changes — moved deployment from conftest to test files
- **All Opus runs**: Unnecessary lambda wrapping of all_active, redundant status assertions after wait()
