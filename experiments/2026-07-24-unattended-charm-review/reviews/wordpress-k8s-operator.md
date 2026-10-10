# WordPress K8s Operator

A mature, well-structured Juju charm for running WordPress on Kubernetes: comprehensive unit tests, clean status-exception handling, and thoughtful WordPress-specific integrations (plugins, SSO, Swift storage, COS observability, ingress). It deploys and runs correctly under normal conditions on both Juju 3.6 and Juju 4.0.

But it is fragile under fault conditions. Observational testing found three real correctness gaps: the charm does nothing when the database relation is removed, leaving WordPress serving with stale credentials while reporting `active`; killing the Apache parent process leaves zombie workers holding port 80, which the charm never notices until it cascades into a full pod restart; and a malformed OpenID team-map config crashes the charm with a raw `ValueError` instead of a blocked status. A maintainer should fix the database relation-broken/departed handling first — it's the most likely to bite in production — then the Apache/Pebble health-check gap.

| | |
|---|---|
| Repo | canonical/wordpress-k8s-operator @ `9de6d14` (2026-07-21) |
| Charms | wordpress-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3, charmhub latest/stable rev 180; also concierge-k8s-4 (blocked, no db available on Juju 4) |
| Reviewed | 2026-08-10 |

## What it does

Deploys WordPress on Kubernetes, managed by Juju. Requires a `mysql_client` database relation and supports: plugin and theme install/uninstall via config; optional plugin configuration for Akismet, Launchpad OpenID, and OpenStack Swift object storage; Apache modsecurity WAF via nginx-route integration; COS observability (Prometheus metrics via Apache exporter, Loki log forwarding with custom Apache access-log histogram metrics, Grafana dashboards); configurable PHP settings (upload limits, execution time); secret rotation; and WordPress database upgrade actions. Uses a Rocks-based OCI image (`wordpress_rock/`).

## Deployment log

### Juju 3.6 deployment (rv-wp-deep, concierge-k8s-3)

```
juju add-model -c concierge-k8s-3 rv-wp-deep
juju deploy wordpress-k8s --channel stable --trust
juju deploy mysql-k8s --channel 8.0/stable --trust -n 1
juju integrate wordpress-k8s:database mysql-k8s:database
```

- 16:46:49 — wordpress-k8s agent initialising
- 16:46:58 — blocked "Waiting for db relation/config" (endpoints missing; mysql-k8s uses modern secrets-based interface)
- 16:49:40 — maintenance "Initializing WordPress DB" (database-created event arrived with full data)
- 16:49:56 — active

Total time to active: ~3m. The delay waiting for MySQL initialization and secret handshake is expected.

### Juju 4.0 deployment (rv-wp-juju4, concierge-k8s-4)

```
juju add-model -c concierge-k8s-4 rv-wp-juju4
juju deploy wordpress-k8s --channel stable --trust
```

- 17:01:37 — deploying
- 17:02:00 — blocked "Waiting for db relation/config"

The charm works on Juju 4.0.5. No database was available (mysql-k8s 8.0/stable does not support Juju 4), so the charm correctly entered `blocked`. Workload version (6.8.1) displayed correctly.

### Operations performed

| operation | result |
|---|---|
| `get-initial-password` | returned password `REDACTED` |
| `rotate-wordpress-secrets` | `result: ok` (confirmed secrets rotated in peer relation data) |
| `update-database` | `Success: WordPress database already at latest db version 58975` |
| `update-database dry-run=true` | `Success: WordPress database already at latest db version 58975` |
| `upload_max_filesize=0` | accepted and written to php.ini as `upload_max_filesize = 0` (no suffix — PHP may reject) |
| `post_max_size=0M` | accepted, written as `post_max_size = 0M` |
| `max_execution_time=99999` | accepted, written correctly |
| `max_input_time=999999` | accepted, written correctly |
| `max_execution_time=abc` | rejected by Juju type validation |
| Scale to 2 units | both units active, replica secret keys identical |
| Scale back to 1 unit | clean teardown |
| `blog_hostname=changed.example.com` | nginx-route relation data updated with new `service-hostname` |
| `wp_plugin_openid_team_map=badformat` | crashed: `ValueError: not enough values to unpack` → `error` state (see finding) |
| `wp_plugin_openstack-objectstorage_config=auth-url: http://example.com` | blocked "missing bucket in wp_plugin_openstack-objectstorage_config" (clear error) |
| Reset bad swift config to `""` | recovered to `active` |
| Database relation removal | charm stayed `active` with stale credentials in wp-config.php (see finding) |
| Database re-integration | recovered immediately, new credentials generated (`relation-5_...`) |
| Kill Apache parent process | zombie children held port 80, Pebble service went to `backoff`, charm stayed `active`, Pebble health check still `up`, killing zombies triggered pod restart (see finding) |
| `remove-application wordpress-k8s` | clean teardown, `terminated` → removed without error |

## Observed behaviour

- **Pebble services**: `wordpress` (startup: disabled, started by charm), `apache-exporter` (startup: enabled, current: active). Pebble health checks: `wordpress-ready` (level: alive, period: 10s, `http://localhost`) and `apache-exporter-up` (level: alive).
- **wp-config.php**: 37 lines, correctly generated with `DB_HOST` pointing to `mysql-k8s-primary.rv-wp-deep.svc.cluster.local.:3306`, `DISALLOW_FILE_MODS` and `WP_CACHE` enabled, all 8 secret keys present and identical across units after scale-up.
- **php.ini**: settings applied via regex substitution on the stock PHP 8.3 php.ini. Values lacking proper suffixes (e.g., `upload_max_filesize = 0` instead of `0M`) are written blindly. `upload_max_filesize` is type `string` in `config.yaml`, so Juju accepts bare integers as strings, but PHP expects a size suffix.
- **Workload version**: `6.8.1` on Juju 3.6, `6.8.1` on Juju 4.0, via `wp core version`.
- **Multi-unit**: scaling to 2 units correctly replicates secret keys via the `wordpress-replica` peer relation; both units show identical `auth_key`, `auth_salt`, etc. The follower unit waits for leader installation completion via `_wp_is_installed()` polling with a 10-minute timeout.
- **Database relation removal**: `database-relation-departed` and `database-relation-broken` both fire in the uniter (confirmed in `juju debug-log`). The charm observes neither. `juju status` shows `active`; `wp-config.php` retains stale `DB_HOST`, `DB_USER`, `DB_PASSWORD`. `_current_effective_db_info` correctly returns `None` internally (via `model.get_relation`), but no reconciliation is triggered to act on that.
- **Apache kill → pod restart cascade**: killing the parent `apache2` process (PID 385) with SIGKILL leaves all 6 worker children alive (PIDs 392–396, 427) holding port 80. Pebble detects the parent's exit and tries to restart, failing with `(98)Address already in use`; the service goes to `backoff`. The `wordpress-ready` health check keeps passing because the zombie workers still serve HTTP. When the zombies are killed (or crash), the check fails and, since it's `level: alive`, Kubernetes treats it as a liveness failure and restarts the pod. After the restart, `pebble_ready` fires, the charm reconciles, and recovers — but this is a full pod restart with minutes of downtime. A config-change attempted during the zombie window instead produces `error` state, because `pebble.start()` throws a `ChangeError` the charm doesn't catch.
- **OpenID format validation crash**: `wp_plugin_openid_team_map=badformat` crashes `_encode_openid_team_map` with `ValueError: not enough values to unpack (expected 2, got 1)` at `src/charm.py:1285-1286`. The charm enters `error` ("hook failed: config-changed"). Juju auto-retries the hook, so clearing the config resolves it, but the initial crash is unhandled.
- **nginx-route config propagation**: changing `blog_hostname` correctly updates `service-hostname` in the nginx-route relation application data, driven by `NginxRouteRequirer._config_reconciliation` on `relation-changed`.
- **Apache restart on every config-changed**: a change to `max_execution_time` (which touches php.ini) triggers a full Apache stop/restart via `_core_reconciliation`. The restart is skipped only when neither wp-config nor php.ini content changed; since PHP settings always modify php.ini, every PHP config change causes a brief outage.
- **Pebble check failure event**: `wordpress-pebble-check-failed` fired at 16:55:02 after the zombie children were killed. The charm does not observe this event, so it goes unnoticed.

These behaviours — the zombie process cascade, the database relation removal gap, and the OpenID format crash — are not visible from code review alone.

## Findings

### Missing database relation-broken/departed handler leaves WordPress serving stale DB config
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:189-190`
- **Evidence**: `__init__` observes only `database.on.database_created` and `database.on.endpoints_changed`:
  ```python
  self.framework.observe(self.database.on.database_created, self._reconciliation)
  self.framework.observe(self.database.on.endpoints_changed, self._reconciliation)
  ```
  Confirmed at 16:54:37: `database-relation-departed` and `database-relation-broken` both fired (visible in `juju debug-log`) but neither was observed. `juju status` showed `active`; `kubectl exec` confirmed stale `DB_HOST`, `DB_USER`, `DB_PASSWORD` still present in wp-config.php. `_current_effective_db_info` correctly returns `None` after relation removal, but `_reconciliation` is never called to act on that.
- **Impact**: When the database relation is removed — migration, operator error, infra churn — WordPress keeps running with stale credentials, Apache keeps serving, and the operator sees `active` with no indication anything is wrong.
- **Fix**: Observe `self.on["database"].relation_broken` (and ideally `relation_departed`) and trigger `_reconciliation`, which will detect `_current_effective_db_info` is `None` and set `BlockedStatus`. `DatabaseRequirerEventHandlers` does not emit events for these hooks, so the charm must handle them directly.
- **Linter rule**: flag charms that observe `database_created`/`endpoints_changed` on a `DatabaseRequires` but do not observe `relation_broken`/`relation_departed` on the same relation.

### Killing Apache parent causes cascading failure to pod restart with charm oblivious throughout
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:600-605` (`_start_server`, no pebble check observation), `src/charm.py:540-545` (pebble layer with `level: alive` check)
- **Evidence**: killing the Apache parent (PID 385, `apache2 -D FOREGROUND`, running as root) with SIGKILL leaves 6 `_daemon_` worker children holding port 80. Pebble tries to restart the service and fails with `(98)Address already in use`, going to `backoff`. The health check keeps reporting `up` (21 successes) because zombies still serve HTTP. Killing the zombies makes the check fail; since it's a `level: alive` check, Kubernetes restarts the pod. The charm reports `active` throughout — it never observes `pebble_check_failed`. Recovery via config-change during the zombie window instead produces `error` state (see next finding).
- **Impact**: any Apache parent crash (OOM kill, accidental `kill`, segfault) leaves the workload degraded indefinitely with no operator signal, until an eventual pod restart causes minutes of downtime. Significant reliability gap for production WordPress.
- **Fix**: observe `pebble_check_failed` and set `MaintenanceStatus`/alert; call `pebble.stop()` in `_stop_server` (sends SIGTERM) rather than relying on charm-tracked state; add explicit zombie cleanup or `pebble.replan()` before restart attempts; catch `ChangeError` from `container.start()` in `_start_server()`.
- **Linter rule**: flag charms where `pebble_check_failed` is never observed but Pebble health checks with `level: alive` are defined.

### `_encode_openid_team_map` crashes on malformed input with a bare ValueError traceback
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:1285-1286`
- **Evidence**:
  ```python
  for idx, mapping in enumerate(team_map.split(","), start=1):
      launchpad_role, wordpress_role = mapping.split("=")
  ```
  Setting `wp_plugin_openid_team_map=badformat` raises `ValueError: not enough values to unpack (expected 2, got 1)` at line 1286. It is uncaught: `_encode_openid_team_map` runs before the `check_result()` closure that would normally translate failures into a `WordPressStatusException`, so the raw exception crashes the hook, putting the charm into `error` ("hook failed: config-changed").
- **Impact**: an operator entering a malformed team map (missing `=`) crashes the charm with a traceback rather than a clear blocked status. Juju auto-retries and clearing the config resolves it, but the initial experience is a hard failure.
- **Fix**: wrap `_encode_openid_team_map` in try/except catching `ValueError`, raising `WordPressBlockedStatusException` with a message like "Invalid team map format: expected key=value pairs separated by commas".
- **Linter rule**: not mechanically checkable in general, but pattern-detectable: bare `str.split("=")` unpacking in charm config parsing should be flagged.

### Config change during Apache zombie window crashes the charm (uncaught `pebble.start` ChangeError)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:608` (`_start_server` → `container.start()`, no error handling)
- **Evidence**: during the zombie-window test, a `juju config` change triggered `_core_reconciliation` → `_start_server()` → `self._container().start(self._SERVICE_NAME)`. Since zombie children held port 80, Pebble's start failed with a `ChangeError`, which propagated uncaught, bypassing the `WordPressStatusException` handler and crashing the hook. The charm showed `error` ("hook failed: config-changed").
- **Impact**: an operator trying the natural troubleshooting step of a config change, while Apache is degraded, hits an error state instead of recovering; manual zombie cleanup is required first.
- **Fix**: wrap `container.start()` in try/except `ops.pebble.ChangeError`, raising `WordPressBlockedStatusException` with the pebble error message instead of crashing.
- **Linter rule**: flag bare `container.start()` calls not wrapped in try/except `ops.pebble.ChangeError`.

### php.ini validation is too permissive — invalid values written silently
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:868-873`
- **Evidence**: regex-based php.ini update:
  ```python
  search = f"^{php_config}\\s*=\\s*[^\\s]+"
  new = re.sub(search, f"{php_config} = {php_config_value}", new, flags=re.MULTILINE)
  ```
  Values like `upload_max_filesize=0` (missing `M` suffix) are written without validation. If a setting were commented out in the stock php.ini, the regex would not match and the setting would be silently ignored — not currently triggered for the four managed settings (`max_input_time` happens to have both a commented and an uncommented line, so it works today), but a latent defect that a future OCI image change could trip.
- **Impact**: silently writing invalid PHP INI values can break PHP at runtime in non-obvious ways, with no warning to the operator.
- **Fix**: verify each expected key is present with a valid value after substitution, or use a proper INI-manipulation library; match both commented and uncommented forms of each key.
- **Linter rule**: not mechanically checkable.

### Unnecessary Apache restart on every PHP-related config change
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:928-937`
- **Evidence**: `_core_reconciliation()` compares generated wp-config/php.ini against current files, correctly avoiding no-op writes — but on any difference:
  ```python
  if wp_config != self._current_wp_config():
      self._stop_server()
      self._push_wp_config(wp_config)
  if php_ini != self._current_php_ini():
      self._stop_server()
      self._update_php_ini(php_ini)
  self._start_server()
  ```
  Changing `max_execution_time` triggers a stop → update → start cycle (~2s observed downtime). `blog_hostname` changes do not trigger a restart, since they touch neither file — the impact is limited to PHP config changes.
- **Impact**: every PHP config change causes a brief outage; several changes in sequence accumulate unnecessary downtime for a production site.
- **Fix**: restart Apache only for wp-config changes; use `apache2ctl graceful` for php.ini changes (mod_php reloads PHP config per request, no full restart needed).
- **Linter rule**: not mechanically checkable.

### No limit on database relations causes hook failure (open issue #336)
- **Severity**: medium
- **Kind**: bug
- **Where**: `metadata.yaml` (database relation)
- **Evidence**: GitHub issue #336 (2025-11-25) reports that relating multiple databases causes `hook failed: storage-attached`. `metadata.yaml` declares:
  ```yaml
  requires:
    database:
      interface: mysql_client
  ```
  with no `limit`, unlike `nginx-route`, which correctly sets `limit: 1`. Issue is open and confirmed.
- **Impact**: relating multiple MySQL charms simultaneously crashes the charm rather than producing a clear error message.
- **Fix**: add `limit: 1` to the `database` relation in `metadata.yaml`.
- **Linter rule**: flag `requires` relations using `mysql_client` or similar single-database interfaces without `limit`.

### Deferred storage event lacks retry limit
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:1554-1557`
- **Evidence**:
  ```python
  if not self._storage_mounted():
      logger.info("Storage is not ready, reconciliation deferred")
      self.unit.status = WaitingStatus("Waiting for storage")
      _event.defer()
      return
  ```
  The event is deferred indefinitely with no timeout or escalation if storage provisioning fails permanently.
- **Impact**: a permanent storage failure hangs the charm in "Waiting for storage" forever instead of surfacing a `BlockedStatus`.
- **Fix**: track a retry counter (via `StoredState`) or timeout after N defers, then transition to `BlockedStatus` with an actionable message.
- **Linter rule**: flag `event.defer()` calls not paired with a visible retry counter or timeout mechanism in the same method.

### `_set_version` failure silently ignored
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:203-207`
- **Evidence**:
  ```python
  if version_result.return_code != 0:
      logger.error("WordPress version command failed with exit code %d.", version_result.return_code)
      return
  ```
  If `wp core version` fails, the error is logged but no workload version is set; the operator sees no version in `juju status` and no indication of failure.
- **Fix**: set a fallback version string ("unknown") or retry on the next `update-status`.
- **Linter rule**: not mechanically checkable.

### wp-cli addon list uses fixed retry intervals without jitter
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:968-977`
- **Evidence**:
  ```python
  for wait in (1, 3, 5, 5, 5):
      ...
      time.sleep(wait)
  ```
- **Impact**: minor; multiple units hitting a transient `wp plugin list` error simultaneously would retry in lockstep.
- **Fix**: add random jitter (e.g., `time.sleep(wait + random.uniform(0, 1))`).
- **Linter rule**: not mechanically checkable.

### `state.py` docstring copy-paste error mentions "Jenkins" instead of "WordPress"
- **Severity**: nit
- **Kind**: docs
- **Where**: `src/state.py:74`
- **Evidence**:
  ```python
  proxy_config: Proxy configuration to access Jenkins upstream through.
  ```
- **Fix**: change "Jenkins" to "WordPress".
- **Linter rule**: mechanically checkable with a project-specific spellcheck for charm-name mismatches.

### Architecture doc outdated: claims WordPress 6.4.3 on Ubuntu 20.04
- **Severity**: nit
- **Kind**: docs
- **Where**: `docs/reference/charm-architecture.md:80-83`
- **Evidence**: the doc states "Currently, WordPress version 6.4.3 is used alongside Ubuntu 20.04 LTS base image." The observed deployment runs WordPress 6.8.1, `charmcraft.yaml` declares `ubuntu@22.04`, and PHP is at 8.3 (`/etc/php/8.3/apache2/php.ini`). `docs/tutorial.ipynb` also shows WordPress 6.4.3 (rev 87) in example output, versus the current stable rev 180 / WordPress 6.8.1.
- **Fix**: update the architecture doc to reflect WordPress 6.8.1 and Ubuntu 22.04; update the tutorial notebook output.
- **Linter rule**: not established.

## Worth copying

- **Custom exception hierarchy for status management** (`src/exceptions.py`): `WordPressStatusException` with subclasses `WordPressBlockedStatusException`, `WordPressWaitingStatusException`, `WordPressMaintenanceStatusException` encode both status type and message; a top-level handler catches these and sets unit status — cleaner than scattering `self.unit.status = BlockedStatus(...)` throughout.
- **Comprehensive unit test mocking system** (`tests/unit/wordpress_mock.py`): `WordpressPatch` provides a full virtual container with mock filesystem, wp-cli command registry, and mock MySQL database, letting tests inspect what WordPress "sees" without a real container.
- **Plugin reconciliation as a reusable pattern** (`src/charm.py:1184-1204`): `_activate_plugin`/`_deactivate_plugin` with options dictionaries make Akismet, OpenID, and Swift plugin management cleanly reusable, each following check-config → activate/deactivate → set/delete options → report-errors.
- **`DISALLOW_FILE_MODS` enforced** (`src/charm.py:357-358`): sets `DISALLOW_FILE_MODS` and `AUTOMATIC_UPDATER_DISABLED` in wp-config.php, making WordPress immutable from the admin panel.
- **COS integration with custom logfmt metrics pipeline** (`src/cos.py:90-130`): `ApacheLogProxyConsumer` extends `LogProxyConsumer` to add a Promtail metrics pipeline extracting `request_duration_microseconds` from Apache access logs as a Prometheus Histogram with custom buckets, and drops `/server-status` entries.
- **Workload version from the actual application** (`src/charm.py:196-209`): `_set_version` runs `wp core version` rather than hardcoding it.
- **Replica consensus pattern** (`src/charm.py:307-328`): leader initializes secret keys in peer relation data on `leader_elected`; followers poll via `_replica_consensus_reached()` in `_core_reconciliation()` until secrets are available.

## Common-practice notes

- **Follows**: Diátaxis documentation structure (`docs/tutorial`, `docs/how-to`, `docs/reference`, `docs/explanation`); `charmcraft.yaml` uv plugin; `data-platform-libs` for database integration; `src/` layout; ops framework idioms; standard OCI resource pattern; multiple action definitions with params; `assumes: k8s-api`.
- **Drifts**: uses `ops.testing.Harness` (deprecated in ops 3.5, emits `PendingDeprecationWarning` on every test run); ops now recommends the `scenario` framework.
- **Drifts**: `DatabaseRequires` usage calls `fetch_relation_field(relation.id, "endpoints")` directly (`src/charm.py:574`) rather than the library's higher-level event properties — works, but bypasses the library's secret resolution and event-driven design.
- **Drifts**: `charmcraft.yaml` builds only on `ubuntu@22.04`; many newer charms declare multiple bases. Reasonable given WordPress 6.8/PHP 8.3 on 22.04.
- **Drifts**: single monolithic `charm.py` at 1580 lines is large by modern standards, though well-factored; plugin reconciliation could be split into separate modules.
- **Drifts**: `JujuVersion.from_environ()` deprecation in bundled `data_interfaces.py` — a library issue, not charm-specific, but the charm ships this code.

## Tests

### Unit tests
93 tests passed (`PYTHONPATH=src:lib uv run --group unit --group lint python -m pytest tests/unit/ -v -p no:craft_application` on Python 3.14). `craft_application` plugin disabled due to a system-level `pyOpenSSL` incompatibility (environment issue, not a charm defect).

Strong coverage: WordPress secret key generation/rotation, replica consensus, database relation data parsing (with/without explicit port), wp-config.php generation with all secret keys and proxy config, wp-cli install command generation, status transitions (waiting for storage → consensus → database → active), theme/plugin reconciliation, Akismet/OpenID/Swift plugin lifecycle, ingress relation data, PHP ini generation, Promtail/Loki config generation.

Coverage gaps relative to the findings above:
- No test for database relation-broken triggering reconciliation (tests verify `_current_effective_db_info` becomes `None`, not that reconciliation fires)
- No test for OpenID team map format validation with malformed input (the `_encode_openid_team_map` crash path)
- No test for pebble `ChangeError` on failed `container.start()`
- No test for `pebble_check_failed` event handling (or the charm's lack thereof)
- No test for PHP ini regex substitution on commented-out settings
- No test for deferred event retry limits
- No test for multiple database relations (issue #336)
- No test for `max_input_time` where the key appears both commented and uncommented in the stock php.ini

### Integration tests
7 test files: `test_core.py`, `test_addon.py`, `test_cos_grafana.py`, `test_cos_loki.py`, `test_cos_prometheus.py`, `test_external.py`, `test_ingress.py`, `test_machine.py`. These go beyond "wait for active/idle":
- `test_core.py` does real HTTP requests, tests WordPress login/post/comment flow, upload file size limit enforcement, and media upload/download via the WordPress API with PIL image verification.
- `test_addon.py` tests theme/plugin install/uninstall with multiple config transitions and verifies `blocked` status on invalid addon names.
- COS tests verify actual Grafana dashboards, Loki log entries, and Prometheus metrics.
- All use `pytest-operator` with real assertions.

### Spread tests
`spread.yaml` defines a tutorial test using concierge to set up MicroK8s on an ubuntu-24.04 multipass VM. CI-only.

## Docs

- **README.md**: clear — badges, overview, deploy instructions, actions list, links to full documentation.
- **docs/**: full Diátaxis structure with 30+ markdown files; architecture doc is thorough and well-diagrammed.
- **Charmhub description**: well-written and current, links to ReadTheDocs-hosted docs.
- **Doc/reality mismatches**:
  - `docs/reference/charm-architecture.md:80-83`: claims "WordPress version 6.4.3 is used alongside Ubuntu 20.04 LTS base image"; actual deployment runs WordPress 6.8.1 on Ubuntu 22.04 with PHP 8.3. Also mentions PHP 7 support for the `wordpress-launchpad-integration` plugin, since updated.
  - `docs/tutorial.ipynb`: example output shows `wordpress-k8s 6.4.3` with revision 87; current stable is revision 180 with WordPress 6.8.1.

## Open questions

- **Full COS integration**: not tested end-to-end — `grafana-agent-k8s` requires a full COS stack (grafana-cloud-config, send-remote-write) needing additional charms. COS endpoints are properly declared and the `ApacheLogProxyConsumer` design looks correct.
- **Juju 4 with database**: not tested because `mysql-k8s` 8.0/stable has no Juju-4-compatible (ubuntu@24.04) builds. wordpress-k8s itself works on Juju 4 (confirmed without a database — correctly enters `blocked`). Should be retested once mysql-k8s gains Juju 4 support.
- **Database credential rotation on re-relation**: re-adding the database relation creates new credentials (e.g., `relation-5_...` instead of `relation-4_...`) with the same database name; WordPress detects existing tables and skips re-installation. Behaviour if the database is dropped between relation cycles is untested.
- **Pod restart behaviour with persistent storage**: pods restarted during testing (Apache kill cascade) and the charm recovered correctly, but uploads storage reattachment was not explicitly verified.
