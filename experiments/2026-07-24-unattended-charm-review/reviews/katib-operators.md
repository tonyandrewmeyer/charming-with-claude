# katib-operators

Three k8s charms (`katib-controller`, `katib-db-manager`, `katib-ui`) wrapping the
upstream Kubeflow Katib AutoML project. `katib-controller` manages CRDs, webhooks and
the Katib controller workload via a sidecar container; `katib-db-manager` bridges Katib
to MySQL; `katib-ui` provides the web UI. The charms use a clean, componentised
architecture (`charmed_kubeflow_chisme` `CharmReconciler`), but there are correctness
bugs serious enough to make the controller unsuitable for autoscaling or upgrade paths
that scale to zero, a status-reporting bug that can mask a broken pebble layer as
healthy, and an orphaned cluster-admin-equivalent ClusterRole that survives charm
removal. A maintainer should fix the scale-to-zero ServiceAccount deletion (#379) and
the `parse_images_config` return-type bug first — both are live, reproduced, and
block normal operational workflows (scaling, config recovery). The orphaned
`*/*:*/*` ClusterRole is the most severe finding from a security standpoint and needs
investigation into whether it is a charm or Juju substrate defect.

| | |
|---|---|
| Repo | canonical/katib-operators @ `9b3e1d1` (2026-06-19) |
| Charms | katib-controller, katib-db-manager, katib-ui |
| Substrate | k8s |
| Deployed | yes — deployed and exercised across four Juju models (rv-katib on Juju 4.0/concierge-k8s-4, rv-katib-lxd and rv-katib3 on Juju 3.6/concierge-k8s-3, rv-katib2 on Juju 4.0). All three charms reached `active`, relations were exercised, scale/refresh/kill/remove operations performed. |
| Reviewed | 2026-08-19 |

## What it does

Deploys Kubeflow Katib. `katib-controller` creates ClusterRoles, ServiceAccounts,
ClusterRoleBindings, CRDs, webhooks and the Katib controller pod; `katib-db-manager`
bridges Katib to MySQL; `katib-ui` serves the web UI. Relations: `katib-controller` ↔
`katib-db-manager` via `k8s-service-info`; `katib-db-manager` ↔ `mysql-k8s` via
`relational-db`; `katib-ui` optionally via `k8s-service-info` and
`istio-ingress-route`/`ingress`.

## Deployment log

### rv-katib (Juju 4.0 / concierge-k8s-4)

1. `juju deploy katib-controller katib-db-manager katib-ui --channel 0.18/stable --trust`
   - katib-ui: active immediately (no required relations)
   - katib-controller: blocked — missing `k8s-service-info` (required in 0.18/stable)
   - katib-db-manager: blocked — missing `relational-db`
2. `juju relate katib-controller:k8s-service-info katib-db-manager:k8s-service-info`
   - katib-controller: blocked → active in ~8s
3. `juju config katib-controller custom_images='{"invalid_json":'` (bad JSON)
   - katib-controller: active → blocked with misleading status
4. `juju config katib-controller custom_images=''`
   - still blocked — empty string → `parse_images_config` returns `[]`, `get_images()` calls
     `.items()` on a list → `AttributeError`
5. `juju config katib-controller custom_images='{}'`
   - blocked → active (empty dict works)
6. `juju remove-relation katib-controller:k8s-service-info katib-db-manager:k8s-service-info`
   - active → blocked (k8s-service-info missing again); re-related → active
7. Deployed `grafana-agent-k8s --channel 2/stable`, related `metrics-endpoint` and
   `grafana-dashboard`. katib-controller stayed active; correctly published `scrape_jobs`
   (`job_name: katib_controller_metrics`, `metrics_path: /metrics`, `targets: ["*:8080"]`),
   alert rules and dashboard JSON. grafana-agent-k8s itself stayed blocked (needs further
   integrations, not provided here).
8. `juju refresh katib-controller --channel 0.18/edge`: revision 1163 → 1354. Pod replaced;
   brief maintenance (~40s) then active; all relations preserved.
9. `juju scale-application katib-ui 2` — katib-ui/1 "Waiting for leadership" (expected);
   scaled back to 1.
10. `juju scale-application katib-controller 2` — katib-controller/1 waited for leadership;
    both eventually active.
11. `juju scale-application katib-controller 0`:
    - pods terminated; `remove` hook fired; ServiceAccount `katib-controller` deleted
    - scale back to 1: pod **failed to start** — `serviceaccount katib-controller not found`
    - recovery: manually recreated the ServiceAccount, scaled the StatefulSet 0 → 1
12. `juju config katib-controller custom_images='["a","b"]'` (YAML list) — same
    `AttributeError` path as the empty string; blocked with "Failed to compute status".
13. Sidecar architecture: katib-controller workload runs in a sidecar container named
    `katib-controller` with its own Pebble instance (`:38813`), separate from the charm
    container's Pebble (`:38812`, running only `container-agent`).
14. `kill -9` on katib-controller PID 21 (sidecar): Pebble auto-restarted within ~15s;
    charm stayed active throughout.
15. `juju remove-relation katib-controller:k8s-service-info katib-db-manager:k8s-service-info`
    — active → maintenance (brief) → blocked: "Missing relation with a k8s service info
    provider." Re-add: blocked → active within ~20s.
16. traefik-k8s (1.0/stable, rev 164) related to `katib-ui:ingress` — relation created
    (exit 0) but katib-ui went to `waiting`: "List of `<ops.model.Relation ingress:8>`
    versions not found for apps: traefik-k8s". traefik-k8s provides `ingress` v0;
    katib-ui requires `ingress` v1 with schema v2. `istio-ingress-route` uses the
    `istio_ingress_route` interface, which traefik-k8s does not support at all.
17. TLS: none of the three charms exposes `tls-certificates` in provides/requires;
    `self-signed-certificates` cannot be related to any of them.
18. `juju remove-application katib-controller` (full teardown): ClusterRole/
    ClusterRoleBinding `katib-controller` (KRH-managed) and `rv-katib-katib-controller`
    (Juju-substrate) were all deleted — teardown clean in this run. **Note**: an earlier
    teardown of the same app in this model left `rv-katib-katib-controller`
    ClusterRole/ClusterRoleBinding orphaned (see Findings) — the two observations are not
    fully reconciled and the orphan risk should be treated as real and unresolved.
19. `juju config katib-ui port=9999` then reset to `8080` — stayed active throughout;
    pebble service updated correctly.

### rv-katib-lxd (Juju 3.6 / concierge-k8s-3)

1. Deployed `mysql-k8s --channel 8.0/stable` (rev 423) and `katib-db-manager --channel
   0.18/stable` (rev 1123). mysql-k8s 8.0 requires Juju < 4.0.
2. `juju relate katib-db-manager:relational-db mysql-k8s:database` — blocked → active;
   pebble layer populated with `DB_HOST`, `DB_PASSWORD`, `DB_USER`, etc.
3. `kill 1` inside the katib-db-manager container — Pebble auto-restarted within 5s,
   RESTARTS counter incremented, status returned to active without intervention.
4. `juju remove-relation katib-db-manager:relational-db mysql-k8s:database` — active →
   blocked ("Please add required database relation: relational-db"). Re-related → active.
5. `juju scale-application katib-db-manager 2` — unit/1 in maintenance → waiting for
   leadership (expected: only leader applies K8s resources). Scaled back to 1.

### rv-katib2 (Juju 4.0 / concierge-k8s-4)

1. Deployed katib-controller/db-manager/ui (0.18/stable, rev 1163/1123/1122) plus
   `istio-ingress-k8s` (1/edge, rev 78).
2. `juju relate katib-controller:k8s-service-info katib-db-manager:k8s-service-info` —
   succeeded, katib-controller active.
3. `juju relate katib-ui:k8s-service-info katib-db-manager:k8s-service-info` — **failed**:
   "no candidates for katib-ui:k8s-service-info: relation endpoint not found" (katib-ui
   0.18/stable has no `k8s-service-info` endpoint).
4. `juju relate katib-ui:istio-ingress-route istio-ingress-k8s:ingress` — **failed**: "no
   candidates for katib-ui:istio-ingress-route: relation endpoint not found" — istio-ingress-k8s
   provides `ingress`, not `istio_ingress_route`; the interfaces are incompatible.
5. Bad-config / recovery sequence reproduced the same `AttributeError` path as in rv-katib
   (`custom_images=''` stays blocked, `custom_images='{}'` recovers).
6. `juju remove-relation` / re-relate on `k8s-service-info` reproduced the same
   blocked/active cycle as rv-katib.
7. SIGTERM (`kill -15`) then SIGKILL (`kill -9`) on the katib-controller sidecar process —
   Pebble auto-restarted within 3–5s each time; charm stayed active throughout.
8. `juju scale-application katib-controller 2` — unit/1 waited for leadership (expected).
9. Scale to 0 then back to 1 — reproduced issue #379: ServiceAccount deleted on scale-to-0,
   StatefulSet.create failed on scale-back with "serviceaccount katib-controller not found".
   Confirms the bug on Juju 4.0 as well as 3.6/4.0 elsewhere in this review.
10. Inspection of the earlier rv-katib teardown: `kubectl get clusterrole
    rv-katib-katib-controller` still returned a ClusterRole with
    `rules: [{apiGroups: ["*"], resources: ["*"], verbs: ["*"]}]` and no KRH labels — an
    orphaned, over-privileged ClusterRole persisting after `juju remove-application`.

### rv-katib3 (Juju 3.6 / concierge-k8s-3)

1. Deployed katib-controller (rev 1163), katib-db-manager (rev 1123), mysql-k8s (8.0/stable,
   rev 423) — confirms mysql-k8s deploys on Juju 3.6.
2. `juju relate katib-controller:k8s-service-info katib-db-manager:k8s-service-info` —
   katib-controller: blocked → maintenance → briefly active (14:01:02) → blocked again
   (14:01:06) → active after the next update-status hook (~14:05:57). Root cause:
   `relation-changed` fires on katib-controller before katib-db-manager has written its
   relation data; the charm self-heals but the intermediate blocked state is confusing.
   Confirmed data via `juju show-unit katib-controller/0`: `{name: katib-db-manager, port:
   "6789"}`. This transient state was not observed on Juju 4.0.
3. `juju scale-application katib-controller 2` — unit/1 waits for leadership (expected).
4. Scale to 0 then back to 1 — same issue #379 reproduced a third time.

## Observed behaviour

- All three pods reach Running/Ready; StatefulSets, Services, webhooks, ConfigMaps are
  created correctly.
- katib-controller pebble service active with env vars `KATIB_CORE_NAMESPACE`,
  `KATIB_DB_MANAGER_SERVICE_PORT=6789` set correctly from the `k8s-service-info` relation.
- katib-ui pebble service active; no `KATIB_DB_MANAGER_SERVICE_*` vars when unrelated (as
  expected for an optional relation).
- katib-db-manager pebble service active after the mysql-k8s relation, with
  `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `KATIB_MYSQL_DB_HOST:PORT` all correctly populated.
- Container security context: `runAsUser=0, runAsGroup=0` (root) despite metadata declaring
  `uid: 584792` — non-root is declared but not enforced by the charm.
- TLS certificate generation for katib-controller happens once, at first hook invocation,
  and is cached in `_stored`; it is **not** regenerated periodically (contrary to the
  "every 5 min" claim in issue #31, which the code does not support).
- Pebble auto-restarts katib-controller, katib-ui and katib-db-manager after SIGTERM/SIGKILL
  to the workload process, typically within 3–15s, with no explicit health checks
  configured — this is Pebble's default process-restart behaviour, not charm-specific logic.
- grafana-agent-k8s receives correct scrape config and dashboard JSON from katib-controller.
- katib-ui and katib-db-manager non-leader units on scale-up report "Waiting for leadership"
  — expected, all operations are gated behind `_check_leader()`.
- Scale-to-zero of katib-controller reliably reproduces issue #379 across three separate
  models (Juju 3.6 and 4.0): the `remove` hook deletes the ServiceAccount, and scaling
  back up fails until the ServiceAccount is manually recreated.
- KRH-managed `ClusterRole katib-controller` / `ClusterRoleBinding katib-controller` carry
  the expected KRH labels (`app.kubernetes.io/instance`, `kubernetes-resource-handler-scope`).
  The Juju k8s substrate separately creates `ClusterRole rv-<model>-katib-controller` /
  `ClusterRoleBinding rv-<model>-katib-controller` with **no** KRH labels — invisible to
  KRH's `delete()`. In one teardown these were cleaned up by Juju itself; in an earlier
  teardown of the same app they were observed to persist with `*/*:*/*` permissions. The
  two observations were not reconciled during this review (unverified which is the reliable
  behaviour).
- traefik-k8s relation to katib-ui fails on interface-version mismatch (`ingress` v0 vs
  required v1/schema v2); `istio-ingress-route` uses `istio_ingress_route`, unsupported by
  traefik-k8s. `istio-ingress-k8s` provides `ingress`, not `istio_ingress_route` — also
  incompatible. No published ingress charm currently works with katib-ui's ingress
  endpoints.
- No TLS integration for any of the three charms; `self-signed-certificates` cannot be
  related.
- Deprecation warnings observed in `juju debug-log`: `ops.main()` deprecated (katib-ui);
  `KubernetesServicePatch v1` deprecated, removal October 2025 (all three charms);
  `JujuVersion.from_environ()` deprecated (vendored `loki_k8s` v13, all charms).

## Findings

### Orphaned Juju-substrate ClusterRole with `*/*:*/*` permissions may persist after `juju remove-application`

- **Severity**: critical
- **Kind**: bug
- **Where**: Juju k8s substrate (creates `ClusterRole`/`ClusterRoleBinding
  rv-<model>-katib-controller`); `charms/katib-controller/src/templates/auth_manifests.yaml.j2`
  (ServiceAccount template); KRH cleanup path in `charmed_kubeflow_chisme`
- **Evidence**: After `juju remove-application katib-controller` in one model (rv-katib,
  first session), `kubectl get clusterrole rv-katib-katib-controller` still returned a
  ClusterRole with `rules: [{apiGroups: ["*"], resources: ["*"], verbs: ["*"]}]` and only
  Juju labels (`app.juju.is/created-by`, `app.kubernetes.io/managed-by`, etc.) — no KRH
  labels (`app.kubernetes.io/instance`, `kubernetes-resource-handler-scope`), so `KRH.delete()`
  cannot find it. A later teardown of the same app in the same review did show these
  resources being cleaned up. The two observations are inconsistent; the persistence has not
  been root-caused (unverified which condition triggers the leak).
- **Why it matters**: If real, a ClusterRole granting full cluster permissions to a
  ServiceAccount name persists indefinitely after charm removal, and a redeployed charm (or
  any future workload reusing that ServiceAccount name) inherits it silently.
- **Fix**: Add an explicit by-name cleanup of `rv-<model>-<app>` ClusterRole/ClusterRoleBinding
  in the charm's `remove` path, independent of KRH label matching; alternatively, have the
  Juju k8s substrate label the resources it creates so KRH can find them.
- **Linter rule**: not mechanically checkable — requires understanding Juju substrate
  resource lifecycle.

### `katib-controller`: scale-to-zero deletes ServiceAccount, breaking scale-back-to-n (issue #379)

- **Severity**: high
- **Kind**: bug
- **Where**: `charms/katib-controller/src/templates/auth_manifests.yaml.j2` (ServiceAccount
  creation); `KubernetesComponent.remove()` in `charmed_kubeflow_chisme`; `CharmReconciler`
  fires `remove` on both `juju remove-application` and pod termination from scale-to-zero
- **Evidence**: Reproduced live in three separate models (rv-katib, rv-katib2 on Juju 4.0;
  rv-katib3 on Juju 3.6). `juju scale-application katib-controller 0` fires the `remove` hook,
  which deletes the ServiceAccount. Scaling back to 1 fails:
  `error looking up service account rv-katib/katib-controller: serviceaccount "katib-controller"
  not found`. Manual recovery required (recreate ServiceAccount, scale StatefulSet 0 → 1).
- **Why it matters**: Any scale-to-zero-and-back workflow (autoscaling, some upgrade paths)
  breaks the charm and requires manual `kubectl` intervention.
- **Fix**: Don't delete the ServiceAccount in `remove()` while the StatefulSet still exists —
  e.g. guard the `remove` hook's resource deletion on whether it was triggered by full
  application removal versus scale-to-zero, or make ServiceAccount creation idempotent and
  skip its deletion entirely (the StatefulSet still needs it).
- **Linter rule**: not mechanically checkable — requires StatefulSet lifecycle awareness.

### `katib-controller`: reconciler swallows `get_layer()` exceptions, charm can report Active while broken

- **Severity**: high
- **Kind**: bug
- **Where**: `charmed_kubeflow_chisme.components.charm_reconciler.CharmReconciler.reconcile()`
  (upstream library); `charms/katib-controller/src/charm.py:201` (`inputs_getter` lambda)
  via `PebbleServiceComponent.get_layer()`
- **Evidence**: `CharmReconciler.reconcile()` catches all exceptions from `configure_charm()`
  with `except Exception as err: ... logger.error(msg)` — logged but not propagated and not
  reflected in status. `PebbleServiceComponent.get_status()` only checks `pebble_ready` and
  returns `ActiveStatus()` regardless. If `get_layer()` raises (e.g. `ValueError` from
  `get_service_info().port` in the `inputs_getter` lambda when the relation is broken), the
  reconciler logs and proceeds, and the charm still reports `ActiveStatus`.
- **Why it matters**: The charm can appear healthy while its pebble layer is stale or
  misconfigured, with no status signal that `configure_charm` failed.
- **Fix**: `KatibControllerPebbleService` should track `get_layer()` failures and surface
  `MaintenanceStatus`/`BlockedStatus` from `get_status()`; alternatively the reconciler should
  propagate `configure_charm` exceptions after logging.
- **Linter rule**: "PebbleServiceComponent subclass does not track `get_layer()` failures in
  `get_status()`" — not mechanically checkable without runtime behaviour analysis.

### `katib-controller`: `parse_images_config` returns a `list` for empty/YAML-list input, causing an unrecoverable `AttributeError`

- **Severity**: high
- **Kind**: bug
- **Where**: `charms/katib-controller/src/charm.py:78` (`parse_images_config` returns `[]`);
  `charms/katib-controller/src/charm.py:241` (`get_images` calls `custom_images.items()`)
- **Evidence**: `parse_images_config('')` returns `[]` although the function signature says
  `-> Dict`. `get_images()` calls `.items()` unconditionally, raising
  `AttributeError: 'list' object has no attribute 'items'`, surfaced as:
  ```
  [kubernetes:auths-webhooks-crds-configmaps] Failed to compute status.  See logs for details.
  ```
  Reproduced live twice: setting `custom_images=''` (recover with `custom_images='{}'`, not
  the empty string) and setting a YAML list, `custom_images='["a","b"]'` (same failure path,
  since `yaml.safe_load` accepts YAML lists and the README only documents JSON-dict format).
- **Why it matters**: An operator who clears `custom_images` or uses valid YAML list syntax
  cannot recover without guessing the correct reset value (`{}`, not `''`).
- **Fix**: Change `return []` to `return {}` in `parse_images_config`; add
  `isinstance(custom_images, dict)` guard in `get_images` with a clear error message.
- **Linter rule**: "Function that parses user-supplied config must not return heterogeneous
  types; empty input must return an empty dict, not a list" — mechanically checkable via
  type-annotation analysis and unit tests for empty/list input.

### `mlops_libs`: `KubernetesServiceInfoProviderWrapper.send_data` missing `return` after leader check

- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/mlops_libs/v0/k8s_service_info.py` (`send_data` method), vendored
  identically in katib-controller, katib-db-manager and katib-ui
- **Evidence**:
  ```python
  if not self.charm.model.unit.is_leader():
      logger.info("...Skipping event - no data sent.")
  # NO return HERE — execution continues even when not leader
  ```
  The comment says "otherwise return" but no `return` statement follows. On a single-unit
  deployment the unit is always leader, so the bug is latent, but the code will continue on
  to write relation data as a non-leader if a future code path calls `send_data` from a
  non-leader unit; Juju silently rejects such writes.
- **Why it matters**: Latent data-loss bug: any future change that triggers `send_data` from
  a non-leader will silently fail to write relation data.
- **Fix**: Add `return` immediately after the leader-check log message.
- **Linter rule**: "Control flow after a guard clause implying early exit must contain an
  explicit return/break/continue" — mechanically checkable with a custom AST rule.

### `katib-ui`: published charm (0.18/stable rev 1122, 0.18/edge rev 1316) lacks `k8s-service-info` endpoint

- **Severity**: high
- **Kind**: docs
- **Where**: published charmhub `katib-ui` 0.18/stable and 0.18/edge; local
  `charms/katib-ui/metadata.yaml` has `k8s-service-info` in requires
- **Evidence**: `juju info katib-ui --channel 0.18/edge` shows only `dashboard-links`,
  `ingress`, `logging` in requires. `juju relate katib-ui katib-db-manager` fails: "no
  compatible endpoints found" (also reproduced as "no candidates for
  katib-ui:k8s-service-info: relation endpoint not found" in rv-katib2). The local source
  HEAD has the endpoint, but it has not shipped in any published channel.
- **Why it matters**: The documented katib-ui ↔ katib-db-manager integration path does not
  work with any published katib-ui charm; the UI falls back to Kubernetes-injected env
  vars, which the charm's own code documents as racy. Tracked by open issue #410, unresolved.
- **Fix**: Promote local HEAD to a released channel, or clearly document the limitation on
  charmhub.
- **Linter rule**: not mechanically checkable.

### All charms: 21 ruff lint errors

- **Severity**: medium
- **Kind**: lint
- **Where**: `charms/katib-controller/src/`, `charms/katib-db-manager/src/`,
  `charms/katib-ui/src/`
- **Evidence**: `ruff check` found 21 errors: `I001` (3, unsorted imports), `UP006` (5 in
  katib-controller, `Dict` → `dict`), `UP045` (2 in katib-ui, `Optional[X]` → `X | None`),
  `TRY201` (3, bare `raise err` → `raise`), `RUF100` (5, unused `noqa` directives),
  `EXE001` (1, shebang on non-executable
  `charms/katib-controller/src/components/k8s_service_info_requirer_component.py`), `UP035`
  (1, `from typing import Dict` in `charms/katib-controller/src/charm.py`). 16 are
  auto-fixable with `ruff --fix`.
- **Why it matters**: Modest code-quality drift; the dead `noqa` directives add noise.
- **Fix**: `ruff check --fix`, then address the 5 remaining manually (including the
  `parse_images_config` return type).
- **Linter rule**: "Ruff E,W,F,I rules should be enforced in CI" — mechanically checkable.

### All charms: deprecated `ops.KubernetesServicePatch v1` library in use

- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/katib-controller/src/charm.py:21`,
  `charms/katib-db-manager/src/charm.py:14`, `charms/katib-ui/src/charm.py:32`
- **Evidence**: `juju debug-log` on all three charms: "WARNING ops.KubernetesServicePatch v1
  library is DEPRECATED and will be removed in October 2025. ... `ops.Unit.set_ports`
  functionality should be used instead."
- **Why it matters**: All three charms will break at import time once the library is
  removed; no migration is documented.
- **Fix**: Replace `KubernetesServicePatch` with `self.unit.set_ports(...)`.
- **Linter rule**: "Import or use of deprecated `KubernetesServicePatch` library" —
  mechanically checkable via import analysis.

### `katib-controller`: `service-mesh` declared as required in metadata but not enforced

- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/katib-controller/src/components/service_mesh_component.py:88-94`
  (`ServiceMeshComponent.get_status()`)
- **Evidence**: `metadata.yaml` has no `optional: true` for `service-mesh`, implying it's
  required, but `get_status()` returns `ActiveStatus()` regardless of relation presence.
  katib-controller reached `ActiveStatus` with no `service-mesh` relation during this review.
- **Why it matters**: Declared intent (required relation) doesn't match implementation,
  misleading operators about deployment requirements.
- **Fix**: Add `optional: true` to metadata, or enforce the required relation in
  `get_status()`.
- **Linter rule**: "Relation declared without `optional: true` but charm never raises
  `BlockedStatus` for its absence" — mechanically checkable.

### `katib-db-manager`: Pebble health checks permanently disabled, referencing open issue #128

- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/katib-db-manager/src/charm.py:149-155,163`
- **Evidence**: The entire Pebble `checks` section and `on-check-failure` are commented out
  with `# FIXME: uncomment when https://github.com/canonical/katib-operators/issues/128 is
  closed` (issue: `grpc_health_probe` binary missing from the 0.16.0 image). Confirmed via
  `pebble plan` in the running container — no `checks` section present. Two unit tests are
  skipped for this reason.
- **Why it matters**: No automated health monitoring of the workload beyond Pebble's default
  process-restart behaviour (which does work, per the observed-behaviour section).
- **Fix**: Re-enable health checks against an alternative probe (e.g. an HTTP `/healthz`
  endpoint), or explicitly document the decision and track resolution of #128.
- **Linter rule**: "Pebble service has no `on-check-failure` configured" — mechanically
  checkable via Pebble layer inspection.

### `katib-ui`: ingress relation to traefik-k8s and istio-ingress-k8s both fail — no working ingress path

- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/katib-ui/metadata.yaml` (`ingress`, `istio-ingress-route` endpoints)
- **Evidence**: `juju relate katib-ui:ingress traefik-k8s:ingress` succeeds at the relation
  level but katib-ui goes `waiting`: "List of `<ops.model.Relation ingress:8>` versions not
  found for apps: traefik-k8s" — traefik-k8s provides `ingress` v0 with no `versions` key;
  katib-ui requires `ingress` v1 with schema v2. Separately, `juju relate
  katib-ui:istio-ingress-route istio-ingress-k8s:ingress` fails outright: "no candidates for
  katib-ui:istio-ingress-route" — istio-ingress-k8s provides `ingress`, not the
  `istio_ingress_route` interface katib-ui requires.
- **Why it matters**: No published ingress charm currently works with katib-ui. Standalone
  deployment has no working ingress option; only an in-Kubeflow-bundle Istio setup would work.
- **Fix**: Add `ingress` v0/no-schema-v2 support to katib-ui, or clearly document that
  traefik-k8s and istio-ingress-k8s are both incompatible ingress providers.
- **Linter rule**: not mechanically checkable — requires interface compatibility testing.

### `katib-controller` on Juju 3.6: transient blocked state on relation establishment

- **Severity**: low
- **Kind**: bug
- **Where**: relation event ordering between katib-controller and katib-db-manager's
  `KubernetesServiceInfoProvider`
- **Evidence**: On Juju 3.6, `juju relate` produced:
  `blocked → maintenance → briefly active (14:01:02) → blocked (14:01:06) → active (after
  update-status, ~14:05:57)`. Root cause: `k8s-service-info-relation-joined` fires on
  katib-controller before katib-db-manager's data is persisted. Not observed on Juju 4.0 in
  this review.
- **Why it matters**: Self-healing but produces a confusing blocked-then-active sequence that
  could trigger unnecessary alerts.
- **Fix**: `K8sServiceInfoRequirerComponent.get_status()` should catch the missing-data error
  and return `WaitingStatus` with a clear message instead of transient `blocked`.
- **Linter rule**: not mechanically checkable — timing-dependent race condition.

### `katib-controller`: `gen_certs` uses blocking `subprocess.check_call` with no timeout

- **Severity**: low
- **Kind**: performance
- **Where**: `charms/katib-controller/src/certs.py:28-62`
- **Evidence**: 5 blocking `subprocess.check_call` calls (`genrsa` × 2, `req` × 2, `x509` × 1)
  with no timeout. Only invoked once, on first hook, since certs are cached in `_stored`
  thereafter (the "every 5 min" concern in issue #31 is not supported by the code).
- **Why it matters**: On a slow host, adds measurable startup latency; a hung OpenSSL
  process could block the charm indefinitely.
- **Fix**: Use `subprocess.run(..., timeout=30)`, or generate certs in-process with the
  `cryptography` package.
- **Linter rule**: "Blocking subprocess call without timeout in charm init/hot path" —
  mechanically checkable.

### `katib-ui`: uses deprecated `main(KatibUIOperator)` pattern

- **Severity**: low
- **Kind**: lint
- **Where**: `charms/katib-ui/src/charm.py:326`
- **Evidence**: `main(KatibUIOperator)` produces `DeprecationWarning: Calling ops.main() is
  deprecated, call ops.main() instead` on every update-status hook.
- **Why it matters**: Log noise; will break when `ops` removes support.
- **Fix**: Use `ops.main()` directly.
- **Linter rule**: "Call to deprecated `ops.main()` form" — mechanically checkable.

### `katib-ui`: non-leader units always report `WaitingStatus`

- **Severity**: low
- **Kind**: ux
- **Where**: `charms/katib-ui/src/charm.py:239` (`_check_leader`)
- **Evidence**: `_check_leader()` runs first in `main()`; every non-leader unit reports
  "Waiting for leadership" regardless of workload health. Observed when scaling katib-ui to
  2 units. katib-db-manager has the same pattern.
- **Why it matters**: Cosmetic but can be mistaken for a real problem when scaling to
  multiple units.
- **Fix**: Gate only leadership-requiring operations behind `_check_leader()`; report
  `ActiveStatus("Standby")` for non-leader units.
- **Linter rule**: not mechanically checkable — design decision.

### All charms: no `tls-certificates` integration endpoint

- **Severity**: low
- **Kind**: ux
- **Where**: `metadata.yaml` for all three charms
- **Evidence**: `juju info` for all three charms shows no `tls-certificates` in provides or
  requires; `self-signed-certificates` cannot be related to any of them.
- **Why it matters**: No charm-native TLS provisioning path; operators must rely on external
  mechanisms (e.g. Istio mTLS).
- **Fix**: Add a `tls-certificates` requires relation where TLS is desired.
- **Linter rule**: not mechanically checkable — design decision.

### All charms: vendored `loki_k8s` (v13) uses deprecated `JujuVersion.from_environ()`

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/loki_k8s/v1/loki_push_api.py`
- **Evidence**: `DeprecationWarning` visible in unit test runs and `juju debug-log` for all
  charms using `LogForwarder`.
- **Why it matters**: Will break outright when the API is removed; requires updating a
  vendored library.
- **Fix**: `charmcraft fetch-lib` a newer version of `loki_k8s`.
- **Linter rule**: not mechanically checkable for vendored libraries.

### `katib-controller`: kubeflow-profiles / cmr-mesh relation not exercised by charm's own tests

- **Severity**: low
- **Kind**: test-gap
- **Where**: `charms/katib-controller/metadata.yaml` (`require-cmr-mesh`,
  `provide-cmr-mesh`); `tests/integration/test_charms.py`
- **Evidence**: The integration test deploys `kubeflow-profiles` and relates it via a shared
  `charmed_kubeflow_chisme.testing` helper, but the `cross_model_mesh` interface's data
  format and status handling are not exercised or documented in the charm's own tests.
- **Why it matters**: A core deployment-topology relation has no dedicated regression
  coverage.
- **Fix**: Add a unit/scenario test exercising the cmr-mesh relation data format directly.
- **Linter rule**: not mechanically checkable.

### All charms: no `actions.yaml`

- **Severity**: informational
- **Kind**: docs
- **Where**: all three charms
- **Evidence**: no `actions.yaml` present; `juju run-action` fails with "no actions defined
  on charm". All operations go through config/relations, appropriate for these charms.
- **Why it matters**: no issue, informational only.
- **Fix**: none required.
- **Linter rule**: informational only.

## Worth copying

**Structured component-based reconciliation in katib-controller** — `CharmReconciler` with
`KubernetesComponent`, `LeadershipGateComponent`, `PebbleServiceComponent` and custom
components is a clean pattern; each component has a clear `get_status()`, and the reconciler
orchestrates them. Cleaner than the single-handler-per-event style in katib-db-manager and
katib-ui. See `charms/katib-controller/src/charm.py`.

**Explicit blocking of mutually exclusive relations in katib-ui** — `_check_istio_relations()`
(`charms/katib-ui/src/charm.py:278-296`) checks for the presence of both ambient and sidecar
ingress relations and raises `CheckFailed` with a clear message — good defensive pattern.

**Graceful degradation for optional k8s-service-info in katib-ui** —
`_get_db_manager_service_info()` (`charms/katib-ui/src/charm.py:245-268`) returns `None` when
the relation is absent or has no data, falling back to Kubernetes-injected env vars, with the
race condition it avoids documented in the code.

**`ErrorWithStatus` pattern in katib-db-manager** — `GenericCharmRuntimeError`,
`ErrorWithStatus` and typed status-raising used consistently
(`charms/katib-db-manager/src/charm.py`), making status propagation predictable.

## Common-practice notes

- `charmcraft.yaml`: all three use the `poetry` plugin (two-part `poetry-deps` +
  `charm-poetry` build), pinned Rust 1.92.0, Python 3.12, `uv` for tool installation.
- Charm libraries vendored under `lib/charms/<name>/v<N>/` — standard location, no
  versioning issues found.
- `ops` pinned to `^2.17.1` across all charms — current stable, no `ops` v3 usage.
- `mlops_libs` v0 (`k8s_service_info`) is used by all three charms; its `send_data` bug is
  covered in Findings.
- All charms declare `charm-user: non-root` and `uid: 584792` in container specs, but pods
  run as root (`runAsUser: 0`) — a metadata/reality mismatch.
- `charmed-kubeflow-chisme` `^0.4.x` used for K8s resource handling, pebble operations and
  components (`^0.4.22` in katib-controller, `>=0.4.11` in db-manager).
- `data_platform_libs`'s `DatabaseRequires` used by katib-db-manager for MySQL — standard.
- Complete Terraform modules under `terraform/` for all three charms with correct
  `provides`/`requires` outputs.
- CI (`ci.yaml`/`concierge.yaml`) tests only against Juju 3.6/stable, K8s 1.32-classic/stable
  — no LXD bootstrap, K8s only.
- Renovate is configured but broken (open issue #351: invalid JSON preset).

## Tests

- Unit tests (via `tox -e unit`, confirmed in this review, run twice with consistent results):
  - katib-controller: 12/12 pass, 89% coverage, 23 warnings (deprecated `Harness`,
    `JujuVersion.from_environ()`)
  - katib-db-manager: 9/11 pass (2 `test_update_status` cases skipped, FIXME referencing
    issue #128), 75% coverage, 17 warnings
  - katib-ui: 15/15 pass, 94% coverage, 29 warnings
  - Total: 36/38 pass, 2 skipped, 0 failed
- Coverage gaps:
  - No unit test for `parse_images_config('')` or a YAML-list input — the exact bug
    reproduced live in this review is untested
  - No unit test for the reconciler's exception-swallowing behaviour in
    `PebbleServiceComponent.get_status()`
  - No unit test for the `remove` hook path in any charm (no coverage of KRH cleanup or
    ServiceAccount deletion on scale-to-zero)
  - No test of `custom_images` recovery after an invalid value
  - All tests are `Harness`-based (deprecated per pytest warning); no scenario/state-transition
    tests
  - The two skipped health-check tests leave that code path entirely untested in
    katib-db-manager
  - katib-controller (89%): `parse_images_config` error path (lines 78, 81-85), `certs.py`
    cleanup path (line 94), and the `inputs_getter` lambda (lines 200-240) uncovered
  - katib-db-manager (75%): `_on_install` K8s resource path, `_on_remove` cleanup path,
    `_get_check_status` health-check path uncovered
  - katib-ui (94%): `_katib_ui_layer` with a real `KubernetesServiceInfoObject`,
    `_deploy_k8s_resources` ApiError path, `_check_istio_relations` with both relations
    present, `_handle_ingress` error paths uncovered
  - No test of `mlops_libs`' `send_data` behaviour on non-leader units
  - No test of the `cross_model_mesh` interface data format for `require-cmr-mesh`/
    `provide-cmr-mesh`
- Integration tests: exercise the full lifecycle — build, deploy, config changes, CRDs,
  ConfigMaps, security context, metrics, logging, ingress. katib-ui's integration tests
  also cover ambient mesh with multiple ingress relations. All build from local source via
  `ops_test.build_charm()`.
- Bundle integration test (`tests/integration/test_charms.py`): deploys all three katib
  charms + mysql-k8s + kubeflow-profiles + service mesh, verifies full idle.
- Linting: `pflake8` and `codespell` clean. `isort`/`black` check only `src/` and `tests/`,
  not vendored `lib/`. `ruff check` finds the 21 errors covered in Findings (16
  auto-fixable).

## Docs

- README.md: documents install sequence, bundle deploy, per-charm deploy; the "Setting
  Custom Images" section correctly documents the JSON dict format; the `--channel=edge` note
  is accurate.
- CONTRIBUTING.md: template-style, minimal but functional, same across all three charms.
- Terraform `README.md` per charm documents inputs/outputs.
- Doc/reality mismatch: README says to relate `istio-pilot katib-ui` for Kubeflow
  integration, but current katib-ui uses `istio-ingress-route` (Gateway API), not
  `istio-pilot` — README not updated for the ambient-mesh rewrite.
- Doc/reality mismatch: README documents JSON-dict format only for `custom_images`, but
  `parse_images_config` also silently accepts YAML (including lists), which triggers the
  `AttributeError` bug — an undocumented footgun.
- Charmhub description is accurate for what it covers but doesn't mention the katib-ui
  `k8s-service-info` gap or the disabled health checks.

## Open questions

1. When will `KubernetesServicePatch` be migrated to `ops.Unit.set_ports`? Removal is
   October 2025 with no documented migration plan.
2. Will `service-mesh` become a truly required relation, or should the metadata be relaxed
   to `optional: true`?
3. What is the current status of issue #128 (missing `grpc_health_probe`)? Is a health
   endpoint planned, or is running without health checks a deliberate decision?
4. Why does katib-controller 0.18/stable have `k8s-service-info` but katib-ui does not in
   any published channel? Issue #410 tracks making the katib-ui relation mandatory but has
   not shipped.
5. Is the scale-to-zero ServiceAccount deletion (#379) actually fixed anywhere upstream?
   Reproduced three times in this review across two Juju versions — no evidence of a fix.
6. What is the plan (if any) for migrating from `Harness` to `scenario` tests?
7. What is the plan for updating the vendored `loki_k8s` library past its deprecated API?
8. Why does the Juju k8s substrate create a duplicate, unlabeled ClusterRole/
   ClusterRoleBinding alongside the KRH-managed ones, and under what conditions does it
   persist vs. get cleaned up on `juju remove-application`? This review saw both outcomes
   and could not reconcile them.
9. Can traefik-k8s or istio-ingress-k8s be made compatible with katib-ui's ingress
   endpoints? Currently neither works.
10. What is the root cause of the transient blocked state on Juju 3.6 relation
    establishment — a timing issue in `ops`, or in the library's `send_data`
    implementation?
