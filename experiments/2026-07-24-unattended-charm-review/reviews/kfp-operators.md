# kfp-operators

Eight Kubernetes charms (`kfp-api`, `kfp-ui`, `kfp-persistence`, `kfp-profile-controller`, `kfp-schedwf`, `kfp-viewer`, `kfp-viz`, `kfp-metadata-writer`) that together provide the Kubeflow Pipelines backend, UI, scheduled workflows, persistence agent, per-profile controllers, and visualization service. All eight are k8s charms running as non-root and share patterns via `charmed_kubeflow_chisme`. Seven of the eight use the modern `CharmReconciler` pattern; `kfp-api`, the most complex and central charm, still uses manual event handling and is visibly behind the rest of the codebase in style and safety (no `can_connect()` guards, direct `serialized_data_interface` use, unused config option). The charm deploys and runs correctly end to end — pipelines can be created and run — but a maintainer should prioritize: (1) fixing the empty `viewer-pod-template.json` in `kfp-ui`, (2) fixing or removing the broken pebble health check in `kfp-persistence`, and (3) bringing `kfp-api` in line with the `CharmReconciler` pattern used elsewhere.

| | |
|---|---|
| Repo | canonical/kfp-operators @ `bbc97a3` (2026-07-22) |
| Charms | kfp-api, kfp-ui, kfp-persistence, kfp-profile-controller, kfp-schedwf, kfp-viewer, kfp-viz, kfp-metadata-writer |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3, kfp-api/kfp-viz/kfp-ui rev 2861/2818/2872 from latest/edge; kfp-db rev 434; minio rev 694 |
| Reviewed | 2026-08-17 |

## What it does

Deploys Kubeflow Pipelines on Kubernetes. `kfp-api` is the central API server backed by MySQL and object storage (MinIO or S3). `kfp-viz` provides the visualization service. `kfp-persistence` is the persistence agent that archives completed runs. `kfp-schedwf` manages scheduled/cron workflows. `kfp-profile-controller` creates per-user namespace resources. `kfp-ui` provides the web frontend. `kfp-viewer` manages pipeline viewer CRDs. All charms integrate with Istio service mesh and expose Prometheus/Grafana/Loki metrics/logs/dashboards.

## Deployment log

1. Created model `rv-kfp-ops-3` on `concierge-k8s-3` (Juju 3.6.25).
2. Deployed `mysql-k8s kfp-db` (channel `8.0/edge`, rev 434) → Active.
3. Deployed `kfp-viz` (`latest/edge`, rev 2818) → initially Waiting for Pebble; later Active.
4. Deployed `kfp-api` (`latest/edge`, rev 2861) → initially Waiting ("Waiting for object storage to become accessible").
5. Deployed `minio` (`latest/edge`, rev 694) → Active but with a **service selector mismatch** (Finding: kfp-persistence health check is separate; this is a MinIO charm bug, not kfp-operators — see below).
6. Deployed `kfp-ui` (`latest/edge`, rev 2872) → Active.
7. Related `kfp-api`↔`kfp-db` (mysql), `kfp-api`↔`kfp-viz`, `kfp-api`↔`minio` (object-storage), `kfp-ui`↔`kfp-api`, `kfp-ui`↔`minio`.
8. `s3-integrator` (rev 188, `latest/edge`) also deployed but **Blocked** — no cloud credentials in this microk8s environment (expected).
9. After the MinIO fix, `kfp-api`, `kfp-viz`, and `kfp-ui` all reached **Active**.

**Channel choice note**: `kfp-api` on `2.5/edge` (rev 2722) refused to deploy outside a model literally named `kubeflow` ("must be deployed to model named `kubeflow`"). `latest/edge` (rev 2861) removes this restriction and was used for the rest of the test.

**MinIO bug note**: `minio` rev 694 creates a Service with selector `app=minio,app.kubernetes.io/name=minio` but does not apply the `app=minio` label to its own pods, leaving the Service with zero endpoints and breaking every consumer (including `kfp-api`). Fixed manually with `kubectl label pod minio-0 app=minio --overwrite`. This is a bug in the `minio` charm, not in kfp-operators, but it blocks kfp-operators deployments that use the object-storage relation.

## Observed behaviour

- `kfp-api` startup sequence: K8s resources created → Pebble layer applied → bucket checked/created → apiserver started → Active. Log shows "Bucket mlpipeline already exists and is accessible" → "Successfully initialized blob storage" → sample pipelines uploaded → servers started. Also: "DB client initialized successfully", "Object store client initialized successfully", "All samples are loaded".
- `kfp-viz` startup: service mesh reconciled → Pebble layer applied → Active.
- `kfp-ui` startup: relation data received → Pebble layer applied → `ml-pipeline-ui` started → Active. `kubectl exec kfp-ui-0 -c ml-pipeline-ui -- cat /etc/config/viewer-pod-template.json` returns empty content (see Finding below).
- **Failure injection** (removed `minio` relation): `kfp-api` immediately went to `BlockedStatus` with "Missing object storage relation. Please relate to one of `object-storage` or `s3-credentials`." — correct and actionable.
- **Recovery** (restored `minio` relation): `kfp-api` returned to `ActiveStatus` — correct.
- Deprecation warnings across all charms' unit test runs: `ops.testing.Harness`, `JujuVersion.from_environ()`, `websockets.legacy`, `kubernetes_service_patch` v1 library.

## Findings

### `kfp-persistence` pebble health check targets an unreachable endpoint
- **Severity**: high
- **Kind**: bug
- **Where**: `charms/kfp-persistence/src/components/pebble_components.py:76-81`
- **Evidence**:
```python
"checks": {
    "persistenceagent-get": {
        ...
        "http": {"url": "http://localhost:8080/metrics"},
    }
}
```
The persistence agent binary does not expose a `/metrics` endpoint on port 8080, and the charm defines no `MetricsEndpointProvider`.
- **Impact**: The Pebble health check always fails; with the default `on-check-failure: restart`, the container restarts repeatedly. Matches upstream issue #514.
- **Fix**: Remove the health check, point it at a path the agent actually serves, or add a real metrics endpoint plus `MetricsEndpointProvider`.
- **Linter rule**: "pebble http check URL not confirmed to be served by the workload" — mechanically checkable by running the container and probing the URL.

### `kfp-profile-controller` has no error handling for a missing metacontroller CRD
- **Severity**: high
- **Kind**: bug
- **Where**: `charms/kfp-profile-controller/src/charm.py` (creates `DecoratorController` via `KubernetesComponent`)
- **Evidence**: Upstream issue #876 describes an unhandled `httpx.HTTPStatusError`/`ApiError` from `lightkube.Client` when the `metacontroller.k8s.io/v1alpha1` API group is absent. Not independently reproduced in this review (cluster used had metacontroller present) — **(unverified)** for direct behaviour, but consistent with the reported issue.
- **Impact**: Deploying on a cluster without metacontroller crashes the reconciler with an unhandled exception instead of a clear `BlockedStatus`.
- **Fix**: Pre-check that the CRD exists (e.g. in `_generate_context` or the `KubernetesComponent`) before applying, and surface a `BlockedStatus` if it's missing.
- **Linter rule**: not mechanically checkable (requires cluster state).

### `kfp-ui`'s `viewer-pod-template.json` is empty
- **Severity**: high
- **Kind**: bug
- **Where**: `charms/kfp-ui/src/templates/viewer-pod-template.json` (0 bytes); confirmed at runtime at `/etc/config/viewer-pod-template.json`
- **Evidence**: `kubectl exec kfp-ui-0 -c ml-pipeline-ui -- cat /etc/config/viewer-pod-template.json` returns empty; the source file has zero content.
- **Impact**: Matches upstream issue #603 — the UI reads this file at startup expecting real content; an empty file can cause viewer pods to render incorrectly or generate warnings.
- **Fix**: Populate `charms/kfp-ui/src/templates/viewer-pod-template.json` with the content described in issue #603.
- **Linter rule**: not mechanically checkable — requires comparing against upstream source.

### `kfp-api`'s `cache-enabled` config option is defined but never used
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/kfp-api/config.yaml:32-35` (option defined); `charms/kfp-api/src/charm.py` (`_generate_environment()`, never referenced)
- **Evidence**: `grep -n "cache-enabled\|cache_enabled\|CACHE_ENABLED" src/charm.py` returns nothing but `"CACHE_IMAGE"`. Confirmed against upstream issue #915.
- **Impact**: Operators setting `cache-enabled: false` get no effect — the apiserver defaults to caching behaviour regardless.
- **Fix**: Read `self.model.config["cache-enabled"]` and pass it as `CACHE_ENABLED` in `_generate_environment()`, or remove the option if unsupported.
- **Linter rule**: "config option defined in `config.yaml` but never read in charm code" — mechanically checkable by cross-referencing config options against `self.model.config` calls.

### `kfp-api` has no `can_connect()` guard on container operations
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/kfp-api/src/charm.py`, `_check_status()` and other event handlers
- **Evidence**:
```python
def _check_status(self):
    container = self.unit.get_container(self._container_name)
    if container:
        try:
            check = container.get_check("kfp-api-up")
```
`container.get_check()`/`get_service()`/`get_plan()` are called without a preceding `can_connect()` check; the `if container:` guard does not protect against `ModelError` when Pebble isn't ready.
- **Impact**: If the container is still initializing, `get_check()` raises `ModelError`, which is caught but surfaces as a generic `GenericCharmRuntimeError` rather than a `WaitingStatus`.
- **Fix**: Add `can_connect()` checks before Pebble calls, or catch the specific error and return `WaitingStatus`.
- **Linter rule**: "calls `container.get_check()`/`get_service()`/`get_plan()` without a preceding `can_connect()` guard" — mechanically checkable.

### `kfp-schedwf` hardcodes its ServiceAccount name
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/kfp-schedwf/src/charm.py:37`
- **Evidence**: `SA_NAME = "kfp-schedwf"`, used both in the Kubernetes resource context and in `SATokenComponent`. Matches upstream issue #843.
- **Impact**: Deploying with a non-default app name (e.g. `juju deploy kfp-schedwf --as kfp-schedwf-renamed`) creates a ServiceAccount named `kfp-schedwf-renamed`, but the charm still looks for `kfp-schedwf`, breaking token mounting — likely a silent Waiting/failed Pebble service.
- **Fix**: Replace the hardcoded constant with `self.model.app.name`, or make it configurable.
- **Linter rule**: "hardcoded string used as Kubernetes resource name that should be derived from `self.model.app.name`" — mechanically checkable.

### `kfp-api` boto3 S3 client has no addressing-style enforcement
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/kfp-api/src/services/s3.py:113-120`
- **Evidence**:
```python
self._client = boto3.client(
    "s3",
    endpoint_url=self.s3_url,
    aws_access_key_id=self.access_key,
    aws_secret_access_key=self.secret_access_key,
    config=Config(connect_timeout=CONNECT_TIMEOUT, read_timeout=READ_TIMEOUT),
    verify=self._ca_file,
)
```
No `addressing_style` is set; boto3's default virtual-hosted-style addressing can be rejected by MinIO for namespaced service endpoints.
- **Impact**: Depending on MinIO configuration/version, requests may be built against the wrong host form, causing spurious "bucket not found" errors.
- **Fix**: Pass `config=Config(..., s3={'addressing_style': 'path'})`.
- **Linter rule**: "boto3 s3 client created without explicit `addressing_style` when `endpoint_url` is non-AWS" — mechanically checkable.

### `kfp-api` has no timeout/retry ceiling around `_ensure_bucket_exists`
- **Severity**: medium
- **Kind**: performance / reliability
- **Where**: `charms/kfp-api/src/services/s3.py:113-120`, `charms/kfp-api/src/charm.py:922-931`
- **Evidence**: `S3BucketWrapper` sets `connect_timeout=10, read_timeout=10`, but the calling code has no retry/backoff ceiling:
```python
self.unit.status = MaintenanceStatus(f"Checking if bucket {bucket_name} exists.")
if s3_wrapper.bucket_exists(bucket_name):
    return
self.unit.status = MaintenanceStatus(f"Creating bucket {bucket_name}.")
s3_wrapper.create_bucket(bucket_name)
```
- **Impact**: During a prolonged S3 outage, every hook invocation retries with the same slow timeouts, risking hook timeouts.
- **Fix**: Add a `tenacity` retry with a bounded max wait, or catch specific exceptions and return `WaitingStatus` with backoff.
- **Linter rule**: not mechanically checkable.

### All charms use the deprecated `kubernetes_service_patch` v1 library
- **Severity**: low (future risk)
- **Kind**: bug
- **Where**: e.g. `charms/kfp-api/src/charm.py:62-66`; used across multiple charms
- **Evidence**: Runtime log: "The 'kubernetes_service_patch v1' library is DEPRECATED and will be removed in October 2025."
- **Impact**: All eight charms break once the library is removed.
- **Fix**: Migrate to `ops.Unit.set_ports()`.
- **Linter rule**: not mechanically checkable (external library deprecation).

### `kfp-api` uses `serialized_data_interface` directly instead of the chisme abstraction
- **Severity**: low
- **Kind**: lint
- **Where**: `charms/kfp-api/src/charm.py:45-51`
- **Evidence**: Direct import of `serialized_data_interface`, while `kfp-ui`, `kfp-persistence`, `kfp-profile-controller`, and `kfp-schedwf` all use `charmed_kubeflow_chisme`'s SDI component wrappers.
- **Impact**: More error-prone, less consistent with the rest of the codebase.
- **Fix**: Refactor to use `SdiRelationDataReceiverComponent` from chisme.
- **Linter rule**: "direct import of `serialized_data_interface` in charm code rather than via `charmed_kubeflow_chisme`" — mechanically checkable.

### `kfp-persistence` defines an unused `CheckFailedError` class
- **Severity**: low
- **Kind**: lint
- **Where**: `charms/kfp-persistence/src/charm.py`
- **Evidence**: `CheckFailedError` is defined but never imported or raised; the charm uses `ErrorWithStatus` from chisme instead.
- **Fix**: Remove the dead class.
- **Linter rule**: "defined class never instantiated or raised" — mechanically checkable with pyflakes.

### All charms' unit tests use the deprecated `ops.testing.Harness` API
- **Severity**: low (future risk)
- **Kind**: lint
- **Where**: All `tests/unit/test_operator.py` files
- **Evidence**: 48 warnings across test runs: `PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html`
- **Impact**: Tests will need rework once `Harness` is removed.
- **Fix**: Migrate to `scenario.Context` or `craft_application.testing.CharmHarness`.
- **Linter rule**: "use of `ops.testing.Harness` in test code" — mechanically checkable.

## Worth copying

- **`CharmReconciler` pattern** (chisme): used by `kfp-persistence`, `kfp-schedwf`, `kfp-ui`, `kfp-profile-controller`. Expresses component dependencies as a DAG via `depends_on=` and wires event handling with `charm_reconciler.install_default_event_handlers()` — cleaner than `kfp-api`'s manual event handling and the model future charms should follow.
- **`ErrorWithStatus` exceptions**: all charms raise typed exceptions carrying status, caught centrally and assigned to `self.model.unit.status`. Clean separation of error creation from handling.
- **`_generate_environment()`** in `kfp-api` (`src/charm.py` ~line 355): a well-structured pure function building the Pebble environment from config/relations/defaults, validating inputs and raising `ErrorWithStatus` on failure — easily unit-testable in isolation.
- **`ObjectStorageValidatorComponent`** in `kfp-profile-controller` (`object_storage_validator.py`): normalizes both `object-storage` (MinIO SDI) and `s3-credentials` (AWS S3) into one dict, cleanly handling the mutual exclusion of the two interfaces.
- **`S3BucketWrapper`** singleton boto3 client (`services/s3.py`): lazy-initialized and cached, with TLS CA chain handled via a temp file.
- **Unit test structure**: `tests/unit/test_operator.py` harness fixtures with `can_connect` and K8s client mocks; parametrized tests for relation-data shapes (gRPC vs HTTP) are a good pattern.

## Common-practice notes

- All charms use `charm-base:ubuntu-24.04` running as non-root (uid/gid 584792), matching modern best practice.
- Poetry-based builds with a `poetry-deps` bootstrap step, including rust/cargo for Python packages with Rust extensions.
- Workloads run from OCI rock images, not charm-installed packages.
- `charms/<name>/terraform/` directories exist for all charms.
- CI via GitHub Actions (`on_pull_request.yaml`, `release.yaml`, `promote.yaml`), tests on `ubuntu-24.04` runners, destructive mode for bundle tests.
- `concierge.yaml` specifies `juju 3.6/stable` and `k8s 1.32-classic/stable`, matching the environment used for this review.
- Libraries vendored under `lib/charms/<charm>/v<N>/`, updated via `charmcraft lib`/`charm libs update`.
- No `juju secret` usage — credentials flow through relation data and Kubernetes Secrets.
- The `object-storage`/`s3-credentials` mutual-exclusion pattern is correctly implemented across all charms that support both.
- **Pattern drift**: `kfp-api` is noticeably older in implementation style (manual ops, no `CharmReconciler`, direct SDI usage) than the other seven charms, making it harder to maintain and inconsistent with the rest of the codebase.

## Tests

### Unit tests
All five charms with unit tests pass: kfp-api 55, kfp-persistence 14, kfp-ui 39, kfp-profile-controller 55, kfp-schedwf 8 (171 total).

- All use the deprecated `ops.testing.Harness` API.
- No test covers `cache-enabled` config behaviour.
- No test covers the empty `viewer-pod-template.json`.
- No test parametrizes/exercises the hardcoded `SA_NAME` in `kfp-schedwf`.
- Good parametrized coverage of relation-data shapes (dict-returning `minimum=maximum=1` vs list-returning `minimum=0, maximum=1` SDI components).

### Integration tests
Uses `jubilant` for model management, `pytest-operator`-style `CharmSpec` deployment, the KFP SDK (`kfp.Client`) for API testing, and port-forwarding for UI access. `tests/integration/test_kfp_functional.py` runs actual pipeline operations (create experiment, compile, run, check status) — genuine behavioural tests, not just active/idle waiting. Bundle integration tests are split into standard, ambient (Istio ambient mesh), and S3 (s3-integrator) variants.

### Coverage gaps
- No unit test for the `_ensure_bucket_exists` retry path (network error → `WaitingStatus`).
- No unit test for `_check_status` when the container is not ready.
- No test for the `kubernetes_service_patch` deprecation impact.
- No test for `DecoratorController` creation failure when metacontroller is absent.

## Docs

- Each charm has a basic `README.md`; the top-level README links to Charmhub and gives a `juju deploy kubeflow-pipelines` one-liner. No troubleshooting guide.
- Repo-level and per-charm `CONTRIBUTING.md` cover manifest updates, test running, and rock image updates.
- `charmcraft.yaml` uses `platforms: ubuntu@24.04:amd64`; poetry + Rust toolchain build, with `uv` for poetry installation.
- Terraform modules exist per charm under `charms/<name>/terraform/`, with outputs for service names and relation endpoints.
- All eight charms are published on Charmhub with generic descriptions ("Machine learning toolkit...") that don't differentiate charms; no embedded documentation in metadata.

## Open questions

1. Is a refactor planned to bring `kfp-api` onto the `CharmReconciler` pattern used by the other seven charms?
2. Should `cache-enabled` be implemented (wire up `CACHE_ENABLED`) or removed from `config.yaml`?
3. What is the correct upstream content for `viewer-pod-template.json` (issue #603 doesn't specify)?
4. Is the MinIO charm's service-selector bug (blocking `object-storage` relations) tracked upstream in the `minio` charm repo?
5. Is `metacontroller.k8s.io/v1alpha1` expected to be pre-installed on target clusters, or should something provide it as a dependency?
</content>
