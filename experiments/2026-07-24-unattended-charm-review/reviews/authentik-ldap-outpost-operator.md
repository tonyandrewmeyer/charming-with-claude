# authentik-ldap-outpost-operator

The charm is a well-engineered Kubernetes operator that manages the Authentik LDAP Outpost. It provisions unique per-relation service accounts in Authentik, handles full lifecycle (provision → reconcile → cleanup), and exposes credentials via the `ldap` provider interface. The codebase is clean, the test suite is thorough (81 scenario tests), and the architecture is sound. There are several rough edges worth addressing before production use: 16 pyright / 18 mypy type errors, missing config validation at runtime, `AuthentikConnectionError` and `AuthentikHttpError` crashing hooks instead of setting `WaitingStatus`, a `model.config.get()` return type that is not narrowed to `str` before passing to functions expecting `str`, and a `LayerDict` return type mismatch in `services.py`. The metrics endpoint on port 9300 is advertised to Prometheus but not exposed in the k8s service, so COS monitoring will never scrape the outpost. The loki push API library shipped in `lib/` uses a deprecated `JujuVersion.from_environ()` API (34 deprecation warnings in tests). No critical bugs were found, but the uncaught API exceptions and the metrics scrape gap are the most likely to cause production incidents.

| | |
|---|---|
| Repo | canonical/authentik-ldap-outpost-operator @ 4c99e99 (2026-07-23) |
| Charms | authentik-ldap-outpost |
| Substrate | k8s (k8s-only; `juju deploy` on LXD fails with "charm must be deployed on a Kubernetes cloud") |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.12), authentik-ldap-outpost rev 18 → refreshed to rev 19; also concierge-k8s-3 (Juju 3.6.25) |
| Reviewed | 2026-08-21 |

## What it does

Manages the Authentik LDAP Outpost on Kubernetes. On first run it provisions an LDAP Provider, Application, and Outpost in the upstream Authentik server via REST API, creates a non-interactive LDAP Bind Flow, and stores the API token in a Juju application secret. For each LDAP consumer relation it creates a unique service-account user with a strong random password, grants full-directory search via a provider-scoped RBAC role, and exposes connection details (URLs, Bind DN, password) to the consumer. On relation-broken it deletes the service account. The traefik-route integration exposes LDAPS (port 636) via Traefik with Proxy Protocol v2 and dynamic trusted-proxy CIDR discovery.

## Deployment log
What you actually did, what worked, what did not, with the commands that matter.

### k8s-4 (Juju 4.0.12) — primary model

```
juju add-model rv-authentik-ldap2 k8s --controller concierge-k8s-4
juju deploy authentik-ldap-outpost --channel stable
  → deployed rev 18, image ghcr.io/canonical/authentik-ldap-outpost:2026.5.3
  → blocked "missing authentik-server-info relation" ✓

juju deploy authentik-server --channel edge (rev 30)
juju deploy traefik-k8s --channel edge (rev 405)
juju deploy self-signed-certificates --channel edge
juju deploy loki-k8s --channel stable
juju relate traefik-k8s:receive-ca-cert self-signed-certificates:send-ca-cert
juju relate authentik-ldap-outpost authentik-server
juju relate authentik-ldap-outpost:traefik-route traefik-k8s:traefik-route
juju relate authentik-ldap-outpost logging loki-k8s
  → status: waiting "waiting for authentik-server-info data" ✓
  → traefik-route-relation-joined/changed hooks fired ✓
  → logging-relation-changed hooks fired ✓
  → loki-k8s went active, pebble plan confirmed log-targets ✓

juju config authentik-ldap-outpost log_level=debug
  → accepted with no validation ✓

juju config authentik-ldap-outpost search_mode=invalid_mode bind_mode=invalid_mode log_level=superverbose
  → accepted silently — NOOP conditions prevented processing ✓

juju add-unit authentik-ldap-outpost
  → unit 1 created, status "running" ✓

juju refresh authentik-ldap-outpost --channel stable
  → status "maintenance", pod restarted (PodInitializing → Running)
  → returned to "waiting" after settle ✓

# Pebble plan inspection (workload container via juju exec):
PEBBLE_SOCKET=/charm/containers/authentik-ldap/pebble.socket /charm/bin/pebble plan
  → ldap service: startup=disabled, no AUTHENTIK_* env vars (NOOP state)
  → log-targets: loki-k8s/0 with full Juju topology labels ✓
PEBBLE_SOCKET=... /charm/bin/pebble services
  → ldap: disabled, inactive (correct — starts when server relation is ready)
PEBBLE_SOCKET=... /charm/bin/pebble notices
  → 3 change-update notices, 3 occurrences each (plan + relation events)

juju remove-application authentik-ldap-outpost --force
  → application destroyed, scale 0 ✓
```

### k8s-3 (Juju 3.6.25) — secondary model

```
juju add-model rv-authentik-k8s3 --controller concierge-k8s-3
juju deploy authentik-ldap-outpost --channel stable
  → blocked "missing authentik-server-info relation" ✓

juju deploy authentik-server --channel edge
  → unit running ✓

juju relate authentik-ldap-outpost authentik-server
  → waiting "waiting for authentik-server-info data" (identical to k8s-4) ✓
```

Hook sequence on k8s-3: `install → peers-relation-created → leader-elected → pebble-ready → config-changed → start` — identical to k8s-4. No behavioral differences observed between Juju 3.6 and 4.0 for this charm.

## Observed behaviour

**Hook sequence** (k8s-4, k8s-3): `install → peers-relation-created → leader-elected → pebble-ready → config-changed → start` — correct and complete lifecycle ordering.

**Pebble layer for workload container** (k8s-4, via `juju exec --unit authentik-ldap-outpost/0 -- PEBBLE_SOCKET=/charm/containers/authentik-ldap/pebble.socket /charm/bin/pebble plan`):
```
services:
    ldap:
        startup: disabled
        command: /ldap
        environment:
            GOFIPS: "1"
            TMPDIR: /dev/shm/
log-targets:
    loki-k8s/0:
        type: loki
        location: http://loki-k8s-0.loki-k8s-endpoints....svc.cluster.local:3100/loki/api/v1/push
        services: [all]
        labels: {juju_model, juju_unit, juju_application, charm, job, ...}
```
The `ldap` service is `startup: disabled` — it will be started by the charm once the server relation is established and the Pebble layer is re-planned. The `AUTHENTIK_*` env vars are absent because the NOOP conditions prevent the full layer from being planned until the server relation provides data. The loki log target IS present and correctly configured with full Juju topology labels (`juju_model`, `juju_unit`, etc.), confirming the loki push API integration is live and working. The pebble notices show 3 `change-update` events (initial plan, logging-relation-created, logging-relation-changed), each with 3 occurrences.

**Hook double-firing** (k8s-4, Juju 4.0.12): Both `config-changed` and `logging-relation-changed` fire twice per change. `config-changed` fired twice for each `juju config` invocation (e.g. `log_level=debug`, `log_level=warning`, `log_level=info` each triggered two hooks). `logging-relation-changed` also fired twice per logging relation event. This is normal Juju 4.x behaviour — the hook fires once for the agent config update and once for the unit — and does not cause incorrect state. No extra hook execution beyond the double-fire was observed.

**K8s resource patch failure on every hook** (confirmed in container logs): On every `config-changed` and `update-status` hook:
```
HTTP Request: GET .../statefulsets/authentik-ldap-outpost "HTTP/1.1 403 Forbidden"
Kubernetes resources patch failed: `juju trust` this application.
  statefulsets.apps "authentik-ldap-outpost" is forbidden:
  User "system:serviceaccount:...authentik-ldap-outpost" cannot get...
```
The charm logs the error, then transitions to `maintenance` ("Configuring resources"), then `_on_collect_status` sets `waiting` ("waiting for authentik-server-info data"). No `BlockedStatus` or `ErrorStatus` is set — this is appropriate since K8s resource patching is an optional optimisation.

**Status progression**: agent init → maintenance "Configuring resources" → blocked "missing authentik-server-info relation" → (after relation) waiting "waiting for authentik-server-info data". Status precedence was correct throughout: `BlockedStatus` (no server relation) beats `WaitingStatus` (server relation present but not yet providing data).

**Resource use**: Pod at ~70 mCPU, 39 MiB memory — very lightweight.

**Config without validation** (confirmed by observation):
- `juju config search_mode=invalid_mode bind_mode=invalid_mode log_level=superverbose` — all accepted silently; NOOP conditions prevented processing so the invalid values never reached the API. If the relation had been established with these invalid values, they would have been passed to `_provision_authentik_resources` and the type-error risk would become a runtime `TypeError`.

**Loki integration confirmed working**: `juju relate authentik-ldap-outpost logging loki-k8s` successfully established the relation. The pebble plan shows a `log-targets` entry for `loki-k8s/0` with `type: loki`, full Juju topology labels (`juju_model`, `juju_unit`, `juju_application`, `charm`, `job`), and the correct push URL. No additional configuration was required on the outpost side — the `LogForwarder` library automatically configured log forwarding on relation creation.

**Scaling**: `juju add-unit` works correctly on k8s (new pod created, status "running"). Scale-down requires `--num-units`.

**`juju refresh`**: Triggers `maintenance` status, pod restart (PodInitializing), returns to `waiting` after settle. Clean upgrade path.

**Application teardown**: `juju remove-application --force` destroys both units, pod terminates. Clean.

**`ldap-relation-broken` hook fires correctly**: Relation removal triggers the hook on the outpost unit. The hook calls `_on_holistic_handler`, which correctly passes through NOOP conditions and exits cleanly. Container logs show `'app' expected but not received` and `'app_name' expected in snapshot but not found` warnings from the ldap library — the hook completes successfully despite these warnings.

**`server-info` relation removal transitions cleanly to `BlockedStatus`**: Removing the relation causes the outpost to transition from `WaitingStatus("waiting for authentik-server-info data")` to `BlockedStatus("missing authentik-server-info relation")`. No traceback, no error — status precedence is correct.

**Process kill recovers automatically**: Killing the `container-agent` process (PID 16) inside the workload container causes Pebble (PID 1) to automatically restart it. The `authentik-ldap-pebble-ready` hook re-runs, status returns to `WaitingStatus` — zero manual intervention required.

**`juju exec` access to workload pebble**: The workload container's pebble socket is at `/charm/containers/authentik-ldap/pebble.socket` and accessible via `juju exec --unit authentik-ldap-outpost/0 -- PEBBLE_SOCKET=/charm/containers/authentik-ldap/pebble.socket /charm/bin/pebble <cmd>`. This allows inspection of the workload pebble layer without kubectl.

**K8s-only constraint**: Attempting `juju deploy authentik-ldap-outpost` on the LXD cloud fails with "charm must be deployed on a Kubernetes cloud". The `charmcraft.yaml` declares `type: charm` without `bases`, but the charm's container-wrapped binary requires Kubernetes.

**No custom actions**: `juju actions` reports "No actions defined". The charm has no `actions:` in charmcraft.yaml. Configuration is entirely through `juju config` and relation lifecycle.

## Findings

### `model.config.get()` returns wide type not narrowed before use — runtime TypeError risk
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:498-510`, `src/charm.py:712-713`
- **Evidence**:
  ```python
  # src/charm.py:498-510
  base_dn = self.model.config.get("base_dn")   # → bool|int|float|str|None
  search_mode = self.model.config.get("search_mode", "cached")   # → bool|int|float|str
  bind_mode = self.model.config.get("bind_mode", "cached")       # → bool|int|float|str
  ...
  self._verify_and_update_existing_resources(..., base_dn=base_dn, search_mode=search_mode, ...)
  self._provision_fresh_resources(..., base_dn=base_dn, search_mode=search_mode, ...)
  ```
  pyright reports: `Argument of type "bool | int | float | str" cannot be assigned to parameter "search_mode" of type "str"` (×2 at lines 499, 500, 509, 510). mypy reports 6 errors of the same kind.
- **Why it matters**: Juju's `model.config.get()` returns `bool | int | float | str | None` for all config values. The charmcraft.yaml types `search_mode` and `bind_mode` as `string`, but the charm code never validates or narrows this type. If the charmcraft.yaml schema ever allows a non-string value (e.g., an integer default or an accidentally numeric value in the YAML), a `TypeError` would be raised at the function call site, crashing the hook.
- **Fix**: Cast/narrow after retrieval: `search_mode = str(self.model.config.get("search_mode", "cached"))` or use a typed validator in `CharmConfig`.
- **Linter rule**: "Config value passed to a typed function must be narrowed to the expected type".

### `model.config.get()` for `base_dn` at `src/charm.py:712-713` — None not handled
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:712-713`
- **Evidence**: `base_dn = self.model.config.get("base_dn")` then `bind_dn = f"cn={username},ou=users,{base_dn}"`. pyright: `Argument of type "bool | int | float | str | None" cannot be assigned to parameter "base_dn" of type "str"`. mypy same. The code at line 713 uses `base_dn` in an f-string directly; if the config returns `None` this would produce `"cn=user,ou=users,None"`.
- **Why it matters**: Same mechanism as above. `model.config.get()` returns `None` if the key is absent. The f-string at line 713 would silently embed `"None"` in the bind DN, breaking LDAP authentication.
- **Fix**: Add explicit `str(base_dn)` or assert non-None.
- **Linter rule**: Same as above.

### `model.config.get()` for peer data access at `src/charm.py:290` — None not handled
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:290`
- **Evidence**: `secret_id = self._get_peer_data("outpost_token_secret_id")` (returns `str | None`), then passed to `self._read_outpost_token_secret(secret_id)` which expects `str`. pyright/mypy: `Argument of type "str | None" cannot be assigned to parameter "secret_id" of type "str"`.
- **Why it matters**: If the peer data is absent on a follower unit, the charm would crash with `TypeError: expected str, got None` in `_read_outpost_token_secret`.
- **Fix**: Guard with `if secret_id is None: return None`.

### No runtime validation of `search_mode` and `bind_mode` config values
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:471-472`
- **Evidence**: `self.model.config.get("search_mode", "cached")` and `self.model.config.get("bind_mode", "cached")` are passed directly to the Authentik API without checking they are `"direct"` or `"cached"`. Observed: `juju config search_mode=invalid_mode bind_mode=invalid_mode` accepted silently. Because NOOP conditions prevented reconciliation at the time of testing, the invalid value was not processed — but with the server relation established, the invalid values would be passed to `_provision_authentik_resources` and then to `_provision_fresh_resources` / `_verify_and_update_existing_resources`. The type system cannot catch this because `model.config.get()` returns `bool | int | float | str`.
- **Why it matters**: The upstream API call would either reject it (and the charm would fail with an opaque error) or silently accept the wrong value, putting the outpost in a broken state. Additionally, the `model.config.get()` return type (`bool|int|float|str`) passed to a `str`-typed parameter is a type error that pyright flags.
- **Fix**: Validate in `CharmConfig` or at the top of `_provision_authentik_resources`: raise `CharmError` if the value is not in `{"cached", "direct"}`.
- **Linter rule**: "config option with restricted string values must be validated at runtime".

### Same: `log_level` accepted without runtime validation
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:471`, `src/configs.py:36`
- **Evidence**: `juju config log_level=superverbose` was accepted silently; `log_level` is passed to `AUTHENTIK_LOG_LEVEL` env var without validation.
- **Why it matters**: An invalid log level may be ignored by the binary or cause a startup failure.
- **Fix**: Add a validator in `CharmConfig` or the pebble layer builder.
- **Linter rule**: Same as above.

### `_cleanup_orphaned_relations` errors are swallowed silently
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:738-742`
- **Evidence**:
  ```python
  if self.unit.is_leader():
      try:
          self._cleanup_orphaned_relations()
      except Exception as e:
          logger.error("Failed to clean up orphaned relations: %s", e)
  ```
  No status is set; the orphaned accounts remain in Authentik until the next `leader-elected` or `update-status`.
- **Why it matters**: If the Authentik API is temporarily down during orphan cleanup, service accounts are not deleted, creating a security and credential-rot risk.
- **Fix**: Track failed orphan IDs in peer data for retry, or set `WaitingStatus` when the API call fails.
- **Linter rule**: "exception caught and logged without status update".

### `TraefikRouteRequirer.__init__` called with `Relation | None` — type error
- **Severity**: medium
- **Kind**: lint
- **Where**: `src/integrations.py:155`
- **Evidence**:
  ```python
  self._requirer = TraefikRouteRequirer(
      charm,
      charm.model.get_relation(TRAEFIK_ROUTE_RELATION),  # returns Relation | None
      relation_name=TRAEFIK_ROUTE_RELATION,
  )
  ```
  `TraefikRouteRequirer.__init__` signature: `relation: Relation` (not `Relation | None`). pyright: `Argument of type "Relation | None" cannot be assigned to parameter "relation" of type "Relation"`.
- **Why it matters**: At runtime, when there is no traefik-route relation, `get_relation` returns `None`. The `TraefikRouteRequirer` constructor stores it as `self._relation = relation` and later accesses it without null-checking in `submit_route()` (which has its own null guard, but the constructor should not accept `None`). This is a type-level violation; the runtime behaviour is safe because `submit_route()` returns early if the relation is absent, but the type contract is violated.
- **Fix**: Guard with `if rel := charm.model.get_relation(...):` before constructing.
- **Linter rule**: pyright catches this: `reportArgumentType`.

### `service.current.value` dead code path — pyright flags unreachable attribute access
- **Severity**: low
- **Kind**: lint
- **Where**: `src/services.py:130`
- **Evidence**:
  ```python
  current_str = (
      service.current.value if hasattr(service.current, "value") else service.current
  )
  ```
  pyright: `Cannot access attribute "value" for class "str"`. The ops `ServiceStatus` type is `ServiceStatus | str`. At the point of this expression, pyright has narrowed to `str`, so the `.value` branch is unreachable. In practice, ops returns a `ServiceStatus` enum member (which has `.value`) when the service is active, and a `str` when inactive — the `hasattr` guard handles this correctly at runtime.
- **Why it matters**: No runtime impact — the code is correct. But the pyright error means the type annotations should be clarified.
- **Fix**: Use `isinstance(service.current, enum.Enum)` instead of `hasattr(service.current, "value")`.
- **Linter rule**: pyright `reportAttributeAccessIssue`.

### `configs.py` env var return type mismatch
- **Severity**: low
- **Kind**: lint
- **Where**: `src/configs.py:42`, `src/configs.py:57`
- **Evidence**: `CharmConfig.to_env_vars()` returns a dict whose values come from `self._config.get()`, which yields `bool | int | float | str | None`. The declared return type is `EnvVars` (`Mapping[str, Union[str, bool]]`), which excludes `int`, `float`, and `None`. pyright: `Type "bool | int | float | str" is not assignable to return type "str | bool"`.
- **Why it matters**: The Pebble layer accepts string env values; numeric values would be coerced by Pebble, but the mismatch is a type error that could mask real issues.
- **Fix**: Cast each value to `str` before returning.
- **Linter rule**: pyright `reportReturnType`.

### `build_layer` `LayerDict` return type mismatch — pyright error in `services.py:46`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/services.py:30-58`
- **Evidence**:
  ```python
  def build_layer(env: EnvVars) -> LayerDict:
      return {
          "services": {
              SERVICE_NAME: {
                  ...
                  "environment": env,  # env is Mapping[str, Union[str, bool]]
              }
          },
          ...
      }
  ```
  pyright: `Type "dict[str, dict[str, dict[str, str | EnvVars]]]" is not assignable to return type "LayerDict"`. `LayerDict` expects `dict[str, str]` for environment values, but `EnvVars` is `Mapping[str, Union[str, bool]]`. In practice the pebble layer accepts both at runtime; this is purely a type-signature mismatch.
- **Why it matters**: Clean type checking is important for maintainability. The mismatch could mask real type errors in adjacent code.
- **Fix**: Cast `env` to `dict[str, str]` before passing, or declare `env` as `Mapping[str, str]`.
- **Linter rule**: pyright `reportReturnType`.

### Dead constants never referenced
- **Severity**: low
- **Kind**: lint
- **Where**: `src/constants.py:24-25`
- **Evidence**: `BASE_DN = "DC=ldap,DC=goauthentik,DC=io"` and `BIND_DN = "cn=akadmin,ou=users,DC=ldap,DC=goauthentik,DC=io"` are defined but never imported or used.
- **Why it matters**: Dead code; appears to be legacy from an earlier design.
- **Fix**: Remove.
- **Linter rule**: Not mechanically checkable without cross-module analysis.

### traefik-route template rendered with insecure Proxy Protocol v2
- **Severity**: low
- **Kind**: ux
- **Where**: `templates/traefik-route.json.j2`, `src/integrations.py:155`
- **Evidence**: Static config hardcodes `"proxyProtocol": {"insecure": true}`. No Juju config controls it.
- **Why it matters**: Operators who want to disable proxy protocol cannot do so without patching the template.
- **Fix**: Add a `proxy_protocol` Juju config option (boolean, default `true`).
- **Linter rule**: Not mechanically checkable.

### `AUTHENTIK_INSECURE` is hardcoded to `"true"` throughout
- **Severity**: low
- **Kind**: docs
- **Where**: `src/constants.py:27`, `src/env_vars.py:16`, `src/charm.py:67`
- **Evidence**: `AUTHENTIK_INSECURE = "true"` in constants; also in `DEFAULT_CONTAINER_ENV` and in `OutpostEnv.to_env_vars()`. Tracked as GitHub issue #8.
- **Why it matters**: Operators expecting TLS between outpost and server cannot configure `AUTHENTIK_INSECURE=false`.
- **Fix**: Document the limitation in the README until issue #8 is resolved.
- **Linter rule**: Not applicable (intentional design).

### `_ensure_traefik_route` always returns `True` — not a bug
- **Severity**: informational
- **Kind**: pattern-note
- **Where**: `src/charm.py:594-601`
- **Evidence**: `_ensure_traefik_route` returns `True` regardless of whether traefik is ready. This is intentional — the traefik-route is stored in the relation and Traefik applies it when ready.
- **Why it matters**: None — this is correct behaviour.
- **Fix**: None needed.

### `AuthentikConnectionError` and `AuthentikHttpError` crash the hook instead of setting status
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:607-610`, `src/api_client.py:166-188`
- **Evidence**: The retry loop in `_request_with_retry` (`api_client.py:173-188`) exhausts 3 retries then re-raises. The holistic handler only catches `CharmError` (`src/charm.py:608-610`), not `AuthentikApiError` (the base class of `AuthentikConnectionError` and `AuthentikHttpError`). Any non-retryable API failure, or a retryable failure after 3 attempts, propagates as an uncaught exception and crashes the hook.
- **Why it matters**: If the Authentik API is down or returns a 401/403/500, the hook terminates with a traceback. The unit remains in its previous status (not `BlockedStatus` or `WaitingStatus`) and the operator has no actionable message. The charm recovers only when a subsequent hook fires, but transient failures between hooks are invisible.
- **Fix**: Catch `AuthentikApiError` in `_holistic_handler` and set `WaitingStatus`. Alternatively, convert API errors to `CharmError` subclasses so the existing catch-all handles them uniformly.
- **Linter rule**: Not mechanically checkable without knowing the exception hierarchy.

### Metrics scrape port 9300 not exposed in k8s service
- **Severity**: high
- **Kind**: bug
- **Where**: `src/services.py:95-99`, `src/charm.py:86-89`
- **Evidence**: `MetricsEndpointProvider` is instantiated with `jobs=[{"static_configs": [{"targets": ["*:9300"]}]}]` (`src/charm.py:87`). The Pebble layer defines the ldap service on port 3389 but no HTTP server on 9300. The k8s service only exposes port 3389/tcp. `WorkloadService.open_port()` (`src/services.py:98-99`) only opens LDAP_PORT (3389) and LDAPS_PORT (636), never METRICS_PORT (9300).
- **Why it matters**: The `prometheus_scrape` interface advertises `*:9300` as the scrape target, so `grafana-agent-k8s` configures Prometheus to scrape it. But port 9300 is not exposed on the Pod or Service, so the scrape will fail with connection refused. The metrics relation will never produce useful monitoring data. Observed: `metrics-endpoint-relation-created/joined/changed` hooks all fired, relation established, but no metrics will be scraped.
- **Fix**: Either (a) add `self._unit.open_port(protocol="tcp", port=METRICS_PORT)` to `WorkloadService.open_port()`, or (b) serve Prometheus metrics from the same HTTP endpoint as the ldap binary already exposes, or (c) remove the `metrics-endpoint` provider interface if the binary does not expose metrics.
- **Linter rule**: "Provider interface port must be opened via `unit.open_port()`".

### `ldap-relation-broken` hook emits library warnings about missing 'app' and 'app_name'
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/glauth_k8s/v0/ldap.py` (the charm ships this library)
- **Evidence**: Observed in container logs on `ldap-relation-broken`:
  ```
  juju-log ldap:3: 'app' expected but not received
  juju-log ldap:3: 'app_name' expected in snapshot but not found
  ```
  The library is checking for app identity in the relation snapshot when the relation is being torn down.
- **Why it matters**: These are `WARNING`-level logs, not errors. The hook completes successfully and the relation is cleaned up. However, the library appears to be checking state that is no longer available during teardown — this suggests the library's cleanup logic may not be handling the relation-broken case correctly, or is looking for data that was never set.
- **Fix**: Examine the library's relation-broken handling and ensure it doesn't emit warnings during cleanup. The charm itself cannot fix this without patching the library.
- **Linter rule**: Not mechanically checkable from the charm code.

### grafana-dashboard relation fails: wrong interface on grafana-agent-k8s
- **Severity**: low
- **Kind**: ux
- **Where**: Deployment: `grafana-agent-k8s:grafana-dashboard` ↔ `authentik-ldap-outpost:grafana-dashboard`
- **Evidence**: `juju relate grafana-agent-k8s:grafana-dashboard authentik-ldap-outpost:grafana-dashboard` fails with:
  ```
  ERROR: no candidates for grafana-agent-k8s:grafana-dashboard: relation endpoint not found
  ```
  `grafana-agent-k8s` rev 243 does not provide a `grafana-dashboard` interface — it uses a different COS integration model.
- **Why it matters**: Operators following the charm's declared `provides` interfaces would attempt this relation and fail. The README does not mention this limitation. The grafana dashboard is packaged in the charm but can only be used by charms that provide the `grafana-dashboard` interface.
- **Fix**: Document the limitation in the README.
- **Linter rule**: Not mechanically checkable.

### `loki_push_api` library ships deprecated `JujuVersion.from_environ()` — 34 deprecation warnings
- **Severity**: medium
- **Kind**: lint
- **Where**: `lib/charms/loki_k8s/v1/loki_push_api.py:2272`
- **Evidence**:
  ```python
  juju_version = JujuVersion.from_environ()  # DEPRECATED in ops 3.8.x
  if not juju_version > JujuVersion(version=str("3.3")):
      ...
  ```
  `JujuVersion.from_environ()` is deprecated in ops 3.8.x (the version installed in the charm's venv). The correct replacement is `model.juju_version`. The `_PebbleLogClient` class is a static utility, not a charm object, so it cannot use `self.model.juju_version`. The charm ships this library as part of its `lib/` tree. pytest reports 34 `DeprecationWarning`s from this exact call site. The feature still works in Juju 3.x and 4.x, but the warning is noisy and will break on a future ops release.
- **Why it matters**: Every test run produces 34 identical deprecation warnings, masking other issues. A future ops version may remove `JujuVersion.from_environ()` entirely, breaking the log-forwarding feature.
- **Fix**: The library needs to accept `juju_version` as a constructor parameter, defaulting to `JujuVersion.from_environ()` for backward compatibility but allowing the charm to pass `self.model.juju_version`. Alternatively, the charm could use a newer version of the library that has fixed this.
- **Linter rule**: Not mechanically checkable — requires running tests with deprecation warnings visible.

### Test environment note: ops 3.7.1 + ops-scenario 8.7.1 is the correct combination
- **Severity**: informational
- **Kind**: docs
- **Where**: `pyproject.toml`, `tests/unit/`
- **Evidence**: Running `uv run pytest tests/unit` against the as-installed venv (ops 3.8.1, ops-scenario 8.8.1) passes all 81 tests with 34 deprecation warnings (from the loki library). The `pyproject.toml` specifies `ops~=3.0` and `ops[testing]` (which does not include ops-scenario), so ops-scenario must be installed separately via `uv pip install -e ".[unit]"`. Mixing ops 3.8.x with ops-scenario 8.6.0 causes `AttributeError: 'CapturingFramework' object has no attribute '_closed'`.
- **Why it matters**: Developers running tests for the first time will encounter a version mismatch. The `tox -e unit` path works correctly.
- **Fix**: Add `ops-scenario` explicitly to the `[project.optional-dependencies].unit` list in `pyproject.toml`.

## Worth copying

**Holistic handler pattern** (`src/charm.py:589-620`): A single `_holistic_handler` function orchestrates all reconciliation (traefik route, Authentik resources, LDAP provider), with a preceding NOOP check. This is the cleanest reconciliation pattern in the codebase — easy to follow, testable, and avoids the common pattern of having each event handler independently trigger work.

**CollectStatusEvent for status precedence** (`src/charm.py:628-652`): Using ops's `CollectStatusEvent` correctly composes multiple status checks (Blocked/Waiting/Active) with the correct Juju precedence. The pattern of calling `event.add_status()` for each condition rather than `event.status =` ensures the most significant status wins.

**Deployment-unique resource naming** (`src/charm.py:160-171`): The `_deployment_identity` property combines a slug of the app name with a 12-character SHA256 of the model UUID. This prevents name collisions when the same charm is deployed multiple times to the same Authentik server, and is stable across charm refreshes.

**Peer-data tracking for config drift detection** (`src/charm.py:314-336`): Storing `last_base_dn`, `last_search_mode`, etc. in peer relation data lets the charm detect config changes and update existing resources (instead of always re-provisioning). The check `config_unchanged = (last_base_dn == base_dn and ...)` is simple and correct.

**Strict permission verification** (`src/api_client.py:599-633`): `verify_provider_search_permission` strictly rejects a global grant and requires an object-scoped grant. This prevents a subtle security misconfiguration where the search permission would accidentally be granted to all LDAP providers.

**Orphan cleanup on multiple triggers** (`src/charm.py:563-582`): `_cleanup_orphaned_relations` is called from `_ensure_ldap_provider` (leader only, line 740), and the peer data tracks all known relation IDs. On `relation-broken`, the peer tracking is cleared only after the Authentik API call completes (or is retried on next hook). The test `test_failed_orphan_deletion_preserves_tracking_for_retry` covers this precisely.

**Pebble layer environment merging** (`src/services.py:155-165`): `PebbleService.render_pebble_layer` starts with `DEFAULT_CONTAINER_ENV` and updates with each `EnvVarConvertible` source, producing a clean layered env var accumulation. The pebble plan correctly shows log-targets for loki integration without needing any custom charm code.

**Scenario/state-transition tests** (`tests/unit/test_charm.py`): Using `ops-scenario` with a `create_state()` fixture is the right approach. 81 tests covering all major state transitions.

**Terraform module with Juju offer** (`terraform/main.tf`, `terraform/outputs.tf`): The module exposes a `juju_offer` resource for the LDAP endpoint, enabling cross-model relations via Terraform.

## Common-practice notes

| Area | Status | Notes |
|---|---|---|
| `charmcraft.yaml` layout | Standard | `type: charm`, `charm-user: non-root`, `parts: charm` with `charm-binary-python-packages` |
| `lib/charms/` layout | Standard | Libraries versioned under `v0`/`v1`; `LIBAPI=0, LIBPATCH=13` for ldap library |
| `src/` layout | Standard | Clean separation: `charm.py`, `api_client.py`, `integrations.py`, `services.py`, `configs.py`, `constants.py`, `exceptions.py`, `utils.py` |
| `tox.ini` | Standard | fmt/lint/unit/integration envs; `PYTHONPATH` set correctly |
| Holistic handler | Leads | `_holistic_handler` as single reconciliation entry point — better than N independent handlers |
| Status management | Standard | Uses `CollectStatusEvent` — correct modern ops pattern |
| Config handling | Drifts | No runtime validation; also untyped `model.config.get()` values passed directly to str-typed functions |
| Secret management | Standard | Uses `model.app.add_secret()` / `model.get_secret()` — modern Juju secrets API |
| NOOP conditions | Standard | `utils.py` defines conditions checked before reconciliation — clean pattern |
| Type checking | Lags | 16 pyright errors, 18 mypy errors — should be 0 |
| CI workflow | Standard | `.github/workflows/ci.yaml` with lint/unit/integration |
| OpenSpec specs | Notable | `openspec/specs/traefik-route-integration` and `openspec/specs/ldap-rbac` — well-documented design decisions |
| No actions | Standard | No custom actions — configuration is entirely through `juju config` and relations |
| K8s-only | Standard | Charm declares k8s-only; LXD deploy fails with appropriate error message |
| Charm libraries in `lib/` | Standard | 8 libraries shipped in `lib/` including `loki_push_api`, `prometheus_scrape`, `traefik_route`, `grafana_dashboard`, `ldap`, `authentik_server_info`, `tracing`, `kubernetes_compute_resources_patch` |
| Loki push API integration | Leads | Correctly uses `LogForwarder` from `loki_k8s`; pebble plan confirmed with live log-targets |
| Tracing integration | Standard | Uses `TracingEndpointRequirer` from `tempo_coordinator_k8s`; OTLP endpoint injected as `AUTHENTIK_OUTPOST__DISCOVER__OTLP_TRACES_ENDPOINT` in pebble layer env |
| Upgrade path | Standard | No explicit `upgrade-charm` handler; charm libraries handle their own upgrade (`grafana_dashboard._update_all_dashboards_from_dir`, `loki_push_api._on_lifecycle_event`) |

## Tests

**Unit tests**: 81 tests, all passing. The correct test environment is Python 3.12 with `uv pip install -e ".[unit]"`, which resolves to ops 3.8.1 + ops-scenario 8.8.1. In CI this is handled by `tox -e unit`. Mixing ops 3.8.x with ops-scenario 8.6.0 causes `AttributeError: 'CapturingFramework' object has no attribute '_closed'` — ops-scenario 8.7.1+ is required.

**Test environment**: ruff 0.8.x, Python 3.12, ops 3.8.1, ops-scenario 8.8.1.

**Coverage areas**:
- Status collection (5 tests): correct status precedence
- Holistic handler (3 tests): NOOP conditions, pebble planning
- Pebble ready (2 tests): open_port, set_version
- LDAP relation (2 tests): service account provision, relation broken cleanup
- Authentik provisioning (9 tests): first run, config unchanged skip, mode change update, outpost-not-found reprovision, transient failure, follower token read, missing bind secret rotation, orphan deletion failure/success, leader election cleanup
- Traefik route (3 tests): LDAPS enabled/disabled, plain LDAP ingress config
- RBAC search authorization (1 test): provider-scoped role assignment
- Requirer identity (5 tests): user rename, group adoption, conflict blocking
- API client (18 tests): HTTP methods, pagination, retry, flow resolution, provider CRUD, outpost CRUD, user management, RBAC
- Integrations (9 tests): env vars, tracing data, traefik route submission
- Services (5 tests): pebble layer, plan/start, workload service

**Linting results**:
- `ruff check .` — all checks passed, all files formatted
- `codespell lib/ src/` — no issues
- `pyright src/charm.py src/integrations.py src/services.py src/configs.py` — **16 errors** (updated from 15)
- `mypy src/charm.py src/api_client.py src/integrations.py src/services.py src/configs.py` — 18 errors
- pytest (81 tests) — **81 passed, 34 deprecation warnings** (all from `loki_push_api.py:2272` calling deprecated `JujuVersion.from_environ()`)

**Coverage gaps**:
- No test for invalid `search_mode`/`bind_mode` config value (the gap that maps to the type-error risk)
- No test for invalid `log_level` config value
- No test for traefik `submit_route` failure (only mocked happy path)
- No test for `_cleanup_orphaned_relations` non-404 API errors (tested for 404, not for other exceptions)
- No test for `base_dn=None` (the `create_state()` fixture does not set config, relying on charmcraft.yaml defaults — the actual value is always a string, so this path is never hit)
- No test for `AuthentikConnectionError` or `AuthentikHttpError` propagation in `_holistic_handler` — the test harness catches only `CharmError`, not the API error base class
- No test for the `open_port()` method omitting METRICS_PORT (9300) — the `open_port_opens_ldap_and_ldaps` test only asserts 3389 and 636
- No test for the loki push API deprecation warning (would require running pytest with deprecation warnings enabled)
- Integration tests require the full Authentik stack — spread/integration tests exist but cannot be run in this environment due to missing `postgresql-k8s` on Juju 4.x

## Docs

**README.md** is thorough and accurate. Key strengths:
- Explains the dynamic service account design clearly
- Documents cached vs direct modes with upgrade implications
- SNI multiplexing explanation for multi-outpost deployments
- Proxy Protocol v2 explanation
- E2E verification steps with `ldapsearch`

**Gaps in README**:
- `AUTHENTIK_INSECURE` is hardcoded to `true` but this is not documented (tracked as GitHub issue #8)
- No troubleshooting section for common blocked states
- No documentation of the `ldap-client-<user>-<deployment-identity>-<relation-id>` username format
- The `metrics-endpoint` provider advertises port 9300 but the k8s service does not expose it — the README does not mention this limitation
- The `grafana-dashboard` provider cannot be used with `grafana-agent-k8s` — the README does not mention this incompatibility

**`CONTRIBUTING.md`**: Standard Juju SDK guidance, brief but sufficient.

**`docs/adr/001` and `002`**: ADRs for traefik-route and proxy protocol are detailed and accurate reflections of the implementation.

**charmhub description**: "Operator for Authentik LDAP Outpost" — minimal. The README is the real documentation.

## Open questions

### What could not be tested

**Full Authentik provisioning pipeline**: The Authentik server requires a PostgreSQL database, and `postgresql-k8s` does not support Juju 4.0.12 (requires < 4.0.0). A full end-to-end test of LDAP provider provisioning, service account creation, and traefik-route submission could not be performed. The 81 unit tests and code review give high confidence, but a live test would confirm the full API call chain.

**Invalid config values with active server relation**: Without a working server relation, the NOOP conditions prevent reconciliation when the server relation is absent. Testing invalid `search_mode`/`bind_mode` config values reaching the Authentik API (and whether they cause hook crashes via the uncaught `AuthentikApiError`) was not possible without a running server.

**Secret injection**: `juju exec --unit authentik-server/0 -- secret-add` hangs (blocks on an internal operation). Setting up a valid `authentik_token_secret_id` in the server-info relation required creating a Juju secret, which was not achievable from outside the charm agent's hook context. A fake token in the relation databag would make `get_provider_data()` return `None` (no token), keeping the outpost in `WaitingStatus` — the same state it already has.

### Other open questions

1. **`AUTHENTIK_INSECURE`**: Tracked in GitHub issue #8. The README does not document this limitation.

2. **`ldap-relation-broken` library warnings**: The glauth_k8s ldap library emits `'app' expected but not received` and `'app_name' expected in snapshot but not found` during the relation-broken hook. This is a library issue, not a charm issue, but worth tracking as it may indicate incorrect library cleanup behaviour.

3. **LXD/machine substrate**: Not applicable — the charm is k8s-only. Attempting to deploy on LXD fails with a clear error message.

4. **`juju trust` missing status**: The charm logs "Kubernetes resources patch failed: `juju trust` this application." on every hook when `juju trust` is not granted, but does not set a `WaitingStatus` indicating that `juju trust` would improve performance. A clear message would be more operator-friendly.
