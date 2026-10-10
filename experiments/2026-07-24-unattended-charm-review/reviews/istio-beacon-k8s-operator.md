# istio-beacon-k8s

A K8s sidecar charm acting as the Istio "beacon" in Canonical's service-mesh ecosystem. When deployed alongside `istio-k8s`, it does create Gateway resources, namespace labels, and AuthorizationPolicies, and the code architecture (reconciler pattern, integration test coverage) is solid. But the published revision (74, channel `1/edge`) is unreliable in practice: it crashes on deploy without `istio-k8s` present (the normal first step for most operators) and gets stuck in an unrecoverable loop that also blocks config changes and teardown; it never creates HPAs even in the happy path; it leaks Kubernetes resources on removal, especially on Juju 4.x where the `remove` event never fires; and it cannot interoperate with any consumer using the current PyPI `charmlibs-interfaces-service-mesh` library (immediate `ValidationError` crash). HEAD fixes most of these, but the published charm does not correspond to any single commit on main — it mixes old and new behaviours, so operators are running the worst available combination.

**A maintainer should, in order:** (1) publish a new revision built cleanly from HEAD to pick up the HPA and `planned_units()` fixes, (2) replace the `RuntimeError` crash-loop with `BlockedStatus`/`defer()` so the charm can recover once `istio-k8s` is installed and so config-changed keeps being processed, (3) fix `_on_remove`/`stop` handling so cleanup runs on Juju 4.x, and (4) update the published `ServiceMeshProvider` to emit `mesh_type` so it doesn't break consumers on the current library.

| | |
|---|---|
| Repo | canonical/istio-beacon-k8s-operator @ `51b204d` (2026-06-24, matches `_context/head.txt`) |
| Charms | istio-beacon-k8s (primary), service-mesh-tester (test helper) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5) and concierge-k8s-3 (Juju 3.6.25), channel `1/edge` rev 74; multiple deploys: standalone crash, happy path with istio-k8s dev/edge rev 71, full stack with service-mesh-tester (local pack), scale-up/scale-down, remove-application on both Juju versions |
| Reviewed | 2026-08-11 |

## What it does

`istio-beacon-k8s` is the Istio-specific "beacon" in Canonical's service-mesh charm family. It:

1. **Provides a service mesh** via the `ServiceMeshProvider` library — publishing mesh labels (`istio.io/dataplane-mode: ambient`, `istio.io/use-waypoint`) and collecting MeshPolicy requests from related charms over the `service-mesh` relation.
2. **Manages an Istio waypoint** — constructing a Kubernetes Gateway (`gateway.networking.k8s.io/v1`, `gatewayClassName: istio-waypoint`) and (in HEAD) a HorizontalPodAutoscaler tying waypoint replicas to charm unit count. Gateway names are derived from model/app name, truncated to ≤63 chars.
3. **Generates AuthorizationPolicies** from MeshPolicy objects on the `service-mesh` relation, supporting L7 (AppPolicy) and L4 (UnitPolicy) modes, gated by `manage-authorization-policies`.
4. **Optionally puts the entire model on the mesh** via `model-on-mesh`, adding `istio.io/use-waypoint`, `istio.io/dataplane-mode: ambient`, and a `charms.canonical.com/istio.io.waypoint.managed-by` ownership label to the namespace.
5. **Runs a metrics-proxy** sidecar (`docker.io/ubuntu/metrics-proxy:0.1.1-22.04_stable`) broadcasting mesh workload metrics.
6. **Exposes metrics** via `prometheus_scrape` (port 15090) and **accepts tracing** via `charm-tracing` (otlp_http).
7. **Handles cross-model relations** via `provide-cmr-mesh`.

Config: `manage-authorization-policies` (bool, default true), `model-on-mesh` (bool, default false), `ready-timeout` (int, default 100s). No actions defined.

## Deployment log

### Environment
- **concierge-k8s-4**: Juju 4.0.5, Kubernetes (shared cluster)
- **concierge-k8s-3**: Juju 3.6.25, Kubernetes (same cluster)
- Gateway API CRDs v1.2.1 pre-installed

### Deploy 1: rv-deep (Juju 4.0.5, standalone)
```
$ juju add-model rv-deep --controller concierge-k8s-4
$ juju deploy istio-beacon-k8s --channel 1/edge --trust
```
Gateway `istio-beacon-k8s-rv-deep-waypoint` created (`Programmed: Unknown`). HPA **not** created. Charm loops in `_is_waypoint_deployment_ready()`: 10×10s retries (default `ready-timeout=100`), each 404ing on the Deployment lookup (no istio control plane). After 100s: **RuntimeError crash** — but on Juju 4.x the unit stays `maintenance/executing`, never showing `error`. Juju auto-retries every ~5s, repeating indefinitely. Workload status shows `"Validating waypoint readiness"` perpetually.

### Deploy 2: rv-deep36 (Juju 3.6.25, standalone)
Same initial behaviour (Gateway created, no HPA, RuntimeError cycle). On Juju 3.6 status-history records `error: hook failed: "config-changed"` between retries (Juju 4 never shows `error`). Workload status stays `maintenance` on both, so `juju resolve` is ineffective either way.

### Config changes during crash loop (rv-deep)
- `model-on-mesh=true`: no effect — event queued but never processed.
- `ready-timeout=0`: no effect, same reason.
- `manage-authorization-policies="not-a-bool"` / `model-on-mesh="not-a-bool"`: correctly rejected by Juju itself.

Relation events, however, *are* processed during the crash loop: relating `tempo-k8s` (latest/edge rev 83) established `charm-tracing` successfully, and relating `grafana-agent-k8s` (1/edge rev 168) established `prometheus_scrape`. Config-changed events apparently have lower priority than relation events in the queue.

### Scale up to 2 units (both models)
Non-leader unit reaches `blocked: "Waypoint can only be provided on the leader unit."` on both Juju versions; application status becomes `blocked`.

### Scale down to 1 unit — critical bug on Juju 3.6
**rv-deep (Juju 4):** unit 1 runs `stop` only (not `remove`); clean removal.

**rv-deep36 (Juju 3.6):** unit 1 runs `remove`. Published rev 74 lacks the `planned_units() > 0` guard present in HEAD (`src/charm.py:225`). Sequence:
1. `_remove_labels()` warns `"Cannot remove labels: managed by another entity"` (no labels present).
2. `_get_waypoint_resource_manager().delete()` **succeeds** — deletes Gateway `istio-beacon-k8s-rv-deep36-waypoint` (created by unit 0).
3. `_get_authorization_policy_resource_manager().delete()` **crashes** — `get_deployed_resources()` lists `security.istio.io/v1/authorizationpolicies`, gets 404 (CRDs not installed), raises `httpx.HTTPStatusError` uncaught by `except ApiError`.
4. `_get_modeloperator_policy_resource_manager().delete()` never runs.

Unit 1 stuck `error: hook failed: "remove"`; application shows scale `2/1`, deadlocked — cannot scale further, remove, or reconfigure.

### Simulated crash (rv-deep)
```
$ kubectl exec -n rv-deep istio-beacon-k8s-0 -c charm -- kill -9 <pid>
```
Juju detects the killed process, restarts the unit agent, retries the hook. Workload stays `maintenance`, no `error` state. Behaviour indistinguishable from the ordinary crash loop.

### Remove-application — orphaned resources on Juju 4
`juju remove-application istio-beacon-k8s --model rv-deep --no-prompt` removes the application but does **not** clean up the Gateway or namespace labels. `istio-beacon-k8s-rv-deep-waypoint` persists in the cluster after model destruction (confirmed via `kubectl get gateways -A`; rv-deep36's Gateway was already deleted earlier by the remove-hook crash).

### Deploy 3: happy path — istio-k8s + beacon on Juju 4 (rv-final)
```
$ juju add-model rv-final --controller concierge-k8s-4
$ juju add-model istio-system2 --controller concierge-k8s-4
$ juju deploy istio-k8s --channel dev/edge --trust --model istio-system2
$ juju deploy istio-beacon-k8s --channel 1/edge --trust --model rv-final
```
Waypoint Deployment created and ready in ~30s. Charm reaches `active`:
- Gateway created, `Programmed: True`
- Waypoint Deployment `1/1 Ready`
- Metrics-proxy pebble service `active`
- **HPA still not created** — `kubectl get hpa -A` empty; the published KRM only reconciles the Gateway
- No AuthorizationPolicies (correct — no service-mesh relations, `model-on-mesh=false`)

Setting `model-on-mesh=true` (with `ready-timeout=200` to avoid a race): first attempt crashed with `ops.model.ModelError: connection reset by peer` on config-changed; the unit agent restarted and the retry succeeded, applying labels and creating the modeloperator AuthorizationPolicy (`istio-beacon-k8s-rv-final-policy-all-sources-modeloperator`).

**Scale-up → agent lost (Juju 4.x controller instability):** scaling 1→2 caused unit 0's agent to go permanently `lost`; unit 1 hit the non-leader `BlockedStatus` bug. Unit 0 never recovered despite the containeragent process still running. Reproduced in both rv-happy and rv-final models.

**Remove-application blocked:** with unit 0 `lost`, `juju destroy-model` hung indefinitely (the lost unit cannot run its remove hook); forced namespace deletion via kubectl was required.

### Deploy 4: all-in-one — istio-k8s + beacon + service-mesh-tester (rv-mesh, Juju 4)
Beacon initially crashed with `httpx.HTTPStatusError: 404` (Gateway API CRDs not yet installed by istio-k8s), self-healed after ~40s once istio-k8s installed the CRDs. Reached `active`, waypoint `1/1 Ready`, metrics-proxy `active`. istio-k8s itself got stuck on `"Istio CNI not ready"` (cluster CNI incompatibility) — control plane worked, data plane never did. Additional confirmations in this model:
- HPA still not created
- `service-mesh-tester` crashed with `pydantic.ValidationError: mesh_type Field required` (library mismatch, see Finding 1)
- `model-on-mesh` true→false crash with a transport error after labels were already removed
- `ready-timeout=5` caused an immediate RuntimeError (0 retries) despite the waypoint actually being ready
- Non-leader `BlockedStatus` on scale-up
- Remove-application leaked the Gateway (Juju 4 fires `stop` but not `remove`)

### Refresh between channels
`1/edge` → `2/edge`: failed with `"one or more of the provided endpoints ... do not exist"` — track 2 has different relation endpoints, cross-track refresh unsupported. All track-1 channels are rev 74, so within-track refresh was not testable.

## Observed behaviour

**HPA never created, in every environment.** Debug logs show exactly one GET (gateways) and one PATCH (Gateway) per hook cycle, no HPA API calls at all — with or without istio-k8s present. HEAD's `_sync_waypoint_resources()` constructs both Gateway and HPA and scenario tests confirm correct HPA specs, but the published charm's KRM (`lightkube_extensions.batch.KubernetesResourceManager`, `WAYPOINT_RESOURCE_TYPES = {Gateway}`) never processes it.

**Namespace labels applied before readiness check (partial success).** With `model-on-mesh=true`, the namespace PATCH lands before the deployment-readiness loop. When RuntimeError crashes the hook, labels persist on a namespace whose charm is in error/maintenance — an inconsistent half-done state.

**Config changes blocked by the crash loop.** `model-on-mesh=true` / `ready-timeout=0` had no effect while the RuntimeError loop ran; `juju show-status-log` shows no config-changed event was processed after the initial deploy.

**Juju 3.6 vs 4.x differences observed:**

| Behaviour | Juju 3.6 | Juju 4.0 |
|---|---|---|
| Hook crash shows as | `error` in status-history, `maintenance` workload | `maintenance` everywhere, never `error` |
| `juju resolve` works? | No | No |
| Config changes processed during crash loop? | No | No |
| Scale-down hook | `remove` (crashes on published charm) | `stop` only (`remove` never fires) |
| Application removal | Blocked by remove-hook crash | Completes but leaks Gateway + labels |

**Gateway label drift.** Published rev 74 sets `istio.io/waypoint-for: all`; HEAD sets `"service"` (`src/charm.py:384`/`400` across revisions). The value has flipped across commits, changing mesh scope for all namespace workloads on upgrade.

**Metrics-proxy never starts without istio-k8s.** `_setup_proxy_pebble_service()` only runs after `_is_waypoint_ready()` succeeds, so it's silently skipped in the crash-loop scenario; even when `container.can_connect()` is False the method returns `None` and the caller never checks (open issue #42). With istio-k8s present, metrics-proxy does reach `active`.

**Non-leader status differs between published and HEAD.** Published: `BlockedStatus("Waypoint can only be provided on the leader unit.")`. HEAD (commit `36cf71b`): `ActiveStatus("Backup unit; standing by for leader takeover")`.

**False-positive "managed by another entity" warning.** Fires on every hook execution even on a fresh deploy with no prior beacon, because the namespace has no `managed-by` label and `_remove_labels()` (`src/charm.py:549-553`) treats absence as "managed by another entity." Should be DEBUG-level for the no-label case.

**Hook blocking.** Each hook blocks up to `ready-timeout` seconds (default 100) in `time.sleep(10)` loops; the uniter retries almost immediately (~1-2s) after a crash, so the charm spends ~100s executing, crashes, and retries within ~2s. On Juju 3.6 the retry backoff grows slightly (~10s between status-history error entries).

**No actions; metrics-proxy pebble state matches expectations.** `kubectl exec` confirms pebble service `inactive` when istio-k8s is absent (hook crashes before `_setup_proxy_pebble_service()`), `active` once istio-k8s is deployed.

**Happy-path summary (istio-k8s deployed, Juju 4):** Gateway created and programmed automatically once istio-k8s picks it up; waypoint readiness takes ~30s; AuthorizationPolicies created correctly for `model-on-mesh=true` and for service-mesh relations; metrics-proxy becomes active after waypoint readiness; namespace labels applied correctly via PATCH with ownership-label conflict protection. HPA remains the one thing that never works, even here.

**Juju 4.x controller instability — reproducible agent-lost.** In two separate fresh models (rv-happy, rv-final), unit 0's agent went permanently `lost` under: (a) scale from 1→2 units, or (b) a `model-on-mesh=true` config change that PATCHes the namespace. The containeragent process kept running (`ps aux` showed the pid) and pebble stayed responsive, but the controller never reconnected. `juju destroy-model` hung indefinitely because the lost unit couldn't run its remove hook. This did **not** happen on Juju 3.6.25 in the same cluster under equivalent operations.

**Pod resource state.** `istio-beacon-k8s-0`: 2 containers (`charm`, `metrics-proxy`); charm container limit 1Gi memory, no OOM or resource pressure observed. After model destruction with a lost unit, Gateway, AuthorizationPolicy, and namespace labels leaked (remove hook never ran).

**Service-mesh relation library crash (published beacon + repo tester).** Deployed `service-mesh-tester` (packed from local repo, pulling `charmlibs-interfaces-service-mesh` v0.2.0+ from PyPI) related to published `istio-beacon-k8s` rev 74. Tester crashed immediately on `service-mesh-relation-changed`:
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for ServiceMeshProviderAppData
mesh_type
  Field required [type=missing, input_value={'labels': {'istio.io/dat...-namespace': 'rv-mesh'}}, input_type=dict]
```
The published beacon's `ServiceMeshProvider.update_relations()` writes only `{"labels": json.dumps(...)}`; the newer library requires both `labels` and `mesh_type` per its `ServiceMeshProviderAppData` model. This is a hard version mismatch affecting every consumer of the current PyPI library.

**model-on-mesh true→false crash with partial success.** After `model-on-mesh=true` succeeded (labels applied, modeloperator AuthorizationPolicy created), toggling back to `false` crashed config-changed: `_sync_waypoint_resources()` (Gateway reconcile) succeeded, `_remove_labels()` removed labels (confirmed via kubectl), then `_sync_authorization_policies()`'s `krm.reconcile([])` crashed with an httpx transport error. Labels are gone but policy cleanup may not have completed — an inconsistent intermediate state, the mirror image of the remove-hook ordering bug.

**Non-leader remove hook deletes Gateway on scale-down (Juju 3.6).** Scaling 2→1 on Juju 3.6 (rv-mesh36): unit 1's remove hook deleted the Gateway (`istio-beacon-k8s-rv-mesh36-waypoint`) via `krm.delete()`; `kubectl get gateways` confirmed it gone immediately. Unit 0 recreated it only on a subsequent config-changed (triggered manually via `juju config ready-timeout=200`). The Gateway was absent ~45 seconds; the waypoint Deployment was also terminated and restarted by the Istio control plane — mesh traffic disruption for the whole model during any scale-down.

**Juju 3.6 fires both `stop` and `remove`; Juju 4 fires only `stop`.** On Juju 3.6, scale-down fired `stop` then `remove` on the departing unit, and the remove hook's `krm.delete()` succeeded (CRDs present). On Juju 4, scale-down and application removal both fired only `stop` — `remove` was never emitted, confirmed via debug-log — so `_on_remove` never runs and the Gateway cleanup path never executes on Juju 4.x, leaking resources consistently.

**`ready-timeout=5` causes immediate RuntimeError (0 retries).** `range(5 // 10)` = `range(0)` = 0 retries. `_is_waypoint_deployment_ready()` returns False immediately even though the waypoint was actually ready and running before the config change. Values below 10 are silently treated as "no retries" instead of being rejected.

**istio-k8s deployed in the same model as the beacon partially works.** The beacon initially crashes with `httpx.HTTPStatusError: 404` on the Gateway API list because istio-k8s hasn't yet installed the CRDs; after retries istio-k8s installs them and the beacon's next retry succeeds — self-healing, but dependent on istio-k8s's own deploy timing. In this run, istio-k8s itself got stuck on `"Istio CNI not ready"` (cluster CNI incompatibility), so the data plane never worked even though the control plane (istiod) was functional enough to process the waypoint.

## Findings

### 1. Service-mesh library version incompatibility breaks all current consumers
- **Severity**: critical
- **Kind**: bug
- **Where**: published rev 74 `lib/charms/istio_beacon_k8s/v0/service_mesh.py` (`ServiceMeshProvider`) vs deps/PyPI `charmlibs-interfaces-service-mesh` `ServiceMeshProviderAppData`
- **Evidence**: relating `service-mesh-tester` (packed from repo, using PyPI `charmlibs-interfaces-service-mesh` v0.2.0+) to published `istio-beacon-k8s` rev 74 crashed with `pydantic_core._pydantic_core.ValidationError: mesh_type Field required`. Published provider writes only `{"labels": ...}`; the newer library requires `{"labels": ..., "mesh_type": ...}`.
- **Impact**: any consumer built against the current recommended library — including the charm's own test helper — crashes immediately on relation with the published beacon.
- **Fix**: publish a new revision from HEAD, whose `ServiceMeshProvider` includes `mesh_type`. As an interim mitigation the PyPI package could make `mesh_type` optional.
- **Linter rule**: integration test deploying published beacon + local consumer on latest library — mechanically checkable.

### 2. Remove hook crashes on Juju 3.x when Istio CRDs are absent, blocking scale-down and teardown
- **Severity**: critical
- **Kind**: bug
- **Where**: published rev 74 `_on_remove` (no `planned_units()` guard, unlike HEAD `src/charm.py:225-228`); `deps/canonical_service_mesh/k8s/resource_manager/_resource_manager.py:179-186` (`get_deployed_resources()`)
- **Evidence**: scaling 2→1 on Juju 3.6 crashed unit 1's remove hook with `httpx.HTTPStatusError` after successfully deleting the Gateway. `raise error` at line 186 is unconditional — it re-raises even after the 404 branch logs "Ignoring this type" — and `httpx.HTTPStatusError` (API group absent) is not caught by `except ApiError` at line 181. Unit stuck in `error: hook failed: "remove"`, application scale `2/1`, deadlocked.
- **Impact**: on Juju 3.x, any scale-down or application removal can crash the departing unit, leaving mixed state (Gateway gone, policies maybe leaked) and blocking further lifecycle operations.
- **Fix**: already fixed in HEAD via the `planned_units() > 0` guard. The `canonical_service_mesh` dependency also needs the `raise error` moved under an `else:`, and `httpx.HTTPStatusError` caught for the missing-API-group case.
- **Linter rule**: "`_on_remove` calls Kubernetes API without guarding `planned_units() == 0`"; "unconditional `raise` in `except` block after conditional log-and-ignore" — both mechanically checkable.

### 3. RuntimeError instead of BlockedStatus when istio-k8s is absent — unrecoverable crash loop
- **Severity**: critical
- **Kind**: bug / ux
- **Where**: `src/charm.py:337` (HEAD) — `raise RuntimeError("Waypoint's k8s deployment not ready, is istio properly installed?")`
- **Evidence**: observed on every standalone deployment. Juju 4.x: unit never reaches workload `error`, stays `maintenance` perpetually; `juju resolve` doesn't work. Juju 3.6: status-history shows `error` but workload status stays `maintenance` too. Config-changed events are queued but never processed in either case, so operators cannot even change `ready-timeout` or `model-on-mesh` to work around it. Only recovery: install istio-k8s or destroy the model.
- **Impact**: deploying the beacon before istio-k8s — the natural first step for most operators — produces a silent, unrecoverable crash loop instead of a clear "waiting for istio-k8s" status.
- **Fix**: replace the `raise RuntimeError(...)` with `self.unit.status = BlockedStatus(...)` and `defer()`/`return`; the hook re-fires when istio-k8s's Deployment appears via relation or pebble events.
- **Linter rule**: "`raise` of a built-in exception in a hook handler reachable from `self.framework.observe`" — mechanically checkable.

### 4. HPA never created — confirmed in every deployment, including the happy path
- **Severity**: critical
- **Kind**: bug
- **Where**: published rev 74 KRM reconciliation path (`lightkube_extensions.batch.KubernetesResourceManager`, `WAYPOINT_RESOURCE_TYPES = {Gateway}`); HEAD has `_construct_hpa()` at `src/charm.py:331-351`
- **Evidence**: confirmed across five deployments spanning both Juju versions and both with/without istio-k8s. `kubectl get hpa -A` shows no beacon HPA anywhere, even with Gateway `Programmed: True`, waypoint `1/1 Ready`, metrics-proxy `active`, and charm status `active`. Debug logs show exactly one GET/PATCH per hook cycle, for Gateway only. `_construct_hpa()` exists in git history since `36cf71b` (2025-06-30) but is not in the reconciliation path used by the published (2026-06-09) build.
- **Impact**: the waypoint runs at a fixed replica count of 1 regardless of charm scale; the HA scaling story is completely non-functional.
- **Fix**: publish HEAD, which uses `canonical_service_mesh` KRM with proper multi-resource-type reconciliation including `HorizontalPodAutoscaler`.
- **Linter rule**: integration test asserting `kubectl get hpa` — mechanically checkable.

### 5. Remove-application leaves orphaned Kubernetes resources
- **Severity**: high
- **Kind**: bug
- **Where**: published rev 74 `_on_remove`; `src/charm.py:220-240` (HEAD)
- **Evidence**: after `juju remove-application` on Juju 4, Gateway `istio-beacon-k8s-rv-deep-waypoint` and namespace istio labels persisted (`kubectl get gateways -A` after model destruction). On Juju 3.6, the remove hook partially clears (Gateway deleted, then crashes on AuthorizationPolicy cleanup — see Finding 2).
- **Impact**: orphaned Gateways and labels pollute the cluster; reusing a model name can conflict with the leftover Gateway; the `managed-by` ownership label never gets removed.
- **Fix**: already partly addressed in HEAD via the `planned_units()` guard. Additionally wrap each `krm.delete()` call in `_on_remove` in its own try/except so one failure doesn't skip the rest.
- **Linter rule**: "multiple side-effecting calls in a remove handler without individual try/except" — mechanically checkable.

### 6. Juju 4.x fires `stop` but not `remove` on application removal — cleanup never runs
- **Severity**: high
- **Kind**: bug (environment-dependent)
- **Where**: published rev 74 `src/charm.py` — `_on_remove` registered only to `self.on.remove`, no `stop` handler
- **Evidence**: on Juju 4.x (concierge-k8s-4), `juju remove-application` triggered `stop` on unit 0 but not `remove`; `_on_remove` never ran; Gateway persisted (confirmed via `kubectl get gateways -n rv-mesh` after removal). On Juju 3.6, both `stop` and `remove` fired and cleanup completed correctly.
- **Impact**: all Gateway and AuthorizationPolicy resources leak on application removal in the Juju 4.x environment that is the target for new deployments.
- **Fix**: register a `stop` handler performing the same cleanup as `_on_remove` (or have `_on_remove` also observe `self.on.stop`), on top of HEAD's existing `planned_units()` guard.
- **Linter rule**: "charm registers `remove` handler but not `stop` handler" — mechanically checkable.

### 7. Unit agent goes permanently "lost" on Juju 4.x during scale-up or namespace-patching config changes
- **Severity**: high
- **Kind**: bug (possibly Juju controller, not charm) — (unverified whether root cause is charm-side)
- **Where**: observed on concierge-k8s-4 (Juju 4.0.5), affects charm rev 74
- **Evidence**: reproduced in two separate models (rv-happy, rv-final). Scaling 1→2, or a `model-on-mesh=true` config change that PATCHes namespace labels, triggers `connection reset by peer` on the unit agent's controller connection; the agent restarts but never reconnects, showing `unknown/lost` permanently. containeragent (confirmed running via `ps aux`) and pebble stay responsive. `juju destroy-model` hangs indefinitely because the lost unit can't run its remove hook. Did not reproduce on Juju 3.6.25 in the same cluster under equivalent operations.
- **Impact**: makes the charm effectively undeployable on Juju 4.x after any scale or config-change operation; operators must force-delete the namespace via kubectl.
- **Fix**: investigate the Juju 4.x controller connection-reset behaviour. The charm could reduce likelihood by batching Kubernetes API calls and avoiding large namespace-label PATCHes during hook execution, but the root cause looks like a Juju controller issue.
- **Linter rule**: not mechanically checkable.

### 8. Published charm revision 74 does not correspond to any single commit on main
- **Severity**: high
- **Kind**: process
- **Where**: charmhub channel `1/edge` rev 74 (published 2026-06-09) vs git HEAD `51b204d` (2026-06-24)
- **Evidence**: rev 74 mixes behaviours from different commits — the `istio.io/waypoint-for: all` Gateway label from `36cf71b` (2025-06-30), the pre-`36cf71b` non-leader `BlockedStatus`, and the pre-`9a65d62` (2026-06-03) `lightkube_extensions` KRM (no HPA), despite `9a65d62` predating the 2026-06-09 publish date.
- **Impact**: bug reports against the published charm can't be mapped to a specific commit; it's unclear which HEAD fixes are actually present in production.
- **Fix**: tag releases with the exact commit SHA and ensure CI builds from main HEAD at release time; publish a fresh revision from current HEAD.
- **Linter rule**: not mechanically checkable.

### 9. `mesh_labels_for_service_mesh_relation()` returns empty dict when model-on-mesh=True — inverted-looking logic
- **Severity**: high
- **Kind**: bug (design, likely intentional but confusing)
- **Where**: `src/charm.py:594-599` (HEAD)
- **Evidence**: line 596: `if self.config["model-on-mesh"]: return {}` — when the whole model is on the mesh, individual related charms stop getting mesh labels via the relation (because the model already provides mesh access). The comment at line 594 documents this but the naming makes it easy to misread as a bug during debugging.
- **Impact**: operators debugging mesh connectivity can waste time on what looks like an inversion but is deliberate; low risk of an actual functional bug, higher risk of wasted investigation time.
- **Fix**: rename to something like `_labels_for_service_mesh_relation()` with a clearer docstring, or add an explicit comment explaining the inversion.
- **Linter rule**: not mechanically checkable.

### 10. Non-leader remove hook deletes application-level Gateway even when the leader is still running
- **Severity**: medium
- **Kind**: bug
- **Where**: published rev 74 `_on_remove` (no `planned_units()` guard); HEAD `src/charm.py:225-228`
- **Evidence**: on Juju 3.6, scaling 2→1 caused unit 1's remove hook to call `_get_waypoint_resource_manager().delete()`, which deleted the Gateway `istio-beacon-k8s-rv-deep36-waypoint`/`istio-beacon-k8s-rv-mesh36-waypoint` created by unit 0 — the KRM's labels are app/model-scoped, so any departing unit targets all application resources. Gateway absent for ~45 seconds until the next config-changed recreated it; waypoint Deployment also terminated and restarted by the Istio control plane.
- **Impact**: any scale-down operation (not just the crash-loop scenario) temporarily removes the waypoint and disrupts mesh traffic for the whole model.
- **Fix**: already fixed in HEAD by the `planned_units() > 0` guard; publish it.
- **Linter rule**: same as Finding 2.

### 11. `get_deployed_resources()` always re-raises ApiError (dependency bug)
- **Severity**: high
- **Kind**: bug
- **Where**: `deps/canonical_service_mesh/k8s/resource_manager/_resource_manager.py:186` (PyPI `canonical_service_mesh` v0.1.0 in deps, v0.0.2 pinned in uv.lock — published charm version unconfirmed)
- **Evidence**: `raise error` sits at the same indentation as `except ApiError as error:`, not inside the `if error.status.code == 404:` branch, so every ApiError is re-raised despite the "Ignoring this type" log message. `httpx.HTTPStatusError` (raised when the API group doesn't exist at all) is also not caught, since the `_k8s_api_call` decorator only catches `httpx.TransportError`.
- **Impact**: affects every consumer of `canonical_service_mesh`; `reconcile()` and `delete()` both crash on any ApiError, not only genuine 404s — this is what caused the observed remove-hook crash in Finding 2.
- **Fix**: move `raise error` into an `else:` clause (or `return` after the debug log); also catch `httpx.HTTPStatusError` in `get_deployed_resources()` for the missing-API-group case.
- **Linter rule**: "unconditional `raise` in `except` block after a conditional log-and-ignore" — mechanically checkable.

### 12. `model-on-mesh` toggle true→false crashes config-changed, leaving inconsistent state
- **Severity**: medium
- **Kind**: bug
- **Where**: published rev 74 `_sync_all_resources()` → `_sync_authorization_policies()` → `krm.reconcile()`
- **Evidence**: after `model-on-mesh=true` succeeded (labels applied, modeloperator AuthorizationPolicy created), toggling to `false` crashed config-changed: `_sync_waypoint_resources()` succeeded, `_remove_labels()` removed the namespace labels (confirmed via `kubectl get namespace ... -o json`), then `_sync_authorization_policies()`'s `krm.reconcile([])` crashed with an httpx transport error.
- **Impact**: labels are gone but the AuthorizationPolicy may remain; the operator sees an error with no indication of what succeeded.
- **Fix**: reorder `_sync_waypoint_resources` to do KRM reconciliation before label mutation, and wrap each KRM call in its own try/except.
- **Linter rule**: not mechanically checkable — requires runtime observation.

### 13. Namespace labels applied before waypoint readiness check — partial success on crash
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:318-340` (`_sync_all_resources()` calls `_sync_waypoint_resources()` — which applies/removes labels — at line 335, before `_is_waypoint_ready()` at line 336); label logic itself at `src/charm.py:459-468` (HEAD)
- **Evidence**: with `model-on-mesh=true`, the namespace PATCH (200 OK) appears in logs before the readiness loop; when RuntimeError crashes the hook, the labels persist on the namespace. Observed directly in the rv-happy deployment: namespace had all three istio labels while the charm was crashed/hung.
- **Impact**: an inconsistent, half-configured namespace state with no atomicity; force-destroying the model at this point leaks labels, and a new beacon in the same namespace hits a `managed-by` conflict.
- **Fix**: move `_add_labels()`/`_remove_labels()` to after the readiness check passes; if the check fails, set `BlockedStatus` without touching labels.
- **Linter rule**: not mechanically checkable — requires semantic understanding of mutation-before-validation ordering.

### 14. Metrics-proxy pebble service silently skipped
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:173-175` (definition), `src/charm.py:233` (call site) — open issue #42
- **Evidence**: `_setup_proxy_pebble_service()` implicitly returns `None` when `container.can_connect()` is False; the caller at line 233 doesn't check the return value and proceeds to `ActiveStatus` at line 237. Observed `inactive` metrics-proxy on all units in the crash-loop scenario; confirmed `active` once istio-k8s is present.
- **Impact**: the charm can report `ActiveStatus` while metrics-proxy isn't running, with no signal to the operator that mesh metrics are unavailable.
- **Fix**: return a `bool` from `_setup_proxy_pebble_service()`; on False, set `MaintenanceStatus` and `defer()`, or at minimum log an ERROR.
- **Linter rule**: "return value of a `_setup_*`/`_ensure_*` method not checked at call site" — mechanically checkable.

### 15. Terraform module channel validation blocks deploying the published charm
- **Severity**: medium
- **Kind**: docs / bug
- **Where**: `terraform/variables.tf:7-10`
- **Evidence**: validation requires `startswith(var.channel, "dev/")` with error "The track of the channel must be 'dev/'"; but published channels are `1/edge`, `1/stable`, `2/edge`, etc., none starting with `dev/`. The terraform module as documented cannot deploy the published charm.
- **Impact**: operators following the documented terraform workflow hit a validation error and must fork the module or use a non-public dev track.
- **Fix**: relax the validation to accept standard tracks, or remove it and let Juju reject genuinely invalid channels.
- **Linter rule**: not mechanically checkable — requires cross-referencing terraform validation against published channels.

### 16. `ready-timeout` accepts values below 10 that silently become zero retries
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `charmcraft.yaml` config definition; `src/charm.py:303-305`, `337`
- **Evidence**: `ready-timeout=5` → `range(5 // 10)` = `range(0)` = 0 retries → immediate RuntimeError, even though the waypoint deployment was actually ready (running fine before the config change). `ready-timeout=0` or negative values behave the same way.
- **Impact**: an operator lowering `ready-timeout` to speed up feedback gets an unconditional crash regardless of actual readiness.
- **Fix**: add `minimum: 10` to the config definition in `charmcraft.yaml`, and document the minimum effective timeout as one 10-second cycle.
- **Linter rule**: "integer config option without `minimum` when used in integer division" — mechanically checkable.

### 17. `time.sleep()` blocks the event loop for up to 100 seconds
- **Severity**: low
- **Kind**: performance (documented design choice)
- **Where**: `src/charm.py:308`
- **Evidence**: `time.sleep(check_interval)` inside `_is_waypoint_deployment_ready()` blocks the Juju event loop; hooks observed sitting in "executing" for the full 100 seconds, with no other events processed except queued relation events picked up between crash/retry cycles.
- **Impact**: a slow waypoint deployment (e.g. image pull delay) freezes charm event processing for the full `ready-timeout` even in a working setup.
- **Fix**: use `defer()` and re-check on the next hook invocation instead of sleeping; at minimum reduce `check_interval`.
- **Linter rule**: "`time.sleep()` in a charm hook handler" — mechanically checkable.

### 18. Non-leader units report BlockedStatus in the published charm
- **Severity**: low
- **Kind**: ux
- **Where**: published rev 74 `_sync_all_resources()` non-leader path
- **Evidence**: unit 1 reported `BlockedStatus("Waypoint can only be provided on the leader unit.")`, putting the application in `blocked`. HEAD changed this to `ActiveStatus("Backup unit; standing by for leader takeover")` in commit `36cf71b`.
- **Impact**: false-positive `blocked` alerts on any normal scale-up.
- **Fix**: already fixed in HEAD; publish it.
- **Linter rule**: not mechanically checkable.

### 19. Gateway `waypoint-for` label flips between "all" and "service" across revisions
- **Severity**: low
- **Kind**: bug / drift
- **Where**: `src/charm.py:384` (HEAD)
- **Evidence**: published rev 74 has `istio.io/waypoint-for: all`; HEAD has `"service"`. The label has changed value across commits (introduced as `"all"` in `36cf71b`).
- **Impact**: `"all"` means the waypoint handles all namespace traffic, `"service"` only service traffic — changing this on upgrade silently alters mesh behaviour for every workload in the namespace.
- **Fix**: settle on the intended value (`"service"` per HEAD), document its meaning, and add a test asserting the label doesn't change unexpectedly across upgrades.
- **Linter rule**: not mechanically checkable.

### 20. No `_on_upgrade_charm` handler
- **Severity**: low
- **Kind**: design note
- **Where**: `src/charm.py` — handler absent from `__init__`
- **Evidence**: handlers exist for `config_changed`, `remove`, `metrics_proxy_pebble_ready`, `service-mesh` relation events, `peers` relation events, and `provide-cmr-mesh`, but not `upgrade_charm`.
- **Impact**: an upgrade that changes internal state, resource naming, or label values (e.g. the `waypoint-for` flip in Finding 19) has no dedicated migration path and may only reconcile on the next unrelated config-changed, which could be a long time coming.
- **Fix**: add an `_on_upgrade_charm` handler that at minimum calls `_sync_all_resources()`.
- **Linter rule**: "charm without `upgrade_charm` event handler" — mechanically checkable.

### 21. `_remove_labels()` triggers a false-positive "managed by another entity" warning on every hook
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:549-553`
- **Evidence**: the warning fires on every hook when `model-on-mesh=false`, even on a fresh deploy with no prior beacon, because the guard compares the (nonexistent) `managed-by` label to the app identity and treats `None != identity` as "managed by another entity."
- **Impact**: WARNING-level log noise on every hook; can mislead operators into thinking there's a conflict when there isn't.
- **Fix**: return early when the `managed-by` label is absent, and log at DEBUG in that case.
- **Linter rule**: not mechanically checkable.

### 22. No secrets handling — unclear if intentional
- **Severity**: low
- **Kind**: design note
- **Where**: `src/charm.py` — no references to secrets; `peers` relation declared but handler (`_on_peers_changed`, line 215) only calls `_sync_all_resources()`
- **Evidence**: grep for "secret" in `src/charm.py` returns nothing; the `peers` relation is declared in `charmcraft.yaml` but no data is read from or written to it.
- **Impact**: currently no sensitive-data exposure risk since nothing is stored, but if future functionality needs to share data between peers it would need to avoid unencrypted relation data.
- **Fix**: implement peer data sharing if intended (e.g. waypoint readiness status), or remove the unused relation and document the decision.
- **Linter rule**: "peer relation declared but handler never reads peer data" — mechanically checkable.

### 23. codespell typo in library
- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/istio_beacon_k8s/v0/service_mesh.py:678`
- **Evidence**: `codespell` reports `defintion ==> definition`.
- **Impact**: cosmetic.
- **Fix**: correct the spelling.
- **Linter rule**: already caught by `codespell`.

## Worth copying

- **Central reconciler pattern with clear status progression** (`src/charm.py:318-340`) — `_sync_all_resources()` is a clean single-entry-point reconciler: checks leadership first, then progresses through discrete phases (mesh labels → waypoint → proxy → policies), setting `MaintenanceStatus` at each step.
- **Namespace label ownership tracking** (`src/charm.py:512-570`) — `_add_labels()`/`_remove_labels()` use a `charms.canonical.com/istio.io.waypoint.managed-by` label to prevent two beacons from fighting over the same namespace; good pattern for any charm mutating shared cluster resources.
- **Lightkube client indirection for testability** (`src/charm.py:243-258`) — `lightkube_client` is a lazily-created property designed for test injection without global patching.
- **Test coverage of namespace label logic** (`tests/unit/test_charm.py:22-167`) — parametrized tests cover 4+ scenarios (empty labels, existing labels, managed-by-self, managed-by-other).
- **Integration tests assert traffic behaviour, not just status** (`tests/integration/test_charm.py:153-230`) — sends real HTTP requests and asserts specific status codes (200, 403, connection-refused) based on authorization policies.
- **Scenario tests for remove-on-scale-down** (`tests/unit/test_charm_scenario.py:51-85`) — asserts `_on_remove` only deletes KRM resources when `planned_units == 0`, parametrized over 0/1/2 units.
- **Comprehensive integration test matrix** (`tests/integration/test_charm.py`) — covers model-on-mesh toggling both ways, mesh label updates on config change, AppPolicy/UnitPolicy traffic control, consumer scaling, peer communication in scaled consumers, and cross-model modeloperator connectivity.

## Common-practice notes

**Follows convention:**
- `src/charm.py` is a manageable ~600-line file.
- `charmcraft.yaml` declares `assumes: k8s-api, juju >= 3.6`, uses OCI resource containers, marks optional relations correctly.
- Standard tox environments: `lint`, `static`, `unit`, `integration`.
- Library versioning follows the standard `v<N>/` layout with `LIBAPI`, `LIBPATCH`, `LIBID`.
- Uses `pyright` instead of `mypy` — clean (0 errors, 0 warnings).

**Drifts from convention:**
- Library also published to PyPI (`charmlibs-interfaces-service-mesh`) — novel in the ecosystem; `lib/` remains source of truth but consumers import from PyPI, which is how Finding 1 arose.
- No `metadata.yaml` — uses only `charmcraft.yaml`, correct for Juju 3.6+.
- `ready-timeout` sleep-loop polling is unusual; most charms use `defer()`.
- No `upgrade_charm` handler, unlike most production charms.

## Tests

**Lint, static analysis, spell-check — all pass clean:**
- ruff (`tox -e lint`): all checks passed.
- pyright (`tox -e static`): 0 errors, 0 warnings, 0 informations; the custom `LIBPATCH`/`LIBAPI` bump check also passes.
- codespell: 1 finding (`lib/charms/istio_beacon_k8s/v0/service_mesh.py:678: defintion ==> definition`).

**Unit tests — 61 passed, 0 failed, 78% coverage** (confirmed via `tox -e unit`). Notable uncovered lines in `src/charm.py`:
- `174-198`: `_setup_proxy_pebble_service()` entirely untested
- `206, 210, 214, 218`: `_on_remove()` error paths
- `278`: non-leader path in `_sync_all_resources()`
- `289-311`: `_sync_waypoint_resources()` internals (KRM interaction mocked)
- `315, 337`: `_is_waypoint_ready()` return-False path and the RuntimeError crash path — untested because `_is_waypoint_deployment_ready` is always mocked to return True
- `438, 483-490, 501-503, 509-510, 516, 520, 524`: error paths in label handling and policy building
- `551`, `578`, `594`, `605, 609`: `_remove_labels()` error path, `_put_charm_on_mesh()`, `format_labels()`, library helper functions

**Scenario tests confirm the fix but not the deployed charm:**
- `test_sync_all_triggers_hpa_reconcile` (parametrized 1/3/5 planned units) — asserts exactly 2 resources (Gateway + HPA) with correct replica counts; passes on HEAD, confirming the HPA code works even though it isn't in the published charm.
- `test_on_remove_deletes_hpa_only_when_last_unit` (parametrized 0/1/2 planned units) — confirms the `planned_units() > 0` guard in HEAD's `_on_remove`.

**Test quality observations:**
- Integration tests assert concrete HTTP behaviour (200 vs 403 vs connection refused), not just `all_active` — a strength.
- `test_deploy_dependencies` uses `@pytest.mark.setup` and `@pytest.mark.abort_on_fail` for correct ordering.
- Some OpenTelemetry noise ("Already shutdown, dropping span") in output — harmless.
- Unregistered pytest marker `disable_lightkube_client_autouse` (not in `pyproject.toml`).
- Harness-based tests use a deprecated API (`PendingDeprecationWarning`) — should migrate to Scenario.

## Docs

**README** (885 bytes) is minimal — links to Charmhub but is missing deployment instructions, the dependency chain (Gateway API CRDs → istio-k8s → istio-beacon-k8s), config reference, and troubleshooting. Operators need external docs to deploy this successfully.

**Charmhub description** matches `charmcraft.yaml` summary. Channels `1/stable`–`1/edge` are all rev 74 (2026-06-09); `2/stable`–`2/edge` are all rev 63 (2026-02-05). Charm is unlisted in search results (open issue #164).

**CONTRIBUTING.md** has a good developer setup covering lint, static, unit, scenario, and integration tox environments.

**Terraform module** has a proper `terraform/README.md` with terraform-docs output, but the channel validation (`variables.tf:7-10`) requires `startswith(var.channel, "dev/")`, so the module cannot deploy the published charm — see Finding 15.

**Docs/reality mismatches:**
- README doesn't mention the Gateway API CRD prerequisite.
- `ready-timeout` config description says "charm will go into error state" — on Juju 4.x it never actually does.
- The published charm's non-leader status message isn't documented anywhere.
- Terraform module channel validation blocks deploying the published charm.
- No deployment guide explains the istio-k8s dependency chain.

## Open questions

1. **Does the charm recover if istio-k8s is deployed after the beacon?** Partially settled: in the same model, the beacon self-heals from its initial CRD-missing 404 crash once istio-k8s installs the CRDs. In a separate model, the crash loop is the unrecoverable RuntimeError path. Replacing RuntimeError with BlockedStatus+defer would make both cases self-heal.
2. **Does the published charm use `lightkube_extensions` or `canonical_service_mesh` KRM?** Settled — rev 74 uses `lightkube_extensions.batch.KubernetesResourceManager` (confirmed via `kubectl exec`; `canonical_service_mesh`/`charmlibs` absent from site-packages). HEAD uses `canonical_service_mesh`.
3. **What commit was rev 74 built from?** Unresolved — see Finding 8; no single commit matches all three observed behaviours.
4. **What causes the Juju 4.x agent-lost-on-scale-up bug?** Unresolved — reproduced twice, likely a Juju controller issue possibly exacerbated by the charm's heavy in-hook Kubernetes API calls.
5. **Is the `peers` relation intentionally unused?** Open — declared and handled but no peer data is read or written.
6. **Does the `canonical_service_mesh` 0.0.2 KRM (pinned in uv.lock) have the same `raise error` bug as 0.1.0 (in deps)?** Open — needs audit of both versions.
7. **What is the intended upgrade path from `1/edge` to `2/edge`?** Open — different relation endpoints make cross-track refresh fail outright; no migration path evident.
8. **Why did the Gateway get `Programmed: True` on Juju 3.6 without a local istio-k8s?** Settled — a previously-deployed istiod control plane (cluster-scoped, from an earlier Juju 4 deployment) was still running and processed the Gateway from any namespace.
9. **Will publishing HEAD resolve the service-mesh library mismatch (Finding 1)?** Likely — HEAD's `ServiceMeshProvider` includes `mesh_type` and scenario tests confirm compatibility with the newer library format, provided the published charm's dependencies are updated to match.
