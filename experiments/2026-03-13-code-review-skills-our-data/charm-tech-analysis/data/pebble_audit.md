# Pebble Bug Audit Report

Audit of `canonical/pebble` HEAD against known Go-specific bug patterns from `CROSS_REPO_PATTERNS.md` (sections 4 and 5).

---

## Finding 1: File Descriptor and Temp File Leak in `NewAtomicFile`

**File**: `/home/ubuntu/charm-tech-analysis/pebble/internals/osutil/io.go`, lines 100-110
**Pattern**: Resource leak
**Severity**: Medium

**Evidence**:
```go
func NewAtomicFile(filename string, perm os.FileMode, flags AtomicWriteFlags, uid sys.UserID, gid sys.GroupID) (aw *AtomicFile, err error) {
    // ...
    fd, err := os.OpenFile(tmp, os.O_WRONLY|os.O_CREATE|os.O_TRUNC|os.O_EXCL, perm)
    if err != nil {
        return nil, err
    }

    if flags&AtomicWriteChmod != 0 {
        err := fd.Chmod(perm)
        if err != nil {
            return nil, err  // BUG: fd is leaked, temp file left on disk
        }
    }
    // ...
}
```

**Why this is a real bug**: When `fd.Chmod(perm)` fails (e.g., filesystem doesn't support chmod, or permission denied), the function returns `nil, err` without closing `fd` and without removing the temp file `tmp` from disk. The caller receives a nil `AtomicFile`, so there is no way to clean up the leaked file descriptor or the orphaned temporary file.

**Suggested fix**: Close `fd` and remove the temp file before returning on error:
```go
if flags&AtomicWriteChmod != 0 {
    err := fd.Chmod(perm)
    if err != nil {
        fd.Close()
        os.Remove(tmp)
        return nil, err
    }
}
```

---

## Finding 2: String-Based Error Matching for User/Group Lookup

**File**: `/home/ubuntu/charm-tech-analysis/pebble/internals/osutil/user.go`, lines 67, 104, 120, 138
**Pattern**: String-based error matching (`strings.Contains(err.Error()...)`)
**Severity**: Low

**Evidence**:
```go
var enoentMessage = syscall.ENOENT.Error()

// Line 67:
if err != nil && strings.Contains(err.Error(), enoentMessage) {
    return cur, nil
}

// Line 104:
if strings.Contains(err.Error(), enoentMessage) {
    return nil, nil, user.UnknownUserError(username)
}
```

**Why this is a noted concern**: The code explicitly documents this as a workaround for Go issue #67912 where `user.Lookup` doesn't return `UnknownUserError` when it should. The `enoentMessage` match (`"no such file or directory"`) is reasonably specific, but could match errors unrelated to the user not being found (e.g., missing `/etc/passwd` file vs. user not in that file). The four call sites all use the same pattern.

This is an acknowledged fragile pattern rather than an undiscovered bug -- the code comments reference the upstream Go issue. However, if Go changes the error message string for `ENOENT` in a future version, all four checks would silently break.

**Suggested fix**: When the upstream Go bug (#67912) is fixed in the minimum Go version required by Pebble, these workarounds should be removed. Until then, using `errors.Is(err, syscall.ENOENT)` on the unwrapped error would be more robust, though it may not work if the `user` package wraps the error without using `%w`.

---

## Finding 3: Replan Dead Code -- Slice Modification Loop Never Executes

**File**: `/home/ubuntu/charm-tech-analysis/pebble/internals/overlord/servstate/manager.go`, lines 301-305
**Pattern**: Logic error (dead code / misleading)
**Severity**: Low

**Evidence**:
```go
func (m *ServiceManager) Replan() ([][]string, [][]string, error) {
    // ...
    needsRestart := make(map[string]bool)
    var stop []string
    for name, s := range m.services {
        // ... (various continue conditions)
        needsRestart[name] = true   // line 286
        stop = append(stop, name)   // line 287
    }
    // ...
    stopLanes, err := currentPlan.StopOrder(stop)
    // ...
    for i, name := range stop {
        if !needsRestart[name] {                    // line 302: always false
            stop = append(stop[:i], stop[i+1:]...)  // line 303: never executed
        }
    }
    // ...
}
```

**Why this is a real issue**: Every element in `stop` was added at the same time `needsRestart[name]` was set to `true` (lines 286-287). Therefore `needsRestart[name]` is always `true` for every element in `stop`, and the removal condition on line 302 is always false. The loop body never executes.

If the loop body *could* execute, it would also be buggy: modifying a slice with `append(stop[:i], stop[i+1:]...)` while iterating over it with `range` skips elements (the classic "delete during iteration" bug in Go). This suggests the code was either: (a) left over from a refactor that changed how `stop` is populated, or (b) written with the intent to filter but the filter became redundant.

While not a runtime bug (the dead code is harmless), the presence of a buggy-if-reached slice modification pattern is a code quality concern and could become a real bug if the surrounding logic changes.

**Suggested fix**: Remove the dead loop (lines 301-305) entirely. The `stop` variable is not used after this point -- only `stopLanes` and `startLanes` are returned.

---

## Finding 4: Lock Ordering Risk Between `planLock` and `servicesLock`

**File**: `/home/ubuntu/charm-tech-analysis/pebble/internals/overlord/servstate/manager.go`
**Pattern**: Concurrency/lock ordering
**Severity**: Medium

**Evidence**:

Several methods acquire `planLock` (via `getPlan()`) and then `servicesLock`:

- `Services()` (line 120-122): `getPlan()` then `servicesLock.Lock()`
- `Replan()` (line 262-264): `getPlan()` then `servicesLock.Lock()`
- `servicesToStop()` (line 419-434): `getPlan()` then `servicesLock.Lock()`

The `doStart` handler (line 115 in handlers.go) acquires locks in a different pattern:
- Lines 117-120: `state.Lock()` then `state.Unlock()`
- Line 132: `getPlan()` (acquires `planLock`)
- Line 180: `servicesLock.Lock()` (inside `serviceForStart`, but only if tomb is dying)

And `PlanChanged()` (line 67-71) acquires only `planLock`.

While the current code appears to consistently acquire `planLock` before `servicesLock` (never the reverse), the pattern is subtle because `getPlan()` acquires and immediately releases `planLock` (it uses `defer`), so the two locks are never held simultaneously in the main paths. However, `servicesToStop()` at line 419 calls `getPlan()` which locks/unlocks `planLock`, then at line 433 locks `servicesLock`. Between those two operations, another goroutine could call `PlanChanged()` and change the plan, meaning `servicesToStop()` operates on a stale plan pointer while holding `servicesLock`.

This is the same class of bug documented in the patterns doc (entries 73-79). The current code mitigates it by treating the plan as immutable once returned from `getPlan()`, but the window between `getPlan()` releasing `planLock` and `servicesLock` being acquired means the plan could change. This is a TOCTOU (time-of-check-to-time-of-use) issue.

**Why this is a real concern**: The pattern doc explicitly calls out multi-lock ordering between `servicesLock`, `state lock`, and `planLock` as the most common high-severity deadlock pattern in Pebble (entries 73-79). While the current code avoids deadlock by never holding both locks simultaneously, it introduces a race window instead.

**Suggested fix**: This is a design-level concern. The current approach (immutable plan snapshots) is a reasonable mitigation. Document the invariant that `getPlan()` returns an immutable snapshot and must never be mutated.

---

## Finding 5: `Replan()` Marks Services as Needing Restart Even When Not in Plan

**File**: `/home/ubuntu/charm-tech-analysis/pebble/internals/overlord/servstate/manager.go`, lines 269-288
**Pattern**: Logic error
**Severity**: Medium

**Evidence**:
```go
func (m *ServiceManager) Replan() ([][]string, [][]string, error) {
    currentPlan := m.getPlan()
    // ...
    for name, s := range m.services {
        if config, ok := currentPlan.Services[name]; ok {
            // ... check if config changed, continue if not ...
            s.config = config.Copy()
            // ...
        }
        // BUG: falls through here even when service is NOT in the plan
        needsRestart[name] = true
        stop = append(stop, name)
    }
```

**Why this is a real bug**: When a service exists in `m.services` (it was previously started) but is NOT in the current plan (`currentPlan.Services[name]` returns `!ok`), the code falls through the `if` block and unconditionally marks the service as needing restart (`needsRestart[name] = true`) and adds it to the `stop` list. This means:

1. A service removed from the plan will be added to both the stop AND start lists.
2. The `startLanes` computation (line 307) calls `currentPlan.StartOrder(start)`, which will fail or behave unexpectedly for service names not in the plan.

The intent appears to be that services removed from the plan should be stopped but not restarted. The fix would be to only set `needsRestart` when the service IS in the plan but has changed config.

**Suggested fix**:
```go
for name, s := range m.services {
    if config, ok := currentPlan.Services[name]; ok {
        // ... check if config changed ...
        s.config = config.Copy()
        if workload != nil {
            s.workload = workload
        }
        needsRestart[name] = true
        stop = append(stop, name)
    } else {
        // Service removed from plan, stop but don't restart
        stop = append(stop, name)
    }
}
```

Wait -- on closer inspection, `currentPlan.StopOrder(stop)` and `currentPlan.StartOrder(start)` are called with these names. If a service name is not in the plan, `StopOrder` may still work (it only needs dependency info for ordering), but `StartOrder` would fail. However, the `start` list is built separately (lines 290-295) and only includes names from `currentPlan.Services`, so the removed service would only appear in `start` if `needsRestart[name]` is true AND the name is in `currentPlan.Services`. Since the removed service is not in `currentPlan.Services`, it won't be in `start`.

But `needsRestart[name] = true` is still set for services not in the plan, which is misleading. And the service that was removed from the plan IS added to `stop`, which gets passed to `StopOrder` -- this could fail if `StopOrder` requires the service to be in the plan.

**Revised severity**: Medium -- the stop path likely works (stopping a removed service is correct), but the code is fragile and the `needsRestart` map contains incorrect entries.

---

## Summary

| # | Finding | File | Severity | Pattern |
|---|---------|------|----------|---------|
| 1 | File descriptor + temp file leak in `NewAtomicFile` on `Chmod` failure | `internals/osutil/io.go:105-110` | Medium | Resource leak |
| 2 | String-based error matching for user lookup (documented workaround) | `internals/osutil/user.go:67,104,120,138` | Low | String-based error matching |
| 3 | Dead code with buggy-if-reached slice modification in `Replan` | `internals/overlord/servstate/manager.go:301-305` | Low | Logic error (dead code) |
| 4 | TOCTOU race between `getPlan()` and `servicesLock` acquisition | `internals/overlord/servstate/manager.go` (multiple methods) | Medium | Concurrency/lock ordering |
| 5 | Services removed from plan marked as `needsRestart` in `Replan` | `internals/overlord/servstate/manager.go:269-288` | Medium | Logic error |

### Patterns Checked With No Findings

- **Nil map panics in CombineLayers**: The `Merge` methods on `Service`, `Check`, and `LogTarget` all have proper nil map checks before assignment (e.g., lines 302-304 in plan.go). `CombineLayers` initializes all maps in the combined layer.
- **sync.Cond usage**: Both `noticeCond.Broadcast()` calls are made with the state lock held (line 282 in notices.go is inside `AddNotice` which calls `s.writing()` requiring the lock; line 457 explicitly acquires `noticeCond.L.Lock()`). The `executionsCond.Broadcast()` in cmdstate also acquires the lock first (line 65-67).
- **tomb.Tomb lifecycle**: The reaper's tomb has `reaperTomb.Go(reapChildren)` called in `Start()`. The `pullerGroup` starts a sentinel goroutine. The `logGatherer` starts `g.tomb.Go(g.loop)`. The taskrunner creates tombs and immediately calls `tomb.Go()`. No "orphan tomb" patterns found.
- **Named return shadowing**: The `idkey.go:save()` and `tlsstate/manager.go:saveIDCert()` both use named `err` returns with deferred `errors.Join(err, file.Close())` -- these are intentional and correct patterns for ensuring file close errors are captured.
- **JSON nil vs empty**: The checks endpoint explicitly uses `[]checkInfo{}` to avoid nil. The services endpoint uses `make([]serviceInfo, 0, len(services))` which also produces `[]` not `null`.
- **Struct initialization without constructor**: No cases found of `&ServiceManager{}` or similar zero-value usage where `NewManager()` exists.
