# opentelemetry-collector-integrator-operator

A workloadless charm that acts as a configuration bridge for the OpenTelemetry Collector, injecting arbitrary exporter configs (with Juju secret management) into related `otelcol` charms via the custom `external-config` relation interface. The code is clean and well-tested (100% unit coverage), but the review found several real gaps: no validation that referenced secret keys actually exist (silent integration failure on the otelcol side), a generic `BlockedStatus` message that hides the actual config error, and a `create-secret` action that hangs indefinitely on Kubernetes due to missing RBAC permissions on the charm's service account — a pre-existing bug present in both the tested local build and the currently published charmhub revision. Hooks, lifecycle events, and the upgrade path otherwise work correctly on both LXD and k8s. A maintainer should fix the k8s RBAC/action-hang issue first (it makes a core action unusable on k8s), then add secret-key validation and a relation-integration test.

| | |
|---|---|
| Repo | canonical/opentelemetry-collector-integrator-operator @ `abeacf9` (2026-07-10) |
| Charms | opentelemetry-collector-integrator |
| Substrate | machine + k8s (workloadless) |
| Deployed | yes — LXD (concierge-lxd-4, Juju 4.0.12, charmhub 3.0/edge rev 21; concierge-lxd, Juju 3.6.27, rev 21) and k8s (concierge-k8s-4, local rev 1 from `charmcraft pack`, later refreshed to charmhub rev 21) |
| Reviewed | 2026-08-25 |

## What it does

Provides the `external-config` relation interface, letting operators inject arbitrary OpenTelemetry Collector exporter configuration (YAML) into related `otelcol` charms. Credentials are managed as Juju secrets (created via the `create-secret` action, with base64 auto-decode), granted to one or more pipelines (metrics/logs/traces), and written along with the config to relation application data.

## Deployment log

### LXD — Juju 4.0.12 (concierge-lxd-4, model `rv-otelcol-lxd`, rev 21, 2026-08-25)
1. Deployed from charmhub channel `3.0/edge` (rev 21).
2. Machine provisioned (~75s cloud-init). Initial state: **blocked** — "Invalid configuration. Verify juju debug-logs" (no pipelines configured).
3. `metrics_pipeline=true` → **active** — "Pipelines: metrics configured" in <1s.
4. `create-secret name=test-api token=...` → works, secret created instantly.
5. `create-secret` with duplicate name → action fails: "Secret 'test-api' already exists".
6. `create-secret` with empty name → action fails: validation error.
7. `create-secret` with no data → action fails: "At least one key-value pair is required".
8. Invalid YAML (unclosed quote) → **blocked**, same generic message; debug log shows the YAML parse error.
9. Valid config, no pipeline enabled → **blocked** (generic message, no pipeline).
10. Config using OTEL `${secret://...}` template syntax → **blocked**. Debug log: `"Secret URI must include a key: ...file}"` (trailing `}` captured by the regex).
11. Config referencing a non-existent (but well-formed) secret → **blocked**, "Secret secret://... not found", after 2–3 hook cycles.
12. Valid config + real secret reference + `metrics_pipeline=true` → **active**.
13. Related to `opentelemetry-collector` (rev 438, beta) → relation data written (`config_yaml`, `pipelines: ["metrics"]`, confirmed via `juju show-unit`); otelcol receives and resolves the config.
14. Relation removed → `relation-broken` fires, `_reconcile` runs, charm stays **active**.
15. `juju add-unit -n 1` → non-leader unit 1 → **blocked** — "This charm is not intended to be scaled".
16. `juju remove-application --force --no-wait` → app and unit removed, machine destroyed.
17. Re-deployed fresh (unit 1 on machine 2).
18. Config with a wrong secret key (`secret://uuid/id/nonexistent-key`) → **active** on the integrator (no validation of key existence). otelcol log: `"Skipping relation: secret resolution failed - Secret key 'nonexistent-key' not found"`.
19. `juju refresh --channel 3.0/edge` → "already up-to-date" (rev 21 already latest for ubuntu@24.04).

### LXD — Juju 3.6.27 (concierge-lxd, model `rv-otel-lxd36`, rev 21, 2026-08-25)
1. Deployed from charmhub `3.0/edge` (rev 21). Machine provisioned (~90s).
2. Initial state: **blocked**, identical message to Juju 4.x.
3. Valid config + `metrics_pipeline=true logs_pipeline=true` → **active** — "Pipelines: metrics, logs configured" in <1s.
4. `create-secret name=juju36-test token=my-secret-value` → works instantly, identical to Juju 4.x.
5. All tested failure modes matched Juju 4.x behaviour exactly. No Juju-version-specific issues found.

### Kubernetes (concierge-k8s-4, model `rv-otelcol-k8s`, local rev 1 from `charmcraft pack`)
1. `charmcraft pack` → `opentelemetry-collector-integrator_ubuntu@24.04-amd64.charm` (5.6 MB).
2. `juju deploy <local-charm>` → StatefulSet created, pod running.
3. Initial state: **blocked** (no pipelines), same as LXD.
4. Valid config + `metrics_pipeline=true` → **active** in ~10s.
5. `create-secret name=k8s-test token=k8svalue` → **hangs**: secret record created, but Juju's k8s secrets backend repeatedly fails to save content (10+ attempts over 5+ minutes): `secrets "..." is forbidden: User "system:serviceaccount:rv-otelcol-k8s:juju-secret-consumer-..." cannot patch resource "secrets"`. Action never completes; charm stays active throughout.
6. Hooks observed: `leader-elected`, `config-changed` (×2), `start` — same pattern as LXD.
7. Model subsequently destroyed (cleanup from a prior session); not re-deployed this session for the initial k8s pass — see refresh/relation testing below, done in this session against a fresh deploy.

## Observed behaviour

### Status transitions (LXD 4.x, all scenarios)
| Trigger | Observed status |
|---|---|
| No config / no pipelines | blocked — "Invalid configuration. Verify juju debug-logs" |
| Invalid YAML | blocked — same generic message; debug log has the YAML parse error |
| Valid config, no pipeline | blocked — generic message, no indication that a pipeline flag is missing |
| Non-existent secret (valid URI format) | blocked — "Secret secret://... not found", after 2–3 hook cycles |
| Wrong secret key (key absent from secret) | **active** on integrator; otelcol logs "Secret key 'X' not found" and skips the relation |
| Valid config + relation | active — secret granted, config written to relation data |
| Config broken while relation active | blocked — same generic message |
| Relation removal | active — reconciler runs on `relation-broken`, no relations, config still valid |
| Non-leader unit | blocked — "This charm is not intended to be scaled" |
| `juju remove-application` | app and unit removed, machine destroyed |

### Secret key validation gap — otelcol skips relation silently
1. Integrator parses the URI format (e.g. `secret://uuid/id/nonexistent-key?render=file`) — valid.
2. `SecretURI.from_uri()` succeeds (format-only validation).
3. Integrator grants the secret to the relation — no error.
4. Integrator writes relation data with the broken URI, shows **active**.
5. otelcol fetches the secret, looks for `nonexistent-key`, raises `ValueError`.
6. otelcol logs: `"Skipping relation 4: secret resolution failed - Secret key 'nonexistent-key' not found"`.
7. The operator sees no indication of the problem on the integrator side.

### Secret grant failure — full trace (non-existent secret)
1. `config-changed` fires → `_reconcile` runs → `_grant_config_secrets` calls `model.get_secret(id=secret_uri)`.
2. `get_secret` raises `SecretNotFoundError`/`ModelError`.
3. `grant_secrets` catches it and appends `BlockedStatus(f"Failed to grant secret {secret_uri}")` to `self.statuses`.
4. `_update_relations` still runs (even with the grant failure), logging "Updated 1 relation(s) with config and secrets".
5. Second `config-changed` fires; reconciler runs again.
6. `collect-status` fires; `collect_unit_status` adds all accumulated statuses; Juju picks the highest-priority one — **blocked**.

This confirms `BlockedStatus` from a grant failure does eventually reach the operator (after ~2 hook cycles), correctly.

### Relation data written (LXD, confirmed)
```
relation-id: 4
endpoint: external-config
application-data:
  config_yaml: |
    exporters:
      otlphttp:
        endpoint: https://example.com/secure
        headers:
          Authorization: "secret://8cae7c1e-44d9-4cf5-867b-7cd7e999ef3a/edp9nkn6nc9c27ssajd0/token?render=file"
  pipelines: '["metrics"]'
```

### k8s relation integration (concierge-k8s-4, rev 21)
- `external-config-relation-created` fires correctly on relation establishment.
- `"Updated 1 relation(s) with config and secrets"` logged at 17:18:38.
- `relation.data` confirmed via `juju show-unit`: `config_yaml` and `pipelines: ["metrics"]` present.
- Consumer (`opentelemetry-collector`, rev 438) went into `error`: `hook failed: install` — it tries to install the `node-exporter` snap, which requires snapd, unavailable on k8s. Unrelated to this integration.
- `in-scope: false` in `related-units` correctly reflects the consumer's error state.
- Relation removal fires `external-config-relation-broken`; charm stays **active** (config still valid, no relations).

### Upgrade path — both substrates (concierge-k8s-4, concierge-lxd-4)
**LXD** (`juju refresh --switch opentelemetry-collector-integrator --channel 3.0/edge`, local rev 0 → charmhub rev 21):
- Hooks: `upgrade-charm` → `config-changed` (queued) → both succeed.
- Status throughout: active.
- Charm revision updated 0 → 21.

**k8s** (same refresh command, local rev 0 → charmhub rev 21):
- Hooks: `upgrade-charm` → `config-changed` (queued) → `start` (reboot detected).
- Status transition: maintenance "(upgrade-charm)" → active.
- Pod replaced (IP 10.1.0.11 → 10.1.0.93); new pod came up correctly.
- `create-secret` still hangs (same RBAC issue persists in rev 21 — no code change between revisions changes this).

### Hook activity (LXD 4.x)
- `config-changed` fires twice per `juju config` call — Juju uniter behaviour, not a charm bug.
- `collect_unit_status` fires alongside `config-changed` (both are in `all_events`).
- `relation-joined`, `relation-changed`, `relation-broken` all trigger `_reconcile`.
- `observe_events` uses `_reconcile` directly (it has an `event` parameter) — no GC concern (see cosl analysis below).

### Secret lifecycle events (via `all_events`)
cosl's `all_events` set includes `SecretChangedEvent`, `SecretRotateEvent`, `SecretRemoveEvent`, `SecretExpiredEvent`, all observed by `_reconcile`, which re-runs secret granting and relation-data writing on any secret lifecycle change. The charm does not specifically handle rotation or expiration — it simply re-grants and re-writes. If a secret is removed, `_grant_config_secrets` would try to re-grant the removed secret and fail into `BlockedStatus`.

### Install/start timing
- LXD machine provision (cloud-init): ~75–90s.
- k8s pod ready: ~10s.
- Post-config active transition: <1s on LXD, ~10s on k8s.

### No observability endpoints
The charm exposes no metrics, logs, or HTTP endpoints, no Pebble workload layer. On k8s it runs as a StatefulSet with a `container-agent` service managed by Pebble; on LXD it runs as a machine agent. No resource metrics come from the charm itself.

## Findings

### `create-secret` action hangs indefinitely on Kubernetes — RBAC root cause
- **Severity**: high
- **Kind**: bug
- **Where**: `src/secret_manager.py:125-129` (the `app.add_secret()` call) + Kubernetes RBAC
- **Evidence**: The `juju-secret-consumer-...` Role bound to the charm's service account only grants:
  ```yaml
  rules:
  - apiGroups: [""]
    resources: ["namespaces"]
    verbs: ["get", "list"]
  ```
  No permissions on `secrets`. `app.add_secret()` triggers Juju's k8s secrets backend to create a K8s Secret object using the charm's credentials, which fails: `secrets "ibg3j3t8gsiob451etj0-1" is forbidden: User "system:serviceaccount:rv-otelcol-k8s:juju-secret-consumer-..." cannot patch resource "secrets"`. Retried 10+ times over 5+ minutes; the action never completes. Confirmed on both local rev 0 and charmhub rev 21. Confirmed via `kubectl auth can-i patch secrets --as=system:serviceaccount:rv-otelcol-k8s:opentelemetry-collector-integrator -n rv-otelcol-k8s` → `no`. The charm itself never errors and stays active throughout.
- **Impact**: `create-secret` is the primary way to create secrets in this charm. On k8s it never completes — an operator would wait indefinitely for a hanging action.
- **Fix**: This is fundamentally a Juju controller/RBAC configuration issue and the charm cannot grant itself the missing permission. The charm should catch the `ModelError` raised by `app.add_secret()` in `_on_create_secret_action` and fail the action promptly with a message naming the k8s secrets backend failure, instead of hanging.
- **Linter rule**: not mechanically checkable (requires a live k8s environment to trigger).

### Integrator doesn't validate that secret keys exist — silent relation failure
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:84` (`_grant_config_secrets`) and `lib/charms/opentelemetry_collector_integrator/v0/opentelemetry_collector_integrator.py:385-401` (`SecretURI.from_uri`)
- **Evidence**: For `secret://uuid/id/nonexistent-key?render=file`, `SecretURI.from_uri()` validates only the URI format (valid) and never checks that `nonexistent-key` exists in the secret content. The integrator grants the secret and writes relation data, showing **active**. otelcol then fetches the secret, fails to find the key, and logs: `"Skipping relation 4: secret resolution failed - Secret key 'nonexistent-key' not found in secret 'secret://8cae7c1e-44d9-4cf5-867b-7cd7e999ef3a'"`. The relation is silently skipped on the otelcol side.
- **Impact**: An operator who mistypes a secret key gets a working-looking integrator status while otelcol silently ignores the config — a silent integration failure diagnosable only by reading otelcol's debug log.
- **Fix**: Before granting, fetch the secret content and verify the key exists. In `_grant_config_secrets`, after `model.get_secret(id=secret_uri)`, call `secret.get_content()` and check the key is present; raise/handle as a `BlockedStatus` if absent.
- **Linter rule**: "Charm grants secret without verifying the key exists in the secret content" — mechanically checkable if the charm calls `secret.get_content()` before `secret.grant()`.

### OTEL `${...}` template syntax in config YAML causes silent block with cryptic error
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/opentelemetry_collector_integrator/v0/opentelemetry_collector_integrator.py:260` (regex), same file line ~333 (`_parse_secret_uri`)
- **Evidence**: `_extract_secret_references`'s regex `\?[^\s"\']*` greedily captures the trailing `}` of an OTEL `${secret://...}` template. For `Authorization: "${secret://uuid/secret-id/token?render=file}"`, the regex extracts `secret://uuid/secret-id/token?render=file}` (note the trailing `}`), and `SecretURI._parse_secret_uri` fails with `"Secret URI must include a key: secret://...file}"`. Charm goes **blocked** with the generic message; confirmed live.
- **Impact**: OTEL's standard config format uses `${...}` template expansion. An operator using canonical OTEL syntax fails silently with no actionable error.
- **Fix**: Either strip trailing `}` from extracted URIs before validation, or explicitly document `${...}` as unsupported and pre-validate/reject configs containing `${secret://`.
- **Linter rule**: "Config YAML containing `${secret://` will cause silent failure" — mechanically checkable by scanning config for the pattern before processing.

### `BlockedStatus` message is too generic — operator cannot act without debug-log
- **Severity**: high
- **Kind**: ux
- **Where**: `src/charm.py:92`
- **Evidence**: `self._statuses.append(BlockedStatus("Invalid configuration. Verify juju debug-logs"))`. The full Pydantic validation error is logged at WARNING but `juju status` gives no clue which rule failed. Confirmed by injecting invalid YAML (debug log: `"Invalid YAML: while scanning a quoted scalar"`, status: generic message) and by a no-pipeline config (no clue a pipeline flag is missing).
- **Impact**: `juju status` is the primary operator interface; requiring a separate `juju debug-log` call to diagnose a blocked status slows incident response.
- **Fix**: Include the specific validation error, e.g. `BlockedStatus(f"Config error: {e}")` from the caught `ValidationError`.
- **Linter rule**: not mechanically checkable.

### No relation-integration test
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py:1-17`
- **Evidence**: The only integration test calls `juju.deploy` + `juju.wait(jubilant.all_blocked)`; it never creates a relation, never checks relation data, never checks secret granting, and never exercises `create-secret` in integration. `opentelemetry-collector` (rev 438, beta) provides `requires: external-config`, making a proper relation test possible.
- **Impact**: The charm's core value — sharing config and granting secrets to `otelcol` — is untested end to end. Regressions in relation-data writing or secret granting would go undetected.
- **Fix**: Add integration tests that deploy, relate to `opentelemetry-collector`, verify relation data contains `config_yaml`/`pipelines`, and exercise secret granting end to end.
- **Linter rule**: not mechanically checkable.

### README includes a `juju add-secret` example that cannot work
- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md` (complete workflow section)
- **Evidence**: The README's full workflow shows `juju add-secret splunk-creds token="my-splunk-token" ...` (a user-owned secret). The `create-secret` action description explicitly states "we cannot use user secrets (the app doesn't own them so cannot grant them)". Following the README example would create a secret the integrator cannot grant to otelcol; the integration would silently fail (otelcol log: "Failed to fetch secret ... not valid").
- **Impact**: Silent integration failure with no actionable error for the operator who followed the README.
- **Fix**: Remove the `juju add-secret` example; keep only the `create-secret` action workflow.
- **Linter rule**: not mechanically checkable.

### Secret grant not verified in unit test
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:201-234` (`test_secret_uris_extracted_and_granted`)
- **Evidence**: The test creates a secret and relation and asserts `assert fake_secret_uri in rel_out.local_app_data["config_yaml"]`, but never asserts `secret.grant.assert_called_once_with(relation)`. The actual `secret.grant()` call was only confirmed via otelcol debug logs in the live deployment.
- **Impact**: If `grant_secrets` were accidentally dropped from the code path, this test would still pass, and secret sharing with related charms would silently break.
- **Fix**: Mock the secret and add the `grant.assert_called_once_with(relation)` assertion; add a test for a valid-format-but-nonexistent key and assert the resulting status.
- **Linter rule**: not mechanically checkable.

### `collect_unit_status` handler never tested in unit tests
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py` (entire file); handler at `src/charm.py:130-134`
- **Evidence**: None of the 10 charm unit tests exercises `collect_unit_status`; `grep -n collect tests/unit/test_charm.py` returns nothing. The handler appends a bare `ActiveStatus()` before iterating `self._statuses`, accumulating across reconciliations. Neither behaviour is tested.
- **Impact**: The redundant bare `ActiveStatus()` and unbounded `_statuses` growth (see below) would both be caught by a test targeting this handler.
- **Fix**: Add unit tests for `ctx.on.collect_unit_status()` covering valid config (active), invalid config (blocked), and no config (blocked), checking `state_out.unit_status` and the number of statuses added.
- **Linter rule**: not mechanically checkable.

### Non-leader `BlockedStatus` not asserted in unit test
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:177-200` (`test_non_leader_does_nothing`)
- **Evidence**: The test asserts `assert not rel_out.local_app_data` but never checks `state_out.unit_status`. The message "This charm is not intended to be scaled" is never checked.
- **Impact**: Confirmed correct live on scale-up, but the test would not catch a regression in the status type or message.
- **Fix**: Add `assert isinstance(state_out.unit_status, testing.BlockedStatus)` and `assert "not intended to be scaled" in state_out.unit_status.message`.
- **Linter rule**: not mechanically checkable.

### `_statuses` list grows without bound across reconciliations
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:41`
- **Evidence**: `self._statuses: List[StatusBase] = []` is initialized once in `__init__` and never cleared; each `_reconcile` call appends. Observed: 4 config changes → 4 entries, growing further with each `collect-status`.
- **Impact**: Memory growth over a long-running charm's lifetime.
- **Fix**: Clear the list at the start of `_reconcile`: `self._statuses.clear()`.
- **Linter rule**: "Instance variable `_statuses` is never reset between reconciliations".

### `CollectStatusEvent` handler adds redundant `ActiveStatus` on every hook
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:130-132`
- **Evidence**: `_on_collect_unit_status` appends `ActiveStatus()` before iterating `self._statuses`, but `_reconcile` already adds an `ActiveStatus` there — so a second, bare `ActiveStatus()` is always appended. When a `BlockedStatus` is present, Juju's priority resolution still picks blocked correctly, but the redundant append still happens and is logged.
- **Impact**: Wastes a status slot, adds confusing log output.
- **Fix**: Remove `self._statuses.append(ActiveStatus())` from `_on_collect_unit_status`.
- **Linter rule**: "collect-status handler should not append ActiveStatus when it is already appended by the reconciler".

### Library `LIBPATCH` not bumped when publishing
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/opentelemetry_collector_integrator/v0/opentelemetry_collector_integrator.py:243`
- **Evidence**: `LIBPATCH = 1`. The tox static check for LIBPATCH increment is commented out with a TODO. The library is currently only used internally.
- **Impact**: If the library is ever published without bumping LIBPATCH, consumers get stale code.
- **Fix**: Move the library into `src/` (since it isn't published), or enable the LIBPATCH lint and keep it current.
- **Linter rule**: "LIBPATCH not incremented since initial publish" (present in `tox.ini`, currently commented out).

### Terraform targets in `charms.just` with no `terraform/` directory
- **Severity**: low
- **Kind**: docs
- **Where**: `charms.just:206-216` (imported by `justfile`)
- **Evidence**: The centralized `charms.just` template defines `terraform-docs` and `terraform-lint` targets referencing a `terraform/` directory that does not exist (`find . -name '*.tf'` returns nothing). `.tfdocs.yaml` exists with no corresponding terraform module. Running `just terraform-lint` fails.
- **Impact**: Dead infrastructure configuration; confusing to a maintainer running `just` targets.
- **Fix**: Implement a terraform module, or gate the terraform targets on `terraform/` existing (via a `charms.just` template fix upstream).
- **Linter rule**: not mechanically checkable (template-level issue).

### `base64 -w0` in README example may not be portable
- **Severity**: low
- **Kind**: docs
- **Where**: `README.md`
- **Evidence**: `base64 -w0` is GNU coreutils syntax; macOS BSD `base64` uses `-b 0` for the same effect.
- **Impact**: An operator on macOS following the README literally gets line-wrapped base64, which fails when passed to `create-secret`.
- **Fix**: Add a note: "On macOS, use `base64 -b 0` instead."
- **Linter rule**: not established.

## Worth copying

### Clean use of the cosl reconciler pattern
`src/charm.py:45` — `observe_events(self, all_events, self._reconcile)` replaces the usual hook-method mapping with a single reconciler. `_reconcile(self, event)` has a parameter, so cosl's `observe_events` uses it directly rather than via the GC-risky proxy class (confirmed by reading cosl's `reconciler.py`).

### Status precedence via `CollectStatusEvent`
`src/charm.py:130-135` — `_on_collect_unit_status` uses `event.add_status()` for each status in priority order (aside from the redundant bare `ActiveStatus()` — see Findings).

### Pydantic validation of relation data at the boundary
`lib/charms/.../opentelemetry_collector_integrator.py:295-359` — `OtelcolIntegratorProviderAppData` validates `config_yaml` (YAML parse + secret URI validation) and pipelines at the charm boundary. Good defensive pattern, though it doesn't validate secret key existence (see Findings).

### `SecretInfo` with base64 auto-decode on `create-secret`
`src/secret_manager.py:62-89` — auto-detects and decodes base64-encoded secret values on creation, with graceful fallback for non-base64 strings. Confirmed working on Juju 3.6 and 4.x.

### `SecretURI` as a reusable, testable URI parser
`lib/charms/.../opentelemetry_collector_integrator.py:192-287` — self-contained, exhaustively tested Pydantic model for parsing/validating `secret://` URIs, cleanly separated regex extraction. Note: does not validate key existence in the secret.

### Non-leader correctly blocks with an informative message
`src/charm.py:51` — `BlockedStatus("This charm is not intended to be scaled")` on non-leader, verified by scale-up test. Clear and actionable.

### Grant failure correctly reaches `BlockedStatus`
`src/secret_manager.py:168` — `self.statuses.append(BlockedStatus(msg))` on `SecretNotFoundError`. Observed working live: when a non-existent secret is referenced, the charm eventually reports blocked with the specific grant error (after 2–3 hook cycles).

### 100% code coverage
All three source files have 100% statement and branch coverage in unit tests.

### cosl `all_events` — GC-safe use confirmed
`observe_events` uses the method directly when the handler has a parameter (as `_reconcile(self, event)` does), avoiding the `_Observer` proxy class that would otherwise hold a reference to prevent GC.

## Common-practice notes

**Follows convention:**
- `src/` layout with separate modules for charm, constants, and secret management.
- `lib/charms/<name>/v<N>/` library versioning.
- `ops.CharmBase` subclass with `ops.main()` entrypoint.
- `charmcraft.yaml` with `type: charm`, actions, config options.
- `pyproject.toml` with dependency groups and tool configs.
- `tox.ini` with lint/static/unit environments using `uv run`.
- Jubilant-based integration tests (k8s in CI).
- Copyright headers on all source files.
- `justfile` using the centralized `canonical/observability` charms.just template.

**Drifts from convention:**
- Library used only internally, never published; the LIBPATCH tox static check is disabled. Should be moved to `src/` or marked internal-only.
- `provides` interface name (`external-config`) is not prefixed with the charm name (convention would be `<charm-name>-<interface>`, e.g. `otelcol-integrator-external-config`).
- Deploys as a StatefulSet on k8s using `container-agent` rather than a Pebble workload — expected/correct for workloadless k8s charms.
- No spread tests despite the `canonical/observability` CI template supporting them.
- `charms.just` terraform targets exist with no `terraform/` directory.

**Leads convention:**
- `base64` auto-decode in `SecretInfo` is a thoughtful UX improvement over bare secret storage.
- `SecretURI` Pydantic model for URI validation is a clean, reusable pattern.
- Grant failure correctly produces `BlockedStatus` (not all charms handle this).

## Tests

### Unit tests
76 tests across `test_charm.py`, `test_secret_manager.py`, `test_otelcol_integrator_lib.py`. All pass, 100% coverage:
```
Name  Stmts  Miss  Branch  BrPart  Cover
TOTAL  355     0     70      0     100%
```
Key gaps:
- `collect_unit_status` never explicitly tested (would catch the redundant `ActiveStatus` and `_statuses` growth).
- Non-leader `BlockedStatus` message not asserted.
- `secret.grant()` not verified in `test_secret_uris_extracted_and_granted` — only the relation-data URI is checked.
- The OTEL `${...}` template failure is not tested.
- Secret key existence is not validated in any unit test (only observed live).
- Secret lifecycle events (`SecretChangedEvent`, `SecretRotateEvent`, `SecretRemoveEvent`, `SecretExpiredEvent`) are not tested, though all trigger `_reconcile` via `all_events`.

### Integration tests
Single test (`test_deploy`): deploys and waits for blocked, with no assertions about relations, secrets, config, or lifecycle. Uses `jubilant.temp_model()`, so it cannot be run locally without CI credentials. `opentelemetry-collector` (rev 438, beta) on charmhub now provides `requires: external-config`, making a proper relation test possible.

### Linters
- `ruff check`: clean.
- `pyright`: 0 errors, 0 warnings.
- `codespell`: clean.

## Docs

**README.md**: Comprehensive usage guide covering deployment, secret creation, config format, secret URI syntax, pipeline options, and a full example workflow.

**Known doc issues:**
1. The `juju add-secret` complete-workflow example cannot work (user-owned secrets can't be granted by the integrator charm) — the `create-secret` action description says as much.
2. `base64 -w0` is GNU-specific.
3. Terraform targets in `charms.just` reference a non-existent `terraform/` directory.
4. No documentation of the `${...}` OTEL template syntax limitation (secret URIs must be bare, not template-wrapped).
5. No documentation of the secret-key-existence validation gap.

**CONTRIBUTING.md**: Minimal — references tox, `charmcraft pack`, and the Juju SDK docs.

**charmcraft.yaml description**: Matches README.

## Open questions

1. **OTEL template syntax**: should `${secret://...}` be supported, or explicitly documented as unsupported?
2. **Secret rotation** (repo issue #2): `create-secret` creates new secrets but doesn't notify related otelcol charms when content changes. The URI stays the same; otelcol would need `refresh=True` on fetch. The charm observes `SecretChangedEvent`/`SecretRotateEvent` via `all_events`, but since the secret is already granted, re-grant is a no-op — otelcol's own secret-watching would need to handle re-fetch. Untested here.
3. **k8s secret RBAC**: root cause confirmed — the `juju-secret-consumer-...` Role grants only `namespaces get/list`, not `secrets`. This is a Juju controller configuration issue the charm code cannot work around directly; the charm should at minimum catch the `ModelError` and fail the action instead of hanging.
4. **Upgrade path**: verified working on both LXD and k8s (local rev 0 → charmhub rev 21), same hook sequence on both substrates. No upgrade-specific automated tests exist, though live verification confirms the path is clean.
5. **Secret management actions**: no `remove-secret`, `update-secret`, or `rotate-secret` action exists. A created secret can't be updated or removed without recreating it — a functional gap if rotation is required. `SecretRotateEvent` is observed but not specifically handled.
