# istio-ingress-k8s

A well-crafted, feature-rich Istio ingress gateway charm that delegates most real logic to
the `canonical_service_mesh` PyPI package and `charmlibs-interfaces-*` libraries, keeping the
charm itself as a clean orchestrator that normalises relation data into K8s Gateway API
resources. Deployment works but **requires `--trust`**, which is undocumented (confirmed by
open issue #34) — without it the charm enters an infinite 403-retry loop and never reaches
`BlockedStatus`. TLS, scaling, route deduplication, hostname validation, and auth integration
all behave as designed. Beyond the `--trust` gap, the sharpest problems are: `ready-timeout=0`
silently bricks the charm with a misleading status message, an empty
`external-traffic-policy-cidrs` silently deploys a deny-all AuthorizationPolicy, scaling to 0
blocks the event loop for up to 200s, and a dependency-level 404-handling bug
(`KubernetesResourceManager.get_deployed_resources()`) is dead code that can crash hooks. A
maintainer should first fix the `--trust` documentation/detection and the two silent
misconfiguration traps (`ready-timeout=0`, empty CIDR list) — these are the ones most likely to
put an operator into an unrecoverable or dangerous state without any indication something is
wrong.

| | |
|---|---|
| Repo | canonical/istio-ingress-k8s-operator @ `a9ef964` (2026-06-10) |
| Charms | istio-ingress-k8s (primary), tester-grpc, tester-http, tester-mock-oauth2 (test helpers) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5), 2/edge rev 61; also concierge-k8s-3 (Juju 3.6), 2/edge rev 61 |
| Reviewed | 2026-08-04 |

## What it does

Deploys an Istio ingress gateway on Kubernetes. Creates a K8s Gateway resource (Gateway API),
manages TLS certificates via a `certificates` relation, synchronises HTTPRoutes and GRPCRoutes
from two relation systems (the older `ingress`/`ingress-unauthenticated` IPA interface and the
newer `istio-ingress-route`/`istio-ingress-route-unauthenticated` interface), handles external
authorisation via `forward-auth` and `istio-ingress-config`, supports JWT-based
`istio-request-auth`, publishes gateway metadata to downstream charms, exposes a
metrics-proxy sidecar, and can itself be ingressed through `upstream-ingress`. Uses
HorizontalPodAutoscalers pinned to unit count for scaling the gateway workload.

## Deployment log

### Juju 4.0.5 (concierge-k8s-4)

```bash
juju add-model rv-ingress2
juju deploy istio-k8s --channel 2/edge --trust
# → active after ~50s

# FIRST ATTEMPT (no --trust):
juju deploy istio-ingress-k8s --channel 2/edge
# → INFINITE ERROR LOOP: "leader-elected" hook fails with 403 Forbidden
#   "User system:serviceaccount:rv-ingress-deep:istio-ingress-k8s cannot list
#   resource authorizationpolicies in API group security.istio.io at the cluster scope"
#   ClusterRole created by Juju only has namespace get/list — no Istio CRD access.
#   Charm never reaches BlockedStatus, never gives a human-readable message.
#   Destroyed model, created fresh.

# SECOND ATTEMPT (with --trust):
juju deploy istio-ingress-k8s --channel 2/edge --trust
# → maintenance "Validating gateway readiness" → active "Serving at 10.43.45.0"
#   Deployment time: ~20s from deploy to active.

juju relate istio-ingress-k8s istio-k8s
# → brief maintenance then active. Relation is truly optional — charm works without it.

juju deploy self-signed-certificates --channel latest/edge
juju relate istio-ingress-k8s:certificates self-signed-certificates
# → Gateway gained https-443 listener with TLS secret
#   (istio-ingress-k8s-tls-certificate: tls.crt + tls.key).

juju config istio-ingress-k8s external_hostname="test.example.com"
# → active, "Serving at test.example.com"

juju config istio-ingress-k8s external_hostname="INVALID HOSTNAME!@#"
# → blocked, "Invalid hostname provided, Please ensure this adheres to RFC 1123."
#   Correctly blocked with actionable message.

juju config istio-ingress-k8s external_hostname=""
# → active, "Serving at 10.43.45.0" — recovers cleanly.

juju config istio-ingress-k8s external-traffic-policy-cidrs="10.0.0.0/8"
# → AuthorizationPolicy updated, ipBlocks: ["10.0.0.0/8"]

juju config istio-ingress-k8s external-traffic-policy-cidrs="not-a-cidr"
# → ACCEPTED with no validation error. Charm stays active.
#   AuthorizationPolicy ipBlocks is ["not-a-cidr"]. Invalid CIDR silently deployed.

juju config istio-ingress-k8s external-traffic-policy-cidrs=""
# → ACCEPTED. Charm stays active. AuthorizationPolicy has EMPTY ipBlocks [].
#   This is a DENY-ALL policy — all external traffic is blocked.
#   Charm does not detect or warn about this.

juju config istio-ingress-k8s ready-timeout=0
# → ACCEPTED. Charm goes to blocked: "Gateway k8s deployment not ready".
#   ready-timeout // 10 = 0 iterations → always returns False.
#   Gateway is actually healthy; message is misleading.

juju config istio-ingress-k8s ready-timeout=100
# → Recovers to active. Confirms the zero-timeout was the cause.

juju remove-relation istio-ingress-k8s:certificates self-signed-certificates
# → Gateway https-443 listener removed, TLS secret deleted. Charm stays active.

juju remove-relation istio-ingress-k8s:istio-ingress-config istio-k8s:istio-ingress-config
# → Charm stays active. Relation removal handled cleanly.

juju scale-application istio-ingress-k8s 3
# → HPA minReplicas/maxReplicas → 3, deployment scaled to 3.
#   Non-leader units: "Backup unit; standing by for leader takeover"
juju scale-application istio-ingress-k8s 1
# → Clean scale-down, HPA back to 1.

kubectl delete pod <istio-ingress-k8s-istio-*>
# → Deployment recreates pod within seconds. Charm stays active.

juju refresh istio-ingress-k8s --channel dev/edge
# → FAILED: "one or more of the provided endpoints ... do not exist"
#   dev/edge rev 82 has new endpoints (gateway-metadata, istio-ingress-route, etc.)
#   not present in rev 61. Cross-track refresh not supported.

echo "rv-ingress2" | juju destroy-model rv-ingress2 --force --no-wait --destroy-storage
# → Takes ~45s (model operators take time to terminate).
```

### Juju 3.6 (concierge-k8s-3)

```bash
juju add-model rv-ingress-juju3
juju deploy istio-k8s --channel 2/edge --trust
juju deploy istio-ingress-k8s --channel 2/edge --trust
# → active "Serving at 10.43.45.1" in ~25s. No RBAC retry issues with --trust.
#   Invalid hostname → blocked, then reset → recovers. Behaviour identical to 4.0.5.
```

### Deepened testing (concierge-k8s-4, model rv-ingress-deep2)

```bash
juju add-model rv-ingress-deep2
juju deploy istio-k8s --channel 2/edge --trust   # active after ~50s
juju deploy istio-ingress-k8s --channel 2/edge --trust  # active after ~20s

# Note: even with --trust, leader-elected hook failed once with 403 before
# retrying and succeeding. Charm recovered without operator intervention.

# Same-track refresh: all 2/* channels point to rev 61 — no refresh possible.
# Same-track upgrades are untestable until a new revision is published.

kubectl delete pod istio-ingress-k8s-istio-<id>
# → Deployment recreates pod in ~16s, charm stays active.

kubectl exec istio-ingress-k8s-0 -c charm -- kill 1
# → Pod restarts (RESTARTS: 0→2), both containers come back.
#   Charm recovers to active "Serving at test.example.com" within ~20s.

kubectl exec istio-ingress-k8s-0 -c metrics-proxy -- pebble stop metrics-proxy
# → Pebble auto-restarts the service (startup=enabled). Charm does not detect or
#   report the transient failure; status stays active throughout.

kubectl delete gateway istio-ingress-k8s -n rv-ingress-deep2
# → Charm stays active on stale status. Gateway is NOT recreated until next event.
#   Triggering a juju config change forces reconciliation → Gateway recreated in <10s.
#   No update-status handler means no periodic self-healing.

kubectl delete authorizationpolicy istio-ingress-k8s-...-external-traffic
# → Same: not healed until next config/relation event.

juju scale-application istio-ingress-k8s 0
# → maintenance "Validating gateway readiness" — BLOCKS for 200s (ready-timeout × 2).
#   _is_deployment_ready() loops 100s trying to find the (now-deleted) deployment.
#   _is_load_balancer_ready() then loops 100s checking the Service for LB ingress.
#   After blocking, the remove hook finally fires and cleans up resources.
#   Application → 0 units, status unknown. Two Services leaked (Juju infra, not charm).

juju scale-application istio-ingress-k8s 1
# → Active "Serving at test.example.com" in ~25s. Full recovery.

juju remove-relation istio-ingress-k8s:istio-ingress-config istio-k8s
# → Brief maintenance "Validating gateway readiness", then active. Clean.
```

## Observed behaviour

- **`--trust` is mandatory but undocumented**: Without `--trust`, Juju creates a minimal ClusterRole with only namespace get/list. The service account cannot list Istio CRDs (AuthorizationPolicies, Gateways, etc.) and the charm enters an infinite retry loop on `leader-elected` with 403 Forbidden. It never reaches `BlockedStatus` with a clear message. README does not mention `--trust`; the terraform module hardcodes `trust = true` (`terraform/main.tf`).
- **Deployment time (with --trust)**: ~20s to active on both Juju 3.6 and 4.0.5. No RBAC propagation delay needed when trusted.
- **No actions defined**: `juju actions istio-ingress-k8s` returns nothing. Operators cannot trigger cert refresh, show-proxied-endpoints, or any diagnostic action.
- **`ready-timeout=0` silently bricks the charm**: Zero or negative values are accepted with no validation. `_is_deployment_ready()` and `_is_load_balancer_ready()` compute `attempts = timeout // 10` — zero iterations if timeout < 10 — and return False. Status message is misleading: "Gateway k8s deployment not ready, is istio properly installed?" when the gateway is actually healthy.
- **Empty `external-traffic-policy-cidrs` creates a deny-all**: The config accepts an empty string, which `_sync_external_traffic_auth_policy` splits and filters to an empty `ipBlocks` list `[]`. An Istio AuthorizationPolicy with empty ipBlocks blocks ALL traffic. The charm reports active with no warning. Invalid CIDRs like `"not-a-cidr"` are similarly silently deployed.
- **`_sync_all_resources` is called from every hook handler** (config-changed, start, peers-changed, relation-changed, etc.). It re-derives all routes, listeners, auth policies, gateway resources, ingress resources, and certificates from scratch every invocation, with no early-exit for unchanged inputs. On a trivial config change, 9 K8s API GET calls and 3 PATCH calls were observed, all for unchanged resources.
- **`_is_load_balancer_ready()` blocks the event loop**: Uses `time.sleep(10)` in a polling loop for up to `ready-timeout` seconds, blocking the unit agent from processing other events.
- **Cross-track `juju refresh` fails**: Refreshing from 2/edge (rev 61) to dev/edge (rev 82) fails because the charm metadata endpoints changed between tracks. The error message names the missing endpoints but does not suggest a resolution.
- **`_on_remove` does not clean up gRPC DestinationRules**: `_get_grpc_destination_rule_resource_manager()` is called during sync but its `.delete()` is never called in `_on_remove`. GRPCRoutes themselves are cleaned up via the ingress route resource manager, but associated DestinationRules in backend namespaces are leaked.
- **Juju 3.6 vs 4.0.5**: No observable behavioural differences. Both require `--trust`, both reach active in similar time, config validation behaves identically.
- **Scale to 0 blocks for up to 200s**: Scaling to 0 removes the deployment and HPA, but `_is_ready()` still tries to verify deployment readiness. `_is_deployment_ready()` loops for `ready-timeout` (100s) getting `ApiError` (404) every iteration. `_is_load_balancer_ready()` then loops another 100s checking `Service.status.loadBalancer.ingress`, which is `None` for the ClusterIP service. Total up to 200s of blocked event processing, until the remove hook fires and cleans up. Recovers fully on scale-back-up to 1.
- **No update-status observer → no periodic self-healing**: The charm observes `config-changed`, `start`, `remove`, `peers-changed`, relation events, and `pebble-ready`, but not `update-status`. External changes (kubectl-deleted Gateway, AuthorizationPolicy) persist until the next config/relation event — a deleted Gateway sat unreconciled until `juju config` was manually triggered. A deliberate design choice, but it means the charm does not self-heal from drift.
- **Metrics-proxy pebble monitoring is passive**: The charm sets up the metrics-proxy pebble layer on `pebble-ready` and during sync, but does not observe `pebble-check-recovered` or `pebble-notice`. If the process dies, pebble auto-restarts it (startup=enabled), but the charm never notices.
- **Charm pod restart recovery**: Killing PID 1 in the charm container restarts the pod; charm recovers to active within ~20s.
- **Gateway workload pod recovery**: The istio workload pod (managed by Deployment, not the charm) is recreated by the Deployment controller in ~16s after deletion; the charm does not notice or react to this transient outage.
- **Only 3 config options**: `external_hostname`, `ready-timeout`, `external-traffic-policy-cidrs`. No `additional-hostnames`, `labels` override, `enable-metrics` toggle, or `log-level`. Minimal surface compared to traefik-k8s or istio-beacon-k8s — partly by design since much config comes from relations, but limits standalone usability.
- **No upgrade-charm handler**: Upgrades rely on the standard Juju hook sequence and existing event handlers firing in order.

## Findings

### `--trust` required but undocumented; missing it causes infinite error loop
- **Severity**: critical
- **Kind**: bug
- **Where**: `charmcraft.yaml` (missing `kubernetes` RBAC section), `README.md` (no `--trust` mention)
- **Evidence**: Deploying without `--trust` on Juju 4.0.5 produces a `ClusterRole` with only `namespaces: [get, list]`. The charm hits 403 Forbidden on `authorizationpolicies.security.istio.io` and retries forever, never reaching `BlockedStatus`. `terraform/main.tf` hardcodes `trust = true`, confirming the charm knows it needs this.
- **Impact**: A new operator following the README will deploy without `--trust`, hit an infinite error loop with no indication what's wrong, and likely abandon the charm.
- **Fix**: Add a `kubernetes` section to `charmcraft.yaml` declaring the needed RBAC, or document `--trust` prominently in README, or catch the 403 in `_sync_all_resources` and set `BlockedStatus` with an actionable message ("Deploy with --trust ...").
- **Linter rule**: mechanically checkable — flag k8s charms with no `kubernetes` section in `charmcraft.yaml` that use `lightkube` to manage cluster-scoped resources.

### `ready-timeout=0` (or negative) silently bricks the charm
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:543-554`, `src/charm.py:568-582`
- **Evidence**:
  ```python
  timeout = int(self.config["ready-timeout"])
  attempts = timeout // check_interval  # 0 // 10 = 0
  for _ in range(attempts):  # zero iterations → always returns False
  ```
  Observed: `juju config istio-ingress-k8s ready-timeout=0` → blocked with "Gateway k8s deployment not ready" despite gateway being healthy. `ready-timeout=-1` has the same effect.
- **Impact**: An operator experimenting with timeouts can brick the charm with a single config value, and the status message incorrectly blames the istio installation.
- **Fix**: Add a `min: 10` constraint on `ready-timeout` in `charmcraft.yaml`, or validate at runtime with `max(1, timeout // check_interval)`.
- **Linter rule**: mechanically checkable — flag `range(timeout // N)` patterns without a `max(1, ...)` guard.

### Empty `external-traffic-policy-cidrs` creates a deny-all AuthorizationPolicy
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:1349-1356`
- **Evidence**:
  ```python
  cidrs_config = cast(str, self.config["external-traffic-policy-cidrs"])
  ip_blocks = [cidr.strip() for cidr in cidrs_config.split(",") if cidr.strip()]
  # empty cidrs_config → ip_blocks = [] → empty ipBlocks means "deny all" in Istio
  ```
  Observed: setting config to `""` produced an AuthorizationPolicy with `ipBlocks: []`; charm reported active.
- **Impact**: Silent denial-of-service — all external traffic to the gateway is blocked with no operator-visible indication.
- **Fix**: If `ip_blocks` is empty, either default to `["0.0.0.0/0"]` (matching the default config value) or set `BlockedStatus`. Also validate each CIDR before patching.
- **Linter rule**: not mechanically checkable.

### `KubernetesResourceManager.get_deployed_resources()` 404-handling is dead code
- **Severity**: high
- **Kind**: bug
- **Where**: `deps/canonical_service_mesh/k8s/resource_manager/_resource_manager.py:185-189`
- **Evidence**:
  ```python
  except ApiError as error:
      if error.status.code == 404:
          self.log.debug(f"resource type {resource_type} not found in cluster. Ignoring this type.")
      raise error  # ← always executed; 404 branch is dead code
  ```
  Ships as dependency `canonical-service-mesh`; the same pattern exists in the old `lightkube_extensions` package used by deployed rev 61.
- **Impact**: Any 404 from listing a resource type (e.g. CRD not yet installed) crashes the charm instead of being silently skipped; the log message is misleading since the error is re-raised regardless.
- **Fix**: Move `raise error` inside an `else:` block, or restructure to only re-raise non-404 errors.
- **Linter rule**: mechanically checkable — flag bare `raise` inside an `except` that follows a conditional check on the exception status code.

### `PolicyResourceManager.delete()` catches wrong exception type for 404
- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/canonical_service_mesh/k8s/resource_manager/_resource_manager.py:424-436`
- **Evidence**:
  ```python
  def delete(self, ignore_missing=True):
      try:
          self._krm.delete(ignore_missing=ignore_missing)
      except httpx.HTTPStatusError as e:  # ← catches httpx error
          if e.response.status_code == 404 and ignore_missing:
              ...
  ```
  `get_deployed_resources()` raises `lightkube.ApiError` (not `httpx.HTTPStatusError`); the `_k8s_api_call` decorator only catches `httpx.TransportError`. So when `_krm.delete()` hits a 404 via `get_deployed_resources()`, the `ApiError` propagates past this handler uncaught.
- **Impact**: If a CRD is not installed, `PolicyResourceManager.delete()` does not gracefully skip the 404 — it raises `ApiError` and crashes the hook.
- **Fix**: Also catch `ApiError`, or fix the root cause in `get_deployed_resources()`.
- **Linter rule**: mechanically checkable — flag `except` clauses that catch a specific exception type when the call chain can raise a different type.

### Scale-to-0 blocks the event loop for up to 200s before the remove hook fires
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:542-605`
- **Evidence**: `juju scale-application istio-ingress-k8s 0` → maintenance "Validating gateway readiness". The deployment is deleted (HPA minReplicas=0), so `_check_deployment_ready()` catches `ApiError` (404) and returns False. `_is_deployment_ready()` loops for `ready-timeout` (100s) doing nothing useful, then `_is_load_balancer_ready()` loops another 100s because the Service has no `loadBalancer.ingress`. Only after 200s does the remove hook fire (killing the stuck config-changed hook). Confirmed by open issue #70.
- **Impact**: Scale-to-0 is a common lifecycle operation (maintenance, cost saving); blocking the event loop for minutes is operator-visible and unnecessary since the deployment was already removed.
- **Fix**: In `_is_ready()`, if `self.model.app.planned_units() == 0`, return True immediately. The `unit_count < 1` guard already present at `src/charm.py:1372` should cover the `_is_ready()` call too.
- **Linter rule**: not mechanically checkable — requires understanding of scale-to-0 semantics.

### No update-status handler → no periodic self-healing from external drift
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:250-303` (framework observers)
- **Evidence**: The charm observes config-changed, start, remove, peers-changed, relation events, and pebble-ready, but not `update-status`. Deleting the Gateway resource via `kubectl` left the charm reporting active "Serving at..." with no Gateway present; it was only recreated when `juju config` was manually triggered.
- **Impact**: If a controller or operator modifies/deletes charm-managed resources outside Juju, the charm will not self-heal until the next config/relation event — which could be hours or never.
- **Fix**: Add `self.framework.observe(self.on.update_status, self._on_update_status)` calling `_sync_all_resources()`.
- **Linter rule**: mechanically checkable — flag k8s charms that manage resources via `lightkube` but do not observe `update-status`.

### No Juju actions defined
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py` — no `@action` decorators, `charmcraft.yaml` has no `actions` section
- **Evidence**: `juju actions istio-ingress-k8s` returns "No actions defined for istio-ingress-k8s."
- **Impact**: Operators have no programmatic way to trigger a cert refresh, dump the route table, show proxied endpoints, or force reconciliation. Open issue #108 explicitly requests `show-proxied-endpoints`.
- **Fix**: Add at minimum `show-proxied-endpoints` and `force-reconcile` actions.
- **Linter rule**: not mechanically checkable.

### Deprecated `cert_handler` v1 library in use, past its own deprecation deadline
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/observability_libs/v1/cert_handler.py`, used at `src/charm.py:305`
- **Evidence**: The library warns `DeprecationWarning: The cert_handler library is deprecated and will be removed in October 2025.` Open issue #158 tracks migration to `tls_certificates_interface` v4. Observed 226 times in unit test warnings.
- **Impact**: The stated removal deadline (October 2025) has passed as of this review (2026-08-04); the library has not actually been removed yet, but the charm is depending on undefined future availability.
- **Fix**: Migrate to `tls_certificates_interface` v4 per #158.
- **Linter rule**: mechanically checkable — `charmcraft analyse` could flag deprecated library versions and warn when the stated deprecation deadline has passed.

### `_sync_all_resources` does full reconciliation on every hook with no early-exit
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:948`
- **Evidence**: Every event handler (config-changed, start, peers-changed, ingress-data-provided, etc.) calls `_sync_all_resources()`, which re-derives all routes, listeners, auth policies, gateway resources, ingress resources, and certificates from scratch even when nothing changed. 9 K8s API GET calls + 3 PATCH calls were observed for a trivial config change.
- **Impact**: At scale with many ingressed apps this becomes expensive. `KubernetesResourceManager.reconcile()` already has a diff mechanism, but the charm rebuilds the desired state from scratch regardless.
- **Fix**: Cache the last known state hash and compare before full reconciliation, or use a dirty-flag pattern per subsystem.
- **Linter rule**: not mechanically checkable.

### `_on_remove` does not clean up gRPC DestinationRules
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:498-520` vs `src/charm.py:1601-1602`
- **Evidence**: `_on_remove()` calls `.delete()` on ingress routes, gateway resources, ingress authz, ext authz, external traffic, request auth, and deny auth — but not on the gRPC DestinationRule resource manager created at `_get_grpc_destination_rule_resource_manager` (line 414-415) and used during sync at line 1601-1602. 7 of 8 sync-time resource managers are cleaned up in `_on_remove`; the 8th (grpc DestinationRule) is not.
- **Impact**: Scaling to 0 or removing the application can leave stale DestinationRules in backend namespaces, which persist after the charm is gone since they live outside the charm's own namespace.
- **Fix**: Add `self._get_grpc_destination_rule_resource_manager().delete()` to `_on_remove()`.
- **Linter rule**: mechanically checkable — a linter could check every `_get_*_resource_manager()` call-site used during sync has a corresponding `.delete()` in `_on_remove`.

### `_is_load_balancer_ready()` and `_is_deployment_ready()` block the event loop
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:543-554`, `src/charm.py:568-582`
- **Evidence**: Both methods use `time.sleep(10)` in polling loops that can run for up to `ready-timeout` (default 100) seconds; `_is_ready()` (line 604-605) calls both, so it can block for up to 200 seconds. Called from `_sync_all_resources()` (line 1032), which is called from every hook handler.
- **Impact**: The Juju unit agent is single-threaded; blocking for up to 200s prevents processing of other events.
- **Fix**: `_collect_readiness_status()` already uses the non-blocking single checks (`_check_deployment_ready()`, `_get_lb_external_address`). `_sync_all_resources` should use those and rely on future hook retries (deferred events or update-status) rather than blocking.
- **Linter rule**: mechanically checkable — flag `time.sleep()` calls inside hook handlers (not in actions or tests).

### `tox.ini` static check for library version bumps is broken
- **Severity**: low
- **Kind**: lint
- **Where**: `tox.ini:55`
- **Evidence**: `[testenv:static]` includes a shell command that diffs `$lib_path` files for LIBPATCH/LIBAPI bumps, but `lib_path` is commented out (`;lib_path = {tox_root}/lib/charms/operator_name_with_underscores`). `git diff main --name-only {[vars]lib_path}` expands to an empty path, so no files are ever checked.
- **Impact**: The CI gate meant to catch missing library version bumps is a no-op; library version drift can go unnoticed.
- **Fix**: Uncomment and correct `lib_path`, or remove the dead check.
- **Linter rule**: mechanically checkable — flag tox.ini variables that are commented out but still referenced.

### Cross-track `juju refresh` fails with endpoint mismatch
- **Severity**: low
- **Kind**: ux
- **Where**: `charmcraft.yaml` (endpoint list differs between tracks)
- **Evidence**: `juju refresh istio-ingress-k8s --channel dev/edge` (from 2/edge rev 61) fails: "one or more of the provided endpoints 'certificates, charm-tracing, forward-auth, gateway-metadata, ingress, ...' do not exist." dev/edge rev 82 adds gateway-metadata, istio-ingress-route, istio-request-auth, upstream-ingress, and juju-info.
- **Impact**: Operators on 2/edge cannot upgrade to the dev track without removing the application first.
- **Fix**: Document the cross-track upgrade procedure (remove-application with preserved storage/config, re-deploy).
- **Linter rule**: not mechanically checkable.

### CONTRIBUTING.md references non-existent `scenario` tox environment
- **Severity**: low
- **Kind**: docs
- **Where**: `CONTRIBUTING.md:15-17`
- **Evidence**: CONTRIBUTING.md lists `tox run -e scenario` and says `tox` runs `lint, static, unit, and scenario`, but `tox.ini` has `env_list = lint, static, unit` and no `[testenv:scenario]` section.
- **Impact**: New contributors following the docs will hit a tox error. The project already has `ops-scenario` in dev deps but hasn't migrated tests off `Harness`.
- **Fix**: Remove the scenario references from CONTRIBUTING.md, or add `[testenv:scenario]` and migrate tests.
- **Linter rule**: not established.

### Tests use deprecated `ops.testing.Harness`
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:46`, `tests/unit/test_ingress_config.py:35`, `tests/unit/test_upstream_ingress.py:17`
- **Evidence**: `PendingDeprecationWarning: Harness is deprecated.` The project has `ops-scenario` in dev dependencies but doesn't use it.
- **Impact**: The Harness API will be removed in a future ops release.
- **Fix**: Migrate unit tests to `scenario`.
- **Linter rule**: mechanically checkable — detect `Harness` imports in test files.

### Comment typos
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:1004` ("doesnt"), `src/charm.py:1596` ("wll"), `src/charm.py:1598` ("cant")
- **Evidence**: `codespell` detected three spelling errors.
- **Impact**: cosmetic only.
- **Fix**: Correct to "doesn't", "will", "can't".
- **Linter rule**: mechanically checkable with `codespell`.

### `requires-python = "~=3.10"` is ambiguous in pyproject.toml
- **Severity**: nit
- **Kind**: lint
- **Where**: `pyproject.toml` (`requires-python`)
- **Evidence**: `uv` warns: "The `requires-python` specifier (`~=3.10`) ... uses the tilde specifier without a patch version. This will be interpreted as `>=3.10, <4`. Did you mean `~=3.10.0`?"
- **Impact**: Low-risk given CI pins Python 3.12, but the specifier could accidentally allow Python 4.x in the future.
- **Fix**: Change to `>=3.10,<4` (if intentional) or `~=3.10.0` (if meant to cap at 3.11).
- **Linter rule**: mechanically checkable — `uv lock` already warns.

### `__pycache__` directory checked into git
- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/oauth2_proxy_k8s/v0/__pycache__/forward_auth.cpython-312.pyc`
- **Evidence**: A compiled `.pyc` bytecode file is tracked in the repository.
- **Impact**: Can cause spurious diffs across Python versions; minor hygiene issue.
- **Fix**: Add `__pycache__/` to `.gitignore` and `git rm --cached` the file.
- **Linter rule**: mechanically checkable — flag `.pyc` files in a git-tracked repository.

## Worth copying

- **`CollectStatusEvent` pattern with sub-collectors**: `src/charm.py:1080-1093`. `_on_collect_status` calls a sequence of `_collect_*` methods that each add status to the event — clean, testable, avoids monolithic status logic. The non-leader path is a single-line delegation.
- **Normalised intermediate data layer**: `src/utils.py`. Route data from the two relation interfaces (IPA and istio-ingress-route) is normalised into common TypedDict structures (`HTTPRoute`, `GRPCRoute`, `GatewayListener`) before deduplication and K8s resource construction, cleanly separating relation parsing from resource construction.
- **Fail-closed auth**: `src/charm.py:897-950`. When `istio-request-auth` is active, the charm creates a DENY AuthorizationPolicy that blocks any request without a validated JWT principal. Malformed apps are logged but don't leave the gateway open; combined with `forward-auth`, the DENY policy is scoped to Bearer-token requests only so ext-authz continues to work.
- **`_ingress_url` caching**: `src/charm.py:1624-1658`. Caches the first resolved value to prevent flapping between address sources (LB IP, upstream ingress, config) during a single charm execution — important for CSR/SAN consistency.
- **`GatewayMetadata` provider**: `deps/charmlibs/interfaces/gateway_metadata/_gateway_metadata.py`. Small, focused interface publishing namespace, gateway name, deployment name, and service account to downstream charms, with a Pydantic model, proper leader guard, and typed interface.
- **Resource manager labelset pattern**: `deps/canonical_service_mesh/k8s/resource_manager/_resource_manager.py:208-216`. `create_charm_default_labels()` gives consistent label selectors for all managed resources, making cleanup and reconciliation predictable. `PolicyResourceManager` wraps `KubernetesResourceManager` with mesh-type-specific builders — a clean layering.

## Common-practice notes

- **`charmcraft.yaml` as single source of truth**: correctly done, no separate `metadata.yaml`.
- **Single-file charm with one large `src/charm.py`**: at 76KB / >1700 lines it's large but comprehensible; `utils.py` (35KB) extracts normalisation logic. Approaching the threshold where splitting by subsystem (gateway, auth, ingress) would help.
- **Dependency-heavy architecture**: most logic lives in PyPI packages (`canonical-service-mesh`, `charmlibs-interfaces-*`), a deliberate choice for code reuse across the istio-beacon/istio-ingress family — means `deps/` is primary code, not just `repo/`.
- **Tox-based test setup**: standard for Canonical charms, uses `uv` (ahead of many charms still on pip), `--frozen --isolated` flags are good practice. Python 3.14 incompatibility with `grpcio-tools` is a near-term risk (unverified beyond noted dependency).
- **Terraform module included**: `terraform/main.tf` is simple and correct, with `trust = true` hardcoded.
- **No `justfile` or `spread.yaml`**: tox handles test orchestration only; no spread tests for destructive/system-level testing. Integration tests run via `pytest-jubilant`, the modern replacement for `pytest-operator`.

## Tests

**Unit tests**: 114 tests passing across 10 files, run in 4.4s (`uv run pytest tests/unit/ -v`).

Cover: gateway construction with/without TLS and hostnames (`test_gateway.py`); ingress route construction, auth policies, route publishing (`test_ingress.py`); auth policy construction for ext-authz, request-auth, external traffic (`test_auth.py`); route deduplication edge cases (`test_utils_deduplication.py`); data normalisation for IPA and istio-ingress-route (`test_utils_normalization.py`); JWT rule conversion, RA sync, DENY policy with/without forward-auth (`test_request_auth.py`); upstream ingress URL cascading (`test_upstream_ingress.py`); ingress config provider (`test_ingress_config.py`).

**Coverage (src/charm.py: 84%)**. Untested areas:
- `_on_remove` handler (lines 498-520): 0% on resource cleanup path
- `_is_deployment_ready` / `_check_deployment_ready` (lines 543-567): retry loop untested
- `_is_load_balancer_ready` (lines 568-582): blocking loop untested
- `_get_lb_external_address` error paths (lines 590-600): `ApiError` branches untested
- `_sync_all_resources` readiness guard (line 1032-1033): `not self._is_ready()` branch untested
- `BlockedStatus` paths in `_collect_readiness_status` (lines 1145-1149)
- gRPC destination rule construction/cleanup (lines 1527, 1587, 1601-1602)
- `_get_grpc_destination_rule_resource_manager` (lines 414-415)

**Integration tests**: 7 files in `tests/integration/`, using `pytest-jubilant`, deploying real charms (istio-k8s, self-signed-certificates, tester charms). Verify IPA ingress routing with/without TLS (`test_charm_ipa.py`), multi-port/multi-protocol istio-ingress-route (`test_charm_istio_ingress_route.py`), forward auth with oauth2-proxy (`test_charm_auth.py`), request auth with JWT (`test_charm_request_auth.py`), gateway metadata publishing (`test_gateway_metadata.py`), upstream ingress cascading (`test_upstream_ingress.py`), and scaling with HPA min/max assertions (`test_charm_scaling.py`).

Could not run integration tests locally — they require a separate istio-k8s model and significant cluster resources (`istio_core_juju` fixture deploys istio-k8s in a dedicated model). Tester charms are built on the fly (`pytest_jubilant.pack()`); a pre-built `tester-http_ubuntu@24.04-amd64.charm` exists but cannot be deployed directly because it references an OCI image resource unavailable in this environment.

Collected `tests/integration/test_charm_scaling.py --collect-only`: 4 test functions (`test_deploy_dependencies`, `test_deployment`, `test_gateway_scaling[3]`, `test_gateway_scaling[2]`). The scaling test asserts `hpa.spec.minReplicas == n_units` and `hpa.spec.maxReplicas == n_units` — real assertions beyond active/idle. `test_charm_auth.py` verifies AuthorizationPolicy spec, ConfigMap data, and listener conditions. `test_charm_ipa.py` verifies HTTP reachability through the gateway with and without TLS.

**Static analysis**: `ruff check src/ tests/` passes clean. `pyright src/` — 0 errors/warnings/informations. `codespell src/ tests/` — 3 comment typos (reported above).

## Docs

- **README**: brief but functional; describes what the charm does and links to Charmhub discourse. The "Usage" section is `**todo**` — a significant gap for new operators.
- **CONTRIBUTING.md**: references non-existent `tox -e scenario` environment.
- **Terraform README**: auto-generated terraform-docs output, clean and complete.
- **Charmhub description**: present but minimal, just repeats the summary; no relation/config details.
- **Code docstrings**: generally good — `_sync_all_resources` has a detailed 13-step flow list; normalisation functions have extensive docstrings with examples.
- **Doc/reality mismatches**:
  - CONTRIBUTING.md's `tox -e scenario` does not exist in `tox.ini`.
  - `--trust` is mandatory but mentioned nowhere in README or charmhub description.
  - `ready-timeout` description says the charm will go into blocked state if the deployment doesn't become ready, but does not warn that setting it too low (including 0) causes a permanent block regardless of actual readiness.

## Open questions

- **Issue #187 (BYO istio)**: should the charm support running without an istio-k8s relation, letting operators use an external istio instance? Currently no mechanism to skip Gateway resource creation if istio already manages gateways.
- **Issue #17 (stuck LB)**: if the LoadBalancer never gets an IP, the charm stays in maintenance forever during `_sync_all_resources` because `_is_load_balancer_ready()` blocks. Related to issue #70 (model destroy hangs).
- **HPA vs Deployment direct control**: the charm uses HPA with min=max=unitCount rather than setting `deployment.spec.replicas` directly (deliberate per issue #62), adding indirection and HPA overhead. Open issue asks whether HPA is meant to actually autoscale eventually.
- **Why is `istio-ingress-config` truly optional?**: deployed and tested without the relation — the charm works standalone. The relation carries auth configuration (ext-authz); if unconfigured, the charm functions independently. Is standalone use intentional?
- **Why does leader-elected sometimes fail even with --trust?**: observed on both initial deployment and the deepened test — the first `leader-elected` hook fails with 403, then succeeds on retry. Suggests a race between Juju's ClusterRole binding propagation and the charm's first `lightkube` call. Juju's retry mechanism handles it, but the transient error in debug-log could alarm operators.
