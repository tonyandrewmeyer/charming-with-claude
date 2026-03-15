# Concierge Bug-Fix Classification Summary

**Project**: canonical/concierge (Go-based charm development machine provisioning tool)
**Total fixes analyzed**: 35
**Date range**: 2024-10-11 to 2026-03-10

## Fixes by Severity

| Severity | Count | Percentage |
|----------|-------|------------|
| High     | 8     | 22.9%      |
| Medium   | 17    | 48.6%      |
| Low      | 10    | 28.6%      |

## Top Bug Areas

| Bug Area      | Count | Percentage |
|---------------|-------|------------|
| provisioning  | 13    | 37.1%      |
| cli           | 7     | 20.0%      |
| snap          | 6     | 17.1%      |
| lxd           | 3     | 8.6%       |
| config        | 3     | 8.6%       |
| testing       | 1     | 2.9%       |
| ci-build      | 1     | 2.9%       |
| multipass      | 1     | 2.9%       |

## Top Bug Types

| Bug Type          | Count | Percentage |
|-------------------|-------|------------|
| error-handling    | 8     | 22.9%      |
| logic-error       | 8     | 22.9%      |
| edge-case         | 6     | 17.1%      |
| state-management  | 4     | 11.4%      |
| config-parsing    | 3     | 8.6%       |
| other             | 3     | 8.6%       |
| test-fix          | 1     | 2.9%       |
| resource-leak     | 1     | 2.9%       |
| data-validation   | 1     | 2.9%       |

## Fix Categories

| Category    | Count |
|-------------|-------|
| source-fix  | 33    |
| test-fix    | 1     |
| build-fix   | 1     |

## Notable Patterns

### 1. Retry/Resilience Dominance
The single most common fix pattern is adding retries with backoff to external API calls. At least 7 commits (20%) add retry logic to snapd client calls, juju controller checks, or provider wait-ready commands. The project depends heavily on external services (snapd, LXD, k8s, juju) that are inherently unreliable, and the initial implementation was too optimistic about single-shot success.

### 2. Idempotency Gaps
Four fixes (11.4%) address state-management issues where running `concierge prepare` a second time would break the system. Key examples: re-bootstrapping k8s when already bootstrapped, removing containerd when k8s is running, and unconditionally stopping LXD. This suggests the tool was initially designed for single-use provisioning and idempotency was retrofitted.

### 3. String-Based Error Matching Fragility
Multiple fixes tighten string-contains checks on error messages (e.g., matching "not found" too loosely, matching "snap not found" to short-circuit retries). This is a recurring Go pattern where error inspection relies on substring matching rather than typed errors, leading to false positives when different error messages share common phrases.

### 4. Provider Initialization Is the Hardest Part
37% of all fixes are in the provisioning area. The k8s, LXD, and MicroK8s providers collectively account for the majority of bugs, particularly around install sequencing, readiness checks, and handling pre-existing state.

### 5. Snap API Is a Frequent Pain Point
Six fixes (17%) deal with snapd client interactions -- rate limiting, incorrect snap name lookups, channel/confinement mismatches, and retry logic. The snapd REST API appears to be a significant source of flakiness.

## Go-Specific Patterns

### Error Wrapping and Inspection
Several fixes involve improving `strings.Contains(err.Error(), ...)` checks. Go's error handling encourages string-based error inspection when dealing with external command output, which is inherently fragile. The codebase would benefit from defining sentinel errors or using `errors.Is`/`errors.As` where possible.

### Goroutine Coordination with errgroup
Commit #8 introduces `golang.org/x/sync/errgroup` for concurrent package installation. This is a standard Go pattern for fan-out work with error propagation.

### Context-Based Retry with go-retry
The project adopted `github.com/sethvargo/go-retry` for retry logic, using Go's `context.Context` for cancellation. Multiple fixes layer this library over snapd and juju API calls.

### os.Chown vs os.Lchown
Commit #1 fixes a subtle Go standard library distinction: `os.Chown` follows symlinks while `os.Lchown` does not. The fix prevents privilege escalation through symlink traversal during recursive ownership changes.

### Path Resolution Edge Cases
Two fixes (#31, #32) address command path resolution, where `exec.LookPath` and `os.Getenv("SHELL")` may not behave as expected in constrained environments (e.g., snap confinement, minimal containers). The fallback chain pattern (SHELL -> bash -> sh) is a defensive Go idiom.

### Empty Struct Initialization Bug
Commit #34 fixes `&concierge.Manager{}` (zero-value struct) being used instead of the proper constructor `concierge.NewManager(conf)`. This is a common Go mistake since the compiler does not enforce constructor usage -- zero-value structs are valid but may lack required initialization.
