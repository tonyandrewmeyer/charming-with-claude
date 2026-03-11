# Skill: Adopt layer_from_rockcraft in Tests

Replace manually constructed Pebble layers in unit tests with `testing.layer_from_rockcraft()` to keep tests in sync with `rockcraft.yaml`.

## When to Use

Use this when a K8s charm's unit tests manually construct `ops.pebble.Layer` objects with service definitions that duplicate what's in the charm's `rockcraft.yaml`.

## Prerequisites

- ops >= 2.23.0
- The charm is a K8s charm with a `rockcraft.yaml` file
- The charm has unit tests that construct Pebble layers for `testing.Container`

## Step 1: Identify Manual Layer Construction

Search test files for:
- `ops.pebble.Layer({` or `pebble.Layer({`
- `layers={` in `testing.Container()` constructor calls
- Service definitions in test code that duplicate `rockcraft.yaml`

## Step 2: Replace with `layer_from_rockcraft`

```python
# Before:
import ops
from ops import testing

container = testing.Container(
    name="workload",
    layers={
        "rock": ops.pebble.Layer({
            "services": {
                "myapp": {
                    "command": "/bin/myapp serve",
                    "override": "replace",
                    "startup": "enabled",
                    "environment": {"PORT": "8080"},
                }
            }
        }),
    },
)

# After:
from ops import testing

rock_layer = testing.layer_from_rockcraft("rockcraft.yaml")
container = testing.Container(
    name="workload",
    layers={"rock": rock_layer},
)
```

### Path Resolution

The path is relative to where the tests are run (typically the project root). Common patterns:
- `testing.layer_from_rockcraft("rockcraft.yaml")` — rock in the project root
- `testing.layer_from_rockcraft("../rock/rockcraft.yaml")` — rock in a sibling directory

### What Gets Extracted

The function reads `summary`, `description`, `services`, and `checks` from the rockcraft.yaml and constructs a `pebble.Layer`. All other rockcraft fields (name, base, parts, platforms) are ignored.

## Step 3: Keep Charm-Specific Layers Separate

Tests typically need two layers:
1. **The rock layer** (from `layer_from_rockcraft`) — the base services from the rock
2. **The charm's config layer** — what the charm adds on top (environment overrides, etc.)

The test should assert that the charm correctly adds its config layer:

```python
def test_pebble_ready():
    ctx = testing.Context(MyCharm)
    rock_layer = testing.layer_from_rockcraft("rockcraft.yaml")
    container = testing.Container("workload", layers={"rock": rock_layer})
    state_in = testing.State(containers={container})

    state_out = ctx.run(ctx.on.pebble_ready(container), state_in)

    out_container = state_out.get_container("workload")
    assert len(out_container.layers) == 2  # rock + charm config
    plan = out_container.plan
    assert plan.services["myapp"].environment["CUSTOM_VAR"] == "expected"
```

## Step 4: Verify

1. Run unit tests — they should pass with identical behaviour.
2. Review the diff — the test should be simpler, with the duplicated service definitions removed.

## Exemplar Charms

No production charm has adopted this yet. Best references:
- **[ops documentation](https://github.com/canonical/operator/blob/main/docs/howto/manage-containers/manage-the-workload-container.md)** — official how-to example.
- **[ops test suite](https://github.com/canonical/operator/blob/main/testing/tests/test_e2e/test_state.py)** — `test_layer_from_rockcraft` parametrised tests.

## Common Mistakes

- Don't remove layers that the charm adds *on top of* the rock layer — only replace the base rock layer duplication.
- Don't use this for charms that don't have a `rockcraft.yaml` (e.g. charms that use a third-party image).
- Make sure the path to `rockcraft.yaml` is correct relative to the test runner's working directory.
