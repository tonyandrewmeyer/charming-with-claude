# Charm Go Anti-Patterns: Searchable Code Patterns

Concrete code patterns to grep for when auditing Charm Tech Go codebases. Each pattern includes the search command, what to check, and how to distinguish true bugs from false positives.

## Contents
- Concurrency: multiple lock acquisition
- Concurrency: sync.Cond broadcast
- Concurrency: tomb lifecycle
- Nil maps: struct field assignment
- Error handling: discarded errors
- Error handling: %s/%v wrapping
- Error handling: string-based matching
- Error handling: boolean error swallowing
- Resource leaks: file descriptors
- Resource leaks: deferred close errors
- Named returns: deferred overwrite
- Idempotency: unconditional operations
- Retry: all errors retryable
- Snap: status state confusion
- Snap: string-based error matching
- Copy-paste: wrong provider config
- JSON: nil vs empty slice
- Struct init: zero-value bypassing constructor
- Security: os.Chown vs os.Lchown
- State: map overwrite in loops
- Firewall: unconditional flush

---

## Concurrency: multiple lock acquisition

**Search**: `\.Lock()` in Go files, then check if another lock is acquired before the corresponding `Unlock()`
**What to check**: Are multiple locks held simultaneously? Is the acquisition order consistent across all call sites?
**True bug**: Function A acquires `servicesLock` then `planLock`; Function B acquires `planLock` then `servicesLock`.
**False positive**: Single lock acquired and released within a function with no other lock held.

**Method**: List all mutex fields in a struct. For each, find all `Lock()` call sites. Check if another lock is held at each site.

---

## Concurrency: sync.Cond broadcast

**Search**: `\.Broadcast()` or `\.Signal()` in Go files
**What to check**: Is the Cond's associated lock held when Broadcast/Signal is called?
**True bug**: `cond.Broadcast()` without `cond.L.Lock()`.
**False positive**: Called inside a function that already holds the lock (e.g., inside `s.writing()` which acquires the state lock).

---

## Concurrency: tomb lifecycle

**Search**: `tomb.Tomb` in Go files
**What to check**: Is a goroutine started on the tomb (via `tomb.Go()`) before `tomb.Wait()` is called?
**True bug**: Tomb created but no goroutine started — `Wait()` blocks forever.
**False positive**: `tomb.Go(func)` called immediately after creation.

---

## Nil maps: struct field assignment

**Search**: `\.\w+ *\[` on the left side of `=` for map fields in structs
**What to check**: Is the map initialized before first assignment?
**True bug**: `service.Environment[key] = value` when `Environment` could be nil.
**False positive**: Map initialized in constructor or preceding `if == nil` check.

**Quick grep**: Search for `= make(map` to find initialization points, then check corresponding assignment sites.

---

## Error handling: discarded errors

**Search**: `fmt.Errorf\(` where the format string doesn't contain `%w` and the surrounding code has an `err` variable
**What to check**: Is an error variable available but not included in the format string?
**True bug**: `return fmt.Errorf("failed for '%s'", name)` when `err` is in scope.
**False positive**: Constructing a new error with no prior error to wrap.

---

## Error handling: %s/%v wrapping

**Search**: `fmt.Errorf.*%[sv].*err` in Go files
**What to check**: Should `%s` or `%v` be `%w` for error wrapping?
**True bug**: `fmt.Errorf("failed: %s", err)` — breaks `errors.Is`/`errors.As` chain.
**False positive**: Intentionally formatting error as string (not wrapping).

---

## Error handling: string-based matching

**Search**: `strings.Contains(err.Error()` or `strings.Contains(string(output)` in Go files
**What to check**: Is there a more robust alternative (sentinel errors, `errors.Is`, structured output)?
**True bug**: `strings.Contains(err.Error(), "not found")` — breaks if message changes.
**False positive**: Matching CLI output where no structured alternative exists, with explicit upstream issue reference.

---

## Error handling: boolean error swallowing

**Search**: Functions returning `bool` that call error-returning functions internally
**What to check**: Are unexpected errors treated as a definitive `false`?
**True bug**: `needsBootstrap()` returns `false` on transient errors, silently skipping bootstrap.
**Fix**: Return `(bool, error)` to propagate unexpected errors.

---

## Resource leaks: file descriptors

**Search**: `os.OpenFile(` or `os.Open(` or `os.Create(` in Go files
**What to check**: Is the file closed on ALL error paths, not just the happy path?
**True bug**: `fd, _ := os.OpenFile(...)` followed by an error return before `fd.Close()`.
**False positive**: File wrapped in a struct whose `Close()` handles cleanup.

---

## Resource leaks: deferred close errors

**Search**: `defer.*\.Close()` in Go files
**What to check**: Is the error from Close() captured? Does it shadow a named return?
**True bug**: `defer f.Close()` ignoring the error when writing to the file.
**Correct pattern**: `defer func() { err = errors.Join(err, f.Close()) }()`

---

## Named returns: deferred overwrite

**Search**: Functions with `(err error)` named return that contain `defer` statements
**What to check**: Does a deferred function assign to `err`, potentially overwriting the original error?
**True bug**: `defer func() { err = reaper.Stop() }()` overwrites original error.
**False positive**: `defer func() { err = errors.Join(err, f.Close()) }()` — correct pattern.

---

## Idempotency: unconditional operations

**Search**: `init()`, `bootstrap()`, `install()`, `prepare()` functions in provisioning code
**What to check**: Does the operation check existing state before acting?
**True bug**: `lxd init --minimal` without checking if LXD is already initialized.
**False positive**: Operation followed by `if alreadyExists` guard.

---

## Retry: all errors retryable

**Search**: `retry.RetryableError(err)` or `RetryableError` in Go files
**What to check**: Are ALL errors marked as retryable, or only transient ones?
**True bug**: `return nil, retry.RetryableError(err)` for every error — permanent failures retried for minutes.
**Fix**: Check for permanent errors (ErrNotFound, permission denied) before wrapping.

---

## Snap: status state confusion

**Search**: `StatusActive` or `snap.Status` in Go files
**What to check**: Does the code handle all snap status states, or only `Active`?
**True bug**: Non-active but installed snaps treated as "not installed".

---

## Snap: string-based error matching

**Search**: `"snap not found"` or `"snap not installed"` in Go files
**What to check**: Same as "Error handling: string-based matching" above. Check if snapd client changes would break the match.

---

## Copy-paste: wrong provider config

**Search**: `config.Providers.` in provider initialization code
**What to check**: Does each provider reference its OWN config section?
**True bug**: MicroK8s reading `config.Providers.Google.ModelDefaults`.
**Method**: For each `New<Provider>()` constructor, verify all `config.Providers.X` references use the correct provider name.

---

## JSON: nil vs empty slice

**Search**: `json.Marshal` on variables that could be nil slices
**What to check**: Will nil slices produce `null` where API consumers expect `[]`?
**True bug**: `var items []string; json.Marshal(items)` → `null`.
**False positive**: `items := make([]T, 0); json.Marshal(items)` → `[]`.

---

## Struct init: zero-value bypassing constructor

**Search**: `&\w+\{\}` for types that have `New\w+` constructors
**What to check**: Is the zero-value struct missing required initialization?
**True bug**: `&concierge.Manager{}` when `NewManager(conf)` exists and sets required fields.
**False positive**: `&sync.Mutex{}`, `&sync.WaitGroup{}` — designed for zero-value use.

---

## Security: os.Chown vs os.Lchown

**Search**: `os.Chown` in Go files
**What to check**: Could the path contain a symlink? `os.Chown` follows symlinks.
**True bug**: `os.Chown(path, uid, gid)` on user-controllable paths — symlink traversal.
**Fix**: Use `os.Lchown(path, uid, gid)`.

---

## State: map overwrite in loops

**Search**: `= map[string]` inside `for` loops
**What to check**: Is a map value being replaced on each iteration instead of merged?
**True bug**: `credentials["key"] = map[string]any{...}` inside a loop — previous entries lost.
**Fix**: Access existing map and add to it.

---

## Firewall: unconditional flush

**Search**: `iptables` with `-F` flag
**What to check**: Does the flush target only the rules that need removing, or does it flush everything?
**True bug**: `iptables -F FORWARD` without checking what rules exist — destroys other providers' rules.
