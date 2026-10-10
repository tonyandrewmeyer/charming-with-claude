# mysql-router-k8s (and mysql-router VM charm)

A well-structured pair of charms proxying MySQL traffic between application clients and
InnoDB Cluster backends: `mysql-router-k8s` (primary, Pebble-based) and `mysql-router`
(VM, subordinate, snap-based). Both are built on a shared reconciler pattern that is
clean and worth copying. Live testing on k8s found two high-severity bugs that both
cause silent, unrecovered outages: a peer-data flag (`_K8S_SERVICE_CREATING_KEY`) that
is set once and never cleared, permanently masking `Blocked` behind `Maintenance`; and
a Pebble service-health check that reads `startup` instead of `current`, so a manually
or accidentally stopped `mysql_router` process is invisible to the charm and never
restarted. Two further bugs crash hooks/actions on bad input (`loadbalancer-extra-
annotations` invalid JSON takes the whole unit to `error`; `set-tls-private-key` with
bad base64 fails with an opaque `binascii.Error`). The VM charm deploys cleanly and
already has `connection-sharing` active by default, a feature the k8s charm only has
at HEAD, not in its published revision. Password redaction in logging is exemplary.
Both substrates' unit test suites are practically unrunnable in full due to a
combinatorial explosion from parametrized relation-combination tests (2,545 cases on
k8s, 814 on machines), and k8s test coverage sits at 39%, missing the reconcile method
entirely. A maintainer should fix the two high-severity recovery bugs first — they mean
a stopped/crashed router does not come back without manual `pebble start` — then trim
the parametrized test suite so CI and local runs are actually feasible.

| | |
|---|---|
| Repo | canonical/mysql-router-operators @ `59983c3` (2026-07-23) |
| Charms | mysql-router-k8s (primary), mysql-router (VM, subordinate) |
| Substrate | k8s and machines — both deployed and reviewed |
| Deployed | yes — k8s: concierge-k8s-3 (Juju 3.6.25), mysql-router-k8s 8.0/edge rev 929; VM: concierge-lxd (Juju 3.6.23), mysql-router 8.4/edge rev 1173 |
| Reviewed | 2026-08-02 |

## What it does

MySQL Router is a transparent proxy that routes MySQL traffic between applications and
InnoDB Cluster backends. This charm:
- Connects to a MySQL backend (`backend-database` requires relation)
- Bootstraps and runs `mysqlrouter` in a Pebble workload container (k8s) or via the
  `charmed-mysql` snap (machines)
- Provides a `database` relation for downstream applications, creating databases and
  users on demand
- Supports TLS via `certificates` relation (CSR generation, renewal, and a
  `set-tls-private-key` action)
- Supports COS: metrics (Prometheus scrape on port 9152), dashboards (Grafana), logs
  (Loki push API via promtail), tracing (Tempo)
- Manages a k8s Service (ClusterIP / NodePort / LoadBalancer) via `expose-external` config
- Supports in-place refreshes (charm and workload) with a controlled rolling upgrade
- Runs a logrotate executor service in the workload container

## Deployment log

All deployments performed 2026-08-02. Two k8s models and one VM model were deployed,
tested, and destroyed.

### k8s charm — first deploy (concierge-k8s-3, Juju 3.6.25)

```
juju add-model rv-mysql-router-k8s --controller concierge-k8s-3
juju deploy mysql-router-k8s --channel 8.0/edge
juju deploy mysql-k8s --channel 8.0/edge --trust
juju deploy self-signed-certificates --channel latest/stable
juju deploy data-integrator --channel latest/edge --config database-name=testdb
juju integrate mysql-k8s mysql-router-k8s
juju integrate mysql-router-k8s data-integrator
juju integrate mysql-router-k8s self-signed-certificates
```

First hook crash: `certificates-relation-created` failed with
`lightkube.core.exceptions.ApiError: nodes "generic-juju" is forbidden`. Required
`juju trust mysql-router-k8s --scope=cluster` then `juju resolve`. After trust, reached
`active/idle` within ~60s.

### k8s charm — second deploy (concierge-k8s-3, Juju 3.6.25) — deeper testing

```
juju add-model rv-mysql-k8s-deep --controller concierge-k8s-3
juju deploy mysql-router-k8s --channel 8.0/edge --revision 929
juju deploy mysql-k8s --channel 8.0/edge --trust
juju deploy self-signed-certificates --channel latest/stable
juju deploy grafana-agent-k8s --channel 1/stable
juju deploy data-integrator --channel latest/edge --config database-name=testdb
juju trust mysql-router-k8s --scope=cluster
juju integrate mysql-k8s mysql-router-k8s
juju integrate mysql-router-k8s self-signed-certificates
juju integrate mysql-router-k8s data-integrator
juju integrate mysql-router-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate mysql-router-k8s:logging grafana-agent-k8s:logging-provider
```

`juju trust` was performed before relating, and the charm reached `active/idle` with no
hook failures.

### VM charm (concierge-lxd, Juju 3.6.23)

```
juju add-model rv-mysql-vm-deep --controller concierge-lxd
juju deploy mysql-router --channel 8.4/edge
juju deploy mysql --channel 8.0/edge
juju deploy ubuntu --base ubuntu@26.04
juju integrate mysql-router ubuntu:juju-info
juju integrate mysql-router:backend-database mysql:database
```

## Observed behaviour

### Startup performance
- **k8s charm** (rev 929, ubuntu@22.04): download ~10s, install to active ~90s with TLS
  + backend relation pre-established. Time dominated by mysql-k8s cluster creation +
  mysqlrouter bootstrap.
- **VM charm** (rev 1173, ubuntu@26.04): snap install ~60s, mysql cluster setup ~120s,
  router bootstrap ~30s. Total ~3.5min to active.

### Resource usage
- `mysql-router-k8s` pod: 16m CPU, 79Mi memory
- `mysql-k8s` pod: 8m CPU, 2483Mi memory

### Pebble services (k8s, with COS relations)
Four services defined, all running:
- `mysql_router`: enabled, active
- `mysql_router_exporter`: enabled, active (started because COS metrics-endpoint
  relation present)
- `logrotate_executor`: enabled, active
- `promtail`: disabled, active (from grafana-agent-k8s sidecar injection)

### K8s service management
- Creates `mysql-router-k8s-service` (ClusterIP, NodePort, or LoadBalancer depending on
  config)
- Service maps ports 6446 (rw) and 6447 (ro) only — ports 6448 (x_rw) and 6449 (x_ro)
  are opened via `open_port` in `_on_install` but not present in the k8s Service spec
- `_K8S_SERVICE_CREATING_KEY` in peer data is set to `"true"` during service creation
  and **never cleared** (confirmed via peer data inspection on the second deploy). Both
  `k8s-service-creating` and `k8s-service-initialized` remain `"true"` permanently.
- Consequence: `_status()` always returns
  `MaintenanceStatus("Waiting for K8s service connectivity")` (never
  `BlockedStatus("K8s service not connectable")`) when the service connectivity check
  fails.

### Pebble service killed — charm does not detect it
1. `pebble stop mysql_router` → service `current=inactive`, `startup=ENABLED`
2. Charm remains `active/idle` — `mysql_router_service_enabled` checks `startup`, not
   `current`
3. After ~60s, app goes to `maintenance` ("Waiting for K8s service connectivity")
   because the TCP connectivity check fails. Unit stays `active/idle`.
4. Pebble does not restart the service (it was an explicit stop). The charm's
   `_router_running_correctly()` returns `True` (startup is ENABLED), so
   `RunningWorkload.reconcile()` never enters the disable→enable cycle needed to
   restart it.
5. After 5+ minutes the service was still inactive. Only a config change
   (`expose-external=false`) triggered a full reconcile that re-created the k8s service
   and eventually led to recovery. The router process itself was only restarted after
   manually issuing `pebble start`.

### Config failure: loadbalancer-extra-annotations
Setting `loadbalancer-extra-annotations='{bad-json'` with `expose-external=loadbalancer`
causes a `json.JSONDecodeError` in `_reconcile_service()`. Unit goes to `error` state
(`hook failed: "config-changed"`). All reconciliation is blocked until `juju resolve`.
Recovery required setting both config values back.

### set-tls-private-key action failure
Passing `internal-key="not-valid-base64!!!"` causes `binascii.Error: Incorrect padding`
at `common/common/relations/tls.py:232`. The action returns `exit status 1` with no
user-friendly message. The log shows "Saved TLS private key" before the parse attempt,
making it look like the save succeeded when it did not.

### Scale lifecycle
- **Scale up (1→2)**: Second unit bootstrapped and reached active/idle within ~120s.
  k8s Service endpoints updated to include both pod IPs. Database relation endpoints
  updated correctly.
- **Scale down (2→1)**: Unit 1 removed cleanly. k8s Service endpoints reduced to unit 0
  only.

### Relation lifecycle
- Removed `backend-database` relation → app blocked `Missing relation: backend-database`,
  unit waiting. Correct and useful.
- Re-added relation → recovered to active/idle within ~30s.
- Removed `certificates` relation → TLS disabled cleanly, remained active.

### COS integration
- Prometheus scrape job at `*:9152/metrics` correctly published to grafana-agent-k8s
- Alert rules (`HostDown`, `HostMetricsMissing`) properly propagated with model metadata
- Exporter service auto-started on metrics-endpoint relation and auto-stopped on
  relation removal
- grafana-agent-k8s remained `blocked` because no `send-remote-write`/
  `grafana-cloud-config` was provided (expected)

### VM charm (mysql-router, 8.4/edge rev 1173)
- Uses snap `charmed-mysql` revision 230 (8.4.8), held
- Uses unix sockets by default (not TCP) — config shows
  `socket = /var/snap/charmed-mysql/common/run/mysqlrouter/mysql.sock`
- **Connection sharing already active** in the VM charm:
  `routing:bootstrap_rw_split` with `connection_sharing = 1` is in the generated
  config. This differs from the k8s charm, where `connection-sharing` config exists
  only at HEAD (commit `59983c3`), not in the published rev 929.
- Has `max_idle_server_connections = 64` and `router_require_enforce = 1` in DEFAULT —
  not present in k8s config
- Subordinate pattern works: `mysql-router/0` appears as a sub-unit of `ubuntu/0`
- App blocked with `Missing relation: database` (needs a client on the provides
  endpoint) — correct
- Config differs from k8s: has `vip` (virtual IP for external connectivity) and
  `pause-after-unit-refresh`, but no `expose-external`, `connection-sharing`, or
  `loadbalancer-extra-annotations`
- Actions: `pre-refresh-check`, `resume-refresh`, `force-refresh-start`,
  `set-tls-private-key` — same set as k8s. `pre-refresh-check` returns a readiness
  report with rollback instructions.
- No TLS deployed in this session (`self-signed-certificates` not related)

## Findings

### `_K8S_SERVICE_CREATING_KEY` never cleared — status stuck on Maintenance
- **Severity**: high
- **Kind**: bug
- **Where**: `kubernetes/src/charm.py:275-278`, status check at `kubernetes/src/charm.py:151-158`
- **Evidence**:
  ```python
  self._peer_data.set_value(
      common.relations.secrets.APP_SCOPE, self._K8S_SERVICE_CREATING_KEY, "true"
  )
  ```
  Set in `_reconcile_service()` but never deleted. Observed in peer data:
  `k8s-service-creating: "true"` persists permanently. This blocks the `BlockedStatus`
  path in `_status()`:
  ```python
  if self._peer_data.get_value(
      common.relations.secrets.APP_SCOPE, self._K8S_SERVICE_CREATING_KEY
  ):
      return ops.MaintenanceStatus("Waiting for K8s service connectivity")
  ```
- **Impact**: When the k8s service exists but is unreachable (router stopped, node
  failure), the app shows `maintenance` instead of `blocked`. An operator cannot
  distinguish "still coming up" from "permanently broken." Confirmed live: after
  killing pebble `mysql_router`, the charm showed `maintenance` for 5+ minutes with no
  recovery.
- **Fix**: Clear `_K8S_SERVICE_CREATING_KEY` from peer data once
  `_check_service_connectivity()` returns True (or after a timeout). Alternatively,
  derive status entirely from `_check_service_connectivity()` without a separate
  "creating" flag.
- **Linter rule**: "peer relation flag is set but never unconditionally cleared within
  the same class" — mechanically checkable.

### Pebble service state check reads `startup`, not `current` — dead router invisible
- **Severity**: high
- **Kind**: bug
- **Where**: `kubernetes/src/rock.py:95-99`, `common/common/workload.py:411,428`
- **Evidence**:
  ```python
  # rock.py:95-99
  @property
  def mysql_router_service_enabled(self) -> bool:
      service = self._container.get_services(self._SERVICE_NAME).get(self._SERVICE_NAME)
      if service is None:
          return False
      return service.startup == ops.pebble.ServiceStartup.ENABLED
  ```
  Used by `_router_running_correctly()` (`workload.py:411,428`), which for k8s returns
  `self._container.mysql_router_service_enabled`. After `pebble stop mysql_router`,
  `startup` stays `ENABLED` but `current` becomes `inactive`.
- **Impact**: The charm cannot detect a manually stopped router. It returns
  `RunningWorkload` and `_router_running_correctly()` → `True` even though the workload
  is dead, so `RunningWorkload.reconcile()` never enters the `_disable_router()` path
  needed to restart. Pebble does not auto-restart explicitly-stopped services.
  Reproduced live: router stayed inactive for 5+ minutes through multiple idle cycles.
  Only a config change (`expose-external=false`) triggered enough reconciliation to
  re-create the k8s service; the router process itself was only restarted after
  manually issuing `pebble start`.
- **Fix**: Check `service.current == ops.pebble.ServiceStatus.ACTIVE` in addition to
  `startup`. Add a health check in `update-status` that restarts services whose
  startup is enabled but current is inactive, or use Pebble health checks.
- **Linter rule**: "pebble service enabled check reads `startup` but not `current`" —
  mechanically checkable in Pebble-using charms.

### Unit test suite is combinatorially infeasible
- **Severity**: high
- **Kind**: test-gap
- **Where**: `kubernetes/tests/unit/scenario_/database_relations/combinations.py` →
  parametrized across `test_database_relations.py`
- **Evidence**: Excluding `database_relations/`, the k8s test suite runs in ~20s (11
  tests, 39% coverage). Including it attempts 2,545 parametrized test cases and timed
  out at 300 seconds during this review. The machines charm has the same architecture
  with 814 parametrized tests (40s, 57% coverage).
- **Impact**: Developers cannot run the full test suite locally in a reasonable time.
  This discourages running tests before committing and slows CI feedback. The
  combinatorial approach tests many trivially equivalent cases at low marginal value —
  2,545 tests still only reach 39% coverage on k8s because they exercise database
  relation combinations, not the rest of the reconcile logic.
- **Fix**: Reduce the combination space using equivalence classes or property-based
  testing. A well-chosen set of ~50 parametrized cases would likely cover the same
  logic with comparable confidence.
- **Linter rule**: "parametrized test count > 500" would flag this.

### `functools.cache` on bound methods — forever-stale k8s API caches
- **Severity**: medium
- **Kind**: bug
- **Where**: `kubernetes/src/charm.py:198-209`
- **Evidence**:
  ```python
  @functools.cache
  def _get_pod(self, unit_name: str) -> lightkube.resources.core_v1.Pod:
  ```
  `functools.cache` on a bound method caches by `(self, unit_name)`. Since `self` is
  the charm instance (lifetime of the unit agent), these caches never expire. Same
  pattern for `_get_node`.
- **Impact**: If a pod is recreated (container restart, node migration), the cached pod
  object becomes stale. The node backing a pod can also change, causing
  `_get_hosts_ports()` to return stale node IPs and give wrong endpoints to downstream
  applications. Also affects TLS SAN generation (`tls_sans_ip()` calls
  `get_all_k8s_node_hostnames_and_ips()`, which uses `_get_node()`). Not reproduced live
  (unverified in practice — pods were stable throughout this review); node-drain impact
  is inferred from the code.
- **Fix**: Use `functools.lru_cache` with a TTL, clear the cache each reconcile cycle,
  or (better) don't cache these — lightkube GETs are fast and called at most once per
  reconcile.
- **Linter rule**: "`@functools.cache` on a bound method" — mechanically checkable.

### set-tls-private-key action crashes with opaque error on invalid key
- **Severity**: medium
- **Kind**: bug
- **Where**: `common/common/relations/tls.py:218-225` (parse), crash observed at line 232
- **Evidence**:
  ```python
  def _parse_tls_key(self, raw_content: str) -> str:
      if re.match(r"(-+(BEGIN|END) [A-Z ]+-+)", raw_content):
          return re.sub(...)
      return base64.b64decode(raw_content).decode("utf-8")
  ```
  Passing `internal-key="not-valid-base64!!!"` causes `binascii.Error: Incorrect
  padding`. Reproduced live: action task fails with `exit status 1`, no user-friendly
  message. The action logs "Saved TLS private key" before attempting the parse,
  misleading in the logs.
- **Impact**: An operator receives an unhelpful error and cannot distinguish "wrong
  format" from "internal error."
- **Fix**: Validate key format upfront with try/except; call
  `event.fail("Invalid key format: must be PEM or base64-encoded")`.
- **Linter rule**: "action handler calls parse function without catching format
  errors" — mechanically checkable.

### loadbalancer-extra-annotations config crash on invalid JSON
- **Severity**: medium
- **Kind**: bug
- **Where**: `kubernetes/src/charm.py:236`, within `_reconcile_service()`
- **Evidence**:
  ```python
  annotations = (
      json.loads(self.config.get("loadbalancer-extra-annotations", "{}"))
      if desired_service_type == _ServiceType.LOAD_BALANCER
      else {}
  )
  ```
  Setting `loadbalancer-extra-annotations='{bad-json'` with
  `expose-external=loadbalancer` causes a `json.JSONDecodeError`. Reproduced live: unit
  goes to `error` state, all reconciliation blocked.
- **Impact**: A single bad config value takes the entire charm offline until
  `juju resolve` plus a config fix.
- **Fix**: Wrap `json.loads()` in try/except; return
  `BlockedStatus("Invalid JSON in loadbalancer-extra-annotations")`.
- **Linter rule**: "`json.loads()` of config value not wrapped in try/except" —
  mechanically checkable.

### Hook crashes when k8s API inaccessible before trust
- **Severity**: medium
- **Kind**: bug
- **Where**: `kubernetes/src/charm.py:467` (`get_all_k8s_node_hostnames_and_ips`) →
  `kubernetes/src/charm.py:209` (`_get_node`)
- **Evidence**:
  ```python
  def get_all_k8s_node_hostnames_and_ips(self) -> tuple[list[str], list[str]]:
      node = self._get_node(self.unit.name)  # line 467, no try/except
  ```
  Called from `tls_sans_ip()` (line 436), itself called from the TLS
  `_on_tls_relation_created` path via `request_certificate_creation`. The lightkube
  `ApiError` propagates uncaught. Reproduced live:
  `certificates-relation-created` hook failed until `juju trust` + `juju resolve`.
- **Impact**: If the TLS relation is created before `juju trust` is run, the charm
  crashes. The eventual status message points to `juju trust`, but only after the hook
  has already failed.
- **Fix**: Wrap `get_all_k8s_node_hostnames_and_ips()` (or all lightkube calls) in a
  try/except that catches `ApiError` and returns a graceful `BlockedStatus`.
- **Linter rule**: "lightkube client usage not guarded by try/except ApiError" —
  mechanically checkable.

### Potential AttributeError in `_remove_value` during teardown
- **Severity**: medium
- **Kind**: bug
- **Where**: `common/common/relations/secrets.py:77-82`
- **Evidence** (from reading code, not reproduced live):
  ```python
  def _remove_value(self, scope: Scopes, key: str) -> None:
      peers = self._charm.model.get_relation(self._relation_name)
      self._peer_relation_data(scope).delete_relation_data(peers.id, [key])
  ```
  If `get_relation()` returns `None` (peer relation already gone during teardown),
  `peers.id` raises `AttributeError`. Referenced in an open upstream issue (#115) as
  causing `certificates-relation-broken` to fail during scale-in — not independently
  reproduced in this review (unverified).
- **Impact**: A crash during teardown can leave stale secrets and prevent clean removal.
- **Fix**: Guard with `if peers is None: return`.
- **Linter rule**: not established.

### Test coverage gap: reconcile method barely covered
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `kubernetes/src/charm.py` (33% covered), `common/common/abstract_charm.py`
  (not covered in k8s tests)
- **Evidence**: The k8s unit tests achieve 39% overall coverage across 11 tests
  (excluding the parametrized relation suite). The reconcile method has branches for
  leader/not-leader, refresh-in-progress, relation-breaking, workload states, and
  exception handling — none exercised. Existing scenario tests (`test_start.py`) only
  cover the startup path with different relation combinations. No tests exist for TLS
  state transitions, k8s service reconciliation (`_reconcile_service`),
  `_check_service_connectivity`, `_update_endpoints`, actions, COS integration, config
  change handling, refresh/upgrade lifecycle, or Pebble service state transitions.
- **Impact**: The bugs found live in this review (service-creating flag, `startup`
  vs `current`) are exactly the kind of reconcile-path logic this coverage gap misses.
- **Fix**: Add scenario tests for the reconcile method's major branches. Mock lightkube
  for k8s service tests. Use `ops.testing.Harness` or scenario for TLS and COS
  integration tests.
- **Linter rule**: "coverage on primary charm module below 50%" would flag this.

### Ports 6448/6449 opened but not present in the k8s Service
- **Severity**: low
- **Kind**: ux
- **Where**: `kubernetes/src/charm.py:482-483` (`_on_install`), Service spec at
  `kubernetes/src/charm.py:260-263`
- **Evidence**:
  ```python
  for port in (self._READ_WRITE_PORT, self._READ_ONLY_PORT, 6448, 6449):
      self.unit.open_port("tcp", port)
  ```
  The k8s Service created in `_reconcile_service()` only maps ports 6446 (rw) and 6447
  (ro). Ports 6448 (x_rw) and 6449 (x_ro), for the X Protocol, are opened on the pod but
  never mapped through the Service.
- **Impact**: Ports 6448/6449 are unreachable through the k8s Service. Low severity
  since on k8s `open_port` is largely a no-op — the charm manages its own Service
  object separately.
- **Fix**: Either add 6448/6449 to the k8s Service spec, or remove them from
  `_on_install`.
- **Linter rule**: "`unit.open_port` for a port not present in k8s Service spec" —
  mechanically checkable.

### connection-sharing config in code but not yet published
- **Severity**: nit
- **Kind**: docs
- **Where**: `kubernetes/config.yaml:6-24`, `common/common/workload.py:277-282`
- **Evidence**: The `config.yaml` at HEAD defines `connection-sharing` (boolean,
  default false) and the workload bootstrap code reads it, but the deployed revision
  929 (8.0/edge) does not expose this config option — `juju config mysql-router-k8s
  connection-sharing` returns "key not found". The code was added in commit `59983c3`.
- **Impact**: Operators reading HEAD docs expecting this feature will not find it in
  the currently published revision.
- **Fix**: Publish the new revision to 8.0/edge.
- **Linter rule**: not established.

## Worth copying

### Reconciler pattern (`common/common/abstract_charm.py`)
The charm observes **every event** (except `CollectStatusEvent`) and routes them all to
a single `reconcile()` method:
```python
for bound_event in self.on.events().values():
    if bound_event.event_type == ops.CollectStatusEvent:
        continue
    self.framework.observe(bound_event, self.reconcile)
```
This eliminates ordering bugs and is a pattern other charms should adopt.

### Status priority with fallback
`_prioritize_statuses()` and `_determine_unit_status()` / `_determine_app_status()`
correctly implement status precedence: Blocked > Maintenance > Waiting > Active, with
the refresh mechanism allowed to override. The `unit_status_lower_priority` callback
from `charm_refresh` is a clean extension point.

### TLS CSR handling (`common/common/relations/tls.py`)
The `RelationEndpoint` correctly tracks CSR state (`tls-requested-csr`,
`tls-active-csr`), handles renewal, and ignores unknown certificates. State is kept in
peer relation secrets, not `StoredState`.

### Redacted logging of sensitive data (`common/common/workload.py`)
The bootstrap command and errors are logged with `RedactedConnectionInformation`
(password replaced with `***`), and exceptions containing passwords are caught and
re-raised with `from None`:
```python
logger.error(f"Failed to bootstrap router\n{logged_command=}\nstderr:\n{e.stderr}\n")
raise Exception("Failed to bootstrap router") from None
```

### Graceful handling of user deletion during teardown
`_RelationWithSharedUser.delete_user()` catches `ExecutionError` (which may occur if
MySQL already revoked credentials during teardown) and falls back to
`delete_databag()`:
```python
try:
    relation.delete_user(shell=shell)
except ExecutionError:
    logger.warning("Failed to delete user... Cleaning up databag only")
    relation.delete_databag()
```

### Container abstraction layer (`common/common/container.py`)
The `Container` ABC and `Path` ABC cleanly separate the snap (VM) and rock (k8s)
implementations — a well-factored pattern for multi-substrate charms.

### Lifecycle / authorized_leader (`common/common/lifecycle.py`)
Correctly handles the known Juju bugs LP #1979811 and LP #2025676 by using `goal-state`
to determine whether a tearing-down leader should still act as leader. Prevents a
departing leader from doing cleanup that the new leader should handle.

### VM charm already has connection-sharing
The VM charm (8.4/edge rev 1173) bootstraps with `routing:bootstrap_rw_split` and
`connection_sharing = 1` baked into the config directly, plus
`max_idle_server_connections = 64`. The k8s charm only gets this feature at HEAD
(commit `59983c3`), gated behind a config option. The VM charm's approach (baked into
bootstrap) is simpler even though it exposes less operator control.

## Common-practice notes

### Follows
- `src/` layout with `src/charm.py` as main entry point
- `lib/charms/` for external charm libraries, `common/common/` for shared code
- `charmcraft.yaml` with poetry plugin and explicit part names
- `charm-user: non-root` — runs as uid 584788
- Metadata follows Canonical Data Platform conventions: `assumes` with `juju >= 3.6.0`,
  `peers` relations
- `concierge.yaml`, `tox.ini`, GitHub Actions CI — standard DPW setup

### Drifts
- `charm_refresh` for upgrades: unique to the DPW ecosystem; most charms don't have
  this level of upgrade sophistication
- Lightkube direct access: most k8s charms avoid direct k8s API access. This charm
  uses it for node lookups (TLS SANs) and k8s Service management, creating the trust
  requirement.
- `_read_write_endpoints` / `_read_only_endpoints` take an `event` parameter but are
  often called with `None` — a pragmatic compromise between VM (needs event for port
  reconciliation) and k8s (doesn't)

### Ahead of convention
- Redacted logging with `from None` exception chaining — few charms handle password
  redaction this thoroughly
- Connection-sharing already active in the VM charm, ahead of the k8s charm's
  published state

## Tests

### Unit tests — k8s
- Location: `kubernetes/tests/unit/`
- Framework: pytest with ops-scenario (state-transition testing)
- Files: `test_architecture.py` (3 tests), `test_rock_path.py` (2 tests),
  `test_workload.py` (2 tests), `scenario_/test_start.py` (4 tests),
  `scenario_/database_relations/test_database_relations.py` (~2,400 parametrized),
  `scenario_/database_relations/test_database_relations_breaking.py` (~140 parametrized)
- Run result (excluding `database_relations`): 11 passed in 20s, 39% coverage. `ruff`
  and `codespell` both pass cleanly.
- Run result (including `database_relations`): timed out at 300s. 2,545 tests
  collected.
- Coverage gaps: `src/charm.py` at 33%, `src/rock.py` at 44%. The reconcile method
  (leader/non-leader branches, refresh-in-progress, relation-breaking, exception
  handling), k8s service reconciliation, TLS state transitions, COS integration, config
  changes, and actions are all untested.

### Unit tests — machines
- Location: `machines/tests/unit/`
- Files: `test_architecture.py`, `test_snap_path.py`, `test_workload.py`,
  `scenario_/test_*.py`
- Run result: 814 passed in 40s, 57% coverage. Same combinatorial explosion pattern as
  k8s.
- `src/charm.py` at 61%, `src/snap.py` at 48%, `src/relations/hacluster.py` at 38%.

### Integration tests
- Framework: Jubilant (recently migrated from pytest-operator per commits `d6b91693`
  and `e5261c9c`)
- Present for both k8s and machines, with dedicated test files for connection-sharing,
  TLS, refresh, COS
- Not run (requires a full Juju environment)

### Lint tools
- `ruff`: all checks passed
- `codespell`: no issues found
- `poetry check --lock`: clean
- `terraform fmt/validate`: available via `tox -e lint-terraform` (not run)

## Docs

- **README.md**: adequate; could benefit from mentioning the trust requirement and the
  `expose-external` config.
- **Discourse docs**: navigation hub at `kubernetes/docs/overview.md` pointing to
  Discourse topics.
- **CONTRIBUTING.md**: present.
- **Doc/reality mismatch**: the README does not mention the required
  `juju trust mysql-router-k8s --scope=cluster` step. Without trust, the TLS relation
  hook crashes (see findings above). The `connection-sharing` config is documented in
  the code but not present in the published charm revision.

## Open questions

1. Why does the charm need node-level k8s API access for TLS SANs? `tls_sans_ip`
   queries k8s node addresses to generate IP SANs for the TLS certificate. Could the
   charm use pod-level addresses or the k8s Service instead? This is what creates the
   trust requirement.
2. Is the `_K8S_SERVICE_CREATING_KEY` issue already known upstream? Not found in the
   open issues list checked during this review. Issue #22 ("mysql-router-k8s in
   blocked status") may be related but describes a different scenario.
3. Does `connection-sharing` work correctly once deployed? The code is at HEAD, not in
   published rev 929. `RunningWorkload.reconcile()` checks whether
   `_router_connection_sharing_enabled != connection_sharing_config` and triggers
   `_disable_router()` if they differ — untested live in this review.
4. What is the real-world impact of `functools.cache` on `_get_pod`/`_get_node`? Pods
   are normally stable in k8s, but a node-drain/pod-reschedule scenario was not tested
   live.
5. Why does the VM charm bootstrap with connection-sharing already active while the
   k8s charm gates it behind config (default false)? An inconsistent approach across
   substrates worth reconciling.
