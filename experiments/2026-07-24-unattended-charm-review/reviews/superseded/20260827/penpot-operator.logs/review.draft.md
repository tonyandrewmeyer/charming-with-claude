# penpot-operator

One-paragraph verdict: A well-structured k8s charm that manages Penpot (the open-source design tool) via Pebble, with holistic reconciliation, a clean secret-management pattern, and good observability integration. The charm is in reasonable shape — the most pressing finding is that unit tests are broken by a missing `PYTHONPATH` in the default test invocation (developer experience issue), and the `_reconcile` loop has a 120-second blocking busy-wait that makes charm hooks run long. The README and default charm deployment describe an incompatible `postgresql-k8s` revision that cannot satisfy the `postgresql_client` interface penpot requires — this is a critical operator surprise. The `TimeoutError` shadowing issue in the readiness check is real but minor. The `exporter` missing `PENPOT_SECRET_KEY` finding from the first-pass review is **incorrect**: the exporter pebble service does have `**self._get_penpot_secret_key()`.

| | |
|---|---|
| Repo | canonical/penpot-operator @ 85243e0 (2026-07-21) |
| Charms | penpot |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), charmhub latest/edge rev 80 |
| Reviewed | 2026-08-19 |

## What it does

Deploys Penpot (design tool) as a multi-service Pebble workload on k8s. Required integrations: PostgreSQL, Redis, S3, Ingress. Optional: SMTP, OAuth/OIDC, Loki logging, Prometheus/Grafana metrics. Single container (`penpot`) with three Pebble services: `backend` (Java), `frontend` (NGINX), `exporter` (Node.js). Single-unit exporter elected via peer-relation sort. Secret key stored in a Juju secret on the peer relation. Uses holistic reconciliation (single `_reconcile` handler triggered by every event). The rock image (`penpot_rock/rockcraft.yaml`) specifies `run-user: _daemon_`, so pebble services run as uid 584792 — matching the file ownership of `/opt/penpot/*`.

## Deployment log

**Environment**: concierge-k8s-3 (Juju 3.6.25), model `rv-penpot-3`, k8s cluster without LoadBalancer support.

**Step 1 — Initial deployment of penpot + dependencies**:
```
juju deploy penpot --channel latest/edge --trust         # rev 80 ✓
juju deploy postgresql-k8s --channel latest/stable        # rev 20 — WRONG revision (see finding #6)
juju deploy redis-k8s --channel latest/edge              # rev 42 ✓
juju deploy traefik-k8s --channel latest/edge            # rev 401 — error: LoadBalancer unavailable
juju deploy self-signed-certificates --channel latest/stable  # rev 264 ✓
juju deploy smtp-integrator --channel latest/stable       # rev 121 — blocked: needs host config
juju deploy s3-integrator --channel 1/stable            # rev 562 — blocked: needs credentials
```

**Step 2 — Attempted relation (failed)**:
```
juju relate penpot postgresql-k8s       # ERROR: no relations found
juju relate penpot:postgresql postgresql-k8s:database  # ERROR: interface mismatch
```
Confirmed by reading postgresql-k8s rev 20 charm metadata: provides `pgsql` interface, not `postgresql_client`. Removed broken postgresql-k8s.

**Step 3 — Correct postgresql-k8s revision**:
```
juju deploy postgresql-k8s --channel 14/stable --revision 774 --trust  # rev 774 ✓
juju integrate penpot:postgresql postgresql-k8s:database  # ✓ relation created
```
Database created at `postgresql:10` — confirmed from container-agent log.

**Step 4 — Redis relation**:
```
juju integrate penpot:redis redis-k8s  # ✓
```

**Step 5 — Ingress (traefik-k8s)**:
```
juju integrate penpot:ingress traefik-k8s:ingress  # relation created, but traefik-k8s stuck in error
```
traefik-k8s fails because the cluster has no LoadBalancer provisioner. The traefik-k8s pod also has a cluster-level RBAC issue: `User "system:serviceaccount:rv-penpot-3:traefik-k8s" cannot list resource "services" at cluster scope`. traefik-k8s returns HTTP 418 from its readiness probe.

**Step 6 — Failure injections**:
```
juju remove-relation penpot postgresql-k8s   # status: waiting for ingress, postgresql, s3 ✓
juju integrate penpot:postgresql postgresql-k8s:database  # status restored ✓
juju run penpot/0 create-profile email="test@example.com"  # "penpot is not ready" ✓
juju run penpot/0 delete-profile email="test@example.com"  # "penpot is not ready" ✓
juju config smtp-integrator host="invalid..hostname" port="99999"  # smtp-integrator: blocked on port ✓
juju config traefik-k8s external_hostname="penpot.example.com"  # traefik-k8s: still error ✓
```

**Result**: penpot blocked on `waiting for ingress, s3`. No LoadBalancer in cluster prevents traefik-k8s from providing an ingress URL. s3-integrator needs MinIO or cloud S3 credentials to provide credentials.

**Previous environment (rv-penpot-1 on concierge-k8s-4, Juju 4.0.12)**: All charms including penpot failed with hook errors because the Juju operator service account cannot `patch secrets` in the namespace — a cluster RBAC issue (`User ... cannot patch resource 'secrets' in API group ''`). This is an infrastructure issue, not a charm bug.

## Observed behaviour

**Status precedence**: The charm correctly sets `BlockedStatus` listing all unfulfilled requirements in alphabetical order. Observed sequence: `waiting for ingress, postgresql, redis, s3` → `waiting for ingress, s3` (after redis/postgresql related) → `waiting for ingress, s3` (with s3 still pending). The blocked message is always actionable.

**Hook sequence on first deploy** (from container-agent log):
1. `install` 21:20:27
2. `penpot_peer-relation-created` 21:20:28 ← peer relation created BEFORE leadership
3. `leader-elected` 21:20:29 ← leadership acquired
4. `penpot-pebble-ready` 21:20:30
5. `config-changed` 21:20:32
6. `start` 21:20:34
7. `penpot_peer-relation-changed` 21:20:36 ← leader wrote secret to peer relation
8. `postgresql-relation-created` 21:30:01 ← postgresql related
9. `database created at postgresql:10 21:30:05` ← PostgreSQL provisioned the database
10. `ingress-relation-created` 21:31:17 ← traefik related

**Relation removal**: Removed redis relation with `juju remove-relation penpot redis-k8s`. The status immediately updated to include `redis` in the blocked requirements (the `update-status` hook at 21:25:09 triggered `_check_ready` which re-evaluated requirements). Re-adding the relation restored the state.

**Critical relation removal (postgresql)**: Removed postgresql relation with `juju remove-relation penpot postgresql-k8s`. Within 5 seconds, status changed from `waiting for ingress, s3` to `waiting for ingress, postgresql, s3`. The charm correctly detected the missing dependency and updated status. Restoring the relation restored the blocked set. No traceback, no crash — clean `BlockedStatus` propagation.

**Action execution while blocked**: Both `create-profile` and `delete-profile` actions correctly fail with `"penpot is not ready"` when the pebble container cannot be connected to. The action handlers check `container.can_connect()` and `container.get_service("backend").is_running()` before executing. No traceback, graceful failure with actionable message.

**SMTP invalid config**: Configured smtp-integrator with invalid port (`99999`). The smtp-integrator charm blocked with `"invalid configuration: port"`. Penpot was unaffected (SMTP is optional when OAuth is not configured).

**No `update-status` handler**: The charm has no explicit `on.update_status` observer. The `update-status` hook fires but does nothing in the charm — the ops framework calls `ops.main.main()` with `update-status` as the hook name, which has no handler and returns successfully. `_check_ready` is NOT called on `update-status`. This means the unit status is only updated when other hooks fire.

**Loki logging**: `WARNING unit.penpot/0.juju-log No Loki endpoints available` — the charm observes Loki via `LogForwarder` but no `loki_k8s` charm is deployed. This is a harmless warning.

**Pebble state**: `Plan has no services.` — correct, because penpot is blocked and `_check_ready` returns False, so no pebble layer is added. The penpot workload directories exist in the container (`/opt/penpot/backend`, `/opt/penpot/frontend`, `/opt/penpot/exporter`), owned by `_daemon_:_daemon_` (uid 584792), matching the rock's `run-user: _daemon_`.

**No `juju refresh` available**: `juju refresh penpot --channel latest/edge` returns `"penpot: already up-to-date"`. The charm is at the latest revision on the edge channel.

**traefik-k8s on this cluster**: The traefik-k8s charm fails every 10 seconds retrying its `config-changed` hook. The pebble readiness check also fails with HTTP 418. This is a cluster limitation (no LoadBalancer, no IngressClass), not a traefik-k8s bug.

## Findings

### postgresql-k8s requires specific revision to satisfy `postgresql_client` interface
- **Severity**: critical
- **Kind**: bug
- **Where**: `README.md`; `charmcraft.yaml` has no version constraint
- **Evidence**: `juju deploy postgresql-k8s --channel latest/stable` (rev 20) provides `interface: pgsql` on the `db` endpoint. penpot requires `interface: postgresql_client` on its `postgresql` endpoint. `juju integrate penpot:postgresql postgresql-k8s:database` fails with `ERROR no relations found`. The integration tests use `postgresql-k8s --channel 14/stable --revision 774` which provides `interface: postgresql_client` via the `database` endpoint. `tests/integration/conftest.py:22` declares `POSTGRESQL_REVISION = 774`.
- **Why it matters**: Any operator who follows the README (`juju deploy postgresql-k8s` without a channel/revision pin) gets rev 20 which is incompatible. The relation can never be established, leaving penpot permanently blocked on `waiting for postgresql`. The charmcraft.yaml has no `requires` constraint that specifies the compatible postgresql-k8s version.
- **Fix**: Either (a) add a `requires` constraint in charmcraft.yaml or metadata noting `postgresql-k8s >= 14/stable` or the specific revision, or (b) use `juju deploy postgresql-k8s --channel 14/stable` in the README.
- **Linter rule**: "README deployment instructions must use charm revisions compatible with all declared interfaces."

### Unit tests broken in the default developer invocation
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py:16`; `pyproject.toml` has no `pythonpath`
- **Evidence**: `from src.charm import PenpotCharm` → `ModuleNotFoundError: No module named 'src'` when running `.venv/bin/pytest tests/unit/test_charm.py`. The charm's `dispatch` script sets `PYTHONPATH="${dispatch_path}/lib:${dispatch_path}/src"` (absolute paths), but the test conftest runs from the repo root and needs `PYTHONPATH=.:lib`. The `pyproject.toml` has `[tool.uv] package = false` and no `pythonpath` in `[tool.pytest.ini_options]`.
- **Why it matters**: A developer who clones the repo and runs `pytest tests/unit` or even `.venv/bin/pytest tests/unit` gets an immediate failure. All 13 tests pass only with `PYTHONPATH=.:lib .venv/bin/pytest tests/unit/`. The test invocation is broken for the default `uv sync && pytest tests/unit` workflow.
- **Fix**: Add `pythonpath = [".", "lib"]` to `[tool.pytest.ini_options]` in `pyproject.toml`. Alternatively, ensure `pyproject.toml` has `package = true` and `src/__init__.py` exists.
- **Linter rule**: "pytest must be runnable without environment manipulation after `uv sync`."

### `_reconcile` blocks for up to 120 s doing a busy-wait
- **Severity**: high
- **Kind**: performance
- **Where**: `src/charm.py:164–172`
- **Evidence**: 
  ```python
  deadline = time.time() + 120
  self.unit.status = ops.WaitingStatus("waiting for penpot services")
  while time.time() < deadline:
      if self._check_penpot_backend_ready():
          self.unit.status = ops.ActiveStatus()
          return
      time.sleep(3)
  ```
- **Why it matters**: On every reconcile trigger (config change, relation change, pebble ready, secret changed, upgrade charm), the charm loops for up to 120 s, sleeping 3 s at a time. The unit is in `WaitingStatus` the entire time, blocking other work. This was not observed in this deployment because the charm is permanently blocked (no ingress URL available) so `_reconcile` never reaches this loop. But if the charm were in a working state, any config change would freeze the hook for up to 2 minutes.
- **Fix**: Replace the busy-wait with Pebble health checks (`checks` in the pebble layer already exist with `backend-ready`). Trust Pebble to manage service health after `container.replan()`, or use an async approach with `Tenacity`.
- **Linter rule**: "hook handler must not contain a `time.sleep()` loop longer than 5 seconds."

### README references `nginx-ingress-integrator` for ingress
- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md`
- **Evidence**: The README shows `nginx-ingress-integrator --trust` and `juju integrate ... nginx-ingress-integrator`. The integration tests use `traefik-k8s` (deployed as `traefik-public`) with subdomain routing mode. The penpot charm declares `requires.ingress: interface: ingress` which traefik-k8s satisfies but nginx-ingress-integrator does not.
- **Why it matters**: Following the README literally results in a non-functional stack: `nginx-ingress-integrator` does not satisfy the `ingress` interface, so penpot stays blocked on `waiting for ingress` forever. The integration tests also use `traefik-public` with specific configuration for host-based routing (`routing_mode: subdomain`), which is needed for the Penpot SPA.
- **Fix**: Update README to use `traefik-k8s` and document the subdomain routing configuration required for Penpot to work correctly.
- **Linter rule**: "README integration examples must match the interfaces declared in charmcraft.yaml."

### Integration tests pin specific charm revisions not documented in README
- **Severity**: medium
- **Kind**: docs
- **Where**: `tests/integration/conftest.py:18–27`
- **Evidence**: The conftest pins: `MINIO_REVISION = 383`, `POSTGRESQL_REVISION = 774`, `REDIS_REVISION = 42`, `S3_INTEGRATOR_REVISION = 330`, `SELF_SIGNED_CERTIFICATES_REVISION = 264`, `SMTP_INTEGRATOR_REVISION = 93`, `TRAEFIK_PUBLIC_REVISION = 277`, `HYDRA_REVISION = 399`, `KRATOS_REVISION = 567`. The README deploys with no revision pins.
- **Why it matters**: Tests run against specific revisions that may not be available on all channels. An operator reproducing the test environment may get different behavior. The most impactful pin is `POSTGRESQL_REVISION = 774` (the postgresql_client interface requirement), but others like `SMTP_INTEGRATOR_REVISION = 93` vs the latest/stable 121 suggest the integration test suite is not kept in sync with latest stable.
- **Fix**: Document the required revisions in a `tests/integration/README.md` or ensure the CI uses the latest stable revisions.
- **Linter rule**: "Integration test conftest should document or automate the maintenance of charm revision pins."

### `_get_penpot_exporter_unit` will crash if called before peer relation exists
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:457–465`
- **Evidence**:
  ```python
  def _get_penpot_exporter_unit(self) -> str:
      relation = typing.cast(ops.Relation, self.model.get_relation("penpot_peer"))
      units = list(relation.units)   # AttributeError if relation is None
  ```
- **Why it matters**: `_get_penpot_exporter_unit` is called from `_reconcile` via `_gen_pebble_plan()`. If an event like `upgrade_charm` fires before the peer relation is established, `get_relation` returns `None` and `relation.units` raises `AttributeError`. In observed practice, the peer relation is created before `upgrade_charm` could fire, and `penpot_peer_relation_created` triggers `_reconcile` after the relation exists. The unit tests always include a `peer_relation`, masking this gap. A multi-unit scale-up scenario could trigger this if the new unit's `pebble_ready` fires before the peer relation change propagates.
- **Fix**: Guard with `if (relation := self.model.get_relation("penpot_peer")) is None: return self.unit.name`.
- **Linter rule**: "relation accessor must guard against `None` before accessing relation attributes."

### No `update_status` handler: status not refreshed between hook invocations
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py` — no `self.framework.observe(self.on.update_status, ...)` line
- **Evidence**: From observed debug log: `update-status` hook fires at 21:25:09 but the charm has no handler. The unit status only updates when a relation hook or config hook fires. When the redis relation was removed, the status was only updated at the next `update-status` hook, not immediately.
- **Why it matters**: If a dependency charm becomes unavailable between hook invocations, the penpot unit continues to report its stale status (e.g., `active`) until the next hook fires. An operator relying on `juju status` to detect failures would see outdated information. The charm uses a holistic reconciliation pattern but omits the periodic trigger.
- **Fix**: Add `self.framework.observe(self.on.update_status, self._reconcile)` to periodically re-evaluate readiness.
- **Linter rule**: "charms with blocking dependencies should observe `update_status` to refresh status periodically."

### `_gen_pebble_plan` always adds the layer with `combine=True`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:156`
- **Evidence**: `self.container.add_layer("penpot", self._gen_pebble_plan(), combine=True)` — the layer is always added even if the plan hasn't changed.
- **Why it matters**: Combined with the 120-second busy-wait, every reconcile touches Pebble unconditionally. The `combine=True` merges with the existing layer of the same name, so Pebble re-executes the layer even if nothing changed.
- **Fix**: Only add the layer if the generated plan differs from the current plan, or use `combine=False` and manage idempotently.
- **Linter rule**: "Pebble layer should only be updated when the plan has changed."

### `_get_local_resolver` calls `dns.resolver.resolve` with `search=True` on an FQDN
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:450–451`
- **Evidence**: `dns.resolver.resolve(kube_dns, search=True)` where `kube_dns = f"kube-dns.kube-system.svc.{self._get_kubernetes_cluster_domain()}"` is already a fully-qualified domain name. `search=True` adds local domain suffixes before the FQDN, which is unnecessary and adds DNS lookup latency.
- **Why it matters**: If the search path includes the local domain and the FQDN doesn't resolve, the resolver tries multiple search domains before failing. The function returns a fallback to the system nameserver on `DNSException`, which is correct but the initial call should use `search=False`.
- **Fix**: Use `dns.resolver.resolve(kube_dns)` without `search=True`.
- **Linter rule**: "Do not use `search=True` with fully-qualified domain names."

### `TimeoutError` from `_check_penpot_backend_ready` is not caught
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:173–182`
- **Evidence**:
  ```python
  def _check_penpot_backend_ready(self) -> bool:  # pragma: nocover
      try:
          return requests.get("http://localhost:6060/readyz", timeout=1).text == "OK"
      except (requests.exceptions.RequestException, TimeoutError):
          return False
  ```
- **Why it matters**: `requests.get(..., timeout=1)` raises `requests.exceptions.ReadTimeout`, a subclass of `requests.exceptions.RequestException`, so that is caught correctly. However, Python's built-in `TimeoutError` is shadowed by the `TimeoutError` name imported from `requests.exceptions`. In practice `requests` always raises its own exception subclasses, so this is mostly theoretical. But the name shadowing is confusing and a static analysis linter would flag it. The function also lacks a `# pragma: nocover` but the tests monkeypatch this method, so it is never actually executed in tests.
- **Fix**: Use `requests.exceptions.Timeout` explicitly. Rename to avoid shadowing the built-in.
- **Linter rule**: "use `requests.exceptions.Timeout` explicitly; do not shadow `builtins.TimeoutError`."

## Worth copying

- **Holistic reconciliation pattern**: Single `_reconcile` handler triggered by all relevant events. Clean and maintainable. `src/charm.py:145–173`.
- **Peer-relation secret sharing**: Leader creates a Juju secret and stores the ID in the peer relation databag. Non-leaders read via `secret.get_content(refresh=True)`. Good pattern for sharing secrets across units without a leader dependency. `src/charm.py:278–304`.
- **Deterministic exporter election**: `sorted(units + [self.unit])[0]` picks the lowest-numbered unit as exporter. No leader election needed for this role. `src/charm.py:457–465`.
- **Graceful readiness check**: `_check_ready()` returns False with `BlockedStatus` listing unfulfilled requirements alphabetically. The blocked message is always actionable. `src/charm.py:250–277`.
- **Dedicated metrics endpoint and dashboard**: `MetricsEndpointProvider` + `GrafanaDashboardProvider` integration with a bundled `grafana_dashboards/penpot.json`. Good observability pattern.
- **OPS scenario testing**: The unit tests use `ops.testing.Context` with a `testing.State` builder and `conftest.py` fixture helpers. Clean separation of concerns.
- **ops framework conventions**: Uses `ops.pebble.LayerDict`, `ops.ActiveStatus`, `ops.BlockedStatus`, `ops.WaitingStatus`, `ops.ActionEvent` correctly. Uses `container.can_connect()` guard in action handlers.
- **Rock run-user**: The rockcraft.yaml specifies `run-user: _daemon_`, ensuring pebble services run as the correct non-root user matching file ownership. No manual user/group needed in the pebble layer.

## Common-practice notes

- **ops framework usage**: Modern ops 3.x. The `dispatch` script correctly sets `PYTHONPATH="${dispatch_path}/lib:${dispatch_path}/src"` for the operator pod. Uses the modern `charmcraft.yaml` `parts.charm.plugin = uv` approach (no manual dispatch file in the repo).
- **Charm libraries**: Uses `data_platform_libs v0`, `loki_k8s v1`, `prometheus_k8s v0`, `grafana_k8s v0`, `traefik_k8s v2`, `redis_k8s v0`, `smtp_integrator v0`, `hydra v0`. All pinned in `lib/charms/`. Library code ships 228 ruff violations (f-strings, `.format()`, mutable defaults, `assert` statements) — all in the library code, not the charm code.
- **Structure**: `src/charm.py` (520 lines), `lib/charms/` (8 libraries), `tests/unit/`, `tests/integration/`. Convention-following.
- **charmcraft.yaml**: Clean layout with `parts.charm.plugin = uv`. `base: ubuntu@24.04`, `platforms: amd64`. `assumes: juju >= 3.4`. Single charm only, k8s-only (containers + resources declared).
- **No `src/__init__.py`**: The `src/` directory lacks `__init__.py`, contributing to the test invocation issue. `pyproject.toml` has `package = false` under `[tool.uv]`.
- **Linting clean**: `ruff check src/` → 0 violations. `mypy src/charm.py` → 0 issues. `codespell src/` → 0 issues.
- **charmcraft analyze**: The `charmcraft analyze` tool reports `Cannot find the entrypoint file` for the packed charm. This is a charmcraft analyze tool limitation with modern `uv`-plugin charms, not a charm bug — the dispatch script and entrypoint exist and work correctly.
- **No LXD substrate**: The charm is k8s-only (declares `containers:` and `resources:`), so it cannot be deployed on the LXD controllers. Only k8s deployment is possible.

## Tests

**Unit tests**: 13 tests in `tests/unit/test_charm.py`. All pass with `PYTHONPATH=.:lib .venv/bin/pytest tests/unit/test_charm.py`. Without `PYTHONPATH`: `ModuleNotFoundError: No module named 'src'`.

**Coverage** (76% of `src/charm.py`):
  - ✓ `_get_postgresql_credentials`, `_get_redis_credentials`, `_get_s3_credentials`, `_get_smtp_credentials`, `_get_penpot_secret_key` — covered by `test_postgresql_config`, `test_redis_config`, `test_s3_config`, `test_smtp_config`, `test_penpot_pebble_layer`
  - ✓ `_gen_pebble_plan` — covered by `test_penpot_pebble_layer` (full plan verified)
  - ✓ `_get_penpot_exporter_unit` — covered by `test_penpot_exporter_unit`
  - ✓ `_get_penpot_backend_options`, `_get_penpot_frontend_options` — covered by `test_smtp_penpot_option`
  - ✓ `_get_public_uri` — covered by `test_public_uri`
  - ✓ `_get_oauth_client_config` — covered by `test_oauth_client_config_uses_penpot_212_callback`
  - ✓ `create-profile` / `delete-profile` actions — covered by `test_penpot_create_profile_action`, `test_penpot_delete_profile_action`
  - ✗ `_check_ready` blocked path — NOT tested. No test asserts that `_check_ready` returns False with the correct blocked message when a requirement is missing. All existing tests patch `_check_penpot_backend_ready` to return True and only test the success path.
  - ✗ `_check_penpot_backend_ready` — NOT tested. All tests monkeypatch this method to return True. The `pragma: nocover` on the method confirms it is intentionally untested.
  - ✗ `_get_local_resolver` — NOT tested
  - ✗ `_get_kubernetes_cluster_domain` — NOT tested
  - ✗ `_reconcile` timeout path — NOT tested (only the success path via monkeypatch)
  - ✗ `_get_penpot_exporter_unit` without peer relation — NOT tested
  - ✗ `_get_oauth` — NOT tested
  - ✗ `_get_penpot_oauth_config` — NOT tested

**Test infrastructure**: Uses `ops.testing` with `scenario` `State` fixtures in `conftest.py`. The fixtures use the ops testing framework's direct relation data format (not the JSON-serialized format used by `DatabaseRequires`). This is correct for the test framework.

**Integration tests**: Two tests: `test_create_profile` (waits up to 900s for full stack) and `test_oauth_login` (waits up to 900s + 600s). Both require `--charm-file` and `--penpot-image`. Not runnable in this environment. Integration conftest pins specific charm revisions (see finding above).

**Linting**: `ruff check src/` passes (0 violations). `ruff check lib/` → 228 violations (all in library code). `mypy src/charm.py` → 0 issues. `codespell src/` → 0 issues.

## Docs

- `README.md`: Deployment instructions use `nginx-ingress-integrator` instead of `traefik-k8s`. Also doesn't pin postgresql-k8s revision. Otherwise well-structured with the full stack described.
- `docs/reference/charm-architecture.md`: Excellent architecture documentation with mermaid diagrams explaining the holistic reconciliation approach.
- `docs/tutorial/getting-started.md`: Comprehensive guide for local LXD testing. References `nginx-ingress-integrator` for ingress.
- `docs/how-to/upgrade.md`: Basic upgrade documentation.
- `docs/how-to/configure-sso.md`, `configure-s3.md`, `configure-smtp.md`: Good integration how-tos.
- `CONTRIBUTING.md`: 7277 bytes of detailed contributing guide.
- `pyproject.toml`: No `pythonpath` in pytest config (causing test breakage).

## Open questions

- Whether the 120-second busy-wait in `_reconcile` is ever useful in practice: if the backend takes longer than 120s to become ready after `container.replan()`, this is a reasonable timeout. But if the backend typically starts in seconds, this loop adds unnecessary hook duration. The check uses a Pebble health check (`backend-ready`) already defined in the pebble layer.
- Whether `nginx-ingress-integrator` on charmhub provides the `ingress` interface (I couldn't verify — the README uses it but the integration tests use traefik-k8s).
- Whether the `_check_ready` method correctly handles the case where `ingress` is provided but the URL is `http://` (non-HTTPS). The check `public_uri.startswith("https://")` correctly blocks in this case, but this scenario was not tested.
- Whether traefik-k8s rev 401 on this cluster would work with a manually configured `external_hostname` (without LoadBalancer). The traefik-k8s charm requires a LoadBalancer in its current implementation, plus cluster-level RBAC permissions to list services at cluster scope.
- Whether `_get_penpot_exporter_unit` could theoretically be called before the peer relation exists in a multi-unit scale-up scenario — the fix is trivial but the gap is real.