## Bug Review: Concierge Full Codebase Audit

### Summary
- **Findings**: 10 (2 High, 6 Medium, 2 Low)
- **Code areas reviewed**: internal/providers/ (all 4 providers), internal/system/ (snap, helpers, runner, command, dryrun, util), internal/juju/ (juju.go), internal/concierge/ (manager, plan, executable, validators), internal/packages/ (snap_handler, deb_handler), internal/snapd/ (client), internal/config/ (config, config_format, overrides, presets, util)

### Findings

#### [BUG-001] Copy-Paste — MicroK8s reads Google provider config (High)
- **Location**: `internal/providers/microk8s.go:36-37`
- **Pattern**: Copy-paste: wrong provider config
- **Issue**: `NewMicroK8s` sets `modelDefaults` and `bootstrapConstraints` from `config.Providers.Google` instead of `config.Providers.MicroK8s`.
- **Impact**: MicroK8s bootstraps with Google's model defaults and constraints. If Google is also configured, MicroK8s silently gets the wrong settings. If Google is not configured, both fields are nil maps and any attempt to iterate them is a no-op, masking the bug.
- **Evidence**:
  ```go
  return &MicroK8s{
      // ...
      modelDefaults:        config.Providers.Google.ModelDefaults,       // WRONG
      bootstrapConstraints: config.Providers.Google.BootstrapConstraints, // WRONG
  ```
  Compare with LXD (`config.Providers.LXD.*`) and K8s (`config.Providers.K8s.*`) which correctly reference their own config sections.
- **Recommended fix**:
  ```go
  modelDefaults:        config.Providers.MicroK8s.ModelDefaults,
  bootstrapConstraints: config.Providers.MicroK8s.BootstrapConstraints,
  ```
- **Historical precedent**: Documented in bug-patterns.md as a confirmed current bug.

#### [BUG-002] State Management — Credentials map overwrite in loop (High)
- **Location**: `internal/juju/juju.go:141-145`
- **Pattern**: State: map overwrite in loops
- **Issue**: Inside the loop over providers, each iteration replaces the entire `credentials["credentials"]` inner map with a new `map[string]any` containing only the current provider's credentials. Previous providers' credentials are silently discarded.
- **Impact**: When multiple providers have credentials (e.g., Google + another credentialed provider), only the last provider's credentials survive in `credentials.yaml`. All prior providers fail to authenticate during bootstrap.
- **Evidence**:
  ```go
  for _, p := range j.providers {
      if p.Credentials() == nil {
          continue
      }
      // Replaces entire inner map each iteration:
      credentials["credentials"] = map[string]any{
          p.CloudName(): map[string]any{
              "concierge": p.Credentials(),
          },
      }
      addedCredentials = true
  }
  ```
- **Recommended fix**:
  ```go
  for _, p := range j.providers {
      if p.Credentials() == nil {
          continue
      }
      credMap := credentials["credentials"].(map[string]any)
      credMap[p.CloudName()] = map[string]any{
          "concierge": p.Credentials(),
      }
      addedCredentials = true
  }
  ```
- **Historical precedent**: Documented in bug-patterns.md as a confirmed current bug.

#### [BUG-003] Error Handling — Discarded error in checkBootstrapped callers (Medium)
- **Location**: `internal/juju/juju.go:194` and `internal/juju/juju.go:270`
- **Pattern**: Error handling: discarded errors
- **Issue**: Both `bootstrapProvider` and `killProvider` call `checkBootstrapped` and construct a new error on failure without wrapping the original `err`. The diagnostic information from the original error (e.g., retry exhaustion, connection failure) is lost.
- **Impact**: Operators debugging bootstrap failures see "error checking bootstrap status for provider 'lxd'" with no underlying cause, making diagnosis difficult.
- **Evidence**:
  ```go
  bootstrapped, err := j.checkBootstrapped(controllerName)
  if err != nil {
      return fmt.Errorf("error checking bootstrap status for provider '%s'", provider.Name())
      // 'err' is discarded — should be: ...: %w", provider.Name(), err)
  }
  ```
- **Recommended fix**:
  ```go
  if err != nil {
      return fmt.Errorf("error checking bootstrap status for provider '%s': %w", provider.Name(), err)
  }
  ```
- **Historical precedent**: Documented in bug-patterns.md. Concierge entries reference discarded errors in juju.go.

#### [BUG-004] Retry Logic — RunWithRetries retries all errors indiscriminately (Medium)
- **Location**: `internal/system/helpers.go:39-52`
- **Pattern**: Retry: all errors retryable
- **Issue**: `RunWithRetries` marks every error as `retry.RetryableError(err)` without distinguishing permanent from transient errors. Permission denied, invalid arguments, and "not found" errors are retried for the full `maxDuration` (typically 5 minutes).
- **Impact**: Permanent failures (e.g., binary not found, invalid command arguments) cause 5-minute hangs with exponential backoff retries before finally failing with the same error. This is the dominant source of slow failure paths in concierge.
- **Evidence**:
  ```go
  return retry.DoValue(ctx, backoff, func(ctx context.Context) ([]byte, error) {
      output, err := w.Run(c)
      if err != nil {
          return nil, retry.RetryableError(err)  // ALL errors retried
      }
      return output, nil
  })
  ```
- **Recommended fix**:
  ```go
  if err != nil {
      if errors.Is(err, ErrNotInstalled) || errors.Is(err, exec.ErrNotFound) {
          return nil, err  // Permanent — don't retry
      }
      return nil, retry.RetryableError(err)
  }
  ```
- **Historical precedent**: Documented in bug-patterns.md. Commits `b418443e`, `20188c54`.

#### [BUG-005] Snap API — snapInstalledInfo treats non-Active installed snaps as uninstalled (Medium)
- **Location**: `internal/system/snap.go:115-123`
- **Pattern**: Snap: status state confusion
- **Issue**: `snapInstalledInfo` only reports a snap as installed when `snap.Status == snapd.StatusActive`. Snaps in other installed states (e.g., `installed` but not yet active after refresh) are reported as not installed, causing a fresh `snap install` instead of `snap refresh`.
- **Impact**: If a snap is installed but inactive (e.g., during a held refresh), concierge runs `snap install` instead of `snap refresh`, which can fail or produce unexpected behavior. The `SnapInfo.Installed` field and `SnapInfo.TrackingChannel` will be false/"" respectively.
- **Evidence**:
  ```go
  if snap.Status == snapd.StatusActive {
      trackingChannel := snap.TrackingChannel
      // ...
      return true, trackingChannel
  }
  return false, ""  // Installed but inactive → reports as NOT installed
  ```
- **Recommended fix**:
  ```go
  if snap.Status != "" {
      trackingChannel := snap.TrackingChannel
      if trackingChannel == "" {
          trackingChannel = snap.Channel
      }
      return true, trackingChannel
  }
  return false, ""
  ```
- **Historical precedent**: Documented in bug-patterns.md as a confirmed current bug.

#### [BUG-006] Idempotency — LXD init runs unconditionally (Medium)
- **Location**: `internal/providers/lxd.go:135-141`
- **Pattern**: Idempotency: unconditional operations
- **Issue**: `LXD.init()` runs `lxd init --minimal` unconditionally without checking if LXD is already initialized. Compare with `K8s.init()` which checks `needsBootstrap()` first. While `lxd waitready` runs first, re-running `lxd init --minimal` on an already-initialized LXD can reset network configuration.
- **Impact**: On re-run (e.g., after a partial failure), `lxd init --minimal` may disrupt an already-working LXD setup. The `lxc network set lxdbr0 ipv6.address none` also runs unconditionally.
- **Evidence**:
  ```go
  func (l *LXD) init() error {
      return system.RunMany(l.system,
          system.NewCommand("lxd", []string{"waitready", "--timeout", "270"}),
          system.NewCommand("lxd", []string{"init", "--minimal"}),
          system.NewCommand("lxc", []string{"network", "set", "lxdbr0", "ipv6.address", "none"}),
      )
  }
  // No check for existing initialization, unlike K8s.needsBootstrap()
  ```
- **Recommended fix**: Add an `isInitialized` check before running `lxd init --minimal`, similar to K8s provider.
- **Historical precedent**: Documented in bug-patterns.md. Commit `baf4fffe` fixed a similar idempotency issue in K8s.

#### [BUG-007] Firewall — Unconditional iptables FORWARD chain flush (Medium)
- **Location**: `internal/providers/lxd.go:156-161`
- **Pattern**: Firewall: unconditional flush
- **Issue**: `deconflictFirewall()` runs `iptables -F FORWARD` which flushes ALL rules in the FORWARD chain, not just Docker-related ones. If K8s or another provider has added FORWARD rules, they are destroyed.
- **Impact**: When LXD is prepared alongside K8s or another provider that sets iptables FORWARD rules, `deconflictFirewall` silently destroys those rules, potentially breaking networking for the other provider.
- **Evidence**:
  ```go
  func (l *LXD) deconflictFirewall() error {
      return system.RunMany(l.system,
          system.NewCommand("iptables", []string{"-F", "FORWARD"}),
          system.NewCommand("iptables", []string{"-P", "FORWARD", "ACCEPT"}),
      )
  }
  ```
- **Recommended fix**: Either target only Docker-specific rules, or check what rules exist before flushing. Consider using `iptables -D` to remove specific conflicting rules instead of `-F`.
- **Historical precedent**: Documented in bug-patterns.md as a confirmed current bug.

#### [BUG-008] Error Handling — K8s needsBootstrap swallows unexpected errors (Medium)
- **Location**: `internal/providers/k8s.go:233-249`
- **Pattern**: Error handling: boolean error swallowing
- **Issue**: `needsBootstrap()` returns `bool` without propagating unexpected errors. If `k8s status` fails for a transient reason (e.g., network timeout, temporary API unavailability) that is neither `ErrNotInstalled` nor the specific "not part of a Kubernetes cluster" message, the function falls through to `return false`, indicating "already bootstrapped" when in reality the status is unknown.
- **Impact**: Transient errors cause concierge to skip bootstrapping K8s, leaving it in an un-bootstrapped state while reporting success. The subsequent `k8s status --wait-ready` may then fail or hang.
- **Evidence**:
  ```go
  func (k *K8s) needsBootstrap() bool {
      // ...
      if err != nil {
          if errors.Is(err, system.ErrNotInstalled) {
              return true
          }
          if strings.Contains(string(output), "Error: The node is not part of a Kubernetes cluster.") {
              return true
          }
      }
      return false  // Transient error → treated as "already bootstrapped"
  }
  ```
- **Recommended fix**: Return `(bool, error)` and propagate unexpected errors to the caller.
  ```go
  func (k *K8s) needsBootstrap() (bool, error) {
      // ...
      if err != nil {
          if errors.Is(err, system.ErrNotInstalled) {
              return true, nil
          }
          if strings.Contains(string(output), "Error: The node is not part of a Kubernetes cluster.") {
              return true, nil
          }
          return false, fmt.Errorf("failed to check k8s status: %w", err)
      }
      return false, nil
  }
  ```
- **Historical precedent**: Documented in bug-patterns.md as a confirmed current bug.

#### [BUG-009] Error Handling — String-based snap error matching (Low)
- **Location**: `internal/system/snap.go:71`, `internal/system/snap.go:104`, `internal/system/snap.go:132`
- **Pattern**: Error handling: string-based matching
- **Issue**: Three call sites use `strings.Contains(err.Error(), "snap not found")` and `strings.Contains(err.Error(), "snap not installed")` to detect snap API errors. These strings come from the local `snapd/client.go` (lines 102, 143, 165) which uses `fmt.Errorf`, so the strings are currently stable. However, this creates tight coupling between the client error messages and the detection logic.
- **Impact**: If the error messages in `snapd/client.go` are changed (e.g., to match upstream snapd conventions) without updating these three call sites, the error detection silently breaks: "snap not found" errors would be treated as retryable transient errors, causing unnecessary retry loops. Risk is low because both sides are in the same repository.
- **Evidence**:
  ```go
  // snap.go:71
  if strings.Contains(err.Error(), "snap not found") {
      return nil, err
  }
  // snap.go:104
  if err != nil && strings.Contains(err.Error(), "snap not installed") {
      return snap, nil
  }
  ```
- **Recommended fix**: Define sentinel errors in `snapd/client.go` and use `errors.Is` for matching:
  ```go
  // In snapd/client.go:
  var ErrSnapNotFound = errors.New("snap not found")
  var ErrSnapNotInstalled = errors.New("snap not installed")

  // In snap.go:
  if errors.Is(err, snapd.ErrSnapNotFound) { ... }
  ```
- **Historical precedent**: Commits `63c74a37`, `20188c54`.

#### [BUG-010] Security — Credentials file written with 0644 permissions (Low)
- **Location**: `internal/system/helpers.go:84`
- **Pattern**: Security: file permissions
- **Issue**: `WriteHomeDirFile` writes all files with permissions `0644` (world-readable). This includes `credentials.yaml` (containing Juju cloud credentials, e.g., Google service account keys) and `kubeconfig` files. These should use restrictive permissions.
- **Impact**: Any local user can read Juju cloud credentials and Kubernetes config from `~/.local/share/juju/credentials.yaml` and `~/.kube/config`. On shared machines (common in CI environments where concierge runs), this is a credential exposure risk.
- **Evidence**:
  ```go
  // helpers.go:84 — hardcoded 0644 for ALL files
  if err := w.WriteFile(absPath, contents, 0644); err != nil {
  ```
  Called by `juju.go:160` to write `credentials.yaml` and by `k8s.go:230` / `microk8s.go:257` to write kubeconfig.
- **Recommended fix**: Use `0600` for sensitive files, or add a `perm` parameter to `WriteHomeDirFile`:
  ```go
  func WriteHomeDirFile(w Worker, filePath string, contents []byte, perm os.FileMode) error {
      // ...
      if err := w.WriteFile(absPath, contents, perm); err != nil {
  ```
- **Historical precedent**: Documented in bug-patterns.md under Security: file permissions.

### Confirmed Safe

- **Lock ordering in `helpers.go`**: `RunExclusive` acquires `cmdMu` (global), then a per-executable mutex. The global mutex is released before the per-executable mutex is acquired, so there is no multi-lock deadlock. The per-executable mutex is the only lock held during command execution.
- **`os.Lchown` usage in `runner.go:109`**: `ChownAll` correctly uses `os.Lchown` instead of `os.Chown`, avoiding symlink traversal.
- **`defer resp.Body.Close()` in `snapd/client.go`**: Both `Snap()` and `FindOne()` properly defer `resp.Body.Close()`. The response body is fully read before the function returns, so no data is lost.
- **`checkBootstrapped` retry logic**: The retry in `checkBootstrapped` correctly distinguishes `ErrNotInstalled` (permanent, returns false without retry) from the specific "controller not found" message (permanent, returns false) vs other errors (retryable). This is well-designed.
- **`errgroup` usage in `plan.go`**: The errgroup is reused between provider preparation phases, but `eg.Wait()` is called between them, ensuring the previous phase completes before the next starts. This is correct usage.
- **Snap retry logic in `snap.go`**: `SnapChannels` and `snapIsClassic` correctly short-circuit on "snap not found" (permanent) and only retry other errors. This is correct retry discrimination within the snap layer, contrasting with the generic `RunWithRetries` issue in BUG-004.
