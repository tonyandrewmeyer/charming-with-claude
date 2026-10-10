# kserve-operators

The kserve-operators repo packages four k8s charms for KServe ML model serving: `kserve-controller` (the long-established `InferenceService` controller), `kserve-llmisvc` (`LLMInferenceService` controller), `lws-controller` (`LeaderWorkerSet` controller), and `llm-integrator` (end-user LLM rendering charm). The three newer charms form the "LLM serving stack." The code is well-structured, well-typed (pyright: 0 errors on all four charms), and self-heals correctly from pod kills and liveness failures. But it has several critical defects: a cached-handler bug that silently stops config changes from reaching Kubernetes resources after the first reconcile; a readiness-publishing bug in kserve-controller that tells kserve-llmisvc the cluster is ready when it isn't (the correct pattern exists next door in kserve-llmisvc but wasn't applied); and the entire LLM serving stack is undeployable from charmhub because the sync relation between kserve-controller and kserve-llmisvc only exists in unreleased source. Add to that widespread lint debt, three of four charms' unit tests failing to import at all, an unconditional Pebble restart on every hook, and a still-open remove-application bug (#131). A maintainer should first fix the config-propagation bug and the sync-data readiness leak (both are correctness bugs with silent failure modes), then get a compatible kserve-controller/kserve-llmisvc pair onto a real channel before promoting the LLM stack any further.

| | |
|---|---|
| Repo | canonical/kserve-operators @ `9d257c9` (2026-07-23) |
| Charms | kserve-controller, kserve-llmisvc, lws-controller, llm-integrator |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4, kserve-controller@0.14/stable (rev 951), kserve-llmisvc@latest/edge (rev 40), lws-controller@latest/edge (rev 28), llm-integrator@latest/edge (rev 22) |
| Reviewed | 2026-08-18 |

## What it does

`kserve-controller` is the core KServe controller, managing `InferenceService` and `ClusterServingRuntime` CRDs. `kserve-llmisvc` manages the `LLMInferenceService` CRD and a metrics-proxy sidecar. `lws-controller` manages the `LeaderWorkerSet` CRD. `llm-integrator` is a rendering-only charm (no workload container) that creates a single `LLMInferenceService` CR from Juju config, gating on `kserve-llmisvc` readiness. All four are k8s charms with Pebble workload management and lightkube Kubernetes resource handlers.

## Deployment log

```
juju add-model rv-kserve --controller concierge-k8s-4
juju deploy kserve-controller --channel 0.14/stable --trust
# → rev 951, status: blocked "Please relate to istio-pilot:gateway-info" (expected)
# Pod: kserve-controller-0 Running 2/2, CRDs created
# Pebble service: inactive (charm is blocked, service not started)
# Hook sequence: install → leader-elected → config-changed → start → pebble-ready (~45s)

juju config kserve-controller deployment-mode=standard
# → blocked "Please set deployment-mode to either Serverless or RawDeployment" (deployed rev 951)

juju config kserve-controller deployment-mode=Serverless
# → blocked "Please relate to istio-pilot:gateway-info" (correct next step)

juju deploy kserve-llmisvc --channel latest/edge --trust
# → rev 40, blocked "Please relate to kserve-controller:kserve-controller"
# NOTE: 0.14/stable kserve-controller does NOT expose the kserve-controller sync relation
# that kserve-llmisvc requires. Integration is impossible without refreshing kserve-controller.

juju deploy lws-controller --channel latest/edge --trust
# → rev 28, goes active without any relations (correct — no required relations)

juju deploy llm-integrator --channel latest/edge --trust
# → rev 22, blocked "Please relate to kserve-llmisvc:kserve-llmisvc" (expected)

# Scale test: lws-controller
juju add-unit lws-controller
# → scaled to 2 units, both active

juju remove-unit lws-controller --num-units 1
# → Juju reports scale=1, but StatefulSet spec.replicas stays at 2
# → lws-controller-1 pod remains Running 1/2 (orphaned, never cleaned up)

# Failure injection: invalid deployment-mode
juju config kserve-controller deployment-mode=invalid-mode
# → BlockedStatus("Please set deployment-mode to either Serverless or RawDeployment")
# Validates config correctly (deployed rev 951 maps "invalid-mode" → invalid → BlockedStatus)

# Failure injection: invalid manager-config for lws-controller
juju config lws-controller manager-config="this is not yaml"
# → BlockedStatus("manager-config must be a YAML mapping")
# Debug-log confirmed: ERROR unit.lws-controller/0.juju-log Failed to handle <ConfigChangedEvent>
# with error: manager-config must be a YAML mapping
# Recovery confirmed after reverting config.

# juju refresh failure
juju refresh kserve-controller --channel latest/edge
# → downloaded rev 1392 but failed:
# "one or more of the provided endpoints 'gateway-metadata, ingress-gateway, ...' do not exist"
# The new edge has different relation endpoints from the old version.

# Additional deployments for integration testing:
juju deploy grafana-agent-k8s --channel 2/stable --trust
juju deploy loki-k8s --channel 2/stable --trust
juju deploy istio-pilot --channel 1.22/stable --trust
juju deploy knative-operator --channel latest/edge --trust
juju deploy knative-serving --channel latest/edge --trust
# → grafana-agent-k8s blocked (no metrics/logging/tracing provider)
# → loki-k8s active (after ~4 minutes)
# → istio-pilot active (after ~10 minutes)
# → knative-operator active (after ~5 minutes)
# → knative-serving active (after ~6 minutes)

# istio-pilot integration with kserve-controller
juju integrate kserve-controller:ingress-gateway istio-pilot:gateway-info
# → relation established successfully (interface: istio-gateway-info matches)
# → kserve-controller blocked on "Please relate to knative-serving:local-gateway" (Serverless mode)

# Switch to RawDeployment to avoid knative dependency
juju config kserve-controller deployment-mode=RawDeployment
# → kserve-controller immediately active
# → Pebble service "kserve-controller: active" confirmed in kserve-controller container

# loki-k8s integration
juju integrate lws-controller:logging loki-k8s:logging
juju integrate kserve-llmisvc:logging loki-k8s:logging
# → Both relations established, no errors

# kserve-llmisvc sync integration attempt (fails — rev 951 lacks sync relation)
juju integrate kserve-llmisvc:kserve-controller kserve-controller:kserve-controller
# → ERROR: no candidates for kserve-controller:kserve-controller: relation endpoint not found
# Confirmed for all published channels: 0.14/stable, 0.14/edge, 0.15/edge, 0.17/edge, latest/edge

# Failure injection: remove istio-pilot relation while kserve-controller is active
juju remove-relation kserve-controller:ingress-gateway istio-pilot:gateway-info
# → kserve-controller goes blocked "Please relate to istio-pilot:gateway-info" immediately
# Pebble service stays active (not stopped when charm blocks)
# Hooks fired: ingress-gateway-relation-departed, ingress-gateway-relation-broken
# Recovery: re-integrate → kserve-controller active within ~30s

# Failure injection: kill kserve-controller Pebble service
kubectl exec kserve-controller-0 -c kserve-controller -- pebble stop kserve-controller
# → Service went inactive
# → kserve-controller-pebble-check-failed hook fired
# → _on_event ran, _restart_controller_service() called
# → Service restarted, charm went maintenance then active
# Self-healing confirmed

# grafana-agent-k8s integration (metrics-endpoint)
juju integrate kserve-controller:metrics-endpoint grafana-agent-k8s:metrics-endpoint
# → Relation established successfully (prometheus_scrape interface)

# S3 integration attempt (fails — rev 951 lacks s3-credentials)
juju deploy s3-integrator --channel 2/stable --trust
juju integrate kserve-controller:object-storage s3-integrator:s3-integrator
# → ERROR: s3-integrator does not expose object-storage interface (it has s3-credentials)
# → rev 951 has object-storage but not s3-credentials

# kserve-llmisvc removal + cascade failure
juju remove-application kserve-llmisvc
# → kserve-llmisvc removed successfully
# → loki-k8s:logging-relation-departed hook failed with exit 1
# → loki-k8s went to error status (loki-k8s issue, not kserve)
```

## Observed behaviour

- **lws-controller maintenance→active lifecycle**: After a pod deletion+recreate (which fires `upgrade-charm` → `config-changed` → `pebble-ready`), the charm runs the full reconcile in `upgrade-charm` and `config-changed`, then `pebble-ready` completes. Total time from pod recreation to active: ~30 seconds. The `maintenance "Creating k8s resources"` status is correct during reconciliation, and `ready=true` is published correctly afterward.
- **Pebble readiness checks, threshold=3**: Both kserve-controller and lws-controller define `level: ready` checks with `threshold: 3` and `on-check-failure: restart`. kserve-controller's liveness probe failed once at ~07:14 UTC (container killed and restarted by Kubernetes); the readiness check then returned 418 ("I'm a teapot") until the webhook server finished initializing — normal during startup.
- **Loki log target to blocked grafana-agent-k8s**: The Pebble layer includes a log target pushing to `grafana-agent-k8s/0:3500`. Since grafana-agent-k8s is blocked, the endpoint is unreachable: `Cannot flush logs to target "grafana-agent-k8s/0": dial tcp 10.1.0.240:3500: connection refused`. Pebble logs the warning but continues working — graceful degradation, no functional impact.
- **Pod deletion causes `upgrade-charm`, not `install`**: Deleting the kserve-controller pod caused Kubernetes to recreate it, and Juju ran `upgrade-charm` because the application already existed. The charm's generic `_on_event` handles `upgrade-charm` identically to every other event; there is no dedicated `_on_upgrade_charm` handler.
- **Hook timing**: install → leader-elected → config-changed → start → pebble-ready completed in ~45s total.
- **Pebble service lifecycle**: `kserve-controller` service stays `inactive` while the charm is blocked, and starts immediately once the charm transitions to active (RawDeployment + istio-pilot); confirmed via `pebble services` in the workload container.
- **lws-controller lifecycle**: Goes `ActiveStatus` on first successful reconcile with no required relations. Scale-up works correctly.
- **lws-controller scale-down bug (confirmed live)**: After `juju remove-unit lws-controller/1`, the Kubernetes StatefulSet `spec.replicas` remained at 2. The `lws-controller-1` pod remained `Running 1/2` (charm container unhealthy, 502 probe failure), with no `deletionTimestamp` set. Juju eventually corrected the StatefulSet to 1 replica and the orphaned pod was garbage collected, but this took several minutes — a window of resource waste and confusion.
- **Failure injections**: bad `manager-config` YAML for lws-controller → `BlockedStatus("manager-config must be a YAML mapping")`, recovered on revert. Invalid `deployment-mode` for kserve-controller → `BlockedStatus`; valid values accepted.
- **Relation removal while running**: Removing `kserve-controller:ingress-gateway → istio-pilot:gateway-info` while active caused an immediate transition to `blocked "Please relate to istio-pilot:gateway-info"`. Both `ingress-gateway-relation-departed` and `ingress-gateway-relation-broken` hooks fired correctly. The Pebble service in the `kserve-controller` container **stays active** even after the charm blocks — it is not stopped on block. Re-integrating recovered the charm to `active` within ~30s.
- **Pebble service kill + self-healing**: `pebble stop kserve-controller` triggered the `kserve-controller-pebble-check-failed` hook; `_on_event` ran, called `_restart_controller_service()`, and the service restarted. Charm went `maintenance` then back to `active`. Self-healing confirmed.
- **Lowercase deployment-mode accepted**: `deployment-mode=rawdeployment` (lowercase) was accepted as valid by deployed rev 951 — charm went to `maintenance` and reconciled before hitting the (unrelated) missing-istio-pilot block. Only `Serverless`/`RawDeployment` (capitalized) are officially documented as accepted.
- **Logging integration**: `lws-controller` and `kserve-llmisvc` both integrate cleanly with `loki-k8s` over `loki_push_api`; no errors in debug-log.
- **grafana-agent-k8s metrics integration**: `kserve-controller:metrics-endpoint → grafana-agent-k8s:metrics-endpoint` (`prometheus_scrape`) integrated successfully; grafana-agent-k8s itself remains blocked on missing `grafana-cloud-config`/`send-remote-write`.
- **istio-pilot integration**: `kserve-controller:ingress-gateway → istio-pilot:gateway-info` (`istio-gateway-info`) integrates cleanly; kserve-controller correctly waits for gateway data then unblocks.
- **S3/object-storage integration gap**: `juju integrate kserve-controller:object-storage s3-integrator:s3-integrator` fails — s3-integrator provides `s3-credentials`, not `object-storage`. Deployed 0.14/stable has only `object-storage` (SDI). Operators cannot integrate S3 storage with the published 0.14/stable via the standard s3-integrator charm.
- **Knative stack**: `knative-operator` and `knative-serving` deploy and become active correctly (the latter waiting for the former's CRDs). In Serverless mode, kserve-controller correctly blocks waiting for `knative-serving:local-gateway`.
- **RawDeployment mode**: kserve-controller becomes active immediately with only the istio-pilot relation, without knative dependencies — correct behaviour.
- **kserve-controller pod restarted mid-reconcile**: Kubernetes events show the container was killed by its liveness probe (`HTTP probe failed with statuscode: 502`) at ~07:14 UTC. On restart, the readiness check returned 418 until ready; charm self-healed to `active` via the `pebble-check-failed` hook path.
- **`juju refresh` failure**: Upgrading from 0.14/stable (rev 951) to latest/edge (rev 1392) fails with an endpoint mismatch — the new edge added/dropped relations without backward compatibility.
- **Sync relation gap confirmed across all published channels**: Integration between kserve-llmisvc and kserve-controller's sync relation failed for rev 951 (0.14/stable), rev 1367 (0.14/edge), rev 1340 (0.15/edge), rev 1393 (0.17/edge), and rev 1392 (latest/edge). No published version of kserve-controller exposes the `kserve-controller:` provides relation.
- **llm-integrator removal**: Removed cleanly; no orphaned CRs in the namespace afterward.
- **kserve-llmisvc removal + loki-k8s cascade failure**: Removing kserve-llmisvc broke its logging relation to loki-k8s; loki-k8s's `logging-relation-departed` hook failed with exit code 1 (`rehash: warning: skipping ca-certificates.crt, it does not contain exactly one certificate or CRL`), and loki-k8s went to `error`. This is a loki-k8s issue, not a kserve issue, but demonstrates that removing a kserve charm can cascade into unrelated charms.
- **Update-status hooks**: Fire every ~5 minutes for all active charms; each re-runs the full `_on_event` reconciliation, including an unconditional Pebble restart and (for lws-controller) an unconditional config re-upload.
- **Open issue #527 confirmed**: `LLMInferenceService` stuck `Ready=False / WaitingForGateway` is active and tracked in the repo's open issues.

## Findings

### 1. Config changes do not propagate to Kubernetes resources after initial reconcile
- **Severity**: critical
- **Kind**: bug
- **Where**: `charms/llm-integrator/src/charm.py:204`; `charms/kserve-controller/src/charm.py:325`; `charms/kserve-llmisvc/src/charm.py:191`; `charms/lws-controller/src/charm.py:140` (all `@property` resource-handler accessors)
- **Evidence**: Each charm caches its `KubernetesResourceHandler` as `self._resource_handler = None` in `__init__`, then lazily creates it in a property:
  ```python
  @property
  def resource_handler(self):
      if not self._resource_handler:   # only creates if None
          self._resource_handler = KubernetesResourceHandler(
              field_manager=self._lightkube_field_manager,
              template_files=TEMPLATE_FILES,
              context=self._context,   # context snapshotted at creation time
          )
      return self._resource_handler
  ```
  `_on_event` never resets `self._resource_handler = None`, and `handler.apply()` renders manifests using the handler's stored context snapshot, not the current `_context` value. Changing `model-uri`, `runtime-image`, `storage-initializer-image`, `enable-prefill-decode` (llm-integrator), or `custom_images` (kserve-controller) has no effect until the charm process restarts.
- **Why it matters**: llm-integrator is a pure config-to-CR renderer; any config change after initial deploy silently fails to update the CR, and the workload keeps serving stale config. The bug self-heals on `juju restart-unit`, but that is not a reasonable workaround for routine config changes.
- **Fix**: Reset `self._resource_handler = None` at the top of `_on_event`, or pass `context=self._context` explicitly to `handler.apply()`/`handler.render_manifests()`.
- **Linter rule**: not mechanically checkable — requires understanding the chisme KRH lifecycle.

### 2. kserve-controller publishes `ready=true` to llmisvc sync even when ClusterServingRuntimes failed to apply
- **Severity**: critical
- **Kind**: bug
- **Where**: `charms/kserve-controller/src/charm.py:791–825`
- **Evidence**: In `_on_event()`, the inner `try/except ApiError` block handles two recoverable error types ("connect: connection refused" / "no endpoints available") by setting `MaintenanceStatus`, then **falls through** to publish readiness:
  ```python
  try:
      self.cluster_runtimes_resource_handler.apply()   # may raise ApiError
      self.model.unit.status = ActiveStatus()
  except ApiError as e:
      if e.status.code == 500 and "connect: " in e.status.message:
          self.model.unit.status = MaintenanceStatus(msg)   # recoverable
      elif "no endpoints available" in e.status.message:
          self.model.unit.status = MaintenanceStatus(msg)   # recoverable
      else:
          raise GenericCharmRuntimeError(...)

      self._publish_llmisvc_sync_data(ready=True)   # BUG: still publishes ready=true
  except ErrorWithStatus as err:
      self._publish_llmisvc_sync_data(ready=False)
  ```
  Both recoverable branches reach line 825 and publish `ready=true` even though `apply()` raised and ClusterServingRuntimes were never applied. Only the third (`else: raise`) path correctly avoids publishing.
- **Why it matters**: kserve-llmisvc reads the sync relation's `ready` flag to decide when to become active and reconcile. If kserve-controller reports ready before its own CRs are applied, kserve-llmisvc reconciles prematurely against a cluster that isn't ready.
- **Contrast**: `kserve-llmisvc` does this correctly at `charms/kserve-llmisvc/src/charm.py:395–418` — `ready=true` is only published after `apply()` succeeds, and both error branches explicitly publish `ready=false`.
- **Fix**: Publish `ready=False` for the recoverable `ApiError` cases; only publish `ready=True` inside the success path.
- **Linter rule**: not mechanically checkable.

### 3. LLM stack sync relation never published — entire LLM serving stack undeployable from charmhub
- **Severity**: critical
- **Kind**: bug (integration gap)
- **Where**: `charms/kserve-controller/metadata.yaml:29` (local source only); absent from all published channels
- **Evidence**: The local `metadata.yaml` defines:
  ```yaml
  provides:
    kserve-controller:
      interface: kserve-controller-sync
  ```
  Added in commit `9d257c9` (2026-07-23, "Add KServe LLM serving stack #517"). No published channel of kserve-controller (0.14/stable rev 951 through 0.17/edge rev 1393) includes this `provides` section. `juju integrate kserve-llmisvc:kserve-controller kserve-controller:kserve-controller` fails with "no candidates ... relation endpoint not found" against every published channel tested.
- **Why it matters**: `kserve-llmisvc`, `lws-controller`, and `llm-integrator` cannot be integrated with any published version of kserve-controller — the LLM serving stack requires unreleased local source.
- **Fix**: Publish kserve-controller with the `kserve-controller:` provides relation to a stable or edge channel, then point kserve-llmisvc's metadata at that channel.
- **Linter rule**: not mechanically checkable.

### 4. lws-controller StatefulSet replicas not updated on scale-down — orphaned pod
- **Severity**: high
- **Kind**: bug
- **Where**: Juju/charm interaction on `juju remove-unit`; StatefulSet `spec.replicas` not updated
- **Evidence**: After scaling to 2 units then `juju remove-unit lws-controller --num-units 1`: Juju reports scale=1, but `kubectl get statefulset lws-controller` shows `spec.replicas: 2`; `lws-controller-1` remains `Running 1/2` with no `deletionTimestamp`. Debug-log confirms the stop hook ran at 08:29:52 but the StatefulSet replica count was not updated at that time. Juju eventually corrected the StatefulSet after several minutes and the orphaned pod was garbage collected.
- **Why it matters**: Scale-down appears to succeed in Juju's view but leaves an orphaned, unhealthy pod consuming resources for several minutes.
- **Fix**: Investigate whether the delay is in Juju's k8s provider StatefulSet reconciliation or in the charm's stop/remove hook path, and close the timing gap.
- **Linter rule**: not mechanically checkable (requires live cluster test).

### 5. Issue #131 (kserve-controller fails to remove) — still active
- **Severity**: high
- **Kind**: bug (lifecycle)
- **Where**: `charms/kserve-controller/src/charm.py:851–873` (`_on_remove`); `charms/kserve-controller/src/charm.py:856–858` (handler init); `charms/kserve-controller/src/charm.py:323` (lazily-created `k8s_resource_handler` property)
- **Evidence**: Issue #131 (filed 2024-07-10) reports `juju remove-application kserve-controller` failing when the istio-pilot relation is absent. `_on_remove` calls `_delete_managed_resources([k8s_resource_handler, cm_resource_handler])`, which calls `handler.render_manifests()`. Both handlers are lazily created properties; if the charm was blocked before `_on_event` ever ran successfully, the underlying `_k8s_resource_handler`/`_cm_resource_handler` are `None`, and `_delete_managed_resources` would call `render_manifests()` on `None`, raising `TypeError`. (Separately confirmed: the `_context` property does not include gateway data, so where a handler *was* created, CRD manifests render fine without it — the failure mode is specifically the never-initialized-handler case.)
- **Why it matters**: Operators cannot cleanly remove kserve-controller if it never ran a successful `_on_event` (e.g., never had a working istio relation), blocking model teardown and namespace cleanup.
- **Fix**: Guard `_on_remove` against uninitialized handlers — e.g., `if self._k8s_resource_handler is not None` before calling `_delete_managed_resources`, or wrap `render_manifests()` in a try/except.
- **Linter rule**: not mechanically checkable without runtime tracing.

### 6. Published 0.14/stable kserve-controller rejects modern deployment-mode values
- **Severity**: high
- **Kind**: bug (deployed artifact)
- **Where**: deployed kserve-controller code, 0.14/stable rev 951
- **Evidence**: Setting `deployment-mode=knative` or `deployment-mode=standard` results in `BlockedStatus("Please set deployment-mode to either Serverless or RawDeployment")`. Only the deprecated `Serverless`/`RawDeployment` names are accepted on this revision; the current repo HEAD has aliasing code for both old and new names with deprecation warnings.
- **Why it matters**: Operators following current docs or using the intended modern config values hit a confusing block on the stable track.
- **Fix**: Backport the aliasing code to 0.14/stable, or promote a newer revision with the fix to the stable channel.
- **Linter rule**: not mechanically checkable (deployed artifact mismatch).

### 7. `juju refresh` to latest/edge fails with endpoint mismatch
- **Severity**: medium
- **Kind**: bug
- **Where**: relation-schema compatibility between 0.14/stable and latest/edge channels
- **Evidence**: `juju refresh kserve-controller --channel latest/edge` downloads rev 1392 but fails: `one or more of the provided endpoints "gateway-metadata, ingress-gateway, ..." do not exist`. The new edge adds `kserve-controller`, `provide-cmr-mesh`, `require-cmr-mesh`, `s3-credentials` and drops `service-mesh`; the old revision has `service-mesh` but lacks the new endpoints.
- **Why it matters**: In-place upgrade from 0.14/stable to latest/edge is impossible without first removing all existing relations — a destructive operation.
- **Fix**: Document the upgrade path explicitly, or maintain backward-compatible endpoints across the transition.
- **Linter rule**: not mechanically checkable.

### 8. S3/object-storage integration gap in deployed 0.14/stable
- **Severity**: medium
- **Kind**: bug (integration gap)
- **Where**: deployed kserve-controller (rev 951, 0.14/stable); absent from published channel
- **Evidence**: `juju integrate kserve-controller:object-storage s3-integrator:s3-integrator` fails: s3-integrator provides `s3-credentials`, not `object-storage`. Deployed 0.14/stable has only `object-storage` (SDI); local source has both. Operators cannot use the standard s3-integrator charm with the published 0.14/stable.
- **Why it matters**: S3 storage integration is a core KServe use case, and the published stable version can't do it with the standard integrator charm.
- **Fix**: Promote a kserve-controller revision with `s3-credentials` to the stable track.
- **Linter rule**: not mechanically checkable.

### 9. Pebble service unconditionally restarted on every hook (`is_running()` return value discarded)
- **Severity**: medium
- **Kind**: bug (logic error) / performance
- **Where**: `charms/kserve-controller/src/charm.py:1107` (call), `charms/kserve-controller/src/charm.py:785` (`_on_event` call site); `charms/kserve-llmisvc/src/charm.py:646`, `charms/kserve-llmisvc/src/charm.py:385`; `charms/lws-controller/src/charm.py:458`
- **Evidence**: In all three controller charms, `_restart_controller_service()` calls `is_running()` but discards the return value, then unconditionally calls `container.restart()`:
  ```python
  try:
      self.controller_container.get_service(self._controller_container_name).is_running()  # return value ignored
  except ModelError:
      log.info("Service not found, nothing to restart.")
      return
  self.controller_container.restart(self._controller_container_name)  # always called
  ```
  `update_layer` (from `charmed_kubeflow_chisme`) correctly compares old vs new layer before calling `replan()`, but this method ignores that and restarts regardless. Debug-log confirmed: after removing the istio-pilot relation, the `ingress-gateway-relation-broken` hook ran `_on_event` and restarted the Pebble service even though the layer hadn't changed. This fires on every `config-changed`, `relation-*`, and `update-status` (~5 min) hook.
- **Why it matters**: Gratuitous brief downtime on every hook for a controller manager that should be stable.
- **Fix**: Skip `restart()` if `is_running()` is already `True`, or condition the restart on the layer-diff result from `update_layer`.
- **Linter rule**: not mechanically checkable without runtime tracing.

### 10. kserve-controller has no `upgrade-charm` handler — no graceful upgrade path
- **Severity**: medium
- **Kind**: bug (upgrade gap)
- **Where**: `charms/kserve-controller/src/charm.py:210` (generic `self.framework.observe(event, self._on_event)`); no `on.upgrade_charm` observer
- **Evidence**: All events, including `upgrade-charm`, route through the same `_on_event`. There is no dedicated handler to distinguish a fresh install from a `juju refresh`. The `juju refresh` from 0.14/stable to latest/edge failed outright on an endpoint mismatch (finding 7), so this gap was not directly exercised, but any refresh that does succeed will follow the same reconcile path as a fresh install.
- **Why it matters**: Upgrade-specific concerns (CRD schema migration, webhook config changes) can't be handled differently from a fresh install.
- **Fix**: Add `self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)` and implement upgrade-specific handling.
- **Linter rule**: not mechanically checkable.

### 11. No actions defined for any charm
- **Severity**: medium
- **Kind**: ux
- **Where**: all four charms — no `actions.yaml` files
- **Evidence**: `find . -name actions.yaml` returns nothing; `juju actions kserve-controller` returns nothing.
- **Why it matters**: Operators cannot trigger manual operations (cert regeneration, resource cleanup, status refresh) without direct Kubernetes access.
- **Fix**: Define actions such as `regenerate-certs`, `sync-resources`, `show-managed-resources`.
- **Linter rule**: not mechanically checkable.

### 12. kserve-llmisvc, llm-integrator, and lws-controller unit tests cannot run — broken conftest
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py` in kserve-llmisvc, llm-integrator, and lws-controller
- **Evidence**: All three conftest.py files import `from ops.testing import Container, Context, Relation, State` (llm-integrator line 18, kserve-llmisvc line 23, lws-controller line 19). The installed `ops` (3.6.0) does not export `Context` from `ops.testing`, and `ops-scenario` is not installed. Every test file in these three charms fails at import time with `ImportError: cannot import name 'Context' from 'ops.testing'`. Even lws-controller's `test_certs.py`, which doesn't directly use Scenario, fails because the shared conftest fails to load first. 100% of these three test suites are blocked.
- **Why it matters**: The three newest charms have zero passing unit tests.
- **Fix**: Wrap the Scenario imports in `pytest.importorskip("ops_scenario")`, or install `ops-scenario` in the test environment.
- **Linter rule**: not mechanically checkable.

### 13. kserve-controller unit tests: 19/53 fail due to uninitialized Harness
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `charms/kserve-controller/tests/unit/test_charm.py:~73`
- **Evidence**: `harness = Harness(KServeControllerCharm)` without `meta`/model name raises `ValueError: Both model_name and app_name must be at least 1 character long.` in 19/53 tests. Failures cover install, remove, controller-ready, restart-controller-service, deployment-mode validation, gateway relations, s3 credentials, and storage relations — the core reconcile paths. The 34 passing tests cover auxiliary functionality (metrics, logging, certs, gateway/storage context generation).
- **Why it matters**: The core reconcile loop is effectively untested at the unit level.
- **Fix**: Pass `meta=open("metadata.yaml").read()` to `Harness()`, or centralize a fixture that initializes the harness with metadata.
- **Linter rule**: not mechanically checkable.

### 14. kubernetes_service_patch v1 library deprecated — removal deadline October 2025
- **Severity**: low
- **Kind**: bug (dependency)
- **Where**: `charms/kserve-controller/src/charm.py:38` (import), `charms/kserve-controller/src/charm.py:233` (instantiation)
- **Evidence**: Debug-log on every hook: `WARNING: The kubernetes_service_patch v1 library is DEPRECATED and will be removed in October 2025. ... ops.Unit.set_ports functionality should be used instead.`
- **Why it matters**: After removal, kserve-controller will fail to import until updated.
- **Fix**: Replace `KubernetesServicePatch` with `ops.Unit.set_ports`.
- **Linter rule**: not mechanically checkable (external library deprecation).

### 15. Pebble layer `level: ready` checks with threshold=3 — confusing startup behaviour
- **Severity**: low
- **Kind**: ux
- **Where**: `charms/kserve-controller/src/charm.py:194` (`_controller_pebble_layer`); `charms/lws-controller/src/charm.py:186`
- **Evidence**: Both charms define `level: ready`, `threshold: 3`, `on-check-failure: restart` checks. During startup, `/readyz` returns 418 ("I'm a teapot" — cert not yet loaded) until the webhook server is ready; with a 10s interval this adds ~30s before restart/settle.
- **Why it matters**: Operators see `maintenance` during this normal startup window and may mistake it for a failure.
- **Fix**: Add a longer initial-delay startup probe, or raise the threshold to account for startup time.
- **Linter rule**: not mechanically checkable.

### 16. lws-controller uploads manager-config on every update-status hook
- **Severity**: low
- **Kind**: performance
- **Where**: `charms/lws-controller/src/charm.py:216` (`_upload_manager_config`), called unconditionally from `_on_event`
- **Evidence**: `_upload_manager_config` pushes the config file on every hook, including `update-status` (~5 min), regardless of whether the content changed, and triggers a Pebble restart afterward via the unconditional restart path (finding 9).
- **Why it matters**: Unnecessary I/O and repeated service restarts every 5 minutes even when nothing changed.
- **Fix**: Compare new config against current file content before pushing; only push/restart on change.
- **Linter rule**: not mechanically checkable without runtime tracing.

### 17. `cert-gen-*` cleanup glob in certs.py matches no files
- **Severity**: low
- **Kind**: bug (dead code)
- **Where**: `charms/kserve-controller/src/certs.py:94`
- **Evidence**: `for file in tmp_path.glob("cert-gen-*"): file.unlink()` — generated files are `ca.key`, `ca.crt`, `ca.srl`, `server.key`, `server.csr`, `cert.pem`, none matching `cert-gen-*`. No-op loop.
- **Why it matters**: No functional impact (temp dir is cleaned by the context manager regardless), but misleading.
- **Fix**: Remove the dead loop.
- **Linter rule**: not mechanically checkable.

### 18. 487 ruff violations in charm source code
- **Severity**: low
- **Kind**: lint
- **Where**: all four charm source trees
- **Evidence**: `ruff check`: kserve-controller 232, kserve-llmisvc 165, lws-controller 81, llm-integrator 9 — total 487. Key rules: `I001` (import order, all four), `UP035`/`UP006`/`UP045` (deprecated typing generics, kserve-controller/kserve-llmisvc), `RUF013` (implicit Optional, lws-controller/kserve-llmisvc), `RUF100` (unused noqa), `TRY201` (bare raise preferred), `SIM102` (nested if), `RUF015` (single-element slice), `EXE001` (shebang in non-executable file).
- **Fix**: `ruff check --fix` resolves most of these automatically.
- **Linter rule**: `I001`, `UP006`, `UP035`, `UP045`, `RUF013`, `RUF100`, `TRY201`, `SIM102`, `RUF015`, `EXE001` — all mechanically checkable.

### 19. 3,362 ruff violations in bundled library code
- **Severity**: low
- **Kind**: lint
- **Where**: `charms/kserve-controller/lib/`
- **Evidence**: Bundled libraries use deprecated `typing.Dict`/`List`/`Set`/`Type`, `Optional[...]`, `List[...]` throughout — 3,362 violations total.
- **Fix**: Update libraries to modern Python 3.9+ typing syntax.
- **Linter rule**: `UP006`, `UP007`, `UP035`, `UP039`, `UP045` — mechanically checkable.

### 20. codespell: "UpToDate" vs "up-to-date" in Jinja2 template
- **Severity**: nit
- **Kind**: lint
- **Where**: `charms/kserve-controller/src/templates/crd_manifests.yaml.j2:28445,28448`
- **Evidence**: `codespell` flags `UpToDate ==> up-to-date`.
- **Fix**: Lowercase/hyphenate (verify it isn't a Kubernetes API enum value first — if so, mark as a false positive rather than fixing).
- **Linter rule**: mechanically checkable with codespell.

## Worth copying

- **llm-integrator status derivation** (`_llm_isvc_status()`): reads the actual CR status and derives charm status from it with a clear `Ready=True/False/Unknown` → `Active/Blocked/Waiting` mapping. (`charms/llm-integrator/src/charm.py:287`)
- **kserve-llmisvc CRD-first teardown** (`_delete_crds_and_wait`, `_delete_base_resources_and_wait`): handles CRD→CR cascade deletion ordering and blocks until resources are actually gone, avoiding orphaned webhooks. (`charms/kserve-llmisvc/src/charm.py:468`)
- **kserve-llmisvc sync data publishing**: only publishes `ready=true` after the scheduler config is successfully applied, and `ready=false` in all exception paths — the correct readiness contract, contrasted with finding 2. (`charms/kserve-llmisvc/src/charm.py:395–418`)
- **lws-controller finalizer-safe removal**: same CRD-first pattern as kserve-llmisvc. (`charms/lws-controller/src/charm.py:276`)
- **lws-controller cert generation guard**: `_gen_certs_if_missing()` only regenerates when an attribute is missing. (`charms/lws-controller/src/charm.py:296`)
- **metrics-proxy pebble layer with `can_connect()` guard** in kserve-llmisvc's `_on_event()`. (`charms/kserve-llmisvc/src/charm.py:395`)
- **lws-controller config validation**: validates manager-config YAML structure, raising an actionable `BlockedStatus`. (`charms/lws-controller/src/charm.py:400`)
- **Deployment mode aliasing**: accepting `RawDeployment`/`Serverless` while warning and translating is a good backward-compatibility pattern — though it has not yet reached the stable channel (finding 6). (`charms/kserve-controller/src/charm.py:247`)

## Common-practice notes

- All four charms use ops 2.x/`charmed_kubeflow_chisme` patterns; llm-integrator and kserve-llmisvc use newer Scenario-style testing (currently unrunnable — finding 12).
- Libraries under `lib/charms/<name>/v<N>/` are named correctly and versions are consistent across charms (`loki_k8s/v1` LIBPATCH 13 identical MD5 in all three; kserve-controller additionally bundles `istio_beacon_k8s/v0` LIBPATCH 16, `istio_pilot/v0` LIBPATCH 4, `prometheus_k8s/v0` LIBPATCH 47, `observability_libs/v1` LIBPATCH 13, `resource_dispatcher/v0` LIBPATCH 1).
- Self-signed certs are generated at `__init__` and stored in `StoredState` in all three controller charms — appropriate for immutable certs.
- The lazy-property KRH-caching pattern is used consistently across charms, but the cached-context issue (finding 1) means the pattern is currently unsafe for config-driven rendering.
- Terraform modules exist for all four charms but kserve-controller's does not expose `deployment-mode` or `custom_images` — a gap for IaC users.
- Test strategy is split by design (Harness for kserve-controller, Scenario for the newer three, pytest-operator integration tests for kserve-controller) — the right architecture, but all three approaches are currently broken or partial (findings 12, 13).
- `poetry` build with separate `poetry-deps`/`charm-poetry` charmcraft parts — non-standard vs. the usual `poetry` charmcraft plugin.
- Test environment: `concierge.yaml` specifies Juju 3.6, k8s 1.32; the review used concierge-k8s-4 (Juju 4.0.12) — backward-compatible.
- `renovate.json` has a broken preset (issue #384, invalid JSON); Renovate has stopped creating PRs.

## Tests

- **kserve-controller**: 34/53 unit tests pass; 19 fail with `ValueError: Both model_name and app_name must be at least 1 character long` from an uninitialized `Harness` (finding 13). Failures cover install, remove, controller-ready, restart, deployment-mode validation, gateway relations, s3 credentials — the critical reconcile paths.
- **llm-integrator, kserve-llmisvc, lws-controller**: 0% of unit tests run — shared conftest import failure (finding 12).
- **Ruff**: 487 violations in charm source (mechanically fixable), 3,362 in bundled library code.
- **codespell**: 2 issues, both the same `UpToDate` occurrence in `crd_manifests.yaml.j2`.
- **pyright**: all four charms pass with 0 errors (`PYTHONPATH=src:lib pyright src/charm.py`).
- **Integration tests**: present for kserve-controller (ambient, object-storage, S3), lws-controller, and the full bundle. Not run in this review — they require a full cluster with istio, knative, storage, and S3.
- **CI**: each charm has its own `tox.ini`; `concierge.yaml` sets up Juju 3.6 and k8s 1.32 for testing.

## Docs

- Root `README.md`: getting-started guide for Standard/Knative modes, pre-requisites, and a sklearn example; no docs for the LLM stack.
- `charms/kserve-controller/README.md`: one paragraph linking to discourse.
- `charms/llm-integrator/README.md` and `charms/kserve-llmisvc/README.md`: empty, no usage docs.
- `charms/lws-controller/README.md`: minimal, describes what it is only.
- `config.yaml`: all four charms have well-documented `description:` fields per config option.
- Charmhub descriptions: kserve-controller has a full description; kserve-llmisvc and llm-integrator have minimal one-line descriptions.
- No `docs/` directory in the repo root.

## Open questions

- Whether the lws-controller StatefulSet scale-down delay (finding 4) is a Juju k8s-provider timing issue or something the charm should compensate for.
- Whether issue #131's failure mode is exactly the never-initialized-handler `TypeError` described in finding 5, or also involves the ConfigMap-handler path specifically — not confirmed live in this review, only from code reading.
- Whether promoting a newer kserve-controller revision to stable (to fix findings 3, 6, 8) is blocked by other unreleased changes that haven't been reviewed here.
- Whether `ops-scenario` can simply be added to the test dependencies to unblock all three broken Scenario-based test suites (finding 12), or whether the tests themselves need updating for a newer Scenario API.
