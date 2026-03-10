# testing-trace-data

## Version
ops 2.23.0

## Type
Feature

## Summary
`ops.testing` now exposes trace data generated during test runs, allowing charms that use `ops[tracing]` to verify their tracing instrumentation in unit tests.

## Before
```python
import ops
from ops import testing

ctx = testing.Context(MyCharm)
state_out = ctx.run(ctx.on.start(), testing.State())
# No way to inspect whether the charm produced correct trace spans.
# Tracing verification required integration tests with a real collector.
```

## After
```python
import ops
from ops import testing

ctx = testing.Context(MyCharm)
state_out = ctx.run(ctx.on.start(), testing.State())
# Can now inspect trace data from the test run
# (Exact API to be verified against current documentation)
```

## Why Upgrade
- Enables unit-level testing of tracing instrumentation without a real OpenTelemetry collector.
- Catches tracing regressions early in the development cycle.
- Useful for charms using `ops[tracing]` that want to verify span names, attributes, and structure.

## Complexity
Moderate

## Detection
Look for charms that use `ops[tracing]` or import from `ops.tracing`. If they have unit tests but no tracing assertions, they could benefit from this feature.

## Exemplar Charms
*To be populated in Phase 2.*

## Pitfalls
- Only relevant for charms that use `ops[tracing]`.
- The trace data exposed in tests is a simplified representation; don't expect it to match the exact wire format of OTLP.
- Verify the exact API against current ops documentation, as this was introduced in 2.23.0 and may have evolved.
