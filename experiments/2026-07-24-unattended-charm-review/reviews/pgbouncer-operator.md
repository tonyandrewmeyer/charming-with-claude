# pgbouncer-operator

A machine charm that deploys PgBouncer as a subordinate connection pooler in front of PostgreSQL. The code is generally clean and idiomatic (pydantic-based config, well-separated relation handlers, a documented upgrade path), and it deployed and ran correctly in the base case tested. But it ships a critical bug: destroying and recreating the principal subordinate relation permanently crashes the upgrade hook on all remaining units (`KeyError` in the bundled `data_platform_libs` upgrade library), leaving them stuck in `error` with no self-recovery. There is also a real base-compatibility gap — pgbouncer 1/edge only supports ubuntu@22.04/20.04 while postgresql 16/edge only supports ubuntu@24.04, so that combination cannot be deployed at all — and several smaller status/error-handling bugs. A maintainer should fix the upgrade-stack `KeyError` first (it causes permanent, unrecoverable outages on ordinary subordinate churn), then align base support between pgbouncer and postgresql 16, then work through the medium-severity status/exception bugs.

| | |
|---|---|
| Repo | `canonical/pgbouncer-operator` @ `fd640c4` (2026-07-21) |
| Charms | `pgbouncer` (machine charm, subordinate) |
| Substrate | machine (LXD VM) |
| Deployed | yes — `concierge-lxd` (Juju 3.6.27), postgresql 14/edge rev 1199, pgbouncer 1/edge rev 1070 (CharmHub), ubuntu 22.04 principal |
| Reviewed | 2026-08-18 |

## What it does

Deploys PgBouncer as a subordinate machine charm in front of a PostgreSQL backend (via the `postgresql_client` interface). Exposes database connections to client applications via the modern `database` (`postgresql_client`) interface and the legacy `db`/`db-admin` (`pgsql`) interfaces. Supports TLS, HA via hacluster, observability via grafana-agent/cos-agent, and tracing via the ops tracing library. Runs one pgbouncer instance per CPU core (capped at 2–4) when exposed, one instance otherwise. Configuration drives pool sizes derived from `max_db_connections`.

## Deployment log

**Deployment on `concierge-lxd` (Juju 3.6.27) with postgresql 14/edge on ubuntu@22.04 and pgbouncer 1/edge (CharmHub rev 1070) as subordinate to an ubuntu principal.**

```
juju add-model rv-pgb3 --controller concierge-lxd
juju deploy postgresql --channel 14/edge --base ubuntu@22.04
juju deploy pgbouncer --channel 1/edge --base ubuntu@22.04
juju deploy ubuntu --base ubuntu@22.04
juju relate pgbouncer:backend-database postgresql:database
juju relate pgbouncer:juju-info ubuntu:juju-info
```

PostgreSQL 14 reached `active` after ~5 minutes. The pgbouncer subordinate appeared within ~20 seconds of the juju-info relation, showed `maintenance / Installing and configuring PgBouncer` during snap install, then `active`. Scale-out via `juju add-unit ubuntu` caused a new pgbouncer subordinate to appear on the new machine.

**Base-compatibility failure: postgresql 16/edge (ubuntu@24.04) + pgbouncer** — pgbouncer 1/edge only supports ubuntu@22.04 and ubuntu@20.04 (per `juju info pgbouncer`); postgresql 16/edge only supports ubuntu@24.04 (per `juju info postgresql`). No valid base exists for this combination, so it could not be deployed.

**Juju 4 failure** — `juju deploy postgresql` fails on `concierge-lxd-4` (Juju 4.0.12) with "charm requires Juju version < 4.0.0". The machine postgresql charm cannot be tested on Juju 4 controllers at all.

**Upgrade hook crash** — When the principal (`juju-info` relation) is removed, subordinate units are destroyed and re-created. The new units (`pgbouncer/2`, `pgbouncer/3`) receive `upgrade-relation-changed` hooks, but the leader's upgrade stack still contains the destroyed unit IDs (`pgbouncer/0`, `pgbouncer/1`). The leader crashes with `KeyError: <ops.model.Unit pgbouncer/0>` at `data_platform_libs/v0/upgrade.py:987`, permanently putting both units into `error` state.

## Observed behaviour

- **Hook sequence on first relation**: `install → backend-database-relation-created → juju-info-relation-created → pgb-peers-relation-created → leader-elected → config-changed → start → backend-database-relation-changed (×3) → backend-database-relation-joined → juju-info-relation-joined → upgrade-relation-changed → pgb-peers-relation-changed`. Total ~35 seconds from principal relation to `active`.
- **Backend relation data**: postgresql 14/edge correctly implements `postgresql_client` on the `database` endpoint, setting `username`, `password`, `endpoints`, and `version` databag fields; `DatabaseRequires` fires `DatabaseCreatedEvent` correctly.
- **Invalid config**: `juju config pgbouncer max_db_connections=-5` caused `blocked / Configuration Error. Please check the logs`. Recovery was automatic on `max_db_connections=100`. The error logged as `ERROR Invalid configuration` with a traceback through `data_models.py → pydantic/__init__`.
- **Backend relation removal**: `juju remove-relation pgbouncer postgresql` caused `blocked / waiting for backend database relation to initialise`. Re-relating recovered to `active` within ~15 seconds.
- **Principal removal**: `juju remove-relation pgbouncer:juju-info ubuntu:juju-info` caused all subordinate units to be immediately destroyed. New units were created when the relation was re-added.
- **Principal scale-out**: `juju add-unit ubuntu` caused a new pgbouncer subordinate on the new machine; briefly `maintenance / Installing and configuring PgBouncer` during snap install, then `active`.
- **Actions**: `pre-upgrade-check` completed with return code 0; `set-tls-private-key` completed with return code 0.
- **Upgrade hook crash (observed)**: Both units ended in `error / hook failed: "upgrade-relation-changed"`. Traceback in `/var/log/juju/unit-pgbouncer-2.log`:
  ```
  File ".../data_platform_libs/v0/upgrade.py", line 987, in on_upgrade_changed
      top_state = self.peer_relation.data[top_unit].get("state")
  KeyError: <ops.model.Unit pgbouncer/0>
  ```
  `top_unit_id = self.upgrade_stack.pop()` returns `0`, but unit `pgbouncer/0` was destroyed and no longer exists in `self.peer_relation.data`.
- **Workload confirmed running (via SSH)**: `pgbouncer-pgbouncer@0.service` and `pgbouncer-pgbouncer-prometheus.service` both `active/running`; pgbouncer listening on `localhost:6432`. Instance config at `/var/snap/charmed-pgbouncer/27/etc/pgbouncer/pgbouncer/instance_0/pgbouncer.ini` shows `auth_type = scram-sha-256`, `pool_mode = session`, `max_db_connections = 100`, `auth_query = SELECT username, password FROM pgbouncer_auth_relation_7.get_auth($1)`.
- **Snap holds correctly**: `charmed-pgbouncer 1.21 / 27 / latest/stable / canonical / held` — pinned at revision 27, does not refresh.
- **Legacy `db`/`db-admin` relations**: `juju relate pgbouncer:db postgresql:db` returned `ERROR: no relations found` (same for `db-admin`); this could not be exercised end-to-end in this pass.

## Findings

### `upgrade-relation-changed` crashes with `KeyError` when subordinate units are destroyed and re-created

- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/data_platform_libs/v0/upgrade.py:987` (bundled library)
- **Evidence**: `juju remove-relation pgbouncer:juju-info ubuntu:juju-info` destroyed subordinate units `pgbouncer/0`/`pgbouncer/1`, replaced by `pgbouncer/2`/`pgbouncer/3`. The leader's upgrade stack still referenced the destroyed unit IDs. In `on_upgrade_changed`, `self.upgrade_stack.pop()` returned `0`, and `self.peer_relation.data[self.charm.model.get_unit("pgbouncer/0")]` raised `KeyError: <ops.model.Unit pgbouncer/0>`. Both units end up permanently `error / hook failed: "upgrade-relation-changed"`.
- **Impact**: Any removal and re-creation of a principal subordinate relation crashes the upgrade hook on all remaining units. They never recover without manual intervention — re-adding the relation does not fix it, because the new units still carry stale upgrade-stack data.
- **Fix**: Guard `on_upgrade_changed` to check whether `top_unit` still exists in `self.peer_relation.data` before accessing it, skipping it and rebuilding the stack if not. Alternatively, `build_upgrade_stack()` should only return currently-existing units. This affects any charm using this bundled library with subordinate scaling and should be fixed upstream in `data-platform-libs`.
- **Linter rule**: not mechanically checkable.

### `generate_relation_databases` uses loop-iteration variable as `auth_dbname`

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:751` (`add_wildcard` block at `src/charm.py:795`)
- **Evidence**:
```python
# src/charm.py:768–795
for relation in self.model.relations.get("db", []):
    database = self.legacy_db_relation.get_databags(relation)[0].get("database")
    if database:
        databases[str(relation.id)] = {"name": database, "legacy": True}

for relation in self.model.relations.get("db-admin", []):
    database = self.legacy_db_admin_relation.get_databags(relation)[0].get("database")
    if database:
        databases[str(relation.id)] = {"name": database, "legacy": True}
        add_wildcard = True  # <-- db-admin loop sets this

for rel_id, data in self.client_relation.database_provides.fetch_relation_data(
    fields=["database", "extra-user-roles"]
).items():
    database = data.get("database")  # <-- overwrites the db-admin loop's `database`
    ...
    if PERMISSIONS_GROUP_ADMIN in extra_user_roles or ...:
        add_wildcard = True

if add_wildcard:
    databases["*"] = {"name": "*", "auth_dbname": database, "legacy": False}  # line 795
```
`database` is whatever was last assigned by the client-relation loop. If `add_wildcard` was actually set by the earlier `db-admin` loop, but the client-relation loop ran after it, `database` at line 795 is the last client database name, not the admin database name.
- **Impact**: The `*` pgbouncer entry (wildcard access for admin users) may authenticate against the wrong database. Requires a specific relation ordering (db-admin present, client relation last) to manifest — untested whether this occurs in practice (unverified).
- **Fix**: Track the admin database name separately (e.g., `admin_database = database` in the `db-admin` loop) and use `admin_database` in the `add_wildcard` block.
- **Linter rule**: not mechanically checkable — requires value-flow analysis.

### `render_pgb_config` leaves the wrong status when config is invalid

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:857–860` (`render_pgb_config`)
- **Evidence**:
```python
def render_pgb_config(self, restart=False) -> None:
    initial_status = self.unit.status
    self.unit.status = MaintenanceStatus("updating PgBouncer config")

    if not self.configuration_check():
        return  # returns early WITHOUT restoring initial_status
```
When `configuration_check()` fails, the function returns without restoring `initial_status`, leaving `MaintenanceStatus("updating PgBouncer config")` instead of the prior status (which could be `BlockedStatus` or `ActiveStatus`). In `_on_config_changed` this is quickly corrected by a subsequent `update_status()` call, but Path A of `_on_database_created` has no such follow-up call.
- **Impact**: Operator sees "updating PgBouncer config" instead of "Configuration Error" when config is invalid, in the code paths lacking a later `update_status()`.
- **Fix**: Restore `self.unit.status = initial_status` before the early `return` when `configuration_check()` fails.
- **Linter rule**: not mechanically checkable — requires control-flow analysis.

### `render_prometheus_service` crashes when called with invalid config

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/relations/backend_database.py:210–212`, `src/charm.py:951–956`
- **Evidence**:
```python
# backend_database.py:212
self.charm.render_pgb_config()          # may return early if config invalid
self.charm.render_prometheus_service()  # called even if config invalid

# charm.py:951–956 (render_prometheus_service)
stats_password=self.get_secret(APP_SCOPE, MONITORING_PASSWORD_KEY),
listen_port=self.config.listen_port,    # ValueError if config invalid
metrics_port=self.config.metrics_port,  # ValueError if config invalid
```
In Path A of `_on_database_created`, if `render_pgb_config()` returns early due to invalid config, `render_prometheus_service()` is still called unconditionally and accesses `self.config.listen_port`/`metrics_port` without a prior `configuration_check()`, raising an unhandled `ValueError`. This can occur when config becomes invalid, a backend `endpoints-changed` event fires (invoking `render_pgb_config`), and a `database-relation-changed` event then fires Path A.
- **Impact**: A backend endpoint change while config is invalid crashes the hook with an unhandled `ValueError`.
- **Fix**: After calling `render_pgb_config()` in `_on_database_created`, check config validity before calling `render_prometheus_service()`, or guard the latter with its own `configuration_check()`.
- **Linter rule**: not mechanically checkable.

### Snap `hold()` has no timeout

- **Severity**: medium
- **Kind**: bug / performance
- **Where**: `src/charm.py:1038–1043` (`_install_snap_packages`)
- **Evidence**:
```python
SNAP_PACKAGES = [(PGBOUNCER_SNAP_NAME, {"revision": {"aarch64": "28", "x86_64": "27"}})]
# no "channel" key

if revision := snap_version.get("revision"):
    snap_package.ensure(snap.SnapState.Latest, revision=revision, channel=channel)  # channel=""
    snap_package.hold()  # no timeout, no error handling
```
`SNAP_PACKAGES` pins a revision with no channel (`channel=""` passed to `ensure()`). `hold()` is called with no timeout.
- **Impact**: On a slow or unreachable snap store, install could hang indefinitely and exceed the install hook timeout.
- **Fix**: Add a timeout to the hold call (e.g., `subprocess.run(["snap", "hold", ...], timeout=30)`), or document the snap-store connectivity requirement.
- **Linter rule**: not mechanically checkable.

### `PostgreSQLDeleteUserError` re-raised after status set in `relation-broken`

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/relations/pgbouncer_provider.py:273`
- **Evidence**:
```python
except PostgreSQLDeleteUserError as e:
    logger.exception(e)
    self.charm.unit.status = BlockedStatus(
        f"Failed to delete user during {self.relation_name} relation broken event"
    )
    raise  # re-raises — hook fails
```
- **Impact**: When a client relation is removed and user deletion fails, `relation-broken` fails; Juju marks the hook failed and retries, showing "hook failed" in `juju status`. Matches upstream issue #687. Behaviour is inconsistent with the legacy `db.py` path (`src/relations/db.py:446`), which logs and continues instead of re-raising for the same exception.
- **Fix**: Log the failure and set `BlockedStatus`, but do not re-raise, matching the pattern already used in `db.py`.
- **Linter rule**: not mechanically checkable.

### HA integration messages have typo "data-intgrator"

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:599`, `src/charm.py:603`, `src/charm.py:607`
- **Evidence**:
```python
self.unit.status = BlockedStatus("ha integration used without data-intgrator")    # line 599
self.unit.status = BlockedStatus("ha integration used without vip configuration") # line 603
self.unit.status = BlockedStatus("vip configuration without data-intgrator")      # line 607
```
- **Impact**: Confusing message in `juju status`.
- **Fix**: Replace `"data-intgrator"` with `"data-integrator"` in all three messages.
- **Linter rule**: `RUF001` (unusual-English check) would catch this if the correct spelling is in the dictionary.

### `_on_database_created` error message truncated

- **Severity**: low
- **Kind**: bug
- **Where**: `src/relations/backend_database.py:258`
- **Evidence**: `logger.error("deferring database-created hook - cannot monitoring hash password")`
- **Impact**: Grammatically broken log message, harder to grep.
- **Fix**: `"deferring database-created hook - cannot generate monitoring hash password"`.
- **Linter rule**: not mechanically checkable.

### `db.py` handles `PostgreSQLDeleteUserError` inconsistently with `pgbouncer_provider.py`

- **Severity**: low
- **Kind**: bug
- **Where**: `src/relations/db.py:446`
- **Evidence**:
```python
except PostgreSQLDeleteUserError:
    # We've likely lost connection at this point, and can't do anything about a
    # trailing user.
    logger.exception(f"connection lost to PostgreSQL - unable to delete user {user}.")
```
Logs and continues, unlike `pgbouncer_provider.py`'s re-raise for the same exception (see above finding).
- **Impact**: Legacy `db`/`db-admin` relations recover from this failure while the modern `database` relation's hook fails permanently.
- **Fix**: Apply the `db.py` pattern (log, don't re-raise) to `pgbouncer_provider.py`.
- **Linter rule**: not mechanically checkable.

### Hardcoded version `"3"` instead of a named constant

- **Severity**: low
- **Kind**: lint
- **Where**: `src/upgrade.py:43`
- **Evidence**:
```python
"dependencies": '{"charm": {"dependencies": {"pgbouncer": ">0"}, "name": "postgresql",
    "upgrade_supported": ">0", "version": "3"}, ...}'
```
- **Impact**: Magic number that could drift silently.
- **Fix**: Define as a named constant, e.g. `POSTGRESQL_UPGRADE_VERSION = "3"`.
- **Linter rule**: not established.

### Auth query uses relation-derived schema name, suppressed with `noqa`

- **Severity**: low
- **Kind**: lint / security
- **Where**: `src/relations/backend_database.py:483`
- **Evidence**: `return f"SELECT username, password FROM {self.auth_user}.get_auth($1)"  # noqa: S608`
- **Impact**: `auth_user` is dynamically derived from the relation username (e.g. `pgbouncer_auth_relation_3`), not a constant; ruff's `S608` (possible SQL injection via string formatting) is suppressed rather than resolved.
- **Fix**: If the schema always equals `auth_user` by design, document that this is intentional; otherwise avoid the dynamic interpolation.
- **Linter rule**: `S608` — flagged, currently suppressed via `noqa`.

### Deprecated `ops.testing.Harness` throughout test suite

- **Severity**: low
- **Kind**: tech-debt
- **Where**: all test files under `tests/unit/`
- **Evidence**: Every test file imports `from ops.testing import Harness`; deprecation warnings fire on every test run (174 warnings observed).
- **Impact**: Noisy test output; charm is not on the modern `ops-scenario` testing API.
- **Fix**: Migrate to `ops-scenario` or the current harness API.
- **Linter rule**: not mechanically checkable (runtime deprecation warning, not lint-detectable).

### Typo "in in" in `metadata.yaml` description

- **Severity**: low
- **Kind**: docs
- **Where**: `metadata.yaml:10`
- **Evidence**: `"This charm supports PgBouncer in in bare-metal/virtual-machines."`
- **Impact**: Cosmetic error in published charm metadata.
- **Fix**: `"This charm supports PgBouncer in bare-metal and virtual-machines."`
- **Linter rule**: not mechanically checkable.

## Worth copying

- **`CharmConfig` (`TypedConfigModel`)** — `src/config.py`: clean pydantic-based structured config (`PositiveInt`, `conint(ge=0)`, `Literal`, `IPvAnyAddress`).
- **Upgrade stack ordering** — `src/upgrade.py:64–70`: `build_upgrade_stack` builds an ordered unit list, self first then peers, ensuring the leader upgrades last.
- **Status precedence guard** — `src/charm.py:581–586`: a guard against clearing specific blocking statuses; worth standardising across charms.
- **Secret migration path** — `src/charm.py:299–318`: handles both old-style databag secrets and new-style Juju secrets, with `SECRET_KEY_OVERRIDES` for migration.
- **HA virtual IP handling** — `src/relations/hacluster.py`: clean abstraction over the hacluster relation with proper JSON resource-parameter encoding.
- **Extensive ASCII diagrams in relation docstrings** — `src/relations/backend_database.py`, `src/relations/db.py`, `src/relations/pgbouncer_provider.py`: docstrings show exactly what data flows over each relation.
- **Conditional Python-version dependencies** — `pyproject.toml`: focal (Python 3.8) vs noble (Python 3.10+) handled cleanly.

## Common-practice notes

- **Source layout**: uses `src/` directly (not `src/charms/<name>/`) — slightly non-standard but acceptable; confirmed by `PYTHONPATH="src:lib"` in tests.
- **Library versioning**: libraries under `lib/charms/` aren't versioned in `v0/` subdirectories for all libs — the charm bundles its own copies rather than depending on charmhub-published libs. Heavy (~7,000 lines bundled: `pgbouncer_k8s`, `postgresql_k8s`, `data_platform_libs`, `tls_certificates_interface`, `grafana_agent`, `operator_libs_linux`) but avoids external dependency-availability issues.
- **`single_kernel_postgresql` dependency**: `INVALID_DATABASE_NAME_BLOCKING_MESSAGE` and `INVALID_EXTRA_USER_ROLE_BLOCKING_MESSAGE` are imported from `single_kernel_postgresql.compat.postgresql` (version 16.3.4), not from the charm's own `constants.py` — opaque external constants the charm doesn't control.
- **ops framework usage**: `TypedCharmBase` (`data_platform_libs.v0.data_models`), `Tracing` (`ops_tracing`), `COSAgentProvider` (`charms.grafana_agent.v0.cos_agent`) — modern ops 3.x pattern.
- **Config-driven instances**: `instances_count` dynamically computes pgbouncer instance count from CPU count and exposure state.
- **Upgrade handling**: uses `charms.data_platform_libs.v0.upgrade.DataUpgrade` base class with a snap refresh in `_on_upgrade_granted`, and pinned snap holds — canonical pattern for machine charms (but see the `KeyError` finding above).

## Tests

- **Unit tests**: 70 tests across `test_charm.py`, `test_upgrade.py`, `test_utils.py`, and 6 relation test files. All pass, with 174 deprecation warnings (Harness and other ops deprecations). Runs in 0.47s.
- **Test coverage gaps**:
  - No test for `update_status()` when `configuration_check()` returns False (the status-overwrite scenario).
  - No test for `generate_relation_databases()` with `db`-only relations plus admin perms (the `auth_dbname` dangling-variable bug).
  - No test for HA status precedence.
  - No test for `upgrade-relation-changed` when units have been destroyed (the `KeyError` crash).
  - Snap `hold()` timeout issue is not testable under full mocking.
  - `PostgreSQLDeleteUserError` re-raise in `relation-broken` is not tested.
  - No test for `render_prometheus_service()` crashing on invalid config.
- **Integration tests**: under `tests/integration/`; CI runs on LXD with `spread.yaml` (concierge). `test_build_and_deploy` relates `pgbouncer:backend-database` to `postgresql:database` and waits for blocked-then-active. CI builds the postgresql machine charm locally via `charmcraftcache pack` (from the postgresql-operator repo) rather than using the CharmHub-published version — likely why CI passes while testing against the published postgresql charm surfaced the base-compatibility gap.
- **CI**: `ci.yaml` on PRs, `integration_test.yaml` on schedule; tests against juju 3.6/stable with `POSTGRESQL_CHARM_CHANNEL=14/edge` and a `16/edge` variant on juju 3.6. Uses locally built charms, not CharmHub charms.

## Docs

- **README.md**: comprehensive usage guide with config option explanations.
- **docs/how-to/h-enable-monitoring.md**: describes grafana-agent integration, metrics port, cos-agent relation; appears accurate.
- **docs/tutorial/t-deploy-charm.md**: step-by-step tutorial with correct commands.
- **docs/explanation/e-legacy-charm.md**: explains old vs new pgbouncer machine charm — good context.
- **docs/explanation/e-statuses.md**: documents possible status messages.
- **CharmHub description**: states the charm is "only compatible with the data platform postgresql-operator charm" — accurate for postgresql 14/edge, but postgresql 16/edge + ubuntu@24.04 cannot be paired with pgbouncer (no ubuntu@24.04 base), and postgresql doesn't deploy on Juju 4.x at all; this is not called out in the description.
- **Upgrade docs (issue #677)**: reference a `resume-upgrade` action that does not exist in the charm's `actions.yaml`.
- **Terraform module**: not present in the repo.

## Open questions

1. **Does the CharmHub postgresql 16/edge machine charm implement `postgresql_client` correctly?** Confirmed working for postgresql 14/edge on ubuntu@22.04; postgresql 16/edge + ubuntu@24.04 cannot be tested because pgbouncer 1/edge has no ubuntu@24.04 base. A locally built pgbouncer with an ubuntu@24.04 base would settle this.
2. **Does the snap `hold()` call ever actually time out in practice?** No enforced timeout exists; behaviour under constrained snap-store connectivity is untested.
3. **What is the intended behaviour of the documented `resume-upgrade` action?** Issue #677 notes it's documented but not implemented — should be removed from docs or added to the charm.
4. **Is the `auth_dbname` dangling-variable bug reachable in real deployments?** It requires db-admin relations combined with a later-evaluated client relation loop; if client relations are always related before db-admin in practice, this may not trigger (unverified).
5. **Should the destroyed-unit `KeyError` fix land in the charm or upstream in `data-platform-libs`?** The upgrade stack is persisted in peer relation data but never pruned when units are destroyed; this affects every charm using this bundled library with subordinate scaling.
