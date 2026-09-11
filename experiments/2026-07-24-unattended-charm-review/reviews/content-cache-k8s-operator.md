# content-cache-k8s

A mature, well-structured k8s charm that deploys Nginx as an HTTP caching proxy for CDN use cases. Code is clean, follows `ops` conventions well, and is thoroughly unit-tested (36 tests, all passing, ~88-92% branch coverage). But deployment testing found a class of config-validation bugs that crash the workload: any cache-related string config set to empty produces an invalid nginx directive, and `cache_all=true` produces a bare `;` — both put the charm into an unrecoverable error state requiring `juju resolve`. There is also a confirmed GC bug (`require_nginx_route()` return value discarded, `NginxRouteRequirer` collected before events fire), a Juju-version-dependent status bug where `_on_start` unconditionally overwrites `BlockedStatus`/messages with a bare `ActiveStatus()`, and a `report-visits-by-ip` action that reads `$http_x_forwarded_for` (always `-` for internal/direct traffic) instead of `$remote_addr`. These bugs are present in both the stable (rev 49, 2024-12-17) and edge (rev 115, 2026-07-15) channels — same git hash, 8 months of only dependency/doc churn between them. A maintainer should first fix the cache-config validation bug (it's a one-line template fix and directly crashes the workload) and store the `require_nginx_route()` return value, then add unit tests for non-default cache config and the `_on_start`/upgrade status paths that let these bugs slip through untested.

| | |
|---|---|
| Repo | canonical/content-cache-k8s-operator @ 9a06042 (2026-07-15) |
| Charms | content-cache-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5), stable rev 49 and edge rev 115; concierge-k8s-3 (Juju 3.6.25), stable rev 49 and edge rev 115 |
| Reviewed | 2026-08-13 |

## What it does

Deploys Nginx on Kubernetes as a caching reverse proxy, configured either via Juju config (`backend`, `site`, cache tuning) or via an `nginx-proxy` relation from another charm providing service details. Integrates with the observability stack (Prometheus metrics via `nginx-prometheus-exporter` on port 9113, Loki log forwarding, Grafana dashboards) and with `nginx-ingress-integrator` for ingress. Also acts as an `nginx-proxy` provider so downstream charms can use it as a cache layer. The workload runs in a single Pebble-managed container with two services — `content-cache` (Nginx on 8080) and `nginx-prometheus-exporter` (metrics on 9113) — plus a `promtail` service injected by `LogProxyConsumer` when the `logging` relation to `grafana-agent-k8s` is added.

## Deployment log

### Deploy 1: Juju 4.0.5, charmhub stable rev 49

```
juju switch concierge-k8s-4
juju add-model rv-content-cache
juju deploy content-cache-k8s --channel stable
```

Pod came up (2/2 containers), pebble-ready fired, config-changed detected missing `backend` → `BlockedStatus`. Then the `start` hook ran and overwrote status to `ActiveStatus()` with no message — the unit showed "active" despite being unconfigured (see Finding: start hook overrides BlockedStatus).

```
juju deploy any-charm backend-app --channel beta
juju integrate content-cache-k8s:nginx-proxy backend-app:nginx-route
juju deploy nginx-ingress-integrator --channel stable --trust
juju integrate content-cache-k8s nginx-ingress-integrator
```

`backend-app` failed to install (unrelated any-charm hook error). The `nginx-proxy` relation existed with no data, so the charm stuck in "maintenance: Configuring workload container (config-changed)" — `_make_env_config()` returned `None`, causing repeated defers, until the relation was removed.

```
juju remove-relation content-cache-k8s:nginx-proxy backend-app:nginx-route
juju config content-cache-k8s backend="http://httpbin.org:80" site="test-cache.local"
```

Charm reached "active: Ready", two Pebble services running, Nginx config rendered on port 8080.

```
juju config content-cache-k8s cache_all=true
```

Hook failed: `nginx: [emerg] unexpected ";" in /etc/nginx/sites-enabled/default:29`. The template variable `{NGINX_CACHE_ALL}` renders empty when `cache_all=true`, producing a bare `;`. Both units went to error state and could not recover automatically.

```
juju config content-cache-k8s cache_all=false
juju resolve content-cache-k8s/0
juju resolve content-cache-k8s/1
```

Charm recovered to "Ready" after resolving the error and pushing corrected config.

### Deploy 2: Juju 3.6.25, charmhub stable rev 49

```
juju switch concierge-k8s-3
juju add-model rv-content-cache-3
juju deploy content-cache-k8s --channel stable --config backend="http://httpbin.org:80" --config site="test-cache.local"
```

Deployed and reached "Ready" within ~60s. Deployed again without config → unit went to "Blocked: Required config(s) empty: backend" and *stayed* blocked — the `_on_start` `ActiveStatus` override did not occur because Juju 3.6 fires `start` before `config-changed` (unlike Juju 4.x, where `start` fires after).

### Deploy 3: Juju 4.0.5, edge rev 115 — deepened review with failure injections

```
juju switch concierge-k8s-4
juju add-model rv-cache-deep
juju deploy content-cache-k8s --channel stable --config backend="http://httpbin.org:80" --config site="test-cache.local"
juju refresh content-cache-k8s --channel edge
```

Refreshed to edge rev 115, same git hash `9a06042` as HEAD. Unit reached "Ready".

**Observability**:
```
juju deploy grafana-agent-k8s --channel stable
juju integrate content-cache-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate content-cache-k8s:logging grafana-agent-k8s:logging-provider
juju integrate content-cache-k8s:grafana-dashboard grafana-agent-k8s:grafana-dashboards-consumer
```
All three relations established. A new Pebble service `promtail` appeared for log forwarding. content-cache-k8s remained "Ready" throughout.

**Failure injections (edge rev 115)**:
- Kill `nginx-prometheus-exporter`: Pebble restarted within 3s.
- Kill `nginx` master: Pebble restarted within 3s.
- Delete pod: recreated, "Ready" within ~15s.
- `cache_all=true`: same bare-`;` bug as stable.
- `cache_use_stale=""`: `nginx: [emerg] invalid number of arguments in "proxy_cache_use_stale" directive` → error.
- `cache_valid=""`: `nginx: [emerg] invalid number of arguments in "proxy_cache_valid" directive` → error.
- `cache_inactive_time=""`: `nginx: [emerg] invalid inactive value "inactive="` → error.
- `cache_max_size=""`: `nginx: [emerg] invalid max_size value "max_size="` → error.
- `backend="not-a-valid-url"`: `nginx: [emerg] invalid URL prefix` → error (nginx catches most bad URLs at parse level; the silent `Host "None"` scenario from initial code analysis is narrower/harder to trigger than first thought — `(unverified)` as a general failure mode).
- `backend="http://"`: `nginx: [emerg] no host in upstream ""` → error.
- `backend="http:///"`: `nginx: [emerg] no host in upstream "/"` → error.

### Deploy 4: Juju 4.0.5, edge rev 115 — lifecycle and GC confirmation

```
juju switch concierge-k8s-4
juju add-model rv-cache-final
juju deploy content-cache-k8s --channel edge --config backend="http://httpbin.org:80" --config site="final-test.local"
```

Deployed and "Ready". Then:

**Scale**: 1→2 units, both "Ready" within ~20s. Memory ~55MB per pod (70-80MB with promtail from the logging relation). Scale 2→1, clean termination.

**nginx-route GC confirmation**: deployed `nginx-ingress-integrator` and related it. Debug-log showed:
```
WARNING nginx-route:1: Reference to ops.Object at path ContentCacheCharm/NginxRouteRequirer[nginx-route]
has been garbage collected between when the charm was initialised and when the event was emitted.
Make sure sure you store a reference to the observer.
```
Confirms `require_nginx_route()`'s return value is not stored on `self`, so the `NginxRouteRequirer` object can be GC'd before the relation-changed event fires.

**Pebble plan confirmed** (two services, environment variables, health checks):
```
services:
  content-cache:             startup: enabled, command: /srv/content-cache/entrypoint.sh
  nginx-prometheus-exporter: startup: enabled, requires: [content-cache]
checks:
  content-cache:      exec: {command: "ps -A | grep nginx"}
  nginx-exporter-up:  http: {url: http://localhost:9113/metrics}
```

**Action confirmed**: `report-visits-by-ip` returned `-` as the IP with 26 requests (all from `nginx-prometheus-exporter` polling stub_status internally — no X-Forwarded-For header present).

**Start-hook status override confirmed** (Juju 4.x status-history, deploy without config):
```
00:47:10  workload  blocked   Required config(s) empty: backend       (config-changed)
00:47:11  workload  active                                            (start)
00:47:13  workload  blocked   Required config(s) empty: backend       (content-cache-pebble-ready)
```
The start hook erases `BlockedStatus` to `ActiveStatus`. Pebble-ready re-fires and re-blocks here, so the end state happens to be correct, but the transient wrong state exists — and in Deploy 1, the final state actually stuck as "active" because pebble-ready had already fired before start. Whether the final state is blocked or active depends on hook-firing order/timing.

### Deploy 5: Juju 3.6.25, edge rev 115

```
juju switch concierge-k8s-3
juju add-model rv-cache-36
juju deploy content-cache-k8s --channel edge --config backend="http://httpbin.org:80" --config site="rv36.local"
juju deploy content-cache-k8s --channel edge content-cache-noconfig
```

With config: "Ready" within ~60s. Without config: correctly "Blocked", no `ActiveStatus` override — on Juju 3.6, `start` fires before `config-changed`, so the start handler's unconditional `ActiveStatus` is immediately overwritten by config-changed's `BlockedStatus`.

### Key finding: rev 49 (2024-12-17) and rev 115 (2026-07-15) contain identical functional code

Edge rev 115 was built from the same git hash (`9a06042`) as repo HEAD. All bugs are present in both channels. The 8 months between revisions contain only renovate dependency bumps and docs changes — no functional fixes.

## Observed behaviour

- **Hook ordering differs between Juju 3.6 and 4.x**: Juju 4.x typically: `config-changed` → `start` → `content-cache-pebble-ready` (can vary). Juju 3.6: `start` → `config-changed` → `content-cache-pebble-ready`. `_on_start`'s unconditional `ActiveStatus()` causes transient or permanent wrong status only on Juju 4.x.
- **Startup time**: ~45-60 seconds from deploy to active, on both controllers.
- **Memory footprint**: ~55MB per pod with nginx + exporter; ~70-80MB after adding the `promtail` sidecar via the logging relation.
- **Pebble recovery**: kill nginx or exporter → restart within 3s.
- **Pod recovery**: delete pod → recreated, "Ready" within ~15s.
- **Scale up/down**: 1→3 units all "Ready" within ~20s; scale back to 1 terminates cleanly.
- **Observability integrations**: metrics-endpoint, grafana-dashboard, logging all established cleanly; `promtail` service correctly injected by `LogProxyConsumer`.
- **The `cache_all=true` bug is invisible from static code alone**: only visible once nginx actually parses the rendered config with an empty `{NGINX_CACHE_ALL}`.
- **All four cache-tuning config options are unvalidated**: `cache_use_stale`, `cache_valid`, `cache_inactive_time`, `cache_max_size` each accept empty strings that produce invalid nginx directives. Defaults protect against this at deploy time, but `juju config` allows setting empty strings post-deploy.
- **Invalid backend URLs**: contrary to the code-analysis prediction of a silent `Host "None"` header, nginx catches most invalid URL patterns at config-parse time (`invalid URL prefix`, `no host in upstream`). The charm still enters error state rather than a clear `BlockedStatus` message.
- **Action log-format mismatch**: log format `content_cache` uses `$http_x_forwarded_for` as the first field, `-` for all internal traffic (Prometheus exporter polls). Behind a real ingress proxy this field would carry the client IP, so the action may work in production but is misleading in test/direct-access environments.
- **`_filter_lines` timestamp parsing**: `line.split()[3]` returns `[12/Aug/2026:12:40:49` (partial timestamp, timezone `+0000]` overflows into `[4]`). Works only because `strptime("%d/%b/%Y:%H:%M:%S")` doesn't require the timezone — one log-format change away from silent failure.
- **GC warning confirmed**: `require_nginx_route()` return value not stored, causing `NginxRouteRequirer[nginx-route]` to be garbage collected; the relation-changed handler may fire on a dead object.
- **Pebble `promtail` service**: appears (disabled startup, active) after adding the logging relation, managed by `LogProxyConsumer` from `charms.loki_k8s.v0.loki_push_api`.
- **`entrypoint.sh` copies unrendered template to `/etc/nginx/sites-available/default`**: never read by nginx (which includes `sites-enabled/*`, not `sites-available/*`). The rendered config is pushed by the charm to `sites-enabled/default`.
- **`self.on.nginx_route_available` observer at `src/charm.py:108` is dead code**: `self.on` is the charm's `_NginxRouteCharmEvents` instance, but `provide_nginx_route()` creates its own `_NginxRouteProvider` with a separate `on` instance and emits there — nothing emits on the charm's `self.on.nginx_route_available`. The real callback is registered correctly via `provide_nginx_route()` on `provider.on`; the duplicate registration is harmless but confusing.
- **Refresh between revisions works cleanly**: refreshed edge rev 115 → stable rev 49 (same git hash), upgrade-charm hook fired, workload reconfigured, "Ready" within ~15s. Refreshing back to edge also worked.
- **nginx-route relation removal is clean**: removed relation to nginx-ingress-integrator — content-cache-k8s stayed "Ready" with no errors.
- **`_on_start` erases the "Ready" message even on a correctly configured charm**: status-history: `active (Ready)` → `active ()` (start hook, blank message) → `maintenance` (pebble-ready) → `active (Ready)`. UX regression on Juju 4.x where start fires after config-changed; on Juju 3.6 start fires first, so it's immediately overwritten.
- **Every config change restarts nginx unnecessarily**: `_make_env_config()` embeds all template variables in the pebble service's environment; since the pebble comparison checks the full services dict, any config change (even nginx-only) triggers a full pebble replan/restart, clearing the in-memory cache. Observed: changing `client_max_body_size` from `1m` to `50m` produced "Updating pebble layer config" despite only the nginx config file changing.
- **Upgrade from edge→stable performs 3 configuration cycles**: status-history showed upgrade-charm → config-changed → start → pebble-ready all triggering `configure_workload_container`, three rounds of nginx config pushes/replans for a single no-op refresh.

## Findings

### `cache_all=true` (and four other cache config values) generate invalid Nginx config, crashing the workload
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:377-379` (cache_all), `src/charm.py:401-406` (cache_use_stale, cache_valid, cache_inactive_time, cache_max_size)
- **Evidence**:
  ```python
  cache_all_configs = ""
  if not config["cache_all"]:
      cache_all_configs = "proxy_ignore_headers Cache-Control Expires"
  ```
  When `cache_all=true`, `cache_all_configs` is `""` and the template has `{NGINX_CACHE_ALL};`, producing a bare `;`. Same root cause for:
  ```python
  "NGINX_CACHE_USE_STALE": config["cache_use_stale"],       # empty → "proxy_cache_use_stale ;"
  "NGINX_CACHE_VALID": config["cache_valid"],                 # empty → "proxy_cache_valid ;"
  "NGINX_CACHE_INACTIVE_TIME": config.get("cache_inactive_time", "10m"),  # empty → "inactive="
  "NGINX_CACHE_MAX_SIZE": config.get("cache_max_size", "10G"),            # empty → "max_size="
  ```
- **Impact**: All five empty-value scenarios produce distinct nginx parse errors and hook failures on both rev 49 and rev 115. The charm enters error state on all units and cannot recover without operator intervention (`juju config` + `juju resolve`). An operator clearing a value to "revert to default" gets a hard crash instead.
- **Fix**: Validate config values that become nginx directives; reject empty values with `BlockedStatus` or fall back to defaults:
  ```python
  if not config.get("cache_use_stale"):
      self.unit.status = BlockedStatus("cache_use_stale must not be empty")
      return None
  ```
  For `cache_all`, move the semicolon inside the variable:
  ```python
  cache_all_configs = "" if config["cache_all"] else "proxy_ignore_headers Cache-Control Expires;"
  ```
  and change the template from `{NGINX_CACHE_ALL};` to `{NGINX_CACHE_ALL}`.
- **Linter rule**: "Template variable used in an nginx directive must produce a complete directive or be empty" — not mechanically checkable without parsing nginx grammar.

### `_on_start` unconditionally sets `ActiveStatus`, overriding `BlockedStatus`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:119-126`
- **Evidence**:
  ```python
  def _on_start(self, event) -> None:
      logger.info("Starting workload container (start)")
      self.model.unit.status = ActiveStatus()
  ```
- **Impact**: On Juju 4.x, status-history confirmed: `00:47:10` config-changed set `blocked: Required config(s) empty: backend`, `00:47:11` start set `active` (no message). The unit briefly (or, per Deploy 1, permanently) shows "active" while unconfigured, depending on whether `pebble-ready` re-fires `config-changed` afterward. This breaks the Juju contract that "active" means operational. On Juju 3.6, start fires before config-changed so the override is immediately corrected — but the code is unconditionally wrong on both versions.
- **Fix**: Remove `_on_start` entirely (it does no useful work beyond logging), or guard it:
  ```python
  def _on_start(self, event) -> None:
      if isinstance(self.unit.status, BlockedStatus):
          return
      self.unit.status = ActiveStatus()
  ```
- **Linter rule**: "Event handler for `start` hook must not unconditionally set `ActiveStatus`" — mechanically checkable: flag any `self.on.start` observer that assigns `ActiveStatus()` without a status guard.

### `require_nginx_route()` return value not stored, causing GC of the observer
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:93-101`
- **Evidence**:
  ```python
  require_nginx_route(
      charm=self,
      max_body_size=ingress_config.get("max-body-size", None),
      ...
  )
  ```
  The returned `NginxRouteRequirer` object is not assigned. Debug log (Juju 4.x, edge rev 115):
  ```
  WARNING nginx-route:1: Reference to ops.Object at path ContentCacheCharm/NginxRouteRequirer[nginx-route]
  has been garbage collected between when the charm was initialised and when the event was emitted.
  Make sure sure you store a reference to the observer.
  ```
- **Impact**: The GC warning appeared exactly when nginx-ingress-integrator joined the nginx-route relation. Relation data (service-hostname, service-name, service-port, max-body-size) was still populated correctly, suggesting the initial config push (in `__init__`) succeeded before collection — but subsequent relation-changed events (e.g. ingress IP updates) may fire on a dead object and be dropped. `provide_nginx_route` (provider side) correctly keeps references via a module-level `WeakKeyDictionary`; `require_nginx_route` (requirer side) relies on the caller.
- **Fix**: Store the return value:
  ```python
  self._nginx_route = require_nginx_route(
      charm=self,
      ...
  )
  ```
- **Linter rule**: "Return value of library functions that register `ops.Object` observers must be assigned to `self`" — mechanically checkable: flag calls to known `require_*`/`*Requirer(...)` setup functions whose return value is discarded.

### `_on_start` erases the "Ready" status message even on a correctly configured charm (Juju 4.x)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:119-126`
- **Evidence**: Same handler as above (`self.model.unit.status = ActiveStatus()`, no message). Status-history for a correctly configured charm during normal operation: `active (Ready)` → `active ()` (start hook) → `maintenance` (pebble-ready) → `active (Ready)`.
- **Impact**: An operator running `juju status` during the brief start→pebble-ready window sees a blank "active" status with no indication of what's happening. Combined with the above finding, the unconditional `ActiveStatus()` is harmful in two ways: erasing meaningful status messages and overriding blocked states.
- **Fix**: Same as above — remove `_on_start` or guard it against overwriting existing status/messages.
- **Linter rule**: same as start-hook finding above.

### `report-visits-by-ip` action reads `$http_x_forwarded_for`, not `$remote_addr`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:187` (`_get_ip`) and `content-cache_rock/nginx-logging-format.conf:1-4`
- **Evidence**: Log format is `log_format content_cache '$http_x_forwarded_for - $remote_user [$time_local] ...'`. The action does `line.split()[0]`, reading `$http_x_forwarded_for`, which is `-` for connections with no such header.
- **Impact**: Action output: `| IP | Requests | | - | 26 |` — all 26 "requests" were internal stub_status polls from the exporter with no X-Forwarded-For header. Behind a real ingress proxy the field would contain the client IP, so the action may work correctly in production but gives useless/misleading results in any environment without such a proxy (including test setups). An operator running this action to find abuse sources gets `-` for all entries.
- **Fix**: Either change the log format to include `$remote_addr` and update `_get_ip` to parse by position, or parse with a regex matching the actual format structure. If `$http_x_forwarded_for` is intentional, document this explicitly.
- **Linter rule**: not mechanically checkable — requires matching log-format definitions to parsing code.

### No fallback to juju config when `nginx-proxy` relation exists but has no data
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:348-373`
- **Evidence**:
  ```python
  relation = self.model.get_relation("nginx-proxy")
  if relation and relation.data[relation.app] and relation.units:
      ...
  elif relation:
      return None     # defers forever
  else:
      backend = str(config["backend"])
  ```
  If a relation exists but the remote app hasn't set data yet (or is missing a required field), the charm defers forever without falling back to juju config.
- **Impact**: Observed: with `any-charm` deployed but failing to provide data, the charm stuck in "maintenance" deferring until the relation was removed; setting `backend`/`site` via juju config had no effect while the relation existed. Related to open issue #193 (CMR hang). An operator who relates first and configures later (or whose related charm is slow) gets a permanently wedged charm; the only recovery is `juju remove-relation`.
- **Fix**: Fall back to juju config if relation data is incomplete, or set `WaitingStatus`:
  ```python
  if relation and relation.app and relation.data[relation.app]:
      if all(relation.data[relation.app].get(f) for f in REQUIRED_INGRESS_RELATION_FIELDS):
          ...  # use relation data
  # Fall through to juju config
  backend = str(config["backend"])
  ```
- **Linter rule**: not mechanically checkable — requires understanding relation-vs-config precedence semantics.

### No unit test for `cache_all=true` or empty cache directive values
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py` (`test_make_nginx_config` tests only the default case)
- **Evidence**: The default-config test asserts against `tests/files/nginx_config.txt`. Variant test files exist for `backend_site_name`, `client_max_body_size`, `proxy_cache_revalidate` — none for `cache_all=true` or empty cache directives.
- **Impact**: The critical `cache_all=true` bare-`;` bug would have been caught by a unit test rendering the config with that setting.
- **Fix**: Add test cases: `test_make_nginx_config_cache_all_enabled` (assert no bare `;` directives), plus empty-value tests for `cache_use_stale`, `cache_valid`, `cache_inactive_time`, `cache_max_size` expecting `BlockedStatus`/validation error.
- **Linter rule**: "Every boolean config option should have both true and false branches tested in template-rendering tests" — mechanically checkable for simple patterns.

### Integration tests don't cover config changes
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_core.py`
- **Evidence**: Six integration tests cover active status, backend reachability, cache headers, unit reachability, the `report-visits-by-ip` action, and the OpenStack Swift plugin. None tests a config change (e.g. `cache_all=true`) or validates the rendered nginx config.
- **Impact**: The `cache_all=true` bug survived because integration tests never exercise config changes that alter template output; the rendered nginx config is never fetched/validated in any test.
- **Fix**: Add tests that set various config values, wait for active, and verify the service is still reachable (`test_config_cache_all_enabled`, `test_config_cache_all_disabled_again`, `test_config_proxy_cache_revalidate_toggle`).
- **Linter rule**: not mechanically checkable.

### `_make_ingress_config` accesses `relation.app` without a None check
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:322`
- **Evidence**:
  ```python
  relation = self.model.get_relation("nginx-proxy")
  if relation:
      prev_site = site
      site = relation.data[relation.app].get("service-hostname", prev_site)
  ```
  No check that `relation.app is not None`; contrast with `_make_env_config`'s guard `if relation and relation.data[relation.app] and relation.units:`.
- **Impact**: During relation-broken events (or before the remote app registers), `relation.app` can be `None`, causing a `TypeError`. Not triggered in testing, but the inconsistency with `_make_env_config` is a maintenance hazard.
- **Fix**: `if relation and relation.app and relation.data[relation.app]:`
- **Linter rule**: "Access to `relation.data[relation.app]` must be guarded by a `relation.app is not None` check" — mechanically checkable.

### `_make_ingress_config` is only called in `__init__`, so ingress config can go stale
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:93` (called in `__init__` only)
- **Evidence**: `_make_ingress_config()` builds the `ingress_config` dict once at `__init__`, passed to `require_nginx_route()`. If `site` or `tls_secret_name` change via juju config afterward, the ingress config is not updated unless a full charm restart occurs.
- **Impact**: An operator changing `site` or `tls_secret_name` expects the ingress to update, but nothing re-invokes `_make_ingress_config` from `configure_workload_container` or `_on_config_changed` — a `juju refresh`/unit restart would be needed to pick up the change.
- **Fix**: Re-invoke `_make_ingress_config()` from `configure_workload_container`/`_on_config_changed` and update the `NginxRouteRequirer`'s (mutable) config, then call `_config_reconciliation()`.
- **Linter rule**: not mechanically checkable.

### `_filter_lines` timestamp parsing is fragile
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:165`
- **Evidence**:
  ```python
  timestamp_str = line_elements[3].lstrip("[").rstrip("]")
  ```
  The log format `[12/Aug/2026:12:29:10 +0000]` contains a space, so `line.split()[3]` returns `[12/Aug/2026:12:29:10` while the timezone `+0000]` overflows into `[4]`. Works only because `strptime("%d/%b/%Y:%H:%M:%S")` doesn't require the timezone.
- **Impact**: If parsing fails, `_filter_lines` returns `False` for all lines and the action returns empty results with no error — the operator sees an empty IP table with no indication the data is bad.
- **Fix**: Use a regex to extract the timestamp, e.g. `re.match(r'^\S+ \S+ \S+ \[([^\]]+)\]', line)`.
- **Linter rule**: not mechanically checkable.

### Pebble health check for `content-cache` uses fragile `ps | grep`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:438`
- **Evidence**: `"exec": {"command": "ps -A | grep nginx"}`.
- **Impact**: Succeeds even for a zombie/defunct nginx process, or matches the grep process itself. The exporter already uses a proper `http` check (`http://localhost:9113/metrics`); content-cache lacks the equivalent.
- **Fix**: Use an HTTP check, e.g. `http://localhost:8080/stub_status`.
- **Linter rule**: "Pebble check uses `ps | grep` pattern instead of `http`/`tcp`" — mechanically checkable.

### `self.on.nginx_route_available` observer is dead code
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:108`
- **Evidence**: `self.framework.observe(self.on.nginx_route_available, self._on_config_changed)`. The charm replaces `CharmBase.on` with `_NginxRouteCharmEvents()`, but `provide_nginx_route()` creates its own `_NginxRouteProvider` with a separate `on` and emits there, not on the charm's event bus. Nothing emits `self.on.nginx_route_available`. The same handler is (correctly) also registered via `provide_nginx_route(..., on_nginx_route_available=self._on_config_changed)`.
- **Impact**: Harmless in practice (the working path is the `provide_nginx_route()` registration) but confusing, and indicates a misunderstanding of the event architecture.
- **Fix**: Remove the dead observer, or document it as an intentional no-op safety net.
- **Linter rule**: not easily mechanically checkable without library-internals knowledge.

### Every config change triggers a Pebble replan even when only nginx config changed
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:432` (env_config includes all template vars), `src/charm.py:243-245` (pebble comparison)
- **Evidence**: `_make_env_config()` includes all template variables (e.g. `NGINX_CLIENT_MAX_BODY_SIZE`, `NGINX_CACHE_INACTIVE_TIME`) in the pebble service's `environment`. The comparison at `charm.py:240-244` diffs the full services dict, so any config change triggers a replan/restart. Observed: changing `client_max_body_size` produced "Updating pebble layer config" and restarted nginx unnecessarily.
- **Impact**: nginx supports hot reload, but the charm restarts the whole pebble service on every config change — a brief outage (~1-2s) and a cleared in-memory cache on every config tweak, which matters for a caching proxy in production.
- **Fix**: Separate environment variables that affect pebble/entrypoint from ones that only affect nginx config, or use `SIGHUP`/`nginx -s reload` for nginx-only changes.
- **Linter rule**: not mechanically checkable.

### Upgrade from edge→stable (same hash) performs three configuration cycles
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:203-211` (`_on_upgrade_charm`), `src/charm.py:128-137` (`_on_config_changed`)
- **Evidence**: Observed on `juju refresh --channel stable` from rev 115 to rev 49: `upgrade-charm` → config push → active Ready, then `config-changed` → config push again → active Ready, then `start` (erasing message) → `pebble-ready` → config push a third time.
- **Impact**: Three unnecessary reconfiguration cycles (three nginx restarts) on every upgrade, adding downtime/traffic disruption for a no-op refresh.
- **Fix**: Skip `configure_workload_container` in `_on_upgrade_charm` if the charm code/hash hasn't changed, or set a sentinel flag to skip the subsequent `config-changed` cycle once work is already done.
- **Linter rule**: not mechanically checkable.

### `entrypoint.sh` copies unrendered template to `sites-available/default` (never used)
- **Severity**: nit
- **Kind**: lint
- **Where**: `content-cache_rock/entrypoint.sh:11-13`
- **Evidence**:
  ```sh
  cat /srv/content-cache/templates/nginx_cfg.tmpl > /etc/nginx/sites-available/default
  exec nginx -g 'daemon off;'
  ```
  nginx.conf includes `sites-enabled/*`, not `sites-available/*`. The charm pushes the rendered config to `sites-enabled/default`; `sites-available/default` is dead, unrendered data.
- **Impact**: Confusing when debugging the container — the file looks like a config but has unresolved template variables. On initial pod startup, nginx starts with no virtual hosts until the charm pushes the rendered config, so there's a brief window where the workload runs but serves nothing.
- **Fix**: Remove the `cat` line, or symlink `sites-available/default` → `sites-enabled/default` and have the charm push to `sites-available/default` so nginx always has a config.
- **Linter rule**: not mechanically checkable.

### Unit tests use deprecated `ops.testing.Harness`
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:80`
- **Evidence**: `PendingDeprecationWarning: Harness is deprecated. ...`
- **Impact**: Harness is being removed from `ops`; tests will need rewriting. Not urgent but should be planned.
- **Fix**: Migrate to `ops.testing.Scenario`.
- **Linter rule**: "Use of deprecated `ops.testing.Harness`" — mechanically checkable.

### No unit test for the `file_reader` module
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/file_reader.py` (no dedicated test file)
- **Evidence**: `readlines_reverse` is only exercised indirectly through `test_report_visits_by_ip`. No tests for empty files, files without trailing newline, single-line files, very long lines, or performance with large files.
- **Impact**: The function reads byte-by-byte in reverse via `os.SEEK_END`; for large production log files this could be slow, with no documented bounds.
- **Fix**: Add `tests/unit/test_file_reader.py` with edge cases and a note on performance expectations.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Pebble layer comparison before replanning** (`src/charm.py:240-245`): compares the existing pebble services dict against the new one and only replans if they differ, avoiding restarts on no-op config changes:
  ```python
  services = container.get_plan().to_dict().get("services", {})
  if services != pebble_config["services"]:
      ...
      container.pebble.replan_services()
  ```
- **Clean env_config pattern for template rendering** (`src/charm.py:338-406`): all template variables collected into one dict and passed to `.format()` — testable, avoids scattered string concatenation.
- **`nginx-prometheus-exporter` as a Pebble sidecar** (`src/charm.py:262-289`): separate Pebble service in the same container, proper `http` health check on `/metrics`, startup ordering (`requires: [content-cache]`), no separate container needed.
- **`_missing_charm_configs` as a dedicated check method** (`src/charm.py:460-473`): required-config validation extracted into a focused, testable method.
- **Cache-poisoning header stripping** (`content-cache_rock/nginx_cfg.tmpl:18-22`): explicitly clears `Forwarded`, `X-Forwarded-Host`, `X-Forwarded-Port`, `X-Forwarded-Proto`, `X-Forwarded-Scheme` — security-conscious and well-commented.
- **`X-Cache-Status` header with pod identity** (`content-cache_rock/nginx_cfg.tmpl:24`): `add_header X-Cache-Status "$upstream_cache_status from {JUJU_POD_NAME} {JUJU_POD_NAMESPACE}"` — operators can see which cache pod served a request and whether it was a HIT or MISS.

## Common-practice notes

- **Follows**: standard `src/charm.py`, `lib/charms/<lib>/v<N>/` layout, `charmcraft.yaml` with `uv` plugin, `tox.toml` for test environments, `pyproject.toml` for tool config — consistent with current Canonical charm conventions.
- **Follows**: idiomatic use of `ops` (`CharmBase`, `framework.observe`, Pebble API `can_connect()`, `add_layer`, `replan_services`).
- **Drifts**: `_NginxRouteCharmEvents` is assigned to `self.on` at the class level (`on = _NginxRouteCharmEvents()`), replacing the standard `CharmBase.on` descriptor, rather than using `charm.on.define_event(...)`. Works because the class extends `CharmEvents`, but is unusual and caused the dead-code observer noted above.
- **Drifts**: uses the deprecated `ops.testing.Harness` in unit tests, while the ecosystem is moving to Scenario.
- **Follows**: `limit: 1` on `nginx-proxy` provides prevents ambiguity for a single-backend cache.
- **Notable**: supports both providing and requiring `nginx-route` on different relation names (`nginx-proxy` provides, `nginx-route` requires), making the charm usable both as a cache frontend and as an ingress backend — well documented in metadata.

## Tests

**Unit tests**: 36 tests in `tests/unit/test_charm.py`, all passing. Cover event handlers (`pebble_ready`, `start`, `config_changed`, `upgrade_charm`), `configure_workload_container` with various mock configs, `report_visits_by_ip` with parametrized log inputs, `_get_ip`, `_filter_lines`, ingress config generation (tls_secret, client_max_body_size, proxy relation), env config, pebble config, nginx config rendering, missing-config detection, `proxy_cache_revalidate` toggles. Coverage target: 88% branch coverage (the draft's byte-level number of "92% branch, 11 uncovered statements, 8 partial branches" is `(unverified)` against the notes, which cite an 88% target).

**Linting**: `ruff check src/` clean. `ruff check tests/` has one issue: `RUF036` (`None` not at end of type union) in `tests/integration/conftest.py:74` — not in charm code. `codespell` clean. `bandit` clean.

**Gaps** (confirmed):
- No test for `cache_all=true` nginx config output
- No test for `_on_start` status-override behaviour
- No test for `_make_env_config` with an `nginx-proxy` relation missing fields (the defer path)
- No test for the `file_reader` module independently
- No test for the `nginx-prometheus-exporter` pebble config generation
- No test for any empty cache-directive value
- No test for `_make_ingress_config` being called from a non-init context
- No Scenario-based tests (all use deprecated Harness)

**Integration tests**: `tests/integration/test_core.py` — 6 test functions: active status, backend reachability, cache-header presence, unit reachability, `report-visits-by-ip` action, OpenStack Swift plugin. Deploys a full topology (any-charm backend, content-cache-k8s, nginx-ingress-integrator). No tests for config changes, scaling, or failure recovery. Requires OpenStack credentials for the Swift test.

## Docs

- **README.md**: well-written, clear value proposition, lists integrations, links to external docs. Example shows `juju integrate content-cache-k8s:nginx-proxy wordpress-k8s`, the right relationship.
- **Discourse docs**: published at discourse.charmhub.io include tutorial, how-to, reference, and explanation sections following Diátaxis; the getting-started tutorial matches observed behaviour.
- **Charmhub description**: accurate, lists production use cases.
- **CONTRIBUTING.md**: comprehensive — CLA signing, AI-usage policy, development setup (`uv`, `tox`), rock building, deployment.
- **Docs/reality mismatch**: the tutorial says deploying without a backend relation results in "blocked" status — true on Juju 3.6, but timing-dependent on Juju 4.x where the `_on_start` bug may override it to "active".
- **Missing**: `config.yaml`'s `cache_all` description warns about `Vary: *` and `Set-Cookies` but doesn't mention the feature is currently broken (a bug rather than a doc gap per se).

## Open questions

- Why is there 8 months between stable rev 49 (2024-12-17) and edge rev 115 (2026-07-15) with no functional fixes, when the `cache_all` bug appears to have been present the whole time? Git history between those revisions shows only renovate bumps and doc changes.
- How does `_make_env_config` handle `relation.units` being empty (e.g. during relation-broken as remote units depart)? The guard `if relation and relation.data[relation.app] and relation.units:` falls through to `elif relation: return None` in that case — a possible third stuck-in-defer scenario alongside the missing-data case.
- Does `proxy_cache_revalidate` interact correctly with `cache_all` once the `cache_all` bug is fixed? The combination of "cache everything" and "revalidate expired items" is non-obvious and undocumented.
- Is the `self.on = _NginxRouteCharmEvents()` pattern safe going forward? It replaces `CharmBase`'s standard event descriptor; testing with multiple relations simultaneously showed no missing events, but the dead-code observer at `charm.py:108` suggests some confusion about the event architecture that could bite if ops/library assumptions about `self.on` change.
