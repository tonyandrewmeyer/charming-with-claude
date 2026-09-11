# grafana-agent

Grafana Agent is a mature, widely-deployed subordinate machine charm for the Canonical Observability Stack (COS Lite). It installs the `grafana-agent` snap and relays metrics, logs, and traces from principal charms (via `juju-info`/`cos-agent`) to Prometheus, Loki, Tempo and/or Grafana Cloud. The codebase is well-architected — a clean base/derived split (`GrafanaAgentCharm` / `GrafanaAgentMachineCharm`), a centralized `CompoundStatus` pattern, and the clearest mandatory-relation UX in the ecosystem — but it has a critical operational defect: every config-changed event calls `snap.set()` unconditionally, which restarts the workload even when nothing relevant changed, and on Juju 4.x can crash the hook outright. Combined with no `update-status` health check (charm reports `active` while the agent process is dead — issue `#367`) and silent acceptance of invalid duration config, this charm needs the snap-set/restart coupling fixed before it can be recommended without caveats. A maintainer's first move should be caching snap config state so `snap.set()` is only called when the value actually changes, and wrapping that call so a snapd failure degrades to `BlockedStatus` instead of crashing the hook. The charm is scheduled for end-of-life at the end of 2026, with `opentelemetry-collector` as the suggested successor.

| | |
|---|---|
| Repo | `canonical/grafana-agent-operator` @ `4ad98c8` (2026-07-14) |
| Charms | grafana-agent |
| Substrate | machine |
| Deployed | yes — concierge-lxd (juju 3.6.23): 2/stable rev 848, dev/edge rev 857; concierge-lxd-4 (juju 4.0.5): 2/stable rev 848 |
| Reviewed | 2026-08-01 |

## What it does

Grafana Agent is a subordinate machine charm that installs the `grafana-agent` snap, pinned to specific revisions in `snap_management.py`. It builds `/etc/grafana-agent.yaml` from:

- **Metrics**: node_exporter self-monitoring, scrape jobs from `cos-agent` relations, remote-write to Prometheus via `send-remote-write` or `grafana-cloud-config`, plus its own alert rules from `src/prometheus_alert_rules/`.
- **Logs**: `/var/log` scraping, journald scraping, and snap-plug log paths from `cos-agent` relations, forwarded to Loki via `logging-consumer` or `grafana-cloud-config`.
- **Traces**: OTLP, Jaeger, Zipkin receivers, configurable via `always_enable_*` flags or `cos-agent` relation data, forwarded to Tempo via `tracing`.
- **Dashboards**: node-exporter dashboard plus dashboards from `cos-agent`, forwarded via `grafana-dashboards-provider`.
- **TLS**: certificates from `certificates` (tls-certificates) or `receive-ca-cert` (certificate_transfer) relations.

It enforces mandatory relation pairs (e.g. `juju-info` must be paired with `send-remote-write`, `logging-consumer`, or `grafana-cloud-config`) and blocks with a clear message when they are missing.

## Deployment log

### 2/stable (rev 848, snap grafana-agent 0.40.4 rev 95) on Juju 3.6

```sh
juju deploy ubuntu --base ubuntu@24.04 principal
juju deploy grafana-agent --channel 2/stable
juju deploy grafana-cloud-integrator --channel 1/stable gci
juju integrate principal grafana-agent
juju integrate grafana-agent gci
```

- Install time: 3min 14s (snap download dominant)
- Active message: empty (no Loki/Prometheus endpoints configured)

### 2/stable (rev 848) on Juju 4.x

```sh
juju deploy ubuntu --base ubuntu@24.04 principal4 -m rv-gagent-4
juju deploy grafana-agent --channel 2/stable -m rv-gagent-4
juju integrate principal4 grafana-agent
```

- Install time: ~3min 45s
- Status: blocked `"Missing ['grafana-cloud-config']|['logging-consumer']|['send-remote-write'] for juju-info"` — same as 3.6

### dev/edge (rev 857, snap grafana-agent 0.44.6 rev 143)

```sh
juju deploy ubuntu --base ubuntu@24.04 principal2
juju deploy grafana-agent --channel dev/edge
juju integrate principal2 grafana-agent
```

- Install time: ~3min 14s
- Status: blocked with the same clear, actionable message

### Config change — bad value

```
juju config grafana-agent log_level=invalid
→ blocked: "log_level must be one of ['debug', 'info', 'warn', 'error']"
juju config grafana-agent log_level=info
→ active (recovers)
```

### Config change — unrelated restart (critical)

```
juju config grafana-agent extra_alert_labels='test=value'
# /etc/grafana-agent.yaml md5 unchanged (733caba3...)
# BUT systemd service restarted (ActiveEnterTimestamp advanced)
```

Root cause confirmed: `snap set grafana-agent reporting-enabled=0` always restarts the grafana-agent service, even when the value is unchanged. Two consecutive identical `snap set` commands produced two restarts. The charm calls `snap.set()` from within `_verify_snap_track()` on every `config-changed` event.

### Kill workload

```
sudo kill -9 $(pgrep agent)
→ snap systemd auto-restarted the process
→ charm stayed active/idle throughout
```

### Trash config file

```
echo "garbage: {" > /etc/grafana-agent.yaml
systemctl restart snap.grafana-agent.grafana-agent.service
→ service inactive (config parse error)
→ charm stayed active/idle
juju config grafana-agent log_level=warn   # triggers _update_config
→ service recovered to active
```

### Remove/re-add required relation

```
juju remove-relation grafana-agent gci
→ blocked: "Missing ['grafana-cloud-config']|['logging-consumer']|['send-remote-write'] for juju-info"
juju integrate grafana-agent gci
→ active (recovers)
```

### TLS integration with self-signed-certificates (Juju 3.6)

```sh
juju deploy self-signed-certificates --channel latest/stable
juju integrate grafana-agent:certificates self-signed-certificates:certificates
```

- TLS cert/key/CA files appeared at `/tmp/agent/grafana-agent.{pem,key}` and `/var/snap/grafana-agent/common/`
- `/etc/grafana-agent.yaml` included `server.http_tls_config` and `server.grpc_tls_config`
- Removing the relation properly cleaned up all cert files

### Config change — invalid `global_scrape_timeout` (Juju 3.6)

```
juju config grafana-agent global_scrape_timeout=invalid
→ no validation error, config accepted silently
→ snap.grafana-agent.grafana-agent service became inactive (agent failed to parse config)
→ charm still reported blocked (for mandatory relations) — did NOT detect the agent was dead
juju config grafana-agent global_scrape_timeout=10s
→ recovers
```

### Config change — invalid `global_scrape_timeout` (Juju 4.x)

```
juju config grafana-agent global_scrape_timeout=invalid
→ config-changed hook CRASHED with GrafanaAgentInstallError
→ root cause: snap.set() raised SnapError: "snap change 'configure-snap' id 18 failed with status Error"
→ hook retried 3 times; 3rd attempt succeeded
juju config grafana-agent global_scrape_timeout=10s
→ recovers
```

### Refresh from 2/stable (rev 848) to dev/edge (rev 857)

```
juju refresh grafana-agent --channel dev/edge
→ upgrade-charm hook ran _install() → snap refreshed from rev 95 to rev 142/143
→ snap install took ~90s
→ charm came up blocked (same message) — refresh succeeded
```

### Juju 4.x: `grafana-cloud-config` relation not detected for mandatory check

```sh
juju deploy grafana-cloud-integrator --channel 2/edge gci
juju integrate grafana-agent:grafana-cloud-config gci:grafana-cloud-config
```

- gci came up blocked ("No outputs configured" — no cloud credentials)
- grafana-agent stayed blocked with `"Missing ['grafana-cloud-config']|['logging-consumer']|['send-remote-write']"`
- The relation is visible in `juju status --relations` but the charm does not recognize it for the mandatory check
- `juju config grafana-agent log_level=debug` (forcing config-changed) did not unblock it
- Juju 4.x-specific — on 3.6 the same pattern works correctly

## Observed behaviour

- **Snap revision pinning**: `snap_management.py:38-46` hardcodes revisions per `(confinement, arch)`. Deployed 2/stable used rev 95 (agent 0.40.4); local HEAD maps to rev 140-147 (agent 0.44.6). Each new agent release requires a charm update to the pin table.
- **Snap is held**: `snap.hold()` prevents auto-refresh — correct for a pinned-revision strategy.
- **Config comparison before restart**: `_update_config()` (`grafana_agent.py:614-622`) compares old/new yaml and only restarts on a real diff — good, but undermined by the separate snap-config path (see Findings).
- **Agent version detection**: `agent_version_output()` (`charm.py:412`) runs `/bin/agent -version`, but that path doesn't exist on the snap (checked against 0.44.6); the method appears untested in live deployment.
- **Memory**: ~56MB RSS for the agent process on a minimal deploy.
- **No actions defined.**
- **Copy-paste error message in `stop()`**: `charm.py:431` says `"Failed to restart grafana-agent"` but the method stops the service. Only observable by reading code.
- **Active status reported when process is dead**: confirms open issue `#367` — charm reports `active/idle` even when `snap.grafana-agent.grafana-agent.service` is inactive. `_is_installed` (`charm.py:449`) only checks `self.snap.present`, not whether the service is running.
- **No `update-status` health monitoring**: a dead agent goes undetected until the next relation or config event.
- **Hook cascade**: a single `config-changed` event triggers 3+ `_update_config()` calls (via `_on_config_changed`, a Loki event, and a COS event), each doing full config generation, comparison, and possible restart.
- **Juju 4.x hook crash from `snap.set()`**: on Juju 4.0.5, `snap.set({"reporting-enabled": "0"})` can fail with `SnapError: snap change 'configure-snap' id N failed with status Error`, thrown from `_verify_snap_track()` (`src/charm.py:268`) as an unhandled `GrafanaAgentInstallError` that crashes the hook. It eventually succeeds on retry, but the unit sits in `error` state in the meantime. On Juju 3.6.23 the same call succeeds (still restarting the agent).
- **Invalid config values silently accepted**: `global_scrape_timeout=invalid` and `global_scrape_interval=0` are accepted with no validation, written straight into `/etc/grafana-agent.yaml`, and cause the agent to fail to parse the file and go inactive — undetected by the charm. Only `log_level` is validated.
- **TLS cert cleanup works correctly**: removing the `certificates` relation triggers `_update_config()` to detect `cert.enabled == False` and delete all six cert/key files via `_delete_file_if_exists()`.
- **Refresh correctly triggers snap upgrade**: `juju refresh` from 2/stable (rev 848) to dev/edge (rev 857) correctly ran `_on_upgrade_charm` → `_install()` → `install_ga_snap()`, moving the snap from rev 95 to 142/143.

## Findings

### Every snap config change restarts the workload, including no-op changes
- **Severity**: critical (high on Juju 3.6, critical on Juju 4.x where it also crashes the hook)
- **Kind**: performance / ux / bug
- **Where**: `src/charm.py:265` (`_verify_snap_track`) → `src/snap_management.py:58` (`_install_snap`) → `snap.set(config)` at line 89
- **Evidence**: `snap set grafana-agent reporting-enabled=0` restarts the service even when the value is already 0; two consecutive identical `snap set` calls produced two restarts. `_verify_snap_track()` is called on every `config-changed` event and from `_connect_logging_snap_endpoints()`, both feeding `install_ga_snap()` a `config={"reporting-enabled": ...}` dict. Setting `extra_alert_labels='test=value'` (which does not touch the yaml at all — md5 unchanged) still caused a restart because `_verify_snap_track()` called `snap.set()`. On Juju 4.x this call can additionally raise `SnapError`, propagating uncaught through `_verify_snap_track()` → `GrafanaAgentInstallError` → crashed `config-changed` hook.
- **Impact**: on Juju 3.6, any config change restarts the agent, causing gaps in metric/log/trace collection. On Juju 4.x it also crashes the hook, putting the unit in error state and forcing retries. In fleets with many units, a rolling config change can restart or error-loop them all.
- **Fix**: cache the last-set snap config values and only call `snap.set()` when they differ (or check `snap.get(...)` first). Wrap `_verify_snap_track()` in try/except in the event handlers and set `BlockedStatus` on `GrafanaAgentInstallError` instead of crashing.
- **Linter rule**: "charm calls `snap.set()` without checking if value changed" — mechanically checkable via static analysis of the snap-config path.

### Active status reported when Grafana Agent process is dead
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:449` (`_is_installed`); no service-health handler exists
- **Evidence**: after writing garbage to `/etc/grafana-agent.yaml` and restarting the snap service (which failed to start), the charm continued reporting `active/idle`. `_is_installed` only checks `self.snap.present`. No `update-status` handler checks service health. Matches open issue `#367`, open since 2026-01-26.
- **Impact**: operators see `active/idle` and believe the agent is healthy when it is not.
- **Fix**: add an `update-status` handler that checks `snap.services["grafana-agent"]["active"]` (or subscribes to snap service-status events) and sets `BlockedStatus` when the service isn't running.
- **Linter rule**: "charm reports active status without verifying workload health" — not generally mechanically checkable, but a linter could flag the absence of an `update-status` handler in a charm that deploys a workload.

### `config-changed` hook crashes on Juju 4.x when `snap.set()` fails
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:268` (`_verify_snap_track`); `GrafanaAgentInstallError` uncaught in `_on_config_changed` (`src/grafana_agent.py:311`)
- **Evidence**: on Juju 4.0.5, `juju config grafana-agent global_scrape_timeout=invalid` crashed the hook:
  ```
  File "src/snap_management.py", line 85, in _install_snap
      snap.set(config)
  SnapError: snap change 'configure-snap' id 18 failed with status Error
  ...
  File "src/charm.py", line 268, in _verify_snap_track
      raise GrafanaAgentInstallError("Failed to refresh grafana-agent.") from e
  ```
  No try/except exists in `_on_config_changed`. On Juju 3.6.23 the same operation succeeds silently (though the agent still restarts).
- **Impact**: `config-changed` is the most frequently-triggered hook. A transient `snap.set()` failure (snapd load, configure-hook timeout) puts the unit in `error` state, blocks other hooks, and forces Juju to retry — each retry re-attempts `snap.set()`, risking a retry storm.
- **Fix**: wrap `_verify_snap_track()` in try/except in all handlers that call it (`_on_config_changed`, `_connect_logging_snap_endpoints`, `_on_upgrade_charm`); catch `GrafanaAgentInstallError` and set `BlockedStatus` instead of re-raising.
- **Linter rule**: "unhandled exception path from `snap.set()` through `_verify_snap_track()` to event handler" — mechanically checkable by tracing exception propagation from snap-library calls.

### `_on_cert_transfer_removed` does not update CA certificates or restart the agent
- **Severity**: high
- **Kind**: bug
- **Where**: `src/grafana_agent.py:335-340`
- **Evidence**: the method deletes cert files from disk but does not call `self.run(["update-ca-certificates", "--fresh"])` or `self.restart()`. Compare `_on_cert_transfer_available` (lines 326-331), which does call both. After the `receive-ca-cert` relation is removed, the old CA remains in the system trust store and the agent process continues to trust it.
- **Impact**: if a CA is rotated or revoked via `receive-ca-cert`, grafana-agent keeps trusting the old CA until the next unrelated config rebuild — a security gap.
- **Fix**: after deleting cert files, call `self.run(["update-ca-certificates", "--fresh"])` and `self.restart()`.
- **Linter rule**: "event handler for removed/departed relation does not undo side effects from the joined/created handler" — mechanically checkable by comparing paired event handlers.

### `_on_cloud_config_revoked` does not clean up the CA file or refresh CA certificates
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/grafana_agent.py:321-322`
- **Evidence**: the method only calls `self._update_config()`. It does not delete `self._cloud_ca_path` (written by `_on_cloud_config_available` at line 316) or run `update-ca-certificates`. Compare `_on_cloud_config_available` (lines 313-318), which writes the CA file and runs the refresh.
- **Impact**: removing a `grafana-cloud-config` relation leaves the stale cloud CA on disk and in the trust store.
- **Fix**: add `self._delete_file_if_exists(self._cloud_ca_path)` and `self.run(["update-ca-certificates", "--fresh"])` before `self._update_config()`.
- **Linter rule**: same as above — "paired available/revoked handlers should undo side effects".

### No validation for `global_scrape_timeout` and `global_scrape_interval`
- **Severity**: medium
- **Kind**: ux / bug
- **Where**: `charmcraft.yaml` (config definition); `src/grafana_agent.py:774-775` (values passed straight into the config dict)
- **Evidence**: `global_scrape_timeout=invalid` was accepted silently, written into `/etc/grafana-agent.yaml`, and caused grafana-agent to fail parsing the config at startup and go `inactive`. The charm gave no error — it stayed blocked only because of the mandatory-relation check, an unrelated message. Only `log_level` is validated (`src/grafana_agent.py:882-889`).
- **Impact**: a trivially wrong config value silently breaks the agent, and the charm's status hides the real cause.
- **Fix**: validate time-duration fields (regex or parse function) and reject invalid values with `BlockedStatus`. Extend to other string-typed fields interpolated into YAML (`classic_snap`, `tls_insecure_skip_verify`, `tracing_sample_rate_*`, etc.).
- **Linter rule**: "config options with `type: string` interpolated into structured output without validation" — mechanically checkable.

### `run()` and `agent_version_output()` do not check subprocess return codes
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:446` (`run()`); `src/charm.py:388` (`agent_version_output()`)
- **Evidence**: `run()` calls `subprocess.run(cmd)` without `check=True`, so failures are silently ignored — this affects `_on_cert_transfer_available` (line 329), `_on_cloud_config_available` (line 319), and `_update_ca` (line 955), all of which call `self.run(["update-ca-certificates", "--fresh"])`. `agent_version_output()` similarly omits `check=True`; a failed call returns an empty string. Additionally, `/bin/agent` does not exist on the current snap (0.44.6) — the binary lives at `/snap/grafana-agent/current/agent`.
- **Impact**: a failed `update-ca-certificates` call goes unnoticed, potentially leaving TLS verification broken with no diagnostic signal.
- **Fix**: add `check=True` to `subprocess.run` calls and handle `CalledProcessError`.
- **Linter rule**: "`subprocess.run` without `check=True`" — mechanically checkable.

### Unnecessary cascade of config regeneration on each hook
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/grafana_agent.py:282` (`_on_config_changed`) triggers downstream Loki and COS events that each call `_update_config()`
- **Evidence**: a single `config-changed` hook in the dev/edge deployment triggered 3+ `_update_config()` calls (visible via `_on_config_changed` → `LokiPushApiEndpointJoined` → `COSAgentDataChanged`), each regenerating the full config dict and doing a yaml comparison.
- **Impact**: wasteful CPU/I/O on every hook; should update config once per hook.
- **Fix**: debounce or dirty-flag `_update_config()` calls within a single hook execution.
- **Linter rule**: not mechanically checkable.

### Pinned snap revision approach is deprecated
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/snap_management.py:38-46`
- **Evidence**: the revision map keys `(confinement, arch)` to hardcoded numbers, requiring a charm release for every grafana-agent snap update. Open issue `#31` requests a `snap_channel` config option. Deployed 2/stable uses rev 95 (agent 0.40.4) while local HEAD maps to rev 140-147 (agent 0.44.6).
- **Impact**: maintenance burden; growing gap between charm releases and available agent versions.
- **Fix**: add a `snap_channel` config option per `#31`, falling back to the pinned revision for determinism.
- **Linter rule**: not mechanically checkable.

### Test failures: 3 tests fail due to missing `update-ca-certificates`
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_cert_transfer.py:49`, `tests/unit/test_cloud_integration.py:54`
- **Evidence**: `tox -e unit` reports 79 pass, 3 fail, 2 skip. All 3 failures are `FileNotFoundError: update-ca-certificates` from `grafana_agent.py:324` and `grafana_agent.py:335`, where `self.run(["update-ca-certificates", "--fresh"])` isn't mocked by the test harness.
- **Impact**: cert-transfer and cloud-integration logic aren't actually validated by CI; regressions could slip through.
- **Fix**: mock `self.run` in the harness, or use `scenario`'s `State` with appropriate mocking.
- **Linter rule**: not mechanically checkable.

### `stop()` reports the wrong error message
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:431`
- **Evidence**: `raise GrafanaAgentServiceError("Failed to restart grafana-agent") from e` inside `stop()` (which calls `self.snap.stop()`).
- **Impact**: misleading debug output when stop fails.
- **Fix**: change the message to `"Failed to stop grafana-agent"`.
- **Linter rule**: "copy-paste error detection in except blocks" — mechanically checkable by comparing method name against error text.

### Shell injection in `_evaluate_log_paths`
- **Severity**: low (mitigated by charm trust model)
- **Kind**: bug
- **Where**: `src/charm.py:578`
- **Evidence**: the method runs `echo 'echo {path}' | snap run --shell {snap}.{app}` with `shell=True` to resolve environment variables in log paths. The code acknowledges the risk in a comment: "There is a potential for shell injection here. It seems okay because the potential attacking charm has root access on the machine already anyway."
- **Impact**: the trust-model argument is reasonable today, but this remains a code smell that could become exploitable if the trust assumption changes.
- **Fix**: use `snap run --shell` with explicit arguments, or `os.path.expandvars` instead of shell evaluation.
- **Linter rule**: "`subprocess` with `shell=True` and interpolated strings" — mechanically checkable.

### `agent_version_output()` uses a path that's wrong on the current snap
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:412`
- **Evidence**: runs `subprocess.run(["/bin/agent", "-version"], ...)`. On the dev/edge deployment (snap rev 143), `/bin/agent` doesn't exist — the binary is at `/snap/grafana-agent/current/agent`.
- **Impact**: `_agent_version` would silently return `None`, affecting any logic depending on version detection (appears currently unused, unverified).
- **Fix**: use the snap path or `snap run grafana-agent agent -version`.
- **Linter rule**: not mechanically checkable (requires deployment).

### `_enhance_endpoints_with_tls` mutates endpoint dicts in place
- **Severity**: low
- **Kind**: performance / ux
- **Where**: `src/grafana_agent.py:649-652`
- **Evidence**: the method sets `endpoint["tls_config"] = {...}` directly on dicts from the iterated `endpoints` collection. Currently idempotent (same key assigned each call), but if those dict objects are shared/reused references across calls, this is a latent bug.
- **Impact**: could compound into a real bug if the method's mutation logic becomes non-idempotent.
- **Fix**: copy endpoint dicts before modifying, or build new dicts via comprehension.
- **Linter rule**: not mechanically checkable.

### `CONTRIBUTING.md` is outdated (references a k8s charm that no longer exists in this repo)
- **Severity**: low
- **Kind**: docs
- **Where**: `CONTRIBUTING.md:48`
- **Evidence**: describes building the k8s charm with `tox -e render-k8s` and deploying `grafana-agent-k8s_ubuntu-20.04-amd64.charm`; this repo only contains the machine charm.
- **Impact**: confuses new contributors.
- **Fix**: update to describe the machine-charm workflow and remove k8s references.
- **Linter rule**: not mechanically checkable.

### `GrafanaAgentCharm` cannot be instantiated directly — undocumented
- **Severity**: low
- **Kind**: ux
- **Where**: `src/grafana_agent.py:193` (`__new__`)
- **Evidence**: `__new__` raises `TypeError` if the class is `GrafanaAgentCharm` directly — a clean pattern, but not mentioned in the class docstring.
- **Impact**: minor discoverability gap; design itself is sound.
- **Fix**: document in the class docstring that it is an abstract base and cannot be instantiated directly.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **`CompoundStatus` pattern** (`src/grafana_agent.py:182-187`): a `@dataclass CompoundStatus` acts as a shared struct for status fields; `_update_status()` (lines 400-438) resolves them in priority order, avoiding status races between event handlers.
- **`MandatoryRelationPairs` with OR-ed outgoing relations** (`src/charm.py:170-178`): maps incoming relations to sets of acceptable outgoing relation sets with OR semantics, and via `cosl.MandatoryRelationPairs.get_missing_as_str()` produces clear blocked messages like `"Missing ['grafana-cloud-config']|['logging-consumer']|['send-remote-write'] for juju-info"` — the clearest mandatory-relation UX seen in the ecosystem.
- **Config comparison before restart** (`src/grafana_agent.py:614-622`): compares `yaml.safe_load(old)` with `yaml.dump(new)` and only restarts on a real diff — most charms restart unconditionally.
- **Base/derived class split**: `GrafanaAgentCharm` (abstract base) vs `GrafanaAgentMachineCharm` (machine implementation) is clean multi-substrate architecture, with `NotImplementedError` and clear messages on all abstract methods.
- **`__new__` guard against direct instantiation** (`src/grafana_agent.py:193-195`): simpler than `abc.ABC` for ops-framework charms that need an abstract base class.

## Common-practice notes

- **`charmcraft.yaml` as single metadata source**: no separate `metadata.yaml`/`config.yaml` — follows current convention.
- **Snap-based deployment**: standard for machine charms; the pinned-revision approach is less common than channel-based deployment.
- **Library versions**: open issue `#92` tracks upgrading `cert_handler` (v0→v1) and `tls_certificates` (v2→v4) — known technical debt.
- **Empty `.gitkeep` files**: `src/loki_alert_rules/.gitkeep` (genuinely empty dir) vs `src/prometheus_alert_rules/*.rules` (populated) — slightly unusual but harmless.
- **No `update-status` handler**: uncommon gap relative to ecosystem norms; means workload failures go undetected during idle periods.
- **`justfile` / `tox.ini`**: standard, clean, well-commented project layout.

## Tests

- 82 unit tests: 79 pass, 3 fail (`test_cert_transfer` and `test_cloud_integration` — both due to missing `update-ca-certificates` in the test environment), 2 skipped (snap-endpoint scrape configs).
- Lint: `ruff check` passes.
- Test mix: both `ops.testing.Harness` (older, deprecation-warned) and `scenario` (newer) — migration is partial.
- Integration tests exist under `tests/integration/` but are not run (would need a full COS deployment).
- Coverage gaps: `_on_start`, `_on_stop`, `_on_remove`; `_evaluate_log_paths` (the shell-injection path); `_snap_plugs_logging_configs`; `_connect_logging_snap_endpoints`; the upgrade-charm flow; classic vs strict snap confinement switching.

## Docs

- **README.md**: brief but functional, includes an EOL warning pointing to `opentelemetry-collector`. The "OCI Images" section is a copy-paste artifact from the k8s charm and doesn't apply here.
- **INTEGRATING.md**: comprehensive (11KB), covers deployment scenarios, relation usage, and troubleshooting — well above average.
- **CONTRIBUTING.md**: outdated, references the k8s charm (see Findings).
- **Charmhub description**: accurate and current.
- **Charm docs link**: `https://discourse.charmhub.io/t/grafana-agent-docs-index/13452` — valid.

## Open questions

1. Should the charm work around the grafana-agent snap's configure-hook behavior of restarting on any `snap set` (even identical values), by caching config state — or should the snap itself be fixed?
2. What's the plan for the `snap_channel` config option requested in `#31` (open since 2026-02-19), given the growing gap between pinned charm revisions and available agent versions?
3. `tests/manual/smoke/` contains `amd64.yaml`/`arm64.yaml` spread configs listed in inventory but not run by tox, and undocumented invocation.
4. Does `agent_version_output()` work in production at all — does the 2/stable snap (rev 95, agent 0.40.4) even have the binary at `/bin/agent`? The method appears unused in the main charm flow.
5. Why does the mandatory-relation check fail to recognize an established `grafana-cloud-config` relation on Juju 4.x specifically, when `juju status --relations` shows it but `juju show-unit` does not list it under `relation-info`? Possibly a Juju 4.x subordinate-charm relation-visibility change worth filing upstream.
