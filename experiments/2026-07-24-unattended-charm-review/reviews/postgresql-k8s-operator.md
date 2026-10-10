# postgresql-k8s

A mature, well-organised K8s charm managing PostgreSQL 14 via Patroni, with extensive pydantic-typed config, structured upgrade support, and thoughtful operational patterns (Pebble health checks, dual-file Patroni config, on-failure-condition overrides for maintenance). Underneath that polish are several serious defects: numeric config bounds are almost entirely unenforced (a pydantic v1/`Annotated` incompatibility silently disables ~30 `Field(ge=…)` constraints), an unbounded `experimental_max_connections` field can crash PostgreSQL into an unrecoverable restart loop, and the `set-password` action can be used to permanently break the charm's own database credentials with no fallback recovery path short of manual `kubectl exec` surgery. A maintainer should first fix the `Annotated`/pydantic-v1 validation gap and add bounds to `experimental_max_connections`, then fix `set-password` to reject empty/quote-containing passwords before they reach PostgreSQL — these three issues are all reachable through normal `juju config`/`juju run` usage and each can put the charm in a state it cannot repair on its own.

| | |
|---|---|
| Repo | canonical/postgresql-k8s-operator @ `7c8f99d` (2026-07-21) |
| Charms | postgresql-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3, 14/edge rev 939 (models `rv-pg-deep`, `rv-pg-deep4`). Also refreshed to 14/stable rev 925. |
| Reviewed | 2026-07-28 |

## What it does

Deploys PostgreSQL 14 on Kubernetes using the Patroni HA framework. The charm manages cluster membership via k8s endpoints/services, renders Patroni YAML, handles TLS certificate rotation, backup/restore to S3, point-in-time recovery, async cross-cluster replication, LDAP authentication, COS observability (Prometheus, dashboards, Loki, Tempo), and in-place rolling upgrades. It exposes three client interfaces: modern `postgresql_client` (`database`), legacy `pgsql` (`db`/`db-admin`), and async replication offer/consumer.

## Deployment log

```
# Juju 4 attempt — blocked by assumes:
$ juju deploy postgresql-k8s --channel 14/edge --trust -n 1 -m rv-pg-k8s
ERROR charm requires all of the following:
  - charm requires Juju version < 4.0.0, model has version 4.0.5

# Juju 3.6 — successful single unit (model rv-pg-deep):
$ juju add-model rv-pg-deep
$ juju deploy postgresql-k8s --channel 14/edge --trust -n 1
Deployed from charm-hub, revision 939
~90s to active/Primary

# TLS integration (self-signed-certificates 1/edge rev 659):
$ juju deploy self-signed-certificates --channel 1/edge
$ juju relate postgresql-k8s:certificates self-signed-certificates:certificates
Rolling restart completes, Patroni config gains hostssl entries and SSL certs

# Database client (data-integrator):
$ juju deploy data-integrator database-test --channel edge --config database-name=testdb
$ juju relate postgresql-k8s:database database-test:postgresql
Database testdb created, credentials delivered via secrets

# Observability (grafana-agent-k8s 0.40/edge rev 233):
$ juju deploy grafana-agent-k8s --channel edge
$ juju relate postgresql-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
$ juju relate postgresql-k8s:logging grafana-agent-k8s:logging-provider
grafana-agent-k8s goes to Blocked (no cos-lite — expected), relations formed correctly

# Scale 1→3→1:
$ juju add-unit postgresql-k8s -n 2   # all active within ~60s
$ juju scale-application postgresql-k8s 1  # clean scale-down, stays active/Primary

# Failure injection — out-of-range config:
$ juju config postgresql-k8s experimental_max_connections=1000000000
Accepted by pydantic. PostgreSQL crashes with FATAL:
"1000000000 is outside the valid range for parameter 'max_connections' (1 .. 262143)"
Unit enters a restart loop until config is reset with --reset.

$ juju config postgresql-k8s experimental_max_connections=-5
Also accepted. PostgreSQL would crash with similar FATAL.

# Failure injection — pydantic v1 Annotated constraints don't work:
$ juju config postgresql-k8s memory_shared_buffers=0   # Field(ge=16) — ACCEPTED
$ juju config postgresql-k8s profile_limit_memory=0     # Field(ge=128) — ACCEPTED
$ juju config postgresql-k8s vacuum_autovacuum_naptime=0 # Field(ge=1) — ACCEPTED
Verified via .tox/unit/bin/python: pydantic 1.10.26 silently ignores
Annotated[int, Field(ge=...)] metadata. All bounded fields are unvalidated.

# Failure injection — bad profile value (uses @validator, which DOES work):
$ juju config postgresql-k8s profile=invalid
→ BlockedStatus "Configuration Error. Please check the logs" (correct)

# Pod delete (simulate node failure):
$ kubectl delete pod postgresql-k8s-0 -n rv-pg-deep2
Pod recreated, unit returns to active/Primary in ~40s.

# Kill test:
$ kubectl exec postgresql-k8s-0 -c postgresql -- kill -9 <patroni-pid>
Pebble on-failure:restart brings patroni back in ~5s. Unit stays active.

# Actions:
$ juju run postgresql-k8s/0 get-primary → primary: postgresql-k8s/0
$ juju run postgresql-k8s/0 get-password → password: REDACTED
$ juju run postgresql-k8s/0 set-password username=operator → "The old and new passwords are equal." (no-op)
$ juju run postgresql-k8s/0 set-password username=operator password=ExplicitPass123 → works
$ juju run postgresql-k8s/0 pre-upgrade-check → succeeds
$ juju run postgresql-k8s/0 promote-to-primary scope=unit → fails ("Switchover failed or timed out" — single unit, expected)

# TLS removal:
$ juju remove-relation postgresql-k8s:certificates self-signed-certificates:certificates
Charm reverts to non-TLS config, stays active.

# Database relation removal:
$ juju remove-relation postgresql-k8s:database db-test:postgresql
Clean removal, db-test goes to blocked (expected).

# Refresh 14/edge→14/stable (rev 939→925):
$ juju refresh postgresql-k8s --channel 14/stable
Pod recreated, ~60s to active/Primary on revision 925.

# Rapid kill test (3x SIGKILL on patroni, 2s apart):
All three kills recovered by Pebble on-failure:restart within ~5s each. Unit stayed active.

# set-password with operator-supplied password containing single quote:
$ juju run postgresql-k8s/0 set-password username=operator password="test'pass"
→ Action failed: "Failed changing the password." (SQL syntax error from injected quote)

# Failure injection — TLS + bad config interaction:
$ juju config postgresql-k8s durability_synchronous_commit=invalid  # Blocked (correct, @validator works)
$ juju relate postgresql-k8s:certificates self-signed-certificates:certificates
→ Unit enters error state: "hook failed: certificates-relation-changed"
Traceback shows push_tls_files_to_workload raises ValidationError from invalid durability_synchronous_commit.
Recovery requires juju config durability_synchronous_commit=on + juju resolve.

# SECOND SESSION — rv-pg-deep4 (fresh model, same revision 939):

# Remaining actions:
$ juju run postgresql-k8s/0 pre-upgrade-check → success (return-code 0)
$ juju run postgresql-k8s/0 list-backups → "Relation with s3-integrator charm missing" (correct)
$ juju run postgresql-k8s/0 create-backup → "Stanza was not initialised" (correct, no S3 config)
$ juju run postgresql-k8s/0 promote-to-primary scope=unit → "Switchover failed or timed out" (correct, single unit)

# set-password edge cases (rv-pg-deep4):
$ juju run postgresql-k8s/0 set-password username=operator password='' → SUCCEEDED, result: password: ""
→ PostgreSQL: empty string rejected, password cleared, stored secret became None
→ Charm could no longer connect as operator: FATAL password authentication failed
→ All subsequent set-password attempts permanently failed: "Failed changing the password."
→ get-password returned None for operator
→ Recovery required manual PostgreSQL intervention (ALTER USER via superuser + secret update)

$ juju run postgresql-k8s/0 set-password username=operator password='p@ss"word' → "Failed changing the password." (double-quote breaks SQL)
$ juju run postgresql-k8s/0 set-password username=operator password='test\back' → "Failed changing the password." (backslash breaks SQL)

# Scale 1→3 with broken operator password (cascade failure):
$ juju add-unit postgresql-k8s -n 2
→ Units 1,2 joined Patroni cluster (sync standbys, verified via Patroni API)
→ But hook failures: "upgrade-relation-changed" KeyError on both new units
→ unit 0: "Failed to list PostgreSQL database users: password authentication failed for user 'operator'" on every peer-relation-changed hook
→ Units 1,2 stuck in error state, unit 0 stays active/Primary but unmanageable
→ Scale-down to 1 stuck (units 1,2 in error, can't tear down cleanly)

# S3 integration (s3-integrator 1/edge rev 580):
$ juju deploy s3-integrator --channel 1/edge
$ juju relate postgresql-k8s:s3-parameters s3:s3-credentials
→ s3-integrator stays blocked: "Missing parameters: ['access-key', 'secret-key']"
→ postgresql-k8s stays active: correctly detects missing S3 params
$ juju run postgresql-k8s/0 list-backups → "Missing S3 parameters: ['access-key', 'secret-key']" (correct)
→ s3-integrator on Juju 3.6 uses sync-s3-credentials action, not config keys; couldn't test with fake credentials without action

# Patroni health during cascade failure:
$ kubectl exec → python3 urllib.request → GET /health: {"state": "running", "role": "master"}
$ kubectl exec → GET /cluster: 3 members (postgresql-k8s-0 leader, 1 and 2 sync_standby running)
PostgreSQL/Patroni healthy despite charm hook failures — the database was serving replicas throughout.
```

## Observed behaviour

- **Startup time:** 36s from allocate to active for a single unit. Patroni health endpoint returns 503 for ~5s during bootstrap. Three-unit cluster forms in ~60s.
- **Pebble layout:** 6 services in the postgresql container: `postgresql` (Patroni + PostgreSQL, enabled, on-failure:restart), `metrics_server` (enabled), `pgbackrest_metrics_service` (enabled), `ldap-sync`, `pgbackrest server`, `rotate-logs` (disabled). Pebble health check on `https://<pod>:8008/health` when TLS is enabled.
- **Patroni config (from `/var/lib/postgresql/data/patroni.yml`):** DCS failsafe mode enabled, synchronous mode with `synchronous_node_count` from config, `max_timelines_history=50`, `wal_level=logical`, `shared_preload_libraries: timescaledb,pgaudit,pg_stat_statements`. When TLS is active, `hostssl` pg_hba entries replace `host` entries, and REST API listens on `0.0.0.0:8008` with HTTPS and client certificates. Full PostgreSQL parameter set rendered from charm config (~150+ parameters).
- **K8s resources:** Headless `endpoints` Service (Juju-managed), `primary` and `replicas` ClusterIP Services (charm-managed), Patroni-created endpoints and config/sync Services.
- **Resource use:** ~2m CPU, ~310Mi memory for the postgresql container at idle on a small 3.6 cluster.
- **Kill recovery:** SIGKILL on patroni → Pebble restart brings it back in ~5s. Unit stays active throughout.
- **Pod delete recovery:** `kubectl delete pod` → unit goes to maintenance (stop) → StatefulSet recreates pod → unit returns to active/Primary in ~40s. Clean recovery, no manual intervention needed.
- **Password rotation no-op:** `set-password` without an explicit `password` parameter generates `new_password()` and compares it to the stored secret. When the stored secret was also originally generated by `new_password()`, the strings are generally not equal — but the action log from the first run reported them as equal. Behaviour depends on how the stored secret was originally set; supplying an explicit password worked correctly in a later test.
- **Hook churn:** `set-password` triggers `update_config()` → `_handle_postgresql_restart_need()` → Patroni reload + rolling restart lock. Reasonable for a credential rotation.
- **Config-to-crash path:** `juju config experimental_max_connections=1000000000` → pydantic accepts (field typed `int | None`, no bounds) → `_build_postgresql_parameters()` in `postgresql.py` passes it through as `max_connections` → Patroni YAML renders it → PostgreSQL FATAL: value outside `[1..262143]` → Patroni crash-loops → Pebble restarts endlessly → charm cannot process hooks to fix it. Recovery requires `juju config --reset`.
- **Pydantic v1 Annotated bypass:** `memory_shared_buffers=0` (type `SharedBuffersInt = Annotated[int, Field(ge=16)]`) was accepted, rendered into `/var/lib/postgresql/data/patroni.yml` as `shared_buffers: 0`, and PostgreSQL is running with it. The `Field(ge=16)` constraint was silently ignored because pydantic v1.10 does not process `Annotated` metadata. This affects all ~30 type aliases defined at the top of `src/config.py` (`WorkerProcessInt`, `PgIntMax`, `PgPositiveIntMax`, `PercentFloat`, `SharedBuffersInt`, `TempBuffersInt`, `WorkMemInt`, `StatisticsTargetInt`, `GeqoEffortInt`, `ProfileLimitMemoryInt`, `BgwriterLruMaxpagesInt`, `DeadlockTimeoutInt`, `AutovacuumNapTimeInt`, `FreezeMinAgeInt`, `FailsafeAgeInt`, etc.). Only `@validator`-decorated methods (for enum-style string fields like `profile`, `durability_synchronous_commit`) actually enforce constraints.
- **TLS hostname mismatch:** The TLS certificate SANs include pod hostnames like `postgresql-k8s-0.postgresql-k8s-endpoints` but not `localhost`. Connecting to `localhost:8008` with TLS verification fails with hostname mismatch. The Patroni health check uses correct pod hostnames, so this is only a local debugging inconvenience.
- **Patroni DCS template:** A second config file at `/config/patroni.yaml` holds the DCS bootstrap template (Raft-based, using `/var/snap/charmed-postgresql/common/raft`). This is distinct from the rendered YAML at `/var/lib/postgresql/data/patroni.yml`.
- **Config validation + TLS event interaction:** When `durability_synchronous_commit` is invalid and a `certificates-relation-changed` event fires, `_on_certificate_available` → `push_tls_files_to_workload` → `update_config` → `self.config` raises `ValidationError`, propagating uncaught through the TLS library and sending the unit to `error` state. Recovery requires fixing the config AND `juju resolve`. The `_on_config_changed` handler has a `ValueError` catch that correctly sets `BlockedStatus`, but the TLS event path bypasses it.
- **Refresh 14/edge→14/stable:** Downgrade from rev 939 to rev 925. Pod was recreated, charm recovered to active/Primary in ~60s. Clean.
- **Rapid kill (3× SIGKILL, 2s apart):** Pebble `on-failure:restart` brought Patroni back each time within ~5s. Unit never left active status.
- **set-password with operator-supplied password `test'pass`:** Confirmed SQL syntax error in `update_user_password` (`ALTER USER "operator" WITH ENCRYPTED PASSWORD 'test'pass'` — the quote splits the string). Action fails gracefully with "Failed changing the password." — the charm does not crash. The error is logged clearly.
- **set-password with empty string password:** The action SUCCEEDS (result: `password: ""`). PostgreSQL rejects the empty string (`NOTICE: empty string is not a valid password, clearing password`), leaving the operator user with no password. The charm stores `None` in the Juju secret. Thereafter, all charm hooks that connect to PostgreSQL fail with `FATAL: password authentication failed for user "operator"` because the charm passes `None` while pg_hba requires md5. The `set-password` action itself becomes permanently broken because `update_user_password()` connects as the operator user to change its own password. Manual `kubectl exec` intervention was required to recover: `su - postgres -c "psql -U backup -d postgres"` and `ALTER USER operator WITH ENCRYPTED PASSWORD`. The charm has no fallback authentication path for this scenario.
- **set-password with double-quote or backslash in password:** Also fails (same class of SQL syntax break). Both `p@ss"word` and `test\back` produced "Failed changing the password." The charm doesn't crash — graceful failure with logged error.
- **Scale-up cascade during broken operator password:** When operator credentials are broken, new units cannot bootstrap their Patroni instances (they need operator credentials from peer relation data). The PostgreSQL/Patroni cluster itself forms correctly (replicas stream from primary as sync standbys), but the charm hooks fail with `KeyError` in `data_platform_libs/v0/upgrade.py:987` looking for peer unit data that never populated. Units 1 and 2 permanently stuck in `error: hook failed: "upgrade-relation-changed"`. Scale-down to 1 also stalls.
- **Patroni proxying charm failures:** During the cascade failure, Patroni REST API (`GET /health`, `GET /cluster`) showed all 3 members healthy, the primary serving normally, and both replicas streaming as sync standbys. The database was operational throughout — only the charm management layer was broken. This is a credit to Patroni's resilience but also means charm-level issues can go unnoticed.
- **S3 integration without credentials:** When s3-integrator lacks credentials, postgresql-k8s stays `active` (correct — no blocking). `list-backups` action fails with clear message: "Missing S3 parameters: ['access-key', 'secret-key']". `create-backup` action fails with "Stanza was not initialised" when no S3 relation exists, or "Missing S3 parameters" when relation exists but credentials are absent.
- **`_connect_to_database` missing-space claim retracted:** Initially reported as a bug but verified with `psycopg2.extensions.parse_dsn()` — libpq's DSN parser correctly handles the concatenation `host='val'password='val2'` (the closing quote terminates the value, then the next keyword is recognised). This is NOT a bug. The only DSN-level vulnerability is when `self.password` contains `'`, but internally-generated passwords from `new_password()` are alphanumeric, and operator-supplied passwords with `'` are already blocked by the SQL-level bug before reaching this code path.

## Findings

### `set-password` accepting empty string password causes irrecoverable cascade failure
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:1268-1295` (`_on_set_password`), `lib/charms/postgresql_k8s/v0/postgresql.py:831-844` (`update_user_password`)
- **Evidence**: `juju run postgresql-k8s/0 set-password username=operator password=''` — the action SUCCEEDED with result `password: ""`. PostgreSQL then rejected the empty string (`NOTICE: empty string is not a valid password, clearing password`), leaving the operator user with NO password (`rolpassword` set to NULL). The stored Juju secret updated to `operator-password: None`. Subsequently every `config-changed` and `peer-relation-changed` hook emitted `FATAL: password authentication failed for user "operator"` because the charm passed `None` as the password while pg_hba.conf requires md5 auth. The `set-password` action handler calls `update_user_password()`, which itself connects as the operator to ALTER the operator — a circular dependency that permanently breaks password rotation. Scaling 1→3 then failed: new units could not bootstrap (they require operator credentials from peer relation data), causing `hook failed: "upgrade-relation-changed"` with `KeyError` from `data_platform_libs/v0/upgrade.py:987`. The charm has no fallback authentication path — manual `kubectl exec` + `su - postgres` + `psql -U backup` intervention was required to `ALTER USER operator WITH ENCRYPTED PASSWORD`.
- **Impact**: An operator testing password rotation with an empty string can permanently break the charm's ability to manage PostgreSQL. The charm reports `active/Primary` (PostgreSQL/Patroni keep running) but cannot process config changes, scale operations, or further password rotations. The only recovery path requires PostgreSQL-level manual intervention.
- **Fix**: (1) Validate `password` in `_on_set_password`: reject empty strings, and reject passwords containing `'`, `"`, or `\` with a clear error message before they reach PostgreSQL. (2) Add a fallback recovery path: if `update_user_password()` fails with an authentication error, attempt the change using the `backup` superuser via local Unix-socket peer auth. (3) Store the new password in the Juju secret only after `update_user_password()` succeeds, not before, so a partial failure can't desync stored credentials and the database.
- **Linter rule**: "set-password action that does not validate password content before passing to PostgreSQL" — partially mechanically checkable (detect `password = event.params["password"]` without subsequent empty/character-filter check).

### All `Annotated[..., Field(ge=…)]` numeric bounds are silently ignored (pydantic v1 incompatibility)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/config.py:16-57` (all `Annotated` type aliases), `pyproject.toml` (`pydantic = "^1.10.26"`)
- **Evidence**: Pydantic v1.10 does not process `Annotated` metadata for `Field` constraints. Verified with pydantic 1.10.26 in the tox environment: `SharedBuffersInt = Annotated[int, Field(ge=16)]` followed by `TestConfig(memory_shared_buffers=0)` does NOT raise `ValidationError` — it silently accepts 0. Also confirmed for `profile_limit_memory=0` (should be `ge=128`) and `vacuum_autovacuum_naptime=0` (should be `ge=1`). Deployed confirmation: `juju config postgresql-k8s memory_shared_buffers=0` was accepted (charm stayed active), and `shared_buffers: 0` was rendered into `/var/lib/postgresql/data/patroni.yml`. Affects all ~30 type aliases at `src/config.py:16-57`.
- **Impact**: An operator can silently set a dangerously low or high PostgreSQL parameter that either crashes the database or degrades performance in ways that are hard to diagnose. `config.yaml` has no Juju-level `minimum`/`maximum` constraints either, so there is zero validation for numeric bounds. The integration test `test_config_parameters` (`tests/integration/test_config.py`) expects these values to be rejected — with the current pydantic pin it cannot pass for the `Annotated`-based cases (see test-gap finding below).
- **Fix**: Either (a) upgrade to pydantic v2 where `Annotated` is natively supported (requires a `data_platform_libs` upgrade and Python ≥3.9), (b) replace the `Annotated[..., Field(ge=..., le=...)]` aliases with pydantic v1-compatible `Field(default=None, ge=..., le=...)` syntax, or (c) add Juju-level `minimum`/`maximum` constraints in `config.yaml` as a belt-and-suspenders measure. (c) is the quickest fix and doesn't require a pydantic migration.
- **Linter rule**: "`Annotated[..., Field(ge=…)]` used with pydantic <2" — mechanically checkable by detecting `Annotated[..., Field(ge=` patterns combined with a pydantic <2 version constraint in `pyproject.toml`.

### `experimental_max_connections` accepts out-of-range values, crashes PostgreSQL
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/config.py:78` (`experimental_max_connections: int | None`)
- **Evidence**: The field has no `Field` constraint. `juju config experimental_max_connections=1000000000`, `=-5`, and `=0` were all accepted. The value flows through `postgresql.py`'s `build_postgresql_parameters()` to `render_patroni_yml_file()`. Observed: PostgreSQL FATAL `"1000000000 is outside the valid range for parameter 'max_connections' (1 .. 262143)"`, causing an infinite restart loop. The charm cannot recover on its own because `config-changed` hooks cannot run while Patroni is crash-looping; the operator must manually `juju config --reset`.
- **Impact**: An operator changing an `[EXPERIMENTAL]` config field can crash the entire PostgreSQL instance with no self-healing path — downtime until manual intervention.
- **Fix**: Add `Field(ge=1, le=262143)` to the field. Accepting out-of-range values is worse than rejecting them, even for an experimental field.
- **Linter rule**: "Pydantic `int` config fields mapping to PostgreSQL parameters without `Field(ge=..., le=...)` bounds" — mechanically checkable by comparing field names to known PostgreSQL parameter ranges.

### Integration test `test_config_parameters` cannot pass for `Annotated`-based fields with pydantic v1.10
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/integration/test_config.py:23-358`
- **Evidence**: The test sets invalid config values and expects `BlockedStatus`. For `@validator`-protected fields (e.g. `durability_synchronous_commit`, `profile`, `request_backslash_quote`) this works. For `Annotated[..., Field(ge=…)]` fields (e.g. `memory_shared_buffers=15`, `profile_limit_memory=127`, `optimizer_default_statistics_target=0` — ~30 fields total) the `Field` constraints are silently ignored by pydantic v1.10.26 (confirmed via `.tox/unit/bin/python`: `TestConfig(memory_shared_buffers=15)` raises no error). `_validate_config_options()` in `charm.py:2367` only checks a handful of DB-dependent text-search/locale/date-style fields — it does not validate numeric bounds. The test's `block_until(workload_status == "blocked", timeout=100)` would time out for these cases. `pyproject.toml` pins `pydantic = "^1.10"` because `data_platform_libs/v0/upgrade.py` requires it.
- **Impact**: Double failure: config validation doesn't work at runtime, and the integration test meant to catch that either doesn't exercise the `Annotated`-based cases or is red in CI. Operators can set `memory_shared_buffers=0`, `profile_limit_memory=0`, `vacuum_autovacuum_naptime=0`, etc., and the charm stays active with silently incorrect PostgreSQL configuration.
- **Fix**: Fix the underlying validation gap (see pydantic finding above), then confirm/update the test to actually assert rejection of out-of-range values for all affected fields.
- **Linter rule**: "`Annotated[..., Field(ge=…)]` used with pydantic <2" combined with "integration test asserting BlockedStatus for config validation the underlying model doesn't enforce" — the latter requires cross-referencing config.yaml, the pydantic model, and test assertions.

### TLS `certificate-available` event propagates config `ValidationError` as unhandled exception
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:1915` (`push_tls_files_to_workload`), `lib/charms/postgresql_k8s/v0/postgresql_tls.py:134` (`_on_certificate_available`)
- **Evidence**: Set `durability_synchronous_commit=invalid` (correctly blocked by `@validator`), then related TLS certificates. `certificates-relation-changed` fired `_on_certificate_available` → `push_tls_files_to_workload` → `update_config` → `self.config` (constructs `CharmConfig`), which raised a pydantic `ValidationError` that propagated uncaught through the TLS library. The unit went to `error` state with "hook failed: certificates-relation-changed". `_on_config_changed` (line 688) has a `ValueError` catch that correctly sets `BlockedStatus`, but the TLS event path has no equivalent. Recovery required `juju config durability_synchronous_commit=on` + `juju resolve`.
- **Impact**: A bad config value set before establishing a TLS relation causes the unit to enter error state on every `certificates-relation-changed` retry. The operator sees "hook failed" rather than "Configuration Error", and must both fix the config AND run `juju resolve`.
- **Fix**: Wrap the `update_config()` call inside `push_tls_files_to_workload` in a try/except that catches `ValidationError` and sets `BlockedStatus`, or ensure `update_config()` itself catches `ValidationError` at its outermost boundary.
- **Linter rule**: not mechanically checkable — requires tracing event handler call chains for missing exception handling around pydantic `ValidationError`.

### `create_user` concatenates password into SQL via f-string (same class of bug as `update_user_password`)
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/postgresql_k8s/v0/postgresql.py:325,330`
- **Evidence**:
  ```python
  user_definition += f"WITH … ENCRYPTED PASSWORD '{password}' …"
  …
  cursor.execute(SQL(f"{user_definition};").format(Identifier(user)))
  ```
  The password is interpolated into the SQL string via f-string before `SQL()` wraps it; `Identifier()` only covers the username. A password containing `'` will break the SQL syntax. Internally-generated passwords (`new_password()`) are alphanumeric and safe, but `set-password` (`charm.py:1294`) accepts arbitrary operator-supplied values.
- **Impact**: Confirmed for the sibling `update_user_password` method (see below); `create_user` has the identical pattern but was not directly exercised in this session because `set-password` calls `update_user_password`, not `create_user`, for existing users. `create_user` is used during relation creation, so if a relation ever supplies a user-specified password the same bug triggers.
- **Fix**: Use `psycopg2.sql.Literal(password)` for the password value, or pass it as a parameter via `%s` placeholders.
- **Linter rule**: "String interpolation of variables into SQL strings passed to `psycopg2.sql.SQL()`" — mechanically checkable with AST analysis.

### `update_user_password` concatenates password into SQL — confirmed breakage with `test'pass`
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/postgresql_k8s/v0/postgresql.py:837-839`
- **Evidence**:
  ```python
  SQL("ALTER USER {} WITH ENCRYPTED PASSWORD '" + password + "';").format(
      Identifier(username)
  )
  ```
  `password` is concatenated with `+` rather than passed as a parameter. Confirmed in deployment: `juju run postgresql-k8s/0 set-password username=operator password="test'pass"` produced:
  ```
  psycopg2.errors.SyntaxError: unrecognized role option "pass"
  LINE 1: ALTER USER "operator" WITH ENCRYPTED PASSWORD 'test'pass';
  ```
  The action failed gracefully with "Failed changing the password." — logged, no crash.
- **Impact**: An operator setting a password containing `'` via `set-password` gets a failed action. Not a security concern (the operator already has Juju admin access), but a reliability defect.
- **Fix**: Use `psycopg2.sql.Literal(password)` or a parameterised query. Alternatively, validate the password in the action handler and reject `'` (and other SQL-breaking characters) with a clear message.
- **Linter rule**: "String concatenation inside `SQL()`" — mechanically checkable with AST analysis of `psycopg2.sql.SQL` calls containing `+`.

### `cluster_members` is also a `cached_property`, freezing cluster topology after first call
- **Severity**: high
- **Kind**: bug
- **Where**: `src/patroni.py:334-337`
- **Evidence**:
  ```python
  @cached_property
  def cluster_members(self) -> set:
      """Get the current cluster members."""
      return {member["name"] for member in self.cluster_status()}
  ```
  Like `cached_cluster_status` (line 128), this is cached forever on the `Patroni` object. `charm.py:807-812` uses `self._patroni.cluster_members` to detect members added/removed (`if self._patroni.cluster_members == self._hosts`, `for member in self._hosts - self._patroni.cluster_members`). Since both the `Patroni` object (`charm.py:1655`) and `cluster_members` are `cached_property`, membership detection is frozen after the first call within a charm process lifetime.
- **Impact**: On a long-running charm process (`update-status` fires every 5 minutes), a unit could join or leave the cluster without the charm detecting it, leaving k8s endpoints stale and potentially causing connection routing errors.
- **Fix**: Same remedy as `cached_cluster_status` — remove `cached_property`, use a TTL cache, or invalidate explicitly on relevant events.
- **Linter rule**: "`cached_property` wrapping mutable/volatile external state queries" — mechanically checkable with AST analysis.

### Charm cannot self-recover from invalid config that crashes PostgreSQL
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:665-700` (`_on_config_changed`)
- **Evidence**: During the `experimental_max_connections` crash-loop, the charm could not process `config-changed` to apply a fix because the `postgresql` Pebble service never stabilized. The only recovery path was `juju config --reset` from outside, which re-renders the Patroni config without the bad value; this works because Patroni re-reads its YAML on restart, but would not work if Patroni didn't restart under a different `on-failure` policy.
- **Impact**: The operator must know to run `--reset`, which is not obvious from the charm's status (it just shows "Executing restart operation" / "awaiting for cluster to start").
- **Fix**: Validate `experimental_max_connections` (and similarly unbounded fields) against PostgreSQL's valid range in `build_postgresql_parameters()` or `update_config()` before rendering, and set `BlockedStatus` with an actionable message instead of rendering an invalid value.
- **Linter rule**: not mechanically checkable — requires domain knowledge of PostgreSQL parameter ranges.

### Patroni health check URL uses hardcoded HTTPS scheme when TLS is enabled
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:1830-1893` (`_postgresql_layer`)
- **Evidence**: The Pebble health check URL is `f"{self._patroni._patroni_url}/health"`, and `_patroni_url` returns `https://...` once `is_peer_data_tls_set` is True. During TLS setup/teardown there is a window where the health check scheme and the actual Patroni listener scheme are mismatched. Observed indirectly: k8s readiness probe showed 502 errors ("Readiness probe failed: HTTP probe failed with statuscode: 502") during the TLS rolling restart.
- **Impact**: Misleading readiness-probe failures during TLS transitions. The probe eventually stabilizes, but intermediate 502s could trigger unnecessary alerts.
- **Fix**: Align the Pebble health-check scheme with the actual Patroni listener state, or use a TCP-based check during transitions.
- **Linter rule**: not mechanically checkable.

### `cached_cluster_status` is a `cached_property` that never invalidates
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/patroni.py:128-130`
- **Evidence**:
  ```python
  @cached_property
  def cached_cluster_status(self):
      """Cached cluster status."""
      return self.cluster_status()
  ```
  `is_creating_backup` reads `self.cached_cluster_status`; because `Patroni` itself is a `cached_property` on the charm, the first `cluster_status()` result is cached for the lifetime of the `Patroni` instance. If a backup starts after that first call, `is_creating_backup` will never see it during that charm process's lifetime.
- **Impact**: The pre-upgrade check calls `is_creating_backup` to block upgrades during a backup. With a stale cache, an upgrade could proceed while a backup is in progress, risking a corrupted backup.
- **Fix**: Remove the `cached_property` decorator, convert to a TTL cache, or invalidate explicitly on backup start/end.
- **Linter rule**: "`cached_property` wrapping a method that returns mutable/volatile data" — mechanically checkable with AST analysis.

### `BlockedStatus` says "Configuration Error. Please check the logs" — unactionable
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:688`
- **Evidence**: On a `ValueError` from config validation, the handler sets `BlockedStatus("Configuration Error. Please check the logs")`. The actual message IS logged at ERROR level, but `juju status` shows nothing useful. E.g. `profile=invalid` produced this generic status while debug-log contained "Value not one of 'testing' or 'production'".
- **Impact**: Operators must run `juju debug-log` to understand a config error visible in the primary status UI.
- **Fix**: Include the validation error text in the status message: `BlockedStatus(f"Configuration Error: {e}")`.
- **Linter rule**: not mechanically checkable, but pattern-matchable for `BlockedStatus("Configuration Error. Please check the logs")`.

### `set-password` action is a silent no-op when the generated password matches the stored one
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:1288-1295`
- **Evidence**:
  ```python
  password = new_password()
  if "password" in event.params:
      password = event.params["password"]
  if password == self.get_secret(APP_SCOPE, f"{username}-password"):
      event.log("The old and new passwords are equal.")
      event.set_results({"password": password})
      return
  ```
  When no `password` parameter is given, `new_password()` generates a 16-char random string; the equality check is a defensive no-op guard, but if triggered the action succeeds without changing anything, contrary to operator intent.
- **Impact**: An operator running a security playbook to rotate credentials could get a false-success no-op.
- **Fix**: When no explicit password is supplied, loop `new_password()` until it differs from the stored secret, or remove the early-return equality check and unconditionally set the new password.
- **Linter rule**: not mechanically checkable.

### `on_deployed_without_trust` status may be overwritten (partial mitigation exists)
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:2513-2531` (`get_available_resources`), callers at `src/charm.py:598` and `src/charm.py:680`
- **Evidence**: `get_available_resources()` catches a 403 `ApiError` and calls `on_deployed_without_trust()`, setting `BlockedStatus("Insufficient permissions...")`. Both `_on_config_changed` (line 680) and `_on_peer_relation_changed` (line 598) call `update_config()` without checking its return value. In practice `_on_peer_relation_changed` guards with `if isinstance(self.unit.status, BlockedStatus): return` (line 601), and `_on_config_changed` only resets the "Configuration Error" status (line 690), so the insufficient-permissions status usually survives — but `_on_config_changed` proceeds to call `update_async_replication_data()` and `enable_disable_extensions()` after a failed `update_config()`, which could overwrite the status with `MaintenanceStatus`. This matches open issue #1404 ("Unit enters blocked 'Insufficient permissions' after pod deletion despite trust: true").
- **Impact**: The blocked status may be overwritten by subsequent maintenance/active status operations if other operations succeed despite missing k8s permissions.
- **Fix**: Check `update_config()`'s return value and return early if False; better, validate `--trust` once at startup rather than on every resource access.
- **Linter rule**: "bool-returning method call whose return value is not checked" — mechanically checkable with AST analysis.

### `parallel_patroni_get_request` uses `asyncio.run()` in a sync context
- **Severity**: low
- **Kind**: bug
- **Where**: `src/patroni.py:225`
- **Evidence**: `return run(self._async_get_request(uri, endpoints, verify))`. `asyncio.run()` creates a new event loop; if the charm ever has an existing running loop, this raises `RuntimeError: asyncio.run() cannot be called from a running event loop`. Currently the charm uses sync handlers so this is not triggered, but it is fragile.
- **Impact**: Blocks a future migration to async handlers.
- **Fix**: Use a synchronous HTTP client (`requests`) instead of `httpx` async, or refactor to an event-loop-aware runner.
- **Linter rule**: "`asyncio.run()` called outside a `__main__`-style entrypoint" — mechanically checkable.

### `_validate_config_options` risks `ExecError` on locale check
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:2394-2395`
- **Evidence**: `container.exec(["locale", "-a"]).wait_output()` can raise `ops.pebble.ExecError` if the container isn't ready. This is not caught by the `psycopg2.OperationalError` handler used elsewhere in `_on_config_changed`.
- **Impact**: During startup, before the workload container is ready, a `config-changed` event could raise an uncaught `ExecError`, causing a hook failure.
- **Fix**: Catch `ExecError` (and connection errors) in `_validate_config_options`, or guard the locale check with `container.can_connect()`.
- **Linter rule**: "`container.exec()` without a `container.can_connect()` guard" — mechanically checkable.

### `_validate_config_options` depends on PostgreSQL connectivity but the caller only anticipates `OperationalError`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:2367-2404` (`_validate_config_options`)
- **Evidence**: This method makes psycopg2 connections to validate `date_style`, `time_zone`, `default_text_search_config`, `group_map`, and `default_table_access_method`, and also runs `container.exec(["locale", "-a"])`. It raises `ValueError` for invalid config, but if PostgreSQL is unavailable it raises `psycopg2.OperationalError`, which `_on_config_changed` catches and defers on — though `_on_peer_relation_changed` also reaches this path via `update_config()`, and the locale check's `ExecError` (above) isn't caught at all.
- **Impact**: Config validation that requires a running database creates a circular dependency: you need the database to validate config, but invalid config can prevent the database from starting. Observed with `experimental_max_connections`, where the crash happens in `build_postgresql_parameters` before `_validate_config_options` ever runs.
- **Fix**: Split validation into "static" checks (pydantic bounds, formats) that run before config is rendered, and "dynamic" checks (require PostgreSQL) that run only once the database is confirmed up.
- **Linter rule**: not mechanically checkable.

### `charm.py` is 2819 lines
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py`
- **Evidence**: The main charm file handles config rendering, Pebble layer management, K8s resource creation, LDAP, backup coordination, extension management, password rotation, rolling restart, and status management.
- **Impact**: Code review and maintenance burden, though the team has already extracted `patroni.py`, `backups.py`, `config.py`, `upgrade.py`, `relations/`.
- **Fix**: Extract Pebble layer construction, K8s service/endpoint management, and extension handling into dedicated modules.
- **Linter rule**: "charm.py exceeds 1000 lines" — mechanically checkable.

### `_build_postgresql_parameters` checks `shared_buffers` against a max but not a min
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/postgresql_k8s/v0/postgresql.py:948-953`
- **Evidence**:
  ```python
  shared_buffers_max_value_in_mb = int(available_memory * 0.4 / 10**6)
  shared_buffers_max_value = int(shared_buffers_max_value_in_mb * 10**3 / 8)
  if parameters.get("shared_buffers", 0) > shared_buffers_max_value:
      raise Exception(...)
  ```
  Only the maximum bound is checked. If `memory_shared_buffers=0` passes through (which it does, per the pydantic v1 finding above), PostgreSQL receives `shared_buffers: 0`; PostgreSQL clamps this internally to its own minimum (16), so it doesn't crash but silently ignores the operator's config.
- **Impact**: Combined with the `Annotated`/pydantic issue, operators can set `memory_shared_buffers` below 16 with no error and no indication that PostgreSQL silently overrode it.
- **Fix**: Add a minimum check (`if parameters.get("shared_buffers", 0) < 16:`), ideally superseded once the pydantic-level fix lands.
- **Linter rule**: not mechanically checkable.

### `enable_disable_extensions` uses f-string for extension names in SQL
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/postgresql_k8s/v0/postgresql.py:461-463`
- **Evidence**:
  ```python
  cursor.execute(
      f"CREATE EXTENSION IF NOT EXISTS {extension};"
      if enable
      else f"DROP EXTENSION IF EXISTS {extension};"
  )
  ```
  Extension names are f-string interpolated rather than passed through `psycopg2.sql.Identifier()`. Names come from config keys (`plugin_<name>_enable`), not user input, so this isn't currently exploitable, but it's inconsistent with the rest of the codebase.
- **Impact**: Code smell today; would become an injection vector if extension names were ever user-controlled.
- **Fix**: Use `SQL("CREATE EXTENSION IF NOT EXISTS {}").format(Identifier(extension))` consistently.
- **Linter rule**: "f-string interpolation into SQL `execute()`" — mechanically checkable.

### `update_config` re-fetches node resources on every call
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:2297-2307` (`update_config`), `src/charm.py:2513-2531` (`get_available_resources`)
- **Evidence**: `update_config()` calls `get_available_resources()`, which makes 3 lightkube API calls (Pod, Node, container limits) every time. `update_config` is invoked from `_on_config_changed`, `_on_peer_relation_changed`, `_on_postgresql_pebble_ready`, and password changes — on a 3-unit cluster during startup this multiplies quickly.
- **Impact**: Extra load on the k8s API server during startup sequences; not observed to cause failures.
- **Fix**: Cache results with a short TTL, or invalidate on `upgrade-charm` events.
- **Linter rule**: "lightkube API calls in hot-path hook handlers without caching" — mechanically checkable.

### Test coverage gap: several critical modules under 75%
- **Severity**: low
- **Kind**: test-gap
- **Where**: coverage report
- **Evidence**: `src/relations/async_replication.py` 68%, `src/upgrade.py` 72%, `src/patroni.py` 67%, `src/charm.py` 72%, `src/relations/postgresql_provider.py` 68%, `src/authorisation_rules_observer.py` 41%. Many uncovered branches are error paths (switchover failures, upgrade rollback, API errors); unit tests skip async replication entirely (no second cluster in the test environment).
- **Impact**: Bugs in async replication or upgrade logic can cause data loss or split-brain; open issues #1204 and #1405 involve replication/upgrade edge cases that are poorly covered.
- **Fix**: Add scenario-based tests for switchover failure, upgrade rollback, and API error paths.
- **Linter rule**: not mechanically checkable.

### TLS relation shows "Provider relation data did not pass JSON Schema validation" warning
- **Severity**: low
- **Kind**: ux
- **Where**: debug-log: `certificates:4: Provider relation data did not pass JSON Schema validation`
- **Evidence**: During TLS setup with self-signed-certificates 1/edge, two such warnings appeared. TLS setup completed successfully afterwards; the message didn't identify the failed field or value.
- **Impact**: Unexplained warnings in debug-log can make an otherwise-working TLS setup look broken.
- **Fix**: Include the failed field/value in the log message, and log at DEBUG if the failure is expected/transient.
- **Linter rule**: not mechanically checkable.

### Use of `Harness` is deprecated
- **Severity**: nit
- **Kind**: lint
- **Where**: all `tests/unit/test_*.py` files
- **Evidence**: The test suite emits 1208 `PendingDeprecationWarning` messages for `ops.testing.Harness`, pointing to the `Scenario`-based testing guide.
- **Impact**: Will break when `ops` removes `Harness` in a future version.
- **Fix**: Migrate to `Scenario` (state-transition testing) — a significant effort given 381 test cases.
- **Linter rule**: "import of `ops.testing.Harness`" — mechanically checkable.

## Worth copying

- **Structured config via pydantic (`src/config.py`):** Comprehensive type-annotated config model with per-category validators. `plugin_keys()` and the `prefix_category_parameter` naming convention make plugin management straightforward. Reuse of typed bounds (`PgPositiveIntMax`, `WorkerProcessInt`, `SharedBuffersInt`, etc.) is a good pattern even though the pydantic-v1 gap undermines it in practice.
- **Clean reconciliation in `update_config()` (`src/charm.py:2297`):** Checks workload readiness, renders Patroni config, patches via API, handles TLS transitions, updates hashes — all in one coherent flow with clean deferrals.
- **`_patroni` cached_property (`src/charm.py:1655`):** Instantiated once and reused, avoiding re-reading secrets on every access.
- **Pebble health checks (`src/charm.py:1830`):** A Pebble health check on Patroni's `/health` endpoint feeds k8s readiness probes, and the URL updates when TLS is enabled/disabled.
- **Authorisation rules observer (`src/authorisation_rules_observer.py`):** Subprocess-based watcher for `pg_hba.conf` and user/group changes without polling, firing a custom charm event on change.
- **Dependency model for upgrades (`src/upgrade.py` / `src/dependency.json`):** `DependencyModel` with a JSON manifest tracks charm and rock versions for upgrade validation, consistent with other data-platform charms.
- **`override_patroni_on_failure_condition` / `restore_patroni_on_failure_condition` (`src/charm.py:2627`):** Temporarily overrides Pebble's on-failure condition during backup restores to stop the restart loop, then restores it — a clean pattern for crash-loop-prone maintenance operations.
- **Patroni config dual-file approach:** `/config/patroni.yaml` holds the DCS bootstrap template (Raft-based), while `/var/lib/postgresql/data/patroni.yml` is the rendered per-unit config — a clear separation of concerns.

## Common-practice notes

- **Data-platform conventions:** Uses `DataPeerData`/`DataPeerUnitData` for secrets, `TypedCharmBase` for typed config, `DataUpgrade` for upgrades, and a standard `src/` layout, with the library under `lib/charms/postgresql_k8s/v0/`.
- **Ops tracing enabled:** Imports `ops_tracing.Tracing` and logs trace IDs.
- **`assumes` block blocks Juju 4:** Declares `<4.0.0`, so the charm cannot deploy on Juju 4.x. Open issue #1615 confirms this is a real pain point. Repo CI tests against Juju 3.6 only.
- **Uses poetry + charmcraft 3 plugin:** `charmcraft.yaml` uses the `poetry` plugin with `charm-poetry` part naming, following charmcraft 3 conventions.
- **TLS integration delegates to `PostgreSQLTLS` library:** Delegates to `charms.postgresql_k8s.v0.postgresql_tls`, including a `tls_transfer` sub-module for CA certificate transfer between clusters for async replication.
- **Legacy interface support:** Maintains backward compatibility with the legacy `pgsql` interface (`db`/`db-admin`) alongside the modern `postgresql_client`, with a README warning against simultaneous use.
- **Secret handling uses both old and new paths:** `get_secret`/`set_secret` try `fetch_my_relation_field` (old databag) before falling back to Juju secrets — necessary for upgrades from old revisions but adds complexity.
- **`psycopg2` imported at module level:** A binary dependency that would `ModuleNotFoundError` on non-x86 architectures; the charm handles this with `sys.exit()` and a placeholder `WrongArchitectureWarningCharm` — the standard pattern for architecture-gated charms.

## Tests

- **Unit tests:** 381 passed, 9 skipped, 13-14s runtime, 75% coverage overall. Uses `Harness` (deprecated — 1208 `PendingDeprecationWarning` warnings). Coverage gaps: `authorisation_rules_observer.py` (41%), `patroni.py` (67%), `async_replication.py` (68%), `upgrade.py` (72%), `postgresql_provider.py` (68%), `charm.py` (72%).
- **Integration tests:** Extensive suite under `tests/integration/` covering HA (self-healing, replication, restart, upgrade, label migration), backups (AWS/GCP/Ceph + PITR), TLS, LDAP, storage, relations (legacy + modern), plugins, audit, pg_hba, password rotation, config, wrong-arch detection. Could not run in full on this VM without cloud credentials for backup tests.
- **Lint:** `ruff check` passes clean on `src/` and `tests/`. `tox -e lint` runs `ruff`, `codespell`, `shellcheck` — clean output (shellcheck was not installed locally, an environment gap, not a code issue).
- **Test gap:** no integration test for the `assumes`/Juju-version compatibility issue (open issue #1615 confirms real-world deployment problems on Juju 4.0.11).
- **Test gap:** `experimental_max_connections` (and other unbounded config fields) are not integration-tested with out-of-range values; such a test would catch the crash-loop issue directly.
- **Test gap:** no unit test for `cached_cluster_status`/`cluster_members` staleness — a test that creates a `Patroni` instance, reads a cached property, mutates cluster state, and re-reads would expose the bug.
- **Test gap:** `test_config_parameters` cannot pass for `Annotated`-based fields with pydantic v1.10.26 (see Findings).
- **Test gap:** no test for the TLS-event + bad-config interaction that sends the unit to `error` instead of `BlockedStatus`.

## Docs

- **README:** Clear, with deployment commands, relation examples, architecture overview. Covers both modern and legacy interfaces, OCI image sourcing, a security policy link, and prominently notes the `--trust` requirement.
- **Charmhub page:** Well-written description with links to docs, source, issues, website. Published on 14/stable (rev 925), 14/edge (rev 939), 16/stable, 16/edge, latest/stable channels.
- **External docs:** Linked to `https://canonical-charmed-postgresql-k8s.readthedocs-hosted.com/14/` — a substantial site with tutorials, how-to guides, and reference material.
- **terraform/README.md:** Documents the Terraform module for deploying the charm.
- **CONTRIBUTING.md:** Standard contribution guide with environment setup, testing instructions, code style.
- **Doc/reality match:** The README correctly states the `--trust` requirement, channels, and `assumes` constraints, and matched observed behaviour (`--trust` needed, 14/edge deployed correctly, TLS relations produced certificates, database relations produced credentials, refresh from 14/edge→14/stable worked). Discrepancies: (1) the README doesn't mention that the charm uses DCS failsafe mode — an important operational detail (a lost DCS quorum lets the cluster continue on a single node); (2) the blocked-status message on config error says "Configuration Error. Please check the logs" rather than the actual error; (3) the README doesn't document that `set-password` fails for operator-supplied passwords containing `'`, `"`, or `\`.

## Open questions

- **Is the `cached_cluster_status`/`cluster_members` staleness actually hit in production?** The `Patroni` object survives for the lifetime of the charm process, which normally spans many `update-status` events. An integration test verifying backup/membership detection during a long-running process would settle this.
- **Why does open issue #1404 report "Insufficient permissions" after pod deletion despite `--trust`?** The status-overwrite pattern described above may explain it — if the first post-recreation API call returns 403 before RBAC propagates, and a later successful call overwrites the blocked status.
- **What is the plan for Juju 4 migration?** The `assumes: <4.0.0` block combined with issue #1615 suggests the charm is actively blocked from Juju 4, and there's no Juju 4 CI workflow.
- **Should `experimental_max_connections` even exist as a config option?** It's marked `[EXPERIMENTAL]`; PostgreSQL's `max_connections` is normally derived from available resources rather than set directly. If it stays, it needs pydantic bounds.
- **Why does the CI integration test `test_config_parameters` appear to pass?** With pydantic 1.10.26, `Annotated[..., Field(ge=…)]` constraints are silent no-ops, so the test should fail for a large fraction of its cases. Possibilities: CI uses a different pydantic version, the test is actually red and unnoticed, or there's a validation layer not found in this review. Worth checking CI logs directly. *(unverified which of these is true)*
- **Is `durability_synchronous_commit=''` intentionally stored as `None`?** `juju config durability_synchronous_commit=''` stores `None` (the field is `str | None` and the `@validator` only runs on non-`None` values), which falls back to the default `"on"` — correct behaviour, but with no operator-visible confirmation that the default was restored.
