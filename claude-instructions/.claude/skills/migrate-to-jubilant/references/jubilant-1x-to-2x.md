# pytest-jubilant 1.x → 2.0 Migration

Complete mapping of renames and behaviour changes in `pytest-jubilant` 2.0.

Released 2026-03-29. Pin to `>=2,<3`. The maintainers are committed to semver and do not intend another major version soon.

## Fixture Renames

| 1.x | 2.0 | Notes |
|---|---|---|
| `temp_model_factory` | `juju_factory` | Module-scoped; type-annotate as `pytest_jubilant.JujuFactory` |
| `juju` | `juju` | Unchanged; type-annotate as `jubilant.Juju` |

## CLI Option Renames

| 1.x | 2.0 | Notes |
|---|---|---|
| `--model` | `--juju-model` | Sets the model name prefix |
| `--keep-models` | **Removed** | Use `--no-juju-teardown` instead |
| `--no-setup` | `--no-juju-setup` | Skips `@pytest.mark.juju_setup` tests and model creation |
| `--no-teardown` | `--no-juju-teardown` | Skips `@pytest.mark.juju_teardown` tests and model destruction |
| `--switch` | `--juju-switch` | Auto-switch to the current test's model |
| `--dump-logs` | `--juju-dump-logs` | Dump `juju debug-log` to `.logs/` (or specified dir) |

### Behaviour change: `--no-juju-teardown`

In 1.x, `--keep-models` only prevented model destruction. In 2.0, `--no-juju-teardown` also **skips tests marked with `@pytest.mark.juju_teardown`**, so destructive cleanup tests are not run against the preserved model.

### Behaviour change: `--no-juju-setup`

In 2.0, `--no-juju-setup` both skips `@pytest.mark.juju_setup` tests **and** prevents new model creation. It must be combined with `--juju-model` to specify which existing models to use.

## Marker Renames

| 1.x | 2.0 | Notes |
|---|---|---|
| `@pytest.mark.setup` | `@pytest.mark.juju_setup` | Skipped with `--no-juju-setup` |
| `@pytest.mark.teardown` | `@pytest.mark.juju_teardown` | Skipped with `--no-juju-teardown` |

## Removed Helpers

| 1.x | 2.0 Replacement | Notes |
|---|---|---|
| `pytest_jubilant.pack()` | Pack charm before tests | Use `charmcraft pack` in CI or a Makefile target |
| `pytest_jubilant.get_resources()` | Handle in your own fixtures | Read `charmcraft.yaml` yourself if needed |

These removals reflect the [design philosophy](https://github.com/canonical/pytest-jubilant/blob/main/CONTRIBUTING.md#design-philosophy): `pytest-jubilant` starts where Juju does — at packed charms.

## Log Dumping

| 1.x | 2.0 | Notes |
|---|---|---|
| Logs always dumped on failure | Logs **not** dumped by default | Pass `--juju-dump-logs` to enable |
| N/A | Last 1000 lines to stderr on failure | Always happens if any tests fail |

## Model Naming

| 1.x | 2.0 | Notes |
|---|---|---|
| `test-<randomhex>-<module>` | `jubilant-<randomhex>-<module>` | Default prefix changed |
| `--model <name>` | `--juju-model <prefix>` | Prefix is combined with module name |

In 2.0, each module gets its own model with the naming scheme `<prefix>-<module>`. The `--juju-model` value sets the prefix; the module name is always appended. This means models are not shared between modules even when using `--juju-model`.

## Dependency Update

```toml
# pyproject.toml
[dependency-groups]
integration = [
    "pytest>=9,<10",
    "pytest-jubilant>=2,<3",
]
```

## Typical conftest.py After Migration

In most cases, `conftest.py` becomes very simple because `pytest-jubilant` 2.0 provides the `juju` and `juju_factory` fixtures automatically:

```python
import pathlib
import pytest


@pytest.fixture(scope="module")
def charm():
    """Return the path to the packed charm."""
    return next(pathlib.Path(".").glob("*.charm")).resolve()
```

The `juju` fixture does not need to be defined — it is provided by `pytest-jubilant`.
