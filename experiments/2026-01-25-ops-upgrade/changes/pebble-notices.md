# pebble-notices

## Version
ops 2.10.0

## Type
Feature

## Summary
Pebble Notices support allows K8s charms to react to custom notices from workloads via `PebbleCustomNoticeEvent`. Workloads can notify the charm of application-level events without polling, enabling event-driven communication between the charm and its container.

## Before
```python
import ops

class MyCharm(ops.CharmBase):
    def _on_update_status(self, event: ops.UpdateStatusEvent):
        # Polling pattern: check workload state periodically
        container = self.unit.get_container("myapp")
        if container.can_connect():
            process = container.exec(["check-migration-status"])
            stdout, _ = process.wait_output()
            if "complete" in stdout:
                self._handle_migration_complete()
```

## After
```python
import ops

class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        # React to a custom notice from the workload
        self.framework.observe(
            self.on["myapp"].pebble_custom_notice,
            self._on_custom_notice,
        )

    def _on_custom_notice(self, event: ops.PebbleCustomNoticeEvent):
        if event.notice.key == "example.com/migration-complete":
            self._handle_migration_complete()
```

The workload creates the notice via the Pebble API or CLI:
```bash
pebble notify example.com/migration-complete
```

## Why Upgrade
- **Event-driven**: eliminates polling in `update-status`, reducing unnecessary hook executions.
- **Lower latency**: the charm reacts immediately when the workload signals, rather than waiting up to 5 minutes for the next `update-status`.
- **Cleaner separation**: the workload explicitly signals meaningful state changes rather than the charm scraping for them.
- **Reduced load**: fewer hook executions means less Juju overhead in large deployments.

## Complexity
Moderate — requires both charm code changes and workload changes (the workload must issue `pebble notify` calls).

## Detection
Look for patterns where `update-status` or a timer polls the workload container for state. Also look for `exec()` calls that check workload status.

## Exemplar Charms
- Observability charms (tempo-k8s, grafana-k8s) have adopted Pebble notices for workload readiness signalling.
- Search for `pebble_custom_notice` across canonical/ repos.

## Pitfalls
- Requires Pebble 1.4+ in the rock/container image. Older rocks won't support notices.
- The notice key must follow the `domain/name` format (e.g. `example.com/migration-complete`).
- Notices are *not* guaranteed exactly-once — the charm may receive the same notice multiple times. Handlers should be idempotent.
- Both the charm and workload need updating — this isn't a charm-only change.
- The notice is delivered as a Juju event, so it's subject to the same event queue serialisation as other hooks.
