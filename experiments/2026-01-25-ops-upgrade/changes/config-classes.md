# config-classes

## Version
ops 2.23.0

## Type
Feature

## Summary
Charm config options can now be defined as Python dataclasses or Pydantic models, loaded via `CharmBase.load_config()`, replacing raw dictionary access to `self.config`.

## Before
```python
import ops

class MyCharm(ops.CharmBase):
    def _on_config_changed(self, event: ops.ConfigChangedEvent):
        # Raw dictionary access — no type safety, manual validation
        log_level = self.config.get("log-level", "info")
        port = int(self.config["port"])  # manual type conversion
        enable_tls = self.config.get("enable-tls", False)

        if not isinstance(port, int) or port < 1 or port > 65535:
            self.unit.status = ops.BlockedStatus("Invalid port")
            return
```

## After
```python
import dataclasses

import ops


@dataclasses.dataclass(frozen=True)
class MyConfig:
    log_level: str = "info"
    port: int = 8080
    enable_tls: bool = False

    def __post_init__(self):
        valid_levels = {"info", "debug", "warning", "error", "critical"}
        if self.log_level.lower() not in valid_levels:
            raise ValueError(
                f"Invalid log level: '{self.log_level}'. "
                f"Valid values are: {', '.join(valid_levels)}."
            )


class MyCharm(ops.CharmBase):
    def _on_config_changed(self, event: ops.ConfigChangedEvent):
        # Typed, validated config — dashes converted to underscores automatically
        config = self.load_config(MyConfig, errors="blocked")
        # config.log_level, config.port, config.enable_tls are typed
```

Or with Pydantic for richer validation:
```python
from pydantic import BaseModel, Field

import ops


class MyConfig(BaseModel):
    log_level: str = "info"
    port: int = Field(default=8080, ge=1, le=65535)
    enable_tls: bool = False


class MyCharm(ops.CharmBase):
    def _on_config_changed(self, event: ops.ConfigChangedEvent):
        # With errors='blocked', invalid config sets BlockedStatus automatically
        config = self.load_config(MyConfig, errors="blocked")
```

## Why Upgrade
- **Type safety**: config values are properly typed without manual conversion.
- **Validation**: Pydantic models can enforce constraints (ranges, patterns, etc.) declaratively.
- **IDE support**: autocompletion and type checking work with config fields.
- **Dash-to-underscore**: Juju config option names use dashes (`log-level`), but the class fields use underscores (`log_level`). The conversion is automatic.
- **Error handling**: `errors='blocked'` automatically sets `BlockedStatus` on validation failure, and `errors='raise'` raises an exception.

## Complexity
Moderate

## Detection
Search for direct access to `self.config[` or `self.config.get(` in charm code. Charms with multiple config options benefit most.

## Exemplar Charms
- [canonical/cve-scanner-operator](https://github.com/canonical/cve-scanner-operator) (src/config.py) -- Best overall: Pydantic with `Field(alias=, description=, gt=, le=)` constraints, `SecretStr`, Enum log levels, `errors="blocked"`. Separate config module.
- [canonical/conserver-charm](https://github.com/canonical/conserver-charm) (src/config.py) -- Cleanest minimal example: Pydantic with `errors="blocked"` in `__init__`, stores as `self.typed_config`.
- [canonical/microovn-operator](https://github.com/canonical/microovn-operator) (src/config.py) -- Good Pydantic v2 `field_validator` pattern for custom risk/channel validation.
- [canonical/auditd-operator](https://github.com/canonical/auditd-operator) (src/workloads.py) -- Pydantic v2 with manual try/except instead of `errors=` for more control over error flow.
- [canonical/forgejo-k8s-operator](https://github.com/canonical/forgejo-k8s-operator) (src/charm.py) -- The only exemplar using `dataclasses` instead of Pydantic, with `__post_init__` for validation.

**Notable**: nearly all production charms use Pydantic, not dataclasses. The common pattern is `self.typed_config = self.load_config(MyConfig, errors="blocked")` in `__init__`, with the config class in a separate `src/config.py` module.

## Pitfalls
- The config class field names must use underscores where the Juju config uses dashes (`log-level` → `log_level`). The conversion is automatic.
- Pydantic is optional — standard `dataclasses` work too, but without validation beyond type coercion.
- If using Pydantic, ensure `pydantic` is in the charm's dependencies.
- The `errors` parameter controls behaviour on invalid config: `'raise'` (default) raises an exception, `'blocked'` sets `BlockedStatus`.
- Field aliases (via Pydantic's `alias` or dataclass `metadata`) are supported for cases where the Juju name doesn't follow the dash-to-underscore pattern.
