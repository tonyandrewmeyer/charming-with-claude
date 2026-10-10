# canonical-cla

A k8s charm wrapping the Canonical CLA API service (FastAPI + PostgreSQL + Redis). It requires seven Juju secrets plus postgresql-k8s and redis-k8s relations before it reports Active. The codebase is a single-template commit with no meaningful history, and its test suite does not run at all. The charm reaches Active and survives relation churn, scaling, and process failure correctly, but ships with three critical correctness bugs that make both of its documented actions permanently non-functional, a key relation-vs-secret contract that's silently broken, and zero passing tests. A maintainer's first move should be fixing the `container.exec()` environment serialization bug (kills both actions), then the uppercase/lowercase key mismatch that makes the "database secret overrides the relation" promise false, then getting the test suite importing again.

| | |
|---|---|
| Repo | canonical/charmed-canonical-cla @ 5f24ee5 (2026-05-22) |
| Charms | canonical-cla |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), charmhub rev 190 (channel edge) |
| Reviewed | 2026-08-24 |

## What it does

Deploys the Canonical CLA API service as a k8s workload. The service is a FastAPI application with PostgreSQL (primary data store) and Redis (caching). The charm:
- Manages Pebble layers with uvicorn (4 workers) and dual health checks (READY + ALIVE)
- Integrates with postgresql-k8s, redis-k8s, nginx-ingress-integrator, Loki (logging), Prometheus (metrics), Grafana (dashboards)
- Exposes `migrate-db` and `audit-logs` Juju actions
- Supports maintenance mode via config

## Deployment log

**Phase 1 deployment (concierge-k8s-3, Juju 3.6.25)**
```
juju deploy canonical-cla --channel edge --revision 190
juju deploy postgresql-k8s
juju deploy redis-k8s --channel edge
juju deploy nginx-ingress-integrator
juju deploy grafana-agent-k8s --channel edge
juju deploy loki-k8s --channel edge
juju integrate postgresql-k8s:database canonical-cla:database
juju integrate redis-k8s:redis canonical-cla:redis
# Plus 7 Juju secrets (secret_key, internal_api_secret, github_oauth,
#  github, canonical_oidc, smtp, database) with correct key structure
# Plus config: app_url, sentry_dsn=""
```
Time from deploy to Active: ~4 minutes. Resource use: 8m CPU, 387Mi RAM per unit.

**Phase 2 (additional tests, same model rv-cla-k8s3, 2026-08-24)**
- Removed nginx-route relation → charm stayed Active (optional relation, confirmed) ✓
- Ran `migrate-db` action → FAILED with `cannot unmarshal bool` error ✓
- Ran `audit-logs` action → FAILED with identical error ✓
- Scaled from 1 to 3 units → all reached Active in ~1 min ✓
- Scaled back to 1 unit via `juju scale-application canonical-cla 1` ✓
- Created secret with wrong key structure → BlockedStatus with pydantic error ✓
- Restored correct secret → Active ✓
- Deployed self-signed-certificates → no relation possible (charm has no `tls-certificates` interface)

**Not tested:**
- `juju refresh` (no newer charmhub revision available)
- Juju 4.x substrate (postgresql-k8s not compatible with Juju 4.x in this environment)

## Observed behaviour

- **Status precedence** is well-ordered: config validation → Pebble readiness → postgres blocked → postgres data → redis relation → redis data → service running → Active.
- **Relation removal (redis)**: `juju remove-relation canonical-cla:redis redis-k8s:redis` → `BlockedStatus("Waiting relation to redis,  run 'juju relate redis-k8s:redis canonical-cla:redis'")`. Restoring the relation returns to Active within ~15 seconds. ✓
- **Relation removal (database)**: same pattern, correct BlockedStatus with actionable message. ✓
- **nginx-route removal**: `juju remove-relation nginx-ingress-integrator canonical-cla` → charm stays Active. The nginx-route relation is optional.
- **Config changes**: `app_url` change fires `config-changed`, compares Pebble layer diffs, restarts only on actual changes.
- **`app_url="not-a-valid-url"`**: accepted without URL validation. No regex or URL scheme check.
- **`migrate-db` action**: fails consistently. `juju run canonical-cla/0 migrate-db` returns `"cannot decode request body: json: cannot unmarshal bool into Go struct field execPayload.environment of type string"`. Verified with three independent runs across two phases.
- **`audit-logs` action**: fails with the identical error. Additionally, even if Pebble accepted the environment, the action would return the Python string representation of an `ExecProcess` object (not the log output) because `.wait_output()` is never called.
- **Scale up (1→3)**: units briefly in "Waiting for database relation" / "Waiting for Pebble", all Active within ~1 minute.
- **Scale down**: `juju scale-application canonical-cla 1` removes extra pods; unit 0 stays Active.
- **Bad secret (wrong key structure)**: `BlockedStatus("Config values are not valid: Error fetching secrets: 1 validation error for Secret\nsecret_key\n  field required")` — clear and actionable on Juju 3.x. On Juju 4.x the same failure surfaced as a raw 13-error pydantic dump (unverified whether this is a Juju version difference or environment-specific).
- **No TLS relation support**: charm has no `tls-certificates` interface. Cannot integrate with self-signed-certificates or any TLS provider.
- **Pebble layer confirmed with env vars**: `pebble plan` shows all 7 secrets' env vars plus database relation data, redis data, proxy vars, and `MAINTENANCE_MODE: "false"` (string — correct for the Pebble layer).
- **`app_environment` works correctly for the Pebble layer** but fails for `container.exec()` because ops JSON-serializes the Python bool `False` to a JSON boolean `false` instead of the string `"false"`.
- **Loki relation**: `ERROR Loki push api not available` appears in the unit log on every `_pebble_layer` access (i.e. every config-changed hook), not just when Loki is unrelated. When Loki is actually related, log targets appear in the Pebble layer only after a subsequent, unrelated event forces `_update_layer_and_restart`.
- **Grafana dashboards**: `Invalid Grafana dashboards folder at .../src/grafana_dashboards: directory does not exist` on every config-changed hook. `juju show-unit grafana-agent-k8s/0` confirms `dashboards: '{"templates": {}, "uuid": "..."}'` — empty templates, no actual dashboards.
- **Metrics (Prometheus)**: `juju show-unit grafana-agent-k8s/0` confirms `scrape_jobs` and `scrape_metadata` are present on the metrics-endpoint relation. `application-data: {}` on the canonical-cla/0 side is the charm's view of data written by the consumer, not the data it itself writes — metrics are correctly propagated. (An earlier draft of this review misread this as a bug; it is not.)
- **Pebble restart recovery**: killing the main uvicorn process (PID 734/595) — Pebble detected the failure and restarted the service within seconds; Juju stayed Active throughout for a transient failure.
- **Pebble backoff not surfaced**: separately, killing the main process left orphaned worker processes serving traffic while Pebble entered backoff (`address already in use`); Juju stayed Active because health checks kept passing against the orphaned workers. See finding below.
- **Ruff linting**: 18 errors including unused imports, f-strings without placeholders, missing docstrings, docstring formatting.
- **Unit tests**: completely broken — `ImportError: cannot import name 'CanonicalCla2Charm' from 'charm'` (actual charm class is `FastAPICharm`).

## Findings

### `migrate-db` and `audit-logs` actions always fail (boolean env var sent to Pebble)

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/utils.py:17` (`map_config_to_env_vars`), used from `src/charm.py:177,211`
- **Evidence**: `map_config_to_env_vars` maps non-secret config values directly to env vars: `{k.replace("-", "_").upper(): v for k, v in charm.config.items() if not str(v).startswith("secret:")}`. For `maintenance_mode=false` this produces `MAINTENANCE_MODE: False` (Python bool) inside `app_environment`. `container.exec(environment=self.app_environment)` JSON-serializes that dict; Python `False` becomes a JSON boolean, but Pebble's Go server types `execPayload.environment` as `map[string]string` and rejects it. The Pebble *layer* itself is fine (`pebble plan` shows `MAINTENANCE_MODE: "false"` as a YAML string), because the layer path uses YAML, not JSON. Confirmed with three independent action runs: `"cannot decode request body: json: cannot unmarshal bool into Go struct field execPayload.environment of type string"`.
- **Impact**: both documented actions are completely non-functional. Database migrations cannot be run through the charm, and audit logs cannot be retrieved.
- **Fix**: in `map_config_to_env_vars`, stringify all values: `{k.replace("-", "_").upper(): str(v) for k, v in charm.config.items() if not str(v).startswith("secret:")}`.
- **Linter rule**: dict passed to `container.exec(environment=...)` must contain only `str` values — mechanically checkable with a typeguard or static analysis.

### Database secret/relation key-case mismatch breaks the "override" contract

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:362–365` (`postgres_relation_blocked`), `src/charm.py:380–399` (`fetch_postgres_relation_data`)
- **Evidence**: `utils.fetch_secrets(self)` returns uppercase keys (`{"DB_HOST": ..., ...}`, see `src/utils.py:47`), but both methods check `secrets.get("db_host")` (lowercase), which is always `None`. Confirmed at runtime: with a correctly configured `database` secret but no relation, the charm blocked with "Waiting relation to database"; only integrating `postgresql-k8s:database` reached Active.
- **Impact**: the `database` secret is documented as overriding the database relation, but the code makes the relation mandatory regardless of the secret.
- **Fix**: change the lookups to uppercase (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`) in both methods.
- **Linter rule**: keys returned by `fetch_secrets()` must match the case used at call sites — mechanically checkable by cross-referencing the return type against usages.

### `audit-logs` action never reads command output

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:212–213`
- **Evidence**: `_on_audit_logs_action` calls `logs = self.container.exec(...)` and passes the resulting `ExecProcess` object straight to `event.set_results({"logs": logs})` without ever calling `.wait_output()`. The action reports success but `logs` contains the Python `repr()` of an `ExecProcess`, not real output.
- **Impact**: even once the boolean-serialization bug is fixed, `audit-logs` returns garbage instead of log content.
- **Fix**: `(stdout, stderr) = self.container.exec(cmd, environment=self.app_environment, combine_stderr=True).wait_output()`, then `event.set_results({"logs": stdout})`.
- **Linter rule**: result dict values must not contain `ExecProcess` objects; `container.exec()` must be followed by `.wait_output()` or `.wait()` — mechanically checkable.

### Pebble backoff state invisible to Juju (orphaned worker processes)

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:93–102` (`_on_collect_status`)
- **Evidence**: killing the main uvicorn process left 4 orphaned multiprocessing workers still serving on port 8000 while Pebble entered `backoff` (`"cannot start service: address already in use"`). `_on_collect_status` relies on `status.is_running()`, which checks Pebble health checks; since the orphaned workers kept those passing, Juju stayed Active throughout. Recovery required manually killing the orphaned processes.
- **Impact**: a failed Pebble service restart is invisible to the operator — the charm reports Active while the workload is stuck in a backoff loop.
- **Fix**: in `_on_collect_status`, also check `self.container.get_service("app").current` and surface non-`"active"` states as `MaintenanceStatus`, or add an explicit health check on the actual service process.
- **Linter rule**: not mechanically checkable without knowing the service architecture.

### Loki relation changes do not update Pebble log targets

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:56` (`self._logging = LokiPushApiConsumer(...)`); no observer registered for logging relation changes
- **Evidence**: after relating Loki, `pebble plan` showed no `log-targets` section. `LokiPushApiConsumer` internally tracks `loki_endpoints`, but the charm never calls `_update_layer_and_restart` on the logging relation event. Only after a subsequent, unrelated config change did `_update_layer_and_restart` fire and `log-targets: loki-0: {...}` appear in the Pebble plan.
- **Impact**: log forwarding is silently absent from the Pebble layer when Loki is related, with no indication to the operator.
- **Fix**: add `framework.observe(self._logging.on.logging_relation_changed, self._update_layer_and_restart)` in `__init__`.
- **Linter rule**: a charm using `LokiPushApiConsumer` should observe its relation-changed event and call the layer-update method — mechanically checkable by searching for `logging_relation` handling in the charm source.

### `audit-logs` action catches the wrong exception type

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:215`
- **Evidence**: `_on_audit_logs_action` catches `ops.model.ModelError`, but `container.exec()` raises `ops.pebble.ExecError` on failure. The except clause is unreachable for this path.
- **Impact**: exec failures are not handled by the intended error path.
- **Fix**: catch `ops.pebble.ExecError` instead.
- **Linter rule**: not mechanically checkable.

### Unit tests completely broken (wrong class name, wrong container name)

- **Severity**: critical
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:10`
- **Evidence**: imports `from charm import CanonicalCla2Charm`, but the charm class is `FastAPICharm` (`src/charm.py:25`). `pytest tests/unit/` fails at collection with `ImportError`. The test also references an `httpbin` container/service (line 37), but the charm's container/service is `app`; integration tests reference a nonexistent `httpbin-image` resource.
- **Impact**: zero unit test coverage; the test suite provides no value and would not catch any of the bugs listed above.
- **Fix**: replace `CanonicalCla2Charm` with `FastAPICharm`, `"httpbin"` with `"app"` throughout, and the `httpbin-image` resource with `cla-image`.
- **Linter rule**: not mechanically checkable (test infrastructure).

### `GrafanaDashboardProvider` sends empty dashboards (directory not found)

- **Severity**: high
- **Kind**: ux
- **Where**: `src/charm.py:56–57` (`GrafanaDashboardProvider` init); `lib/charms/grafana_k8s/v0/grafana_dashboard.py:977`
- **Evidence**: `GrafanaDashboardProvider` resolves the default dashboard path `"src/grafana_dashboards"`, which does not exist in the repo. It catches `InvalidDirectoryPathError`, logs a warning, but does not reassign `dashboards_path`. `Path.glob("*")` on the unresolved path returns nothing, so `dashboard_templates` stays empty. Confirmed via `juju show-unit grafana-agent-k8s/0`: `dashboards: '{"templates": {}, "uuid": "..."}'`.
- **Impact**: the charm declares `provides: grafana-dashboard` but delivers zero dashboards.
- **Fix**: add real dashboard JSON files under `src/grafana_dashboards/`, or remove the `GrafanaDashboardProvider` and the `grafana-dashboard` relation from metadata.
- **Linter rule**: `GrafanaDashboardProvider` must point at a directory containing `*.json` files — mechanically checkable.

### No `upgrade-charm` handler: Pebble layer not updated on refresh

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:35–72` (no observer for `on.upgrade_charm`)
- **Evidence**: the charm observes config-changed, pebble-ready, collect-unit-status, both actions, redis-relation-updated, database-created, endpoints-changed — but not `on.upgrade_charm`. Not exercised live (no newer charmhub revision available to test `juju refresh` against); confirmed by source inspection only.
- **Impact**: `juju refresh` would leave the workload running against the stale Pebble layer.
- **Fix**: add `framework.observe(self.on.upgrade_charm, self._update_layer_and_restart)`.
- **Linter rule**: a charm that manages Pebble layers should observe `on.upgrade_charm` — mechanically checkable.

### `config_valid_values` requires the database secret unconditionally

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:340–347`
- **Evidence**: iterates all secret config options from `config.yaml` and requires every one to be set, including `database`, which the docs describe as overriding the relation (i.e. optional). Confirmed: even with the postgresql-k8s relation established, the charm blocked until a `database` secret was also provided.
- **Impact**: a user who correctly sets up the relation still must create a dummy database secret to pass validation.
- **Fix**: skip the `database` secret requirement when the database relation is present.
- **Linter rule**: not mechanically checkable without doc analysis.

### `fetch_secrets` silently drops empty-string secret values

- **Severity**: high
- **Kind**: bug
- **Where**: `src/utils.py:47–50`
- **Evidence**: `if not (isinstance(v, str) and v == ""):` strips any empty-string value. A `database-host=""` key is silently removed from the dict rather than flagged.
- **Impact**: silent failure — the charm can report Active with no database credentials actually applied.
- **Fix**: only drop `None` values (`if v is not None:`).
- **Linter rule**: not mechanically checkable without understanding downstream use.

### `fetch_secrets` raises raw pydantic `ValidationError` into Juju status

- **Severity**: medium
- **Kind**: ux
- **Where**: `src/utils.py:45` (`Secret.parse(**secrets_values).dict()`)
- **Evidence**: on Juju 3.x, a malformed secret produced a clean, actionable message (`Config values are not valid: Error fetching secrets: 1 validation error for Secret\nsecret_key\n  field required`). On Juju 4.x, a wrong-key-structure secret surfaced the raw pydantic dump with 13 errors and Python field names instead of the `juju config` secret names. (unverified whether this is a genuine Juju-version behaviour difference or an artefact of the test environment.)
- **Impact**: operator sees an opaque error, not guidance, at least in some cases.
- **Fix**: wrap `Secret.parse(...)` in `try/except ValidationError` and surface an actionable message naming the required keys.
- **Linter rule**: not mechanically checkable.

### `fetch_secrets` called three times per status collection cycle

- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:355` (`config_valid_values`), `:361` (`postgres_relation_blocked`), `:380` (`fetch_postgres_relation_data`)
- **Evidence**: all three methods independently call `fetch_secrets(self)`, each reading all 7 Juju secrets as separate RPC calls.
- **Impact**: 3x the RPC overhead per status cycle (runs every ~5 minutes).
- **Fix**: fetch secrets once and cache/pass the result.
- **Linter rule**: not mechanically checkable.

### `pebble_log_targets` logs ERROR on every layer update when Loki is absent

- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:308–327` (`pebble_log_targets` property)
- **Evidence**: called on every `_pebble_layer` access; when Loki is unrelated, `self._logging.loki_endpoints` is empty and the method calls `logger.error("Loki push api not available")`. Fires on every config-changed hook, even for unrelated changes like `app_url=foo`.
- **Impact**: ERROR-level logs imply a fault in a healthy, correctly-configured charm and drown out real errors.
- **Fix**: downgrade to `logger.info()` or `logger.debug()` since Loki is optional.
- **Linter rule**: not mechanically checkable.

### `config_valid_values` reads `config.yaml` from disk on every call

- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:334–337`
- **Evidence**: `yaml.safe_load(open(f"{base_dir}/config.yaml"))` with `base_dir = os.getcwd()`, called from `_on_collect_status` roughly every 5 minutes.
- **Impact**: unnecessary disk I/O on the status hook path; currently works "by accident" since `os.getcwd()` resolves to `/` in the pod, where the charm happens to be mounted.
- **Fix**: cache the parsed config schema at `__init__` time.
- **Linter rule**: config validation should not perform disk I/O on every invocation — mechanically checkable.

### `charmcraft.yaml` missing charm name

- **Severity**: medium
- **Kind**: bug
- **Where**: `charmcraft.yaml`
- **Evidence**: file contains only `type: charm` and `bases`, no `name` field.
- **Impact**: minimal but non-compliant charmcraft metadata.
- **Fix**: add `name: canonical-cla`.
- **Linter rule**: `charmcraft.yaml` must contain a `name` field — mechanically checkable.

### `fetch_redis_relation_data` uses imprecise type annotation

- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:408`
- **Evidence**: declared as `-> Dict | None` but actually returns `Dict[str, str] | None`.
- **Fix**: use `Dict[str, str] | None`.
- **Linter rule**: not mechanically checkable.

### `on = RedisRelationCharmEvents()` overrides `CharmBase.on` property

- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:29`
- **Evidence**: Pyright: `"on" incorrectly overrides property of same name in class "CharmBase"`. `CharmBase.on` is a property returning the framework's event registry; assigning a plain instance attribute shadows it. Works at runtime because the instance attribute takes precedence, but only `self.on.redis_relation_updated` is reachable this way — other standard events must go through `self.framework.observe(self.on.<event>, ...)`, which still works because `self.on` was set before the override in practice, but is fragile.
- **Fix**: use a separate attribute, e.g. `self.redis_events = RedisRelationCharmEvents()`, and observe `self.redis_events.redis_relation_updated`.
- **Linter rule**: caught by Pyright.

### Unused imports and minor formatting issues

- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:5` (unused `Optional`), `:154,159` (f-strings without placeholders), `:137` (blank line after docstring)
- **Evidence**: Ruff reports 18 errors total (8 auto-fixable).
- **Fix**: `ruff check --fix`.
- **Linter rule**: mechanically checkable with `ruff check`.

## Worth copying

- **Status precedence ordering** (`_on_collect_status`): the chain from config validity → Pebble readiness → relation presence → relation data → service running → Active is clear and handles all states.
- **Pebble checks with restart-on-failure** (`_pebble_layer`): defining both `online` (READY) and `up` (ALIVE) checks with `"up": "restart"` is correct for a production service.
- **Separate secrets per concern** (`src/secret.py`): a pydantic `Secret` model to parse and validate secret content, including normalising `kebab-case` keys to `snake_case`, is a clean pattern.
- **Config-driven Pebble layer** (`_pebble_layer`): built entirely from a property, recomputed on every call — correct for a dynamic layer.
- **Debounced restarts** (`_update_layer_and_restart`): only restarts the service when the layer actually differs from the current plan.
- **Proxy environment variable support** (`get_proxy_dict`): correctly falls back to Juju charm proxy environment variables.
- **`MAINTENANCE_MODE` correctly stringified in the Pebble layer**: `_pebble_layer` passes `MAINTENANCE_MODE: "false"` (string) to Pebble; only the `container.exec()` path fails.

## Common-practice notes

- **Library versioning**: all libraries vendored at `v0/`. Convention is `vN` with incrementing major version.
- **`charmcraft.yaml` minimalism**: no `name`, `title`, `description`, `summary`, or `assumes` fields.
- **No Terraform module**: infrastructure-as-code users cannot manage the charm via Terraform.
- **Test structure**: standard layout but completely stale content.
- **Single-template commit**: no meaningful git history.
- **Loki integration pattern**: initializing `LokiPushApiConsumer` without observing its relation events is a common ecosystem mistake.
- **No TLS certificates interface**: TLS must be handled externally (e.g. at the ingress layer).

## Tests

**Unit tests**: completely broken. Cannot import `CanonicalCla2Charm` (charm is `FastAPICharm`). References `httpbin` container (charm uses `app`). `pytest tests/unit/` fails at collection with `ImportError`. Zero unit tests execute. `PYTHONPATH="lib:src"` required for imports.

**Integration tests**: references `httpbin-image` resource (non-existent) and the wrong container name. `test_build_and_deploy` is the only test — it builds and deploys the charm but has no assertions beyond waiting for Active.

**Coverage gap**: no tests for any actual code path: secret parsing, actions, status precedence, database/redis relation data fetching, Pebble layer construction, `app_environment`, upgrade handling, or the Loki/Grafana/Prometheus integrations. Even the status-precedence chain has no unit test.

**Ruff**: 18 errors, 8 auto-fixable via `ruff check --fix src/`. Codespell: 1 typo (`PostgresSQL` → `PostgreSQL` in `README.md`).

**Pyright**: 7 errors, all import-resolution (charm libraries not on path in this environment). 1 genuine type error: `"on"` incorrectly overrides property from `CharmBase`.

## Docs

**README.md**: describes integrations, secrets, and actions clearly. One typo (`PostgresSQL` → `PostgreSQL`). COS Lite section is detailed. Actions are documented accurately (though broken at runtime).

**CONTRIBUTING.md**: standard template, correctly documents the `tox` workflow.

**Config doc/reality mismatch**: `database` secret is described as "overrides the database relation" (optional) but is required unconditionally. `sentry_dsn` is described as "(optional)" but treated as required.

**Missing upgrade documentation**: no section on `juju refresh`, which is notable given the missing `upgrade-charm` handler.

## Open questions

1. Why are `secret_key` and `internal_api_secret` separate config options? Both are single-value string secrets requiring separate Juju secrets.
2. `app_url` is not URL-validated — `not-a-valid-url` is accepted without error.
3. `app_url` is set in `app_environment` but the Pebble layer/uvicorn command doesn't appear to reference it — unclear whether the application itself uses it.
4. `app_name` config is declared but never referenced in `app_environment` or `_pebble_layer` — appears to be dead config.
5. The `database` secret's required key names (`database-host`, `database-port`, etc.) are undocumented in the README.
6. Can `app_environment` be called before a database relation is established? `config_valid_values()` runs first and would set BlockedStatus, but the path where `fetch_postgres_relation_data()` is called with a missing secret but present relation is untested.
7. `environment` config accepts any string with no validation — `production`, `foobar`, or empty string are all accepted.
8. `migrate-db`'s pre-flight database-readiness check (charm.py lines 159-162) is commented out.
9. `migrate-db` has a dead except clause for `ops.pebble.ChangeError`, which `container.exec()` never raises (only `ops.pebble.ExecError` is possible).
10. `audit_logs.py` imports the full app config at module import time; running it standalone (e.g. `--help`) fails with a pydantic `ValidationError` before argument parsing — even with the Pebble environment bug fixed, the action requires every secret and the full database/redis environment to be correctly set.
