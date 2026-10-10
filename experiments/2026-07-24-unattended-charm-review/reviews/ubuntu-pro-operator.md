# ubuntu-pro-operator

A machine-subordinate charm that enables Ubuntu Pro subscriptions on a principal charm via the `ubuntu-pro-client` (`pro`) CLI. Four build targets share code in `src/`: `ubuntu-advantage` (bases 16.04–22.04), `ubuntu-advantage_noble`, `ubuntu-pro`, and `ubuntu-pro_noble`.

The code has reasonable structure and test coverage (45 unit tests passing, 80% line coverage on `src/charm.py`), but the deployed charm is fragile: any one of four unrelated config options (`contract_url`, `override-http-proxy`, `override-https-proxy`, `ppa`) can crash the unit into Juju error state via an uncaught `subprocess.CalledProcessError`, and there is no `update_status` handler or action to self-heal or recover without SSH access. The published `ubuntu-advantage` charm on `noble/edge` (rev 143) is also months behind `main` — it is missing a critical token-leak fix and three config options that exist in source. A maintainer should first: (1) release the token-leak fix to charmhub, (2) wrap every `subprocess.check_call`/`apt.add_package` in the config-changed path with exception handling that sets `BlockedStatus` instead of crashing, and (3) add an `update_status` handler and/or a manual retry action so operators aren't required to SSH into the machine to recover.

| | |
|---|---|
| Repo | canonical/ubuntu-pro-operator @ 80b53d2 (2026-04-06) |
| Charms | ubuntu-pro (bases 16.04–22.04), ubuntu-pro_noble, ubuntu-advantage, ubuntu-advantage_noble |
| Substrate | machine (LXD) |
| Deployed | yes — `concierge-lxd-4`, `ubuntu-advantage` from `noble/edge` channel, rev 143 |
| Reviewed | 2026-09-02 |

## What it does

A subordinate that relates to any principal charm via `juju-info`. On every `config-changed` hook it:

1. Installs `ubuntu-advantage-tools` (once, via `apt.add_package`) or a configured custom PPA.
2. Configures proxy, SSL cert, contract URL, security URL, apt-news URL, and vulnerability-data URL via the `pro config` CLI or by editing `/etc/ubuntu-advantage/uaclient.conf`.
3. Handles livepatch on-prem server/token (snap install + `canonical-livepatch` CLI).
4. Attaches or detaches the Ubuntu Pro subscription using the configured token.
5. Reports `ActiveStatus` with the list of enabled services, or `BlockedStatus` with an error message.

## Deployment log

```
# Model rv-ubuntu-pro on concierge-lxd-4 (Juju 4.0.12)
juju deploy ubuntu                                   # rev 79 on ubuntu@24.04
juju deploy ubuntu-advantage --channel noble/edge     # rev 143
juju integrate ubuntu ubuntu-advantage
# Machine provisioned in ~3 minutes
# Subordinate went to "No token configured" (blocked) — correct

# === FAILURE INJECTION 1: bad token ===
juju config ubuntu-advantage token=invalid-token-xyz
# Result: blocked, token appears in status AND unit log — CONFIRMED BUG (issue #17)

# === FAILURE INJECTION 2: bad contract_url ===
juju config ubuntu-advantage contract_url="not-a-url"
# Result: charm goes to ERROR state (hook failed), not BlockedStatus
# Cannot recover with config changes alone — required manual fix + juju resolve
# Root cause: uncaught CalledProcessError in _configure_ua_proxy
# Debug log timestamp: 04:17:51

# === FAILURE INJECTION 3: bad override-http-proxy ===
juju config ubuntu-advantage override-http-proxy="not-a-url"
# Result: SAME error-state crash as bad contract_url
# CalledProcessError: pro config set http_proxy=not-a-url returned exit status 1
# Recovery: required SSH + manual ua config unset + juju resolve
# Debug log timestamps: 04:28:17, 04:28:23, 04:28:33

# === FAILURE INJECTION 4: bad override-https-proxy ===
juju config ubuntu-advantage override-https-proxy="http://bad-proxy"
# Result: SAME error-state crash
# CalledProcessError: pro config set https_proxy=http://bad-proxy returned exit status 1
# Recovery: same as above (SSH + manual fix + juju resolve)
# Debug log timestamp: 04:31:13

# === FAILURE INJECTION 5: invalid PPA ===
juju config ubuntu-advantage ppa="ppa:totally-invalid/ppa-does-not-exist"
# Result: charm goes to ERROR state (hook failed)
# CalledProcessError: add-apt-repository ... returned non-zero exit status 1
# Debug log timestamps: 04:40:57 hook start, 04:41:01 hook failed
# KEY INSIGHT: PPA error auto-recovers on config change (see below)

# === FAILURE INJECTION 6: bad livepatch config ===
juju config ubuntu-advantage livepatch_server_url="https://livepatch.example.com" livepatch_token="bad-livepatch-token"
# Result: charm goes to BLOCKED (NOT error state) — correct behavior
# Debug log: 04:54:59 canonical-livepatch disable fails (no daemon), 04:55:00 enable fails
# Error message correctly shows in unit status
# Clearing config recovers correctly to "No token configured"

# === CONFIG CHANGES DON'T TRIGGER NEW HOOKS WHILE IN ERROR STATE (proxy/contract_url) ===
juju config ubuntu-advantage override-https-proxy=""
# Result: NO NEW HOOK FIRED. Unit kept retrying old failing hook every ~10s.
# Only manual fix on machine + juju resolve worked.

# === PPA RECOVERY IS DIFFERENT — AUTO-RECOVERS WITHOUT juju resolve ===
juju config ubuntu-advantage ppa=""
# Result: new hook fired after ~40s, unit recovered to "No token configured" blocked
# Debug log: 04:41:40 new hook, 04:41:43 completed successfully
# NO juju resolve needed. Why: remove_ppa("") succeeds (no-op), subsequent steps complete.

# === JUJU REFRESH BLOCKED BY BASE MISMATCH ===
juju refresh ubuntu-advantage --revision 148
# Result: ERROR cannot upgrade from single base "ubuntu@24.04" charm to
#         a charm supporting ["ubuntu@16.04" "ubuntu@18.04" "ubuntu@20.04" "ubuntu@22.04"].
# rev 148 is latest/edge for older bases; noble/edge is stuck at rev 144

# === SCALE UP: principal + subordinate ===
juju add-unit ubuntu --num-units 1
# Machine 1 provisioned in ~2 minutes
# New subordinate ubuntu-advantage/3 created on machine 1
# Both subordinates: "No token configured" (blocked) — correct
# Debug log: relation-created, relation-joined, relation-changed all fire for new unit

# === SCALE DOWN: subordinate removed — STOP HOOK FAILS ===
juju remove-unit ubuntu/1
# Debug log: 04:46:40 ERROR ops.model.ModelError: b'ERROR permission denied\n'
# Debug log: 04:46:40 ERROR hook "stop" (via hook dispatching script: dispatch) failed: exit status 1
# The charm has no stop handler; ops runs its default, which fails with permission denied
# Juju eventually removes the unit anyway

# === CONFIG GAP IN PUBLISHED CHARM ===
juju config ubuntu-advantage security_url="https://..."
# Result: ERROR invalid application config: unknown option "security_url"
juju config ubuntu-advantage apt_news_url="..."
# Result: ERROR invalid application config: unknown option "apt_news_url"
juju config ubuntu-advantage vulnerability_data_url_prefix="..."
# Result: ERROR invalid application config: unknown option "vulnerability_data_url_prefix"
# Published rev 143 has 9 options; source has 12. Missing: security_url, apt_news_url, vulnerability_data_url_prefix

# === NO ACTIONS DEFINED ===
juju actions ubuntu-advantage
# Result: "No actions defined for ubuntu-advantage."
# No way to manually trigger attach, detach, retry, or recovery without SSH

# === RELATION REMOVAL ===
juju remove-relation ubuntu ubuntu-advantage
# Result: juju-info-relation-departed fires, charm runs hook (no-op), unit removed
# UA subscription left on machine (no detach called)
# Re-integrate: new subordinate unit (ubuntu-advantage/1) spawned — confirmed

# === JUJU REMOVE-APPLICATION ===
juju remove-application --force ubuntu-advantage
# Result: subordinate removed cleanly; principal stays up
# UA subscription on machine persists (no cleanup)

# === RECOVERY FROM ERROR STATE (PPA case — automatic) ===
juju resolve ubuntu-advantage/2  # NOT NEEDED for PPA crash — auto-recovered via config change

# === RECOVERY FROM ERROR STATE (proxy/contract_url case — requires manual fix) ===
# After fixing contract_url in /etc/ubuntu-advantage/uaclient.conf manually via SSH:
juju resolve ubuntu-advantage/2
# Result: charm recovered to "No token configured" blocked — correct

# === juju resolve on a BLOCKED (non-error) unit ===
juju resolve ubuntu-advantage/2
# ERROR resolving unit: checking unit ... status: unit is not in error state
# Correct Juju behavior: resolve only works on error-state units, refused for blocked units
```

## Observed behaviour

**Token leak (critical, confirmed live)**
```
juju status → ubuntu-advantage/0*  blocked  idle  10.5.87.29
  Failed running command '['ubuntu-advantage', 'attach', 'invalid-token-xyz']' [exit status: 1].
```
Token `invalid-token-xyz` appears in both the workload status message and `juju debug-log`. Confirms GitHub issue #17. Deployed rev 143 passes the token directly as a positional arg; current HEAD (`80b53d2`) always uses `--attach-config` with a temp file, which hides it — but that fix has not been released.

**Bad `contract_url` → unhandled exception → error state (critical, confirmed live)**
```
unit-ubuntu-advantage-2: 04:17:51 ERROR juju.worker.uniter.operation
  hook "config-changed" (via hook dispatching script: dispatch) failed: exit status 1
subprocess.CalledProcessError: Command '['ubuntu-advantage', 'config', 'unset',
  'http_proxy']' returned non-zero exit status 1.
```
Originates in `_configure_ua_proxy` (`src/charm.py:416–428`, `subprocess.check_call`), not wrapped in any try/except.

**Bad proxy config → same crash (critical, confirmed live)**
`override-http-proxy="not-a-url"` and `override-https-proxy="http://bad-proxy"` trigger the identical crash. README acknowledges this failure mode but gives no recovery path.

**Invalid PPA → same crash (critical, confirmed live)**
```
CalledProcessError: Command '['add-apt-repository', '--yes',
  'ppa:totally-invalid/ppa-does-not-exist']' returned non-zero exit status 1.
```
Debug log: 04:40:57 hook start, 04:41:01 hook failed.

**Livepatch failure → BlockedStatus (confirmed live, correct behaviour)**
```
unit-ubuntu-advantage-2: 04:54:59 ERROR Error running canonical-livepatch disable:
  connection to the daemon failed: dial unix ... no such file or directory
unit-ubuntu-advantage-2: 04:55:00 ERROR Error running canonical-livepatch enable:
  failed to register client: ... lookup livepatch.example.com ... no such host
ubuntu-advantage  blocked  Failed running command '['canonical-livepatch', 'enable', 'bad-livepatch-token']' [exit status: 1].
```
Caught by the outer `try/except` in `_configure_livepatch` (`src/charm.py:395–398`), and `BlockedStatus` is set correctly. Clearing both config values recovers to "No token configured" blocked — no `juju resolve` needed. This is the one config-failure path that behaves correctly.

**Config changes don't retrigger hooks in error state — except for PPA (nuanced)**
After proxy/contract_url error state, `juju config ubuntu-advantage override-https-proxy=""` triggered no new hook; the unit re-ran the same failing hook every ~10s and required SSH + `juju resolve`. After PPA error state, the equivalent `ppa=""` did trigger a new hook (after ~40s) and the unit auto-recovered. Cause: clearing PPA lets `remove_ppa("")` succeed as a no-op and the rest of the hook completes; clearing proxy config still re-runs `_configure_ua_proxy`, which re-hits the same broken config file.

**`relation-departed`/`relation-broken` fire but do nothing (confirmed from debug log)**
```
INFO ... running juju-info-relation-departed hook for ubuntu/0
INFO ... ran "juju-info-relation-departed" hook
INFO ... running juju-info-relation-broken hook
INFO ... ran "juju-info-relation-broken" hook
```
Both complete successfully because there is no handler — ops runs the empty default. The UA subscription is left attached on the machine.

**`update_status` hook runs as a no-op** — debug log at 04:27:56/04:30:13 shows the hook firing with no error; no `self.framework.observe(self.on.update_status, ...)` is registered.

**Stop hook fails on subordinate unit removal (confirmed live)**
```
unit-ubuntu-advantage-3: 04:46:40 ERROR Uncaught exception while in charm code:
ops.model.ModelError: b'ERROR permission denied\n'
unit-ubuntu-advantage-3: 04:46:40 ERROR hook "stop" (via hook dispatching script: dispatch) failed: exit status 1
unit-ubuntu-advantage-3: 04:46:40 ERROR resolver loop error: unit "ubuntu-advantage/3" not found
```
No custom stop handler exists; ops's default stop handler fails when its `juju-run` call is denied. Juju removes the unit regardless. Error originates in `ops/model.py:2183`.

**`juju resolve` correctly refuses blocked (non-error) units** — `ERROR resolving unit: ... unit is not in error state`. This is correct Juju behaviour, but operators reading the README (which mentions "hook failed") may try `juju resolve` on a merely blocked unit and be confused by the refusal.

**`juju refresh` blocked by base mismatch** — rev 148 (latest/edge) targets `ubuntu@16.04,18.04,20.04,22.04`; rev 144 (noble/edge) targets `ubuntu@24.04`. The deployed machine (24.04) is stuck on `noble/edge` rev 144, missing the fixes in rev 148.

**Scale up/down works correctly (with stop-hook caveat)** — `juju add-unit ubuntu` creates a new subordinate cleanly; `juju remove-unit ubuntu/1` removes it and stops the machine, modulo the stop-hook failure above.

**No actions defined** — `juju actions ubuntu-advantage` → "No actions defined for ubuntu-advantage." No `get-status`, `retry-attach`, or other manual-intervention action (issue #22).

**Empty config file crashes the `pro` CLI (confirmed live)** — manually emptying `/etc/ubuntu-advantage/uaclient.conf` causes `sudo pro config show` to crash:
```
File "/usr/lib/python3/dist-packages/uaclient/config.py", line 520, in parse_config
  cfg.update(safe_load(system.load_file(config_path)))
TypeError: 'NoneType' object is not iterable
```
`yaml.safe_load("")` returns `None`; `cfg.update(None)` raises. Would also crash the charm's own `update_configuration` if a hook fired against an empty file.

**Retry behaviour** — debug log shows `Retrying 2 more times.` / `Retrying 1 more times.` with sleeps of 0.5s/1s/2s (3.5s total); the attach call itself takes ~2s, so total wall time to give up is ~12s.

## Findings

### Token leaks in the published charm
- **Severity**: critical
- **Kind**: security
- **Where**: `src/charm.py` (published rev 143; local HEAD `80b53d2` has the fix, unreleased)
- **Evidence**: Live `juju status`/`juju debug-log` show `['ubuntu-advantage', 'attach', 'invalid-token-xyz']` in cleartext. Rev 143 passes the token directly as a positional arg; HEAD always uses `["ubuntu-advantage", "attach", "--attach-config", temp_file]`.
- **Impact**: Any operator with `juju status` or `juju debug-log` access can read the Ubuntu Pro subscription token in cleartext — secret exposure.
- **Fix**: Trigger the release workflow for `ubuntu-advantage`/`ubuntu-advantage_noble` to ship commit `3476e53` ("Don't print secrets on errors", June 2025), which already fixes this.
- **Linter rule**: "Hook handler passes a token as a direct positional argument to `subprocess`; must be passed via config file or environment variable." Not mechanically checkable without data-flow analysis.

### Unhandled `CalledProcessError` in multiple config paths crashes the charm to error state
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:416–428` (`_configure_ua_proxy`), `install_ppa`/`remove_ppa` (`src/charm.py:32`, `:36`), `_update_ua_config_variable` (`src/charm.py:498–507`)
- **Evidence**: Four independent config options cause the identical error-state crash on the live system: `contract_url="not-a-url"` (04:17:51), `override-http-proxy="not-a-url"` (04:28:17/23/33), `override-https-proxy="http://bad-proxy"` (04:31:13), `ppa="ppa:totally-invalid/ppa-does-not-exist"` (04:40:57–04:41:01). In each case `subprocess.check_call` raises `CalledProcessError`, uncaught anywhere in the call chain.
- **Impact**: Any invalid config value that makes the UA client or apt fail during `config_changed` crashes the hook instead of setting a recoverable `BlockedStatus`. Recovery for proxy/contract_url requires SSH; PPA recovers automatically (see below).
- **Fix**: Wrap all `subprocess.check_call` calls in `_configure_ua_proxy`, `install_ppa`, `remove_ppa`, and `_update_ua_config_variable` in `try/except subprocess.CalledProcessError` → `BlockedStatus(str(e))`. Add `@retry(CalledProcessError)` to `install_ppa`/`remove_ppa`.
- **Linter rule**: "Hook handler calls `subprocess.check_call` without catching `CalledProcessError`." Mechanically checkable.

### Charm cannot self-recover from proxy/contract_url error state; PPA errors can auto-recover
- **Severity**: critical
- **Kind**: ux
- **Where**: `src/charm.py` — no `update_status` handler; `_configure_ua_proxy` runs unconditionally on every `config-changed`
- **Evidence**: After a proxy/contract_url error, `juju config ubuntu-advantage override-https-proxy=""` did not trigger a new hook — unit stayed in error state, re-running the failing hook every ~10s; recovery required SSH + `juju resolve`. After a PPA error, `juju config ubuntu-advantage ppa=""` did trigger a new hook (~40s later) and the unit recovered automatically to "No token configured" blocked, no `juju resolve` needed. Root cause: clearing PPA lets `remove_ppa("")` succeed as a no-op; clearing proxy still re-executes `_configure_ua_proxy`, which re-hits the same broken config file.
- **Impact**: Two classes of error exist — transient (PPA, auto-recoverable) and persistent (proxy/contract_url, needs manual intervention) — and operators have no way to distinguish them or trigger recovery without SSH. Issue #22 (open since 2026-06-29) was filed specifically because an operator got stuck this way.
- **Fix**: Add an `update_status` handler. Validate config values (e.g. URL format) before writing them. Consider a `retry-attach` action as requested in #22.
- **Linter rule**: "Charm does not observe `self.on.update_status`." Checkable.

### `apt.add_package` has no exception handling in the charm layer
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:355–361` (`_handle_package_state`)
- **Evidence**: `apt.add_package("ubuntu-advantage-tools", update_cache=True)` is called with no try/except. `update_cache=True` triggers `apt.update()`, which calls `check_call(["apt-get", "update"], ...)` (`lib/charms/operator_libs_linux/v0/apt.py:837`) with no exception handling of its own; failure propagates as `CalledProcessError`. Package-not-found propagates as `PackageError`. Neither path has test coverage.
- **Impact**: On a machine with no network access, the charm crashes to error state on first install rather than reporting a clear `BlockedStatus`.
- **Fix**: Wrap the `apt.add_package` call in `try/except (apt.PackageError, apt.PackageNotFoundError, CalledProcessError)` and set `BlockedStatus` with a distinct message per exception type.
- **Linter rule**: "Hook handler calls `apt.add_package` without catching `PackageError`." Checkable.

### Empty config file crashes the `pro` CLI and propagates to the charm
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:49–69` (`update_configuration`)
- **Evidence**: `yaml.safe_load("")` returns `None` (confirmed via `python3 -c "import yaml; print(yaml.safe_load(''))"`). `client_config[key] = value` on `None` raises `TypeError`. Confirmed live: after emptying `/etc/ubuntu-advantage/uaclient.conf`, `sudo pro config show` itself crashes in `uaclient/config.py:parse_config` with `cfg.update(safe_load(...))` → `TypeError: 'NoneType' object is not iterable`. All subsequent `pro config` calls from the charm would then crash too.
- **Impact**: If the config file is ever emptied or corrupted externally, the entire UA client stack fails and the charm has no defense. Root cause of the CLI crash is in `pro` itself, not the charm, but the charm's own `update_configuration` has the identical vulnerability.
- **Fix**: Change `client_config = yaml.safe_load(f)` to `client_config = yaml.safe_load(f) or {}`; add try/except around the file operations for corruption handling.
- **Linter rule**: "File read with `yaml.safe_load` without handling `None` return for an empty file." Checkable.

### Missing `update_status` hook — charm cannot self-heal
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:285` (only `config_changed` is observed)
- **Evidence**: `grep -n "update_status\|on_update_status" src/charm.py` returns nothing. Debug log at 04:27:56/04:30:13 confirms the hook fires as a no-op. Confirmed by issue #20 (open since 2025-06-24).
- **Impact**: A transient attach failure (network, contract server) blocks the charm permanently with no retry path, especially painful combined with the inability to SSH.
- **Fix**: Add `self.framework.observe(self.on.update_status, self._on_update_status)`; guard against overwriting an existing `BlockedStatus`.
- **Linter rule**: "Charm does not observe `self.on.update_status`." Checkable.

### Published charm is months behind current source — missing 3 config options
- **Severity**: high
- **Kind**: bug
- **Where**: charmhub — `ubuntu-advantage` on `noble/edge` at rev 143; local HEAD `80b53d2` (2026-04-06)
- **Evidence**: `juju config ubuntu-advantage` on rev 143 returns 9 options; source `config.yaml` has 12. Missing: `security_url`, `apt_news_url`, `vulnerability_data_url_prefix`; setting any returns "unknown option". The token-leak fix (`3476e53`, 2025-06-20) is also missing. Confirmed by issue #35 (2026-03-02).
- **Impact**: Operators cannot use these three options, which matter most for air-gapped environments (issue #19) needing local mirrors.
- **Fix**: Trigger the release workflow to build and publish from current `main`.
- **Linter rule**: not established.

### Race condition in `disable_canonical_livepatch` can block the unit permanently
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:128–141`
- **Evidence**: `canonical-livepatch disable` returns exit code 1 when the daemon is not running; `_configure_livepatch` catches this and sets `BlockedStatus` correctly, but there is no `update_status` handler to retry. Confirmed by issue #38 (open since 2026-04-24) and live debug log at 04:54:59 (`connection to the daemon failed: dial unix ... no such file or directory`). `_state.livepatch_installed` is also never reset to `False` after a successful disable.
- **Impact**: If the snap daemon is not running when disable is attempted, the unit blocks permanently with no automatic recovery. The comment at line 391 ("does not throw an error") is factually wrong and contributed to this not being prioritized.
- **Fix**: Treat "connection refused"/"no such file" as a benign non-error path. Reset `_state.livepatch_installed = False` after successful disable. Add `@retry(ProcessExecutionError)`.
- **Linter rule**: not established.

### Stop hook fails on subordinate unit removal
- **Severity**: medium
- **Kind**: bug
- **Where**: ops default stop handler, invoked because the charm has no `on_stop` observer
- **Evidence**: `unit-ubuntu-advantage-3: 04:46:40 ERROR Uncaught exception while in charm code: ops.model.ModelError: b'ERROR permission denied\n'`; `hook "stop" ... failed: exit status 1`; `resolver loop error: unit "ubuntu-advantage/3" not found`. `grep "on_stop" src/charm.py` returns nothing. Error originates in `ops/model.py:2183` (a denied `juju-run` call). Juju removes the unit regardless.
- **Impact**: Removing a unit logs a noisy failure and triggers the resolver loop unnecessarily, though the unit does eventually shut down.
- **Fix**: Implement `self.framework.observe(self.on.stop, self._on_stop)` with a no-op (or subscription-detach) body to prevent the default handler from running.
- **Linter rule**: "Machine subordinate charm does not observe `self.on.stop`; default stop handler may fail with permission-denied errors." Checkable.

### No cleanup on relation departure or charm removal
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` (`grep -n "relation_departed\|on_stop"` returns nothing)
- **Evidence**: Debug log confirms `juju-info-relation-departed` and `juju-info-relation-broken` complete successfully via the empty default handler. `juju remove-application --force ubuntu-advantage` leaves the UA subscription attached on the machine.
- **Impact**: In a real deployment with a valid token, breaking the relation or removing the charm leaves the subscription attached, continuing to consume a contract seat.
- **Fix**: Observe `juju_info_relation_departed` and call `detach_subscription(self.ssl_env)`; add a `stop` handler that detaches on charm removal.
- **Linter rule**: "Subordinate charm does not observe `juju-info` relation-departed or `stop`; subscription not detached on removal." Checkable.

### `_configure_ua_proxy` runs on every `config-changed` unconditionally
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:416–428`
- **Evidence**: `_configure_ua_proxy` calls `subprocess.check_call` twice on every `config-changed` (unset `http_proxy`/`https_proxy` when no override is set), regardless of whether values changed. `test_config_changed_ppa_unmodified` confirms a `check_call` count of 2 even on no-op config changes.
- **Impact**: Redundant subprocess calls, and — more importantly — these calls crash the hook if the UA config file is invalid (see the critical finding above).
- **Fix**: Guard with StoredState comparison, matching the `_update_ua_config_variable` pattern.
- **Linter rule**: "Hook handler calls `subprocess.check_call` without checking if the value changed." Checkable.

### `update_configuration`/`remove_configuration` assume the config file exists
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:49–69`
- **Evidence**: Both open `/etc/ubuntu-advantage/uaclient.conf` with mode `"r+"`, which raises `FileNotFoundError` if missing. Ordering relative to package install is implicit, not enforced by a guard.
- **Impact**: If the config file is missing for any reason, the charm crashes to error state with an unhandled `FileNotFoundError`.
- **Fix**: Catch `FileNotFoundError` and create the file with default contents.
- **Linter rule**: "File I/O function does not handle `FileNotFoundError`." Checkable.

### Config post-deploy is not additive (issue #33)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:423–431` (`parse_services`/`attach`)
- **Evidence**: Confirmed by open issue #33 (2026-02-16, unverified against a live re-attach in this review). Setting `services=esm-infra` then `services=esm-infra,usg` allegedly only enables `usg`, because `--attach-config` re-attaches with only the specified services.
- **Impact**: Operators expect additive service lists; the current behaviour silently drops previously-enabled services.
- **Fix**: Merge new services with the existing `pro status` output before re-attaching, or document the replacement semantics explicitly.
- **Linter rule**: not established.

### `no_proxy` not forwarded to the UA client (issue #19)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:416–428` (`_configure_ua_proxy`)
- **Evidence**: `self.proxy_env["no_proxy"]` (from `JUJU_CHARM_NO_PROXY`) is passed to PPA operations via `env=env`, but `_configure_ua_proxy` only sets `http_proxy`/`https_proxy`, never `no_proxy`. Confirmed by issue #19 (open since 2025-06-24).
- **Impact**: In air-gapped environments with a local contract server behind a Juju proxy, contract API calls route through the proxy even when they should be excluded by `no_proxy`.
- **Fix**: Also call `pro config set no_proxy=<JUJU_CHARM_NO_PROXY>`.
- **Linter rule**: not established.

### `canonical-livepatch` commands inconsistently decorated with `@retry`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:89–141`
- **Evidence**: `attach` and `get_status_output` are decorated with `@retry(ProcessExecutionError)`; `set_livepatch_server`, `enable_livepatch_server`, `disable_canonical_livepatch` are not, despite raising the same exception type. The misleading comment at line 391 ("Disabling ... when already disabled does not throw an error") is false — see the livepatch race finding above.
- **Impact**: Transient livepatch/snap failures block the unit with no retry.
- **Fix**: Apply `@retry(ProcessExecutionError)` to all three functions; correct the comment.
- **Linter rule**: not established.

### `test_config_changed_ppa_apt_failure` documents the bug rather than testing a fix
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:201–210`
- **Evidence**: The test calls `self.assertRaises(CalledProcessError)`, asserting the exception propagates rather than converting to `BlockedStatus`.
- **Impact**: A future fix that adds exception handling to `install_ppa` would make this test fail, discouraging the fix.
- **Fix**: Change the assertion to expect `BlockedStatus`, and add the corresponding exception handling to `install_ppa`.
- **Linter rule**: not established.

### README documents the error-state crash without explaining recovery
- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md` (proxy configuration section)
- **Evidence**: README states proxy misconfiguration "will most likely get a `hook failed: \"config-changed\"` message," but gives no recovery instructions, no mention of `juju resolve`, and no note that the charm cannot self-heal. Confirmed by issue #22, where an operator was stuck in exactly this situation.
- **Impact**: Operators know the failure can happen but not how to recover from it.
- **Fix**: Add a Troubleshooting section covering `juju resolve`, checking the unit log, manually fixing the UA config file, and the PPA-vs-proxy auto-recovery distinction.
- **Linter rule**: not established.

### `ops` library pinned to `>=1.5.0, <2.0` blocks Python 3.13+ support (issue #12)
- **Severity**: medium
- **Kind**: bug
- **Where**: `requirements.txt:1`
- **Evidence**: Confirmed by open issue #12 (2025-06-16): the constraint does not work on Python 3.13+, which Ubuntu 25.04 ships. Issue #39 (2026-06-16) requests Ubuntu 26.04 support, blocked on this.
- **Impact**: The charm cannot run on newer Ubuntu releases.
- **Fix**: Upgrade to `ops >= 2.0.0` and migrate breaking API changes.
- **Linter rule**: not established.

### Release workflow only builds two of four targets
- **Severity**: medium
- **Kind**: bug
- **Where**: `.github/workflows/release.yml`
- **Evidence**: The matrix only includes `ubuntu-pro` and `ubuntu-pro_noble`. `ubuntu-advantage`/`ubuntu-advantage_noble` are absent, yet still published on charmhub (rev 143/148), out of date by months.
- **Impact**: The deprecated `ubuntu-advantage` name is left unmaintained by CI while still distributed with known security issues (the token leak).
- **Fix**: Add the missing targets to the release matrix, or remove them from charmhub and update the README to only reference `ubuntu-pro`.
- **Linter rule**: not established.

### `ssl_env` not forwarded to apt operations
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:293–300` (`_setup_proxy_env`) and `:359` (`apt.add_package`)
- **Evidence**: `self.ssl_env["SSL_CERT_FILE"]` (from `override-ssl-cert-file`) is used only for pro-client operations (`attach`, `detach`, `get_status_output`, `ua_enable_service`), not for `apt.add_package`, which runs with the default environment. Live test: setting `override-ssl-cert-file="/nonexistent/cert.pem"` did not immediately error (unit stayed blocked); a real mismatch would only surface when apt needs the custom CA.
- **Impact**: A custom CA cert configured for the pro API is not honored by apt/PPA operations, causing inconsistent TLS trust between the two.
- **Fix**: Pass `ssl_env` into apt operations, or document that the override only applies to pro-client calls.
- **Linter rule**: not established.

### StoredState upgrade path has no explicit handler
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:273–280`; no `upgrade_charm` handler
- **Evidence**: `grep "upgrade.charm\|on_upgrade" src/charm.py` returns nothing. `StoredState.set_default()` does not overwrite existing keys on upgrade; new keys (`apt_news_url`, `vulnerability_data_url_prefix`) default to `None`, which happens to be handled correctly downstream. No test covers the upgrade path.
- **Impact**: A future StoredState key with a non-idempotent default could misbehave silently on upgrade; no migration path exists for UA config-file format changes.
- **Fix**: Add an explicit `upgrade_charm` handler that re-runs `_handle_package_state`; add a test that pre-populates partial StoredState to simulate upgrade.
- **Linter rule**: "Charm does not observe `self.on.upgrade_charm`." Checkable.

### `apt.update()` in the vendored library has no exception handling
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/operator_libs_linux/v0/apt.py:837`
- **Evidence**: `check_call(["apt-get", "update"], stderr=PIPE, stdout=PIPE)` with no try/except; failure propagates as `CalledProcessError` to the charm layer, which also doesn't catch it (see the critical finding above).
- **Impact**: Same failure mode as the charm-layer finding; pre-existing issue in the vendored library.
- **Fix**: Add exception handling in the library, or ensure the charm layer wraps `apt.add_package`.
- **Linter rule**: "Library function calls `subprocess.check_call` without catching `CalledProcessError`." Checkable.

### Charm does not surface `pro` client warnings (issue #34)
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:456–462` (`_handle_status_state`)
- **Evidence**: Confirmed by issue #34 (2026-02-13). Services with `status: warning` from `pro status` are included in the active-services list and reported as `ActiveStatus`, hiding the warning.
- **Impact**: Operators/dashboards don't see services that need attention (e.g. livepatch not covering the current kernel).
- **Fix**: Separate "enabled" and "warning" services in the status message.
- **Linter rule**: not established.

### README typo
- **Severity**: low
- **Kind**: docs
- **Where**: `README.md:7`
- **Evidence**: `recieved` → `receive`.
- **Fix**: One-character correction.
- **Linter rule**: caught by `codespell`.

### Tests use deprecated `ops.testing.Harness` API
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:79` and throughout
- **Evidence**: Tests emit `PendingDeprecationWarning: Harness is deprecated`; a `harness` pytest fixture exists but `TestCharm` still uses `Harness` directly.
- **Impact**: Tests will need migration before `Harness` is removed from `ops`.
- **Fix**: Migrate to `Context`/`State` from `ops.testing`.
- **Linter rule**: not established.

### Ruff finds 97 violations across charm and vendored library
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py`, `src/exceptions.py`, `src/utils/retry.py`, `lib/charms/operator_libs_linux/v0/apt.py`
- **Evidence**: `ruff check src/ lib/` reports 97 errors, including `IOError` → `OSError` (deprecated alias, line 174), `raise e` without exception chaining (`TRY201`), f-strings vs `.format()` (`UP032`), `subprocess.run` without explicit `check=` (`PLW1510`), and `capture_output` vs `stdout=PIPE, stderr=PIPE` (`UP022`). The codebase passes `pflake8`, `isort`, and `black` but fails `ruff`.
- **Impact**: Code-quality drift relative to increasingly-standard tooling; some findings (e.g. `subprocess` checks) overlap with real bugs above.
- **Fix**: `ruff check --fix src/ lib/`, then manually address the rest.
- **Linter rule**: caught by `ruff`.

## Worth copying

- **Clean status precedence** (`src/charm.py:325–331`) — `if isinstance(self.unit.status, BlockedStatus): return` after each config-changed step is a clean way to stop later steps from overwriting an error status.
- **Retry decorator** (`src/utils/retry.py`) — a focused decorator with `RETRY_SLEEPS = [0.5, 1, 2]`, better than inline retry loops.
- **StoredState for idempotency** (`src/charm.py:273–280`) — tracks package/PPA install state cleanly, avoiding redundant subprocess calls.
- **File update pattern with seek/truncate** (`src/charm.py:49–69`) — `open(path, "r+")` + `seek(0)` + `yaml.dump` + `truncate()` is the right pattern for atomic config-file updates on machine charms.
- **Config variable update helper** (`src/charm.py:479–519`) — `_update_ua_config_variable` with StoredState comparison avoids redundant subprocess calls; should be applied to the proxy config path too.
- **Regression test for the token leak** (`tests/integration/test_charm.py::test_attach_invalid_token`) — explicitly asserts the token is not in `unit.workload_status_message`, directly testing the fix for issue #17.

## Common-practice notes

**Follows convention**: machine subordinate with `juju-info`/`scope: container`; shared `src/` with per-target `charmcraft.yaml`; vendored `operator_libs_linux/v0/apt.py` with proper `__init__.py` files; `StoredState` for idempotency; clean separation of pure subprocess-wrapper functions from `CharmBase`; `pytest-operator` integration tests against real Juju.

**Drifts from convention**: no `update_status` handler; no `stop` hook (unusual for a subordinate needing cleanup, and its absence caused a visible scale-down failure); no `concierge*.yaml`/`spread.yaml`, uses plain tox + manual LXD; deprecated `Harness` instead of `Context`; no `terraform/` module; no actions defined; release workflow covers 2 of 4 build targets; no `upgrade-charm` handler.

**Worse than convention**: `_configure_ua_proxy` re-runs on every hook without the StoredState guard used elsewhere; multiple `subprocess.check_call` sites with no `CalledProcessError` handling, unlike the `subprocess.run`→`ProcessExecutionError` pattern used for `attach`/`get_status_output`; tests mix `unittest.TestCase` and pytest fixtures in the same file; no retry decorator on livepatch operations even though `attach`/`get_status_output` have one.

## Tests

**Unit tests**: 45 passing, 80% line coverage on `src/charm.py` (54 statements missed), 33 `PendingDeprecationWarning`s for `Harness`.

Uncovered lines relevant to findings above: `set_livepatch_server` (80–98) and `enable_livepatch_server` (103–119) never tested in isolation; the non-zero-exit path of `disable_canonical_livepatch` (126–147) is untested (the issue #38 gap); `create_attach_config` IOError path (174–176) untested; `attach` error-detaching (192–201) and error-running (212–223, only via retry mock) paths untested; `get_status_output` retry-exhausted path (229–252) untested; exception-handler branches at 355–361, 370–374, 393–395, 433–435 untested.

Key coverage gaps: no test for `CalledProcessError` in `_configure_ua_proxy` or `_update_ua_config_variable` (the critical failure path, confirmed by 3 live failure injections); no test for `CalledProcessError`/`PackageError` from `install_ppa`/`remove_ppa`/`apt.add_package` (`test_config_changed_ppa_apt_failure` explicitly expects the exception to propagate, documenting the bug rather than fixing it); no test for `FileNotFoundError` on a missing config file; no test for the empty-file `TypeError` path; no test for `canonical-livepatch disable` returning non-zero when the daemon isn't running; no test for `update_status` (doesn't exist), relation-departed cleanup, invalid `contract_url`, the StoredState upgrade path, or `ssl_env` not being used for apt.

**Integration tests**: 14 cases in `tests/integration/test_charm.py` covering attach/detach, livepatch, URL configs, and the token-leak regression (`test_attach_invalid_token`, `test_livepatch_server_set_fails`). Could not be run in this environment (requires `PRO_CHARM_TEST_TOKEN` / `PRO_CHARM_TEST_LIVEPATCH_STAGING_TOKEN`).

**Linter results**: `codespell` — 1 typo ("recieved"); `pflake8`/`isort --check`/`black --check` — clean; `ruff check src/ lib/` — 97 errors (see finding above).

## Docs

**README.md**: basic usage, proxy-config note (which explicitly acknowledges the `hook failed: "config-changed"` crash), dev setup, charmhub links. Missing: upgrade path, what to do when blocked/errored, what `juju resolve` does, per-option documentation, meaning of "Attached (services)", and the auto-recoverable-vs-not distinction between PPA and proxy/contract_url errors.

**CONTRIBUTING.md**: build instructions for all four targets, integration-test env var requirements — clear and accurate.

**config.yaml**: full option documentation at repo root, populates the Charmhub Configure tab; missing from published rev 143: `security_url`, `apt_news_url`, `vulnerability_data_url_prefix`.

**Charmhub description**: notes `ubuntu-advantage` is "the old name" for `ubuntu-pro" while both remain published; doesn't explain the deprecation given continued publication. Charm noted as "not publicly findable via search in charmhub."

## Open questions

1. Why hasn't the token-leak fix (`3476e53`, 2025-06-20) been released to `ubuntu-advantage`? The release workflow only builds `ubuntu-pro`/`ubuntu-pro_noble` — is `ubuntu-advantage` built by a separate CI system?
2. What is the intended semantics for service-list updates (issue #33) — additive or replacement? Open since February 2026 with no fix.
3. Can the `pro` package's postinst script recreate `/etc/ubuntu-advantage/uaclient.conf` if emptied? What would trigger that?
4. Is `ubuntu-advantage` truly deprecated? Charmhub says so, README recommends `ubuntu-pro`, but both names are still published and neither the release workflow nor the docs fully explain the situation.
5. Should the charm validate config values (URLs, proxy settings) before writing them to the UA config file, rather than relying on catching failures after the fact?
6. Why is `_state.livepatch_installed` never reset to `False` after a successful disable? Does this cause unnecessary reinstall work if livepatch is later re-enabled?
7. What is the plan for Ubuntu 26.04 support (issue #39), given it's blocked on the `ops < 2.0` constraint (issue #12)?
8. Is the stop-hook `ModelError: permission denied` a Juju-agent bug or something the charm can work around simply by adding a no-op stop handler?
