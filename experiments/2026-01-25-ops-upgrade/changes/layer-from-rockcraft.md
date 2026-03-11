# layer-from-rockcraft

## Version
ops 2.23.0

## Type
Feature

## Summary
A new `testing.layer_from_rockcraft()` function generates a Pebble `Layer` from a `rockcraft.yaml` file, eliminating the need to duplicate service definitions in tests.

## Before
```python
import ops
from ops import testing

# Tests had to manually define layers matching the rockcraft.yaml services
container = testing.Container(
    name="workload",
    layers={
        "workload": ops.pebble.Layer({
            "services": {
                "myapp": {
                    "command": "/bin/myapp --config /etc/myapp/config.yaml",
                    "override": "replace",
                    "startup": "enabled",
                }
            }
        }),
    },
)
```

## After
```python
import pathlib

from ops import testing

# Generate the layer directly from rockcraft.yaml
layer = testing.layer_from_rockcraft(pathlib.Path("rockcraft.yaml"))
container = testing.Container(
    name="workload",
    layers={"rock": layer},
)
```

## Why Upgrade
- **DRY**: service definitions live in `rockcraft.yaml` only, not duplicated in tests.
- **Consistency**: tests always match the actual rock definition.
- **Maintenance**: when `rockcraft.yaml` changes, tests automatically pick up the new service definitions.

## Complexity
Moderate

## Detection
Look for test files that manually construct `ops.pebble.Layer` objects with service definitions that duplicate what's in the charm's `rockcraft.yaml`. Also search for `layers={` in `testing.Container` constructor calls.

## Exemplar Charms
No external charm adoption found. The only references are within the ops repository itself:
- [canonical/operator](https://github.com/canonical/operator) (docs/howto/manage-containers/manage-the-workload-container.md) -- Official documentation example showing the recommended test pattern.
- [canonical/operator](https://github.com/canonical/operator) (testing/tests/test_e2e/test_state.py) -- Parametrised tests covering empty layers, services, and checks.
- [PR #1831](https://github.com/canonical/operator/pull/1831) -- The original implementation PR.

**Notable**: zero adoption in production charms despite being available since ops 2.23.0. This makes it an excellent candidate for the experiment — measuring whether AI can successfully introduce a feature with no real-world exemplars to reference.

## Pitfalls
- The function reads the `rockcraft.yaml` file at the specified path, so the path must be correct relative to where tests run (usually the charm project root). Raises `ValueError` if the file does not exist.
- Extracts `services`, `checks`, `summary`, and `description` from `rockcraft.yaml`. Ignores all other rockcraft fields (name, base, parts, platforms, etc.).
- The generated layer is a starting point — tests typically assert that the charm adds its own configuration layer on top.
- Only useful for K8s charms that have a `rockcraft.yaml` alongside their charm code.
