# action-classes

## Version
ops 2.23.0

## Type
Feature

## Summary
Action parameters can now be loaded into Python dataclasses or Pydantic models via `ActionEvent.load_params()`, replacing raw dictionary access to `event.params`.

## Before
```python
import ops

class MyCharm(ops.CharmBase):
    def _on_backup_action(self, event: ops.ActionEvent):
        # Raw dictionary access — no type safety
        target = event.params.get("target", "/data")
        compress = event.params.get("compress", True)
        max_size = int(event.params.get("max-size", 0))

        if not target.startswith("/"):
            event.fail("Target must be an absolute path")
            return
```

## After
```python
import dataclasses

import ops


@dataclasses.dataclass(frozen=True, kw_only=True)
class BackupParams:
    target: str = "/data"
    compress: bool = True
    max_size: int = 0


class MyCharm(ops.CharmBase):
    def _on_backup_action(self, event: ops.ActionEvent):
        # Typed, validated parameters — dashes converted to underscores automatically
        params = event.load_params(BackupParams)
        # params.target, params.compress, params.max_size are typed
```

Or with Pydantic:
```python
from pydantic import BaseModel, Field

import ops


class BackupParams(BaseModel):
    target: str = Field(default="/data", pattern=r"^/")
    compress: bool = True
    max_size: int = Field(default=0, ge=0)


class MyCharm(ops.CharmBase):
    def _on_backup_action(self, event: ops.ActionEvent):
        # With errors='fail', invalid params call event.fail() automatically
        params = event.load_params(BackupParams, errors="fail")
```

## Why Upgrade
- **Type safety**: action parameters are properly typed without manual conversion.
- **Validation**: Pydantic models can enforce constraints declaratively.
- **IDE support**: autocompletion and type checking work with parameter fields.
- **Dash-to-underscore**: Juju action parameter names use dashes, class fields use underscores. Conversion is automatic.
- **Error handling**: `errors='fail'` automatically calls `event.fail()` on validation failure, `errors='raise'` raises an exception.

## Complexity
Moderate

## Detection
Search for `event.params[` or `event.params.get(` in charm code. Charms with actions that take parameters benefit most.

## Exemplar Charms
- [canonical/ubuntu-autopkgtest-operators](https://github.com/canonical/ubuntu-autopkgtest-operators) (charms/autopkgtest-dispatcher-operator/src/action_types.py) -- Best production exemplar: Pydantic `BaseModel` with `Field(description=)`, `Enum` field types, `errors="fail"`. Separate `action_types.py` module. 3 actions with typed params.
- [canonical/ubuntu-autopkgtest-operators](https://github.com/canonical/ubuntu-autopkgtest-operators) (charms/autopkgtest-janitor-operator/src/action_types.py) -- Sibling charm, simpler Pydantic models, same pattern.
- [canonical/operator](https://github.com/canonical/operator) (examples/k8s-4-action/src/charm.py) -- Official tutorial example using `dataclasses.dataclass(frozen=True, kw_only=True)` with `errors="fail"`. The canonical introductory reference.

**Notable**: adoption is still early — only ~2 production charms found. Every usage passes `errors="fail"` explicitly. The well-known observability/data charms (tempo-k8s, grafana-k8s, mysql-k8s, etc.) have not adopted this yet, making them good candidates for the experiment's target charms.

## Pitfalls
- Similar to config classes: field names use underscores where Juju uses dashes.
- The `errors` parameter differs from config: `'raise'` (default) raises, `'fail'` calls `event.fail()`.
- Pydantic is optional — standard `dataclasses` work too.
- If using Pydantic, ensure `pydantic` is in the charm's dependencies.
