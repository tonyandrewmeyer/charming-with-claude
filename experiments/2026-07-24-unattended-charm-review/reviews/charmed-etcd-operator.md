# charmed-etcd-operator

A mature, well-structured machine charm that deploys and manages single- or multi-node etcd
clusters on VMs, covering TLS, backup/restore to S3/Azure, client relations, cluster membership,
HA failover, and in-place upgrades via charm-refresh. The code is production-grade and
well-tested. The main actionable issue is a hardcoded 10-second subprocess timeout that is too
short for slow cluster operations (e.g. member promotion); everything else is minor polish.
A maintainer should fix the subprocess timeout first, then tighten the two type/message issues
in config and external-client handling.

| | |
|---|---|
| Repo | `canonical/charmed-etcd-operator` @ `5214bcf` (2026-07-15) |
| Charms | `charmed-etcd`, `requirer-charm` (test-only) |
| Substrate | machine |
| Deployed | yes — `concierge-lxd` (Juju 3.6.27), `charmed-etcd` 3.6/stable rev 181 |
| Reviewed | 2026-08-17 |

## What it does

The `charmed-etcd` machine charm installs the `charmed-etcd` snap (rev 38 on amd64), configures and
starts etcd, and manages a Raft cluster of one or more units. It handles TLS via relation to a
`tls-certificates` provider (peer and client certificates independently), exposes an `etcd-client`
interface for external applications, supports backup/restore to S3 or Azure blob storage, and
implements a coordinated multi-step disaster-recovery workflow (rebuild-cluster) plus a
charm-refresh upgrade path with pre-flight health checks.

## Deployment log

```
# Bootstrap model
juju add-model rv-etcd-test -c concierge-lxd localhost

# Deploy from charmhub
juju deploy charmed-etcd --channel 3.6/stable
  → revision 181, ubuntu@24.04

# Wait for machine + agent
  machine pending → started: ~90s
  install hook: ~90s (08:04:57 → 08:06:30)
  cluster init + start: ~15s
  active/idle: 08:06:55

# Verify workload
juju ssh charmed-etcd/0 'charmed-etcd.etcdctl endpoint status'
  → {"Status":{"version":"3.6.13","leader":"14118785660492827405",...}}

# Add TLS: deploy self-signed-certificates and relate
juju deploy self-signed-certificates
juju integrate charmed-etcd:peer-certificates self-signed-certificates
juju integrate charmed-etcd:client-certificates self-signed-certificates
  → peer TLS established at 08:14:29–08:14:41
  → client TLS established at 08:16:19–08:16:33
  → both use https:// in listen-* and advertise-* URLs ✓

# Test config validation
juju config charmed-etcd heartbeat-interval=150
  → BlockedStatus correctly set: "Election timeout 1000 is invalid. It must be
    at least 10x the heartbeat interval (150)"
  → 1 config-changed hook fired
  → no spurious restart (config is invalid so charm refuses to apply)
juju config charmed-etcd heartbeat-interval=100  # revert

# Test status-detail action
juju run charmed-etcd/0 status-detail recompute=true
  → shows all 6 component statuses (upgrades, cluster, config, tls, external_clients, backup)
  → all "Active" ✓

# Charm resource use
  Memory: 148Mi used (etcd process ~38MB RSS)
  Quota backend: auto-set to 30.3GB (0.9 × 31GB memory)
  LXD dir storage warning: correctly logged in debug-log
```

Model `rv-etcd-test` was destroyed after the review.

## Observed behaviour

- **Install time**: ~90s for snap install on a fresh LXD container (includes snap download).
- **Hook sequence on fresh deploy**: `install` → `data-storage-attached` (×3) → `restart-relation-created` → `etcd-peers-relation-created` → `status-peers-relation-created` → `refresh-v-three-relation-created` → `leader-elected` → `config-changed` → `start` → `etcd-peers-relation-changed` → `refresh-v-three-relation-changed`.
- **Config-changed hook**: Fires once per `juju config` call. Triggers a rolling restart only when tuning parameters are valid and actually changed. Invalid config is rejected with `BlockedStatus` — no restart is issued.
- **TLS enable flow**: `relation-created` → `relation-joined` → sets `TO_TLS` state → `relation-changed` → rolling restart → `relation-changed` again → TLS cert written → `restart-relation-changed` → health check. Correctly avoids restarting peer TLS before client TLS when both are transitioning simultaneously.
- **`_restart_enable_peer_tls` vs `_restart_enable_client_tls` ordering**: When both peer and client TLS are being enabled (different relations), peer TLS is enabled first, then client TLS on the second restart — correct, because peer URL broadcast needs peer TLS active first.
- **Quota auto-size**: The `quota-backend-bytes: auto` formula (`min(100GiB, 0.9×memory, 0.9×data_storage_size)`) correctly used 90% of the 31 GiB available memory → 30.3 GB. The LXD dir-storage driver warning is correctly emitted.
- **Secrets**: The root password is stored in a Juju secret (`08udtdpoc9tr7ekc759g`, label `etcd-peers.charmed-etcd.app`). The secret ID is not stored in peer relation data — it stays in the Juju secrets store.
- **Pre-refresh-check action**: Runs without arguments and returns check results.
- **Status precedence**: Uses `data_platform_helpers.advanced_statuses.handler.StatusHandler` with explicit priority ordering (upgrades > cluster > config > tls > external_clients > backup). The `CharmStatuses` enum uses `StatusObject` from the data-platform-helpers library, not ops built-in statuses.

## Findings

### 1. etcdctl/etcdutl subprocess timeout is too short for some operations
- **Severity**: high
- **Kind**: bug
- **Where**: `src/common/client.py:271` and `src/common/client.py:323`
- **Evidence**: `subprocess.run(... timeout=10)` on every etcdctl and etcdutl call. The `promote_member` operation (learning member promotion) can take 30–120 seconds on a large cluster; `member remove` can also be slow. A 10-second timeout causes spurious `None` returns and retry-at-most-once behaviour for any slow operation.
- **Impact**: When promoting a new learning member to full voting member, a slow cluster (network latency, large snapshot transfer) can cause `promote_member()` to return `None` after 10s, triggering `EtcdClusterManagementError` and leaving the member in an inconsistent `learning_member` state in the peer databag.
- **Fix**: Increase the default timeout to 60 seconds for all calls, or make the timeout per-operation. Use `tenacity` for retry on timeout, matching the pattern already used in `is_healthy()`.
- **Linter rule**: "subprocess.run with timeout < 30 in charm code should be checked; commands that mutate cluster state should have timeout ≥ 60". Not mechanically checkable without knowing operation semantics.

### 2. `_exists_preventing_reason` returns `bool` but callers treat it as `str`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/events/external_clients.py:79` and `src/events/external_clients.py:149`
- **Evidence**: The method is typed `-> bool` and returns `True`/`False`. But `_on_bulk_resources_requested` calls `self._exists_preventing_reason()` and treats the result in a boolean context (`if preventing_reason or not self.charm.unit.is_leader()`) — works today by coincidence (non-empty string is truthy, `False` is falsy), but is semantically wrong. The name also suggests a string return, matching the pattern of its sibling `_check_rebuild_preventing_reason`.
- **Impact**: If the method is later extended to return descriptive strings (as its sibling does), the `if preventing_reason` pattern breaks silently. The type mismatch is a maintenance hazard.
- **Fix**: Rename to `has_preventing_reason() -> bool` and update the one call site, or change the return type to `str` to match the sibling pattern.
- **Linter rule**: not established (not mechanically checkable).

### 3. `quota-backend-bytes` invalid-value error is too generic to act on
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/managers/config.py:220` and `src/managers/config.py:228`
- **Evidence**: `_is_backend_quota_valid` checks `quota_backend_bytes < db_file_size` and `quota_backend_bytes < MIN_QUOTA_BACKEND_BYTES`. If `quota-backend-bytes=abc` is set, the charm logs `"Quota backend bytes value 'abc' is invalid. It must be an integer or 'auto'."` from the `quota_backend_bytes` property and a similar message from `_is_backend_quota_valid`, but the `BlockedStatus` shown in `juju status` is the generic `"Invalid value(s) set on the tuning config option(s), see debug-log for details"`.
- **Impact**: A user running `juju status` cannot tell which specific tuning option is invalid without checking `juju debug-log`.
- **Fix**: Pass the actual invalid option name through to the `ConfigStatuses.TUNING_CONFIG_INVALID` status message, e.g. `"Invalid tuning config option(s): quota-backend-bytes, see debug-log for details"`.
- **Linter rule**: not established (not mechanically checkable).

### 4. Deprecated TLS library calls will break in future charmlibs versions
- **Severity**: medium
- **Kind**: lint
- **Where**: `deps/charmlibs/interfaces/tls_certificates/_tls_certificates.py` (shipped as `charmlibs-interfaces-tls-certificates` PyPI package)
- **Evidence**: The charm imports `charmlibs.interfaces.tls_certificates`, which internally uses deprecated methods: `generate_private_key()` (use `PrivateKey.generate()`), `generate_ca()` (use `Certificate.generate_self_signed_ca()`), `generate_csr()` (use `CertificateRequestAttributes.generate_csr()` or `CertificateSigningRequest.generate()`), and `generate_certificate()` (use `Certificate.generate()`). These raise `DeprecationWarning` at runtime; the charm's test output shows 132 total deprecation warnings from this source.
- **Impact**: When `charmlibs-interfaces-tls-certificates` removes these methods, the charm will break at the next dependency bump.
- **Fix**: Pin `charmlibs-interfaces-tls-certificates` to a version range that supports the current API; monitor for deprecation removals and update before a breaking release is pulled in.
- **Linter rule**: "charm uses deprecated library API — pin to stable version range". Not mechanically checkable without version metadata.

### 5. Unit test failures from ops-scenario API incompatibility
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py`, `tests/unit/test_upgrades.py`, `tests/unit/test_backup.py`
- **Evidence**: In this environment, unit tests showed 6 failed / 13 passed (charm tests), 1 failed / 11 passed (TLS tests), and 13 failed / 45 passed (backup/upgrade/external-client tests) — 20 failures, 69 passes, out of 89 tests total. Failures are `scenario.errors.InconsistentScenarioError` or `AttributeError: 'str' object has no attribute 'items'` on `ops.testing.Secret(remote_grants=APP_NAME)`. Root cause: installed `ops-scenario 8.8.0` expects `remote_grants: dict[int, set[str]]` but the tests pass a bare string. The exact ops-scenario version pinned by the project's own poetry resolution was not established in this review.
- **Impact**: The unit test suite is broken in this environment; developers cannot run unit tests locally without matching the exact dependency resolution used upstream.
- **Fix**: Update test code to the current `ops-scenario` API, or pin `ops-scenario` to a compatible version in `pyproject.toml`. Add a CI job that verifies the test suite runs in an isolated environment.
- **Linter rule**: not established (not mechanically checkable).

### 6. `SNAP_USER` and `SNAP_GROUP` are hardcoded numeric/literal values
- **Severity**: low
- **Kind**: lint
- **Where**: `src/literals.py:16-17`
- **Evidence**: `SNAP_USER = 584788` (UID of `snap_daemon`), `SNAP_GROUP = "root"`. If Canonical ever changes the snap daemon user's UID, file ownership would be set incorrectly.
- **Impact**: Unlikely to change for a published snap, but hardcoding UIDs is fragile.
- **Fix**: Query the UID/GID at runtime via `pwd.getpwnam("snap_daemon")` / `grp.getgrnam("root")`, or use the snap library's API to get the daemon user info.
- **Linter rule**: "UID/GID of system users should not be hardcoded as literals". Not mechanically checkable without semantic knowledge of what the numbers represent.

### 7. `config_properties` can leave `http://` in `initial-cluster` during TLS transition
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/config.py:68`
- **Evidence**: `initial-cluster` is built from `self.state.cluster.model.cluster_members`, which stores `http://` URLs set when the member was originally added. When TLS is enabled, `listen-peer-urls` and `initial-advertise-peer-urls` are rewritten to `https://`, but `initial-cluster` is not — `broadcast_peer_url` (in `_restart_enable_peer_tls`) updates it only after the restart.
- **Impact**: In a multi-unit cluster enabling TLS, the restarting unit could attempt to contact existing members using stale `http://` URLs before `broadcast_peer_url` completes. Single-unit deployments are unaffected.
- **Fix**: In `_restart_enable_peer_tls`, update `initial-cluster` to `https://` before writing the config and restarting.
- **Linter rule**: not established (not mechanically checkable).

### 8. `is_reachable` retries without first checking if etcd is alive
- **Severity**: low
- **Kind**: performance
- **Where**: `src/workload.py:64-76`
- **Evidence**: `is_reachable` loops 5 times with 3-second waits using a socket connect, without checking `self.alive()` first. If the etcd service is stopped, it retries for 5×3s = 15 seconds before returning `False`. `start_member()` calls `is_reachable` before considering the service started.
- **Impact**: Adds up to 15 seconds of unnecessary delay to `start_member()` when etcd is slow to start or not running.
- **Fix**: Check `self.alive()` first and return `False` immediately if the service is not running.
- **Linter rule**: not established (not mechanically checkable).

## Worth copying

- **Advanced status handler with priority ordering**: `StatusHandler` from `data_platform_helpers.advanced_statuses` gives fine-grained control over status precedence across multiple components — 6 manager objects in priority order, each computing its own statuses. One of the cleanest status-management patterns seen in charms.
- **Multi-step coordinated workflows via peer relation state machine** (`src/events/backup.py`, `_on_peer_relation_changed`): the restore workflow is a state machine driven by a `RestoreStep` enum — the leader advances steps in `proceed_restore_workflow_if_possible` and workers follow via `match`/`case`. A solid pattern for multi-unit coordinated operations.
- **TLS state machine** (`src/literals.py` `TLSState` enum, `src/managers/tls.py`): the four-state TLS model (`NO_TLS → TO_TLS → TLS → TO_NO_TLS → NO_TLS`) cleanly handles enable, disable, and rotation transitions.
- **Graceful failure in `_check_rebuild_preventing_reason`** (`src/events/etcd.py`): returns descriptive error strings, not booleans, letting callers use `event.fail(error)` directly — the right pattern for action handlers.
- **Verification step before destructive restore** (`src/events/backup.py`, `_verify_restore`): the restore workflow verifies the backup can be restored on one node before wiping all nodes.
- **Pre-flight checks in refresh** (`src/events/refresh.py`, `run_pre_refresh_checks_after_1_unit_refreshed`): checks backup, restore, rebuild, TLS states, and cluster health before allowing the next unit to refresh.
- **Config template separation** (`src/managers/config/etcd.conf.yml`): the etcd config template is loaded fresh and merged with live values on each write, avoiding config drift between disk state and charm state.

## Common-practice notes

**Drifts from ecosystem convention:**
- The `src/` layout with `core/`, `events/`, `managers/`, `common/` subdirectories is more granular than the common `src/charm.py`-only approach, but follows a clear domain-driven pattern worth adopting.
- Status values use `StatusObject` from `data_platform_helpers.advanced_statuses` instead of `ops.Status` — a newer pattern better suited to multi-component charms.
- Uses `dpcharmlibs.interfaces` (the `pathops` library) for peer relation data access, Canonical's emerging pattern replacing direct `relation.data` access.
- `src/workload.py` appears to be a stub/alias into the concrete VM implementation.

**Follows ecosystem convention:**
- `lib/charms/` vendored charm libraries with explicit versioned paths.
- `charmcraft.yaml` with `type: charm` and `platforms:` syntax.
- `tox.ini` with `format`, `lint`, `unit`, `integration` environments.
- Spread tests on LXD VMs with `concierge.yaml` for local CI.
- `CONTRIBUTING.md`, `SECURITY.md` present.
- Terraform module under `terraform/charm/` and `terraform/product/`.

## Tests

**Unit tests** (`tests/unit/`): 6 modules covering charm lifecycle, TLS, backup, external client relations, and upgrades — 89 tests observed, 69 passing, 20 failing in this environment. All observed failures trace to `ops-scenario 8.8.0` API changes (`remote_grants` format changed from a string to `dict[int, set[str]]`, and `relation_changed` events now require a `remote_unit`) — see Finding 5. These appear to be test-infrastructure/dependency-pinning issues, not code bugs.

**Integration tests** (`tests/integration/`): extensive coverage of:
- HA: failover, rolling restart, network cuts, storage reuse, scaling
- TLS: CA rotation, private key rotation, Vault intermediate CA
- Backup: S3 backup/restore, restore verification failure
- Upgrades: stable release upgrades, edge cases, cluster size changes
- Client relations: v0 and v1 data interfaces, cross-model

**Spread tests** (`tests/spread/`): one `.yaml` per scenario for LXD VM testing.

**Test gaps**: `test_enabling_tls_one_restart` correctly tests that enabling both peer and client TLS triggers only one restart, but the equivalent for *disabling* both simultaneously is not tested. `test_ca_rotation` tests rotation when all units are healthy, but not when a unit is in `TO_TLS` state during CA rotation (the code path exists but is untested).

## Docs

**`README.md`**: clear basic usage and cluster-scaling instructions, points to full documentation.

**`docs/`**: Sphinx documentation covering tutorial (first deployment, basic operations), how-to guides (client relations, disaster recovery, monitoring/COS, password management, storage, refresh, scaling, tuning), and an explanation of advanced statuses.

**`docs/how-to/enable-monitoring.md`**: 16KB covering COS integration, alert rules, and dashboards — the most detailed doc.

**`docs/how-to/disaster-recovery.md`**: explains the rebuild-cluster workflow and majority-failure recovery.

**`docs/how-to/tune-settings.md`**: documents the `quota-backend-bytes: auto` formula and the LXD dir-storage warning.

**Doc/reality gaps found during deployment**:
- `juju debug-log` showed `Quota backend bytes reduced to 30278264832 to fit available memory`, but the docs cite a community-recommended maximum of 8 GiB. The auto-formula ignores that recommendation and uses 0.9×memory instead — undocumented.
- The docs do not mention that `quota-backend-bytes: auto` uses 90% of available memory rather than 90% of storage size on the LXD dir driver.

## Open questions

1. What is the expected behaviour when the TLS provider relation is broken while TLS is active? The charm sets `TO_NO_TLS` state and initiates a rolling restart, but external clients that were issued credentials would lose access, and this scenario isn't covered in the disaster-recovery docs.
2. How should `quota-backend-bytes` auto-sizing behave on a system with >111GB RAM (where the 100GiB hard cap kicks in), given that the 8 GiB community recommendation is ignored entirely by the auto-formula — is that intentional?
3. Open issue #237 (gRPC-gateway auth path for Patroni/Charmed PostgreSQL): the current `etcd-client` interface only supports mTLS authentication via CN. Gateway-only clients cannot authenticate; this is a known limitation not addressed in the current implementation.
