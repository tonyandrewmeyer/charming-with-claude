# grafana-k8s-operator

A mature, well-structured Kubernetes charm for Grafana from Canonical's Observability team. It uses a modern `cosl`-based reconciler pattern, has an extensive integration surface (15+ relations), and supports OAuth, TLS, HA via PostgreSQL, and ships with built-in self-monitoring. Code quality is high in config generation and workload management, but the shared libraries for dashboards and datasources carry real technical debt: an unguarded `json.loads` that can crash the charm on a malformed dashboard, datasource duplication on leader re-election, and flapping template comparisons. The charm also reports `active` while Grafana is actually down, several config options accept garbage with no validation, and the scenario test suite is broken against HEAD. The 2/stable → 12.4/stable jump quietly drops the litestream sidecar in favour of PostgreSQL-only HA — undocumented.

A maintainer should first fix the unguarded `json.loads` in `grafana_dashboard.py` (finding 1, crash-on-bad-input), then close the "active but actually down" status gap (finding 2), then fix the scenario test patch target so that suite runs again (finding 6).

| | |
|---|---|
| Repo | canonical/grafana-k8s-operator @ `1378c31` (2026-07-14) |
| Charms | grafana-k8s, grafana-tester (test only) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5) and concierge-k8s-3 (Juju 3.6.25), both on 2/stable rev 180 (HEAD is the 12.4 track, rev 193; the cluster runs ubuntu@24.04 and lacks ubuntu@26.04, so 12.4/stable could not be deployed) |
| Reviewed | 2026-07-26 |

## What it does

Deploys Grafana on Kubernetes with automatic datasource and dashboard registration via Juju relations. Supports HA via PostgreSQL (HEAD) or litestream SQLite replication (2/stable), OAuth2/OIDC auth, TLS termination, ingress via Traefik, service mesh integration, profiling, tracing, and log forwarding. Ships built-in alert rules and a self-monitoring dashboard. Part of the COS Lite bundle.

## Deployment log

### Juju 4.0.5 (concierge-k8s-4, models rv-grafana-deep, rv-grafana-deep2, rv-grafana-int)

```bash
$ juju deploy grafana-k8s --channel 2/stable
→ Deployed rev 180
```

- **t+40s**: `blocked` — `Kubernetes resources patch failed: juju trust this application`
- `juju trust grafana-k8s --scope cluster`
- **t+30s after trust**: `active/idle`
- Full deploy: ~3 minutes (block → trust → active)

**First round — multi-integration (model rv-grafana-deep):**
```bash
$ juju deploy traefik-k8s --channel latest/beta
$ juju deploy self-signed-certificates --channel edge
$ juju deploy prometheus-k8s --channel 2/stable
$ juju trust prometheus-k8s --scope cluster && juju trust traefik-k8s --scope cluster
$ juju relate grafana-k8s:certificates self-signed-certificates
$ juju relate grafana-k8s:ingress traefik-k8s
$ juju relate grafana-k8s:grafana-source prometheus-k8s:grafana-source
→ All active within ~2 minutes
```

**Second round — failure injection (model rv-grafana-deep2):**
- `juju config log_level=$(python3 -c 'print("A"*10000)')` — accepted; 10KB `'A'` string written verbatim to `GF_LOG_LEVEL` in the Pebble plan. Charm stays `active`.
- `juju config datasource_query_timeout=-1` — accepted (Juju validates `int` type, not range).
- `juju config datasource_query_timeout=notanumber` — rejected by Juju (type mismatch).
- `juju config allow_anonymous_access=maybe` — rejected by Juju (boolean mismatch).
- `juju config cpu="3.14horses" memory="yesplease"` — `BlockedStatus`: "Failed obtaining resource limit spec".
- `juju config --reset cpu && juju config --reset memory` — still `BlockedStatus` (empty strings sent to the resource parser).

**Third round — relation lifecycle (model rv-grafana-int):**
- `juju remove-relation grafana-k8s:ingress traefik-k8s` → clean: reverted to internal URL, `serve_from_sub_path` off.
- `juju remove-relation grafana-k8s:grafana-source prometheus-k8s` → clean: datasource moved to `deleteDatasources` in the provisioning YAML.
- `juju remove-relation grafana-k8s:certificates self-signed-certificates` → clean: reverted to HTTP, cert files removed.

### Juju 3.6.25 (concierge-k8s-3, models rv-grafana-36-deep, rv-grafana-36-new)

Identical behaviour to 4.x. Notable: 3.6 shows `litestream-pebble-ready` hooks in debug-log (rev 180 runs a litestream sidecar container doing `litestream replicate` for SQLite replication). The pod has three containers: `charm`, `grafana`, `litestream`. HEAD's `charmcraft.yaml` has removed the litestream container entirely.

## Observed behaviour

1. **`grafana-server` is deprecated** — the Pebble service command in `grafana.py:215` uses `grafana-server -config`, which produces a deprecation warning in Grafana 12.x logs. Same for the version check at `grafana.py:95` (`grafana-server -v`).
2. **Admin password is plaintext in the Pebble plan** — `GF_SECURITY_ADMIN_PASSWORD` is set as an env var at `grafana.py:204`, visible via `pebble plan` or `kubectl describe pod`. The Juju secret abstraction gives a false sense of security.
3. **Grafana runs as root** — log warning: "Grafana server is running with elevated privileges."
4. **Plugin registration error** on every restart: "Could not register plugin pluginId=table error=plugin table is already registered". Harmless but noisy.
5. **Config validation gaps observed at runtime**:
   - `log_level=invalid` passed through to `GF_LOG_LEVEL=invalid`; Grafana silently ignored it.
   - `log_level` accepts unbounded strings — a 10,000-character string was written verbatim to the Pebble plan. Charm remained `active`.
   - `admin_user=""` accepted, setting `GF_SECURITY_ADMIN_USER=""`, which locks operators out of Grafana.
   - `web_external_url="javascript:alert(1)"` accepted with no URL validation (though this option is marked DEPRECATED and isn't wired into `GF_SERVER_ROOT_URL` in rev 180).
   - `datasource_query_timeout=-1` accepted (Juju validates `int` type; negative values pass through). `datasource_query_timeout=notanumber` correctly rejected by Juju.
   - `cpu="3.14horses"` and `memory="yesplease"` caused `BlockedStatus`: "Failed obtaining resource limit spec: Invalid limits spec" — the resource parser catches garbage.
   - `cpu=""` / `memory=""` (attempting to clear/reset, including via `juju config --reset`) also cause `BlockedStatus` — `adjust_resource_requirements` in `kubernetes_compute_resources_patch.py:158` treats empty string as invalid. Once cpu/memory are set to a non-default value, they cannot be reset via config.
6. **Resource usage** — 66m CPU, 153Mi memory at idle. Charm size: 19MB (rev 180), 25MB (rev 193).
7. **Charm reports `active` while Grafana is actually down** — after `pebble stop grafana`, the charm continues to show `active/idle`. The `get-admin-password` action correctly detects this and fails ("Grafana is not reachable yet."), but `juju status` does not reflect it. Self-heals only on the next reconciliation hook (config-change, relation-change, or `update-status` every 5 min). Contrast: killing the Grafana process directly (`kill -9`) causes Pebble to auto-restart it within seconds and the charm never sees the outage.
8. **Clean TLS teardown** — removing the certificates relation properly removed cert files and reverted `GF_SERVER_PROTOCOL` to `http`.
9. **Clean ingress teardown** — removing the ingress relation reverted to the internal URL (`http://<pod>.<svc>.<ns>.svc.cluster.local:3000`), `GF_SERVER_SERVE_FROM_SUB_PATH` back to `False`.
10. **Clean datasource removal** — removing the grafana-source relation moved the datasource from `datasources` to `deleteDatasources` in the provisioning YAML. Correct behaviour.
11. **Rev 180 has a litestream sidecar; HEAD removed it** — rev 180's `metadata.yaml` defines two containers (`grafana`, `litestream`) with SQLite replication via `litestream replicate -config /etc/litestream.yml`. HEAD's `charmcraft.yaml` has only `grafana`, relying solely on PostgreSQL for HA. No litestream references exist anywhere in HEAD. A significant undocumented architectural change.
12. **Ingress subpath handling works** — with Traefik, `GF_SERVER_ROOT_URL` is set to `http://<traefik-ip>/<model>-grafana-k8s` and `GF_SERVER_SERVE_FROM_SUB_PATH: True`. Correct.
13. **Hook count for config change** — a single `juju config log_level=debug` triggers one `config-changed` hook. Hash-based change detection in `_reconcile_config` avoids unnecessary restarts when config is unchanged.
14. **Grafana container is minimal** — no `python3`, `curl`, or `wget`; only `bash`, `sh`, `apt`, `base64`, and the `grafana` binary. API health checks were confirmed via `/dev/tcp` in bash.
15. **Version reported as 12.0.2** — `/api/health` returns `{"database":"ok","version":"12.0.2","commit":"5bda17e7"}`.
16. **`set-admin-password` action does not exist** — only `get-admin-password` is defined in both rev 180 and HEAD.

## Findings

### 1. Unguarded `json.loads` in dashboard consumer causes ERROR state on malformed dashboard
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/grafana_k8s/v0/grafana_dashboard.py:1559`
- **Evidence**: `data = json.loads(raw_data)` has no try/except. If a related app sends malformed JSON on the `dashboards` relation, `json.JSONDecodeError` propagates uncaught → error state with `hook failed: "grafana-dashboard-relation-changed"`. Confirmed by open issue #582. Additional unguarded `json.loads` calls at lines 1343, 1977, 1981.
- **Impact**: A single broken dashboard from any related charm can take down the entire Grafana charm instance.
- **Fix**: Wrap `json.loads(raw_data)` in try/except, log the error, record an error in relation data, and return.
- **Linter rule**: "`json.loads` on relation data without try/except" — mechanically checkable.

### 2. Charm reports `active` while Grafana workload is down
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:515-519` (`_on_collect_unit_status`)
- **Evidence**: After `pebble stop grafana`, `juju status` shows `active/idle` while Grafana is not running. The reconcile flow checks `container.can_connect()` but not whether the Pebble service is actually running. `get-admin-password` correctly fails, but status stays green. Grafana stays down until the next `update-status` (default 5 min) or other hook.
- **Impact**: Operators trust "active" and assume Grafana is up; status-based monitoring misses the outage.
- **Fix**: In `_on_collect_unit_status`, check `container.get_services("grafana")` (or equivalent) and emit `WaitingStatus`/`MaintenanceStatus` if Grafana is not running.
- **Linter rule**: not mechanically checkable without understanding the workload.

### 3. Datasource duplication on leader re-election in HA
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/grafana_k8s/v1/grafana_source.py:738-771` (`_on_grafana_source_relation_changed`, `_sources_to_delete`)
- **Evidence**: `sources_to_delete` is computed in `_on_grafana_source_relation_changed` (leader-only). On leader re-election the new leader re-scrapes via `update_sources()`, but `_sources_to_delete` compares stale peer data if the old leader hadn't committed its sources before dying. Confirmed by open issue #568.
- **Impact**: Duplicate datasources accumulate on every leader change, causing dashboard confusion and storage bloat in HA deployments.
- **Fix**: Add a periodic `update-status` reconciliation pass recomputing `sources_to_delete` against the full known source set, or make it unconditionally prune anything outside the current set.
- **Linter rule**: not mechanically checkable.

### 4. No config validation for `log_level` option
- **Severity**: medium
- **Kind**: bug
- **Where**: `charmcraft.yaml` (`log_level` definition), `src/charm.py:282` (`_pebble_env`)
- **Evidence**: `juju config grafana-k8s log_level=invalid` accepted silently; value passed to `GF_LOG_LEVEL=invalid`, which Grafana silently ignores. No enumeration constraint in `charmcraft.yaml`.
- **Impact**: Operators get no feedback that their config change was ineffective.
- **Fix**: Add validation in `charmcraft.yaml` or in `_pebble_env`, restricting to `["debug", "info", "warn", "error", "critical"]`.
- **Linter rule**: "Config option with enumerated values has no constraint" — mechanically checkable against `charmcraft.yaml`.

### 5. No config validation for `admin_user` (empty string accepted)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:285` (`_pebble_env`)
- **Evidence**: `juju config grafana-k8s admin_user=""` accepted; `GF_SECURITY_ADMIN_USER=""` set, rendering login unusable.
- **Impact**: Misconfiguration locks operators out of Grafana.
- **Fix**: Validate `admin_user` is non-empty, or emit `BlockedStatus` on empty.
- **Linter rule**: not mechanically checkable in general.

### 6. `get-admin-password` returns password-changed message as success, not failure
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:613-619`
- **Evidence**: `event.set_results({"url": ..., "admin-password": msg})` where `msg = "Admin password has been changed by an administrator."` is returned as a success result. Confirmed by open issue #409.
- **Impact**: Automation parsing `admin-password` from action results may mistake the error message for a real password.
- **Fix**: Use `event.fail()` with the message instead of `event.set_results()`.
- **Linter rule**: not mechanically checkable.

### 7. Scenario tests broken — patch targets non-existent attribute
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/scenario/test_admin_password.py:38`
- **Evidence**: All 9 tests fail at setup with `AttributeError: <class 'charm.GrafanaCharm'> does not have the attribute 'grafana_version'`. `grafana_version` is a property on `Grafana` (the workload class), not on `GrafanaCharm`. No tox environment runs the scenario suite (`tox.ini`'s `unit` env only runs `tests/unit`). `tests/unit/conftest.py:34` patches the correct class.
- **Impact**: The only coverage for `get-admin-password` edge cases (password changed, Grafana down, follower unit) is non-functional.
- **Fix**: Patch `Grafana.grafana_version` instead. Add a `[testenv:scenario]` in `tox.ini`.
- **Linter rule**: not mechanically checkable without running tests.

### 8. Terraform module channel validation overly restrictive
- **Severity**: medium
- **Kind**: bug
- **Where**: `terraform/variables.tf:17-19`
- **Evidence**: `validation { condition = startswith(var.channel, "dev/") ... }` rejects valid channels like `2/stable`, `12.4/stable`.
- **Impact**: The terraform module is unusable for deploying from any channel except `dev/`.
- **Fix**: Remove or loosen the validation to accept all published Charmhub tracks.
- **Linter rule**: "Terraform channel validation rejects published tracks" — mechanically checkable.

### 9. Dashboard template databag value is nondeterministic (flapping)
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/grafana_k8s/v0/grafana_dashboard.py:~1375`
- **Evidence**: `stored_data`, generated from freshly-read templates, is compared with `type_convert_stored(currently_stored_data)` from peer data. The serialised value differs causelessly, triggering continuous `relation-changed` events. Confirmed by open issue #579.
- **Impact**: Continuous relation-changed events cause unnecessary hook execution in deployments with dashboard providers.
- **Fix**: Ensure the comparison uses a stable serialisation matching the stored format.
- **Linter rule**: not mechanically checkable.

### 10. Litestream container removed between 2/stable and HEAD — undocumented architectural change
- **Severity**: medium
- **Kind**: ux
- **Where**: `charmcraft.yaml` (HEAD has only `grafana`; rev 180 `metadata.yaml` has both `grafana` and `litestream`)
- **Evidence**: Rev 180 defines a `litestream` container with a `litestream-image` OCI resource running `litestream replicate -config /etc/litestream.yml`. HEAD has no such container — no "litestream" reference anywhere in the codebase.
- **Impact**: Operators running 2/stable with HA via litestream will find their HA architecture silently changed on upgrade.
- **Fix**: Document the removal in the 12.4-track upgrade/release notes.
- **Linter rule**: not mechanically checkable.

### 11. `cpu` and `memory` config cannot be reset to defaults once set
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:681-683` (`_resource_reqs_from_config`), `lib/charms/observability_libs/v0/kubernetes_compute_resources_patch.py:158` (`adjust_resource_requirements`)
- **Evidence**: Setting `cpu=""` or `memory=""` (including via `juju config --reset`) passes empty strings to `adjust_resource_requirements`, which rejects them: `"Failed obtaining resource limit spec: Invalid limits spec: {'cpu': '', 'memory': ''}"`, and the charm enters `BlockedStatus`.
- **Impact**: Operators who set cpu/memory limits cannot revert to unset/default without removing and re-deploying the application.
- **Fix**: Treat empty string / `None` as "no limit" in `_resource_reqs_from_config`, filtering before passing to `adjust_resource_requirements`.
- **Linter rule**: not mechanically checkable.

### 12. `log_level` config accepts unbounded strings, can exceed Pebble plan limits
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:282` (`_pebble_env`), `charmcraft.yaml` (`log_level` definition)
- **Evidence**: A 10,000-character string of `'A'`s was passed into `GF_LOG_LEVEL` in the Pebble plan; charm stayed `active`. No length limit anywhere.
- **Impact**: Pebble plans have practical size limits; an excessive `GF_LOG_LEVEL` could cause plan push failures or waste etcd storage. Grafana itself silently ignores invalid levels, so the operator gets no feedback either way.
- **Fix**: Add a max-length constraint in `charmcraft.yaml` or validate against known levels in `_pebble_env`.
- **Linter rule**: "String config option with no maxLength constraint" — mechanically checkable against `charmcraft.yaml`.

### 13. `grafana_client.py` `is_ready` only catches `MaxRetryError`; other connection errors propagate unhandled
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/grafana_client.py:64` (`build_info`), `src/grafana_client.py:45` (`is_ready`)
- **Evidence**: `build_info` catches `urllib3.exceptions.MaxRetryError` but not `NameResolutionError`, `ConnectTimeoutError`, `NewConnectionError`, or other `urllib3` exceptions. Any of these propagate uncaught through `is_ready` → `_on_get_admin_password` → error state.
- **Impact**: Edge-case network failures that should degrade gracefully instead crash the hook.
- **Fix**: Broaden the except clause to `urllib3.exceptions.HTTPError` or a base `Exception`, returning `{}` on error.
- **Linter rule**: not mechanically checkable.

### 14. `grafana_auth.py` silently swallows validation and configuration failures
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/grafana_k8s/v0/grafana_auth.py:472-473` (`_set_urls_in_relation_data` bare except), `lib/charms/grafana_k8s/v0/grafana_auth.py:589` (`_validate_auth_config_json_schema` bare except), `lib/charms/grafana_k8s/v0/grafana_auth.py:332` (`_set_auth_config_in_relation_data`)
- **Evidence**: `_set_urls_in_relation_data` catches `except: # noqa: E722` around `validate()` and returns without logging. `_validate_auth_config_json_schema` similarly returns `False` silently, and the caller at line 332 checks this and returns silently too.
- **Impact**: A misconfigured auth setup is invisible — the relation appears connected but auth data never flows.
- **Fix**: Log a warning/error in both catch blocks; consider setting status to reflect the failure.
- **Linter rule**: "bare except without logging" — mechanically checkable.

### 15. `tox -e fmt` runs checker not formatter
- **Severity**: low
- **Kind**: lint
- **Where**: `tox.ini:48`
- **Evidence**: `tox -e fmt` runs `ruff check --fix-only`, which only fixes auto-fixable lint violations and does not run `ruff format`. Confirmed by open issue #428.
- **Impact**: Developers running `tox -e fmt` believe they've formatted their code, but the formatter is never invoked.
- **Fix**: Replace with `ruff format` (or run both).
- **Linter rule**: "tox.ini fmt env uses check --fix-only instead of format" — mechanically checkable.

### 16. Admin password exposed in Pebble plan as environment variable
- **Severity**: low
- **Kind**: ux
- **Where**: `src/grafana.py:204`
- **Evidence**: `extra_info["GF_SECURITY_ADMIN_PASSWORD"] = cast(str, pebble_env.admin_password)` puts the admin password into a Pebble env var, visible via `pebble plan`.
- **Impact**: Anyone with pod access can read the admin password; the Juju secret abstraction gives a false sense of security.
- **Fix**: Document prominently, or write the password to a file and use `GF_SECURITY_ADMIN_PASSWORD__FILE` instead.
- **Linter rule**: "`GF_SECURITY_ADMIN_PASSWORD` in Pebble environment" — mechanically checkable.

### 17. `grafana-server` command deprecated in Grafana 12.x
- **Severity**: low
- **Kind**: bug
- **Where**: `src/grafana.py:215` (Pebble command), `src/grafana.py:95` (version check)
- **Evidence**: Grafana logs: "Deprecation warning: The standalone 'grafana-server' program is deprecated."
- **Impact**: When Grafana removes `grafana-server`, the charm will fail to start.
- **Fix**: Change `grafana-server -config` to `grafana server --config`.
- **Linter rule**: "Deprecated binary `grafana-server` in Pebble command" — mechanically checkable.

### 18. `_reconcile` bypass — database hooks call `_grafana_service.reconcile()` directly
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:545` (`_on_database_changed`), `src/charm.py:565` (`_on_database_broken`)
- **Evidence**: Both handlers call `self._grafana_service.reconcile()` instead of `self._reconcile()`, bypassing `_set_ports()`, `set_workload_version()`, the `resource_patch.is_ready()` check, `ingress.provide_ingress_requirements()`, `_check_wrong_relations()`, and `_reconcile_tls_config()`.
- **Impact**: Currently low (database changes don't affect ports/ingress/TLS) but is a latent maintenance hazard — new logic added to `_reconcile()` may silently not run on database events.
- **Fix**: Route through `self._reconcile()`, or document the bypass explicitly.
- **Linter rule**: not mechanically checkable.

### 19. `custom_config` config option not available in deployed 2/stable revision
- **Severity**: low
- **Kind**: docs
- **Where**: `charmcraft.yaml` (HEAD) vs rev 180 metadata
- **Evidence**: `juju config grafana-k8s custom_config=...` returns `ERROR unknown option "custom_config"` on rev 180. `custom_config` (and its Pydantic validator), `admin_roles`, and `editor_roles` exist only in HEAD (12.4 track).
- **Impact**: Operators reading docs written against the current codebase will hit errors on the stable channel.
- **Fix**: Version-document the availability of config options, or backport to 2/stable.
- **Linter rule**: "Config option present in HEAD but not in published track" — mechanically checkable by comparing `charmcraft.yaml` against the Charmhub API.

### 20. `_reconcile_own_dashboard` reads a local file from `src/` inside the workload class
- **Severity**: low
- **Kind**: bug
- **Where**: `src/grafana.py:509`
- **Evidence**: `Path("src/self_dashboard.json").read_bytes()` reads a file from the charm's source tree at runtime, relative to CWD — works because the file is packaged, but is an implicit and brittle dependency.
- **Impact**: Minor maintainability concern.
- **Fix**: Use a `Path(__file__).parent`-relative path, or embed the dashboard as a Python string constant.
- **Linter rule**: not mechanically checkable.

### 21. `set_peer_data` silently drops data when peer relation is not ready
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/grafana_k8s/v1/grafana_source.py:1079-1082` (`set_peer_data`); same pattern at `lib/charms/grafana_k8s/v0/grafana_source.py:845`
- **Evidence**: `if not peers or not peers.data: logger.info(...); return` — when the peer relation doesn't exist or has no data bucket yet (e.g. during install or relation-departed), the write is silently dropped.
- **Impact**: Datasource/dashboard state can be lost during certain lifecycle transitions, particularly on followers that haven't yet received peer data.
- **Fix**: Defer the triggering event, or raise so the caller can handle it.
- **Linter rule**: not mechanically checkable.

### 22. `_render_dashboards_and_signal_changed` has unguarded `data.pop("templates")`
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/grafana_k8s/v0/grafana_dashboard.py:1561`
- **Evidence**: `templates = data.pop("templates")` raises `KeyError` if a provider sends dashboard JSON without a `"templates"` key. The preceding unguarded `json.loads` (finding 1) is on the same code path.
- **Impact**: A malformed dashboard payload from a provider can crash the Grafana charm.
- **Fix**: Use `data.get("templates", {})` and wrap in try/except.
- **Linter rule**: "`.pop()` on untrusted dict without default" — mechanically checkable.

### 23. Bare `except: raise` is a redundant no-op
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/secret_storage.py:51-52`
- **Evidence**: `except: raise` catches everything and immediately re-raises. The preceding `except ops.SecretNotFoundError` and `except ops.ModelError` already handle specific cases; this block adds nothing.
- **Impact**: Code smell, misleading to readers.
- **Fix**: Remove the block.
- **Linter rule**: "bare `except: raise`" — mechanically checkable via a ruff rule.

## Worth copying

1. **Hash-based change detection** (`src/grafana.py:_reconcile_config`, `_reconcile_ds_config`) — computes SHA256 of generated config, compares against on-disk hash, only restarts when something changed.
2. **`GrafanaConfig` class** (`src/grafana_config.py`) — clean separation of config generation from workload management; `get_status()` integrates with `collect-unit-status`.
3. **`SecretStorage` class** (`src/secret_storage.py`) — reusable abstraction for Juju secrets handling leader generation, follower waiting, and label-based lookup.
4. **`SecretGetter` for `secret://` URLs** (`src/secrets_helper.py`) — lets config values reference Juju secrets via URLs.
5. **Dashboard-file lifecycle management** (`src/grafana.py:_reconcile_dashboards`) — tracks which files should be kept and removes any not in the set.
6. **`Relation` helper** (`src/relation.py`) — minimal peer-data accessor wrapping `json.dumps`/`json.loads` with graceful missing-relation handling.
7. **Pydantic-based `custom_config` validation** (`src/custom_ini_config.py`) — validates specific ini sections (SMTP) with Pydantic models.
8. **Reconciler pattern** (`src/charm.py:_reconcile`) — uses `cosl.reconciler.observe_events` with `all_events`, running the same function on every hook.

## Common-practice notes

- **Follows**: modern COS charm layout (`src/`, `lib/charms/`, `tests/integration/`, `tests/unit/`, `tests/scenario/`), the `uv` charmcraft plugin, the `cosl` reconciler.
- **Follows**: Pydantic for config validation, secret-URL pattern for sensitive config — emerging COS convention.
- **Drifts**: `lib/charms/grafana_k8s/v1/grafana_source.py` and `v0/grafana_dashboard.py` still carry `StoredState` baggage (`_stored.set_default`, `upgrade_keys` migration) for backward compatibility; most COS charms have completed the StoredState → peer-data migration.
- **Drifts**: the Terraform module hardcodes `trust = true`, diverging from COS charms that leave trust as a model-level concern.
- **Drifts**: the `grafana-server` deprecation puts this charm behind; other COS charms on 26.04 may have moved to the new binary — likely a base-image timing issue (24.04 ships Grafana 12.0.2 with the deprecation warning).

## Tests

**Unit tests (pytest):** 197 passed, 1 skipped via `tox -e unit` (downloads `sqlite-static` and `cos-tool-amd64` binaries to repo root). Coverage 75% overall:
- `src/grafana_client.py`: 76% — HTTP client error paths uncovered.
- `lib/charms/grafana_k8s/v0/grafana_dashboard.py`: 61% — large swaths of dashboard handling untested.
- `src/grafana.py`: 73% — container error paths and litestream/sqlite paths untested.
- `src/charm.py`: 77% — database handlers and TLS teardown paths untested.

**Scenario tests:** 9 errors in `test_admin_password.py`, all failing at fixture setup (see finding 7). Requires `PYTHONPATH=src:lib` to resolve `from charm import GrafanaCharm`; no tox environment runs this suite.

**Lint:** `ruff check` passes clean on `src/`, `tests/`, `lib/charms/grafana_k8s/`.

**Static:** `pyright` produces 16 errors, attributable to missing import resolution without proper `PYTHONPATH`. The tox `static` env also checks library version bumps.

**Integration tests:** present under `tests/integration/` with the `grafana-tester` charm; not run in this review (requires a full COS deployment).

**Coverage gaps relative to findings:** no test for invalid or oversized `log_level`, empty `admin_user`, malformed dashboard JSON, `custom_config` validation, scale > 1 without a pgsql relation, `get-admin-password` success-on-changed-password, active-while-down status, `web_external_url` XSS-like input, `grafana-server` command format, cpu/memory reset, negative `datasource_query_timeout`, `grafana_client.is_ready` non-`MaxRetryError` exceptions, auth validation silent failure, or `set_peer_data` data loss.

## Docs

- **README.md**: covers basic usage, web interface, integrations, HA. Contains outdated Juju 2 syntax. Does not mention `custom_config`, `admin_roles`, `editor_roles`.
- **terraform/README.md**: auto-generated terraform-docs output, clean, but the channel validation contradicts published Charmhub channels (finding 8).
- **RELEASE.md**: clear release channels and process, but references `latest/stable` naming that has since moved to track-based channels.
- **Charmhub description**: comprehensive, matches the feature set.
- **Doc/reality mismatch**: README says "default password is randomized at first install" — true, but omits that it's visible in `pebble plan`. `custom_config` is documented in HEAD's `charmcraft.yaml` but unavailable in published 2/stable.

## Open questions

1. **Does `_check_wrong_relations()` work correctly in HEAD?** — exists at `charm.py:455-460` and looks correct on review; rev 180 doesn't call it from the reconcile path. Would settle with: deploy HEAD on a 26.04 cluster and scale to 2.
2. **Does the `grafana server` binary exist yet on 26.04 images?** — the ubuntu@24.04 OCI image has the deprecated `grafana-server`; unclear if 26.04 drops it. Would settle with: inspect `ubuntu/grafana:12.4-26.04_edge`.
3. **Does `GF_SECURITY_ADMIN_PASSWORD__FILE` work on Grafana 12.x?** — would settle with: test on the 12.4 OCI image.
4. **Why does the Terraform module restrict to `dev/`?** — possibly internal-only; the `>= 1.0` provider constraint suggests external use too.
5. **What happens on upgrade from 2/stable to 12.4/stable?** — the litestream-removal and PostgreSQL-migration path is untested. Would settle with: deploy 2/stable, attach PostgreSQL, `juju refresh --channel 12.4/stable`, and observe.
6. **Does the dashboard flapping (finding 9) actually manifest at runtime?** — the hash-based comparison should short-circuit; the bug may be in `type_convert_stored` producing a different structure than `json.loads`. Would settle with: a focused integration test with a dashboard provider (`test_dashboard_relation_stability.py` exists for this but is currently skipped).
7. **Were the 2/stable `_check_wrong_relations`/`_reconcile_tls_config` omissions deliberate?** — rev 180's `_reconcile` calls neither on every pass; HEAD calls both. Would settle with: git blame on those lines.
8. **Why does `_reconcile_relations` not include `_log_forwarding`?** — `LogForwarder` is instantiated at `charm.py:171` but never called from `_reconcile`/`_reconcile_relations`; it likely wires its own observers. Would settle with: verify `LogForwarder.__init__`.
