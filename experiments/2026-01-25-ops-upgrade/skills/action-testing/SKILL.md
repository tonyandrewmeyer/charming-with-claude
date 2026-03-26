# Skill: Adopt Modern Action Testing

Replace legacy action test patterns with `Harness.run_action()`, `ActionOutput`, and `ActionFailed`.

## When to Use

Use this when a charm's unit tests exercise actions using older Harness patterns (manual event emission, backend introspection) instead of the `run_action()` API introduced in ops 2.9.0.

## Prerequisites

- ops >= 2.9.0
- The charm has actions defined in `charmcraft.yaml` (or `actions.yaml`)
- The charm's unit tests test actions using the Harness

## Step 1: Audit Current Action Tests

Search test files for action testing patterns:

### Old patterns to look for

1. **Manual event emission**:
   ```python
   harness.charm.on.backup_action.emit(params={"target": "/data"})
   ```

2. **Backend introspection for results**:
   ```python
   action_results = harness._backend._action_results
   ```

3. **No clean failure testing**: tests that can't easily verify `event.fail()` was called.

4. **Action event stored as instance variable**:
   ```python
   self._last_action_event = event  # stored for test inspection
   ```

### Already-modern patterns (no change needed)

If tests already use `harness.run_action()`, they don't need updating:
```python
output = harness.run_action("backup", {"target": "/data"})
```

## Step 2: Rewrite Action Tests

### Testing successful actions

```python
# Before:
def test_backup_action(harness):
    harness.begin()
    harness.charm.on.backup_action.emit(params={"target": "/data"})
    # Hard to inspect results cleanly

# After:
from ops.testing import ActionOutput

def test_backup_action(harness):
    harness.begin()
    output: ActionOutput = harness.run_action("backup", {"target": "/data"})
    assert output.results["backup-file"] == "/data/backup.tar.gz"
    assert output.logs == ["Backup started", "Backup complete"]
```

### Testing action failures

```python
# Before:
def test_backup_fails_bad_target(harness):
    harness.begin()
    harness.charm.on.backup_action.emit(params={"target": "relative/path"})
    # Can't easily verify event.fail() was called

# After:
from ops.testing import ActionFailed

def test_backup_fails_bad_target(harness):
    harness.begin()
    with pytest.raises(ActionFailed) as exc_info:
        harness.run_action("backup", {"target": "relative/path"})
    assert "absolute path" in str(exc_info.value)
```

### Testing actions that set results

```python
def test_get_credentials_action(harness):
    harness.begin()
    output = harness.run_action("get-credentials")
    assert "username" in output.results
    assert "password" in output.results
```

### Testing actions with no parameters

```python
def test_restart_action(harness):
    harness.begin()
    output = harness.run_action("restart")
    assert output.results.get("status") == "restarted"
```

## Step 3: Key API Details

### Action name format

`run_action()` takes the action name as it appears in `charmcraft.yaml`, **without** the `-action` suffix:

```python
# Action defined as "get-password" in charmcraft.yaml:
output = harness.run_action("get-password", {"username": "admin"})
# NOT: harness.run_action("get-password-action", ...)
```

### Parameter naming

Parameters use the Juju naming convention (dashes), matching `charmcraft.yaml`:

```python
# If the action parameter is "max-retries" in charmcraft.yaml:
output = harness.run_action("backup", {"max-retries": "3"})
# NOT: {"max_retries": "3"}
```

### ActionOutput attributes

- `output.results` — dictionary of results set by the charm via `event.set_results()`
- `output.logs` — list of log messages set by the charm via `event.log()`

### ActionFailed

Raised when the action handler calls `event.fail()`. The exception message contains the failure message.

## Step 4: Clean Up Test Helpers

Remove any test infrastructure that existed to work around the old action testing limitations:

- Instance variables storing action events for test inspection
- Custom action result extraction helpers
- Backend introspection utilities
- Action event mock objects

## Step 5: Verify

1. Run `tox -e lint`.
2. Run `tox -e unit` — all action tests should pass.
3. Search for any remaining old patterns (manual `.emit()` for actions, backend access for results).
4. Review the diff — action tests should be simpler and more readable.

## Note: ops.testing (Scenario) Actions

If the charm's tests already use `ops.testing` (Scenario) instead of Harness, the action testing API is different:

```python
from ops import testing

def test_backup_action():
    ctx = testing.Context(MyCharm)
    state = testing.State()
    ctx.run(ctx.on.action("backup", params={"target": "/data"}), state)
    assert ctx.action_results["backup-file"] == "/data/backup.tar.gz"
```

This skill focuses on Harness action testing. If the charm is migrating to Scenario entirely, the ops-testing-migration skill is more appropriate.

## Common Mistakes

- **Using the `-action` suffix in `run_action()`**: the action name should match `charmcraft.yaml`, not the event name. Use `"backup"`, not `"backup-action"`.
- **Expecting string parameters to be auto-converted**: `run_action()` passes parameters as-is. If the action handler expects an integer, the parameter should be a string (as Juju passes them).
- **Not testing failure paths**: `run_action()` makes it easy to test `event.fail()` with `pytest.raises(ActionFailed)`. Add failure tests if they don't exist.
- **Mixing old and new patterns**: convert all action tests in a file, not just some. Mixing patterns is confusing.
