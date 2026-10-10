# landscape-server-operator

A machine charm for deploying and managing Self-Hosted Landscape Server, Canonical's
computer-management platform. It installs the `landscape-server` APT package, manages
its systemd services, and relates it to PostgreSQL (legacy `pgsql` or modern
`data_interfaces`), RabbitMQ, HAProxy, and a growing set of integrations (SMTP, cos-agent,
debarchive, task-handler, etc.).

**Verdict**: The code has good bones — atomic file writes, clean StoredState usage,
Pydantic v2 config validation, and a modern scenario-based test suite — but the currently
published revision (134) is drastically behind local HEAD and cannot be fully deployed:
its `db`/`website` endpoints use interfaces incompatible with current PostgreSQL and
HAProxy charms, and `juju refresh` to the edge/preview channels is blocked. On top of the
interface gap, there is a critical logic bug that silently stops the charm from ever
rewriting AMQP broker credentials, a critical `pydantic_core` import failure that strands
any unit that does manage to refresh, and a `hash-id-databases` action that crashes with
a raw Python traceback. A maintainer should: (1) publish current HEAD (or otherwise close
the endpoint gap) so the documented bundles and integration tests actually work against a
real channel, (2) fix the AMQP readiness condition and the `event.fail()` format-string
bug, and (3) get the packaged charm's `pydantic-core` extension building against the same
Python minor version as the deployment base before recommending refreshes.

| | |
|---|---|
| Repo | canonical/landscape-server-operator @ b753f20 (2026-07-17) |
| Charms | `landscape-server` (machine) |
| Substrate | LXD machines (no k8s — no `containers:` in metadata.yaml) |
| Deployed | yes — `concierge-lxd` (Juju 3.6.27) rev 134, refreshed to 143 and 210; `concierge-lxd-4` (Juju 4.0.12) rev 134 fresh deploy |
| Reviewed | 2026-08-31 |

## What it does

Installs the `landscape-server` APT package (from a configurable PPA), configures the
PostgreSQL connection, RabbitMQ AMQP vhost, `service.conf`, systemd service overrides,
OIDC/OpenID authentication, SMTP relay, and the battery of landscape-server systemd units.
Exposes metrics/dashboards via `cos-agent`, routes traffic through HAProxy, and — in the
unreleased local HEAD only — also integrates with the debarchive charm, a task-handler
service, and multiple per-service HAProxy-route endpoints.

## Deployment log

### concierge-lxd (Juju 3.6.27)

1. `juju add-model rv-landscape -c concierge-lxd`
2. `juju deploy landscape-server --channel stable` → rev 134 from charmhub
3. `juju deploy postgresql --channel 16/stable`, `rabbitmq-server --channel 3.12/stable`,
   `haproxy --channel 2.8/stable`, `self-signed-certificates`, `grafana-agent`
4. Machines provisioned; apt install of `landscape-server` took ~4–6 minutes
5. `juju relate landscape-server:amqp rabbitmq-server:amqp` → relation established
6. `juju relate landscape-server:cos-agent grafana-agent:cos-agent` → subordinate deployed
7. `juju config landscape-server site_name=test-landscape` → `config-changed` fired;
   status cycled Maintenance "Configuring OpenID" → "Configuring OIDC" → Waiting
8. `juju config landscape-server min_install=true` → no hook fired (correct)
9. Failure injection: bad OIDC config, pause/resume, AMQP relation removal/restoration,
   `juju refresh --channel latest/edge`, `juju refresh --channel preview/edge` (both blocked)
10. `juju run landscape-server/0 hash-id-databases` → **FAILED**: `FileNotFoundError` for
    `/var/run/landscape/batch-hash-ids.pid` plus `TypeError: ActionEvent.fail() takes from
    1 to 2 positional arguments but 3 were given`
11. `juju run landscape-server/0 migrate-schema` → correctly refused: "Cannot migrate
    schema while running. Please run action 'pause' prior to migration"
12. `juju run landscape-server/0 pause` → succeeded, `MaintenanceStatus("Services stopped")`
13. `juju run landscape-server/0 upgrade` → succeeded, `landscape-server` upgraded to
    `24.04.14-0landscape0`, package correctly placed on hold
14. `juju run landscape-server/0 resume` → succeeded; brief `ActiveStatus` then `WaitingStatus`
15. `juju add-unit landscape-server --num-units 1` → machine 5 created, unit stuck in
    "allocating", later removed
16. `juju relate landscape-server:tls-certificates self-signed-certificates:tls-certificates`
    → FAILED: "application 'landscape-server' has no 'tls-certificates' relation"

**What blocked full deployment**: rev 134's `db` endpoint uses interface `pgsql`; the
`postgresql` charm (rev 1158) offers `postgresql`/`postgresql_client` on `database` —
incompatible. The `website` endpoint uses interface `http` and does not relate to
haproxy's `website` endpoint (interface `haproxy`). No haproxy-route endpoints exist in
rev 134. Full deployment requires the unreleased local HEAD.

**Refresh blocked**: both `latest/edge` (rev 143) and `preview/edge` (rev 210) refuse to
refresh with "would break relation 'landscape-server:amqp rabbitmq-server:amqp'" even
though stable and edge both declare interface `rabbitmq` — Juju detects a deeper
incompatibility.

### concierge-lxd-4 (Juju 4.0.12)

- `juju add-model rv-landscape4 -c concierge-lxd-4`
- `juju deploy landscape-server --channel stable` → rev 134, same ~3 min install timing,
  same Waiting-status behaviour as on Juju 3.6.27
- `juju deploy rabbitmq-server --channel 3.12/stable` (rev 294) → install hook **fails**:
  `FileNotFoundError: [Errno 2] No such file or directory: 'leader-get'`. The rabbitmq
  charm uses the Juju 3.x `leader-get` binary, removed in Juju 4.x. `juju resolved` does
  not help — the unit is permanently stuck in error, blocking AMQP testing on this
  controller (not a landscape-server bug).

### Recovery / teardown checks

- `juju resolved --no-retry landscape-server/0` clears the `pydantic_core` error state
  and returns the unit to Waiting — the documented recovery path works.
- `juju config` changes are accepted and queued while the unit is in error state, and
  processed once the error is resolved.
- `juju remove-application landscape-server` destroys machine 0 cleanly; other
  applications are unaffected.
- Verified on `preview/edge` rev 210: no `database`, `amqp`, `inbound-amqp`, or
  `outbound-amqp` relations exist. `juju relate landscape-server:database
  postgresql:database` → "no 'database' relation". Charmhub revision numbers do not
  track local git history predictably.

## Observed behaviour

- **AMQP relation**: worked initially because RabbitMQ connected before install
  finished. The published charm's `_amqp_relation_changed` condition is always true (see
  Finding below), so it never actually applies later.
- **AMQP relation removal/restoration**: `juju remove-relation` fires
  `amqp-relation-departed` → `amqp-relation-broken`; charm returns to Waiting without
  crashing. Re-establishing fires `amqp-relation-created` → `-joined` correctly.
- **AMQP relation removal while in error state**: `juju remove-relation` on an errored
  unit silently queues via Juju's deferred-hook mechanism (CLI returns success
  immediately); the queued `-departed`/`-broken` hooks fire only after `juju resolve`.
- **Maintenance flicker**: `_configure_openid` sets "Configuring OpenID" then
  immediately overwrites with `WaitingStatus("Waiting on relations")`, visible in the
  status log.
- **Active briefly then Waiting**: after AMQP connects, the unit briefly shows
  `ActiveStatus("Unit is ready")` before `_update_ready_status` catches the missing `db`
  and `haproxy` relations on the next tick and reverts to Waiting.
- **pause action**: works correctly — runs `lsctl stop` and `snap stop`, sets
  `MaintenanceStatus("Services stopped")`. Services report "Not enabled, skipping"
  because they need a complete config to run.
- **resume action**: works correctly — brief `MaintenanceStatus("Starting services")`,
  then `ActiveStatus("Unit is ready")`, immediately overwritten to
  `WaitingStatus("Waiting on relations: db, haproxy")`.
- **Partial OIDC config**: `oidc_issuer="http://test"` alone triggers
  `BlockedStatus("OIDC connect config requires at least 'oidc_issuer', 'oidc_client_id',
  and 'oidc_client_secret' values")` — the published rev 134 message, different from
  local HEAD's "When using OIDC, must provide all of {required_configs}".
- **Clearing OIDC config to `""`**: does NOT recover from BlockedStatus in rev 134 — the
  published charm treats empty strings as non-empty, so validation re-fires every
  config-changed. Local HEAD (Pydantic v2) treats empty strings as falsy and is unaffected.
- **Partial bootstrap config**: setting only `admin_email` (leaving `admin_name`,
  `admin_password` empty) causes `_bootstrap_account` to log an error and return
  silently; charm settles into `WaitingStatus("Waiting on relations: db, haproxy")` with
  no indication that bootstrap was skipped.
- **Invalid `deployment_mode`**: `deployment_mode="invalid mode with spaces"` fires
  config-changed but does not set BlockedStatus; Pydantic validation is caught and the
  charm silently falls back to `DEFAULT_CONFIGURATION` ("standalone") — the operator gets
  no signal the value was rejected `(unverified — draft and notes disagree on whether this
  produces BlockedStatus; notes describe silent fallback, treat as unconfirmed detail)`.
- **Invalid `redirect_https`**: `redirect_https="invalid_value"` correctly triggers
  `BlockedStatus("Invalid configuration. See \`juju debug-log\`.")`; resetting to
  `"default"` returns the charm to Waiting.
- **cos-agent integration**: deploying `grafana-agent` as a subordinate and relating via
  `cos-agent` works correctly — relation hooks fire (`cos-agent-relation-created`,
  `-joined`, `-changed`), the subordinate is blocked only for lacking a Grafana/Prometheus
  backend, and landscape-server correctly provides scrape configs and dashboards.
- **cos-agent relation removal**: fires `cos-agent-relation-departed` →
  `cos-agent-relation-broken`; landscape-server returns to Waiting, and grafana-agent goes
  to `blocked: Missing incoming relation: cos-agent|juju-info`.
- **Log typo**: the published charm logs `"rabbimq-server has not sent password yet"` —
  a typo not present in local source, confirming it lives only in the published charm.py.
- **Services installed but idle**: all landscape systemd units (landscape-api,
  -appserver, -async-frontend, -job-handler, -msgserver, -package-upload, -pingserver)
  are present on disk but not started, since they require a complete config with db.
- **`hash-id-databases` action**: fails with two stacked errors — (1)
  `FileNotFoundError: [Errno 2] No such file or directory:
  '/var/run/landscape/batch-hash-ids.pid'` because `/var/run/landscape/` doesn't exist;
  (2) `TypeError: ActionEvent.fail() takes from 1 to 2 positional arguments but 3 were
  given` from a format-string call (`event.fail("message %s", arg)`), which crashes the
  hook entirely instead of reporting a clean failure. The format-string fix landed in
  local HEAD and was first published in rev 209; the missing-directory issue is unfixed
  even in local HEAD.
- **`migrate-schema`**: correctly refuses to run while the unit isn't paused, with an
  actionable message.
- **`upgrade` action**: after pausing, correctly upgrades `landscape-server` to
  `24.04.14-0landscape0`, `landscape-client` to `24.04-0landscape0`, and
  `landscape-common` to `24.04-0landscape0`, and places the package on hold.
- **Invalid SSL config**: `ssl_key="not a valid key"` (non-base64, with `ssl_cert="not a
  valid cert"`) crashes `config-changed` and enters an exponential-backoff retry loop —
  `error: hook failed: "config-changed"` indefinitely. Clearing to valid values does not
  break the loop; only `juju resolve` clears it and lets the charm return to Waiting. The
  "Installing SSL certificate" status seen during retries is the landscape-server systemd
  service's own status, not the charm's.
- **`upgrade-charm` fails after `juju refresh`**: refreshing 134→143 (`latest/edge`) or
  134→210 (`preview/edge`) triggers `hook failed: "upgrade-charm"` with
  `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'`. Confirmed via
  `juju run landscape-server/0 pause`, which reproduces the same traceback — every action
  fails identically once the unit is in this state. `juju resolve` clears it and the
  charm settles into Waiting at rev 143/210.
- **Recovery path for `juju refresh`**: refreshing from 134 to a newer channel first
  requires breaking the AMQP relation (`juju remove-relation`); afterwards `juju refresh`
  succeeds and `upgrade-charm` runs (and may still need `juju resolve` per above).
- **Services run despite Waiting status**: landscape-server systemd services are active
  on the machine even while the charm reports `waiting: Waiting on relations: db,
  haproxy`, cycling through "Installing SSL certificate" as their systemd status —
  consuming CPU and filling logs. Root cause appears to be the package starting its own
  services during apt install, before the charm can stop them.
- **All 6 documented actions present**: `hash-id-databases`, `migrate-schema`, `pause`,
  `resume`, `upgrade`, plus the internal `juju-exec` runner. No `get-authentication-method`,
  `get-computer-groups`, or `get-registration-key` actions exist in the published charm.
- **Scaling**: `juju add-unit landscape-server --num-units 1` provisions a new machine;
  the unit stays in "allocating" until the machine is ready, then stalls because it can't
  fully start without `db`/`haproxy`. Scaling down required `juju remove-unit --force`.
- **No TLS relation**: no `tls-certificates` endpoint in the published charm; TLS is
  configured via `ssl_cert`/`ssl_key` config options only. `redirect_https` config option
  does not exist in rev 134 (confirmed: "unknown option").

## Findings

### AMQP broker config condition always true in published charm

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:1396–1397` (`_amqp_relation_changed`)
- **Evidence**:
  ```python
  self._stored.ready[relation_name] = True
  if not (
      self._stored.ready.get("inbound-amqp")
      and self._stored.ready.get("outbound-amqp")
  ):
      self.unit.status = MaintenanceStatus(
          "Waiting for inbound and outbound AMQP details..."
      )
      return
  update_service_conf({"broker": {"host": hostname, "password": password}})
  ```
  Rev 134's AMQP endpoint is named `amqp` (single relation), so
  `ready.get("inbound-amqp")` and `ready.get("outbound-amqp")` both return `None`. The
  condition `not (None and None)` evaluates `True`, so the handler always enters the
  if-block, sets `MaintenanceStatus`, and returns — `update_service_conf` is never
  called after the AMQP relation fires.
- **Impact**: If RabbitMQ credentials change after initial deployment (password rotation,
  cluster failover to a different hostname), `service.conf` is never updated.
  Landscape Server keeps trying to connect with stale credentials and fails silently,
  because `_stored.ready["amqp"]` is already `True` and won't re-trigger the check.
- **Fix**: Match the condition to the actual relation name(s) actually declared, e.g.
  check `self.model.get_relation("amqp")` directly, or simply remove the guard since
  `_stored.ready[relation_name] = True` was just set unconditionally above it.
- **Linter rule**: not mechanically checkable without semantic analysis of relation
  names vs. `_stored.ready` keys.

### `pydantic_core` import failure strands units after `juju refresh`

- **Severity**: critical
- **Kind**: bug
- **Where**: packaged charm venv (not in source tree); triggered from `src/charm.py:25`
  (`from charms.grafana_agent.v0.cos_agent import COSAgentProvider`)
- **Evidence**: refreshing rev 134 → 143 or 210 fails `upgrade-charm` with
  `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'`. The
  `pydantic-core` C extension in the packaged venv can't load under the machine's Python
  3.12.3. `helpers.py:16`'s comment about filtering `/usr/lib/python3.14` paths confirms
  this class of Python-version mismatch is a known concern. Reproduced identically via
  `juju run landscape-server/0 pause` — every action fails with the same traceback until
  `juju resolve`.
- **Impact**: Any operator who runs `juju refresh` on the published charm is immediately
  stuck — `upgrade-charm` fails, every subsequent action fails, and the unit sits in a
  permanent error loop until manually resolved. This is undocumented.
- **Fix**: Ensure the charm build environment's Python minor version matches the target
  deployment base's Python (rev 134's build appears fine; 143/210 appear to have built
  against Python 3.14 while the base runs Python 3.12). Add a CI/build check validating
  that compiled extensions match the target base.
- **Linter rule**: not mechanically checkable from source; requires runtime validation
  against the deployment base.

### `hash-id-databases` action crashes instead of failing cleanly

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:2585–2602` (`_hash_id_databases`); landscape-server package
  script (root cause of the first error)
- **Evidence**: `juju run landscape-server/0 hash-id-databases` produces:
  ```
  FileNotFoundError: [Errno 2] No such file or directory: '/var/run/landscape/batch-hash-ids.pid'
  Uncaught TypeError in charm code: ActionEvent.fail() takes from 1 to 2 positional arguments but 3 were given
  ```
  The package's `hash-id-databases-ignore-maintenance` script fails because
  `/var/run/landscape/` doesn't exist. The charm catches the resulting
  `CalledProcessError` and calls `event.fail("message %s", arg)` — a format-string call
  instead of an f-string — which raises `TypeError` and crashes the hook. Fixed in
  commit `70a4ac1` (2025-04-29), first published in rev 209; rev 134 (stable) and rev 143
  (latest/edge) still have the bug. The missing-directory root cause is unfixed even in
  local HEAD.
- **Impact**: An operator regenerating hash-ID databases sees a raw Python traceback
  instead of an actionable message, and the crashed hook leaves the action's failure
  state ambiguous.
- **Fix**: Create `/var/run/landscape` (e.g. in the install hook) before running the
  landscape script; separately, ensure `event.fail()` calls use f-strings (already fixed
  upstream for the format-string half of this bug).
- **Linter rule**: not mechanically checkable.

### Published charm is drastically behind local HEAD

- **Severity**: high
- **Kind**: docs | test-gap
- **Where**: `metadata.yaml` (local HEAD) vs. published rev 134 / rev 210
- **Evidence**: The published charm has 9 endpoints: `db` (pgsql), `amqp` (rabbitmq),
  `website` (http), `data`, `hosted`, `nrpe-external-master`, `cos-agent`, `replicas`,
  `application-dashboard`. Local HEAD additionally has `database` (postgresql via
  data_interfaces), `inbound-amqp`/`outbound-amqp`, `smtp`, `debarchive`, `task-handler`,
  and 8 individual `*-haproxy-route` endpoints. `charmcraft.yaml` references charm-libs
  (`data_platform_libs` v0.54, `haproxy.haproxy_route` v1.13, `smtp_integrator.smtp`
  v0.21, `grafana_agent.cos_agent` v0.25) the published charm doesn't ship. Published
  `charm.py` is 1233 lines vs. local's 2643. `redirect_https` is not a config option in
  the published charm. `preview/edge` rev 210 also lacks `database`, `inbound-amqp`,
  `outbound-amqp`, and haproxy-route endpoints.
- **Impact**: The bundle examples (`pgbouncer.bundle.yaml`, `postgres14.bundle.yaml`,
  `saas.bundle.yaml`) and `tests/integration/test_bundle.py` all reference endpoints that
  don't exist on any published channel. An operator following the documentation cannot
  deploy the described configuration, and the integration tests can't run against any
  charmhub revision.
- **Fix**: Publish current HEAD (the bundle examples and README are correct; the
  published charm is the problem).
- **Linter rule**: not mechanically checkable without comparing published vs. local
  metadata.

### AMQP hostname KeyError when key is absent

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:1387` (`_amqp_relation_changed`)
- **Evidence**:
  ```python
  if "password" not in unit_data:
      logger.info("rabbitmq-server has not sent password yet")
      return

  hostname = unit_data["hostname"]  # no guard
  password = unit_data["password"]
  ```
  The guard checks `password` but not `hostname`. A RabbitMQ-compatible charm that omits
  or renames `hostname` would raise an uncaught `KeyError`.
- **Impact**: Crashes the hook rather than surfacing a human-readable BlockedStatus,
  producing a rapid retry loop and Error status. `(unverified — could not be triggered
  against the current RabbitMQ charm, which always provides hostname)`.
- **Fix**: Add `if "hostname" not in unit_data: return` alongside the existing password
  guard.
- **Linter rule**: "Dictionary access on unvalidated relation data without a `.get()`
  guard" — not mechanically checkable without dataflow analysis.

### Invalid SSL config causes persistent error state with no self-recovery

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:250–268` (`_get_ssl_cert`), called from `_on_config_changed`
- **Evidence**: `ssl_key="not a valid key"` / `ssl_cert="not a valid cert"` (non-base64)
  causes `config-changed` to crash and enter exponential-backoff retries, landing on
  `error: hook failed: "config-changed"`. Clearing to valid values afterward does not
  break the loop. `_get_ssl_cert` raises `SSLConfigurationError` on a failed base64
  decode, and `_on_config_changed` has no try/except for it, so the exception propagates
  to the hook dispatcher.
- **Impact**: An operator who misconfigures `ssl_cert`/`ssl_key` strands the unit
  permanently; only manual `juju resolve` recovers it.
- **Fix**: Wrap the `_get_ssl_cert()` call in `_on_config_changed` with a try/except for
  `SSLConfigurationError`, setting `BlockedStatus("SSL configuration error: ssl_cert and
  ssl_key must be base64-encoded")` — mirroring the pattern already used in
  `_update_haproxy_connection` (`src/charm.py:1448`).
- **Linter rule**: "Call to `_get_ssl_cert()` outside try/except for
  `SSLConfigurationError`" — mechanically checkable by searching for `_get_ssl_cert(` calls.

### OIDC config cannot be cleared once set to empty string in published rev 134

- **Severity**: medium
- **Kind**: bug
- **Where**: published rev 134 (source not available for citation)
- **Evidence**: `oidc_issuer="http://test"` triggers `BlockedStatus` with the OIDC
  validation error. Setting all OIDC fields back to `""` does NOT recover — the
  validation error re-fires on every `config-changed`. Local HEAD uses Pydantic v2, where
  empty strings are falsy, so its validator (`if any(oidc.values())`) skips the check
  correctly; the published rev 134's validation appears to treat empty strings as
  non-empty.
- **Impact**: An operator who accidentally sets an incomplete OIDC config cannot recover
  by clearing it — all three fields must be set to valid values, which may not be
  desired.
- **Fix**: Update the published charm's OIDC validation to treat empty strings as
  "not configured" (same as unset).
- **Linter rule**: "Optional string config field not handling empty-string as unset" —
  checkable with a test that sets all OIDC fields to `""` and asserts no `BlockedStatus`.

### `_leader_elected` does not guard against a missing peer relation

- **Severity**: medium
- **Kind**: correctness
- **Where**: `src/charm.py:2073–2074`
- **Evidence**:
  ```python
  if self.unit.is_leader():
      peer_relation = self.model.get_relation("replicas")
      ip = str(self.model.get_binding(peer_relation).network.bind_address)  # no None check
  ```
  Unlike `_update_debarchive_relations` (`src/charm.py:1811`) and `_landscape_hostname`
  (`src/charm.py:1895`), which both guard with `if peer_relation is not None:`,
  `_leader_elected` does not. `get_binding(None)` raises `ModelError` if the peer
  relation is absent when the handler fires.
- **Impact**: In an HA deployment, a leader election during a brief network partition or
  unit restart would crash the hook, requiring `juju resolve`. No unit test exercises
  this path.
- **Fix**: Add `if peer_relation is None: return` before the `get_binding` call, or use
  a `unit_ip` property that already handles the missing-peer case.
- **Linter rule**: "Unguarded `model.get_binding(relation)` after `get_relation()`
  without a None check" — mechanically checkable.

### `_update_ready_status` early-return can leave the charm stuck in Waiting

- **Severity**: medium
- **Kind**: correctness | ux
- **Where**: `src/charm.py:990–992`
- **Evidence**:
  ```python
  def _update_ready_status(self, restart_services=False) -> None:
      if isinstance(self.unit.status, (BlockedStatus, MaintenanceStatus)):
          return
  ```
  Correctly skips overwriting Blocked/Maintenance. But if a prior handler leaves the
  status in `WaitingStatus` (e.g. `_bootstrap_account` on partial config), and all
  relations subsequently become ready, this early return is not hit — but the function
  is only called on the relevant hooks, so a fully-ready charm that never re-fires one of
  those hooks could remain in `WaitingStatus` with no operator-actionable message. No
  unit test covers this path.
- **Impact**: A fully-configured charm could appear stuck in Waiting with no signal to
  the operator that anything is wrong.
- **Fix**: Ensure all readiness-affecting code paths re-invoke `_update_ready_status`, or
  narrow the early-return to only `BlockedStatus`.
- **Linter rule**: not mechanically checkable.

### `_bootstrap_account` silently no-ops on partial required args

- **Severity**: medium
- **Kind**: correctness
- **Where**: `src/charm.py:2333–2336`
- **Evidence**:
  ```python
  if not any(required_args):
      return
  if not all(required_args):
      logger.error(
          "Admin email, name, and password required for bootstrap account"
      )
      return  # no status set
  ```
  Observed directly: setting only `admin_email` (with `admin_name`/`admin_password`
  empty) logs an error and returns; no `BlockedStatus` is set, and the unit settles into
  `WaitingStatus("Waiting on relations: db, haproxy")` with no indication bootstrap was
  skipped.
- **Impact**: An operator who forgets one of the three required fields believes the charm
  is working normally, but no admin account is ever created.
- **Fix**: Set `BlockedStatus("Admin email, name, and password are all required to
  bootstrap the admin account")` before returning.
- **Linter rule**: "Method returns without setting unit status when a precondition is
  not met" — not mechanically checkable.

### Postfix config rewrite is fragile

- **Severity**: medium
- **Kind**: correctness
- **Where**: `src/charm.py:2229–2261` (`_configure_smtp`)
- **Evidence**: Reads `main.cf` line by line, modifies matching keys in place, appends
  new keys at the end. No backup, no validation of existing values, no atomic write
  (file opened, modified, written back in place), and no handling of duplicate keys or
  formatting variants (`relayhost = ` vs `relayhost=`). `(unverified — could not inject a
  malformed postfix config to observe the failure directly)`.
- **Impact**: A malformed rewrite could corrupt `main.cf`; if postfix then fails to
  reload, the charm goes `BlockedStatus("postfix configuration failed")` but the corrupt
  file isn't recoverable from the charm side.
- **Fix**: Use `postconf(1)` to set individual parameters, or write atomically to a temp
  file and rename.
- **Linter rule**: not mechanically checkable.

### 2 unit tests fail (and crash teardown) under Python 3.14

- **Severity**: medium
- **Kind**: bug
- **Where**: `tests/unit/test_settings_files.py:87` and `:150`
- **Evidence**: `test_writes_drop_in_for_each_service` and
  `test_empty_id_removes_existing_drop_in` fail with `TypeError: Path.replace() takes 2
  positional arguments but 3 were given`. The `redirect_systemd_paths` fixture calls
  `path.replace("/etc/systemd/system", str(tmp_path))` — a 3-argument call that worked in
  Python 3.10–3.13 (applying `str.replace` semantics to the Path) but fails under Python
  3.14's `Path.replace()`, which now takes a single destination argument. Production code
  in `settings_files.py` uses `os.path.join`/`open()`/`os.rename` and is unaffected.
  Overall unit test run: 340 pass, 2 fail with an additional `INTERNALERROR` during
  pytest teardown when the monkeypatched `fake_exists` is invoked during cleanup.
- **Impact**: CI's `ubuntu-24.04` job (system Python 3.14) silently produces broken test
  coverage for these two cases, and the teardown crash can abort the whole run.
- **Fix**: Replace `path.replace("/etc/systemd/system", str(tmp_path))` with
  `str(path).replace("/etc/systemd/system", str(tmp_path))` in the `fake_exists`/
  `fake_remove` closures.
- **Linter rule**: none existing catches this.

### Integration tests never run in CI

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_bundle.py` + CI workflow
- **Evidence**: All live-model tests are decorated
  `@pytest.mark.skipif(USE_HOST_JUJU_MODEL, reason=LIVE_MODEL_SKIP_REASON)`. CI runs only
  `make test`, which runs `uv run pytest tests/unit`. `bundle.yaml` (used by the
  integration tests) references the local charm path
  (`../landscape-server_ubuntu@24.04-amd64.charm`) and endpoints absent from the
  published charm. The unit-test CI matrix covers ubuntu-22.04 and ubuntu-24.04, not
  ubuntu-26.04 (the charm's default base).
- **Impact**: The tests that assert real behaviour (DB migration, HAProxy routing, snap
  install, pause/resume) never run automatically; they require manual
  `USE_HOST_JUJU_MODEL=true`, which is discouraged.
- **Fix**: Add an integration-test pipeline against a temporary Juju model, and update
  `conftest.py`'s bundle path to match the new bundle layout once HEAD is published.
- **Linter rule**: none.

### Landscape-server services run in a restart loop despite Waiting status

- **Severity**: medium
- **Kind**: correctness | ux
- **Where**: systemd service lifecycle (package level); `_on_install` does not stop them
- **Evidence**: The landscape-server systemd services (landscape-api, -appserver,
  -async-frontend, -job-handler, -msgserver, -package-upload, -pingserver) are active on
  the machine while the charm reports `waiting: Waiting on relations: db, haproxy`,
  cycling through "Installing SSL certificate" repeatedly and filling systemd logs. The
  package's install hook starts them before the charm can intervene, and nothing stops
  them until the charm has a complete config.
- **Impact**: Resource consumption (CPU, disk for logs), log noise that may mask real
  issues, and services attempting DB connections that fill error logs.
- **Fix**: In `_on_install`, after the package installs, explicitly `lsctl stop` before
  the charm proceeds with its own configuration.
- **Linter rule**: not mechanically checkable.

### `_resume` sets `ActiveStatus` before verifying services actually started

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:2462–2480`
- **Evidence**:
  ```python
  self._stored.running = True
  self._stored.paused = False
  self.unit.status = ActiveStatus("Unit is ready")   # set here
  self._update_ready_status()                        # overwrites
  ```
  If `snap.SnapCache()[LANDSCAPE_OUTBOX_SNAP].start()` raises `SnapError`, the status was
  already briefly set to `ActiveStatus` before being overwritten to `BlockedStatus`.
  Observed in the status log: `ActiveStatus("Unit is ready")` at 12:40:23, immediately
  overwritten to `WaitingStatus` by `_update_ready_status` in the same tick.
- **Impact**: Minor — observability tooling polling `juju status` sees a brief flash of
  `ActiveStatus` before the real status.
- **Fix**: Move the `ActiveStatus` assignment to after the snap start succeeds, or rely
  entirely on `_update_ready_status()`.
- **Linter rule**: not established.

### Status flicker in OIDC/OpenID config handlers

- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:2297–2324`
- **Evidence**: `_configure_openid` and `_configure_oidc` set
  `MaintenanceStatus("Configuring OpenID"/"Configuring OIDC")` then immediately set
  `WaitingStatus("Waiting on relations")` before returning — two visible transitions in
  `show-status-log` even though no services actually start.
- **Impact**: Status log noise, potentially confusing operators alerting on status
  transitions.
- **Fix**: Only set a `MaintenanceStatus` when there is actual configuration work to do,
  and let `_update_ready_status` handle the final status.
- **Linter rule**: not established.

### `_pause` not fully idempotent on partial failure

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:2425–2445`
- **Evidence**: If `lsctl stop` fails, the snap isn't stopped and neither
  `_stored.running` nor `_stored.paused` is updated. If `snap.stop()` fails after `lsctl
  stop` succeeded, `_stored.running` is also left stale. The event fails with "Failed to
  stop services" in both cases.
- **Impact**: After a partial failure, `_stored.running` may not reflect reality, and a
  subsequent `_resume` may act on stale state.
- **Fix**: Update `_stored.running`/`_stored.paused` to reflect actual state even on
  partial failure.
- **Linter rule**: not established.

### `_on_config_changed` sets a useless intermediate status

- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:536`
- **Evidence**:
  ```python
  self.charm_config = LandscapeCharmConfiguration.model_validate(self.model.config)
  self.unit.status = WaitingStatus("Configuration validated...")
  ```
  followed immediately by all the real configuration steps (snap refresh, service conf,
  OIDC, database, bootstrap, autoregistration, GPG), which overwrite this status before
  the next hook tick.
- **Impact**: Status log noise with no useful signal.
- **Fix**: Drop the intermediate `WaitingStatus("Configuration validated...")` and start
  directly with `MaintenanceStatus("Configuring Landscape...")`.
- **Linter rule**: not established.

### Pydantic deprecated API in vendored `cos_agent` lib

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/grafana_agent/v0/cos_agent.py:702`
- **Evidence**: `data.json()` is called — deprecated in Pydantic v2 (`model_dump_json`
  is the replacement). Every unit test creating a `GrafanaMachineAgentRelation` produces
  a `PydanticDeprecatedSince20` warning (52+ warnings per run).
- **Impact**: Test noise; the charm itself uses the library correctly, the library's
  internals are stale.
- **Fix**: Pin `cosl` to a version using `model_dump_json`, or update/patch the vendored
  lib.
- **Linter rule**: mechanical deprecation check.

### No caching on `get_modified_env_vars()` workaround

- **Severity**: low
- **Kind**: performance
- **Where**: `src/helpers.py:16`
- **Evidence**: `get_modified_env_vars()` filters `sys.path` on every call and is invoked
  from many subprocess call sites (`execute_psql`, `migrate_service_conf`,
  `_bootstrap_account`, `_set_autoregistration`, `_resume`, `_migrate_schema`,
  `_hash_id_databases`), potentially several times per hook. The workaround itself
  (avoiding a C-extension Python-version mismatch) is necessary and correct.
- **Impact**: Minor overhead only.
- **Fix**: `functools.lru_cache` on the function, since `sys.path` is static during a
  hook run.
- **Linter rule**: not established.

### Rabbitmq charm rev 294 broken on Juju 4.x (not a landscape-server bug)

- **Severity**: medium
- **Kind**: bug | test-gap
- **Where**: rabbitmq-server charm rev 294 (external dependency)
- **Evidence**: Deploying rabbitmq-server on `concierge-lxd-4` (Juju 4.0.12) fails the
  install hook with `FileNotFoundError: [Errno 2] No such file or directory:
  'leader-get'` — the charm uses the Juju 3.x `leader-get` binary, removed in Juju 4.x.
  `juju resolved` doesn't help; the unit is permanently stuck.
- **Impact**: Blocks AMQP integration testing of landscape-server on Juju 4.x
  controllers, even though landscape-server itself deploys and behaves identically on
  Juju 3.x and 4.x (confirmed rev 134 on both).
- **Fix**: Not a landscape-server fix — use a newer rabbitmq-server revision on Juju 4.x.
- **Linter rule**: not applicable to landscape-server.

### Charmhub revision numbers don't reflect local source

- **Severity**: medium
- **Kind**: docs | test-gap
- **Where**: charmhub channel mapping (not in source tree)
- **Evidence**: `preview/edge` is at rev 210, but `juju relate landscape-server:database
  postgresql:database` → "no 'database' relation" and `juju relate
  landscape-server:amqp rabbitmq-server:amqp` (from stable, when attempting to relate
  differently) → "no 'amqp' relation" against 210's actual endpoint set. Local HEAD's
  `metadata.yaml` defines `database`, `inbound-amqp`/`outbound-amqp`, and 8
  haproxy-route endpoints absent from rev 210.
- **Impact**: Operators following the README's integration examples find the described
  endpoints absent from every published channel.
- **Fix**: Publish current HEAD; document which channel/revision has which features.
- **Linter rule**: not mechanically checkable without comparing published vs. local
  metadata.

### `upgrade` action works correctly; "Not enabled" services are expected

- **Severity**: informational
- **Kind**: ux
- **Where**: `src/charm.py:2504–2552`
- **Evidence**: `juju run landscape-server/0 upgrade --wait` upgraded `landscape-server`
  to `24.04.14-0landscape0` and placed the package on hold. Subsequent `lsctl
  stop/start` output shows all services report "Not enabled, skipping" because the
  charm hasn't been fully configured (no database, no HAProxy) — expected given Waiting
  status, not a bug.
- **Impact**: none — documentation only.
- **Fix**: none needed.

### Scale-up works; second unit waits on machine provisioning

- **Severity**: informational
- **Kind**: ux
- **Where**: Juju scale operation
- **Evidence**: `juju add-unit landscape-server --num-units 1` created machine 5 and
  began provisioning; `landscape-server/1` stayed "allocating" while machine 5 was
  "pending", and had to be removed with `juju remove-unit --force` after it got stuck.
- **Impact**: Scaling mechanics work; the second unit can't fully start without `db`/
  `haproxy` relations, which the published charm can't establish.
- **Fix**: none needed from the charm; full testing requires a complete relation setup.

### No `tls-certificates` relation in published charm

- **Severity**: informational
- **Kind**: docs
- **Where**: `metadata.yaml` (local HEAD) vs. rev 134
- **Evidence**: `juju relate landscape-server:tls-certificates
  self-signed-certificates:tls-certificates` → "application 'landscape-server' has no
  'tls-certificates' relation". TLS is configured via `ssl_cert`/`ssl_key` config
  options; `redirect_https` also does not exist in the published charm.
- **Impact**: Operators expecting relation-based TLS will be surprised by the
  config-file approach.
- **Fix**: Document the config-based TLS approach in the README, or add a
  `tls-certificates` relation if dynamic TLS is desired.

## Worth copying

- **Atomic file writes**: `settings_files.py` and `charm.py` write-to-temp + chmod +
  `os.replace` throughout — the right pattern for sensitive files (certs, keys,
  passwords).
- **`PgHbaNotReadyError` re-raise for Juju retry**: `database.py` raises this when
  Patroni hasn't yet updated `pg_hba.conf`; it propagates so Juju retries the hook — the
  correct pattern for asynchronous database-init races.
- **Status precedence in `_update_ready_status`**: returns early when already Blocked/
  Maintenance, avoiding wasted work.
- **StoredState for cross-hook state**: `ready` (a clean single dict keyed by relation
  name), `leader_ip`, `running`, `paused`, `account_bootstrapped`, `secret_token`,
  `cookie_encryption_key`, `enable_ubuntu_installer_attach` are all in `StoredState` —
  easy to audit.
- **Per-service systemd drop-ins**: `write_deployment_mode_systemd_override` and
  `write_analytics_id_systemd_override` write drop-in snippets rather than patching
  package-supplied unit files directly.
- **Scenario tests with full state**: uses `ops.testing.Context`/`State` objects
  including stored state, relations, leader flags, and network bindings — better
  coverage than the older `Harness` approach still used elsewhere in the suite.
- **GPG home directory permissions**: `write_outbox_certificates` creates
  `OUTBOX_GRPC_CERTS_DIR` with `0o700` and the key with `0o600`.
- **Pydantic config validation**: `LandscapeCharmConfiguration` uses field validators
  (`deployment_mode`, `analytics_id`), model validators (OpenID/OIDC mutual exclusivity
  and minimum-fields), and port-overlap detection — the right level of validation for a
  complex multi-service charm.
- **Upgrade path safety**: `upgrade` action requires the unit paused first, unholds the
  package, upgrades, then re-holds it — prevents accidental package drift.

## Common-practice notes

- Modern `main(LandscapeServerCharm)` dispatch with `self.framework.observe` handlers;
  followed correctly.
- `charm-libs` declared with pinned versions in `charmcraft.yaml`.
- Correct split of StoredState (internal per-unit flags) vs. peer relation data
  (leader IP, cross-unit token sharing).
- Libraries under `lib/charms/<charm>/v<N>/` follow convention:
  `data_platform_libs` v0.54, `grafana_agent` v0, `haproxy` v0, `smtp_integrator` v0.
- Modern `#!/bin/sh` dispatch, no `hooks/` directory needed.
- Terraform module (`terraform/charm/`) is a thin but functional wrapper around
  `juju_application`; `trust = true` is appropriate.
- 5 bundle files (`bundle.yaml`, `legacy.bundle.yaml`, `pgbouncer.bundle.yaml`,
  `postgres14.bundle.yaml`, `saas.bundle.yaml`) cover different configurations, but the
  primary bundle references a local packed charm path, not charmhub, and requires
  unreleased code.
- Test style mixes deprecated `ops.testing.Harness` (52 warnings) with modern
  `ops.testing.Context`/scenario tests; the `capture_service_conf` fixture is a good
  pattern for redirecting filesystem writes in unit tests.
- No k8s support (no `containers:` in `metadata.yaml`) — purely systemd/apt/snap, which
  is appropriate for this workload.
- `needrestart` is removed during install to avoid interactive prompts — good practice
  for unattended charm operation.

## Tests

| Suite | Count | Status | Notes |
|---|---|---|---|
| `pytest tests/unit` (excl. settings_files) | 317 | all pass | |
| `pytest tests/unit/test_database_relation.py` | 29 | all pass | Scenario/state-transition tests |
| `pytest tests/unit/test_haproxy_route.py` | 34 | all pass | Full haproxy route logic |
| `pytest tests/unit/test_legacy_haproxy.py` | 47 | all pass | SSL cert validation, HAProxy service |
| `pytest tests/unit/test_charm.py` | 150 | all pass | All actions, relations, bootstrap |
| `pytest tests/unit/test_config.py` | 49 | all pass | Pydantic config validation |
| `pytest tests/unit/test_settings_files.py` | 25 | 23 pass, 2 fail + INTERNALERROR | Python 3.14 `Path.replace` crash |
| `ruff check src tests` | — | all pass | No lint errors |

**Coverage confirmed:**
- All 29 `database_relation` tests pass; `PgHbaNotReadyError` propagation and
  schema-failure `BlockedStatus` are correctly tested.
- All 47 `legacy_haproxy` tests pass; `test_requires_ssl_cert_and_key` covers
  `_get_ssl_cert` raising `SSLConfigurationError` for invalid base64, cert/key mismatch,
  and missing key — so `_get_ssl_cert`'s validation logic itself is tested even though
  the config-changed handler doesn't catch the exception (see SSL finding above).
- All 34 `haproxy_route` tests pass; `_provide_all_haproxy_route_requirements` is
  exercised on `config_changed`, `haproxy_route_relation_joined`, `leader_elected`, and
  `upgrade_charm` — with mocked relations.
- All 150 `charm` tests and 49 `config` tests pass.

**Test gaps:**
- No test exercises `_leader_elected` with no peer relation present (would raise
  `ModelError`; see finding above).
- No test covers `_update_ready_status` failing to promote a `WaitingStatus` unit to
  `ActiveStatus` once relations become ready.
- No test covers `_bootstrap_account` with only some of `admin_email`, `admin_name`,
  `admin_password` set — the suite assumes all-or-nothing.
- Integration tests (20+ tests asserting real DB queries, HTTP responses, systemd
  service state, snap installs) are comprehensive but never run in CI (see finding above).

## Docs

- **README.md**: extensive, covers standalone/scalable/PgBouncer/SaaS deployment
  scenarios with relation diagrams and example bundles. One known inaccuracy:
  `min_install`'s description says it skips recommended packages, but it also skips
  hashids.
- **charmhub description**: accurate for the published rev 134; doesn't mention the
  haproxy-route endpoints, task-handler, or debarchive integration (local-only).
- **Contributing guide**: no `CONTRIBUTING.md`, though `tox.ini`'s CI workflow
  references one.
- **LICENSE**: Apache 2.0, present.
- **Terraform docs**: `terraform/charm/README.md` documents all variables; minimal but
  sufficient.

## Open questions

1. When will local HEAD be published? It has a large feature gap over rev 134, and even
   `preview/edge` rev 210 lacks the `database` and `inbound-amqp`/`outbound-amqp`
   endpoints the integration tests and bundles depend on.
2. Does the AMQP hostname `KeyError` path ever trigger in practice, given the current
   RabbitMQ charm always sends `hostname`?
3. Would a malformed existing postfix `main.cf` actually corrupt the file, or does
   postfix's own validation catch it first?
4. Why did the build environment for revs 143/210 apparently target a different Python
   minor version than rev 134's build, causing the `pydantic_core` failure?
5. Should the charm create `/var/run/landscape` itself in the install hook?
6. Why does `juju refresh` to edge/preview channels get blocked before `upgrade-charm`
   even runs — is this a Juju relation-compatibility metadata check?
7. Are the landscape-server systemd services supposed to run and fail gracefully before
   the charm has a full config, or should the charm stop them proactively during install?
8. Is `_update_ready_status`'s early-return-on-Waiting behaviour intentional, or an
   oversight?
9. Will a newer rabbitmq-server revision fix the Juju 4.x `leader-get` incompatibility?
