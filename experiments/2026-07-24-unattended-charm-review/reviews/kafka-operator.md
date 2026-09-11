# kafka-k8s / kafka

A mature, well-structured monorepo charm for Apache Kafka (KRaft mode) on machine and Kubernetes substrates, sharing a large `single_kernel_kafka` library. The code quality (TLS handling, status pattern, structured config) is generally strong, but three separate defects each independently make the charm unsafe to run unattended: unit status does not reflect actual workload health, invalid config permanently bricks every hook, and scaling up brokers on K8s deadlocks via a spurious refresh cycle. A maintainer should fix the workload-health check in `_determine_unit_status` first — it is the one defect that silently hides all the others from an operator watching `juju status`.

| | |
|---|---|
| Repo | canonical/kafka-operator @ `3c25f09` (2026-07-17) |
| Charms | kafka (machine), kafka-k8s (k8s), application (test-only) |
| Substrate | k8s + machine, reviewed on Juju 3.6 (K8s + LXD) and Juju 4.0.5 (LXD) |
| Deployed | yes — Juju 3.6 K8s (rev 116): active with scale-up bug; Juju 3.6 LXD (rev 262): active with sysctl warnings; Juju 4 LXD (rev 262): active (bootstrap race not reproduced on retry); Juju 4 K8s: failed to deploy (controller timeout, 3 attempts) |
| Reviewed | 2026-07-29 |

## What it does

Deploys Apache Kafka 4.x clusters with KRaft consensus (no ZooKeeper), supporting split roles (broker, controller, balancer/Cruise Control), TLS/mTLS with automatic self-signed CA generation, SASL/SCRAM authentication, OAuth, monitoring integration, and external K8s exposure via NodePorts. Code is shared between machine and K8s variants through a `single_kernel_kafka` common library.

## Deployment log

### K8s on Juju 3.6 (concierge-k8s-3) — SUCCESS

```
juju add-model rv-kafka-k8s36 k8s
juju deploy kafka-k8s --channel 4/edge -n 1 --trust
juju deploy kafka-k8s --channel 4/edge -n 1 --trust --config roles=controller ctrl
juju integrate kafka-k8s:peer-cluster-orchestrator ctrl:peer-cluster
```

Both units reached `active` within ~5 minutes. Self-signed TLS certificates were auto-generated (no TLS provider relation needed). `bootstrap-controller` was correctly populated as `ctrl-0.ctrl-endpoints:9098`. Version: 4.1.1 (rev 116).

An earlier attempt on Juju 4 with no RBAC/trust in place hit `KubernetesJujuAppNotTrusted` and `ApiError: nodes "generic-juju" is forbidden` during `__init__`, and an `OSError: [Errno 19] No such device` from `SO_BINDTODEVICE` in `RelationState.ip()` (GitHub issue #520). None of this reproduced on Juju 3.6 K8s with `--trust`.

### Machine on Juju 3.6 (concierge-lxd) — SUCCESS

```
juju deploy kafka --channel 4/edge --config roles=controller controller36 -n 1
juju deploy kafka --channel 4/edge --config roles=broker broker36 -n 1
juju integrate broker36:peer-cluster-orchestrator controller36:peer-cluster
```

Both units reached `active` within ~8 minutes. Broker briefly showed `blocked: sysctl params cannot be set`, resolving after snap install completed. Both units show `machine system settings are not optimal` warnings (sysctl checks running inside LXD containers). Version: 4.2.0 (rev 262).

### Machine on Juju 4 (concierge-lxd-4) — SUCCESS (with caveats)

```
juju deploy kafka --channel 4/edge --config roles=controller ctrl4 -n 1
juju deploy kafka --channel 4/edge --config roles=broker broker4 -n 1
juju integrate broker4:peer-cluster-orchestrator ctrl4:peer-cluster
```

Both units reached `active` within ~6 minutes; sysctl warnings present. The bootstrap-address race seen in an earlier attempt on this controller (broker stuck in `error: hook failed "secret-remove"`, root-caused to `bootstrap-controller: :9098` with an empty host because the controller wrote bootstrap data before its IP was populated in peer relation data) did not reproduce this time — both units showed active/active with `charmed-kafka.daemon active`. `debug-log` did show a transient `__main__:unit not connected to the controller` error with a traceback in `health.py:_on_update_status` that self-recovered. The race appears timing-dependent.

### K8s on Juju 4 (concierge-k8s-4) — FAILED

Three attempts to deploy `kafka-k8s` timed out (180s each); the model remained empty. May be a controller-level issue, but the charm's heavy `__init__` (`charm_refresh.Kubernetes` + lightkube calls) could be contributing.

## Observed behaviour

### Deployment success patterns

- **Self-signed TLS works**: internal CA and self-signed peer certs are auto-generated without a TLS provider relation.
- **Bootstrap address on K8s is correct**: `bootstrap-controller` in peer-cluster relation data resolves to `ctrl-0.ctrl-endpoints:9098`.
- **Relation recovery works**: removing the peer-cluster relation blocks both units with clear messages; re-adding restores them to active within ~30 seconds (machine) / ~2 minutes (K8s).

### Failure injection results

- **Invalid config bricks the charm**: `juju config kafka-k8s compression-type=invalid` was accepted by Juju but raised `pydantic.ValidationError` in `CharmConfig.__init__()`. Since `__init__` runs on every hook, every subsequent hook (`config-changed`, `secret-remove`, `update-status`, etc.) failed with the same traceback until valid config was restored. Confirmed on both K8s and machine.
- **`log-level=TRACE` accepted silently**: config.yaml documents allowed values as `ERROR, WARNING, INFO, DEBUG`, but `TRACE` was accepted without error on both substrates.
- **Workload health not monitored**: `pebble stop kafka` inside the K8s container stopped the service (`pebble services` → `inactive`), but the charm continued to report `active/idle` for the full ~3-minute observation window, with no detection in `debug-log`. `_determine_unit_status` (both `machine/src/charm.py` and `k8s/src/charm.py`) calls `self.state.ready_to_start`, which checks relation data, TLS state, and bootstrap addresses but never calls `self.workload.active()`. The workload check exists (`broker.py` / `controller.py` `.healthy` properties do call `self.workload.active()`) but is only used in the refresh/config-changed/credential-cache paths, never in status determination. Detection is otherwise indirect: K8s `update-status` (5-minute interval) queries the controller via `broker_active()`, not Pebble directly.
- **Scale-up on K8s triggers spurious refresh cycle**: scaling `broker` from 2 to 3 units caused the app to enter a `charm_refresh` cycle (`maintenance: Refreshing`). The new unit (`broker/2`) was permanently stuck at `waiting for internal TLS setup` because `_on_start` (`broker.py:156-158`) returns early while `self.charm.refresh.in_progress` is true. `resume-refresh` failed with `"Unit 2 is unhealthy. Refresh will not resume."` — a deadlock: the unit can't become healthy without starting, and can't start while refresh is in progress. Root cause: `KubernetesKafkaRefresh.run_pre_refresh_checks_after_1_unit_refreshed` (`refresh.py:70-76`) sets a StatefulSet rolling-update partition and the library treats the new unit as mid-refresh. Scaling `ctrl` from 2 to 3 worked correctly (no refresh cycle triggered).
- **Scale-up 1→2 (earlier round)**: scaling kafka-k8s and ctrl from 1 to 2 units worked; the second controller unit briefly showed `blocked: service not running` before recovering — a transient false positive.
- **Actions**: `get-listeners` returns correct listener info on both substrates. `pre-refresh-check` returns ready status and rollback instructions. `rebalance` failed validation with `"mode" property is missing and required`, a required parameter not shown in `juju actions` output. `force-refresh-start force=True` was rejected with `additional property "force" is not allowed`.
- **Relation removal and recovery**: on both substrates, removing the peer-cluster relation cleanly blocks both units (`"application needs to be related with a KRaft controller"` / `"missing required peer-cluster relation"`); re-adding restores to active in ~30s (machine) / ~2min (K8s).
- **sysctl warnings**: both machine deployments (Juju 3.6 and 4) warn about `vm.swappiness=60 > 1` and related sysctl settings. `KafkaHealth.machine_configured()` (`health.py`) tries to set these values, gets `permission denied` in LXD containers, and restores original values; status correctly shows `active` with `machine system settings are not optimal` appended. On the Juju 4 run the health check crashed once with a traceback (`"unit not connected to the controller"` at `health.py:191`) before self-recovering on the next hook.

### Juju version differences

| | Juju 3.6 | Juju 4.0.5 |
|---|---|---|
| K8s charm | Deploys, active (scale-up has refresh deadlock) | Fails to deploy (controller timeout) |
| Machine charm | Deploys, active | Deploys, active (bootstrap race transient, self-recovers) |
| Charm revision | 4/edge rev 116 (k8s), 262 (machine) | Same |

An earlier pass of this review claimed the machine charm was broken on Juju 4; retesting showed both units reaching `active/idle`. The bootstrap-address race may be timing- or unit-count-dependent rather than deterministic.

### Resource usage

- Snap install time: ~3-4 minutes on LXD containers (Juju 3.6 and 4).
- K8s pod startup: ~2-3 minutes (image pull + Pebble service start).
- Pydantic `UnsupportedFieldAttributeWarning` on every hook — 2 warnings/hook, hundreds over a deployment lifecycle.
- On Juju 4 LXD, `_on_update_status` crashed once during startup (`health.py:191`) but recovered on the next hook.
- `pebble stop kafka` went undetected for the full 3-minute observation window; the K8s update-status interval is 5 minutes and detection would go via the controller's `broker_active()` check, not a direct Pebble `active()` check.

## Findings

### 1. `_determine_unit_status` does not check workload health — false-positive `active`
- **Severity**: critical
- **Kind**: bug
- **Where**: `machine/src/charm.py:214-237` and `k8s/src/charm.py:195-213` (`_determine_unit_status`)
- **Evidence**: `pebble stop kafka` inside the K8s container stopped the service (confirmed `inactive` via `pebble services`), but `juju status` continued to show `active/idle` for the entire ~3-minute observation window with no detection in `debug-log`. `_determine_unit_status` calls `self.state.ready_to_start` (relation data, TLS state, passwords) but never `self.workload.active()`. That check exists elsewhere (`broker.py`/`controller.py` `.healthy` properties) but is only used in the refresh and config-changed paths.
- **Impact**: An operator relying on `juju status` believes the cluster is healthy while a broker is dead.
- **Fix**: Call `self.workload.active()` in `_determine_unit_status`; return a `SERVICE_NOT_RUNNING`-equivalent status if inactive.
- **Linter rule**: "`_determine_unit_status` does not call `workload.active()`" — mechanically checkable.

### 2. K8s scale-up triggers spurious `charm_refresh` cycle, permanently blocks new units
- **Severity**: critical
- **Kind**: bug
- **Where**: `k8s/src/charm.py:92-98` (refresh init), `common/single_kernel_kafka/events/broker.py:156-158` (`_on_start` early return), `common/single_kernel_kafka/events/refresh.py:70-76` (`run_pre_refresh_checks_after_1_unit_refreshed`)
- **Evidence**: Scaling `broker` 2→3 on Juju 3.6 K8s put the app into `maintenance: Refreshing`. The new unit (`broker/2`) stayed stuck at `waiting for internal TLS setup`. `resume-refresh` failed with `"Unit 2 is unhealthy. Refresh will not resume."`. Root cause: `run_pre_refresh_checks_after_1_unit_refreshed` sets a StatefulSet rolling-update partition; the new unit is detected as mid-refresh, so `_on_start` returns early and never starts Kafka on it — a deadlock. Scaling `ctrl` 2→3 did not trigger the cycle.
- **Impact**: A standard scale-up permanently breaks the deployment with no documented recovery path — a showstopper for K8s production use.
- **Fix**: `run_pre_refresh_checks_after_1_unit_refreshed` should not trigger a refresh cycle for scale-up; alternatively `_on_start` should always run for genuinely new units regardless of refresh state.
- **Linter rule**: not mechanically checkable.

### 3. Invalid config values raise `ValidationError` in `__init__`, bricking every hook
- **Severity**: high
- **Kind**: bug
- **Where**: `common/single_kernel_kafka/core/cluster.py:73` (`ClusterState.__init__` → `charm.config`), `machine/lib/charms/data_platform_libs/v0/data_models.py:200`
- **Evidence**: `juju config kafka-k8s compression-type=invalid` was accepted by Juju but produced `pydantic.ValidationError` in `CharmConfig.__init__()`. Every subsequent hook (`config-changed`, `secret-remove`, `update-status`, ...) failed with the same traceback until valid config was restored. Confirmed on both K8s and machine.
- **Impact**: A single bad config value can brick the entire charm — no hooks run, no status update, operator sees only `error: hook failed` with no indication which value is wrong.
- **Fix**: catch `pydantic.ValidationError` around config access and set `BlockedStatus(f"invalid config: {e}")` instead of crashing; or move validation to a lazy property invoked from `config-changed`/`collect-status` rather than `__init__`.
- **Linter rule**: "`__init__` accesses `self.config`/`charm.config` without try/except for `ValidationError`" — partially mechanically checkable.

### 4. Heavy `__init__` calls K8s API and `charm_refresh` without graceful error handling
- **Severity**: high
- **Kind**: bug
- **Where**: `k8s/src/charm.py:92-98` (charm_refresh init), `common/single_kernel_kafka/events/tls.py:62` (`TLSHandler.__init__` → `build_sans`)
- **Evidence**: `charm_refresh.Kubernetes(...)` is instantiated in `__init__` and may call the K8s API; `TLSHandler.__init__` calls `build_sans()` → `K8sManager.get_node_ip()` → lightkube. An untrusted deployment raised `KubernetesJujuAppNotTrusted`, and missing RBAC raised `ApiError: nodes "generic-juju" is forbidden` — neither is caught (only `PeerRelationNotReady` and `UnitTearingDown` are). On Juju 4 the K8s charm consistently failed to deploy (3 attempts, 180s timeout each).
- **Impact**: The charm is undeployable on K8s clusters without the right trust/RBAC, and every hook pays for expensive K8s calls it may not need.
- **Fix**: catch `KubernetesJujuAppNotTrusted` and `ApiError` and set a clear `BlockedStatus`; move `build_sans`/lightkube calls out of `__init__` into lazily-initialised properties or explicit hook handlers.
- **Linter rule**: "`__init__` calls lightkube or `charm_refresh.Kubernetes` without catching `ApiError`" — mechanically checkable.

### 5. Bootstrap controller address race on machine substrate (timing-dependent)
- **Severity**: high
- **Kind**: bug
- **Where**: `common/single_kernel_kafka/core/models.py:1018-1028` (`KafkaBroker.internal_address`), `common/single_kernel_kafka/core/models.py:811` (`KafkaCluster.bootstrap_controller`), `common/single_kernel_kafka/events/controller.py:114-118` (`_init_kraft_mode`)
- **Evidence**: On one Juju 4 LXD attempt, `bootstrap-controller` resolved to `:9098` (empty host) because `internal_address` reads from peer-relation-data keys that are not yet populated on first start; the broker daemon then crashed with `Main process exited, code=exited, status=1/FAILURE`, and the unit ended up in `error: hook failed "secret-remove"`. On a repeat attempt both units reached `active` without incident, with only a transient self-recovering `"unit not connected to the controller"` error. The race is timing-dependent, not consistently reproducible.
- **Impact**: on slower machines or different unit counts the broker may reliably hit this race and get stuck in an error state.
- **Fix**: call `update_ip_addresses()` before `_init_kraft_mode()`, or derive the address from `self.model.get_binding(self.peer_relation).network.bind_address` instead of relying on not-yet-populated peer relation data.
- **Linter rule**: not mechanically checkable (event-ordering dependency).

### 6. `_broker_status` reads bootstrap-controller from wrong relation in combined mode
- **Severity**: high
- **Kind**: bug
- **Where**: `common/single_kernel_kafka/core/cluster.py:551` (`_broker_status`), `common/single_kernel_kafka/core/cluster.py:157` (`peer_cluster` property)
- **Evidence**: with `roles=broker,controller` on the same app, `peer_cluster` wraps `peer_cluster_orchestrator_relation` (the provides side, `None` in same-app mode), so `_broker_status` reads `self.peer_cluster.bootstrap_controller` → `""`, while `self.cluster.bootstrap_controller` has the correct local value. Observed as `blocked: unit not connected to the controller` in combined-mode deployment; a separate attempt (1 unit, then scaled to 3) had units 1 and 2 stuck at `waiting for internal TLS setup` and unit 0 eventually blocked the same way.
- **Impact**: the combined `roles=broker,controller` mode documented in the README is broken.
- **Fix**: when `runs_broker and runs_controller`, `_broker_status` should read bootstrap data from `self.cluster` rather than `self.peer_cluster`.
- **Linter rule**: not mechanically checkable.

### 7. `RelationState.ip()` has no error handling — crashes on K8s
- **Severity**: medium
- **Kind**: bug
- **Where**: `common/single_kernel_kafka/core/models.py:302-317`
- **Evidence**: `ip` uses `socket.setsockopt(SOL_SOCKET, SO_BINDTODEVICE, ...)` and `connect(("10.10.10.10", 1))` with no try/except. On K8s this raised `OSError: [Errno 19] No such device` (GitHub issue #520) on `peer-cluster-orchestrator-relation-changed` and `storage-attached` hooks in an untrusted/no-RBAC deployment. Not reproduced on Juju 3.6 K8s with `--trust`.
- **Impact**: any hook that calls `update_ip_addresses()`/`update_peer_ip_address()` can crash on K8s pods where the bound interface name doesn't exist in the pod netns.
- **Fix**: wrap the body in try/except, falling back to `self.internal_address` or empty string; make the `SO_BINDTODEVICE` binding substrate-aware or remove it.
- **Linter rule**: "`socket.setsockopt` without try/except" — mechanically checkable.

### 8. `log-level` config accepts invalid values (`TRACE`) — `LogLevel` enum defined but not wired
- **Severity**: medium
- **Kind**: bug
- **Where**: `common/single_kernel_kafka/core/structured_config.py:25-29` (`LogLevel` enum), `structured_config.py:61` (`log_level: str`)
- **Evidence**: `juju config broker log-level=TRACE` was accepted without error on both K8s and machine, though config.yaml documents allowed values as `ERROR, WARNING, INFO, DEBUG`. `LogLevel(str, Enum)` is defined at line 25 with the four valid values, but `CharmConfig.log_level` is typed `str`, not `LogLevel` — the enum is dead code.
- **Impact**: the Kafka workload may not understand `TRACE`, producing a silent misconfiguration.
- **Fix**: change `log_level: str` to `log_level: LogLevel` at line 61.
- **Linter rule**: "enum class defined but not used as a type annotation in the same module" — mechanically checkable.

### 9. Action schemas under-documented — `rebalance` and `force-refresh-start` fail validation
- **Severity**: medium
- **Kind**: ux
- **Where**: `common/single_kernel_kafka/events/actions.py`, `common/single_kernel_kafka/events/balancer.py`
- **Evidence**: `juju run broker/0 rebalance` failed with `"mode" property is missing and required, given {}"`, though `juju actions` lists no required parameters. `juju run broker/0 force-refresh-start force=True` failed with `additional property "force" is not allowed`.
- **Impact**: operators cannot use these actions without reading source to discover parameter names.
- **Fix**: add `params` with descriptions to the action definitions in `actions.yaml`/`charmcraft.yaml`.
- **Linter rule**: "action defined without params in actions.yaml" — mechanically checkable.

### 10. K8s charm fails to deploy on Juju 4
- **Severity**: medium
- **Kind**: bug
- **Where**: deployment to concierge-k8s-4 (Juju 4.0.5)
- **Evidence**: three separate deploy attempts timed out (>180s); the model remained empty. Plausibly related to the heavy `__init__` K8s calls (Finding #4), but not confirmed — the model never reached a point where charm hooks could log.
- **Impact**: the K8s charm is not deployable on this Juju 4 environment; significant blocker given the ecosystem's Juju 4 migration.
- **Fix**: make `__init__` lightweight (lazy K8s clients); test explicitly against Juju 4 K8s controllers.
- **Linter rule**: not mechanically checkable.

### 11. machine LXD deployments produce sysctl warnings and an uncaught crash path
- **Severity**: low
- **Kind**: ux
- **Where**: `common/single_kernel_kafka/health.py`
- **Evidence**: both Juju 3.6 and 4 LXD deployments show `machine system settings are not optimal — see logs for info` (`vm.swappiness=60 > 1`, `vm.max_map_count`, fd limits); the health check tries to set these, gets `permission denied` in the LXD container, and restores originals — correctly reported as a non-fatal `active` warning. On the Juju 4 run, `_on_update_status` crashed once with a traceback in `machine_configured()` (`"unit not connected to the controller"` at `health.py:191`) — not a `SnapError`, so not caught by the existing except clause (`broker.py:326`) — before self-recovering on the next hook.
- **Impact**: expected in LXD but clutters logs; the crash shows a gap in exception handling for health checks.
- **Fix**: detect container environment and skip sysctl checks; broaden the except clause beyond `SnapError` to catch unexpected exceptions from `machine_configured()`.
- **Linter rule**: not mechanically checkable.

### 12. Unit tests fail collection when `keytool` is not installed
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_tls_manager.py:54-70`
- **Evidence**: module-level `_exec(KEYTOOL)` raises `KeyError: 'log_on_error'` when `keytool` returns non-zero; the handler at line 64 accesses `kwargs["log_on_error"]` without checking the key exists. Requires `openjdk-17-jdk-headless` to run.
- **Impact**: contributors without Java installed can't run the test suite.
- **Fix**: use `pytest.importorskip`/skip module-level setup gracefully when `keytool` is missing; fix the handler to use `kwargs.get("log_on_error", True)`.
- **Linter rule**: not mechanically checkable.

### 13. `BALANCER.requested_secrets` has a typo: `controller-passwrod`
- **Severity**: low
- **Kind**: bug
- **Where**: `common/single_kernel_kafka/core/literals.py:224`
- **Evidence**: `"controller-passwrod"` (misspelling of "password").
- **Impact**: latent bug — if any code matches this exact string to a secret field name, lookup fails silently. Impact currently limited because secrets are looked up via `SECRET_LABEL_MAP` with different keys.
- **Fix**: change to `"controller-password"`.
- **Linter rule**: "suspicious string matching known typo patterns" (custom codespell dictionary) — could be checked mechanically.

### 14. Pydantic `UnsupportedFieldAttributeWarning` spam on every hook
- **Severity**: low
- **Kind**: lint
- **Where**: dependency issue in `charms.data_platform_libs.v1.data_interfaces`
- **Evidence**: `UnsupportedFieldAttributeWarning: The 'default' attribute with value None was provided to the Field() function...` on every hook, 2 warnings per hook.
- **Impact**: log noise; hundreds of repeated warnings over a deployment lifecycle make `debug-log` harder to scan.
- **Fix**: fix the upstream library to use `Annotated` metadata, or suppress the warning in the charm's logging config.
- **Linter rule**: not a charm-level lint issue.

### 15. `_on_roles_changed` handler duplicated between machine and k8s `charm.py`
- **Severity**: low
- **Kind**: lint
- **Where**: `machine/src/charm.py:119-133` and `k8s/src/charm.py:148-162`
- **Evidence**: `_on_roles_changed` is identical in both files; `_restart_broker` is near-identical (minor `disable_enable` difference on machine).
- **Impact**: duplication that the shared `single_kernel_kafka` library was intended to eliminate.
- **Fix**: move `_on_roles_changed` into the shared base class or a mixin.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Single-kernel architecture**: `common/single_kernel_kafka/` is a well-structured shared-library pattern for monorepo charms — `core/`, `events/`, `managers/`, `lib/` is logical and navigable. `KafkaCharmBase` + `TypedCharmBase` gives good type safety.
- **Structured config**: `CharmConfig` (`core/structured_config.py`) uses Pydantic validators for range checks, regex validation, and secret URI validation across all config options. (The failure mode when validation fails needs improvement — see Finding #3.)
- **Status enum pattern**: `Status` enum paired with `StatusLevel`/`DebugLevel` (`core/literals.py:262-358`) cleanly ties status to log level.
- **`collect_unit_status`/`collect_app_status`**: correct, idiomatic use of ops 2.x `CollectStatusEvent`/`event.add_status()`.
- **Comprehensive TLS handling**: `TLSManager` (`managers/tls.py`) handles internal CA generation, self-signed certs, keystore/truststore management, cert rotation with old/new prefix aliases, and cross-app trust chain updates — production-grade.
- **`refresh_versions.toml`**: externalising snap revision and charm version makes workload version tracking easy.
- **Per-feature integration test envs**: `tox.ini` has per-feature envs (e.g. `integration-tls`, `integration-kraft`), and `conftest.py` supports a `--kraft-mode` CLI flag.
- **Self-signed TLS auto-generation**: lowers the barrier to entry by not requiring a TLS provider relation for peer communication.
- **Relation removal/recovery UX**: clear, actionable `blocked` messages on both ends, with fast, correct recovery on re-add — a model pattern for relation-required handling.

## Common-practice notes

- **Monorepo layout**: `machine/`/`k8s/` + `common/` follows the Data Platform convention (consistent with PostgreSQL, MySQL, OpenSearch charms).
- **`charmcraft.yaml`**: `poetry` plugin with `rustup` for Rust-based Python deps; `poetry-deps` part with `uv`.
- **`charm_refresh` integration**: uses the Canonical-standard in-place upgrade library; `force-refresh-start`/`resume-refresh` follow the refresh protocol.
- **Data Interfaces**: both V0 (`charms.data_platform_libs.v0.data_interfaces`) and V1 are used; the V1 migration is partial — `RelationStateV1` and `RelationState` coexist.
- **Terraform module**: `terraform/` provides a Terraform charm module, consistent with ecosystem trend.
- **Drift from convention**: uses `socket` tricks (`connect(("10.10.10.10", 1))`) to determine IP addresses rather than Juju network bindings; most modern charms use `self.model.get_binding(relation).network.bind_address`.
- **Drift from convention**: `__init__` does heavy work (K8s API calls, TLS SAN computation, refresh coordinator init) instead of staying lightweight.
- **Drift from convention**: relies on peer relation data for essential startup information (IP, bootstrap controller address) rather than Juju primitives, creating fragile ordering dependencies (Findings #5, #6).

## Tests

195 passed, 97 skipped, 69% coverage. Skipped tests are mostly TLS-manager tests requiring `keytool` (`openjdk-17-jdk-headless`). `tox -e unit` runs cleanly in ~73 seconds once Java is installed.

Coverage gaps relative to findings:
- `events/peer_cluster.py`: 28% — peer-cluster relation handling and split-role logic barely tested
- `events/refresh.py`: 29% — upgrade/refresh path barely tested; no test for the K8s scale-up refresh deadlock (Finding #2)
- `managers/k8s.py`: 39% — K8s-specific operations (NodePort, service creation, lightkube calls) largely untested
- `events/tls.py`: 45% — TLS rotation, truststore updates, mTLS cert handling largely untested
- `events/actions.py`: 60% — action handlers barely tested
- `managers/auth.py`: 56% — user add/remove, credential caching not well covered
- `managers/balancer.py`: 51% — Cruise Control operations, including `wait_for_task` (open issue #437), little covered
- no integration test covers the K8s substrate (all integration tests target the machine charm)
- no test covers `roles=broker,controller` combined mode on a single app (Finding #6)
- no test for scale-up triggering the refresh cycle (Finding #2)
- `ip`'s `SO_BINDTODEVICE` path has no unit test mocking the `OSError` (Finding #7, GH #520)
- `_on_start`'s ordering dependency (IP before bootstrap address) has no explicit test (Finding #5)
- no test for `log_level` validation (Finding #8)
- no test for `CharmConfig.__init__` catching `ValidationError` gracefully (Finding #3)

## Docs

- **README**: comprehensive — deployment, scaling, password rotation, storage, relations, TLS, monitoring. Deployment example uses `roles=controller`/`roles=broker` separately, the working path. Does not mention the `juju trust` requirement for K8s.
- **Reference docs**: extensive — `statuses.md`, `file-system-paths.md`, `listeners.md`, `performance-tuning.md`, `requirements.md`, `snap-commands.md`, `terraform.md`.
- **How-to guides**: `client-connections.md`, `create-mtls-client-credentials.md`, `kafka-connect.md`, `kafka-ui.md`, `manage-units.md`, `monitoring.md`, `oauth.md`, `schemas-serialisation.md`, `tls-encryption.md`, `upgrade.md`.
- **Doc/reality mismatch**: the README tutorial (`juju deploy kafka -n 5 --config roles="controller"`, `-n 3 --config roles="broker"`) works on machine/Juju 3.6 but the K8s charm fails on Juju 4; the `juju trust` requirement for K8s is undocumented. The documented `roles=broker,controller` combined mode is broken (Finding #6).
- **CONTRIBUTING.md**: references an outdated Discourse docs process (open issue #473).

## Open questions

1. Does the `roles=broker,controller` combined mode work on any deployment? Observed failures suggest it is broken across substrates; a successful deployment would settle this.
2. Is the bootstrap-address race (Finding #5) specific to Juju 4? Succeeded on Juju 3.6 machine; on Juju 4, one attempt reproduced it and a second did not — suggests non-determinism.
3. Why does the K8s charm consistently time out on Juju 4 (3/3 attempts)? Controller-level issue vs. the charm's heavy `__init__` is unresolved — the model never reached a point where charm hooks could log.
4. What is the memory/CPU profile of a running broker vs. controller? `kubectl top pod` output was not obtained (unverified — related to open issue #512 on controller JVM sizing).
5. Is the `controller-passwrod` typo (Finding #13) actually used anywhere at runtime?
6. Does scaling down (removing units) also trigger the refresh deadlock (Finding #2)? Only 2→3 scale-up on K8s was tested.
7. Can the K8s scale-up deadlock be bypassed via `force-refresh-start` with correct parameters? The actual parameter name is unknown from `juju actions` output alone.
8. Does the `_on_update_status` crash in `machine_configured()` on Juju 4 LXD (Finding #11) reproduce consistently, or was it a one-off startup race?
