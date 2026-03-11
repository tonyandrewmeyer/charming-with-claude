# testing-exception-wrapping

## Version
ops 3.5.0

## Type
Feature

## Summary
A new environment variable `SCENARIO_BARE_CHARM_ERRORS` controls whether `ops.testing` wraps charm exceptions in `UncaughtCharmError` or raises them bare, making test debugging easier.

## Before
```python
import ops
from ops import testing

ctx = testing.Context(MyCharm)
# When the charm raised an exception, ops.testing wrapped it in
# UncaughtCharmError, making it harder to see the original traceback
# and match on specific exception types in tests.
try:
    ctx.run(ctx.on.start(), testing.State())
except testing.UncaughtCharmError as e:
    # Had to unwrap to get the original exception
    original = e.__cause__
```

## After
```python
import os
os.environ["SCENARIO_BARE_CHARM_ERRORS"] = "true"

import ops
from ops import testing

ctx = testing.Context(MyCharm)
# Now the original exception propagates directly
with pytest.raises(MySpecificError):
    ctx.run(ctx.on.start(), testing.State())
```

Or set in `tox.ini` / `pyproject.toml`:
```ini
[testenv:unit]
setenv =
    SCENARIO_BARE_CHARM_ERRORS=true
```

## Why Upgrade
- Cleaner test assertions: `pytest.raises(SpecificError)` works directly without unwrapping.
- Better tracebacks: the original exception's traceback is shown directly, not nested inside `UncaughtCharmError`.
- Aligns with standard Python testing patterns.

## Complexity
Trivial

## Detection
Search for `UncaughtCharmError` in test files, or for patterns like `e.__cause__` used to unwrap testing exceptions. Also check if tests catch broad exceptions when testing error paths.

## Exemplar Charms
No downstream charm adoption found. The env var is currently used only within `canonical/operator` itself (its own tox.ini and test files).

- [canonical/job-manager](https://github.com/canonical/job-manager) (charm/tests/unit/test_charm.py) -- Aware of the `UncaughtCharmError` wrapping behaviour but works around it manually rather than using the env var. A good candidate for adoption.

## Pitfalls
- This is controlled by an environment variable, not a Context parameter. Set it in `tox.ini` or `conftest.py` to apply it consistently across all tests.
- When enabled, tests that previously caught `UncaughtCharmError` will need to be updated to catch the actual exception type.
- The variable name is `SCENARIO_BARE_CHARM_ERRORS` (a legacy name from the ops-scenario era).
