# hook-commands-api

## Version
ops 3.4.0

## Type
Feature

## Summary
A new low-level `ops.hookcmds` module provides direct Python access to Juju hook commands (`relation-get`, `config-get`, `secret-get`, etc.) without going through the ops framework's model layer.

## Before
```python
import subprocess
import json

# The only way to call hook commands directly was via subprocess
result = subprocess.run(
    ["relation-get", "--format=json", "-r", str(relation_id), "-", unit_name],
    capture_output=True, text=True,
)
data = json.loads(result.stdout)
```

Or through the ops framework (which calls the hook commands internally):
```python
# Most charms use the ops model layer, which is the recommended approach
data = event.relation.data[event.unit]
```

## After
```python
import ops.hookcmds

# Direct access to hook commands with proper Python types
data = ops.hookcmds.relation_get(relation_id=rel_id, unit_name=unit)
```

## Why Upgrade
- **For library authors and advanced use cases**: provides a clean Python API for hook commands without subprocess management.
- **Internal improvement**: the ops framework itself now uses `ops.hookcmds` internally (refactored in 3.4.0), making the codebase cleaner.
- **Not for typical charms**: most charms should continue using the high-level ops model API (`self.model`, `event.relation`, etc.).

## Complexity
Trivial (but niche applicability)

## Detection
Search for `subprocess.run` or `subprocess.check_output` calls to Juju hook commands (`relation-get`, `config-get`, `status-set`, `secret-get`, etc.) in charm code or charm libraries.

## Exemplar Charms
*To be populated in Phase 2.*

## Pitfalls
- **Not for typical charms**: the high-level ops model API (`self.model`, `self.config`, `event.relation.data`) is the recommended interface. `ops.hookcmds` is for library authors, tools, and advanced use cases.
- **Not covered by semver**: Canonical reserves the right to make breaking changes to `ops.hookcmds` within the 3.x series. Do not depend on it for stable charm APIs.
- Only callable during hook execution (same constraint as the hook commands themselves).
- The module provides individual functions corresponding to each Juju hook command: `relation_get`, `relation_set`, `config_get`, `status_set`, `secret_get`, etc.
- All commands raise `ops.hookcmds.Error` (wrapping `subprocess.CalledProcessError`) on non-zero exit.
