# kafka-connect-k8s

A well-architected Kafka Connect charm from Canonical's Data Platform team, built on `TypedCharmBase` with clean manager/event/model separation. It deploys and operates correctly in practice — Kafka integration, TLS on the REST API, HTTP Basic auth, and plugin management all work — but the most serious finding is a config-validation-at-`__init__` pattern that can crash the charm into an unrecoverable error loop when an invalid config value (e.g. `log_level=TRACE`) bypasses Juju's CLI validation. A maintainer should fix that first, then address the unbounded status-accumulation bug and the bare `except` in version detection; all issues are concentrated in a handful of files and are straightforward to fix.

| | |
|---|---|
| Repo | canonical/kafka-connect-k8s-operator @ `de000b6` (2026-07-08) |
| Charms | kafka-connect-k8s, integrator (test-only) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5) and concierge-k8s-3 (Juju 3.6.25), `latest/edge` rev 17 (charmhub), with `kafka-k8s` 3/edge rev 83 |
| Reviewed | 2026-07-31 |

## What it does

Deploys Apache Kafka Connect 3.9.0 in distributed mode on Kubernetes, inside a `ghcr.io/canonical/charmed-kafka` OCI image managed by Pebble. Provides a `connect-client` interface for integrator charms to register connectors and requires a `kafka-client` relation to a Kafka cluster. Supports TLS on the REST API (via `tls-certificates`), HTTP Basic auth (via `PropertyFileLoginModule`), plugin management via `juju attach-resource` and integrator-provided URLs, in-place upgrades via `DataUpgrade` with StatefulSet partition control, and observability via JMX Prometheus exporter, Grafana dashboards, and Loki log forwarding.

## Deployment log

### Juju 4.0.5 (concierge-k8s-4, model rv-kc-deep4)
```bash
juju add-model rv-kc-deep4
juju deploy kafka-k8s --channel 3/edge -n 3 --config roles="broker,controller" --trust
juju deploy kafka-connect-k8s --channel latest/edge --trust
juju integrate kafka-connect-k8s kafka-k8s
```
Reached `active/idle` in ~6 minutes. Three restarts in quick succession during initial startup (04:39:29, 04:40:22, 04:40:33). Status progression: `agent initialising` → `maintenance: installing charm software` → `blocked: Application needs Kafka client relation` → `waiting: Waiting for Kafka cluster credentials` → `Awaiting restart operation` → `Executing restart operation` → `active`. Juju 4 keeps the workload `waiting` until charm code runs.

### Juju 3.6.25 (concierge-k8s-3, model rv-kc-deep3)
```bash
juju add-model rv-kc-deep3
juju deploy kafka-k8s --channel 3/edge -n 3 --config roles="broker,controller" --trust
juju deploy kafka-connect-k8s --channel latest/edge --trust
juju integrate kafka-connect-k8s kafka-k8s
```
Reached `active/idle` in ~4 minutes, faster than Juju 4. Only two restarts observed (04:38:38, 04:38:59), vs three on Juju 4. Juju 3.6 shows the workload as `running` even before the install hook completes — a Juju version display difference, not a charm bug.

### Config changes and failure injections

```bash
# Invalid profile — Juju CLI does NOT reject this, charm crashes at init
juju config kafka-connect-k8s profile=invalid
# Unit: error: "hook failed: config-changed" — app status: "active" (stale)
# Recovery: juju config kafka-connect-k8s profile=production; juju resolved

# Invalid log_level — Juju CLI does NOT reject this, charm enters total crash loop
juju config kafka-connect-k8s log_level=TRACE
# 'TRACE' is not in the LogLevel Literal; every hook fails at __init__ with a
# pydantic ValidationError. Charm is broken until config is fixed externally.
# Observed 4-5 retries of certificates-relation-created before eventual recovery.

# Valid config change — triggers restart as expected
juju config kafka-connect-k8s log_level=DEBUG
# Status: "Beginning rolling restart" → "Executing restart operation" → "active"

# Kill workload process — Pebble recovers
kubectl exec ... -c kafka-connect -- kill -9 $(pgrep -f connect-distributed)
# Pebble restarts within seconds, charm stays active. Correct.

# Remove kafka-client relation — stops service, shows blocked
juju remove-relation kafka-connect-k8s kafka-k8s
# Unit: blocked "Application needs Kafka client relation"
# Service: connect-distributed stopped (pebble: inactive)
# Re-integrate: transitions to "Waiting for Kafka cluster credentials", recovers

# TLS integration
juju deploy self-signed-certificates --channel edge
juju integrate kafka-connect-k8s self-signed-certificates
# Juju 3.6: works smoothly, TLS active in ~90s
# Juju 4: transient keystore validation failure; connect-distributed entered Pebble
#   backoff with "java.lang.IllegalStateException: /etc/connect/keystore.p12 is not
#   a valid keystore". Recovered after a few Pebble retries (~2 minutes). Keystore
#   file existed but was possibly incompletely written when the service first read it.

# TLS removal
juju remove-relation kafka-connect-k8s self-signed-certificates
# Both Juju versions: clean teardown, all TLS files removed, no bundle.pem artifact
# Reverted to HTTP, REST API working correctly

# Scale up (Juju 3.6) — new unit gets TLS certs correctly
juju scale-application kafka-connect-k8s 2
# Unit 1 comes up with TLS files and keystore. BUT bundle.pem is 0 bytes.
# Scale back down works cleanly.

# Actions
juju run kafka-connect-k8s/0 pre-upgrade-check   # succeeds on both
juju run kafka-connect-k8s/0 resume-upgrade      # correctly fails

# User secrets
juju add-secret my-auth admin=testpass123
juju grant-secret my-auth kafka-connect-k8s
juju config kafka-connect-k8s system-users=secret:d9lo3dfmp25c765s7bu0
# Password file updated correctly. REST API auth with new password works.
```

## Observed behaviour

- **Multiple restarts at startup**: 3 on Juju 4, 2 on Juju 3.6. The `reconcile()` diff logic on the worker properties file detects differences on the initial write, causing the rolling-ops restart callback to fire multiple times. The difference between Juju versions may be timing of relation-changed hooks (unverified).
- **REST API listener binds to the K8s service hostname**, not `0.0.0.0` or localhost, by design (`listeners` uses `internal_address`). `curl localhost:8083` fails inside the container — only the FQDN works.
- **Java 18 in the deployed image** (rev 17 on ubuntu@22.04), while the local source targets Java 21 (pebble layer specifies `JAVA_HOME: /usr/lib/jvm/java-21-openjdk-amd64`). Base-image mismatch between `latest/edge` (22.04) and the source `charmcraft.yaml` (24.04). The 4/edge track (rev 19, 24.04) exists but was not tested.
- **Workload memory: 386 MiB** (`kubectl top pod`), reasonable for a single Connect worker.
- **TLS keystore transient failure on Juju 4**: `set_keystore()` wrote a keystore that Jetty rejected as invalid on first read, causing a Pebble backoff loop. Recovered after a few restarts (~2 minutes). Keystore file was present (4003 bytes, correct ownership `kafka:kafka 770`) and readable with the configured password after recovery — suggests a write-vs-read race, not corrupt content.
- **0-byte `bundle.pem` on scale-up**: when a new unit is added while TLS is enabled, `set_bundle()` writes an empty string because `self.tls_context.bundle` is empty for a unit that hasn't yet received the full TLS context. Confirmed on Juju 3.6 unit 1. An earlier 0-byte `bundle.pem` after TLS removal was not reproduced this round — that cleanup was complete.
- **App-level status stale during unit errors**: when a hook fails (invalid config), the unit shows `error` but the app shows `active`. The `pending_inactive_statuses` list never clears, so the last `Status.ACTIVE` keeps getting reported to `collect_app_status`.
- **Invalid config crashes charm at `__init__`**: `log_level=TRACE` or `profile=invalid` pass Juju CLI validation (they are plain strings; the `Literal` check only happens in-charm via pydantic). The charm crashes in `__init__` at `src/charm.py:65` (`self.workload = Workload(...)`) before any hook handler runs. Every hook, including `config-changed`, fails, and the charm sits in a tight error loop until config is fixed externally.
- **Juju 4 vs Juju 3.6 workload status reporting**: Juju 4 tracks `waiting` as the initial workload state with more granular messages; Juju 3.6 shows `running` once Pebble starts, even before charm hooks fire. The charm's own status messages are identical across versions.

## Findings

### Config validation at `__init__` crashes charm into unrecoverable error loop
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:65`, `src/core/structured_config.py:27-45`
- **Evidence**: Setting `juju config kafka-connect-k8s log_level=TRACE` causes:
  ```
  pydantic.error_wrappers.ValidationError: 1 validation error for CharmConfig
    unexpected value; permitted: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
  ```
  This occurs in `CharmConfig.__init__()`, called from `TypedCharmBase.__init__()` at `src/charm.py:65`. Every subsequent hook fails at charm construction. Observed 4-5 consecutive hook failures on Juju 4 before recovery once config was fixed externally. Juju's CLI accepts `TRACE` because the config type is `string` — there is no Juju-level constraint for `Literal` types. The same failure mode was reproduced with `profile=invalid`.
- **Impact**: An operator who sets an invalid config value can brick the charm; it stays in an error loop until they run another `juju config` to fix it.
- **Fix**: Move config validation to a `config-changed` handler instead of `__init__`. On invalid config, set `BlockedStatus` with guidance instead of crashing. Alternatively, add `pre=True` validators that coerce invalid values to safe defaults — the existing `blank_string` validator at `structured_config.py:44` already does this for empty strings and the pattern should be extended.
- **Linter rule**: "Charm `__init__` must not raise on config validation" — flag any pydantic model instantiation in `__init__` that can raise `ValidationError`.

### Unbounded `pending_inactive_statuses` list causes stale/cumulative app status
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:62,150,155`
- **Evidence**:
  ```python
  self.pending_inactive_statuses: list[Status] = []   # line 62
  self.pending_inactive_statuses.append(key)            # line 150
  for status in self.pending_inactive_statuses + [workload_status]:  # line 155
      event.add_status(status.value.status)
  ```
  The list is only ever appended to, never cleared. Every `collect-status` event reports all statuses seen during the charm process's lifetime. Confirmed on Juju 4: app status showed `active` while the unit was `error: hook failed: config-changed`.
- **Impact**: A charm that transitioned `MISSING_KAFKA` → `NO_KAFKA_CREDENTIALS` → `ACTIVE` reports all three on every `collect-status` event, and when a hook error occurs the app-level status doesn't reflect it because the historical `ACTIVE` persists.
- **Fix**: Clear the list at the start of `_on_collect_status`, or recompute status fresh from current conditions rather than accumulating history.
- **Linter rule**: "`_on_collect_status` handler must not rely on mutable state that is only appended to" — partially mechanically checkable.

### Bare `except:` in `get_version()` swallows all exceptions
- **Severity**: high
- **Kind**: bug
- **Where**: `src/core/workload.py:216`
- **Evidence**:
  ```python
  try:
      version = re.split(r"[\s\-]", self.run_bin_command("topics", ["--version"]))[0]
  except:  # noqa: E722
      version = ""
  ```
- **Impact**: `SystemExit` and `KeyboardInterrupt` are silently swallowed. Even normal exceptions produce an empty version string with no log entry.
- **Fix**: Catch a specific exception type (e.g. `(CalledProcessError, ExecError)`) and log a warning, or at minimum use `except Exception:`.
- **Linter rule**: "No bare `except:` clauses" — mechanically checkable (`ruff` E722).

### TLS REST API requests use `verify=False` with no CA validation
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/connect.py:125-129`
- **Evidence**:
  ```python
  with warnings.catch_warnings():
      # FIXME: Connect Manager should use the CA chain to verify its requests.
      warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)
      try:
          response = requests.request(method, url, verify=False, auth=auth, ...)
  ```
  The code carries a FIXME acknowledging this.
- **Impact**: All internal REST API calls skip TLS certificate verification. A MITM on the pod network could intercept Connect API calls; this would fail a security audit.
- **Fix**: Use the CA certificate from the TLS context to build a `requests.Session` with proper verification.
- **Linter rule**: "`requests.request(..., verify=False)` requires a documented justification" — mechanically checkable.

### `tls_manager.py` has 27% test coverage
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/managers/tls.py`
- **Evidence**: 148 statements, 100 missed; nearly all methods have zero unit test coverage. This gap is material given the live observation of a keystore validation failure during TLS setup.
- **Fix**: Add unit tests with mocked `self.workload.exec`/`self.workload.write` covering keystore creation, truststore population, cert import/removal, and SAN change detection.

### Config diff mechanism uses set symmetric difference, causing false-positive restarts
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:198-201`
- **Evidence**:
  ```python
  current_config = set(self.workload.read(self.workload.paths.worker_properties))
  diff = set(self.config_manager.properties) ^ current_config
  if diff:
      self.context.worker_unit.should_restart = True
  ```
  Converting the properties list to a set loses ordering and de-duplicates identical lines (e.g. repeated SASL JAAS config lines for worker/consumer/producer). Comment lines from `PROPERTIES_BLACKLIST` differ between write and read on every reconcile, triggering restarts.
- **Impact**: Observed 3 restarts on Juju 4 and 2 on Juju 3.6 during initial startup; any config change, even one that shouldn't require a restart, can trigger a full one.
- **Fix**: Parse the properties file into a dict and compare non-comment keys only.
- **Linter rule**: not mechanically checkable.

### Transient keystore validation failure on TLS setup (Juju 4)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/tls.py:124-132` (`set_keystore`)
- **Evidence**: After TLS integration on Juju 4, connect-distributed entered a Pebble backoff loop:
  ```
  java.lang.IllegalStateException: /etc/connect/keystore.p12 is not a valid keystore
  at org.eclipse.jetty.util.security.CertificateUtils.getKeyStore(CertificateUtils.java:50)
  ```
  The keystore file existed (4003 bytes, `kafka:kafka 770`) and was readable with the configured password. The service recovered after ~2 minutes of Pebble retries, consistent with a race between file-write completion and the service reading the keystore.
- **Impact**: TLS setup relies on Pebble retry luck rather than being reliable; a new operator seeing the transient failure could wrongly conclude TLS is broken.
- **Fix**: After writing keystore/truststore files in `set_keystore()`/`set_truststore()`, ensure they are flushed (e.g. `self.workload.exec(['sync'])`) before triggering a service restart, or write TLS files before applying service configuration.
- **Linter rule**: not mechanically checkable.

### Integration test for upgrade is disabled
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `.github/workflows/ci.yaml:66`
- **Evidence**: `# FIXME: re-enable after new base is released` / `# - integration-upgrade`. `ConnectUpgrade` has only 41% coverage.
- **Impact**: The 4/edge track (rev 19, 24.04) exists but the upgrade path from rev 17 (22.04) to rev 19 (24.04) is untested.
- **Fix**: Enable the upgrade integration test, or test the cross-base upgrade explicitly.

### 0-byte `bundle.pem` on scale-up of a new TLS unit
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/tls.py:100-106` (`set_bundle`)
- **Evidence**: On Juju 3.6, after scaling to 2 units with TLS active, the new unit's `/etc/connect/bundle.pem` was 0 bytes:
  ```
  -rw-r--r-- 1 root  root     0 Jul 30 16:52 bundle.pem
  ```
  `set_bundle()` writes `"\n".join(self.tls_context.bundle)`, which is empty because the new unit may not have received the full TLS chain before `configure()` runs.
- **Impact**: Benign in practice (the service falls back to `server.pem` when there's no chain) but leaves a silent, potentially confusing artifact.
- **Fix**: Guard `set_bundle()` with `if self.tls_context.bundle:`, or skip writing when the bundle is empty.
- **Linter rule**: not mechanically checkable.

### `_request()` wraps all exceptions in a generic `Exception`, losing error type
- **Severity**: low
- **Kind**: ux
- **Where**: `src/managers/connect.py:130-132`
- **Evidence**:
  ```python
  except Exception as e:
      raise Exception(f"Connect API call /{api} failed: {e}")
  ```
  The `health_check` retry uses `retry_if_exception(lambda _: True)`, retrying on everything including an HTTP 401.
- **Impact**: Callers cannot distinguish transient network errors from permanent configuration errors.
- **Fix**: Re-raise the original exception, or define a custom exception hierarchy.
- **Linter rule**: not mechanically checkable.

### `PROPERTIES_BLACKLIST` writes commented lines that trigger unnecessary restarts
- **Severity**: low
- **Kind**: performance
- **Where**: `src/managers/config.py:38-43,105`
- **Evidence**:
  ```python
  translated_key = key.replace("_", ".") if key not in PROPERTIES_BLACKLIST else f"# {key}"
  ```
  Blacklisted config options are written as comments, which change on config update and are picked up by the set-diff mechanism, triggering a full restart.
- **Impact**: Same restart-amplification effect as the config-diff finding above.
- **Fix**: Omit blacklisted properties entirely rather than writing them as comments.
- **Linter rule**: not mechanically checkable.

### `get_version` exception branch has zero test coverage
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/core/workload.py:216`
- **Evidence**: The bare `except:` branch has 0% branch coverage; no test exercises the failure path.
- **Fix**: Add a unit test that mocks `run_bin_command` to raise.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **`TypedCharmBase` with structured config** (`src/charm.py:55`, `src/core/structured_config.py`): pydantic `BaseConfigModel` for config validation, including a custom validator for secret IDs (`SECRET_REGEX`). The pattern is good, but placing validation in `__init__` rather than a handler is the critical finding above.
- **Clean manager separation** (`src/managers/`): TLS, authentication, config, and connect operations are each in their own manager class, accepting context and workload as dependencies.
- **Context model pattern** (`src/core/models.py`): `Context` aggregates relation data into typed properties, each with its own `status`/`ready` properties, simplifying reconciliation logic.
- **`WorkloadBase` abstraction** (`src/core/workload.py`): abstract interface for workload operations with a K8s-specific implementation (`src/workload.py`), clean prep for a future machine charm.
- **Integration tests using `jubilant`** (`tests/integration/`): `jubilant` + `jubilant-adapters` instead of `pytest-operator`, testing real behaviour — socket checks, authenticated REST API requests, TLS certificate extraction, plugin downloads.
- **Rolling ops via `rolling_ops` library** (`src/charm.py:92`): `RollingOpsManager` with a `restart` peer relation for safe rolling restarts.
- **`DataUpgrade` for in-place upgrades** (`src/events/upgrade.py`): StatefulSet partition management for controlled rolling upgrades.
- **Auth via `PropertyFileLoginModule`** (`src/managers/auth.py`): correct file ownership (`kafka:kafka`, mode 770); credentials updated atomically by loading, merging, and writing back.

## Common-practice notes

- **Follows canonical Data Platform patterns**: `TypedCharmBase`, structured config, `DataPeerData`/`DataPeerUnitData`, `KafkaRequirerData`/`KafkaConnectProviderData`, `DataUpgrade`.
- **Drifts from ecosystem**: charm source targets 24.04 (`charmcraft.yaml`) but the deployed `latest/edge` revision 17 is on 22.04 with Java 18, while the source pebble layer specifies `JAVA_HOME: /usr/lib/jvm/java-21-openjdk-amd64`. The `4/edge` track (rev 19, 24.04) is newer and untested here.
- **Library versions**: uses `data_platform_libs/v0/data_interfaces.py` (not `v1`), `tls_certificates_interface/v3/tls_certificates.py` (current).
- **`metadata.yaml`**: `docs` field points to the Kafka docs URL, not Kafka Connect docs; `description` field is the placeholder string `"Description"`, never filled in.
- **No terraform module in the repo**: referenced in git log but not present locally.

## Tests

- **Unit tests**: 65 passed, 9 skipped, via `tox -e unit`. Coverage 77%. Key gaps: `tls_manager.py` (27%), `upgrade.py` (41%), `workload.py` (59%), `kafka.py` (76%).
- **Integration tests**: 7 suites, using `jubilant`. The upgrade integration test is disabled in CI.
- **Lint**: 0 pyright errors, 0 warnings; `codespell`, `ruff`, `black` all pass via `tox -e lint`.
- **CI**: runs on `self-hosted-linux-amd64-noble-medium` runners; nightly runs include unstable-tagged tests.

## Docs

- **README**: comprehensive. Monitoring section references `micro:admin/cos.loki` for Loki, working through the `loki_push_api` interface, matching observed behaviour.
- **Charmhub description**: `metadata.yaml` has `"Description"` as the description — essentially empty.
- **No `docs/` directory**: documentation lives on Discourse, the standard Data Platform approach.
- **CONTRIBUTING.md**: well-structured, covers build, deploy, develop, test, and docs workflows.

## Open questions

- Is the transient keystore failure on Juju 4 a race condition or an actual TLS configuration bug? The keystore was readable with the configured password after recovery, suggesting a write-vs-read race; would need a `sync` call or ordering change in `configure()` to confirm.
- Does `sans_change_detected` work correctly for the first unit after scale-up? Not tested directly; the logic in `build_sans()` looks correct on inspection but is unverified.
- Why does `_on_kafka_pebble_ready_upgrade` (`src/events/upgrade.py:62`) use `or` rather than `and`? `if not self.charm.context.ready or self.idle: return` — the accompanying comment ("ensure pebble-ready only fires after normal peer-relation-driven server init") suggests the intent may be to proceed only when both ready AND not idle.
- Why is `KafkaManager.health_check()` defined but only called from `_on_relation_created` (`kafka.py:60`) and never during reconciliation? The reconciliation path trusts relation data alone rather than checking cluster health.
