# postgresql-single-kernel-library

A Python library (pip-installable as `postgresql-charms-single-kernel`) providing
shared charm logic for the Canonical PostgreSQL VM and K8s operators. It is
**not a standalone deployable charm** — it is consumed by `postgresql` (VM,
charmhub rev 1162) and `postgresql-k8s` (K8s, charmhub rev 925). The library is
mid-migration, consolidating two former codebases into a unified "single
kernel," and the evidence (TODO markers, stubbed handlers, unused manager code)
is everywhere. The architecture itself is sound — clean substrate abstraction,
sensible manager breakdown, a well-designed live-fetch TLS model — but it is
not finished. The most dangerous issues are a **password embedded in a
psycopg2 connection string** (leakable via PostgreSQL logs), **passwords
persisted in the `pg_subscription` catalog** (readable by any superuser),
**passwords concatenated into raw SQL** (log-leak and injection risk), and a
**hardcoded relative template path** that breaks when the library is used
outside a charm's working directory. Deployed and exercised in the 16/edge VM
charm (rev 1195) and K8s charm (rev 943), both ran successfully in this
review's tests. On K8s, the consuming charm still uses its own Pebble layer
code rather than the library's `K8sManager`, so a chunk of the library's K8s
path — including a `NotImplementedError` stub — is never hit in production.
The charm cannot deploy on Juju 4.x. A maintainer should fix the password
handling (findings 1–3) and the packaging path bug (finding 4) before the
next edge promotion; everything else can follow.

| | |
|---|---|
| Repo | canonical/postgresql-single-kernel-library @ `0832dd7` (2026-07-21) |
| Charms | postgresql (VM, rev 1162), postgresql-k8s (K8s, rev 925), postgresql-single-kernel (test placeholder only) |
| Substrate | library — consumed by both K8s and machine charms |
| Deployed | yes — concierge-lxd (Juju 3.6.23), postgresql 16/edge rev 1195 (VM, 2-unit cluster); concierge-k8s-3 (Juju 3.6.25), postgresql-k8s 16/edge rev 943 (K8s, single unit) |
| Deployed (Juju 4) | no — 16/edge charm metadata blocks Juju >= 3.5 |
| Reviewed | 2026-07-30 |

## What it does

Shared Python package under `single_kernel_postgresql/` with substrate-abstracted
PostgreSQL charm logic:

- **Charm skeletons** (`charms/`): `AbstractPostgreSQLCharm` base class with
  `PostgreSQLVMCharm` / `PostgreSQLK8sCharm` concrete subclasses.
- **Managers** (`managers/`): `ClusterManager` (password bootstrap, workload
  install), `ConfigManager` (Patroni YAML rendering, PostgreSQL parameter
  building), `PatroniManager` (REST API, cluster health, switchover),
  `TLSManager` (internal/operator TLS cert generation and push), `K8sManager`
  (Pebble layers).
- **Core state** (`core/`): `CharmState` — a single `ops.Object` aggregating
  pydantic-validated config, peer/app relation state, secrets, endpoint
  derivation, and status management.
- **Event handlers** (`events/`): `PostgreSQLEventsHandler` (install, start,
  leader-elected, pebble-ready), `TLS` (certificate requirers, live-fetch
  push), `TLSTransfer` (CA certificate transfer interface — never wired up).
- **Workload abstraction** (`workload/`): `BaseWorkload` with `K8sWorkload`
  and `VMWorkload`, plus substrate-specific `Paths`.
- **PostgreSQL client** (`utils/postgresql.py`, `compat/postgresql.py`):
  psycopg2-based client for database/user management, privilege grants,
  publication/subscription, and login-hook function generation.

The consuming charms import this package and use the appropriate concrete
charm class as their entry point.

## Deployment log

### VM deployment (concierge-lxd, Juju 3.6.23)

```
$ juju add-model rv-pg-deep -c concierge-lxd
$ juju deploy postgresql --channel 16/edge --storage data=1G --storage logs=1G --storage archive=1G --storage temp=1G
$ juju status
# ~6-7 min: install → start → active/idle

App         Version  Status  Scale  Charm       Channel   Rev  Exposed  Message
postgresql  16.14    active      1  postgresql  16/edge  1195  no

Unit           Workload  Agent  Machine  Public address  Ports     Message
postgresql/0*  active    idle   0        10.5.87.207     5432/tcp  Primary
```

- `juju config profile_limit_memory=0` → blocked, "Configuration Error. Please check the logs"
- `juju config profile_limit_memory=-1` → blocked, same message (pydantic `ge=128` constraint)
- `juju config profile_limit_memory=99999999` → blocked, same message (pydantic `le=9999999` constraint)
- `juju config --reset profile_limit_memory` → recovered to active
- `juju config profile_limit_memory=128` → active (valid value)
- `juju run postgresql/0 get-primary` → returned `postgresql/0`
- `juju run postgresql/0 pre-refresh-check` → returned refresh instructions
- `kill -9` on the Patroni process → snap auto-restarted, charm stayed active (no status change)
- `kill -9` on the PostgreSQL postmaster → Patroni restarted it within ~5 seconds, charm stayed active
- `juju add-unit postgresql` → second unit started, cluster formed with sync standby, streaming, lag 0

### TLS integration

```
$ juju deploy self-signed-certificates --channel edge
$ juju relate postgresql:client-certificates self-signed-certificates
$ juju relate postgresql:peer-certificates self-signed-certificates
```

- Certs, keys, CA bundles pushed to `/var/snap/charmed-postgresql/current/etc/patroni/`
- All files `0o600`, owned by `_daemon_:_daemon_`
- `patroni.yaml` reloaded via Patroni REST API (HTTP 202)
- `cluster_status` endpoint confirmed both client and peer TLS files present
- Live-fetch TLS model correctly reads certs from the requirer and pushes on every relation-changed

### K8s deployment (concierge-k8s-3, Juju 3.6.25)

```
$ juju deploy postgresql-k8s --channel 16/edge --storage data=1G --storage logs=1G --storage archive=1G --storage temp=1G
$ juju trust postgresql-k8s --scope=cluster
$ juju status
# ~5 min: pod start → trust → active/idle

App             Version  Status  Scale  Charm           Channel  Rev  Address        Exposed  Message
postgresql-k8s  16.14    active      1  postgresql-k8s  16/edge  943  10.152.183.56  no

Unit               Workload  Agent  Address    Ports  Message
postgresql-k8s/0*  active    idle   10.1.0.28         Primary
```

- Pebble services: `postgresql` (active), `metrics_server` (active), `pgbackrest_metrics_service` (active)
- The K8s charm **does not use the library's `K8sManager._postgresql_layer()`** — it has its own Pebble layer code in `src/charm.py` using `DATA_SOURCE_PASS`/`DATA_SOURCE_URI` instead of the library's `DATA_SOURCE_NAME`
- The library is present in the venv and its TLS code IS executed (log shows `single_kernel_postgresql.managers.tls:Internal peer CA generated`)

### Juju 4.x attempt (concierge-lxd-4, Juju 4.0.5)

```
$ juju deploy postgresql --channel 16/edge --storage data=1G
ERROR not supported Charm cannot be deployed because:
  - charm requires Juju version < 3.5.0, model has version 4.0.5
  - charm requires Juju version < 4.0.0, model has version 4.0.5
```

- 16/edge (rev 1195) metadata has `min-juju-version: 3.0.0` plus a constraint blocking 3.5+ and 4.x
- 16/stable (rev 1158) has the same constraint — neither single-kernel nor pre-migration versions support Juju 4

### Scale up/down

- Scale up: second unit installed in ~5 min, cluster formed leader + sync_standby
- Patroni cluster endpoint showed 2 members: `postgresql-0` (leader, running), `postgresql-1` (sync_standby, streaming, lag=0)
- Scale down: `juju remove-unit postgresql/1` removed cleanly, primary stayed active
- Remove application: `juju remove-application postgresql` tore down cleanly, storage detached, no errors

## Observed behaviour

### Startup timing
- VM install-to-active: ~6-7 minutes (install ~3 min, start/bootstrap ~2 min)
- K8s pod initialization to active: ~5 minutes (including image pull)

### Resource usage
- PostgreSQL process: ~213 MB RSS (single unit, idle)
- Patroni process: ~49 MB RSS
- Charmed-postgresql snap: ~394 MB total
- K8s pod: 2/2 containers, standard resource profile

### Config validation
- Values outside pydantic ge/le constraints produce `blocked` status
- The status message is always the generic "Configuration Error. Please check the logs" — the actual pydantic error (e.g. "Input should be greater than or equal to 128") only appears in `debug-log`
- Resetting to default recovers immediately to `active`

### Process resilience
- Killing Patroni: snap auto-restarted, charm stayed `active`, no hook fired
- Killing the PostgreSQL postmaster: Patroni restarted it within ~5 seconds, charm stayed `active`, no hook fired
- In both cases the charm never observed the failure — process monitoring is delegated entirely to snap/Patroni

### TLS
- Internal peer certificates generated on leader-elected
- Operator TLS (self-signed-certificates) correctly pushed to workload on relation-changed
- Files at correct VM paths with correct permissions (`0o600`)
- Patroni reloaded via REST API on TLS changes
- The K8s `/tmp/` fallback path (finding 6) was not triggered on VM — the correct path was used there
- On K8s, TLS code from the library IS executed (internal CA generation logged)

### Cluster behaviour
- Two-unit cluster formed correctly: leader + sync_standby
- Patroni REST `/cluster` showed both members with correct roles/states
- Replication lag was 0 on the sync standby
- Primary showed "degraded" during provisioning of the second unit, then recovered
- Scale-down was clean

### K8s-specific observations
- The library's `K8sManager._postgresql_layer()` is not used by the consuming K8s charm
- The K8s charm (rev 943) has its own `_postgresql_layer()` and `_update_pebble_layers()` in `src/charm.py`
- The K8s charm uses `DATA_SOURCE_PASS`/`DATA_SOURCE_URI` (separate password from URI) while the library uses `DATA_SOURCE_NAME` (password embedded in DSN)
- The library's K8s codepath — including `get_available_memory()`'s `NotImplementedError` — is not exercised in production today

### Juju 4 compatibility
- The consuming charm cannot deploy on Juju 4.x (metadata constraint blocks >= 3.5)
- This is a deployment blocker for operators on modern Juju

## Findings

### 1. Password passed as string interpolation in a psycopg2 connection string

- **Severity**: critical
- **Kind**: bug
- **Where**: `single_kernel_postgresql/compat/postgresql.py:186-188`
- **Evidence**:
  ```python
  connection = psycopg2.connect(
      f"dbname='{dbname}' user='{self.user}' host='{host}'"
      f"password='{self.password}' connect_timeout=1"
  )
  ```
- **Impact**: The password appears verbatim in the DSN. With `log_connections = on`
  (common in production) PostgreSQL will write the full connection string,
  including the password, to the server log. It's also inspectable via
  `pg_stat_activity` and psycopg2 debug output.
- **Fix**: Pass the password as a keyword argument —
  `psycopg2.connect(dbname=dbname, user=self.user, host=host, password=self.password, connect_timeout=1)`
  — which routes it through `PQconnectdbParams` without embedding it in the DSN.
- **Linter rule**: `psycopg2.connect` called with an f-string containing `password=` — mechanically checkable via AST pattern match.

### 2. Passwords persisted in the `pg_subscription` catalog

- **Severity**: critical
- **Kind**: bug
- **Where**: `single_kernel_postgresql/utils/postgresql.py:1205` (`create_subscription`) and `:1245` (`update_subscription`)
- **Evidence**:
  ```python
  Literal(f"host={host} dbname={db} user={user} password={password}"),
  ```
- **Impact**: `CREATE SUBSCRIPTION`/`ALTER SUBSCRIPTION` embed the password in the `CONNECTION` string, stored permanently in `pg_subscription.subconninfo`. Any superuser can read it; it survives restarts and is included in `pg_dump` output. Unlike finding 1 (log leak), this persists in the catalog.
- **Fix**: PostgreSQL's `CREATE SUBSCRIPTION` requires the password in the connection string — there is no parameterized alternative. Mitigate with a dedicated, minimally-privileged replication user or `pgpass`-based auth, and log a warning that the password is stored in the catalog.
- **Linter rule**: f-string containing `password=` inside `Literal()` in a SQL context — mechanically checkable.

### 3. Password concatenated into raw SQL in `create_user` and `update_user_password`

- **Severity**: critical
- **Kind**: bug
- **Where**: `single_kernel_postgresql/compat/postgresql.py:276`, `single_kernel_postgresql/utils/postgresql.py:1039`
- **Evidence**:
  ```python
  # compat/postgresql.py:276
  user_definition += f"WITH LOGIN{' SUPERUSER' if admin else ''}{' REPLICATION' if replication else ''} ENCRYPTED PASSWORD '{password}'"

  # utils/postgresql.py:1039
  SQL("ALTER USER {} WITH ENCRYPTED PASSWORD '" + password + "';").format(
      Identifier(username)
  )
  ```
- **Impact**: Both sites are preceded by `SET LOCAL log_statement = 'none'`, but the password remains in the SQL text and can surface via failed-statement error logs, `pg_stat_activity`, or query-inspecting extensions. A password containing a single quote will break the SQL syntax (or worse). The `update_user_password` case uses raw `+` concatenation rather than `psycopg2.sql.Literal()`, making it directly vulnerable to special characters.
- **Fix**: Use `%s` parameterized queries — `cursor.execute("ALTER USER %s WITH ENCRYPTED PASSWORD %s", (username, password))` — or at minimum `psycopg2.sql.Literal(password)`.
- **Linter rule**: password value in SQL string concatenation or f-string — mechanically checkable.

### 4. Hardcoded relative template path breaks pip-installed usage

- **Severity**: critical
- **Kind**: bug
- **Where**: `single_kernel_postgresql/managers/config.py:207`
- **Evidence**:
  ```python
  with open("templates/patroni.yml.j2") as file:
      template = Template(file.read())
  ```
- **Impact**: When installed as a pip package, the library's working directory is not the charm root. The `templates/` directory lives under the consuming charms, not the library package. This works today only because the consuming charm's own CWD happens to contain the template; the library will fail with `FileNotFoundError` in any other context.
- **Fix**: Ship the template as package data and load it via `importlib.resources`, or move it into the charm skeletons.
- **Linter rule**: `open()` in library code with a relative path containing `templates` — mechanically checkable.

### 5. Relative path for `refresh_versions.toml` in `VMWorkload`

- **Severity**: high
- **Kind**: bug
- **Where**: `single_kernel_postgresql/workload/vm.py:73-74`
- **Evidence**:
  ```python
  with pathlib.Path("refresh_versions.toml").open("rb") as file:
      revisions = tomli.load(file)["snap"]["revisions"]
  ```
- **Impact**: Same class of bug as finding 4. `refresh_versions.toml` ships in the charm root, not the library package; the relative path resolves incorrectly when the library is a pip-installed dependency elsewhere.
- **Fix**: Accept the path as a parameter from the consuming charm, or load via `importlib.resources` after shipping the file as package data.
- **Linter rule**: `open()` with a relative toml/path in library code — checkable.

### 6. Intentionally shortened health-check timeout left in production code

- **Severity**: high
- **Kind**: bug
- **Where**: `single_kernel_postgresql/managers/patroni.py:135`
- **Evidence**:
  ```python
  # TODO: Revert stop after delay to 60 and wait fixed to 7 after testing
  for attempt in Retrying(stop=stop_after_delay(1), wait=wait_fixed(1)):
  ```
- **Impact**: The Patroni health check retries for only 1 second instead of the intended 60. Where PostgreSQL takes several seconds to start (post-crash, slower hardware), `get_patroni_health()` raises `RetryError` after a single retry, and `member_started` returns `False`, so the charm never settles. Observed to start fine on fast SSD-backed VMs in this review; the 1-second window would fail on slower hardware.
- **Fix**: Change `stop_after_delay(1)` → `stop_after_delay(60)` and `wait_fixed(1)` → `wait_fixed(7)`.
- **Linter rule**: `Retrying` with `stop_after_delay(1)` in a non-test path — mechanically checkable.

### 7. Hardcoded `/tmp/` path for TLS CA bundle on K8s

- **Severity**: high
- **Kind**: bug
- **Where**: `single_kernel_postgresql/managers/patroni.py:101-103`
- **Evidence**:
  ```python
  else:
      # CA bundle is not secret
      self.verify = f"/tmp/{TLS_CA_BUNDLE_FILE}"  # noqa: S108
  ```
- **Impact**: On K8s the CA bundle path falls back to `/tmp/...`, which is volatile (lost on pod restart) and often world-readable. The explicit `# noqa: S108` suppression of bandit's hardcoded-tmp-path rule confirms this is a known workaround. Not exercised in production today because the K8s charm uses its own Pebble layer code, but the path remains in the library.
- **Fix**: Use the K8s TLS directory already defined in `K8sPaths.tls` instead of `/tmp`.
- **Linter rule**: `/tmp/` path in `managers/patroni.py` — project-specific.

### 8. `cluster_status()` disables TLS verification for cross-cluster queries

- **Severity**: high
- **Kind**: bug
- **Where**: `single_kernel_postgresql/managers/patroni.py:199-202`
- **Evidence**:
  ```python
  # TODO we don't know the other cluster's ca
  verify = not bool(alternative_endpoints)
  ```
- **Impact**: When `alternative_endpoints` is set (e.g. querying another cluster during async replication), TLS verification is disabled entirely — cross-cluster Patroni API traffic is vulnerable to MITM. The TODO acknowledges this is unresolved.
- **Fix**: Implement cross-cluster CA trust (e.g. exchange CA certs via the async replication relation), or at minimum warn prominently in logs and docs.
- **Linter rule**: TLS verification disabled in an API call — mechanically checkable.

### 9. Library-wide incomplete migration — many stubs and TODO markers

- **Severity**: high
- **Kind**: bug (incompleteness)
- **Where**: `events/postgresql.py:128-216` and scattered across 20+ files
- **Evidence**:
  - `events/postgresql.py:128` — `# TODO: Safeguard against refresh`
  - `events/postgresql.py:145` — `# TODO: Create pgdata`
  - `events/postgresql.py:176` — `# TODO: Check raft keys and initialize`
  - `events/postgresql.py:214` — `# TODO: Assert the member is up and running`
  - `managers/config.py:94-104` — five `# TODO add rel handler` stubs
  - `core/state.py:322` — `# TODO: This is temporary till data interfaces v1`
  - `managers/patroni.py:135` — `# TODO: Revert stop after delay to 60`
- **Impact**: The library is not feature-complete, yet the 16/edge charm ships with these paths active. The charm started and formed a cluster successfully in this review, but the TODO paths (refresh, pgdata bootstrap, raft init, member-startup check, LDAP, async replication, watcher) are either unimplemented or would fail if exercised.
- **Fix**: Complete the migration before cutting a stable release; add warning logs for incomplete paths if shipping in this state is intentional.
- **Linter rule**: TODO/FIXME in shipped library code — optional lint rule.

### 10. `TLSTransfer` is dead code, never wired into the charm

- **Severity**: high
- **Kind**: bug
- **Where**: `single_kernel_postgresql/events/tls_transfer.py:25-89`
- **Evidence**: `TLSTransfer` is defined but never imported or instantiated in production code — `abstract_charm.py` imports only `PostgreSQLEventsHandler` and `TLS`. The class calls `self.charm.set_secret()` and `self.charm.push_ca_file_into_workload()`, neither of which exists on `AbstractPostgreSQLCharm`. Only unit tests exercise it.
- **Impact**: The CA certificate transfer interface (`receive-ca-cert`) is declared in metadata but has no handler. Operators relating to a CA provider via `certificate_transfer` see no effect. If ever wired in as-is, it would raise runtime errors from the nonexistent method calls.
- **Fix**: Wire `TLSTransfer` into `AbstractPostgreSQLCharm` after implementing `set_secret` and `push_ca_file_into_workload`, or remove the dead code.
- **Linter rule**: class in production code only imported by tests — mechanically checkable.

### 11. `K8sManager` Pebble layer code is unused by the consuming K8s charm

- **Severity**: high
- **Kind**: bug (dead code in production path)
- **Where**: `single_kernel_postgresql/managers/k8s.py:60-122`
- **Evidence**: The K8s charm (rev 943) has its own `_postgresql_layer()` and `_update_pebble_layers()` in `src/charm.py`. Observed in deployment: the running pod's Pebble plan uses `DATA_SOURCE_PASS`/`DATA_SOURCE_URI` (charm code), not `DATA_SOURCE_NAME` (library code).
- **Impact**: The library's K8s path — including `get_available_memory()`'s `NotImplementedError` (finding 15), the monitoring password in Pebble env (finding 12), and the layer reconciliation logic — is not exercised in production, so bugs in it are latent. The migration is halfway: the K8s charm uses the library for TLS and state but not Pebble management.
- **Fix**: Complete the migration so the K8s charm uses the library's `K8sManager`, or remove the unused code.
- **Linter rule**: not mechanically checkable.

### 12. Monitoring password in Pebble layer environment variable

- **Severity**: high
- **Kind**: bug
- **Where**: `single_kernel_postgresql/managers/k8s.py:137-141`
- **Evidence**:
  ```python
  "DATA_SOURCE_NAME": (
      f"user={MONITORING_USER} "
      f"password={self.state.application.monitoring_password} "
      "host=/var/run/postgresql port=5432 database=postgres"
  ),
  ```
- **Impact**: The monitoring password is embedded in the Pebble layer as an environment variable, readable by anyone with container access (`pebble plan` or reading the plan file). Not exercised in production — the K8s charm (rev 943) uses `DATA_SOURCE_PASS`/`DATA_SOURCE_URI` instead — so this remains latent in the library's unused `K8sManager`.
- **Fix**: Inject the password via a Juju secret at runtime, or reference it from a file rather than embedding it in the env var. The consuming charm's approach (separate `DATA_SOURCE_PASS`) is better than the library's embedded-DSN approach.
- **Linter rule**: password in a Pebble layer environment variable in non-test code — mechanically checkable.

### 13. Charm does not deploy on Juju 4.x

- **Severity**: high
- **Kind**: bug
- **Where**: consuming charm metadata (not in this repo, but the library's primary consumer)
- **Evidence**: `juju deploy postgresql --channel 16/edge` on Juju 4.0.5 fails: "charm requires Juju version < 3.5.0" / "< 4.0.0". Both 16/edge (rev 1195, single-kernel) and 16/stable (rev 1158, pre-migration) have the same constraint.
- **Impact**: Operators on Juju 4.x cannot deploy the charm — a growing deployment blocker as Juju 4 adoption increases. The library itself has no Juju version constraint; its primary consumer does.
- **Fix**: Update the consuming charm's metadata to support Juju 3.5+/4.x after validating against the newer Juju APIs.
- **Linter rule**: not mechanically checkable.

### 14. Test coverage at 49%, well below the project's 70% target

- **Severity**: high
- **Kind**: test-gap
- **Where**: throughout — see open issue #59 ("Increase codecov coverage target 70.00%")
- **Evidence**: Coverage is weakest in the modules with the most business logic: `utils/postgresql.py` (47%), `compat/postgresql.py` (56%), `events/postgresql.py` (31%), `managers/cluster.py` (23%), `core/peer_relation.py` (57%), `core/relation_state.py` (27%), `managers/patroni.py` (67%, ~15 untested methods), `workload/vm.py` (40%).
- **Impact**: 31% coverage on `events/postgresql.py` means the install/start/leader-elected/pebble-ready lifecycle handlers are almost untested. 23% on `managers/cluster.py` means password bootstrap is mostly untested. 47% on `utils/postgresql.py` means the password-handling bugs (findings 2, 3) sit in largely untested code.
- **Fix**: Prioritise tests for `events/postgresql.py`, then `managers/cluster.py`, then `utils/postgresql.py`.
- **Linter rule**: not mechanically checkable.

### 15. `K8sWorkload.get_available_memory()` raises `NotImplementedError`

- **Severity**: high
- **Kind**: bug
- **Where**: `single_kernel_postgresql/workload/k8s.py:225-227`
- **Evidence**:
  ```python
  def get_available_memory(self) -> int:
      """Returns the system available memory in bytes."""
      raise NotImplementedError
  ```
- **Impact**: `ConfigManager._build_postgresql_parameters` calls `self.workload.get_available_memory()` unconditionally; on K8s this raises. Not currently hit because the K8s charm doesn't use the library's `ConfigManager.update_config()` path — but once the K8s migration completes and activates this path, it becomes a hard crash.
- **Fix**: Implement it for K8s (e.g. read cgroup memory limits), or return a safe default.
- **Linter rule**: `NotImplementedError` in a non-abstract method called from a hot path — mechanically checkable.

### 16. README is one line with no documentation

- **Severity**: high
- **Kind**: docs
- **Where**: `README.md`
- **Evidence**: The entire file is `# postgresql-single-kernel-library`.
- **Impact**: No information on what the package is, how it relates to the consuming charms, how to install/develop against it, or its architecture.
- **Fix**: Add a README covering purpose, relationship to `postgresql`/`postgresql-k8s`, install/usage, architecture, development guide, and links to upstream charm docs.
- **Linter rule**: README.md shorter than 200 bytes — mechanically checkable.

### 17. `PatroniManager.configure_patroni_on_unit()` bypasses the workload abstraction

- **Severity**: medium
- **Kind**: bug
- **Where**: `single_kernel_postgresql/managers/patroni.py:168,174,178`
- **Evidence**:
  ```python
  os.makedirs(patroni_data_path, exist_ok=True)          # line 168
  open(patroni_conf_file, "a").close()                    # line 174
  os.chmod(patroni_data_path, POSTGRESQL_STORAGE_PERMISSIONS)  # line 178
  ```
- **Impact**: Uses raw `os.makedirs`/`os.chmod`/`open()` directly rather than `BaseWorkload`, so it only works where the filesystem is local (VM), not on K8s where operations must go through Pebble push/pull. `ConfigManager` has a parallel, correctly-abstracted `configure_patroni_on_unit()` — the two are duplicates, one correct and one not.
- **Fix**: Remove the raw-OS version and delegate to the `ConfigManager` version.
- **Linter rule**: `os.makedirs`/`os.chmod` in manager code that also holds a workload reference — mechanically checkable.

### 18. Config validation error messages are too generic

- **Severity**: medium
- **Kind**: ux
- **Where**: `single_kernel_postgresql/core/config.py` (pydantic model) and the consuming charm's config-changed handler
- **Evidence**: `profile_limit_memory=0`, `=-1`, and `=99999999` all produce the identical status "Configuration Error. Please check the logs"; the actual pydantic error (e.g. "Input should be greater than or equal to 128") is only in `debug-log`. Observed in this review's deployment.
- **Impact**: No actionable feedback from `juju status` on ~150 config options with complex validation constraints; operators must dig into `debug-log`.
- **Fix**: Surface the pydantic validation message in the status, e.g. `"Configuration Error: profile_limit_memory must be >= 128"`.
- **Linter rule**: `BlockedStatus` with a generic "check the logs" message when a `ValidationError` is available — mechanically checkable.

### 19. `get_secret_from_id` catches and immediately re-raises

- **Severity**: medium
- **Kind**: lint
- **Where**: `single_kernel_postgresql/core/state.py:377-382`
- **Evidence**:
  ```python
  try:
      secret_content = self.model.get_secret(id=secret_id).get_content(refresh=True)
  except (SecretNotFoundError, ModelError):
      raise
  return secret_content
  ```
- **Impact**: The try/except does nothing — catches then immediately re-raises with no logging or transformation. Dead code.
- **Fix**: Remove the try/except, or add logging before the re-raise.
- **Linter rule**: try/except whose only handler is a bare `raise` — mechanically checkable.

### 20. `_default_encoder` in `RelationState` can leak complex objects

- **Severity**: medium
- **Kind**: bug
- **Where**: `single_kernel_postgresql/core/relation_state.py:104-110`
- **Evidence**:
  ```python
  if hasattr(o, "__dict__"):
      return vars(o)
  ```
- **Impact**: `vars(o)` dumps the entire `__dict__` of any object with one, including any that may hold passwords, keys, or TLS material. If such an object reaches `put_object()`, its full internal state serialises into the peer relation databag as JSON.
- **Fix**: Restrict the `vars()` fallback to a whitelist of known-safe types, or remove it and let `TypeError` propagate.
- **Linter rule**: `vars()` called in a JSON serialisation method — mechanically checkable.

### 21. Unit tests use deprecated `ops.testing.Harness`

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py:42`, `tests/unit/test_postgresql.py:44`
- **Evidence**: Every unit test fixture instantiates `Harness(...)`, producing `PendingDeprecationWarning: Harness is deprecated` (234 warnings observed).
- **Impact**: `ops` has deprecated `Harness` in favour of `Scenario`; the suite will break when `Harness` is removed.
- **Fix**: Migrate to `ops.testing.Scenario`.
- **Linter rule**: import of `ops.testing.Harness` — mechanically checkable.

### 22. No integration tests

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/` (no `tests/integration/` directory)
- **Evidence**: Test tree contains only `tests/unit/`; `tox.ini` defines only `lint` and `unit` environments.
- **Impact**: For a library handling complex state transitions (cluster bootstrap, TLS rotation, switchover, backup/restore), integration tests against a real Juju model would catch race conditions and integration bugs unit tests can't.
- **Fix**: Add integration tests for the VM and K8s test charms, or document that integration testing lives in the consuming charm repos.
- **Linter rule**: not mechanically checkable.

### 23. `ruff check` reports 81 issues in vendored `data_platform_libs`

- **Severity**: low
- **Kind**: lint
- **Where**: `single_kernel_postgresql/lib/charms/data_platform_libs/v0/data_interfaces.py`, `v1/data_models.py`
- **Evidence**: `ruff check` passes clean on the library's own code but finds 81 issues in the vendored code, including mutable default arguments, deprecated typing imports, collapsible ifs, and a hardcoded password string in a connection string (`data_interfaces.py:3681`).
- **Impact**: `data_interfaces.py:3681` has the same password-in-connection-string pattern as finding 1, shipped with the package though outside this project's direct control.
- **Fix**: Update the vendored libraries to their latest versions, or suppress lint rules for `lib/`.
- **Linter rule**: already caught by the existing `ruff` configuration.

## Worth copying

### Clean substrate abstraction pattern
`charms/abstract_charm.py` defines `AbstractPostgreSQLCharm` with three abstract
properties (`postgresql`, `workload`, `substrate`). VM and K8s subclasses each
provide substrate-specific implementations; the abstract base wires managers
and handlers once, and subclasses only plumb the substrate. A clean pattern
other multi-substrate charms should adopt.

### Live-fetch TLS model (cert/key never persisted)
`managers/tls.py` and `events/tls.py` implement a design where operator-provided
TLS certificates and keys are never persisted to charm state — they're read
live from the certificate requirer's `get_assigned_certificates()` on every
call. Only the CA is tracked in peer state for rotation (`current-ca` →
`old-ca`), documented at `events/tls.py:38-57` and consistently implemented.
Observed working in this review: certs from self-signed-certificates were
correctly pushed on relation-changed, and Patroni was reloaded. Should be the
standard pattern for all TLS-consuming charms.

### Comprehensive pydantic config model
`core/config.py` defines `CharmConfig` with ~150 typed, validated pydantic
fields covering every exposed PostgreSQL parameter, each with explicit ge/le
constraints. `keys()` and `plugin_keys()` classmethods provide useful
introspection.

### Path abstraction via pathops
`workload/paths/` defines a `Paths` abstract base with substrate-specific
`VMPaths` and `K8sPaths`. All file operations go through `BaseWorkload`
methods (`write_text`, `read_text`, `mkdir`, `exists`, `unlink`) wrapping
`pathops.PathProtocol`, giving a unified API across local filesystem (VM) and
Pebble container (K8s). Substrate-aware mode/owner methods (`tls_file_mode`,
`user`, `group`) are a good detail.

### Well-scoped TLS test suite
`tests/unit/test_tls_manager.py`, `test_tls_events.py`, `test_tls_state.py`,
and `test_tls_client_addrs.py` together give thorough, well-isolated coverage
of the TLS subsystem (100% on `events/tls.py`). Each test asserts a single
behaviour with proper mocking, covering happy path and edge cases.

### Status precedence via StatusHandler
`StatusHandler` from `data_platform_helpers.advanced_statuses` collects
statuses from all managers and resolves precedence, with each manager
defaulting to `[GeneralStatuses.ACTIVE_IDLE.value]`. A clean pattern for
multi-manager charms.

## Common-practice notes

### Follows ecosystem convention
- Uses `ops`' `Object` for event handlers, `CharmBase` for the charm skeleton, `Relation`/`Unit`/`Application` for state.
- Manager pattern (`BaseManager` with `get_statuses()`) follows `data-platform-helpers` conventions.
- Pydantic config validation via `data_platform_libs/v1/data_models.py` matches the data platform team's standard approach.
- `pyproject.toml` with `uv` build, `ruff` lint, `tox` test runner — matches current data platform conventions.
- CI uses `canonical/data-platform-workflows` reusable workflows.

### Drifts from convention
- The one-line README is well below the team's usual documentation standard.
- The library ships as a pip package (`uv_build` backend) rather than as `lib/charms/...` charm libraries — a deliberate architectural choice for this migration.
- The `lib/charms/data_platform_libs/` tree inside the package duplicates charm libraries also published independently.
- `pyproject.toml` classifier is `Development Status :: 3 - Alpha` — honest, but diverges from the team's typical "Production/Stable" classification for published charms.
- The K8s charm has not fully adopted the library — it uses it for TLS/state but keeps its own Pebble layer and config handling code (a partial migration state).

## Tests

- **Unit tests**: 234 passed, 10 skipped, 0 failures, ~0.92s. Run with `tox -e unit` or `uv run pytest tests/unit`.
- **Test structure**: `tests/unit/`, 17 files, covering the TLS subsystem, PostgreSQL client operations, config, config manager, Patroni manager (partial — ~18 of ~33 methods), architecture guard, filesystem utilities, locales, literals, and general utilities.
- **Test framework**: `pytest` with `ops.testing.Harness` (deprecated), parametrized by substrate (`vm`/`k8s` fixtures via `tests/conftest.py`).
- **Coverage gaps** (critical untested branches):
  - `events/postgresql.py` (31%): `_on_install`, `_on_start`, `_on_leader_elected`, `_on_postgresql_pebble_ready` all untested.
  - `managers/cluster.py` (23%): `configure_system_passwords`, `expose_ip_and_port`, `can_connect_to_postgresql` untested.
  - `managers/config.py` (76%): `_build_postgresql_parameters`, `update_config` untested.
  - `managers/patroni.py` (67%): ~15 untested methods including `bootstrap_cluster`, `get_standby_leader`, `get_sync_standby_names`, `promote_standby_cluster`, `restart_patroni`, `restart_postgresql`, `bulk_update_parameters_controller_by_patroni`, `ensure_slots_controller_by_patroni`, `primary_changed`, `reload_patroni_configuration`, `is_replication_hba_ready`, `is_member_registered_in_cluster`.
  - `compat/postgresql.py` (56%): user creation with roles, database creation with plugins, login hook, predefined catalog roles untested.
  - `workload/vm.py` (40%): `install_snap_package`, `temp_file`, `get_available_memory` untested.
  - `workload/k8s.py` (50%): `reconcile_pebble_layer`, `get_available_memory` untested.
- No integration tests, no spread tests, no scenario tests.
- **Lint**: `ruff check` passes clean on library code; `codespell` passes clean; `ruff check` finds 81 issues in vendored `data_platform_libs`.

## Docs

- **README.md**: one line — `# postgresql-single-kernel-library`. No description, architecture overview, install instructions, or development guide.
- **SECURITY.md**: present and reasonable, covers reporting process and links to Ubuntu disclosure policy.
- **Code docstrings**: generally good — `events/tls.py` has exemplary design-note docstrings explaining the live-fetch model, CA bundle composition, and SAN-trigger design.
- No `docs/` directory, no ADRs, no CONTRIBUTING.md.
- `pyproject.toml` `description`: "Shared and reusable code for PostgreSQL-related charms" — accurate but terse.
- **Charmhub**: not listed (not a charm). The consuming charms (`postgresql`, `postgresql-k8s`) have thorough charmhub/discourse docs, but nothing links back to this library.

## Open questions

1. **Is the 16/edge charm (rev 1195) stable enough for edge users?** It deployed successfully on both VM and K8s, formed a 2-unit cluster with sync replication, and handled TLS correctly. But the TODO density and incomplete migration paths (refresh, LDAP, async replication, watcher, raft bootstrap) suggest these features aren't ready, despite the honest Alpha classifier.

2. **What is the migration timeline?** The latest commit (`0832dd7`) adds peer-state config/user hash and TLS accessors — still scaffolding. The K8s charm still uses its own Pebble layer and config handling rather than the library's equivalents. TODO density suggests several more sprints of work.

3. **Will the template/path issues (findings 4, 5) be caught before pip-install use?** They're currently masked because consuming charms ship the required files in their own charm directories. They will surface if the library is used in a test or CI context outside a charm.

4. **Why is `TLSTransfer` dead code?** Fully written and tested but never wired into the charm, with a `receive-ca-cert` relation declared but unhandled. Intentional scope exclusion or oversight? (unverified)

5. **When will the K8s charm fully adopt the library's `K8sManager`?** Currently uses the library for TLS/state but keeps its own Pebble layer code, leaving `K8sManager` (with its `NotImplementedError` and password-in-env issues) unexercised in production.

6. **When will Juju 4.x be supported?** Both 16/edge (single-kernel) and 16/stable (pre-migration) block Juju >= 3.5. The library itself has no Juju version constraint, but its primary consumer cannot run on modern Juju — an increasingly critical deployment blocker.
