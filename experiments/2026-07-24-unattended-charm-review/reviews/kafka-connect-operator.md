# kafka-connect-operator

**Verdict**: A well-architected machine charm (TypedCharmBase + pydantic config, clean context/manager separation) that is **broken on Juju 4.x**: any attempt to enable TLS crashes the `certificates-relation-joined` hook and leaves the unit permanently stuck in `error` — unrecoverable except by removing the application. A second, independent bug bricks the unit if `system-users` is ever set to an empty string. Both are one-line-guard fixes but currently make the charm unsafe to run in production on Juju 4.x with TLS. A maintainer should fix `internal_address` to fall back to `ingress-address`, add the missing `None` guard in `system_users_secret_validator`, and add `event.defer()` to the plugin-download error path (issue #58) before this ships further on `4/edge`.

| | |
|---|---|
| Repo | canonical/kafka-connect-operator @ `ad7cfb3` (2026-07-02) |
| Charms | kafka-connect (machine), sink-integrator (machine, test-only), source-integrator (machine, test-only) |
| Substrate | machine (LXD) |
| Deployed | yes — `concierge-lxd-4` (Juju 4.0.12), channel `4/edge` rev 38; cross-checked on `concierge-lxd` (Juju 3.6.27) |
| Reviewed | 2026-08-20 |

## What it does

Charmed Apache Kafka Connect operator. The charm:
- Installs and holds the `charmed-kafka` snap (rev 67) on the machine
- Starts/stops the `connect-distributed` service via snap services
- Manages connector plugin lifecycle (from Juju resources or downloaded from URLs)
- Provides credentials to integrator charms via the `connect-client` relation interface
- Requires an Apache Kafka cluster via the `kafka-client` relation
- Supports TLS via `tls-certificates` relation (REST API and Kafka client)
- Exposes JMX metrics to COS via `cos-agent`
- Manages REST API user credentials via Juju secrets (`system-users` config)

## Deployment log

### Juju 4.x (primary deployment on `concierge-lxd-4`)

```
juju add-model rv-kafka-connect --controller concierge-lxd-4  # OK
juju deploy kafka-connect --channel 4/edge --model rv-kafka-connect  # OK, rev 38
# Machine juju-9d93d8-1 created, IP 10.5.87.42
# Unit blocked: "Application needs Kafka client relation" — expected, no Kafka
```

**Config change with invalid `log_level=INVALID`**
```
juju config kafka-connect log_level=INVALID
# Hook fires: config-changed → pydantic ValidationError → hook fails
# Unit goes to ERROR state with Python traceback in unit log:
#   pydantic.error_wrappers.ValidationError: 1 validation error for CharmConfig
#   log_level: unexpected value; permitted: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
# Fixing config to valid value (log_level=DEBUG) → unit recovers to blocked
```

**TLS relation test on Juju 4.x**
```
juju deploy self-signed-certificates --channel 1/stable
juju relate kafka-connect self-signed-certificates
# certificates-relation-joined hook fires → crash:
#   ValueError: Attribute's length must be >= 1 and <= 64, but it was 0
#   at tls_certificates.py:1057 generate_csr() — subject=""
#   subject=self.charm.context.worker_unit.internal_address  # returns "" on Juju 4.x
# Unit goes to ERROR state.
```

**TLS relation removal (Juju 4.x) — permanent error state**
```
juju remove-relation kafka-connect self-signed-certificates
# Log on machine 1 (juju-9d93d8-1):
# 21:26:50 ERROR hook "certificates-relation-joined" failed: exit status 1
# 21:26:50 INFO juju.worker.uniter resolver.go:169 awaiting error resolution
# (no certificates-relation-broken entry ever appears in the log)
# The hook continues retrying every few seconds.
# juju resolve kafka-connect/1 → command accepted, no effect.
# Unit remains stuck in ERROR state.
# Only `juju remove-application kafka-connect` can clean up.
```

**COS/grafana-agent integration**
```
juju deploy grafana-agent --channel 2/edge
juju relate kafka-connect:cos-agent grafana-agent:cos-agent
# Relation established; grafana-agent deployed to same machine (correct for machine charms)
# grafana-agent reaches "blocked" (needs its own config) — cos-agent relation is working
```

**Process kill / restart test**
```
ssh ubuntu@10.5.87.42 'sudo kill -9 37567'   # grafana-agent, PID 37567
# Process auto-restarts within 3 seconds (snap systemd service)
# PID changes to 41942 — correct, expected behaviour
# juju status shows no change to kafka-connect unit
```

**Scale-up**
```
juju add-unit kafka-connect -n 1
# Machine juju-9d93d8-3 created (IP 10.5.87.33)
# Unit kafka-connect/2: install → blocked (no Kafka)
# Scale-down: blocked by interactive confirmation prompt (requires `yes |` or `echo y |`)
```

**Pre-upgrade-check action**
```
juju run kafka-connect/1 pre-upgrade-check
# Action fails: "Pre-upgrade check failed and cannot safely upgrade"
# Cause: "Cluster is not healthy" (no Kafka, Connect service not running)
# Expected and correct behavior
```

**Peer relation data (Juju 4.x)**
```
endpoint: worker
local-unit data:
  egress-subnets: 10.5.87.42/32
  ingress-address: 10.5.87.42
  restart: "true"
# NO private-address, NO hostname, NO ip → internal_address returns ""
```

### Juju 3.6 (cross-version check on `concierge-lxd`)
```
juju add-model rv-kafka-connect-36 --controller concierge-lxd
juju deploy kafka-connect --channel 4/edge
# Machine juju-9fda84-0 created (IP 10.5.87.151)
# Unit blocked: "Application needs Kafka client relation" — correct
```

**Peer relation data (Juju 3.6)**
```
endpoint: worker
local-unit data:
  egress-subnets: 10.5.87.151/32
  ingress-address: 10.5.87.151
  private-address: 10.5.87.151   ← present in Juju 3.6
  restart: "true"
# private-address IS present → internal_address returns "10.5.87.151"
```

### Runtime behaviour deepening (additional tests on `rv-kafka-connect-v4`)

**Invalid `profile=INVALID` config**
```
juju config kafka-connect profile=INVALID
# Hook fires → pydantic ValidationError → hook exits 1
# Unit goes to ERROR, awaiting error resolution
# Fix: juju config kafka-connect profile=production + juju resolve kafka-connect/0
# Unit returns to blocked — recoverable
```

**Invalid `system-users` secret ID format (`secret:doesnotexist123` — 12 chars)**
```
juju config kafka-connect system-users=secret:doesnotexist123
# Hook fires → ValidationError: "Provided value for system-users config is not a valid secret URI..."
# Unit goes to ERROR, awaiting error resolution
# Recovery: juju resolve kafka-connect/0 → recovers to blocked
```

**Valid-format but non-existent secret ID (`secret:abcdefghijklmnopqrst` — 20 chars)**
```
juju config kafka-connect system-users=secret:abcdefghijklmnopqrst
# Hook fires → charm __init__ succeeds (regex matches 20-char format)
# load_auth_secret() catches SecretNotFoundError → returns {} silently
# Unit stays in blocked status (no crash) — graceful degradation
```

**Blank secret config (`system-users=''`)**
```
juju config kafka-connect system-users=''
# blank_string pre-validator converts "" to None
# system_users_secret_validator calls SECRET_REGEX.match(None) → TypeError
# Hook exits 1: "expected string or bytes-like object, got 'NoneType'"
# Unit goes to ERROR, awaiting error resolution
# Recovery: set valid-format secret ID + juju resolve kafka-connect/0
```

**Invalid `rest_port=99999`**: Config accepted without bounds check; charm goes through `config-changed` without crashing; port value written to `connect-distributed.properties` without charm-level validation.

**Recovery comparison**:
- Config pydantic validation errors → recoverable with `juju resolve` (after fixing config)
- TLS `generate_csr` crash on Juju 4.x → NOT recoverable; `certificates-relation-broken` never fires; unit permanently stuck

## Observed behaviour

- **Install time**: ~90s for snap install (observed in status transition `maintenance → blocked`)
- **Status**: `blocked` with "Application needs Kafka client relation" when no Kafka relation — clear and actionable
- **Snap hold**: The charm calls `snap hold` after install — prevents automatic updates, good for production
- **Config files**: Written to `/var/snap/charmed-kafka/current/etc/connect/` with ownership `_daemon_:root`, permissions `750/770`
- **Invalid config → hook failure**: `log_level=INVALID` raises a pydantic `ValidationError` during `__init__`, crashing the hook with a raw Python traceback. Unit goes to `error`. Fixing the config lets it recover.
- **TLS on Juju 4.x → permanent hook failure, unrecoverable**: Adding a TLS relation crashes `certificates-relation-joined` with `ValueError: Attribute's length must be >= 1 and <= 64, but it was 0`. Removing the relation does NOT fire `certificates-relation-broken`; the unit stays in `error` and the hook retries indefinitely. `juju resolve` does not recover it.
- **TLS on Juju 3.6 → works**: Peer relation has `private-address`, so `internal_address` returns the correct IP.
- **Recovery from invalid-config error state**: fixing the config lets the agent retry the hook and recover.
- **Recovery from TLS error state**: not possible without removing the application.
- **COS integration**: `cos-agent` relation works correctly; grafana-agent deploys to the same machine and reaches its own expected blocked state.
- **Scale-up**: adds a new machine with the snap installed; new unit reaches `blocked` (no Kafka) correctly.
- **Pre-upgrade-check**: correctly fails when the Connect service is not healthy.
- **Process kill**: grafana-agent restarts automatically within 3 seconds via snap systemd service; the charm itself does not manage any process directly.
- **Only one action defined**: `pre-upgrade-check`. No actions for connector, user, or plugin management.
- **Kafka relation**: attempted with the `kafka` charm (charmhub rev 262, Juju 4/edge). Blocked at "waiting for machine" → "blocked: application needs to be related with a KRaft controller." Kafka 4.x requires a multi-node KRaft controller cluster not achievable in this environment — the kafka→kafka-connect integration flow was not exercised.
- **Linting**: ruff (`--select=E,F,W`) finds no correctness bugs; 31 E501 line-too-long violations in `src/`. Wider ruleset (`+C4,UP,ANN,S`) adds 39 `ANN` missing-type-annotation warnings. pyright: 0 errors, 0 warnings. codespell: 2 typos in vendored library code. `charmcraft analyze`: entrypoint ERROR (false positive from the poetry plugin layout), series WARNING, config-naming WARNING, framework false positive ("charm is not based on the operator framework").
- **Unit tests**: 75/75 pass in ~2.2s (`PYTHONPATH=lib:src poetry run python -m pytest tests/unit/`).
- **Test coverage**: 81% overall. `managers/tls.py` 27% — lines 48–285 essentially untested (certificate creation, keytool operations, keystore/truststore setup, SANs parsing, rotation). `workload.py` 63% — `start`/`stop`/`restart` and `exec` error branches untested. `events/provider.py` 82% — `PluginDownloadFailedError` path untested.

## Findings

### 1. `internal_address` returns empty string on Juju 4.x — TLS broken and unit permanently stuck in error
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/core/models.py:336-337`, `src/events/tls.py:134`, `src/managers/config.py:210`, `src/managers/tls.py:189`
- **Evidence**:
  ```python
  def internal_address(self) -> str:
      addr = ""
      if self.substrate == "vm":
          for key in ["hostname", "ip", "private-address"]:
              if addr := self.relation_data.get(key, ""):
                  break
      return addr
  ```
  Juju 4.x LXD does not set `private-address`, `hostname`, or `ip` in the `worker` peer relation — only `ingress-address`. Confirmed via `juju show-unit`:
  ```
  local-unit data:
    egress-subnets: 10.5.87.42/32
    ingress-address: 10.5.87.42
    restart: "true"
  ```
  (Juju 3.6.27 has `private-address: 10.5.87.151` in the same relation.)

  `internal_address` therefore returns `""`, causing four downstream effects:
  1. `generate_csr(subject=internal_address, ...)` in `src/events/tls.py:134` calls into `tls_certificates.py:1057`, which raises `ValueError: Attribute's length must be >= 1 and <= 64, but it was 0`. The `certificates-relation-joined` hook crashes and the unit goes to `error`.
  2. `src/managers/config.py:210` writes `listeners={protocol}://{internal_address}:{port}`, producing `listeners=https://:8083`.
  3. `src/managers/tls.py:189` passes `sans_ip=[internal_address]` — an empty SAN entry.
  4. Removing the TLS relation while in error state never dispatches `certificates-relation-broken`; the `certificates-relation-joined` hook keeps retrying indefinitely, and `juju resolve` does not break the cycle. Recovery requires `juju remove-application`.

  Log evidence (`/var/log/juju/unit-kafka-connect-1.log`):
  ```
  21:26:49 INFO ran "certificates-relation-created" hook
  21:26:50 ERROR hook "certificates-relation-joined" failed: exit status 1
  21:26:57 ERROR hook "certificates-relation-joined" failed: exit status 1
  (no certificates-relation-broken ever appears in the log)
  21:27:08-21:27:50 INFO awaiting error resolution (hook keeps retrying)
  ```
- **Impact**: Any deployment on Juju 4.x LXD cannot use TLS, and an attempted TLS relation leaves the entire application permanently unrecoverable. The charm ships on `4/edge`, targeting exactly this Juju version. Confirmed bugs #58 (integrator permanently blocked) and #51 (upgrade tests broken) are downstream of related test gaps (see finding 2).
- **Fix**: Add `ingress-address` to the lookup keys (`for key in ["hostname", "ip", "private-address", "ingress-address"]`). Also guard `_tls_relation_joined` to check `internal_address` is non-empty before calling `generate_csr`, failing gracefully into `BlockedStatus` instead of crashing.
- **Linter rule**: "Context property reads peer relation for address but does not check `ingress-address`" — mechanically checkable.

### 2. Unit tests mock `private-address` in peer relation, masking the Juju 4.x bug
- **Severity**: critical
- **Kind**: test-gap
- **Where**: `tests/unit/test_tls.py:266`, `tests/unit/test_upgrade.py:81-82`
- **Evidence**: `test_tls.py` sets `local_unit_data={"private-address": "10.10.10.10", ...}`; `test_upgrade.py` sets `local_unit_data={"private-address": "000.000.000"}`. `ops-scenario`'s `PeerRelation` also defaults to `private-address: 192.0.2.0`. `internal_address` therefore always resolves in tests, and the Juju 4.x bug is never caught.
- **Impact**: Test suite passes despite the charm being broken on the Juju version it targets in production.
- **Fix**: Add a test variant with a peer relation that has `ingress-address` but no `private-address`, matching real Juju 4.x behaviour.
- **Linter rule**: not established.

### 3. `_on_integration_requested` does not defer on `PluginDownloadFailedError` — permanently blocks integrator (issue #58)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/events/provider.py:70-72`
- **Evidence**:
  ```python
  except PluginDownloadFailedError as e:
      logger.error(f"Unable to fetch the plugin: {e}")
      return
  ```
  No `event.defer()` before `return`. The integrator charm is left waiting indefinitely for credentials never set on `connect-client`.
- **Impact**: Any integrator whose `plugin-url` is unreachable or invalid permanently blocks on the kafka-connect side; the only recovery is removing and re-relating the integrator.
- **Fix**: Call `event.defer()` before `return` so the handler reruns later.
- **Linter rule**: "Hook handler catches a named exception and returns without deferring the event" — mechanically checkable.

### 4. `system_users_secret_validator` crashes on `None` — `system-users=''` bricks the unit
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/core/structured_config.py:41-46`
- **Evidence**: The `blank_string` pre-validator (`@validator("*", pre=True)`) converts `''` to `None`. `system_users_secret_validator` runs afterward but does not guard against `None`:
  ```python
  @validator("system_users")
  @classmethod
  def system_users_secret_validator(cls, value: str) -> str:
      if not SECRET_REGEX.match(value):  # value is None here after blank_string pre-validator
          raise ValueError(...)
      return value
  ```
  `SECRET_REGEX.match(None)` raises `TypeError: expected string or bytes-like object, got 'NoneType'`. Confirmed: `juju config kafka-connect system-users=''` → unit `error`. Recovery requires setting a valid-format ID and `juju resolve`. (A valid-format but non-existent secret ID is handled gracefully — `load_auth_secret()` catches `SecretNotFoundError` and returns `{}`.)
- **Impact**: Accidentally clearing `system-users` bricks the charm with a cryptic TypeError; recovery requires knowing to set a valid-format placeholder first.
- **Fix**: Add `if value is None: return None` at the top of `system_users_secret_validator`, before the regex match.
- **Linter rule**: "Field-level validator calls a string method on a field declared as `str | None` without checking for `None` first" — mechanically checkable.

### 5. TLS manager only 27% covered — entire `configure()` path and certificate rotation untested
- **Severity**: high
- **Kind**: test-gap
- **Where**: `src/managers/tls.py` (lines 48–285)
- **Evidence**: Coverage report shows the following entirely untested: `set_server_key()`, `set_ca()`, `set_certificate()`, `set_bundle()`, `set_chain()`, `set_truststore()`, `set_keystore()`, `configure()`, `build_sans()`, `get_current_sans()`, `sans_change_detected`, `remove_stores()`.
- **Impact**: Certificate installation and renewal — the most security-sensitive paths in the charm — are entirely untested.
- **Fix**: Add scenario tests for the full TLS lifecycle: certificate available → configure → files written; certificate expired → `sans_change_detected` → new CSR generated.
- **Linter rule**: not established.

### 6. Integration upgrade tests are broken (issue #51)
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/integration/test_upgrade.py`
- **Evidence**: Issue #51: "Refresh tests should actually work after release — test_upgrade.py does nothing due to lack of refresh path." The `kafka_connect_charm` fixture always builds from source and ignores `CI_PACKED_CHARMS` passed in by CI.
- **Impact**: The upgrade path is not tested end-to-end in CI.
- **Fix**: Fixture should use the packed charm from `CI_PACKED_CHARMS` when available, falling back to building from source.
- **Linter rule**: not established.

### 7. Invalid config causes pydantic `ValidationError` crash instead of `BlockedStatus`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:60`
- **Evidence**: Setting `log_level=INVALID` raises `pydantic.error_wrappers.ValidationError` before `__init__` completes. The hook crashes with a raw traceback and the unit goes to `error` rather than `blocked` with an actionable message. Recovers once the config is fixed.
- **Impact**: Operators monitoring for `error` state see this as a charm bug rather than a config mistake, even though it is recoverable.
- **Fix**: Wrap the top of `__init__` in try/except for `ValidationError` and set `Status.CONFIG_ERROR`, or rely on `config.yaml` schema validation to reject invalid values before they reach the charm.
- **Linter rule**: not established.

### 8. `_restart_callback` tight polling loop — `should_restart` may not clear if service is slow to start
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:134-139`
- **Evidence**:
  ```python
  for _ in range(4):
      # shouldn't take longer than a minute
      if self.connect_manager.healthy:
          self.context.worker_unit.should_restart = False
          return
  ```
  No `time.sleep()` between iterations. `workload.active()` uses a tenacity retry (`wait=1s, stop=5 attempts`), so it can take up to 5 seconds to report healthy — longer than 4 rapid, unslept iterations may allow. If the loop exits without the service reporting healthy, `should_restart` stays `True`, and the next `reconcile()` will attempt to restart again, risking a restart loop. This path is untested.
- **Impact**: On slower machines, the unit could enter a restart loop.
- **Fix**: Add `time.sleep(1-2)` inside the loop, or replace the fixed-count loop with a tenacity `@retry` decorator.
- **Linter rule**: "Polling loop without sleep/delay" — mechanically checkable.

### 9. SSL verification disabled in REST API calls with `FIXME` comment
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/connect.py:124-128`
- **Evidence**:
  ```python
  # FIXME: Connect Manager should use the CA chain to verify its requests.
  warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)
  response = requests.request(..., verify=False, auth=auth, timeout=self.REQUEST_TIMEOUT, ...)
  ```
- **Impact**: A man-in-the-middle could intercept and spoof Connect REST API responses, including connector configurations and credentials.
- **Fix**: Pass `verify=ca_path` using the CA from the TLS context when `context.tls_enabled`.
- **Linter rule**: "`requests.request()` called with `verify=False`" — mechanically checkable.

### 10. `_download_plugin` has no timeout — potential hang on unreachable URL
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/connect.py:169`
- **Evidence**: `requests.get(url, stream=True)` with no `timeout`.
- **Impact**: A network partition or slow/failing plugin URL can hang the hook indefinitely, risking a Juju hook-timeout error.
- **Fix**: Add `timeout=30` (or similar) to `requests.get()`.
- **Linter rule**: "`requests.get()`/`requests.request()` called without a `timeout` argument" — mechanically checkable.

### 11. TLS SANs parsing is fragile and can silently miss certificate rotation
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/tls.py:218-235`
- **Evidence**:
  ```python
  for line in sans_lines:
      if "DNS" in line and "IP" in line:
          break
  sans_ip = []
  sans_dns = []
  for item in line.split(", "):
      san_type, san_value = item.split(":")
  ```
  If the OpenSSL output format differs, the loop can break on the wrong line. `item.split(":")` assumes exactly one `:`; an IPv6 address like `2001:db8::1` would split into more than two parts and raise `ValueError` (unobserved in practice).
- **Impact**: `sans_change_detected` could silently return `False` (empty sets compare equal), meaning no certificate renewal is triggered even when SANs have changed.
- **Fix**: Parse all lines unconditionally, or use `maxsplit=1` on the `:` split, with error handling.
- **Linter rule**: not established.

### 12. `kafkacl` dependency pulls from git `main` branch without a version pin
- **Severity**: medium
- **Kind**: bug
- **Where**: `pyproject.toml:36`
- **Evidence**: `kafkacl = { git = "https://github.com/canonical/kafkacl", branch = "main" }` — no revision or version constraint.
- **Impact**: A future commit to `main` could introduce a breaking change silently.
- **Fix**: Pin to a git revision SHA or version tag, or publish `kafkacl` to PyPI.
- **Linter rule**: not established.

### 13. `test_provider.py` does not cover the `PluginDownloadFailedError` path (issue #58 untested)
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_provider.py::test_integration_requested`
- **Evidence**: `charm.connect_manager` is replaced with a `MagicMock`, so `load_plugin_from_url` never raises `PluginDownloadFailedError`; the exception handler is never exercised.
- **Impact**: Issue #58 is not reproduced by any test — a future refactor removing `event.defer()` would not be caught.
- **Fix**: Add a test with `side_effect=PluginDownloadFailedError(...)` asserting the handler defers the event.
- **Linter rule**: not established.

### 14. Charm library uses deprecated `JujuVersion.from_environ()`
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/tls_certificates_interface/v3/tls_certificates.py:1585`, `lib/charms/data_platform_libs/v0/data_interfaces.py:995`
- **Evidence**: Both libraries call `JujuVersion.from_environ()`, emitting `DeprecationWarning` in tests; `self.model.juju_version` is the current API.
- **Impact**: Deprecated API may be removed in a future `ops` version, breaking the charm at runtime.
- **Fix**: Update to `self.model.juju_version`, or bump the vendored library versions.
- **Linter rule**: mechanically checkable (ruff/flake8 deprecation warnings).

### 15. `rest_port` config has no bounds validation
- **Severity**: medium
- **Kind**: bug
- **Where**: `config.yaml`, `src/core/structured_config.py:27`
- **Evidence**: `rest_port` is `type: int` in `config.yaml` with no `min`/`max`; `structured_config.py` declares `rest_port: int` with no validator. Observed: `rest_port=99999` accepted by Juju, `config-changed` completes without error, value written to `connect-distributed.properties` — the Connect service would reject it at startup.
- **Impact**: Operators get no feedback until the Connect service fails to start.
- **Fix**: Add `min: 1, max: 65535` to `rest_port` in `config.yaml`, or a pydantic validator.
- **Linter rule**: "Integer config option with no bounds in `config.yaml`" — mechanically checkable.

### 16. Only one action defined — no operator-facing actions for connector or user management
- **Severity**: medium
- **Kind**: ux
- **Where**: `actions.yaml`
- **Evidence**: Only `pre-upgrade-check` is defined. No actions for pausing/resuming connectors, listing connectors, managing users, reloading plugins, or manual TLS renewal.
- **Impact**: Operators must use the REST API or the `charmed-kafka` snap CLI directly for common tasks.
- **Fix**: Consider adding actions that wrap common REST API operations.
- **Linter rule**: not established.

### 17. `apply_backwards_compatibility_fixes` is a no-op stub with no tests
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/events/upgrade.py:112-115`
- **Evidence**:
  ```python
  def apply_backwards_compatibility_fixes(self, _: UpgradeGrantedEvent) -> None:
      """A range of functions needed for backwards compatibility."""
      logger.info("Applying upgrade fixes")
      pass
  ```
  No unit tests exist for the upgrade path at all; the integration test is broken (finding 6).
- **Impact**: The upgrade path is completely untested end-to-end.
- **Fix**: Add unit tests for the upgrade handler; implement the method if backward-compat fixes are ever needed.
- **Linter rule**: not established.

### 18. `_on_integration_requested` downloads plugin on non-leader units unnecessarily
- **Severity**: low
- **Kind**: performance
- **Where**: `src/events/provider.py:67-77`
- **Evidence**: The leadership check comes after the plugin download:
  ```python
  if client.plugin_url != PLUGIN_URL_NOT_REQUIRED:
      try:
          self.charm.connect_manager.load_plugin_from_url(...)
      except PluginDownloadFailedError as e:
          logger.error(...)
          return  # no defer — see finding 3
  if not self.charm.unit.is_leader():
      return
  ```
  On an N-unit cluster, all N units may download the plugin even though only the leader creates credentials.
- **Impact**: Wasted network I/O and disk usage on follower units.
- **Fix**: Move the leadership check before the plugin download.
- **Linter rule**: not established.

### 19. Non-leader units don't clear `peer_workers.tls` on TLS relation broken
- **Severity**: low
- **Kind**: bug
- **Where**: `src/events/tls.py::_tls_relation_broken`
- **Evidence**:
  ```python
  def _tls_relation_broken(self, _) -> None:
      self.charm.context.worker_unit.update(dict.fromkeys(self.unit_tls_context.KEYS, ""))
      self.charm.tls_manager.remove_stores()
      if not self.charm.unit.is_leader():
          return
      self.charm.context.peer_workers.update({"tls": ""})
      self.charm.on.config_changed.emit()
  ```
  Non-leader units clear their own TLS state and stores but never clear `peer_workers.tls`.
- **Impact**: In a multi-unit cluster, `peer_workers.tls` may remain `enabled` even after all units clear TLS, if the non-leader loses the relation.
- **Fix**: Move `peer_workers.update({"tls": ""})` outside the leader check.
- **Linter rule**: not established.

### 20. `test_user_secrets.py::test_remove_credentials` does not assert removed users are absent
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_user_secrets.py::test_remove_credentials`
- **Evidence**: The test checks `len(charm.auth_manager.credentials) == 1` and that admin is present, but never asserts `user1`/`user2` are absent.
- **Impact**: A regression that removed the `remove_user` loop would still pass this test.
- **Fix**: Add `assert "user1" not in charm.auth_manager.credentials` and similarly for `user2`.
- **Linter rule**: not established.

### 21. `metadata.yaml` uses deprecated `series` attribute
- **Severity**: low
- **Kind**: lint
- **Where**: `metadata.yaml:18`
- **Evidence**: `series: - noble` — deprecated in Juju 4.0.
- **Impact**: Charm will fail to load in Juju 4.x if the attribute is removed from the schema.
- **Fix**: Remove the `series` key.
- **Linter rule**: `charmcraft analyze` already flags this.

### 22. Config option naming is inconsistent (hyphen vs underscore)
- **Severity**: low
- **Kind**: lint
- **Where**: `config.yaml`
- **Evidence**: `system-users` uses hyphens while `exactly_once_source_support`, `key_converter`, `log_level`, `rest_port`, `value_converter` use underscores. `charmcraft analyze` warns about this.
- **Impact**: Operator confusion; inconsistent with ecosystem conventions.
- **Fix**: Standardize on underscores and document the mapping.
- **Linter rule**: `charmcraft analyze` already flags this.

### 23. Stale comment claims `removed` has no functionality, but it is implemented
- **Severity**: nit
- **Kind**: docs
- **Where**: `src/events/user_secrets.py:57-58`
- **Evidence**: Comment `# removed does not have functionality right now, since we only allow internal user.` sits above the `removed` set comprehension, but the `remove_user` loop at line 66 implements exactly that functionality.
- **Impact**: Misleading to anyone reading the source.
- **Fix**: Remove the stale comment.
- **Linter rule**: not established.

## Worth copying

- **`TypedCharmBase[CharmConfig]`** with pydantic structured config and validators — clean and type-safe
- **Context objects** (`KafkaClientContext`, `ConnectClientContext`, `TLSContext`, `WorkerUnitContext`, `PeerWorkersContext`) — well-separated concerns with clear `status` property
- **`reconcile()`** pattern in `charm.py` — orchestrates all hot-path operations idempotently
- **`HealthResponse`** wrapper with boolean coercion for clean health checks
- **`PROPERTIES_BLACKLIST`** approach for config-to-properties translation — clean separation
- **`RollingOpsManager`** for coordinated restarts across the cluster — proven library, well-integrated
- **Upgrade stack** built from unit IDs with proper leader-first ordering via `data_platform_libs`
- **`snap hold`** after install to prevent automatic updates (good for production)
- **Comprehensive COS alert rules** for Kafka Connect (JVM memory, task failures, unassigned connectors, restart rates, commit failures)
- **`pending_inactive_statuses`** list — clean way to collect statuses across event handlers

## Common-practice notes

- **Layout**: Standard `src/{events,managers,core}/` + `lib/charms/` layout, matches ecosystem convention.
- **Build**: Uses the `poetry` plugin in `charmcraft.yaml` with a custom `poetry-deps` part that installs poetry via `uv` — more complex than the standard `charm` plugin but avoids `pip install` version issues. This causes `charmcraft analyze` to report an entrypoint ERROR (false positive; the charm works when deployed from charmhub) and a framework false positive ("charm is not based on the operator framework").
- **Charm libraries**: No owned libraries in `lib/charms/kafka_connect/`. Uses external `data_platform_libs/v0`, `grafana_agent/v0`, `tls_certificates_interface/v3`, `rolling_ops/v0`, `operator_libs_linux/v2`. Both `data_platform_libs/v0` and `tls_certificates_interface/v3` use the deprecated `JujuVersion.from_environ()` API (finding 14); both are v0 libraries, pinned transitively.
- **Testing**: `ops-scenario` `Context` testing with state transitions; `pytest-mock`; `jubilant`/`jubilant-adapters` for integration test assertions.
- **Python**: Targets 3.10+, pyright with type stubs, pydantic 1.x (not 2.x, due to `grafana_agent` lib constraint).
- **Storage**: `plugins` storage type at `/var/snap/charmed-kafka/common/var/lib/connect` — correctly placed in snap common data dir.
- **Peer relations**: Three peer relations (`restart`, `worker`, `upgrade`) with meaningful interfaces — unusual but intentional.
- **No `StoredState`**: correctly avoided; all state is derived from config, relations, or the workload.
- **ops-scenario default peer relation includes `private-address`**: the test framework defaults to `private-address: 192.0.2.0`, which real Juju 4.x does not set — root cause of finding 2.
- **Test runner caveat**: `poetry run pytest` fails due to `PYTHONPATH`; use `PYTHONPATH=lib:src poetry run python -m pytest tests/unit/` from the repo root.

## Tests

- **Unit tests**: 75/75 pass in ~2.2s (`PYTHONPATH=lib:src /path/to/venv/bin/python -m pytest tests/unit/`). Coverage 81% overall. `managers/tls.py` 27% — entire certificate install/rotation path untested. `workload.py` 63%. `events/provider.py` 82% — `PluginDownloadFailedError` path untested.
- **Integration tests**: Split by feature via pytest markers, using `jubilant` for relation assertions. Requires a Kafka KRaft cluster; not run in this review.
- **Upgrade tests**: Broken (issue #51) — fixture ignores packed charms.
- **Terraform tests**: `integration-terraform` tests the terraform module; not run.
- **Kafka relation integration**: Not exercised — the `kafka` charm (charmhub rev 262) requires a multi-node KRaft controller cluster that could not be provisioned in this environment; the full blocked → active lifecycle via Kafka relation was not observed.
- **Coverage detail** (from the coverage report, unverified line numbers marked `(unverified)`):
  - `src/charm.py`: 93%
  - `src/core/models.py`: 87%
  - `src/core/structured_config.py`: 100% (the `None`-crash path is not exercised despite full line coverage — the branch is reached only via a config value pydantic never sees in tests)
  - `src/core/workload.py`: 89%
  - `src/events/connect.py`: 86%
  - `src/events/kafka.py`: 79% — missing TLS import on kafka relation
  - `src/events/provider.py`: 82%
  - `src/events/tls.py`: 83%
  - `src/events/upgrade.py`: 93%
  - `src/events/user_secrets.py`: 94%
  - `src/managers/auth.py`: 100%
  - `src/managers/config.py`: 94%
  - `src/managers/connect.py`: 92%
  - `src/managers/kafka.py`: 97%
  - `src/managers/tls.py`: 27%
  - `src/workload.py`: 63%
- **Critical untested paths**: `internal_address` on a peer relation without `private-address` (the Juju 4.x scenario); `PluginDownloadFailedError` in `_on_integration_requested`; `system_users_secret_validator` with `None`; `tls_manager.configure()` and the full certificate lifecycle; `_restart_callback`'s unslept polling loop; `get_current_sans()` IPv6 parsing; `workload.restart/stop/start` snap calls and `exec` error paths; `_on_config_changed` defer path when the container cannot connect.

## Docs

- **README.md**: Comprehensive — covers snap install, plugin management, user management via secrets, TLS configuration, COS integration, relations, with code examples matching observed behaviour.
- **CONTRIBUTING.md**: Explains dev setup (poetry, tox), testing approach, code style.
- **charmcraft.yaml**: No doc part — no rendered docs hosted on charmhub; the `docs` URL in `metadata.yaml` points to Discourse.
- **Terraform module**: exists at `terraform/`, confirming a real-world integration path.

## Open questions

1. Confirmed that Juju 4.0.12 on LXD does not set `private-address` in peer relations — only `ingress-address` — root-causing findings 1 and 2.
2. The permanent error state on TLS relation removal (`certificates-relation-broken` never dispatched) needs upstream Juju/ops confirmation of whether this is charm-side or a broader ops-framework gap.
3. Kafka integration could not be exercised because Kafka 4.x requires a multi-node KRaft cluster; the full blocked → active transition via the Kafka relation is unverified.
4. IPv6 SANs parsing crash (finding 11) is theoretical — not observed in practice.
5. The `_restart_callback` polling-loop risk (finding 8) has not been observed to fail in practice; the timing window is theoretical given the tenacity retry budget in `workload.active()`.
6. `kafkacl`'s API stability (finding 12) is unverified — no incident observed, but the dependency is unpinned.
