## Bug Review: charmlibs snap and passwd libraries

### Summary
- **Findings**: 7 (1 Critical, 3 High, 2 Medium, 1 Low)
- **Code areas reviewed**: Snap CLI interaction, System libraries (passwd), Error handling, Data mutability, Falsy value confusion
- **Repos affected**: charmlibs (snap, passwd)

### Findings

#### [BUG-001] Snap CLI — Spurious embedded quotes in `_install` and `_refresh` (High)
- **Location**: `snap/src/charmlibs/snap/_snap.py:531-535` and `snap/src/charmlibs/snap/_snap.py:558-576`
- **Pattern**: Snap CLI embedded quotes (from `references/anti-patterns.md`)
- **Issue**: The `_install` and `_refresh` methods embed literal `"` characters inside subprocess arguments using f-strings like `f'--channel="{channel}"'`. When arguments are passed as a list to `subprocess.check_output`, each element is passed directly to the process without shell interpretation. The literal `"` characters become part of the argument value, so snap receives `--channel="latest/edge"` instead of `--channel=latest/edge`.
- **Impact**: Snap install and refresh operations pass malformed arguments to the `snap` command. The snap CLI may reject the channel/revision/cohort value or interpret it incorrectly because the value includes literal quote characters. This affects `_install` (channel, revision, cohort) and `_refresh` (channel, revision, cohort) -- 6 occurrences total.
- **Evidence**:
  ```python
  # _install (lines 531-535)
  if channel:
      args.append(f'--channel="{channel}"')
  if revision:
      args.append(f'--revision="{revision}"')
  if cohort:
      args.append(f'--cohort="{cohort}"')

  # _refresh (lines 558-576)
  if channel:
      args.append(f'--channel="{channel}"')
  if revision:
      args.append(f'--revision="{revision}"')
  # ...
  elif cohort:
      args.append(f'--cohort="{cohort}"')
  ```
- **Recommended fix**:
  ```python
  if channel:
      args.append(f'--channel={channel}')
  if revision:
      args.append(f'--revision={revision}')
  if cohort:
      args.append(f'--cohort={cohort}')
  ```
- **Historical precedent**: Known current bug documented in `references/bug-patterns.md` under "Snap CLI: Spurious embedded quotes". Exists in both operator-libs-linux and charmlibs.

---

#### [BUG-002] Falsy Value — `if uid` drops UID 0 (root) in `add_user` (High)
- **Location**: `passwd/src/charmlibs/passwd/_passwd.py:112` and `passwd/src/charmlibs/passwd/_passwd.py:124`
- **Pattern**: Falsy value confusion (from `references/anti-patterns.md`)
- **Issue**: `add_user()` uses `if uid:` to check whether a UID was provided. UID 0 (root) is a valid UID but is falsy in Python, so passing `uid=0` skips both the existence check and the `--uid` flag in the `useradd` command.
- **Impact**: When `uid=0` is passed to `add_user()`: (1) the existence check on line 112 is skipped, so the function does not detect that UID 0 already exists; (2) the `--uid 0` argument on line 124 is not added to the command, so `useradd` assigns a system-allocated UID instead of 0. The caller's explicit request for UID 0 is silently ignored.
- **Evidence**:
  ```python
  # Line 112: existence check skipped for uid=0
  if uid:
      user_info = pwd.getpwuid(int(uid))
      logger.info("user '%d' already exists", uid)
      return user_info

  # Line 124: --uid flag omitted for uid=0
  if uid:
      cmd.extend(['--uid', str(uid)])
  ```
- **Recommended fix**:
  ```python
  if uid is not None:
      user_info = pwd.getpwuid(int(uid))
      ...

  if uid is not None:
      cmd.extend(['--uid', str(uid)])
  ```
- **Historical precedent**: Documented in `references/bug-patterns.md` under "UID/GID 0 (root user/group)". Exists in both operator-libs-linux and charmlibs.

---

#### [BUG-003] Falsy Value — `if gid` drops GID 0 (root) in `add_group` (High)
- **Location**: `passwd/src/charmlibs/passwd/_passwd.py:169` and `passwd/src/charmlibs/passwd/_passwd.py:175`
- **Pattern**: Falsy value confusion (from `references/anti-patterns.md`)
- **Issue**: `add_group()` uses `if gid:` to check whether a GID was provided. GID 0 (root group) is a valid GID but is falsy, so passing `gid=0` skips both the GID existence check and the `--gid` flag in the `addgroup` command.
- **Impact**: When `gid=0` is passed to `add_group()`: (1) the GID existence check on line 169 is skipped; (2) the `--gid 0` argument on line 175 is not added to the command. The caller's explicit request for GID 0 is silently ignored.
- **Evidence**:
  ```python
  # Line 169: existence check skipped for gid=0
  if gid:
      group_info = grp.getgrgid(gid)
      logger.info("group with gid '%d' already exists", gid)

  # Line 175: --gid flag omitted for gid=0
  if gid:
      cmd.extend(['--gid', str(gid)])
  ```
- **Recommended fix**:
  ```python
  if gid is not None:
      group_info = grp.getgrgid(gid)
      ...

  if gid is not None:
      cmd.extend(['--gid', str(gid)])
  ```
- **Historical precedent**: Documented in `references/bug-patterns.md` under "UID/GID 0 (root user/group)". Exists in both operator-libs-linux and charmlibs.

---

#### [BUG-004] Error Handling — Printf-style exception constructors in `user_exists` and `group_exists` (Medium)
- **Location**: `passwd/src/charmlibs/passwd/_passwd.py:56` and `passwd/src/charmlibs/passwd/_passwd.py:76`
- **Pattern**: Printf-style exception constructors (from `references/anti-patterns.md`)
- **Issue**: `TypeError` is raised with printf-style formatting: `raise TypeError("specified argument '%r' should be a string or int", user)`. Python's `TypeError` constructor does not perform printf formatting -- the `%r` appears literally in the error message, and the `user` value is stored as a separate element in `args` but is not interpolated into the message string.
- **Impact**: When a non-str, non-int value is passed to `user_exists()` or `group_exists()`, the error message reads literally `"specified argument '%r' should be a string or int"` followed by the value as a separate tuple element, rather than showing the formatted representation of the argument. This makes debugging harder.
- **Evidence**:
  ```python
  # Line 56
  raise TypeError("specified argument '%r' should be a string or int", user)
  # Line 76
  raise TypeError("specified argument '%r' should be a string or int", group)
  ```
- **Recommended fix**:
  ```python
  raise TypeError(f"specified argument {user!r} should be a string or int")
  raise TypeError(f"specified argument {group!r} should be a string or int")
  ```
- **Historical precedent**: Documented in `references/bug-patterns.md` under "Printf-style exception constructors". Known current bug in operator-libs-linux and charmlibs.

---

#### [BUG-005] Falsy Value — `if num_lines` drops `num_lines=0` in `Snap.logs` (Medium)
- **Location**: `snap/src/charmlibs/snap/_snap.py:434`
- **Pattern**: Falsy value confusion (from `references/anti-patterns.md`)
- **Issue**: `Snap.logs()` uses `if num_lines` to decide whether to include the `-n` flag. When `num_lines=0`, the check is falsy, so the `-n=0` argument is omitted. This causes snap to return its default number of log lines instead of 0.
- **Impact**: Calling `snap.logs(num_lines=0)` returns the default number of log lines instead of none. The test on line 356 of `test_snap.py` confirms this behavior with the comment "falsey num_lines is ignored", meaning the bug is codified in tests rather than fixed.
- **Evidence**:
  ```python
  args = ['logs', f'-n={num_lines}'] if num_lines else ['logs']
  ```
- **Recommended fix**:
  ```python
  args = ['logs', f'-n={num_lines}'] if num_lines is not None else ['logs']
  ```
- **Historical precedent**: Documented in `references/bug-patterns.md` under "Numeric parameters". Known current bug in operator-libs-linux and charmlibs.

---

#### [BUG-006] Mutability — `Snap.apps` returns internal `_apps` list without copy (Medium)
- **Location**: `snap/src/charmlibs/snap/_snap.py:711-714`
- **Pattern**: Returning internal state without copy (from `references/anti-patterns.md`)
- **Issue**: The `apps` property returns `self._apps` directly. While it first calls `_update_snap_apps()` to refresh the list from snapd, the returned list is the same object stored internally. A caller who appends to, removes from, or clears the returned list would corrupt the `Snap` object's internal state.
- **Impact**: If a caller mutates the returned list (e.g., `snap.apps.append(...)` or `snap.apps.clear()`), the internal `_apps` list is mutated, causing subsequent property accesses (`apps`, `services`) to return corrupted data until the next refresh.
- **Evidence**:
  ```python
  @property
  def apps(self) -> list[dict[str, JSONType]]:
      """Returns (if any) the installed apps of the snap."""
      self._update_snap_apps()
      return self._apps
  ```
- **Recommended fix**:
  ```python
  @property
  def apps(self) -> list[dict[str, JSONType]]:
      """Returns (if any) the installed apps of the snap."""
      self._update_snap_apps()
      return list(self._apps)
  ```
- **Historical precedent**: Documented in `references/bug-patterns.md` under "Returning internal state without copy". `Snap.apps` is listed as a known current bug in operator-libs-linux and charmlibs.

---

#### [BUG-007] Security — Password passed via command-line argument in `add_user` (Critical)
- **Location**: `passwd/src/charmlibs/passwd/_passwd.py:128-129`
- **Pattern**: Novel (security concern)
- **Issue**: The `add_user` function passes the password as a command-line argument to `useradd` via `cmd.extend(['--password', password])`. Command-line arguments are visible to all users on the system via `/proc/*/cmdline` and tools like `ps aux`. This exposes the password in plaintext to any user who can list processes during the brief window the command is running. The `useradd` man page warns against this: "the password will be visible to users listing the processes."
- **Impact**: Any local user on the system can observe the plaintext password by monitoring process listings during user creation. This is a privilege escalation vector: a low-privilege user could capture credentials for a newly-created account.
- **Evidence**:
  ```python
  if password:
      cmd.extend(['--password', password])
  ```
- **Recommended fix**: Use `chpasswd` via stdin to set the password after user creation, which does not expose the password on the command line:
  ```python
  # Create user without password
  check_output(cmd, stderr=STDOUT)
  # Set password via stdin
  if password:
      proc = subprocess.run(
          ['chpasswd'],
          input=f'{username}:{password}',
          text=True,
          check=True,
          capture_output=True,
      )
  ```
- **Historical precedent**: Novel finding. Related to the general "Security" pattern in `references/bug-patterns.md` regarding information leaks, though this specific case is not documented.

---

### Confirmed Safe

- **`Snap.name`, `Snap.revision`, `Snap.channel`, `Snap.confinement`, `Snap.version`**: These properties return immutable types (`str`, `str | None`), so returning `self._name`, etc. without copy is correct.
- **`Snap.state`**: Returns a `SnapState` enum value, which is immutable.
- **`Snap.present`, `Snap.latest`**: Return `bool`, immutable.
- **`SnapService.daemon_scope` using `kwargs.get('daemon-scope') or daemon_scope`**: The `or` here is safe because both values are strings and an empty string daemon-scope is not meaningful -- it would indicate "not set" and falling through to `daemon_scope` is correct.
- **`self._cohort = cohort or ''`** (line 277): Safe because `cohort` is either `str` or `None`, and empty string cohort means "no cohort" which is equivalent to `None`.
- **`self._apps = apps or []`** (line 278): Safe because `apps` is either a list or `None`, and an empty list is the intended default.
- **`optargs = optargs or []`** (line 316): Safe because `optargs` is either an iterable or `None`.
- **`if channel:` in `_install`/`_refresh`**: The `channel` parameter defaults to `''` (empty string), so the falsy check correctly distinguishes "no channel provided" from a channel value. Channel strings are never empty when provided.
- **`if password:` in `add_user`**: Password is always a non-empty string when provided. An empty string password is not meaningful.
- **`if home_dir:` in `add_user`**: Home directory is always a non-empty path string when provided. An empty string path is not meaningful.
- **`datetime.now(timezone.utc)`** in `hold_refresh` (line 1327): Correctly uses timezone-aware datetime.
- **`__all__` in both `snap/__init__.py` and `passwd/__init__.py`**: All names listed in `__all__` exist and are correctly imported.
