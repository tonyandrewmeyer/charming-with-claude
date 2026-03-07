# Migrate Your Integration Tests to Jubilant in Under 20 Minutes with Copilot

We've been experimenting with using GitHub Copilot to automate the migration of charm integration tests from `pytest-operator` to [Jubilant](https://documentation.ubuntu.com/jubilant), and feel that the results are good enough that you should give this a go yourself. The joy of running your integration tests on Juju 4 is within (much easier) reach!

## TL;DR

With a single prompt and the right model, Copilot can migrate your integration tests to Jubilant in minutes, producing code that's ready to merge with light review. We tested this on seven charms across five different teams and got scores of 21–25 out of 25 (against our internal rubric) on every single run. Some took only three minutes, all were done in under twenty (although you'll need a bit of human time afterwards for validation, of course). This may be faster than the actual tests run -- it might be faster than bootstrapping the test environment in some cases ;).

## What We Did

We ran 22 experiments testing different strategies for AI-assisted migration:

- **6 different prompt strategies** — from a bare one-line instruction to a detailed step-by-step recipe
- **2 models** — Claude Sonnet 4.6 and Claude Opus 4.6
- **7 charms** — from simple (2 tests) to large (18 files, 1,450 lines removed)

We scored each result on correctness, completeness, code quality, minimality of changes, and how much human review would be needed.

## What We Found

**The best approach is simple:** tell the model to install Jubilant and read its source code before migrating.

```bash
copilot -p "Migrate this charm's integration tests from pytest-operator \
to jubilant and pytest-jubilant. Update all test files, conftest.py, \
helpers, and dependencies.

Before starting, install jubilant and pytest-jubilant from PyPI \
(pip install jubilant pytest-jubilant) and read the source code to \
understand the API." --model claude-sonnet-4.6 --allow-all-paths --allow-all-urls
```

That's it. No detailed recipe needed. No example charm to point to. Just "read the source, then migrate."

Some things we found interesting:

1. **Sonnet beats Opus** — for this task, every single time. Opus over-engineers; Sonnet keeps it simple.
2. **A bare prompt scores 24/25** — the model already knows enough about Jubilant to do a decent job with zero guidance. This was definitely not the case even 6 months ago.
3. **Detailed recipes can hurt** — we borrowed a carefully-crafted migration recipe, but it actually scored *lower* than the bare prompt (feel free to argue in the comments that we were unfair here).
4. **Pointing to docs is counterproductive** — the model reads the low-level API docs and rolls its own fixtures instead of using `pytest-jubilant`'s built-in ones. This is almost certainly because Charm Tech doesn't currently promote `pytest-jubilant`, and that's changing (really soon). It'll be interesting to see how much this changes, and how quickly.

## Example Migrations

We asked Copilot to pick 5 charms to migrate, instructing it to select a diverse set across teams. Although the tests are somewhat diverse in style and complexity, most of the chosen charms are actually from the same team — sorry about that. These have been submitted as real PRs upstream by [tonyandrewmeyer](https://github.com/tonyandrewmeyer):

| Charm | PR | Time | Score | AI Commit | Fix Commits | CI |
|-------|:--:|:----:|:-----:|:---------:|:-----------:|:--:|
| content-cache-k8s | [#167](https://github.com/canonical/content-cache-k8s-operator/pull/167) | 7 min | 25/25 | 1 | 3 | All green |
| nginx-ingress-integrator | [#324](https://github.com/canonical/nginx-ingress-integrator-operator/pull/324) | 10 min | 22/25 | 1 | 6 | Pass |
| indico | [#723](https://github.com/canonical/indico-operator/pull/723) | 10 min | 21/25 | 1 | 8 | Pass |
| loki-k8s | [#572](https://github.com/canonical/loki-k8s-operator/pull/572) | 17 min | 21/25 | 1 | 5 | Pass |
| hockeypuck-k8s | [#201](https://github.com/canonical/hockeypuck-k8s-operator/pull/201) | 9 min | 21/25 | 1 | 4 | All green |

In each PR, **the first commit is the direct output of the AI migration process**. All the remaining commits are fixes to get the tests actually passing — but AI was able to make those too, with a bit of help. The key was having the CI infrastructure hooked up so the model could see test failures and iterate. Having a way to `charmcraft test` and run integration tests locally would let this feedback loop happen earlier.

All PRs were manually reviewed by tonyandrewmeyer (Jubilant co-author, Charm Tech) before being submitted upstream. They look reasonable from that perspective, but they need review from someone familiar with the specific charm and its tests.

### What the fix commits tell us

Looking across the fix commits, the same patterns come up repeatedly:

- **Linting/formatting** — almost every PR needed a ruff, black, or flake8 fix. The migration is structurally correct but doesn't always match the project's exact formatter config.
- **Lock files** — `pyproject.toml` was updated but `uv.lock` wasn't always regenerated.
- **Wait/status subtleties** — `jubilant.all_active` checks *all* apps in the model, which breaks if a related app is in "waiting" status. Several PRs needed scoped waits.
- **Duplicate registrations** — `pytest-jubilant` already registers `--charm-file`, so re-adding it in `conftest.py` causes errors.
- **CI configuration** — Jubilant needs Juju 3+, so workflows defaulting to 2.9 needed channel updates.
- **Tooling compat** — `charmcraft pack -p` was removed in 3.x, requiring workarounds in some charms.

None of these are hard to fix, and the AI handled them all once it could see the CI output. All code checks pass on every PR, and the integration test failures that remain are environmental (timeouts, DNS, missing credentials) — not migration-related.

## What to Watch For

The output is good but not perfect, as you'd expect with using AI. **AI does the migration, but charming humans do full review!** When reviewing, check:

- **conftest.py**: Does it use the built-in `juju` fixture, or did it create a custom one? (Built-in is better.)
- **`juju.wait()` calls**: Watch for `successes=3` — this parameter doesn't exist.
- **Dependencies**: Make sure both `jubilant` and `pytest-jubilant` are added, and `pytest-operator` is removed.
- **Linting**: Run the project's linter — the AI migration may not match your exact config.
- **Lock files**: Regenerate `uv.lock` (or equivalent) if the AI didn't.

## Full Details

The complete experiment write-up, including all 22 run transcripts, evaluation scores, methodology, and a detailed practical guide, is available at:

[charming-with-claude/experiments/2026-02-17-jubilant-migration-experiment](https://github.com/tonyandrewmeyer/charming-with-claude/tree/main/experiments/2026-02-17-jubilant-migration-experiment)

If you try this on your charm, let us know how it goes! We know that a few people have already boldly walked this path — we'd love to hear more about how things went for you, too, and what approach(es) you took.
