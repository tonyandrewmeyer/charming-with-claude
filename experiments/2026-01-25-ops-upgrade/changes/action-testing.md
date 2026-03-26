# action-testing

## Version
ops 2.9.0

## Type
Feature

## Summary
New action testing API: `Harness.run_action()` returns an `ActionOutput` object (or raises `ActionFailed`), replacing the older pattern of manually triggering action events and inspecting results via `Harness._get_backend()`.

## Before
```python
from ops.testing import Harness

def test_backup_action(harness: Harness):
    harness.begin()
    # Awkward: trigger action event manually
    action_event = harness.charm.on.backup_action
    harness.charm.on.backup_action.emit(params={"target": "/data"})
    # No clean way to get action results without backend hacks
```

## After
```python
from ops.testing import Harness

def test_backup_action(harness: Harness):
    harness.begin()
    output = harness.run_action("backup", {"target": "/data"})
    assert output.results["backup-file"] == "/data/backup.tar.gz"

def test_backup_action_fails(harness: Harness):
    harness.begin()
    try:
        harness.run_action("backup", {"target": "/nonexistent"})
        assert False, "Should have failed"
    except ActionFailed as e:
        assert "not found" in str(e)
```

## Why Upgrade
- **Clean API**: `run_action()` returns results directly instead of requiring backend introspection.
- **Error handling**: `ActionFailed` exception provides a clean pattern for testing action failure paths.
- **Realistic**: more closely mirrors how actions actually execute in Juju.
- **Readable tests**: test code clearly expresses intent.

## Complexity
Moderate — requires updating existing action tests to use the new API. Straightforward but potentially many test files to update.

## Detection
Search for action testing patterns in test files: manual action event emission, `_get_backend()` calls for action results, or any action test that doesn't use `run_action()`.

## Exemplar Charms
- Most actively maintained charms have migrated to `run_action()` by now.
- Search for `run_action(` in test files across canonical/ repos.

## Pitfalls
- The old pattern still works but is less maintainable — this isn't a breaking change, just a strong improvement.
- `run_action()` takes the action name without the `-action` suffix (e.g. `"backup"`, not `"backup-action"`).
- Action parameters use the Juju naming convention (dashes), not Python (underscores).
- If the charm is migrating to `ops.testing` (Scenario), the action testing API there is different again — consider which migration to prioritise.
