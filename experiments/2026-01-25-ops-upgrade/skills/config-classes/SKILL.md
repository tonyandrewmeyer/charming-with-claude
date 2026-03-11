# Skill: Adopt Config Classes

Replace raw `self.config` dictionary access with typed Python classes using `CharmBase.load_config()`.

## When to Use

Use this when a charm accesses config via `self.config["key"]` or `self.config.get("key")` and would benefit from type safety, validation, and IDE support.

## Prerequisites

- ops >= 2.23.0
- The charm has config options defined in `charmcraft.yaml` (or `config.yaml`)

## Step 1: Audit Current Config Usage

1. Read the charm's config definition in `charmcraft.yaml` to understand all config options and their types.
2. Search the charm code for all config access patterns:
   - `self.config["..."]`
   - `self.config.get("...")`
   - `self.config[...]` with variable keys
3. Note any manual validation (type checks, range checks, enum validation).

## Step 2: Define the Config Class

Create a config class in `src/config.py` (or inline if the charm is small).

### Option A: Dataclass (no extra dependencies)

```python
import dataclasses


@dataclasses.dataclass(frozen=True)
class MyCharmConfig:
    log_level: str = "info"
    port: int = 8080
    enable_tls: bool = False

    def __post_init__(self):
        """Validate config values. Raise ValueError for invalid config."""
        valid_levels = {"info", "debug", "warning", "error", "critical"}
        if self.log_level.lower() not in valid_levels:
            raise ValueError(
                f"Invalid log level: '{self.log_level}'. "
                f"Valid values are: {', '.join(sorted(valid_levels))}."
            )
```

### Option B: Pydantic BaseModel (richer validation, requires pydantic dependency)

```python
import pydantic


class MyCharmConfig(pydantic.BaseModel):
    log_level: str = "info"
    port: int = pydantic.Field(default=8080, ge=1, le=65535)
    enable_tls: bool = False

    @pydantic.field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"info", "debug", "warning", "error", "critical"}
        if v.lower() not in valid:
            raise ValueError(f"Invalid log level: '{v}'")
        return v.lower()
```

### Field Naming Rules

- Juju config names use dashes: `log-level`
- Python field names use underscores: `log_level`
- The conversion is automatic — just use underscores in the class.
- For names that don't follow this pattern, use aliases:
  ```python
  # Dataclass:
  workload_class: str = dataclasses.field(metadata={"alias": "class"})
  # Pydantic:
  workload_class: str = pydantic.Field(alias="class")
  ```

## Step 3: Update the Charm

### Loading config

The standard pattern is to load config in `__init__` with `errors="blocked"`:

```python
from config import MyCharmConfig


class MyCharm(ops.CharmBase):
    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self.typed_config = self.load_config(MyCharmConfig, errors="blocked")
        # ...event observers...
```

With `errors="blocked"`, if the config is invalid:
1. The unit status is set to `BlockedStatus("Invalid config: ...")`.
2. The hook exits cleanly (Juju won't retry).
3. The charm should handle this in `collect_unit_status` or check the status before proceeding.

### Replacing config access

```python
# Before:
log_level = self.config.get("log-level", "info")
port = int(self.config["port"])

# After:
log_level = self.typed_config.log_level
port = self.typed_config.port
```

### Removing manual validation

Any validation that's now handled by the config class can be removed from the charm code.

## Step 4: Update Tests

If tests set config values via `testing.State(config={...})`, those continue to work — no test changes needed for the state setup. But assertions that check for manual validation behaviour (e.g. checking that the charm sets BlockedStatus on bad config) should verify the new error path.

```python
def test_invalid_config():
    ctx = testing.Context(MyCharm)
    state_out = ctx.run(
        ctx.on.config_changed(),
        testing.State(config={"log-level": "invalid"}),
    )
    assert isinstance(state_out.unit_status, testing.BlockedStatus)
```

## Step 5: Verify

1. Run `tox -e lint` — ensure the new module is properly imported.
2. Run `tox -e unit` — all tests should pass.
3. Review the diff — it should be focused on config access patterns. No unrelated changes.

## Exemplar Charms

- **[cve-scanner-operator](https://github.com/canonical/cve-scanner-operator)** — Pydantic with rich Field constraints, `errors="blocked"`, separate `src/config.py`.
- **[conserver-charm](https://github.com/canonical/conserver-charm)** — Clean minimal Pydantic example.
- **[forgejo-k8s-operator](https://github.com/canonical/forgejo-k8s-operator)** — Dataclass approach with `__post_init__` validation.

## Common Mistakes

- Don't partially convert — if adopting `load_config`, convert *all* `self.config` access.
- Don't forget to add `pydantic` to dependencies if using Pydantic.
- Don't add validation that changes behaviour — the goal is to replace raw access with typed access, not to add new restrictions.
- Don't put the config class in the charm module if it's complex — use a separate `src/config.py`.
