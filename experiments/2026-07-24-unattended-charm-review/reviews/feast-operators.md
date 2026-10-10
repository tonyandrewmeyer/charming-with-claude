# Feast Operators

Feast Operators is a two-charm repository for the Feast feature store on Kubernetes. `feast-ui` is a k8s charm serving the Feast web UI; `feast-integrator` is a machine charm that aggregates PostgreSQL credentials and propagates the feature store configuration both to k8s resources (via `resource-dispatcher`) and to `feast-ui` (via a Juju relation). Both charms use `charmed-kubeflow-chisme`'s `CharmReconciler` pattern well, and the dependency-graph reconciler behaves correctly under refresh, scale, and relation-removal testing. The charm-owned code is ruff-clean and unit tests (22/22 and 25/25) pass, but the code has one real, easily-triggered bug — an unhandled `TypeError` that turns a "missing configuration field" error into an opaque "Failed to compute status" message — plus an architectural gap (feast-ui, a k8s charm, has no k8s-native feast-configuration provider it can be related to for standalone testing), a credentials-over-relation-databag security concern, and a stale `latest/edge` channel missing a TLS fix. A maintainer should first fix the `TypeError` handling in `get_feature_store_yaml()`, since it directly affects operator-facing error messages, then address the `latest/edge` channel gap and consider re-scoping the plaintext credential flow.

| | |
|---|---|
| Repo | canonical/feast-operators @ 793aeef (2026-07-10) |
| Charms | feast-ui (k8s), feast-integrator (machine), configuration-requirer-tester (test-only) |
| Substrate | k8s (feast-ui) / machine (feast-integrator) |
| Deployed | yes — concierge-k8s-4 (feast-ui rev 172 `latest/edge` after refresh, and rev 173 `0.49/edge`, scaled 1→4→1 units), concierge-k8s-3 (feast-ui rev 173 `0.49/edge`, Juju 3.6), concierge-lxd-4/concierge-lxd (feast-integrator rev 200→201 via refresh, `configuration-requirer-tester` rev 0 local) |
| Reviewed | 2026-08-25 |

## What it does

**feast-ui** (k8s): wraps the Feast UI container image. Receives feature-store configuration over the `feast-configuration` relation from `feast-integrator`, renders `feature_store.yaml`, and serves it via a Pebble service on port 8888. Integrates with Kubeflow Dashboard (sidebar link), Istio (sidecar or ambient ingress), and optionally Canonical Service Mesh.

**feast-integrator** (machine): requires three PostgreSQL relations (offline store, online store, registry), then renders and sends (1) a Kubernetes Secret containing `feature_store.yaml` to `resource-dispatcher` via the `kubernetes_manifest` interface, (2) a `PodDefault` to inject the secret into Kubeflow Notebooks, and (3) the feature store configuration to `feast-ui` via `feast-configuration`.

**configuration-requirer-tester**: test-only machine charm that receives `feast-configuration` and logs the YAML; not published to charmhub.

## Runtime resource usage

feast-ui idle (no feast-configuration relation, pebble service inactive): **1m CPU, 47Mi memory** (`kubectl top pod feast-ui-0`). No measurement was taken under an active workload — this would require the full feast-integrator + PostgreSQL chain, not available in this environment.

## Findings

Sorted by severity.

### 1. `get_feature_store_yaml()` does not catch `TypeError` from missing relation fields
- **Severity**: high
- **Kind**: bug
- **Where**: `charms/feast-ui/lib/charms/feast_integrator/v0/feast_store_configuration.py:350–352`
- **Evidence**: `FeastStoreConfigurationRequirer.get_feature_store_yaml()` catches only `FeastStoreConfigurationDataInvalidError`. When relation data is missing required fields, `FeastStoreConfiguration(**relation_data)` raises `TypeError: ... missing 14 required positional arguments`, which is not caught and propagates to `CharmReconciler.reconcile()`'s bare `except Exception`, logged as `"execute_components caught unhandled exception"`. The charm settles on `BlockedStatus("[feast-configuration] Failed to compute status. See logs for details.")`. Confirmed with a scenario test injecting relation data `{'registry_user': 'u'}` only.
- **Impact**: An operator whose feast-configuration provider sends incomplete data gets a generic, non-actionable status. The list of missing fields is only visible in `juju debug-log`, forcing cross-pod log correlation to diagnose a misconfigured provider. This is also the underlying cause of the feast-ui status-message finding below.
- **Fix**: Add `except TypeError as e:` alongside the existing handler in `get_feature_store_yaml()`, wrapping it as `FeastStoreConfigurationDataInvalidError(f"Missing required fields: {e}")`.
- **Linter rule**: "Bare `except Exception` in library masks `TypeError` from missing dataclass fields."

### 2. feast-ui status message for partial relation data is not operator-actionable
- **Severity**: high
- **Kind**: ux / bug
- **Where**: `charms/feast-ui/lib/charms/feast_integrator/v0/feast_store_configuration.py:350–352`, `charms/feast-ui/src/components/store_configuration_reciver_component.py:44–66`
- **Evidence**: Same scenario test as above: injecting `{'registry_user': 'u'}` only produces `BlockedStatus("[feast-configuration] Failed to compute status. See logs for details.")`; the actual error (14 missing field names) is only in `juju debug-log`.
- **Impact**: Operators cannot diagnose from `juju status` alone. This is the primary operator-facing manifestation of finding 1.
- **Fix**: Fixing the `TypeError` handling above will automatically surface the missing-field names in the status message.
- **Linter rule**: "Error messages from `get_feature_store_yaml()` must be actionable without reading debug logs."

### 3. Database passwords transmitted through the Juju relation databag
- **Severity**: high
- **Kind**: security
- **Where**: `charms/feast-integrator/lib/charms/feast_integrator/v0/feast_store_configuration.py:292` (`send_data`), `charms/feast-ui/lib/charms/feast_integrator/v0/feast_store_configuration.py:292` (`get_feature_store_yaml`)
- **Evidence**: `FeastStoreConfigurationProvider.send_data()` sends all 15 dataclass fields — including `registry_password`, `offline_store_password`, `online_store_password` — into the Juju relation databag. `FeastStoreConfigurationRequirer.get_feature_store_yaml()` renders these into a YAML file, which feast-ui writes to `/home/ubuntu/feature_store.yaml` in the container.
- **Impact**: Juju relation data lives in the controller's database and is visible to anyone with controller access (e.g. `juju show-secret --reveal`). A compromised controller or misconfigured RBAC exposes all database credentials, which then also persist in plaintext on the Feast UI container filesystem.
- **Fix**: Have the provider render the YAML server-side and send only the rendered YAML (not raw credentials) over the relation, or use Juju secrets for credentials with only metadata over the relation.
- **Linter rule**: not mechanically checkable — requires semantic analysis of which relation fields carry credentials.

### 4. `latest/edge` channel is behind, missing the TLS port fix
- **Severity**: high
- **Kind**: bug / channel-management
- **Where**: charmhub channels for `feast-ui`
- **Evidence**: `juju info feast-ui` shows `latest/edge: 172`, `0.49/edge: 173`, `0.49/beta: 201`. Commit `793aeef` (`fix: use 443 for tls #108`) changed `istio_ambient_requirer_component.py` to use port 443 when TLS is enabled instead of always port 80. This fix is present in `0.49/edge` (rev 173) but absent from `latest/edge` (rev 172); `0.49/beta` (rev 201) is 29 revisions ahead. Confirmed at runtime: `juju refresh feast-ui --channel=latest/edge` on a rev 173 deployment actually **downgraded** the unit to rev 172.
- **Impact**: An operator deploying `feast-ui --channel=latest/edge` gets the TLS port bug: when ambient-mode Istio ingress has TLS enabled, the charm submits a Listener on port 80 instead of 443 and ingress traffic fails. The channel named "latest" is not actually the most recent revision.
- **Fix**: Keep `latest/edge` in sync with (or ahead of) `0.49/edge`; add CI/automation to promote the latest-tested revision to `latest/edge`.
- **Linter rule**: not mechanically checkable — requires monitoring charmhub channel revisions.

### 5. `fetch_relation_data` returns only the first non-empty relation
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/feast-integrator/src/components/database_requirer_component.py:53–65`
- **Evidence**: `for data in relations.values(): if not data: continue ... return db_data` returns on the first relation with non-empty data. If multiple units have data, only the first unit's is used.
- **Impact**: In a scaled deployment or rolling upgrade, different units may present different credentials; the charm would silently use stale ones with no indication.
- **Fix**: Use only the leader unit's data (via the leadership gate), or log when multiple units have data and which one was chosen.
- **Linter rule**: "Loop over relations collection returns on first match without checking for multiple matches."

### 6. YAML injection risk in feast-integrator secret template
- **Severity**: medium
- **Kind**: security / bug
- **Where**: `charms/feast-integrator/src/templates/feature_store_secret.yaml.j2`
- **Evidence**: The Jinja2 template renders `registry_password`, `offline_store_password`, `online_store_password` directly into YAML without quoting. A password containing `:` would render as an invalid nested mapping; a password containing newlines could inject arbitrary YAML structure. The library's own `get_feature_store_yaml()` avoids this by using `yaml.dump()` (which quotes correctly), but the Kubernetes Secret template bypasses the library and uses raw Jinja2.
- **Impact**: Credentials currently come from `postgresql-k8s`, whose generated passwords are alphanumeric, so this is latent rather than actively exploited. A custom password with special characters would produce invalid YAML and cause `resource-dispatcher` to fail applying the Secret.
- **Fix**: Quote credential values in the template (`"{{ registry_password }}"`) or render via `yaml.dump()` in Python and pass a pre-rendered string to the template.
- **Linter rule**: "Jinja2 template renders unquoted credential fields — suggest quoting or a `yaml_quoted` filter."

### 7. feast-integrator: `get_status()` sends configuration data on every status check
- **Severity**: medium
- **Kind**: performance
- **Where**: `charms/feast-integrator/src/components/store_configuration_sender_component.py:86–97`, `charms/feast-integrator/src/components/secret_sender_component.py:76–88`
- **Evidence**: Both `StoreConfigurationSenderComponent.get_status()` and `FeastSecretSenderComponent.get_status()` call their `send_*` methods on every status evaluation. `get_status()` runs on every `update-status` hook (every 5 minutes), so the configuration YAML is re-rendered and re-sent regardless of whether anything changed.
- **Impact**: Unnecessary re-render/re-send churn 12×/hour; idempotent but wasteful, and adds relation-data churn.
- **Fix**: Track a hash of the last-sent configuration and only re-send on change, or only send on relation events rather than every status check.
- **Linter rule**: "`get_status()` method sends data over the network or performs expensive computation."

### 8. feast-integrator is a machine charm managing Kubernetes resources
- **Severity**: medium
- **Kind**: architecture / ux
- **Where**: `charms/feast-integrator/metadata.yaml` (no `containers:`) vs. `provides:` (`secrets`, `pod-defaults` using `kubernetes_manifest`)
- **Evidence**: feast-integrator is a machine charm with no `kubectl` access to the operator Kubernetes cluster, yet it manages Kubernetes Secret and PodDefault manifests via `resource-dispatcher`.
- **Impact**: The charm cannot independently verify whether its manifests were actually applied; if `resource-dispatcher` is unavailable or misconfigured, the charm blocks with no diagnostic feedback about why k8s resources aren't appearing.
- **Fix**: Consider migrating to a k8s charm for direct verification, or improve status messages to reflect resource-propagation state and document the machine-as-operator pattern explicitly.
- **Linter rule**: not mechanically checkable.

### 9. feast-ui cannot be related to any feast-configuration provider on k8s
- **Severity**: medium
- **Kind**: architecture / ux
- **Where**: charm architecture — feast-ui `requires` `feast-configuration`; the only provider (feast-integrator) is a machine charm
- **Evidence**: Confirmed at runtime: deploying `configuration-requirer-tester` (which also `requires` the interface) to a k8s model and attempting `juju integrate` with feast-ui fails with "no compatible endpoints found" — feast-ui requires, it does not provide.
- **Impact**: feast-ui cannot be exercised in isolation on a k8s model without also deploying feast-integrator, which needs a machine cloud (LXD). This constrains manual testing and demoing.
- **Fix**: Provide a thin k8s "feast-configuration provider" charm for testing/demo purposes, or document the required cross-substrate testing path.
- **Linter rule**: not mechanically checkable.

### 10. `TypeError` and `get_status()` error paths in feast-integrator sender components are untested
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `charms/feast-integrator/src/components/store_configuration_sender_component.py:68, 85–90, 109–110, 116, 119`; `charms/feast-integrator/src/components/secret_sender_component.py:81, 85–90`
- **Evidence**: Coverage report shows these lines uncovered. `create_store_configuration()` handles three `TypeError` cases (missing/unexpected keyword arg, general) — none exercised by wrong-typed context values. `StoreConfigurationSenderComponent.get_status()` catches `FeastStoreConfigurationRelationError` and `ErrorWithStatus`; `FeastSecretSenderComponent.get_status()` catches a generic `Exception` from `send_configuration()` — none of these paths are exercised.
- **Impact**: A regression in any of these error-handling paths (e.g. wrong status returned on transient relation failure) would go undetected.
- **Fix**: Add unit tests patching `_inputs_getter`/`send_store_configuration`/`send_configuration` to raise each error type and assert the resulting status.
- **Linter rule**: not mechanically checkable.

### 11. Integration test: `relation-broken` path not exercised end-to-end
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `charms/feast-ui/tests/integration/test_charm.py`, `charms/feast-integrator/tests/integration/test_charm.py`
- **Evidence**: Integration tests deploy the full stack and assert `ActiveStatus`; none remove a relation afterward. Runtime testing confirmed `relation-broken` fires correctly and the reconciler re-runs all components, but this path has no integration-test coverage.
- **Impact**: A regression in relation-broken handling (e.g. the requirer stops emitting `updated`, or the reconciler stops observing it) would not be caught by CI.
- **Fix**: Add a test that establishes the feast-configuration relation, asserts `ActiveStatus`, removes the relation, and asserts the charm returns to the correct blocked/waiting status.
- **Linter rule**: not mechanically checkable.

### 12. Temporary file leak on feast-ui charm host
- **Severity**: low
- **Kind**: bug
- **Where**: `charms/feast-ui/src/charm.py:119–124`
- **Evidence**: `tempfile.NamedTemporaryFile(delete=False, ...)` creates a file that is passed to `ContainerFileTemplate` and rendered into the container, but the temp file on the charm host is never deleted.
- **Impact**: Every reconciliation that regenerates the feature-store YAML leaves a new file in the temp directory, accumulating over time.
- **Fix**: Explicitly `os.unlink()` the path after pushing, or pass the rendered content directly to `ContainerFileTemplate` instead of via a temp file.
- **Linter rule**: "Calls to `tempfile.NamedTemporaryFile` must use `delete=True` or explicitly delete the file after use."

### 13. `KubeflowDashboardLinksRequirer` instantiated but unmonitored
- **Severity**: low
- **Kind**: ux
- **Where**: `charms/feast-ui/src/charm.py:69`
- **Evidence**: `KubeflowDashboardLinksRequirer` is created in `__init__` but extends `ops.framework.Object`, not `Component`, so it cannot be added to `CharmReconciler`. The charm never checks whether the `dashboard-links` relation succeeded. `dashboard-links` is not marked `required: true` in `metadata.yaml`, so the charm is correct not to block on it.
- **Impact**: If `kubeflow-dashboard` is not deployed or the relation fails, the Feast link never appears in the sidebar and the charm still reports `ActiveStatus` with no indication — a silent, undiagnosable UX degradation.
- **Fix**: Wrap the requirer in a `Component` implementing `get_status()` (e.g. `WaitingStatus` when no relation exists) and add it to the reconciler.
- **Linter rule**: "Library requiring relation not validated for status purposes."

### 14. feast-ui has no runtime configuration options
- **Severity**: low
- **Kind**: ux
- **Where**: no `config.yaml` in either charm directory
- **Evidence**: `juju config feast-ui` returns an empty settings map. The ingress path prefix (`INGRESS_PATH_MATCHED_PREFIX = "/feast/"`, `charm.py:38`) is hardcoded.
- **Impact**: An operator cannot change port, feature-store file path, or ingress prefix without rebuilding the charm.
- **Fix**: Add config options such as `ingress-path-prefix` and `app-port` at minimum.
- **Linter rule**: not mechanically checkable — opinion-based.

### 15. PodDefault `FEAST_FS_YAML_FILE_PATH` may not match container path
- **Severity**: low
- **Kind**: ux / docs
- **Where**: `charms/feast-integrator/src/templates/feature_store_poddefault.yaml.j2:15` vs. `charms/feast-ui/src/charm.py:32`
- **Evidence**: The PodDefault sets `FEAST_FS_YAML_FILE_PATH: /feast/feature_store.yaml`, while feast-ui's pebble layer writes the file to `DEST_PATH = "/home/ubuntu/feature_store.yaml"`. These paths differ; whether this matters for Notebook users depends on where the Notebook container (not feast-ui) actually mounts the file — not confirmed in this review (unverified).
- **Impact**: If the Feast SDK reads `FEAST_FS_YAML_FILE_PATH` literally and the Notebook container is expected to have the file at that path, notebook users relying on this env var could fail to find the config.
- **Fix**: Verify where the PodDefault-injected path is actually consumed and align it with the actual file location.
- **Linter rule**: not mechanically checkable.

### 16. `upgrade-charm` deferred ~48s after refresh, fires before `config-changed`
- **Severity**: low
- **Kind**: observability / ux
- **Where**: `CharmReconciler` upgrade path, observed on feast-integrator, Juju 4.0.12 (concierge-lxd-4)
- **Evidence**: `juju refresh feast-integrator` (rev 200→201) downloaded the new charm; `upgrade-charm` did not fire for ~48 seconds, then `config-changed` fired immediately after. The reconciler ran via `config-changed` and set correct status; no `leader-elected` occurred (leadership preserved). `CharmReconciler` does not explicitly observe `upgrade-charm`.
- **Impact**: Operators may expect hooks to fire immediately on refresh; the delay could cause confusion, though the charm settles correctly.
- **Fix**: This is Juju's own scheduling behaviour, not fixable in the charm; document the expected delay in upgrade documentation.
- **Linter rule**: not mechanically checkable.

### 17. `configuration-requirer-tester` does not observe `relation-broken`
- **Severity**: low
- **Kind**: test-gap / bug (test helper only)
- **Where**: `charms/feast-integrator/tests/integration/configuration-requirer-tester/src/charm.py:18–25`
- **Evidence**: The tester observes `leader_elected`, `config_changed`, `start`, `install`, `update_status`, `relation_changed`, but not `relation_broken`. Confirmed at runtime: removing the feast-configuration relation left the tester's status stale until the next `update-status` (~5 min), even though the `relation-broken` hook fired correctly at the unit-agent level. Production charms (using `CharmReconciler`) are unaffected.
- **Impact**: The test helper cannot be used to test relation removal, though this is test infrastructure only, not production code.
- **Fix**: Observe `relation_broken` for each relation (or loop over `self.model.relations`).
- **Linter rule**: "Charm does not observe `relation-broken` events for its declared relations."

### 18. No unit test for `relation-broken` on feast-configuration
- **Severity**: low
- **Kind**: test-gap
- **Where**: `charms/feast-ui/tests/unit/test_charm.py`, `charms/feast-integrator/tests/unit/test_charm.py`
- **Evidence**: Neither suite fires `relation-broken` on the feast-configuration relation; only `relation-changed` (`test_relation_exists_but_empty`) is covered. Production code correctly handles the event.
- **Impact**: A regression in `relation-broken` handling would not be caught by unit tests.
- **Fix**: Add a test firing `relation-broken` and asserting the correct blocked status.
- **Linter rule**: not mechanically checkable.

### 19. No unit tests for `can_connect=False`
- **Severity**: low
- **Kind**: test-gap
- **Where**: `charms/feast-ui/tests/unit/test_charm.py`
- **Evidence**: All 22 unit tests use `Container(name="feast-ui", can_connect=True)`. `PebbleServiceComponent` (from `charmed-kubeflow-chisme`) handles `can_connect=False` by returning `WaitingStatus`, but this is verified only by source inspection, not tests.
- **Impact**: A regression in container-unavailable handling would go undetected.
- **Fix**: Add a parametrized test with `can_connect=False` asserting `WaitingStatus`.
- **Linter rule**: not mechanically checkable.

### 20. Integration test: ingress-accessible assertions are effectively tautological
- **Severity**: low
- **Kind**: test-gap
- **Where**: `charms/feast-ui/tests/integration/test_charm.py::test_feast_ui_ingress_accessible`, `test_charm_ambient.py::test_feast_ui_ingress_accessible`
- **Evidence**: Both assert `"Feast" in response.text or len(response.text) > 0`; the `or` clause always evaluates true for any non-empty response, so the "Feast" check is redundant.
- **Impact**: A failing UI returning an error page with a non-empty body would still pass the test, giving false confidence.
- **Fix**: `assert "Feast" in response.text`, dropping the fallback.
- **Linter rule**: "Test assertion `X or len(body) > 0` is always True — remove the redundant condition."

### 21. Code duplication between `FeastStoreConfiguration` dataclass and the secret template
- **Severity**: low
- **Kind**: maintainability
- **Where**: `lib/charms/feast_integrator/v0/feast_store_configuration.py` (dataclass), `src/templates/feature_store_secret.yaml.j2`
- **Evidence**: The dataclass fields and the Jinja2 template variables are structurally identical (15 fields). Already flagged in GitHub issue #13.
- **Impact**: Every configuration-structure change must be kept in sync across both files, with real drift risk.
- **Fix**: Derive the template from the dataclass (render YAML from a dataclass instance) rather than maintaining a parallel template.
- **Linter rule**: not mechanically checkable.

### 22. `CharmReconciler` logs "unhandled exception" for a handled `ErrorWithStatus`
- **Severity**: low
- **Kind**: ux / observability
- **Where**: `charmed-kubeflow-chisme` `components/charm_reconciler.py` (third-party library)
- **Evidence**: When a component's `configure_charm()` raises `ErrorWithStatus`, it's caught by a bare `except Exception` and logged as `"execute_components caught unhandled exception ..."`, even though the charm status is correctly set and remaining components still execute.
- **Impact**: Operators reading debug logs may believe the charm crashed when it is functioning correctly, adding noise and delaying real diagnosis.
- **Fix**: In the reconciler, detect `ErrorWithStatus` (or subclasses) and log at INFO/WARNING with an accurate message. Requires a change to `charmed-kubeflow-chisme`, not the charm.
- **Linter rule**: not applicable — library change.

### 23. Kubernetes Secret has plaintext passwords, propagated by resource-dispatcher
- **Severity**: medium
- **Kind**: security
- **Where**: `charms/feast-integrator/src/templates/feature_store_secret.yaml.j2`
- **Evidence**: The template renders all three database passwords directly into `stringData` of a Kubernetes Secret, managed by `resource-dispatcher`.
- **Impact**: `stringData` secrets are only base64-encoded, trivially decoded by anyone with Secret read access in the operator namespace; `resource-dispatcher` propagates the Secret into user namespaces, widening blast radius if the operator namespace is compromised.
- **Fix**: Document blast radius and lock down namespace RBAC at minimum; consider tighter secret-management options.
- **Linter rule**: not mechanically checkable.

### 24. Test interface-name constant uses underscore instead of hyphen
- **Severity**: nit
- **Kind**: lint / docs
- **Where**: `charms/feast-integrator/tests/unit/test_charm.py:158,196`, `charms/feast-ui/tests/unit/test_charm.py:24,64`
- **Evidence**: Tests use `interface="feast_configuration"` (underscore); `metadata.yaml` declares `feast-configuration` (hyphen). `ops.testing.Relation` doesn't validate interface names, so tests still pass.
- **Impact**: Misleads readers about the real interface name; would break if `ops.testing.Relation` ever validates names.
- **Fix**: Use `feast-configuration` consistently in tests.
- **Linter rule**: "Interface name in test should match the interface name in `metadata.yaml`."

### 25. Typo in log message: "Proivder" instead of "Provider"
- **Severity**: nit
- **Kind**: lint
- **Where**: `charms/feast-integrator/lib/charms/feast_integrator/v0/feast_store_configuration.py:257`
- **Evidence**: `logger.info("StoreConfigurationProivder handled send_data event when it is not the leader.")`
- **Impact**: Cosmetic, misleading when grepping logs.
- **Fix**: `StoreConfigurationProvider`.
- **Linter rule**: "Misspelled identifier 'Proivder' — suggest 'Provider'."

### 26. `get_feature_store_yaml` docstring references a non-existent `config` parameter
- **Severity**: nit
- **Kind**: docs
- **Where**: `charms/feast-ui/lib/charms/feast_integrator/v0/feast_store_configuration.py:326`
- **Evidence**: Docstring documents `Args: config (FeastConfiguration): ...` but the method signature is `def get_feature_store_yaml(self):` — no parameters.
- **Impact**: Confusing for library API readers.
- **Fix**: Remove the erroneous `Args` section.
- **Linter rule**: not established.

### 27. `resource_dispatcher.py` lint issues (vendored library)
- **Severity**: nit
- **Kind**: lint
- **Where**: `charms/feast-integrator/lib/charms/resource_dispatcher/v0/resource_dispatcher.py`
- **Evidence**: `ruff check` reports 29 errors: W291 trailing whitespace, W293 blank-line whitespace, E501 line too long, D212/D200/D205/D401/D415 docstring formatting. Vendored/third-party, not charm-owned.
- **Impact**: Pollutes VCS diffs; cosmetic otherwise.
- **Fix**: `ruff check --fix` for whitespace; manual fix or library upgrade for docstrings.
- **Linter rule**: W291, W293, E501, D212, D200, D205, D401, D415.

### 28. Unused import in vendored `istio_ingress_route.py`
- **Severity**: nit
- **Kind**: lint
- **Where**: `charms/feast-ui/lib/charms/istio_ingress_k8s/v0/istio_ingress_route.py:147`
- **Evidence**: `F401 'pydantic.field_validator' imported but unused`.
- **Impact**: Dead import; contributes to the larger lint-error count in vendored libraries (97 errors total in feast-ui `lib/`).
- **Fix**: Remove the unused import.
- **Linter rule**: F401.

## Corrected non-findings

- **`SdiRelationBroadcasterComponent`** (`charms/feast-ui/src/components/istio_relations_conflict_detector.py` area, sidecar ingress): verified at runtime to correctly implement `get_status()`, returning `ActiveStatus`/`WaitingStatus`/`BlockedStatus` as appropriate. No finding.
- **Pebble layer deferred while blocked**: the Juju pebble layer's `working-dir` not being visible in the combined pebble plan is intentional — charm logs confirm `"[feast-ui-pebble-service] Execution pending - waiting on feast-configuration"`, and the dependency graph correctly gates the pebble component on the store-configuration receiver. No finding.
- **`PodDefaultSenderComponent`** has no `configure_charm()` override by design; the underlying `KubernetesManifestsRequirer` handles the send lifecycle via its own `leader_elected`/`relation_created` observation. Correct design, not a finding.

## Observed behaviour

- **Hook sequence differs by Juju version**: Juju 4.x (concierge-k8s-4): `install → leader-elected → config-changed → start → feast-ui-pebble-ready`. Juju 3.6 (concierge-k8s-3): `install → leader-elected → feast-ui-pebble-ready → config-changed → start`. Both converge on the same blocked state; the ordering difference is cosmetic here.
- **Relation removal**: removing `feast-configuration` fires `relation-departed` then `relation-broken` on both sides; feast-integrator reconciles cleanly to `BlockedStatus` with no crash (the unit shutdown seen in logs is the normal uniter cycle, not a crash).
- **Pebble recovery**: killing the feast-ui process inside the container (process was already inactive due to missing config) and manually running `pebble start feast-ui` produced a `backoff` (config missing) followed by recovery to `active` — pebble recovery mechanics work correctly.
- **Istio-k8s deploy failure**: deploying `istio-k8s` to the k8s model produced `ErrorStatus` (`hook failed: "leader-elected"`), preventing Istio ingress testing in this environment (TLS ambient-mode behaviour is verified only by unit tests).
- **Scale up/down**: `juju add-unit feast-ui --num-units 2` (1→4 total observed across runs) reached `BlockedStatus` in ~30s per unit, with non-leader units showing `[leadership-gate] Waiting for leadership` until settled; `juju scale-application feast-ui 1` shut down extra units cleanly (`shutting down: agent should be terminated`), remaining unit correctly `BlockedStatus`.
- **feast-integrator upgrade** (concierge-lxd-4, Juju 4.0.12): `juju refresh` rev 200→201, `upgrade-charm` queued ~48s after refresh, then `config-changed` fired immediately after; reconciler ran all components; no `leader-elected`; status settled correctly.
- **Grafana/observability**: feast-ui has no `cos-agent` interface, `grafana-agent-k8s` has no `service-mesh` interface — no relation possible either direction.
- **self-signed-certificates deploy**: deployed to the k8s model (rev 586, beta), reached Active, but no matching interface with feast-ui (feast-ui has no `tls-certificates` interface) — confirms no direct TLS-cert integration path exists for feast-ui itself.
- **Resource usage**: feast-ui idle at 1m CPU / 47Mi memory.
- **No actions**: neither charm has `actions.yaml`; nothing to `juju run`.

## Deployment log

### feast-ui (k8s, concierge-k8s-4)
1. Created model `rv-feast-ui`. Deployed `feast-ui --channel=0.49/edge --trust --resource oci-image=docker.io/charmedkubeflow/feast-ui:0.49.0-fb7767e`.
2. Rev 173 downloaded; pod `feast-ui-0` reached Running (2/2) in ~90s; unit `BlockedStatus("[feast-configuration] Missing relation: feast-configuration")`.
3. Hook sequence: `install → leader-elected → config-changed → start → feast-ui-pebble-ready`.
4. Scaled to 4 units (`juju add-unit feast-ui --num-units 2`); all reached the same blocked state; non-leader units additionally showed `[leadership-gate] Waiting for leadership`. Scaling took ~30s per unit.
5. Killed the `feast ui` process inside the container (process was already inactive, no config file); `pebble start feast-ui` went to `backoff` then recovered to `active`.
6. Deployed `grafana-agent-k8s` — no compatible interface with feast-ui; no relation possible.
7. `juju refresh feast-ui --channel=latest/edge` — resulted in **rev 172**, a downgrade from rev 173, missing the TLS fix from `793aeef`. All 4 units re-ran hooks (`upgrade-charm` on non-leaders, leadership re-established), returned to blocked state.
8. Deployed `istio-k8s`; entered `ErrorStatus` (`hook failed: "leader-elected"`) — could not test Istio ingress.
9. Deployed `configuration-requirer-tester` locally and attempted `juju integrate tester:feast-configuration feast-ui:feast-configuration` — failed, "no compatible endpoints found" (feast-ui requires, doesn't provide, the interface).

### feast-ui (k8s, concierge-k8s-3 — Juju 3.6.25)
1. Created model `rv-feast-ui-k8s3`. Deployed `feast-ui --channel=0.49/edge` (rev 173); reached `BlockedStatus("Missing relation: feast-configuration")`.
2. Hook sequence: `install → leader-elected → feast-ui-pebble-ready → config-changed → start` (pebble-ready before config-changed/start, unlike Juju 4.x). Functional outcome identical.
3. Combined pebble plan showed only the rockcraft layer; Juju layer correctly not applied while blocked.

### feast-integrator (LXD, concierge-lxd, Juju 3.6.27)
1. Created model `rv-feast-test`. Deployed `configuration-requirer-tester` from local `.charm` (rev 0); machine provisioned in ~5 minutes; reached `BlockedStatus("Error with relation: Missing relation with name feast-configuration with a store configuration provider.")`.
2. Deployed `feast-integrator` from charmhub (`--channel=latest/edge`, rev 200); reached `BlockedStatus("[offline-store] Please add the missing relation: offline-store")`.
3. Related `feast-integrator:feast-configuration` ↔ `tester:feast-configuration`. Hook sequence on provider: `feast-configuration-relation-created → leader-elected → config-changed → start → feast-configuration-relation-joined → feast-configuration-relation-changed`; on requirer: `feast-configuration-relation-joined → feast-configuration-relation-changed`.
4. After relation established, tester status changed to `"Error with relation: No data found in relation feast-configuration data bag."` — correct chain (relation exists, but feast-integrator has no data to send without the database relations).
5. Removed the feast-configuration relation (`juju remove-relation feast-integrator:feast-configuration tester:feast-configuration`); `relation-departed → relation-broken` fired on both sides; feast-integrator reconciled correctly to `BlockedStatus` (offline-store missing); the tester's status did NOT update immediately (finding 17: tester doesn't observe `relation-broken`).
6. Machine provisioning on LXD took ~5 minutes per machine; controller switching worked correctly.

### feast-integrator upgrade (concierge-lxd-4, Juju 4.0.12)
1. `juju refresh feast-integrator` rev 200→201. `upgrade-charm` queued ~48s after refresh, then `config-changed` fired immediately after. Reconciler executed `leadership-gate → offline-store → online-store → registry`; settled to `BlockedStatus('[offline-store] Please add the missing relation: offline-store')`. No `leader-elected` fired (leadership preserved).

## Tests

### Unit tests
- feast-ui: 22/22 passed, 81% line coverage. `src/charm.py`, `istio_ambient_requirer_component.py`, `istio_relations_conflict_detector.py`, `pebble_component.py` at 100%. `store_configuration_reciver_component.py` 92% (lines 54, 65–66 error paths uncovered). Library `feast_store_configuration.py`: 56% (exception init methods, Provider internals uncovered — exercised via feast-integrator's suite instead).
- feast-integrator: 25/25 passed, 88% line coverage. `src/charm.py` 100%. `database_requirer_component.py` 84% (lines 53–66, first-match logic, uncovered). `poddefault_sender_component.py` 92% (line 64 uncovered). `secret_sender_component.py` 86% (lines 81, 85–86, 89–90 uncovered). `store_configuration_sender_component.py` 84% (lines 68, 85–90, 98, 109–110, 116, 119 uncovered). Library `feast_store_configuration.py` 89%.

### Missing test coverage
- `TypeError` from missing/wrong-typed fields (findings 1 and 10).
- `FeastStoreConfigurationRelationError`/generic `Exception` paths in `get_status()` (finding 10).
- `relation-broken` on feast-configuration in either unit-test suite (finding 18).
- `can_connect=False` for feast-ui (finding 19).
- `KubeflowDashboardLinksRequirer` and `SdiRelationBroadcasterComponent`: no dedicated unit tests (though the latter is verified correct at runtime).
- YAML-injection edge cases (special characters in passwords) — not exercised.
- Wrong interface-name constant in tests (finding 24).

### Integration tests
- Both charms have full suites using `jubilant`, deploying the full dependency stack (3× postgresql-k8s, resource-dispatcher, metacontroller, admission-webhook, istio) and asserting ActiveStatus, k8s resource creation, HTTP ingress, HTTPRoute attachment, container security context. Not run in this review (would require packing charms locally plus 8+ dependent charms).
- Gaps: no relation removal tested end-to-end (finding 11); tautological ingress assertion (finding 20).

### Lint
- Charm-owned code (`src/`, `lib/charms/feast_integrator/`) for both charms: zero ruff errors.
- Vendored libraries (`istio_*`, `kubeflow_*`, `data_platform_libs`, `resource_dispatcher`): feast-ui 97 errors, feast-integrator 121 errors, all in `lib/`. Real code findings extracted: unused `field_validator` import (finding 28), `resource_dispatcher.py` whitespace/docstring issues (finding 27).

## Docs

- **feast-ui README**: clear feature list and deployment/relation instructions, but incorrectly states `dashboard-links` is `(required)` — `metadata.yaml` does not mark it `required: true`, and the charm does not block without it. No mention of ambient vs. sidecar ingress distinction; no troubleshooting section.
- **feast-integrator README**: very sparse (345 bytes) — just the `summary` field from `metadata.yaml`; no deployment, relation, or configuration instructions.
- **Tutorial (`docs/tutorial/get-started.rst`)**: references stale charm revisions (`feast-integrator rev 72`, `feast-ui rev 42`); describes a Terraform-based deployment from a separate repo (`charmed-kubeflow-solutions`) whose expected `juju status` output uses different app names (`feast-offline-store`, etc.) than the charms' actual defaults — confusing for anyone following it literally.
- **System architecture (`docs/explanation/system-architecture.rst`)**: accurate, good overview diagram.
- **How-to guide (`docs/how-to/use.rst`)**: solid, concrete examples; hardcodes `pip install feast[postgres]==0.49.0`, which matches the current charm version but could drift.

## Positive patterns worth keeping

- **`CharmReconciler` dependency graph** (`charmed-kubeflow-chisme`): both charms model components as a DAG, making ordering explicit and deferral correct. The "gate → database relations → configuration sender → downstream relations" pattern in feast-integrator (`charms/feast-integrator/src/charm.py:36–106`) is a model worth reusing elsewhere.
- **Dedicated conflict-detector component**: `IstioRelationsConflictDetectorComponent` (`charms/feast-ui/src/components/istio_relations_conflict_detector.py`) cleanly detects sidecar/ambient Istio conflicts and blocks with a clear message.
- **Leadership gate as first-class component**: `LeadershipGateComponent` as the root of the dependency graph is the correct pattern.
- **`ErrorWithStatus` + `StatusBase` for error paths**: `store_configuration_reciver_component.py:37–57` uses the appropriate status subclass per failure mode.
- **Templated k8s resources with Jinja2**: feast-integrator's Secret/PodDefault templates are readable and isolated to their components (aside from the quoting issue in finding 6).
- **Non-root workload user**: both charms configure `charm-user: non-root`; feast-ui container runs UID/GID 584792.
- **Integration test infrastructure**: `jubilant`-based fixtures with proper model teardown, `--keep-models`/`--model` CLI options — a solid k8s charm integration-testing pattern.
- **Versioned interface library**: `FeastStoreConfiguration`/`FeastStoreConfigurationProvider`/`Requirer` in `lib/charms/feast_integrator/v0/` are well-designed and versioned, aside from the `TypeError` gap.

## Common-practice notes

**Following convention**: Poetry-based dependency management with `charm`/`fmt`/`lint`/`unit`/`integration` groups; `lib/charms/<charm>/v0/` versioning with `LIBID`/`LIBAPI`/`LIBPATCH`; `src/` layout; `tox.ini` at root and per-charm; `metadata.yaml`; no `actions.yaml` (nothing actionable); non-root charm user.

**Drifting from convention**: `charmcraft.yaml` in both charms uses an unusually complex two-stage build (poetry-deps + charm-poetry, rustup, uv) versus the standard `charm` plugin — documented in comments but high complexity. feast-integrator is a machine charm that runs no workload on the machine itself, only relation management and k8s manifest generation (finding 8). No `config.yaml` in either charm (finding 14). The `feast-configuration` relation has `limit: 1`, restricting to a single feast-ui per feast-integrator — appropriate for the single-UI use case but limiting multi-tenancy.

## Open questions

1. Whether `FEAST_FS_YAML_FILE_PATH` in the PodDefault (`/feast/feature_store.yaml`) is actually consumed at that path by the Notebook SDK, versus the feast-ui pebble path (`/home/ubuntu/feature_store.yaml`) — not verified (see finding 15).
2. Whether the full feast-integrator + PostgreSQL database chain behaves correctly under production load — untestable in an LXD-only environment since `postgresql-k8s` requires Kubernetes; the project's own CI covers this with a combined k8s environment.
3. Resource usage under an active feast-configuration workload (only idle numbers were captured).
4. Whether `resource-dispatcher`'s target-namespace RBAC is configured tightly enough to mitigate findings 3/23 in practice — not verified.
5. TLS/ambient-mode ingress behaviour end-to-end — `istio-k8s` entered `ErrorStatus` in this environment, so only unit-test coverage of the port 443/80 logic was checked, not a live deployment.
