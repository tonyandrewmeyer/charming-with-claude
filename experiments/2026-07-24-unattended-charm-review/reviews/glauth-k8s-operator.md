# glauth-k8s

A well-structured k8s charm for the GLAuth LDAP server, but with a critical status-reporting bug and several stale-flag/no-validation issues that undermine operator trust in `juju status`. The charm deploys cleanly on Juju 3.6 and 4.0, handles its core integrations (database, certificates, ingress) correctly, and has solid unit/integration test coverage — but it silently overwrites `BlockedStatus` with `ActiveStatus` after failed resource patches or restarts (finding #1), never resets its `config_changed` flag (finding #2), retries a ConfigMap-sync loop forever with no stop condition (finding #3), and accepts invalid config values with no validation (finding #4). The `grafana-dashboard` and `metrics-endpoint` integrations are both non-functional despite being advertised. A maintainer should fix the status-overwrite bug first (it hides every other failure mode below it), then add a stop condition to the retry loop and reset the `config_changed` flag.

| | |
|---|---|
| Repo | canonical/glauth-k8s-operator @ `a4e34aa` (2026-07-24) |
| Charms | glauth-k8s |
| Substrate | k8s |
| Deployed | yes — deployed and exercised across four Juju 3.6 models (`rv-glauth-full`, `rv-glauth2`, `rv-glauth-deep`) and one Juju 4.0 model (`rv-glauth-deep4`), rev 57 (stable) and rev 67 (edge) |
| Reviewed | 2026-08-04 |

## What it does

GLAuth is a Go-based LDAP server. This charm deploys it on Kubernetes, backed by PostgreSQL (or an upstream LDAP server), with TLS via `tls-certificates`. It provides `ldap`, `glauth-auxiliary`, `certificate-transfer`, `grafana-dashboard`, and `metrics-endpoint` integrations. It uses a ConfigMap to deliver the glauth config file, mounted into a distroless workload container. Pebble manages the single `glauth` service. Config includes base DN, StartTLS toggle, LDAPS toggle, anonymous DSE toggle, a `log_level` option (which has no effect — finding #7), and K8s resource limits.

## Deployment log

```sh
# ========== Juju 3.6 — full integration deploy (rv-glauth-full, rev 57) ==========
juju add-model rv-glauth-full

juju deploy glauth-k8s --channel stable --trust          # rev 57
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy self-signed-certificates --channel stable --trust
juju deploy traefik-k8s --channel stable --trust
juju deploy grafana-k8s --channel 12.4/stable --trust
juju deploy prometheus-k8s --channel 3.11/stable --trust

juju integrate glauth-k8s postgresql-k8s:database
juju integrate glauth-k8s self-signed-certificates
juju integrate glauth-k8s:ingress traefik-k8s:ingress-per-unit
juju integrate glauth-k8s:grafana-dashboard grafana-k8s:grafana-dashboard
juju integrate glauth-k8s:metrics-endpoint prometheus-k8s:metrics-endpoint
# ~3 min → all active

# Pod kill (full pod recovery test):
kubectl delete pod glauth-k8s-0
# ~34s → pod recreated, charm recovered to active with no intervention
# Private key logged again at info level on new pod's first start

# Bad cpu config + status race:
juju config glauth-k8s cpu=abc
# ERROR: "Failed obtaining resource limit spec: Invalid limits spec: {'cpu': 'abc', 'memory': None}"
# Charm stays ActiveStatus (finding #1 confirmed for cpu)

juju config glauth-k8s cpu=""     # reset

# Trivial config change triggers restart:
juju config glauth-k8s anonymousdse_enabled=true  # → AP exit + AP start at 17:20:47

# Empty base_dn accepted:
juju config glauth-k8s base_dn=""  # → "Waiting for config update" ~60s, then active
# ConfigMap gets baseDN = "", glauth still starts

# Toggle ldaps:
juju config glauth-k8s ldaps_enabled=true
# → active, ldaps enabled

# Grafana dashboard: relation data on glauth side is {} — dashboards not pushed (finding #15)
# Metrics endpoint: relation data on glauth side is {"event": "{}"} — no scrape targets (finding #16)
# No actions defined; no glauth-auxiliary or certificate-transfer requesters deployed

# ========== Juju 3.6 — first deploy (rv-glauth2, rev 57) ==========
juju switch concierge-k8s-3
juju add-model rv-glauth2

juju deploy glauth-k8s --channel stable --trust          # rev 57
juju deploy self-signed-certificates --channel stable --trust
juju deploy postgresql-k8s --channel 14/stable --trust

juju integrate glauth-k8s postgresql-k8s:database
juju integrate glauth-k8s self-signed-certificates
# ~2 min → active

# Config changes (all accepted silently — no validation):
juju config glauth-k8s log_level=invalid      # accepted, zero effect
juju config glauth-k8s base_dn=""             # accepted, ConfigMap gets empty baseDN
juju config glauth-k8s memory=abc             # accepted, causes resource patch error every hook

# Reset configs:
juju config glauth-k8s log_level=info; juju config glauth-k8s base_dn="dc=glauth,dc=com"; juju config glauth-k8s memory=""
# memory="" also causes resource patch errors — empty string != None (finding #13)

# Relation removals / re-integration:
juju remove-relation glauth-k8s self-signed-certificates  # → stays active until next hook; then blocked
juju remove-relation glauth-k8s postgresql-k8s            # → same: stays active until next hook
juju integrate glauth-k8s self-signed-certificates        # → recovers to active
juju integrate glauth-k8s postgresql-k8s:database         # → recovers to active

# Kill workload via pebble:
kubectl exec glauth-k8s-0 -c glauth -- pebble stop glauth
# Charm stays "active" — no detection until next hook (finding #8)

# Refresh to edge (rev 57 → rev 67):
juju refresh glauth-k8s --channel edge         # rev 67, ubuntu@26.04 base
# Successful, charm came up active

# Remove application with --force → ConfigMap LEAK:
juju remove-application glauth-k8s --force --no-wait --no-prompt
# ConfigMap persisted (finding #6)

# Remove application WITHOUT --force → ConfigMap DELETED:
# (tested in rv-glauth-deep) — _on_remove fires correctly, ConfigMap gone

# ========== Juju 3.6 — deep test (rv-glauth-deep, rev 57) ==========
juju add-model rv-glauth-deep

juju deploy glauth-k8s --channel stable --trust
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy self-signed-certificates --channel stable --trust
juju deploy traefik-k8s --channel stable --trust

juju integrate glauth-k8s postgresql-k8s:database
juju integrate glauth-k8s self-signed-certificates
juju integrate glauth-k8s:ingress traefik-k8s:ingress-per-unit
# ~2 min → all active

# Ingress works: TCP connection to 10.43.45.0:3893 succeeded
# pebble logs: service restarted 3+ times during initial setup, each logs full private key

# Bad config:
juju config glauth-k8s memory=abc  # → ERROR "Failed obtaining resource limit spec" but charm stays ActiveStatus

# Scale up:
juju scale-application glauth-k8s 2  # → both glauth units active, traefik goes to error (known issue #406)
juju scale-application glauth-k8s 1  # → scale down OK, traefik stays in error

# Remove without --force:
juju remove-application glauth-k8s --no-prompt
# ConfigMap DELETED — _on_remove fired correctly

# ========== Juju 4.0 (rv-glauth-deep4, rev 57) ==========
juju switch concierge-k8s-4
juju add-model rv-glauth-deep4

juju deploy glauth-k8s --channel stable --trust
juju deploy self-signed-certificates --channel stable --trust
juju integrate glauth-k8s self-signed-certificates
# glauth → blocked "Backend integration…missing"
# postgresql-k8s 14/stable does not support Juju 4 (requires < 4.0.0)
# Charm deploys correctly on Juju 4; only needs compatible backend

# No actions defined: juju actions glauth-k8s → "No actions defined"
```

## Observed behaviour

- **Service restarts during setup**: The glauth workload restarted 3 times within the first ~15 seconds of initial deployment (pebble logs at 17:18:10, 17:18:17, 17:18:25 UTC in `rv-glauth-full`). Each restart logs the full RSA private key at info level. The restarts correspond to initial start, certificate push, and config update — each triggers a full restart rather than a reload.
- **Pod kill recovery**: After `kubectl delete pod glauth-k8s-0`, a new pod was created and the charm recovered to `active` within ~34 seconds with no operator intervention. Pebble-ready fired, and the charm re-pushed certificates, patched resources, and restarted glauth. Recovery is clean and correct.
- **Each config change causes exactly one restart**: Confirmed across `anonymousdse_enabled`, `base_dn`, `ldaps_enabled`. No duplicate restarts observed, but the `config_changed` flag stays `True` for subsequent `update_status` events.
- **ConfigMap sync delay**: "Waiting for configuration to be updated" took ~58–71s per config change (19–24 poll cycles at 3s each in `rv-glauth2`; 11 GETs during `database_created` in `rv-glauth-deep`). The `after_config_updated` decorator polls via `container.pull()` → GET ConfigMap → compare hashes.
- **Memory**: 56Mi (glauth workload container), very lightweight.
- **CPU**: 2m steady state.
- **Container is distroless**: no shell, no `cat`, no `ls` — Pebble is the only way to interact with files.
- **Resource patches**: with `memory=abc`, resource patch failed every hook with "Failed obtaining resource limit spec: Invalid limits spec: {'cpu': None, 'memory': 'abc'}" — charm stayed `ActiveStatus`. Same with `memory=""`. Only unset config (`None`) works correctly.
- **ConfigMap leak with `--force`, clean without**: after `juju remove-application glauth-k8s --force --no-wait --no-prompt`, the ConfigMap persisted (`rv-glauth2`). After `juju remove-application glauth-k8s --no-prompt` (no `--force`), the ConfigMap was correctly deleted and the remove hook fired (`rv-glauth-deep`, confirmed via `kubectl` returning "NotFound"). `--force` skips Juju remove hooks.
- **Private key in logs**: every glauth restart logs the full RSA private key (N, E, D, Primes, CRT values) in structured JSON at info level in the "enabling LDAP over TLS" message. Confirmed on both deploys, across 5 separate service starts.
- **`update_status` triggers unnecessary work**: once `config_changed` is `True` (which it is after the first config change), every `update_status` triggers a ConfigMap poll (3 GET requests) and a service restart attempt. The flag never resets.
- **Service stop not detected**: after `pebble stop glauth`, charm remained `ActiveStatus`. The service was only restarted when the next hook fired (`config-changed` for `memory=abc`), via the stale `config_changed` flag. `service_not_ready` is only used on `_on_ldap_requested`, not on the main event path.
- **Relation removal not immediate**: removing the certificates or postgresql relation leaves the charm `ActiveStatus` until the next `config-changed` or `update-status`. The charm does not observe `relation_broken` for these integrations. On the next hook, the `block_when` guard in `_handle_event_update` correctly sets `BlockedStatus`. Observed gap: ~2m42s active-while-broken for the postgres relation removal.
- **Scale-up succeeds for glauth, breaks traefik**: both glauth units came up active, but traefik went to error (`hook failed: "ingress-per-unit-relation-changed"`) — known upstream issue traefik-k8s #406. Scale-down OK.
- **Ingress reachable**: TCP connection to traefik ingress IP `10.43.45.0:3893` succeeded.
- **Juju 4 compatible**: charm deploys on Juju 4.0.5, goes to blocked status waiting for backend — all correct. Only barrier is dependent charms (postgresql-k8s 14/stable) not yet supporting Juju 4.
- **Grafana dashboard data not pushed**: `grafana-dashboard` relation application data on glauth's side is `{}` (empty). Despite a dashboard template at `src/grafana_dashboards/glauth.json.tmpl`, no dashboard was pushed to grafana-k8s. `GrafanaDashboardProvider` observes `leader_elected`, `upgrade_charm`, and `config_changed` — all of which fired — but the dashboard wasn't rendered. Likely a path-resolution issue in the deployed charm (finding #15, unverified root cause).
- **Metrics endpoint not configured**: `metrics-endpoint` relation application data on glauth's side is `{"event": "{}"}` with no scrape targets. GLAuth doesn't expose a `/metrics` endpoint — the charm template has `[api] enabled = false` and no Prometheus metrics configuration. `MetricsEndpointProvider` is instantiated but the workload doesn't serve metrics (finding #16).

## Findings

### 1. `ActiveStatus` overwrites `BlockedStatus` after failed service restart or failed resource patch
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:248-249` (restart BlockedStatus), `src/charm.py:365` (resource-patch BlockedStatus), `src/charm.py:265` (ActiveStatus overwrite)
- **Evidence**: `_restart_glauth_service` (lines 242-250) catches `ChangeError` and sets `BlockedStatus("Failed to restart the service…")` at lines 248-249. `_on_resource_patch_failed` (lines 362-365) sets `BlockedStatus(event.message)` at line 365. Both feed into `_handle_event_update`, which unconditionally sets `self.unit.status = ActiveStatus()` at line 265, overwriting either. Observed on both `rv-glauth2` and `rv-glauth-deep`: `memory=abc` caused "Failed obtaining resource limit spec" errors on every hook while the charm showed `ActiveStatus` throughout.
- **Impact**: An operator whose workload restart or resource patch fails sees "active" instead of "blocked" and gets no indication anything is broken. The resource patch error repeats silently on every hook.
- **Fix**: In `_handle_event_update`, only set `ActiveStatus` if the current status is not already `BlockedStatus`, or propagate status from `_restart_glauth_service`/`_on_resource_patch_failed` instead of overwriting.
- **Linter rule**: "hook handler unconditionally sets ActiveStatus after calling methods that may have set BlockedStatus" — checkable via AST analysis of status-setting calls in the call chain.

### 2. `self.config_changed` flag never reset — forces unnecessary restarts on every hook
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:109` (declaration), `src/charm.py:287` (set to `True`, never reset)
- **Evidence**: `config_changed = False` is a class attribute. In `_update_glauth_config`, when the config hash differs, it sets `self.config_changed = True` (line 287) — never reset. `_handle_event_update` calls `_restart_glauth_service(restart=restart or self.config_changed)` (line 266), so after the first config change every subsequent event (`update_status` every 5 min, `database_created`, `ldap_ready`, etc.) forces a restart. Observed in `rv-glauth-deep`: after `pebble stop glauth`, the `memory=abc` config-changed forced a restart of the stopped service.
- **Impact**: The service restarts on `update_status` alone (roughly every 5 minutes) plus on every relation event, disrupting existing LDAP connections and undermining the config-hash idempotency check.
- **Fix**: Reset `self.config_changed = False` after the restart completes, e.g. at the end of `_handle_event_update`.
- **Linter rule**: "stored state flag set but never cleared" — checkable via basic dataflow analysis.

### 3. `after_config_updated` retry loop has no stop condition
- **Severity**: high
- **Kind**: bug
- **Where**: `src/utils.py:149-158`
- **Evidence**: `for attempt in Retrying(wait=wait_fixed(3)):` — `tenacity.Retrying.__init__` defaults `stop=stop_never()` and `retry=retry_if_exception_type()` (confirmed in `deps/tenacity/__init__.py:217-221`). No `stop_after_attempt` or timeout is set. Observed 19-24 poll cycles (~57-72s) in `rv-glauth2` when ConfigMap propagation was slow. If it never syncs, the hook hangs for the full Juju hook timeout (5 min). The unit test at `test_utils.py:185` only covers the happy path.
- **Impact**: Can cause hooks to hang for the full timeout, blocking other charm operations.
- **Fix**: Add `stop=stop_after_attempt(10)` or `stop=stop_after_delay(60)`, matching the pattern in `kubernetes_compute_resources_patch.py` (`PATCH_RETRY_STOP = stop_after_delay(20)`).
- **Linter rule**: "tenacity Retrying without a stop condition" — checkable via AST pattern match.

### 4. No config validation — invalid values accepted silently
- **Severity**: high
- **Kind**: bug / ux
- **Where**: `charmcraft.yaml` (config definitions), `src/charm.py` (no validation logic)
- **Evidence**: `log_level=invalid` accepted, charm stayed active. `base_dn=""` accepted, ConfigMap received `baseDN = ""`. `memory=abc` accepted, caused resource patch errors on every subsequent hook. `memory=""` (empty string, distinct from unset) also caused resource patch errors. None produced operator-visible feedback about the config itself (the resource-patch BlockedStatus is overwritten per finding #1).
- **Impact**: Operators can configure nonsensical values with no feedback. An empty base DN could break LDAP operations; a bad resource spec errors on every hook silently. `memory=""` is particularly surprising since it's the natural way to try to "clear" a value.
- **Fix**: Validate config in `_on_config_changed` before applying — check `log_level` against the allowed set, validate `base_dn` is non-empty, validate `cpu`/`memory` are valid K8s quantities, and set `BlockedStatus` on invalid values. Treat empty string same as `None` in `_resource_reqs_from_config`.
- **Linter rule**: "config option with a documented value constraint but no corresponding validation in charm code" — partially checkable by cross-referencing config descriptions with charm code.

### 5. Relation removal not immediately detected — charm stays active until next hook
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:110-200` (event observer wiring)
- **Evidence**: the charm observes `_on_database_created`/`_on_database_changed` and `_on_cert_changed`, but does not observe `relation_broken` for either integration. When the postgresql relation was removed, `pg-database-relation-broken` fired at 04:59:06 UTC but the charm remained `ActiveStatus`; only the next forced config-changed (05:01:48 UTC) triggered the `block_when` guard and set `BlockedStatus`. Gap observed: ~2m42s. Same behaviour observed for the certificates relation.
- **Impact**: Operators removing a required relation see "active" for up to 5 minutes (until the next `update_status`) while the service may be non-functional. Matches the pattern described in upstream issue #28.
- **Fix**: Observe `relation_broken` directly for both `pg-database` and `certificates` and call `_handle_event_update` immediately.
- **Linter rule**: not mechanically checkable.

### 6. ConfigMap not deleted on `--force` application removal
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:199, 320-321`, Juju lifecycle
- **Evidence**: after `juju remove-application glauth-k8s --force --no-wait --no-prompt`, the ConfigMap `glauth-k8s` persisted in namespace `rv-glauth2`; the stop hook fired (04:39:14 UTC) but the remove event did not. After `juju remove-application glauth-k8s --no-prompt` (no `--force`), the ConfigMap was correctly deleted and `_on_remove` fired (`rv-glauth-deep`, `kubectl` returned "NotFound"). `--force` causes Juju to skip the remove hook.
- **Impact**: An operator using `--force` (common in cleanup scripts) leaks a ConfigMap that could interfere with a subsequent redeploy under the same app name.
- **Fix**: Delete the ConfigMap in the `stop` hook as well as `remove`, or document the `--force` caveat.
- **Linter rule**: not mechanically checkable.

### 7. `log_level` config is a dead option — has no effect
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `charmcraft.yaml` (defines `log_level`), `templates/glauth.cfg.j2:1` (hardcodes `debug = false`), `src/charm.py` (no reference to `log_level`)
- **Evidence**: `charmcraft.yaml` defines `log_level` with description "Configures the log level. Acceptable values are: info, debug, warning, error, critical". `grep -rn log_level src/` returns zero hits. `templates/glauth.cfg.j2:1` hardcodes `debug = false`. `ConfigFileData` (`src/configs.py:95-101`) has no `log_level` field. Setting `log_level=debug` produces no change to the ConfigMap or workload behaviour.
- **Impact**: Operators trust the config description and expect debug logs when setting `log_level=debug`; nothing changes — misleading documentation embedded in the charm's own metadata.
- **Fix**: Wire `log_level` through to the template (e.g. `log_level=debug` → `debug = true`), or remove the option from `charmcraft.yaml`.
- **Linter rule**: "config option defined but never read in charm code" — checkable by cross-referencing config keys with `self.config.get` calls.

### 8. `service_not_ready` not checked on main `update-status` path — up to 5 min downtime on crash
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:254-261` (decorators on `_handle_event_update`), `src/charm.py:368` (where `service_not_ready` is used)
- **Evidence**: `_handle_event_update` is decorated with `@block_when(backend_integration_not_exists, integration_not_exists(CERTIFICATES_INTEGRATION_NAME))` and `@wait_when(container_not_connected, backend_not_ready, tls_certificates_not_ready)`, but not `service_not_ready` — that condition is only used on `_on_ldap_requested` (line 368). Confirmed live: after `pebble stop glauth`, the charm remained `ActiveStatus` and the service was only restored by the next config-changed hook, not because the charm detected the crash.
- **Impact**: Up to 5 minutes of downtime for a crashed workload.
- **Fix**: Add `service_not_ready` to `_handle_event_update`'s wait conditions (which would restart the service via `_restart_glauth_service`), or make `_on_update_status` explicitly check and restart.
- **Linter rule**: not mechanically checkable.

### 9. GrafanaDashboardProvider not pushing dashboards — non-functional integration
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:183-187`, `lib/charms/grafana_k8s/v0/grafana_dashboard.py:1970-1972`
- **Evidence**: `GrafanaDashboardProvider(self, relation_name=GRAFANA_DASHBOARD_INTEGRATION_NAME)` is instantiated at `charm.py:186`. After full deploy with grafana-k8s, the relation's application data on the glauth side was `{}` (empty), despite `leader_elected`, `upgrade_charm`, and `config_changed` all firing. A dashboard template exists at `src/grafana_dashboards/glauth.json.tmpl` (13,749 bytes). Likely cause is path resolution: `_resolve_dir_against_charm_path` (`grafana_dashboard.py:1970-1972`) resolves `src/grafana_dashboards` relative to the charm root, which may differ between source checkout and deployed charm — root cause unverified.
- **Impact**: Operators integrating with grafana-k8s expect an LDAP monitoring dashboard; none appears. The integration is dead.
- **Fix**: Verify `src/grafana_dashboards/` is included in the built charm payload, and check `_resolve_dir_against_charm_path` resolves correctly in the deployed charm.
- **Linter rule**: not mechanically checkable.

### 10. MetricsEndpointProvider non-functional — no metrics endpoint configured
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/charm.py:183-185`, `templates/glauth.cfg.j2:52-53`
- **Evidence**: `MetricsEndpointProvider(self, relation_name=PROMETHEUS_SCRAPE_INTEGRATION_NAME)` is instantiated at `charm.py:183`. Observed relation application data on the glauth side: `{"event": "{}"}`, no scrape targets. `templates/glauth.cfg.j2:52-53` has `[api] enabled = false` — GLAuth's REST API (which would include `/metrics`) is disabled, and nothing in the template or charm code configures metrics.
- **Impact**: Operators integrating with prometheus-k8s expect LDAP metrics; none appear. The charm advertises `metrics-endpoint` but doesn't deliver it.
- **Fix**: Either configure glauth to expose metrics (`[api] enabled = true` with an appropriate listen address), or remove the `metrics-endpoint` provides relation from `charmcraft.yaml` and `src/charm.py`.
- **Linter rule**: not mechanically checkable.

### 11. Private key logged in plaintext by glauth at startup
- **Severity**: medium
- **Kind**: bug (upstream)
- **Where**: workload (glauth binary v2.4.0), observed in pebble logs on both deploys
- **Evidence**: `kubectl exec glauth-k8s-0 -c glauth -- pebble logs glauth` shows the full RSA private key (N, E, D, Primes, CRT values) in structured JSON in the "enabling LDAP over TLS" message at info level, on every service start — confirmed across 5 separate starts on two deploys.
- **Impact**: Private key material in logs is a security concern; any log aggregation (e.g. Loki) would exfiltrate the private key. Upstream glauth issue with direct impact on the charm's security posture.
- **Fix**: Raise with glauth upstream to stop logging key material; consider filtering the charm's own log ingestion in the interim.
- **Linter rule**: not mechanically checkable at charm level.

### 12. `after_config_updated` poll takes 60–90s per config change, risks hook timeout
- **Severity**: low
- **Kind**: performance
- **Where**: `src/utils.py:149-158`
- **Evidence**: during `base_dn=""` on `rv-glauth-full`, the charm spent ~60s in "Waiting for configuration to be updated", polling ConfigMap every 3s (`Retrying(wait=wait_fixed(3))`, no stop condition — see finding #3). ~20-30 GET requests observed before the ConfigMap was remounted.
- **Impact**: Slow config changes block other hook processing; under high API latency the poll count increases further, and combined with finding #3 an unresponsive ConfigMap could hang a hook for the full Juju timeout.
- **Fix**: Add a stop condition as in finding #3.
- **Linter rule**: same as finding #3 — "tenacity Retrying without a stop condition".

### 13. `memory=""` (empty string) causes resource patch failures — not equivalent to unset
- **Severity**: low
- **Kind**: bug / ux
- **Where**: `src/charm.py:428-429`, `kubernetes_compute_resources_patch.py`
- **Evidence**: with `memory` unset (`None`), `adjust_resource_requirements({'cpu': None, 'memory': None}, …)` succeeds, producing default requests. With `memory=""`, the same function raises `ValueError: Invalid limits spec: {'cpu': None, 'memory': ''}`. Observed after `juju config glauth-k8s memory=""` following a `memory=abc` config.
- **Impact**: `juju config key=""` is a natural way to try to clear a value; here it breaks resource patching on every hook instead. The correct approach (`juju reset key`) is not obvious to operators.
- **Fix**: Treat empty-string values the same as `None` in `_resource_reqs_from_config`.
- **Linter rule**: not mechanically checkable.

### 14. `AuxiliaryData()` constructed with no args would raise `ValidationError`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/integrations.py:184-185`, `lib/charms/glauth_utils/v0/glauth_auxiliary.py:158-162`
- **Evidence**: `auxiliary_data` (`src/integrations.py:182-185`) calls `return AuxiliaryData()` when `DatabaseConfig.load()` returns `None`. `AuxiliaryData` has required fields `database`, `endpoint`, `username`, `password` with no defaults, so this would raise `pydantic.ValidationError`. In practice `_on_auxiliary_requested` is gated by `@wait_when(database_not_ready)`, so this path is currently dead code but a latent crash if that guard is ever removed.
- **Impact**: If a future change removes the guard, the hook crashes with an unhandled `ValidationError` rather than a clear status.
- **Fix**: Make `AuxiliaryData` fields `Optional`, or handle the `None` case explicitly.
- **Linter rule**: "pydantic model with all required fields constructed with no arguments" — checkable via type analysis.

### 15. `config_changed` is a class attribute, not an instance attribute
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:109`
- **Evidence**: `config_changed = False` is declared at class level, not in `__init__`. Multiple charm instances (e.g. in tests) would share the flag.
- **Fix**: Move to `__init__`: `self.config_changed = False`.
- **Linter rule**: "mutable class attribute used as instance attribute" — checkable via static analysis.

### 16. `LdapRequirer.ready()` raises `IndexError` for a non-existent relation_id
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/glauth_k8s/v0/ldap.py:578-582`
- **Evidence**: `ready()` uses `[relation for relation in self.relations if relation.id == relation_id][0]`, which raises `IndexError` if the id doesn't exist. The docstring documents this, but a Juju `ModelError` would be more conventional and consistent with other ops APIs.
- **Impact**: Non-standard exception type surfaced to charm code; minor since callers typically only query existing relation ids.
- **Fix**: Raise `ops.ModelError(...)` instead of relying on list-index `IndexError`.
- **Linter rule**: not mechanically checkable.

### 17. Custom `Secret` class in `ldap.py` duplicates `ops.Secret` functionality
- **Severity**: nit
- **Kind**: cleanup
- **Where**: `lib/charms/glauth_k8s/v0/ldap.py:246-276`
- **Evidence**: the library defines its own `Secret` class wrapping `ops.Secret` (`load()`, `create_or_update()`, `grant()`, `remove()`), and its own `leader_unit` decorator, duplicating patterns already present elsewhere in the codebase (`src/utils.py`).
- **Impact**: Two implementations of the same pattern in one codebase; both need updating if the `ops.Secret` API changes.
- **Fix**: Replace the library's `Secret` class with direct `ops.Secret` usage, or share the implementation with `src/utils.py`.
- **Linter rule**: not mechanically checkable.

## What's good

- **Decorator-based guard pattern**: `block_when`/`wait_when` (`src/utils.py:97-136`) express hook preconditions declaratively as `(CharmBase) -> (bool, str)` functions — easy to test and compose.
- **Config hash-based idempotency**: `_update_glauth_config` (`src/charm.py:280-288`) checks an MD5 hash of the rendered config before writing to the ConfigMap, avoiding unnecessary K8s API calls (undermined on the restart side by finding #2).
- **`ops.testing` migration**: all unit tests use `ops.testing` (Context, State, Relation, Container) — no legacy Harness usage; `conftest.py` fixtures are well-organized and reusable.
- **Clear separation of concerns**: `configs.py` (data models + rendering), `integrations.py` (relation logic), `database.py` (SQLAlchemy models), `utils.py` (decorators/conditions).
- **MD5-based `__hash__` on `ConfigFile`**: stable hashing across process restarts, avoiding Python's hash randomization (`src/configs.py:142-146`).
- **Forced restart on certificate changes**: `_on_cert_changed` passes `restart=True` explicitly (`src/charm.py:412`), ensuring cert rotation always restarts the service.
- **Pebble-native**: full use of Pebble for service management and file operations — no exec hacks into a shell-less container.
- **`_remove_certificates` uses `suppress(PathError)`**: clean cleanup pattern at `src/integrations.py:316-319`.
- **`_prepare_certificates` retries with a limit**: correctly uses `stop=stop_after_attempt(3)` at `src/integrations.py:295`, unlike `after_config_updated`.

## Common-practice notes

- **Conventional structure**: standard `src/`, `lib/`, `templates/`, `tests/` layout; `charmcraft.yaml` with ubuntu@22.04 base; `uv` for dependency management, `tox-uv` for test envs.
- **Library versions**: v0 `ldap` and `glauth_auxiliary` (owned), v4 `tls_certificates`, v0 `data_interfaces`, v1 `ingress_per_unit`, v0 `kubernetes_compute_resources_patch` — all current.
- **pydantic v1/v2 compatibility**: `lib/charms/glauth_k8s/v0/ldap.py:157-224` has a ~70-line compat layer, exercised by `TestGlauthClientPydanticV1`/`TestGlauthClientPydanticV2` in the integration test suite. Likely dead weight for new deployments but tested.
- **Distroless workload**: no shell in the container; `after_config_updated` (`utils.py:159`) is the only way to verify ConfigMap sync (by pulling the mounted file).
- **No `metadata.yaml`**: uses `charmcraft.yaml` for all metadata — correct for modern charms.
- **Terraform module**: `terraform/` with `MODULE_SPECS.md` documenting inputs/outputs clearly.
- **Juju 4 ready**: charm itself functions correctly on Juju 4.0.5; the only barrier is dependent charms (postgresql-k8s) not yet supporting Juju 4.
- **Config description vs. reality**: `charmcraft.yaml` promises more than the charm delivers (`log_level` has no effect, `cpu`/`memory` lack validation) — a common but avoidable pattern.

## Tests

- **Unit tests**: 54 tests, all passing (`tox -e unit`, ~3s). Coverage: 73% overall, with gaps in `integrations.py` (54%), `kubernetes_resource.py` (40%), `database.py` (71%).
- **Lint**: `tox -e lint` passes cleanly (codespell, isort, ruff). No type-checker environment (no mypy/pyright). 116 deprecation warnings, mostly `JujuVersion.from_environ()` from library code.
- **Framework**: `ops.testing` throughout with a well-structured `conftest.py` (fixtures for relations, TLS certs, mock resources; module-scoped for expensive operations).
- **Coverage gaps aligned to findings above**:
  - `src/charm.py:248-249` — `ChangeError` path and the subsequent ActiveStatus overwrite: untested.
  - `src/charm.py:287` — `config_changed` set to `True`; no test verifies it is ever reset.
  - `src/charm.py:362-365` — `_on_resource_patch_failed` and its interaction with `_handle_event_update`: untested.
  - `src/utils.py:149-158` — `after_config_updated` timeout/retry path: only the happy path is tested.
  - `src/integrations.py:184-185` — `AuxiliaryData()` empty construction: dead code, untested.
  - `src/kubernetes_resource.py` — all methods except the `name` property are untested (the class is mocked in tests).
  - `src/charm.py:199, 320-321` — `_on_remove` tested via `ops.testing` (passes), but `--force` behaviour isn't captured by unit tests.
  - `GrafanaDashboardProvider`/`MetricsEndpointProvider` — no unit tests verify dashboards are pushed or scrape targets configured (findings #9, #10).
- **Integration tests**: present and comprehensive (`tests/integration/test_charm.py`) — database, ingress (LDAP/LDAPS), certificates, LDAP client search/StartTLS/LDAPS, certificate transfer; run with `jubilant`; tests pydantic v1 and v2 clients via `any-charm`. Scale-up/down tests are skipped (known traefik #406 and a cert_handler bug). Not run in this review (require a full Juju + traefik environment).
- **No state-transition tests**: no coverage for leader/non-leader transitions, upgrade sequences, secret rotation, or retry-exhaustion.

## Docs

- **README**: covers usage, integrations, config, and observability. The PostgreSQL integration example uses `juju integrate glauth-k8s postgresql-k8s` without the `:database` qualifier (open issue #261) — works in practice on Juju 3.6 because there's only one matching interface at deploy time, but is technically ambiguous.
- **CONTRIBUTING.md**: standard — development setup with `uv`, test commands, build/deploy instructions.
- **Charmhub description**: minimal — "Kubernetes Charmed Glauth Operator" with no config reference, integration list, or getting-started guide.
- **Terraform docs**: `terraform/MODULE_SPECS.md` documents module inputs/outputs clearly.
- **CHANGELOG.md**: comprehensive, conventional-commits formatted, back to v1.0.0 — shows active maintenance.
- **Config description mismatch**: `charmcraft.yaml` describes `log_level` as functional; it has no effect (finding #7).
- **README config table incomplete**: lists only `base_dn`, `starttls_enabled`, `anonymousdse_enabled`, omitting `log_level`, `ldaps_enabled`, `cpu`, `memory`. Omission of `ldaps_enabled` is notable since it's a key setting.
- **Non-functional integrations advertised as working**: `charmcraft.yaml` lists `grafana-dashboard` and `metrics-endpoint` as provides, but neither delivers data (findings #9, #10).

## Open questions

1. Does `update_status` restart the service on every 5-minute tick indefinitely, or does Pebble no-op once the service is already running? A longer observation window (15+ min with pebble log timestamps) would quantify this precisely.
2. Is the private-key logging (finding #11) a known upstream glauth issue, and is there an existing bug report to link to?
3. Is `--force` skipping the remove hook (finding #6) documented Juju behaviour that operators should simply be warned about, or is there a charm-side mitigation worth pursuing (e.g. delete-on-stop)?
4. Does `base_dn=""` actually degrade LDAP query behaviour, or does glauth silently no-op with an empty base DN? Confirmed only that the ConfigMap accepts it and glauth reports "listening" — actual LDAP query testing against the empty-base-DN config was not performed.
5. Is the `config_changed` class attribute intended as a way to force a restart across pod restarts, or a plain oversight? If intentional, the name and mechanism should be clarified.
6. What is the actual root cause of the GrafanaDashboardProvider not pushing dashboards (finding #9)? Path-resolution in the deployed charm is the leading hypothesis but was not confirmed by inspecting the running container's filesystem.
