# ops-testing-migration

## Version
ops 2.17.0

## Type
Feature (major)

## Summary
`ops[testing]` extras introduced, exposing Scenario-based testing as `ops.testing`. This is the beginning of the official migration path from Harness to Scenario-based testing. Installing `pip install ops[testing]` makes `ops.testing.State`, `ops.testing.Context`, and related classes available, providing a declarative, state-transition-based testing model.

## Before
```python
from ops.testing import Harness

from charm import MyCharm


def test_config_changed():
    harness = Harness(MyCharm)
    harness.begin()
    harness.update_config({"log-level": "debug"})
    assert harness.charm.unit.status == ops.ActiveStatus()
```

## After
```python
import ops
from ops import testing


def test_config_changed():
    ctx = testing.Context(MyCharm)
    state = testing.State(
        config={"log-level": "debug"},
    )
    out = ctx.run(ctx.on.config_changed(), state)
    assert out.unit_status == testing.ActiveStatus()
```

## Why Upgrade
- **Declarative**: tests define input state and assert on output state, rather than imperatively driving the charm.
- **Isolated**: each test run is independent — no shared mutable Harness state between tests.
- **Accurate**: Scenario more faithfully models Juju's actual behaviour (e.g. relation data access rules, event ordering).
- **Future-proof**: Harness is being phased out; `ops.testing` is the supported path forward.
- **Better error messages**: state mismatches produce clear diffs showing expected vs actual state.

## Complexity
Significant — a full Harness-to-Scenario migration can be a large undertaking for charms with extensive test suites. The testing paradigm is fundamentally different (imperative vs declarative), so tests need rewriting rather than mechanical updating.

## Detection
Check whether the charm's tests import from `ops.testing.Harness` or use the Harness class. Any charm still using Harness is a candidate for migration.

## Exemplar Charms
- Newer charms in the canonical/ org use `ops.testing` from the start.
- Some observability charms have partially migrated.
- Search for `from ops import testing` or `from ops.testing import Context` across canonical/ repos.

## Pitfalls
- This is a large migration — consider doing it incrementally (new tests in Scenario, migrate existing tests gradually).
- Harness and Scenario can coexist in the same test suite during migration.
- Some Harness patterns don't have direct Scenario equivalents — e.g. `harness.begin_with_initial_hooks()` becomes explicit event sequences.
- `ops[testing]` must be installed as an extra (`pip install ops[testing]`), not just `pip install ops`.
- Secret handling, relation data access rules, and storage behave differently in Scenario vs Harness — tests may need adjusting beyond syntax changes.
- The `ops.testing` API evolved between 2.17.0 and 2.23.0 — some patterns available in later versions weren't available initially.
