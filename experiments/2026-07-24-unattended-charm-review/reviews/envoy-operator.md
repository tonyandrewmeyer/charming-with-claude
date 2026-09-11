# envoy-operator

A k8s charm that wraps Envoy proxy specifically for Kubeflow's `metadata-envoy` component (see
GitHub issue #66 — the charm name is misleading for anyone expecting a general-purpose Envoy
charm). Built on `charmed_kubeflow_chisme.CharmReconciler` with a clean component architecture,
well-structured and actively maintained. The charm works for its single intended path (grpc
relation to `mlmd` + SDI ingress to Kubeflow's own ingress stack), but has a critical crash bug
on invalid config, does not support scaling beyond one unit, and declares three relations
(`service-mesh`, `require-cmr-mesh`, `provide-cmr-mesh`) that have no code behind them. A
maintainer should fix the `__init__` crash first (it's a one-line try/except or config-type
change), then decide whether to support scale-out or document that it isn't supported, then
resolve the dead relation declarations.

| | |
|---|---|
| Repo | canonical/envoy-operator @ `c88457d` (2026-06-23) |
| Charms | envoy |
| Substrate | k8s |
| Deployed | yes — `concierge-k8s-4`, `2.4/edge` rev 576 (local HEAD `c88457d`, same commit) |
| Reviewed | 2026-08-21 |

## What it does

Deploys the `ghcr.io/kubeflow/kfp-metadata-envoy:2.16.0` OCI image as a Pebble-managed workload.
Requires a `grpc` (k8s-service-info) relation to discover the upstream metadata store. Supports
two mutually-exclusive ingress paths: the legacy SDI `ingress` relation (produces a
`VirtualService`) and the Istio ambient `istio-ingress-route` relation (produces an `HTTPRoute`).
Provides Prometheus metrics at `/stats/prometheus`, Grafana dashboards, and Loki log forwarding.
Config exposes `admin-port` (default 9901) and `http-port` (default 9090).

## Deployment log

```
# Bootstrap
juju add-model rv-envoy-k8s --controller concierge-k8s-4

# Deploy from charmhub
juju deploy envoy --channel 2.4/edge
# → rev 576, blocked: "[grpc] Missing relation with a k8s service info provider"

# Deploy upstream provider
juju deploy mlmd --channel latest/edge --trust
# → mlmd active after ~90s

# Relate
juju integrate envoy:grpc mlmd:grpc
# → envoy active within ~15s

# Observe workload
kubectl exec envoy-0 -c envoy -- pebble services
# Service  Startup  Current  Since
# envoy    enabled  active   today at 04:05 UTC

# Config change: admin-port=9902
juju config envoy admin-port=9902
# → config-changed fires 2×, full reconcile runs 2×, file pushed twice

# Bad config: admin-port=not-a-port
juju config envoy admin-port=not-a-port
# → charm crashes with ValueError in __init__, enters error loop, retries infinitely
# juju resolve → returns 0 but does NOT fix the charm (config still bad)
juju config envoy admin-port=9901
# → auto-recovers after valid config applied (no juju resolve needed)

# Bad config: http-port=not-a-port (same crash, same recovery)
juju config envoy http-port=not-a-port
# → same ValueError crash, same auto-recovery path

# Pod restart
kubectl delete pod envoy-0
# → pod respawns, charm auto-recovers to active within ~45s

# Observability: grafana-agent-k8s
juju deploy grafana-agent-k8s --channel 2/stable --trust
juju integrate envoy:metrics-endpoint grafana-agent-k8s:metrics-endpoint
# → grafana-agent-k8s blocked: "Missing ['grafana-cloud-config']|['send-remote-write']"
#   (expected — grafana-agent needs cloud config; envoy is fine)

# Ingress integration with traefik-k8s
juju deploy traefik-k8s --channel latest/edge --trust
juju integrate envoy:ingress traefik-k8s:ingress
# → relation created, traefik-k8s immediately goes to "Provider not ready"
#   traefik-k8s logs: "failed to fetch proxied endpoints: This application did not
#    publish_url yet" and "failed to validate databag"
# → envoy goes waiting: "[relation:ingress] List of ... versions not found for apps: traefik-k8s"

# istio-ingress-route integration
juju deploy istio-ingress-k8s --channel 2/stable --trust
juju integrate envoy:istio-ingress-route istio-ingress-k8s:istio-ingress-route
# → relation created, hooks fire (created → joined → changed)
# → envoy stays active (istio-ingress-k8s itself in error due to its own leader-elected hook)
# → HTTPRoute not created because istio-ingress-k8s is in error

# Relation removal: grpc
juju remove-relation envoy:grpc mlmd:grpc
# → grpc-relation-broken fires, envoy goes blocked: "[grpc] Missing relation..."
# Re-integrate: envoy recovers to active within ~15s
# Stale SDI ingress status: after removing traefik-k8s relation, envoy's juju status
#  shows stale traefik-k8s message for ~2 min until next reconcile clears it.
#  Unit workload status updates correctly; only juju status display lags.

# Scale to 2 units
juju scale-application envoy 2
# → envoy/0 stays active (leader), envoy/1 goes to waiting:
#   "[leadership-gate] Waiting for leadership"
#   envoy/1 is stuck permanently; there is only ever one leader

# Scale back to 1
juju scale-application envoy 1
# → envoy/1 enters error state: "hook failed: 'remove'"
#   juju resolve envoy/1 → recovers
# → orphaned envoy-1 pod remains in Kubernetes (not cleaned up automatically)
#   Manual cleanup: kubectl delete pod envoy-1 -n rv-envoy-k8s

# Workload kill: pebble stop envoy
kubectl exec envoy-0 -n rv-envoy-k8s -c envoy -- pebble stop envoy
# → service goes inactive; Juju status still shows "active" for >30 seconds
#   (update-status fires every ~5 min, so lag is up to 5 min)
#   Recovery: pebble start envoy → service back to active

# juju refresh
juju refresh envoy --channel 2.4/edge --force
# → "charm envoy: already up-to-date" (no newer revision in channel)

# juju remove-application
juju remove-application envoy
# → clean teardown; mlmd stays active

# Unit tests
PYTHONPATH="lib:src" python3 -m pytest tests/unit/test_charm.py -v
# → 14/14 pass, 97 warnings (Harness deprecated, JujuVersion deprecated, logger.warn deprecated)
```

**Resource usage:** envoy-0 pod: ~11m CPU, ~66Mi RAM.

**Hook fire count for trivial config change:** 2× `config-changed` per single `juju config` call.

## Observed behaviour

- Charm starts, installs agent (~30s), deploys pod (~40s), becomes active after `grpc` relation.
- The Envoy workload image is distroless/minimal: no `ls`, `/bin/sh`, `kill` via `kubectl exec`,
  but `pebble` and `pebble ls` work. `pebble exec` fails with "cannot find executable" for
  anything other than `pebble` itself.
- Config file is pushed to `/var/lib/pebble/default/envoy-config.yaml`; Envoy hot-reloads without
  process restart (service `Since` timestamp unchanged after config change).
- **`config-changed` fires twice per config change** — confirmed directly from the uniter log:
  ```
  unit-envoy-0: 16:38:49 INFO juju.worker.uniter.operation ran "config-changed" hook
  unit-envoy-0: 16:38:50 INFO juju.worker.uniter.operation ran "config-changed" hook
  ```
  Each fire triggers a full `CharmReconciler.reconcile()` — all 6 components re-execute. Pebble
  log shows two identical `Pushing file /var/lib/pebble/default/envoy-config.yaml` events ~1s
  apart, matching the hook dispatches. This is Juju's uniter dispatching the hook twice, not
  the `CharmReconciler` re-triggering itself.
- **`grpc-relation-changed` also fires twice** on relation join (16:05:26 and 16:05:28 UTC), same
  pattern.
- **`ingress-relation-created` fires twice** when the SDI ingress relation is established
  (16:54:53, twice). Same uniter behaviour.
- **Bad integer config** for either `admin-port` or `http-port`: charm crashes in `__init__`,
  unit enters error state, retries forever. `juju resolve` returns 0 but does not clear the
  error — the config is still invalid. Recovers automatically once a valid value is applied,
  without needing `juju resolve`.
- **Pod restart** (`kubectl delete pod`): pod respawns within ~45s, charm auto-recovers to
  active. `CharmReconciler` is re-initialized on the new pod.
- **Relation removal (grpc)**: `grpc-relation-broken` fires correctly, envoy goes
  `BlockedStatus("[grpc] Missing relation with a k8s service info provider...")`. Recovers to
  `ActiveStatus` within ~15s on re-integration.
- **SDI ingress relation with traefik-k8s**: relation created but immediately fails —
  traefik-k8s reports `Provider not ready` / `failed to validate databag`. Envoy enters
  `WaitingStatus("[relation:ingress] List of ... versions not found for apps: traefik-k8s")`.
  Root cause: version incompatibility — envoy's ingress interface declares `versions: [v1]`
  (SDI v1 only); traefik-k8s supports v2 only, and its own `ingress` interface schema (fields
  `model`, `name`, `host`, `port`, `strip-prefix`, `redirect-https`) has no fields in common with
  envoy's SDI v1 payload (`service`, `port`, `prefix`, `rewrite`) — the two are fundamentally
  incompatible, not just version-mismatched. Confirmed from traefik-k8s logs:
  `failed to validate databag: {'_supported_versions': '- v1\n'}`. After relation removal, the
  stale status persists for roughly 2 minutes until the next reconcile (e.g. `config-changed`)
  clears it — a brief race condition, not a permanent hang. The unit workload status updates
  correctly on `ingress-relation-broken`; only the `juju status` display lags.
- **`istio-ingress-route` integration**: relation establishes successfully; hooks fire
  (`relation-created` → `relation-joined` → `relation-changed`). In this test the
  `istio-ingress-k8s` charm itself entered error state on its own `leader-elected` hook, so no
  `HTTPRoute` was created. The requirer component (`AmbientMeshRequirerComponent`) correctly
  checked `is_ready()` before attempting submission and skipped it rather than crashing.
- **Conflict detection** (both `ingress` and `istio-ingress-route` present at once): at 16:54:54
  the conflict detector returned `BlockedStatus` ("Both 'ingress' and 'istio-ingress-route'
  relations found. Please choose one."). At 16:54:55, once the `istio-ingress-route` relation
  was gone, the conflict was resolved and the `ingress` component ran and returned
  `WaitingStatus` (SDI version mismatch), which then became the overall charm status. This is
  correct behaviour given `Prioritiser.highest()`'s priority ordering
  (error < blocked < waiting < ... ); it is not a status-priority bug, just a fast-moving
  sequence of events that can look confusing in the status log.
- **Workload monitoring gap**: `pebble stop envoy` makes the Pebble service `inactive`; Juju
  status stays `active` for more than 30 seconds, with detection lag of up to ~5 min
  (`update-status` interval). `PebbleComponent._events_to_observe` is hardcoded to only
  `pebble_ready`; no event observes a service transitioning from `active` to `inactive`.
- **Scaling to 2 units**: non-leader (`envoy/1`) goes to `WaitingStatus("[leadership-gate]
  Waiting for leadership")` and is permanently stuck — every component depends (directly or
  transitively) on `leadership_gate`, whose `ready_for_execution()` is `unit.is_leader()`.
- **Scale-down leaves orphaned pod**: `juju scale-application envoy 1` (from 2) causes the
  `remove` hook to fail on the non-leader (`hook failed: 'remove'`), requiring `juju resolve`.
  Kubernetes does not clean up the `envoy-1` pod because the unit agent stayed alive in error
  state. Manual cleanup required: `kubectl delete pod envoy-1 -n rv-envoy-k8s`.
- Grafana-agent integration establishes correctly; the agent blocks for lack of cloud config
  (expected, unrelated to envoy).
- No Juju secrets are used by this charm (no `model.get_secret()` calls, no `secret-*` hooks).
- **`juju refresh`**: charm already at latest revision in `2.4/edge` — upgrade path (there is no
  `upgrade-charm` handler) was not exercised end-to-end.
- **`juju remove-application`**: clean teardown, no orphaned resources.
- **LXD substrate**: not applicable — k8s-only charm.

## Findings

### `__init__` crashes on invalid config for either port option, causing an infinite error loop
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:119` (`admin-port`), `src/charm.py:142` (`http-port`)
- **Evidence**:
  ```python
  admin_port = ServicePort(int(self.model.config["admin-port"]), name="admin")
  ...
  http_port = ServicePort(int(self.model.config["http-port"]), name="http")
  ```
  With `admin-port="not-a-port"` or `http-port="not-a-port"`:
  ```
  File "/var/lib/juju/agents/unit-envoy-0/charm/src/charm.py", line 119, in __init__
      admin_port = ServicePort(int(self.model.config["admin-port"]), name="admin")
  ValueError: invalid literal for int() with base 10: 'not-a-port'
  ```
  The charm never reaches any hook handler — `main()` throws before the charm object exists.
  Juju retries every ~10s and re-crashes. Recovery is confirmed: setting a valid config value
  restores the charm without `juju resolve`. `juju resolve` returns exit code 0 but does not fix
  the charm while config is still invalid — a no-op for this crash class.
- **Why it matters**: Any operator who mistypes a port number crashes the charm into an
  unrecoverable error loop that `juju resolve` cannot fix.
- **Fix**: Wrap both `int()` casts in try/except in `__init__` and emit `BlockedStatus`, or change
  `config.yaml` (`config.yaml:5,9`) to `type: int` for both options so `ops`/Juju reject invalid
  values before the charm code ever runs.
- **Linter rule**: "Hook charm `__init__` must not raise unhandled exceptions for config
  validation failures" — mechanically checkable via a scenario test with invalid config.

### Non-leader units permanently stuck in `WaitingStatus` after scale-out
- **Severity**: high
- **Kind**: bug / ux
- **Where**: `src/charm.py:46-58` (all 6 components depend on `leadership_gate`)
- **Evidence**: `juju scale-application envoy 2`:
  ```
  Unit          Workload  Agent      Message
  envoy/0*      active    idle
  envoy/1       waiting   executing  [leadership-gate] Waiting for leadership
  ```
  `envoy/1` never becomes active. `LeadershipGateComponent.ready_for_execution()` returns
  `self._charm.unit.is_leader()`, `False` for any non-leader. All 6 components have
  `depends_on=[self.leadership_gate]` (directly or transitively), so
  `ComponentGraph.yield_executable_component_items()` never yields anything past the leadership
  gate for non-leaders.
- **Why it matters**: Horizontal scaling is impossible; scaling to 2+ units wastes resources on
  a permanently stuck unit. Scaling back down triggers a failing `remove` hook on the non-leader
  and an orphaned pod (see next finding).
- **Fix**: Document prominently that HA/scale-out is unsupported, or refactor the dependency
  graph so only leader-specific components (SDI ingress broadcast, `KubernetesServicePatch`)
  depend on `leadership_gate`. The `grpc` and `envoy_pebble_container` components read relation
  data and start the workload independently of leadership; removing their dependency would let
  non-leaders reach `active`.
- **Linter rule**: not mechanically checkable.

### `remove` hook fails on non-leader units, leaving orphaned Kubernetes pods
- **Severity**: high
- **Kind**: bug
- **Where**: `charmed_kubeflow_chisme.components.charm_reconciler` (inherited behaviour);
  `src/charm.py:46-58` (hard dependency on leadership gate)
- **Evidence**: `juju scale-application envoy 1` (scaling down from 2):
  ```
  16:23:15+12:00  juju-unit  executing    running remove hook
  16:23:16+12:00  juju-unit  error        hook failed: "remove"
  ```
  The `remove` hook fires on the non-leader and fails because `CharmReconciler.reconcile()` hits
  the leadership-gate deadlock. Kubernetes does not clean up the `envoy-1` pod once the hook
  fails — the unit agent stays alive in error state. Manual cleanup required:
  `kubectl delete pod envoy-1 -n rv-envoy-k8s`.
- **Why it matters**: Routine scale-down fails, leaving orphaned pods and requiring manual
  `juju resolve` plus manual Kubernetes cleanup — makes autoscaling dangerous.
- **Fix**: Fix the non-leader deadlock (see previous finding), or make the `remove` handler skip
  reconciliation on non-leaders (early return when `not self.unit.is_leader()`).
- **Linter rule**: not mechanically checkable.

### `service-mesh`, `require-cmr-mesh`, `provide-cmr-mesh` relations are declared but unhandled
- **Severity**: high
- **Kind**: bug
- **Where**: `metadata.yaml` (declarations); `src/charm.py` (no handlers)
- **Evidence**: `metadata.yaml` declares:
  - `service-mesh` (`interface: service_mesh`, limit 1)
  - `require-cmr-mesh` (`interface: cross_model_mesh`)
  - `provide-cmr-mesh` (`interface: cross_model_mesh`)

  No code in `src/charm.py` or any component handles these. The `istio_beacon_k8s` library
  ships a `ServiceMeshConsumer` capable of handling `service-mesh`/`cross_model_mesh`, and it is
  imported for the `metrics-endpoint` relation in `AmbientMeshRequirerComponent`, but the charm
  never instantiates it for these three relations. `juju integrate envoy:service-mesh
  <provider>:service-mesh` creates the relation and fires `service-mesh-relation-created`, but
  the charm does nothing — no policies applied, no labels added, no mesh subscription. Same for
  the CMR mesh relations. (No `service_mesh`-providing charm was available in the test
  environment to confirm the relation-created event beyond this; the absence of handler code is
  confirmed by inspection.)
- **Why it matters**: Operators relating envoy to a service mesh or cross-model mesh will believe
  the relation works when it silently does nothing.
- **Fix**: Remove the declarations from `metadata.yaml` if unused, or instantiate the
  corresponding handlers (`ServiceMeshConsumer` for `service-mesh`, and matching CMR handling).
- **Linter rule**: not mechanically checkable — requires cross-referencing metadata declarations
  with handler code.

### Integration tests require Juju < 4.0 but the deployed/test controller runs Juju 4.x
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py`; `tox.ini`; environment (`concierge-k8s-4` runs
  Juju 4.0.12)
- **Evidence**:
  ```
  ERROR tests/integration/test_charm.py::test_build_and_deploy
      juju.errors.JujuConnectionError: juju server-version 4.0.12 not supported
  ```
  All 7 integration tests error this way against Juju 4.x — the `juju` Python client package in
  the tox venv doesn't support Juju 4.x servers. `tox -e lint` (`pflake8` over `src/`/`tests/`)
  passes, but `tox -e integration` cannot run at all on the deployed infrastructure.
- **Why it matters**: Ingress, security-context, alert-rule, metrics and logging integration
  paths are only validated by manual testing, never by the project's own integration suite, on
  the infrastructure this review targets.
- **Fix**: Update the `juju` Python package constraint to support Juju 4.x, or add a dedicated
  Juju 4.x CI job.
- **Linter rule**: not mechanically checkable.

### `config-changed` (and other relation hooks) fire twice per event, doubling reconcile work
- **Severity**: medium
- **Kind**: performance
- **Where**: `juju.worker.uniter` (Juju behaviour); no guard in the charm
- **Evidence**: uniter log on `juju config envoy http-port=9092`:
  ```
  unit-envoy-0: 16:38:49 INFO juju.worker.uniter.operation ran "config-changed" hook
  unit-envoy-0: 16:38:50 INFO juju.worker.uniter.operation ran "config-changed" hook
  ```
  Pebble log shows two `Pushing file /var/lib/pebble/default/envoy-config.yaml` events at
  04:38:49 and 04:38:50 UTC, matching the two dispatches. `grpc-relation-changed` and
  `ingress-relation-created` show the same double-fire pattern. This is Juju's uniter
  dispatching the hook twice, not `CharmReconciler` re-triggering itself.
- **Why it matters**: Every config or relation change does twice the work; any component with
  side effects (e.g. a relation broadcast) fires twice.
- **Fix**: Add a guard in `CharmReconciler.reconcile()` to detect and skip a duplicate dispatch
  within the same hook execution, or file this as a Juju bug.
- **Linter rule**: "Hook handler should guard against duplicate dispatch within a single hook
  execution" — not mechanically checkable without runtime tracing.

### `SdiRelationBroadcasterComponent.get_status()` shows a stale status briefly after relation removal
- **Severity**: medium
- **Kind**: bug (library)
- **Where**: `charmed_kubeflow_chisme.components.serialised_data_interface_components`
  (`SdiRelationBroadcasterComponent.get_status()`)
- **Evidence**: After `juju remove-relation envoy:ingress traefik-k8s:ingress`, the
  `ingress-relation-broken` hook fires and the unit goes idle, but the Juju application status
  briefly shows `"[relation:ingress] List of <ops.model.Relation ingress:10> versions not found
  for apps: traefik-k8s"` for roughly 2 minutes, clearing on the next reconcile (e.g.
  `config-changed`). Root cause: when `interface.get_data()` returns an empty dict, accessing
  `self.model.relations[self._relation_name][0]` raises `KeyError`/`IndexError`; the surrounding
  `except Exception` catches this and returns `BlockedStatus`/an error-derived status instead of
  `ActiveStatus`. The unit workload status updates correctly; only the `juju status` display
  lags until the next hook fires — this is a brief race, not a permanent hang.
- **Why it matters**: After removing an ingress relation, the operator briefly sees a misleading
  status message referencing the deleted relation.
- **Fix**: In `SdiRelationBroadcasterComponent.get_status()`, check `if not interface_data_dict`
  (or that the relation list is non-empty) before indexing, and return `ActiveStatus` when the
  relation has been removed. This is a library bug in `charmed_kubeflow_chisme`.
- **Linter rule**: "Relation component `get_status` must return `ActiveStatus` when the relation
  has been removed" — mechanically checkable.

### Ingress integration with traefik-k8s fails — SDI schema incompatibility, not just a version mismatch
- **Severity**: medium
- **Kind**: bug / docs
- **Where**: `metadata.yaml` (ingress SDI schema); traefik-k8s ingress implementation
- **Evidence**: `juju integrate envoy:ingress traefik-k8s:ingress` creates the relation, but
  envoy goes `WaitingStatus("[relation:ingress] List of ... versions not found for apps:
  traefik-k8s")`. traefik-k8s logs:
  ```
  unit-traefik-k8s-0: WARNING failed to fetch proxied endpoints: This application did not
    `publish_url` yet.
  unit-traefik-k8s-0: INFO Provider not ready; validation error encountered: failed to
    validate databag: {'_supported_versions': '- v1\n'}
  ```
  envoy's ingress interface declares `versions: [v1]` (SDI v1 only); traefik-k8s supports SDI
  ingress v2 only, and its own `ingress` schema fields (`model`, `name`, `host`, `port`,
  `strip-prefix`, `redirect-https`) share nothing with envoy's SDI v1 payload (`service`, `port`,
  `prefix`, `rewrite`) — the two charms are fundamentally incompatible for this relation, not
  merely on different versions of the same schema.
- **Why it matters**: Operators who try to relate envoy to traefik-k8s for ingress get a
  confusing waiting-status with no actionable message. The SDI `ingress` relation only works
  with charms implementing the same SDI schema (Kubeflow's own ingress stack), not with
  traefik-k8s.
- **Fix**: Document prominently that the `ingress` relation only works with Kubeflow's own
  ingress stack, and/or surface a clearer incompatibility message.
- **Linter rule**: not mechanically checkable.

### No workload health monitoring between hook events
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/components/pebble.py` (thin wrapper inheriting from `PebbleServiceComponent`)
- **Evidence**: `pebble stop envoy` makes the Pebble service `inactive`; Juju status remains
  `active` for more than 30 seconds, with a worst case lag of ~5 minutes until `update-status`
  fires. `PebbleComponent._events_to_observe` is hardcoded to only `pebble_ready`; no event is
  observed for a service transitioning from `active` to `inactive`.
- **Why it matters**: If the Envoy process dies between hooks (including from malformed upstream
  config — see the grpc data-validation finding below), the operator is not notified; the charm
  reports `active` while the workload is down.
- **Fix**: Observe `container.service.changed` events and trigger a reconcile, or add a
  background health-polling mechanism.
- **Linter rule**: "Pebble workload charms must observe service state change events" —
  mechanically checkable by verifying `_events_to_observe` includes a service-changed event.

### No grpc relation data validation — Envoy can fail silently on malformed upstream data
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/mlops_libs/v0/k8s_service_info.py` (`KubernetesServiceInfoObject`);
  `src/templates/envoy-config.yaml.j2` (uses values without validation)
- **Evidence**: `KubernetesServiceInfoObject` declares `name: str` and `port: str`, neither
  validated as non-empty or as a valid port number. `envoy-config.yaml.j2` interpolates
  `upstream_service`/`upstream_port` directly into Envoy's config. If the upstream provider sends
  an empty `name` or a non-numeric `port`, the generated config is invalid and Envoy fails to
  start — but Pebble started the process successfully, so the charm stays `active`, and the
  workload-monitoring gap above means the failure is never surfaced.
- **Why it matters**: A misconfigured upstream provider can make Envoy fail silently while the
  charm reports healthy; traffic is not proxied and the operator has no signal.
- **Fix**: Validate `name` (non-empty) and `port` (valid port number) in
  `K8sServiceInfoRequirerComponent` before using the values, or in the library's
  `get_data()`/`get_service_info()` path.
- **Linter rule**: not mechanically checkable.

### Blind `except Exception` in `AmbientMeshRequirerComponent`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/components/istio_ambient_requirer_component.py:58`
- **Evidence**:
  ```python
  except Exception as e:
      raise GenericCharmRuntimeError(f"Failed to submit ingress config: {e}")
  ```
- **Why it matters**: Catches `KeyboardInterrupt`, `SystemExit`, `MemoryError`, `RecursionError`;
  the `GenericCharmRuntimeError` wrapper obscures the original exception type.
- **Fix**: Catch the specific exceptions raised by the `istio_ingress_route` library; let
  system-level exceptions propagate.
- **Linter rule**: ruff BLE001 already detects this — not currently enabled/enforced for this
  file in the project's lint config.

### Unit test fixture uses malformed `_supported_versions` data, bypassing the real serialization path
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py`
- **Evidence**: The test hardcodes `app_data={"_supported_versions": "- v1"}` rather than going
  through `SerializedDataInterface.send_versions()` (which calls `yaml.safe_dump(list(versions))`
  and produces a different literal format, confirmed via the real traefik-k8s log line
  `'_supported_versions': '- v1\n'`). The test therefore never exercises the real
  `send_versions()` serialization path.
- **Why it matters**: The test passes even if the real serialization format changes or breaks.
- **Fix**: Construct the fixture via `yaml.safe_dump(["v1"])`, or drive the harness relation
  through a real `SerializedDataInterface` instance.
- **Linter rule**: not mechanically checkable.

### `tox -e lint` misses 313 lint violations in the vendored `lib/` directory
- **Severity**: medium
- **Kind**: lint / test-gap
- **Where**: `lib/charms/prometheus_k8s/v0/prometheus_scrape.py` (dominant),
  `lib/charms/loki_k8s/v1/loki_push_api.py`, `lib/charms/grafana_k8s/v0/grafana_dashboard.py`,
  `lib/charms/observability_libs/v1/kubernetes_service_patch.py`
- **Evidence**: `ruff check .` on the full repo finds 313 errors: 7 in `src/`/`tests/`
  (already covered by other findings) and 306 in `lib/` (UP006, UP007, UP032, UP035, UP045,
  PIE800, SIM117, SIM118, SIM201, BLE001, C419, RUF012, RUF015, RUF059, RUF100; 254 fixable with
  `--fix`). `tox -e lint` only runs `pflake8` against `src/` and `tests/`, and `codespell` with
  `--skip ./lib`, so none of this is caught by CI.
- **Why it matters**: Type-annotation modernization issues, mutable class attributes, and a blind
  `except Exception` sit in vendored libraries CI never touches.
- **Fix**: Enable ruff on `lib/` as a separate lint job, or fold it into the existing lint target.
- **Linter rule**: `ruff check lib/ --fix` would catch most of these automatically.

### Typos in vendored `istio_beacon_k8s` library
- **Severity**: medium
- **Kind**: lint
- **Where**: `lib/charms/istio_beacon_k8s/v0/service_mesh.py`
- **Evidence** (via `codespell lib/`):
  - line 252: `Polcy` → `Policy`
  - line 274: `currenlty` → `currently`
  - line 928: `polcies` → `policies`
- **Why it matters**: These appear in user-facing error/log messages.
- **Fix**: `codespell --fix lib/charms/istio_beacon_k8s/v0/service_mesh.py`.
- **Linter rule**: `codespell` catches this, but `tox.ini` skips `lib/` — add `lib/` to the
  scanned paths.

### `logger.warn()` deprecated since Python 3.3
- **Severity**: medium
- **Kind**: lint
- **Where**: `src/components/istio_relations_conflict_detector.py:23`
- **Evidence**: `logger.warn(...)` — flagged by ruff G010.
- **Fix**: `logger.warning(...)`.
- **Linter rule**: ruff G010 (enabled by default).

### Grafana dashboard template uses deprecated `__inputs` provisioning format
- **Severity**: medium
- **Kind**: docs
- **Where**: `src/grafana_dashboards/envoy-service.json.tmpl`
- **Evidence**: Template includes a Grafana 5.x-era `__inputs`/`__requires` block alongside the
  `${prometheusds}` variable that `GrafanaDashboardProvider` actually injects at relation time.
  The `__inputs` block is unused in practice and may confuse newer Grafana versions.
- **Fix**: Remove the `__inputs`/`__requires` block; `GrafanaDashboardProvider` supplies the
  datasource name at relation time.
- **Linter rule**: not mechanically checkable.

### `metadata.yaml` UID/GID comment misleading after rock migration
- **Severity**: low
- **Kind**: docs
- **Where**: `metadata.yaml:17`
- **Evidence**: The rock (`ghcr.io/kubeflow/kfp-metadata-envoy:2.16.0`) runs as UID 584792, but
  `metadata.yaml` still declares `uid: 0, gid: 0` with a comment saying to set these to 584792
  "when using the rock" — a migration that was apparently never completed.
- **Fix**: Update the values/comment to reflect the actual rock UID, or remove the comment if the
  values are intentionally left as-is.
- **Linter rule**: not mechanically checkable.

### Integration test lint issues (ruff)
- **Severity**: low
- **Kind**: lint
- **Where**: `tests/integration/test_charm.py`
- **Evidence**: C419 (unnecessary `all([...])`), RUF059 (unused variable `res_text`), SIM117
  (nested `with` statements).
- **Fix**: `ruff check tests/ --fix` handles C419 and SIM117; `res_text` needs a manual rename.
- **Linter rule**: ruff C419, RUF059, SIM117.

### Shebang on non-executable file
- **Severity**: low
- **Kind**: lint
- **Where**: `src/components/k8s_service_info_requirer_component.py:1`
- **Evidence**: A `#!` shebang line is present, but the file is not executable — flagged by ruff
  EXE001.
- **Fix**: Remove the shebang; this file is imported as a module, never executed directly.
- **Linter rule**: ruff EXE001.

### `Optional[str]` should be `str | None`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/components/k8s_service_info_requirer_component.py:31`
- **Evidence**: `relation_name: Optional[str] = "k8s-service-info"` — flagged by ruff UP045.
- **Fix**: `relation_name: str | None = "k8s-service-info"`.
- **Linter rule**: ruff UP045 (auto-fixable with `--fix`).

### Unit tests use deprecated `Harness` API
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py`
- **Evidence**: `PendingDeprecationWarning: Harness is deprecated. For the recommended approach,
  see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html`
- **Fix**: Migrate to `Scenario` (or the recommended replacement API).
- **Linter rule**: not mechanically checkable.

## Worth copying

- **`IstioRelationsConflictDetector` component** (`src/components/istio_relations_conflict_detector.py`):
  a clean, single-responsibility component that detects mutually-exclusive relations and returns
  a `BlockedStatus` with a precise, human-readable message — better than scattering the check
  across handlers.
- **`LazyContainerFileTemplate` context as a lambda**: the Pebble config file uses
  `context=lambda: {...}` so relation data is re-read at reconcile time, not snapshotted at
  `add_layer` time — the correct pattern for charms deriving config from relation data.
- **`KubernetesServicePatch` initialized unconditionally in `__init__`** (`src/charm.py`):
  registered once at startup from config-derived `ServicePort` objects, rather than re-created on
  every reconcile — correct for a service patch.
- **`test_each_istio_ingress_route_relation_receives_config`** (`tests/unit/test_charm.py`):
  verifies HTTPRoute config is submitted to each of multiple ingress relations — a non-obvious
  correctness property the unit tests explicitly cover.
- **`charmed_kubeflow_chisme.CharmReconciler`**: the component graph with explicit `depends_on`
  ordering is readable and maintainable, and its automatic registration of relation-change event
  handlers is elegant.
- **No Juju secrets used**: appropriate for this charm's design — no secrets read, no `secret-*`
  hooks, no `model.get_secret()` calls.
- **`reconcile()` resets all `.executed=False`** on every reconcile, defending against ops issue
  #736 (charm not re-initialized on custom events) — a correct defensive pattern.

## Common-practice notes

| Area | Status | Notes |
|---|---|---|
| `lib/charms/` vendoring | Convention | Follows ecosystem standard; 7 libraries in `lib/charms/` |
| `src/` layout | Convention | One component per file; clear separation |
| `charmcraft.yaml` parts | Leads | Poetry-based build with `uv`-bootstrapped Poetry 2.x; more sophisticated than most |
| `metadata.yaml` `charm-user: non-root` | Convention | Juju 4.x style |
| Config options as strings | Drift | Both `admin-port` and `http-port` declared as `type: string` but used as integers; `ops` supports `type: int`, which would fix the `__init__` crash |
| Terraform module | Convention | Standard `juju_application` resource; well documented |
| CI: lint → unit → build → release | Convention | Canonical pattern; separate integration job per test type |
| Poetry for dev, pip-compile for CI | Convention | `poetry.lock` committed |
| Renovate config | Broken | Issue #184: invalid JSON preset `github>canonical/charmed-kubeflow-workflows` |
| Scaling / HA | Not supported | `LeadershipGateComponent` is a hard dependency for all components; non-leaders permanently blocked. By design but undocumented |
| Unhandled relations | Bug | `service-mesh`, `require-cmr-mesh`, `provide-cmr-mesh` declared in `metadata.yaml` with no handlers in `src/charm.py` |
| codespell/ruff skip `lib/` | Bug | `tox.ini lint` skips `lib/` for both codespell and pflake8 — typos and 306 lint issues in vendored libs go undetected |
| Secrets | Not used | No `model.get_secret()`, no `secret-*` hooks. Appropriate |
| Ingress SDI compat | Incompatible | envoy supports `ingress` SDI v1 only; traefik-k8s's `ingress` schema shares no fields with it |
| Unit test harness | Drift | Uses deprecated `Harness`; `Scenario` is the recommended replacement |
| Integration test Juju version | Broken | Tests require Juju < 4.0; deployed/test controller is Juju 4.x — integration tests never run against it |
| Double hook fire | Juju behaviour | `config-changed`, `grpc-relation-changed`, `ingress-relation-created` all fire twice per event; charm has no guard |
| `remove` hook failure | Bug | Non-leader units fail the `remove` hook, leaving orphaned Kubernetes pods |
| Actions | None | No `actions.yaml`; the charm defines no actions |

## Tests

**Unit tests (14 tests, all pass):**
`PYTHONPATH="lib:src" python3 -m pytest tests/unit/test_charm.py -v` — 14/14 pass, 97 warnings
(`Harness` deprecated, `JujuVersion.from_environ()` deprecated in `loki_push_api.py`,
`logger.warn` deprecated in `istio_relations_conflict_detector.py`).

**Missing unit coverage**: the `__init__` crash path on bad config; the double `config-changed`
fire; the non-leader blocking/`remove`-hook-failure behaviour; the blind `except Exception` in
`istio_ambient_requirer_component.py`; Pebble service-state-change observation; the unhandled
`service-mesh`/`cmr-mesh` relations; graceful degradation on malformed grpc relation data.

**Test fixture issue**: `_supported_versions` is hardcoded as a literal string instead of being
constructed via `yaml.safe_dump(["v1"])`/`send_versions()`, so the test doesn't exercise the real
serialization path (see Findings).

**Integration tests**: cannot run against the Juju 4.x controller —
`juju.errors.JujuConnectionError: juju server-version 4.0.12 not supported` for all 7 tests.
`test_web_grpc_mlmd` is commented out (issue #106: gRPC-web returns 503 after an Envoy upgrade).

**Linter findings** (confirmed by direct `ruff check`):
- `src/components/istio_ambient_requirer_component.py:58`: BLE001 (blind `except Exception`)
- `src/components/istio_relations_conflict_detector.py:23`: G010 (`logger.warn`)
- `src/components/k8s_service_info_requirer_component.py:1`: EXE001 (shebang)
- `src/components/k8s_service_info_requirer_component.py:31`: UP045 (`Optional[str]`)
- `tests/integration/test_charm.py`: C419, RUF059, SIM117
- `lib/` (all 7 vendored libraries): 306 additional errors, not scanned by `tox -e lint`

## Docs

**README.md** (435 bytes): minimal — "deploy with `juju deploy envoy`" plus a link to
juju.is/docs. No architecture explanation, no relation guide, no config reference, no
troubleshooting, and no mention that scaling beyond 1 unit is unsupported.

**CONTRIBUTING.md** (3383 bytes): the best document in the repo — clear on the contributor
workflow, how to update manifests by diffing the upstream KFP repo, how to manage Python
dependencies (poetry groups), how to run tox environments.

**Terraform README.md** (2348 bytes): complete — inputs table, outputs table, two usage
examples (`juju_model` resource and `data` source). Follows the canonical module format.

**charmcraft.yaml comments**: extensive and valuable — documents magic constants and build
choices (uv bootstrapping, rustup workaround, etc.).

**charmhub description**: just `https://www.envoyproxy.io/` — a bare URL, not a description.
Users landing on charmhub get no information about what this charm does, what relations it
needs, or which Kubeflow component it serves.

## Open questions

1. Is the double `config-changed` (and other hook) dispatch a Juju bug worth filing upstream, or
   should the charm add a reconcile-level guard against duplicate dispatch within one hook
   execution?
2. Should `config.yaml` switch `admin-port`/`http-port` to `type: int` (input-time validation) or
   should `charm.py` add try/except around the casts? The schema approach protects operators
   earlier; try/except is more robust for composite validation.
3. Is GitHub issue #106 (gRPC-web returning 503) resolved against Envoy 2.16.0? The relevant
   integration test is commented out and was not re-verified here.
4. Should `metadata.yaml`'s `uid: 0, gid: 0` be updated to the rock's actual UID (584792), per
   the stale migration comment?
5. Should the charm support scale-out at all? If so, only leader-specific components (SDI
   ingress broadcast, `KubernetesServicePatch`) need to depend on `leadership_gate` — `grpc` and
   `envoy_pebble_container` do not.
6. Were `service-mesh`, `require-cmr-mesh`, `provide-cmr-mesh` intentionally left unhandled? The
   `istio_beacon_k8s` library has the handlers available but the charm never instantiates them
   for these relations — this looks like dead metadata that should either be wired up or removed.
