# Migrate Your Integration Tests to Jubilant in Under 20 Minutes with Copilot

We've been experimenting with using GitHub Copilot to automate the migration of charm integration tests from pytest-operator to [Jubilant](https://documentation.ubuntu.com/jubilant), and the results are surprisingly good.

## TL;DR

With a single prompt and the right model, Copilot can migrate your integration tests to jubilant in 3–17 minutes, producing code that's ready to merge with light review. We tested this on 7 charms across 5 different teams and got scores of 21–25 out of 25 on every single run.

## What We Did

We ran 22 experiments testing different strategies for AI-assisted migration:

- **6 different prompt strategies** — from a bare one-line instruction to a detailed step-by-step recipe
- **2 models** — Claude Sonnet 4.6 and Claude Opus 4.6
- **7 charms** — from simple (2 tests) to large (18 files, 1,450 lines removed)

We scored each result on correctness, completeness, code quality, minimality of changes, and how much human review would be needed.

## What We Found

**The best approach is simple:** tell the model to install jubilant and read its source code before migrating.

```bash
copilot -p "Migrate this charm's integration tests from pytest-operator \
to jubilant and pytest-jubilant. Update all test files, conftest.py, \
helpers, and dependencies.

Before starting, install jubilant and pytest-jubilant from PyPI \
(pip install jubilant pytest-jubilant) and read the source code to \
understand the API." --model claude-sonnet-4.6 --allow-all-paths --allow-all-urls
```

That's it. No detailed recipe needed. No example charm to point to. Just "read the source, then migrate."

Some surprises:

1. **Sonnet beats Opus** — for this task, every single time. Opus over-engineers; Sonnet keeps it simple.
2. **A bare prompt scores 24/25** — the model already knows enough about jubilant to do a decent job with zero guidance.
3. **Detailed recipes can hurt** — our carefully-crafted migration recipe actually scored *lower* than the bare prompt, because the model faithfully copied slightly-wrong examples from it.
4. **Pointing to docs is counterproductive** — the model reads the low-level API docs and rolls its own fixtures instead of using pytest-jubilant's built-in ones.

## Example Migrations

We prepared migrations for 5 charms across different teams:

| Charm | Complexity | Time | Score |
|-------|:----------:|:----:|:-----:|
| content-cache-k8s-operator | Simple | 7 min | 25/25 |
| nginx-ingress-integrator-operator | Medium | 10 min | 22/25 |
| indico-operator | Complex | 10 min | 21/25 |
| loki-k8s-operator | Large (18 files) | 17 min | 21/25 |
| hockeypuck-k8s-operator | Multi-model | 9 min | 21/25 |

## What to Watch For

The output is good but not perfect. When reviewing, check:

- **conftest.py**: Does it use the built-in `juju` fixture, or did it create a custom one? (Built-in is better.)
- **`juju.wait()` calls**: Watch for `successes=3` — this parameter doesn't exist.
- **Dependencies**: Make sure both `jubilant` and `pytest-jubilant` are added, and `pytest-operator` is removed.

## Full Details

The complete experiment write-up, including all 22 run transcripts, evaluation scores, methodology, and a detailed practical guide, is available at:

[charming-with-claude/experiments/2026-02-17-jubilant-migration-experiment](https://github.com/tonyandrewmeyer/charming-with-claude/tree/main/experiments/2026-02-17-jubilant-migration-experiment)

If you try this on your charm, let us know how it goes!
