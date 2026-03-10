# Skill: Adopt SCENARIO_BARE_CHARM_ERRORS

Enable bare exception propagation in `ops.testing` so that charm exceptions surface directly instead of being wrapped in `UncaughtCharmError`.

## When to Use

Use this when a charm has unit tests using `ops.testing` and you want cleaner tracebacks and more natural exception assertions.

## Prerequisites

- ops >= 3.5.0
- The charm has unit tests using `ops.testing`

## Step 1: Check Current Exception Handling

Search test files for:
- `UncaughtCharmError` — tests catching the wrapper
- `e.__cause__` — tests unwrapping to get the original exception
- Broad `except Exception` in test code around `ctx.run()` calls

## Step 2: Set the Environment Variable

Add `SCENARIO_BARE_CHARM_ERRORS=true` to the test environment.

### In `tox.ini`:
```ini
[testenv:unit]
setenv =
    SCENARIO_BARE_CHARM_ERRORS=true
```

### Or in `pyproject.toml` (if using pytest directly):
```toml
[tool.pytest.ini_options]
env = [
    "SCENARIO_BARE_CHARM_ERRORS=true",
]
```

## Step 3: Update Affected Tests

### Tests catching UncaughtCharmError

```python
# Before:
from ops.testing import UncaughtCharmError

def test_bad_config():
    ctx = testing.Context(MyCharm)
    with pytest.raises(UncaughtCharmError) as exc_info:
        ctx.run(ctx.on.config_changed(), state)
    assert isinstance(exc_info.value.__cause__, ValueError)

# After:
def test_bad_config():
    ctx = testing.Context(MyCharm)
    with pytest.raises(ValueError, match="Invalid config"):
        ctx.run(ctx.on.config_changed(), state)
```

### Tests that don't check exceptions

Tests that don't catch `UncaughtCharmError` are unaffected — they'll just get better tracebacks when things go wrong.

## Step 4: Verify

1. Run `tox -e unit` — all tests should pass.
2. Intentionally break something and verify the traceback is cleaner (shows the original exception directly).

## Exemplar Charms

No downstream charm has adopted this yet. Reference:
- **[canonical/operator](https://github.com/canonical/operator)** (tox.ini) — ops' own tests use this env var.

## Common Mistakes

- Don't set this in production code — it's a testing-only environment variable.
- Don't forget to update tests that explicitly catch `UncaughtCharmError` — they'll start failing because the exception type changes.
- The variable name is `SCENARIO_BARE_CHARM_ERRORS` (legacy name from the ops-scenario era) — don't misspell it.
