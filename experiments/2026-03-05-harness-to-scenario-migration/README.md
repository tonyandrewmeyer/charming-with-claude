# Harness to Scenario Migration

In this experiment, I used AI to migrate the unit tests for the [prometheus-k8s](https://github.com/canonical/prometheus-k8s-operator) charm from the deprecated `ops.testing.Harness` to state-transition tests (Scenario, via `ops.testing`). Unlike the previous experiments, this wasn't about building a new charm -- it was about a common maintenance task that many charm teams face, and one that I think is particularly well suited to AI assistance. I'd been meaning to try this for a while, and was prompted (sorry!) by the appearance of a dedicated skill in the [copilot-collections](https://github.com/canonical/copilot-collections) repository (currently still a PR).

I ran the same migration twice: once with a bare prompt and no special instructions, and once with a detailed skill (taken entirely from the copilot-collections PR) that provides a structured workflow, reference materials, and reusable recipes. My theory, based on what I've seen likely with skills,  was that recent models are capable enough to do a good job without elaborate scaffolding, and that the skill would provide diminishing returns.

## Goals

* Compare the quality of AI-assisted Harness-to-Scenario migration with and without a detailed skill.
* Determine whether investing in creating skills for this kind of task is worthwhile.
* Evaluate how well current models understand the Scenario testing API. (This is particularly interesting because they've done poorly in the past, and having both Harness and Scenario in the `ops.testing` namespace, and the relative new-ness of Scenario in "ops[testing]" form, has caused models difficulty).

## Setup

I would normally use Claude Code for experiments, but since the copilot-collections skill is designed specifically for Copilot (even though it ought to work equally well with Claude Code), both runs used GitHub Copilot Coding Agent on the same repository ([prometheus-k8s-operator](https://github.com/canonical/prometheus-k8s-operator)), targeting the same file: `tests/unit/test_charm.py`.

### Run 1: Bare Prompt (PR [#1](https://github.com/tonyandrewmeyer/prometheus-k8s-operator/pull/1))

The prompt was simply:

> Please convert the tests/unit/test_charm tests from Harness to Scenario (ops[testing], State transition tests)

(I realised after viewing the results that I was a bit lax with the instruction, which is, I think, why I had an additional file changed. I fixed that for the other prompt).

### Run 2: With Skill (PR [#2](https://github.com/tonyandrewmeyer/prometheus-k8s-operator/pull/2))

The prompt was:

> Migrate the tests in tests/unit/test_charm.py from Harness to State Transition. There is a skill available for this.

The skill used is from [this copilot-collections PR](https://github.com/canonical/copilot-collections/pull/29). A copy of the skill files is in the [skill/](./skill/) directory of this experiment.

## Results

### Summary

| Metric | Bare Prompt (PR #1) | With Skill (PR #2) |
|--------|---------------------|---------------------|
| Files changed | 2 | 1 |
| Lines added | 686 | 525 |
| Lines deleted | 774 | 686 |
| Net change | -88 | -161 |
| Test classes migrated | 5 | 5 |
| Import style | `from ops.testing import ...` | `from scenario import ...` |
| Container setup | Inline with layers | Minimal `_container()` factory |
| Plan access | Custom `_get_plan()` helper | `container.plan` property |
| Parametrisation | Loops inside tests | `pytest.mark.parametrize` |
| Status assertions | `state_out.unit_status.name == "active"` | `isinstance(state_out.unit_status, ActiveStatus)` |

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

## Conclusion

Neither approach produced a perfect migration, but both produced something substantially useful -- a charmer would be starting from a much better position than doing the migration from scratch.

The skill version is modestly better overall. Its advantages are in the details: proper use of `container.plan`, `pytest.mark.parametrize`, more idiomatic status assertions, and more thoughtful handling of the tricky "no restart" test. The bare prompt version's biggest mistake was reimplementing plan merging, which suggests the model didn't know about the `.plan` property -- exactly the kind of API detail a skill can surface.

However, the bare prompt version got the import style right (`ops.testing` rather than `scenario`), which is arguably more important for long-term maintainability. It also produced a more defensive container setup that would be more robust against `collect-status` issues.

The key question is whether the skill was worth the effort to create. For a one-off migration of a single charm, almost certainly not. The bare prompt got close enough. But for a team migrating dozens of charms, the skill's structured approach (inventory, checklist, recipes) and its ability to surface API details like `.plan` would compound in value. However, I strongly suspect that over time these advantages will continue to fade, as Scenario is more established and the models continue to improve.

My original theory -- that recent models would do the job well without elaborate instructions -- is partially confirmed. The bare prompt did a creditable job. But the skill version was noticeably better in ways that matter for code review and long-term maintenance. The investment in a skill pays off more with scale and repetition than with a single use.

## Files of Interest

* [PR #1](https://github.com/tonyandrewmeyer/prometheus-k8s-operator/pull/1) -- Bare prompt migration
* [PR #2](https://github.com/tonyandrewmeyer/prometheus-k8s-operator/pull/2) -- Migration using the skill
* [skill/](./skill/) -- Copy of the skill files used in PR #2
* [Skill PR](https://github.com/canonical/copilot-collections/pull/29) -- The original skill in copilot-collections
