# kyuubi-k8s

A well-structured, mature Kubernetes charm for Apache Kyuubi from the Canonical Data Platform team. It follows modern Juju patterns (collect-status, `TypedCharmBase`, `charm_refresh` v3), has clean linting, decent unit tests, and a thorough integration test suite. In deployment it successfully runs Kyuubi, integrates with PostgreSQL for authentication and Zookeeper for HA, handles TLS certificate generation, and correctly blocks on missing required relations. Two defects stand out: invalid config values crash the charm to `error` state instead of producing a `BlockedStatus` (an uncaught pydantic `ValidationError`), and a status-masking bug in `_collect_domain_statuses` can hide a more severe failure (workload stopped) behind a less severe one (relation missing). There's also an open, unresolved multi-tenancy/data-isolation gap (issue #106) that maintainers should document or fix before recommending multi-tenant use. A maintainer should first fix the config-validation crash and the status-masking bug, since both directly mislead operators about the charm's actual state.

| | |
|---|---|
| Repo | canonical/kyuubi-k8s-operator @ `0dab7e2` (2026-07-23) |
| Charms | kyuubi-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), 3.5/stable rev 183; refreshed to 4.0/edge rev 203; also deployed (charm-only) on concierge-k8s-4 (Juju 4.0.5) |
| Reviewed | 2026-07-30 |

## What it does

Apache Kyuubi is a distributed multi-tenant JDBC/SQL gateway for Spark. This charm deploys Kyuubi on Kubernetes and provides a JDBC endpoint (`provides: jdbc`) usable by data-integrator charms. It requires a `spark-service-account` relation (integration hub) for K8s namespace and object-storage configuration, and an `auth-db` relation (PostgreSQL) for user authentication. It optionally integrates with Zookeeper for HA, TLS certificates, a metastore database, Loki for logging, and Prometheus/Grafana for observability. The charm manages Spark configuration, Hive metastore configuration, Kyuubi configuration, and TLS keystore/truststore generation via Pebble.

## Deployment log

**Deployment 1 — Juju 4.0.5 (charm-only, no postgresql):**
```bash
juju add-model rv-kyuubi-j4 k8s --controller concierge-k8s-4
juju deploy kyuubi-k8s --channel 3.5/stable --trust
# → rev 183, pod comes up, version 1.10
# → Status: blocked "Missing integration hub relation"
# Charm itself works fine on Juju 4
# But postgresql-k8s 14/stable rejects Juju 4, so full stack not deployable
```

**Deployment 2 — Juju 3.6.25 (full stack):**
```bash
juju add-model rv-kyuubi-j3 k8s --controller concierge-k8s-3
juju deploy kyuubi-k8s --channel 3.5/stable --trust
juju deploy spark-integration-hub-k8s --channel latest/edge --trust
juju deploy postgresql-k8s --channel 14/stable --trust
# → all three apps active/idle
juju integrate kyuubi-k8s:auth-db postgresql-k8s:database
juju integrate kyuubi-k8s spark-integration-hub-k8s
# → kyuubi-k8s: blocked "Missing Object Storage backend"
# (Kyuubi is actually running; auth-db is configured)
```

**TLS, Zookeeper, S3 integrations:**
```bash
juju deploy self-signed-certificates --channel latest/edge
juju deploy zookeeper-k8s --channel 3/stable
juju deploy s3-integrator --channel latest/edge --trust
juju integrate kyuubi-k8s:certificates self-signed-certificates
juju integrate kyuubi-k8s:zookeeper zookeeper-k8s
juju config s3-integrator bucket=test-bucket path=/test endpoint=http://10.1.0.1:9000
juju run s3-integrator/0 sync-s3-credentials access-key=test secret-key=test
juju integrate spark-integration-hub-k8s s3-integrator
# → TLS integrated: keystore.p12, truststore.jks, server.pem, ca.pem created at /opt/kyuubi/conf/
# → Zookeeper integrated, HA path configured
# → integration-hub blocked "Invalid S3 credentials" (dummy creds, expected)
# → kyuubi stays blocked "Missing Object Storage backend" (hub validates creds first)
```

**Refresh from 3.5/stable (rev 183, v1.10) to 4.0/edge (rev 203, v1.11):**
```bash
juju refresh kyuubi-k8s --channel 4.0/edge
# → Refresh accepted, new pod created with new OCI image
# → Image pull ~10 minutes
# → Kyuubi starts at v1.11, spark-defaults.conf updated to 4.0 image
# → All integrations (auth, TLS, zookeeper) preserved
# → Status returns to blocked "Missing Object Storage backend"
```

**Scale up/down:**
```bash
juju add-unit kyuubi-k8s -n 1  # → 2 units, both blocked
juju remove-unit kyuubi-k8s --num-units 1  # → back to 1 unit
# Works correctly on both Juju 3.6 and Juju 4.0
```

**Remove application:**
```bash
juju remove-application kyuubi-k8s --force --no-wait --destroy-storage
# → Clean teardown, pod removed within ~1 minute
```

## Observed behaviour

### Startup and runtime
- **Image pull time**: ~8–10 minutes on first deploy (large Spark+Kyuubi OCI image from `registry.jujucharms.com`). The charm stays in `maintenance "Waiting for Pebble"` during this time. Observed on both 3.5 and 4.0 images.
- **Pebble plan**: Three services — `kyuubi` (enabled, active), `history-server` (disabled), `sparkd` (enabled but inactive). The charm only manages the `kyuubi` service.
- **Kyuubi actually running while blocked**: Despite `blocked "Missing Object Storage backend"`, Kyuubi was running and serving the REST API on port 10099 (health-check pings returning HTTP 200 with admin credentials, HTTP 401 without). JDBC auth was configured against PostgreSQL. The blocked status is strictly about whether Spark jobs can be submitted (no object storage), not about Kyuubi itself being down.
- **Config files on disk**: `kyuubi-defaults.conf` at `/opt/kyuubi/conf/` with JDBC auth pointing to PostgreSQL; `spark-defaults.conf` at `/etc/spark8t/conf/` with K8s master URL, namespace, service account; `kyuubi-env.sh` empty/missing until S3 truststores are needed.
- **TLS files**: `keystore.p12`, `truststore.jks`, `server.pem`, `ca.pem` at `/opt/kyuubi/conf/` after TLS integration.
- **Resource usage**: 55m CPU, 478Mi memory (limit 1Gi, no CPU limits).

### Failure injection
- **Bad config values crash the hook** (Juju 3.6 and 4.0):
  ```bash
  juju config kyuubi-k8s profile=invalid-profile expose-external=true
  # → config-changed hook crashes: "hook failed: config-changed"
  # → pydantic ValidationError in debug-log:
  #   "value is not a valid enumeration member" / "unexpected value; permitted: ..."
  # → Must juju resolve to recover
  ```
  Real defect: the pydantic `ValidationError` is not caught and turned into a `BlockedStatus` (see Findings).
- **Removing integration hub relation while auth-db is also present**: Correctly transitions to `blocked "Missing integration hub relation"`. Pebble shows the `kyuubi` service inactive (correctly stopped).
- **Removing auth-db relation while integration hub is also missing**: Status remains `blocked "Missing integration hub relation"` even though Kyuubi was actually stopped due to the auth-db removal. Debug-log confirms: `"Workload stopped because auth db is missing"`. This is the status-masking bug — the first check in `_collect_domain_statuses` hides the later, more severe problem.
- **Killing the Java process**: Pebble restarted Kyuubi immediately (~1 second). Status remained unchanged.
- **Pod deletion (simulating node failure)**: Juju recreated the pod. Kyuubi recovered after ~2 minutes (image pull + startup). All integrations were restored.
- **Refresh**: Successful from rev 183 (v1.10) to rev 203 (v1.11). All integrations and config preserved. Kyuubi restarted with the new version.
- **Scale up with Zookeeper**: Works correctly — both units registered with Zookeeper for HA.
- **Bad secret reference in config**: Not tested directly (unverified). `_collect_status_system_users` and `_collect_status_tls_client_private_key` check for secret existence/permission and should produce a `BlockedStatus` rather than a crash — but if `Secret.exists()` returns `True` due to the bare `except Exception` (see finding below), the charm might proceed when it shouldn't.

### Hook count for a config change
- Changing `profile` from `staging` to `production`: 1 config-changed hook per unit (2 hooks for 2 units). No redundant events.

### Available channels
From `juju info kyuubi-k8s`:
- `3.5/stable`: rev 182
- `3.5/edge`: rev 183
- `4.0/stable`: rev 179
- `4.0/edge`: rev 203
- Channels support both amd64 and arm64.

## Findings

### pydantic `ValidationError` crashes config-changed hook
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:56` (`TypedCharmBase`) → `lib/charms/data_platform_libs/v0/data_models.py:200` (pydantic validation)
- **Evidence**: Setting `profile=invalid-profile` or `expose-external=true` (not a valid enum member) causes a `pydantic.error_wrappers.ValidationError` that propagates uncaught through the config-changed handler, crashing the hook to `error` status. Observed on both Juju 3.6.25 and Juju 4.0.5. Debug-log:
  ```
  pydantic.error_wrappers.ValidationError: 2 validation errors for CharmConfig
  expose_external: value is not a valid enumeration member
  profile: unexpected value; permitted: ('production', 'staging', 'testing')
  ```
  The unit enters `error` state and requires `juju resolve` to recover after fixing the config.
- **Impact**: An operator making a typo in a config value crashes the charm instead of getting a clear `BlockedStatus` with the permitted values.
- **Fix**: Wrap the config-changed handler (or `_on_config_changed`, or the `Context` constructor) in a try/except for `ValidationError` and set `BlockedStatus` with the validation message. Ideally handled centrally in `TypedCharmBase` or the config model, returning a status instead of raising.
- **Linter rule**: not mechanically checkable ("pydantic ValidationError from charm config is not caught").

### Status masking: early return hides downstream failures
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:189-192` (`_collect_domain_statuses`)
- **Evidence**: When both the integration hub and auth-db relations are missing, the method returns early at line 191 with `MISSING_INTEGRATION_HUB`, even though a later check (`MISSING_AUTH_DB`) reflects a more critical condition. Observed in deployment: after removing auth-db with the integration hub already removed, debug-log showed `"Workload stopped because auth db is missing"` but the status message remained `"Missing integration hub relation"`. Kyuubi was stopped, but the operator only sees the integration-hub message.
- **Impact**: An operator fixing the integration hub relation first may be confused when Kyuubi still doesn't start, because the auth-db problem was never surfaced.
- **Fix**: Collect all statuses without early returns and decide precedence at the end, or check the most critical condition first (auth-db stops the workload, so it should take priority over integration hub).
- **Linter rule**: not mechanically checkable.

### Missing user isolation between JDBC clients
- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/provider.py:119-176`
- **Evidence**: `_on_database_requested` creates a user in the `kyuubi_users` PostgreSQL table (username `relation_id_{N}`) and returns JDBC credentials to the client, but Kyuubi's JDBC authentication only controls access to Kyuubi, not access to data within Spark. All users share the same Spark cluster and Hive metastore; `event.database` is passed to the client via `set_database()` but is not enforced as a namespace/database-level isolation mechanism. Open issue #106: "User A can see tables from User B."
- **Impact**: A multi-tenant deployment with multiple data-integrator clients connected to the same Kyuubi instance has no data isolation between tenants.
- **Fix**: Design-level fix — configure per-user Spark engines or per-user Hive databases (Kyuubi supports `kyuubi.session.isolated.classes` and engine isolation). At minimum, document the limitation explicitly.
- **Linter rule**: not mechanically checkable.

### TLS SANs may not include all NodePort IPs
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/tls.py:48-84` (`build_sans`)
- **Evidence**: `build_sans` adds `node_ip` for the unit's own node, but with `expose_external=nodeport` and multiple units on different nodes, each certificate only includes the local unit's node IP. Open issue #113: "Server (unit) TLS certificate does not contain all node IPs as SAN when external exposure is NodePort."
- **Impact**: Clients connecting via NodePort to a different node than the unit's own will fail TLS hostname verification.
- **Fix**: When `expose_external=nodeport`, gather node IPs from all peer units (peer relation data or K8s API) and include them in each unit's certificate SANs.
- **Linter rule**: not mechanically checkable.

### Blocked status while workload is running
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:201-203` (`_collect_domain_statuses`)
- **Evidence**: The charm reports `BlockedStatus("Missing Object Storage backend")` when the integration hub doesn't provide S3/Azure storage config, but Kyuubi is actually running and serving REST API requests (health-check pings returned HTTP 200) as observed in deployment. The `is_serving_requests` check runs only after all `BlockedStatus` checks pass, so an operator sees "blocked" and assumes the service is down when it's up.
- **Impact**: Operators may waste time debugging a "blocked" service that is actually running; the distinction between "Kyuubi is down" and "Kyuubi is up but Spark jobs won't work" is lost.
- **Fix**: Downgrade `MISSING_OBJECT_STORAGE_BACKEND` from `BlockedStatus` to `MaintenanceStatus`/`WaitingStatus`, or report `ActiveStatus` with a message like "Kyuubi running; object storage not configured."
- **Linter rule**: not mechanically checkable ("BlockedStatus should only be used when the workload is actually blocked from running").

### Stale truststore files not cleaned on S3 relation removal
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/kyuubi.py:67-68` (`_sync_hub_truststore`)
- **Evidence**: `_sync_hub_truststore` cleans truststore paths when `service_account_info` is provided (lines 72-75), but when the integration hub relation is removed entirely, `update()` is called with `set_service_account_none=True`, setting `service_account_info=None`; the method returns early at line 68 without cleaning existing truststore files.
- **Impact**: Stale truststore files remain on disk and could be picked up by Spark jobs referencing the old path, leading to connection failures with outdated certificates.
- **Fix**: Move truststore cleanup before the `if not service_account_info: return` guard so it always runs.
- **Linter rule**: mechanically checkable ("`_sync_hub_truststore` called with `None` argument does not clean existing truststores").

### `Secret.exists()` swallows all exceptions
- **Severity**: low
- **Kind**: bug
- **Where**: `src/core/domain.py:520-529`
- **Evidence**:
  ```python
  def exists(self) -> bool:
      try:
          self.model.get_secret(id=self.secret_id)
      except ops.model.SecretNotFoundError:
          return False
      except Exception:
          return True
      else:
          return True
  ```
  The bare `except Exception: return True` means any error (connection error, permission error) makes `exists()` return `True`, which is then used by `has_permission()` and content access.
- **Impact**: The charm could proceed with a secret that doesn't exist or is inaccessible, crashing later when reading its content instead of reporting a clear status now.
- **Fix**: Only catch `SecretNotFoundError`; let unexpected errors propagate (or catch a specific documented exception with a comment).
- **Linter rule**: mechanically checkable ("bare `except Exception` in secret access methods").

### `_collect_domain_statuses` exceeds complexity threshold
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:182` (`# noqa: C901`)
- **Evidence**: ~130 lines with 15+ conditional branches and a `# noqa: C901` suppression. Creates new manager objects (`K8sManager`, `IntegrationHubManager`, `ServiceManager`) on every invocation; `ServiceManager`'s constructor calls `socket.getfqdn()`, doing a DNS lookup on every status update.
- **Impact**: Hard to reason about (as evidenced by the status-masking bug above); repeated object creation wastes a DNS lookup every 5-minute update-status hook.
- **Fix**: Split into smaller methods, cache manager objects, and remove early returns so all statuses are collected.
- **Linter rule**: mechanically checkable ("`noqa: C901` without justification").

### User password generated with only 16 characters
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/auth.py:48-50`
- **Evidence**: `AuthenticationManager.generate_password()` generates 16-character passwords from `string.ascii_letters + string.digits`, while `KyuubiWorkload.generate_password()` (`src/core/workload/kyuubi.py:115-126`) generates 32-character passwords. The shorter password is used for all JDBC client users (external, multi-tenant).
- **Impact**: Inconsistent, and the shorter password is used for the higher-risk case (multiple external clients vs. internal keystore passwords).
- **Fix**: Use one shared 32-character password-generation utility everywhere.
- **Linter rule**: mechanically checkable ("duplicate password generation with different lengths").

### Commented-out `self.delete_service()` in reconcile
- **Severity**: low
- **Kind**: lint
- **Where**: `src/managers/service.py:258`
- **Evidence**: `# self.delete_service()` left in place; when the service type changes, the code uses `lightkube.apply()` to update in-place instead.
- **Impact**: Dead code is confusing; if `apply()` fails for immutable field changes, the old service could persist with the wrong type.
- **Fix**: Remove the comment, or explain why delete-then-create is unnecessary.
- **Linter rule**: mechanically checkable ("commented-out code").

### `DatabaseManager.execute()` catches all exceptions with no differentiation
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/database.py:58-59`
- **Evidence**: `except Exception as e: self.logger.warning(...)` catches everything and returns `(False, [])`. Transient errors (connection refused) and permanent errors (bad SQL, auth failure) are treated identically.
- **Impact**: `create_user`/`user_exists` may fail silently, causing the charm to defer events indefinitely rather than reporting a clear error.
- **Fix**: Distinguish transient (retryable) vs. permanent (block with message) errors; at minimum log the exception type.
- **Linter rule**: not mechanically checkable ("bare `except Exception` in database operations without re-raise or status differentiation").

### `_on_peer_relation_changed` emits TLS refresh on every peer change
- **Severity**: low
- **Kind**: performance
- **Where**: `src/events/kyuubi.py:226-227`
- **Evidence**: The peer relation changed handler unconditionally calls `self.charm.tls_events.refresh_tls_certificates_event.emit()`. This event is passed to `TLSCertificatesRequiresV4` as `refresh_events`, which triggers certificate regeneration — intentional for new units needing SANs added, but it fires on every peer relation change, including non-TLS-related updates (e.g., admin password changes).
- **Impact**: Unnecessary certificate regeneration and extra Kyuubi restarts on unrelated peer data changes.
- **Fix**: Check which peer keys changed before emitting; only emit when TLS-related keys (hostname, ip, fqdn, kyuubi-address) changed.
- **Linter rule**: not mechanically checkable.

### Connection opened/closed on every SQL query
- **Severity**: low
- **Kind**: performance
- **Where**: `src/managers/database.py:36-60`
- **Evidence**: `execute()` opens a new `psycopg2` connection, runs the query, and closes it on every call. `AuthenticationManager.prepare_auth_db` calls `execute()` multiple times in sequence (`enable_pgcrypto_extension`, `create_authentication_table`, `user_exists`, `create_user`/`set_password`), each a separate TCP connection.
- **Impact**: Negligible for infrequent operations like user creation, but adds latency/DB load if this pattern is reused for frequent operations.
- **Fix**: Open one connection and run all queries for the auth flow; consider a connection pool for future use.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **`collect_unit_status` / `collect_app_status` pattern** (`src/charm.py:126-178`): Correct use of the ops 2.x collect-status pattern with a single source of truth for status; priority ordering (refresh v3 high → domain → refresh v3 low → active) is clean and documented.
- **`TypedCharmBase` with pydantic config** (`src/charm.py:56`, `src/core/config.py`): Structured config validation with pydantic validators for `k8s_node_selectors` and `system_users`/`tls_client_private_key` secret patterns. (Needs a wrapper to catch `ValidationError` and produce a status instead of crashing — see finding above.)
- **`_compare_and_update_file` pattern** (`src/managers/kyuubi.py:39-57`): Before writing a config file, the charm reads existing content and only writes if it changed; combined with `should_restart` logic, the workload only restarts when configuration actually changed.
- **`defer_when_not_ready` decorator** (`src/events/base.py:33-47`): A clean, reusable decorator that defers events when the workload container isn't connectable — worth standardizing across the ecosystem.
- **Integration test suite** (`tests/integration/`): Comprehensive, covering 13+ scenarios (charm, trust, HA, external access, TLS, dynamic allocation, observability, iceberg, metastore, auth, provider, refresh, GPU), each a separate tox environment. Tests assert specific status messages, not just "active/idle."
- **`charm_refresh` v3 integration** (`src/events/refresh.py`): In-place refresh with compatibility checks, pre-refresh checks, and pause-after-unit-refresh; `is_workload_compatible` enforces a same-major, greater-or-equal-minor version policy. Successfully tested in deployment (3.5→4.0).
- **Clean linting**: All ruff checks pass, mypy passes with no issues, codespell is clean; `pyproject.toml` has a well-configured ruff setup.
- **TLS truststore update strategy** (`src/managers/tls.py:137-158`): The three-step rename-import-delete approach to updating truststore entries without leaving the keystore empty is well thought out and documented.
- **`libpq` staging in `charmcraft.yaml`**: Stages `libpq.so` libraries for `psycopg2` — a clean solution to the binary-dependency problem in charm containers.

## Common-practice notes

- **Follows**: Canonical Data Platform team conventions: `src/` layout with `core/`, `events/`, `managers/`, `config/`; `charmcraft.yaml` with poetry plugin; `tox.ini` with format/lint/unit/integration environments; `lib/charms/` for shared libraries; spread tests.
- **Follows**: Uses `data_platform_libs` for database relations, `tls_certificates_interface` v4 for TLS, and `spark_service_account` library for the integration hub.
- **Drifts from convention**: Creates its own K8s Service via `lightkube` rather than using Juju's `juju expose` or `kubernetes-service-type` config — deliberate for the Spark use case (NodePort/LoadBalancer with custom annotations).
- **Drifts from convention**: Uses two peer relations (`kyuubi-peers` and `refresh-v-three`) instead of the usual single peer relation; `refresh-v-three` is required by `charm_refresh`.
- **Leads**: `refresh_versions.toml` and `charm_refresh` integration is more advanced than most charms.
- **Leads**: Deploys and runs correctly on Juju 4.0.5, which many charms don't yet support. The full stack is blocked only because `postgresql-k8s` doesn't support Juju 4.

## Tests

**Unit tests**: 52 tests, all pass. Coverage: 66% (583/1967 statements missed). Uses `ops.testing` (scenario) with `Context`, `State`, and `Relation` objects. Areas covered: charm lifecycle (install, pebble-ready, config-changed, update-status); relations (spark-service-account, auth-db, zookeeper, peer); status paths (all `BlockedStatus`, `MaintenanceStatus`, `ActiveStatus`); config (profile, k8s-node-selectors validation); TLS (relation created/broken, certificate available); refresh (workload compatibility checks); providers (database-requested deferral, endpoints update).

**Coverage gaps**:
- `src/managers/auth.py`: 24% — `create_user`, `delete_user`, `set_password`, `user_exists` not unit-tested (relies on integration tests).
- `src/managers/database.py`: 24% — SQL execution not unit-tested.
- `src/managers/hive_metastore.py`: 24% — schematool commands not unit-tested.
- `src/managers/service.py`: 41% — NodePort/LoadBalancer endpoint resolution, service creation/deletion not unit-tested.
- `src/managers/tls.py`: 41% — keystore/truststore file operations not unit-tested.
- `src/events/refresh.py`: 53% — `run_pre_refresh_checks_after_1_unit_refreshed` not tested.
- `src/events/provider.py`: 54% — `_on_database_requested` and `_on_relation_broken` not unit-tested.
- `src/events/kyuubi.py`: 56% — `_on_config_changed`, `_on_secret_changed`, `_on_peer_relation_changed` not unit-tested.
- GPU config paths in `src/config/spark.py` (lines 67-88) not tested.
- No test for invalid config values being caught and turned into `BlockedStatus`; existing `test_config.py` tests focus on validators, not on the charm's error-handling path.

**Integration tests**: 13 tox environments covering all major scenarios. Uses `jubilant`; `test_charm.py` asserts actual status messages, not just "active/idle."

**Spread tests**: `spread.yaml` configured with LXD VM and GitHub CI backends; deploys full stack (MicroK8s, MicroCeph, TLS certificates).

## Docs

- **README.md** (1000 bytes): Brief, links to Charmhub and the Kyuubi project. Doesn't explain how to deploy, what relations are needed, or what config options matter.
- **metadata.yaml docs link**: `https://canonical-charmed-spark.readthedocs-hosted.com/main/how-to/apache-kyuubi`
- **CONTRIBUTING.md** (1084 bytes): Clear dev setup with tox, but mentions `tox run -e static` which doesn't exist in `tox.ini` (no `[testenv:static]` section).
- **Charmhub description**: Minimal — doesn't list required relations, config options, or deployment instructions.
- **config.yaml**: Well-documented — each config option maps to a specific Spark/Kyuubi setting, with examples.
- **Doc/reality match**: `system-users` config description says "If this config option is not provided, the charm will generate a random password for the admin user" — confirmed in deployment (auto-generated password stored in peer relation data).
- **Doc/reality mismatch**: `CONTRIBUTING.md` says `tox run -e static` exists, but `tox.ini` has no `static` environment.

## Open questions

1. Does the charm work on Juju 4.x with a PostgreSQL charm that supports Juju 4? Kyuubi itself deployed and refreshed fine on Juju 4.0.5; the full stack is blocked only by `postgresql-k8s` 14/stable requiring Juju < 4.0.
2. What happens when `expose-external` is changed from `nodeport` to `loadbalancer` and back? `reconcile_services` uses `lightkube.apply()` with a commented-out `delete_service()`; needs a cloud K8s with LB support to verify.
3. Is the `Secret.exists()` bare `except Exception` an intentional workaround for a Juju bug, or defensive coding that masks errors? Git history doesn't clarify (unverified).
4. Does the charm handle secret rotation for `system-users` correctly? `_on_secret_changed` updates the admin password when secret content changes, but this path is untested (see coverage gap).
