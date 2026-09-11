# discourse-k8s

A mature, feature-rich Kubernetes charm for deploying Discourse. Code quality is generally high — clean reconciler pattern, good separation of concerns (`DatabaseHandler`, `OAuthObserver`), strong config validation, and solid observability wiring (Prometheus, Loki, Grafana). Deployment is smooth, and the charm recovers cleanly from relation removal, scaling, and crashes of the main unicorn process.

The two things a maintainer should fix first: (1) `_get_saml_config` can crash the charm with an uncaught `StopIteration`/`IndexError` on malformed SAML provider data, and (2) SAML relation validation is silently skipped until the next full setup cycle because relation-joined/created events aren't observed — an operator can end up "active" with an invalid SAML config. Beyond that: sidekiq/prometheus child-process death goes completely undetected (charm stays "active" while background jobs silently stop), `db:migrate` runs redundantly on every unit, every `config-changed` triggers a full Pebble replan even when nothing changed, and the >4GB OCI image (11-14 min pulls) is a real operational cost. Test suite and docs are strong (55 unit tests, 88% coverage, real-assertion integration tests, full Diátaxis doc set).

| | |
|---|---|
| Repo | canonical/discourse-k8s-operator @ 0e44652 (2026-07-20) |
| Charms | discourse-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), stable rev 277 and edge rev 288; concierge-k8s-4 (Juju 4.0.5), edge rev 288 (without DB — no Juju 4.x PostgreSQL charm exists) |
| Reviewed | 2026-08-09 |

## What it does

This charm deploys and manages a full Discourse forum on Kubernetes. It handles:

- **Workload**: Packages Discourse v2026.1.5 as a custom OCI image (built with Rockcraft) including Discourse core, multiple plugins (SAML, Prometheus, Signatures, Markdown Note, Mermaid Theme), and compiled assets
- **Database**: Requires PostgreSQL via the `postgresql_client` interface, runs Rails `db:migrate` on setup
- **Caching/queues**: Requires Redis for Sidekiq job processing
- **Ingress**: Requires nginx-route integration for external HTTP access
- **Observability**: Provides metrics-endpoint (Prometheus on port 3000), grafana-dashboard, and loki_push_api for log forwarding
- **Authentication**: Supports SAML (optional) and OAuth/OIDC integration
- **Storage**: Supports S3-compatible object storage for uploads, with migration support and optional backup bucket
- **Configuration**: 26 config options covering SMTP, S3, CORS, rate limiting, SAML, category nesting, and Sidekiq memory
- **Actions**: `create-user` (with optional admin/active flags), `promote-user-to-admin`, `anonymize-user`
- **Rolling restart**: Via the rolling-ops library on a peer relation, triggered on charm upgrade

## Deployment log

### Juju 3.6 deployment (rv-discourse2 — first review pass)
```
$ juju add-model rv-discourse2 --controller concierge-k8s-3
$ juju deploy discourse-k8s --channel stable          # revision 277
$ juju deploy postgresql-k8s --channel 14/stable       # revision 925
$ juju deploy redis-k8s --channel latest/edge          # revision 42
$ juju deploy nginx-ingress-integrator --channel stable # revision 203
$ juju deploy traefik-k8s --channel stable             # revision 377
$ juju deploy self-signed-certificates --channel stable # revision 586

# PostgreSQL needed juju trust for k8s service creation
$ juju trust postgresql-k8s --scope=cluster

# Relate
$ juju relate discourse-k8s postgresql-k8s
$ juju relate discourse-k8s redis-k8s
$ juju relate discourse-k8s nginx-ingress-integrator

# nginx-ingress-integrator got stuck waiting for ingress IP — no k8s nginx ingress
# controller on this microk8s cluster.

# Image pull took ~14 minutes (first pull), ~8 minutes (cached).
# After image pull + db:migrate: went directly to active, workload version 2026.1.5
```

### Juju 3.6 deep-dive deployment (rv-discourse3 — second review pass)
```
$ juju add-model rv-discourse3 --controller concierge-k8s-3
$ juju deploy discourse-k8s --channel stable          # revision 277
$ juju deploy postgresql-k8s --channel 14/stable       # revision 925
$ juju deploy redis-k8s --channel latest/edge          # revision 42
$ juju deploy nginx-ingress-integrator --channel stable # revision 203
$ juju deploy s3-integrator --channel stable            # revision 562 (blocked, no creds)
$ juju deploy self-signed-certificates --channel stable # revision 586

# Image pull took ~11 minutes. Setup completed, went to active.
```

### Juju 3.6 refresh test
```
$ juju refresh discourse-k8s --channel edge            # stable 277 → edge 288
→ Pod recreated (new IP from 10.1.0.39 to 10.1.0.21), rolling restart triggered.
→ Recovered to active within ~90s.
# Diff between 277 and 288: only docs/deps config files, no src/ changes.
# Yet the rolling restart still recreated the pod and re-ran the full setup.
```

### Juju 4.0 deployment (rv-discourse5)
```
$ juju add-model rv-discourse5 --controller concierge-k8s-4
$ juju deploy discourse-k8s --channel edge             # revision 288
$ juju deploy redis-k8s --channel latest/edge           # revision 42

# postgresql-k8s: 14/stable FAILS (requires Juju < 4.0.0)
# postgresql-k8s: 14/edge FAILS (requires Juju < 4.0.0)
# postgresql-k8s: 16/stable FAILS (requires Juju < 4.0.0)
# No PostgreSQL charm exists for Juju 4.x Kubernetes.

# discourse-k8s on Juju 4.x without database: correctly goes to
# "Waiting for database relation" status. Pebble plan has ONLY the
# rock base layer (discourse-setup-completed check, no services).
# Charm handles the missing relation cleanly.
```

### Juju 3.6 integration testing (rv-discourse6 — third review pass)
```
$ juju add-model rv-discourse6 --controller concierge-k8s-3
$ juju deploy discourse-k8s --channel edge             # revision 288
$ juju deploy postgresql-k8s --channel 14/stable
$ juju deploy redis-k8s --channel latest/edge
$ juju deploy self-signed-certificates --channel stable
$ juju deploy s3-integrator --channel stable
$ juju deploy saml-integrator --channel stable
$ juju deploy grafana-agent-k8s --channel 0.40/stable
$ juju relate discourse-k8s postgresql-k8s
$ juju relate discourse-k8s redis-k8s
→ Active after setup. s3_enabled=true without creds → blocked (correct).
$ juju config discourse-k8s s3_enabled=false  → active

# Add observability relations
$ juju relate discourse-k8s:logging grafana-agent-k8s:logging-provider
$ juju relate discourse-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
→ Both relations established, discourse-k8s stays active.
→ grafana-agent-k8s goes to blocked (no sink configured) — expected, not discourse's fault.

# Add SAML relation — saml-integrator blocked (no metadata configured)
$ juju relate discourse-k8s:saml saml-integrator
→ SAML relation established. discourse-k8s stays active — NO validation triggered.
→ Reason: saml-integrator has no app-level data, so saml_data_available event never fires.
→ _is_config_valid requires force_https=true when SAML relation exists, but validation
  is never called because the relation-joined event is not observed.

# Pod restart test (kubectl delete pod)
$ kubectl delete pod discourse-k8s-0
→ Pod recreated (new IP). Full setup re-runs, _is_config_valid now catches:
  "A saml relation cannot be specified without 'force_https' being true"
→ Charm goes to blocked. This SHOULD have been caught when SAML was first related.
$ juju config discourse-k8s force_https=true  → active again
```

### Failure injection
```
# Config validation — correctly blocks with actionable messages
$ juju config discourse-k8s force_saml_login=true
→ blocked: "force_saml_login cannot be true without a saml relation"
$ juju config discourse-k8s throttle_level=bananas
→ blocked: "throttle_level must be one of: none permissive strict"
$ juju config discourse-k8s s3_enabled=true
→ blocked: "'s3_enabled' requires 's3_access_key_id', ..."
$ juju config discourse-k8s s3_enabled=false  → back to active
$ juju config discourse-k8s throttle_level=none  → back to active

# Kill unicorn master — Pebble auto-restarts, charm stays active
$ kubectl exec discourse-k8s-0 -c discourse -- pkill -9 -f "unicorn master"
→ service back up within ~15s via Pebble auto-restart, charm never left active

# Kill sidekiq child process — NOT restarted (silent failure)
$ kubectl exec discourse-k8s-0 -c discourse -- pkill -9 -f sidekiq
→ sidekiq process stays dead, charm stays active, no pebble events
→ Discourse stops processing background jobs with no operator-visible signal
# Same behaviour for prometheus-collector — killed, not restarted

# Pebble stop — charm reports active while service is inactive
$ kubectl exec discourse-k8s-0 -c discourse -- pebble stop discourse
→ service inactive, charm shows active status
→ discourse-ready check has no on-check-failure action; service stays stopped

# Relation removal — correctly goes to waiting, stops service
$ juju remove-relation discourse-k8s redis-k8s
→ waiting "Waiting for redis relation"; Pebble service inactive
$ juju relate discourse-k8s redis-k8s  → recovers to active within ~30s

$ juju remove-relation discourse-k8s postgresql-k8s
→ waiting "Waiting for database relation"; Pebble service inactive
$ juju relate discourse-k8s postgresql-k8s  → recovers to active within ~60s

# Scale up/down
$ juju scale-application discourse-k8s 2  → second unit deploys, both active
$ juju scale-application discourse-k8s 1  → unit 1 removed, unit 0 stays active

# Trivial config change causes full replan + restart
$ juju config discourse-k8s developer_emails="test@test.com"
→ pebble services "Since" time updated — service restarted even though
  developer_emails doesn't affect service behaviour
```

### Actions
```
# create-user (non-admin) → returns password
$ juju run discourse-k8s/0 create-user email=test2@example.com
→ password: REDACTED, user: test2@example.com

# create-user (admin) → returns password
$ juju run discourse-k8s/0 create-user email=admin2@example.com admin=true
→ password: REDACTED, user: admin2@example.com

# create-user (duplicate) → fails with clear message
$ juju run discourse-k8s/0 create-user email=test2@example.com
→ failed: "User with email test2@example.com already exists"

# promote-user (nonexistent) → fails with clear message
$ juju run discourse-k8s/0 promote-user email=nonexistent@test.com
→ failed: "User with email nonexistent@test.com does not exist"

# anonymize-user → succeeds
$ juju run discourse-k8s/0 anonymize-user username=system
→ user: system
```

## Observed behaviour

| Metric | Value |
|---|---|
| Image pull time (fresh) | ~11-14 minutes (image layer >4GB — known issue #427) |
| Image pull time (cached) | ~8 minutes |
| Pod startup after image pull | ~60s to active (including db:migrate) |
| Container memory (1 unit) | ~1700-1950 MiB (unicorn master + 3 workers + sidekiq + prometheus) |
| Container memory (2 units) | ~1950 MiB each |
| Container CPU at idle | ~55-82m |
| Service user | `_daemon_` (UID 584792), not root |
| Hooks for trivial config change | 1 (config-changed → pebble replan → service restart) |
| Pebble plan checks | `discourse-ready` (HTTP `/srv/status`), `discourse-setup-completed` (rock-defined) |
| Workload restart on config change | Yes — every config-changed triggers `pebble.replan_services()` + service restart even when environment didn't change |
| Recovery from killed unicorn master | ~15s via Pebble auto-restart |
| Recovery from killed sidekiq | Never — Pebble monitors only the main script process, not children |
| Recovery from killed prometheus-collector | Never — same reason |
| Recovery from `pebble stop` | Never — charm stays active, no `on-check-failure` action configured |
| Scale-up from 1 to 2 | New unit builds full env, runs db:migrate, starts all services |
| Scale-down from 2 to 1 | Unit 1 removed cleanly, unit 0 stays active |
| Relation removal recovery | Stops service, re-relate brings both back to active |
| DB relation removal recovery | Stops service, re-relate brings back to active (~60s) |
| juju refresh (277→288, no code changes) | Pod recreated, rolling restart, full setup re-run (~90s) |
| Juju 4.x compatibility | Charm deploys cleanly on Juju 4.0.5, but no PostgreSQL charm exists for Juju 4.x Kubernetes across any channel (14/stable, 14/edge, 16/stable all refuse). The charm reaches "Waiting for database relation" cleanly with only the rock base layer in Pebble. |
| Pod restart (kubectl delete pod) | Pod recreated in ~20s, full setup re-runs (db:migrate + layer generation). Recovers to active ~20-30s after new pod starts. Re-validates config — this exposed the SAML relation gap (see below). |
| SAML relation with no provider data | `saml_data_available` event only fires when the SAML provider publishes non-empty app data. Adding a SAML relation with a blocked saml-integrator (no data) leaves the charm active even when config is invalid (`force_https=false`). Only caught on next full setup cycle (pod restart, upgrade). |
| Observability (grafana-agent-k8s) | Both logging and metrics-endpoint relations connect successfully. Charm stays active regardless of grafana-agent status. |
| Teardown (destroy-model) | Model destroyed cleanly — all 7 apps, 4 volumes, 4 filesystems cleaned up. No hangs or errors. |

**Pebble plan** (excerpt, from rv-discourse2/rv-discourse3/rv-discourse6 — consistent across all deployments):
```yaml
services:
  discourse:
    command: /srv/scripts/app_launch.sh
    user: _daemon_
    environment:
      DISCOURSE_DB_HOST: postgresql-k8s-primary.rv-discourse2.svc.cluster.local
      DISCOURSE_REDIS_HOST: redis-k8s-0.redis-k8s-endpoints.rv-discourse2.svc.cluster.local
      UNICORN_SIDEKIQ_MAX_RSS: "1000"
      RAILS_ENV: production
      HTTP_PROXY: ""
      HTTPS_PROXY: ""
      NO_PROXY: 127.0.0.1,localhost,::1     # ← NOT empty despite charm setting ""
      http_proxy: ""
      https_proxy: ""
      no_proxy: 127.0.0.1,localhost,::1     # ← NOT empty despite charm setting ""
      # DB_PASSWORD visible in plain text
      DISCOURSE_DB_PASSWORD: <visible>
      DISCOURSE_DB_USERNAME: <visible>
checks:
  discourse-ready:
    http: {url: http://localhost:3000/srv/status}
    # Note: no on-check-failure action configured
  discourse-setup-completed:
    exec: {command: ls /run/discourse-k8s-operator/setup_completed}
```

**Rock base layer** (`/var/lib/pebble/default/layers/001-rockcraft-discourse.yaml`):
```yaml
summary: Discourse rock
checks:
  discourse-setup-completed:
    override: replace
    level: ready
    exec:
      command: ls /run/discourse-k8s-operator/setup_completed
```
The rock base layer has NO services and NO environment variables — only the `discourse-setup-completed` check. The charm layer completely adds the service with `override: replace`.

**Runtime processes:**
```
_daemon_  unicorn master -c config/unicorn.conf.rb
_daemon_  sidekiq 7.3.9 app [0 of 5 busy]
_daemon_  discourse prometheus-collector
_daemon_  discourse prometheus-global-reporter
_daemon_  unicorn worker[0..2]
```

The `app_launch.sh` script (`discourse_rock/scripts/app_launch.sh`) simply execs `bin/unicorn -c config/unicorn.conf.rb`. Unicorn spawns sidekiq, prometheus-collector, and prometheus-global-reporter as child processes. Pebble monitors only the main process (unicorn master). If any child process dies, Pebble does not notice and does not restart it.

The `NO_PROXY` environment variable in the plan shows `127.0.0.1,localhost,::1` despite the charm setting it to `""` — this comes from Pebble's service environment merge behaviour, where empty-string values are treated as "inherit from parent process environment" (Pebble itself inherits its proxy settings from the container environment set by Kubernetes/Juju). Confirmed across two separate deployments (rv-discourse2 with rev 277 and rv-discourse3 with rev 288), both showing identical NO_PROXY leakage.

**Juju 4.x Pebble plan** (no database, no layer applied):
```yaml
checks:
  discourse-setup-completed:
    override: replace
    level: ready
    threshold: 1
    exec:
      command: ls /run/discourse-k8s-operator/setup_completed
```
Only the rock base layer; no services defined. The charm correctly avoids creating a layer when relations are not ready.

## Findings

Each `###` is one finding, most serious first.

### SAML `_get_saml_config` has unguarded `next()` and `certificates[0]` access
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:346` and `src/charm.py:354`
- **Evidence**:
  ```python
  # Line 346 — StopIteration if no SingleSignOnService with HTTP-Redirect binding
  sso_redirect_endpoint = next(
      e
      for e in relation_data.endpoints
      if e.name == "SingleSignOnService"
      and e.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
  )
  # Line 354 — IndexError if certificates tuple is empty
  certificate = relation_data.certificates[0]
  ```
  `_get_saml_config()` has no try/except. It's called from `_create_discourse_environment_settings()` (line 481), which is called from `_configure_pod()` and `_set_up_discourse()`. A SAML provider sending data with no `SingleSignOnService` endpoint of `HTTP-Redirect` type, or an empty certificates list, crashes the charm with an uncaught `StopIteration` or `IndexError` instead of reaching a clean BlockedStatus.
- **Impact**: A SAML provider that sends valid but differently-shaped data (e.g. only HTTP-POST binding, or an empty certificate list) causes `_configure_pod()` to traceback. The operator sees a hook error, not a status message, and every operation is blocked because `_create_discourse_environment_settings()` is called on every layer rendering.
- **Fix**: Wrap the `next()` call in `try/except StopIteration` and return `{}` or set BlockedStatus. Guard `certificates[0]` with a length check.
  ```python
  sso_endpoints = [e for e in relation_data.endpoints if ...]
  if not sso_endpoints:
      logger.error("SAML provider missing SingleSignOnService with HTTP-Redirect binding")
      return {}
  certificate = relation_data.certificates[0] if relation_data.certificates else None
  if not certificate:
      logger.error("SAML provider sent empty certificates")
      return {}
  ```
- **Linter rule**: Mechanically checkable — flag `next(generator)` without surrounding `try/except StopIteration` or a default argument in charm event handlers; flag `tuple_or_list[0]` access without a preceding length guard.

### SAML relation-joined/created events not observed — config validation bypassed when SAML relation added without app data
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/saml_integrator/v0/saml.py:298` (event only fires when app data is non-empty); `src/charm.py:310-313` (validation requires force_https when SAML relation exists)
- **Evidence**: `_is_config_valid()` at line 310 checks `self.model.get_relation(DEFAULT_RELATION_NAME) is not None` to enforce `force_https=true`. But `_on_config_changed` only runs on config changes, not relation changes. The only SAML event observed is `saml_data_available` (registered at `src/charm.py:97`), which the library only emits when `event.relation.data[event.relation.app]` is non-empty (saml.py line 298). When a SAML relation is first added and the provider hasn't published data yet, neither `relation_joined` nor `relation_created` is observed. Confirmed in rv-discourse6: adding the SAML relation to discourse-k8s while saml-integrator was blocked (no metadata) left discourse-k8s active with `force_https=false`. The invalid config was only detected after `kubectl delete pod` forced a full `_setup_and_activate()` cycle.
- **Impact**: An operator adding SAML integration gets no immediate feedback that `force_https=true` is required. The charm appears healthy with an invalid configuration until a full restart or upgrade triggers re-validation. The same gap exists for OAuth, though the OAuth observer at least observes `relation_created`.
- **Fix**: Observe `self.on["saml"].relation_joined` and `self.on["saml"].relation_created` and call `_configure_pod()` (or `_is_config_valid()` + status update) from those handlers. Apply the same fix to OAuth if not already covered.
- **Linter rule**: Mechanically checkable — `_is_config_valid` references `self.model.get_relation(X)` but no handler observing `relation_created`/`relation_joined` for X calls re-validation.

### Database migrations run on every unit, not just the leader
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:449-451` (in `_set_up_discourse`); confirmed by observing unit 1 running the same Pebble service set as unit 0
- **Evidence**: `_set_up_discourse()` calls `_execute_migrations()` unconditionally for every unit. The code comment (lines 465-469) acknowledges the migration is idempotent and concurrent-safe, hence "safe to run on all units" — true but wasteful. At 2 units, both run `db:migrate` on startup and on upgrade.
- **Impact**: At scale (open issue #298 discusses needing "quite a few Juju units"), every unit runs migrations on every deploy/upgrade, adding unnecessary database load and startup time. `rake db:migrate` acquires advisory locks, so concurrent runs serialize and waste time.
- **Fix**: Gate `_execute_migrations()` on `self.unit.is_leader()` in `_set_up_discourse()`. Non-leader units should wait for the leader to complete setup (e.g. via peer relation data) before proceeding. The existing `SETUP_COMPLETED_FLAG_FILE` is per-unit, not per-application.
- **Linter rule**: Mechanically checkable — flag `container.exec(..., ['rake', 'db:migrate'], ...)` calls not inside `if self.unit.is_leader()`.

### `NO_PROXY` from Pebble-inherited environment leaks into workload despite charm setting empty proxy vars
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:385-391` (charm setting) vs observed Pebble plan at runtime, confirmed across two deployments
- **Evidence**: The charm sets:
  ```python
  pod_config["HTTP_PROXY"] = pod_config["http_proxy"] = os.environ.get("JUJU_CHARM_HTTP_PROXY") or ""
  pod_config["HTTPS_PROXY"] = pod_config["https_proxy"] = os.environ.get("JUJU_CHARM_HTTPS_PROXY") or ""
  pod_config["NO_PROXY"] = pod_config["no_proxy"] = os.environ.get("JUJU_CHARM_NO_PROXY") or ""
  ```
  but the observed Pebble plan (rv-discourse2 and rv-discourse3) shows `NO_PROXY`/`no_proxy` as `127.0.0.1,localhost,::1`, not empty, while `HTTP_PROXY`/`HTTPS_PROXY` correctly show empty. The rock's base layer has no environment variables. The values come from Pebble's service environment merge: an empty-string layer value is treated as "inherit from parent process environment", and Pebble's own environment supplies a default `NO_PROXY` but no default `HTTP_PROXY`/`HTTPS_PROXY`.
- **Impact**: The observed `NO_PROXY` value silently differs from what the charm intends in the default (no-proxy) case — a hidden discrepancy between operator-configured proxy settings and what the workload actually sees.
- **Fix**: Always set `NO_PROXY` to a sensible explicit default (e.g. `127.0.0.1,localhost,::1`) rather than relying on Pebble's inherit-on-empty behaviour, or document the behaviour clearly.
- **Linter rule**: Not mechanically checkable (requires understanding Pebble environment merge semantics).

### Killing sidekiq or prometheus-collector child processes goes undetected — charm reports active while service is degraded
- **Severity**: medium
- **Kind**: bug
- **Where**: `discourse_rock/scripts/app_launch.sh` — execs `bin/unicorn`; unicorn spawns sidekiq and prometheus as child processes
- **Evidence**: `kubectl exec ... pkill -9 -f sidekiq` — process stayed dead permanently, charm remained "active" throughout. Pebble monitors only the main unicorn process, not children. Same behaviour for `pkill -9 -f prometheus-collector`. Confirmed via `pebble services` (active) and `ps aux` (process absent 15s+ later).
- **Impact**: If sidekiq dies (OOM, segfault, etc.), Discourse silently stops processing all background jobs — email sending, post processing, image resizing, user sync. The operator sees "active" status while the forum is degraded. If prometheus-collector dies, metrics silently stop being scraped.
- **Fix**: Add a Pebble health check that monitors sidekiq (e.g. a process/heartbeat check). Alternatively, wrap child processes under a supervisor, or split sidekiq into its own Pebble service.
- **Linter rule**: Not mechanically checkable.

### Redis relation data accessed without validating `relation.app` is not None
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:417` (`relation.data[relation.app]`)
- **Evidence**: In `_get_redis_relation_data()`:
  ```python
  relation = self.model.get_relation(self.redis.relation_name)
  if not relation:
      raise MissingRedisRelationDataError("No redis relation data")
  relation_app_data = relation.data[relation.app]
  ```
  The guard checks `relation` is not `None` but not `relation.app`. In a race between relation-broken and redis-relation-changed, `relation.app` can be `None`, producing an uncaught `TypeError: 'NoneType' object is not subscriptable` instead of the intended `MissingRedisRelationDataError`.
- **Impact**: During relation teardown races, the charm crashes with a hook error instead of handling the situation gracefully (blocked/waiting).
- **Fix**: Add `and relation.app` to the guard, or use the `RedisRequires.app_data` property (which has its own None checks).
- **Linter rule**: Mechanically checkable — flag `relation.data[relation.app]` patterns without a preceding `relation.app is not None` check.

### OAuth redirect_uri uses app name (not routable) when `external_hostname` is unset
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/oauth_observer.py:89-93` (`_generate_client_config`); `lib/charms/hydra/v0/oauth.py:87-94,277` (URL regex)
- **Evidence**: When `external_hostname` is empty, `_get_external_hostname()` returns `self.app.name` (e.g. "discourse-k8s"), producing `redirect_uri = https://discourse-k8s/auth/oidc/callback`. The OAuth library's URL regex requires a dotted domain or IP; "discourse-k8s" matches neither, so `ClientConfig.validate()` raises `ClientConfigError`, caught in `get_oidc_env()`, resulting in `BlockedStatus("Invalid OAuth client config, check the logs for more info.")`. Confirmed by unit test `test_oauth_integration[external_hostname not set]`; GitHub issue #413 confirms the same problem in production.
- **Impact**: The blocked-status message is not actionable — it doesn't tell the operator that setting `external_hostname` fixes the problem.
- **Fix**: Validate the hostname before generating the config; if it isn't a dotted domain or IP, block with a message that names `external_hostname` explicitly.
- **Linter rule**: Not mechanically checkable.

### Rock OCI image is >4GB — builds Ruby, Node, ImageMagick from source
- **Severity**: medium
- **Kind**: performance
- **Where**: `discourse_rock/rockcraft.yaml` — builds Ruby 3.3.8 from source (ruby-install), Node 22.12.0 from tarball, ImageMagick 7.1.2-3 from git source (400+ lines of build config), and runs full Rails asset precompilation at build time
- **Evidence**: Image pull times of 11-14 minutes observed across three deployments (rv-discourse2, rv-discourse3, rv-discourse6). Open issue #427 confirms this is known. The `imagemagick` part alone is ~180 lines with 20+ build-packages; the `discourse-precompile-assets` part starts a local PostgreSQL and runs `rake assets:precompile` at build time.
- **Impact**: Every fresh pull costs 11-14 minutes of downtime, compounding on pod restarts and each unit of a rolling upgrade.
- **Fix**: Multi-stage rock build — compile Ruby/Node/ImageMagick in a build stage and ship only the compiled binaries/libraries in the final image.
- **Linter rule**: Not mechanically checkable (build optimization).

### Juju 4.x gap: charm is compatible but its required database dependency is not
- **Severity**: medium
- **Kind**: docs / ops
- **Where**: `charmcraft.yaml` / metadata (charm declares `ubuntu@22.04` base)
- **Evidence**: `discourse-k8s` deploys and runs on Juju 4.0.5 (rev 277 on concierge-k8s-4), correctly reaching "Waiting for database relation". `postgresql-k8s` 14/stable rev 925 refuses: "charm requires Juju version < 4.0.0, model has version 4.0.5" — same for 14/edge and 16/stable.
- **Impact**: Operators on Juju 4.x clusters cannot use this charm end-to-end, because its required PostgreSQL dependency doesn't yet support Juju 4.x. This is invisible to operators until they try.
- **Fix**: Document Juju 4.x status explicitly. Test end-to-end once postgresql-k8s ships a Juju 4.x-compatible revision.
- **Linter rule**: Not mechanically checkable.

### Every config-changed triggers a Pebble replan even when nothing changed
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:928-935` (`_start_service` → `replan_services()`)
- **Evidence**: `_configure_pod()` unconditionally calls `_activate_charm()` → `_start_service()` → `container.add_layer(...)` + `container.pebble.replan_services()`, regardless of whether the effective configuration changed. `_config_force_https()` also runs unconditionally as a subprocess call. Observed: setting `developer_emails` (which doesn't affect service behaviour) still bumped the Pebble service "Since" time.
- **Impact**: Every `juju config` call causes a service replan and an extra Rails runner subprocess, even for config values that don't change the layer.
- **Fix**: Compare the new layer config against the current plan before calling `add_layer`/`replan_services`; only call `_config_force_https()` if `force_https` actually changed.
- **Linter rule**: Not mechanically checkable.

### `_stop_service` calls `container.stop(CONTAINER_NAME)` instead of `container.stop(SERVICE_NAME)`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:936`
- **Evidence**:
  ```python
  def _stop_service(self):
      ...
      container.stop(CONTAINER_NAME)
  ```
  `CONTAINER_NAME` and `SERVICE_NAME` both currently equal `"discourse"`, so the call works. `container.stop()` stops a Pebble service by name, not a container, so this is coincidentally correct.
- **Impact**: Latent bug — if either constant is renamed independently, this silently stops the wrong thing (or fails).
- **Fix**: Change to `container.stop(SERVICE_NAME)`.
- **Linter rule**: Mechanically checkable — flag `container.stop(CONTAINER_NAME)`.

### Pebble service manually stopped (`pebble stop`) stays stopped — charm reports active
- **Severity**: low
- **Kind**: bug
- **Where**: Pebble layer configuration, `src/charm.py:528-532`
- **Evidence**: After `kubectl exec ... pebble stop discourse`, the charm continued to report "active". The `discourse-ready` health check didn't restart the service because no `on-check-failure` action is configured. Service stayed inactive until manually started again.
- **Impact**: If a service is stopped via Pebble (manually or by an automated tool), the charm won't detect or restart it.
- **Fix**: Add `on-check-failure: { discourse-ready: restart }` to the Pebble check configuration.
- **Linter rule**: Not mechanically checkable.

### juju refresh triggers pod recreation and full setup even when no code changed
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:148-149` (`_on_upgrade_charm`), `src/charm.py:180-185` (`_on_rolling_restart`)
- **Evidence**: Refreshed stable rev 277 → edge rev 288. The diff between revisions is 6 files (CI workflows, `discourse_rock/rockcraft.yaml` base image digest, `docs/requirements.txt`, `pyproject.toml`, `uv.lock`) — no `src/` changes. Despite this, the pod was recreated (IP changed 10.1.0.39 → 10.1.0.21), a rolling restart triggered, the full image re-pulled (~11 min), and `db:migrate` ran again. `_on_upgrade_charm` emits `acquire_lock` unconditionally on any upgrade.
- **Impact**: Every refresh — even one only updating dependency pins or docs — triggers a full pod recreation, image re-pull, and migration run; 15+ minutes of effective downtime per unit for a 4GB+ image.
- **Fix**: Compare old/new charm revision or workload image digest in `_on_upgrade_charm`, and only emit `acquire_lock` when a restart is actually required.
- **Linter rule**: Not mechanically checkable.

### OAuth observer sets BlockedStatus as side-effect from env-var builder
- **Severity**: low
- **Kind**: ux
- **Where**: `src/oauth_observer.py:114-123` (`get_oidc_env`)
- **Evidence**: `get_oidc_env()`, called from `_create_discourse_environment_settings()` during layer generation, can set `self.charm.unit.status = BlockedStatus(...)` if `client_config.validate()` fails — an unexpected side effect for what looks like a pure data-gathering method.
- **Impact**: Status-setting logic is scattered across `_is_config_valid`, `_are_relations_ready`, and `get_oidc_env`, making status precedence hard to reason about.
- **Fix**: Have `get_oidc_env` raise or return an error sentinel and let the caller set status.
- **Linter rule**: Not mechanically checkable.

### `_set_workload_version` runs on non-leader units
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:613-631`, called at line 672 from `_set_up_discourse`
- **Evidence**: `_set_workload_version()` calls `self.unit.set_workload_version(version)` without a leadership guard, so non-leader units also run a Rails subprocess to fetch the version string.
- **Impact**: Wasteful subprocess call on every non-leader unit.
- **Fix**: Gate on `self.unit.is_leader()`.
- **Linter rule**: Mechanically checkable — flag `self.unit.set_workload_version()` calls outside an `is_leader()` guard.

### RollingOpsManager emits acquire_lock on upgrade but callback runs full setup
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:148-149` (`_on_upgrade_charm`), `src/charm.py:180-185` (`_on_rolling_restart`)
- **Evidence**: On upgrade the charm emits `acquire_lock`, which triggers `_on_rolling_restart` per unit. That callback calls `_setup_and_activate()`, re-running the full reconciler — `_set_up_discourse()` (short-circuits via completion check), `_configure_pod()`, and `_activate_charm()` (both replan) — when only the service restart is actually needed.
- **Impact**: Extra unnecessary work per unit during rolling restart.
- **Fix**: Have `_on_rolling_restart` restart the service directly instead of going through the full reconcile cycle.
- **Linter rule**: Not mechanically checkable.

### `require_nginx_route` called at `__init__` with static hostname — does not update on config change
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:95` (call site), `src/charm.py:209-217` (definition), `src/charm.py:219` (`_get_external_hostname`)
- **Evidence**: `_require_nginx_route()` is called once in `__init__`, passing `self._get_external_hostname()`. If `external_hostname` is empty at deploy time, the route registers with `self.app.name`; if the operator later sets `external_hostname` via `juju config`, the nginx route data is not resent because the call only happens once.
- **Impact**: Changing `external_hostname` after initial deployment doesn't update ingress routing — a likely surprise for operators.
- **Fix**: Re-call the nginx-route setup (or the library's `update_route_data()`) from `_on_config_changed` when `external_hostname` changes.
- **Linter rule**: Not mechanically checkable.

### `RedisRequires.app_data` and `url` properties have unguarded `relation.data[relation.app]` access
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/redis_k8s/v0/redis.py:92-93` (`app_data`), `lib/charms/redis_k8s/v0/redis.py:120` (`url`)
- **Evidence**: `app_data` returns `relation.data[relation.app]` with no `relation.app is not None` check. `url` falls back with a bare `except KeyError: pass`. This is library code; the charm itself uses unit-level `relation_data` (which checks `relation.units`) rather than `app_data`/`url` directly, so it isn't directly affected, but any charm calling these properties would be.
- **Impact**: Potential `TypeError` during a relation-broken race for any consumer of this library method; the bare `except KeyError: pass` also masks genuine bugs.
- **Fix**: Add `and relation.app` guard to `app_data`; replace the bare except with `.get()` in `url`.
- **Linter rule**: Mechanically checkable — flag `relation.data[relation.app]` without a preceding null check (library code, not charm code).

### S3 config error message is repetitive
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:323-326`
- **Evidence**: `'s3_enabled' requires 's3_access_key_id', 's3_enabled' requires 's3_bucket', 's3_enabled' requires 's3_region', 's3_enabled' requires 's3_secret_access_key'` — repeats the prefix for each missing field.
- **Impact**: Hard to scan quickly.
- **Fix**: `f"'s3_enabled' requires: {', '.join(missing)}"`.
- **Linter rule**: Not mechanically checkable (style).

### DB password visible in plain text in the Pebble plan
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:412-418` (Pebble layer construction in `_start_service`); confirmed at runtime
- **Evidence**: The Pebble plan environment block includes `DISCOURSE_DB_PASSWORD`, `DISCOURSE_DB_USERNAME`, and `DISCOURSE_REDIS_HOST` in plain text, visible via `juju run -- pebble plan` or `kubectl exec`.
- **Impact**: Anyone with unit-level exec access can read the database password. Standard pattern for k8s charms passing credentials via env vars, but a defense-in-depth gap.
- **Fix**: Ecosystem-wide concern — would require Juju secrets and runtime credential injection instead of a static Pebble layer, not specific to this charm.
- **Linter rule**: Not mechanically checkable (ecosystem-wide pattern).

### Deprecated library warnings at runtime
- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/rolling_ops/v0/rollingops.py:28` (deprecation warning in `RollingOpsManager.__init__`); `lib/charms/data_platform_libs/v0/data_interfaces.py:1176` (uses deprecated `JujuVersion.from_environ()`)
- **Evidence**: Deploy-time log: `WARNING unit.discourse-k8s/0.juju-log redis:5: The 'rollingops' v0 library is deprecated and no longer maintained.` Pytest runs show 54 `DeprecationWarning`s: `JujuVersion.from_environ() is deprecated, use self.model.juju_version instead`.
- **Impact**: Warnings logged on every hook that touches these libraries; noise that could mask real issues, and noisy test output.
- **Fix**: Migrate `rolling_ops` to the newer `charmlibs` implementation; the `data_interfaces` deprecation needs an upstream fix.
- **Linter rule**: Mechanically checkable — scan `lib/charms/` for known-deprecated library versions/APIs.

## Worth copying

### Clean reconciler pattern: `_setup_and_activate()`
`src/charm.py:187-193` — A single entry point that multiple event handlers call, with clear guard clauses: check if setup is needed, then configure, then activate if relations are ready. The right pattern for k8s charms where events can arrive in any order.

### Separation of concerns with helper classes
`src/database.py` and `src/oauth_observer.py` — `DatabaseHandler` and `OAuthObserver` encapsulate relation handling, keeping the main charm class focused on orchestration. `DatabaseHandler.get_relation_data()` gracefully returns defaults when the relation isn't ready, with proper `None` checks on all required fields.

### Pebble health checks at the rock level
`discourse_rock/rockcraft.yaml:checks` — `discourse-setup-completed` is defined in the rock, separating "is the container healthy" (rock concern) from "is the application running" (charm concern via `discourse-ready`). Prevents premature Pebble-ready events.

### Running as non-root user
`discourse_rock/rockcraft.yaml:9` (`run-user: _daemon_`), `src/charm.py:420` (`"user": CONTAINER_APP_USERNAME`) — The workload runs as `_daemon_` (UID 584792), not root, with correct directory ownership. Confirmed via `kubectl exec ... ps aux`.

### Comprehensive integration tests with real assertions
`tests/integration/test_charm.py` — Tests verify actual behaviour, not just status: the registration page returns 200, compiled assets are served, categories can be created via the API, S3 uploads produce real bucket objects, and relation removal/recovery is checked against both Juju status and HTTP availability.

### Dual test approach: scenario + Harness
`tests/unit/test_charm.py` (scenario-based, `ops.testing.Context`) and `tests/unit_harness/test_charm.py` (Harness-based) — Scenario tests are concise and focused (CORS origin computation, OAuth integration); Harness tests cover lower-level interactions (exec handling, action dispatch).

### Config validation before any work
`src/charm.py:220-265` — `_is_config_valid()` runs before any Pebble or subprocess work in `_configure_pod()`/`_activate_charm()`, checking cross-config constraints (SAML/OAuth require `force_https`, S3 requires all S3 fields) and collecting multiple errors together.

### Clean observability wiring
`src/charm.py:109-115` — Metrics, logging, and Grafana dashboard integrations wired declaratively at `__init__` with minimal code (`LogProxyConsumer`, `MetricsEndpointProvider`, `GrafanaDashboardProvider`). Confirmed working in rv-discourse6: both logging and metrics-endpoint relations to grafana-agent-k8s connected successfully, and charm status was unaffected by grafana-agent-k8s being blocked.

## Common-practice notes

**Follows ecosystem conventions:**
- Standard `src/charm.py` + `src/constants.py` layout
- `charmcraft.yaml` with the uv plugin
- Charm libraries under `lib/charms/<pkg>/v<N>/` follow the standard layout
- Observability integrations use standard COS libraries (`prometheus_scrape`, `grafana_dashboard`, `loki_push_api`)
- `concierge.yaml` pins Juju 3.6/stable and microk8s 1.34-strict, consistent with IS DevOps team convention
- Terraform module at `terraform/` follows the charmkeeper convention

**Drifts from convention:**
- Uses two unit test frameworks (Harness and scenario/Context); the ecosystem is transitioning to scenario-only, and the Harness tests use the deprecated `ops.testing.Harness`.
- `_require_nginx_route()` is called once at `__init__` and doesn't update when `external_hostname` config changes; most charms re-run ingress setup on config-changed.

**Leads ecosystem:**
- Rock-level Pebble checks (`discourse-setup-completed`) separating container readiness from application readiness — worth broader adoption.
- The dual scenario/Harness test approach is a pragmatic transitional strategy other charms with legacy Harness tests could adopt.

**Questionable:**
- The rock builds Ruby, Node, ImageMagick, and precompiles assets from source in a single stage, producing a >4GB image. Most ecosystem rocks use multi-stage builds or pre-built packages.

## Tests

**Unit tests** (55 passing, all clean, re-run confirmed 2026-08-09):
- 9 scenario-based tests (`tests/unit/test_charm.py`) covering CORS origin computation and OAuth integration (including the `external_hostname not set` → BlockedStatus path)
- 46 Harness-based tests (`tests/unit_harness/test_charm.py`) covering relations, config validation, actions, proxy env, upgrade, and edge cases for database/redis relation readiness
- Coverage: 88% overall (`charm.py`: 88%, `database.py`: 95%, `oauth_observer.py`: 84%, `constants.py`: 100%)
- 54 `DeprecationWarning` messages from `JujuVersion.from_environ()` in `data_interfaces.py` (known upstream issue)
- 43 `PendingDeprecationWarning` messages from `ops.testing.Harness`

**Linting** (all clean, `tox -e lint`):
- `ruff format --check`: 19 files already formatted
- `ruff check`: all checks passed
- `mypy`: no issues found in 19 source files
- `codespell`: no issues

**Static analysis** (all clean, `tox -e static`):
- `bandit`: no issues identified (various `#nosec` annotations for test password strings)

**Integration tests** (not executed — require a full microk8s environment with S3/SAML test infrastructure):
- `test_charm.py`: active status, Prometheus endpoint, setup verification, S3 with MicroCeph, category creation, compiled asset serving, relation removal/recovery
- `test_db_migration.py`: migration from a Discourse v3.3.0 database to current
- `test_oauth.py`, `test_saml.py`, `test_users.py`: OAuth, SAML, user management
- Tests use Jubilant (not `pytest-operator`) and make real HTTP assertions against the deployed application

**Test gaps** (from coverage report):
- `src/charm.py:609-611`: `_on_database_relation_broken` → `_stop_service` error path (container not connectable)
- `src/charm.py:629-631`: `_on_anonymize_user_action` error path (`ExecError`)
- `src/charm.py:773-776`, `786-787`: `_on_promote_user_action` container-not-connectable and `ExecError` paths
- `src/charm.py:811-812`, `824-825`: `_on_create_user_action` container-not-connectable and `ExecError` paths
- `src/charm.py:852-854`, `861-862`: `_user_exists`, `_activate_user` `ExecError` paths
- `src/charm.py:946`: main entry point (never covered, expected/`pragma: no cover`)
- `src/oauth_observer.py:80-81`: OAuth relation-broken handling
- `src/oauth_observer.py:114-123`: `ClientConfig` validation error path in `get_oidc_env`
- SAML `_get_saml_config` error paths: the `StopIteration` (line 346) and `IndexError` (line 354) paths are uncovered by unit tests
- SAML relation-joined without app data: no test covers a SAML relation without app data; the existing test `test_on_config_changed_when_saml_target_url_and_force_https_disabled` always adds app-level data, so `saml_data_available` always fires
- Child process death: no test covers sidekiq/prometheus-collector dying
- Pebble layer non-change detection: no test verifies config changes that don't affect the environment skip the replan
- Juju 4.x Pebble plan: no test verifies the empty-plan-no-services behaviour when relations are missing
- juju refresh with no-op revision: no test verifies a no-op refresh skips pod recreation (confirmed by observation that it does not skip it)

The integration tests are the main defense against regressions in the uncovered action error paths — hard to simulate in unit tests, more feasible in integration.

## Docs

**Coverage**: Excellent. `docs/` contains a full Diátaxis-structured set:
- Tutorial (`docs/tutorial.md`): step-by-step from zero to a working deployment
- How-to guides: hostname config, container config, Rails console, S3, SMTP, SAML, backup/restore, upgrades, contributing
- Reference: actions, charm architecture, configurations, external access, integrations, plugins, versioning
- Explanation: security
- Changelog

**Quality**: High. The tutorial includes concrete commands with expected output, uses Concierge for environment setup, and covers the full lifecycle including admin user creation. Architecture docs include a diagram and explain the event flow. The security explanation covers data at rest, data in transit, and patching policy.

**Match with observed behaviour**: Documented behaviour matches what was observed. The tutorial's claim that `force_https` must be true for SAML/OAuth is validated by the config validation code. The backup/restore docs reference `pg_dump`, present in the rock.

**Charmhub description**: Good overview with links to docs, issues, and source.

**Terraform module**: `terraform/README.md` documents input/output tables; follows the standard charmkeeper pattern (single `juju_application` resource with configurable name, channel, revision, units, constraints, config map).

**Doc gaps**:
1. Juju 4.x compatibility status is undocumented — the charm deploys on Juju 4.x but its required PostgreSQL dependency doesn't; no PostgreSQL charm (any channel) supports Juju 4.x Kubernetes.
2. OAuth setup doesn't mention that `external_hostname` must be a valid DNS name, not the default app name. The "Invalid OAuth client config" error doesn't point to the fix.
3. SAML docs don't note the specific binding requirement (HTTP-Redirect) or that a missing endpoint/empty certificate causes a hook error rather than a clean status message.
4. No documentation that sidekiq/prometheus-collector are unicorn child processes — operators should know killing sidekiq silently disables background jobs.

## Open questions

1. **S3 migration race on multi-unit**: `_should_run_s3_migration` is correctly gated on `is_leader()`, but if that unit dies mid-migration there's no recovery mechanism. Is `FORCE_S3_UPLOADS=true` (set unconditionally when S3 is enabled) still needed, or a stale workaround?
2. **Image size**: would a multi-stage rock build or a separate sidecar for image processing address the >4GB image (issue #427)? The 400+ line `imagemagick` part is a significant contributor.
3. **Unicorn worker count**: issue #298 notes the charm starts only 3 unicorn workers, relying on the unicorn config default (`UNICORN_WORKERS` isn't set in the observed Pebble plan). Should this be a config option?
4. **Redis HA and `leader-host`**: the redis relation data includes `leader-host`; the charm falls back to unit-data `hostname`. Correct for single-unit Redis — untested with multi-unit Redis HA.
5. **nginx-route hostname update on config change**: `_require_nginx_route()` runs only at `__init__`. `NginxRouteRequirer._config_reconciliation` does run on relation-changed, so a relation refresh picks up a hostname change but a config change alone does not — inconsistent UX.
6. **SAML relation-joined without app data**: should the charm observe `relation_joined`/`relation_created` to catch the `force_https` requirement when a SAML relation is first established, rather than waiting for `saml_data_available` or a full setup cycle?
7. **Pebble plan exposes database credentials in plain text**: standard k8s-charm pattern, but should the ecosystem move toward Juju secrets for relation credentials? Ecosystem-wide question, not specific to this charm.
8. **Pebble `on-check-failure` gap**: the `discourse-ready` check has no failure action; should the charm configure `on-check-failure: { discourse-ready: restart }`?
9. **OAuth callback URL**: per issue #413 and this review's testing, should the charm hard-refuse the OAuth relation when `external_hostname` is unset, with a message directing the operator to set it?
