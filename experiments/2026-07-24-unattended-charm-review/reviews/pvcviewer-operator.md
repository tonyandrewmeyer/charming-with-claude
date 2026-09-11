# pvcviewer-operator

A Kubernetes charm wrapping the [pvcviewer-controller](https://github.com/kubeflow/kubeflow/tree/master/components/pvcviewer-controller) from Kubeflow. It provides a CRD and webhook to open a file-browser UI on arbitrary PersistentVolumeClaims, and ships its own RBAC, CRD, webhook configuration, self-signed certs, Istio integration, metrics, Loki logging, and Grafana dashboards.

**Verdict**: the charm works, but only with `--trust`, and that requirement is undocumented. The RBAC declared in `auth_manifests.yaml.j2` omits the cluster-scoped `customresourcedefinitions` permission the charm actually needs at startup, so every deployment without `--trust` goes permanently `blocked` — on both Juju 3.6 and 4.x. Integration tests always pass `trust=True`, so CI cannot catch this. A maintainer should first either self-declare the needed cluster-scoped RBAC (`juju-app-access` in `metadata.yaml`) or document `trust` as a hard requirement, then fix the `stop`-hook/cluster-resource-leak issue on removal, then add a non-trust CI job so this class of bug can't silently return.

| | |
|---|---|
| Repo | kubeflow-charming/pvcviewer-operator @ `49f27c4` (2026-05-28) |
| Charms | `pvcviewer-operator` |
| Substrate | k8s |
| Deployed | yes — `concierge-k8s-4:rv-pvcviewer-trust` (`1.10/edge` rev 487, `--trust`, `active`, later removed); `concierge-k8s-4:rv-pvcviewer-fresh` (`blocked` without trust); `concierge-k8s-3:rv-pvcviewer-k8s3` (`blocked` without trust); `concierge-lxd-4:rv-pvcviewer-lxd` (`error`); `concierge-k8s-4:rv-pvcviewer-k8s4` (`active`, confirmed deployed with `--trust`) |
| Reviewed | 2026-08-24 |

## What it does

Deploys a StatefulSet (created by Juju's k8s substrate from the container spec in `metadata.yaml`, not by the charm) running `/manager` (workload container, UID 584792) alongside the charm container (UID 170). Exposed via a ClusterIP Service on 443/8443 (webhook) and 8080 (metrics). The controller exposes `:9443` (webhook, TLS), `:8080` (metrics), `:8081` (health probe).

The leader unit creates: CRD `pvcviewers.kubeflow.org`, ClusterRole/ClusterRoleBinding, Role/RoleBinding, ServiceAccount, Service, and MutatingWebhookConfiguration + ValidatingWebhookConfiguration (self-signed certs stored in `StoredState`).

Relations: `service-mesh` (Istio), `gateway-metadata`, `metrics-endpoint` (Prometheus), `grafana-dashboard`, `logging` (Loki). No custom config options — all configuration is via relations and the workload image, a deliberate design choice.

## Deployment log

### Kubernetes with `trust=True` (`rv-pvcviewer-trust`)

```
juju deploy pvcviewer-operator --channel 1.10/edge --trust -m rv-pvcviewer-trust
```

- Rev 487 on ubuntu@24.04 k8s, `concierge-k8s-4` (Juju 4.0.12). Reached `active` within ~60s. Clean; still `active` after 5 minutes, Pebble service `active`.
- With `trust=True`, the charm creates the CRD, webhooks, Service, RBAC, and the workload starts correctly.
- The ServiceAccount still has `automountServiceAccountToken: false`, but Juju overrides this at container level — the charm container has a mounted k8s API token regardless. The relevant permission is the SA's RBAC, which becomes cluster-scoped via `--trust`.

### Kubernetes without `trust` (`rv-pvcviewer-fresh`, `rv-pvcviewer-k8s3`)

- `rv-pvcviewer-fresh` (Juju 4.0.12), rev 487, no `--trust`: immediately `blocked`:
  ```
  lightkube.core.exceptions.ApiError: customresourcedefinitions.apiextensions.k8s.io is forbidden:
  User "system:serviceaccount:rv-pvcviewer-fresh:pvcviewer-operator" cannot list resource
  "customresourcedefinitions" in API group "apiextensions.k8s.io" at the cluster scope
  ```
- `rv-pvcviewer-k8s3` (Juju 3.6.25): identical `blocked` result, same error text.
- `kubectl auth can-i list customresourcedefinitions --as=system:serviceaccount:rv-pvcviewer-fresh:pvcviewer-operator` → `no` without trust.
- Confirmed identical across Juju 3.6 and 4.x — not a Juju-version issue.

### Kubernetes after refresh (`rv-pvcviewer-k8s4`)

- `rv-pvcviewer-k8s4` was in fact deployed **with** `trust=True` (its ClusterRole `rv-pvcviewer-k8s4-pvcviewer-operator` grants `apiGroups:['*'], resources:['*'], verbs:['*']`, the cluster-admin role `--trust` produces). Model stayed `active` throughout.
- `juju refresh pvcviewer-operator --channel 1.10/edge` → rev 487. Clean upgrade, ~10s. `config-changed` re-reconciled all components.

### Application removal (`rv-pvcviewer-trust`)

- `juju remove-application pvcviewer-operator` issued.
- Unit entered `error`: `"resolver loop error: unit is dead"`. The `stop` hook did not fire.
- CRD `pvcviewers.kubeflow.org` and ClusterRole `pvcviewer-role` remained in the cluster (labeled as owned by the still-running `rv-pvcviewer-k8s4` model). Webhook configurations also not deleted.
- The `rv-pvcviewer-trust` application itself was fully removed from Juju; the cluster-scoped resources it shared with `rv-pvcviewer-k8s4` persisted.

### LXD (`concierge-lxd-4`)

```
juju deploy pvcviewer-operator --channel 1.11/edge
```
- Machine `juju-c56cef-0` (ubuntu@24.04). Install hook crashed: `FileNotFoundError: /var/run/secrets/kubernetes.io/serviceaccount/namespace`. Charm `error`, and every subsequent hook repeats the same crash.

## Observed behaviour

### With trust=True (working)

- Install/start timing: ~60s deploy → `active`.
- Pebble service: `startup: enabled`, `override: replace`, `active` after ~90s.
- K8s resources created by the charm: CRD, `pvcviewer-mutating-webhook-configuration` and `pvcviewer-validating-webhook-configuration` (cluster-scoped), `pvcviewer-role` ClusterRole (cluster-scoped), ClusterIP Service on 443/8080. The StatefulSet itself is created by Juju's substrate, not the charm.
- Metrics: `/metrics` on `:8080`, verified in the Pebble layer.
- Scale to 2: unit 1 comes up `running` (charm container) but Pebble service `inactive` — leadership gate correctly blocks workload start on the non-leader.
- Scale back to 1: StatefulSet updated by Juju in the normal case. When a scale-down was issued while the charm was `blocked`, the StatefulSet stayed at `replicas=2` even though Juju reported scale=1 — a Juju/substrate interaction rather than a charm bug, but it left an orphaned pod `pvcviewer-operator-1` (charm container only, no workload container) after one scale up/down cycle.
- Workload process kill (`kill -9` on the manager PID): Pebble auto-restarts the manager within ~5s; pod shows `restarts=1`; manager re-acquires the leader lease and restarts its workers. No charm hook fires — Pebble handles recovery entirely.
- Full pod delete (leader): triggers `upgrade-charm` → `config-changed` → `start` → `pebble-ready`; `active` again within ~25s. `upgrade-charm` forces a fresh reconciliation of CRDs/RBAC/webhooks. Certs are not regenerated (`_gen_certs_if_missing` finds everything already in `StoredState`).
- Cert rotation on pod delete: `controller-runtime.certwatcher` sees `REMOVE` events for `tls.key`/`tls.crt` and re-reads them gracefully — no downtime, verified from Pebble logs.
- Prometheus (`metrics-endpoint`) relate/unrelate: both sides `active` throughout. Relate fires `-relation-created`, `-relation-joined`, `-relation-changed` (×2); remove fires `-relation-departed` → `-relation-broken`. Clean lifecycle.
- `grafana-dashboard` relation: the charm provides interface `grafana_dashboard`, which does not match `grafana-agent-k8s`'s consumer interface `grafana_dashboards` (plural) — integration fails with `no candidates for pvcviewer-operator:grafana-dashboards`.
- `logging` relation (Loki): works as designed via `LogForwarder`.
- Application removal: as above — `stop` hook never runs because the unit dies first; cluster-scoped resources (CRD, ClusterRole, webhook configs) are not cleaned up.

### Without trust (broken)

- All tested Juju versions: `blocked` immediately on fresh deploy; `auth can-i list customresourcedefinitions` → `no`.
- `automountServiceAccountToken: false` on the SA is a red herring: the charm container does have a mounted k8s API token (Juju overrides the SA setting at container level). The actual failure is that the SA's RBAC is namespace-scoped without `--trust`, and the charm needs cluster-scoped CRD list access at startup.
- Juju 3.6 (`rv-pvcviewer-k8s3`): identical error text to the Juju 4.x case.

### Unit test run

```
PYTHONPATH=src:lib pytest tests/unit/test_operator.py -v
```
- 15/15 pass in ~7.5s. Uses deprecated `Harness` (emits `PendingDeprecationWarning`). Requires `ops==2.23.1` and `ops-scenario==7.23.1` — the standalone `scenario` package from PyPI is incompatible (imports `JujuContext`, removed in ops 2.23+).
- Coverage: 93% overall. Gaps:
  - `src/certs.py:95` — `gen_certs` return statement (unreached)
  - `src/charm.py:175–196` — `_gen_certs_if_missing` error path
  - `src/components/pebble_component.py:29–30` — `get_layer` error path
  - `src/components/service_mesh_component.py:88–89, 151` — `_configure_app_leader` and a `get_status` edge case

### Lint (`ruff check src/ tests/`)

- 4 errors in `src/`: `I001` unsorted imports, `RUF100` unused noqa, `UP035`/`UP006` deprecated `Tuple`. All fixable with `ruff check --fix`.
- 7 errors in `tests/`: `EXE001` files not executable, `TRY203` redundant exception handler, `TRY201` bare raise, `SIM117` nested `with` statements. Also fixable.
- Not caught by the project's own lint (`tox -e lint` uses pflake8+isort+black+codespell, no ruff) — that suite passes clean.

## Findings

### CRITICAL: Charm requires `trust=True` but doesn't declare or document it

- **Severity**: critical
- **Kind**: bug / ux
- **Where**: `src/templates/auth_manifests.yaml.j2:88` (RBAC missing a rule); `metadata.yaml` (no `juju-app-access`); `README.md` (no mention of trust)
- **Evidence**: The charm's `pvcviewer-role` ClusterRole covers namespaced resources (`deployments`, `persistentvolumeclaims`, `pods`, `services`, `pvcviewers`, ...) but not the cluster-scoped `customresourcedefinitions.apiextensions.k8s.io`. `charmed_kubeflow_chisme`'s `KubernetesComponent` (invoked from `src/charm.py`) calls `lightkube.Client().list(CustomResourceDefinition)` at startup to detect drift, and without cluster-scoped list permission this raises:
  ```
  lightkube.core.exceptions.ApiError: customresourcedefinitions.apiextensions.k8s.io is forbidden:
  User "system:serviceaccount:...:pvcviewer-operator" cannot list resource
  "customresourcedefinitions" in API group "apiextensions.k8s.io" at the cluster scope
  ```
  Confirmed on Juju 3.6.25 and 4.0.12: `blocked` without `trust`, `active` with `trust`.
- **Impact**: `juju deploy pvcviewer-operator` without `--trust` produces a permanently broken charm. Nothing in the README or Charmhub description warns about this; the charm is unusable in production without discovering this by trial and error.
- **Fix**: Add `juju-app-access: ""` to `metadata.yaml` to self-declare the cluster-scoped CRD read permission, or add the explicit RBAC rule to `auth_manifests.yaml.j2`, or at minimum document `trust` as a hard requirement in `README.md`.
- **Linter rule**: not mechanically checkable without deploying.

### CRITICAL: Integration tests always deploy with `trust=True`, masking the failure

- **Severity**: critical
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py:131`; `tests/integration/test_charm_ambient.py:85`
- **Evidence**:
  ```python
  # tests/integration/test_charm.py:131
  await ops_test.model.deploy(
      entity_url, resources=resources, application_name=CHARM_NAME, trust=True
  )
  ```
  Both integration test files always pass `trust=True`, granting cluster-admin. CI is green regardless of whether the RBAC gap above is present.
- **Impact**: The RBAC bug can regress silently — CI provides no signal.
- **Fix**: Add a CI job that deploys without `trust` and asserts the charm doesn't go `blocked`, or remove `trust=True` from tests once the charm self-declares its cluster-scoped permissions.
- **Linter rule**: not mechanically checkable.

### HIGH: `stop` hook never fires on `juju remove-application` — cleanup code never runs

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py` removal path (`KubernetesComponent.remove()`, `ServiceMeshComponent.remove()`); observed on `rv-pvcviewer-trust`
- **Evidence**:
  ```
  juju.worker.uniter resolver loop error: preparing operation "run stop hook" for pvcviewer-operator/0:
  getting context for unit "pvcviewer-operator/0": unit is dead
  ```
  The unit dies before the `stop` hook runs, so the `remove()` handlers that would delete CRDs, ClusterRoles, and webhook configurations never execute.
- **Impact**: Cluster-scoped resources (CRD, ClusterRole, Mutating/ValidatingWebhookConfiguration) leak after `remove-application`. Resource leak and lingering-webhook security concern.
- **Fix**: Root-cause why the `stop` hook doesn't fire before unit death on this substrate/version; as a mitigation, consider a finalizer-based cleanup path that doesn't depend on the charm hook lifecycle.
- **Linter rule**: not mechanically checkable.

### HIGH: Cluster-scoped resources collide across models sharing a cluster

- **Severity**: high
- **Kind**: bug
- **Where**: `src/templates/crd_manifests.yaml.j2` / `auth_manifests.yaml.j2` (no per-model label); `charmed_kubeflow_chisme`'s `create_charm_default_labels`
- **Evidence**: The CRD `pvcviewers.kubeflow.org` and ClusterRole `pvcviewer-role` created in the cluster were labeled `app.kubernetes.io/instance: pvcviewer-operator-rv-pvcviewer-k8s4` — i.e. owned by whichever model first created them (`rv-pvcviewer-k8s4`), not by `rv-pvcviewer-trust`, which also deployed the charm to the same cluster and reused (applied over) the same resources. After `rv-pvcviewer-trust` was removed, the CRD and ClusterRole (still labeled for `rv-pvcviewer-k8s4`) remained, because `rv-pvcviewer-trust`'s `remove()` selector never matched them.
- **Impact**: In any cluster hosting more than one deployment of this charm, cluster-scoped resources are effectively owned by whichever model created them first, and later models' `remove()` handlers can't clean up "their" copy. Confusing ownership in multi-tenant clusters, and a related integration test (`test_remove_deletes_virtual_service` in `test_charm_ambient.py`) would be expected to fail in this scenario.
- **Fix**: Add model-identifying labels (e.g. `model.juju.is/id`) to cluster-scoped resources in the templates, or configure `KubernetesComponent` with model-specific labels; this is arguably a `charmed_kubeflow_chisme` library issue rather than charm-specific.
- **Linter rule**: not mechanically checkable.

### HIGH: LXD (machine) substrate — install hook crashes unconditionally

- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/observability_libs/v1/kubernetes_service_patch.py:304`, triggered unconditionally from `src/charm.py` (`PvcViewer.__init__`)
- **Evidence**:
  ```python
  # lib/charms/observability_libs/v1/kubernetes_service_patch.py:304
  with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
      return f.read().strip()
  ```
  `KubernetesServicePatch(...)` is called unconditionally in `PvcViewer.__init__`. On LXD there is no service-account namespace file, so this raises `FileNotFoundError`, uncaught, and the charm enters `error` permanently; every subsequent hook repeats the crash. `charmcraft.yaml` declares `platforms: ubuntu@24.04:amd64` without a `k8s`-only qualifier, so charmcraft permits the LXD deploy in the first place.
- **Impact**: Any operator deploying this charm to LXD gets a permanently bricked unit.
- **Fix**: Replace `KubernetesServicePatch` with `self.unit.set_ports(...)` (`ops ≥ 2.17.1`), or guard the call behind a check that the service-account namespace file exists.
- **Linter rule**: not mechanically checkable.

### MEDIUM: `gateway-metadata` absence silently defaults to a hardcoded, possibly-nonexistent Gateway

- **Severity**: medium
- **Kind**: robustness
- **Where**: `src/components/service_mesh_component.py:111–112`
- **Evidence**:
  ```python
  # src/components/service_mesh_component.py:111
  f"Relation {self._gateway_metadata_relation_name} not found, "
  "defaulting to sidecar configuration."
  gateway_namespace = "kubeflow"
  gateway_name = "kubeflow-gateway"
  ```
  When `gateway-metadata` is absent, the component logs a WARNING and defaults to `namespace=kubeflow, name=kubeflow-gateway`, and configures the workload with `EXPERIMENTAL_K8S_GATEWAY_NAME=kubeflow-gateway` regardless.
- **Impact**: If no Istio Gateway exists at those coordinates, the workload will fail to route traffic while the charm shows `active` — a silent misconfiguration.
- **Fix**: Return `WaitingStatus` from `get_status()` when `gateway-metadata` is absent and ambient mesh is not enabled, rather than defaulting silently.
- **Linter rule**: not mechanically checkable.

### MEDIUM: `ServiceMeshComponent._configure_app_leader` untested

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/components/service_mesh_component.py:88–89` (and around 151)
- **Evidence**: Unit tests mock `ServiceMeshComponent` entirely; coverage confirms these lines are missed. This is the ambient-mesh `AuthorizationPolicy` creation path (`PolicyResourceManager.reconcile()`), which requires cluster-scoped RBAC at runtime and is completely untested.
- **Fix**: Add a unit test patching `_policy_resource_manager` and asserting `reconcile()` is called with the right `MeshType`/policy list when `is_ambient_mesh_enabled()` is `True`.
- **Linter rule**: not mechanically checkable.

### MEDIUM: `PvcViewerPebbleService.get_layer` error path untested

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/components/pebble_component.py:29–30`
- **Evidence**: `get_layer()`'s `except: raise ValueError(...)` path is unreached per coverage; tests mock `ServiceMeshComponent` with fixed return values only.
- **Fix**: Add a test that makes `_inputs_getter` raise and asserts `ValueError`.
- **Linter rule**: not mechanically checkable.

### MEDIUM: `certs.py` `gen_certs` not exercised

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/certs.py:14–97` (specifically line 95, return statement)
- **Evidence**: `gen_certs()` calls `subprocess.check_call(["openssl", ...])` four times; unit tests mock the whole `PvcViewer` class so `_gen_certs`/`_gen_certs_if_missing` (`src/charm.py:175–196`) is never invoked.
- **Fix**: Add a test mocking `subprocess.check_call`/`tempfile` and asserting `gen_certs` returns `{"cert", "key", "ca"}`.
- **Linter rule**: not mechanically checkable.

### MEDIUM: `ServiceMeshComponent.get_status` edge case untested

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/components/service_mesh_component.py:151` (draft cites 151, notes cite 135 — location unverified)
- **Evidence**: Coverage confirms the line is unreached: `get_status()` should return `WaitingStatus` when `gateway-metadata` relation exists but `get_metadata()` returns `None`. Existing unit test covers the component in isolation, not full charm-level status propagation.
- **Fix**: Add an integration test that relates `gateway-metadata` without populating data and asserts the charm goes `waiting`.
- **Linter rule**: not mechanically checkable.

### MEDIUM: Integration tests contain a redundant `try/except: raise e`

- **Severity**: medium
- **Kind**: lint
- **Where**: `tests/integration/test_charm.py:64–67`; `tests/integration/test_charm_ambient.py:64–66`
- **Evidence**:
  ```python
  # tests/integration/test_charm.py:64
  try:
      lightkube_client.apply(obj)
  except lightkube.core.exceptions.ApiError as e:
      raise e
  ```
  Ruff flags `TRY201` (bare raise) and `TRY203` (remove the handler); also `SIM117` for nested `async with` blocks nearby that could be merged.
- **Fix**: `ruff check --fix tests/integration/` handles `TRY201`/`SIM117`; `TRY203` needs manual removal of the wrapper.
- **Linter rule**: `TRY201`, `TRY203`, `SIM117` — checkable with `ruff check`.

### LOW: `ssl.conf.j2` template loaded via a relative path

- **Severity**: low
- **Kind**: robustness
- **Where**: `src/certs.py:11`
- **Evidence**:
  ```python
  SSL_CONFIG_FILE = "src/templates/ssl.conf.j2"
  template = Template(Path(SSL_CONFIG_FILE).read_text())
  ```
  Depends on the process's working directory being the repo root.
- **Fix**: `Template((Path(__file__).parent.parent / "templates" / "ssl.conf.j2").read_text())`.
- **Linter rule**: not mechanically checkable.

### LOW: Bundled `kubernetes_service_patch` v1 library is deprecated, past removal date

- **Severity**: low
- **Kind**: maintainability
- **Where**: `lib/charms/observability_libs/v1/kubernetes_service_patch.py`
- **Evidence**: Library marked `#[DEPRECATED!]`; Juju emits a warning that it "will be removed in October 2025" — a date already past as of this review (2026-08-24).
- **Fix**: Replace with `self.unit.set_ports(...)` in `PvcViewer.__init__` (also fixes the LXD crash above).
- **Linter rule**: not mechanically checkable (bundled, not from PyPI).

### LOW: Unsorted imports in `charm.py`

- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:10–43`
- **Evidence**: `ruff check` reports `I001`.
- **Fix**: `ruff check --fix src/`.
- **Linter rule**: `I001`.

### LOW: Deprecated `Tuple` type hint

- **Severity**: low
- **Kind**: lint
- **Where**: `src/components/service_mesh_component.py:4`
- **Evidence**: `from typing import Tuple`, `-> Tuple[str, str]`; ruff flags `UP035`/`UP006`.
- **Fix**: `ruff check --fix src/components/service_mesh_component.py`.
- **Linter rule**: `UP035`, `UP006`.

### LOW: Unused `# noqa: E501`

- **Severity**: low
- **Kind**: lint
- **Where**: `src/components/pebble_component.py:40`
- **Evidence**: `ruff check` reports `RUF100` — `E501` isn't part of the ruff config, so the noqa is dead.
- **Fix**: Remove the comment.
- **Linter rule**: `RUF100`.

### NIT: Deprecated `Harness` in unit tests

- **Severity**: nit
- **Kind**: test-gap
- **Where**: `tests/unit/test_operator.py:15`
- **Evidence**: `harness = Harness(PvcViewer)`; emits `PendingDeprecationWarning`. `ops` docs recommend `Context`/`State` from `ops.testing`.
- **Fix**: Migrate to `Context`/`State` (mechanical migration).
- **Linter rule**: not established.

### NIT: Bundled `loki_k8s` library uses deprecated API

- **Severity**: nit
- **Kind**: maintainability
- **Where**: `lib/charms/loki_k8s/v1/loki_push_api.py:2436`
- **Evidence**: `JujuVersion.from_environ()` is deprecated in favor of `self.model.juju_version`; emits a `DeprecationWarning` on every charm start.
- **Fix**: Update the bundled library once a fixed release is available.
- **Linter rule**: not in the charm's lint suite.

## Worth copying

- **`CharmReconciler` pattern** (`src/charm.py`): components registered in a dependency graph with explicit `depends_on`; `install_default_event_handlers()` wires all hooks — cleaner than a decorator forest. `LeadershipGateComponent` correctly gates non-leader units to `waiting` via Pebble.
- **`StoredState` for certs**: generated once, idempotent across restarts; regenerates all certs if any attribute is missing (blunt but correct).
- **Status precedence** (`service_mesh_component.py`): `BlockedStatus` for inconsistent relation state (service-mesh present, gateway-metadata missing) is actionable for operators.
- **Pebble layer as pure data** (`pebble_component.py`): `get_layer()` is a pure function returning a `Layer` dict — trivially testable.
- **`test_service_mesh_component_modes` parametrised test**: covers sidecar and ambient modes in one function.
- **`test_pvcviewer_example` with retry**: 600s wait / 10s interval, appropriate for a real k8s workload behind Istio.
- **`test_container_security_context`**: verifies actual container UID/GID via `lightkube` — a strong integration test.
- **`PvcViewerInputs` dataclass**: clean separation of config from Pebble layer definition.
- **`certwatcher` graceful rotation**: cert-file removal on scale-down is handled without downtime or crash.

## Common-practice notes

- Follows the modern Kubeflow charms pattern: `charmed-kubeflow-chisme` for components/reconciler, `lightkube` for k8s resources, `ops` for the framework.
- `lib/` bundles full copies of `grafana_k8s`, `istio_beacon_k8s`, `loki_k8s`, `observability_libs`, `prometheus_k8s` — larger bundle, more reproducible.
- `observability_libs v1` is the deprecated version; its stated removal date (October 2025) has already passed.
- Certificate generation uses raw `subprocess.check_call` to OpenSSL, standard for charms; CN hardcoded to `127.0.0.1` — fine for self-signed internal TLS.
- `metadata.yaml` absent, auto-generated by `charmcraft.yaml` — normal for modern charms.
- `terraform/README.md` exists but the `terraform/` module directory does not — the module is managed elsewhere or missing.
- Ruff catches issues (deprecated `Tuple`, unused noqa, try/except anti-patterns) that the project's own `tox -e lint` (pflake8+isort+black+codespell) does not.
- No custom config options — all configuration via relations, a deliberate design choice, not a gap.

## Tests

| Suite | Location | Run | Result |
|---|---|---|---|
| Unit | `tests/unit/test_operator.py` | `PYTHONPATH=src:lib pytest -v` | 15/15 pass in 7.5s, 93% coverage |
| Integration | `tests/integration/test_charm.py` | not run (requires k8s cluster + Istio) | — |
| Integration (ambient) | `tests/integration/test_charm_ambient.py` | not run | — |
| Lint (pflake8+isort+black+codespell) | `src/`, `tests/` | `tox -e lint` | pass |
| Lint (ruff) | `src/`, `tests/` | `ruff check src/ tests/` | 11 errors |

Integration tests (`test_charm.py`) deploy with `istio-pilot`, `istio-gateway`, `grafana-agent-k8s`, and cover metrics, logging, alert rules, the PVCViewer CRD example, container security context, and application removal — all with `trust=True`, which masks the RBAC bug above. `test_charm_ambient.py` tests ambient-mesh mode via `charmed_kubeflow_chisme.testing`'s `deploy_and_integrate_service_mesh_charms()`, also with `trust=True`; its `test_remove_deletes_virtual_service` would be expected to fail in a multi-model environment given the cluster-scoped resource collision described above.

## Docs

- `README.md` — adequate: describes what the charm does, relation endpoints, config, deployment examples. Does not document the `service-mesh`/`gateway-metadata` dual-relation model, and **does not mention the `trust=True` requirement**.
- `CONTRIBUTING.md` — minimal but functional.
- `terraform/README.md` — describes a module that isn't present in the repo.
- Charmhub description accurate and matches observed behaviour.

## Open questions

1. Should `trust=True` remain the answer, or should the charm self-declare cluster-scoped permissions via `juju-app-access` in `metadata.yaml`? The latter avoids granting full cluster-admin for what is a narrower set of needs.
2. Is the ambient-mesh integration test in `test_charm_ambient.py` actually exercised in CI, or always skipped (it's marked `skip_if_deployed`)?
3. `ServiceMeshComponent._configure_app_leader` creates an Istio `AuthorizationPolicy`, which also needs cluster-scoped create permission — another reason `trust` is currently required; unclear if this is covered by the same fix as the CRD-list gap.
4. Should the cluster-scoped label collision be fixed in this charm's templates, or upstream in `charmed_kubeflow_chisme`'s `create_charm_default_labels` (shared by other Kubeflow charms)?
5. Why did the `stop` hook fail to fire before "unit is dead" during removal — Juju k8s-substrate timing, or something charm-side? Reproducing reliably would need a cleaner test environment.
