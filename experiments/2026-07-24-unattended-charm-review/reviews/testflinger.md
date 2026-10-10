# testflinger-k8s + testflinger-agent-host

testflinger-k8s wraps the Testflinger Flask API (machine test-queue orchestrator)
as a Pebble-managed gunicorn workload; testflinger-agent-host is a machine charm
that installs and supervises testflinger-agent processes on bare-metal/VM hosts.
Both are well-structured, use pydantic config validation and scenario-style unit
tests, and ship good ops idioms. But the k8s charm has a **critical,
deployment-blocking regression present in every published channel, including the
latest beta (rev 365, 2026-08-17)**: `_pebble_layer` calls `sys.exit()` whenever
MongoDB relation data is incomplete, so the Pebble layer is never added and the
workload never starts. The unit does not go to ErrorStatus — it sits in
WaitingStatus, retrying the failing hook every ~5s forever, with no operator
alert. A maintainer should fix `fetch_mongodb_relation_data` (guard against a
missing `endpoints` key) and remove `sys.exit()` from hook/action/property code
paths before anything else; those two changes resolve three of the five critical
findings below.

| | |
|---|---|
| Repo | canonical/testflinger @ `86e2beb` (2026-07-23) |
| Charms | testflinger-k8s (rev 365 beta), testflinger-agent-host (rev 124 edge) |
| Substrate | k8s (concierge-k8s-4, Juju 4.0.12) / machine (concierge-lxd, Juju 3.6.27; concierge-lxd-4, Juju 4.0.12) |
| Deployed | yes — k8s deployed and refreshed edge→stable→beta on concierge-k8s-4; machine charm deployed on concierge-lxd and concierge-lxd-4 |
| Reviewed | 2026-08-24 |

## What it does

testflinger-k8s deploys the Testflinger Flask API as a Pebble-controlled
gunicorn workload (port 5000, metrics on 9090). It relates to mongodb-k8s for
the main database and a separate mongodb-k8s instance for the CSFLE key vault,
and optionally to ingress (`traefik-k8s` or `nginx-ingress-integrator`). It
exposes Prometheus metrics and Grafana dashboards. Operators set admin
credentials via `set-admin-password` and rotate the MongoDB CSFLE master key via
`retry-key-rotation`. OIDC authentication is configurable.

testflinger-agent-host installs Docker, snaps (maas), supervisord, and the
testflinger-agent Python packages, then manages per-agent supervisord service
files driven by a git-configured agent-configs repo.

## Findings

### CRITICAL: `_pebble_layer` crashes via `sys.exit()` — service never starts
- **Severity**: critical
- **Kind**: bug
- **Where**: `server/charm/src/charm.py:211` (`_on_testflinger_pebble_ready`), property at `charm.py:379` (local HEAD) / `charm.py:419` (deployed rev 365)
- **Evidence**: `_on_testflinger_pebble_ready` reads `self._pebble_layer` before
  calling `container.add_layer()`. `_pebble_layer` calls `app_environment`,
  which calls `fetch_mongodb_relation_data()`, which calls `sys.exit()` when
  relation data is incomplete — before the layer is ever added. `pebble plan`
  in the workload container returns `{}`; `pebble services` returns
  `Plan has no services.`. Confirmed on rev 354 (edge, unit → ERROR via
  config-changed), rev 355 (stable, unit → WAITING, silent), and rev 365
  (beta, published 2026-08-17, **still broken**) — same traceback, same crash
  site, at all three revisions:
  ```
  File ".../charm.py", line 211, in _on_testflinger_pebble_ready
    container.add_layer("testflinger", self._pebble_layer, combine=True)
  File ".../charm.py", line 419, in _pebble_layer
  File ".../charm.py", line 436, in app_environment
  File ".../charm.py", line 474, in fetch_mongodb_relation_data
    if ":" in val.get("endpoints"):
  TypeError: argument of type 'NoneType' is not iterable
  hook "testflinger-pebble-ready" failed: exit status 1
  ```
  Deployed rev 365 line numbers (211/419/436/474) are offset by ~40 lines from
  local HEAD (211/379/431/473) in `_pebble_layer`, suggesting the built beta
  charm differs slightly from the reviewed git commit; the crash logic is
  identical.
- **Why it matters**: The testflinger service never starts. The unit sits in
  WaitingStatus, not ErrorStatus, so no monitoring/alerting keyed on ERROR will
  fire. The retry loop runs indefinitely (~5s interval). This is a shipping
  regression present in the newest published beta.
- **Fix**: Don't call `fetch_mongodb_relation_data()` unconditionally inside the
  `_pebble_layer` property. Build a layer with placeholder env vars when
  relation data is unavailable and update it when data arrives, or move the
  `fetch_mongodb_relation_data()` call out of the property into the handler
  body, after `add_layer()`.
- **Linter rule**: "Properties with side effects (network calls, `sys.exit`) must
  not be used in hot paths before I/O operations" — not mechanically checkable.

### CRITICAL: `fetch_mongodb_relation_data` crashes on missing `endpoints` key
- **Severity**: critical
- **Kind**: bug
- **Where**: `server/charm/src/charm.py:473`
- **Evidence**:
  ```python
  if ":" in val.get("endpoints"):
      host, port = val.get("endpoints").split(":")
  ```
  When `endpoints` is absent, `val.get("endpoints")` returns `None` and
  `":" in None` raises `TypeError: argument of type 'NoneType' is not iterable`.
  mongodb-k8s rev 117 provides only `{"database": "testflinger_db"}` in the
  relation data bag — no `endpoints`, `username`, `password`, or `uris` — because
  it uses the Juju secrets backend for credentials (confirmed by reading
  `data_platform_libs/v0/data_interfaces.py`, which merges relation-data-bag and
  secret data). testflinger-k8s reads only the relation data bag, so it sees an
  incomplete dict. The existing `if not val: continue` guard doesn't catch this
  because `{"database": "testflinger_db"}` is truthy — the loop enters and
  crashes. Present in all tested channels (354, 355, 365).
- **Why it matters**: This is the root cause behind all the pebble-ready and
  config-changed crashes above; any MongoDB relation providing partial data
  takes the unit down and it cannot self-heal.
- **Fix**:
  ```python
  endpoints = val.get("endpoints")
  if endpoints is None:
      continue
  if ":" in endpoints:
      host, port = endpoints.split(":")
  else:
      host = endpoints
      port = "27017"
  ```
- **Linter rule**: "dictionary access via `.get()` must guard against None before
  using the value in an `in` expression or `.split()` call" — mechanically
  checkable with ruff/pyright.

### CRITICAL: `retry-key-rotation` action kills unit agent if key is configured
- **Severity**: critical
- **Kind**: bug
- **Where**: `server/charm/src/charm.py:365`
- **Evidence**:
  ```python
  env = {
      **self.app_environment,   # calls fetch_mongodb_relation_data()
      "TESTFLINGER_SECRETS_MASTER_KEY": stored_key,
      "TESTFLINGER_SECRETS_NEW_MASTER_KEY": current_key,
  }
  ```
  The action handler does not catch the `sys.exit()` raised inside
  `app_environment` → `fetch_mongodb_relation_data()`. Observed:
  `retry-key-rotation` without a key configured fails gracefully
  ("testflinger_secrets_master_key is not configured"). With a key configured
  but incomplete relation data, the unit agent dies.
- **Why it matters**: The action meant to let an operator fix a rotation
  problem instead kills their own unit.
- **Fix**:
  ```python
  if not self.container.can_connect():
      event.fail("Container is not ready")
      return
  if not self.mongodb.fetch_relation_data():
      event.fail("Database relation not ready")
      return
  env = {**self.app_environment, ...}
  ```
- **Linter rule**: "Actions that call `app_environment` or `_pebble_layer` must
  guard against incomplete relation data first" — not mechanically checkable.

### HIGH: `sys.exit()` terminates the unit agent process, not just the hook
- **Severity**: high
- **Kind**: bug
- **Where**: `server/charm/src/charm.py:264` (relation-removed), `charm.py:467` (empty data), `charm.py:485` (loop completes without break)
- **Evidence**:
  ```python
  # relation-removed
  self.unit.status = ops.WaitingStatus("Waiting for database relation")
  sys.exit()
  # empty relation data
  self.unit.status = ops.WaitingStatus("Waiting for database relation")
  sys.exit()
  # loop completes without break
  logger.error("No database relation data found yet")
  sys.exit()
  ```
  `sys.exit()` raises `SystemExit`, which terminates the unit agent process;
  Juju restarts it, but the hook is not deferred cleanly. Unit tests use
  `pytest.raises(SystemExit)`, documenting the crash rather than correct
  behaviour. Confirmed by unit restarts in `juju debug-log` after each
  pebble-ready crash.
- **Why it matters**: In pebble-ready it prevents `add_layer` from ever running;
  in `retry-key-rotation` it kills the unit agent mid-action; in
  relation-removed it prevents clean deferral.
- **Fix**: Set status and `return` instead of `sys.exit()`; let Juju re-emit the
  hook when the condition changes.
- **Linter rule**: "Hook handlers must not call `sys.exit()` or `os._exit()`" —
  mechanically checkable with ruff S307.

### HIGH: pebble-ready crash does not put the unit in ERROR state
- **Severity**: high
- **Kind**: bug
- **Where**: Juju unit-agent behaviour interacting with `server/charm/src/charm.py:211`
- **Evidence**: On rev 355/365, `pebble-ready` crashes with `sys.exit()` but
  `juju status` shows "waiting", not "error"; `juju debug-log` shows repeating
  `hook "testflinger-pebble-ready" failed: exit status 1` every ~5s while the
  workload stays "waiting". By contrast, rev 354's config-changed crash puts
  the unit in ERROR.
- **Why it matters**: The pebble-ready failure mode is invisible in `juju
  status`; an operator relying on ERROR to page will not be alerted, and the
  retry loop runs forever.
- **Fix**: Replace `sys.exit()` with a status set + return so the unit reaches
  BlockedStatus with an actionable message.
- **Linter rule**: "`_on_pebble_ready` handlers must not call `sys.exit()`" —
  mechanically checkable with ruff S307.

### HIGH: Error visibility inconsistency across scaled units
- **Severity**: high
- **Kind**: bug
- **Where**: `server/charm/src/charm.py` (leader/non-leader asymmetry in `_on_config_changed`, `_update_layer_and_restart`)
- **Evidence**: After `juju scale-application testflinger-k8s 2` (rev 355): unit 0
  stays WAITING ("Waiting for Pebble in workload container", pebble-ready crash
  masked); unit 1 goes to ERROR via config-changed (visible). `juju status`
  shows app-level `error` driven by unit 1 while unit 0 is silently broken.
  `juju resolve` on unit 1 clears the state temporarily; the next config-changed
  re-crashes immediately. Root cause: the leader's `_on_config_changed` has a
  `can_connect()` guard on its key-rotation path that returns early; non-leader
  units and no-key-change paths call `_update_layer_and_restart()`
  unconditionally, which crashes via `_pebble_layer` → `sys.exit()`.
- **Why it matters**: On a scaled deployment for HA, an operator may see one
  unit "waiting" (looks healthier) and one "error" without realising both are
  non-functional; monitoring on ERROR alone misses unit 0.
- **Fix**: Replace all `sys.exit()` with status + return so every unit
  consistently reaches BlockedStatus/ErrorStatus regardless of leadership; add
  the `can_connect()` guard before `_update_layer_and_restart()` unconditionally.
- **Linter rule**: "Multi-unit charms must not rely on hook-type differences to
  determine visible status" — not mechanically checkable.

### HIGH: `on_update_testflinger_action` crashes with uncaught `FileNotFoundError`
- **Severity**: high
- **Kind**: bug
- **Where**: `agent/charms/testflinger-agent-host-charm/src/charm.py:305` (`on_update_testflinger_action`), `charm.py:91–105` (`update_testflinger_repo`)
- **Evidence**: `update_testflinger_repo` calls
  `testflinger_source.create_virtualenv()`, which runs `python3 -m virtualenv`
  via `run_with_logged_errors` — that helper logs and returns an exit code but
  does not raise. When the venv is never created (observed on LXD: no
  `virtualenv` module in system Python), the subsequent `clone_repo()` call to
  `uv pip install --python {VIRTUAL_ENV_PATH}/bin/python3` raises
  `FileNotFoundError`, which propagates out of the action handler uncaught.
  Observed live:
  ```
  Uncaught FileNotFoundError in charm code: [Errno 2] No such file or directory:
    '/srv/testflinger-venv/bin/pip3'
  ```
  This happened after `on_install` failed to create the venv (apt error was
  caught, but the `create_virtualenv()` failure was not), and
  `on_config_changed` did not re-create it.
- **Why it matters**: An operator trying to fix a failed install via
  `update-testflinger` gets a cryptic crash instead of an actionable error.
- **Fix**: Wrap `create_virtualenv()`/`clone_repo()` in try/except and handle
  `FileNotFoundError` explicitly, or verify the venv exists before using it.
- **Linter rule**: "Action handlers that call methods that can raise
  FileNotFoundError must handle it explicitly" — not mechanically checkable.

### MEDIUM: Key rotation race condition on concurrent config changes
- **Severity**: medium
- **Kind**: bug
- **Where**: `server/charm/src/charm.py:308–341`
- **Evidence**:
  ```python
  def _on_config_changed(self, _: ops.framework.EventBase) -> None:
      new_key = self.typed_config.testflinger_secrets_master_key
      stored_key = self._stored.previous_master_key
      if stored_key and new_key != stored_key and self.unit.is_leader():
          self._run_rotation(env)
      self._stored.previous_master_key = new_key  # stored immediately
  ```
  If a second config change fires while a rotation is in flight, the stored
  key is overwritten before the rotation completes; a subsequent rotation will
  see `stored_key == new_key` and skip silently.
- **Why it matters**: A key rotation can be lost silently — the unit goes
  Active with no warning, and future rotations are also skipped.
- **Fix**: Use a separate stored field for "rotation-in-progress old key" so a
  config change during an active rotation is deferred rather than overwriting
  state.
- **Linter rule**: "State transitions that involve async operations must not
  overwrite intermediate state in StoredState before the async op completes" —
  not mechanically checkable.

### MEDIUM: `write_supervisor_service_files` uses `sys.exit(1)` on missing dirs
- **Severity**: medium
- **Kind**: bug
- **Where**: `agent/charms/testflinger-agent-host-charm/src/charm.py:123–126, 134–135`
- **Evidence**:
  ```python
  if not config_dirs.is_dir():
      logger.error("config-dir must point to a directory")
      self._block("config-dir must point to a directory")
      sys.exit(1)
  ```
  Same `sys.exit()` pattern in the install and config-changed hot paths. Not
  triggered in the observed LXD run because `update_config_files` failed
  first, but reachable if the config-dir check is reached with a
  misconfigured path.
- **Fix**: Return from the handler after `_block()` instead of `sys.exit(1)`.
- **Linter rule**: "Hook handlers must not call `sys.exit()` or `os._exit()`" —
  mechanically checkable with ruff S307.

### MEDIUM: `write_file` is not truly atomic on non-existent parent dir
- **Severity**: medium
- **Kind**: bug
- **Where**: `agent/charms/testflinger-agent-host-charm/src/common.py:28–37`
- **Evidence**:
  ```python
  with tempfile.NamedTemporaryFile("w", dir=location.parent, ...) as tmp:
      tmp.write(contents)
      tmp_path = Path(tmp.name)
  os.replace(tmp_path, location)  # atomic rename
  ```
  If `location.parent` doesn't exist, `NamedTemporaryFile` raises
  `FileNotFoundError` before any file is created, before the `try`/`OSError`
  handler is entered. No test covers this path (coverage confirms lines 28–37
  missing).
- **Why it matters**: Setting SSH keys via config on a fresh machine with no
  SSH config directory would crash with an uncaught exception, leaving the
  unit in Error.
- **Fix**: `location.parent.mkdir(parents=True, exist_ok=True)` before the
  `NamedTemporaryFile` call.
- **Linter rule**: "NamedTemporaryFile with `dir=` must guard against missing
  parent directory" — mechanically checkable with ruff S202.

### MEDIUM: `on_config_changed` non-leader path crashes when relation data is incomplete
- **Severity**: medium
- **Kind**: bug
- **Where**: `server/charm/src/charm.py:293` (`_on_config_changed`)
- **Evidence**: The `can_connect()` guard only protects the leader's
  key-rotation path; non-leader units and no-key-change paths call
  `_update_layer_and_restart()` unconditionally, which reaches
  `_pebble_layer.to_dict()` → `fetch_mongodb_relation_data()` → `sys.exit()`.
  Masked in practice by Juju's pebble polling subsystem (see the scaling
  finding above).
- **Why it matters**: On a multi-unit deployment, non-leader config-changed
  crashes every time it fires, contributing to inconsistent visible status.
- **Fix**: Add the same `can_connect()` guard before
  `_update_layer_and_restart()` unconditionally, or replace `sys.exit()` calls
  with proper status + return.
- **Linter rule**: Not mechanically checkable.

### MEDIUM: No `update_status` handler in k8s charm — no self-heal path
- **Severity**: medium
- **Kind**: bug
- **Where**: `server/charm/src/charm.py` (absent)
- **Evidence**: No `on_update_status` or `on_upgrade_charm` handler exists.
  When the unit is stuck in the pebble-ready retry loop, no periodic hook
  attempts recovery. Confirmed by debug-log: `update-status` fires every ~5
  min and completes with exit 0 (default empty handler) — no recovery
  attempted. The only recovery paths are `juju resolve` or `juju refresh`,
  neither automatic.
- **Why it matters**: If MongoDB relation data later becomes complete, the
  unit never notices and stays stuck in the retry loop indefinitely.
- **Fix**: Add an `update_status` handler that re-fires the layer update when
  the container can connect:
  ```python
  def _on_update_status(self, _):
      if self.container.can_connect():
          self._update_layer_and_restart()
  ```
- **Linter rule**: "Charms that use Pebble should have an update_status handler
  to attempt recovery when the workload is not Active" — not mechanically
  checkable.

### MEDIUM: Config integer options lack range constraints
- **Severity**: medium
- **Kind**: bug
- **Where**: `server/charm/src/config.py`
- **Evidence**: `keepalive`, `max_pool_size`, `jwt_leeway` are typed `int` with
  no `gt=0` constraint; `juju config keepalive=-5` passes pydantic validation
  and the charm proceeds to `MaintenanceStatus("Assembling pod spec")`. The
  invalid value reaches the MongoDB driver, which accepts or rejects it
  silently.
- **Why it matters**: Invalid config passes charm validation but fails only at
  the application level, with no BlockedStatus.
- **Fix**:
  ```python
  keepalive: int = pydantic.Field(default=10, gt=0)
  max_pool_size: int = pydantic.Field(default=100, gt=0)
  jwt_leeway: int = pydantic.Field(default=5, ge=0)
  ```
- **Linter rule**: "Integer config options with semantic lower bounds should
  have pydantic `gt=`/`ge=` constraints" — not mechanically checkable.

### MEDIUM: Machine charm `sys.exit(1)` in hot path after config validation passes
- **Severity**: medium
- **Kind**: bug
- **Where**: `agent/charms/testflinger-agent-host-charm/src/charm.py:123–126, 134–135`
- **Evidence**: `write_supervisor_service_files()` calls `sys.exit(1)` after
  `_block()` in two places, reachable from `on_config_changed`. Not hit in the
  observed LXD run because `update_config_files` failed first (git clone
  failure) — but if the git repo is reachable, a misconfigured `config-dir`
  would kill the unit agent.
- **Why it matters**: `_block()` sets status before the crash, but the unit
  agent process still dies and restarts.
- **Fix**: Remove the `sys.exit(1)` calls; return after `_block()`.
- **Linter rule**: "Hook handlers must not call `sys.exit()` or `os._exit()`" —
  mechanically checkable with ruff S307.

### MEDIUM: Machine charm `on_upgrade_charm` has no error handling
- **Severity**: medium
- **Kind**: bug
- **Where**: `agent/charms/testflinger-agent-host-charm/src/charm.py:183–189`
- **Evidence**:
  ```python
  def on_upgrade_charm(self, _):
      self.install_dependencies()
      self.update_tf_cmd_scripts()
      self.update_testflinger_repo()  # can raise; no try/except
      self.unit.status = ops.ActiveStatus()
  ```
  `update_testflinger_repo` can raise `FileNotFoundError` (via
  `create_virtualenv`/`clone_repo`); `install_dependencies` can raise apt
  errors. Neither is caught here, unlike `on_install`, which handles apt
  errors gracefully.
- **Why it matters**: A `juju refresh` that fails the git clone or apt install
  leaves the charm in Error with no recovery path except another refresh.
- **Fix**: Wrap `install_dependencies` and `update_testflinger_repo` in
  try/except with `_block()` on failure.
- **Linter rule**: "`on_upgrade_charm` handlers must handle exceptions from
  long-running operations" — not mechanically checkable.

### MEDIUM: Machine charm `on_install` has unhandled failure modes
- **Severity**: medium
- **Kind**: bug
- **Where**: `agent/charms/testflinger-agent-host-charm/src/charm.py:77–84`
- **Evidence**: `on_install` runs five steps: (1) `install_dependencies()` —
  apt errors caught, but the `pipx install uv` sub-step relies on
  `run_with_logged_errors`, which logs and returns an exit code without
  raising; (2) `setup_docker()` — `charmlibs.passwd` group/user operations
  with no try/except; (3) `update_tf_cmd_scripts()` — `write_file` with no
  try/except; (4) `update_testflinger_repo()` — no try/except, can raise
  `FileNotFoundError`; (5) `update_config_files()` — wrapped in try/except for
  `RuntimeError`/`OSError`. Only step 5 is protected.
- **Why it matters**: Failures in steps 1–4 leave the unit in Error status
  rather than BlockedStatus, with no actionable message.
- **Fix**: Wrap steps 1–4 in try/except using `_block()` for recoverable
  failures.
- **Linter rule**: "Hook handlers must not call methods that can raise without
  try/except" — not mechanically checkable.

### MEDIUM: Machine charm `update_testflinger_repo` has no error handling
- **Severity**: medium
- **Kind**: bug
- **Where**: `agent/charms/testflinger-agent-host-charm/src/charm.py:91–105`
- **Evidence**: `create_virtualenv()` logs on failure but doesn't raise; the
  subsequent `clone_repo()` uses `uv pip install --python
  {VIRTUAL_ENV_PATH}/bin/python3`, which raises `FileNotFoundError` if the venv
  was never created (observed on LXD). This is called from both `on_install`
  and `on_upgrade_charm`, and separately from the `update-testflinger` action.
- **Why it matters**: The install-time failure is silent (logged only); the
  same underlying gap later crashes the `update-testflinger` action (see HIGH
  finding above).
- **Fix**: Check the venv exists before pip install; handle
  `FileNotFoundError` gracefully with `_block()`.
- **Linter rule**: "Methods that can raise FileNotFoundError must handle it" —
  not mechanically checkable.

### MEDIUM: Machine charm default `config-dir` is empty — charm blocks immediately on start
- **Severity**: medium
- **Kind**: ux
- **Where**: `agent/charms/testflinger-agent-host-charm/src/charm.py:134`, `charmcraft.yaml`
- **Evidence**: `config-dir` defaults to `""`; a pydantic validator requires
  both `config_repo` and `config_dir` to be non-empty. `config-repo` defaults
  to `https://github.com/canonical/testflinger-agent-configs.git`, which is
  not a valid public config repo, so the charm blocks on a clean deploy
  regardless — but even with a valid `config-repo`, the operator must also set
  `config-dir`, and there is no sensible default or explicit guidance in the
  BlockedStatus message about which option is missing.
- **Why it matters**: Out-of-the-box deploy fails without explicit config, and
  the error message doesn't name the missing option.
- **Fix**: Provide a meaningful default for `config-dir`, or make the
  BlockedStatus message explicitly name the missing config option(s).
- **Linter rule**: Not mechanically checkable.

### MEDIUM: Pyright type errors in k8s charm
- **Severity**: medium
- **Kind**: lint
- **Where**: `server/charm/src/charm.py:242, 428`
- **Evidence**:
  1. Line 242 (`_update_layer_and_restart`):
     ```python
     services = self.container.get_plan().to_dict().get("services", {})
     if services != new_layer["services"]:
     ```
     pyright: `"services" is not a required key in "LayerDict", so access may
     result in runtime exception`.
  2. Line 428 (`_pebble_layer`):
     ```python
     return Layer(pebble_layer)  # pebble_layer is dict[str, Unknown]
     ```
     pyright: `Argument of type "dict[str, Unknown]" cannot be assigned to
     parameter "raw" of type "str | LayerDict | None"`.
- **Why it matters**: Fragile typing around exactly the code path that
  contains the critical bug; if `LayerDict` changes shape, runtime behaviour
  may silently diverge from what type checking assumes.
- **Fix**: Add explicit casts or type the `pebble_layer` dict as `LayerDict`.
- **Linter rule**: "TypedDict access on optional keys should use `.get()` with
  type annotation" — mechanically checkable with strict pyright mode.

### MEDIUM: Machine charm uses module-level `logger` instead of `self.logger`
- **Severity**: medium
- **Kind**: lint
- **Where**: `agent/charms/testflinger-agent-host-charm/src/charm.py:90`
- **Evidence**: pyright: `Cannot access attribute "logger" for class
  "TestflingerAgentHostCharm"`. `self.logger` resolves to the module-level
  `logger` variable in practice, but pyright flags it as an unknown attribute.
- **Fix**: Rename the module-level `logger` to `_logger`/`LOGGER` to avoid
  shadowing the conventional `self.logger`.
- **Linter rule**: "Charm classes should use `self.logger` (provided by
  ops.CharmBase) rather than a module-level `logger` variable" — mechanically
  checkable with pyright.

### MEDIUM: No unit test for partial relation data (root-cause gap)
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `server/charm/tests/unit/test_charm.py`
- **Evidence**: `test_exit_on_empty_relation_data` uses `remote_app_data={}`;
  `test_missing_mongodb_relation` uses no relation at all. Neither covers the
  actual deployed failure: `{"database": "testflinger_db"}` present but
  `endpoints` absent. The `if not val: continue` guard skips truly-empty dicts
  but not this partial case, so it falls through to the crash.
- **Why it matters**: This is the exact scenario hit in production with
  mongodb-k8s rev 117. A scenario test with this relation data would have
  caught all three critical k8s findings.
- **Fix**: Add a scenario test with
  `remote_app_data={"database": "testflinger_db"}` (no `endpoints`).
- **Linter rule**: Not mechanically checkable.

### MEDIUM: Machine charm `on_secret_changed` not exercised by unit tests
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `agent/charms/testflinger-agent-host-charm/tests/unit/test_charm.py`
- **Evidence**: `_on_secret_changed` is registered but no scenario test fires
  a `SecretChangedEvent` for the credentials secret. `test_blocked_on_no_secret`
  covers `_valid_secret()` directly, not the full handler path.
- **Why it matters**: Credential rotation while running is an untested,
  potentially fragile path.
- **Fix**: Add a scenario test firing `secret_changed` with a valid secret and
  asserting `testflinger_client.authenticate` is called.
- **Linter rule**: Not mechanically checkable.

### MEDIUM: Machine charm `write_file` parent-directory-not-exists case untested
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `agent/charms/testflinger-agent-host-charm/src/common.py:28–37`
- **Evidence**: Coverage report shows lines 28–37 (the `FileNotFoundError`
  pre-try path) missing entirely.
- **Fix**: Add `mkdir(parents=True, exist_ok=True)` (see above) and a unit
  test for the missing-parent case.
- **Linter rule**: "NamedTemporaryFile with `dir=` must guard against missing
  parent directory" — mechanically checkable with ruff S202.

### MEDIUM: Machine charm `on_upgrade_charm` error-handling gaps untested
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `agent/charms/testflinger-agent-host-charm/src/charm.py:183–189`
- **Evidence**: Coverage shows lines 291–294 missing (upgrade hook without git
  failure exercised); `update_status` and `secret_changed` handlers are also
  untested.
- **Fix**: Add scenario tests for `on_upgrade_charm` failure paths alongside
  the try/except fix above.
- **Linter rule**: Not mechanically checkable.

### MEDIUM: concierge.yaml specifies Juju 3/stable but test environments run Juju 4.x
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `server/charm/concierge.yaml`, `agent/charms/testflinger-agent-host-charm/concierge.yaml`
- **Evidence**: Both specify `juju: channel: 3/stable`. The actual controllers
  used were concierge-k8s-4 (Juju 4.0.12), concierge-lxd-4 (Juju 4.0.12),
  concierge-k8s-3 (Juju 3.6.25), concierge-lxd (Juju 3.6.27).
- **Why it matters**: Tests declared against Juju 3/stable but must pass on
  Juju 4.x production controllers; compatibility gaps (secret handling, Pebble
  API changes) may not be caught by CI.
- **Fix**: Update `concierge.yaml` to `juju: channel: 4/stable` for the
  primary environment; keep a 3.x environment for regression coverage.
- **Linter rule**: Not mechanically checkable.

### MEDIUM: Integration tests require a real k8s/LXD controller — cannot run locally
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `server/charm/tests/integration/test_charm.py`, agent-host `tests/integration/`
- **Evidence**: k8s integration tests use `jubilant` and require
  `JUJU_K8S_CONTROLLER`; the agent-host tests need an LXD controller. Neither
  ran in this review environment.
- **Why it matters**: These are the only tests exercising end-to-end behaviour
  with real MongoDB and the full Pebble lifecycle; developers can't run them
  without dedicated infrastructure.
- **Fix**: Document the required environment in CONTRIBUTING.md and ensure CI
  runs them on every PR.
- **Linter rule**: Not mechanically checkable.

### LOW: Agent venv certifi path mismatch causes TLS failures (open issue #1121)
- **Severity**: low
- **Kind**: bug
- **Where**: not established (open issue, not reproduced in this review)
- **Evidence**: Open issue #1121 (2026-07-13) reports the testflinger-agent
  fails with `Could not find a suitable TLS CA certificate bundle, invalid
  path: /srv/testflinger-venv/lib/python3.10/site-packages/certifi/cacert.pem`.
  No charm-level detection or workaround exists; the agent exits, supervisord
  restarts it, and it loops.
- **Why it matters**: A deployed agent silently fails TLS connections and
  never processes jobs, with no BlockedStatus raised.
- **Fix**: Verify certifi is present in the venv at install time, or install
  it explicitly.
- **Linter rule**: Not mechanically checkable.

### LOW: `delete_refresh_token` is defined but never called
- **Severity**: low
- **Kind**: bug
- **Where**: `server/src/testflinger/database.py`, `server/src/testflinger/api/v1.py:1163`
- **Evidence**: `database.delete_refresh_token` exists and is correctly
  implemented, but the `revoke_refresh_token` endpoint only calls
  `database.edit_refresh_token(token, {"revoked": True})`. Open issue #979
  confirms this is known: refresh tokens rely on TTL expiry (90 days) instead.
- **Why it matters**: Refresh tokens remain valid for up to 90 days after
  revocation; a compromised token can still be used until TTL expires.
- **Fix**: Call `database.delete_refresh_token(token)` in
  `revoke_refresh_token`, in addition to or instead of setting `revoked=True`.
- **Linter rule**: "Functions defined but never called should be flagged" —
  mechanically checkable with ruff F841/pyright.

### LOW: Open issue #292 — anyone can cancel any job
- **Severity**: low
- **Kind**: ux
- **Where**: not established
- **Evidence**: Open issue #292 (2026-07-01) reports any user can cancel any
  job via the web UI at `/jobs`; `cancel_job` has no ownership check. Tracked
  but not fixed.
- **Why it matters**: Accidental or malicious cancellation of other users'
  jobs.
- **Fix**: Check `g.client_id` matches the job owner in `cancel_job()`.
- **Linter rule**: Not mechanically checkable.

### LOW: `update_testflinger_repo` has no error handling in `on_upgrade_charm`
- **Severity**: low
- **Kind**: bug
- **Where**: `agent/charms/testflinger-agent-host-charm/src/charm.py:188`
- **Evidence**: `on_upgrade_charm` calls `self.update_testflinger_repo()`,
  which can raise from `testflinger_source.clone_repo()`, with no
  try/except around the call (subsumed by the broader `on_upgrade_charm`
  MEDIUM finding above, noted separately as it was raised independently in
  the notes).
- **Fix**: Add try/except in `update_testflinger_repo` or in
  `on_upgrade_charm`.
- **Linter rule**: Not mechanically checkable.

### LOW: Duplicate docstring in `vault.py`
- **Severity**: low
- **Kind**: lint
- **Where**: `server/src/testflinger/secrets/vault.py:72`
- **Evidence**: The `write()` method docstring has `:returns:` twice.
- **Fix**: Remove the duplicate `:returns:` line.
- **Linter rule**: Not mechanically checkable.

### NIT: `ops` framework version pinned to >=3.5.0 on agent-host
- **Severity**: not established
- **Kind**: lint
- **Where**: `agent/charms/testflinger-agent-host-charm/pyproject.toml`
- **Evidence**: `"ops >= 3.5.0"` while the server charm uses `"ops >= 2.2.0"`.
- **Fix**: Align both charms to `"ops >= 3.5.0"` to match the minimum Juju
  version actually supported.
- **Linter rule**: Not mechanically checkable.

### NIT: Pytest collection warning on config classes
- **Severity**: not established
- **Kind**: lint
- **Where**: `server/charm/src/config.py:14`, `agent/charms/testflinger-agent-host-charm/src/config.py:16`
- **Evidence**: `TestflingerServerConfig` and `TestflingerAgentConfig`
  (pydantic `BaseModel`s) are collected by pytest as test classes because
  their names start with `Test`; `__test__ = False` prevents this for the
  charm class but not for the config classes.
- **Fix**: Rename the config classes (e.g. `TestflingerServerConfigModel`) or
  add `__test__ = False`.
- **Linter rule**: Not mechanically checkable.

### NIT: `occured` typo in machine charm error message
- **Severity**: low
- **Kind**: lint
- **Where**: `agent/charms/testflinger-agent-host-charm/src/charm.py:90`
- **Evidence**: `self.logger.error("An error occured while installing
  dependencies")` — found by `codespell`.
- **Fix**: `occured` → `occurred`.
- **Linter rule**: Mechanically checkable with `codespell`.

## Worth copying

- **Pydantic config validation via `load_config(..., errors="blocked")`**
  (`server/charm/src/config.py`, agent-host `src/config.py`): sets
  `BlockedStatus` with a descriptive message automatically on validation
  failure. Canonical pattern, worth documenting more widely.
- **StoredState for rotation-in-progress tracking** (`server/charm/src/charm.py`):
  sound pattern; only the race condition above undermines it.
- **Supervisor config discovery for COS metrics**
  (`agent/charms/testflinger-agent-host-charm/src/supervisord.py`): parses
  existing supervisord configs to discover ports and reuses them on
  regeneration, avoiding port churn.
- **Scenario-style unit tests with `ops.testing.Context`**: both charms use
  `Context`/`State` rather than `harness`; `tests/unit/conftest.py` fixtures
  are clean and composable.
- **Split secrets store (Vault + MongoDB CSFLE)**
  (`server/src/testflinger/secrets/__init__.py`): tries Vault first, falls
  back to MongoDB CSFLE — good multi-backend pattern.

## Common-practice notes

**Follows convention**: correct ops idioms (observed handlers, status
precedence); `charmcraft.yaml` layout matches ecosystem norms; `lib/charms/
<name>/v<N>/` versioning; `src/` layout with separated config/utilities; ruff
config with `per-file-ignores` for tests; uv for dependency management.

**Leads the pack**: pydantic config validation with `errors="blocked"` (most
charms still use `voluptuous` or raw config access); CSFLE key rotation via
`retry-key-rotation` is a sophisticated feature; OIDC Device Authentication
Flow support is more complete than most charms; agent-host uses
`charmlibs-apt`/`charmlibs-passwd` (the newer preferred approach over
`operator-libs-linux`); server has 93%+ test coverage with comprehensive
integration tests.

**Drifts from convention**: `sys.exit()` in hook handlers is non-standard;
most charms use deferral or stored state instead. The k8s charm provides both
`nginx-route` and `ingress` interfaces with a documented conflict — unusual.
No terraform module for the k8s charm (agent-host has one).

## Tests

### Unit tests
| Suite | Tests | Status | Coverage | Notes |
|---|---|---|---|---|
| server/charm unit (`tox -e unit`) | 33 | pass (1.1–1.3s) | 84% | `sys.exit` paths tested for crash, not correct behaviour |
| agent-host unit (`tox -e unit`) | 60 | pass (0.5–0.6s) | 59% | apt failure, secret change, git failure untested |
| server Flask app | 564 | pass (~3.5min) | 94% | v1 API, auth, database, secrets, OIDC, views |
| server/charm integration | N/A | not run | — | requires k8s controller + MongoDB |
| agent-host integration | N/A | not run | — | requires LXD controller |

Pytest collection warnings for `TestflingerServerConfig`/`TestflingerAgentConfig`
remain unresolved (see NIT above).

### Coverage detail (live `tox -e unit`)
- `server/charm/charm.py`: 231 statements, 31 missing → 84%. Missing: lines
  180, 212–213, 219–222, 226, 242–253, 270, 275–274, 286–291, 310–313, 355–356,
  477–478, 500–501, 505–506, 511–512, 540–542, 547–558, 571. Untested: the
  `sys.exit()` correctness paths, partial relation data, key-rotation
  ExecError, `connect_to_mongodb()` failure.
- `agent-host/charm.py`: 182 statements, 75 missing → 59%. Missing: install
  path, apt install, Docker setup, `sys.exit(1)` in
  `write_supervisor_service_files`, `on_upgrade_charm` without git failure,
  `on_secret_changed`, `on_update_status`, `on_update_testflinger_action` with
  non-existent venv, `write_file` parent-dir-not-exists.
- `agent-host/common.py`: 40 statements, 4 missing → 86%. Missing: lines
  28–37 (the `write_file` parent-directory-not-exists case).
- `agent-host/supervisord.py`: 88 statements, 18 missing → 82%.
- Server Flask app: 2015 statements, 128 missing → 94%. Untested: attachment
  endpoints with invalid UUIDs, job state transitions, OIDC callback edge
  cases, vault connection retry paths.

### Static analysis
- `ruff check`: clean on both charms.
- `codespell`: one hit — `occured` → `occurred` in agent-host `charm.py:90`.
- `pyright` (server/charm): 9 errors — mostly import-resolution/TypedDict
  noise; 2 genuine type-safety issues (`charm.py:242` services key access,
  `charm.py:428` Layer constructor argument).
- `pyright` (agent-host): 3 errors — `charmlibs.apt` import unresolved
  (pyright limitation), `self.logger` attribute access issue.

### Missing test coverage relative to findings
- `fetch_mongodb_relation_data` with `endpoints=None` — root cause of all
  three critical k8s findings; no test covers this; existing tests use `{}`
  which takes a different code path.
- `_on_testflinger_pebble_ready` with incomplete-but-present relation data —
  untested crash path.
- `retry-key-rotation` when container cannot connect / relation data
  incomplete — untested; would crash the unit agent.
- `write_supervisor_service_files` with missing `config_dirs` — `_block()` is
  tested, the subsequent `sys.exit(1)` is not.
- `write_file` with non-existent parent directory — untested.
- `on_upgrade_charm` with git clone failure — untested.
- `on_secret_changed` — registered handler, no scenario test.
- `on_update_status` — machine charm has one, untested; k8s charm has none at
  all.
- `on_update_testflinger_action` with non-existent venv — the actual observed
  production failure, uncovered.
- Machine charm `on_install` with apt failure — only the success path is
  tested.

## Docs

- `server/charm/README.md` (1624 bytes): thin — overview only, assumes
  familiarity with Testflinger. Links to
  `canonical-testflinger.readthedocs-hosted.com`, which is comprehensive; the
  charm-specific README is not.
- `server/charm/CONTRIBUTING.md` (1950 bytes): covers setup/testing but
  doesn't mention `concierge.yaml`, the tox workflow, or how to run
  integration tests locally.
- Charmhub descriptions for both charms match their listings and are
  accurate.
- Open issue #961 (confirmed): the authorization-error message links to a
  stale docs URL that no longer exists.

## Deployment log

### Environment issue: mongodb-k8s RBAC
mongodb-k8s (channel 6/stable, rev 117) requires the Juju Kubernetes secret
backend to store credentials. `juju-secret-consumer-*` service accounts
lacked RBAC (`create,patch` on `secrets` in namespace `rv-tf-k8s`). Fixed
manually with a Role + RoleBindings. MongoDB then started but stayed blocked
on "Waiting for replica set initialisation" — an mongodb-k8s issue, not
testflinger's.

### testflinger-k8s lifecycle, rev 354 (edge, initial deploy)
1. install → config-changed (no relation data yet) → start → pebble-ready.
2. mongodb relation joined/changed: data has only `{"database":
   "testflinger_db"}`, no `endpoints`/`username`/`password`/`uris`.
3. pebble-ready → `_pebble_layer` → `app_environment` →
   `fetch_mongodb_relation_data()` → `sys.exit()` — hook exits 1.
4. config-changed fires → same crash → unit → **ERROR**.
5. `juju resolve` clears the error temporarily; next hook re-crashes; unit
   stays in ERROR.

```
File "charm.py", line 473, in fetch_mongodb_relation_data
  if ":" in val.get("endpoints"):
TypeError: argument of type 'NoneType' is not iterable
hook "config-changed" failed: exit status 1
```

### testflinger-k8s lifecycle after `juju refresh --channel latest/stable`, rev 355
1. upgrade-charm → config-changed → start: all succeed (config-changed no
   longer crashes, due to the leader `can_connect()` guard).
2. pebble-ready → same `_pebble_layer` crash → hook exits 1.
3. Unit → **WAITING: "Waiting for Pebble in workload container"**.
4. pebble-ready re-fires every ~5s, crashing every time.
5. Unit never reaches Active or Error — silently stuck.

### Charm revisions on charmhub
- edge: 354 (2026-07-23) — config-changed crashes → ERROR.
- stable: 355 (2026-07-23) — pebble-ready still crashes → WAITING (silent).
- beta: 365 (2026-08-17) — pebble-ready still crashes → WAITING (silent).
  Confirmed by refreshing the deployed charm to beta and observing the same
  traceback. Beta was published after the local HEAD commit date
  (2026-07-23), meaning it was built from a newer commit than the reviewed
  branch, but still carries the bug.

### Integrations tested
- **mongodb-k8s** (rev 117): incomplete relation data; database and keyvault
  relations established; MongoDB itself stuck on replica-set init.
- **grafana-agent-k8s** (rev 243, edge): relations to metrics-endpoint and
  grafana-dashboard created; grafana-agent-k8s BlockedStatus ("Missing
  ['grafana-cloud-config']") is expected without a Grafana cloud. testflinger
  correctly emits Prometheus scrape config (`*:9090`) and dashboard metadata —
  COS wiring is correct.
- **traefik-k8s** (rev 377, stable): relation created; `ingress-relation-created`
  fired successfully (doesn't call `_pebble_layer`, so it succeeds even though
  pebble-ready is crashing). traefik-k8s itself went BlockedStatus
  ("Traefik load balancer is unable to obtain an IP or hostname") — an
  environment limitation, not a testflinger bug.
- **grafana-agent** (machine charm, concierge-lxd): relation created but the
  charm is blocked on config, so COS integration wasn't exercised.
  `COSAgentProvider` refresh_events include `config_changed` — correct
  pattern.

### Actions tested
- `set-admin-password`: fails gracefully ("Unable to connect to MongoDB") —
  expected since MongoDB isn't running. Does not crash the unit agent.
- `retry-key-rotation`: fails gracefully ("testflinger_secrets_master_key is
  not configured") when no key set. With a key configured and incomplete
  MongoDB data, it calls `app_environment` → `sys.exit()` and kills the unit
  agent (see CRITICAL finding above).

### Failure injection
- `juju config keepalive=-5`: triggers config-changed → same TypeError crash
  in rev 354 (unit → ERROR); in rev 355 the pebble-ready crash dominates.
- `juju resolve testflinger-k8s/0`: clears error state temporarily in rev
  354; next hook re-crashes immediately. No effect on the waiting unit in rev
  355.
- Scaling to 2 units (`juju scale-application testflinger-k8s 2`): unit 1 →
  ERROR (config-changed, visible); unit 0 → WAITING (pebble-ready, invisible).
  App-level status `error` driven by unit 1 only. `juju resolve` on unit 1
  doesn't fix it — next config-changed re-crashes.
- Removing mongodb relation
  (`juju remove-relation testflinger-k8s:mongodb_client mongodb-k8s:database`):
  unit → `WAITING: "Waiting for database relation"` (set before `sys.exit()`).
  `relation-removed` fired on mongodb-k8s at 05:15:16, but pebble-ready fired
  at 05:15:06 — before the removal completed — so pebble-ready still saw
  incomplete relation data and crashed first.
- `kubectl exec` into workload container: `pebble services` → `Plan has no
  services.`; `pebble plan` → `{}` — confirms no service has ever been
  defined.
- Killing the workload process: N/A — no workload process exists (empty
  Pebble plan).
- traefik-k8s `config-changed` also failed after scaling ("hook failed:
  config-changed"); resolved with `juju resolve`. Root cause: traefik could
  not create its LoadBalancer service in this environment — not a
  testflinger issue.

### Machine charm lifecycle (concierge-lxd, Juju 3.6.27, rev 124)
- Machine provisioned on LXD (Ubuntu 22.04), reached `started` in ~3 min.
- `install` hook completed successfully: Docker installed, testflinger-agent
  source cloned, SSH keys copied.
- `config-changed` fired after `config-repo`/`config-dir` set; git clone of
  `github.com/canonical/testflinger-agent-configs.git` failed with exit code
  128 (repo does not exist or is private):
  `Cmd('git') failed due to: exit code(128)`, `fatal: could not read Username
  for 'https://github.com': No such device or address`.
- Charm → **BlockedStatus: "Failed to update or config files"** — graceful,
  no crash.
- `write_supervisor_service_files`'s `sys.exit(1)` path was not triggered in
  this run because `update_config_files` failed first.
- No `sys.exit()` in the install path (unlike the k8s charm's pebble-ready).
  The install hook completes even when the git clone fails.
- `juju run testflinger-agent-host/0 update-configs`: completed rc=0, status
  stayed Blocked (`update_config_files()` failed gracefully internally).
- `juju run testflinger-agent-host/0 update-testflinger branch=main`:
  **action failed** with uncaught `FileNotFoundError` (see HIGH finding
  above): `/srv/testflinger-venv/bin/pip3` did not exist because
  `create_virtualenv()` had silently failed during `on_install`, and
  `on_config_changed` never re-created it.
- Unit → **BlockedStatus: "Invalid credentials secret"** (from `on_start`,
  via `_update_refresh_token` → `_valid_secret()` returning `None` with no
  secret configured).
- Invalid `testflinger-server` config (no protocol prefix): pydantic
  validator correctly catches it →
  `BlockedStatus: "Invalid config: ... testflinger_server must include
  protocol"`.
- `credentials-secret` config uses Juju secrets correctly.
- `COSAgentProvider` refresh_events = `[config_changed, upgrade_charm]` —
  correct pattern.

### Machine charm lifecycle (concierge-lxd-4, Juju 4.0.12)
- Machine took ~3 min pending → started, same as concierge-lxd.
- Identical behaviour to Juju 3.6: git clone fails → BlockedStatus "Failed to
  update or config files". No Juju-version-specific issues observed.

## Observed behaviour

- Pebble in the k8s workload container is reachable
  (`/charm/bin/pebble services` responds), but the plan stays empty (`{}`) —
  the testflinger service is never added because `container.add_layer()` is
  never reached.
- `sys.exit()` in pebble-ready kills the unit agent; Juju restarts it;
  pebble-ready re-fires; same crash — an infinite retry loop with no operator
  alert.
- Hook ordering determines which crash is visible: in rev 354, config-changed
  fires first and crashes → ERROR; in rev 355/365, the leader's config-changed
  succeeds (guarded), pebble-ready crashes silently → WAITING; non-leader
  units still crash via `_update_layer_and_restart()`.
- `update-status` fires every ~5 min with no handler registered — Juju runs
  the empty default, exits 0, no recovery attempted. Debug-log:
  `unit-testflinger-k8s-0: INFO juju.worker.uniter.operation ran
  "update-status" hook (via hook dispatching script: dispatch)`.
- The k8s charm has no `update_status` handler, no `on_upgrade_charm` handler,
  and no `on_start` handler — no self-heal path exists if the unit gets stuck.

### Timing
- Pod startup: ~60s container init + ~90s image pull ≈ 2.5 min.
- Hook sequence (upgrade-charm → config-changed → start → pebble-ready): ~10s.
- pebble-ready retry interval: ~5s.
- `update-status` fires every ~5 min, exits 0 (no handler).
- Machine provisioning (both LXD environments): ~3 min pending → started.

## Open questions

1. **Why does pebble-ready crash not put the unit in ERROR in rev 355?**
   Answered: Juju's pebble polling doesn't escalate pebble-ready failures to
   ERROR the way it does for config-changed. Which hook fires last (and
   whether the leader's `can_connect()` guard applies) determines the visible
   status; confirmed via the 2-unit scaling test.
2. **Why doesn't mongodb-k8s rev 117 provide `endpoints`/`username`/`password`?**
   Answered: mongodb-k8s uses the Juju secrets backend for credentials
   (confirmed by reading `data_platform_libs/v0/data_interfaces.py`); the
   testflinger charm reads only the relation data bag, creating the mismatch.
3. **What changed between rev 354 and 355?** Partially answered — cannot
   verify without a diff of the built charm. The bug moved from config-changed
   (leader now guarded by `can_connect()`) to pebble-ready (still crashes),
   suggesting an incomplete fix. Non-leader config-changed still crashes.
4. **Is beta rev 365 fixed?** Answered: no. Refreshing to beta reproduces the
   identical traceback at the same crash site.
5. **Key rotation recovery**: if a rotation fails and the charm goes
   BlockedStatus, does `retry-key-rotation` correctly read the old key from
   `_stored.previous_master_key`? Unit tests mock `_run_rotation` and don't
   exercise the full recovery path end-to-end — not established.
6. **Ingress conflict behaviour**: the charm sets BlockedStatus when both
   nginx-route and ingress relations are active; `ingress-relation-created`
   succeeded in the deployed environment. Whether BlockedStatus clears
   correctly once the conflict is resolved was not tested (no nginx-route
   relation was established) — not established.
7. **Machine charm self-healing on LXD**: `on_config_changed` will re-fire if
   the operator sets a valid `config-repo` (Juju's normal behaviour);
   `update_config_files` is guarded by try/except, so a subsequent failure
   would be caught. But `write_supervisor_service_files`'s `sys.exit(1)` path,
   if reached, still kills the unit agent.
8. **Why does the rev 355 leader's config-changed succeed while non-leader
   crashes?** The leader's key-rotation path returns early on
   `can_connect()`; non-leader units (no key rotation) go straight to
   `_update_layer_and_restart()`, which crashes — a leader/non-leader
   asymmetry.
9. **Will `juju resolve` on the non-leader unit fix the crash?** No — it only
   clears the error state; the next config-changed or pebble-ready re-crashes.
   The only real fix is removing `sys.exit()` from `_pebble_layer`'s
   dependency chain.
</content>
