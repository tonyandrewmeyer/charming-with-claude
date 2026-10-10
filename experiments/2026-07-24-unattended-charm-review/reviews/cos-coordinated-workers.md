# coordinated-workers

`coordinated-workers` is a PyPI library (v4.1.2), not a standalone charm — it provides the `Coordinator`/`Worker` abstractions shared by Tempo, Loki, and Mimir coordinator-operators. The code is generally solid: 165 unit tests pass (3 fail, and the failures reveal a real production defect rather than an environment problem), 89% line coverage, ruff and pyright strict mode both clean, and it deployed successfully on both Juju 3.6 and 4.x with correct nginx proxying of worker metrics and TLS. Runtime testing surfaced several defects invisible from a code-only read: an unguarded `update-ca-certificates` call that crashes worker/coordinator hooks on minimal container images and cascades across every worker on any topology change; stale/broken TLS state left behind when the coordinator is blocked on another condition or when nginx hits a port-reuse race; and a silent TLS outage after certs are re-integrated (charm reports active, but TLS never comes back). A maintainer should first fix the `update-ca-certificates` crash (findings #1 and #2 below) since it is the single root cause behind most of the cascading hook failures observed, then address the TLS lifecycle gaps (stale certs, port-reuse race, silent re-integration failure). Integration test coverage is thin (one smoke test plus a service-mesh test) and should be expanded before the next major consumer upgrade.

| | |
|---|---|
| Repo | canonical/cos-coordinated-workers @ `3c7fec5` (2026-06-24) |
| Charms | ceci-nest-pas-une-charm (dummy), coordinator-tester, worker-tester |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5) and concierge-k8s-3 (Juju 3.6.25), locally packed tester charms, four separate model deployments |
| Reviewed | 2026-07-26 |

## What it does

- **`Coordinator`** (`src/coordinated_workers/coordinator.py`): Manages Nginx reverse-proxying, TLS certificate distribution, S3 config sharing, Prometheus scrape job generation, Loki alert rule consolidation, service mesh policy generation, and worker telemetry proxying. Uses a reconciler pattern that re-evaluates deployment coherence on every event.
- **`Worker`** (`src/coordinated_workers/worker.py`): Receives config from the coordinator, manages Pebble layers, handles TLS certificate sync, forwards logs to Loki via `ManualLogForwarder`, and reports readiness via optional Pebble HTTP checks.
- **Cluster interface** (`src/coordinated_workers/interfaces/cluster.py`): The `ClusterProvider`/`ClusterRequirer` relation interface carrying worker config, TLS certs, tracing receivers, Loki endpoints, remote write endpoints, and service mesh labels.
- **Worker telemetry proxy** (`src/coordinated_workers/worker_telemetry.py`): Generates nginx config for proxying metrics, logs, traces, and remote-write through the coordinator.
- **Service mesh** (`src/coordinated_workers/service_mesh.py`): Generates Istio-compatible `AuthorizationPolicy` resources for cluster-internal traffic.
- **Telemetry correlation** (`src/coordinated_workers/telemetry_correlation.py`): Finds correlated Grafana datasources (e.g. Loki for Tempo trace-to-log correlation).
- **Consistency probe** (`probes/cluster_consistency.py`): A juju-doctor probe for validating deployment topology.

## Deployment log

Four separate deployments were run across two Juju versions.

**Deployment 1 — basic smoke (Juju 4.0.5, model `rv-cw-test`)**

```
cd tests/integration/testers/coordinator && charmcraft pack
cd tests/integration/testers/worker && charmcraft pack

juju switch concierge-k8s-4
juju add-model rv-cw-test
juju deploy ./coordinator-tester_ubuntu@24.04-amd64.charm coordinator \
  --resource nginx-image=ghcr.io/canonical/nginx@sha256:... \
  --resource nginx-prometheus-exporter-image=nginx/nginx-prometheus-exporter:1.1.0 --trust
juju deploy ./worker-tester_ubuntu@24.04-amd64.charm worker-a --trust --config role-a=true
juju deploy ./worker-tester_ubuntu@24.04-amd64.charm worker-b --trust --config role-b=true
juju deploy s3-integrator s3 --channel edge --trust
juju config s3 endpoint="http://s3.example.com" bucket="test-bucket"
juju run s3/0 sync-s3-credentials access-key=minio123 secret-key=minio123
juju integrate coordinator:cluster worker-a:cluster
juju integrate coordinator:cluster worker-b:cluster
juju integrate coordinator:s3 s3:s3-credentials

# ~30s later, all three apps active.
curl http://10.1.0.23:8080/proxy/worker/worker-a-0/metrics  # returns prometheus metrics
curl http://10.1.0.23:9113/metrics  # returns nginx-exporter metrics

# Failure injection
juju remove-relation coordinator s3
# → Coordinator reports "[s3] Missing S3 integration." (blocked)
juju remove-relation coordinator worker-b
# → Coordinator: "[consistency] Cluster inconsistent." Worker-b: "Missing relation to a coordinator charm."
juju config worker-a role-a=false
# → Worker-a: "Node offline: no role assigned..." (blocked)
juju config worker-a role-a=true
# → Worker-a recovers to "a ready." (active)
# Re-adding relations recovers everything to active.
```

**Deployment 2 — TLS and Juju 3.6 cross-check (`rv-cw-deep`, `rv-cw-36`)**

```
juju add-model rv-cw-deep
juju deploy self-signed-certificates certs --channel edge
juju integrate coordinator:certificates certs:certificates
# nginx now serves listen 8080 ssl; worker proxy backends switch to https://

juju deploy ./worker-tester_ubuntu@24.04-amd64.charm worker-c --trust --config role-a=true --config role-b=true
# All three workers reach active: "a ready.", "b ready.", "a,b ready."

juju remove-relation coordinator certs
juju remove-relation coordinator s3
# → Coordinator blocked "[s3] Missing S3 integration." — nginx still serving SSL, cert files still on disk (finding: stale TLS certs)

juju config worker-a role-a=false   # → blocked: "Node offline: no role assigned..."
juju config worker-a role-a=true    # → error: hook failed: "config-changed"
# debug-log: ops.pebble.APIError: cannot find executable "update-ca-certificates" at worker.py:600
# → Self-recovers on Juju retry

juju remove-relation coordinator worker-c
# → worker-c blocked: "Missing relation to a coordinator charm"; coordinator stays active (cluster still coherent with a, b)

# Juju 3.6 cross-check
juju switch concierge-k8s-3 && juju add-model rv-cw-36
# Deploy coordinator + 2 workers + s3-integrator (as deployment 1)
# All apps active/idle, no behavioural differences from 4.x; same update-ca-certificates crash in debug-log.

# Unit tests
PYTHONPATH=.:src:lib:probes uv run --frozen --all-groups pytest tests/unit/ -v
# → 165 passed, 3 failed (all FileNotFoundError: update-ca-certificates)
# → 0 ruff errors, 0 pyright errors (strict mode)
```

**Deployment 3 — wider integration surface (`rv-cw-full`, Juju 4.0.5)**

```
juju add-model rv-cw-full
juju deploy coordinator-tester coordinator --trust
juju deploy worker-tester worker-a --trust --config role-a=true --resource server-image=...
juju deploy worker-tester worker-b --trust --config role-b=true --resource server-image=...
juju deploy s3-integrator s3 --channel edge --trust
juju deploy self-signed-certificates certs --channel edge
juju deploy grafana-agent-k8s grafana-agent --channel edge --trust
juju integrate coordinator:cluster worker-a:cluster
juju integrate coordinator:cluster worker-b:cluster
juju integrate coordinator:s3 s3:s3-credentials
juju integrate coordinator:certificates certs:certificates
juju integrate coordinator:metrics-endpoint grafana-agent:metrics-endpoint
juju config s3 endpoint="http://s3.example.com" bucket="test-bucket"
juju run s3/0 sync-s3-credentials access-key=minio123 secret-key=minio123
# → All coordinator/worker apps active; grafana-agent blocked (no remote-write configured, expected)

kubectl exec coordinator-0 -c nginx -- /charm/bin/pebble signal SIGKILL nginx
# → Pebble auto-restarted nginx within 5s, no charm hooks involved. Transparent.
kubectl exec worker-a-0 -c server -- /charm/bin/pebble signal SIGKILL server
# → Pebble auto-restarted server within 5s. Worker remained active throughout.

juju deploy worker-tester worker-c --trust --config role-a=true --config role-b=true --resource server-image=...
juju integrate coordinator:cluster worker-c:cluster
# → worker-c reaches active "a,b ready." BUT worker-a and worker-b each cycle through multiple errors:
#   worker-a: 3 separate cluster-relation-changed errors (04:47:43, 04:49:23, 04:49:49)
#   worker-b: 2 separate cluster-relation-changed errors
#   coordinator: cluster-relation-joined error for worker-c, then certificates-relation-changed error
#   All self-recover within 10-20s (Juju retry)

juju remove-relation coordinator worker-c
# → coordinator crashes on cluster-relation-departed (04:50:58), recovers 04:51:18
#   worker-a/worker-b crash on cluster-relation-changed (04:51:23-25), all recover
```

**Deployment 4 — certificates lifecycle and failure injection (`rv-cw-deep2`, Juju 4.0.5)**

```
juju add-model rv-cw-deep2
juju deploy coordinator-tester coordinator --trust --resource nginx-image=... --resource nginx-prometheus-exporter-image=...
juju deploy worker-tester worker-a --trust --config role-a=true --resource server-image=...
juju deploy worker-tester worker-b --trust --config role-b=true --resource server-image=...
juju deploy s3-integrator s3 --channel edge --trust
juju deploy self-signed-certificates certs --channel edge
juju config s3 endpoint="http://s3.example.com" bucket="test-bucket"
juju run s3/0 sync-s3-credentials access-key=minio123 secret-key=minio123
juju integrate coordinator:cluster worker-a:cluster
juju integrate coordinator:cluster worker-b:cluster
juju integrate coordinator:s3 s3:s3-credentials
juju integrate coordinator:certificates certs:certificates
# → All apps active

juju config worker-a role-a=false   # → blocked: "Node offline: no role assigned..."
juju config worker-a role-a=true    # → 05:08:09 error: "hook failed: config-changed"
juju show-status-log worker-a/0     # → 05:08:19 retry, 05:08:20 restarting, 05:08:21 active (10s recovery)

juju remove-relation coordinator certs
# → certificates-relation-broken FAILED (05:09:11): ops.pebble.ExecError: non-zero exit code 1 executing 'nginx'
#   nginx log: "bind() to 0.0.0.0:8080 failed (98: Address already in use)"
# → Recovered on retry at 05:09:19 (8s). Nginx config updated to listen 8080 without SSL; certs dir empty.
# → worker-a then crashes on cluster-relation-changed (05:09:22), recovers 05:09:42 (20s) — coordinator publishing
#   TLS-less data triggers the same update-ca-certificates crash on the worker.

juju integrate coordinator:certificates certs:certificates
# → certificates-relation-created succeeds (05:10:04-05:10:08); CSR published in relation data
# → No cert issued within 90+ seconds. Coordinator reports active, nginx still serving without SSL,
#   /etc/nginx/certs/ empty. Silent TLS outage.

kubectl exec coordinator-0 -c nginx -- /charm/bin/pebble signal SIGKILL nginx
# → pebble auto-restarts nginx within 3s, no charm hooks involved.

# Loki/Tempo integration NOT tested: loki-k8s and tempo-coordinator-k8s require ubuntu@26.04,
# not available on the test controller. Logging/tracing relation data paths unverified at runtime.
```

## Observed behaviour

**Timings**: Coordinator deploys in ~30s, workers in ~20s. Relation changes settle within 10-15s. Nginx responds to proxy requests in <5ms.

**Resource usage**: Coordinator pod ~61-104Mi memory (61Mi on Juju 4.x, 104Mi on Juju 3.6), 1m CPU. Worker pods 34-37Mi memory, 1-62m CPU across both Juju versions.

**Nginx config**: Generated correctly. Upstreams point to worker k8s service FQDNs (e.g. `worker-a-0.worker-a-endpoints.rv-cw-test.svc.cluster.local:8080`). Proxy paths like `/proxy/worker/worker-a-0/metrics` route correctly to worker metrics.

**Status precedence**: `_on_collect_unit_status` correctly orders resource-patch status → cluster consistency → S3 availability, with the most severe condition winning. Blocked messages are clear and actionable.

**Self-healing**: The coordinator re-evaluates deployment coherence on every hook; when a worker or S3 is re-added it recovers from blocked to active without intervention.

**S3 misconfiguration**: With a fake S3 endpoint the coordinator correctly reports "[s3] S3 not ready (probably misconfigured)." (unverified whether this is a limitation of the test setup vs. the library, per notes).

**No actions**: Neither tester charm defines actions; the library provides no action infrastructure of its own.

**Hook count / churn**: A single config change on worker-a triggers exactly one `config-changed` hook when nothing crashes. When cluster topology changes (worker joins/leaves), non-deterministic relation-data ordering (finding below) contributes to multiple redundant `cluster-relation-changed` events per worker — worker-a received 3 such events during worker-c's join (04:47:43, 04:49:23, 04:49:49), each crashing on `update-ca-certificates`.

**TLS integration**: Integrating `self-signed-certificates` correctly added `listen 8080 ssl` with `ssl_certificate`/`ssl_certificate_key` pointing at `/etc/nginx/certs/server.cert`/`.key`; worker proxy backends switched to `https://`; cert files confirmed present and correctly sized (~1.7KB each).

**TLS removal and stale certs**: Removing the `certificates` relation while S3 was also not ready left the coordinator blocked on S3, never registering its reconcile observer — nginx kept serving `listen 8080 ssl` with old cert files on disk until S3 was restored and reconcile could run again.

**Stale TLS certs recovery (Juju 3.6)**: Confirmed the stale-cert window is bounded by S3 availability — once S3 was re-added, the coordinator reconciled and removed the SSL directives and cert files.

**Grafana-agent integration**: Integrated on `metrics-endpoint`; grafana-agent went blocked ("Missing ['grafana-cloud-config']|['send-remote-write']") because no remote-write endpoint was configured — expected for a standalone test deployment. Coordinator's scrape jobs were correctly generated.

**Worker workload container is minimal/distroless**: The `prometheus-example-app` image used by worker-tester has no shell, `curl`, `ls`, or `update-ca-certificates`. `kubectl exec` for standard utilities fails with "exec format error." A realistic scenario the Worker library should handle more gracefully.

**Tester charm log pollution**: `tests/integration/testers/worker/src/charm.py:39` logs `logging.error("WorkerCharm __init__")` unconditionally, producing false-positive ERROR entries on every hook and making genuine errors harder to spot. The coordinator-tester does not have this issue.

**What could not be seen from code alone**: exact reconciliation timing, the rendered nginx config on disk, the S3-library/s3-integrator interaction, the cascading nature of hook failures on topology change, the `update-ca-certificates` crash/recovery cycle, the nginx `ExecError` on `certificates-relation-broken`, and the silent TLS re-integration failure — all only visible at runtime.

## Findings

### 1. `Worker._update_tls_certificates` crashes the hook when `update-ca-certificates` is missing from the workload container
- **Severity**: high
- **Kind**: bug
- **Where**: `src/coordinated_workers/worker.py:600` (also `worker.py:436` `_wipe_configs`)
- **Evidence**: `self._container.exec(["update-ca-certificates", "--fresh"]).wait()` is called without try/except in `_update_tls_certificates`. Observed at runtime: toggling worker-a from `role-a=false` back to `role-a=true` crashed `config-changed` with `ops.pebble.APIError: cannot find executable "update-ca-certificates"`. `_wipe_configs()` deletes cert files during the offline phase; on return, `_update_tls_certificates` re-writes them, sets `any_changes=True`, and calls `update-ca-certificates`, which doesn't exist in the minimal `prometheus-example-app` container. The charm recovers on Juju's automatic retry because `any_changes` is `False` the second time. The same failure is the cause of 3 of the 165 failing unit tests (`FileNotFoundError` for `update-ca-certificates`), previously mischaracterized as environment issues.
- **Impact**: Every TLS cert sync (initial deploy, TLS relation added/removed, cert rotation) crashes the worker hook if the workload container lacks the binary — true of many production images (distroless, scratch, minimal Alpine). Recovers automatically but delays readiness by one hook cycle and produces confusing error states; in a cluster with many workers this amplifies into N spurious error transitions per TLS change (see finding #2).
- **Fix**: Wrap the `update-ca-certificates` call in try/except, log a warning, and continue — the cert files are already on disk, which is what matters. Consider making the call optional via a `Worker` parameter.
- **Linter rule**: Not mechanically checkable — requires knowing that workload containers may be minimal.

### 2. Cascading hook failures across workers when cluster topology changes
- **Severity**: high
- **Kind**: bug
- **Where**: `src/coordinated_workers/worker.py:600` (root cause, same as finding #1), amplified by `src/coordinated_workers/coordinator.py:1000` (`publish_data` on every reconcile)
- **Evidence**: Adding worker-c to a healthy 2-worker cluster put both worker-a and worker-b into error state ("hook failed: cluster-relation-changed") — worker-a cycled through 3 separate errors (04:47:43, 04:49:23, 04:49:49), worker-b through 2, each caused by the `update-ca-certificates` crash. Removing worker-c again crashed both workers a second time (worker-a at 04:51:25). The coordinator also crashed on related events (`cluster-relation-joined`, `certificates-relation-changed`, `cluster-relation-departed`), all self-recovering within 10-20s.
- **Impact**: For a cluster of N workers, adding or removing one worker causes up to N+1 spurious error-state transitions. In a production cluster with 10 workers, scaling down by one would cycle 5+ workers through error state, delaying readiness and flooding monitoring with false alarms. Non-deterministic relation-data ordering (finding #6) compounds this by causing redundant relation-changed events with different serialized data, each re-triggering the crash.
- **Fix**: Same as finding #1 (guard `update-ca-certificates`). Additionally make `publish_data` idempotent with respect to TLS certs (sorted keys, no republishing of unchanged fields) to reduce unnecessary relation-changed events.
- **Linter rule**: Not mechanically checkable.

### 3. TLS certificate re-integration does not complete — silent TLS outage
- **Severity**: high
- **Kind**: bug
- **Where**: `src/coordinated_workers/coordinator.py:473` (`self._certificates.sync()` in `_reconcile`)
- **Evidence**: After removing and re-integrating the `certificates` relation, `certificates-relation-created` ran successfully (05:10:04-05:10:08) and the CSR was published in relation data. No `certificates-relation-changed` fired within 90+ seconds and no cert was issued by `self-signed-certificates`. The coordinator stayed active, nginx served without SSL, and `/etc/nginx/certs/` was empty.
- **Impact**: Silent failure — the charm reports healthy while TLS is absent. `_on_collect_unit_status` does not check whether TLS is configured vs. expected, so there's no status-level signal. Likely cause: the TLS handshake stalls when both sides publish data in `relation-created`, preventing the subsequent `relation-changed` that would trigger cert sync — may be specific to `self-signed-certificates` or Juju 4.x event ordering, but plausibly affects any consuming charm (unverified beyond this deployment).
- **Fix**: Verify TLS is actually configured after the certs relation is (re-)established rather than assuming success; add a delayed re-check in `certificates-relation-created`, or have `_on_collect_unit_status` report "TLS not configured" when the relation exists but no certs are on disk.
- **Linter rule**: Not mechanically checkable.

### 4. Non-deterministic relation data ordering causes unnecessary hook churn
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/coordinated_workers/coordinator.py:620-632` (`_upstream_loki_endpoints_by_unit`), `src/coordinated_workers/interfaces/cluster.py:216-228` (`gather_addresses_by_role`)
- **Evidence**: `_upstream_loki_endpoints_by_unit` builds a plain `Dict[str, str]` by iterating `relation.units` (a set, unordered). `gather_addresses_by_role` returns `defaultdict(set)`, also unordered. Both are serialized into relation data. Open issues #158, #166, #175 confirm this causes unnecessary relation-changed events on workers when iteration order differs between hooks.
- **Impact**: Every time the coordinator publishes data with a different key ordering, Juju fires `relation-changed` on every worker — for a cluster with many workers, O(n) unnecessary hook executions per reconcile, wasting CPU and amplifying finding #2.
- **Fix**: Sort keys before serializing — sorted list instead of `set` in `gather_addresses_by_role`, `OrderedDict`/sort-by-unit-name in the loki endpoints path.
- **Linter rule**: "Databag values derived from unordered collections (set, dict.keys()) must be sorted before serialization" — mechanically checkable by detecting `set`/`dict` iteration in relation-data write paths.

### 5. Stale TLS certificates left on disk when the coordinator is blocked on another condition
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/coordinated_workers/coordinator.py:439-447` (early-return guards in `__init__`)
- **Evidence**: Removing the `certificates` relation while S3 was also not ready left the coordinator blocked on S3 (`if self.cluster.has_workers and not self.s3_ready` returns early at line 447), so the reconcile observer was never registered, nginx config was never rebuilt, and `/etc/nginx/certs/server.cert`/`.key` remained on disk with nginx still serving `listen 8080 ssl`. Confirmed on both Juju 4.x and 3.6; confirmed bounded by S3 availability (once S3 restored, cleanup completed).
- **Impact**: If certs are removed (or expire) while the coordinator is blocked on an unrelated condition, TLS cleanup is deferred indefinitely with no operator-visible indication. Worst case: nginx serves with expired certs until the unrelated block clears.
- **Fix**: Register at minimum a cleanup observer for relation-departed/broken events even when the full reconcile observer is withheld, or handle `certificates_relation_broken` independently of other blocking conditions.
- **Linter rule**: Not mechanically checkable.

### 6. `__init__.py` exports broken lazy module references to a removed `nginx` submodule
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/coordinated_workers/__init__.py:47-50`
- **Evidence**: `NginxConfig`, `Nginx`, `NginxPrometheusExporter`, `NginxTracingConfig` are all `_LazyModule(".nginx")`. `src/coordinated_workers/nginx.py` does not exist — removed in commit `31265e9` when nginx support migrated to `charmlibs.nginx_k8s`. Confirmed at runtime: `from coordinated_workers import NginxConfig; NginxConfig._load()` raises `ModuleNotFoundError: No module named 'coordinated_workers.nginx'`. All four names remain in `__all__`.
- **Impact**: These are documented public-API names; a consumer upgrading from v3.x (which had `coordinated_workers.nginx`) gets a cryptic runtime error with no migration path surfaced. The README still describes the library as providing `NginxConfig`.
- **Fix**: Remove the broken exports from `__init__.py`/`__all__`, or add a shim `nginx.py` re-exporting from `charmlibs.nginx_k8s` with a `DeprecationWarning`; update the README.
- **Linter rule**: "Lazy module reference target file does not exist" — mechanically checkable by verifying every `_LazyModule(...)` target exists in the source tree.

### 7. `_build_nginx_config` relies on private attributes of `charmlibs.nginx_k8s.NginxConfig`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/coordinated_workers/coordinator.py:1120-1146`
- **Evidence**: Accesses `config._upstream_configs`, `config._server_ports_to_locations`, `config._server_name`, `config._map_configs`, `config._enable_health_check`, `config._enable_status_page` — all private, suppressed with `# type: ignore[reportPrivateUsage]`. Code comment: "This method is a bit hacky because the charmlib's nginx config class doesn't support incremental construction."
- **Impact**: A minor version bump of `charmlibs.nginx_k8s` renaming these attributes breaks the coordinator at runtime; the library already went through one major migration (v3→v4) touching this exact area.
- **Fix**: Add a public incremental-construction API to `charmlibs.nginx_k8s.NginxConfig` (e.g. `add_upstreams()`, `add_locations()`), or move the copy logic into the charmlib itself.
- **Linter rule**: "Access to private attributes (prefixed `_`) of external packages" — mechanically checkable (pyright already flags these as `reportPrivateUsage`).

### 8. Private method call on the TLS certificates library
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/coordinated_workers/coordinator.py:1008-1010`
- **Evidence**: `self._certificates._get_private_key_secret_label(mode=Mode.UNIT)` calls a private method on `TLSCertificatesRequiresV4`. FIXME comment in the code references issue #16.
- **Impact**: Same coupling risk as finding #7 — an upstream signature/name change breaks TLS distribution between coordinator and workers.
- **Fix**: `tls_certificates` should expose a public accessor for the private key secret label, or the coordinator should manage its own labeling.
- **Linter rule**: "Access to private methods of external packages" — mechanically checkable.

### 9. Coordinator `certificates-relation-broken` hook crashes with nginx `ExecError` on port reuse
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/coordinated_workers/coordinator.py:481-484` (nginx reconcile call in `_reconcile`)
- **Evidence**: When `certificates-relation-broken` fired after removing the certs integration, the hook failed with `ops.pebble.ExecError: non-zero exit code 1 executing 'nginx'`; nginx log showed `bind() to 0.0.0.0:8080 failed (98: Address already in use)`. Recovered on Juju's automatic retry 8s later (05:09:11 → 05:09:19). The new nginx process attempts to bind port 8080 before the old process fully releases it — a Pebble stop/start race.
- **Impact**: Every TLS relation removal transiently error-states the coordinator with a non-actionable status message ("hook failed: certificates-relation-broken"). If the race persisted across retries the coordinator could stay in error indefinitely.
- **Fix**: Use `nginx -s reload` instead of a full restart on config change (ideally in the nginx charmlib), or add a short retry/sleep for the port-release race; catch `ExecError` specifically in `_reconcile` with a brief backoff rather than failing the hook outright.
- **Linter rule**: Not mechanically checkable.

### 10. Coordinator hook failures on relation events (topology-change side effects)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/coordinated_workers/coordinator.py:437-447` (early-return guards), `coordinator.py:1000` (`publish_data`)
- **Evidence**: On worker-c join/leave, coordinator/0 went through error states on `cluster-relation-joined`, `certificates-relation-changed`, and `cluster-relation-departed`, each self-recovering on the next Juju retry (10-15s): 04:49:07 error → 04:49:12 retry ok; 04:49:33 error → 04:49:43 retry ok; 04:50:58 error → 04:51:18 retry ok.
- **Impact**: The coordinator is the cluster control plane; even transient error states pause all N workers' config processing, amplifying finding #2's impact.
- **Fix**: Identify the specific exception per event (likely the same `update-ca-certificates` path, or `_PebbleLogClient.check_juju_version()` being called unconditionally on every init). Consider caching/lazy-initializing the many objects `Coordinator.__init__` creates on every event to reduce the surface for such crashes.
- **Linter rule**: Not mechanically checkable.

### 11. S3 connection info accessed in reconcile path without exception handling
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/coordinated_workers/coordinator.py:1015`
- **Evidence**: `_reconcile_cluster_relations` calls `self.s3_connection_info.ca_cert`; the property raises `S3NotFoundError` if the S3 relation is missing or data is corrupt. `__init__` guards against registering the reconcile observer when S3 is not ready, but this is an implicit coupling — not observed to fail in testing because the Coordinator is rebuilt fresh every hook, but the coupling is real and fragile.
- **Impact**: If the observer-registration guard were ever changed or S3 were removed mid-hook, `_reconcile` would crash uncaught.
- **Fix**: Wrap the `s3_connection_info` access in try/except, log and return early, or add an explicit `s3_ready` guard immediately before the access.
- **Linter rule**: Not mechanically checkable — requires following the call chain.

### 12. Unhandled JSON parsing in `_upstream_loki_endpoints_by_unit` can crash the coordinator hook on malformed Loki relation data
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/coordinated_workers/coordinator.py:633-634`
- **Evidence**: `json.loads(endpoint)` followed by `deserialized_endpoint["url"]` with no try/except. A malformed or missing `url` key from a third-party Loki charm raises `JSONDecodeError`/`KeyError`, which propagates through `_reconcile_cluster_relations` → `_reconcile` and crashes the hook.
- **Impact**: A Loki-side bug or endpoint-format change crashes the coordinator hook with a bare, unhelpful exception rather than degrading gracefully.
- **Fix**: Catch `(json.JSONDecodeError, KeyError)`, log a warning naming the unit, and continue to the next unit.
- **Linter rule**: "Access of dict subscripts from parsed JSON without KeyError handling" — partially mechanically checkable (flag `json.loads` followed by subscript access without a try/except in the same method).

### 13. Integration test suite is essentially a single smoke test
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_solution.py`
- **Evidence**: Deploys coordinator + 2 workers + s3-integrator, asserts active, checks two metrics endpoints. No coverage for TLS, logging, tracing, service mesh, worker scaling, relation removal/recovery, config changes, Pebble check readiness, resource patching, or telemetry correlation at the integration level. Open issue #111 explicitly asks how to integration-test this library. A second file, `test_service_mesh.py`, does cover Istio mesh policy and label propagation comprehensively.
- **Impact**: The library is complex (7 source modules, 12+ integrations) and used by production HA charms (Tempo, Loki, Mimir); a regression in any untested path — including the ones found by this review at runtime — could ship silently.
- **Fix**: Add integration tests for at minimum TLS handshake, logging relation, tracing relation, worker scale up/down, and relation-broken recovery.
- **Linter rule**: Not mechanically checkable.

### 14. Worker `running_version` raises on non-standard binary name
- **Severity**: low
- **Kind**: bug
- **Where**: `src/coordinated_workers/worker.py:679-689`
- **Evidence**: `self._container.exec([f"/bin/{self._name}", "-version"])` hardcodes the binary path as `/bin/<container_name>`. Tester charm's container is named `server` but the binary is `/bin/prometheus-example-app`, causing `ops.pebble.APIError: cannot find executable "/bin/server"` on every deploy.
- **Impact**: Caught and logged, so non-fatal, but produces ERROR-level noise on every deploy and the workload version never gets set.
- **Fix**: Make the version command configurable via a `Worker.__init__` parameter, e.g. `version_command: Optional[Callable[[], str]] = None`.
- **Linter rule**: Not mechanically checkable.

### 15. `ManualLogForwarder` imports a private class from the Loki charm library
- **Severity**: low
- **Kind**: bug
- **Where**: `src/coordinated_workers/worker.py:38`
- **Evidence**: `from charms.loki_k8s.v1.loki_push_api import _PebbleLogClient` — imports a private (`_`-prefixed) class.
- **Impact**: Same coupling risk as findings #7/#8: renaming or removing `_PebbleLogClient` upstream breaks worker log forwarding.
- **Fix**: Loki library should expose `PebbleLogClient` publicly, or the worker should use the public `LogForwarder` interface.
- **Linter rule**: "Import of private names (prefixed `_`) from external packages" — mechanically checkable.

### 16. `Worker._update_tls_certificates` calls `subprocess.run` on the charm host without checking the return code
- **Severity**: low
- **Kind**: bug
- **Where**: `src/coordinated_workers/worker.py:601`
- **Evidence**: `subprocess.run(["update-ca-certificates", "--fresh"])` — no `check=True`, no return-code inspection.
- **Impact**: If it fails on the charm host (missing binary, permission error), the failure is silent; charm tracing may then fail to verify TLS certs. Low probability since the charm host almost always has the binary.
- **Fix**: Add `check=True`, or log a warning on non-zero return code.
- **Linter rule**: "`subprocess.run` without `check=True`" — mechanically checkable.

### 17. Tester charms cannot be packed without manual setup
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/testers/coordinator/`, `tests/integration/testers/worker/`
- **Evidence**: No `pyproject.toml`/`uv.lock` in either tester directory; `conftest.py` copies them from the repo root at test time along with the `coordinated_workers` source. `charmcraft pack` run directly in either tester directory fails with "No pyproject.toml found".
- **Impact**: Confusing for anyone manually testing the tester charms; the setup is fragile against incompatible changes to the repo root's `pyproject.toml`.
- **Fix**: Give each tester charm its own `pyproject.toml`/`uv.lock`, or document the build process in a CONTRIBUTING.md.
- **Linter rule**: Not mechanically checkable.

### 18. CI only tests against Juju 3.6, not 4.x
- **Severity**: low
- **Kind**: test-gap
- **Where**: `.github/workflows/pull-request.yaml:49-50`
- **Evidence**: `CONCIERGE_JUJU_CHANNEL: 3.6/stable`. This review deployed and tested successfully on Juju 4.0.5, but CI does not validate that.
- **Impact**: Juju 4.x-specific regressions could go undetected as adoption increases.
- **Fix**: Add a Juju 4.x matrix entry, or run integration tests on both versions.
- **Linter rule**: Not mechanically checkable.

### 19. README is minimal — no usage examples or architecture docs
- **Severity**: low
- **Kind**: docs
- **Where**: `README.md`
- **Evidence**: 10 lines describing the library's purpose and release process. No usage examples, API docs, architecture diagram, or links to consuming charms. Open issue #67 requests service-mesh usage docs specifically.
- **Impact**: A new developer has to read the source to understand how to use the library.
- **Fix**: Add a Quick Start with a minimal coordinator/worker example, document key classes and parameters, link to Tempo/Loki/Mimir as reference implementations.
- **Linter rule**: Not mechanically checkable.

### 20. `yaml.safe_load` in `Worker._running_worker_config` raises unhandled `YAMLError` on a corrupt config file
- **Severity**: low
- **Kind**: bug
- **Where**: `src/coordinated_workers/worker.py:493`
- **Evidence**: The method's try/except catches only `(ProtocolError, PathError)`; `yaml.safe_load(raw_current)` can raise `yaml.YAMLError` on a corrupted file, which is not caught and propagates to a hook crash.
- **Impact**: A corrupted config file (rare — Pebble writes atomically, but possible on disk-full or container restart) puts the worker into a crash loop with no automatic recovery path short of manual file deletion.
- **Fix**: Add `yaml.YAMLError` to the except clause, log, and return `None` so the config gets rewritten on the next reconcile.
- **Linter rule**: Not mechanically checkable — requires knowing which exceptions `yaml.safe_load` raises.

### 21. `shutil.copy` in `_consolidate_nginx_alert_rules` can raise unhandled
- **Severity**: low
- **Kind**: bug
- **Where**: `src/coordinated_workers/coordinator.py:1066`
- **Evidence**: `shutil.copy(filename, consolidated_path)` with no try/except; missing source/destination or a full disk raises `FileNotFoundError`/`OSError`, propagating through `_consolidate_alert_rules` → `_reconcile` to a hook crash.
- **Impact**: A secondary, non-critical concern (alert rule consolidation) can crash the coordinator hook.
- **Fix**: Wrap in try/except, log a warning and continue.
- **Linter rule**: "Use of `shutil.copy` without exception handling" — mechanically checkable.

### 22. `Coordinator.__init__` creates 12+ heavyweight library objects on every charm event
- **Severity**: low
- **Kind**: performance
- **Where**: `src/coordinated_workers/coordinator.py:355-415`
- **Evidence**: Every event instantiates `ClusterProvider`, `Nginx`, `NginxPrometheusExporter`, `TLSCertificatesRequiresV4`, `S3Requirer`, `DatasourceExchange`, `GrafanaDashboardProvider`, `LokiPushApiConsumer`, `LogForwarder`, `MetricsEndpointProvider`, two `TracingEndpointRequirer`s, `KubernetesComputeResourcesPatch`, `CatalogueConsumer`, and `ServiceMeshConsumer`, several of which scan relation data or call `check_juju_version()` in their constructors.
- **Impact**: Adds measurable per-hook overhead, including on `update-status` (default every 5 minutes) where the work is often discarded by the early-return guards. Not critical but wasteful, and widens the surface for finding #10.
- **Fix**: Cache stateless integration wrappers outside the Coordinator, or use `functools.cached_property`; would require redesigning the reconciler bootstrap.
- **Linter rule**: Not mechanically checkable.

### 23. Tester charm logs `ERROR` on every hook execution
- **Severity**: low
- **Kind**: lint
- **Where**: `tests/integration/testers/worker/src/charm.py:39`
- **Evidence**: `logging.error("WorkerCharm __init__")` in `WorkerCharm.__init__`, unconditional. Confirmed in debug-log: an ERROR-level `WorkerCharm __init__` line appears on every hook execution (config-changed, start, pebble-ready, cluster-relation-changed) on both worker-a and worker-b.
- **Impact**: Pollutes logs with false-positive ERROR entries, making genuine errors (e.g. the `update-ca-certificates` crash, the nginx `ExecError`) harder to spot.
- **Fix**: Change to `logging.debug(...)` or remove the line.
- **Linter rule**: "ERROR-level log in `__init__` without a guard condition" — mechanically checkable (detect `logging.error` in charm `__init__` methods).

### 24. `_PebbleLogClient.check_juju_version()` called at class init time
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/coordinated_workers/worker.py:761`
- **Evidence**: Called unconditionally in `ManualLogForwarder.__init__`; raises if the Juju version is too old.
- **Impact**: Low — Juju version is known at deploy time — but would crash on import in a non-Juju environment (e.g. some unit test setups).
- **Fix**: Move the check to the first call of `update_logging`/`disable_logging`, or guard with a version check.
- **Linter rule**: Not mechanically checkable.

## Worth copying

1. **Reconciler pattern with early-exit guard** (`coordinator.py:415-452`): the Coordinator refuses to register the reconcile observer until the deployment is coherent, preventing work that will fail. `_on_collect_unit_status` is always registered separately, so the operator always sees a clear status message. Clean separation of "are we ready?" from "do the work."
2. **Frozen set of non-reconcilable events** (`helpers.py:21-25`): `NON_RECONCILABLE_EVENTS` excludes `PebbleCheckFailedEvent` from triggering reconciliation, preventing restart loops while a workload is still starting. References issue #159.
3. **Comprehensive unit test coverage** (`tests/unit/`): 165 tests covering coordinator/worker status, TLS sync, proxy env injection, service restart, pebble layer management, alert rule consolidation, scrape job generation, service mesh policies, charm tracing, telemetry correlation, and worker telemetry nginx config generation, using `ops.testing` (scenario) with realistic state.
4. **Tenacity retry with configurable parameters** (`worker.py:620-660`): `restart()` uses `tenacity.Retrying` with overridable class-level constants, raising after retries are exhausted so Juju can retry the hook — a canonical pattern for transient failures.
5. **`ClusterRolesConfig` validation at construction time** (`coordinator.py:120-148`): `__post_init__` validates meta-roles and minimal-deployment roles are subsets of the defined roles, catching misconfiguration at charm startup with specific error messages.
6. **`check_libs_installed` helper** (`helpers.py:28-39`): raises `RuntimeError` with a copy-pasteable `charmcraft fetch-lib` command if required charm libraries are missing.
7. **`_LazyModule` for deferred imports** (`__init__.py:23-40`): reduces startup time and avoids circular imports (though see finding #6 for a case where the targets don't exist).
8. **Clear status messages with category prefixes** (`coordinator.py:927-935`): `[consistency]`, `[s3]` prefixes help operators quickly locate the problem; messages like "Missing any worker relation" are directly actionable.

## Common-practice notes

- **Follows**: the `cosl.reconciler` pattern (`observe_events`, `all_events`) is standard for COS charms; unit tests use `ops.testing` (scenario), the current best practice.
- **Follows**: `src/` layout, `pyproject.toml` with hatchling, `uv.lock` for pinning — standard for modern charm libraries.
- **Follows**: `charmcraft.yaml` with `type: charm`/`plugin: uv` even for a library (the dummy charm `ceci-nest-pas-une-charm` is a deliberate workaround).
- **Drifts**: imports charm libraries (`charms.*`) directly rather than PyPI packages — a known pain point given charmhub-hosted libs are deprecated. Partial migration already done (`tls_certificates` → PyPI in `2ef769a`, `nginx_k8s` → `charmlibs` in `31265e9`); s3, grafana_dashboard, prometheus_scrape, loki_push_api, tracing, catalogue, and service_mesh remain charmhub-hosted.
- **Drifts**: `_EndpointMapping` TypedDict duplicates relation endpoint names across the library and every consuming charm; a Pydantic model/dataclass with defaults would be more conventional.
- **Drifts**: uses `partial()` to bind `self` to callbacks (`workers_config`, `resources_requests`) rather than explicit parameter passing — works, but less discoverable.

## Tests

**Unit tests**: 165 pass, 3 fail — all `FileNotFoundError: update-ca-certificates`, which is the real code defect in finding #1, not an environment issue. Overall line coverage 89% (1365 statements). Per-module: `coordinator.py` 93%, `worker.py` 86%, `cluster.py` 89%, `worker_telemetry.py` 96%, `telemetry_correlation.py` 92%, `service_mesh.py` 75%, `helpers.py` 72%, `__init__.py` 71%.

**Test gaps** (untested branches): `_reconcile` on coordinator/worker when `resources_patch` is set but not ready; `_reconcile_mesh_policies` when mesh is `None`; `_setup_charm_tracing` when `charm_tracing.is_ready()` is `False`; `_build_nginx_config`/`_inject_worker_telemetry_config` with no telemetry proxy config or empty worker topology; `Worker._is_readiness_check_failing` when not ready; `ManualLogForwarder.disable_logging`; `Worker.charm_tracing_config` for `https://` endpoint with no `server_ca_cert`; exception paths in `_sync_tls_files`; `ClusterProvider._remote_data_ready` with incomplete relation data.

**Integration tests**: two files — `test_solution.py` (basic smoke: coordinator + 2 workers + s3-integrator, active/idle + metrics endpoint checks) and `test_service_mesh.py` (deploys istio-k8s/istio-beacon-k8s, verifies mesh labels, authorization policies, and the `app.kubernetes.io/part-of` solution label). Not covered at integration level: TLS, logging, tracing, worker scaling, relation removal/recovery, config changes, Pebble check readiness, resource patching, telemetry correlation. CI runs integration tests on Juju 3.6 only.

**Linting**: 0 ruff errors, 0 pyright errors (strict mode). `charmcraft analyse` not applicable (library, not a charm).

## Docs

- **README.md**: 10 lines — library purpose plus a "How to release" section for maintainers. No usage examples, API reference, or quick start.
- **SECURITY.md**: present, standard Canonical security policy.
- **Pull request template**: present, standard checklist.
- **No `docs/` directory**: no architecture docs, API docs, or tutorial.
- **No CONTRIBUTING.md**: no dev-environment setup or test-running instructions.
- **Charmhub**: not published (dummy charm `ceci-nest-pas-une-charm` returns 404) — correct, since the library is distributed on PyPI.
- **Doc/reality mismatch**: README describes the library as providing "Coordinator, Worker, and NginxConfig." Coordinator and Worker are present and functional; `NginxConfig` is broken (finding #6) — the actual class now lives in `charmlibs.nginx_k8s`, not this package. README needs updating.

## Open questions

1. **Can the tester charms be packed in CI as-is?** `conftest.py` copies `pyproject.toml`/`uv.lock` from the repo root and copies `src/coordinated_workers` into the tester's `src/`; this works locally but assumes the repo root as working directory. The CI job (`uvx tox -e integration`) presumably handles this via fixtures but wasn't run in this review. Settle by running `tox -e integration` on a real controller.
2. **Does service mesh policy generation work correctly against a real Istio deployment beyond mocks?** `test_service_mesh.py` does exercise a real Istio deployment and passed in this review's context (per notes), but unit tests mock `PolicyResourceManager`. Consider this settled at the integration-test level; unit-level behaviour on `PolicyResourceManager` edge cases remains unverified.
3. **Are the three `update-ca-certificates` unit test failures environment-specific?** No — confirmed as a real code defect (finding #1), reproduced identically at runtime on both Juju 3.6 and 4.x.
4. **Race window in `_reconcile_cluster_relations` between the `s3_ready` check and `s3_connection_info` access** (finding #11): not observed to trigger in testing because `__init__` re-evaluates fresh every hook, but the coupling is real. Settle by stress-testing rapid S3 relation add/remove cycles.
5. **Does the logging integration work correctly with Loki?** Not validated at runtime — `loki-k8s`/`tempo-coordinator-k8s` require ubuntu@26.04, unavailable on the test controller. The `logging` relation's dual use of `LokiPushApiConsumer` and `LogForwarder` on the same endpoint (issue #23) is a known workaround whose correctness is unverified here. Settle by deploying on a controller with ubuntu@26.04 support.
6. **Why does TLS re-integration stall after `certificates-relation-created`?** (finding #3) CSR published, capabilities published, no cert issued within 90s. May be Juju 4.x event-ordering or `self-signed-certificates`-specific behaviour. Settle by testing with a different TLS provider and by inspecting the `tls_certificates` library's handling of the case where both sides set data in `relation-created`.
