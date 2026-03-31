# juju-context

## Version
ops 3.3.0

## Type
Feature

## Summary
The Juju hook execution context is now exposed as a structured `ops.JujuContext` object, providing typed access to environment variables like the model name, unit name, availability zone, and event-specific context (relation ID, secret ID, etc.).

## Before
```python
import os

import ops


class MyCharm(ops.CharmBase):
    def _on_start(self, event):
        # Accessing Juju context required reading environment variables directly
        model_name = os.environ.get("JUJU_MODEL_NAME", "")
        unit_name = os.environ.get("JUJU_UNIT_NAME", "")
        az = os.environ.get("JUJU_AVAILABILITY_ZONE", "")

    def _on_relation_changed(self, event):
        # Relation context also via env vars
        relation_id = os.environ.get("JUJU_RELATION_ID", "")
        remote_unit = os.environ.get("JUJU_REMOTE_UNIT", "")
```

## After
```python
import ops


class MyCharm(ops.CharmBase):
    def _on_start(self, event):
        # Structured, typed access to the Juju context
        ctx = ops.JujuContext.from_environ()
        model_name = ctx.model_name
        unit_name = ctx.unit_name
        az = ctx.availability_zone  # Optional[str], None if not set

    def _on_relation_changed(self, event):
        ctx = ops.JujuContext.from_environ()
        relation_id = ctx.relation_id  # Optional[int]
        remote_unit = ctx.remote_unit_name  # Optional[str]
```

## Why Upgrade
- **Typed access**: no more string-based environment variable lookups with magic names.
- **Discoverability**: IDE autocompletion shows all available context fields.
- **Documentation**: each field is documented, making it clear which context is available for which event types.
- **Correctness**: reduces typos in environment variable names.

## Complexity
Trivial to moderate

## Detection
Search for `os.environ` or `os.getenv` calls that reference `JUJU_` prefixed variables in charm code. These can be replaced with `JujuContext` attribute access.

## Exemplar Charms
- [canonical/blackbox-exporter-operator](https://github.com/canonical/blackbox-exporter-operator) (src/charm.py) -- The only production charm using `JujuContext.from_environ()`. Uses it to access `principal_unit`, `availability_zone`, and `hook_name` — context not otherwise exposed by the framework. Good, idiomatic usage.

**Notable**: several repos (jhack, ops-reactive-interface, sunbeam-charms) use the private `_JujuContext` rather than the public API, suggesting the need existed before it was made public.

## Pitfalls
- Most charms access Juju context through the ops framework (`self.model.name`, `self.unit.name`, etc.) rather than environment variables. `JujuContext` is primarily useful for:
  - Charms that need context not exposed by the framework (e.g. availability zone).
  - Code outside the charm class (e.g. helper modules, libraries).
  - Advanced use cases like custom charming approaches outside the standard `CharmBase` pattern.
- `JujuContext.from_environ()` should only be called during hook execution (when the Juju environment is set up). Calling it outside a hook will raise `ValueError`.
- Optional fields return `None` when not applicable to the current event type.
