# Cross-Repository Bug Pattern Analysis: Canonical Charm Tech

A comprehensive analysis of **452 bug-fix commits** across 10 repositories in the Canonical Charm Tech ecosystem, synthesized from individual repo classifications.

**Repos analyzed**: operator (Python), pebble (Go), concierge (Go), charmlibs (Python), jubilant (Python), pytest-jubilant (Python), operator-libs-linux (Python), charmhub-listing-review (Python), charmcraft-profile-tools (Python), charm-ubuntu (Python)

**Date range**: August 2019 through March 2026

---

## 1. Aggregate Statistics

### Total Fixes by Repository

| Repository | Fixes | High | Medium | Low | Language |
|---|---|---|---|---|---|
| operator | 218 | 48 | 136 | 34 | Python |
| pebble | 108 | 27 | 42 | 39 | Go |
| concierge | 35 | 8 | 17 | 10 | Go |
| operator-libs-linux | 29 | 7 | 7 | 15 | Python |
| jubilant | 18 | 7 | 8 | 3 | Python |
| charmlibs | 19 | 2 | 7 | 10 | Python |
| charmcraft-profile-tools | 7 | 0 | 4 | 3 | Python |
| charm-ubuntu | 7 | 1 | 3 | 3 | Python |
| charmhub-listing-review | 6 | 0 | 6 | 0 | Python |
| pytest-jubilant | 5 | 2 | 3 | 0 | Python |
| **TOTAL** | **452** | **102** | **233** | **117** |  |

**Severity distribution**: 22.6% High, 51.5% Medium, 25.9% Low

### Total Fixes by Bug Type (Cross-Repo)

| Bug Type | operator | pebble | concierge | libs-linux | jubilant | charmlibs | smaller* | Total |
|---|---|---|---|---|---|---|---|---|
| logic-error | 93 | 21 | 8 | 12 | 4 | 3 | 4 | **145** |
| error-handling | 14 | 12 | 8 | 0 | 2 | 1 | 0 | **37** |
| edge-case | 5 | 5 | 6 | 5 | 3 | 2 | 1 | **27** |
| concurrency | 0 | 13 | 0 | 0 | 0 | 0 | 0 | **13** |
| type-error | 12 | 1 | 0 | 5 | 1 | 4 | 0 | **23** |
| api-contract | 4 | 4 | 0 | 4 | 8 | 3 | 2 | **25** |
| test-divergence | 16 | 0 | 0 | 0 | 0 | 0 | 0 | **16** |
| data-validation | 13 | 3 | 1 | 2 | 0 | 0 | 1 | **20** |
| none-guard | 10 | 0 | 0 | 0 | 0 | 0 | 0 | **10** |
| nil-pointer | 0 | 7 | 0 | 0 | 0 | 0 | 0 | **7** |
| naming-mismatch | 10 | 0 | 0 | 0 | 0 | 0 | 0 | **10** |
| mutability | 6 | 0 | 0 | 0 | 0 | 2 | 0 | **8** |
| race-condition | 2 | 6 | 0 | 0 | 1 | 0 | 0 | **9** |
| security | 0 | 8 | 0 | 0 | 0 | 0 | 0 | **8** |
| version-compat | 9 | 0 | 0 | 0 | 0 | 0 | 0 | **9** |
| state-management | 0 | 5 | 4 | 1 | 0 | 0 | 0 | **10** |
| config-related | 0 | 0 | 3 | 9 | 0 | 0 | 6 | **18** |
| exception-type | 8 | 0 | 0 | 0 | 0 | 0 | 0 | **8** |
| other/misc | 25 | 17 | 3 | 7 | 3 | 4 | 5 | **64** |
| parsing | 1 | 0 | 0 | 1 | 1 | 0 | 0 | **3** |
| resource-leak | 0 | 2 | 1 | 0 | 0 | 0 | 0 | **3** |
| performance | 0 | 4 | 0 | 0 | 0 | 0 | 0 | **4** |

*smaller = charmhub-listing-review + charmcraft-profile-tools + charm-ubuntu + pytest-jubilant

### Cross-Repo Heatmap: Bug Types by Repository

```
                      operator  pebble  concierge  libs-linux  jubilant  charmlibs  smaller
logic-error              +++      ++       +           +          +         +          +
error-handling            +       ++      +++                     +         +
edge-case                 +        +      +++          +          +         +          +
concurrency                      +++
type-error               ++                            +          +        ++
api-contract              +        +                   +         +++       ++          +
test-divergence         +++
data-validation          ++        +        +          +                               +
mutability               ++                                                +
nil-pointer/none-guard   ++      +++
race-condition            +       ++                              +
security                         +++
state-management                  +       ++           +
config-related                           ++          +++                             +++
naming-mismatch          ++
version-compat           ++                                       +

Legend: +++ = dominant (>10% of repo fixes), ++ = significant (5-10%), + = present (<5%)
```

### Fix Categories

| Category | Count | Percentage |
|---|---|---|
| source-fix | 331 | 73.2% |
| test-fix | 64 | 14.2% |
| ci-fix | 28 | 6.2% |
| docs-fix | 18 | 4.0% |
| build-fix | 11 | 2.4% |

---

## 2. Universal Patterns (Appear Across 3+ Repos)

### Pattern 1: Logic Errors in Conditional/Control Flow (145 instances, all 10 repos)

The single most common bug type across the entire ecosystem. These are incorrect conditions, wrong branches, missing code paths, or inverted logic.

**Affected repos**: All 10 (32% of all fixes)

**Concrete examples**:

- **operator** (`3ce1c7f`): `secret-info-get` allowed passing both ID and label simultaneously, but Juju rejects this. Missing guard clause.
- **pebble** (entry 63): Named return variable `err` was overwritten by deferred `reaper.Stop()`, losing the original error value. Fix: use local variable instead of named return.
- **concierge** (`dd30fa88`): Debug logging condition used AND instead of OR: `if verbose && trace` instead of `if verbose || trace`, so debug logs only showed when *both* flags were set.
- **operator-libs-linux** (`322f9b4833b6`): Copy-paste error in `snap.set()` caused it to not actually set the key/value correctly.
- **jubilant** (`30f07eaf`): `WaitError` message said error function "returned false" when it actually returned true (inverted polarity).
- **charmcraft-profile-tools** (`8d4730bb`): Justfile checked for `.ven` instead of `.venv`, so venv existence check always failed.

**Before/After**:
```python
# Before (concierge, Go):
if verbose && trace {
    log.SetLevel(log.DebugLevel)
}

# After:
if verbose || trace {
    log.SetLevel(log.DebugLevel)
}
```

**Recommendation**: This is too broad to detect with a single rule, but sub-patterns are detectable: inverted boolean conditions, copy-paste errors, missing else branches.

---

### Pattern 2: Edge Cases at Input Boundaries (27 instances, 7 repos)

Unhandled empty, missing, nil, or unusual inputs causing crashes or silent failures.

**Affected repos**: operator, pebble, concierge, operator-libs-linux, jubilant, charmlibs, pytest-jubilant

**Concrete examples**:

- **operator** (`f005747b`): Empty Juju config options map was not handled, causing crash on charm startup.
- **pebble** (entry 4): `json.Marshal(nil)` produces `null` but API consumers expected `[]` for empty arrays.
- **concierge** (`00102fd0`): iptables not installed on minimal systems, causing k8s provider failure.
- **operator-libs-linux** (`74ddb086`): `snap.get` with falsy key (`None`) crashed instead of returning all config.
- **jubilant** (`814ab9b8`): `KeyError` on Juju < 3.6 which lacks the 'checksum' field in revealed secrets.
- **pytest-jubilant** (`3404c373`): `pack_charm()` crashed when charm metadata had no `resources` section.
- **charmlibs** (`aaf1d1fb`): Version string read from file contained trailing newline whitespace.

**Before/After**:
```python
# Before (pytest-jubilant):
resources = meta['resources']  # KeyError if no resources section

# After:
resources = meta.get('resources', {})
```

**Recommendation**: High-value pattern for a skill. Detectable by looking for dict access without `.get()`, missing `None` checks before attribute access, and assumptions about external data completeness.

---

### Pattern 3: Error Handling Gaps (37 instances, 6 repos)

Missing error paths, wrong exception types, swallowed errors, or inadequate error messages.

**Affected repos**: operator, pebble, concierge, jubilant, charmlibs, charmhub-listing-review

**Concrete examples**:

- **operator** (`97501fd7`): Caught the wrong exception type when checking if a relation exists, causing unhandled crashes.
- **pebble** (entry 63): Named return `err` was overwritten by deferred function, losing the original error.
- **concierge** (`e28f3b50`): Command failures were only logged in trace mode, making debugging impossible in normal operation.
- **charmlibs** (`6cfdcc75`): CI lint script was missing `exit $FAILURES`, causing linting to always report success even when errors existed.
- **jubilant** (`ae4efad6`): `StatusError` exceptions on transient machine setup states crashed `wait()` instead of allowing retry.

**Before/After**:
```python
# Before (operator):
except RelationNotFoundError:  # Wrong exception class
    pass

# After:
except KeyError:  # Correct -- Juju raises KeyError for missing relations
    pass
```

---

### Pattern 4: API Contract Mismatches (25 instances, 7 repos)

Functions called with wrong argument types, wrong argument combinations, or misunderstanding of upstream API behavior.

**Affected repos**: operator, pebble, operator-libs-linux, jubilant, charmlibs, charmhub-listing-review, charm-ubuntu

**Concrete examples**:

- **operator** (`0dd27df3`): `RelationDataContent.update()` signature did not accept keyword-only args, breaking standard dict interface.
- **jubilant** (`5feadf3b`): `deploy --bind` used comma-separated format but Juju CLI expects space-separated `key=value` pairs.
- **charmlibs** (`0de72f66`): `Mode.APP` stored private keys as unit-owned secrets instead of app-owned, violating the ownership model.
- **operator-libs-linux** (`b2096f78`): Systemd helper functions were public but should have been private API.
- **charm-ubuntu** (`59324d47`): Used `addClassCleanup` which was not available in all Python versions.

**Before/After**:
```python
# Before (jubilant):
bind_arg = ",".join(f"{k}={v}" for k, v in bindings.items())
# Produces: "ep1=space1,ep2=space2"

# After:
bind_arg = " ".join(f"{k}={v}" for k, v in bindings.items())
# Produces: "ep1=space1 ep2=space2"
```

---

### Pattern 5: Type Confusion (int/str, type()/isinstance()) (23 instances, 5 repos)

Wrong types used for parameters, incorrect type checks, or missing type coercion.

**Affected repos**: operator, pebble, operator-libs-linux, jubilant, charmlibs

**Concrete examples**:

- **operator** (`0fc35804`): `JujuContext.machine_id` was `int` but Juju machine IDs can be strings like `"0/lxd/0"`.
- **operator-libs-linux** (`57e7a6f9`): Used `type()` instead of `isinstance()` for type checks, failing for subclasses and allowing `bool` to pass as `int`.
- **operator-libs-linux** (`1a09b160`): Snap revision was handled as `int` but should be `str` -- major enough to require a v2 bump.
- **jubilant** (`fde3e333`): `Juju.exec` machine parameter only accepted `int`, but LXD containers like `"0/lxd/0"` require `str`.
- **charmlibs** (`d1262302`): `snap.logs()` num_lines only accepted `int` but snap CLI also accepts `"all"`.

**Before/After**:
```python
# Before (operator-libs-linux):
if type(package) == str:  # Fails for subclasses
    ...

# After:
if isinstance(package, str):  # Correct
    ...
```

---

### Pattern 6: CI/Build Configuration Issues (28 instances, 7 repos)

Broken workflows, wrong paths, missing dependencies, masked test failures.

**Affected repos**: operator, pebble, concierge, charmlibs, charmhub-listing-review, charmcraft-profile-tools, charm-ubuntu

**Concrete examples**:

- **charmlibs** (`6cfdcc75`): Lint script missing `exit $FAILURES` -- masked pyright errors across multiple libraries.
- **charm-ubuntu** (`89a3e4cf`): CI referenced `master` branch which was renamed to `main`.
- **charmhub-listing-review** (`b3fec634`): Workflow ran script directly instead of installing package first.
- **charmcraft-profile-tools** (`3f9d8337`): CI missing `tox` and `tox-uv` installation step.
- **operator** (`c3dde624`): Broken GitHub variable expansion in workflow.
- **pebble**: Go version bumps required for CVE-2024-24790 (entries 40, 42).

---

### Pattern 7: State Management / Idempotency Issues (10 instances, 3 repos)

Operations that fail on re-run because they assume fresh state.

**Affected repos**: pebble, concierge, operator-libs-linux

**Concrete examples**:

- **concierge** (`baf4fffe`): `k8s bootstrap` was not idempotent -- running `concierge prepare` twice broke the system.
- **concierge** (`0ddf24c3`): Removing `/run/containerd` when k8s is already bootstrapped breaks running services.
- **concierge** (`158c3a70`): LXD was stopped for refresh but never restarted, leaving it in a broken state.
- **pebble**: Carryover state from previous daemon runs referenced keys that no longer exist, causing panics on type assertion.

**Before/After**:
```go
// Before (concierge):
func (p *K8sProvider) Bootstrap() error {
    return p.runCommand("k8s", "bootstrap")  // Fails if already bootstrapped
}

// After:
func (p *K8sProvider) Bootstrap() error {
    if p.isBootstrapped() {
        return nil  // Skip if already done
    }
    return p.runCommand("k8s", "bootstrap")
}
```

---

### Pattern 8: Data Validation at Trust Boundaries (20 instances, 5 repos)

Missing or incorrect validation of data from external sources (CLI output, API responses, user input, relation data).

**Affected repos**: operator, pebble, concierge, operator-libs-linux, charmhub-listing-review

**Concrete examples**:

- **operator** (`4ffc1256`): Non-string keys could be used in relation data, violating the `Dict[str, str]` contract.
- **operator** (`668701b4`): Databag access validation was not enabled during `__init__`, allowing invalid operations.
- **pebble**: API request validation missing for POST endpoints (entries 50-54).
- **concierge** (`b418443e`): No pre-check for snap existence before entering retry loop.
- **charmhub-listing-review** (`b45e0d53`): Incorrect GitHub username in reviewers.yaml caused silent assignment failure.

---

## 3. Python-Specific Patterns

These patterns appear only in the Python repos (operator, charmlibs, jubilant, pytest-jubilant, operator-libs-linux, charmhub-listing-review, charmcraft-profile-tools, charm-ubuntu).

### 3.1 Data Mutability at API Boundaries (8 instances)

**Repos**: operator (6), charmlibs (2)

The most persistent and insidious Python pattern. Dicts and lists passed by reference allow callers to silently corrupt internal state, or internal state changes to leak to callers.

**Key commits**:
- `3f8fb9b9` (operator): `testing.Context` held direct references to user-provided dicts for `meta`, `config`, and `actions`. Users mutating their own dict after passing it would corrupt test state.
- `be09012` (operator): `_MockModelBackend.relation_get` returned the actual stored relation data dict -- callers could mutate it.
- `385bdf03` (operator): Config state was mutable, allowing charms to accidentally modify their own config.
- `3dda5b5f` (operator): Pebble layer merging in Harness mutated the original layer objects.
- `89d6218e` (charmlibs): Missing `__hash__` on certificate classes after migration from dataclasses (which auto-generate `__hash__`).
- `49e542c6` (charmlibs): Same pattern -- `CertificateRequestAttributes` missing `__hash__`.

**The fix pattern is always the same**:
```python
# BUG: stores reference
self._meta = meta

# FIX: copy on store
self._meta = dict(meta)

# BUG: returns reference
def get_config(self):
    return self._config

# FIX: copy on return
def get_config(self):
    return dict(self._config)
```

**Hashability sub-pattern**: When migrating from `dataclass(frozen=True)` to plain classes, `__hash__` must be explicitly added. Two separate commits in charmlibs hit this (months apart), suggesting the migration was done without a protocol compliance checklist.

### 3.2 Testing Framework Divergence from Production (16 instances)

**Repos**: operator (16)

Unique to operator because it maintains both Harness and Scenario testing frameworks that must replicate Juju behavior. This is the single largest bug area in the entire ecosystem (51 fixes when including related testing-framework fixes).

**Sub-patterns**:
- **Secret behavior divergence**: Harness secrets not matching Juju (`79706f40`, `e7e2c8d`, `0fa4497`)
- **Relation event simulation**: Wrong remote unit handling, missing databag access (`5a63e01e`, `cb720c85`)
- **Environment variable leakage**: Tests modifying `os.environ` and leaking state (`e302b630`, `101997e6`)
- **Context manager lifecycle**: Testing context not properly exiting on exceptions (`3ac3706b`)
- **Pebble simulation**: Layer merging, service names, check infos not matching real Pebble (`3dda5b5f`, `1b10db40`)

### 3.3 Type Annotation Errors (12 instances)

**Repos**: operator (8), charmlibs (4)

**Sub-patterns**:
- **Wrong return types**: `Model.get_binding()` annotated incorrectly (`3df8ae9`)
- **Assignment vs annotation syntax**: `StorageMeta.properties = list[str]` instead of `: list[str]` (`aa06bf54`)
- **Import compatibility**: mypy not understanding conditional imports (`d6325d05`)
- **pyright strictness**: Multiple charmlibs fixes for pyright compliance (`0d09cef6`)
- **Optional vs non-Optional**: `FileInfo.user/group` typed as Optional but actually always present (`00aea1c0`)

### 3.4 Import/Module Issues (6 instances)

**Repos**: operator (4), pytest-jubilant (1), charmhub-listing-review (1)

- **Cyclic imports**: `14f3baf5` (operator) -- circular dependency between modules
- **Missing `__init__.py` exports**: `15ce4176` (pytest-jubilant) -- functions in `__all__` but not imported
- **Package installation**: `b3fec634` (charmhub-listing-review) -- script run without installing package first

### 3.5 Dict/List Handling Pitfalls (15+ instances)

**Repos**: operator, operator-libs-linux, jubilant, pytest-jubilant

Beyond the mutability pattern above:
- **Missing `.get()` for optional keys**: Multiple crashes from `dict[key]` instead of `dict.get(key, default)` -- affects operator (relation data, secrets), jubilant (CLI output parsing), pytest-jubilant (charm metadata)
- **Falsy value confusion**: `1c0ff40d` (operator) -- empty string, 0, and False config defaults treated as missing because of `if not value` checks
- **Non-string keys in string-only dicts**: `4ffc1256` (operator) -- Python happily writes int keys to a dict that Juju requires to be `Dict[str, str]`

### 3.6 Secrets/Relation Data Handling (52 instances combined)

**Repos**: operator (50), charmlibs (2)

The largest domain-specific bug area. See Section 5 for detailed analysis.

---

## 4. Go-Specific Patterns

These patterns appear only in the Go repos (pebble, concierge).

### 4.1 Concurrency Bugs: Deadlocks and Race Conditions (19 instances in pebble)

The dominant high-severity pattern in Go code. Pebble's architecture involves multiple goroutines with independent locks.

**Sub-patterns**:

**Multi-lock deadlock** (most common): Goroutines acquiring `servicesLock`, `state lock`, and `planLock` in different orders.
- Pebble entries 73-79: 3-lock deadlock between servicesLock, state lock, and planLock. Fix: reduce lock scope and decouple locking from callbacks.
- Entry 45: `net/http` panic recovery while a lock is held leaves the lock permanently held, deadlocking the entire daemon. Fix: disable default panic recovery.

**sync.Cond broadcast timing**: Entry 12 -- `sync.Cond.Broadcast()` called outside the Cond's lock, so the signal is missed by goroutines not yet in `Wait()`.

**tomb.Tomb lifecycle**: Entry 3 (sha `f7589e55`) -- creating a `tomb.Tomb` without starting a goroutine on it causes `Wait()` to block forever. Fix: lazy initialization.

**Cmd.WaitDelay**: Entry 90 -- child processes inheriting stdin/stdout/stderr FDs prevent `Command.Wait` from returning. Fix: use Go 1.20's `Cmd.WaitDelay`.

### 4.2 Nil Pointer/Map Panics (7 instances in pebble)

Go-specific: assigning to a nil map panics, and nil state after restart causes type assertion failures.

**Key commits**:
- Pebble entry 100: `CombineLayers` panics when merging service environment maps because the target map was nil. Fix: initialize map before merge.
- Entries 16-17, 49: Carryover state keys from previous daemon runs reference objects that no longer exist, causing panics on type assertion.

**Before/After**:
```go
// Before: nil map panic
service.Environment[key] = value  // panics if Environment is nil

// After:
if service.Environment == nil {
    service.Environment = make(map[string]string)
}
service.Environment[key] = value
```

### 4.3 Error Wrapping and String-Based Error Matching (8+ instances in concierge)

Go's error handling encourages `strings.Contains(err.Error(), ...)` when dealing with external command output. This is inherently fragile.

**Key commits**:
- `63c74a37` (concierge): Matched `"not found"` too broadly; changed to `"controller <name> not found"` to avoid false positives from transient errors.
- `20188c54` (concierge): Short-circuit retry when snap is definitively "not found" in the store, but `"not found"` can appear in other error messages.

**Recommendation**: Define sentinel errors and use `errors.Is`/`errors.As` where possible. For CLI output, use structured parsing (JSON output flags) instead of substring matching.

### 4.4 Struct Initialization Pitfalls (2 instances)

Go compilers do not enforce constructor usage -- zero-value structs are valid but may lack required initialization.

- `34230b59` (concierge): `&concierge.Manager{}` (zero-value) used instead of `concierge.NewManager(conf)`, causing nil pointer dereference at runtime.
- Pebble's `tomb.Tomb` issue: tomb created without starting a goroutine, blocking forever on `Wait()`.

### 4.5 Named Return Value Shadowing (1 instance)

- Pebble entry 63: Named return `err` was overwritten by deferred `reaper.Stop()`, losing the original error. Fix: switch from named return to local variable.

### 4.6 JSON Marshaling Nil vs Empty (1 instance)

- Pebble entry 4: `json.Marshal(nil)` produces `null` but `json.Marshal([]string{})` produces `[]`. API consumers expected `[]`.

### 4.7 os.Chown vs os.Lchown (1 instance)

- `39a18ffc` (concierge): `os.Chown` follows symlinks while `os.Lchown` does not. Fix prevents privilege escalation through symlink traversal.

---

## 5. Domain-Specific Patterns (Juju/Charm Ecosystem)

### 5.1 Juju CLI Argument Formatting (10+ instances)

**Repos**: operator, jubilant, operator-libs-linux

The Juju CLI is the primary interface for charm operations, and its argument format is a frequent source of bugs.

**Concrete examples**:
- **jubilant** (`5feadf3b`): `--bind` uses space-separated format, not comma-separated
- **jubilant** (`2c749e95`): `juju offer` does not accept `--model` flag
- **operator** (`5151a1e`): `--app` flag for `relation-get`/`relation-set` not available before Juju 2.7.0
- **operator** (`9fe65c7c`): Switched to `--file` for `relation-set` to avoid shell argument length limits
- **operator-libs-linux** (`abe9ec7c`, `0ac58381`): Snap install/refresh cohort and channel args not properly formatted as CLI flags

**Pattern**: Every wrapper around `juju` or `snap` CLI hits argument formatting bugs. The fix is always to test against the actual CLI, not just the documentation.

### 5.2 Relation Data Lifecycle (33 instances in operator)

The most complex domain area. Relations are Juju's inter-charm communication mechanism.

**Key sub-patterns**:
- **Accessing data after relation-broken**: Data bags unavailable but code tries to access them (`1b086258`)
- **Non-string keys/values**: Juju requires `Dict[str, str]` but Python doesn't enforce this (`4ffc1256`)
- **Remote unit availability**: Wrong units added for wrong event types (`5a63e01e`)
- **Relation-departed data access**: Remote unit data IS available in relation-departed but code assumed it wasn't (`794e0e1a`)
- **Shell argument length**: Large relation data exceeding command-line limits (`9fe65c7c`)

### 5.3 Secrets Management (19 instances across operator + charmlibs)

Secrets are a newer Juju feature (introduced ~2023) and have been a persistent bug source.

**Key sub-patterns**:
- **ID canonicalization**: Juju uses `secret:<id>` format; code sometimes omits prefix (`7670b59c`)
- **Caching**: Stale cached secrets (`9323ead`)
- **Conflicting API arguments**: `secret-info-get` cannot accept both ID and label (`3ce1c7f`, `5afc2842`)
- **Owner normalization**: Inconsistencies between ops and testing (`e7e2c8d`)
- **App vs unit ownership**: Private keys stored as unit-owned instead of app-owned in charmlibs (`0de72f66`)
- **Event reliability**: `secret_expired` can fail to trigger, requiring safety-net fallbacks (`8fdf5b4f`)

### 5.4 Pebble Layer/Service Management (32 instances in operator + 17 in pebble)

Pebble is the workload manager inside charm containers.

**Operator-side bugs** (Python client):
- Path handling (relative paths, empty dirs, binary files)
- Layer merging semantics in testing vs production
- Container.restart() iterating over string characters instead of treating as single service (`37fdcbaf`)
- Exec process stdout iteration not working correctly (`91b6551a`)

**Pebble-side bugs** (Go server):
- Service lifecycle deadlocks (multi-lock ordering)
- Nil map panics in CombineLayers
- Notice timing races
- Exec subprocess cleanup (Cmd.WaitDelay)

### 5.5 Testing vs Production Divergence (51+ instances)

The largest single bug area. Spans operator (Harness/Scenario) and pebble (test helpers).

**Why it's so large**: The testing frameworks must faithfully simulate:
- Juju event dispatch ordering
- Relation data visibility at each lifecycle stage
- Secret behavior (caching, ownership, labels)
- Pebble layer merging semantics
- Environment variable exposure
- Status transitions and validation

Every bug fix in the production code potentially requires a matching fix in the testing framework.

### 5.6 Version Compatibility (11+ instances)

**Repos**: operator (9), jubilant (2)

- **Juju version**: Features like `credential-get`, `--app` flag, secrets checksums only available in certain Juju versions
- **Python version**: datetime parsing, typing syntax, dataclass features differ across 3.8-3.12+
- **Go version**: CVE patches requiring Go version bumps (pebble)

### 5.7 Snap API Interaction (19 instances across concierge + operator-libs-linux)

The snapd REST API is a significant source of flakiness and bugs:
- Rate limiting ("too many requests")
- Task status states (`Do` as a valid pending state)
- Revision type (int vs str)
- Channel/confinement mismatches
- Retry logic needed for nearly all operations

---

## 6. Recommendations for Skill Design

### 6.1 Should We Build One Skill or Multiple?

**Recommendation: Build two skills with shared infrastructure.**

1. **A Python/Charm-focused skill** covering:
   - Data mutability at API boundaries
   - Missing None/optional guards
   - Dict access patterns (`.get()` vs `[]`)
   - Relation data lifecycle
   - Secrets management patterns
   - Type annotation correctness
   - Testing/production divergence awareness

2. **A Go/Systems-focused skill** covering:
   - Lock ordering and deadlock prevention
   - Nil map/pointer guards
   - Error wrapping and inspection patterns
   - Struct initialization (constructor enforcement)
   - Goroutine lifecycle management
   - Named return value pitfalls

**Rationale**: The Python and Go patterns have almost zero overlap. The only universal patterns (logic errors, edge cases, error handling) are too broad to capture in language-agnostic rules -- they manifest differently in each language. Maintaining two focused skills will produce higher-quality detections.

### 6.2 Highest-Value Patterns to Include

Ranked by (frequency x severity x detectability):

| Rank | Pattern | Instances | Avg Severity | Detectability | Language |
|---|---|---|---|---|---|
| 1 | Data mutability at boundaries | 8 | High | High -- look for dict/list assignments without `.copy()` | Python |
| 2 | Missing None/optional guards | 10 | High | High -- look for attribute access without None check | Python |
| 3 | Nil map/pointer panics | 7 | High | High -- look for map assignment without init check | Go |
| 4 | Concurrency/lock ordering | 19 | High | Medium -- requires understanding lock acquisition patterns | Go |
| 5 | Dict access without `.get()` | 15+ | Medium-High | High -- syntactic pattern | Python |
| 6 | Juju CLI argument formatting | 10+ | High | Medium -- requires knowledge of Juju CLI contracts | Both |
| 7 | Relation data lifecycle | 33 | High | Medium -- requires lifecycle knowledge | Python |
| 8 | Secrets ID canonicalization | 5 | High | High -- check for `secret:` prefix | Python |
| 9 | Type confusion (int/str) | 23 | Medium | High -- type checker integration | Python |
| 10 | String-based error matching | 8+ | Medium | High -- flag `strings.Contains(err.Error()` | Go |
| 11 | Struct zero-value vs constructor | 2 | High | Medium -- flag `&Type{}` without constructor | Go |
| 12 | Named return shadowing | 1 | High | High -- flag deferred calls that overwrite named returns | Go |

### 6.3 Language-Specific vs Universal Patterns

**Language-specific** (must be in separate skills):
- Python: mutability, `__hash__`, type annotations, `isinstance()` vs `type()`, import cycles, `os.environ` leakage
- Go: concurrency/locks, nil maps, `sync.Cond` timing, `tomb.Tomb` lifecycle, JSON nil vs empty, `os.Chown` vs `os.Lchown`, named returns

**Domain-specific** (could be shared knowledge base):
- Juju CLI argument contracts
- Relation data lifecycle rules
- Secrets management rules
- Pebble layer merging semantics
- Version compatibility matrices

**Truly universal** (applicable everywhere):
- Edge case handling at input boundaries
- Error handling completeness
- Idempotency for stateful operations
- CI configuration correctness
- API contract compliance

### 6.4 False-Positive Controls Needed

1. **Mutability pattern**: Not every dict assignment needs `.copy()`. Only flag when:
   - The dict is received as a function parameter AND stored as an instance attribute
   - The dict is an internal attribute AND returned from a public method
   - The class is part of a testing framework or API boundary

2. **None guard pattern**: Not every attribute access needs a None check. Only flag when:
   - The value comes from an external source (Juju API, environment variable, dict lookup)
   - The code is in an event handler (where Juju state may be incomplete)
   - The value is documented as Optional in type annotations

3. **Dict `.get()` pattern**: Not every `dict[key]` is a bug. Only flag when:
   - The dict comes from parsing external data (JSON, YAML, CLI output)
   - The key is a string literal that could vary by version or context
   - There's no preceding `if key in dict` check

4. **Go nil map pattern**: Only flag when:
   - The map is a struct field (not a local variable)
   - There's no initialization in the constructor or preceding code path
   - The struct could be created via zero-value (`&Type{}`)

5. **Lock ordering pattern**: Requires call-graph analysis to detect. Should only flag when:
   - Two or more locks are acquired in the same function
   - The same locks appear in different order in different functions
   - The locks are struct-level mutexes (not function-scoped)

6. **CI/config patterns**: These are low-value for a skill -- they are one-off issues specific to each repo's CI setup. Include only as general awareness, not as detection rules.

### 6.5 Data-Driven Priority Summary

Based on the 452 fixes analyzed:

- **73%** of all fixes are source-level code changes (highest ROI for a code-review skill)
- **22.6%** are high-severity (102 fixes that caused crashes, data corruption, or security issues)
- **The top 5 bug types account for 60%** of all fixes: logic-error (32%), error-handling (8%), edge-case (6%), api-contract (6%), type-error (5%)
- **Testing-framework divergence** is the single largest *area* (51 fixes, 11%) but is highly specific to operator
- **Relation data handling** is the most cross-cutting domain pattern (33 fixes in operator + 2 in charmlibs)
- **Concurrency** is the highest-severity Go-specific pattern (19 fixes, 76% high-severity)
- **Data mutability** has the highest severity-to-frequency ratio in Python (8 fixes, all high-severity)

The skill should prioritize patterns that are **both detectable and high-impact**: mutability, nil/None guards, dict access safety, and Juju-specific lifecycle rules.
