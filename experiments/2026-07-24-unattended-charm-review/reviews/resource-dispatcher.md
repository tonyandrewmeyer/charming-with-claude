# resource-dispatcher

A k8s charm that injects Kubernetes resources (ConfigMaps, Secrets, ServiceAccounts, PodDefaults, Roles, RoleBindings) into namespaces matching a configurable label, using a Metacontroller `DecoratorController` as its reconciliation engine. Code quality is generally good — 91% unit test coverage, a well-defined manifest conflict-detection scheme, and correct `relation-broken` handling in the currently-published revision. It is not deployable out of the box: the install hook races the Metacontroller CRD on Juju 4.x and fails for ~7 minutes with no `WaitingStatus`, and the CRD's config-driven label selector is never refreshed after `install`/`upgrade-charm`, so `target_namespace_label` changes silently stop taking effect on the cluster side. The 2.0/edge track (rev 611) also regresses meaningfully versus 2.0/stable (rev 547): it drops the `config-maps` relation (breaking `juju refresh` while any relation is active, and removing `configmaps` from the CRD's attachments), and simplifies manifest-conflict and directory-layout logic in ways that reintroduce bugs the current library avoids. A maintainer should first: (1) make the install hook tolerate a missing CRD instead of crash-looping, (2) re-apply the CRD on `config-changed`, and (3) resolve whether rev 611's relation/CRD/library regressions are intentional before promoting it further.

| | |
|---|---|
| Repo | canonical/resource-dispatcher @ `8b655320` (2026-07-13) |
| Charms | resource-dispatcher (k8s), manifests-tester (machine, integration-only) |
| Substrate | k8s (Juju 4.x and 3.6 tested) |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.12) and concierge-k8s-3 (Juju 3.6.25), channel 2.0/stable rev 547, with a `juju refresh` to 2.0/edge rev 611 on the k8s-3 model |
| Reviewed | 2026-08-20 |

## What it does

The charm deploys a Metacontroller `DecoratorController` CRD and a Python webhook server. The webhook server reads manifests from a Pebble layer filesystem (`/var/lib/pebble/default/resources/`), and the DecoratorController watches for namespace changes, calling the webhook when namespaces with the target label are created or modified. The charm receives Kubernetes manifests from up to six requirer charms via Juju relations (`config-maps`, `secrets`, `service-accounts`, `pod-defaults`, `roles`, `role-bindings`) and writes them to the Pebble layer. When relations are removed, manifests are removed from the filesystem but the already-created K8s resources in namespaces are not deleted (known issue #8). The charm also manages Istio AuthorizationPolicies for ambient-mode service mesh.

## Deployment log

```bash
# Model rv-rd-k8s on concierge-k8s-4 (Juju 4.0.12)
juju add-model rv-rd-k8s --controller concierge-k8s-4
juju deploy resource-dispatcher --channel 2.0/stable --trust
```

1. **Deploy k8s-4**: unit went to `error` for ~7 minutes (install hook failed 12 times) — CRD not yet present; recovered after the CRD was created manually and `juju resolve` run.
2. **Config change** (`target_namespace_label`: `user.kubeflow.org/enabled` → `test.kubeflow.org/enabled`): Pebble layer command updated with the new label; CRD's label selector NOT updated.
3. **Scale to 2 units**: unit 1 (non-leader) Pebble service `inactive` — correct, only the leader runs the webhook.
4. **Kill unit 0 pod**: failover, unit 0 rebuilt and recovered.
5. **Invalid label** (`target_namespace_label="not.a.valid/label-syntax!"`): accepted silently; CRD label selector updated to the invalid value.
6. **Empty label** (`target_namespace_label=""`): accepted silently; Pebble service entered `backoff` (webhook crashed with `error: argument --label/-l: expected one argument`); `juju status` still showed `active`.
7. **Attempted `juju refresh --channel 2.0/edge`**: blocked by active relations (`config-maps` dropped from rev 611 endpoints).

```bash
# Model rv-rd-k8s3 on concierge-k8s-3 (Juju 3.6.25)
juju add-model rv-rd-k8s3 --controller concierge-k8s-3
juju deploy resource-dispatcher --channel 2.0/stable --trust
```

1. **Deploy k8s-3**: unit went `active` immediately — CRD created on first attempt (~1 min, no errors).
2. **Relate kserve-controller** (`secrets`, `service-accounts`): kserve-controller blocked waiting for istio-pilot — never sent manifests.
3. **Relate manifests-tester** (via Juju secrets, new library): `relation-changed` on resource-dispatcher rev 547 crashed with `JSONDecodeError` — old library tried to `json.loads()` the secret URI. Unit went to `error`; `juju resolve` did NOT recover it. Removed relation — hook kept retrying. Killed the unit pod to recover.
4. **Relation broken** (`resource-dispatcher:service-accounts ← kserve-controller:service-accounts`): `service-accounts-relation-broken` fired; `_on_event` called `_sync_manifests([], dispatch_folder)`, cleaning up empty dispatch directories. No orphaned manifests (kserve-controller never sent any).
5. **`juju refresh` to 2.0/edge (rev 611)**: after breaking the `service-accounts` relation, refresh succeeded. Hook sequence: `upgrade-charm` → `_deploy_k8s_resources` (CRD re-applied, generation 1→2) → `config-changed` → `start` → `pebble-ready`. Pebble plan updated with the full command. CRD now has 5 attachment types (missing `configmaps`).
6. **Scale to 2 units**: unit 0 (leader) Pebble service `active`; unit 1 (non-leader) `inactive` — correct.
7. **Deploy istio-pilot**: related to kserve-controller (`istio-pilot:gateway-info ← kserve-controller:ingress-gateway`). istio-pilot went to `error` (`hook failed: gateway-info-relation-created`); kserve-controller then `waiting: Waiting for ingress gateway data`. Service mesh integration untested due to istio-pilot's own error.
8. **Unit tests**: 49 passed, 46 `PendingDeprecationWarning`s. Coverage 91% on `src/charm.py`.
9. **No actions defined**: `actions.yaml` does not exist; the "run every action" checklist item is N/A for this charm.

## Observed behaviour

**Install hook failure pattern differs between Juju 3.6 and 4.x**: On concierge-k8s-4 (Juju 4.0.12), the install hook failed 12+ times over ~7 minutes with `LoadResourceError: Cannot find resource DecoratorController`. On concierge-k8s-3 (Juju 3.6.25), the install hook succeeded on first attempt (~1 minute). Both run microk8s 1.32. Consistent with Juju 4.x firing the install hook before pod network access to the API server is fully established.

**Pebble layer IS correctly updated on config change** (this corrects an earlier working assumption): `_resource_dispatcher_operator_layer` is a property that re-evaluates `self._namespace_label` from `self.model.config` on each access, and `_update_layer()` builds a fresh `Layer` object each call. Confirmed from the Pebble plan after `upgrade_charm`: `python3 main.py --port 8080 --label user.kubeflow.org/enabled --folder /var/lib/pebble/default/resources`. The CRD, not the Pebble layer, is what goes stale (see findings).

**ROCK's readiness check (HTTP 418) during pod startup**: the rock image ships a Pebble layer with `command: /bin/python3 /main.py` (no args) and an HTTP readiness check returning 418. During initial pod startup, before `upgrade_charm` runs, Pebble logs show `Check "readiness" failure 1/3: non-2xx status code 418` repeated every ~10s. The charm's own layer uses `override: replace`, which removes the ROCK's service definition and its checks entirely; once `upgrade_charm` runs, the combined plan has no health checks and the service runs cleanly.

**Stale CRD label on config change**: after a `target_namespace_label` config change, the Pebble layer is updated but the CRD's `labelSelector` still references the old label. Observed after refresh: CRD `generation: 2`, `labelSelector` = `user.kubeflow.org/enabled` (the default, not the configured value). The CRD is only re-applied on `install` and `upgrade_charm`, never on `config-changed`.

**Scale-up (2 units)**: leader's Pebble service `active`; non-leader's `inactive`. Non-leader's `_on_event` raises `ErrorWithStatus("Waiting for leadership")` from `_check_leader` before doing any other work — correct behaviour.

**`juju refresh` from 2.0/stable to 2.0/edge**: succeeded only after breaking the sole active relation (`service-accounts`); attempting it with a `config-maps`-typed relation active fails with `ERROR: one or more of the provided endpoints ... do not exist`. CRD `metadata.generation` went 1→2 (confirming `apply()` re-ran). CRD `attachments` field changed from 6 types to 5 — `configmaps` disappeared.

**`relation-broken` manifest cleanup**: breaking `service-accounts` fires `service-accounts-relation-broken`; `_on_event` calls `_sync_manifests([], dispatch_folder)`, which removes stale YAML files and empty subdirectories. No K8s resources were orphaned in this test only because kserve-controller was blocked and never sent manifests.

**Service mesh relation untested**: istio-pilot (1.22/stable) went to `error` on `gateway-info-relation-created`; kserve-controller showed `waiting: Waiting for ingress gateway data`. Unable to verify AuthorizationPolicy creation/removal or the `ambient_mesh_enabled` code path.

**Library version mismatch causes hook crash**: `manifests-tester` (new library, sends manifests via Juju secrets) related to resource-dispatcher rev 547 (old library, no secret support) → `relation-changed` crashes with `JSONDecodeError`. Unit stuck in `error`; `juju resolve` does not break the retry cycle. Integration test `test_upgrade_erroneous_path.py` explicitly documents this exact scenario as expected when the wrong upgrade order is used.

**Empty label → silent Pebble crash**: setting `target_namespace_label=""` caused Pebble to restart the service with `main.py: error: argument --label/-l: expected one argument`, entering `backoff`. `juju status` showed `active` despite the workload being non-functional.

**Unit test coverage gaps** (from `coverage report --show-missing`, `src/charm.py`):
- Line 157: `_check_container` return path when `container.can_connect()` is `False`
- Lines 162, 167, 172: `_deploy_k8s_resources` success path and `ApiError` handler — `k8s_resource_handler` is entirely mocked
- Line 213: `_on_service_mesh_relation_events` full `reconcile()` call path
- Lines 408–411, 419, 461→464: `_on_remove` cleanup paths (`ApiError` non-404 handler)

## Findings

### CRD not re-applied on `target_namespace_label` config change — Metacontroller watches the wrong namespaces
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:57–65` (`__init__`: `_namespace_label`/`_context["label"]` set once); `src/charm.py:199–209` (`k8s_resource_handler` property, caches context); `src/charm.py:161–173` (`_deploy_k8s_resources` only called on `install`/`upgrade_charm`)
- **Evidence**: `_namespace_label` and `_context["label"]` are plain variables assigned once in `__init__`. `k8s_resource_handler` builds a handler from this stale context and caches it. `_deploy_k8s_resources` is never invoked from `config-changed`. `KubernetesResourceHandler.apply()` uses `force_recompute=False`, which returns cached manifests. After a config change and after a refresh, the CRD's `labelSelector` remained `user.kubeflow.org/enabled` rather than the configured value.
- **Impact**: After a config change, the Metacontroller watches the wrong namespaces — resources continue to be applied against the old label, silently, with no error surfaced.
- **Fix**: Call `_deploy_k8s_resources` from `_on_event` when leader and config has changed, or invalidate the cached `_k8s_resource_handler`/force recompute on config change, or explicitly document that label changes require a full `juju refresh`.
- **Linter rule**: not mechanically checkable.

### Install hook fails for ~7 minutes on Juju 4.x when the Metacontroller CRD isn't yet present, with an uncaught `LoadResourceError`
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:161` (`_on_install`); `src/charm.py:165` (`_deploy_k8s_resources` → `self.k8s_resource_handler.apply()`)
- **Evidence**: On concierge-k8s-3 (Juju 3.6.25), `juju deploy resource-dispatcher --trust` went `active` in ~1 minute, CRD created on the first attempt. On concierge-k8s-4 (Juju 4.0.12), the same deploy put the unit into `error` for ~7 minutes across 12 retries before the CRD was created on the 13th attempt. Both controllers run microk8s 1.32. The hook raises `lightkube.core.exceptions.LoadResourceError: Cannot find resource DecoratorController of group metacontroller.k8s.io/v1alpha1`, uncaught, and is simply retried by Juju.
- **Impact**: Any operator deploying with `juju deploy resource-dispatcher --trust` without first deploying `metacontroller-operator` gets a unit stuck in `error` for ~7 minutes on Juju 4.x before auto-recovery, and the failure is timing-dependent rather than deterministic (Juju 3.6 didn't reproduce it).
- **Fix**: Catch `LoadResourceError` in `_deploy_k8s_resources` and set `WaitingStatus("Waiting for Metacontroller CRD")`, deferring to `pebble-ready` or a retry loop, instead of letting the hook fail.
- **Linter rule**: "hook handler catches `ApiError` but not `LoadResourceError`" — mechanically checkable by scanning for `except ApiError` without `except (ApiError, LoadResourceError)`.

### Rev 547's `KubernetesManifestsProvider` library crashes when a requirer sends manifests via Juju secrets
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/resource_dispatcher/v0/kubernetes_manifests.py` (rev 547, 355 lines, no `is_secret_enabled()`); `src/charm.py:237` (`_update_manifests` → `get_manifests`)
- **Evidence**: Relating `manifests-tester` (new library with secret support) to resource-dispatcher rev 547 crashed `relation-changed` with `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`, from `get_manifests` calling `json.loads()` directly on relation data that is actually a Juju secret URI (`secret://...`). Rev 547's library has no `is_secret_enabled()` method; rev 611's library (508 lines) checks `is_secret` first and reads the secret content instead.
- **Impact**: Any operator who relates resource-dispatcher rev 547 to a requirer using the newer secret-based `KubernetesManifestsRequirer` gets a permanently stuck unit — the hook retries indefinitely and `juju resolve` does not break the cycle; only killing the pod recovers.
- **Fix**: Upgrade to a revision with the secret-aware library (rev 611+), or ensure requirer charms are never upgraded to the secret-based library before resource-dispatcher is upgraded.
- **Linter rule**: "provider charm's `KubernetesManifestsProvider` library lacks `is_secret_enabled()`" — mechanically checkable by scanning the library for that method.

### Rev 611 CRD in cluster has only 5 attachment types — `configmaps` silently disappears on upgrade
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/templates/decorator-controller.yaml.j2` (local source has all 6 resources); rev 611 CRD after refresh
- **Evidence**: After `juju refresh resource-dispatcher --channel 2.0/edge` (rev 611), CRD `generation` went 1→2, and `kubectl get decoratorcontroller ... -o jsonpath='{.spec.attachments[*].resource}'` returned `secrets serviceaccounts poddefaults roles rolebindings` — `configmaps` missing. The local source template still includes all 6 resources. Whether rev 611's embedded template itself dropped `configmaps`, or whether the re-apply removed it from the existing CRD, was not established (see open questions).
- **Impact**: An operator upgrading from 2.0/stable to 2.0/edge silently loses the ability to dispatch ConfigMaps to namespaces, with no warning.
- **Fix**: Verify rev 611's embedded CRD template against the local source; restore `configmaps` if it was accidentally dropped, or explicitly document the removal as a breaking change.
- **Linter rule**: not mechanically checkable without cross-revision comparison of the embedded template.

### Rev 611 dropped the `config-maps` relation — blocks `juju refresh` from 2.0/stable while relations are active
- **Severity**: high
- **Kind**: bug
- **Where**: `metadata.yaml` (local source provides `config-maps`; rev 611 does not)
- **Evidence**: Local source (HEAD, rev 617 per charmhub) provides `config-maps, secrets, service-accounts, pod-defaults, roles, role-bindings`. Rev 611 provides only the latter five. `juju refresh resource-dispatcher --channel 2.0/edge` failed with `ERROR: one or more of the provided endpoints ... do not exist` while a `service-accounts` relation was active, and only succeeded after removing that relation. Integration test `test_charm.py` (lines 230, 241, 461) uses the `config-maps` relation and would fail against rev 611.
- **Impact**: Operators cannot refresh from 2.0/stable to 2.0/edge while any relation is active. The repo's integration tests only exercise the local source (which still has `config-maps`), not rev 611 as actually published.
- **Fix**: Restore `config-maps` in the metadata for the published rev, or explicitly document the breaking change and update integration tests to match what's actually published.
- **Linter rule**: not mechanically checkable (requires cross-revision comparison).

### `except ApiError` does not catch `LoadResourceError`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:165` (`_deploy_k8s_resources`)
- **Evidence**:
  ```python
  try:
      self.unit.status = MaintenanceStatus("Creating K8S resources")
      self.k8s_resource_handler.apply()
  except ApiError as err:          # does NOT catch LoadResourceError
      raise GenericCharmRuntimeError("K8S resources creation failed") from err
  ```
  `ApiError` and `LoadResourceError` share no inheritance relationship.
- **Impact**: An error during manifest rendering (e.g. missing CRD) propagates as an uncaught exception rather than a handled charm error.
- **Fix**: Add `except lightkube.core.exceptions.LoadResourceError` alongside `ApiError`, or catch the broader exception and translate to `ErrorWithStatus`.
- **Linter rule**: "exception handler catches `ApiError` but not `LoadResourceError`" — mechanically checkable.

### No config validation — invalid or empty `target_namespace_label` accepted silently, empty label crashes the workload
- **Severity**: high
- **Kind**: bug
- **Where**: `config.yaml:5` (no validator); `src/charm.py:57` (no runtime check)
- **Evidence**: Setting `target_namespace_label="not.a.valid/label-syntax!"` left the unit `active` and updated the CRD's label selector to the invalid value. Setting `target_namespace_label=""` left the unit `active` while Pebble entered `backoff` with `error: argument --label/-l: expected one argument`.
- **Impact**: Invalid labels silently misroute resources or crash the workload with no operator-visible signal.
- **Fix**: Add a validator to `config.yaml` rejecting empty strings, `/`, whitespace, or labels over 63 characters; add a runtime check that sets `BlockedStatus` on invalid config.
- **Linter rule**: "config option `target_namespace_label` lacks a `validator` in `config.yaml`" — mechanically checkable.

### Empty config label leaves `juju status` showing `active` while Pebble is in backoff
- **Severity**: high
- **Kind**: ux
- **Where**: `src/charm.py:381` (`_on_event`); `src/charm.py:57` (no validation)
- **Evidence**: After `juju config resource-dispatcher target_namespace_label=""`, the unit showed `active` while Pebble logs showed `Service "resource-dispatcher" stopped unexpectedly with code 2 ... on-failure action is "restart", waiting ~30s before restart (backoff 39)`.
- **Impact**: The workload is crashed and non-functional but the charm reports healthy, hiding the failure from operators.
- **Fix**: Validate `target_namespace_label` before updating the Pebble layer; set `BlockedStatus("Invalid target_namespace_label")` if empty/invalid.
- **Linter rule**: not mechanically checkable.

### Rev 611 regression: simplified conflict detection flags pinned + global manifests of the same name as conflicting
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/resource_dispatcher/v0/kubernetes_manifests.py` (rev 611 `_manifests_valid`); local source rev 547 `_find_manifest_conflicts`
- **Evidence**: Local source uses `Counter` over `(namespace, name)` tuples, so a pinned manifest (with `metadata.namespace`) and a global manifest of the same name are not flagged. Rev 611's `_manifests_valid` only checks `name` uniqueness across all manifests, so it flags a same-named global and namespace-pinned manifest as conflicting even though they aren't.
- **Impact**: In a multi-namespace deployment, a global secret and a namespace-pinned secret sharing a name would be incorrectly rejected.
- **Fix**: Restore the `(namespace, name)` uniqueness check.
- **Linter rule**: not mechanically checkable without understanding the semantics.

### `kubernetes_service_patch` v1 library deprecated, removal announced for October 2025
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:19` (`from charms.observability_libs.v1.kubernetes_service_patch import KubernetesServicePatch`)
- **Evidence**: Every hook fires: `WARNING: The kubernetes_service_patch v1 library is DEPRECATED and will be removed in October 2025. ... ops.Unit.set_ports functionality should be used instead.`
- **Impact**: Once the library is removed, the charm stops patching the K8s service, potentially losing its custom port configuration.
- **Fix**: Replace `KubernetesServicePatch` with `self.unit.set_ports([...])` and drop the dependency.
- **Linter rule**: "charm imports from a deprecated library (`charms.observability_libs.v1.kubernetes_service_patch`)" — mechanically checkable by scanning imports.

### README doesn't document `metacontroller-operator` as a required prerequisite
- **Severity**: high
- **Kind**: docs
- **Where**: `README.md`
- **Evidence**: Searching the README for "metacontroller", "prerequisite", "dependency" returns no results. The charm cannot start without the Metacontroller CRD, and issue #126 only asks for `--trust` documentation, not this larger gap.
- **Impact**: Operators following the README get a unit stuck in `error` for ~7 minutes with no explanation.
- **Fix**: Add a "Prerequisites" section: deploy `metacontroller-operator --channel latest/edge --trust` first.
- **Linter rule**: not mechanically checkable.

### Unresolved `relation-broken`: K8s resources left orphaned in namespaces
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:381–407` (`_on_event`); open issue #8
- **Evidence**: On relation removal, `_on_event` removes the manifest YAML from the Pebble layer filesystem via `_sync_manifests`, relying on the Metacontroller's reconciliation loop (bound to `resyncPeriodSeconds`, ~10s) to notice and delete the corresponding K8s resources — there is no explicit delete via the K8s API. In this test run, no resources were orphaned only because kserve-controller was blocked and had never sent manifests. Issue #8 confirms this is a known, unresolved problem.
- **Impact**: Secrets, ServiceAccounts, and PodDefaults created by the Metacontroller in user namespaces are not cleaned up when the requesting relation is removed, in real deployments where manifests were actually sent.
- **Fix**: Explicitly call `delete_many` against the removed relation's manifests via the K8s API on `relation-broken`, rather than relying solely on the Metacontroller.
- **Linter rule**: not mechanically checkable.

### Rev 611 regression: `_sync_manifests` drops the namespace-pinned directory layout
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/resource_dispatcher/v0/kubernetes_manifests.py` (rev 611 flat layout vs. rev 547 two-level layout)
- **Evidence**: Rev 611 writes all manifests flat as `{push_location}/{name}.yaml`. Local source writes namespace-pinned manifests to `{push_location}/{namespace}/{name}.yaml` and global manifests to `{push_location}/_global/{name}.yaml`, which the README documents as the expected layout.
- **Impact**: If rev 611 is deployed, the image-side dispatcher may be unable to distinguish global from namespace-pinned manifests.
- **Fix**: Restore the two-level directory layout in `_sync_manifests`.
- **Linter rule**: not mechanically checkable.

### Deprecated `resource_dispatcher.py` library shipped but unused
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/resource_dispatcher/v0/resource_dispatcher.py`
- **Evidence**: File docstring: "NOTE: This library should not be used anymore as it was incorrectly created. ... that other one [kubernetes_manifests.py] should be used instead." No imports of this library found anywhere in the codebase. Uses the old relation field name (`resource_dispatcher`), no secret support, and a distinct `LIBID` from `kubernetes_manifests.py`.
- **Impact**: Ships dead, self-contradicting code that would produce a broken result if any downstream developer imported it.
- **Fix**: Delete the file.
- **Linter rule**: "charm ships a library unused in the codebase" — mechanically checkable by cross-referencing library imports against usage.

### README bug-report URL points to the wrong repository
- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md` (~line 100)
- **Evidence**: README links bug reports to `https://github.com/canonical/seldon-core-operator/issues`, which is a different charm's tracker.
- **Impact**: Bugs get filed against the wrong repo.
- **Fix**: Point to `https://github.com/canonical/resource-dispatcher-operator/issues`.
- **Linter rule**: not mechanically checkable.

### `provide-cmr-mesh` declared in metadata but never implemented
- **Severity**: medium
- **Kind**: bug
- **Where**: `metadata.yaml:11–17`; `src/charm.py` (no handler code)
- **Evidence**: Searching `src/charm.py` for `cmr.mesh`/`cmr-mesh`/`cross_model` returns nothing — the interface is declared with no event handlers, relation-data access, or library.
- **Impact**: Dead interface declaration clutters `juju status`/`juju find` output.
- **Fix**: Implement the interface or remove the declaration.
- **Linter rule**: "charm declares a relation interface in `metadata.yaml` with no handler code" — mechanically checkable by cross-referencing metadata against framework observers.

### `_deploy_k8s_resources` has no leader check
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:161–173` (`_on_install`); `src/charm.py:174` (`_on_upgrade_charm`)
- **Evidence**: `_on_install`/`_on_upgrade_charm` call `_deploy_k8s_resources()` without first calling `_check_leader()`, unlike other K8s API operations in the charm.
- **Impact**: Inconsistent with the rest of the charm's leadership pattern; unlikely to cause visible problems since install fires once, but is a code-quality gap.
- **Fix**: Add `self._check_leader()` at the start of `_deploy_k8s_resources`, matching `_on_service_mesh_relation_events`/`_on_remove`.
- **Linter rule**: not mechanically checkable.

### Integration tests pre-deploy `metacontroller-operator` — install-hook failure path untested in CI
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py::test_deploy_metacontroller_setup`
- **Evidence**: This is the first integration test function and deploys `metacontroller-operator` and applies CRDs before `test_deploy_resource_dispatcher_charm` runs — the install hook has never been exercised against a cluster without the CRD pre-installed.
- **Impact**: The install-hook race (issue #66) is never caught by CI.
- **Fix**: Add a test deploying resource-dispatcher to a fresh model without `metacontroller-operator`, asserting the unit reaches `Active` or sets a meaningful `WaitingStatus`.
- **Linter rule**: not mechanically checkable.

### `update-status` fires `config-changed` twice on Juju 4.x
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:381` (`_on_event` bound to `on.update_status`)
- **Evidence**: Debug log shows two `config-changed` hooks running within milliseconds of each other for a single config change (Juju 4.x behaviour), each triggering the full `_check_leader`/`_check_container`/`_update_layer`/six `_update_manifests` sequence.
- **Impact**: Wastes compute and doubles API calls per config change.
- **Fix**: Debounce via a last-run timestamp, skipping if within a short window (e.g. 5s).
- **Linter rule**: not mechanically checkable.

### Unit tests use deprecated `Harness` class
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:117` and throughout
- **Evidence**: Every test fixture emits `PendingDeprecationWarning: Harness is deprecated...`.
- **Impact**: Deprecated test harness risks losing support; migration will require rework.
- **Fix**: Migrate to the `scenario` test framework.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Manifest conflict detection** (`_find_manifest_conflicts`): uses `collections.Counter` over `(namespace, name)` tuples to precisely define conflicts, with clear docstring and test coverage.
- **Two-level manifest layout** (`_sync_manifests`, current rev): namespace-pinned manifests under `{ns}/{name}.yaml`, global manifests under `_global/{name}.yaml`, with legacy flat-file cleanup and correct handling of the 404 `ApiError` for a non-existent push directory.
- **`KubernetesManifestsProvider` library** (current version): proper event sourcing (`KubernetesManifestsUpdatedEvent`), secret support, and the `JUJU_REMOTE_APP` workaround for relation-broken; `generate_secret_label`/`parse_relation_id_from_secret_label` are cleanly implemented.
- **Test coverage**: 91% statement coverage on `src/charm.py`, with clear parametrization across conflict-detection variants, layer update scenarios, and sync operations.
- **`generate_allow_all_authorization_policy`** (`charmed_kubeflow_chisme.service_mesh`): canonical workaround for the Metacontroller/Juju relations gap, allowing all traffic to the webhook.
- **Explicit upgrade-order documentation in tests**: `test_upgrade_erroneous_path.py`/`test_upgrade_happy_path.py` document correct and incorrect upgrade order and the expected error state, matching what was observed in the field.
- **`charm-user: non-root`**: runs as uid 584792, good security practice.
- **Poetry-based build**: poetry 2.0.0 with the `charmcraft.yaml` poetry plugin — modern and reproducible.

## Common-practice notes

- **`KubernetesResourceHandler` pattern**: uses `charmed-kubeflow-chisme`; `apply()`'s `force_recompute=False` caching is non-obvious and is the root cause of the CRD-staleness finding above.
- **`ErrorWithStatus` pattern**: `except ErrorWithStatus as err: self.model.unit.status = err.status` used consistently in `_on_event` — the standard pattern for charm-managed status.
- **Library versioning**: `kubernetes_manifests.py` uses `LIBID`/`LIBAPI`/`LIBPATCH`, standard pattern.
- **`concierge.yaml` uses microk8s 1.32**: CI/test environment is a real microk8s cluster, not a mocked Harness.
- **Terraform module** (`terraform/`): issue #130 reports it uses base 24.04, which breaks track/2.0/stable (only 20.04 available there).
- **`copy_libraries_into_tester_charm` fixture**: ensures tester charms use the current library version — good practice.
- **No explicit `relation-broken` K8s cleanup**: issue #8 confirms orphaned resources are a known, accepted tradeoff of relying on the Metacontroller's reconciliation loop.
- **ROCK layer `override: replace`**: intentional and correct — removes the ROCK's readiness check (which returns 418 and would otherwise cause repeated failures).

## Tests

**Unit tests**: 49 tests, all passing. `PYTHONPATH=src:lib poetry run coverage run --source=src -m pytest tests/unit -vv` — 91% coverage on `src/charm.py`, 46 `PendingDeprecationWarning`s (deprecated `Harness`). Categories: `TestCharm` (lifecycle hooks, leader/container checks, layer update, K8s resource deploy/remove, conflict detection, auth policy reconciliation), `TestManifestsValid` (6 parametrized conflict cases), `TestSyncManifests` (filesystem sync with legacy cleanup), `TestKubernetesManifest` (YAML validation), `TestManifestsProvider`/`TestManifestsRequirer` (relation data, plaintext and secret modes).

**Gaps**: no scenario tests; no test for the install hook with a missing CRD (the real failure path); no test for config-change with active relations; no test for the `relation-broken` → manifest cleanup path (issue #8); no test for `_on_service_mesh_relation_events` without container connectivity; no test for `_check_container` returning `False`; `_deploy_k8s_resources` is entirely mocked so its `ApiError` handler and success path are never exercised against a real K8s API client.

**Integration tests** (`test_charm.py`, `test_charm_ambient.py`, `test_upgrade_happy_path.py`, `test_upgrade_erroneous_path.py`): require `metacontroller-operator` pre-deployed and a `poddefaults.yaml` CRD applied. `test_upgrade_happy_path.py` deploys rev 547 (`RESOURCE_DISPATCHER_NO_SECRET`) first, then upgrades to local source — correct sequence. `test_upgrade_erroneous_path.py` explicitly tests the wrong order and expects the provider to go into `error` — matching what was observed in the field. These tests exercise local source (built from repo), which still has `config-maps`, not the published rev 611.

**Ruff lint**: `ruff check src/charm.py` — 6 errors (import order, explicit conversion flag, unused noqa, return-condition inlining, raise without name). `ruff check lib/charms/` — 31 errors (deprecated `typing.List`/`Optional[]`, `LOG015` root logger, `SIM201` negated equality).

## Docs

**README.md** (138 lines): sections are Description, Usage, Manifest conflict resolution, Charmed Kubeflow promotion. Gaps: no prerequisites section (metacontroller-operator requirement); no `--trust` documentation (issue #126); no explanation of which namespaces are affected beyond "specific kubernetes namespaces"; no mention of the six relation interfaces; no troubleshooting section; bug URL points to `seldon-core-operator/issues` instead of this repo's tracker.

**CONTRIBUTING.md** (206 lines): good contributing guide with PR checklist, test instructions, release process.

**terraform/README.md** (86 lines): explains terraform usage, but the module uses base 24.04, which breaks the stable track (issue #130).

**charmcraft.yaml**: modern poetry 2.0.0-based build, well-commented, handles Rust toolchain setup.

**charmhub description**: "Resource Dispatcher charm for injecting Kubernetes resources to desired namespaces." Minimal but accurate; does not mention the Metacontroller dependency.

## Open questions

1. **Rev 611 CRD template contents** (unverified): is the missing `configmaps` attachment in the post-refresh CRD due to rev 611's embedded template dropping it, or because applying a 5-resource manifest removed it from the existing CRD? Not established — requires comparing rev 611's embedded `decorator-controller.yaml.j2` against local source.
2. Does `_deploy_k8s_resources` running on a non-leader unit (no leader check) cause real problems in practice, given install fires once and that unit typically becomes leader? Not established.
3. Can `_on_service_mesh_relation_events` run without container connectivity? Likely yes since it uses the K8s API directly via lightkube, not the container — not testable without a working istio-pilot integration.
4. Why is `juju resolve` ineffective for the stuck error state after a bad relation? Because the hook keeps retrying while relation data (or the secret) still exists; the only observed recovery was killing the unit pod.
5. Is the ROCK's HTTP 418 readiness check intentional (a deliberate placeholder) or an oversight that should be removed from the rock entirely? Not established.
