# testing-az-principal

## Version
ops 3.4.0

## Type
Feature

## Summary
`testing.Context` now allows setting the Juju availability zone and principal unit, enabling tests for subordinate charm behaviour and AZ-aware logic.

## Before
```python
import ops
from ops import testing

ctx = testing.Context(MySubordinateCharm)
# No way to set the availability zone or principal unit in tests.
# Subordinate charm testing was limited — couldn't properly simulate
# the principal unit relationship.
state_out = ctx.run(ctx.on.start(), testing.State())
```

## After
```python
import ops
from ops import testing

ctx = testing.Context(
    MySubordinateCharm,
    juju_context={"availability_zone": "zone-1"},
)
state = testing.State(
    relations=[
        testing.SubordinateRelation(
            endpoint="juju-info",
            remote_app_name="principal-app",
        ),
    ],
)
state_out = ctx.run(ctx.on.start(), state)
```

## Why Upgrade
- Availability zone testing: charms that distribute workloads across AZs can now be tested properly.
- Subordinate charm testing: principal unit context enables more realistic subordinate charm tests.

## Complexity
Trivial

## Detection
- Search for subordinate charms (check `metadata.yaml` for `subordinate: true`) that have limited test coverage.
- Search for charms that reference availability zones or use `model.get_raw_juju_context()` to access AZ information.

## Exemplar Charms
*To be populated in Phase 2.*

## Pitfalls
- The exact API for setting availability zone and principal unit should be verified against current documentation — the Context constructor parameters may have a specific format.
- Only relevant for charms that are subordinates or care about availability zones.
