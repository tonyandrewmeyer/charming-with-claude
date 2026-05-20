# Pebble Bug-Fix Classification Summary

Analysis of 108 bug-fix commits from the Pebble project (Go-based lightweight Linux service manager).

## Fixes by Severity

| Severity | Count | Percentage |
|----------|-------|------------|
| High     | 27    | 25.0%      |
| Medium   | 42    | 38.9%      |
| Low      | 39    | 36.1%      |

## Top Bug Areas

| Bug Area            | Count | Percentage |
|---------------------|-------|------------|
| service-management  | 17    | 15.7%      |
| http-api            | 15    | 13.9%      |
| ci-build            | 11    | 10.2%      |
| exec                | 10    | 9.3%       |
| notices             | 9     | 8.3%       |
| testing             | 8     | 7.4%       |
| cli                 | 8     | 7.4%       |
| checks              | 7     | 6.5%       |
| docs                | 6     | 5.6%       |
| plan-management     | 5     | 4.6%       |
| logging             | 4     | 3.7%       |
| other               | 4     | 3.7%       |
| layer-config        | 3     | 2.8%       |
| file-operations     | 1     | 0.9%       |

## Top Bug Types

| Bug Type         | Count | Percentage |
|------------------|-------|------------|
| logic-error      | 21    | 19.4%      |
| other            | 17    | 15.7%      |
| concurrency      | 13    | 12.0%      |
| error-handling   | 12    | 11.1%      |
| security         | 8     | 7.4%       |
| nil-pointer      | 7     | 6.5%       |
| race-condition   | 6     | 5.6%       |
| state-management | 5     | 4.6%       |
| edge-case        | 5     | 4.6%       |
| api-contract     | 4     | 3.7%       |
| performance      | 4     | 3.7%       |
| data-validation  | 3     | 2.8%       |
| resource-leak    | 2     | 1.9%       |
| type-error       | 1     | 0.9%       |

## Fix Categories

| Category   | Count | Percentage |
|------------|-------|------------|
| source-fix | 83    | 76.9%      |
| ci-fix     | 9     | 8.3%       |
| test-fix   | 8     | 7.4%       |
| docs-fix   | 6     | 5.6%       |
| build-fix  | 2     | 1.9%       |

## Notable Patterns

### Concurrency is the dominant high-severity category

Concurrency bugs (deadlocks, race conditions) account for 19 of 108 fixes (17.6%) and are disproportionately high-severity. Pebble's architecture involves multiple goroutines managing services, checks, exec tasks, and state, each with their own locks. The most common pattern is **multi-lock deadlock**: goroutines acquiring state lock + servicesLock or planLock in different orders. Several fixes (entries 73-79) addressed a 3-lock deadlock between servicesLock, state lock, and planLock by reducing lock scope and decoupling locking from external callbacks.

### Nil pointer panics from uninitialized Go maps and missing state

Seven nil-pointer fixes were found. A recurring Go-specific pattern is **nil map assignment panic**: in Go, assigning to a nil map panics, and Pebble hit this in CombineLayers when merging service environment maps (entry 100). Another pattern is **nil state after restart**: carryover changes from previous daemon runs reference state keys that no longer exist, causing panics on type assertion (entries 16-17, 49).

### Security fixes came in clusters

Eight security fixes are present, with two distinct clusters: (1) CVE-2024-24790 Go runtime fix requiring a Go version bump (entries 40, 42), and (2) access control fixes where POST endpoints and the file pull API were accidentally left as user-accessible instead of admin-only after a code port from snapd (entries 50-54). These access control issues affected multiple branches and required multiple backports.

### Test flakiness from timing and shared state

Eight test-fix commits address flaky tests, almost all caused by timing sensitivity or shared mutable state. Common patterns include tests that relied on operations completing within tight timeouts (50ms okayWait in entry 0, slow disk os.Remove in entry 1) and tests that shared a ServiceManager instance (entry 94). The fix patterns are consistent: increase timeouts, use assertions instead of checks to fail fast, and isolate test state.

### Backport commits inflate the count

Approximately 15-20 entries are backports of the same fix to different branches (e.g., entries 16/17, 19/20, 50-54, 61/62, 67/72, 73/76/78, 74/77/79, 69/71, 68/70). This is typical for a project maintaining multiple release branches.

### CI/build fixes are non-trivial

The 11 CI/build fixes include substantive issues like snap build architecture (remote builds), credential path changes, workflow run conditions, and Go version bumps for CVEs. These are not mere cosmetic changes.

## Go-Specific Patterns

1. **Lock ordering deadlocks**: Go's sync.Mutex has no built-in deadlock detection. Multiple fixes addressed goroutines acquiring locks in inconsistent order (servicesLock before state lock in one goroutine, opposite in another). The fix pattern was always to reduce lock scope rather than enforce ordering.

2. **sync.Cond broadcast timing**: Entry 12 fixed a race where sync.Cond.Broadcast() was called outside the Cond's lock, meaning the signal could be missed by goroutines not yet in Wait(). This is a subtle Go-specific pitfall.

3. **tomb.Tomb lifecycle**: Entry 3 fixed a hang caused by creating a tomb.Tomb without starting a goroutine on it -- calling Wait() on such a tomb blocks forever. The fix was lazy initialization.

4. **Named return value shadowing**: Entry 63 fixed a case where a named return `err` was overwritten by a deferred reaper.Stop(), losing the original error. The fix was switching from named return to local variable.

5. **Go nil slice vs empty slice JSON marshaling**: Entry 4 fixed the Go-specific behavior where `json.Marshal(nil)` produces `null` but `json.Marshal([]string{})` produces `[]`. API consumers expected `[]`.

6. **Cmd.WaitDelay for subprocess cleanup**: Entry 90 used Go 1.20's Cmd.WaitDelay to prevent Command.Wait from blocking indefinitely when child processes inherit stdin/stdout/stderr file descriptors.

7. **net/http panic recovery causing deadlocks**: Entry 45 disabled Go's default http.Server panic recovery because recovering a panic while a lock is held leaves the lock permanently held, causing the entire daemon to deadlock.
