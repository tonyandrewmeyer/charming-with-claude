# valkey

Valkey is a Redis-compatible key-value store charm (k8s and VM/machine) from Canonical's data-platform team, providing Sentinel-based HA, TLS, S3 backup, and LDAP auth. The codebase is in excellent structural shape — clean architecture, 202 passing unit tests, zero pyright/lint warnings — but the project itself is early-stage and documented as "under active development and not yet production-ready." The most actionable fix is adding workload health monitoring: the charm reports `active/idle` indefinitely after a deliberate `pebble stop` of the valkey process. Next priorities are hardening file permissions (TLS private key and sentinel config are world-readable on K8s) and moving the topology observer's Sentinel password off the subprocess command line. Both VM and K8s substrates deployed cleanly on Juju 3.6 and 4.x during this review.

| | |
|---|---|
| Repo | canonical/valkey-operator @ `f3dc0b6` (2026-07-21) |
| Charms | valkey |
| Substrate | k8s (also VM via snap) |
| Deployed | yes — concierge-k8s-4 (juju 4.0.5), concierge-k8s-3 (juju 3.6.25), concierge-lxd-4 (juju 4.0.5, VM). All charmhub rev 65, channel 9/edge |
| Reviewed | 2026-07-31 |

## What it does

Deploys Valkey with Sentinel-based HA on Kubernetes or VMs. Supports client relations (`valkey-client`), TLS (`client-certificates` + internal peer TLS via self-signed certs), certificate transfer for external client CA, S3 backups (`create-backup`, `list-backups`), and LDAP authentication. Ships a topology observer subprocess that watches Sentinel for primary/replica role changes and updates K8s pod labels and services accordingly. Uses a reconciler pattern with per-component managers and a unified status handler.

## Deployment log

### Juju 4.0.5 (K8s) — concierge-k8s-4
```
juju add-model rv-valkey-k8s --controller concierge-k8s-4
juju deploy valkey --channel 9/edge --trust
```
- Rev 65 deployed from charmhub (repo HEAD `f3dc0b6` is same week).
- Single unit active in ~14s from start hook.
- Scaled to 3 units: all active in ~2.5 min via StartLock coordination.
- Scaled down to 2: ~1 min with graceful dataset save.
- Model destroyed after test.

### Juju 3.6.25 (K8s) — concierge-k8s-3
```
juju add-model rv-valkey-k8s-36 --controller concierge-k8s-3
juju deploy valkey --channel 9/edge --trust
juju deploy self-signed-certificates --channel edge
juju deploy s3-integrator --channel edge
juju integrate valkey self-signed-certificates:certificates
```
- Rev 65, same as local HEAD. Single unit active in ~30s.
- Added TLS relation → valkey entered maintenance "Enabling client TLS..." then active. K8s services `valkey-primary` and `valkey-replicas` created, pointing to port 6380.
- Removed TLS relation → brief error (sentinel connection refused during restart), then recovered to active. Config files retained TLS settings but the `valkey-server` process switched to plain port 6379.
- Scaled to 3, then back to 2: same coordinated StartLock behaviour as Juju 4.
- Integrated `s3-integrator` with no credentials → correctly blocked with "Missing or invalid S3 credentials". Removed relation → returned to active.
- `ldap-map="bad,,format"` accepted without error when no LDAP relation present (validation deferred until LDAP is connected).
- Model destroyed after test.

### Juju 4.0.5 (VM / LXD) — concierge-lxd-4
```
juju add-model rv-valkey-lxd --controller concierge-lxd-4
juju deploy valkey --channel 9/edge --trust --base ubuntu@24.04
```
- Rev 65. Single unit active in ~2 min (snap install + valkey startup).
- Ports opened: `6379-6380,26379-26380/tcp`.
- `status-detail` action: all 7 components active, identical to K8s output.
- SSH key issue prevented deeper machine-level inspection.
- Model destroyed after test.

### Cross-environment actions
- Actions available: `status-detail` (7 components active), `create-backup` ("No S3 relation. Integrate with s3-integrator first."), `list-backups` (same), `sync-ldap-users` ("LDAP not yet enabled on this unit"). Only 4 actions exist — `get-password`, `prefill-data`, `restart` are not defined on this charm.
- Config: `certificate-extra-sans="bad{malformed"` → `blocked` with clear message; reverting the value returns the charm to active.
- Failure: `pebble stop valkey` on valkey/0 (primary) → charm stays `active/idle` indefinitely. Confirmed on both Juju 3.6 and 4.0.5.
- Failure: `kill -9 $(pgrep valkey-server)` inside container → Pebble restarts the service within seconds (default `on-failure: restart` applies). Contrast with `pebble stop`, which is a deliberate stop and is not restarted.
- Failure: `kill -9 $(pgrep valkey-sentinel)` → Pebble restarts it too.
- Only 1 revision (65) on 9/edge; no `juju refresh` path testable.
- No behavioural differences observed between Juju 3.6 and 4.x; port listing differs cosmetically (3.6 shows ports as "none" when not exposed, 4.x always shows them).

## Observed behaviour

- **Startup time**: K8s ~14s from start hook to active; VM ~2 min (includes snap install).
- **Scale-up**: ~2.5 min for 3 units with coordinated rolling start via StartLock.
- **Scale-down**: ~1 min with graceful dataset save, sentinel reset, replica count verification.
- **Resource use**: `valkey-0` (primary) at 235m CPU / 132Mi RAM, `valkey-1` (replica) at 101m CPU / 76Mi RAM (`kubectl top`).
- **Ports**: 6379 (plain), 6380 (TLS), 26379 (sentinel plain), 26380 (sentinel TLS) — all opened on VM, dynamic on K8s.
- **Pebble services**: `valkey`, `valkey-sentinel`, `metric_exporter` — all `startup: enabled`. No explicit `on-failure`/`on-success` directive, so Pebble defaults to `on-failure: restart`. A crashed process is restarted, but a `pebble stop` (deliberate stop) is not. Confirmed: `kill -9` restarts within seconds; `pebble stop` stays inactive indefinitely.
- **K8s services created**: `valkey-primary`, `valkey-replicas` (ClusterIP, pointing to appropriate pods), `valkey-endpoints` (headless). Created via topology observer calling the k8s API.
- **Pod labels**: `role: primary` on valkey-0, `role: replica` on others.
- **Config rendering**: `valkey.conf` binds to the unit hostname (not `0.0.0.0`), enables the LDAP module by default. `primaryauth` password is cleartext in `valkey.conf` (required by Valkey replication auth). Sentinel config has cleartext passwords in `auth-pass` and `sentinel-pass`. `sentinel.conf` also carries a `# Generated by CONFIG REWRITE` section from Sentinel's own self-rewrites.
- **No workload health monitoring between update-status events**: `alive()` is only called at start and restart time. Observed valkey dead for 5+ minutes across multiple update-status cycles with the charm reporting `active/idle`. Not visible from code alone — only observable by running it.
- **Pebble `user: _daemon_`**: metadata declares uid `584792`; `/etc/passwd` maps uid `584792` to `_daemon_`, so the effect is correct, but the Pebble layer uses the string `_daemon_` rather than the numeric uid.
- **TLS integration lifecycle**: adding the `self-signed-certificates` relation triggers "Enabling client TLS..." status. Certs written to `/var/lib/valkey/tls/` with CA rehash symlinks. Removing the relation triggers a restart where sentinel briefly becomes unreachable ("Connection refused" on 26379), then recovers. Config files retain TLS settings; `valkey-server` switches to plain port.
- **File permissions on K8s**: all files under `/var/lib/valkey/` are `-rw-r--r--` (644), including `sentinel.conf` (contains sentinel passwords, owned `_daemon_:170` — group mismatch), `users.acl`, `sentinel-users.acl`, and `client.key` (TLS private key). The `mode=0o600` passed to `write_file` has no effect on K8s `ContainerPath`.
- **ACL files**: `users.acl` and `sentinel-users.acl` use SHA256 hashes (`#<hash>`) correctly. `valkey.conf` uses cleartext `primaryauth` for replication (required by Valkey).
- **VM substrate**: snap-based install via the `charmed-valkey` snap. Systemd services managed by Juju, not Pebble. Ports opened via `juju open-port`. Same 7-component status structure as K8s.

## Findings

### No workload health monitoring — charm reports active when valkey is deliberately stopped
- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/base_events.py:296-305` (`_on_update_status`)
- **Evidence**: `_on_update_status` only starts the topology observer if the unit is leader; it does not check `workload.alive()` or `cluster_manager.is_healthy()`. `alive()` exists (`src/workload_k8s.py:195-213`, with retry logic) but is only called from `workload.start()` (line 178) and `charm.py:129` (`_on_restart_workload`). Running `pebble stop valkey` on valkey/0: after 5+ minutes and multiple update-status cycles, the charm still showed `active/idle` while Pebble showed `valkey: inactive`. If valkey *crashes* (SIGKILL), Pebble's default `on-failure: restart` restarts it within seconds — the gap is specifically for deliberately stopped services or crashes Pebble fails to restart.
- **Impact**: A valkey process that Pebble cannot restart (config error causing immediate exit, OOM kill under memory pressure) goes undetected indefinitely. Operators relying on `juju status` will not know the database is down.
- **Fix**: In `_on_update_status`, check `self.workload.alive()` and `self.cluster_manager.is_healthy()`; if unhealthy, set a maintenance/blocked status and attempt recovery (emit `restart_workload`).
- **Linter rule**: mechanically checkable — flag update-status handlers that don't call an alive/health check.

### TLS private key file is world-readable (644)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/tls.py:86-87` (and similarly `276-277`)
- **Evidence**: `self.workload.write_file(private_key.raw, self.workload.tls_paths.client_key)` is called without a `mode` parameter. `write_file` (`src/core/base_workload.py:218`) delegates to `path.write_text(content, mode=mode, user=user, group=group)`, but on K8s, `ops.Container.push_path`/`ContainerPath` does not support mode setting — permissions default to the container filesystem's umask. Observed: `/var/lib/valkey/tls/client.key` was `-rw-r--r--` (644), owned `_daemon_:_daemon_`, readable by any process in the pod.
- **Impact**: The TLS private key is readable by any process in the pod container, violating least privilege; on shared nodes this could expose the key to neighbouring processes.
- **Fix**: on K8s, `chmod 600` the key file after writing; on VM, pass `mode=0o600` to `write_file` (works on real filesystems there).
- **Linter rule**: mechanically checkable — flag `write_file` calls where the path contains `key` and no `mode` argument is given.

### Topology observer passes password on command line
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/topology.py:79-96` (spawn args), `96` password arg
- **Evidence**: the subprocess is spawned with the sentinel admin password as a positional argument: `CharmUsers.SENTINEL_CHARM_ADMIN.value, self.state.cluster.internal_users_credentials.get(CharmUsers.SENTINEL_CHARM_ADMIN.value, "")`. Visible in `/proc/<pid>/cmdline` to any process on the same node. `src/common/client.py:48` explicitly avoids this pattern, using the `VALKEYCLI_AUTH` env var instead — the inconsistency is notable.
- **Impact**: password exposure via `/proc/cmdline` is a security concern, especially on shared nodes.
- **Fix**: pass the password through an environment variable or stdin, matching `ValkeyClient.build_command_prefix`.
- **Linter rule**: not generally mechanically checkable, but a rule flagging `subprocess.Popen` calls with a `password`-named variable in `args` would catch it.

### Sentinel config file contains cleartext passwords, and is world-readable
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/config.py:233-249` (`_generate_sentinel_configs`), `src/managers/config.py:262` (`set_sentinel_config_properties`)
- **Evidence**: the rendered `sentinel.conf` (observed via `kubectl exec`) contains `sentinel auth-pass primary <cleartext>` and `sentinel sentinel-pass <cleartext>`. Unlike the Valkey ACL file, which uses SHA256 hashes (`#<hash>`), sentinel requires plaintext in this file. `set_sentinel_config_properties` passes `mode=0o600` on write, but the observed file was `644` (owned `_daemon_:170`, a group mismatch), so the mode is being lost on the K8s write path.
- **Impact**: any process in the pod can read the sentinel passwords from the config file.
- **Fix**: investigate the Pebble/ContainerPath write path (same root cause as the TLS key finding above); `chmod 600` after write as a workaround.
- **Linter rule**: not mechanically checkable — requires runtime observation.

### Open issue #88: ACL for client relation users is too restrictive
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/managers/auth.py:133` (`_get_client_user_acl_lines`)
- **Evidence**: client relation user ACL grants `-@all +@read +@write +@keyspace +@pubsub +@transaction +info +ping +role`. Open GitHub issue #88 reports `CLIENT ID` and `CLIENT TRACKING` commands fail (`+ping` is already present, so `PING` itself should work). `+client` and `+client|tracking` are missing.
- **Impact**: client applications using connection pooling or client-side tracking will fail.
- **Fix**: add `+client +client|tracking` to the default ACL permissions.
- **Linter rule**: not mechanically checkable.

### `write_file` mode parameter ineffective on K8s via ContainerPath
- **Severity**: low
- **Kind**: lint
- **Where**: `src/managers/config.py:262-270`, `src/core/base_workload.py:218`
- **Evidence**: `write_file` accepts `mode=0o600` for the sentinel config (and elsewhere), which delegates to `path.write_text(content, mode=mode, user=user, group=group)`; on K8s this is `ContainerPath.write_text`, whose underlying `ops.Container.push_path` does not support mode setting. This is the underlying cause of both the sentinel-config and TLS-key permission findings above.
- **Impact**: operators may believe files are protected by restrictive permissions when they are not.
- **Fix**: after writing, run `chmod` in the container explicitly, or document that `mode` is advisory-only on K8s.
- **Linter rule**: not mechanically checkable.

### No `upgrade_charm` event handler
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py` — no `upgrade_charm` observer anywhere in `src/` (confirmed via `grep -rn upgrade_charm src/`)
- **Evidence**: the charm does not observe `upgrade_charm` or define an `_on_upgrade_charm` handler. On `juju refresh`, K8s pods are recreated so `start` refires and reinitialises; on VMs, there is no such reset, and config re-rendering relies on `config_changed`/`update_status` catching up. Only one revision (65) currently exists, so this has not been exercised in practice.
- **Impact**: a charm revision upgrade on VMs could leave the charm in a state where new-revision config changes are not applied until an unrelated event fires.
- **Fix**: add an `upgrade_charm` handler that re-renders configs and re-pushes the Pebble layer / snap config, matching `config_changed`.
- **Linter rule**: mechanically checkable — flag charms that don't observe `upgrade_charm`.

### Topology observer log file descriptor never closed
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/topology.py:104` (also referenced as line 84 in raw notes)
- **Evidence**: `stdout=open(self._log_file_path.as_posix(), "a")` with a comment stating "File shouldn't close." The handle is never assigned to a variable or closed. `start_observer` checks whether the old process is running via `os.kill(pid, 0)` but never closes the old file handle on restart.
- **Impact**: repeated observer restarts (triggered on every peer relation change) leak file descriptors over time, potentially hitting the ulimit.
- **Fix**: store the file handle and close it before opening a new one on restart; use a context manager or `atexit`.
- **Linter rule**: mechanically checkable — flag `open()` results that are never assigned to a variable.

### Valkey config retains TLS settings after TLS relation removal
- **Severity**: low
- **Kind**: bug
- **Where**: `src/events/tls.py` (`_on_client_tls_relation_broken`)
- **Evidence**: after removing the `self-signed-certificates` relation, `valkey.conf` still contained `tls-port 6380`, `tls-cert-file`, `tls-key-file`, `tls-ca-cert-dir` directives, even though the `valkey-server` process correctly switched to the plain port (6379). New internally-generated certs replaced the removed client certs, so the stale directives point to valid but different certs.
- **Impact**: cosmetic confusion for operators inspecting `valkey.conf`, who will see TLS apparently enabled when client TLS is disabled.
- **Fix**: on TLS relation removal, rewrite `valkey.conf` without `tls-*` directives, or at minimum set `tls-port 0`.
- **Linter rule**: not mechanically checkable.

### `ldap-map` config accepted without validation until LDAP relation exists
- **Severity**: low
- **Kind**: ux
- **Where**: LDAP config validation path (not further localized in draft/notes)
- **Evidence**: `ldap-map="bad,,format"` was accepted without error when no LDAP relation was present; validation is deferred until LDAP is actually connected.
- **Impact**: a malformed config value can sit unnoticed until an LDAP relation is added, at which point failure mode is unclear.
- **Fix**: validate `ldap-map` format at `config-changed` time regardless of relation state.
- **Linter rule**: not mechanically checkable.

### `is_healthy` called without clear `check_replica_sync` semantics after restart
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:129`, `src/managers/cluster.py:162`
- **Evidence**: `_on_restart_workload` calls `self.cluster_manager.is_healthy(check_replica_sync=False)`. The parameter defaults to `True` in the method signature. This is intentional for restart (the handler checks replica sync separately) but the naming reads ambiguously.
- **Impact**: misleading parameter semantics — future maintainers may misread the intent.
- **Fix**: rename to `skip_replica_sync_check: bool = False`, or invert the default.
- **Linter rule**: not mechanically checkable.

### `_reconfigure_quorum_if_necessary` runs on every peer relation event even when quorum is unchanged
- **Severity**: low
- **Kind**: performance
- **Where**: `src/events/base_events.py:261,295` (call sites), `src/events/base_events.py:694-716` (method body)
- **Evidence**: the method reads sentinel's configured quorum and compares it with `self.charm.config_manager.quorum` (line 714), but runs on *every* peer relation changed/departed event, including ones that don't change unit count. The comparison is cheap, but still issues sentinel CLI commands each time.
- **Impact**: unnecessary `SENTINEL primary`/`SENTINEL SET` commands on peer relation churn; minor, but adds up in chatty deployments.
- **Fix**: cache the last-reconciled quorum value and skip if unchanged.
- **Linter rule**: not mechanically checkable.

### `sync-ldap-users` action's real query path not unit tested
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/events/ldap.py` (`_on_sync_ldap_users_action`); `src/managers/topology.py` at 40% coverage, `src/events/ldap.py` at 77% coverage
- **Evidence**: LDAP sync has unit tests for config validation, but the actual LDAP query/connection path is mocked rather than exercised for failure modes.
- **Impact**: LDAP sync failure scenarios (connection timeout, bad credentials, malformed responses) are not covered.
- **Fix**: add unit tests for the LDAP-group-lookup path with mocked connections covering failure modes.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Unified status handler pattern**: `src/statuses.py` defines status objects as enums; `src/charm.py:57-70` instantiates a `StatusHandler` that aggregates statuses from every manager via `get_statuses()`. The `status-detail` action exposes this clearly — the cleanest status management seen in a data-platform charm.
- **Pydantic models for peer relation state**: `src/core/models.py` defines `PeerAppModel`, `PeerUnitModel`, and `S3Parameters` as pydantic models with validators, accessed via `data_interface.build_model()`. Combined with `InternalUsersSecret`/`ClientUsersSecret` annotations for Juju secrets, this eliminates stringly-typed relation data access.
- **RestartLock pattern**: `src/common/locks.py` — `RestartLock`/`StartLock` coordinate rolling restarts via peer databags; the leader grants the lock to one unit at a time, freed on completion. Prevents concurrent restarts from destabilizing the cluster.
- **Scale-down with dataset save and sentinel reset**: `src/events/base_events.py:440-500` — on scale-down, the departing unit fails over if primary, waits for replica sync, calls `save_dataset_before_shutdown` (BGSAVE + disable save-on-shutdown), stops valkey/sentinel, resets sentinel state on remaining units, and verifies expected replica count. Thorough, prevents data loss.
- **Backup safety**: `src/events/backup.py:186-189` sets a `BACKUP_IN_PROGRESS` status and guards `storage-detaching` against backups in progress. `_CountingReader` validates RDB magic bytes post-upload. `BACKUP_ID_FORMAT` uses UTC timestamps for deterministic, collision-resistant IDs.
- **AGENTS.md**: `/AGENTS.md` is detailed and explicit about invariants (backward compat, idempotency, eventual consistency, integration coverage) — useful for humans and AI agents alike. Every charm repo should have one.
- **Zero pyright errors**: `tox -e static` reports 0 errors, 0 warnings — rare for an ops charm.
- **Password-in-env, not argv**: `src/common/client.py:48` deliberately avoids `--pass` on the command line, using `VALKEYCLI_AUTH` instead; `exec_stream` in `src/managers/backup.py:219` does the same. (Contrast with the topology-observer finding above, which doesn't follow this pattern.)

## Common-practice notes

- **Follows convention**: `src/` layout, `charmcraft.yaml` with poetry plugin, `tox.ini` with format/lint/static/unit/integration environments, `lib/charms/` for Charmhub libraries — standard data-platform team patterns.
- **Unified `charmcraft.yaml`**: uses the new unified syntax but keeps `metadata.yaml` with a comment explaining it's "still required due to data-platform-workflows not supporting unified charmcraft.yaml syntax" — the workaround is documented, which is good practice.
- **Non-root container**: `metadata.yaml` declares `uid: 584792`/`gid: 584792` and `charm-user: non-root` — ahead of most data-platform charms, which still run as root.
- **`charmcraft.yaml` has explicit part documentation**: comments explain why each part exists — helpful, worth other charm repos adopting.
- **Platform support**: `charmcraft.yaml` declares both `amd64` and `arm64` — good for multi-arch.
- **Drift from convention**: the Pebble layer uses `_daemon_` rather than the numeric uid for `user`/`group`, while metadata declares `584792` numerically — functionally equivalent (uid 584792 maps to `_daemon_` in `/etc/passwd`) but an unusual documentation mismatch versus most charms, which use numeric uids throughout.
- **Sentinel port 26380 always opened**: `src/charm.py:134` opens port 26380 regardless of TLS state — correct, since sentinel always uses TLS internally (`tls-replication=yes`), but unusual compared to charms that gate port openings on TLS state.

## Tests

- **202 unit tests, all passing** (`tox -e unit`), 80% coverage overall. Local run: 202 passed in 19s, 0 failures.
- **Lint**: `tox -e lint` — codespell 0 errors, ruff 0 errors, ruff format 75 files already formatted, shellcheck 0 errors.
- **Static**: `tox -e static` — pyright 0 errors, 0 warnings, 0 informations.
- **Unit test files**: `test_backup.py` (55), `test_charm.py` (18), `test_client_relation.py` (15), `test_cluster_manager.py` (6), `test_config_manager.py` (11), `test_ldap.py` (22), `test_min_replicas_reconcile.py` (3), `test_scaledown.py` (8), `test_storage.py` (6), `test_substrates.py` (3), `test_tls.py` (33), `test_workload_exec_stream.py` (9), `test_workload_vm.py` (8).
- **Integration tests**: comprehensive — HA failover, network cut, scaling, two-unit availability, TLS, certificate rotation, certificate options, private key, client relations, LDAP, rootless K8s, S3 backup. Tests assert actual data (ping, set/get key, continuous-write consistency), not just active/idle.
- **Spread tests**: both K8s and VM substrates covered for failover, scaling, TLS, network cut, client relations, LDAP.
- **Lowest coverage**: `src/managers/topology.py` (40%), `src/workload_vm.py` (54%), `src/common/k8s_client.py` (56%), `src/common/client.py` (63%), `src/events/external_clients.py` (67%). Topology observer subprocess management and K8s API client paths have the least coverage.
- **Test gaps relative to observed risks**: no unit test verifies `_on_update_status` performs a health check (it doesn't); the leaked-file-descriptor path in `topology.py:104` is uncovered; there is no `upgrade_charm` test because there's no handler; LDAP `sync-ldap-users` connection-failure paths are mocked but not exercised for error handling.

## Docs

- **README.md**: good — explains what the charm is, basic usage, links to full docs, community, contributing.
- **ReadTheDocs**: full Diátaxis structure — tutorial, how-to guides (deploy, clients, LDAP, TLS, manage-passwords, scale-horizontally), reference. Tutorial walks through MicroK8s + Multipass setup, deploying, scaling, password rotation, client relations, TLS.
- **Development docs**: `AGENTS.md` is excellent architecture documentation; `CONTRIBUTING.md` covers setup.
- **Charmhub description**: brief but accurate, matches observed behaviour.
- **Doc/reality mismatch**: none found. The tutorial's `juju deploy valkey --channel 9/edge --trust` worked as documented; the client how-to's mention of mutual TLS as a prerequisite matches the code (`tls-auth-clients` set to `optional` with `CN` auth).

## Open questions

- **Does sentinel's own `# Generated by CONFIG REWRITE` section conflict with charm-rendered config?** Sentinel rewrites its own config on certain events; if the charm later re-renders `sentinel.conf`, the REWRITE section (observed containing `latency-tracking-info-percentiles`, `sentinel myid`, `sentinel config-epoch`, `sentinel leader-epoch`, `sentinel current-epoch`) might be overwritten. Would settle by testing a config change after sentinel has run for hours and checking whether sentinel IDs/epochs survive.
- **Why does the Pebble `user` field show `_daemon_` instead of `584792`?** Fine functionally, but confusing against the metadata's numeric declaration. Would settle by checking whether the rock hardcodes or derives the username.
- **Does the topology observer handle TLS CA rotation cleanly?** The observer stores the CA cert at start time (`src/managers/topology.py:87`) and is restarted on CA rotation (`src/events/base_events.py:342`), picking up the new CA — but if that restart fails silently (only logged), the observer would keep running with a stale CA. Would settle by running a CA-rotation integration test with the observer active.
