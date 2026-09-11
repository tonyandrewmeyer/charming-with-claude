# kafka-k8s

A mature, feature-rich Kafka K8s charm from the Canonical Data Platform team: clean role-based architecture, extensive docs, sophisticated test setup. It deploys and runs correctly on Juju 3.6 (K8s) — TLS via self-signed-certificates, COS observability, kafka-client provider relations, config handling, scale-up/down, and in-place refresh all work. But **on Juju 4.x (K8s) the charm is completely undeployable**: an unhandled `OSError: [Errno 19] No such device` from an unconditional `SO_BINDTODEVICE` setsockopt call crashes every unit on `pebble-ready`. On top of that, config validation errors crash the charm instead of setting `BlockedStatus`, and the crash poisons *every* subsequent hook (not just `config-changed`) because validation runs unconditionally in `__init__`. The Pebble layer also lacks `on-failure: restart`, so a crashed Kafka process doesn't self-heal. A maintainer should first fix the Juju 4.x `SO_BINDTODEVICE` crash (charm is unusable there otherwise), then wrap config validation in try/except to produce `BlockedStatus`, then add `on-failure: restart` to the Pebble service. The `controller-passwrod` typo is a one-line fix that likely breaks balancer authentication. Architecture and lint/test hygiene are otherwise strong.

| | |
|---|---|
| Repo | `canonical/kafka-k8s-operator` @ `cc8a5ba` (2026-06-28) |
| Charms | kafka-k8s |
| Substrate | k8s |
| Deployed | yes — Juju 3.6 (concierge-k8s-3): 4/stable rev 111 reached `active/idle`; Juju 4.x (concierge-k8s-4): 4/stable rev 111 and 4/edge rev 116 both failed to deploy (error-looping on `OSError: [Errno 19] No such device`) |
| Reviewed | 2026-07-28 |

## What it does

Deploys Apache Kafka 4.1.1 on Kubernetes using KRaft consensus (no ZooKeeper dependency). Supports running as a combined broker+controller, or as separate controller and broker clusters. The charm provides:

- Combined or separated broker/controller/balancer roles via `roles` config
- Automatic internal TLS (self-signed certs) with optional external TLS via `certificates` relation
- mTLS client authentication via `client-cas` relation
- SASL/SCRAM-SHA-512 and OAUTHBEARER authentication
- Cruise Control auto-balancing with `rebalance` action
- External access via Kubernetes NodePort services
- COS integration (metrics, dashboards, Loki log forwarding)
- Juju 3 secrets-based password management
- In-place refresh with `charm-refresh` library

## Deployment log

**Attempt 1: 4/edge rev 116, separate controller+broker, Juju 4.x**
```bash
juju add-model rv-kafka-k8s --controller concierge-k8s-4
juju deploy kafka-k8s --channel 4/edge --config roles="controller" --trust -n 1 controller
juju deploy kafka-k8s --channel 4/edge --config roles="broker" --trust -n 1 broker
juju integrate broker:peer-cluster controller:peer-cluster-orchestrator
juju integrate controller:peer-cluster broker:peer-cluster-orchestrator
```
Result: Both units error-looping. `controller/0` fails on `peer-cluster-relation-joined`, `broker/0` fails on `peer-cluster-orchestrator-relation-changed`. Traceback: `OSError: [Errno 19] No such device` at `core/models.py:338` in the `ip` property, called from `update_peer_ip_address()` → `update_ip_addresses()` → `_on_start()`.

**Attempt 2: 4/stable rev 111, combined broker+controller, Juju 4.x**
```bash
juju destroy-model rv-kafka-k8s --force --no-wait --destroy-storage --no-prompt
juju add-model rv-kafka-k8s --controller concierge-k8s-4
juju deploy kafka-k8s --channel 4/stable --config roles="broker,controller" --trust -n 1
```
Result: Unit stuck `waiting: waiting for internal TLS setup`, then error-loops on `kafka-pebble-ready` with the identical `OSError: [Errno 19] No such device`. Confirmed: bug exists in both stable and edge.

**Attempt 3: 4/stable rev 111, combined broker+controller, Juju 3.6**
```bash
juju add-model rv-kafka-k8s-3 --controller concierge-k8s-3
juju deploy kafka-k8s --channel 4/stable --config roles="broker,controller" --trust -n 1
```
Result: **SUCCESS.** Reached `active/idle` in ~30 seconds from `kafka-pebble-ready`. Kafka 4.1.1 started, internal TLS with self-signed certs configured, SCRAM-SHA-512 auth configured for internal and controller listeners.

**Attempt 4: self-signed-certificates integration, Juju 3.6**
```bash
juju deploy self-signed-certificates --channel edge ss-cert
juju integrate kafka-k8s:certificates ss-cert:certificates
```
Result: Succeeded. Charm detected 4 changed properties, performed a rolling restart, remained active. External TLS certificates provisioned.

**Attempt 5: scale up to 2, then back to 1**
```bash
juju scale-application kafka-k8s 2  # both units active
juju scale-application kafka-k8s 1  # unit 1 removed cleanly
```
Result: Both directions worked. Second unit joined the cluster; on scale-down the departing unit was removed with a rolling restart of the remaining unit.

**Attempt 6: config validation failure injection**
```bash
juju config kafka-k8s profile=invalid compression-type=invalid roles=invalid log-retention-ms=notanumber
```
Result: Charm went to `error` state with a Pydantic `ValidationError` traceback instead of a clean `BlockedStatus` with actionable messages. Error loop continued until valid config restored; then charm returned to `active`.

**Attempt 7: kill workload process**
```bash
kubectl exec -n rv-kafka-deep kafka-k8s-0 -c kafka -- pebble stop kafka
```
Result: After ~3 minutes (next update-status cycle), charm set `blocked: service not running`. Workload was **not auto-restarted** — the `healthy` gate in `_on_update_status` (`broker.py:303`) returns early when `workload.active()` is False, preventing the `config_changed.emit()` that would trigger a restart. After manual `pebble start kafka`, the next update-status detected the running service, `healthy` returned True, `config_changed` fired, and the charm recovered to `active`. The Pebble layer has `startup: enabled` but no `on-failure: restart`.

**Attempt 8: grafana-agent-k8s and data-integrator integration, Juju 3.6**
```bash
juju deploy grafana-agent-k8s --channel stable gragent
juju deploy data-integrator --channel stable dataint --config topic-name=test-topic
juju integrate kafka-k8s:metrics-endpoint gragent:metrics-endpoint
juju integrate kafka-k8s:grafana-dashboard gragent:grafana-dashboards-consumer
juju integrate kafka-k8s:logging gragent:logging-provider
juju integrate kafka-k8s:kafka-client dataint:kafka
```
Result: All integrations succeeded. Loki log forwarding configured in the Pebble plan. data-integrator received kafka credentials (username, password, tls, tls-ca, uris) and reached `active`. Metrics-endpoint and grafana-dashboard relations connected successfully.

**Attempt 9: relation removal**
```bash
juju remove-relation kafka-k8s:certificates ss-cert:certificates
juju remove-relation kafka-k8s:kafka-client dataint:kafka
```
Result: Removing certificates was graceful — internal TLS continued, `certificates-relation-broken` ran cleanly, charm stayed `active`. Removing kafka-client triggered a rolling restart (8 properties changed) — heavy but likely required for SASL config cleanup.

**Attempt 10: config failure — empty-string → None bug**
```bash
juju config kafka-k8s ssl-principal-mapping-rules=""
```
Result: Crashed with `ValidationError: ssl_principal_mapping_rules — Input should be a valid string [type=string_type, input_value=None]`. Setting a string config field to empty string causes Juju to pass `None` through to Pydantic, which the `str` annotation rejects — a distinct bug from the general validation crash.

**Attempt 11: scale-test 2→1 (second round)**
```bash
juju scale-application kafka-k8s 2  # both units active
juju scale-application kafka-k8s 1  # unit 1 removed cleanly
```
Result: Confirmed again. Scale-up ~45 seconds, scale-down ~15 seconds. Remaining unit performed a rolling restart after scale-down.

**Attempt 12: refresh 4/stable rev 111 → 4/edge rev 116, Juju 3.6**
```bash
juju refresh kafka --channel 4/edge
```
Result: Succeeded. Pre-refresh-check passed, stop hook ran, container restarted with new revision, and after ~30 seconds of TLS setup/restart the unit reached `active`. A brief transient `blocked: service not running` self-resolved. Confirms in-place refresh works on Juju 3.6.

**Attempt 13: kill -9 the JVM process directly (hard kill)**
```bash
kubectl exec -n rv-kafka-d2 kafka-0 -c kafka -- bash -c "kill -9 \$(pgrep -f 'kafka.Kafka')"
```
Result: Kubernetes detected process exit and restarted the container; Pebble started Kafka again. Kafka logged `DUPLICATE_BROKER_REGISTRATION` for ~12 seconds before recovering, since the crash left the old broker session uncleaned. Charm remained `active` throughout (pod restart faster than the 5-minute update-status interval). Operational concern: a hard JVM crash causes ~12s unavailability plus pod restart time, versus near-instant recovery with Pebble-level `on-failure: restart`.

**Attempt 14: expose-external=nodeport config**
```bash
juju config kafka expose-external="nodeport"
```
Result: Succeeded. Created `kafka-0-sasl-plaintext-scram` (NodePort, port 29092→31290) and `kafka-bootstrap` (NodePort, ports 29092-29096 for all SASL mechanisms). Charm performed a rolling restart to apply new listeners.

**Attempt 15: extreme config value (log-retention-ms=-99999)**
```bash
juju config kafka log-retention-ms="-99999"
```
Result: Crashed with `ValidationError: log_retention_ms — Value error, Value below -1`. Crash occurred on a **subsequent `secret-changed` hook**, not `config-changed`. `juju status` misleadingly showed `hook failed: "secret-changed"`. Every secret-changed retry triggered `__init__` → `ClusterState` → `charm.config.roles` → full Pydantic validation → crash. Cleared with `juju config kafka log-retention-ms="-1"` + `juju resolve`. Distinct crash path: invalid config poisons *any* subsequent hook, not just `config-changed`.

**Attempt 16: remove certificates relation (Juju 3.6, 4/edge)**
```bash
juju remove-relation kafka:certificates ss-cert:certificates
```
Result: Graceful. `certificates-relation-departed`/`-broken` ran cleanly, charm triggered a rolling restart, reached `active`. Internal TLS continued with self-signed certs. No crash.

**Attempt 17: rebalance action (non-balancer role)**
```bash
juju run kafka/0 rebalance mode=full
```
Result: Correctly rejected: `error: Action must be run on an application with balancer role`. Clean action failure via `fail`, not a charm crash.

**Attempt 18: force-refresh-start and resume-refresh actions (not run)**

Not exercised — require a multi-unit refresh-in-progress state to be meaningful. Schemas are well-defined with sensible defaults.

## Observed behaviour

**Juju 3.6 (working deployment):**

- Deployment time: ~30 seconds from pebble-ready to active
- OCI image: 318 MB, pulls quickly
- Memory usage: 555 MiB (Pod), 1.4 CPU cores
- Pebble service: single `kafka` service, enabled, `override=replace`, running as `kafka:kafka`
- Internal TLS: self-signed CA with per-unit certificates in `/etc/kafka/` (`peer-keystore.p12`, `peer-truststore.jks`, `peer-bundle.pem`, etc.)
- Authentication: SCRAM-SHA-512 for internal broker and controller listeners. Super users: `controller`, `operator`, `replication`
- Listeners: `INTERNAL_SASL_SSL_SCRAM_SHA_512://0.0.0.0:19093`, `CONTROLLER_SASL_SSL_SCRAM_SHA_512://0.0.0.0:9098`
- Advertised listeners use k8s service DNS: `kafka-k8s-0.kafka-k8s-endpoints:19093`
- Config diffing via `properties_changed()` (XOR of current vs desired properties) — only changed properties trigger restart
- TLS integration: 4 properties changed, rolling restart, status stayed active
- Scale-up: second unit joins, 8 properties changed
- Scale-down: clean removal, rolling restart of remaining unit, logs `potential data loss due to storage removal without replication` warning
- Hook count: ~10 hooks from install to active (install, leader-elected, pebble-ready, secret-changed, secret-remove, storage-attached, config-changed, start, update-status, relation hooks)
- `juju debug-log` shows on every secret-changed: `"Received secret cluster.kafka-k8s.unit but couldn't parse, seems irrelevant"` — noisy but benign
- After refresh rev 111→116, start hook briefly reports `blocked: service not running` before self-recovering — a race between the start hook's health check and service readiness
- **Hard JVM kill recovery**: SIGKILL on the JVM causes a container restart; Kafka logs `DUPLICATE_BROKER_REGISTRATION` for ~12s before the old session times out and the new instance registers. `on-failure: restart` at the Pebble level would likely eliminate this gap (a Pebble-restarted process would re-use the same session)
- `expose-external=nodeport` creates `kafka-bootstrap` (NodePort, all SASL mechanism ports) and `kafka-0-sasl-plaintext-scram` (per-unit NodePort) — external exposure works as documented
- **Config validation poisons all hooks**: invalid config (e.g. `log-retention-ms=-99999`) crashes *every subsequent hook*, including `secret-changed`, because `ClusterState.__init__` reads `charm.config.roles`, triggering full Pydantic validation on every hook dispatch. `juju status` reports the triggering hook name, not the actual error, hindering diagnosis
- **Lint**: `tox -e lint` passes cleanly — ruff 0 issues, black all formatted, pyright 0 errors/0 warnings, codespell 0 issues (though `controller-passwrod` at `src/literals.py:183` is not caught by codespell's dictionary). 799 deprecation warnings from Pydantic `@validator` (18 uses), `JujuVersion.from_environ()` (3 library files), and `config.dict()` (`config.py:822`)

**Juju 4.x (failed deployment):**

- The `network_interface` property (`core/models.py:322`) returns a non-empty interface name from `model.get_binding()` that does not exist in the workload container's network namespace (container has only `eth0` and `lo`)
- The `ip` property (`core/models.py:338`) calls `s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, interface_name)`, raising `OSError: [Errno 19] No such device`
- Traceback path: `_on_start` → `update_ip_addresses` → `update_peer_ip_address` → `self.ip or self.internal_address` — the `ip` property raises before `or` can fall back to `internal_address`
- No try/except wraps the `ip` property, `update_peer_ip_address`, `update_ip_addresses`, or `_on_start`
- The hook errors out; Juju retries every ~10 seconds indefinitely
- **The charm never reaches a `BlockedStatus` with an actionable message** — it just crashes
- Juju 4.x-specific: on Juju 3.6, `get_binding()` returns an interface name that exists in the container (`eth0`); on Juju 4.x, it returns a different name that doesn't exist

**Config validation failure (general):**

- Invalid config is rejected by Pydantic's `CharmConfig` via `ClusterState(self, substrate=self.substrate)` at `src/charm.py:70`
- `ValidationError` is raised unhandled, producing a traceback instead of `BlockedStatus`
- The error message lists all validation failures but is buried in the traceback — operators need `juju debug-log`
- The error-loop continues indefinitely until valid config is restored
- Misleading `juju status`: shows the triggering hook name, not the actual failure (e.g. "hook failed: kafka-client-relation-joined")
- Restoring valid config after an error in a non-config-changed hook may require `juju resolve`

**Config validation failure (empty-string → None):**

- Setting a string config field to `""` causes Juju to pass `None` to Pydantic, which rejects `None` for a `str`-typed field
- Observed on `ssl_principal_mapping_rules`
- Distinct from the general validation crash: the operator sets what looks like a valid value (empty string, explicitly handled by the validator with `return []`), but Juju transforms it to `None` first

**Workload kill recovery gap:**

- After `pebble stop kafka`, `update_status` detects the stopped service ~3 minutes later via `healthy` → `workload.active()` → `False`
- `healthy()` sets `SERVICE_NOT_RUNNING` and returns `False`
- `_on_update_status` (`broker.py:303`): `not self.healthy` is `True` → returns immediately without emitting `config_changed`
- Pebble layer has `startup: enabled` but no `on-failure: restart`
- Manual `pebble start kafka` → next update-status → `healthy()` True → `config_changed.emit()` → reconciliation restarts/reconfirms service → charm recovers
- Two layers of non-recovery: Pebble won't restart crashed processes, and the charm won't emit the restart path when the workload is stopped
- Fix option 1 (Pebble): add `on-failure: restart`
- Fix option 2 (charm): in `_on_update_status`, attempt `workload.start()` before returning when service is detected stopped

## Findings

### Critical: `SO_BINDTODEVICE` setsockopt fails on Juju 4.x K8s, blocking all deployments
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/core/models.py:330` (and duplicate at line 248)
- **Evidence**: `s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, self.network_interface.encode("utf-8"))` — `network_interface` returns `interfaces[0].name` from `model.get_binding()`. On Juju 4.x this name doesn't exist in the workload container's network namespace. Observed: `OSError: [Errno 19] No such device` on every `kafka-pebble-ready` hook. Path: `_on_start` → `update_ip_addresses` → `update_peer_ip_address` → `self.ip or self.internal_address` — `ip` raises before `or` can fall back.
- **Impact**: Charm is completely undeployable on Juju 4.x K8s. Both 4/stable (rev 111) and 4/edge (rev 116) affected. Works on Juju 3.6 because the binding interface name matches the container's `eth0`.
- **Fix**: Wrap `setsockopt` in try/except falling back without `SO_BINDTODEVICE`, or use `self.internal_address` directly on k8s (reorder the `or` in `update_peer_ip_address` at line 997 to try `internal_address` first on k8s).
- **Linter rule**: "Call to `setsockopt` with `SO_BINDTODEVICE` must be guarded by try/except OSError" — mechanically checkable.

### Config validation errors crash the charm instead of setting BlockedStatus
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:70`
- **Evidence**: `self.state = ClusterState(self, substrate=self.substrate)` calls `charm.config.roles`, triggering Pydantic validation of `CharmConfig`. Invalid values (e.g. `profile=invalid`, `roles=invalid`) raise `pydantic_core.ValidationError` unhandled. Observed: 4 simultaneous validation errors produced a traceback instead of `BlockedStatus`.
- **Impact**: Operators see `error: hook failed: "config-changed"` with no actionable message; must read `juju debug-log`. Error-loop continues until valid config restored.
- **Fix**: Catch `ValidationError` in `__init__` or `_on_roles_changed` and set `BlockedStatus` with details, or wrap the `config` property of `TypedCharmBase`.
- **Linter rule**: "Pydantic model validation in charm `__init__` without try/except ValidationError" — mechanically checkable.

### Config validation poisons all hooks with misleading error messages
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:70` (via `charm.config.roles` → Pydantic validation)
- **Evidence**: After `log-retention-ms=-99999`, a *subsequent* `secret-changed` hook crashed with the same `ValidationError`. `juju status` showed `error: hook failed: "secret-changed"`, masking the actual config problem. `ClusterState.__init__` calls `charm.config.roles` on every hook, triggering full validation each time.
- **Impact**: A bad config value causes the charm to fail on arbitrary hooks (secret-changed, relation-changed, update-status) with error messages pointing to the wrong hook. Operator must read `juju debug-log`; charm may need `juju resolve` even after fixing config.
- **Fix**: Cache validated config in `__init__` with try/except setting `BlockedStatus`, or validate eagerly on `config-changed` and store a validation-failed flag checked by other hooks before accessing config.
- **Linter rule**: same as above — sub-case of the general config validation finding.

### Unit tests fail to collect: `KeyError: 'log_on_error'` in `test_tls_manager.py`
- **Severity**: high
- **Kind**: bug (test infrastructure)
- **Where**: `tests/unit/test_tls_manager.py:63`
- **Evidence**: `if kwargs["log_on_error"]:` uses direct key access instead of `.get()`. The call `_exec(KEYTOOL)` at line 65 doesn't pass `log_on_error`, causing `KeyError` during collection.
- **Impact**: Entire unit test suite fails to run in CI (`tox -e unit` → `Interrupted: 1 error during collection`).
- **Fix**: Change `kwargs["log_on_error"]` to `kwargs.get("log_on_error", False)`. **Confirmed working** — after the fix, 240 tests pass, 1 fails (`test_peer_cluster_trust`, requires keytool/JDK not installed on the test host), 50 skipped.
- **Linter rule**: "Direct key access on `**kwargs` dict without `.get()` fallback" — mechanically checkable.

### Workload crash auto-recovery is blocked by the `healthy` gate
- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/broker.py:270` and `src/events/broker.py:303`
- **Evidence**: Both `_on_update_status` and `_on_config_changed` check `self.healthy` first and return early if `False`; `healthy` checks `self.workload.active()`. Observed: after `pebble stop kafka`, charm set `SERVICE_NOT_RUNNING` but never restarted the workload — the `config_changed` emit that would trigger the restart is gated behind `healthy`.
- **Impact**: If Kafka crashes or is killed, the charm detects and reports it correctly but never attempts a restart; workload stays down until an external event or manual intervention.
- **Fix**: In `_on_update_status`, attempt to restart the workload when detected stopped before returning, or emit `config_changed` even when unhealthy.
- **Linter rule**: not established.

### Pebble service missing `on-failure: restart` — Kafka crashes are never auto-restarted
- **Severity**: high
- **Kind**: bug
- **Where**: Pebble layer rendered by `src/workload.py` and `src/events/broker.py`
- **Evidence**: Running Pebble plan shows `startup: enabled` with no `on-failure` key. Combined with the `healthy` gate above, a crashed Kafka process stays dead until an external event or human intervention.
- **Impact**: For a data platform charm, a significant reliability gap — no infrastructure-level auto-recovery from an OOM kill or crash.
- **Fix**: Add `on-failure: restart` (or `restart-after: 10s`) to the Pebble service definition — a one-line fix providing infrastructure-level auto-recovery.
- **Linter rule**: "Pebble service without `on-failure` in a production charm" — mechanically checkable if Pebble plans are available for static analysis.

### Hard JVM kill shows ~12-second DUPLICATE_BROKER_REGISTRATION recovery gap
- **Severity**: medium
- **Kind**: bug (operational)
- **Where**: Observed in live deployment; Pebble layer definition (lacks `on-failure: restart`)
- **Evidence**: After `kill -9` on the Kafka JVM, Kubernetes restarts the container. Kafka repeatedly logs `DUPLICATE_BROKER_REGISTRATION` for ~12 seconds because the old broker session hasn't timed out. No Pebble-level restart is available — only the full container restart path.
- **Impact**: A hard JVM crash causes a full container restart plus 12+ seconds of Kafka unavailability while the old session times out.
- **Fix**: Add `on-failure: restart` to the Pebble kafka service definition — would give sub-second recovery without triggering `DUPLICATE_BROKER_REGISTRATION`.
- **Linter rule**: not established.

### Dead `_on_peer_cluster_broken` handler — never registered
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/events/peer_cluster.py:182-226` (`meta.properties` removal at line 199)
- **Evidence**: `_on_peer_cluster_broken` is defined with cleanup logic (stop workload, remove `meta.properties`/`quorum-state` files) but never registered in `PeerClusterEventsHandler.__init__`, which only registers `relation_created`, `relation_changed`, `secret_changed`. No `relation_broken` handler is registered for either peer-cluster relation.
- **Impact**: When a peer-cluster relation breaks, cleanup logic never runs; workload keeps running, stale metadata files remain — could cause issues re-joining a different cluster.
- **Fix**: `self.framework.observe(self.charm.on[PEER_CLUSTER_RELATION].relation_broken, self._on_peer_cluster_broken)`.
- **Linter rule**: "Method named `_on_.*_broken` not registered as an observer" — mechanically checkable for common naming patterns.

### `_get_service` return type is `Service | None` but raises `ApiError` on 404
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/k8s.py:277-281`
- **Evidence**: `return self.client.get(res=Service, name=service_name)` annotated `Service | None`, but `lightkube` raises `ApiError` on 404, not `None`. Callers at lines 131 and 140 use `if not (service := self.get_service(...))` expecting `None`.
- **Impact**: When a listener/bootstrap service doesn't exist yet (e.g. initial deployment with `expose_external`), callers get an unhandled `ApiError` instead of `None`.
- **Fix**: Wrap `self.client.get()` in try/except `ApiError`, returning `None` on 404, or drop the `| None` annotation and let callers handle the exception.
- **Linter rule**: not established.

### `_handle_configuration_updates` restarts the workload on every storage event
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/events/broker.py:234-246`
- **Evidence**: `if any([properties_changed, self.charm.state.tls_rotate, self.charm.tls.certs_updated]):` followed by `self.charm.on[f"{self.charm.restart.name}"].acquire_lock.emit()` — fires a rolling restart on every storage-attached event regardless of whether log dirs actually changed.
- **Impact**: Adding new storage triggers a full broker restart even when unnecessary, causing avoidable downtime.
- **Fix**: Only trigger the restart for `StorageEvent` when log dirs have actually changed.
- **Linter rule**: not established.

### `_on_storage_detaching` blocks the event loop for up to 30 seconds per iteration
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/events/broker.py:384-388`
- **Evidence**: `while not self.balancer_manager.all_storages_drained(...): time.sleep(30)` — blocking loop inside a Juju hook handler, holding the event loop for an unbounded duration.
- **Impact**: During storage removal, the hook blocks for minutes (or indefinitely if draining never completes), preventing other hooks from running; Juju may treat the hook as hung.
- **Fix**: Use `event.defer()` and re-check on subsequent hook invocations, or a background-task pattern.
- **Linter rule**: "`time.sleep` in a hook handler" — mechanically checkable.

### `update_status` handler emits `config_changed` on every invocation
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/events/broker.py:308`
- **Evidence**: `self.charm.on.config_changed.emit()` called unconditionally in `_on_update_status` (every 5 minutes by default).
- **Impact**: `_on_config_changed` is heavy (re-renders config, checks TLS, updates credentials, reconciles clients); running it every 5 minutes when nothing changed is wasteful, though intentional for cases like IP change / late rack-awareness integration.
- **Fix**: Add a dirty flag or check whether relevant state actually changed before emitting.
- **Linter rule**: "`config_changed.emit()` in `update_status` handler without a change guard" — mechanically checkable.

### Unit test coverage gaps in key error paths
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_tls_manager.py` (peer_cluster_trust test), `src/managers/k8s.py:277-281` (`_get_service`), `src/core/models.py:338` (`ip` property), `src/events/broker.py:384-388` (`_on_storage_detaching` blocking loop)
- **Evidence**: `test_peer_cluster_trust` fails because `keytool`/JDK isn't installed on the test host — it calls real `subprocess.check_output` instead of mocking. `_get_service`'s `ApiError` path has 0% coverage. The `ip` property's `SO_BINDTODEVICE` crash path (the Juju 4.x bug) has 0% coverage — tests mock `workload.exec` but not `socket.setsockopt`. `_on_storage_detaching`'s `while time.sleep(30)` loop has 0% coverage.
- **Impact**: The critical Juju 4.x deployment-blocking bug had zero test coverage; the `_get_service` mismatch is also untested; CI cannot run `test_peer_cluster_trust`.
- **Fix**: Mock `socket.setsockopt`/`socket.socket` at conftest level; mock `lightkube` client exceptions for `_get_service`; install JDK/keytool in CI or mock keytool subprocess calls.
- **Linter rule**: not established.

### Typo in `BALANCER.requested_secrets`: `"controller-passwrod"`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/literals.py:183`
- **Evidence**: `"controller-passwrod"` should be `"controller-password"` in `BALANCER.requested_secrets`.
- **Impact**: A balancer role requesting controller secrets won't match the actual `controller-password` secret; balancer would fail to authenticate. (unverified — not exercised live in this review)
- **Fix**: Change `"controller-passwrod"` to `"controller-password"`.
- **Linter rule**: "Spell-check of string literals in secret field names" — codespell should catch this but currently doesn't (compound word not in its dictionary); could add a custom dictionary entry.

### `_on_secret_changed_event` is a no-op
- **Severity**: low
- **Kind**: bug
- **Where**: `src/events/peer_cluster.py:76`
- **Evidence**: `def _on_secret_changed_event(self, _: SecretChangedEvent) -> None: pass` — registered but does nothing.
- **Impact**: Secret changes on peer-cluster relations are silently ignored.
- **Fix**: Implement the handler, or remove the registration if intentionally inert.
- **Linter rule**: "Registered event handler with `pass` body" — mechanically checkable.

### Duplicated `network_interface`/`ip` property pair with identical `SO_BINDTODEVICE` bug
- **Severity**: low
- **Kind**: bug (code duplication)
- **Where**: `src/core/models.py:240-273` and `src/core/models.py:322-352`
- **Evidence**: Two separate classes have identical implementations of `network_interface` and `ip`, both with the same `SO_BINDTODEVICE` bug — copy-pasted code, so both need fixing independently.
- **Impact**: Bug fixes to one copy will miss the other; already the reason both copies share the Juju 4.x bug.
- **Fix**: Extract into a shared mixin/utility and apply the `try/except OSError` fix once.
- **Linter rule**: "Duplicate method body detected" — mechanically checkable via similarity/diff linters.

### `data_models.py` library metadata pins `pydantic<2` but charm uses `pydantic^2.11`
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/data_platform_libs/v0/data_models.py:173`
- **Evidence**: `PYDEPS = ["ops>=2.0.0", "pydantic>=1.10,<2"]` vs. `pyproject.toml`'s `pydantic = "^2.11"` and actual v2 API usage.
- **Impact**: Misleading metadata; `charmcraft pack` dependency resolution could install pydantic v1 alongside v2, creating subtle runtime conflicts.
- **Fix**: Update PYDEPS to `pydantic>=2.0` or remove the pin.
- **Linter rule**: "PYDEPS constraint contradicts pyproject.toml dependency" — mechanically checkable.

### `config.dict()` deprecated in `config.py:822`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/managers/config.py:822`
- **Evidence**: `for conf_key, value in self.config.dict().items():` — `PydanticDeprecatedSince20` warning; 40+ warnings generated in the test suite.
- **Impact**: Will break when Pydantic V3 drops `dict()`; currently generates test noise.
- **Fix**: `self.config.dict()` → `self.config.model_dump()`.
- **Linter rule**: already caught by Pydantic deprecation warnings in pytest.

### Pydantic V1 `@validator` decorators throughout structured config
- **Severity**: low
- **Kind**: lint
- **Where**: `src/core/structured_config.py:182,197,208,214,253`
- **Evidence**: `PydanticDeprecatedSince20: Pydantic V1 style @validator validators are deprecated` — 18 uses of the deprecated decorator.
- **Impact**: Will break when Pydantic V3 drops V1-style validators; already emits deprecation warnings.
- **Fix**: Migrate to `@field_validator`.
- **Linter rule**: already caught by pyright/pytest warnings.

### Deprecated `JujuVersion.from_environ()` called in multiple libraries
- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/tls_certificates_interface/v4/tls_certificates.py:1209`, `lib/charms/loki_k8s/v1/loki_push_api.py:2251`, `lib/charms/data_platform_libs/v0/data_interfaces.py:998`
- **Evidence**: `DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead` — 40+ warnings across the test suite.
- **Impact**: Test noise, eventual breakage when the deprecated API is removed.
- **Fix**: Use `self.model.juju_version`.
- **Linter rule**: already caught by Python deprecation warnings in pytest.

### `_handle_configuration_updates` uses `any()` with a list, not a generator
- **Severity**: nit
- **Kind**: performance
- **Where**: `src/events/broker.py:230`
- **Evidence**: `any([properties_changed, self.charm.state.tls_rotate, self.charm.tls.certs_updated])` constructs a full list before `any()` short-circuits.
- **Impact**: Each element is a property access that may involve relation-data reads; computing all three unconditionally is wasteful.
- **Fix**: `properties_changed or self.charm.state.tls_rotate or self.charm.tls.certs_updated`.
- **Linter rule**: "`any([...])` with non-trivial expressions" — mechanically checkable.

### `BALANCER_GOALS_TESTING` defined but only used in `config.py`; `HARD_BALANCER_GOALS` unused
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/literals.py:190-191`, `src/managers/config.py`
- **Evidence**: `HARD_BALANCER_GOALS` is never referenced anywhere; `BALANCER_GOALS_TESTING` is used only in `config.py` for the testing profile.
- **Impact**: Dead code adds maintenance burden.
- **Fix**: Remove or use `HARD_BALANCER_GOALS`.
- **Linter rule**: "Unused variable" — already caught by ruff/pyright.

## Worth copying

- **Clean role-based architecture**: `src/events/broker.py`, `src/events/controller.py`, `src/events/balancer.py` — each role gets its own event handler class, orchestrated from `charm.py`. Good pattern for multi-role charms; the fast exit in `BrokerOperator.__init__` when the role isn't active avoids registering irrelevant handlers.
- **`src/core/structured_config.py`**: Strong Pydantic validators — `extra_listeners` port range/uniqueness checks, `roles` validation against a known enum, secret URI format validation. The `ssl_principal_mapping_rules` validator that actually parses the rules is excellent.
- **`src/core/cluster.py`**: Centralized `ClusterState` encapsulating all relation-data access behind typed properties — a textbook reconciliation pattern; `ready_to_start` gates startup on prerequisites cleanly.
- **`src/managers/config.py` `Listener` class**: Clean modeling of Kafka listeners with protocol/scope/port logic; `advertised_listener` handles external vs internal addressing well.
- **`src/workload.py`**: Clean separation between `WorkloadBase` and concrete implementations; `CharmedKafkaPaths` role-parameterized path resolution is elegant.
- **`src/managers/auth.py`**: ACL diff-and-reconcile pattern (`acls_to_add`/`acls_to_remove` via set difference) is clean and correct; `delete_user` gracefully swallows "user does not exist".
- **`get-listeners` action**: Well-structured output (advertised-listeners, auth-mechanism, protocol, scope, port) — a model for action output design.
- **`charmcraft.yaml`**: Well-commented, explicit about implicitly staged files, clean multi-part build. `refresh_versions.toml` generation is a nice touch.
- **`tox.ini`**: Clean parameterized integration test environments with shared `pass_env`; `RETRIES=3` for flaky test retries is pragmatic.
- **Graceful TLS relation removal**: `certificates-relation-broken` runs cleanly, internal TLS continues, charm stays active — no crash, no restart.

## Common-practice notes

- **Follows**: `src/` layout with `core/`, `events/`, `managers/` is a common, well-executed pattern in the Data Platform team's charms. Use of `charm_refresh` for in-place upgrades matches team standard.
- **Follows**: `TypedCharmBase[CharmConfig]` from `data-platform-libs` is the established structured-config pattern.
- **Follows**: `data-platform-libs` v1 `Data`/`ProviderData`/`RequirerData` pattern used consistently.
- **Drifts (positive)**: Uses `ops >= 3.1.0` with `CollectStatusEvent`/`add_status()`, ahead of many charms still on ops 2.x `_on_collect_status`.
- **Drifts**: The `SO_BINDTODEVICE` pattern in `ip` is unusual — most k8s charms use `self.internal_address` or `socket.getfqdn()` directly; this looks like a VM-centric pattern that leaked into the k8s code.
- **Drifts**: `JAVA_HOME` hardcoded in the Pebble layer as `/usr/lib/jvm/java-21-openjdk-amd64` with a `FIXME` referencing issue #80; most modern rocks set `JAVA_HOME` in the image itself.
- **Drifts**: `CONTRIBUTING.md` is thorough and up-to-date, which is rare among charms.

## Tests

**Unit tests**: 18 test files in `tests/unit/`. Coverage includes auth, balancer, charm, config, controller manager, health, KRaft, provider, refresh, secrets, SSL principal mapping, structured config, TLS, TLS manager, workload. Uses `pytest` with `ops.testing` and monkeypatching.

**Test run results**: The `KeyError` bug in `test_tls_manager.py` was fixed during this review (line 63: `kwargs["log_on_error"]` → `kwargs.get("log_on_error")`). With the fix, `tox -e unit` passes 240 tests, fails 1 (`test_peer_cluster_trust` — requires `keytool`/JDK not installed on the test host), skips 50. Total coverage: **70%** (4194 statements, 1040 missed, 1306 branches, 1306 partials).

**Lint results**: `tox -e lint` passes completely clean: `ruff check` 0 issues on src/ and tests/, `black --check` 0 files would be reformatted, `pyright` 0 errors/0 warnings/0 informations, `codespell` 0 issues on src/ and lib/charms/kafka. 799 deprecation warnings during tests: Pydantic `@validator` (18 uses in `structured_config.py`), `JujuVersion.from_environ()` (3 library files), and `config.dict()` (`config.py:822`).

**Full per-file coverage**:

| File | Stmts | Miss | Cover |
|---|---|---|---|
| `src/charm.py` | 117 | 28 | 70% |
| `src/core/cluster.py` | 366 | 45 | 85% |
| `src/core/models.py` | 686 | 134 | 73% |
| `src/core/structured_config.py` | 169 | 7 | 94% |
| `src/events/broker.py` | 263 | 69 | 69% |
| `src/events/controller.py` | 99 | 14 | 79% |
| `src/events/peer_cluster.py` | 75 | 47 | 28% |
| `src/events/provider.py` | 129 | 40 | 67% |
| `src/events/refresh.py` | 60 | 25 | 53% |
| `src/events/tls.py` | 208 | 103 | 45% |
| `src/health.py` | 93 | 71 | 18% |
| `src/literals.py` | 120 | 1 | 99% |
| `src/managers/auth.py` | 127 | 30 | 71% |
| `src/managers/config.py` | 366 | 68 | 77% |
| `src/managers/k8s.py` | 106 | 55 | 39% |
| `src/managers/tls.py` | 326 | 105 | 63% |

**Coverage gaps by file**:

| File | Coverage | Notable untested paths |
|---|---|---|
| `src/events/peer_cluster.py` | 28% | Most relation-changed logic, the dead `_on_peer_cluster_broken` handler (lines 182-226) |
| `src/managers/k8s.py` | 39% | `_get_service` (the `ApiError` bug at line 278), `get_node_port`, `apply_service` |
| `src/events/tls.py` | 45% | TLS rotation (lines 156-184), certificate renewal, truststore rebuild (lines 190-236) |
| `src/events/refresh.py` | 53% | `run_pre_refresh_checks_after_1_unit_refreshed` (lines 59-79) |
| `src/health.py` | 18% | All VM health checks (class raises on k8s, untestable on k8s substrate) |
| `src/core/structured_config.py` | 94% | Paths where `expose_external` returns `None` on VM (line 187), `extra_listeners` empty handling (line 249) |
| `src/literals.py` | 99% | Single uncovered line: 148 |

**Integration tests**: 13 test files in `tests/integration/` covering deployment, KRaft, provider (v0/v1), scaling, password rotation, TLS (simple/complex), refresh, HA (broker/controller), auto-balance, and balancer (single/multi). Use `jubilant` (recently migrated from `pytest-operator`/`libjuju` per commit `841396f`). Not run — require a full K8s cluster with the charm deployed, and the charm cannot deploy on Juju 4.x.

**Test gaps**:
- No test for the `ip` property's `SO_BINDTODEVICE` failure path — `conftest.py`'s `patched_exec` fixture patches `workload.KafkaWorkload.exec` but not `socket.setsockopt`; the Juju 4.x crash path has zero coverage
- No test for `_get_service` returning `None` on missing service — the `ApiError` path is untested
- No test for `_on_storage_detaching`'s blocking `while` loop — `time.sleep(30)` path has zero coverage
- No test for `_on_peer_cluster_broken` — unregistered, so untestable via normal hook dispatch
- `update_status`'s `config_changed.emit()` side-effect is not tested for correctness or performance
- The empty-string → `None` config handling path (Juju-level transformation before Pydantic) has no test

## Docs

Extensive and well-organized: 37 files across `docs/tutorial/`, `docs/how-to/`, `docs/explanation/`, `docs/reference/`. `docs/reference/statuses.md` (11KB) is comprehensive. README is clear and up-to-date.

**Issues**:
- `docs/reference/statuses.md` includes VM-only statuses like `SNAP_NOT_INSTALLED` and `SYSCONF_NOT_POSSIBLE` — shouldn't appear in a k8s charm's reference docs
- Open issue #258: upgrade guide references a `pre-upgrade-check` action which doesn't exist (should be `pre-refresh-check`)
- Open issue #257: upgrade docs don't specify broker/controller upgrade ordering
- README's "Requirements" section cites "64GB of RAM, 24 cores" for production, while the charm container itself deploys with `memory: 1Gi` — a reasonable disconnect (charm container vs. workload) but worth clarifying in the docs
- `tox -e lint` passes cleanly (ruff/black/pyright/codespell) — an excellent baseline many charms don't meet

## Open questions

1. Why does `model.get_binding()` return different interface names on Juju 3.6 vs 4.x? On 3.6 it matches the container's `eth0`; on 4.x it returns a name absent from the container's network namespace. Likely a Juju 4.x change in how K8s network bindings are reported — the `SO_BINDTODEVICE` approach is fundamentally fragile on K8s regardless.
2. Does the `BALANCER.requested_secrets` typo actually break the balancer? Verifying requires deploying with the balancer role and checking Cruise Control's authentication to the controller.
3. Is the `update_status` → `config_changed` emit pattern intentional and documented as-is? The comment says it's for "IP change and late integration with rack-awareness charm," but the cost of full reconciliation every 5 minutes is significant, and the `healthy` gate blocking the restart path seems like an unintended side effect.
4. Why doesn't `_get_service` catch `ApiError`? Known gap in lightkube usage, or intentional (callers should ensure services exist first)?
5. Is `_on_peer_cluster_broken` intentionally dead? Its cleanup logic references ZooKeeper, suggesting a pre-KRaft leftover whose registration was dropped when KRaft support landed but the method itself was never removed.
6. Why is `_on_secret_changed_event` a no-op — placeholder for future work, or vestigial?
7. Should the Pebble layer have `on-failure: restart`? Kafka is stateful and should auto-restart after a crash; the `healthy` gate prevents the charm from doing so itself, so Pebble-level restart would be the natural recovery path. Was this omitted deliberately (e.g. to avoid restart loops on config errors)?
8. Why does `config.dict()` still call the deprecated method, and why does `data_models.py` still pin `pydantic<2`? Both fixes are mechanical; suggests the library metadata/config layer hasn't been revisited since the v1→v2 pydantic migration.
9. Why does invalid config crash `secret-changed` instead of `config-changed`? Because validation happens in `__init__` on every hook dispatch. Should validation be isolated to `config-changed` with a cached flag other hooks can check?
10. Why does `test_peer_cluster_trust` require real `keytool`? It calls `subprocess.check_output(['keytool', ...])` via `_exec` instead of mocking the workload exec path — un-runnable in CI without JDK. Should mock the keytool calls or skip cleanly when unavailable (currently fails, not skips).
