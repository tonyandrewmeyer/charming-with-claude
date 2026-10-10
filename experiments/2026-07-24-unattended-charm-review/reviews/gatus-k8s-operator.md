# gatus-k8s-operator

A thin, well-built Juju charm wrapping the Gatus health-check binary via the `go-framework`
extension and the `paas-charm` library. Code quality is high — clean separation, comprehensive
validation, 49 passing unit tests — but the review surfaced a real peer-relation initialization
race with no recovery path, a secret-access error that crashes the hook instead of blocking, an
`is_ready()` override that can mask peer-relation readiness, and a PaaSCharm-level bug that blocks
the charm on an integration marked `optional: true`. None of these were hit in a plain single-unit
deploy with default config; all surfaced under multi-unit scaling, removal/redeploy cycles, or
secret misconfiguration. A maintainer should first fix the peer-relation `leader-elected` gap
(finding 1) since it can leave a deployment permanently unrecoverable, then tighten exception
handling around `_create_charm_state()` (findings 2–3) since both currently turn recoverable
misconfiguration into hook failures requiring manual `resolve`.

| | |
|---|---|
| Repo | canonical/gatus-k8s-operator @ `b9dbe99` (2026-07-03) |
| Charms | gatus-k8s |
| Substrate | Kubernetes (runs on K8s via `go-framework` extension; `_context/charms.json` mislabels kind as `machine`) |
| Deployed | yes — `concierge-k8s-4` (`rv-gatus-2`, `rv-gatus-k8s`), `latest/edge` rev 14; `concierge-k8s-3` (`rv-gatus-j3`, Juju 3.6.25), `latest/edge` rev 14 |
| Reviewed | 2026-08-18 |

## What it does

Deploys the Gatus binary (v5.35.0, patched to 1-year SQL retention) on Kubernetes. The rock's
entrypoint script renders YAML config files from environment variables injected by the charm into
the Pebble layer. Supports PostgreSQL storage (`postgresql-k8s` relation), Mattermost alerting (via
Juju secret), OIDC/OAuth (`hydra` relation), metrics (`grafana-agent-k8s`), and UI customization
(charm config). All dynamic configuration flows through Pebble environment variables rather than
file templating inside the charm itself.

## Deployment log

### Round 4 — Juju 3.6 environment (`rv-gatus-j3`, concierge-k8s-3)

1. Created model `rv-gatus-j3` on `concierge-k8s-3` (Juju 3.6.25).
2. `juju deploy gatus-k8s --channel edge` — rev 14, ~2 min to `active/idle`.
3. `juju deploy postgresql-k8s --channel 14/stable` — required `juju trust --scope=cluster` for
   sufficient k8s permissions.
4. `juju deploy self-signed-certificates --channel 1/stable`.
5. Related postgresql-k8s to self-signed-certificates (auto TLS).
6. Related gatus-k8s to postgresql-k8s → `postgresql-database-database-created` fired → pebble
   plan updated with `POSTGRESQL_DB_*` env vars; `/config/storage.yaml` rendered.
7. `kubectl exec ... cat /config/storage.yaml` confirmed:
   ```
   storage:
     path: postgresql://relation_id_5:dy1x5kM6...@postgresql-k8s-primary.rv-gatus-j3.svc.cluster.local:5432/gatus-k8s
     type: postgres
   ```
8. `juju remove-relation gatus-k8s:postgresql postgresql-k8s:database` → `relation-broken` fired →
   `/config/storage.yaml` removed; gatus stays `active/idle` (reverts to in-memory storage).
9. `juju integrate gatus-k8s postgresql-k8s` → relation re-established → `storage.yaml`
   re-rendered with new relation ID (`relation_id_6:AbwN9T3Mi...`).
10. `juju config gatus-k8s ui-default-sort-by=invalid` → unit goes `blocked` with "Invalid default
    sort order. Valid values are: name, group, health." — correct, actionable message.
11. `kubectl exec ... pkill gatus` → Pebble self-healed within ~10s, service back to `active`.
12. `juju deploy hydra --channel latest/stable`.
13. `juju integrate gatus-k8s:oidc hydra:oauth` → relation established; `/config/security.yaml`
    NOT rendered (hydra blocked on missing public-route). PaaSCharm blocks gatus-k8s with "Please
    check hydra charm!" even though OIDC is `optional: true`. Workload keeps running (Pebble
    `active`).
14. `juju run gatus-k8s/0 rotate-secret-key` → action succeeded.

### Round 3 — fresh clean deploy (`rv-gatus-2`, concierge-k8s-4)

1. `juju add-model rv-gatus-2 --controller concierge-k8s-4`.
2. `juju deploy gatus-k8s --channel edge` — rev 14, ~2 min to `active/idle`.
3. Confirmed gatus running (Fiber v2.52.11, PID 40, monitoring ubuntu.com successfully).
4. `pkill gatus` → Pebble self-healed within ~5s, service `active`.
5. `juju config oidc-redirect-path="%%invalid"` → charm stayed `active` — no path-format
   validation; silently accepts malformed path, would break OIDC once hydra is related.
6. `juju config ui-dashboard-heading=<1000 A's>` → charm stayed `active`, long string written to
   `/config/ui.yaml` with no length validation.
7. `add-unit gatus-k8s` → scaled to 2 units; both `active/idle` within ~90s; unit 1 has correct
   pebble layer with `APP_SECRET_KEY` from the peer relation.
8. `juju remove-application gatus-k8s --force` → both units' `secret-storage-relation-departed`
   hooks **succeeded**, `stop`/`remove` hooks ran, all pods destroyed cleanly. No hook failure.
9. Redeployed gatus-k8s fresh to `rv-gatus-2`.
10. Deployed `grafana-agent-k8s`; `integrate gatus-k8s:metrics-endpoint grafana-agent-k8s` →
    relation data confirmed correct (`scrape_jobs`, `alert_rules`, `scrape_metadata`).
11. `juju remove-relation gatus-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint` → clean
    removal; gatus stays `active/idle`.
12. `juju add-secret mattermost-test alerts="http://example.com/webhook"` (no `default` key) →
    secret created but NOT granted to the charm.
13. `juju config mattermost-alerting="secret:fi3ff11gr7rota1hsee0"` → **`config-changed` hook
    FAILED** with exit status 1. Unit `gatus-k8s/0` went to `error` state. Debug log:
    ```
    ops.model.ModelError: ERROR "gatus-k8s/0" is not allowed to read this secret
    exceptions.SecretAccessPendingError: Waiting for access to Juju secret 'secret:fi3ff11gr7rota1hsee0':
      ERROR "gatus-k8s/0" is not allowed to read this secret
    ```
14. `juju grant-secret fi3ff11gr7rota1hsee0 gatus-k8s` → grant added with `role: view`; hook
    retried but still failed (`view` role does not permit content reading).
15. `juju config mattermost-alerting=""` → charm recovered to `active/idle`.
16. `juju run gatus-k8s/0 rotate-secret-key` → action succeeded; pebble layer briefly cleared (all
    env vars gone, `go` service `inactive`) then restored ~10s later after `restart()` completed.
    Service interruption approximately 5–10s.
17. `juju refresh gatus-k8s --channel edge` → already up-to-date.

### Round 1 (first pass, `rv-gatus-k8s` model)

- `secret-storage-relation-departed` FAILED on the leader unit (exit status 1) during
  `remove-application`.
- `secret-storage-relation-created` fired BEFORE `leader-elected` on re-deployment → peer
  relation stuck in "joining" state; all units blocked on "Waiting for peer integration".
- `postgresql-k8s --channel 14/stable` rejected by Juju 4.x ("charm requires Juju version <
  4.0.0").

## Observed behaviour

**Resource use**: `kubectl top pod gatus-k8s-0` → 1m CPU, 90Mi memory; Pebble + gatus binary
~30Mi RSS.

**Config file rendering** (confirmed by exec into container):
- `/config/ui.yaml` — always created with defaults; updated on every config change.
- `/config/endpoints.yaml` — default Ubuntu.com sample; updated on config change.
- `/config/storage.yaml` — absent unless the postgresql relation is present; correctly rendered
  with `postgresql://` URI (username, password, host, port, database).
- `/config/alerting.yaml` — absent unless `mattermost-alerting` has a `default` key; with an
  invalid URL (`http://invalid-url`) the file is still rendered and gatus stays `active`.
- `/config/security.yaml` — absent unless all four OIDC env vars are present from the hydra
  relation; not rendered until hydra has fully created the OAuth client.

**Pebble env after secrets integration**: `APP_MATTERMOST_ALERTING` holds the secret ID (kept
intentionally, so the rock can detect changes); `MATTERMOST_WEBHOOK_URL` is resolved from the
secret's `default` key.

**Pebble env after PostgreSQL integration**: `POSTGRESQL_DB_CONNECT_STRING`,
`POSTGRESQL_DB_NAME`, `POSTGRESQL_DB_PASSWORD`, `POSTGRESQL_DB_USERNAME`,
`POSTGRESQL_DB_HOSTNAME`, `POSTGRESQL_DB_PORT`, `POSTGRESQL_DB_SCHEME`.

**Secret blocking (confirmed)**: when the Mattermost secret exists but lacks a `default` key,
`is_ready()` returns False and sets `BlockedStatus("Secret exists but 'default' webhook URL is
not set")`. The Pebble service keeps running (charm-level check only); `update-status` fires
cleanly; the charm recovers to `active` once the secret gains a `default` key or is removed.

**PaaSCharm blocks on optional OIDC (Juju 3.6)**: after relating gatus-k8s to hydra while hydra
itself is blocked ("Missing required relation with public-route"), PaaSCharm's `is_ready()` calls
`_oauth.is_client_created()` → False → `BlockedStatus("Please check hydra charm!")`. The Pebble
workload stays `active`. Status log within the same hook shows `workload active` then `workload
blocked "Please check hydra charm!"` — consistent with PaaSCharm setting `ActiveStatus` and then
the OIDC check overriding it. `security.yaml` is not rendered. OIDC is declared `optional: true`
in `charmcraft.yaml`, but PaaSCharm does not check that flag before blocking.

**`config-changed` fires twice per change (confirmed)**. From `juju show-status-log --days 1`:
```
00:04:13  running config-changed hook
00:04:13  workload active
00:04:13  workload maintenance  Preparing service for restart   ← restart() called
00:04:14  workload active
00:04:14  workload active                                    ← first hook ends, second begins
00:04:15  workload maintenance  Preparing service for restart   ← restart() called again
```
Each `juju config` call triggers two `config-changed` invocations. Each calls `restart()`, which
calls `_create_charm_state()` in `is_ready()`, again inside `is_ready()`'s call to
`stop_all_services()`, and again in `restart()`'s call to `_create_app()` — three calls per
invocation, six per config change. The second hook invocation repeats identical work.

**Relation removal**:
- Removing `metrics-endpoint` fires `relation-departed`/`relation-broken` cleanly; pebble service
  keeps running.
- Removing the postgresql relation removes the `POSTGRESQL_DB_*` env vars and
  `/config/storage.yaml`; gatus stays `active/idle` (in-memory storage). Re-adding re-renders
  storage config with the new relation ID.
- On a clean deploy, `secret-storage-relation-departed` succeeds on all units, followed by clean
  `stop`/`remove` hooks and pod destruction. On a stuck peer relation (from a prior failed
  removal) the hook can fail — see Finding 1.

**`update-status` hook**: fires every 5 minutes; observed at 00:28:53 — clean, no errors, no
restart. Only restarts on FAILED database-migration status, not set in normal operation.

**`rotate-secret-key` action**: causes `restart()`; the pebble layer briefly disappears (env vars
removed, `go` service `inactive`) for ~5–10s while the plan regenerates and the service restarts.
Not instant — operators should expect a short interruption.

**Leader-election race on peer-relation init**: if `secret-storage-relation-created` fires before
the unit is elected leader, `KeySecretStorage._on_secret_storage_relation_created()` exits early
(`if not self._charm.unit.is_leader(): return`) and the secret key is never written. PaaSCharm
does not register a `leader-elected` hook to catch this. The peer relation stays "joining" with
empty `application-data`, and the charm blocks on "Waiting for peer integration" indefinitely.

**Misleading unit status**: while blocked on peer integration, non-leader unit workload status
can show `active/idle` because Juju reports Kubernetes pod/container "Running" as workload
"active" regardless of whether the Pebble service inside is actually running.

**Juju 3.6 vs 4.0**: PostgreSQL integration works on 3.6, fails on 4.x
("charm requires Juju version < 4.0.0"). The OIDC-blocking behaviour is code-level and applies on
both versions (unverified on 4.x directly — observed on 3.6 only). All other observed behaviours
(config validation, secret handling, relation removal) matched across both environments.

## Findings

### 1. Peer-relation secret-key init race: `relation-created` can fire before leadership is established, with no recovery path
- **Severity**: high
- **Kind**: bug
- **Where**: `deps/paas_charm/secret_storage.py:52-57` (`_on_secret_storage_relation_created`); `deps/paas_charm/charm.py` (no `leader-elected` handler registered)
- **Evidence**: `juju show-status-log --days 1 gatus-k8s/0`:
  ```
  00:39:17  secret-storage-relation-created hook fires
  00:39:18  workload waiting "Waiting for peer integration"
  00:39:35  leader-elected hook fires  ← later, not earlier
  ```
  `_on_secret_storage_relation_created()` returns early because `unit.is_leader()` is False at
  00:39:17. `juju show-unit gatus-k8s/0` confirmed `application-data: {}` afterward. Same pattern
  seen on `gatus-k8s/1`. This race was reproduced after a prior failed `remove-application` left
  a stuck peer relation, and re-deployment onto it triggered the ordering issue; it can also
  occur independent of a prior failure if Juju elects the leader late.
- **Impact**: the charm can never become healthy without manual intervention once this race
  occurs — peer relation is permanently "joining". Every subsequent hook that calls
  `_create_charm_state()` finds `is_secret_storage_ready = False` and sets
  `WaitingStatus("Waiting for peer integration")`. Only recovery is destroy-and-redeploy, which
  can fail again if the old pod isn't fully cleaned up.
- **Fix**: register a `leader-elected` handler in PaaSCharm's `KeySecretStorage` that checks
  `is_initialized` and calls `gen_initial_value()` if False. Alternatively, allow
  `_on_secret_storage_relation_created` to write keys regardless of leadership (ops permits any
  unit in a peer relation to write app data, though this needs care for concurrent writers).
- **Linter rule**: "peer-relation secret initialization only in relation-created handler without
  a leader-elected fallback" — mechanically checkable.

### 2. `block_if_invalid_data` only catches two exception types; others propagate as hook failures
- **Severity**: high
- **Kind**: bug
- **Where**: `deps/paas_charm/charm_utils.py:45-71`
- **Evidence**: the decorator around `_create_charm_state()` catches only
  `CharmConfigInvalidError` and `RelationDataError`. `_create_charm_state()` can also raise
  `ValueError` (from `app_config_class_factory`, `charm_state.py:410`), `NameError` (missing
  charm libraries), and `SecretAccessPendingError` (charm-specific — see Finding 3, confirmed
  concretely).
- **Impact**: any unexpected exception from `_create_charm_state()` fails the hook with exit
  status 1, leaving the charm in `error` state awaiting `juju resolve`, with no status message
  to guide the operator.
- **Fix**: catch `Exception` broadly and set a generic `BlockedStatus`, or at minimum add
  `SecretAccessPendingError`, `ValueError`, and `RuntimeError`.
- **Linter rule**: "decorator only catches `CharmConfigInvalidError`/`RelationDataError` but
  `_create_charm_state()` can raise other types" — checkable by instrumenting with mock
  exceptions.

### 3. `SecretAccessPendingError` propagates as a hook failure when secret-typed config is unreadable
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:86` (`_get_juju_secret_content`); `deps/paas_charm/charm_utils.py:45-71`
- **Evidence**: deployment log step 13 (Round 3) — `juju add-secret ... alerts=...` (no `default`
  key) → `juju config mattermost-alerting="secret:..."` → `config-changed` FAILED, exit status 1,
  unit in `error`:
  ```
  ops.model.ModelError: ERROR "gatus-k8s/0" is not allowed to read this secret
  exceptions.SecretAccessPendingError: Waiting for access to Juju secret 'secret:fi3ff11gr7rota1hsee0':
    ERROR "gatus-k8s/0" is not allowed to read this secret
  ```
  `_get_juju_secret_content()` raises `SecretAccessPendingError` when `secret.get_content()`
  raises `ModelError` (access denied); this happens during `_create_charm_state()`'s config
  iteration, before `is_ready()` runs, and is not caught by `block_if_invalid_data`.
- **Impact**: any config-typed secret the charm cannot read — missing grant, wrong role,
  persistent policy issue — turns into `error` status instead of an actionable `blocked` message.
  Recovery requires manually resetting config or fixing the grant.
- **Fix**: catch `SecretAccessPendingError` in `block_if_invalid_data` and set
  `BlockedStatus("Waiting for access to secret '{secret_id}'")`, or wrap the `get_content()` call
  in `_create_charm_state()` to convert `ModelError` into a handled status.
- **Linter rule**: "hook handler calls `secret.get_content()` without catching `ModelError`" —
  mechanically checkable.

### 4. `is_ready()` override can bypass parent's peer-relation readiness check
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:200-240` (`is_ready()`); `deps/paas_charm/charm.py:586` (`is_ready()`)
- **Evidence**: `GatusCharm.is_ready()` validates the Mattermost secret, endpoint placeholders,
  and Gatus config before calling `super().is_ready()`. If any Gatus-specific check fails, it
  returns False without reaching the parent's `is_secret_storage_ready` check, which would
  otherwise set `WaitingStatus("Waiting for peer integration")`. Non-leader units were observed
  showing `active/idle` while the peer relation had empty `application-data: {}` (confirmed via
  `juju show-unit`).
- **Impact**: when the peer relation isn't initialized, a unit whose Gatus-specific checks happen
  to pass can report status inconsistent with actual readiness.
- **Fix**: call `super().is_ready()` first and short-circuit on False before Gatus-specific
  checks, or explicitly check `is_secret_storage_ready` in the override.
- **Linter rule**: "`is_ready()` override does not call `super().is_ready()` on a False-return
  path" — mechanically checkable.

### 5. PaaSCharm unconditionally blocks on optional OIDC integration
- **Severity**: high
- **Kind**: bug
- **Where**: `deps/paas_charm/charm.py:613-617`
  ```python
  if self._oauth and self._oauth.is_related():
      if not self._oauth.is_client_created():
          logger.warning(msg := f"Please check {self._oauth.get_related_app_name()} charm!")
          self.update_app_and_unit_status(ops.BlockedStatus(msg))
          return False
  ```
- **Evidence**: deployment log step 13 (Round 4). After `juju integrate gatus-k8s:oidc
  hydra:oauth` with hydra itself blocked, `_oauth.is_client_created()` returns False and
  PaaSCharm sets `BlockedStatus("Please check hydra charm!")`. Status log within the same hook:
  `workload active` then `workload blocked`. The Pebble workload stays `active`; `security.yaml`
  is not rendered. OIDC is declared `optional: true` in `charmcraft.yaml`, but the check does not
  consult that flag.
- **Impact**: an operator who relates gatus to hydra to enable OIDC sees the charm go `blocked`
  even though the workload is running fine and OIDC was never required.
- **Fix**: either override `is_ready()` in `GatusCharm` to skip the OIDC block when the
  integration is optional, or fix PaaSCharm to check `requires[endpoint_name].optional` before
  blocking — the latter benefits all PaaSCharm-based charms with optional OIDC.
- **Linter rule**: not mechanically checkable without reading charm metadata.

### 6. `secret-storage-relation-departed` fails on leader unit when the peer relation is stuck
- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/paas_charm/charm.py:571` (`_on_secret_storage_relation_departed`);
  `deps/paas_charm/charm.py:586` (`is_ready()`)
- **Evidence** (Round 1): `juju debug-log`:
  ```
  unit-gatus-k8s-0: WARNING ... we should run a leader-deposed hook here, but we can't yet
  unit-gatus-k8s-0: ERROR ... hook "secret-storage-relation-departed" failed: exit status 1
  ```
  while unit `gatus-k8s/1` (non-leader) ran the hook, `stop`, and `remove` successfully. Both
  pods remained `Running` after `remove-application` completed. On a clean deploy (Round 3, step
  8) the same hook succeeded on both units, with `stop`/`remove` following and pods destroyed —
  confirming the failure is specific to a peer relation already stuck "joining" from a prior
  failed removal (see Finding 1), not a general decorator bug.
- **Impact**: when the peer relation is stuck, the only recovery is destroy-and-redeploy; the
  stuck state is not obviously distinguishable in `juju status` from normal init delay, and a
  leftover pod can re-join a future deployment (triggering Finding 1).
- **Fix**: same as Finding 1 — a `leader-elected` recovery handler removes the underlying stuck
  state; the `relation-departed` hook itself needs no change for the normal case.
- **Linter rule**: same as Finding 1.

### 7. `config-changed` fires twice per config change (triple `_create_charm_state()` per hook)
- **Severity**: medium
- **Kind**: performance
- **Where**: `deps/paas_charm/charm.py:728` (`restart()`), `deps/paas_charm/charm.py:586`
  (`is_ready()`), `deps/paas_charm/go/charm.py:79` (`_create_app()`)
- **Evidence**: see Observed Behaviour above — two `config-changed` hooks per `juju config`,
  three `_create_charm_state()` calls per invocation (via `is_ready()`, `stop_all_services()`,
  and `_create_app()`), six total per config change. Each `_create_charm_state()` call accesses
  `self.config` via `config_get_with_secret()`, which the ops framework appears to detect as a
  config change mid-hook and re-emits `config-changed`.
- **Impact**: 2× hook execution, 2× workload restart and pebble `replan()` per config change; on a
  slow container config application takes roughly twice as long.
- **Fix**: cache `CharmState` on the charm instance for the duration of a hook invocation instead
  of recomputing it, or restructure `restart()` to call `is_ready()` once and pass the resulting
  `CharmState` down. Best fixed in `paas_charm`.
- **Linter rule**: "`_create_charm_state()` called more than once per event handler without
  caching" — checkable via call-count instrumentation in tests.

### 8. No caching on `_get_juju_secret_content`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:86` (`_get_juju_secret_content`)
- **Evidence**: the method is called on every `config-changed` (twice per change), every
  `secret-changed`, and every `is_ready()` run, each time calling `secret.get_content(refresh=True)`
  against the API server with no memoization.
- **Impact**: a misconfigured secret grant causes repeated `SecretAccessPendingError` retries on
  every hook without progress, and each attempt re-fetches from the API server, adding load.
- **Fix**: memoize within a hook invocation (instance variable or `functools.lru_cache` scoped
  appropriately).
- **Linter rule**: "hook handler calls `secret.get_content()` more than once per invocation
  without caching" — checkable via data-flow analysis.

### 9. postgresql-k8s channel 14 does not support Juju 4.x; CI only tests Juju 3.6
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `.github/workflows/integration_test.yaml:21` (`juju-channel: 3.6/stable`)
- **Evidence**: `juju deploy postgresql-k8s --channel 14/stable` on `concierge-k8s-4` (Juju
  4.0.12) fails with "charm requires Juju version < 4.0.0". Confirmed working correctly on Juju
  3.6.25 (Round 4): storage.yaml rendered correctly, relation removal/re-add worked cleanly.
- **Impact**: production deployments on Juju 4.x cannot use the postgresql-k8s relation, and CI
  does not catch this since it only runs on 3.6. `postgresql` is declared `optional: true`, so
  it's not a hard blocker, but it's a significant gap for production use needing persistent
  storage.
- **Fix**: add a Juju 4.x CI job, or document the 3.6 requirement for the postgresql relation, or
  find a postgresql-k8s channel that supports 4.x.
- **Linter rule**: "integration tests run on a different Juju version than the charm's published
  bases support" — checkable by comparing CI `juju-channel` against `bases` in `charmcraft.yaml`.

### 10. Juju secret `view` role does not permit content reading; `grant-secret` gives no way to grant more
- **Severity**: medium
- **Kind**: ux
- **Where**: Juju secret grant mechanism (ops library); `src/charm.py:86`
- **Evidence**: Round 3 step 14 — `juju grant-secret fi3ff11... gatus-k8s` → `juju show-secret`
  shows `role: view`; the unit still cannot read content
  (`ERROR "gatus-k8s/0" is not allowed to read this secret`). `juju grant-secret` has no `--role`
  flag.
- **Impact**: the documented Mattermost-alerting workflow (create secret → grant → set config)
  hits a hook failure (see Finding 3) instead of a clean blocked status, because the default
  grant role is insufficient.
- **Fix**: document the correct grant procedure if one exists, or handle the resulting
  `ModelError`/`SecretAccessPendingError` gracefully with an actionable `BlockedStatus` (ties into
  Finding 3's fix).
- **Linter rule**: not mechanically checkable.

### 11. `restart()` does not catch all exceptions from `is_ready()`'s call chain
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:237` (`restart()`); `deps/paas_charm/charm.py:728` (`restart()`)
- **Evidence**: `is_ready()` calls `_create_charm_state()`, which can raise
  `CharmConfigInvalidError` or `RelationDataError` (and others per Finding 2). `restart()` only
  catches `CharmConfigInvalidError`, and only after `_create_app().restart()` has already been
  invoked — an exception raised earlier in the chain propagates uncaught.
- **Impact**: an unexpected exception type propagating from `_create_charm_state()` during a
  decorated hook fails the hook with exit status 1.
- **Fix**: wrap the `is_ready()` call in `restart()` with a broader exception handler that sets
  `BlockedStatus`, not just for `CharmConfigInvalidError`.
- **Linter rule**: not mechanically checkable — requires flow analysis.

### 12. Bare `except Exception` in the YAML validator masks bugs
- **Severity**: low
- **Kind**: bug
- **Where**: `src/validator.py:70-73`
  ```python
  except Exception as e:
      logger.error(e)
      return "Unexpected error on {config_key}"
  ```
- **Evidence**: any unexpected error during Pydantic validation is replaced with a generic
  message; `ValidationError` is handled separately (line 75, returns `FAILED_TO_VALIDATE`), so
  only genuinely unexpected exceptions are swallowed here.
- **Impact**: a bug in `GatusConfig.model_validate()` produces "Unexpected error on endpoints"
  with no actionable detail for the operator.
- **Fix**: re-raise so the exception propagates to the hook's own error handling, or log
  `type(e).__name__` and `repr(e)` in addition to `str(e)`.
- **Linter rule**: "do not catch bare `Exception` in validation code" — checkable with a ruff
  rule.

### 13. `oidc-redirect-path` config option has no format validation
- **Severity**: low
- **Kind**: bug
- **Where**: `charmcraft.yaml` config definition (no regex constraint on the string type)
- **Evidence**: deployment log step 5 (Round 3) — `juju config oidc-redirect-path="%%invalid"`
  left the charm `active`, silently accepting a malformed path.
- **Impact**: a malformed redirect path silently produces a broken OIDC flow — user
  authenticates but is never redirected back correctly.
- **Fix**: add a regex constraint in `charmcraft.yaml`, or a `GatusValidator` check on the path
  format.
- **Linter rule**: "string config option with no constraints is not validated in the charm" —
  mechanically checkable.

### 14. `_alerting_secret` computed twice in `is_ready()`
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:209` and `src/charm.py:212`
- **Evidence**: `is_ready()` reads `self._alerting_secret` and then separately calls
  `self._get_juju_secret_content(MATTERMOST_ALERTING_CONFIG)` again; each fetches secret content
  via `secret.get_content(refresh=True)`.
- **Impact**: minor extra API calls on every `is_ready()` invocation (which itself fires twice
  per config change per Finding 7); compounds with the lack of caching in Finding 8.
- **Fix**: compute once, reuse the value.
- **Linter rule**: not mechanically checkable.

### 15. `test_endpoints_config` does not read back the rendered config file
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py:53-83`
- **Evidence**: after `juju config endpoints=...`, the test waits for `active` and reads back
  config via the pebble layer (`get_config()`), but never checks the actual rendered
  `/config/endpoints.yaml` in the container. By contrast, `test_mattermost_alerting` and
  `test_endpoints_provider_override_webhook` poll the real rendered file.
- **Impact**: the test could pass with a stale config if the charm re-rendered from old data or
  the pebble layer drifted from the filesystem.
- **Fix**: add a `juju ssh gatus-k8s/0 cat /config/endpoints.yaml` assertion, mirroring the
  alerting tests' polling helpers.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **`restart()` validation guard** (`src/charm.py:42-49`): calling `GatusValidator.validate()`
  before `super().restart()` is a clean, explicit way to keep an invalid config from ever
  reaching the workload, self-contained without relying on callers checking a return value.
- **Secret placeholder resolution** (`src/charm.py:82-104`): the `[webhook-url:channel-name]`
  placeholder syntax in endpoints YAML, resolved from a Juju secret, keeps sensitive data in
  secrets while letting operators reference per-channel webhooks in plain config; missing keys
  correctly block the charm.
- **`SecretAccessPendingError` sentinel** (`src/exceptions.py`): a dedicated exception type for
  "secret exists but not yet readable" correctly distinguishes eventual-consistency lag from a
  permanent misconfiguration — it just isn't caught everywhere it should be (Findings 2–3).
- **Conditional file cleanup in `render_configs()`** (`gatus_rock/render_config.py`): stale config
  files (`alerting.yaml`, `security.yaml`) are removed when their inputs disappear, keeping the
  filesystem consistent with current config.
- **Placeholder-aware validation skip** (`src/validator.py:58-64`): validation is skipped when
  unresolved placeholders are present, and this is documented and tested
  (`test_validator_skips_endpoints_with_placeholders`).
- **`render_config.py` separation of concerns**: always-render (ui.yaml), conditionally-render
  (storage/alerting/security), and raw-passthrough (announcements/endpoints) paths are cleanly
  separated and independently testable.
- **Pydantic models for config validation** (`src/gatus.py`): give structured, actionable error
  messages that surface as blocked-status text.
- **49 unit tests, all passing**: `SimpleNamespace` mocks are appropriate for the covered paths;
  `_create_app` override is tested by mocking the parent class and asserting on
  `gen_environment()` output.
- **`go-framework` rock-based deployment**: Pebble manages the service lifecycle, avoiding a
  custom workload layer in the charm.
- **Database integration test polling helpers** (`tests/integration/test_alerting.py`):
  `_wait_for_mattermost_webhook()` and `_wait_for_resolved_endpoint_webhook()` poll actual
  rendered files in the container, not just the pebble layer.

## Common-practice notes

- Uses the `go-framework` extension appropriately for a Go binary workload on Kubernetes.
- Charm libraries vendored under `lib/charms/<lib>/v<N>/`, all at `v0` — correct convention.
- The charm is a thin wrapper around `paas_charm.go.Charm`; real logic lives in `deps/paas_charm/`.
  This means library bugs (most findings above) are outside the charm's own test suite, and the
  library version in use is determined by the rock's vendored deps, not `requirements.txt`.
- `block_if_invalid_data` is applied to all hook handlers — correct pattern, but incomplete
  exception coverage (Findings 2–3).
- No `StoredState` usage; `CharmState` dataclass instead — modern approach.
- `pytest` via `uv`, and `pyproject.toml` for ruff/pyright/bandit/codespell config — standard.
- `charmcraft.yaml` config descriptions are comprehensive; `mattermost-alerting` secret
  description lists all supported keys.
- `_context/charms.json` reports `kind: machine` for gatus-k8s, but it runs on Kubernetes via
  `go-framework` — a metadata reporting issue, not a code defect.
- Metrics integration correctly uses the standard `prometheus_scrape` interface; confirmed
  working with `grafana-agent-k8s` (relation data contains `alert_rules`, `scrape_jobs`).
- No custom `hooks/` directory; all events go through `ops.main()`.
- OAuth relation uses `PaaSOAuthRequirer` wrapping `charms.hydra.v0.oauth`; `update_client()` runs
  in PaaSCharm's `restart()` before the pebble layer is applied, and `is_client_created()` gates
  `is_ready()` (see Finding 5).

## Tests

**Unit tests: 49 passed (0.17s)**
```
tests/unit/test_charm.py           21 tests — GatusConfig, validator, secret handling,
                                    _create_app injection
tests/unit/test_render_config.py   28 tests — all template rendering paths
```
Run with `PYTHONPATH=lib:src python3 -m pytest tests/unit/ -v`. Tests use `SimpleNamespace`
mocks rather than full `Harness` setup, appropriate for the paths covered.

**Static analysis: clean**
- `ruff check src/ tests/` — 0 issues
- `ruff format --check src/ tests/` — 13 files already formatted
- `codespell src/ tests/` — 0 issues
- `PYTHONPATH=lib:src pyright src/charm.py src/validator.py src/gatus.py src/constants.py src/exceptions.py`
  — 0 errors/warnings/informations
- `bandit` — not installed in the review environment; `tox.ini` references it but config lives in
  `pyproject.toml`

**Integration tests: not run** — require a pre-built `.charm` or rock image (`CHARM_PATH` /
`ROCK_IMAGE`/`OCI_RESOURCE_NAME`), not available in the review environment. The test suite itself
is well-structured and reads actual rendered files from the container via `juju ssh ... cat
/config/...` rather than only the pebble layer.

**Coverage gaps relative to observed behaviour**
1. `secret-storage-relation-departed` failure on a stuck peer relation — not tested.
2. Double `config-changed` fire — not tested or documented.
3. The `restart()` validation guard is not unit-tested (parent is fully mocked).
4. Pebble self-healing after a process kill — not tested.
5. Secret-without-`default`-key blocking path — not unit-tested (`is_ready()` not exercised).
6. `_get_juju_secret_content` no-caching behaviour — not tested in isolation.
7. `is_ready()` override bypassing the parent's peer-relation check — not tested.
8. Peer-relation initialization race (leader not yet elected at `relation-created`) — not tested
   in any scenario.
9. postgresql-k8s integration not runnable on Juju 4.x due to the channel-14 constraint; confirmed
   working on Juju 3.6 in this review, but no CI coverage of that constraint.
10. `SecretAccessPendingError` from an unreadable secret-typed config — not unit-tested.
11. Juju secret `view` role insufficient for content reading — not tested; integration tests
    grant secrets without verifying the charm can actually read the content.
12. `rotate-secret-key`'s ~5–10s service interruption — not tested.
13. PaaSCharm blocking on optional OIDC — not tested; `test_charm.py` doesn't cover the OIDC
    relation path.
14. `_oauth.is_client_created()` returning False and setting BlockedStatus — not unit-tested.
15. `test_endpoints_config` does not read back the rendered `/config/endpoints.yaml`.

## Docs

- **README.md**: clear and accurate; step-by-step for PostgreSQL, Mattermost secrets, and OIDC
  relations. Verified against the deployed charm — config file rendering matches documented
  behaviour. One mismatch: the README describes OIDC setup as `juju deploy hydra; juju relate
  gatus-k8s hydra` but doesn't mention hydra itself needs a database (postgresql-k8s) and ingress
  (traefik-k8s), and postgresql-k8s can't be deployed on Juju 4.x.
- **CONTRIBUTING.md**: standard Canonical boilerplate.
- **charmcraft.yaml config descriptions**: clear and thorough, including all supported
  `mattermost-alerting` secret keys.
- **CLAUDE.md**: minimal — points to `.github/instructions/`.
- **No `docs/` directory**: all documentation lives in README.md; acceptable for a single-charm
  repo, and no other doc/reality mismatches found for the paths tested.

## Open questions

1. **Config-changed double-fire root cause**: the working theory is that `self.config` access
   inside `_create_charm_state()` triggers the ops framework to re-emit `config-changed`.
   Confirming this needs either reading the ops framework's event-firing logic or a test that
   asserts the exact invocation count per `juju config` call.
2. **Which postgresql-k8s channel supports Juju 4.x, if any**: 14/stable rejects 4.0.12; not
   established whether any channel currently supports Juju 4.x.
3. **Correct Juju secret role/procedure for content reading**: `grant-secret` defaults to `view`,
   which does not permit content reading in this environment, and has no `--role` flag; the
   correct grant mechanism is not established from this review.
4. **`charmcraft pack --force` fails with an experimental-extension warning on ubuntu@24.04** for
   the `go-framework` extension — not resolved locally; the charm was deployed from charmhub
   instead. Whether CI has special handling for this is not established.
