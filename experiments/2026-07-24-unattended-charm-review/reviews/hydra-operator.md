# hydra-operator

Charmed Ory Hydra wraps the Ory Hydra OAuth 2.0 / OpenID Connect server as a k8s Juju charm. Architecturally it's one of the stronger charms in the ecosystem — a declarative holistic-reconciliation loop, clean separation of integration plumbing from business logic, 182 passing unit tests at 81% coverage, and a working end-to-end deployment with correct upgrade/downgrade and migration handling. But two crash bugs sit on paths that are exercised in normal operation: `Relation.active` is accessed on `ops.model.Relation`, which has no such attribute in the pinned ops 3.8.0, crashing the entire holistic handler whenever stale OAuth relation data exists in peer storage; and the `list-oauth-clients` action fails on every fresh deployment because it conflates "zero clients" with "error listing clients." Two other actions throw raw `KeyError` on invalid enum input. A maintainer should fix the `Relation.active` bug first — it can wedge the charm out of reconciliation entirely — then the empty-list bug in `list-oauth-clients`, then the action `KeyError`s.

| | |
|---|---|
| Repo | canonical/hydra-operator @ `f9f0295` (2026-07-24) |
| Charms | hydra |
| Substrate | k8s |
| Deployed | yes — `concierge-k8s-3`, latest/edge rev 404; also tested latest/stable rev 396 |
| Reviewed | 2026-08-03 |

## What it does

Deploys Ory Hydra — an OAuth 2.0 / OIDC provider — on Kubernetes. Requires PostgreSQL (`pg-database`), a login UI (`ui-endpoint-info`), and a public route via Traefik (`public-route`). Supports optional internal route, tracing, logging, metrics, dashboards, and a token hook for custom token enrichment. Exposes 11 Juju actions: OAuth client CRUD, JWK rotation, database migration, secret key get/add, access token revocation, and OAuth client reconciliation.

## Deployment log

Deployed on `concierge-k8s-3` (Juju 3.6.25):

```sh
juju add-model rv-hydra-a
juju deploy hydra --channel edge --trust                                          # rev 404
juju deploy postgresql-k8s --channel 14/stable --trust                            # rev 925
juju deploy traefik-k8s --channel latest/stable --trust                           # rev 377
juju deploy self-signed-certificates --channel latest/stable                      # rev 264
juju deploy identity-platform-login-ui-operator --channel latest/edge --trust     # rev 205
juju integrate hydra:pg-database postgresql-k8s:database
juju integrate hydra:public-route traefik-k8s
juju integrate traefik-k8s:certificates self-signed-certificates:certificates
juju integrate hydra:ui-endpoint-info identity-platform-login-ui-operator:ui-endpoint-info
juju integrate identity-platform-login-ui-operator:hydra-endpoint-info hydra:hydra-endpoint-info
```

Reached active/idle in ~3 minutes. Hydra workload version `v26.2.0`.

First attempt on `concierge-k8s-4` (Juju 4.0.5) failed — `postgresql-k8s` 14/stable does not support Juju 4.x, and no available postgresql-k8s channel (14, 16, latest) does either. The hydra charm itself deploys fine standalone on Juju 4.x, but cannot form a functional stack without a Juju-4-compatible PostgreSQL charm. This is an ecosystem gap, not a charm bug.

Second attempt on `concierge-k8s-4` (Juju 4.0.5) failed for a different reason: the Juju client (4.0.12) is incompatible with the 4.0.5 controller (`"patterns are not implemented"`). No compatible Juju 4.x client snap was available, so full-stack Juju 4.x testing was blocked entirely.

Third deployment on `concierge-k8s-3` (`rv-hydra-d`) re-deployed the full stack for deeper testing, adding `grafana-agent-k8s` for metrics and `traefik-admin` for `internal-route`. Active after ~3 minutes. `internal-route` relation data exchanged correctly (`external_host: 10.43.45.2`, `scheme: https`), though `traefik-admin` itself remained blocked due to a missing load-balancer IP in this test cluster.

**Refresh upgrade/downgrade**:

```
rev 404 (v26.2.0) → rev 396 (v25.4.0) → rev 404 (v26.2.0)
```

Both directions worked correctly. After each refresh, the charm detected the version mismatch and entered `WaitingStatus("Waiting for migration to run, try running the run-migration action")`. Running `run-migration` restored active status. Downgrade: ~35s including migration. Upgrade: ~50s (pod restarted during agent restart), plus migration.

**Scale up/down**: Scaled to 2 units, both active; scaled back to 1 unit without issue. On a later deployment, scale 1→2 was re-tested with peer-data verification (follower's databag matched leader's); scale 2→1 was clean, with the departing unit entering maintenance while unit 0 stayed active throughout.

## Observed behaviour

- **Resource usage**: ~200m CPU, ~87Mi memory (via `kubectl top pod`).
- **Pebble plan**: service `hydra` runs `hydra serve all --config /etc/config/hydra.yaml` with `startup: disabled` (charm controls lifecycle). Two health checks: `ready` on `/health/ready` and `alive` on `/health/alive`.
- **Container image**: distroless (no shell, no `cat`, no `ls`) — all introspection goes through Pebble or the Hydra admin API.
- **Log spam during startup**: `ERROR External hostname is not set on the ingress provider` and `INFO Public route URL is not available. Deferring the event.` fire dozens of times before Traefik provides the hostname. `WARNING Raw mode enabled` (from the `traefik_route` lib) fires 2× per hook because both `public-route` and `internal-route` use raw mode.
- **Workload process kill & auto-recovery**: `pebble stop hydra` → checks went to `down, 3/3 failures`; Pebble detected the failure and the charm eventually restarted the service, checks recovering to `up, 0/3 failures`. `_on_pebble_check_failed` fired but only logged a warning — the status update relied on `_on_collect_status`.
- **Pod kill**: `kubectl delete pod hydra-0` → new pod created, charm reconfigured, back to active in ~33 seconds.
- **Config `cpu=invalid`, `memory=bad`**: accepted by Juju (type `string`, no validation pattern), but `KubernetesComputeResourcesPatch` rejects them. Charm goes to `BlockedStatus("Failed obtaining resource limit spec: Invalid limits spec: ...")` — clear message, recovers immediately once reset. Empty strings (`cpu=""`, `memory=""`) rejected the same way.
- **Config `log_level=invalid`**: accepted silently — the Jinja2 template defaults invalid values to `"info"`. No warning or blocked status; defensive but opaque to the operator.
- **Config `dev=true`**: accepted; `DEV="true"` appears in the Pebble layer, and the public-route-is-secure check in `_on_collect_status` correctly allows non-HTTPS routes in dev mode.
- **Remove pg-database relation**: `BlockedStatus("Missing integration pg-database")` within seconds, hydra service stopped. Re-adding recovers to active in ~20 seconds. Similarly, removing `ui-endpoint-info` or `public-route` produced immediate, correctly-worded blocked statuses, both recovering cleanly on re-add.
- **Config change hooks**: a `log_level` change fires exactly one `config-changed` hook, plus a Kubernetes resource-patch GET/PATCH/GET sequence. The PATCH runs on every hook even when resources haven't changed (dry-run PATCH first, then real PATCH).
- **Action `list-oauth-clients`**: fails on a fresh deployment with zero clients (confirmed bug); succeeds once at least one client exists.
- **Actions `add-secret-key type=invalid` and `get-secret-keys type=invalid`**: crash with uncaught `KeyError` instead of a clean action failure.
- **`add-secret-key type=system key=short`**: fails cleanly ("Key must have >16 characters").
- **All other actions with valid inputs** (`create-oauth-client`, `get-oauth-client-info`, `update-oauth-client`, `delete-oauth-client`, `rotate-key`, `run-migration`, `get-secret-keys`, `add-secret-key`, `revoke-oauth-client-access-tokens`, `reconcile-oauth-clients`) worked correctly, including clean failure messages for bad IDs (`update-oauth-client client-id=nonexistent`) and bad algorithms (`rotate-key algorithm=INVALID`).
- **Internal route**: `traefik-admin` integrated with `hydra:internal-route`; relation data populated correctly and internal endpoints updated to use the admin ingress.
- **Observability**: `grafana-agent-k8s` integrated via `metrics-endpoint` successfully. `logging` relation also available (requires `loki_push_api` on the provider side).
- **Juju 4.x standalone**: hydra deploys on Juju 4.0.5 (`concierge-k8s-4`), reaches `BlockedStatus("Missing integration pg-database")` correctly. Actions requiring a running service (e.g. `list-oauth-clients`) correctly fail with `"Service is not ready. Please re-run the action when the charm is active"`. Deeper Juju 4.x testing was blocked by the client/controller version mismatch noted above.
- **Actions from non-leader unit**: `run-migration` correctly fails with "Only the leader unit can run the database migration"; `reconcile-oauth-clients` correctly fails with "You need to run this action from the leader unit"; `get-secret-keys` succeeds from a non-leader (reads app-level Juju secrets, no leadership needed).
- **`create-oauth-client` with invalid grant types**: `grant-types='["invalid_grant"]'` is accepted with no validation — the action path constructs `OAuthClient` directly from `event.params`, bypassing the `OAuthRequirer` library's `ClientConfig.validate()` used on the relation-based path.
- **`run-migration` with negative timeout**: `timeout=-1` is accepted (Python `float()` conversion succeeds); Pebble then fails with an empty error message — no pre-validation that timeout > 0.
- **`_on_pebble_check_failed` / `_on_pebble_check_recovered`**: only log (warning / info respectively); status updates rely on `_on_collect_status` checking `is_failing()`, introducing an observed ~3-second gap between check failure and visible blocked status.
- **`_on_oauth_client_deleted` commented out**: in `src/charm.py` (around line 255) due to upstream ops issue #888 — it's impossible to distinguish relation removal from unit scale-down. OAuth clients created via the `oauth` relation are therefore not automatically deleted when the relation is removed; `_clean_up_oauth_relation_clients` is the intended remediation but is itself buggy (see findings below).

## Findings

### Uncaught `AttributeError` in OAuth client cleanup — `Relation.active` does not exist in ops 3.8.0
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:892`
- **Evidence**:
  ```python
  rel = self.model.get_relation(OAUTH_INTEGRATION_NAME, relation_id=int(rel_id))
  if rel.active:
      continue
  ```
  `ops.model.Relation` in the pinned ops 3.8.0 has no `active` attribute:
  ```
  $ python3 -c "import ops; print(ops.__version__); from ops.model import Relation; print(hasattr(Relation, 'active'))"
  3.8.0
  False
  ```
- **Impact**: `_clean_up_oauth_relation_clients()` is called from `_holistic_handler()` (line 612) without a try/except. Whenever a stale OAuth relation client exists in peer data, the holistic handler crashes with `AttributeError`, blocking all reconciliation — the charm gets stuck in maintenance/error and never reaches active. Coverage confirms this path (lines 848-880) is entirely untested.
- **Fix**: Replace `if rel.active` with a check against `self.model.relations`, e.g. `if rel and any(r.id == rel.id for r in self.model.relations[OAUTH_INTEGRATION_NAME])`, and add `if rel is None: to_delete.append(k); continue` before the attribute check.
- **Linter rule**: attribute access `.active` on `ops.model.Relation` is mechanically checkable by inspecting imports for `Relation` and flagging `.active` access.

### `list-oauth-clients` action fails when there are zero clients
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:795`, `src/cli.py:263`
- **Evidence**:
  ```python
  # charm.py:795
  if not (oauth_clients := self._cli.list_oauth_clients()):
      event.fail("Failed to list OAuth clients. Please check the juju logs")
      return

  # cli.py:218 — on error returns [], on success with no clients also returns []
  clients = json.loads(stdout)["items"]
  return [OAuthClient(**c) for c in clients]
  ```
  Observed on a fresh deployment with no clients: action consistently fails; succeeds after `create-oauth-client` is run once.
- **Impact**: the most basic introspection action fails on every fresh deployment. Operators see "Failed to list OAuth clients" when the correct answer is "no clients found." Integration tests only exercise this action after a client already exists, so this bug is not caught by CI.
- **Fix**: distinguish "error" from "empty" — have `list_oauth_clients` return `None` on error and `[]` on success with no clients; update the action handler to check `is None`.
- **Linter rule**: not mechanically checkable without taint analysis ("boolean check on collection that conflates empty with error").

### Uncaught `KeyError` in `get-secret-keys` and `add-secret-key` actions for invalid type
- **Severity**: high
- **Kind**: bug
- **Where**: `src/secret.py:83-86` (`get_secret_keys`), `src/secret.py:93-96` (`add_secret_key`)
- **Evidence**:
  ```python
  secret_label = {
      SYSTEM_SECRET: SYSTEM_SECRET_LABEL,
      COOKIE_SECRET: COOKIE_SECRET_LABEL,
  }[typ]
  ```
  Observed:
  ```
  $ juju run hydra/0 add-secret-key type=invalid key=my-long-key-over16
  Action id 23 failed: exit status 1
  Uncaught KeyError in charm code: 'invalid'
  ```
  `get-secret-keys type=invalid` fails identically.
- **Impact**: the action params declare `enumerate: [system, cookie]`, but Juju does not enforce this — any string reaches the handler, so users get a raw Python traceback instead of a clean error.
- **Fix**: replace `{...}[typ]` with `{...}.get(typ)` and `event.fail(...)` on `None`.
- **Linter rule**: bare dict key access on untrusted `event.params` input in action handlers — a pattern-based check would catch this.

### `_clean_up_oauth_relation_clients` has no unit test coverage
- **Severity**: high
- **Kind**: test-gap
- **Where**: `src/charm.py:881-916`
- **Evidence**: all lines in this function appear in the coverage "Missing" column; zero unit tests exercise the OAuth cleanup path. It contains the `Relation.active` bug above and the `remove_secret(None)` bug below — either would have been caught by a test.
- **Impact**: a failure here leaves orphaned Hydra clients and leaked Juju secrets, undetected until the charm crashes in production.
- **Fix**: add `ops.testing` unit tests with peer data containing stale OAuth client entries, covering both existing and non-existing relations.
- **Linter rule**: not mechanically checkable without coverage data ("function with >0 lines and 0% test coverage").

### `remove_secret(rel)` crashes when `rel` is `None`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:911`, `lib/charms/hydra/v0/oauth.py:778`
- **Evidence**:
  ```python
  # charm.py:911
  self.oauth_provider.remove_secret(rel)

  # oauth.py:778
  def remove_secret(self, relation: Relation) -> None:
      return self._delete_juju_secret(relation)

  # oauth.py:751-752
  def _get_secret_label(self, relation: Relation) -> str:
      return f"client_secret_{relation.id}"
  ```
  If `get_relation()` returns `None`, the loop already crashes on `rel.active` first; once that's fixed, it crashes again here at `relation.id`.
- **Impact**: after fixing the `.active` bug, the cleanup code still crashes for orphaned peer-data keys where the relation has been fully removed.
- **Fix**: add `if rel is None: to_delete.append(k); continue` before any attribute access, and skip `remove_secret` for `None` relations.
- **Linter rule**: unguarded access on the result of `get_relation()` — mechanically checkable.

### `_on_collect_status` has no unit test coverage
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/charm.py:625-669`
- **Evidence**: `# noqa: C901` complexity annotation, 9 conditional branches with `event.add_status()`, but zero unit tests. Coverage shows lines 625-669 hit only from integration tests.
- **Impact**: this is the operator-facing status surface; `event.add_status()` accumulates multiple simultaneous conditions but only the highest priority is shown, and that priority ordering is untested.
- **Fix**: add unit tests using `ops.testing`'s `collect_unit_status` event, covering each branch individually and in combination.
- **Linter rule**: not established.

### `_on_pebble_check_failed` / `_on_pebble_check_recovered` do not update status directly
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/charm.py:614-616`
- **Evidence**:
  ```python
  def _on_pebble_check_failed(self, event: PebbleCheckFailedEvent) -> None:
      if event.info.name == PEBBLE_READY_CHECK_NAME:
          logger.warning("The service is not running")
  ```
  Only logs; status update happens via `_on_collect_status` → `is_failing()`. Observed ~3-second gap between check failure and blocked status appearing. Same pattern in `_on_pebble_check_recovered` (logs info only).
- **Impact**: operators see a delay between workload crash and status reflecting it, and a possible window where status is stale during recovery.
- **Fix**: set `self.unit.status = BlockedStatus(...)` directly in the handler, or explicitly invoke the collect-status logic.
- **Linter rule**: "pebble_check_failed handler that doesn't set unit status" — mechanically checkable.

### ERROR-level log spam for a normal startup condition
- **Severity**: medium
- **Kind**: lint / ux
- **Where**: `src/integrations.py:304`
- **Evidence**:
  ```python
  if not external_host:
      logger.error("External hostname is not set on the ingress provider")
      return cls()
  ```
  Fires from `PublicRouteData.load()` on every relation hook until Traefik provides `external_host`; since `_on_collect_status` calls `load()` twice (via `public_route_is_ready()` and `public_route_is_secure()`), this ERROR fires 2× per collect-status invocation during startup.
- **Impact**: this is not actually an error — the charm handles missing hostname correctly (returns empty data, defers) — but it pollutes juju debug-log at ERROR severity, dozens of times per deploy.
- **Fix**: downgrade to `logger.debug`/`info`, and de-duplicate the double `load()` call (see below).
- **Linter rule**: not established.

### Kubernetes resource PATCH on every hook regardless of change
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:168-171` (`KubernetesComputeResourcesPatch` initialization)
- **Evidence**: every `config-changed` and relation hook triggers a GET/PATCH(dry-run)/GET/PATCH cycle against the statefulset even when resource config hasn't changed.
- **Impact**: unnecessary API calls to the k8s API server on every hook; adds up under relation churn.
- **Fix**: cache the computed `ResourceRequirements` and skip the patch call when unchanged.
- **Linter rule**: not established.

### Direct mutation of private library attribute `_relation`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:378`, `src/charm.py:405`
- **Evidence**:
  ```python
  # needed due to how traefik_route lib is handling the event
  self.internal_ingress._relation = event.relation
  ```
  Comments acknowledge this is a workaround for a library bug.
- **Impact**: private attribute access breaks silently if the `traefik_route` lib renames or removes `_relation`.
- **Fix**: fix the upstream library or vendor a patched copy.
- **Linter rule**: private attribute access — already flaggable by pyright/pylint.

### Outdated README with wrong relation names
- **Severity**: low
- **Kind**: docs
- **Where**: `README.md:31-38`
- **Evidence**: README shows `juju integrate traefik-k8s hydra:public-ingress` and `juju integrate traefik-admin hydra:admin-ingress`; the charm exposes `public-route` and `internal-route`. Verified correct commands during deployment:
  ```sh
  juju integrate hydra:public-route traefik-k8s
  juju integrate hydra:internal-route traefik-admin
  ```
- **Impact**: new operators following the README get relation-not-found errors.
- **Fix**: update README and its "Integrations" section to the current relation names.
- **Linter rule**: not established.

### JWT access token config toggle — fragile bool-to-string roundtrip
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:508`, `lib/charms/hydra/v0/oauth.py:215-225`
- **Evidence**:
  ```python
  jwt_access_token=self.config.get("jwt_access_tokens", True),
  # oauth.py: elif isinstance(v, bool): ret[k] = str(v)
  ```
  Round-trips correctly today (bool → `"True"` string → `strtobool`), but is fragile against future type or library changes.
- **Impact**: a config type change or `_dump_data` behaviour change could silently break the value. Confirmed working end-to-end in integration tests (both opaque and JWT token flows pass).
- **Fix**: explicit cast, e.g. `bool(self.config.get("jwt_access_tokens", True))`.
- **Linter rule**: not established.

### `list_oauth_clients` return type conflates error and empty
- **Severity**: low
- **Kind**: lint
- **Where**: `src/cli.py:200-218`
- **Evidence**: returns `[]` both on error and on success with zero clients.
- **Impact**: this is the direct root cause of the `list-oauth-clients` critical finding above.
- **Fix**: return `None` on error, `[]` on empty success, and update all callers.
- **Linter rule**: not established ("function returning empty collection for both error and success").

### Dead code constants for removed relation names
- **Severity**: low
- **Kind**: lint
- **Where**: `src/constants.py:34-35`
- **Evidence**:
  ```python
  PUBLIC_INGRESS_INTEGRATION_NAME = "public-ingress"
  ADMIN_INGRESS_INTEGRATION_NAME = "admin-ingress"
  ```
  Not imported or used anywhere in `src/`, `lib/`, or `tests/`; the charm migrated to `public-route`/`internal-route` in v2.0.0.
- **Impact**: dead code misleads contributors and echoes the same wrong relation names as the stale README.
- **Fix**: remove both constants.
- **Linter rule**: unused import/constant — mechanically checkable by static analysis.

### Traefik raw-mode `WARNING` logged on every hook execution
- **Severity**: low
- **Kind**: ux
- **Where**: `lib/charms/traefik_k8s/v0/traefik_route.py:362`
- **Evidence**: `TraefikRouteRequirer.__init__` logs a warning when `raw=True`; the charm creates two such instances (`public-route`, `internal-route`), so the warning fires 2× per hook — ~20+ times observed during initial deploy.
- **Impact**: noisy operator logs for a condition that's meaningful only once.
- **Fix**: guard the warning to fire only on first instantiation, or fix upstream.
- **Linter rule**: not mechanically checkable (external library).

### `_on_collect_status` calls `PublicRouteData.load()` twice per invocation
- **Severity**: low
- **Kind**: performance
- **Where**: `src/utils.py:52-67`, `src/charm.py:625-669`
- **Evidence**: `public_route_is_ready()` and `public_route_is_secure()` each call `PublicRouteData.load()` independently, doubling both the relation read and the ERROR log noise described above.
- **Impact**: duplicated work and doubled log spam on a hot code path.
- **Fix**: call `load()` once, store the result, query `.is_ready()` and `.secured` from it.
- **Linter rule**: not established.

### `log_level` config silently defaults to `"info"` for invalid values
- **Severity**: low
- **Kind**: ux
- **Where**: `templates/hydra.yaml.j2:1-2`
- **Evidence**:
  ```yaml
  {% set valid_log_levels = ["panic", "fatal", "error", "warn", "info", "debug", "trace"] %}
  {% set log_level = log_level if log_level in valid_log_levels else "info" %}
  ```
  Confirmed: `juju config hydra log_level=invalid` is accepted, charm stays active, no indication the value was ignored.
- **Impact**: an operator who typos `warning` for `warn` gets silently different behaviour.
- **Fix**: validate in `config-changed` and set `BlockedStatus` (or at least log a warning) for invalid values.
- **Linter rule**: not established.

### No validation on `cpu`/`memory` config
- **Severity**: low
- **Kind**: ux
- **Where**: `charmcraft.yaml:184-196`
- **Evidence**: `cpu` and `memory` are `type: string` with no pattern validation; invalid or empty values are only caught at runtime by `KubernetesComputeResourcesPatch`.
- **Impact**: worse error-message experience than necessary — the eventual message is fine, but earlier validation would be faster feedback.
- **Fix**: add a `pattern` regex to these config options, or validate in `config-changed`.
- **Linter rule**: not established.

### `_pop_relation_data` guard uses wrong condition — dead but latent
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/hydra/v0/oauth.py:255`
- **Evidence**:
  ```python
  if len(self.model.relations) == 0:
      return
  ```
  Checks whether *any* relations exist on the model, not whether the specific OAuth relation exists.
- **Impact**: the only caller (`_on_relation_broken`) is currently commented out (ops issue #888), so this is dead code today — but if that caller is restored, the guard fails to protect against the specific relation being absent while other relations exist.
- **Fix**: change to `if self._relation_name not in self.model.relations: return`.
- **Linter rule**: `len(self.model.relations)` used to check specific-relation existence — mechanically checkable.

### `_on_oauth_client_changed` defers indefinitely without status feedback
- **Severity**: low
- **Kind**: bug / ux
- **Where**: `src/charm.py:543-559`
- **Evidence**:
  ```python
  if not self._cli.update_oauth_client(target_oauth_client):
      logger.error(...)
      event.defer()
  ```
  No status update accompanies the defer; the charm stays in whatever status it had, and the event re-fires on every subsequent hook indefinitely.
- **Impact**: on a persistent failure (Hydra not running, malformed requirer config) the charm enters an invisible infinite-defer loop with no operator-facing signal. (Definitively demonstrating this end-to-end would require a malformed `oauth` requirer, which was not tested — unverified in practice, but the code path is confirmed.)
- **Fix**: set `BlockedStatus`/`WaitingStatus` before deferring; consider a retry limit.
- **Linter rule**: `event.defer()` without a status update in an event handler — mechanically checkable.

### `create-oauth-client` action bypasses grant type validation
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:710-718`, `src/cli.py:72-74`
- **Evidence**: `OAuthClient` has no validator on `grant_types`; the relation-based path validates via `OAuthRequirer`'s `ClientConfig.validate()`, but the action path constructs `OAuthClient(**event.params)` directly. Confirmed: `create-oauth-client grant-types='["invalid_grant"]'` succeeds.
- **Impact**: operators can create non-functional OAuth clients with no warning; failures only surface later, confusingly, at token-issuance time.
- **Fix**: add a `field_validator` on `grant_types`, or validate in the action handler.
- **Linter rule**: not established.

### `run-migration` accepts negative timeout
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:694`
- **Evidence**: `timeout = float(event.params.get("timeout", 120))`. Confirmed `timeout=-1` is accepted; Pebble then fails with an empty error message.
- **Impact**: confusing empty-error UX for a trivially preventable input mistake.
- **Fix**: `if timeout <= 0: event.fail("Timeout must be positive"); return`.
- **Linter rule**: not established.

## Worth copying

1. **Holistic handler with condition gates** (`src/charm.py:571-612`, `src/utils.py:72-87`): `NOOP_CONDITIONS` (early exit) and `EVENT_DEFER_CONDITIONS` (defer) are tuples of callables checked before any work — declarative and easy to extend, preferable to deeply nested if/return chains.
2. **Config file dedup before restart** (`src/services.py:99-105`): `PebbleService.plan()` diffs the rendered config against what's on disk and only pushes+restarts on change, avoiding needless workload restarts on no-op hooks.
3. **Jinja2 template defensive defaults** (`templates/hydra.yaml.j2:1-2`): validates `log_level` against a hardcoded list and defaults invalid input to `"info"` — silent (see finding above), but validate-in-template is a good pattern for other charms with complex config templates.
4. **`ops.testing` fixture pattern** (`tests/unit/conftest.py`): a single `create_state()` factory pre-populates containers with `Exec` mocks, peer/db/public-route relations, and secrets; individual tests compose via keyword arguments.
5. **Separation of business logic from integration plumbing** (`src/integrations.py`): each integration has a frozen dataclass with a `load()` classmethod and `to_service_configs()`/`to_env_vars()` methods, keeping `charm.py` thin and testable.
6. **Charm config as a service config source** (`src/configs.py:20-85`): `CharmConfig` implements the `ServiceConfigSource` protocol alongside the integration dataclasses; `ConfigFile.from_sources(*sources)` merges them via `ChainMap`.
7. **Migration detection on refresh** (`src/charm.py:337-340`): `migration_needed` compares workload version against the last-migrated version in peer data, correctly putting the charm in a waiting state after `juju refresh` rather than silently migrating.
8. **Pebble health checks with auto-recovery** (`src/services.py:33-50`): `ready` and `alive` checks let Pebble detect and restart a dead workload process; recovery observed on multiple deployments.

## Common-practice notes

- **Follows**: standard k8s charm layout (`src/`, `lib/`, `templates/`, `tests/unit`, `tests/integration`), ops framework idioms, `charmcraft.yaml` with `assumes: [juju >= 3.0.2, k8s-api]`; library versioning under `lib/charms/hydra/v0/` with LIBID/LIBAPI/LIBPATCH; Terraform module for the Juju provider.
- **Drifts slightly**: uses a `src/` layout rather than a flatter top-level pattern seen in simpler charms — appropriate given complexity.
- **Drifts**: the `TraefikRouteRequirer._relation` workaround is a known ecosystem quirk, but many charms handle it by instantiating `TraefikRouteRequirer(...)` inside the handler instead of mutating a private attribute.
- **Leads**: the holistic-handler + condition-tuples pattern is cleaner than most charms in the ecosystem and worth standardizing on.
- **Ecosystem gap**: Juju 4.x deployment is blocked by `postgresql-k8s` not supporting Juju 4.x on any channel (14, 16, latest); hydra's own `assumes: [juju >= 3.0.2]` is correct, but no working full stack can be formed on 4.x today.

## Tests

- **Unit tests**: 182 passed, 5 xfailed (known issue #268 — client deletion on relation removal), 1 xpassed, 81% coverage. `tox -e unit`, ~7s. Uses `ops.testing.Context` (scenario) throughout with well-structured `conftest.py` fixtures.
- **Integration tests**: comprehensive — full-stack deploy (hydra, postgres, traefik×2, self-signed-certs, login-ui), action coverage (create/list/get/update/delete clients), OAuth flows (opaque + JWT), scale-up/down, relation removal/recovery (pg-database, public-route, login-ui), JWKS endpoint, OpenID discovery, rotate-key. Uses `jubilant`. Does **not** test: `list-oauth-clients` on empty state (only tested after a client is created — misses the empty-list bug), `reconcile-oauth-clients`, `get-secret-keys`/`add-secret-key`, `run-migration` explicitly (only implicitly via deploy/refresh).
- **Coverage gaps mapped to findings**:
  - `src/cli.py` at 56% — untested `list_oauth_clients` empty-list path (would have caught the critical `list-oauth-clients` bug), and several other failure paths.
  - `src/charm.py` at 83% — `_clean_up_oauth_relation_clients` entirely untested (would have caught the `Relation.active`/`remove_secret(None)` bugs), `_on_collect_status` entirely untested, `_on_internal_ingress_changed`/`_on_internal_ingress_joined` gaps.
  - `src/configs.py` at 67% — untested `get_system_secret`/`get_cookie_secret` paths.
  - `src/integrations.py` at 97% — three untested lines.
- **Lint**: `ruff check` and `codespell` both pass cleanly. `.pre-commit-config.yaml` includes mypy, ruff, codespell, markdownlint, isort, conventional-pre-commit.

## Docs

- **README**: accurate description, but uses stale relation names (`public-ingress`, `admin-ingress`) from pre-2.0 versions; deployment commands omit `--channel` for hydra. Migration walkthrough is thorough and correct.
- **Doc/reality mismatch confirmed**: README's `juju integrate traefik-k8s hydra:public-ingress` does not work — the charm only exposes `public-route` since v2.0.0; `juju integrate hydra:public-route traefik-k8s` is required.
- **Charmhub description**: minimal ("Charmed Ory Hydra"), with links to documentation and issues present.
- **terraform/MODULE_SPECS.md**: clean, auto-generated terraform-docs output.
- **CONTRIBUTING.md**: standard, with tox devenv instructions and a Matrix chat link.

## Open questions

1. **Does `list-oauth-clients` intermittently fail on first run?** Resolved — the empty-list bug explains this deterministically; behaviour is not intermittent.
2. **Is `jwt_access_tokens` config actually consumed correctly by the requirer?** Confirmed working end-to-end (opaque and JWT token flows both pass in integration tests), but the bool-to-string round-trip through `_dump_data`/`strtobool` remains fragile against future changes.
3. **What happens on Juju 4.x with a compatible PostgreSQL?** Untestable currently — hydra deploys and runs standalone correctly on Juju 4.0.5, and `assumes: [juju >= 3.0.2]` is accurate, but full-stack deployment is blocked by `postgresql-k8s` lacking Juju 4.x support, compounded by a Juju 4.0.12 client / 4.0.5 controller incompatibility.
4. **Why is `_on_oauth_client_deleted` commented out?** Disabled due to upstream ops issue #888 (cannot distinguish relation removal from unit scale-down). `_clean_up_oauth_relation_clients` is the intended remediation path but is itself buggy.
5. **Can `create-oauth-client` create clients with invalid grant types?** Yes, confirmed — the action bypasses the library's validation and Hydra accepts arbitrary grant type strings.
6. **Does `_on_oauth_client_changed` enter an infinite defer loop on failure?** The code path supports this reading (defer with no status update, no retry limit), but demonstrating it end-to-end would require a malformed `oauth` requirer, which was not exercised — unverified.
</content>
