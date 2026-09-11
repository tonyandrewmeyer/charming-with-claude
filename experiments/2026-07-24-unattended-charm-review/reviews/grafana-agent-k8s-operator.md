# grafana-agent-k8s

A mature, feature-rich telemetry collection charm that serves as the single integration point for the Canonical Observability Stack (metrics, logs, traces, dashboards, TLS). It works for its core single-unit use case and has clean static analysis (0 ruff, 0 pyright errors), but the codebase is carrying real debt: a 1,289-line monolithic base class, a publicly announced end-of-life, and two serious bugs found in live testing. A maintainer should first fix the non-leader crash in `publish_receivers()` — it makes multi-unit deployments unusable — and then wire up TLS cleanup on certificate-relation removal, which currently leaves stale certs live indefinitely.

| | |
|---|---|
| Repo | canonical/grafana-agent-k8s-operator @ `4e17d01` (2026-07-13) |
| Charms | grafana-agent-k8s, prometheus-tester, loki-tester |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), grafana-agent-k8s from 2/edge rev 221; also from 2/stable rev 211 upgraded to 2/edge rev 221; Juju 4 deploy attempted on concierge-k8s-4 but failed due to broken controller (no modeloperator pods) |
| Reviewed | 2026-07-25 |

## What it does

Grafana Agent consolidates metrics, logs, and traces from multiple charms and forwards them to observability backends (Prometheus, Loki, Tempo, or Grafana Cloud). Charms relate to grafana-agent-k8s instead of to each backend individually. It supports:

- **Metrics**: scrape targets via `metrics-endpoint` (prometheus_scrape), forward via `send-remote-write` (prometheus_remote_write) or Grafana Cloud
- **Logs**: receive via `logging-provider` (loki_push_api), forward via `logging-consumer` or Grafana Cloud
- **Tracing**: receive via `tracing-provider`, forward via `tracing` or Grafana Cloud
- **Dashboards**: receive via `grafana-dashboards-consumer`, forward via `grafana-dashboards-provider`
- **TLS**: certificate management via `certificates` (tls-certificates) and `receive-ca-cert` (certificate_transfer)
- **Self-monitoring**: the agent scrapes its own metrics

The charm enforces a "mandatory relation pairs" pattern: if an incoming relation is joined, at least one corresponding outgoing relation must also be present, or the charm blocks.

## Deployment log

### Juju 3.6 — full-stack deploy with refresh (rv-ga-v3, concierge-k8s-3)
```bash
juju add-model rv-ga-v3 --controller concierge-k8s-3
juju deploy grafana-agent-k8s --channel 2/stable --trust   # rev 211
juju deploy prometheus-k8s --channel 2/stable --trust
juju deploy loki-k8s --channel 2/stable --trust
juju deploy traefik-k8s --channel stable --trust            # provides metrics-endpoint
juju deploy self-signed-certificates --channel edge --trust

# Establish outgoing relations first
juju integrate grafana-agent-k8s:send-remote-write prometheus-k8s:receive-remote-write
juju integrate grafana-agent-k8s:logging-consumer loki-k8s:logging
juju integrate grafana-agent-k8s:certificates self-signed-certificates:certificates
# Charm blocks: "Missing incoming ('requires') relation: metrics-endpoint|..." — correct

# Add incoming relation → charm goes active
juju integrate grafana-agent-k8s:metrics-endpoint traefik-k8s:metrics-endpoint
# Status: active, "grafana-dashboards-provider: off, tracing: off"

# Test mandatory relation pair enforcement: remove outgoing while incoming exists
juju remove-relation grafana-agent-k8s:send-remote-write prometheus-k8s:receive-remote-write
# Status: blocked, "Missing ['grafana-cloud-config']|['send-remote-write'] for metrics-endpoint" — correct
# Re-add → recovers to active within 10s
juju integrate grafana-agent-k8s:send-remote-write prometheus-k8s:receive-remote-write
# Status: active — recovered

# Refresh from 2/stable (rev 211) to 2/edge (rev 221)
juju refresh grafana-agent-k8s --channel 2/edge
# Pod recreated, new IP, ~90s total downtime, recovered to active cleanly

# Remove TLS relation — config NOT updated (bug, confirmed on rev 221)
juju remove-relation grafana-agent-k8s:certificates self-signed-certificates:certificates
# Pebble command still has: -server.http.enable-tls -server.grpc.enable-tls
# TLS files still on disk at /tmp/agent/grafana-agent.{pem,key}
# /etc/grafana-agent.yaml still has TLS config blocks
```

### Juju 3.6 — scale-up to 2 units (rv-ga-deep2, concierge-k8s-3)
```bash
juju scale-application grafana-agent-k8s 2
# Unit 1 enters error state: hook failed: "config-changed"
# Root cause: _update_tracing_provider -> publish_receivers -> RuntimeError("only leader can do this")
# Unit 1 is NOT the leader, but publish_receivers requires leader
# Same error retried on every config-changed — unit stuck in error loop
# Must be resolved with juju resolve, but re-triggers immediately
# Charm app status flipped to error; non-leader units are broken by design
```

### Juju 3.6 — TLS removal confirmation (rv-ga-deep2, concierge-k8s-3)
```bash
juju integrate grafana-agent-k8s:certificates self-signed-certificates:certificates
# TLS established, verified via kubectl exec
juju remove-relation grafana-agent-k8s:certificates self-signed-certificates:certificates
# certificates-relation-broken fired at 15:40:19 and 15:46:07 (multiple attempts)
# Neither triggered _update_config
# Pebble command persists: -server.http.enable-tls -server.grpc.enable-tls
# TLS cert files persist: /tmp/agent/grafana-agent.{pem,key} (1674+1402 bytes)
# Config file /etc/grafana-agent.yaml still has http_tls_config and grpc_tls_config blocks
```

### Config injection tests
```bash
juju config grafana-agent-k8s cpu="bad_cpu_value"
# Shows: "Failed obtaining resource limit spec: Invalid limits spec: {'cpu': 'bad_cpu_value', ...}"
# but this status is immediately overwritten by the mandatory relations check
# Result: operator sees "Missing incoming..." instead of the actual error

juju config grafana-agent-k8s memory="not_a_valid_memory"
# Same pattern: error appears briefly then replaced

juju config grafana-agent-k8s extra_alert_labels="invalid"
# Accepted silently, returns {} — no operator feedback

juju config grafana-agent-k8s tracing_sample_rate_workload=150.0
# Accepted without validation — charm relies on agent binary to normalise
```

### Juju 4.x (concierge-k8s-4, Juju 4.0.5) — FAILED, not a charm issue
```bash
juju add-model rv-ga-j4 --controller concierge-k8s-4
juju deploy grafana-agent-k8s --channel 2/edge --trust
# All units stuck at "allocating" / "installing agent" indefinitely
# kubectl shows empty namespace — no modeloperator pod created
# Root cause: Juju 4 controller broken (no modeloperators for any rv-* model)
# Also: 2 previous models stuck in "destroying" state for 47+ minutes
```

## Observed behaviour

### Full-stack integration (Juju 3.6, rv-ga-v3)
Deployed grafana-agent-k8s + traefik-k8s (incoming metrics-endpoint) + prometheus-k8s (remote-write) + loki-k8s (logging) + self-signed-certificates (TLS). The charm correctly:
- Generated scrape configs for traefik-k8s at port 8082 with proper Juju topology labels
- Configured remote_write to Prometheus and loki_push_api to Loki
- Established TLS on HTTP and gRPC server endpoints
- Enforced mandatory relation pairs (blocked with actionable message when `send-remote-write` removed, recovered when re-added)
- Weathered a `juju refresh` from 2/stable rev 211 to 2/edge rev 221 (~90s recovery)

### Multi-unit failure (Juju 3.6, rv-ga-deep2)
Scaling from 1 to 2 units immediately broke: the non-leader unit crashed in `_update_tracing_provider -> publish_receivers` with `RuntimeError("only leader can do this")` at `tracing.py:683`. The hook retried on every subsequent config-changed, creating an infinite error loop. The same call path exists in `_on_upgrade_charm` (line 425) and `_on_config_changed`/`_on_cloud_config_available` (lines 442, 453). Consequences observed:
- Multi-unit deployments are broken since tracing was added
- Upgrades on multi-unit deployments will crash non-leader units
- The issue also blocks clean scale-down (config-changed fires on the departing unit before removal)

### Container internals (single unit, active)
- **Pebble plan**: single service `agent` with command `/bin/agent -config.file=/etc/grafana-agent.yaml -server.http.enable-tls -server.grpc.enable-tls`
- **Config file**: `/etc/grafana-agent.yaml` — correctly generated with server TLS config, integration self-monitoring relabel_configs, and empty metrics/logs/traces sections when no relevant relations exist
- **TLS files**: `/tmp/agent/grafana-agent.pem` (1402 bytes), `/tmp/agent/grafana-agent.key` (1674 bytes), owned by root, 644 permissions
- **Resource usage**: 96Mi memory, 3m CPU at idle (`kubectl top pod`)
- **Workload version**: 0.40.4 correctly reported in `juju status`

### Timing
- **Deploy to blocked**: ~60 seconds
- **Pebble ready hook**: ~2 seconds after container start
- **Config-changed hook**: ~2-3 seconds (observed via status-log timestamps)
- **Workload restart after kill**: Pebble auto-restarted within 1 second (kill and restart both observed at 03:09 UTC)

### Config-change behaviour
- The `config == old_config` check in `_update_config`, combined with `is_command_changed()`, correctly avoids unnecessary workload restarts
- Setting `tls_insecure_skip_verify=true` triggered a config-changed hook, which triggered `_update_config` -> `_update_certs` -> the TLS files were re-pushed even though the TLS config itself hadn't changed. `_update_certs` is called unconditionally inside `_update_config`, before the config-equality comparison, so certs are rewritten on every hook regardless of whether they changed
- A single `juju config` change triggered exactly one config-changed hook (expected)

### Failure injection
- **Kill workload process**: Pebble auto-restarted within ~1-2s; no hook fired; charm did not need to intervene
- **Remove TLS relation (confirmed on rev 211 and rev 221)**: `certificates-relation-broken` fired but no handler was registered for it. TLS config, pebble command, and TLS files persisted indefinitely
- **Remove outgoing relation while incoming exists**: charm correctly went to blocked with `"Missing ['grafana-cloud-config']|['send-remote-write'] for metrics-endpoint"`; recovered cleanly when relation was re-added
- **Scale up to 2 units**: non-leader unit immediately entered an error loop (see multi-unit failure above)
- **Invalid CPU/memory config**: error appeared briefly in status, then overwritten by the mandatory relations check
- **Invalid `extra_alert_labels`**: silently accepted, returns `{}`
- **Out-of-range tracing sample rate (150.0)**: accepted without validation

## Findings

### Non-leader units crash in `publish_receivers` — multi-unit deployments broken
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/grafana_agent.py:373` (`_update_tracing_provider`) calls `publish_receivers()`, which checks leadership at `lib/charms/tempo_coordinator_k8s/v0/tracing.py:683`
- **Evidence**: Scaling to 2 units on rv-ga-deep2, the non-leader unit immediately entered error state with `RuntimeError("only leader can do this")`. Call chain: `_on_config_changed:442` -> `_update_tracing_provider:373` -> `publish_receivers:683` -> raises. The same call path exists in `_on_upgrade_charm:425` and `_on_cloud_config_available:453`. The unit retries on every config-changed and cannot recover; `juju resolve` just re-triggers the error. Upstream issue #366 is open for this.
- **Impact**: Multi-unit deployments cannot be used. Any scale-up or upgrade in a multi-unit context causes non-leader units to enter a restart loop, flipping app-level status to error and breaking monitoring for all units.
- **Fix**: Guard `publish_receivers()` with `if self.unit.is_leader()` in `_update_tracing_provider`, or push the leadership check into the caller. All three call sites (`_on_config_changed`, `_on_upgrade_charm`, `_on_cloud_config_available`) need the guard.
- **Linter rule**: if a library method raises `RuntimeError("only leader ...")`, flag callers that don't check `unit.is_leader()` first — mechanically checkable.

### TLS configuration not removed when certificates relation is removed
- **Severity**: high
- **Kind**: bug
- **Where**: `src/grafana_agent.py:285` (event handler registration); `lib/charms/tls_certificates_interface/v4/tls_certificates.py:1685-1689` (library limitation)
- **Evidence**: The charm only observes `self._cert_requirer.on.certificate_available` (`grafana_agent.py:285`). `TLSCertificatesRequiresV4`'s `CertificatesRequirerCharmEvents` class exposes only `certificate_available` — no `certificate_expired` or `certificate_revoked` event exists at all (`tls_certificates.py:1685-1689`). Confirmed in two separate deployments: after `juju remove-relation`, `certificates-relation-broken` fired but no handler called `_update_config()`. `_update_certs` (line 1205) has a correct else-branch that deletes TLS files when `_tls_config` returns `None`, and `_generate_config` (line 865) correctly omits TLS blocks when `_tls_available` is `False` — but neither is ever reached because `_update_config` is never invoked on relation removal.
- **Impact**: Grafana Agent continues serving TLS with stale certificates after the TLS provider is removed — a security issue. Existing cleanup code is correct but unreachable.
- **Fix**: Observe `self.on["certificates"].relation_broken` and call `self._update_config()` from that handler, since the library provides no removal event of its own.
- **Linter rule**: if a charm observes `certificate_available`, it must also observe `relation_broken` on the certificates endpoint (or an equivalent library removal event) — mechanically checkable.

### K8s resource patch failure status overwritten by mandatory relations check
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/grafana_agent.py:741,756` (`_update_config` clearing status) and `src/grafana_agent.py:648-650` (`_on_k8s_patch_failed`)
- **Evidence**: `_on_k8s_patch_failed` sets `self.status.update_config = BlockedStatus(...)`. `_update_config` (from `_on_config_changed`) then sets `self.status.update_config = None` on success, clearing the K8s patch failure — both share the same `CompoundStatus.update_config` field. Observed: `cpu="invalid_cpu_value"` briefly showed the K8s error, then it was replaced by the mandatory relations message.
- **Impact**: An operator who sets an invalid CPU/memory value sees the real error flash and disappear, replaced by an unrelated relations message. They may never learn their resource config is invalid.
- **Fix**: Give `CompoundStatus` a separate field for K8s resource patch failures (e.g. `k8s_resource_patch`), or use a priority-ordered status list.
- **Linter rule**: not established (not mechanically checkable without semantic analysis).

### TLS relation removal does not trigger config regeneration (event-wiring gap)
- **Severity**: high
- **Kind**: bug
- **Where**: `src/grafana_agent.py:285` — only `certificate_available` is observed; no `certificate_expired` and no `relation_broken` on `certificates`
- **Evidence**: Same root cause as the TLS-cleanup finding above; called out separately in the draft because it's the missing event-wiring half of the fix rather than the config-generation logic itself.
- **Impact**: Stale TLS configuration persists indefinitely after relation removal.
- **Fix**: Observe `self.on["certificates"].relation_broken` (and `certificate_expired` if the library ever adds it), both calling `_update_config`.
- **Linter rule**: same as the TLS-cleanup finding above.

### `_update_certs` called unconditionally before config comparison
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/grafana_agent.py:727,737` (`_update_config`)
- **Evidence**: `_update_config` calls `self._update_certs()` (line 727) before the `config == old_config` comparison (line 737). `_update_certs` pushes TLS files to the workload container via Pebble; `kubectl logs` showed repeated `POST /v1/files` calls for the same files on every config-changed hook, even when nothing changed.
- **Impact**: Minor overhead per hook (three unnecessary file pushes), and a "do work then check if it was needed" code smell that recurs elsewhere in the base class.
- **Fix**: Move `_update_certs()` inside the `if config != old_config or self.is_command_changed()` block, or add a dedicated cert-changed check.
- **Linter rule**: flag any `write_file`/`push` call that appears before a `config == old_config` comparison — mechanically checkable.

### `update_dashboards` crashes if dashboard title is `None`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/grafana_agent.py:641`
- **Evidence**: `title = dash.get("title").replace(" ", "_").replace("/", "_").lower()` — `dash.get("title")` defaults to `None`, and calling `.replace()` on `None` raises `AttributeError`.
- **Impact**: A malformed dashboard entry from a related charm crashes the dashboard update handler, potentially leaving the charm in error state and breaking dashboard forwarding for all related charms.
- **Fix**: Use `dash.get("title", "")`, or guard with `if not dash.get("title"): continue`.
- **Linter rule**: flag `.get()` without a default where the result is immediately chained to a method call — mechanically checkable.

### `key_value_pair_string_to_dict` silently swallows malformed input
- **Severity**: low
- **Kind**: ux
- **Where**: `src/grafana_agent.py:72-101` (definition); call sites at `src/grafana_agent.py:209-211,217,227`
- **Evidence**: The function logs errors for invalid pairs but returns whatever it could parse; setting `extra_alert_labels="invalid"` returns `{}` with no operator-visible error. It also splits on `:` before `=`, so a value containing `:` (e.g. `"url=http://example.com:8080"`) would be split incorrectly.
- **Impact**: An operator who misconfigures `extra_alert_labels` gets no feedback; labels are silently dropped.
- **Fix**: Split on `=` first, or raise/surface a validation error for unparseable input.
- **Linter rule**: not established (not mechanically checkable).

### Dead code: second `is_ready` check in `_update_status`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/grafana_agent.py:700-702`
- **Evidence**: Lines 673-675 check `if not self.is_ready` and return early. Lines 700-702 repeat the same check, which can never be reached.
- **Impact**: Confusing to readers; suggests leftover code from a refactor.
- **Fix**: Remove the second check.
- **Linter rule**: unreachable code after an early return — mechanically checkable via control-flow analysis.

### Terraform channel validation requires `dev/` track
- **Severity**: medium
- **Kind**: bug
- **Where**: `terraform/variables.tf:10-12`
- **Evidence**: `validation { condition = startswith(var.channel, "dev/") }` restricts the module to `dev/edge`, `dev/stable`, etc. It cannot deploy the production tracks (`2/stable`, `2/edge`, `1/stable`). Added in commit `5699d35` ("feat(terraform): add channel validation and split outputs"); appears to be a leftover from development that was never generalised.
- **Impact**: Operators using the Terraform module cannot deploy the production version of the charm.
- **Fix**: Change the validation to accept any published track, or match the actual production tracks.
- **Linter rule**: Terraform channel validation should match published charm tracks — mechanically checkable given access to Charmhub metadata.

### `_reload_config` uses HTTP even when TLS is enabled
- **Severity**: low
- **Kind**: bug
- **Where**: `src/grafana_agent.py:1247`
- **Evidence**: `url = "http://localhost/-/reload"` is hardcoded. When TLS is enabled (`-server.http.enable-tls`), the reload endpoint should be `https://`. The charm has a FIXME comment referencing issue #19; the method is currently unused (the charm calls `restart()` instead, per the FIXME at line 751).
- **Impact**: If someone switches to `_reload_config` for a faster reload path, it will fail silently under TLS.
- **Fix**: Fix the URL to use HTTPS when TLS is enabled, or remove the unused method.
- **Linter rule**: flag a hardcoded `http://` endpoint URL in code paths that also enable TLS — mechanically checkable.

### Integration test `test_kubectl_delete_pod` marked `xfail`
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/test_kubectl_delete.py:26`
- **Evidence**: `@pytest.mark.xfail` — the test never validates pod-recovery behaviour. Open issue #421 documents that the agent can get stuck in a restart loop when WAL processing takes too long after a pod restart.
- **Impact**: Resilience to pod deletion is untested; the xfail masks a real failure scenario.
- **Fix**: Investigate the underlying WAL restart-loop issue and fix it, or replace the test with a more targeted one, then remove the xfail marker.
- **Linter rule**: flag integration tests carrying an `xfail` marker for review — mechanically checkable.

### Integration test `test_upgrade_charm` also marked `xfail`
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/test_upgrade_charm.py:17`
- **Evidence**: `@pytest.mark.xfail` on `test_deploy_from_edge_and_upgrade_from_local_path`, which deploys from edge and refreshes with a local charm.
- **Impact**: Upgrade regressions — including ones from the ongoing base-class refactor (issue #305) — are invisible to CI.
- **Fix**: Investigate and fix the underlying issue, then remove the xfail marker.
- **Linter rule**: same as the `test_kubectl_delete_pod` finding above.

## Worth copying

### Centralised status setting with `CompoundStatus`
`src/grafana_agent.py:109-114` — the `CompoundStatus` dataclass and `_update_status` method centralise all status decisions in one place, with an explicit precedence (ready -> config error -> validation error -> mandatory relations -> active), instead of scattered `self.unit.status = ...` assignments.

### Config comparison before restart
`src/grafana_agent.py:731-740` — the charm compares the newly generated config against the existing file, and `is_command_changed()` compares the pebble command, before deciding whether to restart the workload. This avoids unnecessary restarts and is logged clearly (`"no change in config; leaving as-is"`).

### `MandatoryRelationPairs` from `cosl`
`src/grafana_agent.py:707-711` — using `cosl.MandatoryRelationPairs` to enforce that incoming relations have corresponding outgoing relations is a good, declarative pattern (`src/charm.py:39-55`).

### Self-monitoring integration with topology labels
`src/grafana_agent.py:907-967` — the agent scrapes itself via the `integrations.agent` config block, injecting Juju topology labels via `relabel_configs`, with a unique `juju_{model}_{uuid}_{app}_self-monitoring` job name. A well-established COS pattern.

### `@trace_charm` decorator with `extra_types`
`src/charm.py:28-36` — the charm uses `trace_charm` with `extra_types` to trace calls through library objects, a good practice for distributed tracing of charm operations.

## Common-practice notes

### Follows convention
- **charmcraft.yaml layout**: standard for COS k8s charms — `type: charm`, `assumes: [k8s-api]`, containers with OCI resources, `parts` with the `uv` plugin
- **Library layout**: `lib/charms/<charm>/v<N>/` follows the standard library versioning convention
- **Terraform module**: standard layout (`main.tf`, `variables.tf`, `outputs.tf`, `README.md` with `terraform-docs` markers)
- **tox.ini**: standard COS layout with `lint`, `static`, `unit`, `scenario`, `integration` environments
- **justfile**: imports `charms.just` for shared recipes

### Drifts from convention
- **Monolithic base class**: `src/grafana_agent.py` (1,289 lines) is a shared base class originally intended for both k8s and machine charms; the machine charm has since moved to a separate repo, but the k8s charm still carries the abstraction overhead. Open issue #305 ("Untangle src/*") acknowledges this.
- **`_recurse_call_chain` pattern**: `src/grafana_agent.py:598-602` — a recursive function that resolves callables vs. properties because `MetricsEndpointConsumer.alerts` is a method call but `LokiPushApiProvider.alerts` is a property. A workaround for inconsistent library APIs that would be better fixed in the library layer.
- **Abstract method pattern**: the base class defines 12 abstract methods the k8s subclass must implement — a machine-charm-era pattern; for a k8s-only charm these could be private methods directly on the charm class.
- **TLS certs in `/tmp/agent/`**: TLS certs are written to `/tmp/agent/`, a Pebble-mounted storage volume. Open issue #216 suggests moving them to `/etc/grafana-agent/` for security hardening.

## Tests

### Unit tests: 38 passed, 0 failed
- Framework: `ops.testing.Harness` (deprecated — tests emit `PendingDeprecationWarning`)
- Coverage: 78% overall (`charm.py` 94%, `grafana_agent.py` 76%)
- Key test files: `test_relation_status.py`, `test_scrape_configuration.py`, `test_tracing_integration.py`, `test_alert_labels.py`, `test_alerts.py`, `test_cert_transfer.py`, `test_start_statuses.py`, `test_setup_statuses.py`, `test_update_status.py` — all sound
- **Notable gaps**:
  - No unit test for TLS certificate removal (`_on_certificate_available` is tested; the removal path is not)
  - No unit test for `update_dashboards` with a `None` title
  - No unit test for `key_value_pair_string_to_dict` with `:` in values
  - No unit test for the missing non-leader guard in `_update_tracing_provider`
  - No scenario tests despite a `testenv:scenario` in `tox.ini` (no `tests/scenario` directory exists)
  - Coverage gaps in `grafana_agent.py`: lines 86-93 (`key_value_pair_string_to_dict`), 381-386 (tracing receiver config), 649-650 (`_on_k8s_patch_failed`), 748-753 (config comparison), 806-817 (dashboard update), 1249-1259 (`_reload_config`)

### Integration tests
- 4 test files + 1 helper: `test_charm.py` (basic deploy, config CPU/memory, Loki relation), `test_forwards_alerts.py` (real API assertions against Prometheus and Loki for alert-rule forwarding), `test_kubectl_delete.py` (xfail), `test_upgrade_charm.py` (xfail), `grafana.py` (deploy + relation to Grafana)
- **Gaps**: no integration test for TLS certificate removal, no integration test for multi-unit behaviour; both pod-deletion and upgrade tests are xfail, leaving two key resilience scenarios untested by CI

### Lint/static
- **ruff**: 0 errors
- **pyright**: 0 errors, 0 warnings, 0 informations

## Docs

### README
- Clear description, EOL warning prominently displayed, links to Charmhub/Discourse/GitHub, example deployment commands
- Relations table is incomplete — lists only `requires: send-remote-write, metrics-endpoint, logging-consumer` and `provides: self-metrics-endpoint, grafana-dashboard, logging-provider`; missing `tracing`, `tracing-provider`, `certificates`, `receive-ca-cert`, `grafana-cloud-config`, `grafana-dashboards-consumer`, `grafana-dashboards-provider`
- `self-metrics-endpoint` no longer exists in `charmcraft.yaml` (removed in commit `ec4da00`) but is still documented

### INTEGRATING.md
- Comprehensive integration guide with code examples and a mermaid deployment diagram
- Outdated: still documents `self-metrics-endpoint`, which no longer exists

### Terraform README
- Auto-generated with `terraform-docs`, lists all inputs/outputs
- Does not document the `dev/`-only channel validation bug

### CONTRIBUTING.md
- Outdated: references `tox -e render-k8s` (no longer exists) and old `.charm`-extension charmcraft command examples; credits `@dylanstathis` and `@jose-masson` as primary authors though the codebase has since been maintained by many others

### Doc/reality mismatch
- README and INTEGRATING.md both document `self-metrics-endpoint`, which has been removed from `charmcraft.yaml`
- CONTRIBUTING.md references the non-existent `tox -e render-k8s`
- `tracing_sample_rate_charm`/`_workload`/`_error` config options are documented as normalised outside 0-100, but the charm performs no validation itself — it relies entirely on the Grafana Agent binary

## Open questions

1. **Does the TLS library emit a `certificate_expired` event on relation removal?** No — confirmed by reading `lib/charms/tls_certificates_interface/v4/tls_certificates.py:1685-1689`; `CertificatesRequirerCharmEvents` exposes only `certificate_available`. The fix must use `self.on["certificates"].relation_broken`.
2. **Is `_reload_config` intentionally dead code?** Yes — a FIXME at line 751 says to switch to it once issue #19 is fixed; two years later the method still hardcodes `http://` and is unused.
3. **Why are `test_kubectl_delete_pod` and `test_upgrade_charm` marked `xfail`?** Issue #421 (WAL restart loop) likely explains `test_kubectl_delete_pod`; the upgrade test has apparently been xfail since it was added, so upgrade regressions have never been caught by CI.
4. **Does `grafana_cloud_config` handle TLS properly?** Cloud config passes `basic_auth` credentials, and `_enhance_endpoints_with_tls` only adds `insecure_skip_verify` — there's no way to configure a proper CA for the cloud endpoint. Unverified against a real Grafana Cloud instance.
5. **Can the Juju 4 controller be recovered?** `concierge-k8s-4` had no working modeloperators during testing, and two models were stuck destroying for 47+ minutes. This blocked any Juju 4 behavioural testing beyond the failed deploy attempt; it is an infrastructure issue, not a charm issue.
