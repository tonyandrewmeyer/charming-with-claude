# sysbench

A machine charm that runs sysbench OLTP-style (TPC-C) load generation against MySQL or
PostgreSQL, exposing throughput/latency metrics on port 8088 for Prometheus scraping via
`cos-agent`. Workload is managed as a `systemd` service; the charm supports only LXD machine
substrate.

| | |
|---|---|
| Repo | canonical/sysbench-operator @ `8747b17` (2026-07-21) |
| Charms | sysbench |
| Substrate | machine (LXD) |
| Deployed | yes — concierge-lxd (Juju 3.6.27): sysbench edge rev 311 + postgresql 14/edge + mysql 8.0/edge; also deployed successfully on Juju 4.0.12 (LXD, no DB relation tested) |
| Reviewed | 2026-08-20 |

**Verdict**: functionally usable against PostgreSQL for the happy path, but not production-ready.
Two critical, confirmed bugs make it dangerous to operate: (1) on single-unit deployments — the
default — a crash during `prepare` (SIGSEGV, SIGKILL, bad config) is silently reported as
`active` instead of `blocked`, because `SysbenchStatus.check()` bypasses its own error check
when `planned_units() <= 1`; (2) MySQL `prepare` deadlocks indefinitely (confirmed >33 minutes,
never completes) because `_exec()` uses `subprocess.check_output()` against a Lua script whose
output exceeds the 64KB pipe buffer, hanging the unit agent entirely. The database password is
also visible in `ps aux` and `juju debug-log`. A maintainer should fix the `planned_units()`
bypass and the MySQL deadlock first — both are confirmed, reproducible, and destroy the basic
promise of the charm (visible status, working MySQL support) — then close the password leak
and add negative-value config validation.

## What it does

Connects to a related MySQL or PostgreSQL database and runs the TPC-C benchmark via `sysbench`
Lua scripts. The workload runs as a systemd service (`sysbench.service`) managed by the charm.
The `sysbench_svc.py` wrapper starts a Prometheus HTTP server on port 8088 to expose TPS, QPS,
and 95th-percentile latency metrics. The charm provides `cos-agent` so Grafana Agent can scrape
those metrics, and requires `mysql` or `postgresql`.

Lifecycle: `prepare` (create TPC-C tables/data) → `run` (start systemd service) → `stop` →
`clean` (drop tables). A peer relation (`benchmark-peer`) coordinates status across units.

## Deployment log

### Model: rv-sysbench-lxd (Juju 3.6.27)

1. Created model `rv-sysbench-lxd` on `concierge-lxd` (Juju 3.6.27).
2. Deployed `sysbench` from charmhub edge (rev 311) and `postgresql` from 14/edge (rev 1199).
3. Related sysbench→postgresql: sysbench went "Waiting on data from relation" (correct).
4. postgresql reached active; sysbench followed (relation data populated → CONFIGURED).
5. Install hook ran 16:14:15–16:14:42 (18 seconds).
6. First `prepare` (scale=10, threads=4): ran 16:29:52–16:30:06 (~12 minutes, LXD I/O).
7. `sysbench_prepared.target` installed and activated after prepare.
8. `run` action: service started, metrics confirmed at `http://10.5.87.38:8088/metrics`.
9. `stop` action: service stopped, status "blocked — Sysbench is stopped after run".
10. `clean` action: tables dropped, systemd files removed, status back to "active".
11. Config change `threads=5`: `config-changed` hook fired. No service restart (correct).
12. `juju config threads=-1`: accepted (no int range validation). Prepare crashed SIGSEGV.
13. Relation removal while prepare running: deferred, applied after prepare. Unit blocked (correct).
14. Re-related sysbench→postgresql. Second prepare took >10 minutes on LXD.
15. `run` after relation recreate: sysbench exit code 1 (user mismatch after relation recreate).
    Charm correctly showed "blocked — Sysbench failed, please check logs".
16. `clean` action succeeded, unit returned to "active".
17. Scaled up to 2 units (`juju add-unit sysbench`). sysbench/1 provisioned on machine 3.
18. `duration=-5` accepted by Juju (no int range validation). `run` action started; sysbench
    produced metrics with duration=-5 (sysbench treated it as 5 seconds).
19. `stop` action: service stopped, "blocked — Sysbench is stopped after run" (correct).
20. Prepared and ran with duration=-5: service ran, TPS/QPS/latency metrics confirmed.
21. `clean` action ran; `sysbench_prepared.target` confirmed inactive.

### Model: rv-sysbench-mysql (Juju 3.6.27)

22. Created model `rv-sysbench-mysql` on `concierge-lxd`.
23. Deployed `mysql` 8.0/edge rev 513 and `sysbench` edge rev 311.
24. Related sysbench:mysql → mysql:database.
25. MySQL reached active. sysbench went "active" (relation data received).
26. `prepare scale=1 threads=1` at 17:10:35 — **DEADLOCKED**. Action still running at 17:43+
    (>33 minutes, confirmed never completes). Unit agent blocked; no further actions
    dispatchable. Confirmed the `subprocess.check_output()` deadlock in `_exec()`.

### Model: rv-sysbench-j4 (Juju 4.0.12)

27. Created `rv-sysbench-j4` on `concierge-lxd-4` (Juju 4.0.12). Deployed sysbench edge
    rev 311. Machine was `pending` for >5 minutes (infrastructure); model later no longer
    visible — appears cleaned up.
28. Separate model `rv-sysbench-lxd4` on `concierge-lxd-4` (Juju 4.0.12): sysbench edge
    rev 311 deployed successfully, machine reached "started", unit correctly showed
    "blocked — No database relation available". PostgreSQL does not support Juju 4.x, so
    no DB integration was tested on this controller.

### Additional runtime tests (session 2, ~17:30–18:00)

29. `sudo kill -9 <sysbench_pid>` on the running `prepare` process. Unit log shows
    `subprocess.CalledProcessError: ... died with <Signals.SIGKILL: 9>`. Peer relation data
    recorded `status: error`, but `juju status` showed **"active"** — same
    `planned_units() <= 1` bypass as the SIGSEGV case.
30. Contrast test: `sudo kill -9` on the sysbench child process during a *run* that followed a
    successful prepare — unit correctly showed "blocked — Sysbench failed, please check logs".
    The bypass only masks errors when the service was never successfully prepared.

## Observed behaviour

- **Password in process list and debug log** (critical, confirmed): `ps aux` consistently
  shows `--db_password=REDACTED` and `--pgsql-password=REDACTED` in both
  `sysbench_svc.py` and `sysbench` child process command lines. Also appears in
  `juju debug-log` when the code logs the full `CalledProcessError`. Tracked upstream as
  issue #30.
- **Duplicate `--duration`** (confirmed): the systemd `ExecStart` template has `{{ duration }}`
  from the jinja template *and* `f"--duration={args.duration}"` appended by Python.
  `systemctl show sysbench.service` confirmed: `--duration=-5 --command=run ... --duration=-5`.
- **"active" status after SIGSEGV crash** (critical, confirmed): `threads=-1` crashed prepare
  with `CalledProcessError: Command died with <Signals.SIGSEGV: 11>`. Unit then showed
  **"active"** — the charm did not surface the failure. Root cause: the
  `planned_units() <= 1` guard in `SysbenchStatus.check()` bypasses `_has_error_happened()`.
- **"active" status after SIGKILL during prepare** (critical, confirmed): same masking
  behaviour reproduced independently of SIGSEGV — any crash during prepare on a single-unit
  deployment is invisible in `juju status`.
- **MySQL prepare deadlock** (critical, confirmed): `subprocess.check_output()` in
  `sysbench_svc.py._exec()` deadlocks when the MySQL TPCC Lua script's prepare output exceeds
  the 64KB Linux pipe buffer. Action started 17:10:35, still running at 17:43+ (>33 minutes,
  never completes). Unit agent fully blocked; no further actions dispatchable.
- **PostgreSQL and MySQL both use Juju secrets for credentials** (confirmed, corrects an
  earlier assumption in this review process): live relation data inspection showed
  `secret-user: secret://.../...` for both databases, with no plain-text `username`/`password`
  fields. The `data_interfaces` library's `_get_secret()` resolves these correctly. The
  password exposure is in the CLI arguments the charm builds afterward, not in relation data.
- **Metrics endpoint open by default**: `curl http://10.5.87.38:8088/metrics` returns
  Prometheus metrics with no authentication, even before any `cos-agent` relation exists.
- **grafana-agent incompatible with sysbench's base**: `juju integrate sysbench grafana-agent`
  fails: "subordinate must support principal application's base; subordinate only supports:
  [ubuntu@24.04/stable]" — sysbench is on ubuntu@22.04, grafana-agent 2/edge requires 24.04.
  The cos-agent integration is currently untestable end-to-end.
- **No range validation on numeric config**: `juju config threads=true` is correctly rejected
  by Juju itself (type mismatch). But `juju config threads=-1` and `juju config duration=-5`
  are both accepted — no minimum-value check anywhere in the stack.
- **ARM SIGSEGV (open issue #151)**: reported crash on Raspberry Pi 5 (exit code -11) appears
  to be the same Lua-script SIGSEGV reproduced here with `threads=-1`. The
  `planned_units() <= 1` bypass means that crash would also silently show "active" on
  single-unit ARM deployments (unverified against real ARM hardware in this review).
- **Charm cannot run on Kubernetes (open issue #36)**: `systemctl` is not available in k8s
  pods; the charm uses systemd throughout (`service_running`, `service_stop`,
  `systemctl is-active`, etc.) with no Pebble workload defined. `concierge.yaml` enables a k8s
  provider but the charm itself is machine-only.
- **Juju 4 compatibility**: sysbench itself deploys and runs cleanly on Juju 4.0.12 (LXD);
  PostgreSQL does not support Juju 4.x so end-to-end DB integration was not exercised there.

## Failure injection summary

| Scenario | Input | Observed outcome | Expected outcome | Verdict |
|---|---|---|---|---|
| Negative thread count | `juju config threads=-1` | SIGSEGV crash; unit shows **"active"** | Blocked with actionable message | **FAIL** |
| Negative duration | `juju config duration=-5` | Accepted; run started with duration=-5 | Config rejected or validated | **FAIL** |
| `threads=true` (bool) | `juju config threads=true` | Rejected by Juju ("expected int, got true") | Same | **PASS** |
| Relation removal during prepare | `juju remove-relation` while prepare running | Deferred; applied after prepare; unit blocked | Same | **PASS** |
| Relation removal after prepare | `juju remove-relation` with tables present | Unit blocked — "No database relation available" | Same | **PASS** |
| Sysbench exit code 1 (run, after relation recreate) | `run` after relation recreate | "blocked — Sysbench failed, please check logs" | Same | **PASS** |
| MySQL prepare deadlock | `prepare scale=1 threads=1` on MySQL 8.0 | Action blocks >33 min; unit agent stuck | Non-blocking or timeout with error | **FAIL** |
| SIGKILL during prepare | `sudo kill -9 <pid>` while prepare running | Unit shows **"active"**; peer data has ERROR but not surfaced | Blocked | **FAIL** |
| SIGKILL during run | `sudo kill -9 <pid>` while run running | Unit blocked — "Sysbench failed, please check logs" | Same | **PASS** |
| Stop action | `stop` action on idle unit | Service stopped; "blocked — Sysbench is stopped after run" | Same | **PASS** |
| Charm upgrade during prepare | not tested | not tested | Graceful defer or error | **UNTESTED** |
| Junk in secret | not tested | not tested | Blocked with message | **UNTESTED** |
| Restart unit | not tested | not tested | Clean restart | **UNTESTED** |

## Findings

### `planned_units() <= 1` bypasses `_has_error_happened()` — root cause of "active after crash"
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/sysbench.py:203–218`
- **Evidence**:
  ```python
  if not self.app_status() or not self.unit_status() or self.charm.app.planned_units() <= 1:
      return self.service_status()
  ```
  On the default single-unit deployment, `planned_units() <= 1` is always True, so
  `_has_error_happened()` is never called. Even though `_execute_sysbench_cmd` writes
  `SysbenchExecStatusEnum.ERROR` into peer relation data when sysbench crashes, this early
  return prevents the ERROR check. `service_status()` then returns `UNSET` (target never
  created because prepare crashed) → `_set_sysbench_status()` maps `UNSET` to `ActiveStatus()`.
  Confirmed live twice: after `threads=-1` → SIGSEGV, and after `sudo kill -9` on the prepare
  process — both times `juju status` showed "active" while peer relation data recorded
  `status: error`. Run-time failures (after a successful prepare) are not affected, because in
  that case `service_status()` itself returns `ERROR` (the systemd unit is in `failed` state)
  and is caught correctly.
- **Why it matters**: every single-unit deployment (the default) that crashes during prepare —
  SIGSEGV, SIGKILL, bad config, database auth failure, etc. — silently shows "active" instead
  of "blocked". Open issue #151 (ARM SIGSEGV) would be masked the same way.
- **Fix**: call `_has_error_happened()` before the `planned_units()` guard:
  ```python
  if self._has_error_happened():
      return SysbenchExecStatusEnum.ERROR
  if not self.app_status() or not self.unit_status() or self.charm.app.planned_units() <= 1:
      return self.service_status()
  ```
  Additionally, `charm.py:78–79` maps `UNSET` directly to `ActiveStatus()`; that mapping
  should also check `_has_error_happened()` before defaulting to active.
- **Linter rule**: "error status checks must not be inside conditional blocks guarded by
  `planned_units()`" — not mechanically checkable without failure injection.

### Password visible in process list and debug log
- **Severity**: critical
- **Kind**: bug
- **Where**: `templates/sysbench.service.j2:8`, `templates/sysbench_svc.py:44–47`, `src/charm.py:182`
- **Evidence**: `ps aux` consistently shows `--db_password=REDACTED` and
  `--pgsql-password=REDACTED` in both `sysbench_svc.py` and `sysbench` child process
  command lines. The unit log also shows it via the logged `CalledProcessError`:
  ```
  WARNING unit.sysbench/0.juju-log server.go:405 Process failed with: Command
  '['/usr/bin/sysbench_svc.py', ..., '--db_password=REDACTED', ...]' returned non-zero
  ```
  Tracked upstream as issue #30. Credential *storage* is not the problem — both MySQL and
  PostgreSQL relations use Juju secrets and the charm resolves them correctly; the leak is
  where the resolved password is later passed as a CLI argument.
- **Why it matters**: any process able to read `/proc/<pid>/cmdline` (including unprivileged
  co-tenant processes) can extract the database password. Operators with `juju debug-log`
  access can extract it from forwarded logs.
- **Fix**: write the password to a root-owned file (mode 0o600), pass it via
  `EnvironmentFile=/etc/sysbench/creds.env` in the systemd unit, and source it in
  `sysbench_svc.py`. For the log exposure, change
  `logger.warning(f"Process failed with: {e}")` to something that excludes command args, e.g.
  `logger.warning("Sysbench process failed with exit code %s", e.returncode)`.
- **Linter rule**: "password or secret fields must not appear in command-line arguments or
  process cmdline" — mechanically checkable via `ps --no-headers` or `/proc/*/cmdline`.

### `subprocess.check_output` in `_exec` deadlocks — confirmed on MySQL
- **Severity**: critical
- **Kind**: bug / performance
- **Where**: `templates/sysbench_svc.py:50` (`_exec` method)
- **Evidence**: confirmed on MySQL 8.0 with `prepare scale=1 threads=1`. Action started
  17:10:35, still running at 17:43+ (>33 minutes, never completed). Unit agent completely
  stuck — no further actions dispatchable; a second `prepare` call queued as "pending"
  indefinitely. The MySQL TPCC Lua script's prepare output exceeds the Linux pipe buffer
  (64KB), so `subprocess.check_output()` blocks while the child blocks trying to write more
  output. The `run()` method already uses `subprocess.Popen` with streaming stdout, avoiding
  this; `_exec()` does not.
- **Why it matters**: MySQL is completely unusable with this charm — every prepare hangs the
  unit agent indefinitely. Confirmed, not theoretical. PostgreSQL prepare did not deadlock in
  this review, plausibly because its Lua script produces less output per second and stays
  under the buffer limit (unverified).
- **Fix**: replace `subprocess.check_output()` with `subprocess.Popen` and a draining thread,
  matching the pattern already used in `run()`:
  ```python
  def _exec(self, cmd):
      proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      output = []
      def drain():
          for line in proc.stdout:
              output.append(line)
      import threading; t = threading.Thread(target=drain); t.start()
      retcode = proc.wait(); t.join(); return b"".join(output)
  ```
- **Linter rule**: "`subprocess.check_output` must not be used with a command that produces
  unbounded stdout" — not mechanically checkable.

### 25 pyright type errors not caught by CI
- **Severity**: high
- **Kind**: lint
- **Where**: `tox.ini` lint target does not run pyright
- **Evidence** (`pyright src/charm.py src/relation_manager.py src/sysbench.py`):
  - `src/charm.py:73`: `_set_sysbench_status()` declares `-> SysbenchExecStatusEnum` but has no
    `return` statement — always returns `None` implicitly.
  - `src/charm.py:122`: `_unit_ip` declares `-> str` but `get_binding().network.bind_address`
    returns `IPv4Address | IPv6Address | str | None`.
  - `src/charm.py:134,270`: `database.script()` / `database.chosen_db_type()` return
    `str | None`, passed to `render_service_file` which expects `str`.
  - `src/charm.py:215`: `check()` declares `-> SysbenchExecStatusEnum` but returns `None` when
    `SysbenchIsInWrongStateError` is caught; caller does `if not self.check()`, treating `None`
    as falsy.
  - `src/relation_manager.py:48`: `on = DatabaseManagerEvents()` overrides `Object.on`.
  - `src/relation_manager.py:59`: `config.get("request-external-connectivity")` returns
    `bool | int | float | str | None`, assigned to `external_node_connectivity: bool`.
  - `src/relation_manager.py:119`: `get_db_config()` declares
    `-> SysbenchBaseDatabaseModel | None` but returns `Dict[str, Any]`.
  - `src/relation_manager.py:134,135`: `config.get("threads")` etc. are
    `bool | int | float | str | None`, passed where `int` is required.
  - `src/relation_manager.py:184,200`: `get_database_options()` returns `Dict[str, Any]`, used
    where `SysbenchBaseDatabaseModel` is expected.
  - `src/sysbench.py:138`: `unset()` declares `-> bool` but `except Exception: pass` has no
    return — implicitly returns `None`.
  - `src/sysbench.py:159`: `_relation` declares `-> Dict[str, Any]` but
    `model.get_relation()` returns `Relation | None`.
  - `src/sysbench.py:167,175,183,184,187,188`: callers access `self._relation.data[...]` and
    `self._relation.units` — `Dict` has no such attributes.
- **Why it matters**: all 25 errors are real type mismatches; `_relation`'s annotation is
  demonstrably wrong, and the `_set_sysbench_status`/`check()` return-type bugs mean callers
  can silently receive `None`.
- **Fix**: add `poetry run pyright src/` to the lint target and fix all 25 errors.
- **Linter rule**: pyright in CI is standard practice for ops-framework charms.

### `_relation` property has wrong type annotation
- **Severity**: high
- **Kind**: bug
- **Where**: `src/sysbench.py:187`
- **Evidence**:
  ```python
  @property
  def _relation(self) -> Dict[str, Any]:      # wrong annotation
      return self.charm.model.get_relation(self.relation)  # actually Relation | None
  ```
  All callers access `self._relation.data[...]` and `self._relation.units`, which are
  `Relation` attributes, not `Dict` attributes.
- **Why it matters**: relying on the declared type would cause incorrect handling (e.g.
  calling `.get()` or failing to handle `None`).
- **Fix**: change return type to `Relation | None`.
- **Linter rule**: pyright `reportReturnType` — mechanically checkable.

### Charm cannot run on Kubernetes
- **Severity**: high
- **Kind**: bug
- **Where**: throughout `src/sysbench.py` and `src/charm.py`
- **Evidence**: the charm calls `subprocess.check_output(["systemctl", "is-active", ...])`,
  `service_running()`, `service_stop()`, `service_failed()`, `service_restart()` (from
  `charmlibs.systemd`) throughout; `systemctl` is not available in k8s pods. Open issue #36
  confirms `FileNotFoundError: [Errno 2] No such file or directory: 'systemctl'`. No k8s
  substrate in metadata, no Pebble workload defined; `concierge.yaml` comment mentions
  "Switch to Canonical k8s" (#247) as future work.
- **Why it matters**: operators attempting a k8s deployment get a `FileNotFoundError` in the
  install hook and a non-functional charm.
- **Fix**: complete the k8s migration (#247), replacing systemd calls with Pebble
  (`container.pebble`) equivalents; add a `containers:` stanza to `metadata.yaml`.
- **Linter rule**: not mechanically checkable — requires a k8s deployment attempt.

### No pydantic constraints on `threads`/`duration`, and validation errors are swallowed
- **Severity**: high
- **Kind**: bug
- **Where**: `src/constants.py:105–113`, `src/relation_manager.py:71–75`
- **Evidence**:
  ```python
  class SysbenchExecutionModel(BaseModel):
      threads: int
      duration: int
      db_info: SysbenchBaseDatabaseModel
  ```
  No `ge=1` constraints, so `threads=-1` / `duration=-5` pass validation; the crash only
  happens at execution time. Compounding this, `relation_status()` catches all exceptions at
  DEBUG level and still returns `AVAILABLE`:
  ```python
  try:
      SysbenchOptionsFactory(...).get_database_options()
  except Exception as e:
      logger.debug("Failed relation options check %s" % e)
  ```
  So even a future pydantic `ValidationError` would be silently swallowed here.
- **Fix**: add `threads: int = Field(ge=1)` and `duration: int = Field(ge=1)`; narrow the
  `except Exception` in `relation_status()` and let validation errors propagate to a
  `BlockedStatus`.
- **Linter rule**: pyright `reportAssignmentType` — mechanically checkable for the missing
  constraints; the swallowed-exception pattern is not.

### `is_tls_enabled` always returns `False` — scrape config HTTP/HTTPS mismatch risk
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:115–117`
- **Evidence**: `is_tls_enabled` always returns `False`; `scrape_config()` at line 133 uses
  `"scheme": "https" if self.is_tls_enabled else "http"`. If TLS support were added and this
  property updated without updating the metrics server, scrapes would silently use the wrong
  scheme against an HTTP-only endpoint (`sysbench_svc.py:91`).
- **Why it matters**: the property name implies a real check; currently it is dead code.
- **Fix**: implement TLS for the metrics endpoint, or rename the property (e.g.
  `is_http_metrics`) with a comment explaining why it is always `False`.
- **Linter rule**: "property that always returns a constant should be reviewed for dead code" —
  not mechanically checkable.

### No unit tests — `tests/unit/` does not exist
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tox.ini:24` references `tests/unit`; `lib/` excluded from ruff lint
- **Evidence**: `tox -e unit` fails with `file or directory not found: tests/unit`.
  `tox -e lint` passes cleanly (ruff, codespell, shellcheck) but does not run pyright. ruff on
  `lib/charms/data_platform_libs/v0/data_interfaces.py` (excluded from CI's lint target) finds
  2 complexity errors that are invisible to CI.
- **Coverage gaps**: `SysbenchStatus.check()`'s state machine (including the
  `planned_units() <= 1` bypass), `DatabaseRelationManager.check()`, `_set_sysbench_status`,
  the prepare-crash scenario, the MySQL deadlock, negative config validation, and
  `_has_error_happened()`'s error-surfacing path all have zero unit test coverage. The existing
  integration test `test_run_action_and_cause_failure` kills the sysbench *child* process
  during `run` (after a successful prepare) — it passes, but for the wrong scenario: it never
  exercises the prepare-crash path, which is where the status-masking bug actually lives.
- **Fix**: add `tests/unit/`; add pyright to `tox -e lint`; run `ruff check lib/`.
- **Linter rule**: "test directory `tests/unit/` must exist" — mechanically checkable.

### grafana-agent subordinate incompatible with sysbench's base
- **Severity**: medium
- **Kind**: bug
- **Where**: charm topology / base mismatch
- **Evidence**: `grafana-agent` 2/edge (rev 848) requires ubuntu@24.04; sysbench is on
  ubuntu@22.04. `juju integrate sysbench grafana-agent` fails:
  ```
  ERROR cannot add relation: subordinate must support principal application's base;
  subordinate only supports: [ubuntu@24.04/stable]
  ```
- **Why it matters**: the cos-agent integration cannot currently be exercised or used in
  production with the documented `grafana-agent` charm.
- **Fix**: upgrade sysbench to ubuntu@24.04, find a grafana-agent build supporting 22.04, or
  document a standalone Prometheus scrape job as the interim path.
- **Linter rule**: not mechanically checkable.

### Duplicate `--duration` in systemd service command line
- **Severity**: medium
- **Kind**: bug
- **Where**: `templates/sysbench.service.j2:8`
- **Evidence**: the jinja template embeds `{{ duration }}` in `ExecStart=`, and
  `sysbench_svc.py`'s `main()` also appends `f"--duration={args.duration}"`. Confirmed via
  `systemctl show sysbench.service`: `--duration=-5 --command=run ... --duration=-5`. The
  second flag silently overrides the first, which happens to work today but is fragile.
- **Fix**: remove `{{ duration }}` from the template's `ExecStart=` line.
- **Linter rule**: "the same CLI flag must not appear more than once in a command template" —
  mechanically checkable.

### No `upgrade-charm` handler — upgrade path is implicit
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` — no `on_upgrade_charm` handler defined
- **Evidence**: no `upgrade` handler exists. `_on_config_changed` restarts the service if
  running but does not check whether a prepare is currently in progress before re-rendering
  the service file.
- **Why it matters**: an upgrade during a running prepare could rewrite the service file
  mid-operation and leave inconsistent state (unverified — not exercised in this review).
- **Fix**: add an `on_upgrade_charm` handler that defers while a prepare is running and
  restores a clean state afterward.
- **Linter rule**: not mechanically checkable.

### `charm.py` — `_set_sysbench_status()` and `check()` declare return types they don't satisfy
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:73–86, 205–215`
- **Evidence**: `_set_sysbench_status()` declares `-> SysbenchExecStatusEnum` but has no
  `return` statement. `check()` declares `-> SysbenchExecStatusEnum` but returns `None` when
  `SysbenchIsInWrongStateError` is caught with no event to defer. Callers do
  `if not (status := self.check())`, treating `None` as falsy and triggering a misleading
  "unset" failure message.
- **Fix**: change both return type annotations to `-> SysbenchExecStatusEnum | None` and
  handle the `None` case explicitly at call sites.
- **Linter rule**: pyright `reportReturnType` — mechanically checkable.

### `sysbench.py:138` — `unset()` can return `None` instead of declared `bool`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/sysbench.py:137–146`
- **Evidence**: pyright: "Function with declared return type 'bool' must return value on all
  code paths." `except Exception: pass` does not return; if `os.remove()` raises, callers
  doing `result ^= service_stop(...)` get `TypeError: unsupported operand type(s) for ^: 'bool'
  and 'NoneType'`.
- **Fix**: add `return False` in the `except Exception: pass` block.
- **Linter rule**: pyright `reportReturnType` — mechanically checkable.

### `relation_manager.py` config-to-model type chain is unsafely typed
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/relation_manager.py:134–135, 200`
- **Evidence**: `SysbenchExecutionModel(threads=self.charm.config.get("threads"), ...)` —
  `config.get()` returns `bool | int | float | str | None`; passing a `bool` would fail
  pydantic validation with a confusing traceback. `get_database_options()` returns
  `Dict[str, Any]` but is used where `SysbenchBaseDatabaseModel` is expected.
- **Fix**: add explicit coercion, e.g. `threads=int(self.charm.config.get("threads", 1))`.
- **Linter rule**: pyright `reportArgumentType` — mechanically checkable.

### `DATABASE_NAME` is a hardcoded TODO constant
- **Severity**: low
- **Kind**: bug
- **Where**: `src/constants.py:28`
- **Evidence**: `DATABASE_NAME = "sysbench-db"  # TODO: use a UUID here and publish its name in
  the peer relation`. Every unit connecting to the same PostgreSQL server gets the same
  database name, risking conflicts across deployments sharing a server.
- **Fix**: generate a UUID in the leader-elected hook and store it in the peer relation data.
- **Linter rule**: not mechanically checkable.

### `on` class attribute overrides `Object.on`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/relation_manager.py:48`
- **Evidence**: `class DatabaseRelationManager(Object): ... on = DatabaseManagerEvents()`.
  pyright: `Property "on" already defined in class "Object"`.
- **Fix**: rename to e.g. `db_events`.
- **Linter rule**: pyright `reportIncompatibleMethodOverride` — mechanically checkable.

### `refresh_events=[]` has no effect
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:53`
- **Evidence**: `COSAgentProvider(..., refresh_events=[])`. The library
  (`lib/charms/grafana_agent/v0/cos_agent.py:673`) does
  `self._refresh_events = refresh_events or [self._charm.on.config_changed]`. Since `[]` is
  falsy, this evaluates to `[self._charm.on.config_changed]` — config-changed events do
  trigger scrape config refresh regardless of the empty list.
- **Why it matters**: dead code today; if the library's guard ever changes from `or` to an
  explicit `is not None` check, the bug would silently activate.
- **Fix**: remove `refresh_events=[]` or pass `None`.
- **Linter rule**: "empty-list literal used with `x or default` is dead code" — not
  mechanically checkable.

### Charm library versions pinned to v0
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/data_platform_libs/v0/` (LIBAPI=0, LIBPATCH=58),
  `lib/charms/grafana_agent/v0/` (LIBAPI=0, LIBPATCH=25)
- **Evidence**: `grep "^LIB" lib/charms/*/v0/*.py`. Both libraries remain on `v0`.
- **Fix**: run `charmcraft libs` to check for newer major versions and evaluate migrating.
- **Linter rule**: `charmcraft libs` can be run in CI to flag outdated pins.

### Misleading comment in `_on_config_changed`
- **Severity**: low
- **Kind**: docs
- **Where**: `src/charm.py:126`
- **Evidence**: `# For now, ignore the configuration` — but the method body reads and uses
  `database.get_execution_options()` and conditionally restarts the service.
- **Fix**: remove or correct the comment.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Status precedence design**: the destructor-based status check correctly prioritizes the
  most important issue (no DB relation, multiple relations, missing data) before service
  status. The concept — cross-checking app-level, unit-level, and service-level status — is
  sound; the bug is only that `service_status()` returns `UNSET` on a crashed prepare, masking
  the `ERROR` recorded in peer data.
- **Action error messages**: action handlers consistently return meaningful messages via
  `event.fail("Failed: ...")` rather than bare `event.fail()`.
- **Peer relation for multi-unit coordination**: using a peer relation to share status across
  units is the right pattern.
- **Poetry build**: uses Poetry with custom `poetry-deps` and `charm-poetry` build parts — the
  modern Canonical approach.

## Common-practice notes

- **Libraries co-located** under `lib/charms/`, as is standard. `data_platform_libs` (5782
  lines) has full Juju secrets support; both MySQL and PostgreSQL relations use it correctly.
- **tox without pyright**: the lint target runs ruff, codespell, and shellcheck but not
  pyright, letting 25 real type errors go undetected.
- **`__del__` for status**: using the destructor for status evaluation is unusual and fragile
  — an exception inside `__del__` would crash the unit agent. `update_status` would be the
  more standard, reliable pattern.
- **Machine-only charm**: `concierge.yaml` references a planned "Switch to Canonical k8s"
  (#247), but the current systemd dependency needs a full Pebble rewrite; issue #36 confirms
  the k8s failure exists today.
- **`lib/` excluded from ruff lint**: the tox lint target is `src/ tests/`, excluding `lib/`;
  2 complexity errors in vendored `data_interfaces.py` are invisible to CI as a result.

## Tests

- **No unit tests**: `tests/unit/` does not exist; `tox -e unit` exits with code 4. `tox -e
  lint` passes (ruff, codespell, shellcheck) but does not run pyright.
- **Integration tests** (`tests/integration/test_charm.py`, 365 lines) cover the happy path:
  - `test_prepare_action`: runs prepare, waits for "waiting" status.
  - `test_run_action_and_cause_failure`: SIGKILLs the sysbench child process during a *run*
    (after successful prepare), verifies the service fails and the unit blocks. Catches the
    SIGKILL-during-run case, not the SIGSEGV/SIGKILL-during-prepare case — those have
    different status-machine behaviour.
  - `test_run_action`: runs with a duration, verifies blocked on completion.
  - `test_clean_action`: runs clean, verifies "active" status.
- **Spread tests**: four spread files (mysql / mysql-router / postgresql / pgbouncer) on
  lxd-vm and github-ci backends.
- **Coverage gaps** (all confirmed untested): the SIGSEGV/SIGKILL-during-prepare masking bug,
  negative thread/duration config values, the MySQL deadlock, `relation_manager.check()`'s
  multi-status path, `_set_sysbench_status()` return handling, `_has_error_happened()`'s
  surfacing path, and `unset()` returning `None` instead of `bool`.

## Docs

- **README.md**: one-line description plus a warning; real docs live on Discourse
  (`https://discourse.charmhub.io/t/charmed-sysbench-documentation-home/13945`).
- **CONTRIBUTING.md**: covers development workflow, testing, and release process.
- **charmcraft.yaml**: well-commented with bug references and rationale.
- **No terraform module**: no `.terraform/` files present.
- **Secrets handling undocumented but correct**: both MySQL 8.0 and PostgreSQL 14 use Juju
  secrets for credentials (confirmed); the README does not document which backend uses which
  credential mechanism.

## Open questions

1. **MySQL prepare deadlock**: confirmed to run indefinitely (>33 minutes and counting).
   `subprocess.check_output()` in `_exec` must be replaced with streaming `Popen`. Is this on
   the near-term roadmap given MySQL is unusable today?
2. **ARM SIGSEGV (#151)**: appears to be the same `threads=-1`-style crash observed on x86
   (unverified on real ARM hardware here). The `planned_units()` bypass would mask it the same
   way on single-unit ARM deployments.
3. **grafana-agent base mismatch**: is an ubuntu@24.04 base for sysbench planned, to unblock
   the cos-agent integration?
4. **k8s migration (#247)**: `concierge.yaml` enables a k8s provider but the charm has no
   Pebble workload; is there a timeline for the rewrite?
5. **Pydantic validation**: adding `ge=1` constraints on `threads`/`duration` is the obvious
   fix, but the broad `except Exception` in `relation_status()` would currently swallow the
   resulting `ValidationError` — both need fixing together.
6. **Why didn't PostgreSQL's prepare deadlock?** Plausibly its Lua script output is less
   verbose than MySQL's TPCC script and stays under the 64KB pipe buffer — not independently
   verified.
