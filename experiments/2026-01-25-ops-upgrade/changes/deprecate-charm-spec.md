# deprecate-charm-spec

## Version
ops 3.5.0

## Type
Deprecation

## Summary
`testing.Context.charm_spec` is deprecated. Tests should use the charm's metadata directly rather than constructing or accessing a `CharmSpec` object.

## Before
```python
import ops
from ops import testing

# Accessing charm_spec directly (now deprecated)
ctx = testing.Context(MyCharm)
spec = ctx.charm_spec
# Using spec to inspect metadata or configure tests
```

## After
```python
import ops
from ops import testing

# Use the charm class and its metadata directly.
# Context reads the metadata from the charm's source directory.
ctx = testing.Context(MyCharm)
# No need to access charm_spec; the Context handles metadata internally.
```

## Why Upgrade
- Removes usage of a deprecated API that will eventually be removed.
- Simplifies test code by relying on the Context's built-in metadata handling.

## Complexity
Trivial

## Detection
Search for `charm_spec` in test files: `grep -r "charm_spec" tests/`.

## Exemplar Charms
*To be populated in Phase 2.*

## Pitfalls
- If tests use `charm_spec` to override metadata for testing purposes, they'll need to find an alternative approach (e.g. providing metadata via the Context constructor).
- The deprecation emits a warning; it still works in ops 3.5.0 but will be removed in a future version.
