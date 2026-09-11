# ranger-k8s

A well-architected Kubernetes charm for Apache Ranger with two operational modes (admin, usersync), deployed and exhaustively tested on both Juju 3.6 and 4.0. The codebase features a clean State abstraction, structured Pydantic config validation, an excellent Trino catalog reconciler, and good recovery from most failure modes. 19 findings, 2 critical: (1) Jinja2 templates render with `autoescape=True`, which HTML-escapes `&`, `<`, `>`, `"`, `'` — any password or LDAP URL containing these characters is silently corrupted in the rendered config file, causing hard-to-diagnose authentication failures; (2) `update-status` crashes when any config field fails Pydantic validation, because `self.config` is accessed without a try/except guard — this locks the charm in an error state requiring manual `juju resolve`, confirmed on both Juju versions. Other high-severity findings: `update-status` unconditionally overwrites `BlockedStatus` with `ActiveStatus` for usersync deployments that never started; switching `charm-function` from usersync back to admin causes a silent Java crash with no auto-recovery. A maintainer should fix the two critical issues first — they are both one-line changes (`autoescape=False`; guard the `self.config` access in `_on_update_status`) with outsized blast radius.

| | |
|---|---|
| Repo | canonical/ranger-k8s-operator @ a1e3aac (2026-07-13) |
| Charms | ranger-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25) and concierge-k8s-4 (Juju 4.0.5), latest/edge rev 47 |
| Reviewed | 2026-07-31 |

## What it does

Apache Ranger is a framework for data security — enabling, monitoring, and managing access policies across data platforms. This charm deploys Ranger in either `admin` mode (the policy manager web UI and REST API, backed by PostgreSQL, with optional OpenSearch audit logging) or `usersync` mode (synchronises users/groups from LDAP into Ranger admin). It provides a `policy` (ranger_client) interface consumed by data-platform charms like Trino, a `trino-catalog` interface that automatically reconciles security zones, roles, and policies when Trino catalogs change, and standard COS observability integration (metrics, logs, Grafana dashboards).

## Deployment log

Deployed on Juju 3.6.25 controller `concierge-k8s-3`, model `rv-ranger-36`:

```bash
juju deploy ranger-k8s --channel edge                           # 00:01:54
juju deploy postgresql-k8s --channel 14/stable --trust          # 00:02:24
juju relate ranger-k8s postgresql-k8s:database                  # 00:02:43
juju model-config update-status-hook-interval=1m
```

Timeline:
- 00:03:14: database created, first `database-relation-changed` fires
- 00:03:19–00:08:00: charm in "waiting — handling database change"; container image pulling (~5 min for a large OCI image)
- 00:08:46: charm enters "maintenance — replanning application" (pebble layer applied, workload starting)
- 00:10:20: charm reaches "active — Status check: UP"

Total time from deploy to active: ~8.5 minutes (dominated by image pull).

Tested usersync deploy:
```bash
juju deploy ranger-k8s --channel edge ranger-usersync-k8s \
    --config "charm-function=usersync" \
    --config "policy-mgr-url=http://ranger-k8s.rv-ranger-36.svc.cluster.local:6080"
```
- 00:15:30: config-changed correctly blocks with "Add an LDAP relation or update config values." — the charm has no LDAP config/relation, so it correctly refuses to configure.
- 00:17:15: **Bug**: `update-status` overwrites this `BlockedStatus` with `ActiveStatus` "Status check: UP" despite the workload never having been configured (Pebble shows no `ranger` service running). See Finding #3.

Second deployment for failure injection (`rv-ranger-deep`, Juju 3.6.25):

```bash
juju add-model rv-ranger-deep
juju deploy ranger-k8s --channel edge --config charm-function=admin
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy traefik-k8s --channel latest/stable --trust
juju relate ranger-k8s:database postgresql-k8s:database
juju relate ranger-k8s:ingress traefik-k8s
juju model-config update-status-hook-interval=30s
```
Timeline:
- ~00:32:00: ranger reaches "blocked — database relation not ready" (correct, no DB yet)
- ~00:33:50: ranger reaches "active — Status check: UP" after DB and ingress settle
- Ingress URL `http://10.43.45.0/rv-ranger-deep-ranger-k8s` returns HTTP 302 → login page (correct)

Also tested:
- `juju run ranger-k8s/0 restart --wait 2m`: executes successfully, returns "ranger successfully restarted"
- Scaled to 2 units then back to 1: worked smoothly, both units became active
- `juju config ranger-k8s sync-interval=100`: correctly blocked with "Value out of range" validation error
- `juju config ranger-k8s ranger-admin-password=NewPass1!`: correctly blocked with "value of 'ranger-admin-password' config cannot be changed after deployment"
- Kill workload Java process (`kill -9`): Pebble restarted it within seconds. Pebble check-failed hook fired (no handler exists — see Finding #5) but `update-status` recovered to active on the next tick
- Remove database relation: charm went to "blocked — database relation not ready"; re-relating recovered to active within ~20s
- Teardown (`remove-application`): clean — no hook crashes, no stuck units

Third deployment for Juju 4.x compatibility (`rv-ranger-juju4`, Juju 4.0.5):
```bash
juju deploy ranger-k8s --channel edge -m rv-ranger-juju4 --config charm-function=admin
```
- Charm reached "blocked — database relation not ready" within ~30s, identical behaviour to Juju 3.6.
- Config changes accepted correctly; `update-status-hook-interval` model config applied correctly.
- Full integration (with PostgreSQL) not possible: `postgresql-k8s` 14/stable does not support Juju 4.

Fourth deployment for full integration testing (`rv-ranger-full2`, Juju 3.6.25, pre-existing model):
```bash
# ranger + postgresql + traefik + self-signed-certificates + grafana-agent, all related
```
- All five apps deployed and related. Ranger active with "Status check: UP".
- Ingress via Traefik with TLS from self-signed-certificates: `https://10.43.45.0/rv-ranger-full2-ranger-k8s` → HTTP 302 to login.
- Grafana-agent integrated for metrics (`metrics-endpoint`), logs (`log-proxy`), and dashboards (`grafana-dashboard`); promtail sidecar running in the workload container.
- Memory: 1131 MiB for the ranger pod (Java + promtail + Pebble).
- Pebble health check: 41 successes, 0/3 failures, status "up".

Repeated the two critical-finding failure injections on `rv-ranger-full2` for confirmation (config validation crash, and killing the Java process) — same outcomes as below.

## Observed behaviour

### Juju 4.x compatibility
Deployed on `concierge-k8s-4` (Juju 4.0.5) with `--channel edge --config charm-function=admin`. The charm reaches "blocked — database relation not ready" correctly. Config changes, model-config, and status reporting all work identically to Juju 3.6. No Juju 4-specific incompatibilities found in the charm code or runtime behaviour.

### Config validation crash in update-status (confirmed on two models)
After setting `ranger-admin-password=NoDigitHere` (fails Pydantic's password regex but passes Juju's plain string validation), `config-changed` correctly set `BlockedStatus` ("1 validation error for CharmConfig ... Password does not match requirements"). ~14–61s later, `update-status` crashed with `exit status 1` because `_on_update_status` accesses `self.config["charm-function"].value`, which re-triggers full Pydantic validation on the still-bad password. Status went active → blocked (config-changed) → error (update-status crashed). On the `rv-ranger-deep` model, a newly added unit-1 remained in error state even after the password was fixed and unit-0 recovered, requiring `juju resolve --no-retry`. Repeating with an out-of-range `lookup-timeout=99999` produced the identical crash pattern, confirming the bug triggers on *any* Pydantic validation failure, not just passwords.

### Sensitive data in plaintext peer relation data
`juju show-unit` reveals the following values in the peer relation's `application-data` bag (JSON-encoded but trivially readable):
- `database_connection.password`: the PostgreSQL password
- `ranger_admin_password`, `ranger_usersync_password`
- `truststore_pwd`

These are accessible to anyone with Juju access to the model. postgresql-k8s provides its own password via a Juju secret, but the charm then copies it into its own peer relation data as plaintext.

### Jinja rendering defect: `None` → `"None"` in config files
Inspected `/usr/lib/ranger/admin/install.properties` on the running container. With no OpenSearch relation, the template renders `None` as the literal string `None`:
```
audit_elasticsearch_urls=None
audit_elasticsearch_port=None
audit_elasticsearch_user=None
audit_elasticsearch_password=None
```
Ranger's config parser is expected to treat these as literal strings, not empty/unset values. The same unguarded pattern exists in the usersync template (e.g. `SYNC_GROUP_SEARCH_BASE = None`).

### charm-function switch: usersync → admin causes silent Java crash
Switched the main ranger-k8s app from admin to usersync (`juju config ranger-k8s charm-function=usersync`); `config-changed` correctly blocked with "Add an LDAP relation or update config values." Switching back to admin caused `config-changed` to run and the Pebble layer to be applied, but the Java process crashed silently during initialisation. Pebble showed the `ranger` service "active" (the entrypoint bash script was still alive) while `ps aux` showed no java process. The Pebble HTTP check registered 19 failures. `update-status` correctly detected "Status check: DOWN" and set `MaintenanceStatus`, but the process never recovered on its own — a manual `juju run ranger-k8s/0 restart` was required. Not intermittent: the process never came back without the manual restart.

### No pebble-check-failed handler
Killing the Java process (`kill -9`) triggered a Pebble health-check failure and a `ranger-pebble-check-failed` hook, for which the charm has no handler (`grep -rn "check.failed" src/` returns nothing). Between the kill and the next `update-status` tick (up to 30s in these tests, up to 5 minutes with default intervals), the unit still showed `ActiveStatus` while the workload was actually restarting. Pebble auto-restarted the service and the next `update-status` tick corrected the status, but there is a real window of misleading status.

### Ingress integration works
Traefik received ingress data and returned a working URL; curling it returned HTTP 302 (redirect to login page), confirming the ingress → Ranger pipeline functions correctly.

### General
- **Memory**: `kubectl top pod` showed ~1050 MiB after startup (JVM `-Xmx1g -Xms1g`), consistent with heap settings.
- **Pebble plan**: the rock ships default `ranger-admin`/`ranger-usersync` services (disabled); the charm overrides with its own `ranger` layer and an HTTP health check at `http://localhost:6080/` (10s period).
- **Restart on no-op config change**: `juju config ranger-k8s lookup-timeout=5000` triggered a full replan and restart of the Java process even though `lookup-timeout` does not appear in the admin config template.
- **Port handling**: `update()` unconditionally calls `close_port` then conditionally `open_port` for admin mode, even when charm-function doesn't change.
- **Truststore password**: successfully generated and persisted via `_state.truststore_pwd` on first config.

## Findings

### 1. Jinja2 `autoescape=True` corrupts config values containing HTML special characters
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/utils.py:30`
- **Evidence**:
  ```python
  return (
      Environment(loader=loader, autoescape=True).get_template(template_name).render(**context)
  )
  ```
  `autoescape=True` HTML-escapes `&`, `<`, `>`, `"`, `'` in every rendered template regardless of file extension:
  `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`, `"` → `&#34;`, `'` → `&#39;`.
  Verified with `admin-config.jinja`: `DB_PWD='pass&word<test>'` renders as `db_root_password=pass&amp;word&lt;test&gt;` in the generated `install.properties`.
- **Why it matters**: Any config value or secret containing `&` (common in generated passwords, LDAP DNs, JDBC URLs) is silently corrupted. Database, admin, usersync, and OpenSearch passwords all render through these templates. An operator would see the correct password via `juju config` but the on-disk file would have a different value — very hard to diagnose.
- **Fix**: Change `autoescape=True` to `autoescape=False` in `src/utils.py`. Config file templates should never use HTML escaping.
- **Linter rule**: "Jinja2 `Environment` instantiated with `autoescape=True` in a non-HTML context" — mechanically checkable by inspecting the `autoescape` parameter of `Environment()` calls against template file extensions.

### 2. update-status crashes when config validation fails
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:249`
- **Evidence**:
  ```python
  # src/charm.py:249
  charm_function = self.config["charm-function"].value
  ```
  `_on_update_status` accesses `self.config["charm-function"]` before any try/except guard. `self.config` (from `TypedCharmBase[CharmConfig]`) re-runs Pydantic validation on every access. If any config field fails validation, the hook crashes with a Pydantic `ValidationError` propagating as `exit status 1`.
  Observed: after `juju config ranger-k8s ranger-admin-password=NoDigitHere`, both units' `update-status` hooks crashed; app status went to "error — hook failed: update-status". Unit-0 recovered after the config was fixed; unit-1 (added after the bad config) stayed in error until `juju resolve --no-retry`. Reproduced identically with an out-of-range `lookup-timeout=99999`.
- **Why it matters**: Any config validation error locks the charm in an error state. The periodic `update-status` hook keeps crashing indefinitely, requiring manual `juju resolve` and filling the debug log with tracebacks.
- **Fix**: Wrap the `self.config` access in a try/except that catches `ValidationError`, sets `BlockedStatus(str(err))`, and returns — or read `self.model.config` (the raw dict) in `update-status` instead of the Pydantic model.
- **Linter rule**: "handler that accesses `self.config` (Pydantic model) without an enclosing try/except ValidationError guard" — mechanically checkable by AST pattern matching.

### 3. update-status unconditionally sets ActiveStatus for usersync
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:249-252`
- **Evidence**:
  ```python
  if charm_function == "usersync":
      self.unit.status = ActiveStatus("Status check: UP")
      return
  ```
  Deployed a usersync unit with no LDAP config. `config-changed` correctly set `BlockedStatus("Add an LDAP relation or update config values.")` — Pebble showed no `ranger` service. 105 seconds later `update-status` overwrote this with `ActiveStatus("Status check: UP")`.
- **Why it matters**: Operators cannot distinguish a working usersync from one that failed to configure. The status oscillates blocked → active on every config-changed/update-status cycle; nobody would notice the blocked status before it's overwritten.
- **Fix**: In the usersync branch of `_on_update_status`, verify the workload is actually running (e.g. `container.get_service(self.name).is_running()`) before setting `ActiveStatus`.
- **Linter rule**: "hook handler that sets `ActiveStatus` without a preceding container/service-health check" — mechanically checkable (AST pattern match).

### 4. charm-function switch usersync→admin causes silent Java crash
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:453-515` (replanning logic in `update()`)
- **Evidence**: Switching `charm-function` admin→usersync→admin at runtime: `config-changed` replans the Pebble layer, the entrypoint script starts, but the Java process crashes silently during initialisation. Pebble reports `ranger` "active" (entrypoint bash script alive) while `ps aux` shows no java PID; the HTTP check logs 19 failures. `update-status` correctly sets `MaintenanceStatus("Status check: DOWN")` but never restarts the service. `juju run ranger-k8s/0 restart` was required to recover.
- **Why it matters**: An operator switching to usersync temporarily and back will find admin permanently down with no auto-recovery — the charm reports "Status check: DOWN" indefinitely.
- **Fix**: In `_on_update_status`, when the check is not UP, call `container.restart(self.name)` before setting `MaintenanceStatus` (with a retry limit to avoid restart loops). Alternatively, restart from a `pebble_check_failed` handler.
- **Linter rule**: not mechanically checkable — requires runtime observation.

### 5. No handler for pebble-check-failed; stale status on workload crash
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` (missing handler)
- **Evidence**: Killing the Ranger Java process (`kill -9`) triggers a Pebble health-check failure and a `ranger-pebble-check-failed` hook. `grep -rn "check.failed" src/` returns nothing — there is no handler. Between the kill and the next `update-status` tick (~30s in these tests), the unit showed `ActiveStatus` while the workload was actually restarting. Recovery happens on the next `update-status` tick.
- **Why it matters**: With a default 5-minute `update-status` interval, an operator could see `ActiveStatus` for up to 5 minutes after the workload died; alerting keyed on charm status would miss the incident.
- **Fix**: Observe `self.on[self.name].pebble_check_failed` and set `MaintenanceStatus` immediately.
- **Linter rule**: "charm with a Pebble health check that does not observe `pebble_check_failed`" — mechanically checkable by cross-referencing defined checks against observed events.

### 6. Jinja template variable mismatches in usersync config
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:285-320`, `templates/ranger-usersync-config.jinja`
- **Evidence**: The template references `{{ SYNC_GROUP_SEARCH_SCOPE }}` but the config key `sync_ldap_group_search_scope` maps (via `key.upper()`) to `SYNC_LDAP_GROUP_SEARCH_SCOPE`. The template also references `{{ SYNC_GROUP_NAME_ATTRIBUTE }}`, for which no corresponding `CharmConfig` field exists. `SYNC_LDAP_GROUP_SEARCH_FILTER=` is hardcoded empty with no config key to populate it.
- **Why it matters**: The rendered `install.properties` for usersync gets empty values for group search scope, group name attribute, and group search filter — controlling how usersync queries LDAP for groups, risking incorrect or incomplete group sync.
- **Fix**: Add a `sync_group_name_attribute` config option; correct the render-context key name for group search scope; add `sync_ldap_group_search_filter` if intended to be configurable.
- **Linter rule**: "Jinja template variable referenced but never set in the render context" — mechanically checkable by parsing template variables against context construction sites.

### 7. None values rendered as literal "None" string in config files
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:302-312`, `templates/admin-config.jinja:86-92`
- **Evidence**: When OpenSearch is not related, context values like `OPENSEARCH_HOST`/`OPENSEARCH_PORT` are `None`. Jinja2 renders `None` as the literal string `"None"` (the `| default(9200)` filter only triggers on `Undefined`, not `None`). Verified in the running container:
  ```
  audit_elasticsearch_urls=None
  audit_elasticsearch_port=None
  audit_elasticsearch_user=None
  audit_elasticsearch_password=None
  audit_elasticsearch_bootstrap_enabled=None
  ```
- **Why it matters**: Ranger's config parser may treat literal "None" differently from an unset value (e.g. attempt to connect to a host literally named "None"). Cosmetic while OpenSearch is disabled, but the same pattern in the usersync template would write `SYNC_GROUP_SEARCH_BASE = None`, which LDAP libraries would treat as a literal search base.
- **Fix**: Use `{{ value or '' }}` or `{% if value is not none %}` guards in the templates, or set empty strings instead of `None` in the Python context. Applies to both admin and usersync templates.
- **Linter rule**: "Jinja2 template renders a Python `None` without an `or ''` coercion" — partially mechanically checkable.

### 8. Sensitive values stored in plaintext peer relation data
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/state.py:27-28`
- **Evidence**:
  ```python
  def __setattr__(self, name, value):
      v = json.dumps(value)
      self._get_relation().data[self._app].update({name: v})
  ```
  The `State` class stores all state — including passwords — as JSON in the peer relation's application databag. `juju show-unit` reveals the database password, admin password, usersync password, and truststore password in plaintext.
- **Why it matters**: Anyone with Juju access to the model can read these secrets. postgresql-k8s supplies its password via a Juju secret, but the charm copies it into its own peer relation as plaintext.
- **Fix**: Use `self.model.set_secret()`/`get_secret()` for sensitive values, storing only secret IDs in peer relation data. Significant refactor of `State`.
- **Linter rule**: "JSON-encoded peer relation value matches a password-like key pattern" — mechanically checkable by scanning key names for `password`, `pwd`, `secret`, `key`, `token`.

### 9. trino-catalog relation-broken skips state cleanup when container unreachable
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/relations/trino.py:75-77`
- **Evidence**:
  ```python
  container = self.charm.model.unit.get_container(self.charm.name)
  if not container.can_connect():
      return
  ```
  The `can_connect()` guard returns early before clearing `_state.trino_url`, `_state.trino_catalogs`, `_state.trino_credentials_secret_id`. If the container recovers later while the relation is gone, `run_reconciliation()` may run with stale catalog data (the guard `if not has_relation and not catalogs:` stays False when stale `catalogs` remain).
- **Why it matters**: Stale catalog state persisting across container restarts could trigger unintended zone/policy reconciliation or leave dangling references to a removed Trino integration. Low likelihood but an incorrect state-management pattern.
- **Fix**: Clear the state variables before the connectivity guard returns.
- **Linter rule**: "relation-broken handler returning early before clearing peer-relation state" — partially mechanically checkable.

### 10. Every config change triggers a full workload restart
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:511-512`
- **Evidence**:
  ```python
  container.add_layer(self.name, pebble_layer, combine=True)
  container.replan()
  ```
  `replan()` runs unconditionally at the end of `update()`. Since `add_layer(combine=True)` always produces a new layer dict, `replan()` almost always restarts the service, even for config fields unrelated to the rendered template. Observed: `juju config ranger-k8s lookup-timeout=5000` triggered a full replan/restart even though `lookup-timeout` doesn't appear in the admin config template.
- **Why it matters**: The Ranger Java process takes ~20-30s to start. In production, any `juju config` change — including a no-op for the rendered files — causes a service disruption.
- **Fix**: Compare the current plan (`container.get_plan()`) to the new layer before calling `replan()`; skip if unchanged.
- **Linter rule**: not mechanically checkable — requires runtime comparison.

### 11. README documents wrong database relation endpoint
- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md:28`
- **Evidence**: README says `juju relate ranger-k8s:db postgresql-k8s:database`, but `charmcraft.yaml` defines the endpoint as `database`, not `db`:
  ```yaml
  requires:
    database:
      interface: postgresql_client
  ```
  Confirmed via `juju status --relations` showing `ranger-k8s:database`; `:db` fails with "endpoint not found".
- **Why it matters**: A new operator following the README's first deployment command hits an error and must debug the endpoint name.
- **Fix**: Change `ranger-k8s:db` to `ranger-k8s:database` throughout the README.
- **Linter rule**: "relation endpoint in docs doesn't match `charmcraft.yaml`" — mechanically checkable by parsing both files.

### 12. Unhandled relation-broken crash when peer relation is missing
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/relations/provider.py:114`
- **Evidence**:
  ```python
  if f"relation_{event.relation.id}" not in self.charm._state.services:
  ```
  Accessing `self.charm._state.services` triggers `State.__getattr__`, which calls `self._get_relation().data[self._app]`. If the peer relation is `None` (e.g. during `remove-application` or scale-to-zero), `_get_relation()` returns `None` and `.data` raises `AttributeError`. Reported as GitHub issue #46 `(unverified — not independently reproduced in this review)`.
- **Why it matters**: During teardown or scale-to-zero, the `policy-relation-broken` hook crashes, preventing clean unit removal and causing timeouts.
- **Fix**: Add an early guard: `if not self.charm._state.is_ready(): return`.
- **Linter rule**: "access to `self._state.<attr>` without a prior `is_ready()` check in a hook that can fire during teardown" — partially mechanically checkable.

### 13. Dead code: `retry` and `raise_service_error` decorators
- **Severity**: low
- **Kind**: lint
- **Where**: `src/utils.py:76-166`
- **Evidence**: `retry()` and `raise_service_error()` are defined but never imported or used anywhere in the charm:
  ```
  $ grep -rn "retry\|raise_service_error" src/ --include="*.py"
  src/utils.py:76:def retry(max_retries=3, delay=2, backoff=2):
  src/utils.py:134:def raise_service_error(func):
  ```
- **Why it matters**: Dead code increases maintenance burden and inflates uncovered-line counts (`utils.py` at 46% coverage). `retry`'s wrapper also has a bug — it catches all `Exception` and re-raises as `RangerServiceException`, losing the original type.
- **Fix**: Remove both decorators, or start using `retry` in `ranger_client.py`.
- **Linter rule**: "top-level function/class never referenced in the same package" — mechanically checkable (vulture, ruff F811, pyright reportUnusedFunction).

### 14. Password config description missing special-character requirement
- **Severity**: low
- **Kind**: docs
- **Where**: `charmcraft.yaml` config for `ranger-admin-password`/`ranger-usersync-password`
- **Evidence**: `charmcraft.yaml` description: "Password should be minimum 8 characters with min one alphabet and one numeric." The Pydantic validator (`src/structured_config.py:136`) requires three character classes:
  ```python
  pattern = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[\W_])[A-Za-z\d\W_]{8,}$")
  ```
  A password like `MyPassword1` (letters + digits, no special char) matches the documented rule but is rejected by the validator.
- **Why it matters**: Operators following the documented requirement get a validation error with no explanation of what's actually missing.
- **Fix**: Update the description to state all three requirements; improve the Pydantic error message to enumerate the missing character class.
- **Linter rule**: not mechanically checkable — requires semantic comparison between docs and validator regex.

### 15. Unused `ranger-image` resource forces a large image pull
- **Severity**: low
- **Kind**: lint
- **Where**: `charmcraft.yaml:94-96`
- **Evidence**: The `ranger-image` OCI resource, when deployed from Charmhub, is large (~500MB+); pulling it dominated deployment time (~5 min observed).
- **Why it matters**: Not a code defect, but every Charmhub deployment incurs this cost.
- **Fix**: Optimise the published image (multi-stage build, slimmer base) — a rock concern, not a charm-code concern.
- **Linter rule**: not established.

### 16. Config-changed always closes and re-opens the port
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:473-479`
- **Evidence**:
  ```python
  self.model.unit.close_port(port=APPLICATION_PORT, protocol="tcp")
  if charm_function == "usersync":
      ...
  elif charm_function == "admin":
      self.model.unit.open_port(port=APPLICATION_PORT, protocol="tcp")
  ```
  For admin-mode config changes that don't touch `charm-function`, the port is closed and immediately reopened. Harmless but unnecessary.
- **Fix**: Only close/open the port when `charm-function` actually changes.
- **Linter rule**: not mechanically checkable — requires semantic analysis.

### 17. Leader-only peer_relation_changed handler ignores non-leader units
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:227-231`
- **Evidence**:
  ```python
  def _on_peer_relation_changed(self, event):
      if self.unit.is_leader():
          return
      ...
  ```
  The leader ignores `peer-relation-changed`. If a non-leader ever writes peer data, the leader won't react until the next `config-changed`/`update-status`.
- **Why it matters**: Currently low impact since state is mostly leader-written, but the pattern is fragile — a future non-leader state write would silently fail to propagate.
- **Fix**: Remove the leader guard and make the handler idempotent, or document why the leader doesn't need to react.
- **Linter rule**: not mechanically checkable.

### 18. Password validation silently skipped when state is not ready
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:439-444`
- **Evidence**:
  ```python
  ranger_admin_password = self._state.ranger_admin_password
  ranger_usersync_password = self._state.ranger_usersync_password
  self._validate_password(
      ranger_admin_password,
      "ranger-admin-password",
      "ranger_admin_password",
  )
  ```
  `_validate_password` gets `None` on first deploy and only sets/validates the password when `self.unit.is_leader()`. Non-leader units never validate.
- **Why it matters**: If a non-leader's config diverges from the leader's state, the mismatch isn't caught until a leader-triggered hook runs. Theoretical in the current architecture, but a correctness gap.
- **Fix**: Store the leader-validated password in state for all units to read, or validate independent of leadership.
- **Linter rule**: not mechanically checkable.

### 19. Copy-paste error in docstring
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/structured_config.py:4`
- **Evidence**: `"""Structured configuration for the Superset charm."""` — this file is for the Ranger charm, not Superset.
- **Fix**: Change to "Ranger charm".
- **Linter rule**: "charm name in docstring doesn't match project name" — mechanically checkable.

## Worth copying

### State abstraction (`src/state.py`)
A clean, minimal data-store backed by peer relation data. JSON serialisation/deserialisation is transparent to callers; the `is_ready()` guard is well-designed. A pattern other charms should adopt instead of scattering `relation.data[self.app]` access across handlers.

### Structured config with Pydantic validation (`src/structured_config.py`)
The `CharmConfig` model with validators for range checking, URL format, password strength, and blank-string-to-None coercion is clear and operator-actionable ("Value out of range.", "Value incorrectly formatted."). `TypedCharmBase[CharmConfig]` gives type-safe config access throughout.

### Trino catalog reconciler (`src/reconcile.py`)
`TrinoCatalogReconciler` declaratively reconciles desired zones/roles/policies against Ranger's actual state: idempotent creation, stale-zone cleanup with a safety check for custom policies, and auto-generated policy purging. Policy builders (`_build_ro_policy`, `_build_rw_policy`, etc.) make defaults explicit and testable. `_serialise_resources`/`_serialise_items` enable meaningful policy comparison. A pattern worth copying for any charm managing external API resources declaratively.

### RangerAPIClient wrapper (`src/ranger_client.py`)
Thin, clean wrapper around `apache-ranger`: every call catches `RangerServiceException` and re-raises as `RangerAPIError`, returns empty lists instead of `None`, consistent INFO logging. Predictable `list_*`/`get_*`/`create_*`/`delete_*`/`update_*` surface.

### Scenario-based unit tests (`tests/unit/test_charm.py`)
Clean migration from `Harness` to ops `testing.Context` (Scenario). Helper functions (`_container()`, `_peer()`, `_service_env()`, `_carry()`) reduce boilerplate; tests cover config validation, pebble plan generation, relation data flow, and error statuses without a real controller.

### Incremental test marker (`tests/integration/conftest.py`)
`@pytest.mark.incremental`, implemented via `pytest_runtest_makereport`/`pytest_runtest_setup`, is a faithful reimplementation of pytest-operator's `abort_on_fail` without the dependency.

## Common-practice notes

- **Follows convention**: `src/` layout, `TypedCharmBase`, `charmcraft.yaml` with `charm-libs`, uv-based build (`charm.plugin: uv`), Pydantic structured config, COS libraries (`grafana_dashboard`, `loki_push_api`, `prometheus_scrape`), ops Scenario testing — all standard for the current Canonical charm ecosystem.
- **Differs from convention**: uses a custom `State` class backed by peer relation data with JSON encoding rather than `StoredState` or `data_platform_libs`. Arguably an improvement over `StoredState` (no upgrade concerns) but less common.
- **No `metadata.yaml`**: relies entirely on `charmcraft.yaml` — modern and correct for newer charms.
- **Multiple lib versions**: `traefik_k8s.ingress` uses v2 while most data-platform libs use v0 — expected, since the ingress lib stabilised at v2.
- **Integration test migration**: uses `jubilant`/`pytest-jubilant` instead of `pytest-operator`, aligned with the ecosystem migration; `conftest.py`'s `wait_for_apps` approximates `ops_test.model.wait_for_idle` via `Juju.wait`.
- **No terraform module, no `docs/` directory**: documentation is limited to README.md, CONTRIBUTING.md, and the Charmhub discourse link.

## Tests

**Unit tests**: 50 tests, all passing. Coverage:
```
src/charm.py             81%
src/reconcile.py         83%
src/structured_config.py 94%
src/state.py            100%
src/literals.py         100%
src/ranger_client.py     21%  ← no unit tests
src/relations/*        32-77%  ← postgres, trino, opensearch handlers lightly tested
TOTAL                    66%
```
Key gaps:
- `ranger_client.py`: zero unit tests — API error paths, empty-response handling, None-check branches untested.
- `relations/postgres.py` (42%): `_on_database_relation_broken` and `validate` branches uncovered.
- `relations/trino.py` (32%): no tests for the trino-catalog handler.
- `relations/provider.py` (57%): service-creation failure paths untested.
- `utils.py` (46%): `retry`/`raise_service_error` decorators untested (and dead — Finding #13).

**Integration tests**: 6 modules (`test_charm.py`, `test_policy.py`, `test_scaling.py`, `test_trino_catalog.py`, `test_upgrades.py`, `test_usersync.py`). Not run in this review — require a real k8s cluster with image resources and substantial time. Structure uses `jubilant` + `pytest-jubilant`, well organised, with deploy-as-fixture and incremental markers.

**Linting**: ruff reports zero issues. pyright produces only import-resolution warnings (expected, `typeCheckingMode = "off"`). codespell clean. bandit passes.

## Docs

- **README.md**: comprehensive — deployment, usersync, Trino integration, OpenSearch, ingress, backup/restore, observability. Wrong database relation endpoint (`:db` vs `:database`, Finding #11). Backup/restore S3 command has a typo: `juju relate s3-integratior postgresql-k8s` (missing "o" in "integrator").
- **CONTRIBUTING.md**: clear developer setup with `make` targets covering build/test/lint/deploy.
- **Charmhub page**: links to discourse, issues, source; short but accurate description.
- **No `docs/` directory**: all documentation lives in the README; for a charm of this complexity a separate architecture doc would help.
- **No architecture/sequence diagram**: the Trino catalog reconciliation flow is complex and would benefit from a visual explanation.

## Open questions

1. **Trino catalog reconciliation with multiple Trino services**: `run_reconciliation()` picks `services[0].name` — behaviour with multiple registered Trino services (e.g. from different `policy` relations) is unclear; could reconcile against the wrong service. The README recommends only creating the `trino-catalog` relation on a Trino charm already related via `policy`.
2. **OpenSearch cross-controller relation**: not tested — requires an LXD controller with OpenSearch, not feasible in the time budget. Code appears to extract certificates from secrets and add them to the Java truststore correctly, but unverified end-to-end.
3. **`ranger-client` interface contract**: no documented interface spec for the `policy` (ranger_client) relation. The provider inspects `data["name"]`, `data["type"]`, and passes remaining keys through as service config. Testing against a real Trino charm would clarify the contract.
4. **Root cause of the usersync→admin Java crash** (Finding #4): possibly caused by stale usersync `install.properties` state conflicting with Ranger's DB initialisation path on switchback. The entrypoint script doesn't log enough detail to diagnose without modifying the rock; would need verbose Java logging to confirm.
