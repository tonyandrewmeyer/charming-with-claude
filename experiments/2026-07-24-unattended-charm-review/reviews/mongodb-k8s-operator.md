# mongodb-k8s-operator review

A thin Kubernetes charm wrapper (~30 lines) that delegates all business logic to the shared `mongo-charms-single-kernel` library (v1.8.52). The single-kernel pattern is well-executed and the build system is modern (charmcraft 3 + poetry), but the charm as published (rev 219, 8/edge) **fails to start MongoDB on a fresh deploy** due to incorrect `/tmp` permissions on the temp storage mount — mongod crashes with exit code 48 (matches open issue #467). A maintainer should fix `prepare_storage()`'s K8S no-op (or the rock image) first; everything else is secondary. Once worked around, the replica set forms correctly, status reporting is detailed, and the charm recovers cleanly from workload kills. A second real bug — an uncaught `ShardingMigrationError` in `on_config_changed` — turns a user config mistake into a hook failure. No unit tests exist in this repo (they live in the kernel library); integration tests are minimal (deploy + ping, plus a more substantial sharding test).

| | |
|---|---|
| Repo | `canonical/mongodb-k8s-operator` @ `a8c78d0` (2026-07-20) |
| Charms | mongodb-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (3.6.25), `ch:mongodb-k8s` 8/edge rev 219 |
| Reviewed | 2026-08-02 |

## What it does

Deploys MongoDB (Percona Server for MongoDB 8.0.10) on Kubernetes as a replica set, shard, or config-server. Supports TLS (peer + client), LDAP, backup/restore (S3 + GCS), encryption-at-rest via Vault, logs/metrics/dashboards via COS, sharding, cross-model cluster relations, charm refresh with rolling ops, and password rotation. All logic lives in the `mongo-charms-single-kernel` PyPI package; this repo is the Kubernetes packaging layer.

## Deployment log

1. `juju add-model rv-mongodb-review` on controller `concierge-k8s-3` (Juju 3.6.25).
2. `juju deploy mongodb-k8s --channel 8/edge --num-units 1 --trust` → revision 219 on ubuntu@24.04.
3. Pod `mongodb-k8s-0` stayed `PodInitializing` for ~7 minutes while pulling the 400MB+ MongoDB image from `registry.jujucharms.com`.
4. Charm reported `active` within 1 minute, while the mongod container was still pulling — the `pebble-ready` check had not actually seen a running workload.
5. Once the image pulled, pebble started mongod, which exited immediately with code 48:
   ```
   Failed to unlink socket file /tmp/mongodb-27017.sock: Permission denied
   ```
   Root cause: `/tmp` had permissions `0755` (owned by root). The `temp` storage PVC is mounted at `/tmp`, and its root directory inherits restrictive permissions.
6. After `chmod 1777 /tmp`, mongod started successfully; the charm initialised the replica set and reported `active` / `Primary.`.
7. `juju scale-application mongodb-k8s 3` — the two new units hit the same `/tmp` permission error. After `chmod 1777 /tmp` on both, all three formed a healthy replica set in ~2 minutes.
8. `juju run mongodb-k8s/leader get-primary` → correctly returned `mongodb-k8s/0`.
9. `juju run mongodb-k8s/leader status-detail recompute=true` → showed active statuses for `mongo` (Primary.) and `upgrades`.
10. `juju run mongodb-k8s/leader list-backups` → correctly failed with "Missing valid integration for backups." (no S3 relation).
11. `juju config mongodb-k8s role=shard` → all 3 units went to `error: hook failed: "config-changed"` because `ShardingMigrationError` is not caught. Reverting to `role=replication` and waiting for the rollingops restart recovered all units to active.
12. Killed mongod on unit 0 (`pkill mongod`) → pebble restarted it, unit stayed active.
13. Resource use: ~400m CPU, 200-315Mi RAM per pod.
14. `juju destroy-model rv-mongodb-review --force --no-wait --destroy-storage` — clean teardown.

## Observed behaviour

- **Deploy time**: Image pull took ~7 minutes. Charm reported `active` well before mongod was running — misleading status during image pull.
- **Exit code 48**: The `/tmp` permissions bug is deterministic — every fresh unit hits it. The charm's `prepare_storage` is a no-op on K8S (`src/charm.py` delegates to `single_kernel_mongo.managers.mongodb_operator.MongoDBOperator.prepare_storage`, which returns immediately for `Substrates.K8S`).
- **Hook count**: A trivial config change triggers ~5 hooks per unit (config-changed, rollingops-peers, status-peers). The rolling ops manager uses peer relations for synchronisation.
- **Status reporting**: The charm uses `data_platform_helpers.advanced_statuses.handler`, which emits structured JSON for app and unit scope from multiple components (mongodb-k8s, mongod, vault-kv, mongo, upgrades, tls, sharding, config-server, backup-s3, backup-gcs, ldap). This is good.
- **Recovery**: Killing mongod results in a pebble restart within seconds; unit stays active. Rolling ops handles restarts correctly.
- **Journal warning**: The config template emits `storage.journal.enabled: true`, but Percona Server for MongoDB 8.0 ignores this (journal is always enabled). Generates a startup warning on every restart — noise, not harmful.
- **Cluster ID**: Uses `shortuuid` for cluster ID generation, but only on VM substrate (`_generate_cluster_id` returns `None` for K8S). The rolling ops manager then falls back to the peer backend, logging "Etcd relation configured but no cluster_id yet. Using peer backend until cluster_id provided." on every hook — noisy.
- **Version info**: The deployed image reports `"version":"8.0.10"` and `"gitVersion":"nogitversion"`, using Percona Server for MongoDB (confirmed by Percona-specific warning messages).

## Findings

### MongoDB fails to start on fresh deploy — `/tmp` permissions cause exit code 48
- **Severity**: critical
- **Kind**: bug
- **Where**: `single_kernel_mongo/managers/mongodb_operator.py` `prepare_storage` (K8S path is a no-op); container image `/tmp` mount at the `temp` storage PVC
- **Evidence**: Every fresh unit showed `0755`/`drwxr-xr-x` on `/tmp` and mongod exited with `Failed to unlink socket file /tmp/mongodb-27017.sock: Permission denied`, followed by `Error setting up listener: /tmp/mongodb-27017.sock :: caused by :: setup bind :: caused by :: Permission denied`.
- **Impact**: The charm as published on 8/edge (rev 219) cannot form a working MongoDB deployment without manual intervention. This matches open issue #467 ("MongoDB-k8s fails to start, stuck in a crash loop of exit status 48"). An operator deploying from charmhub gets a broken deployment with no actionable error in `juju status`.
- **Fix**: In `MongoDBOperator.prepare_storage()`, add a K8S branch that calls `self.workload.exec(["chmod", "1777", "/tmp"])`. Alternatively, fix the rock image so `/tmp` has 1777 permissions at build time.
- **Linter rule**: Not mechanically checkable — a CI integration test running `kubectl exec ... stat -c %a /tmp` would catch it.

### `ShardingMigrationError` uncaught in config-changed handler causes hook failure
- **Severity**: high
- **Kind**: bug
- **Where**: `single_kernel_mongo/events/lifecycle.py` `on_config_changed` (installed library `mongo-charms-single-kernel` 1.8.52, not in this repo)
- **Evidence**: `juju config mongodb-k8s role=shard` sent all 3 units to `error: hook failed: "config-changed"` because `ShardingMigrationError("Migration of sharding components not permitted, revert config role to replication")` is raised but not caught. Caught exceptions in that handler are `UpgradeInProgressError`, `WaitingForLeaderError`, `DeferrableFailedHookChecksError`, `SetPasswordError`, `WaitingForVaultError`, `RollingOpsNoRelationError`, `PyMongoError`, `InvalidConfigRoleError`, `InvalidLdapUserToDnMappingError`, `InvalidLdapQueryTemplateError`, `NonDeferrableFailedHookChecksError`, and `WorkloadServiceError` — but not `ShardingMigrationError`.
- **Impact**: An operator changing the role gets a confusing hook failure instead of a clear `BlockedStatus`. The error message is informative but only visible in `juju debug-log`, not `juju status`. The unit goes to error state, inappropriate for a user configuration mistake.
- **Fix**: Add `except ShardingMigrationError` to `on_config_changed`, set app status to blocked with the error message, and do not defer.
- **Linter rule**: Not mechanically checkable without exception-flow analysis.

### No unit tests in this repository
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/` contains only `integration/` and `spread/`
- **Evidence**: Commit `68e41c967` ("remove UTs from charm repo") explicitly removed unit tests; `tox.ini` has no unit test environment; `src/charm.py` has no unit test coverage.
- **Impact**: `MongoDBK8sCharm` is thin but still responsible for verifying the integration between the kernel library and the K8S substrate. A new storage mount, relation, or `charmcraft.yaml` change could silently break K8S packaging without a local test catching it.
- **Fix**: Add a minimal scenario test for `MongoDBK8sCharm` verifying the substrate is `Substrates.K8S`, the peer relation is `database-peers`, and the config type is `MongoDBCharmConfig`.
- **Linter rule**: "charm has no unit tests" — mechanically checkable by absence of `tests/unit/` or a unit test tox environment.

### Integration tests only verify deploy + ping
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py`
- **Evidence**: `test_build_and_deploy` waits for active; `test_application_is_up` runs `MongoClient(...).admin.command("ping")`. No TLS test, no backup test, no LDAP test, no upgrade test, no relation test with real clients.
- **Impact**: Integration coverage is thin. The most complex features (TLS, backups, upgrades, sharding) are tested only against the kernel library, not the packaged charm.
- **Fix**: `test_sharding.py` is more substantial (config-server/shard integration); consider adding at minimum a TLS integration test and a backup test in this repo.
- **Linter rule**: Not mechanically checkable without test coverage analysis.

### Charm reports active before workload is running
- **Severity**: medium
- **Kind**: ux
- **Where**: Observed during deployment; `mongod-pebble-ready` handling path
- **Evidence**: `juju status` showed `active` 1 minute after deploy, while `kubectl get pods` showed `PodInitializing` for 7 minutes. The pebble-ready hook returned without verifying the service was actually running.
- **Impact**: Operators waiting for `active` to connect to MongoDB get connection errors — the status is misleading during initial deploy.
- **Fix**: Ensure `on_start` (triggered by pebble-ready) does not report the unit ready unless `self.workload.active()` returns `True`.
- **Linter rule**: Not mechanically checkable — requires state-machine analysis of the status reporting path.

### `storage.journal.enabled` warning on every startup
- **Severity**: low
- **Kind**: lint
- **Where**: `single_kernel_mongo/managers/config.py` (mongod configuration template; installed library, not in this repo)
- **Evidence**: Every mongod startup emits: "The storage.journal.enabled option and the corresponding --journal and --nojournal command-line options have no effect in this version of Percona Server for MongoDB. Journaling is always enabled. Please remove those options from the config."
- **Impact**: Log noise, no functional impact, but may mask real startup warnings.
- **Fix**: Remove `journal: enabled: true` from the MongoDB config template for version-aware builds.
- **Linter rule**: not established.

### Rolling ops manager logs "Etcd relation configured but no cluster_id yet" on every hook for K8S
- **Severity**: low
- **Kind**: performance / ux
- **Where**: `single_kernel_mongo/managers/mongodb_operator.py` `_generate_cluster_id` (returns `None` for K8S)
- **Evidence**: The message "Etcd relation configured but no cluster_id yet. Using peer backend until cluster_id provided." appears in debug-log on every hook invocation, even on idle units.
- **Impact**: Debug-log noise; this condition is permanent for K8S since cluster IDs are never generated there.
- **Fix**: Demote the log message to `debug` level, or generate cluster IDs for K8S too.
- **Linter rule**: not established.

### ruff reports 15 style issues in test code
- **Severity**: nit
- **Kind**: lint
- **Where**: `tests/integration/helpers.py`, `tests/integration/conftest.py`, etc.
- **Evidence**: `ruff check` reports `UP035` (`typing.Dict`/`List` deprecated), `UP045` (`Optional[str]` → `str | None`), `B006` (mutable default argument), `TRY002` (bare `Exception`), `PIE808` (unnecessary `start=0` in `range`), and `EXE001` (shebang on non-executable files).
- **Impact**: Minor code quality drift in test helpers.
- **Fix**: Accept ruff's auto-fixes (`ruff check --fix`).
- **Linter rule**: All already caught by `ruff`.

## Worth copying

- **Single-kernel pattern**: `AbstractMongoCharm[T, U]` (`single_kernel_mongo/abstract_charm.py`) is a clean design for sharing logic across multiple charms (mongodb-k8s, mongodb VM, mongos-k8s, mongos VM). The charm only specifies `config_type`, `operator_type`, `substrate`, and `peer_rel_name` — everything else is inherited.
- **Structured config with Pydantic**: `MongoDBCharmConfig` in `single_kernel_mongo/core/structured_config.py` uses `BaseModel` with field validators, serializers, and aliases; role validation is particularly clean.
- **Exception hierarchy**: `single_kernel_mongo/exceptions.py` defines 40+ typed exceptions with clear semantics (`DeferrableError`/`NonDeferrableFailedHookChecksError` base classes), making event handlers readable and debuggable.
- **Status management**: `data_platform_helpers.advanced_statuses.handler.StatusHandler` provides per-component, per-scope (app/unit) structured status reporting with recompute support via the `status-detail` action.
- **Rolling ops integration**: The charm uses `charm_refresh` and `charmlibs.rollingops` with sync lock backends for safe rolling restarts. `StopReplsetSyncLockBackend` stops the replica set member before restarting, preventing split-brain.
- **Container access guard**: `KubernetesWorkload.restart()` (`k8s_workload.py`) catches `ChangeError`, `TimeoutError`, and `ConnectionError` and wraps them in `WorkloadServiceError` — a standard ops `Container.can_connect()` guard.
- **Clean charmcraft.yaml**: Uses the modern `poetry-deps`/`charm-poetry` part names, the poetry build plugin, rustup for building from source, and `write-charm-version` from git tags — the canonical Data Platform workflow pattern.

## Common-practice notes

- **Follows convention**: Standard Data Platform layout (`src/charm.py`, `charmcraft.yaml` with poetry plugin, `concierge.yaml`, `spread.yaml`, `tox.ini`). `pyproject.toml` has well-structured dependency groups (`charm-libs`, `build-refresh-version`, `format`, `lint`, `integration`).
- **Follows convention**: Uses `canonical/data-platform-workflows` for CI (`build_charm.yaml`, `lint_workflows.yaml`) — standard for Canonical data platform charms.
- **Follows convention**: `config.yaml` uses `type: secret` for sensitive config options (`system-users`, `tls-peer-private-key`, `tls-client-private-key`) — the modern Juju 3.x approach.
- **Drift from convention**: Four separate storage volumes (`archive`, `data`, `logs`, `temp`) is unusual; most K8S charms use a single data volume. The `temp` volume specifically causes the startup bug.
- **Drift from convention**: No `lib/charms/` directory — all charm libraries are bundled in the `mongo-charms-single-kernel` package. Intentional per `CONTRIBUTING.md`, but means operators can't inspect library code by downloading the charm.

## Tests

- **Unit tests**: None in this repo — removed in commit `68e41c967`. The kernel library has its own tests.
- **Integration tests**: Two modules — `test_charm.py` (deploy + ping, ~30 lines of assertions) and `test_sharding.py` (config-server + 3 shard integration, ~100 lines). Both require a pre-built charm file at `./mongodb-k8s_ubuntu@24.04-{arch}.charm`.
- **Spread tests**: Two tasks (`tests/spread/test_charm.py/task.yaml`, `tests/spread/test_sharding.py/task.yaml`), each running `tox run -e integration` against the respective module. Supports LXD VMs and GitHub CI runners on microk8s 1.35-strict.
- **What's missing**: No TLS, backup, LDAP, upgrade, password rotation, or storage integration test in this repo. Likely covered in the kernel library's CI, but not validated against the packaged K8S charm.
- **CI workflow**: `.github/workflows/ci.yaml` runs lint (tox `lint`), Terraform validation (replica-set and sharded modules), build, and integration tests. Concurrency cancels in-progress CI on new pushes.

## Docs

- **README.md**: Clear overview, requirements, basic usage with deploy examples. Explicitly directs contributors to the `mongo-single-kernel-library` repository; links to ReadTheDocs and Matrix/Discourse community channels.
- **CONTRIBUTING.md**: Explains the single-kernel workflow, testing commands, and build steps. Clear and honest about where to make changes.
- **Terraform modules**: Well-structured modules under `terraform/charm/` and `terraform/product/` for both replica-set and sharded deployments, with variables, outputs, and READMEs; tested in CI.
- **Docs/reality mismatch**: The README's deploy example uses a local `.charm` file rather than the charmhub deploy command (`juju deploy mongodb-k8s --channel 8/edge`), which is not mentioned. An operator following the README exactly would need to pack the charm first, which isn't explained.
- **Missing**: No `docs/` directory in the repo — documentation is hosted on ReadTheDocs (`canonical-charmed-mongodb.readthedocs-hosted.com/8/`).

## Open questions

- Was the `/tmp` permission bug introduced by a change in the rock image, or has it always been present? Issue #467 is from 2026-01-05, suggesting a persistent problem — possibly the rock image or PVC provisioner default mount permissions changed.
- Does the `charm_refresh` upgrade path work correctly on K8S? The code (`KubernetesMongoDBRefresh`, `_post_refresh` handling health checks, balancer re-enable, feature compatibility version) looks solid but was not exercised in this review.
- Is `CrossAppVersionChecker` correctly handling version propagation between config-server and shards? Complex enough to warrant a dedicated integration test.
- Why does `_generate_cluster_id` return `None` for K8S? The rolling ops manager falls back to the peer backend, which works but adds log noise — is there a reason cluster IDs aren't generated on K8S?
</content>
