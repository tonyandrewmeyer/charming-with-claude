# testing-app-name-unit-id

## Version
ops 3.1.0

## Type
Feature

## Summary
`testing.Context` gains `app_name` and `unit_id` attributes, allowing tests to set the charm's application name and unit number explicitly.

## Before
```python
import ops
from ops import testing

ctx = testing.Context(MyCharm)
# The app name and unit ID were fixed defaults; no easy way to test
# behaviour that depends on the unit number or app name.
state_out = ctx.run(ctx.on.start(), testing.State())
```

## After
```python
import ops
from ops import testing

ctx = testing.Context(MyCharm, app_name="my-app", unit_id=2)
# Now the charm sees self.app.name == "my-app" and self.unit.name == "my-app/2"
state_out = ctx.run(ctx.on.start(), testing.State())
```

## Why Upgrade
Enables testing behaviour that depends on the application name or unit number (e.g. leader election logic, unit-specific paths, peer relation behaviour with specific unit IDs).

## Complexity
Trivial

## Detection
Look for tests that need specific app names or unit numbers but work around the limitation (e.g. mocking `self.app.name` or `self.unit.name`).

## Exemplar Charms
- [canonical/charmed-etcd-operator](https://github.com/canonical/charmed-etcd-operator) (tests/unit/test_charm.py) -- Uses both `app_name="etcd"` and `unit_id=0`. Clean example.
- [canonical/generic-exporter-operator](https://github.com/canonical/generic-exporter-operator) (tests/unit/test_charm.py) -- Uses `unit_id=1` to test non-zero unit scenarios. Strongest exemplar.
- [canonical/opensearch-operator](https://github.com/canonical/opensearch-operator) (tests/unit/conftest.py) -- Uses `unit_id=` parameterised from test fixtures.
- [canonical/data-kubeflow-integrator](https://github.com/canonical/data-kubeflow-integrator) (tests/unit/) -- Consistently uses `unit_id=0` across 6 test modules.
- [canonical/cos-coordinated-workers](https://github.com/canonical/cos-coordinated-workers) (tests/unit/test_coordinator.py) -- Library (not a charm) but demonstrates good `app_name=` pattern.

## Pitfalls
- Most tests don't need custom app names or unit IDs — only use this when testing behaviour that genuinely depends on them.
- The `unit_id` is the numeric part only (e.g. `2`), not the full unit name (`my-app/2`).
