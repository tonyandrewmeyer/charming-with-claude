# Charm Python Anti-Patterns: Searchable Code Patterns

Concrete code patterns to grep for when auditing Charm Tech Python codebases. Each pattern includes the search command, what to check, and how to distinguish true bugs from false positives.

## Contents
- Mutability: returning internal state
- Mutability: storing without copy
- Mutability: incomplete mutation guards
- Falsy value: if value / if not value
- Falsy value: or default
- Security: file permissions
- Security: error message exposure
- Secrets: invalid flags
- Secrets: caching
- Secrets: ID prefix
- Datetime: missing timezone
- Relations: non-string data
- Relations: post-broken access
- Pebble: string iteration
- Pebble: path handling
- Pebble: temp file cleanup
- Testing: return without copy
- Testing: ops-harness-scenario divergence
- Snap CLI: embedded quotes
- Snap CLI: revision type
- Context managers: yield without try/finally
- Type checks: type() vs isinstance()
- Exception constructors: printf-style
- Dict inheritance: unpopulated parent
- Dict access: bare bracket on external data
- Juju version: unchecked feature use
- Naming: hyphen-underscore mismatch
- Imports: circular dependencies
- Imports: __all__ completeness

---

## Mutability: returning internal state

**Search**: `return self\._` in Python files
**What to check**: Is the returned value a mutable container (dict, list, set)? Could the caller mutate it?
**True bug**: Returns `self._apps` — caller can corrupt internal list.
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
**False positive**: `self._name = name` where `name` is a string (immutable).

---

## Mutability: incomplete mutation guards

**Search**: `class.*\(dict\)` or `class.*\(list\)` in Python files
**What to check**: Does the subclass override `__setitem__` but leave `update()`, `pop()`, `clear()` unguarded?
**True bug**: `sysctl.Config(Dict)` overrides `__getitem__` to delegate to `self._data` but inherits dict methods that operate on empty parent.

---

## Falsy value: if value / if not value

**Search**: `if uid`, `if gid`, `if num_lines`, `if not value`, `if value` in code handling numeric parameters
**What to check**: Can the value legitimately be 0, empty string, or False?
**True bug**: `if uid:` where UID 0 (root) is a valid value.
**True bug**: `if num_lines:` where 0 means "return 0 lines".
**True bug**: `{name: value for name, value in fields if value}` drops 0 and False.
**False positive**: `if channel:` where channel is always a non-empty string when provided.

**Example fix:**
```python
# Before (bug):
if uid:
    cmd.extend(["--uid", str(uid)])
# After (fix):
if uid is not None:
    cmd.extend(["--uid", str(uid)])
```

---

## Falsy value: or default

**Search**: `or default` or `or ''` or `or \[\]` or `or \{\}` in config/parameter code
**What to check**: Does this treat 0, False, or "" as "missing"?
**True bug**: `value = config.get(key) or default` treats `0` and `""` as missing.
**Fix**: `value = config.get(key); if value is None: value = default`

---

## Security: file permissions

**Search**: `open(` in files that handle secrets, credentials, or state
**What to check**: Are files created with restrictive permissions (0o600)?
**True bug**: `open(path, 'w')` for files containing secret content.
**False positive**: Opening files for reading.

---

## Security: error message exposure

**Search**: `__str__` and `__repr__` in exception classes
**What to check**: Do error representations include full command lines or environment variables?
**True bug**: `f"command {self.command} failed"` exposes full argument list.

---

## Secrets: invalid flags

**Search**: `--owner` in secret-related code
**What to check**: Is `--owner` passed to `secret-set`? Only valid for `secret-add`.

---

## Secrets: caching

**Search**: `_secret_cache`, `_cached_secret`, or any dict storing secret content
**What to check**: Is secret content stored and reused without re-fetching?

---

## Secrets: ID prefix

**Search**: `secret_id` or `id=` in secret-related code
**What to check**: Is the `secret:` prefix consistently applied?

---

## Datetime: missing timezone

**Search**: `datetime.now()` or `datetime.fromtimestamp(` without `tz=`
**What to check**: Is the result sent to Juju or serialized?
**True bug**: `datetime.datetime.now()` — naive datetime misinterpreted.
**Fix**: `datetime.datetime.now(tz=datetime.timezone.utc)`

---

## Relations: non-string data

**Search**: `relation_set` or databag `__setitem__`
**What to check**: Is there validation that keys and values are strings?

---

## Relations: post-broken access

**Search**: `relation-broken` or `RelationBrokenEvent`
**What to check**: Does code access `event.relation.data` during relation-broken events?

---

## Pebble: string iteration

**Search**: `for .* in .*service` where the variable could be a string
**What to check**: Is a `str | list[str]` parameter iterated directly?
**True bug**: `for svc in services` where `services` is a single string.
**Fix**: `services = [services] if isinstance(services, str) else list(services)`

---

## Pebble: path handling

**Search**: `push_path|pull_path` and path concatenation
**What to check**: Are relative paths, empty strings, trailing slashes handled?
**Fix**: Use `pathlib.Path` for all path operations.

---

## Pebble: temp file cleanup

**Search**: `tempfile` or `NamedTemporaryFile|TemporaryDirectory`
**What to check**: Is cleanup guaranteed on exception? Use `with` blocks.

---

## Testing: return without copy

**Search**: `return self\._` in harness.py, mocking.py, or testing backend files
**What to check**: Does the testing backend return a copy where production code does?
**True bug**: Scenario `secret_get` returns direct reference; production returns `.copy()`.

---

## Testing: ops-harness-scenario divergence

**Search**: For a method name, check if it exists in all three: `_ModelBackend`, `_TestingModelBackend`, `_MockModelBackend`
**What to check**: Does the same method behave differently? Check return types, validation, error types, side effects.

---

## Snap CLI: embedded quotes

**Search**: `'--channel="` or `'--revision="` or `'--cohort="` in snap-related code
**What to check**: Are literal `"` characters embedded in subprocess args?
**True bug**: `f'--channel="{channel}"'` — quotes passed literally to subprocess.
**Fix**: `f'--channel={channel}'`

---

## Snap CLI: revision type

**Search**: `revision` in snap code, especially comparisons and type annotations
**What to check**: Is revision treated as `int` when it should be `str`?

---

## Context managers: yield without try/finally

**Search**: `@contextmanager` in Python files
**What to check**: Is the `yield` wrapped in `try/finally` for cleanup?
**True bug**: State set before `yield`, restored after `yield` without `try/finally`. Exception skips restoration.

**Quick grep**: Search for `@contextmanager` then check if `try:` appears before `yield` in the same function.

---

## Type checks: type() vs isinstance()

**Search**: `type(` followed by `==` or `is` in conditional checks
**What to check**: Should this be `isinstance()` instead?
**True bug**: `type(package) == str` fails for subclasses.

---

## Exception constructors: printf-style

**Search**: `raise \w+Error\(.*%[srdx]` in Python files
**What to check**: Are exceptions using printf-style formatting?
**True bug**: `raise TypeError("arg '%r' should be str", val)` — `%r` appears literally.
**Fix**: `raise TypeError(f"arg {val!r} should be str")`

---

## Dict inheritance: unpopulated parent

**Search**: `class \w+\(dict\)` or `class \w+\(Dict\)` in Python files
**What to check**: Does `__init__` call `super().__init__()` with the data? Are inherited methods (`.keys()`, `.items()`, `.values()`, `.get()`) correct?
**True bug**: `sysctl.Config(Dict)` — parent dict is always empty, `.items()` returns nothing.

---

## Dict access: bare bracket on external data

**Search**: `\[['"]` on dicts from Juju, JSON, CLI output, or API responses
**What to check**: Is `dict[key]` used where `.get(key)` would be safer?
**True bug**: `data['field']` on a Juju response where the field is optional or version-dependent.
**False positive**: Access on dicts where the key is guaranteed by construction.

---

## Juju version: unchecked feature use

**Search**: `JujuVersion` or version-dependent flags like `--app`, `--label`, `--expire`
**What to check**: Is there a version check before using features not in all supported versions?

---

## Naming: hyphen-underscore mismatch

**Search**: Juju field names in Python dicts (`auth-type`, `auth_type`)
**What to check**: Does code assume hyphens or underscores? Handle both?
**True bug**: `data['auth-type']` when data uses underscored keys.

---

## Imports: circular dependencies

**Search**: `import ops` or `from ops` inside ops package files
**What to check**: Are there import cycles? Common: `model.py` ↔ `charm.py` ↔ `framework.py`.
**False positive**: Imports inside `TYPE_CHECKING` blocks.

---

## Imports: __all__ completeness

**Search**: `__all__` in `__init__.py` files
**What to check**: Do all listed names exist? Are any misspelled?
