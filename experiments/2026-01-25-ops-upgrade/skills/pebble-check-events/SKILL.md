# Skill: Adopt Pebble Check Events

Replace health check polling with reactive `pebble-check-failed` and `pebble-check-recovered` events.

## When to Use

Use this when a K8s charm polls Pebble health check status (e.g. in `update-status`) or could benefit from reactive health monitoring. Also useful for charms that define Pebble checks but don't react to their failure/recovery.

## Prerequisites

- ops >= 2.15.0
- The charm runs a workload in a Pebble-managed container
- The container's Pebble layer defines (or should define) health checks

## Step 1: Audit Current Health Monitoring

Search the charm code for:

1. **Existing Pebble checks**: look at the Pebble layer definition for `"checks"` sections.
   ```python
   layer = ops.pebble.Layer({
       "checks": {
           "myapp-ready": {
               "override": "replace",
               "level": "ready",
               "http": {"url": "http://localhost:8080/health"},
           }
       }
   })
   ```

2. **Manual health polling**: search for patterns like:
   - `container.get_checks(` — direct check inspection
   - Health checks in `_on_update_status` — polling on the 5-minute timer
   - `container.exec(["curl", ...])` or similar health probes in event handlers

3. **Status management based on health**: look for patterns where the charm sets `BlockedStatus` or `WaitingStatus` based on workload health.

## Step 2: Ensure Pebble Checks Are Defined

If the charm's Pebble layer doesn't already define checks, add them. Common check types:

### HTTP check
```python
"checks": {
    "myapp-ready": {
        "override": "replace",
        "level": "ready",
        "period": "30s",
        "threshold": 3,
        "http": {"url": "http://localhost:8080/health"},
    }
}
```

### TCP check
```python
"checks": {
    "myapp-alive": {
        "override": "replace",
        "level": "alive",
        "period": "30s",
        "threshold": 3,
        "tcp": {"port": 5432},
    }
}
```

### Exec check
```python
"checks": {
    "myapp-ready": {
        "override": "replace",
        "level": "ready",
        "period": "30s",
        "threshold": 3,
        "exec": {"command": "/usr/bin/healthcheck"},
    }
}
```

**Key parameters**:
- `level`: `"alive"` (is the process running?) or `"ready"` (is it ready to serve?)
- `period`: how often Pebble runs the check (default `"10s"`)
- `threshold`: how many consecutive failures before firing `check-failed` (default `3`)

## Step 3: Add Event Observers

Register handlers for the check events. The events are per-container:

```python
class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        # ... existing observers ...
        self.framework.observe(
            self.on["myapp"].pebble_check_failed,
            self._on_check_failed,
        )
        self.framework.observe(
            self.on["myapp"].pebble_check_recovered,
            self._on_check_recovered,
        )
```

Replace `"myapp"` with the container name from `charmcraft.yaml`.

## Step 4: Implement the Handlers

### Basic pattern: update status on check state changes

```python
def _on_check_failed(self, event: ops.PebbleCheckFailedEvent):
    """Handle a Pebble health check failure."""
    logger.warning(
        "Health check %s failed (threshold reached)", event.info.name
    )
    # Let collect-status handle the actual status — just log here
    # Or set status directly if the charm doesn't use collect-status:
    self.unit.status = ops.BlockedStatus(
        f"Workload health check '{event.info.name}' failing"
    )

def _on_check_recovered(self, event: ops.PebbleCheckRecoveredEvent):
    """Handle a Pebble health check recovery."""
    logger.info("Health check %s recovered", event.info.name)
    # Re-evaluate status
    self.unit.status = ops.ActiveStatus()
```

### With collect-status (preferred for charms that use it)

If the charm uses `collect-unit-status`, the check event handlers can simply trigger a status re-evaluation rather than setting status directly:

```python
def _on_check_failed(self, event: ops.PebbleCheckFailedEvent):
    logger.warning("Health check %s failed", event.info.name)
    # Status will be set by collect-unit-status on next hook

def _on_check_recovered(self, event: ops.PebbleCheckRecoveredEvent):
    logger.info("Health check %s recovered", event.info.name)

def _on_collect_unit_status(self, event: ops.CollectStatusEvent):
    container = self.unit.get_container("myapp")
    if container.can_connect():
        checks = container.get_checks(level=ops.pebble.CheckLevel.READY)
        for name, info in checks.items():
            if info.status == ops.pebble.CheckStatus.DOWN:
                event.add_status(ops.BlockedStatus(f"Check '{name}' failing"))
                return
    event.add_status(ops.ActiveStatus())
```

## Step 5: Remove Polling

Remove any health check polling from `update-status` or other periodic handlers. Common patterns to remove:

```python
# Remove this kind of pattern:
def _on_update_status(self, event):
    container = self.unit.get_container("myapp")
    if container.can_connect():
        checks = container.get_checks()
        for name, check in checks.items():
            if check.status == ops.pebble.CheckStatus.DOWN:
                self.unit.status = ops.BlockedStatus(f"{name} failing")
                return
    self.unit.status = ops.ActiveStatus()
```

If `_on_update_status` does other things besides health polling, only remove the health check portion.

## Step 6: Update Tests

### ops.testing (Scenario) tests

```python
import ops
from ops import testing


def test_check_failed():
    container = testing.Container(
        "myapp",
        can_connect=True,
    )
    ctx = testing.Context(MyCharm)
    state = testing.State(containers={container})
    check_info = ops.pebble.CheckInfo(
        name="myapp-ready",
        level=ops.pebble.CheckLevel.READY,
        status=ops.pebble.CheckStatus.DOWN,
        threshold=3,
        failures=3,
    )
    state_out = ctx.run(
        ctx.on.pebble_check_failed(container, check_info),
        state,
    )
    assert isinstance(state_out.unit_status, testing.BlockedStatus)


def test_check_recovered():
    container = testing.Container(
        "myapp",
        can_connect=True,
    )
    ctx = testing.Context(MyCharm)
    state = testing.State(containers={container})
    check_info = ops.pebble.CheckInfo(
        name="myapp-ready",
        level=ops.pebble.CheckLevel.READY,
        status=ops.pebble.CheckStatus.UP,
        threshold=3,
    )
    state_out = ctx.run(
        ctx.on.pebble_check_recovered(container, check_info),
        state,
    )
    assert isinstance(state_out.unit_status, testing.ActiveStatus)
```

## Step 7: Verify

1. Run `tox -e lint`.
2. Run `tox -e unit` — all tests should pass.
3. Verify no remaining health check polling in `update-status` (unless it serves a purpose beyond what check events cover).
4. Review the diff:
   - New event observers and handlers should be present.
   - Pebble layer should include checks (if not already).
   - Polling code should be removed.
   - No unrelated changes.

## Common Mistakes

- **Not defining Pebble checks in the layer**: the events only fire if Pebble checks exist. Adding observers without checks does nothing.
- **Setting the threshold too low**: a threshold of 1 means a single failure fires `check-failed`. For health checks, 3 is a sensible default to avoid false alarms.
- **Forgetting that `check-recovered` only fires after `check-failed`**: you can't rely on `check-recovered` firing on initial startup. Use `pebble-ready` for initial health confirmation.
- **Removing all health logic from `collect-status`**: if the charm uses `collect-unit-status`, keep health check inspection there as a safety net — the check events are the primary signal, but collect-status should reflect current reality regardless.
- **Not handling multiple containers**: if the charm has multiple containers, each needs its own event observers.
