# Jubilant Migration Experiment: Can Copilot Migrate Your Integration Tests?

An experiment to evaluate how effectively GitHub Copilot (using Claude models) can migrate Juju charm integration tests from pytest-operator/python-libjuju to [Jubilant](https://documentation.ubuntu.com/jubilant) and [pytest-jubilant](https://pypi.org/project/pytest-jubilant/).

## Contents

- [README.md](README.md) — This file: overview, goals, and summary of findings
- [methodology.md](methodology.md) — Detailed experimental methodology
- [results.md](results.md) — Full results with data tables and analysis
- [evaluation-rubric.md](evaluation-rubric.md) — Scoring criteria used to evaluate migrations
- [guidance.md](guidance.md) — Practical guide for charmers using Copilot to migrate
- [prompts/](prompts/) — The 6 prompt templates tested at each assistance level
- [results/](results/) — Raw Copilot session transcripts and diffs for each run
- [gold-standards/](gold-standards/) — Reference migrations used for comparison
- [discourse-post.md](discourse-post.md) — Draft Discourse post announcing findings

## Background

Canonical's charm ecosystem is migrating integration tests from [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) (which wraps [python-libjuju](https://github.com/juju/python-libjuju)) to [Jubilant](https://github.com/canonical/jubilant), a simpler, synchronous library that wraps the Juju CLI directly. This migration involves:

- Removing `async`/`await` patterns throughout test code
- Replacing `OpsTest` fixtures with `Juju` instances
- Updating deployment, waiting, integration, and action APIs
- Switching from `ops_test.build_charm()` to `pytest_jubilant.pack()`
- Updating dependencies in `pyproject.toml` or `tox.ini`

The migration is largely mechanical but touches many files and requires understanding both the old and new APIs. This makes it an ideal candidate for AI-assisted migration.

Like many technical debt projects, it is difficult to find the time to get this work done, so if AI can assist, that would be particularly useful. There is some time pressure, because Jubilant supports both Juju 3 and Juju 4 (and even Juju 2.9 via `jubilant-backports`), whereas `python-libjuju` does not (and will never, in the current form) support Juju 4. We want charms to verify that they work on Juju 4, so having integration tests that work across both versions is critical for achieving that.

## Goals

This experiment has two primary goals:

1. **Scientific evaluation**: Determine how much assistance Copilot needs to produce high-quality migrations, using a controlled comparison of different prompt strategies.
2. **Practical guidance**: Produce actionable recommendations for charmers who want to use Copilot to speed up their own migrations.

For charmers, (2) is the most important. (1) plays into it, but is also continuing the investigations of previous experience into how much assistance is required, especially with the models released in late 2025 and afterwards.

### Research Questions

1. Can Copilot migrate integration tests from `pytest-operator` to `jubilant` with minimal human review? Note that the goal is not *no* human review - humans should always be reviewing the code that goes into the charm, including tests. However, we want 2-3 skilled charmers familiar with the charm to be able to spend a normal amount of time reviewing the charms, removing the extensive manual conversion work.
2. How much context/guidance does the model need? Is a bare prompt enough, or does it need detailed recipes, documentation pointers, or working examples?
3. Does model choice matter? (Claude Opus 4.6 vs Claude Sonnet 4.6 -- I'm a bit biased towards the Claude models from previous success, but I would also guess that some of this research would apply to other model choice)
4. How close does the AI output come to human-authored "gold standard" migrations?
5. What patterns does Copilot handle well, and where does it consistently struggle?

## Methodology Summary

See [methodology.md](methodology.md) for full details.

I tested **6 levels of assistance**, from a bare one-line prompt to a detailed recipe combined with a working example:

| Level | Description | Context Provided |
|-------|-------------|-----------------|
| 1 | Bare prompt | One-line migration instruction |
| 2 | + Docs pointer | Points to Jubilant documentation |
| 3 | + Source inspection | Instructs model to install and read Jubilant source |
| 4 | + Example charm | Points to a fully-migrated charm as reference |
| 5 | Detailed recipe | Full migration recipe with API mappings and steps |
| 6 | Recipe + example | Recipe plus reference to migrated charm |

I ran all 6 levels on `saml-integrator-operator` using both Claude Sonnet 4.6 and Claude Opus 4.6 (12 runs), additional targeted runs on `s3-integrator` (5 runs), then the best approach on 5 additional charms from diverse teams (5 runs) — 22 experiments in total.

(It's worth noting that one of the reasons for the number of runs was that some of them used a lot of memory and OOM'd out a couple of times, so I dropped a couple of less promising ones. The VM doing the work only had 8GB of memory.)

Each run was evaluated against the [evaluation rubric](evaluation-rubric.md) scoring correctness, completeness, code quality, minimal diff, and human review needed.

## Charms Tested

### Full Matrix (all 6 levels, both models)

| Charm | Domain | Complexity | Integration Test Files |
|-------|--------|------------|----------------------|
| [saml-integrator-operator](https://github.com/canonical/saml-integrator-operator) | Identity | Simple (2 tests) | conftest.py, test_charm.py |

### Confirmation Runs (selected levels, Sonnet)

| Charm | Domain | Complexity | Levels Tested |
|-------|--------|------------|---------------|
| [s3-integrator](https://github.com/canonical/s3-integrator) | Data/Storage | Medium (5 tests + helpers) | L1, L3, L5, L6 |

### Broader Sample (L3 + Sonnet 4.6)

| Charm | Domain | Complexity | Files Changed |
|-------|--------|------------|:-------------:|
| [nginx-ingress-integrator-operator](https://github.com/canonical/nginx-ingress-integrator-operator) | Networking | Medium | 5 |
| [content-cache-k8s-operator](https://github.com/canonical/content-cache-k8s-operator) | Web Infrastructure | Simple-Medium | 4 |
| [indico-operator](https://github.com/canonical/indico-operator) | Web App / PaaS | Complex | 7 |
| [loki-k8s-operator](https://github.com/canonical/loki-k8s-operator) | Observability | Large | 18 |
| [hockeypuck-k8s-operator](https://github.com/canonical/hockeypuck-k8s-operator) | Security | Complex (multi-model) | 4 |

### Gold Standard References

| Charm | Source | Notes |
|-------|--------|-------|
| paas-charm (Django) | [PR #222](https://github.com/canonical/paas-charm/pull/222) | AI-assisted migration, reviewed and merged |
| paas-charm (FastAPI) | [PR #226](https://github.com/canonical/paas-charm/pull/226) | AI-assisted migration, reviewed and merged |
| wordpress-k8s-operator | [Repository](https://github.com/canonical/wordpress-k8s-operator) | Fully migrated to jubilant |
| kyuubi-k8s-operator | [PR #76](https://github.com/canonical/kyuubi-k8s-operator/pull/76) |

Note that all of these were done by others, not me.

## Results Summary

See [results.md](results.md) for the full data.

### TL;DR numbers

| Metric | Value |
|--------|-------|
| Best approach | **Level 3 (source inspection) + Claude Sonnet 4.6** |
| Average score with best approach | **24.0 / 25** (across 7 charms) |
| Perfect scores (25/25) | 2 out of 7 L3+Sonnet runs |
| Runs scoring 21+ ("merge-ready") | **100%** of L3+Sonnet runs |
| Worst approach | Level 5 (recipe) + Claude Opus 4.6: **12 / 25** |
| Time range | 3–17 minutes depending on charm complexity |

### Score comparison (saml-integrator, all levels)

| Level | Sonnet 4.6 | Opus 4.6 |
|-------|:----------:|:--------:|
| L1: Bare prompt | **24** | 20 |
| L2: + Docs pointer | 17 | 17 |
| L3: + Source inspection | **25** | 18 |
| L4: + Example charm | **24** | 18 |
| L5: Detailed recipe | 18 | 12 |
| L6: Recipe + example | 22 | 14 |

## Key Findings

### 1. Sonnet consistently outperforms Opus for this task

Across all 12 paired comparisons, Sonnet scored higher than or equal to Opus. The average gap was **+5.2 points** (out of 25). Opus tends to over-engineer: adding unnecessary logging, environment variable handling, redundant assertions, and structural refactoring that goes beyond the migration scope. For a well-defined mechanical migration, Sonnet's simpler, more direct approach wins.

### 2. Reading the source code is the best form of guidance

Level 3 (install `jubilant` + read the source) produced the best results because (I assume) the model gets absolute truth API information and doesn't need to extract it out of (nice for humans) HTML docs. I believe this reduces risk of hallucination, increases the likelihood of correct parameter names, and provides awareness of all available fixtures and methods. This scored a perfect 25/25 on the simple charm and 21-25 on all others.

My guess was that this would be best, based on what I've observed models do when building charms: with no guidance at all there is a lot of 'fumbling' around, but extensive help isn't required after the late 2025 model releases. I've seen agents inspecting packages (typically out of the venv) frequently, so based this approach on that, with an explicit push.

### 3. More guidance doesn't always help

Perhaps counter-intuitively to some, the detailed recipe (Level 5) scored *lower* than the bare prompt (Level 1). The recipe introduced problems:
- **Hallucinated parameters**: The recipe's examples included slightly wrong API details that the model copied faithfully (perhaps this was unfair of me and I should have fixed this when I noticed and re-ran these ones)
- **Interactive design conflict**: Recipe checkpoints saying "STOP and wait" caused Opus to exit immediately in non-interactive mode
- **Unnecessary artefacts**: State tracking files that shouldn't be committed

### 4. A bare prompt works surprisingly well

Level 1 scored 24/25 with Sonnet — the model proactively searched for Jubilant documentation and produced a clean migration with no prompting beyond "migrate these tests". This suggests the Jubilant API is already well-represented in the model's training data.

### 5. Pointing to docs can be counterproductive

Level 2 (docs pointer) scored the lowest of all Sonnet runs (17/25). This does seem a bit odd given (4) above! Reading the Jubilant documentation led models to implement low-level patterns (manual `temp_model()` fixtures) instead of using `pytest-jubilant`'s higher-level abstractions (James's work this cycle may solve this). Pithy, but: The docs describe what's possible; the source code shows what's idiomatic.

### 6. The approach scales to complex charms

Level 3 + Sonnet successfully migrated charms ranging from two tests (`saml-integrator`) to 18 files with 1,450 lines removed (`loki-k8s`). It correctly handled multi-model testing, container SSH, complex fixture chains, and action migrations. Time scaled roughly linearly with complexity.

## Recommendations

1. **Use Claude Sonnet 4.6** (or later) as the model — over Opus (or if wanting a non-Anthropic model, research which is best)
2. **Use the Level 3 prompt** (source inspection) for best results
3. **Run linting and formatting** after the migration — Copilot usually does this itself, but verify
4. **Review the conftest.py carefully** — this is where most issues appear (custom vs built-in fixtures)
5. **Check for hallucinated parameters** — especially `successes=` in `juju.wait()` calls
6. **Don't use the detailed recipe in non-interactive mode** — it was designed for supervised use

See [guidance.md](guidance.md) for a complete step-by-step guide.

## Example Migrations

To put this into practice, Copilot was instructed to pick 5 charms to migrate using the recommended approach (Level 3 + Sonnet 4.6), selecting a diverse set across teams. Although the tests are somewhat diverse in style and complexity, most of the charms are actually from the same team — sorry about that. The resulting migrations have been submitted as PRs upstream (currently draft):

| Charm | PR | Score | AI Commit | Fix Commits | CI |
|-------|:--:|:-----:|:---------:|:-----------:|:--:|
| [content-cache-k8s](https://github.com/canonical/content-cache-k8s-operator) | [#167](https://github.com/canonical/content-cache-k8s-operator/pull/167) | 25/25 | 1 | 3 | All green |
| [nginx-ingress-integrator](https://github.com/canonical/nginx-ingress-integrator-operator) | [#324](https://github.com/canonical/nginx-ingress-integrator-operator/pull/324) | 22/25 | 1 | 6 | Pass (except a couple of arm tests that I think are unrelated) |
| [indico](https://github.com/canonical/indico-operator) | [#723](https://github.com/canonical/indico-operator/pull/723) | 21/25 | 1 | 8 | Pass (env failures only, from what I can tell) |
| [loki-k8s](https://github.com/canonical/loki-k8s-operator) | [#572](https://github.com/canonical/loki-k8s-operator/pull/572) | 21/25 | 1 | 5 | Pass (env failures I think, but am least sure) |
| [hockeypuck-k8s](https://github.com/canonical/hockeypuck-k8s-operator) | [#201](https://github.com/canonical/hockeypuck-k8s-operator/pull/201) | 21/25 | 1 | 4 | All green |

In each PR, **the first commit is the direct output of the AI migration process**. All subsequent commits are fixes needed to get the tests passing — but AI was able to make those fixes too, with a bit of help, once the CI infrastructure was hooked up so that the model could actually see the test failures and act on them. Having a way to `charmcraft test` and run integration tests locally would mean this feedback loop could happen earlier, without needing to push to CI first.

I manually reviewed each PR before submitting upstream, but this is from someone that knows Jubilant pretty well but doesn't really know the charm or its tests. They look reasonable from that perspective, but they do need review from someone familiar with the specific charm and its tests.

### Common fixes needed after the initial AI migration

Looking across the fix commits, clear patterns emerge:

1. **Linting and formatting** (ruff, black, flake8): Almost every PR needed at least one formatting fix. The initial migration gets the code right but doesn't always match the project's exact formatter configuration.

2. **Lock file regeneration**: The AI updated `pyproject.toml` dependencies but didn't always regenerate `uv.lock` (nginx-ingress, loki).

3. **Type errors**: `jubilant.Juju.model` is `str | None`, and the AI sometimes passed it where `str` was expected (nginx-ingress, loki).

4. **Duplicate option registration**: `pytest-jubilant` already registers `--charm-file`, so adding it again in `conftest.py` causes a `ValueError` (indico).

5. **Wait/status subtleties**: `jubilant.all_active` checks *all* apps in the model, which can fail if a related app is in "waiting" status. Several PRs needed to scope waits to specific apps (content-cache, nginx-ingress).

6. **Tooling compatibility**: confusion around `charmcraft pack -p`, which `pytest_jubilant.pack()` uses internally (loki).

7. **CI configuration**: Jubilant uses `juju integrate` (Juju 3+), so CI workflows defaulting to Juju 2.9 needed channel updates. Juju 3.6 also requires strictly confined microk8s (indico).

8. **API details**: Jubilant's `juju.run()` raises `TaskError` on failure rather than returning a failed result, requiring `pytest.raises` (indico). Local charm paths need `resolve()` to avoid ambiguity with charmhub names (hockeypuck).

These are all things the AI was able to fix once it could see the CI output. The pattern was consistent: the initial migration is structurally correct but needs a round or two of polish to handle project-specific linting rules, dependency tooling, and CI environment details that aren't visible from the source code alone.

## Related Experiments

The [harness-to-scenario migration experiment](../2026-03-05-harness-to-scenario-migration/) explores the same core question — how much does an AI model need to be guided to perform a mechanical test migration? — but for unit tests rather than integration tests. It compares a bare prompt against a detailed skill for migrating from the deprecated `ops.testing.Harness` to state-transition tests (`ops.testing` / Scenario), and is a much smaller study (2 runs on a single charm). The conclusions broadly align: a bare prompt does a creditable job, and a well-crafted skill offers modest but meaningful improvements.

## Post-script: Charmkeeper

Since this experiment was conducted, the [Charmkeeper](https://github.com/seb4stien/charmkeeper) project has published a dedicated [integration test agent](https://github.com/seb4stien/charmkeeper/blob/main/.github/agents/charmkeeper-integration-tests.md) for writing, updating, and migrating integration tests to Jubilant. Charmkeeper is a custom agent designed to automate charm maintenance and modernisation — it analyses charm repositories and proposes standardisation improvements via draft PRs, covering unit tests, integration tests, and Terraform modules.

The integration test agent takes a more opinionated approach than our experiment's single-prompt strategy. It provides structured conventions around fixtures, test organisation, dependency management (including Renovate configuration for tracking charm revisions), and maintains a "learnings" folder to accumulate organisational knowledge across runs — letting the agent improve over time as it encounters new patterns.

This wasn't evaluated as part of our experiment because it wasn't available at the time, but it's well worth investigating — particularly if you're looking for an ongoing, agent-based workflow for charm maintenance rather than one-off migrations.

## TL;DR but somehow got this far down, how does this help you?

See [guidance.md](guidance.md) for a practical, step-by-step guide to using Copilot for your own migration.
