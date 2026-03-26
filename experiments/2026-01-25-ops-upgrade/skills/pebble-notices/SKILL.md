# Skill: Adopt Pebble Notices

Replace workload polling patterns with event-driven communication via Pebble custom notices.

## When to Use

Use this when a K8s charm polls its workload container for state changes (e.g. checking migration status, waiting for initialisation, monitoring background tasks) and could instead react to explicit signals from the workload.

## Prerequisites

- ops >= 2.10.0
- The charm runs a workload in a Pebble-managed container
- The workload can be modified to emit `pebble notify` calls (or uses a rock with Pebble 1.4+)

## Step 1: Identify Polling Patterns

Search the charm code for patterns where the charm polls the workload:

1. **`update-status` polling**: checking workload state every 5 minutes.
   ```python
   def _on_update_status(self, event):
       container = self.unit.get_container("myapp")
       result = container.exec(["check-status"]).wait_output()
       if "ready" in result[0]:
           self._handle_ready()
   ```

2. **`exec()` probes**: running commands in the container to inspect state.
   ```python
   process = container.exec(["migration-status"])
   stdout, _ = process.wait_output()
   ```

3. **File polling**: reading files in the container to detect changes.
   ```python
   content = container.pull("/var/lib/myapp/status").read()
   ```

For each polling pattern, determine:
- What state transition is being detected?
- How frequently is it polled?
- What action does the charm take when the state changes?

## Step 2: Design the Notice Keys

Each state transition needs a notice key. Keys follow the `domain/name` format:

```
example.com/migration-complete
example.com/backup-finished
example.com/config-reload-needed
```

Use a domain you control (or the charm's domain). The key should describe the state transition, not the action the charm should take.

## Step 3: Update the Workload

The workload needs to emit notices at the right moments. This requires modifying the workload's entrypoint, scripts, or configuration.

### Using the Pebble CLI

```bash
# In the workload's migration script:
pebble notify example.com/migration-complete
```

### Using the Pebble API (from Python)

```python
import requests

requests.post(
    "http://localhost/.pebble/v1/notices",
    json={"action": "add", "type": "custom", "key": "example.com/migration-complete"},
)
```

### Common integration points

- **Post-migration hook**: emit a notice after database migrations complete.
- **Startup script**: emit a notice once the application is fully initialised.
- **Background task completion**: emit a notice when a long-running task finishes.
- **Configuration reload**: emit a notice when the workload detects it needs the charm to update something.

## Step 4: Add Event Observers

Register handlers for the custom notice events:

```python
class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(
            self.on["myapp"].pebble_custom_notice,
            self._on_custom_notice,
        )
```

## Step 5: Implement the Handler

Route notices by key:

```python
def _on_custom_notice(self, event: ops.PebbleCustomNoticeEvent):
    """Handle a custom notice from the workload."""
    if event.notice.key == "example.com/migration-complete":
        self._handle_migration_complete()
    elif event.notice.key == "example.com/config-reload-needed":
        self._reconfigure_workload()
    else:
        logger.debug("Unhandled notice: %s", event.notice.key)
```

Or, for a single notice type, handle it directly:

```python
def _on_custom_notice(self, event: ops.PebbleCustomNoticeEvent):
    if event.notice.key != "example.com/migration-complete":
        return
    logger.info("Migration complete, updating status")
    self.unit.status = ops.ActiveStatus()
```

## Step 6: Remove Polling

Remove the polling patterns identified in step 1:

- Remove health/status checks from `_on_update_status` that are now covered by notices.
- Remove `exec()` calls that probe for state changes.
- Remove file-watching patterns.

If `_on_update_status` has other responsibilities, only remove the parts replaced by notices.

## Step 7: Update Tests

### ops.testing (Scenario) tests

```python
from ops import testing


def test_migration_notice():
    container = testing.Container(
        "myapp",
        can_connect=True,
        notices=[
            testing.Notice(
                key="example.com/migration-complete",
                type=ops.pebble.NoticeType.CUSTOM,
            ),
        ],
    )
    ctx = testing.Context(MyCharm)
    state = testing.State(containers={container})
    state_out = ctx.run(
        ctx.on.pebble_custom_notice(container, key="example.com/migration-complete"),
        state,
    )
    assert isinstance(state_out.unit_status, testing.ActiveStatus)
```

## Step 8: Verify

1. Run `tox -e lint`.
2. Run `tox -e unit`.
3. Verify polling has been removed from `update-status` (for the replaced patterns).
4. Review the diff:
   - New notice handler should be present.
   - Polling code should be removed.
   - No unrelated changes.

## Common Mistakes

- **Forgetting the workload side**: notices only work if the workload actually emits them. The charm-side changes are useless without the corresponding `pebble notify` calls.
- **Not making handlers idempotent**: notices may be delivered more than once. The handler should handle repeated invocations gracefully.
- **Using notices for health checks**: Pebble has dedicated health check events (`check-failed`/`check-recovered`) for ongoing health monitoring. Notices are for discrete state transitions, not continuous status.
- **Notice key format**: keys must use the `domain/name` format. Using a bare name like `migration-complete` is invalid.
- **Pebble version requirements**: custom notices require Pebble 1.4+. Check the rock's Pebble version.
- **Over-converting**: not every polling pattern should become a notice. If the charm is checking something that the workload doesn't know about (e.g. relation state), keep the polling.
