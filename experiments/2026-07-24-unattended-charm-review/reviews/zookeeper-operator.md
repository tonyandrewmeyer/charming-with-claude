# zookeeper-operator

A mature, well-structured machine charm for Apache ZooKeeper 3.9.2, with a clean manager/event architecture, typed pydantic config, and broad feature coverage (TLS, S3 backup/restore, rolling restarts, quorum management, in-place upgrades). Deployment and basic operation work cleanly. But the upgrade path is broken in a way that cascades badly: a routine Juju controller upgrade leaves a stale `upgrade_stack` in peer data that this charm never clears, and that stale value silently blocks TLS-disable rolling restarts, blocks password rotation, and crashes new units on scale-up. The unit test suite currently has 20/160 failing tests, some of which cover exactly the code paths above. A maintainer should first fix the `upgrade_events.idle` gate so it cannot block non-upgrade rolling restarts (the TLS/`sslQuorum` cascade), then decouple `on_upgrade_changed` from the wrong peer relation, then get the test suite green again — those three fixes address every "critical" and most "high" findings below.

| | |
|---|---|
| Repo | canonical/zookeeper-operator @ `9804990` (2026-05-01) |
| Charms | zookeeper (machine, primary), application (integration test harness) |
| Substrate | machine (LXD VMs); K8s manager code exists but `SUBSTRATE` is hardcoded to `"vm"` |
| Deployed | yes — `concierge-lxd-4` (Juju 4.0.12), `3/edge` rev 164; also redeployed fresh on `concierge-lxd` (Juju 3.6.27) |
| Reviewed | 2026-08-21 |

## What it does

Deploys and manages an Apache ZooKeeper 3.9.2 cluster on Ubuntu machines via the `charmed-zookeeper` snap:
- Cluster formation and quorum management (leader election, scaling in/out)
- SASL/Digest authentication for server-server (quorum) and client-server communication
- TLS certificate management via `tls-certificates`
- S3 backup/restore via `s3-integrator`
- Rolling restarts on config change via `rolling_ops`
- In-place snap upgrades
- COS agent integration (metrics and logs)
- Password rotation for `super` and `sync` internal users

## Deployment log

### Initial deploy (2 units, `concierge-lxd-4`, Juju 4.0.12)

```bash
juju add-model rv-zookeeper --controller concierge-lxd-4
juju deploy zookeeper --channel 3/edge -n 1   # revision 164
juju add-unit zookeeper -n 1
```

| time | event |
|---|---|
| 08:04 | machines pending |
| 08:05 | data-storage-attached hook fires on unit 0 |
| 08:05 | install hook fires, snap installs |
| 08:06 | unit 0 waiting for peer relation |
| 08:07 | unit 1 machine provisioned |
| 08:09 | unit 1 begins install |
| 08:11 | unit 1 in maintenance ("not all units related") |
| 08:13 | unit 0 quorum forming |
| 08:15 | both units active, version 3.9.2 |

Time to active-idle: ~12 minutes for a 2-unit cluster.

### Config change test

```bash
juju config zookeeper log-level=DEBUG
```

Triggered rolling restart (`config-changed` → `restart-relation-changed` per unit). Both units returned to active in ~60 seconds.

### TLS integration test

```bash
juju deploy self-signed-certificates --channel latest/edge   # rev 633
juju integrate zookeeper self-signed-certificates
```

Cluster briefly showed `provider not ready - not all units using same encryption`, completed the rolling restart, returned to active. `sslQuorum=true` confirmed in `zoo.cfg`.

### Action tests

```bash
juju run zookeeper/leader get-super-password    # succeeds
juju run zookeeper/leader get-sync-password     # succeeds

juju run zookeeper/leader set-password username=super password="TestP@ss1234"
# Action 61 failed: Cannot set password while upgrading (upgrade_stack: [1, 0])

juju run zookeeper/leader pre-upgrade-check
# Action 57 failed: Pre-upgrade check failed and cannot safely upgrade

juju run zookeeper/leader list-backups
# Action 63 failed: Cluster needs an access to an object storage to make a backup

juju run zookeeper/0 create-backup
# Action 79 failed: Cluster needs an access to an object storage to make a backup

juju run zookeeper/0 set-tls-private-key
# Action 81 failed: exit status 1
#   Uncaught RuntimeError in charm code: Relation certificates does not exist
```

`list-backups`/`create-backup` fail with a clean, user-facing message. `set-password` and `pre-upgrade-check` fail due to the stale `upgrade_stack` (false positive — the cluster is healthy, not upgrading). `set-tls-private-key` crashes with an uncaught `RuntimeError` when no certificates relation exists.

### TLS relation removal

```bash
juju remove-relation zookeeper self-signed-certificates
```

Both units ran `_on_certificates_broken` → cleared cert data → removed keystores → leader set `switching-encryption=started` → emitted `config_changed`. **The rolling restart did not fire**: no "Beginning rolling restart" in status history after 08:54. `acquire_lock.emit()` in `_on_cluster_relation_changed` requires `upgrade_events.idle`, which was `False` (stale `upgrade_stack = [1, 0]`). `sslQuorum=true` remained stuck in the ZooKeeper config — a silent failure of the TLS-disable operation.

### `pre-upgrade-check`

- Juju 4.x cluster (stale `sslQuorum=true`): action hangs ~20 minutes then fails "Pre-upgrade check failed and cannot safely upgrade". The non-TLS KazooClient can't reach a ZooKeeper server enforcing TLS for quorum traffic.
- Juju 3.6 fresh cluster (no `upgrade_stack`, no `sslQuorum`): fails quickly — quorum leader not found, cluster was only ~4s old.

### `set-password` on Juju 3.6 (fresh cluster, `concierge-lxd`)

Proceeds past the `idle` check (no stale `upgrade_stack` on this controller), stores the password, then crashes: `Uncaught ConnectionLoss in charm code` from the KazooClient during SASL authentication. `_on_client_relation_updated` catches `KazooTimeoutError` but not `ConnectionLoss`.

### `grafana-agent` / COS integration

`grafana-agent` (rev 605, Ubuntu 24.04 base) deployed to the same model. `juju integrate zookeeper:cos-agent grafana-agent:cos-agent` failed: "no compatible bases found for application 'zookeeper' and 'grafana-agent'" (zookeeper is 22.04-only). Not exercisable in this environment; not a charm defect per se.

### `juju resolve` on failed unit (zookeeper/2)

```bash
juju resolve zookeeper/2
```

Unit re-enters `error` immediately. Debug log: `KeyError` at `lib/charms/data_platform_libs/v0/upgrade.py:1130` → `ops/model.py:1817`, reading unit state from the upgrade relation where it was never written. `juju resolve` does not fix it.

### S3 integrator deployment attempt

```bash
juju deploy s3-integrator --channel latest/edge
juju config s3-integrator bucket="zookeeper-backups" endpoint="http://10.5.87.123:9000"
juju integrate zookeeper s3-integrator
```

`s3-integrator` deployed to Ubuntu 24.04 (base-incompatible with the 22.04 zookeeper machines) and entered `blocked` ("Missing parameters: ['access-key', 'secret-key']" — not configurable via `juju config`). Relation never formed; S3 backup/restore not exercised in this environment.

### `juju refresh`

```bash
juju refresh zookeeper --channel 3/edge
# charm "zookeeper": already up-to-date
```

No newer revision available (`3/edge` = rev 164, deployed revision).

### Juju 3.6 environment (`concierge-lxd`, Juju 3.6.27, fresh model)

| time | event |
|---|---|
| 09:12 | model created |
| 09:13 | zookeeper deployed |
| 09:18 | machine 0 provisioned |
| 09:22 | both units in maintenance (installing) |
| 09:25 | cluster active |
| 09:26 | `get-super-password` works |
| 09:26 | `set-password` crashes with `Uncaught ConnectionLoss` |

`upgrade-relation-created` fired (09:23:52) but `pre-upgrade-check` was not called by the controller (no agent version gap), so no `upgrade_stack` was created — confirming the `upgrade_stack` issue is Juju-4.x/controller-upgrade specific, and that Juju 3.6 has its own, separate `ConnectionLoss` bug.

## Observed behaviour

- **Hook wiring**: `update_status` is wired to the same `_on_cluster_relation_changed` handler as `config_changed`/`cluster_relation_changed`/`leader_elected`, not a dedicated health-check handler. The handler does check `workload.alive`, but only at the end, after the `config_changed()`/`switching_encryption` block that can fire `acquire_lock.emit()`. A unit whose config is unchanged and workload has died is only caught when `update_status` next runs (up to 5 minutes).
- **Dead workload detection lag**: killing `snap.charmed-zookeeper.daemon` left the unit `active` immediately (no hook fired). After ~2 minutes, `update_status` fired and the unit went `blocked: zookeeper service not running`. Restarting the service left the unit `blocked` for another ~5 minutes until the next `update_status` cleared it.
- **Invalid config crashes the hook, not just blocks**: `init-limit=0` raises pydantic `ValidationError` during `ClusterState.__init__` (called from `ZooKeeperCharm.__init__`), before any handler can set status. Both units went to `error` with `hook failed: "config-changed"`. `juju resolve` had no effect; only correcting the config recovered the unit.
- **`set-password` blocked by stale `upgrade_stack`**: after a Juju controller upgrade, `pre-upgrade-check` runs as part of Juju's lifecycle and the leader's `build_upgrade_stack()` writes `upgrade_stack: [1, 0]` to peer data. Juju never sends `upgrade_granted` to machine charms, so the stack never clears. `set-password` then always fails with "Cannot set password while upgrading (upgrade_stack: [1, 0])" — a permanent false positive.
- **Scale-up crash**: adding a unit while `upgrade_stack` is set causes the new unit to receive `upgrade-relation-changed`; `on_upgrade_changed` (data_platform_libs) pops the stack and reads `self.peer_relation.data[top_unit]` on the **upgrade relation** — but this charm writes unit state to the **cluster peer relation**, so the read raises `KeyError`. The new unit enters `error` and stays there; `juju resolve` re-crashes it immediately.
- **TLS integration**: works end-to-end with `self-signed-certificates` rev 633, though the integration test suite pins rev 163 with a `FIXME` comment about a known compatibility issue.
- **Restart timing**: each rolling restart step takes roughly 5s for ZooKeeper to restart plus a hardcoded `time.sleep(5)` in `_restart`.
- **`set-tls-private-key`** crashes with an uncaught `RuntimeError` when no certificates relation exists; exit status 1 with no actionable message.
- **`create-backup`/`list-backups`** fail cleanly with a descriptive message when S3 credentials are absent — correct behaviour.
- **`expose-external` on VM substrate** is a silent no-op: `K8sManager` is instantiated but never invoked from `charm.py` when `SUBSTRATE == "vm"`. Correct behaviour, but nothing stops an operator from setting the config value and being misled.
- **Known open issue #205**: after a machine reboot, ZooKeeper election port 3888 binds to localhost only, preventing other units from reconnecting (not independently reproduced in this review; unverified).

## Findings

### Stale `upgrade_stack` permanently blocks the TLS-disable rolling restart

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:207–211` (rolling-restart gate), `src/events/upgrade.py:44–50` (`idle` property)
- **Evidence**: `_on_cluster_relation_changed` only calls `acquire_lock.emit()` when `(config_manager.config_changed() or state.cluster.switching_encryption) and unit_server.started and upgrade_events.idle`. `idle` returns `not bool(self.upgrade_stack)`. After a Juju controller upgrade writes `upgrade_stack = [1, 0]` to peer data (see below) and it is never cleared, `idle` is permanently `False`. Observed: after `certificates-relation-broken`, the leader set `switching-encryption=started` and emitted `config_changed`, but no rolling restart ever fired — no "Beginning rolling restart" appears in status history. `sslQuorum=true` stayed in `zoo.cfg` indefinitely.
- **Impact**: TLS disable silently fails with no user-visible indication. This cascades into `pre-upgrade-check` failing permanently (the non-TLS KazooClient cannot reach a quorum that still enforces `sslQuorum`), making safe upgrades impossible, and it is the same gate that blocks password rotation (see below).
- **Fix**: Decouple the `switching_encryption` restart trigger from `upgrade_events.idle` — TLS state changes should acquire the lock regardless of a stale upgrade stack. Alternatively, make `idle` recognize a stale (non-actionable) `upgrade_stack` left over from a controller upgrade and treat it as idle.
- **Linter rule**: flag any `and self.upgrade_events.idle` guarding a `switching_encryption`-triggered lock acquisition.

### Hardcoded `snap_daemon` UID breaks backup restore on Ubuntu 24.04

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/literals.py:29` (`USER = 584788`), `src/managers/backup.py:216–218`
- **Evidence**: `backup.py` calls `workload.exec(["bash", "-c", f"chown {USER}:{USER} {restored_snapshot}"])` with the numeric UID. `snap_daemon`'s UID is 584788 on Ubuntu 22.04 but 584792 on Ubuntu 24.04. `workload.py`'s own `write()` uses `shutil.chown(..., user="snap_daemon")` (the string form, which resolves correctly on both), so the two files are inconsistent.
- **Impact**: `restore-backup` fails on any Ubuntu 24.04 machine because `chown 584788:584788` targets a UID that doesn't exist. Not independently verified against a live 24.04 machine in this review (unverified).
- **Fix**: Use the string `snap_daemon` consistently in `backup.py`, or resolve the UID dynamically (`pwd.getpwnam("snap_daemon").pw_uid`) instead of hardcoding.
- **Linter rule**: flag hardcoded numeric UIDs passed to `chown` where a string username is available — not fully mechanically checkable without cross-referencing OS base.

### Stale `upgrade_stack` permanently blocks password rotation

- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/upgrade.py:44–50` (`idle`), `lib/charms/data_platform_libs/v0/upgrade.py` (`_on_pre_upgrade_check_action`)
- **Evidence**: A Juju controller bootstrap/upgrade fires `upgrade-relation-created/changed/joined`; the leader's `pre-upgrade-check` builds `upgrade_stack = [1, 0]` and stores it in peer app data. Juju never grants `upgrade_granted` to machine charms, so the stack persists forever. `set-password` checks `not self.upgrade_events.idle` and always fails: "Cannot set password while upgrading (upgrade_stack: [1, 0])" — reproduced on the Juju 4.x deployment.
- **Impact**: After any Juju controller bootstrap/upgrade, password rotation is permanently blocked on an otherwise healthy, `active` cluster. Recovery requires manually clearing the `upgrade-stack` key from peer relation data.
- **Fix**: Guard `_on_pre_upgrade_check_action` to detect whether a real Juju-granted upgrade is in progress before trusting `upgrade_stack`; clear it if not. Or provide a manual recovery action.
- **Linter rule**: not mechanically checkable.

### New unit crashes on `upgrade-relation-changed` due to wrong relation as data source

- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/data_platform_libs/v0/upgrade.py:1087,1130` (`on_upgrade_changed`), `src/events/upgrade.py`
- **Evidence**: On `juju add-unit`, `on_upgrade_changed` pops `top_unit_id` from `upgrade_stack`, resolves `top_unit`, then reads `self.peer_relation.data[top_unit].get("state")` where `peer_relation` is the **upgrade relation** (Juju controller's relation), not the cluster peer relation the charm actually writes unit state to. Debug log confirms `KeyError` at `lib/charms/data_platform_libs/v0/upgrade.py:1130` → `ops/model.py:1817`. `juju resolve` re-crashes the unit immediately.
- **Impact**: Any scale-up on a cluster with a stale `upgrade_stack` (i.e. any cluster that has been through a Juju controller upgrade) permanently fails the new unit. The cluster cannot grow without manual intervention.
- **Fix**: Override `on_upgrade_changed` in `ZKUpgradeEvents` to read unit state from the cluster peer relation, or additionally write unit state to the upgrade relation.
- **Linter rule**: not mechanically checkable — requires understanding the data_platform_libs contract.

### `pre-upgrade-check` hangs ~20 minutes then fails on a cluster with residual `sslQuorum=true`

- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/zookeeper/v0/client.py:155–169` (`members_broadcasting`), `src/managers/quorum.py:59–79` (`is_syncing`)
- **Evidence**: Action started 08:34:38, produced output 08:34:43, failed 08:52:25 (~18 minutes). Root cause: the TLS-disable rolling restart was blocked (see above), so `sslQuorum=true` remains in `zoo.cfg`. `ZooKeeperManager.client` connects with `use_ssl=False`; ZooKeeper enforces TLS for quorum traffic, so each connection attempt hangs/times out, and retry logic (2 attempts × 3s in the manager, 5 attempts with 1–5s random wait in `post_upgrade_check`) compounds the delay.
- **Impact**: The action appears to hang, then fails with a message that gives no hint that residual `sslQuorum` is the cause — an operator cannot diagnose it without inspecting `zoo.cfg` directly.
- **Fix**: Fix the TLS-disable restart gate (above) so `sslQuorum` is actually cleared. Add a diagnostic action reporting TLS config state. Add a fail-fast timeout to `ZooKeeperManager.client` construction.
- **Linter rule**: not mechanically checkable.

### `srvr` property in the ZooKeeper client library has no bounds checking

- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/zookeeper/v0/client.py:548–556`
- **Evidence**:
  ```python
  for item in response.splitlines():
      k = re.split(": ", item)[0]
      v = re.split(": ", item)[1]  # IndexError if no ": " in item
      result[k] = v
  ```
  `mntr` has an equivalent guard (`if re.search("=|\\t", item): ... else: result[item] = ""`); `srvr` does not.
- **Impact**: Any line in ZooKeeper's `srvr` 4lw output without `": "` (blank lines, unexpected formats) raises an uncaught `IndexError`, crashing `get_version()` and any caller of `srvr` — including code reached from `_on_cluster_relation_changed` and the upgrade flow.
- **Fix**: Apply the same guard used in `mntr`, or use `re.split(maxsplit=1)` with a length check before subscripting.
- **Linter rule**: flag dict subscript on the result of `re.split` without a bounds check.

### `set-tls-private-key` crashes with an uncaught `RuntimeError` when no certificates relation exists

- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/tls.py:97` (`_set_tls_private_key` → `_on_certificate_expiring`)
- **Evidence**: `juju run zookeeper/0 set-tls-private-key` with no certificates relation produced `Uncaught RuntimeError in charm code: Relation certificates does not exist - The certificate request can't be completed`. `_set_tls_private_key` calls `_on_certificate_expiring` unconditionally, which calls `request_certificate_renewal(...)`, raising an uncaught `RuntimeError`.
- **Impact**: Action fails with exit status 1 and an opaque message that doesn't tell the operator to integrate a TLS provider first.
- **Fix**: Guard on `self.certificates.relations` before calling `_on_certificate_expiring`; fail the action with a descriptive message if absent.
- **Linter rule**: flag TLS action handlers calling `request_certificate_renewal` without checking the certificates relation exists.

### Unguarded dict-key access in password action handlers

- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/password_actions.py:36,44` (`_get_super_password_action`, `_get_sync_password_action`)
- **Evidence**: Both read `internal_user_credentials["super"]`/`["sync"]` directly. `internal_user_credentials` (`src/core/models.py`) returns `{}` if any of `CHARM_USERS` is missing, so the subscript raises `KeyError`.
- **Impact**: `get-super-password`/`get-sync-password` fail with a Python traceback rather than a clean message if called before the peer relation has fully delivered credentials (e.g. immediately after deploy).
- **Fix**: Use `.get()` with a fallback, or check for an empty dict up front and fail the action with a descriptive message.
- **Linter rule**: flag `["super"]`/`["sync"]` subscripts on `internal_user_credentials` without a guard.

### Blocking `time.sleep(5)` in the restart handler

- **Severity**: high
- **Kind**: performance
- **Where**: `src/charm.py:225` (`_restart`)
- **Evidence**: `time.sleep(5)` after each unit restart, with a comment that it exists to give the unit time to rejoin quorum before other units restart.
- **Impact**: Every rolling restart step blocks the hook executor for 5 extra seconds per unit; on larger clusters this adds up meaningfully and masks a real race (units restarting before this one rejoins) rather than solving it.
- **Fix**: Replace with a retry/poll loop against quorum membership (e.g. via `tenacity`), with a timeout, instead of a fixed sleep.
- **Linter rule**: flag blocking `time.sleep()` calls in `src/charm.py` or `src/events/`.

### 20 unit tests fail in the current environment

- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py`, `tests/unit/test_config.py`, `tests/unit/test_quorum.py`, `tests/unit/test_tls.py`
- **Evidence**: `PYTHONPATH=src:lib python -m pytest tests/unit/` → **140 passed, 9 skipped, 20 failed** in ~34s (ops 3.8.1 / ops-scenario 8.8.1). Two categories:
  - **Category A (5 tests, `InconsistentScenarioError`)**: `cluster_relation_changed` events missing the now-required `remote_unit` parameter — `test_relation_changed_updates_ip_hostname_fqdn`, `test_relation_changed_defers_if_upgrading`, `test_relation_changed_emitted_for_relation_changed`, `test_relation_changed_emitted_for_relation_joined`, `test_update_quorum_skips_relation_departed`.
  - **Category B (15 tests, `PermissionError`)**: tests calling `_restart()`/`set_zookeeper_properties()` without mocking `workload.write()`, which calls `os.makedirs`/`shutil.chown` under `/var/snap/charmed-zookeeper`. Affects all TLS rolling-restart tests, restart-guard tests, JAAS tests, `test_get_updated_servers_implicit_removal`, `test_certificates_available_halfway_through_upgrade_succeeds`.
- **Impact**: 12.5% of the unit suite fails, and Category B specifically covers TLS rolling restart, restart guards, and quorum update — exactly the areas with live bugs found in this review.
- **Fix**: Add `remote_unit=zookeeper/1` to affected `State` constructions (Category A). Mock `workload.ZKWorkload.write` (and related filesystem calls) in Category B tests.
- **Linter rule**: not mechanically checkable — requires running the suite against a known-good baseline.

### K8s substrate code paths are untested in CI

- **Severity**: high
- **Kind**: test-gap
- **Where**: `src/managers/k8s.py` (21% coverage), `src/managers/tls.py` K8s paths (26%), `src/managers/backup.py` S3 paths (24%)
- **Evidence**: `SUBSTRATE` is hardcoded to `"vm"` in `literals.py`; `skipif(SUBSTRATE == "k8s")` prevents K8s-specific tests from running, and there is no K8s integration test.
- **Impact**: If this charm is ever deployed on K8s, bugs in K8s-specific storage/service/TLS code will not be caught by CI.
- **Fix**: Add K8s-substrate unit tests or a K8s integration job.
- **Linter rule**: flag `if substrate == 'k8s'` code paths without a corresponding test — checkable via coverage analysis.

### `ConnectionLoss` from KazooClient crashes `set-password` on Juju 3.6

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/events/password_actions.py:50`, `src/events/provider.py` (`_on_client_relation_updated`)
- **Evidence**: On a fresh 2-unit cluster on `concierge-lxd` (Juju 3.6.27, no `upgrade_stack`), `set-password` stores the password then calls `quorum_manager.update_acls` → KazooClient, which raises `RuntimeError: Invalid error code` during SASL authentication, wrapped as `kazoo.exceptions.ConnectionLoss`, uncaught: `Uncaught ConnectionLoss in charm code`. Action exit status 1. `_on_client_relation_updated` catches `KazooTimeoutError` but not `ConnectionLoss`.
- **Impact**: `set-password` fails on a freshly deployed, fully active cluster if run shortly (~4s) after the cluster stabilises.
- **Fix**: Add `ConnectionLoss` to the caught exceptions in `provider.py`, or add retry logic for transient `ConnectionLoss` in `update_acls`.
- **Linter rule**: flag `KazooTimeoutError` caught without `ConnectionLoss` alongside it.

### `get_relation_ip` has no error handling around raw socket calls

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/core/cluster.py:445` (`get_relation_ip`)
- **Evidence**: Uses raw `socket.socket()`/`connect()`/`getsockname()` calls with no try/except; callers (e.g. `quorum.py:98` → `init_server`) have no guard.
- **Impact**: If the network isn't fully initialized (e.g. right after a reboot), `s.connect(("10.10.10.10", 1))` can fail and crash `_on_cluster_relation_changed`, putting the unit into `error`. Possibly related to open issue #205 (unverified).
- **Fix**: Wrap the socket calls in try/except, log at ERROR, and return a `BlockedStatus`/empty string the caller can handle.
- **Linter rule**: flag raw socket operations without try/except in a charm hook path.

### Regex in `_get_updated_servers` has no bounds checking

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/quorum.py:106`
- **Evidence**: `unit_id = str(int(re.findall(r"server.([0-9]+)", server_string)[0]) - 1)` — if the regex doesn't match, `findall` returns `[]` and `[0]` raises `IndexError`.
- **Impact**: A malformed server string (future ZK version, manually edited dynamic config) crashes the leader's `update_quorum`.
- **Fix**: Wrap in try/except, log a warning, skip the malformed entry.
- **Linter rule**: flag list subscript on `re.findall` result without a bounds check.

### `endpoints_external` retry adds up to 15s delay to client relation hooks

- **Severity**: medium
- **Kind**: performance
- **Where**: `src/core/cluster.py:127` (`endpoints_external`)
- **Evidence**: `@retry(wait=wait_fixed(5), stop=stop_after_attempt(3))`, called from `get_endpoints()` on every client relation change.
- **Impact**: On a transient K8s API glitch, the entire hook delays for up to 15 seconds before failing.
- **Fix**: Move the retry to the specific failing API call rather than the whole property, or reduce attempts.
- **Linter rule**: not mechanically checkable.

### Non-leader units can be left with stale TLS keystores if cleanup fails

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/events/tls.py:166` (`_on_certificates_broken`)
- **Evidence**: Calls `tls_manager.remove_stores()` unconditionally on every unit. `remove_stores()` uses `workload.exec()` (shell glob deletion), which can raise `subprocess.CalledProcessError`; this is not caught in the handler.
- **Impact**: A transient failure in `remove_stores()` crashes the hook and leaves that unit in `error` with stale keystores on disk.
- **Fix**: Wrap `remove_stores()` in try/except `CalledProcessError`, log and continue rather than crash.
- **Linter rule**: flag file-deletion calls in hook handlers without a `CalledProcessError` guard.

### Restore workflow can stop the workload before the unit is ready

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/events/backup.py:246` (`_stop_workflow`)
- **Evidence**: Calls `self.charm.workload.stop()` without checking `state.unit_server.started`. `_restore_event_dispatch` runs on every `cluster_relation_changed`, so a unit still starting up could have its (not-yet-started) ZooKeeper stopped mid-join.
- **Impact**: Potential race where a restore initiated while units are still joining stops units before they ever started, breaking cluster formation.
- **Fix**: Add a `not state.unit_server.started` guard at the top of `_restore_event_dispatch`.
- **Linter rule**: flag restore workflow entry points that don't check `unit_server.started`.

### `update_acls` exceptions not fully caught in the client relation handler

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/quorum.py:141–179` (`update_acls`), `src/events/provider.py:53` (`_on_client_relation_updated`)
- **Evidence**: `_on_client_relation_updated` catches `MembersSyncingError`, `MemberNotReadyError`, `QuorumLeaderNotFoundError`, `KazooTimeoutError`, but not `ConnectionLoss` or the `IndexError` that can propagate from `srvr` parsing.
- **Impact**: A transient ZooKeeper connectivity issue during a client relation update crashes the hook instead of deferring; the client never receives credentials.
- **Fix**: Broaden the exception handler (at minimum add `ConnectionLoss`) and defer the event on failure.
- **Linter rule**: not mechanically checkable.

### `restart_unit` integration test helper is broken

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/helpers.py:83–93` (`restart_unit`)
- **Evidence**: `grep awk '{{print $4}}'` — `grep` is given `awk` syntax instead of a pattern, so the pipeline fails outright; additionally `machine_id` (from `juju status`) carries a trailing newline that breaks the subsequent `grep -e '-{machine_id}'` pattern.
- **Impact**: HA/scaling tests that rely on `restart_unit` to simulate machine restarts never actually restart a machine — the scenario is not being tested at all.
- **Fix**: Rewrite using `juju ssh ... sudo shutdown -r now` or the LXD API directly.
- **Linter rule**: flag `grep` invocations with `awk`-style arguments; flag shell pipelines using unsanitized command output as a pattern.

### `subprocess.CalledProcessError` not handled in `workload.exec()` callers

- **Severity**: low
- **Kind**: bug
- **Where**: `src/workload.py:62–66` (`exec`), `src/events/backup.py` (`restore_snapshot`)
- **Evidence**: `exec()` uses `subprocess.check_output`, which raises `CalledProcessError` on non-zero exit; some callers (`tls.py`) catch it, `restore_snapshot`'s `chown` call does not.
- **Impact**: Compounds the Ubuntu 24.04 UID bug above — a failing `chown` in restore crashes the action instead of failing gracefully.
- **Fix**: Catch `CalledProcessError` in `restore_snapshot`, log, and fail the action cleanly.
- **Linter rule**: flag `workload.exec()` results not checked for `CalledProcessError` in a code path that can fail.

### `srvr` shell command in test helper is fragile

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/helpers.py:146` (`srvr`)
- **Evidence**: Constructs `juju ssh ... sudo -i 'curl localhost:{ADMIN_SERVER_PORT}/commands/srvr -m 10'` inside single quotes; if the admin server returns a non-200/error body, parsing downstream may fail unpredictably.
- **Impact**: Leadership/mode checks used across multiple integration tests can silently return incorrect results.
- **Fix**: Run the request through a controlled Python HTTP call over `juju ssh`, or use KazooClient directly in tests.
- **Linter rule**: not mechanically checkable.

### `password_rotated` uses `None` as a dict default instead of `False`

- **Severity**: low
- **Kind**: lint
- **Where**: `src/core/models.py:349`
- **Evidence**: `return bool(self.relation_data.get("password-rotated", None))` — works because `bool(None) == False`, but the intent is unclear.
- **Impact**: Minor maintenance/readability burden.
- **Fix**: Use an explicit `False`/empty-string default and a clear comparison.
- **Linter rule**: flag `dict.get(key, None)` immediately wrapped in `bool()`.

### TLS integration test pins an old `self-signed-certificates` revision

- **Severity**: low
- **Kind**: docs
- **Where**: `tests/integration/test_tls.py:45`
- **Evidence**: `revision=163` with `FIXME (certs): Unpin the revision once the charm is fixed`, while the charm was deployed and manually verified against rev 633 in this review.
- **Impact**: If rev 163 hides a regression present in newer `self-signed-certificates` releases, the integration suite would not catch a production-affecting change.
- **Fix**: Unpin and test against current edge, or document precisely why rev 163 is required.
- **Linter rule**: flag pinned charm revisions in integration tests without an accompanying explanation.

### `upgrade_stack` is not created on fresh Juju 3.6 clusters (informational)

- **Severity**: informational
- **Kind**: observation
- **Where**: `lib/charms/data_platform_libs/v0/upgrade.py`, `src/events/upgrade.py`
- **Evidence**: On a fresh `concierge-lxd` (Juju 3.6.27) deploy, `upgrade-relation-created` fired but `pre-upgrade-check` was not invoked (no controller/agent version gap), so `build_upgrade_stack()` never ran and `idle` stayed `True`.
- **Impact**: The `upgrade_stack` false-positive block is specific to Juju 4.x controller/agent version mismatches; Juju 3.6 fresh clusters avoid it but hit the separate `ConnectionLoss` bug instead.
- **Fix**: n/a (observation).
- **Linter rule**: not mechanically checkable.

## Worth copying

**Status precedence in `literals.py`** — the `Status` enum pairs each status with a log level via a `StatusLevel` dataclass (`ACTIVE = StatusLevel(ActiveStatus(), "DEBUG")`, etc.), so `_set_status` in `charm.py` gets both a meaningful message and the right log level automatically, instead of hardcoding log levels at each call site.

**Manager/event separation** (`src/managers/`, `src/events/`) — `ConfigManager`, `QuorumManager`, `TLSManager`, `BackupManager` hold logic; `ProviderEvents`, `TLSEvents`, `BackupEvents`, `PasswordActionEvents`, `ZKUpgradeEvents` handle events. `charm.py` is a thin coordinator, keeping each concern independently testable.

**Typed charm config with pydantic** (`core/structured_config.py`) — `BaseConfigModel` with `pydantic.Field(gt=0)` validators for `init_limit`, `sync_limit`, `tick_time`, etc. rejects invalid config before it reaches charm logic (modulo the `error`-state crash finding above).

**Comprehensive HA test suite** (`tests/integration/ha/`) — dedicated tests for kill/freeze/network-cut/scaling/leader-restart/full-cluster-restart scenarios, all using `continuous_writes` to confirm no data loss. This is a strong baseline for HA testing in charm repos, even with the `restart_unit` helper bug noted above.

**Streaming S3 backup** (`managers/backup.py`) — uses `httpx.stream()` to stream ZooKeeper snapshots directly to S3 without buffering the whole file in memory.

## Common-practice notes

**Follows convention**: `TypedCharmBase[CharmConfig]`, proper `framework.observe()` registration, standard charm-library versioning (`LIBID`/`LIBAPI`/`LIBPATCH`), poetry-based `charmcraft.yaml`, `tox.ini` with `lint`/`unit`/`integration-*` environments, CI via `data-platform-workflows`.

**Deviates from convention**:
- Repo contains both the `zookeeper` charm and a separate `application` test-harness charm under `tests/integration/app-charm/` — unusual to keep both in one repo.
- Deliberate `managers/`+`events/` architecture rather than a flat `src/charm.py` — good, but non-standard for smaller charms.
- README claims production deployments of "at least 5 nodes" but the charm targets machine/LXD substrate only; `K8sManager`/`managers/k8s.py`/K8s-specific TLS paths exist but are unused (`SUBSTRATE = "vm"`) and untested (21–26% coverage).
- Hardcoded numeric UID (`USER = 584788` in `literals.py`) instead of a dynamic lookup — most charms avoid hardcoding UIDs, and this one breaks on Ubuntu 24.04 (see findings).

**Shipped charm library caveat**: `lib/charms/zookeeper/v0/client.py` is versioned and reusable by other charms (e.g. Kafka), which is the right pattern, but it carries the `srvr`-parsing `IndexError` bug noted above and has not been patched since it was introduced (library at 0.8).

**`rolling_ops` as the concurrency primitive**: used for all restarts via a peer-relation-backed distributed lock — a solid pattern for machine charms, undermined here only by the `upgrade_events.idle` coupling that blocks the lock during a stale upgrade state.

## Tests

### Unit tests

**140 passed, 9 skipped, 20 failed** in ~34s (`ops-scenario 8.8.1` / `ops 3.8.1`), split into:
- **Category A — `InconsistentScenarioError` (5 tests)**: `cluster_relation_changed` events missing `remote_unit`, required by the newer `ops-scenario` consistency checker.
- **Category B — `PermissionError` (15 tests)**: tests exercising restart/TLS/JAAS code paths without mocking `workload.write()`'s filesystem operations (`os.makedirs`, `shutil.chown` under `/var/snap/charmed-zookeeper`).

`test_cluster.py` (22 tests) and `test_client.py` (15 tests) pass completely. Coverage is lowest in `managers/backup.py` (24%), `managers/k8s.py` (21%), `managers/tls.py` K8s-specific lines (26%) — all dead code on the VM substrate since `skipif(SUBSTRATE == "k8s")` prevents them running.

**Confirmed test gaps** (via failure injection and code review): no test for `get-super-password` before the peer relation forms; no test for pydantic `ValidationError` crashing `__init__`; no test for `update_status` detecting a dead workload; no test for `set-password`/new-unit-join under a stale `upgrade_stack`; no test for `pre-upgrade-check` against residual `sslQuorum=true`; no test for `ConnectionLoss` during `set-password`; K8s paths never exercised anywhere.

### Integration tests

Substantial coverage: `test_charm.py` (deploy/storage/log-level/scaling), `test_provider.py` (relation/ACL/JAAS), `test_tls.py` (enable/disable cycle, pins rev 163), `test_upgrade.py` (in-place snap upgrade), `test_backup.py` (S3 create/list/restore), `test_password_rotation.py`, `test_network.py`, and the `ha/` suite (kill, freeze, network cut, scaling, restart, all backed by `continuous_writes`).

Known gaps: `test_scale_down_storage_re_use` is explicitly skipped (issue #85); `test_network_cut_self_heal` is marked `@unstable`. The `restart_unit` helper bug (finding above) means HA scaling tests that depend on it never actually restart a machine. S3 and COS integration tests require infrastructure (compatible S3 provider, matching-base COS charms) not available in this review environment.

## Docs

**README.md**: accurate and comprehensive; documents relations, config, and the `base64 -w0` gotcha for TLS key actions.

**CONTRIBUTING.md**: clear dev setup and `tox devenv -e integration` workflow; the "Build and Deploy" section has a dangling colon with no following code block (minor typo).

**docs/index.md**: points to ReadTheDocs; sidebar links reference the Kafka discourse tag (`https://discourse.charmhub.io/tag/kafka`) rather than a ZooKeeper-specific one.

**Charmhub listing**: matches `metadata.yaml`; `3/stable` is rev 163, bases limited to amd64/22.04 — no 24.04 support declared, consistent with the UID bug above.

## Open questions

1. Does the `snap_daemon` string-vs-numeric-UID inconsistency actually break `chown` on a real Ubuntu 24.04 machine, or does the snap carry backward-compat UID mapping? Needs testing on real 24.04 hardware (unverified in this review).
2. What changed in `self-signed-certificates` between rev 163 (pinned in tests) and rev 633 (used successfully in this review's deployment)?
3. Would replacing `time.sleep(5)` in `_restart` with a quorum-membership poll be both faster and safer, or does the sleep serve a purpose the poll wouldn't cover?
4. Is issue #205 (localhost binding on port 3888 after reboot) related to the unguarded `get_relation_ip` socket calls? Needs a real reboot test.
5. Why does `ops-scenario 8.8.1` newly reject these test constructions — was there a compatible pinned version previously, and did it silently drift via `poetry install --with unit`?
6. Can S3 backup/restore be exercised without a same-base-compatible S3 provider in this environment (e.g. self-hosted MinIO on a 22.04 machine)?
7. Is there a K8s test environment available to actually exercise the untested `managers/k8s.py` paths?
8. Is the `ConnectionLoss`/SASL `RuntimeError: Invalid error code` on Juju 3.6 a timing issue specific to a ~4-second-old cluster, or a version mismatch between KazooClient and the ZooKeeper SASL implementation?
9. Does real ZooKeeper 3.9.2 `srvr` output ever actually emit a line without `": "` (triggering the `IndexError`), or is this a theoretical-only defect?
