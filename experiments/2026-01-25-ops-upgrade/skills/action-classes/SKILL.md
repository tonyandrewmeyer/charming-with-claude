# Skill: Adopt Action Classes

Replace raw `event.params` dictionary access with typed Python classes using `ActionEvent.load_params()`.

## When to Use

Use this when a charm has actions with parameters accessed via `event.params["key"]` or `event.params.get("key")`.

## Prerequisites

- ops >= 2.23.0
- The charm has actions defined in `charmcraft.yaml` (or `actions.yaml`)

## Step 1: Audit Current Action Usage

1. Read the charm's action definitions to understand all actions and their parameters.
2. Search charm code for action handlers (methods observing `self.on.*_action`).
3. For each handler, note how `event.params` is accessed and any manual validation.

## Step 2: Define Action Parameter Classes

Create a class for each action's parameters. Use `@dataclasses.dataclass(frozen=True, kw_only=True)`.

```python
import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class BackupParams:
    """Parameters for the backup action."""

    target: str = "/data"
    compress: bool = True
    max_size: int = 0
```

Or with Pydantic for richer validation:

```python
import pydantic


class BackupParams(pydantic.BaseModel):
    target: str = pydantic.Field(default="/data", description="Backup target path.")
    compress: bool = True
    max_size: int = pydantic.Field(default=0, ge=0, description="Max size in MB.")
```

### Field Naming

Same rules as config: dashes become underscores automatically. Use aliases for exceptions.

### Where to Put Them

For charms with several actions, create a separate `src/action_types.py` module. For one or two simple actions, inline in the charm module is fine.

## Step 3: Update Action Handlers

```python
# Before:
def _on_backup_action(self, event: ops.ActionEvent):
    target = event.params.get("target", "/data")
    compress = event.params.get("compress", True)
    if not target.startswith("/"):
        event.fail("Target must be an absolute path")
        return
    # ...

# After:
def _on_backup_action(self, event: ops.ActionEvent):
    params = event.load_params(BackupParams, errors="fail")
    # params is None if validation failed (event.fail() already called)
    # ...use params.target, params.compress, params.max_size...
```

**Key**: always use `errors="fail"` for actions. This automatically calls `event.fail()` with the validation error message if parameters are invalid.

## Step 4: Update Tests

Action tests that set params via the testing framework should continue to work:

```python
def test_backup_action():
    ctx = testing.Context(MyCharm)
    state_out = ctx.run(
        ctx.on.action("backup", params={"target": "/data", "compress": True}),
        testing.State(),
    )
```

## Step 5: Verify

1. Run linting and unit tests.
2. Check that `juju run <unit> <action> --param key=value` still works as expected.

## Exemplar Charms

- **[ubuntu-autopkgtest-operators](https://github.com/canonical/ubuntu-autopkgtest-operators)** (charms/autopkgtest-dispatcher-operator) — Pydantic with `Field(description=)`, Enum types, `errors="fail"`. Separate `src/action_types.py`.
- **[canonical/operator](https://github.com/canonical/operator)** (examples/k8s-4-action) — Official tutorial example with dataclasses.

## Common Mistakes

- Don't forget `errors="fail"` — the default `errors="raise"` will cause an unhandled exception.
- Don't add params classes for actions that take no parameters.
- Don't change action result keys or formats — only the *input* parameter handling is changing.
