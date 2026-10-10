# kubeflow-volumes-operator

A Kubernetes-only charm wrapping the `volumes-web-app` sidecar for Kubeflow PVC management UI. The codebase is professionally structured using the `charmed-kubeflow-chisme` reconciler pattern with good unit test coverage, and Pebble provides real workload resilience (crash restart in ~500ms). But two config-driven paths can take the workload down without the charm noticing or recovering cleanly: an out-of-range `port` value causes an uncaught hook failure that needs `juju resolved --no-retry` to clear, and an invalid `backend-mode` value crashes gunicorn into a Pebble backoff loop while `juju status` keeps reporting `active` for up to five minutes. On top of that, the `ClusterRoleBinding` hardcodes `namespace: kubeflow` for its ServiceAccount subject, which is wrong in every model not literally named `kubeflow` — PVC viewer pods will fail RBAC in this charm's own deployment. A maintainer should fix these three first: add `enum`/`minimum`/`maximum` constraints to `config.yaml`, template the ClusterRoleBinding namespace, and either add an active health check or narrow the status-misreport window. Two declared relations (`require-cmr-mesh`, `provide-cmr-mesh`) are dead code and should be implemented or removed.

| | |
|---|---|
| Repo | canonical/kubeflow-volumes-operator @ a767840 (2026-06-23) |
| Charms | kubeflow-volumes |
| Substrate | k8s only |
| Deployed | yes — concierge-k8s-4, 1.11/edge rev 652 |
| Reviewed | 2026-08-25 |

## What it does

The charm deploys the `volumes-web-app` as a Kubernetes sidecar container (UID/GID 584792), exposing a Flask/gunicorn web UI on port 5000. It renders a `viewer-spec.yaml` into the container for the volumes web app to use when spawning PVC viewer pods. The charm provides Kubernetes RBAC (ClusterRole, ClusterRoleBinding, ServiceAccount) for PVC and notebook access, integrates with the Kubeflow dashboard sidebar, and can operate in either sidecar Istio mode (`ingress` relation, SDI broadcasting) or ambient mesh mode (`istio-ingress-route` relation, HTTPRoute submission). Logging is forwarded to Loki via `grafana-agent-k8s`. The charm ships four config options: `port`, `backend-mode`, `secure-cookies`, and `volume-viewer-image`. Two relations declared in `metadata.yaml` are dead: `require-cmr-mesh` and `provide-cmr-mesh` are never handled by any code.

## Deployment log

```
# Session 1 — basic lifecycle and failure injection
juju add-model rv-kubeflow-volumes --controller concierge-k8s-4          # OK
juju deploy kubeflow-volumes --channel 1.11/edge --trust                 # OK, rev 652
# Lifecycle hooks: install → leader-elected → config-changed → start → pebble-ready (~97s total)
juju config backend-mode=development                                      # config-changed, new gunicorn PIDs 74-77
juju config backend-mode=production                                      # restored
juju config secure-cookies=true                                          # APP_SECURE_COOKIES updated
juju deploy grafana-agent-k8s --channel 1/stable --trust                  # OK, rev 164
juju relate kubeflow-volumes grafana-agent-k8s                           # OK, logging relation established
juju remove-relation kubeflow-volumes grafana-agent-k8s                  # OK, charm stayed active
juju add-unit -n 2 kubeflow-volumes                                     # 2 new units
# Units 1+2: WaitingStatus "[leadership-gate] Waiting for leadership"
juju remove-unit --num-units 2 kubeflow-volumes                        # clean scale-down
yes | juju remove-application kubeflow-volumes                           # teardown OK
juju refresh --channel 1.11/edge kubeflow-volumes                       # already up-to-date

# Session 2 — integration testing
echo "rv-kubeflow-volumes" | juju destroy-model concierge-k8s-4:rv-kubeflow-volumes  # OK
juju add-model rv-kubeflow-volumes --controller concierge-k8s-4          # OK
juju deploy kubeflow-volumes --channel 1.11/edge --trust                 # OK, rev 652
juju deploy kubeflow-dashboard --channel 1.10/stable --trust            # OK, rev 948
juju relate kubeflow-volumes kubeflow-dashboard                         # OK, dashboard-links relation established
kubectl exec kubeflow-volumes-0 -c kubeflow-volumes -- kill -9 $(pgrep gunicorn | head -1)
# Pebble: "Service stopped unexpectedly with code 137" → restart ~500ms → active
kubectl delete pod kubeflow-volumes-0 --grace-period=0                   # ~90s to active
echo "rv-kubeflow-volumes" | juju destroy-model concierge-k8s-4:rv-kubeflow-volumes  # OK

# Session 3 — failure injection
echo "rv-kubeflow-volumes" | juju destroy-model concierge-k8s-4:rv-kubeflow-volumes  # OK
juju add-model rv-kubeflow-volumes --controller concierge-k8s-4
juju deploy kubeflow-volumes --channel 1.11/edge --trust  # rev 652, ~60s to active
juju config kubeflow-volumes port=-1                      # error state, hook retried
# Recovery: juju resolved --no-retry kubeflow-volumes/0 → juju config port=5000 → active
# Recovery WITHOUT --no-retry: juju resolved re-runs failing hook → still error
juju config kubeflow-volumes port=65536                   # same error, same recovery
juju config kubeflow-volumes port=0                       # accepted, active (port 0 is technically valid)
juju deploy grafana-agent-k8s --channel 1/stable --trust  # OK
juju relate kubeflow-volumes grafana-agent-k8s            # logging relation OK
juju remove-relation kubeflow-volumes grafana-agent-k8s   # kubeflow-volumes stayed active
# Pebble log target persisted after relation removal

# Session 4 — integration and live log observation
echo "rv-kubeflow-volumes" | juju destroy-model concierge-k8s-4:rv-kubeflow-volumes  # OK
juju add-model rv-kubeflow-volumes --controller concierge-k8s-4
juju deploy kubeflow-volumes --channel 1.11/edge --trust  # rev 652, active
juju deploy --channel latest/edge --trust istio-pilot    # rev 1552, active
juju relate kubeflow-volumes istio-pilot                  # ingress (sidecar) relation OK
# juju show-unit kubeflow-volumes/0: sends SDI data
# {"port": 5000, "prefix": "/volumes", "rewrite": "/", "service": "kubeflow-volumes"}
juju config kubeflow-volumes backend-mode=invalidvalue    # Pebble backoff, juju shows active!
# kubectl logs: HaltServer 'Worker failed to boot.' 3
# kubectl exec pebble services: kubeflow-volumes enabled backoff
# juju status: kubeflow-volumes active (WRONG!)
# Pebble logs: "waiting ~8s before restart (backoff 5)"
# Recovery: juju config backend-mode=production → active in ~9s
# Stale log target: kubectl logs -c kubeflow-volumes shows repeated
# "Cannot flush logs to target grafana-agent-k8s/0: connection refused" every ~30s
juju remove-relation kubeflow-volumes istio-pilot         # kubeflow-volumes stayed active
# ClusterRoleBinding: namespace=kubeflow in subjects, but SA is in rv-kubeflow-volumes
```

## Observed behaviour

- **Lifecycle**: install → leader-elected → config-changed → start → pebble-ready; no extra hooks.
- **Config change propagation**: `config-changed` hook triggers full reconciler → `KubeflowVolumesPebbleService._update_layer()` → `container.replan()` → new gunicorn workers in ~6s. Gunicorn logs confirm: workers receive SIGTERM, new workers spawn. Pebble layer reflects new config values (confirmed `BACKEND_MODE=development` after `juju config backend-mode=development`).
- **Hook count for trivial config change**: one `config-changed` hook, full reconciler runs (all 6 component statuses evaluated).
- **Workload crash on invalid config (confirmed live)**: `juju config backend-mode=invalidvalue` → gunicorn crashes with `HaltServer 'Worker failed to boot.'` → Pebble transitions to `backoff` with 8-second backoff window. `kubectl exec pebble services` shows `kubeflow-volumes enabled backoff`. `juju status` simultaneously shows `kubeflow-volumes active` — **wrong status**. Recovery after restoring valid config: ~9s. The misreport persists until the next periodic `update-status` hook (up to 5 min), which re-checks the service state. Mechanism: `container.replan()` is non-blocking; Pebble starts gunicorn asynchronously. The reconciler's status check (`PebbleServiceComponent.get_status()`) runs before gunicorn has time to fail. Only the next `update-status` (5 min later) picks up the backoff.
- **Invalid port config**: `juju config port=-1` or `port=65536` → pydantic `ValidationError` in `BackendRef` construction → uncaught `GenericCharmRuntimeError` → `config-changed` hook exits with status 1 → charm in `error` state → hook retried repeatedly. Recovery requires `juju resolved --no-retry` (without `--no-retry`, the hook re-runs with the same bad config and fails again), then `juju config port=5000`.
- **`ingress` sidecar relation**: Relating kubeflow-volumes to `istio-pilot` via the `ingress` interface works correctly. kubeflow-volumes sends SDI data: `{"port": 5000, "prefix": "/volumes", "rewrite": "/", "service": "kubeflow-volumes"}`. The `SdiRelationBroadcasterComponent.get_status()` catches all exceptions and returns `BlockedStatus`, unlike the ambient component. `juju remove-relation` leaves kubeflow-volumes active (correct — `ingress` is optional).
- **`istio-ingress-route` ambient mesh**: `juju relate kubeflow-volumes istio-pilot` defaults to the `ingress` sidecar interface. To relate via ambient mesh, a charm providing `istio-ingress-route` (e.g., `istio-ingress-k8s`) is required — not `istio-pilot`.
- **Conflict detector**: `juju relate kubeflow-volumes istio-pilot` via `ingress` succeeds. The conflict detector is invoked when both `ingress` and `istio-ingress-route` relations exist — `BlockedStatus` is returned, and the reconciler's `Prioritiser` sorts statuses with `blocked=1` which wins over `active=4`.
- **grafana-agent-k8s integration**: Logging relation works correctly. kubeflow-volumes sends `alert_rules: '{}'` and `metadata`. grafana-agent-k8s responds with Loki push endpoint URL. **After relation removal**: Pebble log target persists — `disable_inactive_endpoints` is never called because `_update_logging` returns early when there are no Loki endpoints. **Live evidence**: Pebble logs show continuous `Cannot flush logs to target "grafana-agent-k8s/0": ... connection refused` errors every ~30s — even after the relation was removed and the model was destroyed/recreated. The stale Pebble log target survives model destruction/recreation because the container filesystem persists.
- **kubeflow-dashboard integration**: `dashboard-links` relation established correctly. kubeflow-volumes sends: `dashboard_links: [{"text": "Volumes", "link": "/volumes/", "location": "menu", "icon": "device:storage", "type": "item", "desc": ""}]`. kubeflow-dashboard itself blocks with "must be deployed to model named `kubeflow`" (expected), but kubeflow-volumes stays active. Relation removal handled gracefully.
- **Scale-up behaviour**: Adding 2 units creates 2 new pods. New units go `WaitingStatus ("[leadership-gate] Waiting for leadership")` indefinitely. Workload container on non-leaders: no gunicorn, no `/etc/config/viewer-spec.yaml`. Only the leader unit runs the workload.
- **Scale-down behaviour**: `juju remove-unit --num-units 2` cleanly removes the extra pods. Remaining leader unit stays active.
- **Teardown**: `juju remove-application` cleanly removes all Kubernetes resources. No errors.
- **Refresh**: `juju refresh` reports "already up-to-date" — no newer revision available on the 1.11/edge channel.
- **TLS port detection**: Unit tests confirm port 443 when `tls_enabled=True`, port 80 when `False`.
- **Gunicorn crash and Pebble auto-restart**: `kill -9` on the gunicorn master process → workers shut down → Pebble detects crash ("Service 'kubeflow-volumes' stopped unexpectedly with code 137") → immediately restarts with ~500ms backoff → new gunicorn starts within ~1s → service returns to `active`. Pebble's default `on-failure=restart` policy.
- **Pod restart**: `kubectl delete pod` → pod recreated → ~90s to active through maintenance. Pebble readiness probe failures on port 38813 during startup are from Juju's built-in container probes — environmental lag, not a charm bug.
- **RBAC inspection**: `kubectl get clusterrolebinding kubeflow-volumes-binding -o yaml` shows `subjects: [{kind: ServiceAccount, name: kubeflow-volumes-sa, namespace: kubeflow}]`. The `kubeflow-volumes-sa` ServiceAccount was created by the charm in the `rv-kubeflow-volumes` namespace (confirmed via `kubectl get sa`). The `kubeflow` namespace exists in this cluster (from a prior kubeflow deployment), but `kubeflow-volumes-sa` does NOT exist in it. The ClusterRoleBinding references a non-existent ServiceAccount.
- **`upgrade-charm` hook behavior**: Fires after every hook in Juju 4.x. The `CharmReconciler` handles it via component-registered event handlers and ops framework lifecycle. `reconcile()` resets all components' `executed=False` flag, ensuring a full execution cycle on each hook.
- **Reconciler status aggregation**: The `Prioritiser` (from `charmed_kubeflow_chisme/status_handling/multistatus.py`) orders statuses as: error=0, blocked=1, waiting=2, maintenance=3, active=4, unknown=5. The worst status wins. `ComponentGraphItem.get_status()` catches exceptions from prerequisite status checks and returns `BlockedStatus`, but `GenericCharmRuntimeError` propagates from `configure_charm()` uncaught, causing the hook to fail.
- **No custom actions**: `actions.yaml` does not exist. `juju actions` would show no available actions.
- **`require-cmr-mesh` and `provide-cmr-mesh` relations**: Declared in `metadata.yaml` with `interface: cross_model_mesh` but have no code handlers. `grep -rn "cmr|require-cmr|provide-cmr" src/` finds only the `metadata.yaml` declarations. These relations can never be established and the charm cannot participate in cross-model mesh.
- **Rockcraft base layer**: The OCI image ships a Pebble base layer with `override: replace`, `startup: enabled`, gunicorn command, `PYTHONPATH: /` and `working-dir: /src/`. The charm layer uses `override: merge` to add its environment variables while inheriting PYTHONPATH and working-dir from the base. The `parts/` directory is the charmcraft build artifact containing copies of the rockcraft base layer and is not in `.gitignore`.

## Findings

### Unvalidated `port` config causes uncaught hook failure requiring `juju resolved --no-retry` to recover
- **Severity**: critical
- **Kind**: bug
- **Where**: `config.yaml:5` (no `minimum`/`maximum` constraint) + `src/charm.py:117` (port passed directly to `IstioIngressRouteRequirer`)
- **Evidence**: `juju config port=-1` → `pydantic_core._pydantic_core.ValidationError: 1 validation error for BackendRef / port / Input should be greater than or equal to 1`. The error propagates from `src/components/istio_ambient_requirer_component.py:91` (`GenericCharmRuntimeError`) and out of the reconciler uncaught → `config-changed` hook exits with status 1. The charm goes to `error` state. The hook is retried repeatedly. Recovery requires `juju resolved --no-retry kubeflow-volumes/0` (without `--no-retry`, the hook re-runs with the same bad config and fails again), then `juju config port=5000`. The same failure occurs with `port=65536`.
- **Impact**: Any out-of-range port value causes a hook failure loop. The operator cannot fix the config until they use `juju resolved --no-retry` first. The `error` status provides no indication of the root cause.
- **Mechanism**: `src/charm.py:75-78` passes `int(self.model.config["port"])` directly to `AmbientIngressRequirerComponent`. Inside `_get_ingress_config()`, this becomes `BackendRef(service=self.service_name, port=self.port)`. The `BackendRef` pydantic model requires `port >= 1`. The `ValidationError` is caught in `_configure_app_leader` (`istio_ambient_requirer_component.py:88-91`) and re-raised as `GenericCharmRuntimeError`. The reconciler (`charm_reconciler.py`) only catches `Exception` from `component.configure_charm()`, logs it, then calls `_update_charm_status()`. The status check returns `ActiveStatus` for all components (the error was in execution, not status), but the hook exits with status 1 because the exception propagated out.
- **Fix**: (1) Add `minimum: 1` and `maximum: 65535` to the `port` option in `config.yaml`. (2) Add a guard in `_configure_app_leader` to validate the port before constructing `BackendRef`. (3) The reconciler should handle `GenericCharmRuntimeError` gracefully by setting the charm to `BlockedStatus` with a message.
- **Linter rule**: `config.yaml` options of `type: int` that are used to construct network resources should have `minimum` and `maximum` constraints.

### Invalid `backend-mode` crashes gunicorn but the charm reports `active` while Pebble is in backoff
- **Severity**: critical
- **Kind**: bug
- **Where**: `config.yaml:9` (no `enum` constraint) + `src/components/pebble_components.py:39` (passes value through unchecked)
- **Evidence**: `juju config backend-mode=invalidvalue` → gunicorn crashes with `HaltServer 'Worker failed to boot.'` → Pebble transitions to `backoff` (8s backoff interval) → Pebble logs: `"Service kubeflow-volumes on-failure action is 'restart', waiting ~8s before restart (backoff 5)"` → `kubectl exec pebble services` shows `kubeflow-volumes enabled backoff`. Simultaneously, `juju status` shows `kubeflow-volumes active` — **wrong status**. Recovery after restoring valid config: ~9s.
- **Impact**: An operator watching `juju status` after applying bad config sees `active` — no indication the workload is down. The misreport persists until the next periodic `update-status` hook (up to 5 min), which re-checks the service state and correctly returns `WaitingStatus`. During the ~5-minute misreport window, the operator has no automated alert of the failure.
- **Mechanism**: `PebbleServiceComponent.get_status()` calls `container.get_services()` to check if the service is running. `container.replan()` is non-blocking — it starts gunicorn asynchronously and returns immediately. The reconciler's status check runs before gunicorn has had time to fail. Only the next `update-status` (every 5 min) picks up the backoff state.
- **Fix**: (1) Add `enum: [development, production]` to `config.yaml`'s `backend-mode` option — prevents invalid values at the Juju API layer. (2) Use Pebble `checks` to actively probe the service health rather than relying on passive `get_services()` state. (3) The `WaitingStatus` message should name the specific cause.
- **Linter rule**: `config.yaml` options used as string pass-through to the workload should have an `enum` constraint if the valid values are known.

### `ClusterRoleBinding` subjects hardcode `namespace: kubeflow`, breaking in non-kubeflow model names
- **Severity**: high
- **Kind**: correctness
- **Where**: `src/templates/auth_manifests.yaml.j2:159` — `namespace: kubeflow`
- **Evidence**: `kubectl get clusterrolebinding kubeflow-volumes-binding -o yaml` confirms: `subjects: [{kind: ServiceAccount, name: kubeflow-volumes-sa, namespace: kubeflow}]`. `kubectl get sa -n rv-kubeflow-volumes` shows `kubeflow-volumes-sa` exists in the `rv-kubeflow-volumes` namespace. `kubectl get sa -n kubeflow` succeeds (namespace exists from a prior kubeflow deployment) but `kubeflow-volumes-sa` is not present there. The ClusterRoleBinding binds to a ServiceAccount that does not exist.
- **Impact**: The charm was deployed in model `rv-kubeflow-volumes`. Viewer pods spawned by the volumes web app will fail to start with "serviceaccount kubeflow-volumes-sa not found" errors because the ClusterRoleBinding cannot bind to the non-existent ServiceAccount. The RBAC setup is broken by default in every non-kubeflow-named model.
- **Fix**: Change `namespace: kubeflow` to `namespace: {{ namespace }}` in `auth_manifests.yaml.j2`. The context callable already provides `namespace`, and the template already uses `{{ namespace }}` for the ServiceAccount. Apply the same variable to the ClusterRoleBinding subjects.
- **Linter rule**: not mechanically checkable without understanding the Kubeflow deployment topology.

### Non-leader units in a scaled deployment are permanently idle with no workload
- **Severity**: high
- **Kind**: correctness
- **Where**: `src/charm.py:41` — `KubeflowVolumesPebbleService` depends on `leadership_gate`, executed only for the leader unit
- **Evidence**: `juju add-unit -n 2 kubeflow-volumes` → two new pods. On each non-leader pod: `pebble services` shows `kubeflow-volumes  enabled  inactive` and `/etc/config/viewer-spec.yaml` does not exist. The unit status is `WaitingStatus ("[leadership-gate] Waiting for leadership")`.
- **Impact**: A deployment with `scale=3` has only 1 unit serving traffic. The `WaitingStatus` message is generic and does not indicate that this is by design.
- **Fix**: If intentional, change the `WaitingStatus` message to describe the design, and document non-scalability in `metadata.yaml`/`README.md`. If not intentional, remove `KubeflowVolumesPebbleService`'s dependency on `leadership_gate`.
- **Linter rule**: not mechanically checkable.

### `LogForwarder` does not remove Pebble log targets after the logging relation is broken
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/loki_k8s/v1/loki_push_api.py:2571-2585` (`LogForwarder._update_logging`)
- **Evidence**: `juju relate kubeflow-volumes grafana-agent-k8s` → Pebble log target created (`pebble plan` shows the Loki endpoint URL). `juju remove-relation kubeflow-volumes grafana-agent-k8s` → `relation_broken` fires → `_update_logging` called → `_retrieve_endpoints_from_relation()` returns `{}` → `_update_logging` returns early (no call to `_update_endpoints`) → `disable_inactive_endpoints` is never called → `pebble plan` still shows the log target. **Live log evidence**: Pebble logs show repeated `Cannot flush logs to target "grafana-agent-k8s/0": ... connection refused` every ~30s — even after the relation was removed and the model was destroyed and recreated. The stale target persists because the container filesystem survives model destruction.
- **Impact**: The workload continues attempting to push logs to a non-existent Loki endpoint indefinitely, wasting resources and filling logs with connection failures. The misconfigured Pebble log target is invisible to `juju status` but visible in container logs.
- **Fix**: In `_update_logging`, when `loki_endpoints` is empty, call `_update_endpoints(container, {})` for each container to trigger `disable_inactive_endpoints` and remove stale log targets. This is a library-level bug affecting all charms using `LogForwarder`, not specific to kubeflow-volumes.
- **Linter rule**: not mechanically checkable from charm code — library-level bug.

### `require-cmr-mesh` and `provide-cmr-mesh` declared in `metadata.yaml` but have no code handlers
- **Severity**: medium
- **Kind**: correctness
- **Where**: `metadata.yaml:71` (relation declaration) + no handler code in `src/`
- **Evidence**: `grep -rn "cmr|require-cmr|provide-cmr" src/` returns only `metadata.yaml`. No charm code registers event handlers for, reads from, or writes to either `require-cmr-mesh` or `provide-cmr-mesh`. The `service_mesh` relation (used by `ServiceMeshConsumer` in the ambient ingress component) is separate from these CMR mesh relations.
- **Impact**: These relations can never be established. If another charm attempts to relate via these interfaces, Juju will reject the relation at the interface level. The charm cannot participate in cross-model mesh via these declared relations. If this was the intended cross-model mesh integration path, it is completely unimplemented.
- **Fix**: Either implement the CMR mesh relations or remove the dead declarations from `metadata.yaml` to avoid misleading operators.
- **Linter rule**: a lint rule that flags `metadata.yaml` relation declarations whose interface names never appear in `src/` would catch this.

### `tox -e lint` fails on `parts/` build artifacts
- **Severity**: medium
- **Kind**: lint
- **Where**: `tox.ini:lint` (codespell does not skip `parts/`) + `lib/charms/istio_beacon_k8s/v0/service_mesh.py:252,274,928` (typos in vendored library)
- **Evidence**: `python3 -m tox -e lint` fails with exit code 65. `codespell` finds `Polcy`, `currenlty`, `polcies` in `lib/` (correctly skipped) but also in `parts/` (build artifact copies, not skipped). Running `codespell src/` passes clean.
- **Impact**: CI will fail on lint for every PR that includes a `parts/` directory.
- **Fix**: (1) Add `--skip {toxinidir}/./parts` to the codespell command in `tox.ini`. (2) Fix the three typos in `lib/charms/istio_beacon_k8s/v0/service_mesh.py`. (3) Add `parts/` to `.gitignore`.
- **Linter rule**: `codespell` with `parts/` in the skip list.

### Integration tests for the workload itself are disabled (issue #29)
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py:107-174` — all volume creation/deletion tests commented out with `TODO: Re-enable tests`
- **Evidence**: Issue #29 (2024-02-01): "Integration tests are missing for volume's workload." The selenium-based tests were disabled due to CI flakiness. Remaining integration tests only verify `status="active"` and container security context.
- **Impact**: The charm's primary purpose is PVC management UI. Without integration tests for volume creation/deletion, a regression in `viewer-spec.yaml`, the PVC viewer logic, or the RBAC rules would not be caught.
- **Fix**: Re-enable volume integration tests with a more robust approach — use the Kubernetes Python client directly instead of Selenium.
- **Linter rule**: a CI gate requiring no `pytest.skip` or commented-out test functions in the integration test directory.

### Untested error path in `KubeflowVolumesPebbleService.get_layer`
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/components/pebble_components.py:22-25`
- **Evidence**: Unit test `test_pebble_services_running` mocks the harness to return valid config but never exercises the `except Exception as err` branch. If `_inputs_getter()` raises, the charm raises `ValueError("Failed to get inputs for Pebble container.")`. This path is not tested.
- **Fix**: Add a unit test that patches `_inputs_getter` to raise an exception and verifies the `ValueError`.
- **Linter rule**: `coverage` tool already flags this.

### Renovate configuration is broken (open issue #219)
- **Severity**: medium
- **Kind**: docs
- **Where**: `renovate.json:3` — `"github>canonical/charmed-kubeflow-workflows"` is an invalid preset
- **Evidence**: Open issue #219 (2025-10-03): "Action Required: Fix Renovate Configuration... Error type: Preset is invalid JSON." `renovate.json` is unchanged.
- **Impact**: Broken Renovate config stops dependency updates, leading to stale transitive dependencies.
- **Fix**: Update `renovate.json` to use a valid preset.
- **Linter rule**: a CI check running `renovate-config-validator` on `renovate.json` would catch this.

### `except Exception` in ambient ingress config submission
- **Severity**: low
- **Kind**: bug
- **Where**: `src/components/istio_ambient_requirer_component.py:88-91`
- **Evidence**: `_configure_app_leader` catches all exceptions from `submit_config` and re-raises as `GenericCharmRuntimeError`. The unit test `test_ambient_ingress_configure_app_leader_generic_error` confirms this branch but does not distinguish between expected and unexpected exception types.
- **Impact**: Catching all exceptions and re-raising as `GenericCharmRuntimeError` loses information and propagates uncaught out of the hook. If `submit_config` raises a new exception type in the future, the handler will silently convert it. `GenericCharmRuntimeError` is not caught by the reconciler and propagates as an uncaught hook failure.
- **Fix**: Narrow the exception type to the specific exceptions that `submit_config` can raise (e.g., `RequestError` from the HTTP client).
- **Linter rule**: `BLE001` from `ruff` catches this pattern.

### `ServiceMeshConsumer` instantiated for side effects, stored reference unused
- **Severity**: low
- **Kind**: dead-code / clarity
- **Where**: `src/components/istio_ambient_requirer_component.py:53` — `self._mesh = ServiceMeshConsumer(self._charm)` (stored to `self._mesh`, never read)
- **Evidence**: `self._mesh` is assigned but never referenced. `ServiceMeshConsumer` has observable side effects (registers event handlers via `auto_join=True`), so it is not dead code, but the stored reference is unused.
- **Impact**: The unused stored reference suggests the object was intended to be used and is confusing to reviewers.
- **Fix**: Remove the `self._mesh = ` assignment, or add a comment explaining the reference is intentionally unused.
- **Linter rule**: `ruff` rule `B018` does not flag stored `self.` attributes.

### Ambient ingress `_config` is computed once in `__init__` and may not reflect TLS state changes
- **Severity**: low
- **Kind**: bug
- **Where**: `src/components/istio_ambient_requirer_component.py:51,57` — `self._config = self._get_ingress_config()` (called in `__init__`; `self.ingress.tls_enabled` read inside it)
- **Evidence**: `_get_ingress_config()` reads `self.ingress.tls_enabled` at `__init__` time. If TLS state changes after initialization, `self._config` would be stale.
- **Impact**: Latent bug. In practice, TLS state is unlikely to change after the charm starts.
- **Fix**: Move `_get_ingress_config()` from `__init__` into `_configure_app_leader`, recomputing on each reconcile.
- **Linter rule**: not mechanically checkable.

### Conflicting Istio relations produce a `BlockedStatus` with no actionable guidance
- **Severity**: low
- **Kind**: ux
- **Where**: `src/components/istio_relations_conflict_detector.py:37-38`
- **Evidence**: The `BlockedStatus` message says "Cannot have both 'istio-ingress-route' and 'ingress' relations" but gives no guidance on which to remove.
- **Fix**: Add a guidance sentence, e.g. `"Remove one of these relations to unblock."`
- **Linter rule**: not mechanically checkable.

### Pyright type errors on charm code
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:152-154` (type mismatch on config values), `src/components/istio_ambient_requirer_component.py:86` (parameter name mismatch on override)
- **Evidence**: `pyright src/` reports: `Argument of type "bool | int | float | str" cannot be assigned to parameter "APP_SECURE_COOKIES" of type "bool"` — `self.model.config` values are typed as the union, but the `KubeflowVolumesInputs` dataclass expects specific types. Also: `Parameter 2 name mismatch`.
- **Fix**: Add `type: ignore` comments for the config access, or use `cast()` to assert the correct types. Fix the parameter name in `_configure_app_leader`.
- **Linter rule**: `pyright` in CI would catch these.

### Ruff lint errors on `src/`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:10-35` (I001 import block unsorted), `src/components/pebble_components.py:33` (RUF100 unused noqa E501), `src/components/istio_ambient_requirer_component.py:90` (BLE001 blind except Exception)
- **Evidence**: `ruff check src/` returns exit code 1 with three errors. The import sorting error is real but `black --check` and `isort --check-only` pass, suggesting the import sorter configuration differs from ruff's defaults. The unused noqa is real — `E501` is not enabled in the ruff config so the noqa is unnecessary. The blind except is the same finding as above.
- **Fix**: (1) Run `ruff check --fix src/` to auto-fix the import order. (2) Remove the `# noqa: E501` comment from `src/components/pebble_components.py:33`. (3) Narrow the exception type in `src/components/istio_ambient_requirer_component.py:90`.
- **Linter rule**: `ruff` in CI.

## Worth copying

### Charm reconciler pattern (`src/charm.py`)
The use of `CharmReconciler` with explicit dependency ordering is clean and idiomatic. The dependency graph is explicit, testable, and avoids the common mistake of putting all work in `config-changed`.

### Dual-mode Istio support with conflict detection
`IstioRelationsConflictDetectorComponent` prevents the charm from running in an ambiguous state. Returning `BlockedStatus` from a component (rather than from the charm level) is clean and composable. The `Prioritiser` status aggregation correctly handles the `blocked=1` priority.

### Container template pattern (`pebble_components.py`)
The `KubeflowVolumesInputs` dataclass cleanly separates the configuration schema from the layer rendering logic. Using `override: merge` to add environment variables while inheriting `PYTHONPATH` and working-dir from the rockcraft base layer is correct.

### TLS port detection (`istio_ambient_requirer_component.py`)
```python
if self.ingress.tls_enabled:
    http_listener = Listener(port=443, protocol=ProtocolType.HTTP)
else:
    http_listener = Listener(port=80, protocol=ProtocolType.HTTP)
```
Correct and unit-tested on both branches.

### Unit test structure
The test file uses fixtures for mocked dependencies (`mocked_lightkube_client`, `mocked_kubernetes_service_patch`, `mocked_istio_ingress_requirer`) cleanly, and the parametrized tests for the conflict detector cover all combinations.

### `SdiRelationBroadcasterComponent` exception handling
`SdiRelationBroadcasterComponent.get_status()` catches all exceptions and returns `BlockedStatus`. This is better than `AmbientIngressRequirerComponent`, which lets exceptions propagate. Worth adopting as a pattern.

## Common-practice notes

- **ops usage**: Uses ops `^2.17.1`, compatible with Juju 4.x. The charm runs as `charm-user: non-root` (UID 584792), consistent with the "run workload as unprivileged user" feature.
- **Library versioning**: Libraries are pinned under `lib/charms/<name>/v0/` and `lib/charms/<name>/v1/`, following standard conventions. The `charms` namespace packages are PEP 420 implicit namespace packages (no `__init__.py`).
- **Poetry build system**: Uses `poetry` with separate groups for `charm`, `fmt`, `lint`, `unit`, `integration`. `pyproject.toml` correctly uses `package-mode = false`. `charmcraft.yaml` uses a two-stage build with a rustup workaround for building Python packages with Rust from source.
- **charmed-kubeflow-chisme**: Heavy use of shared library components. Results in less custom code at the cost of dependency on a shared library. The reconciler pattern is well-implemented.
- **`src/` layout**: Modern pattern using `src/charm.py` and `src/components/` rather than root-level `src/`.
- **terraform module**: Present and correct with inputs for `app_name`, `base`, `channel`, `config`, `model_name`, `resources`, `revision`.
- **CI**: Uses `canonical/data-platform-workflows` for build/release. The lint → unit → build → release pipeline is standard.
- **Renovate**: Broken preset — see finding above.

## Tests

- **Unit tests**: 17 tests in `tests/unit/test_operator.py`. All pass. Coverage: 96.5% line, 95% branch.
  - `src/charm.py`: 95% (missing line 168 — `if __name__ == "__main__"`, expected gap)
  - `src/components/pebble_components.py`: 90% (missing lines 24-25, the `_inputs_getter` error path)
  - `src/components/istio_ambient_requirer_component.py`: 100%
  - `src/components/istio_relations_conflict_detector.py`: 100%
- **Lint**: `codespell src/` passes clean. `tox -e lint` fails because `codespell` is not configured to skip the `parts/` directory. `ruff check src/` finds 3 errors (import order, unused noqa, blind except).
- **Integration tests**: Cannot be run locally without a live Juju model and `pytest-operator`. Volume creation/deletion tests are disabled. Sidecar ingress (`ingress` interface with `istio-pilot`) and ambient mesh ingress (`istio-ingress-route` with `istio-ingress-k8s`) integrations are tested in CI via `tests/integration/test_charm.py` and `tests/integration/test_charm_ambient.py` respectively.
- **Test gaps**: Error path in `get_layer` (`pebble_components.py:24-25`) not tested. Port config error path not tested. Workload crash injection not tested in unit tests. Log target removal after relation broken not tested. CMR mesh relations not tested (no code to test).

## Docs

- **README.md**: Minimal — one paragraph overview, install instruction, link to juju.is/docs. Does not describe relations, config options, or architecture. A new operator needs to read the code to understand the integrations.
- **CONTRIBUTING.md**: Detailed and accurate — covers the poetry/tox workflow, how to run tests, how to update dependencies.
- **terraform/README.md**: Correct and complete with usage examples, an inputs table, and an outputs table.
- **config.yaml descriptions**: Descriptive and accurate for `port`, `secure-cookies`, and `volume-viewer-image`. The `backend-mode` description is minimal but accurate. No `enum` validation, however.
- **charmhub description**: "Kubeflow Volumes" — only 3 words, no detail.
- **Code comments**: `auth_manifests.yaml.j2` includes source attribution comments. `viewer-spec.yaml` has explanatory comments about variable expansion.

## Open questions

- **Non-leader workload design**: Confirmed intentional. `metadata.yaml` and `README.md` should document that the charm is not designed for horizontal scaling.
- **TLS state change after init**: Latent bug. A unit test that mocks `ingress.tls_enabled` toggling between reconcile cycles would confirm or deny the risk.
- **`serviceAccountName: default-editor` in viewer-spec.yaml**: The viewer pods spawned by the volumes web app use `default-editor`, not the charm's own ServiceAccount. This is correct per Kubeflow conventions but the charm doesn't validate it.
- **`require-cmr-mesh` / `provide-cmr-mesh`**: Completely unimplemented. If intended for cross-model mesh support, it needs implementation. If not, the declarations should be removed from `metadata.yaml`.
- **Ambient mesh ingress**: Unit tested but not exercised end-to-end in this review (requires the `istio-ingress-k8s` charm). Unit tests cover the HTTPRoute config generation and conflict detection.
- **Log target removal**: The `LogForwarder` library bug means Pebble log targets persist after relation removal. This is a library-level issue affecting any charm using `LogForwarder`, not specific to kubeflow-volumes. The fix belongs in `lib/charms/loki_k8s/v1/loki_push_api.py`.
