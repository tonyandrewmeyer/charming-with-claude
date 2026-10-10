# cos-registration-server-k8s

The COS registration server is a Django-backed k8s charm that registers robotics devices and feeds their data (dashboards, alert rules, blackbox probes, device TLS certificates) into the COS observability stack. It deploys cleanly, blocks correctly when its database relation is missing, and passes lint/static/unit checks. But its one operator-facing action is permanently broken, its liveness model is incomplete (Juju can report `active` while the workload is dead), its custom TLS pipeline depends on private upstream APIs, and channel refreshes are blocked by a certificates interface incompatibility. A maintainer should first fix the `get-admin-password` action (missing `DATABASE_URL` in the exec environment) and add a real liveness check to `_update_layer_and_restart`, since both defects mean the charm can silently and permanently fail while Juju status says everything is fine.

| | |
|---|---|
| Repo | canonical/cos-registration-server-k8s-operator @ `92fed0d` (2026-07-21) |
| Charms | cos-registration-server-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), charmhub `latest/edge` rev 21, integrated with postgresql-k8s, self-signed-certificates, traefik-k8s, grafana-agent-k8s, prometheus-k8s, loki-k8s, blackbox-exporter-k8s. Also deployed standalone on concierge-k8s-4 (Juju 4.0.5) — postgresql-k8s has no Juju-4.x-compatible channel, so full integration could not be tested there. Channel refresh tested (`latest/beta` rev 12, `0/stable` rev 14). |
| Reviewed | 2026-07-27 |

## What it does

- Deploys a single workload container running Gunicorn on port 8000, managed by Pebble.
- Requires a PostgreSQL relation (`data_platform_libs.v0.data_interfaces`) to function; blocks with a clear message without it.
- Fetches Grafana dashboards, Loki alert rules, Prometheus alert rules, device SSH keys, and device IP endpoints from its own REST API (`/api/v1/...`) and republishes them over the corresponding COS relations (grafana-agent, prometheus, loki, blackbox-exporter).
- Runs a custom TLS pipeline: fetches pending device CSRs from the DB, submits them to a TLS provider (e.g. self-signed-certificates), and patches the signed certificate back into the DB.
- Provides a `get-admin-password` action to retrieve Django admin credentials (currently broken — see findings).
- Ships a Terraform module for declarative deployment.

## Deployment log

**Primary deployment** on `concierge-k8s-3` (Juju 3.6.25, model `rv-deep`):

```bash
juju add-model rv-deep
juju deploy cos-registration-server-k8s --channel edge --resource cos-registration-server-image=ghcr.io/canonical/cos-registration-server:dev
juju deploy postgresql-k8s --channel 14/stable --trust
juju integrate cos-registration-server-k8s:database postgresql-k8s:database
```

Reached `active` ~30s after the database relation settled; Postgres itself took ~2min to install.

**Relation removal test:**
```bash
juju remove-relation cos-registration-server-k8s:database postgresql-k8s:database
# → workload=blocked "Database not configured yet" within 15s
juju integrate cos-registration-server-k8s:database postgresql-k8s:database
# → recovered to active within 60s, no tracebacks
```

**Juju 4.x** on `concierge-k8s-4` (Juju 4.0.5): charm deploys cleanly but reaches `unknown` status without a database — postgresql-k8s (14/stable, 14/edge rev 939, 16/stable) all refuse to deploy on Juju 4.x ("charm requires Juju version < 3.5.0" or similar). Full integration was not testable on Juju 4.x as a result.

**Scale-up:** 1→2 units without tracing succeeds (both active). Scaling to 2 and then adding the `tracing` relation (`grafana-agent-k8s:tracing-provider`) also succeeds on rev 21 — both units remain active. Non-leader unit debug-log shows `"failed validating relation data for tracing:8"`, which is expected: `TracingEndpointRequirer.is_ready()` correctly returns `False` when relation data isn't populated yet, and `@trace_charm` falls back to buffer-only mode. (An earlier note suspected a crash on scale-up with tracing active on an earlier revision; on rev 21 this does not reproduce — treat that earlier claim as superseded.)

**Channel refresh — blocked:** `juju refresh cos-registration-server-k8s --channel latest/beta` (rev 12) and `--channel 0/stable` (rev 14) both fail:
```
cannot upgrade application "cos-registration-server-k8s" to charm "ch:amd64/cos-registration-server-k8s-12":
would break relation "cos-registration-server-k8s:certificates self-signed-certificates:certificates"
```

**Application removal:** `juju remove-application cos-registration-server-k8s --force --no-wait --destroy-storage` removes cleanly; Postgres is left unaffected.

**Second deployment** (model `rv-deep2`, Juju 3.6.25, rev 21) for targeted failure injection:

```bash
juju deploy cos-registration-server-k8s --channel edge --resource cos-registration-server-image=ghcr.io/canonical/cos-registration-server:dev
juju deploy postgresql-k8s --channel 14/stable --trust
juju integrate cos-registration-server-k8s:database postgresql-k8s:database
# → active ~90s after deploy

juju deploy self-signed-certificates --channel edge
juju integrate cos-registration-server-k8s:certificates self-signed-certificates:certificates
# → stays active, no CSRs to process (empty DB)

juju deploy traefik-k8s --channel edge --trust
juju integrate cos-registration-server-k8s:ingress traefik-k8s
# → active, external_url becomes http://10.43.45.0/..., Pebble ALLOWED_HOST_DJANGO updated
```

**Ingress revocation test:**
```bash
juju remove-relation cos-registration-server-k8s:ingress traefik-k8s
# → charm stays active but ALLOWED_HOST_DJANGO still contains stale traefik IP 10.43.45.0
# → Pebble layer never updated; _on_ingress_revoked only logged "This app no longer has ingress"
```

## Observed behaviour

**Resource use**: 96Mi RAM, 1m CPU (single gunicorn worker). Lean.

**Install time**: ~35s from deploy to agent idle, then another ~55s for the database relation to propagate and the workload to reach active.

**Pebble plan**: single service `cos-registration-server` running `/usr/bin/launcher.bash` (gunicorn). Environment includes `DATABASE_URL` (full Postgres credentials visible in plan), `ALLOWED_HOST_DJANGO`, `SCRIPT_NAME`, `COS_MODEL_NAME`, `CSRF_TRUSTED_ORIGINS`.

**Hook count**: ~25 hooks for a full deploy cycle; no spurious re-renders at idle.

**Pebble service lifecycle:**

| Operation | Pebble behaviour | Juju status | Recovery |
|---|---|---|---|
| `kill -9 <gunicorn>` | Auto-restarts within ~5s (`override: replace` detects main process exit) | `active` throughout | Automatic |
| `pebble stop <service>` | Service becomes `inactive` and stays inactive across multiple `update-status` hooks | `active` (incorrect) | Never — needs a manual `pebble start` |
| Database relation removed | Service keeps running, charm sets `blocked` | `blocked (Database not configured yet)` | Re-adding relation restarts correctly |

`pebble stop` was confirmed twice (`rv-deep` at 20:54 UTC, `rv-deep2` at 21:06 UTC): waited 45+ seconds / 4 `update-status` cycles in each case, service stayed `inactive`, Juju stayed `active`. `_update_layer_and_restart()` (`src/charm.py:402-428`) only diffs Pebble layer dicts; if the layer is unchanged it never calls `container.restart()`, and there is no `is_running()` check anywhere.

**Kubectl exec internals:**
- `/usr/bin/`: `launcher.bash`, `create_super_user.bash`, `install.bash`, `configure.bash` — all root:root 755.
- `install.bash` generates the Django secret key into `/server_data/secret_key`.
- `configure.bash` runs `manage.py migrate` with `DATABASE_URL` from the environment.
- `create_super_user.bash` runs `manage.py createsuperuser`, reads `SECRET_KEY_DJANGO` from file, but does **not** receive `DATABASE_URL` — relies entirely on the exec's own environment.
- `/server_data/` contains only `secret_key` and `lost+found`.
- Gunicorn's own process environment does contain `DATABASE_URL` with full credentials.

**`get-admin-password` action**: returns `password: ""` on every invocation, confirmed across three separate deployments (`rv-deep` ×2, `rv-deep2` ×1). `_generate_admin_password` (`src/charm.py:262`, notes cite `:266-273`) execs `create_super_user.bash` with `DJANGO_SUPERUSER_PASSWORD`/`DJANGO_SUPERUSER_EMAIL`/`DJANGO_SUPERUSER_USERNAME` but no `DATABASE_URL`. Django falls back to an in-memory SQLite DB with no tables (`sqlite3.OperationalError: no such table: auth_user`). The admin URL itself is composed correctly.

**External URL propagation**: `external_url`/`external_host` log `WARNING: No ingress URL configured, returning internal URL` on every call before the ingress relation is ready. Called from multiple hook handlers, producing 20+ warning lines in debug-log during startup.

**Ingress revocation leaves stale hostname in Pebble layer**: after `juju remove-relation cos-registration-server-k8s:ingress traefik-k8s`, the Pebble layer's `ALLOWED_HOST_DJANGO` (set at `src/charm.py:611`) still contained the traefik IP `10.43.45.0`. `_on_ingress_revoked` (`src/charm.py:254-255`, notes cite `163-164`) only logs `"This app no longer has ingress"` and never calls `_update_layer_and_restart()`. Matches open issue #61.

**Startup error noise**: before the workload is up, the TLS pipeline, blackbox probes, and auth-keys fetchers all hit the not-yet-running workload's HTTP API, producing 20+ ERROR-level `Connection refused` lines with full stack traces in debug-log. Transient but noisy; confirmed across multiple deployments.

**No charm-owned config keys**: `charmcraft.yaml` has no `options` block; `juju config cos-registration-server-k8s` returns only library-managed keys (Traefik ingress library).

**Juju 4.x status display differs**: without a database on Juju 4.0.5, app status shows `unknown` (not `blocked`), and the workload shows `running` even though the Pebble service is `inactive`. `CollectStatusEvent` behaves differently across Juju versions.

**Relation data flow (verified via full integration):**
- `probes` → blackbox-exporter: HTTP 2xx probe targeting Traefik URL, correct.
- `probes-devices` → blackbox-exporter: `scrape_probes: '[]'` (no devices in DB — expected).
- `grafana-dashboard` → grafana-agent: dashboard UIDs set correctly.
- `receive-remote-write` → prometheus: URL provided, no alert-rules data (no devices in DB).
- `tracing` → grafana-agent: `receivers: '[]'` (grafana-agent has no tracing backend configured).

## Findings

### Admin password action always returns empty — `DATABASE_URL` missing from exec environment
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:262` (`_generate_admin_password`)
- **Evidence**: The `container.exec()` call passes `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_USERNAME` but no `DATABASE_URL`. `juju run cos-registration-server-k8s/0 get-admin-password` returned `password: ""` on every invocation across three separate deployments. Without `DATABASE_URL`, Django's `createsuperuser` falls back to an in-memory SQLite DB and fails with `sqlite3.OperationalError: no such table: auth_user`.
- **Impact**: The charm's only action is permanently broken; operators can never obtain admin credentials through the intended mechanism.
- **Fix**: Add `"DATABASE_URL": self.database_url` to the environment dict passed to `container.exec()` in `_generate_admin_password()`.
- **Linter rule**: "`container.exec()` called with an environment dict lacking `DATABASE_URL` while the charm has a database relation" — partially mechanically checkable.

### Workload not restarted if stopped externally — no liveness check
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:402-428` (`_update_layer_and_restart`)
- **Evidence**: The function decides whether to restart solely by comparing `services != new_layer_dict["services"]`. Confirmed twice (`rv-deep` 20:54 UTC, `rv-deep2` 21:06 UTC): after `pebble stop`, the service stayed `inactive` across 45+ seconds and multiple `update-status` hooks while Juju reported `active`. By contrast `kill -9` on gunicorn does trigger a Pebble restart within ~5s via `override: replace` detecting the main-process exit — that path works.
- **Impact**: If a service is stopped for maintenance and not manually restarted, the charm reports healthy while the workload is permanently down.
- **Fix**: In `_update_layer_and_restart`, check `container.get_service(self.name).is_running()` and restart regardless of layer diff, or add an explicit liveness check in `_on_update_status`.
- **Linter rule**: "Pebble layer diff used as sole restart condition without checking actual service state" — not easily mechanically checkable.

### Custom TLS library imports private upstream APIs
- **Severity**: high
- **Kind**: bug
- **Where**: `src/tls_certificates_devices.py:19-21`
- **Evidence**: Imports `_CertificateSigningRequest`, `_ProviderApplicationData`, `_RequirerData` from `charms.tls_certificates_interface.v4.tls_certificates`. The upstream module's own comment states these "should not be imported outside of this module."
- **Impact**: Any upstream change to these `_`-prefixed symbols (which carry no stability guarantee) can silently break this charm.
- **Fix**: Either upstream pre-generated-CSR support into `tls_certificates_interface` directly, or vendor the needed types instead of importing private symbols.
- **Linter rule**: "Import of a private (`_`-prefixed) symbol from a charm library outside its own module" — mechanically checkable.

### `_on_ingress_revoked` only logs — does not reconfigure the workload, leaves stale hostnames
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:254-255`
- **Evidence**: `def _on_ingress_revoked(self, _): logger.info("This app no longer has ingress")` — never calls `_update_layer_and_restart()`. Confirmed on `rv-deep2`: after `juju remove-relation cos-registration-server-k8s:ingress traefik-k8s`, `ALLOWED_HOST_DJANGO` (set at `src/charm.py:611`) still contained the traefik IP `10.43.45.0`; service not restarted. Matches open issue #61.
- **Impact**: When the ingress relation is removed or the external IP changes, the workload continues serving with a stale hostname until some other event triggers a layer update.
- **Fix**: Call `self._update_layer_and_restart(None)` from `_on_ingress_revoked`.
- **Linter rule**: not mechanically checkable.

### Admin-password unit test never asserts the password is non-empty
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:56-64`
- **Evidence**: `test_create_super_user_action` checks `len(action_output.results) == 3` and that the password is consistent across two calls, but never asserts `action_output.results["password"]` is non-empty. The harness mock for `create_super_user.bash` returns `result=0` unconditionally, masking the real `DATABASE_URL` bug.
- **Impact**: The critical admin-password bug (above) passes CI undetected.
- **Fix**: Add `self.assertNotEqual(action_output.results["password"], "")` and configure the harness to validate that `DATABASE_URL` is present in the exec environment.
- **Linter rule**: not mechanically checkable.

### Cannot refresh between channels — certificates interface incompatibility
- **Severity**: medium
- **Kind**: bug
- **Where**: `juju refresh` from `latest/edge` (rev 21) to `latest/beta` (rev 12) or `0/stable` (rev 14)
- **Evidence**: Both refreshes fail with `cannot upgrade application "cos-registration-server-k8s" ... would break relation "cos-registration-server-k8s:certificates self-signed-certificates:certificates"`.
- **Impact**: Operators cannot downgrade or switch release tracks without first removing and re-adding the certificates relation, risking loss of device certificate state.
- **Fix**: Document the breaking interface change in release notes; ensure future certificates-relation schema changes are backward compatible or provide a migration path.
- **Linter rule**: not mechanically checkable.

### `_cleanup_certificate_requests` unconditionally removes and re-adds all CSRs
- **Severity**: medium
- **Kind**: bug / performance
- **Where**: `src/tls_certificates_devices.py:86` (call site in `_configure`), `:256` (definition; notes cite `258-260`)
- **Evidence**: `_cleanup_certificate_requests()` removes every CSR from relation data on every call, logging "Removed CSR from relation data because it did not match any certificate request" regardless of whether it actually matched, and `_send_certificate_requests()` immediately re-adds them. `_configure()` runs this on `relation_created`, `relation_changed`, and `update_status`.
- **Impact**: Constant churn on relation data on every reconcile, with a misleading log message that hampers debugging, and a possible race with the provider reading/populating certificates.
- **Fix**: Only remove CSRs no longer present in the current `certificate_signing_requests` list; make the log conditional on an actual removal.
- **Linter rule**: not mechanically checkable.

### Loud error spam during charm initialisation
- **Severity**: medium
- **Kind**: performance / ux
- **Where**: `src/charm.py` — TLS pipeline `_configure`, `_get_devices_ip_endpoints_from_db` (~line 672-703), `_get_auth_devices_keys_from_db` (~line 461-476)
- **Evidence**: Every hook handler that queries the workload's own REST API before gunicorn is up emits ERROR-level `Connection refused` with full `HTTPConnectionPool`/`NewConnectionError` traces. 20+ identical lines observed per deploy, across multiple deployments.
- **Impact**: Floods debug-log, obscuring real issues; each failed call also burns a retry/timeout budget.
- **Fix**: Guard self-HTTP calls behind `container.get_service(self.name).is_running()`, or downgrade to WARNING until the service is confirmed running.
- **Linter rule**: "HTTP request to self workload URL without a container-readiness check" — not easily mechanically checkable.

### TLS certificates integration test asserts empty data — no validation of certificate flow
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py:135-141` (notes cite `109-114`)
- **Evidence**: `test_integrate_self_signed_certificates` asserts `data == []`, commented "expected to be empty since certificates are stored as secrets." No test sends a CSR, waits for a signed certificate, or checks that the DB is patched.
- **Impact**: The most complex, most fragile part of the charm (private-API-dependent TLS pipeline) has zero integration coverage; a regression would not be caught.
- **Fix**: Add a test that seeds a device CSR in the database, waits for a signed certificate over the relation, and verifies the DB patch.
- **Linter rule**: not mechanically checkable.

### `CatalogueConsumer` uses deprecated v0 API
- **Severity**: low
- **Kind**: lint / docs
- **Where**: `src/charm.py:19`
- **Evidence**: `from charms.catalogue_k8s.v0.catalogue import CatalogueConsumer, CatalogueItem`; unit tests emit `DeprecationWarning: charms.catalogue_k8s.v0.catalogue is deprecated. Use charms.catalogue_k8s.v1.catalogue instead.`
- **Impact**: v0 will eventually be removed; a documented migration path already exists.
- **Fix**: Migrate to `charms.catalogue_k8s.v1.catalogue`.
- **Linter rule**: "import from deprecated charm library version" — mechanically checkable.

### `_update_grafana_dashboards` mutates the API response in place
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:339`
- **Evidence**: `dashboard["dashboard"]["uid"] = dashboard["uid"]` mutates the dict returned by `_get_grafana_dashboards_from_db()`.
- **Impact**: Currently harmless since the response isn't reused, but a latent hazard if the code is refactored.
- **Fix**: `dashboard = dict(dashboard)` before mutating.
- **Linter rule**: "mutation of dict values returned from a fetch method" — not easily mechanically checkable.

### Fragile chain-ordering heuristic in `_on_certificate_available`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:580-581`
- **Evidence**: `if str(chain[0]) != str(event.certificate): chain.reverse()` — guesses ordering from a single string comparison.
- **Impact**: Could reverse the chain incorrectly for some TLS provider configurations (e.g. duplicate/self-signed intermediates).
- **Fix**: Use a proper method for chain ordering, or rely on the provider library's documented order.
- **Linter rule**: not mechanically checkable.

### Variable shadowing in `_on_certificate_available`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:579`
- **Evidence**: `chain = [str(certificate) for certificate in event.chain]` shadows the outer `certificate = str(event.certificate)` from the previous line.
- **Impact**: Readability/maintenance risk only; no current runtime bug.
- **Fix**: Rename the comprehension variable, e.g. `[str(cert) for cert in event.chain]`.
- **Linter rule**: variable shadowing (ruff `A001`) — mechanically checkable.

### `_scheme` property always returns "http" — misleading name
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:623-624`
- **Evidence**: Returns `"http"` unconditionally, even with TLS certificates configured (correct, since TLS terminates at ingress, but the name implies it might vary).
- **Impact**: Confusing for future maintainers.
- **Fix**: Rename to `_internal_scheme` or add a clarifying comment.
- **Linter rule**: not mechanically checkable.

### Copy-paste bugs in `AuthDevicesKeysProvider` error messages
- **Severity**: low
- **Kind**: bug
- **Where**: `src/auth_devices_keys.py:109-110`, `:128` (notes cite `84-85`, `100-101`)
- **Evidence**: `RelationInterfaceMismatchError.__init__` uses `{actual_relation_interface}` twice instead of expected-then-actual; `RelationRoleMismatchError.__init__` has the analogous bug with `{actual_relation_role}`. Neither exception is currently raised in the codebase.
- **Impact**: If ever raised, the message would show the actual value where the expected value belongs, misleading operators.
- **Fix**: Correct the format strings.
- **Linter rule**: "same variable used twice in a format string while a similarly-named variable goes unused" — mechanically checkable.

### `AuthDevicesKeysConsumer` fires a spurious changed event on first run
- **Severity**: low
- **Kind**: performance
- **Where**: `src/auth_devices_keys.py:169-171`
- **Evidence**: `coerced_data` is `[]` on first run while `databag` is a JSON string, so `[] != "[...]"` is always `True` and the event fires spuriously on first `relation-changed`.
- **Impact**: Harmless today, but wasted work if more consumers are added.
- **Fix**: Compare parsed JSON to parsed JSON (or `json.dumps(coerced_data)` to `databag`).
- **Linter rule**: not mechanically checkable.

### README claims the charm is "not available yet on CharmHub"
- **Severity**: low
- **Kind**: docs
- **Where**: `README.md:7`
- **Evidence**: States the charm "is still under development and is not available yet on CharmHub," but it is published on `latest/edge` (rev 21), `latest/beta` (rev 12), and `0/stable` (rev 14), confirmed via `juju info cos-registration-server-k8s`.
- **Impact**: Misleads users into thinking they must build from source.
- **Fix**: Update the README with current publication status and a `juju deploy` command.
- **Linter rule**: not established.

### CONTRIBUTING.md references a non-existent `static` tox environment
- **Severity**: low
- **Kind**: docs
- **Where**: `CONTRIBUTING.md:15`
- **Evidence**: Lists `tox run -e static`, but `tox.ini` defines `static-charm` and `static-lib`, not `static`.
- **Impact**: A contributor following the docs hits an error (CI itself uses the correct env names, so low overall impact).
- **Fix**: Change to `static-charm` in CONTRIBUTING.md, or add a `static` alias in `tox.ini`.
- **Linter rule**: not established.

### Terraform test has a stale assertion error message
- **Severity**: low
- **Kind**: test-gap
- **Where**: `terraform/tests/main.tftest.hcl:10` (notes cite line 9)
- **Evidence**: `condition = length(module.cos_registration_server_k8s.requires) == 8` but `error_message` says "Expected 6 required integration endpoints."
- **Impact**: A failing assertion would show a misleading "6" instead of "8," slowing debugging.
- **Fix**: Update the error message to say 8.
- **Linter rule**: "literal value in assertion condition does not match literal in error message" — mechanically checkable with a custom rule.

### No explicit upgrade-charm handler
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/charm.py` — no `self.framework.observe(self.on.upgrade_charm, ...)`
- **Evidence**: State reconciliation after upgrade relies on library-level `refresh_events` (e.g. `update_status` for TLS, `config_changed` for blackbox); there is no dedicated handler, and no test covers the upgrade path.
- **Impact**: Works in practice since `StoredState` persists, but fragile if a future upgrade needs an explicit data migration.
- **Fix**: Add an `_on_upgrade_charm` handler, even as a no-op, as an explicit hook point.
- **Linter rule**: "charm has `StoredState` but no `upgrade_charm` handler" — mechanically checkable.

### Juju 4.x: `CollectStatusEvent` masks the blocked state
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:591-593` (`_on_collect_status`)
- **Evidence**: On Juju 3.6 without a database, unit status shows `blocked (Database not configured yet)`. On Juju 4.0.5 the app status shows `unknown` and the workload shows `running` even though Pebble is `inactive`. The charm never explicitly adds `BlockedStatus` at the app level in `_on_collect_status` — it relies on the unit status set from `_update_layer_and_restart`.
- **Impact**: On Juju 4.x, operators lose the visible `blocked` signal for a genuinely broken deployment.
- **Fix**: Add `event.add_status(BlockedStatus(...))` in `_on_collect_status` when `database_url` is empty, so app-level status is consistent across Juju versions.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Hash-based change detection** (`src/charm.py:330-356`): dashboards/alert-rules/keys are MD5-hashed and relations only updated on change — avoids unnecessary Pebble restarts and relation churn.
- **Database-missing → blocked status** (`src/charm.py:407-409`): clean, human-readable `BlockedStatus("Database not configured yet")` with clean automatic recovery on relation re-add.
- **Blackbox probes for registered devices** (`src/charm.py:672-703`): dynamically generates ICMP probes per device in the DB — good example of data-driven probe generation.
- **`CollectStatusEvent` for app status aggregation** (`src/charm.py:591-593`): modern `collect_app_status` pattern for aggregating blackbox-probe provider status.
- **Terraform module with CI validation**: `terraform fmt`/`validate`/`test` in CI, terraform-docs-generated docs, sensible default of 1 unit (matches the known scale limitation).
- **Declarative `charm-libs` in `charmcraft.yaml:19-46`**: modern approach over manually bundled libraries (migration still in progress, tracked in issue #25).
- **Graceful handling of optional relations**: certificates, tracing, and logging relations are all optional and don't error when absent; only the database relation blocks.
- **`override: replace` in the Pebble layer**: correct setting for a daemon — lets Pebble auto-restart on main-process exit (confirmed via the `kill -9` test).

## Common-practice notes

- **Custom libraries under `src/` rather than `lib/`**: `src/auth_devices_keys.py` and `src/tls_certificates_devices.py` were intentionally moved from `lib/` to `src/` (commit `3ee87ca`), a departure from convention that makes sense for libraries not meant for external consumption — but the rationale isn't documented (see open questions).
- **`StoredState` usage**: deprecated in ops 2.x in favor of plain attributes, but consistent with the rest of the COS charm ecosystem for now.
- **Juju version assumption**: `charmcraft.yaml` declares `juju >= 3.4.3`; CI runs Juju 3.6. The charm itself deploys standalone on Juju 4.0.5, but full integration testing is blocked by postgresql-k8s's lack of a Juju-4.x-compatible channel.
- **`requests` for internal HTTP calls to its own REST API**: standard for COS charms; goes through the k8s service DNS.
- **Credentials in Pebble environment variables**: `DATABASE_URL` with full credentials is stored as plain Pebble-plan environment — standard for k8s charms (pod-scoped visibility), though Juju secrets would be more secure.
- **`charm-libs` coexisting with `lib/`**: transitional state migrating from `charmcraft fetch-lib` to the declarative system, tracked in open issue #25.

## Tests

### What exists
- **Unit tests** (`tests/unit/test_charm.py`): 23 tests using the (deprecated) ops `Harness`. Cover dashboard hash detection, auth-keys fetch/hash, Loki/Prometheus alert rules, CSR fetching, certificate patching, MD5 utilities. All pass.
- **Integration tests** (`tests/integration/`): Jubilant-based (migrated from pytest-operator, commit `d126a90`), deploying with postgresql, prometheus, grafana-agent, blackbox-exporter, and self-signed-certificates; assert relation-data content for alert rules, dashboards, probes, tracing, TLS.
- **Terraform tests** (`terraform/tests/`): `terraform test` validates the module deploys.

### Static analysis
- `tox -e lint` (ruff + codespell): PASS, 0 issues
- `tox -e static-charm` (pyright 1.1.327): PASS, 0 errors, 0 warnings
- `tox -e unit`: 23/23 PASS, coverage 57% overall (`charm.py` 77%, `auth_devices_keys.py` 38%, `tls_certificates_devices.py` 22%)

### Coverage gaps
- `src/tls_certificates_devices.py` at 22% coverage: no tests for `_configure`, `_find_available_certificates`, `_request_certificate`, `_cleanup_certificate_requests`, or the CSR send flow.
- `src/auth_devices_keys.py` at 38% coverage: consumer/provider relation-handling logic largely untested.
- No negative tests for database API errors, `container.exec()` failures, malformed relation data, or ingress URL changes.
- No upgrade or channel-refresh tests.
- No multi-unit scale tests.

### Integration test quality
Integration tests do assert specific relation-data content (e.g. `"my-alert" in data[0]["alert_rules"]`), going beyond simple active/idle waits (`test_tracing` and `test_blackbox_devices` are more shallow, only checking presence/truthiness). They do **not** cover: the `get-admin-password` action (would have caught the critical bug), scale-up, ingress removal/re-addition (would have caught the `_on_ingress_revoked` gap), the certificate-signing flow (explicitly skipped via `data == []`), channel refresh/upgrade, or Traefik/Catalogue behaviour (open issue #65).

## Docs

- **README**: clear deployment instructions for standalone and COS-lite-bundle use, but incorrectly claims the charm is "not available yet on CharmHub."
- **CONTRIBUTING.md**: references a non-existent `static` tox environment; otherwise serviceable.
- **SECURITY.md**: present, with clear reporting instructions referencing Ubuntu's disclosure policy.
- **terraform/README.md**: comprehensive, terraform-docs generated.
- **Missing**: no architecture diagram, no explanation of the custom TLS CSR pipeline, no docs for the auth-devices-keys interface, no troubleshooting section.

## Open questions

1. Why was the auth-devices-keys library moved from `lib/` to `src/` (commit `3ee87ca`)? If it's meant to be shared with consumers, it should live under `lib/` with LIBID/LIBAPI/LIBPATCH; if not, that should be explicit.
2. Can the custom TLS library be retired if upstream `tls_certificates_interface` adds pre-generated CSR support, as its own docstring anticipates? It currently depends on private `_`-prefixed upstream symbols.
3. Why does the certificates relation block channel refresh between rev 12/14 and rev 21? Was the interface/schema change documented anywhere, and is there a negotiation mechanism for such changes?
4. Is the "failed validating relation data" log on non-leader units during tracing setup worth suppressing/downgrading, given it's expected behaviour (`is_ready()` correctly returning `False` before the protocol is requested)?
5. Should `_on_collect_status` explicitly set `BlockedStatus` for the missing-database case, to make status consistent between Juju 3.x and 4.x?
6. Are the ~20+ ERROR-level connection-refused lines during startup worth suppressing or downgrading to WARNING while the Pebble service is known not to be running yet?
