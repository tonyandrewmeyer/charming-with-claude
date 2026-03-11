# check-info-successes

## Version
ops 2.23.0

## Type
Feature

## Summary
`CheckInfo` gains a `successes` field and a `has_run` property, making it easier to determine whether a Pebble health check has executed and how many times it has succeeded.

## Before
```python
container = self.unit.get_container("workload")
checks = container.get_checks()
for name, check in checks.items():
    # No way to tell if a check has actually run yet vs. just being defined
    # Only had check.failures to look at
    if check.status == ops.pebble.CheckStatus.UP:
        logger.info(f"Check {name} is up (failures: {check.failures})")
```

## After
```python
container = self.unit.get_container("workload")
checks = container.get_checks()
for name, check in checks.items():
    if not check.has_run:
        logger.info(f"Check {name} hasn't run yet")
    else:
        logger.info(f"Check {name}: {check.successes} successes, {check.failures} failures")
```

## Why Upgrade
- `has_run` eliminates guesswork about whether a check has actually executed or is still pending.
- `successes` provides the positive counterpart to the existing `failures` count, enabling richer health reporting.

## Complexity
Trivial

## Detection
Search for usage of `container.get_checks()` or references to `CheckInfo`. Charms that inspect Pebble check results can benefit from the new fields.

## Exemplar Charms
*To be populated in Phase 2.*

## Pitfalls
- Only relevant for charms that use Pebble health checks (K8s charms with check definitions in their Pebble layers).
- `has_run` is a convenience property; it's equivalent to checking `successes > 0 or failures > 0`, but more readable.
