# minio

A well-structured k8s charm for MinIO with good test coverage and clean architecture (sidecar pattern with CharmReconciler/Component). Four critical defects emerge: (1) SSL/TLS configuration is entirely broken — the charm fails to push certificates because Pebble itself runs as the non-root UID 584792 and cannot create directories under `/` (the container rootfs is root-owned); the CharmReconciler silently swallows the `PathError`, leaving the charm showing `active` with no TLS; (2) negative or zero port values cause tracebacks instead of validation errors; (3) the backwards-incompatible endpoint change still blocks `juju refresh`; (4) the `and`-vs-`or` logic error in gateway mode validation silently accepts any invalid storage backend, causing MinIO to crash-loop. The `set_ports()` + `KubernetesServicePatchComponent` interaction was flagged as a port-duplication source in the first review session but did not reproduce in a fresh deploy on Juju 4.0.5 — it may be timing-dependent.

| | |
|---|---|
| Repo | canonical/minio-operator @ fd979cd (2026-06-24) |
| Charms | minio |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5), latest/edge rev 694; concierge-k8s-3 (Juju 3.6.25), latest/edge rev 694; also tested with grafana-agent-k8s integration |
| Reviewed | 2026-08-03 |

## What it does

Deploys a single-instance MinIO object store on Kubernetes, configurable in `server` (local storage) or `gateway` (S3/Azure proxy) modes. Exposes `object-storage` (legacy SerializedDataInterface), `s3-credentials` (newer `s3` interface), Prometheus `metrics-endpoint`, Grafana dashboards, Velero backup config, and service mesh relations. Uses the sidecar pattern with Pebble, the `charmed-kubeflow-chisme` component framework, and a `CharmReconciler`-driven execution loop.

## Deployment log

**Deploy on Juju 4.0.5 (latest/edge rev 694):**
```
juju switch concierge-k8s-4
juju add-model rv-minio-deep
juju deploy minio --channel latest/edge
juju deploy self-signed-certificates --channel latest/stable
juju deploy s3-integrator --channel latest/edge
juju deploy traefik-k8s --channel latest/stable --trust
```
MinIO reached `active`/`idle` in ~55 seconds. All integration attempts with self-signed-certificates, s3-integrator, and traefik-k8s failed — see Integration Gaps below.

**Deploy on Juju 3.6.25 (latest/edge rev 694):**
```
juju switch concierge-k8s-3
juju add-model rv-minio-36
juju deploy minio --channel latest/edge
```
Reached `active`/`idle` in ~65 seconds. No caasfirewaller duplicate-port errors (Juju 3.6 does not use `set_ports()` to manage K8s Service ports). ISTIO 403 error still present on every reconcile. The K8s Service has exactly 2 ports (patched by lightkube only).

**Integration gaps — all standard ecosystem relations failed:**
- `juju relate minio self-signed-certificates`: **no compatible endpoints** — minio has no `certificates` requires endpoint; TLS is config-based only.
- `juju relate minio:s3-credentials s3-integrator:s3-credentials`: **no compatible endpoints** — both charms *provide* `s3-credentials`; neither is a consumer. The `s3-credentials` endpoint added in PR #300 can only be consumed by requirer charms that need S3 access, not by another provider.
- `juju relate minio traefik-k8s`: **no compatible endpoints** — minio has no `ingress` requires endpoint.

**Port validation failures:**
- `juju config minio port=-1` → **traceback**: `set_ports(-1, ...)` crashed in `__init__` with `subprocess.CalledProcessError: Command '('open-port', '-1/tcp')' returned non-zero exit status 2`. Charm went to `error` status with `hook failed: "config-changed"`. Recovered after `juju config minio port=9000`.
- `juju config minio console-port=0` → charm accepted it, but `set_ports(9000, 0)` registered port 0, causing the K8s Service to show `0,9000/tcp`. `KubernetesServicePatchComponent` then failed to patch, producing `BlockedStatus('[kubernetes-service-patch] K8s Service was not patched correctly.')`. Recovered after `juju config minio console-port=9001`.

**SSL configuration failure (critical):**
- `juju config minio ssl-cert="dGVzdA=="` (cert only, no key) → charm logged `No SSL configuration provided` (the check requires both) and skipped push. Status remained `active`. No warning that only one SSL option was set.
- `juju config minio ssl-cert="aW52YWxpZA==" ssl-key="aW52YWxpZA=="` → charm logged `SSL configuration provided, pushing SSL files to MinIO container.` followed immediately by `No SSL configuration provided, skipping file push.` (the latter log is outside the `else` block — a logging bug). The underlying file push failed with `ops.pebble.PathError: permission-denied - cannot create directory: mkdir /minio.mkdir-new: permission denied`. The non-root workload user (UID 584792) cannot create `/minio/` in the container's root filesystem. The CharmReconciler caught this exception (`execute_components caught unhandled exception when executing configure_charm for container:minio`), logged it, and continued. Charm status remained `active`. **TLS is silently not working** — no files in `/minio/.minio/certs/`, minio still serving plain HTTP.
- Reset via `juju config minio ssl-cert="" ssl-key=""`: no change in status (was already `active` despite the failure).

**Gateway mode validation:**
- `juju config minio mode=gateway gateway-storage-service=xyz` → **NOT BLOCKED** — charm set status to `waiting` with `[container:minio] Waiting for Pebble services (minio)...`. MinIO crashed in the workload: `'xyz' is not a minio sub-command`. Confirmed the `and` vs `or` validation bug. Recovered after reverting mode to `server`.
- `juju config minio mode=invalid` → correctly set to `BlockedStatus("Invalid mode 'invalid'...")`. Recovered after reverting.
- `juju config minio gateway-storage-service=azure` (with mode=server) → **silently ignored**, charm stayed `active`. No warning that the config value has no effect in server mode.

**Other failure injections:**
- `juju config minio secret-key="short"` → **blocked** with `The 'secret-key' config value must be at least 8 characters long.` Recovered on re-set.
- **Killed minio process** via `kubectl exec ... pkill -9 minio` → Pebble auto-restarted within seconds (health checks enabled), charm remained `active`.
- **No-op config change** (same secret-key re-set) → no workload restart (Pebble layer comparison prevents unnecessary replan).

**Lifecycle:**
- `juju scale-application minio 2` → second unit stuck in `Pending` (CSI rawfile provisioner "Not enough disk space" — cluster issue, not charm). Scaled back to 1.
- `juju refresh minio --channel 1.10/edge` → worked cleanly.
- `juju refresh minio --channel latest/edge` (back) → **FAILED** with endpoint mismatch (see finding below).
- `juju remove-application minio --force --no-wait` → teardown clean, model destroyed without hangs.

**Integrations (with grafana-agent-k8s, confirmed in deepened session):**
- Deployed `grafana-agent-k8s --channel 1/stable` and related via `metrics-endpoint` and `grafana-dashboard`. Relations established correctly on Juju 4.0.5. Scrape jobs (targeting `*:9000` on `/minio/v2/metrics/cluster`) and alert rules (KubeflowServiceDown, MinIO_Disk_Space_Filling_Up, MinIO_Low_Disk_Space, etc.) were published in relation data. Grafana dashboard JSON (minio-overview) was published. The grafana-agent-k8s app showed `blocked` due to missing cloud-config provider — this is a grafana-agent requirement, not minio's fault. Removal was clean.

**Deepened session (Juju 4.0.5, model rv-minio-v2):**
- Redeployed minio latest/edge rev 694 and confirmed all critical findings still hold.
- Additional confirmations:
  - Pebble PID 1 runs as UID 584792 (confirmed via `/proc/1/status`), not root — this is the root cause of the SSL push `PathError`. Pebble can create directories under `/data/` (group 170) but not under `/` (root-owned).
  - The K8s Service had 2 clean ports (no duplicates) in this fresh deploy, unlike the first review session. The duplicate-port issue appears timing-dependent.
  - ISTIO 403 error confirmed present on every hook.
  - `_get_files_to_push()` logging bug confirmed: both "SSL configuration provided" and "No SSL configuration provided" fire in the same hook cycle when SSL is set.
  - `set_ports()` correctly records ports (confirmed via `opened-ports`: 9000/tcp, 9001/tcp) and the lightkube Service patch applies cleanly.

**Deepened session (Juju 3.6.25, model rv-minio-36v2):**
- Redeployed minio latest/edge rev 694. All code-level findings (SSL push failure, ISTIO 403, logging bug) confirmed identical to Juju 4.x.
- K8s Service has 2 clean ports (lightkube patch only — `set_ports()` on 3.6 doesn't manage K8s Service).
- No caasfirewaller errors (as expected).

## Observed behaviour

| Metric | Juju 4.0.5 | Juju 3.6.25 |
|---|---|---|
| Deploy to active | ~55s | ~65s |
| Juju refresh (latest/edge→1.10/edge) | ~15s, clean | not tested |
| Juju refresh (1.10/edge→latest/edge) | **blocked** by endpoint mismatch | not tested |
| MinIO pod memory | 92Mi | — |
| MinIO pod CPU | 1m (idle) | — |
| Pebble services | minio (enabled/active, auto-restart) | same |
| Pebble health checks | ready/alive on `/minio/health/ready|lite`, 30s | same |
| Workload UID/GID | 584792:584792 | same |
| Secret key (auto-generated) | 30-char alphanumeric | same |
| K8s Service ports | 2 ports (clean in fresh deploy); duplicates seen in first session | 2 ports (clean) |
| caasfirewaller errors | **none** in fresh deploy; duplicates seen in first session | **none** |
| Service mesh (ISTIO) errors | 403 Forbidden on every reconcile | 403 Forbidden on every reconcile |
| SSL file push | **fails silently** (permission-denied on `/minio/`) | same |
| K8s API GETs per reconcile | ~20+ GETs to services/minio from `get_status()` | same |

### Juju version differences

- **caasfirewaller duplicate-port error is timing-dependent on Juju 4.x**: Observed in the first review session but NOT in a fresh deploy in the deepened session. When it occurs, `unit.set_ports()` and `KubernetesServicePatchComponent` both manage the K8s Service, creating duplicate ports. On Juju 3.6.25, `set_ports()` does not create K8s Service ports, so the issue cannot occur. Open issue #238 tracks this.
- **ISTIO 403 error is present on both Juju versions**: The `PolicyResourceManager.reconcile()` call in `ServiceMeshComponent._configure_app_leader()` unconditionally queries ISTIO CRDs, and the charm's service account lacks permission without `--trust`. This is a code-level issue, not Juju-version-specific.
- **SSL file push failure is present on both**: Pebble runs as UID 584792 (non-root) in the container, and `/minio/` is under the root-owned rootfs. This is inherent to the OCI image and Pebble configuration, independent of Juju version.
- **Juju 3.6 does not show open ports in `juju status`**: On 3.6 the Ports column is empty; on 4.x it shows `9000-9001/tcp`. Opened ports are correctly recorded on both (`opened-ports` shows 9000/tcp, 9001/tcp).
- **Log format differs**: Juju 4.x uses `[container-agent]` prefix with structured timestamps; Juju 3.6 uses `unit-minio-0:` prefix. Both include the same charm-level log content.

## Findings

### SSL/TLS certificate push fails silently — TLS is completely broken
- **Severity**: critical (confirmed in deployment on both Juju 4.0.5 and 3.6.25)
- **Kind**: bug
- **Where**: `src/charm.py:188` (hardcoded `/minio/.minio/certs` path) and `src/charm.py:268-283` (file push destinations under `/minio/.minio/certs/`)
- **Evidence**: Every push fails with `ops.pebble.PathError: permission-denied - cannot create directory: mkdir /minio.mkdir-new: permission denied`. **Root cause**: Pebble itself (PID 1 in the workload container) runs as UID 584792, NOT root — confirmed via `cat /proc/1/status` in the container. The container root filesystem `/` is owned by `root:root` with `drwxr-xr-x`, so the Pebble process cannot create `/minio/`. The `/data` volume is writable by UID 584792 (group 170), but `/minio/` is under the rootfs. The `CharmReconciler` at `charmed_kubeflow_chisme/components/charm_reconciler.py:96-100` catches the exception with `except Exception` and only logs it — the charm status stays `active`. The Pebble layer command includes `--certs-dir /minio/.minio/certs` at `charm.py:188`, but the directory never exists. MinIO runs without TLS.
- **Why it matters**: An operator who configures `ssl-cert` and `ssl-key` gets an `active` charm status and believes TLS is working. It is not. The cert files are never pushed, the directory is never created, and MinIO serves plain HTTP. There is zero indication to the operator that anything is wrong — they would only discover it by testing the endpoint or finding the permission-denied errors buried in debug-log. This is a silent security failure.
- **Fix**: Either (a) change the certs directory to a location writable by the Pebble process, e.g. under the `/data` volume (e.g. `--certs-dir /data/.minio/certs`), or (b) pre-create `/minio/.minio/certs/` with ownership 584792:584792 in the OCI image, or (c) adjust the container security context to run Pebble as root. Also fix the CharmReconciler to propagate component execution errors to status rather than silently swallowing them.
- **Linter rule**: mechanically checkable — a charm linter could detect when `make_dirs=True` file pushes target paths under `/` when the container runs as non-root, by cross-referencing `metadata.yaml` container UID/GID with Pebble push destinations and the container filesystem ownership.

### Pebble (PID 1) runs as non-root user, making rootfs immutable for file pushes
- **Severity**: high (root cause of the SSL failure above)
- **Kind**: bug
- **Where**: `metadata.yaml:20-21` and the OCI image `charmedkubeflow/minio:ckf-1.10-25a3ea0`
- **Evidence**: `cat /proc/1/status` in the workload container shows `Uid: 584792 584792 584792 584792` and `Gid: 584792 584792 584792 584792`. The container rootfs `/` is `drwxr-xr-x root root`. Pebble cannot create directories directly under `/` — confirmed via `mkdir /testrootdir` → `Permission denied`. The `/data` volume is mounted with group 170 (which UID 584792 belongs to), so file operations under `/data/` succeed. This is the root cause of the SSL file push failure: `--certs-dir /minio/.minio/certs` attempts to create `/minio/` which Pebble cannot do.
- **Why it matters**: Any Pebble `push` operation with `make_dirs=True` that targets a path under `/` (outside `/data/`) will fail silently. The charm currently only hits this for SSL certs, but any future file push would also be affected.
- **Fix**: Either run Pebble as root (revert `charm-user: non-root` or use a different OCI image), or ensure all pushed files target paths under `/data/`.
- **Linter rule**: mechanically checkable — flag `charm-user: non-root` combined with file push destinations outside storage mounts.

### Gateway mode validation silently accepts invalid storage backends
- **Severity**: critical (confirmed in deployment)
- **Kind**: bug
- **Where**: `src/charm.py:220`
- **Evidence**: `if not storage and storage not in ["s3", "azure"]:`
- **Deployment confirmation**: Setting `gateway-storage-service=xyz` resulted in the charm setting `waiting` status instead of `blocked`. MinIO crashed in the workload with `'xyz' is not a minio sub-command`. The Pebble service went into a crash-restart loop.
- **Why it matters**: The `and` operator means any non-empty invalid string (e.g. `"xyz"`) passes validation: `not "xyz"` evaluates to `False`, short-circuiting the `and`. The charm deploys but MinIO then fails at runtime with an obscure error message. Operators see `waiting` status with a Pebble-level message rather than `blocked` with a clear config correction hint.
- **Fix**: Change `and` to `or`: `if not storage or storage not in ["s3", "azure"]:`
- **Linter rule**: mechanically checkable — a charm linter could flag `not X and X not in [...]` as a likely logic error.

### Refresh blocked by backwards-incompatible endpoint change
- **Severity**: critical (confirmed in deployment)
- **Kind**: bug
- **Where**: metadata.yaml (diff between rev 686 and rev 694)
- **Evidence**: `juju refresh minio --channel latest/edge` from rev 686 (1.10/edge) to rev 694 (latest/edge) failed with `ERROR setting application "minio" charm: one or more of the provided endpoints "...juju-info..." do not exist`. Rev 686 has a `juju-info` provides endpoint that rev 694 dropped; rev 694 added `s3-credentials` that rev 686 lacks.
- **Why it matters**: Operators running `1.10/edge` cannot upgrade to `latest/edge` (or vice versa) without first destroying and recreating the application. This blocks in-place charm upgrades.
- **Fix**: Either keep `juju-info` as a deprecated endpoint in rev 694 alongside `s3-credentials`, or provide an intermediate revision that supports both. Document the breaking change in release notes.
- **Linter rule**: mechanically checkable — a CI check could diff `metadata.yaml` between the target channel and the branch and flag when endpoints are dropped.

### Port values lack validation — negative/zero ports cause tracebacks
- **Severity**: high (confirmed in deployment)
- **Kind**: bug
- **Where**: `src/charm.py:43-46`
- **Evidence**: `self.model.unit.set_ports(int(self.model.config["port"]), int(self.model.config["console-port"]))` — this is called in `__init__` without any validation. `juju config minio port=-1` crashed the `__init__` with `subprocess.CalledProcessError: Command '('open-port', '-1/tcp')' returned non-zero exit status 2`. `console-port=0` was accepted and registered port 0, breaking the K8s Service and causing `KubernetesServicePatchComponent` to report blocked. Neither `config.yaml` nor code validates port ranges.
- **Why it matters**: Invalid port values crash the charm's `__init__`, which means every subsequent hook fails until the config is fixed. The operator gets a `hook failed` error rather than a clear `BlockedStatus("Port must be between 1 and 65535")`. Port 0 is technically invalid for TCP but was accepted, creating a broken K8s Service.
- **Fix**: Add validation in `_get_minio_args()` or early in `__init__`: check that `port` and `console-port` are in the range 1–65535, and raise `ErrorWithStatus(BlockedStatus(...))` if not.
- **Linter rule**: mechanically checkable — a charm linter could flag `int(config[...])` used as a port number without range validation.

### CharmReconciler silently swallows component execution errors
- **Severity**: high
- **Kind**: bug
- **Where**: `.tox/unit/lib/python3.12/site-packages/charmed_kubeflow_chisme/components/charm_reconciler.py:96-100` (shipped as dependency `charmed_kubeflow_chisme`)
- **Evidence**: The `reconcile()` method catches all exceptions from `component_item.component.configure_charm(event)` with `except Exception as err`, logs the message, and continues. The component's `get_status()` is then called later, which returns `ActiveStatus()` if the Pebble container is running — it does not know about the file-push failure. This means both the SSL permission-denied error and the ISTIO 403 error are logged but never reflected in charm status.
- **Why it matters**: When a component fails to do its job (push TLS certs, reconcile mesh policies), the charm still reports `active`. The operator cannot distinguish between "TLS configured and working" and "TLS configuration failed silently". This is a framework-level issue — any charm using `CharmReconciler` inherits this pattern.
- **Fix**: The `CharmReconciler` should set a component-level error status when `configure_charm` raises, rather than only logging. Alternatively, each component's `configure_charm` method should catch its own errors and set internal state that `get_status()` can report. Upstream fix needed in `charmed_kubeflow_chisme`.
- **Linter rule**: not mechanically checkable — requires semantic understanding of error-handling-vs-status patterns.

### Duplicate K8s Service port management creates continuous controller errors (Juju 4.x only)
- **Severity**: high (Juju 4.x specific; observed in first review session, NOT reproduced in fresh deploy)
- **Kind**: bug
- **Where**: `src/charm.py:43-46` and `src/components/service_component.py:73-85`
- **Evidence**: In the first review session on Juju 4.0.5, debug-log showed repeated errors from `caasfirewaller` at ~5-20s intervals: `Service "minio" is invalid: [spec.ports[2]: Duplicate value: …, spec.ports[3]: Duplicate value: …]`. The K8s Service had 4 ports — two from `set_ports()` (Juju-managed) and two from `KubernetesServicePatchComponent` (lightkube-managed). In a fresh deploy on the same controller in the deepened session, the Service had exactly 2 clean ports and no caasfirewaller errors — suggesting the duplication is timing-dependent or triggered only after specific config-change sequences. Open issue #238 ("Unit.set_ports is not a drop-in replacement for KubernetsServicePatch library") confirms the maintainers are aware of this interaction. On Juju 3.6.25, `set_ports()` does not manage K8s Service ports, so the issue does not apply.
- **Why it matters**: On Juju 4.x controllers, `unit.set_ports()` manages K8s Service ports directly. Adding a separate `KubernetesServicePatchComponent` that also patches the same Service can create duplicates, causing the controller's `caasfirewaller` worker to crash and restart continuously.
- **Fix**: Remove either `unit.set_ports()` (line 43) or `KubernetesServicePatchComponent` (lines 73-85). On Juju 4.x, `set_ports()` alone is sufficient. If Juju 3.x support is required, condition the Service patch component on the Juju version.
- **Linter rule**: mechanically checkable — a charm linter should flag any charm that uses both `unit.set_ports()` and a K8s Service patch component.

### SSL certificate/key permissions set to 0o511 instead of 0o600/0o644
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:268-271, 273-275, 280-283`
- **Evidence**: `permissions=0o511` is used for `private.key`, `public.crt`, and `root.cert`. Octal `0o511` = `r-x--x--x`. The unit tests (`test_ssl_files`) assert these exact permission bits, cementing the wrong value.
- **Why it matters**: The private key with permissions `0o511` has meaningless execute bits and is world-readable. Expected: `0o600` for private keys, `0o644` for certificates. While inside a container with a dedicated UID/GID, the execute bit on a data file is wrong and indicates carelessness.
- **Fix**: Change private key to `0o600`, certificates and CA to `0o644`.
- **Linter rule**: mechanically checkable — a charm linter should flag `permissions` values that include the execute bit (`& 0o111`) for files pushed to cert/key directories.

### PolicyResourceManager.reconcile called without service mesh, producing 403 errors
- **Severity**: high
- **Kind**: bug
- **Where**: `src/components/service_mesh_component.py:70-75`
- **Evidence**: Debug-log on every reconcile: `httpx.HTTPStatusError: Client error '403 Forbidden' — authorizationpolicies.security.istio.io is forbidden: User "system:serviceaccount:...:minio" cannot list resource "authorizationpolicies"`. The `_configure_app_leader` method calls `self._policy_resource_manager.reconcile(policies=[], ...)` unconditionally at line 70, even when `self.ambient_mesh_enabled` is `False`. The `delete()` method in `lib/charms/istio_beacon_k8s/v0/service_mesh.py:1156` catches 404 (CRD not found) but not 403 (RBAC denied).
- **Why it matters**: Every hook execution (install, config-changed, start) triggers a 403 Forbidden against the Kubernetes API. This is noisy, wastes API calls, and would alarm operators monitoring for security events. The ambient integration test deploys with `trust=True`, masking this issue.
- **Fix**: Guard the `reconcile` call: `if self.ambient_mesh_enabled: self._policy_resource_manager.reconcile(...)`. Also fix the library to catch 403 errors gracefully.
- **Linter rule**: not mechanically checkable in general, but a pattern-based linter could flag unguarded `lightkube` API calls in `_configure_app_leader` methods.

### `secure` flag hardcoded to False regardless of SSL configuration
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:105`
- **Evidence**: `"secure": False` is hardcoded in the `object-storage` relation data, while `_get_minio_endpoint()` (`charm.py:158-166`) correctly switches to `https://` when SSL certs are configured. The `s3-credentials` relation (via `S3ProviderComponent`) correctly derives the endpoint from `_get_minio_endpoint()`.
- **Why it matters**: When SSL is configured, the `object-storage` relation advertises `secure: False` but the endpoint is actually `https://`. Requirers might connect over plain HTTP when they should use HTTPS, or fail unpredictably.
- **Fix**: Derive `secure` from SSL config: `"secure": bool(self.model.config.get("ssl-cert") and self.model.config.get("ssl-key"))`.
- **Linter rule**: mechanically checkable — a charm linter could detect when a boolean flag in relation data contradicts config-derived state elsewhere.

### Charm lacks standard TLS and ingress integration endpoints
- **Severity**: medium
- **Kind**: ux
- **Where**: `metadata.yaml` (missing `requires: certificates` and `requires: ingress`)
- **Evidence**: `juju relate minio self-signed-certificates` failed with "no compatible endpoints". `juju relate minio traefik-k8s` also failed. minio has no `certificates` requires endpoint (TLS is config-based via `ssl-cert`/`ssl-key`/`ssl-ca` options) and no `ingress` requires endpoint. Deployment testing confirmed neither relation could be established.
- **Why it matters**: In the ecosystem, TLS is typically managed via the `certificates` relation (using `tls-certificates` interface), not by pasting base64-encoded certs into config. Operators expect to `juju relate minio self-signed-certificates` to get TLS. The config-based approach also requires the operator to manually obtain and encode certs. Similarly, the lack of an `ingress` endpoint means operators cannot use `traefik-k8s` to expose the MinIO console.
- **Fix**: Add `requires: certificates: interface: tls-certificates` and handle certs from relation data. Consider adding `requires: ingress: interface: ingress` for console exposure. Until then, document the manual TLS setup clearly.
- **Linter rule**: not mechanically checkable — ecosystem design choice.

### Secret key stored in StoredState rather than Juju secrets
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:238-249`
- **Evidence**: `secret = self._stored.secret_key` and `self._stored.set_default(secret_key=secret)` — the auto-generated secret key is persisted in StoredState (plain text in Juju state).
- **Why it matters**: The secret key is stored in plain text in Juju's state, accessible to anyone with model access. Juju offers `juju secrets` for this purpose. Open issue #167 tracks this.
- **Fix**: Use `self.app.add_secret()` / `self.app.get_secret()` from Juju's secrets API.
- **Linter rule**: mechanically checkable — a charm linter could flag use of `StoredState` for credential-like data.

### Excessive K8s API calls from get_status()
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/components/service_component.py:50-52`
- **Evidence**: `KubernetesServicePatchComponent.get_status()` calls `_is_patched()` which makes a K8s API GET to `/api/v1/namespaces/<ns>/services/minio` on every call. The `CharmReconciler` calls `get_status()` multiple times per reconcile, resulting in ~20+ identical GETs per hook event.
- **Why it matters**: Every hook event triggers ~20+ redundant K8s API calls just for status checks. At scale, this adds unnecessary load on the API server.
- **Fix**: Cache the result of `_is_patched()` and invalidate only after `_configure_app_leader` patches the service.
- **Linter rule**: not mechanically checkable — requires reasoning about caching.

### ssl-cert/ssl-key set individually produces misleading log messages
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:267-292`
- **Evidence**: The `_get_files_to_push()` method has `if self.model.config.get("ssl-key") and self.model.config.get("ssl-cert"): ... logger.info("SSL configuration provided...")` followed by an unconditional `logger.info("No SSL configuration provided, skipping file push.")` at line 292. When only one of ssl-cert/ssl-key is set, both messages fire in the same execution cycle. Deployment confirmed: `juju config minio ssl-cert="dGVzdA=="` produced no warning that only one SSL option was set.
- **Why it matters**: An operator who sets only `ssl-cert` or only `ssl-key` gets no warning that both are required. The log is actively misleading — it says both "SSL configuration provided" (when ssl-key+ssl-cert were previously set in a different hook cycle) and "No SSL configuration provided".
- **Fix**: Move the "No SSL" log into an `else:` block. Add an `elif` that warns when only one of the two options is set.
- **Linter rule**: mechanically checkable — a linter could flag log messages about "no configuration" that appear outside the `else` block of the corresponding check.

### Type annotation for `files` variable is wrong
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:270`
- **Evidence**: `files: LazyContainerFileTemplate = []`
- **Why it matters**: The variable is annotated as a single `LazyContainerFileTemplate` but used as a list with `.extend()`. pyright reports: `Cannot access attribute "extend" for class "LazyContainerFileTemplate"`.
- **Fix**: `files: list[LazyContainerFileTemplate] = []`
- **Linter rule**: mechanically checkable — pyright.

### Config values passed to LazyContainerFileTemplate may not be str
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:268, 274, 287`
- **Evidence**: `source_template=self.model.config["ssl-key"]` — `model.config[...]` has type `bool | int | float | str` but `LazyContainerFileTemplate` expects `str`. pyright reports the type mismatch.
- **Why it matters**: If an operator sets `ssl-key` to an integer via YAML, the charm would write the integer's repr as cert content, producing a broken certificate.
- **Fix**: Cast: `source_template=str(self.model.config["ssl-key"])`.
- **Linter rule**: mechanically checkable — pyright.

### relation_id type mismatch in S3ProviderComponent
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/components/s3_provider_component.py:83`
- **Evidence**: `self.s3_provider.set_storage_connection_info(relation_id=relation_id, data=data)` — `relation_id` is `event.relation.id` (int) but `set_storage_connection_info` expects `str`. pyright reports the mismatch.
- **Why it matters**: If the `object-storage-charmlib` is strict about the type, this could fail depending on how it uses relation_id internally. Introduced in PR #300.
- **Fix**: `relation_id=str(event.relation.id)` or fix the library to accept int.
- **Linter rule**: mechanically checkable — pyright.

### _is_patched() does not handle Service with None spec
- **Severity**: low
- **Kind**: bug
- **Where**: `src/components/service_component.py:61-62`
- **Evidence**: `fetched_service_object.spec.ports` — `spec` may be `None`. pyright: `Object of type "None" cannot be used as iterable value`.
- **Fix**: Guard with `if fetched_service_object.spec is None: return False`.
- **Linter rule**: mechanically checkable — pyright.

### No juju actions defined
- **Severity**: low
- **Kind**: ux
- **Where**: no `actions.yaml` exists
- **Evidence**: `juju actions minio` returns "No actions defined for minio."
- **Why it matters**: Operators have no supported way to retrieve the auto-generated secret key or manage users without manually connecting to the workload container. Open issues #168, #179.
- **Fix**: Add `actions.yaml` with at least `get-secret-key` and `add-bucket` actions.
- **Linter rule**: not mechanically checkable.

### No interface tests despite having the test fixture
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/interface_tests/conftest.py`
- **Evidence**: `interface_tester.configure(charm_type=MinIOOperator)` is set up but zero test files exist in `tests/interface_tests/`.
- **Why it matters**: `s3-credentials`, `metrics-endpoint`, `grafana-dashboard`, `velero-backup-config`, and service mesh relations lack interface-level contract tests. Breaking interface changes in library upgrades would not be caught.
- **Fix**: Add interface test files for each relation endpoint.
- **Linter rule**: mechanically checkable — flag directories with only `conftest.py` and no test files.

### MinIO workload reports outdated image
- **Severity**: low
- **Kind**: ux
- **Where**: `metadata.yaml:19`
- **Evidence**: MinIO workload logs: `You are running an older version of MinIO released 4 years ago`. OCI image: `docker.io/charmedkubeflow/minio:ckf-1.10-25a3ea0`.
- **Why it matters**: An old MinIO server misses years of security fixes and features. The warning is shown on workload startup and will concern operators.
- **Fix**: Update the rock/base image to a more recent MinIO release.
- **Linter rule**: not mechanically checkable.

### ruff reports 14 issues, pyright reports 22 errors — neither in CI
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py`, `src/components/*.py`
- **Evidence**: `ruff check src/`: 14 issues (deprecated `typing.List`/`Optional`, import sorting, simplifiable return). `pyright src/`: 22 errors (type mismatches, None-safety, missing imports, wrong annotations). `tox -e lint` passes (pflake8, isort, black only). CI does not include ruff or pyright.
- **Fix**: Add `ruff` and `pyright` to the CI lint pipeline.
- **Linter rule**: N/A — this *is* the linter finding.

### gateway-storage-service silently ignored in server mode
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:186-189,220`
- **Evidence**: When `mode=server`, `_get_minio_args()` returns `["server", "/data", "--certs-dir", ...]` at line 186 without reading `gateway-storage-service` (only read at line 220 in `_get_minio_args_gateway()`). Deployment confirmed: `juju config minio gateway-storage-service=azure` with mode=server produced no warning and charm stayed `active`.
- **Why it matters**: An operator might set `gateway-storage-service` thinking it takes effect, but it is silently ignored in server mode. No validation warns about this.
- **Fix**: Add a config validation that warns or blocks when `gateway-storage-service` is set but `mode` is not `gateway`.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Component architecture with CharmReconciler**: The charm is well-factored into single-responsibility components (`pebble_component.py`, `service_component.py`, `s3_provider_component.py`, `owasp_logging.py`, `service_mesh_component.py`) connected via a dependency graph. Each component declares what events it observes and what it depends on. This is a clean pattern for sidecar charms. (`src/components/*.py`)
- **No-op Pebble layer comparison**: The `PebbleServiceComponent._update_layer()` compares `current_layer.services != new_layer.services` before replanning. Config changes that don't affect the workload don't trigger unnecessary restarts — confirmed in deployment testing.
- **Clear BlockedStatus messages (when validation fires)**: Both the secret-key length check and the gateway mode validation produce readable, actionable BlockedStatus messages with exact requirements — e.g. `The 'secret-key' config value must be at least 8 characters long.`
- **OWASP audit logging for credential changes**: The `OWASPLoggerComponent` emits structured audit events when `secret-key` changes. (`src/components/owasp_logging.py:32-34`)
- **Pebble health checks**: `MinIOPebbleService.get_layer()` defines both `minio-ready` and `minio-alive` checks against MinIO's health endpoints, with 30s periods. Process-kill testing confirmed Pebble auto-restarts the workload. (`src/components/pebble_component.py:44-56`)
- **Integration tests assert real behaviour**: The integration tests connect with `mc` client to create/delete buckets, test console connectivity via curl, verify credential refresh propagates correctly, and check container security contexts — they assert real behaviour, not just active/idle. (`tests/integration/test_charm.py`)
- **CI setup**: GitHub Actions CI runs lint, unit tests, terraform checks, build, release, and integration tests with good failure diagnostics. (`.github/workflows/ci.yaml`)

## Common-practice notes

- **Sidecar pattern**: Follows the standard migration from PodSpec to sidecar. Uses Pebble via `charmed_kubeflow_chisme`'s `PebbleServiceComponent` wrapper. This is the convention in the Kubeflow charm ecosystem.
- **Poetry + tox**: Uses Poetry for dependency management with well-defined dependency groups and tox for orchestration. Follows `charmed-kubeflow-workflows` conventions.
- **Charmcraft 3.x**: Uses `charmcraft.yaml` with explicit `parts` definitions.
- **Library usage**: Vendors charm libraries for `grafana_k8s`, `prometheus_k8s`, `istio_beacon_k8s`, and `velero_libs`. Business logic is in the charm source, not hidden in a PyPI package — good for reviewability.
- **Drift — `unit.set_ports()` plus manual Service patch**: On Juju 4.x, this dual approach creates duplicate K8s Service ports and continuous controller errors. On Juju 3.6, the lightkube patch works cleanly. The charm should pick one approach or condition on Juju version.
- **Drift — no standard TLS/ingress relations**: Most ecosystem charms use `certificates` relation for TLS and `ingress` for exposure. This charm uses config options instead, which prevents integration with `self-signed-certificates` and `traefik-k8s`.
- **Drift — backwards-incompatible endpoint change**: Removing `juju-info` and adding `s3-credentials` between revisions without an intermediate version breaks ecosystem convention of backward-compatible upgrades.
- **Drift — CharmReconciler error handling**: The `except Exception` pattern in `charm_reconciler.py:96-100` silently swallows component failures. This is a framework-level design choice that affects all charms using `charmed_kubeflow_chisme` — failed components do not affect charm status.

## Tests

**Unit tests**: 30 tests, all pass (`tox -e unit`), 30/30, 98% coverage (2 uncovered branches in `s3_provider_component.py:67,100` and `charm.py:254`). Tests cover: leadership gating, object-storage relation (compatible/incompatible/unversioned), config modes (server, gateway with valid/invalid args, invalid mode), secret-key validation, SSL file push (parametrized for full/cert+key/cert-only/none), console port, Prometheus scrape data, K8s Service patch (patched/already-patched), service mesh reconciliation and removal, mesh error handling, endpoint URL with SSL config, and s3-credentials relation (initialised/uninitialised).

**CI lint** (`tox -e lint`): passes — codespell, pflake8, isort, black all clean.

**Tools not in CI:**
- `ruff check src/`: 14 issues (import sorting I001, deprecated `typing.List` UP035/UP006, deprecated `typing.Optional` UP045, simplifiable return SIM103)
- `pyright src/`: 22 errors (type mismatches, None-safety, missing imports, wrong type annotations)
- `codespell`: clean

**Test gaps** (verified against code and deployment findings):
- **No test for the gateway validation bug** (`and` vs `or`): `test_gateway_minio_missing_args` tests `storage=""` (empty, which blocks via `not storage` path) but no test sets `gateway-storage-service="xyz"` to exercise the `storage not in ["s3", "azure"]` path.
- **No test for SSL file permissions** being `0o511`: `test_ssl_files` asserts these exact values, cementing the wrong permissions.
- **No test for SSL file push failure** due to permission-denied on `/minio/` path — the Harness-based tests don't exercise real Pebble file push, so the non-root user permission issue is invisible.
- **No test for `secure` flag derivation** from SSL config.
- **No test for `unit.set_ports()` + `KubernetesServicePatchComponent` interaction** (duplicate ports on Juju 4.x).
- **No test for port validation** (negative, zero values).
- **No test for `gateway-storage-service` set in `server` mode** (silently ignored).
- **No interface tests**: `tests/interface_tests/conftest.py` exists but no test files — all non-`object-storage` relations lack contract tests.
- **No integration test for gateway mode**: Integration tests only exercise server mode.
- **No integration test for SSL configuration**: TLS is not exercised in integration tests.

## Docs

- **README.md**: Good overview covering install, console configuration, and gateway mode with examples. Missing: SSL configuration instructions (and the fact that it's broken), observability integration, how to retrieve credentials, troubleshooting section, upgrade path notes (especially the breaking endpoint change), and the fact that standard `juju relate self-signed-certificates` does not work.
- **CONTRIBUTING.md**: Standard, covers build, test, and deploy instructions, plus Canonical CLA.
- **Charmhub description**: Minimal — just the upstream summary. Docs link points to Discourse (https://discourse.charmhub.io/t/10861).
- **Doc/reality mismatches**:
  - README does not mention that SSL requires manual base64-encoded cert/key config rather than a relation.
  - README gateway example (`gateway-storage-service: azure`) does not document that invalid values cause MinIO to crash silently rather than producing a clear error.
  - No mention of the `juju-info` → `s3-credentials` endpoint change or its upgrade-blocking impact.
  - **Confirmed**: SSL TLS configuration is non-functional — setting `ssl-cert`/`ssl-key` silently fails, but operators would not know this from the docs (or the charm status).
  - No documentation that the charm exposes `velero-backup-config` and `service-mesh` endpoints.

## Open questions

1. **Is the `secure: False` flag intentional for backwards compatibility?** The `object-storage` interface predates the SSL features. The `s3-credentials` relation does advertise `https://` when SSL is configured. Would changing `secure` to match SSL config break existing requirers?
2. **Why is the OCI image 4 years old?** The MinIO workload logs warn about an old version. Is this a deliberate pin for Kubeflow stability, or is an image refresh pending?
3. **Does the `ssl-ca` config option work?** The code writes `CAs/root.cert` but SSL is entirely broken due to the Pebble permission issue — this cannot be tested until the path issue is fixed.
4. **What is the migration plan for the `juju-info` → `s3-credentials` endpoint change?** The deployed rev 694 still has `juju-info`, while HEAD fd979cd removes it and adds `s3-credentials`. The upgrade is blocked between some channel pairs. Is there a documented migration path for existing deployments?
5. **Should CharmReconciler propagate component exceptions to status?** Currently it logs and continues, which means component failures (SSL push, mesh reconcile) are invisible to operators. This is a framework design question for `charmed_kubeflow_chisme`.
6. **Why does Pebble run as the non-root UID 584792?** The `charm-user: non-root` in `metadata.yaml` causes the entire container (including Pebble PID 1) to run as the specified UID. This means Pebble cannot create directories in the rootfs. Was the `/minio/` path expected to be pre-created in the OCI image, or should the charm use paths under the existing `/data/` volume?
7. **Is the duplicate-port issue reproducible?** The first review session observed it on Juju 4.0.5; the deepened session on the same controller did not. It may depend on the timing of K8s Service admission webhook processing vs lightkube patching. More investigation is needed.
8. **Why doesn't the refresh to add endpoints work?** Juju appears to reject charm upgrades that add new relation endpoints (e.g., `s3-credentials`) while accepting downgrades that remove them. This needs verification against the Juju upgrade policy documentation.
