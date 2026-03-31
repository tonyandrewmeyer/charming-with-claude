# deferred-events-logging

## Version
ops 3.4.0

## Type
Improvement

## Summary
Ops now logs the total number of deferred events at the start of each event dispatch, providing visibility into deferred event accumulation.

## Before
```python
# No built-in logging of deferred event counts.
# Charms that wanted to monitor deferred event accumulation had to
# implement their own tracking, e.g.:
class MyCharm(ops.CharmBase):
    def __init__(self, framework):
        super().__init__(framework)
        # Custom deferred event tracking was the only option
```

## After
```python
# No code changes needed in the charm itself.
# Ops automatically logs a message like:
#   "Total deferred events: 3"
# at the start of each event dispatch.
# This helps operators and developers spot deferred event buildup.
```

## Why Upgrade
- **No charm code changes required** — this is a framework-level improvement.
- Helps identify charms that are accumulating deferred events, which is generally an anti-pattern.
- Useful for debugging: if a charm is misbehaving, operators can check logs for deferred event counts.

## Complexity
Trivial (no charm changes needed)

## Detection
Not applicable — this change is automatic when upgrading to ops 3.4.0+. However, charms that implement their own deferred event counting can now remove that custom logic.

## Exemplar Charms
Not applicable — this is a framework-level change.

## Pitfalls
- This is an informational improvement only. It doesn't change behaviour.
- If a charm has custom deferred event logging, consider removing it to avoid duplicate log messages.
- The real benefit is motivational: seeing "Total deferred events: 47" in logs may prompt developers to address the root cause.
