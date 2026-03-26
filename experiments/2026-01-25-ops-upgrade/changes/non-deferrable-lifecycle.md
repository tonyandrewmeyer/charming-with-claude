# non-deferrable-lifecycle

## Version
ops 2.11.0

## Type
Breaking change

## Summary
`StopEvent`, `RemoveEvent`, and all `LifecycleEvent` subclasses are now non-deferrable. Calling `defer()` on these events raises `RuntimeError`. Charms that defer lifecycle events must be updated.

## Before
```python
import ops

class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.stop, self._on_stop)
        self.framework.observe(self.on.remove, self._on_remove)

    def _on_stop(self, event: ops.StopEvent):
        if not self._cleanup_complete():
            event.defer()  # This worked before 2.11.0
            return
        self._do_cleanup()

    def _on_remove(self, event: ops.RemoveEvent):
        if not self._can_remove():
            event.defer()  # This worked before 2.11.0
            return
        self._do_removal()
```

## After
```python
import ops

class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.stop, self._on_stop)
        self.framework.observe(self.on.remove, self._on_remove)

    def _on_stop(self, event: ops.StopEvent):
        # Must handle cleanup immediately — cannot defer
        self._do_cleanup()

    def _on_remove(self, event: ops.RemoveEvent):
        # Must handle removal immediately — cannot defer
        self._do_removal()
```

## Why Upgrade
- **Correctness**: deferring lifecycle events was always semantically wrong — these events represent one-time state transitions that won't be re-emitted. The deferred handler would run in a context where the event's semantics no longer apply.
- **Required**: calling `defer()` on these events now raises `RuntimeError`, so the charm will crash if not updated.
- **Better design**: forces charms to handle cleanup synchronously, which is more predictable and debuggable.

## Complexity
Trivial to moderate — trivial if the charm simply removes the `defer()` call, moderate if it needs to restructure cleanup logic to work without deferral.

## Detection
Search for `.defer()` in handlers for `StopEvent`, `RemoveEvent`, `InstallEvent`, `StartEvent`, `UpgradeCharmEvent`, and other lifecycle events. Also check for `event.defer()` in any handler registered on `self.on.stop`, `self.on.remove`, etc.

## Exemplar Charms
Most charms were already not deferring lifecycle events. This is primarily a fix for charms with legacy patterns.

## Pitfalls
- Some charms may have deferred lifecycle events intentionally as a retry mechanism. These need redesigning — consider using stored state or Pebble notices to trigger retry logic from a different event.
- The change applies to *all* `LifecycleEvent` subclasses, not just `StopEvent` and `RemoveEvent`. Check `InstallEvent`, `StartEvent`, `UpgradeCharmEvent`, `LeaderElectedEvent`, `LeaderSettingsChangedEvent`, `PreSeriesUpgradeEvent`, `PostSeriesUpgradeEvent` as well.
- `CollectStatusEvent` was also designated as a `LifecycleEvent` in 2.10.0, so it's non-deferrable too.
