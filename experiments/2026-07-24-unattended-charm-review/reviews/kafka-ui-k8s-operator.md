# kafka-ui-k8s

A cleanly architected k8s charm for Kafbat's Kafka UI (v1.3.0), wrapping the upstream JAR in a Charmed OCI image with Pebble. All five integrations were tested and working (kafka, karapace, kafka-connect, traefik, TLS) across 5 deployments and 4 models, plus scale-up/down and failure-injection lifecycle tests. Juju 4.0 compatible in standalone mode; full-stack testing on 4.0 is blocked by an upstream kafka-k8s bug, not this charm. The architecture is solid, but there are real defects: an unbound-variable crash path in `get_current_sans`, zero unit test coverage, a `tox -e static` that silently does nothing (masking 40 real pyright findings), a `schemaRegistry: http://` config artifact when Karapace isn't related, and silent swallowing of invalid/permission-denied secrets. First fixes: add a Harness-based unit test suite around config generation and status flow (this alone would have caught the schemaRegistry bug), wire pyright into `tox -e static`, and fix the unbound `line` variable in `get_current_sans`.

| | |
|---|---|
| Repo | canonical/kafka-ui-k8s-operator @ `335fea0` (2026-03-13) |
| Charms | kafka-ui-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3, latest/edge rev 8 (=HEAD); 5 deployments across 4 models: basic stack (rv-kui-36), deep stack with TLS+Karapace (rv-kui-deep), kafka-connect (rv-connect), Juju 4.0 standalone (rv-juju4), stale-status recovery verification (rv-stale-status) |
| Reviewed | 2026-08-10 |

## What it does

Deploys [Kafbat's Kafka UI](https://github.com/kafbat/kafka-ui) (v1.3.0) as a single-container pod on Kubernetes via the canonical `charmed-kafka-ui` OCI image. The charm:

- Sets up a Spring Boot webapp on port 8080 behind Pebble
- Integrates with `kafka-k8s` (required), `karapace-k8s` / `kafka-connect-k8s` (optional) via the data-platform library client interfaces
- Supports TLS on the Kafka, Karapace, and Kafka Connect client connections via a `tls-certificates` relation, importing remote CAs into a JKS truststore
- Exposes the UI through `traefik-k8s` ingress (required) with a context path `/<model>-<app>`
- Manages the admin password automatically, stored as a Juju secret on the peer relation, with optional rotation via the `system-users` config pointing to a Juju secret
- Provides Prometheus metrics on port 9101

## Deployment log

### Attempt 1 — Juju 4.0 / concierge-k8s-4 (FAILED)

```
juju add-model rv-kafka-ui --controller concierge-k8s-4
juju deploy kafka-ui-k8s --channel latest/edge --trust
juju deploy kafka-k8s kafka --channel 4/edge --trust --config "roles=broker,controller" -n 1
juju deploy traefik-k8s --channel 1.0/stable --trust
juju integrate kafka-ui-k8s traefik-k8s
juju integrate kafka-ui-k8s kafka
```

kafka's `kafka-client-relation-created` hook repeatedly failed with `OSError: [Errno 19] No such device` in `update_peer_ip_address` (`core/models.py:345`). This is a kafka-k8s bug under Juju 4.0, not kafka-ui-k8s. Destroyed.

### Attempt 2 — Juju 3.6 / concierge-k8s-3 (basic deploy, first review)

```
juju add-model rv-kui-36 --controller concierge-k8s-3
juju deploy kafka-ui-k8s kui --channel latest/edge --trust
juju deploy kafka-k8s kafka --channel 4/edge --trust --config "roles=broker,controller" -n 1
juju deploy traefik-k8s traefik --channel 1.0/stable --trust
juju integrate kui traefik
juju integrate kui kafka
```

Active/idle in ~4 minutes. Basic lifecycle tests passed (relation remove/re-add, kill workload, bad secret injection, scale to 2 and back).

### Attempt 3 — Juju 4.0 / concierge-k8s-4 (standalone, no kafka)

```
juju add-model rv-juju4 --controller concierge-k8s-4
juju deploy kafka-ui-k8s kui --channel latest/edge --trust
```

kafka-ui-k8s deployed and initialized correctly on Juju 4.0. Status: blocked "application needs Kafka client relation". Pebble service running, config file written correctly with admin password and context-path `/rv-juju4-kui`. The application fails to start due to empty bootstrap servers (expected with no kafka relation), but the charm correctly reports blocked status via `health_check`. Two Juju 4.0 differences observed: (1) the Pebble plan shows `override: replace` instead of the charm's intended `override: merge` — likely the OCI image has no pre-existing layer for the service; (2) the Pebble environment includes `JAVA_HOME` and `KAFKA_UI_CONFIG` from the image metadata, which the charm does not set. Destroyed.

### Attempt 4 — Juju 3.6 / concierge-k8s-3 (kafka-connect-k8s integration)

```
juju add-model rv-connect --controller concierge-k8s-3
juju deploy kafka-ui-k8s kui --channel latest/edge --trust
juju deploy kafka-k8s kafka --channel 4/edge --trust --config "roles=broker,controller" -n 1
juju deploy traefik-k8s traefik --channel 1.0/stable --trust
juju deploy kafka-connect-k8s connect --channel latest/edge --trust
juju integrate connect kafka
juju integrate kui kafka
juju integrate kui traefik
juju integrate kui connect
```

All apps reached active/idle. kafka-connect integration correctly populated `kafka-connect` section in the generated config with `address: http://connect-0.connect-endpoints:8083`, username, and password from the DPE relation. After dropping the `connect-client` relation, the `kafka-connect` section was cleanly removed from the config. Password rotation via a valid `system-users` secret also worked correctly: the admin password in the live config changed to the new value.

### Attempt 5 — Juju 3.6 / concierge-k8s-3 (deep review with TLS, Karapace, scale)

```
juju add-model rv-kui-deep --controller concierge-k8s-3
juju deploy kafka-ui-k8s kui --channel latest/edge --trust
juju deploy kafka-k8s kafka --channel 4/edge --trust --config "roles=broker,controller" -n 1
juju deploy traefik-k8s traefik --channel 1.0/stable --trust
juju deploy self-signed-certificates ssc
juju deploy karapace-k8s karapace --channel latest/edge --trust
juju integrate kui traefik
juju integrate kui kafka
juju integrate kui ssc
juju integrate kafka:certificates ssc:certificates
juju integrate karapace:kafka kafka:kafka-client
juju integrate karapace:certificates ssc:certificates
```

Initial observation: kui stayed blocked ("application needs Kafka client relation") even after kafka reached active. kafka-client relation data was present on the Kafka side, but the `kafka-client-relation-changed` hook had already fired before the data was ready. A manual config change (`juju config kui kubernetes-ingress-allow-http=true`) re-triggered config-changed and kui became active. This is a DPE-library timing artefact; the `update_status → config_changed.emit()` safety net at `src/charm.py:116` catches it within 5 minutes (90s in the test config).

After triggering config, full stack active. Then integrated kui↔karapace (`juju integrate kui karapace`): schema registry endpoint populated correctly in the generated config.

### Lifecycle and failure tests (deep review)

| Test | Result | Notes |
|---|---|---|
| Remove kafka relation | Blocked "application needs Kafka client relation" in ~10s | Re-integrated, recovered to active within ~90s (DPE secret timing) |
| Remove kafka, re-integrate from cold | Blocked → active after ~90s with no manual intervention | `update_status` safety net works, but delay is wall-clock visible |
| Remove ingress relation | Blocked "application needs ingress relation" in ~10s | Re-integrated, recovered fine |
| Remove TLS relation (kui↔ssc) | Stayed active | On k8s, this relation is vestigial — server TLS is handled by Traefik, kafka TLS is from kafka↔ssc |
| Kill workload (`pkill -f api-1.3.0.jar`) | Pebble restarted immediately | Charm stayed active, retry in `health_check` absorbed transient |
| Restart unit (`kubectl delete pod`) | Recovered to active within ~30s | Full unit restart, no data loss, peer relation intact |
| Bad secret ID (`juju config kui system-users="secret:bad"`) | Stayed active, no visible status change | `SecretNotFoundError`→`return {}`, `_on_secret_changed` exits early |
| Valid secret but wrong owner (permission denied) | Stayed active, no visible status change | `ModelError` (permission denied) also caught and swallowed |
| Valid secret with non-admin keys | Stayed active | Extra keys logged at ERROR but admin password unchanged |
| Scale to 2 units | Both active, 611Mi/601Mi mem | Admin password shared via peer relation, identical configs |
| Scale back to 1 | Clean | Unit-1 terminated cleanly, no dangling resources |
| Karapace integration | `schemaRegistry: http://karapace-0.karapace-endpoints:8081` | Correctly populated with auth credentials |
| No-op config change | One config-changed hook, no workload restart | `config_manager.config_changed()` correctly detected no diff |

## Observed behaviour

- **Pebble service**: single service `kafka-ui`, enabled, running as root. Layer command: `java -Dspring.config.additional-location=/etc/kafka-ui/application-local.yml --add-opens java.rmi/javax.rmi.ssl=ALL-UNNAMED -jar /opt/kafka-ui/libs/api-1.3.0.jar`. Environment: `JAVA_OPTS: -Xms1G -Xmx1G -XX:+UseG1GC`.
- **Config file** `/etc/kafka-ui/application-local.yml`: correctly populated with bootstrap servers, SASL credentials, context path, and metrics config. Schema registry populated when Karapace related, broken (`http://`) when not.
- **TLS config on kafka-client**: `security.protocol: SASL_SSL` with truststore JKS and SCRAM-SHA-512. CA cert at `/etc/kafka-ui/kafka-client.pem`, truststore at `/etc/kafka-ui/truststore.jks`. TLS correctly integrates via DPE secrets.
- **Resource usage** (`kubectl top pod`): kui-0 645Mi (idle), kui-1 561Mi (idle). The `-Xms1G -Xmx1G` heap is consistent with ~600MB resident.
- **`/etc/environment`**: Contains `JAVA_OPTS='-Xms1G -Xmx1G -XX:+UseG1GC'` plus craft/rockcraft build env vars. Redundant with the Pebble layer environment on k8s.
- **Traefik proxy**: Returns 302 redirect at `http://10.43.45.0/rv-kui-deep-kui/`. Login flow works.
- **Metrics**: Prometheus on port 9101, successfully fetching kafka metrics (`ClustersStatisticsScheduler: Metrics updated for cluster: kafka`).
- **Kafka-connect integration** (rv-connect): Correctly populated `kafka-connect` config section with `address: http://connect-0.connect-endpoints:8083`, per-relation username and password. When the `connect-client` relation was removed, the config section was cleanly removed — the charm re-rendered config correctly.
- **Password rotation via valid secret**: Created a Juju secret with `admin=NewTestPassword2024!`, granted to kui, and set `system-users` config. The `_on_secret_changed` handler detected the changed `admin` key, wrote the new password to the peer relation, and triggered `config_changed`. The live config file showed the updated password. The charm stayed `active` throughout.
- **Hook count for redundant config change**: One config-changed hook fired. `config_manager.config_changed()` compared on-disk config to generated config and found no diff, so workload was not restarted.
- **Hook count for kafka-connect relation change**: Two hooks: `connect-client-relation-changed` → `config-changed`. The workload was restarted once to pick up the new config. Clean.
- **DPE event timing**: `kafka-client-relation-changed` fires when secret URIs are written to the relation databag, but the actual secret content may not be populated yet. `KafkaRequirerEventHandlers._on_secret_changed_event` at `lib/charms/data_platform_libs/v0/data_interfaces.py:4030` is a no-op (`pass`). The charm relies on the `update_status → config_changed` cycle to eventually pick up the data. Confirmed working: automatic recovery from blocked→active in ~90s without manual intervention.
- **Juju 4.0**: Charm deploys cleanly. Pebble plan shows `override: replace` instead of the charm's `override: merge` — the OCI image has no pre-existing layer for the service. The Pebble environment includes `JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64` and `KAFKA_UI_CONFIG=/etc/kafka-ui/application-local.yml` from image metadata, which the charm does not set.
- **Application startup with empty bootstrap servers**: When kafka is not related, the Spring Boot application fails to start with `Property: kafka.clusters[0].bootstrapServers, Value: "", Reason: field bootstrapServers for cluster could not be blank`. Pebble keeps retrying; the charm correctly sets `blocked` status via `health_check`.
- **Stale-status recovery (verified)**: After scaling up from 0→1 kafka relation, kui stayed blocked for ~90s then recovered to active without manual intervention. Verified in a fresh deployment (rv-stale-status) with `update-status-hook-interval` set to 30s; recovery at first `update_status` hook after DPE secrets propagated. The `pending_inactive_statuses` list pattern was checked for a potential stale-status bug — the charm object is recreated per hook invocation (Juju dispatch model), so `pending_inactive_statuses = []` in `__init__` resets it correctly each hook.

## Findings

Ordered by severity, most serious first.

### `get_current_sans` unbound variable crash path
- **Severity**: high
- **Kind**: bug
- **Where**: `src/managers/tls.py:301-307`
- **Evidence**:
  ```python
  for line in sans_lines:
      if "DNS" in line and "IP" in line:
          break

  sans_ip = []
  sans_dns = []
  for item in line.split(", "):   # line 307: line may be unbound
  ```
  If `sans_lines` contains no line with both "DNS" and "IP" (e.g., openssl output format changes, or the cert has no SANs), the loop exhausts without setting `line`, and `line.split(", ")` raises `UnboundLocalError`.
- **Impact**: `get_current_sans` detects SAN drift in TLS certs. If the cert format changes (upstream JRE update, custom CA), the charm crashes with an unhelpful traceback instead of a clear error.
- **Fix**: Add an `else` clause on the `for` loop to handle the no-match case explicitly:
  ```python
  for line in sans_lines:
      if "DNS" in line and "IP" in line:
          break
  else:
      logger.warning("No SAN line found in certificate")
      return None
  ```
- **Linter rule**: Mechanically checkable — pyright `reportPossiblyUnboundVariable` catches this exactly; the project just doesn't run pyright.

### Zero unit test coverage
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py` (0 bytes)
- **Evidence**: `tox -e unit` collects 0 tests from an empty file, exit code 5. `poetry run coverage` reports "No data was collected."
- **Impact**: Every code path in config generation, TLS truststore management, status precedence, and secret handling has zero automated verification. The `schemaRegistry: http://` bug, the `get_current_sans` crash path, and the secret-loading error-swallowing would all be caught by basic harness tests.
- **Fix**: Write unit tests using `ops.testing.Harness` or `scenario`. Minimum set:
  - `test_application_local_config_no_relations` — verify `schemaRegistry` is absent/None, not `http://`
  - `test_application_local_config_with_karapace` — verify `schemaRegistry` populated correctly
  - `test_application_local_config_with_tls` / `_without_tls` — verify `ssl` block presence/absence
  - `test_status_missing_kafka` / `test_status_no_kafka_credentials` — status transitions
  - `test_load_auth_secret_bad_id` — error handling for invalid secret ID
- **Linter rule**: Mechanically checkable — flag `.py` files in `tests/unit/` that define zero test functions.

### `tox -e static` is a no-op; pyright finds 40 real errors
- **Severity**: high
- **Kind**: lint
- **Where**: `tox.ini` (no `[testenv:static]` section defined)
- **Evidence**: `tox -e static` returns `OK` in ~0.03s — it runs the default `[testenv]`, which only installs poetry with no type-check commands. `poetry run pyright src/` reports 40 errors, 4 warnings, including:
  - `tls.py:307`: `line` possibly unbound (real bug, above)
  - `tls.py:389`: `name` not a known attribute of `None` on `client.relation.name` — false positive, guarded by `tls_ca`, see nit below
  - `workload.py:53`: `write()` parameter type mismatch (`str` vs `str | BinaryIO`)
  - `workload.py:57`: `exec()` parameter count mismatch (missing `sensitive` param from base)
  - 36 import-resolution errors (expected — `ops`, `charmlibs`, `cryptography` not in the dev/lint dependency group)
- **Impact**: `CONTRIBUTING.md` tells developers to run `tox -e static` for "static type checking" but it does nothing. Real type errors are invisible to contributors. The `workload.py` override mismatches could cause a `TypeError` if the abstract `WorkloadBase` methods are ever called with `BinaryIO` content or `sensitive=True`.
- **Fix**: Add a `[testenv:static]` section:
  ```ini
  [testenv:static]
  description = Static type checking
  commands =
      poetry install --with dev
      poetry run pyright src/
  ```
  Configure `pyrightconfig.json` to exclude unresolvable import errors if the dev deps can't be installed in CI.
- **Linter rule**: Mechanically checkable — flag `tox.ini` environments listed in `env_list` with no corresponding `[testenv:X]` section, or environments with no commands.

### `schemaRegistry` writes `http://` when Karapace is not related
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/config.py:155`
- **Evidence**:
  ```python
  "schemaRegistry": f"http://{self.context.karapace_client.endpoints}" or None,
  ```
  When `karapace_client.endpoints` is `""` (no relation), the f-string evaluates to `"http://"`, which is truthy, so `or None` never fires. Observed live in `/etc/kafka-ui/application-local.yml` as `schemaRegistry: http://` in both the basic and deep deployments. When Karapace is related, the field correctly shows `schemaRegistry: http://karapace-0.karapace-endpoints:8081`.
- **Impact**: Kafka UI receives an invalid schema registry URL and will fail to connect to it — config noise that can mask real issues or produce misleading logs/UI errors.
- **Fix**: Use a conditional instead of `or None`:
  ```python
  "schemaRegistry": f"http://{self.context.karapace_client.endpoints}" if self.context.karapace_client.endpoints else None,
  ```
- **Linter rule**: Not mechanically checkable in general, but a linter could flag f-string interpolations combined with `or` as suspicious when the format string is non-empty even with empty interpolations.

### Invalid secret ID / permission denied silently swallowed — no blocked status
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/events/user_secrets.py:69`
- **Evidence**:
  ```python
  except (SecretNotFoundError, ModelError) as e:
      logging.error(f"Failed to fetch the secret, details: {e}")
      return {}
  ```
  Demonstrated live with two failure modes: bad ID (`juju config kui system-users="secret:this-does-not-exist"` → `SecretNotFoundError`, logged but charm stayed `active`) and permission denied (`system-users` pointed at a secret owned by another app → `ModelError`, also swallowed, charm stayed `active`). In both cases `_on_secret_changed` gets `credentials = {}` and exits early without setting a status.
- **Impact**: An operator who misconfigures `system-users` gets no feedback from `juju status` — the charm silently ignores the bad config and continues with the previous/auto-generated password. Confirmed for both failure modes in the live deployment.
- **Fix**: When `system-users` is configured but `load_auth_secret()` returns `{}`, set a blocked status ("configured secret not found or invalid"). Validate the secret ID early during config-changed.
- **Linter rule**: Partially checkable — flag `except` blocks in config-change handlers that swallow errors without setting a status; the `return {}` + early-exit pattern needs flow analysis.

### DPE library event timing: charm stays blocked until `update_status` fires
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/data_platform_libs/v0/data_interfaces.py:4030` (`KafkaRequirerEventHandlers._on_secret_changed_event` is `pass`)
- **Evidence**: Observed in three separate deployments. After `juju integrate kui kafka`, kafka became active and relation data appeared on the kafka side (endpoints, secret-user URI), but kui stayed blocked. In one run, `kafka-client-relation-changed` fired at 12:49:34 while kafka didn't reach active until ~12:50:16 — by the time secret URIs were written, the hook had already processed. A manual config change triggered `config-changed`, which re-read the now-populated secrets and reached active. Automatic recovery (no manual intervention) was also observed, ~90s after re-integration, via the `update_status` hook.
- **Impact**: `KafkaRequirerEventHandlers._on_secret_changed_event` is deliberately `pass` in the DPE library. When Kafka writes secret URIs to the relation databag, `relation-changed` fires, but the actual secret content hasn't propagated yet, so `DataDict.__getitem__` returns empty strings for secret-backed fields. The charm's config-changed handler sees no credentials and stays blocked until the next `update_status → config_changed` cycle (up to the full `update-status-hook-interval`, 5 min default, 90s in test).
- **Fix**: Either (a) add a comment at `src/charm.py:116` explaining that `update_status → config_changed.emit()` is a safety net for DPE secret timing, or (b) have `_on_config_changed` set a waiting status ("waiting for Kafka cluster credentials") rather than blocked while credentials are pending, so operators know the charm isn't broken.
- **Linter rule**: not established.

### Juju 4.0: charm deploys and initializes correctly; Kafka integration not testable
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py` is 4.0-compatible; blocked by upstream kafka-k8s
- **Evidence**: Deployed kafka-ui-k8s standalone on Juju 4.0 (concierge-k8s-4). Charm initialized correctly: `blocked` status "application needs Kafka client relation", Pebble service `kafka-ui` running, config file `/etc/kafka-ui/application-local.yml` written with admin password and correct context-path `/rv-juju4-kui`. No tracebacks or framework errors. The kafka-k8s charm fails on Juju 4.0 with `OSError: [Errno 19] No such device` in `update_peer_ip_address`, so the full stack could not be tested.
- **Impact**: No blocker on the kafka-ui-k8s side — the charm's own code uses modern ops patterns (`collect-status`, `TypedCharmBase`) compatible with 4.0. The blocker is entirely the kafka-k8s dependency.
- **Fix**: No charm code changes needed here; tracked as an upstream kafka-k8s fix.
- **Linter rule**: not established.

### Dead code: snap-related constants on a k8s-only charm
- **Severity**: low
- **Kind**: lint
- **Where**: `src/literals.py:15-16,48-49`; `src/workload.py:27`
- **Evidence**: `SNAP_NAME="charmed-kafka-ui"`, `SNAP_REVISION="3"`, `Status.SNAP_NOT_INSTALLED`, and `Status.INSTALLING` (message "installing charmed-kafka-ui") are defined but `SNAP_NOT_INSTALLED` is never set on any code path. `SUBSTRATE` is hardcoded to `"k8s"` at `src/literals.py:23`. `SNAP_NAME` in `src/workload.py:27` is only used for the `keytool` path on VM substrate (`src/managers/tls.py:38-39`).
- **Impact**: Confuses maintainers. The status message "installing charmed-kafka-ui" was observed in `juju status` during pod startup before pebble-ready fired — it looks like a snap operation on a k8s charm.
- **Fix**: Gate snap-specific constants behind `SUBSTRATE == "vm"`, or remove them. Rename the `INSTALLING` message to something like "waiting for Pebble".
- **Linter rule**: Mechanically checkable — flag top-level constants used only in unreachable branches (via `SUBSTRATE` static analysis).

### Redundant `/etc/environment` write on k8s
- **Severity**: low
- **Kind**: performance
- **Where**: `src/workload.py:130-136` (`set_environment`)
- **Evidence**: `set_environment()` writes `JAVA_OPTS` to `/etc/environment`, which is already set in the Pebble layer (`src/workload.py:120-125`). On k8s, `/etc/environment` is not sourced by the Pebble process; it only affects interactive shells.
- **Impact**: Marginal — one extra file write and read per config-changed cycle that detects a change.
- **Fix**: Gate `set_environment()` behind `SUBSTRATE == "vm"` or remove it on k8s.
- **Linter rule**: not established.

### `update_status` emits `config_changed` without explanation
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:116`
- **Evidence**:
  ```python
  def _on_update_status(self, _) -> None:
      logger.debug("Update status, emitting config-changed")
      self.on.config_changed.emit()
  ```
- **Impact**: This is a necessary safety net for DPE secret timing (see finding above), but there's no comment explaining it. Without context it reads as wasteful polling.
- **Fix**: Add a comment explaining that this re-emit exists to eventually pick up DPE-secret-backed relation data that arrives after the initial `relation-changed` event.
- **Linter rule**: Mechanically checkable — flag `update_status` handlers that call `config_changed.emit()` without an accompanying comment mentioning "DPE" or "secret".

### `Workload.write()` and `Workload.exec()` override signatures don't match the base class
- **Severity**: low
- **Kind**: bug
- **Where**: `src/workload.py:53,57` vs `src/core/workload.py:73-84,95-104`
- **Evidence**: pyright `reportIncompatibleMethodOverride`: `write(self, content: str, ...)` narrows the base's `content: str | BinaryIO`; `exec(self, command, env, working_dir)` is missing the base's `sensitive: bool = False` parameter.
- **Impact**: If any code path calls the abstract `WorkloadBase.write()` with a `BinaryIO` object, or `.exec()` with `sensitive=True`, it will get a `TypeError`. Not currently triggered because all callers go through the concrete `Workload` type, but the abstraction is leaky.
- **Fix**: Match the base signatures exactly, or accept `**kwargs` and pass through.
- **Linter rule**: Mechanically checkable — pyright `reportIncompatibleMethodOverride`.

### No Juju actions
- **Severity**: low
- **Kind**: ux
- **Where**: no `actions.yaml` exists
- **Evidence**: The charm defines zero actions. The README instructs operators to SSH into the container for the password: `juju ssh --container kafka-ui kafka-ui-k8s/0 'cat /etc/kafka-ui/application-local.yml'`.
- **Impact**: Password retrieval and rotation are awkward — operators must `kubectl exec`/`juju ssh` or use the `system-users` secret flow.
- **Fix**: Add `get-admin-password` and `set-admin-password` actions.
- **Linter rule**: not established.

### `restart` peer relation (rolling_op) declared but never used
- **Severity**: low
- **Kind**: lint
- **Where**: `metadata.yaml:46-48` (declares `restart` peer with `rolling_op` interface)
- **Evidence**: `grep -rn 'restart\|rolling_op' src/` returns only `self.workload.restart()` and the `def restart()` method — no references to the `restart` relation itself. Likely a template remnant from dual-substrate charms like kafka-k8s.
- **Impact**: Every unit participates in an unused peer relation, adding relation scaffolding (data-bag writes, hooks) on every Juju operation for no benefit.
- **Fix**: Remove the `restart` peer relation from `metadata.yaml`, or add a comment explaining it as a placeholder for future rolling-restart support.
- **Linter rule**: Mechanically checkable — flag relation names in `metadata.yaml` with zero references in `src/`.

### Config comparison is string-based and fragile
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/config.py:202`
- **Evidence**:
  ```python
  @property
  def clean_yaml_config(self) -> str:
      raw_yaml_string = yaml.dump(self.application_local_config, default_flow_style=False)
      return "\n".join([line for line in raw_yaml_string.splitlines() if line[-4:] != "null"])
  ```
  Stripping trailing `null` values by checking the last 4 characters is fragile: it would strip any value whose last 4 characters happen to be `null`, and if the YAML library's null representation ever changes (e.g. `~`), trailing nulls would leak into the written config, causing `config_changed()` to permanently detect a diff.
- **Impact**: If the YAML library's null representation changes (e.g. on a `ruamel.yaml` upgrade), the config comparison would always report a diff, causing the JVM to restart on every `update_status` hook (every 90s in test, every 5min in prod) — a workload-stability risk.
- **Fix**: Recursively strip dict keys with `None` values before serialization, or use a custom YAML representer for `None`, instead of string-matching the dumped output.
- **Linter rule**: not established.

### `generate_self_signed_certificate` return value not None-checked in `init_unit_tls`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/events/tls.py:97-104`
- **Evidence**:
  ```python
  self_signed = self.charm.tls_manager.generate_self_signed_certificate()
  self.charm.context.unit.update(
      {
          TLSContext.PRIVATE_KEY: self_signed.private_key,  # line 100
          TLSContext.CERT: self_signed.certificate,
          TLSContext.CSR: self_signed.csr,
          TLSContext.CA: self_signed.ca,
      }
  )
  ```
  `generate_self_signed_certificate()` (`src/managers/tls.py:79`) is typed `SelfSignedCertificate | None`. If it ever returns `None`, the attribute accesses would raise `AttributeError`. In practice `generate_internal_ca()` always returns a valid `GeneratedCa`, so on k8s this path is unreachable, but the code exists behind a substrate check and would be live on a VM variant.
- **Impact**: On VM substrate (currently unsupported but the code path exists), this would crash with an unhelpful traceback rather than a logged error. On k8s it's unreachable dead code.
- **Fix**: Either drop the `| None` from the return type (if `generate_internal_ca` truly never returns `None`), or guard with an explicit `if not self_signed: logger.error(...); return`.
- **Linter rule**: Mechanically checkable — pyright `reportOptionalMemberAccess`.

### `check_socket` method defined but never called
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/core/workload.py:106-108` and `src/workload.py:95-97`
- **Evidence**: Implemented in both the abstract base and the concrete `Workload`, but `grep -rn check_socket src/` finds no callers.
- **Fix**: Remove it, or use it in `health_check` as a pre-flight check before the HTTP request.
- **Impact**: Dead code, no operational impact.
- **Linter rule**: Mechanically checkable — flag methods with no callers in reachable code (vulture or similar).

### pyright false positive: `tls.py:389` is safe in practice
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/managers/tls.py:389`
- **Evidence**: pyright reports `"name" is not a known attribute of "None"` for `client.relation.name` in `update_truststore`. The access is guarded by `if client.tls_ca:`, and `tls_ca` returns `""` (falsy) when `self.relation` is `None` (`models.py:83-86`), so the path is unreachable when `relation` is `None`. Pyright cannot track this cross-property invariant.
- **Impact**: A reviewer could waste time chasing a non-bug; noisy but harmless.
- **Fix**: Add a `# pyright: ignore[reportOptionalMemberAccess]` comment, or restructure with an explicit `client.relation is not None` check.
- **Linter rule**: Already caught by pyright; this is a documented false positive, not a bug.

### `WithTlsCa` declared abstract with no abstract methods
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/core/models.py:77`
- **Evidence**: `class WithTlsCa(ABC)` has no abstract methods or properties. Caught by ruff B024.
- **Impact**: Misleading — implies an interface contract that doesn't exist. Used as a mixin for `KafkaClientContext`, `ConnectClientContext`, `KarapaceClientContext`.
- **Fix**: Remove the `ABC` base, or add an `@abstractmethod` if a contract is intended.
- **Linter rule**: Mechanically checkable — ruff B024 (`abstract-base-class-without-abstract-method`).

### Private member `_fetch_relation_data_with_secrets` accessed from charm code
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/core/models.py:128`
- **Evidence**: `self.data_interface._fetch_relation_data_with_secrets(remote_unit, [field], self.relation)` accesses a private DPE library method. Caught by ruff SLF001.
- **Impact**: The private method signature could change without notice in a DPE library update.
- **Fix**: Request a public API from the DPE library, or suppress with `# noqa: SLF001` acknowledging the intentional use.
- **Linter rule**: Mechanically checkable — ruff SLF001 (`private-member-access`).

### `_on_secret_changed` handler type annotation doesn't match observed events
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/events/user_secrets.py:37`
- **Evidence**: Declared as `def _on_secret_changed(self, event: SecretChangedEvent)` but observed from both `config_changed` (`ConfigChangedEvent`) and `secret_changed` (`SecretChangedEvent`). In practice the handler doesn't access `SecretChangedEvent`-specific attributes, so it works.
- **Impact**: Misleading annotation for future maintainers.
- **Fix**: Use `EventBase` (or `object`) as the annotation, or split into two handlers.
- **Linter rule**: not established (requires resolving `ops` imports for pyright to flag).

### `SERVICE_STARTING` status defined but never used
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/literals.py:56`
- **Evidence**: `SERVICE_STARTING = StatusLevel(WaitingStatus("service is still starting up"), "INFO")` defined but `grep -rn SERVICE_STARTING src/` returns only the definition. `health_check` uses `Status.SERVICE_NOT_RUNNING` (a `BlockedStatus`) instead, even during the brief window when Pebble is starting the JVM.
- **Impact**: Dead code; a `WaitingStatus` would be more accurate than `BlockedStatus` during startup.
- **Fix**: Either use it in `health_check` (e.g. when Pebble reports the service starting but not yet active) or remove it.
- **Linter rule**: Mechanically checkable — flag enum members never referenced outside their definition.

### Terraform module `endpoints` output is an empty placeholder
- **Severity**: nit
- **Kind**: docs
- **Where**: `terraform/outputs.tf:5-8`
- **Evidence**:
  ```hcl
  output "endpoints" {
    value = {
      # Add actual service URLs here if available
    }
  }
  ```
- **Impact**: CC006 mandates the `endpoints` output; operators consuming the module get an empty map.
- **Fix**: Populate with the Traefik-proxied URL pattern, or document how to retrieve it (`juju run traefik-k8s/leader show-proxied-endpoints`).
- **Linter rule**: Mechanically checkable — flag empty `endpoints` outputs in terraform modules.

## Worth copying

- **Clean `Context` model** (`src/core/models.py`): the `Context` class with property accessors for each relation client is well-structured; each client context (`KafkaClientContext`, `ConnectClientContext`, `KarapaceClientContext`) encapsulates its own data access and status logic. The `WithStatus` mixin (`ready` == `status == Status.ACTIVE`) is clean and reusable.
- **Status precedence in `_on_collect_status`** (`src/charm.py:117-121`): uses `CollectStatusEvent.add_status` with a priority-ordered list instead of manual if/elif cascades — the canonical `collect-status` pattern.
- **`ConfigManager.config_changed()`** (`src/managers/config.py:180-182`): reads the on-disk config and compares it to the generated config, avoiding unnecessary workload restarts — confirmed in deployment that a no-op config change does not restart the JVM.
- **`TypedCharmBase` with structured config** (`src/charm.py:47`): uses `TypedCharmBase[CharmConfig]` for typed access to `self.config`; `CharmConfig` in `structured_config.py` is minimal and correct.
- **Integration tests** (`tests/integration/test_charm.py`): full deployment of the ecosystem (kafka, karapace, connect, TLS, Traefik) with real HTTP assertions — login flow, cluster API response, password rotation — using `jubilant` with proper `successes=N` stability checks and a parametrized `--tls` flag.
- **Terraform module** (`terraform/`): a proper TF module following CC006 conventions, with required provider pins (juju >= 1.0.0).

## Common-practice notes

- **Follows**: canonical DPE library stack (`data_interfaces`, `data_models`), Pebble-based k8s patterns, `collect-status`, and the `poetry` plugin in `charmcraft.yaml`. The `src/` layout with `core/`, `events/`, `managers/` mirrors kafka-k8s-operator and similar DPE charms.
- **Follows**: `charmcraft.yaml` uses the modern `poetry-deps` + `charm-poetry` parts pattern for reproducible builds.
- **Follows**: the `system_users` config + Juju secrets password-rotation pattern is the canonical DPE password-management approach, and is well-documented inline.
- **Drifts**: the `workload.py`/`core/workload.py` split (abstract base + concrete) is a carryover from VM/K8s dual-substrate templates. Since `SUBSTRATE` is hardcoded to `"k8s"` with no VM variant, the abstraction adds maintenance overhead without benefit.
- **Drifts**: the `restart` rolling_op peer relation is unused by the charm code — inert metadata, likely a template remnant.
- **Drifts**: `pyright` is declared as a dependency in `pyproject.toml` (`fmt`/`lint` groups) but never wired into `tox.ini`'s `static` environment, and there is no `[tool.pyright]` config, so 36 of 40 reported errors are import-resolution noise.
- **Drifts**: `pydantic = "<2"` in `pyproject.toml` — most newer DPE charms have moved to pydantic v2.

## Tests

### Unit tests
- `tests/unit/test_charm.py` is 0 bytes. `tox -e unit` reports 0 tests collected, exit code 5. No coverage data.
- Notable untested branches: `ConfigManager.kafka_cluster_config` (`schemaRegistry` bug path), `ConfigManager.cluster_tls_properties`, `ConfigManager.spring_boot_tls_config`, `SecretsHandler._on_secret_changed` (valid/invalid/no-op), `TLSHandler._on_certificate_available`, `TLSManager.truststore_changed()`, `TLSManager.get_current_sans()` (crash path), `KafkaClientContext.status` transitions, `health_check` retry logic.

### Integration tests
- `tests/integration/test_charm.py` — 4 test functions: `test_build_and_deploy`, `test_integrate`, `test_ui`, `test_password_rotation`. Deploys full ecosystem with `jubilant`, asserts blocked→active transitions, login via Traefik, cluster API, password rotation. Parametrized for TLS.
- `conftest.py` handles local charm build, TLS parametrization, ephemeral model lifecycle. `helpers.py` handles secret retrieval, password rotation, address utilities.
- Note: `tests/integration/test_charm.py:2` and `helpers.py:2` carry "Copyright 2025 marc" rather than "Copyright 2025 Canonical Ltd." used elsewhere — likely a copy-paste from a personal dev setup.

### Lint
- `tox -e lint`: PASS (codespell clean, ruff check, ruff format check).
- `tox -e format`: available and functional.
- `tox -e static`: listed in `env_list` but has no `[testenv:static]` section — runs as a no-op (confirmed 0.03s, just installs poetry).
- `poetry run pyright src/`: 40 errors, 4 warnings. 36 are import-resolution failures (expected, deps not installed in lint set). 4 are real/notable: `tls.py:307` unbound variable (bug), `tls.py:389` optional member access (false positive), `workload.py:53` incompatible `write()` override, `workload.py:57` incompatible `exec()` override.
- Broad ruff scan (`--select ALL` minus noisy categories): 5 additional findings — B024 (`WithTlsCa` abstract without abstract methods), SLF001 (private `_fetch_relation_data_with_secrets` access), 2× B009 (`getattr` with constant values, DPE pattern, not a real bug), B904 (bare `raise` pattern in `tls.py:180`). None are operational bugs.

### CI
- GitHub Actions: `lint`, `build`, `integration-test` matrix (with/without TLS). Self-hosted runners, `concierge` for env setup, daily cron at 00:53 UTC. Juju 3.6/stable per `concierge.yaml`.
- `build_charm.yaml` uses `charmcraft-snap-channel: latest/candidate` (TODO note to switch after charmcraft 3.3 stable).

## Docs

- **README**: good overview with deployment instructions, relation list, and a worked example from MicroK8s through to browser access. Password retrieval via `juju ssh --container kafka-ui kafka-ui-k8s/0 'cat /etc/kafka-ui/application-local.yml'` works but is awkward — an action would be better. Includes a "We are Hiring!" callout (standard practice).
- **Charmhub description**: published on all channels at rev 8; accurate summary, matches observed behaviour.
- **CONTRIBUTING.md**: standard tox-based dev setup, but references `tox -e static` as "static type checking" when it is a no-op (see findings). `tox devenv -e integration` instructions are correct.
- **Terraform**: complete module with variables, outputs, provider pins; the `endpoints` output is an empty placeholder (see findings).

## Open questions

- Is the `update_status → config_changed.emit()` safety net intentional and permanent, or should the charm move to a `WaitingStatus` while DPE secrets are propagating? Confirmed necessary across four deployments; still undocumented in code.
- Is the `restart` peer relation a placeholder for future rolling-restart support, or dead metadata to be removed? No handler references it.
- Should the integration-test copyright headers ("Copyright 2025 marc") be normalized to "Copyright 2025 Canonical Ltd."?
- Is the Juju 4.0 `override: replace` vs `override: merge` divergence in the Pebble plan intentional, or would it break if the rockcraft image later ships a default layer for the service? *(unverified — not confirmed against rockcraft image internals)*
