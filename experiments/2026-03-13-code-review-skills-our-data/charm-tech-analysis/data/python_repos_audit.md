# Python Repos Audit: Bug Pattern Analysis

Audit of current HEAD of charmlibs, jubilant, pytest-jubilant, and operator-libs-linux repos against known Charm Tech ecosystem bug patterns (sections 3 and 5 of CROSS_REPO_PATTERNS.md).

---

## Finding 1: Snap CLI args contain spurious double quotes (operator-libs-linux + charmlibs)

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v2/snap.py`
**Lines**: 600, 602, 604, 627, 629, 645
**Pattern**: API contract issue -- wrong argument format for snap CLI
**Severity**: High

**Evidence** (from `_install` method, lines 599-604):
```python
if channel:
    args.append(f'--channel="{channel}"')
if revision:
    args.append(f'--revision="{revision}"')
if cohort:
    args.append(f'--cohort="{cohort}"')
```

And the same pattern in `_refresh` (lines 627, 629, 645):
```python
if channel:
    args.append(f'--channel="{channel}"')
if revision:
    args.append(f'--revision="{revision}"')
...
    args.append(f'--cohort="{cohort}"')
```

**Why it is a bug**: The double quotes inside the f-string are embedded as literal `"` characters in the argument string. When passed to `subprocess.check_output(args, ...)` as a list, the shell is NOT involved, so the quotes are passed literally to the snap command. The snap command receives `--channel="stable"` instead of `--channel=stable`. While snapd happens to tolerate this today (it strips quotes internally), this is fragile and incorrect -- it violates the snap CLI argument contract. The same pattern was already identified as a known bug in the patterns document (commits `abe9ec7c`, `0ac58381`).

**Also present in charmlibs**:
**File**: `/home/ubuntu/charm-tech-analysis/charmlibs/snap/src/charmlibs/snap/_snap.py`
**Lines**: 531, 533, 535, 558, 561, 576

Same code was copied into charmlibs as a "bug-for-bug compatible migration" per the documentation, so the bug persists.

**Suggested fix**:
```python
# Remove the embedded double quotes:
args.append(f'--channel={channel}')
args.append(f'--revision={revision}')
args.append(f'--cohort={cohort}')
```

---

## Finding 2: Falsy value confusion in `Snap.logs()` -- `num_lines=0` silently returns all logs (operator-libs-linux + charmlibs)

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v2/snap.py`
**Line**: 503
**Pattern**: Falsy value confusion (`if num_lines` treats 0 as falsy)
**Severity**: Medium

**Evidence** (line 503):
```python
args = ["logs", f"-n={num_lines}"] if num_lines else ["logs"]
```

**Why it is a bug**: If a caller passes `num_lines=0`, the condition `if num_lines` is `False`, so the method falls through to `["logs"]` and returns ALL logs rather than 0 lines. The value `0` is a legitimate integer that should mean "return 0 lines" (matching `snap logs -n=0` behavior), but the falsy check treats it the same as not providing a value at all. This matches the exact pattern described in the patterns doc (section 3.5, commit `1c0ff40d`): "empty string, 0, and False config defaults treated as missing because of `if not value` checks."

**Also present in**:
- charmlibs: `/home/ubuntu/charm-tech-analysis/charmlibs/snap/src/charmlibs/snap/_snap.py`, line 434

**Suggested fix**:
```python
args = ["logs", f"-n={num_lines}"] if num_lines is not None else ["logs"]
```
Note: The charmlibs version already accepts `num_lines: int | Literal['all'] = 10`, but still has the same falsy check.

---

## Finding 3: `Snap.apps` property returns internal `_apps` list without copy (operator-libs-linux + charmlibs)

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v2/snap.py`
**Lines**: 780-783
**Pattern**: Data mutability -- public method returning internal list without copy
**Severity**: Medium

**Evidence**:
```python
@property
def apps(self) -> list[dict[str, JSONType]]:
    """Returns (if any) the installed apps of the snap."""
    self._update_snap_apps()
    return self._apps
```

**Why it is a bug**: The `apps` property returns a direct reference to `self._apps`. Any caller can mutate the list (append, remove, clear) and corrupt the internal state of the Snap object. This is the exact mutability pattern described in section 3.1 of the patterns doc. The `services` property is safe because it constructs a new dict, but `apps` is not.

**Also present in**:
- charmlibs: `/home/ubuntu/charm-tech-analysis/charmlibs/snap/src/charmlibs/snap/_snap.py`, lines 710-714

**Suggested fix**:
```python
@property
def apps(self) -> list[dict[str, JSONType]]:
    self._update_snap_apps()
    return list(self._apps)
```

---

## Finding 4: `add_user()` falsy check on `uid` treats UID 0 (root) as "no UID" (operator-libs-linux + charmlibs)

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v0/passwd.py`
**Lines**: 136, 148
**Pattern**: Falsy value confusion -- `if uid` incorrectly handles UID 0
**Severity**: High

**Evidence** (lines 136, 148):
```python
if uid:
    user_info = pwd.getpwuid(int(uid))
    logger.info("user '%d' already exists", uid)
    return user_info
...
if uid:
    cmd.extend(["--uid", str(uid)])
```

**Why it is a bug**: UID 0 is the root user's UID. When `uid=0` is passed, `if uid` evaluates to `False`, skipping the UID-based existence check and the `--uid 0` argument. This means:
1. If you try to check if root exists by UID, it will fall through to `getpwnam(username)` instead.
2. If creating a user with explicit `uid=0`, the UID argument won't be passed to `useradd`.

This is a textbook falsy-value bug (pattern 3.5). UID 0 is a valid and important value.

**Also present in charmlibs**:
**File**: `/home/ubuntu/charm-tech-analysis/charmlibs/passwd/src/charmlibs/passwd/_passwd.py`
**Lines**: 112, 124

Same bug in the migrated code.

**Suggested fix**:
```python
if uid is not None:
    user_info = pwd.getpwuid(int(uid))
    ...
if uid is not None:
    cmd.extend(["--uid", str(uid)])
```

---

## Finding 5: `add_group()` falsy check on `gid` treats GID 0 as "no GID" (operator-libs-linux + charmlibs)

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v0/passwd.py`
**Lines**: 193, 199
**Pattern**: Falsy value confusion -- `if gid` incorrectly handles GID 0
**Severity**: Medium

**Evidence** (lines 193, 199):
```python
if gid:
    group_info = grp.getgrgid(gid)
    ...
if gid:
    cmd.extend(["--gid", str(gid)])
```

**Why it is a bug**: GID 0 (the root group) is a valid GID. `if gid` evaluates to `False` when `gid=0`, skipping the GID lookup and the `--gid` argument to `addgroup`. Same pattern as Finding 4.

**Also present in charmlibs**:
**File**: `/home/ubuntu/charm-tech-analysis/charmlibs/passwd/src/charmlibs/passwd/_passwd.py`
**Lines**: 169, 175

**Suggested fix**:
```python
if gid is not None:
    ...
```

---

## Finding 6: `add_user()` falsy checks on `home_dir` and `password` treat empty strings as "not set" (operator-libs-linux + charmlibs)

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v0/passwd.py`
**Lines**: 150, 152
**Pattern**: Falsy value confusion
**Severity**: Low

**Evidence**:
```python
if home_dir:
    cmd.extend(["--home", str(home_dir)])
if password:
    cmd.extend(["--password", password])
```

**Why it is a bug**: An empty string `""` for `home_dir` or `password` would be treated as "no value provided", which may not be the caller's intent. While edge-case for `home_dir`, an explicitly empty password is meaningful in some contexts. This is minor compared to the UID/GID issue but follows the same falsy-check anti-pattern.

**Also present in charmlibs**:
**File**: `/home/ubuntu/charm-tech-analysis/charmlibs/passwd/src/charmlibs/passwd/_passwd.py`
**Lines**: 126, 128

**Suggested fix**: Use `if home_dir is not None:` and `if password is not None:`.

---

## Finding 7: `Snap.ensure()` in operator-libs-linux has logic error in revision comparison (operator-libs-linux only)

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v2/snap.py`
**Line**: 714
**Pattern**: Logic error -- wrong comparison due to None vs string
**Severity**: Medium

**Evidence** (line 714):
```python
elif revision is None or revision != self._revision:
```

**Why it is a bug**: The `ensure()` method parameters define `revision: str | None = None`. When `revision=None`, the condition `revision is None` is True, so the snap is ALWAYS refreshed even if nothing has changed (channel/cohort may be identical). This causes unnecessary refresh operations. Compare to the charmlibs version (line 645):
```python
elif revision != self._revision:
```
The charmlibs version converts `revision` to `str(revision)` or `''` earlier (line 616), so the comparison `'' != self._revision` correctly triggers a refresh only when the installed revision differs. The operator-libs-linux version has the original logic error: when the caller doesn't specify a revision, it should check channel changes instead, not blindly refresh.

**Suggested fix**: Convert revision to string early (as charmlibs does) and remove the `None` check:
```python
revision = revision or ""
...
elif revision != self._revision:
```

---

## Finding 8: `TypeError` constructor called with printf-style formatting instead of f-string (operator-libs-linux + charmlibs)

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v0/passwd.py`
**Lines**: 79, 100
**Pattern**: API contract issue -- wrong exception constructor usage
**Severity**: Medium

**Evidence** (line 79):
```python
raise TypeError("specified argument '%r' should be a string or int", user)
```
And line 100:
```python
raise TypeError("specified argument '%r' should be a string or int", group)
```

**Why it is a bug**: `TypeError` (and all `Exception` subclasses) does NOT support printf-style formatting in the constructor. This creates a `TypeError` with `args=("specified argument '%r' should be a string or int", <user_value>)`, meaning `str(error)` will show something like `("specified argument '%r' should be a string or int", True)` instead of the intended formatted message. The `%r` is never expanded -- it appears literally in the message.

**Also present in charmlibs**:
**File**: `/home/ubuntu/charm-tech-analysis/charmlibs/passwd/src/charmlibs/passwd/_passwd.py`
**Lines**: 56, 76

Same bug in the migrated code.

**Suggested fix**:
```python
raise TypeError(f"specified argument {user!r} should be a string or int")
```

---

## Finding 9: `add_user()` return type annotation is wrong in operator-libs-linux

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v0/passwd.py`
**Line**: 116
**Pattern**: Type annotation error
**Severity**: Low

**Evidence**:
```python
def add_user(
    ...
) -> str:
```

**Why it is a bug**: The function returns `pwd.getpwnam(username)` which is `pwd.struct_passwd`, not `str`. The type annotation lies to callers. The charmlibs version correctly annotates it as `-> pwd.struct_passwd`.

**Suggested fix**: Change return type to `-> pwd.struct_passwd`.

---

## Finding 10: `Snap.get()` with `typed=True` returns `None` for missing key without indication (operator-libs-linux + charmlibs)

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v2/snap.py`
**Lines**: 445-446
**Pattern**: Missing None guard / silent failure
**Severity**: Low

**Evidence**:
```python
config = json.loads(self._snap("get", args))  # json.loads -> Any
if key:
    return config.get(key)
```

**Why it is a bug**: When `typed=True` and a specific `key` is provided, `config.get(key)` returns `None` if the key doesn't exist in the parsed JSON. However, the return type annotation says `JSONType` (which doesn't include `None`). The caller has no way to distinguish "key is set to null" from "key doesn't exist" and the type system won't warn them about the `None` return. With `typed=False`, a missing key correctly raises `SnapError` from the snap CLI.

**Also present in charmlibs**:
**File**: `/home/ubuntu/charm-tech-analysis/charmlibs/snap/src/charmlibs/snap/_snap.py`
**Lines**: 377-378

**Suggested fix**: Use `config[key]` (which raises `KeyError`) or add `None` to the return type.

---

## Finding 11: `GrubConfig._lazy_data` is a class variable, shared across all instances (operator-libs-linux)

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v0/grub.py`
**Line**: 215
**Pattern**: Data mutability -- class-level mutable default
**Severity**: Medium

**Evidence**:
```python
class Config(Mapping[str, str]):
    _lazy_data: Optional[Dict[str, str]] = None

    def __init__(self, charm_name: str) -> None:
        self._charm_name = charm_name
```

**Why it is a bug**: `_lazy_data` is declared as a class variable with default `None`. Once any instance loads data (via `self._lazy_data = _load_config(...)` in `_data` property), it becomes an instance variable on that instance only. However, if two `Config` instances are created and the first loads data, the second still sees `None` at the class level and loads its own copy -- so this doesn't cause data sharing. BUT: the `_set_value` method mutates `self._data[key] = value`, and `remove` sets `self._lazy_data = config`. If an `ApplyError` rollback happens (lines 376-384), `self._lazy_data = snapshot` restores the snapshot, which is a `copy()` -- this is correct. The class-variable declaration is misleading but the code happens to work because Python creates an instance attribute on first assignment. This is a code smell rather than a hard bug, but could cause subtle issues if inheritance is involved.

**Suggested fix**: Initialize `_lazy_data` in `__init__`:
```python
def __init__(self, charm_name: str) -> None:
    self._charm_name = charm_name
    self._lazy_data: Optional[Dict[str, str]] = None
```

---

## Finding 12: `sysctl.Config` inherits from `Dict` but never calls `super().__init__()` (operator-libs-linux)

**Repo**: operator-libs-linux
**File**: `/home/ubuntu/charm-tech-analysis/operator-libs-linux/lib/charms/operator_libs_linux/v0/sysctl.py`
**Line**: 133
**Pattern**: API contract issue -- incorrect inheritance
**Severity**: Medium

**Evidence**:
```python
class Config(Dict):
    """Represents the state of the config that a charm wants to enforce."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._data = self._load_data()
```

**Why it is a bug**: `Config` inherits from `Dict` (i.e., `dict`) but:
1. Never calls `super().__init__()`, leaving the underlying dict empty.
2. Overrides `__contains__`, `__len__`, `__iter__`, `__getitem__` to delegate to `self._data` instead of the dict itself.
3. The underlying `dict` is always empty, so any `dict`-specific methods (`.keys()`, `.values()`, `.items()`, `.get()`, `.update()`, etc.) that are NOT overridden will operate on the empty dict, returning wrong results.

For example, `config.items()` will return an empty `dict_items` object because the parent `dict` is empty, while `config['key']` works because `__getitem__` is overridden. Similarly, `dict(config)` or `{**config}` will produce an empty dict. The class should either inherit from `Mapping` (like `GrubConfig` does) or properly populate the parent dict.

**Suggested fix**: Change inheritance to `Mapping` (from `collections.abc`) instead of `Dict`/`dict`, and add proper abstract method implementations.

---

## Finding 13: `pytest-jubilant` `TempModelFactory.get_juju()` catches wrong exception attribute

**Repo**: pytest-jubilant
**File**: `/home/ubuntu/charm-tech-analysis/pytest-jubilant/pytest_jubilant/_main.py`
**Line**: 125
**Pattern**: Error handling -- wrong exception attribute access
**Severity**: Medium

**Evidence**:
```python
except jubilant.CLIError as e:
    if "already exists on this k8s cluster" in e.args[1] and self._check_models_unique:
        raise
```

**Why it is a bug**: `CLIError` is a subclass of `subprocess.CalledProcessError`, constructed as `CLIError(e.returncode, e.cmd, e.stdout, e.stderr)`. So `e.args` is `(returncode, cmd, stdout, stderr)`, meaning `e.args[1]` is the command list (e.g., `['juju', 'add-model', ...]`), not the error message. The string check `"already exists on this k8s cluster" in e.args[1]` is checking if that substring exists in the command list, which will almost always be False. The correct attribute to check would be `e.stderr` (which is `e.args[3]`).

**Suggested fix**:
```python
if "already exists on this k8s cluster" in (e.stderr or "") and self._check_models_unique:
```

---

## Finding 14: `temp_model` context manager in `_test_helpers.py` does not clean up model on `add_model` failure

**Repo**: jubilant
**File**: `/home/ubuntu/charm-tech-analysis/jubilant/jubilant/_test_helpers.py`
**Lines**: 51-71
**Pattern**: Context manager safety
**Severity**: Low

**Evidence**:
```python
juju = Juju()
model = 'jubilant-' + secrets.token_hex(4)
juju.add_model(model, cloud=cloud, controller=controller, config=config, credential=credential)
try:
    yield juju
finally:
    if not keep:
        ...
```

**Why it is a bug**: If `add_model` partially succeeds (creates the model but raises an exception during setup), the model is left orphaned because the `try/finally` block hasn't been entered yet. The `yield` is inside the `try`, but `add_model` is outside it. In practice this is mitigated by the fact that `add_model` either fully succeeds or fully fails from the CLI perspective, but it's a code smell.

This is minor because `add_model` is atomic at the Juju CLI level.

---

## Finding 15: `Snap.logs()` in charmlibs accepts `num_lines: int | Literal['all']` but still uses falsy check

**Repo**: charmlibs
**File**: `/home/ubuntu/charm-tech-analysis/charmlibs/snap/src/charmlibs/snap/_snap.py`
**Lines**: 427, 434
**Pattern**: Falsy value confusion
**Severity**: Medium

**Evidence**:
```python
def logs(self, services: list[str] | None = None, num_lines: int | Literal['all'] = 10) -> str:
    ...
    args = ['logs', f'-n={num_lines}'] if num_lines else ['logs']
```

**Why it is a bug**: The type signature was updated to accept `'all'` (fixing the type-confusion bug from commit `d1262302`), but the falsy check `if num_lines` was not updated. If `num_lines=0` is passed, it will be treated as falsy and fall through to `['logs']`. While `0` is uncommon, the pattern is incorrect. The `'all'` value works correctly since non-empty strings are truthy.

**Suggested fix**:
```python
args = ['logs', f'-n={num_lines}'] if num_lines is not None else ['logs']
```

---

## Summary Table

| # | Repo | File (basename) | Line(s) | Pattern | Severity |
|---|------|-----------------|---------|---------|----------|
| 1 | operator-libs-linux + charmlibs | snap.py / _snap.py | 600,602,604,627,629,645 / 531,533,535,558,561,576 | API contract (spurious quotes in snap CLI args) | High |
| 2 | operator-libs-linux + charmlibs | snap.py / _snap.py | 503 / 434 | Falsy value confusion (`num_lines=0`) | Medium |
| 3 | operator-libs-linux + charmlibs | snap.py / _snap.py | 780-783 / 710-714 | Data mutability (apps returns internal list) | Medium |
| 4 | operator-libs-linux + charmlibs | passwd.py / _passwd.py | 136,148 / 112,124 | Falsy value confusion (`uid=0`) | High |
| 5 | operator-libs-linux + charmlibs | passwd.py / _passwd.py | 193,199 / 169,175 | Falsy value confusion (`gid=0`) | Medium |
| 6 | operator-libs-linux + charmlibs | passwd.py / _passwd.py | 150,152 / 126,128 | Falsy value confusion (empty string) | Low |
| 7 | operator-libs-linux | snap.py | 714 | Logic error (unnecessary refresh) | Medium |
| 8 | operator-libs-linux + charmlibs | passwd.py / _passwd.py | 79,100 / 56,76 | API contract (wrong exception constructor) | Medium |
| 9 | operator-libs-linux | passwd.py | 116 | Type annotation error | Low |
| 10 | operator-libs-linux + charmlibs | snap.py / _snap.py | 445-446 / 377-378 | Missing None guard (silent None return) | Low |
| 11 | operator-libs-linux | grub.py | 215 | Data mutability (class-level mutable) | Medium |
| 12 | operator-libs-linux | sysctl.py | 133 | API contract (incorrect Dict inheritance) | Medium |
| 13 | pytest-jubilant | _main.py | 125 | Error handling (wrong exception attribute) | Medium |
| 14 | jubilant | _test_helpers.py | 51-53 | Context manager safety | Low |
| 15 | charmlibs | _snap.py | 434 | Falsy value confusion | Medium |

**Totals**: 15 findings (2 High, 9 Medium, 4 Low)

**Most common pattern**: Falsy value confusion (Findings 2, 4, 5, 6, 15) -- exactly matching the known ecosystem pattern from commit `1c0ff40d` and section 3.5.

**Cross-repo propagation**: Findings 1-6, 8, 10 exist in both operator-libs-linux and charmlibs because charmlibs was documented as a "bug-for-bug compatible migration" of the operator-libs-linux libraries. The bugs were faithfully copied.
