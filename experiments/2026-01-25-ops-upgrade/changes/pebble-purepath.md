# pebble-purepath

## Version
ops 3.4.0

## Type
Improvement

## Summary
PebbleClient file methods (`push`, `pull`, `list_files`, `make_dir`, `remove_path`) now also accept `pathlib.PurePath` in addition to `str` for path arguments.

## Before
```python
from pathlib import PurePosixPath

container = self.unit.get_container("workload")
config_path = PurePosixPath("/etc/myapp/config.yaml")

# Had to convert PurePath to str explicitly
container.push(str(config_path), config_content)
pulled = container.pull(str(config_path))
container.list_files(str(config_path.parent))
container.make_dir(str(config_path.parent), make_parents=True)
container.remove_path(str(config_path))
```

## After
```python
from pathlib import PurePosixPath

container = self.unit.get_container("workload")
config_path = PurePosixPath("/etc/myapp/config.yaml")

# PurePath objects accepted directly
container.push(config_path, config_content)
pulled = container.pull(config_path)
container.list_files(config_path.parent)
container.make_dir(config_path.parent, make_parents=True)
container.remove_path(config_path)
```

## Why Upgrade
Cleaner code when using `pathlib` for container paths. Removes the need for `str()` conversions, making path manipulation more natural and consistent with standard Python file APIs.

## Complexity
Trivial

## Detection
Search for `str(` calls wrapping path variables in arguments to Pebble container methods: `container.push(str(`, `container.pull(str(`, etc. Also look for charms that use `pathlib` for container paths.

## Exemplar Charms
*To be populated in Phase 2.*

## Pitfalls
- Only applies to K8s charms that use Pebble containers; machine charms are unaffected.
- The change is backwards-compatible — existing `str` paths still work. This is a code quality improvement, not a required migration.
- Only `PurePath`/`PurePosixPath` are useful here (container paths are always POSIX). Using `pathlib.Path` or `PureWindowsPath` would be inappropriate.
