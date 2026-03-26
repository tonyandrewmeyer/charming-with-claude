# Skill: Adopt ops[tracing]

Add first-party charm tracing via `ops[tracing]`, or migrate from the community `charm_tracing` library.

## When to Use

Use this when:
- A charm uses the community `charm_tracing` / `charms.tempo_k8s.v2.tracing` library and should migrate to the first-party `ops[tracing]`.
- A charm participates in the observability stack and should add tracing support.

## Prerequisites

- ops >= 2.21.0
- The charm has (or should have) a `tracing` relation providing an OTLP endpoint (typically backed by Tempo)

## Step 1: Assess Current State

Determine which scenario applies:

### Scenario A: Migrating from community `charm_tracing`

Search for:
- `from charms.tempo_k8s` imports
- `charm_tracing` or `trace_charm` decorators
- `TracingEndpointRequirer` or similar classes
- Charm library files in `lib/charms/tempo_k8s/`

### Scenario B: Adding tracing to a charm that doesn't have it

Check:
- Does the charm have a `tracing` relation in `charmcraft.yaml` / `metadata.yaml`? If not, one needs adding.
- Is the charm in the observability ecosystem or would it benefit from tracing?

## Step 2: Update Dependencies

### Add ops[tracing]

In `pyproject.toml`:
```toml
[project]
dependencies = [
    "ops[tracing]>=2.21",
]
```

Or in `requirements.txt`:
```
ops[tracing]>=2.21
```

### Remove community library (Scenario A only)

1. Delete the charm library files: `lib/charms/tempo_k8s/`
2. Remove any `charmcraft fetch-lib` configuration for the tracing library
3. Remove the library from `tox.ini` fetch commands if present

## Step 3: Update charmcraft.yaml (if needed)

Ensure the charm declares the tracing relation. The relation name must match what you pass to `ops.tracing.setup()`.

```yaml
requires:
  tracing:
    interface: tracing
```

If the charm already has this relation from the community library, no change is needed — just verify the relation name.

## Step 4: Update the Charm Code

### Scenario A: Migration from charm_tracing

```python
# Before:
from charms.tempo_k8s.v2.tracing import charm_tracing, trace_charm

@trace_charm(
    tracing_endpoint="tracing_endpoint",
    extra_types=[SomeHelper, AnotherClass],
)
class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.tracing = TracingEndpointRequirer(self, relation_name="tracing")
        # ...
```

```python
# After:
import ops.tracing

class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        ops.tracing.setup(self, relation_name="tracing")
        # ...
```

Key differences:
- No decorator on the charm class.
- No `TracingEndpointRequirer` — `ops.tracing.setup()` handles relation watching internally.
- No `extra_types` parameter — `ops[tracing]` traces at the charm level.
- The `relation_name` must match the relation in `charmcraft.yaml`.

### Scenario B: Adding tracing from scratch

```python
import ops
import ops.tracing


class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        ops.tracing.setup(self, relation_name="tracing")
        # ... rest of __init__ ...
```

That's it. `ops.tracing.setup()` registers the necessary event observers and handles OTLP export when a tracing relation is established.

## Step 5: Clean Up

### Remove community library remnants (Scenario A)

- Delete `lib/charms/tempo_k8s/` directory
- Remove any `fetch-lib` entries for `charms.tempo_k8s.v2.tracing` from CI or `charmcraft.yaml`
- Remove `charm_tracing` / `trace_charm` imports from all files
- Remove any `@trace_charm` decorators
- Remove `TracingEndpointRequirer` instantiation

### Check for manual span creation

If the charm creates custom OpenTelemetry spans, those continue to work with `ops[tracing]` — the underlying instrumentation is compatible. No changes needed for custom spans.

## Step 6: Update Tests

### Unit tests

If tests mock or patch `charm_tracing` components, update them:

```python
# Before:
@patch("charm.TracingEndpointRequirer")
def test_something(mock_tracing):
    ...

# After — ops.tracing.setup() doesn't need mocking in most cases.
# If the test needs to avoid tracing overhead:
def test_something():
    ctx = testing.Context(MyCharm)
    # ops.testing handles tracing setup automatically
    ...
```

### Integration tests

If integration tests check tracing output, verify they still work. The trace format from `ops[tracing]` should be compatible, but endpoint configuration may differ.

## Step 7: Verify

1. Run `tox -e lint` — ensure no remaining imports from the community library.
2. Run `tox -e unit` — all tests should pass.
3. Search for any remaining references to `charm_tracing`, `trace_charm`, `TracingEndpointRequirer`, or `charms.tempo_k8s`.
4. Review the diff:
   - Community library files should be deleted.
   - Charm code should be simpler (fewer imports, no decorator, no manual requirer).
   - `charmcraft.yaml` should be unchanged or minimally changed.

## Common Mistakes

- **Forgetting to remove the charm library directory** (`lib/charms/tempo_k8s/`): the old library will still be importable and may conflict.
- **Mismatched relation names**: the `relation_name` in `ops.tracing.setup()` must exactly match the relation name in `charmcraft.yaml`.
- **Not updating test dependencies**: ensure `ops[tracing]` is in the test dependency group too, not just the main dependencies.
- **Removing custom spans**: if the charm creates custom OpenTelemetry spans for specific operations, keep those — they're orthogonal to the charm-level tracing setup.
- **Confusing charms that *provide* tracing with charms that *use* tracing**: Tempo itself provides the tracing endpoint. Most charms *require* it. Don't add `ops.tracing.setup()` to a charm that provides the OTLP endpoint.
