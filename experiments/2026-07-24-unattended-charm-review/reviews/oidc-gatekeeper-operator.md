# oidc-gatekeeper-operator

`oidc-gatekeeper` is a single Kubernetes charm wrapping [oidc-authservice](https://github.com/arrikto/oidc-authservice) to provide OIDC authentication for Charmed Kubeflow, integrating with Dex, Istio, and Loki. The handler code is clean (centralised `ErrorWithStatus`/status pattern, good leader-election discipline) and the happy path is solid, but the charm has one critical, easily-triggered defect: setting `ca-bundle` to any non-empty value puts the charm into an unrecoverable `error` state via an uncaught `PathError`, and unsetting the config alone does not fix it. There are also three confirmed upstream bugs (unused `client-secret` config, hardcoded `OIDC_AUTH_URL`, no Pebble health checks), a broken `juju refresh` path from the published stable revision, and meaningful test/lint gaps that let real defects through CI. A maintainer should fix the `ca-bundle` crash first — it is a data-loss/availability risk for any operator who touches that config — then address the refresh-breakage and the missing unit-test coverage that let it ship.

| | |
|---|---|
| Repo | canonical/oidc-gatekeeper-operator @ 80f4b1c (2026-05-28) |
| Charms | oidc-gatekeeper |
| Substrate | k8s |
| Deployed | yes — `concierge-k8s-4`, started at `latest/edge` rev 641, refreshed to `ckf-1.10/stable` rev 615 |
| Reviewed | 2026-08-23 |

## What it does

Provides an HTTP reverse-proxy OIDC authenticator that integrates with Dex (via `dex-oidc-config`), publishes OIDC client info to Dex (via `oidc-client`), registers itself as an Istio external authorizer (via `forward-auth` and `istio-ingress-route-unauthenticated`), and optionally forwards logs to Loki. Runs the workload as non-root user (uid 584792).

## Deployment log

```
# Deployed to model rv-oidc-kg on concierge-k8s-4
juju deploy dex-auth --channel latest/edge --trust
juju deploy oidc-gatekeeper --channel latest/edge --trust
juju integrate oidc-gatekeeper:dex-oidc-config dex-auth:dex-oidc-config
```

- `dex-auth` deployed at rev 811 (`latest/edge`), came up in ~1 min
- `oidc-gatekeeper` deployed at rev 641 (`latest/edge`), came up in ~20s after the Dex relation was established
- Pebble workload (`oidc-authservice`) started within ~5s of container readiness
- OIDC environment variables confirmed in the Pebble plan:
  - `OIDC_PROVIDER: http://dex-auth.rv-oidc-kg.svc:5556/dex`
  - `CLIENT_ID: authservice-oidc`
  - `CLIENT_SECRET: GTD6XHFXJ80JBMBV7ATUI4ILVO3QK5` (auto-generated, 30-char uppercase-alphanumeric)
  - `SKIP_AUTH_URLS: /dex/`
  - `OIDC_AUTH_URL: /dex/auth` (hardcoded — see Finding #3)

Subsequent lifecycle steps:

1. Scale up to 3 units: non-leader units in `WaitingStatus("Waiting for leadership")`, Pebble service `inactive` on non-leaders. Scale back down: clean teardown.
2. `juju refresh --channel ckf-1.10/stable` (rev 615, a downgrade): **success**. Charm went `maintenance` → `stop` → `start`. Peer relation data (`client-secret`) preserved. Pebble plan correct after refresh. ~30s downtime.
3. `juju refresh --channel latest/edge` (rev 641) from rev 615: **failed**. Rev 641 exposes endpoints not present in rev 615. The failed refresh left the charm running normally at rev 615.
4. `juju remove-application oidc-gatekeeper`: confirmed clean teardown — pod terminated within ~30s, no dangling resources.

Second session:

5. `grafana-agent-k8s` (`1/stable`) deployed. `logging` relation requires `logging-consumer` on the remote end; oidc-gatekeeper uses `loki_push_api` as a consumer, not a provider. `metrics-endpoint` also failed — the charm has no `metrics` relation. **No observability integration is viable.**
6. `juju refresh --channel ckf-1.10/edge` (rev 642) from rev 615: same failure as rev 641 — `"one or more of the provided endpoints client-secret, dex-oidc-config, forward-auth, ... do not exist"`. The endpoint list matches the **local source** metadata, confirming the local source has new relations absent from published rev 615.
7. `istio-pilot` deployed and integrated via `ingress` and `ingress-auth`. Charm stayed `active`.
8. **Pod restart test**: `kubectl delete pod oidc-gatekeeper-0` — pod rescheduled, Pebble service `active` within ~30s, peer relation secret preserved (same `CLIENT_SECRET`).
9. **CA bundle failure injection**: setting `ca-bundle` to a valid certificate put the charm in `error` with a `PathError`. **Unsetting the config alone did not recover the charm** — required `juju resolve --no-retry` as well.

Other integrations attempted:

- `traefik-k8s` via `ingress`: `WaitingStatus` — incompatible interface (`serialized_data_interface` vs newer ingress library).
- `self-signed-certificates`: deployed and active, no relevant integration interface.
- `istio-pilot` via `ingress`/`ingress-auth`: integrated successfully, charm stayed `active`.

## Observed behaviour

### Happy path

- Deploy → active in ~30s total.
- Pebble service (`oidc-authservice`) starts automatically; logs show the server binding to `:8080` and `:8082`.
- Config changes (`oidc-scopes`, `skip-auth-urls`) trigger immediate Pebble layer update and service restart; logs show "Starting server" with the new config within seconds.
- Killing the workload process: Pebble auto-restarts it immediately with the same config (`startup: enabled`).
- Scale to 3 units: non-leaders join and sit in `WaitingStatus("Waiting for leadership")`, Pebble services `inactive`. Scale back to 1: clean teardown.
- Removing `dex-oidc-config`: `BlockedStatus("Missing relation with a Dex OIDC config provider. Please add the missing relation.")`; recovers to `active` on re-integration.
- Removing `ingress` while running: charm stays `active` — ingress is optional.
- Pod restart via `kubectl delete pod`: rescheduled, active within ~30s, peer secret preserved.

### Relation data confirmed

**`oidc-client`** (from `juju show-unit oidc-gatekeeper/0`):
```
id: authservice-oidc
name: Ambassador Auth OIDC
redirectURIs:
  - /authservice/oidc/callback
secret: GTD6XHFXJ80JBMBV7ATUI4ILVO3QK5  (same as peer secret)
```

**`ingress`** sent to istio-pilot:
```
port: 8080
prefix: /authservice
rewrite: /
service: oidc-gatekeeper
```

**`ingress-auth`** sent to istio-pilot:
```
port: 8080
service: oidc-gatekeeper
allowed-request-headers: [cookie, X-Auth-Token]
allowed-response-headers: [kubeflow-userid]
```

**`forward-auth`** (constructed but not exercised — no requirer related): `ForwardAuthConfig` JSON with `decisions_address: http://oidc-gatekeeper.<namespace>.svc.cluster.local:8080`, `app_names: []`, `headers: ["kubeflow-userid"]`.

### Failure injections

- **Remove `dex-oidc-config`**: → `blocked` with a clear message; recovers automatically on re-integration. ✓
- **Set `ca-bundle` to a valid certificate**: → `error`, `hook failed: "config-changed"`. Container-agent log:
  ```
  ops.pebble.PathError: permission-denied - cannot create directory: mkdir /etc/certs.mkdir-new: permission denied
  ```
  Propagates `service_environment` → `_oidc_layer` → `update_layer` → `main()`, exits the hook with code 1. **Unsetting `ca-bundle=""` alone does not recover it** — the charm stays in `"awaiting error resolution"`. Required `juju resolve --no-retry` in a separate shell. The `can_connect()` guard does not help — it only skips when the container is unreachable, not when the push is permission-denied. ✗ (Finding #1)
- **Set `ca-bundle` to a junk string**: same `PathError` — content is irrelevant, only presence of a non-empty value matters. ✗
- **Set `oidc-scopes` to `INVALIDS`**: accepted, Pebble layer updated, workload starts with `OIDCScopes:[openid INVALIDS]`. No charm-level validation, no status change.
- **Set `userid-claim` to `INVALID`**: same — accepted with no validation, no status change.
- **Set `client-secret` config to an arbitrary string**: Pebble plan's `CLIENT_SECRET` is unchanged, still the auto-generated peer secret. Confirms upstream issue #27. No status change.
- **Kill workload process**: Pebble restarts within ~1s, back to `active`. ✓
- **Integrate with `traefik-k8s` (`ingress`)**: → `waiting`, "List of ingress versions not found for apps: traefik-k8s" — incompatible interface, not a charm bug.
- **`remove-application --force`**: accepted, pod terminated within ~30s, no dangling resources. ✓

### Timing and resource use

- Install/start: ~20s deploy to active.
- Pebble restart on config change: ~1–3s.
- Refresh downtime: ~30s (`maintenance` → `stop` → `start`).
- Scale-up to 3: non-leaders join in ~30s, workload inactive on non-leaders.
- `update-status` fires every 5 min cleanly.
- No Pebble health checks implemented (open issue #82).
- Remove-application teardown: ~30s.
- Pod restart recovery: ~30s.
- CA-bundle error recovery: requires unsetting config **and** `juju resolve --no-retry`.

## Findings

### 1. `ca-bundle` push raises uncaught `PathError` in non-root container; charm cannot self-recover
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:200-207` (`service_environment` property, CA bundle push block)
- **Evidence**: `if self.model.config["ca-bundle"]:` → `if self._container.can_connect():` → `self._container.push("/etc/certs/oidc/root-ca.pem", ..., make_dirs=True, ...)`. The workload container runs as uid 584792 (non-root). Setting `ca-bundle` triggers `ops.pebble.PathError: permission-denied - cannot create directory: mkdir /etc/certs.mkdir-new: permission denied` (confirmed in the container-agent log). The exception propagates through `service_environment` → `_oidc_layer` → `update_layer` → `main()` and exits the `config-changed` hook with code 1, leaving the charm in Juju's "awaiting error resolution" state. Recovery requires **two** steps: `juju config oidc-gatekeeper ca-bundle=""` **and** `juju resolve --no-retry oidc-gatekeeper/0`; unsetting config alone does not trigger a retry. `can_connect()` only guards unreachable containers, not permission-denied pushes. Reproduced with both a junk string and a valid certificate.
- **Impact**: Any operator who sets `ca-bundle` to a non-empty value permanently breaks the charm with no actionable error message, and the two-step recovery procedure is undocumented.
- **Fix**: Pre-create `/etc/certs/oidc/` in the OCI image with writable permissions for the workload's uid, or catch `ops.pebble.PathError` in `service_environment` and raise `ErrorWithStatus(BlockedStatus, "CA bundle requires a writable /etc/certs/oidc/ directory in the container image")`.
- **Linter rule**: not mechanically checkable without knowing the container's run-as user and filesystem ACLs.

### 2. `kubernetes_service_patch` v1 library deprecated, removal due October 2025
- **Severity**: high
- **Kind**: lint
- **Where**: `src/charm.py:59` (`self.service_patcher = KubernetesServicePatch(...)`), import at line 30
- **Evidence**: Container agent logs: `WARNING: The kubernetes_service_patch v1 library is DEPRECATED and will be removed in October 2025. ... ops.Unit.set_ports functionality should be used instead.`
- **Impact**: Charm will break once the library is removed from `charmhub` tooling/lib support.
- **Fix**: Replace with `ops.Unit.set_ports([Port(8080, "http-port")])`.
- **Linter rule**: "usage of `kubernetes_service_patch` library" — mechanically checkable with a grep.

### 3. `client-secret` config option is unused (upstream issue #27)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:287-295` (`_check_secret`); `config.yaml`
- **Evidence**: `_check_secret()` iterates `self.model.relations["client-secret"]` (the peer relation) and generates a random password if none is stored; the `client-secret` config option is never read. Confirmed: `juju config oidc-gatekeeper client-secret="MY_SECRET"` leaves the Pebble plan's `CLIENT_SECRET` unchanged.
- **Impact**: Operators setting this config get no effect and no warning — silently misleading.
- **Fix**: Either remove the config option or wire it into `_check_secret()` as a fallback.
- **Linter rule**: not established.

### 4. `OIDC_AUTH_URL` hardcoded to `/dex/auth` (upstream issue #158)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:187`
- **Evidence**: `ret_env_vars["OIDC_AUTH_URL"] = "/dex/auth"` — hardcoded, ignoring any OIDC provider that doesn't use Dex's `/dex/auth` path.
- **Impact**: Breaks non-Dex OIDC providers even though the charm's Dex relation could supply an issuer URL to construct this dynamically.
- **Fix**: Construct from `issuer_url + "/auth"` or use OIDC discovery.
- **Linter rule**: not established.

### 5. No Pebble health checks implemented (upstream issue #82)
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/charm.py:212-231` (`_oidc_layer`)
- **Evidence**: The Pebble service has no `healthcheck` stanza. Workload logs show a readiness endpoint on port 8081, but no Pebble check references it. The workload container has no `curl`, `wget`, or `python3` available for ad-hoc checking.
- **Impact**: Juju cannot accurately determine workload health; a hung authservice process could stay reported `active`.
- **Fix**: Add a Pebble `check` (e.g. `exec: curl -f http://localhost:8081/ready`, `interval: 30s`) and reference it in the service definition.
- **Linter rule**: not established.

### 6. `juju refresh` fails: local source exposes endpoints absent from published rev 615
- **Severity**: medium
- **Kind**: bug
- **Where**: `metadata.yaml` (local source) vs `juju info oidc-gatekeeper` (charmhub rev 615)
- **Evidence**: `juju info oidc-gatekeeper` for rev 615 lists only `client-secret, dex-oidc-config, ingress, ingress-auth, juju-info, logging, oidc-client`. The local source additionally defines `forward-auth`, `istio-ingress-route-unauthenticated`, `service-mesh`, `provide-cmr-mesh`, `require-cmr-mesh`. `juju refresh` from rev 615 to rev 641 or rev 642 fails with `"one or more of the provided endpoints ... do not exist"`, listing the local source's relation names. Published `ckf-1.10/edge` rev 642 (2026-07-30) fails the same way.
- **Impact**: Operators cannot upgrade via `juju refresh` from the currently published stable revision without first removing existing relations; the upgrade path is undocumented.
- **Fix**: Backport the new relations to a compatible published revision (as empty placeholders) or document the required pre-upgrade steps.
- **Linter rule**: not mechanically checkable without comparing source and published charm metadata.

### 7. Integration tests assert only status, not behaviour
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py`, `tests/integration/test_charm_ambient.py`
- **Evidence**: The main deploy test asserts only `workload_status == "active"`. Upstream issue #130 confirms "integration tests are not detecting failures in the workload." `test_login_redirection` and `test_authservice_url_is_unauthenticated` do assert real HTTP behaviour, but only for the ambient-mesh configuration.
- **Impact**: Regressions like the CA-bundle crash (Finding #1) can pass CI.
- **Fix**: Add integration tests that read Pebble plan env vars, exercise the readiness endpoint, and assert `oidc-client` relation data contents.
- **Linter rule**: not established.

### 8. Unit tests do not catch the CA-bundle failure mode
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_operator.py:85` (`test_ca_bundle_config`)
- **Evidence**: `test_ca_bundle_config` passes (13/13 tests pass) but only checks that `CA_BUNDLE` is present in the environment; it never exercises `container.push()`. `ops.testing.Harness` does not enforce container filesystem permissions, so the permission-denied error is never simulated.
- **Impact**: The single most serious defect in the charm (Finding #1) is invisible to the test suite.
- **Fix**: Add a unit test that mocks `container.push()` raising `ops.pebble.PathError` and asserts `service_environment` raises `ErrorWithStatus` with `BlockedStatus`.
- **Linter rule**: not established.

### 9. Owned libraries ship 67 ruff violations invisible to CI
- **Severity**: medium
- **Kind**: lint
- **Where**: `lib/charms/oauth2_proxy_k8s/v0/forward_auth.py` (51 errors), `lib/charms/dex_auth/v0/dex_oidc_config.py` (13 errors), `src/charm.py` (3 errors)
- **Evidence**: `ruff check src/charm.py lib/charms/dex_auth/v0/dex_oidc_config.py lib/charms/oauth2_proxy_k8s/v0/forward_auth.py` reports 67 violations: deprecated typing (`UP035`/`UP006`), unsorted/unused imports, unnecessary `pass`, explicit `return None`, and more. CI's `tox.ini` uses `pflake8` (pyflakes + pycodestyle), which does not run ruff rules.
- **Impact**: Deprecated typing (`typing.List` → `list`) will break under Python 3.13+; 46 of the 67 violations are auto-fixable and currently ship unnoticed.
- **Fix**: Add `ruff check src/ lib/` to the `lint` tox environment.
- **Linter rule**: "CI linting uses `pflake8` which does not cover modern ruff rules" — mechanically checkable.

### 10. Renovate configuration error blocks automated dependency updates
- **Severity**: medium
- **Kind**: ci
- **Where**: `renovate.json` (open issue #225, since 2025-10-03)
- **Evidence**: "Action Required: Fix Renovate Configuration. Error type: Preset is invalid JSON (github>canonical/charmed-kubeflow-workflows)."
- **Impact**: No automated dependency-update PRs while the preset error persists.
- **Fix**: Fix the `renovate.json` preset reference.
- **Linter rule**: not established.

### 11. Pebble layer recomputed unconditionally on every hook
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:115` (`main()` calls `update_layer` unconditionally); `_oidc_layer` property
- **Evidence**: `main()` calls `update_layer(self._container_name, self._container, self._oidc_layer, self.logger)` on every hook (start, config-changed, pebble-ready, relation-changed, upgrade-charm, etc.). `_oidc_layer` re-evaluates `self.service_environment`, including `_check_secret()`, on every call, even though `update_layer` (from `charmed_kubeflow_chisme`) only calls `set_plan()` when the plan actually differs.
- **Impact**: Wasted relation-data reads and secret lookups on every hook invocation.
- **Fix**: Cache the computed layer, or compute the secret once in `main()` and pass it into `service_environment`.
- **Linter rule**: "property that performs I/O or relation-data access called unconditionally in a hot path" — not mechanically checkable without dataflow analysis.

### 12. `service_environment` calls `_check_secret()` redundantly
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:223` (`self.service_environment` access inside `_oidc_layer`)
- **Evidence**: In a normal `main()` execution, `_check_secret()` is called once explicitly (line 110) and again when `self._oidc_layer` evaluates `self.service_environment`. The second call is a no-op but adds an unnecessary relation-data pass.
- **Impact**: Minor wasted work; no functional bug.
- **Fix**: Have `service_environment` accept the secret as a parameter from `main()`.
- **Linter rule**: not established.

### 13. `_ambient_mesh_ingress()` called unconditionally in `__init__`
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:69` (call site), method at line 122
- **Evidence**: `self._ambient_mesh_ingress()` runs on every hook invocation. When the `istio-ingress-route-unauthenticated` relation exists, it calls `submit_config()`, writing identical data to the relation databag on every hook and triggering `relation-changed` on the remote side.
- **Impact**: Unnecessary relation-changed churn for a static configuration.
- **Fix**: Move `submit_config()` to a `relation-created` event observer.
- **Linter rule**: not established.

### 14. `forward_auth.py` `_compare_apps` has a type-confusion bug (dormant in this charm)
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/oauth2_proxy_k8s/v0/forward_auth.py:551-554`
- **Evidence**: `ingress_apps = requirer_data["ingress_app_names"]` (line 551) is a JSON *string*, while `app_names` (line 552) is correctly `json.loads()`-decoded into a list. `if app not in ingress_apps:` (line 553) then checks a string against a JSON string using substring semantics rather than list membership — e.g. `"jupyter-ui" in '["jupyter-ui","tensorboard"]'` is `False`.
- **Impact**: Would emit `InvalidForwardAuthConfigEvent` incorrectly on the requirer side. oidc-gatekeeper only uses the provider side and never calls `_compare_apps`, so the bug is dormant here but live for any charm using the requirer side.
- **Fix**: `ingress_apps = json.loads(requirer_data["ingress_app_names"])`.
- **Linter rule**: not established.

### 15. Unit tests use deprecated `ops.testing.Harness`
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_operator.py:21`
- **Evidence**: `PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: ...`
- **Impact**: Test suite is on a deprecation path; will require migration eventually.
- **Fix**: Migrate to `ops.testing`'s `scenario`-based harness.
- **Linter rule**: not established.

### 16. Test controller (Juju 3.6) differs from production controller (Juju 4.x)
- **Severity**: low
- **Kind**: test-gap
- **Where**: `concierge.yaml` vs `concierge-k8s-4`
- **Evidence**: `concierge.yaml` pins Juju 3.6/stable for CI; production runs Juju 4.0.12. Juju 3.6 and 4.x differ in `juju refresh` endpoint-compatibility checks.
- **Impact**: CI may not catch refresh-compatibility issues (such as Finding #6) that manifest on the production controller version.
- **Fix**: Update `concierge.yaml` to a Juju 4.x channel matching production.
- **Linter rule**: not established.

### 17. Observability integration not viable with the current charm design
- **Severity**: low
- **Kind**: ux
- **Where**: `metadata.yaml` (provides `forward-auth`, `oidc-client`; no `metrics-endpoint`)
- **Evidence**: The charm consumes `loki_push_api` (`LogForwarder`) but does not provide a `logging-provider` or `metrics-endpoint` relation. `juju integrate oidc-gatekeeper:logging grafana-agent-k8s:logging-provider` failed (requires `logging-consumer` on the remote side); `juju integrate oidc-gatekeeper:metrics grafana-agent-k8s:metrics-endpoint` failed with "relation endpoint not found."
- **Impact**: No path to hook the charm into `grafana-agent-k8s` for metrics or forwarded logging in the standard COS pattern.
- **Fix**: Add a `metrics-endpoint` and/or `grafana-dashboards` relation if observability is desired.
- **Linter rule**: not established.

### 18. `ServiceMeshConsumer` instantiated without being stored meaningfully
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:65` (`self._mesh = ServiceMeshConsumer(self)`)
- **Evidence**: `ServiceMeshConsumer(self)` is assigned to `self._mesh` but never referenced again — it observes its own events internally via `framework.observe`. Not a bug, just unnecessary storage (contrast with `self._logging = LogForwarder(charm=self)`, which is stored and unused identically but is at least named consistently).
- **Impact**: Cosmetic only.
- **Fix**: Drop the assignment — call `ServiceMeshConsumer(self)` without storing the return value.
- **Linter rule**: not established.

### 19. No action commands; upgrade handled entirely by `main()` on `upgrade_charm`
- **Severity**: info
- **Kind**: ux
- **Where**: `metadata.yaml` (no `actions.yaml`)
- **Evidence**: No actions are defined. `upgrade_charm` is observed and handled by `main()`'s full reconciliation loop; `ServiceMeshConsumer` also observes `upgrade_charm` → `_relations_changed` → `update_service_mesh`.
- **Impact**: No manual intervention required for upgrades (aside from the refresh-endpoint issue in Finding #6).
- **Fix**: none required.
- **Linter rule**: not established.

## Worth copying

- **`main()` handler with `ErrorWithStatus` exception pattern** (`src/charm.py:107-121`): `try/except ErrorWithStatus` centralises all status-setting; each helper raises a typed exception caught in one place. Right pattern for leader-election charms.
- **`DexOidcConfigRequirerWrapper._validate_relation`** (`lib/charms/dex_auth/v0/dex_oidc_config.py:237-248`): raises typed exceptions before any data access — clean error hierarchy.
- **`ForwardAuthConfig` dataclass** (`lib/charms/oauth2_proxy_k8s/v0/forward_auth.py:175`): clean `from_dict`/`to_dict` round-trip (note: `_compare_apps`, Finding #14, has a bug using it).
- **`forward_auth.py` `_load_data`/`_dump_data`** (`lib/charms/oauth2_proxy_k8s/v0/forward_auth.py:108-140`): correctly uses `json.loads()`/`json.dumps()` for nested fields.
- **Non-root workload user** (`metadata.yaml:45`): `charm-user: non-root`, uid 584792 — correctly isolates workload from the charm agent.
- **`LogForwarder` pebble-ready observation** (`lib/charms/loki_k8s/v1/loki_push_api.py:2571-2581`): observes `pebble_ready` per container, uses `can_connect()` guards for relation events — correct Pebble log forwarding.
- **`disable_inactive_endpoints`** (`lib/charms/loki_k8s/v1/loki_push_api.py:2497-2520`): correctly disables Pebble log forwarding for removed Loki endpoints by checking the current plan and adding a disable layer.

## Common-practice notes

- **Leader-election design**: correctly requires leadership for all operations (`_check_leader()` raises `WaitingStatus`); non-leaders do no work and have inactive Pebble services.
- **`update_layer` from `charmed_kubeflow_chisme`**: standard pattern across the Kubeflow-charms ecosystem.
- **`serialized_data_interface` for ingress**: pinned `<0.4`, limiting compatibility to charms with `_supported_versions` (e.g. istio-pilot) and excluding traefik-k8s.
- **`pyproject.toml` missing `version`**: has `[project]` but no `version` field, causing `uv`/`ruff` to fail parsing.
- **`ops` version pin**: `pyproject.toml` pins `ops>=2.17.1,<3`; ops 2.23.4 has a `scenario`/`Harness` incompatibility (JujuContext capitalisation), ops 3.8.0 works.
- **Python version**: `pyproject.toml` requires `python>=3.12,<4.0`; `charmcraft.yaml` builds on Ubuntu 24.04 (Python 3.12) — consistent.
- **`cosl` unused directly**: declared as a dependency but not imported by the charm — used transitively by `loki_push_api.py` for `JujuTopology`.

## Tests

### Unit tests
- **Location**: `tests/unit/test_operator.py`
- **Count**: 13 tests
- **Result**: 13/13 pass (with `ops==3.8.0`, `serialized-data-interface==0.3.6`, `charmed-kubeflow-chisme==0.4.29`; `ops==2.23.4` is incompatible due to a scenario/Harness mismatch)
- **Framework**: `ops.testing.Harness` (deprecated — Finding #15)
- **Coverage gaps**:
  - No test for `ca-bundle` with a non-root container push failure (Finding #1, the most critical bug)
  - No test for the `upgrade_charm` hook
  - No test for `_check_secret()` when no peer relation exists
  - No test asserting `ingress`/`ingress-auth` relation data sent
  - No test asserting `oidc-client` relation data sent
  - No test for invalid config values (`oidc-scopes`, `userid-claim`)

### Integration tests
- **Location**: `tests/integration/test_charm.py`, `tests/integration/test_charm_ambient.py`
- **Style**: `pytest-operator` with `ops_test.model.deploy/integrate/wait_for_idle`
- **Not run**: require istio-pilot, dex-auth, jupyter-ui in the model (not available in this review environment)
- **Known issue**: upstream issue #130 — tests rely on `wait_for_idle(status="active")` and do not detect workload failures
- **Observations**: `test_charm_ambient.py`'s `test_login_redirection` (asserts 302 with `dex/auth?client_id`) and `test_authservice_url_is_unauthenticated` (asserts 200 with "OK") are genuine behavioural tests, but only for the Istio ambient-mesh path.

## Docs

- **README.md**: accurate deployment instructions, verified against this review's deployment. "Limitations" section correctly notes the charm only works within a Charmed Kubeflow model.
- **Config descriptions**: `ca-bundle` omits the non-root container constraint that causes Finding #1. `client-secret` is misleading (Finding #3). `oidc-scopes` and `userid-claim` have no validation note.
- **charmhub description**: consistent with `metadata.yaml`.
- **Contributing guide**: references `concierge.yaml` for local testing.

## Open questions

1. **What changed between `latest/edge` (rev 641) and `ckf-1.10/stable` (rev 615)?** Resolved: the local source has new relations absent from rev 615, confirmed by comparing `juju info oidc-gatekeeper` against `metadata.yaml`.
2. **Can `pebble-ready` fire before the peer relation exists?** If so, `_check_secret()` raises `ErrorWithStatus("Waiting for Client Secret", WaitingStatus)`, caught correctly by `main()`. Believed safe but untested.
3. **`public-url` config cleanup** (issue #167): the option no longer exists in the codebase (confirmed by grep); `test_upgrade` still references it but was not run in this review.
4. **`dex-oidc-config` relation data appeared empty in `juju show-unit`** but the charm read it correctly and went active — may be a `juju show-unit` display issue rather than a real data problem. (unverified)
5. **`istio-ingress-k8s`** (rev 61, `2/edge`) went to `error` with `hook failed: "leader-elected"`, which prevented end-to-end testing of the `forward-auth` relation.
6. **Pebble reports 200 OK for a file push that never lands**: when `ca-bundle` is set, the Pebble API returns `200` for `POST /v1/files` for a *different*, Pebble-initiated operation, while the charm's own `container.push()` call over the same socket raises `PathError`. Confirmed via the container-agent log showing the exception.
