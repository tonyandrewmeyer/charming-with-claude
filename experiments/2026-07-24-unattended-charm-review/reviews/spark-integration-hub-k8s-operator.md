# spark-integration-hub-k8s

A cleanly-structured K8s sidecar charm that centralises Spark configuration for the Charmed Apache Spark ecosystem, bridging relations (S3, Azure Storage, COS, Loki logging) into Spark properties injected into Kubernetes secrets per service account. The codebase is well-organised, passes all 72 unit tests (83% coverage), and deploys successfully on both Juju 3.6 and 4.0 controllers. It is not production-ready as-is: a config-validation bug bricks the charm on **any** hook (not just config-changed) until the bad config is fixed externally, and a relation-removal handler leaves stale config behind. A maintainer should fix Finding #1 (validation crash) and Finding #2 (`_on_service_account_released` not calling `update()`) first — both are correctness bugs with straightforward fixes — then address the missing `update-status` observation and the status-hook I/O cost (Findings #5–#7).

| | |
|---|---|
| Repo | canonical/spark-integration-hub-k8s-operator @ `4bb5a34` (2026-07-09) |
| Charms | spark-integration-hub-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5) and concierge-k8s-3 (Juju 3.6.25), both 3/edge rev 142. Deep-dive on both controllers: S3 integrator, config round-trips, pod kill/recovery, process kill auto-restart, config crash traceback analysis, service account monitoring via config, secret creation/deletion lifecycle, stop-hook cleanup verification, config file corruption/recovery, and label analysis. |
| Reviewed | 2026-07-30 |

## What it does

1. **Aggregates relations** — connects to S3 integrator, Azure Storage integrator, COS (Prometheus Pushgateway), and Loki logging, translating relation data into Spark configuration properties (e.g. `spark.hadoop.fs.s3a.access.key`, `spark.eventLog.dir`).
2. **Monitors service accounts** — watches Kubernetes service accounts specified via the `spark-service-account` relation or the `monitored-service-accounts` config.
3. **Publishes configs via the `spark-service-account` relation** — consumer charms (e.g. Kyuubi) receive Spark properties and a Kubernetes resource manifest containing secrets to mount.
4. **Provides a Pebble workload** — runs a `monitor_sa.sh` script inside the `integration-hub` container that watches service accounts and injects configuration secrets.

## Deployment log

```
# --- Juju 4.0.5 on microk8s ---
juju switch concierge-k8s-4
juju add-model rv-sihub-k8s-4
juju deploy spark-integration-hub-k8s --channel 3/edge --trust
# → rev 142, active after ~90s

# --- Juju 3.6.25 on microk8s ---
juju switch concierge-k8s-3
juju add-model rv-sihub-k8s-3
juju deploy spark-integration-hub-k8s --channel 3/edge --trust
# → rev 142, active after ~90s (same revision, same behaviour)

# Config changes work on both controllers:
juju config spark-integration-hub-k8s enable-dynamic-allocation=true
juju config spark-integration-hub-k8s spark-image=test-image:latest
# → spark-properties.conf updated

# Scale to 2 units → BlockedStatus on both controllers
juju scale-application spark-integration-hub-k8s 2
# → "Integration Hub can be run with only one unit."
# Scale back to 1: recovers cleanly

# S3 integration deployed and related (both controllers):
juju deploy s3-integrator --channel 2/stable
juju integrate spark-integration-hub-k8s s3-integrator
# Configure S3 with fake credentials via Juju secrets:
juju add-secret s3-creds --file /path/to/creds.yaml
juju grant-secret s3-creds s3-integrator
juju config s3-integrator credentials=secret:<id>
# → BlockedStatus: "Invalid S3 credentials" (correct behaviour)
# Remove relation: recovers to active

# juju refresh between revisions:
juju refresh spark-integration-hub-k8s --channel 3/stable
# → rev 134 deployed, charm recovers to active
juju refresh spark-integration-hub-k8s --channel 3/edge
# → rev 142 deployed, charm recovers to active

# Additional deep-dive testing on k8s-4:
juju add-model rv-sihub-deep
juju deploy spark-integration-hub-k8s --channel 3/edge --trust

# S3 integration with fake credentials:
juju deploy s3-integrator --channel 2/stable
juju integrate spark-integration-hub-k8s s3-integrator
juju add-secret s3-creds-deep --file ~/s3-creds.yaml
juju grant-secret s3-creds-deep s3-integrator
juju config s3-integrator credentials=<secret-uri>
juju config s3-integrator bucket=test-bucket endpoint=http://s3.example.com
# → Hub remains active while s3-integrator is blocked trying to create bucket

# Config change round-trip:
juju config spark-integration-hub-k8s enable-dynamic-allocation=true
# → spark-properties.conf gets DynamicAllocation keys
juju config spark-integration-hub-k8s spark-image=test-image:v1
# → spark-properties.conf adds spark.kubernetes.container.image
juju config spark-integration-hub-k8s enable-dynamic-allocation=false
# → DynamicAllocation keys removed, image key remains
# Confirms config changes are correctly propagated

# Kill workload:
juju ssh --container integration-hub spark-integration-hub-k8s/0 "pebble stop integration-hub"
# → juju status stays "active" (no update-status hook)
# → Next relation-changed triggers status update to BlockedStatus

# Pebble plan confirms startup:enabled from container image:
# services:
#     integration-hub:
#         startup: enabled  (from base layer)
#         on-success: restart  (added by charm)
#         on-failure: restart  (added by charm)

# Teardown on both models:
juju destroy-model rv-sihub-deep --force --no-wait --destroy-storage
juju remove-application spark-integration-hub-k8s --force
# → Application removed cleanly
# → No K8s secrets left behind (but see Finding #3: labelling inconsistency, no secrets existed to begin with in this run)
```

## Observed behaviour

- **Deploy to active**: ~90 seconds from deploy to active/idle on both Juju 3.6.25 and 4.0.5 (container image pull dominates). Behaviour is identical across Juju versions.
- **Startup hook sequence**: install → hub-peers-relation-created → leader-elected → config-changed → start → integration-hub-pebble-ready. The charm emits "Waiting for Pebble" maintenance status during initialisation.
- **Pebble layer**: The `integration-hub` service runs `/bin/bash /opt/hub/bin/monitor_sa.sh` with environment `SPARK_PROPERTIES_FILE`, `SA_ALLOWLIST`, `TRUSTSTORE_PATH`, `TRUSTSTORE_SECRET_NAME`. The container image's base layer sets `startup: enabled` and `on-success: restart`; the charm's `start()` method adds `on-failure: restart` and `environment`, then calls `container.restart()`. The unit-test fixture in `tests/unit/conftest.py:77` uses `"startup": "disabled"`, which diverges from the real image (see Finding #8).
- **Config validation crash (both Juju versions)**: Setting `monitored-service-accounts=badformat` or `monitored-service-accounts=bad` (missing the required colon) crashes the **next** hook that fires, not necessarily config-changed. The ops framework constructs a new charm instance on every hook, and `__init__` accesses `self.charm.config` via event handler construction (`charm.py:39-44`). `TypedCharmBase.config` calls `self.config_type(**translated_keys)`, triggering pydantic validation. Traceback: `charm.py:39` → `S3Events.__init__` → `TypedCharmBase.config` → `ValidationError`. The unit enters `error` state with `hook failed: "config-changed"`. Fixing the config and `juju resolve` recovers cleanly.
- **Config changes propagate correctly**: Setting `enable-dynamic-allocation=true` adds the expected Spark properties; setting it back to `false` removes them. `spark-properties.conf` is empty when no integrations or config are active. This works because the charm is re-constructed on each hook, so `IntegrationHubManager.config` always captures current state.
- **Killed workload — two scenarios**:
  - `pebble stop integration-hub`: `juju status` stays "active" because no `update-status` hook exists. The service stays inactive until a config change or relation event fires `update()` → `restart()`. On the next event, `_on_collect_status` correctly shows "Integration Hub is not running. Please check logs."
  - `pkill -9 -f monitor_sa`: Pebble's `on-failure: restart` auto-restarts the service within seconds (verified: PID 52→93 after SIGKILL). Works correctly.
- **Pod kill and recovery**: `kubectl delete pod` forces a full pod restart. The charm goes to "Waiting for Pebble" maintenance, then pebble-ready fires ~50s later, and the charm recovers to active. The base layer's `startup: enabled` ensures the service auto-starts before the charm hook runs.
- **Pod resource usage**: 72Mi memory, 1m CPU for the whole pod (2 containers: charm + integration-hub). Very lightweight.
- **juju refresh**: Refreshing rev 142 (3/edge) → rev 134 (3/stable) → rev 142 (3/edge) works cleanly; the charm recovers to active after each refresh.
- **No actions**: The charm defines no `actions.yaml` and thus no Juju actions.
- **No separate TLS integration**: No `certificates` relation in `metadata.yaml`. TLS is only supported via the `tls-ca-chain` field in S3 relation data — `self-signed-certificates` cannot be directly related.
- **S3 integration with bad credentials**: Deployed `s3-integrator` (2/stable rev 544), related, configured with a fake endpoint/credentials. The hub remains active with empty spark-properties until `s3-integrator` provides credentials. With unreachable credentials, the hub correctly shows `BlockedStatus("Invalid S3 credentials")`. Removing the S3 relation recovers to active with S3 properties removed from the file. The s3-integrator must verify the bucket before sharing credentials via Juju secrets; if bucket creation fails, the hub never receives credentials and stays active — this is correct behaviour.
- **Service account monitoring via config**: Deployed a test service account labelled `app.kubernetes.io/managed-by=spark8t` and added it to `monitored-service-accounts`. `monitor_sa` correctly watched the labelled SA and injected Spark properties as a K8s secret in the SA's namespace (confirmed: secret `integrator-hub-conf-spark-sa-labeled` in namespace `test-sa-monitor`). Secret content updates correctly on config change (e.g. disabling dynamic allocation removes the relevant keys). When the SA is removed from the allowlist, the K8s secret is **not** cleaned up — it stays orphaned (Finding #18). The monitor script always does GET→DELETE→POST on every update cycle, even when content is unchanged (Finding #17).
- **Stop-hook cleanup verification (revised)**: On normal removal (without `--force --no-wait`), the stop hook fires and correctly deletes secrets labelled `app.kubernetes.io/managed-by=integration-hub`. Confirmed by deploying, configuring SAs, then removing — secrets in the monitored namespace were deleted. With `--force --no-wait`, the stop hook appears to be skipped (secrets remained). This supersedes an earlier draft claim that cleanup was broken due to a label mismatch — the label actually matches (`managed-by` in both the monitor script and `INTEGRATION_HUB_LABEL`); `generated-by` is used only in the YAML manifests sent to consumer charms, never applied directly by the hub. See Finding #3.
- **Config file corruption recovery**: Manually writing garbage to `spark-properties.conf` in the container did not crash the workload. A subsequent config change correctly overwrote the file and restarted the service. No error status was surfaced for the corrupted file — the charm stayed "active" throughout.
- **Per-hook construction cost**: Because the charm is re-constructed on every hook, every event handler class creates a new `IntegrationHubManager`, which creates a new lightkube `Client` via `KubernetesManager.__init__`. `_on_collect_status` additionally creates a fresh `KubernetesManager` and `S3Manager` on every invocation. On a simple config change the debug-log shows 3 K8s API calls (`SelfSubjectAccessReview`).

## Findings

### 1. Config validation errors crash the charm instead of surfacing BlockedStatus — bricks every hook, not just config-changed

- **Severity**: high
- **Kind**: bug
- **Where**: `src/core/config.py:24-42` via `TypedCharmBase.config`, accessed from `src/charm.py:39-44`
- **Evidence**: Setting `monitored-service-accounts=badformat` (or `bad` — anything missing the `namespace:sa` colon) crashes the charm on the next hook dispatch. Traceback from Juju 4.0.5 at rev 142:
  ```
  File "src/charm.py", line 39, in __init__     # self.s3 = S3Events(self, ...)
  File "src/events/s3.py", line 39, in __init__ # IntegrationHubManager(..., self.charm.config)
  File "lib/charms/data_platform_libs/v0/data_models.py", line 207, in config
  File "pydantic/main.py", line 263, in __init__
  pydantic.ValidationError: 1 validation error for CharmConfig
    Value error, Malformed monitored-service-accounts options.
  ```
  The unit enters `error` state with `hook failed: "config-changed"`. Fixing the config and `juju resolve` recovers cleanly.
- **Root cause**: The ops framework constructs a new charm instance on **every** hook dispatch, not just config-changed. The constructor's event handler classes each call `IntegrationHubManager(..., self.charm.config)`. `TypedCharmBase.config` is a property that calls `self.config_type(**translated_keys)`, triggering pydantic validation on every hook.
- **Impact**: Any hook that fires after bad config is set crashes, bricking the unit entirely. An operator gets `hook failed` with no actionable message in `juju status`. The unit cannot process relations, pebble-ready, or any Juju event until config is fixed externally.
- **Fix**: Move config validation out of the pydantic model constructor path and into `_on_collect_status`, where it can surface `BlockedStatus`. Alternatively, wrap `self.charm.config` in a try/except in `__init__` and set a flag so handlers can emit BlockedStatus. Least-invasive: make `monitored_service_accounts_validator` accept any string and do parsing in `_on_collect_status`.
- **Linter rule**: "`TypedCharmBase.config` is accessed in a charm `__init__` without a try/except for `pydantic.ValidationError`" — mechanically checkable.

### 2. `_on_service_account_released` does not call `update()` — stale config after relation removal

- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/provider.py:72-90`
- **Evidence**: `_on_service_account_requested` (line 69) calls `self.integration_hub.update()` after creating the service account. `_on_service_account_released` (line 88) deletes the service account but never calls `update()`.
- **Impact**: The allowlist file retains the stale service-account entry; `spark-properties` and `resource-manifest` for remaining service accounts are not regenerated; the workload isn't restarted to pick up the change. The integration hub continues watching the deleted SA and may attempt to inject secrets into a namespace with no client. Stale state persists until the next config change or relation event.
- **Fix**: Add `self.integration_hub.update()` at the end of `_on_service_account_released`, after deleting the service account.
- **Linter rule**: "Event handler for relation removal does not call the charm's reconciler/update method" — mechanically checkable with pattern matching on relation-broken/released handlers.

### 3. `monitored-service-accounts` regex rejects valid Kubernetes namespace names containing dots

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/core/config.py:35`
- **Evidence**: The regex `r"[a-z0-9A-Z\*](?:[a-z0-9\-\*]{0,61}[a-z0-9\*])?$"` requires names to start/end with alphanumeric or `*` and does not allow `.`, which is valid in Kubernetes namespace names (e.g. `team-a.namespace`).
- **Impact**: Operators using namespaces or service accounts with dots cannot use this config option.
- **Fix**: Expand the pattern to include dots; use `re.fullmatch` instead of `re.match` to avoid partial matches; document allowed syntax.
- **Linter rule**: not mechanically checkable (requires knowledge of valid K8s names).

### 4. `_on_collect_status` calls `KubernetesManager.trusted()` on every status evaluation

- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:56-57`
- **Evidence**:
  ```python
  k8s_manager = KubernetesManager(self.model.app.name)
  if not k8s_manager.trusted():
  ```
  `trusted()` creates a new `Client` and performs a `SelfSubjectAccessReview` API call on every `collect_unit_status`/`collect_app_status` event.
- **Impact**: `collect_*_status` fires frequently. Making a K8s API call on every status evaluation is unnecessary; trust status rarely changes during a charm's lifetime.
- **Fix**: Cache the trusted status at init or with a TTL; re-check only on config change or `upgrade-charm`.
- **Linter rule**: "Hook handler creates a fresh Kubernetes client and calls the API server on every invocation" — plausibly mechanically checkable (pattern: `KubernetesManager(...)`/`Client(...)` called outside `__init__`).

### 5. `S3Manager.verify()` is called on every `collect_status` evaluation, uncached, and can propagate unhandled `RetryError`

- **Severity**: medium
- **Kind**: bug / performance
- **Where**: `src/charm.py:63-66`, `src/managers/s3.py:62-94`
- **Evidence**:
  ```python
  if self.context.s3:
      s3_manager = S3Manager(self.context.s3)
      if not s3_manager.verify():
  ```
  `verify()` makes real S3 API calls (`list_objects_v2`, `put_object`, potentially `create_bucket`) on every status collection. `_verify_bucket_and_path` is decorated with `@retry(stop=stop_after_attempt(2), ...)`: on `NoSuchBucket` it creates the bucket then re-raises to trigger the retry. If the retry also fails, tenacity raises `RetryError`, which neither `verify()` nor `_on_collect_status` catches — it propagates unhandled and crashes the status hook.
- **Impact**: Status evaluation makes expensive network calls repeatedly (`collect_*_status` can fire multiple times per hook cycle), and a transient S3 failure crashes the charm's event loop with an unhandled `RetryError`, putting the unit into error state with no recovery path until the next hook.
- **Fix**: Cache verification results, invalidating on S3 relation-changed/broken; add a timeout to S3 client calls; wrap `_verify_bucket_and_path` calls with a try/except that returns `False` on `RetryError` (or use tenacity's `retry_error_callback`).
- **Linter rule**: "Network I/O (boto3 client calls) inside `collect_unit_status`/`collect_app_status` handler" — mechanically checkable by detecting `boto3` usage in status handlers. The `RetryError` path is not mechanically checkable.

### 6. No `update-status` hook — workload death goes undetected

- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py` — `on.update_status` is not observed
- **Evidence**: On both controllers, `pebble stop integration-hub` kills the service but `juju status` continues to show "active" until an external event (relation change, config change) fires. Confirmed on both Juju 3.6.25 and 4.0.5.
- **Impact**: A crashed workload goes undetected until the next hook fires; an operator running `juju status` sees "active" while the service is dead. Pebble's `on-failure: restart` only covers process crashes (non-zero exit), not `pebble stop` or OOM kills.
- **Fix**: Observe `self.on.update_status` and route it to `_on_collect_status`. Juju fires `update-status` every 5 minutes by default.
- **Linter rule**: "Charm does not observe `update-status`" — mechanically checkable.

### 7. `SparkServiceAccountRequirerEventHandlers._on_secret_changed_event` missing `return` after ignoring self-owned secrets

- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/spark_integration_hub_k8s/v0/spark_service_account.py:458-459`
- **Evidence**:
  ```python
  if relation.app == self.charm.app:
      logging.info("Secret changed event ignored for Secret Owner")
  remote_unit = None
  for unit in relation.units:
      if unit.app != self.charm.app:
          remote_unit = unit
  getattr(self.on, "properties_changed").emit(relation, app=relation.app, unit=remote_unit)
  ```
  Execution falls through to emit `properties_changed` even when the secret owner is the charm itself, despite logging "ignored".
- **Impact**: Consumer charms receive spurious `properties_changed` events. For a hub with many service-account relations, each secret write by the hub can trigger spurious events on consumer relations, causing unnecessary config re-renders and restarts downstream.
- **Fix**: Add `return` after the "ignored" log line.
- **Linter rule**: "Conditional block logging 'ignored'/'skipped' without a subsequent `return` or `continue`" — mechanically checkable.

### 8. Inconsistent K8s labels: manifests use `generated-by`, secrets use `managed-by`

- **Severity**: low
- **Kind**: ux
- **Where**: `src/common/utils.py:99,120` vs `src/managers/k8s.py:76`
- **Evidence**: `get_hub_secret_manifest` and `get_hub_truststore_secret_manifest` (`src/common/utils.py:99,120`) generate YAML manifests carrying `app.kubernetes.io/generated-by: integration-hub`; these are sent to consumer charms over `spark-service-account` as `resource-manifest` data for the consumer to apply. Meanwhile `monitor_sa` creates secrets directly with `app.kubernetes.io/managed-by: integration-hub`, and the stop-hook cleanup (`delete_secrets`, `src/managers/k8s.py:76`) uses `managed-by` — which correctly matches the secrets the hub creates directly (confirmed by deploy/configure/remove cycle). The `generated-by` label applies only to consumer-created secrets and would not be cleaned up by the hub.
- **Impact**: Low practical impact today — cleanup works for the secrets the hub creates directly — but the two labels invite confusion during debugging, and if a future change has the charm applying its own manifests, cleanup would silently miss them.
- **Fix**: Use one label constant (e.g. `INTEGRATION_HUB_LABEL`) consistently across `get_hub_secret_manifest` and the monitor script, or document the distinction explicitly.
- **Linter rule**: "K8s label string literal duplication across creation and deletion paths" — mechanically checkable.

### 9. Pebble service `startup` relies on container image, not set explicitly by charm

- **Severity**: low
- **Kind**: ux
- **Where**: `src/workload.py:97-116` (`start()`)
- **Evidence**: `start()` adds `on-failure: restart` to the Pebble layer but never sets `startup`. The published image's base layer includes `startup: enabled`, so the service does auto-start after Pod restart — but the unit test fixture (`tests/unit/conftest.py:77`) uses `"startup": "disabled"`, meaning unit tests don't exercise this path and a base-image change could silently break Pod recovery.
- **Impact**: Low immediate risk (published image is correct today) but an undeclared dependency on the base layer is a robustness gap.
- **Fix**: Explicitly set `"startup": "enabled"` in `start()`, or document the requirement on the base layer.
- **Linter rule**: not mechanically checkable.

### 10. `_remove_resources` (stop handler) swallows exceptions silently

- **Severity**: low
- **Kind**: bug
- **Where**: `src/events/integration_hub.py:52-55`
- **Evidence**:
  ```python
  try:
      hub_conf: CharmConfig = self.charm.config
      self.k8s_manager.delete_secrets(hub_conf.monitored_service_accounts)
  except Exception:
      self.logger.error(f"Could not delete secret with label {INTEGRATION_HUB_LABEL}")
  ```
  The exception object itself is discarded — only a static message is logged.
- **Impact**: Operators cannot diagnose why cleanup failed after removing the application.
- **Fix**: `except Exception as e: self.logger.error(f"Could not delete secrets: {e}")`.
- **Linter rule**: "`except Exception` without logging the exception object" — mechanically checkable.

### 11. `.keep` file written as S3 write-verification artifact, never cleaned up

- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/s3.py:78-82`
- **Evidence**:
  ```python
  s3.put_object(
      Bucket=self.connection_info.bucket,
      Key=f"{self.connection_info.path}/.keep",
      Body=b"",
  )
  ```
  A zero-byte `.keep` file is written on every verification (`_on_collect_status`) and never removed.
- **Impact**: Minor litter in the S3 bucket, rewritten frequently since `verify()` runs on every status evaluation.
- **Fix**: Use `head_bucket` for an existence check instead, or delete the `.keep` file after verification.
- **Linter rule**: not mechanically checkable.

### 12. `IntegrationHubConfig` constructs `S3Manager`/`AzureStorageManager` even when credentials may be invalid

- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/integration_hub.py:44-45`
- **Evidence**:
  ```python
  self.s3 = S3Manager(s3) if s3 else None
  self.azure_storage = AzureStorageManager(azure_storage) if azure_storage else None
  ```
  These managers are constructed whenever relation data exists, before `verify()` is checked, coupling config rendering with credential verification.
- **Impact**: If S3 relation data is incomplete (e.g. missing `access-key`), the manager holds invalid credentials until `verify()` fails elsewhere; the dual purpose of `S3Manager` (rendering + verification) makes the data flow harder to follow.
- **Fix**: Decouple `IntegrationHubConfig` from `S3Manager` (pass raw `S3ConnectionInfo`), or add a `verified` parameter.
- **Linter rule**: not mechanically checkable.

### 13. `assert` statements in integration tests lack assertion messages

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py:75-78` and elsewhere
- **Evidence**: `assert does_secret_exist(...)` / `assert not does_secret_exist(...)` with no message.
- **Impact**: Cryptic CI failures.
- **Fix**: Add descriptive messages, e.g. `assert does_secret_exist(...), f"Secret {SECRET_NAME_PREFIX}{name} not found in namespace {namespace}"`.
- **Linter rule**: not mechanically checkable generally, but could be a lint rule scoped to test files.

### 14. Config model uses pydantic `Field(default="")` for a `list[str]` field

- **Severity**: low
- **Kind**: bug
- **Where**: `src/core/config.py:21`
- **Evidence**:
  ```python
  monitored_service_accounts: list[str] = Field(default="")
  ```
  The default (`str`) doesn't match the annotated type (`list[str]`); it only works because a `pre=True` validator (`monitored_service_accounts_validator`) coerces it.
- **Impact**: Fragile — a future refactor that removes or reorders the pre-validator would break silently.
- **Fix**: `Field(default_factory=list)` or `Field(default=[])`.
- **Linter rule**: "pydantic Field default type does not match field type annotation" — mechanically checkable with mypy/pyright.

### 15. `tls.reset()` failure is silently caught in `update()` — stale TLS state possible

- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/integration_hub.py:349-353`
- **Evidence**:
  ```python
  try:
      self.tls.reset()
  except Exception as e:
      self.logger.warning(f"Failed to reset truststore path: {e}.")
  finally:
      self.context.cluster.set_truststore_path("")
  ```
  If `reset()` fails, the `finally` still clears the truststore path even though the underlying file may not have been deleted.
- **Impact**: A corrupted or undeletable truststore file (permissions, read-only fs) could persist silently; TLS verification could use stale certificates.
- **Fix**: If `reset()` fails while TLS was previously configured, move to `BlockedStatus` instead of continuing silently.
- **Linter rule**: not mechanically checkable.

### 16. Monitor script always performs DELETE+CREATE cycle on secrets, even when content is unchanged

- **Severity**: low
- **Kind**: performance
- **Where**: container workload script `monitor_sa` (OCI image at `ghcr.io/canonical/spark-integration-hub`, not charm source)
- **Evidence**: Pebble logs during config changes show GET 200 → DELETE 200 → POST 201 for every service-account event cycle, regardless of whether Spark properties actually changed.
- **Impact**: For many service accounts, each config change generates unnecessary K8s API calls (2 + N×3), adding API-server load and latency before updated config is live.
- **Fix**: Compare existing secret data with the new config before deleting; only delete+create if content differs.
- **Linter rule**: not mechanically checkable (bug is in the OCI image, not the charm source).

### 17. Monitor script does not clean up secrets when a service account is removed from the allowlist

- **Severity**: low
- **Kind**: bug
- **Where**: container workload script `monitor_sa` (OCI image, not charm source)
- **Evidence**: Clearing `monitored-service-accounts` correctly emptied the allowlist file, but the previously-created secret (`integrator-hub-conf-spark-sa-labeled`) remained in `test-sa-monitor`. Charm status stayed "active" with no indication of the orphaned secret. It's only deleted if the SA is re-added and reprocessed.
- **Impact**: Stale secrets (potentially with outdated Spark config) accumulate in monitored namespaces and can still be picked up by consumer applications.
- **Fix**: On start, compare secrets the monitor script manages against the current allowlist and delete any that no longer match.
- **Linter rule**: not mechanically checkable (bug is in the OCI image).

### 18. Monitor script fetches non-existent truststore secret on every cycle

- **Severity**: low
- **Kind**: performance
- **Where**: container workload script `monitor_sa` (OCI image, not charm source)
- **Evidence**: Pebble logs show `GET .../secrets/integrator-hub-conf-truststore-* → 404` on every SA processing cycle, even with no TLS configured.
- **Impact**: Minor unnecessary API-server load on every cycle.
- **Fix**: Cache the 404 after the first check, or skip the lookup unless `TRUSTSTORE_PATH` is non-empty.
- **Linter rule**: not mechanically checkable (bug is in the OCI image).

## Worth copying

- **Clean reconciler pattern in `_on_collect_status`** (`src/charm.py:49-68`): status logic centralised via `event.add_status()`, letting Juju's `collect_*_status` pick the most severe status, avoiding scattered `self.unit.status = ...` assignments.
- **`_compare_and_update_file`** (`src/managers/integration_hub.py:272-294`): reads existing config file content, compares it (sorted, set-based), and only writes/restarts if content actually changed — avoids unnecessary workload restarts.
- **Typed config via `CharmConfig(BaseConfigModel)`** (`src/core/config.py`): pydantic-based config validation with pre-validators — a good pattern, notwithstanding the crash-on-validation-failure bug (Finding #1).
- **`defer_when_not_ready` decorator** (`src/events/base.py:18-28`): defers all event handlers when the workload container isn't connectable, avoiding scattered `if not container.can_connect(): event.defer(); return`.
- **Separation of concerns**: domain objects (`core/domain.py`), context parsing (`core/context.py`), workload abstractions (`core/workload.py`, `workload.py`, `common/k8s.py`), event handlers (`events/`), and managers (`managers/`) are cleanly separated.
- **Comprehensive proxy support** (`src/common/utils.py:87-143`, `src/managers/integration_hub.py:116-155`): handles `JUJU_CHARM_HTTP_PROXY`, `JUJU_CHARM_HTTPS_PROXY`, `JUJU_CHARM_NO_PROXY` with CIDR/suffix matching, and applies S3 proxy configuration when set. 22 parametrized test cases in `tests/unit/test_component_utils.py`.
- **TLS via truststore** (`src/managers/tls.py`): imports CA certificates into a Java truststore (keytool), stores the password in peer relation data, and injects truststore secrets into the resource manifest — a complete, careful TLS integration.
- **Well-documented library** (`lib/charms/spark_integration_hub_k8s/v0/spark_service_account.py`): full usage examples for both provider and requirer sides.

## Common-practice notes

- Uses `TypedCharmBase`/`BaseConfigModel` from `data_platform_libs` — the standard Data Platform team pattern for typed config. The crash-on-validation-failure issue (Finding #1) is a known pain point of this pattern when `self.charm.config` isn't wrapped in try/except.
- Three-part OCI image reference in `metadata.yaml` (digest + comment giving the tag) — Data Platform convention, good for reproducibility.
- `concierge.yaml` and `spread.yaml` follow the team's standardized CI test-environment setup (LXD VMs with microceph for S3-backed integration tests).
- Poetry with charmcraft 3, `poetry` plugin with separate `poetry-deps`/`charm-poetry` parts — the modern Data Platform approach.
- Library under `lib/charms/spark_integration_hub_k8s/v0/`, well-documented with usage examples for both sides.
- No `actions.yaml` — for a configuration hub, `list-config` or `show-manifest` actions would help debugging.
- `juju trust` required — the charm checks trust via `SelfSubjectAccessReview` and blocks with an actionable message if untrusted; appropriate for a charm managing K8s secrets across namespaces.
- Behaviour identical across Juju 3.6.25 and 4.0.5 — deployment, config changes, relation handling, failure injection, and recovery all match. No Juju-version-specific issues found.

## Tests

### Unit tests (72 tests, all passing, 83% coverage)

- **Framework**: pytest + ops-scenario
- **Run**: `PYTHONPATH=src:lib poetry run pytest tests/unit/ -v` — all 72 pass in ~4.3s.
- **Coverage** (`coverage report --show-missing`):

  | Module | Coverage | Missing |
  |---|---|---|
  | `src/charm.py` | 88% | 60-62, 65, 76 ("not trusted", "multiple units", "multiple storage", "not running" branches) |
  | `src/events/provider.py` | 62% | 54, 57, 65, 74-90 (non-leader paths, `_on_service_account_released`) |
  | `src/managers/k8s.py` | 39% | 30, 34-52, 57-62, 67, 71-102 (nearly all `KubernetesManager` methods are mocked) |
  | `src/managers/s3.py` | 85% | dedicated `test_s3_managers.py` |
  | `src/managers/integration_hub.py` | 92% | — |
  | `src/workload.py` | 75% | exec wrappers for service account create/delete/get-manifest |
  | `src/common/k8s.py` | 64% | exec, read_bytes, write paths |
  | **Overall** | **83%** | 1105 statements, 157 missed, 32 partial branches |

- **Coverage gaps**:
  - No unit test for `NOT_TRUSTED` status (`src/charm.py:60-62`)
  - No unit test for `MULTIPLE_UNITS` status (`src/charm.py:65`)
  - No unit test for `MULTIPLE_OBJECT_STORAGE_RELATIONS` status (`src/charm.py:68-69`)
  - No unit test for `NOT_RUNNING` status (`src/charm.py:76`)
  - No unit test for `KubernetesManager.delete_secrets()` (the entire `stop` hook path)
  - No unit test that `_on_service_account_released` calls `update()` (Finding #2 — the gap is the missing call itself, not just an untested branch)
  - No unit test exercising the `_none` flags (`set_s3_none`, `set_azure_storage_none`, `set_pushgateway_none`, `set_loki_url_none`) on `update()` individually
  - No unit test for `_remove_resources` (the `stop` event handler)
  - No unit test for non-leader paths in `_on_service_account_requested`/`_on_service_account_released`
- **Test quality**: good — scenario-based state transitions asserting specific properties written to the container filesystem, not just status values. `parse_spark_properties` validates individual keys. Proxy-skip tests are parametrized with 22 cases (exact match, CIDR, suffix, edge cases, empty inputs).

### Integration tests

- **Framework**: jubilant + pytest, run via `tox run -e integration-{suite}` on concierge/spread.
- **Suites**: integration-charm, integration-provider, integration-observability, integration-tls, integration-trust.
- **Quality**: asserts specific behaviour (`does_secret_exist()`, `get_secret_data()`) rather than just active/idle. Not run as part of this review (require spread/microceph environment).

### Static analysis

- **ruff**: `poetry run ruff check --config pyproject.toml src/` — all checks pass.
- **mypy**: `poetry run mypy src/` — no issues in 27 source files.
- **codespell**: `poetry run codespell src/` — no typos.

## Docs

- **README.md**: good — covers what the charm does, usage examples, links to contributing. Shows a complete flow: deploy hub, deploy s3-integrator, configure S3, relate, create service accounts with the spark-client snap, verify config.
- **CONTRIBUTING.md**: brief but functional — covers tox environments and `charmcraft pack`.
- **Charmhub description**: matches metadata; generic without being misleading.
- **`spark_service_account.py` library**: excellent docstring with full usage examples for both provider and requirer sides.
- **No observed docs/reality mismatch**: README's `s3-integrator --channel 2/stable` matches current `object-storage` library usage.

## Open questions

1. **ARM64 support**: `charmcraft.yaml` declares `ubuntu@22.04:arm64` but the OCI resource digest (`sha256:60d965c9dafd9c9c32165639fcbf6523966ca7bd630a248f6c361188715805d7`) appears architecture-specific. Is there a separate ARM64 digest? Charmhub shows arm64 builds for 3/stable (rev 133) but amd64 for 3/edge (rev 142).
2. **Force-destroyed models**: if a model is force-destroyed or the controller wiped, K8s secrets are orphaned regardless of the stop-hook fix, since the stop hook never runs. Would an ownerReference on the `Secret` (pointing to the Juju application) prevent orphaned secrets? *(unverified — not tested in this review)*
3. **Test fixture divergence**: why does `tests/unit/conftest.py:77` use `startup: disabled` when the production container image has `startup: enabled`? Intentional (testing explicit-start behaviour) or an oversight that leaves the auto-start path untested?
4. **Per-hook construction cost**: each event handler class creates a new `IntegrationHubManager` (and its `TLSManager`), and `_on_collect_status` creates fresh `KubernetesManager`/`S3Manager` instances on every status evaluation. Could these be cached at module level or via `functools.cached_property` on the charm instance to reduce per-hook overhead?
