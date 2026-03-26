# Skill: Fix Non-Deferrable Lifecycle Events

Remove `defer()` calls on lifecycle events, which now raise `RuntimeError` as of ops 2.11.0.

## When to Use

Use this when upgrading a charm to ops >= 2.11.0 and the charm may defer lifecycle events. This is a **mandatory** fix — the charm will crash if lifecycle events are deferred.

## Prerequisites

- The charm targets ops >= 2.11.0
- The charm defers one or more lifecycle events

## Background

Since ops 2.11.0, all `LifecycleEvent` subclasses are non-deferrable. Calling `event.defer()` on these events raises `RuntimeError`. This was always semantically wrong — lifecycle events represent one-time state transitions that won't be re-emitted by Juju, so deferring them had unpredictable results.

The affected events are:
- `InstallEvent`
- `StartEvent`
- `StopEvent`
- `RemoveEvent`
- `UpgradeCharmEvent`
- `LeaderElectedEvent`
- `LeaderSettingsChangedEvent`
- `PreSeriesUpgradeEvent`
- `PostSeriesUpgradeEvent`
- `CollectStatusEvent` (designated as a LifecycleEvent in 2.10.0)

## Step 1: Find All Deferred Lifecycle Events

Search for `defer()` calls in handlers for any of the affected events:

```bash
# Search for .defer() in the charm code
grep -rn '\.defer()' src/ tests/
```

Then check which events those handlers are observing. Look for patterns like:

```python
self.framework.observe(self.on.install, self._on_install)
self.framework.observe(self.on.start, self._on_start)
self.framework.observe(self.on.stop, self._on_stop)
self.framework.observe(self.on.remove, self._on_remove)
self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
self.framework.observe(self.on.leader_elected, self._on_leader_elected)
```

For each handler that defers its event, check whether the event is a lifecycle event.

## Step 2: Understand Why the Defer Exists

Before removing a `defer()`, understand what it was trying to achieve:

### Pattern A: "Not ready yet, try later"

```python
def _on_install(self, event: ops.InstallEvent):
    if not self._dependencies_ready():
        event.defer()  # hoping to retry later
        return
    self._do_install()
```

**Fix**: remove the defer and handle the "not ready" case differently. Options:
1. **Set a waiting status and handle in a later event** (e.g. `config-changed`, `relation-changed`, or `update-status`):
   ```python
   def _on_install(self, event: ops.InstallEvent):
       if not self._dependencies_ready():
           self.unit.status = ops.WaitingStatus("Waiting for dependencies")
           return
       self._do_install()
   ```
2. **Do what you can now** — partial installation is often fine; complete the rest when the dependency arrives.

### Pattern B: "Resource not available"

```python
def _on_start(self, event: ops.StartEvent):
    container = self.unit.get_container("myapp")
    if not container.can_connect():
        event.defer()
        return
    self._configure_workload(container)
```

**Fix**: this is the wrong event for Pebble configuration anyway. Use `pebble-ready` instead:
```python
def __init__(self, *args):
    super().__init__(*args)
    self.framework.observe(self.on["myapp"].pebble_ready, self._on_pebble_ready)

def _on_pebble_ready(self, event: ops.PebbleReadyEvent):
    self._configure_workload(event.workload)
```

### Pattern C: "Cleanup might fail"

```python
def _on_stop(self, event: ops.StopEvent):
    if not self._cleanup_complete():
        event.defer()
        return
    self._do_cleanup()
```

**Fix**: do the cleanup unconditionally. If it fails, log the error but don't try to defer:
```python
def _on_stop(self, event: ops.StopEvent):
    try:
        self._do_cleanup()
    except Exception:
        logger.exception("Cleanup failed during stop")
```

### Pattern D: "Waiting for leader"

```python
def _on_upgrade_charm(self, event: ops.UpgradeCharmEvent):
    if not self.unit.is_leader():
        event.defer()
        return
    self._run_migration()
```

**Fix**: non-leaders should simply skip leader-only work, not defer:
```python
def _on_upgrade_charm(self, event: ops.UpgradeCharmEvent):
    if self.unit.is_leader():
        self._run_migration()
    self._update_workload()
```

## Step 3: Apply the Fixes

For each deferred lifecycle event:

1. Remove the `event.defer()` call.
2. Remove the early `return` that followed the defer (if the handler would otherwise do nothing).
3. Add appropriate alternative handling (status update, logging, guard clause, or restructured logic).
4. If the handler now does nothing useful for the non-ready case, consider whether the observer registration should be removed entirely.

## Step 4: Check for Indirect Deferrals

Some charms use a shared pattern like:

```python
def _ensure_ready(self, event):
    if not self._ready():
        event.defer()
        return False
    return True
```

If this is called from lifecycle event handlers, those paths need fixing too. Check all callers of such shared methods.

## Step 5: Update Tests

If tests verify deferral behaviour for lifecycle events, update them:

```python
# Before (testing that the event was deferred):
def test_install_defers_when_not_ready():
    ...
    assert event.deferred  # or similar

# After (testing that status is set instead):
def test_install_waits_when_not_ready():
    ...
    assert unit.status == ops.WaitingStatus("Waiting for dependencies")
```

## Step 6: Verify

1. Run `tox -e lint`.
2. Run `tox -e unit` — ensure no test expects a lifecycle event to be deferred.
3. Search for any remaining `defer()` calls and verify they're on non-lifecycle events (relation events, action events, etc. — those can still be deferred).
4. Review the diff — it should be focused on removing defers and adding alternative handling.

## Common Mistakes

- **Simply removing the defer without adding alternative handling**: the charm may silently skip important work. Always ensure the "not ready" case is handled (even if just setting a status).
- **Moving lifecycle logic to non-lifecycle events but still deferring there**: this trades one problem for another. Prefer status-based signalling over deferral where possible.
- **Missing shared utility methods**: a `_guard_ready(event)` helper that defers might be called from both lifecycle and non-lifecycle handlers. The fix needs to handle both cases.
- **Not checking `CollectStatusEvent`**: this became a LifecycleEvent in 2.10.0 and is also non-deferrable. It's less commonly deferred but worth checking.
