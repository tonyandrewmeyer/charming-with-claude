# istio-k8s

A mature, well-structured k8s charm that deploys and manages the Istio service mesh control plane (pilot/istiod, CNI, ztunnel). The charm itself is thin (~780 lines), delegating Kubernetes resource management to the `canonical_service_mesh` PyPI library and manifest generation to `istioctl`. It follows canonical observability conventions, uses a clean reconciler pattern, and handles the ambient mesh profile correctly. It is not safe to run in production as-is: removing the application deletes cluster-scoped CRDs regardless of how many other consumers rely on them (confirmed live), relating tracing permanently breaks non-leader units, bad config values produce silent unrecoverable hook errors, and cross-channel downgrades brick the control plane. A maintainer should fix the `_remove` handler's CRD deletion first — it is the one finding with cluster-wide blast radius — then address the tracing and config-error-handling bugs before recommending this charm for anything beyond a single, disposable deployment.

| | |
|---|---|
| Repo | canonical/istio-k8s-operator @ `639f306` (2026-06-25) |
| Charms | istio-k8s, service-mesh-tester (test helper) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5), rev 58 from 2/edge; concierge-k8s-3 (Juju 3.6.25), rev 58 and rev 71 from dev/edge |
| Reviewed | 2026-08-10 |

## What it does

Deploys the Istio control plane into the model namespace via `istioctl manifest generate`. Manages three resource groups via `KubernetesResourceManager`: Istio CRDs, Gateway API CRDs, and control-plane resources (Deployments, DaemonSets, RBAC, ConfigMaps, HPAs). Integrates with the Canonical Observability Stack (`metrics-endpoint`, `grafana-dashboard`, `charm-tracing`, `workload-tracing`), supports external authorizer configuration via `istio-ingress-config`, publishes mesh metadata via `istio-metadata`, accepts CA certs for JWKS resolution via `jwks-ca-cert`, and can enable a hardened mode that creates global deny-all `AuthorizationPolicy` resources for ztunnel and waypoints.

## Deployment log

### Juju 4.0.5 (concierge-k8s-4)

```
$ juju add-model rv-istio-k8s --controller concierge-k8s-4
$ juju deploy istio-k8s --channel 2/edge --trust
Deployed "istio-k8s" from charm-hub charm "istio-k8s", revision 58 in channel 2/edge on ubuntu@24.04/stable
```

- **Deploy time**: ~20 seconds to active/idle (install → leader-elected → config-changed → start → pebble-ready)
- **Workload version**: 1.26.1 (set from `istioctl version`)
- **Pods running**: istiod (Deployment), ztunnel (DaemonSet), istio-cni-node (DaemonSet), istio-k8s (StatefulSet), metrics-proxy sidecar
- **CNI readiness probe failing**: `istio-cni-node` reports `Readiness probe failed: HTTP probe failed with statuscode: 503` throughout the deployment's lifetime, on both Juju versions. The DaemonSet shows `desiredNumberScheduled=1, numberReady=0`. Charm status stays `Active` regardless — see the status-check finding below.

### Config changes

```
$ juju config istio-k8s platform=microk8s   # no-op: already the default
```

Triggered 3 `istioctl` subprocess calls (CRD manifest, control-plane manifest, version check) plus ~25 Kubernetes PATCH calls, despite no configuration change — the charm re-generates and re-applies all manifests on every `config-changed`.

```
$ juju config istio-k8s hardened-mode=true
```

Created two `AuthorizationPolicy` resources: `policy-global-allow-nothing-ztunnel` and `policy-global-allow-nothing-waypoint`. Flipping back to `false` removed them. Works correctly.

### Scaling

```
$ juju scale-application istio-k8s 2
```

The second unit comes up as non-leader with status `Backup unit; standing by for leader take over`. The HPA's `minReplicas`/`maxReplicas` update to 2, and the istiod Deployment scales to 2 replicas, lagging ~10s behind the HPA update (normal Kubernetes HPA behaviour).

### Juju 3.6.25 (concierge-k8s-3)

Same revision, same channel. Deployed and went active in ~20 seconds. Identical behaviour; CNI readiness probe also failing.

### Cross-channel refresh (dev/edge rev 71 ↔ 2/edge rev 58)

- **dev/edge (rev 71)**: Deploys Istio 1.29.0 using Canonical rocks (`docker.io/ubuntu/istio-pilot:1.29-24.04_stable`). The charm correctly reports `Waiting: Istio CNI not ready. Possible platform mismatch. Check charm config.` when the CNI DaemonSet isn't ready — the status check works on this revision.
- **`jwks-ca-cert` endpoint**: `juju refresh` output shows `adding endpoint "jwks-ca-cert" to default space "alpha"` — rev 58 does not include this relation endpoint; rev 71 adds it.
- **Refresh back to 2/edge (downgrade)**: Causes persistent `config-changed` hook failure. The istiod control plane running v1.29 cannot be reconciled by the older (v1.26) istioctl binary. No version guard, no informative message.
- Setting `cniConfDir`/`cniBinDir` to the correct microk8s paths did not fix the CNI readiness issue — `istio-cni-node` still reports 0/1 ready. Appears to be a microk8s-specific issue with Istio's CNI chaining rather than a charm bug.

### Workload inspection

- Images on rev 58: upstream distroless Istio images (`docker.io/istio/pilot:1.26.1-distroless`, `docker.io/istio/install-cni:1.26.1-distroless`, `docker.io/istio/ztunnel:1.26.1-distroless`), not the Canonical rocks referenced in HEAD source.
- Images on rev 71: Canonical rocks (`docker.io/ubuntu/istio-pilot:1.29-24.04_stable`, `docker.io/ubuntu/istio-install-cni:1.29-24.04_stable`, `docker.io/ubuntu/istio-ztunnel:1.29-24.04_stable`).
- Metrics-proxy sidecar: Pebble service `metrics-proxy` active, command `metrics-proxy --labels charms.canonical.com/rv-istio-k8s.istio-k8s.telemetry=aggregated`.
- Memory: istiod ~39Mi, ztunnel ~1Mi, istio-cni-node ~15Mi, charm unit ~42Mi.
- ConfigMap `istio`: correctly sets `accessLogFile: /dev/stdout`, `discoveryAddress: istiod.rv-istio-k8s.svc:15012`, `rootNamespace: rv-istio-k8s`.

### Kill test

Killing the istiod pod resulted in a new pod within seconds (Juju 4: seconds; separately logged as ~10s). The charm remained `Active` throughout.

### Failure injection

- `platform=""` (empty string, valid per schema): no error, charm stayed `Active`. `_get_istioctl` checks `if self.parsed_config["platform"]:` before applying the override, so empty string correctly skips the platform setting.
- `platform="invalid-platform"`: charm immediately went to `error` with `hook failed: "config-changed"` and `exit status 1`; no `juju-log` output and no message in `juju status`. Recovered by resetting config and `juju resolve`.
- `cniBinDir="/nonexistent/path/that/does/not/exist"`: same silent failure.
- **Relate to grafana-agent-k8s with charm-tracing**: non-leader unit (unit 1) stuck permanently in `error` on `hook failed: "charm-tracing-relation-created"`. `juju resolve` retries and fails again. Removing the relation does not clear it — only `juju resolve` after the remote application is completely destroyed recovers.
- **Cross-channel downgrade**: refreshing from dev/edge (rev 71, Istio 1.29) to 2/edge (rev 58, Istio 1.26) produces persistent `config-changed` hook failure; the older istioctl binary cannot reconcile against the newer control plane left behind.
- **Attempted `jwks-ca-cert` integration**: relating rev 58 to `self-signed-certificates:send-ca-cert` failed with "no compatible endpoints" — confirms the endpoint is absent on the published revision.

## Observed behaviour

1. **CNI DaemonSet never reaches ready state on microk8s**, across both Juju 3 and 4, and both rev 58 (Istio 1.26.1) and rev 71 (Istio 1.29.0). The CNI agent logs `no networks found in /host/etc/cni/net.d`; the readiness probe returns 503. On rev 58 the charm silently reports `Active` despite this; on rev 71 it correctly reports `Waiting: Istio CNI not ready. Possible platform mismatch. Check charm config.`
2. **Every `config-changed` re-applies all resources**, ~25 Kubernetes PATCH calls even when nothing changed — visible in debug-log and consistent with the reconciler code.
3. **HPA-based scaling works**, with the expected lag between HPA update and Deployment replica count change.
4. **Bad config values cause silent hook failures** — `platform="invalid-platform"` produces `hook failed: "config-changed"` / `exit status 1` with no visible error message or `juju-log` output. Diagnosis requires reading raw uniter logs.
5. **Cross-channel downgrade is broken** — refreshing from dev/edge (v1.29) to 2/edge (v1.26) leaves the charm permanently erroring on `config-changed`.
6. **Non-leader units break on the charm-tracing relation** — relating grafana-agent-k8s puts non-leader units into permanent error on `charm-tracing-relation-created`.
7. **CRD deletion confirmed** — `juju remove-application istio-k8s` removes all Istio and Gateway API CRDs from the cluster (verified with `kubectl get crd`; 22 standard CRDs remained, none of the Istio/Gateway API ones).
8. **`jwks-ca-cert` endpoint only in newer revisions** — absent from rev 58, present from rev 71 onward; confirmed both by `juju show-application` and a failed relation attempt.

## Findings

### Removing the application deletes cluster-scoped CRDs
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:299-303`
- **Evidence**: `_remove` runs `if self.unit.is_leader(): for name in self._resource_manager_factories: krh = self._get_resource_manager(name); krh.delete()`. After `juju remove-application istio-k8s` (single unit, rev 71), `kubectl get crd` showed all Istio CRDs (authorizationpolicies, virtualservices, etc.) and Gateway API CRDs (httproutes, gateways, etc.) gone; only 22 standard Kubernetes CRDs remained. Confirmed on both Juju 3 and Juju 4. Tracked upstream as open issue #79.
- **Impact**: Removing this application is a cluster-wide destructive operation, not a scoped one — any custom resources of these types anywhere on the cluster are cascade-deleted, even when removal is triggered by a single unit departing.
- **Fix**: Guard the delete with a remaining-unit check (e.g. `if len(self.model.app.units) > 1: return`) before deleting cluster-scoped resources, or move CRD lifecycle management out of the charm entirely (open issue #83).
- **Linter rule**: `_remove` handler calls `delete()` on cluster-scoped resources without checking remaining unit count — mechanically checkable if cluster-scoped resource types are registered in a known way.

### `config-changed` failures produce no visible error message
- **Severity**: high
- **Kind**: ux
- **Where**: `src/charm.py:216-237` (`_reconcile`, no try/except), `src/istioctl.py:219-226` (`_run` raises `IstioctlError`)
- **Evidence**: Setting `platform="invalid-platform"` produced `hook failed: "config-changed"` / `exit status 1`, no `juju-log` output, and no message in `juju status`. Same silent failure with `cniBinDir="/nonexistent/path/that/does/not/exist"`.
- **Impact**: Operators see "error" with no actionable information; the only diagnostic path is raw uniter logs. Bad config leaves the charm in an unrecoverable error state until config is reset and `juju resolve` is run.
- **Fix**: Wrap `_reconcile` in a try/except that catches `IstioctlError` and sets `BlockedStatus(str(e))` (or similar) instead of letting the hook crash.
- **Linter rule**: not established (requires detecting unguarded subprocess calls in the reconciler).

### `trace_charm` decorator breaks non-leader units when `charm-tracing` is related
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:115,146` (`@trace_charm` decorator, `TracingEndpointRequirer`); `lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py` (vendored)
- **Evidence**: Relating `charm-tracing` to grafana-agent-k8s put the non-leader unit (istio-k8s/1) permanently into `error` on `hook failed: "charm-tracing-relation-created"`. Error persists after the relation is removed; only `juju resolve` after the remote application is fully destroyed recovers. Leader unit unaffected.
- **Impact**: Any deployment scaled beyond one unit and integrated with tracing gets its non-leader units permanently stuck in error, with no resolve path short of tearing down the tracing relation entirely.
- **Fix**: Make the vendored `trace_charm`/`_setup_root_span_initializer` tolerant of non-leader units — either skip tracing setup on non-leaders or catch setup exceptions — or restrict tracing setup to the leader unit in the charm itself.
- **Linter rule**: not established.

### Downgrade between incompatible Istio versions causes unrecoverable error
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:216-237` (`_reconcile`), `src/istioctl.py:99-120` (`manifest_generate`)
- **Evidence**: Fresh deploy of dev/edge (rev 71, Istio 1.29.0), then `juju refresh --channel 2/edge` (rev 58, Istio 1.26.1), causes persistent `config-changed` failure. The older istioctl (1.26.1) cannot reconcile against the existing 1.29.0 control plane; workload version stays stuck at `1.29.0`.
- **Impact**: Operators who move to a newer channel and then need to roll back find the charm permanently broken, with no recovery short of destroying and recreating the model.
- **Fix**: Add a pre-check in `_reconcile` comparing the running control-plane version (`istioctl version`) against what the current revision supports, and refuse to proceed with a clear `BlockedStatus` message if the running version is newer. Document that downgrades are unsupported.
- **Linter rule**: not established.

### Status checks silently swallow Kubernetes API errors (rev 58; fixed in rev 71)
- **Severity**: medium (low on rev 71)
- **Kind**: bug
- **Where**: `src/charm.py:275-283`, `src/charm.py:288-296`
- **Evidence**: `_check_daemonset_ready` and `_check_deployment_ready` wrap lightkube calls in `try: ... except Exception as e: LOGGER.error(...); return None`, falling through to `ActiveStatus()`. On deployed rev 58, the CNI DaemonSet was 0/1 ready but the charm reported `Active`. On rev 71 the same code path correctly reported `Waiting: Istio CNI not ready.` — meaning the lightkube call succeeded there and only the ready-count logic differs by revision; the remaining risk is that a genuine (transient) K8s API error would still be swallowed into `None`/Active on either revision.
- **Impact**: Operators can't trust `Active` status to mean the CNI is actually ready.
- **Fix**: Return a non-`None`/non-Active status (e.g. `MaintenanceStatus(f"Checking {name}: {e}")`) when the K8s API call fails, instead of silently returning `None`.
- **Linter rule**: status-check methods catching bare `Exception` without returning a non-None status — mechanically checkable.

### `get_deployed_resources` re-raises 404 after logging "Ignoring"
- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/canonical_service_mesh/k8s/resource_manager/_resource_manager.py:183-186`
- **Evidence**: `except ApiError as error: if error.status.code == 404: self.log.debug(f"resource type {resource_type} not found in cluster. Ignoring this type."); raise error` — the `raise error` sits at the same indentation as the `if`, so it is unconditional, not inside the block it appears to guard.
- **Impact**: If any resource type in `CONTROL_PLANE_RESOURCE_TYPES` or `ISTIO_CRDS_RESOURCE_TYPES` 404s (e.g. an API group not registered on the cluster), the whole `reconcile()` call fails despite the log message implying the 404 is tolerated.
- **Fix**: Move `raise error` inside an `else` block, or replace with `continue` to actually skip the resource type as the log message states.
- **Linter rule**: bare `raise` immediately after a conditional 404 log inside an `except` block — mechanically checkable via AST analysis.

### `jwks-ca-cert` endpoint missing from published rev 58
- **Severity**: medium
- **Kind**: bug
- **Where**: `charmcraft.yaml:84,107-115` (HEAD) vs. published rev 58
- **Evidence**: `juju show-application istio-k8s` on rev 58 lists only `charm-tracing`, `grafana-dashboard`, `istio-ingress-config`, `istio-metadata`, `metrics-endpoint`, `peers`, `workload-tracing` — no `jwks-ca-cert`. `juju refresh` to dev/edge rev 71 shows `adding endpoint "jwks-ca-cert" to default space "alpha"`. A relation attempt to `self-signed-certificates:send-ca-cert` on rev 58 failed with "no compatible endpoints".
- **Impact**: Operators on the default 2/edge channel cannot relate istio-k8s to a CA certificate provider for JWKS resolution — the feature exists in source but hasn't shipped to that channel.
- **Fix**: Release current HEAD to 2/edge, or document which channel carries the `jwks-ca-cert` endpoint.
- **Linter rule**: not established.

### Config cached indefinitely after first read
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:309-314`
- **Evidence**: `if self._parsed_config is None: config = dict(self.model.config.items()); self._parsed_config = CharmConfig(**config); ...`. `_parsed_config` is only reset to `None` in `__init__`. `hardened-mode=true` was observed to work correctly in deployment, so this is unverified as an actual live bug — it depends on hook execution order (whether `parsed_config` is accessed before the first `config-changed`). `(unverified)`
- **Impact**: If triggered, config changes after the first access would be silently ignored by the reconciler.
- **Fix**: Reset `self._parsed_config = None` at the top of `_reconcile`, or drop the caching (pydantic validation is cheap).
- **Linter rule**: instance-variable cache of config without invalidation in the config-changed handler — mechanically checkable.

### Every `config-changed` re-applies all manifests from scratch
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:220-237`
- **Evidence**: `_reconcile` unconditionally calls `_reconcile_gateway_api_crds`, `_reconcile_istio_crds`, `_reconcile_authorization_policies`, `_reconcile_control_plane`, `_set_istio_version` on every invocation — 3 `istioctl` subprocess calls plus ~25 Kubernetes PATCH calls, confirmed via a no-op `platform=microk8s` config change.
- **Impact**: Unnecessary Kubernetes API load and noisy debug-log on every config change, even no-ops.
- **Fix**: Hash current settings and compare against a stored hash (peer relation data or similar); skip manifest regeneration when nothing changed.
- **Linter rule**: not established.

### `IngressConfigRequirer` duplicated between `deps` and vendored `lib`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:17-19` vs. `lib/charms/istio_k8s/v0/istio_ingress_config.py`
- **Evidence**: The charm imports `IngressConfigRequirer` from the PyPI `canonical_service_mesh` package, but an older copy (`LIBPATCH=4`, `LIBID = "12331b5ac41547e087edd7ac993176ed"`, `PYDEPS = ["pydantic>=2"]`) still lives in `lib/` and remains publishable to Charmhub.
- **Impact**: Charms fetching this library from Charmhub get the stale, unmaintained copy instead of the maintained PyPI version. Related to open issue #129 (istio-metadata migration).
- **Fix**: Delete the local `istio_ingress_config.py` if there are no external consumers, or turn it into a thin re-export of the PyPI package.
- **Linter rule**: charm library in `lib/` with a corresponding import already sourced from a PyPI dependency — mechanically checkable.

### Fake-authz detection can return a partial provider list
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:498-500`
- **Evidence**: `if self.ingress_config.is_fake_authz_config(relation): return providers` — the comment implies an empty-list return, but the code returns the `providers` list accumulated so far. With two `istio-ingress-config` relations, a fake config on the second leaks the first relation's real provider config into the result.
- **Impact**: Low in practice, since `istio-ingress-config` is typically single-relation, but it's a correctness bug.
- **Fix**: `return []` instead of `return providers`.
- **Linter rule**: not established (requires semantic understanding of intent).

### Ztunnel hardened-mode `AuthorizationPolicy` uses empty `spec={}`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:716-720`
- **Evidence**: The ztunnel policy is created with `spec={}`, while the waypoint policy uses a proper `AuthorizationPolicySpec` with `targetRefs`. An empty spec in Istio's `AuthorizationPolicy` selects all workloads in the namespace with no rules, which is default-allow, not deny. `(unverified — not confirmed against actual mesh traffic)`
- **Impact**: If this behaves as the Istio docs describe, "hardened mode" may not actually deny traffic to ztunnel despite naming the policy `allow-nothing`.
- **Fix**: Give the ztunnel policy explicit deny semantics (empty rules list plus `action: DENY`, or equivalent to the waypoint policy's `targetRefs` approach); verify against Istio's documented empty-spec behaviour.
- **Linter rule**: not established.

### `dict()` used instead of `model_dump()` on a Pydantic v2 model
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:314`
- **Evidence**: `return self._parsed_config.dict(by_alias=True)` — flagged by the test suite as a `PydanticDeprecatedSince20` warning.
- **Impact**: Will break on a future Pydantic v3 upgrade.
- **Fix**: `return self._parsed_config.model_dump(by_alias=True)`.
- **Linter rule**: Pydantic v2 `.dict()` call — mechanically checkable with ruff/pyright.

### Ruff warnings in vendored charm libraries
- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py:915`, `lib/charms/certificate_transfer_interface/v1/certificate_transfer.py:483`, and 57 others under `lib/`
- **Evidence**: `ruff check lib/` reports 59 errors, mostly `RET505` (unnecessary `else` after `return`), `I001` (unsorted imports), and deprecated Pydantic API usage (e.g. `__fields__` in `lib/charms/tempo_coordinator_k8s/v0/tracing.py:276`). `src/` itself passes clean.
- **Impact**: Vendored, not charm-authored, but shipped as part of the charm and affecting downstream consumers.
- **Fix**: Refresh the vendored libraries from their canonical sources.
- **Linter rule**: already caught by ruff.

## Worth copying

1. **Clean reconciler pattern** (`src/charm.py:218-237`): all reconciliation flows through a single `_reconcile` observed on `config_changed` and `start`; `_remove` is kept separate. Idiomatic ops pattern — one reconciler, explicit sub-reconciler ordering, leader guard at the top.
2. **Telemetry label generation with collision resistance** (`src/charm.py:751-774`): `generate_telemetry_labels` handles the Kubernetes 63-character label limit by truncating and appending an MD5 hash of the full model+app name; mirrored in the dependency (`canonical_service_mesh/utils/_labels.py`). Correct way to keep label uniqueness under length constraints.
3. **Pebble runtime patching for read-only root filesystems** (`src/charm.py:625-664`): `_patch_pebble_runtime` is a reusable pattern for adapting Pebble-based Rock images to workloads enforcing `readOnlyRootFilesystem: true` — adds an emptyDir at `/run/pebble`, sets `PEBBLE`/`PEBBLE_COPY_ONCE`, strips args Pebble would misinterpret as subcommands. Well-commented.
4. **Workload version set via `istioctl version`** (`src/charm.py:325-332`): reports the actually-running control plane version in `juju status`, not the charm's compile-time version.
5. **Terraform module with channel validation** (`terraform/`): standard `juju_application` module with `trust=true` (required for CRD management); README auto-generated with `terraform-docs`.
6. **`CharmConfig` pydantic model** (`src/config.py`): clean separation of config parsing via `Field(alias=...)` for kebab-case keys (aside from the `.dict()` nit above).

## Common-practice notes

- **Layout**: standard `src/` layout (`charm.py`, `config.py`, `istioctl.py`), vendored libraries under `lib/charms/`; matches canonical observability charm conventions.
- **PyPI dependency pattern**: `canonical_service_mesh` centralises shared logic (`KubernetesResourceManager`, models, utils) — the right direction, but the migration is incomplete (see `IngressConfigRequirer` duplication finding).
- **`collect_unit_status`**: used to aggregate statuses, letting the framework pick the worst — the recommended Juju ≥3.6 pattern, though the underlying checks silently swallow errors (see finding above).
- **No `event.defer()` usage**: correct for a full-reconcile-on-every-event charm, but means transient Kubernetes API unavailability surfaces as an error state rather than a retry.
- **`force=True` on control-plane reconcile**: `src/charm.py:362` has `# TODO: A validating webhook raises a conflict if force=False. Why?` — a workaround for a known Istio admission-webhook interaction, not fully understood by the charm authors.
- **`charm-libs` entry plus bundled `lib/` copy**: `certificate_transfer_interface.certificate_transfer` v1 is declared as a `charm-libs` dependency and also bundled in `lib/` — correct for Charmhub publication.
- **Version skew between HEAD and published charm**: `charmcraft.yaml` at HEAD bakes in `istioctl-1.29.0` and Istio 1.29 rocks; the published rev 58 uses Istio 1.26.1 upstream images. HEAD is ahead of what's released.

## Tests

### Unit tests (52 tests, all passing)

Run with `PYTHONPATH=".:lib:src" uv run --frozen --isolated --extra=dev --python 3.12 pytest tests/unit -v`. All 52 pass (~1s). `tox -e lint` and `tox -e static` (pyright) also pass clean on `src/`. Coverage: `charm.py` 68%, `istioctl.py` 95%, `config.py` 100%, overall 75%.

- `test_charm_harness.py`: charm startup and config parsing (2 tests)
- `test_charm.py`: scenario test, charm goes active (1 test)
- `test_ca_cert.py`: JWKS CA cert handling (3 tests)
- `test_extension_providers.py`: tracing/external-authorizer provider config flattening (4 tests)
- `test_istioctl.py`: istioctl wrapper, version parsing, manifest generation, arg building, error handling — bulk of the suite
- `test_status.py`: component readiness → `WaitingStatus`/`Active` (2 tests)
- `test_istio_metadata_*.py`: `istio-metadata` library provider/requirer tests

**Coverage gaps**: `_remove` (lines 301-304, the critical CRD-deletion path), `_patch_pebble_runtime` with real resource objects (640-671), reconcile methods with real-ish resource lists (337-363, all mocked), metrics-proxy Pebble service setup, hardened-mode `AuthorizationPolicy` create/remove lifecycle, config-change handling (the stale-cache path).

### Integration tests

`tests/integration/` uses `pytest-operator` (deprecated in favour of jubilant per open issue #95). Covers: `test_charm.py` (build/deploy, istiod up, ambient mode, CNI reconciliation, Gateway API CRDs, workload version, removal), `test_charm_scaling.py`, `test_authorization_policies.py`. Tests assert real cluster state (DaemonSet/Deployment readiness, ConfigMap values), not just active/idle — good practice.

**Not runnable in this environment**: requires a real Juju controller and microk8s cluster; importing `juju` fails under Python 3.14 due to a protobuf incompatibility unrelated to the charm.

### CI

Reusable workflows from `canonical/observability/.github/workflows/charm-pull-request.yaml@v2` with `provider: microk8s`. Additional workflows: promote, release, quality-gates, tiobe-scan, update-libs.

## Docs

- **README.md**: explains deployment and links related charms (istio-beacon, istio-ingress); could mention hardened-mode and tracing config options.
- **CONTRIBUTING.md**: standard dev workflow (tox, testing, building, updating vendored Gateway API CRDs); badge URLs still reference the old repo name `istio-core-operator`, and the "Lines of Code" badge uses a likely-broken `tokei` service.
- **charmcraft.yaml**: config options well documented with links to upstream Istio docs; `assumes: k8s-api + juju >= 3.6` is correct.
- **terraform/README.md**: auto-generated, covers all inputs/outputs; `main.tf` example is minimal but correct.
- **SECURITY.md**: standard Ubuntu disclosure policy.
- **No `docs/` directory**: narrative docs live at `discourse.charmhub.io/t/istio-k8s-docs-index/20487`, not in-repo.
- **Doc/reality mismatch**: README's `juju deploy istio-k8s --trust` doesn't mention that `--trust` is required specifically for CRD creation, or that cluster-admin-level RBAC is needed.

## Open questions

1. **Does the hardened-mode ztunnel policy with `spec={}` actually deny traffic?** Needs verification against a live workload behind ztunnel; `tests/integration/test_authorization_policies.py:test_hardened_mode` exercises HTTP reachability but not specifically whether ztunnel denies traffic.
2. **How far behind is 2/edge (rev 58) from HEAD?** Rev 58 is on Istio 1.26.1 upstream images and lacks `jwks-ca-cert`; HEAD is on Istio 1.29.0 Canonical rocks with `jwks-ca-cert`, a CNI readiness check, Pydantic v2 fixes, and cert_transfer integration. Behaviour observed on rev 58 may not reflect HEAD.
3. **Is the stale config-caching bug actually reachable in practice?** `hardened-mode=true` worked correctly when tested against the deployed charm, suggesting the cache-invalidation gap in the code either isn't hit on the observed access paths, or the process happens to be re-instantiated between hooks in this environment. Marked `(unverified)` above pending a targeted repro.
4. **How does the charm behave when `istioctl` is missing?** The `charmcraft.yaml` part downloads istioctl to `./istioctl`; a failed download or wrong path would raise `FileNotFoundError` in `Istioctl.__init__`, with no graceful handling observed in the reconciler.
5. **Why does the CNI agent never become ready on microk8s?** Logs `no networks found in /host/etc/cni/net.d` on both Istio versions tested, even with correct `cniBinDir`/`cniConfDir`. Likely a microk8s CNI-chaining compatibility issue rather than a charm bug — the charm at HEAD (rev 71) detects and reports it correctly.
6. **Does rev 71 properly handle the `certificate_transfer` relation for `jwks-ca-cert`?** Could not be fully tested — relating to `self-signed-certificates:send-ca-cert` requires a compatible base/charm pairing not exercised here.
