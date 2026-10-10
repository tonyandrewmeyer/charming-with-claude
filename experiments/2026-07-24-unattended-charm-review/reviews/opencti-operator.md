# opencti-operator

A large, well-structured family of Juju charms deploying the OpenCTI threat intelligence platform on Kubernetes. The primary `opencti` charm is in decent shape — clean reconciliation loop, correct status precedence, 86% unit test coverage, sensible secret handling — but it has a critical resilience gap confirmed live: a transient Juju secret-backend timeout crashes the charm to `error` status because `_init_peer_relation` only catches `SecretNotFoundError`, not `ModelError`. The same narrow-catch pattern recurs in three other secret-access paths. There is also a real credential-leak bug (Redis passwords logged at ERROR level) and a reachable `IndexError` in the RabbitMQ env builder. A maintainer should first fix the `ModelError` handling in `_init_peer_relation`/`_get_peer_secret`/`_cleanup_secrets` (or add a catch-all in `_reconcile`), then redact `_dump_integration`'s output, then guard `_gen_rabbitmq_env` against an empty unit list. The 22 connector charms are cleanly template-generated except the hand-written WOAP connector, which duplicates and diverges from the base class's reconcile logic.

| | |
|---|---|
| Repo | canonical/opencti-operator @ `d639522` (2026-07-06) |
| Charms | opencti + 22 connector charms |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5) and concierge-k8s-3 (Juju 3.6.25); latest/edge rev 117. (Draft states the concierge-k8s-4 deploy "timed out"; notes do not corroborate this and show successful deploys/tests on that controller — unverified.) |
| Reviewed | 2026-08-04 |

## What it does

Deploys and manages [OpenCTI](https://filigran.io/solutions/open-cti/) (Node.js backend + Python workers) on Kubernetes via Juju. The primary `opencti` charm integrates with OpenSearch, Redis, RabbitMQ, S3-compatible storage, and ingress, and creates per-connector users in the OpenCTI API, distributing credentials via Juju secrets. The 22 connector charms wrap individual OpenCTI connectors (AlienVault, MITRE, URLhaus, CrowdStrike, VirusTotal, etc.) for importing/exporting threat intelligence. Connector charms are mostly generated from `scripts/gen_connector_charm.py` via a Jinja2 template; the WOAP connector is hand-written.

## Deployment log

**Model `rv-opencti-full` on `concierge-k8s-4` (Juju 4.0.5)**

```bash
juju switch concierge-k8s-4
juju add-model rv-opencti-full
juju deploy opencti --channel latest/edge  # rev 117
juju deploy redis-k8s --channel latest/edge --trust
juju deploy s3-integrator --channel latest/edge --config bucket=opencti --config endpoint=http://s3.example.com
juju deploy nginx-ingress-integrator --channel edge --trust --config path-routes=/ --config service-hostname=opencti.local --revision=109
juju integrate opencti redis-k8s
juju integrate opencti s3-integrator
juju integrate opencti nginx-ingress-integrator
```

- Image pull took ~4 minutes on this controller (cached from an earlier deploy on the same cluster); first-time pull in a prior model was 8m19s for the 1.58GB image.
- With redis, s3, and ingress present but `opensearch-client` and `amqp` missing, the charm correctly showed `blocked: "missing integration(s): opensearch-client, amqp"`.
- `nginx-ingress-integrator` went active quickly (revision 109, ubuntu@20.04 base).
- `s3-integrator` remained `blocked: "Missing parameters: ['access-key', 'secret-key']"` — correct, since no credentials were configured.

**Failure injection: secret backend timeout**

The charm spontaneously crashed on an `update-status` hook at 12:29:51 when the Juju secret backend (etcd) returned `"etcdserver: request timed out"`. The error propagated from `_init_peer_relation` → `_reconcile_platform` → `_reconcile`, none of which catch `ops.ModelError`. Result: `error: hook failed: "update-status"`.

```
File "src/charm.py", line 452, in _init_peer_relation
    self.model.get_secret(id=secret_id)
File "venv/ops/model.py", line 3928, in secret_get
    with self._wrap_hookcmd('secret-get', ...):
ops.model.ModelError: ERROR cannot ensure service account "unit-opencti-0": etcdserver: request timed out
```

The charm recovered on the next `update-status` (5 minutes later) when the backend became available again.

**Config injection**

- Setting `admin-user="not-a-secret-id"` (invalid secret reference) was accepted but the charm stayed `blocked` on missing integrations — correct precedence (integration checks run before the admin-user config check).
- Setting a valid Juju secret (via `juju add-secret` / `juju grant-secret`) also left the charm `blocked` on integrations — correct.

**Relation lifecycle**

- Removing the `redis-k8s` relation: status updated immediately to `"missing integration(s): opensearch-client, redis, amqp"`.
- Re-adding the relation: briefly still showed redis as missing (1–2 hooks) before the remote unit list populated — expected transient state, self-recovered.

**Connector charm: `opencti-export-file-stix-connector`**

```bash
juju deploy opencti-export-file-stix-connector --channel latest/edge  # rev 117
```

- Started as `waiting: "missing configurations: connector-scope"`.
- After `juju config opencti-export-file-stix-connector connector-scope="application/json"`: `waiting: "missing opencti-connector integration"`.
- After `juju integrate opencti opencti-export-file-stix-connector`: `waiting: "waiting for opencti-connector integration"` — correct; the main charm can't provide credentials until its own dependencies are met.

**Scale test (connector)**

- `juju scale-application opencti-export-file-stix-connector 2`: new unit 1 went to `blocked: "connector charm cannot have multiple units, scale down using the \`juju scale\` command"`. Unit 0 stayed `waiting` until the next hook reconciled (eventual consistency).
- Scaling back to 1: unit 0 recovered to `waiting` promptly; unit 1 terminated cleanly.

**Scale test (opencti on Juju 3.6)**

- Scaling opencti to 2 units: both units showed identical `blocked` status. OpenCTI intentionally supports multiple units (workers scale horizontally), unlike connectors.
- Scaling back to 1: clean teardown.

**Cross-version comparison (Juju 3.6.25 vs 4.0.5)**

```bash
juju switch concierge-k8s-3
juju add-model rv-opencti-j3
juju deploy opencti --channel latest/edge  # rev 117
```

Deployed opencti rev 117 on concierge-k8s-3 with no integrations. Charm entered `blocked: "missing integration(s): opensearch-client, redis, amqp, s3, ingress"` — identical to Juju 4.0.5. Config injection, status transitions, and scale-up/down all matched. No version-specific issues observed.

## Findings

### 1. `_init_peer_relation` crashes on transient Juju secret-backend errors — observed live
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:452` (except clause `src/charm.py:449-454`)
- **Evidence**: live traceback:
  ```
  File "src/charm.py", line 452, in _init_peer_relation
      self.model.get_secret(id=secret_id)
  ops.model.ModelError: ERROR cannot ensure service account "unit-opencti-0": etcdserver: request timed out
  ```
  The except clause only catches `ops.SecretNotFoundError`:
  ```python
  try:
      self.model.get_secret(id=secret_id)
      return
  except ops.SecretNotFoundError:
      logger.error("secret %s removed unexpectedly", secret_id)
  ```
  The `ModelError` propagates through `_init_peer_relation` → `_reconcile_platform` → `_reconcile`, none of which catch it.
- **Impact**: A transient etcd timeout (or any secret-backend blip) takes the charm offline — `error: hook failed: "update-status"` — for up to 5 minutes until the next `update-status`, with no actionable message. The same uncaught-`ModelError` pattern exists in `_get_peer_secret` (`src/charm.py:432`) and `_cleanup_secrets` (`src/charm.py:207`); `_setup_connector_integration_and_user` was also flagged in the draft as sharing this pattern (unverified — not directly quoted in notes). Only `_gen_secret_env` catches `ModelError` properly, so handling is inconsistent across the codebase. The connector library's `_reconcile` has the same vulnerability.
- **Fix**: Catch `ops.ModelError` alongside `SecretNotFoundError` in `_init_peer_relation` and re-raise as `IntegrationNotReady`, or add a broad `except Exception` in `_reconcile` that sets `WaitingStatus` instead of crashing on transient infrastructure errors.
- **Linter rule**: mechanically checkable — "ops.ModelError not caught in secret access path"

### 2. `_dump_integration` logs relation data including credentials at ERROR level
- **Severity**: high
- **Kind**: bug (security)
- **Where**: `src/charm.py:687-716`; called from `_gen_redis_env` (`src/charm.py:616`) and `_extract_opensearch_info` (`src/charm.py:575`)
- **Evidence**:
  ```python
  def _dump_integration(self, name: str) -> str:
      ...
      dump["application-data"] = dict(integration.data[app])
      dump["unit-data"] = {unit.name: dict(integration.data[unit]) for unit in units}
      return json.dumps(dump)
  ```
  ```python
  logger.error("invalid redis integration: %s", self._dump_integration("redis"))
  logger.error("invalid opensearch-client integration: %s", self._dump_integration("opensearch-client"))
  ```
- **Impact**: When a Redis integration is invalid, the entire relation data — including `redis-password` and `sentinel-password`, observed present at relation-id 3 in the live deployment — is logged at ERROR level, appearing in `juju debug-log`, model logs, and any log-forwarding destination (e.g. Loki). For OpenSearch, the logged fields (`secret-user`, `secret-tls`) are secret URIs rather than content, so the exposure there is lower risk; the Redis case is a real credential leak.
- **Fix**: Strip sensitive fields (password, secret-key, access-key, redis-password, sentinel-password) before logging, or log only field names, not values.
- **Linter rule**: mechanically checkable — "logger.error() with relation data without redaction"

### 3. `_gen_rabbitmq_env` crashes with `IndexError` when the `amqp` relation has no units
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:629`
- **Evidence**:
  ```python
  integration = typing.cast(ops.Relation, self.model.get_relation("amqp"))
  unit = sorted(list(integration.units), key=lambda u: int(u.name.split("/")[-1]))[0]
  data = integration.data[unit]
  ```
- **Impact**: Between `amqp-relation-joined` and `amqp-relation-changed`, the relation can exist with app data set but no units yet. `sorted(...)[0]` then raises `IndexError`, which is not caught by `_reconcile`'s exception handling (it only catches the charm's own exception types), crashing the hook. Not observed live (the amqp relation was never exercised), but reachable in production.
- **Fix**: Guard with `if not integration.units: raise IntegrationNotReady(...)` before the sorted call.
- **Linter rule**: mechanically checkable — "subscript on sorted(relation.units) without emptiness guard"

### 4. Pebble start failures in connector charms retry with no limit
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/opencti/v0/opencti_connector.py:247-251`
- **Evidence**:
  ```python
  try:
      container.replan()
      container.start("connector")
  except ops.pebble.ChangeError as exc:
      raise Blocked("failed to start connector, will retry") from exc
  ```
- **Impact**: `Blocked` sets status to "failed to start connector, will retry" but there is no bounded retry — every subsequent hook (e.g. `update-status`) re-pushes the layer and retries `start()`. If the connector binary is fundamentally broken (wrong arch, missing library), the charm loops `Blocked` → hook → `Blocked` indefinitely.
- **Fix**: Check `container.get_service("connector").is_running()` before starting; skip if already running. Track consecutive failures and escalate to a permanent `Blocked` after N attempts.
- **Linter rule**: mechanically checkable — "container.start() in reconcile loop without idempotency guard"

### 5. WOAP connector overrides `_reconcile`, duplicating the base class
- **Severity**: medium
- **Kind**: bug (maintainability)
- **Where**: `connectors/woap/src/charm.py:85-113`
- **Evidence**:
  ```python
  missing_requirements = []
  try:
      self._check_integration()
      self._reconcile_integration()
  except NotReady:
      missing_requirements.append("OpenCTI relation")
  # ... check OpenSearch relation ...
  if missing_requirements:
      self.unit.status = ops.WaitingStatus("Waiting for: " + ", ".join(missing_requirements))
      self.stop_connector()
      return
  ```
- **Impact**: Reimplements multi-unit check, config validation, and status precedence with a different pattern (list accumulation vs. sequential raise) than the base class. Bugfixes to `OpenctiConnectorCharm._reconcile` will not automatically apply to WOAP. The `stop_connector()` call on missing requirements is a good idea but is stranded in WOAP instead of the base class; WOAP's `_check_config` override also duplicates the base class's required-config check.
- **Fix**: Move `stop_connector()` into `OpenctiConnectorCharm`; add an `_extra_validate_config()` extension point WOAP can override; refactor WOAP's `_reconcile` to call `super()._reconcile()`.
- **Linter rule**: not mechanically checkable (architectural)

### 6. Connector `_gen_env` raises `NotReady` with a misleading message
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `lib/charms/opencti/v0/opencti_connector.py:174-175`
- **Evidence**:
  ```python
  if not opencti_url or not opencti_token_id:
      raise NotReady("waiting for opencti-connector integration")
  ```
- **Impact**: The integration itself already exists (`_check_integration` passed) — the provider just hasn't populated the data. The message implies the relation is missing, and an operator may re-run `juju integrate` unnecessarily.
- **Fix**: Change message to "waiting for OpenCTI platform credentials".
- **Linter rule**: not mechanically checkable

### 7. Documentation has copy-paste errors in integration descriptions
- **Severity**: medium
- **Kind**: docs
- **Where**: `docs/reference/integrations.md:5, 17, 30, 42, 53`
- **Evidence**: every non-redis section says "uses the `redis` integration":
  ```
  ### `opensearch-client`
  OpenCTI charm uses the `redis` integration to obtain OpenSearch server connection information.

  ### `amqp`
  OpenCTI charm uses the `redis` integration to obtain rabbitmq connection information.

  ### `s3`
  OpenCTI charm uses the `redis` integration to obtain S3 compatible storage credentials.

  ### `ingress`
  OpenCTI charm uses the `redis` integration to obtain S3 ingress services.
  ```
  The `ingress` section additionally says "S3" instead of "ingress".
- **Impact**: Confuses operators skimming the reference.
- **Fix**: Replace "redis" with the correct integration name in each section; fix "S3" → "ingress" in the ingress section.
- **Linter rule**: mechanically checkable — script checking integration-name mismatches in docs

### 8. `_check_preconditions` checks `integration.units` but not remote app data
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:434`
- **Evidence**:
  ```python
  if integration is None or integration.app is None or not integration.units:
      missing_integrations.append(integration_name)
  ```
- **Impact**: On cross-model relations the consumer side may have no units but valid app data; the check passes anyway, and the later `_gen_*_env` methods then raise `IntegrationNotReady` for empty data. Minor efficiency issue only — individual guards already handle it correctly.
- **Fix**: Could be tightened; low priority given the downstream guards.
- **Linter rule**: not mechanically checkable

### 9. Unnecessary `list()` call in `sorted()` (Ruff C414)
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:629`
- **Evidence**: `sorted(list(integration.units), ...)` — `sorted()` already accepts any iterable.
- **Fix**: Remove the `list()` wrapper.
- **Linter rule**: Ruff C414 (already flagged by tooling)

### 10. Exception names don't use "Error" suffix (Ruff N818)
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:33-57`
- **Evidence**: `MissingConfig`, `InvalidConfig`, `MissingIntegration`, `InvalidIntegration`, `ContainerNotReady`, `IntegrationNotReady`, `PlatformNotReady`; suppressed via `per-file-ignores = ["src/charm.py:N818"]` in `pyproject.toml`.
- **Fix**: Rename, or keep the explicit suppression as-is.
- **Linter rule**: Ruff N818 (suppressed)

### 11. No STREAM connector type support despite docstring claim
- **Severity**: low
- **Kind**: bug (docs/code mismatch)
- **Where**: `lib/charms/opencti/v0/opencti_connector.py:41-47`
- **Evidence**: docstring lists "STREAM" as a valid `connector_type`, but no connector uses it and the base class doesn't handle it.
- **Fix**: Implement STREAM support or remove it from the docstring.
- **Linter rule**: not mechanically checkable

### 12. Ingress library workaround uses a protected method
- **Severity**: low
- **Kind**: bug (fragile)
- **Where**: `src/charm.py:206`
- **Evidence**:
  ```python
  # Sometimes the ingress library doesn't properly handle pod
  # restarts, which can cause the IP field inside the ingress
  # relation data to become stale...
  ingress._publish_auto_data()  # pylint: disable=protected-access
  ```
- **Impact**: Works around a bug in the `traefik_k8s` library by calling a private method; if the library's internals change, this breaks silently. The explanatory comment is good practice but doesn't remove the fragility.
- **Fix**: Contribute a fix upstream to `traefik_k8s` and remove the workaround.
- **Linter rule**: not mechanically checkable

### 13. No actions defined despite docs referencing actions
- **Severity**: low
- **Kind**: docs / ux
- **Where**: `docs/reference/actions.md` (181 bytes, essentially empty); no `actions.yaml` or `actions/` directory in the repo
- **Evidence**: placeholder doc with no corresponding action definitions.
- **Impact**: Operators looking for runnable actions (e.g. restart-workers, get-admin-token, sync-connectors, health-check) will find none.
- **Fix**: Implement actions, or state plainly in the docs that none exist.
- **Linter rule**: not mechanically checkable

### 14. Double assignment `users = users = {...}`
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:783`
- **Evidence**: `users = users = {...}` — redundant, harmless.
- **Fix**: Remove one `users =`.
- **Linter rule**: mechanically checkable — "redundant double assignment"

### 15. Codespell finds "softwares" in vendored GraphQL schema
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/opencti.graphql:5244`
- **Evidence**: `"softwares"` (should be `"software"`); this is a vendored copy of the upstream OpenCTI schema, not charm-authored.
- **Fix**: Upstream fix; already skipped in `tox.ini` codespell config.
- **Linter rule**: codespell

## Worth copying

1. **Clean reconciler pattern with typed exceptions for status** — `src/charm.py:211-226`. `_reconcile` catches specific exception types and maps them to Blocked/Waiting. Testable, avoids string-based status logic.
2. **Generated connector charms from a Jinja2 template** — `scripts/gen_connector_charm.py` + `connector-template/`. Autogenerates 20+ connector charms from upstream README config tables; `extract_template_configs` parses upstream Markdown for config metadata; the `@connector_generator` decorator pattern is elegantly composable.
3. **`StateBuilder` pattern for unit tests** — `tests/unit/state.py`. Fluent API for constructing `ops.testing.State`; `add_required_integrations(excludes=[...])` is especially useful for missing-integration test scenarios.
4. **Peer relation secret caching** — `src/charm.py:413-428`. Caches peer secret content after first retrieval to avoid repeated `secret.get_content(refresh=True)` calls; defensive comment about secret removal during upgrades shows real-world awareness.
5. **Health check via pebble custom notice** — `src/charm.py:183-195`. A bash script running as a pebble service polls the OpenCTI health endpoint and triggers `pebble notify` when healthy, avoiding busy-waiting in charm hooks.
6. **Connector charm scale guard** — `lib/charms/opencti/v0/opencti_connector.py:123-128`. `if self.app.planned_units() != 1` blocks multi-unit connector deployments with a clear, actionable message. Observed live — works as intended.

## Common-practice notes

- Standard layout: `src/charm.py` + `lib/charms/`; each charm's `charmcraft.yaml` declares `assumes: juju >= 3.4`.
- 23 charms in one repo via subdirectories, each with its own `charmcraft.yaml` — standard for charm families.
- `lib/charms/opencti/v0/opencti_connector.py` is properly versioned (LIBAPI=0, LIBPATCH=3) with a unique LIBID; uses `abc.ABC` with abstract properties.
- Vendors well-known community libraries: `data_platform_libs`, `grafana_k8s`, `loki_k8s`, `prometheus_k8s`, `rabbitmq_k8s`, `redis_k8s`, `traefik_k8s`.
- Drift: no `config.yaml` — config lives in `charmcraft.yaml`; valid but less common. The connector library handles both via `_config_metadata()`.
- Drift: Ruff N818 suppressed for exception naming — defensible for brevity but off ecosystem convention.
- Uses `rockcraft.yaml` for OCI images (modern Canonical approach).
- `terraform/charm/` and `terraform/product/` modules with their own tests and READMEs.

## Tests

- **Unit**: 48 tests, all passing via `tox -e unit`. Coverage: 86% for `src/charm.py`, 40% for `src/opencti.py`. Uses the `ops.testing` (Scenario) framework.
- **Integration**: `tests/integration/test_charm.py` has 4 tests deploying the full stack (OpenSearch and RabbitMQ on LXD, plus k8s dependencies); assertions check worker count, user creation, and connector registration — not just `wait_for_idle`. Requires a machine controller and cross-model relations, so not runnable in this review's environment.
- **Coverage gaps**:
  - `_dump_integration` (`src/charm.py:687-716`) — 0% coverage
  - `_cleanup_secrets` (`src/charm.py:192-206`) — not tested
  - `_install_callback_script` (`src/charm.py:278-289`) — exercised but content not verified
  - `_pebble_custom_notice` handler (`src/charm.py:196-200`) — not tested
  - WOAP connector's `_reconcile` override, `stop_connector`, and `_gen_env` — no dedicated tests
  - No test for connector user reactivation (Inactive → Active)
- **No spread tests**: integration tests use `pytest-operator` only.
- **CI**: GitHub Actions for unit/integration (`test.yaml`), Charmhub publishing (`publish_charm.yaml`), channel promotion (`promote_charm.yaml`).
- **Tooling notes**: `ruff check src/ --quiet` reports N818 x7 (suppressed) and C414; `charmcraft analyse .` crashed with `IsADirectoryError` in this monorepo layout; direct `pytest` invocation failed due to a system `pyOpenSSL` version mismatch, but `tox` worked fine.

## Docs

- README: clear and well-structured.
- Tutorial (`docs/tutorial/index.md`): comprehensive ~300-line walkthrough covering full deployment across LXD and k8s, including sysconfig, MinIO setup, and cross-model relations.
- Reference: `docs/reference/charm-architecture.md` has detailed Mermaid diagrams; `docs/reference/integrations.md` has copy-paste errors (Finding 7).
- How-to guides: sparse — `docs/how-to/account.md` is 3 lines, `docs/how-to/backup.md` is two short paragraphs, `docs/how-to/upgrade.md` is 3 lines. Mostly placeholders.
- Charmhub descriptions: connector charms mostly share identical generic descriptions that don't explain what each connector does; `opencti-woap-connector` is the exception with a connector-specific description.
- Terraform module docs: detailed, with usage examples.

## Open questions

1. Does an admin-user secret change trigger a platform restart? `get_content(refresh=True)` ensures new content is read, but the code relies on `container.replan()` detecting changes rather than explicitly stopping/starting the platform.
2. Does the health-check callback race with worker startup? Workers start only after the callback reports the platform healthy, but if the health endpoint returns 200 before full initialization, workers could fail briefly — depends on OpenCTI's own readiness semantics.
3. Is the WOAP connector's OpenSearch integration (using `OpenSearchRequires` with `extra_user_roles="admin"`) verified across models? Secret URI resolution via `get_content(refresh=True)` should work cross-model but wasn't verified.
4. Would the `IsADirectoryError` from `charmcraft analyse` reproduce in a single-charm directory, or is it specific to this monorepo layout?
