# testing-context-state

## Version
ops 2.23.0

## Type
Feature

## Summary
`testing.Context` gains a method to create a `testing.State` from the current context, making it easier to set up realistic test states by introspecting the charm's metadata.

## Before
```python
import ops
from ops import testing

ctx = testing.Context(MyCharm)
# Had to manually construct state matching the charm's metadata
state = testing.State(
    relations=[
        testing.Relation(endpoint="database", interface="postgresql"),
    ],
    containers=[
        testing.Container(name="workload", can_connect=True),
    ],
)
state_out = ctx.run(ctx.on.start(), state)
```

## After
```python
import ops
from ops import testing

ctx = testing.Context(MyCharm)
# Generate a state pre-populated from charm metadata
state = ctx.get_default_state()
# Then customise as needed
state_out = ctx.run(ctx.on.start(), state)
```

## Why Upgrade
Reduces boilerplate in tests by auto-generating a `State` object from the charm's metadata (relations, containers, storage, etc.). Tests stay in sync with metadata changes automatically.

## Complexity
Moderate

## Detection
Look for test files that manually construct `testing.State` objects with containers and relations that mirror the charm's `metadata.yaml` or `charmcraft.yaml`. These are candidates for using the default state factory.

## Exemplar Charms
*To be populated in Phase 2.*

## Pitfalls
- The generated state is a starting point — tests still need to customise it for their specific scenario (e.g. setting relation data, container file contents).
- The exact method name and API should be verified against the current ops documentation, as this feature was new in 2.23.0 and may have evolved.
