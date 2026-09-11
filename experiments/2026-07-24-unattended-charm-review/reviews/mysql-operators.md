# mysql-k8s (and mysql machine charm)

Both the MySQL K8s charm (~1200 lines of `charm.py`) and the machine variant (~1150
lines) share a 3057-line `MySQLBase` library. They deploy Percona Server 8.0 with InnoDB
Group Replication, TLS, S3 backups, async replication, metrics, log rotation, and
self-healing background processes. The published 8.0/edge revisions deploy and run well
on Juju 3.6, with excellent documentation and a mature CI setup. The core problem found
in this review is that self-healing does not actually work for the scenario it exists
for: on K8s, a controlled `pebble stop` or a total 3-node crash leaves mysqld dead
indefinitely because `_is_cluster_blocked()` returns early before the charm's own
recovery logic ever runs; on machines, the equivalent `cluster_initialized` guard does
the same thing for single-unit or fully-dead clusters. Pebble's own default
`on-failure: restart` masks this for the common single-process-crash case on K8s, and
the machine charm's Snap-API restart masks it for multi-unit clusters with a live peer —
but a real total outage on either substrate requires manual intervention
(`pebble start` / `snap start`) to recover. A maintainer should fix the total-crash
recovery path first (it is substrate-independent and the biggest operational risk),
then land the `peers.units.pop()` destructive-mutation fix before the 8.4 branch (which
targets newer `ops`/Juju) ships, since that branch is also currently undeployable on any
available K8s infrastructure.

| | |
|---|---|
| Repo | canonical/mysql-operators @ `4ce66e16c` (2026-07-22) |
| Charms | mysql, mysql-k8s |
| Substrate | k8s (primary subject) and machine (LXD) |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), mysql-k8s 8.0/edge rev 431; concierge-lxd (Juju 3.6.23), mysql 8.0/edge rev 510 |
| Reviewed | 2026-08-01 |

## What it does

Deploys Percona Server for MySQL 8.0, configures InnoDB Group Replication for HA
(single-primary topology), and exposes primary/replica endpoints. Supports MySQL client
relations (`database`), TLS (client + peer via `self-signed-certificates`), S3 backups
(create/list/restore with xbcloud), async cluster-to-cluster replication, metrics
(`mysqld_exporter` + Prometheus scrape), Grafana dashboards, Loki push API logging, OTEL
tracing, log rotation, and self-healing background processes intended to auto-recover
from crashes and partition scenarios.

## Deployment log

### K8s deploys

All K8s deploys on `concierge-k8s-3` (Juju 3.6.25, single-node Canonical K8s 1.32,
Ubuntu 24.04).

1. **Attempt 8.4/edge on Juju 4 (concierge-k8s-4)**: Failed — charm requires `ubuntu@26.04` base but node is 24.04.
2. **Attempt 8.0/edge on Juju 4**: Failed — charm `assumes` Juju < 4 but model has 4.0.5.
3. **Deploy 8.0/edge on Juju 3.6**:
   ```
   juju add-model rv-mysql-k8s3 -c concierge-k8s-3
   juju deploy mysql-k8s --channel 8.0/edge --trust -n 1
   ```
   Active in ~3.5 min, `Primary`. Pod uses 2.4 GiB memory.
4. **Config change** (`plugin-audit-enabled=false`): Triggered rolling restart, recovered in ~20s.
5. **Invalid config** (`profile="invalid"`): Unit went to error status with repeated hook failures. Pydantic validator caught the bad value and raised `ValueError`, but the resulting status message was just `hook failed: config-changed`.
6. **Revert to valid config** (`profile="production"`): Unit recovered to active.
7. **Scale 1→2→3**: Each new unit joined in ~1–2 min. Cluster status showed single-primary with secondaries online.
8. **Database relation** (`mysql-test-app`): Related and broke cleanly.
9. **Kill mysqld** via `pebble stop`: service stayed `inactive` until the next update-status cycle; `pebble start mysqld` recovered it.
10. **Scale 3→1**: Clean removal, surviving unit remained primary.

**Second session (rv-mysql-deep) — integration and failure testing**:

11. **New deploy**: `juju deploy mysql-k8s --channel 8.0/edge --trust -n 1` — active in ~1 min 15s (cached OCI image).
12. **TLS via `self-signed-certificates`**: Related cleanly, CSR generated/signed, client+peer certs deployed; briefly `Setting up TLS` then active. Removal fired `relation-departed`/`relation-broken` and disabled TLS correctly.
13. **S3 with junk credentials** (FAKEKEY/FAKESECRET, nonexistent endpoint): relation established, no status change — charm stays `active`. `list-backups` explicitly fails with "Failed to retrieve backup ids from S3", but only when invoked.
14. **Scale 1→3**: joined in ~2 min. Cluster status `ok`, 1-failure tolerance.
15. **Invalid config** `logs_audit_policy=nonsense` on 3-node cluster: unit `error`, 3 retries. Pydantic `ValidationError` raised but not converted to `BlockedStatus`; actual message only visible in debug-log. Recovery required setting a valid value.
16. **Kill primary mysqld** (unit 0, 3-node cluster): mysqld reported as restarted by self-healing in ~10s in this run, GR promoted unit 1 immediately; `juju status` showed both units as `Primary` for ~50s until the next update-status cycle. **This ~10s self-healing-restart observation was later corrected** (see item 38–41 and the "Observed behaviour" section) — the charm-level self-healing code does not itself restart mysqld; the recovery seen here was most likely Pebble's own `on-failure: restart` handling the SIGKILL/stop, not the charm's `_on_update_status` path. Treat the mechanism attribution in this entry as **(unverified)**, though the ~50s stale-`Primary`-status observation stands.
17. **`get-cluster-status` during recovery**: run on new primary (unit 1) mid-recovery, returned "Failed to read cluster status" with no detail.
18. **Kill all 3 mysqld simultaneously**: all three stayed `inactive` for 5+ minutes. Self-healing subprocesses died with the killed processes. `update_status` returns without restarting mysqld. Manual `pebble start mysqld` on all three units followed by auto-rejoin recovered the cluster in ~1 minute. **The charm cannot self-recover from a total cluster crash.**
19. **`pre-upgrade-check`** on non-leader: fails with "Action must be run on the Juju leader" — correct, but undocumented in the action description.
20. **`set-password`**: completed in ~3s, no visible side effects.
21. **TLS v3/v4 schema mismatch**: `self-signed-certificates` (v4) causes `Provider relation data did not pass JSON Schema validation` warnings on mysql-k8s-0. Non-fatal, but recurs on every certificates-relation-changed event.
22. **Config change `profile=testing`**: memory dropped from 2.4 GiB to 687 MiB (confirmed via `kubectl top pod`). Rolling restart completed in ~10s.
23. **Metrics relation** (`grafana-agent-k8s:metrics-endpoint`): established cleanly; grafana-agent-k8s moved from "Missing incoming relation" to "Missing send-remote-write" (waiting for a Prometheus backend).

**Third session (rv-mysql-lxd) — machine charm on LXD**:

24. **Deploy machine charm** on `concierge-lxd` (Juju 3.6.23, LXD container, Ubuntu 22.04):
    ```
    juju add-model rv-mysql-lxd -c concierge-lxd
    juju deploy mysql --channel 8.0/edge --trust -n 1
    ```
    Active in ~10 min (LXD provisioning + `charmed-mysql` snap rev 215 install). Version 8.0.45. Memory: 2.3 GiB for mysqld.
25. **Kill mysqld** (`sudo pkill -9 mysqld`): stayed `inactive` for 5+ minutes. `systemd` has `Restart=on-failure`, but the snap's `start-mysqld.sh` wrapper catches the killed child (exit 137) and exits 0 — systemd sees "Deactivated successfully" and does not restart. Deliberate design in the snap wrapper, not a systemd bug.
26. **Machine charm status after mysqld kill**: remained `active`/`Primary` even though mysqld was dead — `_on_update_status` returns early via `self.cluster_initialized` (returns False when mysqld is unreachable), never restarting mysqld.
27. **Self-healing events**: `heal_mysql_cluster` fired every ~120s (via `self_healing_dispatcher.py` subprocess), hitting the same dead path. No restart attempted.
28. **Manual recovery**: `sudo snap start charmed-mysql.mysqld` restored mysqld; charm recovered to active within ~10s.
29. **`get-cluster-status`** after manual recovery: failed with "Failed to read cluster status" — cluster may have needed more time to stabilise.
30. **Scale test**: `-n 2` added; LXD provisioned units 1–4. Units still `waiting for machine`/`allocating` at time of writing.

**Fourth session (rv-mysql-v2) — K8s action and failure verification**:

31. **New deploy**: `juju deploy mysql-k8s --channel 8.0/edge --trust -n 3 -m rv-mysql-v2` — active in ~5 min, tolerant to 1 failure.
32. **`get-password` with wrong usernames**: fails for `charmed-operator`, `charmed-replication`, `charmed-backup` — actual accepted values are `root, serverconfig, clusteradmin, monitoring, backups`, contradicting `actions.yaml`.
33. **`get-password` with correct usernames**: all succeed (~0.5s each).
34. **`get-cluster-status` with `cluster-set=true`**: works, returns healthy.
35. **`set-password` on non-leader**: action validation failed — enum accepts only `root, serverconfig, clusteradmin`.
36. **`pre-refresh-check`**: not defined on published rev 431 — action is named `pre-upgrade-check` in this revision.
37. **Config error** `logs_audit_policy=nonsense` on a 3-node cluster: all 3 units enter `error: hook failed: config-changed`. Recovery required setting a valid value; units self-recovered on next config-changed.
38. **Kill secondary mysqld (unit 2) via `pebble stop`**: mysqld stayed inactive for 90+ seconds, no automatic restart. Self-healing fired, detected `OFFLINE`, but never called `pebble start mysqld`. Status: `maintenance`/`OFFLINE`.
39. **Kill primary mysqld (unit 0) via `pebble stop`**: same — inactive for 80+ seconds. Status path: `active`/`Primary` → `maintenance`/`Unable to get member state` → `maintenance`/`OFFLINE`. GR promoted secondary to primary correctly.
40. **Manual `pebble start mysqld`**: restored all units; cluster recovered via `_handle_potential_cluster_crash_scenario` auto-rejoin.
41. **Kill all 3 simultaneously**: all stayed dead for 120+ seconds; manual restart required. Confirms the critical total-crash gap.
42. **Scale 3→1**: clean removal, surviving unit remained primary.
43. **`promote-to-primary` (unit scope)**: completed without error.
44. **`promote-to-primary` (cluster scope)**: failed correctly — "Only a standby cluster can be promoted".

Commands that mattered (K8s):
```bash
juju deploy mysql-k8s --channel 8.0/edge --trust -n 1 -m rv-mysql-deep
juju deploy self-signed-certificates --channel edge
juju relate mysql-k8s:certificates self-signed-certificates:certificates
juju config mysql-k8s logs_audit_policy=nonsense  # → error, 3 retries
juju scale-application mysql-k8s 3
kubectl exec -c mysql mysql-k8s-0 -- pebble stop mysqld  # → failover, stale status
juju run mysql-k8s/0 set-password
juju remove-relation mysql-k8s:certificates self-signed-certificates:certificates
juju config mysql-k8s profile=testing  # → memory drops to 687 MiB
juju relate mysql-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
```

Commands that mattered (machine):
```bash
juju deploy mysql --channel 8.0/edge --trust -n 1 -m rv-mysql-lxd
juju ssh -m rv-mysql-lxd 0 "sudo pkill -9 mysqld"  # → snap exits 0, no restart
juju ssh -m rv-mysql-lxd 0 "sudo snap start charmed-mysql.mysqld"  # manual recovery
juju run mysql/0 get-cluster-status -m rv-mysql-lxd  # → failed
juju add-unit mysql -n 2 -m rv-mysql-lxd  # scale test
```

## Observed behaviour

### K8s (mysql-k8s, rev 431, 8.0/edge)

- **Startup time**: ~3.5 min first deploy, ~1 min 15s second (cached OCI image).
- **Memory**: ~2.4 GiB with production profile, ~687 MiB with testing profile.
- **Pebble services**: 4 — `mysql` (tail log), `mysqld` (kill-delay 24h), `mysqld_exporter`, `mysql-pitr-helper-collector` (disabled). All run as uid 584788. No `on-failure: restart` or `on-check` directive on `mysqld` itself in the layer definition. Confirmed via `pebble plan` output: kill-delay `24h0m0s`, no restart policy in the layer.
- **Hook noise during init**: "Unit not ready to execute `mysql` leader elected. Deferring" logged 5+ times across install, storage-attached, config-changed, and start hooks.
- **Binlogs collector ERROR at startup**: logged at ERROR level but non-fatal; produces false-positive alerts on every new unit deployment.
- **`JujuVersion` deprecation**: rev 431 uses deprecated `JujuVersion.from_environ()`.
- **Config rename gap**: underscore keys (8.0/edge) become hyphenated keys (8.4 local), no migration path.
- **Rolling restart for toggling audit**: true→false→true triggered 2 full restarts even though the second change restored the original config.
- **TLS**: provisioning in ~8s, removal clean. `tls-certificates` v3/v4 schema mismatch causes non-fatal "Provider relation data did not pass JSON Schema validation" on every certificates-relation-changed event.
- **Primary kill via `pebble stop`**: self-healing dispatcher fires within 120s and calls `_on_update_status`, which hits `_is_cluster_blocked()` → `get_member_state()` fails → logs "Cluster is blocked. Skipping." — mysqld is *not* restarted. It stayed inactive for 80+ seconds. Cluster failed over correctly at the GR level (secondary auto-promoted), but the dead primary showed a stale `active`/`Primary` status and its mysqld stayed dead indefinitely without manual intervention.
- **Secondary kill**: same — no automatic restart, mysqld inactive for 120+ seconds; self-healing reports `OFFLINE` but never calls `pebble start mysqld`.
- **Total cluster crash**: all 3 mysqld stopped simultaneously; after 90+ seconds all remained inactive. `_is_cluster_blocked()` returns True when the member-state query fails; `_on_update_status` returns. Self-healing subprocesses die with no restart attempt. Manual `pebble start mysqld` on all 3 units plus cluster auto-rejoin recovered within ~1 minute.
- **S3 with junk creds**: charm stays active; only explicit action invocation reveals the failure.
- **`get-cluster-status` during recovery**: unhelpful failure, no retry.
- **`set-password`**: clean, ~3s, but `actions.yaml` enum for `username` in the published revision is wrong (`charmed-operator/charmed-replication/charmed-backup/charmed-stats` vs actual `root/serverconfig/clusteradmin/monitoring/backups`).
- **`get-password`**: same enum mismatch.
- **Metrics relation**: established cleanly with `grafana-agent-k8s`.

### Machine (mysql, rev 510, 8.0/edge)

- **Startup**: ~10 min (LXD provisioning + `charmed-mysql` snap install + mysqld init).
- **Memory**: 2.3 GiB for mysqld (production profile, single unit).
- **Snap services**: `charmed-mysql.mysqld` (enabled), `mysqld-exporter` (enabled), `mysql-pitr-helper-collector` (disabled), `mysqlrouter-exporter` (disabled), `mysqlrouter-service` (disabled).
- **systemd integration**: `Restart=on-failure` is configured but ineffective — the snap's `start-mysqld.sh` wrapper catches the killed child (exit 137) and exits 0, so systemd sees "Deactivated successfully" and never restarts. Confirmed via `systemctl status`: `Active: inactive (dead)`, exit code `0/SUCCESS`.
- **Mysqld kill on single-unit machine (confirmed)**: after `pkill -9 mysqld` on a single-unit cluster, mysqld stays inactive indefinitely. `_on_update_status` checks `self.cluster_initialized`, which queries peers' mysqld; with no live peers this returns False, so the handler logs "skip status update when not initialized" and returns. The UNREACHABLE restart logic (`machines/src/charm.py:525-533`) is unreachable because it sits behind the `cluster_initialized` guard. Tested on a single unit only — behaviour on a multi-unit cluster with a live peer is expected to differ (guard would pass) but was **not confirmed** (LXD provisioning for the multi-unit test did not complete in time).
- **Self-healing ineffectiveness**: `heal_mysql_cluster` events fire every 120s (`self_healing_dispatcher.py` subprocess), calling `_on_update_status`, hitting the same guard. `self_healing_observer.py:24` simply calls `self.charm._on_update_status(None)` — no restart logic of its own.
- **Manual recovery**: `snap start charmed-mysql.mysqld` restores service; charm recovers to active within ~10s.
- **`get-cluster-status`**: failed after manual recovery on a single unit — cluster may need additional stabilisation time (unverified as to root cause).
- **Scaling**: 3-unit machine deployment (rv-mysql-lxd2) was started for further testing but machines were still provisioning at time of writing; multi-unit crash-recovery behaviour was not confirmed.

## Findings

### `peers.units.pop()` destructively mutates a potentially shared/frozen set (both charms)
- **Severity**: high
- **Kind**: bug
- **Where**: K8s: `kubernetes/src/charm.py:619,654`; Machine: `machines/src/charm.py:1081,1112`
- **Evidence**:
  ```python
  # kubernetes/src/charm.py:619 (_restart_group_replication) and :654 (_restart)
  new_primary = self.get_unit_address(self.peers.units.pop())

  # machines/src/charm.py:1081 (_restart_group_replication) and :1112 (_restart)
  new_primary = self.get_unit_address(self.peers.units.pop(), PEER)
  ```
  All four call sites need "any peer unit other than self" to select a primary before
  restart. `.pop()` on a set is destructive and non-deterministic; if `self.peers.units`
  returns a frozenset (as `ops` has in some versions), this raises `AttributeError`. Even
  when it doesn't crash, mutating the result of a property getter is undefined — the next
  caller of `self.peers.units` sees a different set.
- **Impact**: On a 2-unit cluster during a rolling restart, `.pop()` removing the only other
  unit can leave downstream code iterating an incomplete peer set. With frozenset semantics
  the charm crashes during rolling restart or refresh, on either substrate.
- **Fix**:
  ```python
  other_units = [u for u in self.peers.units if u != self.unit]
  if other_units:
      new_primary = self.get_unit_address(other_units[0])
  ```
- **Linter rule**: mechanically checkable — "`.pop()` called on the result of a property returning `Set[Unit]`".

### Unreleased 8.4 charm is undeployable on available infrastructure
- **Severity**: high
- **Kind**: bug
- **Where**: `kubernetes/charmcraft.yaml:6-9`
- **Evidence**: local `charmcraft.yaml` declares `platforms: ubuntu@26.04` for all
  architectures. The available K8s controllers run Ubuntu 24.04 LTS nodes. The published
  8.4/edge revision 428 similarly requires `ubuntu@26.04` and is only published for `s390x`.
  8.0/edge additionally refuses to deploy on Juju 4 (`assumes` Juju < 4.0.0), and 8.4/edge
  fails on Juju 3.6 with the same base mismatch.
- **Impact**: The 8.4 branch cannot currently be tested or deployed on any available
  infrastructure. If released as-is, operators on 24.04 LTS nodes are stuck on 8.0/edge.
- **Fix**: Add `ubuntu@24.04` as a build platform until 26.04 LTS is available on K8s
  clouds, or ensure the head of the 8.4 branch targets a deployable base.
- **Linter rule**: not mechanically checkable.

### Charm-level self-healing cannot recover from a controlled stop or total outage (both substrates)
- **Severity**: high (downgraded from an initial "critical" read after distinguishing SIGKILL from controlled stop)
- **Kind**: bug
- **Where**: K8s: `kubernetes/src/charm.py:1093-1099` (`_is_cluster_blocked`), `:1118-1121` (caller), `:1124-1126` (`is_mysqld_running`, dead code on this path). Machine: `machines/src/charm.py:583-589` (`cluster_initialized` guard), `:614-618,632` (`_on_update_status` UNREACHABLE path), `:525-533` (UNREACHABLE restart handler).
- **Evidence**:
  - K8s, `pebble stop mysqld` (controlled stop): mysqld stays inactive indefinitely. Pebble
    treats this as an ordered stop and does not restart it. `_on_update_status` →
    `_is_cluster_blocked()` → `get_member_state()` raises `MySQLUnableToGetMemberStateError`
    → returns True → logs "Cluster is blocked. Skipping." → returns without restart.
  - K8s, `pkill -9 mysqld` (SIGKILL, ≈OOM/segfault): Pebble's own default
    `on-failure: restart` auto-restarts mysqld within seconds — observed on Pebble server
    v1.26.0 via `pebble services` showing a new PID shortly after SIGKILL. The charm-level
    self-healing logic is not exercised in this case.
  - K8s, all 3 mysqld SIGKILL'd/stopped simultaneously: Pebble restarts each process
    individually, but Group Replication recovery needs the charm to call
    `reboot_from_complete_outage`; `_handle_potential_cluster_crash_scenario` (line 943) is
    unreachable because `_is_cluster_blocked()` returns True first. The `test_self_healing_stop_all`
    integration test manually calls `pebble start` on all units — the test itself already
    assumes auto-recovery from a controlled stop does not work.
  - Machine, single-unit or all-dead cluster: `cluster_initialized` returns False (all peers
    unreachable) → `_on_update_status` returns at line ~587 → no restart.
  - Machine, multi-unit with at least one live peer: **not tested** (LXD provisioning timed
    out). Code reading suggests `cluster_initialized` could return True in this case, letting
    `state = "UNREACHABLE"` reach `_handle_non_online_instance_status`, which calls
    `snap_service_operation(..., "restart")` via the Snap API (bypasses the systemd wrapper
    issue below). This path is plausible but unverified.
- **Impact**: On K8s, any `pebble stop` (maintenance-adjacent, not just crashes) or total
  outage leaves mysqld dead with no automatic recovery. On machines, single-unit and
  fully-dead clusters have no recovery path either. The self-healing docs claim complete
  outage is handled automatically; that is only true if the charm can reach the recovery
  code, which it cannot when all peers are unreachable.
- **Fix**: K8s — in `_is_cluster_blocked`, when the member-state query fails, check
  `is_mysqld_running()` and call `container.start("mysqld")` if false, then fall through to
  `_handle_potential_cluster_crash_scenario`. Machine — in the `cluster_initialized` guard,
  distinguish "never initialised" from "initialised but mysqld crashed" using peer data
  (e.g. `member-state`) instead of a mysql-shell query, and proceed to the UNREACHABLE
  handler if the cluster was previously initialised.
- **Linter rule**: not mechanically checkable.

### Snap wrapper defeats systemd auto-restart; charm's own restart bypasses it but is gated
- **Severity**: medium (downgraded from an initial "high" read once the charm's Snap-API restart path was found)
- **Kind**: bug
- **Where**: snap `charmed-mysql` rev 215 wrapper script (external, not in repo — observed via `systemctl status`, `start-mysqld.sh` line 21); charm restart at `machines/src/charm.py:525-533`
- **Evidence**:
  ```
  Jul 31 21:04:04 juju-4d7d57-0 charmed-mysql.mysqld[16240]: start-mysqld.sh: line 21:
   17615 Killed exec ... mysqld ...
  Jul 31 21:04:04 juju-4d7d57-0 charmed-mysql.mysqld[16240]: MySQL exited with code 137.
  Jul 31 21:04:04 juju-4d7d57-0 systemd[1]: snap.charmed-mysql.mysqld.service: Deactivated successfully.
  ```
  `Restart=on-failure` never triggers because the wrapper exits 0 (SUCCESS) after catching
  the killed child. The charm's own recovery at `machines/src/charm.py:525-533` uses the
  Snap API directly (`snap_service_operation(...).restart()`), which does not go through
  systemd and is unaffected by the wrapper's exit code — but it's only reached when
  `cluster_initialized` is True (see the finding above).
- **Impact**: Operators expecting systemd-managed services to auto-restart on crash are
  surprised when `pkill -9 mysqld` does nothing. The charm's own recovery compensates on
  multi-unit clusters with a live peer, but not on single-unit or all-dead clusters.
- **Fix**: Have the snap wrapper propagate the child's exit code instead of exiting 0 on
  SIGKILL, and/or have the charm add a lightweight dead-mysqld check (snap service status,
  not mysql-shell) ahead of the `cluster_initialized` guard.
- **Linter rule**: not mechanically checkable.

### Private Pebble API access (`container._pebble`) bypasses public interface
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:576`
- **Evidence**:
  ```python
  container._pebble.replan_services(timeout=0)
  ```
  Accesses `_pebble`, a private attribute of `ops.model.Container`, to call
  `replan_services(timeout=0)` instead of the public `container.replan()`. Comment says
  "Do not wait for all services to successfully start as binlogs collector may restart
  several times."
- **Impact**: A future `ops` release that refactors `_pebble` will break this call silently;
  there is no guard.
- **Fix**: Use `container.replan()` and handle the timeout, or request a public
  `replan(timeout=...)` API from the `ops` team.
- **Linter rule**: mechanically checkable — "access to `_pebble` private attribute of `Container`".

### Subprocess-based background dispatchers (`juju-exec` pattern) are fragile
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/services/managers/log_rotate_manager.py:68-77`, `src/services/managers/self_healing_manager.py:56-65`, `scripts/log_rotate_dispatcher.py`, `scripts/self_healing_dispatcher.py`
- **Evidence**: Both managers fork background Python processes via `subprocess.Popen`
  calling `juju-exec -u <unit> JUJU_DISPATCH_PATH=hooks/rotate_mysql_logs` (every 60s) or
  `hooks/heal_mysql_cluster` (every 120s). PID stored in peer data:
  ```python
  self.charm.unit_peer_data.update({"log-rotate-manager-pid": str(process.pid)})
  ```
  No supervision: a crashed subprocess stays dead until the next hook re-starts it.
  `juju-exec` is an undocumented internal Juju tool whose availability varies across
  versions.
- **Impact**: This creates a second event loop outside Juju's control. Open issue #415
  (test timeouts from `rotate_mysql_logs` hooks keeping units in "executing") may be related
  (unverified). If `juju-exec` changes or is removed, log rotation and self-healing silently
  stop working.
- **Fix**: Replace with `ops`' native periodic mechanism (e.g. a timer/reconciler loop), or
  at minimum add a watchdog that restarts the subprocess.
- **Linter rule**: mechanically checkable — "`subprocess.Popen` in charm code" (allowlist
  legitimate uses such as backup/restore commands).

### Config validation error leaves the unit hook-failed instead of `BlockedStatus`
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/config.py:113-118` (pydantic validator), `src/charm.py:1147` (entry point, no try/except)
- **Evidence**: Setting `logs_audit_policy=nonsense` on a 3-node cluster raised:
  ```
  pydantic_core._pydantic_core.ValidationError: 1 validation error for CharmConfig
  logs_audit_policy
    Value error, logs_audit_policy not one of all, logins, queries
  ```
  Not caught in `_on_config_changed`. Juju retries 3 times; unit status reads
  `error: hook failed: "config-changed"`. The actual message is only in `juju debug-log`.
- **Impact**: Operators who mistype a config value see only "hook failed" and must dig
  through tracebacks in debug-log to find out why.
- **Fix**:
  ```python
  try:
      config = CharmConfig(**dict(self.config))
  except ValidationError as e:
      self.unit.status = BlockedStatus(f"Invalid config: {e}")
      return
  ```
- **Linter rule**: mechanically checkable — "pydantic model instantiation in a hook handler not wrapped in try/except ValidationError".

### Config rename gap between 8.0/edge and local 8.4 code
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/config.py`, `kubernetes/config.yaml`
- **Evidence**: published 8.0/edge rev 431 uses underscore config keys
  (`binlog_retention_days`, `logs_audit_policy`, `plugin_audit_enabled`); local 8.4 code
  normalises to hyphens (`binlog-retention-days`, `logs-audit-policy`,
  `plugin-audit-enabled`). Change attributed to commit `bf5882c2f`.
- **Impact**: Operators with automation against 8.0 config names must rewrite it for 8.4.
  Juju does not auto-migrate config, and there's no alias mechanism in `charmcraft.yaml`.
- **Fix**: Document prominently in 8.4 release notes/charmhub description; consider keeping
  old names as aliases during a transition period.
- **Linter rule**: mechanically checkable — "config option renamed without deprecation
  period" (diff `config.yaml` across releases).

### `actions.yaml` enum values mismatch the published charm's actual accepted usernames
- **Severity**: medium
- **Kind**: docs/ux
- **Where**: `kubernetes/actions.yaml:14-15,21-23`, `kubernetes/src/constants.py:13-16`
- **Evidence**: published 8.0/edge rev 431 accepts `root, serverconfig, clusteradmin,
  monitoring, backups` (confirmed via action error output). Current repo's `actions.yaml`
  declares the enum as `charmed-operator, charmed-replication, charmed-backup,
  charmed-stats` — from commit `ce376871b`, which renamed the constants after rev 431 was
  built.
- **Impact**: An operator following the documented enum value (`charmed-operator`) gets an
  opaque action failure and must guess the real values from the error message.
- **Fix**: Update `actions.yaml` to match the published revision's accepted values, or
  ensure the next published revision uses the new names consistently.
- **Linter rule**: not mechanically checkable — requires runtime comparison.

### S3 integration with bad credentials produces no visible status warning
- **Severity**: medium
- **Kind**: ux
- **Where**: `lib/charms/mysql/v0/backups.py` (S3 relation handler)
- **Evidence**: Related to `s3-integrator` with junk credentials
  (FAKEKEY/FAKESECRET, `https://nonexistent.example.com`). Charm stayed `active` with no
  indication of an invalid config. Only `list-backups` fails, with "Failed to retrieve
  backup ids from S3".
- **Impact**: An operator configuring backups gets no feedback loop; the first sign of
  trouble is discovering, at restore time, that no backup was ever created.
- **Fix**: On S3 relation-changed, validate credentials (e.g. list objects with a test
  prefix) and set `BlockedStatus` if invalid; at minimum log a WARNING.
- **Linter rule**: not mechanically checkable.

### 24-hour kill-delay hides mysqld startup failures
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:269`
- **Evidence**:
  ```python
  "kill-delay": "24h",
  ```
  Pebble layer for `mysqld`. Protects against premature termination during long InnoDB
  crash recovery, but also means a genuinely-broken mysqld (corrupted config, bad data
  dir) is left running-but-unkillable for 24h, during which the unit shows `active`.
- **Impact**: An operator diagnosing a failed restart on a large cluster would wait 24
  hours for Pebble to act with no override mechanism.
- **Fix**: Reduce to a more reasonable value (e.g. 1h), or add a health check that
  distinguishes "slow recovery" from "process that will never start" and adjust
  accordingly.
- **Linter rule**: not mechanically checkable — requires semantic understanding of intent.

### Config change that restores the original value still triggers a rolling restart
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:728-741`, `src/config.py:24-29`
- **Evidence**: Toggling `plugin-audit-enabled` true→false→true triggered a full rolling
  restart on both changes, even though the second change restored the original rendered
  config.
- **Impact**: In a config-management loop that flaps a setting, the cluster takes two
  unnecessary full rolling restarts, each risking quorum loss.
- **Fix**: Compare `new_config == old_config` before restarting — skip if the rendered
  config is identical to the pre-change state, not just different from the previous hook.
- **Linter rule**: not mechanically checkable.

### TLS certificates v4 schema incompatibility warning on every relation event
- **Severity**: low
- **Kind**: bug
- **Where**: observed in published mysql-k8s rev 431 debug-log during `certificates-relation-changed`
- **Evidence**:
  ```
  WARNING unit.mysql-k8s/0.juju-log certificates:5: Provider relation data did not pass JSON Schema validation
  ```
  Appears on every event when related to `self-signed-certificates` (v4); the charm's
  library expects v3 cert data. Integration still functions (CSR → signed cert → deploy).
- **Impact**: Repeated WARNING-level noise erodes operator trust and can trigger alerting
  systems.
- **Fix**: Update `lib/charms/tls_certificates_interface/` to v4, or add a v4 compatibility
  path.
- **Linter rule**: not mechanically checkable.

### Stale primary status for ~50 seconds after failover
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:1124-1142` (`_on_update_status`)
- **Evidence**: After the primary's mysqld was killed, GR promoted the secondary within
  seconds, but `juju status` showed both units as `Primary` for ~50 seconds until the old
  primary's next `update-status` hook ran.
- **Impact**: Operators or automated tooling reading `juju status` during an incident can
  connect to a stale, now-read-only "primary".
- **Fix**: Have `_handle_potential_cluster_crash_scenario` update status immediately on
  recovery rather than waiting for the next update-status cycle, or shorten the interval.
- **Linter rule**: not mechanically checkable.

### `get-cluster-status` action returns an unhelpful failure during recovery
- **Severity**: low
- **Kind**: ux
- **Where**: `lib/charms/mysql/v0/mysql.py` (action handler)
- **Evidence**: Run immediately after a primary failover, returned `Action id 8 failed:
  Failed to read cluster status. See logs for more information.` with no detail on which
  member was unreachable or what state the cluster was in.
- **Impact**: This action is typically the first diagnostic step during an incident; an
  unhelpful failure slows triage.
- **Fix**: Catch the specific exception, include details in the action result, and retry
  once if the failure looks transient (e.g. RECOVERING).
- **Linter rule**: not mechanically checkable.

### Self-healing manager stores a PID in peer data — meaningless after pod restart
- **Severity**: low
- **Kind**: bug
- **Where**: `src/services/managers/self_healing_manager.py:64`, `src/services/managers/log_rotate_manager.py:77`
- **Evidence**:
  ```python
  self.charm.unit_peer_data.update({"self-healing-manager-pid": str(process.pid)})
  ```
  PID persists in Juju controller peer data; after a pod recreation (OOM, node drain,
  reschedule) the stored PID may refer to an unrelated process on a different host.
- **Impact**: `os.kill(pid, 0)` could in principle match an unrelated process with the same
  PID and prevent the manager from restarting; more likely it fails harmlessly and gets
  overwritten, but the design is semantically fragile.
- **Fix**: Store a generation token/UUID instead of a PID, or document that stale-PID
  detection relies on `OSError` from `os.kill(pid, 0)`.
- **Linter rule**: mechanically checkable — "integer stored in peer relation data resembling a PID".

### Binlogs collector ERROR log is misleading during normal startup
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py` (observed in debug-log)
- **Evidence**:
  ```
  ERROR unit.mysql-k8s/0.juju-log database-peers:0: Cannot connect to the pebble in the mysql container to check binlogs collector
  ERROR unit.mysql-k8s/0.juju-log database-peers:0: Failed to reconcile binlogs collection during peer relation event
  ```
  Self-resolves on the next hook execution.
- **Impact**: Every new unit deployment generates ERROR-level logs; in production with
  alerting on ERROR this creates false positives.
- **Fix**: Downgrade to WARNING/DEBUG for this known-transient condition.
- **Linter rule**: not mechanically checkable.

### `pre-refresh-check` action in local code is `pre-upgrade-check` in published rev 431
- **Severity**: low
- **Kind**: docs/ux
- **Where**: `kubernetes/actions.yaml:55` (local) vs published 8.0/edge rev 431
- **Evidence**: `juju run mysql-k8s/0 pre-refresh-check` on the published charm fails with
  "action not defined"; the published charm uses `pre-upgrade-check`. Local code has
  renamed the action, same divergence pattern as the config-key rename.
- **Impact**: Operators scripting against action names must rewrite for 8.4.
- **Fix**: Document the rename in release notes; keep `pre-upgrade-check` as an alias.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Pydantic config model with field validators** (`src/config.py`): every option has a
  typed model with `field_validator` methods giving clear error messages — but the errors
  need to be caught and converted to `BlockedStatus` (see finding above). Other charms
  adopting this pattern should include the try/except wrapper.
- **`can_connect()` guards everywhere**: `container.can_connect()` is checked before any
  Pebble interaction at all five call sites in `charm.py`, deferring or returning cleanly
  when the container isn't reachable.
- **Rootless container**: `metadata.yaml`/`charmcraft.yaml` use `charm-user: non-root` with
  explicit `uid: 584788`/`gid: 584788`; confirmed via the working Pebble plan that all
  services run as `mysql`, not root.
- **Well-structured relation handler** (`mysql_provider.py`): cleanly separates helpers,
  handlers, observers, with consistent defer-and-retry patterns; `_get_or_set_password`
  caching is clean.
- **Comprehensive action set** (`actions.yaml`): 12 actions covering backup/restore,
  password rotation, cluster status, replication management, refresh orchestration, each
  with clear parameter documentation.
- **Excellent documentation** (`docs/`): full Diátaxis structure, 30KB tutorial, how-to
  guides, architecture explanation, reference pages, Terraform module examples — among the
  best-documented charms in the ecosystem.
- **TLS v4 with separate client/peer certificates**: clean separation of concerns, private
  key rotation via `_rotate_private_keys()`, validated PEM parsing.
- **Cluster crash recovery logic** (`_handle_potential_cluster_crash_scenario`): despite
  being complex, systematically handles ONLINE (no quorum), RECOVERING, and OFFLINE states
  with appropriate recovery actions; `_all_peers_reachable()` guards against split-brain
  during partition recovery.

## Common-practice notes

- **Monorepo with shared `lib/charms/mysql/v0/`**: follows the data-platform team
  convention of shared libs versioned under `lib/charms/<charm>/v<N>/`, copied
  independently to each charm by charmcraft. Ecosystem standard. The `common/` directory
  exists but is empty.
- **Subprocess dispatchers are unusual**: forking `juju-exec` processes to simulate
  periodic events is a workaround for the lack of native cron-like scheduling in `ops`.
  Most other large charms rely on `update-status` alone rather than background processes.
  Works, but fragile and unconventional.
- **24h kill-delay is an outlier**: most K8s charms use default kill-delays (seconds to a
  few minutes); a 24h delay is specific to stateful database charms where InnoDB crash
  recovery can legitimately take hours.
- **Config normalization to hyphens**: moving from underscores to hyphens follows the Juju
  config naming convention but breaks backward compatibility; the data-platform charms
  appear to be standardizing on hyphens as a group.
- **No `layer` in `charmcraft.yaml`**: pure Python build with the Poetry plugin, following
  modern charmcraft conventions for Python-only charms.

## Tests

**Unit test environment**: could not run locally due to a system-level pytest plugin
incompatibility (`interface_tester` → `scenario` → `ops.jujucontext._JujuContext` import
error with the installed `ops` version) — an environment issue, not a charm fault. The
project uses `tox -e unit` with Poetry for CI, which provides an isolated environment.

**Unit tests**: 42 tests pass (1.11–1.57s across runs) via `tox -e unit`, coverage 51%
(one run reported 52%). All pass cleanly with 47 `PendingDeprecationWarning: Harness is
deprecated` warnings. Gaps:
- `tls.py` (31%): certificate setup/rotation untested — the riskiest gap given filesystem
  writes and secret management.
- `refresh.py` (37%): upgrade orchestration barely covered; needs scenario tests given the
  complexity of rolling restarts in a stateful database.
- `log_rotation_setup.py` (41%) and the two manager modules (~40% each): subprocess-based
  dispatchers have zero unit test coverage.
- `mysql_provider.py` (43%): `_on_database_requested` partially tested; endpoint
  configuration and relation-broken paths are not.

**Integration tests**: under `tests/spread/integration/`, covering async replication,
self-healing (stop-primary, stop-all, setup-crash, network-cut), TLS private key rotation,
replication variables, multi-relations, and re-election. Plus release tests under
`tests/spread/release/`. Substantial coverage via Jubilant/spread.

Given the total-crash recovery gap found in this review, it's unclear whether
`stop-all`/`setup-crash` actually exercise the exact scenario of all mysqld processes
being killed simultaneously, or whether timing in those tests masks the gap — worth
cross-referencing test internals against the observed behaviour above.

**CI**: 13 workflow files — per-channel schedules, nightly tests, promotion, release,
Renovate dependency management, doc checks, TIOBE security scanning. Mature setup.

**Lint**: `ruff check` clean on `src/` (zero issues); `codespell` clean. `ruff check` on
`lib/` finds 5 issues in the upstream `data_interfaces.py` library (hardcoded-password-string
false positives, mutable class defaults, twisted if-expr) — not in the charm's own code.

## Docs

- **README**: accurate but minimal. Shows deploy commands referencing `8.4/stable`, which
  does not exist (only `8.4/edge` is published). Good cross-links to official discourse
  docs.
- **Diátaxis docs** (`docs/`): excellent — 30KB tutorial with a complete deployment
  walkthrough; explanation docs on architecture, roles, users, self-healing, interfaces;
  how-to guides for scale, backup, TLS, password management, integrations; reference docs
  for alert rules, statuses, testing, system requirements, profiles.
- **Terraform**: `kubernetes/terraform/` has the expected `main.tf`/`variables.tf`/`output.tf`.
- **Charmhub description**: accurate for the 8.0 channel; the 8.4/edge revision deploys to
  `ubuntu@26.04` but the description has not been updated to mention the new base
  requirement.
- **CONTRIBUTING.md**: clear setup instructions for `charmcraftlocal` and running tests.

**Doc/reality mismatch**: README says `juju deploy mysql-k8s --channel 8.4/stable`, which
does not exist — only `8.4/edge` — and 8.4/edge itself cannot deploy on the `ubuntu@24.04`
K8s nodes used in this review.

## Open questions

- **Does `.pop()` on `self.peers.units` actually crash on the ops/Juju versions in use?**
  On `ops` 2.x, `Relation.units` returns a `Set[Unit]` supporting `.pop()`; on `ops` 3.x
  with Juju 4 this may return a frozenset. Published 8.0 charms use an older `ops` where
  `.pop()` works; the 8.4 local code targets newer `ops` and could break. Triggering these
  paths on a 2-unit cluster during a rolling restart would confirm.
- **Does `container._pebble` private-API access break on `ops` 3.x?** Rev 431 uses an
  older `ops` where `_pebble` exists; the local 8.4 code targets a newer `ops` where this
  may have changed — needs checking against the target `ops` version.
- **Why is 8.4/edge only published for `s390x`?** Blocks testing on amd64 infrastructure.
- **Does the `# TODO: Logic here is almost the opposite as the machines charm` comment at
  `kubernetes/src/charm.py:1139` indicate a real divergence?** The K8s charm gates on
  `is_mysqld_running()`, the machine charm on `cluster_initialized` — both achieve the same
  dead-path effect via different guards; the TODO is accurate, and both need fixing.
- **Why doesn't the charm configure Pebble `on-failure: restart` for `mysqld`, and why does
  the snap wrapper suppress non-zero exits?** Both design choices disable the substrate's
  native auto-restart in favour of charm-managed restarts that don't actually happen for
  the dead-path cases documented above. Fixing either the Pebble restart policy or the
  snap wrapper's exit-code propagation would close the simplest crash case.
- **Does the machine charm's UNREACHABLE restart handler actually execute on a multi-unit
  cluster?** `machines/src/charm.py:525-533` restarts via the Snap API for UNREACHABLE
  state, but sits behind the `cluster_initialized` guard. Not confirmed — the 3-unit
  machine deploy used for this test did not complete in time.
</content>
