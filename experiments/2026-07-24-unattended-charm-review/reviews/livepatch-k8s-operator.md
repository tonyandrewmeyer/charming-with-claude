# canonical-livepatch-server-k8s

A mature, well-structured k8s charm for the Canonical Livepatch Server, but it has several
concrete failure modes that would surface in production: `schema-upgrade` leaves the unit stuck
in `WaitingStatus` forever; `_on_database_relation_broken` never refreshes the Pebble layer, so
the workload keeps running against a stale/dead database DSN; `juju refresh` does not update the
Pebble layer either, since `_on_upgrade_charm` skips it too; and on Juju 4.x the charm is
completely non-functional from the first hook — the bundled `ops-lib-pgsql` library calls the
`leader-get` binary, which Juju 4.x has removed from the charm execution environment, so every
`leader-elected` hook crashes and the unit never leaves `error`. A maintainer should fix the Juju
4.x blocker first (it is a hard deployment-time failure, not an edge case), then the two Pebble-layer
sync bugs (relation-broken and upgrade-charm), then the `schema-upgrade` status bug. The
plaintext resource-token storage and several config-validation gaps (log-level, swift storage,
non-string URLs) are real but lower urgency.

| | |
|---|---|
| Repo | canonical/livepatch-k8s-operator @ ac63148 (2026-07-23) |
| Charms | canonical-livepatch-server-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25, rev 50 edge) and concierge-k8s-4 (Juju 4.0.12, rev 50 edge) |
| Reviewed | 2026-08-19 |

## What it does

Canonical Livepatch Server is an on-prem patch server that receives kernel livepatches from
Canonical and distributes them to registered machines. It requires PostgreSQL for state,
optionally TimescaleDB for metrics, and integrates with `traefik-k8s` or
`nginx-ingress-integrator` for ingress, Tempo for tracing, an OpenTelemetry collector for
metrics, Grafana/Prometheus for observability, Loki for log forwarding, and an optional
`pro-airgapped-server` for air-gapped environments.

## Deployment log

**k8s-3 (Juju 3.6.25, primary deployment on rv-livepatch-2):**
1. `juju add-model rv-livepatch-2 --controller concierge-k8s-3`
2. `juju deploy postgresql-k8s --trust --channel stable` → rev 925, active
3. `juju deploy canonical-livepatch-server-k8s --channel edge` → rev 50, blocked on postgres
4. `juju integrate canonical-livepatch-server-k8s:database postgresql-k8s:database`
5. `juju config server.is-hosted=true server.url-template="..."` → active (05:17:20)
6. Schema tool ran in `livepatch-schema-upgrade` container (version 073)
7. `juju run schema-version` → migration-required: false
8. `juju run restart` → completed, no output, service confirmed restarted
9. `juju run schema-upgrade` → completed, unit went to `WaitingStatus("Schema migration done")` and stayed
10. Removed db relation: `juju remove-relation ...database` → Pebble layer still had the stale DSN (verified via `pebble plan`)
11. Service remained `active` despite holding a connection string to a non-existent database
12. Re-integrated db: new DSN correctly applied, service restarted
13. Tested `get-resource-token` action: requires `contract-token` arg (validation error without it), returns "failed to fetch the machine token" for unreachable URLs
14. k8s-4 (Juju 4.0.12, model rv-livepatch-k8s): unit immediately went to `error` with `hook failed: "leader-elected"`, stuck indefinitely

## Observed behaviour

- **Schema upgrade action bug**: `juju run canonical-livepatch-server-k8s/0 schema-upgrade` leaves the
  unit in `WaitingStatus("Schema migration done")` indefinitely. Confirmed on two deployments
  (rv-livepatch-k8s-3 and rv-livepatch-2). A subsequent config-changed hook clears it — an operator
  has no indication this is needed.
- **Db relation broken → Pebble layer retains stale DSN (runtime confirmed)**: After
  `juju remove-relation canonical-livepatch-server-k8s:database postgresql-k8s:database`,
  `pebble plan` in the livepatch container still showed:
  ```
  LP_DATABASE_CONNECTION_STRING: postgresql://relation_id_4:PlUCv4bNfE8mMux5@postgresql-k8s-primary.rv-livepatch-2.svc.cluster.local:5432/livepatch-server
  ```
  The service remained `active` (Pebble's `on-success` restart policy kept it running) with a
  connection string pointing to a non-existent database. The unit status showed
  `WaitingStatus("Schema migration done")` from the prior `schema-upgrade` action, not
  `BlockedStatus`. Re-integration correctly updated the Pebble layer to the new DSN (relation_id_5).
- **leader-elected on k8s-3 succeeds, no hook fires again for single unit**: `juju debug-log`
  confirmed that on k8s-3 (single unit), the leader-elected hook ran successfully (05:16:18) with
  no error. No subsequent leader-elected hooks fired for this unit.
- **leader-elected on k8s-4: `FileNotFoundError` for `leader-get`**: On k8s-4, the leader-elected
  hook crashes with `FileNotFoundError: [Errno 2] No such file or directory: 'leader-get'`. Root
  cause: Juju 4.x has removed the `leader-get`/`leader-set` CLI tools from the charm execution
  environment entirely. The `/var/lib/juju/tools/unit-*/` directory on k8s-4 contains 35 tools
  (`action-get`, `is-leader`, `secret-*`, etc.) but not `leader-get` or `leader-set`. On k8s-3
  (Juju 3.6.25) both tools are present. `ops-lib-pgsql` calls `leader-get` at
  `deps/pgsql/opslib/pgsql/client.py:697` with no fallback, causing an immediate crash.
- **leader-elected crash causes permanent error on k8s-4**: The hook retries every ~2 minutes and
  fails each time. `show-status-log` shows the pattern: `workload blocked` then `juju-unit error`
  on every retry. The unit is permanently non-functional.
- **leader-elected hook ordering**: The pgsql library registers
  `charm.on.leader_elected → _on_leader_change` at `deps/pgsql/opslib/pgsql/client.py:351`, before
  the charm's own handler (registered at `src/charm.py:93`). The pgsql handler fires first and
  crashes, so the charm's own handler never runs.
- **Invalid log level → hook failure**: `server.log-level="not-a-valid-level"` causes the
  livepatch server binary to exit immediately. `container.start()` raises a Pebble `ChangeError`,
  `config-changed` exits with code 1, unit goes to `error`. Recovery requires another config
  change. `"warning"` (instead of `"warn"`) causes the same failure.
- **Numeric config value → silent failure**: `juju config contracts.url=123` accepted by Juju,
  becomes `"123/v1/resources/..."` in the requests call. The action returns the generic "failed to
  fetch machine token" error, indistinguishable from a network failure.
- **`patch-storage.type=swift` → backoff restart loop**: livepatch binary exits code 0 on fatal
  config errors. Pebble's `start()` call succeeds, unit shows `active` briefly, then `error`.
  Service cycles in backoff indefinitely.
- **Other unvalidated config accepted without failure**: `patch-sync.interval=not-a-duration`,
  `contracts.password=not-base64!`, and `patch-sync.token=not-base64!` are all written to the
  Pebble layer as-is; the livepatch server handles these gracefully at runtime with no hook
  failure (unlike log-level and swift storage).
- **Pebble auto-restart**: Killing the livepatch-server process caused Pebble to restart it within
  ~2 seconds, unit staying `active`. No hook fired.
- **Unit recovery on Juju 3.x**: Units in `error` from a failed `config-changed` recover on a
  subsequent valid config change.
- **`juju relate` succeeds where `juju integrate` fails**: For `metrics-endpoint` and
  `grafana-dashboard` relations with grafana-agent-k8s, `juju integrate` returns "no candidates"
  but `juju relate` succeeds.
- **grafana-agent-k8s and loki-k8s**: Both integrate without affecting livepatch's Pebble layer.
  grafana-agent-k8s goes `blocked` (needs metrics backend). loki-k8s goes `blocked` (RBAC in test
  environment).
- **All four actions confirmed working**: `schema-version` (OK), `restart` (OK), `schema-upgrade`
  (leaves unit in `WaitingStatus`), `get-resource-token` (requires `contract-token` arg, generic
  error for unreachable URLs).
- **`emit-updated-config` action absent from rev 50**: Returns "action not defined" on deployed rev 50.
- **Deployed rev 50 missing features**: The deployed metadata has only 7 relations vs 12 in local
  ac63148. `ingress`, `send-otlp`, `metrics-db`, `cve-catalog`, `tracing` are all absent from rev 50.
- **`juju refresh` reports "already up-to-date"**: despite deployed rev 50 vs current edge rev 88
  (v2.2.0, per `juju info`). Unresolved — either rev 50 content matches rev 88's hash, or there is
  a `juju refresh` detection issue (unverified).
- **Scale-down and teardown clean**: `juju remove-unit` fires stop/remove hooks cleanly.
  `juju remove-application` cleanly fires `stop` hooks on all units.

## Findings

### Juju 4.x removed `leader-get`/`leader-set` — pgsql library crashes with `FileNotFoundError`

- **Severity**: critical
- **Kind**: bug
- **Where**: `deps/pgsql/opslib/pgsql/client.py:696-698` (`_leader_get`)
- **Evidence**: On k8s-4 (Juju 4.0.12), pod logs show the uncaught exception:
  ```
  FileNotFoundError: [Errno 2] No such file or directory: 'leader-get'
    File ".../pgsql/client.py", line 529, in _on_leader_change
      cur_lead_data = _get_pgsql_leader_data()
    File ".../pgsql/client.py", line 689, in _get_pgsql_leader_data
      return yaml.safe_load(_leader_get(LEADER_KEY) or "{}")
    File ".../pgsql/client.py", line 698, in _leader_get
      raise child_exception_type(errno_num, err_msg, err_filename)
  ```
  The charm agent's `/var/lib/juju/tools/unit-*/` directory on k8s-4 contains 35 tools
  (`action-get`, `is-leader`, `secret-*`, `state-get`, etc.) but no `leader-get` or `leader-set`.
  The same directory on k8s-3 (Juju 3.6.25) has both. `_leader_get` calls
  `subprocess.check_output(["leader-get", "--format=yaml", attribute])` with no exception handling
  and no fallback. The library registers `charm.on.leader_elected → _on_leader_change` at line 351,
  before the charm's own handler (`charm.py:93`), so the crash happens before the charm's handler
  runs. The hook retries every ~2 minutes; `show-status-log` confirms `workload blocked` then
  `juju-unit error` on every retry.
- **Why it matters**: The charm is completely non-functional on Juju 4.x from the first deploy. No
  operator action can resolve this. The affected `_on_leader_change` logic (mirroring app relation
  data for compatibility with the legacy PostgreSQL charm) is not needed for functionality — real
  connection handling goes through ops `DatabaseRequires` on the `database` relation, not the
  legacy `database-legacy` relation that uses pgsql.
- **Fix**: Either (a) remove the `database-legacy` relation and the pgsql library entirely, since
  `DatabaseRequires` on `database` works fine, or (b) update the pgsql library to use the ops
  leadership API instead of `leader-get`, or (c) wrap `_leader_get` in a try/except that falls back
  gracefully when the binary is absent.
- **Linter rule**: "Hook handlers must not assume external CLI tools exist without checking" — not
  mechanically checkable without explicit tooling awareness.

### `_on_database_relation_broken` does not update the Pebble layer — stale DSN retained (runtime confirmed)

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:826` (`_on_database_relation_broken`)
- **Evidence**: After `juju remove-relation canonical-livepatch-server-k8s:database
  postgresql-k8s:database`, `pebble plan` in the livepatch container showed:
  ```
  LP_DATABASE_CONNECTION_STRING: postgresql://relation_id_4:PlUCv4bNfE8mMux5@postgresql-k8s-primary.rv-livepatch-2.svc.cluster.local:5432/livepatch-server
  ```
  unchanged from before the relation removal. `_on_database_relation_broken` (lines 826-830) calls
  `_stop_service()`, `_clear_db_connection()`, and sets `BlockedStatus`, but does not call
  `_update_workload_container_config(event)`. `_clear_db_connection()` only clears
  `self._state.dsn` in peer-relation state (`state.py:697`), not the Pebble layer. Pebble's
  `on-success` restart policy immediately restarts the service with the stale DSN. The unit showed
  `WaitingStatus("Schema migration done")` (left over from an earlier action), not a status
  reflecting broken database connectivity. GitHub issue #121 covers this class of bug. Note that
  `_on_metrics_db_relation_broken` (line 819) does call `_update_workload_container_config(event)`
  — the `database-legacy` path is inconsistent with it.
- **Why it matters**: After removing the database relation, Livepatch keeps running with a
  connection string to a non-existent database — alive but with broken connectivity, and the unit
  status does not reflect this.
- **Fix**: Call `self._update_workload_container_config(event)` as the last line of
  `_on_database_relation_broken`, matching `_on_metrics_db_relation_broken`. Also note
  `_stop_service()` sets `WaitingStatus("service stopped")` which is immediately overwritten when
  Pebble restarts the service — disable Pebble's restart policy first if status tracking matters.
- **Linter rule**: "relation-broken handler must call `_update_workload_container_config` to sync
  the Pebble layer" — not mechanically checkable without runtime tracing.

### `_on_upgrade_charm` does not update the Pebble layer — `juju refresh` silently ignores config changes

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:247-253` (`_on_upgrade_charm`)
- **Evidence**: The `upgrade-charm` handler only calls `self.otel_metrics.publish()` (line 251);
  there is no call to `_update_workload_container_config` anywhere in it. When a new charm
  revision is deployed via `juju refresh`, the Pebble layer is not rebuilt. The integration test
  `test_upgrade.py` only checks `active`/`idle` status after refresh — it does not verify the
  Pebble layer was updated. The handler's own docstring (lines 248-255) acknowledges "juju refresh
  does not trigger any relation events on existing relations."
- **Why it matters**: If a new revision changes the Pebble layer (e.g. adds a required env var),
  that change is not applied on `juju refresh`. The service keeps running with the old layer
  indefinitely.
- **Fix**: Add `self._update_workload_container_config(event)` to `_on_upgrade_charm` (it may
  correctly defer if state is not ready).
- **Linter rule**: "upgrade-charm handler must update the Pebble layer" — not mechanically checkable.

### `schema-upgrade` action leaves unit permanently in `WaitingStatus` (runtime confirmed)

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:1041` (`schema_upgrade` action handler)
- **Evidence**: On deployed rev 50, `juju run canonical-livepatch-server-k8s/0 schema-upgrade`
  completed successfully but the unit immediately went to `WaitingStatus("Schema migration
  done")`. Confirmed on two independent deployments (rv-livepatch-k8s-3, rv-livepatch-2), stayed in
  `WaitingStatus` for over 5 minutes with no indication a subsequent hook is needed to clear it.
  `self.unit.status = WaitingStatus("Schema migration done")` is set unconditionally at line 1041
  after migration completes; the handler never sets `ActiveStatus`. The unit test
  `tests/unit/test_charm.py:311-312` asserts this `WaitingStatus` as the expected outcome, meaning
  the test locks in the bug rather than catching it.
- **Why it matters**: Running `schema-upgrade` leaves the unit looking unhealthy with no operator
  guidance; monitoring systems watching unit status will fire alerts.
- **Fix**: After migrations complete successfully, call `_update_workload_container_config(None)`
  (or otherwise set `ActiveStatus`) instead of leaving `WaitingStatus` set. Also fix
  `tests/unit/test_charm.py:311-312` to assert `ActiveStatus`.
- **Linter rule**: "Action handler must set unit to ActiveStatus after successful completion" —
  mechanically checkable by linting for absence of `ActiveStatus` after successful action completion.

### `patch-storage.type=swift` without required Swift config causes a backoff restart loop

- **Severity**: high
- **Kind**: bug
- **Where**: `config.yaml` (no validation); livepatch server binary (exits 0 on fatal config error)
- **Evidence**: `juju config canonical-livepatch-server-k8s patch-storage.type=swift` accepted with
  no validation. The livepatch binary read the config and exited with code 0 on the fatal error:
  ```
  param: required_if
  field_path: LivepatchConfig.PatchStorageConfig.SwiftUsername
  message: This field is required because Type is set to 'swift'
  ```
  Because the exit code is 0, Pebble's `start()` call succeeds (no `ChangeError`), and the hook
  completes. The unit briefly showed `active` (04:53:56) then `error` (04:53:57). Pebble's
  `on-success` restart policy cycled indefinitely (backoff 1 through 10+); `pebble services
  livepatch` confirmed state `backoff`. Recovery required fixing the config back to filesystem
  storage.
- **Why it matters**: The livepatch binary's exit-0-on-fatal-error behaviour means Pebble cannot
  detect the crash cleanly; the unit briefly shows `active` before entering an infinite restart
  loop with no operator guidance.
- **Fix**: Validate `patch-storage.type=swift`'s required fields (e.g. `SwiftUsername`) in
  `_update_workload_container_config` before writing the Pebble layer, and set `BlockedStatus`
  with a clear message if they are missing.
- **Linter rule**: "Storage type with required fields must validate those fields before applying
  config" — not mechanically checkable without running the livepatch server binary.

### No config validation for `server.log-level` — invalid values cause hook failure

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py` (log level passed directly to Pebble layer); `config.yaml` (no enum validation)
- **Evidence**: `juju config server.log-level=not-a-valid-level` accepted, written to the Pebble
  layer unvalidated. The livepatch binary rejected it at startup and exited; `juju status` showed
  `error` with `hook failed: "config-changed"`. `"warning"` (instead of `"warn"`) caused the same
  failure. README documents "warning" as valid — it is not.
- **Why it matters**: An operator setting "warning" (as the docs suggest) gets an opaque hook
  failure with the unit stuck in `error` and no clear recovery path.
- **Fix**: Validate `server.log-level` in `_update_workload_container_config` against the allowed
  set (debug, info, warn, error, dpanic, panic, fatal) and set `BlockedStatus` before restarting
  the service, or add a juju-schema enum to `config.yaml`.
- **Linter rule**: "Config options with enumerated values should have juju-schema enum validation"
  — not mechanically checkable without running the livepatch server binary.

### `resource_token` stored in plaintext in the peer relation app databag

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:1191` (`get_resource_token_action`); `src/state.py:61` (`State.__setattr__`)
- **Evidence**: `self._state.resource_token = resource_token` stores the token as
  `json.dumps(token)` in the peer relation app databag (`state.py:51`:
  `self._get_relation().data[self._app].update({name: v})`). Confirmed by GitHub issue #117. Any
  operator with `juju show-unit` or `juju debug-log` access can read the raw databag.
- **Why it matters**: The resource token is a sensitive credential and is exposed to all
  operators, not just the charm.
- **Fix**: Store the token via Juju secrets instead of the plain peer relation databag.
- **Linter rule**: "Sensitive credentials must not be stored in relation databags in plaintext; use
  Juju secrets" — mechanically checkable by scanning for `self._state` assignments of sensitive fields.

### `_update_trusted_ca_certs` catches broad `Exception` and proceeds as if it succeeded

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:1268`
- **Evidence**: `except Exception:` catches all exceptions from base64 decode and `exec`, logs an
  error, and returns. Control returns to `_update_workload_container_config`, which calls
  `_start_or_restart_service` and sets `ActiveStatus` even though the CA certificates were not
  updated.
- **Why it matters**: If `update-ca-certificates --fresh` fails, the service restarts with the
  same old certificates. Clients presenting new CA-signed certs will be rejected with no operator
  indication of the cause.
- **Fix**: Set `self.unit.status = BlockedStatus("Failed to update CA certificates")` in the except
  block and return early.
- **Linter rule**: "except Exception is too broad; catch specific exceptions" — mechanically
  checkable (ruff/pylint).

### `contracts.url` config accepts non-string values causing silent URL corruption

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:1183`; `config.yaml` (no type validation)
- **Evidence**: `juju config contracts.url=123` accepted. `self.config.get("contracts.url", "")`
  returns the integer `123`, interpolated into `f"{contracts_url}/v1/resources/..."` →
  `"123/v1/resources/..."`. The subsequent `requests` call fails, and `get-resource-token` returns
  the generic "failed to fetch machine token" error — indistinguishable from a network failure.
  pyright catches this at `src/charm.py:1183`.
- **Why it matters**: A numeric config value silently corrupts the contracts URL, and the error
  message is identical to a genuine network failure, making diagnosis impossible.
- **Fix**: Cast `contracts_url` to `str()` before use, or validate in the config handler.
- **Linter rule**: "Config values used in URL construction must be cast to str" — pyright catches
  this (`reportArgumentType`).

### `_stop_service` sets `WaitingStatus` immediately before Pebble restarts, masking the real state

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:690`
- **Evidence**: `_on_database_relation_broken` calls `_stop_service()`, which immediately sets
  `WaitingStatus("service stopped")`. Pebble's `on-success` restart policy immediately restarted
  the service with stale config; the unit showed `active` within seconds, not `WaitingStatus`.
- **Why it matters**: An operator checking `juju status` moments after a db-relation-broken hook
  fires sees `active`, even though the service is connecting to a non-existent database — the
  status is misleading.
- **Fix**: Do not set `WaitingStatus` after stopping the service unless Pebble's restart policy has
  first been disabled.
- **Linter rule**: "Status update must consider Pebble restart policy" — not mechanically checkable.

### `contracts.ca` config accepts non-string values, `b64decode` fails and is silently swallowed

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:1266`
- **Evidence**: pyright: `Argument of type "bool | int | float | str | None" cannot be assigned to
  parameter "s" of type "str | ReadableBuffer"` for `b64decode`. If `contracts.ca` is numeric,
  `b64decode` raises `TypeError`, and the broad `except Exception` (see above) swallows it, leaving
  the old CA cert in place with no indication.
- **Why it matters**: A bad CA certificate value fails silently.
- **Fix**: Cast `self.config.get("contracts.ca")` to `str` before passing to `b64decode`.
- **Linter rule**: "Config values used in `b64decode` must be validated as str or bytes" — pyright
  catches this.

### Schema-upgrade error handling can crash on `None` stderr

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:1046`
- **Evidence**: pyright: `"splitlines" is not a known attribute of "None"` at
  `e.stderr.splitlines()`. `pebble.ExecError.stderr` is typed `Optional[str]`; if `stderr` is
  `None`, calling `.splitlines()` raises `AttributeError`.
- **Why it matters**: If the schema-upgrade tool fails and returns `None` for stderr, the error
  handler itself crashes, leaving the unit in an inconsistent state.
- **Fix**: Guard with `if e.stderr: for line in e.stderr.splitlines():`.
- **Linter rule**: "Optional attribute access without null check" — pyright catches this
  (`reportOptionalMemberAccess`).

### `_get_available_cve_service` accesses `relation.app` without a null check

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:949`
- **Evidence**: pyright: `"get" is not a known attribute of "None"` at
  `relation.data.get(relation.app)`. `relation.app` is `Optional[Application]`; if the remote app
  is `None`, `.get()` raises `AttributeError`.
- **Why it matters**: If the `cve-catalog` relation exists with no remote app, the charm crashes
  with `AttributeError`, causing an error status.
- **Fix**: Add `if not relation.app: return None` before the `address =` line.
- **Linter rule**: "Optional attribute access without null check" — pyright catches this
  (`reportOptionalMemberAccess`).

### `_on_tracing_endpoint_changed` and `_on_otel_metrics_relation_created` missing null checks

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:886` and `src/charm.py:894`
- **Evidence**: `self.tracing.reqeuirer.requesting_protocols` and `self.otel_metrics.requester` are
  accessed without null guards. If the relation provides no protocols or endpoints, these accesses
  can fail.
- **Why it matters**: A crash in a relation-changed hook drives the unit into error status.
- **Fix**: Add null checks before accessing requirer/requester attributes.
- **Linter rule**: "Relation data access must check for None values" — not mechanically checkable
  without runtime tracing.

### Deployed rev 50 lacks multiple relations present in local head

- **Severity**: medium
- **Kind**: docs
- **Where**: `metadata.yaml` (local vs deployed)
- **Evidence**: Deployed rev 50 has only 7 relations; local ac63148 additionally has `ingress`
  (traefik-k8s), `send-otlp`, `metrics-db`, `cve-catalog`, `tracing`. The `ingress-interface`
  config option and `emit-updated-config` action are also absent from rev 50. `juju info` shows
  the edge channel is now rev 88 (v2.2.0), so rev 50 was current edge at deploy time but the
  channel has since moved.
- **Why it matters**: The README documents integrations (traefik-k8s ingress, OTLP metrics,
  TimescaleDB metrics, CVE catalog, tracing) that are not available in the deployed charm.
- **Fix**: Publish a newer revision to edge with these relations, or clearly version-gate the
  README documentation.
- **Linter rule**: not established

### No test for `on_leader_elected` handler

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py` (no test found for leader-elected)
- **Evidence**: `grep -n "leader_elected\|leader-elected" tests/unit/test_charm.py` returns no
  results. The `leader-elected` hook is critical — on Juju 4.x it crashes with `FileNotFoundError`,
  and even on Juju 3.x it can fail if the database connection is not ready.
- **Why it matters**: The interaction between the charm's `on_leader_elected` handler,
  `_update_workload_container_config`, and the pgsql library's `_on_leader_change` is an entirely
  untested critical path.
- **Fix**: Add a test covering: (1) the handler does not crash when state is not ready (should
  defer), (2) it calls `_update_workload_container_config` correctly when ready.
- **Linter rule**: not established

### No test for invalid `server.log-level` config

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py` (no test for log-level validation)
- **Evidence**: No test covers what happens with an invalid `server.log-level`. Real deployment
  showed this causes a hook failure and a non-recoverable error state until the next valid config
  change.
- **Why it matters**: Config validation is a high-risk area — an invalid log level crashes the
  service with no operator guidance.
- **Fix**: Add a test that sets an invalid `server.log-level` and verifies the charm sets
  `BlockedStatus` (not `ErrorStatus`) with a meaningful message.
- **Linter rule**: not established

### No test for `patch-storage.type=swift` without Swift config

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py` (no test for swift storage config)
- **Evidence**: No test covers `patch-storage.type=swift` without the required Swift config; real
  deployment showed this causes a backoff restart loop.
- **Why it matters**: The backoff loop is a silent failure mode — the unit shows `active` briefly
  before going to `error`, cycling indefinitely.
- **Fix**: Add a test that sets `patch-storage.type=swift` without Swift config and verifies the
  charm sets `BlockedStatus` with a message about missing Swift configuration.
- **Linter rule**: not established

### `ON_PREM_REQUIRED_SETTINGS` is always empty — dead code path

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:55`
- **Evidence**: `ON_PREM_REQUIRED_SETTINGS: Dict[str, str] = {}` is never populated. Line 525:
  `if self.config.get("server.is-hosted"): required_settings.update(ON_PREM_REQUIRED_SETTINGS)` is
  a no-op since the dict is empty, and the condition's polarity looks wrong — on-prem-required
  settings should presumably apply when `server.is-hosted=false`, not `true`.
- **Why it matters**: On-prem deployments get no additional config validation beyond
  `server.url-template`; the variable name implies validation that never actually happens.
- **Fix**: Either populate `ON_PREM_REQUIRED_SETTINGS` with the required on-prem config keys and
  fix the condition, or remove the dead code path.
- **Linter rule**: "Empty dict used in `.update()` call may indicate missing configuration" —
  mechanically checkable.

### pydantic deprecated `dict()` method in bundled `tempo_coordinator_k8s` library

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/tempo_coordinator_k8s/v0/tracing.py:879`
- **Evidence**: `PydanticDeprecatedSince20: The 'dict' method is deprecated; use 'model_dump'
  instead.` appears 10 times in test output, from
  `self.on.endpoint_changed.emit(relation, [i.dict() for i in data.receivers])`. This is in a
  bundled charm library, not the charm's own code.
- **Why it matters**: The library will break when Pydantic V3 lands; the deprecation warning
  pollutes every unit test run.
- **Fix**: Update the bundled `tempo_coordinator_k8s` library to use `model_dump()`.
- **Linter rule**: not established (bundled library, not mechanically checkable from charm code).

### Ruff finds unsorted imports

- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:9`
- **Evidence**: `ruff check src/` reports `I001 [*] Import block is un-sorted or un-formatted` at
  the first import block (lines 9-34).
- **Fix**: Run `ruff check --fix src/`.
- **Linter rule**: "Import blocks must be sorted by ruff" — mechanically checkable.

### `test_schema_upgrade_action__success` asserts the bug as correct behaviour

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:311-312`
- **Evidence**: `self.assertEqual(self.harness.charm.unit.status.name, WaitingStatus.name)` and
  `self.assertEqual(self.harness.charm.unit.status.message, "Schema migration done")` explicitly
  assert that after a successful `schema-upgrade` the unit is `WaitingStatus`. See the
  schema-upgrade finding above for the underlying bug.
- **Why it matters**: This test gives false confidence and would fail (correctly) once the bug is
  fixed, unless updated alongside.
- **Fix**: Change the assertion to `ActiveStatus` once the underlying handler is fixed.
- **Linter rule**: not established

### `test_restart_action__success` does not assert Pebble service state

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:243`
- **Evidence**: Test asserts `ActiveStatus` but does not verify the Pebble service was actually
  restarted.
- **Why it matters**: If `_start_or_restart_service` breaks, the test would still pass.
- **Fix**: Assert that `container.get_service(LIVEPATCH_SERVICE_NAME)` was actually restarted.
- **Linter rule**: not established

### `juju integrate` fails for `metrics-endpoint`/`grafana-dashboard` where `juju relate` succeeds

- **Severity**: low
- **Kind**: ux
- **Where**: Juju CLI (not charm code)
- **Evidence**: `juju integrate canonical-livepatch-server-k8s:metrics-endpoint
  grafana-agent-k8s:metrics-endpoint` returned `ERROR: no candidates`. The identical relation
  succeeded via `juju relate ... metrics-endpoint grafana-agent-k8s:metrics-endpoint`. Same pattern
  for `grafana-dashboard`.
- **Why it matters**: The README's examples use `juju integrate` throughout; following them
  literally fails.
- **Fix**: Investigate whether `juju integrate` requires different charm state than `juju relate`,
  or document `juju relate` as the working alternative. (unverified whether this is a charm or
  Juju CLI issue)
- **Linter rule**: not established

## Worth copying

- **Log redaction** (`src/log_redactor.py`): a logging filter/formatter scrubs passwords, tokens,
  connection strings, and sensitive env vars from all log output. Clean, extensible pattern worth
  adopting elsewhere.
- **Explicit env-var key management** (`src/charm.py:406-414`): an `explicit_keys` set ensures
  certain keys are always present in the env (as empty strings) even when unset, so removing a
  relation correctly clears the old value from the Pebble layer — better than relying on a filter.
- **`DeferError` exception class** (`src/charm.py:68`): a typed exception for signaling that an
  event should be deferred, as an alternative to inline `event.defer()` returns. Makes the
  deferral point explicit and testable.
- **`State` class** (`src/state.py`): a clean peer-relation-backed state manager using JSON
  encoding, with `is_ready()` guarding all state-dependent operations.
- **Alert rules via OTLP only** (`src/charm.py:165-173`): alert rules published exclusively via the
  `send-otlp` relation to avoid duplicate evaluation when both Prometheus and OTEL collector are
  present. Thoughtful observability design.
- **Schema version check in Pebble layer**: `livepatch-schema-tool check` runs on a 1-minute
  period, gating whether schema upgrades run. Prevents schema drift without a separate cron.
- **pgsql `_on_leader_change` conditional**: at `deps/pgsql/opslib/pgsql/client.py:528-537`, the
  library only calls `_mirror_appdata()` when there is existing leader data to migrate, otherwise
  it defers — a good pattern; the only issue is that `_leader_get` is called unconditionally
  within `_mirror_appdata` and crashes when the binary is absent.

## Common-practice notes

- **ops framework usage**: modern ops patterns (`CharmBase`, Pebble layer, Container API). All
  hooks registered via `self.framework.observe`. Status precedence handled.
- **Charm library versioning**: libraries bundled under `lib/charms/*` at specific versions,
  standard pattern. `tempo_coordinator_k8s` has the pydantic deprecation noted above.
- **Config structure**: namespaced with dots (e.g. `server.url-template`), a recommended modern pattern.
- **tox environments**: multiple integration environments (`integration-ingress`,
  `integration-metricsdb`, `integration-otlp`, `integration-airgapped`) reflect the charm's complexity.
- **pylint suppresses many issue classes**: `pyproject.toml` disables E0401, W1203, W0613, W0718,
  R0903, W1514, C0103, R0913, C0301, W0212, R0902, C0104, E1121, R0801, E1120, W0511, C0415,
  C0114 — a significant amount of suppression.
- **mypy misses pyright findings**: mypy is configured with `--follow-imports=skip
  --ignore-missing-imports` and finds 0 issues; pyright (with full type info) finds 15 real type
  errors. mypy's "0 issues" result is misleading under this config.
- **Juju 4.x removes leadership CLI tools**: `leader-get`/`leader-set` are present in Juju 3.x
  (`/var/lib/juju/tools/unit-*/leader-get`) but absent from Juju 4.x. Charms depending on these
  (like `ops-lib-pgsql`) crash on Juju 4.x; the ops framework's leadership API should be used instead.

## Tests

- **Unit tests**: 144 pass, 255 warnings (mostly `PendingDeprecationWarning` from Harness), 9
  subtests passed, in 1.69s. Coverage 85% overall (`charm.py` 85%, `utils.py` 72%,
  `legacy_constants.py` 91%, `log_redactor.py` 98%, `state.py` 100%, `constants.py` 100%). Key
  untested gaps: `database-relation-broken` when peer relation is unavailable (the actual crash
  scenario), `_update_trusted_ca_certs` failure path, `metrics-db-relation-broken` with
  `timescale_db.enabled=true`, `on_leader_elected` (completely untested — the Juju 4.x crash
  path), `test_schema_upgrade_action__success` asserting `WaitingStatus` as correct, invalid
  log-level config, `patch-storage.type=swift` without Swift config, `contracts.url` non-string
  values, and Pebble-layer sync in `_on_database_relation_broken`.
- **Integration tests**: `test_charm.py` (2 tests: wait for active + HTTP 200), `test_ingress.py`
  (nginx-route and traefik ingress via `self-signed-certificates`, `gateway-api-integrator`,
  `gateway-route-configurator` — the most thorough test, exercising both ingress interfaces with
  specific status assertions), `test_airgapped.py`, `test_otlp.py`, `test_timescale_db.py`,
  `test_upgrade.py` (tests `juju refresh` from stable to local charm but only checks
  status/HTTP, not the Pebble layer). `test_charm.py`'s integration tests wait for `active`/`idle`
  without strong behavioural assertions. Integration tests require `pytest-operator` and a
  matching Juju version — could not be run in this environment (Juju 3.6.1.3 python-libjuju vs
  Juju 4.0.12 controller).
- **Static analysis**: `bandit` — no issues. `ruff` — unsorted imports at `src/charm.py:9`. `mypy`
  — 0 issues (but `--ignore-missing-imports` hides real errors). `pyright` — 15 errors including 5
  concrete type-safety bugs at lines 949, 1046, 1183, 1266, 567.
- **Linting**: `tox -e lint` passes black, isort, pydocstyle, codespell, pflake8, mypy, pylint (10/10).
- **Harness deprecation**: `PendingDeprecationWarning` appears 255 times across all unit test runs.

## Docs

- **README.md**: comprehensive for the relations it documents, with correct `juju integrate`
  commands for the relations present in rev 50. Observed behaviour matches documented behaviour
  for those relations.
- **README/deployed-charm mismatch**: README documents `ingress` (traefik-k8s), OTLP metrics,
  TimescaleDB metrics, CVE catalog, and tracing relations — none present in deployed rev 50.
- **Doc/reality mismatch**: README says `server.log-level` accepts "debug, info, warning, error",
  but the binary uses Go-standard levels (debug, info, warn, error). "warning" crashes the server
  with a hook failure.
- **CONTRIBUTING.md**: standard template with PR checklist and test instructions.
- **charmhub description**: matches the README. Published on stable, beta, candidate, edge.

## Open questions

- **Juju 4.x leadership API**: the pgsql library uses `leader-get`/`leader-set` CLI tools, which
  Juju 4.x has removed. The fix is to update the library to use the ops leadership storage API.
  The `database-legacy` relation using pgsql is deprecated — the `database` relation (ops
  `DatabaseRequires`) does not need these tools. Removing `database-legacy` entirely would fix
  Juju 4.x compatibility while `ops-lib-pgsql` remains unmaintained.
- **pgbouncer SQLSTATE 42P05 (issue #96)**: not tested — no pgbouncer was deployed.
- **`juju refresh` "already up-to-date"**: `juju refresh canonical-livepatch-server-k8s --channel
  edge` said "already up-to-date" despite deployed rev 50 vs current edge rev 88. Either rev 50's
  content hash matches rev 88's, or there is a detection issue in `juju refresh` (unverified).
- **Traefik-k8s ingress and OTLP/tracing relations**: not testable against deployed rev 50 (the
  `ingress` relation is absent); would require a local pack with the latest code.
- **`juju integrate` vs `juju relate`**: `juju integrate` fails for `metrics-endpoint` and
  `grafana-dashboard` with grafana-agent-k8s while `juju relate` succeeds with identical arguments
  — may be a Juju CLI issue tied to specific interface types or charm state (unverified).
