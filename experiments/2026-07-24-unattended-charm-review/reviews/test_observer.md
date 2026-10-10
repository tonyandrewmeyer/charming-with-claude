# test_observer

Two charms (`test-observer-api` and `test-observer-frontend`) that together deploy a FastAPI backend and Flutter frontend for tracking and reviewing test results. Both are k8s-only wrappers; the backend is the substantial one (Pebble-managed API + Celery containers, Postgres/Redis integration, leader-coordinated database migrations). The charms are generally well-structured — migration coordination via peer databag, SAML validation on every hot path, and `CollectStatusEvent` ingress-conflict handling are all solid patterns. The critical problem found in extended testing is that `sys.exit()` is used as control flow inside a property that gets evaluated *while* a Pebble layer is being built: if the redis relation breaks (or is simply absent) at the wrong moment, the layer update is interrupted mid-flight and both the `api` and `celery` containers end up with **empty Pebble plans** — the workload goes fully offline while the charm still reports `waiting`, and it does not recover on its own. Combined with a total absence of unit tests for the backend charm and several actions that silently no-op under the same condition, this is the top priority for a maintainer to fix before the next release. Read: fix the `sys.exit()`-in-layer-construction bug first, then add backend unit tests to stop it from recurring.

| | |
|---|---|
| Repo | canonical/test_observer @ `01c5ca9` (2026-07-13, per `_context/head.txt`) |
| Charms | test-observer-api (backend/charm), test-observer-frontend (frontend/charm) |
| Substrate | k8s only (no machine/lxd support) |
| Deployed | yes — concierge-k8s-3 (stable rev 380/256), upgraded backend to edge rev 387; also tested on concierge-k8s-4 (Juju 4.0.12) |
| Reviewed | 2026-08-23 |

## What it does

`test-observer-api` (the primary charm, k8s) wraps a FastAPI + Celery workload with two Pebble containers (`api`, `celery`). It provides a REST API (`test-observer-rest-api`), Prometheus metrics, and Grafana dashboards. It requires PostgreSQL, Redis, and optionally ingress (Traefik) or nginx-route. Database migrations are run by the leader and the outcome is shared via the peer relation databag — all units wait for migrations before starting workloads. `test-observer-frontend` wraps an nginx-serving Flutter SPA and requires only the API charm's REST relation and optionally ingress.

## Deployment log

**Controller**: concierge-k8s-3 (Juju 3.6.25), model `rv-tobs`.

```
juju deploy postgresql-k8s --channel=14/stable db          # rev 925
juju deploy redis-k8s --channel=latest/edge redis           # rev 42
juju deploy test-observer-api --channel=stable backend      # rev 380
juju deploy test-observer-frontend --channel=stable frontend # rev 256
juju config backend hostname=test-observer-api.test sessions_secret=$(openssl rand -base64 32)
juju config frontend hostname=test-observer-frontend.test test-observer-api-scheme='https://'
juju trust db --scope=cluster   # needed: "Insufficient permissions" without this
juju relate backend redis
juju relate backend db
juju relate backend frontend
```

DB took ~6 minutes to become active (from "awaiting for cluster to start"). All four apps were `active` by ~01:10 UTC.

**Deploy from charmhub (rev 380/256) vs local HEAD (`01c5ca9`)**: the running backend serves version `0.0.0+g5441e23`; local HEAD is 4 commits newer. The gap is not expected to affect the behaviour observed.

**Juju 4.0.12 test**: deployed backend on concierge-k8s-4 (Juju 4.0.12). Charm deployed and entered `waiting` state as expected. No behavioural difference found between Juju 3.6 and 4.0.

**`juju refresh`**: upgraded backend from `latest/stable` (rev 380) to `latest/edge` (rev 387). Hook sequence: `stop` → `upgrade-charm` → `config-changed` → `start`. New unit (`backend/1`) showed "Waiting for Pebble for Celery" while the new container image was pulled. Both units recovered to `active` once redis was re-related.

**Scale up**: `juju add-unit backend --num-units 1` — both units went `active` in ~30s. Migration coordination via peer databag worked correctly (follower waited for leader's migration revision before starting workloads).

**Scale down**: `juju remove-unit backend --num-units 1` — target unit went to `terminated (remove)`. Clean teardown.

**Relation removals**:
- Redis removed: backend → `WaitingStatus("Waiting for redis relation")` ✓
- Database removed: backend → `WaitingStatus("Waiting for database relation")` ✓
- Re-relating both: recovered to `active` ✓

**Failure injections**:
- Partial SAML config (only `saml_idp_metadata_url`): blocked ✓
- Invalid frontend YAML config: blocked ✓
- Invalid email in `add-user`: fails with `ValueError: Email not registered in launchpad` ✓
- Non-existent artefact in `change-assignee`: fails with `ValueError: No artefact with id N found` ✓
- Non-existent artefact in `delete-artefact`: **silently succeeds** (see Findings)
- Short `sessions_secret` ("short"): accepted, no config-level guard (see Findings)
- Kill uvicorn process inside API container: Pebble restarted it automatically. Status stayed `active` ✓
- Config change while redis absent: `_celery_broker_url` fires `sys.exit(0)` after setting `WaitingStatus`; hook exits with code 0, status persists in the simple case, but see the layer-interruption finding below for the case where this happens during a layer update.

**Integrations**:
- **Grafana dashboards**: `backend:grafana-dashboard → grafana:grafana-dashboards-consumer` established. `grafana-agent-k8s` (rev 233) is `blocked` because it needs `grafana-cloud-config` or a real `grafana-dashboards-provider` — expected, since the backend only provides dashboards, not a full Grafana.
- **Metrics endpoint**: `backend:metrics-endpoint → grafana` established. Prometheus scrape target on `*:9090` confirmed in code, not verified end-to-end.
- **TLS**: backend charm has no `tls` relation interface; no integration with `self-signed-certificates` is possible.
- **Ingress**: charm uses `IngressPerAppRequirer` from `traefik_k8s` v2. Not exercised end-to-end (no Traefik deployed), but correctly declared.

## Observed behaviour

- `backend/0` and `backend/1` reach `active` cleanly when all relations are present.
- `juju exec --unit backend/0 -- curl http://localhost:30000/v1/version` → `{"version":"0.0.0+g5441e23"}` ✓
- OpenAPI at `/openapi.json` has 62 paths.
- **Config change** (`juju config backend hostname=...`): one `config-changed` hook fires; ~8s total; the charm restarts both `api` and `celery` workloads.
- **Redis relation broken**: `charms.redis_k8s.v0.redis`'s `RedisRequires._on_relation_broken` (`lib/charms/redis_k8s/v0/redis.py:58-62`) emits `redis_relation_updated`, which triggers `_on_config_changed`, which calls `_update_api_layer()` → `_celery_broker_url` → `sys.exit(0)` after setting `WaitingStatus("Waiting for redis relation")`. This is an indirect mechanism (no explicit `redis_relation_broken` handler exists) but works for the simple case.
- **Upgrade-charm hook**: runs `_migrate_database()` — correct. The `stop` → `upgrade-charm` → `config-changed` → `start` sequence is clean.
- `juju show-status-log` for `backend/0` shows clean state transitions across lifecycle events, except for the layer-interruption case below.
- **Backend charm has no unit tests.** Frontend has 5 passing unit tests (config validation + relation scenarios), using the deprecated `ops.testing.Harness` API (warnings emitted).
- **`sys.exit()` fires DURING Pebble layer updates** — the most serious finding. The status log for the redis-removal sequence shows:
  - `01:25:06`: `config-changed` → maintenance "Updating test-observer-api layer" → waiting "Waiting for redis relation" (sys.exit)
  - `01:25:13`: another `config-changed`, maintenance "Updating test-observer-api layer" persists until `01:26:27` (~74s) before flipping to waiting — the layer update was mid-flight when the exit fired
  - After a stop/start cycle: `api-pebble-ready` → maintenance "Updating test-observer-api layer" → idle → waiting "Waiting for redis relation"; `celery-pebble-ready` → maintenance "Updating celery-worker layer" → idle
  - Result: `kubectl exec <pod> -c api -- /charm/bin/pebble plan` → `{}` (empty). Both `api` and `celery` containers have no services running. The FastAPI app and Celery worker are offline despite the charm reporting `waiting`.
- **Actions when redis is absent**: `juju run backend/0 promote-user-to-admin email="nonexistent@test.com"` completed with `return-code: 0` and no results. `sys.exit(0)` fires during `_app_environment` evaluation before `container.exec()` runs, so the action script never executes and `event.set_results()` is never called — the action silently "succeeds" with no output.
- **Health check endpoints**: `/live` and `/ready` in `backend/test_observer/controllers/health/health.py` call `_ensure_local_client`, which rejects non-localhost clients with HTTP 403. Good practice.
- **`_get_frontend_url`** (`backend/charm/src/charm.py:805-808`): `relation.data[relation.app]` access is guarded by `if relation := self.model.get_relation(...)`, which is sufficient since `get_relation` returns `None` when absent. No bug here.

## Findings

### `sys.exit(0)` fires during Pebble layer updates, causing workloads to go offline
- **Severity**: critical
- **Kind**: bug / correctness
- **Where**: `backend/charm/src/charm.py:698-700` (`_celery_broker_url`), `backend/charm/src/charm.py:572-573` (`_postgres_relation_data`)
- **Evidence**: `_update_api_layer` sets `MaintenanceStatus("Updating ...")` (line 504) then calls `self.api_container.add_layer(...)` (line 509), which evaluates the `_api_pebble_layer` property, which evaluates `_app_environment`, which calls `_celery_broker_url`. When redis is absent, `_celery_broker_url` sets `WaitingStatus` and calls `sys.exit(0)` before `add_layer` completes. Status log for a live redis-removal: `01:25:06 maintenance "Updating test-observer-api layer"` → `01:25:06 waiting "Waiting for redis relation"`, and a subsequent occurrence where maintenance persisted 74s before flipping. Confirmed via `kubectl exec <pod> -c api -- /charm/bin/pebble plan` → `{}` on both containers.
- **Impact**: the workload goes offline immediately and the charm cannot recover on its own — it is stuck `waiting` with no services running, and re-relating redis does not fix it because the layers were never applied (in this environment, recovery was further blocked because the available `redis-k8s` revision did not provide the required interface). This is a complete application outage triggered by a relation change.
- **Fix**: check relation/database readiness *before* any Pebble layer work begins — move the redis-relation check into `_update_api_layer`/`_update_celery_layer` directly rather than deferring it to `_celery_broker_url` inside the `_app_environment`/`_api_pebble_layer` property chain. Replace `sys.exit()` with an early `return` from the handler after setting status.
- **Linter rule**: "do not call `sys.exit()` in a method invoked during Pebble layer construction"

### Action handlers silently succeed when preconditions are not met
- **Severity**: high
- **Kind**: bug
- **Where**: `backend/charm/src/charm.py:713-719` (`_on_delete_artefact_action`), `:722-731` (`_on_add_user_action`), `:733-746` (`_on_change_assignee_action`), `:748-759` (`_on_promote_user_to_admin_action`)
- **Evidence**: all four handlers call `self._app_environment` to build the `container.exec()` environment. When redis is absent, `_app_environment` → `_celery_broker_url` → `sys.exit(0)` fires before `container.exec()` runs. Observed: `juju run backend/0 promote-user-to-admin email="nonexistent@test.com"` returned `return-code: 0` with no results; `event.set_results()` was never called and the underlying script (which would raise `ValueError` for a non-existent user) never ran.
- **Impact**: operators cannot tell from the action result whether it ran, ran but had nothing to act on, or never ran. Confirmed silent no-op for `delete-artefact`; the other three actions are similarly reachable but were not individually confirmed to no-op beyond `promote-user-to-admin`.
- **Fix**: check precondition readiness (database, redis, migration status) in each action handler before calling `_app_environment`, and return an explicit failure result if the charm cannot act.
- **Linter rule**: "action handlers must check precondition readiness before calling `_app_environment`"

### Backend charm has zero unit tests
- **Severity**: high
- **Kind**: test-gap
- **Where**: `backend/charm/` — no `tests/` directory
- **Evidence**: `ls backend/charm/tests/` returns no such path. `.github/workflows/static-analysis-backend-charm.yml` only runs `ruff` and `codespell`, not pytest. The frontend charm, by contrast, has `frontend/charm/tests/unit/test_charm.py` with 5 scenario tests.
- **Impact**: the backend charm has complex state (migration coordination, peer databag, multi-container Pebble layers, action handlers, SAML validation, redis lifecycle) with no automated verification. Both critical bugs above would likely have been caught by unit tests.
- **Fix**: add `tests/unit/` using `ops.testing.Harness` or the `scenario` library, covering config validation, database/redis relation lifecycle (created/broken), migration coordination (leader vs follower), and all four actions under both healthy and degraded preconditions.
- **Linter rule**: "charm must have a tests/unit directory with at least one passing test"

### `delete-artefact` silently succeeds for non-existent artefacts
- **Severity**: medium
- **Kind**: bug
- **Where**: `backend/scripts/delete_artefact.py:26-27`, `backend/charm/src/charm.py:713-719`
- **Evidence**: the script does `artefact = session.get(Artefact, artefact_id); if artefact: session.delete(artefact); session.commit()` — a no-op if the artefact doesn't exist. The action handler then calls `event.set_results({"result": "Deleted successfuly"})` unconditionally. Observed: `juju run backend/0 delete-artefact artefact-id=99999` → `"Deleted successfuly"` even though no such artefact exists.
- **Impact**: an operator running the action with the wrong ID gets a false success message, either believing a nonexistent artefact was deleted or wrongly believing a real one was removed.
- **Fix**: raise `ValueError` in the script when `artefact is None`; let the error propagate or check the return value and fail explicitly in the handler.
- **Linter rule**: "action handler must not report success when the underlying operation had nothing to act on"

### `sessions_secret` config has no minimum-length validation
- **Severity**: medium
- **Kind**: ux
- **Where**: `backend/charm/charmcraft.yaml:95-96`
- **Evidence**: `sessions_secret` is `type: string` with no `min-length` constraint. `juju config backend sessions_secret="short"` is accepted without complaint.
- **Impact**: weak session secrets are cryptographically insecure; an operator following a quick-start guide could set a trivial secret and the charm would still report healthy.
- **Fix**: add `min-length: 32` to the option in `charmcraft.yaml`, or validate in `_on_config_changed` and set `BlockedStatus` for short secrets.
- **Linter rule**: "string config options used as cryptographic material must have a min-length constraint"

### `juju trust db --scope=cluster` required but undocumented
- **Severity**: medium
- **Kind**: ux
- **Where**: deployment procedure
- **Evidence**: `postgresql-k8s` (rev 925) fails to create k8s services without cluster-scoped trust; the error "Insufficient permissions, try: `juju trust db --scope=cluster`" only appears after deployment. `spread/integration/task.yaml` does not include this step (concierge grants it automatically). Neither `README.md` nor the charmhub description mentions it.
- **Impact**: an operator following the charmhub description alone cannot deploy successfully; the first deployment appears to stall indefinitely at "awaiting for cluster to start".
- **Fix**: document the trust requirement in the charm's README; consider a `CollectStatusEvent` check that detects and reports this state.
- **Linter rule**: not established

### "successfuly" typo in four action success messages
- **Severity**: low
- **Kind**: lint
- **Where**: `backend/charm/src/charm.py:719, 732, 746, 759`
- **Evidence**: `event.set_results({"result": "Deleted successfuly"})` and three similar calls. `codespell` flags: "successfuly ==> successfully".
- **Impact**: visible in action output; unprofessional but harmless.
- **Fix**: s/successfuly/successfully/
- **Linter rule**: codespell (already runs in CI, but these were missed)

### Bare `except Exception` in `version` property
- **Severity**: low
- **Kind**: lint
- **Where**: `backend/charm/src/charm.py:680`
- **Evidence**: `except Exception as e: logger.warning(f"Failed to get version: {e}")` — catches everything including `KeyboardInterrupt`, `SystemExit`, and `MemoryError`. The `version` property also makes an HTTP request to `http://0.0.0.0:{port}/v1/version` on every hook invocation.
- **Impact**: silently swallows serious errors (worst case is version stays unset); bad practice more than a live bug.
- **Fix**: `except (ConnectionError, TimeoutError, ValueError) as e:` to match the actual failure modes of a localhost HTTP call.
- **Linter rule**: ruff broad-except (tryceratops-style) would catch this

### `_app_environment` re-fetches database relation data on every call
- **Severity**: low
- **Kind**: performance
- **Where**: `backend/charm/src/charm.py:562`
- **Evidence**: `_app_environment` is a property calling `self._postgres_relation_data()` → `self.database.fetch_relation_data()` on every access; it's read from `_api_pebble_layer`, `_celery_pebble_layer`, and all four action handlers — including the celery layer path, which doesn't need DB data.
- **Impact**: negligible in practice, but wasteful and couples unrelated layers.
- **Fix**: cache the result locally, or split into `_api_environment`/`_celery_environment`.
- **Linter rule**: not established

### Frontend charm: `relation.data[relation.app]` unguarded access
- **Severity**: low
- **Kind**: bug
- **Where**: `frontend/charm/src/charm.py:234`
- **Evidence**: `relation_data = api_relation.data[api_relation.app]` — no guard for `api_relation.app is None`. The leader check protects most cases, but a `CollectStatusEvent` or relation-teardown race could expose this as a `TypeError`.
- **Impact**: potential traceback in a hook where a clean status would be expected. (unverified — not observed directly in testing)
- **Fix**: `if api_relation.app is None: return None` before the access.
- **Linter rule**: "access to `relation.data[relation.app]` requires guard `if relation.app is not None`"

### Frontend charm: `_api_url` triggers a side effect from a property
- **Severity**: low
- **Kind**: code smell
- **Where**: `frontend/charm/src/charm.py:143`
- **Evidence**: `_api_url` both returns a value and calls `self._handle_no_api_relation()` as a side effect when `api_relation is None`; callers then also check `if api_url: ... else: self._handle_no_api_relation()`, calling it twice in the failure path.
- **Impact**: confusing control flow; masks the ambiguity of `None` meaning "not connected" vs "error".
- **Fix**: have `_api_url` return `None` for "not connected" and let the caller decide whether to call `_handle_no_api_relation()`.
- **Linter rule**: not established

### Frontend charm: `ops.testing.Harness` is deprecated
- **Severity**: info
- **Kind**: tech-debt
- **Where**: `frontend/charm/tests/unit/test_charm.py:28,40`
- **Evidence**: pytest emits `PendingDeprecationWarning: Harness is deprecated`.
- **Impact**: the existing test harness will stop working in a future `ops` release.
- **Fix**: migrate to the `scenario` library (`Context`/`State`).
- **Linter rule**: not established

### README claims metrics on port 9000; code defaults to 9090
- **Severity**: low
- **Kind**: docs
- **Where**: `README.md:76` vs `backend/test_observer/common/config.py:36`
- **Evidence**: README says "The charm exposes metrics on port 9000". Code: `METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))`; `MetricsEndpointProvider` targets `["*:9090"]`.
- **Impact**: an operator following the README configures the wrong firewall port and gets confusing scrape failures.
- **Fix**: correct the README to 9090, or make the port configurable and keep the scrape target in sync.
- **Linter rule**: not established

### Both charm READMEs are near-empty
- **Severity**: low
- **Kind**: docs
- **Where**: `frontend/charm/README.md`, `backend/charm/` (absent)
- **Evidence**: `frontend/charm/README.md` is one paragraph pointing to charmhub.io; `backend/charm/` has no README at all.
- **Impact**: operators working from the local source have no per-charm config/relation reference.
- **Fix**: add READMEs covering config options, relation diagrams, deployment commands, and local development.
- **Linter rule**: not established

## Worth copying

- **Database migration coordination via peer databag** (`backend/charm/src/charm.py:155-175, 210-275, 290-330`): the leader runs alembic and publishes the applied revision and database relation id to the peer databag; followers wait for the published revision to match before starting workloads. Correct pattern for leader-distributed schema migrations, worth copying widely.
- **`WAITING_FOR_MIGRATION_MSG` constant for update-status backstop** (`backend/charm/src/charm.py:48`): a shared sentinel between `_migrate_database` and `_on_update_status` so the backstop can reliably distinguish "waiting for migrations" from other `WaitingStatus` states.
- **`_on_update_status` as a reconciliation loop** (`backend/charm/src/charm.py:288-317`): checks both "did the last migration fail?" and "do I need to reconcile layers?" before acting — the correct shape for a periodic backstop.
- **`CollectStatusEvent` for ingress conflict detection**: both charms detect conflicting ingress + nginx-route relations and report `BlockedStatus`, cleaner than a per-hook check.
- **SAML config validation on every hot path**: `_validate_saml_config()` is called from `_on_database_changed`, `_on_config_changed`, `_update_api_layer`, and `_update_celery_layer`, so misconfiguration blocks the workload rather than silently breaking SAML.
- **Frontend 503 fallback**: `frontend/charm/src/nginx_config.py` pushes a 503 nginx config and human-readable page when the API relation isn't connected — operator-friendly.
- **Pebble restart-on-failure**: uvicorn in the API container is Pebble-managed; killing the process results in automatic restart with no visible status change — correct k8s resilience pattern.
- **Health endpoints restrict to localhost**: `backend/test_observer/controllers/health/health.py` (`_ensure_local_client`) checks `request.client.host in {"127.0.0.1", "::1"}` and 403s remote clients.
- **`_database_relation_ready` as a non-exit-gating check** (`backend/charm/src/charm.py:381-387`): returns `bool` instead of raising `SystemExit`, letting hot-path callers check readiness without aborting the hook — the correct pattern, and it proves the `sys.exit()` elsewhere is unnecessary.

## Common-practice notes

- Both charms use `ops.CharmBase` and the modern `ops.pebble.Layer` API. ✓
- Both use `IngressPerAppRequirer` from `traefik_k8s` v2 with `strip_prefix=True`. ✓
- Backend charm uses `StoredState` for redis relation storage; deprecated in favour of `scenario`'s `State`, but not yet a problem.
- Charm libs are bundled under `lib/charms/` rather than fetched dynamically. ✓
- `charmcraft.yaml` uses `assumes: [juju >= 2.9, k8s-api]` — appropriate for a k8s charm. ✓
- `requires`/`provides` correctly model database (1), redis (1), ingress (1) constraints. ✓
- No machine substrate support — k8s-only, confirmed by the `containers:` key in `charmcraft.yaml`.
- No terraform module for the charms themselves (the repo's `terraform/` covers deployment management of the full system, not the charms).
- The frontend's `pytest-operator` integration test only checks that the charm reaches `maintenance` status; it does not verify behaviour — common but weak.
- Bundled library versions: `data_platform_libs/v0` (LIBPATCH 58), `grafana_k8s/v0` (LIBPATCH 49), `nginx_ingress_integrator/v0` (LIBPATCH 7), `prometheus_k8s/v0` (LIBPATCH 58), `redis_k8s/v0` (LIBPATCH 7), `traefik_k8s/v2` (LIBPATCH 20).
- `spread/integration/task.yaml` pins `redis-k8s --revision=27`; the latest `redis-k8s` (rev 42) does not provide the `redis` interface the charm requires, so the charm cannot be related to latest redis-k8s. This is an undocumented deployment constraint, and it directly blocks recovery from the layer-interruption bug above (re-relating with rev 42 fails).

## Tests

**Frontend charm unit tests** (`frontend/charm/tests/unit/test_charm.py`): 5 tests covering config validation (invalid port, invalid scheme, empty hostname, valid YAML frontend-config) and relation lifecycle. All pass, using the deprecated `ops.testing.Harness` API (`PendingDeprecationWarning`).

**Backend charm unit tests**: none. CI only runs `ruff check` and `codespell` on the backend charm.

**Static analysis**: `ruff check` passes on both charms. `codespell` finds 4 instances of "successfuly" in `backend/charm/src/charm.py` (lines 719, 732, 746, 759).

**Integration tests** (`spread/integration/task.yaml`): uses spread with concierge/microk8s, deploying postgresql-k8s, redis-k8s (rev 27), then both charms from locally-packed `.charm` files. Does not include `juju trust db --scope=cluster` (concierge handles it). Checks that both charms reach idle, then runs the `add-user` action and verifies the user was added to the database (a real assertion, not just a status wait). The task relates redis before database, with a comment noting "we seem to need to relate redis before the database until the charm is updated to handle the relations and app environment variables more gracefully" — direct acknowledgement of the fragility behind the critical finding above.

**Test coverage gaps relative to risks found**: the `sys.exit(0)` paths in `_celery_broker_url` and `_postgres_relation_data`, action-handler behaviour under missing preconditions, `delete-artefact`'s no-op-on-missing-artefact, and multi-unit peer-databag leader coordination are all untested. Only `add-user` is exercised in CI (via integration test); `delete-artefact`, `change-assignee`, and `promote-user-to-admin` are not.

## Docs

**README.md (repo root)**: good overview of system architecture; clear Docker Compose instructions for local development; explains the SimpleSAMLPHP setup; clear charm integration test instructions.

**Charm READMEs**: `frontend/charm/README.md` is one paragraph pointing to charmhub.io; `backend/charm/` has no README. Operators working from local source have no per-charm reference.

**Charmhub descriptions**: both charms have identical descriptions describing the overall Test Observer system rather than what each specific charm provides — an operator can't tell from the charm page what relations it needs.

**`docs/`**: Sphinx docs cover authentication, release management, reviewer assignment, test execution lifecycle, tutorial, and how-tos. Well-structured, though the tutorial assumes the Docker Compose environment rather than a Juju deployment.

**README metrics port mismatch**: `README.md:76` says port 9000; code defaults to 9090 (see Findings).

**Open issue #834**: "Test Observer charm should demo endpoint validators" — suggests adding a `validate` action for the postgresql_client interface. Not implemented.

## Open questions

1. **Leader election race for peer databag writes**: `_update_frontend_relation_data` and `_set_migration_status` both check `self.unit.is_leader()`. If leadership changes between the check and the write, the write is silently dropped — standard Juju behaviour, but worth flagging in a multi-unit context.
2. **Why backend rev 380 vs frontend rev 256?** Independently versioned charms; the backend was additionally upgraded to edge rev 387 mid-review.
3. **Could `alembic upgrade heads` run against a stale DB_URL?** No — `_postgres_relation_data` is called once per `_migrate_database` invocation and the result passed via environment to the alembic process.
4. **Can the charm recover from the empty-Pebble-plan state?** Attempted: removed redis, redeployed redis-k8s, tried `juju relate backend redis` again. Relation creation failed because the latest redis-k8s (rev 42) doesn't provide the `redis` interface the charm needs. Recovery required the correct revision (rev 27, as pinned in spread tests) — meaning the charm can land in a state it cannot recover from without operator intervention and specific knowledge of the interface-version constraint.
