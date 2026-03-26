# ops-tracing-adoption

## Version
ops 2.21.0

## Type
Feature (major)

## Summary
`ops[tracing]` introduced as the first-party charm tracing library, replacing the community `charm_tracing` / `charms.tempo_k8s.v2.tracing` library approach. Charms can now add OpenTelemetry tracing with `pip install ops[tracing]` and minimal code changes.

## Before
```python
# Using the community charm_tracing library
from charms.tempo_k8s.v2.tracing import charm_tracing, trace_charm

from ops.charm import CharmBase


@trace_charm(
    tracing_endpoint="tracing_endpoint",
    extra_types=[...],
)
class MyCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.tracing = TracingEndpointRequirer(self, ...)
```

## After
```python
import ops
import ops.tracing


class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        ops.tracing.setup(
            self,
            relation_name="tracing",  # the relation providing the OTLP endpoint
        )
```

## Why Upgrade
- **First-party**: maintained alongside ops itself, guaranteed compatibility.
- **Simpler**: one `setup()` call replaces decorator-based configuration.
- **No charm library dependency**: no need to fetch and update `charms.tempo_k8s` libs.
- **Consistent**: all charms using `ops[tracing]` trace in the same way.
- **Tested in ops CI**: the tracing integration is tested as part of the ops release process.

## Complexity
Moderate — straightforward for charms already using `charm_tracing` (mostly a simplification), more work for charms adding tracing for the first time.

## Detection
- Charms already using tracing: search for `charm_tracing`, `trace_charm`, or `TracingEndpointRequirer` imports.
- Charms that could add tracing: check for a `tracing` or `tempo-k8s` relation in `charmcraft.yaml` / `metadata.yaml`, or look for charms in the observability ecosystem.

## Exemplar Charms
- [canonical/sdcore-amf-operator](https://github.com/canonical/sdcore-amf-operator) (src/charm.py) — Cleanest pattern: `self.tracing = ops.tracing.Tracing(self, "tracing")` with `ops[tracing]~=3.0`.
- [canonical/postgresql-k8s-operator](https://github.com/canonical/postgresql-k8s-operator) (src/charm.py) — Typical K8s charm: `from ops_tracing import Tracing` then `Tracing(self, tracing_relation_name=TRACING_RELATION_NAME)` with a named constant.
- [canonical/postgresql-operator](https://github.com/canonical/postgresql-operator) (src/charm.py) — Advanced VM pattern: uses `set_destination()` to route tracing through grafana-agent for VM charms.

**Notable**: adoption is still early — only ~4 production charms found using `ops[tracing]`. The Data Platform team (postgresql, pgbouncer) and SD-Core team are early adopters. Most observability charms (alertmanager, loki, traefik, tempo) still use the community `charm_tracing` library.

## Pitfalls
- `ops[tracing]` requires the charm to have a relation providing an OTLP endpoint (typically `tracing` backed by Tempo).
- The `relation_name` in `setup()` must match the relation name in `charmcraft.yaml`.
- Charms migrating from `charm_tracing` need to remove the old library and its charm lib fetching configuration.
- The `ops[tracing]` API evolved between 2.21.0 and later versions — check for compatibility if targeting an older ops version.
- Charms using `charm_tracing` decorators on individual methods may need to adjust — `ops.tracing` traces at the charm level.
