# Operator Anti-Patterns: Searchable Code Patterns

Concrete code patterns to grep for when auditing the operator codebase. Each pattern includes the search command, what to look for, and how to distinguish true bugs from false positives.

## Contents
- Mutability: returning internal state
- Mutability: storing without copy
- Mutability: incomplete mutation guards
- Security: file permissions
- Security: error message exposure
- Secrets: invalid flags
- Secrets: caching
- Datetime: missing timezone
- Relations: non-string data
- Relations: post-broken access
- Pebble: string iteration
- Pebble: path handling
- Pebble: temp file cleanup
- Testing: return without copy
- Testing: ops-harness-scenario divergence
- Config: falsy default handling
- Naming: hyphen-underscore mismatch
- Event framework: deferred event snapshots
- Event framework: handle reuse
- Imports: circular dependencies
- Imports: __all__ completeness
- Error handling: wrong exception type
- Error handling: bare dict access
- Juju version: unchecked feature use

---

## Mutability: returning internal state

**Search**: `return self\._` in Python files
**What to check**: Is the returned value a mutable container (dict, list, set)? Could the caller mutate it?
**True bug**: Returns `self._relation_data_raw[id][name]` — caller can corrupt internal state.
**False positive**: Returns `self._data[key]` where values are immutable primitives (str, int, bool).

**Example fix (from commit be090122):**
```python
# Before (bug):
return self._relation_data_raw[relation_id][member_name]
# After (fix):
return self._relation_data_raw[relation_id][member_name].copy()
```

---

## Mutability: storing without copy

**Search**: `self\._\w+ = ` followed by a parameter name (not a constructor call)
**What to check**: Is a dict/list parameter stored directly without copying?
**True bug**: `self._meta = meta` where `meta` is a mutable dict from a caller.
**False positive**: `self._meta = meta` where `meta` is a frozen dataclass or immutable object.

**Example fix (from commit 3f8fb9b9):**
```python
# Before (bug):
self._meta = meta
self._config = config
# After (fix):
self._meta = dict(meta)
self._config = dict(config)
```

---

## Security: file permissions

**Search**: `open(` in files that handle secrets, credentials, or state
**What to check**: Are files created with restrictive permissions (0o600)?
**True bug**: `open(path, 'w')` for files containing secret content in a shared or persistent directory — uses default 0o644.
**False positive**: Opening files for reading, files that contain only non-sensitive data, or files inside a `tempfile.TemporaryDirectory()` (which creates the parent directory with `0o700` permissions, making the files inaccessible to other users regardless of individual file permissions).

**Correct pattern (for persistent or shared directories):**
```python
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode=0o600)
with os.fdopen(fd, 'w', encoding='utf-8') as f:
    f.write(secret_value)
```

**Note**: The `secret_add()` and `secret_set()` functions in `ops/hookcmds/_secret.py` write secret content to temp files, but these are inside a `TemporaryDirectory` (directory permissions `0o700`) and are deleted when the block exits. This was investigated and confirmed as a false positive — see [PR #2377](https://github.com/canonical/operator/pull/2377) (closed without merging).

---

## Security: error message exposure

**Search**: `__str__` and `__repr__` in exception classes
**What to check**: Do error string representations include full command lines, environment variables, or request bodies?
**True bug**: `f"command {self.command} failed"` — exposes full argument list.
**Correct pattern**: `f"command {self.command[0]!r} failed"` — shows only executable name.

---

## ~~Secrets: invalid flags~~ (retracted — false positive)

~~**Search**: `--owner` in secret-related code~~
This anti-pattern was incorrect: `secret-set` does accept `--owner` per the [Juju documentation](https://documentation.ubuntu.com/juju/latest/reference/hook-command/list-of-hook-commands/secret-set/). Do not flag `--owner` usage in `secret-set` as a bug.

---

## Secrets: caching

**Search**: `_secret_cache`, `_cached_secret`, or any dict storing secret content
**What to check**: Is secret content stored after retrieval and reused without re-fetching?
**True bug**: Any local cache of secret content — secrets must always be fetched fresh from Juju.

---

## Datetime: missing timezone

**Search**: `datetime.now()` or `datetime.fromtimestamp(` without `tz=`
**What to check**: Is the result sent to Juju or serialized to RFC 3339?
**Historical bug**: `datetime.datetime.now() + expire` — naive datetime may be misinterpreted. Fixed in [PR #2378](https://github.com/canonical/operator/pull/2378).
**Correct pattern**: `datetime.datetime.now(tz=datetime.timezone.utc)`
**Still relevant**: Check for other uses of naive `datetime.now()` or `datetime.fromtimestamp()` in new code.

---

## Relations: non-string data

**Search**: `relation_set` or databag `__setitem__`
**What to check**: Is there validation that both keys and values are strings before writing?
**True bug**: Allowing `data[123] = value` or `data['key'] = 456` without type checking.

---

## Relations: post-broken access

**Search**: `relation-broken` or `RelationBrokenEvent`
**What to check**: Does code access relation data bags during or after relation-broken events?
**True bug**: Accessing `event.relation.data` in a `relation_broken` handler without checking availability.

---

## Pebble: string iteration

**Search**: `for .* in .*service` where the iterated variable could be a string
**What to check**: Is a `str | list[str]` parameter iterated directly without normalization?
**True bug**: `for svc in services` where `services` is a single string — iterates over characters.
**Correct pattern**: `services = [services] if isinstance(services, str) else list(services)`

---

## Testing: return without copy

**Search**: `return self\._` in harness.py, mocking.py, or testing backend files
**What to check**: Same as "returning internal state" above, but specifically in testing backends.
**Historical bug**: Harness `relation_get()` returned direct reference while Scenario returned `.copy()`. Fixed in [PR #2376](https://github.com/canonical/operator/pull/2376).
**Still relevant**: Check other methods (e.g., `config_get`, `secret_get`) for the same pattern.

---

## Config: falsy default handling

**Search**: `if not config` or `if config\[` or `or default` in config-related code
**What to check**: Are falsy values (0, False, empty string) treated as "missing"?
**True bug**: `value = config.get(key) or default` — treats `0`, `False`, `""` as missing.
**Correct pattern**: `value = config.get(key); if value is None: value = default`

---

## Mutability: incomplete mutation guards

**Search**: `class.*\(dict\)` or `class.*\(list\)` in Python files
**What to check**: Does the subclass override `__setitem__` to prevent mutation but leave `update()`, `pop()`, `clear()`, `__delitem__`, `setdefault()` unguarded?
**True bug**: `_TestingConfig(dict)` overrides `__setitem__` to raise but inherits mutable `update()`.
**False positive**: Classes that intentionally allow some mutations.

**Correct pattern:**
```python
# Either override ALL mutation methods:
class ImmutableDict(dict):
    def __setitem__(self, key, value): raise TypeError(...)
    def __delitem__(self, key): raise TypeError(...)
    def update(self, *args, **kwargs): raise TypeError(...)
    def pop(self, *args): raise TypeError(...)
    def clear(self): raise TypeError(...)
    def setdefault(self, *args): raise TypeError(...)

# Or use MappingProxyType:
from types import MappingProxyType
config = MappingProxyType(raw_config)
```

---

## Naming: hyphen-underscore mismatch

**Search**: `auth-type`, `auth_type`, or any Juju field names in Python dicts
**What to check**: Does the code assume hyphens or underscores? Does it handle both?
**True bug**: `data['auth-type']` when the data dict uses underscored keys (or vice versa).
**Correct pattern**: Use `.get()` with explicit alias mapping or normalize at the boundary.

---

## Pebble: path handling

**Search**: `push_path|pull_path` and any path string concatenation (e.g., `f'{path}/'`, `os.path.join`)
**What to check**: Are relative paths, empty strings, and trailing slashes handled? Is `pathlib.Path` used?
**True bug**: String concatenation for paths without normalization — breaks on relative paths or empty components.
**Correct pattern**: Use `pathlib.Path` for all path operations. Test with `"."`, `""`, `"../foo"`, and absolute paths.

Precedent: `cbaec52e`

---

## Pebble: temp file cleanup

**Search**: `tempfile` or `NamedTemporaryFile|TemporaryDirectory` in pebble-related code
**What to check**: Is the temp file/dir always cleaned up, even on exception?
**True bug**: Creating a temp file outside a `with` block or not handling cleanup in the error path.
**Correct pattern**: Always use `with tempfile.TemporaryDirectory() as tmp:` or equivalent context manager.

Precedent: `a1574f43`

---

## Testing: ops-harness-scenario divergence

**Search**: For any method name, check if it exists in all three: `_ModelBackend` (ops/model.py), `_TestingModelBackend` (harness.py), `_MockModelBackend` (mocking.py)
**What to check**: Does the same method behave differently across the three backends? Check:
- Return types (copy vs reference)
- Validation (present in one, absent in another)
- Error types raised
- Side effects (e.g., event emission)
**True bug**: `relation_get` returns `.copy()` in Scenario but direct reference in Harness.
**Method**: Pick a method name like `relation_get`, `config_get`, `secret_get`, etc. Read the implementation in all three backends and diff the logic.

---

## Event framework: deferred event snapshots

**Search**: `defer()` or `snapshot` or `_stored_data` in framework.py
**What to check**: When one observer defers an event and another does not, is the snapshot data still available for the deferred re-emission?
**True bug**: Snapshot data lost because it was cleaned up after the first (non-deferring) observer finished.

Precedent: `d0f9f501`

---

## Event framework: handle reuse

**Search**: `_event_counter` or `handle.*count` or `Handle\(` in framework.py
**What to check**: Is the event counter persisted across charm invocations? Reused handles cause event collisions.
**True bug**: Counter resets to 0 on each invocation, causing handles like `on/start[0]` to collide with previously deferred events.

Precedent: `f36e90b9`

---

## Imports: circular dependencies

**Search**: `import ops` or `from ops` inside ops package files, especially conditional imports
**What to check**: Are there import cycles between modules? Common cycle: `model.py` ↔ `charm.py` ↔ `framework.py`.
**True bug**: Top-level import that creates a cycle, causing `ImportError` or `AttributeError` at import time.
**False positive**: Imports inside `TYPE_CHECKING` blocks or inside function bodies (lazy imports).

Precedent: `14f3baf5`

---

## Imports: __all__ completeness

**Search**: `__all__` in `__init__.py` files
**What to check**: Are all public API classes/functions listed? Are any listed names misspelled or referencing removed symbols?
**True bug**: `__all__` lists a name that doesn't exist in the module, causing `AttributeError` on `from ops import *`.

Precedent: `9dbb6b66`

---

## Error handling: wrong exception type

**Search**: `except \w+Error` and `raise \w+Error` in ops source files
**What to check**: Is the caught/raised exception the right type for the situation?
**True bug**: `except KeyError` when the actual error is `RelationNotFoundError`, masking the real failure.
**Also check**: Are `TypeError` and `ValueError` used correctly? `TypeError` for wrong argument types, `ValueError` for wrong argument values.

Precedents: `97501fd7`, `4fc4cfdb`

---

## Error handling: bare dict access

**Search**: `\[['"]` (bracket-quote access) on dicts that come from Juju or external APIs
**What to check**: Is `dict[key]` used where `.get(key)` with a default would be safer? Especially for Juju API responses where fields may be missing in certain versions.
**True bug**: `data['field']` on a Juju API response where the field is optional or version-dependent.
**False positive**: Access on dicts where the key is guaranteed by prior validation or construction.

Precedent: `c1661cae` (missing fields in network-get)

---

## Juju version: unchecked feature use

**Search**: `JujuVersion` or version-dependent Juju CLI flags like `--app`, `--label`, `--expire`
**What to check**: Is there a `JujuVersion` check before using features that are not available in all supported versions?
**True bug**: Unconditionally passing `--app` to `relation-get` when it was only added in Juju 2.7.0.
**Also check**: Are the version thresholds correct? A wrong version number in a check is as bad as no check.

Precedents: `d6d1746b`, `5151a1e`
