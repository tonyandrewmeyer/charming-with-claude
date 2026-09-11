# nginx-ingress-integrator-operator

A machine charm (workload-less; drives Kubernetes resources via the Python `kubernetes` client) that provisions Nginx Ingress resources for HTTP/HTTPS workloads. It supports the generic `ingress` (traefik IngressPerApp) and nginx-specific `nginx-route` interfaces — only one at a time, enforced in `_check_precondition()` — and optionally consumes `tls-certificates` to provision and rotate TLS certificates. The real logic lives in the vendored `nginx-ingress-integrator` Python package.

**Verdict**: Core reconciliation is clean and well-tested on Juju 3.6 (deploy, scale, refresh, relation join/remove, pod restart all behaved correctly). But the charm is broken in two important ways: TLS certificate provisioning fails permanently on Juju 4.x (RBAC on the secrets API), and the unit test suite fails almost completely on Python 3.12 (`functools.partial` bug in the test fixture, 46/53 tests). There's also a real correctness gap — charm config is never validated when no ingress relation exists, so bad config is silently accepted until a relation shows up. A maintainer should first fix the Juju 4.x TLS failure (it's a hard blocker on newer Juju) and the test-fixture bug (it's blocking any Python-3.12 CI/dev workflow), then land the `remove`-hook cleanup and config-validation fixes.

| | |
|---|---|
| Repo | canonical/nginx-ingress-integrator-operator @ `8f872b9` (2026-07-20) |
| Charms | nginx-ingress-integrator |
| Substrate | Machine (Kubernetes via k8s API) |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), channel latest/edge rev 498; also concierge-k8s-4 (Juju 4.0.12) rev 498 |
| Reviewed | 2026-09-01 |

## What it does

When related via `nginx-route` or `ingress`, the charm creates and manages Kubernetes resources in the consuming app's namespace: an `Ingress`, a `Service`, an `Endpoints`/`EndpointSlice` (for the `ingress` relation), and a TLS `Secret`. It translates charm config (rate limiting, OWASP ModSecurity, proxy timeouts, session affinity, etc.) into Nginx Ingress Controller annotations, and integrates with `tls-certificates` to auto-provision and rotate certificates.

## Deployment log

### Controller: concierge-k8s-3 (Juju 3.6.25)

**Deploy from charmhub edge (rev 498)**: `juju deploy nginx-ingress-integrator --channel edge --trust` → deployed, status `waiting` ("waiting for relation").

**TLS relation**:
```
juju deploy self-signed-certificates --trust
juju integrate nginx-ingress-integrator:certificates self-signed-certificates:certificates
```
→ `certificates-relation-created`, `-joined`, `-changed` all fire cleanly. No secret errors, private key generated.

**Ingress relation with `any-charm` (empty app data)**: `juju integrate any-charm:ingress nginx-ingress-integrator:ingress` → relation established, but `any-charm` sends no app data. Pebble logs from nginx-ingress-integrator/0:
```
INFO juju-log ingress:6: Provider not ready; validation error encountered:
  failed to validate ingress requirer data: failed to validate databag: {}
```
logged at INFO for `-created`, `-joined`, `-changed`. No `data_provided` event emitted. Charm stays `waiting` silently, no `BlockedStatus`. Relation removed afterward; `-departed`/`-broken` fired cleanly, status returned to `waiting`.

**Config validation bypassed with no relation**: with no relation, set `backend-protocol=FAKE` plus static service config (`service-name`, `service-hostname`, `service-port`). Status stayed `waiting`; no juju-log output from the charm during `config-changed` (early return before validation runs).

**Scale to 2 units**: `juju scale-application nginx-ingress-integrator 2` → succeeds; unit 1 immediately goes `blocked`: "this charm only supports a single unit, please remove the additional units using `juju scale-application nginx-ingress-integrator 1`". ✓

**Pod restart**: `kubectl delete pod -n rv-nginx2 nginx-ingress-integrator-0` → new pod starts, `upgrade-charm` → `config-changed` → `start` fire in sequence, TLS relation preserved. ✓ Brief Pebble readiness-probe failure (`non-2xx status code 418`) during `upgrade-charm`, auto-recovers within threshold. ✓

**`get-certificate` without TLS relation**: `juju run nginx-ingress-integrator/0 get-certificate hostname=test.example.com` → "Certificates relation not created." ✓

**`juju refresh` edge→stable→edge** (rev 498 → 203 → 498): both refreshes succeed, `upgrade-charm` → `config-changed` fire, status transitions `maintenance` → `waiting` cleanly each time. ✓

**`juju remove-application`**: succeeds, `stop` and `remove` hooks fire. No orphaned K8s resources — but none existed to clean up (the ingress relation never had valid data). No juju-log output from the charm during `remove`, confirming no custom handler ran.

### Controller: concierge-k8s-4 (Juju 4.0.12)

**Deploy + TLS relation**: same steps as above. TLS relation fails immediately:
```
hook "certificates-relation-created" failed: saving content for secret "14s9i2rotd42s0aoe1b0":
attempt count exceeded: secrets "14s9i2rotd42s0aoe1b0-1" is forbidden:
User "system:serviceaccount:rv-nginx3:juju-secret-consumer-2ec8737d-0b47-41ac-8fac-ddee1cd58dd5"
cannot patch resource "secrets" in API group "" in the namespace "rv-nginx3"
```
Hook retries indefinitely; unit never reaches `idle`. Status misleadingly shows `waiting: waiting for relation` while the agent is actually stuck in an error-recovery loop.

**RBAC check** (both controllers): `kubectl auth can-i patch secrets --namespace=rv-nginx3 --as=system:serviceaccount:rv-nginx3:juju-secret-consumer-...` → `no` on both Juju 3.6 and 4.x. On Juju 3.6 the TLS library falls back to peer relation data; on Juju 4.x it does not.

**`get-certificate` on Juju 4.x**: times out after 60+ seconds — the unit is stuck in the hook retry loop and never responds to actions. ✗

**Scale to 2 units on Juju 4.x**: scale succeeds, but unit 1 gets stuck in `maintenance: installing charm software` because it hits the same TLS hook failure. Pod stays `0/1 Ready`. ✗

**Pebble readiness probe** (unit 1 logs):
```
Check "readiness" failure 1/3: non-2xx status code 418
Check "readiness" threshold 3 hit, triggering action and recovering
```
Returns 418 because the Juju agent's readiness endpoint reports the charm's error state; the pod never becomes `Ready`. ✗

## Observed behaviour

| Aspect | Juju 3.6 | Juju 4.0.12 |
|---|---|---|
| Deploy time (agent install) | ~45 seconds | ~45 seconds |
| Workload version | 24.2.0 | 24.2.0 |
| TLS relation | ✓ works, hooks clean | ✗ hook fails, infinite retry |
| `certificates-relation-created` hook | ✓ succeeds | ✗ fails with RBAC error |
| `get-certificate` without TLS | "Certificates relation not created." | "Certificates relation not created." |
| `get-certificate` with TLS relation | ✓ returns cert | ✗ times out |
| TLS relation removal | `-departed` + `-broken`, clean | N/A (relation never established) |
| Pod restart | `upgrade-charm` → `config-changed` → `start` | N/A (pod stuck in TLS hook) |
| Scale to 2 | Scale succeeds; unit 1 `blocked` immediately | Scale succeeds; unit 1 stuck in `maintenance` |
| Pebble readiness during upgrade | Brief 418, auto-recovers | N/A (unit in error state) |
| `juju-secret-consumer` can patch secrets | ✗ no | ✗ no |
| `DeprecationWarning` in Pebble logs (`JujuVersion.from_environ()`) | ✓ yes | ✓ yes |
| Hook sequence on install | `install`, `nginx-peers-created`, `leader-elected`, `config-changed`, `start` | same |
| TLS storage mechanism | peer relation data (works) | Juju secrets (fails) |
| `juju refresh` edge→stable→edge | ✓ clean | N/A |
| `juju remove-application` | ✓ succeeds | N/A |
| Config validation without relation | ✗ silently accepted | N/A |
| Ingress relation with empty data | `waiting`, no `BlockedStatus` | N/A |

## Findings

### TLS certificates broken on Juju 4.x
- **Severity**: critical
- **Kind**: bug
- **Where**: interaction of `TLSCertificatesRequiresV4` (`deps/charmlibs/interfaces/tls_certificates/_tls_certificates.py:1878`) with `src/charm.py:448` (`_has_secrets()`)
- **Evidence**: On Juju 4.0.12 the `certificates-relation-created` hook fails and retries indefinitely: `hook "certificates-relation-created" failed: saving content for secret "...": attempt count exceeded: secrets "...-1" is forbidden: User "system:serviceaccount:rv-nginx3:juju-secret-consumer-..." cannot patch resource "secrets"`. On Juju 3.6.25 the same relation completes cleanly. `kubectl auth can-i patch secrets --as=system:serviceaccount:...:juju-secret-consumer-...` returns `no` on both controllers. The TLS library checks `self.model.juju_version.has_secrets` (`True` for both Juju versions ≥3.0.3) and always attempts the secrets API; Juju 3.6 transparently redirects to peer relations, Juju 4.x does not.
- **Impact**: TLS integration is completely broken on Juju 4.x. The unit shows `waiting: waiting for relation` while actually stuck in an error loop; Pebble readiness returns 418, so the pod is never `Ready`.
- **Fix**: Add error handling around TLS library operations — either fall back to peer-relation data, catch the `ApiException` and set an actionable `BlockedStatus`, or confirm/fix `juju-secret-consumer` RBAC permissions at the cluster level.
- **Linter rule**: not mechanically checkable without cluster-level RBAC verification.

### Config validation bypassed when no ingress relation exists
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:265-270` (`_update_ingress()`); root cause in `_get_nginx_relation()` at `src/charm.py:134-148`
- **Evidence**: `relation.data[relation.app]` is an empty `{}` when the ingress requirer sends no data — an empty dict is falsy, so `_get_nginx_relation()` returns `None` even though the relation exists. With `backend-protocol=FAKE` and static service config set and no relation, status stayed `waiting`; `_update_ingress()` calls `_cleanup()` and returns before `_get_definition_from_relation()` is ever called, so `InvalidIngressError` validation (`src/ingress_definition.py:217`) is never reached. No juju-log output confirms the early return.
- **Impact**: An operator setting invalid config (e.g. `backend-protocol=FAKE`) with no relation gets no `BlockedStatus` warning. When a relation is later created, the charm jumps straight from `waiting` to `blocked` with no clear indication the pre-existing config was the cause.
- **Fix**: Validate config before the relation check, e.g. in `_check_precondition()`:
  ```python
  def _check_precondition(self) -> None:
      _ = IngressDefinitionEssence(model=self.model, config=self.config, relation=None)
      # ... rest of precondition checks
  ```
- **Linter rule**: not mechanically checkable — requires data-flow analysis of which paths validate config.

### Unit tests fail on Python 3.12+
- **Severity**: critical
- **Kind**: bug
- **Where**: `tests/unit/conftest.py:260-290` (`k8s_stub` fixture)
- **Evidence**: `PYTHONPATH=src:lib uv run python -m pytest tests/unit/` on Python 3.12.3 → **46 failed, 7 passed**. `functools.partial` assigned to a class attribute becomes a bound method in Python 3.12+, so it passes the instance as the first positional argument: `TypeError: Stub.list_namespaced_resource() got multiple values for argument 'namespace'`. Passing tests: `test_get_certificate_action`, `test_get_certificate_action_cert_not_available`, `test_get_certificate_action_no_tls_relation`, `test_given_when_certificate_available_then_ingress_updated` (all mock out the k8s API), plus `test_backend_protocol_error`, `test_follower` (own monkeypatch), `test_two_relation`.
- **Impact**: The test suite cannot run on Python 3.12+, the default on this machine — 87% of tests fail. CI presumably pins an older/uv-managed Python.
- **Fix**: Replace `functools.partial` in the fixture with `lambda`:
  ```python
  monkeypatch.setattr(
      "kubernetes.client.CoreV1Api.list_namespaced_endpoints",
      lambda namespace, label_selector='': stub.list_namespaced_resource("endpoints", namespace, label_selector),
  )
  ```
- **Linter rule**: not mechanically checkable; needs a Python-version compatibility test.

### `get-certificate` action hangs indefinitely on Juju 4.x
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:430-444` (`_on_get_certificate_action`), triggered by the TLS hook failure at `src/charm.py:448`
- **Evidence**: `juju run nginx-ingress-integrator/0 get-certificate hostname=test.example.com` times out after 60+ seconds on Juju 4.0.12 because the unit is stuck in the `certificates-relation-created` retry loop and never processes the action. On Juju 3.6 the same action correctly returns "Certificates relation not created." when there's no TLS relation.
- **Impact**: Any action targeting the unit hangs forever once the TLS hook fails.
- **Fix**: Same as the TLS finding above — the action can't be fixed independently of the hook failure.
- **Linter rule**: not mechanically checkable.

### Pebble readiness probe fails permanently when TLS hook errors on Juju 4.x
- **Severity**: high
- **Kind**: bug
- **Where**: Juju agent / Pebble layer, triggered by the hook failure in `src/charm.py`
- **Evidence**: unit 1 pod on Juju 4.x (rv-nginx3) stays `0/1 Running`; logs show `Check "readiness" failure 1/3: non-2xx status code 418` repeating without recovery. On Juju 3.6 the same 418 appears briefly during `upgrade-charm` and auto-recovers within the 3-attempt threshold; on Juju 4.x the unit is permanently in error state so the probe never clears.
- **Impact**: Kubernetes sees the pod as never ready — PodDisruptionBudgets/affinity rules keyed on readiness will misbehave.
- **Fix**: Fix the underlying TLS hook failure so the charm doesn't enter a persistent error state.
- **Linter rule**: not mechanically checkable.

### `remove` hook has no custom handler — `_cleanup()` never called
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py` — no `_on_remove` handler registered
- **Evidence**: `grep "on.remove\|observe.*remove" src/charm.py` returns nothing. `_cleanup()` (`src/charm.py:253-259`) is only called from `_update_ingress()` when `relation is None`, never wired to the `remove` hook. `juju remove-application` runs `stop` then `remove` with no juju-log output from the charm during `remove`, confirming no handler ran. Tested with no K8s resources present (relation had empty data), so orphaning itself was not directly observed — but the code path is unambiguous.
- **Impact**: If K8s resources (Ingress, Service, Endpoints, TLS Secret) exist, they'd be orphaned on `juju remove-application`, with the `nginx-ingress-integrator.charm.juju.is/managed-by` label lingering indefinitely.
- **Fix**:
  ```python
  self.framework.observe(self.on.remove, self._on_remove)

  def _on_remove(self, _: Any) -> None:
      self._cleanup()
  ```
- **Linter rule**: `no-dead-hooks` — flag charms with no handler for a hook defined in `metadata.yaml`.

### `IngressPerAppProvider` silently ignores invalid ingress relation data
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/traefik_k8s/v2/ingress.py:512-525` (`_handle_relation`)
- **Evidence**: relating `any-charm:ingress` with empty app data produces, at INFO level:
  ```
  INFO juju-log ingress:6: Provider not ready; validation error encountered:
    failed to validate ingress requirer data: failed to validate databag: {}
  ```
  on `-created`, `-joined`, and `-changed`. `_handle_relation()` returns early, no `data_provided` event fires. Charm stays `WaitingStatus("waiting for relation")` even though a relation exists with invalid data.
- **Impact**: A requirer bug produces no diagnosable signal on either side — both charms sit stuck with a misleading "waiting for relation" message.
- **Fix**: Log at WARNING or emit a `data_invalid` event when `is_ready()` is `False`.
- **Linter rule**: not mechanically checkable.

### `JujuVersion.from_environ()` is deprecated
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:448`
- **Evidence**: `return JujuVersion.from_environ().has_secrets` — deprecated since ops 3.x, producing a `DeprecationWarning` in Pebble logs on every call. On Juju 4.x this is the code path that drives the TLS library into using the (broken) secrets API.
- **Impact**: Will error out on a future ops release; contributes to the root cause of the Juju 4.x TLS failure.
- **Fix**: Replace with `self.model.juju_version.has_secrets`. Note: this alone does not fix the RBAC issue — the TLS library uses the same property internally and it evaluates `True` on Juju 4.x regardless.
- **Linter rule**: `no-deprecated-ops` rule could flag `JujuVersion.from_environ`.

### `ingress_class` lookup silently continues without setting a class when multiple defaults exist
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/controller/ingress.py:76-92`
- **Evidence**: when multiple ingress classes carry the `is-default-class` annotation, the charm logs a warning and returns without setting `ingress_class_name`; the Ingress is created with no class, which Kubernetes may route arbitrarily. No `BlockedStatus` set.
- **Impact**: In a multi-ingress-controller cluster, the Ingress can be silently mis-routed or ignored while status still shows `WaitingStatus("Waiting for ingress IP availability")`.
- **Fix**: Raise `InvalidIngressError` directing the user to set `ingress-class` explicitly.
- **Linter rule**: not mechanically checkable.

### `IngressPerAppProvider.wipe_ingress_data` uses `assert` and has a useless expression
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/traefik_k8s/v2/ingress.py:534-536`
- **Evidence**:
  ```python
  assert self.unit.is_leader(), "only leaders can do this"  # S101 / B101
  try:
      relation.data  # B018 — useless expression
  except ModelError as e:
  ```
  `assert` crashes the charm if called on a non-leader unit; `relation.data` result is discarded (the next line does `del relation.data[self.app]["ingress"]`).
- **Impact**: assert failures crash the charm instead of setting a status; the dead expression is a no-op.
- **Fix**: replace the assert with an if-guard that sets an appropriate status, and drop the useless expression.
- **Linter rule**: `ruff check lib/` flags S101 and B018; `bandit -r lib/` flags B101.

### `_IPAEvent` mutable class attribute causes shared state
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/traefik_k8s/v2/ingress.py:416`
- **Evidence**: `__optional_kwargs__: Dict[str, Any] = {}` is a mutable class attribute shared across all instances and subclasses.
- **Impact**: setting kwargs on one event instance can leak into other instances/subclasses.
- **Fix**: initialize `__optional_kwargs__` as an instance attribute in `__init__`.
- **Linter rule**: `ruff check lib/` flags RUF012.

### `proxy-connect-timeout` default mismatch between code and `charmcraft.yaml`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/ingress_definition.py:318` vs `charmcraft.yaml:142`
- **Evidence**: Python fallback default is `5`; `charmcraft.yaml` documents `default: 60`.
- **Impact**: a user reading `charmcraft.yaml` gets the wrong default value.
- **Fix**: change the Python fallback to `60`.
- **Linter rule**: not mechanically checkable without comparing schema against code.

### `SecretController.cleanup_resources` has an incompatible type signature
- **Severity**: low
- **Kind**: bug
- **Where**: `src/controller/secret.py:107` (`exclude: Union[list, None]`) vs `src/controller/resource.py:163` (`exclude: Optional[AnyResource]`)
- **Evidence**: the override expects a list; the base class expects a single item; `# type: ignore[override]` suppresses mypy. If ever called with a single item (matching the base signature), `for exclude_item in exclude` would iterate over the item's attributes instead of matching it, deleting all secrets. Current call site (`src/charm.py:249`) passes a list, so the bug doesn't currently manifest.
- **Impact**: latent — silently wrong behaviour (delete-all) if the method is ever called with a single item as the base class signature implies it should accept.
- **Fix**: make the base class accept `Optional[List[AnyResource]]`, or make the override accept `Optional[Union[AnyResource, List[AnyResource]]]`.
- **Linter rule**: `OVERRIDE` — currently suppressed by `# type: ignore[override]`.

### `IngressPerAppProvider` validates port/host with `assert`
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/traefik_k8s/v2/ingress.py:314-315` (`validate_port`), `:333` (`validate_host`)
- **Evidence**:
  ```python
  assert isinstance(port, int), type(port)
  assert 0 < port < 65535, "port out of TCP range"
  assert isinstance(host, str), type(host)
  ```
- **Impact**: under `python -O` these become no-ops; otherwise they crash with a non-descriptive `AssertionError` rather than a `TypeError`/`ValueError`.
- **Fix**: replace with explicit `if` checks raising proper exceptions.
- **Linter rule**: `ruff check lib/` (S101) and `bandit -r lib/` (B101).

### `SecretController.define_resource` override bypasses the base class
- **Severity**: low
- **Kind**: bug
- **Where**: `src/controller/secret.py:74-103`
- **Evidence**: duplicates the entire `ResourceController.define_resource` body; the only difference is an extra `key` parameter.
- **Impact**: base-class fixes (retry logic, logging, validation) silently don't propagate to secret handling.
- **Fix**: refactor to call `super()` and pass `key` through a helper.
- **Linter rule**: not mechanically checkable without a rule flagging `define_resource` overrides that skip `super()`.

### Third-party `traefik_k8s` library ships with 18 lint issues
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/traefik_k8s/v2/ingress.py`
- **Evidence**: `uv run ruff check lib/` → 18 issues: RUF012 (mutable class attr, real bug, see above), S101 ×4 (asserts, see above), B018 (useless expression, real bug, see above), plus UP032 ×4, UP031 ×3, UP034 ×2, UP037 ×1, RUF100 ×2 (style, auto-fixable). `uv run bandit -r lib/` → 4 HIGH-confidence LOW-severity B101 findings at the same assert locations (lines 314, 315, 333, 534).
- **Fix**: `ruff check lib/ --fix` for the safe/style fixes; fix RUF012, S101, B018, B101 manually (tracked individually above).
- **Linter rule**: `ruff check lib/ && bandit -r lib/` — mechanically checkable.

## Worth copying

- **Clean event-driven reconciliation, no `StoredState`/`defer()`**: every handler (`_on_config_changed`, `_on_start`, `_on_data_provided`, `_on_data_removed`, `_on_nginx_route_available`, `_on_certificate_available`, `_on_nginx_route_broken`) funnels into a single `_update_ingress()`. (`src/charm.py`)
- **`_map_k8s_auth_exception` decorator**: k8s API calls are wrapped to map `ApiException(status=403)` into an `InvalidIngressError` with an actionable `juju trust ...` message. (`src/controller/resource.py:19-54`)
- **`IngressDefinitionEssence` / `IngressDefinition` split**: cleanly separates live config+relation-data derivation (essence, side-effecting) from immutable validated config (frozen dataclass). (`src/ingress_definition.py`)
- **Explicit status precedence**: `_update_ingress()` sets `BlockedStatus` on `InvalidIngressError`, `WaitingStatus` for "waiting for relation"/"waiting for ingress IP", `ActiveStatus` on success. (`src/charm.py:265-291`)
- **Comprehensive K8s test stub**: `tests/unit/conftest.py:K8sStub` records all create/patch/list/delete calls and supports `legacy_mode` for API-version fallback testing (currently broken on Python 3.12+, see Findings).
- **`RelationFixture` test helper**: clean `update_app_data`/`update_unit_data`/`remove_relation` API for readable test code. (`tests/unit/conftest.py:220-300`)
- **Single-relation enforcement**: `_check_precondition()` prevents both `nginx-route` and `ingress` being related simultaneously. (`src/charm.py:195-215`)

## Common-practice notes

| Aspect | Status |
|---|---|
| `src/` layout with `__init__.py` | ✓ follows convention |
| Library versioning (`lib/charms/<charm>/v0/`) | ✓ v0 for both nginx_route and ingress libraries |
| `ops.CharmBase` with `main()` call | ✓ standard |
| `charmcraft.yaml` with `type: charm` | ✓ modern format |
| `pyproject.toml` + `uv` build | ✓ uv-based build with parts |
| `ops >= 3.0` | ✓ uses ops 3.8.0 |
| Pydantic v2 | ✓ uses pydantic 2.13.4 |
| TLS certificates via charmlibs-interfaces | ✓ uses `charmlibs-interfaces-tls-certificates==1.10.0` |
| `assumes: k8s-api` | ✓ in charmcraft.yaml |
| No Pebble containers | ✓ workload-less, no containers in metadata |
| Maintenance mode notice in README | ✓ prominent notice at top |
| `ruff check src/` | ✓ passes |
| `mypy src/` | ✓ passes |
| `codespell src/ lib/` | ✓ passes |
| `ruff check lib/` | ✗ 18 issues in vendored traefik_k8s library |
| `bandit -r lib/` | ✗ 4 B101 issues in vendored traefik_k8s library |
| `bandit -r src/` | ✓ no issues |
| `ruff format --check src/ lib/` | ✓ all files formatted |
| `DeprecationWarning` for `JujuVersion.from_environ()` | ✗ visible in Pebble logs |
| Juju 4.x support | ✗ TLS broken, actions hang |
| CI Juju versions | Only 2.9 and 3.6; no 4.x |
| `remove` hook handler | ✗ missing — `_cleanup()` never called |
| Config validation without relation | ✗ silently skipped |
| Single relation enforcement | ✓ `_check_precondition()` prevents both simultaneously |
| `juju refresh` edge→stable→edge | ✓ clean, hooks fire correctly on Juju 3.6 |

## Tests

**Unit tests**: 53 tests in `tests/unit/`. On Python 3.12.3: **46 failed, 7 passed**. All failures trace to `functools.partial` assigned to a class attribute becoming a bound method in Python 3.12+ — `EndpointsController` creates a fresh `CoreV1Api()` and calls `list_namespaced_endpoints(namespace=..., label_selector=...)`, and the bound method passes the instance as an extra positional `namespace` argument, raising `TypeError`. Passing tests: `test_get_certificate_action`, `test_get_certificate_action_cert_not_available`, `test_get_certificate_action_no_tls_relation`, `test_given_when_certificate_available_then_ingress_updated` (all mock out the k8s API entirely), `test_backend_protocol_error` (no k8s API needed), `test_follower` (own monkeypatch), `test_two_relation` (no k8s API needed).

**Coverage** (`fail_under = 88`): untested gaps include the `get_ingress_ips()` 100-second polling path (`src/controller/ingress.py:272-289`, stub returns an IP immediately), `SecretController.cleanup_resources` with a single-item exclude, the `ingress_class` multi-default branch, `remove`-hook resource cleanup, the `_has_secrets()` behaviour difference between Juju 3.x/4.x (cert tests mock the TLS library out entirely), and invalid config with no relation (validation path is never exercised without a relation).

**Integration tests**: 3 modules (`test_cert_relation`, `test_ingress_relation`, `test_nginx_route`) using `jubilant` with `src-overwrite` to inject the `nginx_route` library into `any-charm`. Tests assert real behaviour, not just `active/idle`: `test_given_charms_deployed_when_relate_then_status_is_active`, `test_given_charms_deployed_when_relate_then_requirer_received_certs` (calls `get-certificate`), `test_ingress_connectivity` (real HTTP through the ingress), `test_ingress_connectivity_invalid_backend` (asserts `blocked` with correct message), `test_missing_field` (asserts `blocked` with "Missing fields for nginx-route: service-name").

**CI**: `test.yaml` uses `canonical/operator-workflows/.github/workflows/test.yaml@main`. `integration_test.yaml` runs against Juju 3.6 (`channel: 1.34-strict/stable`) and Juju 2.9 (`channel: 1.24/stable`) — **no Juju 4.x**. The `integration-juju2` tox env uses `jubilant-backports` for Juju 2 compatibility.

## Docs

- **README.md**: good overview, links to `docs/`, prominent maintenance-mode notice, clearly lists the three interfaces.
- **docs/**: Diátaxis-structured (how-to, tutorial, explanation, reference). Tutorial (`docs/tutorial/tutorial.md`) is detailed (~8KB).
- **terraform/**: a terraform module exists with its own README, tests, and CI workflow.
- **Charmhub**: description matches README; public at `nginx-ingress-integrator` (stable rev 203, edge rev 498).
- **Docs vs. reality**: `charmcraft.yaml`'s `proxy-connect-timeout` default (60) doesn't match the code default (5) — see Findings. The README correctly documents the single-relation limitation.

## Open questions

1. Does the Juju 4.x secrets failure affect every charm in this cluster, or is it specific to this one? Both `nginx-ingress-integrator` and `self-signed-certificates` hit the same `juju-secret-consumer cannot patch secrets` error — may be a cluster-level RBAC misconfiguration rather than a charm bug per se.
2. Why does Juju 3.6 succeed without secret-patch permissions? Peer relation data was not visible in `juju show-unit` output, so the fallback path is opaque from the outside; the 3.6 controller apparently intercepts secrets API calls transparently.
3. Would `juju trust --scope=cluster` fix the Juju 4.x issue? No — it grants the workload pod's SA broader permissions but does not grant `patch` to the Juju-managed `juju-secret-consumer` SA, whose permissions are controlled by Juju itself.
4. Would fixing `JujuVersion.from_environ()` alone fix Juju 4.x? No — the TLS library independently checks `self.model.juju_version.has_secrets`, which is `True` on Juju 4.x regardless; the RBAC constraint is the actual blocker.
5. Is Juju 4.x incompatibility a real blocker given the charm is in maintenance mode (per README, as of Jan 2026) with no new features planned? If Juju 4.x support is ever required, the TLS failure must be fixed — either by graceful degradation in the charm or by fixing cluster RBAC.
6. Is the `remove`-hook orphaning risk real in production? In this deployment no K8s resources existed to orphan (the ingress relation never had valid data), so the failure mode itself wasn't directly observed — but the code path (`_cleanup()` unreachable from `remove`) is unambiguous, and in a deployment with a real relation, resources would be left behind.
</content>
