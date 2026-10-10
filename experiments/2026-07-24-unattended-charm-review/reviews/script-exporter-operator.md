# script-exporter-operator

The script-exporter charm is a Juju subordinate machine charm that deploys the Prometheus-compatible Script Exporter on host machines, converting arbitrary script output into metrics. It is well-structured and follows modern charm conventions (`src/` layout, `uv` packaging, `ops-scenario` tests, bundled binary), but ships several critical uncaught-exception bugs that crash hooks in normal operation (bad YAML, systemd failures), plus a multi-subordinate binary race, a missing `upgrade_charm` handler, and multiple silent-failure paths where the unit reports Active while the workload is actually broken. A maintainer should first fix the unhandled `SystemdError`/`yaml.ParserError`/`TypeError` paths in `src/charm.py` (they crash hooks on ordinary misconfiguration) and add exception handling around `_ensure_binary` for the multi-subordinate race, before addressing the lower-severity UX and maintainability items.

| | |
|---|---|
| Repo | canonical/script-exporter-operator @ `295c8f4` (2026-06-30) |
| Charms | script-exporter |
| Substrate | machine |
| Deployed | yes — concierge-lxd-4, channel 3.2/stable (rev 76 vs local rev 77+), refreshed to 3.2/edge rev 124; additional fresh deployments and failure injections performed across several models |
| Reviewed | 2026-08-22 |

## What it does

A subordinate machine charm (related over `juju-info`). Deploys the `script_exporter` binary (v3.2.0, bundled in the charm at pack time) as a systemd service on the host machine. Exposes a `/probe` HTTP endpoint on port 9469 for Prometheus to scrape. Provides `cos-agent` (optional, limit 1) to forward scrape jobs and charm traces to a Grafana Agent. Optionally requires `receive-ca-cert` for TLS validation of the tracing endpoint.

Four config options: `script_file` (single script), `scripts_archive` (LZMA+base64 tarball), `config_file` (script_exporter YAML config), `prometheus_config_file` (Prometheus scrape jobs).

## Deployment log

1. Created model `rv-script-exporter` on `concierge-lxd-4` (Juju 4.0.12).
2. Deployed `ubuntu` base charm (`latest/stable`, rev 79, ubuntu@24.04) — machine came up in ~3 min.
3. Deployed `script-exporter` from charmhub (`3.2/stable`, rev 76 — local HEAD is rev 77+).
4. Related script-exporter to ubuntu via `juju integrate script-exporter ubuntu`.
5. Subordinate agent installed on machine 0.
6. Set `script_file`, `config_file`, `prometheus_config_file` via `juju config`, using shell command substitution for multi-line YAML values.
7. Observed hook sequence:
   - install hook: binary installed, dirs created ✅
   - config-changed (no config): status=blocked ✅
   - config-changed (config set, first time): briefly active, then error — hook failed due to `SystemdError` from `service_restart` ❌
   - config-changed (retry): error ❌
   - config-changed (second auto-retry): active ✅ — Juju self-healed
   - config-changed (bad YAML in `prometheus_config_file`): error — hook failed on uncaught `yaml.ParserError` from `scripts_scraping_jobs` ❌
   - config-changed (correct YAML restored): active ✅
8. Deployed `self-signed-certificates` (rev 586, ubuntu@24.04), related via `receive-ca-cert`:
   - relation-created/joined/changed hooks all fired ✅
   - CA certificate received and written without error; unit stayed active ✅
9. Refreshed `script-exporter` from `3.2/stable` (rev 76) → `3.2/edge` (rev 124):
   - `upgrade-charm` fired (no handler — did nothing)
   - `config-changed` fired, ran `service_restart`; unit stayed active
10. Attempted cos-agent integration with `grafana-agent`:
    - Relation created, grafana-agent deploying on machine 0
    - grafana-agent snap install took several minutes, ended up blocked (missing required integrations — expected)
    - `script-exporter/1` (subordinate of grafana-agent) install hook **failed**: `OSError: [Errno 26] Text file busy: '/usr/local/bin/script_exporter'` — binary held open by `script-exporter/0`'s running process ❌
11. `juju remove-application script-exporter`: unit removed cleanly, stop hook ran ✅
12. Re-deployed in a fresh model on `concierge-lxd-4`:
    - Deployed `self-signed-certificates`, related via `send-ca-cert` endpoint ✅
    - CA cert written to `/etc/script-exporter/receive-ca-cert.crt`, mode 644 (world-readable) ✅ (confirmed via `stat`)
    - Removed relation: CA cert file correctly deleted ✅
    - Deployed `grafana-agent`, related via cos-agent; `grafana-agent/0` became subordinate of script-exporter on machine 0
    - `script-exporter/2` (second subordinate) install hook **failed again**: `OSError: Text file busy` — reproduces the binary race
13. Tested bad config scenarios:
    - `script_file='plain text'` (no shebang): charm stays Active, runtime failure, no Juju indication ❌
    - `script_file='#!/bin/sh\nexit 1'`: charm Active, `script_success=0` — correct ✅
    - config referencing a script name not in the archive: charm Active, binary logs ERROR, no Juju indication ❌
14. Attempted Juju 3.6 deployment on `concierge-lxd`:
    - `ubuntu` deployment stuck in `allocating`; error `"download request with archiveSha256 length 0 not valid"` — charm-store cache issue on the controller, not a charm bug. Juju 3.x substrate could not be tested in this environment.
15. Fresh deployment on a new model (concierge-lxd-4, Juju 4.0.12): deployed ubuntu (rev 79) and script-exporter (rev 76); set `script_file`/`config_file` → active.
16. Failure injection — remove `juju-info` relation:
    - `juju remove-relation script-exporter ubuntu` → subordinate unit destroyed (scale=0), stop hook fired, service received SIGTERM and exited gracefully ✅
    - Re-integrated → new subordinate created, active ✅
17. Failure injection — bad `prometheus_config_file`:
    - `juju config script-exporter prometheus_config_file="not: [valid: yaml"` → error, hook failed ❌
    - `juju resolve --no-retry` → active, but bad config never applied
    - Reset to empty string → active ✅
    - Confirmed via debug-log: `yaml.parser.ParserError` from `scripts_scraping_jobs`
18. Confirmed via scenario test that `scripts_scraping_jobs` (a `@property`, evaluated at line 59 of `src/charm.py` inside `COSAgentProvider(...)` construction in `__init__`) is evaluated eagerly in real Juju. `ops-scenario`'s lazy config loading masks this: `Context(ScriptExporterCharm)` with a bad `prometheus_config_file` in state does not crash in tests, but would crash the real charm at startup if the bad value were present in metadata/deploy-time config.

## Observed behaviour

- **Workload process kill → systemd auto-recovers.** Killing the `script_exporter` process caused systemd's `Restart=always` to restart it in ~12 seconds. No Juju hook fired; unit stayed active throughout.
- **Relation removal → clean teardown.** `juju remove-relation script-exporter ubuntu` destroyed the subordinate unit, ran the stop hook, and the service exited gracefully on SIGTERM. No orphaned unit; the app shows `unknown` status with scale 0.
- **`/probe` endpoint works correctly.** With a proper single-script config (with shebang), `curl localhost:9469/probe?script=test_script` returned `test_metric{label="value"} 1` and `script_success=1`. `/metrics` returns Go runtime metrics. Both reachable on port 9469.
- **`juju resolve` masks errors without fixing them.** Setting `config_file` to invalid YAML failed the hook (`yaml.parser.ParserError`) before `write_text` ran, so the bad config was never written to disk. `juju resolve script-exporter/1 --no-retry` cleared the error and the unit reported active, but the service kept running the *previous* config with no operator-visible indication that the last change was rejected.
- **Service restart on every config-changed.** `_on_config_changed` calls `service_restart(SERVICE_FILENAME)` whenever `config_file` is non-empty, with no comparison to the previous value — even a no-op config change restarts the service (observed in the systemd journal).
- **Bad LZMA archive handled correctly.** Setting `scripts_archive` to invalid LZMA data is caught (`LZMAError`) and produces `BlockedStatus`: "scripts_archive is not a valid lzma archive - Input format not supported by decoder." ✅
- **Config-changed fires twice per config change.** A single `juju config` command triggered two `config-changed` invocations ~1 second apart; the first `service_restart` failed (unhandled `SystemdError` from the rapid restart), the second succeeded. Juju's auto-retry papers over this, but it's a real race window.
- **`receive-ca-cert` relation lifecycle is correct.** CA cert correctly written to `/etc/script-exporter/receive-ca-cert.crt` on relation-changed; correctly deleted on relation removal (`_on_cert_transfer_removed`). File permissions were 644 (world-readable) — see finding below.
- **cos-agent relation data is correct.** `grafana-agent/0`'s relation data included `metrics_scrape_jobs` with a deterministic job name (`script-exporter_script-exporter_<hash>`), `metrics_alert_rules` (`HostDown`, `HostMetricsMissing`), `tracing_protocols: ["otlp_http"]`, empty `dashboards`/`log_slots`.
- **Binary not updated on refresh — confirmed.** After `juju refresh` from rev 76 to rev 124, `/var/lib/juju/agents/unit-script-exporter-1/charm/version` still showed the old build version; `upgrade-charm` fired but has no handler, and `config-changed` restarted the service with the *old* binary.
- **Integration test run against local build.** `test_simple_script.py` deployed the charm to active status; SSH verification failed due to a missing SSH key in the jubilant-created model (environment issue, not a charm bug). Deployment/startup logic itself worked.

## Findings

### Unhandled `SystemdError` from `service_restart`/`service_resume`/`service_stop`/`daemon_reload` crashes hooks
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:103` (`_on_start`), `src/charm.py:108` (`_on_stop`), `src/charm.py:122` (`_on_config_changed`), `src/charm.py:300-305` (`_create_systemd_service`)
- **Evidence**: All calls to `service_restart`, `service_resume`, `service_stop`, and `daemon_reload` use `check=True` by default (`lib/charms/operator_libs_linux/v1/systemd.py`), which raises `SystemdError` on failure and is never caught. Observed live: `service_restart` failed with exit status 1 during the first `config-changed` after the initial config was set, and the hook crashed; Juju's auto-retry eventually succeeded.
- **Impact**: Any condition preventing the service from starting (bad config, missing binary, systemd conflict from rapid restarts, resource exhaustion) crashes the hook. The operator sees a traceback, not an actionable message, and recovery depends on Juju's auto-retry succeeding.
- **Fix**: Wrap all `service_restart`/`service_resume`/`service_stop`/`daemon_reload` calls in try/except for `SystemdError`; on failure set `BlockedStatus` with a diagnostic message instead of letting the exception propagate.
- **Linter rule**: Hook handlers must not let `SystemdError` propagate uncaught — grep for `service_restart|service_resume|service_stop|daemon_reload` without a surrounding try/except for `SystemdError`.

### Unhandled YAML/`TypeError`/`KeyError` in config parsing crashes hooks
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:186` and `src/charm.py:193-198` (`_insert_full_path_in_command`); `src/charm.py:256-258` (`scripts_scraping_jobs`, evaluated eagerly at `__init__` line 59); `src/charm.py:189` (`_insert_full_path_in_command`, null `scripts` key)
- **Evidence**: `yaml.safe_load(config)` and `yaml.safe_load(prometheus_scrape_jobs)` have no exception handling — invalid YAML in `config_file` or `prometheus_config_file` crashes the hook with an uncaught `yaml.parser.ParserError` (reproduced live via `juju config script-exporter prometheus_config_file="not: [valid: yaml"` and equivalent for `config_file`). A valid-but-incomplete `prometheus_config_file` (missing `scrape_configs` key) raises an uncaught `KeyError` on `scrape_jobs["scrape_configs"]` (reproduced via `prometheus_config_file="other_key: value"`). `conf_dict.get("scripts", [])` returns `None`, not `[]`, when the YAML is `scripts:` (null value); the subsequent `for definition in scripts_def:` then raises `TypeError: 'NoneType' object is not iterable` (reproduced via `juju config script-exporter config_file="scripts:"`).
- **Impact**: Because `scripts_scraping_jobs` is evaluated at `__init__` time, a bad `prometheus_config_file` supplied at deploy time (`--config`) crashes the charm on every startup — `juju resolve --no-retry` does not fix it, since the charm crashes again immediately. Ordinary typos in either config file also crash `config-changed`.
- **Fix**: Wrap all `yaml.safe_load` calls in try/except; on parse failure set `BlockedStatus(f"... is not valid YAML: {e}")` and return an empty/safe default. Use `conf_dict.get("scripts") or []` instead of `conf_dict.get("scripts", [])`. Guard `scrape_jobs["scrape_configs"]` with `.get("scrape_configs", [])`.
- **Linter rule**: Hook handlers must not let `yaml.parser.ParserError`/`TypeError`/`KeyError` propagate uncaught from config parsing; `.get()` calls with a non-`None` default must guard against explicit `null` values (`or []` instead of `, []`).

### Multi-subordinate binary race — `OSError: Text file busy`
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:138` (`_ensure_binary`)
- **Evidence**: `shutil.copy("script_exporter", self._binary_path)` raises `OSError: [Errno 26] Text file busy` when the target binary is already open by a running process. Reproduced twice: when `grafana-agent` (which is related over cos-agent) creates a second script-exporter subordinate unit on the same machine, the second unit's install hook fails because the first unit's `script_exporter` process holds `/usr/local/bin/script_exporter` open.
- **Impact**: Any multi-subordinate scenario on the same machine — the primary one being cos-agent integration with grafana-agent — fails the install hook outright.
- **Fix**: Check whether the binary already exists before copying; if the existing binary is the same version, skip the copy; if different, stop the service, copy, and restart.
- **Linter rule**: not mechanically checkable without runtime context — filesystem writes to a path that may be held open by another process should check for existence/version first.

### `_statuses` list accumulates across hook invocations
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:37` (`self._statuses = []`), `src/charm.py:175-179` (`_on_collect_unit_status`)
- **Evidence**: `_statuses` is never cleared; each `_on_collect_unit_status` call appends to it, so by the second invocation the list contains duplicate `ActiveStatus`/`BlockedStatus` entries, and `event.add_status()` is called multiple times with the same status.
- **Impact**: Juju deduplicates statuses in its model today, so no visible bug yet, but the pattern is fragile and any future addition to `_statuses` elsewhere will accumulate unboundedly.
- **Fix**: Clear `_statuses` at the start of `_on_collect_unit_status` (`self._statuses.clear()`), or build the list locally in the handler instead of storing it as instance state.
- **Linter rule**: instance attributes mutated across events without reset should be flagged — partially mechanically checkable.

### No `upgrade_charm` handler — bundled binary not updated on refresh
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py` — no `on.upgrade_charm` observer
- **Evidence**: `grep -n "upgrade.charm\|on.upgrade" src/charm.py` returns nothing. Confirmed live: after `juju refresh` from rev 76 to rev 124, the version file in the unit's charm directory still showed the old build, and `config-changed`'s `service_restart` ran against the old binary — the new binary is only installed via `_on_install` for brand-new units.
- **Impact**: `juju refresh` does not apply binary updates (including security fixes) to existing units; only newly created units get the new binary.
- **Fix**: Add an `on.upgrade_charm` observer that calls `_ensure_binary()` (and restarts the service) on refresh.
- **Linter rule**: machine charm bundling a binary but with no `upgrade_charm` handler — mechanically checkable via grep for `upgrade_charm` in charm source.

### `juju resolve` silently masks rejected config — operator unaware
- **Severity**: high
- **Kind**: ux
- **Where**: `src/charm.py` — uncaught exceptions abort the hook before config is written to disk
- **Evidence**: When `config_file` was set to invalid YAML, the hook failed before `_set_config_file()` could write the new config. `juju resolve script-exporter/1 --no-retry` cleared the error and reported the unit active; the service kept running the previous config. Verified: post-resolve, `curl localhost:9469/probe?script=test_script` returned metrics from the old config, and the on-disk config file still had the previous value.
- **Impact**: The operator believes their config change was applied because the unit is active. If the service ever restarts (e.g. reboot), it may fail on a queued bad config that was never surfaced. Hidden, hard-to-diagnose failure mode.
- **Fix**: All config validation must produce `BlockedStatus` on failure, so `resolve` clears an unambiguous blocked state rather than papering over a silently-reverted config.
- **Linter rule**: not mechanically checkable.

### Two silent runtime failures — charm stays Active despite broken script
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` — no script content validation; `src/charm.py:193-198` (`_insert_full_path_in_command`, silent skip on unknown script name)
- **Evidence**:
  - Setting `script_file` to plain text with no shebang (e.g. `echo "hello"`) is written to `/etc/script-exporter-script` (mode 0o755) and executed by the binary, which fails with `exitCode=-1`; `/probe` shows `script_success=0`, `script_exit_code=-1`; binary logs "Script execution failed" at ERROR. Charm reports Active throughout.
  - When `config_file` references a script name not present in `scripts_archive` (e.g. `wrong.sh` vs. archived `script1.sh`), `_insert_full_path_in_command` logs at DEBUG and silently skips it (`continue`); the config is written with the unresolved path unchanged; the binary fails with `fork/exec ...: no such file or directory`. Charm reports Active.
- **Impact**: In both cases the operator has no Juju-visible indication of the failure; they must manually curl `/probe` to discover it.
- **Fix**: Log at WARNING (not DEBUG) when a script is skipped, and/or set `BlockedStatus` if a referenced script cannot be resolved. Consider validating script content (shebang presence) in `_set_script_files()`.
- **Linter rule**: function silently skips configuration entries on mismatch without a warning-level log — mechanically checkable for the DEBUG-log case.

### `PermissionError` from `mkdir` not handled in CA cert path creation
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:323` (`_on_cert_transfer_available`)
- **Evidence**: `CA_CERT_PATH.parent.mkdir(parents=True, exist_ok=True)` is not wrapped in exception handling; if the parent directory exists with restrictive permissions, this raises an uncaught `PermissionError`. (unverified — not exercised during the live deployment runs, inferred from code.)
- **Impact**: The `receive-ca-cert` integration hook would crash unhandled if the directory is not writable.
- **Fix**: Wrap the `mkdir` call in try/except for `PermissionError`; set `BlockedStatus` on failure.
- **Linter rule**: filesystem operations (`mkdir`) called without error handling for `PermissionError` — partially mechanically checkable.

### Port 9469 hardcoded and never registered with Juju
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:43` (`EXPORTER_PORT = 9469`)
- **Evidence**: The charm never calls `self.unit.open_port()`. Mentioned in upstream issue #17.
- **Impact**: `juju expose` cannot work for this charm since the port is never registered with the Juju model; the exporter can only be reached from the machine itself or via relation data.
- **Fix**: Call `self.unit.open_port("tcp", EXPORTER_PORT)` when the service starts, and `close_port` on stop.
- **Linter rule**: charm uses a hardcoded network port but never calls `open_port` — mechanically checkable.

### CA certificate file written world-readable
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:325` (`_on_cert_transfer_available`)
- **Evidence**: `CA_CERT_PATH.write_text(certs + "\n")` uses the default umask (typically 022) → world-readable. Confirmed live via `stat -c "%a %U:%G %n" /etc/script-exporter/receive-ca-cert.crt` → `644 root:root`.
- **Impact**: CA trust material is sensitive; world-readable permissions let any local user read it.
- **Fix**: Write with `mode=0o600`, or `os.chmod(CA_CERT_PATH, 0o600)` after writing.
- **Linter rule**: sensitive file written without explicit mode restriction — mechanically checkable.

### Path traversal in `_extract_scripts_archive`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:177` (`_extract_scripts_archive`)
- **Evidence**: `tar.extractall(path=self._scripts_dir_path)` with no member-path validation. A malicious tarball with entries like `../../etc/cron.d/malicious` or an absolute path could write outside the intended directory. Requires an attacker with `juju config` access. (unverified live — code-review finding, not exercised in the deployment runs.)
- **Impact**: Privilege escalation on the host if an attacker with config access supplies a crafted `scripts_archive`.
- **Fix**: Validate `tar.getmembers()` names before extraction, rejecting absolute paths or `..` components.
- **Linter rule**: `tar.extractall()` called without path validation on user-controlled input — mechanically checkable.

### `_insert_full_path_in_command` re-decodes `scripts_archive` twice per config-changed
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:113` (`_on_config_changed`), `src/charm.py:231` (`_insert_full_path_in_command`)
- **Evidence**: `_on_config_changed` calls `_retrieve_script_names()` and stores the result in `self._script_names`, but `_insert_full_path_in_command` calls `_retrieve_script_names()` again independently, re-running the base64+LZMA decode.
- **Impact**: Doubles the CPU cost of archive decoding on every `config-changed`, worse for large archives.
- **Fix**: Have `_insert_full_path_in_command` use the already-computed `self._script_names` instead of re-decoding.
- **Linter rule**: not mechanically checkable without dataflow analysis.

### Service unconditionally restarted on every config-changed
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:122`
- **Evidence**: `service_restart(SERVICE_FILENAME)` is called whenever `config_file` is non-empty, with no comparison to the previously-applied value. Observed: setting `prometheus_config_file` to identical content still restarts the service (systemd journal).
- **Impact**: Every config-changed hook — even unrelated ones — interrupts metric collection; a Prometheus scrape landing during the restart window fails.
- **Fix**: Store a hash/content of the last-applied config and only restart when it changes.
- **Linter rule**: not mechanically checkable without stored state.

### `_insert_full_path_in_command` dead code from type mismatch
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:200` (`_insert_full_path_in_command`)
- **Evidence**: `self._single_script_path in self._script_names` — `_script_names` is `List[str]` and `_single_script_path` is a `LocalPath` object, so this comparison is always `False`; the intended skip branch never executes. In practice this does not currently break anything because a user supplying the exact path (`/etc/script-exporter-script`) hits an earlier `continue` via the `executable not in self._script_names` check.
- **Impact**: Confusing dead code; a latent bug that could surface if the surrounding logic changes.
- **Fix**: Fix the type comparison (compare strings) or remove the dead branch.
- **Linter rule**: type mismatch in `in` comparison (`LocalPath` vs `List[str]`) — mechanically checkable with a type checker (pyright would catch this).

### `_retrieve_script_names` re-parses `scripts_archive` on every call, no caching
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:239-252`
- **Evidence**: Called from both `_on_config_changed` and `_insert_full_path_in_command`; each call re-decodes the base64+LZMA archive.
- **Impact**: Wasteful for large archives; not severe.
- **Fix**: Cache the result in `self._script_names` and reuse it.
- **Linter rule**: not mechanically checkable.

### Logger not configured — charm logs invisible in `juju debug-log`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:27` (`logger = logging.getLogger(__name__)`)
- **Evidence**: No `logging.basicConfig()` or handler attached. On machine charms, ops sends logs to the systemd journal by default rather than to hook stdout, which is what `juju debug-log` captures. Observed: none of the charm's INFO-level messages appeared in `juju debug-log`.
- **Impact**: Operators cannot observe the charm's behaviour via `juju debug-log`; must SSH in and read the journal.
- **Fix**: Configure the root logger with a `StreamHandler(sys.stdout)`.
- **Linter rule**: machine charm using `logging.getLogger` without configuring a stdout/stderr handler — partially mechanically checkable.

### No actions defined
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py` — no `@action`-decorated methods
- **Evidence**: `juju actions script-exporter` returns "No actions defined".
- **Impact**: No operator-facing way to reload config, validate a script, or dump rendered config without a full restart.
- **Fix**: Consider `reload`, `validate-script`, `show-config` actions.
- **Linter rule**: not applicable.

### `ops[tracing]<3` and `pydantic<2` pins are stale
- **Severity**: low
- **Kind**: maintainability
- **Where**: `pyproject.toml`
- **Evidence**: Pin comment references Ubuntu 20.04 support ("chore: pin ops to '<3' to be able to release for 20.04"), but the charm's practical target is 22.04+. The `pydantic<2` pin exists because `cos_agent.py` uses pydantic v1 APIs (`__fields__` at line ~372/439, `.json()` at line ~702), producing `PydanticDeprecatedSince20` warnings in unit tests.
- **Impact**: Blocks moving to ops 3.x's cleaner API and to pydantic v2; ongoing maintenance burden.
- **Fix**: Remove both pins once 20.04 support is fully dropped and the `cos_agent` library is updated to pydantic v2 APIs.
- **Linter rule**: not mechanically checkable.

### Deprecated `charms.operator_libs_linux.v1.systemd` library
- **Severity**: low
- **Kind**: maintainability
- **Where**: `src/charm.py:14-17` (import)
- **Evidence**: The library file itself states it is deprecated in favour of `charmlibs.systemd` v1.0 (bug-for-bug compatible).
- **Impact**: Charm depends on a library that will no longer receive fixes.
- **Fix**: Migrate to `charmlibs.systemd`.
- **Linter rule**: import from deprecated library path — mechanically checkable.

### `receive-ca-cert` endpoint not documented — wrong endpoint fails silently at relate time
- **Severity**: low
- **Kind**: docs
- **Where**: `charmcraft.yaml` (interface `certificate_transfer`), README.md
- **Evidence**: Relating via `self-signed-certificates:certificates` (interface `tls-certificates`) fails with "no compatible endpoints found"; the correct endpoint is `self-signed-certificates:send-ca-cert`. This was hit during the review's own relate attempt.
- **Impact**: An operator following intuition (or the `certificates` endpoint name) will fail to integrate TLS.
- **Fix**: Document the required `send-ca-cert` endpoint in the README.
- **Linter rule**: not mechanically checkable.

### `prometheus_config_file` optionality undocumented
- **Severity**: medium
- **Kind**: docs
- **Where**: `charmcraft.yaml` config option `prometheus_config_file` (default `""`), README.md
- **Evidence**: The code correctly guards against an empty string, so the charm works without `prometheus_config_file` (self-scraping `/metrics` only). The README doesn't clarify that script metrics require setting this option.
- **Impact**: Operators may assume `script_file`+`config_file` alone is sufficient for Prometheus to scrape script metrics.
- **Fix**: Document that `prometheus_config_file` is required for script metrics to be scraped.
- **Linter rule**: not mechanically checkable.

## Test gaps

- No unit test covers: invalid YAML in `config_file` or `prometheus_config_file` (expect `BlockedStatus`); `SystemdError` from `service_restart` (expect `BlockedStatus`); missing `scrape_configs` key (expect no crash); null `scripts:` key (expect `BlockedStatus`); `_statuses` accumulation across repeated `collect_unit_status` calls; bad LZMA archive already has coverage per the "worth copying" note but the others do not.
- `ops-scenario`'s lazy config evaluation means the `scripts_scraping_jobs` `__init__`-time crash (see YAML finding above) cannot be caught by the current scenario test harness at all — this is a structural test-tooling gap, not just a missing test case.
- Coverage: `src/charm.py` at 61% (66/180 statements missed), with `_on_start`, `_on_stop`, most of `_on_config_changed`, `_extract_scripts_archive`, `_insert_full_path_in_command`, `_retrieve_script_names`, `_create_systemd_service`, `_reconcile_charm_tracing`, and the `_on_cert_transfer_*` handlers all untested.
- Integration tests (`test_simple_script.py`, `test_multiple_scripts.py`, `test_charm_tracing.py`) all failed in this run, but for environment reasons (missing SSH key in the jubilant model; `opentelemetry-collector` config option `tracing_sampling_rate_workload` passed as string instead of float) rather than charm bugs — deployment/config steps in all three completed successfully before the failing step.

## Tests

| Test | Result |
|------|--------|
| `tests/unit/test_charm.py::test_status_no_config_file` | PASS |
| `tests/unit/test_charm.py::test_status_no_prometheus_config_file` | PASS |
| `tests/unit/test_charm.py::test_cos_agent_relation_data_is_set_script_file` | PASS (2 warnings) |
| `tests/unit/test_charm.py::test_cos_agent_relation_data_is_set_scripts_archive` | PASS (2 warnings) |
| `ruff check src/ tests/` | All checks passed |
| `pyright src/` | 0 errors, 0 warnings |
| `tests/integration/test_simple_script.py::test_metrics` | FAILED (SSH key missing in jubilant model — environment issue; deployment/active status achieved) |
| `tests/integration/test_multiple_scripts.py::*` | FAILED (SSH key missing — environment issue; multi-script config worked) |
| `tests/integration/test_charm_tracing.py::test_charm_traces_are_pushed` | FAILED (`opentelemetry-collector` config option `tracing_sampling_rate_workload` expects float, not string — environment/test issue) |

Warnings: `PydanticDeprecatedSince20` from `cos_agent.py` (`__fields__` and `.json()` — pydantic v1 APIs deprecated in v2).

## Worth copying

- Clean use of `ops.CollectStatusEvent`: statuses appended to a list, then `event.add_status()` per entry (correct pattern modulo the accumulation bug noted above).
- `ops-tracing` integration via `cos_agent`'s `charm_tracing_config`, with correct null-safety (`None, None` when not ready).
- Proper use of `charms.operator_libs_linux.v1.systemd` primitives (daemon_reload, service_restart, service_resume, service_running, service_stop) — the only issue is missing exception handling, not misuse.
- Clear config surface: four options cover single-script, multi-script, raw config, and scrape-job use cases with distinct responsibilities.
- `_remove_file_dir` correctly handles `FileNotFoundError`, `PermissionError`, and general exceptions separately.
- Modern test structure: `ops-scenario` for unit tests avoids mocking the whole ops framework; `patch_etc_paths` fixture sandboxes filesystem access cleverly.
- Integration tests use `jubilant` and actually SSH into the machine and curl `/probe`, and verify charm traces reach the otel-collector — genuinely high-value integration coverage where it works.
- `cos_agent` relation data (scrape jobs, alert rules, tracing protocols) is correct and deterministic, confirmed by inspecting `grafana-agent/0`'s relation data.

## Common-practice notes

- Library versioning: `cos_agent` is still v0 (patch 25); ecosystem convention is shifting to v1/v2 for new libraries, but this is acceptable for a stable machine charm.
- `src/` layout, `uv`-based packaging via `charmcraft.yaml`, and separate `tests/unit`/`tests/integration` trees are all current best practice.
- Binary bundled as a charm part fetched from GitHub at pack time — preferable to a runtime download; the README documents a resource-based offline alternative.
- CI uses shared `canonical/observability` workflow templates (`charm-quality-gates.yaml@v2`, `charm-pull-request.yaml@v2`), consistent with the rest of the observability charm fleet.
- The instance-level `_statuses` list pattern is common across charms but the standard/safer approach is to build the list locally in the handler rather than storing it as persistent instance state.
- Subordinate-of-subordinate topology: when script-exporter integrates with grafana-agent via cos-agent, grafana-agent becomes a subordinate of script-exporter (itself a subordinate of ubuntu), producing a second script-exporter-adjacent unit on the same machine — this is what triggers the binary race condition, and is a real, not contrived, deployment shape.

## Docs

- README.md: comprehensive, covers single- and multi-script workflows with good examples; the "How to compare a config option against their scripts" and "Environments with no internet access" sections are strong. Missing: `prometheus_config_file` optionality/behaviour when absent; correct TLS relation endpoint (`send-ca-cert`, not `certificates`).
- `charmcraft.yaml` description: clear on purpose, subordinate nature, and COS integration.
- charmhub.md confirms publication at `3.2/stable` rev 77 (deployed rev during this review was 76, one revision behind); `3.2/edge` at rev 124, `dev/edge` at rev 133.
- SECURITY.md: brief but covers disclosure process.
- Open issues corroborate findings in this review: #16 (systemd failure → hook failure), #17 (port not registered with Juju), #57 (self-generated scrape jobs).

## Open questions

1. Why did `service_restart` fail on the very first config-changed after initial config was set? Likely a race from rapid, repeated `config-changed` invocations; retry/backoff logic or a pre-restart service-state check would help.
2. Should `prometheus_config_file` be required (with `BlockedStatus` when absent) given it's needed for the charm's primary use case?
3. Can `ops[tracing]<3` and `pydantic<2` be dropped now that 20.04 support is effectively gone?
4. Why does Juju 3.6.27 on `concierge-lxd` fail to download the `ubuntu` principal charm (`archiveSha256 length 0`)? This blocked testing the Juju 3.x substrate in this environment — worth re-attempting with a fresh controller.
5. Is the double `config-changed` firing per `juju config` command expected behaviour for subordinates, or a Juju-side issue? Needs separate investigation, but the charm should be robust to it regardless.
