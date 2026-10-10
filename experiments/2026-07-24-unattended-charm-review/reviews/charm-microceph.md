# microceph

A mature, well-structured machine charm (ops-sunbeam based) that deploys and manages a MicroCeph
(Ceph via snap) cluster: bootstrap/join, OSD enrollment (config DSL + actions), RGW/NFS/MDS services,
COS telemetry, remote-cluster federation, and snap upgrades. The codebase is large (~16 source files,
~1.2k LOC in `charm.py`) but coherent, and the compound-status design is a good example of layering
independent concerns. It was deployed and exercised on a two-node LXD cluster (squid/edge, rev 331)
and works for the core lifecycle: bootstrap, config changes, RGW enable/disable, and the
`receive-ca-cert` integration with `self-signed-certificates` all behaved correctly.

The charm's weak point is failure handling at the edges. Scale-down is broken: `remove-unit` reliably
drives the departing unit into a stop-hook retry loop (issue #177, confirmed live with a traceback),
because a non-benign `cluster remove` error is followed by an unguarded `is_cluster_member` call that
raises and isn't caught. There's also a `return` hidden inside a `finally` block that silently swallows
`ModelError` during bootstrap parameter resolution, an unguarded HTTP call in the snap-upgrade path that
will hang indefinitely in an airgapped environment, and a `TypeError` in `ceph_rgw.py` when
`default-pool-size` is unset. None of these are exotic scenarios — they're all in scale-down, upgrade,
and default-config paths a maintainer should expect operators to hit.

**First priority for a maintainer**: fix the `_remove_self`/`is_cluster_member` exception handling
(critical, breaks scale-down) and the `finally: return` in `_get_bootstrap_params` (masks bootstrap
failures silently). Both are small, well-understood fixes. After that, add a timeout to the snap-store
HTTP call and guard `default-pool-size` against `None`.

| | |
|---|---|
| Repo | canonical/charm-microceph @ `6ac6e6d` (2026-07-23) |
| Charms | microceph |
| Substrate | machine |
| Deployed | yes — `concierge-lxd-4`, squid/edge rev 331 (deployment log below) |
| Reviewed | 2026-08-27 |

## What it does

MicroCeph installs the `microceph` snap, bootstraps a single-node cluster, and scales out. It publishes
Ceph client credentials, RGW/NFS/MDS services, and integrates with COS (Grafana Agent), Traefik,
Keystone, and remote microceph clusters.

- Declarative OSD enrollment via `osd-devices` config DSL
- WAL/DB carrier device support
- Snap upgrade with health gating
- Maintenance mode (enter/exit actions)
- Remote cluster federation
- AZ support

## Deployment log

### First deployment (`rv-microceph-lxd4`, destroyed)
Controller: `concierge-lxd-4` (Juju 4.0.12). Bootstrap time: ~6 min from deploy to active/idle.
Hook sequence: `install` → `peers-relation-created` → `leader-elected` → `config-changed` → `start` →
`peers-relation-changed` (×2). Cluster: mon/mgr/mds, 0 OSDs, `HEALTH_WARN`.

### Second deployment (`rv-microceph2`, current)
Controller: `concierge-lxd-4` (Juju 4.0.12), model `rv-microceph2`.

```
juju add-model rv-microceph2 --controller concierge-lxd-4
juju deploy microceph --channel squid/edge -n 1
juju add-unit microceph -n 1   # scale to 2 units
juju deploy self-signed-certificates --channel stable
juju relate microceph:receive-ca-cert self-signed-certificates
juju remove-relation microceph self-signed-certificates
```

Installed snap: squid/stable 19.2.3, rev 331.

**Two-unit lifecycle:**
- microceph/0 bootstrap: ~6 min to active/idle (machine 0: `juju-951c24-0`, 10.5.87.9)
- microceph/1 bootstrap: ~7 min from `add-unit` to active/idle (machine 2: `juju-951c24-2`, 10.5.87.233)
- Hooks on microceph/1: `install` → `peers-relation-created` → `leader-elected` → `config-changed` →
  `start` → `peers-relation-changed` (multiple times)
- Peer relation churn: the peers relation fires many `relation-changed` events during bootstrap. The log
  line `Skipping notice (.../CephNfsProvides[ceph-nfs]/_on_ceph_peers) - already in the queue` appears
  frequently, confirming the reconciliation is triggered repeatedly but correctly deduplicates via the
  event queue.

**`receive-ca-cert` integration with `self-signed-certificates`:**
- `juju relate microceph:receive-ca-cert self-signed-certificates` — relation established (05:14:24 UTC)
- microceph/0 deferred the relation-changed event 4 times (`"Storage not available, deferring event."`)
  but stayed `active/idle` throughout
- CA cert eventually processed; `update-ca-certificates` logged a harmless rehash warning
- microceph detected RGW not enabled, stayed `active/idle` throughout
- `juju remove-relation microceph self-signed-certificates` removed cleanly (`relation-departed` →
  `relation-broken` on all units)
- Library version mismatch: microceph ships `certificate_transfer_interface/v0` (LIBPATCH 6) with no
  `version` field, which triggers a deprecation warning on the provider side

**`namespace-projects` toggle after deployment:**
- `juju config microceph namespace-projects=true` → both units blocked with `"Config
  namespace-projects cannot be changed after deployment, revert to False"` — correctly guarded
- Reverted cleanly

**`default-pool-size` failure injection:**
- `default-pool-size=0` → accepted without blocking (`microceph pool set-rf --size 0 ''` fails but the
  error is caught and handled without visible status change, since there are no RGW pools to set)
- `default-pool-size=-1` → both units blocked with `"Error: Command ['sudo', 'microceph', 'pool',
  'set-rf', '--size', '-1', ''] returned non-zero"` — recoverable on revert

**`ceph-cluster-network` config:**
- `ceph-cluster-network="10.0.0.0/24"` → accepted, applied without blocking
- `ceph-cluster-network="not-a-cidr"` → both units blocked with `"Invalid config
  ceph-cluster-network: 'not-a-cidr' has no prefix length"` — recoverable on revert to `""`

**Other config:** `enable-perf-metrics=true` accepted without blocking. `site-name="test-site"`
accepted without blocking. `rbd-stats-pools="invalid@pool!"` accepted (no charm-level validation; Ceph
mgr validates).

**Scale-down (`remove-unit microceph/1`):**
- Unit entered `maintenance` (stopping charm software), then `error` with `"hook failed: 'stop'"`
- Debug log: `microceph cluster remove juju-951c24-2 --force` timed out with `"Delete
  ... context deadline exceeded"`
- Then `is_cluster_member` raised `500 Server Error: Internal Server Error` — NOT caught, propagated
  through `_remove_self` → `_on_stop`, causing the hook to fail
- Unit stuck in stop hook retry loop: cycles `maintenance` → `error` → `maintenance` → `error`
- Juju removal worker still scheduled machine removal (`INFO juju.worker.removal scheduling unit job`)

## Observed behaviour

- Install hook: `snap install microceph --channel tentacle/stable` with 900s timeout succeeded. Snap
  alias `ceph → microceph.ceph` created. Snap held.
- `ceph-public-network="not-a-cidr"` → blocked with clear message. Recovered on revert.
- `ceph-cluster-network="not-a-cidr"` → blocked with clear message. Recovered on revert.
- `ceph-cluster-network="10.0.0.0/24"` → accepted, applied.
- `snap-channel="invalid-channel-xyz"` → blocked with clear message. Recovered on revert.
- `snap-channel=""` → blocked with confusing `"Cannot upgrade from X to "` (empty target). Recovered on
  revert.
- `osd-devices='{"osd-per-device": 1}'` → blocked with DSL parse error. Recovered on revert.
- `namespace-projects=true` after deployment → blocked with `"cannot be changed after deployment"`.
  Recovered on revert.
- `default-pool-size=-1` → blocked. Recovered on revert.
- Unit is `active/idle` even with `HEALTH_WARN` (0 OSDs, `POOL_NO_REDUNDANCY`): `ready_for_service()`
  only checks `microceph.is_ready()` (daemon alive) and leadership, not `ceph health`. This appears to
  be deliberate design.
- Upgrade health gate fires on `POOL_NO_REDUNDANCY`: `health != CephHealth.Ok` blocks any `HEALTH_WARN`,
  including benign pool-redundancy warnings.
- File-based OSD creates non-functional PGs: `add-osd loop-spec='4G,1'` created OSD.1 but 32 PGs stuck
  in `creating+peering`.
- COS subordinate (`grafana-agent`) does not affect principal status: microceph stayed `active/idle`
  when grafana-agent blocked waiting for a data sink.
- `remove-unit` → stop hook fails, unit stuck in retry loop (issue #177 confirmed).
- Two-unit deployment: both microceph units reached `active/idle`. Peer relation reconciliation fires
  many `relation-changed` events but correctly deduplicates.
- `juju debug-log` hook counts: only 1 `config-changed` per config change — the guard pattern in
  `configure_charm` prevents spurious re-renders.
- Lint: 483 ruff issues across `src/` and `lib/charms/`, dominated by typing deprecations
  (UP006/UP035: 99+), f-string modernisations (UP032: 97+), bare except (BLE001: 12), `raise e`
  (TRY201: 12), root logger (LOG015: 21), unnecessary pass (PIE790: 23).

## Findings

### Stop hook fails on `remove-unit` — unit stuck in retry loop (issue #177 confirmed)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:175` (`_remove_self`)
- **Evidence**: `remove-unit microceph/1` caused the departing unit's stop hook to fail. Debug log
  traceback:
  ```
  File ".../src/charm.py", line 175, in _remove_self
      if microceph.is_cluster_member(hostname):
  File ".../src/microceph.py", line 189, in is_cluster_member
      raise e
  File ".../src/microceph.py", line 181, in is_cluster_member
      return hostname in str(output)
  File ".../src/microceph.py", line 149, in cluster_members
      members = client.cluster.list_members()
  unit-microceph-1: ERROR juju.worker.uniter.operation hook "stop" (via hook dispatching script: dispatch) failed: exit status 1
  ```
  Root cause is two-part: (1) `microceph cluster remove --force` times out with `"context deadline
  exceeded"`, which is not in `_is_benign_cluster_remove_error` (`src/charm.py:128`), so the error is
  not swallowed; (2) the subsequent `is_cluster_member(hostname)` call then fails with `"500 Server
  Error: Internal Server Error"`, which propagates up through `_remove_self` and `_on_stop` and fails
  the hook. The unit is then stuck cycling `maintenance` → `error` → `maintenance` → `error`
  indefinitely, while Juju's removal worker still schedules the machine removal asynchronously.
- **Impact**: partial scale-down leaves a unit permanently in error state, requiring manual `juju
  resolve` or controller intervention. In production this creates orphaned units.
- **Fix**: catch the exception from `is_cluster_member` in `_remove_self`:
  ```python
  try:
      is_still_member = microceph.is_cluster_member(hostname)
  except (CalledProcessError, TimeoutExpired):
      logger.info("Could not verify cluster membership after remove attempt; assuming removed")
      return
  if is_still_member:
      raise e
  ```
  Also add `"context deadline exceeded"` and `"500 Server Error"` to `_is_benign_cluster_remove_error`.
- **Linter rule**: not mechanically checkable.

### `_get_bootstrap_params`: `return` inside `finally` swallows `ModelError`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:744` (notes place the try/except at `charm.py:792`; kept as reported, treat
  line number as approximate)
- **Evidence**:
  ```python
  def _get_bootstrap_params(self) -> dict:
      ...
      try:
          public_net = public_net_cfg or self._get_space_subnet(space="public") or ""
          cluster_net = cluster_net_cfg or self._get_space_subnet(space="cluster") or ""
          micro_ip = self.model.get_binding(binding_key="admin").network.bind_address
      except ops.model.ModelError as e:
          logger.exception(e)       # logs but does NOT re-raise
      finally:
          return {                   # always returns, even after the except
              "public_net": format(public_net),
              ...
          }
  ```
- **Impact**: if `_get_space_subnet("public")` raises `ModelError`, the except block logs and the
  finally block returns empty strings regardless. Callers `bootstrap_cluster()` and `adopt_cluster()`
  then call `microceph join_cluster` with empty network params. The notes indicate the join CLI falls
  back to defaults on empty strings, so this is a latent issue (silent masking) rather than an
  immediate crash, but a real network-resolution failure is hidden either way.
- **Fix**: re-raise in the except block, or move the return after the try/except:
  ```python
  except ops.model.ModelError as e:
      logger.exception(e)
      raise
  return { ... }
  ```
- **Linter rule**: not mechanically checkable without dataflow analysis.

### `can_upgrade_snap`: HTTP request without timeout
- **Severity**: high
- **Kind**: bug
- **Where**: `src/microceph.py:599` (`get_snap_info`)
- **Evidence**:
  ```python
  def get_snap_info(snap_name):
      url = f"https://api.snapcraft.io/v2/snaps/info/{snap_name}"
      headers = {"Snap-Device-Series": "16"}
      response = requests.get(url, headers=headers)   # no timeout
      response.raise_for_status()
      return response.json()
  ```
- **Impact**: in an airgapped environment this hangs indefinitely during `config-changed` on snap
  upgrade. Matches upstream issue #326: "Unhandled ConnectionError in `can_upgrade_snap` blocks leader
  unit during config-changed hook in airgapped environment."
- **Fix**: add `timeout=10` to `requests.get` and catch `requests.exceptions.RequestException` in
  `can_upgrade_snap` to return `False` gracefully.
- **Linter rule**: not mechanically checkable with a static ruff rule for this specific call, but a
  general "requests without timeout" rule would flag it.

### `ceph_rgw.py`: `TypeError` when `default-pool-size` config is `None`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/ceph_rgw.py:57`
- **Evidence**:
  ```python
  if osd_count < self.charm.config.get("default-pool-size"):   # None comparison
      return False
  ```
  `config.get("default-pool-size")` returns `None` when the option is not explicitly set;
  `osd_count < None` raises `TypeError: '<' not supported between instances of 'int' and 'NoneType'`.
  Confirmed directly (`1 < None` raises `TypeError`). Affects `rgw_ready`, called from the
  `ceph-rgw-ready` relation handler and `update_status`.
- **Impact**: on a cluster where `default-pool-size` was never explicitly set, evaluating `rgw_ready`
  raises an uncaught `TypeError` and crashes the hook. `config.yaml` defines a default of 3, but ops
  may still surface `None` for the option depending on when it's evaluated.
- **Fix**: `self.charm.config.get("default-pool-size", 3)`.
- **Linter rule**: not mechanically checkable without knowing the config option can be `None`.

### Upgrade health gate fires on `POOL_NO_REDUNDANCY` — overly strict
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/cluster.py:149` (`ClusterUpgrades._can_upgrade`)
- **Evidence**: `health != CephHealth.Ok` blocks any `HEALTH_WARN`. After `add-osd loop-spec='4G,1'`
  and `enable-rgw='*'`, setting `snap-channel="squid/edge"` blocked with `"Cannot upgrade, ceph health
  not ok: HEALTH_WARN, {'POOL_NO_REDUNDANCY': ...}"`.
- **Impact**: a cluster with `default-pool-size=1` can never upgrade the snap, because `ceph health`
  always reports `POOL_NO_REDUNDANCY` on a single-replica pool.
- **Fix**: filter `POOL_NO_REDUNDANCY` and `TOO_FEW_OSDS` out of the blocking checks for same-track
  upgrades.
- **Linter rule**: not mechanically checkable.

### `snap-channel=""` produces a confusing error message
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:654` (`can_upgrade_charm_payload`)
- **Evidence**: setting `snap-channel=""` triggers `"Cannot upgrade from squid/stable to "` — nothing
  after "to".
- **Fix**: in `can_upgrade_snap`, replace `if not new: return False` with a clear blocked error, e.g.
  `raise BlockedExceptionError("snap-channel cannot be empty")`.
- **Linter rule**: not mechanically checkable.

### Bare `except Exception` in 12 locations silences failures
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:161` (`_on_stop` cluster_member_count), `src/ceph.py:1246` (`osd_count`
  returns 0), `src/ceph_broker.py:225,838,857,871`, `src/ceph_nfs.py:244,309`,
  `src/maintenance.py:82,124`, `src/relation_handlers.py:681`, `src/utils.py:95`
- **Evidence**:
  ```python
  # src/ceph.py:1246
  except Exception as e:
      log("Failed getting the number of OSDs: {}".format(str(e)), WARNING)
      return 0   # silently returns 0, masking real OSD-detection failures
  ```
  Some of these are intentional (`ceph_broker.py process_requests` deliberately returns
  `{"exit-code": 1}` rather than raising, which is the correct broker contract; the maintenance-action
  handlers also catch a specific exception type alongside the bare except).
- **Fix**: narrow to specific exceptions (e.g. `CalledProcessError`) where the catch isn't intentionally
  broad; for `_on_stop`, catch `CalledProcessError | TimeoutExpired`.
- **Linter rule**: BLE001 — mechanically checkable with ruff.

### `mutable-default-argument` in `adopt_ceph_cluster`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/microceph.py:320`
- **Evidence**: `mon_hosts: list = []` — mutable default, flagged by ruff B006.
- **Fix**: `mon_hosts: list | None = None`, then `if mon_hosts is None: mon_hosts = []`.
- **Linter rule**: B006 — mechanically checkable with ruff.

### `list-disks` action returns nested objects as strings
- **Severity**: medium
- **Kind**: docs
- **Where**: `src/storage.py:232` (`_list_disks_action`)
- **Evidence**: confirmed from actual action output: `"osds": '[{'osd': 1, ...}]'` (a stringified list)
  instead of structured JSON. Matches upstream issue #185.
- **Fix**: `event.set_results({"osds": json.dumps(osds), ...})`.
- **Linter rule**: not mechanically checkable.

### Terraform module README documents wrong `juju` provider version
- **Severity**: medium
- **Kind**: docs
- **Where**: `terraform/microceph/README.md`, `terraform/microceph/version_constraints.tf`
- **Evidence**: README says `~> 1.0.0`; `version_constraints.tf` was updated to `~> 2.0` (per PR #339).
  README is stale.
- **Fix**: update README to document `juju ~> 2.0`.
- **Linter rule**: not mechanically checkable.

### Getting-started tutorial is severely outdated
- **Severity**: medium
- **Kind**: docs
- **Where**: `docs/tutorials/getting-started.rst`
- **Evidence**: tutorial references `tentacle/stable rev 155` throughout; deployed charm observed is
  `squid/stable rev 325`. The install guide separately shows `latest/edge rev 3`.
- **Impact**: new operators following the tutorial get a very different (and old) charm version.
- **Fix**: update tutorial and install guide to current channel/revision references.
- **Linter rule**: not mechanically checkable.

### Root logger calls in shipped libraries
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/keystone_k8s/v1/identity_service.py` (8), `lib/charms/sunbeam_libs/v0/service_readiness.py`
  (5), `lib/charms/ceph_nfs_client/v0/ceph_nfs_client.py` (2), `src/charm.py:239`, `src/cluster.py:49,57,59`
- **Evidence**: `logging.debug(...)` used instead of a module-level `logger.debug(...)`, bypassing the
  charm's logging configuration.
- **Fix**: use `logger = logging.getLogger(__name__)` consistently.
- **Linter rule**: LOG015 — mechanically checkable with ruff.

### `raise e` without exception chaining in 12 locations
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:178,851,1130,1156`, `src/cluster.py:72,103`, `src/microceph.py:190,661`,
  `src/microceph_client.py:125`, `src/storage.py:699`, `src/utils.py:47,65`
- **Fix**: replace `raise e` with bare `raise`.
- **Linter rule**: TRY201 — mechanically checkable with ruff.

### `subprocess.run` without explicit `check=` in `snap_has_connection`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/utils.py:76`
- **Evidence**: `subprocess.run(cmd, capture_output=True, text=True)` with no `check=`. If `snap` is
  unavailable, a `FileNotFoundError` propagates uncaught.
- **Fix**: `subprocess.run(cmd, capture_output=True, text=True, check=False)`.
- **Linter rule**: PLW1510 — mechanically checkable with ruff.

### Pydantic deprecation in shipped grafana-agent library
- **Severity**: low
- **Kind**: ux
- **Where**: `lib/charms/grafana_agent/v0/cos_agent.py:689`
- **Evidence**: Pydantic deprecation warnings observed in unit test output (draft cites 96 occurrences
  across the suite; notes observed 4 from this specific call site — kept as `(unverified)` count):
  ```
  PydanticDeprecatedSince20: The `json` method is deprecated; use `model_dump_json` instead.
  ```
- **Impact**: warning noise on every test run; will break on a future Pydantic v3 upgrade.
- **Fix**: update the shipped `cos_agent.py` to use `model_dump_json()`.
- **Linter rule**: not mechanically checkable from within the charm.

### Default `snap-channel` discrepancy: local `config.yaml` vs published charm
- **Severity**: low
- **Kind**: docs
- **Where**: `config.yaml` vs deployed charm (rev 331)
- **Evidence**: local `config.yaml` specifies `default: "tentacle/stable"`; the deployed charm reports
  `"squid/stable"`. The README examples show `tentacle/stable`.
- **Fix**: align `config.yaml` default with the published channel track.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **`storage.py` cacheable config pattern**: `_is_cached_osd_config()` / `_storage_config_signature()`
  / `_set_osd_config_cache()` is a well-designed cache key for declarative config; correctly treats
  WAL/DB-only changes as non-actionable while tracking OSD-affecting changes.
- **`utils.py` `is_departing()`**: `app.planned_units() == 0` is a clean, fail-safe way to detect
  whole-application teardown.
- **`utils.py` `get_mon_addresses()` cross-check**: `get_live_mon_ips()` against `ceph mon dump` filters
  dead mons from the microceph API response, with graceful fallback. `_sort_mon_addresses()` uses
  normalised IP sorting to prevent spurious relation-changed events.
- **`microceph_client.py` graceful error handling**: `BaseService._request()` translates HTTP errors
  into typed exceptions (`ClusterServiceUnavailableException`, `CephServiceNotFoundException`,
  `MaintenanceOperationFailedException`).
- **`device_flags.py`**: clean DSL parser, raises `ValueError` on unknown flags, dataclass for parsed
  results, no mutable state or external dependencies.
- **`ceph_nfs.py` graceful fallback**: `_get_nfs_bind_address()` tries `nfs-address` from peer data
  first, then `public-address`; handles both `nfs-use-dedicated-binding` and older charm revisions.
- **`CephCOSAgentProvider._custom_scrape_configs()`** (`lib/charms/ceph_mon/v0/ceph_cos_agent.py:104`):
  returns `[]` when the mgr is unavailable, avoiding bogus `localhost:9283` scrape targets.
- **`cluster.py` graceful upgrade with `poll_ok()`**: `tenacity`-based health polling requiring 3
  consecutive OK checks prevents flapping upgrades on transient degraded health.
- **`microceph_remote.py` idempotent reconciliation**: `import_remote_cluster` treats "already exists"
  `CalledProcessError` as a no-op, keeping relation reconciliation convergent.
- **`_is_benign_cluster_remove_error`** (`src/charm.py:128`): a good pattern for classifying stderr
  strings as benign vs fatal. Currently covers "Cannot leave a cluster with 1 members", "not found in
  dqlite or database", and "cluster member" + "not found" — the observed scale-down failure shows this
  list needs extending (see findings above).
- **`ceph_broker.py process_requests`**: wraps all exceptions into `{"exit-code": 1, "stderr": msg}`
  rather than raising — the correct broker pattern; the client charm is expected to check exit code.
- **ops-sunbeam compound status**: `StatusPool` / `Status` allows independent concerns (bootstrap,
  storage, upgrade, workload) to set status with priorities.

## Common-practice notes

- **ops-sunbeam usage**: built on `OSBaseOperatorCharm`, `sunbeam_guard.guard`, `sunbeam_rhandlers`,
  `compound_status` — heavier than plain `ops` but appropriate for a multi-service charm of this size.
- **Relation library layout**: ships `ceph_mon/v0/ceph_cos_agent`, `operator_libs_linux/v2/snap`,
  `sunbeam_libs/v0/service_readiness`, `grafana_agent/v0/cos_agent`, `keystone_k8s/v1/identity_service`,
  `traefik_k8s/v0/traefik_route`, `ceph_nfs_client/v0/ceph_nfs_client`,
  `certificate_transfer_interface/v0/certificate_transfer`. `ceph_cos_agent.py` is at LIBPATCH 6; the
  shipped `cos_agent.py` carries Pydantic v2 deprecation warnings.
- **Subordinate integration**: `cos-agent` (grafana-agent) does not affect principal status; microceph
  stays `active/idle` even when the subordinate is blocked. `receive-ca-cert` similarly keeps microceph
  `active/idle` throughout — the sunbeam guard sets `WaitingStatus` only transiently.
- **Upgrade handling**: no `juju refresh` for in-place upgrades; instead `snap-channel` config change
  triggers `ClusterUpgrades` via `config-changed`. The gate uses `ceph health detail` and blocks on any
  non-OK health, including benign warnings.
- **Subprocess call pattern**: `utils.run_cmd()` is the standard wrapper, raising `CalledProcessError`
  on non-zero exit; some callers use `check=True`, others handle failure explicitly.
- **Status precedence**: a cluster with 0 OSDs reports `active/idle` because `ready_for_service()` only
  checks `microceph.is_ready()` and leadership, not `ceph health`. `HEALTH_WARN` alone never triggers
  `blocked`.

## Tests

**Unit tests**: 270 passed, 0 errors in ~10.5s via `tox -e py3`. A one-off "267 passed, 1 error" from
running pytest directly was a conftest conflict; `tox` isolates from the global conftest cache.

Coverage gaps relative to findings:
- `_on_stop` with `remove_cluster_member` timeout → `is_cluster_member` raising: not tested (existing
  tests cover benign errors and both `is_cluster_member` return values, but not it raising)
- `_get_bootstrap_params` `ModelError` swallowing: not tested
- `can_upgrade_snap` HTTP timeout in airgapped environments: not tested
- `rgw_ready` with `default-pool-size=None`: not tested
- `adopt_ceph_cluster` mutable-default `mon_hosts` across multiple calls: not tested
- `ceph-cluster-network` invalid CIDR: not tested
- `namespace-projects` post-deployment toggle guard: not tested
- `default-pool-size=-1` blocking: not tested

**Integration tests** (`tests/integration/`): `test_charm.py`, `test_mon_addresses.py`,
`test_network_config.py`, `test_nfs_binding.py`, `test_osd_devices_config.py`,
`test_storage_waldb_config.py`, `test_terraform.py`, `test_upgrade_health_recovery.py`. Not runnable in
this environment (require a real LXD model with storage).

**Functional tests** (`tests/functests/`): `test_encrypt_osd.py`, `test_wipe_osd.py` — LXD functional
tests for storage flags.

**Sunbeam tests** (`tests/sunbeam/`): end-to-end upgrade test requiring an attached OpenStack model.
Not runnable in this environment.

**Linting** (ruff, 483 issues):

| Category | Count | Auto-fixable |
|---|---|---|
| UP006/UP035 (typing) | 99+ | yes |
| UP032 (f-string) | 97+ | yes |
| BLE001 (bare except) | 12 | no |
| TRY201 (raise e) | 12 | no |
| LOG015 (root logger) | 21 | no |
| PIE790 (unnecessary pass) | 23 | yes |
| EXE001 (shebang) | 13 | no |
| PLW1510 (subprocess no check) | 1 | yes |
| B006 (mutable default) | 2 | no |

`codespell`: 1 error — "installled → installed" in `lib/charms/`.

## Docs

The README delegates to charmhub for documentation. `docs/` has guides for getting-started, AZ support,
OSD configuration (file-based + DSL), RGW enable, cluster maintenance, and the terraform module.

**Doc/reality mismatches:**
- Getting-started tutorial says `tentacle/stable rev 155` throughout; deployed charm is
  `squid/stable rev 325`
- Install guide shows `latest/edge rev 3`
- Terraform README says `~> 1.0.0`; `version_constraints.tf` requires `~> 2.0`

**Doc/reality matches:**
- Maintenance mode guide correctly describes dry-run/check-only/ignore-check options and the `noout`
  behaviour
- OSD configuration guide is accurate for the DSL syntax
- `nfs-use-dedicated-binding` documentation correctly warns about the default space fallback

## Open questions

- **Upgrade with `POOL_NO_REDUNDANCY`**: should a cluster operator who deliberately sets
  `default-pool-size=1` be permanently blocked from snap upgrades until OSDs are added and replica
  count restored?
- **Airgapped snap store call**: should a snap upgrade be permitted in airgapped mode with a
  pre-downloaded snap, or should it explicitly block instead of hanging?
- **`ceph_rgw.py` TypeError**: is `model.config.get()` expected to ever return `None` for an option with
  a declared default in `config.yaml`, or is this an ops behaviour quirk at bootstrap time?
- **`receive-ca-cert` library version mismatch**: microceph ships `certificate_transfer_interface/v0`
  (LIBPATCH 6) without a `version` field; `self-signed-certificates` detects this and emits a
  deprecation warning. Worth resolving before the interface library moves further.
- **`_get_bootstrap_params` swallowing**: since `join_cluster` appears to tolerate empty network
  strings by falling back to defaults, is the swallowing purely cosmetic, or can it produce a
  misconfigured join under some network topologies? Not fully verified.
- **`namespace-projects` toggle**: the blocked message says "revert to False" — is the revert value
  hardcoded regardless of what the operator's actual pre-deployment value was?
- **Integrations not exercised**: `ceph` (broker) relation, `adopt-ceph` relation, `remote-requirer`
  relation, NFS/Keystone/MDS providers — these need additional charms or multi-cluster setups not
  available in this environment.
