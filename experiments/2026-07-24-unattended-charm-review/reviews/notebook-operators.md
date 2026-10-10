# notebook-operators

Two Kubernetes charms (`jupyter-controller`, `jupyter-ui`) that together run the Kubeflow
multi-user Jupyter notebook stack. `jupyter-controller` deploys the notebook-controller
image and owns the notebook CRD ClusterRoles; `jupyter-ui` deploys the jupyter-web-app
image and manages the spawner configmap. Both run as non-root (uid/gid 584792) and use a
modern poetry/rust build.

**Verdict**: functionally solid for the happy path — install, config, scaling, and
teardown all work — but the charms have no self-healing story for relation and workload
failures. `jupyter-ui`'s `ingress-relation-broken` hook has no handler, so removing an
ingress relation leaves the unit permanently stuck in `WaitingStatus` with a stale
message until an operator forces a `config-changed`. `jupyter-controller`'s
`pebble-check-failed` hook is likewise unhandled, so a stopped workload takes ~5 minutes
to recover instead of seconds. `juju refresh` for `jupyter-ui` left the application
completely broken (invalid workload image, unrecoverable without force-remove and
redeploy). A maintainer should fix the two missing relation/check handlers first, then
investigate the `juju refresh` breakage before recommending in-place upgrades to users.
The `EXPERIMENTAL_*` env vars and ambient-mesh relations present in local source are
absent from every published track — a maintenance gap, not a runtime bug — and `use-istio`
is dead code in the deployed charm.

| | |
|---|---|
| Repo | canonical/notebook-operators @ `06cefb2` (2026-06-17) |
| Charms | jupyter-controller, jupyter-ui |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4, jupyter-controller 1.10/edge rev 1528, jupyter-ui 1.10/edge rev 1452 |
| Reviewed | 2026-08-23 |

## What it does

**jupyter-controller**: deploys the Kubeflow notebook-controller as a workload container,
applies ClusterRole/ClusterRoleBinding manifests, owns the notebook CRD, exposes
metrics/prometheus/grafana/loki endpoints. Supports Istio sidecar mode (the only mode in
the published charm) and ambient mesh mode (local source only, not published).

**jupyter-ui**: deploys the Kubeflow jupyter-web-app image, renders
`spawner_ui_config.yaml` into the container from user-supplied config (images, GPU,
affinity, tolerations, etc.), supports both Istio sidecar (`ingress` relation) and
ambient (`istio-ingress-route`) modes.

## Deployment log

```
# Create model
juju add-model rv-notebook-ops -c concierge-k8s-4

# Deploy from charmhub
juju deploy jupyter-controller --channel 1.10/edge --trust   # rev 1528
juju deploy jupyter-ui --channel 1.10/edge --trust            # rev 1452

# Timings:
# - Both charms: install → active/idle in ~2-3 minutes
# - K8s resources created: ~10 seconds per charm
# - Both pods: 2/2 Running, 0 restarts after 30+ minutes

# Config changes tested:
juju config jupyter-controller cull-idle-time=60      # CULL_IDLE_TIME="60" ✓
juju config jupyter-controller idleness-check-period=2  # IDLENESS_CHECK_PERIOD="2" ✓
juju config jupyter-ui url-prefix=/test-jupyter       # APP_PREFIX updated ✓
juju config jupyter-controller cull-idle-time=-5      # accepted silently, CULL_IDLE_TIME="-5" ✓
juju config jupyter-controller cull-idle-time=9999999 # triggers maintenance then recovers ✓
juju config jupyter-ui jupyter-images='{ invalid yaml }' # accepted silently, fallback to empty ✓
juju config jupyter-ui gpu-vendors-default="invalid-vendor" # accepted silently, vendors=[], default="" ✓

# juju refresh (jupyter-controller 1.10/edge rev1528 → latest/edge rev1539):
juju refresh jupyter-controller --channel latest/edge
# FAILED: "one or more of the provided endpoints ... do not exist"
# Charm entered maintenance, recovered to active after ~15s ✓

# Process kill (failure injection, jupyter-controller):
kubectl exec ...jupyter-controller-0 -c jupyter-controller -- kill <pid>
  # Pebble auto-restart <5s ✓
  # pebble services: active; pebble logs show clean startup at 20:31:01 UTC ✓

# Scale up: juju add-unit jupyter-controller -n 2
  # 3 units: /0 (leader, active), /1 and /2 (non-leaders, pebble service INACTIVE ✓)
  # Non-leaders don't run the manager (leader election) — correct

# Scale down: juju remove-unit jupyter-controller/1 jupyter-controller/2
  # Units removed from juju state ✓
  # BUT orphaned pods remain: jupyter-controller-1 and jupyter-controller-2
  #   stuck at 1/2 Ready (charm container unhealthy). K8s-level issue, not charm bug.

# Relation removal: juju remove-relation grafana-agent-k8s:metrics-endpoint jupyter-controller
  # jupyter-controller stays active ✓
  # grafana-agent-k8s goes blocked (missing metrics source) ✓

# Relation addition: juju relate grafana-agent-k8s:metrics-endpoint jupyter-controller
  # Relation established successfully ✓
  # jupyter-controller emits alert_rules (3 groups, 5 alerts) and scrape_config ✓
  # grafana-agent-k8s joins with egress/ingress addresses ✓
  # grafana-agent-k8s: blocked (needs grafana-cloud-config or send-remote-write) — expected

# Standard removal (no --force): juju remove-application jupyter-ui --no-prompt
  # Application removed from model ✓
  # ClusterRole/jupyter-ui DELETED ✓
  # ClusterRoleBinding/jupyter-ui DELETED ✓
  # jupyter-web-app-kubeflow-notebook-ui-* aggregate ClusterRoles DELETED ✓

# Force removal (--force --no-wait): juju remove-application jupyter-ui --force --no-wait
  # Application removed from model ✓
  # BUT _on_remove hook NOT RUN (stop hook skipped by --force)
  # ClusterRole/jupyter-ui STILL EXISTS (orphaned) — see Findings

# Pebble layer env vars (verified via pebble plan):
jupyter-controller: 7 env vars present
  CLUSTER_DOMAIN, CULL_IDLE_TIME, ENABLE_CULLING, IDLENESS_CHECK_PERIOD,
  ISTIO_GATEWAY, ISTIO_HOST, USE_ISTIO
  MISSING: EXPERIMENTAL_USE_GATEWAY_API, EXPERIMENTAL_K8S_GATEWAY_NAME,
           EXPERIMENTAL_K8S_GATEWAY_NAMESPACE
  NOT A BUG (maintenance gap): these vars were added in commit 79ee14d (2026-01-20);
  both published tracks (1.10/edge rev1528, latest/edge rev1539) predate that commit.
  Unit test passes because it runs against local source. The test gives false confidence.

# pebble-check-failed hook test (failure injection):
kubectl exec ...jupyter-controller-0 -c jupyter-controller -- pebble stop jupyter-controller
  # After ~2 min: check went DOWN (4/4 failures)
  # jupyter-controller-pebble-check-failed hook fired at 20:58:10 UTC
  # BUT: service remained INACTIVE, no restart occurred
  # Hook produced NO charm log output (no handler registered)
  # Service recovered only after ~5 min when update_status fired
  # on-check-failure: restart does NOT restart manually-stopped services

# traefik-k8s ingress relation test:
juju relate traefik-k8s:ingress jupyter-ui:ingress
  # Relation established ✓
  # jupyter-ui went to WaitingStatus ✓
  # Message: "List of ingress versions not found for apps: traefik-k8s"
  # traefik-k8s ingress interface incompatible with jupyter-ui ingress interface

# ingress-relation-broken test:
juju remove-relation traefik-k8s:ingress jupyter-ui:ingress
  # ingress-relation-departed and ingress-relation-broken hooks fired
  # Hooks produced NO charm log output (no handler registered)
  # jupyter-ui stayed in WaitingStatus with STALE MESSAGE
  # Did NOT recover until forced config-changed

# juju refresh (jupyter-ui 1.10/edge rev1452 → latest/edge rev1464):
juju refresh jupyter-ui --channel latest/edge
  # Downloaded new charm successfully ✓
  # FAILED: "one or more of the provided endpoints ... do not exist"
  # Application went to error/unknown state ✓
  # Pod entered ErrImagePull/ImagePullBackOff with invalid image "store:latest"
  # Application was completely non-functional and unrecoverable
  # Required remove-application --force and re-deploy
```

**Resources observed:**
- jupyter-controller-0: 63 MB RAM, 2 CPU millicores
- jupyter-ui-0: 291 MB RAM, 1 CPU millicore
- Both pods: 0 restarts after 30+ minutes

## Observed behaviour

### Leader election and non-leader units
When `jupyter-controller` is scaled to 3 units, units `/1` and `/2` become non-leaders.
Their Pebble `jupyter-controller` service is `inactive` (expected — only the leader runs
the manager). Units `/1` and `/2` report `running` workload status, not `active`, which
is correct: the charm only sets `ActiveStatus` for the leader via `_check_status()` in
`_on_update_status`. Non-leaders raise `ErrorWithStatus("Waiting for leadership",
WaitingStatus)` via `_check_leader()`, caught and set correctly.

### Scale down leaves orphaned K8s pods (Juju, not charm)
Scaling `jupyter-controller` down from 3 to 1 unit via `juju remove-unit --num-units 2`
removes the Juju units but leaves the K8s pods `jupyter-controller-1` and
`jupyter-controller-2` orphaned in `1/2` state (charm container unhealthy). This is a Juju
k8s provider issue, not a charm bug — the Juju agent reports "unit not found" when trying
to run the stop hook.

### jupyter-ui: Pebble health check permanently failing (401 Unauthorized)
The `up` check probes `http://localhost:5000` every 30s with threshold 3. After 30+
minutes it shows `up: down 0/3 (48 failures)` because the workload requires the
`kubeflow-userid` header, which only an Istio ingressgateway provides. `curl
http://localhost:5000/` from inside the container returns `401 UNAUTHORIZED "No user
detected"`. The charm's `main()` unconditionally sets `ActiveStatus()` regardless of
Pebble check status. Confirmed by `pebble checks` and `curl` from inside the container.

### jupyter-controller: Pebble health check working correctly
The `jupyter-controller-up` check probing `http://localhost:8081/healthz` is UP. Killing
the manager process triggers Pebble auto-restart within seconds; `on-check-failure:
restart` works correctly for crashed (not stopped) services.

### Config type validation absent
`cull-idle-time=-5` and `cull-idle-time=9999999` are both accepted (the latter triggers a
brief maintenance cycle). `idleness-check-period=999999999` is accepted, producing
`IDLENESS_CHECK_PERIOD: "999999999"` (~1900 years) in the pebble layer.
`gpu-vendors-default="invalid-vendor"` is silently ignored, rendering an empty GPU vendor
list. No lower/upper bounds on integer options, no enum validation on string options.
`cull-idle-time=abc` is rejected by Juju at the API level (type mismatch), but all other
invalid integer values pass through.

### `juju refresh` between channels fails (jupyter-controller)
`juju refresh jupyter-controller --channel latest/edge` (rev 1528 → rev 1539) fails with
an error listing endpoints (`gateway-metadata`, `service-mesh`, `provide-cmr-mesh`,
`require-cmr-mesh`, `grafana-dashboard`, `juju-info`, `logging`, `metrics-endpoint`) that
do not exist. Both published charms (1.10/edge and latest/edge) have identical relation
metadata: only `metrics-endpoint`, `grafana-dashboard`, and `logging`. The error message
appears to reference the local source's `metadata.yaml` rather than either published
charm's metadata. The charm enters transient maintenance and recovers after ~15s, but the
in-place upgrade path is broken for any charm that has added new relations since the
target track was cut.

### `EXPERIMENTAL_*` env vars absent from deployed pebble plan
`pebble plan` on the workload container shows 7 env vars, not the 10 defined in
`service_environment` in local source. **Not a runtime bug**: the `1.10/edge` charm (rev
1528, built 2026-05-26) predates the ambient-mesh integration commit `79ee14d`
(2026-01-20) that added these vars. The unit test asserts 10 env vars and passes because
it runs against local source, not the published charm — the test gives false confidence
about what's actually deployed.

### `use-istio` config option is dead code
The deployed `config.yaml` declares a `use-istio` boolean option (default: true). The
charm code contains no reference to it — `grep -rn "use.istio\|use_istio"` returns nothing
in `src/` or `lib/`. Juju accepts and stores the value but it has zero effect. It was
removed from source in commit `79ee14d` (the same commit that added ambient mesh support)
but persists in the deployed charm because `1.10/edge` predates that removal.

### Config-changed fires twice per change
Each `juju config` invocation triggers two `config-changed` hooks (visible in the uniter
log). Each run re-applies K8s resources (lightkube apply) and re-renders the pebble layer.
This is Juju behaviour, not a charm bug.

## Findings

### CRITICAL — `ingress-relation-broken`/`-departed` unhandled: jupyter-ui stuck in WaitingStatus permanently
- **Severity**: critical
- **Kind**: bug
- **Where**: `charms/jupyter-ui/src/charm.py:158` (registered observers); no `ingress-relation-broken` or `ingress-relation-departed` handler exists
- **Evidence**: `grep -n "relation_broken\|relation_departed"` returns nothing in `src/charm.py`. After `juju remove-relation traefik-k8s:ingress jupyter-ui:ingress`, `juju debug-log` shows the `ingress-relation-broken` hook firing, but `kubectl logs -c charm` shows no charm-handler output. The charm stays in `WaitingStatus("List of ingress versions not found for apps: traefik-k8s")` — the stale message from before removal. Only `config-changed` (or `start`) triggers recovery. The `istio-ingress-route` relation has the same gap.
- **Impact**: Any operator who removes and re-adds an ingress relation finds the charm permanently stuck with no self-heal path — a silent, invisible failure.
- **Fix**: Observe `relation_departed`/`relation_broken` for both `ingress` and `istio-ingress-route` and re-run `main()`.
- **Linter rule**: "Charms that observe `relation_changed` must also observe `relation_departed` and `relation_broken` for the same relation — mechanically checkable"

### HIGH — `pebble-check-failed` unhandled: jupyter-controller stays inactive for ~5 minutes
- **Severity**: high
- **Kind**: bug
- **Where**: `charms/jupyter-controller/src/charm.py:106-115` (registered observers); no `jupyter_controller_pebble_check_failed` handler
- **Evidence**: `grep -n "framework.observe"` shows no registration for `self.on.jupyter_controller_pebble_check_failed`. Stopping the workload service causes the hook to fire (confirmed in `juju debug-log` at 20:58:10 UTC) with no charm-handler log output. The service stays `inactive`/`pebble checks down` until the next `update_status` hook (~5 minute interval) restarts it. `on-check-failure: restart` in the pebble layer only restarts crashed services, not manually-stopped ones.
- **Impact**: Real workload outages are bounded by the `update_status` interval, not by the check itself — several minutes of avoidable downtime.
- **Fix**: Observe `self.on.jupyter_controller_pebble_check_failed` and call `container.restart(...)` plus set `MaintenanceStatus`, or explicitly document the ~5 minute recovery SLA.
- **Linter rule**: "Charms that define `on-check-failure` in their pebble layer must register a handler for the corresponding `pebble-check-failed` hook — mechanically checkable by grepping for the check name in `framework.observe`"

### HIGH — jupyter-ui Pebble health check uses an unauthenticated endpoint that can never pass
- **Severity**: high
- **Kind**: bug
- **Where**: `charms/jupyter-ui/charmcraft.yaml` (pebble check definition); `charms/jupyter-ui/src/charm.py:610-628` (`main()` sets `ActiveStatus` at line ~627)
- **Evidence**: `pebble checks` shows `up: down 0/48 failures` after 30+ minutes uptime. `curl http://localhost:5000/` returns `401 UNAUTHORIZED`. `main()` sets `ActiveStatus()` unconditionally regardless of check state.
- **Impact**: In standalone mode (no Istio) the check can never succeed; the unit reports Active while the health check fails constantly, masking real problems from anyone monitoring Pebble checks.
- **Fix**: Use an unauthenticated `/healthz`-style endpoint if one exists, make the check conditional on the ingress relation being present, or otherwise decouple check status from `ActiveStatus`.
- **Linter rule**: "Pebble HTTP checks probing a workload that requires auth headers must be conditional on the presence of an ingress relation, or must use an unauthenticated health endpoint"

### HIGH — `juju refresh` leaves jupyter-ui completely broken
- **Severity**: high
- **Kind**: bug
- **Where**: Upgrade path; `charms/jupyter-ui/charmcraft.yaml` (relation metadata)
- **Evidence**: `juju refresh jupyter-ui --channel latest/edge` (rev 1452 → rev 1464): new charm binary downloaded successfully, but the upgrade failed with "one or more of the provided endpoints ... do not exist". The application went to `error`/`unknown` state ("agent lost"); the workload pod went `ErrImagePull`/`ImagePullBackOff` with invalid image `store:latest`. Application was completely non-functional and required `remove-application --force` and a fresh deploy to recover. `latest/edge` and `1.10/edge` jupyter-ui have the same declared relations (`dashboard-links`, `ingress`, `logging`), so the failure looks like it's in image/resource reconciliation on refresh, not relation metadata mismatch (unverified).
- **Impact**: `juju refresh` is the standard upgrade mechanism; when it fails and leaves the app unrecoverable, operators face an unplanned outage and manual recovery.
- **Fix**: Investigate why the workload resource/image reference changes incompatibly between revisions; add a pre-flight check or make the resource definition backwards-compatible across revisions.
- **Linter rule**: not mechanically checkable — requires integration testing of the upgrade path

### HIGH — `juju refresh` fails between channels for jupyter-controller due to relation-metadata mismatch
- **Severity**: high
- **Kind**: bug
- **Where**: Upgrade path; `charms/jupyter-controller/metadata.yaml` (local source)
- **Evidence**: `juju refresh jupyter-controller --channel latest/edge` (rev 1528 → rev 1539) fails: `ERROR ... endpoints "gateway-metadata, grafana-dashboard, juju-info, logging, metrics-endpoint, provide-cmr-mesh, require-cmr-mesh, service-mesh" do not exist`. Both `1.10/edge` and `latest/edge` on charmhub have identical relations (`metrics-endpoint`, `grafana-dashboard`, `logging` only) — neither has the extra endpoints the error names. The error appears to reference the local source's `metadata.yaml` rather than either published charm's. Charm recovers automatically after ~15s.
- **Impact**: In-place upgrade is broken and the error message is misleading, since it lists relations absent from both the running and target charm — operators may misdiagnose or roll back unnecessarily.
- **Fix**: Ensure new relation endpoints are added incrementally (optional first) across published tracks; add a pre-upgrade compatibility check.
- **Linter rule**: "New relation endpoints in a published track must not cause `juju refresh` from prior tracks to fail — not mechanically checkable at charm authoring time"

### HIGH — jupyter-ui: invalid config silently falls back to empty, no operator-visible feedback
- **Severity**: high
- **Kind**: bug
- **Where**: `charms/jupyter-ui/src/charm.py:370-387` (`_get_from_config`), `charms/jupyter-ui/src/charm.py:422-448` (`_get_options_with_default_from_config`)
- **Evidence**: `juju config jupyter-ui jupyter-images='{ invalid yaml }'` renders `spawner_ui_config.yaml` with `options: []` (empty). `gpu-vendors-default="invalid-vendor"` renders `vendors: []` and `vendor: ""`. Only a `WARNING` appears in the charm log; unit reports Active. Confirmed via `kubectl exec ... cat /etc/config/spawner_ui_config.yaml`. Related to open issue #297.
- **Impact**: Bad YAML or an invalid vendor name is accepted silently, users see an empty dropdown with no explanation.
- **Fix**: Catch YAML parse errors in `_get_from_config` and raise `CheckFailed` with `BlockedStatus` and a descriptive message; same for `ConfigValidationError` in `_get_options_with_default_from_config`.
- **Linter rule**: "Config option parse/validation errors should raise `CheckFailed`/`ErrorWithStatus` with `BlockedStatus`, not silently return default/empty values"

### HIGH — jupyter-ui: `main()` can set `ActiveStatus` when container is not ready
- **Severity**: high
- **Kind**: bug
- **Where**: `charms/jupyter-ui/src/charm.py:610-628`
- **Evidence**: `_is_container_ready()` returns `False` (and sets `MaintenanceStatus`) when the container is not connectable, but `main()` treats this as a plain `if` guard: the block is skipped and execution falls through to `self.model.unit.status = ActiveStatus()`, overwriting the `MaintenanceStatus` just set.
- **Impact**: A brief network partition or container restart can leave the unit reporting Active without the spawner config actually rendered; users see an empty spawner.
- **Fix**: Have `_is_container_ready()` raise `ErrorWithStatus(..., MaintenanceStatus)` instead of returning `False`, or restructure `main()` with an early return before the `try` block.
- **Linter rule**: "`ActiveStatus()` must not be reachable when the container is not confirmed ready — use exception-based flow control, not boolean return values, to prevent fallthrough"

### MEDIUM — jupyter-controller: non-conflict K8s ApiErrors propagate as unhandled exceptions
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/jupyter-controller/src/charm.py:329-353` (`_apply_k8s_resources`), `charms/jupyter-controller/src/charm.py:355-367` (`_on_event`)
- **Evidence**: `_apply_k8s_resources` wraps non-409 `ApiError`s as `GenericCharmRuntimeError`. `_on_event` only catches `ErrorWithStatus`. `ErrorWithStatus` and `GenericCharmRuntimeError` are sibling classes (both inherit directly from `Exception`), so the `except ErrorWithStatus` clause does not catch `GenericCharmRuntimeError`. Confirmed by reading `charmed_kubeflow_chisme/exceptions/_with_status.py` and `_generic_charm_runtime_error.py`.
- **Impact**: A non-conflict K8s API error (e.g. 403, network timeout) during resource application crashes the hook with an unhandled traceback and error unit state, instead of a graceful status.
- **Fix**: Catch `GenericCharmRuntimeError` in `_on_event` and set the appropriate status, or re-raise as `ErrorWithStatus` in `_apply_k8s_resources`.
- **Linter rule**: "Exception handlers in charm event handlers must catch all expected exception types, including library exceptions like `GenericCharmRuntimeError`, not only custom `ErrorWithStatus` types — not mechanically checkable without knowing the full exception hierarchy"

### MEDIUM — jupyter-controller: no config value range validation
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/jupyter-controller/config.yaml`; `charms/jupyter-controller/src/charm.py` (no validation)
- **Evidence**: `cull-idle-time=-5` accepted, pebble layer gets `CULL_IDLE_TIME="-5"`, unit Active. `cull-idle-time=9999999` accepted, briefly triggers maintenance. No `minimum`/`maximum` in `config.yaml`, no runtime validation.
- **Impact**: Negative or absurdly large idle times produce nonsensical behaviour with no operator notification.
- **Fix**: Add `min: 0` to `cull-idle-time` and `idleness-check-period`, plus a sane upper bound in code.
- **Linter rule**: "Integer config options should have `min` constraints in `config.yaml` to prevent nonsensical values"

### MEDIUM — jupyter-controller: no `relation-broken`/`relation-departed` handlers for any relation
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/jupyter-controller/src/charm.py:106-115` (observers register only `relation_changed`)
- **Evidence**: `__init__` registers `relation_changed` for all relations; no `relation_departed`/`relation_broken` observers exist. For the deployed relation set (`metrics-endpoint`, `grafana-dashboard`, `logging`) removal doesn't require charm-side cleanup today, but the reconciliation loop is blind to relation lifecycle events generally.
- **Impact**: Any future relation requiring cleanup on removal will silently not get it.
- **Fix**: Add `relation_departed`/`relation_broken` observers per relation, or a generic handler.
- **Linter rule**: "Charms that observe `relation_changed` should also observe `relation_departed` and `relation_broken` — not mechanically checkable without knowing which relations require cleanup"

### MEDIUM — jupyter-ui: `_deploy_k8s_resources` runs before the container-ready guard
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/jupyter-ui/src/charm.py:608-628` (`main()`)
- **Evidence**: `_deploy_k8s_resources()` is called before `_is_container_ready()` in `main()`. If the container is not ready, K8s resources are applied anyway. If `_deploy_k8s_resources()` raises, it is caught and `BlockedStatus` is set correctly, but the ordering contradicts the intent of the readiness guard.
- **Impact**: Confusing control flow; resources get applied while the workload itself isn't confirmed ready.
- **Fix**: Move the `_is_container_ready()` guard before `_deploy_k8s_resources()`, or document why it's intentional.
- **Linter rule**: "Readiness guards should appear before operations that depend on the resource being ready"

### MEDIUM — jupyter-ui: `test_with_relation` unit test permanently broken
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `charms/jupyter-ui/tests/unit/test_operator.py:293-326`
- **Evidence**: Test fails with `serialized_data_interface.errors.MissingSchemaError: No provides schema found for data on ingress:0 from istio-pilot`. The mock relation data doesn't satisfy the `ingress` interface schema `serialized_data_interface` expects.
- **Impact**: One unit test is permanently failing, reducing confidence in the ingress-relation code path.
- **Fix**: Update the mock to a schema-satisfying payload, or mock `get_interfaces` directly.
- **Linter rule**: not mechanically checkable — requires integration with the `serialized_data_interface` test harness

### MEDIUM — traefik-k8s `ingress` relation is incompatible with jupyter-ui
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/jupyter-ui/src/charm.py:610-628` (`main()` via `_get_interfaces`); `serialized_data_interface`
- **Evidence**: `juju relate traefik-k8s:ingress jupyter-ui:ingress` establishes, but jupyter-ui goes to `WaitingStatus("List of ingress versions not found for apps: traefik-k8s")` — traefik-k8s's ingress interface schema differs from `serialized_data_interface`'s expectations. The `WaitingStatus` is the correct/intended response, but the message is cryptic.
- **Impact**: traefik-k8s is a common ingress provider; operators relating it get a confusing wait state with no clear guidance.
- **Fix**: Document compatible ingress providers in the README; consider a clearer `BlockedStatus` message naming the mismatch.
- **Linter rule**: not mechanically checkable

### LOW — jupyter-controller: swapped error messages in `_on_remove`
- **Severity**: low
- **Kind**: bug
- **Where**: `charms/jupyter-controller/src/charm.py:340-346`
- **Evidence**: Line 340 logs "Failed to delete CRD resources" but operates on `k8s_resource_handler`; line 345 logs "Failed to delete K8S resources" but operates on `crd_resource_handler`.
- **Impact**: Debugging a delete failure gets the wrong resource type in the message.
- **Fix**: Swap the two log messages.
- **Linter rule**: "Error messages must identify the correct resource type being operated on"

### LOW — jupyter-controller: `_check_status` raises untyped `GenericCharmRuntimeError` instead of `ErrorWithStatus`
- **Severity**: low
- **Kind**: bug
- **Where**: `charms/jupyter-controller/src/charm.py:289` (raise site); `:360,381` (`except ErrorWithStatus` in `_on_update_status`/`_on_event`)
- **Evidence**: When `container.get_check()` raises `ModelError`, `_check_status` raises `GenericCharmRuntimeError`, which is not caught by the `except ErrorWithStatus` handlers and propagates as an unhandled exception.
- **Impact**: An unexpected Pebble check state crashes `update_status` with a traceback instead of setting a sensible status.
- **Fix**: Raise `ErrorWithStatus(..., MaintenanceStatus)` instead.
- **Linter rule**: "All status-setting exceptions should use `ErrorWithStatus` (or `CheckFailed`) so they are caught by the charm's event handler — not mechanically checkable without knowing the exception hierarchy"

### LOW — jupyter-controller: `ServiceMeshConsumer` instantiated but never used
- **Severity**: low
- **Kind**: lint
- **Where**: `charms/jupyter-controller/src/charm.py:106-109`
- **Evidence**: `self._mesh = ServiceMeshConsumer(...)` is assigned but never referenced again. The library registers observers as a side effect of construction, so functionality is unaffected, but the attribute is dead code.
- **Impact**: Misleading for maintainers who might expect to read `self._mesh` elsewhere.
- **Fix**: Drop the assignment; call `ServiceMeshConsumer(...)` without binding it.
- **Linter rule**: "Instance variables assigned but never read are dead code — mechanically checkable with a bytecode analysis tool"

### LOW — jupyter-controller: `logging.info()` on root logger
- **Severity**: low
- **Kind**: lint
- **Where**: `charms/jupyter-controller/src/charm.py:314` (`_set_istio_configurations`)
- **Evidence**: `logging.info(...)` calls the root logger directly instead of `self.logger`. Flagged by `ruff` as `LOG015`.
- **Impact**: Log messages bypass the charm's logger, complicating log filtering.
- **Fix**: Use `self.logger.info(...)`.
- **Linter rule**: "Do not call `logging` directly; use `self.logger` — mechanically checkable with ruff LOG015"

### NIT — jupyter-ui: typo in variable name `rstusio_images_config`
- **Severity**: nit
- **Kind**: lint
- **Where**: `charms/jupyter-ui/src/charm.py:496, 506`
- **Evidence**: `rstusio_images_config = self._get_from_config(RSTUDIO_IMAGES_CONFIG)`. Used consistently downstream, so no functional bug.
- **Impact**: Readability only.
- **Fix**: Rename to `rstudio_images_config`.
- **Linter rule**: "Variable names must not contain typos — mechanically checkable with codespell or a spell-checker"

### NIT — jupyter-ui: useless `return` at end of `_on_install`
- **Severity**: nit
- **Kind**: lint
- **Where**: `charms/jupyter-ui/src/charm.py:523`
- **Evidence**: `return` after `except CheckFailed as err: self.model.unit.status = err.status`. Flagged by `ruff` as `PLR1711`.
- **Impact**: None functionally; redundant statement.
- **Fix**: Remove the `return`.
- **Linter rule**: "Remove useless `return` at end of void function — mechanically checkable with ruff PLR1711"

## Worth copying

### Mutual-exclusion check for incompatible ingress modes
`charms/jupyter-ui/src/charm.py:60` (`ISTIO_INGRESS_ROUTE_RELATION`) and `:596-610`
(`_check_istio_relations()`) explicitly block if both `istio-ingress-route` (ambient) and
`ingress` (sidecar) relations are present, with an actionable error message. Good
defensive programming.

### Config validation with `OptionsWithDefault` dataclass
`charms/jupyter-ui/src/config_validators.py`: clean dataclass-based approach to
config-with-default; validation functions raise typed `ConfigValidationError` exceptions
that bubble up cleanly.

### Pebble layer with health checks and restart policy
`charms/jupyter-controller/src/charm.py:178-198`: `jupyter-controller-up` check with
`on-check-failure: restart`, `threshold: 4`, `period: 30s`, `timeout: 20s`. Observed
working correctly when the manager process was killed.

### Force-conflict resolution on upgrade
`charms/jupyter-controller/src/charm.py:334-336`: `_on_upgrade` passes
`force_conflicts=True` to `_apply_k8s_resources`, cleanly handling ownership conflicts on
upgrade.

### Poetry/rust build system
Both `charmcraft.yaml`s use `uv` to install poetry, `rustup` for rustc, and the poetry
plugin to build the charm, with extensive comments explaining magic constants — exemplary
documentation of a non-trivial build.

### Exhaustive pebble layer unit test
`charms/jupyter-controller/tests/unit/test_operator.py:143-165` (`test_pebble_layer`)
verifies exactly 10 environment variables and the `ISTIO_GATEWAY` format — this specific
assertion is what surfaced the env-var drift between the test harness and production.

## Common-practice notes

- **ops framework**: `ops >= 2.17.1`, `@property` lazy resource handlers,
  `framework.observe()`, `ErrorWithStatus`/`CheckFailed` for structured error handling —
  followed correctly.
- **Library versioning**: libraries live under `lib/charms/<charm>/v0/`, vendored rather
  than fetched from charmhub — standard pattern.
- **Non-root user**: both charms declare `charm-user: non-root` and use uid/gid 584792 in
  the security context — correctly implemented.
- **Status precedence**: `jupyter-controller` uses `MaintenanceStatus` during resource
  creation, `WaitingStatus` for leadership/container waits, `BlockedStatus` for
  unrecoverable config errors, `ActiveStatus` when healthy — correct order.
  `jupyter-ui` has a bug in this ordering (see findings).
- **charmcraft.yaml parts**: both use the standard `poetry-deps`/`charm-poetry`/`files`
  part structure — canonical pattern.
- **Code/metadata publishing gap**: the ambient-mesh relations (`service-mesh`,
  `gateway-metadata`, `provide-cmr-mesh`, `require-cmr-mesh`) and `EXPERIMENTAL_*` env
  vars exist in local source since January 2026 but are absent from every published
  track — the published charms are 3+ months behind local source, a real maintenance
  hazard because local source cannot be tested against what's actually shipped.
- **Drift from convention**: `jupyter-controller` uses `charmed-service-mesh-helpers`
  (pip-installed) for `GatewayMetadataRequirer`, while the mesh library
  (`lib/charms/istio_beacon_k8s/`) is vendored — mixing external and vendored deps for the
  same integration surface. `GatewayMetadataRequirer.get_metadata()` itself is
  well-written and returns `None` safely when the relation isn't ready.
- **Deprecation warnings in unit tests**: both charms emit `PendingDeprecationWarning:
  Harness is deprecated` from `ops.testing.Harness`, and `JujuVersion.from_environ() is
  deprecated` from `loki_k8s`. Library deprecations, not charm bugs, but indicate the test
  infrastructure needs updating.

## Tests

### Unit tests
- **jupyter-controller**: 7 tests, all pass. Covers log forwarding, not-leader, no-relation,
  prometheus data, pebble layer, deploy K8s resources, update_status. Missing coverage:
  `_get_gateway_info` with service-mesh but no gateway-metadata, `_check_status` when the
  Pebble check is DOWN, `_on_remove` with `ApiError`, `_on_event` with a non-409 `ApiError`
  (the `GenericCharmRuntimeError` propagation bug), config value range validation.
- **jupyter-ui**: 43 tests, 42 pass / 1 fails (`test_with_relation`). Comprehensive coverage
  of config parsing, GPU validation, spawner UI rendering, istio relation mutual
  exclusion. Missing: `main()` when container is not ready (tests always call
  `harness.set_can_connect(True)`), invalid YAML config raising `BlockedStatus` (only a
  warning is asserted), and the broken `test_with_relation`.

### Integration tests
Both charms have integration tests (`test_charm.py` sidecar, `test_charm_ambient.py`
ambient) deploying from charmhub + istio + grafana-agent, then asserting notebook
creation, security context, alert rules, metrics endpoint, logging, and removal cleanup
via `charmed-kubeflow-chisme` helpers. `test_create_notebook` retries up to 30 times for
`readyReplicas == 1`. Ambient tests additionally verify notebook reachability via
ingress. Both end with `test_remove_with_resources_present` verifying cleanup. These
integration tests were not executed in this review (not established whether they were run
against this repo state — the notes record only that CI configuration was inspected, not
that the suite was executed here).

### Lint checks
- `ruff`: 10 issues total.
  - `jupyter-controller`: unsorted import block, deprecated `typing.Tuple` (use `tuple`),
    `.format()` instead of f-string, `key in dict.keys()` instead of `key in dict`,
    `logging.info()` on root logger.
  - `jupyter-ui`: unsorted import block, deprecated `Union` (use `X | Y`), useless `return`
    at end of `_on_install`, bare `raise e` (use `raise`).
- `codespell`: 0 issues.
- `pyright`: 6 errors in `jupyter-controller/src/charm.py` — all `reportMissingImports` for
  vendored libraries (expected, not on `PYTHONPATH`) plus one real type mismatch
  (`dict[str, Unknown]` vs `LayerDict`).

## Docs

### README
Top-level `README.md` is minimal — a bundle description and two install commands. Fuller
docs live on [discourse.charmhub.io](https://discourse.charmhub.io/t/10963).
`CONTRIBUTING.md` files are brief.

### charmcraft.yaml comments
Both files have extensive comments explaining the build system, the `poetry-deps` magic
constant, and the `rustup` snap vs apt workaround — exemplary.

### Config descriptions
`jupyter-controller/config.yaml`'s `cull-idle-time` description says "in minutes"
(correct), but charmhub renders it as "in seconds" — tracked as issue #542. `use-istio`'s
description is accurate but the option is dead code in the deployed charm (see findings).

### Spawner config default images
`jupyter-ui/src/default-jupyter-images.yaml`, `default-vscode-images.yaml`,
`default-rstudio-images.yaml` are checked in. Issue #297 requests an option to keep
default images alongside custom ones — currently setting any image config replaces the
defaults entirely.

## Open questions

1. When will ambient-mesh relations be published? Code has existed since January 2026 but
   no published track has it.
2. **gateway-metadata provider**: issue #574 is unanswered — what provides
   `gateway_metadata`? If nothing does, the relation should be `optional: true` in the
   published metadata.
3. Does the jupyter-web-app workload have an unauthenticated `/healthz` endpoint that the
   Pebble check could use instead of the auth-gated root?
4. `cull-idle-time` charmhub description says "seconds" vs in-repo "minutes" (issue #542)
   — stale charmhub docs?
5. Why does `test_with_relation` fail — is it a `serialized_data_interface` version
   incompatibility in the test harness that needs a schema-satisfying mock?
6. Why does the `juju refresh` error for jupyter-controller list relations absent from
   both the running and target published charm? Is Juju comparing against local source
   metadata rather than the published charm's?
7. When will jupyter-ui get metrics/grafana support (issues #441/#400)? The controller has
   it; the UI does not.
8. What creates the `rv-notebook-ops-jupyter-controller` ClusterRole seen at model-creation
   time (not created by the charm), and does it persist after charm removal? Should the
   Juju operator clean it up automatically? (unverified — noted but not traced to source)
9. Is the non-409 `ApiError` path in `_on_event`/`_apply_k8s_resources` actually reachable
   in practice, or only theoretical? Needs a test case to confirm.
10. Issue #572 (upgrade-charm after pod deletion): if the container isn't ready after pod
    recreation during upgrade, `_check_container_connection()` sets `MaintenanceStatus`
    correctly, but does the upgrade actually complete afterward? (unverified)
11. Should `jupyter-controller-pebble-check-failed` restart the service immediately, or is
    the ~5 minute `update_status`-bound recovery an acceptable SLA?
12. Which ingress providers are actually compatible with jupyter-ui's `ingress` relation?
    traefik-k8s is not — is there a known-compatible ingress charm to recommend?
13. Why does jupyter-ui's `juju refresh` leave the workload pod with an invalid image
    reference (`store:latest`)? Charm packaging issue or Juju operator bug? (unverified)
</content>
