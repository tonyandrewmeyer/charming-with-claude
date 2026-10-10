# user-verification-service-operator

A Kubernetes charm for the Canonical Identity Platform's User Verification Service: it checks new users against the Salesforce API via a Kratos registration webhook, fronts them with Traefik ingress, and wires up the standard observability stack (Prometheus, Loki, Tempo, Grafana). The code is clean and follows a holistic reconciliation pattern, but three confirmed production bugs push it to broken or misleading states: the Pebble layer ships with `startup: disabled`, a Salesforce secret with the wrong keys crashes the charm to `error`, and the required `ingress` integration is not enforced in status. A maintainer should fix the `startup: disabled` layer and the ingress status check first — both are one-line changes with clear runtime confirmation — then harden the Salesforce secret handling to avoid `error` states.

| | |
|---|---|
| Repo | canonical/user-verification-service-operator @ `eb793cd` (2026-07-24) |
| Charms | user-verification-service |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (4.0.5) and concierge-k8s-3 (3.6.25), latest/edge rev 11 (only revision published) |
| Reviewed | 2026-08-11 |

## What it does

The charm wraps the `ghcr.io/canonical/user-verification-service` workload (v0.4.1), a Go service acting as a Kratos registration webhook. When a user registers, Kratos calls this service, which checks the user against Salesforce (or a noop client when Salesforce is disabled). It provides:

- **Kratos registration webhook** (`kratos-registration-webhook`): configures Kratos with the webhook URL, auth token, and hook body
- **Login UI endpoints** (`ui-endpoint-info`): consumes login/error URLs from the login-ui charm; provides a registration-error URL back
- **Ingress** (`traefik_route`): exposes the service via Traefik with prefix-based routing
- **Observability**: Prometheus metrics, Loki log forwarding, Tempo tracing, Grafana dashboard
- **Resource patching**: K8s compute resource limits configurable via `cpu`/`memory` juju config

## Deployment log

### Juju 4.x (concierge-k8s-4, 4.0.5) — `rv-uvs-4`

```
juju add-model rv-uvs-4
juju deploy user-verification-service --channel edge --trust       # rev 11, ubuntu@22.04
juju deploy traefik-k8s traefik --channel latest/stable --trust
juju deploy identity-platform-login-ui-operator login-ui --channel latest/stable --trust
juju integrate user-verification-service traefik
juju integrate user-verification-service login-ui
juju integrate traefik login-ui
```

Initial status: `blocked` — "Missing required configuration: ['salesforce_domain', 'salesforce_consumer_secret']". Correct.

```
juju config user-verification-service salesforce_enabled=false support_email=test@example.com
```
→ `active` after ~30s. Workload version 0.4.1 correctly reported.

### Juju 3.6 (concierge-k8s-3, 3.6.25) — `rv-uvs-36`

Same deployment steps; same results (active, correct version). Scale up to 2 units and back to 1 worked correctly.

### Failure injection — both versions tested

- `log_level=debug` → one `config-changed` hook, service restarted. `log_level=banana` → accepted without error, passed to workload as `BANANA`.
- `cpu=eleventybillion memory=not-a-real-unit` → K8s resource patch library caught it ("Failed obtaining resource limit spec: Invalid limits spec", workload briefly blocked), but charm returned to `active` with no limits applied.
- `salesforce_enabled=true` without domain/secret → correctly blocked.
- `salesforce_enabled=false` → recovered to active.
- Salesforce secret with wrong keys (`wrong-key`/`also-wrong` instead of `consumer-key`/`consumer-secret`) → charm crashed to **error** state with "hook failed: config-changed" on both Juju versions. Required `juju resolved` to recover. **Confirmed production bug.**
- Removed `ui-endpoint-info` relation → blocked "Missing integration ui-endpoint-info". Re-add → active.
- Removed `ingress` relation → charm stayed **active** (bug: required ingress not enforced). Re-add → active.
- Killed workload via `pebble stop` (via `juju exec --container`) → charm blocked "Failed to start the service". Config change after kill → recovered.
- `kubectl delete pod` → pod recreated, service recovered via pebble-ready → config-changed flow.
- Scale up/down (3.6): scale to 2 units → both active; scale back to 1 → active.

## Observed behaviour

- **Pebble plan shows `startup: disabled`**: confirmed via `pebble plan` on both Juju versions. If Pebble restarts independently of the pod (e.g. Pebble daemon crash), the service will not auto-start.
- **Service restart count**: each config change (even `log_level`) triggers a `replan()` that restarts the service if the layer changed. 5+ restarts observed during testing.
- **Container image is minimal**: the workload container (`ghcr.io/canonical/user-verification-service:v0.4.1`) has no shell — `/bin/sh`, `/bin/bash`, `ls`, `id`, `whoami` are all absent. Only the Go binary and Pebble are present. This prevents `juju ssh --container` from working.
- **Resource usage**: 1m CPU, 40Mi memory — very lightweight.
- **Hook count for trivial config change**: 1 hook (`config-changed`). Good.
- **`ERROR_UI_URL` initially malformed**: `https:///ui/oidc_error` (triple slash) appeared before login-ui settled, then corrected.
- **No `juju refresh` test possible**: only revision 11 is published (latest/edge); all other channels are empty.
- **No actions**: `juju actions` returns empty. Operators must use `juju exec` for any operational work.
- **Status recovery gap after pebble check recovery**: `_on_pebble_check_recovered` only logs — the charm remains blocked until the next periodic `update-status` (up to 5 minutes).
- **`log_level=banana` accepted**: value `BANANA` passed to workload, no Juju-level validation.
- **`cpu`/`memory` with junk values**: the K8s resource patch library detects the invalid spec (workload briefly shows blocked), but the charm returns to active with no limits applied — the failure is silently masked.
- **Juju 3.6 ↔ 4.x differences**: none observed; behaviour is identical across Juju versions.

These observations (except resource usage and hook count) could not be discerned from code review alone.

## Findings

### Pebble service has `startup: disabled`
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/services.py:33`
- **Evidence**: `"startup": "disabled"` in `PEBBLE_LAYER_DICT`. Confirmed at runtime: `pebble services` shows `Startup: disabled`.
- **Impact**: If Pebble itself restarts (not the pod), the workload service will not come back. The pod appears healthy to Kubernetes (container running, Pebble running) but the application is down. Recovery only happens on the next charm hook.
- **Fix**: Change to `"startup": "enabled"`.
- **Linter rule**: check that all Pebble services declared in `LayerDict` have `"startup": "enabled"` unless explicitly justified. Mechanically checkable.

### Missing status check for required `ingress` integration
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:237-251` (`_on_collect_status`), `charmcraft.yaml` (ingress marked `optional: False`)
- **Evidence**: Removing the ingress relation left the charm in `active` state. The `ingress_integration_exists` condition is defined in `src/utils.py:49` but never used in `NOOP_CONDITIONS` or `_on_collect_status`.
- **Impact**: Operators get no indication that a required integration is missing. The workload starts but is unreachable.
- **Fix**: Add an `ingress_integration_exists` check to `_on_collect_status`, mirroring the existing `login_ui_integration_exists` check:
  ```python
  if not ingress_integration_exists(self):
      event.add_status(ops.BlockedStatus(f"Missing integration {INGRESS_INTEGRATION_NAME}"))
  ```
- **Linter rule**: for each `requires` entry in `charmcraft.yaml` with `optional: False` or no `optional` key, the corresponding integration-existence condition must appear in `_on_collect_status`. Mechanically checkable.

### `CharmConfig._get_salesforce_consumer_info` raises `KeyError` on wrong secret keys — confirmed in deployment
- **Severity**: high
- **Kind**: bug
- **Where**: `src/configs.py:23-25`
- **Evidence**:
  ```python
  def _get_salesforce_consumer_info(self) -> Tuple[str, str]:
      secret_id = self._config["salesforce_consumer_secret"]
      secret = self._model.get_secret(id=secret_id)
      content = secret.get_content(refresh=True)
      return content[CONFIG_CONSUMER_KEY_SECRET_KEY], content[CONFIG_CONSUMER_SECRET_SECRET_KEY]
  ```
  Confirmed in production on both Juju 3.6 and 4.x: created a secret with `wrong-key`/`also-wrong` instead of `consumer-key`/`consumer-secret`, set `salesforce_enabled=true`, and the charm went to `error` state with "hook failed: config-changed". The uncaught `KeyError` propagates out of the handler.
- **Impact**: An operator who misnames a key in their Salesforce secret gets a cryptic error state with no guidance on what went wrong. Recovery requires `juju resolved` after fixing the secret.
- **Fix**: Catch `KeyError` and raise a `BlockedStatus` with a clear message, e.g. `f"Secret {secret_id} must contain keys 'consumer-key' and 'consumer-secret'"`.
- **Linter rule**: secret content key access should be guarded with `.get()` or `try`/`except KeyError`. Mechanically checkable.

### Pebble check events only log, don't update status
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:240-246`
- **Evidence**:
  ```python
  def _on_pebble_check_failed(self, event: ops.PebbleCheckFailedEvent) -> None:
      if event.info.name == PEBBLE_READY_CHECK_NAME:
          logger.warning("The service is not running")

  def _on_pebble_check_recovered(self, event: ops.PebbleCheckRecoveredEvent) -> None:
      if event.info.name == PEBBLE_READY_CHECK_NAME:
          logger.info("The service is online again")
  ```
  Neither handler calls `_holistic_handler` or updates `self.unit.status`.
- **Impact**: If the Pebble health check fails, the charm only logs a warning and stays `active` until `update-status` fires (up to 5 minutes). If the charm was showing `BlockedStatus` because `is_running()` returned `False`, the recovery handler doesn't trigger a status refresh either — the charm remains blocked for up to 5 minutes after the service actually recovers.
- **Fix**: Call `self._holistic_handler(event)` in both handlers so `_on_collect_status` is re-evaluated and the status updates immediately.
- **Linter rule**: Pebble check event handlers that don't update unit status or trigger reconciliation. Partially mechanically checkable (detect empty handler bodies).

### `Secrets.values()` returns empty on any label error
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/secret.py:43-57`
- **Evidence**:
  ```python
  for key, label in zip(self.KEYS, self.LABELS):
      try:
          secret = self._model.get_secret(label=label)
      except SecretNotFoundError:
          return ValuesView({})
  ```
  If the first secret lookup fails, the method returns empty immediately instead of continuing for other labels.
- **Impact**: Today `KEYS` and `LABELS` each have one element, so this isn't triggered. But the code structure implies multiple labels are supported, and adding a second label would introduce a silent correctness bug.
- **Fix**: Collect all available secrets and return whatever was found; have `is_ready` check all expected labels independently.
- **Linter rule**: secret getter methods that iterate over labels must not short-circuit on the first missing secret unless partial results are intentional. Partially checkable.

### Mutable module-level `PEBBLE_LAYER_DICT`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/services.py:25-42, 93, 123`
- **Evidence**: `PEBBLE_LAYER_DICT` is a module-level dict. `PebbleService.__init__` assigns `self._layer_dict: LayerDict = PEBBLE_LAYER_DICT` (reference, not copy). `render_pebble_layer` mutates `self._layer_dict["services"][WORKLOAD_SERVICE]["environment"]`. Multiple `PebbleService` instances share the same nested dict.
- **Impact**: harmless with a single unit in production, but in unit tests where multiple `PebbleService` instances might exist, environment variables would leak between tests, and `render_pebble_layer` mutates the object on every call, making output non-deterministic across repeated calls.
- **Fix**: Deep-copy `PEBBLE_LAYER_DICT` in `__init__`:
  ```python
  import copy
  self._layer_dict = copy.deepcopy(PEBBLE_LAYER_DICT)
  ```
- **Linter rule**: module-level mutable containers assigned as instance attributes without copy. Mechanically checkable via AST analysis.

### No config validation for `log_level`; `cpu`/`memory` only partially caught
- **Severity**: medium
- **Kind**: ux
- **Where**: `charmcraft.yaml` config options, `src/configs.py`
- **Evidence**: `log_level` accepts any string with no validation. Tested `log_level=banana` → accepted, charm stays active, value `BANANA` passed to workload. `cpu`/`memory` accept any string; tested `cpu=eleventybillion memory=not-a-real-unit` — the K8s resource patch library catches this ("Failed obtaining resource limit spec: Invalid limits spec", workload status briefly blocked), but the charm ultimately stays active with the resource patch silently doing nothing.
- **Impact**: operators get no feedback for invalid values; the workload may crash or silently ignore a bad log level, and resource limits can silently fail to apply.
- **Fix**: Add an `enum` constraint in `charmcraft.yaml` for `log_level` (`[info, debug, warning, error, critical]`). For `cpu`/`memory`, catch the resource patch failure and set a persistent blocked status.
- **Linter rule**: config options with documented allowed values should use an enum constraint or validate at hook time. Partially checkable.

### `ui-endpoint-info` marked `optional: True` in metadata but treated as required
- **Severity**: medium
- **Kind**: docs
- **Where**: `charmcraft.yaml:78` (`optional: True`), `src/charm.py:281`
- **Evidence**: `charmcraft.yaml` line 78 sets `optional: True` for `ui-endpoint-info`, but `_on_collect_status` checks `login_ui_integration_exists(self)` and sets `BlockedStatus("Missing integration ui-endpoint-info")` when missing. Confirmed in deployment: removing the relation causes blocked status.
- **Impact**: metadata says the integration is optional but the charm refuses to run without it — misleading to an operator reading the metadata.
- **Fix**: Change `optional: True` to `optional: False` in `charmcraft.yaml`, or relax the status check to `WaitingStatus`/warning instead of `BlockedStatus`.
- **Linter rule**: requires entries marked `optional: True` should not be checked as blocking in `_on_collect_status`. Mechanically checkable.

### `_on_resource_patch_failed` sets unit status directly, bypassing `_on_collect_status`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:235-237`
- **Evidence**:
  ```python
  def _on_resource_patch_failed(self, event: K8sResourcePatchFailedEvent) -> None:
      logger.error(f"Failed to patch resource constraints: {event.message}")
      self.unit.status = ops.BlockedStatus(event.message)
  ```
  This sets `self.unit.status` directly instead of going through `_on_collect_status`. The next `collect_unit_status` event overrides it, potentially with `ActiveStatus`, silently masking the failure.
- **Impact**: after a failed resource patch (e.g. bad cpu/memory), the charm briefly shows blocked then returns to active on the next `collect_unit_status` cycle — the operator sees active even though resource limits were never applied.
- **Fix**: Store the patch-failure state and check it in `_on_collect_status`, or call `_holistic_handler` to trigger a fresh status collection.
- **Linter rule**: event handlers that set `self.unit.status` directly instead of going through `_on_collect_status`. Mechanically checkable.

### No `upgrade-charm` handler — gap during `juju refresh`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` (no `upgrade_charm` observation)
- **Evidence**: `grep -rn "upgrade" src/` returns zero hits in charm code. Libraries (loki_push_api, grafana_dashboard, prometheus_scrape) handle `upgrade_charm` internally, but the charm itself does not.
- **Impact**: after a `juju refresh`, new charm code doesn't run until the next hook (config-changed, update-status, etc.). If a refresh changes Pebble layer config or relation handling, the old configuration persists until then. Only revision 11 is published so this could not be tested directly against a real refresh (unverified in production, but the code gap is real).
- **Fix**: Observe `self.on.upgrade_charm` and call `_holistic_handler`.
- **Linter rule**: charms should observe `upgrade_charm` or otherwise guarantee reconciliation runs on refresh. Advisory, not mechanically checkable.

### `Secrets.api_token` unguarded access
- **Severity**: low
- **Kind**: bug
- **Where**: `src/secret.py:63-64`
- **Evidence**:
  ```python
  @property
  def api_token(self) -> str:
      return self[API_TOKEN_SECRET_LABEL][API_TOKEN_SECRET_KEY]
  ```
  If the secret doesn't exist, `self[API_TOKEN_SECRET_LABEL]` returns `None`, and subscripting `None` raises `TypeError`. Called from `_holistic_handler` (`charm.py:233`) but only after `is_ready()` returns True, so protected today — still fragile.
- **Impact**: a future call path that skips the `is_ready()` guard would produce an unhandled `TypeError` instead of a clear error.
- **Fix**: Raise a custom `CharmError` with a clear message instead of letting a `TypeError` propagate.
- **Linter rule**: accessors on secret containers should check for `None` before subscript access. Mechanically checkable.

### `IngressData.load` reads template from filesystem on every hook
- **Severity**: low
- **Kind**: performance
- **Where**: `src/integrations.py:87-89`
- **Evidence**:
  ```python
  with open("templates/ingress.json.j2", "r") as file:
      template = Template(file.read())
  ```
  The template is opened and parsed from disk on every call to `IngressData.load()`, which happens via the `_pebble_layer` property called from `_holistic_handler`.
- **Impact**: minor I/O per hook. Not a real performance problem at this scale, but unnecessary.
- **Fix**: Load the template once at class definition or module level.
- **Linter rule**: file I/O in hot-path hook handlers. Mechanically checkable.

### No actions defined
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py` (no `ActionEvent` handlers)
- **Evidence**: `juju actions user-verification-service` returns "No actions defined" on both Juju 3.6 and 4.x.
- **Impact**: operators have no juju-native way to check service health, trigger a Salesforce check, or rotate the API token without `juju exec`.
- **Fix**: Add actions such as `check-status`, `get-version`, `rotate-api-token`.
- **Linter rule**: not mechanically checkable.

### `KratosRegistrationWebhookProvider` emits `ready` on `relation_created`, not `relation_changed`
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/kratos/v0/kratos_registration_webhook.py:174-175`
- **Evidence**:
  ```python
  def _on_relation_created(self, event: RelationCreatedEvent) -> None:
      self.on.ready.emit(event.relation)
  ```
  The provider emits `ready` immediately on relation creation, before the requirer has joined. The requirer side correctly waits for `relation_changed` with data before emitting ready — inconsistent with the provider's own model.
- **Impact**: not functionally broken — data sits in the app databag until the requirer joins — but `_holistic_handler` may run and try to update relation data before the remote end exists.
- **Fix**: Emit `ready` on `relation_changed` (or `relation_joined`) instead of `relation_created`.
- **Linter rule**: not mechanically checkable.

### CHANGELOG claims a config-no-change optimisation that is only partial
- **Severity**: nit
- **Kind**: docs
- **Where**: `CHANGELOG.md` (v1.3.4: "don't restart service if config didn't change"), `src/services.py:84-89`
- **Evidence**: the referenced fix changed `container.restart()` to `_restart_service()`, which calls `replan()`. `replan()` still restarts the service if any environment variable changed in the Pebble layer; the charm does not diff old vs. new config before re-rendering the layer.
- **Impact**: the changelog entry overstates the improvement — any config change affecting env vars (log_level, support_email, proxy settings, salesforce config) still triggers a restart, though this is better than the previous unconditional restart.
- **Fix**: Either implement full diff-detection before calling `plan()`, or reword the changelog to "don't restart service if Pebble layer unchanged".
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Holistic handler / reconciliation pattern** (`src/charm.py:227-243`): most event handlers delegate to `_holistic_handler`, which checks preconditions (`NOOP_CONDITIONS`, `EVENT_DEFER_CONDITIONS`) then reconciles all state. Clean and easy to reason about.
- **Condition/decorator pattern for pre-checks** (`src/utils.py`): `leader_unit` decorator, `container_connectivity`, `config_readiness` as composable `Condition` functions; the `NOOP_CONDITIONS`/`EVENT_DEFER_CONDITIONS` tuple approach is elegant.
- **Separation of concerns** (`src/`): `charm.py`, `configs.py`, `integrations.py`, `services.py`, `secret.py`, `env_vars.py` each have a clear single responsibility. The `EnvVarConvertible` protocol in `env_vars.py` neatly standardises how data sources contribute to workload environment.
- **`CollectStatusEvent`** (`src/charm.py:251-265`): uses the modern pattern correctly, adding statuses for multiple conditions rather than picking a single "winning" status.
- **Good config modelling** (`charmcraft.yaml`): `salesforce_consumer_secret` is `type: secret`, the correct Juju 3.x+ way to handle sensitive config.
- **`charm-user: non-root`** (`charmcraft.yaml`): explicit non-root charm user with `uid: 584792`/`gid: 584792`.

## Common-practice notes

- Conforms to Identity Platform library conventions (`LoginUIEndpointsRequirer/Provider`, `KratosRegistrationWebhookProvider`), ops framework 3.x idioms, and `cosl` observability libraries.
- No `StoredState` — all state derives from Juju model primitives (config, secrets, relations), the modern recommended approach.
- No `defer()` abuse — `EVENT_DEFER_CONDITIONS` is empty; the charm relies on the holistic handler running on every relevant event, correct for this pattern.
- Library versioning follows the standard `lib/charms/<charm>/v<N>/` convention.
- Terraform module present, follows the Identity Platform's module pattern with `MODULE_SPECS.md` generated by `terraform-docs`.
- Drifts from the `cosl` reconciler: `cosl.reconciler.reconcilable_events_k8s` is not used; the charm manually observes each event instead. Not necessarily worse, but worth noting.

## Tests

### Unit tests (11 tests, all passing)
```
$ PYTHONPATH=src:tests:lib python3 -m pytest tests/unit/ -v --tb=long
11 passed in 0.38s
```
(Requires `PYTHONPATH` set, since `from charm import ...` imports the charm from `src/`.)

Tests use the ops `scenario` library and cover:
- `PebbleReadyEvent`: port opened, holistic handler called, workload version set
- `ConfigChangedEvent`: missing config → BlockedStatus; full config → ActiveStatus
- Ingress ready/broken events: both result in ActiveStatus
- `_holistic_handler`: container not connected → WaitingStatus; all conditions satisfied → ActiveStatus with correct env vars
- `CollectStatusEvent`: parametrised for container connectivity, login-ui integration, service running

**Coverage gaps** (not tested):
- `Secrets`: `values()`, `is_ready()`, `api_token`, `__setitem__`, `__getitem__`
- `CharmConfig`: `_get_salesforce_consumer_info()`, `to_env_vars()` with Salesforce enabled
- `PebbleService`: `plan()`, `render_pebble_layer()`, `prepare_dir()`
- `WorkloadService`: `get_service()`, `set_version()`, `is_running()`
- `_on_pebble_check_failed`/`_on_pebble_check_recovered`: not exercised
- `SecretChangedEvent`: handler observed but never tested
- `_on_resource_patch_failed`: not tested
- `_on_leader_elected`/`_on_leader_settings_changed`: only exercised indirectly
- Non-leader unit behaviour: `_prepare_secrets` and relation data updates are `@leader_unit` guarded, but there's no test verifying non-leaders skip these
- `_on_internal_ingress_changed`: the `ingress.is_ready()` True path (with `submit_to_traefik`) is not tested

### Integration tests
`tests/integration/` uses `jubilant`, deploys the charm with traefik and login-ui, and verifies:
- `test_build_and_deploy`: charm reaches active/idle
- `test_app_health`: `GET /api/v0/status` returns 200
- `test_public_ingress_integration`: `/ui/registration_error` redirects (302)
- `test_error_redirect`: redirect URL contains the oidc_error_url and support email

Good end-to-end smoke tests, but no failure-injection tests (invalid secret, missing relation, killed workload, bad config).

### Lint
- `ruff check --show-fixes`: 0 issues
- `codespell`: clean

## Docs

- **README**: covers deployment, secret creation, config, and integration. Clear but concise. Would benefit from documenting `salesforce_enabled=false` for noop-mode dry runs.
- **CONTRIBUTING.md**: standard tox devenv/testing instructions, but line 7's "open an issue" link points to `https://github.com/canonical/hydra-operator/issues` instead of this repo — a copy-paste error.
- **Doc/reality mismatch on `ui-endpoint-info`**: `charmcraft.yaml` says `optional: True`, but the charm blocks when it's missing (see findings).
- **SECURITY.md**: standard vulnerability reporting process with private security advisory link.
- **CHANGELOG.md**: auto-generated by release-please, comprehensive (but see the nit above).
- **terraform/MODULE_SPECS.md**: auto-generated terraform-docs, accurate.
- **No discourse docs**: `_context/published-docs.md` confirms no published docs on discourse.
- **Doc/reality match**: README's deployment instructions match observed behaviour.

## Open questions

1. **Why is `startup: disabled` deliberate?** The pebble layer's service key was renamed from `WORKLOAD_CONTAINER` to `WORKLOAD_SERVICE` in commit `b2dc340`, but `startup` was already `disabled` before that. Is the charm relying on Juju's `pebble-ready` event to start the service on each pod startup? What happens if Pebble restarts independently (e.g. a Pebble daemon upgrade)?
2. **Does `charm-user: non-root` actually work?** `charmcraft.yaml` sets `charm-user: non-root` alongside `uid: 584792`/`gid: 584792` on the container. `non-root` governs the charm agent user, not the workload user, which runs as whatever the container image specifies. Whether the workload actually runs as 584792 is unverified — the minimal image has no `id` to check.
3. **Does the `kratos-registration-webhook` library's `on.ready` fire correctly?** `KratosRegistrationWebhookProvider._on_relation_created` emits `ready` immediately on relation creation, before the other side has set any data. Is this intentional, or should it wait for `relation_changed`?
</content>
