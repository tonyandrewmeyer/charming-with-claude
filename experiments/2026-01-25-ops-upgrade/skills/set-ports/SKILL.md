# Skill: Adopt Declarative Port Management

Replace imperative `open_port()` / `close_port()` calls with the declarative `Unit.set_ports()` API.

## When to Use

Use this when a charm manages open ports using `open_port()`, `close_port()`, or tracks port state manually. The declarative API is simpler, idempotent, and less error-prone.

## Prerequisites

- ops >= 2.7.0
- The charm opens or closes ports (search for `open_port` or `close_port` in the codebase)

## Step 1: Audit Current Port Usage

1. Search the charm code for all port management:
   - `self.unit.open_port(` — imperative open
   - `self.unit.close_port(` — imperative close
   - `self.unit.opened_ports()` — port enumeration (still valid, no change needed)
2. Map out where ports are opened and closed. Common patterns:
   - Open a fixed port in `_on_start` or `_on_install`
   - Open/close ports in `_on_config_changed` when the port config changes
   - Close ports in `_on_stop` or `_on_relation_broken`
   - Track open ports in stored state to compute diffs
3. Note whether the charm opens ports in multiple event handlers — this affects the migration strategy.

## Step 2: Identify the Desired Port Set

For each event handler that manages ports, determine what the *desired set of ports* should be at that point. The key mental shift: instead of "open this, close that", think "the charm should have these ports open".

Common cases:

- **Fixed port**: the charm always wants one port open.
  ```python
  # Before:
  self.unit.open_port("tcp", 8080)

  # After:
  self.unit.set_ports(ops.Port("tcp", 8080))
  ```

- **Configurable port**: the port comes from config.
  ```python
  # Before:
  for opened in self.unit.opened_ports():
      if opened.port != new_port:
          self.unit.close_port("tcp", opened.port)
  self.unit.open_port("tcp", new_port)

  # After:
  self.unit.set_ports(ops.Port("tcp", new_port))
  ```

- **Multiple ports**: the charm manages several ports.
  ```python
  # Before:
  self.unit.open_port("tcp", 80)
  self.unit.open_port("tcp", 443)

  # After:
  self.unit.set_ports(ops.Port("tcp", 80), ops.Port("tcp", 443))
  ```

- **No ports** (e.g. relation broken, charm stopped):
  ```python
  # Before:
  for opened in self.unit.opened_ports():
      self.unit.close_port(opened.protocol, opened.port)

  # After:
  self.unit.set_ports()  # empty = close all
  ```

## Step 3: Apply the Changes

### Simple case: ports managed in one place

If all port management happens in a single method (e.g. a `_configure_ports` helper or `_on_config_changed`), the migration is straightforward: replace the open/close logic with a single `set_ports()` call.

### Complex case: ports managed across multiple handlers

If the charm opens ports in `_on_config_changed` and closes them in `_on_relation_broken`, you need to consolidate. Two approaches:

**Option A: Centralise into a helper method** (preferred)
```python
def _update_ports(self):
    """Set ports based on current charm state."""
    if not self._ready():
        self.unit.set_ports()
        return
    port = int(self.config["port"])
    self.unit.set_ports(ops.Port("tcp", port))
```
Call this helper from every handler that might affect port state.

**Option B: Set ports in each handler**
```python
def _on_config_changed(self, event):
    self.unit.set_ports(ops.Port("tcp", int(self.config["port"])))

def _on_relation_broken(self, event):
    self.unit.set_ports()  # close all
```
This is fine for simple charms but can lead to inconsistency if port logic is duplicated.

### Naming: `Port` vs `OpenPort`

`OpenPort` was renamed to `Port` in ops 2.7.0. Both work, but use `ops.Port` in new code.

## Step 4: Remove Port Tracking

If the charm tracks open ports in stored state or instance variables to compute diffs, that tracking code can be removed — `set_ports()` is declarative and handles the diff internally.

## Step 5: Update Tests

If tests assert on port state, update them to use the new API or assert on the expected outcome of `set_ports()`.

For `ops.testing` (Scenario) tests, the port state is part of `State.opened_ports`:
```python
state_out = ctx.run(ctx.on.config_changed(), state_in)
assert ops.Port("tcp", 8080) in state_out.opened_ports
```

For Harness tests, `opened_ports()` still works for inspection.

## Step 6: Verify

1. Run `tox -e lint` — ensure `ops.Port` is imported where needed.
2. Run `tox -e unit` — all tests should pass.
3. Review the diff:
   - All `open_port()` / `close_port()` calls should be gone.
   - Any port-tracking stored state should be removed.
   - The diff should be focused on port management — no unrelated changes.

## Common Mistakes

- **Forgetting that `set_ports()` replaces all ports**: if you call `set_ports(Port("tcp", 80))` and the charm also needs port 443 open, port 443 will be closed. Always pass the *complete* set of desired ports.
- **Leaving `close_port()` calls alongside `set_ports()`**: they're redundant. Use one pattern or the other, not both.
- **Not handling the "no ports" case**: when the charm should have no ports open (e.g. after relation departure), call `self.unit.set_ports()` with no arguments.
- **Using `OpenPort` instead of `Port`**: both work, but `Port` is the canonical name from 2.7.0 onwards.
