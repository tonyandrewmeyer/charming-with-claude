# testing-context-state

## Version
ops 2.23.0

## Type
Feature

## Summary
`testing.State` gains a class method `from_context()` that creates a `State` pre-populated from the charm's metadata, making it easier to set up realistic test states without manually mirroring `charmcraft.yaml`.

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
# Generate a State pre-populated from charm metadata:
# relations (with endpoint and interface set, no data), containers
# (can_connect=True), storage, and StoredState.
# Config is set to its default values from charmcraft.yaml.
state = testing.State.from_context(ctx)
# Then customise as needed — pass overrides directly:
state = testing.State.from_context(ctx, leader=True)
# Or replace specific components after construction:
db_relation = testing.Relation("database", local_app_data={"key": "value"})
state = testing.State.from_context(ctx, relations={db_relation})
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
- Passing a `Relation` override to `from_context()` replaces the auto-generated relation for that endpoint entirely; make sure to include all the fields you need.
- Relations in the generated state simulate `integrate` having already run; if your test is for the `relation-created` event, start from a bare `State()` instead.
