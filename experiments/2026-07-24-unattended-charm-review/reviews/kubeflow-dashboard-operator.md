# kubeflow-dashboard-operator

A k8s charm wrapping the Kubeflow Central Dashboard Node.js workload. It exposes
relation endpoints for sidebar links, metrics, grafana dashboards, and cross-model
mesh, and requires `kubeflow-profiles`, Istio ingress, and (optionally) a service
mesh. It ships a `KubeflowDashboardLinksProvider` library (LIBID
`635fdbfc0fcc420882835d4c0086bb5d`, v0.3) that lets related apps register sidebar
links dynamically.

**Verdict:** the happy path (deploy, relate to kubeflow-profiles, serve the
dashboard) works and is well-tested, but the charm does not react to change after
initial setup. Every port-dependent resource (k8s Service, Pebble layer,
`MetricsEndpointProvider`, `KubernetesServicePatch`) is frozen at `__init__` and
never re-evaluated on `config-changed`, so changing the `port` config is a no-op
in practice. The charm also does not observe `relation-broken` for its required
`kubeflow-profiles` relation, so it reports `active` while running against a
dead dependency. Removal — both normal and forced — leaves orphaned
ClusterRoles/ClusterRoleBindings in the cluster, including a Juju-created
ClusterRole with unrestricted `*/* -> *` permissions. A maintainer should fix the
`self._port` caching and the missing `relation-broken` observers first (both are
one-line-ish changes with outsized impact), then address the `_on_remove`
ApiError handling before this charm sees any more production churn.

| | |
|---|---|
| Repo | canonical/kubeflow-dashboard-operator @ `e6b1d7c` (2026-06-22) |
| Charms | kubeflow-dashboard (k8s), kubeflow-dashboard-requirer-mock (machine, test-only) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4, `1.10/edge` rev 996 |
| Reviewed | 2026-08-20 |

## What it does

Deploys a single-container Node.js workload (OCI image
`charmedkubeflow/centraldashboard`) behind a ClusterIP service, creates a
ClusterRole/ClusterRoleBinding, and manages a ConfigMap holding the dashboard's
sidebar link configuration. It integrates with Istio ambient or sidecar ingress,
provides Prometheus/Grafana/Loki endpoints, and exposes a `links` relation that
other charms use to inject sidebar links.

## Findings

### `_port` captured at init, never updated — root cause of port-config bugs
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:92` (`self._port = int(self.model.config["port"])`),
  `src/charm.py:95-101` (`MetricsEndpointProvider`), `src/charm.py:103`
  (`KubernetesServicePatch`), `src/charm.py:205-219` (pebble layer `_context`)
- **Evidence**: All four port-dependent resources are built from `self._port` in
  `__init__`, set once and never re-read. `config-changed` fires (confirmed via
  `juju debug-log`) but nothing re-evaluates the port. `juju config port=9090`
  followed by `juju show-unit` still shows `scrape_jobs` targeting `*:8082`;
  `kubectl get service kubeflow-dashboard` still shows port 8082; the pebble
  layer env is unchanged. The `ingress` relation data sent to `istio-pilot` also
  showed the stale port 8082 after a config change, confirming the bug
  end-to-end. Confirmed by open issue #202.
- **Impact**: Operators cannot change the dashboard port at runtime. Prometheus
  scrapes the wrong port, the k8s Service exposes the wrong port, and the Istio
  ingress relation advertises the wrong port — while the charm reports `active`.
- **Fix**: Remove the cached `self._port`; read `int(self.model.config["port"])`
  at each use site (or re-cache inside `main()` on every call). Pass
  `refresh_event=[self.on.config_changed]` to `KubernetesServicePatch`.
- **Linter rule**: not mechanically checkable without an integration test
  asserting k8s Service port, pebble layer, and scrape targets match
  `juju config`.

### Normal `remove-application` leaves a `*/* -> *` ClusterRole orphaned
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:389` (`_on_remove` re-raises `ApiError`)
- **Evidence**: `juju remove-application kubeflow-dashboard` (normal path, 1
  unit) removes the charm, but `kubectl get clusterrole
  kubeflow-kubeflow-dashboard -o yaml` still shows `rules: [{apiGroups: ['*'],
  resources: ['*'], verbs: ['*']}]`. This ClusterRole is created by the Juju
  kubernetes worker (not the charm's template, which creates a ClusterRole named
  `kubeflow-dashboard`). `_on_remove` tries to delete `kubeflow-dashboard`, gets
  a 404, and re-raises the `ApiError` instead of treating it as a no-op. The
  charm's own ServiceAccount (`kubeflow-dashboard`) also persists after removal.
- **Impact**: A ClusterRole with unrestricted cluster-wide permissions is left
  behind with no indication it was created by this charm — a security and
  cluster-hygiene concern that compounds on every remove/redeploy cycle.
- **Fix**: In `_on_remove`, catch `ApiError` and treat a 404 as a no-op:
  `except ApiError as e: if e.status.value != 404: raise`. Document that the
  Juju-created ClusterRole is a Juju/subordinate-worker artifact, cleaned up by
  Juju model destruction, not by the charm.
- **Linter rule**: not mechanically checkable.

### Charm stays `active` when `kubeflow-profiles` relation is removed
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:122-132` (observed events list has no
  `relation-broken` for `kubeflow-profiles`)
- **Evidence**: `juju remove-relation kubeflow-profiles kubeflow-dashboard` →
  charm stays `active`; `kubeflow-profiles-relation-broken` fires on the leader
  (confirmed in `juju debug-log`), but no status update occurs. The pebble layer
  keeps the stale `PROFILES_KFAM_SERVICE_HOST: kubeflow-profiles.kubeflow`.
  Confirmed by open issue #52.
- **Impact**: The charm reports healthy while its required dependency is gone.
  Operators have no signal that the dashboard is broken.
- **Fix**: Add `self.on["kubeflow-profiles"].relation_broken` to the observed
  events list and call `main()` to re-evaluate `_check_kf_profiles`.
- **Linter rule**: not mechanically checkable without a state-transition test.

### `KubernetesServicePatch` never re-patches the service on config change
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:103` (`KubernetesServicePatch(self, [port])`)
- **Evidence**: `lib/charms/observability_libs/v1/kubernetes_service_patch.py`
  accepts a `refresh_event` parameter; it is not passed. `kubectl get service
  kubeflow-dashboard -o yaml` still shows port 8082 after `juju config
  port=9090`.
- **Impact**: The k8s Service never reflects the configured port; the service
  patch is applied once, at startup, only.
- **Fix**: Pass `refresh_event=[self.on.config_changed]` to
  `KubernetesServicePatch`. (Same underlying `self._port` issue as the top
  finding; separate finding because it's a distinct fix point.)
- **Linter rule**: not mechanically checkable without an integration test.

### `KubernetesServicePatch` library deprecated, removal due October 2025
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/observability_libs/v1/kubernetes_service_patch.py`
  (header docstring), `src/charm.py:103`
- **Evidence**: The library docstring states it is "DEPRECATED and will be
  removed in October 2025... `ops.Unit.set_ports` should be used instead."
  Kubeflow-dashboard still depends on it, without `refresh_event`.
- **Impact**: After the library is pulled, the charm will fail to build.
  Even before then, it receives no active maintenance.
- **Fix**: Migrate to `ops.Unit.set_ports()`: remove the
  `KubernetesServicePatch` instantiation, call `self.unit.set_ports()` in
  `main()`, and remove the service-patcher dependency. As an interim step, add
  `refresh_event=[self.on.config_changed]`.
- **Linter rule**: not mechanically checkable without knowing the library's
  deprecation status.

### Istio ingress route config sent only once at startup, never updated
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:112,120` (`_ambient_mesh_ingress` called only in
  `__init__`); `src/charm.py:358-374` (`main` does not call it)
- **Evidence**: `_ambient_mesh_ingress()` runs only in `__init__` under
  `if self.unit.is_leader():`. `main()` never calls it, and
  `istio-ingress-route` is not in the observed events list.
- **Impact**: An Istio ingress related after initial deployment never receives
  the dashboard's `HTTPRoute` config; the gateway won't know how to route to it,
  while the charm shows `active`.
- **Fix**: Add `self.on["istio-ingress-route"].relation_changed` to the
  observed events, and call `self._ambient_mesh_ingress()` inside `main()`.
- **Linter rule**: not mechanically checkable without an integration test.

### `_get_data_from_profiles_interface` raises unhandled `IndexError` on empty relation data
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:355-356`
- **Evidence**: `return
  list(kf_profiles_interface.get_data().values())[0]` — if `get_data()` returns
  `{}`, `[0]` raises `IndexError`, which is not caught by the `except
  CheckFailed` in `main()`. `_check_kf_profiles` checks `not
  kf_profiles.get_data()`, which passes for an empty dict, then
  `_get_data_from_profiles_interface` crashes on the empty list.
- **Impact**: If kubeflow-profiles sends empty relation data before it has
  finished initialising, the charm crashes with a traceback into Error state
  instead of `WaitingStatus`.
- **Fix**: Wrap the access in try/except and raise
  `CheckFailed("Waiting for kubeflow-profiles relation data", WaitingStatus)`
  on `IndexError`.
- **Linter rule**: not mechanically checkable without an integration test
  injecting empty relation data.

### `_on_remove` re-raises `ApiError`, putting the charm in Error state
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:389`
- **Evidence**: `raise e` after logging a warning. Confirmed by open issue #99;
  also the direct cause of the ClusterRole leak above, since a genuine 404
  aborts the rest of the cleanup path.
- **Impact**: Any failure to delete a k8s resource on removal (404 because
  Kubernetes is already GC'ing it, or permission denied) causes an unhandled
  traceback and leaves the application stuck in `Error` instead of completing
  removal cleanly.
- **Fix**: Catch `ApiError`, treat 404 as acceptable (log and continue),
  re-raise everything else.
- **Linter rule**: not mechanically checkable.

### No test for `kubeflow-profiles` `relation-broken`
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/test_operator.py`
- **Evidence**: All tests exercise `relation_changed` or no-relation start-of-life
  scenarios; none removes the relation mid-flight and asserts `BlockedStatus`.
  Confirmed by open issue #52.
- **Fix**: Add `test_check_kf_profiles_relation_broken` that removes the
  relation and asserts `BlockedStatus("Add required relation to
  kubeflow-profiles")`.
- **Linter rule**: not mechanically checkable.

### No test for port config propagating to k8s Service/pebble layer
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/test_operator.py`
- **Evidence**: No test asserts that `juju config port=X` results in the k8s
  Service or pebble layer reflecting `X`. Confirmed by open issue #202.
- **Fix**: Add an integration test that changes the port config and asserts
  the k8s Service port matches `juju config`.
- **Linter rule**: not mechanically checkable.

### No test for `_get_data_from_profiles_interface` with empty/malformed data
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/test_operator.py`
- **Evidence**: No test covers empty relation data from kubeflow-profiles, nor
  a missing `service-name` key.
- **Fix**: Add `test_get_data_from_profiles_interface_empty_data` (patches the
  interface to return `{}`, asserts `CheckFailed`/`WaitingStatus`) and a
  companion test for a missing key.
- **Linter rule**: not mechanically checkable.

### `juju refresh` blocked on newer channels by new `juju-info` endpoint
- **Severity**: medium
- **Kind**: ux
- **Where**: `charmcraft.yaml` (rev 1005/1006 add a `juju-info` provides
  endpoint)
- **Evidence**: `juju refresh kubeflow-dashboard --channel latest/edge` (from
  the deployed rev 996) fails: "one or more of the provided endpoints do not
  exist." `2.0/edge` (rev 1006) fails the same way. Both add a subordinate
  `juju-info` provides endpoint; the current model has no principal charm to
  consume it.
- **Impact**: Operators cannot upgrade through `juju refresh` to any newer
  channel without deploying an additional consumer charm — significant upgrade
  friction.
- **Fix**: If `juju-info` is intentional, document the upgrade path
  prominently (e.g. required subordinate for COS). If accidental, remove it.
- **Linter rule**: not mechanically checkable.

### `require-cmr-mesh` relation declared but completely unhandled
- **Severity**: medium
- **Kind**: bug
- **Where**: `metadata.yaml` (declares `require-cmr-mesh`, interface
  `cross_model_mesh`); no handling in `src/charm.py`
- **Evidence**: No import, instantiation, or handler exists for this endpoint.
  `ServiceMeshConsumer` handles the separate `service-mesh` relation, not this
  one.
- **Impact**: An operator can relate a charm to `require-cmr-mesh`; Juju
  establishes the relation but the charm neither reads nor sends data over it,
  so cross-model mesh setup silently fails.
- **Fix**: Implement the relation handler, or remove the declaration from
  metadata to avoid misleading operators.
- **Linter rule**: not mechanically checkable without a state-transition test.

### Negative/out-of-range port accepted silently, no validation
- **Severity**: medium
- **Kind**: bug
- **Where**: `config.yaml` (no `min`/`max`), `src/charm.py:92`
- **Evidence**: `juju config port=-1` and `juju config port=65536` are both
  accepted by Juju (int type, no range constraint) and the charm stays
  `active`; the k8s Service port stays unchanged (8082) in both cases. A string
  port (`port=notanumber`) is correctly rejected by the Juju CLI. `port=99999`
  briefly showed `maintenance` ("Creating k8s resources") before recovering to
  `active`.
- **Impact**: Misconfiguration gets no feedback; invalid values reach the
  pebble layer while the charm reports healthy.
- **Fix**: Add `min: 1, max: 65535` to the `port` option in `config.yaml`, or
  add in-charm validation raising `CheckFailed(BlockedStatus)` on an
  out-of-range value.
- **Linter rule**: `charmcraft validate` with range constraints.

### `ingress-relation-broken` not observed — sidecar ingress removal ignored
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:122-132` (`ingress` observed only for
  `relation_changed`)
- **Evidence**: `juju remove-relation istio-pilot kubeflow-dashboard` fires
  `ingress-relation-broken` (confirmed in `juju debug-log`), but the charm's
  status tracking does not react — it stays `active`. `KubernetesServicePatch`
  itself observes all events by default and would clean up its own patch, but
  the charm's own checks are unaffected.
- **Impact**: If the sidecar ingress is removed, the charm doesn't re-evaluate
  status or take any compensating action.
- **Fix**: Add `self.on["ingress"].relation_broken` to the observed events and
  call `main()`.
- **Linter rule**: not mechanically checkable without an integration test.

### `configmap_handler` uses the wrong lightkube client for generic resources
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:197`
- **Evidence**: `load_in_cluster_generic_resources(self.k8s_resource_handler.lightkube_client)`
  should read `self._configmap_handler.lightkube_client`. The `configmap_handler`'s
  own client never gets generic resources loaded.
- **Impact**: Latent bug — only manifests if ConfigMap creation involves
  unregistered CRDs, at which point the client may not recognise them.
- **Fix**: Change line 197 to use `self._configmap_handler.lightkube_client`.
- **Linter rule**: not mechanically checkable.

### tox lint env does not run `ruff` or `pyright`
- **Severity**: medium
- **Kind**: test-gap / lint
- **Where**: `tox.ini:lint`, `pyproject.toml`
- **Evidence**: `tox -e lint` runs `pflake8`, `isort --check-only`,
  `black --check` only. `ruff check src/ lib/` separately finds 335 errors (272
  fixable): `src/charm.py` has unused `noqa` directives (RUF100), unsorted
  imports (I001), bare exception catch (BLE001), `next(iter())` preferred
  (RUF015); `src/dashboard_links.py` has deprecated `typing.List` and bare
  exception catches; bundled libraries (mainly `prometheus_scrape.py`) account
  for 329 of the 335 issues. `pyright src/charm.py src/dashboard_links.py`
  finds 8 type errors.
- **Impact**: CI lint passes today but would fail under a modern lint stack;
  type errors and stylistic debt accumulate unnoticed.
- **Fix**: Add `ruff check src/ lib/` and `pyright src/charm.py
  src/dashboard_links.py` to the `lint` tox environment.
- **Linter rule**: mechanically checkable — `ruff check src/` and `pyright`.

### Integration test deps pin `juju < 4.0`, but live deployment used Juju 4.0.12
- **Severity**: medium
- **Kind**: test-gap / env-mismatch
- **Where**: `pyproject.toml` (`juju = "<4.0"` in the integration test group)
  vs `concierge.yaml` (`juju.channel: 3.6/stable`)
- **Evidence**: The concierge target is Juju 3.6, matching the pinned test
  dependency. This review's live deployment ran on concierge-k8s-4 (Juju
  4.0.12) instead. No Juju 4.x-specific issues were observed during the review,
  but CI never exercises Juju 4.x.
- **Impact**: CI cannot catch Juju 4.x-specific regressions even though
  production deployments (per this review) run on Juju 4.x.
- **Fix**: Add a Juju 4.x concierge target, or explicitly document that the
  charm is validated against Juju 3.x only.
- **Linter rule**: not mechanically checkable.

### README bug-report URL points to the wrong repo
- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md`, last paragraph
- **Evidence**: "If you find a bug... please file a bug here:
  `https://github.com/canonical/dex-auth-operator/issues`" — that's the
  dex-auth operator, not kubeflow-dashboard.
- **Fix**: Replace with
  `https://github.com/canonical/kubeflow-dashboard-operator/issues`.
- **Linter rule**: not mechanically checkable.

### Charm goes to `maintenance` (not `blocked`) on pod restart without kubeflow-profiles
- **Severity**: medium
- **Kind**: bug / ux (unverified root cause)
- **Where**: observed at runtime; root cause not established in the code
- **Evidence**: After `kubectl delete pod` while the `kubeflow-profiles`
  relation was absent, `juju status` showed `maintenance` with no message for
  both app and unit, instead of the expected `BlockedStatus("Add required
  relation to kubeflow-profiles")` from `_check_kf_profiles`/`CheckFailed`. The
  charm recovered to `active` once the relation was restored.
- **Impact**: An operator restarting a pod while the relation is absent gets a
  confusing, non-actionable `maintenance` status instead of a clear `blocked`
  message.
- **Fix**: not established — root cause unclear (possible uniter status race
  during hook execution). Add logging around `_on_remove`/status transitions
  to trace it.
- **Linter rule**: not mechanically checkable without more diagnostic data.

### No tests for `ingress-relation-broken` / `_handle_ingress` no-ingress path
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_operator.py`
- **Evidence**: No test removes the `ingress` relation and asserts a status
  change; the no-op branch `if interfaces["ingress"]:` at `src/charm.py:347` is
  untested.
- **Fix**: Add unit tests for `relation-broken` on `ingress` and the no-ingress
  branch of `_handle_ingress`.
- **Linter rule**: not mechanically checkable.

### `test_dashboard_access` asserts against config port, not actual service port
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py::test_dashboard_access`
- **Evidence**: The test builds its request URL from
  `get_config()["port"]["value"]` and never checks the actual port the Node.js
  service or k8s Service is listening on.
- **Impact**: The test provides false confidence — it would pass even if the
  port-config bug (top finding) silently breaks the mapping, as long as the
  default port happens to still work.
- **Fix**: Determine the actual listening port (e.g. `kubectl get service` or
  `pebble services`) and assert against that, not the config value.
- **Linter rule**: not mechanically checkable.

### Kubeflow-profiles `service-port` ignored from relation data
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:372` (`main` uses only `service-name`);
  `src/charm.py:371` (`_get_data_from_profiles_interface`)
- **Evidence**: `juju show-unit kubeflow-profiles/0` shows relation data
  containing `service-port: '8081'`; the charm never reads it, and the pebble
  layer has no `PROFILES_KFAM_SERVICE_PORT` env var.
- **Impact**: The workload relies on both sides defaulting to 8082 rather than
  using the port actually advertised over the relation — currently harmless in
  practice but an incorrect assumption.
- **Fix**: Read `kf_profiles["service-port"]` and set
  `PROFILES_KFAM_SERVICE_PORT` in the pebble environment.
- **Linter rule**: not mechanically checkable without an integration test
  comparing the actual workload port against relation data.

### `LinksProvider` carries a workaround for ops < 2.10 env-var behaviour
- **Severity**: low
- **Kind**: tech-debt
- **Where**: `lib/charms/kubeflow_dashboard/v0/kubeflow_dashboard_links.py:320-337`
- **Evidence**: `get_name_of_breaking_app()` uses the `JUJU_REMOTE_APP` env var
  to identify the departing app on `relation-broken` — a workaround tracked as
  issue #177, for ops versions before 2.10. The charm already depends on ops
  `^2.17.1`.
- **Fix**: Remove `get_name_of_breaking_app` and its uses; verify links are
  correctly omitted from the ConfigMap on relation removal without the
  workaround.
- **Linter rule**: not mechanically checkable.

### No actions defined
- **Severity**: low
- **Kind**: ux
- **Where**: `metadata.yaml`, `src/charm.py`
- **Evidence**: `juju actions kubeflow-dashboard` returns "No actions defined."
- **Impact**: Operators have no operational controls beyond config and
  relations (e.g. no way to fetch the dashboard's external URL directly).
- **Fix**: Add at least a `get-dashboard-url` action.
- **Linter rule**: not mechanically checkable.

### Non-leader units show `waiting`/`Waiting for leadership`
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:356-357` (`_check_leader` raises `CheckFailed` with
  `WaitingStatus`)
- **Evidence**: `juju status` shows `kubeflow-dashboard/1` and `/2` as
  `waiting` ("Waiting for leadership") while `/0` (leader) is `active`; pebble
  service is `inactive` on followers even though `running` in the workload —
  this is expected, only the leader applies the pebble layer.
- **Impact**: Can look alarming to an operator unfamiliar with the charm's HA
  design.
- **Fix**: Document the behaviour clearly, or consider surfacing `ActiveStatus`
  for followers once the pebble layer is correctly applied.
- **Linter rule**: not mechanically checkable.

### Pyright: 8 type errors in charm source
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py`, `src/dashboard_links.py`
- **Evidence**: `pyright src/charm.py src/dashboard_links.py` reports issues
  including: `charm.py:68` `None` cannot be called (`self._container`);
  `charm.py:197` wrong attribute access (see finding above); `charm.py:228`
  layer dict type mismatch; `charm.py:255/257` exception type passed to
  `CheckFailed`; `charm.py:349/350` config values typed `bool | int | float |
  str` used as `str`; `dashboard_links.py:125` return type `list | tuple` vs
  `List[str]`.
- **Fix**: Fix type annotations and/or add targeted `type: ignore` comments.
- **Linter rule**: `pyright`.

### Import block in `src/charm.py` unsorted
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:5-41`
- **Evidence**: `ruff check src/` reports `I001` on the
  `serialized_data_interface` import.
- **Fix**: Run `isort` on `src/charm.py`.
- **Linter rule**: `ruff` rule I001.

### `parse_dashboard_link_order` catches bare `Exception`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/dashboard_links.py:112`
- **Evidence**: `except Exception as err:` also catches `KeyboardInterrupt`/
  `SystemExit`/`MemoryError`. `ruff check src/` reports BLE001.
- **Fix**: Catch `yaml.YAMLError` specifically.
- **Linter rule**: `ruff` rule BLE001.

### `next(iter(...))` preferred over single-element slice
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:356`
- **Evidence**: `ruff check src/` reports RUF015.
- **Fix**: `return next(iter(kf_profiles_interface.get_data().values()))`.
- **Linter rule**: `ruff` rule RUF015.

### Unused `# noqa E501` directives
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:57`, `src/charm.py:220`
- **Evidence**: `ruff check src/` reports RUF100 on both lines.
- **Fix**: Remove the `# noqa E501` suffix from both lines.
- **Linter rule**: `ruff` rule RUF100.

### Bundled `prometheus_scrape` library carries 272 ruff-fixable issues
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/prometheus_k8s/v0/prometheus_scrape.py`
- **Evidence**: `ruff check` finds 272 fixable issues in this bundled library:
  deprecated `typing.List/Dict/Tuple/Optional`, `.format()` calls instead of
  f-strings, mutable class attributes, and more.
- **Impact**: Technical debt in a bundled (not charm-authored) library; will
  eventually break under stricter Python typing.
- **Fix**: Submit a fixup upstream to the `prometheus-k8s` library, or wait for
  maintainers to modernise it. Not primarily this charm team's responsibility.
- **Linter rule**: `ruff check lib/`.

### Stale `DEFAULT_RESOURCE_FILES` test constant references removed template
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_operator.py:51-56`
- **Evidence**: `DEFAULT_RESOURCE_FILES` lists `profile_crds.yaml.j2`,
  `auth_manifests.yaml.j2`, `configmaps.yaml.j2`, but
  `K8S_RESOURCE_FILES` in `src/charm.py:43-45` is only
  `["src/templates/auth_manifests.yaml.j2"]`. `profile_crds.yaml.j2` was
  removed in commit `32935a2` and the test constant was never updated. The
  constant is dead code (unused outside a comment) but misleads readers.
- **Fix**: Remove the constant or update it to match `K8S_RESOURCE_FILES`.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **`CheckFailed` exception pattern** (`src/charm.py:62-68`): carries both a
  message and a status type; used consistently in `main` to set status before
  returning, cleaner than inlining status logic per error branch.
- **Status precedence in `main`** (`src/charm.py:358-374`): all checks run in
  one try/except so the first failure determines the status — no cascading
  status clobbering.
- **Pebble layer diff check** (`src/charm.py:241-249`): `_update_layer`
  compares `current_layer.services != new_layer.services` before calling
  `add_layer`, avoiding unnecessary pebble reloads.
- **ConfigMap template** (`src/templates/configmaps.yaml.j2`): Jinja2 renders
  the links JSON, keeping the template language-agnostic and readable.
- **`istio_ingress_route.py` library handles `relation-broken`** (line 833):
  observes `relation_broken`, clears stored state, and emits `ready` — the
  correct pattern that kubeflow-dashboard's own required relations should
  follow but don't.
- **`ServiceMeshConsumer` (istio_beacon_k8s) handles `relation-broken`**
  (`service_mesh.py:382`): correctly clears pod labels on mesh relation break.
- **`LogForwarder` (loki_push_api)**: observes both `relation_changed` and
  `relation_broken`; pebble `log-targets` (with Loki endpoint and Juju
  topology labels) are configured correctly in this charm.
- **Terraform module** (`terraform/`): present, documented, exports
  `provides`/`requires` maps for composition.
- **Integration test dashboard assertions** (`tests/integration/test_charm.py`):
  use `lightkube.Client` to read the ConfigMap directly from the cluster and
  assert on link content — stronger than a status-only check.
- **CONTRIBUTING.md**: documents the poetry workflow, tox environments, and
  the `charm` poetry group vs project dependencies distinction clearly.

## Common-practice notes

| Area | Status |
|---|---|
| ops framework version | `^2.17.1` — current at review time |
| Python version | `>=3.12` — ahead of most charms (3.10/3.11 common) |
| `charmcraft.yaml` parts layout | Poetry plugin, rustup, uv — modern |
| `lib/charms/` layout | v0 only, single lib — fine for this charm |
| Observes `config_changed` | Yes — but see port-caching findings |
| Observes `relation_broken` for kubeflow-profiles | No |
| Observes `relation_broken` for ingress | No |
| Observes `relation_changed` for istio-ingress-route | No (handled once at init only) |
| Observes `relation_broken` for istio-ingress-route | Handled by library |
| Uses deprecated library | `KubernetesServicePatch` — deprecated Oct 2025 |
| Handles `require-cmr-mesh` relation | No — declared but unhandled |
| Juju 3.x tested | Yes — via concierge |
| Juju 4.x tested | Yes — live deployment (concierge-k8s-4, Juju 4.0.12) |
| Upgrade path (refresh) | Blocked: rev 1005/1006 add `juju-info` endpoint |
| Unit test harness | `ops.testing.Harness` — works, 47 tests pass |
| `charm-user: non-root` | Correctly set in `metadata.yaml` |
| CI with concierge | Uses concierge for k8s integration tests |
| `juju` in integration deps | `<4.0` — Juju 3.x only, but review deployed on 4.x |

**Drift from convention:**
- README.md "Bugs and feature requests" points to `dex-auth-operator/issues`.
- `tox.ini` lint env runs only `pflake8`/`isort`/`black` — no `ruff`/`pyright`.
- `LinksProvider` library ships a workaround for ops < 2.10 (issue #177) no
  longer needed given the ops `^2.17.1` dependency.
- Integration tests pin `juju < 4.0` while production use (per this review) is
  on Juju 4.x.
- Uses deprecated `KubernetesServicePatch` instead of `ops.Unit.set_ports`.
- Bundled `prometheus_scrape` library carries 272 ruff-fixable issues.

## Tests

**Unit tests (47, all pass):**
```
PYTHONPATH=$(pwd):$(pwd)/lib:src poetry run pytest tests/unit -v
======================= 47 passed, 46 warnings in 0.83s =======================
```
Coverage via `tox -e unit`:
```
Name                     Stmts   Miss Branch BrPart  Cover   Missing
src/charm.py               196     19     30      4    88%   172-180, 184, 188-196, 200, 254-257, 262, 329, 338-339, 390
src/dashboard_links.py      56      5     16      1    92%   112-114, 122-123
TOTAL                      252     24     46      5    89%
```
The uncovered lines are exactly the operationally critical paths: the
`_deploy_k8s_resources` failure path, `_handle_ingress` with no ingress,
`_update_layer` failure, `_get_interfaces`, `_check_leader` failure, and
`_on_remove`.

**Integration tests (`test_charm.py`):** exercise the full deploy + relate
lifecycle via `pytest-operator`, with meaningful assertions (ConfigMap
content, HTTP response, metrics endpoint presence). `test_dashboard_access`
uses the config port value rather than the actual service port (see finding).
No test checks charm status after relation removal or verifies config changes
propagate to k8s resources.

**Integration tests (`test_charm_ambient.py`):** same suite with Istio ambient
mesh; adds HTTPRoute-attachment assertions and a
`test_deploy_and_relate_second_ingress` test for multiple
`istio-ingress-route` relations. Requires L2 load-balancer networking and a
real Istio install — cannot run on a generic k8s cluster. Integration tests
were not run locally for this review (require the full concierge
environment).

**Lint (`tox -e lint`):** runs `pflake8`, `isort --check-only`,
`black --check` only — would not catch ruff/pyright findings.
`ruff check src/ lib/` finds 335 total errors (272 fixable):
- `src/charm.py` (6 issues): unsorted imports (I001), unused noqa (RUF100),
  `.format()` vs f-string (UP032), `next(iter())` preferred (RUF015), bare
  `raise` (TRY201)
- `src/dashboard_links.py` (5 issues): deprecated `typing.List` (UP006), bare
  `Exception` catch (BLE001), unsorted imports (I001)
- `prometheus_scrape.py` (272 issues, all fixable): deprecated typing, string
  formatting, mutable class attributes, bare `Exception` raise
- `kubernetes_service_patch.py`: 3 unused noqa directives (RUF100)
- `loki_push_api.py`, `grafana_dashboard.py`, `service_mesh.py`: fewer issues
- `kubeflow_dashboard_links.py`: 1 unused noqa (RUF100)

`pyright src/charm.py src/dashboard_links.py` finds 8 type errors, all missed
by the tox lint environment. `tox -e fmt` (isort + black) passes cleanly.

## Docs

- **README.md**: substantial (180 lines), covers sidebar link management via
  both relation and config; usage section matches observed behaviour. The
  "What's included in Charmed Kubeflow 1.4" section is stale (charm tracks
  1.10). Bug-report URL is wrong (see finding).
- **CONTRIBUTING.md**: documents the poetry workflow and tox environments
  clearly.
- **Terraform README**: accurate, covers inputs, outputs, and both
  `juju_model` resource/data-source usage patterns.
- **Charmhub description**: "Kubeflow Central Dashboard" — minimal.
- **docs/** directory: does not exist.

## Deployment log

```bash
# Deployed from charmhub: kubeflow-dashboard 1.10/edge rev 996
juju add-model kubeflow --controller concierge-k8s-4
juju deploy kubeflow-dashboard --channel 1.10/edge --trust -m kubeflow
juju deploy kubeflow-profiles --channel 1.10/edge --trust -m kubeflow
juju relate kubeflow-profiles kubeflow-dashboard -m kubeflow
# Status settled to active in ~4 minutes
```

Lifecycle events observed:
- `install` → `leader-elected` → `pebble-ready` → `config-changed` → `start`,
  all fired while the charm was `blocked` waiting for kubeflow-profiles
- After relation creation: `relation-created` → `relation-joined` →
  `relation-changed` (twice, with a transient `waiting` state)
- Pebble layer applied: service started, `npm start` running on port 8082
- ConfigMap created with correct links, ClusterRole + ClusterRoleBinding
  applied
- Service port 8082 confirmed, HTTP 200 from within cluster

### Config-change test (port=9090)

```bash
juju config kubeflow-dashboard port=9090
# config read back as 9090 ✓
# k8s Service port → 8082 (unchanged) ✗
# pebble layer env PROFILES_KFAM_SERVICE_HOST → kubeflow-profiles.kubeflow (unchanged) ✗
# charm remained active (no error)
# metrics scrape_targets → *:8082 (unchanged, confirmed from relation data)
```
`config-changed` fires (confirmed via `juju debug-log`) but neither the k8s
Service port, the pebble layer, nor the `MetricsEndpointProvider` scrape
targets are updated.

### Relation-remove test (kubeflow-profiles)

```bash
juju remove-relation kubeflow-profiles kubeflow-dashboard
# kubeflow-profiles-relation-broken fires on leader (confirmed in debug-log)
# charm status → active ✗ (should be blocked)
# pebble env PROFILES_KFAM_SERVICE_HOST → kubeflow-profiles.kubeflow (stale) ✗
```

### Relation re-add test

```bash
juju relate kubeflow-profiles kubeflow-dashboard
# charm status → active ✓
# pebble env PROFILES_KFAM_SERVICE_HOST → kubeflow-profiles.kubeflow ✓
```

### Failure injection — workload kill

```bash
kubectl exec kubeflow-dashboard-0 -c kubeflow-dashboard -- pkill -f "node dist/server"
# pebble service → backoff
# pebble auto-restart within ~5s
# EADDRINUSE in old process logs (expected)
# charm stayed active throughout
```

### Failure injection — invalid port config

```bash
juju config kubeflow-dashboard port=-1
# Juju accepts -1 (type is int, no range check)
# charm stays active ✗ — no validation

juju config kubeflow-dashboard port=99999
# charm → maintenance "Creating k8s resources" briefly
# then recovers to active ✓ (but k8s service port still 8082)
```

### Scale test (1 → 3 units)

```bash
juju add-unit kubeflow-dashboard -n 2
# all 3 units active within ~3 min
# pebble active on leader, inactive on followers
# grafana-agent-k8s receives scrape targets for all 3 unit IPs
```

### Grafana-agent-k8s integrations

```bash
juju deploy grafana-agent-k8s --channel 2/stable --trust -m kubeflow
juju integrate grafana-agent-k8s:metrics-endpoint kubeflow-dashboard
juju integrate grafana-agent-k8s:logging-provider kubeflow-dashboard
juju integrate kubeflow-dashboard:grafana-dashboard grafana-agent-k8s
# metrics: all 3 units scraped at *:8082 ✓ (port from init-time config)
# logging: pebble log-targets configured with grafana-agent Loki endpoint ✓
# dashboards: LZMA templates with Juju topology served in relation ✓
# grafana-agent-k8s blocked: missing cloud config (external COS, not a charm bug)
```

### Links relation test

```bash
# Deployed kubeflow-dashboard-requirer-mock (machine charm, test charm)
# Related it to kubeflow-dashboard:links
# Mock charm failed on install (machine charm on k8s model — expected)
# Links relation data confirmed via kubeflow-dashboard:links relation data
# ConfigMap correctly aggregated links from relation + defaults
```

### Istio ingress integration attempt

```bash
juju deploy istio-ingress-k8s --channel 1/edge --trust -m kubeflow
juju relate istio-ingress-k8s:ingress kubeflow-dashboard:ingress
# istio-ingress-k8s went to error (hook failed: "leader-elected")
# kubeflow-dashboard/0 did not receive ingress-relation-changed (relation joining)
# istio-ingress-k8s later removed; kubeflow-dashboard stayed active throughout
```
The charm supports both `istio-ingress-route` (ambient mesh, via
`IstioIngressRouteRequirer`) and `ingress` (sidecar); they are mutually
exclusive (`_check_istio_relations`).

### `juju refresh` attempt

```bash
juju refresh kubeflow-dashboard --channel latest/edge
# latest/edge = rev 1005; currently deployed = rev 996
# ERROR: "one or more of the provided endpoints [...] do not exist"
# latest/edge adds juju-info provider endpoint (subordinate interface)
# The upgrade requires a principal charm for juju-info in the model
```

### `juju remove-application` — executed (normal path, 1 unit)

```bash
juju remove-unit -m kubeflow --num-units 2 kubeflow-dashboard
juju remove-application -m kubeflow kubeflow-dashboard
# charm removed from model ✓
# kubectl get clusterrole | grep kubeflow-dashboard
# kubeflow-kubeflow-dashboard  (Juju-created, persists) ✗
# kubectl get clusterrolebinding | grep kubeflow-dashboard
# kubeflow-kubeflow-dashboard  (Juju-created, persists) ✗
# kubectl -n kubeflow get serviceaccount | grep kubeflow-dashboard
# kubeflow-dashboard  (charm-created SA, persists) ✗
```
The charm's template creates ClusterRole `name: kubeflow-dashboard`. Juju's
kubernetes worker separately creates `kubeflow-kubeflow-dashboard` with
`*/* -> *` permissions. The charm's `_on_remove` renders manifests with name
`kubeflow-dashboard`, issues a 404 delete against that name, and re-raises
`ApiError` — leaving both the Juju-created wildcard-permission ClusterRole and
the charm's own ServiceAccount orphaned.

### Forced removal — ClusterRole leak (mock charm)

```bash
# Deployed kubeflow-dashboard-requirer-mock (machine charm)
# Related to kubeflow-dashboard:links
# Force-removed the mock charm with juju remove-application --force
# Result: ClusterRole, ClusterRoleBinding, Service for the mock persist
# kubectl get clusterrole | grep requirer-mock → still present ✗
# kubectl get clusterrolebinding | grep requirer-mock → still present ✗
# kubectl -n kubeflow get service | grep requirer-mock → still present ✗
```

### `istio-pilot` via `ingress` relation — stale port confirmed

```bash
juju deploy istio-pilot --channel latest/edge --trust -m kubeflow
juju relate istio-pilot:ingress kubeflow-dashboard:ingress
# istio-pilot active ✓; relation established ✓
juju show-unit kubeflow-dashboard/0  →  port: 8082  ← STALE
# (config was set to port=9090 in an earlier test)
```
This confirms the port bug end-to-end: kubeflow-dashboard sends `port: 8082`
in its `ingress` relation data via `_handle_ingress()` (`src/charm.py:348`),
which uses `self._port` captured at `__init__`. After relation removal
(`juju remove-relation istio-pilot kubeflow-dashboard`),
`ingress-relation-broken` fires on `kubeflow-dashboard/0` but the charm stays
`active` (no `ingress-relation-broken` observer — see finding).

## Observed behaviour

| Metric | Value |
|---|---|
| Memory (pod) | 133 MiB |
| CPU (pod) | ~4 mCPU |
| Time to active (cold) | ~4 min |
| `relation-broken` on kubeflow-profiles | fires, no status update |
| Pebble service | `npm start`, port 8082, `active` |
| Pebble log forwarding | Configured correctly (`log-targets`, Loki endpoint, Juju topology labels) |
| Metrics scraping | All 3 units scraped at `*:8082` via grafana-agent |
| Grafana dashboards | 3 LZMA templates served via `grafana-dashboard` relation |
| Prometheus scrape targets | `*:8082` (stale, from init-time port) |
| Negative port config | Accepted silently, charm stays `active` |
| Port 0 config | Accepted silently, charm stays `active`, k8s service port stays 8082 |
| Port 65536 config | Accepted silently, charm stays `active` |
| Port as string | Properly rejected by Juju ("expected int, got string") |
| Out-of-range port (99999) | `maintenance` briefly, recovers to `active` |
| Workload crash + recovery | Pebble backoff → auto-restart, ~5s |
| Pod restart without kubeflow-profiles relation | Charm goes to `maintenance` (no message); recovers to `active` when relation restored |
| Non-leader pebble service | `inactive` while workload is `running` — expected |
| Scale-up to 3 units | All up; pebble active on leader, inactive on followers |
| Scale-down to 1 unit | Clean, all units removed |
| Kubeflow-profiles relation removed | Charm stays `active`; pebble env stale (no `relation-broken` observer) |
| Normal `remove-application` | Juju-created ClusterRole `*/* -> *` persists; charm SA orphaned; `_on_remove` 404s on wrong ClusterRole name |
| Forced removal | ClusterRoles/ClusterRoleBindings leaked for removed charms |
| Actions | None defined (`juju actions kubeflow-dashboard` → empty) |
| istio-ingress-k8s integration | charm went to error (leader-election failure) |
| `istio-pilot` via `ingress` | Established; sends stale port 8082 in ingress data |
| `istio-pilot` relation removed | Charm stays `active` (no `ingress-relation-broken` observer) |
| `juju refresh` (1.10/edge → latest/edge) | blocked: rev 1005 adds `juju-info` (subordinate) not satisfiable |
| `juju refresh` (1.10/edge → 2.0/edge) | also blocked by rev 1006 adding `juju-info` |
| Logging via grafana-agent-k8s | Pebble log-targets correctly configured; handled properly on relation removal by LogForwarder library |
| kubeflow-profiles alone | Goes to `active` alone; requires `logging` (loki_push_api) to go active |
| `tox -e unit` | 47 passed, 88% statement coverage on src/charm.py |
| `tox -e fmt` | isort + black, all pass |
| `ruff check src/ lib/` | 335 errors (272 fixable); src/charm.py has 6 issues; libs have 329 issues |
| grafana-agent-k8s relations | Logging, metrics, dashboards all established; grafana-agent-k8s blocked on missing cloud config (external COS issue) |

**Things only visible from running:**
- `KubernetesServicePatch` never re-patches the service on `config-changed`:
  the port in the k8s Service stays 8082 even after `juju config port=9090`
  and `juju config port=9091`.
- kubeflow-profiles requires a `logging` relation (`loki_push_api` interface)
  to go active. Deployed alone without relations, it eventually goes `active`
  anyway; `juju info kubeflow-profiles` confirms `requires: logging:
  loki_push_api`.
- After a pod restart while the `kubeflow-profiles` relation is absent, the
  unit and app status both show `maintenance` with no message rather than the
  expected `BlockedStatus`. Cause not established; the charm does recover to
  `active` once the relation is restored.
- After `juju config port=9091`, the ingress relation data showed `port:
  9091` in one test — because the pod had been killed and restarted, so
  `__init__` re-ran with the then-current config value. In an earlier test
  where the pod was *not* restarted after a port change, the ingress data
  showed the stale port (8082) instead. This confirms the `self._port` capture
  is the mechanism, not per-hook logic.
- `MetricsEndpointProvider` sends `scrape_jobs: [{"metrics_path":
  "/prometheus/metrics", "static_configs": [{"targets": ["*:8082"]}]}]` in the
  `metrics-endpoint` relation data even after `juju config port=9091` —
  locked at the init-time value.
- Pebble `log-targets` are configured correctly once the logging relation is
  established: `type: loki`, correct Loki endpoint, all Juju topology labels
  (`juju_model`, `juju_application`, etc.).
- Grafana dashboards served correctly: `kubeflow_dashboard_nodejs.json`,
  `kubeflow_dashboard_requests_four_signals.json`, and `generic.json` LZMA
  templates all present in the `grafana-dashboard` relation data with correct
  Juju topology.
- `istio_ingress_route` library (`IstioIngressRouteRequirer`) observes
  `relation-broken` internally, clears `external_host`/`tls_enabled` stored
  state, and emits `ready` — handled correctly by the library, unlike the
  charm's own required relations.
- `LogForwarder` (`loki_push_api`) observes both `relation_changed` and
  `relation_broken`.
- `GrafanaDashboardProvider` (`grafana_k8s`) observes only `relation_changed`
  — acceptable since dashboards are informational and need no cleanup.
- The `kubeflow-dashboard-requirer-mock` test charm is a machine charm and
  cannot be deployed on the k8s model itself, limiting live testing of the
  `links` relation.

## Open questions

1. Does `_context` need to call `_get_dashboard_links` on every property
   access (`k8s_resource_handler` and `configmap_handler` both trigger it)?
   Practical impact is negligible (list operations), but it could be
   memoised.
2. Is `profile_crds.yaml.j2` still needed anywhere, or should the stale
   `DEFAULT_RESOURCE_FILES` test constant simply be deleted?
3. Why is `additional-menu-links`'s default `""` while the other
   `additional-*-links` defaults are `'[]'`? Functionally equivalent but
   inconsistent and possibly confusing to operators reading `config.yaml`.
4. Why did grafana-agent-k8s remain `blocked` even after the
   `grafana-dashboard` relation was established — interface version mismatch,
   or an external COS configuration issue unrelated to this charm? (unverified)
5. What is the correct/documented upgrade path from rev 996 to rev 1005/1006,
   given the new `juju-info` endpoint requirement?
6. Is the Juju-created `kubeflow-kubeflow-dashboard` ClusterRole with `*/* ->
   *` permissions a known/expected Juju k8s-worker artifact that gets cleaned
   up on model destruction, or is it itself a leak worth reporting upstream to
   Juju?
7. Should the bundled `prometheus_scrape` library's ruff findings be fixed in
   this charm's copy, or upstream in the `prometheus-k8s` charm library?
8. Should `require-cmr-mesh` be implemented, or removed from `metadata.yaml`
   since it currently has no effect?
