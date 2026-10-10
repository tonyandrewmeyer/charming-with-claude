# temporal-worker-k8s-operator

A compact Kubernetes sidecar charm that starts a Temporal worker from a user-supplied OCI image, wires it to a Temporal server via the `temporal-host-info` relation, and injects configuration, secrets, and database credentials as environment variables.

**Verdict**: Solid scenario-test coverage and clean separation of concerns, but the vault actions are completely broken due to a container-name bug, an unguarded auth-secret path crashes the charm to `error` state, the restart action leaks `MaintenanceStatus` on failure, and on Juju 4.0 the charm shows a misleading `ActiveStatus` for ~60s while the worker is crash-looping. The PostgreSQL and observability integrations work structurally. Deploy-time experience is good once the operator supplies a valid worker image — the published Charmhub resource does not contain one. A maintainer should fix the vault container-name bug first (one-line fix, breaks two user-facing actions entirely), then the auth-secret exception handling, then the restart/replan status issues.

| | |
|---|---|
| Repo | canonical/temporal-worker-k8s-operator @ `13b7c5c` (2026-06-29) |
| Charms | temporal-worker-k8s, temporal-worker-info-requirer (test-only) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (juju 3.6) and concierge-k8s-4 (juju 4.0), locally packed charm with a sample rock; Charmhub rev 32 (1.0/stable) and rev 38 (2.0/edge) were also deployed but could not run a working workload |
| Reviewed | 2026-07-25 |

## What it does

The charm deploys a Temporal worker sidecar. The operator supplies an OCI image containing workflows/activities and a `/app/scripts/start-worker.sh` entrypoint. The charm:

- Resolves the Temporal server address from the `temporal-host-info` relation (preferred) or deprecated `host` config fallback
- Passes all charm config as `TEMPORAL_*` and `TWC_*` environment variables into the workload
- Supports three sources of extra environment variables via the `environment` config: plain `env` values, Juju user secrets, and HashiCorp Vault secrets
- Integrates with PostgreSQL (`database` relation) to inject `TEMPORAL_DB_*` connection variables
- Integrates with Vault (`vault` relation) for secret storage, plus `add-vault-secret`/`get-vault-secret` actions
- Publishes `namespace` and `queue` over the `temporal-worker-info` relation for downstream charms
- Exposes Prometheus metrics, Loki log forwarding, and a Grafana dashboard
- Detects Temporal SDK eviction loops via a pebble custom check

## Deployment log

### Attempt 1: juju 4.0, 2.0/edge rev 38 (Charmhub)

```bash
juju switch concierge-k8s-4
juju add-model rv-tworker-k8s
juju deploy temporal-worker-k8s --channel 2.0/edge
# → rev 38, stuck "installing agent"; StatefulSet creation failed repeatedly:
#   "Pod temporal-worker-k8s-0 is invalid: spec.containers[0].volumeMounts[8].name:
#    Not found: temporal-worker-k8s-certs-96db9b"
```
The `certs` filesystem storage declared in `metadata.yaml` caused the StatefulSet to reference a volume mount not present in the pod spec — likely a Juju 4.0 / storage-class interaction with that specific Charmhub revision. Storage class was `csi-rawfile-default` (WaitForFirstConsumer). Model destroyed.

### Attempt 2: juju 3.6, 1.0/stable rev 32 (Charmhub)

```bash
juju switch concierge-k8s-3
juju add-model rv-tworker-k8s-3
juju deploy temporal-worker-k8s --channel 1.0/stable
# → rev 32 deployed, resource temporal-worker-image rev 18.
```

**Status**: `blocked` — "Please refresh the charm with a valid worker image". The upstream-source `ubuntu/python:3.12-24.04_stable` (18.7 MB) does not contain `/app/scripts/start-worker.sh`. Limited to observing update-status cycle and config validation without a working workload.

### Attempt 3: juju 3.6, locally packed charm with sample rock

```bash
# Built charm: charmcraft pack → temporal-worker-k8s_ubuntu@24.04-amd64.charm
# Extracted pre-built rock: resource_sample_py/temporal-worker_1.0_amd64.rock
# → POSIX tar, extracted with tar, converted to docker-archive with skopeo
# → imported into containerd k8s.io namespace via /snap/k8s/5410/bin/ctr
juju add-model rv-tworker-local
juju deploy ./temporal-worker-k8s_ubuntu@24.04-amd64.charm \
  --resource temporal-worker-image=docker.io/library/latest:latest
# → Pod running 2/2. Workload: ubuntu@22.04 temporal-worker-sample rock.
```

With required config set (`namespace`, `queue`, `host=localhost:7233`), the charm correctly constructed the pebble plan with all `TEMPORAL_*`/`TWC_*` env vars, both pebble checks, and started the service. The worker predictably failed to connect to `localhost:7233` (no Temporal server), but the charm lifecycle was fully observable.

### Attempt 4: juju 4.0, locally packed charm

Same local charm deployed on juju 4.0 worked without the storage volume-mount bug seen with rev 38. The certs storage issue appears specific to that Charmhub revision or a transient platform interaction — not established which.

### Attempt 5 (deep-dive): juju 3.6, full integrations

```bash
juju add-model rv-deep2
juju deploy /home/ubuntu/tw.charm --resource temporal-worker-image=docker.io/library/latest:latest
juju deploy postgresql-k8s --channel 14/stable
juju deploy grafana-agent-k8s --channel 0.40/stable
juju deploy self-signed-certificates --channel 1/stable
juju relate temporal-worker-k8s:database postgresql-k8s:database
juju relate temporal-worker-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju relate temporal-worker-k8s:logging grafana-agent-k8s:logging-provider
juju relate temporal-worker-k8s:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
```

All relations established. Metrics scrape jobs (targets `*:9000`) and the `temporal-monitoring` Grafana dashboard correctly published; logging endpoint URL shared. PostgreSQL credentials did not propagate during the observation window (>3 min) — `DB_HOST`/`DB_PORT`/`DB_PASSWORD`/`DB_USER`/`DB_TLS` remained absent while relation data on the charm side showed only `requested-secrets`. This appears to be postgresql-k8s taking time to complete its handshake, not a temporal-worker-k8s bug.

### Attempt 6 (deep-dive): juju 4.0, platform comparison

Same local charm on juju 4.0. Key difference: `container.replan()` does not raise `ChangeError` on Juju 4.0 when the service exits quickly (different pebble version). The charm sets `ActiveStatus` after replan, but the worker is in pebble `backoff` state. The pebble check takes ~60s (30–40s observed across runs) to detect the failure and transition to `BlockedStatus`.

## Observed behaviour

All observations below are from the locally packed charm with a working (although failing-to-connect) worker image, repeated across three separate deploy/test sessions on both Juju 3.6 and 4.0.

- **Deploy time**: ~2 min to active/blocked on juju 3.6. Image import into containerd was fast; pod startup ~30s.
- **Pebble plan construction**: Correct. All 50+ environment variables injected with both `TEMPORAL_*` and `TWC_*` prefixes. Both checks (`start-worker-check` via pgrep, `eviction-loop-check` via pebble log grep) properly configured. Verified via `juju ssh --container temporal-worker temporal-worker-k8s/0 pebble plan`.
- **Config validation**: `BlockedStatus` messages are clear and actionable:
  - `"config: invalid log level 'invalid'"` — tells the operator what's wrong
  - `"Invalid config: namespace value missing"` — names the missing key
  - `"Incorrectly formatted \`environment\` config: while parsing a flow mapping..."` — includes parse error details
  - `"Invalid config: sentry-sample-rate must be between 0 and 1"` — gives the valid range
  - `"Invalid config: oidc-project-id value missing"` — when `auth-provider=google` is set without OIDC config
  - `"temporal-host-info relation not established; set deprecated \`host\` config as fallback"` — offers the workaround
- **auth-secret-id crash**: Setting `auth-secret-id` to a non-existent secret crashes the charm to `error` state (`"hook failed: config-changed"`). Recovery is automatic on the next config-changed after clearing the bad value. **Confirmed on both juju 3.6 and 4.0, repeated across sessions.**
- **Vault actions**: `add-vault-secret` fails with `UnboundLocalError: cannot access local variable 'vault_client'`. `get-vault-secret` fails with `"Unable to initialize vault client. Remove relation and retry."` (different message, same root cause). **Confirmed on both juju 3.6 and 4.0, repeated across sessions.**
- **Restart action**: Fails with exit status 1 on both Juju versions because `container.restart()` raises `pebble.ChangeError`, which is not caught. **Additionally**: the action handler sets `MaintenanceStatus("restarting worker")` before calling `restart()`, and when `ChangeError` fires, the exception propagates before the status can be cleared — leaking a `maintenance` status observed to persist for over a minute, until the next hook fires.
- **ActiveStatus window while crash-looping — platform-dependent**: On juju 3.6, `container.replan()` raises `ChangeError`, which the charm catches and sets `BlockedStatus` immediately. On **juju 4.0**, `replan()` succeeds (service starts, exits, enters pebble `backoff`), the charm sets `ActiveStatus("worker listening to namespace ...")`, and it takes ~40–60s for the pebble check to fire and transition to `BlockedStatus("temporal-worker service is not running")`. Observed on both platforms; the delayed-transition window is specific to 4.0.
- **update-status cycle**: Runs `update_db_relation_data_in_state`, `_validate`, `_validate_pebble_plan`, then `_update` if the plan is invalid. With a blocked state and no database relation, this is wasted work every 5 minutes.
- **Memory**: Pod uses ~40 MB total (charm container + workload), 86m CPU (juju 3.6).
- **Scale up/down**: Works. New unit gets the same config, service, and pebble checks. Verified with `juju add-unit` and `juju scale-application`.
- **Service kill/recovery**: Killing the workload process (`pkill -f start-worker.sh`) causes pebble to restart it automatically (`startup: enabled`), cycling `backoff → active → backoff`. No charm-level involvement.
- **Database relation**: `TEMPORAL_DB_NAME` (from config `db-name`) is injected immediately. `TEMPORAL_DB_HOST`, `DB_PORT`, `DB_PASSWORD`, `DB_USER`, `DB_TLS` are absent until postgresql-k8s completes its credential handshake — which took >3 minutes and had not completed by the time the relation was removed in one session. The charm sets no `WaitingStatus` to indicate it is waiting for credentials.
- **Database relation removal**: Clean transition — no error state, no crash. The charm removes `DB_*` env vars from the pebble plan.
- **Observability integrations**: All three (metrics-endpoint, logging, grafana-dashboard) correctly publish data. Scrape jobs (`*:9000`) appear on the grafana-agent side, the logging endpoint is received, and the `temporal-monitoring` dashboard is shared.
- **Application removal**: Clean teardown observed; certs storage detached without error.

## Findings

### Vault actions use wrong container name — always fails `can_connect()`
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/vault/actions.py:99`
- **Evidence**: `container = self.charm.unit.get_container(self.charm.name)` — `self.charm.name` is the Juju application name `"temporal-worker-k8s"`, but the container defined in `metadata.yaml` is `"temporal-worker"`. The charm's own handlers correctly use `self._service_name = "temporal-worker"`. Confirmed at runtime across multiple sessions: `add-vault-secret` raises `UnboundLocalError` on both Juju 3.6 and 4.0.
- **Impact**: `add-vault-secret` and `get-vault-secret` are completely broken. `_validate_vault_relation()` raises `Exception("Failed to connect to the container")`, `event.fail()` is called but execution continues (no `return`), and the subsequent use of `vault_client` raises `UnboundLocalError`.
- **Fix**: Change `self.charm.name` to `"temporal-worker"` or `self.charm._service_name`.
- **Linter rule**: "action handler calls `unit.get_container()` with an argument that does not match any container name in `metadata.yaml`" — mechanically checkable.

### Vault action handlers continue execution after `event.fail()` — inconsistent behaviour
- **Severity**: high
- **Kind**: bug
- **Where**: `src/vault/actions.py:39-40,48-49` (`_on_add_vault_secret`); cf. `src/vault/actions.py:69-70,78-82` (`_on_get_vault_secret`)
- **Evidence**: In `_on_add_vault_secret`, `_validate_vault_relation()` failure calls `event.fail(str(e))` at line 40 but does **not** return — execution falls through to access `path`, `key`, `value` from params, then fails with `UnboundLocalError` at the `vault_client.write_secret()` call (line 53). In `_on_get_vault_secret`, the same failure calls `event.fail(str(e))` at line 71, again with no `return`, but a later `event.fail()` (line 82) does have a `return`, producing a clean error message. Confirmed at runtime: `add-vault-secret` → `UnboundLocalError`; `get-vault-secret` → `"Unable to initialize vault client. Remove relation and retry."`
- **Impact**: Operators get two different error messages for the same root cause. `add-vault-secret`'s `UnboundLocalError` is a raw Python traceback, not an actionable message.
- **Fix**: Add `return` after every `event.fail()` call that should terminate the handler — specifically after the `_validate_vault_relation()` failure and after the `get_vault_client()` failure in `_on_add_vault_secret`.
- **Linter rule**: "`event.fail()` not followed by `return` in action handler" — mechanically checkable.

### `get_auth_config_from_juju_secret` crashes to error state on missing/inaccessible secrets
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:252-253` (`secret_content["auth-provider"]` access around line 255)
- **Evidence**: `secret = self.model.get_secret(id=self.config.get("auth-secret-id"))` followed by `secret_content = secret.get_content(refresh=True)`. If the secret doesn't exist, `get_secret` raises `ModelError` (Juju 4.0) or `SecretNotFoundError`; if `auth-provider` is missing from the content, `secret_content["auth-provider"]` raises `KeyError`. The only exception handling is in `_update` (line 376), which catches `ValueError` — none of `ModelError`, `SecretNotFoundError`, or `KeyError` is a `ValueError`. Confirmed at runtime, repeatedly: setting `auth-secret-id=nonexistent` puts the charm in `error` state on both Juju 3.6 and 4.0.
- **Impact**: A misconfigured `auth-secret-id` crashes every `config-changed`, `pebble-ready`, `secret-changed`, and `update-status` event — putting the charm in unrecoverable `error` state instead of `BlockedStatus` with a clear message. Recovery only happens after clearing the value and waiting for the next hook.
- **Fix**: Wrap in try/except that catches `SecretNotFoundError`, `ModelError`, and `KeyError`, and re-raise as `ValueError` so the existing `except ValueError` in `_update` handles it cleanly.
- **Linter rule**: not mechanically checkable (requires knowing which ops exceptions `get_secret` can raise).

### Restart action does not handle `pebble.ChangeError`, and leaks `MaintenanceStatus`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:146-150`
- **Evidence**:
  1. Line 146: `self.unit.status = MaintenanceStatus("restarting worker")` — set before the restart attempt.
  2. Line 148: `container.restart(self._service_name)` — no try/except. When the service fails to restart, pebble raises `ChangeError`, which propagates uncaught.
  3. The status set at line 146 is never cleared — the exception unwinds past line 150 where `event.set_results(...)` would run, leaving `self.unit.status` at `MaintenanceStatus("restarting worker")`. Observed at runtime: status stuck in `maintenance` for over a minute until a `config-changed` fired.
- **Impact**: The action crashes with an uncaught `ChangeError` instead of a clean failure message, and the unit status is corrupted to `maintenance` until the next non-action hook runs.
- **Fix**: Wrap `container.restart()` in try/except `pebble.ChangeError`, call `event.fail()` with a diagnostic message, and restore the previous unit status (or set `BlockedStatus`) in the except block.
- **Linter rule**: not mechanically checkable (status leak).

### Misleading `ActiveStatus` window when service is crash-looping (~40–60s on Juju 4.0)
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:503-505`
- **Evidence**: `self.unit.status = ActiveStatus(...)` is set immediately after `container.replan()` returns. On Juju 3.6, `replan()` raises `ChangeError` when the service exits quickly, which is caught (line 501) and converted to `BlockedStatus`. On **Juju 4.0** (different pebble version), `replan()` succeeds — the service starts, exits with code 1, and enters pebble `backoff` state. The charm sets `ActiveStatus` while the worker is crash-looping; the pebble check (threshold 3, 30s period) takes ~40–60s to fire and transition to `BlockedStatus`. Observed on juju 4.0 across two sessions: `juju status` showed `active` while `pebble services` showed `backoff`.
- **Impact**: A 40–60 second window where operators and automation see `active` for a non-functional worker. Severity is higher on 4.0 because 3.6 fails fast via `ChangeError`.
- **Fix**: After `replan()`, inspect `container.get_service(self._service_name).current` to confirm the service is actually running before setting `ActiveStatus`. Alternatively, set `WaitingStatus` initially and let `pebble-check-recovered` set `ActiveStatus` when the pebble check passes.
- **Linter rule**: not mechanically checkable.

### Open issue #89: `vault-relation-broken` fails when restarting service without credentials
- **Severity**: medium
- **Kind**: bug (confirmed by open issue)
- **Where**: `src/charm.py:358` (`_update`), `src/relations/vault.py:61,67`
- **Evidence**: Open issue #89 reports that `vault-relation-broken` fails repeatedly because it attempts to restart the temporal-worker service after Vault credentials have been removed, causing the service to crash. `_on_vault_gone_away` calls `_update(event)`, which calls `create_env()` → `process_vault_variables()`; if `environment` config references vault secrets, resolution would fail.
- **Impact**: Removing the vault relation puts the charm in an error loop; confirmed by CI per the issue.
- **Fix**: On vault gone-away, either validate that no vault env vars are configured, or handle the missing vault client gracefully in `create_env()`.
- **Linter rule**: not mechanically checkable.

### No `WaitingStatus` while waiting for database credentials
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/relations/postgresql.py:33-49`, `src/charm.py:456-465,508-510`
- **Evidence**: After relating to postgresql-k8s, `TEMPORAL_DB_NAME` appears in the pebble plan immediately, but `DB_HOST`, `DB_PORT`, `DB_PASSWORD`, `DB_USER`, `DB_TLS` are absent until postgresql finishes its credential handshake — observed taking >3 minutes without completing. The existing `WaitingStatus` set in `_on_database_changed` (postgresql.py:46) is immediately overwritten by `_update`, which sets `ActiveStatus` (charm.py:508) or `BlockedStatus` (charm.py:387,418,503).
- **Impact**: An operator who relates to PostgreSQL sees `DB_NAME` in the plan but no connection parameters, with a status message unrelated to the database wait state.
- **Fix**: Set `WaitingStatus("waiting for database credentials")` when a database relation exists but `_state.database_connection` is not yet populated, and prevent `_update` from overwriting it with an unrelated status.
- **Linter rule**: not mechanically checkable.

### Blind `Exception` catches swallow real errors — 6 instances
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/vault/actions.py:39,48,70,79,86`, `src/relations/vault.py:77`
- **Evidence**: Multiple `except Exception` blocks — e.g. `src/vault/actions.py:48` catches any exception from `get_vault_client()` and fails the action with a generic message, discarding the real error (e.g. `FileNotFoundError` writing the CA cert). Ruff `BLE001` flags all 6 instances.
- **Impact**: Operators diagnosing vault issues get unhelpful error messages; the charm cannot distinguish transient errors from permanent misconfiguration.
- **Fix**: Catch specific exception types; log the full exception with `logging.exception()` before re-raising or failing.
- **Linter rule**: `BLE001` (blind `except Exception`) — ruff catches this. 43 total BLE001/TRY issues across charm-owned source (22 TRY003, 6 BLE001, 6 TRY400, 4 TRY002, 2 TRY300, 1 TRY401).

### `_on_update_status` calls `update_db_relation_data_in_state` without leadership guard, defers on `update-status`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:173`, `src/relations/postgresql.py:83`
- **Evidence**: `_on_update_status` calls `self.postgresql.update_db_relation_data_in_state(event)` unconditionally. Non-leader units return `False` immediately (line 78), so this is harmless there — but on the leader unit, if `_state.is_ready()` is False, the method calls `event.defer()` (line 83) on an `update-status` event. `update-status` is periodic, not queued — the defer is a no-op that logs a warning.
- **Impact**: Minor log noise on the leader unit when the peer relation isn't ready. No functional impact.
- **Fix**: Guard the call with `self.unit.is_leader()` in `_on_update_status`, or skip the defer path for non-deferrable events.
- **Linter rule**: "`event.defer()` called in `update-status` handler" — mechanically checkable.

### `_validate_pebble_plan` catches only `ConnectionError`, not other pebble exceptions
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:241-244`
- **Evidence**: `def _validate_pebble_plan(self, container): try: plan = container.get_plan().to_dict() ... except pebble.ConnectionError: return False`. `get_plan()` can also raise `FileNotFoundError` or `APIError`.
- **Impact**: An unexpected exception from `get_plan()` in the update-status path would crash the charm rather than falling through to `_update`.
- **Fix**: Check `container.can_connect()` first, or broaden the except clause to `(pebble.ConnectionError, pebble.APIError, FileNotFoundError)`.
- **Linter rule**: "hook handler calls `container.<method>()` without `can_connect()` guard" — mechanically checkable.

### `parse_environment` validates then reconstructs with `.get()` — structure mismatch risk
- **Severity**: low
- **Kind**: bug
- **Where**: `src/environment_processors.py:129,186-194`
- **Evidence**: `parse_environment` validates that required keys exist (e.g. `"name" in item and "value" in item`) but then reconstructs the parsed dict using `item.get("name")` and `item.get("value")`. If validation and reconstruction logic drift, missing keys would silently become `None`.
- **Impact**: A future change to validation logic that doesn't update reconstruction could introduce silent data corruption.
- **Fix**: Use direct key access (`item["name"]`) in reconstruction to fail fast on a missing key, or reuse the validated data rather than rebuilding it.
- **Linter rule**: not mechanically checkable.

### No `upgrade-charm` event handler
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py` (no `_on_upgrade_charm` method)
- **Evidence**: The charm does not observe `upgrade-charm`, relying on `config-changed`, `pebble-ready`, and relation events to reconfigure after an upgrade.
- **Impact**: On `juju refresh`, new charm code may deploy but the workload might not be reconfigured until the next hook fires (up to 5 minutes via update-status).
- **Fix**: Add an `upgrade-charm` handler that calls `_update(event)` to ensure reconfiguration on refresh.
- **Linter rule**: not mechanically checkable.

### Charm-level `ruff` issues: 43 errors in BLE001/TRY rule categories
- **Severity**: low
- **Kind**: lint
- **Where**: `src/` (all charm-owned code)
- **Evidence**: `ruff --select BLE001,TRY --no-cache src/` produces 43 errors: 6 `BLE001` (blind `except Exception`), 4 `TRY002` (bare `raise Exception`), 22 `TRY003` (inline message in raise), 6 `TRY400` (`logging.error` instead of `logging.exception`), 2 `TRY300`, 1 `TRY401`. All in charm-owned code, not vendored libraries.
- **Impact**: Blind exception catches hide real errors; bare `raise Exception` gives no type information; `logging.error` drops the traceback.
- **Fix**: Address incrementally — `BLE001` (specific types) first, then `TRY400` (exception logging), then `TRY002` (custom exceptions).
- **Linter rule**: all mechanically checkable via ruff.

### Config `log-level` description refers to "gunicorn"
- **Severity**: nit
- **Kind**: docs
- **Where**: `config.yaml:13`
- **Evidence**: `description: | Configures the log level of gunicorn.` — this charm runs a Temporal worker, not gunicorn.
- **Impact**: Copied from a template and never updated; confusing to operators reading Charmhub config docs.
- **Fix**: Change to "Configures the log level of the Temporal worker."
- **Linter rule**: not established.

### No `.gitignore`
- **Severity**: nit
- **Kind**: lint
- **Where**: repo root
- **Evidence**: The repo lacks a `.gitignore`. Build artifacts (`__pycache__`, `.venv`, `.tox`, `*.rock`, `*.charm`) could be accidentally committed.
- **Impact**: Risk of accidental commits of build artifacts.
- **Fix**: Add a standard Python `.gitignore`.
- **Linter rule**: not established.

## Worth copying

- **Scenario test coverage** (`tests/scenario/test_charm.py`, `tests/scenario/conftest.py`): 19 tests covering config validation, pebble plan construction, error handling (missing entrypoint, pebble `ChangeError`, invalid environment config), environment variable precedence (vault > juju > env), auth-secret override of environment auth keys, DB relation env injection, pebble check failure/recovery, and eviction-loop detection. Uses `ops.testing` (scenario) rather than `Harness`. The `_build_environment_config` and `_get_plan_environment` helpers keep test code DRY.
- **State pattern** (`src/state.py`): A clean JSON-encoding wrapper around peer relation data with `__getattr__`/`__setattr__`/`__delattr__`. Simple, well-tested, avoids the pitfalls of `StoredState`.
- **`environment_processors.py`**: Clean separation of three secret backends (env, juju, vault) with consistent error handling and YAML schema validation in `parse_environment()`. The reserved-prefix check (`TEMPORAL_`/`TWC_`) guards against accidental override.
- **Temporal worker info library** (`lib/charms/temporal_worker_k8s/v0/temporal_worker_info.py`): Well-designed custom event `TemporalWorkerInfoRelationReadyEvent` with snapshot/restore, proper leader-guarding in the provider, and `relation_payloads()` for multi-relation support.
- **Pebble eviction-loop check** (`src/charm.py:486-494`): Using `pebble logs -n 50 | grep "continually retrying eviction"` as a custom pebble check is a creative use of pebble's health-check framework for application-level monitoring.
- **Deprecation path for `host` config** (`src/charm.py:95-100,403-420`): Clean precedence logic (relation data wins, then deprecated config), with clear warning logs and a `BlockedStatus` when neither is available, including an actionable fallback message.
- **Integration tests that assert on behaviour** (`tests/integration/`): Deploy the full Temporal ecosystem, run workflows, and assert on results rather than only `wait_for_idle`. The `helpers.py` module provides reusable primitives (`run_sample_workflow`, `setup_temporal_ecosystem`, `add_juju_secret`).

## Common-practice notes

- **Drifts from convention**: The charm carries the old `TWC_*` prefix alongside `TEMPORAL_*` for backward compatibility, doubling the environment variable surface. 24 config options, many deprecated (`candid-*`, `oidc-*` fields) but not hidden with `hidden: true`, cluttering the config UI.
- **Follows convention**: `charmcraft.yaml` with the `uv` plugin, `ops==2.21.1`, `ops-scenario==7.21.1` for tests, `pyproject.toml` with `[project.optional-dependencies]` for test deps. Tox environments cover fmt, lint, unit, static, coverage-report, integration.
- **Library versioning**: Libraries under `lib/charms/` follow the `v0/` convention; `temporal_worker_info.py` uses a custom `LIBID` and proper snapshot/restore for events.
- **Terraform module**: Present and well-typed. Variables constrained, `main.tf` clean, outputs expose `provides`/`requires` maps. Missing a `temporal-worker-info` output (open issue #48); the `database` requirement is listed as `postgresql_client` (should be the interface name, not the relation name).
- **Charmhub description**: Published on 1.0/stable and 2.0/edge. The default `upstream-source` (`ubuntu/python:3.12-24.04_stable`) is not a working worker image (missing entrypoint) — the charm blocks on deploy until the operator provides a valid image. Arguably correct behaviour, but the README should be clearer about it.

## Tests

### Test results
All 23 tests pass in ~0.66–0.67s using `ops==2.21.1`, `ops-scenario==7.21.1`, `pytest==7.1.3`, `cosl==0.0.6`, `pytest-interface-tester==3.3.1`, `hvac==2.3.0`.

### Unit tests (`tests/unit/test_state.py`)
4 tests (State CRUD + `is_ready`). All pass. Minimal coverage; no edge cases (JSON encoding of non-serializable types, relation being `None` during `__getattr__`).

### Scenario tests (`tests/scenario/test_charm.py`)
19 tests. All pass. Coverage includes:
- Config validation (missing required, missing `db-name`, invalid environment YAML — three structure variants)
- Image validation (missing entrypoint, pebble `ChangeError`)
- Auth secret handling (invalid secret content, valid auth secret, auth secret override)
- Environment precedence (vault > juju > env for same key name)
- Juju secret override of charm config (issue #36 regression test)
- Pebble check failures and recovery (`start-worker-check`, `eviction-loop-check`)
- Database relation environment injection

### Scenario test gaps (untested branches)
- `temporal-host-info` relation: no test for host resolution, fallback to deprecated config, or blocked-when-neither
- Restart action: no test for the handler or its `ChangeError` path
- `secret-changed` hook: no test for triggering `_update`
- `_on_install`: no test for nonce secret creation
- `add-vault-secret` / `get-vault-secret` actions: no test for either handler
- Environment config with wrong `secret-id`: no test for secret-ID-not-found path
- `update-status` path: no test for the full flow (DB state check, pebble plan validation, re-update triggering)

### Integration tests (not run — require full Temporal ecosystem)
- `tests/integration/test_charm.py`: deploys Temporal ecosystem, runs a basic workflow, asserts on result
- `tests/integration/test_host_info.py`: relation precedence, fallback, removal/recovery
- `tests/integration/test_postgres_db.py`: DB relation, runs database workflow, asserts result
- `tests/integration/test_scaling.py`: scale-up/down, runs workflows after scaling
- `tests/integration/test_upgrades.py`: refresh from published edge to local build
- `tests/integration/test_vault.py`: deploys vault-k8s, unseals, authorizes, relates, writes secrets, runs vault workflow
- `tests/integration/test_worker_info.py`: deploys test requirer, verifies namespace/queue propagation
- **Gaps**: no test for the `logging` relation (Loki), no test for `metrics-endpoint`/`grafana-dashboard` beyond data-sharing, no test for `secret-changed` hook, no test for `restart` action

### Lint results
- `ruff --select BLE001,TRY`: 43 errors in charm-owned code (see findings above)
- `codespell`: one finding in vendored lib (`data_interfaces.py:612` "re-using" → "reusing"), zero in charm code

## Docs

- **README.md**: Comprehensive — deployment, config, auth, secrets, proxy, scaling, Sentry, observability, Vault, PostgreSQL. Missing a "Quick Start" that works end-to-end without external dependencies; deploy instructions assume a pre-built Temporal server and worker image.
- **CONTRIBUTING.md**: Covers tox environments and local deploy, references `charmcraft pack` and `make build_rock`. Base reference is stated as ubuntu@22.04, but the charm now uses ubuntu@24.04 — stale.
- **terraform/README.md**: Documents inputs/outputs with a good API table.
- **Charmhub description**: Published on 1.0/stable and 2.0/edge. The `upstream-source` `ubuntu/python:3.12-24.04_stable` is not a working image (missing entrypoint) — the charm should either provide a default functional image or make the resource requirement clearer.
- **`config.yaml:13`**: `log-level` description says "Configures the log level of gunicorn" — should say "Temporal worker".
- **Doc/reality mismatch**: The README's deploy instructions imply `juju config ... --file=path/to/config.yaml` will work standalone, but the charm blocks without either the `temporal-host-info` relation or the deprecated `host` config. The README explains this but the flow is still confusing for first-time operators.

## Open questions

1. **Why does the published 1.0/stable resource (rev 18) not contain `/app/scripts/start-worker.sh`?** The resource is 18.7 MB — likely the `ubuntu/python:3.12-24.04_stable` base image rather than a built rock. If intentional (operator provides their own image), the README and Charmhub description should say so more clearly; if not, the publish workflow may not be building/uploading the correct rock.
2. **Is the juju 4.0 storage volume-mount failure a charm bug or a Juju bug?** The `certs` storage caused a StatefulSet creation failure on juju 4.0 / k8s 1.32 with Charmhub rev 38. The locally packed charm on the same controller worked fine, suggesting a revision-specific or storage-class interaction issue rather than a blanket Juju 4.0 regression.
3. **Should the charm auto-detect when a valid worker image is provided?** Even after `juju attach-resource` with a valid image, the charm needs another hook (config-changed, update-status) to re-check. A `resource-changed` event observer could close this gap.
4. **Why does `container.replan()` behave differently between Juju 3.6 and 4.0?** On 3.6, `replan()` raises `ChangeError` when the service exits quickly; on 4.0 it does not — a pebble version difference. The charm should handle both behaviours consistently; the current behaviour gives operators on 4.0 a 40–60s `active` window for a non-functional worker.
