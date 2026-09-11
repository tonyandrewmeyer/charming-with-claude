# identity-platform-admin-ui

The `identity-platform-admin-ui` charm deploys the Identity Platform Admin UI, a Go web application providing a graphical interface for identity management within the Canonical Identity Platform. The codebase is well-structured, with a clean module layout and a holistic reconciliation pattern that most identity-platform charms follow. In practice it has several real operational problems: a hard SMTP dependency that blocks deployment entirely without it (acknowledged upstream in #269), a `create-identity` action that crashes with an unhandled `KeyError` when the optional `password` parameter is omitted, and a systemic bug where stale environment variables — including Juju secrets such as the OpenFGA API token and database DSN — persist in the Pebble layer after their integration is removed, because the NOOP_CONDITIONS check short-circuits the holistic handler before it can clear them. `@cached_property` on `_ca_bundle` means the charm will never pick up a rotated CA certificate without a pod restart, and `PebbleService.stop()` cannot actually stop the workload because the service is defined with `startup: enabled`. There's also a pydantic v1/v2 conflict baked into the openfga dependency that is a ticking time bomb rather than an active failure. None of these are exotic — a maintainer should first fix the `create-identity` crash and the stale-secret-on-removal bug, since both directly leak or misuse credentials/functionality in ordinary operation, then address the CA rotation and Pebble stop issues before the next release.

| | |
|---|---|
| Repo | canonical/identity-platform-admin-ui-operator @ `f28d3e7` (2026-02-16) |
| Charms | identity-platform-admin-ui |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6), `latest/edge` rev 116 (standalone, full ecosystem, and observability); concierge-k8s-4 (Juju 4.0), `latest/edge` rev 116 (standalone); refresh from `latest/stable` rev 85 → rev 116 tested |
| Reviewed | 2026-08-11 |

## What it does

Deploys the Identity Platform Admin UI as a Kubernetes pod with a single `admin-ui` Pebble container. The workload is a Go binary (`identity-platform-admin-ui serve`) listening on port 8080. Integrates with kratos (identity provider), hydra (OAuth2/OIDC provider), OpenFGA (authorization), PostgreSQL (database), traefik (ingress), self-signed-certificates (TLS CA), SMTP (email), Loki (logging), Tempo (tracing), Prometheus (metrics), and Grafana (dashboards). Exposes four Juju actions: `create-identity`, `run-migration-up`, `run-migration-down`, `run-migration-status`.

## Deployment log

### Deploy 1: Juju 4.0 standalone (model rv-admin-ui-j4)
```shell
juju add-model rv-admin-ui-j4  # on concierge-k8s-4
juju deploy identity-platform-admin-ui --channel edge --trust  # rev 116
```
Deployed successfully, reached `blocked (Missing integration kratos-info)`. Pebble service `inactive` (no integrations — NOOP_CONDITIONS prevent layer planning). PostgreSQL charm incompatible with Juju 4.0 — not this charm's fault. Config changes accepted; bad `cpu`/`memory` values caused `BlockedStatus("Failed obtaining resource limit spec...")`, which IS visible in `juju status` on Juju 4.0. A `FileNotFoundError` traceback was logged during initial startup (pod termination-related; see finding on CA bundle path below). Destroyed.

### Deploy 2: Juju 3.6 full ecosystem (model rv-admin-ui-deep)
```shell
juju add-model rv-admin-ui-deep  # on concierge-k8s-3
juju deploy identity-platform-admin-ui --channel latest/stable --trust  # rev 85
juju refresh identity-platform-admin-ui --channel latest/edge  # rev 116
# Deployed 7 deps: postgresql-k8s, openfga-k8s, self-signed-certificates,
# traefik-k8s, smtp-integrator, kratos, hydra
juju integrate ... (all 12 relations)
```
Refresh from rev 85 → 116 clean: pod terminated, new pod started, charm re-initialized, all hooks replayed. After all integrations: charm reached `active` with workload version 1.25.0, service running. Destroyed after all tests.

### Deploy 3: Juju 3.6 with observability (model rv-admin-ui-3, earlier session)
Identical to deploy 2 plus grafana-agent-k8s, loki-k8s, tempo-k8s. All 11 apps deployed and integrated. Charm reached `active` after ~7 minutes. Destroyed.

### Deploy 4: Juju 3.6 failure injection (model rv-admin-ui-deep2)
Standalone deploy of rev 116 on concierge-k8s-3. Used to test bad config values, ERROR log patterns, and pebble plan inspection in blocked state. Confirmed that on Juju 3.6, bad `cpu`/`memory` config values are silently accepted with no visible status change (unlike Juju 4.0, where the error is surfaced). Destroyed.

### Actions exercised
```shell
juju run identity-platform-admin-ui/0 run-migration-status  # SUCCESS
juju run identity-platform-admin-ui/0 run-migration-down     # SUCCESS
juju run identity-platform-admin-ui/0 run-migration-up       # SUCCESS
juju run identity-platform-admin-ui/0 create-identity schema=default traits.email=test@example.com
# -> Uncaught KeyError: 'password' (confirmed in all three deploys)
juju run identity-platform-admin-ui/0 create-identity schema=default traits.email=test@example.com password=test123
# -> FAILED: "Failed to create the identity" — KRATOS_ADMIN_URL is empty
```

### Scale tested
Scale up to 2: unit 1 started, brief `blocked (Missing certificate transfer integration)`, then CA bundle propagated, service started. Scale down to 1: clean teardown. Both units `active` at scale 2.

### Refresh from stable to edge
`juju refresh identity-platform-admin-ui --channel latest/edge` succeeded (rev 85 → 116). Pod was terminated and recreated. New pod came up, charm hooks ran, unit reached `blocked (Missing integration kratos-info)` before integrations were added, then reached `active` once all integrations were added after the refresh. The refresh itself was clean with no hook failures.

### Juju 4.0 vs Juju 3.6 comparison
- Charm deploys and operates on both controllers.
- On Juju 4.0 without integrations: `blocked (Missing integration kratos-info)` with no admin-ui pebble service.
- **Key difference**: On Juju 4.0, bad `cpu`/`memory` config values cause `BlockedStatus("Failed obtaining resource limit spec...")` visible in `juju status` and logged at ERROR level. On Juju 3.6, the same bad values are silently accepted — no status change and no ERROR log; the resource patch error is swallowed. This is because on Juju 3.6, `KubernetesComputeResourcesPatch` does not fire the `patch_failed` event when pebble is not connected/no service is running, but on Juju 4.0 it does.
- PostgreSQL charm incompatibility with Juju 4.0 prevents full ecosystem deploy (not this charm's fault).

## Observed behaviour

### Deployment progression
- **Deploy time to active**: 6-8 minutes with all integrations, gated by PostgreSQL readiness and OpenFGA store creation.
- **Status progression**: `blocked (Missing integration kratos-info)` → `blocked (Missing certificate transfer integration with oauth provider)` → `blocked (Either Database migration is required)` → `active`.
- **After integration removal**: Correctly goes to `blocked (Missing integration <name>)` for required integrations. For optional integrations (logging, tracing), stays `active` with stale config.

### Version check ERROR log spam during startup
During charm install and every subsequent hook (`install`, `relation-created`, `leader-elected`, `config-changed`, `start`, `stop`), each hook emits:
```
ERROR Failed to fetch the Admin Service version: Could not connect to Pebble: socket not found
```
This is because `_on_collect_status` calls `migration_needed_on_leader(self)`, which calls `self.migration_needed` → `self._workload_service.version` → `self._cli.get_admin_service_version()` → `container.exec()`, and the Pebble socket is not available before `admin-ui-pebble-ready`. The error is caught by `get_admin_service_version`'s `except Error` (`cli.py:43`), so hooks do not crash, but the ERROR log spam is misleading to operators. Observed on Juju 3.6 but NOT on Juju 4.0 — on Juju 4.0 the `migration_needed` path may short-circuit differently or the Pebble socket is available earlier.

### `_on_collect_status` reaches `migration_needed_on_leader` even without database
`_on_collect_status` at line 440 calls `migration_needed_on_leader(self)` unconditionally — the preceding `if not database_integration_exists(self)` at line 435 only adds a `BlockedStatus`, it does not `return`. When database doesn't exist, `migration_needed` still calls `self._workload_service.version` (container exec). The version lookup catches the error and returns `""`, then `migration_needed` compares `DatabaseConfig.load(...).migration_version` (which is `""`) against the version (`""`), but the comparison is `self.peer_data[""] != self._workload_service.version` → `{} != ""` → `True`, so a spurious `BlockedStatus("Either Database migration is required...")` is added. This message is misleading when the real problem is a missing database.

### Stale environment variables after integration removal (systemic bug)
Confirmed via `pebble plan` inspection after each integration removal:
- **OpenFGA removal**: `OPENFGA_API_TOKEN` (Juju secret), `OPENFGA_STORE_ID`, `OPENFGA_API_HOST` all persist
- **Database removal**: `DSN` (with credentials) persists, service continues running because `startup: enabled`
- **OAuth removal**: `OIDC_ISSUER`, `OAUTH2_CLIENT_ID`, `OAUTH2_CLIENT_SECRET` all persist
- **SMTP removal**: `MAIL_HOST`, `MAIL_PORT` persist with their last values
- **Logging removal**: Loki log-targets persist in pebble config (no broken-event handler exists)
- **Tracing removal**: `OTEL_GRPC_ENDPOINT`, `OTEL_HTTP_ENDPOINT`, `TRACING_ENABLED: true` persist (no broken-event handler exists)

Root cause: `_holistic_handler` checks `NOOP_CONDITIONS` first; when an integration is removed, its existence check returns `False`, so the handler returns early without updating the pebble layer. For optional integrations (logging, tracing), there is no broken-event handler at all, so the pebble layer is never replanned after their removal — the stale config persists indefinitely until an unrelated hook triggers a replan.

### PebbleService.stop() fails to stop the workload on database removal
After removing the `pg-database` relation, `_on_database_integration_broken` (line 400-404) calls `self._pebble_service.stop()`, but the pebble plan has `startup: enabled` for the admin-ui service, so Pebble immediately restarts it. Observed: `pebble services` showed `active` after database removal, and the health check `/api/v0/status` continued returning 200. The DSN with credentials remained in the pebble plan.

### Pebble replans on every hook
Each integration event and config change triggers `_holistic_handler` → `_pebble_service.plan()` → `container.replan()`. Changing `log_level` from `info` to `debug` triggered a replan even though only the `LOG_LEVEL` env var changed. The K8s resource patch code also fires on every config-changed event regardless of whether `cpu`/`memory` changed.

### Workload SIGKILL recovery
`pebble signal SIGKILL admin-ui` restarts the service within ~1 second. Pebble logs show `Server closed` → restart → `Starting server on port 8080`. Health check stays `up` with 0 failures. The workload binary itself crashes periodically (observed 3 restarts in 25 seconds during initial startup, before all integrations were ready).

### Public metric endpoint
`/api/v0/metrics` is publicly accessible through the traefik ingress (`curl http://<ingress>/.../api/v0/metrics` returns 200). Acknowledged in open issue #240.

### Bad config values: Juju 4.0 vs Juju 3.6
- `log_level=INVALIDVALUE`: Juju accepted it on both versions. `LOG_LEVEL=INVALIDVALUE` in pebble plan (on 3.6 with integrations), charm stayed `active`.
- `cpu=999xxx`, `memory=not-a-number`: On Juju 4.0, caused visible `BlockedStatus("Failed obtaining resource limit spec: Invalid limits spec...")` and ERROR logs. On Juju 3.6, the same values were silently accepted — no status change and no ERROR log. This cross-version inconsistency means operators get different feedback depending on Juju version.

### SMTP unreachable host accepted
Setting `smtp-integrator` to an unreachable host (`10.255.255.1:25`) was accepted; `MAIL_HOST`/`MAIL_PORT` updated in pebble plan, charm stayed `active` — no connectivity validation.

## Findings

### 1. `create-identity` action crashes with `KeyError` when `password` is omitted
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:552` — `password = event.params["password"]`
- **Evidence**: `event.params["password"]` uses dict key access, but `password` is not in the action's `required` list in `charmcraft.yaml:195-209`. Running `juju run identity-platform-admin-ui/0 create-identity schema=default traits.email=test@example.com` produces `Uncaught KeyError in charm code: 'password'`. Confirmed in three separate deploys across both Juju versions.
- **Impact**: Any operator omitting the optional password parameter gets an unhandled traceback instead of a clear action failure. The action definition explicitly marks `schema` and `traits` as required but not `password`.
- **Fix**: Use `event.params.get("password")`, or add `password` to `required`. The CLI code in `cli.py:89-91` already handles `password=None` correctly.
- **Linter rule**: "Action parameter accessed via `event.params[key]` where key is not in the action's `required` list" — mechanically checkable.

### 2. Stale environment variables (including Juju secrets) persist after any integration is removed
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:470-472` (NOOP_CONDITIONS check in `_holistic_handler`), `src/charm.py:389-390` (example: database broken handler calls it), `src/utils.py:113-118` (NOOP_CONDITIONS definition)
- **Evidence**: When any required integration is removed, the broken handler calls `_holistic_handler(event)`, which checks NOOP_CONDITIONS — the removed integration's existence check returns `False`, so the handler returns early without updating the pebble layer. Confirmed by `pebble plan` inspection after each removal (see Observed behaviour above). For optional integrations (logging, tracing, SMTP), there is no broken-event handler at all, so the pebble layer is never replanned.
- **Impact**: Juju secret tokens (OpenFGA API token, OAuth client secret, database DSN) and other sensitive values remain in the container environment after their integration is removed. For optional integrations, the stale config persists indefinitely until the next unrelated hook event triggers a replan. The workload continues running with stale credentials and invalid endpoints.
- **Fix**: Broken-event handlers should update the pebble layer even when NOOP_CONDITIONS fail, to clear stale env vars. Add relation-broken handlers for optional integrations. For SMTP, no removal handler exists at all — only `smtp_data_available` is observed (`src/charm.py:278-281`).
- **Linter rule**: "Integration-removed handler that calls `_holistic_handler` whose NOOP_CONDITIONS would fail" — partially checkable. "No relation-broken handler for a relation whose data flows into the pebble layer" — mechanically checkable.

### 3. `@cached_property` on `_ca_bundle` prevents certificate rotation
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:510-511`
- **Evidence**: `@cached_property def _ca_bundle(self) -> str:` — the property reads `TLSCertificates.load(...).ca_bundle`, which reads all relations, writes to disk, runs `subprocess.run(["update-ca-certificates", "--fresh"])`, and reads back the bundle. With `cached_property`, this value is computed once per charm process lifetime and never updated. The `_on_certificate_changed` handler calls `_holistic_handler`, which calls `self._workload_service.push_ca_certs(self._ca_bundle)`, but `_ca_bundle` returns the cached value from the first call. Additionally, `TLSCertificates.load()` always reads `CA_BUNDLE_PATH` at the end — if no CA bundle has been installed yet (fresh container), this raises `FileNotFoundError`. On Juju 4.0, an `Uncaught exception: FileNotFoundError: [Errno 2] No such file or directory` was observed during config-changed, likely from this path.
- **Impact**: When the CA certificate provider renews its certificate, the charm will never pick up the new CA bundle until the pod is restarted. TLS validation for outbound connections to hydra/kratos will fail with the old CA. `TLSCertificates.load()` also has side effects (writes files, runs `update-ca-certificates`), making the cache doubly inappropriate.
- **Fix**: Remove `@cached_property` in favour of a plain `@property`, or explicitly invalidate the cache when certificate events fire. Guard `CA_BUNDLE_PATH.read_text()` with an existence check in `TLSCertificates.load()`.
- **Linter rule**: "`@cached_property` on a method that accesses relation data, mutable Juju state, or performs file I/O or subprocess calls" — mechanically checkable.

### 4. `PebbleService.stop()` cannot stop a service with `startup: enabled`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/services.py:142-144`, `src/charm.py:389-393`
- **Evidence**: After removing the `pg-database` relation, `_on_database_integration_broken` calls `self._pebble_service.stop()`, which calls `container.stop("admin-ui")`. The pebble plan defines `startup: enabled` for the admin-ui service (`services.py:51`), so Pebble restarts it immediately. Observed: `pebble services` showed `active` after database removal, health check `/api/v0/status` returned 200. The DSN with credentials persisted in the pebble plan.
- **Impact**: The intent of commit `87ca1c9` ("Stop service when database is gone") doesn't actually work. The workload continues running against a removed database, likely restart-looping, and database credentials remain in the container.
- **Fix**: Before stopping, update the pebble layer to set `startup: disabled` for the service, or remove the service from the layer entirely. Alternatively, disable `startup` by default and use explicit `container.start()`.
- **Linter rule**: not mechanically checkable (requires understanding Pebble semantics).

### 5. Pydantic version conflict: openfga library uses deprecated v1 APIs but requires `pydantic<2.0`, while the charm installs `pydantic>=2`
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/openfga_k8s/v1/openfga.py:91` (`PYDEPS = ["pydantic<2.0"]`) vs `charmcraft.yaml:170` (`"pydantic>=2"`)
- **Evidence**: The openfga library declares `PYDEPS = ["pydantic<2.0"]` and uses pydantic v1 APIs throughout: `from pydantic import BaseModel, Field, validator` (line 79 — `@validator` deprecated in v2), `class Config` with `allow_population_by_field_name` (line 110 — renamed `validate_by_name` in v2), `cls.parse_raw()` (line 134 — deprecated in v2), and `self.__fields__` (line 142 — replaced by `model_fields` in v2). The charm's `charm-binary-python-packages` includes `"pydantic>=2"`. At runtime, pydantic v2 is installed (confirmed by pydantic v2 deprecation warnings in every hook: `PydanticDeprecatedSince20: Support for class-based config is deprecated`, `Pydantic V1 style @validator validators are deprecated`, `parse_raw method is deprecated`). The library appears to work because pydantic v2 offers partial backward compatibility, but this is not guaranteed.
- **Impact**: When pydantic drops `@validator`, `parse_raw`, `__fields__`, and `Config.allow_population_by_field_name` backward compatibility (planned for pydantic v3), this will cause runtime import errors or validation failures. Other charm libraries (traefik-k8s ingress, tempo-k8s tracing) also use v1-era `class Config` patterns but handle both versions through version detection; the openfga library does not.
- **Fix**: Upgrade the openfga library to a pydantic v2-compatible version, or vendor a patched copy.
- **Linter rule**: "`charm-binary-python-packages` or `requirements.txt` specifies a dependency version incompatible with a library's `PYDEPS` constraint" — mechanically checkable.

### 6. Charm reports `active` while critical integration data is empty
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/utils.py:61` (`integration_existence` only checks relation count), `src/charm.py:517-538` (`_pebble_layer`)
- **Evidence**: `kratos_integration_exists` checks `bool(charm.model.relations[KRATOS_INFO_INTEGRATION_NAME])` — relation existence, not data readiness. `KratosData.load` calls `requirer.is_ready()` (`integrations.py:235`) and returns empty data when not ready. Observed: kratos-info relation exists but `application-data` is empty, so `KRATOS_ADMIN_URL=""` and `KRATOS_PUBLIC_URL=""`. Charm reports `active` but `create-identity` fails. Similarly, `oauth_integration_exists` checks existence only; `oauth_is_ready()` exists at `utils.py:68` but is never called in any condition tuple, so OAuth data (`OIDC_ISSUER`, `OAUTH2_CLIENT_ID`, `OAUTH2_CLIENT_SECRET`) is all empty while charm is `active`.
- **Impact**: Operators see `active` and assume the workload is fully functional, but core features are broken. The gap between "relation exists" and "relation data is ready" can persist indefinitely if the provider charm never publishes its data.
- **Fix**: Replace `kratos_integration_exists` and `oauth_integration_exists` in NOOP_CONDITIONS with readiness-checking conditions that call `is_ready()`. Wire in the existing but unused `oauth_is_ready()`.
- **Linter rule**: "`NOOP_CONDITIONS`/`EVENT_DEFER_CONDITIONS` check relation existence for an integration whose requirer has an `is_ready()` method that is not called" — mechanically checkable.

### 7. `_on_collect_status` calls `migration_needed_on_leader` without a `can_connect` guard, causing ERROR log spam on every startup hook
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:440` (`migration_needed_on_leader(self)`), `src/utils.py:96` (→ `charm.migration_needed` → `charm.py:513-518`)
- **Evidence**: During charm install and initial hooks, every hook emits `ERROR Failed to fetch the Admin Service version: Could not connect to Pebble: socket not found` because `_on_collect_status` unconditionally calls `migration_needed_on_leader(self)`, which calls `self.migration_needed` → `self._workload_service.version` → `container.exec()`. The Pebble socket is not available before `admin-ui-pebble-ready`. Observed in `juju debug-log` on Juju 3.6 during pod restart: 5 ERROR messages across install, relation-created, leader-elected, config-changed, start hooks. The error is caught by `cli.py:43` (`except Error`), so hooks don't crash, but the log spam and spurious `migration_needed=True` status are misleading. This log spam was NOT observed on Juju 4.0, suggesting a Pebble socket timing difference between Juju versions. There is also no `return` after the `database_integration_exists` check at line 435, so `migration_needed_on_leader` runs even when there is no database, producing `True` from `self.peer_data[""]` (which returns `{}`) compared against the version string.
- **Impact**: Operators see ERROR-level log messages on every pod restart that look like failures but are harmless. The "Either Database migration is required" blocked status can appear spuriously when the real issue is a missing database.
- **Fix**: Guard `migration_needed_on_leader`/`migration_needed_on_non_leader` checks with `can_connect`. Add a `return` after `if not database_integration_exists(self)` in `_on_collect_status`, or have `migration_needed` check `database_integration_exists` before accessing the container.
- **Linter rule**: "`_on_collect_status` calls a property/method that accesses `self._container` without a `can_connect` guard" — mechanically checkable.

### 8. `SmtpProviderData.load()` calls `model.get_secret()` with no error handling
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/integrations.py:424-428` — `password_secret = requirer.model.get_secret(id=data.password_id)`
- **Evidence**: If the SMTP provider's secret is deleted or `password_id` is invalid, `model.get_secret()` raises `SecretNotFoundError`, which propagates uncaught — `load()` has no try/except. `password_secret.get_content().get("password", "")` could also raise on malformed content. There is a window between the secret being set and the event firing where the secret ID could be stale.
- **Impact**: A crash in `SmtpProviderData.load()` propagates to `_pebble_layer` (a `@property`), crashing the event handler that calls it. The charm would enter an uncaught-exception error state.
- **Fix**: Wrap `model.get_secret()`/`secret.get_content()` in try/except, returning `cls()` (default values) on failure, consistent with other `load()` methods.
- **Linter rule**: "`model.get_secret()` call without try/except" — mechanically checkable.

### 9. Excessive Pebble replans: every hook triggers a workload restart
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:470-508` (`_holistic_handler` → `_pebble_service.plan()` → `container.replan()`), `src/services.py:134-135`
- **Evidence**: Each integration event, config change, and peer relation change triggers a replan and service restart. A trivial `log_level` config change triggered a replan. Each replan restarts the admin-ui service (`startup: enabled`), causing a visible interruption (workload logs show `Server closed` → restart). The service restarted 3+ times in 25 seconds during initial startup as each integration event arrived. The K8s resource patch code also fires on every config-changed event regardless of whether `cpu`/`memory` actually changed.
- **Impact**: In a production deployment with many simultaneous integration events, the service could restart 5+ times in quick succession.
- **Fix**: Compare the generated environment variables against the current pebble plan before calling `replan()`; only replan if the layer actually changed.
- **Linter rule**: "`container.replan()` called without prior layer comparison" — partially checkable.

### 10. `charmcraft.yaml` `optional` mismatch with charm behaviour
- **Severity**: medium
- **Kind**: ux
- **Where**: `charmcraft.yaml:38-41` (only `pg-database` marked `optional: false`) vs `src/utils.py:113-118` (7 integrations are NOOP_CONDITIONS), `src/charm.py:413-438` (7 integrations block status)
- **Evidence**: In `charmcraft.yaml`, only `pg-database` has `optional: false`. All other `requires` relations (`hydra-endpoint-info`, `kratos-info`, `openfga`, `oauth`, `ingress`, `receive-ca-cert`, `smtp`) have no `optional` key (defaulting to `true`). But the charm code treats them as required: NOOP_CONDITIONS includes all seven, and `_on_collect_status` emits `BlockedStatus("Missing integration ...")` for each missing one.
- **Impact**: Operators using `juju info` or Charmhub see these as optional and may deploy without them, then find the charm permanently blocked.
- **Fix**: Mark all required integrations as `optional: false`, or make truly optional ones (SMTP) not block.
- **Linter rule**: "Integration marked `optional: true` (or unset) in metadata but checked with `BlockedStatus` in `_on_collect_status`" — mechanically checkable.

### 11. SMTP hard requirement blocks deployment without an ecosystem SMTP charm
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/utils.py:118` (SMTP in NOOP_CONDITIONS), `src/charm.py:437-438`
- **Evidence**: `_on_collect_status` sets `BlockedStatus("Missing integration smtp")` if no SMTP relation exists. The integration test suite deploys a raw `mailhog` Kubernetes deployment via `lightkube` to work around this (`conftest.py:202-240`). Open issue #269 acknowledges the problem.
- **Impact**: No standard SMTP charm exists on Charmhub. Operators must run their own SMTP server or deploy mailhog manually. The README does not explain how to satisfy this requirement.
- **Fix**: Make SMTP optional (warn but don't block) as suggested in #269, or document the requirement prominently with a recommended solution.
- **Linter rule**: not mechanically checkable.

### 12. `MAIL_FROM_ADDRESS` hardcoded to `identity-team@canonical.com`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/env_vars.py:25`
- **Evidence**: `DEFAULT_CONTAINER_ENV` contains `"MAIL_FROM_ADDRESS": "identity-team@canonical.com"`. Not configurable via Juju config, not settable via SMTP integration data (`SmtpProviderData` has no `from_address` field).
- **Impact**: All emails sent by the admin UI use a Canonical from address regardless of the operator's domain, causing SPF/DKIM failures for non-Canonical deployments.
- **Fix**: Add a `mail_from_address` field to `SmtpProviderData` and make it configurable via Juju config or SMTP integration data.
- **Linter rule**: "Canonical-specific email address in charm source code" — mechanically checkable.

### 13. Bad config values silently accepted; no charm-side validation; behaviour differs between Juju 3.6 and 4.0
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:380-381` (only `logger.error`), `src/configs.py:16-17`, `charmcraft.yaml:93-112`
- **Evidence**:
  - `log_level`: no `enum` constraint. `INVALIDVALUE` accepted, uppercased and passed to the workload; charm stays `active`.
  - `cpu`: no `pattern` constraint. `999xxx` accepted. On Juju 4.0, causes `BlockedStatus("Failed obtaining resource limit spec: Invalid limits spec...")` visible in status. On Juju 3.6, silently swallowed — no status change, no ERROR log.
  - `memory`: no `pattern` constraint; same behaviour as `cpu`.
  - `_on_resource_patch_failed` (`charm.py:380`) only calls `logger.error`; on Juju 3.6 the event never fires when no pebble service is running, so even this is silent.
- **Impact**: Operators get radically different feedback depending on Juju version. On Juju 3.6, invalid resource config is silently ignored; on Juju 4.0, it's surfaced in status. Neither version validates config proactively.
- **Fix**: Add `enum` for `log_level` and a regex `pattern` for `cpu`/`memory` in `charmcraft.yaml`. In `_on_resource_patch_failed`, set a visible status.
- **Linter rule**: "Config option defined without validation constraint" — mechanically checkable.

### 14. No SMTP relation-broken handler; no logging/tracing relation-broken handlers
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:278-281` (only `smtp_data_available` observed); no handlers for logging/tracing removal at all
- **Evidence**: The charm observes `self.smtp_requirer.on.smtp_data_available` but has no corresponding `relation_broken` handler. When SMTP is removed, `_on_collect_status` correctly reports blocked, but `_holistic_handler` is never called, so the pebble layer keeps the old `MAIL_*` variables. For logging and tracing, there are no relation-changed or relation-broken handlers at all; since neither is in NOOP_CONDITIONS, there's no path that triggers a pebble update on removal.
- **Impact**: Same stale-data concern as finding #2. If the operator changes SMTP providers or removes logging/tracing, the old configuration persists in the pebble layer indefinitely — stale Loki push targets, and `TRACING_ENABLED: true` persisting after tracing removal.
- **Fix**: Add `_on_smtp_relation_broken`, `_on_logging_relation_broken`, and `_on_tracing_relation_broken` handlers that call `_holistic_handler`.
- **Linter rule**: "Relation whose data flows into the pebble layer but has no relation-broken handler" — mechanically checkable.

### 15. Integration test upgrade path unconditionally skipped
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_upgrade.py:24` — `@pytest.mark.skip`
- **Evidence**: The `TestUpgrade` class is decorated with `@pytest.mark.skip` and no reason string. It deploys stable-channel charms then refreshes admin-ui to the local build — the only test of the upgrade path from a published revision to HEAD.
- **Impact**: The charm's upgrade path from any published revision to the current code is never tested in CI. The manual refresh test from rev 85 to 116 (this review) succeeded, but automated coverage of the full upgrade with all integrations would catch regressions.
- **Fix**: Add a condition to the skip (e.g., skip on PRs but run on main), or fix the test to work reliably and remove the skip.
- **Linter rule**: not mechanically checkable.

### 16. `ops.main.main()` is deprecated
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:59`
- **Evidence**: `from ops.main import main` at line 59, called at line 649 as `main(IdentityPlatformAdminUIOperatorCharm)`. Confirmed as a legacy wrapper in `deps/ops/main.py:14`. Every hook emits `DeprecationWarning: Calling ops.main.main() is deprecated, call ops.main() instead`.
- **Impact**: Low — the deprecation warning will become an error in a future ops version; the code still works but creates log noise.
- **Fix**: Change to `import ops; ops.main(IdentityPlatformAdminUIOperatorCharm)`.
- **Linter rule**: "Import of `ops.main.main` or call to `ops.main.main()`" — mechanically checkable.

### 17. `load_oauth_client_config` mutates `ClientConfig.audience` after construction
- **Severity**: low
- **Kind**: bug
- **Where**: `src/integrations.py:451` — `client.audience = [oauth_provider_data.client_id]`
- **Evidence**: `client` is a `ClientConfig`, a standard-library `@dataclass` (not a pydantic model — `oauth.py:54`). Setting `.audience` after construction relies on the dataclass being non-frozen (default). The code has a `# TODO(dushu) Remove when audience issue is fixed in login-ui` comment.
- **Impact**: If `ClientConfig` is made frozen in a future library update, this line will raise `FrozenInstanceError`. The workaround is fragile.
- **Fix**: Pass `audience` to the `ClientConfig` constructor, or fix the upstream issue in login-ui.
- **Linter rule**: not mechanically checkable (known workaround with a TODO).

### 18. `OATHKEEPER_PUBLIC_URL` env var persists in deployed charm
- **Severity**: low
- **Kind**: lint
- **Where**: observed in `pebble plan` of deployed rev 116; not present in any source file at HEAD
- **Evidence**: `pebble plan` showed `OATHKEEPER_PUBLIC_URL: ""` in the environment block. The oathkeeper dependency was removed in commit `bb1e755`. This env var does not appear in any source file under `src/`, `lib/`, or `deps/` at HEAD (`f28d3e7`).
- **Impact**: Low — cosmetic noise in the pebble plan; indicates a gap between the source at HEAD and the published charm binary.
- **Fix**: Republish a revision without the stale env var.
- **Linter rule**: not mechanically checkable.

### 19. `FileNotFoundError` traceback on Juju 4.0 during initial config-changed
- **Severity**: low
- **Kind**: bug
- **Where**: observed in Juju 4.0 debug-log; `src/integrations.py:395` (`CA_BUNDLE_PATH.read_text()`)
- **Evidence**: On Juju 4.0 (model rv-admin-ui-j4), during the initial `config-changed` hook after pod start: `ERROR unit.identity-platform-admin-ui/0.juju-log Uncaught exception while in charm code:` followed by `FileNotFoundError: [Errno 2] No such file or directory`. The pod was terminated (SIGTERM) immediately after. This traces to `_ca_bundle` calling `TLSCertificates.load()` → `CA_BUNDLE_PATH.read_text()` on `/etc/ssl/certs/ca-certificates.crt`, which doesn't exist on a fresh container with no certificates. The `ca_certificate_exists` NOOP_CONDITIONS check should short-circuit before `_ca_bundle` is accessed but apparently does not on Juju 4.0. Not observed on Juju 3.6.
- **Impact**: The pod was killed immediately after the traceback, suggesting a crash loop. The Juju 4.0/3.6 difference may stem from event ordering or Pebble socket availability differences between versions (unverified).
- **Fix**: Guard `CA_BUNDLE_PATH.read_text()` with an existence check in `TLSCertificates.load()`, and confirm `ca_certificate_exists` properly guards `_ca_bundle` access when no certificates exist.
- **Linter rule**: "`Path.read_text()` without `Path.exists()` guard" — mechanically checkable.

## Worth copying

- **Holistic reconciliation pattern** (`src/charm.py:312-508`): Most events converge on a single `_holistic_handler` method that checks preconditions, defers if not ready, prepares peer data, pushes certs, runs migrations if needed, and plans the pebble layer. Cleanly implemented with a single code path for the happy case.
- **Condition tuple pattern** (`src/utils.py:93-119`): `NOOP_CONDITIONS` and `EVENT_DEFER_CONDITIONS` are tuples of callables that take a charm and return bool, making the holistic handler's decision logic declarative, testable in isolation, and easy to extend.
- **`EnvVarConvertible` protocol** (`src/env_vars.py:48-52`): Every data class that contributes environment variables implements `to_env_vars()` via a `Protocol` class, composing the pebble layer environment from multiple sources without coupling the pebble service to every integration.
- **`PeerData` abstraction** (`src/integrations.py:53-90`): Wraps peer relation data access with JSON serialization/deserialization, a `prepare()` method for idempotent initialization, and graceful handling of missing peer relations.
- **Separation of CLI, service, integration, and charm layers** (`src/cli.py`, `src/services.py`, `src/integrations.py`, `src/charm.py`): Clean separation of concerns with each module having a clear responsibility.
- **Consistent frozen dataclasses for integration data**: `DatabaseConfig`, `OpenFGAModelData`, `KratosData`, etc. are all `@dataclass(frozen=True, slots=True)` with `load()` class methods and `to_env_vars()` instance methods, enforcing immutability and explicit data flow.
- **`ChainMap` for env var composition** (`src/services.py:143-148`): `render_pebble_layer` uses `ChainMap` and dict spread to overlay env vars from multiple sources with `DEFAULT_CONTAINER_ENV` as the base layer.
- **Good unit test coverage with `ops.testing.Context`**: 103 tests at 89% coverage using the modern ops testing approach with clean fixtures and mock isolation.
- **Well-maintained `CHANGELOG.md`**: Conventional commits and release-please formatting with clear version history.
- **`KratosData.load` checks `requirer.is_ready()` before accessing data** (`src/integrations.py:235`): The data class itself is defensive, even though the caller (`_pebble_layer`) does not use the readiness check in its conditions.
- **`DatabaseConfig.load` handles missing relations gracefully** (`src/integrations.py:109-110`): Returns a default instance when `requirer.relations` is empty, preventing crashes.

## Common-practice notes

- **Follows**: Holistic handler pattern is the de facto standard for identity-platform charms. The `src/` layout, `charmcraft.yaml`-only metadata, `lib/charms/` library layout, and `tox.ini` with fmt/lint/unit/integration all follow ecosystem convention.
- **Follows**: Uses `collect_unit_status` (the modern status API) rather than returning status from event handlers.
- **Follows**: Pins `ops` dependency and uses Ubuntu 22.04 base, consistent with the identity-platform family.
- **Follows**: The traefik-k8s ingress library uses pydantic version detection (`PYDANTIC_IS_V1`) to support both v1 and v2 APIs — a pattern other libraries should adopt.
- **Drift**: `@cached_property` on `_ca_bundle` with side-effecting code (`TLSCertificates.load` writes files, runs subprocess) is unusual — most charms compute CA bundles fresh or use explicit cache invalidation.
- **Drift**: `optional: false` only on `pg-database` but 7 integrations are treated as required at runtime — most charms keep metadata and code in sync on this.
- **Drift**: SMTP treated as required — most charms treat email as optional. Open issue #269 acknowledges this as a usability problem.
- **Drift**: `NOOP_CONDITIONS` check relation existence rather than data readiness — a common anti-pattern across identity-platform charms. `KratosData.load` already handles this correctly by checking `is_ready()`, but the condition never uses that.
- **Drift**: `ops.main.main()` is deprecated in favor of `ops.main()` — many newer charms have already migrated.
- **Drift**: The openfga library uses pydantic v1 APIs with `pydantic<2.0` PYDEPS, but the charm ships pydantic v2 — most other charm libraries in this repo (traefik, certificate_transfer, tempo) have migrated to v2 or support both.

## Tests

- **103 unit tests**, all passing (`tox -e unit`), 89% coverage, 75 warnings (pydantic v2 deprecations from charm libraries).
  - `tests/unit/test_charm.py`: 35 tests (holistic handler, upgrade, collect-status, openfga create/remove, ingress, oauth, cert, database, pebble ready).
  - `tests/unit/test_actions.py`: 15 tests covering create-identity (always with password), all migration actions.
  - `tests/unit/test_cli.py`: 18 tests.
  - `tests/unit/test_integrations.py`: 20 tests covering PeerData, DatabaseConfig, OpenFGA, OAuth.
  - `tests/unit/test_services.py`: 10 tests.
- **`ruff check`**: passes with zero issues.
- **`codespell`**: configured via tox lint.

### Test gaps relative to findings
- No test for `create-identity` without `password` (finding #1).
- No test for stale env vars after integration removal (finding #2).
- No test for `@cached_property` on `_ca_bundle` after certificate rotation (finding #3).
- No test for `PebbleService.stop()` failing because of `startup: enabled` (finding #4).
- No test for `_on_collect_status` with container not connected (finding #7).
- No test for `SmtpProviderData.load()` with missing secret (finding #8).
- No test for bad config values (finding #13).
- No test for logging/tracing relation-broken (finding #14).
- `oauth_is_ready()` at `src/utils.py:68` is defined but never called — dead code.

### Integration tests (`tests/integration/test_charm.py`)
- Build/deploy via identity_bundle.yaml, data checks for all 7 core integrations (kratos, hydra, OpenFGA, ingress, OAuth, peer, SMTP, database), create-identity action (always with `password`), scale up to 2, parametrized remove-integration for 6 integrations (openfga, kratos, hydra, ingress, certificate_transfer, database — does NOT include SMTP or oauth), scale down, remove-application.
- Integration tests check relation data (app-level databag) but not pebble layer content after removal — the stale env var bug (finding #2) is not caught.
- SMTP removal and OAuth removal are NOT tested (not in the parametrized list).
- The mailhog deployment (`conftest.py:202-240`) uses `lightkube` directly to create raw Kubernetes Deployment and Service resources — a brittle dependency that could break on K8s API changes.

### Upgrade test (`tests/integration/test_upgrade.py`)
- `@pytest.mark.skip` with no reason string. The upgrade path from published to HEAD is never tested in CI. The test infrastructure (jubilant + mailhog + full identity bundle) is the same as the main integration test, which passes.

## Docs

- **README.md**: Covers description, deploy, all integrations with example commands, and actions. Missing: SMTP requirement explanation, observability integrations (logging, tracing, metrics-endpoint, grafana-dashboard), and correct `create-identity` trait format (`traits` is an object, not flat key=value).
- **CONTRIBUTING.md**: Clear setup with tox, pre-commit, and multipass-based integration test workflow.
- **SECURITY.md**: Present (535 bytes).
- **CHANGELOG.md**: Well-maintained.
- **charmhub.md** (from context): Minimal description — "Charmed Operator for Canonical Identity Platform's Admin Interface" with no integration details or usage instructions.
- **Doc/reality mismatches**:
  - README shows `create-identity` with `traits.email=<email>` as a flat string, but the action schema defines `traits` as an object needing JSON: `traits='{"email":"..."}'`.
  - README doesn't explain SMTP requirement or how to satisfy it (mailhog).
  - README doesn't list observability integrations the charm supports.
  - `charmcraft.yaml` `optional` mismatch (finding #10).

## Open questions

- **Why is the upgrade test skipped?** The `@pytest.mark.skip` has no reason/condition. The test infrastructure (jubilant + mailhog) is the same as the main integration test, which passes. Running it would settle whether upgrade from published to HEAD works end-to-end.
- **Does `OATHKEEPER_PUBLIC_URL: ""` cause issues in the workload?** The empty string default is harmless, but it indicates incomplete cleanup in the published charm binary vs. HEAD.
- **Will the pydantic v2 warnings from `lib/charms/` libraries cause real breakage?** The charm installs pydantic v2 but multiple libraries (openfga, traefik ingress, tempo tracing) use v1-era `class Config` patterns. The openfga library is the most at risk with explicit `pydantic<2.0` PYDEPS and use of `parse_raw`, `__fields__`, and `@validator`. These are warnings now but could become errors in pydantic v3.
- **Juju 4.0 ecosystem compatibility**: The charm runs on Juju 4.0 but its required PostgreSQL dependency does not. Operators on Juju 4.0 cannot use this charm until `postgresql-k8s` supports Juju 4.0.
- **Why does `FileNotFoundError` occur on Juju 4.0 but not 3.6?** The traceback observed on Juju 4.0 during config-changed suggests `_ca_bundle` is accessed through a path that's guarded on 3.6 but not on 4.0, or hook firing order differs between Juju versions (finding #19, unverified as to root cause).
