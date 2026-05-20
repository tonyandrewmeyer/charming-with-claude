## Bug Review: Pebble — servstate (service management) and osutil (file operations)

### Summary
- **Findings**: 7 (1 High, 4 Medium, 2 Low)
- **Code areas reviewed**: `internals/overlord/servstate/` (manager.go, handlers.go, request.go), `internals/osutil/` (io.go, mkdir.go, user.go, exec.go, stat.go, bootid.go, env.go, exitcode.go, outputerr.go, sys/syscall.go)

### Findings

#### [BUG-001] [Resource Leak] — NewAtomicFile leaks FD and temp file on Chmod error (Medium)
- **Location**: `internals/osutil/io.go:105-109`
- **Pattern**: Resource leaks: file descriptors
- **Issue**: When `AtomicWriteChmod` is set and `fd.Chmod(perm)` fails, the function returns the error without closing the file descriptor or removing the temporary file. The comment at line 73 says "It is the caller's responsibility to clean up on error, by calling Cancel()" but at the point of this error, no `AtomicFile` struct has been returned to the caller, so `Cancel()` cannot be called. The caller receives `(nil, err)` and has no way to clean up.
- **Impact**: Leaked file descriptor and orphaned temp file on disk when Chmod fails. In long-running daemons, repeated failures could exhaust file descriptors.
- **Evidence**:
  ```go
  fd, err := os.OpenFile(tmp, os.O_WRONLY|os.O_CREATE|os.O_TRUNC|os.O_EXCL, perm)
  if err != nil {
      return nil, err
  }

  if flags&AtomicWriteChmod != 0 {
      err := fd.Chmod(perm)
      if err != nil {
          return nil, err // fd not closed, tmp not removed
      }
  }
  ```
- **Recommended fix**:
  ```go
  if flags&AtomicWriteChmod != 0 {
      if err := fd.Chmod(perm); err != nil {
          fd.Close()
          os.Remove(tmp)
          return nil, err
      }
  }
  ```
- **Historical precedent**: Pebble entry 100 (resource leak patterns), referenced in bug-patterns.md as a current known bug in `NewAtomicFile`.

---

#### [BUG-002] [Resource Leak] — mkdir leaves candidate directory on error (Medium)
- **Location**: `internals/osutil/mkdir.go:129-150`
- **Pattern**: Resource leaks: file descriptors (adapted to directory cleanup)
- **Issue**: The `mkdir` function creates a candidate directory at `path + ".mkdir-new"` (line 130), then performs Chown (line 137), Chmod (line 143), and Rename (line 148). If any of Chown, Chmod, or Rename fails, the function returns the error without removing the candidate directory.
- **Impact**: Orphaned `.mkdir-new` directories left on disk after failed operations. On retry, `os.Mkdir(cand, perm)` at line 132 succeeds because `os.IsExist(err)` is ignored, masking the issue, but the stale directory may have wrong ownership/permissions from a previous partial attempt.
- **Evidence**:
  ```go
  cand := path + ".mkdir-new"

  if err := os.Mkdir(cand, perm); err != nil && !os.IsExist(err) {
      return err
  }

  if options.Chown {
      if err := sys.ChownPath(cand, options.UserID, options.GroupID); err != nil {
          return err // cand not removed
      }
  }

  if options.Chmod {
      if err := os.Chmod(cand, perm); err != nil {
          return err // cand not removed
      }
  }
  ```
- **Recommended fix**:
  ```go
  cand := path + ".mkdir-new"

  if err := os.Mkdir(cand, perm); err != nil && !os.IsExist(err) {
      return err
  }

  if options.Chown {
      if err := sys.ChownPath(cand, options.UserID, options.GroupID); err != nil {
          os.Remove(cand)
          return err
      }
  }

  if options.Chmod {
      if err := os.Chmod(cand, perm); err != nil {
          os.Remove(cand)
          return err
      }
  }

  if err := os.Rename(cand, path); err != nil {
      os.Remove(cand)
      return err
  }
  ```

---

#### [BUG-003] [Dead Code / Latent Bug] — Slice modification during iteration in Replan (Low)
- **Location**: `internals/overlord/servstate/manager.go:301-305`
- **Pattern**: Novel
- **Issue**: The loop at lines 301-305 iterates over `stop` and modifies it in-place using `stop = append(stop[:i], stop[i+1:]...)`. This is a classic slice-modification-during-iteration bug that skips elements. However, this code is currently unreachable: every element added to `stop` (line 287) also has `needsRestart[name] = true` (line 286), so the condition `!needsRestart[name]` at line 302 is never true.
- **Impact**: No current impact (dead code). If future changes alter the logic such that `stop` can contain names where `needsRestart[name]` is false, the slice modification would silently skip elements, leading to services not being stopped correctly during replan.
- **Evidence**:
  ```go
  for i, name := range stop {
      if !needsRestart[name] {
          stop = append(stop[:i], stop[i+1:]...)
      }
  }
  ```
- **Recommended fix**: Remove the dead code block entirely, or if the intent was to filter, use a proper filter pattern:
  ```go
  filtered := stop[:0]
  for _, name := range stop {
      if needsRestart[name] {
          filtered = append(filtered, name)
      }
  }
  stop = filtered
  ```
- **Historical precedent**: Referenced in bug-patterns.md as a current finding at pebble servstate/manager.go lines 301-305.

---

#### [BUG-004] [Error Handling] — Error wrapping uses %s/%v instead of %w (Medium)
- **Location**: `internals/osutil/user.go:84,88`, `internals/osutil/exec.go:110`, `internals/overlord/servstate/handlers.go:185`
- **Pattern**: Error handling: %s/%v wrapping
- **Issue**: Several error wrapping sites use `%s` or `%v` instead of `%w`, breaking the `errors.Is`/`errors.As` chain for callers that need to inspect the underlying error.
- **Impact**: Callers cannot use `errors.Is` or `errors.As` to programmatically match the underlying error. For `osutil/user.go` (lines 84, 88), callers of `UidGid` cannot distinguish parse errors from other errors. For `exec.go:110`, callers cannot check if `KillProcessGroup` returned a specific syscall error.
- **Evidence**:
  ```go
  // user.go:84
  return sys.FlagID, sys.FlagID, fmt.Errorf("cannot parse user id %s: %s", u.Uid, err)
  // user.go:88
  return sys.FlagID, sys.FlagID, fmt.Errorf("cannot parse group id %s: %s", u.Gid, err)
  // exec.go:110
  return nil, fmt.Errorf("cannot abort: %s", err)
  // handlers.go:185
  return fmt.Errorf("start aborted, but cannot send SIGKILL to process: %v", err)
  ```
- **Recommended fix**:
  ```go
  // user.go:84
  return sys.FlagID, sys.FlagID, fmt.Errorf("cannot parse user id %s: %w", u.Uid, err)
  // user.go:88
  return sys.FlagID, sys.FlagID, fmt.Errorf("cannot parse group id %s: %w", u.Gid, err)
  // exec.go:110
  return nil, fmt.Errorf("cannot abort: %w", err)
  // handlers.go:185
  return fmt.Errorf("start aborted, but cannot send SIGKILL to process: %w", err)
  ```

---

#### [BUG-005] [Security] — ChownPath follows symlinks (Medium)
- **Location**: `internals/osutil/sys/syscall.go:82-85`
- **Pattern**: Security: os.Chown vs os.Lchown
- **Issue**: `ChownPath` calls `FchownAt` with `flags=0`, which means it follows symlinks. If an attacker can create a symlink at the candidate directory path (e.g., during `mkdir`'s `.mkdir-new` creation), the chown would follow the symlink and change ownership of the target file.
- **Impact**: In the current call site (`osutil/mkdir.go:137`), the candidate path is `path + ".mkdir-new"` which was just created by the function via `os.Mkdir`. The race window is narrow (between `os.Mkdir` creating the directory and `ChownPath` being called), and exploitability requires the attacker to delete the just-created directory and replace it with a symlink, which requires write access to the parent directory. This makes exploitation unlikely in practice but the pattern is still unsafe by principle.
- **Evidence**:
  ```go
  func ChownPath(path string, uid UserID, gid GroupID) error {
      AT_FDCWD := -100
      return FchownAt(uintptr(AT_FDCWD), path, uid, gid, 0) // flags=0, follows symlinks
  }
  ```
- **Recommended fix**: Use `AT_SYMLINK_NOFOLLOW` flag:
  ```go
  func ChownPath(path string, uid UserID, gid GroupID) error {
      AT_FDCWD := -100
      AT_SYMLINK_NOFOLLOW := 0x100
      return FchownAt(uintptr(AT_FDCWD), path, uid, gid, AT_SYMLINK_NOFOLLOW)
  }
  ```
- **Historical precedent**: Concierge commit `39a18ffc` fixed os.Chown to os.Lchown.

---

#### [BUG-006] [Concurrency] — TOCTOU between getPlan and servicesLock in multiple methods (High)
- **Location**: `internals/overlord/servstate/manager.go:120-122` (Services), `internals/overlord/servstate/manager.go:262-265` (Replan), `internals/overlord/servstate/manager.go:419-434` (servicesToStop), `internals/overlord/servstate/handlers.go:132-133` (doStart)
- **Pattern**: Concurrency: TOCTOU between lock releases
- **Issue**: Multiple methods call `getPlan()` (which acquires and releases `planLock`) and then acquire `servicesLock` separately. Between these two operations, another goroutine can call `PlanChanged()`, replacing the plan. The code then operates on a stale plan snapshot while holding `servicesLock`.

  For example, in `Replan()`:
  1. `getPlan()` returns plan A (planLock released)
  2. Another goroutine calls `PlanChanged()` with plan B
  3. `servicesLock` is acquired
  4. Code compares services against stale plan A

  In `doStart()`:
  1. `getPlan()` returns plan A with service config
  2. `PlanChanged()` removes or modifies the service
  3. `serviceForStart` is called, creating a service with the old config

- **Impact**: Service configurations could be stale when starting, stopping, or replanning services. For `Replan`, services could be restarted unnecessarily or fail to restart when they should. For `doStart`, a service could be started with a configuration that has already been superseded. The impact is mitigated by the plan being treated as immutable after retrieval, and by the fact that replans are relatively infrequent operations.
- **Evidence**:
  ```go
  // manager.go:119-122 — gap between getPlan() and servicesLock
  func (m *ServiceManager) Services(names []string) ([]*ServiceInfo, error) {
      currentPlan := m.getPlan()    // planLock acquired and released
      m.servicesLock.Lock()         // servicesLock acquired — plan may have changed
      defer m.servicesLock.Unlock()
  ```
- **Recommended fix**: This is an architectural tension between avoiding multi-lock deadlocks and achieving atomicity. The current approach (documented in bug-patterns.md as a known trade-off) avoids deadlocks by never holding both locks simultaneously, but creates a TOCTOU window. A fix could involve acquiring both locks in a consistent order (always `planLock` then `servicesLock`) or using an atomic pointer for the plan to avoid the lock entirely.
- **Historical precedent**: Pebble entries 73-79 (multi-lock deadlock patterns). The current design is an intentional mitigation that trades TOCTOU for deadlock safety.

---

#### [BUG-007] [Error Handling] — SendSignal constructs error string instead of using errors (Low)
- **Location**: `internals/overlord/servstate/manager.go:319-336`
- **Pattern**: Novel
- **Issue**: `SendSignal` collects errors as formatted strings in a `[]string` slice named `errors` (shadowing the `errors` package import, though it's not imported), then joins them with `; ` and wraps in `fmt.Errorf("%s", ...)`. This discards all structured error information and makes it impossible for callers to inspect individual errors or use `errors.Is`/`errors.As`.
- **Impact**: Callers cannot programmatically determine which services failed or why. All error context is flattened into a single string. This is a code quality issue rather than a runtime bug.
- **Evidence**:
  ```go
  var errors []string
  for _, name := range services {
      s := m.services[name]
      if s == nil {
          errors = append(errors, fmt.Sprintf("cannot send signal to %q: service is not running", name))
          continue
      }
      err := s.sendSignal(signal)
      if err != nil {
          errors = append(errors, fmt.Sprintf("cannot send signal to %q: %v", name, err))
          continue
      }
  }
  if len(errors) > 0 {
      return fmt.Errorf("%s", strings.Join(errors, "; "))
  }
  ```
- **Recommended fix**: Use `errors.Join` to preserve structured errors:
  ```go
  var errs []error
  for _, name := range services {
      s := m.services[name]
      if s == nil {
          errs = append(errs, fmt.Errorf("cannot send signal to %q: service is not running", name))
          continue
      }
      if err := s.sendSignal(signal); err != nil {
          errs = append(errs, fmt.Errorf("cannot send signal to %q: %w", name, err))
      }
  }
  return errors.Join(errs...)
  ```

---

### Confirmed Safe

| Pattern | Location | Why it's safe |
|---------|----------|---------------|
| `defer m.servicesLock.Unlock()` in single-lock functions | `manager.go` (StopTimeout, Services, CheckFailed, WriteMetrics, Prune, etc.) | No other lock acquired within scope |
| `m.state.Lock()` / `m.state.Unlock()` in `doStart`/`doStop` | `handlers.go:117-120, 125-128, 155-157` | State lock acquired and released before `servicesLock` is used; no overlap |
| `m.randLock.Lock()` inside `getJitter` | `handlers.go:656` | Only called while `servicesLock` is held; `randLock` is never held when acquiring `servicesLock`, so lock order is consistent |
| `noticeCond.Broadcast()` in state notices | `state/notices.go:282,457` | Called inside `s.writing()` which holds the state lock |
| `executionsCond.Broadcast()` in cmdstate | `cmdstate/manager.go:67, handlers.go:114` | Called while the executions mutex is held |
| `strings.Contains(err.Error(), enoentMessage)` in `user.go` | `user.go:67,104,120,138` | Explicitly documented as workaround for Go issue #67912, with code comments |
| `var services []*ServiceInfo` nil slice in `Services()` | `manager.go:129` | The API handler at `api_services.go:47` creates `make([]serviceInfo, 0, len(services))` before marshaling, so nil slices don't reach JSON output |
| `defer file.Close()` in `BootID` | `bootid.go:29` | Read-only file, error from Close is inconsequential |
| `defer fd.Close()` in `mkdir` | `mkdir.go:156` | Read-only directory fd opened for Sync, error from Close is inconsequential |
| `defer dir.Close()` in `AtomicFile.Commit` | `io.go:176` | Read-only directory fd opened for Sync |
| `tomb.Tomb` parameter in `doStart`/`doStop` | `handlers.go:115,248` | Tomb is provided by the task runner with a goroutine already running; no risk of blocking `Wait()` |
| `sys.Chown(f, uid, gid)` via `fchown` in `AtomicFile.Commit` | `io.go:163` | Uses file descriptor (not path), so cannot follow symlinks |
