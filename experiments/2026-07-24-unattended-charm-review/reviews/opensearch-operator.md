# opensearch-k8s (primary) / opensearch

A large, mature Kubernetes + machine charm for OpenSearch from Canonical's Data
Platform team. Virtually all logic lives in a shared `opensearch-charms-single-kernel`
Python package (v0.0.6, ~44K lines across 82 `.py` files); each charm in this repo is
a thin wrapper around it. The code covers TLS, snapshots/backup, large-deployment
orchestration, OAuth/JWT, SMTP notifications, COS observability, and in-place
upgrades, and is published and actively maintained.

Shape it's in: functionally broad but not safe to trust blindly. The status system
reports `active` while OpenSearch is unreachable (two independent silent-failure
paths — a stuck invalid-roles recovery and a Kubernetes pod restart that corrupts
TLS cert/key state), the k8s and machine charms diverge in recovery behaviour for the
same failure, and there are zero unit tests across ~44K lines of shared kernel code.

A maintainer should first fix the `health_manager` UNKNOWN→`active` fallthrough
(finding 1) and the pod-restart TLS deadlock (finding 11) — both make `juju status`
lie about workload health — then add unit tests for the manager status logic so these
classes of bug stop reaching integration testing.

| | |
|---|---|
| Repo | canonical/opensearch-operator @ `72b7a9a0c5` (2026-07-23) |
| Charms | opensearch, opensearch-k8s, dummy-client-charm (test helper) |
| Substrate | k8s (primary) + machine |
| Deployed | yes — k8s on concierge-k8s-4 (juju 4.0.5), k8s on concierge-k8s-3 (juju 3.6.25), machine on concierge-lxd (juju 3.6.23), machine on concierge-lxd-4 (juju 4.0.5) |
| Reviewed | 2026-08-01 |

## What it does

OpenSearch is an open-source distributed search and analytics engine. The charm
deploys it on Kubernetes or machines, handling:

- **Cluster formation** with automated node discovery and peer relations
- **TLS** for HTTP and transport layers via `tls-certificates`
- **Backup/restore** via S3, Azure Blob Storage, and GCS
- **Large deployments** through `peer-cluster`/`peer-cluster-orchestrator` relations
- **Observability** via COS (`metrics-endpoint`, `grafana-dashboard`, loki logging)
- **OAuth** and **JWT** authentication
- **SMTP** notifications
- **In-place upgrades** with pre-upgrade checks and rollback
- **Horizontal scaling** with safe scale-down
- **Plugin management** (e.g. `opensearch-knn`)

Both charms import `opensearch-charms-single-kernel==0.0.6` from PyPI; the repo itself
contains only thin wrappers and tests.

## Deployment log

### Kubernetes (Juju 4.0.5, concierge-k8s-4)

1. Created model `rv-os-fresh`.
2. Deployed `self-signed-certificates` (latest/stable rev 264).
3. Deployed `opensearch-k8s` from `2/edge` rev 5 (repo `charm_version`=2,
   `workload_version`=2.19.5). Base ubuntu@24.04. Note: `2/edge` rev 5, not `beta`
   rev 3, was tested.
4. Related `self-signed-certificates` to `opensearch-k8s`.
5. Charm reached `active/idle` in ~100s: install 16:23:25, TLS configured 16:23:50,
   security index initialized 16:24:02, active 16:24:28.
6. `pebble services` showed `disabled active` — started manually by the charm, a
   standard pattern.
7. Failure injection:
   - `profile=invalid` → `blocked`, "Invalid profile configuration option. Only
     `production` and `testing` values are allowed." Recovered on fix.
   - `roles=invalid_role` → OpenSearch stopped (16:26:17), charm `blocked`,
     "Missing requirements: At least 1 cluster manager nodes and 1 data nodes are
     required." Fixing to `roles=""` did **not** restart OpenSearch: charm went
     `active` at 16:27:00 while OpenSearch stayed `inactive`.
   - SIGKILL on the OpenSearch process → charm detected and restarted it within ~10s.
   - Removed the TLS relation → charm stayed `active`. `certificates` is not marked
     `optional: true` in `metadata.yaml`.
8. Scaled to 2 units. Unit 1 came up but OpenSearch never started on either unit
   (both `inactive` at 16:26 and after), while both reported `active` in `juju status`.
9. Actions: `get-password`, `set-password` work; `list-backups` correctly fails
   ("Missing relation with an object storage integrator"); `pre-upgrade-check`
   returns "Charm is ready for upgrade".
10. Destroyed model.

### Machine (Juju 3.6.23, concierge-lxd)

1. Created model `rv-os-lxd`.
2. Deployed `self-signed-certificates` (latest/stable rev 264).
3. Deployed `opensearch` from `2/stable` rev 344 (charmhub's latest is rev 345; 344
   was what deployed). Base ubuntu@24.04.
4. Related them.
5. Reached `active` at 16:39 (snap install + security index init ~6 min).
   `get-password`, `pre-upgrade-check` work.
6. No SSH access (publickey rejected) — could not inspect snap services directly.
7. Destroyed model.

### K8s (Juju 3.6.25, concierge-k8s-3)

1. Created model `rv-os-k8s36`.
2. Same deployment as above (`self-signed-certificates` + `opensearch-k8s` 2/edge
   rev 5), related.
3. Reached active in ~65s (same as Juju 4.x).
4. `get-password` returns passwords for `admin` and `monitor`; `set-password
   username=nonexistent` correctly fails ("The action can only be run on the main
   orchestrator cluster").
5. `status-detail` shows all 12 managers `Active`.
6. Confirmed invalid-roles recovery failure, TLS-relation-removal silence, and the
   health-manager active-when-down bug also occur here.
7. **Pod restart failure**: `kubectl delete pod` caused the start hook to fail with
   `OpenSearchCmdError` from `restore_tls_files_from_secrets()` — openssl PKCS12
   export failed: "No cert matches private key." The cert/key in Juju secrets had
   been mismatched by an earlier TLS relation remove/re-add cycle. Unit stuck in
   error; `juju resolve` left it `active/idle` with OpenSearch `inactive`.
8. Destroyed model.

### K8s with COS (Juju 4.0.5, concierge-k8s-4)

1. Created model `rv-os-cos`.
2. Deployed `opensearch-k8s` (2/edge rev 5), `self-signed-certificates`
   (latest/stable rev 264), `grafana-agent-k8s` (2/stable rev 211).
3. Related TLS, `opensearch-k8s:metrics-endpoint`→`grafana-agent-k8s:metrics-endpoint`,
   `opensearch-k8s:grafana-dashboard`→`grafana-agent-k8s:grafana-dashboards-consumer`.
   Both established.
4. `opensearch-k8s:logging` → `grafana-agent-k8s:logging-consumer` failed ("no
   compatible endpoints found") — an endpoint-choice issue, not necessarily a
   code bug (see Observed behaviour).
5. `status-detail` showed all managers active after COS relations were added.
6. Model left running (not destroyed by end of this leg).

### Machine (Juju 4.0.5, concierge-lxd-4)

1. Created model `rv-os-lxd4`.
2. Deployed `opensearch` (2/stable rev 344) and `self-signed-certificates`.
3. Install took ~9 min (snap download + install in LXD container).
4. Reached active; `get-password` returns the admin password.
5. **Unlike k8s, the machine charm recovers from invalid roles**: `roles=invalid_role`
   → blocked ("Missing requirements") → `roles=""` → `active/idle`, OpenSearch
   confirmed running. Opposite of the k8s behaviour on both Juju versions.
6. `status-detail` action **not available** on the published rev 344 — it exists in
   the repo's `machine/actions.yaml` but was added after 344 was packed. The k8s
   charm's `status-detail` correctly lists all 12 manager statuses.
7. TLS relation removal: stayed `active` (same as k8s).
8. Destroyed model.

### Machine (Juju 4.0.5, concierge-lxd-4) — second deploy

1. Created model `rv-os-vm4`.
2. Deployed `opensearch` (2/stable rev 344) and `self-signed-certificates`.
3. Install took ~12 min.
4. Reached active; confirmed all first-deploy findings:
   - `juju list-actions` confirms `status-detail` absent in rev 344.
   - `get-password` works with `username=monitor` and `username=kibanaserver`.
   - Invalid-roles recovery worked: `roles=invalid_role` → blocked → `roles=""` →
     `active/idle`, OpenSearch confirmed running via `get-password`.
   - TLS relation removal: stayed `active`.
5. Destroyed model.

## Observed behaviour

### Status system reports `active` when workload is down

The single most important finding. On two separate models, the charm reported
`active/idle` while OpenSearch was not running:

- `rv-os-k8s` (earlier run, rev 5 on concierge-k8s-4): both units `active/idle` but
  `pebble services` showed `disabled inactive` on both; OpenSearch had been stopped
  at 16:16 and never restarted.
- `rv-os-fresh`: after setting then clearing invalid roles, the charm reached
  `active/idle` at 16:27:00 while OpenSearch had been `inactive` since 16:26.

Root cause: `health.py`'s `get()` returns `HealthColors.UNKNOWN` when
`get_health()` returns `None` (host unreachable), and `get_statuses()`'s match
statement only handles `RED`, `YELLOW_TEMP`, `YELLOW` — `UNKNOWN` (and `IGNORE`)
fall through to the default `[GeneralStatuses.ACTIVE_IDLE.value]`.

The debug-log does capture the error:
```
ERROR unit.opensearch-k8s/0.juju-log opensearch-peers:1: HTTP error when checking cluster health: HTTP error self.response_code=None
self.response_text='Host opensearch-k8s-0...:9200 and alternative_hosts: [] not reachable.'
```
but at ERROR level without affecting status — `juju status` is misleading unless an
operator checks the debug-log.

### Hook noise: every peer-relation-changed fires the full reconciler

A single `juju config profile=invalid` triggered at least 3 full hook executions
(`config-changed`, `opensearch-peers-relation-changed`,
`upgrade-version-a-relation-changed`), each dumping a ~3KB JSON blob of component
statuses to the debug-log. This means O(relations) duplicate status computations per
config change — a performance concern on multi-unit deployments.

### Invalid roles pass config validation, reach OpenSearch, crash the node

`roles=invalid_role` stopped OpenSearch. `opensearch.yml` rendered
`node.roles: [- invalid_role]`. `config.yaml` explicitly documents "Other dynamic
roles are not validated." `PeerClusterConfig` only validates `data.*`-prefixed
roles, not the full role list. Matches open issue #820.

### TLS relation removal does not produce blocked status

`certificates` is not marked `optional: true` in `metadata.yaml`, but removing it
left the charm `active`. `tls_manager` presumably keeps reporting active because it
already has cached TLS artifacts on disk.

### PebbleObserver: background subprocess for deferred-event replay

The charm spawns a background subprocess (`pebble_observer.py`) that periodically
dispatches `pebble_can_connect` events to replay deferred events — a workaround for
the lack of built-in re-dispatch when Pebble-ready is met asynchronously. Clean
pattern (PID tracked in peer data, SIGTERM on stop) but fragile: a subprocess crash
leaves deferred events permanently un-replayed with no alert.

### Positive: process-kill recovery works

Killing the OpenSearch Java process with SIGKILL was detected and the service
restarted within ~10s.

### Pod restart breaks TLS cert/key reconciliation

On the k8s-3 model, after removing and re-adding the TLS relation, `kubectl delete
pod` caused the start hook to fail:
```
OpenSearchCmdError: Command failed: openssl pkcs12 -export ...
stderr=non-zero exit code 1 ... No cert in -in file matches private key
```
`restore_tls_files_from_secrets()` (`managers/tls.py`, around line 600) rebuilds
PKCS12 stores from Juju secrets, but the cert and key in secrets were issued for
different CSRs — the relation remove/re-add cycle generated new CSRs while old certs
stayed cached. There is no fallback path: the charm does not request new
certificates, and the unit is stuck. `juju resolve` moves the charm to
`active/idle` while OpenSearch stays `inactive` — a double failure, since the
health manager then masks the fact that recovery never completed.

### Machine charm recovers from invalid roles; k8s charm does not

On Juju 4.0.5 LXD: `roles=invalid_role` → blocked → `roles=""` → `active/idle`,
OpenSearch running. On k8s (both Juju 3.6 and 4.0.5): the same sequence leaves
OpenSearch `inactive` while status reports `active/idle`. The machine charm uses
snap services; the k8s charm relies on Pebble plus deferred-event replay via
`PebbleObserver`, which appears not to correctly re-emit the start event after the
config fix.

### COS integration: metrics and dashboards work; logging endpoint choice matters

`metrics-endpoint` and `grafana-dashboard` relations to `grafana-agent-k8s` worked.
The `logging` endpoint failed against `grafana-agent-k8s:logging-consumer` with "no
compatible endpoints found"; the correct target is likely
`grafana-agent-k8s:logging-provider` given the interface's provider/consumer roles
(unverified — this relation was not re-attempted with the alternate endpoint). Best
characterized as a documentation/usability gap rather than a confirmed code bug.

### `status-detail` action not in published machine charm revision

`machine/actions.yaml` at repo HEAD defines `status-detail`; `juju list-actions` on
the published rev 344 confirms it is absent — a release gap, not a code bug. The
k8s charm's `status-detail` correctly shows the 12 manager statuses.

### `TLS_RELATION_MISSING` status defined but never used

`TlsStatuses.TLS_RELATION_MISSING` (`common/statuses.py`) is a blocked status
("Missing TLS relation with this cluster.") but is never referenced in
`_on_tls_relation_broken` (`events/tls.py`, ~lines 335-341), which only checks for
in-progress upgrades. This is why TLS removal doesn't produce a blocked status.

### `_on_pebble_can_connect` handler is a no-op

`PebbleObserver` dispatches `pebble_can_connect` to replay deferred events, but the
handler (`events/opensearch.py`, ~lines 1167-1169) only logs and returns; it relies
entirely on ops-framework deferred-event replay mechanics. The observer subprocess
also appears to be one-shot (exits after a successful dispatch), so if the replayed
event re-defers, nothing retries until an unrelated Juju event fires. This is a
plausible root cause of the invalid-roles k8s recovery failure above.

### Timings

- Machine install: ~12 min (Juju 4.0.5 LXD, second deploy), ~6-9 min (Juju 3.6.23
  LXD) — variability from snap download times.
- OpenSearch restart after kill: ~10s.
- K8s install to active: ~100s first deploy, ~65s subsequent deploys.

### Memory footprint (k8s)

- OpenSearch Java process: 1.5GB RSS (1.6GB VSZ), 1GB heap (testing profile).
- Model operator pod: 31Mi.
- Charm pod (Pebble only, no workload): 140Mi.

## Findings

### 1. `health_manager` reports `active` when workload is unreachable

- **Severity**: critical
- **Kind**: bug
- **Where**: `health.py` (`get()` around lines 85-88; `get_statuses()` around
  lines 106-125)
- **Evidence**: `get_health()` returns `None` on connection failure → `get()`
  returns `HealthColors.UNKNOWN` → `get_statuses()`'s match statement only handles
  RED/YELLOW_TEMP/YELLOW, so UNKNOWN and IGNORE fall through to `ACTIVE_IDLE`.
  Confirmed on two separate models.
- **Impact**: `juju status` shows `active/idle` while OpenSearch is down and
  unreachable — a silent failure only visible in debug-logs.
- **Fix**: Handle `HealthColors.UNKNOWN` explicitly in `get_statuses()`, returning
  e.g. `StatusObject(status="blocked", message="Cannot reach OpenSearch cluster")`.
- **Linter rule**: "`HealthManager.get_statuses()` must handle all `HealthColors`
  enum values explicitly" — checkable with an AST visitor.

### 2. Pod restart causes unrecoverable TLS cert/key mismatch

- **Severity**: critical
- **Kind**: bug
- **Where**: `managers/tls.py` (`restore_tls_files_from_secrets`, ~lines 533-600;
  `store_key_pair`, ~lines 470-503)
- **Evidence**: After removing/re-adding the TLS relation, `kubectl delete pod`
  produced `OpenSearchCmdError` from `openssl pkcs12 -export`: "No cert in -in file
  matches private key." Cert and key stored in Juju secrets were issued for
  different CSRs from a non-atomic re-relate cycle.
- **Impact**: A pod restart (node failure, eviction, reschedule) after any TLS
  relation churn leaves the unit permanently errored with no automatic recovery
  path — a data-plane availability issue requiring manual intervention.
- **Fix**: On a `store_key_pair` failure, clear the stale cert from secrets and
  request a fresh CSR, or validate cert/key match before attempting PKCS12 export
  and request new certificates on mismatch.
- **Linter rule**: not mechanically checkable — requires state-transition testing
  with pod restart after TLS churn.

### 3. No recovery after invalid-roles → fix-roles cycle

- **Severity**: high
- **Kind**: bug
- **Where**: `profiles.py` (`check_cluster_topology`, ~lines 99-113) and
  `events/opensearch.py` (deferred-event replay)
- **Evidence**: `roles=invalid_role` stopped OpenSearch and blocked the charm
  ("Missing requirements"). Fixing to `roles=""` moved the charm to `active/idle` at
  16:27:00 while OpenSearch remained `inactive`; debug-log showed "The unit is not
  allowed to start, the event need to be retried later."
- **Impact**: An operator who fixes a bad role config ends up with a silently-down
  cluster reported as healthy.
- **Fix**: When the topology check passes again, explicitly emit
  `start_opensearch_event` rather than relying solely on deferred-event replay.
- **Linter rule**: not mechanically checkable — requires state-transition testing.

### 4. k8s and machine charms diverge in invalid-roles recovery

- **Severity**: high
- **Kind**: bug
- **Where**: `events/opensearch.py` (deferred-event replay) vs. machine snap
  lifecycle
- **Evidence**: `roles=invalid_role` → `roles=""` leaves OpenSearch `inactive` on
  k8s (both Juju 3.6 and 4.0.5) but correctly restarts it on the machine charm
  (Juju 4.0.5 LXD).
- **Impact**: Operators get different recovery guarantees depending on substrate,
  for what should be identical shared-kernel behaviour.
- **Fix**: Align the k8s start path with the machine path — explicitly re-emit the
  start event after topology checks pass, rather than depending on
  `PebbleObserver` replay.
- **Linter rule**: not mechanically checkable.

### 5. `_on_pebble_can_connect` handler is a no-op; PebbleObserver appears one-shot

- **Severity**: high
- **Kind**: bug
- **Where**: `events/opensearch.py` (~lines 1167-1169), `pebble_observer.py`
  (~lines 32-38)
- **Evidence**: The handler only logs and returns. The observer loop appears to
  exit after its first successful dispatch. If a replayed deferred start event
  re-defers (TLS not ready, health check fails, etc.), there is no further retry
  until an unrelated Juju event fires.
- **Impact**: Plausible root cause of finding 3 and a contributing factor to
  finding 2 — any re-defer after `pebble_can_connect` can leave a unit stuck with
  no automatic recovery path.
- **Fix**: Keep the observer loop running instead of exiting after one dispatch, or
  make `_on_pebble_can_connect` actively re-trigger start/health logic. Consider
  using Pebble's built-in `check`/`startup: enabled` auto-restart instead of a
  custom subprocess.
- **Linter rule**: not mechanically checkable — requires state-transition testing.

### 6. No unit tests exist

- **Severity**: high
- **Kind**: test-gap
- **Where**: `tox.ini` defines a `unit` env targeting `tests/unit/`, which does not
  exist in the repo; the single-kernel package ships no tests either.
- **Evidence**: `tests/unit/` absent; `pytest tests/unit/` fails with no tests
  collected; no `test_*.py` in the kernel package.
- **Impact**: ~44K lines of kernel code have no fast-feedback coverage. Findings 1,
  3, and the role-validation gap (finding 7) would all be catchable with unit tests
  of the manager status logic.
- **Fix**: Add unit tests for at minimum `HealthManager.get_statuses()`,
  `ProfilesManager.check_cluster_topology()`,
  `ConfigManager.update_opensearch_config()`, and `StatusHandler` precedence logic.
- **Linter rule**: "Charm must have a `tests/unit/` directory with at least one
  test" — mechanically checkable.

### 7. Role validation is only partial

- **Severity**: medium
- **Kind**: bug
- **Where**: `core/models.py` (`PeerClusterConfig.set_node_temperature`, ~lines
  205-225)
- **Evidence**: Only `data.*`-prefixed roles are validated; `invalid_role` passes
  through. `config.yaml` documents "Other dynamic roles are not validated" as
  deliberate, but the resulting misleading blocked message ("Missing requirements:
  At least 1 cluster manager nodes...") obscures the real cause. Matches open
  issue #820.
- **Impact**: Users see a confusing blocked message unconnected to a typo in
  `roles`.
- **Fix**: Validate roles in `PeerClusterConfig` or `ProfilesManager` against the
  known OpenSearch role set before the topology check.
- **Linter rule**: "config.yaml `roles` must be validated at config-changed time
  against a known set" — mechanically checkable with a static list.

### 8. OpenSearch config renders invalid roles directly into opensearch.yml

- **Severity**: medium
- **Kind**: bug
- **Where**: `config.py` (`_opensearch_general_config`, ~lines 70-81)
- **Evidence**: `opensearch.yml` rendered `node.roles: [- invalid_role]`, causing
  OpenSearch to refuse to start.
- **Impact**: Unvalidated user input is passed straight into the workload config
  file, guaranteeing a crash rather than failing fast in the charm.
- **Fix**: Validate roles before rendering — see finding 7.
- **Linter rule**: same as finding 7.

### 9. `certificates` relation not optional but charm doesn't go blocked on removal

- **Severity**: medium
- **Kind**: bug
- **Where**: `kubernetes/metadata.yaml` (~lines 38-39), `events/tls.py`
  (`_on_tls_relation_broken`, ~lines 335-341)
- **Evidence**: `certificates` has no `optional: true`; removing it on both k8s and
  machine charms left the charm `active/idle`. `_on_tls_relation_broken` only
  checks for in-progress upgrades. `TlsStatuses.TLS_RELATION_MISSING` (blocked,
  "Missing TLS relation with this cluster.") is defined but never used.
- **Impact**: If the relation is required, its removal should surface as blocked
  so operators know certificate rotation has stopped working.
- **Fix**: Wire up `TLS_RELATION_MISSING` in `_on_tls_relation_broken`, or mark
  the relation `optional: true` in metadata if it's genuinely non-required.
- **Linter rule**: "Non-optional `requires` relations must have departed handlers
  that set blocked status" — mechanically checkable.

### 10. `TLS_RELATION_MISSING` status defined but never used

- **Severity**: medium
- **Kind**: bug
- **Where**: `common/statuses.py` (definition), `events/tls.py` (~lines 335-341)
- **Evidence**: Same as finding 9 — the status object exists but is never
  referenced by any event handler.
- **Impact**: Duplicates finding 9's symptom; the fix is a one-line wiring gap.
- **Fix**: Add the status via `self.charm.state.add_status(...)` in
  `_on_tls_relation_broken`.
- **Linter rule**: "Defined `StatusObject` values must be referenced in at least
  one event handler" — mechanically checkable with AST analysis.

### 11. `status-detail` action not in published machine charm revision

- **Severity**: medium
- **Kind**: release-gap
- **Where**: published `opensearch` rev 344 vs. repo `machine/actions.yaml`
- **Evidence**: `juju list-actions` on rev 344 does not list `status-detail`; the
  action is defined at repo HEAD but was added after 344 was packed.
- **Impact**: Operators on rev 344 cannot access the component-level status
  breakdown that the k8s charm exposes.
- **Fix**: Publish a new machine charm revision with the updated `actions.yaml`
  (the handler already exists in the shared kernel).
- **Linter rule**: "Every charm in a multi-charm repo must define the same
  actions" — mechanically checkable by comparing action YAML files.

### 12. Excessive status JSON logged on every hook

- **Severity**: low
- **Kind**: performance/ux
- **Where**: `events/opensearch.py` — the reconciler calls `status_handler.assess()`
  on every hook.
- **Evidence**: A single `juju config profile=invalid` produced 4+ log entries,
  each dumping an identical ~3KB JSON status blob at INFO level.
- **Impact**: Debug-log becomes unreadable, worse on multi-unit deployments.
- **Fix**: Log this JSON at DEBUG level.
- **Linter rule**: not mechanically checkable.

### 13. PebbleObserver subprocess adds operational risk

- **Severity**: low
- **Kind**: bug
- **Where**: `common/pebble_observer.py`
- **Evidence**: A background subprocess replays deferred events; there is no
  watchdog or health check on it.
- **Impact**: Low probability, high impact — a crashed observer leaves a unit
  stuck with no automatic recovery and no alert.
- **Fix**: Add an `update-status` check that verifies the observer PID is alive and
  restarts it if dead, or replace it with Pebble's built-in `check` mechanism.
- **Linter rule**: not mechanically checkable.

### 14. `actions.yaml` description inaccurate for `set-password`/`get-password`

- **Severity**: low
- **Kind**: docs
- **Where**: `kubernetes/actions.yaml` (~lines 17-18), same in `machine/actions.yaml`
- **Evidence**: Description says "Possible values - admin" but `kibanaserver` and
  `monitor` are also supported (confirmed: `get-password username=monitor` returns
  a valid password). Matches open issue #821.
- **Impact**: Misleads operators about supported usernames.
- **Fix**: Update the description/enum to list all supported usernames.
- **Linter rule**: not mechanically checkable.

### 15. `OpenSearchSecrets` class marked as TODO for refactor

- **Severity**: low
- **Kind**: technical-debt
- **Where**: `core/secrets.py` (TODO comment ~lines 3-7; class docstring ~lines
  28-30)
- **Evidence**: Docstring/comment state the class "needs to be refactored" and
  "should be removed when data interfaces v1 is integrated."
- **Impact**: Secrets handling is on the critical path for TLS/password/credential
  management; leaving it in a known-stale state risks bugs at migration time.
- **Fix**: Prioritise the data-interfaces-v1 migration and document the plan.
- **Linter rule**: not mechanically checkable.

### 16. "No databag present" warnings during install (unverified)

- **Severity**: low
- **Kind**: ux
- **Where**: not established
- **Evidence**: Noted in working notes as observed during install; not detailed
  further and not reproduced with specifics in the draft (unverified).
- **Impact**: Log noise during install, similar in kind to finding 12.
- **Fix**: not established.
- **Linter rule**: not mechanically checkable.

### 17. `node.roles` list-of-one-element rendering is valid but unusual

- **Severity**: nit
- **Kind**: ux
- **Where**: `utils/config.py` (YAML config setter)
- **Evidence**: `opensearch.yml` renders `node.roles:\n- invalid_role` rather than
  flow-style `[cluster_manager, data]`. Valid YAML, harder to read at a glance.
- **Fix**: Use flow-style lists for single-element role lists.
- **Linter rule**: not mechanically checkable.

## Worth copying

### Single-kernel architecture

Both charms share one PyPI-published Python package
(`opensearch-charms-single-kernel`). Charm wrappers are ~6 lines each; all logic is
versioned and testable independently of Juju packaging. Other multi-charm repos
(e.g. postgresql-operator) should consider this pattern.

### Component-manager status decomposition

Status is decomposed into 12 named managers (`profiles_manager`, `tls_manager`,
`health_manager`, etc.), each computing its own `get_statuses()`; `StatusHandler`
picks the worst. Cleaner than status logic scattered across event handlers, and the
`status-detail` action exposes it usefully for debugging.

### Explicit Pebble layer with manual service control

The Pebble service is defined `startup: disabled` and controlled manually via
`pebble start`/`stop`, giving the charm full control over when the workload starts
(after TLS/roles are validated) instead of relying on Pebble auto-restart to mask
configuration issues.

### Continuous writes testing pattern

Integration tests use a `ContinuousWrites` helper that writes continuously during
operations and asserts consistency — catches data-loss bugs during scaling,
upgrades, and relation changes. Worth adopting elsewhere.

### Well-structured docs

20+ docs files covering tutorials, how-tos, explanations, references. Tutorial
commands are extracted from markdown and spread-testable — above ecosystem average.

## Common-practice notes

### Follows conventions

- `src/charm.py` entry point, `charmcraft.yaml` at the charm root.
- `ops` framework with standard lifecycle hooks.
- `lib/` for shared libraries, standard `metadata.yaml` interfaces.
- `tox.ini` with `lint`, `unit`, `integration` envs.
- Renovate comments for dependency pinning.
- Uses `data_platform_helpers.advanced_statuses`, becoming a team standard.

### Drifts from conventions

- **No `lib/charms/` in the repo itself**: shared libraries live in the
  single-kernel package instead, which bundles its own copies of
  `lib/charms/data_platform_libs/v0/`. Intentional but creates a forking risk if
  those copies drift from upstream.
- **`charmcraft.yaml` uses `poetry-deps` + `charm-poetry` parts**: modern Data
  Platform team pattern, well documented inline.
- **Base mismatch in charmhub metadata**: `opensearch-k8s` publishes `beta` on base
  `20.04` while `charmcraft.yaml` declares `22.04`/`24.04` platforms. `2/edge`
  rev 5 correctly uses `24.04`, suggesting `beta` rev 3 is stale.
- **`actions.yaml` in `kubernetes/` and `machine/` are identical copies**: expected
  given the shared kernel, but a maintenance burden since changes must land in both.

### Ahead of conventions

- **PebbleObserver background subprocess pattern**: unusual but addresses a real
  problem; risks noted in finding 13.
- **`approved_critical_component` status override**: the upgrades manager uses this
  flag to make upgrade status take precedence during upgrades — a sophisticated
  pattern not yet widely adopted.

## Tests

### Test structure

```
tests/
├── conftest.py               # shared fixtures
├── helpers.py                # Substrate enum
├── integration/
│   ├── conftest.py
│   ├── test_charm.py         # main integration tests (419 lines)
│   ├── helpers.py            # deploy, actions, HTTP helpers
│   ├── helpers_deployments.py
│   └── continuous_writes.py
├── spread/
│   ├── k8s/test_charm.py
│   └── vm/test_charm.py
├── charms/dummy-client-charm/
├── tutorial/extract_commands.py
└── smoke_test.sh
```

### What exists

- 7 async integration tests: deploy, actions (passwords, TLS), client relations,
  horizontal scale, continuous writes (`pytest-operator`, `wait_until` helpers).
- Spread suites for k8s and VM.
- Tutorial tests extracted from markdown, runnable via spread.
- CI: `ci.yaml`, `integration_test.yaml`, `tutorial-tests.yaml`, `release.yaml`.
- Lint: `ruff`, `codespell` in tox.

### What's missing

- Zero unit tests anywhere in repo or kernel package (finding 6).
- No scenario/state-transition tests — `ops-scenario` is a declared dependency but
  unused.
- No isolated manager-level tests, where findings 1 and 3 live.
- No automated failure-injection tests (bad config, killed processes, removed
  relations) — all tested manually for this review.

### Running tests

- Unit: `tests/unit/` absent; `pytest tests/unit/` fails with "file or directory
  not found."
- Integration: requires a full Juju + LXD environment; not run as part of this
  review beyond the manual deployment log above.
- Lint: `tox -e lint` **fails** — ruff format check flags 2 files needing
  reformatting: `tests/conftest.py` (missing blank lines between functions) and
  `tests/tutorial/extract_commands.py` (string concatenation style). Codespell and
  ruff check pass. No `pyright`/`mypy` configured for the ~44K lines of kernel code.

## Docs

### Coverage

20+ files: tutorial (7 steps), how-to (10 topics), explanation (3), reference (2),
organized in a standard Diátaxis layout ("Getting started", "Deployment", "Manage",
"Monitor", "Secure", "Reference").

### Accuracy checks

- Tutorial references Juju 3.5 (open issue #747); the documented
  `sudo snap install juju --channel 3.5/stable --classic` would fail since 3.5 is
  no longer in the snap store.
- COS interface name in monitoring docs is wrong per open issue #702.
- Profiles docs need update per open issue #701.
- OAuth guide is missing the data-integrator integration step per open issue #813.

### Doc/reality mismatch

- `actions.yaml`'s `set-password` description says "Possible values - admin" but
  `kibanaserver` and `monitor` also work (issue #821); the integration test suite
  tests a nonexistent username for failure but doesn't test the other valid ones.
- `config.yaml`'s `roles` description ("Leave this setting blank to allow
  auto-assignment of roles") is accurate but doesn't warn that arbitrary strings are
  passed straight to OpenSearch's config file and will crash the cluster — "Other
  dynamic roles are not validated" is technically true but misleading.

### Outstanding open issues relevant to docs

12 open doc-related issues: #821, #813, #755, #747, #702, #701, #697, #682, #641,
#610, #567, #485. Several overlap with findings in this review.

## Open questions

1. Does the machine charm share the health-manager status bug? The code path is
   shared with k8s (confirmed there on both Juju 3.6 and 4.0.5); could not directly
   verify on machine (no SSH access to kill the snap service).
2. Does a newer kernel release fix the health-manager bug? Not established — v0.0.6
   (the pinned version tested here) has it.
3. What is the intended status when OpenSearch is unreachable — `blocked` or
   `waiting`? The charm may be mid-restart, so `waiting` seems more correct than
   `blocked`; the current `active` is wrong either way.
4. Is the `tcp_retries2` warning ("above recommended 5") actionable on k8s, where
   the pod can't change the sysctl? It fires on every hook, flooding the log —
   should it log once per unit lifetime instead?
5. Does the single-kernel source repository (as opposed to the published PyPI
   package) contain unit tests that simply aren't shipped in the package?
6. Why exactly does the machine charm recover from invalid roles while k8s doesn't?
   Confirmed behavioural difference; root cause in the `_on_config_changed` →
   `start_opensearch_event` path is plausible (see finding 5) but not fully traced.
7. What is the release timeline for `status-detail` on the machine charm, given the
   code is already merged at HEAD?
8. How stale are the 12+ bundled charm libraries in the kernel package relative to
   their upstream sources? Drift would make this an effective fork; not currently
   tracked in `pyproject.toml`.
