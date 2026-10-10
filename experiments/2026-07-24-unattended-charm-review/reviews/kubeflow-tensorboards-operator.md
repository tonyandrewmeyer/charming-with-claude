# kubeflow-tensorboards-operator

Repository containing two charms: **tensorboard-controller** (wraps the upstream `tensorboard-controller` Kubernetes operator as a Pebble workload, provides `metrics-endpoint`, supports sidecar and ambient-mesh gateway modes) and **tensorboards-web-app** (serves the TensorBoards web UI via gunicorn, integrates with Istio ingress and the Kubeflow dashboard). Both follow the modern ops sidecar pattern and use `charmed-kubeflow-chisme` for common patterns; code quality is generally good (clean status precedence, DRY reconciler pattern, reasonably covered unit tests). However, live deployment testing surfaced four critical/high-severity operational bugs that are currently invisible to the unit staying `active`: a broken health check on tensorboards-web-app that kills gunicorn workers every ~90s, a missing `relation-broken` handler on both charms that leaves stale config in place and can cascade into failing a related charm (`istio-pilot`), a `metrics-endpoint` service patch that silently fails on tensorboard-controller due to a string/int port bug, and a `tensorboard-image` config option that gives the illusion of changing the workload image but only sets an env var. A maintainer should fix the `METRICS_PORT` string bug and the missing `relation-broken` observers first — both are one-line-per-event changes with outsized blast radius — then address the web-app health check.

| | |
|---|---|
| Repo | canonical/kubeflow-tensorboards-operator @ `0cad154` (2026-06-22) |
| Charms | tensorboard-controller (rev 715 on 1.11/edge), tensorboards-web-app (rev 700 on 1.11/edge) |
| Substrate | k8s |
| Deployed | yes — `concierge-k8s-4`, channel 1.11/edge (rev 715/700), alongside istio-pilot rev 1552 |
| Reviewed | 2026-08-22 |

## What it does

`tensorboard-controller` deploys the upstream `tensorboard-controller` manager binary as a Pebble service, managing ClusterRoles/ClusterRoleBindings and CRDs via `KubernetesResourceHandler` from chisme. It requires a gateway relation (`gateway-info` for sidecar Istio, or `gateway-metadata` for ambient mesh) and an optional `service-mesh` relation. It provides `metrics-endpoint` (prometheus_scrape) and `provide-cmr-mesh`. Config: `tensorboard-image` (sets `TENSORBOARD_IMAGE` env var only, see Finding below) and `leader-election` (defined but never read).

`tensorboards-web-app` serves the web UI on port 5000 via gunicorn. It requires `istio-ingress-route` (ambient) or `ingress` (sidecar) — mutually exclusive. It provides `provide-cmr-mesh` and registers a sidebar link via `kubeflow-dashboard-links`. Config: `secure-cookies`, `backend-mode`.

## Deployment log

1. Created model `rv-tensorboards` on `concierge-k8s-4` (Juju 4.0.12, Kubernetes).
2. Deployed `tensorboard-controller` from `1.11/edge` (rev 715) and `tensorboards-web-app` from `1.11/edge` (rev 700), both `--trust`.
3. Both charms went `blocked` (expected — no gateway/ingress relations).
4. Deployed `istio-pilot` from `latest/edge` (rev 1552) — active after ~25s.
5. Related `tensorboard-controller:gateway-info → istio-pilot:gateway-info` — went `active` immediately.
6. Related `tensorboards-web-app:ingress → istio-pilot:ingress` — went `active` immediately.
7. `kubectl top pod`: tensorboard-controller 2m CPU / 59Mi RAM; tensorboards-web-app 2m CPU / 347Mi RAM.
8. `pebble checks`: tensorboard-controller health check **up** (17/17, threshold 4). tensorboards-web-app health check **down** (0/17 successes, 17 failures, threshold 3) — see Finding 1.
9. Related `tensorboard-controller:metrics-endpoint → grafana-agent-k8s:metrics-endpoint` — relation created; grafana-agent-k8s went `blocked`: `Missing ['grafana-cloud-config']|['send-remote-write'] for metrics-endpoint` — see Finding "grafana-agent-k8s blocked status".
10. `juju remove-relation tensorboard-controller:gateway-info istio-pilot:gateway-info` — `gateway-info-relation-broken` fired but unhandled; unit stayed `ActiveStatus`; pebble layer kept stale `ISTIO_GATEWAY=rv-tensorboards/istio-gateway` — see Finding 2.
11. Same test removing `ingress` on tensorboards-web-app: `ingress-relation-broken` fired on `istio-pilot` (which had no observer for it), putting `istio-pilot` into `error`: `hook "ingress-relation-broken" ... failed: exit status 1`. See Finding 2.
12. Workload kill test: `kubectl exec ... kill <PID>` on both charms' processes. Pebble's `startup: enabled` restarted both within ~3s; no status change.
13. Scale-up: `juju scale-application tensorboard-controller 2`. Second unit's pebble layer set, service `inactive` (correct — leadership-gated). Pod stayed `1/2` Ready. Scale-down confirmed.
14. Invalid image config: `juju config tensorboard-controller tensorboard-image=invalidregistry.io/nonexistent:v999`. Status stayed `active`; pebble layer env var updated; K8s container image unchanged — see "`tensorboard-image` config" finding.
15. `juju refresh` attempted — no newer revision available on `1.11/edge`.
16. `juju remove-application tensorboards-web-app`: pod entered `Completed`; ClusterRole/ClusterRoleBinding deleted correctly by `_on_remove`; CRD `tensorboards.tensorboard.kubeflow.org` correctly retained (owned by tensorboard-controller). tensorboard-controller then moved to `WaitingStatus("Waiting for gateway info relation data")` only after a subsequent `config-changed` hook — confirming the stale-state window from the missing `relation-broken` handler.
17. Re-established gateway relation to restore tensorboard-controller to `active`; `istio-pilot` remained in `error` (pre-existing/third-party issue, not scored here).
18. Confirmed Juju rejects invalid config values (`leader-election=invalid`, `secure-cookies=xyz123`) before the charm sees them — no charm-level validation gap.
19. Deployed `kubeflow-dashboard` (`1.10/stable`, rev 948). `juju relate tensorboards-web-app:dashboard-links kubeflow-dashboard:dashboard-links` failed (`relation endpoint not found`); `juju relate tensorboards-web-app:dashboard-links kubeflow-dashboard:links` succeeded — see "`dashboard-links` endpoint mismatch" finding.
20. Deployed `loki-k8s` (`3.7/stable`, rev 244). Related `logging` for both charms successfully; both stayed `active`. Transient `WebSocketConnectionClosedException` on loki-k8s (self-recovering, not a charm bug).
21. Deployed `grafana-agent-k8s` (`0.40/stable`, rev 233); related `metrics-endpoint` — grafana-agent-k8s `blocked` as in step 9; tensorboard-controller stayed `active`.
22. Scale-up `tensorboards-web-app` to 2: non-leader unit-1 pebble layer set, service `inactive` (leadership-gated); both pods `2/2 Running`. Scale-down confirmed.
23. Re-confirmed the web-app pebble check failure via `ps aux`: gunicorn `START` time `09:02` vs. container `START` `08:59` — a ~3 minute gap proving Pebble restarted gunicorn mid-container-life. K8s container restart count stayed 0 throughout.
24. Inspected `tensorboard-controller` K8s Service: `port: 65535`, `targetPort: 65535` (Juju placeholder), no prometheus scrape annotations — the metrics service patch never applied. Root-caused to `METRICS_PORT = "8080"` being a string — see Finding 4 (matches GitHub issue #261, filed 2026-08-12).

## Observed behaviour

### tensorboard-controller
- Pebble service `tensorboard-controller` — `active`, command `/manager`.
- Health check: HTTP GET `http://localhost:8081/healthz` — **passing** (timeout=20s, period=30s, threshold=4).
- `EXPERIMENTAL_USE_GATEWAY_API: "false"` correctly set for sidecar mode (no `service-mesh` relation).
- ClusterRole/ClusterRoleBinding/CRD applied correctly on install.
- Install-to-active: ~2 minutes.
- After gateway relation removal: pebble layer not re-applied, stays `ActiveStatus` initially, env vars stale; only moves to `WaitingStatus("Waiting for gateway info relation data")` after a subsequent `config-changed`, and even then the pebble layer stays stale.
- After workload kill: automatic restart within ~3s, graceful shutdown logged.
- Non-leader unit (scale=2): pebble layer applied, service `inactive` (correct), pod `1/2` Ready since the container's own readiness is tied to the (intentionally not started) manager process.
- Metrics service: K8s Service stuck at placeholder port 65535, no prometheus annotations — see Finding 4.

### tensorboards-web-app
- Pebble service `tensorboards-web-app` — `active`, command `gunicorn -w 3 --bind 0.0.0.0:5000`.
- Health check: HTTP GET `http://localhost:5000` — **failing with 401 Unauthorized**, always (no `kubeflow-userid` header sent by the check).
- Pebble log: `HTTP Exception handled: 401 Unauthorized: No user detected. GET / HTTP/1.1`, repeated.
- Correct relation data sent to istio-pilot: `{port: 5000, prefix: /tensorboards, rewrite: /, service: tensorboards-web-app}`.
- Install-to-active: ~2m30s.
- After ingress relation removal: same missing-handler bug as tensorboard-controller; also puts `istio-pilot` into `error` (cascading failure, see Finding 2).
- After workload kill: recovered within ~3s.
- After `remove-application`: pod → `Completed`; K8s resources cleaned up correctly.

### tensorboards-web-app Pebble check — gunicorn is restarted, not the container
The pebble layer has `"on-check-failure": {"tensorboards-web-app-up": "restart"}`, so a failing check restarts the **gunicorn process**, not the container. `ps aux` shows gunicorn `START` `09:02` against container `START` `08:59`; K8s container `restartCount` stayed `0` throughout. The check had accumulated 8 failures (threshold 3) and was `down`. Every ~90s (3×30s period), all in-flight requests to the 3 gunicorn workers are killed and replaced — invisible to standard container-restart monitoring.

### Relation-removal hook trace (tensorboard-controller)
```
unit-tensorboard-controller-0: ran "gateway-info-relation-departed"
unit-tensorboard-controller-0: ran "gateway-info-relation-broken"
unit-tensorboard-controller-0: juju.worker.uniter.relation unknown relation 1 resolving next op
```
Both hooks fired with no observer registered; unit stayed `ActiveStatus`.

### Relation-removal cascade (tensorboards-web-app → istio-pilot)
```
unit-istio-pilot-0: ERROR juju.worker.uniter.operation hook "ingress-relation-broken" (via hook dispatching script: dispatch) failed: exit status 1
unit-istio-pilot-0: INFO juju.worker.uniter awaiting error resolution for "relation-broken" hook
unit-tensorboards-web-app-0: WARNING juju.worker.uniter.operation we should run a leader-deposed hook here, but we can't yet
unit-tensorboards-web-app-0: INFO juju.worker.uniter.relation unknown relation 2 resolving next op
unit-tensorboards-web-app-0: ERROR juju.worker.uniter resolver loop error: preparing operation "run stop hook" for tensorboards-web-app/0: getting context for unit "tensorboards-web-app/0": unit is dead
```

### tensorboard-controller K8s Service port
- `kubectl get svc tensorboard-controller` → `port: 65535`, `targetPort: 65535` (Juju placeholder), no prometheus scrape annotations expected from `MetricsEndpointProvider`.
- `KubernetesServicePatch._patch` swallows the `ApiError` after logging (no re-raise) — the unit shows `active` with the patch silently failed.
- Reproduced: `ServicePort(port="8080", targetPort="8080")` stores `str` values via lightkube; tensorboards-web-app's equivalent (`PORT = 5000`, an `int`) patches correctly.

### Resource usage (`kubectl top pod`)
| Pod | CPU | Memory |
|---|---|---|
| tensorboard-controller-0 | 2m | 59Mi |
| tensorboards-web-app-0 | 2m | 347Mi |
| istio-pilot-0 | 58m | 47Mi |
| grafana-agent-k8s-0 | 0m | 29Mi |

### Additional integrations exercised
- **kubeflow-dashboard**: `dashboard-links` relation works once the correct provider endpoint (`links`) is used; `KubeflowDashboardLinksRequirer` auto-registers for `leader_elected`/`relation_created`/`upgrade_charm` and correctly sends `{text: TensorBoards, link: /tensorboards/}`.
- **loki-k8s**: `logging` relation on both charms succeeds without error; transient, self-recovering `WebSocketConnectionClosedException` on loki-k8s side only.
- **grafana-agent-k8s**: `metrics-endpoint` relation succeeds; grafana-agent-k8s goes `blocked` because it additionally needs `grafana-cloud-config` or `send-remote-write` — expected behaviour, not a tensorboard-controller bug.
- **Pod deletion**: `kubectl delete pod tensorboard-controller-0 --grace-period=0` — Juju recreated the pod, unit went `maintenance` for ~2 minutes while the pebble layer was reapplied, then returned to `active` automatically. No operator action required.

## Findings

### 1. `METRICS_PORT = "8080"` is a string — service patch silently fails, metrics port stuck at 65535
- **Severity**: critical
- **Kind**: bug
- **Where**: `charms/tensorboard-controller/src/charm.py` (`METRICS_PORT = "8080"` constant; `ServicePort(port=METRICS_PORT, targetPort=METRICS_PORT, ...)`)
- **Evidence**: `kubectl get svc tensorboard-controller` shows `port: 65535`/`targetPort: 65535` (Juju placeholder), no prometheus scrape annotations. `KubernetesServicePatch._patch` logs the `ApiError` but does not re-raise, so the unit stays `active`. Reproduced: `ServicePort(port="8080", targetPort="8080")` stores `str`; the K8s API patch is rejected/ignored. Compare tensorboards-web-app's correctly-typed `PORT = 5000` (int), which patches successfully. Matches open GitHub issue #261 (filed 2026-08-12).
- **Impact**: The `metrics-endpoint` (prometheus_scrape) relation is created but Prometheus cannot actually scrape tensorboard-controller, because the Service is stuck on the placeholder port with no scrape annotations — silently, with the unit reporting `active`.
- **Fix**: Change `METRICS_PORT` to an `int` (`8080`). Longer term, migrate off `KubernetesServicePatch` to `ops.Unit.set_ports([Port(protocol="tcp", port=8080)])`.
- **Linter rule**: "Port constants passed to `ServicePort` must be `int`, not `str`" — mechanically checkable via type-check on all `ServicePort(...)` call sites.

### 2. Both charms silently ignore gateway/ingress relation removal — no `relation-broken` handler, and it can cascade
- **Severity**: critical
- **Kind**: bug
- **Where**: `charms/tensorboard-controller/src/charm.py` (`__init__`: only `relation_changed` observed for `SIDECAR_GATEWAY_RELATION`/`AMBIENT_GATEWAY_RELATION`); `charms/tensorboards-web-app/src/charm.py` (`__init__`: only `ingress.relation_changed` observed)
- **Evidence**: `juju remove-relation tensorboard-controller:gateway-info istio-pilot:gateway-info` fires `gateway-info-relation-broken`, unhandled; unit stays `ActiveStatus`; `pebble plan` still shows the stale `ISTIO_GATEWAY` env var. The same test on `ingress` for tensorboards-web-app causes the `ingress-relation-broken` hook to fire on `istio-pilot` (the provider side), which has no observer for it and enters `error`: `hook "ingress-relation-broken" ... failed: exit status 1`. `grep -rn "relation_broken\|relation_departed" .../tests/` returns nothing — the bug also has zero test coverage in either unit or integration tests.
- **Impact**: Removing (deliberately or accidentally) a gateway/ingress relation leaves the workload running with stale routing config while showing `ActiveStatus`, giving no signal to the operator. On tensorboards-web-app the missing handler additionally cascades into breaking the related `istio-pilot` charm. Any future refactor that removes the (already-missing) observer would go undetected — there is no test guarding against regressions here.
- **Fix**: Observe `relation_departed`/`relation_broken` on `SIDECAR_GATEWAY_RELATION`/`AMBIENT_GATEWAY_RELATION` (tensorboard-controller) and on `ingress`/`istio-ingress-route` (tensorboards-web-app), routing to the existing `_on_event` handler so `_get_gateway_info()`/`_check_istio_relations()` re-evaluate status and pebble layer. Add unit tests using `harness.remove_relation()` and integration tests using `destroy_relation(...)`.
- **Linter rule**: "Charm must observe `relation-broken` for every `requires` relation that gates `ActiveStatus`" — mechanically checkable by cross-referencing `metadata.yaml` requires against `observe()` calls in `__init__`.

### 3. tensorboards-web-app Pebble health check always returns 401, causing repeated gunicorn restarts
- **Severity**: critical
- **Kind**: bug
- **Where**: `charms/tensorboards-web-app/src/charm.py` (pebble layer `checks` block: `"http": {"url": f"http://localhost:{PORT}"}`, `"on-check-failure": {"tensorboards-web-app-up": "restart"}`)
- **Evidence**: `pebble checks` shows `Status: down, Failures: 8/3` (later run: `0/17` successes vs `17` failures). Pebble log: repeated `HTTP Exception handled: 401 Unauthorized: No user detected. GET / HTTP/1.1`. The app requires a `kubeflow-userid` header on all requests; the Pebble HTTP check sends none. `ps aux` shows gunicorn started at `09:02` while the container started at `08:59` — a 3-minute gap confirming Pebble-triggered restarts of gunicorn (not the container: K8s restart count stays `0`). period=30s, threshold=3 → gunicorn restarted roughly every 90s.
- **Impact**: The workload is actually healthy, but Pebble kills and replaces all 3 gunicorn workers every ~90 seconds, terminating any in-flight HTTP requests/sessions. This disruption is invisible to `kubectl get pods` restart counts.
- **Fix**: Replace the HTTP check with a TCP socket check (`"tcp": {"port": PORT}`). A properly unauthenticated `/health` endpoint would require an upstream image change.
- **Linter rule**: not mechanically checkable without app-specific auth knowledge.

### 4. No unit or integration tests for `relation-broken` handling
- **Severity**: high
- **Kind**: test-gap
- **Where**: `charms/tensorboard-controller/tests/unit/test_operator.py`, `charms/tensorboards-web-app/tests/unit/test_operator.py`, both `tests/integration/` dirs
- **Evidence**: `grep -rn "relation_broken\|relation-broken\|relation_departed" charms/tensorboard-controller/tests/ charms/tensorboards-web-app/tests/` returns nothing. The vendored `service_mesh.py` correctly tests/observes `relation-broken` for `service-mesh`, but neither charm's own test suite covers `relation-broken` for `gateway-info`, `ingress`, or `istio-ingress-route`. No `_on_upgrade` handler tests exist in either charm.
- **Impact**: Finding 2 is a critical bug discovered only via manual testing; without regression coverage, a future change could silently reintroduce or worsen it. `_on_upgrade` is entirely untested in both charms.
- **Fix**: Add `harness.remove_relation()` unit tests asserting pebble layer/status updates on relation removal; add `ops_test`-based integration tests using `destroy_relation(...)`; add `harness.charm.on.upgrade_charm.emit()` tests.
- **Linter rule**: "Every `requires` interface in `metadata.yaml` that can trigger `BlockedStatus` must have a test for `relation-broken`" — mechanically checkable by cross-referencing metadata requires against test files.

### 5. `tensorboard-image` config only sets an env var, does not change the workload container image
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/tensorboard-controller/src/charm.py` (`"TENSORBOARD_IMAGE": self.model.config["tensorboard-image"]`)
- **Evidence**: `juju config tensorboard-controller tensorboard-image=invalidregistry.io/nonexistent:v999` updated `pebble plan`'s `TENSORBOARD_IMAGE` env var, but the StatefulSet's container image (from the OCI resource, `...tensorboard-controller-image@sha256:...`) was unaffected. K8s never attempted to pull the invalid registry.
- **Impact**: An operator reasonably expects `tensorboard-image` to change the running container image; it only changes an env var consumed by the manager binary for CR-provisioned TensorBoard pods (unverified whether it's even consumed that way — not confirmed against upstream binary source).
- **Fix**: Document clearly what this config controls (the TensorBoard viewer image used inside CRs, not the charm's own container), or remove it if the intent was to control the charm image.
- **Linter rule**: not mechanically checkable.

### 6. KubernetesServicePatch library is deprecated, removal scheduled October 2025, and swallows patch errors
- **Severity**: medium
- **Kind**: bug, maintenance
- **Where**: `charms/tensorboard-controller/src/charm.py`, `charms/tensorboards-web-app/src/charm.py`, both `lib/charms/observability_libs/v1/kubernetes_service_patch.py` (LIBPATCH 13)
- **Evidence**: The vendored library carries an explicit deprecation notice recommending `ops.Unit.set_ports`. Its `_patch` method logs `ApiError` without re-raising, which is the direct mechanism behind Finding 1 — service patch failures never surface as a hook error or blocked status.
- **Impact**: After the library is pulled from Charmhub, both charms will break on next refresh unless migrated. In the meantime, patch failures are invisible to operators.
- **Fix**: Migrate to `ops.Unit.set_ports([Port(protocol="tcp", port=...)])` and drop the library entirely.
- **Linter rule**: not mechanically checkable.

### 7. No `grafana-dashboard` relation on either charm (tracked upstream as issue #173)
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `charms/tensorboard-controller/metadata.yaml`, `charms/tensorboards-web-app/metadata.yaml`
- **Evidence**: Neither charm provides `grafana-dashboard`. Open issue #173 tracks adding metrics collector/dashboard/alert-rules for tensorboards-web-app.
- **Impact**: COS integration is incomplete — no easy Grafana visibility into charm health, and the `metrics-endpoint` relation alone (see grafana-agent-k8s finding below) doesn't deliver a usable COS pipeline without further relations.
- **Fix**: Implement `grafana-dashboard` per issue #173; consider `send-remote-write`/`grafana-cloud-config` support.
- **Linter rule**: not mechanically checkable.

### 8. `leader-election` config option defined but never read
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/tensorboard-controller/config.yaml` (`leader-election` option), `charms/tensorboard-controller/src/charm.py` (never referenced)
- **Evidence**: `grep -rn "leader-election\|leader_election" src/charm.py` returns nothing. The manager binary handles its own K8s-operator leader election; the charm passes `RWO_PVC_SCHEDULING`/`TENSORBOARD_IMAGE` env vars but no leader-election flag. Juju validates the boolean type at the CLI (`ERROR option "leader-election" expected boolean, got "invalid"`), confirming this is genuinely dead charm-side code, not a validation gap.
- **Impact**: The option is a no-op — misleading to operators who set it expecting an effect.
- **Fix**: Either wire it to a supported manager-binary flag/env var, or remove the config option.
- **Linter rule**: "All config options in `config.yaml` must be read via `self.model.config` in charm code" — mechanically checkable.

### 9. CI lint only runs on `tests/`, not `src/` — real lint issues in charm code undetected
- **Severity**: medium
- **Kind**: lint
- **Where**: `.github/workflows/ci.yaml`, both per-charm `tox.ini`
- **Evidence**: `pflake8`/`isort --check-only`/`black --check --diff` target only `tests/`. `ruff check src/` on both charms finds real violations: E501 line-too-long in both `charm.py` files (import lines and a comment), I001 unsorted import blocks in both, and UP035 deprecated `typing.Dict`/`typing.List` in both copies of `service_mesh.py`.
- **Impact**: Code-quality and style issues in the charms' actual logic are invisible to CI.
- **Fix**: Add `src/` to lint targets in `tox.ini` and CI; fix the flagged E501/I001/UP035 issues.
- **Linter rule**: "Lint commands must include `src/` alongside `tests/`" — mechanically checkable.

### 10. Upgrades and removals not unit-tested
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `charms/tensorboard-controller/src/charm.py` (`_on_upgrade`), `charms/tensorboards-web-app/src/charm.py` (`_on_remove`)
- **Evidence**: Coverage reports show these handlers' lines uncovered in both charms (tensorboard-controller ~82%, tensorboards-web-app ~83%). `_on_upgrade` triggers the full reconciler with `force_conflicts=True`; `_on_remove` calls `k8s_resource_handler.delete()`. In live testing `_on_remove` correctly deleted ClusterRole/ClusterRoleBinding on `remove-application`, but the non-404 `ApiError` error path is untested in either charm.
- **Impact**: Upgrade/remove failure paths could regress silently — orphaned cluster-scoped resources, or a failed force-replan on upgrade.
- **Fix**: Add unit tests for `_on_upgrade` (existing pebble layer + upgrade event) and `_on_remove` (assert `delete()` called; test the non-404 `ApiError` path). Add an integration test for tensorboards-web-app's resource removal (tensorboard-controller already has one).
- **Linter rule**: not mechanically checkable.

### 11. ClusterRole/ClusterRoleBinding names are not namespaced by model — cross-model collision risk
- **Severity**: low
- **Kind**: bug
- **Where**: `charms/tensorboard-controller/src/templates/auth_manifests.yaml.j2`, `charms/tensorboards-web-app/src/templates/auth_manifests.yaml.j2` (`name: {{ app_name }}`)
- **Evidence**: Both templates produce cluster-scoped `ClusterRole`/`ClusterRoleBinding` named only after the app name. Juju guarantees app-name uniqueness within a model, not across models.
- **Impact**: Two Juju models deploying the charm under the same app name would collide on these cluster-scoped resources — rare in practice, but possible in multi-model Kubeflow installs.
- **Fix**: Include the model/namespace in the resource name.
- **Linter rule**: "Cluster-scoped resource names should include model/namespace" — mechanically checkable by scanning templates for cluster-scoped kinds without a namespace component in `name`.

### 12. `JujuVersion.from_environ()` deprecated in vendored `loki_push_api` library
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/loki_k8s/v1/loki_push_api.py` (vendored copy in both charms)
- **Evidence**: Unit test output shows `DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead`, triggered via `LogForwarder`'s `check_juju_version()` on every charm instantiation.
- **Impact**: Deprecation noise on every hook/test run; requires a library update rather than a charm code fix.
- **Fix**: Vendor an updated `loki_push_api` release, or patch the vendored copy.
- **Linter rule**: not mechanically checkable within this repo without comparing against upstream.

### 13. Deprecated `Harness` test API
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_operator.py` in both charms
- **Evidence**: `PendingDeprecationWarning: Harness is deprecated...` on test runs.
- **Impact**: Tests will need migration before `Harness` is removed from `ops`.
- **Fix**: Migrate to `ops.testing.Scenario`.
- **Linter rule**: "Do not use `ops.testing.Harness`" — mechanically checkable via grep for `Harness(`.

### 14. tensorboards-web-app ingress setup only runs once, in `__init__`, gated on initial leadership
- **Severity**: low
- **Kind**: bug
- **Where**: `charms/tensorboards-web-app/src/charm.py` (`if self.unit.is_leader():` block wrapping `self.ingress`, `self._mesh`, `_ambient_ingress_setup()`)
- **Evidence**: Non-leader units never instantiate `IstioIngressRouteRequirer` or call `_ambient_ingress_setup()` at `__init__` time. On leadership promotion, the `leader_elected` observer runs `_on_event`, but `_ambient_ingress_setup()` is not re-invoked from there, and `submit_config` (confirmed idempotent) is never called again on promotion.
- **Impact**: In multi-unit HA with leadership change, ingress config may not be re-published by the newly promoted leader. Single-unit deployments (the common case) are unaffected.
- **Fix**: Move ingress/mesh setup outside the leader-only `__init__` gate, or explicitly re-submit config in the `leader_elected` handler.
- **Linter rule**: not mechanically checkable.

### 15. Non-leader unit stays at `1/2 Ready` indefinitely
- **Severity**: low
- **Kind**: ux
- **Where**: `charms/tensorboard-controller/src/charm.py` (`_on_event` calls `_check_leader()` first; non-leaders never start `/manager`)
- **Evidence**: After scaling to 2, unit-1's pebble layer applied but service stayed `inactive` (correct, leadership-gated); the pod showed `1/2` Ready because container readiness is tied to the (intentionally not started) manager process.
- **Impact**: Correct behaviour, but `kubectl get pods` showing `1/2` indefinitely could read as unhealthy to an operator unfamiliar with the leadership gating.
- **Fix**: Consider a readiness check that passes even when the manager is intentionally not started on non-leaders (e.g. TCP check on the pebble socket).
- **Linter rule**: not mechanically checkable.

### 16. grafana-agent-k8s blocked status is correct but potentially misleading
- **Severity**: low
- **Kind**: ux
- **Where**: `grafana-agent-k8s:metrics-endpoint` relation behaviour
- **Evidence**: After relating `tensorboard-controller:metrics-endpoint → grafana-agent-k8s:metrics-endpoint`, grafana-agent-k8s went `blocked`: `Missing ['grafana-cloud-config']|['send-remote-write'] for metrics-endpoint`. tensorboard-controller stayed `active` throughout.
- **Impact**: An operator could mistake the block for a tensorboard-controller problem; it's actually grafana-agent-k8s needing a metrics destination.
- **Fix**: Document that `metrics-endpoint` alone is insufficient for COS integration, or add a direct `grafana-cloud-config`/`send-remote-write` endpoint to tensorboard-controller.
- **Linter rule**: not mechanically checkable.

### 17. `dashboard-links` endpoint name mismatch vs. kubeflow-dashboard
- **Severity**: low
- **Kind**: docs
- **Where**: `charms/tensorboards-web-app/metadata.yaml` (`dashboard-links` endpoint) vs. kubeflow-dashboard's exposed endpoint (`links`)
- **Evidence**: `juju relate tensorboards-web-app:dashboard-links kubeflow-dashboard:dashboard-links` fails: `relation endpoint not found`. `juju relate tensorboards-web-app:dashboard-links kubeflow-dashboard:links` succeeds (Juju matches by interface type `kubeflow_dashboard_links`).
- **Impact**: An operator following only `metadata.yaml` would not discover the correct counterpart endpoint name.
- **Fix**: Rename the endpoint in `metadata.yaml` to `links` for consistency.
- **Linter rule**: not mechanically checkable.

### 18. `charmed_service_mesh_helpers` poetry.lock out of sync with installed version
- **Severity**: low
- **Kind**: maintenance
- **Where**: `charms/tensorboard-controller/poetry.lock`
- **Evidence**: `poetry.lock` pins `charmed-service-mesh-helpers` to `0.5.0`; `pip show` reports `0.6.0` installed. `pyproject.toml` requires `>=0.3.0`, so no functional regression currently.
- **Impact**: Lock/environment drift can cause inconsistent CI vs. local behaviour.
- **Fix**: Run `poetry lock` and commit the update.
- **Linter rule**: not mechanically checkable.

### 19. Terraform apply check disabled in CI
- **Severity**: low
- **Kind**: docs
- **Where**: `.github/workflows/ci.yaml` (`terraform-checks` job, `apply: false`)
- **Evidence**: CI comment: "Skipping the Terraform apply check as the tensorboard-controller goes to Waiting status instead of the expected Blocked or Active. This is currently a limitation of the Terraform re-usable workflows." `terraform validate`/`plan` still run.
- **Impact**: Terraform-module users won't catch runtime deploy issues via CI.
- **Fix**: Re-enable `apply: true`, or document the limitation more permanently.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Clean status precedence with `ErrorWithStatus`** (`charmed-kubeflow-chisme`): both charms raise `ErrorWithStatus` with the appropriate `BlockedStatus`/`WaitingStatus`/`MaintenanceStatus` and short-circuit cleanly in `_on_event` via `self._log_and_set_status(error.status); return` — avoids nested if/else status logic.
- **Reconciler pattern with resource handlers**: lazily-created `KubernetesResourceHandler` properties (`rbac_resource_handler`, `crd_resource_handler`), used as a set for apply/delete — DRY and reusable.
- **Parameterized unit tests for env var logic**: `test_use_gateway_api_environment_variable_parameterized` in tensorboard-controller's tests uses `@pytest.mark.parametrize` to cover both gateway-API modes plus the service-mesh toggle.
- **Multiple ingress relation support for ambient mesh**: `_ambient_ingress_setup` submits config to every `istio-ingress-route` relation; `test_each_istio_ingress_route_relation_receives_config` explicitly verifies two-app fan-out.
- **`update_layer` idempotency** (chisme): compares current vs. new pebble layer services and only `replan()`s on change, so repeated `config-changed` hooks don't needlessly restart the workload.
- **`charm-user: non-root` security context**: both `metadata.yaml` files specify non-root `uid`/`gid`, with `assert_security_context` integration test coverage.
- **Pebble `startup: enabled` with automatic restart**: confirmed live — killing the workload process recovered within ~3s with no unit status change.

## Common-practice notes

**Following ecosystem conventions:**
- Standard `charmcraft.yaml` (poetry plugin, poetry-deps/charm-poetry parts, Rust toolchain for native extensions).
- `lib/charms/<name>/v<N>/` versioning per charm (not root-level `lib/`).
- `src/charm.py` layout, `tests/unit/`/`tests/integration/` organization.
- Per-charm `tox.ini` with `fmt`/`lint`/`unit`/`integration`/`integration-ambient` environments.
- `pyproject.toml` poetry groups for charm/unit/lint/fmt/integration.
- `charm-user: non-root`, rock images via OCI resources with `upstream-source`.
- `terraform/` module with `main.tf`/`outputs.tf`/`variables.tf`/`versions.tf`.
- CI uses `canonical/data-platform-workflows` and `canonical/charmed-kubeflow-workflows`.

**Drifts from convention:**
- Root `tox.ini` delegates to per-charm `tox.ini` (intentional per README, but unusual).
- `leader-election` config is dead code (Finding 8).
- Lint only checks `tests/`, not `src/`; CI does not run `codespell` on `src/` either (Finding 9).
- `charmed_service_mesh_helpers` is a PyPI dependency in tensorboard-controller, not vendored.
- `kubernetes_service_patch` is deprecated, removal scheduled October 2025 (Finding 6).

**LXD/substrate**: both charms are k8s-only (`containers:` + OCI resources in `metadata.yaml`); cannot run on LXD machine substrate. `concierge-lxd`/`concierge-lxd-4` controllers are not applicable.

**Versioning**: both charms are at `1.11/edge` on Charmhub (rev 715 / rev 700, matching what was deployed). Repo HEAD is `0cad154` (2026-06-22), tagged `tensorboard-controller/rev714` — one revision behind the deployed edge for tensorboard-controller. `concierge.yaml` specifies Juju `3.6/stable` and k8s `1.32-classic/stable` (for LXD/microk8s CI); the actual deployment used Juju 4.0.12 on the k8s cloud, so this concierge file target does not directly describe the review environment.

## Tests

### Unit tests
- **tensorboard-controller**: 13 tests, all pass (~0.7–0.9s). Coverage 82%; missing lines cover `_get_gateway_info` error paths when both gateway relations are present, `_on_upgrade` (entire handler), and the non-404 `ApiError` path in `_apply_k8s_resources`.
- **tensorboards-web-app**: 12 tests, all pass (~1.1–1.2s). Coverage 83%; missing lines cover `_on_remove`'s error path, the non-leader `ServiceMeshConsumer` init path, `dashboard-links` handling, and the upgrade path.
- Both use the deprecated `ops.testing.Harness` (Finding 13).

### Integration tests
- `test_charm.py` (tensorboard-controller): deploys locally built charm, waits for blocked, adds grafana-agent, relates istio-pilot, creates a Tensorboard CR via lightkube, checks metrics/logging/alert-rules, verifies security context, removes app and checks CRD cleanup.
- `test_charm_ambient.py` (tensorboard-controller): same, but via ambient mesh (`gateway-metadata` + `service-mesh`).
- `test_charm.py` (tensorboards-web-app): deploys, waits for blocked, adds grafana-agent/logging, relates istio-pilot ingress, checks UI accessibility with `kubeflow-userid` header, checks security context.
- `test_charm_ambient.py` (tensorboards-web-app): uses `istio-ingress-route`, expects 503 without full ingress config.
- **Gap**: integration tests assert coarse `active`/`blocked` status only, not pebble check status, resource content, or env var values — functional smoke tests rather than behavioural specs. No `relation-broken`, upgrade, or pebble-check-status integration tests (Finding 4).
- Integration tests failed in this review environment: `juju server-version 4.0.12 not supported` by the `charmed-kubeflow-workflows` version in use — an environment limitation, not a charm defect.
- CI runs both `integration` and `integration-ambient` per charm.

### Lint
- `pflake8`, `isort --check-only`, `black --check --diff`, `codespell` all pass — but only against `tests/`.
- `ruff check src/` finds E501 and I001 violations in both `charm.py` files, undetected by CI (Finding 9).
- `ruff check lib/ --select=UP035` finds deprecated `typing.Dict`/`typing.List` in both `service_mesh.py` copies.

## Docs

- **Root README.md**: general Kubeflow marketing document, not charm-specific; gives correct deployment/istio-relation commands but omits `service-mesh`/`gateway-metadata` ambient-mesh options; redirects to `charmed-kubeflow.io/docs`.
- **Per-charm README.md**: thin (546 and 631 bytes) — one-line description plus Charmhub link.
- **CONTRIBUTING.md** (root and per-charm): reasonable coverage of poetry/tox setup, test running, coding standards.
- **Charmhub descriptions**: minimal ("Kubeflow Tensorboard Controller" / "Kubeflow Tensorboards Web App").
- **Terraform README**: documents module inputs/outputs; `outputs.tf` correctly exposes all provides/requires relations.
- **Doc/reality mismatch**: root README suggests `--channel=latest/edge`, but Charmhub `latest/stable` is empty (`--`); should point to `1.10/stable` or `1.11/edge`.
- **Missing docs for `tensorboard-image`**: `config.yaml` describes it as "Configurable TensorBoard image" without clarifying it only sets an env var and does not change the charm's own container image (Finding 5).

## Open questions

1. Does the upstream `tensorboard-controller` manager binary support a leader-election flag? If not, the `leader-election` config option should be removed rather than wired up (Finding 8).
2. Is there a newer published `loki_push_api` that fixes the `JujuVersion.from_environ()` deprecation, or does the vendored copy need patching (Finding 12)?
3. Is cross-model mesh (`provide-cmr-mesh`/`require-cmr-mesh`) exercised anywhere in the broader Kubeflow bundle CI, given it's untested here?
4. Has GitHub issue #261 (METRICS_PORT string bug) already been fixed on a branch ahead of the reviewed HEAD? HEAD (`0cad154`, 2026-06-22) predates the issue filing (2026-08-12) and is one revision behind the deployed `1.11/edge` for tensorboard-controller.
5. Is `ops.Unit.set_ports` supported by the charmcraft/ops versions currently pinned here, and is there a migration plan ahead of the October 2025 `KubernetesServicePatch` removal (Finding 6)?
6. What is the timeline for issue #173 (grafana-dashboard), and does tensorboard-controller need the same treatment as tensorboards-web-app (Finding 7)?
7. Was the missing `relation-broken` observer (Finding 2) a deliberate decision or an oversight? Given the one-line fix and the severity of the cascading failure observed, an oversight seems most likely.
