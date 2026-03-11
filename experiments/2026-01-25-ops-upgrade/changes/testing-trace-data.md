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
from opentelemetry.sdk.trace import ReadableSpan

ctx = testing.Context(MyCharm)
state_out = ctx.run(ctx.on.start(), testing.State())

# ctx.trace_data is a list[ReadableSpan] populated after each run
spans: list[ReadableSpan] = ctx.trace_data
span_names = [span.name for span in spans]
assert "method_name" in span_names

# Verify parent/child relationships using start/end timestamps,
# or check attributes on individual spans:
for span in ctx.trace_data:
    if span.name == "my_span":
        assert span.attributes["charm.name"] == "my-charm"
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
- `ctx.trace_data` is reset to an empty list at the start of each `ctx.run()` call, so inspect it immediately after the run you care about.
- Tests should not rely on the order of spans in `ctx.trace_data`. Validate by name, attributes, or parent/child relationships instead.
