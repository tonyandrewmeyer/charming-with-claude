# opentelemetry-log-target

## Version
ops 3.2.0

## Type
Feature

## Summary
A new `opentelemetry` log target type is available in Pebble layer definitions, allowing workloads to ship logs via OpenTelemetry Protocol (OTLP) instead of only Loki or syslog.

## Before
```python
# Pebble log targets were limited to loki and syslog types
layer = ops.pebble.Layer({
    "services": {
        "myapp": {
            "command": "/bin/myapp",
            "override": "replace",
        }
    },
    "log-targets": {
        "loki": {
            "type": "loki",
            "override": "merge",
            "location": "http://loki:3100/loki/api/v1/push",
            "services": ["all"],
        }
    },
})
```

## After
```python
# Can now use opentelemetry as a log target type
layer = ops.pebble.Layer({
    "services": {
        "myapp": {
            "command": "/bin/myapp",
            "override": "replace",
        }
    },
    "log-targets": {
        "otel": {
            "type": "opentelemetry",
            "override": "merge",
            "location": "http://otel-collector:4318",
            "services": ["all"],
        }
    },
})
```

## Why Upgrade
- OpenTelemetry is becoming the standard for observability. Using OTLP for logs aligns with modern observability stacks.
- Simplifies architecture when the charm already uses an OpenTelemetry collector for traces and metrics — logs can go through the same pipeline.
- Works with any OTLP-compatible backend, not just Loki.

## Complexity
Moderate

## Detection
Search for Pebble layer definitions that include `log-targets` sections, particularly those using `"type": "loki"`. Charms that are part of an OpenTelemetry-based observability stack may benefit from switching.

## Exemplar Charms
*To be populated in Phase 2.*

## Pitfalls
- This only makes sense if the charm's deployment environment uses an OpenTelemetry collector. Don't switch from Loki to OTLP without considering the receiving end.
- The `location` URL format differs between Loki and OTLP endpoints.
- This is a Pebble feature — only relevant for K8s charms using Pebble log forwarding.
- Whether to use this depends on the observability stack, not just the charm. It's an option, not a universal upgrade.
