# temporal-k8s

A well-structured Kubernetes charm for Temporal server (v1.23.1), supporting PostgreSQL backends, OpenFGA authorization, S3 archival, frontend TLS, `nginx-route` ingress, and COS observability. Code quality is good (clean separation of concerns, scenario-based tests, pylint 10/10), but the charm has real correctness problems that would bite an operator on day one: the `restart` action is completely non-functional on every published revision, `db-tls-enabled` can fatally break a working deployment with a delayed, confusing failure, and `create-authorization-model` cannot actually be invoked with JSON. A maintainer should fix `restart` first (one-line fix, zero test coverage caught it), then address the `db-tls-enabled` state-update latency and its ability to crash the workload.

| | |
|---|---|
| Repo | canonical/temporal-k8s-operator @ 96fbca3 (2026-06-30) |
| Charms | temporal-k8s (primary), temporal-host-info-requirer (test only) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), 1.23/stable rev 68, refreshed to 1.23/edge rev 71 |
| Reviewed | 2026-07-25 |

## What it does

Deploys Temporal server (frontend, history, matching, worker services) on Kubernetes backed by PostgreSQL. Supports OpenFGA for fine-grained authorization, S3 archival, frontend TLS via `tls-certificates`, gRPC ingress via `nginx-route`, and COS observability (Prometheus metrics, Grafana dashboards, Loki log forwarding). Provides `temporal-host-info` to consumer charms. Exposes actions for managing authorization models and rules.

## Deployment log

### First deployment (1.23/stable rev 68, with TLS)

Deployed on `concierge-k8s-3` (Juju 3.6.25). `concierge-k8s-4` (Juju 4.0.5) could not be used because `postgresql-k8s` 14/stable rev 925 requires Juju < 4.0.0.

```
juju add-model rv-temp-2 --controller concierge-k8s-3
juju deploy postgresql-k8s --channel 14/stable --trust -n 1
juju deploy temporal-k8s --channel 1.23/stable --trust -n1
juju deploy temporal-admin-k8s --channel 1.23/stable --trust -n1
juju deploy self-signed-certificates --channel edge
juju integrate temporal-k8s:db postgresql-k8s:database
juju integrate temporal-k8s:visibility postgresql-k8s:database
juju integrate temporal-k8s:admin temporal-admin-k8s:admin
juju integrate temporal-k8s:frontend-certificates self-signed-certificates:certificates
juju config temporal-k8s num-history-shards=1
```

PostgreSQL took ~7 minutes to become active. Once the DB was ready, `temporal-admin-k8s` created the schema and `temporal-k8s` reached active at version 1.23.1 with TLS configured. Deploy-to-active: ~14 minutes.

### Second deployment (1.23/stable rev 68)

```
juju add-model rv-temp-3 --controller concierge-k8s-3
juju deploy postgresql-k8s --channel 14/stable --trust -n 1
juju deploy temporal-k8s --channel 1.23/stable --trust -n1
juju deploy temporal-admin-k8s --channel 1.23/stable --trust -n1
juju deploy self-signed-certificates --channel edge
juju deploy traefik-k8s --channel edge --trust
juju integrate temporal-k8s:db postgresql-k8s:database
juju integrate temporal-k8s:visibility postgresql-k8s:database
juju integrate temporal-k8s:admin temporal-admin-k8s:admin
juju integrate temporal-k8s:frontend-certificates self-signed-certificates:certificates
juju config temporal-k8s num-history-shards=1
```

Traefik was deployed but could not be integrated: it provides `ingress`/`traefik-route`, not the `nginx-route` interface temporal-k8s requires. Not a charm failure — an ecosystem mismatch (see issue #140).

### Refresh test

Refreshed 1.23/stable rev 68 → 1.23/edge rev 71 successfully. Pod was rescheduled (IP changed 10.1.0.231 → 10.1.0.4). Service recovered correctly.

## Observed behaviour

### Deploy and lifecycle

- **Charm size**: 35MB packed (`temporal-k8s_ubuntu@24.04-amd64.charm`)
- **Workload memory**: ~137MiB idle (`kubectl top pod`)
- **Pebble check**: `temporal operator cluster health --address=temporal-k8s:7236`, period 300s, threshold 3
- **Deploy-to-active**: ~14 minutes with TLS, ~12 minutes without
- **Refresh**: rev 68 → rev 71 succeeded, service recovered
- **Scale up/down**: 1 → 2 units worked; each unit got a unique `broadcastAddress` from `network.bind_address`. Scale back to 1 worked cleanly.

### TLS integration

TLS via `self-signed-certificates` configured correctly. Certificates/keys pushed to `/etc/temporal/temporal-frontend.pem` and `.key`. Rendered config (`/etc/temporal/config/charm.yaml`) showed correct `certFile`/`keyFile` under `global.tls.frontend.server`. Removing the TLS relation correctly deleted certificate files and removed TLS environment variables from the Pebble plan — a claim that stale TLS env vars persist across hooks was checked and found incorrect: `_extra_context` is reset per hook process (fresh charm process each invocation), so no staleness occurs.

### Config changes

- `juju config temporal-k8s log-level=debug` → replan, 3-minute recovery
- `juju config temporal-k8s log-level=INVALID` → `BlockedStatus("config: invalid log level 'invalid'")`
- `juju config temporal-k8s services=foobar` → `BlockedStatus("error in services config: invalid service 'foobar'")`
- `juju config temporal-k8s db-tls-enabled=true` → **breaks deployment** (see finding below)
- `juju config temporal-k8s db-tls-enabled=false` → recovery requires a further config-changed + update-status cycle to fully heal

### `db-tls-enabled` failure sequence (observed in detail)

1. `db-tls-enabled=true` set via `juju config`. Config-changed fires but does NOT call `update_db_relation_data_in_state`, so state retains `tls: false`. Pebble layer rebuilt without TLS — no apparent change.
2. Next `update-status` fires (~5 minutes later, or forced). `update_db_relation_data_in_state` runs, computes `tls: true` from config, returns `should_update=True`.
3. `_update()` rebuilds pebble layer with `SQL_TLS_ENABLED: "true"`. Temporal tries to connect to PostgreSQL over SSL.
4. Service crashes: `pq: SSL is not enabled on the server`. Pebble enters backoff restart loop.
5. Unit goes to `error` because `update-status` raises `ChangeError` when replan fails.

### Actions — all tested

- **restart**: **FAILED** on both rev 68 and rev 71 with `cannot start services: service "temporal" does not exist`. `container.restart(self.name)` uses `self.name = "temporal"`, but the Pebble service is `"temporal-server"`. 100% reproducible.
- **create-authorization-model**: two failure modes. (a) Any JSON value causes `json: unsupported type: map[interface{}]interface{}` from the Juju CLI before the charm receives the action — the `string`-typed `model` parameter doesn't compose with JSON in the Juju 3.6 CLI. (b) A plain string like `model=test` passes CLI parsing but fails the charm's `json.loads()` with "failed to parse model json" — correctly caught. Without an OpenFGA relation, even a valid JSON string would fail with "missing openfga relation".
- **add-auth-rule**, **remove-auth-rule**, **list-auth-rule**, **check-auth-rule**: all correctly return `"missing openfga relation"`.
- **list-system-admins**: correctly returns `"missing openfga relation"`.

### Failure injections

- **Remove db relation**: `BlockedStatus("db:pgsql relation: no database connection available")` immediately. Re-integrating recovers to `MaintenanceStatus("replanning application")` then `active` within ~3 minutes.
- **Remove admin relation**: `MaintenanceStatus("restarting temporal")` briefly (misleading — it's replanning, not restarting), recovers to `active` within ~30 seconds; temporal-server keeps running throughout.
- **Kill workload process** (`pkill -9 temporal-server`): Pebble auto-restarts within seconds; Juju status stays `active` throughout; `pebble services` shows the service active again within 5 seconds.
- **Delete pod** (`kubectl delete pod temporal-k8s-0`): pod recreated with new IP within 13 seconds. Charm runs config-changed, rebuilds pebble layer, service starts. Unit sits in `MaintenanceStatus("replanning application")` until the next update-status (~5 minutes).

### Status management

Every `_update()` call ends with `MaintenanceStatus("replanning application")`; only the periodic `_on_update_status` (default 5 min) sets `ActiveStatus`. Observed repeatedly after config changes, relation changes, refresh, pod restart, and scaling — unit shows "maintenance" for up to 5 minutes after the service is actually healthy.

The failed `restart` action sets `MaintenanceStatus("restarting temporal")` *before* attempting the restart, so on failure the unit is left with a misleading "restarting temporal" message until the next update-status.

### Resource usage and perf

- Any config change rebuilds the entire Pebble layer and restarts the (heavyweight, multi-service) Temporal server — no diff-based check.
- Plaintext database passwords visible in the Pebble plan environment and `/etc/temporal/config/charm.yaml`.
- Pydantic deprecation warnings on every hook from `tls_certificates_interface/v4/tls_certificates.py` and `openfga_k8s/v1/openfga.py`.

## Findings

### `restart` action uses wrong service name — always fails
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:362-363` (also `src/charm.py:127`, `src/charm.py:686`)
- **Evidence**: `container.restart(self.name)` where `self.name = "temporal"` (`src/charm.py:127`); the Pebble service is `"temporal-server"` (`src/charm.py:686`). Observed on rev 68 and rev 71: `juju run temporal-k8s/0 restart` fails with `cannot start services: service "temporal" does not exist`. 100% reproducible.
- **Impact**: The only operator-accessible restart mechanism is completely non-functional across all published revisions.
- **Fix**: Change the call to `container.restart("temporal-server")`.
- **Linter rule**: Pebble layer service name must match the name used in `container.restart()`/`container.stop()` calls — not generally mechanically checkable, but could be verified against the static pebble layer definition; a unit test on the restart action would also have caught it.

### `create-authorization-model` action is unusable with JSON — CLI parsing failure
- **Severity**: high
- **Kind**: bug
- **Where**: `actions.yaml` (`model` parameter), `src/relations/openfga.py:159-160`
- **Evidence**: Any JSON value for `model` causes `json: unsupported type: map[interface{}]interface{}` from the Juju 3.6 CLI before the charm receives the action. A plain string passes through but is rejected by `json.loads()` with "failed to parse model json". Without an OpenFGA relation, the action correctly returns "missing openfga relation", but the JSON parameter cannot be delivered to the handler at all.
- **Impact**: `create-authorization-model` is the entry point for setting up OpenFGA authorization and cannot be invoked with structured data via the tested CLI.
- **Fix**: Change `model` to accept a file path and read file contents in the handler, or accept an explicitly base64-encoded string. Behaviour on the Juju 4 CLI is unverified.
- **Linter rule**: Action parameters intended to carry JSON must be exercised in integration tests against the target Juju CLI version — mechanically checkable via integration tests.

### `db-tls-enabled` config change does not take effect until an unrelated event fires
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:493` (`_validate()` reads stale `database_connections` state), `src/relations/postgresql.py:78` (`update_db_relation_data_in_state`, not called from `_on_config_changed`)
- **Evidence**: `update_db_relation_data_in_state` (which computes `tls` from config) is only called from DB relation events and `_on_update_status`, not from `_on_config_changed`. Observed: after `juju config temporal-k8s db-tls-enabled=true`, `kubectl exec` showed `SQL_TLS_ENABLED: "false"` still in the pebble plan; the change only took effect (and then broke the deployment) at the next update-status.
- **Impact**: The config change appears to have no effect, then the service crashes minutes later with no correlated user action — hard to troubleshoot.
- **Fix**: Call `self.postgresql.update_db_relation_data_in_state(event)` from `_on_config_changed` before `_update()`.
- **Linter rule**: Config changes affecting database connection parameters must trigger state recomputation — not mechanically checkable.

### `db-tls-enabled=true` breaks deployment on PostgreSQL without TLS
- **Severity**: high
- **Kind**: bug
- **Where**: `src/relations/postgresql.py:123`
- **Evidence**: `"tls": relation_data.get("tls") == "True" or self.charm.config["db-tls-enabled"]`. Setting `db-tls-enabled=true` forces `SQL_TLS_ENABLED: "true"` regardless of whether PostgreSQL has TLS. Observed: service crashes with `pq: SSL is not enabled on the server`, enters backoff loop, unit goes to `error`. Matches open issue #66 (since 2025-06-30).
- **Impact**: An operator toggling this config option (or upgrading from an older deployment) can fatally break Temporal with a single command. The option is documented as deprecated but still functional.
- **Fix**: Remove `db-tls-enabled` entirely, as recommended in issue #66.
- **Linter rule**: Deprecated config options should emit a deprecation warning when set — checkable if config metadata carries a deprecated flag.

### Unguarded `relations[0]` access in PostgreSQL handler risks `IndexError`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/relations/postgresql.py:101, 104`
- **Evidence**: `relation_id = self.charm.db.relations[0].id` and `relation_id = self.charm.visibility.relations[0].id`. The prior check (`src/relations/postgresql.py:98`) tests the Juju model's relation object, not `DatabaseRequires.relations`, which additionally filters on relation-data availability (`_is_relation_active`). There is a window where the model relation exists but `DatabaseRequires.relations` is empty. Not observed to trigger during testing, but the code path is unguarded (unverified in practice).
- **Impact**: If triggered, an uncaught `IndexError` in `update_db_relation_data_in_state` would fail the hook (from `_on_update_status` or a DB relation event) and put the unit in error state.
- **Fix**: Check `len(self.charm.db.relations) > 0` (and same for `visibility`) before indexing, or catch `IndexError` and return `False`.
- **Linter rule**: List indexing into dynamically-populated relation lists must be guarded — mechanically checkable via a static rule targeting `relations[0]` on `DatabaseRequires` objects.

### Unit stays in maintenance for up to 5 minutes after replan
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:707-709`
- **Evidence**: `_update()` ends with `self.unit.status = MaintenanceStatus("replanning application")`; only `_on_update_status` (default 5 min) sets `ActiveStatus`. Observed repeatedly after config changes, relation changes, refresh, pod restarts, and scaling.
- **Impact**: Operators see "maintenance" long after the service is actually healthy, causing false alarms and delaying automation that waits on active/idle.
- **Fix**: Call `self.set_active_unit_status()` after `container.replan()` in `_update()`, or use Pebble's change-wait to confirm the service is running before reporting active.
- **Linter rule**: not established.

### `_on_update_status` swallows `ValueError` silently — can report `active` when degraded
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:374-377`
- **Evidence**: `try: self._validate(); except ValueError: return`. If validation fails between update-status intervals, the method returns without setting status — the unit retains whatever status it previously had, potentially `active` while degraded. Matches issue #134.
- **Impact**: Unit can misleadingly report `active` while `_validate()` is failing, confusing operators and monitoring.
- **Fix**: Set `BlockedStatus` with the error message in the except block, or at minimum trigger a status re-evaluation.
- **Linter rule**: not established.

### `_on_update_status` can fail uncaught when Pebble replan fails
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:377-381`
- **Evidence**: When `update_db_relation_data_in_state` returns `should_update=True`, `_update()` is called directly. If replan fails (service can't start), the `ChangeError` propagates uncaught and the update-status hook fails, putting the unit into error. Observed during `db-tls-enabled` testing: the forced TLS change caused a crash, and the subsequent update-status replan attempt put the unit into error.
- **Impact**: During degraded states, update-status hooks can fail and leave the unit in error, blocking automatic recovery.
- **Fix**: Wrap the `self._update(event)` call at `src/charm.py:380` in try/except, or make `_update()` handle replan failures by setting `BlockedStatus`.
- **Linter rule**: not established.

### `logrotate` binary missing from container
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:427` (call), `src/charm.py:661` (config push)
- **Evidence**: The charm pushes logrotate config to `/etc/logrotate.d/temporal-server` and runs `logrotate` on every update-status; the binary is not present in the temporal container. The resulting error is caught and suppressed, so rotation silently never happens; `/var/log/temporal/server.log` grows unbounded.
- **Impact**: Unbounded log growth can fill container disk and cause cascading failures in production.
- **Fix**: Add `logrotate` to the temporal-server rock image, or rely solely on Pebble's log forwarding to Loki (already configured via `LogProxyConsumer`).
- **Linter rule**: not established.

### `_on_restart_action` sets `MaintenanceStatus` before restart — misleading status on failure
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:359-361`
- **Evidence**: `self.unit.status = MaintenanceStatus("restarting temporal")` is set before `container.restart(self.name)`. When the restart raises `APIError` (wrong service name), the unit is left showing "restarting temporal" despite no restart happening. Observed: status persisted 5+ minutes until the next update-status.
- **Impact**: Misleads the operator into believing a restart occurred.
- **Fix**: Move the status update after the restart call succeeds, or set an explicit failure status in an except block.
- **Linter rule**: not established.

### Dead code: `_check_and_update_certificate` never called
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:763-784`
- **Evidence**: Defined but never referenced elsewhere (confirmed via `grep -rn`). Actual TLS handling uses `_update_certificates_required` from `_handle_frontend_tls`. Appears to be a superseded implementation.
- **Impact**: Dead code confuses maintainers and suggests an incomplete refactor.
- **Fix**: Remove the method and its helpers.
- **Linter rule**: Unused method — detectable with `vulture` or `ruff` (F811-class checks).

### `_validate` has an off-by-one in the `global-rps-limit` check, plus a typo
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:481`
- **Evidence**: `if self.config["global-rps-limit"] < 0:` with message "must be grater than 0" — a value of `0` passes validation despite the message implying it shouldn't. Typo: "grater" → "greater".
- **Impact**: Behaviour inconsistent with the stated constraint; typos in user-facing errors reduce operator confidence.
- **Fix**: Change the comparison to `<= 0` and correct the typo.
- **Linter rule**: `codespell` catches the typo; the off-by-one requires semantic review.

### Plaintext database passwords in Pebble plan and config files
- **Severity**: medium (known design choice)
- **Kind**: ux
- **Where**: `src/charm.py:690` (pebble layer environment), `src/charm.py:664` (config push), `templates/config.jinja`
- **Evidence**: Database passwords are written in plaintext to the Pebble layer environment and `/etc/temporal/config/charm.yaml`; confirmed via `kubectl exec -- pebble plan` and reading the rendered config file.
- **Impact**: Anyone with `kubectl exec` access can read database credentials. Likely an accepted design tradeoff, but undocumented.
- **Fix**: Document in security docs; consider Juju secrets for the Pebble layer environment.
- **Linter rule**: not established.

### Trivial config change triggers full service restart
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:686-706`
- **Evidence**: The Pebble layer `environment` dict includes all config-derived values; any config change alters the layer and forces `container.replan()`, restarting the heavyweight temporal-server process.
- **Impact**: Frequent config tuning causes repeated, unnecessary restarts of a multi-service process.
- **Fix**: Diff the computed layer against the current one in `_update()` and only replan if material values changed.
- **Linter rule**: not established.

### No explicit `upgrade-charm` handler
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/charm.py` (handler absent)
- **Evidence**: No `upgrade_charm` event handler; `upgrade_charm` is only observed by the TLS certificates library as a refresh trigger. The charm relies on `config-changed` firing after refresh. This worked for the tested rev 68 → rev 71 refresh, but there is no explicit path for version-compatibility validation.
- **Impact**: A direct upgrade skipping several minor versions (e.g. 1.23 → 1.31) is known to fail per issue #150; an explicit handler could catch this earlier.
- **Fix**: Add an `_on_upgrade_charm` handler that validates the upgrade path.
- **Linter rule**: not established.

## Worth copying

- **Scenario-based testing with `ops.testing`**: `tests/scenario/` uses custom markers (`@pytest.mark.peer_relation_skipped`, etc.) and a `parametrize_skip_if` filter for leader/non-leader cases. Tests verify exact Pebble plan contents, not just status strings.
- **Clear separation of concerns**: relations (`admin.py`, `postgresql.py`, `openfga.py`, `s3_archival.py`, `ui.py`) isolated in `src/relations/` with their own handlers; `State` class provides a clean abstraction over peer-relation storage.
- **Comprehensive validation**: `_validate()` checks config, relations, and state holistically before any workload operation, producing actionable `BlockedStatus` messages.
- **Real Pebble health check**: uses `temporal operator cluster health`, verifying actual cluster health rather than mere process liveness.
- **`log_event_handler` decorator**: clean, consistent logging of event handler entry/exit.
- **Documentation**: extensive `documentation/` directory (tutorial, how-to, explanation, reference), linked from Charmhub.
- **`uv` for dependency management**: `tox-uv` and `uv.lock` — ahead of many charms still on pip/requirements.txt.

## Common-practice notes

- **Follows** the Canonical k8s charm layout: `lib/charms/` for external libraries, `src/` for charm code, `templates/` for Jinja2 rendering.
- **Uses `ops.testing` (scenario)** over `Harness` — ahead of many charms — but integration tests still use `pytest-operator` (python-libjuju), flagged for deprecation in issue #148.
- **`State` class backed by peer relation**: common pattern of JSON-serialising state into peer relation app data, with known caveats (issue #57: hook re-invocation loops, data duplication), mitigated here with a single `_update()` reconciler.
- **Drift from convention**: uses `require_nginx_route()` with an open issue (#140) to support the generic `ingress` interface; could not integrate with `traefik-k8s` during testing because of this.
- **Interface ambiguity**: `peer`, `admin`, and `ui` relations all use the same `temporal` interface name, creating ambiguous integration scenarios (issue #120).
- **No upgrade-charm handler**: unlike many k8s charms, relies entirely on the `config-changed` flow after refresh.

## Tests

### Test structure
- **Unit/scenario**: `tests/scenario/test_charm.py` — 53 passed, 14 skipped, coverage 59%
- **Unit/scenario**: `tests/scenario/test_openfga_actions.py` — 3 tests, input validation for `list-auth-rule`
- **Unit (legacy)**: `tests/unit/` — `test_state.py`, `test_host_info.py`, `test_log_config.py`
- **Integration**: `tests/integration/` — `test_charm.py`, `test_auth.py`, `test_host_info.py`, `test_pgbouncer.py`, `test_scaling.py`, `test_server_upgrade.py`, `test_upgrades.py`
- **Static**: `tox -e static` (bandit) — 0 issues; `tox -e lint` — all checks pass, pylint 10.00/10

### Test run results
```
$ tox -e unit
53 passed, 14 skipped, 173 warnings in 4.21s
Coverage: 59% (charm.py: 76%, openfga.py: 30%, postgresql.py: 59%)
$ tox -e lint
All passes. pylint: 10.00/10
$ tox -e static
0 issues (High: 0, Medium: 0, Low: 0)
```

### Coverage gaps
- `src/relations/openfga.py` at 30% — async OpenFGA client code, action handlers, API call logic largely untested; the 3 scenario tests only cover `list-auth-rule` input validation.
- `src/relations/postgresql.py` at 59% — `_on_database_relation_broken` and the `relations[0]` indexing path not covered.
- `src/charm.py` at 76%:
  - `_on_restart_action` (`src/charm.py:353-365`) **not tested at all** — the service-name bug would have been caught by a basic test.
  - TLS certificate management methods (`src/charm.py:728-863`) partially untested — `_store_certificate`, `_delete_certificate`, `_get_stored_certificate` not exercised.
  - `_handle_frontend_tls` partially tested but not with real certificate data in the container.
- `create-authorization-model` **not tested** for a usable parameter format in any test file.
- Integration tests do not cover the TLS relation lifecycle (add/remove `frontend-certificates`).
- Integration tests use `pytest-operator` (python-libjuju), not `jubilant` — tracked as tech debt in issue #148.
- No test for the unguarded `relations[0]` access in `update_db_relation_data_in_state`.

## Docs

### Documentation quality
- **Comprehensive**: 20 documentation files covering tutorial, how-to, explanation (architecture), and reference (security). Tutorial walks through full deployment.
- **Tutorial accuracy**: references `latest/stable` and revision 43, outdated versus current 1.23/stable rev 68. Uses the deprecated `juju status --watch 1s` syntax.
- **Terraform module**: present with README, justfile, and CI workflow.
- **Charmhub page**: links to Discourse and GitHub; description is accurate.
- **`config.yaml` descriptions**: well-documented with examples. `db-tls-enabled` says "(Deprecated as of postgresql-k8s revision 462)" but does not warn that setting it to `true` can break deployments.

### Doc/reality mismatches
- Tutorial says to deploy with `--config num-history-shards=4` but omits the required `db`/`visibility`/`admin` integrations.
- `external-hostname` config description ("Will default to the name of the deployed application") — confirmed correct.
- Security docs don't mention that DB passwords are stored in plaintext in config files and the Pebble plan.
- `create-authorization-model` action docs say it "creates the authorization model using the content of the specified file", but the parameter is a JSON string, not a file — and is unusable with JSON under Juju 3.6.

## Open questions

1. Does the `temporal-host-info` relation work correctly end-to-end? Library code looks correct but was not tested with a requirer charm.
2. Would OpenFGA authorization work end-to-end? Not tested — no OpenFGA deployed, so the related actions are untestable without it; integration tests exist but were not run.
3. Does scaling with multiple units survive loss of the leader unit? Not tested; peer relation state is app-scoped and shared across units.
4. How does the charm behave on Juju 4? Could not deploy the full stack because `postgresql-k8s` 14/stable doesn't support Juju 4 (issue #116); the charm itself may work but this is untested.
5. Does the `relations[0]` `IndexError` actually occur in practice? Hard to reproduce — requires a specific timing window. A targeted test injecting an empty `DatabaseRequires.relations` list would settle it.
