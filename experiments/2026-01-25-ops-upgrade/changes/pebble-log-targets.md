# pebble-log-targets

## Version
ops 2.9.0

## Type
Feature

## Summary
Pebble layer and plan APIs now support log targets, allowing charms to configure log forwarding (e.g. to Loki) directly in the Pebble layer definition rather than via separate configuration mechanisms.

## Before
```python
import ops

class MyCharm(ops.CharmBase):
    def _configure_pebble(self):
        layer = ops.pebble.Layer({
            "services": {
                "myapp": {
                    "command": "/app/start",
                    "override": "replace",
                }
            },
            # No way to configure log forwarding in the layer
        })
        container.add_layer("myapp", layer, combine=True)
        # Log forwarding configured separately, e.g. via relation data
```

## After
```python
import ops

class MyCharm(ops.CharmBase):
    def _configure_pebble(self, loki_url: str):
        layer = ops.pebble.Layer({
            "services": {
                "myapp": {
                    "command": "/app/start",
                    "override": "replace",
                }
            },
            "log-targets": {
                "loki": {
                    "type": "loki",
                    "location": loki_url,
                    "services": ["myapp"],
                    "override": "replace",
                }
            },
        })
        container.add_layer("myapp", layer, combine=True)
```

## Why Upgrade
- **Unified configuration**: log forwarding is part of the Pebble layer, alongside services and checks.
- **Simpler plumbing**: no need to configure log forwarding through a separate mechanism.
- **Pebble-native**: leverages Pebble's built-in log forwarding rather than sidecar solutions.
- **Observability stack alignment**: works naturally with the Loki/COS stack that many Juju deployments use.

## Complexity
Moderate — requires understanding the Pebble log targets configuration and integrating with the logging relation (typically `loki-push-api`).

## Detection
Look for charms that have a `loki-push-api` or `logging` relation but configure log forwarding outside the Pebble layer. Also check for charms that use sidecar containers for log shipping.

## Exemplar Charms
- Observability charms (grafana-k8s, tempo-k8s) typically use Pebble log targets.
- Search for `log-targets` in Pebble layer definitions across canonical/ repos.

## Pitfalls
- Requires Pebble support for log targets (available from Pebble 1.1+).
- The `location` field must be a valid Loki push URL.
- Log targets are per-service — you must list which services to forward logs from.
- Layer merging with `combine=True` works for log targets, but be aware of override semantics.
- The OpenTelemetry log target type was added later in ops 3.2.0 — for the 2.9.0 feature, only `loki` type is available.
