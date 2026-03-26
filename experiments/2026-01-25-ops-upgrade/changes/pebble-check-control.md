# pebble-check-control

## Version
ops 2.19.0

## Type
Feature

## Summary
Pebble health checks can now be programmatically started and stopped via `start_checks()` / `stop_checks()`, and their enabled state inspected via `CheckInfo.enabled`. This allows charms to temporarily disable health checks during maintenance operations.

## Before
```python
import ops

class MyCharm(ops.CharmBase):
    def _on_maintenance_action(self, event: ops.ActionEvent):
        # No way to pause health checks during maintenance
        # Charm might get false check-failed events during upgrades
        self._do_maintenance()
```

## After
```python
import ops

class MyCharm(ops.CharmBase):
    def _on_maintenance_action(self, event: ops.ActionEvent):
        container = self.unit.get_container("myapp")
        # Pause health checks during maintenance
        container.stop_checks(["readiness"])
        try:
            self._do_maintenance()
        finally:
            container.start_checks(["readiness"])
```

## Why Upgrade
- **Graceful maintenance**: prevent false health check failures during planned operations.
- **Fine-grained control**: enable/disable individual checks by name.
- **Inspection**: `CheckInfo.enabled` lets charm code reason about check state.

## Complexity
Trivial — simple API addition for charms that already use Pebble checks.

## Detection
Look for charms that define Pebble health checks and have maintenance or upgrade operations where false check failures could be problematic.

## Exemplar Charms
- Search for `start_checks` or `stop_checks` across canonical/ repos.

## Pitfalls
- Only useful for charms that already define Pebble health checks.
- Stopped checks don't fire `check-failed` events, which is the point — but make sure checks are re-enabled after maintenance.
- Requires a Pebble version that supports check control.
