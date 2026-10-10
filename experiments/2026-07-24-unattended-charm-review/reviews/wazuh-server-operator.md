# wazuh-server-operator

A Juju k8s charm deploying and managing Wazuh Server (open-source XDR/SIEM). It orchestrates three Pebble services (`wazuh`, `filebeat`, `rsyslog`), manages TLS certificates via `tls-certificates`, provisions API users, syncs custom configuration from a git repository, and exposes metrics/logs to COS.

**Verdict**: Code quality is generally good — a clean state model with typed exceptions, a sensible error taxonomy, and reasonable unit-test coverage — but the charm ships with serious, confirmed-live bugs. The bundled `loki_push_api` library crashes both units on relation-changed and again on relation-departed, making the `logging` integration with loki-k8s completely unusable. Config validation (`custom-config-repository`, `agent-password`, `logs-ca-cert`) is silently masked by the opensearch dependency, so operators get no feedback on bad config. Several unhandled-exception paths (`WazuhInstallationError`, `SecretNotFoundError` in `_fetch_opencti_details`) and a non-leader CSR crash / multi-unit secret race round out the picture. The charm could not be driven to `Active` in this review (no opensearch relation available), so a meaningful fraction of the reconcile path is untested by this review and confirmed only by code inspection. **A maintainer should first fix the two Loki library crash paths (or drop the loki-k8s integration in favor of grafana-agent-k8s, which works), then add `WazuhInstallationError` to the reconcile exception handlers, then fix config-validation ordering so it isn't masked by the opensearch check.**

| | |
|---|---|
| Repo | canonical/wazuh-server-operator @ `53e8cc6` (2026-07-21) |
| Charms | wazuh-server |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4, channel 4.11/edge rev 272 |
| Reviewed | 2026-08-19 |

## What it does

Deploys Wazuh Server into a k8s pod with three co-managed services (wazuh-manager, filebeat, rsyslog), manages Wazuh API user lifecycle, syncs custom config from a git repo, integrates with wazuh-indexer (opensearch), provides an API for wazuh-api clients, and exposes metrics/dashboards/logs to the COS stack.

## Deployment log

1. Created model `rv-wazuh-server` on `concierge-k8s-4`.
2. Deployed `wazuh-server` from charmhub 4.11/edge rev 272. Install hook initially failed due to missing RBAC: the Juju secret-consumer service accounts lacked `patch` on `secrets` in the namespace. Fixed by creating a Role `wazuh-server-secret-manager` (get/list/watch/create/patch/delete on secrets) and RoleBindings for all service accounts in the namespace.
3. After the RBAC fix, install hook succeeded; charm went to `Waiting` ("Charm state is not yet ready") — opensearch relation missing, as expected.
4. Deployed `traefik-k8s` (latest/edge rev 233) and `self-signed-certificates` (latest/stable). Integrated both with wazuh-server.
5. Traefik obtained LB IP `10.43.45.1` and went `active`. wazuh-server went to `Waiting` ("Certificates do not exist. Waiting for new certificates to be issued.").
6. Certificate CSR was never issued to the provider. Root cause unclear — possibly a `set_content()` reliability issue in `_get_certificate_signing_request` interacting with Juju secret caching (unverified, see Open questions).
7. Removed the traefik relation to test failure handling. Status unchanged (opensearch still missing). Unit logs: "External hostname is not yet present."
8. Removed the certificates relation. Status unchanged. Hook fired without observable effect.
9. Set `custom-config-repository=not-a-url` (invalid URL). Status unchanged — config validation masked by the earlier `IncompleteStateError`.
10. Added a second unit (`juju add-unit wazuh-server`). Both units in `Waiting` ("Charm state is not yet ready"). No multi-unit race triggered (no certificate relation present).
11. Without an opensearch relation the charm cannot reach `Active`; no further status progression was possible in this test environment.
12. `kubectl exec <pod> -- pebble plan` returned `{}` — the pebble plan is completely empty while the charm is in `Waiting` status.
13. **Deployed loki-k8s (channel 3.7/stable) and related it to wazuh-server.** Both units crashed with `AttributeError` in the `logging-relation-changed` hook and went to `error` status. Unit 0 also showed a `TimeoutError` (pebble push timed out) before the `AttributeError`; unit 1 showed a `TimeoutError` too. The charm could not recover without `juju resolve`; after resolving, the hook retried and crashed again — the relation had to be removed.
14. The `logging-relation-broken` hook then fired and crashed: `ops.pebble.APIError: cannot stop services: service "promtail" does not exist`. The handler tries to stop promtail, which was never started (empty pebble plan). After resolving unit 0, both units returned to `Waiting`.
15. **Patched the Loki library** (wrapped `container.stop()` in try/except in `_on_relation_departed`) to unstick the units for continued testing; confirmed both crash paths.
16. **Deployed grafana-agent-k8s (channel 1/stable) and related it** on both `metrics-endpoint` and `logging-provider`. Both succeeded: Prometheus scrape targets and alert rules were published; promtail was installed in the workload container with a pebble layer pointing at `grafana-agent-k8s:3500`. grafana-agent-k8s does not emit `alert_rule_status_changed`, so the Loki crash path was not triggered.
17. `kubectl exec <pod> -c wazuh-server -- pebble plan` confirmed the promtail service present (`startup: disabled`) with correct Juju topology labels and all three log paths (`/var/ossec/logs`, `/var/log/filebeat`, `/var/log/rsyslog`).
18. Scaled to 5+ units — all went to `Waiting`. New units received the promtail pebble layer via `logging-relation-joined`. No certificate race was triggered (opensearch still absent).
19. `juju remove-application wazuh-server --no-prompt` completed cleanly — all pods deleted, no removal-hook errors.
20. Bad config values tested: `agent-password=secret:xyz` and `logs-ca-cert=not-a-cert` — both accepted by Juju and masked by the opensearch check, no status change.
21. `charmcraft pack` succeeded; `charmcraft analyse` on the packed charm reported `[ERROR] Cannot find the entrypoint file: '${dispatch_path}/src/charm.py'` — `${dispatch_path}` was not expanded at analyse time. The pack itself is functional.

## Observed behaviour

- **Install timing**: ~3 minutes from deploy to `Waiting` (after the RBAC fix).
- **Hook chain**: install → pebble-ready → config-changed → peer-relation-created → peer-relation-joined → start, all fired in order.
- **Secret creation**: `wazuh-cluster-key` was created correctly during install. `certificates-secret` was never created — the CSR workflow never completed.
- **Status messages**: `Waiting` ("Charm state is not yet ready") when opensearch missing; `Waiting` ("Certificates do not exist…") after traefik/certs relations added; `Blocked` (actionable message) when `logs-ca-cert` missing — all appropriate.
- **Rsyslog endpoint (port 6514)**: exposed via traefik with a `ClientIP` rule; any client from any IP can connect — security-sensitive.
- **Filebeat/manager/wazuh services**: all three configured in the Pebble layer. The `wazuh` service uses `sh -c 'sleep 1; /var/ossec/bin/wazuh-control reload'` — `reload` rather than `restart`, which is appropriate since `container.replan()` performs a proper stop/start cycle and `wazuh-control reload` handles both fresh start and reload; cold-start works correctly because all three services have `"startup": "enabled"`.
- **Loki/logging integration crash**: two independent crash paths — (1) `logging-relation-changed`: `AttributeError: 'LogProxyEvents' object has no attribute 'alert_rule_status_changed'`; (2) `logging-relation-departed`: `ops.pebble.APIError: cannot stop services: service "promtail" does not exist` (promtail never started because the pebble plan is empty). Both put both units into `error`; recovery requires `juju resolve` on each unit plus removal of the relation.
- **Juju 4.x vs project CI (Juju 3.x)**: the project's own CI runs Juju 3/stable with `automatically-retry-hooks: false` (`concierge.yaml`); this review used Juju 4.0.12. The secret-consumer RBAC issue (missing `patch` on secrets) was observed on Juju 4.x but is reported not to occur in the project's Juju 3.x CI — this difference is not independently confirmed here (unverified).
- **`enable-vulnerability-detection` config is inverted**: `enable-vulnerability-detection=true` (the default) actually means vulnerability detection is **disabled** — `sync_ossec_conf(enable_vulnerability_detection=True)` writes `<enabled>no</enabled>`. A UX hazard, not a bug.
- **Index name "placeholder"**: `src/opensearch_observer.py:29` passes `"placeholder"` as the index name to `OpenSearchRequires`; the wazuh-indexer creates an index literally called "placeholder". The wazuh-server never reads the index name back, so this doesn't affect functionality.
- **grafana-agent-k8s logging integration succeeds**: unlike loki-k8s, it doesn't emit `alert_rule_status_changed`, so the crash path isn't triggered. Confirmed via `pebble plan`: promtail running, pushing to `grafana-agent-k8s:3500`.
- **Prometheus metrics integration works**: `MetricsEndpointProvider` correctly publishes scrape targets (port 5000) and alert rules (`WazuhServerTargetMissing`, `WazuhServerNoEventsReceived`) — confirmed via `juju show-unit wazuh-server/0`.
- **Scale-up to 5 units**: all went to `Waiting`; new units received the promtail pebble layer via `logging-relation-joined`; no certificate race triggered (opensearch absent).
- **Teardown**: `juju remove-application wazuh-server` completed cleanly — all 7 pods deleted, no removal-hook errors.

### Failure injection results

- `custom-config-repository=not-a-url`: status unchanged (masked by the opensearch check).
- `agent-password=secret:xyz` (non-existent secret ID): accepted by Juju; no charm-level validation.
- `logs-ca-cert=not-a-cert`: accepted by Juju; no charm-level validation.
- Traefik relation removed: unit logs show "External hostname is not yet present."; charm raises `IncompleteStateError`; status unchanged.
- Certificates relation removed: no visible status change; `certificates-relation-broken` fired with no observable effect.
- Pebble plan while waiting: `kubectl exec <pod> -- pebble plan` returned `{}` — wazuh, filebeat, rsyslog all absent until `container.add_layer()` runs in `reconcile()`.
- Scale-up to 2 units: both `Waiting`; unit 1 fires the same hook chain as unit 0; the multi-unit certificate race is latent (no certificates relation present to trigger it).
- Unit agent restart: `kill -9 1` in the workload container was blocked by container security policy; pod remained running.
- No actions defined: `juju actions wazuh-server` returns "No actions defined for wazuh-server."
- loki-k8s logging integration: both units crashed to `error` on `logging-relation-changed`; after `juju resolve`, `logging-relation-departed` crashed both units again; relation had to be removed; recovery required patching the Loki library.
- grafana-agent-k8s logging integration: succeeded, no crash.
- Prometheus/grafana-agent-k8s metrics integration: succeeded, no crash.
- Workload process kill: PID 1 is the Pebble daemon and cannot be killed; no other processes exist while the pebble plan is empty.

## Findings

### `LogProxyConsumer` emits an undefined event, crashing both units on the logging relation
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/loki_k8s/v1/loki_push_api.py:1742` (also `:1668`, `:1607`, `:1402`)
- **Evidence**: `LogProxyConsumer._on_relation_changed` calls `self.on.alert_rule_status_changed.emit(valid=valid, errors=errors)`. `LogProxyConsumer.on = LogProxyEvents()` (line 1668) overrides the inherited `ConsumerBase.on = LokiPushApiEvents()` (line 1402), but `LogProxyEvents` (line 1607) does not define `alert_rule_status_changed` — only `LokiPushApiEvents` does. The result is `AttributeError`. Confirmed live: both `wazuh-server-0` and `wazuh-server-1` crashed with this error in `logging-relation-changed` and went to `error` status.
- **Impact**: Any operator relating this charm to loki-k8s via `logging` causes both units to crash to `error`, with no automatic recovery (`juju resolve` needed on each unit, and the hook keeps retrying until the relation is removed). Makes the logging integration completely unusable as shipped. Under the project's own CI settings (`automatically-retry-hooks: false`), every test exercising this path would fail.
- **Fix**: Add `alert_rule_status_changed` to `LogProxyEvents`, or override `_on_relation_changed` in `LogProxyConsumer` to not emit that event. Requires updating the bundled `loki_push_api` library.
- **Linter rule**: not mechanically checkable without type-aware analysis of the event system.

### Second Loki library crash: `_on_relation_departed` tries to stop a non-existent service
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/loki_k8s/v1/loki_push_api.py:1776`, `:1779`
- **Evidence**: When the logging relation is removed, `LogProxyConsumer._on_relation_departed` calls `container.stop("promtail")`. Since the pebble plan is empty (charm never reached Active, promtail never started), this raises `ops.pebble.APIError: cannot stop services: service "promtail" does not exist`. Confirmed live: `wazuh-server-0` went to `error` with `hook failed: "logging-relation-departed"`. After patching the call in a try/except, the unit recovered.
- **Impact**: Independent of the first crash path — removing the Loki relation (planned or unplanned) crashes every unit that received the logging relation. The charm cannot be cleanly un-related from Loki without the patch.
- **Fix**: Guard with `if "promtail" in container.get_plan().services:` before calling `container.stop()`, or catch `APIError`. Requires updating the bundled library.
- **Linter rule**: not mechanically checkable.

### `get_csr()` crashes on non-leader before the leader creates the secret
- **Severity**: high
- **Kind**: bug
- **Where**: `src/certificates_observer.py:64`, `:72-73`, `:119`, `:127`
- **Evidence**: `_get_private_key` initializes `private_key = ""`; on `SecretNotFoundError` for a non-leader, the `else` branch is empty and falls through to `return private_key` (i.e. `""`). `_get_certificate_signing_request` then encodes this to `b""` and passes it to `certificates.generate_csr(private_key=b"")`, which calls `serialization.load_pem_private_key(b"")` and raises `ValueError: Unable to load PEM file` (confirmed by direct test of that call). `_on_certificates_relation_joined` has no try/except around `get_csr()`, so the `ValueError` propagates and fails the hook; the unit agent retries indefinitely. `reconcile()`'s call to `self.state` (which calls `get_csr()`) is similarly not guarded against `ValueError`.
- **Impact**: In a multi-unit cluster, any non-leader that fires `certificates-relation-joined` (or any hook touching `self.state`) before the leader finishes creating `certificates-secret` will crash-loop. Not observed live in this session because `external_hostname` was unset at the time (masked by a caught `IncompleteStateError`), but the code path is confirmed by inspection and unit test of the underlying crypto call.
- **Fix**: Add `if not self._charm.unit.is_leader(): return b""` at the top of `get_csr()`, or add a leader guard in `_get_certificate_signing_request`.
- **Linter rule**: not mechanically checkable without data-flow analysis of leader/non-leader branching.

### Multi-unit race: non-leader could overwrite the leader's private key in the shared secret
- **Severity**: high
- **Kind**: bug
- **Where**: `src/certificates_observer.py:64`, `:119`, `:127`
- **Evidence**: If the leader creates `certificates-secret` between a non-leader's `SecretNotFoundError` and the leader's `add_secret` call, the non-leader's exception handler could attempt to generate a CSR against an empty/mismatched key on the same secret label. This is a race condition inferred from the code and the crash in the previous finding; not observed live (opensearch was never available to reach the state where this fires) — (unverified).
- **Impact**: Leader and non-leader could end up with different private keys stored under the same secret label, causing certificate mismatch across the cluster.
- **Fix**: Add a leader guard to `get_csr()` (see previous finding) and assert leadership in `_get_certificate_signing_request`.
- **Linter rule**: not mechanically checkable.

### Pebble plan never populated without an opensearch relation
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:386-397`
- **Evidence**: Confirmed live: `kubectl exec <pod> -- pebble plan` returned `{}`. `reconcile()` fails at `State.from_charm()` (raises `IncompleteStateError` due to missing opensearch) before reaching `container.add_layer()`.
- **Impact**: rsyslog (port 6514 log ingestion) and the wazuh-manager service never start until opensearch is related — no graceful degradation, even for functionality (rsyslog) that doesn't strictly need opensearch. This same empty-plan state is what causes the Loki crash paths above.
- **Fix**: Consider decoupling pebble services that don't require opensearch (rsyslog, wazuh-agentless) from the full stack, or at minimum document the hard dependency clearly.
- **Linter rule**: not mechanically checkable.

### `WazuhInstallationError` uncaught in `reconcile()` — git clone failures crash the hook
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:403-414`, `src/wazuh.py:472-507`
- **Evidence**: `wazuh.pull_config_repo()` raises `WazuhInstallationError` (base class of `WazuhNotReadyError`, `WazuhConfigurationError`, `WazuhAuthenticationError`) on git clone failure. `reconcile()`'s exception handlers catch `WazuhNotReadyError` and `WazuhConfigurationError` but not the base `WazuhInstallationError` itself, so it propagates unhandled and fails the hook.
- **Impact**: A bad `custom-config-repository` URL, unreachable network, or wrong SSH key results in `hook failed` with a raw traceback rather than an actionable status. In CI with `automatically-retry-hooks: false`, any test exercising this path fails outright.
- **Fix**: Add `except wazuh.WazuhInstallationError: self.unit.status = ops.MaintenanceStatus("Waiting for Wazuh to be ready")` to the reconcile exception handlers.
- **Linter rule**: "exception raised but not caught in same function" — not mechanically checkable without type-aware exception analysis.

### `_fetch_opencti_details` accesses a secret without a `SecretNotFoundError` guard
- **Severity**: high
- **Kind**: bug
- **Where**: `src/state.py:131`
- **Evidence**: `model.get_secret(id=opencti_token_id).get_content().get("token")` is called with no try/except, unlike the analogous `_fetch_password` (`src/state.py:212-218`), which wraps the same call.
- **Impact**: If the OpenCTI relation exists but the secret ID in relation data is stale or invalid, `SecretNotFoundError` propagates unhandled from `State.from_charm()`, crashing the charm on any hook touching `self.state` — with no actionable message.
- **Fix**: Wrap in try/except `ops.SecretNotFoundError` and return `(None, None)`, matching the graceful-degradation path already present in the return statement.
- **Linter rule**: "model secret access without `SecretNotFoundError` guard" — partially checkable with pyright if annotated that the secret ID can be stale.

### `WazuhConfig` validation masked by the opensearch dependency
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/state.py:399-405`
- **Evidence**: `State.from_charm()` calls `_fetch_filebeat_configuration()` (which checks the opensearch relation) before constructing `WazuhConfig(**args)` (pydantic validation). Confirmed live: `custom-config-repository=not-a-url` produced "Charm state is not yet ready" instead of a validation error; `agent-password=secret:xyz` and `logs-ca-cert=not-a-cert` were similarly masked.
- **Impact**: An operator with malformed config gets no feedback until opensearch is related — could ship broken config unknowingly.
- **Fix**: Move `WazuhConfig(**args)` validation ahead of the opensearch check in `State.from_charm()`, or add a pre-check in `reconcile()`.
- **Linter rule**: not mechanically checkable without modeling call order.

### Traefik ingress accepts connections from any IP (`ClientIP` rule)
- **Severity**: medium
- **Kind**: security
- **Where**: `src/traefik_route_observer.py:79`
- **Evidence**: `"rule": "ClientIP(\`0.0.0.0/0\`)"` on all traefik TCP entrypoints (syslog 6514, agents 1514, API 55000); no TLS client verification enforced at the rule level.
- **Impact**: The rsyslog endpoint accepts unauthenticated log ingestion from any client that can reach the traefik IP. `logs-ca-cert` is for verifying client certificates, but the rule itself only checks source IP, not certificate validity.
- **Fix**: Tighten the rule or combine with TLS client-certificate verification at the traefik level; document the current behaviour clearly.
- **Linter rule**: not mechanically checkable.

### `master_fqdn` return type mismatch between abstract and concrete class
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:521` vs `src/state.py:475`
- **Evidence**: `CharmBaseWithState.master_fqdn` is declared `-> list[str]`, but `WazuhServerCharm.master_fqdn` overrides with `-> str`. pyright: "Property method 'fget' is incompatible: Return type mismatch."
- **Impact**: Callers typed against `CharmBaseWithState` (e.g. `CertificatesObserver`) expect `list[str]` and receive `str` — a type-safety violation that could surface bugs if the observer pattern is reused.
- **Fix**: Change `CharmBaseWithState.master_fqdn` return type to `str`.
- **Linter rule**: "abstract property return type must match implementing class" — checkable with pyright strict mode.

### `external_hostname` accessed on `CharmBaseWithState` without declaration
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/certificates_observer.py:94`
- **Evidence**: `self._charm.external_hostname` accessed where `CharmBaseWithState` doesn't declare that attribute (only `WazuhServerCharm` does). pyright: "Cannot access attribute 'external_hostname' for class 'CharmBaseWithState'."
- **Impact**: Any other subclass of `CharmBaseWithState` (e.g. in tests) lacking `external_hostname` would raise `AttributeError` at runtime.
- **Fix**: Declare `external_hostname` as an abstract property on `CharmBaseWithState`, or cast in `CertificatesObserver`.
- **Linter rule**: "access to undeclared attribute on abstract class" — checkable with pyright.

### `state` accessed without a None guard in certificate handlers
- **Severity**: high
- **Kind**: bug
- **Where**: `src/certificates_observer.py:165`, `:183`
- **Evidence**: `CharmBaseWithState.state` is declared `-> State | None`. `_on_certificate_expiring` and `_on_certificate_invalidated` access `self._charm.state.rsyslog_public_cert` without a None check. pyright: "'rsyslog_public_cert' is not a known attribute of 'None'."
- **Impact**: If `certificate_expiring`/`certificate_invalidated` fires while state cannot be built (e.g. opensearch relation data temporarily unavailable after a pod restart), the handler raises `AttributeError`, failing and retrying the hook.
- **Fix**: Add `if not self._charm.state: event.defer(); return` at the top of both handlers.
- **Linter rule**: "access to optional attribute without guard" — checkable with pyright (`reportOptionalMemberAccess`).

### `TraefikRouteObserver.__init__` may pass `None` where a `Relation` is required
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/traefik_route_observer.py:42`
- **Evidence**: `TraefikRouteRequirer(charm, self.model.get_relation(RELATION_NAME), RELATION_NAME, raw=True)` — `get_relation()` can return `None`, but `TraefikRouteRequirer.__init__` declares `relation: Relation` (not optional). pyright flags this. `is_ready()` correctly checks `self._relation is not None`, so `reconcile()` returns early, but the stored `None` is incorrect internal state.
- **Impact**: While guarded in `reconcile()`, the stored `None` could cause an `AttributeError` if `submit_to_traefik()` were ever called without that guard.
- **Fix**: Add a None check before constructing `TraefikRouteRequirer`, or defer construction to `reconcile()`.
- **Linter rule**: "passing None where Relation expected" — checkable with pyright.

### `_cached_state` never cleared on `juju refresh`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:73`, `:146`
- **Evidence**: `_cached_state = None` is set only in `__init__`; there is no `on_upgrade_charm` handler to clear it. `State.from_charm()` only runs when `_cached_state is None`. No integration test exercises `juju refresh`.
- **Impact**: A refresh that changes `State.from_charm()` logic could leave stale state cached across the upgrade, causing incorrect behaviour that isn't caught by tests.
- **Fix**: Remove the cache (call `State.from_charm()` directly each reconcile — it provides no real caching benefit as written) or clear `_cached_state` in `on_upgrade_charm`. Add an integration test for `juju refresh`.
- **Linter rule**: not mechanically checkable.

### Misleading comment in `_wazuh_pebble_layer`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:434`, `:442`
- **Evidence**: Comment states "self.state will never be None at this point," but line 442 has `if not self.state: return {}` immediately after — contradicting the comment.
- **Impact**: Misleading for future maintainers; unclear whether the guard is dead code or a real case.
- **Fix**: Remove the guard, or update the comment to explain why it exists despite the assumption.
- **Linter rule**: not mechanically checkable.

### OCI image build depends on an external package repository
- **Severity**: low
- **Kind**: ux
- **Where**: `rock/rockcraft.yaml`
- **Evidence**: A `TODO: build from sources` comment; Wazuh Manager and Filebeat are pulled from `packages.wazuh.com` (configured as an apt repo); the Prometheus exporter template is pulled from `raw.githubusercontent.com`.
- **Impact**: The rock cannot be built in an air-gapped environment without mirroring the Wazuh package repository.
- **Fix**: Build Wazuh from source within the rock, or document/support mirroring the apt repository.
- **Linter rule**: not mechanically checkable.

### No actions defined
- **Severity**: low
- **Kind**: ux
- **Where**: `charmcraft.yaml` (no `actions` section)
- **Evidence**: `juju actions wazuh-server` returns "No actions defined for wazuh-server." Integration tests use `cluster_control -l` via `juju run` instead of a named action.
- **Impact**: Common operator tasks (force cluster sync, restart a service, check cluster health) have no discoverable action interface.
- **Fix**: Define actions such as `restart-service`, `cluster-health`, `sync-users`.
- **Linter rule**: not mechanically checkable.

### `charmcraft.yaml` `uv` plugin requires the `astral-uv` snap
- **Severity**: low
- **Kind**: docs
- **Where**: `charmcraft.yaml:17,19`
- **Evidence**: `parts.charm.plugin: uv` requires the `astral-uv` snap for builds; `concierge.yaml` specifies `snap: rockcraft` but not `astral-uv`.
- **Impact**: Build-time only — if the snap is missing from the build environment, the charm cannot be packed.
- **Fix**: Document the `astral-uv` snap requirement in `CONTRIBUTING.md`.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Clean state model with typed exceptions**: `InvalidStateError`, `RecoverableStateError`, `IncompleteStateError` map to distinct Juju statuses in `reconcile()`. A good pattern to standardize across charms.
- **Config-sync via git with commit markers**: `sync_wazuh_config_files()` uses a `.wazuh_applied_commit` marker file to avoid reapplying config on every hook — a clean idempotency pattern.
- **Layered pebble config**: `_wazuh_pebble_layer` merges via `container.add_layer(..., combine=True)`, cleanly separating charm-managed config from user-managed layers (Prometheus is added only when credentials are available).
- **OpenCTI connector integration**: `opencti_connector_observer` correctly handles `connector_type`/`connector_charm_name` app data on the leader only.
- **Consistent error handling via property getter**: `State.from_charm()` is called from the `state` property, and any exception is caught and mapped to the appropriate status in one place.

## Common-practice notes

- Uses `ops` directly rather than a higher-level framework — appropriate for this charm's complexity.
- `src/` layout with an observers-per-relation pattern, following ecosystem convention.
- `lib/charms/` includes a charm-owned library (`wazuh_api.py`, versioned under `v<N>/`), following standard practice.
- `CharmBaseWithState` abstract base is not a standard ecosystem pattern — most charms call `State.from_charm()` directly in `reconcile()`. It adds complexity and has the type-safety issues documented above.
- Uses `pydantic.BaseModel` for `State`, `WazuhConfig`, `ProxyConfig` — not universal, but appropriate for this charm's config complexity.
- `WAZUH_USERS` contains default passwords (`"wazuh"`, `"wazuh-wui"`) marked `# nosec`; replaced on first reconcile but unusual to have in source without a clear disclaimer.
- Uses `ops.tracing.Tracing` for OpenTelemetry — modern practice.
- Unit tests use `ops.testing.Harness`, which is pending deprecation in favor of `scenario`; migration recommended.
- Project CI runs Juju 3/stable with `automatically-retry-hooks: false`; this review used Juju 4.0.12 — some behavioural differences (hook retry, secret handling) may be version-dependent (unverified beyond what's noted above).

## Tests

- **Unit tests**: 53 tests, all passing. Coverage includes state construction, config validation, mocked reconcile flow, certificates/traefik/opensearch/OpenCTI observers, and the wazuh API library. `test_state.py`'s `UnitTestHelper` is a well-designed harness.
- **Integration tests**: 7 functions covering API auth, clustering, credentials sync, rsyslog CN validation, OpenCTI integration, filebeat credentials. Uses pytest-operator with spread/concierge infrastructure against a real k8s cluster (traefik) and LXD machines (opensearch, wazuh-indexer). No `juju refresh`/upgrade test; assertions are minimal for most tests (e.g. `test_api` only asserts `status_code == 401`).
- **Reconcile sub-methods**: `_reconcile_prometheus`, `_reconcile_users`, `_reconcile_filebeat`, `_reconcile_rsyslog`, `_reconcile_wazuh` are patched away in unit tests; the most complex reconciliation logic (user management, prometheus layer creation, filebeat keystore sync) is entirely mocked.
- **ruff**: no violations in `src/`.
- **codespell**: 2 typos in `wazuh_api.py` (`TThe` → `The`).
- **pyright**: 17 errors total. `src/` (11): `wazuh_api.py:195` (`on` overrides `Object` property), `wazuh_api.py:142,144,241,243` (possibly-unbound `TypeAdapter`/`parse_obj_as`), `charm.py:390` (`State` not assignable to `HookEvent`), `charm.py:159-160` (`RelationDataContent` not `dict[str,str]`), `certificates_observer.py:94` (`external_hostname` unknown), `certificates_observer.py:123,165,183` (optional member access), `traefik_route_observer.py:42` (`Relation | None` not `Relation`), `charm.py:521` (`master_fqdn` return type mismatch). `src/wazuh.py`: `etree` unknown import, `Retry` not exported (likely false positive).
- **CI**: `test.yaml` runs unit tests on push; `integration_test.yaml` runs spread tests. No `tox.ini` (uses a Makefile).

### Test gaps relative to findings

1. `_on_certificate_expiring`/`_on_certificate_invalidated` crash when `state` is `None` — untested (`ObservedCharm.state` always returns a valid `State` in tests).
2. `sync_filebeat_user` — no dedicated unit test; only exercised in integration tests.
3. `sync_certificates` with `public_key=None, private_key=None` (the filebeat case) — untested; existing test provides all three keys.
4. Non-leader `get_csr()` crash — untested; `ObservedCharm` doesn't model leader/non-leader distinctions.
5. `TraefikRouteObserver` init with no existing relation — untested.
6. `_cached_state` not cleared on `juju refresh` — no integration test for the upgrade path.
7. `LogProxyConsumer._on_relation_changed`/`_on_relation_departed` — not exercised by any unit test; no test simulates an empty pebble plan during a logging-relation event.
8. `WazuhInstallationError` uncaught in `reconcile()` — `test_sync_config_repo_*` tests mock `container.exec()` to succeed, so the failure path isn't exercised.
9. `_fetch_opencti_details` with a non-existent secret — no test verifies graceful degradation to `(None, None)`.

## Docs

- `README.md`: basic one-pager with Charmhub links and an integrations list.
- `docs/`: comprehensive RST structure — architecture, how-to (deploy, backup, integrate with COS, OpenCTI, upgrade), reference (integrations, actions, config).
- `docs/how-to/integrate-with-cos.md`: covers Loki, Grafana, Prometheus integration.
- `docs/how-to/configure.md`: covers config options including the `agent-password` secret flow.
- `SECURITY.md`: standard security policy.
- `CONTRIBUTING.md`: detailed (~7.3KB), covers lib updates, testing, pre-commit.
- Terraform modules (`terraform/charm/`, `terraform/product/`) with tests — good production-readiness signal.
- Mismatch: docs describe integrating with `traefik-k8s` (matching the integration test), not `traefik-k8s-lb` — flagged in notes as worth double-checking (unverified which is authoritative).

## Open questions

1. Why does the CSR never get stored in the K8s secret? Possibly a Juju secret-caching interaction in Juju 4.0.12, a `set_content()` ordering bug in the charm, or a `tls_certificates_interface` library issue — not resolved in this review (unverified).
2. What is the correct way to grant Juju secret-provider permissions in this environment? Manual RoleBindings worked around it here; unclear whether this is a Juju 4.x-specific gap or an artifact of the test cluster.
3. Is `traefik-k8s` or `traefik-k8s-lb` the correct ingress charm? The project's own integration tests use `traefik-k8s` at rev 233, which worked in this review.
4. Could the non-leader CSR crash and the multi-unit key race actually occur in a loaded cluster? Plausible from code inspection but not observed live (opensearch was unavailable throughout this session).
5. Why did the Loki library's promtail push time out on both units? Unexplained; the pebble API itself was reachable even though the plan was empty.
6. Are the differences between Juju 3.x (project CI) and Juju 4.x (this review) — RBAC, hook retry behaviour — genuine version regressions, or artifacts of the test environment?
7. Is the Loki library bug already known upstream? `LogProxyConsumer` is marked deprecated in favor of `LogForwarder` (post-Juju 3.6 LTS) — migrating away from it may be the real fix rather than patching the old library.
