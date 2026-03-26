# pebble-check-events

## Version
ops 2.15.0

## Type
Feature

## Summary
New `pebble-check-failed` and `pebble-check-recovered` events allow K8s charms to react when Pebble health checks fail or recover, replacing manual check polling patterns.

## Before
```python
import ops

class MyCharm(ops.CharmBase):
    def _on_update_status(self, event: ops.UpdateStatusEvent):
        # Polling: manually check health on every update-status
        container = self.unit.get_container("myapp")
        if not container.can_connect():
            return
        checks = container.get_checks(level=ops.pebble.CheckLevel.ALIVE)
        for name, check in checks.items():
            if check.status == ops.pebble.CheckStatus.DOWN:
                self.unit.status = ops.BlockedStatus(
                    f"Health check {name} failing"
                )
                return
        self.unit.status = ops.ActiveStatus()
```

## After
```python
import ops

class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(
            self.on["myapp"].pebble_check_failed,
            self._on_check_failed,
        )
        self.framework.observe(
            self.on["myapp"].pebble_check_recovered,
            self._on_check_recovered,
        )

    def _on_check_failed(self, event: ops.PebbleCheckFailedEvent):
        self.unit.status = ops.BlockedStatus(
            f"Health check {event.info.name} failing"
        )

    def _on_check_recovered(self, event: ops.PebbleCheckRecoveredEvent):
        self.unit.status = ops.ActiveStatus()
```

## Why Upgrade
- **Reactive**: charm is notified immediately when checks fail or recover, rather than polling.
- **Lower latency**: health issues surface within seconds rather than waiting for `update-status`.
- **Simpler code**: no need to enumerate and inspect checks manually.
- **Separation of concerns**: Pebble manages the check schedule; the charm only handles state transitions.

## Complexity
Moderate — requires defining Pebble checks in the layer (if not already present) and adding event observers.

## Detection
Look for `get_checks()` calls in charm code, or for patterns where `update-status` monitors container health. Also check whether the Pebble layer already defines checks — if so, the charm can benefit from check events even if it wasn't previously monitoring them.

## Exemplar Charms
- [canonical/kratos-operator](https://github.com/canonical/kratos-operator) (src/charm.py, src/services.py) — Most complete: defines both `ready` and `alive` HTTP checks, observes both `check_failed` and `check_recovered`, with helper methods `is_running()` / `is_failing()` that also use `get_checks()`.
- [canonical/hydra-operator](https://github.com/canonical/hydra-operator) (src/charm.py) — Same pattern as kratos. HTTP health check with `threshold: 3`.
- [canonical/sunbeam-charms](https://github.com/canonical/sunbeam-charms) (ops-sunbeam/ops_sunbeam/container_handlers.py) — Generic base class handler that triggers status re-evaluation on check events (the only exemplar that actually takes action beyond logging).

**Notable**: adoption is very low — only the Identity Platform team's charms (kratos, hydra, admin-ui) and ops-sunbeam use these events. All Identity Platform charms follow a near-identical log-only pattern. Many charms define Pebble checks but don't observe the events.

## Pitfalls
- Requires Pebble checks to be defined in the container's Pebble layer. If the charm doesn't define health checks yet, those need adding too.
- The events fire based on Pebble's check threshold — a single check failure may not trigger the event if the threshold is > 1.
- `check-recovered` only fires if `check-failed` was previously fired for that check.
- Requires a Pebble version that supports check events (part of the Juju 3.x era rocks).
