# Charmed PostgreSQL (postgresql-operator)

A mature, carefully engineered machine charm for PostgreSQL 14/16 built on the
`charmed-postgresql` snap, Patroni for HA, pgBackRest for S3 backups, and a
RAFT-replicated peer databag. Deploy, TLS integration, client integration,
config validation, rolling restarts, failure recovery, and 2→3→2 scaling all
worked in a live 3.6.27 deployment. The charm is in good shape; the findings
below are mostly validation gaps, a couple of self-healing gaps, and one
uncaught-exception log-noise bug, none of which broke the running cluster.
First things to fix: stop silently accepting invalid
`experimental_max_connections`, and add a `stop`/remove handler so scale-down
isn't a slow Juju-driven teardown (see #1550).

| | |
|---|---|
| Repo | canonical/postgresql-operator @ `8a9170368a426f7658dc3a87fdc8579cd8ce3e80` (2026-07-22) |
| Charms | postgresql |
| Substrate | machine |
| Deployed | yes — concierge-lxd (juju 3.6.27), `14/edge` rev 1199 (published 2026-07-29, ~1 week ahead of local HEAD) |
| Reviewed | 2026-08-15 |

## What it does

Machine charm deploying PostgreSQL from the revision-pinned `charmed-postgresql`
snap (rev 392/393, version 14.23 — see `src/constants.py:45-50` and
`src/dependency.json`). HA is provided by Patroni with a built-in PySyncObj RAFT
DCS (port 2222), with synchronous replication (`synchronous_mode: true`,
`sync_standby_names: "*"`). It exposes `database`/`db`/`db-admin` client relations,
`certificates` + `receive-ca-cert` for TLS, `s3-parameters` for pgBackRest backups,
`ldap`, `tracing`, and cross-cluster async replication (`replication` /
`replication-offer`). The config surface is ~190 typed options (most are bounded
pydantic types) mapping onto `postgresql.conf`/Patroni parameters.

Notable architecture: a background `cluster_topology_observer.py` process polls the
Patroni REST API every 30 s and dispatches synthetic `cluster_topology_change` /
`databases_change` events through `juju-exec`; peer secrets live in Juju secrets via
`data_platform_libs`' `DataPeerData`, with legacy databag fallback; restarts are
serialised through `RollingOpsManager` on a dedicated `restart` peer relation.

## Deployment log

Controller `concierge-lxd` (juju 3.6.27); the repo's `assumes` block permits juju
`>=3.5.1,<4`, so the juju 4 controllers in the environment are not usable for this
charm — a machine charm pinned below Juju 4.

```
juju add-model rv-pg14 -c concierge-lxd
juju deploy postgresql --channel 14/edge -n 2     # rev 1199
```
- 12:02:56 deploy accepted; LXD machines (containers, `virt-type=container` — note
  the project's own `spread.yaml` uses `lxc launch --vm`, so this substrate is *not*
  what CI tests on) provisioned by 12:03:03.
- `install` hook downloads and installs the `charmed-postgresql` snap (rev 393,
  then `hold`-pinned). Units active/idle, workload version 14.23 at 12:11:18.
  **Time to active ≈ 8.4 min** (mostly snap download + cloud-init apt).

Then, in order:
1. `juju run postgresql/0 get-primary` → `primary: postgresql/1`; `patronictl list`
   shows 1 Leader + 1 Sync Standby.
2. `juju config experimental_max_connections=150` → both units ran `config-changed`,
   `PostgreSQL restart required`, rolling restart via the `restart` peer relation
   (≈8 `restart-relation-changed` hooks), applied (`--max_connections=150` on the
   postgres process). Total ≈ 40 s, units stayed active.
3. `juju config experimental_max_connections=-1` → **accepted silently** (finding
   below).
4. `juju config durability_synchronous_commit=foo` → both units `BlockedStatus
   "Configuration Error. Please check the logs"`; full pydantic error in
   `debug-log`; `juju config --reset ...` → back to active. Works.
5. `juju deploy self-signed-certificates` + `juju relate
   postgresql:certificates self-signed-certificates:certificates` → TLS enabled:
   `ca.pem`/`cert.pem`/`key.pem` pushed (mode 600, owned `snap_daemon`),
   `ssl: on` in `patroni.yaml`, Patroni REST API switches to HTTPS, rolling restart
   (status "Beginning rolling restart"), then active.
6. `juju deploy data-integrator --channel edge` + config + relate → user
   `relation-5` + database `testdb` created; `get-credentials` returned endpoints,
   password, tls-ca. Verified `testdb` in `pg_database`.
7. `juju add-unit postgresql -n 1` → 3rd unit joined (2 Sync Standbys), leader
   briefly showed `Primary (degraded)` until the member caught up.
8. `juju remove-unit postgresql/2` → raft member removed via
   `database-peers-relation-departed`; machine + `pgdata/2` storage released and
   machine removed at 12:39:51. **Scale-down ≈ 9.4 min**, see the finding on the
   missing teardown handler.
9. `juju remove-relation ...:certificates ...` → TLS disabled via rolling restart.
10. `juju ssh` + `pkill -9` of patroni on unit 0 → systemd restarted
    `snap.charmed-postgresql.patroni.service` in <1 s; no charm involvement; cluster
    stayed active. (The charm's `_handle_processes_failures` covers the other
    case — patroni alive but postgres dead.)

Not tested live: S3 backups/restore (no S3 endpoint), `juju refresh` upgrade
(rev 1199 is the latest 14/edge), LDAP, async replication, tracing.

## Observed behaviour

Only-visible-from-running items:

- **Timings**: initial deploy ≈ 8.4 min; restart-triggering config change ≈ 40 s;
  scale-up ≈ 6 min; scale-down ≈ 9.4 min; patroni kill → <1 s recovery.
- **Resource use** (per unit, container with 32 GiB): postgres main process ~210 MB
  RSS, patroni ~45 MB, plus exporters and `cluster_topology_observer.py` (root).
  Charm artifact 27 MB.
- **Hook churn**: a single restart-requiring config change fires ~10 hooks
  (config-changed ×2 + restart-relation-changed ×8) across two units, plus the
  resulting `database-peers-relation-changed`. `update_config()` rewrites
  `user_hash`/`config_hash` into unit peer data on every run, and each peer
  `relation-changed` re-renders `patroni.yaml` and hits the Patroni API — the
  behaviour flagged by issue #1843 ("unnecessary databag/config updates").
- **`pkill` recovery** is systemd's `Restart=`, not the charm: the snap service is
  `disabled` (no boot autostart) but `Restart=` still applies while up.
- **Silent invalid config**: `experimental_max_connections=-1` lands in Patroni's
  dynamic config (`show-config` shows `max_connections: -1`) while postgres actually
  runs with the default 100; unit stays `Active`. Confirmed on the wire.
- **Teardown**: no `stop`/`remove` observer exists, so the departing unit runs its
  normal hooks against a stopped Patroni and logs `Early exit update_config: Unable
  to patch Patroni API` repeatedly; removal still completed (storage + machine
  released), but slowly and noisily.
- `get-primary` reads the *leader* flag from Patroni directly (not cached peer
  data), so it stays correct right after failover.

## Findings

### `experimental_max_connections` accepts invalid values silently
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/config.py:79`
- **Evidence**: `experimental_max_connections: int | None` — the only unbounded int
  in the model; every other numeric option uses a bounded alias
  (`PgPositiveIntMax` etc., `src/config.py:22-58`). `_api_update_config`
  (`src/charm.py:2200-2209`) passes it straight into the Patroni API patch. Live:
  `juju config postgresql experimental_max_connections=-1` → unit stayed `Active`,
  `patroni show-config` had `max_connections: -1`, running postgres had
  `--max_connections=100` (the computed default). No warning, no blocked status.
- **Impact**: an operator typing a bad value (negative, or e.g. `0`) gets a
  "successful" config change that silently doesn't do what they asked; the value
  persists in Patroni's dynamic config and can mask a misconfiguration.
- **Fix**: type it `PositiveInt` (or `Annotated[int, Field(ge=1, le=262143)]`) like
  its neighbours.
- **Linter rule**: mechanically checkable — "every `config_type` field must use a
  bounded type or a validating `@validator`; bare `int | None` is an error".

### No `stop`/`remove`/`storage-detaching` handler — teardown is Juju-driven and slow
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/charm.py` (no `self.framework.observe(self.on.stop, ...)`,
  `self.on.remove`, or storage-detaching handler exists — grep confirms)
- **Evidence**: during `juju remove-unit postgresql/2`, the departing unit ran its
  ordinary hooks against a stopped Patroni and repeatedly logged `Early exit
  update_config: Unable to patch Patroni API`; total removal ≈ 9.4 min. GitHub issue
  #1550 documents the worse case: a still-running snap blocks storage release, which
  blocks machine removal, which blocks model teardown.
- **Impact**: scale-down works today only because Juju eventually force-kills
  the unit's processes; it is slow, noisy, and intermittently wedges (per #1550).
- **Fix**: add a `stop` (or `remove`) observer that stops the
  `charmed-postgresql.patroni`/`pgbackrest` services and cleans up before teardown.
- **Linter rule**: not mechanically checkable (requires knowing teardown is
  non-trivial), but a "machine charm with a stateful workload must observe
  `stop`/`remove`" policy would catch it.

### Blocked status after transient S3 failure never self-heals
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/backups.py:1556` (`_s3_initialization_set_failure`) and
  `src/charm.py:1833` (`_set_primary_status_message`)
- **Evidence**: a failed stanza init sets `s3-initialization-block-message` in peer
  data and the leader goes `Blocked`; the only paths that clear it are relation
  events (`_on_s3_credential_changed`, `_on_s3_credential_gone`) and
  `coordinate_stanza_fields` (`src/backups.py:801`), which only propagates an
  already-successful init. Nothing on the `update-status` path retries the stanza
  once S3 recovers. Corroborated by open issue #1724 ("charm stays blocked ...
  never clears the blocked status on its own").
- **Impact**: a transient S3 blip leaves the unit `Blocked` indefinitely with no
  automatic recovery, misleading operators into a manual `juju resolve`/re-relate.
- **Fix**: retry `can_use_s3_repository()`/`_initialise_stanza` from
  `_on_update_status` when the current status is an S3 block message.
- **Linter rule**: not mechanically checkable.

### `logger.exception` outside an exception handler → `NoneType: None` noise
- **Severity**: low
- **Kind**: bug / lint
- **Where**: `src/charm.py:1322`
- **Evidence**: `_check_extension_dependencies` calls `logger.exception(...)` with
  no active exception (it's a plain method, not inside an `except` block), so the
  traceback printed is literally `NoneType: None`. This is the root cause of issue
  #1817 (`plugin_address_standardizer_enable=true` → `NoneType: None` in
  `debug-log`).
- **Impact**: a misleading, unparseable log line every time a plugin is enabled
  with an unsatisfied dependency.
- **Fix**: use `logger.error(...)` (or `logger.warning`) instead.
- **Linter rule**: mechanically checkable — "`logger.exception` may only appear
  inside an `except` block" (e.g. flake8-logging-format/pylint `W1205`).

### `get-primary` action fails silently on Patroni error
- **Severity**: low
- **Kind**: bug / ux
- **Where**: `src/charm.py:489-494`
- **Evidence**:
  ```python
  except RetryError as e:
      logger.error(f"failed to get primary with error {e}")
  ```
  No `event.fail()` and no `event.set_results()`, so `juju run get-primary` returns
  an empty result set with exit code 0.
- **Impact**: scripting around the action can't distinguish "no primary yet" from
  "charm couldn't reach Patroni".
- **Fix**: call `event.fail(...)` in the `except` branch.
- **Linter rule**: not mechanically checkable.

### Config changes that need no restart block the hook for up to ~12 s
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:2380-2393` (`_handle_postgresql_restart_need`)
- **Evidence**: for a no-restart change it loops
  `Retrying(stop=stop_after_attempt(5), wait=wait_fixed(3))`, raising until
  `is_restart_pending()` flips or the loop exhausts (RetryError swallowed) —
  ~12 s of idle polling (attempts at 0/3/6/9/12 s) on every such
  `config-changed`/peer event. The comment shows it's deliberate (wait out
  Patroni's 10 s `loop_wait`). Not reliably measured live: one status-log sample
  showed ~2 s config-changed hooks, plausibly the `_api_update_config` early-exit
  path ("Unable to patch Patroni API" noise was present around the same window),
  so treat the 12 s as an upper bound from the code, not an observation
  (unverified).
- **Impact**: every `juju config` of a reloadable parameter (the majority) can
  block the hook up to ~12 s and re-renders config; in a hot hook loop this
  compounds with issue #1843.
- **Fix**: rely on Patroni's `pending_restart` flag rather than a fixed poll, or
  shrink the window.
- **Linter rule**: not mechanically checkable.

### Topology observer exits on transient unreachability; restarted only on next update-status
- **Severity**: low
- **Kind**: bug / resilience
- **Where**: `scripts/cluster_topology_observer.py:134`
- **Evidence**: `main()` does `raise UnreachableUnitsError(...)` (uncaught) when no
  cluster member answers, so the process dies; the charm only restarts it from
  `_on_update_status` (`src/charm.py:1732`) or `_handle_processes_failures`
  (`src/charm.py:1825`), i.e. up to the 5 min `update-status` interval of no
  topology/database-change detection.
- **Impact**: a short network partition after which topology changes occur
  (failover) can go unobserved for minutes, delaying endpoint updates to clients.
- **Fix**: wrap the loop in `try/except` and `sleep(30)` instead of raising.
- **Linter rule**: not mechanically checkable.

### Wrong charm name in an operator-facing error hint
- **Severity**: nit
- **Kind**: docs
- **Where**: `src/charm.py:1304`
- **Evidence**: the `DependentObjectsStillExist` handler tells the operator to run
  ``juju config postgresql-k8s plugin_<plugin_name>_enable=True`` — the K8s
  charm's name, in the VM charm.
- **Impact**: following the hint fails; the fix (`juju config postgresql ...`)
  is obvious but the doc is wrong.
- **Fix**: `s/postgresql-k8s/postgresql/`.
- **Linter rule**: mechanically checkable (grep for `postgresql-k8s` in a
  non-k8s charm).

### Passwords rendered in plaintext into patroni.yaml (with mitigations)
- **Severity**: low (informational)
- **Kind**: security note
- **Where**: `templates/patroni.yml.j2:31,35-36,169-176`
- **Evidence**: `restapi.authentication.password`, `raft.password`, and
  `authentication.{replication,rewind,superuser}.password` are templated directly;
  observed live in
  `/var/snap/charmed-postgresql/current/etc/patroni/patroni.yaml`. The file is
  rendered mode `0600`, owned `snap_daemon` (`src/cluster.py:735`), and the same
  secrets are also in Juju secrets.
- **Impact**: standard Patroni practice, but the key material is on disk in
  cleartext and readable by root/snap_daemon; worth stating in the security docs.
- **Fix**: document it — Patroni supports no fully-secret-file mode for these
  fields.
- **Linter rule**: not established.

## Worth copying

- **Typed, bounded config** (`src/config.py`): ~190 options as a pydantic model with
  per-option numeric ranges and a handful of explicit `@validator`s; `_on_config_changed`
  surfaces `ValueError` as a clean `BlockedStatus` and self-clears on fix.
- **Rolling restart via `RollingOpsManager`** (`src/charm.py:2015`, `_restart`):
  restart-requiring changes and TLS toggles are serialised one unit at a time on a
  dedicated `restart` peer relation, with `are_all_members_ready()` gating and a
  "Beginning rolling restart" maintenance status.
- **Topology observer** (`src/cluster_topology_observer.py`,
  `scripts/cluster_topology_observer.py`): watches the Patroni API and synthesises
  charm events, so client endpoints update after failover without polling from the
  charm; also polls `pg_database` to trigger pg_hba re-rendering on out-of-band DDL.
- **RAFT recovery machinery** (`src/charm.py:572-708`, `_raft_reinitialisation`):
  a careful multi-unit protocol to detect loss of quorum and re-init a single
  candidate, with `promote-to-primary force` as an operator escape hatch.
- **Secret revision pruning** (`_on_secret_remove`, `src/charm.py:471`): actively
  removes obsolete secret revisions, with a version guard for juju bugs.
- **Docstring discipline and README** (`README.md`): documents the one-replica-at-a-time
  add/remove semantics, primary discovery, password rotation and rollback steps.

## Common-practice notes

- Layout follows the canonical data-platform template (poetry, `charmcraft.yaml`
  with a `poetry-deps` part building its own pip/poetry/rust toolchain, `lib/charms/...`
  vendored at specific `v<N>`, tox with lint/unit/integration envs, `spread.yaml` +
  `concierge.yaml` for CI). This is the reference implementation several other
  data-platform charms are modelled on.
- Drift: the machine charm still vendors the `postgresql_k8s` library
  (`lib/charms/postgresql_k8s/v0/postgresql.py` and `postgresql_tls.py`) — shared
  code imported from the K8s charm's namespace, which also explains the
  `postgresql-k8s` string leak in the "wrong charm name" finding above.
- The charm is pinned to Juju `< 4` via `assumes` (`metadata.yaml`) while the
  ecosystem is moving to Juju 4; the juju-4 controllers in this environment cannot
  run it.
- `experimental_max_connections` is the single config option that bypasses the
  otherwise-uniform bounded-typing convention (finding #1).
- CI tests the charm on VMs (`lxc launch --vm`, `spread.yaml`); this review ran on
  LXD *containers*, and everything still worked — good substrate portability.

## Tests

- Unit suite: `PYTHONPATH=lib:src pytest tests/unit` (in a venv with the pinned
  deps, notably `pydantic==1.10.26`): **444 passed, 10 skipped** in ~7 s. The system
  python has pydantic 2.13, which breaks collection (`@validator(..., each_item=True)`
  is v1-only) — a reminder the charm is hard-pinned to pydantic v1 (poetry.lock has
  1.10.26) and will need migration before pydantic v3; not a runtime defect since
  the charm ships its own venv.
- `ruff check src/` clean; `codespell src/ lib/` clean; `charmcraft analyse` not
  run (not installed here).
- Coverage is genuinely broad for a charm this size (per-module test files for
  backups, cluster, relations, tls, upgrade, ldap, rotate_logs, observer). Gaps
  relative to the findings above: no unit test asserts that invalid
  `experimental_max_connections` is rejected; no test covers the no-stop-hook
  teardown; `_check_extension_dependencies` is only tested for the happy path (the
  `logger.exception` noise went unnoticed).
- Integration tests (`tests/integration/`, 96 files incl. HA, backups against
  AWS/GCP/Ceph, TLS, password rotation, PITR) assert real behaviour (e.g.
  `tests/integration/ha_tests/` failover suites), not just active/idle — but they
  run against VMs in CI, not the container substrate used here.

## Docs

- README is accurate against observation: `get-primary` works on any unit, "Primary"
  status message appears, add-unit/remove-unit one-at-a-time semantics held (`_add_members`
  observed deferring while a member syncs), odd-unit-count recommendation present.
- The `postgresql-k8s` string in a runtime error (see findings) is the one doc/reality
  mismatch found; it is also the only operator-facing hint that names the wrong charm.
- Charmhub description and `metadata.yaml` docs point at the 14.x docs; the
  discourse topic (9710) is up to date with the readthedocs move.

## Open questions

- Whether scale-down can still wedge on a busy/other snap (the #1550 scenario): not
  reproduced here — `pgdata/2` was released and the machine removed cleanly, but
  slowly. Settle by repeated scale-down under load.
- Whether the ~12 s no-restart config-change stall is worth the fixed poll, or
  Patroni's `pending_restart` signal could replace it: needs a maintainer decision.
- Exact revision→commit mapping for `14/edge` rev 1199 vs local HEAD (deployed charm
  is ~1 week newer than the tree reviewed): all findings were read off local code
  plus the running rev 1199, and none depend on the gap.
- Async-replication and LDAP paths were reviewed only in code, not exercised live.
</content>
