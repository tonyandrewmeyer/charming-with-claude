---
name: charm-go-find-bugs
description: Find bugs in Canonical Charm Tech Go repositories (pebble, concierge, and other Go charm ecosystem code). Use when asked to "find bugs", "audit code", "review for bugs", "check for issues", or review Go code in Juju charm infrastructure projects. Specialized for charm ecosystem Go patterns including concurrency/deadlocks, nil map panics, error handling, resource leaks, idempotency, snap API interaction, and Pebble service management. Built from analysis of 143 historical bug fixes across 2 Go repos.
---

# Charm Go Bug Finder

Find bugs in Canonical Charm Tech Go codebases using domain-specific knowledge from 143+ historical bug fixes across pebble and concierge.

## Scope

Report on: only the files or diff the user specifies.
Research: the entire codebase to build confidence before reporting.

Do not report issues based solely on pattern matching. Investigate data flow and confirm the bug is real before reporting.

## Step 1: Determine review scope

Identify what code areas are being reviewed and load the relevant reference sections:

| Code Area | Indicators | Reference Section |
|-----------|-----------|-------------------|
| Service management | `ServiceManager`, `servicesLock`, `doStart`, `doStop`, service lifecycle | `references/bug-patterns.md` — Concurrency, Service Management |
| HTTP API | handlers, `ServeHTTP`, request/response, API endpoints | `references/bug-patterns.md` — API Contracts, JSON Marshaling |
| Plan/layer config | `Plan`, `Layer`, `CombineLayers`, `Merge`, service config | `references/bug-patterns.md` — Nil Maps, Plan Management |
| Exec / processes | `exec.Command`, `tomb.Tomb`, process lifecycle, FD management | `references/bug-patterns.md` — Resource Leaks, Tomb Lifecycle |
| Checks / notices | `CheckManager`, `NoticeManager`, `sync.Cond`, state changes | `references/bug-patterns.md` — Concurrency, State Management |
| Provider/provisioning | providers, LXD, K8s, MicroK8s, bootstrap, init | `references/bug-patterns.md` — Idempotency, Copy-Paste |
| Snap interaction | `snapd`, snap install/refresh, snap API | `references/bug-patterns.md` — Snap API, Retry Logic |
| Juju interaction | `juju`, bootstrap, credentials, controllers | `references/bug-patterns.md` — Error Handling, Juju CLI |
| Error handling | `fmt.Errorf`, `errors.Is`, `strings.Contains(err.Error()` | `references/bug-patterns.md` — Error Patterns |
| File operations | `os.Open`, `os.Create`, `os.Chown`, temp files, atomicity | `references/bug-patterns.md` — Resource Leaks, Security |
| Broad review / full audit | Multiple areas or unspecified | Read full `references/bug-patterns.md` |

Always read `references/anti-patterns.md` for concrete code patterns to search for.

## Step 2: Search for known bug patterns

For each relevant code area, search the codebase for the anti-patterns listed in `references/anti-patterns.md`. Use Grep with the provided search patterns.

For each match:
1. Read surrounding context (at least 30 lines around the match).
2. Trace data flow — especially lock acquisition order and error propagation.
3. Check if there is an existing fix, test, or guard.
4. Only report if the bug is confirmed after investigation.

## Step 3: Hunt for novel bugs

After searching for known patterns:

1. **Read each file in scope end-to-end** — concurrency bugs hide between patterns.
2. **Trace lock acquisition order**: for each mutex in the codebase, list every function that acquires it and what other locks are held at that point. Look for inconsistent ordering.
3. **Trace error propagation**: pick 3-5 error returns and follow them up the call stack. Check for lost errors, wrong wrapping, and incorrect retry behavior.
4. **Check constructor usage**: for each exported type with a `New*` constructor, search for `&Type{}` zero-value construction that bypasses it.
5. **Compare parallel implementations**: for provider code (K8s, LXD, MicroK8s), diff analogous methods side by side. Copy-paste errors are common.
6. **Check recent commits** (`git log --oneline -20 -- <file>`).

## Step 4: Check cross-cutting concerns

Always check these regardless of code area:

1. **Lock ordering**: Are multiple locks acquired in a consistent order across all goroutines?
2. **Nil map guards**: Are map struct fields initialized before assignment?
3. **Error wrapping**: Is `%w` used (not `%s` or `%v`) when wrapping errors for later `errors.Is`/`errors.As`?
4. **Deferred cleanup**: Do deferred `Close()`/`Stop()` calls check errors? Do they shadow named returns?
5. **Idempotency**: Do provisioning/bootstrap operations check existing state before acting?
6. **Retry discrimination**: Does retry logic distinguish permanent from transient errors?
7. **os.Chown vs os.Lchown**: Are file ownership operations safe against symlink traversal?

## Step 5: Verify each finding

For each potential bug:
- Confirm the goroutine/caller context where this code runs.
- Check if another code path already handles the case.
- Search for existing tests.
- Check git blame for recent changes.
- For concurrency bugs, confirm the lock is actually shared across goroutines.

## Step 6: Report findings

### Severity classification

| Severity | Criteria | Examples |
|----------|----------|----------|
| **Critical** | Security issue or data corruption | Symlink traversal via os.Chown, credential exposure |
| **High** | Deadlock, panic, or silent wrong behavior | Multi-lock deadlock, nil map panic, lost error causing wrong decision |
| **Medium** | Resource leak, fragile pattern, or edge case | FD leak on error path, string-based error matching, non-idempotent operation |
| **Low** | Code quality or unlikely edge case | Dead code, duplicate entries, cosmetic issues |

### Output format

```markdown
## Bug Review: [Scope Description]

### Summary
- **Findings**: X (Y High, Z Medium, ...)
- **Code areas reviewed**: [list]

### Findings

#### [BUG-001] [Category] — [Brief description] (Severity)
- **Location**: `file.go:123`
- **Pattern**: [Which known pattern this matches, or "novel"]
- **Issue**: [What the bug is]
- **Impact**: [What goes wrong at runtime]
- **Evidence**:
  ```go
  [Buggy code snippet]
  ```
- **Recommended fix**:
  ```go
  [Fixed code snippet]
  ```
- **Historical precedent**: [Commit that fixed a similar bug, if applicable]

### Confirmed Safe
[Patterns that looked suspicious but were verified as correct]
```

### False-positive controls

Do NOT flag:
- Locks that are acquired and released within the same function with no other lock held
- `sync.Cond.Broadcast()` called while the associated lock is held
- `&Type{}` for types that are designed to work with zero values (e.g., `sync.Mutex`, `sync.WaitGroup`)
- `strings.Contains(err.Error()...)` with explicit code comments referencing the upstream issue being worked around
- Named returns used with `errors.Join(err, file.Close())` — this is the correct pattern for capturing close errors
- `json.Marshal` on initialized empty slices (`make([]T, 0)` or `[]T{}`) — these produce `[]` not `null`
- Deferred unlocks in short functions with no other lock acquisition
- Retry logic that has an explicit timeout/max-duration boundary

### Known false-positive patterns

| Pattern | Why it's safe |
|---------|--------------|
| `defer m.servicesLock.Unlock()` in single-lock functions | No other lock acquired in scope |
| `noticeCond.Broadcast()` in `AddNotice` | Called inside `s.writing()` which holds the state lock |
| `errors.Join(err, file.Close())` with named return | Intentional pattern to capture both errors |
| `make([]serviceInfo, 0, len(services))` | Initialized empty slice, marshals as `[]` |
| `tomb.Go(func)` immediately after tomb creation | Goroutine started, `Wait()` won't block |
| User lookup string matching with documented Go issue reference | Acknowledged workaround for Go #67912 |
