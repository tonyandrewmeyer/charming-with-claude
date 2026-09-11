# mongos-k8s-operator review

A thin k8s charm (~35 lines of charm code) wrapping the shared `mongo-charms-single-kernel` v1.8.52 library to deploy `mongos` as a router for sharded MongoDB clusters. All business logic lives in the shared library, so its bugs hit four charms at once (mongodb-k8s, mongodb-vm, mongos-k8s, mongos-vm).

The 8/edge track is currently unusable: a `processUmask` string-vs-integer bug in the MongoDB 8.0.10 image prevents the config-server from starting, so no full sharded cluster can be deployed on 8/edge — and this silently breaks the integration tests, which deploy config-server from 8/edge with `raise_on_error=False`. The 6/edge track works end-to-end (data-integrator, NodePort external access, scale-up/down, pod recovery, TLS, LDAP), but has a critical defect where `start_charm_services` skips the config-server-URI check, plus a cluster of status-reporting bugs (stale TLS-blocked status, stale post-reintegration status, duplicate LDAP statuses) and a hook crash on `certificates-relation-broken` that can permanently stall k8s scale-down. No unit tests exist, and the integration test suite cannot even install its dependencies. Architecture and code quality are otherwise good (Pydantic config, manager/handler separation, Juju secrets, lightkube k8s management).

**A maintainer should first**: fix the `start_charm_services` config-server-URI guard (critical, low-risk one-line fix) and the `processUmask` int/string bug in the shared library, then reconcile the repo's declared `single_kernel_mongo` version against what's actually packed into the published 6/edge charm — the published charm has methods (`disable_certificates_for_unit`) that don't exist in the repo's own lock file, which means bugs cannot be reliably reproduced or fixed from the repo alone.

| | |
|---|---|
| Repo | canonical/mongos-k8s-operator @ `1b936dd` (2026-07-23) |
| Charms | mongos-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25): 8/edge rev 163/164 (failed, image bug), 6/edge rev 165 (successful, incl. data-integrator, scale, relation-remove/reintegrate, TLS+removal, LDAP+glauth, pod-recovery, kill-recovery, bad-config, actions); concierge-k8s-4 (Juju 4.0.5): 6/edge rev 165 (successful, identical behaviour) |
| Reviewed | 2026-08-10 |

## What it does

Deploys a `mongos` router for sharded MongoDB K8s clusters. Requires integration with a `mongodb-k8s` config-server via the `cluster` relation. Provides a `mongos_proxy` endpoint so client applications can connect. Supports TLS via peer-certificates/client-certificates relations (or the single `certificates` relation on the published 6/edge charm), LDAP authentication, external access via NodePort, and refresh/upgrade orchestration. One of four charms in the MongoDB ecosystem (mongodb-k8s, mongodb-vm, mongos-k8s, mongos-vm) sharing a common single-kernel library.

## Deployment log

**Attempt 1 — Juju 3.6.25 (concierge-k8s-3), 8/edge rev 163 alone:**

```
juju add-model rv-mongos-deep
juju deploy mongos-k8s --channel 8/edge --trust
```

Settled to `blocked: The cluster relation with the config-server is missing.` as expected. Unit status `blocked`, app status `active` (see finding). Actions `status-detail`, `pre-refresh-check`, `force-refresh-start` all worked. Bad configs `expose-external=invalid_value` and `pause-after-unit-refresh=bad_value` were caught gracefully with clear status messages. A double-period typo appeared in the combined unit message: `Missing cluster relation.. Run 'status-detail'...`.

Integrated with `self-signed-certificates` via `peer-certificates`: TLS handler correctly ignored the certificate, logging `mongos is not running (not integrated to config-server). Ignoring certificate.` — good guard.

**Attempt 2 — Full 8/edge cluster on Juju 4.0.5 (concierge-k8s-4):**

```
juju deploy mongos-k8s --channel 8/edge --trust
juju deploy mongodb-k8s --channel 8/edge --config role="config-server" config-server --trust
juju deploy mongodb-k8s --channel 8/edge --config role="shard" shard0 --trust
juju integrate shard0:sharding config-server:config-server
juju integrate mongos-k8s:cluster config-server:cluster
```

config-server's mongod entered a crash loop (exit code 48):
```
Error setting up listener: /tmp/mongodb-27017.sock\u0000 :: Permission denied
```
The null byte suggests a `processUmask` parsing issue in the PSMDB 8.0.10 image. mongos-k8s showed `waiting: Connecting to config-server...` indefinitely since config-server never shared its URI. mongos also crash-looped with `BadValue: error: no args for --configdb`, starting despite having no config-server URI.

**Attempt 3 — Juju 3.6.25, same 8/edge deployment:** Identical behaviour; the image bug reproduces on both Juju 4.x and 3.6.

**Attempt 4 — Full 6/edge cluster:**

```
juju deploy mongodb-k8s --channel 6/edge --config role="config-server" config-server --trust
juju deploy mongodb-k8s --channel 6/edge --config role="shard" shard0 --trust
juju integrate shard0:sharding config-server:config-server
juju integrate mongos-k8s:cluster config-server:cluster
```

Worked. All four applications reached `active` within ~3 minutes. mongos accepted PyMongo connections on port 27018 (not standard 27017 — see finding). Resource usage: mongos-k8s pod 59m CPU / 74Mi memory.

**Attempt 5 — Cross-version (8.x mongos + 6.x config-server):** mongos connected at TCP level but hit wire-version incompatibility (MongoDB 8.0 = wire 25 vs 6.0 = wire 17). Status stuck at `Waiting for mongos to start...` while mongos was actually running and logging `IncompatibleServerVersion`. The charm doesn't detect or report version incompatibility.

**Attempt 6 — Full 6/edge cluster with data-integrator (Juju 3.6.25):** Deployed mongos-k8s, config-server, shard0 (6/edge), data-integrator (latest/edge), self-signed-certificates (1/edge). Cluster reached `active` within ~3 minutes. Integrated data-integrator via `mongos_proxy`; credentials shared correctly, `get-credentials` returned a valid URI on port 27018. Enabled `expose-external=nodeport` — URI updated to `10.42.160.130:32465`, confirming external access works.

**Attempt 7 — Scale-up (6/edge):** Scaled to 2 units; second unit active after ~3 minutes (rolling-ops lock). Scaled back to 1: clean teardown.

**Attempt 8 — Kill mongos process:** `kill -9` on mongos — Pebble restarted it within seconds. Unit never left `active`.

**Attempt 9 — Remove cluster relation (6/edge):** Charm correctly stopped mongos (`Stopped mongos daemon` in log), but **unit status remained `active`** and `status-detail` showed `mongos: Active` for ~3 minutes until the next `update-status` hook. Pebble `mongos` service was `inactive` the whole time.

**Attempt 10 — Reintegration after relation removal (6/edge):** Re-added the cluster relation. mongos restarted correctly (pebble `active since 13:11 UTC`). But **app status stayed `blocked: The cluster relation with the config-server is missing.`** while unit was `active` and mongos running. Only cleared when a scale 1→2 triggered a fresh hook cycle.

**Attempt 11 — 6/edge cluster on Juju 4.0.5:** Identical behaviour to 3.6.25 — same `processUmask: '037'` (parsed correctly as integer 31 by MongoDB 6.0), same port 27018, same status components. No Juju-version-specific differences.

**Attempt 12 — TLS mismatch (8/edge):** Integrated mongos-k8s 8/edge with `self-signed-certificates`, then with config-server 6/edge. Cluster manager detected `Mongos uses peer TLS but config-server does not` and raised `DeferrableFailedHookChecksError` — but this only appeared in `debug-log`; `juju status`/`status-detail` showed `Connecting to config-server...`. Operators cannot see the real problem without reading debug-log.

**Attempt 13 — Bad config values:** `expose-external=invalid_value` caught gracefully: `The expose-external config option is invalid. Valid options are 'nodeport' and 'none'.` Identical on Juju 3.6 and 4.x.

**Attempt 14 — 6/edge cluster with TLS:** Deployed full 6/edge cluster plus `self-signed-certificates`, integrated `mongos-k8s:certificates` (note: the 6/edge relation is named `certificates`, not `peer-certificates` as in current HEAD). After receiving the certificate, mongos detected `Mongos uses TLS but config-server does not` and went `blocked` — correctly detected and reported at app-status level this time. But `juju status` unit message still showed `Connecting to config-server...`. Removing the relation triggered `Disabling TLS...` and mongos became active — but the **app-level `blocked` status persisted** even after the unit fully recovered (unit active, mongos serving, `status-detail` showing `mongos: Active`). Survived multiple update-status cycles and was still present when the model was destroyed.

**Attempt 15 — Data-integrator with stale TLS status present:** Integrated `data-integrator` via `mongos_proxy` while the stale TLS blocked status persisted. `mongos_proxy-relation-changed` repeatedly failed with uncaught `PrematureDataAccessError: Premature access to relation data, update is forbidden before the connection is initialized.` The handler at `events/database.py:109` only catches `PyMongoError`, `FailedToGetHostsError`, `DatabaseRequestedHasNotRunYetError`. After configuring data-integrator's `database-name` and a pod restart, the relation resolved and credentials flowed (port 27018).

**Attempt 16 — Pod deletion/restart:** `kubectl delete pod` — Kubernetes recreated it within ~10 seconds; unit went maintenance → active. mongos resumed, data-integrator relation resolved. Stale TLS app-blocked status unchanged through the restart. Clean, no intervention needed.

**Attempt 17 — Action discrepancy:** `juju actions mongos-k8s` on 6/edge rev 165 shows `force-refresh-start`, `pre-refresh-check`, `set-tls-private-key`, `status-detail`. The repo's `actions.yaml` has `status-detail`, `pre-refresh-check`, `force-refresh-start`, `resume-refresh`. `set-tls-private-key` was removed from the repo (replaced by `tls-peer-private-key`/`tls-client-private-key` config), `resume-refresh` was added but not yet published. `juju run mongos-k8s/0 resume-refresh` on rev 165 fails with `action "resume-refresh" not defined`. Running `set-tls-private-key` fails with `RuntimeError: Relation certificates does not exist`.

**Attempt 18 — Full 6/edge cluster with LDAP, glauth-k8s, self-signed-certificates, data-integrator (Juju 3.6):** Deployed mongos-k8s, config-server, shard0 (6/edge), glauth-k8s (edge, --trust), self-signed-certificates, data-integrator (latest/edge), postgresql-k8s (14/edge, --trust; needed by glauth). All reached active. `mongos-k8s:certificates` ↔ `self-signed-certificates:certificates`: TLS mismatch correctly detected (`TLS must be disabled in mongos, since it is disabled on the config-server`) with clear `status-detail` action message. `mongos-k8s:ldap` ↔ `glauth-k8s:ldap` plus `ldap-certificate-transfer` ↔ `send-ca-cert`: mongos correctly detected missing LDAPS on glauth (`LDAPS not enabled on LDAP application.`). Unit status showed `Waiting for both LDAP data and Glauth certificates.` → after glauth active: `Missing LDAP data from Glauth.`, with **duplicate LDAP status components** (`Blocked` + `Waiting` simultaneously on the same `ldap` component).

**Attempt 19 — TLS removal on scaled-up cluster:** With 2 mongos units and mismatched TLS active, removed the `certificates` relation. Unit 0 entered maintenance `Disabling TLS...` and recovered. Unit 1 (still starting: `Connecting to config-server...`) **crashed** with `hook failed: "certificates-relation-broken"` — traceback: `disable_certificates_for_unit` → `restart_charm_services(force=True)` → `set_running_status(...)` rejects a non-running status (`Waiting for mongos to start...`). Unit 1 stuck in error. App-level blocked status persisted ~5 minutes until scale-down 2→1 triggered a status recompute, which cleared it. Unit 1's hook failure blocked scale-down: stalled at `2/1`.

**Attempt 20 — Integration test run:** `tox -e integration` failed immediately during dependency install — `python-ldap` build requires `lber.h`/`ldap.h` (LDAP headers), not available in the review environment: `fatal error: lber.h: No such file or directory`.

**Attempt 21 — Scale-down with stuck unit:** After attempt 19's crash, scale-down to 1 unit stalled indefinitely at `2/1`. `juju remove-unit` on k8s doesn't support removing a named unit. Model destruction was required to clean up.

**Lint:** `tox -e lint` passed clean (codespell, ruff check, ruff format, shellcheck). `tox -e terraform-lint` fails locally (terraform not installed on review machine — not a code defect). `charmcraft analyse` crashes with `IsADirectoryError`. `ruff check src/` reports `I001` import order. `ruff check deps/` reports `E501` on docstrings in `abstract_charm.py`.

**Tests:** No unit tests exist (`tox.ini` has no `unit` env). Integration tests (`tests/integration/test_charm.py`) were read but not run — they deploy config-server with `8/edge` (currently broken) and use `raise_on_error=False`, which would mask the failure. Spread tests run the integration tests in LXD/CI.

## Observed behaviour

- **Container image defect:** OCI image `ghcr.io/canonical/charmed-mongodb@sha256:8b816bb...` runs mongod via `/bin/start.sh` → `setpriv --clear-groups --reuid mongodb --regid mongodb -- /usr/bin/mongod`. mongod fails to bind `/tmp/mongodb-27017.sock` with "Permission denied", and the error path contains a null byte. The config writes `processUmask: '037'` as a YAML string rather than integer, the likely cause. Not observable from code alone — `"037"` is valid YAML, but MongoDB 8.0 apparently misparses it. Confirmed MongoDB 6.x parses the same string correctly as decimal 31 (`{"processUmask":{"default":63,"value":31}}` in logs); only 8.x is affected.
- **mongos starts without config-server URI:** When the `cluster` relation exists but no URI has been shared yet, mongos still calls `start_charm_services()`, writing a config missing `sharding.configDB` and starting the process, which crashes with `BadValue: error: no args for --configdb` in a Pebble restart loop (seen via `pebble logs mongos`).
- **No observable recovery:** After 30+ minutes neither config-server nor mongos recovered on 8/edge; config-server's mongod stayed in backoff so no URI was ever shared.
- **Resource usage (6/edge):** mongos-k8s 59m CPU / 74Mi memory; config-server 197m / 221Mi; shard0 7m / 162Mi; self-signed-certificates 13m / 28Mi.
- **Scale-up timing:** ~3 minutes total for a second mongos unit (rolling-ops lock → service start).
- **Kill-recovery:** Pebble restarted mongos within <15 seconds of `kill -9`, no charm intervention.
- **Status staleness after relation removal:** `juju status` stayed `active` for ~2.5 minutes after mongos was actually stopped, until the next `update-status`.
- **TLS mismatch invisible in status:** Real error only in `debug-log`; `juju status`/`status-detail` showed `Connecting to config-server...` with no TLS component at all on 6/edge (8/edge does report a `tls` component).
- **Double-period typo:** Combined blocked-status message renders `Missing cluster relation.. Run 'status-detail':...` with no space and a double period.
- **6/edge vs 8/edge status components diverged:** 6/edge reports `upgrade`, `mongos`; 8/edge reports `upgrades`, `mongos`, `tls`, `ldap`. Deploying 6/edge into a model previously hosting 8/edge produced stale-status-cleanup warnings.
- **Port 27018 used for mongos, not standard 27017:** Config file shows `net.port: 27018`. `tests/integration/helpers.py:27` hardcodes `MONGOS_PORT = 27018`, confirming this is deliberate, not a bug.
- **App status lags behind unit status after reintegration:** After remove/re-add of the cluster relation, app-level status stayed `blocked: The cluster relation with the config-server is missing.` while the unit was `active` and mongos running; `status-detail` also showed `mongos: Active`. Cleared only after a scale-triggered hook cycle.
- **Data-integrator integration works end-to-end:** Username/password/URI shared correctly over `mongos_proxy`; `expose-external=nodeport` updated the data-integrator URI from ClusterIP (`mongos-k8s-0.mongos-k8s-endpoints:27018`) to NodePort (`10.42.160.130:32465`).
- **Scale-up uses rolling ops lock:** second unit transitions `Connecting to config-server...` → active; both units run mongos independently; scale-down clean (absent the crash in attempt 19).
- **Juju 4.x vs 3.6 identical for 6/edge:** No behavioural differences observed.
- **Integration tests may be silently broken:** `deploy_cluster_components` deploys config-server/shard on `8/edge` regardless of mongos channel; with the `processUmask` bug, config-server never starts, but `wait_for_idle(raise_on_error=False)` masks the failure — tests likely time out or false-negative rather than fail loudly.
- **TLS blocked app status never clears:** After TLS integrate-then-remove, the app-level `blocked: TLS must be disabled...` status survives multiple `update-status` cycles and a pod restart even though the unit is fully recovered. Root cause: `cluster_manager.tls_statuses()` sets the app-scope status on relation-changed/created, but `_on_relation_broken` doesn't recompute or clear it.
- **`PrematureDataAccessError` crashes `mongos_proxy` handler:** When data-integrator integrates before sending initial relation data, `reconcile_mongo_users_and_dbs` → `update_diff` → `update_relation_data` raises `PrematureDataAccessError`, not caught by the tuple in `events/database.py:109` (`PyMongoError`, `FailedToGetHostsError`, `DatabaseRequestedHasNotRunYetError`). Hook enters error state, retries every ~10s; recovers once the requirer sends data or a pod restart re-triggers the event.
- **Action drift:** rev 165 has `force-refresh-start`, `pre-refresh-check`, `set-tls-private-key`, `status-detail`; repo's `actions.yaml` has `status-detail`, `pre-refresh-check`, `force-refresh-start`, `resume-refresh`. Missing action errors cleanly; the orphaned `set-tls-private-key` on the published charm produces a traceback (`RuntimeError: Relation certificates does not exist`) instead.
- **Pod recovery clean:** `kubectl delete pod mongos-k8s-0` recreated within ~10s; unit maintenance → active; data-integrator relation resolved after recovery; no operator action needed.
- **6/edge relation name is `certificates`, not `peer-certificates`:** Published rev 165 uses `certificates`; current HEAD `metadata.yaml` uses split `peer-certificates`/`client-certificates`. `juju integrate mongos-k8s:peer-certificates` fails on rev 165 with `application "mongos-k8s" has no "peer-certificates" relation` — current README integration commands don't match the published 6/edge charm.
- **Duplicate LDAP status components:** Simultaneous `Blocked: LDAPS not enabled on LDAP application.` and `Waiting: Missing LDAP data from Glauth.` both under component `ldap` — the LDAP status handler doesn't clear previous statuses before adding new ones.
- **Scale-down blocked by hook failure:** A crashed hook on one unit stalls `juju scale-application` indefinitely on k8s (units cannot be individually removed); only recovery is model destruction or a charm fix.
- **Published charm uses a different `single_kernel_mongo` version than repo deps:** rev 165's traceback shows `disable_certificates_for_unit` in `tls.py`, a method absent from the repo's declared dependency (v1.8.52), whose `tls.py` instead calls `self.manager.disable_tls(internal)`. Confirms the published charm was built against a different library resolution than the lock file declares.
- **LDAP integration reveals glauth LDAPS requirement:** Correctly reported in `status-detail` (`Blocked | ldap | LDAPS not enabled on LDAP application.`), but the less-specific `Missing LDAP data from Glauth.` is what shows in the primary unit status message.

## Findings

### Critical: `start_charm_services` does not check for config-server URI before starting mongos
- **Severity**: critical
- **Kind**: bug
- **Where**: `deps/single_kernel_mongo/managers/mongos_operator.py:288-289`, `:426-432` (ships as `mongo-charms-single-kernel` v1.8.52)
- **Evidence**:
  ```python
  # prepare_for_startup, line 288-289
  if self.state.mongos_cluster_relation:
      self.start_charm_services()
      return
  ```
  `start_charm_services` (line 426-432) has no URI guard, unlike `restart_charm_services` (line 440-444) which correctly raises `MissingConfigServerError` if `self.state.cluster.config_server_uri` is unset.
- **Impact**: When mongos-k8s is integrated with a config-server that hasn't yet shared its URI (e.g. still starting), `mongos_cluster_relation` is truthy so `prepare_for_startup` calls `start_charm_services` anyway. This writes a config missing `sharding.configDB` and starts mongos, which crashes (`BadValue: error: no args for --configdb`) and enters a Pebble restart loop that does not self-heal even after the config-server later succeeds. Observed on both Juju 3.6 and 4.x.
- **Fix**: Add the `config_server_uri` check to `start_charm_services`, or to `prepare_for_startup` before calling it; defer or set a waiting status instead of starting.
- **Linter rule**: not mechanically checkable as a simple pattern (the absence of the URI check is a semantic gap), but the pattern "`mongos_cluster_relation` truthy → `start_charm_services()` with no `config_server_uri` check nearby" could be flagged.

### High: `processUmask` passed as string instead of integer, corrupts MongoDB socket path
- **Severity**: high
- **Kind**: bug
- **Where**: `deps/single_kernel_mongo/managers/config.py:433` (ships as `mongo-charms-single-kernel` v1.8.52)
- **Evidence**: `"setParameter": {"processUmask": "037"}` serializes via `yaml.safe_dump` to `processUmask: '037'` — a YAML string, not an integer. mongod (8.0.10) logs `Error setting up listener: /tmp/mongodb-27017.sock\u0000 :: Permission denied`, the null byte consistent with a string-to-int parse failure. The container runs mongod as the `mongodb` user via `setpriv`, and `/tmp` is writable by that user, ruling out a straightforward permission issue.
- **Impact**: Blocks mongod from starting on the current MongoDB 8.0.10 image, making the entire sharded cluster undeployable on 8/edge. MongoDB 6.0 parses the same string correctly as decimal 31, which is why the bug is 8.x-specific and likely why it isn't caught in CI.
- **Fix**: Use the integer `0o37` (or `31`) instead of the string `"037"`.
- **Linter rule**: "`processUmask` in `setParameter` is not an integer literal" — mechanically checkable by flagging string literals passed to known integer MongoDB config keys.

### Medium: `certificates-relation-broken` crashes on non-ready unit — `set_running_status` rejects non-running status
- **Severity**: medium
- **Kind**: bug
- **Where**: published charm rev 165, `single_kernel_mongo/managers/tls.py` (`disable_certificates_for_unit`) and `managers/mongos_operator.py` (`restart_charm_services`); code not present in repo deps v1.8.52
- **Evidence**: Traceback from `debug-log`: `events/tls.py:143 _on_tls_relation_broken` → `managers/tls.py:210 disable_certificates_for_unit` → `mongos_operator.py:336 restart_charm_services(force=True)` → `status_handler.set_running_status(...)` raises `ValueError: Status ... is not a running status.` Triggered when the relation is removed while a unit's workload status is `Waiting for mongos to start...` (non-running).
- **Impact**: Leaves the unit in permanent hook-error state. On k8s, units cannot be individually removed, so scale-down stalls indefinitely (observed `2/1`); only recovery is model destruction or fixing the charm.
- **Fix**: In `disable_certificates_for_unit`/`disable_tls`, check whether the workload is in a restartable state before calling `restart_charm_services`; if mongos isn't yet running, skip the restart.
- **Linter rule**: not mechanically checkable.

### Medium: Published charm uses a different `single_kernel_mongo` version than the repo's declared dependency
- **Severity**: medium
- **Kind**: bug
- **Where**: published rev 165 traceback vs `pyproject.toml` (`mongo-charms-single-kernel = "1.8.52"`)
- **Evidence**: rev 165 has `disable_certificates_for_unit` in `tls.py` (`events/tls.py:143`); repo deps v1.8.52 has no such method — the equivalent is `disable_tls(internal)` at `events/tls.py:161`. Line numbers and call chains also diverge (`restart_charm_services` at line 336 vs 440 in deps).
- **Impact**: The repo's declared dependency doesn't match what's actually shipped in the published charm, so bugs observed against the published charm (e.g. the crash above) can't be reproduced or root-caused from the repo code alone.
- **Fix**: Determine the version actually packed into rev 165, update the lock file to match, or republish pinned to the declared version. Add CI verification comparing the packed charm's single-kernel version to the lock file.
- **Linter rule**: not mechanically checkable.

### Medium: `certificates-relation-broken` hook crash blocks k8s scale-down indefinitely
- **Severity**: medium
- **Kind**: bug
- **Where**: published rev 165 — consequence of the finding above
- **Evidence**: After unit 1's hook crash, `juju scale-application mongos-k8s 1` stalled at `2/1` for 10+ minutes; `juju remove-unit mongos-k8s/1` fails with `k8s models do not support removing named units`. Only recovery was `juju destroy-model`.
- **Impact**: A single hook failure on a non-leader unit blocks all scale operations in production without manual intervention.
- **Fix**: Fix the root-cause crash above; ensure charm hooks never crash on non-ready units.
- **Linter rule**: not mechanically checkable.

### Medium: TLS blocked app-level status never cleared — survives TLS removal, pod restart, update-status cycles
- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/single_kernel_mongo/managers/cluster.py:334-340` and `events/cluster.py` (`_on_relation_broken`), ships as v1.8.52
- **Evidence**: After integrating and removing TLS, the unit fully recovers (mongos restarts without TLS, `active`), but `juju status` app-level stays `blocked: TLS must be disabled in mongos, since it is disabled on the config-server...` indefinitely; survived 30+ minutes of update-status cycles and a pod restart. `tls_statuses()` sets the status at app scope during relation-changed/created but `_on_relation_broken` doesn't recompute or clear it.
- **Impact**: Operator sees a permanently `blocked` app for a healthy system — misleading for the primary health-check surface.
- **Fix**: Clear TLS statuses from app scope in `_on_relation_broken` for the certificates relation, or recompute `tls_statuses()` on every status update rather than caching.
- **Linter rule**: not mechanically checkable.

### Medium: App-level status stale after cluster reintegration — `blocked` while unit is `active` and mongos is running
- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/single_kernel_mongo/managers/cluster.py:334-340` (`update_mongos_and_restart`) and the advanced-statuses status handler
- **Evidence**: After remove/re-add of the cluster relation, app-level `blocked: The cluster relation with the config-server is missing.` while unit `active` and `pebble services` shows `mongos: active`; `status-detail` also shows `mongos: Active`. `update_mongos_and_restart` (line 372-373) only sets app-level `active` when it successfully starts mongos on that hook run — if the handler defers or returns early, the app status never updates.
- **Impact**: Operator sees a contradictory, misleading status after a routine relation cycle.
- **Fix**: On `cluster-relation-created`, clear `MISSING_CONF_SERVER_REL` and push app-level `active` unconditionally, tracking relation presence rather than workload state.
- **Linter rule**: not mechanically checkable.

### Medium: `PrematureDataAccessError` uncaught in `database.py` — hook crashes on late-initialising requirer
- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/single_kernel_mongo/events/database.py:109` (v1.8.52)
- **Evidence**:
  ```python
  except (PyMongoError, FailedToGetHostsError, DatabaseRequestedHasNotRunYetError) as e:
      logger.error("Deferring _on_relation_event since: error=%r", e)
      event.defer()
      return
  ```
  `reconcile_mongo_users_and_dbs` → `update_diff` → `update_relation_data` can raise `PrematureDataAccessError` (from `data_platform_libs`), which isn't in the catch tuple. Observed: `hook failed: "mongos_proxy-relation-changed"` with uncaught `PrematureDataAccessError: Premature access to relation data, update is forbidden before the connection is initialized.`, retrying every ~10 seconds.
- **Impact**: Any requirer that's slow to initialise causes mongos-k8s to crash-loop on `mongos_proxy-relation-changed`, blocking other event processing.
- **Fix**: Add `PrematureDataAccessError` to the catch tuple (or catch a broader data-interfaces exception type) and defer instead of crashing.
- **Linter rule**: not mechanically checkable without call-graph analysis.

### Medium: Action drift between published charm and repo — `set-tls-private-key` orphaned, `resume-refresh` missing
- **Severity**: medium
- **Kind**: ux
- **Where**: `actions.yaml` (repo) vs published 6/edge rev 165 actions
- **Evidence**: rev 165: `force-refresh-start`, `pre-refresh-check`, `set-tls-private-key`, `status-detail`. Repo: `status-detail`, `pre-refresh-check`, `force-refresh-start`, `resume-refresh`. `juju run mongos-k8s/0 resume-refresh` on rev 165 fails (`action not defined`); `set-tls-private-key` on rev 165 fails with `RuntimeError: Relation certificates does not exist`.
- **Impact**: Operators on the published charm can't use `resume-refresh` yet; the orphaned `set-tls-private-key` action errors with a traceback rather than a clean message.
- **Fix**: Publish a release that includes `resume-refresh` and drops `set-tls-private-key`; add a release checklist item verifying `actions.yaml` matches what's published.
- **Linter rule**: not mechanically checkable.

### Medium: 6/edge and 8/edge have diverged status component names, causing stale-status warnings
- **Severity**: medium
- **Kind**: bug
- **Where**: 6/edge vs 8/edge library revisions
- **Evidence**: 6/edge reports `mongos`, `ldap`, `upgrade`; 8/edge reports `mongos`, `tls`, `ldap`, `upgrades`. Deploying 6/edge in a model that previously hosted 8/edge produced `WARNING Tried to delete status ... in scope unit but it was not present`.
- **Impact**: Spurious warnings and potential stale status leakage across channel switches in a shared model.
- **Fix**: Version the status peer data or clear all statuses on install/start rather than warning on not-found deletes.
- **Linter rule**: not mechanically checkable.

### Medium: Duplicate LDAP status components — two `ldap` entries shown simultaneously
- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/single_kernel_mongo/managers/ldap.py`, `events/ldap.py`
- **Evidence**: `status-detail` showed `Blocked | ldap | LDAPS not enabled on LDAP application.` and `Waiting | ldap | Missing LDAP data from Glauth.` simultaneously for the same `ldap` component; the LDAP handler adds statuses without clearing previous ones first.
- **Impact**: Ambiguous `status-detail` output — operators may chase the wrong problem.
- **Fix**: Clear existing `ldap`-scoped statuses before adding new ones, or only surface the highest-priority status.
- **Linter rule**: not mechanically checkable.

### Medium: Integration tests deploy config-server with broken 8/edge and mask the failure
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/helpers.py:189-196` (`deploy_cluster_components`)
- **Evidence**: Always deploys config-server/shard on channel `8/edge` regardless of mongos channel under test; combined with the `processUmask` bug, config-server never starts, but `wait_for_idle(raise_on_error=False)` masks the failure.
- **Impact**: Tests as written cannot reliably pass against current 8/edge images; CI may be relying on cached/older images, masking a real regression.
- **Fix**: Parameterize the channel, or pin to a working config-server image; change `raise_on_error` to `True` so CI catches this.
- **Linter rule**: not mechanically checkable.

### Medium: Unit status stale after cluster relation removal — shows `active` while mongos is stopped
- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/single_kernel_mongo/events/cluster.py:201-206`, `managers/cluster.py:468-485`
- **Evidence**: `_on_relation_broken` → `remove_users_and_cleanup_mongo` correctly calls `stop_charm_services()` (logs `Stopped mongos daemon`) but neither pushes a status update; `juju status` showed `active` for ~2.5 minutes after mongos actually stopped, until the next `update-status`.
- **Impact**: Operator can believe mongos is running when it isn't.
- **Fix**: Push a status update (or explicit blocked/missing-relation status) immediately after stopping the workload, rather than waiting for `update-status`.
- **Linter rule**: not mechanically checkable.

### Medium: TLS mismatch error invisible to operators — only in debug-log
- **Severity**: medium
- **Kind**: ux
- **Where**: `deps/single_kernel_mongo/managers/cluster.py:273-288`, `:392-403`
- **Evidence**: `assert_pass_hook_checks` raises `DeferrableFailedHookChecksError` with a clear message (`"Mongos uses peer TLS but config-server does not..."`), caught by `update_mongos_and_restart_callback` which only logs it and returns `RETRY_RELEASE`. 6/edge's status system has no `tls` component at all; operator sees only `Connecting to config-server...`.
- **Impact**: Debugging TLS misconfiguration requires reading `debug-log`, which is not surfaced through normal `juju status` workflows.
- **Fix**: Surface the TLS mismatch in `status-detail` and the unit message rather than a generic connecting message.
- **Linter rule**: not mechanically checkable.

### Medium: No unit tests — entire test coverage removed
- **Severity**: medium
- **Kind**: test-gap
- **Where**: no `tests/unit/`; commit `b15740a2` ("remove UTs (#103)")
- **Evidence**: No `unit` env in `tox.ini`; CONTRIBUTING.md documents only `lint`, `integration`, `terraform-lint`.
- **Impact**: With all logic in a shared library used by four charms, a library regression (e.g. `processUmask`, `start_charm_services`) hits all of them with no fast pre-merge feedback; only slow full-deployment integration tests exist.
- **Fix**: Restore at least wiring-level unit tests (Scenario) for state transitions, config generation, error paths.
- **Linter rule**: not mechanically checkable.

### Medium: `_post_refresh` calls `start_charm_services` without checking config-server readiness
- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/single_kernel_mongo/managers/mongos_operator.py:200-201`
- **Evidence**: Same pattern as the critical finding — `if self.state.mongos_cluster_relation: ... self.start_charm_services()` with no `config_server_uri` check.
- **Impact**: During `juju refresh`, if the config-server hasn't yet provided its URI (e.g. also refreshing), mongos starts without it and crash-loops.
- **Fix**: Apply the same `config_server_uri` guard here.
- **Linter rule**: same as critical finding.

### Medium: Integration tests assert active/idle but do minimal behavioural verification
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py:33-41`
- **Evidence**: `test_mongos_starts_with_config_server` only checks `check_mongos(... auth=False)`. No tests for TLS, NodePort, config changes, relation removal, LDAP, actions, scaling, or upgrade paths.
- **Impact**: The most complex features have no integration coverage.
- **Fix**: Add integration tests for TLS setup, `expose-external=nodeport`, relation removal, and `status-detail`.
- **Linter rule**: not mechanically checkable.

### Low: TLS relation renamed but old name still used by published charm — README integration commands wrong for 6/edge
- **Severity**: low
- **Kind**: docs
- **Where**: `metadata.yaml` (HEAD) vs published 6/edge rev 165
- **Evidence**: HEAD uses `peer-certificates`/`client-certificates`; rev 165 uses a single `certificates` endpoint. `juju integrate mongos-k8s:peer-certificates ...` fails on rev 165 with `application "mongos-k8s" has no "peer-certificates" relation`.
- **Impact**: Operators following current README instructions against the published 6/edge charm hit this error.
- **Fix**: Document which endpoint name applies to which channel, or backport a compatibility alias.
- **Linter rule**: not mechanically checkable.

### Low: `container.pull()` error handling inconsistent across workload implementations
- **Severity**: low
- **Kind**: bug
- **Where**: `deps/single_kernel_mongo/core/k8s_workload.py:97-101`
- **Evidence**:
  ```python
  def read(self, path: Path) -> list[str]:
      if not self.container.exists(path):
          return []
      with self.container.pull(path) as f:
          return f.read().split("\n")
  ```
  Unlike `restart()` (line 64-75), which catches `ChangeError`/`TimeoutError`/`ConnectionError` and wraps them, `read()` doesn't catch `ops.pebble.ProtocolError`/`PathError`/`ConnectionError`.
- **Impact**: A temporarily unresponsive Pebble could cause a raw traceback instead of a graceful defer during config changes.
- **Fix**: Wrap `container.pull()` and raise a domain exception.
- **Linter rule**: "ops `container.pull()` not wrapped in error handler" — mechanically checkable.

### Low: `kubectl exec` implies container user is root, but mongod runs as `mongodb` user
- **Severity**: low
- **Kind**: ux
- **Where**: container image Pebble layer (`/bin/start.sh` in the rock)
- **Evidence**: mongod runs via `setpriv --clear-groups --reuid mongodb --regid mongodb -- /usr/bin/mongod`, but the container's default exec user is root.
- **Impact**: Operators using `kubectl exec`/`juju ssh` get a root shell while the workload runs as `mongodb`, a common source of permission-debugging confusion. Not a charm-code fix.
- **Fix**: Not fixable in charm code — rock image build concern.
- **Linter rule**: not mechanically checkable.

### Low: App-level status inconsistent with unit status — app shows `active` while unit is `blocked`
- **Severity**: low
- **Kind**: ux
- **Where**: `deps/single_kernel_mongo/abstract_charm.py` and `data_platform_helpers.advanced_statuses.handler`
- **Evidence**: mongos-k8s deployed alone (8/edge, no cluster relation): unit `blocked: The cluster relation with the config-server is missing.`, app `active` with no message, until a config change triggered a hook that pushed app-level status.
- **Impact**: Confusing app/unit status combination undermines trust in `juju status`.
- **Fix**: Push app-level status as soon as the unit detects a blocking condition, not on the next update-status cycle.
- **Linter rule**: not mechanically checkable.

### Low: Non-standard port 27018 used for mongos — deliberate but undocumented for operators
- **Severity**: low
- **Kind**: ux
- **Where**: `MongosConfigManager.set_environment()` / `workload/mongos_workload.py`; `tests/integration/helpers.py:27`
- **Evidence**: config consistently uses `net.port: 27018`; test helpers hardcode `MONGOS_PORT = 27018`, confirming deliberate choice.
- **Impact**: Operators expecting the standard 27017 mongos port may be confused. Low severity since deliberate.
- **Fix**: Document the port choice in the README.
- **Linter rule**: not mechanically checkable.

### Low: Duplicate status entries — "Connecting to config-server" and "Waiting for mongos to start" both shown
- **Severity**: low
- **Kind**: ux
- **Where**: `deps/single_kernel_mongo/managers/mongos_operator.py:755-763` (`get_statuses()`)
- **Evidence**: `status-detail` showed both `"Connecting to config-server..."` and `"Waiting for mongos to start..."` for the same underlying cause (missing config-server URI).
- **Impact**: Redundant entries dilute the signal and can make operators think two problems exist.
- **Fix**: Short-circuit in `get_statuses()` so only one is returned, or merge them.
- **Linter rule**: not mechanically checkable.

### Low: Integration tests cannot install dependencies — `python-ldap` build fails without LDAP headers
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py`, `pyproject.toml` integration deps
- **Evidence**: `tox -e integration` fails at `poetry install --only integration`: `fatal error: lber.h: No such file or directory`. `python-ldap` needs `libldap2-dev`/`libsasl2-dev`, undeclared and undocumented.
- **Impact**: New contributors can't run integration tests without manual system setup.
- **Fix**: Add the headers to the test environment or document them in CONTRIBUTING.md.
- **Linter rule**: not mechanically checkable.

### Nit: ruff I001 — import order in `src/charm.py`
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:6`
- **Evidence**: `ruff check src/` reports `I001 Import block is un-sorted or un-formatted`.
- **Impact**: Trivial formatting issue, no behavioural effect.
- **Fix**: `ruff check --fix src/`.
- **Linter rule**: already detected by ruff I001.

## Worth copying

- **Structured config via Pydantic** (`deps/single_kernel_mongo/core/structured_config.py`): config values like `expose-external` validated through Pydantic `field_validator`s that convert invalid strings to sentinel enum values, letting the operator report a clear status without tracebacks.
- **Separation of event handlers from managers** (`events/lifecycle.py`, `managers/`): handlers observe Juju events and delegate to managers; exceptions are classified deferrable/non-deferrable, keeping `defer()` policy auditable and out of business logic.
- **Exception taxonomy** (`exceptions.py`): rich hierarchy (`DeferrableError`, `NonDeferrableFailedHookChecksError`, `DeferrableFailedHookChecksError`, etc.) that communicates both the error and the intended handler response.
- **Secret caching** (`core/secrets.py`): `SecretCache`/`CachedSecret` avoid repeated Juju secret API calls per event and work around the `refresh=True` bug for secret owners.
- **K8s service management with lightkube** (`managers/k8s.py`): clean Service/StatefulSet abstraction with `@cache` + TTL invalidation; NodePort services carry `OwnerReference` to pods for cleanup on scale-down.
- **Advanced statuses**: multi-component status system (`mongos`, `tls`, `ldap`, `upgrades`) exposed via the `status-detail` action as a structured table — good idea even though the implementation has the bugs noted above.

## Common-practice notes

- **Single-kernel pattern**: four charms sharing one PyPI package; charm itself is a 35-line class. Consistent with the ecosystem (postgresql-k8s, mysql-k8s use similar patterns).
- **No unit tests**: drifts from the canonical charm template (`tests/unit/`), removed deliberately in `b15740a2`.
- **Poetry + charmcraft 3**: modern `charmcraft.yaml`, poetry plugin, explicit platform declarations — current best practice.
- **Terraform module**: ships under `terraform/` with typed variables/outputs; minimal (deploy + offer) but functional.
- **Spread for CI**: `spread.yaml` targeting LXD VM and GitHub CI with microk8s, Juju 3.6/stable — standard data-platform team setup.
- **Pebble layer pattern**: `workload/mongos_workload.py` generates Pebble layers at runtime rather than baking them into the image — common and sensible for k8s charms.
- **Container image resource**: pinned SHA digest in `metadata.yaml`, with a TODO to update on rock changes — deliberate reproducibility tradeoff meaning image CVEs require a charm release.

## Tests

- **Unit tests**: none. No `testenv:unit` in `tox.ini`; removed in `b15740a2`.
- **Integration tests**: `tests/integration/test_charm.py`, three tests — deploy cluster, verify mongos blocks without config-server, verify mongos starts after integration, using pymongo connectivity checks. Critical gap: `deploy_cluster_components` always deploys config-server/shard on `8/edge`, currently broken, and uses `raise_on_error=False` throughout, masking failures. No tests for TLS, NodePort, config changes, refresh/upgrade, or LDAP. Cannot even install: `tox -e integration` fails on `python-ldap` build (missing `libldap2-dev`).
- **Spread tests**: `tests/spread/test_charm.py/task.yaml` runs the integration suite via LXD VM or GitHub CI/microk8s, targeting `ubuntu-22.04`/`ubuntu-22.04-arm`.
- **Terraform tests**: `terraform/tests/` — smoke test deploying mongos + data-integrator via Terraform, no behavioural assertions.
- **Lint**: `tox -e lint` passes clean. `tox -e terraform-lint` fails locally (terraform not installed — not a code defect). `charmcraft analyse` crashes with `IsADirectoryError`.
- **Coverage gaps relative to findings**: the `start_charm_services`/`restart_charm_services` asymmetry (critical), TLS/NodePort/config-change/refresh/relation-break/LDAP paths, the status-staleness bugs, and the `certificates-relation-broken` crash all have zero test coverage — current tests only assert `wait_for_idle(status="active")`.

## Docs

- **README**: explains what mongos is, how to deploy a sharded cluster, integrate, enable TLS, configure external access, remove mongos. Broadly matches observed behaviour.
- **CONTRIBUTING.md**: clear on the single-kernel patch/bump/PR workflow; no mention of unit tests (consistent with their removal).
- **Charmhub docs**: linked to the discourse page; published on 6/stable (rev 75) and 8/stable. Charm is not listed/searchable on charmhub.io (open issue #225) (unverified — not independently confirmed during this review).
- **Terraform README**: complete, documents inputs/outputs/requirements.
- **Doc/reality mismatch**: README says "When the status of `mongos-k8s` becomes `idle`, integrate with `data-integrator`" — but observed status without integrations is `blocked`, not `idle`. Wording could mislead operators into expecting an active/idle state before integrations exist.

## Open questions

1. Does the `processUmask` string bug also affect MongoDB 6.x images? — No, confirmed 6.0.28 parses `'037'` correctly as decimal 31; only 8.0.10 corrupts it.
2. Why were unit tests removed? Commit `b15740a2` ("remove UTs (#103)") gives no explanation.
3. Does the `start_charm_services` bug reproduce on VM substrates (mongos-vm)? Not tested; the shared code path (`mongos_operator.py:288-289`) makes it likely.
4. Is the missing URI guard present in current HEAD, or only in the published rev? Deps code at HEAD (v1.8.52) shows the same missing guard as reviewed; a fix requires a new single-kernel release.
5. Is the stale-status-after-relation-removal bug unique to 6/edge? Confirmed on 6/edge rev 165; not independently tested on 8/edge (never fully working there), but the code path is shared so it likely affects 8/edge too.
6. Do the integration tests actually pass in CI? Unknown, not run in CI during this review; given the 8/edge dependency and masking via `raise_on_error=False`, they should be failing or false-negative.
7. Which version of `single_kernel_mongo` actually ships in 6/edge rev 165? Confirmed different from the repo's declared v1.8.52 (has `disable_certificates_for_unit`, absent from deps) — exact version and how it diverged not determined.
8. Does the `certificates-relation-broken` crash reproduce with current repo code? Unknown — repo's `tls.py` uses `disable_tls(internal)`/`async_restart_charm_services` rather than the published charm's `disable_certificates_for_unit`/`restart_charm_services(force=True)`; would need to pack and deploy HEAD to confirm whether the async path avoids the crash.
9. Why does `charmcraft analyse` crash with `IsADirectoryError`? Appears to be a charmcraft-side issue, worth reporting upstream.
