# Charm Go Bug Patterns

Recurring bug patterns from 143 historical fixes across 2 Go repositories in the Canonical Charm Tech ecosystem: pebble (service manager) and concierge (provisioning tool).

## Contents
- Concurrency and Deadlocks
- Nil Map and Pointer Panics
- Error Handling Patterns
- Resource Leaks
- Idempotency Failures
- Retry Logic
- Snap API Interaction
- Copy-Paste Errors
- Named Return Shadowing
- JSON Marshaling
- Tomb Lifecycle
- Struct Initialization
- Security
- State Management

---

## Concurrency and Deadlocks

**Priority: CRITICAL — 19 instances, 76% high severity. Dominant high-severity Go pattern.**

Pebble's multi-goroutine architecture with independent locks (`servicesLock`, `state lock`, `planLock`) is the primary source of deadlocks.

### Multi-lock deadlock

Goroutines acquiring locks in different orders. The most common high-severity pattern.

```go
// BUG: Function A acquires servicesLock then planLock
// Function B acquires planLock then servicesLock
// → Deadlock when A and B run concurrently

// FIX: Always acquire locks in a consistent global order,
// or restructure to never hold multiple locks simultaneously.
```

Pebble mitigates this by having `getPlan()` acquire and immediately release `planLock` (returning an immutable snapshot), then acquiring `servicesLock` separately. But this creates a TOCTOU window.

Precedents: Pebble entries 73-79

### net/http panic recovery while lock is held

```go
// BUG: HTTP handler holds servicesLock, net/http recovers a panic,
// but the lock is never released → entire daemon deadlocked

// FIX: Disable default panic recovery, or ensure deferred Unlock
// runs before panic propagation
```

Precedent: Pebble entry 45

### sync.Cond broadcast timing

```go
// BUG: Broadcast() called outside the Cond's lock
cond.Broadcast()  // Signal missed by goroutines not yet in Wait()

// FIX: Hold the lock when broadcasting
cond.L.Lock()
cond.Broadcast()
cond.L.Unlock()
```

Precedent: Pebble entry 12

### TOCTOU between lock releases

Current finding: `getPlan()` releases `planLock`, then `servicesLock` is acquired. Between these operations, another goroutine can change the plan via `PlanChanged()`, meaning the code operates on a stale plan.

---

## Nil Map and Pointer Panics

**Priority: HIGH — 7 instances**

Go maps must be initialized before assignment. Nil struct field maps panic on write.

### Nil map in struct field

```go
// BUG: panics if Environment is nil
service.Environment[key] = value

// FIX: initialize before assignment
if service.Environment == nil {
    service.Environment = make(map[string]string)
}
service.Environment[key] = value
```

Precedent: Pebble entry 100 — `CombineLayers` nil map panic on service environment merge.

### Carryover state panics

State keys from previous daemon runs reference objects that no longer exist. Type assertions on these values panic.

Precedents: Pebble entries 16-17, 49

---

## Error Handling Patterns

**Priority: HIGH — 20+ instances across both repos**

### Discarded errors

```go
// BUG: original error lost entirely
if err != nil {
    return fmt.Errorf("error checking status for '%s'", name)
}

// FIX: include the error
if err != nil {
    return fmt.Errorf("error checking status for '%s': %w", name, err)
}
```

Current bug: `checkBootstrapped` and `killProvider` in concierge juju.go discard `err`.

### %s/%v instead of %w for error wrapping

```go
// BUG: error chain broken, errors.Is/As won't work
return fmt.Errorf("failed: %s", err)

// FIX: use %w for wrapping
return fmt.Errorf("failed: %w", err)
```

### String-based error matching

```go
// BUG: fragile, breaks if message format changes
if strings.Contains(err.Error(), "not found") {
    return nil
}

// FIX: define sentinel errors, use errors.Is
if errors.Is(err, ErrNotFound) {
    return nil
}
```

Current bugs: concierge snap.go uses `strings.Contains(err.Error(), "snap not found")` at 3 call sites.
Pebble user.go uses string matching as documented Go workaround (#67912).

Precedents: `63c74a37`, `20188c54` (concierge)

### Error swallowed in boolean return

```go
// BUG: transient error treated as "already bootstrapped"
func needsBootstrap() bool {
    _, err := run("k8s", "status")
    if err != nil {
        if errors.Is(err, ErrNotInstalled) {
            return true
        }
        // Falls through to return false for ANY other error
    }
    return false
}

// FIX: return (bool, error) and propagate unexpected errors
```

Current bug: `K8s.needsBootstrap` in concierge k8s.go

---

## Resource Leaks

**Priority: MEDIUM — confirmed current bugs**

### File descriptor leak on error path

```go
// BUG: fd leaked if Chmod fails
fd, err := os.OpenFile(tmp, flags, perm)
if err != nil { return nil, err }

if err := fd.Chmod(perm); err != nil {
    return nil, err  // fd not closed, tmp not removed
}

// FIX: clean up on error
if err := fd.Chmod(perm); err != nil {
    fd.Close()
    os.Remove(tmp)
    return nil, err
}
```

Known issue (not fixed — narrow edge case, only triggers on filesystems that don't support chmod): `NewAtomicFile` in pebble osutil/io.go

### Child process FD inheritance

Child processes inheriting stdin/stdout/stderr FDs prevent `Command.Wait` from returning.

**Fix**: Use Go 1.20's `Cmd.WaitDelay`.
Precedent: Pebble entry 90

---

## Idempotency Failures

**Priority: MEDIUM — 10 instances, primarily in concierge**

Operations that fail on re-run because they assume fresh state.

### Bootstrap/init not checking existing state

```go
// BUG: fails if already initialized
func (l *LXD) init() error {
    return system.RunMany(l.system,
        system.NewCommand("lxd", []string{"init", "--minimal"}),
    )
}

// FIX: check before acting
func (l *LXD) init() error {
    if l.isInitialized() {
        return nil
    }
    return system.RunMany(l.system,
        system.NewCommand("lxd", []string{"init", "--minimal"}),
    )
}
```

~~Current bug: `LXD.init()` in concierge lxd.go~~ — false positive. Tested directly: `lxd init --minimal` is idempotent and succeeds on re-run.

Precedent: `baf4fffe` (concierge — k8s bootstrap was not idempotent)

### Destructive cleanup of running services

Removing `/run/containerd` when k8s is already bootstrapped breaks running services.
Precedent: `0ddf24c3` (concierge)

### Service stop without restart

Stopping a service for refresh but never restarting it.
Precedent: `158c3a70` (concierge — LXD stopped for refresh, never restarted)

---

## Retry Logic

**Priority: MEDIUM — confirmed current bugs**

### Retrying permanent failures

```go
// BUG: ALL errors retried for full maxDuration
return retry.DoValue(ctx, backoff, func(ctx context.Context) ([]byte, error) {
    output, err := w.Run(c)
    if err != nil {
        return nil, retry.RetryableError(err)  // Always retryable!
    }
    return output, nil
})

// FIX: classify errors before retrying
if errors.Is(err, ErrNotFound) || errors.Is(err, ErrPermissionDenied) {
    return nil, err  // Permanent — don't retry
}
return nil, retry.RetryableError(err)  // Transient — retry
```

Fixed in [PR #164](https://github.com/canonical/concierge/pull/164) — `ErrNotInstalled` is now returned immediately without retrying.

Precedents: `b418443e` (no pre-check before retry loop), `20188c54` (short-circuit on definitive "not found")

---

## Snap API Interaction

**Priority: MEDIUM — 19 instances across concierge + operator-libs-linux**

### Rate limiting

snapd returns "too many requests". Snap operations need retry with backoff.

### Status state confusion

```go
// BUG: only checks Active, treats other installed states as "not installed"
if snap.Status == snapd.StatusActive {
    return true, channel
}
return false, ""  // Installed but inactive → reports as NOT installed

// FIX: check for any installed state
if snap.Status != "" {
    return true, channel
}
```

Fixed in [PR #165](https://github.com/canonical/concierge/pull/165) — now checks for `StatusInstalled` in addition to `StatusActive`, and enables disabled snaps before refreshing.

### Revision type

Snap revisions should be `string`, not `int`. Required v2 library bump in operator-libs-linux.

---

## Copy-Paste Errors

**Priority: HIGH — confirmed current bug**

Provider code with multiple similar structs is prone to copy-paste errors where one provider references another's config.

```go
// BUG: MicroK8s reads Google's config
return &MicroK8s{
    modelDefaults:        config.Providers.Google.ModelDefaults,       // WRONG
    bootstrapConstraints: config.Providers.Google.BootstrapConstraints, // WRONG
}

// FIX: use correct provider
return &MicroK8s{
    modelDefaults:        config.Providers.MicroK8s.ModelDefaults,
    bootstrapConstraints: config.Providers.MicroK8s.BootstrapConstraints,
}
```

Fixed in [PR #166](https://github.com/canonical/concierge/pull/166).

**Detection**: When reviewing provider code, compare field initialization across all providers. Each should reference its own `config.Providers.X` section.

---

## Named Return Shadowing

**Priority: MEDIUM — confirmed pattern**

Deferred calls that overwrite named return values, losing the original error.

```go
// BUG: deferred reaper.Stop() overwrites the named return `err`
func (m *Manager) start() (err error) {
    // ... original error stored in `err`
    defer func() {
        err = reaper.Stop()  // Overwrites original error!
    }()
}

// FIX: use local variable instead of named return
func (m *Manager) start() error {
    var startErr error
    // ...
    defer func() {
        stopErr := reaper.Stop()
        // Handle both errors appropriately
    }()
}
```

Precedent: Pebble entry 63

**Exception**: `errors.Join(err, file.Close())` with named returns is the CORRECT pattern for capturing both the original error and the close error.

---

## JSON Marshaling

**Priority: LOW — 1 instance, but subtle**

### Nil slice vs empty slice

```go
// BUG: json.Marshal(nil) → "null"
var items []string
json.Marshal(items)  // → "null"

// FIX: json.Marshal([]string{}) → "[]"
items := []string{}
json.Marshal(items)  // → "[]"
```

Precedent: Pebble entry 4 — API consumers expected `[]` not `null`.

---

## Tomb Lifecycle

**Priority: MEDIUM — confirmed pattern**

`tomb.Tomb` without a goroutine started on it causes `Wait()` to block forever.

```go
// BUG: tomb created but no goroutine started
t := tomb.Tomb{}
// ... later ...
t.Wait()  // Blocks forever

// FIX: lazy initialization, or start a goroutine immediately
t.Go(workerFunc)
```

Precedent: Pebble entry 3 (`f7589e55`)

---

## Struct Initialization

**Priority: MEDIUM — 2 instances**

Go compilers do not enforce constructor usage. Zero-value structs may lack required initialization.

```go
// BUG: bypasses constructor, nil pointer at runtime
mgr := &concierge.Manager{}

// FIX: use constructor
mgr := concierge.NewManager(conf)
```

Precedent: `34230b59` (concierge)

---

## Security

**Priority: HIGH — 8 instances in pebble**

### os.Chown vs os.Lchown

```go
// BUG: follows symlinks — privilege escalation via symlink attack
os.Chown(path, uid, gid)

// FIX: don't follow symlinks
os.Lchown(path, uid, gid)
```

Precedent: `39a18ffc` (concierge)

### File permissions

Files containing state or credentials must use restrictive permissions (0o600).

---

## State Management

**Priority: MEDIUM — 10 instances**

### Credentials map overwrite

```go
// BUG: each iteration replaces the entire inner map
for _, p := range providers {
    credentials["credentials"] = map[string]any{
        p.CloudName(): map[string]any{"concierge": p.Credentials()},
    }  // Previous providers' credentials lost!
}

// FIX: merge into existing map
credMap := credentials["credentials"].(map[string]any)
credMap[p.CloudName()] = map[string]any{"concierge": p.Credentials()}
```

Fixed in [PR #163](https://github.com/canonical/concierge/pull/163).

### Unconditional firewall flush

```go
// BUG: destroys ALL FORWARD rules, breaking other providers
func (l *LXD) deconflictFirewall() error {
    return system.RunMany(l.system,
        system.NewCommand("iptables", []string{"-F", "FORWARD"}),
    )
}
```

Current bug: concierge lxd.go — no check for existing rules before flushing.

### Dead code with latent bugs

Replan loop in pebble that can never execute, but contains a buggy slice-modification-during-iteration pattern that would break if the code became reachable.

Current finding: pebble servstate/manager.go lines 301-305
