# Operator Bug Pattern Catalog

Derived from analysis of 235+ bug fixes in canonical/operator (2019-2026).

## Contents
- Security
- Data Mutability
- Relation Data
- Secrets
- Pebble
- Testing Divergence
- Juju API
- Error Handling
- Event Framework
- Configuration
- Type Annotations

---

## Security

**Priority: CRITICAL**

### Information leaks in error messages

`ExecError.__str__` previously exposed full command lines including credentials. Fix: show only `self.command[0]`, never full arguments.

Rule: never include full command arguments, environment variables, or request bodies in error messages or logs.

Precedent: `0ce8a0fd`

### Insecure file permissions

SQLite storage file was created with 0o644 (world-readable). Fix: use 0o600.

Rule: always use `os.open(path, flags, mode=0o600)` and `os.fdopen()` for files containing state, credentials, or secrets. Do not rely on umask.

Precedent: `e4b0f9d4`

### CI workflow injection

CI workflows used git refs directly in shell commands, enabling injection.

Rule: never use PR data or git refs directly in shell commands. Use environment variables or intermediate artifacts.

Precedent: `85e677ef`

---

## Data Mutability

**Priority: HIGH — most persistent bug pattern in this codebase**

### Copy on store

When accepting dicts from callers, always copy: `self._data = dict(data)` or `copy.deepcopy(data)` for nested structures.

Bad:
```python
class Context:
    def __init__(self, meta: dict):
        self._meta = meta  # BUG: caller can mutate internal state
```

Good:
```python
class Context:
    def __init__(self, meta: dict):
        self._meta = dict(meta)  # Defensive copy
```

Precedent: `3f8fb9b9` — `testing.Context` held direct references to user-provided dicts for meta, config, actions.

### Copy on return

When returning internal state, return a copy.

Bad:
```python
def relation_get(self, relation_id, member_name, is_app):
    return self._relation_data_raw[relation_id][member_name]  # BUG: caller can corrupt internal state
```

Good:
```python
def relation_get(self, relation_id, member_name, is_app):
    return self._relation_data_raw[relation_id][member_name].copy()
```

Precedent: `be090122` — `_MockModelBackend.relation_get` returned actual stored dict.

### Immutable alternatives

Where possible, use `MappingProxyType`, frozen dataclasses, or `tuple` instead of `dict`/`list`. `Model.config` was made immutable in `6cd5d6c` — this is the gold standard.

---

## Relation Data

**Priority: HIGH — 25+ historical fixes**

### Data access after relation-broken

Data bags are unavailable after relation-broken events. Code accessing them crashes.

Precedent: `1b086258`

### Non-string keys/values

Juju relation data is strictly `Dict[str, str]`. Python code can accidentally write non-string types without validation.

Precedent: `4ffc1256`

### Shell argument length limits

Using command-line arguments for `relation-set` can exceed shell limits with large data. Use `--file` flag instead.

Precedent: `9fe65c7c`

### Relation ID handling

Static method vs instance method confusion, wrong IDs in events.

Precedent: `49aaa0a0`

### Spurious relation_changed events

Issuing relation_changed when there is no actual data delta.

Precedent: `16434141`

### Naming convention mismatch

Juju uses hyphens (`auth-type`), Python uses underscores. Mismatch causes KeyError.

Rule: normalize at API boundaries. Use `.get()` with fallback or explicit alias mapping.

Precedent: `d7473832`

---

## Secrets

**Priority: HIGH — 13+ historical fixes**

### Secret ID canonicalization

Juju uses `secret:<id>` format. Code sometimes omits the prefix.

Precedent: `7670b59c`

### Never cache secrets

Caching secrets in Ops leads to stale data. Always fetch fresh.

Precedent: `9323ead`

### Conflicting API arguments

`secret-info-get` cannot accept both ID and label simultaneously. Validate before calling.

Precedent: `3ce1c7f`, `5afc2842`

### Owner normalization

Secret owner field inconsistencies between ops and testing.

Precedent: `e7e2c8d`

### ~~Invalid flags on wrong commands~~ (retracted — false positive)

~~`--owner` is valid for `secret-add` but not `secret-set`.~~ This was incorrect: `secret-set` does accept `--owner` per the [Juju documentation](https://documentation.ubuntu.com/juju/latest/reference/hook-command/list-of-hook-commands/secret-set/). The code in `hookcmds.secret_set()` is correct.

---

## Pebble

**Priority: MEDIUM — 16+ historical fixes**

### Path handling

Relative paths, empty directories, and path traversal issues in `push_path`/`pull_path`.

Rule: always use `pathlib.Path`. Test with absolute, relative, and edge-case paths.

Precedent: `cbaec52e`

### Binary file handling

`push()` not correctly handling binary files.

Precedent: `5943a59c`

### Exec process stdout iteration

`for line in process.stdout` did not work correctly.

Precedent: `91b6551a`

### Temporary file cleanup

`ops.Pebble.pull` not cleaning up temp files on error. Use context managers.

Precedent: `a1574f4`

### Layer merging

Incorrect merge semantics for Pebble layers in testing.

Precedent: `3dda5b5f`

### String iteration on service names

`Container.restart()` iterated over characters of a service name string instead of treating it as a single service.

Rule: when accepting `str | list[str]` arguments, always normalize to list before iterating.

Precedent: `37fdcbaf`

---

## Testing Divergence

**Priority: MEDIUM — 32+ historical fixes**

### Rule: every ops fix must be mirrored

When fixing a bug in ops, always check if the same fix needs to apply to Harness and Scenario backends.

### Common divergences

1. **Event emission order**: Testing frameworks emitting events in wrong order or with wrong data.
   Precedent: `5a63e01e`

2. **Secret behavior**: Harness secrets not matching Juju behavior.
   Precedent: `79706f40`

3. **Missing validation**: Testing backends allowing operations that Juju would reject.
   Precedent: `668701b4`

4. **Storage/config mocking**: Incorrect kwarg handling in testing backend.
   Precedent: `deccdd6f`

5. **Return references vs copies**: Scenario fixed to return `data.copy()` but Harness still returns direct reference.
   Current finding: `Harness.relation_get()` returns direct dict reference.

6. **Config mutation**: `_TestingConfig` inherits from `dict` — `__setitem__` raises but `update()`, `pop()`, `clear()` bypass the guard.
   Current finding: `config_get()` returns `_TestingConfig` directly.

---

## Juju API

**Priority: MEDIUM — 13+ historical fixes**

### Version-dependent features

Code assuming a Juju feature is always available.

Rule: check `JujuVersion` before using version-dependent features.

Precedents: `d6d1746b`, `5151a1e`

### Python version compatibility

Using features not available in all supported Python versions.

Rule: test on all supported Python versions. Use `sys.version_info` checks.

Precedents: `8e94a4c9`, `be1fdf06`

### Naive datetime

`datetime.datetime.now()` and `datetime.fromtimestamp()` return naive datetimes without timezone info. Juju expects RFC 3339 with timezone.

Rule: always use `datetime.datetime.now(tz=datetime.timezone.utc)` and `datetime.fromtimestamp(ts, tz=datetime.timezone.utc)`.

Current findings: `_calculate_expiry()` at `model.py:539`, `Container._build_fileinfo()` at `model.py:3047`.

---

## Error Handling

**Priority: MEDIUM — 16+ historical fixes**

### Wrong exception types

Catching or raising the wrong exception class.

Precedents: `97501fd7`, `4fc4cfdb`

### Missing edge case handling

Not handling unusual but valid states from Juju.

Precedents: `c1661cae` (missing fields in network-get), `c9bba5b0` (stdout already consumed)

### Poor error messages

Error messages that do not help diagnose the problem. Include what was expected vs what was found.

Precedents: `8df3d2f1`, `1b086258`

---

## Event Framework

**Priority: MEDIUM**

### Event snapshot availability

Event snapshot not available when one observer defers and another does not.

Precedent: `d0f9f501`

### Transaction integrity on first run

Transaction integrity lost on first run.

Precedent: `d14c3033`

### Event handle reuse

Event count not persisted, causing reused event handles.

Precedent: `f36e90b9`

---

## Configuration

**Priority: MEDIUM — 7+ historical fixes**

### Falsy config defaults

Empty string, 0, and False treated as missing (truthy check instead of `is None`).

Precedent: `1c0ff40d`

### Config immutability

`Model.config` should be immutable to prevent accidental mutation.

Precedent: `6cd5d6c`

---

## Type Annotations

**Priority: LOW — 10+ historical fixes**

### Wrong return types

Functions annotated with incorrect types.

Precedents: `3df8ae9` (Model.get_binding), `fad95d7d` (StatusBase.name)

### Assignment vs annotation syntax

Using `= list[str]` instead of `: list[str]` for type annotations.

Precedent: `aa06bf54`

### Import compatibility

Type checkers not understanding conditional imports.

Precedent: `d6325d05`
