# Concierge HEAD Audit: Bug Pattern Analysis

Audit of `canonical/concierge` at current HEAD against known patterns from the Charm Tech ecosystem (CROSS_REPO_PATTERNS.md sections 4 and 5).

---

## Finding 1: MicroK8s uses Google provider's ModelDefaults and BootstrapConstraints (copy-paste bug)

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/providers/microk8s.go`, lines 36-37
- **Pattern**: Logic error / copy-paste error (Pattern 1 from CROSS_REPO_PATTERNS.md)
- **Severity**: High

**Evidence**:
```go
return &MicroK8s{
    Channel:              channel,
    Addons:               config.Providers.MicroK8s.Addons,
    ImageRegistry:        config.Providers.MicroK8s.ImageRegistry,
    bootstrap:            config.Providers.MicroK8s.Bootstrap,
    modelDefaults:        config.Providers.Google.ModelDefaults,       // line 36 - WRONG
    bootstrapConstraints: config.Providers.Google.BootstrapConstraints, // line 37 - WRONG
    system:               r,
    ...
}
```

**Why it is a real bug**: The `NewMicroK8s` constructor reads `modelDefaults` and `bootstrapConstraints` from `config.Providers.Google` instead of `config.Providers.MicroK8s`. This means MicroK8s model defaults and bootstrap constraints configured by the user are silently ignored, and Google's config (likely empty/nil for a MicroK8s-only deployment) is used instead. Compare with `NewK8s` (lines 38-39 of k8s.go) and `NewLXD` (lines 25-26 of lxd.go), which both correctly reference their own provider config.

**Suggested fix**:
```go
modelDefaults:        config.Providers.MicroK8s.ModelDefaults,
bootstrapConstraints: config.Providers.MicroK8s.BootstrapConstraints,
```

---

## Finding 2: String-based error matching on snap API errors

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/system/snap.go`, lines 71, 104, 132-133
- **Pattern**: String-based error matching (Go pattern 4.3 from CROSS_REPO_PATTERNS.md)
- **Severity**: Medium

**Evidence**:
```go
// Line 71 (SnapChannels):
if strings.Contains(err.Error(), "snap not found") {
    return nil, err
}

// Line 104 (snapInstalledInfo):
if err != nil && strings.Contains(err.Error(), "snap not installed") {
    return snap, nil
}

// Line 132 (snapIsClassic):
if strings.Contains(err.Error(), "snap not found") {
    return nil, err
}
```

**Why it is a real bug**: These use fragile substring matching on error messages from the snapd client. The snapd client constructs these errors with `fmt.Errorf("snap not found: %s", name)` and `fmt.Errorf("snap not installed: %s", name)` (see `client.go` lines 103, 143, 165). If the error message format changes (e.g., locale-dependent snapd, or if the client wraps errors differently), these checks will silently stop matching and cause retries to loop indefinitely or return wrong results. This exact pattern was identified in commit `20188c54` as a prior concierge bug.

**Suggested fix**: Define sentinel errors in the `snapd` package (e.g., `var ErrSnapNotFound = errors.New("snap not found")`) and use `errors.Is()` for matching. The snapd client methods should wrap with these sentinels.

---

## Finding 3: `LXD.init()` is not idempotent -- `lxd init --minimal` fails on re-run

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/providers/lxd.go`, lines 135-141
- **Pattern**: Idempotency / state management (Pattern 7 from CROSS_REPO_PATTERNS.md)
- **Severity**: Medium

**Evidence**:
```go
func (l *LXD) init() error {
    return system.RunMany(l.system,
        system.NewCommand("lxd", []string{"waitready", "--timeout", "270"}),
        system.NewCommand("lxd", []string{"init", "--minimal"}),
        system.NewCommand("lxc", []string{"network", "set", "lxdbr0", "ipv6.address", "none"}),
    )
}
```

**Why it is a real bug**: `lxd init --minimal` will fail if LXD is already initialized (e.g., on a re-run of `concierge prepare`). The K8s provider has a `needsBootstrap()` guard (k8s.go line 183), but LXD has no equivalent check. This matches the exact pattern from commit `baf4fffe` where k8s bootstrap was not idempotent. The `RunMany` helper will abort on the first error, so the network configuration on line 139 would also be skipped.

**Suggested fix**: Check if LXD is already initialized before running `lxd init --minimal`. For example, check if the default storage pool exists or if `lxd init` has already been run, and skip if so.

---

## Finding 4: `juju writeCredentials` overwrites credentials for multiple providers

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/juju/juju.go`, lines 129-166
- **Pattern**: Logic error (Pattern 1)
- **Severity**: High

**Evidence**:
```go
func (j *JujuHandler) writeCredentials() error {
    credentials := map[string]any{"credentials": map[string]any{}}
    addedCredentials := false

    for _, p := range j.providers {
        if p.Credentials() == nil {
            continue
        }
        // This REPLACES the entire inner map on each iteration
        credentials["credentials"] = map[string]any{
            p.CloudName(): map[string]any{
                "concierge": p.Credentials(),
            },
        }
        addedCredentials = true
    }
    ...
}
```

**Why it is a real bug**: On each loop iteration, the code assigns a brand-new map to `credentials["credentials"]`, completely replacing the previous iteration's value. If two providers have credentials (e.g., Google and another future credentialed provider), only the last provider's credentials survive. The code should merge into the existing map rather than replace it.

**Suggested fix**:
```go
credMap := credentials["credentials"].(map[string]any)
credMap[p.CloudName()] = map[string]any{
    "concierge": p.Credentials(),
}
```

---

## Finding 5: `checkBootstrapped` error drops the underlying error with `%s` instead of `%w`

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/juju/juju.go`, line 194
- **Pattern**: Error handling gap (Pattern 3 / Go pattern 4.3)
- **Severity**: Medium

**Evidence**:
```go
bootstrapped, err := j.checkBootstrapped(controllerName)
if err != nil {
    return fmt.Errorf("error checking bootstrap status for provider '%s'", provider.Name())
}
```

**Why it is a real bug**: When `checkBootstrapped` returns an error, the wrapping `fmt.Errorf` discards it entirely -- it formats with `provider.Name()` but never includes `err`. The same pattern appears at line 270 in `killProvider`. This makes debugging impossible because the actual error (e.g., network failure, timeout) is lost. This matches the pattern from commit `e28f3b50` where command failures were silently swallowed.

**Suggested fix**:
```go
return fmt.Errorf("error checking bootstrap status for provider '%s': %w", provider.Name(), err)
```

---

## Finding 6: `CommandString` silently ignores LookPath errors

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/system/command.go`, lines 51-54
- **Pattern**: Error handling gap (Pattern 3)
- **Severity**: Low

**Evidence**:
```go
func (c *Command) CommandString() string {
    _, err := exec.LookPath(c.Executable)
    if err != nil {
        slog.Debug("Failed to lookup command in path", "command", c.Executable)
    }
    // proceeds to build command string anyway
    ...
}
```

**Why it is a real bug (limited)**: The function checks `LookPath` but then proceeds to build and return the command string regardless, only logging at debug level. This is mostly informational, but it means the real error only surfaces later when the shell fails to execute the command, producing a less clear error message. The impact is limited because the shell execution will still fail.

**Suggested fix**: Consider returning an error from `CommandString()` or documenting that this is intentionally best-effort. The current behavior is arguably by design for the dry-run case, so this is low severity.

---

## Finding 7: `RunWithRetries` retries ALL errors unconditionally

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/system/helpers.go`, lines 39-52
- **Pattern**: Snap API interaction / missing error discrimination (Pattern 5.7)
- **Severity**: Medium

**Evidence**:
```go
func RunWithRetries(w Worker, c *Command, maxDuration time.Duration) ([]byte, error) {
    backoff := retry.NewExponential(1 * time.Second)
    backoff = retry.WithMaxDuration(maxDuration, backoff)
    ctx := context.Background()

    return retry.DoValue(ctx, backoff, func(ctx context.Context) ([]byte, error) {
        output, err := w.Run(c)
        if err != nil {
            return nil, retry.RetryableError(err)
        }
        return output, nil
    })
}
```

**Why it is a real bug**: Every error is marked as retryable, meaning permanent failures (e.g., "snap not found in store", invalid arguments, permission denied) are retried for the full `maxDuration` (typically 5 minutes) before finally failing. This wastes significant time and was the exact pattern identified in commit `b418443e` (no pre-check for snap existence before entering retry loop) and `20188c54` (short-circuit retry on definitive "not found"). The `checkBootstrapped` method in juju.go correctly distinguishes retryable vs permanent errors, but `RunWithRetries` does not.

**Suggested fix**: Either accept a predicate function to classify errors, or at minimum check for `ErrNotInstalled` and permission errors as non-retryable.

---

## Finding 8: `realUser()` falls back to "root" when not running under sudo

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/system/util.go`, lines 55-62
- **Pattern**: Edge case at input boundary (Pattern 2)
- **Severity**: Low

**Evidence**:
```go
func realUser() (*user.User, error) {
    realUser := os.Getenv("SUDO_USER")
    if len(realUser) == 0 {
        return user.Lookup("root")
    }
    return user.Lookup(realUser)
}
```

**Why it is a real bug (limited)**: When `SUDO_USER` is not set (e.g., running directly as root in a container, or via `su`), the function hard-codes "root". This means all file ownership operations (`ChownAll`) will set root ownership, and home directory paths will use `/root`. In container environments where the user might actually be a non-root user running concierge without sudo, this could place files in the wrong directory. However, the `checkUser()` function in `cmd/main.go` (line 53) requires `uid == 0`, so this is mitigated for the normal CLI path.

**Suggested fix**: Consider using `user.Current()` as the fallback instead of hard-coding "root", or document this assumption.

---

## Finding 9: `snapInstalledInfo` returns `(false, "")` for installed but non-active snaps

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/system/snap.go`, lines 101-124
- **Pattern**: State management / snap API interaction (Patterns 5.7, 7)
- **Severity**: Medium

**Evidence**:
```go
func (s *System) snapInstalledInfo(name string) (bool, string) {
    snap, err := s.withRetry(func(ctx context.Context) (*snapd.Snap, error) {
        snap, err := s.snapd.Snap(name)
        if err != nil && strings.Contains(err.Error(), "snap not installed") {
            return snap, nil  // returns (nil, nil) when not installed
        } else if err != nil {
            return nil, retry.RetryableError(err)
        }
        return snap, nil
    })
    if err != nil || snap == nil {
        return false, ""
    }

    if snap.Status == snapd.StatusActive {
        ...
        return true, trackingChannel
    }

    return false, ""  // Installed but not active -> reports as NOT installed
}
```

**Why it is a real bug**: If a snap is installed but in a non-active state (e.g., "disabled", or temporarily stopped during a refresh), `snapInstalledInfo` reports it as not installed. This causes `installSnap` in `snap_handler.go` (line 63-68) to run `snap install` instead of `snap refresh`, which would fail because the snap is already installed. The snapd API returns statuses like `"installed"` (disabled) in addition to `"active"`. This matches the known pattern where snap task status states are more nuanced than code assumes (Pattern 5.7 mentions `Do` as a valid pending state).

**Suggested fix**: Treat any installed snap (regardless of status) as installed. Check for `snap.Status != ""` or compare against known "installed" states.

---

## Finding 10: `K8s.needsBootstrap` returns `false` on unexpected errors

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/providers/k8s.go`, lines 233-249
- **Pattern**: Error handling gap (Pattern 3)
- **Severity**: Medium

**Evidence**:
```go
func (k *K8s) needsBootstrap() bool {
    cmd := system.NewCommand("k8s", []string{"status"})
    cmd.ReadOnly = true
    output, err := k.system.Run(cmd)

    if err != nil {
        if errors.Is(err, system.ErrNotInstalled) {
            return true
        }
        if strings.Contains(string(output), "Error: The node is not part of a Kubernetes cluster.") {
            return true
        }
    }

    return false  // Returns false for ANY other error
}
```

**Why it is a real bug**: If `k8s status` fails for a transient reason (e.g., network timeout, socket not ready, permission error), the function returns `false` -- meaning "already bootstrapped, skip bootstrap". This silently skips the bootstrap step. The function should distinguish between "definitively bootstrapped" (successful status check) and "error checking status" (which should either retry or propagate). Compare with `checkBootstrapped` in juju.go which correctly retries on transient errors.

**Suggested fix**: Return `(bool, error)` and treat unexpected errors as errors rather than assuming the cluster is bootstrapped.

---

## Finding 11: `envOrFlagSlice` may produce duplicate entries

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/config/config.go`, lines 153-165
- **Pattern**: Edge case (Pattern 2)
- **Severity**: Low

**Evidence**:
```go
func envOrFlagSlice(flags *pflag.FlagSet, key string) []string {
    value, _ := flags.GetStringSlice(key)

    if v := viper.GetString(key); v != "" {
        parts := strings.SplitSeq(v, ",")
        for p := range parts {
            extraValue := p
            value = append(value, extraValue)
        }
    }

    return value
}
```

**Why it is a real bug (limited)**: If both the flag and the environment variable are set, entries from both sources are combined without deduplication. This could cause the same snap or deb to be installed twice. The snap handler would then attempt to install/refresh an already-installed snap, which would succeed but waste time. The deb handler similarly would re-install. Low severity because it is unlikely to cause failures, just wasted operations.

**Suggested fix**: Deduplicate the combined slice before returning, or document that env vars override rather than append to flags.

---

## Finding 12: `LXD.deconflictFirewall` unconditionally flushes FORWARD chain

- **File**: `/home/ubuntu/charm-tech-analysis/concierge/internal/providers/lxd.go`, lines 156-161
- **Pattern**: Idempotency / edge case (Patterns 2, 7)
- **Severity**: Medium

**Evidence**:
```go
func (l *LXD) deconflictFirewall() error {
    return system.RunMany(l.system,
        system.NewCommand("iptables", []string{"-F", "FORWARD"}),
        system.NewCommand("iptables", []string{"-P", "FORWARD", "ACCEPT"}),
    )
}
```

**Why it is a real bug**: This unconditionally flushes ALL rules in the FORWARD chain and sets the default policy to ACCEPT. If the host has legitimate firewall rules (e.g., in a multi-tenant environment, or if another provider like K8s has already configured its own forwarding rules), this silently destroys them. There is no check for whether Docker rules actually exist, no backup of existing rules, and no idempotency guard. Running `concierge prepare` with both LXD and another provider enabled would cause the LXD firewall flush to potentially break the other provider's networking. This relates to edge-case pattern from commit `00102fd0` (iptables not installed on minimal systems).

**Suggested fix**: Check whether Docker's FORWARD DROP rule actually exists before flushing, or use more targeted rule manipulation (e.g., insert specific rules rather than flushing the entire chain).

---

## Summary

| # | Finding | File | Severity | Pattern |
|---|---------|------|----------|---------|
| 1 | MicroK8s uses Google's ModelDefaults/BootstrapConstraints | microk8s.go:36-37 | **High** | Copy-paste / logic error |
| 2 | String-based error matching on snapd errors | snap.go:71,104,132 | Medium | Fragile error inspection |
| 3 | LXD init not idempotent | lxd.go:135-141 | Medium | Idempotency |
| 4 | Credentials map overwritten on each iteration | juju.go:141 | **High** | Logic error |
| 5 | Error discarded in checkBootstrapped wrapper | juju.go:194,270 | Medium | Error handling gap |
| 6 | LookPath error silently ignored | command.go:51-54 | Low | Error handling |
| 7 | RunWithRetries retries permanent failures | helpers.go:39-52 | Medium | Missing error discrimination |
| 8 | realUser hard-codes "root" fallback | util.go:55-62 | Low | Edge case |
| 9 | Non-active installed snaps treated as uninstalled | snap.go:101-124 | Medium | Snap state management |
| 10 | needsBootstrap returns false on transient errors | k8s.go:233-249 | Medium | Error handling gap |
| 11 | envOrFlagSlice produces duplicates | config.go:153-165 | Low | Edge case |
| 12 | Unconditional iptables FORWARD flush | lxd.go:156-161 | Medium | Idempotency / safety |

**High severity**: 2 findings (1, 4)
**Medium severity**: 7 findings (2, 3, 5, 7, 9, 10, 12)
**Low severity**: 3 findings (6, 8, 11)
