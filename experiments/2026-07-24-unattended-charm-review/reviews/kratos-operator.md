# kratos

A mature, well-structured Kubernetes charm for Ory Kratos (identity and user management), published by the Canonical Identity team. The holistic-reconciler architecture, dataclass-based integration data, and unit test discipline are solid. It deploys and operates correctly given `juju trust` and a manually-created RBAC role for ConfigMap access — neither of which is documented, so a first-time deployment following the README will fail twice before it works. The most serious issue is a pebble-check race condition: a bad config value (e.g. an invalid `log_level`) crashes the kratos workload into a restart loop while Juju status keeps reporting `active`, giving operators zero signal that anything is wrong. A maintainer should fix that race first, then document the RBAC prerequisites, then close the SMTP defaults/relation-broken gaps. The charm is effectively undeployable on Juju >= 4.0 today, but that is a PostgreSQL-charm ecosystem gap, not a kratos bug.

| | |
|---|---|
| Repo | canonical/kratos-operator @ `ce1439f` (2026-07-24) |
| Charms | kratos |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), latest/edge rev 574; also concierge-k8s-4 (Juju 4.0.5), latest/edge rev 574 (blocked, no compatible postgresql-k8s) |
| Reviewed | 2026-08-02 |

## What it does

Deploys Ory Kratos, an API-first identity and user management system. Integrates with PostgreSQL (required), Hydra (OAuth2), login UI, external identity providers, registration/login webhooks, SMTP, tracing, COS observability (metrics/logging/grafana), TLS certificates via certificate-transfer, and Traefik routes (public and internal). Manages kratos configuration via a Jinja2-rendered YAML file, identity schemas via Kubernetes ConfigMaps, and offers 9 Juju actions for identity lifecycle management (create/delete/reset/list/unlink, plus admin account creation, MFA reset, session invalidation, and DB migration).

## Deployment log

### Controller: `concierge-k8s-3` (Juju 3.6.25)

Juju 4.x was attempted first but `postgresql-k8s` 14/stable does not support Juju >= 4.0.

**First deploy (rev 565, latest/stable):**
```
juju switch concierge-k8s-3
echo "rv-kratos-review" | juju add-model rv-kratos-review
juju deploy kratos --channel stable                          # rev 565
juju deploy postgresql-k8s --channel 14/stable --trust       # rev 925
juju config postgresql-k8s plugin_pg_trgm_enable=True plugin_btree_gin_enable=True
juju integrate kratos postgresql-k8s
```

**First failure**: install hook crashed with `ApiError: configmaps is forbidden`. The charm uses lightkube to create ConfigMaps (`oidc-providers`, `identity-schemas`) directly, but the default Juju service account lacks that permission. Fix:
```
kubectl create role kratos-configmap --verb=create,get,list,update,patch,delete --resource=configmaps -n rv-kratos-review
kubectl create rolebinding kratos-configmap --role=kratos-configmap --serviceaccount=rv-kratos-review:kratos -n rv-kratos-review
juju resolve kratos/0
```

**Second failure**: `BlockedStatus`: "Kubernetes resources patch failed: `juju trust` this application". Fix: `juju trust kratos --scope cluster`.

After both fixes, the charm reached `active` in ~60 seconds.

**Second deploy (rev 565, richer integrations, model `rv-kratos-deep`):**
```
juju deploy kratos --channel stable --trust
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy self-signed-certificates --channel stable
juju deploy traefik-k8s --channel stable --trust
juju deploy kratos-external-idp-integrator --channel stable
# RBAC role created as above
juju integrate kratos postgresql-k8s
juju integrate kratos self-signed-certificates
juju integrate kratos:public-route traefik-k8s
juju integrate kratos:internal-route traefik-k8s
```
All apps reached active (kratos-external-idp-integrator blocked on missing provider config, as expected). Time to active: ~3 minutes. ConfigMaps `identity-schemas` and `oidc-providers` were created (both empty).

**`juju refresh` (565 → 574, latest/stable → latest/edge):**
```
juju refresh kratos --channel latest/edge
# version v1.3.1 → v26.2.0; new endpoint kratos-login-webhook added
# Status: Waiting for database migration
juju run kratos/0 run-migration timeout=600   # succeeded
# Status: active
```
The courier pebble service appeared post-refresh (absent in rev 565). Identity data created pre-refresh (`create-admin-account`) survived the upgrade — `get-identity` returned the same identity.

**Third deploy (rev 574, latest/edge, full stack with Hydra and SMTP, model `rv-kratos-d3`):**
```
juju deploy kratos --channel latest/edge --trust                    # rev 574
juju deploy postgresql-k8s --channel 14/stable --trust              # rev 925
juju deploy self-signed-certificates --channel stable                # rev 586
juju deploy traefik-k8s --channel stable --trust                     # rev 377
juju deploy hydra --channel latest/edge --trust                      # rev 404
juju deploy smtp-integrator --channel stable                         # rev 121
# RBAC role created as before
juju integrate kratos:pg-database postgresql-k8s
juju integrate hydra:pg-database postgresql-k8s:database
juju integrate kratos:hydra-endpoint-info hydra
juju integrate kratos:receive-ca-cert self-signed-certificates
juju integrate kratos:public-route traefik-k8s
juju integrate kratos:internal-route traefik-k8s
```
All apps reached active/idle (hydra blocked on missing public-route, as expected). Kratos active in ~2 minutes. Hydra admin endpoint propagated correctly: `OAUTH2_PROVIDER_URL: http://hydra.rv-kratos-d3.svc.cluster.local:4445`. SMTP integration updated the pebble env var from the hardcoded default to `smtps://testuser:testpass@smtp.example.com:587/`.

**SMTP relation remove/re-add:**
```
juju remove-relation kratos:smtp smtp-integrator:smtp
# kratos-relation-broken fires immediately (01:13:31), but _on_smtp_data_available is NOT called
# pebble env vars stay at the integrator values (stale)
juju config kratos log_level=debug   # force config-changed
# SMTP reverts to defaults: smtps://test:test@mailslurper:1025/?skip_ssl_verify=true
juju integrate kratos:smtp smtp-integrator:smtp
# SMTP updates back to integrator values within seconds
```
The delay between relation removal and layer update is the interval until the next event that triggers `_holistic_handler` (config-changed or update-status, up to 5 minutes).

**Scale-up/down (rev 574, full stack):**
- Scale 1→2: ~60s, both units active, peer data synced correctly (`migration_version_6` on both units)
- Actions work from non-leader unit (`get-identity` on kratos/1 returned same data)
- Scale 2→1: clean scale-down

**Juju 4.x (`concierge-k8s-4`, model `rv-kratos-deepen`):**
```
juju deploy kratos --channel latest/edge --trust   # rev 574
# Enters BlockedStatus "Missing integration pg-database"
# postgresql-k8s 14/stable refused: "charm requires Juju version < 4.0.0, model has version 4.0.5"
```
- Kratos charm works on Juju 4.x: config changes accepted, actions fire (`run-migration` fails with empty error message since there's no DB), ports displayed as `4433-4434/tcp` (Juju 4.x shows port ranges).
- Cannot proceed beyond blocked: no PostgreSQL charm for Kubernetes currently supports Juju 4.x. Ecosystem gap, not a kratos bug.

**Teardown**: all models destroyed with `juju destroy-model --force --no-wait --destroy-storage`.

## Observed behaviour

### Workload interior (rev 574)
- Pebble services: `kratos` (serve all) and `courier` (courier watch) — courier absent in rev 565.
- Pebble checks: `alive` (`GET /admin/health/alive`) and `ready` (`GET /admin/health/ready`), both threshold=3.
- Workload container is scratch-based, no `ls`/`cat`/`sh`/`tar` — only `pebble` and `kratos` binaries. Debugging requires `kubectl exec ... -- /charm/bin/pebble logs` or `pebble ls`.
- SMTP env var always present: `COURIER_SMTP_CONNECTION_URI: smtps://test:test@mailslurper:1025/?skip_ssl_verify=true` when no SMTP relation exists.
- Cookie secret survives upgrades (same value pre/post refresh).
- Pod resource usage: 1m CPU, 81Mi memory (kratos-0); postgresql-k8s-0: 2m CPU, 320Mi memory.

### Config changes
- `log_level=info` → `log_level=invalid_value`: Juju accepts it (free-form string type). Kratos crashes repeatedly: `I[#/log/level] S[#/properties/log/properties/level/enum] value must be one of...`. Pebble service enters `backoff`. **Juju status remains `active`.** The `ready` check passes because kratos starts, serves the health endpoint, then crashes — all within one check interval — so `c.failures` never reaches the threshold of 3.
- `log_level=invalid_value` → `log_level=info`: recovers immediately.
- `dev=True` → `dev=False` → `dev=True`: two full kratos restarts (confirmed `"Starting the public httpd"` ×2 in pebble logs).
- `identity_schemas='{invalid json}'`: accepted by Juju, logged as error by `CharmConfigIdentitySchemaProvider._get_schemas()` (`configs.py:334-335`), but charm stays `active` — falls through to default identity schemas silently.

### Failure injection
- Kill workload process repeatedly (`pebble signal SIGKILL kratos`): pebble auto-restarts; 5 rapid kills recover to 0 failures within seconds.
- Delete pod (`kubectl delete pod kratos-0`): StatefulSet recreates it; charm enters maintenance/stop then recovers to `active` in ~30s.
- Remove `pg-database` relation: charm correctly stops the service and enters `BlockedStatus: Missing integration pg-database`. Re-adding recovers.
- Remove TLS (`receive-ca-cert`) relation: handled gracefully, charm stays `active`, CA bundle path updated.
- Remove both traefik relations (`public-route`, `internal-route`): charm stays `active`, pebble env drops `SERVE_PUBLIC_BASE_URL` and `SELFSERVICE_ALLOWED_RETURN_URLS`.

### Actions (all 9 tested)

| Action | Success | Failure modes tested |
|---|---|---|
| `create-admin-account` | ✓ (username+email, and username+email+password) | Missing `username` → clear validation error |
| `get-identity` | ✓ (by identity-id, by email) | Nonexistent ID/email → `Identity not found` |
| `delete-identity` | Exercised implicitly via get preconditions | Missing params → clear pydantic error |
| `reset-password` | ✓ | — |
| `invalidate-identity-sessions` | ✓ ("has no sessions" for fresh identity) | — |
| `list-oidc-accounts` | ✓ ("OIDC credentials not found") | — |
| `unlink-oidc-account` | Not applicable (no OIDC providers configured) | — |
| `reset-identity-mfa` | Not tested (requires MFA setup) | `mfa-type` has enum constraint in charmcraft.yaml |
| `run-migration` | ✓ (fresh deploy and after upgrade) | — |

Action error messages are clear and actionable.

### Scale
- Scale 1→2: both units reach `active` in ~60s.
- Scale 2→1: clean scale-down, unit-1 removed, unit-0 active.
- Peer relation data correctly synchronised between units.

### Hydra integration
- With `hydra-endpoint-info` relation, `OAUTH2_PROVIDER_URL` appears in kratos's pebble env pointing to hydra's admin endpoint (`http://hydra.<ns>.svc.cluster.local:4445`).
- Hydra integrates with the same postgresql-k8s (separate database) and works correctly.
- Relation data includes both `admin_endpoint` and `public_endpoint` from hydra.

### SMTP integration lifecycle
- On integration, the pebble layer updates with the correct `COURIER_SMTP_CONNECTION_URI` from the integrator's relation data.
- On relation removal, the charm does **not** update the pebble layer immediately — the old integrator URI persists because no handler is registered for `smtp-relation-broken`. Stale data remains until the next event that triggers `_holistic_handler` (config-changed, update-status, or another relation event).
- On the next config change (e.g. a `log_level` toggle), `SmtpData.load()` correctly returns the hardcoded defaults, since `self.model.get_relation("smtp")` now returns `None`.

### Juju 4.x differences
- Kratos charm deploys and runs on Juju 4.0.5 without code changes.
- Status display: Juju 4.x shows port ranges as `4433-4434/tcp`; Juju 3.6 hides them.
- `run-migration` without postgresql returns `"Database migration failed: "` (empty message after colon) — handled gracefully but unhelpful.
- `juju status` format slightly different (cosmetic only).
- Real blocker is the ecosystem: no postgresql-k8s charm supports Juju >= 4.0.

### Kratos logs
- With `dev=True`, kratos logs: "YOU ARE RUNNING Ory KRATOS IN DEV MODE. SECURITY IS DISABLED. DON'T DO THIS IN PRODUCTION!"
- "The config has no version specified" warning (upstream kratos, not a charm issue).
- TLS warnings: "TLS has not been configured for public/admin, skipping" even when `receive-ca-cert` is present — the charm passes certs via env vars rather than direct file paths in `kratos.yaml` (see Open questions).

## Findings

### Pebble check race condition — crashed workload stays `active`
- **Severity**: critical
- **Kind**: bug
- **Where**: `services.py:111-119` (`is_failing`), `charm.py:568-574` (`_on_collect_status`)
- **Evidence**: `is_failing()` checks `c.failures > 0` on the `ready` check, but the threshold is 3, and `c.failures` resets to 0 on each successful check. When kratos starts, passes `GET /admin/health/ready`, then crashes due to invalid config, the check never accumulates 3 consecutive failures. Observed: `juju config kratos log_level=invalid_value` → pebble shows the service in `backoff`, `pebble checks` shows `ready: up, 0/3 failures`, but `juju status` shows `active`.
- **Impact**: An operator can break a deployment with a config typo and get no feedback from Juju status — the workload silently crash-loops while the charm reports healthy.
- **Fix**: In `is_failing()`, also check `service.current == ServiceStatus.BACKOFF` in addition to check failures. Alternatively lower the pebble check threshold to 1, or wait/verify stabilisation after config changes in `PebbleService.plan()`.
- **Linter rule**: detect patterns where `is_failing` checks only `c.failures` without also checking `service.current`.

### `log_level` config has no validation — invalid values crash the workload with no status change
- **Severity**: high
- **Kind**: bug
- **Where**: `charmcraft.yaml` (`log_level: type: string`), `services.py:111-119`
- **Evidence**: `log_level=invalid_value` was accepted by Juju. Kratos crashed: `I[#/log/level] S[#/properties/log/properties/level/enum] value must be one of...`. Pebble showed `backoff` while `juju status` remained `active` (same race as above; `_on_collect_status` never triggers on it).
- **Impact**: Combined with the pebble race condition, an operator gets zero feedback for a bad `log_level`, despite `charmcraft.yaml`'s description listing valid values.
- **Fix**: Validate `log_level` in `CharmConfig.to_env_vars()`/`to_service_configs()`, and set `BlockedStatus` with a message listing valid values if invalid.
- **Linter rule**: flag free-form string config options whose description enumerates valid values but which have no corresponding validation function in charm code.

### Hardcoded SMTP defaults produce a misleading, non-functional connection URI
- **Severity**: medium
- **Kind**: bug
- **Where**: `integrations.py:230-239,272` (`SmtpData` defaults and `load()`)
- **Evidence**: `SmtpData` defaults to `username="test"`, `password="test"`, `server="mailslurper"`, `port=1025`, `transport_security="tls"`, `skip_ssl_verify="true"`. With no SMTP integration, `SmtpData.load()` returns `cls()` and `to_env_vars()` produces `COURIER_SMTP_CONNECTION_URI: smtps://test:test@mailslurper:1025/?skip_ssl_verify=true`. Observed in `pebble plan` on both rev 565 and rev 574.
- **Impact**: An operator who never integrates SMTP has a non-functional courier pointing at a non-existent host; with `enable_verification=True`, verification/recovery emails silently fail.
- **Fix**: Have `SmtpData.load()` return a sentinel/`None` when no relation data exists, and have `to_env_vars()` return `{}` in that case (or use empty-string defaults and guard on critical fields being empty).
- **Linter rule**: flag non-empty default field values in `@dataclass` classes named `*Data` under `src/integrations.py`.

### No handler for SMTP `relation-broken` — stale SMTP config after removal
- **Severity**: medium
- **Kind**: bug
- **Where**: `charm.py:391-393` (event registration), `lib/charms/smtp_integrator/v0/smtp.py` (library only emits on relation-changed)
- **Evidence**: `juju remove-relation kratos:smtp smtp-integrator:smtp` fires `smtp-relation-broken` at 01:13:31 (confirmed in `juju show-status-log`), but the charm only observes `smtp_requirer.on.smtp_data_available`, which only fires on relation-changed with valid data. Pebble layer retains the old integrator URI (`smtps://testuser:testpass@smtp.example.com:587/`) until the next event triggers `_holistic_handler`; a subsequent config change reverts it to the hardcoded defaults.
- **Impact**: The courier service runs with stale SMTP configuration for up to 5 minutes (update-status interval) after relation removal. If the SMTP server is decommissioned at the same time, emails may fail silently during this window.
- **Fix**: Observe `self.on.smtp_relation_broken` and call `_holistic_handler(event)`, mirroring the pattern already used for tracing (`endpoint_removed`) and receive-ca-cert (`certificates_removed`).
- **Linter rule**: flag relation endpoints with a `_data_available`/`_changed` handler but no corresponding `_broken` handler, cross-checked against `charmcraft.yaml`.

### Undocumented RBAC requirements block first-time deployment
- **Severity**: medium
- **Kind**: docs / ux
- **Where**: `charmcraft.yaml` (no RBAC manifest), `README.md` (no mention)
- **Evidence**: Deploying without `juju trust` produced `BlockedStatus: Kubernetes resources patch failed`. Deploying without a ConfigMap RBAC role produced an install-hook crash loop with `ApiError: configmaps is forbidden`. Neither is mentioned in the README or charmhub page.
- **Impact**: A new operator following the README hits both errors with no guidance.
- **Fix**: Document RBAC requirements in the README; consider shipping a Kubernetes RBAC manifest with the charm.
- **Linter rule**: not mechanically checkable.

### `identity_schemas` invalid JSON silently swallowed
- **Severity**: medium
- **Kind**: bug
- **Where**: `configs.py:328-336` (`CharmConfigIdentitySchemaProvider._get_schemas`)
- **Evidence**: `identity_schemas='{invalid json}'` was accepted by Juju. `_get_schemas()` catches `json.JSONDecodeError`, logs an error, returns `{}`, and the schema-provider fallback chain falls through to default identity schemas. Charm stays `active` with no status change.
- **Impact**: An operator believes their custom schema is active, but the charm silently falls back to defaults, risking inconsistent identity data.
- **Fix**: When `identity_schemas` is set but invalid, set `BlockedStatus` with a clear message, distinguishing "not configured" from "configured but invalid".
- **Linter rule**: not mechanically checkable (requires understanding the schema-provider fallback chain).

### `_on_upgrade_charm` does not auto-migrate — upgrades require manual action
- **Severity**: medium
- **Kind**: ux
- **Where**: `charm.py:637-644` (`_on_upgrade_charm`) vs `charm.py:699-733` (`_on_database_created`)
- **Evidence**: `_on_upgrade_charm` calls `create_configmaps()` and `_holistic_handler()`, but `_holistic_handler` short-circuits when `migration_is_ready()` is False (`NOOP_CONDITIONS`), leaving `WaitingStatus("Waiting for database migration")` indefinitely. `_on_database_created` has auto-migration logic (lines 714-733) but only on initial database creation. Observed after `juju refresh` (565→574): charm required manual `run-migration`.
- **Impact**: Upgrades stall with no automatic unblocking event, only a manual action; this may be intentional (migrations can be destructive) but is undocumented.
- **Fix**: Document that `run-migration` is required after every upgrade, or add an `auto_migrate` config option mirroring `_on_database_created`'s behaviour.
- **Linter rule**: not mechanically checkable.

### Charm is effectively unsupported on Juju >= 4.0 due to PostgreSQL ecosystem gap
- **Severity**: medium
- **Kind**: docs / ecosystem
- **Where**: `charmcraft.yaml` (no Juju version constraint), charmhub channels
- **Evidence**: Kratos deploys and runs correctly on Juju 4.0.5, but `postgresql-k8s` 14/stable refuses: "charm requires Juju version < 4.0.0, model has version 4.0.5". No Juju 4.x-compatible PostgreSQL charm for Kubernetes exists on Charmhub. Without a database, kratos cannot proceed beyond `BlockedStatus`.
- **Impact**: The charm's metadata implies Juju 4.x support (no version constraint), but it is un-deployable in practice.
- **Fix**: Document a Juju 3.x requirement, or add a Juju version constraint to `charmcraft.yaml`.
- **Linter rule**: not mechanically checkable.

### Missing test coverage on action failure paths and `clients.py`
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py`, `src/clients.py:43-222`
- **Evidence**: `tox -e unit`: 222 tests pass (9.90s). Coverage 77% overall; `charm.py` 81% (missing action-handler branches around lines 812-816, 847-848, 897-899, 925-930, 1005-1007); `clients.py` 26% (no HTTP mock tests for any of the 9 API methods); `configs.py` 81% (missing `DefaultIdentitySchemaProvider.get_schemas` file I/O paths, 422-452).
- **Impact**: `clients.py` contains all HTTP calls to the Kratos admin API; a regression in request/error handling would silently affect all 9 actions and go uncaught.
- **Fix**: Add unit tests for `HTTPClient` methods (`responses`/`requests-mock`), and Scenario-based tests for each action's success and failure paths.
- **Linter rule**: mechanically checkable via coverage thresholds.

### Workload container is scratch-based with no debugging tools
- **Severity**: low
- **Kind**: ux
- **Where**: container image `ghcr.io/canonical/kratos:26.2.0`
- **Evidence**: No `sh`/`bash`/`cat`/`ls`/`tar` in the workload container; `juju ssh --container kratos` fails with `exec: "sh": executable file not found`. Only `pebble` and `kratos` binaries available.
- **Impact**: Operators cannot easily inspect files or run diagnostics inside the container; must rely on `pebble logs`/`pebble checks`.
- **Fix**: Document the pebble-based debugging approach; consider a debug sidecar image.
- **Linter rule**: not mechanically checkable.

### Missing Hydra endpoint logged at ERROR level despite being optional
- **Severity**: low
- **Kind**: bug
- **Where**: `integrations.py:198-199` (`HydraEndpointData.load`)
- **Evidence**: With no `hydra-endpoint-info` relation, the charm logs `ERROR: Failed to fetch the hydra endpoints: Missing hydra-endpoint-info relation with hydra` on every config-changed/relation-changed event. Observed 4 times on kratos/1 during scale-up. Hydra is marked `optional: true` in `charmcraft.yaml`.
- **Impact**: ERROR-level log spam from a missing optional integration obscures real errors.
- **Fix**: Log at DEBUG/INFO when the integration is simply missing; reserve ERROR for malformed data on an existing relation.
- **Linter rule**: flag `logger.error` calls inside `load()` methods of `*Data` dataclasses catching generic `Exception`.

### `PeerData.__getitem__` returns `{}` instead of `None` for missing keys
- **Severity**: low
- **Kind**: bug
- **Where**: `integrations.py:63-67`
- **Evidence**: `__getitem__` returns `{}` when either the peer relation or the key is missing, conflating "no peer relation" with "key not set". `migration_needed` (`charm.py:452-457`) compares `{} != self._workload_service.version`, always `True` when no migration version is recorded — currently correct by accident.
- **Impact**: Fragile: future code relying on falsiness of `{}` to mean "missing" would misinterpret a legitimately empty dict.
- **Fix**: Return `None` for missing keys and have callers handle `None` explicitly.
- **Linter rule**: flag `__getitem__` implementations on relation-data wrapper classes that return `{}` rather than `None`.

### `run-migration` action returns an empty error message on Juju 4.x
- **Severity**: low
- **Kind**: ux
- **Where**: `charm.py:899-900` (action error formatting), `clients.py:56-58`
- **Evidence**: On Juju 4.x without postgresql, `juju run kratos/0 run-migration timeout=30` returned `message: 'Database migration failed: '` (empty after colon). Fails gracefully (35s) but with no diagnostic content. Works correctly with a database present on Juju 3.6.
- **Impact**: An operator gets no actionable information from a failed migration.
- **Fix**: Include the underlying exception text (`str(e)`) in the action failure message.
- **Linter rule**: flag `event.fail(message=...)` calls using a static string with no exception variable interpolated.

### `PebbleService.plan()` only detects config-file changes, not layer changes
- **Severity**: low
- **Kind**: bug
- **Where**: `services.py:147-155` (`PebbleService.plan()`)
- **Evidence**: `plan()` sets `self.config_changed` by comparing rendered config file content only. `_configure_courier()` (`charm.py:505`) uses that flag to decide whether to restart courier. If only layer env vars change (e.g. SMTP settings) without the main config file changing, `config_changed` stays `False` and courier may not be explicitly restarted; `replan()` covers the main kratos service but not necessarily courier, which has `startup: disabled`.
- **Impact**: Minor in practice — SMTP changes usually also change the main config or trigger a full replan — but the edge case exists.
- **Fix**: Track whether the pebble layer itself changed (not just the config file) and use that for `_configure_courier()`, or always restart courier when SMTP data changes.
- **Linter rule**: not mechanically checkable.

## Worth copying

1. **Holistic reconciler pattern with condition guards** (`charm.py:466-492`, `utils.py:110-129`): `_holistic_handler` is called from almost every event handler, using `NOOP_CONDITIONS`/`EVENT_DEFER_CONDITIONS` tuples to short-circuit when prerequisites aren't met — avoids state-machine complexity.
2. **Config-aware pebble restart** (`services.py:133-152`): `PebbleService.plan()` compares new vs. current config file content and only restarts when they differ, avoiding needless restarts on no-op config-changed events.
3. **Dataclass-based integration data loading** (`integrations.py`): each integration is a frozen dataclass with `load()`, `to_env_vars()`, `to_service_configs()`. Clear, type-safe, obvious data flow.
4. **Secret management abstraction** (`secret.py`): `Secrets` wraps Juju secret operations with a dict-like interface, label lookup, and an `is_ready` property.
5. **Comprehensive pre-commit config** (`pyproject.toml`): ruff, isort, codespell, mypy (strict for charm code), pytest with `-Werror` and disciplined inline suppressions for third-party warnings.
6. **Dual check in `is_failing`** (`services.py:121-124`): a fallback `service.current == ServiceStatus.ERROR` check (fix from commit `d678616`) is a good pattern — should be extended to also check `BACKOFF` (see critical finding above).
7. **Workload version management** (`services.py:68-88`): version lazily fetched from the kratos CLI, cached, pushed via `unit.set_workload_version()`.
8. **Terraform module** (`terraform/`): ships a Juju provider module with `MODULE_SPECS.md`.

## Common-practice notes

- Structurally conforms: `src/` for charm code, `lib/charms/` for libraries, `templates/` for Jinja2 templates, `tests/{unit,integration}`; platform-style bases (`ubuntu@22.04:amd64`/`arm64`); `uv` build plugin.
- Library management: mix of owned libraries (`lib/charms/kratos/v0/`) and third-party libraries from other charm repos, versioned `v0`/`v1` — standard practice.
- ops 3.8.0 with `CollectStatusEvent`: `event.add_status()` with correct status precedence — modern, well-implemented.
- No `metadata.yaml` — `charmcraft.yaml` used exclusively as the metadata source, modern convention.
- Unusual pattern: direct Kubernetes API access via `lightkube` for ConfigMap creation and StatefulSet patching. Most charms avoid this because of the extra RBAC burden; the rationale (ConfigMaps as a shared data plane readable by other charms) is sound but adds deployment friction (see RBAC finding).
- Log level inconsistency: `WARNING` for traefik "Raw mode enabled" (from traefik_route library) but `ERROR` for the missing optional hydra integration.
- Courier as leader-only singleton (`_configure_courier()`, `charm.py:492-505`): deliberate design to prevent duplicate email processing.

## Tests

**Unit tests**: 222 pass (`tox -e unit`, ~10s). Coverage 77% overall — `charm.py` 81%, `configs.py` 81%, `integrations.py` 93%. Uses `ops[testing]` (Scenario) for charm tests and conventional pytest for integration-data tests. `-Werror` enabled with filtered third-party deprecation warnings.

**Gaps**:
- `clients.py` (26% coverage) — no HTTP mock tests for any of the 9 API methods.
- Action failure paths in `charm.py` — no Scenario-based tests for error conditions.
- `configs.py:422-452` (`DefaultIdentitySchemaProvider.get_schemas`) — file I/O paths untested.
- `integrations.py`'s `ExternalIdpIntegratorData.to_service_configs` — untested.
- No integration tests for SMTP, tracing, or webhook integrations — the integration suite focuses on core login UI + database + traefik.

**Integration tests**: `tests/integration/test_charm.py` (jubilant). Cover peer data consistency, kratos-info provider databag, public/internal route config, scale up/down, all actions, identity schema config changes, and relation removal/recovery. Good happy-path coverage; no failure-injection tests (DB failover, service kill, invalid-config recovery, upgrade+rollback).

## Docs

- **README**: comprehensive — clear deployment instructions, integration examples, full action documentation, API usage examples.
- **Gap**: no mention of RBAC requirements (`juju trust`, ConfigMap permissions). The most impactful doc gap; an operator following the README exactly hits both deployment failures observed above.
- **Charmhub page**: sparse (one-line description); the "detailed documentation" link points to a readthedocs URL that 404s (the discourse link works). No mention of RBAC prerequisites or the upgrade migration workflow.
- **CONTRIBUTING.md**: standard Canonical template.
- **Terraform module docs**: `MODULE_SPECS.md` exists with variable documentation.
- **Doc/reality mismatch**: README's `juju deploy kratos` example omits `--trust`, but the charm requires it to patch the StatefulSet. The postgres config options `plugin_pg_trgm_enable=True`/`plugin_btree_gin_enable=True` in the README could not be set on the deployed `postgresql-k8s` 14/stable version *(unverified whether this is version-specific)*.

## Open questions

1. **Juju 4.x compatibility**: kratos itself deploys and runs correctly on Juju 4.0.5, but `postgresql-k8s` 14/stable refuses to deploy there and no Juju 4.x-compatible PostgreSQL charm for Kubernetes currently exists. Full integration testing on Juju 4.x is blocked on the ecosystem, not the charm.
2. **DB failover handling** (issue #606): migration versions are keyed by `migration_version_{integration_id}` in peer data. If PostgreSQL fails over to a replica, would the charm detect the changed endpoint and re-migrate? `DatabaseEndpointsChangedEvent`'s handler only calls `_holistic_handler`, without re-running migrations *(unverified — not tested against an actual failover)*.
3. **Multiple login-ui relations** (issue #704): `LoginUIEndpointData.load()` (`integrations.py:166-177`) loads endpoints from only the first `ui-endpoint-info` relation via `requirer.get_login_ui_endpoints()`. Known bug if multiple relations exist.
4. **Courier service absent from rev 565**: the courier pebble service was missing from the rev 565 pebble plan even though `services.py`'s `PEBBLE_LAYER_DICT` defines it at HEAD, and appeared after refreshing to rev 574 — suggesting it was added between those revisions. Worth confirming against the changelog.
5. **TLS certificate integration behaviour**: `receive-ca-cert` provides CA certificates pushed to the workload, yet kratos logs "TLS has not been configured for public/admin, skipping" even with the relation active. The charm passes TLS config via env vars (e.g. `SERVE_PUBLIC_TLS_ENABLED`) rather than direct file paths in `kratos.yaml`. Unconfirmed whether TLS is actually enforced at the kratos level or only at the traefik ingress.
