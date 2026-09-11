# jenkins-agent-k8s

A clean, well-tested Kubernetes charm that registers a Jenkins agent with a Jenkins server, either
via direct config or the `jenkins_agent_v0` relation. It uses a single-handler reconciliation
pattern with no `StoredState`/`defer()`, and the happy-path lifecycle (deploy, relate, scale,
refresh, pod restart) works cleanly on both Juju 3.6 and 4.0. The serious problem is that the
charm never stops the Pebble workload when it loses its credentials: on relation removal (and on
config being cleared) the charm goes to `blocked` while the agent process keeps crash-looping
against stale credentials indefinitely, wasting resources and giving operators a false sense that
the unit is idle. A maintainer should fix `_on_reconcile` and `relation_departed` to call
`stop_agent()` whenever credentials become unavailable, then wire up a `pebble_check_failed`
handler so the charm is aware of, and can react to, its own workload's crash loop.

| | |
|---|---|
| Repo | canonical/jenkins-agent-k8s-operator @ `905662d` (2026-06-12) |
| Charms | jenkins-agent-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (`latest/edge` rev 77, matches local HEAD) and concierge-k8s-3 (Juju 3.6) |
| Reviewed | 2026-08-19 |

## What it does

Deploys a Jenkins agent on Kubernetes, registering with a Jenkins server either via explicit
config (`jenkins_url` + `jenkins_agent_name` + `jenkins_agent_token`) or a `jenkins_agent_v0`
relation to a Jenkins server charm. Config takes precedence and is mutually exclusive with the
relation (blocks if both present). The agent JAR runs under Pebble in a workload container as user
`_daemon_` (UID 584792). The OCI image is built via rockcraft with `openjdk-21-jre-headless` and
grants `_daemon_ ALL=NOPASSWD: ALL` in `/etc/sudoers`.

## Deployment log

### Juju 4.x (concierge-k8s-4, primary)

1. `juju add-model rv-jenkins-agent k8s --controller concierge-k8s-4` ✓
2. `juju deploy jenkins-agent-k8s --channel edge` — deployed rev 77, same commit as local HEAD ✓
3. Pod pulled OCI image (~3m51s to Ready) ✓
4. Unit settled to `blocked: Credentials not available from config or relation.` ✓
5. `juju config jenkins_url="http://invalid:8080" ...` — unit went to `maintenance: Reconciling
   agent state <ConfigChangedEvent>` ✓
6. After 4 retry attempts (5s, 8s, 16s backoff): `error: hook failed: "config-changed"` ✓
7. Cleared config — unit recovered to `blocked` correctly ✓
8. Pebble inside workload container: `Plan has no services.` (correct — no credentials) ✓
9. URL-only config: `blocked: Invalid jenkins config values.` ✓
10. name+token without URL: `blocked: Invalid jenkins config values.` ✓
11. Scale-up to 2 units: both pods provisioned and `blocked` ✓
12. Scale-down to 1 unit: pod terminated cleanly ✓
13. `juju refresh`: `already up-to-date` (rev 77 = latest) ✓
14. Related to jenkins-k8s server — both units went to `active` ✓
15. `juju remove-relation jenkins-agent-k8s jenkins-k8s` — relation removed, units `blocked`, but
    pebble services crash-looping (see Observed behaviour) ✓
16. Re-related to jenkins-k8s — both units returned to `active` self-sufficiently ✓
17. Config+relation present simultaneously — `blocked: Please remove either configuration or
    agent relation.` ✓
18. Config with live server + wrong token — `blocked: Additional valid agent-token pairs
    required.` ✓ (validated via live jenkins-k8s at 10.1.0.83:8080)
19. Config cleared while `blocked` — recovered correctly to `blocked: Credentials not available
    from config or relation.` ✓
20. `juju remove-application --force --no-prompt`: pod removed cleanly, model empty ✓

### Juju 3.x (concierge-k8s-3)

1. `juju add-model rv-jenkins-agent-3 k8s --controller concierge-k8s-3` ✓
2. `juju deploy jenkins-agent-k8s --channel edge` — rev 77 ✓
3. Brief `waiting: installing agent` transition (~30s), then converged to
   `blocked: Credentials not available from config or relation.` — same final state as Juju 4.x ✓
4. Related to jenkins-k8s — both units went to `active` ✓
5. `juju remove-relation` — `agent-relation-departed` fired on both units, both pebble services
   entered crash loop, both went to `blocked` ✓

## Observed behaviour

**Lifecycle** (both Juju versions): deploy → `blocked` (no creds) → relate → `maintenance` →
`active` — correct at every step. Config-mode lifecycle (blocked → maintenance (config set) →
maintenance (downloading JAR) → maintenance (starting service) → active) is likewise correct.
Server unreachable in config mode: `maintenance` → exponential-backoff retry → `hook failed:
"config-changed"` after 5 attempts, Juju requeues, repeats indefinitely. Config cleared while in
error recovers to `blocked` on the next hook. Config+relation conflict correctly blocks with
"Please remove either configuration or agent relation." Config mode with a live server but a bad
token correctly reaches `blocked: Additional valid agent-token pairs required.` — `validate_credentials`
detects the failure via `container.exec()` with a 5-second timeout.

**Self-recovery on re-relation.** After relation removal (pebble service crash-looping, unit
`blocked`), re-relating to the same jenkins-k8s unit returned both agent units to
`active: Agent up to date.` The re-relation supplied the same server URL (10.1.0.83) that was
already in the stale pebble layer; `_agent_up_to_date` compares the pebble layer env vars against
the relation databag, finds a match, and short-circuits without restarting the agent. Self-recovery
only works because the new server had the same IP as the stale layer — if the server pod had a new
IP, the charm would correctly detect the mismatch and restart. This means the charm cannot self-heal
from a crash loop caused by credential invalidation alone (only from an IP change).

**Pod restart.** Deleting the agent pod triggers Kubernetes to reschedule it with no pebble layer.
The charm receives `config_changed` + `start` + `pebble_ready` → `_on_reconcile` → relation still
has valid credentials → downloads JAR → starts pebble service → agent reconnects, reaching
`ActiveStatus` within ~30s. The pebble service has `startup: enabled`, so this needs no
charm-level action — correct default behaviour.

**`pebble_check_failed` fires but is a no-op.** The `jenkins-agent-k8s-pebble-check-failed` hook
dispatched on both units after the agent entered a crash loop, confirmed in debug log at 16:44:06
UTC (unit-1) and 16:44:21 UTC (unit-0), and again at 17:21:36 (unit-1, after config was cleared).
The charm has no registered handler for it — `src/charm.py:37–45` only observes `config_changed`,
`upgrade_charm`, `pebble_ready`, and the `relation_*` events — so Juju's default no-op handler runs
and the crash loop continues.

**Stale status window after relation removal with config still set.** `config_changed` fired at
17:19:08 on both units while the relation was still present and config was also set, correctly
blocking with "Please remove either configuration or agent relation." `relation_broken` fired at
17:19:30; by then `get_relation(AGENT_RELATION)` is `None` so the `source == "config"` path should
take over, but `juju status` at 17:20:14 still showed the stale "Please remove..." message. This
appears to be a transient window between the `config_changed` block and the next reconcile; it
resolved once a subsequent hook fired with no relation present, and clearing config (`jenkins_url=""`)
recovered the unit to `blocked: Credentials not available from config or relation.` correctly. Not
persistent — noted for completeness, not treated as a standalone bug.

**Pebble service stays in crash loop after relation removal.** When the relation is removed and
the charm goes to `blocked`, the pebble layer is *not* removed. The service has `startup: enabled`
and keeps restarting the agent with the stale env vars. The agent repeatedly fails with
`404 Not Found` / `Invalid or already used credentials.`; no `.ready` file is created, so the
readiness check fails. Confirmed on both k8s-4 (Juju 4.0.12) and k8s-3 (Juju 3.6.25):
`pebble services` shows `backoff`, pebble logs show repeated `IOException: 404 Not Found`.

**Pebble layer accumulation.** Each `add_layer(label="jenkins-agent-k8s", layer=L, combine=True)`
call adds a new layer to the combined plan; `override: "replace"` makes the latest layer's service
definition win, but old layers are not removed from storage. No observed failure, but layers
accumulate across repeated reconciles — worth monitoring on long-lived units.

**Juju 3.x vs 4.x differences**

| Aspect | Juju 3.6 | Juju 4.0 |
|---|---|---|
| Initial status | `waiting: installing agent` (~30s) → `blocked` | `blocked` directly |
| `relation_departed` with 2 units | Fires on both units | Fires on both units |
| Departing unit in `relation.units` during hook | No | No (yes with 1 unit) |
| Pebble crash loop after relation removal | Yes (both units) | Yes (both units) |
| Final status after relation removal | `blocked` (both units) | `blocked` (both units) |

The transient `waiting` on Juju 3.x is a Juju version difference, not a charm bug.

## Findings

### 1. Pebble service not stopped when credentials become unavailable — indefinite crash loop with stale creds

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:77–81`
- **Evidence**: when `credentials is None`, `_on_reconcile` sets `BlockedStatus` and returns
  without calling `stop_agent()`. The pebble layer with the old `JENKINS_URL`/`JENKINS_TOKEN`/
  `JENKINS_AGENT` env vars is left in place, and with `startup: enabled` Pebble keeps restarting
  the agent process. Confirmed in deployment on both k8s-4 (Juju 4.0.12) and k8s-3 (Juju 3.6.25):
  after relation removal, `pebble services` shows `backoff`, pebble logs show repeated
  `IOException: 404 Not Found` and `Invalid or already used credentials.`, and no `.ready` file
  exists. `test_reconcile_no_config_no_relation` explicitly asserts `stop_agent` is *not* called
  in this state; the test comment says "charm only blocks; operator handles workload lifecycle" —
  a deliberate design choice, but one that produces the observed resource-wasting crash loop.
- **Impact**: after any relation removal or config-clear, the workload keeps crash-looping
  indefinitely, wasting CPU/network on every affected unit (both units simultaneously observed on
  k8s-3). An operator seeing `blocked: Credentials not available...` reasonably assumes the unit is
  idle; it is not.
- **Fix**: when `credentials is None`, call `pebble_service.stop_agent(container)` before setting
  `BlockedStatus`. `stop_agent` is idempotent and safe to call when no service is running.
- **Linter rule**: not mechanically checkable — requires reasoning about the pebble layer
  lifecycle.

### 2. `pebble_check_failed` hook fires but has no handler — crash loop persists undetected

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:37–45`
- **Evidence**: `__init__` registers `config_changed`, `upgrade_charm`, `pebble_ready`,
  `relation_joined`, `relation_changed`, `relation_departed` on `_on_reconcile`; no handler for
  `pebble_check_failed`. Confirmed in debug log: the hook fires at 16:44:06 UTC (unit-1) and
  16:44:21 UTC (unit-0) during the crash loop that follows relation removal, and again at 17:21:36
  (unit-1). Juju's default no-op handler runs each time; the unit stays `blocked` and the pebble
  service stays in `backoff`. Confirmed on both k8s-4 (Juju 4.0.12) and k8s-3 (Juju 3.6.25).
- **Impact**: the charm never becomes aware, via its own event handlers, that its workload is
  crash-looping. An operator cannot tell "charm is aware and recovering" from "charm is unaware."
- **Fix**: register `pebble_check_failed` on `_on_reconcile` (or a dedicated handler) and, if no
  credentials are available, call `pebble_service.stop_agent(container)` to break the loop.
- **Linter rule**: not mechanically checkable — hook registration is implicit.

### 3. `relation_departed` does not stop the agent — orphaned/stale connection to departing server

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:93–97`
- **Evidence**: `relation_departed` is registered on `_on_reconcile` with no special handling.
  - With 1 unit on k8s-4: the departing unit is still present in `relation.units` during the hook,
    so `agent_relation_credentials` is populated, `_agent_up_to_date` returns `True`, and the hook
    completes without stopping the agent — it keeps running against the departing server's
    credentials. Confirmed via debug-log: `agent-relation-departed` fires, status transitions to
    `blocked` only later via `relation_broken`, but `pebble services` shows `backoff` with stale
    env vars in the meantime.
  - With 2 units on both k8s-4 and k8s-3: the departing unit's data is already gone from
    `relation.units` by the time the hook fires on the remaining units, so
    `agent_relation_credentials` is `None`, `_resolve_credentials` returns `(None, "waiting")`, and
    the unit goes to `blocked` — again without calling `stop_agent()`.
  - In both cases the underlying bug is the same: `relation_departed` never stops the agent
    unconditionally.
- **Impact**: after a relation departs, the agent process is left running (single-unit case) or
  crash-looping with stale credentials (multi-unit case) rather than being cleanly stopped.
- **Fix**: in `_on_reconcile`, when the event is a `RelationDepartedEvent`, call
  `pebble_service.stop_agent(container)` unconditionally before any other reconciliation logic.
  `stop_agent` is idempotent.
- **Linter rule**: not mechanically checkable — requires reasoning about Juju hook-timing
  semantics and `_agent_up_to_date`.

### 4. Rock grants `_daemon_` unrestricted passwordless sudo

- **Severity**: medium
- **Kind**: security
- **Where**: `jenkins_agent_k8s_rock/rockcraft.yaml`
- **Evidence**:
  ```yaml
  jenkins-agent-configure:
    override-prime: |
      craftctl default
      /bin/bash -c "chown -R 584792:584792 $CRAFT_PRIME/var/{lib/jenkins,log/jenkins}"
      echo "_daemon_ ALL=NOPASSWD: ALL" >> $CRAFT_PRIME/etc/sudoers
      visudo -c
  ```
  `_daemon_` (UID 584792, the user running the agent JAR) can run any command as root without a
  password. This exists solely to support the integration test `test_agent_run_sudo`, which calls
  `sudo -l` via pebble exec; no charm code uses sudo.
- **Impact**: if the `_daemon_` account is compromised (e.g. via a malicious agent JAR or a
  vulnerability in the Jenkins agent protocol), the attacker gets unauthenticated root in the
  container.
- **Fix**: restrict the sudoers rule to the minimum commands actually needed, or drop it and adapt
  `test_agent_run_sudo` to not require sudo. Document the rationale if the broad rule is kept.
- **Linter rule**: not established.

### 5. No unit test for `relation_departed` with a running agent

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_agent.py`, `tests/unit/test_charm.py`
- **Evidence**: `test_reconcile_service_running` covers `relation_changed` with
  `creds_changed=False` (the short-circuit path), not `relation_departed`.
  `test_reconcile_invalid_state` exercises `relation_departed` only via an `InvalidStateError`
  monkeypatch. The integration test `test_agent_reconnects_after_server_refresh` covers server pod
  refresh, not relation departure.
- **Impact**: finding #3 (`relation_departed` not stopping the agent) would have been caught by
  such a test; a future regression in this path would go undetected.
- **Fix**: add a unit test that simulates a running agent with a relation, fires
  `relation_departed`, and asserts the agent is stopped. Add an integration test that relates,
  removes the relation, and asserts the pebble service is stopped.
- **Linter rule**: not established.

### 6. Pydantic v2 deprecation: `tools.parse_obj_as`

- **Severity**: medium
- **Kind**: lint
- **Where**: `src/state.py:78`
- **Evidence**: test run output shows `PydanticDeprecatedSince20: parse_obj_as is deprecated. Use
  pydantic.TypeAdapter.validate_python instead.`
- **Impact**: will break on a future Pydantic v3 upgrade.
- **Fix**: replace with `AnyHttpUrl.validate_python(server_url) or ""` (or the `TypeAdapter`
  equivalent).
- **Linter rule**: `PydanticDeprecatedSince20` (raised by pydantic itself during tests).

### 7. `download_jenkins_agent` retry predicate is dead code

- **Severity**: low
- **Kind**: lint
- **Where**: `src/server.py:50`
- **Evidence**:
  ```python
  @tenacity.retry(
      ...
      retry=tenacity.retry_if_result(lambda result: result is False),
  )
  def download_jenkins_agent(...):
      ...
      return  # implicit None on success; raises AgentJarDownloadError on failure
  ```
  `None is False` is always `False`, so the retry predicate never fires. Compare
  `server_is_ready`, where the same pattern is meaningful because it returns a real `bool`.
- **Impact**: harmless but misleading — a reader could assume the function retries on a falsy
  result when it only retries on exceptions.
- **Fix**: remove `retry=tenacity.retry_if_result(...)` from the decorator.
- **Linter rule**: not mechanically checkable without semantic analysis of return types.

### 8. `jenkins_agent_labels` defaults to the host machine architecture

- **Severity**: low
- **Kind**: ux
- **Where**: `src/state.py:156`, `src/metadata.py:17`
- **Evidence**:
  ```python
  labels=charm.model.config.get("jenkins_agent_labels", "") or os.uname().machine,
  ```
  `os.uname().machine` yields `"x86_64"` on x86_64 hosts; this becomes the default Jenkins agent
  label when `jenkins_agent_labels` is unset.
- **Impact**: could be a surprising default on ARM deployments, or simply not reflect operator
  intent.
- **Fix**: document the default explicitly, or require an explicit value.
- **Linter rule**: not established.

### 9. Config option names use snake_case, not kebab-case

- **Severity**: low
- **Kind**: lint
- **Where**: `charmcraft.yaml` config options
- **Evidence**: `charmcraft analyze` reports `naming-conventions: WARNING — config-options are
  using snake case naming convention.` Options: `jenkins_url`, `jenkins_agent_name`,
  `jenkins_agent_token`, `jenkins_agent_labels`.
- **Impact**: cosmetic inconsistency with the Juju style guide; renaming is a breaking change for
  existing deployments.
- **Fix**: rename to kebab-case (`jenkins-url`, etc.) — plan as a breaking change with a
  migration note.
- **Linter rule**: `charmcraft analyze` naming-conventions warning.

### 10. `test_agent_run_sudo` tests a sudo privilege, not a defined charm action

- **Severity**: nit
- **Kind**: test-gap
- **Where**: `tests/integration/test_agent_k8s.py::test_agent_run_sudo`
- **Evidence**: the test runs `sudo -l` via `unit.run` / pebble exec; no action is defined in
  `charmcraft.yaml`, and `juju actions` returns nothing for this charm. The test exists solely to
  exercise the `_daemon_ ALL=NOPASSWD: ALL` sudoers rule (finding #4).
- **Impact**: the test name suggests it tests a charm action that does not exist; its only purpose
  is to justify a security-relevant rock configuration.
- **Fix**: either define a real action and test it, or rename the test to reflect that it is
  exercising sudo privileges via pebble exec, and reduce the sudoers rule per finding #4.
- **Linter rule**: not established.

## Worth copying

- **Reconciliation pattern without `defer()`.** All events (`config_changed`, `upgrade_charm`,
  `pebble_ready`, `relation_joined/changed/departed`) funnel into a single `_on_reconcile`, which
  re-derives state from `State.from_charm()` on every call. No `StoredState`, no `defer()`. Other
  charms should adopt this.
- **Status precedence is well-structured.** `_on_reconcile` always writes a final status before
  returning, in a consistent order (`MaintenanceStatus` → `WaitingStatus` → `BlockedStatus` →
  `ActiveStatus`), with no early return that forgets to set one.
- **Idempotent databag publishing.** `_ensure_databag_published` compares the expected vs. current
  `dict(relation.data[self.unit])` before writing, avoiding unnecessary `relation_changed` churn.
- **Explicit pebble error handling.** `stop_agent` checks `container.get_service()` for existence
  rather than parsing `APIError` messages; `credentials_changed` guards against `ConnectionError`
  when reading the plan.
- **Exponential backoff on network calls.** `server_is_ready` and `download_jenkins_agent` both
  use `tenacity` with `wait_exponential(multiplier=2, min=5, max=30)`.
- **Tenacity disabled in tests.** `conftest.py`'s autouse fixture monkeypatches retry predicates to
  `False`, keeping unit tests fast and deterministic without weakening production retry logic.
- **100% test coverage.** `pyproject.toml` requires `fail_under = 99`; actual coverage measured at
  100.00% (`PYTHONPATH=src uv run pytest --cov=src`), 279 statements across 5 source files.

## Common-practice notes

- **Follows convention**: `charmcraft.yaml`-only (no `metadata.yaml`), `src/` layout,
  `ops.CharmBase`, `ops.pebble` for workload management. A Terraform module (`terraform/charm/`)
  is a nice addition many charms lack.
- **Drifts from convention**: config option names are snake_case rather than kebab-case (finding
  #9).
- **Leads convention**: the `defer()`-free reconciliation pattern, disciplined pydantic v2 usage,
  the tenacity-disable test fixture, and 100% coverage are all ahead of typical charms in this
  review set.
- **Notable**: `ops==3.7.0` is recent; the project uses `uv` for builds (not `tox`) and `ruff` for
  linting. The test suite uses the deprecated `ops.testing.Harness` API throughout — the Scenario
  framework is the recommended replacement in ops 3.x. No `lib/charms/` charm libraries are owned
  by this charm.

## Tests

| Suite | Result |
|---|---|
| Unit (52 tests, `PYTHONPATH=src uv run pytest`) | 52 passed, 0 failed |
| `ruff check src/` | All checks passed |
| `mypy src/` | Success: no issues |
| `codespell src/` | No issues |
| `charmcraft analyze` | `pip-check: OK`, `juju-config: OK`, naming-conventions warning |
| Coverage | 100.00% (99% required) |

Warnings in test output: `PendingDeprecationWarning` for `ops.testing.Harness` (used throughout
`conftest.py` and the test suite); `PydanticDeprecatedSince20` for `tools.parse_obj_as` in
`src/state.py:78` (finding #6).

Key untested paths (mapped to findings above):

- `relation_departed` with a running agent and `_agent_up_to_date` returning `True` — not
  covered by any unit test (finding #3, #5).
- `stop_agent` never called when credentials go to `None` — intentionally not covered;
  `test_reconcile_no_config_no_relation` explicitly asserts `stop_agent` is *not* called, which is
  the design choice behind finding #1.
- `pebble_check_failed` — no handler, hence untestable through the current event map (finding #2).
- `relation_departed` timing differences between Juju 3.x and 4.x cannot be exercised through
  `Harness`, which does not simulate real Juju hook-dispatch timing.
- `_daemon_` sudo privilege — only exercised by the integration test discussed in finding #10.

Integration tests (`tests/integration/test_agent_k8s.py`), not run in this review (require a full
k8s+LXD+metallb setup):

- `test_agent_recover` — deletes the agent pod, verifies reschedule and reconnect.
- `test_agent_run_sudo` — runs `sudo -l` via pebble exec (finding #10).
- `test_agent_reconnects_after_server_refresh` — refreshes the server charm (new pod IP), verifies
  agent reconnects.

Not covered by any integration test: relation removal with the agent running (the main crash-loop
bug), multi-unit relation removal, and `pebble_check_failed` handling.

## Docs

| Doc | Quality |
|---|---|
| `README.md` | Clean, links to Charmhub docs |
| `docs/reference/charm-architecture.md` | Detailed Mermaid diagram; accurately describes all 6 observed events and the reconciliation flow |
| `docs/how-to/upgrade.md` | Clear, no-migration safe-upgrade guide; verified accurate |
| `docs/reference/integrations.md` | Minimal — just the one agent→jenkins integration |
| `docs/reference/actions.md` | "See Actions on Charmhub" — no local action definitions |
| `docs/reference/configurations.md` | "See Charmhub" — no local config docs |
| `terraform/charm/README.md` | Complete, with variables, outputs, usage example |
| `CONTRIBUTING.md` | Comprehensive CI/CD and testing guide |

## Open questions

1. Should `pebble_check_failed` call `stop_agent` to prevent the crash loop, even though the unit
   is already `blocked`? (Related to finding #2.)
2. Why is the departing unit's data gone from `relation.units` during `relation_departed` on
   multi-unit deployments but present in the single-unit case? This looks like a Juju hook-timing
   nuance rather than a charm bug — the fix (finding #3) is the same either way.
3. Is `x86_64` (finding #8) the right default agent label, or should ARM/mixed-arch deployments
   require an explicit value?
4. Does the agent reconnect automatically when an HA Jenkins server's leader unit departs and
   another takes over the relation? No integration test covers this (`(unverified)`), and combined
   with finding #3 it looks like it may currently be broken.
5. Pebble layer accumulation (`combine=True` on every reconcile) — not observed to cause failures,
   but worth monitoring on long-lived, frequently-reconciling units.
