# tenant-service

A well-architected charm — clean reconciliation pattern, thorough observability wiring, and an unusually detailed specification document — undermined by a cluster of concrete bugs that hit day-one usability. On the default configuration (`authorization_enabled=true`), the charm can hang indefinitely with an unhelpful `Waiting for the service to start` status because the OpenFGA store isn't ready yet, and gives no diagnostic clue why. One of eleven actions (`update-user-role`) is completely broken by a CLI flag mismatch. Three webhook/hook library integrations never write their relation data on first deploy due to a `ready`/`active` event-ordering bug. The OAuth token-exchange HTTP client disables TLS verification outright, and config values (`log_level`, `invitation_lifetime`) pass through to the workload with zero validation. A maintainer should first fix `src/cli.py:341` (`update-user-role`), then add a warning/log when `_ensure_openfga_model` blocks reconciliation, then fix the three webhook `ready` event handlers and the `verify=False` TLS bypass — these four are quick, high-value fixes. Everything else (lint debt, doc staleness, test gaps) can follow.

| | |
|---|---|
| Repo | canonical/tenant-service-operator @ `a7ef394` (2026-06-18) |
| Charms | tenant-service |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (models `rv-ts-a`, `rv-ts-3`, `rv-ts-e`) and concierge-k8s-4 (`rv-ts-juju4`); charmhub `latest/edge` rev 5; `rv-ts-d` failed at the `postgresql-k8s` deploy step |
| Reviewed | 2026-08-02 |

## What it does

The tenant-service charm deploys the Canonical Identity Platform Tenant Service workload — a Go application providing HTTP/gRPC APIs for tenant and user management, backed by PostgreSQL with OpenFGA-based authorization. It requires `pg-database`, `kratos-info`, and (by default) `openfga`. It optionally integrates with OAuth, Hydra token hooks, Kratos registration/login webhooks, Traefik internal ingress, TLS CA certs, and the full COS observability stack (Prometheus, Grafana, Loki, Tempo). The charm exposes 11 actions for tenant CRUD and user management.

## Deployment log

### First model: rv-ts-a on concierge-k8s-3 (Juju 3.6.25)

```bash
juju deploy tenant-service --channel edge --resource oci-image=ghcr.io/canonical/tenant-service:v0.2.0
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy openfga-k8s --channel latest/stable --trust
juju deploy kratos --channel latest/stable --trust
juju deploy hydra --channel latest/stable --trust
```

1. **08:24:38** — `blocked: Missing integration pg-database` (expected, no relations yet)
2. **08:24:40** — `pebble-ready` fired but NOOP_CONDITIONS not all met (no database) → handler returned early
3. **08:25:39** — related `pg-database`, `openfga`, `kratos-info`
4. **08:25:43** — `blocked: Kubernetes resources patch failed` — needed `juju trust tenant-service --scope cluster`
5. **08:26:09** — `waiting: Waiting for secrets creation`
6. **08:27:02** — `waiting: Waiting for the service to start` — migration completed, but the OpenFGA store wasn't yet created by the provider; `openfga-k8s` logged "token not found" errors and skipped store creation
7. **08:27:15** — stuck. `_ensure_openfga_model()` returned `False` because `is_store_ready()` returned `False`, so `_holistic_handler` never reached `_pebble_service.plan()`. No error logged.
8. **08:31:50** — `juju config tenant-service authorization_enabled=false` → bypasses the OpenFGA check
9. **08:32:06** — **active** — service started successfully

The operator had no way to tell that OpenFGA was the blocker from the status message.

### Second model: rv-ts-3 on concierge-k8s-3

Deployed with `authorization_enabled=true` (the default); the OpenFGA store was already created before tenant-service deployed, so the race did not trigger. All integrations (`postgresql-k8s`, `openfga-k8s`, `kratos`) reached active. Added `traefik-k8s` and `self-signed-certificates` for further integration testing.

**TLS integration** (`juju relate tenant-service:receive-ca-cert self-signed-certificates:send-ca-cert`): the integration works — the certificate_transfer library's v1→v0 fallback succeeds — but it logs a misleading `ERROR "invalid databag contents: expecting json"` three times per `relation-changed` hook (12 occurrences observed over the session; see finding 8 below).

**Traefik internal ingress** (`juju relate tenant-service:internal-route traefik-k8s`): established cleanly, no errors.

### Scaling

Scale to 2 units → both units reached active. The peer relation shared OpenFGA credentials, webhook API tokens, and database DSN correctly. Scale back to 1 → clean teardown, unit-1 removed.

### Config validation

| Config key | Bad value set | Result |
|---|---|---|
| `log_level` | `INVALID` | Accepted silently, passed as `LOG_LEVEL=INVALID` to workload |
| `invitation_lifetime` | `not-a-duration` | Accepted silently, passed as `INVITATION_LIFETIME=not-a-duration` |
| `cpu` | `fifty` | `blocked: Failed obtaining resource limit spec` |
| `memory` | `1TB` | `blocked: Failed obtaining resource limit spec` |

The resource-limit path catches bad `cpu`/`memory` values, but at the Kubernetes API level, not in charm config validation. `log_level` and `invitation_lifetime` pass through with zero validation.

### Actions tested (all 11)

| Action | Result |
|---|---|
| `create-tenant name=test-tenant` | Succeeded |
| `list-tenants` | Succeeded, returned 1 tenant |
| `update-tenant tenant-id=... name=renamed-tenant` | Succeeded |
| `deactivate-tenant tenant-id=...` | Succeeded |
| `activate-tenant tenant-id=...` | Succeeded |
| `delete-tenant tenant-id=...` | Succeeded |
| `provision-user tenant-id=... email=... role=admin` | Failed: depends on `KRATOS_ADMIN_URL` (empty because kratos needs hydra with a public route) |
| `invite-user tenant-id=... email=... role=viewer` | Failed: same `KRATOS_ADMIN_URL` dependency |
| `list-tenant-users tenant-id=...` | Succeeded (empty list) |
| `update-user-role tenant-id=... user-id=... role=...` | Failed: CLI bug — `--role` flag not recognised by workload binary (finding 2) |
| `get-access-token` | Failed with clear message: "OAuth integration is not ready" |

**Action parameter discovery**: `juju actions tenant-service --format json` returns only action descriptions, not parameter schemas. Parameter names (`tenant-id` vs `id`, `user-id` vs `email`) aren't discoverable without reading `charmcraft.yaml`. Failed-validation error messages do name the missing key, so an operator can eventually self-correct.

### Pebble-check timeline (authorization_enabled=true model)

Killed the workload with `pebble stop tenant-service` at 08:47:43:
- **+3s**: `juju status` still shows `active` (charm hasn't detected it yet)
- **+18s**: still `active` (pebble check threshold=3 not yet met)
- **~60s**: status changed to `waiting: Waiting for the service to start`

The gap is roughly threshold × check-interval (~30s for threshold=3) — this is detection latency, not a permanent observability gap. `collect_unit_status` (`src/charm.py:677`) runs automatically after every hook and does correctly set `WaitingStatus` once the check fails.

**Service recovery**: the service was restarted by the holistic handler triggered by a `receive-ca-cert-relation-changed` event (from the TLS relation) — not by `pebble-check-failed` itself. If no other event fires, the service stays dead until `update-status` (5-minute interval) triggers the holistic handler and restarts it.

## Observed behaviour

### Juju 4 deployment attempt (rv-ts-juju4 on concierge-k8s-4, Juju 4.0.5)

The charm itself deployed and reached `blocked: Missing integration pg-database` cleanly on Juju 4. However, `postgresql-k8s 14/stable` refuses to deploy on Juju 4 (`charm requires Juju version < 4.0.0`). `openfga-k8s` and `kratos` were not tested but almost certainly share the same constraint. The charm's `assumes: [juju >= 3.0.2]` is technically correct but the practical minimum is whatever the dependency ecosystem supports — currently Juju 3.x. The failure is at the dependency level, not the charm.

### Workload details (kubectl exec)

- **Image**: minimal scratch image — no shell, no `ls`, no `cat`. Only `pebble` and the `tenant-service` binary are available.
- **Pebble plan** (`pebble plan`):
  - `startup: disabled` — charm manages lifecycle explicitly
  - All env vars present: `DSN`, `WEBHOOKS_API_TOKEN`, `OPENFGA_API_HOST/TOKEN/STORE_ID/MODEL_ID`, `KRATOS_ADMIN_URL`, `INVITATION_LIFETIME`, `LOG_LEVEL`, etc.
  - `KRATOS_ADMIN_URL` is empty when kratos hasn't published `admin_endpoint` (blocked on hydra)
  - DSN includes `postgres://relation_id_12:...@postgresql-k8s-primary...` — username derived from relation ID
- **Pebble check**: `ready` check on `http://localhost:8080/api/v0/status`, threshold=3
- **Pebble logs**: structured JSON logs with service type, security events (`system_startup`, `system_shutdown`)
- **Resource usage** (`kubectl top pod`): 3m CPU / 61Mi memory for tenant-service; 2m/70Mi for kratos; 1m/55Mi for openfga-k8s; 3m/423Mi for postgresql-k8s

### Log noise on nearly every hook invocation

1. `WARNING Raw mode enabled: TLS routes for ALL protocols will not be auto-generated` (traefik_route library, once per hook)
2. `WARNING Invalid Grafana dashboards folder at .../src/grafana_dashboards: directory does not exist` (grafana_dashboard library)
3. `ERROR invalid databag contents: expecting json. {...}` — TLS certificate_transfer v1→v0 fallback error (3× per `receive-ca-cert-relation-changed` hook)
4. `ERROR External hostname is not set on the ingress provider` (`InternalIngressData.load`, when no ingress relation exists)

Over a 2+ hour observation window, hundreds of log entries were just these four repeated warnings/errors.

### Failure injection results (second model, authorization_enabled=true)

1. **Kill workload** (`pebble stop`): stopped; pebble check detected it ~30s later; status changed to `waiting: Waiting for the service to start`; service restarted by the holistic handler on a different event. Without another event, restart waits for the next `update-status` (up to 5 minutes).
2. **Remove required relation (pg-database)**: transitions to `blocked: Missing integration pg-database`; `_on_database_integration_broken` stops the workload; on re-relate, automatic recovery within ~15 seconds.
3. **Bad config values**: `log_level=INVALID` and `invitation_lifetime=not-a-duration` accepted silently and passed through unchanged; `cpu=fifty` / `memory=1TB` caused `blocked` (via k8s resource patching, not charm config validation).
4. **TLS relation (receive-ca-cert)**: certificate transfer works (v0 fallback succeeds) but generates false-positive ERROR logs on every hook.
5. **Kill workload + no other events**: service stays dead until `update-status` fires; status is correctly `waiting` in the meantime, but the service is not restarted.

### Pod restart (fresh model, no dependencies)

Killed the tenant-service pod with `kubectl delete pod tenant-service-0` while in `blocked: Missing integration pg-database`. The StatefulSet controller recreated the pod within 5 seconds; the unit re-installed charm software and returned to `blocked: Missing integration pg-database` within 30 seconds. No crashlooping, clean recovery.

### Application teardown

`juju remove-application tenant-service` removed the unit, pod, and all related Kubernetes resources cleanly within 30 seconds. No dangling secrets, PVCs, or Services remained.

### Postgresql-k8s deployment failure (deepening session)

A fresh full-stack deployment attempt in model `rv-ts-d` on concierge-k8s-3 with `postgresql-k8s 14/stable` failed repeatedly: the CAAS provisioner created no Kubernetes resources (no pod, no statefulset, no PVC) and the charm cycled through `installing agent` → restart loop with `"application not found"` errors. This was not a tenant-service issue — it affected `postgresql-k8s` on this cluster regardless of other deployed charms, and appears related to a charm/Juju interaction with the `csi-rawfile-default` storage class on Juju 3.6.25. Earlier models (`rv-ts-a`, `rv-ts-3`) had deployed `postgresql-k8s` successfully earlier in the session; the failure may be related to repeated deploy/teardown cycles on the same cluster. No further integration testing (OAuth, COS, end-to-end webhooks) was possible as a result.

## Findings

### 1. OpenFGA dependency makes the default deployment path fail silently
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:481-490` (`_ensure_openfga_model`), `src/charm.py:557` (`_holistic_handler`)
- **Evidence**:
  ```python
  def _ensure_openfga_model(self) -> bool:
      if not self._config._config.get("authorization_enabled", True):
          return True
      if not self.openfga_integration.is_store_ready():
          return False   # silently blocks the entire reconciliation
  ```
  In `_holistic_handler`:
  ```python
  can_plan = True
  for f in [..., self._ensure_openfga_model, ...]:
      try:
          can_plan = can_plan and f()
      except CharmError:
          logger.exception("Error in %s", f.__name__)
          can_plan = False
  ```
  When `_ensure_openfga_model` returns `False`, `can_plan` stays `False` and `_pebble_service.plan()` is never called — with no error logged. Status remains `"Waiting for the service to start"`, which does not name OpenFGA. Observed in model `rv-ts-a`: charm stuck for 4+ minutes with no actionable status or log message.
- **Impact**: on a fresh deployment with authorization enabled (the default), the charm never reaches Active if the OpenFGA provider is slow to create its store. An operator has no way to diagnose this without reading source code.
- **Fix**: log a clear WARNING/ERROR when `_ensure_openfga_model` returns `False`. Consider a dedicated `WaitingStatus` in `_on_collect_status` when the relation exists but `is_store_ready()` is `False`. Alternatively, allow the service to start without the OpenFGA model and retry later.
- **Linter rule**: "`_ensure_*` function returns `False` without logging" — mechanically checkable.

### 2. `update-user-role` action broken by CLI flag mismatch
- **Severity**: high
- **Kind**: bug
- **Where**: `src/cli.py:341`
- **Evidence**:
  ```python
  cmd = ["tenant-service", "tenant", "users", "update", tenant_id, user_id, "--role", role]
  ```
  The workload binary expects `role` positionally, not as `--role`:
  ```
  Error: unknown flag: --role
  Usage: app tenant users update [tenant-id] [user-id] [role] [flags]
  ```
  Compare `invite_user` (line 297) and `provision_user` (line 318), which correctly pass `role` positionally:
  ```python
  cmd = ["tenant-service", "tenant", "users", "invite", tenant_id, email, role]
  cmd = ["tenant-service", "tenant", "users", "provision", tenant_id, email, role]
  ```
- **Impact**: `update-user-role` is completely non-functional; any operator changing a user's role gets a confusing CLI flag error.
- **Fix**: change `"--role", role` to `role` at `src/cli.py:341`.
- **Linter rule**: not mechanically checkable — requires comparing CLI flag usage against workload binary convention.

### 3. Webhook relation data never written due to ready/active timing mismatch (3 integrations)
- **Severity**: high
- **Kind**: bug
- **Where**: `src/integrations.py:167` (`HydraHookIntegration.is_ready`), `src/integrations.py:205` (`KratosRegistrationWebhookIntegration.is_ready`), `src/integrations.py:238` (`KratosLoginWebhookIntegration.is_ready`); the corresponding provider libraries
- **Evidence**: all three `is_ready()` methods check:
  ```python
  def is_ready(self) -> bool:
      rel = self._provider._charm.model.get_relation(INTEGRATION_NAME)
      return bool(rel and rel.active)
  ```
  but all three library providers fire `ready` on `relation_created`, before any remote unit joins:
  ```python
  # lib/charms/kratos/v0/kratos_registration_webhook.py:169-170
  def _on_relation_created(self, event: RelationCreatedEvent) -> None:
      self.on.ready.emit(event.relation)
  ```
  Same pattern in `lib/charms/hydra/v0/hydra_token_hook.py:177-178` and `lib/charms/kratos/v0/kratos_login_webhook.py`. The provider never observes `relation_joined`/`relation_changed`, so once `rel.active` becomes `True` no event re-fires to re-trigger `update_relation_data`.
- **Impact**: all three webhook/hook integrations are silently broken on first deployment. Data eventually gets written once `update-status` fires (every 5 minutes), but the features are inactive until then. Observed: the `kratos-registration-webhook` relation data remained `{}` after creation — kratos never received the webhook URL.
- **Fix**: fire `ready` on `relation_changed` (when `rel.active` becomes `True`) instead of `relation_created`, or have the charm's `is_ready()` check for a remote unit's presence rather than gating on `rel.active`.
- **Linter rule**: not mechanically checkable — requires understanding relation lifecycle semantics.

### 4. HTTP client disables TLS certificate verification
- **Severity**: high
- **Kind**: bug
- **Where**: `src/clients.py:18`
- **Evidence**:
  ```python
  def __init__(self, token_url: str) -> None:
      self._token_url = token_url.rstrip("/")
      self._session = requests.Session()
      self._session.verify = False   # TLS verification disabled
  ```
- **Impact**: OAuth2 token exchange with the OAuth provider is performed with TLS verification disabled — a man-in-the-middle could intercept client credentials and access tokens. The charm already maintains a CA bundle at `/usr/local/share/ca-certificates/` via `_ensure_tls`, but the HTTP client doesn't use it.
- **Fix**: set `self._session.verify = "/usr/local/share/ca-certificates/ca-certificates.crt"` (the path `_ensure_tls` writes to), or fall back to the system CA bundle when no custom CA cert is present.
- **Linter rule**: `requests.Session().verify = False` in charm code — mechanically checkable (`grep -R '\.verify\s*=\s*False'`).

### 5. Pebble-check-failed does not attempt recovery
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:617-620` (`_on_pebble_check_failed`), `src/charm.py:626` (`_on_pebble_check_recovered`)
- **Evidence**:
  ```python
  def _on_pebble_check_failed(self, event: ops.PebbleCheckFailedEvent) -> None:
      if event.info.name == PEBBLE_READY_CHECK_NAME:
          logger.warning("The service is not running")
  ```
  `collect_unit_status` (`src/charm.py:677`) does run after every hook and correctly sets `WaitingStatus` once the check fails, so detection latency is threshold × check-interval (~30s), not five minutes. But neither handler triggers reconciliation. With `startup: disabled`, Pebble does not auto-restart, so the service stays dead until some other event (relation-changed, config-changed, or `update-status`) triggers the holistic handler.
- **Impact**: a crashed service can stay dead for up to 5 minutes if no other event fires — a significant recovery gap for an identity service. `_on_pebble_check_recovered` similarly only logs and does not reconcile.
- **Fix**: call `self._on_holistic_handler(event)` from `_on_pebble_check_failed` to attempt an immediate restart, or configure Pebble with `on-failure: restart` instead of `startup: disabled`.
- **Linter rule**: "`pebble_check_failed` handler does not call `_holistic_handler` or set unit status" — mechanically checkable.

### 6. `get_missing_config_keys` is a stub returning an empty list
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/configs.py:34-36`
- **Evidence**:
  ```python
  def get_missing_config_keys(self) -> list:
      """Get missing config keys."""
      return []
  ```
- **Impact**: `_on_collect_status` calls this and reports `BlockedStatus` if any keys are found; since it always returns `[]`, the charm never blocks on missing config through this path (a separate `authentication_config_status` path covers auth config).
- **Fix**: implement validation (e.g. `invitation_lifetime` format, `log_level` enum) or remove the dead check from `_on_collect_status`.
- **Linter rule**: "method that always returns an empty/constant value" — heuristic, not mechanically reliable.

### 7. No config validation — any string accepted for enumerated options
- **Severity**: medium
- **Kind**: ux
- **Where**: `charmcraft.yaml` config section, `src/configs.py:41`
- **Evidence**: `juju config tenant-service log_level=invalid` is accepted without error; the value is uppercased at `src/configs.py:41` and passed to the workload as `LOG_LEVEL=INVALID`. The `log_level` description lists valid values but nothing enforces them. Same for `invitation_lifetime` (no duration-format validation). `cpu`/`memory` do reach `blocked` on bad values, but only via k8s resource patching.
- **Impact**: operators can set invalid values with zero feedback; the workload may ignore or reject them silently.
- **Fix**: add `enum`/`pattern` constraints in `charmcraft.yaml`; validate Go duration format for `invitation_lifetime`; use `enum: [info, debug, warning, error, critical]` for `log_level`.
- **Linter rule**: "config option has enumerated values in its description but no `enum` constraint in charmcraft.yaml" — mechanically checkable.

### 8. TLS certificate_transfer library logs a false-positive ERROR on every hook
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/certificate_transfer_interface/v1/certificate_transfer.py:190-193,215-218,489-498,679-690`
- **Evidence**: on every `receive-ca-cert-relation-changed` hook:
  ```
  ERROR invalid databag contents: expecting json. {'ca': '-----BEGIN CERTIFICATE-----...
  ERROR Error parsing relation databag: ...
  ```
  `DatabagModel.load()` tries `json.loads()` on every value in the provider databag; when the provider uses v0 format (raw PEM) this fails with `json.JSONDecodeError`, logged at ERROR before falling back to v0 unit-data parsing. The fallback succeeds and the certificate transfer actually works. Fired 12 times over the observation session.
- **Impact**: log noise that could mask real errors; an operator investigating a TLS issue would see ERROR-level messages and suspect failure when there is none.
- **Fix**: downgrade the v1→v0 fallback log from `logger.error()` to `logger.debug()` in the library, or suppress it in the charm.
- **Linter rule**: not mechanically checkable — requires understanding the library's fallback contract.

### 9. Action parameter schemas not discoverable via `juju actions`
- **Severity**: medium
- **Kind**: ux
- **Where**: `charmcraft.yaml` actions section
- **Evidence**: `juju actions tenant-service --format json` returns only `{"action-name": "description string", ...}` — no parameter schema. Actual parameters (`tenant-id`, `email`, `role`, etc.) live only in `charmcraft.yaml`.
- **Impact**: an operator scripting `juju run tenant-service/0 update-tenant id=...` gets a confusing validation error about a missing `tenant-id` when they used `id`. Same issue for `update-user-role` (expects `user-id`, not `email`).
- **Fix**: document action parameters in the README/charmhub description, or add an action that surfaces the schema.
- **Linter rule**: not mechanically checkable.

### 10. `_pebble_layer` can raise `ValueError` (not `CharmError`), crashing the handler
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:332` (`_pebble_layer`), `src/charm.py:577` (`except CharmError`), `src/secret.py:62-67` (`api_token`)
- **Evidence**:
  ```python
  @property
  def api_token(self) -> str:
      content = self[API_TOKEN_SECRET_LABEL]
      if content is None:
          raise ValueError("API token secret is not available")
      return content[API_TOKEN_SECRET_KEY]
  ```
  `_pebble_layer` calls `self._secrets.to_env_vars()`, which calls `api_token`. `_holistic_handler`'s `except CharmError` at `src/charm.py:577` does not catch `ValueError`. If a non-leader unit races with secret creation, this would crash the hook with a traceback rather than a graceful `WaitingStatus`.
- **Impact**: unhandled exception in error state instead of graceful waiting.
- **Fix**: catch `ValueError` in `_pebble_layer` and convert it to `CharmError`, or broaden the except clause in `_holistic_handler`.
- **Linter rule**: "property/cached_property raises an exception type not covered by the caller's except clause" — mechanically checkable with dataflow analysis.

### 11. Type errors in config and OAuth code
- **Severity**: medium
- **Kind**: lint
- **Where**: `src/configs.py:41`, `src/integrations.py:487-488`, `src/services.py:195`
- **Evidence**: 8 pyright errors, including:
  - `configs.py:41`: `self._config["log_level"].upper()` — `ConfigData.__getitem__` returns `str | bool | int | float | None`, and `.upper()` is invalid on non-string values
  - `integrations.py:487-488`: `client_id`/`client_secret` from `get_provider_info()` can be `None`, but `ClientConfig` expects `str`
  - `services.py:195`: `self._layer_dict["services"][WORKLOAD_SERVICE]` accesses a non-required TypedDict key and assigns a `dict[str, str | bool]` where a plain `str` dict is expected
- **Impact**: `log_level.upper()` would crash at runtime if the config value were not a string — not merely a type-theoretic issue.
- **Fix**: add a `str()` cast in `configs.py`, add `None` guards in `integrations.py`, use proper typing for `LayerDict` access.
- **Linter rule**: covered by pyright (`reportGeneralTypeIssues`, `reportOptionalMemberAccess`, `reportTypedDictNotRequiredAccess`).

### 12. Three failing unit tests (scenario-ops incompatibility)
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:35,80,125`
- **Evidence**: `TestPebbleReadyEvent::test_when_event_emitted`, `TestAuthn::test_when_oauth_relation_exists`, `TestAuthn::test_when_manual_config_exists` all fail with `InconsistentScenarioError: cannot emit tenant_service_pebble_ready because container tenant-service is not in the state`.
- **Impact**: these tests cover pebble-ready and OAuth/manual-auth scenarios; without a passing CI gate a contributor could break pebble-ready handling undetected.
- **Fix**: pass `container=container` to the `pebble_ready()` event constructor (scenario-ops API change).
- **Linter rule**: not mechanically checkable — CI pass/fail should catch this.

### 13. Unit test coverage gaps for runtime failure paths
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/`
- **Evidence**: no `test_clients.py` — `HTTPClient.get_access_token` is completely untested; no tests for `_on_pebble_check_failed`/`_on_pebble_check_recovered`; `_ensure_tls` success/cert-comparison path untested (only the subprocess-failure path is); no test for `_on_resource_patch_failed`; `_get_management_token` HTTP-failure path untested; `Secrets.api_token`'s `ValueError` path is tested in isolation but not its integration with `_pebble_layer`.
- **Impact**: good happy-path coverage, but the failure/recovery paths operators actually encounter are untested. The HTTP client file has 0% coverage.
- **Fix**: add tests for the paths listed above.
- **Linter rule**: not mechanically checkable.

### 14. Extensive ruff violations — 246 errors, not the 12 the CI lint step catches
- **Severity**: medium
- **Kind**: lint
- **Where**: `src/` (all files)
- **Evidence**: `ruff check --select ALL src/` reports 246 errors (42 auto-fixable); `pyproject.toml`'s ruff config selects only `["E","W","F","C","N","D","CPY"]`, and `tox -e lint` runs default rules only. Notable categories:
  - `docstring-missing-returns` — 24 occurrences (e.g. `__getitem__`, `__setitem__`, `load`, `to_env_vars`, `is_ready`)
  - `private-member-access: _charm` — 6 occurrences in `src/integrations.py` (lines 70, 78, 87, 164, 207, 240)
  - `implicit-return-value` — 4 occurrences in `src/integrations.py` (lines 71, 73, 79, 81) — bare `return` in functions typed `str | None`
  - `hardcoded-temp-file` — 2 occurrences in `src/constants.py` (lines 15, 17) writing TLS certs to `/tmp`
  - `unspecified-encoding`/`builtin-open`/`read-whole-file` — `src/integrations.py:92`, Jinja2 template opened without explicit encoding
  - `blind-except: Exception` — `src/services.py:76,174`
  - `error-instead-of-exception` — `src/services.py:70,77`
  - `raise-without-from-inside-except` / `f-string-in-exception` / `raise-vanilla-args` — several occurrences
  - `any-type` — 4 occurrences in `src/utils.py`/`src/integrations.py`
  - `future-required-type-annotation` — 8 occurrences
  - `undocumented-public-init` — 8 occurrences
  - `if-expr-with-true-false` — `src/integrations.py:470`
  - `property-docstring-starts-with-verb` — 12 occurrences (the only category the current lint step catches)
- **Impact**: the current lint gate catches only a small slice of this; `blind-except`/`error-instead-of-exception` in particular suppress useful diagnostics during debugging.
- **Fix**: enable `--select ALL` (or a curated superset) in `tox.ini`'s lint command, apply the 42 auto-fixes, triage the rest.
- **Linter rule**: the whole list is mechanically checkable — `ruff check --select ALL`.

### 15. Integration test HTTP client also disables TLS verification
- **Severity**: medium
- **Kind**: bug
- **Where**: `tests/integration/conftest.py:131`
- **Evidence**:
  ```python
  @pytest.fixture
  def http_client() -> Generator[requests.Session, None, None]:
      with requests.Session() as client:
          client.verify = False
          yield client
  ```
  Used by `tests/integration/test_charm.py:78` (`test_app_health`) against plain HTTP, so it has no runtime effect today, but it normalizes the same dangerous pattern as finding 4.
- **Impact**: if TLS is ever enabled in integration tests, this flag would silently disable certificate validation and mask TLS misconfiguration.
- **Fix**: remove `client.verify = False`, or make it conditional on scheme.
- **Linter rule**: same as finding 4 — `requests.Session().verify = False` is mechanically grepable.

### 16. `_ensure_openfga_model` not in `NOOP_CONDITIONS` — different diagnostic quality than the database path
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:481-490`, `src/utils.py:109-114`
- **Evidence**: `NOOP_CONDITIONS` includes `database_integration_exists`, `database_resource_is_created`, and `authentication_config_is_valid`, but not `openfga_store_readiness`/`openfga_integration_exists`. A missing database fast-fails before `_holistic_handler` runs, producing an immediate clear `BlockedStatus`; a missing/not-ready OpenFGA store instead lets the holistic handler proceed and silently returns `can_plan=False`, leaving status at the generic `"Waiting for the service to start"`.
- **Impact**: operators get materially different diagnostic quality for the two required integrations. Observed in `rv-ts-a`: 4+ minutes of unspecific "waiting" with no indication OpenFGA was the cause.
- **Fix**: add `openfga_store_readiness` to `NOOP_CONDITIONS` for a fast-fail with a specific `WaitingStatus`, or at minimum log a clear warning when `_ensure_openfga_model` returns `False` (see finding 1).
- **Linter rule**: not mechanically checkable — requires understanding the relationship between condition gates and failure modes.

### 17. Grafana dashboards directory missing — repeated warnings
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:149` (`GrafanaDashboardProvider` initialisation)
- **Evidence**: every hook logs `Invalid Grafana dashboards folder at .../src/grafana_dashboards: directory does not exist`. The directory genuinely does not exist in the repo.
- **Impact**: log noise on every hook.
- **Fix**: add dashboard JSON files, or remove the Grafana integration if none are planned.
- **Linter rule**: "`GrafanaDashboardProvider` initialised but no `src/grafana_dashboards/` directory exists" — mechanically checkable at pack time.

### 18. Juju 4 deployment is blocked by the dependency ecosystem, not by the charm
- **Severity**: low
- **Kind**: docs
- **Where**: `charmcraft.yaml:18-19`, observed in `rv-ts-juju4`
- **Evidence**: the charm's `assumes: [juju >= 3.0.2]` suggests Juju 4 compatibility, and the charm did reach the expected `blocked: Missing integration pg-database` on Juju 4.0.5. But `postgresql-k8s 14/stable` refuses to deploy on Juju 4 (`charm requires Juju version < 4.0.0`), and `openfga-k8s`, `kratos`, `hydra` almost certainly share the constraint. No full-stack deploy was possible on Juju 4.
- **Impact**: an operator following the `assumes` clause could attempt Juju 4 and find they can't install any required dependency charm.
- **Fix**: document the Juju 3.x-only practical limitation in the README/charmhub description, or gate on dependency versions once they support Juju 4.
- **Linter rule**: not mechanically checkable.

### 19. `logger.error` without stacktrace suppresses debugging info
- **Severity**: low
- **Kind**: lint
- **Where**: `src/services.py:70,77`
- **Evidence**:
  ```python
  except (ModelError, ConnectionError) as e:
      logger.error("Failed to get pebble service: %s", e)
  ```
  and
  ```python
  except Exception as e:
      logger.error("Failed to set workload version: %s", e)
  ```
- **Impact**: `logger.exception()` would include the traceback; without it, diagnosing why the service failed to start is harder than it needs to be.
- **Fix**: change `logger.error` to `logger.exception` in both handlers.
- **Linter rule**: mechanically checkable — `error-instead-of-exception`, enabled with `ruff check --select ALL`.

### 20. Documentation references non-existent ADRs and a mismatched CI badge
- **Severity**: low
- **Kind**: docs
- **Where**: `README.md:7`, `README.md:38-41`, `docs/spec/CHARM_SPECIFICATION.md:313,375,393,408`
- **Evidence**: the README links `ADR-0007` (`docs/adr/0007-remove-hydra-token-hook.md`) at line 40, and the spec references `ADR-0005` (gRPC exposure) and `ADR-0007` (hydra-token-hook removal) at lines 313, 375, 393, 408. Only ADRs 0001–0004 exist in the repo. The README CI badge (line 7) links to `on_push.yaml`, but the actual workflow is `ci.yaml`.
- **Impact**: broken links for anyone following an ADR reference or the CI badge; suggests docs were written ahead of implementation and never updated.
- **Fix**: write the missing ADRs or remove the references; point the CI badge at `ci.yaml`.
- **Linter rule**: "markdown link whose target file does not exist" — mechanically checkable with a link checker.

### 21. `_on_internal_route_changed` mutates a private library attribute
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:631`
- **Evidence**:
  ```python
  def _on_internal_route_changed(self, event: ops.RelationEvent) -> None:
      # Needed due to how traefik_route lib handles the event
      self.internal_ingress._relation = event.relation
      self._on_holistic_handler(event)
  ```
  The comment acknowledges this is a workaround for a limitation in the `traefik_route` library's `TraefikRouteRequirer`.
- **Impact**: if the library ever changes the name, type, or semantics of `_relation`, this breaks silently; other charms using the same library must replicate the workaround.
- **Fix**: upstream a fix to `traefik_route` for `relation_changed` handling, or add a public API for updating the relation reference.
- **Linter rule**: mechanically checkable — `private-member-access` (SLF001), already flagged by ruff.

### 22. Only one published revision — no upgrade path exercised on Charmhub
- **Severity**: low
- **Kind**: test-gap
- **Where**: Charmhub `latest/edge` — revision 5 only (2026-05-29)
- **Evidence**: `juju info tenant-service` shows only `latest/edge: 5`, with no stable/candidate/beta revisions and nothing to `juju refresh` to.
- **Impact**: the version-keyed `PeerData` upgrade mechanism (`src/integrations.py:399-435`) has never been exercised across an actual charm upgrade in the field.
- **Fix**: publish a second edge revision (or a beta channel) to enable upgrade testing, or add an integration test that packs and refreshes between two local builds.
- **Linter rule**: not mechanically checkable.

### 23. `_on_database_integration_broken` uses `WORKLOAD_CONTAINER` where `WORKLOAD_SERVICE` is semantically correct
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:637`
- **Evidence**:
  ```python
  self._container.stop(WORKLOAD_CONTAINER)
  ```
  Both constants resolve to `"tenant-service"`, so this is functionally correct, but `Container.stop()` stops a Pebble *service*, not a container.
- **Impact**: code clarity only, today; could cause a real bug if the constant values ever diverge.
- **Fix**: use `WORKLOAD_SERVICE` instead.
- **Linter rule**: not mechanically checkable without understanding the semantic difference.

## Worth copying

1. **`_holistic_handler` + `NOOP_CONDITIONS` pattern** (`src/charm.py:557`, `src/utils.py:96`) — centralised reconciliation with composable, independently testable `_ensure_*` functions; `can_plan = can_plan and f()` short-circuits cleanly.
2. **`EnvVarConvertible` protocol** (`src/env_vars.py:38-42`) — all data sources implement `to_env_vars() -> dict[str, str | bool]`, making pebble-layer composition trivial and extensible.
3. **Charm specification document** (`docs/spec/CHARM_SPECIFICATION.md`) — 408 lines of thorough architecture, data-flow, relation, config, and action documentation; exceptional by ecosystem standards, even with stale sections.
4. **`PeerData` with version-keyed databag** (`src/integrations.py:399-435`) — migration and model state keyed by workload version, enabling clean version-specific upgrade handling; leader writes, all units read.
5. **Integration test with jubilant** (`tests/integration/test_charm.py`) — tenant lifecycle, user management, scale up/down, integration removal/recovery, app removal, with structured helpers such as the `remove_integration` context manager.
6. **`ResourceRequirements` from charm config** (`src/charm.py:753-758`) — maps `cpu`/`memory` config to Kubernetes resource requests/limits with proper adjustment.
7. **`remove_integration` with tenacity retry** (`tests/integration/utils.py:65-84`) — context manager that removes and restores an integration, retrying with exponential backoff (1s→30s, 10 attempts) to handle the case where the prior integration instance is still "dying" when re-integrated. A practical pattern for relation-lifecycle integration tests.

## Common-practice notes

- **charm-user: non-root** (`charmcraft.yaml`) — explicit uid/gid 584792, follows security best practice.
- **charm-binary-python-packages** — correctly declares `pydantic>=2` and `jsonschema` for binary wheels.
- **`startup: disabled`** (`src/services.py:33`) — the charm manages lifecycle explicitly rather than letting Pebble auto-start. Non-standard for k8s charms (most use `startup: enabled`), defensible for env-var-driven restarts, but means no auto-restart on crash — relies on the holistic handler, which may wait up to 5 minutes (see finding 5).
- **Deprecated `JujuVersion.from_environ()`** — vendored `data_interfaces` and `loki_push_api` libraries use this, generating 76 deprecation warnings in unit tests. Library-level issue.
- **Hydra-token-hook present in code but marked removed in spec** — `CHARM_SPECIFICATION.md` §13 Phase 3 marks it as removed and references the non-existent ADR-0007, but the code (`charmcraft.yaml`, `src/charm.py`, `src/integrations.py`) still contains the full integration. Doc/code mismatch.
- **Integration tests defang OpenFGA** — `tests/integration/test_charm.py` deploys with `authorization_enabled=false`, so the OpenFGA integration path is never exercised in CI.
- **Action count**: `charmcraft.yaml` declares 11 actions; confirmed exactly 11 during testing.

## Tests

- **Unit tests**: 146 total, 143 passed, 3 failed — all 3 failures are pebble-ready scenarios broken by a scenario-ops container-passing API change (finding 12).
- **Coverage**: good for actions (success/failure/not-ready), CLI (all commands), integrations (dataclasses and load methods), config, status, and holistic-handler paths. Untested: `HTTPClient` (0% — no `test_clients.py`), `_on_pebble_check_failed`/`_recovered`, the `_ensure_tls` success path, `_on_resource_patch_failed`, the `_get_management_token` failure path (finding 13).
- **Integration tests**: 1 file, 8 test functions using `jubilant`. Covers tenant/user lifecycle, scale, integration removal, app removal. Deploys with `authorization_enabled=false`, so it never tests OpenFGA, OAuth, hydra-token-hook, webhooks, or COS.
- **No spread tests, no concierge files.**
- **Lint**: `ruff check --select ALL`: 246 errors, 42 auto-fixable (finding 14). `tox -e lint` (default ruff rules) catches only 12 of these. `pyright`: 8 type errors (finding 11). `codespell`: 0 errors.
- **Integration test hygiene**: `tests/integration/conftest.py:131` disables TLS (`client.verify = False`) — same anti-pattern as `src/clients.py:18` (finding 15).

## Docs

- **README**: references non-existent ADR-0007 (and the spec also references non-existent ADR-0005); CI badge links to `on_push.yaml` but the repo's workflow is `ci.yaml`. Would benefit from a "Getting Started" deployment example.
- **CHARM_SPECIFICATION.md**: excellent detail but stale — hydra-token-hook removal claim contradicts the code, references non-existent ADRs, marked "Draft".
- **Charmhub description**: "Operator for Identity platform Tenant Service" — bare minimum; should list key integrations.
- **CONTRIBUTING.md**: standard Canonical template.

## Open questions

1. Should the deployment guide document that `openfga-k8s` should be deployed and reach active *before* tenant-service, to avoid the OpenFGA store-creation race (finding 1)?
2. `postgresql-k8s 14/stable` doesn't work on Juju 4 — is the ecosystem simply not ready, making `assumes: [juju >= 3.0.2]` misleading as a practical minimum (finding 18)?
3. Is `get_missing_config_keys` (finding 6) unimplemented-but-planned validation, or should the stub and its call site be removed?
4. Is `self._session.verify = False` in `src/clients.py:18` (finding 4) intentional (e.g. for development) or an oversight, given the charm already manages CA certificates via `_ensure_tls`?
5. Why `startup: disabled` instead of `startup: enabled` with `on-failure: restart`, which would give immediate crash recovery without waiting on the holistic handler?
6. Is the 246-error `ruff check --select ALL` output (finding 14) intentional technical debt, or should the lint command in `tox.ini` be updated to a stricter rule set?
7. Is `client.verify = False` in the integration test fixture (finding 15) intentional (plain-HTTP test) or copy-pasted from `src/clients.py`?
8. Were ADR-0005 and ADR-0007 (finding 20) planned and never written, or should the references simply be removed?
9. Is there a plan to publish beyond `latest/edge` rev 5 (finding 22), so the version-keyed `PeerData` upgrade path can be validated in the field?
10. Was the `postgresql-k8s` deployment failure in `rv-ts-d` a known issue with this charm version on Juju 3.6.25 with `csi-rawfile-default`, or specific to that test cluster's state after repeated deploy/teardown cycles?
