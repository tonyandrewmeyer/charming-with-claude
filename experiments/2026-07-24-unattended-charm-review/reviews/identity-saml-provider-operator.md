# identity-saml-provider-operator

A well-structured Kubernetes charm wrapping the `canonical/identity-saml-provider` OCI image (v0.1.6) to provide a SAML-to-OIDC bridge via Ory Hydra. Requires PostgreSQL, Traefik (ingress), Hydra (OAuth), and optionally a CA certificate provider. Architecture is clean, with protocol-based decoupling and a holistic reconciliation loop, and the unit test suite is large (104 tests). But error handling around Juju secrets is not production-ready: an unreadable secret crashes the `config-changed` hook into ErrorStatus, and the `receive-ca-cert` integration — declared optional in metadata — is functionally required, since removing it drives the workload into an unbounded crash loop. A maintainer should fix the `ModelError` handling in `JujuSecretResolver.resolve` and the `receive-ca-cert` optionality mismatch before anything else; both are reachable by an operator doing ordinary maintenance (secret rotation, relation changes), not just misconfiguration.

| | |
|---|---|
| Repo | canonical/identity-saml-provider-operator @ e64cb6c (2026-07-23) |
| Charms | identity-saml-provider-operator |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3, channel latest/edge, rev 3 |
| Reviewed | 2026-09-02 |

## What it does

The charm deploys a SAML Identity Provider as a Kubernetes workload container. It reads SAML signing credentials from a Juju secret, database credentials from a PostgreSQL integration, OAuth/client credentials from a Hydra integration, public-route configuration from Traefik, and CA certificates from a certificate-transfer provider. It renders Pebble layer environment variables and certificate files into the container and manages the workload lifecycle. The leader unit also runs database migrations via a CLI action. The workload binary is a Go application bridging SAML SPs to OIDC clients via Hydra.

## Deployment log

Controller: concierge-k8s-3 (Juju 3.6.25), model `rv-saml-review3`.

1. Deployed `postgresql-k8s`/14/stable, `traefik-k8s`/latest/stable, `self-signed-certificates`/1/stable, `hydra`/latest/stable — all reached ActiveStatus after integration (hydra required traefik with TLS certs, which required integrating traefik with self-signed-certificates).
2. Deployed `identity-platform-login-ui-operator` to satisfy hydra's `ui-endpoint-info` requirement. Hydra reached ActiveStatus.
3. Deployed `identity-saml-provider-operator` from charmhub latest/edge (rev 3).
4. Created Juju secret `saml-credential` with `private-key` and `public-cert` fields.
5. Granted secret to charm, set `saml_credentials=secret:<id>`, integrated with database, public-route (traefik), oauth (hydra), receive-ca-cert (self-signed-certificates).
6. Charm initially BlockedStatus — workload crashed because `OAuthRequirer.is_client_created()` returned False (hydra not yet Active). After hydra became ActiveStatus, charm reached ActiveStatus.
7. Charm again BlockedStatus — secret creation stored literal `"$(cat /tmp/saml-key.pem)"` strings instead of actual PEM (shell expansion captured as string). Recreated secret with actual PEM content. Charm reached ActiveStatus.
8. `run-migration` action on leader succeeded; on non-leader correctly failed with "Only the leader unit can run the database migration".
9. Config change `dev=true` updated `SAML_PROVIDER_DEV_MODE: "true"` in the pebble plan and restarted the service.
10. Removed oauth relation → BlockedStatus("Missing integration oauth"). Restored → ActiveStatus.
11. Removed database relation → BlockedStatus("Missing integration database"). Restored → ActiveStatus.
12. Removed public-route relation → BlockedStatus("Missing integration public-route"). Restored → ActiveStatus.
13. Removed `receive-ca-cert` relation → workload entered a continuous crash loop with `tls: failed to verify certificate: x509: certificate signed by unknown authority`. Charm went to BlockedStatus("Failed to start the service"). Restored → ActiveStatus within ~20 seconds.
14. Scaled down from 2 to 1 units — succeeded.
15. `juju refresh` → "already up-to-date" (rev 3 is latest).
16. Unit tests: 104 passed. `ruff`: no errors. `mypy`: 2 errors (both documented findings below).
17. After a fresh charmhub re-deploy, the charm went to ErrorStatus on `database-relation-changed` because the SAML secret was not re-granted to the new application instance. Recovery: `juju resolved` after granting the secret restored BlockedStatus → ActiveStatus.
18. Invalid resource limits (`cpu_limit=not-a-number, memory_limit=not-a-size`) → BlockedStatus with clear message `Failed obtaining resource limit spec: Invalid limits spec: ...`. Clearing the limits restored ActiveStatus.
19. `juju remove-application --force` → clean teardown, no orphaned resources.
20. `run-migration` with `timeout=5` and `timeout=1` → both succeeded (database already migrated).
21. (Round 5) `pebble stop identity-saml-provider` → service inactive, checks down; charm went BlockedStatus within ~5s; `pebble-check-failed` hooks fired every ~10s with no charm handler; `pebble start` recovered to ActiveStatus with no `pebble_check_recovered` handler either.
22. (Round 5) Secret rotation: `juju update-secret saml-credential` moved revision 1 → 2; charm re-rendered the pebble layer via `secret-changed` and stayed ActiveStatus throughout (`juju show-secret` showed `revision: 2, updated: 2026-09-02T00:36:14Z`).
23. (Round 5) `juju restart unit identity-saml-provider-operator/0` → "restart is not a juju command" in Juju 3.6.25.

## Observed behaviour

- **Startup time**: unit moved Waiting → Active in ~90 seconds after all integrations were established.
- **Hook frequency**: `update-status` fires approximately every 5 minutes (observed 00:10:06 UTC, then again ~5 minutes later). A config change (`dev=true`) triggered exactly one hook invocation.
- **Pebble layer**: service `identity-saml-provider` has `startup: disabled` — started manually by the charm in `pebble_ready`.
- **Config-diff restart**: changing `dev` to `true` caused a pebble layer re-render and service restart (`SAML_PROVIDER_DEV_MODE: "true"` visible in `pebble plan` afterward).
- **Run-migration action**: leader completes successfully; non-leader correctly fails with "Only the leader unit can run the database migration".
- **Missing oauth relation**: workload crashed (could not reach Hydra); charm went BlockedStatus.
- **Empty SAML cert**: workload refuses to start — `tls: failed to find any PEM data in certificate input`. Charm correctly BlockedStatus throughout.
- **Garbage PEM secret**: charm reads the secret successfully (it's accessible) and writes the garbage to the cert/key files; workload crashes on startup with the same PEM error. Charm goes BlockedStatus. Pebble keeps the workload in a crash loop with unbounded exponential backoff (4s → 8s → 16s → 32s → ...).
- **Manually stopped service does not auto-recover**: `pebble stop identity-saml-provider` leaves the service `inactive`; pebble does not auto-restart it (`startup: disabled`). Charm detects the failure via the pebble check and goes BlockedStatus, but the service stays inactive until manually started.
- **Unreadable secret → ErrorStatus**: setting `saml_credentials` to a secret the charm cannot read causes `secret-get` to fail with `ERROR permission denied`. The uncaught `ops.model.ModelError` propagates through `config-changed` and crashes the hook. Both units go ErrorStatus. Recovery requires `juju resolved` then a config change to a valid secret.
- **Missing optional CA cert**: removing `receive-ca-cert` makes `TransferredCertificates.load()` return `ca_bundle=""`; `HydraCertificates.to_env_vars()` returns `{}`, so `SAML_PROVIDER_HYDRA_CA_CERT_PATH` is absent from the pebble layer. The workload fails to verify Hydra's self-signed TLS cert (`tls: failed to verify certificate: x509: certificate signed by unknown authority`) and enters a continuous crash loop with the same unbounded backoff. Charm goes BlockedStatus. Restoring the integration recovers to ActiveStatus within ~20 seconds. The rest of the pebble layer (database credentials, OAuth info, SAML paths) remains correct — only the CA cert path env var is missing.
- **Pebble check-failed hook fires with no charm handler**: when the workload is down, `identity-saml-provider-pebble-check-failed` fires (observed roughly every ~10s) with no charm-side logic; the charm relies entirely on pebble's own `on-check-failure: alive: restart` policy. `pebble-check-recovered` likewise has no handler.
- **Scale-up transient BlockedStatus**: adding a second unit causes brief BlockedStatus("Missing SAML bridge certificate") then BlockedStatus("waiting for resources patch to apply"), converging to ActiveStatus within ~2 minutes.
- **Scale-down**: `juju remove-unit identity-saml-provider-operator --num-units 1` succeeded without incident.
- **Refresh**: `juju refresh` returns "already up-to-date" — rev 3 (edge) is the latest available.
- **Update-status cost**: each firing triggers `_holistic_handler`, which calls `add_layer` then `replan()` (no restart needed) — a no-op in terms of service state but an unnecessary pebble layer push + replan every cycle.
- **Resource use**: pod runs 2 containers (charm + workload). No metrics-server available in the cluster to measure actual usage (unverified beyond that).
- **Status precedence**: BlockedStatus correctly overrides other statuses in `juju status` output.
- **PebbleService.plan()**: on every `_holistic_handler` invocation, calls `add_layer` then either `replan()` (no file changed) or `restart()` (file changed) — no short-circuit path skips both.
- **Redeploy reproduces the unreadable-secret bug**: re-deploying after teardown hit the same `ops.model.ModelError: ERROR permission denied` in the `database-relation-changed` hook because the secret was not re-granted to the new application. Unit went ErrorStatus; recovered via `juju resolved` after granting the secret. Confirms the bug is reliably reproducible on redeploy when secrets aren't re-managed.
- **Invalid resource limits → clear BlockedStatus**: `cpu_limit=not-a-number`, `memory_limit=not-a-size` → `Failed obtaining resource limit spec: Invalid limits spec: {'cpu': 'not-a-number', 'memory': 'not-a-size'}`. `KubernetesComputeResourcesPatch.get_status()` (observability_libs) correctly translates the validation error to BlockedStatus. Clearing the limits restores ActiveStatus within seconds.
- **`run-migration` with custom timeout**: accepts a `timeout` parameter (default 120s). `timeout=5` and `timeout=1` both succeeded because the database was already migrated. A longer-running migration exceeding the timeout would raise `MigrationError`, caught in the action handler as `event.fail("Database migration failed: <error>")`.
- **`juju remove-application --force`**: clean teardown — pod terminated, unit removed, all relations broken, no orphaned resources. `--force` required for non-interactive removal.
- **Workload container pebble API**: reachable from the charm container via `kubectl exec ... -- /charm/bin/pebble services`; the workload service shows `startup: disabled`, `current: active`, confirming the charm starts it manually in `pebble_ready`.
- **Workload container has no shell**: `kubectl exec -- /bin/sh`, `cat`, `python3` all fail ("executable file not found"); only the Go binary is present. Diagnosis requires `pebble exec`/`pebble logs`/`pebble services`.

## Findings

### `JujuSecretResolver.resolve` does not catch `ops.model.ModelError` — unreadable secret crashes the hook
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/configs.py:138` (`JujuSecretResolver.resolve`)
- **Evidence**: The method catches `SecretNotFoundError` but not `ops.model.ModelError`. When `secret.get_content(refresh=True)` is called on a secret the charm cannot read (not granted, or containing an unreadable file path), it raises `ModelError("ERROR permission denied")`. This propagates through `_pebble_layer` → `_holistic_handler` → `_on_config_changed` and crashes the `config-changed` hook:
  ```
  ops.hookcmds._utils.Error: command ('secret-get', '--format=json', 'secret:...') exited with status 1
  ops.model.ModelError: ERROR permission denied
  hook "config-changed" failed: exit status 1
  ```
  Both units go to ErrorStatus. Reproduced independently on redeploy in the `database-relation-changed` hook when the secret was not re-granted to the new application. Recovery is `juju resolved` after granting the secret, then a config change (if needed).
- **Impact**: Any secret misconfiguration (wrong ID, not granted, unreadable path) causes ErrorStatus rather than a descriptive BlockedStatus. An operator cannot distinguish this from a code bug, and it recurs reliably across redeploys where secret grants aren't re-established.
- **Fix**: Catch `ModelError` in `JujuSecretResolver.resolve()`, return `{}` and log a warning; or translate it at the `CharmConfig.to_service_configs()` level into a `PebbleServiceError` that `_holistic_handler` already maps to BlockedStatus.
- **Linter rule**: not mechanically checkable — requires knowing which ops calls raise `ModelError`.

### `receive-ca-cert` is declared optional but is functionally required — removing it causes an unbounded crash loop
- **Severity**: critical
- **Kind**: bug / ux
- **Where**: `src/integrations.py:198` (`TransferredCertificates.to_env_vars`), `src/integrations.py:202` (`TransferredCertificates.to_service_configs`)
- **Evidence**: `receive-ca-cert` is `optional: true` in `charmcraft.yaml`, but `TransferredCertificates.to_env_vars()` returns `{}` when `ca_bundle` is empty, so `SAML_PROVIDER_HYDRA_CA_CERT_PATH` is absent from the pebble layer. Workload log: `error: "tls: failed to verify certificate: x509: certificate signed by unknown authority"`. Pebble restarts the workload with unbounded exponential backoff (4s → 8s → 16s → 32s → ...). Charm shows BlockedStatus("Failed to start the service") with no indication the CA cert is the cause. Verified by removing the integration in the live deployment; recovers within ~20 seconds on restore.
- **Impact**: Any Hydra deployment using self-signed TLS (the common case) makes this integration effectively mandatory. An operator removing it — e.g., to rotate certs — triggers a crash loop with no actionable error.
- **Fix**: (a) mark `receive-ca-cert` as `optional: false` and update the README, or (b) fall back to the workload's system CA store when `ca_bundle` is empty, or (c) detect this failure mode in `collect_status` and set a specific BlockedStatus message. (a) is the most correct fix.
- **Linter rule**: not mechanically checkable.

### Unit tests are blind to Kubernetes resource-limit bugs — conftest auto-mocks `get_status()` to `ActiveStatus`
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py:14`
- **Evidence**:
  ```python
  @pytest.fixture(autouse=True)
  def mocked_k8s_resource_patch(mocker: MockerFixture) -> None:
      mocked_patch = mocker.patch("charm.KubernetesComputeResourcesPatch", autospec=True)
      mocked_patch.return_value.get_status.return_value = ActiveStatus()
  ```
  This autouse fixture always mocks `KubernetesComputeResourcesPatch.get_status()` to `ActiveStatus()`. No unit test exercises the real method. The invalid resource limits case (`cpu_limit=not-a-number`) was confirmed correct at runtime, but a regression here would not be caught by the unit suite.
- **Impact**: A developer breaking the resource-limits handling would get a green unit test run despite the behaviour actually being broken.
- **Fix**: Add a unit test that bypasses the autouse mock and exercises `KubernetesComputeResourcesPatch.get_status()` with invalid inputs, asserting BlockedStatus.
- **Linter rule**: "autouse conftest fixture mocks library return value without a corresponding un-mocked test" — not mechanically checkable.

### Crash loop on garbage PEM secret — pebble restarts the workload with unbounded backoff
- **Severity**: high
- **Kind**: bug / ux
- **Where**: `src/configs.py:67` (`SAMLBridgeKey.from_sources`), `src/configs.py:88` (`SAMLBridgeCert.from_sources`)
- **Evidence**: When the secret contains non-PEM garbage, `JujuSecretResolver.resolve()` returns the (unvalidated) content and `SAMLBridgeKey.from_sources` writes it to the key file as-is. The workload crashes immediately with `tls: failed to find any PEM data in certificate input`, and pebble restarts it with exponential backoff (4s → 8s → 16s → 32s → ...) with no upper bound. Verified in the live deployment.
- **Impact**: An operator who creates a secret with wrong content gets an endless crash loop; the generic BlockedStatus ("Failed to start the service, please check the logs") does not point at the cert/key.
- **Fix**: In `SAMLBridgeKey.from_sources`/`SAMLBridgeCert.from_sources`, raise a `PebbleServiceError` if content is empty or not valid PEM, producing a specific BlockedStatus message.
- **Linter rule**: not mechanically checkable.

### `PebbleService` shares a module-level mutable `PEBBLE_LAYER_DICT` across instances
- **Severity**: high
- **Kind**: bug
- **Where**: `src/services.py:128`, `src/services.py:148`
- **Evidence**:
  ```python
  self._layer_dict: LayerDict = PEBBLE_LAYER_DICT   # reference, not copy
  ...
  self._layer_dict["services"][WORKLOAD_SERVICE]["environment"] = env_vars
  ```
  Confirmed experimentally: `svc1._layer_dict is PEBBLE_LAYER_DICT` is `True`. Every `PebbleService` instance mutates the same module-level dict. mypy flags the assignment.
- **Impact**: Currently masked because each render sets the full `environment` dict, overwriting the previous value, so single-instance operation doesn't misbehave observably. But the pattern is architecturally wrong and shared across tests too; a future partial-render code path would leak state between instances/tests.
- **Fix**: Use `copy.deepcopy(PEBBLE_LAYER_DICT)` in `PebbleService.__init__`.
- **Linter rule**: rule flagging direct assignment of a module-level mutable literal to an instance attribute without `.copy()`/`deepcopy()`.

### Auto-migration failure silently leaves the charm in stale status
- **Severity**: high
- **Kind**: bug / ux
- **Where**: `src/charm.py:300` (`_on_database_created`)
- **Evidence**:
  ```python
  try:
      self._cli.migrate(DatabaseConfig.load(self.database_requirer).dsn)
  except MigrationError:
      logger.error("Auto migration job failed. Please use the run-migration action")
      return  # no status change
  ```
  On `MigrationError`, the handler logs and returns without touching unit status. The unit stays in whatever status it had before, typically ActiveStatus, even though the workload may not have correct migration state. The unit test `test_when_migration_failed` (`test_charm.py:254`) only asserts `mocked_charm_holistic_handler.assert_not_called()` and log content — it never checks status, confirming this is invisible to the test suite.
- **Impact**: A failed migration is silent; the charm looks healthy while the workload may be misconfigured. Operators must find this via `juju debug-log`.
- **Fix**: Set `self.unit.status = BlockedStatus("Database migration failed. Run the run-migration action manually")` before returning.
- **Linter rule**: not mechanically checkable.

### `CharmConfig.to_service_configs` passes `None` to `SecretResolver.resolve`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/configs.py:169-172` (`CharmConfig.to_service_configs`); the `SecretResolver.resolve` protocol signature it violates is at `src/configs.py:122`
- **Evidence**:
  ```python
  secret_configs = {
      key: self._secret_resolver.resolve(self._config.get(key))  # config.get can return None
      for key in self.SECRET_CONFIGS
  }
  ```
  `self._config.get(key)` is typed `int | float | str | None`; `resolve()` expects `str`. mypy reports this as one of the repo's 2 live errors.
- **Impact**: If `saml_credentials` is unset, `None` is passed to `resolve()` — a latent type violation.
- **Fix**: Guard with `if self._config.get(key): ...` or coerce with `str(self._config.get(key, ""))`.
- **Linter rule**: `mypy` already catches this — it's a live, unaddressed error in the repo.

### Missing/uncreated OAuth client omits required env vars from the pebble layer
- **Severity**: high
- **Kind**: bug / ux
- **Where**: `src/charm.py:202` / `src/integrations.py:167-168` (`OAuthIntegration.to_env_vars`), `src/utils.py:67` (`NOOP_CONDITIONS`)
- **Evidence**: `to_env_vars()` returns `{}` when `self._requirer.is_client_created()` is False. `NOOP_CONDITIONS` includes `oauth_integration_exists`, which only checks relation existence, not whether Hydra has actually registered the OAuth client. When the relation exists but the client isn't created yet, `SAML_PROVIDER_HYDRA_PUBLIC_URL`, `SAML_PROVIDER_OIDC_CLIENT_ID`, and `SAML_PROVIDER_OIDC_CLIENT_SECRET` are absent, and the workload fails with `dial tcp [::1]:4444: connect: connection refused` (also observed as `localhost:4444` in a separate test run). Observed directly in the first deployment: transient BlockedStatus until Hydra reached ActiveStatus.
- **Impact**: A correctly-configured deployment shows a generic BlockedStatus("Failed to start the service") purely because Hydra hasn't finished starting — with no message indicating the OAuth client is still being created.
- **Fix**: Add an `oauth_client_created` condition checking `is_client_created()` to `NOOP_CONDITIONS`, and give it a descriptive `WaitingStatus` message in `_on_collect_status`.
- **Linter rule**: not mechanically checkable.

### No explicit `pebble-check-failed` / `pebble-check-recovered` handlers
- **Severity**: medium
- **Kind**: test-gap / ux
- **Where**: `src/charm.py` (no `framework.observe(self.on.pebble_check_failed, ...)` or `pebble_check_recovered`)
- **Evidence**: Confirmed live — when the workload is down, `identity-saml-provider-pebble-check-failed` fires repeatedly (~every 10s) with no charm-side handler; pebble's own `on-check-failure: alive: restart` policy handles restart. On recovery, `pebble-check-recovered` fires with no handler either; the charm detects recovery only via `_on_collect_status`/`WorkloadService.is_running`.
- **Impact**: The charm can't distinguish a transient failure from a persistent one, and would not react at all if pebble's restart policy were changed or the service set to `startup: ignore`.
- **Fix**: Add explicit handlers for both events.
- **Linter rule**: not mechanically checkable.

### Wrong secret field names produce empty cert/key files with an opaque crash message
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/configs.py:67` (`SAMLBridgeKey.from_sources`), `src/configs.py:88` (`SAMLBridgeCert.from_sources`)
- **Evidence**: The resolver looks for exact keys `private-key` and `public-cert`. If a secret used other key names, `configs.get("private-key", "")` returns `""` silently and the key file is written empty, leading to the same `tls: failed to find any PEM data in certificate input` crash. `juju add-secret` rejects underscored key names via CLI validation, but the charm itself performs no schema validation on read, so this path is reachable by any secret source that doesn't go through that CLI check (unverified whether such a path exists in practice).
- **Impact**: A field-name typo produces a crash message that doesn't hint the field name is wrong.
- **Fix**: In `JujuSecretResolver.resolve()`, validate presence of `private-key`/`public-cert`; if missing, log a warning and return `{}` so `_holistic_handler` raises `PebbleServiceError` → BlockedStatus.
- **Linter rule**: not mechanically checkable without the secret schema.

### Terraform module's `outputs.tf` misdocuments provides/requires
- **Severity**: medium
- **Kind**: docs
- **Where**: `terraform/outputs.tf`
- **Evidence**: Declares `provides: {metrics-endpoint, grafana-dashboard}` and `requires: {database, oauth, public-route, receive-ca-cert, logging}`. The charm itself declares no `provides` at all, and requires only `database`, `public-route`, `oauth`, `receive-ca-cert` — there is no `logging` integration and no `prometheus_scrape`/`grafana-dashboard` library in use. The terraform module also lacks a `variables.tf`, so operators can't configure charm inputs via terraform (unverified whether this is intentional).
- **Impact**: An operator provisioning via this terraform module will attempt relations to charms that don't exist and miss relations that do.
- **Fix**: Remove `metrics-endpoint`/`grafana-dashboard` from `provides` and `logging` from `requires`; align with actual charm metadata.
- **Linter rule**: not mechanically checkable.

### `PublicRouteIntegration.config` opens a template by relative path with no existence check
- **Severity**: medium
- **Kind**: bug / lint
- **Where**: `src/integrations.py:134` (`PublicRouteIntegration.config`)
- **Evidence**:
  ```python
  with open("templates/public-route.json.j2", "r") as file:
      template = Template(file.read())
  ```
  No `exists()` guard; a missing file raises an uncaught `FileNotFoundError` in the `public-route-changed` hook. The relative path is also a hidden implicit dependency on the current working directory.
- **Impact**: If the template file is ever removed or the CWD assumption breaks, the hook crashes uncaught.
- **Fix**: Wrap in try/except setting `BlockedStatus("Public route template not found")`, or embed the template as a string constant in `constants.py`.
- **Linter rule**: "hook handler calls `open()` without existence check" — mechanically checkable.

### `add_layer` called on every `update-status` even when the pebble layer is unchanged
- **Severity**: medium
- **Kind**: performance / test-gap
- **Where**: `src/services.py:133` (`PebbleService.plan`)
- **Evidence**: `plan()` unconditionally calls `add_layer(combine=True)` before checking whether any files changed, then `replan()` or `restart()`. Confirmed by the existing test `test_plan_when_no_container_file_changed`, which shows `replan()` is called even when no file changed — no test asserts `add_layer` is skipped when the layer is identical. Observed live: `update-status` fires roughly every 5 minutes and re-triggers this path each time.
- **Impact**: Every `update-status` (and every other hook reaching `_holistic_handler`) does a pointless pebble layer push + replan cycle, adding latency with no benefit.
- **Fix**: Compare the rendered layer to the current plan before calling `add_layer`; skip both calls if unchanged.
- **Linter rule**: "hook handler always calls `add_layer` without comparing to current plan" — mechanically checkable by asserting `add_layer` is not called when the layer is unchanged.

### `oauth_integration_exists` NOOP condition doesn't check `is_client_created()`
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/utils.py:67` (`NOOP_CONDITIONS`), `src/integrations.py:167-168` (`OAuthIntegration.to_env_vars`)
- **Note**: This overlaps the "Missing/uncreated OAuth client" finding above (same root cause, complementary fix suggestion — kept separate as the draft/notes treat it as a distinct action item).
- **Evidence**: `oauth_integration_exists` checks only `bool(charm.model.relations[OAUTH_INTEGRATION_NAME])`, not whether Hydra has registered the client. Observed directly: transient BlockedStatus during Hydra startup until the client is created.
- **Impact**: Duplicated/related to the high-severity finding above; the fix would additionally need to update `NOOP_CONDITIONS` specifically (not just the collect_status message).
- **Fix**: Add `oauth_client_created` condition and register it in `NOOP_CONDITIONS`.
- **Linter rule**: not mechanically checkable.

### `_on_collect_status` unconditionally adds `ActiveStatus`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:352` (`_on_collect_status`); the unconditional `event.add_status(ActiveStatus())` is at `src/charm.py:394`
- **Evidence**: `event.add_status(ActiveStatus())` is called unconditionally. ops resolves `CollectStatusEvent` to the highest-priority status (error > blocked > waiting > active), so in practice higher-priority statuses win and this doesn't cause incorrect behaviour today.
- **Impact**: Fragile if ops' priority ordering changes or a new lower-priority status is introduced; also misleading to reviewers.
- **Fix**: Wrap in `if all_prerequisites_met: event.add_status(ActiveStatus())`.
- **Linter rule**: "CollectStatus handler adds ActiveStatus unconditionally" — mechanically checkable via AST.

### `leader_unit` decorator defined but never used
- **Severity**: low
- **Kind**: lint
- **Where**: `src/utils.py:20`, `src/utils.py:29`
- **Evidence**: `leader_unit` decorator and `integration_existence` factory are defined but no handler in `charm.py` uses `@leader_unit`; leadership checks are done inline instead.
- **Impact**: Dead code.
- **Fix**: Remove the decorator.
- **Linter rule**: ruff `F401` (unused import/function).

### `HydraCertificates` silently writes empty content for a missing CA bundle
- **Severity**: low
- **Kind**: bug
- **Where**: `src/configs.py:96` (`HydraCertificates.from_sources`)
- **Evidence**: `configs.get("hydra_ca_certs", "")` returns `""` when absent, and the CA cert file is written empty. Combined with `TransferredCertificates.to_env_vars()` returning `{}` for an empty bundle, no CA path env var is set and the file itself is empty — the workload fails TLS verification silently (this is the same code path as the `receive-ca-cert` critical finding above).
- **Impact**: Same root cause as the critical `receive-ca-cert` finding; listed separately per the draft/notes as the specific silent-write behaviour.
- **Fix**: See fix for the `receive-ca-cert` critical finding.
- **Linter rule**: not mechanically checkable.

### Workload container has no shell — diagnostics require pebble, not `kubectl exec`
- **Severity**: low
- **Kind**: ux
- **Where**: workload OCI image `ghcr.io/canonical/identity-saml-provider:v0.1.6`
- **Evidence**: `kubectl exec ... -- /bin/sh`, `cat`, `python3` all fail with "executable file not found"; the container ships only the Go binary. Investigation requires `pebble logs`/`pebble exec`/`pebble services`.
- **Impact**: Operators used to `kubectl exec`-based debugging will be surprised; not itself a bug.
- **Fix**: Document in the README that diagnosis should use `kubectl logs` and pebble commands, not `kubectl exec`. Optionally ship a minimal shell in the image.
- **Linter rule**: not mechanically checkable from the charm repo.

### `TraefikRouteRequirer._relation` private attribute mutated directly in event handler
- **Severity**: low
- **Kind**: lint / fragility
- **Where**: `src/charm.py:319` (`_on_public_route_changed`)
- **Evidence**:
  ```python
  # This is needed due to how traefik_route lib handles the event
  self.public_route_requirer._relation = event.relation
  ```
  `TraefikRouteRequirer` (LIBPATCH=3) stores the relation at `__init__` and exposes no public `set_relation()`. The workaround is documented in a comment but mutates a private attribute directly.
- **Impact**: Couples the charm to the library's internals; a future library refactor could silently break this.
- **Fix**: Request a public `set_relation()` method upstream, or find an approach that doesn't touch the private attribute.
- **Linter rule**: "directly mutates private attribute of library object" — mechanically checkable via AST.

### Database user is granted cluster-wide `SUPERUSER`
- **Severity**: medium
- **Kind**: bug (security posture)
- **Where**: `src/charm.py:124-128`
- **Evidence**: `DatabaseRequires(…, extra_user_roles="SUPERUSER")`.
- **Impact**: the SAML provider's DB user gets superuser on the whole PostgreSQL instance, not just its own `saml_provider` database. If the workload is compromised (it's an internet-facing SAML/SSO component), that's full control of the shared database cluster, including any other tenants on the same PostgreSQL charm. It's a common Canonical-identity-platform pattern, but broader than the migration likely needs (typically only `CREATE EXTENSION` in its own DB).
- **Fix**: investigate whether the migration can run under a less-privileged role (e.g. one that can create extensions/schemas in its own database); if `SUPERUSER` is genuinely required, document why.
- **Linter rule**: mechanically checkable — "`extra_user_roles` contains `SUPERUSER`/`CREATEDB`/`CREATEROLE`".
- **Provenance**: carried over from the 2026-08-13 review of this charm (same commit `e64cb6c`); citations re-verified 2026-09-02.

### Workload version re-exec'd on every hook (uncached)
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:215-223` (`migration_needed`) → `src/services.py:69-71` (`application_version`)
- **Evidence**: `application_version` calls `self._cli.get_application_version()` on every access (runs `/usr/bin/identity-saml-provider version` in the container with a 20 s timeout, `src/cli.py:19-33`). `migration_needed` is evaluated by `NOOP_CONDITIONS` on every hook and by `_on_collect_status`. Measured: a single `config-changed` produced 2 new `version` execs.
- **Impact**: the OCI image version is fixed for the life of a pod; re-execing it on every hook (including `update-status` every 5 min, per unit) is pure overhead and adds a 20 s worst-case stall per hook if the container is slow.
- **Fix**: cache the version at `pebble-ready` (or in `StoredState`/peer data) and re-read only on upgrade events.
- **Linter rule**: mechanically checkable — "hook handler path calls `container.exec` without caching a value that is invariant for the pod lifetime".
- **Provenance**: carried over from the 2026-08-13 review of this charm (same commit `e64cb6c`); citations re-verified 2026-09-02.

### `saml_bridge_certs_exist` checks existence, not content
- **Severity**: low
- **Kind**: bug / ux
- **Where**: `src/utils.py:67-74`
- **Evidence**: `container.exists(SAML_BRIDGE_CERT) and container.exists(SAML_BRIDGE_KEY)` — files pushed empty still pass. Observed with a junk secret: empty files existed, so the precise "Missing SAML bridge certificate and/or key file" status was skipped and the generic "Failed to start the service" was shown instead.
- **Impact**: a misconfigured/rotated secret that lacks the two fields produces a less-precise status; operators have to dig through container logs to learn the cert is empty.
- **Fix**: compare file content (the `ContainerFile.from_workload_container` machinery already reads content) rather than `exists()`.
- **Linter rule**: mechanically checkable — "`saml_bridge_certs_exist` uses `container.exists` on files whose content the charm itself writes".
- **Provenance**: carried over from the 2026-08-13 review of this charm (same commit `e64cb6c`); citations re-verified 2026-09-02.

## Worth copying

- **Protocol-based decoupling** (`src/configs.py`, `src/env_vars.py`): `EnvVarConvertible`, `ServiceConfigSource`, `ContainerFile`, `SecretResolver` protocols cleanly separate domain logic from Juju APIs, making the adapters easy to test with mocks.
- **Holistic reconciliation** (`src/charm.py:231`): `_holistic_handler` converges every event to a single full pebble-layer re-render — the right model for idempotent reconciliation.
- **NOOP/EVENT_DEFER condition split** (`src/utils.py:67-77`): separates no-op conditions from defer conditions via a `Condition` type alias, making failure-mode intent explicit.
- **ADR for secrets migration** (`docs/adr/001-saml-credentials-via-juju-secret.md`): explains not just what changed but why the prior tls-certificates approach was wrong — a good template for other charms.
- **Config dataclasses for integration data** (`src/integrations.py:57-95`): `DatabaseConfig`, `TransferredCertificates`, etc. are frozen dataclasses representing external data as immutable value objects.
- **Comprehensive unit test suite**: 104 scenario/state-transition tests using `ops.testing.Context`, covering every hook handler and integration adapter, with clean reusable `conftest.py` fixtures.
- **`peer_data` migration versioning**: storing the migration version per database relation ID in peer app data is a clean way to track per-database migration state across leader elections.
- **`remove_integration` fixture** (`tests/integration/util.py`): context-manager fixture that auto-restores the relation after the test body, preventing tests from leaving the deployment broken.

## Common-practice notes

- Uses `ops` 3.8.0 with `ops.testing.Context` scenario testing — modern standard.
- Libraries follow `lib/charms/<name>/v<N>/` convention: `certificate_transfer_interface.v1` (LIBPATCH=15), `data_platform_libs.v0` (LIBPATCH=58), `hydra.v0` (LIBPATCH=11), `observability_libs.v0` (LIBPATCH=9), `traefik_k8s.v0` (LIBPATCH=3). `hydra.v0`'s `is_client_created()` is typed `-> bool` but returns `None` when there are no relations — a type-annotation bug in the library, not this charm; the charm's `if not is_client_created()` handles it correctly since `None` is falsy.
- Standard `src/` layout, no `charm.py` at repo root.
- `CharmConfig.CONFIGS`/`SECRET_CONFIGS` explicit allowlists are a good pattern.
- No `StoredState`; peer relation app data used for cross-unit state (migration version) — appropriate for leader-based state.
- No explicit upgrade handler; `juju refresh` triggers `config-changed` → `_holistic_handler`, which should work but has no explicit upgrade narrative.
- `run-migration` action declared in `charmcraft.yaml` rather than a separate `actions.yaml` — modern convention.
- Correctly observes `on.secret_changed` to re-render the pebble layer on SAML credential rotation (confirmed live — revision 1→2 rotation kept the charm ActiveStatus).
- Uses `KubernetesComputeResourcesPatch` from observability_libs for resource limits — standard for k8s charms.
- pre-commit configured with isort, ruff, mypy, codespell, markdownlint, conventional-commit.
- `tox.ini` separates `fmt`, `lint`, `unit`, `integration` environments; `integration` requires `CHARM_PATH`.
- `deps/cosl` is vendored but not imported by the charm (which uses `lib/charms/observability_libs/v0/` instead); `cosl/coordinated_workers/__init__.py` raises `ImportError` pointing at a separate package — irrelevant to this charm but unclear why it's vendored (unverified whether intentional).

## Tests

**Unit tests** (`tests/unit/`): 104 tests, all passing (1.53–1.66s across runs). Uses `ops.testing.Context` for state-transition testing; covers every event handler, integration adapter, CLI, and services layer. No external dependencies required.

Coverage gaps relative to the risks found:
- `PublicRouteIntegration.config` not tested against the real Jinja template file.
- No test asserts `add_layer`/`replan` are skipped when the layer is unchanged (`test_plan_when_no_container_file_changed` only confirms `replan()` IS called).
- `JujuSecretResolver.resolve` with `ModelError` (unreadable secret) — untested; confirmed live bug. `test_configs.py` covers `SecretNotFoundError` but not `ModelError`.
- `JujuSecretResolver.resolve` with `None` secret ID — untested; confirmed latent type error.
- Wrong secret field names (`private_key` vs `private-key`) — untested; CLI validation blocks creating such secrets via `juju add-secret`, but the charm itself doesn't validate on read.
- `secret-changed` with empty/invalid new content — untested; handler calls `_holistic_handler` unconditionally.
- `pebble-check-failed`/`pebble-check-recovered` — no tests, because the handlers don't exist.
- Scale-up transient BlockedStatus — no test exercises `add-unit` with the full integration set.
- `receive-ca-cert` removal — untested (`test_remove_oauth_integration` exists for OAuth removal but there is no CA-cert equivalent).
- `PebbleService`'s shared `PEBBLE_LAYER_DICT` mutation — invisible to tests since each test creates a fresh instance.
- Auto-migration `MigrationError` path — `test_when_migration_failed` (`test_charm.py:254`) asserts only that `_holistic_handler` wasn't called and the log message appears; it never asserts unit status, hiding the "no BlockedStatus" bug.
- `oauth_integration_exists` not guarding `is_client_created()` — untested.
- `KubernetesComputeResourcesPatch` with invalid specs — untested at the unit level because `conftest.py`'s autouse fixture mocks `get_status()` to `ActiveStatus()` unconditionally (see High finding above).
- `PeerData` with missing migration-version key — untested; `__getitem__` returns `{}` when absent, and `{} != "1.0.0"` happens to compare correctly only because an empty dict never equals a string.
- `test_actions.py`'s `test_when_migration_succeeds` is missing the `mocked_database_resource_created` fixture present in other action tests — inconsistent with the file's own pattern, though not itself a bug since the action handler doesn't call `is_resource_created()`.

**Integration tests** (`tests/integration/test_charm.py`): deploy the full stack (postgresql-k8s, traefik-k8s, hydra, self-signed-certificates, login-ui) and assert: deploy/wiring, database/OAuth/public-route/CA-cert integration data, HTTP endpoints (`/healthz`, `/readyz`, `/saml/metadata`), `run-migration` action, scale up/down, removal of database/public-route/oauth integrations (BlockedStatus), and application removal. These are genuine behavioural assertions, not just `wait_for_active`. Gaps: no integration test for removing `receive-ca-cert`; none for `run-migration` against a misconfigured database; none for the transient BlockedStatus while the OAuth client is still being created.

**CI**: `ci.yaml` delegates to `canonical/identity-team/.github/workflows/charm-pull-request.yaml@v1.14.3`, running lint, unit, and integration tests.

**Linters**: `ruff check` passes with no errors. `mypy` reports 2 errors, both corresponding to findings above (`None` passed to `resolve()`, and the `PEBBLE_LAYER_DICT` type mismatch). `codespell` passes.

**Library code review**: `traefik_k8s/v0/traefik_route.py` (LIBPATCH=3) — the `_relation` workaround is the only issue found, otherwise clean. `hydra/v0/oauth.py` (LIBPATCH=11) — `is_client_created()` type-annotation bug noted above. `observability_libs/v0/kubernetes_compute_resources_patch.py` (LIBPATCH=9) — clean; `is_failed()` correctly catches `ValueError` and `get_status()` maps it to BlockedStatus. `certificate_transfer_interface/v1` (LIBPATCH=15) — clean; falls back to v0 unit-databag format gracefully and handles `DataValidationError`.

## Docs

- **README.md**: comprehensive deployment guide covering all required integrations; the `juju add-secret ... "private-key#file=<file>"` example syntax is correct; documents the Canonical identity platform prerequisite. Does not mention that `receive-ca-cert` is effectively required when Hydra uses self-signed certificates.
- **CONTRIBUTING.md**: standard, accurate — `uv sync`, `tox` commands, `charmcraft pack`.
- **AGENTS.ARCHITECTURE.md / AGENTS.DESIGN.md / AGENTS.STYLE.md / AGENTS.TESTING.md / AGENTS.md**: extensive internal docs for the canonical-iam team; `AGENTS.DESIGN.md`'s layered hierarchy diagram and data contract table are notably thorough.
- **terraform/MODULE_SPECS.md**: short spec; module itself is minimal (no `variables.tf`).
- **docs/adr/001-saml-credentials-via-juju-secret.md**: well-reasoned ADR on the secrets migration.
- **SECURITY.md**: minimal — just points to GitHub security advisories.

**Doc/reality mismatches**:
- Terraform `outputs.tf` declares `logging` as required and `metrics-endpoint`/`grafana-dashboard` as provided — none match the actual charm metadata.
- README doesn't document that `receive-ca-cert` is effectively required when Hydra uses self-signed TLS.

## Open questions

1. **OCI image / charm revision gap**: charmhub shows rev 3 (edge); local HEAD `e64cb6c` was committed 2026-07-23. The deployed OCI image is `ghcr.io/canonical/identity-saml-provider:v0.1.6`. Unclear whether local HEAD corresponds to any published charm revision (unverified).
2. **`PEBBLE_LAYER_DICT` mutation in practice**: confirmed the shared reference exists (`svc1._layer_dict is PEBBLE_LAYER_DICT` → `True`); in current single-path usage each render overwrites the full `environment` dict so no observable bug results today, but the pattern is fragile against future partial-render changes.
3. **`is_client_created` return type**: `hydra/v0/oauth.py` types it `-> bool` but returns `None` with zero relations — a library bug the charm happens to handle correctly via truthiness.
4. **Juju 4.0/concierge-k8s-4**: `postgresql-k8s` and `hydra` both went ErrorStatus on that controller, apparently due to a `leadership.py` cache issue in Juju 4.0.12 unrelated to this charm; `identity-saml-provider-operator` itself was not deployed there (unverified whether this generalizes).
5. **Unbounded pebble backoff**: is there a Juju/pebble setting to cap the exponential backoff on repeated crash loops, or is unbounded growth intended behaviour?
6. **Unit 1's initial internal-URL render**: `PublicRouteIntegration.external_base_url` returned empty for unit 1's first pebble layer render during scale-up, possibly a race between `pebble-ready` firing and traefik-route relation data being available on the non-leader unit (unverified root cause).
7. **Terraform module completeness**: no `variables.tf` — operators can't configure charm inputs via terraform. Unclear if the module is meant to be usable as-is.
8. **Auto-migration retry behaviour**: if `get_application_version()` ever returns an empty string, `migration_needed` (`{} != ""`) could evaluate True repeatedly, causing repeated migration attempts on every check — unclear if this is intended.
9. **`oauth_integration_exists` vs `is_client_created()`**: is the transient BlockedStatus during Hydra startup an accepted trade-off, or a bug to fix?
10. **Pebble restart policy vs `startup: disabled`**: pebble's `on-check-failure: {alive: restart}` restarts a crashed service but does not restart a manually-stopped one (`startup: disabled`) — confirmed as the observed distinction; is this deliberate?
11. **`deps/cosl` vendoring**: shipped but unused — intentional for future use, or accidental inclusion?
12. **Inconsistent migration-failure handling**: the `run-migration` action calls `event.fail()` on `MigrationError` (visible failure), while auto-migration in `_on_database_created` silently returns with no status change. Should both paths set BlockedStatus?
