# redis-k8s

A moderately mature k8s-sidecar Redis charm with Sentinel-based HA, replication, TLS support, and COS integrations. It works — deploy, scale, TLS toggling, and process-kill recovery all behave — but it carries real technical debt from a long history (started as pod-spec, converted to sidecar): a status-assignment bug that silently swallows error states, unguarded `None` access on an "optional" peer relation that every code path assumes exists, a deferred-hook race that left a scaled-up unit stuck for minutes, and a legacy `redis` relation that disables authentication for backward compatibility. Fix the `==`/`=` bug and the deferred-hook race first — both directly affect operator-visible status correctness — then guard peer-relation access, then plan removal of the legacy `redis` relation's password-disabling path.

| | |
|---|---|
| Repo | canonical/redis-k8s-operator @ `0691676` (2025-09-19) |
| Charms | redis-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (juju 4.0.5), ch:redis-k8s edge rev 42 |
| Reviewed | 2026-08-11 |

## What it does

Deploys Redis 7.2.5 on Kubernetes with two Pebble-managed containers: `redis` (the database, port 6379) and `sentinel` (high availability, port 26379). Supports replication across multiple units via Sentinel-managed failover, TLS encryption, COS observability (Prometheus metrics, Grafana dashboards, Loki log forwarding), and a legacy `redis` relation interface for client charms. Provides three actions: `check-service`, `get-initial-admin-password`, and `get-sentinel-password`.

## Deployment log

Deployed on `concierge-k8s-4` (juju 4.0.5) in model `rv-redis-k8s`:

```
juju deploy redis-k8s --channel edge --trust
```

From charmhub edge, revision 42. Reached active/idle in ~15s after pod start:

```
redis-k8s/0*  active    idle   10.1.0.46
```

Scaled to 3 units:

```
juju scale-application redis-k8s 3
```

Units 1 and 2 reached active/idle in ~30s. Unit 0 (the leader) went to `WaitingStatus("Waiting for majority")` and stayed there — sentinel `CKQUORUM` already reported "OK 3 usable Sentinels" but a deferred `_peer_relation_changed` never got re-triggered. A subsequent `juju config redis-k8s enable-tls=false` (a no-op value) unblocked it by firing `config-changed`. This is a race condition in deferred hook recovery — see Finding #2.

Enabled TLS without attaching certificates:

```
juju config redis-k8s enable-tls=true
```

All units went to `WaitingStatus("Waiting for Redis...")`. `_config_changed` checks for missing certs and would set `BlockedStatus("Not enough certificates found")`, but the OCI image ships default self-signed certificates in `/var/lib/redis/`. The `certificates` property only checks Juju-attached resources (which are `None`), so the blocked check is bypassed while the leftover image certs let Redis start TLS with certificates the charm never validated — producing a misleading "Waiting" status instead of "Blocked". See Finding #4.

Disabled TLS: recovered to active in ~10s. Rapid toggle (enable → disable within 3 seconds): recovered fully, both units active.

Scaled down to 2 units: clean, no status blips, ~15s.

Killed the `redis-server` process on unit 0 — Pebble restarted within seconds, status stayed active. Killed the `sentinel` process — same recovery.

Actions `get-initial-admin-password`, `get-sentinel-password`, `check-service` all returned correct results.

## Observed behaviour

- **Resource usage**: 48Mi memory, 4m CPU at idle for the pod (redis, sentinel, charm containers). Lightweight.
- **Startup time**: <15s from unit start to active/idle for a single unit; ~30s for replica units.
- **Sentinel has no log file**: the sentinel config template has no `logfile` directive, so sentinel logs go to stdout only — no `/var/log/redis` directory exists on the sentinel container. Matches open issue #112. `LogProxyConsumer` is configured with `container_name="redis"`, so only `redis-server.log` from the `redis` container is forwarded to Loki; sentinel's stdout is never captured.
- **Hook counts**: single-unit deploy fires 9 hooks (install, peer-relation-created, leader-elected, redis-pebble-ready, sentinel-pebble-ready, storage-attached, config-changed, start, peer-relation-changed) — reasonable. A config change fires one `config-changed` hook per unit, no cascading peer events. Scale-up fires install/peer-relation-created/pebble-ready/storage-attached/config-changed/start/peer-relation-changed per new unit, plus a `redis-peers-relation-joined` on the leader per newcomer — efficient.
- **"Waiting for majority" stuck state**: observed live after scaling 1→3 (see deployment log). `_peer_relation_changed` defers when `sentinel.in_majority` is `False`; CKQUORUM had already succeeded but the deferred event was never re-emitted. Only visible from a real multi-unit deployment, not from code alone.
- **Redis restart on config change**: toggling `enable-tls` restarts both `redis` and `redis_exporter` services because `_update_layer` compares the full Pebble layer and the TLS flags change the command line. A no-op config change (same value) correctly avoids a restart via the same layer comparison.
- **Default certs in OCI image**: `ghcr.io/canonical/charmed-redis:7.2.5-22.04-edge` ships self-signed certs at `/var/lib/redis/{ca.crt,redis.crt,redis.key}`. The charm's `_store_certificates` overwrites these with resource-provided certs when resources are attached, but if none are attached the image defaults remain and Redis starts TLS with certificates the charm never validated.
- **Deferred events without re-trigger**: `event.defer()` is used in 8 places across `charm.py` and `sentinel.py`. `_peer_relation_changed` is the sole handler for `redis-peers-relation-changed`; if it defers, nothing re-triggers it except another change to peer relation data — which is only written by leader-elected, upgrade-charm, and a few explicit handlers. A deferred `_peer_relation_changed` may therefore wait arbitrarily long, matching the observed stuck state above.

## Findings

### 1. `==` used instead of `=` for status assignment (silently broken error handling)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:288`, `src/charm.py:297`
- **Evidence**:
  ```python
  self.unit.status == WaitingStatus(msg)   # line 288
  self.unit.status == BlockedStatus(msg)   # line 297
  ```
  These are equality comparisons, not assignments; unit status is never actually set in either branch. The correctly-written `self.unit.status = ActiveStatus()` at line 300 confirms lines 288/297 are typos.
- **Impact**: In `_peer_relation_departed`, when a failover is in progress, the charm intends to set `WaitingStatus` and defer — instead status is unchanged and there's no visible signal to the operator. When `SENTINEL FAILOVER` raises `RedisError`, the intended `BlockedStatus` is never set, so the error is swallowed silently and the unit doesn't visibly recover or block.
- **Fix**: Change `==` to `=` on both lines.
- **Linter rule**: flag statement-level comparisons between `self.unit.status` and a `Status` constructor call with no assignment; pyright's `reportUnusedExpression` catches this as a side-effect-free statement.

### 2. Deferred `_peer_relation_changed` may never be re-triggered
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:262-264`
- **Evidence**:
  ```python
  if not self.sentinel.in_majority:
      self.unit.status = WaitingStatus("Waiting for majority")
      event.defer()
      return
  ```
  `_peer_relation_changed` is the sole handler for `redis-peers-relation-changed`. A deferred event only re-fires when peer relation data changes, but `in_majority` depends on sentinel state, which changes independently. Observed live: unit 0 stuck in "Waiting for majority" for over two minutes after CKQUORUM already reported OK; only a manually-triggered `config-changed` unblocked it. `_update_status` does not re-check this condition — it only calls `_update_application_master` and `_redis_check`.
- **Impact**: After scaling up, units can remain indefinitely stuck in `WaitingStatus` requiring manual operator intervention.
- **Fix**: Either add the `in_majority`/failover re-check to `_update_status` so periodic status updates recover deferred hooks, or drop `defer()` in favour of a `WaitingStatus` retried by `update-status`, or consolidate the failover logic into a reconcile method triggered by multiple events.
- **Linter rule**: flag `event.defer()` in relation-changed handlers with no matching recovery path in `update-status` (partly checkable).

### 3. Peer relation (`_peers`) accessed without None guard
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:510-512` (`_peers`), `src/charm.py:534-536` (`current_master`), and every `self._peers.data[...]` call site
- **Evidence**:
  ```python
  @property
  def _peers(self) -> Optional[Relation]:
      return self.model.get_relation(PEER)

  @property
  def current_master(self) -> Optional[str]:
      return self._peers.data[self.app].get(LEADER_HOST_KEY)
  ```
  `redis-peers` is declared `optional: true` in `metadata.yaml`, and `get_relation()` returns `Optional[Relation]`, but `current_master` (used by `valid_app_databag()`, `_redis_extra_flags()`, `_leader_elected()`, `_peer_relation_departed()`, `_on_redis_relation_created()`) accesses `.data` unconditionally. Pyright reports `"data" is not a known attribute of "None"` at 8 locations. In practice Juju always creates the peer relation so this hasn't been observed to crash, but it's a latent defect, e.g. before `leader-elected` runs, or after `juju remove-relation`.
- **Impact**: If `_peers` is ever `None`, any code path through `current_master` or `self._peers.data[...]` raises `AttributeError: 'NoneType' object has no attribute 'data'`, crashing the hook.
- **Fix**: Guard with an early return/assert, or narrow the type at each call site. Simplest: assert `self._peers is not None` once framework setup is done, or handle `None` explicitly in `current_master`.
- **Linter rule**: flag `.data` access on `Optional[Relation]` without a None check (pyright already flags this).

### 4. TLS block-or-wait behaviour is misleading
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:207-210`
- **Evidence**:
  ```python
  if self.config["enable-tls"] and None in self.certificates:
      self.unit.status = BlockedStatus("Not enough certificates found")
      return
  ```
  `self.certificates` fetches Juju-attached resources; if none are attached this check should trigger `BlockedStatus`. But the OCI image ships default self-signed certs at `/var/lib/redis/`. `_store_certificates()` only pushes certs it fetched from resources — if none are attached, nothing is pushed, and the image's default certs remain on disk. `_redis_layer()` then generates TLS flags pointing at those certs, Redis starts, but the cert doesn't validate, so `_redis_check()` fails and the unit shows `WaitingStatus("Waiting for Redis...")` rather than a clear blocked message.
- **Impact**: An operator enabling TLS without attaching certificates sees "Waiting" instead of an actionable "Blocked" message telling them to attach certificates.
- **Fix**: Remove the default certs from the OCI image, or check for actual certificate provenance in the container rather than relying only on `retrieve_resource`, or write a flag file when resource-provided certs are pushed so the charm can distinguish resource certs from image defaults.
- **Linter rule**: not mechanically checkable — requires knowledge of image contents.

### 5. Sentinel has no persistent log file
- **Severity**: medium
- **Kind**: bug (matches open issue #112)
- **Where**: `templates/sentinel.conf.j2:1-17`
- **Evidence**: the sentinel config template has no `logfile` directive. The redis container gets `--logfile /var/log/redis/redis-server.log` via `_redis_extra_flags`; the sentinel's Pebble command is just `redis-server /etc/redis-server/sentinel.conf --sentinel` with no logfile. Observed: `/var/log/redis/` doesn't exist on the sentinel container.
- **Impact**: debugging sentinel failover requires logs that aren't captured to file, and `LogProxyConsumer` only forwards the `redis` container's log path, so sentinel logs never reach Loki either.
- **Fix**: add `logfile "/var/log/redis/sentinel.log"` to the sentinel template, create the log directory in that container, and add a sentinel-specific `LogProxyConsumer` (or extend the existing one to cover both containers).
- **Linter rule**: not mechanically checkable.

### 6. `get_master_info` result not None-checked before subscript in `_upgrade_charm`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:146-157`
- **Evidence**:
  ```python
  if not self._is_failover_finished(host=k8s_host):
      event.defer()
      return
  if self.unit.is_leader():
      info = self.sentinel.get_master_info(host=k8s_host)
      self._peers.data[self.app][LEADER_HOST_KEY] = info["ip"]
  ```
  `_is_failover_finished` calls `get_master_info` separately and checks for `None`, but the second call at line 161 is not re-checked before `info["ip"]` is subscripted. If sentinel becomes unreachable between the two calls, `info` is `None` and this raises `TypeError`. The equivalent path in `_update_application_master` (line 676) already guards this correctly (line 674).
- **Impact**: during network flaps or sentinel restarts, `_upgrade_charm` could crash with an unhandled `TypeError` instead of deferring gracefully.
- **Fix**: add `if info is None: event.defer(); return` after line 161.
- **Linter rule**: flag subscript access on a call result typed `Optional[dict]` without a None check (mechanically checkable if `get_master_info`'s return type is annotated).

### 7. `_redis_check()` annotated `-> None` but returns `bool`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:462-479`
- **Evidence**:
  ```python
  def _redis_check(self) -> None:
      ...
      return True   # line 474
      ...
      return False  # line 479
  ```
  Used by `check_service`, which branches on the return value — works at runtime, but the annotation contradicts the implementation. Pyright: `Type "Literal[True]" is not assignable to return type "None"`.
- **Impact**: type-checker noise; no runtime effect since the value is actually used.
- **Fix**: change the annotation to `-> bool`.
- **Linter rule**: flag return expressions in functions annotated `-> None` (pyright already flags this).

### 8. `requirements.txt` pins `ops~=2.3.0` — two major versions behind
- **Severity**: medium
- **Kind**: lint
- **Where**: `requirements.txt:5`
- **Evidence**: `ops~=2.3.0`; current ops is 2.24.x.
- **Impact**: misses framework bug fixes and compatibility improvements; works today on Juju 4.0.5 but is increasingly fragile.
- **Fix**: bump to a current `ops` release with testing.
- **Linter rule**: flag `ops` pins below a configured threshold (mechanically checkable).

### 9. Black formatting failure in integration test helpers
- **Severity**: low
- **Kind**: lint
- **Where**: `tests/integration/helpers.py:6`
- **Evidence**: `tox -e lint` fails — black would reformat the file (missing blank line between module docstring and imports).
- **Impact**: CI lint gate fails, blocking PRs unnecessarily.
- **Fix**: run `tox -e format` or add the missing blank line.
- **Linter rule**: standard black check, already caught by CI.

### 10. Release workflow contains stale FIXME about an expired token
- **Severity**: low
- **Kind**: lint
- **Where**: `.github/workflows/release.yaml:18`
- **Evidence**: `credentials: "${{ secrets.CHARMHUB_TOKEN }}" # FIXME: current token will expire in 2023-07-04`
- **Impact**: indicates possible release-automation risk if the token was never actually rotated.
- **Fix**: verify token rotation and remove the stale comment.
- **Linter rule**: not mechanically checkable.

### 11. `unstable` pytest marker declared but never used
- **Severity**: low
- **Kind**: test-gap
- **Where**: `pyproject.toml:12`, `.github/workflows/ci.yaml` (`select-tests` step)
- **Evidence**: `markers = ["unstable"]` is declared and CI filters with `-m 'not unstable'`, but no test uses `@pytest.mark.unstable`. `test_delete_redis_pod` in `test_redis_relation.py` is instead permanently `@pytest.mark.skip(reason="Discourse goes into error on CI on primary change")`.
- **Impact**: CI filtering logic is dead code, and a flaky test is disabled entirely rather than gated to nightly runs.
- **Fix**: change the `skip` on `test_delete_redis_pod` to `unstable` so it runs on schedule but not on PRs.
- **Linter rule**: flag pytest markers declared in config but never applied to a test (mechanically checkable).

### 12. COS library versions are very old
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/grafana_k8s/v0/grafana_dashboard.py`, `lib/charms/prometheus_k8s/v0/prometheus_scrape.py`, `lib/charms/loki_k8s/v0/loki_push_api.py`, `lib/charms/.../juju_topology.py`
- **Evidence**: all vendored at v0 with no visible LIBPATCH updates.
- **Impact**: misses upstream library fixes, potentially including COS compatibility improvements.
- **Fix**: run `charmcraft fetch-lib` to refresh vendored libraries.
- **Linter rule**: flag vendored libraries with a newer upstream version available (checkable via `charmcraft fetch-lib --list`).

## Worth copying

- **Clean two-container Pebble setup**: `redis` and `sentinel` managed as separate Pebble services with clear `_redis_layer()`/`_sentinel_layer()` factories. `src/charm.py:387-410`, `src/sentinel.py:87-104`.
- **`valid_app_databag()` guard pattern**: before rendering configs dependent on peer data, checks readiness and sets `WaitingStatus` rather than proceeding blind. `src/charm.py:342-344`.
- **Separate Redis and Sentinel passwords**: a client with Sentinel access doesn't automatically get Redis access. `src/charm.py:173-179`.
- **`_initialize_directory_structure()` at layer-update time**: creates `/var/log/redis`, `/var/lib/redis` with correct ownership rather than assuming the image provides them. `src/charm.py:355-379`.
- **`_redis_extra_flags()` as a self-contained flag builder**: command-line flags built in one method reading config and peer state, easy to audit. `src/charm.py:415-459`.
- **Tenacity retry on failover check**: `_is_failover_finished` polls sentinel state with `@retry` (stop-after-attempt, wait-fixed) instead of busy-waiting. `src/charm.py:696-718`.
- **`_broadcast_sentinel_command` for cluster-wide operations**: quorum updates and resets are broadcast to every known sentinel rather than assuming leader-only access. `src/charm.py:738-751`.

## Common-practice notes

- **Drift**: `charmcraft.yaml` is minimal — only bare platform plus a setuptools part; no `charm-strict-dependencies` or `analysis.ignore`, which most modern charms declare.
- **Drift**: the legacy `redis` relation disables auth. When it's joined, the charm sets `enable-password = "false"` in peer data, so Redis runs without `--requirepass`. Flagged as deprecated in a comment (`src/charm.py:435-437`) but still fully operational.
- **Drift**: CI uses Juju 2.9.49 (`bootstrap-options: "--agent-version 2.9.49"`) while the charm deploys fine on 4.0.5, as observed. CI should test against the versions the charm actually ships against.
- **Drift**: `metadata.yaml` declares `cert-file`, `key-file`, `ca-cert-file` resources, but TLS integration tests (`tests/integration/test_charm.py:205,224`) are permanently `@pytest.mark.skip` with the comment "TLS will not be implemented as resources in the future" — declared interface and tested behaviour have diverged.
- **Follows convention**: `ops.testing.Harness` for unit tests, with proper cleanup. `tests/unit/test_charm.py:27-34`.
- **Follows convention**: separate `tests/unit` and `tests/integration` directories; `tox.ini` with `lint`, `unit`, `integration-*` environments.

## Tests

- **Unit tests**: 17 tests, all passing. Coverage 78% overall (`charm.py` 77%, `sentinel.py` 75%, `literals.py` 100%). Run with `tox -e unit`.
- **Test quality**: cover Pebble plan generation (including TLS variants), status transitions on update-status/config-changed, password generation/persistence, relation data propagation, and failover scenarios, with appropriate mocking of Redis client calls. `test_non_leader_unit_as_replica` (line 241) correctly checks non-leader units get `--replicaof`.
- **Test gaps**:
  - No test for `_peer_relation_departed` (the handler with the `==` bug).
  - No test for `_upgrade_charm` single-unit path, or with peer units where `get_master_info` returns `None`.
  - No test for `_on_redis_relation_created` with a non-leader unit.
  - No test for `_store_certificates` with mixed valid/invalid resource paths.
  - No test for `_broadcast_sentinel_command` or `_reset_sentinel`.
  - No test for `sentinel.py` independent of `charm.py`.
  - TLS scenario tests (`test_blocked_on_enable_tls_with_no_certificates`, `test_active_on_enable_tls_with_certificates`) only check Pebble plan output — neither tests the observed image-default-cert case.
- **Integration tests**: 4 suites (charm, password, redis-relation, scaling), via `pytest-operator`/`OpsTest`. Scaling tests exercise scale-up after failover and scale-down of the departing master — genuinely valuable. Redis-relation tests deploy Discourse as a real consumer and check end-to-end connectivity, including pod-deletion recovery (though `test_delete_redis_pod` is skipped). Password tests verify rotation survives scale-to-0-and-back. Charm tests verify replication, metrics endpoint, sentinel count, and pod deletion for primary and non-primary pods.
- **Integration test gaps**:
  - No TLS integration testing (both tests skipped).
  - No COS integration testing (grafana-agent, Loki, Prometheus relations declared but untested with real counterparts).
  - No integration test for the legacy `redis` relation on Juju 4.x.
  - No negative testing (bad config, removed required relation, junk peer data).
- **Run environment**: unit tests run in <1s. Integration tests need a full microk8s cluster (not run here); CI uses self-hosted runners on `juju-channel: 2.9/stable`. CI runs lint/unit/integration on PRs; nightly adds "unstable" tests — of which there are currently none (Finding #11).

## Docs

- **README.md** (~100 lines): covers deploy, HA setup, TLS configuration; `--channel edge` reference matches the published channel; the two password-action examples match observed behaviour. Does not mention the legacy `redis` relation, how to relate other charms, or COS integration — these features are undiscoverable from the README alone.
- **DEVELOPMENT.md** (~100 lines): covers local build/deploy with microk8s, debugging, testing. References `ubuntu-20.04` in the charm filename — stale; the charm now targets `ubuntu-22.04`, and the documented `charmcraft pack` output path is wrong for 22.04 builds.
- **Charmhub description**: `metadata.yaml` summary says "replication and clustering are not supported for the moment" — wrong; replication is supported and was observed working (2 replicas), and integration tests verify it. Open issue #116 tracks this doc/behaviour mismatch.
- **Docs link**: `docs: https://discourse.charmhub.io/t/redis-docs-index/4571` in `metadata.yaml`.
- No terraform module. No contributing guide beyond `DEVELOPMENT.md`.

## Open questions

- Is the peer relation truly optional? `redis-peers` is `optional: true`, but every code path assumes it exists. Either add null guards throughout, or drop `optional: true` if it's never actually absent.
- Why does the OCI image ship default TLS certificates? They interact badly with the resource-based TLS model — worth clarifying if intentional (dev convenience) or accidental.
- What replaces the resource-based TLS model? Integration tests are skipped with "TLS will not be implemented as resources in the future" — is a `tls-certificates`-relation migration planned?
- Why does CI pin Juju 2.9.49 (and the scaling test 2.9.29, possibly a typo) when the charm deploys correctly on 4.0.5?
- Is the vendored `redis` relation library (`lib/charms/redis_k8s/v0/redis.py`, LIBPATCH 7) still maintained? The charm itself flags it as a deprecated legacy interface. Separately, its `url` property has a bare `except KeyError` around `dict.get(...)`, which never raises `KeyError` — dead code (`lib/charms/redis_k8s/v0/redis.py:108-111`).
</content>
