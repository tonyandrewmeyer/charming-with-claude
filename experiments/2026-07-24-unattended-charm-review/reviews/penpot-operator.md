# penpot-operator

A Kubernetes charm for Penpot (open-source design tool), built by Canonical IS DevOps. It manages a multi-service OCI image (nginx frontend, Clojure/JVM backend, Node.js exporter) under Pebble, with integrations for PostgreSQL, Redis, S3, Ingress, SMTP, OAuth, and logging, plus COS metrics/dashboards. Code quality is good — holistic reconciliation, clean `_check_ready()`/`_reconcile()` separation, all linters pass, all 13 unit tests pass. But the charm has a confirmed, reproducible race condition that causes a real crash loop whenever the redis relation is removed and restored, plus several correctness gaps around secrets and error handling, and two documentation errors that will break a new operator's first attempt. The unit test suite passes cleanly only because it never exercises the paths that failed in deployment (redis race, timeout path, blocked paths — 76% coverage, all failure branches uncovered). A maintainer should fix the redis race first (it's a real production outage trigger), then close the test gap so it can't regress silently.

| | |
|---|---|
| Repo | canonical/penpot-operator @ `85243e0` (2026-07-21) |
| Charms | penpot |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3, charmhub edge rev 81 |
| Reviewed | 2026-08-31 |

## What it does

Deploys Penpot on Kubernetes using a Pebble-managed multi-service OCI image. Provides 7 integrations (postgresql, redis, s3, ingress, smtp, oauth, logging) and 2 monitoring integrations (metrics-endpoint, grafana-dashboard). Uses a peer relation for shared secret storage and exporter-unit election. Follows the holistic reconciliation pattern: nearly all events trigger `_reconcile()`.

## Deployment log

```
juju add-model rv-penpot-2 --controller concierge-k8s-3

juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy redis-k8s --channel latest/edge
juju deploy traefik-k8s --channel latest/edge --trust
juju deploy s3-integrator --channel 1/stable
juju deploy smtp-integrator --channel latest/stable
juju deploy self-signed-certificates --channel latest/stable --trust
juju deploy minio --channel ckf-1.9/stable --config access-key=minioadmin --config secret-key=minioadmin

juju config s3-integrator bucket=penpot endpoint="http://minio-endpoints.rv-penpot-2.svc.cluster.local:9000"
juju run s3-integrator/0 sync-s3-credentials access-key=minioadmin secret-key=minioadmin
juju config smtp-integrator host=mailhog.local domain=example.com
juju config traefik-k8s juju-external-hostname=penpot.local kubernetes-ingress-ssl-redirect=true

juju integrate penpot postgresql-k8s
juju integrate penpot redis-k8s
juju integrate penpot s3-integrator
juju integrate penpot:smtp smtp-integrator:smtp
juju integrate penpot:ingress traefik-k8s
juju integrate self-signed-certificates:certificates traefik-k8s:certificates

juju deploy penpot --channel edge
```

Timeline (first deploy):
- 20:05:54 — penpot/0 deploys, starts agent
- 20:06:00 — blocked: waiting for all integrations
- 20:14:01–20:14:26 — relations established (postgresql, redis, s3, smtp, ingress)
- 20:27:04 — `penpot_pebble_ready` fires, reconcile starts services
- 20:32:xx — image pulled (~22 min from deploy)
- 20:33:07 — ingress URL updates to `https://10.43.45.0/rv-penpot-2-penpot`
- 20:33:17 — backend `/readyz` returns "OK"; unit goes `ActiveStatus`

Total deploy time ~27 minutes, dominated by the OCI image pull (large multi-service image: Clojure/JVM + Node.js + Playwright chromium + nginx).

## Observed behaviour

**Scale-up**: `juju add-unit penpot -n 1` → penpot/1 active in ~70s. penpot/0 (minimum unit ID) runs the exporter; penpot/1 does not. Correct.

**Scale-down**: `juju remove-unit penpot --num-units 1` → penpot/1 removed cleanly. `penpot_peer-relation-departed` fired on penpot/0; related charms (postgresql, redis, s3, smtp, ingress) all received `*-relation-departed` and stayed `ActiveStatus`. Peer relation data preserved, secret ID intact. ✅

**Actions**: `create-profile email=X fullname=Y` ran successfully, returned a generated password. ✅ `delete-profile email=nonexistent@example.com` ran without error and with no failure feedback for a nonexistent user. ⚠️

**COS integrations**:
- Metrics confirmed at `http://localhost:6060/metrics` (JVM metrics such as `jvm_classes_loaded`, `jvm_buffer_pool_*`); `MetricsEndpointProvider` uses `targets: ["*:6060"]`. ✅
- Grafana dashboard (`src/grafana_dashboards/penpot.json`) uses `${prometheusds}` and `juju_topology` variables correctly; data confirmed on the requirer side of the relation. ✅
- Loki (`LogForwarder`) initialized in `__init__`, standard pattern, no special charm code. ✅
- `juju integrate penpot:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer` establishes the relation and penpot's dashboard data is confirmed present on grafana-agent-k8s's side, but grafana-agent-k8s itself shows `BlockedStatus("Missing ['grafana-cloud-config']|['grafana-dashboards-provider']")` — expected, since grafana-agent-k8s needs a full COS stack (Grafana + Prometheus) not deployed here, but also an interface mismatch (see findings).

**Teardown** (`juju remove-application penpot`): `relation-broken` fired on grafana-agent-k8s (departed 21:41:31, broken 21:41:32), which recovered its dashboard state. All other related charms stayed `ActiveStatus`, no orphan `relation-broken` visible. Peer secret (`vir6cgoingo7dqefr4hg`) was cleaned up automatically by Juju. ✅ Controller scaled penpot to 0 and removed the dead unit cleanly. ✅

**Failure injection — redis removal (stable state)**: `juju remove-relation penpot redis-k8s` → `BlockedStatus("waiting for redis")` in <5s, all services stopped cleanly. ✅

**Failure injection — redis restore (race condition confirmed)**: `juju integrate penpot redis-k8s` after stable removal produced a crash loop. Confirmed event ordering from `debug-log`:
```
20:49:48  redis-relation-broken   on penpot     → backend stopped
20:49:58  redis-relation-created  on penpot     → backend starts (stale relation data)
20:49:59  redis-relation-created  on redis-k8s
20:50:00  redis-relation-joined   on redis-k8s
20:50:00  redis-relation-changed  on redis-k8s  → redis-k8s writes hostname/port data
20:52:02  redis-relation-joined   on penpot     ← 2+ MINUTE DELAY
20:52:03  penpot-pebble-check-failed            ← backend already crashed
```
Backend started at 20:49:58 with a redis URI containing `port=None`. Confirmed from the pod:
```
PENPOT_REDIS_URI: redis://redis-k8s-0....svc.cluster.local:None
```
Pebble backoff is 5 minutes; recovery only happened when a coincidental `config-changed` hook regenerated the pebble plan with the correct port.

**Failure injection — S3 removal during redis-unstable state**: with the backend already in the redis crash loop, `juju remove-relation penpot s3-integrator` → `ErrorStatus` (crash loop) on both pods; the stale `port:None` pebble plan made the crash loop worse rather than transitioning to `BlockedStatus`. ⚠️

**Failure injection — backend kill**: `kubectl exec penpot-0 -- pebble stop backend` → backend went `inactive`, but **Juju status remained `ActiveStatus`** — no mechanism detected the crashed workload. Backend auto-recovered after ~30s when a `config-changed` hook triggered reconcile. ⚠️

**Failure injection — bad config value**: `juju config penpot smtp-from-address="not-an-email"` → `WaitingStatus` during restart, then `ActiveStatus`. No validation, but graceful recovery, no crash. ✅

**`juju refresh`**: `juju refresh penpot --channel edge` → "already up-to-date" (rev 81 = HEAD); no newer revision available to test upgrade path.

**Memory usage**: penpot pod at 1098 MB RAM idle — high but expected for JVM + Node.js + Playwright.

**Linting**: `ruff check` ✅, `bandit` ✅, `mypy` ✅, `codespell` ✅. `charmcraft analyze penpot_amd64.charm` reports an entrypoint error (see findings).

## Findings

### Redis relation-restore race causes a 5-minute crash loop

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:336-340` (`_get_redis_credentials()`), `src/charm.py:260` (`_check_ready()` requirements dict)
- **Evidence**: On redis relation restore, `redis-relation-created` fires on penpot at 20:49:58 while `redis-relation-joined` on penpot doesn't fire until 20:52:02 — a 2+ minute gap in which the backend is started with stale/partial data. `_get_redis_credentials()` reads `relation_data = self.redis.relation_data`; when the relation exists but `port` has not yet been written, `lib/charms/redis_k8s/v0/redis.py`'s `url` property renders `f"redis://{redis_host}:{redis_port}"` with `port=None`, producing the literal string `"None"`. The resulting dict is non-empty and truthy, so `_check_ready()` returns `True` and `_reconcile()` starts the backend with `PENPOT_REDIS_URI=redis://...cluster.local:None`. Confirmed from pod: `PENPOT_REDIS_URI: redis://redis-k8s-0....svc.cluster.local:None`, followed by pebble entering 5-minute backoff.
- **Impact**: Any `juju remove-relation` + `juju integrate` cycle on redis (planned maintenance, network glitch) causes a real ~5-minute outage.
- **Fix**: In `_get_redis_credentials()`, treat a missing/`None` port as "not ready" (e.g. `if not relation_data.get("port"): return {}`). Also guard `_reconcile()` to skip `container.start()` when redis credentials are incomplete.
- **Linter rule**: custom ruff rule flagging `self.redis.url` access without a preceding check of `relation_data.get("port")`.

### Duplicate secrets possible on partial leader write

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:292-297` (`_get_penpot_secret_key()`)
- **Evidence**:
  ```python
  if secret_id is None:
      if self.unit.is_leader():
          new_secret = {"penpot-secret-key": secrets.token_urlsafe(64)}
          secret = self.app.add_secret(new_secret)
          secret.set_content(new_secret)
          peer_relation.data[self.app]["secrets"] = typing.cast(str, secret.id)
  ```
- **Impact**: If the leader creates the secret via `add_secret()`/`set_content()` but the peer-relation write fails (network partition, controller error), no secret ID is stored. The next reconcile finds `secret_id is None` again and creates another secret, accumulating orphaned secrets.
- **Fix**: Scan for an existing secret via `model.get_secret(label=...)` before creating a new one, or wrap the peer-data write in a retry loop.
- **Linter rule**: not mechanically checkable — requires transactional reasoning.

### 120-second blocking wait in `_reconcile` risks hook queuing

- **Severity**: high
- **Kind**: performance
- **Where**: `src/charm.py:156-165` (`_reconcile()` busy-wait loop)
- **Evidence**:
  ```python
  deadline = time.time() + 120
  self.unit.status = ops.WaitingStatus("waiting for penpot services")
  while time.time() < deadline:
      if self._check_penpot_backend_ready():
          self.unit.status = ops.ActiveStatus()
          return
      time.sleep(3)
  self.unit.status = ops.BlockedStatus("timeout waiting for penpot services")
  ```
- **Impact**: A synchronous busy-wait inside a hook handler. Within the 5-minute Juju hook timeout, but it delays processing of subsequent relation/config events during startup, causing hook queuing and delayed status updates on busy clusters.
- **Fix**: Rely on the existing `backend-ready` Pebble check (defined around `src/charm.py:228`) with `container.replan()`, set `WaitingStatus` once, and let the periodic Pebble check drive the transition to `ActiveStatus` via a separate handler or deferred event.
- **Linter rule**: not mechanically checkable.

### S3 removal during redis crash loop escalates to ErrorStatus instead of BlockedStatus

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:148-155` (`_reconcile()`)
- **Evidence**: With the backend already in the redis `port:None` crash loop, removing S3 (`juju remove-relation penpot s3-integrator`) triggers another reconcile; `_check_ready()` returns `False`, the pebble plan is regenerated (still with `port:None`), `container.stop()` then `container.start()` run, and the backend crashes immediately without S3 — Pebble enters backoff and the charm shows `ErrorStatus` rather than `BlockedStatus`.
- **Impact**: A transient disruption to one relation (redis) leaves the charm fragile to a subsequent, unrelated disruption (S3): a healthy-looking removal turns into a crash loop instead of a clean blocked state.
- **Fix**: When `_check_ready()` returns `False`, ensure the pebble plan reflects the absence of all missing dependencies' env vars, or detect an already-unhealthy backend before attempting stop/start.
- **Linter rule**: not mechanically checkable.

### Unit tests never exercise the redis race condition

- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py:80-84`, `tests/unit/test_charm.py`
- **Evidence**: The `redis_relation()` fixture supplies `remote_units_data={0: {"hostname": "redis-hostname", "port": "6379"}}` immediately and completely, so `_get_redis_credentials()` always returns a valid URL in tests. `test_redis_config` asserts `backend_env["PENPOT_REDIS_URI"] == "redis://redis-hostname:6379"`, which never touches the `relation-joined`-before-`relation-changed` window or a `port=None` value. The fixture itself correctly represents complete relation data; the gap is that no test simulates the incomplete/race state that occurs in production.
- **Impact**: The suite passes while the exact failure observed in deployment (backend start with `port=None`) is untested and could regress silently.
- **Fix**: Add a test that simulates `relation-joined` before `relation-changed` (or with `port=None` in the fixture) and asserts `_check_ready()`/backend start is refused until real port data is present. Add a full-cycle test: create relation → backend starts only after complete data is available.
- **Linter rule**: coverage-based check flagging failure-mode branches with near-zero test coverage.

### Backend crash invisible without a coincidental hook

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` (no Pebble-check observer)
- **Evidence**: `kubectl exec -- pebble stop backend` made the backend `inactive`, but Juju status remained `ActiveStatus` for ~30 seconds until an unrelated `config-changed` hook triggered `_reconcile()` and restarted it. The `backend-ready` Pebble check runs every 30s but does not itself generate a Juju hook event.
- **Impact**: A backend crash (OOM, segfault, bad config) is invisible to the charm unless something else happens to trigger a reconcile; the workload can be down while status shows green.
- **Fix**: Use `container.replan()` instead of `container.start()` so Pebble auto-restarts crashed services, and/or add a `pebble-check-failed` observer that triggers reconcile.
- **Linter rule**: static-analysis rule flagging Pebble health checks with no corresponding hook-event observer.

### Unguarded `secret.get_content()` can raise unhandled exceptions

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:301` (`_get_penpot_secret_key()`), `src/charm.py:372` (`_get_smtp_credentials()`)
- **Evidence**: Both call `secret.get_content(refresh=True)` with no `try`/`except`. If the secret is deleted from Juju's store, this raises `ops.SecretNotFoundError`/`ops.SecretReadError`, propagating as an unhandled exception through the reconcile loop and failing the hook with a traceback.
- **Impact**: A deleted secret produces a traceback instead of a clean, actionable `BlockedStatus`.
- **Fix**: Wrap `get_content()` in `try`/`except (ops.SecretReadError, ops.SecretNotFoundError)` and return `{}` or set `BlockedStatus` with a clear message.
- **Linter rule**: custom ruff rule flagging unhandled `SecretReadError`/`SecretNotFoundError` from `secret.get_content()`.

### SMTP password silently falls back to plaintext relation data

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:367-372`
- **Evidence**:
  ```python
  if smtp_data.password:
      smtp_credentials["PENPOT_SMTP_PASSWORD"] = smtp_data.password
  if smtp_data.password_id:
      password_secret = self.model.get_secret(id=smtp_data.password_id)
      password_secret_content = password_secret.get_content(refresh=True)
      smtp_credentials["PENPOT_SMTP_PASSWORD"] = password_secret_content["password"]
  ```
- **Impact**: If `get_content()` fails (secret deleted), the code has already fallen back to the plaintext password from relation data — meaning the password can be used in plaintext for the relation's lifetime if the secret read fails even once.
- **Fix**: If a secret ID is configured but `get_content()` fails, fail explicitly rather than silently using the relation-data fallback.
- **Linter rule**: not mechanically checkable — requires reasoning about exception flow.

### COS docs claim the wrong metrics port

- **Severity**: medium
- **Kind**: docs
- **Where**: `docs/how-to/integrate-with-cos.md:7`
- **Evidence**: Docs say metrics are exposed at `:9117/metrics`; code configures `"targets": ["*:6060"]` (`src/charm.py:61`) and `curl http://localhost:6060/metrics` in deployment showed JVM metrics there. Port 9117 is the `nginx-ingress-integrator` default, not Penpot's.
- **Impact**: An operator following the docs configures Prometheus to scrape the wrong port and sees no metrics.
- **Fix**: Correct the docs to `http://<penpot-unit-ip>:6060/metrics`.
- **Linter rule**: not mechanically checkable.

### Tutorial uses invalid `s3-integrator` config syntax

- **Severity**: medium
- **Kind**: docs
- **Where**: `docs/tutorial/getting-started.md:36`
- **Evidence**: Tutorial shows `juju deploy s3-integrator --config "endpoint=..." --config bucket=penpot`. `endpoint` and `bucket` are not valid `juju config` options for `s3-integrator`; they come via the relation, and credentials are set via the `sync-s3-credentials` action.
- **Impact**: A new operator following the tutorial hits a command failure and cannot proceed.
- **Fix**: Remove the invalid `--config` flags from the deploy command.
- **Linter rule**: not mechanically checkable.

### Grafana-agent-k8s dashboard relation blocked by interface mismatch

- **Severity**: medium
- **Kind**: bug
- **Where**: `charmcraft.yaml` (`grafana-dashboard` interface declaration)
- **Evidence**: `juju integrate penpot:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer` establishes a relation and penpot's dashboard data is confirmed present on grafana-agent-k8s's side, but grafana-agent-k8s shows `BlockedStatus("Missing ['grafana-cloud-config']|['grafana-dashboards-provider']")`. Penpot's `grafana-dashboard` endpoint uses interface `grafana_dashboard` (singular, for Grafana-in-a-charm); grafana-agent-k8s's `grafana-dashboards-consumer` endpoint expects `grafana_dashboards` (plural, COS bundle interface). These are different interfaces from different libraries.
- **Impact**: An operator integrating penpot with grafana-agent-k8s sees an apparently-connected but non-functional relation, and grafana-agent-k8s stays blocked regardless of what else is deployed.
- **Fix**: Document that grafana-agent-k8s is not the correct COS partner for this endpoint (use a Grafana charm instead), or add a second `grafana-dashboards-consumer`/`grafana_dashboards` endpoint to also serve grafana-agent-k8s.
- **Linter rule**: not mechanically checkable.

### Unit tests skip blocked/timeout/failure paths

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py`
- **Evidence**: All 13 tests monkeypatch `_check_penpot_backend_ready` to `True` and assert `ActiveStatus`. Coverage is 76% for `src/charm.py`; none of the `BlockedStatus` paths, the 120s timeout path, or relation-removal paths are exercised.
- **Impact**: The most consequential behaviours — what happens when dependencies are missing or the backend fails to start — are entirely untested.
- **Fix**: Add tests for: missing postgresql → `BlockedStatus`; missing ingress HTTPS → `BlockedStatus`; `_check_penpot_backend_ready` returning `False` for 120s → `BlockedStatus("timeout...")`; relation broken while running → `BlockedStatus`; redis relation present with incomplete data → `BlockedStatus`.
- **Linter rule**: coverage-based rule flagging functions with early-return paths not covered by tests.

### `delete-profile` action succeeds silently for nonexistent users

- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py` (action handler)
- **Evidence**: `juju run penpot/0 delete-profile email=nonexistent@example.com` returned success with no error message, even though the user does not exist.
- **Impact**: An operator gets no feedback and cannot tell whether the user existed prior to the call.
- **Fix**: Check existence before deletion and return an explicit not-found error/message.
- **Linter rule**: not mechanically checkable.

### `_get_penpot_exporter_unit()` recomputed on every reconcile by every unit

- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:463`
- **Evidence**: Called from `_reconcile()` on every reconcile by every unit; accesses the peer relation and sorts all units, O(N log N) per reconcile per unit.
- **Impact**: Unnecessary repeated work on every hook for all but the minimum unit.
- **Fix**: Cache the result in `StoredState`, recomputing only on peer-relation-changed/departed events.
- **Linter rule**: not mechanically checkable.

### DNS resolution repeated on every reconcile

- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:443-451`
- **Evidence**:
  ```python
  def _get_local_resolver(self) -> str:
      kube_dns = f"kube-dns.kube-system.svc.{self._get_kubernetes_cluster_domain()}"
      try:
          dns.resolver.resolve(kube_dns, search=True)
          return kube_dns
  ```
  Called on every `_reconcile()`.
- **Impact**: A DNS query on every reconcile for a value that is effectively static for the pod's lifetime.
- **Fix**: Compute once in `__init__` or cache in `StoredState`.
- **Linter rule**: custom ruff rule flagging network calls in a hot path.

### Undocumented `# nosec` suppression on OAuth config

- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:517`
- **Evidence**: `token_endpoint_auth_method="client_secret_post",  # nosec  # noqa: S106`
- **Impact**: The suppression is likely correct (this is a config value, not a secret), but there's no comment explaining why `client_secret_post` is the right choice, making the suppression hard to audit later.
- **Fix**: Replace the bare `# nosec` with a comment explaining that `client_secret_post` is the standard OAuth2 method for this integration.
- **Linter rule**: bandit S106 suppression without an accompanying explanation — checkable with a custom rule.

### `charmcraft analyze` reports a missing entrypoint

- **Severity**: nit
- **Kind**: lint
- **Where**: `charmcraft.yaml` / generated dispatch script
- **Evidence**: `charmcraft analyze penpot_amd64.charm` → `[ERROR] Cannot find the entrypoint file: '.../${dispatch_path}/src/charm.py'` — the analyzer doesn't resolve `${dispatch_path}` in the generated dispatch script.
- **Impact**: If CI runs `charmcraft analyze`, an ERROR exit code would fail the build.
- **Fix**: Add an explicit `entrypoint: src/charm.py` to `charmcraft.yaml`, or ensure `dispatch` points to a static script with a literal entrypoint path.
- **Linter rule**: mechanical — run `charmcraft analyze` in CI.

## Worth copying

- Clean separation between `_check_ready()` (computes requirements, sets `BlockedStatus`) and `_reconcile()` (stops/starts services) — makes adding new prerequisites trivial.
- The `backend-ready` Pebble check (`'bash -c "pebble services backend | grep -q inactive || curl -f -m 5 localhost:6060/readyz"'`) handles both service-state and HTTP health via the pipe-in-exec pattern.
- Scenario-based unit testing with `ops.testing` and reusable fixture factories (`penpot_container()`, `postgresql_relation()`, etc.) — readable and maintainable.
- Peer-relation app data used as the secret-ID store alongside `app.add_secret` — the correct modern secrets pattern (subject to the duplicate-secret race noted above).
- COS grafana dashboard uses the default `dashboards_path`, `${prometheusds}`, and `juju_topology` variables correctly. ✅
- Metrics scrape config (`targets: ["*:6060"]`) correctly matches the backend's actual metrics port. ✅
- Upgrade docs correctly instruct backing up the database first.
- `test_oauth_login` integration test uses Playwright for full browser-based OIDC validation — the right level of testing for auth.

## Common-practice notes

- Follows ecosystem norms: `ops.CharmBase`, holistic reconciliation, Pebble, `ops.testing`, canonical CI workflows, `uv`, `ruff`/`bandit`/`mypy`.
- No `dispatch`/`entrypoint` field in `charmcraft.yaml` — relies on generated dispatch, which is what breaks `charmcraft analyze`.
- Uses standard `cosl`-adjacent libraries (`charms.grafana_k8s...`, `charms.prometheus_k8s...`, `charms.loki_k8s...`) and `data_platform_libs.v0.data_interfaces` for PostgreSQL, consistent with other Canonical k8s charms.
- `# pragma: nocover` on `_check_penpot_backend_ready` is justified (requires a live HTTP endpoint), but the consequence is that the 120s timeout path in `_reconcile` is also uncovered.
- `target-version = "py310"` in ruff vs. `requires-python = ">=3.12"` in `pyproject.toml` — inconsistent, not currently causing problems.
- Integration tests pin charm revisions (`POSTGRESQL_REVISION = 774`, `REDIS_REVISION = 42`, etc.), which may drift from charmhub over time.
- `create-profile` returns a generated password — good practice; `delete-profile` lacks feedback for nonexistent users (see findings).
- Exporter election uses the minimum-unit-ID pattern with self-healing (stop everywhere, start on the minimum) — race-free by design, separate from the redis race.
- `_reconcile()` is triggered on `upgrade_charm`, ensuring the pebble plan regenerates after upgrade.

## Tests

**Unit**: 13 tests, all passing. Run with `PYTHONPATH=src:lib:. uv run pytest tests/unit/ -v`. Coverage 76% for `src/charm.py`; missing: all blocked paths, the timeout path, relation-broken, the redis race (`port=None`), secret-error paths, OAuth paths. Bandit: 0 issues. Uses `ops.testing.Context`/`testing.State` with good fixture design.

**Integration**: 2 tests (`test_create_profile`, `test_oauth_login`), requiring `--charm-file`/`--penpot-image`, using `jubilant` and `playwright`. No integration test for relation removal/restore, the redis race, or crash-loop recovery. The OAuth test is comprehensive — full browser-based OIDC flow with CA injection into the Java trust store.

**Static analysis**: `ruff check` ✅, `bandit` ✅, `mypy` ✅, `codespell` ✅, `charmcraft analyze` ⚠️ entrypoint error (see findings).

## Docs

- **README.md**: accurate and complete; deployment instructions match what was verified in deployment.
- **Tutorial** (`docs/tutorial/getting-started.md`): invalid `s3-integrator` deploy command (`--config endpoint=... --config bucket=...`); also references `nginx-ingress-integrator` while modern deployments use `traefik-k8s`.
- **COS integration** (`docs/how-to/integrate-with-cos.md`): wrong metrics port (`:9117` vs. actual `:6060`).
- **Upgrade docs**: correctly instruct backing up the database first.
- **SSO docs**: correctly describe `juju integrate penpot:oauth hydra`; link out to the Canonical IAM bundle tutorial.
- **Architecture docs**: comprehensive C4 diagrams explaining the holistic pattern.

## Open questions

1. Does a new leader find the existing peer secret via `peer_relation.data[self.app].get("secrets")` after a leadership handover, or create a duplicate? App-scoped peer data should persist across leadership changes, but this hasn't been tested with a real handover.
2. Does `juju refresh` handle an in-place OCI image upgrade without data loss? Not covered explicitly in the upgrade docs, and no newer revision was available to test against.
3. The exporter uses Playwright/Chromium for PDF export with no visible rate limiting or concurrency control — could this exhaust memory at scale? (unverified)
4. Should `smtp-from-address` validate email format, given the charm currently accepts any string silently?
5. Is `delete-profile`'s silent success for a nonexistent user intentional (idempotent deletion) or a bug?
