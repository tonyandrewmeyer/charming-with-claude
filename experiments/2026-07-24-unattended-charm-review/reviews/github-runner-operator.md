# github-runner-operator

Machine charm that manages self-hosted GitHub Actions runners on OpenStack VMs. Each unit spawns a configurable pool of OpenStack VMs, registers them with GitHub, and reconciles the pool against desired state — either a fixed pool (`base-virtual-machines`) or a planner-driven reactive pool. The charm is a thin wrapper: all real work is delegated to the vendored `github-runner-manager` Python package, which runs as a per-unit systemd service (`github-runner-manager@{unit}.service`) exposing a Flask HTTP API on localhost.

**Verdict**: Well-structured charm with strong config-validation UX and a sophisticated pressure reconciler, but shipping with a critical defect: `@catch_charm_errors` does not catch `RunnerManagerServiceNotReadyError`, so any handler reaching `flush_runner()` while the manager service is down will block for ~2 minutes and then crash the hook. The same 120-second blind wait makes `check-runners`/`flush-runners` actions painfully slow to fail with an unhelpful message. COS integration is half-wired by accident of library defaults (Loki alert rules and dashboards work only because the library's default paths happen to match the charm's directory layout; Prometheus alert rules do not exist at all, and two of three dashboards depend on Loki log scraping the charm never configures). A confirmed security issue: `charm_state.json`, containing credentials, is written world-readable in the charm's working directory. A maintainer should fix the `@catch_charm_errors` exception coverage and the `wait_till_ready()` blind wait first — together they are the single most operator-visible problem — then address `charm_state.json` permissions.

| | |
|---|---|
| Repo | canonical/github-runner-operator @ `72f6e11c1` (rev702, 2026-07-16) |
| Charms | github-runner (machine) |
| Substrate | machine (LXD) |
| Deployed | yes — concierge-lxd-4 (Juju 4.0.12): `juju deploy github-runner --channel=stable` then `juju refresh --channel=latest/edge` (rev697 → rev706). Local HEAD is rev702, so code review findings target rev702/697 and may not exactly match rev706. |
| Reviewed | 2026-08-27 |

## What it does

> **Deployed vs. local revision**: The initially deployed charm was `latest/stable` rev **697** (`73a21a08e`), not rev696 as an earlier pass of this review stated. Local HEAD is `72f6e11c1`, tagged rev702 — five revisions ahead of stable, including: rev698 (stop tracking plaintext `openstack-clouds-yaml`), rev699 (collapse config-changed flush detection), rev700 (integration test with Juju secrets), rev701 (GitHub App auth), rev702 (check image readiness before starting service, fix stop cleanup). Findings below apply to rev702 unless marked otherwise; rev697 behaviour was directly observed during deployment.

Key responsibilities:
- **Install hook**: apt-get install run-one/pip/venv, create `runner-manager` OS user, pipx install `github-runner-manager`, set up logrotate
- **Service**: per-unit systemd service running the Flask HTTP API
- **Reconcile**: pressure reconciler (fixed pool or planner-driven) manages VM creation/deletion
- **Integrations**: `image` (image-builder), `planner` (AMQP-based job scheduling), `cos-agent` (metrics), `debug-ssh` (tmate)
- **Actions**: `check-runners` (runner info), `flush-runners` (destroy all VMs and re-create)
- **Auth**: PAT or GitHub App authentication

## Deployment log

### Deploy (rv-github-runner-4)
```
juju deploy github-runner --channel=stable --model rv-github-runner-4
# Machine bootstrap: ~9 minutes (cloud-init apt dist-upgrade on Noble base)
# Install hook: ~3 minutes (apt install + pipx install of github-runner-manager)
# Start hook: blocked "Please provide image integration."
```

### `juju refresh` — stable to edge (rev697→706, concierge-lxd-4)
```
juju refresh --channel=latest/edge github-runner --model rv-github-runner
# Download started at 01:58:19, completed ~02:00:55
# upgrade-charm hook: started 02:00:55, completed 02:01:14 (~19s)
# pipx reinstall: github-runner-manager package
# config-changed fired after upgrade (01:57:48 for pre-refresh unit, 02:01:15 post-refresh)
# After refresh: status "Invalid Github config, Missing path configuration" (config left over from earlier test)
# Rev 706 confirmed via manifest.yaml: charmcraft-version 4.3.1 (vs 4.2.1 pre-refresh)
```

### `juju add-unit` github-runner
```
juju add-unit github-runner --model rv-github-runner
# Machine 1 provisioned in ~3 min
# Install hook ran: apt install + pipx install
# Unit blocked "Please provide image integration."
# No port conflict between units — each gets a distinct port via ensure_http_port_for_unit()
```

### COS integration (grafana-agent, machine subordinate)
```
juju deploy grafana-agent --channel=stable --model rv-github-runner
juju integrate github-runner:cos-agent grafana-agent:cos-agent
# Both grafana-agent units went ERROR: "hook failed: cos-agent-relation-joined"
# grafana-agent log: "subordinate relation should have exactly one unit"
# Triggered because github-runner had 2 units at the time
# Resolved by removing grafana-agent; integration tests use opentelemetry-collector instead
```

### `juju remove-application` while blocked
```
# Model rv-github-runner-4: charm blocked on "Invalid Github config"
juju destroy-model rv-github-runner-4 --force --no-wait
# Succeeded in ~30 seconds. Stop hook ran, completed cleanly.
# Reason: ConfigurationError is caught by @catch_charm_errors before flush_runner() is ever reached.

# Model rv-github-runner-3: charm blocked on "Missing OpenStack config"
# Stop hook hung ~120s, failed, retried.
# Reason: different blocked state took a different code path (unconfirmed which — possibly
# service was partially started when stop fired; see Findings).
```

### Relation test (debug-ssh)
```
juju deploy tmate-ssh-server --channel=stable --model rv-github-runner-4
juju integrate github-runner:debug-ssh tmate-ssh-server:debug-ssh
# relation-created hook fired: completed cleanly
# tmate-ssh-server bootstrapping: charm remained blocked on image integration
juju remove-relation github-runner tmate-ssh-server
# relation-broken: no handler defined, default no-op, completed cleanly
# Charm still blocked on image integration — no crash, no retry loop
```

## Observed behaviour

### `check-runners` / `flush-runners` action timing (measured)
`juju run github-runner/0 check-runners --wait=5m` while charm is blocked:
- Actions fail with `"Failed runner manager request: GitHub runner manager service not ready"`, correctly surfaced via `event.fail()` (`@catch_action_errors`).
- LXC log inspection (definitive timing): `check-runners` started 01:42:15, failed 01:44:15 — exactly **2 minutes** (8×15s `wait_till_ready()` loop, then a fast final failure). `flush-runners` showed the identical 01:42:15–01:44:15 window.
- An earlier estimate of 4–5 minutes for these actions was wrong; corrected to ~2 minutes based on the LXC log.
- `juju run --wait=1m flush-runners` hits the CLI's 60s timeout before the action completes — the CLI wait must be set ≥3 minutes to observe the actual result.

### COS integration — what IS and IS NOT wired
`COSAgentProvider` is instantiated with `scrape_configs` only (`src/charm.py:208-220`); everything else falls back to library defaults:
```python
self._cos_agent = COSAgentProvider(
    self,
    scrape_configs=[{
        "job_name": "github-runner",
        "metrics_path": "/metrics",
        "static_configs": [{"targets": ["localhost:"f"{manager_service.ensure_http_port_for_unit(...)}"]}],
    }],
    # metrics_rules_dir uses library default "./src/prometheus_alert_rules" → directory does not exist
    # logs_rules_dir uses library default "./src/loki_alert_rules" → directory exists
    # dashboard_dirs uses library default ["./src/grafana_dashboards"] → directory exists
)
```
- **Metrics**: `localhost:<port>/metrics` — Prometheus scrape, correctly structured.
- **Loki alert rules**: ARE wired (library default happens to match `src/loki_alert_rules/`). Confirmed by LXC inspection of the deployed unit: `ls /var/lib/juju/agents/unit-github-runner-0/charm/src/loki_alert_rules/` → `capacity.rules failure.rules`.
- **Prometheus alert rules**: NOT wired — no `src/prometheus_alert_rules/` directory exists.
- **Dashboards**: ARE wired (library default matches `src/grafana_dashboards/`). `metrics_prometheus.json` works (Prometheus queries). `metrics.json` and `metrics_longterm.json` query Loki for `/var/log/github-runner-metrics.log` — Loki log scraping is not configured by this charm's `COSAgentProvider` (only Prometheus scrape configs are provided), so those two dashboards show no data.
- **Trace**: not wired (no `tracing_protocols`).
- **grafana-agent crash**: the machine subordinate crashes when github-runner has more than one unit (`ValueError: subordinate relation should have exactly one unit`); this is a bug in the grafana-agent charm, not github-runner. Integration tests use `opentelemetry-collector` (rev149, `2/candidate`) instead.

### Timing summary
| Operation | Duration |
|---|---|
| Machine bootstrap | ~9 min (cloud-init apt dist-upgrade) |
| Install hook | ~3 min (apt + pipx) |
| Hook execution (post-install) | <1s |
| `check-runners` (blocked) | ~2 min (8×15s wait; LXC log 01:42:15–01:44:15) |
| `flush-runners` (blocked) | ~2 min (same wait loop; LXC log 01:42:15–01:44:15) |
| `juju run --wait=1m flush-runners` | CLI 60s timeout hit before action completed |
| `juju refresh` (stable→edge, 697→706) | Download ~40s; `upgrade-charm` hook ~19s (pipx reinstall); total ~2 min |
| `juju remove-application` (blocked on ConfigurationError) | <30s (hook exits cleanly) |

### Hook counts (unit 0, rv-github-runner-4)
| Hook | Trigger | Duration |
|---|---|---|
| install | initial deploy | ~3 min |
| leader-elected | first start | <1s |
| config-changed | after leader-elected | <1s |
| start | after config-changed | <1s (blocked: image) |
| debug-ssh-relation-created | tmate integration | <1s (completed cleanly) |
| debug-ssh-relation-broken | remove relation | <1s (no-op) |
| upgrade-charm | juju refresh | ~30s |

### Failure injection

| Scenario | Observed | Recovery |
|---|---|---|
| `check-runners` while blocked | ~2 min hang, fails with "Failed runner manager request: GitHub runner manager service not ready" | Operator must resolve config |
| `flush-runners` while blocked | ~2 min hang, same failure message | Operator must resolve config |
| `reconcile-interval=abc` | "expected int, got 'abc'" — rejected by CLI, never reaches the charm | Set to valid int |
| `openstack-clouds-yaml=invalid_yaml` | Charm blocked "Invalid Github config, Missing path configuration" (cascaded from missing GitHub path, not from the YAML itself) | Set valid YAML |
| Secret with wrong key | "missing github-token" error | Update secret content |
| Secret with correct key | Status advances correctly | N/A |
| `juju remove-application` while blocked on `ConfigurationError` | Completes in <30s — hook exits cleanly | N/A |
| `juju remove-application` while blocked on `ImageIntegrationMissingError` | Not retested; expected to hang 120s then fail based on code path | Unknown (unverified) |
| Remove debug-ssh relation while blocked | Completes cleanly, no hook handler defined | N/A |
| `juju refresh` stable→edge (697→706) | Downloaded rev706, `upgrade-charm` hook ran ~19s (pipx install + deps), `config-changed` fired after | N/A |
| `juju refresh` while blocked | `upgrade-charm` completed cleanly (deps reinstalled); `@catch_charm_errors` caught `ConfigurationError` → blocked status retained | N/A |
| Scale up: `add-unit` github-runner | Machine bootstrapped ~3 min, install hook ran, unit blocked "Please provide image integration" | N/A |
| COS integration (grafana-agent) with 2 units | Both grafana-agent units went `error`, `hook failed: "cos-agent-relation-joined"` — `ValueError: subordinate relation should have exactly one unit` | Use `opentelemetry-collector` instead |
| COS integration (grafana-agent) removing relation | `cos-agent-relation-departed`/`-broken` hooks fired cleanly | N/A |

### Failure injection not tested
- **Killing the workload process**: SSH access was available via `lxc exec`, but the service was never running while the charm was blocked, so there was nothing to kill.
- **Adding image/planner integration while blocked**: no provider charms available in this environment.
- **Scale down**: `juju remove-unit` requires interactive confirmation (`Continue [y/N]?`); could not be scripted.
- **`juju remove-unit` while action running**: the `flush-runners` action was executing when the model was force-destroyed; the action's outcome was lost, not observed cleanly.

## Findings

Findings are ordered by severity (critical → high → medium → low → nit/info).

### `@catch_charm_errors` does not catch `RunnerManagerServiceNotReadyError`
- **Severity**: critical
- **Kind**: bug | ux
- **Where**: `src/charm.py:119-159`
- **Evidence**: The decorator catches `ConfigurationError`, `TokenError`, `ImageIntegrationMissingError`, `ImageNotFoundError` — but not `RunnerManagerServiceNotReadyError` (raised by `wait_till_ready()`). All handlers that call `flush_runner()`/`check_runner()` — `_on_stop`, `_on_upgrade_charm`, `_on_debug_ssh_relation_changed`, `_on_image_relation_changed`, `_on_planner_relation_changed`, `_on_secret_changed` — are correctly decorated with `@catch_charm_errors` (confirmed by reading the code at rev697 and rev702; an earlier pass of this review wrongly claimed these handlers were undecorated), but the decorator's exception coverage doesn't include the one exception `flush_runner()` actually raises when the service is down.
- **Impact**: Any handler that reaches `flush_runner()` while the manager service is not running blocks for ~2 minutes and then crashes the hook rather than degrading gracefully. Confirmed applicable to `_on_stop`, `_on_upgrade_charm`, and the relation-changed handlers whenever the charm is active but the service is unavailable.
- **Fix**: Add `except RunnerManagerServiceNotReadyError` handling to `@catch_charm_errors` (e.g. set `WaitingStatus("Runner manager service not ready")` and return), or guard `flush_runner()` calls with a `systemd.service_running()` check first.
- **Linter rule**: not mechanically checkable ("decorator catches ConfigurationError but not RunnerManagerServiceNotReadyError when both can be raised by the same handler").

### `charm_state.json` written world-readable, contains credentials (confirmed on live unit)
- **Severity**: high
- **Kind**: security
- **Where**: `src/charm_state.py:40, 969`
- **Evidence**: `CharmState._store_state()` writes `charm_state.json` to the charm's working directory on every `from_charm()` call. Contents include `proxy_config`, `runner_proxy_config`, `charm_config`, `runner_config`, and `ssh_debug_connections` — any of which may hold GitHub tokens or OpenStack credentials. No `chmod`/`fchmod` call precedes the write. Existing files in the charm directory on the deployed unit have permissions `0o644` (world-readable). The file did not exist on the tested blocked unit because `from_charm()` never fully succeeded there — but the code path and permissions are confirmed by source inspection and the observed default permissions of adjacent files.
- **Impact**: Any local process, even unprivileged, can read GitHub tokens and OpenStack credentials from disk once the charm reaches active status.
- **Fix**: Write to a restricted-permission location (e.g. under `/var/lib/juju/agents/unit-{unit}/charm/`) with mode `0o600`, or move this state into Juju secret storage.
- **Linter rule**: mechanically checkable — flag `Path.write_text`/`open().write` of data containing known credential fields without a preceding `chmod`/`fchmod`/`os.open` with restrictive mode.

### grafana-agent machine subordinate crashes with a multi-unit github-runner
- **Severity**: high
- **Kind**: bug (dependency)
- **Where**: grafana-agent machine charm (rev 827, `0.44/stable`), triggered via github-runner's `cos-agent` relation
- **Evidence**: After `juju integrate github-runner:cos-agent grafana-agent:cos-agent` with 2 github-runner units, both grafana-agent units went `error`: `hook failed: "cos-agent-relation-joined"`, log `ValueError: unexpected error: subordinate relation <ops.model.Relation cos-agent:1> should have exactly one unit`.
- **Impact**: COS integration via `grafana-agent` is unusable for a multi-unit github-runner deployment on machine substrate.
- **Fix**: Not fixable from this charm's side — bug lives in grafana-agent. Workaround: use `opentelemetry-collector` (as the project's own integration tests do), or document the incompatibility.
- **Linter rule**: not applicable (bug is in a dependency charm).

### `wait_till_ready()` creates a hardcoded blind wait in actions and handlers
- **Severity**: high
- **Kind**: performance | ux
- **Where**: `src/manager_client.py:169-181`
- **Evidence**: `wait_till_ready()` loops 8 times, sleeping 15s between calls to `health_check()`, before raising `RunnerManagerServiceNotReadyError`. Measured end-to-end: `check-runners`/`flush-runners` while blocked both take exactly 2 minutes (LXC log 01:42:15–01:44:15) to fail. There is no status pre-check that would short-circuit the wait when the charm is already known to be blocked.
- **Impact**: Every action and every handler calling `flush_runner()` while the service is down pays this fixed 2-minute cost, with an error message ("service not ready") that adds no information the operator doesn't already have from the charm's status.
- **Fix**: Add a pre-flight check: if the charm is not in `ActiveStatus`, raise `RunnerManagerServiceNotReadyError` immediately using the current status.
- **Linter rule**: mechanically checkable — "function named `wait_till_ready`/similar has a hardcoded retry loop with no status pre-flight check".

### COS integration wiring depends silently on library defaults
- **Severity**: medium
- **Kind**: bug | missing-feature
- **Where**: `src/charm.py:208-220`
- **Evidence**: `COSAgentProvider` is instantiated passing only `scrape_configs`. The library's default `logs_rules_dir="./src/loki_alert_rules"` and `dashboard_dirs=["./src/grafana_dashboards"]` happen to match directories that exist in this repo, so Loki alert rules (`capacity.rules`, `failure.rules`) and all three dashboards are sent to the cos-agent relation — confirmed by LXC filesystem inspection of the deployed unit. `metrics_rules_dir` defaults to `./src/prometheus_alert_rules`, which does not exist, so no Prometheus alert rules are shipped at all.
- **Impact**: The wiring "works" for Loki rules and dashboards purely by coincidence of directory naming, which is fragile and easy to break by a future refactor (e.g. renaming `src/loki_alert_rules/`). Prometheus alert rules are simply missing.
- **Fix**: Pass `logs_rules_dir` and `dashboard_dirs` explicitly to make the intent visible in code. Create `src/prometheus_alert_rules/` if Prometheus alert rules are wanted.
- **Linter rule**: mechanically checkable — "`COSAgentProvider` instantiated without `metrics_rules_dir`/`logs_rules_dir`/`dashboard_dirs` when matching rule/dashboard directories exist on disk".

### Loki-backed dashboards non-functional without separate Loki log scraping
- **Severity**: medium
- **Kind**: bug | missing-feature
- **Where**: `src/charm.py:208-220`; `src/grafana_dashboards/metrics.json`, `metrics_longterm.json`
- **Evidence**: `metrics.json` and `metrics_longterm.json` query Loki for `/var/log/github-runner-metrics.log`. `COSAgentProvider` here only supplies `scrape_configs` for Prometheus (`/metrics`); it does not configure Loki log scraping. Only `metrics_prometheus.json` (which queries Prometheus) will show data with the charm's current setup.
- **Impact**: Two of the three shipped dashboards display no data unless the operator separately sets up Loki log scraping of that file — undocumented in the charm.
- **Fix**: Either configure Loki log scraping via the library (`log_endpoints`), or rework those dashboards to use Prometheus metrics, or document the extra requirement.
- **Linter rule**: mechanically checkable — "dashboard JSON with `datasource: loki` shipped alongside a `COSAgentProvider` that provides no log scraping config".

### `StoredState` persists plaintext GitHub token
- **Severity**: medium
- **Kind**: security
- **Where**: `src/charm.py:245-253`
- **Evidence**: `_stored.set_default(token=self.config[TOKEN_CONFIG_NAME], ...)` persists the token config value to `.unit-state.db`. Comment at lines 211-216 acknowledges the same risk for `openstack-clouds-yaml` but does not extend the concern to `token`.
- **Impact**: Token recoverable from disk if the machine is compromised, even when `token-secret-id` is otherwise used to avoid a plaintext config value.
- **Fix**: Don't track `token` in `StoredState` for change detection; compare `self.config.get()` directly in `_on_config_changed`.
- **Linter rule**: mechanically checkable — "known secret config name passed to `_stored.set_default`".

### `flush_runner()` HTTP POST has no short client-side timeout
- **Severity**: medium
- **Kind**: performance | bug
- **Where**: `src/manager_client.py:142-145`
- **Evidence**: `flush_runner()` uses `timeout=WRITE_TIMEOUT` where `WRITE_TIMEOUT = 20*60 = 1200s`. If the manager service is unresponsive (rather than simply down), the caller can block up to 20 minutes after already waiting 120s in `wait_till_ready()`. In testing, `flush-runners` while blocked exceeded the external 5-minute action timeout.
- **Impact**: Worst case operator wait time for a stuck action approaches ~20 minutes.
- **Fix**: Use a much shorter client-side timeout (e.g. 30s), catching `requests.Timeout` and raising `RunnerManagerServiceConnectionError` promptly.
- **Linter rule**: mechanically checkable — "HTTP call using a multi-minute timeout constant with no shorter fallback".

### Actions do not check charm status before calling the manager service
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:395-416`
- **Evidence**: `_on_check_runners_action`/`_on_flush_runners_action` call the manager client without first checking `self.unit.status`. `@catch_action_errors` correctly calls `event.fail()` once `RunnerManagerServiceError` propagates, but only after the full 120s wait.
- **Impact**: An operator running `check-runners` against a blocked charm waits ~2 minutes for a failure the charm's own status already explained.
- **Fix**: Check `self.unit.status` at the top of each action handler; if not `ActiveStatus`, `event.fail(str(self.unit.status))` and return immediately.
- **Linter rule**: not mechanically checkable.

### `wait_till_ready()`/`health_check()` have zero unit test coverage
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/manager_client.py:169-181`; `tests/unit/test_manager_client.py`
- **Evidence**: The unit test file mocks `client.wait_till_ready = MagicMock()` and contains no test exercising the real retry/timeout logic. Coverage report shows `manager_client.py` at 68%. The `catch_charm_errors` unit test (`test_catch_charm_errors`) only covers `ConfigurationError`, `TokenError`, `ImageIntegrationMissingError`, `ImageNotFoundError` — not `RunnerManagerServiceNotReadyError`.
- **Impact**: The exact hang duration discovered by this review (2 minutes, not the 4-5 initially assumed) was only discoverable through manual testing; no automated test would catch a regression here.
- **Fix**: Add unit tests for `wait_till_ready()` with a mocked `health_check()` covering the 8-retry loop and the final raise, plus a `catch_charm_errors` test for `RunnerManagerServiceNotReadyError`.
- **Linter rule**: not mechanically checkable.

### `_apt_install` does not check the exit code of `apt-get update`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:492-506`
- **Evidence**:
  ```python
  def _apt_install(self, packages: Sequence[str]) -> None:
      execute_command(["/usr/bin/apt-get", "update"])  # no exit code check
      _, exit_code = execute_command(
          ["/usr/bin/apt-get", "install", "-qy"] + list(packages), check_exit=False
      )
  ```
- **Impact**: A failed `apt-get update` (network/mirror issue) leaves the subsequent install to fail with a confusing, secondary error.
- **Fix**: Check the exit code of `apt-get update` and raise `SubprocessError` on failure.
- **Linter rule**: mechanically checkable — "subprocess call without exit-code check".

### `juju remove-application` during a running action leaves the action's outcome unrecorded
- **Severity**: low
- **Kind**: ux
- **Where**: model rv-github-runner (concierge-lxd-4)
- **Evidence**: While `flush-runners` was executing, `juju remove-application` (with `--force`) was run. `juju status` showed the unit `executing (flush-runners)` and the action never reached a terminal state before the agent was torn down.
- **Impact**: An operator who removes an application while an action is running loses the action's result silently.
- **Fix**: Document that applications should not be removed while actions are in-flight, or require `juju cancel-action` first.
- **Linter rule**: not mechanically checkable.

### Dead code: `lib/charms/data_platform_libs/v0/data_interfaces.py` (5782 lines)
- **Severity**: low
- **Kind**: test-gap
- **Where**: `lib/charms/data_platform_libs/v0/data_interfaces.py`
- **Evidence**: `grep -r "data_interfaces\|DatabaseRequires" src/` returns no matches — the file is never imported.
- **Impact**: 5782 lines of unused bundled library code, increasing charm size and obscuring what is actually used.
- **Fix**: Remove the file, or document why it's kept.
- **Linter rule**: mechanically checkable — "bundled library file with no imports anywhere in `src/`".

### Unparenthesized implicit string concatenation in COS scrape config
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:216-218`
- **Evidence**:
  ```python
  "targets": [
      "localhost:"
      f"{manager_service.ensure_http_port_for_unit(self.unit.name)}"
  ]
  ```
- **Fix**: Add a comma between the two string literals.
- **Linter rule**: ISC004 (ruff) — implicit string concatenation in a single line.

### Unused `noqa` directives (5 instances)
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:138, 178, 642`; `src/charm_state.py:160, 974`
- **Evidence**: `# noqa: D417` / `# noqa: C901` on rules not enabled in this project's ruff config.
- **Fix**: Remove the unused `noqa` comments.
- **Linter rule**: RUF100 (ruff) — unused noqa directive.

### Root logger used instead of module logger
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:442, 504`; `github-runner-manager/src/github_runner_manager/cli.py:50, 122`; `github-runner-manager/src/github_runner_manager/platform/github_provider.py:263`
- **Evidence**: `logging.warning(...)`/`logging.exception(...)` called on the root logger.
- **Fix**: Use the module-level `logger`.
- **Linter rule**: LOG015 (ruff) — root logger usage detected.

### Mutable class attribute in `AnyHttpsUrl`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/models.py:19`
- **Evidence**: `allowed_schemes = {"https"}` is a mutable set class attribute.
- **Fix**: Annotate with `typing.ClassVar` or make it an instance attribute.
- **Linter rule**: RUF012 (ruff) — mutable default value for class attribute.

### `typing` imports that should be `collections.abc`
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:22` (`Callable`, `Sequence`); `src/manager_client.py:11` (`Callable`); `src/utilities.py:10` (`Sequence`)
- **Fix**: Import from `collections.abc` instead of `typing`.
- **Linter rule**: UP035 (ruff).

### Explicit conversion flag needed (auto-fixable)
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:187`; `src/charm_state.py:507-602` (18 instances)
- **Fix**: `ruff check --fix`.
- **Linter rule**: RUF010 (ruff).

### `_on_stop` and relation handlers were misdiagnosed as undecorated in an earlier draft — corrected
- **Severity**: info (retraction)
- **Kind**: accuracy
- **Where**: `src/charm.py:481, 508, 518, 529, 539`
- **Evidence**: `_on_stop` and the debug-ssh/image/planner relation handlers are all decorated with `@catch_charm_errors` in both rev697 (deployed) and rev702 (HEAD), confirmed by reading `charm.py` at both revisions. An earlier draft of this review claimed these handlers lacked the decorator; that was wrong. The real bug is the decorator's incomplete exception coverage (see the critical finding above), not a missing decorator.

## Worth copying

### Step-by-step status progression
The charm advances `BlockedStatus` messages through each required configuration item in turn — path → token → OpenStack config → image integration → active. Each `ConfigurationError` maps to a specific, actionable message. Worth adopting broadly.

### `catch_charm_errors` decorator pattern
`src/charm.py:118-165` — a clean decorator mapping domain exceptions to Juju statuses, with a separate `catch_action_errors` variant that also calls `event.fail()`. The pattern is sound even though its exception coverage is currently incomplete (see findings).

### Port allocation with file locking
`src/manager_service.py:40-102` — per-unit HTTP port allocation using `fcntl.flock`, deterministic base port from unit index, bounded scan on collision, persisted and reused across restarts. Covered by `tests/integration/test_multi_unit_same_machine.py`, which verifies distinct ports and persistence.

### Pressure reconciler design
`github-runner-manager/src/github_runner_manager/manager/pressure_reconciler.py` — uses an in-memory runner count rather than calling `get_runners()` on every pressure event; docstring explains the fire-and-forget trade-off and natural backoff via the reconcile loop. The `_create_paused` flag avoids tight loops on repeated zero-ID creation results. Handles partial failures well.

### Explicit config file permissions
`src/manager_service.py:363-366` — writes the config file via `os.O_WRONLY | os.O_CREAT | os.O_TRUNC` with `os.fchmod(fd, 0o600)` applied before writing credentials, so the file is never briefly world-readable. Worth contrasting with `charm_state.json`, which gets this wrong.

### `_flush_on_change_config_to_stored` tracking
`src/charm.py:88-106` — explicit tracking of which config keys trigger a runner flush, with a comment explaining why `openstack-clouds-yaml` is deliberately excluded.

### Comprehensive metric instrumentation
`github-runner-manager/src/github_runner_manager/metrics/` — Prometheus gauges for busy/idle/expected runners, reconciliation duration histograms, deletion counts, wired via `COSAgentProvider`.

### Graceful shutdown with signal handling
`github-runner-manager/src/github_runner_manager/cli.py:27-43` — handles SIGTERM/SIGINT, joins reconciler threads with a 60s timeout before exiting.

### Integration test for co-located units
`tests/integration/test_multi_unit_same_machine.py` — verifies two units on the same machine get distinct HTTP ports, services stay active, metrics respond, and ports persist across restarts.

## Common-practice notes

### Follows convention
- `lib/charms/` with `operator_libs_linux` and `grafana_agent` — standard.
- `src/` charm code, `github-runner-manager/src/` bundled package — standard split.
- Idiomatic `ops` usage: `CharmBase`, `StoredState`, `HookEvent`.
- Config via `charmcraft.yaml` `config: options:`.
- Pydantic models for config validation (`CharmConfig`, `OpenstackRunnerConfig`, etc.).
- systemd management via `charms.operator_libs_linux.v1.systemd`.
- tox-based testing across unit/integration/static/lint environments.

### Drifts from convention
- **Bundled Python package as the real logic**: `github-runner-manager/` is installed via `pipx --global`; the charm itself is a thin wrapper. Unusual compared to most fully self-contained charms.
- **`StoredState` for config-change tracking** rather than the config-changed event's own comparison mechanism — functional but less idiomatic.
- **Flask HTTP API as IPC**: the charm talks to the manager service over localhost HTTP rather than direct subprocess calls, which is the direct cause of the 120-second wait-loop failure mode above.
- **Machine charm on LXD containers**: base is Ubuntu 24.04 Noble with a cloud-init `apt-get dist-upgrade`, adding several minutes to bootstrap.

## Tests

### Unit tests
- `tests/unit/test_charm.py` (837 lines) — `ops.testing.Harness`-based; mocks `manager_service`, `execute_command`, `systemd`. Covers install, upgrade, config-changed, start, stop, secret-changed, relation events, action errors, error mapping.
- `tests/unit/test_charm_state.py` — `CharmConfig`, `GithubConfig`, `OpenstackRunnerConfig`, `OpenstackImage`, `CharmState`, proxy config parsing.
- `tests/unit/test_manager_service.py` — service setup, port allocation, cleanup, install.
- `tests/unit/test_manager_client.py` — HTTP client error handling.
- `tests/unit/test_logrotate.py`, `test_utilities.py`, `test_factories.py` — additional coverage.

**Result**: `tox -e unit` → 214 passed, 42 warnings (Harness `PendingDeprecationWarning`), 1.34–1.53s. Overall coverage 88%.

Coverage gaps:
- `manager_client.py`: 68% — `wait_till_ready()` and `_request()` uncovered (deferred to integration tests, per an inline comment "Issuing request will be tested in integration tests")
- `charm.py`: 82% — action-handler branches, `_apt_install`, `StoredState` branches
- `manager_service.py`: 85% — service start/stop branches

**Notable gap**: `test_on_stop_busy_flush_and_cleanup_service` mocks `_manager_client` entirely, so `wait_till_ready()` is never actually exercised — the failure path where stop fires while the service is down is not tested. `test_catch_charm_errors` only covers `ConfigurationError`, `TokenError`, `ImageIntegrationMissingError`, `ImageNotFoundError` — not `RunnerManagerServiceNotReadyError`.

### Integration tests
`tests/integration/` uses `jubilant`. Requires OpenStack credentials, GitHub PAT/App credentials, and a pre-built charm artifact. Key suites: `test_charm_runner.py` (837 lines: check/flush runners, workflow dispatch), `test_charm_upgrade.py` (108 lines), `test_prometheus_metrics.py` (220 lines, full COS integration with k8s prometheus+grafana+traefik), `test_multi_unit_same_machine.py` (88 lines), `test_charm_no_runner.py`, `test_e2e.py`. **Could not be run** in this review environment — no live OpenStack, no GitHub credentials.

### Lint and static analysis
| Tool | Result |
|---|---|
| `mypy` | Success: no issues found in 34 source files |
| `pylint` | 10.00/10 |
| `black --check` | All files properly formatted |
| `isort --check-only` | All files properly sorted |
| `pflake8` | All pass |
| `pydocstyle` | All pass |
| `codespell` | All pass |
| `bandit` | No issues found |
| `ruff` | 33 issues in `src/`, ~100 in `github-runner-manager/src/` |

Ruff breakdown in `src/` (33 total): 15× RUF010 (explicit conversion flag), 5× RUF100 (unused noqa), 3× UP035 (`collections.abc`), 2× UP007 (`X | Y` annotations), 1× UP045 (`X | None`), 1× UP034 (extraneous parens), 1× RUF015 (`next(iter(...))`), 1× RUF012 (mutable class attr), 1× ISC004 (implicit concat). 28 of 33 auto-fixable with `ruff check --fix`.

## Docs

### README.md
Comprehensive, with a mermaid ecosystem diagram (github-runner, image-builder, planner, webhook-gateway, rabbitmq, postgresql, tmate-ssh-server, COS), a clear get-started section, and a link to ADR 001 on the pressure reconciler design.

### `docs/`
Good structure: `docs/how-to/`, `docs/reference/`, `docs/explanation/`, `docs/adr/`. How-to guides for custom labels, path changes, token management, COS integration, SSH debug, troubleshooting.

### charmcraft.yaml description
Matches the Charmhub description; includes worked examples for `pre-job-script` and `manager-ssh-proxy-command`.

### Terraform module
`terraform/charm/` (per-charm) and `terraform/product/` (full stack, including image-builder) appear well-structured but were not exercised in this review.

## Open questions

1. Why does `charm_state.json` exist as a flat file rather than using Juju secret storage, given it holds GitHub tokens and OpenStack passwords?
2. Why doesn't `@catch_charm_errors` catch `RunnerManagerServiceNotReadyError`, given the decorator otherwise covers the domain's other error types?
3. Why doesn't `wait_till_ready()` accept a configurable/shorter timeout, or a pre-flight status check?
4. What is the migration path when a `StoredState` key is removed from the code — does an old value silently persist via `set_default()`'s "only if absent" semantics?
5. Is it intentional that Loki alert rules and dashboards are wired only via library-default path matching, while Prometheus alert rules have no directory at all?
6. What is `lib/charms/data_platform_libs/v0/data_interfaces.py` for, given it is never imported?
7. Are operators expected to configure Loki log scraping separately for the two dashboards that depend on it, and if so, where is that documented?
8. Is the `grafana-agent` machine charm actually supported for multi-unit github-runner deployments, given the observed crash?
9. Does using `localhost:<port>` in the COS `scrape_configs` assume the COS agent is always co-located on the same machine? Would it break with a differently-placed subordinate?
10. Why does `_on_image_relation_joined` write credentials to `relation.data[self.unit]` rather than `relation.data[self.app]`?
