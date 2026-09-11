# pyroscope-operators

A well-engineered pair of k8s charms (coordinator + worker) deploying a horizontally-scalable
Grafana Pyroscope cluster via the coordinated-workers library. Code is clean, unit test
coverage is strong (99%/100%), and both charms deploy cleanly on Juju 3.6 and 4.x with correct
COS integrations (Grafana, Prometheus, catalogue). The deployed 2/edge revision is stale
relative to HEAD: it lacks `retention_period`/`deletion_delay` config, carries a permanently
misleading `[degraded]` status that HEAD has already fixed but not released, and blocks on an
explicit empty-string config value. Six of eight integration test modules are skipped,
including all COS self-monitoring and profiling tests — the two integration surfaces that
matter most for this charm are untested. A maintainer's first move should be releasing the
`[degraded]` fix to 2/edge and unskipping (or replacing) the self-monitoring and profiling
integration tests; the empty-string config bug and the transient nginx-reload error on worker
removal are next.

| | |
|---|---|
| Repo | canonical/pyroscope-operators @ `a396d74` (2026-07-13) |
| Charms | pyroscope-coordinator-k8s, pyroscope-worker-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5): rv-pyro4 (TLS+ingress), rv-pyro-deep (full COS), rv-pyro-deep2 (role-specific worker, failure injections); concierge-k8s-3 (Juju 3.6.25): rv-pyro3, rv-pyro-reset (config reset testing). All on 2/edge (coordinator rev 75, worker rev 27) |
| Reviewed | 2026-07-27 |

## What it does

Deploys Grafana Pyroscope (continuous profiling backend) in the coordinated-workers pattern.
The coordinator runs nginx for HTTP/gRPC routing and owns external integrations (S3, ingress,
TLS, metrics, logging, tracing, Grafana, catalogue). Workers run Pyroscope roles (all, querier,
query-frontend, ingester, distributor, compactor, store-gateway, tenant-settings,
ad-hoc-profiles) and get their config from the coordinator over the `pyroscope-cluster` relation.

## Deployment log

**Controller `concierge-k8s-4` (Juju 4.0.5), model `rv-pyro4`:**

```
juju add-model rv-pyro4 --controller concierge-k8s-4
juju deploy pyroscope-coordinator-k8s --channel 2/edge pyroscope --trust
juju deploy pyroscope-worker-k8s --channel 2/edge pyroscope-worker --trust
juju deploy seaweedfs-k8s --channel latest/edge swfs --trust
juju deploy self-signed-certificates --channel 1/edge ssc --trust
juju deploy traefik-k8s --channel latest/edge traefik --trust
juju integrate pyroscope pyroscope-worker
juju integrate pyroscope swfs
juju integrate pyroscope ssc
juju integrate pyroscope traefik
```

After ~35s the worker went active "(all roles) ready." Coordinator went active
"`[degraded]` UI ready at http://10.43.45.0/rv-pyro4-pyroscope" (ingressed via Traefik). TLS
certificates provisioned correctly.

**Controller `concierge-k8s-3` (Juju 3.6.25), model `rv-pyro3`:**

```
juju add-model rv-pyro3 --controller concierge-k8s-3
juju deploy pyroscope-coordinator-k8s --channel 2/edge pyroscope --trust
juju deploy pyroscope-worker-k8s --channel 2/edge pyroscope-worker --trust
juju deploy seaweedfs-k8s --channel latest/edge swfs --trust
juju integrate pyroscope pyroscope-worker
juju integrate pyroscope swfs
```

Same result: active `[degraded]`, worker active. URL:
`http://pyroscope.rv-pyro3.svc.cluster.local:8080` (no ingress). No behavioural differences
between Juju 3.6 and 4.x.

**Failure injections (across both models):**

- SIGKILL on pyroscope master process → pebble auto-restarted it immediately; the `ready`
  check on `/ready` passed on the next probe. Charm status never changed — no Juju event fired,
  so the transient failure was never detected.
- SIGKILL on nginx (coordinator) → same: pebble auto-restarted, charm status unchanged.
- Removed S3 relation → `blocked [s3] Missing S3 integration.` (both Juju versions).
- Re-added S3 → recovered to active (still `[degraded]`).
- Removed TLS relation → stayed active (TLS is optional; correct).
- `cpu_limit="badvalue"` on coordinator → `blocked`: `Failed obtaining resource limit spec: Invalid limits spec: {'cpu': 'badvalue', 'memory': None}`. Recovered on valid value.
- `cpu_limit="badvalue"` on worker → same message; recovered with `cpu_limit=500m`.
- `cpu_limit=""` on worker → `blocked`: `Invalid limits spec: {'cpu': '', 'memory': None}`. Recovered with `cpu_limit=500m`.
- `cpu_limit=""` on coordinator → also `blocked` with the same message (verified on rv-pyro-deep; an earlier run had suggested the coordinator did not block, which was a timing artifact — both charms block identically on empty strings).
- Scale worker 1→2 → transient memberlist instability (~60s of readiness-check failures, "no acks received"), then both settle active. Coordinator stays `[degraded]` (2 workers still short of the recommended 3 replicas for most roles).
- Scale 2→1 → clean teardown, `worker/0` stays active.

**COS integration verification (model `rv-pyro-deep`):**

```
juju deploy grafana-k8s --channel 2/edge grafana --trust
juju deploy prometheus-k8s --channel 2/edge prometheus --trust
juju deploy catalogue-k8s --channel 2/edge catalogue --trust
juju integrate pyroscope prometheus
juju integrate pyroscope:grafana-dashboard grafana
juju integrate pyroscope:grafana-source grafana
juju integrate pyroscope catalogue
```

All integrations published correct data: Prometheus received alert rules
(`NginxHighHttp4xxErrorRate`, etc.), Grafana received dashboard JSON and a
`grafana-pyroscope-datasource` entry, catalogue received the item with name/icon/URL.

**Worker removal / lifecycle:**

- Scaled worker to 0 → coordinator stayed active (relation still exists); worker showed
  `blocked [node down]`.
- Removed worker application entirely → coordinator correctly went `blocked [consistency] Missing any worker relation.`
- During removal, coordinator briefly hit `error`: `nginx -s reload` returned exit code 1
  (`ops.pebble.ExecError`), likely because the regenerated nginx config had stale upstreams.
  Auto-recovered on the next hook retry.
- Re-deployed worker and re-integrated → cluster recovered to active (still `[degraded]`).

**S3 credentials anomaly**: the seaweedfs S3 relation published `access-key: "placeholder"` and
`secret-key: "placeholder"` as literals, and the charm passed them through unchanged to the
worker config. This is a seaweedfs behaviour, not a pyroscope-operators bug, but it means the
"S3" backend tested here has no real access control (unverified whether seaweedfs enforces auth
in other configurations).

**Actions**: neither charm defines any actions.

**Deep-dive: role-specific worker (model `rv-pyro-deep2`, Juju 4.0.5)**

Coordinator + single worker with all 9 individual roles explicitly enabled
(`role-all=false`, each `role-X=true`). Worker came up listing all 9 roles; coordinator
`[degraded]`. Worker config file confirmed: no `limits` section, no
`cleanup_interval`/`deletion_delay` in the compactor section. nginx config had all 9
role-specific upstream blocks plus a generic "worker" upstream. Pebble `ready` check: 6
successes, 0/3 threshold failures.

Setting `role-compactor=false` on the worker → worker restarted with 8 roles → coordinator
detected the gap → `blocked [consistency] Cluster inconsistent.` (message did not name the
missing role). Re-enabling `role-compactor=true` → recovered to active within ~60s.

**Deep-dive: config reset testing (model `rv-pyro-reset`, Juju 3.6.25)**

`juju config --reset cpu_limit` → value becomes unset (`None`), charm stays active — no
blocked state. `juju config cpu_limit=""` on both charms → `blocked`:
`Failed obtaining resource limit spec: Invalid limits spec: {'cpu': '', 'memory': None}`.
Recovery with `cpu_limit=500m` → maintenance → active within ~60s. On Juju 4.x, `--reset`
could not be tested (client 4.0.12 vs controller 4.0.5: "patterns are not implemented").

**Pebble services**: all correct — nginx and nginx-prometheus-exporter active in coordinator;
pyroscope active in worker (both Juju versions).

**Resource usage at idle** (Juju 3.6): coordinator 2m CPU / 56Mi, worker 4m CPU / 87Mi. Juju 4
with ingress+TLS: coordinator 2m CPU / 58Mi, worker 8m CPU / 91Mi.

**Worker pod readiness time**: ~35–40s from container start to "(all roles) ready." on first
deploy. Pebble health check uses `http://<fqdn>:4040/ready` with threshold 3. The worker
charm's `restart()` has a 5-minute timeout with 60s between retries.

## Observed behaviour

### `[degraded]` status: root cause identified

The deployed 2/edge coordinated-workers library (not HEAD) has an `is_recommended` check
against a `RECOMMENDED_DEPLOYMENT` dict requiring 3 replicas of querier, ingester, compactor,
store-gateway and 2 of query-frontend, query-scheduler, distributor.
`_on_collect_unit_status` sets `ActiveStatus(self._default_degraded_message)` when the cluster
is coherent but not "recommended"; the charm's `_default_degraded_message` prepends
`"[degraded] "`. HEAD has removed the check entirely — fixed but unreleased on 2/edge.

The message never explains why it's degraded or what to do. A single "all" worker provides all
roles but at count 1, versus the recommended 2–3. A message like
`"UI ready at ... (non-HA: add 2+ workers for production)"` would be more useful than a bare
`[degraded]` prefix.

### Worker config missing retention/limits (2/edge only)

`/etc/worker/config.yaml` lacks the `limits` section entirely, and `compactor` lacks
`cleanup_interval`/`deletion_delay` — data cleanup is effectively disabled on this channel.
These are added in HEAD (track 1.18) via `charm_config.py` and
`PyroscopeCoordinatorConfigModel`.

### Process death not detected until next event

Killing the workload process (SIGKILL) causes pebble to restart it immediately (PID changes,
pebble service stays "active"), but the charm never detects the transient failure because no
Juju event fires. The coordinated-workers library's reconcile only runs on events; there is no
periodic health check or watchdog. A genuine crash-loop would go undetected until the next
Juju event triggers a reconcile that observes the failing readiness check.

### Scaling 1→2 workers causes transient instability

Adding a second worker makes the existing worker's pyroscope process see the new node as
"unexpected," failing readiness checks with "Ingester not ready: instance X in state PENDING"
and "no acks received" warnings for ~60s until memberlist stabilizes. Cluster recovers without
intervention.

### No Juju 3.6 vs 4.x differences

Both versions deployed identically, produced the same statuses, and handled failure injections
the same way. Only visible difference: URL format (k8s service FQDN on 3.6 without ingress vs
IP-based with Traefik on 4.x).

### Config reset vs empty string: different behaviour

On Juju 3.6, `--reset cpu_limit` correctly unsets the value (`None`) and the charm stays
active — `is_valid_spec({"cpu": None})` returns True because `parse_quantity(None)` returns
`None`, and `sanitize_resource_spec_dict` deletes `None` entries. But an explicit
`cpu_limit=""` makes `parse_quantity("")` raise `ValueError`, `is_valid_spec` returns False, and
`get_status()` returns `BlockedStatus("Failed obtaining resource limit spec: ...")`. Both
charms block identically on either Juju version. Recovery requires an explicit valid value
(e.g. `cpu_limit=500m`). On Juju 4.x, `--reset` could not be tested due to a client/controller
version mismatch; `cpu_limit=""` produced the same blocked state as on 3.6.

This narrows an earlier suspicion: `--reset` is not the trigger — only an explicit empty
string is, which requires an operator to actively type `cpu_limit=""`.
`sanitize_resource_spec_dict` (`kubernetes_compute_resources_patch.py:136-140`) already handles
empty values by deleting them, but it runs after `is_valid_spec` rejects the empty string.

### Worker removal triggers transient nginx reload error

Removing the worker application fires `certificates-relation-changed` on the coordinator; the
regenerated nginx config (without worker upstreams) causes `nginx -s reload` to fail with exit
code 1 (`ops.pebble.ExecError: non-zero exit code 1 executing ['nginx', '-s', 'reload']`). The
charm goes `error` briefly, then recovers on Juju's automatic hook retry. Transient, but an
operator watching `juju status` would see an error flash.

### COS integration data verified correct

Confirmed by reading relation databags on `rv-pyro-deep`: `metrics-endpoint` published alert
rules (`NginxHighHttp4xxErrorRate` and worker rules); `grafana-dashboard` published
base64-encoded dashboard JSON; `grafana-source` published a `grafana-pyroscope-datasource`
entry with model/application metadata; `catalogue` published an item named
"Pyroscope (pyroscope)" with icon "flame" and the cluster URL.

### Role removal correctly triggers blocked status

Removing a required role (`role-compactor=false`) causes the worker to restart with the new
role set and the coordinator to detect the inconsistency, transitioning to
`blocked [consistency] Cluster inconsistent.` (rv-pyro-deep2). The message does not say which
role is missing. Re-enabling the role recovers the cluster to active (still `[degraded]`)
within ~60s.

### Probes file still references `recommended_deployment`

`probes/cluster-consistency.yaml` (used by juju-doctor) still requires 3 replicas of
querier/ingester/compactor/store-gateway and 2 of query-frontend/query-scheduler/distributor —
the same check removed from the charm code in HEAD. If the internal `is_recommended` check is
dropped from the charm, this probe should be updated to match, or juju-doctor will flag
intentionally small deployments that the charm itself now considers healthy.

## Findings

Ordered by severity.

### 1. Six of eight integration tests skipped — no coverage of COS or profiling

- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/integration/test_self_monitoring.py:50`, `test_profiling.py:7-8`, `test_profiling_tls.py:7-8`, `test_profiling_with_collector.py:7-8`, `test_profiling_with_collector_tls.py:7-8`, `test_retention.py:7-8`
- **Evidence**: All six modules carry `pytestmark = pytest.mark.skip`. Self-monitoring (Prometheus, Loki, Tempo, Grafana, catalogue) is skipped "until we figure out why they're failing in CI" (issue #291). The profiling tests are skipped for profilegen issues (issue #315). Retention is skipped unconditionally. Only `test_ingress.py`, `test_juju_doctor.py`, and `test_scaling_monolithic.py` run.
- **Impact**: The most important integration surface — COS observability — and the charm's core reason to exist — profiling ingestion — have zero automated coverage. Regressions in metrics/logs/traces/dashboards/catalogue or profile ingestion would go uncaught.
- **Fix**: Fix the CI failures behind issue #291 for self-monitoring; fix profilegen or assert on relation-databag contents instead of end-to-end ingestion for profiling; remove the unconditional skip on retention.
- **Linter rule**: mechanically checkable — flag module-level `pytestmark = pytest.mark.skip` in CI.

### 2. `[degraded]` status is permanent, unexplained, and unfixed on the released channel

- **Severity**: medium
- **Kind**: ux
- **Where**: deployed 2/edge coordinated-workers library's `_on_collect_unit_status`; `coordinator/src/charm.py:52-53` (`_default_degraded_message`), `coordinator/src/charm.py:249-256` (`_on_collect_unit_status`) on HEAD
- **Evidence**: On 2/edge, `_on_collect_unit_status` sets `ActiveStatus(self._default_degraded_message)` whenever `is_recommended` is False (requires 3 replicas of most roles, 2 of others). A single all-roles worker never satisfies this, so status permanently reads `[degraded] UI ready at ...`. HEAD has removed the `recommended_deployment`/`is_recommended` check entirely, but the fix is unreleased.
- **Impact**: Operators learn to ignore the `[degraded]` prefix, which trains them to overlook real degradations.
- **Fix**: Release the HEAD fix to 2/edge. If the check is kept, make the message self-explanatory, e.g. `"UI ready at ... (non-HA: add 2+ workers for production)"`.
- **Linter rule**: not mechanically checkable.

### 3. Explicit empty-string config value blocks both charms

- **Severity**: medium
- **Kind**: bug
- **Where**: `coordinator/lib/charms/observability_libs/v0/kubernetes_compute_resources_patch.py:199-205` (`adjust_resource_requirements`); `coordinated_workers/coordinator.py:1067-1080` and `worker.py` call sites
- **Evidence**: `juju config cpu_limit=""` sets an explicit empty string; `is_valid_spec({"cpu": ""})` calls `parse_quantity("")`, which raises `ValueError`, so `is_valid_spec` returns False and both coordinator and worker enter `blocked` with `Invalid limits spec: {'cpu': '', 'memory': None}`. `--reset cpu_limit` (setting to `None`) works correctly and does not block. Verified on Juju 3.6 (rv-pyro-reset) and Juju 4.x (rv-pyro-deep).
- **Impact**: An operator who sets `cpu_limit=""` expecting "no limit" gets a blocked charm instead. `sanitize_resource_spec_dict` already strips empty values but runs after validation rejects them.
- **Fix**: Call `sanitize_resource_spec_dict` before `is_valid_spec`, or treat empty strings as no-limit in `is_valid_spec`.
- **Linter rule**: not mechanically checkable — requires runtime validation of config string parsing.

### 4. Transient nginx reload error on worker removal

- **Severity**: medium
- **Kind**: bug
- **Where**: `coordinated_workers/coordinator.py:486` (nginx reconcile call in `_reconcile`)
- **Evidence**: Removing the worker application triggers `certificates-relation-changed` on the coordinator; the regenerated nginx config causes `nginx -s reload` to fail with exit code 1 (`ops.pebble.ExecError`). Charm enters `error`, then recovers on the next hook retry. Observed in debug-log on `rv-pyro-deep`.
- **Impact**: An operator watching `juju status` sees an error flash during otherwise-normal worker removal.
- **Fix**: Make nginx config generation valid with zero workers (e.g. a `down` backup server per upstream block), or defer the reload until relation removal fully propagates.
- **Linter rule**: not mechanically checkable.

### 5. Process death auto-recovered by pebble, invisible to Juju

- **Severity**: medium
- **Kind**: bug
- **Where**: `coordinated_workers/coordinator.py:450` (`_reconcile`); `coordinated_workers/worker.py:321` (`_reconcile`)
- **Evidence**: SIGKILL on the pyroscope or nginx master process causes pebble to restart it immediately; Juju status stays "active" throughout because no Juju event fires on a pebble state change. Reconciliation is driven by `observe_events`/`all_events`, not pebble check events.
- **Impact**: Fine for transient blips, but a genuine crash-loop would not surface in `juju status` until the next Juju event triggers a reconcile that happens to observe the failing readiness check.
- **Fix**: Observe pebble check events directly, or have `_on_collect_unit_status` check `container.get_service(...).is_running()` rather than relying solely on the next hook.
- **Linter rule**: not mechanically checkable.

### 6. Top-level README offers no deployment guidance

- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md`
- **Evidence**: ~814 bytes; three paragraphs pointing to external discourse links. No deploy instructions, required relations, role configuration, minimum topology, COS integration steps, UI access, or upgrade guidance.
- **Impact**: A new operator has to discover basic deployment steps from discourse, Charmhub, or trial and error.
- **Fix**: Add a quick-start with `juju deploy` commands for a minimal deployment, list required integrations, link to Charmhub/discourse for depth.
- **Linter rule**: not mechanically checkable.

### 7. `Coordinator.__init__` early-return bypassed by charm-level reconcile

- **Severity**: low
- **Kind**: bug
- **Where**: `coordinated_workers/coordinator.py:429-453`; `coordinator/src/charm.py:132`
- **Evidence**: `Coordinator.__init__` returns early without registering its `_reconcile` on `all_events` when the cluster is incoherent. `PyroscopeCoordinatorCharm.__init__` unconditionally registers its own `observe_events(self, all_events, self._reconcile)` regardless, so the charm-level reconcile (ports, ingress, profiling provider, grafana source) always runs even when the library refuses to. Currently harmless because the charm's reconcile checks `is_ready()` before acting on ingress.
- **Impact**: Partially defeats the library's coherence guard; if unsafe operations were ever added to the charm-level reconcile, they'd run during incoherent states.
- **Fix**: Either drop the charm-level `observe_events(all_events, self._reconcile)` and rely on the coordinator's reconcile, or add an explicit coherence check at the top of the charm-level `_reconcile`.
- **Linter rule**: not mechanically checkable.

### 8. No actions defined on either charm

- **Severity**: low
- **Kind**: ux
- **Where**: both charms
- **Evidence**: `juju actions pyroscope` and `juju actions pyroscope-worker` both return "No actions defined."
- **Impact**: Operators have no in-Juju way to run health checks, retrieve diagnostics, check cluster membership, or dump config; they must `juju ssh`/`kubectl exec` instead.
- **Fix**: Add at minimum `health-check` and `show-config` actions; consider `list-members` for cluster topology.
- **Linter rule**: mechanically checkable — flag charms with zero actions.

### 9. "Cluster inconsistent" message doesn't name the missing role

- **Severity**: low
- **Kind**: ux
- **Where**: `coordinated_workers/coordinator.py:905-926` (`_on_collect_unit_status`) and `669-675` (`missing_roles` property)
- **Evidence**: Removing a required role (e.g. `role-compactor=false`) produces
  `blocked [consistency] Cluster inconsistent.` The `missing_roles` property already computes
  the missing set (`set(minimal_deployment).difference(cluster_roles)`) but it is not surfaced
  in the message.
- **Impact**: With 9 distinct roles, an operator needs `juju debug-log` or manual digging to find out which role is missing.
- **Fix**: Include the roles in the message, e.g. `f"[consistency] Cluster inconsistent. Missing roles: {', '.join(sorted(self.missing_roles))}"`.
- **Linter rule**: not mechanically checkable.

### 10. `ProfilingEndpointProvider.publish_endpoint` only catches `ops.ModelError`

- **Severity**: low
- **Kind**: bug
- **Where**: `coordinator/lib/charms/pyroscope_coordinator_k8s/v0/profiling.py:108-112`
- **Evidence**: `publish_endpoint` wraps `relation.save(ProfilingAppDatabagModel(...), self._app)` in `try/except ops.ModelError`. A pydantic `ValidationError` would propagate uncaught. The requirer side (`ProfilingEndpointRequirer.get_endpoints`) catches both `ops.ModelError` and `pydantic.ValidationError`.
- **Impact**: Low likelihood in practice (values are always valid strings), but the asymmetric error handling is a latent bug.
- **Fix**: Add `except pydantic.ValidationError` to the provider side, matching the requirer.
- **Linter rule**: not mechanically checkable.

### 11. Probes file retains `recommended_deployment` check removed from charm code

- **Severity**: low
- **Kind**: test-gap
- **Where**: `probes/cluster-consistency.yaml`
- **Evidence**: The juju-doctor probe requires 3 replicas of querier/ingester/compactor/store-gateway and 2 of query-frontend/query-scheduler/distributor — the same check removed from `_on_collect_unit_status` in HEAD.
- **Impact**: Once the `[degraded]` fix ships, `test_juju_doctor.py` or operator runs of juju-doctor may flag small deployments the charm itself no longer considers degraded.
- **Fix**: Remove `recommended_deployment` from the probe, or mark it advisory-only.
- **Linter rule**: not mechanically checkable.

### 12. Stale typing patterns throughout

- **Severity**: nit
- **Kind**: lint
- **Where**: multiple — `nginx_config.py:6`, `peers.py:7`, `pyroscope.py:7`, `traefik_config.py:19`, `charm.py:170`
- **Evidence**: 49 ruff errors, all style: deprecated `typing.Dict/List/Optional/Tuple/Set` instead of builtins, unsorted imports, unnecessary `# noqa`, shebangs on non-executable files.
- **Impact**: Cosmetic only; no functional effect.
- **Fix**: `ruff check --fix` and commit.
- **Linter rule**: mechanically checkable (UP035, UP006, UP045, I001, EXE001, RUF100, PIE804, SIM103) — rules already exist.

## Worth copying

- **Pydantic-based config generation** (`coordinator/src/pyroscope_config.py`, `coordinator/src/pyroscope.py`): `model_dump(mode="json", by_alias=True, exclude_none=True)` for generating Pyroscope YAML is clean and type-safe; `Field(alias="base-url")` for the one dashed YAML key is elegant.
- **Scenario-based unit testing** (`coordinator/tests/unit/test_config.py`, `worker/tests/unit/test_pebble_plan.py`): `ops.testing.State` rather than Harness — faster, more deterministic. Parametrized config tests cover valid/invalid/default thoroughly.
- **Safety-first config fallback** (`coordinator/src/charm.py:34-38`, `coordinator/src/charm_config.py:76-93`): invalid config disables data deletion rather than passing bad values to Pyroscope, preventing data loss from operator typos.
- **Coordinated-workers pattern usage**: heavy reliance on the library for role management, config distribution, health checks, and status reporting keeps the charm code focused on Pyroscope-specific logic.
- **Clear nginx location mapping** (`coordinator/src/nginx_config.py:24-65`): URL-path-to-role mapping (e.g. `/ingest` → distributor) is well-documented and easy to audit; Traefik config generation handles dual HTTP/gRPC routing with TLS redirect middleware similarly well.
- **`charmcraft.yaml` description quality**: comprehensive, listing features, architecture, and integrations — genuinely useful on Charmhub.
- **Adaptive replication factor** (`coordinator/src/pyroscope.py:79-81`): `replication_factor=3 if len(ingester_addresses) >= 3 else 1` avoids spurious data-loss warnings on small clusters.
- **Worker charm minimalism** (`worker/src/charm.py`): 27 lines total, all logic delegated to `PyroscopeWorker`/`coordinated_workers.worker.Worker`.

## Common-practice notes

- **Follows**: monorepo layout (coordinator/, worker/), each with its own `charmcraft.yaml`, `tox.ini`, `justfile` — standard COS pattern (tempo-, loki-, mimir-operators).
- **Follows**: `pyproject.toml` with uv for dependency management.
- **Follows**: `cosl.reconciler.observe_events` with `all_events` for reconciliation.
- **Drifts**: uses `Coordinator` base class rather than implementing cluster logic directly — newer than many COS charms, intended direction.
- **Drifts**: worker charm is unusually thin (27 lines) — leaner than most COS worker charms, reflects the library's design intent.
- **Missing**: no `charmcraft analyse` results (tool unavailable in review environment); not unusual, most COS charms skip this too.
- **Track gap**: HEAD is track 1.18 (ubuntu@26.04); the only deployable revision on 24.04 controllers is 2/edge. Track 1.18 adds `retention_period`, `deletion_delay`, `cleanup_interval`, pydantic-based config validation, and a newer Pyroscope image, none available on 24.04. 2/edge coordinator rev 75 is from 2026-02-04; worker rev 27 is from 2025-10-06.
- **CI uses Juju 3.6/candidate**: `pull-request.yaml` tests against `juju-channel: 3.6/candidate`, not 4.x; integration tests are enabled only for the coordinator charm.

## Tests

**Unit tests** (re-run): `tox -e unit`. Coordinator: 63 tests, 99% coverage (346 stmts, 3 missed — `charm.py:53`, `charm_config.py:89-90`). Worker: 23 tests, 100% coverage (31 stmts). All pass.

**Static analysis**: `ruff check` reports 49 style errors (deprecated typing imports, unsorted imports, unused noqa, non-executable shebangs), 34 fixable with `--fix`. `pyright` was not available in the review environment.

- Coordinator: 13 test files covering config generation, ingress, nginx config, statuses, catalogue, profiling interface, peers, coherence, and a smoke test.
- Worker: 2 test files — charm statuses (2 tests) and pebble plan generation (21 tests, well-parametrized across roles/config/tracing).
- Uses `ops.testing.State` (scenario framework).
- 1894 warnings (pydantic and LokiPushApiConsumer deprecations), none actionable.

**Interface tests**: present under `coordinator/tests/interface/` and `worker/tests/interface/` (pytest-interface-tester), run via the `interfaces` job in CI — not part of `tox -e unit`.

**Integration tests** (`tests/integration/`, 8 files):

| Test file | Status | Covers |
|---|---|---|
| `test_self_monitoring.py` | skipped | Prometheus metrics, Loki logging, Tempo tracing, Grafana dashboards/source, catalogue, alert rules |
| `test_profiling.py` | skipped (#315) | Profile ingestion via otlp_grpc |
| `test_profiling_tls.py` | skipped (#315) | Profile ingestion with TLS |
| `test_profiling_with_collector.py` | skipped (#315) | Profile ingestion via grafana-agent collector |
| `test_profiling_with_collector_tls.py` | skipped (#315) | Collector-based profiling with TLS |
| `test_retention.py` | skipped | Retention period config and data cleanup |
| `test_ingress.py` | active | Traefik ingress routing |
| `test_juju_doctor.py` | active | juju-doctor health checks |
| `test_scaling_monolithic.py` | active | Deploy, scale up/down, S3 removal |

**Coverage gaps** relative to findings above:
- No test for `_on_collect_unit_status` under invalid config (the `BlockedStatus` path in `charm_config.py`).
- No test for `profiling.publish_endpoint` with TLS-configured ingress.
- No test for peer relation join/leave.
- No test for upgrade-charm/refresh.
- No test for the config-reset → empty-string → blocked recovery path.
- No test for worker scaling / memberlist stabilization.

## Docs

- **Top-level README**: 814 bytes — too thin, no deployment instructions, no quick-start, no architecture diagram; points to external discourse.
- **Coordinator/Worker READMEs**: basic descriptions, ~1400 bytes each.
- **Terraform READMEs**: good — `terraform/README.md` (161 lines) and per-charm TF READMEs (~160 lines) with examples and variable docs.
- **`charmcraft.yaml` description**: excellent — comprehensive feature list, architecture, integrations.
- **CONTRIBUTING.md**: 3343 bytes, standard dev-setup/testing/PR coverage.
- **SECURITY.md**: present (750 bytes), standard Canonical template.
- **No upgrade/migration docs**: nothing on upgrading between Pyroscope versions or charm tracks (open issue #356 discusses the Pyroscope 2.0 migration path).
- **No sizing guide**: open issue #430 confirms missing WAL/storage sizing docs.
- **Doc/reality mismatch**: the deployed 2/edge charm lacks the retention/cleanup options documented in HEAD's `charmcraft.yaml`; an operator reading Charmhub for 2/edge would see features absent from that revision.

## Open questions

1. When will the `[degraded]` fix reach 2/edge? HEAD has removed the check, but 2/edge rev 75 (2026-02-04) still has it.
2. Why are the self-monitoring integration tests failing in CI (issue #291)? The skip reason gives no root cause.
3. What is the migration path to track 1.18 for operators stuck on 24.04 controllers?
4. Are the profiling tests skipped purely for tooling reasons (issue #315), or is the profiling provider path genuinely untested end-to-end?
5. Does seaweedfs actually enforce S3 credentials, or does it accept the observed "placeholder" literals in any configuration? (unverified)
6. Is the charm-level reconcile bypassing the `Coordinator.__init__` coherence guard intentional, or an oversight?
7. Should `probes/cluster-consistency.yaml` be updated in lockstep with the `[degraded]` fix, to avoid juju-doctor flagging deployments the charm no longer considers degraded?
8. How many Kubernetes API calls does the resource-patching code make per config-changed hook (debug-log showed repeated GET/PATCH/GET patterns), and could the dry-run check be cached? (unverified — raised from debug-log observation, not independently measured)
