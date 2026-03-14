# Code Audit: canonical/operator (Current HEAD)

**Date:** 2026-03-14
**Auditor:** Automated pattern-based audit
**Scope:** Core ops library and testing frameworks
**Method:** Cross-referencing 235+ historical bug fixes against current source code

---

## Executive Summary

This audit examined the current HEAD of the canonical/operator repository against 10 known bug pattern categories derived from 15 high-severity fixes and 220 additional historical fixes. The audit identified **13 findings**: 2 high severity, 6 medium severity, and 5 low severity.

The most critical findings are:
1. **Harness `relation_get()` returns a direct reference** to internal relation data rather than a copy, allowing mutations to silently corrupt test state.
2. **Secret temporary files are created with default permissions** (typically 0o644), potentially exposing secret content to other users on the system.

---

## High Severity Findings

### ~~H-1: RETRACTED (false positive)~~

`hookcmds.secret_set()` passing `--owner` to `secret-set` was originally flagged as a bug, on the assumption that `--owner` is only valid for `secret-add`. This is incorrect: the Juju `secret-set` hook command does accept `--owner` (see https://documentation.ubuntu.com/juju/latest/reference/hook-command/list-of-hook-commands/secret-set/). The code is correct as written.

---

### H-2: Harness `relation_get()` returns direct reference to internal dict (no copy)

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/ops/_private/harness.py` |
| **Line** | 2453-2458 |
| **Pattern** | Mutability / shared-dict-no-copy |

**Code:**
```python
def relation_get(self, relation_id: int, member_name: str, is_app: bool):
    if is_app and '/' in member_name:
        member_name = member_name.split('/')[0]
    if relation_id not in self._relation_data_raw:
        raise model.RelationNotFoundError()
    return self._relation_data_raw[relation_id][member_name]
```

**What could go wrong:** This returns a direct reference to the internal `_relation_data_raw` dict. The Scenario mock backend at `testing/src/scenario/mocking.py:257` correctly returns `data.copy()`, and this exact bug was previously fixed for Scenario (commit `be0901227c`, "fix: `_MockModelBackend.relation_get` will return a copy of the relation data"). In production, `relation-get` returns fresh data from Juju each time. In Harness, mutations by the charm to the returned dict will silently modify the Harness's internal state, causing subsequent reads to see stale or corrupted data. This is a test-production behavior mismatch.

**Recommended fix:** Return `self._relation_data_raw[relation_id][member_name].copy()` instead of returning the dict directly, matching the Scenario fix and real Juju behavior.

---

### H-3: Secret temp files created without restrictive permissions

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/ops/hookcmds/_secret.py` |
| **Lines** | 64-68, 303-307 |
| **Pattern** | File permission issues / credential leak |

**Code:**
```python
with tempfile.TemporaryDirectory() as tmp:
    for k, v in content.items():
        with open(f'{tmp}/{k}', mode='w', encoding='utf-8') as f:
            f.write(v)
```

**What could go wrong:** Secret content is written to temporary files using `open()` with default permissions (typically 0o644 depending on umask). This means the secret values are world-readable on disk until the TemporaryDirectory is cleaned up. The historical fix `e4b0f9d4` ("fix: reduce mode of SQLite storage file to 0o600") established the pattern that files containing sensitive data must be created with restrictive permissions. While the exposure window is brief (the files exist only during the subprocess call), on a compromised or multi-tenant system another process could read these files.

**Recommended fix:** Use `os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode=0o600)` and `os.fdopen()` to create the temp files with 0o600 permissions, or set `os.umask(0o077)` before creating them. This applies to both `secret_add()` (lines 64-68) and `secret_set()` (lines 303-307).

---

## Medium Severity Findings

### M-1: `Relation.save()` uses `dataclasses.asdict()` for dataclass objects

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/ops/model.py` |
| **Line** | 1906 |
| **Pattern** | Naming convention mismatch (dataclasses.asdict) |

**Code:**
```python
if dataclasses.is_dataclass(obj):
    assert not isinstance(obj, type)
    for field in dataclasses.fields(obj):
        alias = field.metadata.get('alias', field.name)
        fields[field.name] = alias
    values = dataclasses.asdict(obj)
```

**What could go wrong:** The historical fix `d7473832` ("fix: prevent KeyError on auth-type when creating CloudCredential object") showed that `dataclasses.asdict()` preserves Python-style underscore naming, which can mismatch with hyphenated Juju API keys. While the `fields` mapping handles the alias for key names, `dataclasses.asdict()` deeply converts nested dataclasses, which could cause issues if a field value itself is a dataclass with aliased fields. The values dict uses attribute names as keys, and those are matched against `fields` keys, so the current code works for flat dataclasses. However, if a charm uses nested dataclasses with aliased fields, the deep conversion by `asdict()` could cause unexpected behavior since it recursively converts without alias awareness.

**Recommended fix:** Consider using `{field.name: getattr(obj, field.name) for field in dataclasses.fields(obj)}` instead of `dataclasses.asdict(obj)` to avoid the deep-conversion pitfall, matching the pattern established by `_from_hookcmds()` methods.

---

### M-2: `_calculate_expiry()` uses naive `datetime.datetime.now()` without timezone

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/ops/model.py` |
| **Line** | 539 |
| **Pattern** | Missing timezone awareness |

**Code:**
```python
def _calculate_expiry(
    expire: datetime.datetime | datetime.timedelta | None,
) -> datetime.datetime | None:
    ...
    elif isinstance(expire, datetime.timedelta):
        return datetime.datetime.now() + expire
```

**What could go wrong:** `datetime.datetime.now()` returns a naive (timezone-unaware) datetime. If the charm passes a timezone-aware timedelta-based expiry, the resulting datetime will be naive, which may cause issues when serialized and sent to Juju (which expects RFC 3339 with timezone). The `datetime_to_rfc3339` function in hookcmds also does not add timezone info if the datetime is naive. This could lead to Juju interpreting the expiry time incorrectly, especially in environments where the system timezone is not UTC.

**Recommended fix:** Use `datetime.datetime.now(tz=datetime.timezone.utc)` to produce a timezone-aware datetime.

---

### M-3: `Container._build_fileinfo()` uses naive `datetime.fromtimestamp()`

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/ops/model.py` |
| **Line** | 3047 |
| **Pattern** | Missing timezone awareness |

**Code:**
```python
last_modified=datetime.datetime.fromtimestamp(info.st_mtime),
```

**What could go wrong:** `datetime.fromtimestamp()` without a `tz` argument returns a naive datetime in the local timezone. The resulting `FileInfo.last_modified` may be interpreted differently depending on the system's timezone, leading to inconsistent behavior when comparing file modification times across systems or when pushing files to Pebble containers.

**Recommended fix:** Use `datetime.datetime.fromtimestamp(info.st_mtime, tz=datetime.timezone.utc)`.

---

### M-4: Harness `config_get()` returns `_TestingConfig` object directly (not a copy)

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/ops/_private/harness.py` |
| **Line** | 2496-2497 |
| **Pattern** | Return internal state without copying |

**Code:**
```python
def config_get(self) -> _TestingConfig:
    return self._config
```

**What could go wrong:** The `_TestingConfig` object is returned directly. While `_TestingConfig.__setitem__` raises `TypeError` to prevent `config[key] = value`, the object inherits from `dict` and methods like `dict.update()`, `dict.pop()`, and `dict.clear()` bypass the override. A charm calling any of these inherited methods during testing would silently corrupt the Harness's internal config state without raising an error, whereas in production these operations would have no effect on the actual Juju config. The static analysis finding at line 2497 also flagged this.

**Recommended fix:** Return `dict(self._config)` to return a plain dict copy, or override additional mutation methods in `_TestingConfig`.

---

### M-5: Scenario `_MockModelBackend.relation_set()` operates on the same dict as `RelationDataContent`

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/testing/src/scenario/mocking.py` |
| **Lines** | 394-417 |
| **Pattern** | Test-production mismatch |

**Code:**
```python
def relation_set(self, relation_id: int, data: Mapping[str, str], is_app: bool) -> None:
    # NOTE: The code below currently does not have any effect, because
    # the dictionary has already had the same set/delete operations
    # applied to it by RelationDataContent -- unlike in production,
    # where this method calls out to Juju's relation-set to operate on
    # the real databag, this method currently operates on the same
    # dictionary object that RelationDataContent does.
```

**What could go wrong:** The code comments explicitly acknowledge this is a deviation from production behavior. In production, `relation-set` is a separate operation from the local cache update in `RelationDataContent`. If the `relation-set` hook command fails (e.g., permission denied), the local cache would not be updated. In Scenario, the mutation happens directly in-memory regardless of any validation failures, meaning tests may pass even when the charm would fail in production due to relation-set errors.

**Recommended fix:** This is already documented as a known limitation. A proper fix would involve separating the data storage so that `relation_set` operates on a different copy, with mutations propagated only after validation.

---

### M-6: `_ModelCache` stores `meta` without copying

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/ops/model.py` |
| **Line** | 336 |
| **Pattern** | Shared dict without copy |

**Code:**
```python
class _ModelCache:
    def __init__(self, meta: _charm.CharmMeta, backend: _ModelBackend):
        self._meta = meta
```

**What could go wrong:** The `meta` object (a `CharmMeta` instance) is stored directly. If any code path mutates the meta object after it is passed to `_ModelCache`, the cache would see stale or incorrect metadata. While `CharmMeta` objects are generally treated as immutable, the lack of defensive copying means this invariant is not enforced. The static analysis finding confirmed this pattern.

**Recommended fix:** This is low risk since `CharmMeta` is not typically mutated, but for safety consider using a frozen dataclass or documenting the immutability requirement.

---

## Low Severity Findings

### L-1: Pebble `_MultipartParser.get_file()` opens file without context manager

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/ops/pebble.py` |
| **Line** | 3565 |
| **Pattern** | Resource cleanup |

**Code:**
```python
file_io = open(  # noqa: SIM115
    self._files[path].name,
    mode,
    encoding=encoding,
    newline=newline,
)
return typing.cast('_TextOrBinaryIO', file_io)
```

**What could go wrong:** The file is opened and returned to the caller without using a context manager. If the caller does not properly close the returned file object, the file handle will leak. The `# noqa: SIM115` comment acknowledges this is intentional (the caller is expected to manage the lifecycle), but it creates a risk that callers forget to close the handle. The historical fix `a1574f43` ("fix: ensure `ops.Pebble.pull` cleans up temporary files if it errors") shows this pattern has caused real issues before.

**Recommended fix:** Document that callers must use `with` to manage the returned file object, or consider returning a context manager wrapper.

---

### L-2: `StoredStateData` returns internal `on` attribute without protection

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/ops/framework.py` |
| **Line** | 1187 |
| **Pattern** | Return internal state |

**Code:**
```python
def __getattr__(self, key: str) -> Any:
    if key == 'on':
        return self._data.on
```

**What could go wrong:** The `on` event source object is returned directly. While this is intentional for the event system to work, the static analysis flagged it as a potential issue. In practice this is safe because `ObjectEvents` is not a mutable data container.

**Recommended fix:** No action needed -- this is a false positive from static analysis. The `on` attribute must be the live object for event observation to work.

---

### L-3: Multiple chained `.get()` calls with fallback defaults

| Property | Value |
|---|---|
| **Files** | Multiple (see below) |
| **Pattern** | Potential None access on chained calls |

**Locations:**
- `ops/jujucontext.py:283` -- `env.get('JUJU_STORAGE_ID', '').split('/')[0]`
- `ops/_private/harness.py:2282` -- `self._spec.get('options', {}).get(key)`
- `testing/src/scenario/_consistency_checker.py:543` -- `charm_spec.meta.get('peers', {}).items()`
- `testing/src/scenario/state.py:2064-2066` -- `self.meta.get('requires', {}).items()` etc.

**What could go wrong:** These all use the `.get(key, default)` pattern with a safe default (`{}`, `''`). The chained operations (`.items()`, `.split()`, `.get()`) will work correctly because the defaults are non-None. These are false positives from the static analysis.

**Recommended fix:** No action needed -- the default values provided to `.get()` ensure the chained calls are safe.

---

### L-4: `_TestingConfig` stores spec dict without copying

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/ops/_private/harness.py` |
| **Line** | 2259 |
| **Pattern** | Shared dict without copy |

**Code:**
```python
def __init__(self, config: _RawConfig):
    super().__init__()
    self._spec = config
```

**What could go wrong:** The config spec dict is stored by reference. If the caller (Harness setup code) later modifies the config spec dict, `_TestingConfig` would see the mutations. In practice, the config YAML is parsed once and not modified, so this is unlikely to cause issues.

**Recommended fix:** Use `self._spec = copy.deepcopy(config)` if defensive copying is desired.

---

### L-5: `_GenericLazyMapping.__getitem__` returns internal data values directly

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/operstor-analysis/operator/ops/model.py` |
| **Line** | 894-895 |
| **Pattern** | Return internal state |

**Code:**
```python
def __getitem__(self, key: str) -> _LazyValueType:
    return self._data[key]
```

**What could go wrong:** For `ConfigData`, the values are immutable primitives (`bool | int | float | str`), so returning them directly is safe. For `RelationDataContent` (which inherits `LazyMapping`), the values are strings and also immutable. This finding from the static analysis is a false positive in the current usage.

**Recommended fix:** No action needed -- the value types are immutable.

---

## Summary Table

| ID | Severity | Pattern | File | Line(s) | Status |
|----|----------|---------|------|---------|--------|
| H-1 | ~~High~~ | ~~API mismatch~~ | `ops/hookcmds/_secret.py` | 297 | **False positive**: `secret-set` does accept `--owner` |
| H-2 | **High** | Mutability | `ops/_private/harness.py` | 2453-2458 | Bug: relation_get returns reference |
| H-3 | **High** | File permissions | `ops/hookcmds/_secret.py` | 64-68, 303-307 | Risk: secret files world-readable |
| M-1 | Medium | Naming mismatch | `ops/model.py` | 1906 | Risk: nested dataclass aliasing |
| M-2 | Medium | Timezone | `ops/model.py` | 539 | Risk: naive datetime expiry |
| M-3 | Medium | Timezone | `ops/model.py` | 3047 | Risk: naive file timestamps |
| M-4 | Medium | Mutability | `ops/_private/harness.py` | 2496-2497 | Risk: config state corruption |
| M-5 | Medium | Test mismatch | `testing/src/scenario/mocking.py` | 394-417 | Known: documented limitation |
| M-6 | Medium | Shared state | `ops/model.py` | 336 | Risk: meta mutation |
| L-1 | Low | Resource cleanup | `ops/pebble.py` | 3565 | Risk: file handle leak |
| L-2 | Low | Internal state | `ops/framework.py` | 1187 | False positive |
| L-3 | Low | None access | Multiple | Multiple | False positive |
| L-4 | Low | Shared state | `ops/_private/harness.py` | 2259 | Low risk |
| L-5 | Low | Internal state | `ops/model.py` | 894-895 | False positive |

### Pattern Distribution

| Bug Pattern | Count | Severity Range |
|-------------|-------|---------------|
| Mutability / shared dict no copy | 4 | High-Low |
| API / naming mismatch | 1 | Medium |
| File permission issues | 1 | High |
| Missing timezone awareness | 2 | Medium |
| Test-production mismatch | 2 | Medium |
| Resource cleanup | 1 | Low |
| False positives (confirmed safe) | 4 | High-Low |

### Notable Patterns Already Fixed

The following historically-problematic patterns have been correctly addressed in the current code:

- **ExecError credential leak** (commit `0ce8a0fd`): Fixed -- `ExecError.__str__` now shows only `self.command[0]`, not the full command line.
- **CloudSpec naming mismatch** (commit `d7473832`): Fixed -- `_from_hookcmds()` class methods bypass `dataclasses.asdict()`.
- **JUJU_VERSION fallback** (commit `31091898`): Fixed -- `env.get('JUJU_VERSION', '0.0.0')` provides a fallback.
- **SQLite file permissions** (commit `e4b0f9d4`): Fixed -- `_ensure_db_permissions()` enforces 0o600.
- **Premature transaction commit** (commit `d14c3033`): Fixed -- no `self._db.commit()` in `_setup()`.
- **Relation data access validation in __init__** (commit `668701b4`): Fixed -- `framework._event_context('__init__')` wraps charm instantiation.
- **Remote unit injection scoping** (commit `5a63e01e`): Fixed -- restricted to departed/broken events.
- **Null guard for self.app** (commit `a93d676`): Fixed -- `and self.app is not None` guard is present.
- **Secret temp files via #file=** (commit related): Correctly uses `key#file=` syntax to avoid secrets on command line.
- **Scenario relation_get copy** (commit `be090122`): Fixed in Scenario -- returns `data.copy()`.
