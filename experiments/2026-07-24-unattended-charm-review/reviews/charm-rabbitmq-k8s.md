# rabbitmq-k8s

A well-structured k8s operator for RabbitMQ 3.12: it deploys cleanly, clusters and scales correctly, and the codebase is lint-clean with solid test coverage (111 unit tests passing). But it has two real bugs a maintainer should fix before the next release: an unhandled config-validation exception that crashes the `config-changed` hook (requires manual `juju resolve` to recover), and a broken `HTTPError` check (`e.errno` instead of `e.response.status_code`) that can silently swallow authorization failures during operator-user bootstrap. Neither is exotic to trigger. Fix those two first; the rest (root-run notifier service, a TOCTOU gap in operator-user creation, thin docs) are real but lower-urgency.

| | |
|---|---|
| Repo | canonical/charm-rabbitmq-k8s @ b39e4a3 (2026-07-20) |
| Charms | rabbitmq-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4, 3.12/stable rev 71 |
| Reviewed | 2026-08-03 |

## What it does

Deploys RabbitMQ 3.12 on Kubernetes with k8s-native peer discovery. Exposes AMQP (5672), management HTTP (15672), and Prometheus metrics (15692). Provides `amqp` relation to consumer charms, `ingress` for management UI, `grafana-dashboard`, `metrics-endpoint`, and `logging` (loki_push_api). Manages quorum queue HA with configurable minimum replicas, automatic node/queue rebalancing, and a Pebble custom-notice timer loop. Creates and manages a Kubernetes LoadBalancer service for external AMQP connectivity, with configurable annotations.

## Deployment log

All on `concierge-k8s-4` (Juju 4.0.5), model `rv-rabbitmq`:

1. `juju deploy rabbitmq-k8s --channel 3.12/stable --trust` → deployed as rev 71, `ubuntu@24.04`, active/idle with version 3.12.1 after ~4 minutes.
2. `juju run rabbitmq-k8s/0 get-operator-info` → returned `operator-user: operator`, `operator-password: REDACTED`.
3. `juju scale-application rabbitmq-k8s 3` → all 3 units active/idle within ~30s. Cluster status confirmed `running_nodes` had all 3 nodes. Three Pebble services: `rabbitmq`, `epmd`, `notifier`.
4. LoadBalancer service `rabbitmq-k8s-lb` created with external IP `10.43.45.0`.
5. `juju run rabbitmq-k8s/0 get-service-account username=testuser vhost=testvhost` → returned full credentials and rabbit:// URL.
6. `juju scale-application rabbitmq-k8s 2` → scale-down clean, unit departed within ~10s, `rabbitmqctl forget_cluster_node` ran, cluster running on remaining 2 nodes.
7. `juju config rabbitmq-k8s auto-ha-frequency=-1` → **config-changed hook crashed on all units**, status went to `error: hook failed: "config-changed"`. Recovered after `juju config auto-ha-frequency=30` + `juju resolve`.
8. `juju config rabbitmq-k8s loadbalancer_annotations='invalid annotation with spaces'` → status correctly went to `blocked: Invalid config value 'loadbalancer_annotations'`, but only on the leader unit.
9. Process kill (SIGKILL on `beam.smp`) → Pebble auto-restarted the service, charm stayed active.
10. Actions `ensure-queue-ha`, `rebalance-quorum` both completed successfully.

## Observed behaviour

Timings and measurements from rev 71 on Juju 4.0.5:

| metric | value |
|---|---|
| Time to active/idle (single unit) | ~4 min |
| Time to cluster 3 units | ~30s after scale |
| Unit agent + workload memory | ~180 MB per pod |
| Charm size (packed) | not measured (used charmhub) |
| Pebble services | 3: `rabbitmq` (beam.smp), `epmd`, `notifier` |
| Config change hook failure recovery | requires manual `juju resolve` |
| LoadBalancer external IP assignment | ~1 min |

**Notifier runs as root.** `ps aux` showed `/bin/bash /usr/bin/notifier` running as root (PID 180). The Pebble service definition for `notifier` has no `user`/`group` field, unlike `rabbitmq` and `epmd`, which both set `user: rabbitmq, group: rabbitmq`. The timer loop script does not need root.

**Config-changed hook failure leaves partial state.** When `auto-ha-frequency=-1` crashed the hook, the charm had already pushed `enabled_plugins`, `rabbitmq.conf`, and `rabbitmq-env.conf` before reaching the notifier rendering step that raised `RabbitOperatorError`. The config files were updated but the hook then crashed, and the notifier script itself was never re-rendered.

**Only the leader sets blocked status for invalid annotations.** When `loadbalancer_annotations` is invalid, `_reconcile_lb` only runs on the leader unit, so only the leader shows `blocked`. Non-leader units remain `active` despite the application-level misconfiguration.

## Findings

### `auto-ha-frequency` validation crashes config-changed instead of blocking

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:334` → `src/charm.py:1123`
- **Evidence**: `_on_config_changed` calls `_render_and_push_pebble_notifier()` at line 334, which raises `RabbitOperatorError` at line 1123 when `auto-ha-frequency < 1`. The exception is uncaught, so the hook exits with error status. Observed during deployment: setting `auto-ha-frequency=-1` put both units into `error: hook failed: "config-changed"`.
- **Impact**: Juju 4.x does not validate this option at the config layer (it's `type: int` with no min/max), so an operator can trivially trigger a hard hook error. Recovery requires manual `juju resolve`.
- **Fix**: Move validation into `_on_config_changed` before pushing files; set `BlockedStatus("auto-ha-frequency must be >= 1")` instead of raising. Optionally add a `minimum: 1` constraint to the config option in `charmcraft.yaml`.
- **Linter rule**: "hook handler must not raise uncaught exceptions from config validation" — mechanically checkable by detecting `raise` in code paths reachable from `config_changed` that are not inside a `try/except`.

### `HTTPError` `errno` access is incorrect during operator-user bootstrap

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:473`
- **Evidence**:
  ```python
  except requests.exceptions.HTTPError as e:
      if e.errno == 401:
          logging.error("Authorization failed")
          raise e
  ```
  `HTTPError` does not have an `errno` attribute in practice; the correct check is `e.response.status_code == 401`, as used correctly in `create_amqp_credentials` at line 1284.
- **Impact**: If operator-user initialization gets a 401 (e.g. `guest` was already deleted by a previous leader), the `e.errno == 401` check fails to match and the intended `raise e` never fires — the error is silently swallowed. In the worst case the charm believes initialization succeeded when it didn't, leaving the cluster with no usable admin user.
- **Fix**: Replace with `getattr(e, 'response', None) is not None and e.response.status_code == 401`.
- **Linter rule**: "accessing `.errno` on `requests.HTTPError`" — mechanically checkable by pattern-matching `requests.exceptions.HTTPError` handlers that access `.errno`.

### `HTTPError` `errno` accessed in f-string for `_get_service_account`

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:1391`
- **Evidence**:
  ```python
  msg = f"Rabbitmq is not ready. Errno: {e.errno}"
  ```
  in a combined `except (ConnectionError, HTTPError)` handler. `HTTPError` doesn't reliably have `.errno`.
- **Impact**: An HTTP error during the `get-service-account` action can produce a confusing message (`None`) or a secondary `AttributeError`, masking the real problem inside an already-failing action handler.
- **Fix**: Use `getattr(e, 'errno', 'N/A')` or branch by exception type.
- **Linter rule**: same as above.

### Notifier service runs as root

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:315-324` (Pebble layer, NOTIFIER_SERVICE section)
- **Evidence**: The `notifier` service definition in `_rabbitmq_layer()` has no `user`/`group` keys. Runtime confirmation: `root  180  /bin/bash /usr/bin/notifier`. The other two services (`rabbitmq`, `epmd`) both specify `user: rabbitmq, group: rabbitmq`.
- **Impact**: The notifier script is a simple shell loop that sleeps and calls `pebble notify`; it doesn't need root. Needless privilege escalation.
- **Fix**: Add `"user": RABBITMQ_USER, "group": RABBITMQ_GROUP` to the NOTIFIER_SERVICE Pebble service dict.
- **Linter rule**: "Pebble service without user/group when other services specify them" — mechanically checkable on the Pebble layer dicts.

### Operator-user bootstrap race on leader change

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:464, 934-961`
- **Evidence**: `_initialize_operator_user` uses `guest`/`guest` to create the operator user, then deletes `guest`. The "done" signal is `peers.set_operator_user_created()` at line 956. If leadership changes between creating the operator user (line 950) and setting that flag (line 956), or between the flag and deleting guest (line 960), the new leader never retries — `_on_peer_relation_connected` checks `not self.peers.operator_user_created` at line 464, finds it set, and does nothing, so `guest` stays alive. Alternatively, if `guest` is deleted but the flag wasn't committed before leadership was lost, the new leader retries `guest`/`guest`, gets a 401, and hits the broken `errno` check above.
- **Impact**: Either the `guest` account is left alive (security risk) or the charm gets stuck with no usable admin credentials.
- **Fix**: Make initialization idempotent — check via the API whether the operator user already exists (using existing credentials if available), only create if missing, and don't treat the `operator_user_created` peer flag as sole arbiter of whether `guest` was deleted. Delete guest at the start of the flow rather than the end, or check for its existence before use.
- **Linter rule**: not mechanically checkable.

### Config-changed pushes config files before validation

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:330-333`, `src/charm.py:1117-1123`
- **Evidence**:
  ```python
  self._render_and_push_config_files()      # line 330
  notifier_changed = self._render_and_push_pebble_notifier()  # line 333
  ```
  `_render_and_push_config_files` pushes `enabled_plugins`, `rabbitmq.conf`, `rabbitmq-env.conf` unconditionally; `_render_and_push_pebble_notifier` then raises if `auto-ha-frequency < 1` at line 1123.
- **Impact**: If validation fails, config files have already been changed on disk before the hook crashes. Currently idempotent-but-wasteful on resolve, but architecturally fragile if a future validation path allows a fix without a resolve.
- **Fix**: Hoist validation to the top of `_on_config_changed`, before any side effects.
- **Linter rule**: "config-changed handler performs side effects before validation" — mechanically checkable by looking for exception-raising calls after `container.push`/other writes in the handler.

### `_on_peer_relation_leaving` accesses container without checking RabbitMQ is running

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:410-433`
- **Evidence**: `_on_peer_relation_leaving` calls `self.unit.get_container(RABBITMQ_CONTAINER)` and `container.exec(...)` without a `_rabbitmq_running()`/can-connect guard, unlike `_on_peer_relation_connected` (line 441), which defers if not running.
- **Impact**: If a unit departs while RabbitMQ isn't running (e.g. during initial deployment), `container.exec(["rabbitmqctl", ...])` fails. The `ExecError` catch at line 425 handles part of this, but an uncaught `ModelError` from `container.get_service`/`container.exec` would crash the relation-departed hook.
- **Fix**: Add a `_rabbitmq_running()` guard and defer or skip gracefully.
- **Linter rule**: "Pebble `container.exec` called without can_connect guard in relation-departed handler" — mechanically checkable.

### `PeersConnectedEvent`/`ReadyPeersEvent` type annotations use base `EventBase`

- **Severity**: low
- **Kind**: bug
- **Where**: `src/interface_rabbitmq_peers.py:127-129`, `src/charm.py:559`
- **Evidence**: `on_changed` emits `self.on.ready.emit(event.unit.name)`, which requires `ReadyPeersEvent` to carry a `nodename`. The `_on_peer_relation_ready` handler at `charm.py:559` accesses `event.nodename` correctly at runtime, but its parameter is annotated as plain `EventBase` rather than the concrete `ReadyPeersEvent`.
- **Impact**: No type-safety on `event.nodename`; a refactor or typo in the event class could break silently.
- **Fix**: Annotate handler parameters with the concrete event types.
- **Linter rule**: "charm handler annotated with base `EventBase` but uses subclass-specific attributes" — mechanically checkable with type inference.

### `ensure_queue_ha` raises exception instead of returning a structured result

- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:1477`
- **Evidence**:
  ```python
  if len(nodes) < min_replicas:
      raise RabbitOperatorError(msg)
  ```
  vs. the no-undersized-queues path, which returns a dict. The action handler catches the exception and calls `event.fail(str(e))`, so the action UX is fine, but the method's return/exception contract is inconsistent for direct callers.
- **Impact**: Makes the method harder to reuse outside the action handler.
- **Fix**: Return `{"undersized-queues": N, "replicated-queues": 0, "error": "not enough nodes"}` instead of raising.
- **Linter rule**: not mechanically checkable.

## Worth copying

1. **Scenario tests with `ops.testing`** (`tests/unit/test_charm_scenario.py`). 24 scenario tests covering the full event lifecycle — pebble-ready, config-changed, update-status, actions, and Pebble custom notices — without mocking framework internals. `conftest.py` parses `charmcraft.yaml` to feed metadata into `testing.Context`, keeping test config in sync with reality.

2. **Well-structured config validation** (`src/charm.py:1630-1720`). `parse_annotations`, `validate_annotation_key`, `validate_annotation_value`, and `is_qualified_name` do proper Kubernetes annotation validation against the upstream `apimachinery` regexes, with 27 parametrized test cases for `parse_annotations`.

3. **Deferred event pattern** (`src/charm.py:301-327`). `_on_config_changed` defers early for each prerequisite (container connectivity, erlang cookie, operator user, bind address, storage attached) before doing any work, each with a comment explaining what's missing.

4. **Pebble custom notice timer** (`src/charm.py:1125-1147`, `src/charm.py:654-668`). A shell-script timer that fires via Pebble custom notice avoids running a Python thread or relying on Juju's `update-status` interval for queue HA management. The notifier script is rendered from config and only restarted when its content changes.

5. **Clean separation of concerns**. `rabbit_extended_api.ExtendedAdminApi` extends the upstream `rabbitmq_admin.AdminAPI` package with only the endpoints the charm needs (`grow_queue`, `add_member`, `delete_member`, `rebalance_queues`, `list_quorum_queues`, `get/set_cluster_name`).

6. **Idempotent config push** (`src/charm.py:1070-1147`). `_render_and_push_pebble_notifier` compares existing file content before pushing, and only returns `True` (triggering a restart) when content actually changed.

7. **User sharing detection** (`src/charm.py:619-647`). `_is_amqp_username_in_use_elsewhere` checks all active AMQP relations before deleting a user on relation removal, preventing removal of users shared across multiple CMR relations.

## Common-practice notes

- **Follows**: Standard `src/` layout, `charmcraft.yaml` as single source of truth (no `metadata.yaml`), `lib/charms/<charm>/v<N>/` for charm libraries, ops framework with Pebble, `lightkube` for K8s resource management, `tenacity` for retry loops.
- **Follows**: `StoredState` is used for `enabled_plugins` and `rabbitmq_version` — runtime-only values that don't need to survive pod restarts (plugins are re-enabled in `__init__`, version re-fetched on `update-status`). Appropriate use.
- **Drifts**: The `ingress` library used is `charms.traefik_k8s.v1.ingress` (`IngressPerAppRequirer`), which emits a deprecation warning at runtime (`"ingress v1" library is DEPRECATED in favour of "ingress v2"`), observed in debug-log on both units during `config-changed`. The v2 library should be adopted.
- **Drifts**: Passwords are generated with `pwgen.pwgen(12)`. `secrets.token_urlsafe` would be more cryptographically sound; not a vulnerability given the threat model, but a notable choice.
- **Drifts**: Password storage uses the peer relation app data bag (`src/interface_rabbitmq_peers.py:169`). Juju secrets would be more appropriate for credentials than plain relation data, though exposure is limited since the peer relation is intra-model.
- **Drifts**: The charm manages a Kubernetes LoadBalancer service directly via `lightkube` rather than through an ingress integrator. The README documents `traefik-k8s` for the management UI, but the AMQP LoadBalancer is a custom K8s resource outside Juju's lifecycle (cleaned up in `_on_remove` only if leader).

## Tests

- **Unit tests**: 111 tests, all pass, in two files:
  - `tests/unit/test_charm_scenario.py` (24 tests) — scenario-based tests using `ops.testing.Context`. Covers pebble-ready, config-changed, update-status, actions, custom notices.
  - `tests/unit/test_charm_methods.py` (87 tests) — mock-driven tests for individual methods: queue growth selector, node name generation, ownership handling, erlang cookie, relation data publishing, AMQP credentials, service account action, LB annotation parsing (27 parametrized cases).
- **Functional tests**: 4 tests in `tests/functional/` using the `jubilant` framework:
  - `test_operations` — deploys 1 unit, exercises `get-operator-info`, `get-service-account`, `ensure-queue-ha`.
  - `test_scale_up` — deploys 1 unit, scales to 3, verifies cluster membership.
  - `test_scale_down` — deploys 3 units, scales to 1, verifies node cleanup.
  - `test_refresh` — deploys from stable channel, refreshes to local charm, verifies operator info and actions still work.
- **Coverage gaps**:
  - No test for `_render_and_push_pebble_notifier` raising on invalid `auto-ha-frequency` (the bug found above).
  - No test for leader-change scenarios: operator user initialization after a leadership transition, cookie generation after leadership change.
  - No test for `_on_peer_relation_leaving` with RabbitMQ not running.
  - No test for `_initialize_operator_user` when `guest` is already deleted.
  - No test for the `_reconcile_lb` non-leader path (skipped in unit tests via `TestableRabbitMQOperatorCharm` override).
  - Functional tests are solid but inject no failures (no bad config, no process kill, no network partitions).

## Docs

- **README**: 44 lines. Covers basic deploy (single unit + traefik), AMQP client relate, management UI access. Too thin — no mention of `auto-ha-frequency`, `minimum-replicas`, `loadbalancer_annotations`, quorum queue management actions, or the LB service. No upgrade instructions. No explanation of why `--trust` is required.
- **Charmhub description**: just "RabbitMQ." `links.documentation` points to `https://discourse.charmhub.io/t/thedac-rabbitmq-operator-docs-index/4630`, which is not the canonical RabbitMQ operator docs.
- **Config descriptions**: `loadbalancer_annotations` is thoroughly documented in `charmcraft.yaml` (23 lines with examples and Kubernetes reference links). `minimum-replicas` and `auto-ha-frequency` are documented.
- **Action descriptions**: All actions (`get-operator-info`, `get-service-account`, `ensure-queue-ha`, `rebalance-quorum`, `add-member`, `delete-member`, `grow`, `shrink`) have `description` fields; `grow`/`shrink` params are well described.
- **Missing**: No `docs/` directory, no `CONTRIBUTING.md`, no explanation of the cluster formation protocol or what `cluster_formation.peer_discovery_backend = k8s` means operationally.
- **Doc/reality gap**: The README instructs `juju run-action --wait`, which is Juju 3.x syntax; Juju 4.x uses `juju run ... action-name` without `--wait`. Reproduced: running the documented command against Juju 4.0.5 failed.

## Open questions

1. Why does `update_status` call `_publish_relation_data()` on every tick? The code comment states "We don't have a better way than relying on update status to catch loadbalancer changes." This means every 5 minutes (default interval) the charm re-publishes hostname to all AMQP relations even when nothing changed. Is there a Kubernetes watch or event the charm could use instead?
2. Does the LoadBalancer service survive a controller restart? `_on_remove` deletes the LB K8s service only if the leader is present and running at removal time. If the model is force-destroyed or the leader is gone, the LB service may be orphaned — would need testing with `--force --no-wait` followed by a check for leaked K8s resources. (unverified)
3. Is the erlang cookie secure at rest? It's stored in the peer relation app data bag and written to `/var/lib/rabbitmq/.erlang.cookie` with `600` permissions. Juju secrets would be a better fit but would require changing the peer relation protocol. Worth checking whether `juju show-status-log` exposes the cookie in relation data. (unverified)
