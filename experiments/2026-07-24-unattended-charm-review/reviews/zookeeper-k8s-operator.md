# zookeeper-k8s

A mature, well-structured K8s charm for Apache ZooKeeper from the Canonical Data Platform team, with clean separation between state models, event handlers, managers, and workload abstraction. Deploys reliably from Charmhub on both Juju 3.6 and 4.0 and handles most runtime failures (SIGKILL, missing S3, bad TLS relation removal) gracefully. The critical defect is that six of seven structured-config fields crash the charm at construction time via unguarded pydantic validation, putting every unit into a permanent error state from a single bad `juju config` value — recoverable only via a non-obvious workaround (or `juju resolve`). Combined with a `pre-upgrade-check` action that permanently blocks password rotation on single-unit clusters and a scale-up path that fails outright on Juju 4.0, this charm needs defensive-config and upgrade-path hardening before it's safe for unattended operation. First priority for a maintainer: wrap `ClusterState`'s access to `charm.config` so pydantic `ValidationError` cannot escape `__init__`.

| | |
|---|---|
| Repo | canonical/zookeeper-k8s-operator @ 9acaef3 (2026-03-23) |
| Charms | zookeeper-k8s, application (test-only) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (3/stable rev 78), concierge-k8s-4 (3/stable rev 78); seven deployment/failure-injection sessions run and torn down |
| Reviewed | 2026-08-03 |

## What it does

Deploys Apache ZooKeeper 3.9.2 on Kubernetes via Juju. Provides a `zookeeper` client interface (consumed by Kafka et al.), TLS via `tls-certificates`, monitoring via `metrics-endpoint`/`grafana-dashboard`/`logging`, and S3 backup/restore. Supports external access via NodePort and LoadBalancer. Uses Pebble with a health check for workload management, SASL auth (Digest-MD5), TLS with Java Keystore/Truststore management, and rolling upgrades via the `data_platform_libs` upgrade framework. Structured config via pydantic with `TypedCharmBase`.

## Deployment log

### Juju 4.0 deep deployment (concierge-k8s-4, rv-zk-deep)
```bash
juju deploy zookeeper-k8s --channel 3/stable -n 3 --trust
juju deploy self-signed-certificates --channel 1/stable --trust
juju deploy grafana-agent-k8s --channel 1/stable --trust
juju deploy s3-integrator --channel 1/stable --trust
juju relate zookeeper-k8s:certificates self-signed-certificates
juju relate zookeeper-k8s:logging grafana-agent-k8s:logging-provider
```
All integrations settled. TLS enabled with certificate rotation across 3 dynamic config generations observed. Logging relation → grafana-agent blocked on missing grafana-cloud-config (expected). S3 integrator → zookeeper-k8s blocked "cannot create s3 bucket" with dummy credentials (expected, clean message).

### Juju 3.6 failure-injection deployment (concierge-k8s-3, rv-zk-fail)
```bash
juju deploy zookeeper-k8s --channel 3/stable -n 1 --trust
```
Single unit active/idle. Used for targeted failure testing.

### Failure injections

- `juju config tick-time=-1` (both Juju 3.6 and 4.0) → all units error `hook failed: config-changed`. Reverting to `tick-time=2000` (the current value) does **not** trigger a new hook — units stay in error permanently, since Juju treats it as a no-op. Setting a *different* valid value (e.g. `sync-limit=3`) does trigger a new `config-changed` that recovers successfully — the only recovery path short of `juju resolve`.
- `juju config init-limit=0` (Juju 4.0) → identical crash pattern.
- `juju config expose-external=bogus` → identical pydantic crash on enum validation: `value is not a valid enumeration member; permitted: 'false', 'nodeport', 'loadbalancer'`. Unlike integer fields, recovery works by setting the *same* field to a valid value (e.g. `expose-external=nodeport`), because Juju sees the value change from "bogus" to "nodeport" and fires a fresh hook.
- `juju config log-level=BOGUS` → same enum crash. All three integer fields (`Field(gt=0)`) and the two enum fields (`LogLevel`, `ExposeExternal`) crash identically. Only `certificate-include-ip-sans` (a boolean) is safe, because booleans are coerced rather than validated.
- `juju run zookeeper-k8s/0 set-tls-private-key internal-key="not-a-valid-key"` → crashed with `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x9e`. No graceful error handling.
- Scale-up 3→5 (Juju 4.0, rv-zk-deep) → new units 3 and 4 failed with `hook failed: upgrade-relation-changed` (repeated retries all failing per `show-status-log`). Scale-down was then blocked: `juju scale-application zookeeper-k8s 3` was acknowledged twice but the StatefulSet stayed at 5 replicas (`juju status` showed `5/3`).
- Scale-up 3→5 retested on a fresh model (rv-zk-scale4, Juju 4.0) and again on Juju 3.6 (rv-zk-fail3) → both blocked before reaching the upgrade path: PVCs for units 3 and 4 stuck Pending with "Not enough disk space" from the rawfile CSI provisioner — an infrastructure limitation of the test environment, not a charm bug. Could not re-confirm the `upgrade-relation-changed` failure under these conditions; it stands from the rv-zk-deep run only.
- Remove TLS relation while running → rolling restart triggered, all units recovered to active. TLS lines correctly removed from `zoo.cfg`, but `keystore.p12`, `truststore.jks`, `server.pem`, `ca.pem`, `bundle.pem`, `server.key` left on disk.
- Remove logging relation while running (Juju 4.0) → zookeeper-k8s remained active, no hook failure. Issue #139 not reproduced on rev 78.
- Kill workload with `kill -9` on the Java QuorumPeerMain PID → Pebble restarted the service in ~5s (new start time in `pebble services`). Charm never left active state.
- `create-backup` / `restore` / `list-backups` without functioning S3 → all failed gracefully: "Cluster needs an access to an object storage to make a backup".
- `set-password` on non-leader unit → correct error: "Password rotation must be called on leader unit".
- `set-password` on leader → returned new password, triggered successful rolling restart.
- `pre-upgrade-check` on single-unit cluster → completed successfully but wrote `upgrade-stack: [0]` to the upgrade peer relation, which then permanently blocks `set-password` (see finding below).
- `resume-upgrade` outside a real upgrade → correctly failed: "Upgrade can be resumed only once after juju refresh is called". `get-super-password` and `get-sync-password` both returned passwords correctly.
- `expose-external=nodeport` (Juju 3.6) → NodePort service `zookeeper-k8s-exposer` created with ports `2181:30534`, `2182:32654`. Working.

## Observed behaviour

- **Deploy time**: ~100s to active/idle across 3 units (both Juju versions), ~50s for 1 unit.
- **Resource use** (`kubectl top pod`): ~200-270m CPU, ~200MB memory per unit. Java heap configured at `-Xmx1000m`.
- **Pebble plan**: single service `zookeeper` with `SERVER_JVMFLAGS` env, `startup=enabled`, health check `echo ruok | nc <pod-ip> 2181`.
- **TLS behaviour**: certificate rotation creates a new dynamic config file each time (e.g. `zoo.cfg.dynamic.100000000` → `10000002e` → `10000004b`). Bundle, CA, keystore, truststore, and `server.pem` all present and rotated. After TLS removal, `zoo.cfg` no longer has SSL lines but cert files remain on disk.
- **Hook count**: a trivial config change triggered a rolling restart with 10+ hooks across 3 units, driven through the catch-all handler.
- **Config change with same value**: `config_changed()` correctly returns `False`, no restart occurs.
- **Container not ready**: correctly defers with `MaintenanceStatus("zookeeper container not ready")`.
- **S3 integration with bad credentials**: unit 0 goes to `blocked: cannot create s3 bucket` — correct and helpful.
- **Pydantic crash recovery nuance**: setting a field back to its previously-set value does not fire a `config-changed` hook (Juju treats it as a no-op); setting a *different* valid value triggers a new hook that rebuilds `CharmConfig` successfully. The operator must know this trick, and it isn't documented.
- **Juju 4.0 scale-down bug**: with units 3 and 4 in error state from `upgrade-relation-changed`, `juju scale-application 3` was acknowledged but the StatefulSet was never reduced from 5 replicas; `juju status` showed `5/3`.

## Findings

### Pydantic config validation crash on bad values renders charm inoperable
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:73` → `src/core/cluster.py:51` → `lib/charms/data_platform_libs/v0/data_models.py:200` → `src/core/structured_config.py:19-21`
- **Evidence**: `juju config zookeeper-k8s tick-time=-1` or `init-limit=0` crashes all units with:
  ```
  pydantic.error_wrappers.ValidationError: 1 validation error for CharmConfig
  tick_time / init_limit
    ensure this value is greater than 0 (type=value_error.number.not_gt; limit_value=0)
  ```
  Crash chain: `ZooKeeperCharm.__init__` (line 73) calls `ClusterState(self, …)` → `ClusterState.__init__` (line 51) accesses `charm.config` → `TypedCharmBase.config` property (`data_models.py:200`) calls `self.config_type(**translated_keys)` → `CharmConfig(**translated_keys)` triggers pydantic validation, raising `ValidationError` before any hook handler runs. Units stay in error state permanently. Recovery differs by field type: for integer fields, setting the *same* value is a Juju no-op, so the operator must set a *different* valid field (e.g. `sync-limit=3`) to trigger a new hook; for enum fields, setting the *same* field to a valid value works because Juju sees the value change. Only the boolean `certificate-include-ip-sans` is unaffected.
- **Impact**: 6 of 7 config fields can crash the charm with a single invalid value; the charm cannot set `BlockedStatus` because the crash happens in `__init__`, not in a hook. Single-mistake → total outage, with an undocumented and field-type-dependent recovery path.
- **Fix**: Wrap `self.config` access in `ClusterState.__init__` in try/except, catch `ValidationError`, and store it for hook handlers to report. Alternatively, `TypedCharmBase.config` should return a sentinel rather than raising. Short-term: add Juju config range constraints and regex patterns in `charmcraft.yaml` (Juju 4 supports `range` and `pattern`).
- **Linter rule**: "pydantic config model instantiated without surrounding try/except in charm `__init__` or early `Object.__init__`" — mechanically checkable.

### `set-tls-private-key` action crashes on non-UTF8 keys
- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/tls.py:181`
- **Evidence**: `juju run zookeeper-k8s/0 set-tls-private-key internal-key="not-a-valid-key"` crashed with:
  ```
  Uncaught UnicodeDecodeError in charm code: 'utf-8' codec can't decode byte 0x9e in position 0: invalid start byte
  ```
  ```python
  private_key = (
      key
      if re.match(r"(-+(BEGIN|END) [A-Z ]+-+)", key)
      else base64.b64decode(key).decode("utf-8")
  )
  ```
  When `key` doesn't match the PEM header regex, it is treated as base64 and decoded as UTF-8; non-UTF8 base64 input raises an uncaught `UnicodeDecodeError`. No try/except around the action handler.
- **Impact**: An operator pasting a binary-format key (DER instead of PEM, or corrupted data) gets an unhelpful traceback instead of a clear "invalid key format" error.
- **Fix**: Wrap in try/except `(binascii.Error, UnicodeDecodeError, ValueError)` and fail the action with a clear message. Alternatively, try PEM first, then DER.
- **Linter rule**: "`base64.b64decode` result decoded as utf-8 without surrounding try/except" — mechanically checkable.

### Scale-up to new units fails with `upgrade-relation-changed` error on Juju 4.0
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/data_platform_libs/v0/upgrade.py:960-963`, invoked via `src/events/upgrade.py`
- **Evidence**: Scaling from 3 to 5 units on Juju 4.0 (rv-zk-deep) caused both new units to fail repeatedly with `hook failed: upgrade-relation-changed` per `show-status-log`. `DataUpgrade.on_upgrade_changed` (line ~960) does `top_unit_id = self.upgrade_stack.pop()` then reads `self.peer_relation.data[top_unit].get("state")`; for a newly joining unit the upgrade relation data may not yet carry `state: idle` from `_on_upgrade_created`, and `upgrade-relation-changed` can fire before `upgrade-relation-created` in some event orderings. Re-attempts to reproduce on a different model (rv-zk-scale4, both Juju versions) were blocked earlier by an unrelated PVC/disk-space limit in the test environment, so this finding rests on the single rv-zk-deep observation `(unverified further)`.
- **Impact**: Scaling up a production ZooKeeper cluster (e.g. 3→5 for higher fault tolerance) can permanently fail on new units, which never recover. Scale-down is then also blocked because Juju 4.0 won't reduce StatefulSet replicas while units are in error state — a multi-step manual recovery (`juju resolve` each unit, then re-scale).
- **Fix**: In `on_upgrade_changed`, check whether the unit has completed `_on_upgrade_created` (has `state` in its own relation data) before popping the upgrade stack; defer or set `state: idle` if missing. Guard `self.upgrade_stack.pop()` against an empty stack before, not after, popping.
- **Linter rule**: not mechanically checkable — requires reasoning about event ordering.

### `pre-upgrade-check` permanently blocks password rotation on single-unit clusters
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/data_platform_libs/v0/upgrade.py:808` (`self.upgrade_stack = built_upgrade_stack`), `src/events/password_actions.py:60` (`if not self.charm.upgrade_events.idle`)
- **Evidence**: Running `pre-upgrade-check` on a single-unit ZK cluster writes `upgrade-stack: [0]` to the upgrade peer relation data (`upgrade.py:808`). `ZKUpgradeEvents.idle` (`upgrade.py:71`) then returns `not bool([0])` = `False`. The `set-password` action checks `if not self.charm.upgrade_events.idle:` and fails with "Cannot set password while upgrading (upgrade_stack: [0])". The stack can never drain because `on_upgrade_changed` (`upgrade.py:960-1000`) only progresses when `top_state` is `"completed"` or `"ready"`/`"upgrading"`, but the unit's own state is `"idle"` — neither branch fires. The stack persists in peer relation data forever with no recovery action. Notably, a later `tick-time=3000` config change still succeeded despite the same `idle` gate existing on `_on_cluster_relation_changed` — the reason this path wasn't also blocked is unclear from testing.
- **Impact**: A routine pre-upgrade health check on a single-unit cluster permanently disables password rotation, with no documented recovery short of manually editing peer relation data or redeploying.
- **Fix**: In `_on_pre_upgrade_check_action`, skip writing the upgrade stack when `len(built_upgrade_stack) <= 1`. Alternatively, `on_upgrade_changed` should treat `top_state == "idle"` as immediately completed. Document that `pre-upgrade-check` should only be run on multi-unit clusters.
- **Linter rule**: not mechanically checkable.

### Juju 4.0 scale-down blocked when units are in error state
- **Severity**: medium
- **Kind**: bug
- **Where**: Juju 4.0 StatefulSet controller behaviour, not charm code
- **Evidence**: After the scale-up 3→5 failure left units 3 and 4 in error state, `juju scale-application zookeeper-k8s 3` was acknowledged (twice) but `kubectl get sts zookeeper-k8s -o jsonpath='{.spec.replicas}'` still returned `5`; `juju status` showed `5/3`. `juju remove-unit zookeeper-k8s/3` returned "k8s models do not support removing named units." The only recovery found was `juju resolve` on each unit followed by re-scaling.
- **Impact**: This appears to be primarily a Juju 4.0 bug, but it interacts with the charm's `upgrade-relation-changed` failure to create a full scale-down deadlock with no documented recovery path.
- **Fix**: Charm-side, prevent the `upgrade-relation-changed` failure in the first place (see finding above). Juju-side, error-state units on K8s should still be terminable by the StatefulSet controller.
- **Linter rule**: not mechanically checkable.

### `_on_cluster_relation_changed` is an over-wide catch-all handler
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:225`
- **Evidence**: A single method is observed for six event types:
  ```python
  self.framework.observe(getattr(self.on, "update_status"), self._on_cluster_relation_changed)
  self.framework.observe(getattr(self.on, "leader_elected"), self._on_cluster_relation_changed)
  self.framework.observe(getattr(self.on, "config_changed"), self._on_cluster_relation_changed)
  self.framework.observe(getattr(self.on, "cluster_relation_changed"), self._on_cluster_relation_changed)
  self.framework.observe(getattr(self.on, "cluster_relation_joined"), self._on_cluster_relation_changed)
  self.framework.observe(getattr(self.on, "cluster_relation_departed"), self._on_cluster_relation_changed)
  ```
  The method carries `# noqa: C901` (complexity suppression) and spans ~150 lines with per-event-type conditionals. Open issue #137 (crashes on `leader-elected`/`zookeeper-relation-changed` in Spark CI, not reproduced in this review) is consistent with a race in this handler.
- **Impact**: Reasoning about event ordering and races is difficult; e.g. a `config_changed` rolling restart interleaved with a departing unit's `cluster_relation_departed` may produce unexpected behaviour. SAN checking also runs during `leader_elected` for no clear reason.
- **Fix**: Split into per-event-type handlers calling a shared reconciliation method; `leader_elected` shouldn't need to check SANs or trigger rolling restarts.
- **Linter rule**: "hook handler observes more than 2 distinct event types" — mechanically checkable.

### `apply_service` swallows critical k8s API errors
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/k8s.py:41-50`
- **Evidence**:
  ```python
  def apply_service(self, service: Service) -> None:
      try:
          self.client.apply(service)
      except ApiError as e:
          if e.status.code == 403:
              logger.error("Could not apply service, application needs `juju trust`")
              return
          if e.status.code == 422 and "port is already allocated" in str(e.status.message):
              logger.error(e.status.message)
              return
          else:
              raise
  ```
  The 403 case returns silently. The caller (`charm.py:189`) sets `Status.SERVICE_UNAVAILABLE` before calling `apply_service`, but the next hook overwrites that status with whatever it computes, masking the failure.
- **Impact**: An operator configures `expose-external=nodeport`, sees active status, but the service was never created because `juju trust` was missing — with no persistent, visible feedback.
- **Fix**: Return a result from `apply_service`/`remove_service`, or set a specific blocking status that persists until resolved.
- **Linter rule**: not mechanically checkable.

### `loadbalancer-extra-annotations` config is dead — defined but never read
- **Severity**: low
- **Kind**: bug
- **Where**: `config.yaml:26-28` (defined), never referenced in `src/` or `lib/`
- **Evidence**: `grep -rn loadbalancer_extra_annotations src/ lib/` returns no results. Described in `config.yaml` as "String in json format to describe extra configuration for load balancers", but `build_loadbalancer_service()` (`src/managers/k8s.py:103`) never reads it. Appears in `juju config` output but setting it has no effect.
- **Impact**: Operator sets this config expecting annotations to appear on the LoadBalancer service and gets nothing, silently.
- **Fix**: Implement it in `build_loadbalancer_service()` (parse JSON, apply as Service annotations), or remove the option and document the removal.
- **Linter rule**: "`config.yaml` key never referenced in Python source" — mechanically checkable.

### TLS certificate files left on disk after relation removal
- **Severity**: low
- **Kind**: bug
- **Where**: `src/events/tls.py:139-140` — no cleanup on `certificates_broken`
- **Evidence**: After removing the TLS relation from a running cluster, `zoo.cfg` was correctly sanitised (no SSL lines), but `keystore.p12`, `truststore.jks`, `server.pem`, `ca.pem`, `bundle.pem`, and `server.key` all remained on disk. `_on_certificates_broken` sets `unit_server.update({"certificate": "", "ca": ""})` but does not delete the files.
- **Impact**: Stale TLS material remains accessible to the workload process — minor security hygiene issue.
- **Fix**: Delete TLS files in `_on_certificates_broken` or via `tls_manager.remove_stores()`.
- **Linter rule**: not mechanically checkable.

### Plaintext passwords written to client relation data
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:561-568`
- **Evidence**: `client.update({"password": client.password, ...})` writes plaintext into the relation data bag, while peer-data passwords use Juju secrets (`DataPeerUnitData` with `additional_secret_fields=SECRETS_UNIT`).
- **Impact**: Inconsistent security posture — peer passwords are secret, client-facing passwords are plaintext (still scoped to related applications, but weaker).
- **Fix**: Use Juju secrets for client relation passwords, or document the reason for the difference.
- **Linter rule**: partially checkable via pattern matching on `"password"` in relation writes.

### `_on_install` sets workload version before container is connectable
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:221`
- **Evidence**: `self.unit.set_workload_version(self.workload.get_version())` at install time returns `""` because `self.workload.alive` is `False` at that point. The version is corrected later.
- **Fix**: Guard with `if self.workload.container_can_connect`, or remove the call from install.
- **Linter rule**: "`set_workload_version` called when container `can_connect` is False" — mechanically checkable.

### `_get_current_sans` re-raises exceptions uncaught upstream
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/tls.py:82-87`
- **Evidence**: `except … as e: logger.error(e.stdout); raise e` — logs then re-raises. The caller (`_on_cluster_relation_changed`) has no try/except for this path, so a corrupt `server.pem` causes a hook failure instead of `BlockedStatus`.
- **Fix**: Return `None` instead of re-raising; the caller already handles `None`.
- **Linter rule**: "except block re-raises the same exception it logged" — mechanically checkable.

### `config_changed` log-level check is a fragile substring match
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/config.py:399`
- **Evidence**: `log_level_changed = self.log_level not in "".join(self.current_env)` checks a substring against the entire environment file contents, and would match e.g. `INFO` appearing inside an unrelated env var.
- **Fix**: Parse the env file and check only the `SERVER_JVMFLAGS` value.
- **Linter rule**: not easily mechanically checkable.

### `K8sManager` methods lack retry for transient errors
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/k8s.py:169-182`, `186-196`
- **Evidence**: `get_node_ip`, `get_nodeport`, `get_loadbalancer` call `lightkube` without retry; only the 403 case is specifically handled elsewhere.
- **Fix**: Add retry decorators for transient k8s API errors.
- **Linter rule**: not mechanically checkable.

### `_on_zookeeper_pebble_ready` ignores which event fired it
- **Severity**: nit
- **Kind**: bug
- **Where**: `src/charm.py:330`
- **Evidence**: The handler is observed for `upgrade_charm`, `start`, and `zookeeper_pebble_ready` but treats them identically; `upgrade_charm` during an active upgrade should delegate to `ZKUpgradeEvents` rather than re-initialising the server.
- **Fix**: Route `upgrade_charm` to the upgrade handler explicitly.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Model-based state management** (`src/core/models.py`): `ZKServer`, `ZKClient`, `ZKCluster` wrapping `RelationState` give typed, testable access to relation data.
- **HA integration tests** (`tests/integration/ha/test_ha.py`): SIGKILL, SIGTERM, SIGSTOP/CONT, full cluster crash, network partition, pod reschedule, scale-down/up, all with continuous write verification. Exceptional depth.
- **TLS truststore management** (`src/managers/tls.py:163-189`): three-step replace strategy (chown → rename → import → delete → chown back) avoids empty-truststore windows that could crash ZK's internal watcher thread.
- **Backup streaming adapter** (`src/managers/backup.py:235-255`): `_StreamingToFileSyncAdapter` wraps `httpx.stream` as a file-like object for boto3 upload, avoiding full snapshot materialisation in memory.
- **Structured config with enums** (`src/core/stubs.py`): `LogLevel` and `ExposeExternal` as `str, Enum` with pydantic validation.
- **Ordered unit startup** (`src/core/cluster.py:271-289`): `next_server` ensures units join quorum in unit-id order, avoiding race conditions.

## Common-practice notes

- **Follows convention**: standard `src/` layout, `charmcraft.yaml` with poetry plugin, library layout under `lib/charms/.../v<N>/`.
- **Drifts from convention**:
  - Two-level workload inheritance (`src/core/workload.py` base + `src/workload.py` K8s impl) — unusual but functional.
  - `_restart` is both a charm callback and called by `RollingOpsManager`.
  - Config validation crash-on-init (from `TypedCharmBase`) is shared with other data-platform charms — an ecosystem-wide pattern that should change.
- **Image pinning**: `metadata.yaml` resources pin the OCI image by SHA256 digest — good practice.
- **Dependencies**: ZooKeeper 3.9.2, Java 11, stable boto3/cryptography/kazoo versions.

## Tests

### Unit tests — ran, 159 passed, 10 skipped (29s), 71% coverage
- Strong coverage: `src/charm.py` (85%), `src/core/models.py` (88%), `src/core/cluster.py` (82%), `src/managers/config.py` (81%).
- Weak coverage: `src/managers/backup.py` (24%), `src/managers/tls.py` (34%), `src/managers/k8s.py` (38%), `src/events/upgrade.py` (64%).
- 10 skipped: VM snap paths and upgrade state machine tests needing newer `ops.testing` features.
- Uses `scenario` (ops testing library) extensively — modern approach.
- Test gaps found:
  - `test_set_tls_private_key` (`tests/unit/test_tls.py:567`) only tests a valid PEM key; no test for invalid binary/UTF-8 input.
  - No unit test for invalid config values causing a pydantic crash (a `scenario` test with `state.config = {"tick-time": "-1"}` would catch it).
  - No test for `expose-external` service creation failure without `juju trust`.
  - No test covering `_on_cluster_relation_changed` interleaving config changes with relation departures.

### Integration tests — design review only (not run; requires k8s cluster + charms)
- Test files: `test_charm.py`, `test_provider.py`, `test_password_rotation.py`, `test_tls.py`, `test_backup.py`, `test_upgrade.py`, `ha/test_ha.py`, `ha/test_replication.py`.
- Assert actual behaviour (data integrity, JAAS correctness, cert chain verification), not just active/idle.
- Gap: no integration test for scale-up from 3→5 with an existing upgrade relation — would have caught the `upgrade-relation-changed` failure.

### Lint tools — all clean
`ruff`: clean | `codespell`: clean | `black`: clean | `pyright`: 0 errors, 0 warnings | `tox -e lint`: all pass

## Docs

- **README.md**: comprehensive, covers deploy, scaling, TLS, monitoring, password rotation; matches observed behaviour.
- **docs/index.md**: structured tutorial/how-to/explanation/reference docs on readthedocs.
- **CONTRIBUTING.md**: clear development setup, tox environments, build/deploy steps.
- **Missing**: `loadbalancer-extra-annotations` has no docs beyond "String in json format" — no example, and (per findings above) is never read by the code.
- **Doc/reality mismatch**: README recommends `-n 5` for production but the example shown uses 3.

## Open questions

1. **Issue #137** (crashes on `leader-elected` in Spark CI): not reproduced. Likely a race in the catch-all handler under CI timing; a concurrent-event stress test would settle this.
2. **Issue #139** (`logging-relation-changed` hook failure): not reproduced on rev 78 with grafana-agent-k8s 1/stable, possibly fixed. A `# FIXME: update when rebased on merged` comment near `charm.py:120` about log file paths suggests remaining technical debt in the logging integration.
3. **Issue #135** (blocked after deploy): likely the transient "cluster not stable - not all units related" state; could be CI resource contention.
4. **S3 backup region handling** (`src/managers/backup.py:61-70`): `_construct_endpoint` resolves AWS endpoints from botocore data — likely fragile with non-standard endpoints (MinIO, Ceph). Needs a real S3/alternative-endpoint test to verify (unverified).
5. **Scale-up `upgrade-relation-changed` failure**: reproduced once on Juju 4.0 (rv-zk-deep); retest attempts on both Juju versions were blocked by an unrelated disk-space limit before reaching that code path, so whether it also affects Juju 3.6, or is timing-dependent, remains open.
