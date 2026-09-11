# hook-service

A well-structured k8s charm for the Identity Platform's Hook Service, providing a REST API for group/authz management and a Hydra token hook endpoint. Code quality is high: clean separation of concerns, strong typing, consistent use of dataclasses, and a centralised reconciler pattern (`_holistic_handler`) that is easy to follow. The unit test suite (91 tests, 89% coverage on `charm.py`) passes cleanly with zero lint issues. However, a critical bug in `NOOP_CONDITIONS` blocks all reconciliation when OpenFGA is absent, even with authorization disabled — this silently drops config changes, TLS refresh, and Pebble layer updates while status still reports Active. Fix that first; the rest of the findings are hardening opportunities around config validation, error handling, and test coverage.

| | |
|---|---|
| Repo | canonical/hook-service-operator @ `55f68b0` (2026-07-08) |
| Charms | hook-service |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), channel latest/edge rev 16, integrated with postgresql-k8s, openfga-k8s, self-signed-certificates, traefik-k8s, grafana-agent-k8s. Also deployed standalone on concierge-k8s-4 (Juju 4.0.5), where the postgresql-k8s dependency could not be deployed (no Juju 4-compatible revision), limiting that test to blocked-status and Pebble-plan checks. |
| Reviewed | 2026-08-04 |

## What it does

The charm manages a Go workload (`hook-service serve`) that exposes a REST API on port 8080. It integrates with PostgreSQL (required), OpenFGA (optional, for authorization), Hydra (OAuth + token hook), Traefik (internal ingress), certificate transfer (TLS CA bundles), observability (COS), tenant service info, and logging/tracing. It provides 12 Juju actions for day-2 group and user management. Every hook event feeds into `_holistic_handler`, which runs a sequence of `_ensure_*` steps before planning the Pebble layer.

## Deployment log

### Juju 4.0.5 (concierge-k8s-4)
```sh
juju add-model rv-hook-service k8s --controller concierge-k8s-4
juju deploy hook-service --channel edge --trust
# → blocked "Missing integration pg-database" (correct)
# Deploying postgresql-k8s fails — no Juju 4-compatible revision available.
juju destroy-model rv-hook-service --force --no-wait --destroy-storage
```

### Juju 3.6.25 (concierge-k8s-3) — main deployment with all integrations
```sh
juju add-model rv-hook-deep k8s --controller concierge-k8s-3
juju deploy hook-service --channel edge --trust
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy openfga-k8s --channel latest/stable --trust
juju deploy self-signed-certificates --channel edge
juju deploy traefik-k8s --channel latest/stable --trust
juju deploy grafana-agent-k8s --channel 1/stable --trust
juju integrate hook-service:pg-database postgresql-k8s:database
juju integrate openfga-k8s:database postgresql-k8s:database
juju integrate hook-service:openfga openfga-k8s:openfga
juju integrate hook-service:receive-ca-cert self-signed-certificates:send-ca-cert
juju integrate hook-service:internal-route traefik-k8s
juju integrate hook-service:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate hook-service:logging grafana-agent-k8s:logging-provider
# grafana-dashboard integration failed — no matching relation on grafana-agent-k8s 1/stable
# → all active/idle (~2 min from deploy; status transitioned through "Waiting for secrets
#   creation" → "Waiting for openfga store to be created" → active)
```
- Pebble plan confirmed: all env vars populated (DSN, API_TOKEN, OPENFGA_*), log forwarding to grafana-agent-k8s configured.
- 12 actions tested: `list-groups`, `create-group`, `delete-group` worked. `get-access-token` correctly failed (no OAuth). `groups-add-users`, `groups-remove-users`, `groups-list-users` correctly failed on a non-existent group. `users-delete`, `users-list-groups` worked. `users-set-groups` failed on a non-existent user. `import-groups` failed with a JSON parsing error.
- Actions use comma-separated strings (not JSON arrays) for multi-value params like `users` and `groups` — this differs from the action description shown by `juju actions`.

### Failure injection 1: `NOOP_CONDITIONS` bug (`authorization_enabled=false` without OpenFGA)
```sh
juju config hook-service authorization_enabled=false
juju remove-relation hook-service:openfga openfga-k8s:openfga
# Status shows Active (correct — status collector gates on authorization_enabled)
juju config hook-service log_level=warning
# → Pebble plan STILL shows DEBUG — config change NOT propagated!
```
Confirmed: `openfga_integration_exists` returns False, blocking the entire reconciler. Recovery tested: re-adding OpenFGA and re-enabling authorization restored reconciliation, and `LOG_LEVEL=WARNING` was then applied. Reproduced on both Juju 3.6 and Juju 4.0.

### Failure injection 2: Bad config values
```sh
juju config hook-service log_level=INVALID
# → Accepted silently. Pebble plan shows LOG_LEVEL: INVALID. No validation.

juju config hook-service cpu=INVALID
# → Accepted, then blocked "Failed obtaining resource limit spec: Invalid limits spec:
#   {'cpu': 'INVALID', 'memory': None}"
# → Validated only at K8s API level, not by the charm.
juju config hook-service --reset cpu   # → recovered to active
```

### Failure injection 3: Service kill
```sh
kubectl exec -c hook-service -- /charm/bin/pebble stop hook-service
# → Status stayed "active" until the pebble check reached its failure threshold
# → Status then updated to BlockedStatus "Failed to start the service…" via _on_collect_status
# → _on_pebble_check_failed only logs; does not trigger reconciliation
# → Manual pebble start + config-changed → recovered to active
```

### Scale test
```sh
juju scale-application hook-service 2   # second unit active, same env vars via peer data
juju scale-application hook-service 1   # transient "Missing integration openfga" on the
                                         # departing unit, then resolved
```

### Remove application
```sh
juju remove-application hook-service
# → Teardown showed "Waiting for database migration" — unnecessary during removal
# → Removed successfully after ~30s
```

### Juju 4.0.5 standalone test
```sh
juju add-model rv-hook-j4 k8s --controller concierge-k8s-4
juju deploy hook-service --channel edge --trust --config authorization_enabled=false
# → blocked "Missing integration pg-database" (correct)
# Pebble plan shows only the image's default layer (startup: enabled, no env vars, no checks)
# → NOOP_CONDITIONS blocks all reconciliation on Juju 4 as well
```

## Observed behaviour

| Observation | Value |
|---|---|
| Deploy to active/idle (all integrations) | ~2 min |
| Charm size (Charmhub rev 16) | ~1.6 MB compressed |
| Workload memory (steady state) | 63 MiB |
| Workload CPU (steady state) | 140m |
| Hook count per config-changed | 1 config-changed + collect-status |
| Pebble startup mode | `disabled` (charm explicitly starts) |
| Pebble restart on config change | Yes — `_restart_service` calls `replan` or `start` |
| Status on database removal | Blocked "Missing integration pg-database" |
| Status on OpenFGA removal (authz enabled) | Blocked "Missing integration openfga" |
| Status on OpenFGA removal (authz disabled) | Active (correct message; `NOOP_CONDITIONS` still blocks reconciliation) |
| Config changes propagate with all integrations | Yes |
| Config changes with authz disabled, no OpenFGA | **No** (Finding 1) |
| Invalid `log_level` | Accepted silently, passed to workload |
| Invalid `cpu`/`memory` | Rejected at K8s API level, blocked status set |
| Service manually stopped | Not detected immediately; `_on_collect_status` sets BlockedStatus after the check threshold; restored on next hook |
| 2-unit scale | Peer data sharing works; env vars identical on both units |
| Teardown | Shows "Waiting for database migration" briefly before removal |
| Juju 4 behaviour | Same `NOOP_CONDITIONS` block; Pebble shows default image layer |

## Findings

### 1. `NOOP_CONDITIONS` unconditionally requires OpenFGA, breaking reconciliation when authorization is disabled
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/utils.py:121-127`
- **Evidence**:
  ```python
  NOOP_CONDITIONS: tuple[Condition, ...] = (
      container_connectivity,
      database_integration_exists,
      database_resource_is_created,
      openfga_integration_exists,     # <— unconditional
      authentication_config_is_valid,
  )
  ```
  `openfga_integration_exists` does not check `authorization_enabled`. When `authorization_enabled=false` and no OpenFGA integration exists, `_holistic_handler` returns immediately and does no reconciliation — the Pebble layer is never updated, TLS certificates are never refreshed, and config changes are silently dropped. `_on_collect_status` correctly shows Active because it checks `authorization_enabled` before reporting the missing integration, masking the underlying stall.
- **Impact**: Any config change, cert rotation, or workload update is silently dropped whenever authorization is disabled and OpenFGA is not integrated — a supported, documented configuration. Operators have no signal that reconciliation has stopped.
- **Fix**: Gate `openfga_integration_exists` on `authorization_enabled`:
  ```python
  def openfga_integration_exists(charm):
      if not charm._config.authorization_enabled:
          return True
      return bool(charm.model.relations[OPENFGA_INTEGRATION_NAME])
  ```
- **Linter rule**: "NOOP condition references `openfga_integration_exists` without gating on `authorization_enabled`" — mechanically checkable.

### 2. `authentication_config_is_valid` in `NOOP_CONDITIONS` blocks all reconciliation on bad auth config
- **Severity**: high
- **Kind**: bug
- **Where**: `src/utils.py:121-127`
- **Evidence**: Same tuple as Finding 1. If auth config is invalid (e.g. `authn_jwks_url` set without `authn_issuer`), the reconciler stops entirely — database migration, TLS cert refresh, ingress config, and Pebble layer updates are all skipped, not just the auth-related pieces.
- **Impact**: `_on_collect_status` correctly reports BlockedStatus, but the workload is left completely unconfigured rather than just missing authentication, so an otherwise-working deployment loses all reconciliation over one bad config field.
- **Fix**: Remove `authentication_config_is_valid` from `NOOP_CONDITIONS`. Let `_on_collect_status` report BlockedStatus but still configure the workload — it can run even if auth is misconfigured; it just won't authenticate requests.
- **Linter rule**: "NOOP condition that is not a hard prerequisite for workload configuration" — requires semantic analysis, not mechanically checkable.

### 3. `log_level` config accepts any string without validation
- **Severity**: high
- **Kind**: bug
- **Where**: `src/configs.py:49-59`, `charmcraft.yaml` (`log_level` option)
- **Evidence**:
  ```python
  def to_env_vars(self) -> EnvVars:
      env = {
          "LOG_LEVEL": self._config["log_level"].upper(),
          ...
      }
  ```
  `charmcraft.yaml` describes acceptable values only in prose ("info", "debug", "warning", "error", "critical") with no enforced validation.
- **Observed**: `juju config hook-service log_level=INVALID` was accepted silently. The Pebble plan showed `LOG_LEVEL: INVALID`. The charm remained Active with no warning.
- **Fix**: Validate in `CharmConfig.to_env_vars()` or the config-changed handler; reject values outside the documented set and set BlockedStatus.
- **Linter rule**: "Charm config option with prose-only validation" — mechanically checkable (description-only constraint without type enforcement or code validation).

### 4. `_on_pebble_check_failed` logs but does not trigger reconciliation or restart
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:473-475`
- **Evidence**:
  ```python
  def _on_pebble_check_failed(self, event: ops.PebbleCheckFailedEvent) -> None:
      if event.info.name == PEBBLE_READY_CHECK_NAME:
          logger.warning("The service is not running")
  ```
  No status change, no reconciliation trigger. `_on_collect_status` does detect the failure via `is_failing()` and sets BlockedStatus, so the operator is informed — but the charm never attempts to restart the service; it only recovers on the next hook event, when the reconciler calls `_restart_service()`.
- **Observed**: Stopping the service via `pebble stop` left Active status until the check threshold was reached, then BlockedStatus appeared. The service stayed down until a subsequent config-changed hook restarted it.
- **Fix**: Call `self._holistic_handler(event)` from `_on_pebble_check_failed`, or at minimum attempt a replan/restart directly.
- **Linter rule**: "pebble check failed handler does not trigger reconciliation or service restart" — mechanically checkable.

### 5. `_get_migration_status` can crash `_on_collect_status` if the container is not connectable
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:504-509`, `src/utils.py:69-72`
- **Evidence**: `_get_migration_status` calls `migration_is_ready(self)`, which calls `charm.migration_needed`, which calls `self._cli.migration_check(dsn=...)` — requiring container connectivity. `migration_is_ready` only catches `MigrationCheckError`, not `ops.pebble.Error` (which wraps connection failures). If the container is unreachable when `_on_collect_status` fires, the exception propagates uncaught and crashes the status handler.
- **Fix**: Broaden the exception catch in `_get_migration_status`, or add a `can_connect()` guard before calling it.
- **Linter rule**: "container exec called in collect-status without `can_connect` guard" — mechanically checkable.

### 6. Upgrade integration test skipped and outdated
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_upgrade.py`
- **Evidence**: The entire file is `@pytest.mark.skip`. It references old relation names (`f"{APP_NAME}:ingress"` instead of `internal-route`) and the old health endpoint (`/health` instead of `/api/v0/status`). No upgrade path is tested.
- **Fix**: Un-skip, update relation names and endpoints, add the OpenFGA integration, and run as part of CI.
- **Linter rule**: not established (not mechanically checkable).

### 7. Integration tests do not cover actions, config changes, or the `authorization_enabled=false` path
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py`
- **Evidence**: Integration tests deploy with traefik + postgresql + openfga, check `/api/v0/status` and `/api/v0/authz/groups`, test scaling, and test removing integrations. They do not exercise any of the 12 actions, OAuth integration, TLS certificate transfer, config changes, the `authorization_enabled=false` path, tenant-service-info, or the hydra-token-hook integration. A test of the `authorization_enabled=false` + no-OpenFGA scenario would have caught Finding 1.
- **Linter rule**: not established (not mechanically checkable).

### 8. Config `cpu`/`memory` validation deferred to the K8s API rather than validated in-charm
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:792-794`
- **Evidence**:
  ```python
  def _resource_reqs_from_config(self) -> ResourceRequirements:
      limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
      requests = {"cpu": "100m", "memory": "200Mi"}
      return adjust_resource_requirements(limits, requests, adhere_to_requests=True)
  ```
  Invalid values like `cpu=INVALID` are passed straight to `KubernetesComputeResourcesPatch`, which fails at the K8s API level; the charm sets BlockedStatus via `_on_resource_patch_failed`. Recovery requires `juju config --reset cpu`. Early validation would give a faster, clearer error.
- **Observed**: `juju config hook-service cpu=INVALID` → blocked "Failed obtaining resource limit spec: Invalid limits spec: {'cpu': 'INVALID', 'memory': None}". `juju config --reset cpu` → recovered.
- **Fix**: Validate cpu/memory format in `CharmConfig.to_env_vars()` or a dedicated validation method.
- **Linter rule**: not established (requires semantic understanding of K8s resource format).

### 9. `_ensure_tls` calls `subprocess.run` and container operations without error handling
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:397-414`
- **Evidence**:
  ```python
  def _ensure_tls(self) -> bool:
      ...
      subprocess.run(["update-ca-certificates", "--fresh", ...])
      self._workload_service.update_ca_certs()  # calls container.pull/push
      return True
  ```
  `subprocess.run` is called without `check=True`, so a non-zero exit is silently ignored. `update_ca_certs()` calls `container.pull()`/`push()`, which can raise on connection failure. The function always returns `True` regardless. In practice the container is connectable at this point (prior `_ensure_*` steps require it), but there is no guard.
- **Fix**: Use `subprocess.run(..., check=True)` and wrap in try/except, returning `False` on failure.
- **Linter rule**: "`subprocess.run` without `check=True`" — mechanically checkable.

### 10. `_ensure_internal_ingress` and `_ensure_hydra_relation` always return `True`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:336-353`
- **Evidence**: Both functions unconditionally return `True`, even when internal operations fail silently. A comment in `_ensure_internal_ingress` acknowledges this: `# This always returns true if the unit is not the leader, can't we simplify this function?`
- **Fix**: Either rename to signal they are fire-and-forget, or return success/failure meaningfully.
- **Linter rule**: "`_ensure_*` method always returns `True`" — mechanically checkable.

### 11. `is_failing()` uses `c.failures > 0`, which never resets between checks
- **Severity**: low
- **Kind**: bug
- **Where**: `src/services.py:92-100`
- **Evidence**:
  ```python
  def is_failing(self) -> bool:
      if not self.get_service():
          return False
      if not (c := self._container.get_checks().get(PEBBLE_READY_CHECK_NAME)):
          return False
      return c.failures > 0
  ```
  The pebble check failure count only increments; it resets only on a new check invocation. If the service crashes and is manually restarted without a hook firing, `is_failing()` still returns `True` until the next hook triggers a fresh check status — meaning BlockedStatus can persist after recovery.
- **Fix**: Also check `c.status == CheckStatus.DOWN` in addition to `failures`.
- **Linter rule**: not established (not mechanically checkable).

### 12. `Secrets.values()` short-circuits on the first missing secret, returning an empty view
- **Severity**: low
- **Kind**: bug
- **Where**: `src/secret.py:45-49`
- **Evidence**:
  ```python
  def values(self) -> ValuesView:
      secret_contents = {}
      for key, label in zip(self.KEYS, self.LABELS):
          try:
              secret = self._model.get_secret(label=label)
          except SecretNotFoundError:
              return ValuesView({})     # <— abandons all previously gathered secrets
          else:
              secret_contents[key] = secret.get_content()
      return secret_contents.values()
  ```
  Currently benign because only one secret exists (API_TOKEN). If additional secrets are added, a missing optional secret would make `values()` return empty, causing `is_ready()` to return `False` even when the API token secret is available.
- **Fix**: Return a `ValuesView` of whatever was collected, or continue to the next label on `SecretNotFoundError`.
- **Linter rule**: not established (not mechanically checkable).

### 13. `Secrets.api_token` crashes with `TypeError` if the secret is not ready
- **Severity**: low
- **Kind**: bug
- **Where**: `src/secret.py:66-69`
- **Evidence**:
  ```python
  @property
  def api_token(self) -> str:
      return self[API_TOKEN_SECRET_LABEL][API_TOKEN_SECRET_KEY]
  ```
  `self[API_TOKEN_SECRET_LABEL]` returns `None` when no secret exists, so `None[API_TOKEN_SECRET_KEY]` raises `TypeError`. This is only reachable if `api_token` is accessed before `_ensure_secrets` returns `True`, and the current call chain makes that unreachable — but it is a latent crash path.
- **Fix**: Raise a domain-specific exception, or return a sentinel value.
- **Linter rule**: "subscript on Optional return value" — mechanically checkable with a type checker.

### 14. Hardcoded `redirect_uri` placeholder in OAuth client config
- **Severity**: low
- **Kind**: bug
- **Where**: `src/integrations.py:353`
- **Evidence**:
  ```python
  client = ClientConfig(
      redirect_uri="https://example.com",   # <— placeholder
      ...
  )
  ```
  Confirmed as a known placeholder by open issue #111. Currently harmless because the charm uses the `client_credentials` grant type, which does not use `redirect_uri`.
- **Fix**: Replace with a real value or make it configurable; track against issue #111.
- **Linter rule**: not established (not mechanically checkable).

### 15. Auth config conflict returns `ActiveStatus` rather than `BlockedStatus`
- **Severity**: low
- **Kind**: ux
- **Where**: `src/utils.py:101-107`
- **Evidence**:
  ```python
  if oauth_relation_ready and (oauth_config.get("authn_issuer") or oauth_config.get("authn_jwks_url")):
      ...
      return ActiveStatus("Ignoring authentication config due to OAuth integration")
  ```
  When OAuth integration exists AND manual auth config is also set, the charm silently ignores the manual config and reports Active. `BlockedStatus` would more clearly alert the operator to the conflict.
- **Fix**: Return `BlockedStatus` instead of `ActiveStatus` for this case.
- **Linter rule**: not established (not mechanically checkable).

### 16. `HTTPClient` disables SSL verification
- **Severity**: low
- **Kind**: bug
- **Where**: `src/clients.py:16`
- **Evidence**:
  ```python
  self._session.verify = False
  ```
  All HTTP requests from action handlers ignore TLS certificate validation. Since the client connects to localhost (port 8080), this is low-risk in practice, but it's a hardening gap — the charm has a certificate transfer integration it could use to build a CA bundle instead.
- **Fix**: Load CA certificates from the certificate transfer integration and configure the session to verify against them.
- **Linter rule**: "`requests.Session` with `verify=False`" — mechanically checkable.

### 17. `PeerData.pop()` and `__setitem__` do not enforce leadership
- **Severity**: low
- **Kind**: bug
- **Where**: `src/integrations.py:276-282`
- **Evidence**: Both `pop` and `__setitem__` write to `peers.data[self._app]` without checking `self._model.unit.is_leader()`. In practice the callers (`_on_openfga_store_removed`, `_ensure_openfga_model`) check leadership first, so the class itself is the weak point — a future caller that forgets the check would silently corrupt shared app data.
- **Fix**: Add a leadership check within the class methods themselves, not just at call sites.
- **Linter rule**: "peer relation data write without leadership guard" — mechanically checkable.

### 18. README references Salesforce config that no longer exists
- **Severity**: low
- **Kind**: docs
- **Where**: `README.md:36-52`
- **Evidence**: The README shows config for `salesforce_domain` and `salesforce_consumer_secret`, but these are not declared in `charmcraft.yaml`. The CHANGELOG notes removal of the Salesforce dependency in v1.1.0 (2026-05-28).
- **Fix**: Remove the Salesforce-specific config section and update to match the current `charmcraft.yaml`.
- **Linter rule**: not established (not mechanically checkable).

### 19. Remove-application path triggers an unnecessary migration check
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:480-497` (`_holistic_handler` invoked from relation-broken/stop hooks)
- **Evidence**: During teardown, the charm runs `_holistic_handler`, which calls `_ensure_database_migration`, producing a "Waiting for database migration" status during removal. The remove/stop path should skip migration and just tear down.
- **Observed**: `juju remove-application hook-service` showed "Waiting for database migration" briefly before removal completed.
- **Fix**: Detect a departing/dying state in `_holistic_handler` and skip migration in that case.
- **Linter rule**: not established (not mechanically checkable).

## Worth copying

1. **Reconciler pattern** (`src/charm.py:480-497`): The `_holistic_handler` + `_ensure_*` sequence is a clean, readable pattern for k8s charms. Each `_ensure_*` method is independently testable, returns a boolean success indicator, and the chain short-circuits cleanly via `can_plan = can_plan and f()`.
2. **Dataclass-based integration data** (`src/integrations.py`): `DatabaseConfig`, `TracingData`, `OpenFGAIntegrationData`, `OAuthProviderData`, etc. are modelled as frozen dataclasses with `load()` classmethods and `to_env_vars()` methods, localising integration data extraction in one place.
3. **`EnvVarConvertible` Protocol** (`src/env_vars.py`): `PebbleService.render_pebble_layer` accepts `*env_var_sources: EnvVarConvertible`, letting each data class contribute its own `to_env_vars()` dict, merged in order. Makes adding a new env var source trivial.
4. **Action coverage in unit tests** (`tests/unit/test_charm.py`, classes `TestCreateGroupAction` through `TestGroupsListUsersAction`): every action has tests for success, failure, not-ready, and authenticated vs. unauthenticated modes.
5. **`_pebble_layer` as a property** (`src/charm.py:296-312`): computing the layer on-demand rather than mutating state means it's always derived from current state.
6. **Clean `charmcraft.yaml`**: well-documented config options, properly declared actions with params and required fields, explicit `assumes` (`juju >= 3.0.2`, `k8s-api`), `charm-user: non-root`, and proper resource declarations.

## Common-practice notes

- Standard `src/` + `lib/charms/` layout; `charmcraft.yaml` at root with parts for Rust build dependencies.
- No `metadata.yaml` — uses `charmcraft.yaml` exclusively (modern practice).
- `charm-user: non-root` — runs as non-root (uid/gid 584792).
- `startup: disabled` in Pebble — charm explicitly controls service lifecycle.
- `raw=True` in Traefik integration, required for the internal-route template; `templates/internal-route.json.j2` is clean, but the traefik_route library logs "Raw mode enabled" on every relation hook, which is misleading noise for internal routes.
- Peer relation for app data: `PeerData` class with version-keyed storage to invalidate stale data across upgrades — good pattern, though see Finding 17 on leadership enforcement.
- K8s API call volume: 3 HTTP GET/PATCH/dry-run calls per hook from `KubernetesComputeResourcesPatch` — upstream library behaviour, not the charm's fault.
- Custom `Secrets` class manages secrets manually rather than using the ops framework's built-in rotation/observation patterns — functional but more verbose.

## Tests

**Unit tests**: 91 tests, all passing. Coverage: 78% total, 89% on `charm.py`. Gaps: `cli.py` (38%), `clients.py` (35%), `secret.py` (75%). Tests use the ops testing framework (`testing.Context`, `testing.State`, `testing.Relation`, `testing.Container`, `testing.Secret`) — modern and idiomatic.

**Test quality**: Tests assert real Pebble layer contents, environment variables, and status messages. Action tests verify authenticated and unauthenticated paths, API failures, and pre-condition checks. The parametrized status test (`test_when_a_condition_failed`) covers all 8 failure modes.

**Coverage gaps**:
- `cli.py` methods beyond `get_service_version` and `run_cmd` are untested (migration, import, and user management CLI calls)
- `clients.py` is completely untested (mocked out in unit tests)
- `_on_pebble_check_failed` / `_on_pebble_check_recovered` are untested
- `_on_resource_patch_failed` is untested
- `_ensure_tls` is tested only as a holistic handler side effect
- Hydra token hook data population is tested implicitly but not directly

**Integration tests**: cover basic deployment, API health, ingress routing, scaling, and integration removal. Actions, OAuth, TLS, tenant-service-info, and the `authorization_enabled=false` path are untested (Finding 7). The upgrade test is `@pytest.mark.skip` and references outdated relation names (Finding 6).

**Lint**: `tox -e lint` passed cleanly (codespell, isort, ruff); 105 deprecation warnings from `data_platform_libs` and `loki_k8s` (upstream libraries, not this charm's code).

## Docs

- **README**: comprehensive, with usage examples, config documentation, action tables, and security/contributing links. One stale section references Salesforce config that no longer exists (Finding 18). OAuth configuration section is well documented.
- **CONTRIBUTING.md**: brief but functional — covers tox setup, testing, building, and deploying.
- **Charmhub description**: minimal ("Operator for Identity platform Hook Service"); would benefit from linking to the README's usage examples.
- **No published docs on Discourse**: only the repo README serves as documentation — acceptable for a platform-internal charm.
- **Terraform module**: well-structured with proper variables and outputs; uses `juju` provider `~> 1.0` and requires `model_uuid`.

## Open questions

1. **Does the charm need an explicit upgrade path?** Peer data keys on workload version, which naturally invalidates stale data, and there's no dedicated upgrade-charm handler — the reconciler handles everything through `_holistic_handler`. The upgrade integration test is skipped and outdated (Finding 6), so it's unclear whether migrations across versions actually work.
2. **What happens with 2+ units and peer data sharing under leadership handover?** The integration test scales to 2 units but doesn't validate peer data sharing or leadership handover directly. `PeerData` stores under `model.app`, shared across all units, but `pop`/`__setitem__` assume the caller checks leadership (Finding 17) — a non-leader calling `pop` on a missing relation returns `{}` rather than raising, which could mask stale OpenFGA model IDs on non-leader units.
3. **Is the OAuth `redirect_uri` placeholder (issue #111) genuinely harmless long-term?** The charm's `client_credentials` grant type doesn't use `redirect_uri` today, but a future provider requiring it for client registration validation would break.
4. **Does `_on_database_integration_broken` need to clean up OpenFGA state?** It currently just calls `_holistic_handler`. If the database integration is removed mid-migration, `migration_needed` returns `False` (because `is_resource_created()` is `False`), but peer data may still hold a stale OpenFGA model ID — `_on_openfga_store_removed` cleans that key up on OpenFGA removal, but database removal does not.
