# Skill: Migrate Harness Tests to ops.testing (Scenario)

Migrate unit tests from the deprecated `ops.testing.Harness` to the state-transition model in `ops.testing`.

## When to Use

Use this when a charm's unit tests use `ops.testing.Harness` and should be migrated to the modern `ops.testing` (Scenario) API. This is an exploratory skill for the ops-upgrade experiment — a more comprehensive version exists in the [dedicated harness-to-scenario migration experiment](../../../2026-03-05-harness-to-scenario-migration/).

## Prerequisites

- ops >= 2.17.0 (when `ops[testing]` extras were introduced)
- The charm has unit tests using `ops.testing.Harness`

## Key Insight from Prior Research

The [dedicated migration experiment](../../../2026-03-05-harness-to-scenario-migration/) found that **the feedback loop matters more than the amount of instruction**: running tests after each change and iterating on failures produced better results than following detailed recipes without verification. This skill incorporates that finding.

## Step 1: Assess Scope

1. Count Harness test files: `grep -rl "Harness" tests/unit/`
2. Estimate the migration size — each Harness test becomes one or more state-transition tests.
3. Decide whether to migrate incrementally (one file at a time) or all at once. For large test suites, incremental is safer.

**Harness and Scenario can coexist** during migration — you don't need to convert everything in one go.

## Step 2: Update Dependencies

Ensure `ops[testing]` is installed:

```toml
# pyproject.toml
[project.optional-dependencies]
testing = ["ops[testing]"]
```

Or add to the relevant `requirements.txt` / tox dependency group.

Remove `ops-scenario` if it's listed separately — it's now part of `ops[testing]`.

## Step 3: Understand the Mental Model Shift

### Harness (imperative, mutable)
```python
harness = Harness(MyCharm)
harness.add_relation("database", "postgresql")
harness.update_config({"port": "8080"})
harness.begin()
# State has been mutated step by step
assert harness.charm.unit.status == ActiveStatus()
```

### ops.testing (declarative, immutable)
```python
ctx = testing.Context(MyCharm)
state_in = testing.State(
    config={"port": "8080"},
    relations={testing.Relation(endpoint="database", interface="postgresql")},
)
state_out = ctx.run(ctx.on.config_changed(), state_in)
# state_in is unchanged; state_out is the result
assert state_out.unit_status == testing.ActiveStatus()
```

Key differences:
- **One event per test**: each `ctx.run()` fires a single event. No chaining.
- **State in, state out**: you construct the input state, run one event, and assert on the output state.
- **Immutable**: `state_in` is never modified. `state_out` is a new object.
- **No `begin()` / `begin_with_initial_hooks()`**: the Context handles charm instantiation.

## Step 4: Migrate Test by Test

For each Harness test:

1. **Identify the event being tested**: what Juju event does this test exercise?
2. **Build the input state**: what relations, config, containers, secrets, etc. does the charm need?
3. **Run the event**: `state_out = ctx.run(ctx.on.<event>(), state_in)`
4. **Assert on the output**: check `state_out.unit_status`, relation data, container state, etc.
5. **Run the tests immediately**: `tox -e unit -- tests/unit/test_file.py::test_name` — fix any failures before moving on.

### Common Translations

| Harness | ops.testing |
|---------|-------------|
| `harness = Harness(MyCharm)` | `ctx = testing.Context(MyCharm)` |
| `harness.update_config({"k": "v"})` | `state = testing.State(config={"k": "v"})` |
| `harness.add_relation("db", "pg")` | `rel = testing.Relation(endpoint="db", interface="pg")` in `State(relations={rel})` |
| `harness.begin()` | (implicit in `ctx.run()`) |
| `harness.charm.unit.status` | `state_out.unit_status` |
| `harness.get_relation_data(rel_id, "app/0")` | `state_out.get_relation(rel_id).local_unit_data` |
| `harness.run_action("backup", {...})` | `ctx.run(ctx.on.action("backup", params={...}), state)` |
| `pytest.raises(ActionFailed)` | same, or check `ctx.action_results` |

### Pebble containers

```python
container = testing.Container(
    "myapp",
    can_connect=True,
    layers={"base": ops.pebble.Layer({"services": {"myapp": {...}}})},
    service_statuses={"myapp": ops.pebble.ServiceStatus.ACTIVE},
)
state = testing.State(containers={container})
```

### Relations with data

```python
rel = testing.Relation(
    endpoint="database",
    interface="postgresql",
    remote_app_data={"connection-string": "postgresql://..."},
)
```

## Step 5: Validate After Each File

After migrating each test file:

1. Run: `tox -e unit -- tests/unit/the_migrated_file.py`
2. Fix any failures.
3. Run: `tox -e lint` — fix import ordering, unused imports.
4. Only move to the next file when the current one passes.

## Step 6: Clean Up

Once all tests in a file are migrated:

1. Remove `from ops.testing import Harness` imports.
2. Remove Harness-specific fixtures.
3. Remove any Harness helper utilities.
4. Run the full test suite: `tox -e unit`.

## Step 7: Verify

1. Full `tox -e unit` passes.
2. `grep -r "Harness" tests/unit/` returns no hits (or only hits in files not yet migrated, if doing incremental).
3. `tox -e lint` passes.
4. The diff should show Harness tests replaced with state-transition tests — no missing test coverage.

## Common Mistakes

- **Trying to replicate Harness mutation sequences**: don't chain multiple events in one test. Each test should exercise one event.
- **Forgetting container state**: if `collect-status` checks Pebble, the test state must include a container with appropriate layers/services.
- **Using `from scenario import ...`**: use `from ops import testing` or `from ops.testing import ...`. The `scenario` package is internal.
- **Not running tests after each change**: the most common source of cascading failures. Verify incrementally.
- **Over-mocking**: Scenario handles most Juju interactions. You rarely need to mock ops internals — if you're mocking heavily, the test design may need rethinking.

## References

- [How to migrate unit tests from Harness](https://documentation.ubuntu.com/ops/latest/howto/legacy/migrate-unit-tests-from-harness/) — canonical migration guide
- [Dedicated experiment](../../../2026-03-05-harness-to-scenario-migration/) — full experiment with three approaches tested against prometheus-k8s
- [copilot-collections skill](../../../2026-03-05-harness-to-scenario-migration/skill/SKILL.md) — comprehensive Copilot skill with scripts and references
