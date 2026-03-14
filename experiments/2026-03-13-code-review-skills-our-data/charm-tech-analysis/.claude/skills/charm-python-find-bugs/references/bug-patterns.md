# Charm Python Bug Patterns

Recurring bug patterns from 344 historical fixes across 8 Python repositories in the Canonical Charm Tech ecosystem: operator, charmlibs, jubilant, pytest-jubilant, operator-libs-linux, charmhub-listing-review, charmcraft-profile-tools, charm-ubuntu.

## Contents
- Security
- Data Mutability
- Falsy Value Confusion
- Relation Data
- Secrets
- Pebble
- Testing Divergence
- Juju CLI
- Snap CLI
- System Libraries
- Error Handling
- Type Confusion
- Context Manager Safety
- Configuration Handling
- Version Compatibility
- Imports

---

## Security

**Priority: CRITICAL — always review carefully**

### Information leaks in error messages

`ExecError.__str__` exposed full command lines including credentials passed to Pebble exec.

**Fix pattern**: Show only the executable name, not arguments.
```python
# Bug: f"command {self.command} failed"
# Fix: f"command {self.command[0]!r} failed"
```
Precedent: `0ce8a0fd` (operator)

### Insecure file permissions

SQLite storage and secret temp files created with default 0o644 (world-readable).

**Fix pattern**: Use `os.open()` with explicit mode.
```python
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode=0o600)
with os.fdopen(fd, 'w', encoding='utf-8') as f:
    f.write(secret_value)
```
Precedent: `e4b0f9d4` (operator)

### CI workflow injection

Git references used directly in shell commands in GitHub Actions workflows.

**Fix pattern**: Use environment variables or intermediate artifacts, not git refs in shell commands.
Precedent: `85e677ef` (operator)

---

## Data Mutability

**Priority: HIGH — 8 instances, all high severity. Most persistent pattern in the ecosystem.**

Dicts and lists passed by reference allow callers to corrupt internal state, or internal state changes to leak to callers. This pattern recurs across operator, charmlibs, and operator-libs-linux.

### Returning internal state without copy

```python
# Bug: caller can mutate internal state
def get_config(self):
    return self._config

# Fix: copy on return
def get_config(self):
    return dict(self._config)
```

**Known instances**:
- `_MockModelBackend.relation_get` returned stored dict directly — `be09012` (operator)
- `Snap.apps` property returns `self._apps` list directly — current bug in operator-libs-linux + charmlibs
- `Plan.services`/`checks`/`log_targets` return internal dicts — current bug in operator
- Scenario `secret_get` returns internal dict without copy — current bug in operator
- Scenario `action_get` returns internal params dict without copy — current bug in operator

### Storing external input without copy

```python
# Bug: user's dict is stored directly
class Context:
    def __init__(self, meta: dict):
        self._meta = meta

# Fix: copy on store
class Context:
    def __init__(self, meta: dict):
        self._meta = dict(meta)
```

Precedents: `3f8fb9b9` (operator — meta, config, actions dicts), `3dda5b5f` (operator — Pebble layer merge mutating originals)

### Hashability after dataclass migration

When migrating from `dataclass(frozen=True)` to plain classes, `__hash__` must be explicitly added. Two separate charmlibs commits hit this months apart.

Precedents: `89d6218e`, `49e542c6` (charmlibs)

### Class-level mutable defaults

```python
# Bug: shared across all instances
class Config(Mapping):
    _lazy_data: Optional[Dict] = None

# Fix: initialize in __init__
class Config(Mapping):
    def __init__(self):
        self._lazy_data: Optional[Dict] = None
```

Current bug: `GrubConfig._lazy_data` in operator-libs-linux

---

## Falsy Value Confusion

**Priority: HIGH — most pervasive pattern in current code audits (10+ instances across repos)**

Using `if value` or `if not value` where `value is not None` is needed. Drops legitimate 0, empty string, or False values.

### UID/GID 0 (root user/group)

```python
# Bug: UID 0 (root) treated as "no UID"
if uid:
    cmd.extend(["--uid", str(uid)])

# Fix:
if uid is not None:
    cmd.extend(["--uid", str(uid)])
```

Current bugs:
- `add_user()` in passwd.py: `if uid` drops UID 0 — operator-libs-linux + charmlibs
- `add_group()` in passwd.py: `if gid` drops GID 0 — operator-libs-linux + charmlibs
- `Service.to_dict()` in pebble.py: `if value` drops `user-id: 0` and `group-id: 0` — operator
- `Service._merge()` in pebble.py: `if not value` skips merging 0 values — operator

### Numeric parameters

```python
# Bug: num_lines=0 returns all logs instead of 0
args = ["logs", f"-n={num_lines}"] if num_lines else ["logs"]

# Fix:
args = ["logs", f"-n={num_lines}"] if num_lines is not None else ["logs"]
```

Current bug: `Snap.logs()` in operator-libs-linux + charmlibs

### Config defaults

```python
# Bug: empty string, 0, and False treated as missing
value = config.get(key) or default

# Fix:
value = config.get(key)
if value is None:
    value = default
```

Precedent: `1c0ff40d` (operator)

---

## Relation Data

**Priority: HIGH — 33 fixes in operator, largest domain-specific area**

### Accessing data after relation-broken

Data bags are unavailable after a relation is broken.
Precedent: `1b086258` (operator)

### Non-string keys/values

Juju requires `Dict[str, str]`. Python doesn't enforce this.

```python
# Bug: allows data[123] = value
# Fix: validate isinstance(key, str) and isinstance(value, str) before write
```
Precedent: `4ffc1256` (operator)

### Shell argument length limits

Large relation data exceeds command-line limits when using `relation-set` args.

**Fix pattern**: Use `--file` for relation-set.
Precedent: `9fe65c7c` (operator)

### Remote unit availability

Wrong units added for wrong event types. Remote units should only be available in `departed` and `broken` events.
Precedent: `5a63e01e` (operator)

---

## Secrets

**Priority: HIGH — 19 fixes across operator + charmlibs**

### ID canonicalization

Juju uses `secret:<id>` format. Code sometimes omits the prefix.
Precedent: `7670b59c` (operator)

### Caching

Secrets must never be cached locally — always fetch fresh from Juju.
Precedent: `9323ead` (operator)

### Conflicting API arguments

`secret-info-get` cannot accept both ID and label simultaneously.
Precedent: `3ce1c7f`, `5afc2842` (operator)

### Ownership model

App-owned vs unit-owned secret confusion. Private keys stored as unit-owned instead of app-owned.
Precedent: `0de72f66` (charmlibs)

### Event reliability

`secret_expired` can fail to trigger; code needs safety-net fallbacks.
Precedent: `8fdf5b4f` (charmlibs)

---

## Pebble

**Priority: MEDIUM — 32 fixes in operator**

### String iteration trap

```python
# Bug: if services is a str, iterates over characters
for svc in services:
    container.restart(svc)

# Fix: normalize to list first
services = [services] if isinstance(services, str) else list(services)
```
Precedent: `37fdcbaf` (operator)

### Path handling

Relative paths, empty dirs, binary files all need explicit handling.
Precedents: `cbaec52e`, `942bd23`, `5943a59c` (operator)

### Layer merging mutation

Scenario `_render_services()` mutates Layer Service objects in place. Calling `.plan` multiple times accumulates duplicates in list fields.
Current bug in operator — variant of `3dda5b5f`

### Temp file cleanup

`ops.Pebble.pull` not cleaning up temp files on error.
Precedent: `a1574f4` (operator)

---

## Testing Divergence

**Priority: MEDIUM — 51 fixes, largest single area in the ecosystem**

The Harness and Scenario testing frameworks must replicate Juju behavior. Every ops fix potentially requires a matching fix in testing code.

### Return value mutability

Production returns copies; testing returns references (or vice versa).

Current bugs:
- Scenario `secret_get()` returns internal dict — production returns `.copy()`
- Scenario `action_get()` returns internal dict — production returns fresh data each call

### Environment variable leakage

Tests modifying `os.environ` without cleanup, leaking state between tests.
Precedents: `e302b630`, `101997e6` (operator)

### Secret behavior

Harness secrets not matching Juju behavior for ownership, labels, info visibility.
Precedents: `79706f40`, `e7e2c8d`, `0fa4497` (operator)

### Context manager lifecycle

Testing context not properly exiting on exceptions.
Precedent: `3ac3706b` (operator)

---

## Juju CLI

**Priority: MEDIUM — 10+ fixes across operator + jubilant**

### Argument formatting

Every wrapper around `juju` CLI hits argument formatting bugs.

```python
# Bug: --bind uses comma-separated format
bind_arg = ",".join(f"{k}={v}" for k, v in bindings.items())

# Fix: --bind uses space-separated format
bind_arg = " ".join(f"{k}={v}" for k, v in bindings.items())
```
Precedent: `5feadf3b` (jubilant)

### Version-dependent flags

`--app` flag for `relation-get`/`relation-set` not available before Juju 2.7.0.
Check `JujuVersion` before using version-dependent features.
Precedent: `5151a1e` (operator)

### Flag availability

`juju offer` does not accept `--model` flag.
Precedent: `2c749e95` (jubilant)

---

## Snap CLI

**Priority: MEDIUM — 19 fixes across operator-libs-linux + concierge**

### Spurious embedded quotes

```python
# Bug: literal " chars passed to subprocess
args.append(f'--channel="{channel}"')

# Fix: no embedded quotes needed with list args
args.append(f'--channel={channel}')
```
Current bug: `_install` and `_refresh` in snap.py — operator-libs-linux + charmlibs

### Revision type confusion

Snap revisions handled as `int` but should be `str` — required a v2 library bump.
Precedent: `1a09b160` (operator-libs-linux)

### Rate limiting

snapd API returns "too many requests". All snap operations need retry logic.

### Status states

`Do` is a valid pending state in snap task status. Code often only checks for expected states.

---

## System Libraries

**Priority: MEDIUM — specific to operator-libs-linux + charmlibs**

### Dict inheritance bugs

```python
# Bug: inherits from dict but never populates parent
class Config(Dict):
    def __init__(self):
        self._data = self._load_data()
    # dict methods like .items(), .keys() return empty results
```

Current bug: `sysctl.Config` in operator-libs-linux

### APT environment inheritance

apt commands inheriting incorrect environment from parent process.

### Sources.list parsing

Multiple iterations needed to handle edge cases in apt sources.list format.

---

## Error Handling

**Priority: MEDIUM — 37 fixes across 6 repos**

### Wrong exception types

Catching `RelationNotFoundError` when the actual error is `KeyError` (or vice versa).
Precedent: `97501fd7` (operator)

### Printf-style exception constructors

```python
# Bug: %r never expanded — appears literally in message
raise TypeError("specified argument '%r' should be a string or int", user)

# Fix: use f-string
raise TypeError(f"specified argument {user!r} should be a string or int")
```
Current bug: `passwd.py` in operator-libs-linux + charmlibs

### Wrong exception attribute access

```python
# Bug: e.args[1] is the command list, not stderr
except CLIError as e:
    if "error message" in e.args[1]:  # checks command, not stderr

# Fix: use the correct attribute
    if "error message" in (e.stderr or ""):
```
Current bug: `pytest-jubilant/_main.py`

---

## Type Confusion

**Priority: MEDIUM — 23 instances across 5 repos**

### type() vs isinstance()

```python
# Bug: fails for subclasses, bool passes as int
if type(package) == str:

# Fix:
if isinstance(package, str):
```
Precedent: `57e7a6f9` (operator-libs-linux)

### Machine IDs are strings, not ints

Juju machine IDs can be `"0/lxd/0"` (nested containers).
Precedents: `0fc35804` (operator), `fde3e333` (jubilant)

### Snap revision is str, not int

Precedent: `1a09b160` (operator-libs-linux)

---

## Context Manager Safety

**Priority: HIGH — confirmed current bug**

### Missing try/finally around yield

```python
# Bug: cleanup code skipped if body raises
@contextmanager
def _event_context(self, event_name):
    self._event_name = event_name
    yield
    self._event_name = None  # never reached on exception

# Fix:
@contextmanager
def _event_context(self, event_name):
    self._event_name = event_name
    try:
        yield
    finally:
        self._event_name = None
```

Current bug: `Framework._event_context()` in operator — `_hook_is_running` not restored on exception.
Compare with `_prevent_recursion()` which correctly uses try/finally.

---

## Configuration Handling

**Priority: MEDIUM — 7 fixes in operator**

### Falsy config defaults

See "Falsy Value Confusion" above — same pattern applies to charm config values.

### Mutable config

Config was mutable, allowing charms to accidentally modify their own config.
Fix: `MappingProxyType` or frozen dict.
Precedent: `6cd5d6c` (operator)

---

## Version Compatibility

**Priority: MEDIUM — 11 fixes across operator + jubilant**

### Juju version checks

Check `JujuVersion` before using features like `credential-get`, `--app`, secrets checksums.
Precedents: `d6d1746b`, `5151a1e` (operator), `814ab9b8` (jubilant)

### Python version compatibility

datetime parsing, typing syntax, dataclass features differ across 3.8-3.12+.
Precedents: `8e94a4c9`, `be1fdf06` (operator)

---

## Imports

**Priority: LOW — 6 fixes**

### Circular dependencies

`model.py` ↔ `charm.py` ↔ `framework.py` cycles.
Use `TYPE_CHECKING` blocks for type-only imports.
Precedent: `14f3baf5` (operator)

### __all__ completeness

Names in `__all__` that don't exist cause `AttributeError` on `from X import *`.
Precedent: `9dbb6b66` (operator)
