# kubeflow-profiles-operator

A k8s charm managing Kubeflow Profile CRs and per-user namespaces, running `profile-controller` and `kfam` as Pebble services, with Istio mesh integration, Prometheus metrics, and Velero backup support. The code uses modern ops patterns and is generally clean, but has two critical lifecycle bugs that will hit any real operator: `juju refresh` crashes on upgrade (recovers automatically, but with an opaque error), and `juju remove-application` leaves the CRD and Kubernetes service behind permanently because the `remove` hook never fires on Kubernetes. On top of that, config validation runs unsafely inside `__init__`, several exception types escape the main event handler causing opaque hook failures, the `ingress` relation is declared but never implemented, and the charm has no `relation_broken` observer of its own. A maintainer should fix the remove-application resource leak first (move cleanup to the `stop` hook), then move config-dependent validation out of `__init__`.

| | |
|---|---|
| Repo | canonical/kubeflow-profiles-operator @ `ae75247` (2026-06-01) |
| Charms | kubeflow-profiles |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.12), latest/edge rev 882 (local HEAD `ae75247`, 1 commit ahead); refreshed to 1.10/edge rev 883; also tested on concierge-k8s-3 (Juju 3.6.25) |
| Reviewed | 2026-08-23 |
| Also tested | traefik-k8s ingress relation (hooks fire, no-op); grafana-agent-k8s metrics relation add/remove (graceful); loki-k8s logging relation add/remove (Pebble log target not cleaned up); `juju refresh` to rev 883 — crashed with `KeyError` then recovered; `juju remove-application` — left CRD and service behind; unit tests: 19/19 pass |

## What it does

Kubeflow Profiles and Access Management charm. Manages the `Profile` CRD and per-user namespaces with security-policy labels, runs `profile-controller` and `kfam` workloads as Pebble services, integrates with the service mesh for ambient or sidecar mode, exposes a `kubeflow-profiles` relation, provides Prometheus metrics at ports 8080/8081, and supports Velero backup of profile resources and user workloads. Relations: `kubeflow-profiles` (provides), `logging` (loki, optional), `ingress` (optional, unimplemented), `service-mesh` (optional), `profiles-backup-config` and `user-workloads-backup-config` (Velero).

## Deployment log

```
# === Model rv-kfp (first deploy) ===
juju add-model rv-kfp -c concierge-k8s-4
juju deploy kubeflow-profiles --channel latest/edge --trust
→ Deployed rev 882, pod initialising

kubectl -n rv-kfp get pods  # pod reached 3/3 Running in ~90s
juju status → active after ~2min

# Config propagation
juju config security-policy=baseline  # maintenance→active, namespace-labels.yaml updated
→ Same behavior on concierge-k8s-3 (Juju 3.6.25)

# Scale test
juju scale-application kubeflow-profiles 2  # unit 1 → WaitingStatus("Waiting for leadership")
juju scale-application kubeflow-profiles 1  # unit 1 terminated/lost

# Pod restart
kubectl delete pod kubeflow-profiles-0  # recreated by StatefulSet
→ Recovery hooks: upgrade-charm → config-changed → start → kfam-pebble-ready → profiles-pebble-ready
→ ActiveStatus restored in ~30s

# grafana-agent-k8s (metrics)
juju deploy grafana-agent-k8s --channel 0.40/edge --trust
juju relate kubeflow-profiles:metrics-endpoint grafana-agent-k8s
→ stayed active; relation data: scrape_targets=["*:8080", "*:8081"], alert_rules with KfamDown/ProfilesDown

# loki-k8s (logging)
juju deploy loki-k8s --channel 2/beta --trust
juju relate kubeflow-profiles:logging loki-k8s
→ Pebble log-targets confirmed pointing to loki-k8s endpoint
juju remove-relation kubeflow-profiles:logging loki-k8s
→ logging-relation-broken fired; "No Loki endpoints available" logged
→ BUT Pebble log-target still present in container plan (see findings)

# === Refresh ===
timeout 60 juju refresh kubeflow-profiles --channel 1.10/edge -m rv-kfp
→ upgrade-charm triggered; charm went error: "hook failed: config-changed"
→ Traceback: KeyError: 'istio-gateway-namespace' in __init__ (rev 883 code)
→ Juju retried automatically; maintenance ("K8S resources created") then ActiveStatus
→ Recovery time: ~20s

# === remove-application ===
juju add-model rv-kfp3 -c concierge-k8s-4
juju deploy kubeflow-profiles --channel 1.10/edge --trust --model rv-kfp3
→ Active in ~90s
timeout 90 juju remove-application kubeflow-profiles -m rv-kfp3 --force --no-wait
→ Model became empty immediately
→ CRD profiles.kubeflow.org STILL PRESENT after removal (kubectl confirmed)
→ Service kubeflow-profiles STILL PRESENT after removal
→ Debug log: only `stop` hook fired at 12:55:34, no `remove` hook ever fired
→ `_on_remove` (src/charm.py:412) never called on Kubernetes

# === Model rv-kfp2 (fresh deploy) ===
juju add-model rv-kfp2 -c concierge-k8s-4
juju deploy kubeflow-profiles --channel latest/edge --trust --model rv-kfp2
→ Deployed rev 882, active in ~90s

# traefik-k8s (ingress — declared but not implemented)
juju deploy traefik-k8s --channel 1.0/edge --trust --model rv-kfp2
juju integrate kubeflow-profiles:ingress traefik-k8s --model rv-kfp2
→ traefik-k8s active; ingress-relation-changed hook fired (confirmed in debug-log)
→ No Ingress/IngressClass created; kubeflow-profiles stayed active throughout
→ No ingress provider code in src/charm.py (grep "ingress" → no matches)

# grafana-agent-k8s metrics relation removal
juju deploy grafana-agent-k8s --channel 0.40/edge --trust --model rv-kfp2
juju integrate kubeflow-profiles:metrics-endpoint grafana-agent-k8s --model rv-kfp2
→ relation established, both active
juju remove-relation kubeflow-profiles:metrics-endpoint grafana-agent-k8s --model rv-kfp2
→ metrics-endpoint-relation-broken fired on kubeflow-profiles (confirmed in debug-log)
→ kubeflow-profiles stayed active throughout (no relation_broken observer — hook is a no-op)

# Velero not tested: velero/velero-k8s charms not available on charmhub in this environment
```

## Observed behaviour

- Deploy time: ~2 minutes to active from pod pull/start.
- Hook sequence: install → leader-elected → config-changed → start → kfam-pebble-ready → profiles-pebble-ready.
- `config-changed` fires **two dispatches** per `juju config` call (ops batching `service_patcher._patch` and `_on_event` into sequential runs); full reconciliation runs twice per config change.
- Config propagation: after `security-policy=baseline`, Pebble layer and `namespace-labels.yaml` re-rendered within ~10s.
- Invalid config: `port=-1` → `BlockedStatus("Input should be greater than or equal to 1024...")`; `port=99999` → `BlockedStatus("Input should be less than or equal to 65535...")`; `security-policy=invalid` → `BlockedStatus("Input should be 'privileged', 'baseline' or 'restricted'...")`. Messages are clear. `port=invalid` rejected at Juju CLI level before reaching the charm.
- `restricted` security policy is accepted by the pydantic model and results in `ActiveStatus`, though the config description only mentions `privileged`/`baseline` — mismatch confirmed (see findings).
- Failure — pod restart: automatic recovery, `upgrade-charm → config-changed → start → kfam-pebble-ready → profiles-pebble-ready`, ActiveStatus in ~30s.
- Failure — workload process killed: Pebble health check (period 30s, threshold 3) auto-restarted the process within the window; Juju status stayed active throughout.
- Failure — relation removal: `logging-relation-broken` handled gracefully by the charm (status stays active) but the Pebble log target for Loki is **not** removed (see findings). `metrics-endpoint-relation-broken` fires and charm stays active — handled as a no-op since there's no `relation_broken` observer.
- `update-status` fires every ~5 minutes; the deprecated `KubernetesServicePatch` re-patches the K8S service on it. The charm itself has no `on_update_status` handler.
- Juju 3.6 vs 4.0: identical behavior — same hook sequence, same statuses, same failure modes.
- Scale up: unit 1 (non-leader) correctly reached `WaitingStatus("Waiting for leadership")`. Scale down: unit terminated cleanly.
- Ingress relation: `ingress-relation-changed` fired (confirmed via `juju debug-log`) but is a no-op — no Ingress/IngressClass created, traefik-k8s stayed active and unaware.
- No actions defined: `actions.yaml` absent, no `on_action_*` handlers, no `framework.observe(self.on.*action*...)` calls.
- `juju refresh` crash and recovery: refreshed rev 882→883. First `config-changed` after download crashed with `KeyError: 'istio-gateway-namespace'` in `__init__` at `src/charm.py:61`, propagating from the `istio_gateway_namespace` property at `src/charm.py:173` (`return self.model.config["istio-gateway-namespace"]`). The config option has a default of `"kubeflow"` in `config.yaml`; the `KeyError` implies `self.model.config` returned an incomplete dict during that specific hook dispatch. Juju retried automatically; second attempt succeeded, charm reached maintenance ("K8S resources created") then Active. Recovery ~20s. This is a non-deterministic crash on upgrade with an opaque error message.
- `juju remove-application` resource leak: after `remove-application --force --no-wait`, the CRD `profiles.kubeflow.org` and the `kubeflow-profiles` service were confirmed still present in the cluster. Debug log shows only `stop` fired — `remove` was never dispatched. `_on_remove` (`src/charm.py:412`) is registered at `src/charm.py:128` but never called on Kubernetes: in Juju 4.x on k8s, only `stop` fires during application removal. Complete resource leak of everything the charm created.
- Velero relation not tested: `velero`/`velero-k8s` charms unavailable on charmhub in this environment.

## Findings

### `juju remove-application` leaks all Kubernetes resources (CRD, service) — `remove` hook never fires on Kubernetes

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:128` (`self.framework.observe(self.on.remove, self._on_remove)`), `src/charm.py:412` (`_on_remove`)
- **Evidence**: After `juju remove-application kubeflow-profiles --force --no-wait` on Kubernetes (Juju 4.0.12): `kubectl get crd profiles.kubeflow.org -n rv-kfp3` still returns the CRD (CREATED AT: 2026-08-23T00:21:17Z); `kubectl get service kubeflow-profiles -n rv-kfp3` still returns the service. Debug log shows `stop` fired at 12:55:34 but no `remove` hook was ever dispatched. `_on_remove` is correctly registered but in Juju 4.x on Kubernetes only `stop` is dispatched during application removal — `remove` is never called.
- **Impact**: Removing the charm leaves the `profiles.kubeflow.org` CRD and the `kubeflow-profiles` ClusterIP service behind in the cluster. The CRD can block reinstallation on API-version drift; `juju remove-application` reports success while resources leak silently.
- **Fix**: Move the k8s resource deletion logic from `_on_remove` into the `stop` hook handler (`self.framework.observe(self.on.stop, self._on_remove)`), or use a Kubernetes finalizer.
- **Linter rule**: "`_on_remove`-style cleanup must not be registered on `on.remove` alone for Kubernetes charms; use `on.stop` or a finalizer" — mechanically checkable by verifying the registered event.

### `juju refresh` from rev 882 to rev 883 crashes with `KeyError: 'istio-gateway-namespace'` in `__init__`

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:61` (`istio_gateway_principal` computation), `src/charm.py:173` (`istio_gateway_namespace` property)
- **Evidence**: `juju refresh --channel 1.10/edge` (882→883). First `config-changed` after download crashed:
  ```
  KeyError: 'istio-gateway-namespace'
    File ".../charm.py", line 61, in __init__
      istio_gateway_principal = f"cluster.local/ns/{self.istio_gateway_namespace}/sa/{...}"
    File ".../charm.py", line 173, in istio_gateway_namespace
      return self.model.config["istio-gateway-namespace"]
  ```
  `config.yaml` defaults this option to `"kubeflow"`. Juju retried the hook; second attempt succeeded, reaching Active in ~20s.
- **Impact**: Every upgrade risks triggering an opaque hook failure that produces noise in monitoring/alerting even though the charm self-heals.
- **Fix**: Guard the `istio_gateway_namespace` property with `.get()` and a default, or move config-dependent initialization out of `__init__` into a `_on_config_changed` handler.
- **Linter rule**: "Config values must not be accessed in `__init__` without a `.get()` fallback" — not mechanically checkable.

### Config validation in `__init__` is a structural fragility, not a safety net

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:68-77`, `src/charm.py:76`
- **Evidence**: `pydantic.CharmConfig(**config_data)` runs inside `__init__`, which ops re-executes on every hook dispatch. Confirmed: setting `security-policy=invalid-value` causes the next `config-changed` to re-run `__init__`, hit pydantic validation, and set `BlockedStatus`. Instance variables (containers, mesh handler, K8S handler) set on the first successful `__init__` are not re-obtained on later dispatches (`if container not None` guard), so if a later `config-changed` fails validation, previously-set state may be stale relative to current cluster state.
- **Impact**: Recovery only happens by setting config back to a valid value. The charm has no `update-status` handler to recover from transient failures, so it depends entirely on `config-changed` firing again.
- **Fix**: Move config validation out of `__init__` into the config-changed handler; keep `__init__` to simple, idempotent state setup.
- **Linter rule**: "Hook handler or `__init__` must not call pydantic model validation that re-runs on every hook dispatch" — not mechanically checkable.

### `GenericCharmRuntimeError` and bare `ApiError` escape `_on_event`, causing opaque hook failures

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:318` (`_deploy_k8s_resources`), `src/charm.py:382`/`392` (`_update_profile_namespace_security_policy_labels`), `src/charm.py:361-366` (`_update_profiles_layer`)
- **Evidence**: `_on_event` only catches `ErrorWithStatus`. Three paths escape:
  ```python
  # (a) src/charm.py:312-320
  except ApiError as e:
      raise GenericCharmRuntimeError("Failed to create K8S resources") from e
  ```
  `GenericCharmRuntimeError` inherits from `Exception`, not `ErrorWithStatus` (confirmed via `python3 -c "from charmed_kubeflow_chisme.exceptions import GenericCharmRuntimeError; print(GenericCharmRuntimeError.__bases__)"`).
  ```python
  # (b) src/charm.py:392
  except ApiError as e:
      self.log.warning(f"Failed to patch namespace '{namespace_name}': {e}")
      raise e  # bare ApiError, not wrapped
  ```
  ```python
  # (c) src/charm.py:361-365
  except ChangeError as e:
      raise GenericCharmRuntimeError("Failed to replan") from e
  ```
  `update_layer` from chisme wraps `ChangeError` in `ErrorWithStatus`, but the inline `replan()` call here does not.
- **Impact**: If any of these errors fire during `config-changed` or pebble-ready hooks, the unit goes into error state with a generic "hook failed" message and no diagnostic info at the status level.
- **Fix**: Wrap `GenericCharmRuntimeError` in `ErrorWithStatus` at the `_on_event` level with a catch-all, or wrap the individual call sites.
- **Linter rule**: "Exception types other than `ErrorWithStatus` raised inside `_on_event` or handlers called from it must be caught and wrapped" — mechanically checkable via call-graph analysis.

### `ingress` relation declared but not implemented — hook is a no-op

- **Severity**: high
- **Kind**: bug
- **Where**: `metadata.yaml:35-39` (declares `ingress` as `requires`, interface `ingress`) vs `src/charm.py` (no implementation)
- **Evidence**: No `IngressRequires` provider, no `framework.observe(self.on.ingress.relation_changed, ...)`, no ingress-relation code. `traefik-k8s` related to `kubeflow-profiles:ingress`; `ingress-relation-changed` fired on kubeflow-profiles (confirmed via `juju debug-log`) but was handled silently as a no-op — no Ingress resource created, no error raised, charm stayed active.
- **Impact**: An operator relating traefik-k8s expecting ingress to work gets a successful-looking relation that does nothing.
- **Fix**: Implement an ingress provider, or remove the `ingress` declaration from `metadata.yaml` to avoid misleading operators.
- **Linter rule**: "Any `requires` relation declared in `metadata.yaml` must have at least one `framework.observe(self.on.<rel>.relation_*, ...)` call" — mechanically checkable.

### Charm has no `relation_broken` observer for its own reconciliation

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:139-140`
- **Evidence**:
  ```python
  for rel in self.model.relations.keys():
      self.framework.observe(self.on[rel].relation_changed, self._on_event)
  ```
  `grep -rn "relation_broken" src/` returns nothing. Both `logging-relation-broken` and `metrics-endpoint-relation-broken` fire on the unit (confirmed via `juju debug-log`) but `_on_event` is not invoked. The `LogForwarder` (loki lib) and `ServiceMeshConsumer` (istio lib) handle their own cleanup internally via their own observers, but the charm's own reconciliation (`_send_info`, `_deploy_k8s_resources`, `_update_profiles_layer`, kfam pebble update) does not run after any relation removal.
- **Impact**: If the charm was mid-reconciliation when a relation is removed, it will not re-evaluate state; removing a relation never triggers re-reconciliation.
- **Fix**: Add `self.framework.observe(self.on[rel].relation_broken, self._on_event)` inside the same loop.
- **Linter rule**: "Any charm that observes `relation_changed` must also observe `relation_broken` for the same relation" — mechanically checkable.

### `_update_profile_namespace_security_policy_labels` stops at first failure instead of continuing

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:382-392`
- **Evidence**:
  ```python
  for namespace_name in profile_namespaces:
      try:
          client.patch(...)
      except ApiError as e:
          self.log.warning(f"Failed to patch namespace '{namespace_name}': {e}")
          raise e  # stops loop, remaining namespaces never patched
  ```
- **Impact**: A transient k8s API error on one namespace prevents security-policy updates to all subsequent namespaces in the loop.
- **Fix**: Catch `ApiError` per-namespace, log and `continue`; aggregate failures and raise a single `ErrorWithStatus` at the end if any namespace failed.
- **Linter rule**: "Loop over k8s resources must not `raise` inside the loop body, preventing remaining iterations" — mechanically checkable.

### `LogForwarder._update_logging` does not remove Pebble log targets on relation broken (loki lib bug)

- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/loki_k8s/v1/loki_push_api.py:2581-2587`
- **Evidence**: After `juju remove-relation kubeflow-profiles:logging loki-k8s`, `logging-relation-broken` fired and logged "No Loki endpoints available", but `pebble plan` in the `kubeflow-kfam` container still showed the `loki-k8s/0` log target. The target was only removed after the pod was killed and recreated.
  ```python
  def _update_logging(self, event: RelationEvent):
      if not (loki_endpoints := self._retrieve_endpoints_from_relation()):
          logger.warning("No Loki endpoints available")
          return  # should call disable_inactive_endpoints
      ...
  ```
- **Impact**: After removing the Loki relation, the workload keeps trying to forward logs to an endpoint that no longer exists, wasting resources and generating connection errors.
- **Fix**: Call `_PebbleLogClient.disable_inactive_endpoints` when `loki_endpoints` is empty.
- **Linter rule**: not applicable to this charm — filed as a bug in `charms.loki_k8s.v1.loki_push_api`.

### `_get_profile_namespaces` called in `__init__` can cause opaque startup failures

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:159` (`if profile_namespaces:`), `src/charm.py:298` (`_get_profile_namespaces`), `src/charm.py:304` (raises `GenericCharmRuntimeError` on `ApiError`)
- **Evidence**:
  ```python
  profile_namespaces = self._get_profile_namespaces()  # __init__, line 158
  if profile_namespaces:
      self.user_workload_backup = VeleroBackupProvider(...)
  ```
  `_get_profile_namespaces()` calls the lightkube client and raises `GenericCharmRuntimeError` on `ApiError`. Since this runs inside `__init__` on every hook dispatch, a transient k8s API error during any hook call escapes `__init__` entirely with a generic "hook failed" message.
- **Impact**: The charm has a hard dependency on k8s API availability at every hook, not just install. Also: `user_workload_backup` is only initialized if profile namespaces already exist at that moment — if `__init__` runs before any Profile CRs exist, the Velero backup relation for user workloads never gets configured.
- **Fix**: Defer this to a method called from `_on_event` wrapped in `ErrorWithStatus`; initialize `user_workload_backup = None` in `__init__` and set it up lazily.
- **Linter rule**: "API calls that can raise non-`ErrorWithStatus` exceptions must not be made in `__init__`" — mechanically checkable.

### `VeleroBackupProvider` has no `relation_broken` observer — backup spec not cleaned on relation removal

- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/velero_libs/v0/velero_backup_config.py:201-210`
- **Evidence**: `VeleroBackupProvider` registers observers only for `leader_elected`, `relation_created`, `upgrade_charm`, and Pebble-ready events — no `relation_broken`. When the Velero relation is removed, the backup spec is never cleared from the relation data.
- **Impact**: Velero may continue attempting to back up `profiles.kubeflow.org` resources after the relation is removed, producing errors or wasted work.
- **Fix**: Add a `relation_broken` observer to `VeleroBackupProvider.__init__` that clears the backup spec (library bug, charm uses the library correctly).
- **Linter rule**: "Any `RelationProvider` that sends data must also clear it on `relation_broken`" — mechanically checkable.

### `_on_remove` raises bare `ApiError` instead of `ErrorWithStatus`

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:412-422`
- **Evidence**:
  ```python
  def _on_remove(self, event):
      self.unit.status = MaintenanceStatus("Removing k8s resources")
      manifests = self.k8s_resource_handler.render_manifests()
      try:
          delete_many(self.k8s_resource_handler.lightkube_client, manifests)
      except ApiError as e:
          self.log.warning(f"Failed to delete resources: {manifests} with: {e}")
          raise e  # bare ApiError, not ErrorWithStatus
  ```
- **Impact**: Currently moot since `_on_remove` never fires on Kubernetes (see the critical remove-application finding above), but if the fix for that is applied, an RBAC regression or transient API error during removal would still cause an opaque "hook failed" instead of an actionable status.
- **Fix**: Wrap in `ErrorWithStatus` with a `MaintenanceStatus` describing the failure.
- **Linter rule**: "Bare `raise` of `ApiError` in event handlers must not occur" — mechanically checkable.

### Config documentation/model mismatch: `restricted` is silently accepted then unexplained on rejection

- **Severity**: medium
- **Kind**: docs
- **Where**: `config.yaml:13` (description limits to `privileged`/`baseline`) vs `src/models.py:17` (`Literal["privileged", "baseline", "restricted"]`)
- **Evidence**: `config.yaml` description explicitly lists only two values; the pydantic model accepts three. Setting `security-policy=restricted` succeeds (`ActiveStatus`). The error message for an actually-invalid value truncates to "Input should be 'privileged', 'baseline' or 'res..." making the third valid value unclear.
- **Impact**: A user reading the docs would not try `restricted`; a user reading the truncated error message cannot infer it either.
- **Fix**: Update the config description to list all three values, or drop `restricted` from the model if unsupported.
- **Linter rule**: "Pydantic model Literal values must match config.yaml option descriptions" — mechanically checkable.

### Inconsistent error handling: kfam uses `update_layer` (wraps `ChangeError`) but profiles uses `add_layer`+`replan()` (raises `GenericCharmRuntimeError`)

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:363` (profiles `replan()`) vs chisme's `update_layer` (kfam)
- **Evidence**:
  ```python
  self.profiles_container.add_layer(...)
  try:
      self.profiles_container.replan()
  except ChangeError as e:
      raise GenericCharmRuntimeError("Failed to replan") from e  # escapes _on_event
  ```
  kfam's path goes through chisme's `update_layer`, which wraps `ChangeError` in `ErrorWithStatus` (caught by `_on_event`).
- **Impact**: Identical failure modes on different containers are handled differently — one opaque, one graceful.
- **Fix**: Use `update_layer` from chisme for the profiles layer too, or wrap the `replan()` call to raise `ErrorWithStatus`.
- **Linter rule**: "All Pebble layer update paths must use consistent error handling" — mechanically checkable.

### Duplicate `config_changed` observation causes double reconciliation on every config change

- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:127-129`
- **Evidence**:
  ```python
  self.framework.observe(self.on.config_changed, self.service_patcher._patch)
  self.framework.observe(self.on.config_changed, self._on_event)
  ```
  Confirmed from the uniter log: every `juju config` call produces exactly 2 `config-changed` dispatches ~1s apart; the full maintenance→active reconciliation cycle runs twice per config change.
- **Impact**: Redundant K8S resource application on every config change wastes API calls and extends hook execution time.
- **Fix**: Combine both handlers into one `config_changed` handler calling `service_patcher._patch` and the reconciler in sequence.
- **Linter rule**: "Multiple observers on the same event that both perform I/O or status changes should be consolidated" — not mechanically checkable.

### `kubernetes_service_patch` v1 is deprecated

- **Severity**: medium
- **Kind**: tech-debt
- **Where**: `lib/charms/observability_libs/v1/kubernetes_service_patch.py`
- **Evidence**: The lib logs on every `update-status` (every ~5 min): "The `kubernetes_service_patch v1` library is DEPRECATED and will be removed in October 2025. ... `ops.Unit.set_ports` should be used instead."
- **Impact**: After the deprecation window closes, this service-patching functionality will break.
- **Fix**: Replace `KubernetesServicePatch` with `ops.Unit.set_ports`.
- **Linter rule**: not mechanically checkable.

### Dead code: `_apply_manifest` and `ActionEvent` import unused

- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:27`, `src/charm.py:450-457`
- **Evidence**: `ActionEvent` is imported but never used as a handler argument; `_apply_manifest` is defined but never called.
- **Impact**: Dead code increases maintenance burden and suggests incomplete/abandoned features.
- **Fix**: Remove the unused import and method.
- **Linter rule**: "Unused imports and unreachable methods should be flagged" — mechanically checkable with `pyflakes`/`ruff`.

### `user_workload_backup` Velero spec excludes `profiles.kubeflow.org` without explanation

- **Severity**: low
- **Kind**: docs
- **Where**: `src/constants.py:8`
- **Evidence**:
  ```python
  K8S_USER_WORKLOAD_EXCLUDE_RESOURCECS = [
      ...
      "profiles.kubeflow.org",
      ...
  ]
  ```
  `profiles-backup-config` is the dedicated relation for backing up this resource type; `user-workloads-backup-config` excludes it, arguably correctly, but with no comment explaining the relationship.
- **Impact**: An operator might assume removing `profiles-backup-config` still leaves profiles protected via user-workload backup — it does not.
- **Fix**: Add a comment explaining the exclusion is intentional and delegated to `profiles-backup-config`.
- **Linter rule**: not mechanically checkable.

### `VeleroBackupProvider` logs a warning on every `config-changed` when no relation exists

- **Severity**: nit
- **Kind**: ux
- **Where**: `src/charm.py:151-159`
- **Evidence**: On every `config-changed`/`update-status`, `VeleroBackupProvider` checks for the `profiles-backup-config` relation and logs "VeleroBackupProvider handled send_data event but no relation 'profiles-backup-config' found Skiping event - no data sent" — confirmed in the pod-restart recovery log.
- **Impact**: Harmless but noisy log spam if Velero is never related.
- **Fix**: Only instantiate the provider when the relation exists, or downgrade the log level.
- **Linter rule**: not mechanically checkable.

### `additional_principals` env var: empty string vs absent

- **Severity**: nit
- **Kind**: ux
- **Where**: `src/charm.py:205-206`
- **Evidence**:
  ```python
  if self._additional_principals:
      env["ADDITIONAL_PRINCIPALS"] = self._additional_principals
  ```
  An empty string is falsy, so `ADDITIONAL_PRINCIPALS` is absent rather than empty when config is cleared.
- **Impact**: Minor — the workload can't distinguish "never set" from "intentionally cleared".
- **Fix**: No fix strictly required; worth noting for workload authors.
- **Linter rule**: not applicable.

## Worth copying

- **`ErrorWithStatus` pattern** (`src/charm.py:239-246`): raising typed exceptions from deep helper methods and catching at the top of event handlers. The `_check_container_connection` helper is a clean use of this.
- **`StoredState` for change detection** (`src/charm.py:40`): caching `last_security_policy` to avoid unnecessary Pebble pushes/restarts is idiomatic and worth standardizing across Pebble-layer-config charms.
- **Separate Pebble layers per container**: `_profiles_pebble_layer` and `_kfam_pebble_layer` are clean and maintainable.
- **Non-root container execution**: `metadata.yaml` sets `uid: 584792`/`gid: 584792` for both containers; rock images run as this user — correct security posture.
- **Velero backup integration**: separate `profiles-backup-config` (CRs) and `user-workloads-backup-config` (namespaces, with exclusions) is a good separation of concerns.
- **pydantic config validation**: a dedicated `CharmConfig` model with `Literal` types gives clear errors and type safety (aside from the `__init__` placement issue above).
- **Jinja2 template for namespace labels**: `namespace-labels.yaml.j2` rendered with `security_policy` context is a clean pattern for config-driven manifests.
- **Prometheus alert rules**: `KfamDown`/`ProfilesDown` alerts with proper `juju_model`, `juju_model_uuid`, `juju_application`, `juju_charm` labels — exemplary alerting hygiene.
- **Comprehensive integration tests**: `tests/integration/test_charm.py` and `test_charm_ambient.py` exercise real k8s resource creation, security-policy propagation, health checks, and service-mesh integration, using reusable `charmed_kubeflow_chisme.testing` assertion helpers (`assert_alert_rules`, `assert_logging`, `assert_metrics_endpoint`, `assert_security_context`) other charms should adopt.

## Common-practice notes

- Standard ops patterns: `CharmBase`, `StoredState`, event observers, chisme's `ErrorWithStatus`, `KubernetesServicePatch`, `MetricsEndpointProvider`, `LogForwarder`. Only observing `relation_changed` (never `relation_broken`) is an uncommon gap versus most charms.
- `ingress` relation is declared in `metadata.yaml` but unimplemented — drift from the convention that a declared relation should have at least one observer.
- `lib/charms/`: vendored libraries at reasonable versions (`istio_beacon_k8s/v0`, `loki_k8s/v1`, `observability_libs/v1`, `prometheus_k8s/v0`, `velero_libs/v0`).
- `src/` layout: single-file `charm.py` plus `constants.py`/`models.py`; no `src/charm/` package — acceptable for a charm this size but below current convention.
- `charmcraft.yaml`: modern poetry build with explicit parts and Rust toolchain; correct `charm-user: non-root` in `metadata.yaml`.
- `tox.ini`: poetry-based envs; unit tests use `ops.testing.Harness` (deprecated in favor of Scenario, not migrated); integration tests use `pytest-operator` with good parametrization.
- `pyproject.toml`: poetry, follows modern charm ecosystem standard.
- `concierge.yaml`: tests against Juju 3.6/stable and microk8s 1.32-classic; deployed here fine on a Juju 4.x controller too, suggesting good backward compatibility.
- `config.yaml`: uses `>` YAML folding for multi-line descriptions — correct format.
- Terraform module present under `terraform/` (`main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`) with sensible defaults and `trust: true`.
- `charmcraft analyse` not run (pack failed with LXD conflict in the environment), but lint (`pflake8`, `black`, `isort`, `codespell` with 4 acceptable false positives) passes.

## Tests

**Unit tests** (`tests/unit/test_operator.py`): 19 tests, all passing (0.34s). Run: `PYTHONPATH=./src:./lib poetry run pytest tests/unit/ -v`. Coverage includes:
- Not-leader scenario correctly sets `WaitingStatus`
- Invalid config (port, manager-port, security-policy, service-mesh-mode) correctly sets `BlockedStatus` at init time
- Profiles/kfam containers running after pebble-ready
- No-relation scenario reaches `ActiveStatus`
- Both pebble-ready-first orderings
- Pebble layer content for `istio-sidecar`/`istio-ambient` modes
- `ADDITIONAL_PRINCIPALS` env var presence/absence

**Unit test gaps**:
- No test for `config_changed` at runtime (after `begin_with_initial_hooks`) — a critical gap given the `__init__` validation finding
- No test for leadership change mid-operation
- No test for `_send_info` with missing relation data
- No test for `_get_profile_namespaces` error path
- No test for `_deploy_k8s_resources` error path
- No test for `_update_profile_namespace_security_policy_labels` error path
- No test for `GenericCharmRuntimeError` escaping `_on_event`
- No test for `relation_broken` handling (none exists to test — an implementation gap, not just a test gap)
- No test for `ingress` relation (same — no handler to test)
- No test for `_on_remove` error path

**Integration tests** (`tests/integration/test_charm.py`, `test_charm_ambient.py`): substantial coverage of profile creation and namespace label propagation, security-policy config changes, health check endpoints, container security context, logging relation, alert rules, metrics endpoints, and ambient mode (waypoint gateway, authorization-policy principals, dashboard-to-kfam communication).

**Integration test gaps**:
- No assertion that the charm goes blocked on invalid config
- No test for relation add/remove during operation
- No test for scale-up behavior
- Ambient tests do not clean up authorization policies on teardown (potential cluster pollution)
- No test for pod restart/crash recovery
- Harness-based unit tests flag `PendingDeprecationWarning`; not migrated to Scenario
- No integration test verifies CRD/service removal on `remove-application` — that path is entirely untested
- No integration test for `juju refresh` between revisions — the upgrade path is entirely untested
- No integration test for any `relation_broken` behavior

**Linting** (`tox -e lint`): `pflake8`, `black`, `isort` all pass. `codespell` flags 4 false positives in `crds.yaml.j2` (`NotIn`, a Kubernetes field name) — acceptable but should be explicitly configured as skipped.

## Docs

- `README.md`: brief, links to Kubeflow multi-tenancy and Charmed Kubeflow docs — adequate for orientation, thin for deployment.
- `CONTRIBUTING.md`: strong; covers poetry/tox workflow, dependency management, PR process.
- `terraform/README.md`: present, explains module usage, required providers, and example usage.
- Charmhub description: "Kubeflow Profiles and Access Management" — minimal; the discourse doc is the primary user-facing reference.
- Discourse docs (`https://discourse.charmhub.io/t/charmed-kubeflow-profiles/8232`): canonical location, not reviewed live.

## Open questions

1. Duplicate `config-changed` dispatch — ops 2.x behavior batching multiple observers into separate dispatch runs. Not harmful (both reach Active) but wastes work; worth documenting even if not fixed immediately.
2. `restricted` security policy works at runtime but is undocumented — should be resolved in one direction or the other.
3. `KubernetesServicePatch` migration to `ops.Unit.set_ports` must land before the lib's October 2025 removal deadline.
4. Velero: the `user-workloads-backup-config` exclusion of `profiles.kubeflow.org` is intentional but not surfaced anywhere for operators — they may not realize profile CRs need the separate `profiles-backup-config` relation.
5. `profiles_container` property returns a value cached once in `__init__`; if `__init__` fails before setting it (invalid config on first run), later valid-config hooks may reuse a stale/unset value. Latent issue, not confirmed to have caused a failure in this session.
6. Issue #156 (ServiceAccount names hardcoded from config rather than relation data) confirmed present in code, open since 2024-03-29, no apparent fix.
7. Whether the `ingress` relation is meant to be implemented eventually or is legacy dead code is unclear — should be tracked explicitly either way.
8. Velero relation behavior could not be observed live (charms unavailable on charmhub in this environment) — only the "no relation" warning path was exercised.
9. `_get_profile_namespaces()` runs in `__init__` before any Profile CRs necessarily exist; at install time this list is empty, so `user_workload_backup` may never get initialized if the first `config-changed` fires before any Profile namespaces exist — a latent race, not confirmed to have occurred in this session `(unverified)`.
10. Whether the refresh-time `KeyError` is deterministic (always happens on refresh) or transient was not established — only one refresh cycle (882→883) was tested.
11. Whether the `remove` hook's absence on Kubernetes is a Juju 4.x regression or expected CAAS behavior is not established from this review alone; worth raising with the Juju team regardless of the charm-side fix.
