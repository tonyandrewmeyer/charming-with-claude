# maubot-operator

A k8s charm deploying [Maubot](https://github.com/maubot/maubot), a plugin-based Matrix bot
system, with three Pebble services (maubot, nginx, blackbox-exporter), a mandatory PostgreSQL
integration, and optional Synapse (matrix-auth), ingress, and Loki integrations. The reconcile
pattern and status handling are clean, and the happy path (deploy + relate postgresql-k8s on
Juju 3.6) works. But the charm has serious gaps under failure conditions: losing the postgresql
relation never reaches `BlockedStatus` — it either silently stays `active` with a dead database
connection or crashes into `error` with an uncaught `ChangeError`; a stopped maubot Pebble
service is never detected or restarted; and `juju refresh` from a locally packed charm fails
outright with `ModuleNotFoundError`, making local upgrades impossible. The published
`latest/edge` revision (rev 16) is roughly 97 commits behind HEAD and is missing two actions
that exist in source. A maintainer should first fix the postgresql-removal status handling and
the Pebble self-heal gap, then get CI publishing current revisions to `latest/edge` again.

| | |
|---|---|
| Repo | canonical/maubot-operator @ `e6c34b7` (2026-07-21) |
| Charms | maubot |
| Substrate | k8s |
| Deployed | yes — `concierge-k8s-3` (Juju 3.6.25), `latest/edge` rev 16 reached `active`; locally packed charm failed on `juju refresh` |
| Reviewed | 2026-08-22 |

## What it does

Deploys a Maubot container with three Pebble services (maubot Python app on `:29316`, nginx
reverse-proxy on `:8080`, blackbox-exporter on `:9115`). Requires PostgreSQL for data storage;
optionally integrates with a Synapse homeserver via `matrix-auth`, an ingress controller, and
Loki for log forwarding. Provides a Prometheus scrape target (blackbox) and Grafana dashboards.
Four Juju actions manage admin accounts and bot registration (only two are present in the
currently published revision). Ships 8 bundled charm libs under `lib/charms/` and uses `cosl
1.10.2` for COS integrations.

## Deployment log

### Juju 3.6 k8s — primary environment
- Created model `rv-test2` on `concierge-k8s-3` (Juju 3.6.25)
- `juju trust postgresql-k8s --scope=cluster` required before postgresql-k8s could start (RBAC issue in this environment)
- Deployed maubot from `latest/edge` **rev 16**; related to postgresql-k8s
- Maubot reached `active` in ~60s after relation
- `juju actions maubot` confirmed only 2 of 4 actions: `create-admin`, `register-client-account`
- `create-admin` (newadmin): password returned in cleartext in action results
- `create-admin` (duplicate name): correctly failed with `testadmin already exists`
- `create-admin` (root): correctly rejected with `root is reserved, please choose a different name`
- `register-client-account` (no matrix-auth): correctly failed with `matrix-auth integration is required`

### Failure injection — postgresql relation removal (critical, timing-dependent)

**Test 1** (postgresql still running after relation removal):
- `juju remove-relation maubot postgresql-k8s`
- `postgresql-relation-departed` hook fired
- Status: briefly `maintenance`, then **returned to `active`** within the same hook execution
- Pebble: maubot service kept running, connecting to the database with stale cached credentials
- Root cause: `_get_configuration()` reads the cached `/data/config.yaml` (written during the
  previous reconcile with valid credentials). `_get_postgresql_credentials()` returns the same
  stale credentials because `relation.app` is still set during `relation-departed`. No exception
  is raised, so `add_layer` + `restart` run (they follow the `except MissingRelationDataError`
  block) and the charm returns to `ActiveStatus`.
- Confirmed: postgresql-k8s was still running and accepting the stale credentials

**Test 2** (postgresql cleaned up after relation removal), on a different model (`rv-test2`):
- `postgresql-relation-departed` hook fired
- `_get_postgresql_credentials()` raised `MissingRelationDataError` immediately (`relation.app` was `None`)
- `_configure_maubot()` raised, caught in `_reconcile()`, `BlockedStatus` set
- But `container.restart(MAUBOT_NAME)` runs **after** the except block regardless
- Pebble started maubot with the cached config (stale credentials)
- maubot crashed with `asyncpg.exceptions.InvalidAuthorizationSpecificationError`
- Pebble raised `ops.pebble.ChangeError` — not caught (only `stop()` errors are caught)
- Hook failed with exit status 1 — charm went to `error`
- The maubot Pebble service entered `backoff` (continuous restart loop)

**Conclusion**: postgresql-removal behaviour is entirely timing-dependent. If postgresql still
accepts the stale credentials at restart time, the charm silently stays `active` with no working
database. If postgresql has already cleaned up credentials, maubot crashes, Pebble raises an
uncaught `ChangeError`, and the charm goes to `error`. `BlockedStatus` — the correct outcome for
a missing required relation — was never observed in either case.

### Failure injection — Pebble service stop
- `kubectl exec maubot-0 -c maubot -- pebble stop maubot`
- maubot service: `inactive`; Juju status: `active` with no indication of failure
- No hooks fired, no self-heal within 30+ seconds
- Pebble: `blackbox` and `nginx` still `active`, `maubot` `inactive`
- Recovery: `juju config maubot public-url=...` triggered `_reconcile()`, maubot restarted in ~8s

### Failure injection — invalid config value
- `juju config maubot public-url="not-a-url"` accepted without error, written to config.yaml
  as `public_url: not-a-url`; charm returned to `active` without validation

### Loki integration (live test)
- `juju relate maubot:logging loki-k8s:logging`: Pebble plan acquired
  `log-targets.loki-k8s/0` pointing at the Loki endpoint; loki-k8s itself was blocked with an
  RBAC error in this environment
- `juju remove-relation maubot loki-k8s`: **the Loki log-target persisted in the Pebble plan**,
  still showing `log-targets.loki-k8s/0` with `services: ["-all"]` — confirmed as GitHub issue #27
- Root cause: `lib/charms/loki_k8s/v1/loki_push_api.py:2312` `disable_inactive_endpoints()` calls
  `add_layer()` with `services: ["-all"]`, which only disables the log-target and never removes
  it; the Pebble API has no mechanism to delete log-targets. maubot does not observe
  `loki_push_api_endpoint_departed`, so it has no workaround.

### Grafana/metrics integration
- Related `maubot:metrics-endpoint` to `grafana-agent-k8s:metrics-endpoint`
- Related `maubot:grafana-dashboard` to `grafana-agent-k8s:grafana-dashboards-consumer`
- grafana-agent-k8s remained `blocked` (needs a real Grafana charm or cloud config) — environment
  limitation, not a maubot bug

### `juju refresh` to locally packed charm (critical)
- Deployed charmhub rev 16 → `active`
- `juju refresh maubot --path=maubot_amd64.charm` succeeded as a command
- Immediately: `upgrade-charm`/`postgresql-relation-changed` hook failed with
  `ModuleNotFoundError: No module named 'ops'`; charm went to `error`
- Root cause: the locally packed charm (`charmcraft pack`) creates a traditional Python venv at
  `venv/lib/python3.10/site-packages/ops/` with Python 3.10 bytecode. The container runs Python
  3.12 (`/usr/bin/python3`). The dispatch script symlinks `venv/bin/python → /usr/bin/python3`
  and sets `PYTHONPATH=lib:venv/src`, but `venv/lib/python3.10/site-packages/` is not on
  PYTHONPATH, so `ops` is invisible. The charmhub-published charm avoids this because it uses a
  flat venv layout (Juju's relocatable venv format) with packages at `venv/ops/`, directly on
  PYTHONPATH.
- Note: the charmhub-published charm uses `ops 2.18.1` in a flat venv; the local pack uses
  `ops 3.8.0` in a traditional venv.

### Juju 4.0 k8s — second environment
- Created model `rv-maubot4` on `concierge-k8s-4` (Juju 4.0.12)
- Deployed maubot `latest/edge` rev 16 — succeeded
- `juju deploy postgresql-k8s --channel 14/stable`: failed — "charm requires Juju version < 4.0"
- `juju deploy postgresql-k8s --channel 16/stable`: failed — same constraint
- `juju deploy postgresql-k8s --channel latest/stable` (rev 20): failed — "requires Juju < 3.5"
- `juju deploy self-signed-certificates`: succeeded
- `juju relate maubot self-signed-certificates`: failed — no compatible endpoints (maubot has no
  `certificates` relation)
- Result: maubot can deploy on Juju 4.x but can never reach `active` because no postgresql-k8s
  channel supports Juju 4.x. The charm is effectively incompatible with Juju 4.x in its current
  published form.

### Ingress integration
- Deployed traefik-k8s on k8s-4: succeeded
- `juju relate maubot traefik-k8s` on k8s-3: traefik-k8s entered `error` ("hook failed: start")
  — RBAC issue in this environment, not attributable to maubot

## Observed behaviour

### Timing
- Install to active (with postgresql, Juju 3.6): ~60–70s
- Config change hook: ~4–5s
- Action `create-admin`: ~2s
- Postgresql removal (Test 1, pg still running): hook completes in ~4s, returns to `active` without reaching blocked
- Postgresql removal (Test 2, pg cleaned up): hook fails with exit status 1, charm goes to `error`, maubot enters backoff loop
- Process stop → self-heal via config change: ~8s
- `juju refresh` to local pack: immediately fails with `ModuleNotFoundError`

### Resources
- Pod memory: 87Mi; Pod CPU: 4m average
- Container file ownership: root:root throughout
- `config.yaml`: mode 0600 — correct
- `/data` storage: 974Mi allocated, 1% used

### Postgresql removal — the complete failure spectrum
1. **Silent active** (postgresql still accepting stale credentials): charm stays `active`, maubot keeps running, operator has no indication of misconfiguration
2. **Error + backoff** (postgresql has cleaned up credentials): charm goes to `error`, maubot enters a restart loop with `ChangeError` uncaught in the hook
3. **Correct blocked** (never observed): would require checking relation existence *before*
   reading cached credentials, and catching `ChangeError` from Pebble's background restart

## Findings

### 1. Postgresql relation removal never reaches `BlockedStatus` — timing-dependent silent-active or error+backoff (Critical)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:138-147` (`_configure_maubot`), `src/charm.py:149-171` (`_reconcile`)
- **Evidence**: Live on Juju 3.6, two distinct failure modes depending on whether postgresql-k8s
  had cleaned up credentials at restart time. Test 1: charm returned to `active` with maubot
  running on stale `/data/config.yaml` credentials, no blocked state, no operator signal. Test 2:
  `postgresql-relation-departed` hook failed (exit status 1); `juju show-status-log` showed
  `"hook failed: "postgresql-relation-departed"`; kubectl logs showed
  `asyncpg.exceptions.InvalidAuthorizationSpecificationError: no pg_hba.conf entry for host
  "10.1.0.17", user "relation_id_3", database "maubot"`; maubot Pebble service entered `backoff`.
- **Impact**: An operator gets no actionable status. The charm either stays silently `active`
  without a working database, or crashes into `error` with an unhelpful message, and in the
  second case the maubot Pebble service loops continuously in `backoff`.
- **Fix**: (1) Call `_get_postgresql_credentials()` before `_get_configuration()` so a missing
  relation is detected before touching cached config; raise `MissingRelationDataError`
  immediately if the relation is gone. (2) Catch `ops.pebble.ChangeError` from the `restart()`
  call in `_reconcile()`, not just `stop()` errors. (3) Consider `container.replan()` instead of
  `restart()` to handle in-flight service changes gracefully.
- **Linter rule**: not mechanically checkable — requires an integration test with a live
  postgresql-k8s that has time to clean up credentials between relation removal and hook execution.

### 2. Pebble services do not self-heal when the maubot process is stopped (Critical)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py` (no watchdog/observer pattern)
- **Evidence**: `kubectl exec maubot-0 -c maubot -- pebble stop maubot` left the maubot service
  `inactive` with no hooks firing and no self-heal after 30+ seconds. Juju continued reporting
  `active` with an empty message. `nginx` and `blackbox` remained `active`. Recovery only
  happened via a forced reconcile (config change), in ~8s.
- **Impact**: If the maubot process crashes or is killed, operators are not alerted — the charm
  appears healthy while the bot is down.
- **Fix**: Add a periodic reconcile or watch loop (`container.replan()` on a timer, or a Pebble
  health check combined with a periodic `_reconcile()` call) to detect and restart stopped
  services. The ops framework does not do this automatically.
- **Linter rule**: "charm does not implement Pebble service health monitoring" — mechanically
  checkable by asserting that `_reconcile()` or a periodic handler calls `container.get_service()`
  and restarts any `inactive` services.

### 3. `juju refresh` to a locally packed charm fails with `ModuleNotFoundError` (Critical)
- **Severity**: critical
- **Kind**: bug
- **Where**: `dispatch` script in the locally packed charm; `build-base: ubuntu@22.04` in `charmcraft.yaml`
- **Evidence**: Deploying charmhub rev 16 then running `juju refresh maubot
  --path=maubot_amd64.charm` sent the charm to `error` ("hook failed: upgrade-charm"). kubectl
  logs: `ModuleNotFoundError: No module named 'ops'` at `src/charm.py:17` (`import ops`). The
  charm cannot be upgraded via local pack — it is stuck at rev 16 in this scenario.
- **Impact**: Operators cannot upgrade using `juju refresh` with a locally built charm; CI/CD
  pipelines that build and refresh locally will fail. The charm is effectively read-only once
  deployed from charmhub.
- **Fix**: Add the venv site-packages to `PYTHONPATH` in the dispatch script, e.g.
  `export PYTHONPATH="${dispatch_path}/lib:${dispatch_path}/src:${dispatch_path}/venv/lib/python3.10/site-packages"`,
  or align the local pack format with the charmhub build (flat venv). Changing `build-base` to
  `ubuntu@24.04` would still risk bytecode-format mismatches and needs verification.
- **Linter rule**: "dispatch script sets PYTHONPATH but does not include venv site-packages" — mechanically checkable.

### 4. `_is_maubot_ready()` had an inverted return value in deployed rev 16 (Critical in rev 16, fixed in source)
- **Severity**: critical (in deployed rev 16 only)
- **Kind**: bug
- **Where**: deployed rev 16 (`78f2a72`) — current HEAD has the correct implementation
- **Evidence**: rev 16 source returns `(not self.container.can_connect() or ...)` while its
  docstring says "True if Maubot is ready"; call sites compensate with
  `if not self._is_maubot_ready():` (lines 227, 260, 293, 325). Fixed in commit `ad8a5f2`
  (2025-04-23), which corrected the logic to `(can_connect() and ...)` and updated call sites to
  `if not self._is_maubot_ready()`. The deployed charm (rev 16) still ships the inverted version.
- **Impact**: any future code calling the function without the compensating negation would
  behave incorrectly; the currently published revision carries this latent risk.
- **Fix**: Already fixed in source — publish a refreshed charm to `latest/edge`.
- **Linter rule**: "function returns inverted boolean relative to its docstring" — checkable by static analysis.

### 5. Loki log-targets persist after the Loki relation is removed (High — confirmed live, root cause in library, GitHub issue #27)
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/loki_k8s/v1/loki_push_api.py:2312-2341` (`disable_inactive_endpoints`),
  `src/charm.py:80-83` (maubot doesn't observe `loki_push_api_endpoint_departed`)
- **Evidence**: after removing the Loki relation, the Pebble plan still showed
  `log-targets.loki-k8s/0` with `services: ["-all"]`. GitHub issue #27 (open since 2025-02-18)
  confirms this is a known bug.
- **Impact**: Stale Loki endpoints cause failed scrape attempts, polluted metrics, and confusing observability data.
- **Fix**: Observe `loki_push_api_endpoint_departed` in the charm and call `container.add_layer()`
  with a layer that omits the removed log-target; or fix the library to provide a
  `remove_log_target()` method.
- **Linter rule**: not mechanically checkable without a live Loki integration test.

### 6. maubot is incompatible with Juju 4.x (High)
- **Severity**: high
- **Kind**: bug
- **Where**: `charmcraft.yaml`, postgresql-k8s compatibility matrix
- **Evidence**: maubot deployed successfully on `concierge-k8s-4` (Juju 4.0.12), but
  postgresql-k8s failed to deploy on channels `14/stable`, `16/stable`, and `latest/stable`
  ("charm requires Juju version < 4.0" / "< 3.5"). No postgresql-k8s channel currently supports
  Juju 4.x, so maubot is stuck `blocked` ("postgresql integration is required") indefinitely on Juju 4.
- **Impact**: the charm is effectively non-functional on the current stable Juju release.
- **Fix**: Either get a Juju-4-compatible postgresql-k8s published, or explicitly document the
  Juju 3.x-only requirement (e.g. a version constraint note in `charmcraft.yaml`/README).
- **Linter rule**: not mechanically checkable.

### 7. Published `latest/edge` revision is severely outdated (High)
- **Severity**: high
- **Kind**: process
- **Where**: `.github/workflows/publish_charm.yaml`
- **Evidence**: HEAD is `e6c34b7` (2026-07-21); the deployed `latest/edge` rev 16 corresponds to
  commit `78f2a72` (2025-02-10) — roughly 97 commits behind. The publish workflow only triggers
  on `workflow_dispatch` or `push` to `main`, and appears not to have run since rev 16 was cut.
- **Impact**: users installing from `latest/edge` get a charm missing two actions
  (`delete-admin`, `reset-admin-password`) and the `_is_maubot_ready()` fix, among other changes.
- **Fix**: Trigger the publish workflow, or add automatic publishing on merge to `main`.
- **Linter rule**: not applicable.

### 8. `public-url` config accepts any value without validation (Medium)
- **Severity**: medium
- **Kind**: bug
- **Where**: `charmcraft.yaml` config option `public-url`
- **Evidence**: `juju config maubot public-url="not-a-url"` was accepted, written to
  `config.yaml` as `public_url: not-a-url`, and the charm returned to `active` without validation.
- **Impact**: operators setting a malformed `public-url` get no feedback.
- **Fix**: Add a `pattern` regex in `charmcraft.yaml`, e.g. `^https?://.*`.
- **Linter rule**: "config option 'public-url' has no schema validation" — mechanically checkable.

### 9. Bot passwords and tokens returned in cleartext action results (Medium)
- **Severity**: medium
- **Kind**: security / ux
- **Where**: `src/charm.py:204` (`create-admin`), `src/charm.py:313` (`register-client-account`)
- **Evidence**: `juju run maubot/0 create-admin name=newadmin` returned
  `password: REDACTED` in the action result, visible to anyone with model access.
  `register-client-account` similarly exposes `password` and `access-token` in plain text.
- **Impact**: bot account passwords and Matrix access tokens grant Matrix access and are stored
  in Juju's action/event log.
- **Fix**: Use the ops Secret API (`self.model.app.add_secret()`) and return the secret ID instead.
- **Linter rule**: "action handler sets password value in plain-text action results" —
  mechanically checkable by pattern-matching known password field names in action results.

### 10. Loki integration not verifiable end-to-end due to environment RBAC (Medium)
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/charm.py:80-83`, `lib/charms/loki_k8s/v1/loki_push_api.py`
- **Evidence**: loki-k8s was blocked by RBAC errors in this environment, preventing observation
  of actual log forwarding end-to-end. The integration test `test_loki_endpoint` only checks the
  positive case (Loki relation added) and does not assert that log-targets are removed on
  relation removal.
- **Impact**: the missing assertion means issue #27 (finding 5) will not be caught by CI.
- **Fix**: Add an integration test asserting Pebble log-targets are absent after Loki relation
  removal; re-test Loki integration in an environment with working RBAC.
- **Linter rule**: not applicable.

### 11. Two actions missing from deployed rev 16 (Medium)
- **Severity**: medium
- **Kind**: test-gap / ux
- **Where**: deployed rev 16 (`78f2a72`)
- **Evidence**: `juju actions maubot` on the deployed model shows only `create-admin` and
  `register-client-account`. `delete-admin` (commit `ad8a5f2`, 2025-04-23) and
  `reset-admin-password` (commit `0c6810c`) are absent. After `juju refresh` to the locally
  packed charm, all four actions appeared.
- **Impact**: operators using the published charm cannot delete admin accounts or reset admin passwords.
- **Fix**: Publish a current revision to `latest/edge` (see finding 7).
- **Linter rule**: not applicable.

### 12. `create-admin` and `reset-admin-password` use inconsistent "root" error messages (Nit)
- **Severity**: nit
- **Kind**: ux
- **Where**: `src/charm.py:218` vs `src/charm.py:292`
- **Evidence**: `create-admin` rejects "root" with `"root is reserved, please choose a different
  name"`; `reset-admin-password` rejects with `"action disabled, root is reserved."` —
  inconsistent phrasing and capitalization.
- **Impact**: cosmetic only.
- **Fix**: Use a shared constant/message for both.
- **Linter rule**: not mechanically checkable.

### 13. Bundled charm libs have 105 ruff-fixable lint issues (Low)
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/loki_k8s/v1/`, `lib/charms/data_platform_libs/v0/`,
  `lib/charms/grafana_k8s/v0/`, `lib/charms/prometheus_k8s/v0/`, `lib/charms/traefik_k8s/v2/`,
  `lib/charms/synapse/v0/`, `lib/charms/observability_libs/v0/`
- **Evidence**: `ruff check lib/` reports 105 fixable issues (211 total warnings), including
  `UP032` (`.format()` → f-strings), `SIM118` (`.keys()` usage), `F401` (unused imports), `S101`
  (`assert` usage), `B006` (mutable default args), `RUF012`/`RUF015` (mutable classvars), `D417`
  (missing docstring args), `B028` (missing `stacklevel`).
- **Impact**: bundled code carries technical debt; mutable defaults (`B006`) can cause bugs shared across instances.
- **Fix**: Run `ruff check lib/ --fix`; manually review `assert` usage and mutable defaults.
- **Linter rule**: "bundled charm libraries fail ruff checks" — mechanically checkable.

### 14. `register-client-account` correctly rejects requests without matrix-auth (No issue, noted for completeness)
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:322-331`
- **Evidence**: `juju run maubot/0 register-client-account admin-name=testadmin
  admin-password=fakepass account-name=bot1` correctly failed with "matrix-auth integration is
  required" when no Synapse relation exists.
- **Impact**: none — correct behaviour.
- **Fix**: none needed.
- **Linter rule**: not applicable.

## Worth copying

### Clean reconcile pattern
`src/charm.py:155-180` — `_reconcile()` is the single reconciliation entry point called from all
event handlers. It sets `MaintenanceStatus` up front, returns early if the container is not
connectable, catches `MissingRelationDataError` to set `BlockedStatus`, and only reaches
`ActiveStatus` at the end. This is the correct pattern, though see finding 1 for where it breaks down.

### Status precedence is correct elsewhere
The charm never sets `ActiveStatus` without checking prerequisites in the normal path.
`MaintenanceStatus` is used during reconciliation and `BlockedStatus` carries a specific,
actionable message for missing relations, matching the Juju status precedence model.

### Explicit service dependency in Pebble layer
`src/charm.py:448-454` — nginx declares `"after": [MAUBOT_NAME]`, ensuring maubot starts before
nginx attempts to proxy it, avoiding startup races.

### Grafana dashboard provisioning via `GrafanaDashboardProvider`
`src/charm.py:77` — uses the standard `GrafanaDashboardProvider` from `cosl` to serve dashboard
JSON from `src/grafana_dashboards/` — the canonical pattern.

### Blackbox exporter for Prometheus health checks
`src/charm.py:342-363` — using blackbox-exporter (bundled in the rock) to probe the maubot HTTP
endpoint is the correct approach for external health monitoring.

### Proper file permissions in container
`config.yaml` is written with mode 0600, owned by root; secrets are not world-readable.

### Scenario tests using `ops.testing.Context`
`tests/unit/test_charm.py` uses the modern `ops.testing.Context` API (not the deprecated
`Harness`) for unit tests — the recommended approach.

## Common-practice notes

### Better than average
- Reconcile pattern is cleaner than many charms that scatter logic across individual hook handlers.
- Action error handling is thorough (`EventFailError` and `pebble.PathError` caught separately with distinct messages).
- Rock image is built with Rockcraft and published as a Charmhub resource, cleanly separating workload from charm logic.
- `cosl` version kept current via Renovate.
- Two layers of unit tests: `ops.testing.Context` scenario tests and `Harness` tests for backward compatibility.

### Drifts from convention
- **`build-base: ubuntu@22.04`**: built with Python 3.10 but deployed on Ubuntu 24.04 containers
  (Python 3.12) — causes `juju refresh` to fail for locally packed charms (finding 3). The
  charmhub-published version avoids this via Juju's flat venv format.
- **Bundled charm libs**: 8 libs under `lib/charms/` — large, avoids network dependencies at
  startup, but carries 105 ruff-fixable lint issues.
- **`requests` not `httpx`**: modern charms tend to prefer `httpx` for async-capable HTTP.
- **Upgrade docs**: 106 bytes, just "juju refresh maubot" — no pre/post-upgrade steps.
- **Config validation**: no schema validation for `public-url`.
- **No `upgrade-charm` hook**: relies on `config-changed` to handle upgrades; works, but offers no explicit pre/post-upgrade verification.

## Tests

### Unit tests — 21 tests, all passing
```
tests/unit/test_charm.py: 8 tests (ops.testing.Context API)
tests/unit_harness/test_charm.py: 13 tests (deprecated Harness API)
21 passed, 742 warnings in 0.29s
```

### Integration tests — 13 tests, all fail/error in setup (429s)
```
ERROR tests/integration/test_charm.py::test_build_and_deploy      — assert maubot_image
ERROR tests/integration/test_charm.py::test_create_admin_action_* (all) — assert maubot_image
ERROR tests/integration/test_charm.py::test_reset_admin_password_*  (all) — assert maubot_image
ERROR tests/integration/test_charm.py::test_delete_admin_action_*   (all) — assert maubot_image
ERROR tests/integration/test_charm.py::test_public_url_config         — assert maubot_image
ERROR tests/integration/test_charm.py::test_register_client_account   — assert maubot_image
FAILED tests/integration/test_charm.py::test_cos_integration         — JujuError
XFAIL tests/integration/test_charm.py::test_loki_endpoint           — aborted
ERROR tests/integration/test_e2e_stable.py::test_deploy_stable       — requests exception
```
All fail in setup because `--maubot-image` was not provided — expected, since the rock image is
not available in this review environment and requires a separate rock registry.

### Test coverage gaps relative to the findings above
- Postgresql relation removal: `test_postgresql_relation_departed` uses a
  `postgresql_empty_relation` fixture with no remote app data, so `MissingRelationDataError` is
  raised immediately — it does not reproduce the real-world scenario where cached credentials
  from a prior valid relation are reused (finding 1). Test passes but doesn't catch the bug.
- Loki relation removal: `test_loki_endpoint` only verifies log-targets appear when Loki is
  added, not that they're removed when Loki is removed (finding 5) — issue #27 will not be
  caught by CI.
- No test verifies behaviour when the maubot Pebble service is `inactive` (finding 2).
- No test covers the `juju refresh` upgrade path (finding 3).
- `_reconcile()` catches `stop()` errors but not `restart()` errors — no test covers this gap.
- `register-client-account` MatrixAuth error path — line 273 not covered.
- `delete-admin` `PathError` catch — line 206 not covered.
- `reset-admin-password` `PathError` catch — line 232 not covered.
- No unit test covers the `grafana-dashboard-relation-created` handler.
- No unit test covers the `ingress-ready` handler.
- `_on_matrix_auth_request_processed` reconcile path — line 307 not covered.
- `_get_matrix_credentials` with relation present — line 326 not covered.

### Linting
- `ruff check src/`: all checks passed
- `ruff check lib/`: 105 fixable issues in bundled charm libs (see finding 13)

## Docs

### `README.md` (2134 bytes)
Minimal — mostly a link farm with architecture diagram and community links. Doesn't explain
what `public-url` does, which integrations are required vs. optional, or how to configure bots.

### `docs/reference/charm-architecture.md`
Detailed and accurate: Mermaid C4 diagram, Pebble layer descriptions, OCI image build process,
container entry points, integrations reference. Matches observed behaviour.

### `docs/how-to/upgrade.md` (106 bytes)
Very thin — just "juju refresh maubot". No pre-upgrade steps (backup data storage, check release
notes), no post-upgrade verification, no known issues listed.

### `CONTRIBUTING.md`
Comprehensive — CLA, commit signing, PR description template, `uv`-based dev environment setup, `tox` testing. Accurate and useful.

### `terraform/README.md`
Clear terraform module documentation with example usage.

## Open questions

1. Is there a plan to add Juju 4.x support to postgresql-k8s, or should maubot explicitly
   document the Juju 3.x-only limitation?
2. Would changing `build-base` to `ubuntu@24.04` fix the local-pack `juju refresh` failure, or is
   fixing the dispatch script's `PYTHONPATH` the correct approach? (unverified which is the
   right fix)
3. The published charm resolves `ops 2.18.1` in a flat venv while `requirements.txt` specifies
   `ops==3.8.0` and the local pack resolves that version in a traditional venv — this version/venv
   mismatch needs investigation.
4. GitHub issue #27 (Loki log-target persistence) has been open since February 2025 — is a fix
   planned in the `loki_k8s` library, or does maubot need its own workaround?
5. `publish_charm.yaml` only runs on `workflow_dispatch` or push to `main`. Why hasn't it run
   since the rev 16 tag (Feb 2025) despite ~97 subsequent commits? The publishing pipeline
   appears effectively broken.
