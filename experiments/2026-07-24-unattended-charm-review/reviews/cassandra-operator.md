# cassandra-operator

A machine-substrate charm for Apache Cassandra 5.x, deployed as a snap (`charmed-cassandra`) on Ubuntu. Provides multi-node clustering, TLS, medusa backup/restore to S3/GCS/Azure, COS observability, and a `cassandra-client` data-provider interface. Uses `charm_refresh` for rolling snap upgrades.

**Verdict**: Well-structured code (clean events/managers/core separation, typed Pydantic config, a readable reconciler pattern) but not safe to run unattended yet. Three high-severity bugs land on the most common operational paths: removing the application without `--force` breaks (bug #47, confirmed), a restore failure is silently swallowed with no status change, and a dead Cassandra process is invisible in `juju status` for up to 5 minutes. The install hook also crashes on first attempt due to a snap-catalog race, though it self-heals on retry. A maintainer should fix the `storage-detaching` guard and the restore/liveness status reporting before this charm goes near production; the rest is polish.

| | |
|---|---|
| Repo | canonical/cassandra-operator @ 3d03a6e (2026-07-16) |
| Charms | `cassandra` (machine), `application` (integration test dummy) |
| Substrate | machine (LXD) |
| Deployed | yes — `concierge-lxd-4`, charmhub 5/edge rev 82 (local HEAD: 3d03a6e) |
| Reviewed | 2026-08-18 |

## What it does

Deploys a Cassandra 5.0.5 node as a snap with:
- Automatic cluster bootstrapping (leader first, then subordinates)
- Internal TLS via self-signed CA + external TLS via `tls-certificates` interface
- Juju secrets for operator/nodetool password management
- Cassandra user provisioning via `cassandra-client` data-provider interface
- medusa backup/restore to S3/GCS/Azure
- COS metrics via JMX exporter on port 7071 + Grafana Agent integration
- Rolling snap refresh with health checks and pause-after-refresh

## Deployment log

**Test 1: single-node, rev 82 from charmhub**

1. `juju add-model rv-cassandra-deep --controller concierge-lxd-4`
2. `juju deploy cassandra --channel 5/edge --config profile=testing -n 1`
   - Machine provisioned in ~30s, Cassandra version 5.0.5 detected
   - Install hook ran twice: first attempt failed with `SnapNotFoundError: Snap 'charmed-cassandra' not found!` (HTTP 500 from snapd); second attempt succeeded
   - Install time: ~6 min from deploy to active (snap install ~3 min + medusa pip install ~2 min + bootstrap ~1 min)
3. `juju config profile=production` → config-changed → bootstrap-relation-changed → Cassandra restart, recovered in ~15s
4. `juju config profile=invalid_profile` → unit entered `blocked` with message `invalid config`, Pydantic validation error logged at ERROR level. Restored to `testing` → active in ~30s
5. `juju remove-application cassandra` (no `--force`) → unit entered `error` state with `hook failed: "storage-detaching"` — bug #47 confirmed
6. Force-removed and redeployed

**Test 2: 3-node cluster, rev 82 from charmhub**

1. Same deploy, then `juju add-unit cassandra -n 2`
2. Machines provisioned and Cassandra installed on all 3 units (~5 min for units 1+2)
3. Cluster bootstrapped: unit 0 became leader → unit 1+2 joined as subordinates → auth repair on all units
4. All 3 units reached `active` within ~15 min
5. `juju remove-application cassandra` (no `--force`) on 3-node cluster:
   - Units 0+1: decommissioned successfully, machines stopped, units removed
   - Unit 2: `storage-detaching` hook failed with `ExecError` from `nodetool decommission -f` (Cassandra already stopped because the LXD container was halted before the hook could complete). Unit 2 entered `error` state
6. `juju remove-application cassandra --force` resolved the stuck unit

**Test 3: workload kill (single unit)**

1. `juju exec --unit cassandra/0 -- snap stop charmed-cassandra.daemon` → Cassandra stopped
2. Unit showed `active` in `juju status` for 5+ minutes (until `update_status` fired and the charm detected the failure and restarted Cassandra)
3. Cassandra auto-restarted and unit returned to `active`

**Test 4: TLS integration with self-signed-certificates (3-node)**

1. `juju deploy self-signed-certificates --channel beta`
2. `juju integrate cassandra:client-certificates self-signed-certificates`
3. On adding the relation: cassandra units briefly went `maintenance/waiting for TLS setup` → recovered to `active` within ~15s once certs were issued
4. On removing the relation: unit 0 went `maintenance/waiting for Cassandra to start` (transient, recovered in ~15s)
5. On re-adding the relation: all units transitioned correctly, subordinate units logged repeated keytool ERRORs (see keytool finding)
6. Units 0, 1, 2 all reached `active` with TLS configured

**Test 5: all actions**

- `create-backup`: failed with actionable message "Check if storage relation is in active|idle state, and if the charm is integrated properly with the object storage integrator." ✓
- `list-backups`: same failure with same message ✓
- `pre-refresh-check`: succeeded with readiness message and rollback instructions ✓
- `force-refresh-start`: failed with "No refresh in progress" ✓
- `restore`: same failure as create-backup ✓
- `resume-refresh`: failed with "No refresh in progress" ✓

## Observed behaviour

### Hook sequence for a config change
`config-changed` → `bootstrap-relation-changed` (fires twice) → Cassandra restarts and recovers.

### Install hook fails on first attempt (snap timing)
The first run of the `install` hook on a fresh machine fails with `SnapNotFoundError: Snap 'charmed-cassandra' not found!`. The machine then refreshes its snap catalog, and the second attempt succeeds.

Root cause: `CassandraWorkload.__init__` calls `snap.SnapCache()[SNAP_NAME]`, which queries snapd via HTTP. If the snap is not yet in the local catalog (HTTP 500), the exception propagates to `CassandraCharm.__init__`, crashing the unit agent. Not caught anywhere in the code.

### Cassandra kill is not detected until update_status fires (5 min lag)
When Cassandra is stopped (`snap stop`), `juju status` still shows `active` for the unit. `_on_collect_unit_status` derives status from the `workload_state` field stored in the peer relation databag, which is only refreshed when `_on_update_status` fires (every 5 minutes) and checks `self.workload.is_alive`. During the lag, the operator sees an incorrect status.

### Repeated keytool ERROR logs on subordinate units (TLS setup)
On a 3-node cluster, units 1 and 2 logged 8+ ERROR messages for `keytool -import` failures per unit in ~10 seconds, across `refresh-v-three:2`, `cassandra-peers:1`, and plain `workload` hooks. `set_truststore()` calls `charmed-cassandra.keytool -import` to import `peer-bundle0.pem` and `peer-bundle1.pem` into `peer-truststore.jks`; exit code 1, no stdout. Despite the errors the units eventually reach `active` because later hook invocations succeed (truststore files confirmed to exist on all units afterward). The same failure also fires on `client-certificates:4` (external TLS hook), where the keytool import used `peer-bundle0.pem` (the internal CA chain) rather than the external/client bundle — root cause not confirmed, flagged as an open question.

Likely root cause: a race where `cassandra-peers-relation-changed` fires on a subordinate before the leader has finished writing the TLS bundle files, so the import fails and the hook retries until it succeeds.

### Logged errors during normal operation
```
ERROR unit.cassandra/0.juju-log core.state:Field `keystore-password-secret` were attempted to be written on the relation before it exists.
ERROR unit.cassandra/0.juju-log core.state:Field `truststore-password-secret` were attempted to be written on the relation before it exists.
```
These fire during the install hook from `TLSEvents._init_credentials()` before the peer relation exists. Harmless but noisy.

## Findings

### storage-detaching hook fails when removing single-unit app (bug #47 — confirmed present)
- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/cassandra.py:574` (`_on_storage_detaching`), `is_healthy` check at line 461/579
- **Evidence**: `juju remove-application` without `--force` on a 1-unit cluster leaves the unit in `error` with `hook failed: "storage-detaching"`. On a 3-node cluster the same failure hits the last remaining unit after earlier units decommission cleanly. The `is_healthy` check fails because the peer relation has been torn down while the unit is still mid-hook. Reproduced on rev 82; matches open issue #47 (2026-02-16).
- **Impact**: `juju remove-application` without `--force` is the default operator action. It cannot cleanly remove this charm — operators are forced to use `--force` or manually resolve stuck units.
- **Fix**: Guard for `planned_units() == 0` at the top of `_on_storage_detaching`; when the application is being destroyed, skip the `is_healthy` check and go straight to decommissioning.
- **Linter rule**: not mechanically checkable — needs an integration test asserting `juju remove-application` on a 1-unit cluster without `--force` does not leave a unit in error.

### Install hook crashes unit agent on first attempt (snap catalog timing)
- **Severity**: high
- **Kind**: bug
- **Where**: `src/workload.py:51` (`CassandraWorkload.__init__`)
- **Evidence**: First run of `install` on a fresh machine fails with `SnapNotFoundError: Snap 'charmed-cassandra' not found!` (HTTP 500 from snapd); the second attempt succeeds after the snap catalog refreshes.
- **Impact**: The unit agent crashes during initialization because `snap.SnapCache()[SNAP_NAME]` is called before the snap is installed. It self-heals on retry, but produces spurious ERRORs and delays initial deployment.
- **Fix**: Catch `SnapNotFoundError` in `CassandraWorkload.__init__`, store `None`, and lazily create the snap cache on first access in `install()`.
- **Linter rule**: not mechanically checkable.

### Restore failure is silently swallowed by unconditional finally block
- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/backup.py:185` (`_on_restore_event`), `finally` block lines 190-191
- **Evidence**:
```python
try:
    self.backup_manager.restore(backup_name=event.backup_name)
except ExecError as e:
    logger.error(f"Restore process failed: {e.stdout} {e.stderr}")
finally:
    self.state.unit.restoring = False          # always runs
    self.state.unit.restore_backup_name = ""
```
If `restore()` raises `ExecError`, the error is logged but the unit immediately exits the `RESTORING` state and loses `restore_backup_name`. No `BlockedStatus` is set.
- **Impact**: `juju status` shows `active` while the restore actually failed; the only trace is in `debug-log`.
- **Fix**: Move the `restoring = False` reset into the success path of `try`, or set `workload_state = CANT_START` in the `except` block.
- **Linter rule**: "finally block must not unconditionally reset transient state that could indicate failure".

### Cassandra kill not detected until update_status fires (5 min lag)
- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/cassandra.py:413` (`_on_update_status`), `src/events/cassandra.py:448` (`_on_collect_unit_status`)
- **Evidence**: After `snap stop charmed-cassandra.daemon`, `juju status` continued to show `active` for over 5 minutes. `_on_collect_unit_status` derives status from the `workload_state` field in the peer databag, which is only updated when `_on_update_status` fires and checks `self.workload.is_alive`.
- **Impact**: Operators watching `juju status` see `active` for a dead Cassandra node, which is dangerous during the lag window (potential undetected data inconsistency).
- **Fix**: Have `_on_collect_unit_status` check `self.workload.is_alive` directly (or via a short TTL cache) instead of relying solely on stored state.
- **Linter rule**: "status collection handler must not rely solely on stored state for liveness; must check actual workload state".

### Transient keytool failures during multi-node TLS setup (race condition)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/tls.py:251` (`set_truststore`)
- **Evidence**: On a 3-node cluster with TLS, subordinate units logged 8+ ERROR messages for `charmed-cassandra.keytool -import` failures (exit code 1, no stdout) in ~10 seconds during setup, repeating across `refresh-v-three:2`, `cassandra-peers:1`, and plain `workload` hooks. Units eventually reached `active` (truststore files confirmed to exist afterward). The `client-certificates:4` hook was also observed importing `peer-bundle0.pem` (internal CA) rather than the client bundle.
- **Impact**: Each failed keytool call risks an `ExecError` propagating and failing the hook; the repeated invocations also slow setup. The client-certificates bundle mismatch is suspicious and unexplained (unverified — root cause not confirmed).
- **Fix**: (a) Guard `set_truststore` with try/except, log at WARNING not ERROR, continue gracefully. (b) Investigate why `client-certificates` imports `peer-bundle0.pem`. (c) Check bundle files exist before invoking keytool.
- **Linter rule**: not mechanically checkable.

### charmcraft.yaml declares data_interfaces v0 but code also uses v1
- **Severity**: high
- **Kind**: bug
- **Where**: `charmcraft.yaml`, `src/core/state.py:18`, `src/events/provider.py:11`
- **Evidence**: `src/events/provider.py:11` imports `DataContractV1`/`ResourceProviderModel` from `charms.data_platform_libs.v1.data_interfaces`; `src/core/state.py:18` uses `RepositoryInterface`, `OpsRelationRepository`, `RequirerCommonModel` from v1. `charmcraft.yaml` declares `data_platform_libs.data_interfaces` version "0" only.
- **Impact**: The charm pulls in both v0 and v1 of the same library — fragile, risks symbol conflicts. Not observed to cause problems in the deployed charm, but a latent risk.
- **Fix**: Declare `data_platform_libs.data_interfaces` version "1" in `charmcraft.yaml`, and update `metadata.yaml` charm-libs accordingly.
- **Linter rule**: `charmcraft check` catches version mismatches between charmcraft.yaml and the actual imported library version.

### Integration test for backup/restore does not assert failure modes
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/backup.py`
- **Evidence**: `test_run_actions_before_storage_integration_fails` only asserts that `create-backup`/`list-backups` fail when storage is not integrated. No test covers medusa not installed, wrong credentials, network unreachable, or restore failing mid-operation.
- **Fix**: Add integration tests for each failure mode, asserting the error message is actionable and the unit ends up in a sensible (not falsely-`active`) status.
- **Linter rule**: not applicable.

### Unit tests fail with the wrong ops-scenario version (77 passed, 6 failed once run in a matching venv)
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py`, `tests/unit/helpers.py`
- **Evidence**: The system `ops` (3.6.0) and the deps' `ops` (3.8.1) don't have the right combination of `Harness`/`Context`/scenario secrets support; running under a Python 3.12 venv with ops 3.8.1 + ops-scenario 8.6.0 gives **77 passed, 6 failed** in 10.79s. Failures:
  1. `test_pre_refresh_checks` (3×): `InconsistentScenarioError: 'cassandra_peers_relation_changed' must provide a remote unit. Pass in remote_unit.`
  2. `test_snap_refresh` (2×): same error.
  3. `test_tls_default_certificates_files_setup`: `AssertionError: assert 'internal-ca-secret' in {}` — `get_secrets_latest_content_by_label` helper incompatible with ops-scenario 8.x secrets API.
- **Impact**: Real test code needs updating for ops-scenario 8.x; tests are also not runnable without a bespoke PYTHONPATH (`deps/charmlibs` prepended, `charmlibs` pip package uninstalled).
- **Fix**: Pass `remote_unit=peer_relation.units[0]` to `testing.PeerRelation` scenarios; update the secrets helper for the ops-scenario 8.x API; document the PYTHONPATH setup in `tox`/a `justfile`.
- **Linter rule**: not applicable.

### `_on_resource_entity_permissions_changed` can let ValueError propagate on invalid permissions
- **Severity**: low
- **Kind**: bug
- **Where**: `src/events/provider.py:169` (`_on_resource_entity_requested`/`_on_resource_entity_permissions_changed`)
- **Evidence**: `_validate_entity_permissions` calls `Permissions(*perm.privileges)`, which raises `ValueError` on invalid privileges. This call is not wrapped in try/except in the handler, so a client sending invalid privileges can fail the hook with an unhandled exception rather than a graceful rejection.
- **Impact**: A malformed client request could fail the hook instead of being rejected cleanly.
- **Fix**: Wrap the validation call in try/except, log the invalid permissions, and skip/report them rather than letting the exception propagate.
- **Linter rule**: "event handler must not let ValueError from permission validation propagate".

### TLS init_credentials logs ERROR before peer relation exists
- **Severity**: low
- **Kind**: ux
- **Where**: `src/events/tls.py:259` (`_init_credentials`)
- **Evidence**: During install, `TLSEvents.__init__` calls `_init_credentials()`, which tries to write `keystore-password-secret`/`truststore-password-secret` to the peer relation databag before the peer relation exists, producing `ERROR: Field ... were attempted to be written on the relation before it exists.` on every unit's first install.
- **Impact**: Noisy ERROR-level logs on every install that could alarm operators monitoring logs, with no actual failure.
- **Fix**: Check `self.state.peer_relation is not None` before writing credentials in `_init_credentials`.
- **Linter rule**: "hook handler must not write to relation data before the relation is created" — not mechanically checkable.

### metadata.yaml charm-libs omits data_platform_libs v1 (code uses both v0 and v1)
- **Severity**: low
- **Kind**: docs
- **Where**: `metadata.yaml:20`, `charmcraft.yaml`
- **Evidence**: Code imports both `charms.data_platform_libs.v0.data_interfaces` (`Data`, `DataPeerData`, etc.) in `src/core/state.py` and `charms.data_platform_libs.v1.data_interfaces` (`OpsRelationRepository`, `RepositoryInterface`, `RequirerCommonModel`) in `src/events/provider.py`. `metadata.yaml` charm-libs only declares version "0".
- **Impact**: Misleading metadata about which library versions the charm depends on; tooling relying on the declaration won't know about v1.
- **Fix**: Add `data_platform_libs.data_interfaces` version "1" to `metadata.yaml` and `charmcraft.yaml` charm-libs sections.
- **Linter rule**: not mechanically checkable.

### Unnecessary Cassandra restart on unchanged profile config
- **Severity**: nit
- **Kind**: performance
- **Where**: `src/events/cassandra.py:280` (`_on_config_changed`), `render_env` at line 301
- **Evidence**: A profile config change triggers `render_env`, which returns `True` unconditionally because the environment file is rewritten before any content comparison happens, causing a restart even when the profile value is unchanged (unverified — draft asserts this from code reading, not from an observed no-op restart in the deployment log).
- **Impact**: Adds ~30–60s to config changes that don't actually change the rendered environment.
- **Fix**: Move the content comparison in `render_env` before the write, or return early when unchanged.
- **Linter rule**: not mechanically checkable.

### Typo: "proivded" in error message
- **Severity**: low
- **Kind**: lint
- **Where**: `src/events/backup.py:196` (draft text) / notes cite line 55 for the same string — location not fully reconciled, treat as `src/events/backup.py`
- **Evidence**: `BackupMessages.NOT_READY` contains the typo `"proivded"`.
- **Fix**: `s/proivded/provided/`
- **Linter rule**: `codespell` catches this automatically.

### Copyright year 2026 in backup.py
- **Severity**: low
- **Kind**: lint
- **Where**: `src/events/backup.py:1`
- **Evidence**: All other source files say `# Copyright 2025 Canonical Ltd.`; `src/events/backup.py` says `# Copyright 2026 Canonical Ltd.`.
- **Fix**: Normalize to 2025.
- **Linter rule**: not mechanically checkable.

## Worth copying

1. **Clean reconciler pattern** (`src/charm.py:140`): `CassandraCharm.reconcilers = [self.cassandra_events, self.backup]` + `CassandraEvents.reconcile()` / `BackupEvents.reconcile()`, each reconciler owning its own state and called unconditionally from `_on_collect_unit_status`.
2. **TypedCharmBase with Pydantic config** (`src/core/config.py`): `CharmConfig` as a `BaseConfigModel` gives automatic validation, type coercion, structured error messages for invalid config.
3. **State dataclasses** (`src/core/state.py`): `ApplicationState` → `ClusterContext`/`UnitContext`/`TLSContext` cleanly separates peer, TLS, topology, and storage state.
4. **Lock-based exclusive bootstrap** (`src/common/lock_manager.py`): `LockManager`/`Lock`/`Locks` implement a distributed exclusive lock across units without a separate locking service.
5. **Structured status precedence** (`src/core/statuses.py`): a readable, auditable enum of `Status` values used consistently through `_on_collect_unit_status`.
6. **medusa backup abstraction** (`src/managers/backup.py`): `BackupManager` + `MedusaConfig` cleanly separate medusa CLI invocation from charm logic.
7. **Scaling integration test** (`tests/integration/test_scaling.py`): `test_single_node_scale_down` removes non-leader then leader from a 3-node cluster and asserts continuous writes survive.
8. **Kill/restart integration test suite** (`tests/integration/test_restart.py`): SIGKILL, SIGSTOP/SIGCONT, graceful nodetool drain restart, and full LXC restart, all with continuous write verification.
9. **`conftest.py` refresh mock** (`tests/unit/conftest.py`): `mock_refresh` and `mock_ssh_manager` fixtures avoid needing real snap/cassandra dependencies in unit tests.

## Common-practice notes

**Follows convention:**
- `src/` layout with `events/`/`managers/` subdirectories
- `ops.framework.EventSource` for custom events
- Pydantic for config validation, Juju secrets for passwords
- `charmcraft.yaml` parts for poetry-based build
- `tox` for per-subsystem test environments; `ruff` for linting, `codespell` for spell check
- `spread.yaml` for multi-backend integration tests (LXD + GitHub Actions)
- Semantic versioning via git tags (track 5, managed by data-platform-workflows)
- `ops.testing.Context` (scenario-style) for unit tests rather than the older `Harness`

**Drifts from or leads convention:**
- Uses `charm_refresh` (less common than `rolling_ops`, appropriate for snap-based charms)
- Ships `tests/integration/application-charm/` as a clean, self-contained integration-test charm
- `concierge.yaml` uses LXD 6/stable, ahead of many charms
- Publishes to Charmhub track `5/` instead of the default track — correct given Cassandra's major version
- Stores TLS chain certificates in relation data as JSON-serialized strings (`src/core/state.py:220`) — unusual; most charms use individual secret fields
- Ships its own copy of `data_platform_libs` v1 (`lib/charms/data_platform_libs/v1/`) as a single-file library rather than fetching via charmcraft charm-libs — fine for self-contained distribution but tightly couples the library version to the charm version

## Tests

**Unit tests** (`tests/unit/`, 14 files, 83 collected — **77 passed, 6 failed** in 10.79s under a matching venv):
- Run command: `PYTHONPATH="src:lib:tests/integration/application-charm/lib:deps/charmlibs" venv/bin/python -m pytest tests/unit/ -v` — requires a Python 3.12 venv with ops 3.8.1 + ops-scenario 8.6.0 + all deps, `deps/charmlibs` prepended to PYTHONPATH (system `charmlibs` lacks `pathops`), and the `charmlibs` pip package uninstalled from the venv to avoid an import conflict.
- Coverage: start/config-changed (`test_charm.py`), storage-detaching (`test_scale.py`), data interface events (`test_provider.py`), TLS events (`test_tls.py`), snap refresh (`test_refresh.py`), backup/restore (`test_backup.py`, `test_backup_manager.py`), node manager (`test_node_manager.py`), workload (`test_workload.py`), config (`test_config.py`), TLS manager (`test_tls_manager.py`), authentication (`test_authentication.py`)
- 6 failures are all ops-scenario 8.6.0 API mismatches (see test-gap finding above), not logic bugs.
- No unit test covers the `planned_units() == 0` path in `test_scale.py` — bug #47's scenario is not covered at the unit level.
- No unit test covers the restore-failure silent-swallow path in `test_backup.py`.

**Integration tests** (`tests/integration/`, spread-based):
- Full lifecycle coverage: deploy, config, authentication, TLS, provider, COS, multinode, scaling, network, kill/restart, refresh, backup (AWS/GCS/microceph), multicluster.
- `test_scaling.py:test_single_node_scale_down` uses `juju remove-unit`, not `juju remove-application` — the bug #47 scenario (removing the last unit via `remove-application`) is not covered.
- `test_restart.py` has thorough kill/restart tests with continuous write verification.
- Backup tests assert actionable failure messages and end-to-end restore integrity.
- COS tests verify Prometheus scrape targets, Grafana dashboards, and the k8s/VM cross-model offer workflow.

**Linters**:
- `ruff`: all checks pass
- `codespell`: one typo (`proivded`, `src/events/backup.py`)
- `pyright`: only missing-import errors for `cassandra` driver and `toml` — not actionable in this environment

## Docs

**README.md** (7125 bytes): complete walkthrough — deployment, cluster management, cqlsh, password rotation via Juju secrets, TLS/COS integration. Commands accurate; `juju show-secret` password retrieval correct.

**docs/how-to/encryption.md** (4351 bytes): detailed guide for peer-TLS and client-TLS via `self-signed-certificates`, with verification steps showing expected connection errors. No discrepancies from deployed behaviour observed.

**docs/how-to/monitoring.md** (7189 bytes): JMX exporter direct access, COS Lite on k8s, cross-model relation offers, Grafana/Loki/Prometheus. Cross-model offer workflow correct.

**docs/how-to/index.md** / **docs/index.md**: clean navigation and overview.

**docs/reference/contact.md**: points to GitHub issues and Launchpad.

**CONTRIBUTING.md**: standard SDK contribution guide with tox commands; no unconventional requirements.

**`metadata.yaml` charm-libs**: declares `data_platform_libs.data_interfaces` version "0" but the code also uses version "1" (`cassandra-client` provider). See finding above.

## Open questions

1. Root cause of the transient keytool failures on subordinate units — likely a race between the leader writing TLS bundle files and the subordinate reading them, but not confirmed with `strace` or direct file inspection at failure time. Why does `client-certificates` import `peer-bundle0.pem` instead of the client bundle?
2. Is the `data_interfaces` v0/v1 mismatch in `charmcraft.yaml` causing any real problems beyond fragility? Should be pinned to v1 in both `charmcraft.yaml` and `metadata.yaml`.
3. When will the medusa deb package land (tracked in issue #70)? Current pip-based install is slow and fragile.
4. Does `_on_resource_entity_permissions_changed` handle invalid permissions gracefully? As read, `Permissions(*perm.privileges)` can raise uncaught `ValueError`.
5. Why does `SSHManager.__init__` call `keygen()` unconditionally on every restart? Minor concern, not confirmed as a problem.
