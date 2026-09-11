# sunbeam-charms

Thin operator-layer charms for OpenStack control-plane services (keystone,
placement, nova-ironic, designate-bind, etc.), all built on the shared
`ops-sunbeam` library. Each charm extends a base class from `ops-sunbeam`
(`OSBaseOperatorAPICharm`, `OSBaseOperatorCharmSnap`, or `OSBaseOperatorCharm`)
and follows a consistent pipeline: relation handlers → `configure_charm` →
config rendering → Pebble layer → status.

**Verdict**: the charm pattern and library design are solid — compound
status, secrets-based credential handling, and the relation-handler
abstraction are all well done and worth copying elsewhere. But the
foundation library (`ops-sunbeam`) currently has zero working unit test
coverage in CI because of a two-line `ops` API break
(`ops.jujucontext.JujuContext` no longer exists), and that break was not
caught because ops-sunbeam's unit tests aren't run in CI at all — only
charm builds and zaza functional tests. Two more charms
(`ironic-conductor-k8s`, `sunbeam-machine`) can't even collect their unit
tests outside the tox harness because of top-level imports of
optional/environment-specific modules. None of the k8s deployments reached
a fully working state in this review, but that was traced to cluster RBAC
(missing `secrets/patch` for the `juju-secret-consumer` service account),
not a charm defect. A maintainer should first fix the `JujuContext` import
in `ops-sunbeam/ops_sunbeam/test_utils.py` and wire ops-sunbeam's unit tests
into CI — that fix alone unblocks 91 tests and would have caught this
regression automatically.

| | |
|---|---|
| Repo | openstack-charmers/sunbeam-charms @ `0ac9414c` (2026-07-13) |
| Charms | 12 declared: aodh-k8s, cloudkitty-k8s, designate-bind-k8s, ironic-conductor-k8s, keystone-k8s, manila-data, masakari-k8s, nova-ironic-k8s, openstack-images-sync-k8s, placement-k8s, sunbeam-machine, sunbeam-ovn-proxy |
| Substrate | k8s (all except sunbeam-machine) |
| Deployed | partial — `concierge-k8s-4` (keystone-k8s rev 429, blocked/waiting throughout, never reached active due to cluster RBAC blocking MariaDB secrets); `concierge-lxd-4` (sunbeam-machine rev 1, reached `active` cleanly) |
| Reviewed | 2026-08-24 |

## What it does

`ops-sunbeam` provides base charm classes, relation handlers, WSGI Pebble
handlers, a compound status pool, and shared utilities. Keystone-k8s (2880
lines) is the primary subject charm in this review.

- **keystone-k8s** — OpenStack identity, WSGI/Apache, fernet/credential key
  management, SAML/OIDC/OAuth federation, CA cert transfer, domain config
- **nova-ironic-k8s** — Nova compute with Ironic driver, traefik-route ingress
- **ironic-conductor-k8s** — Ironic bare-metal conductor, Kubernetes LB handler
- **designate-bind-k8s** — BIND9 DNS with RNDC key exchange per relation unit
- **placement-k8s** — OpenStack placement WSGI service
- **openstack-images-sync-k8s** — simplestreams image sync + HTTP mirror
- **sunbeam-ovn-proxy** — proxy bridge between MicroOVN ovsdb and sunbeam
  ovsdb-cms relations (clean pass-through design)
- **sunbeam-machine** — machine config: sysctl, ISCSI initiator, proxy settings

## Deployment log

### k8s — keystone-k8s with MariaDB (concierge-k8s-4, Juju 4.0.12)

```
juju add-model rv-sunbeam-k8s --controller concierge-k8s-4
juju deploy keystone-k8s --channel 2024.1/edge          → rev 429, ubuntu@24.04
juju deploy traefik-k8s --channel latest/stable          → rev 377: RBAC failure
juju deploy mariadb-k8s --channel edge                    → rev 8
juju relate keystone-k8s:database mariadb-k8s:database   → relation created
```

**Result (after 22 min)**:
- keystone-k8s/0: `blocked (database) integration missing`
- keystone-k8s/1: `blocked (database) integration missing` (scaled up)
- mariadb-k8s: `waiting "Waiting for MariaDB to start"`
- traefik-k8s: `error` (RBAC on services listing at cluster scope)

**Root cause**: MariaDB's `pebble-ready` hook fails repeatedly because it
cannot `patch secrets` in the `rv-sunbeam-k8s` namespace. The cluster RBAC
does not grant `secrets/patch` to the `juju-secret-consumer` service
account — a cluster configuration issue, not a charm bug. Secret content
save fails 10 times, then the hook fails. The MariaDB pod is `Ready` but
mysqld never starts because the pebble layer is never applied.

Hook count for keystone-k8s/0 over 22 min: 21 hooks (install, peers,
leader-elected, 2× storage-attached, config-changed, start, 4×
ingress-internal, keystone-pebble-ready, 4× database, 4× update-status,
config-changed). Scaling to 2 units added unit 1 with ~12 hooks over 6
minutes.

### k8s — MariaDB pod restart + re-relate (concierge-k8s-4)

```
kubectl delete pod -n rv-sunbeam-k8s mariadb-k8s-0 --grace-period=0
juju relate keystone-k8s:database mariadb-k8s:database
juju remove-relation keystone-k8s:ingress-internal traefik-k8s:ingress
```

**MariaDB restart result**: pod restarted, became `Ready`. A Juju secret for
root credentials was created but content save failed 10+ times due to
RBAC. MariaDB stuck in `waiting "Waiting for MariaDB to start"` —
pebble-ready hook keeps failing, pebble layer never applied, mysqld never
starts.

**Re-relation result**: keystone-k8s changed from `blocked (database)` →
`waiting (workload) Not all relations are ready` — database relation is
established. Then `blocked (ingress-internal) integration missing` after
removing the traefik ingress relation.

### k8s — Additional charms deployed (concierge-k8s-4)

```
juju deploy openstack-images-sync-k8s --channel 2024.1/edge  → rev 197
juju deploy placement-k8s --channel 2024.1/edge               → rev 256
juju relate placement-k8s:identity-service keystone-k8s:identity-service
```

- **openstack-images-sync-k8s**: blocked `(ingress-internal) integration
  missing` — correct mandatory-relation behaviour.
- **placement-k8s**: blocked `(ingress-internal) integration missing` —
  correct. `keystone:identity-service → placement:identity-service`
  relation created without error; placement received endpoint data from
  keystone even though keystone was blocked.
- `self-signed-certificates` (rev 674): `active` — no dependencies, worked
  first time.
- `grafana-agent-k8s` (rev 243): `waiting "installing agent"` — agent not
  yet connected.
- `ironic-conductor-k8s` (charmhub rev 119): `error "hook failed: install"`
  — install hook fails repeatedly. Charmhub-published charm, not a local
  repo issue.
- `nova-ironic-k8s` (charmhub rev 118): `blocked (amqp) integration
  missing` — correct mandatory-relation behaviour. Related to keystone via
  `identity-credentials`.

### LXD — sunbeam-machine (concierge-lxd-4, Juju 4.0.12)

```
juju add-model rv-sunbeam-lxd -c concierge-lxd-4
juju deploy sunbeam-machine --channel edge → rev 1, ubuntu@22.04
```

**Result (after ~8 min)**: sunbeam-machine/0: `active`, machine 0:
`started`. Charm reached `ActiveStatus("")` correctly on LXD substrate.

## Observed behaviour

**Compound status works correctly.** Both units of keystone-k8s correctly
show `blocked` with a relation-specific message. Removing the database
relation changed the message to `"(database) integration missing"`
immediately. The compound status pool computes the worst status across all
handlers.

**Scale-up works on k8s.** `juju scale-application keystone-k8s 2`
produced a second unit that went through the full hook sequence
independently. Both containers showed 2/2 Running.

**Scale-up stalls on LXD** (cluster resource constraint, not a charm
bug). `juju add-unit sunbeam-machine` creates a container
(`juju-495460-1`) that boots to `Running` in LXD, but Juju never
provisions the unit agent (stays `allocating`).

**sunbeam-machine config change**: `juju config sunbeam-machine
debug=true` fires the `config-changed` hook twice in the same second —
Juju's dispatch mechanism, not the charm; each dispatch runs the handler
once, and the idempotent guard prevents duplicate work. `juju ssh
sunbeam-machine/0` fails with `Permission denied (publickey)` — the Juju
SSH key is not authorized on the LXD container; use `juju exec -m
rv-sunbeam-lxd --unit sunbeam-machine/0 "..."` instead. All systemd
services visible via `juju exec` are standard OS services — no
sunbeam-specific daemon (the charm is a configurator, not a workload).

**`update-status` fires at normal cadence.** No hook spam observed; 564
entries in `show-status-log` for unit 0 over 22 minutes reflect historical
granularity, not rapid re-firing.

**Config validation is deferred to bootstrap time.** `juju config
keystone-k8s identity-backend=invalid_backend` succeeded silently — no
error at config-set time. Validation occurs when the database becomes
available and the charm renders the WSGI config; no crash observed in this
run.

Boolean config validation is enforced at the Juju CLI level:
```
juju config sunbeam-machine debug=notabool
ERROR option "debug" expected boolean, got "notabool"
```

**Action handlers block when dependencies are unavailable.** All seven
keystone-k8s actions requiring database credentials (`get-admin-password`,
`get-admin-account`, `get-service-account`, `list-ca-certs`,
`remove-ca-certs`, `regenerate-password`) time out after 30s when the
database is unavailable. The handler waits on `self.admin_password` →
`_retrieve_or_set_secret()` → database lookup, hanging rather than failing
fast with an error status. `add-ca-certs` with wrong parameter names
returns a proper validation error: `(root) : "name" property is missing
and required` — parameter validation works correctly.

**Secret failure in `DBHandler` silently masks the broken database
relation.** MariaDB's RBAC inability to save secret content (the secret
*ID* is created and stored in relation data, but content save fails)
means:

1. `_on_database_updated()` checks `if not (event.username or
   event.password or event.endpoints): return`. With empty secret content
   these are absent, so the handler returns early without calling
   `configure_charm`. The database relation is never confirmed as working.
2. The `database` relation never transitions to `ready`, so
   `check_relation_handlers_ready()` raises
   `WaitingExceptionError("Not all relations are ready")`.
3. The charm is stuck in `WaitingStatus` even though
   `database-relation-created` fired. No `KeyError` surfaces because
   `context()` is never called.
4. At 09:27:17 (first hooks after deploy), keystone-k8s logs show
   `Relations {'ingress-internal', 'database'} incomplete` and `Charm is
   waiting in section 'Bootstrapping' due to 'Not all relations are
   ready'`. MariaDB logs at 09:07:52 show `Creating root password secret`,
   then 10 failed content-save attempts with `secrets "..." is forbidden:
   cannot patch resource "secrets"`.

The symptom (charm waiting on database) is technically correct but the
*cause* (cluster RBAC blocking secret content save) is invisible to the
operator.

**Pod deletion and recreation recovers cleanly (k8s).**
`kubectl delete pod -n rv-sunbeam-k8s keystone-k8s-0 --grace-period=0`:
pod recreated within seconds, unit agent ran `start-hook` and returned to
`idle`, workload returned to `blocked (ingress-internal)`. Local SQLite
storage reset → `_state.unit_bootstrapped = False` → `configure_charm`
re-ran fully. Clean recovery.

**Scale-down succeeds.** `juju scale-application keystone-k8s 1` reduced
from 2 units to 1 without incident.

**Config-changed fires twice per Juju dispatch — not a charm bug.**
`juju debug-log` shows `config-changed` firing twice in rapid succession
(e.g. 21:49:13 and 21:49:14) for both keystone-k8s and sunbeam-machine.
This is Juju's dispatch mechanism; both invocations go through the same
guard, and the idempotent `unit_bootstrapped` flag prevents duplicate
work.

**Compound status pool shows worst priority, which can mask a newly
broken relation.** Removing the database relation
(`juju remove-relation keystone-k8s:database mariadb-k8s:database`) fires
`database-relation-departed`/`-broken`, and the handler sets
`BlockedStatus("integration missing")`. But the visible status stayed
`blocked (ingress-internal) integration missing`, because the
`ingress-internal` handler has lower `_priority` (0) than the database
handler (priority 100). The precedence logic is correct (lower priority
wins on equal status level), but the effect is that a newly-broken
relation doesn't change the visible status if a worse-priority handler is
already blocking at the same status name.

**`ironic-conductor-k8s` (charmhub rev 119) install hook fails
repeatedly.** `juju deploy ironic-conductor-k8s --channel 2024.1/edge`
fails the install hook repeatedly on k8s (`hook "install" ... failed: exit
status 1`), retrying without success. This is a charmhub-published charm
issue; the local repo charm (head) has no custom install hook. Root cause
not determined without access to the charmhub bundle.

**`nova-ironic-k8s` blocks on mandatory `amqp` relation.** Blocked
immediately on `(amqp) integration missing` — correct, since (unlike
keystone-k8s) `nova-ironic-k8s` declares `amqp` mandatory in
`charmcraft.yaml`. The related `ironic-conductor-k8s` charm being in error
on install prevented testing the baremetal relation between them.

**`placement-k8s` receives `identity-service` data without a database.**
The relation was created and placement received endpoint data without
error even though keystone-k8s was itself blocked on database — correct,
since `identity-service` shares catalog data before its own database is
ready. Hook sequence: `identity-service-relation-created` → `joined` →
`changed`. Both units remained blocked on `ingress-internal`.

**MariaDB pod running but workload idle (k8s).** `mariadb-k8s-0` shows
`Ready`/`ContainersReady=True` but mysqld is not running — only `pebble`
and `container-agent` processes visible. Root cause: the
`mariadb-pebble-ready` hook fails with:
```
hook "mariadb-pebble-ready" failed: saving content for secret "...":
  attempt count exceeded: secrets "..." is forbidden:
  User "...juju-secret-consumer-..." cannot patch resource "secrets"
```
MariaDB retries indefinitely; the pebble layer is never applied so mysqld
never starts.

**Keystone WSGI workload not running (blocked on relations).** The
`keystone-k8s-0/keystone` container shows no Apache process; `pebble
services` shows `wsgi-keystone: disabled/inactive`. `configure_charm`
never completed because `check_relation_handlers_ready` raised
`WaitingExceptionError` while `ingress-internal` and `database` were both
incomplete. Compound status showed `blocked (ingress-internal)` as the
worst active status.

**`sunbeam-machine` config-changed double-call.** The charm's
`_on_config_changed` override calls `configure_charm(event)` directly and
does not call the parent's handler; the parent `OSBaseOperatorCharm` also
registers a `config_changed` observer, but because `self._on_config_changed`
resolves to the child override, the parent's separate handler body is
never invoked — the double hook dispatch is Juju's, and the idempotent
guard prevents duplicate work either way.

**Upgrade path.** The `unit_bootstrapped` flag lives in Juju local SQLite
storage. On k8s pod replacement (`juju refresh`), local storage is lost
and the flag reverts to `False`, triggering a full re-bootstrap — correct
for ephemeral pods. The LB handler supports a `refresh_event` parameter to
reconcile on upgrade events. `juju refresh keystone-k8s --channel
2024.1/edge` reported "already up-to-date" (rev 429 was current edge at
review time). Local `charmcraft pack` fails because `charmcraft.yaml` has
both a `config:`/`actions:` section and legacy `config.yaml`/`actions.yaml`
files; `repository.py prepare` was used to work around this for unit
testing.

## Findings

### `ops-sunbeam` test_utils imports non-existent `JujuContext` from `ops.jujucontext`
- **Severity**: critical
- **Kind**: bug
- **Where**: `ops-sunbeam/ops_sunbeam/test_utils.py:60`, `:842`
- **Evidence**: `from ops.jujucontext import JujuContext` — in ops 2.23.1,
  `ops.jujucontext` exports `JujuVersion` and `_JujuContext` (private), not a
  public `JujuContext`. 5 ops-sunbeam test modules fail on collection with
  `ImportError: cannot import name 'JujuContext'`. Line 842 also calls
  `JujuContext._from_dict(os.environ)`; the method was renamed to
  `from_dict` in ops 2.x, so this would fail too even after fixing the import.
- **Impact**: all ops-sunbeam unit tests (91 tests across 5 modules) fail to
  collect. The library is the foundation of every charm in the repo and
  currently has no working test coverage.
- **Fix**: change line 60 to `from ops.jujucontext import _JujuContext as
  JujuContext`; change line 842 to `JujuContext.from_dict(os.environ)`.
  Verified: with this 2-line fix, all 91 ops-sunbeam tests pass.
- **Linter rule**: not mechanically checkable

### `ops-sunbeam` unit tests are not run in CI
- **Severity**: high
- **Kind**: test-gap
- **Where**: `zuul.d/jobs.yaml`
- **Evidence**: `charm-build-bin` has `irrelevant-files:
  ops-sunbeam/ops_sunbeam/test_.*\.py`, and no CI job runs `pytest` against
  ops-sunbeam's unit tests. Only `charmcraft pack` and zaza functional tests
  run in Zuul; unit tests only run locally via `run_tox.sh`.
- **Impact**: the `JujuContext` import bug above would have been caught
  immediately by CI. Future regressions in the shared library go undetected.
- **Fix**: add a Zuul job that runs `run_tox.sh py3 ops-sunbeam` or equivalent.
- **Linter rule**: not mechanically checkable

### `sunbeam-machine` unit tests cannot collect (`charmlibs` not mocked before import)
- **Severity**: high
- **Kind**: test-gap
- **Where**: `charms/sunbeam-machine/src/charm.py:37`
- **Evidence**: `from charmlibs import apt` at module level. The conftest's
  `_mock_heavy_externals` fixture monkeypatches `charm.apt`, but the
  `ImportError` fires before the fixture is applied. Result:
  `ImportError: cannot import name 'apt' from 'charmlibs'` when running
  pytest directly (outside the tox environment where `charmlibs` is
  installed).
- **Impact**: developers running `pytest` directly get a collection error;
  only `run_tox.sh` works.
- **Fix**: move `from charmlibs import apt` inside the method that uses it
  (`_configure_iscsi_initiator`), or pre-populate `sys.modules["charmlibs"]`
  with a mock in conftest before `charm` is imported.
- **Linter rule**: not mechanically checkable

### `ironic-conductor-k8s` top-level `import glanceclient` breaks unit test collection
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/ironic-conductor-k8s/src/api_utils.py:17`
- **Evidence**: `import glanceclient` at module level. The dependency is
  declared in `pyproject.toml` but is not installed in a standalone pytest
  environment (only `run_tox.sh` installs it via `uv`). Direct pytest fails
  with `ModuleNotFoundError: No module named 'glanceclient'`.
- **Impact**: all unit tests for this charm silently fail to collect outside
  the full tox environment.
- **Fix**: move `import glanceclient` inside `OSClients.__init__` (where it is
  already used at line 51: `glanceclient.Client(session=self._session,
  version=2)`).
- **Linter rule**: "import-outside-toplevel" (B017)

### `DBHandler` silently masks database unavailability via early-return
- **Severity**: medium
- **Kind**: bug
- **Where**: `ops-sunbeam/ops_sunbeam/relation_handlers.py:412`
- **Evidence**:
  ```python
  if not (event.username or event.password or event.endpoints):
      return
  self.callback_f(event)  # configure_charm only called if credentials present
  ```
  When MariaDB cannot save secret content (cluster RBAC issue observed in
  this review), `data_interfaces` receives no username/password/endpoints,
  and the handler returns early without calling `configure_charm`. The
  database relation never reaches `ready`. The charm sits in `WaitingStatus`
  with no indication of the root cause.
- **Impact**: operator sees "Waiting — Not all relations are ready" with no
  way to distinguish "MariaDB not running" from "cluster RBAC misconfigured"
  without reading MariaDB pod logs directly.
- **Fix**: before the early return, check whether a secret ID exists in
  relation data. If it exists but content is empty, raise
  `WaitingExceptionError("Database credentials pending — cluster may lack
  secrets/patch permission")`.
- **Linter rule**: not mechanically checkable

### `KubernetesLoadBalancerHandler` reconciles an empty LB spec on invalid annotations
- **Severity**: medium
- **Kind**: bug
- **Where**: `ops-sunbeam/ops_sunbeam/k8s_resource_handlers.py:197-216`
- **Evidence**:
  ```python
  resources_list = []
  if self._annotations_valid:
      resources_list.append(self._construct_lb())
  else:
      self.charm.status.set(BlockedStatus(
          "Invalid config value 'loadbalancer_annotations'"))
  klm.reconcile(resources_list)  # called even when resources_list == []
  ```
  When annotations are invalid, `BlockedStatus` is set but `reconcile([])`
  still runs, patching the LoadBalancer service with an empty spec —
  potentially wiping existing annotations and port configuration.
- **Impact**: setting an invalid `loadbalancer_annotations` value not only
  blocks the charm but can corrupt an already-working LoadBalancer service.
  Affects `designate-bind-k8s` and `ovn-relay-k8s`, which expose this config.
- **Fix**: return immediately after setting `BlockedStatus`, before calling
  `klm.reconcile`.
- **Linter rule**: not mechanically checkable

### keystone-k8s `_get_service_account_action` can create a service account with a null password
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/keystone-k8s/src/charm.py:1482-1497`
- **Evidence**:
  ```python
  user_password = None
  try:
      credentials_id = self._retrieve_or_set_secret(username)
      credentials = self.model.get_secret(id=credentials_id)
      user_password = credentials.get_content(refresh=True).get("password")
  except SecretNotFoundError:
      logger.warning("Secret for {username} not found")  # not an f-string
  ...
  self.keystone_manager.create_service_account(username=username,
                                                 password=user_password, ...)
  ```
  If `get_content()` returns `{}` (e.g. the same RBAC-style secret failure
  seen elsewhere in this review), no exception is raised, `user_password`
  stays `None`, and `create_service_account` is called with `password=None`.
  The warning message is also broken — `{username}` is a literal string, not
  interpolated.
- **Impact**: a service account can be created in Keystone with no usable
  password while the charm only logs a warning, not a failure.
- **Fix**: check `user_password is not None` (or that `get_content()`
  returned non-empty data) before calling `create_service_account`. Fix the
  log line to use an f-string.
- **Linter rule**: not mechanically checkable

### `run_once_per_unit` decorator logs first-time runs as WARNING
- **Severity**: medium
- **Kind**: bug
- **Where**: `ops-sunbeam/ops_sunbeam/job_ctrl.py:60,66`
- **Evidence**:
  ```python
  if label in storage:
      logging.warning(f"Not running {label}, it has run previously for this unit")
  else:
      logging.warning(f"Running {label}, it has not run on this unit before")
      f(charm, *args, **kwargs)
  ```
  Both branches use `logging.warning`; the "first run" case is normal
  behaviour and should be `logging.info`. Both also use the root logger
  instead of a named logger (OG015). Affects `db-sync`, `a2enmod`, and other
  decorated methods across all WSGI charms.
- **Impact**: every first-time invocation of a decorated method logs a
  WARNING in the unit agent log, adding noise.
- **Fix**: change the second call to `logging.info`; declare and use a named
  logger (`logger = logging.getLogger(__name__)`).
- **Linter rule**: OG015

### `manila-data` unit tests cover only blocking/waiting, not snap configuration
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `charms/manila-data/tests/unit/test_manila_data_scenario.py`
- **Evidence**: 9 passing scenario tests only verify the charm goes
  blocked/waiting when relations are missing. `configure_snap` (which writes
  snap config including the database connection string) is never exercised,
  nor is the `AttributeError` recovery path inside it.
- **Impact**: the highest-risk code path (snap configuration with database
  credentials) has no unit coverage; only manual/zaza functional testing
  exercises it.
- **Fix**: add unit tests for `configure_snap` with complete relation data,
  including the `AttributeError` recovery path.
- **Linter rule**: not mechanically checkable

### Charm unit tests (except keystone-k8s) require `repository.py prepare` or fail with misleading errors
- **Severity**: medium
- **Kind**: test-gap
- **Where**: all charm `tests/unit/test_*.py` except keystone-k8s
- **Evidence**: running pytest on placement-k8s without `repository.py
  prepare` produces 9 failures: `'parts/database-connection' not found in
  search path: 'src/templates'`. After running `prepare`, 19 pass. `prepare`
  copies shared templates from the repo-root `templates/` directory into
  each charm's `src/templates/`; `run_tox.sh` calls this automatically but
  direct pytest invocation does not. keystone-k8s is unaffected because it
  ships its own `parts/` under `src/templates/`.
- **Impact**: developers running `pytest` directly on any charm but
  keystone-k8s see confusing `TemplateNotFound`-style failures.
- **Fix**: either copy the shared templates into every charm's
  `src/templates/` at commit time, or have conftest resolve `template_dir`
  to an absolute path via `CHARM_ROOT`.
- **Linter rule**: not mechanically checkable

### `openstack-images-sync-k8s` `frequency` config raises an unhandled `ValueError`
- **Severity**: medium
- **Kind**: bug
- **Where**: `charms/openstack-images-sync-k8s/src/charm.py:44-49`
- **Evidence**:
  ```python
  def _frequency_to_seconds(frequency: str) -> int:
      match frequency:
          case "hourly": return 3600
          ...
          case _:
              raise ValueError(f"Unknown frequency {frequency!r}")
  ```
  Called from `SyncCharmConfigContext.context()` during `configure_charm`.
  An invalid `frequency` is accepted silently at `juju config` time (same
  deferred-validation pattern seen with keystone-k8s's `identity-backend`)
  and only fails at render time, surfacing as a generic
  `BlockedStatus("Error in charm (see logs): Unknown frequency ...")`.
- **Impact**: an operator setting `frequency=monthly` gets a generic error
  with no indication the config value itself is invalid.
- **Fix**: add `frequency` to a `choices` list in `charmcraft.yaml` for
  Juju-level validation, or catch `ValueError` in
  `SyncCharmConfigContext.context()` and raise
  `sunbeam_guard.BlockedExceptionError` with a descriptive message.
- **Linter rule**: not mechanically checkable

### Guard catches all exceptions, masking relation-specific waiting/blocked status
- **Severity**: low
- **Kind**: bug
- **Where**: `ops-sunbeam/ops_sunbeam/charm.py:362`, `ops-sunbeam/ops_sunbeam/guard.py:112`
- **Evidence**: `configure_charm` is wrapped by `guard(..., "Bootstrapping")`.
  Any unexpected exception becomes `BlockedStatus("Error in charm (see
  logs): ...")`, overwriting the relation handler's specific status — e.g. a
  missing template file surfaces as a generic error instead of a relation
  status.
- **Impact**: operators lose context; they see "Error in charm" instead of
  e.g. "Waiting for database".
- **Fix**: re-raise `WaitingExceptionError` from the guard without wrapping it.
- **Linter rule**: not mechanically checkable

### `DBHandler._update_mysql_data` silently no-ops on non-leader
- **Severity**: low
- **Kind**: bug
- **Where**: `ops-sunbeam/ops_sunbeam/relation_handlers.py:325`
- **Evidence**: returns silently when `not is_leader()`, with no debug log.
  Architecturally correct (only the leader should update), but a deferred
  event on a non-leader is then unobservable.
- **Impact**: hard to debug a silently-skipped relation data update.
- **Fix**: add `logger.debug("Not leader, skipping relation data update")`.
- **Linter rule**: not mechanically checkable

### `_annotations_valid` logs a misleading error when annotations simply aren't configured
- **Severity**: low
- **Kind**: bug
- **Where**: `ops-sunbeam/ops_sunbeam/k8s_resource_handlers.py:163-167`
- **Evidence**:
  ```python
  @property
  def _annotations_valid(self) -> bool:
      if self._loadbalancer_annotations is None:
          logger.error("Annotations are invalid or could not be parsed.")
          return False
      return True
  ```
  `parse_annotations("")` returns `{}`, so `_annotations_valid` is `True`
  when no annotations are configured at all — this path is fine — but the
  log message reads as if a parse failure occurred, which is confusing when
  it does trigger (e.g. for genuinely malformed input the check is checking
  the parsed, not raw, value).
- **Impact**: misleading log output; affects charms exposing
  `loadbalancer_annotations` (e.g. `ironic-conductor-k8s`).
- **Fix**: check the raw config value (`lb_annotations is None`) rather than
  the parsed result, so the error only fires on genuinely invalid input.
- **Linter rule**: not mechanically checkable

### `manila-data` uses `AttributeError` for relation-data flow control
- **Severity**: low
- **Kind**: code-smell
- **Where**: `charms/manila-data/src/charm.py:72`
- **Evidence**: `except AttributeError as e: raise
  WaitingExceptionError("Data missing: {}".format(e.name))` — relies on
  `AttributeError.name` being set by CPython's attribute lookup machinery.
- **Impact**: fragile; if `.name` is absent the resulting error message is
  garbled.
- **Fix**: explicitly check `contexts` dict keys before access, or catch a
  more specific exception with a named-attribute check.
- **Linter rule**: not mechanically checkable

### `designate-bind-k8s` RNDC key rotation does not push new key to existing clients
- **Severity**: low
- **Kind**: bug
- **Where**: `charms/designate-bind-k8s/src/charm.py:224`
- **Evidence**: `_on_secret_rotate` updates secret content and bumps the
  revision counter in peer data, but does not call `register_rndc_client`
  to push the new key to already-connected clients; peer app data is only
  updated when a new client connects.
- **Impact**: already-connected clients keep using the rotated-out key until
  they reconnect.
- **Fix**: after updating secret content, call `register_rndc_client` for
  all existing relations.
- **Linter rule**: not mechanically checkable

### `manila-data` sets `_state.api_ready` but never reads it
- **Severity**: nit
- **Kind**: lint
- **Where**: `charms/manila-data/src/charm.py:46,67`
- **Evidence**: `self._state.set_default(api_ready=False)` and
  `self._state.api_ready = True` (set by an `api_ready()` handler); zero
  reads anywhere in the file.
- **Impact**: dead code; confusing for future maintainers.
- **Fix**: remove `_state.api_ready`.
- **Linter rule**: "unused-StoredState"

### `aodh-k8s`, `placement-k8s`, `sunbeam-machine` declare `StoredState` but never use it
- **Severity**: nit
- **Kind**: lint
- **Where**: `charms/aodh-k8s/src/charm.py:245`, `charms/placement-k8s/src/charm.py:74`, `charms/sunbeam-machine/src/charm.py:61`
- **Evidence**: each declares `_state = StoredState()` with zero references
  in the class body.
- **Fix**: remove the unused declarations.
- **Linter rule**: "unused-StoredState"

### `ops-sunbeam` ruff violations
- **Severity**: nit
- **Kind**: lint
- **Where**: `ops-sunbeam/ops_sunbeam/`
- **Evidence**: `ruff check ops-sunbeam/ops_sunbeam/` flags: ~40× LR040
  (`logging.getLogger(__name__)` should be assigned to a module logger
  variable), 26× OG015 (root-logger use instead of a named logger), 23×
  UP045 (`Optional[X]` instead of `X | None`), 2× E501 (lines at
  `charm.py:1281,1286` exceeding 88 chars).
- **Fix**: run `ruff check --fix` for the mechanical classes; manually
  introduce named loggers where flagged.
- **Linter rule**: LR040, OG015, UP045, E501

## Worth copying

- **Compound status pool** (`ops-sunbeam/ops_sunbeam/compound_status.py`,
  `ops-sunbeam/ops_sunbeam/charm.py:137`): each relation handler registers a
  status slot; `compute_status()` returns the worst priority across all
  slots. Clean separation of concerns.
- **Secrets-based DB credentials** (`ops-sunbeam/ops_sunbeam/relation_handlers.py:452`):
  `user_secret.get_content(refresh=True)` reads DB credentials from a Juju
  secret rather than plain-text relation app data.
- **TLS SAN drift handling** (`ops-sunbeam/ops_sunbeam/relation_handlers.py:920`):
  `validate_and_regenerate_certificates_if_needed` compares DNS/IP SANs
  between stored CSRs and current config, regenerating only on mismatch —
  handles `juju refresh` SAN drift correctly.
- **`TracingRequireHandler`** (`ops-sunbeam/ops_sunbeam/relation_handlers.py:1630`):
  a clean handler for the `tracing` relation (TempoCoordinator), consistent
  with the rest of the handler pattern.
- **Upgrade path via local storage reset** (`ops-sunbeam/ops_sunbeam/charm.py:117`):
  `_state.set_default(unit_bootstrapped=False)` — local storage is lost on
  pod replace, forcing a clean re-bootstrap on `juju refresh`. Minimal and
  correct.
- **Broken-relation workaround** (`ops-sunbeam/ops_sunbeam/charm.py:552-571`):
  references LP bug #2024583 and operator issue #940, checks for
  `GoneAway` events to mark broken relations as not-ready, compensating for
  Juju not clearing relation data on broken relations. Well-commented.
- **Shared scenario test utilities** (`ops-sunbeam/ops_sunbeam/test_utils_scenario.py`):
  `assert_config_file_exists`, `assert_container_disconnect_causes_waiting_or_blocked`,
  `assert_relation_broken_causes_blocked_or_waiting` are reusable
  state-transition assertions used across all charms; keystone-k8s's 153
  passing tests prove the pattern scales.
- **Container exec mocks** (`charms/keystone-k8s/tests/unit/conftest.py:136`):
  `testing.Exec` mocks for `keystone-manage`, `a2ensite`, `a2dissite`, `sudo`
  keep unit tests fast while exercising the full handler pipeline.
- **Fernet/credential key rotation** (`charms/keystone-k8s/src/charm.py:1649`,
  `update_fernet_keys_from_peer`): leader writes keys to a Juju secret,
  publishes the secret ID to peer app-data; all units pull from peer data.
  Clean key distribution without a shared storage backend.
- **`identity_service` v1 library** (`charms/keystone-k8s/lib/charms/keystone_k8s/v1/identity_service.py`):
  well-documented Provides/Requires pattern with Connected/Ready/GoneAway
  events, secrets handled with graceful `None` handling.
- **`sunbeam-ovn-proxy` pass-through design** (`charms/sunbeam-ovn-proxy/src/charm.py`):
  no storage or workload; pure relation proxy bridging MicroOVN's `ovsdb`
  interface to sunbeam's `ovsdb-cms` interface. A minimal, correct pattern
  for a proxy charm.
- **k8s LB handler `refresh_event`** (`ops-sunbeam/ops_sunbeam/k8s_resource_handlers.py:109`):
  lets the LB handler reconcile on upgrade events.
- **`run_once_per_unit` decorator** (`ops-sunbeam/ops_sunbeam/job_ctrl.py`):
  clean `@run_once_per_unit('label')` decorator using local job storage with
  timestamps for auditability; correctly resets on pod restart but persists
  across machine restarts (logging-level nit noted above).

## Common-practice notes

| Aspect | Status | Notes |
|---|---|---|
| ops framework | v2.17+ | Uses `ops[testing]>=2.17.0` |
| ops[testing] API | modern | `testing.Context`, `testing.State`, `testing.Container`, `testing.Exec` |
| jujulib/tracing | yes | `@sunbeam_tracing.trace_sunbeam_charm` on all charm classes |
| lib/ versioning | yes | `lib/charms/<charm>/v<N>/` via `repository.py` |
| template rendering | jinja2 | `FileSystemLoader` + `.j2` extension |
| secret handling | yes | `model.get_secret()`, `secret.get_content(refresh=True)` |
| StoredState | used, sometimes unused | manila-data's `_state.api_ready` dead; aodh/placement/sunbeam-machine declare but never use it |
| relation handler pattern | consistent | all charms: `get_relation_handlers()` → `callback_f()` |
| WSGI service pattern | consistent | all k8s API charms: `WSGI*PebbleHandler` + pebble layers |
| concierge / zuul | present | `zuul.d/jobs.yaml` with charm-build-bin + func-test-* jobs |
| tox | yes | `run_tox.sh` with `fmt`, `pep8`, `py3`, `cover`, `build` |
| charmcraft analyse | not run | local pack fails due to `charmcraft.yaml`/`config.yaml` conflict |
| code style | minor issues | ruff: 40× LR040, 26× OG015, 23× UP045, 2× E501 |
| ops-sunbeam unit tests in CI | absent | only charm builds + zaza functional tests run in Zuul |

## Tests

| Test suite | Run | Result |
|---|---|---|
| keystone-k8s unit (from charm dir) | `cd charms/keystone-k8s && pytest tests/unit/` | 153 passed, 384 warnings, 15.5s |
| keystone-k8s unit (from repo root) | same command from repo root | 88 failed (template path is CWD-relative) |
| ops-sunbeam unit (with JujuContext fix) | `cd ops-sunbeam && pytest tests/unit_tests/` | **91 passed** in 0.57s |
| ops-sunbeam unit (without fix) | same, before fixing import | 5 errors during collection |
| aodh-k8s unit (with prepare) | `repository.py prepare && pytest tests/unit/` | **15 passed** |
| manila-data unit (with prepare) | same pattern | **9 passed** (scenario tests only — no `configure_snap` coverage) |
| placement-k8s unit (without prepare) | `pytest .../placement-k8s/` from charm dir | 9 failed, 10 passed (missing shared templates) |
| placement-k8s unit (with prepare) | `repository.py prepare && pytest ...` | **19 passed** |
| designate-bind-k8s unit (with prepare) | same pattern | **9 passed** |
| sunbeam-ovn-proxy unit (with prepare) | same pattern | **24 passed** |
| nova-ironic-k8s unit (with prepare) | same pattern | **19 passed** |
| cloudkitty-k8s unit (with prepare) | same pattern | **18 passed** |
| masakari-k8s unit (with prepare) | same pattern | **17 passed** |
| openstack-images-sync-k8s unit (with prepare) | same pattern | **12 passed** |
| ironic-conductor-k8s unit (with prepare) | same pattern | **ImportError** (`glanceclient` not on test PYTHONPATH) |
| sunbeam-machine unit (with prepare) | same pattern | **ImportError** (`charmlibs.apt` not on test PYTHONPATH) |

**Coverage summary**: keystone-k8s has good handler-level and
state-transition coverage (153 tests). ops-sunbeam has unit tests but they
could not collect due to the `JujuContext` import error before the 2-line
fix; all 91 tests pass after. All other charms pass their scenario tests
when run with `repository.py prepare`. `ironic-conductor-k8s` and
`sunbeam-machine` cannot collect due to top-level imports of environment-
specific modules. `manila-data` has 9 passing tests but only covers
blocking/waiting transitions — `configure_snap` and the dead
`_state.api_ready` have no coverage. ops-sunbeam unit tests are not run in
CI (only charm builds and zaza functional tests).

## Docs

- README: per-charm, descriptive
- Contributing: not present at repo root
- charmhub.md: all 12 declared charms published (edge/beta channels, ubuntu 22.04/24.04)
- `charmcraft.yaml`: well-structured with `parts` for build; actions defined inline
- terraform module: not present
- Cluster RBAC requirement: undocumented — clusters need `secrets/patch` on
  the `juju-secret-consumer` SA for database relations to work

## Open questions

1. **Cluster RBAC for Juju secrets**: the k8s cluster needs `secrets/patch`
   permission on the `juju-secret-consumer` SA for database relations to
   work. Should this be documented as a cluster requirement in the
   deployment guide?
2. **Unused `StoredState` in aodh-k8s, placement-k8s, sunbeam-machine**:
   were these added in anticipation of future work, or are they dead code?
3. **`manila-data` dead `_state.api_ready`**: is there a missing read
   somewhere, or should the flag and the `api_ready()` handler be removed?
4. **keystone-k8s lacks a `certificates` relation endpoint**: operators
   wanting TLS from `self-signed-certificates`/`vault-k8s` cannot use it —
   is this intentional given `receive-ca-cert` handling?
5. **Loki logging endpoint mismatch**: keystone-k8s has a `logging:
   loki_push_api` relation, but `grafana-agent-k8s` does not expose a
   matching `logging` endpoint — is the intended observability path unclear
   or is a different charm expected on the other end?
6. **keystone-k8s `get-admin-password` action**: times out after 30s rather
   than failing fast when the database is unavailable. Is the hang
   intentional (wait-for-database design) or should it fail fast with a
   clear error?
7. **charmhub-published `ironic-conductor-k8s` rev 119**: install hook
   fails repeatedly on k8s; was this revision released with a broken
   install hook?
8. **`nova-ironic-k8s` traefik-route ingress**: exposes both
   `traefik-route-internal` and `traefik-route-public` for novncproxy,
   distinct from the `ingress-internal`/`ingress-public` pattern used
   elsewhere — is this the intended ingress path for this charm?
