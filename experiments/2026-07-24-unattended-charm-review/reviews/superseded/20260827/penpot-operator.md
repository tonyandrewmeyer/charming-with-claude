# penpot-operator

**Verdict**: A well-structured k8s charm that runs Penpot (design tool) as a multi-service Pebble workload, with a clean holistic-reconciliation pattern, good secret handling, and solid observability integration. The charm itself never reached a working state in this review's environment, but that was driven mostly by environment/cluster limitations (no LoadBalancer, S3 credentials unavailable) and by one real charm/docs bug: the README's default `postgresql-k8s` deploy command pulls a revision that cannot satisfy the `postgresql_client` interface penpot requires, which permanently blocks the integration for anyone following the docs. A maintainer should fix the postgresql-k8s revision guidance first, then fix the broken default `pytest` invocation (missing `PYTHONPATH`) and the 120-second busy-wait in `_reconcile`.

| | |
|---|---|
| Repo | canonical/penpot-operator @ `85243e0` (2026-07-21) |
| Charms | penpot |
| Substrate | k8s |
| Deployed | no — penpot was installed and related to postgresql/redis but never reached `active`; it stayed `blocked` on `waiting for ingress, s3` because the cluster had no LoadBalancer for traefik-k8s and no S3 credentials were available (see Deployment log) |
| Reviewed | 2026-08-19 |

## What it does

Deploys Penpot as a multi-service Pebble workload on k8s. Required integrations: PostgreSQL, Redis, S3, Ingress. Optional: SMTP, OAuth/OIDC, Loki logging, Prometheus/Grafana metrics. Single container (`penpot`) with three Pebble services: `backend` (Java), `frontend` (NGINX), `exporter` (Node.js). Single-unit exporter elected via peer-relation sort. Secret key stored in a Juju secret on the peer relation. Uses holistic reconciliation (single `_reconcile` handler triggered by every event). The rock image (`penpot_rock/rockcraft.yaml`) specifies `run-user: _daemon_`, so Pebble services run as uid 584792, matching the file ownership of `/opt/penpot/*`.

## Deployment log

**Environment**: concierge-k8s-3 (Juju 3.6.25), model `rv-penpot-3`, k8s cluster without LoadBalancer support.

**Step 1 — Initial deployment of penpot + dependencies**:
```
juju deploy penpot --channel latest/edge --trust             # rev 80 ✓
juju deploy postgresql-k8s --channel latest/stable            # rev 20 — wrong revision (see finding below)
juju deploy redis-k8s --channel latest/edge                  # rev 42 ✓
juju deploy traefik-k8s --channel latest/edge                # rev 401 — error: LoadBalancer unavailable
juju deploy self-signed-certificates --channel latest/stable  # rev 264 ✓
juju deploy smtp-integrator --channel latest/stable           # rev 121 — blocked: needs host config
juju deploy s3-integrator --channel 1/stable                 # rev 562 — blocked: needs credentials
```

**Step 2 — Attempted relation (failed)**:
```
juju relate penpot postgresql-k8s                       # ERROR: no relations found
juju relate penpot:postgresql postgresql-k8s:database    # ERROR: interface mismatch
```
Confirmed by reading `postgresql-k8s` rev 20 charm metadata (`/var/lib/juju/agents/unit-postgresql-k8s-0/charm/metadata.yaml`): it provides `db`/`db-admin` with interface `pgsql`, not `postgresql_client`. Removed the broken postgresql-k8s deployment.

**Step 3 — Correct postgresql-k8s revision**:
```
juju deploy postgresql-k8s --channel 14/stable --revision 774 --trust   # rev 774 ✓
juju integrate penpot:postgresql postgresql-k8s:database                 # ✓ relation created
```
Database created at `postgresql:10`, confirmed from the container-agent log.

**Step 4 — Redis relation**:
```
juju integrate penpot:redis redis-k8s   # ✓
```

**Step 5 — Ingress (traefik-k8s)**:
```
juju integrate penpot:ingress traefik-k8s:ingress   # relation created, but traefik-k8s stuck in error
```
traefik-k8s failed because the cluster has no LoadBalancer provisioner, plus a cluster-level RBAC issue: `User "system:serviceaccount:rv-penpot-3:traefik-k8s" cannot list resource "services" at cluster scope`. Its Pebble readiness probe returned HTTP 418.

**Step 6 — Failure injections**:
```
juju remove-relation penpot postgresql-k8s                                    # status: waiting for ingress, postgresql, s3 ✓
juju integrate penpot:postgresql postgresql-k8s:database                      # status restored ✓
juju run penpot/0 create-profile email="test@example.com"                     # "penpot is not ready" ✓
juju run penpot/0 delete-profile email="test@example.com"                     # "penpot is not ready" ✓
juju config smtp-integrator host="invalid..hostname" port="99999"             # smtp-integrator: blocked on port ✓
juju config traefik-k8s external_hostname="penpot.example.com"                # traefik-k8s: still error ✓
```

**Result**: penpot never left `blocked` (`waiting for ingress, s3`). No LoadBalancer in the cluster prevents traefik-k8s from providing an ingress URL; s3-integrator needs MinIO or cloud S3 credentials that were not available in this environment. Neither is a charm bug.

**Previous environment (rv-penpot-1 on concierge-k8s-4, Juju 4.0.12)**: all charms, including penpot, failed with hook errors because the Juju operator service account could not `patch secrets` in the namespace — a cluster RBAC issue (`User ... cannot patch resource "secrets" in API group ''`), not a charm bug.

## Observed behaviour

**Status precedence**: `BlockedStatus` lists unfulfilled requirements in alphabetical order and stayed actionable throughout: `waiting for ingress, postgresql, redis, s3` → `waiting for ingress, s3` (after redis/postgresql related).

**Hook sequence on first deploy** (from container-agent log):
1. `install` 21:20:27
2. `penpot_peer-relation-created` 21:20:28 — peer relation created before leadership
3. `leader-elected` 21:20:29
4. `penpot-pebble-ready` 21:20:30
5. `config-changed` 21:20:32
6. `start` 21:20:34
7. `penpot_peer-relation-changed` 21:20:36 — leader wrote secret to peer relation
8. `postgresql-relation-created` 21:30:01
9. `database created at postgresql:10` 21:30:05
10. `ingress-relation-created` 21:31:17

**Relation removal (redis)**: `juju remove-relation penpot redis-k8s` — status updated to include `redis` in the blocked requirements at the next `update-status` hook (21:25:09), which re-ran `_check_ready`. Re-adding the relation restored the prior state.

**Critical relation removal (postgresql)**: `juju remove-relation penpot postgresql-k8s` — status changed from `waiting for ingress, s3` to `waiting for ingress, postgresql, s3` within 5 seconds. No traceback, clean `BlockedStatus` propagation. Restoring the relation restored the blocked set.

**Action execution while blocked**: `create-profile` and `delete-profile` both correctly fail with `"penpot is not ready"` when the Pebble container cannot be connected to — the handlers guard on `container.can_connect()` and `container.get_service("backend").is_running()` before executing. Graceful, no traceback.

**SMTP invalid config**: `smtp-integrator` configured with an invalid port (`99999`) blocked with `"invalid configuration: port"`. Penpot was unaffected, since SMTP is optional when OAuth is not configured.

**No `update-status` handler**: the charm has no `self.on.update_status` observer. The hook fires but does nothing — `_check_ready` is not re-evaluated on `update-status`. Unit status is therefore only refreshed when some other hook fires.

**Loki logging**: `WARNING unit.penpot/0.juju-log No Loki endpoints available` — expected, since no `loki_k8s` charm was deployed. Harmless.

**Pebble state**: `Plan has no services.` — correct, since penpot is blocked and `_check_ready` returns `False`, so no Pebble layer is added. Workload directories exist in the container (`/opt/penpot/backend`, `/opt/penpot/frontend`, `/opt/penpot/exporter`), owned by `_daemon_:_daemon_` (uid 584792), matching the rock's `run-user: _daemon_`.

**No `juju refresh` available**: `juju refresh penpot --channel latest/edge` returned `"penpot: already up-to-date"` — the charm was already at the latest edge revision.

**traefik-k8s on this cluster**: retried `config-changed` every 10 seconds, and its Pebble readiness check failed with HTTP 418 — a cluster limitation (no LoadBalancer, no IngressClass), not a traefik-k8s bug.

## Findings

### `postgresql-k8s` default revision cannot satisfy penpot's `postgresql_client` requirement
- **Severity**: critical
- **Kind**: bug / docs
- **Where**: `README.md`; `charmcraft.yaml` has no version constraint on `postgresql-k8s`
- **Evidence**: `juju deploy postgresql-k8s --channel latest/stable` installs rev 20, which provides `interface: pgsql` on its `db` endpoint. penpot requires `interface: postgresql_client` on its `postgresql` endpoint. `juju integrate penpot:postgresql postgresql-k8s:database` fails with `ERROR no relations found`. The integration tests instead use `postgresql-k8s --channel 14/stable --revision 774`, which provides `postgresql_client` via the `database` endpoint (`tests/integration/conftest.py:22`, `POSTGRESQL_REVISION = 774`).
- **Impact**: Any operator following the README's `juju deploy postgresql-k8s` verbatim gets an incompatible revision. The relation can never be established, leaving penpot permanently blocked on `waiting for postgresql`.
- **Fix**: Either add a `requires` constraint noting the compatible `postgresql-k8s` channel/revision, or update the README to use `juju deploy postgresql-k8s --channel 14/stable`.
- **Linter rule**: README deployment instructions must use charm revisions compatible with all declared interfaces.

### Unit tests fail on the default developer invocation
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py:16`; `pyproject.toml` (`[tool.pytest.ini_options]` has no `pythonpath`)
- **Evidence**: `from src.charm import PenpotCharm` raises `ModuleNotFoundError: No module named 'src'` when running `.venv/bin/pytest tests/unit/test_charm.py` directly. The charm's `dispatch` script sets `PYTHONPATH="${dispatch_path}/lib:${dispatch_path}/src"` (absolute paths at runtime), but pytest runs from the repo root and needs `PYTHONPATH=.:lib`. All 13 tests pass only with `PYTHONPATH=.:lib .venv/bin/pytest tests/unit/`.
- **Impact**: A developer running `uv sync && pytest tests/unit` (the natural workflow) hits an immediate failure.
- **Fix**: Add `pythonpath = [".", "lib"]` to `[tool.pytest.ini_options]` in `pyproject.toml`, or set `package = true` in `[tool.uv]` and add `src/__init__.py`.
- **Linter rule**: pytest must be runnable without manual environment manipulation after `uv sync`.

### `_reconcile` busy-waits up to 120 seconds per hook
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
- **Impact**: On every reconcile trigger (config change, relation change, Pebble ready, secret changed, upgrade charm), the charm can loop for up to 120s, sleeping 3s at a time, leaving the unit in `WaitingStatus` and blocking further hook processing. Not observed directly in this deployment because the charm never reached the point where `_reconcile` gets past the blocked checks, but any config change on a working deployment would freeze the hook for up to two minutes.
- **Fix**: Replace the busy-wait with the Pebble `backend-ready` health check already defined in the layer; trust Pebble to manage service health after `container.replan()` rather than polling in the hook.
- **Linter rule**: hook handlers must not contain a `time.sleep()` loop longer than 5 seconds.

### README documents `nginx-ingress-integrator`, which does not satisfy the charm's `ingress` interface
- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md`
- **Evidence**: The README shows `juju deploy nginx-ingress-integrator --trust` and relating it to penpot. The integration tests instead use `traefik-k8s` (deployed as `traefik-public`) with subdomain routing. Penpot's `requires.ingress` declares `interface: ingress`, which traefik-k8s satisfies but nginx-ingress-integrator does not.
- **Impact**: Following the README literally leaves penpot permanently blocked on `waiting for ingress`.
- **Fix**: Update the README to use `traefik-k8s`, and document the subdomain routing configuration (`routing_mode: subdomain`) that Penpot's SPA needs.
- **Linter rule**: README integration examples must match the interfaces declared in charmcraft.yaml.

### Integration test charm revisions are pinned but undocumented for operators
- **Severity**: medium
- **Kind**: docs
- **Where**: `tests/integration/conftest.py:18–27`
- **Evidence**: Pins include `MINIO_REVISION = 383`, `POSTGRESQL_REVISION = 774`, `REDIS_REVISION = 42`, `S3_INTEGRATOR_REVISION = 330`, `SELF_SIGNED_CERTIFICATES_REVISION = 264`, `SMTP_INTEGRATOR_REVISION = 93`, `TRAEFIK_PUBLIC_REVISION = 277`, `HYDRA_REVISION = 399`, `KRATOS_REVISION = 567`. The README deploys with no revision pins at all, and at least one pin (`SMTP_INTEGRATOR_REVISION = 93`) is behind the currently-deployed `latest/stable` (rev 121), suggesting the test suite isn't kept in sync.
- **Impact**: Operators reproducing the "known-good" stack from the README get different, potentially incompatible revisions than what CI actually exercises.
- **Fix**: Publish the required revisions (e.g. in `tests/integration/README.md`) or keep them tracking latest/stable via automation.
- **Linter rule**: integration test conftest should document or automate the maintenance of charm revision pins.

### `_get_penpot_exporter_unit` can crash if called before the peer relation exists
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:457–465`
- **Evidence**:
  ```python
  def _get_penpot_exporter_unit(self) -> str:
      relation = typing.cast(ops.Relation, self.model.get_relation("penpot_peer"))
      units = list(relation.units)   # AttributeError if relation is None
  ```
- **Impact**: Called from `_reconcile` via `_gen_pebble_plan()`. In observed practice the peer relation is always created before events that trigger this path, and unit tests always provide a peer relation, masking the gap. A multi-unit scale-up where a new unit's `pebble-ready` fires before the peer-relation change propagates could still hit `AttributeError` on `relation.units`. Risk is theoretical but real (unverified in this deployment).
- **Fix**: Guard with `if (relation := self.model.get_relation("penpot_peer")) is None: return self.unit.name`.
- **Linter rule**: relation accessors must guard against `None` before accessing relation attributes.

### No `update_status` handler — status can go stale between hooks
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py` — no `self.framework.observe(self.on.update_status, ...)`
- **Evidence**: Debug log shows `update-status` firing at 21:25:09 with no handler; `_check_ready` is not called by it. When the redis relation was removed, status only updated at the next `update-status` tick, not immediately.
- **Impact**: If a dependency charm becomes unavailable between other hook invocations, the unit can keep reporting stale status (e.g. `active`) until the next unrelated hook fires.
- **Fix**: Add `self.framework.observe(self.on.update_status, self._reconcile)`.
- **Linter rule**: charms with blocking dependencies should observe `update_status` to refresh status periodically.

### Pebble layer always re-added with `combine=True`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:156`
- **Evidence**: `self.container.add_layer("penpot", self._gen_pebble_plan(), combine=True)` runs unconditionally, whether or not the plan changed.
- **Impact**: Combined with the 120s busy-wait, every reconcile touches Pebble even when nothing changed.
- **Fix**: Only add the layer if the generated plan differs from the current plan.
- **Linter rule**: Pebble layer should only be updated when the plan has changed.

### `_get_local_resolver` uses `search=True` on an already-FQDN
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:450–451`
- **Evidence**: `dns.resolver.resolve(kube_dns, search=True)` where `kube_dns = f"kube-dns.kube-system.svc.{self._get_kubernetes_cluster_domain()}"` is already fully qualified.
- **Impact**: Unnecessary search-domain expansion adds DNS lookup latency; falls back to the system nameserver on `DNSException`, which is the correct behaviour, but the initial call shouldn't use `search=True`.
- **Fix**: Call `dns.resolver.resolve(kube_dns)` without `search=True`.
- **Linter rule**: do not use `search=True` with fully-qualified domain names.

### `TimeoutError` name shadowing in readiness check
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
- **Impact**: `requests` raises `requests.exceptions.ReadTimeout` (a `RequestException` subclass), which is already caught by the first branch, so this is mostly theoretical. But the bare `TimeoutError` here is ambiguous with Python's built-in `TimeoutError`, which a static-analysis linter would flag. This method is monkeypatched in all tests and never actually exercised.
- **Fix**: Use `requests.exceptions.Timeout` explicitly; avoid shadowing the built-in name.
- **Linter rule**: use `requests.exceptions.Timeout` explicitly; do not shadow `builtins.TimeoutError`.

## Worth copying

- **Holistic reconciliation**: single `_reconcile` handler triggered by all relevant events — clean and maintainable (`src/charm.py:145–173`).
- **Peer-relation secret sharing**: leader creates a Juju secret and stores the ID in the peer databag; non-leaders read via `secret.get_content(refresh=True)` — avoids a hard leader dependency for followers (`src/charm.py:278–304`).
- **Deterministic exporter election**: `sorted(units + [self.unit])[0]` picks the lowest-numbered unit, no leader election needed for this role (`src/charm.py:457–465`).
- **Graceful readiness check**: `_check_ready()` returns `False` with a `BlockedStatus` listing unfulfilled requirements alphabetically — always actionable (`src/charm.py:250–277`).
- **Observability**: dedicated `MetricsEndpointProvider` + `GrafanaDashboardProvider` with a bundled `grafana_dashboards/penpot.json`.
- **Testing style**: unit tests use `ops.testing.Context`/`State` with clean `conftest.py` fixture helpers.
- **ops conventions**: correct use of `ops.pebble.LayerDict`, `ops.ActiveStatus`, `ops.BlockedStatus`, `ops.WaitingStatus`, `ops.ActionEvent`; action handlers guard with `container.can_connect()`.
- **Rock `run-user`**: `rockcraft.yaml` sets `run-user: _daemon_`, so Pebble services run as the correct non-root user matching file ownership, with no manual user/group management needed in the layer.

## Common-practice notes

- Modern ops 3.x; the `dispatch` script correctly sets `PYTHONPATH="${dispatch_path}/lib:${dispatch_path}/src"`. `charmcraft.yaml` uses `parts.charm.plugin = uv` (no manual dispatch file checked in).
- Charm libraries: `data_platform_libs v0`, `loki_k8s v1`, `prometheus_k8s v0`, `grafana_k8s v0`, `traefik_k8s v2`, `redis_k8s v0`, `smtp_integrator v0`, `hydra v0` — all pinned under `lib/charms/`. `ruff check lib/` reports 228 violations (f-strings, `.format()`, mutable defaults, `assert` statements), all in library code, none in the charm's own `src/`.
- Structure: `src/charm.py` (520 lines), `lib/charms/` (8 libraries), `tests/unit/`, `tests/integration/` — convention-following.
- `charmcraft.yaml`: clean, `base: ubuntu@24.04`, `platforms: amd64`, `assumes: juju >= 3.4`, single k8s-only charm (declares `containers:` and `resources:`).
- No `src/__init__.py`; `pyproject.toml` has `package = false` under `[tool.uv]` — contributes to the test-invocation issue above.
- Linting: `ruff check src/` → 0 violations; `mypy src/charm.py` → 0 issues; `codespell src/` → 0 issues.
- `charmcraft analyze` reports `Cannot find the entrypoint file` for the packed charm — a known `charmcraft analyze` limitation with `uv`-plugin charms, not a charm bug; the dispatch script and entrypoint exist and work.
- k8s-only charm — cannot be deployed on LXD controllers.

## Tests

**Unit tests**: 13 tests in `tests/unit/test_charm.py`. Pass with `PYTHONPATH=.:lib .venv/bin/pytest tests/unit/test_charm.py`; fail with `ModuleNotFoundError: No module named 'src'` without it.

**Coverage**: 76% of `src/charm.py`.
- Covered: `_get_postgresql_credentials`, `_get_redis_credentials`, `_get_s3_credentials`, `_get_smtp_credentials`, `_get_penpot_secret_key`, `_gen_pebble_plan` (full plan verified, including exporter's `**self._get_penpot_secret_key()` at `src/charm.py:231`), `_get_penpot_exporter_unit`, `_get_penpot_backend_options`, `_get_penpot_frontend_options`, `_get_public_uri`, `_get_oauth_client_config`, `create-profile`/`delete-profile` actions.
- Not covered: `_check_ready`'s blocked-message path (all tests patch `_check_penpot_backend_ready` to return `True` and only exercise the success path); `_check_penpot_backend_ready` itself (`# pragma: nocover`); `_get_local_resolver`; `_get_kubernetes_cluster_domain`; `_reconcile`'s timeout path; `_get_penpot_exporter_unit` without a peer relation; `_get_oauth`; `_get_penpot_oauth_config`.

**Test infrastructure**: uses `ops.testing` with `scenario`-style `State` fixtures in `conftest.py`, using the direct relation-data format rather than `DatabaseRequires`' JSON-serialized format — correct for this test framework.

**Integration tests**: two tests, `test_create_profile` (up to 900s) and `test_oauth_login` (up to 900s + 600s), requiring `--charm-file` and `--penpot-image`; not runnable in this environment. Pins specific charm revisions (see findings above).

**Linting**: `ruff check src/` → 0 violations; `ruff check lib/` → 228 violations (library code only); `mypy src/charm.py` → 0 issues; `codespell src/` → 0 issues.

## Docs

- `README.md`: deployment instructions use `nginx-ingress-integrator` instead of `traefik-k8s`, and don't pin the `postgresql-k8s` revision — both cause the documented deployment path to be non-functional. Otherwise well-structured, describing the full stack.
- `docs/reference/charm-architecture.md`: solid, with mermaid diagrams explaining the holistic reconciliation approach.
- `docs/tutorial/getting-started.md`: comprehensive local-LXD-testing guide; also references `nginx-ingress-integrator`.
- `docs/how-to/upgrade.md`: basic upgrade documentation.
- `docs/how-to/configure-sso.md`, `configure-s3.md`, `configure-smtp.md`: good integration how-tos.
- `CONTRIBUTING.md`: detailed contributing guide.
- `pyproject.toml`: no `pythonpath` in pytest config (causes the test-invocation breakage above).

## Open questions

- Whether the 120-second busy-wait in `_reconcile` is ever load-bearing: if the backend genuinely takes over two minutes to become ready after `container.replan()`, this timeout is reasonable; if it typically starts in seconds, the loop just adds unnecessary hook duration. A Pebble health check (`backend-ready`) already exists in the layer and could replace the polling loop.
- Whether `nginx-ingress-integrator` on charmhub provides the `ingress` interface at all — not verified; the README uses it but the integration tests use `traefik-k8s`.
- Whether `_check_ready`'s `public_uri.startswith("https://")` guard is exercised correctly when ingress is present but non-HTTPS — logic looks correct but untested.
- Whether traefik-k8s rev 401 would work on this cluster with a manually configured `external_hostname` absent a LoadBalancer — current implementation appears to require both a LoadBalancer and cluster-scope RBAC to list services, neither of which this cluster provides.
- Whether `_get_penpot_exporter_unit` could actually be called before the peer relation exists in a multi-unit scale-up scenario — not observed, but the code path exists and the fix is trivial (unverified in production).
