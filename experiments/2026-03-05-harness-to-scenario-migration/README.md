# Harness to Scenario Migration

In this experiment, I used AI to migrate the unit tests for the [prometheus-k8s](https://github.com/canonical/prometheus-k8s-operator) charm from the deprecated `ops.testing.Harness` to state-transition tests (Scenario, via `ops.testing`). Unlike the previous experiments, this wasn't about building a new charm -- it was about a common maintenance task that many charm teams face, and one that I think is particularly well suited to AI assistance. I'd been meaning to try this for a while, and was prompted (sorry!) by the appearance of a dedicated skill in the [copilot-collections](https://github.com/canonical/copilot-collections) repository (currently still a PR).

I ran the same migration twice: once with a bare prompt and no special instructions, and once with a detailed skill (taken entirely from the copilot-collections PR) that provides a structured workflow, reference materials, and reusable recipes. My theory, based on what I've seen likely with skills,  was that recent models are capable enough to do a good job without elaborate scaffolding, and that the skill would provide diminishing returns.

I later added a third run using the [charmkeeper](https://github.com/seb4stien/charmkeeper) agent's unit test instructions -- a deliberately minimal approach that relies on reference implementations and a "learnings" feedback loop rather than detailed recipes.

## Goals

* Compare the quality of AI-assisted Harness-to-Scenario migration with and without a detailed skill.
* Determine whether investing in creating skills for this kind of task is worthwhile.
* Evaluate how well current models understand the Scenario testing API. (This is particularly interesting because they've done poorly in the past, and having both Harness and Scenario in the `ops.testing` namespace, and the relative new-ness of Scenario in "ops[testing]" form, has caused models difficulty).
* (Added 10 March 2026) Test whether a minimal, reference-based approach (charmkeeper) can match the detailed skill.

## Setup

I would normally use Claude Code for experiments, but since the copilot-collections skill is designed specifically for Copilot (even though it ought to work equally well with Claude Code), both runs used GitHub Copilot Coding Agent on the same repository ([prometheus-k8s-operator](https://github.com/canonical/prometheus-k8s-operator)), targeting the same file: `tests/unit/test_charm.py`.

### Run 1: Bare Prompt (PR [#1](https://github.com/tonyandrewmeyer/prometheus-k8s-operator/pull/1))

The prompt was simply:

> Please convert the tests/unit/test_charm tests from Harness to Scenario (ops[testing], State transition tests)

(I realised after viewing the results that I was a bit lax with the instruction, which is, I think, why I had an additional file changed. I fixed that for the other prompts).

### Run 2: With Skill (PR [#2](https://github.com/tonyandrewmeyer/prometheus-k8s-operator/pull/2))

The prompt was:

> Migrate the tests in tests/unit/test_charm.py from Harness to State Transition. There is a skill available for this.

The skill used is from [this copilot-collections PR](https://github.com/canonical/copilot-collections/pull/29). A copy of the skill files is in the [skill/](./skill/) directory of this experiment.

### Run 3: Charmkeeper Agent Instructions (added 10 March 2026)

The prompt was:

> Migrate the tests in tests/unit/test_charm.py from Harness to State Transition tests.

The agent instructions used were from [charmkeeper's unit test agent](https://github.com/seb4stien/charmkeeper/blob/main/.github/agents/charmkeeper-unit-tests.md). This is a deliberately lightweight approach: it names the target (`ops.testing`, not `harness`), links to a migration guide and a reference implementation (haproxy-operator's fixtures), requires linting via `tox -e lint`, and introduces a "learnings" feedback loop where the agent records gotchas for future runs. A copy of the instructions is in the [charmkeeper/](./charmkeeper/) directory of this experiment.

Unlike the copilot-collections skill, charmkeeper provides no recipes, no event playbooks, no checklist, and no code snippets. It trusts the agent to figure out the details from the migration guide and reference code.

This run was initially done with Claude Code (Opus), then re-run with Copilot CLI (Sonnet) to provide a fair comparison with the other two runs, which both used GitHub Copilot. The Copilot run is the one analysed below; where the Claude run differed materially, that's noted.

## Results

### Summary

| Metric | Bare Prompt (PR #1) | With Skill (PR #2) | Charmkeeper (Run 3) |
|--------|---------------------|---------------------|---------------------|
| Files changed | 2 | 1 | 1 |
| Test classes migrated | 5 | 5 | 5 |
| Tests pass | Yes | Yes | Yes (43 in file, 166 full suite) |
| Linting | Not checked | Not checked | Passed (`tox -e lint`) |
| Import style | `from ops.testing import ...` | `from scenario import ...` | `from scenario import ...` |
| Status type imports | N/A | `from scenario import ActiveStatus` (correct) | `from ops.model import ActiveStatus` (incorrect) |
| Container setup | Inline with layers | Minimal `_container()` factory | Reused `prometheus_container` fixture |
| Plan access | Custom `_get_plan()` helper | `container.plan` property | `container.plan` property |
| Parametrisation | Loops inside tests | `pytest.mark.parametrize` | `pytest.mark.parametrize` (partial) |
| Status assertions | `state_out.unit_status.name == "active"` | `isinstance(state_out.unit_status, ActiveStatus)` | `isinstance(state_out.unit_status, ActiveStatus)` |
| Fixture reuse | Created/expected external fixtures | Inline factory functions | Reused existing `conftest.py` fixtures |
| File system access | N/A | N/A | `container.get_filesystem(context)` |
| Learnings generated | N/A | N/A | No (checked for `learnings/` but didn't create one) |

### Detailed Analysis

#### Import Style

The bare prompt version imports from `ops.testing`:

```python
from ops.testing import Container, Exec, Relation, State
```

The skill version imports from `scenario`:

```python
from scenario import ActiveStatus, BlockedStatus, Container, Exec, MaintenanceStatus, Relation, State
```

The `ops.testing` import is the correct modern approach. Importing from `scenario` directly works but is the older style. This is a clear win for the bare prompt -- however, I'm fairly sure this could easily be solved with a small adjustment to the skill.

#### Container Construction

The bare prompt creates containers with explicit layers and service statuses:

```python
def _prometheus_container():
    return Container(
        "prometheus",
        can_connect=True,
        layers={"prometheus": pebble.Layer({"services": {"prometheus": {}}})},
        service_statuses={"prometheus": pebble.ServiceStatus.INACTIVE},
        execs={Exec(["update-ca-certificates", "--fresh"], return_code=0, stdout="")},
    )
```

The skill version creates a minimal container:

```python
def _container():
    return Container(
        "prometheus",
        can_connect=True,
        execs={Exec(["update-ca-certificates", "--fresh"], return_code=0, stdout="")},
    )
```

The skill version is leaner. Whether it's "better" depends on the charm -- if `collect-status` inspects the Pebble plan (as it often does), the bare prompt version's pre-populated layers might be necessary for tests to pass. Both sets of tests pass, but the bare prompt's approach is more defensive and closer to what the original Harness `setUp` was doing.

#### Plan Access

This is one of the more interesting differences. The bare prompt created a custom `_get_plan()` helper that manually merges layers:

```python
def _get_plan(state_out, context):
    container = state_out.get_container("prometheus")
    plan = pebble.Plan()
    for layer in container.layers.values():
        # ... manual merge logic
```

The skill version just uses `container.plan`:

```python
plan = state_out.get_container("prometheus").plan
```

The `.plan` property is the correct Scenario API for accessing the merged plan. The bare prompt version essentially reimplements what Scenario already provides, which is both unnecessary and fragile. This is a clear win for the skill version, and a good example of how models still struggle to 'know' the Scenario API.

#### Test Organisation and Parametrisation

The bare prompt keeps the same test structure as the original -- loops inside test methods:

```python
def test_valid_metrics_retention_times_can_be_set(self, context, prometheus_container):
    acceptable_units = ["y", "w", "d", "h", "m", "s"]
    for unit in acceptable_units:
        ...
```

The skill version uses `pytest.mark.parametrize`:

```python
@pytest.mark.parametrize("unit", ["y", "w", "d", "h", "m", "s"])
def test_valid_metrics_retention_times_can_be_set(self, context, unit):
    ...
```

Parametrisation is clearly better here: each parameter combination gets its own test case, so a failure pinpoints exactly which unit caused the problem. This is a win for the skill version, although it feels a bit outside of the "migrate from Harness to Scenario" task.

#### Status Assertions

The bare prompt uses string comparison:

```python
assert state_out.unit_status.name == "active"
```

The skill version uses `isinstance` with the status types:

```python
assert isinstance(state_out.unit_status, ActiveStatus)
```

Both work, but `isinstance` is more idiomatic for Scenario tests and gives better error messages on failure. The skill version also imports the status types from `scenario` (as noted previously), but the pattern is correct. Mild win for the skill version.

#### Scope and Side Effects

The bare prompt also migrated `test_charm_status.py` (a second file that wasn't explicitly requested), producing a net 2-file change. I believe this was likely because my prompt said `test_charm tests` rather than `test_charm.py`. The skill version stayed focused on the single file (but I had 'fixed' the prompt).

Both versions correctly:
- Removed the `ops.testing.SIMULATE_CAN_CONNECT = True` global
- Removed the `@prom_multipatch`, `@k8s_resource_multipatch`, and `@patch("lightkube...")` decorators
- Replaced `unittest.TestCase` classes with plain pytest classes
- Added an `autouse` fixture for the PVC capacity mock
- Converted `self.assertEqual` / `self.assertIsInstance` to `assert` statements

#### Handling Multi-Step Tests

Both versions handle tests that need state chaining (e.g., `test_configuration_reload` which needs a running Pebble plan before changing config). The bare prompt uses a helper method:

```python
def _get_running_state(self, context, prometheus_container):
    state = State(leader=True, containers=[prometheus_container])
    return context.run(context.on.pebble_ready(prometheus_container), state)
```

The skill version uses `dataclasses.replace`:

```python
state1 = State(containers=[container])
state_mid = context.run(context.on.config_changed(), state1)
state2 = dataclasses.replace(state_mid, config={"evaluation_interval": "1234m"})
```

Both approaches are valid. The skill version is more explicit about what it's doing but more verbose. The bare prompt's helper method creates reuse but hides the event choice. In Scenario, `dataclasses.replace` is the standard way to evolve state between runs, so the skill version is slightly more idiomatic.

#### The Pebble Plan "No Restart" Test

This test (`test_no_restart_nor_reload_when_nothing_changes`) is particularly tricky to migrate because the original Harness version patches the internal Pebble client methods to raise if called. The skill version handles this thoughtfully:

```python
with patch("prometheus_client.Prometheus.reload_configuration") as reload_mock, \
     patch.object(PrometheusCharm, "_generate_prometheus_config", return_value=False), \
     patch.object(PrometheusCharm, "_set_alerts", return_value=False):
    state_out = context.run(context.on.config_changed(), state_mid)
```

The bare prompt version doesn't include a clear equivalent for this test. The skill version's approach of patching the charm's own methods to report "no change" is a reasonable adaptation, with a comment explaining why.

### Fixture Pattern

The bare prompt version uses `conftest.py`-style fixtures via method parameters (`context`, `prometheus_container`), suggesting it created or expected fixtures elsewhere. The skill version creates containers inline or via a module-level factory function, making each test more self-contained.

### Run 3: Charmkeeper (added 10 March 2026)

The charmkeeper approach produced a noticeably different character of migration from the other two. Where the bare prompt and skill runs were both "here is a prompt, go", charmkeeper's feedback loop -- run the tests, lint the code, iterate -- meant the agent worked through problems incrementally rather than producing a single-shot output.

The Copilot (Sonnet) run completed in about 12 minutes of API time, using roughly 1 premium request. It was thorough in its exploration phase: it read every existing Scenario test file in the repository, the charm source, `tox.ini`, and `CONTRIBUTING.md` before writing a single line of migrated code.

#### Context Awareness

The most striking difference was how charmkeeper handled the existing codebase. Because it instructs the agent to look at reference implementations (haproxy-operator's conftest.py) and existing project structure, the agent noticed that the prometheus-k8s-operator already had a `conftest.py` with fixtures and a `helpers.py` with utility functions. Rather than creating its own factories (as both previous runs did), it reused the existing `prometheus_container` and `context` fixtures from conftest.py, adding only a local `pvc_capacity_mock` fixture for the PVC capacity mock that the Harness tests had in `setUp`.

This is arguably the most "charmer-like" behaviour of the three runs -- a human doing this migration would naturally reuse the existing test infrastructure.

#### Import Style

Like the skill version, charmkeeper used `from scenario import ...` rather than `from ops.testing import ...`. However, in this case it was arguably the *correct* choice for this specific repository: the existing test files all import from `scenario` (the standalone package), and the project pins `scenario` in its dependencies. Matching the existing codebase convention is more important than following the general best practice. The charmkeeper instructions say `ops.testing`, but the agent pragmatically followed what was already in the project -- a good sign of context-sensitivity.

The agent imported status types from `ops.model` (`from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus`) rather than from `scenario` as the skill version did. The correct approach is to import them from `ops.testing` (or `scenario`) -- these are Scenario's own status types that mirror the ops ones, and using the ops originals directly can cause subtle issues. This is a minor regression compared to the skill version, which got the imports right.

#### Plan Access

Charmkeeper correctly used `container.plan` rather than reimplementing plan merging. This matches the skill version's behaviour, suggesting that either the migration guide link or the reference implementations in the repo were enough to surface this API detail. The bare prompt's custom `_get_plan()` helper remains the only version to get this wrong.

#### File System Access

Charmkeeper was the only run to use `container.get_filesystem(context)` for reading files pushed to the container (e.g. the prometheus configuration and alert rules). This is the correct Scenario API for this pattern. The agent likely discovered it from the existing Scenario tests in the repo -- it read several of them during its exploration phase.

#### Parametrisation

Like the skill version, charmkeeper used `pytest.mark.parametrize` for retention time units and evaluation interval units. However, it was more selective than the Claude run: it kept the invalid retention time cases as inline assertions within a single test rather than parametrising them, and didn't parametrise log levels. The charmkeeper instructions don't mention parametrisation at all, so this was the agent's own initiative.

#### Status Assertions

Charmkeeper used `isinstance(state_out.unit_status, ActiveStatus)` for status assertions -- matching the skill version's pattern and better than the bare prompt's string comparison. However, it imported `ActiveStatus` from `ops.model` rather than from `scenario`/`ops.testing`, which means it's comparing against the wrong type (the ops status class rather than the Scenario one). The assertion happens to pass because of how Scenario handles this internally, but it's not correct. The earlier Claude run avoided this by using string comparison; the skill version got it right by importing from `scenario`.

#### The "No Restart" Test

Charmkeeper's approach was to fire `config_changed` to establish initial state (with hash files written), then fire `update_status` and compare the plans before and after to verify they're identical:

```python
state_out = context.run(context.on.config_changed(), state)
initial_plan = state_out.get_container("prometheus").plan.to_dict()

with patch("prometheus_client.Prometheus.reload_configuration") as mock_reload:
    state_out2 = context.run(context.on.update_status(), state_out)

current_plan = state_out2.get_container("prometheus").plan.to_dict()
assert initial_plan == current_plan
mock_reload.assert_not_called()
```

This is the cleanest handling of this test across all three runs. It's a true state-transition test: assert that certain state doesn't change, rather than patching internals to raise on unexpected calls.

#### Two-Step Reload Pattern

The agent independently discovered that `reload_configuration` is only triggered when the config *file* changes but the pebble layer stays the same. It created a `_state_after_initial_config()` helper to establish the initial state (including hash files on the container), then ran a second `config_changed` with a different `evaluation_interval` to trigger a reload. This is the same insight the Claude run had, arrived at through the same iterative process of running tests and reading charm source.

#### The Linting Feedback Loop

Charmkeeper was the only run that explicitly required linting (`tox -e lint`). The agent encountered and fixed several issues during iteration: unused imports cleaned by `ruff --fix`, docstring formatting (D205 -- blank line between summary and description), and import ordering. The final output was lint-clean. This is a practical advantage -- the other two runs may or may not pass linting, and any failures would be left for the human reviewer to fix.

#### Learnings

Despite the charmkeeper instructions saying to "look into `learnings/` to find learnings from previous similar tasks", and the agent duly checking for that directory (finding it absent), Copilot did **not** create a `learnings/` directory or write any learnings. This is a missed opportunity. The instructions tell the agent to "highlight your learnings to make future similar tasks easier", but the agent interpreted this as part of its summary output rather than as files to persist. The Claude (Opus) run behaved similarly.

This suggests the "learnings" feedback loop -- charmkeeper's most distinctive feature -- needs stronger prompting to actually trigger. The current instructions describe the concept clearly but don't make the "write learnings files" step explicit enough. Something like "Create `learnings/` if it doesn't exist and write a markdown file documenting gotchas you encountered" would likely close the loop.

The gotchas that *should* have been recorded as learnings include:

1. Import status types from `scenario` (or `ops.testing`), not `ops.model` -- Scenario has its own status classes
2. `_get_pvc_capacity` needs explicit mocking -- not covered by conftest
3. The reload vs. replan distinction (config file changes trigger reload; layer changes trigger replan)
4. Two-step test pattern needed for reload tests: initial `config_changed` to establish hash files, then a second run with changed config
5. D205 docstring formatting caught by ruff -- keep docstrings to single lines or add blank line after summary

## Conclusion

*Updated 10 March 2026 to incorporate the charmkeeper run. The original conclusion compared only the bare prompt and skill approaches.*

None of the three approaches produced a perfect migration, but all produced something substantially useful -- a charmer would be starting from a much better position than doing the migration from scratch.

### Skill vs. Bare Prompt (original finding)

The skill version is modestly better than the bare prompt overall. Its advantages are in the details: proper use of `container.plan`, `pytest.mark.parametrize`, more idiomatic status assertions, and more thoughtful handling of the tricky "no restart" test. The bare prompt version's biggest mistake was reimplementing plan merging, which suggests the model didn't know about the `.plan` property -- exactly the kind of API detail a skill can surface.

However, the bare prompt version got the import style right (`ops.testing` rather than `scenario`), which is arguably more important for long-term maintainability. It also produced a more defensive container setup that would be more robust against `collect-status` issues.

### Where Charmkeeper Fits

The charmkeeper run is the most interesting of the three, because it achieved near-skill-level quality with much less instruction. It got `container.plan` right, used `pytest.mark.parametrize`, produced the cleanest "no restart" test, reused the existing project infrastructure, and delivered lint-clean output -- all from instructions that amount to "use ops.testing, here's a migration guide, here are some reference fixtures, lint your code, and run the tests". Its main slip was importing status types from `ops.model` rather than `scenario`/`ops.testing` -- the kind of subtle API detail that a skill can surface but a migration guide link apparently didn't.

What charmkeeper gets right is the *structure* of the interaction rather than the *content* of the instructions. By requiring the agent to lint and run tests as part of its workflow, it creates a feedback loop that catches problems the other approaches leave for the human reviewer.

The "learnings" concept is charmkeeper's most distinctive idea, but in practice neither the Copilot nor the Claude run actually created learnings files, despite checking for the `learnings/` directory. The instructions describe the concept but don't make the "write files" step concrete enough. This is fixable -- but it's worth noting that the self-improving feedback loop, which is the strongest theoretical argument for the charmkeeper approach, didn't actually engage in this test. What *did* work was the simpler loop: write code, run tests, fix failures, lint, fix lint errors.

The trade-off is that charmkeeper's iterative approach is slower. The agent went through multiple rounds of running tests, fixing failures, linting, and fixing lint errors. The skill version's detailed recipes likely reduce this iteration, which matters if you're paying per token or per minute.

### Three Philosophies of AI Guidance

The three approaches represent three distinct philosophies:

1. **Bare prompt**: Trust the model. Minimal investment, reasonable results. Best when the task is well within the model's training data and you're doing it once.

2. **Detailed skill**: Encode expertise upfront. Higher investment, better first-pass quality. Best when you're doing many similar migrations and want consistent, reviewable output.

3. **Charmkeeper**: Provide structure and references, let the agent iterate. Moderate investment, with the *potential* for quality to improve over time via the learnings loop (though this didn't trigger in practice). Best when you want the agent to adapt to the existing codebase rather than follow a fixed recipe.

My original theory -- that recent models would do the job well without elaborate instructions -- is partially confirmed. The bare prompt did a creditable job. But the charmkeeper run suggests that the key variable isn't how much you tell the model, but whether you give it a way to verify and correct its own output. A feedback loop (run tests, lint, iterate) with minimal instructions outperformed a detailed skill without one.

The charmkeeper run also benefited from something the other two didn't: the existing Scenario tests in the repo. Because the instructions told the agent to look at reference implementations, it read the other test files and picked up patterns (like `isinstance` assertions and `get_filesystem`) that it might not have known otherwise. This is a form of implicit "learnings" -- the codebase itself teaches the agent what good looks like. A bare prompt agent could do the same, but charmkeeper's instructions nudge the agent to look before writing.

If I were advising a team migrating dozens of charms, I'd recommend the charmkeeper approach with two additions: first, the skill's `container.plan` hint and `ops.testing` import convention as explicit instructions; second, a more concrete learnings step (e.g. "create `learnings/harness-migration.md` with gotchas you encountered"). The best system would combine charmkeeper's iterative structure with the skill's most valuable API details -- giving the agent both the freedom to figure things out and the guardrails to avoid known pitfalls.

## Files of Interest

* [PR #1](https://github.com/tonyandrewmeyer/prometheus-k8s-operator/pull/1) -- Bare prompt migration
* [PR #2](https://github.com/tonyandrewmeyer/prometheus-k8s-operator/pull/2) -- Migration using the skill
* [skill/](./skill/) -- Copy of the skill files used in PR #2
* [Skill PR](https://github.com/canonical/copilot-collections/pull/29) -- The original skill in copilot-collections
* [charmkeeper/](./charmkeeper/) -- Copy of the charmkeeper agent instructions used in Run 3
* [Charmkeeper](https://github.com/seb4stien/charmkeeper) -- The charmkeeper project
