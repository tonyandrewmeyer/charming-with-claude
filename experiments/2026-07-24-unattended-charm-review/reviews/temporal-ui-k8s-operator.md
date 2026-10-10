# temporal-ui-k8s

A compact k8s sidecar charm for the Temporal Web UI, clean code and good scenario-test
coverage, but with several runtime defects operators will hit in practice: no
port-range validation (a bad port either error-loops the unit or is silently
swallowed), ingress mutual exclusion is only lazily enforced, the charm shows
`active` while the workload is crash-looping, and `WORKLOAD_VERSION` is 12 minor
releases behind the actual image. Status reporting also lags badly — the charm sits
in `maintenance` most of the time because only `update-status` (up to 5 minutes
later) restores `ActiveStatus`, and this cascades with temporal-k8s to delays over
10 minutes. Docs have several stale/wrong details (charmhub link, README
`server-name` note, Terraform variable name). A maintainer should fix the port
validation and the maintenance/active status gap first — both are cheap fixes with
outsized operator impact — then add the missing pebble-check-failed observer and
correct the hardcoded workload version.

| | |
|---|---|
| Repo | canonical/temporal-ui-k8s-operator @ `3028c00` (2026-04-30) |
| Charms | temporal-ui-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), 1.23/stable rev 31; deep-tested with temporal-k8s 1.23/edge rev 71, postgresql-k8s 14/stable rev 925, nginx-ingress-integrator latest/edge rev 490 |
| Reviewed | 2026-07-26 |

## What it does

A Kubernetes sidecar charm deploying the Temporal Web UI OCI image
(`temporalio/ui`). It renders a YAML config file from a Jinja2 template, pushes it
to the workload container at `/home/ui-server/config/charm.yaml`, and manages the
`ui-server` process via Pebble. It relates to the Temporal server charm over `ui`
(provides) and `temporal-host-info` (requires) to discover the gRPC server address.
Ingress is handled via either nginx-ingress-integrator (`nginx-route`) or Traefik
(`ingress`), with mutual exclusion intended (though lazily enforced — see
findings). OIDC authentication and various UI feature toggles are supported.

## Deployment log

### Juju 3.6 full-stack deploy (concierge-k8s-3, model `rv-tui3`)

```bash
juju add-model rv-tui3
juju deploy temporal-ui-k8s --channel 1.23/stable        # rev 31
juju deploy temporal-k8s --channel 1.23/edge --config num-history-shards=1  # rev 71
juju deploy temporal-admin-k8s --channel 1.23/edge        # rev 28
juju deploy postgresql-k8s --channel 14/stable --trust     # rev 925
juju deploy nginx-ingress-integrator --channel latest/edge # rev 490

juju integrate temporal-k8s:db postgresql-k8s:database
juju integrate temporal-k8s:visibility postgresql-k8s:database
juju integrate temporal-k8s:admin temporal-admin-k8s:admin
juju integrate temporal-ui-k8s:ui temporal-k8s:ui
juju integrate temporal-ui-k8s:temporal-host-info temporal-k8s:temporal-host-info
```

Stack reached active at ~17:36, then `ui-relation-changed` fired at 17:36:26,
re-setting temporal-ui-k8s to `maintenance`. Finally reached active at 17:41:25
(next `update-status` interval). Confirmed HTTP 200 on port 8080, Pebble health
checks passing every 10s.

### Juju 4.0 (concierge-k8s-4, abandoned)

```bash
juju add-model rv-tui4-deep
juju deploy temporal-ui-k8s --channel 1.23/stable
# → blocked "ui:temporal relation: not available" (expected)
```

Full-stack deploy on Juju 4.x blocked by postgresql-k8s (all channels require
`juju < 4.0.0`). Charm itself works on Juju 4.x in isolation. This model was used
to confirm `pebble-check-failed` fires during initial deploy (with no observer,
the hook is a no-op), and that the restart action on an unconfigured workload
fails with `ChangeError`.

## Observed behaviour

### Status stuck in maintenance between `_update` and `update-status`
Every `_update()` and `_on_restart()` call sets `MaintenanceStatus`. The only path
to `ActiveStatus` is `_on_update_status` (`src/charm.py:208-211`), which fires
every 5 minutes by default. Quantified this round: the charm was `active` for
~9 seconds (17:36:17 to 17:36:26) before a `ui-relation-changed` event fired and
re-set it to `maintenance`. The next `update-status` at 17:41:17 restored `active`
— a ~5 minute gap.

### Cascading status delay with temporal-k8s
temporal-k8s has the same maintenance-stuck pattern. Its `ui` relation
`server_status` is set to "ready" only on its own `update-status`. When
temporal-k8s's status changes, a `ui-relation-changed` event fires on
temporal-ui-k8s, which calls `_update()`, re-setting `MaintenanceStatus` and
undoing the `ActiveStatus` the previous `_on_update_status` had just set.
End-to-end delay from both workloads healthy to both charms showing `active` can
exceed 10 minutes.

### Port=99999 causes hook failure, not BlockedStatus
No port-range validation exists anywhere. The Pebble layer is written with the
invalid port, the service crashes, and `config-changed` fails 3 times before the
unit enters `error` state. Operator sees `"hook failed: config-changed"` with no
actionable message. Resetting to a valid port recovers. Replicated on both Juju
3.6 and 4.x.

### Port=0 silently accepted
`juju config port=0` was accepted and written into the Pebble layer. Jinja2
renders `port: 0` in the config file. The workload apparently ignores the
invalid port (uses its default 8080), since the health check
`http://localhost:0/` showed 3 successes — likely the ui-server listening on its
default instead. The charm neither validates nor warns.

### Crash loop invisible to charm
After 5 rapid kills (0.5s intervals), Pebble restarted the service after each
kill without the charm noticing. The charm showed `active` throughout. With
`on-check-failure: ignore`, Pebble never surfaces the check as consistently DOWN,
and no `pebble-check-failed` observer is registered. This round, the
`pebble-check-failed` hook was confirmed to fire at 17:31:02 during initial
deploy (service failed because no config file was yet present), but with no
observer it was a no-op.

### Mutual ingress exclusion not enforced at integration time
Adding `nginx-route` while `traefik` ingress is present (or vice versa) is
silently accepted. The `nginx-route` relation-changed event does not trigger
`_update()`/`_validate()`. The violation is only caught when an unrelated event
(config change, update-status, etc.) fires. Removing the violating relation does
not clear the blocked status until another event triggers validation.

### Nginx-route data IS written correctly (corrected from an earlier finding)
The `NginxRouteRequirer` correctly writes application data to the `nginx-route`
relation. Confirmed by reading the nginx-ingress-integrator side of the relation:
`backend-protocol: HTTP`, `service-hostname: temporal-ui-k8s`,
`service-name: temporal-ui-k8s`, `service-port: 8080`,
`tls-secret-name: temporal-tls`. The `application-data: {}` seen on the
temporal-ui-k8s side is nginx-ingress-integrator's own (empty) app data, not the
charm's. `_config_reconciliation` works correctly on relation-changed.

### Restart action succeeds on previously-active charms but fails on uninitialized workloads
On a charm that has been active (Pebble plan exists), the restart action returns
`"worker successfully restarted"` even if the charm is currently `blocked` due to
a missing relation — the service restarts and recovers. On a freshly deployed
charm that has never pushed a Pebble plan, the restart action crashes with
`ChangeError: "cannot perform the following tasks: Start service 'temporal-ui'
(exited quickly with code 1)"`. No validation of Pebble plan existence before
attempting restart.

### Pod restart recovery
`kubectl delete pod` → pod restarted, `pebble-ready` fired, service active within
~5s, HTTP 200 confirmed. Charm recovered through `maintenance` → `active`
correctly.

### Resource usage
`kubectl top pod` showed 41Mi memory and 3m CPU (quiescent). Pebble health checks
run every 10s (matching the layer's "10s" period), logging 200 responses with
~120µs latency.

### Charm size
5.5MB packed (ubuntu@24.04); rev 31 is 5MB.

### Workload container state
Pebble plan has two checks: `temporal-ui-running` (pgrep, from rock image,
threshold=3) and `up` (HTTP GET on `/`, from charm, period=10s,
`on-check-failure: ignore`, threshold=3). Config at
`/home/ui-server/config/charm.yaml` owned by root:root (644). Actual image
version: `ui-server --version` reports "Temporal UI version 2.39.0". Resource
`upstream-source` comment says `2.39-24.04`. Charm reports `2.27.1`.

### Pebble check recovery
`temporal-ui-pebble-check-recovered` fired at 17:36:32 after the initial
failures. No observer registered — the framework dispatches it as a no-op hook.

## Findings

### No port-range validation — bad config causes error state or silent acceptance
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:279-303` (`_validate`), `config.yaml:44-49` (port option)
- **Evidence**: `config.yaml` declares `port` as `type: int` with no
  `minimum`/`maximum`. `_validate()` checks auth params, ingress mutual
  exclusion, and relations but not port range. `port=99999` was accepted,
  written into the Pebble layer, and crashed the workload with
  `"listen tcp: address 99999: invalid port"`; `config-changed` failed 3 times
  and the unit entered `error`. `port=0` was silently accepted and written into
  the Pebble check URL `http://localhost:0/` — the workload apparently used its
  default port instead. Replicated on Juju 3.6. Also: `log-level=INVALID` was
  silently accepted — no enum constraint in `config.yaml`.
- **Impact**: A fat-fingered port value puts the charm into `error` state with
  only `"hook failed: config-changed"` shown. `port=0` silently produces a
  configuration that doesn't match the operator's intent. The same class of bug
  applies to `log-level`, which has no enum constraint despite its description
  listing valid values.
- **Fix**: Add `minimum: 1` and `maximum: 65535` to `port` in `config.yaml`. Add
  `enum: [info, debug, warning, error, critical]` to `log-level`, or validate
  both in `_validate()`.
- **Linter rule**: "config option of type `int` used as a port without
  `minimum`/`maximum` constraints" — mechanically checkable. "config option of
  type `string` with description listing acceptable values lacks `enum`
  constraint" — mechanically checkable.

### Mutual ingress exclusion not enforced — nginx-route events invisible to validation
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:59-99` (`__init__`), `src/charm.py:296` (ingress
  mutual-exclusion check in `_validate`)
- **Evidence**: The charm registers no observers for nginx-route relation events
  at the charm level. `_require_nginx_route` (called from `__init__`) only
  writes data to the relation (confirmed working correctly). The mutual-exclusion
  check at line 296 is only reached via `_update`, which nginx-route events don't
  trigger. Observed live: adding `nginx-route` while traefik ingress was present
  was silently accepted, charm stayed `active`; the violation was only caught on
  a subsequent `juju config` call. After removing `nginx-route`, the charm stayed
  `blocked` because nothing re-ran `_update()`. `test_blocked_on_two_ingresses`
  only covers both relations present at `pebble-ready` time, not one added after
  the other.
- **Impact**: An operator can add two ingress solutions with no immediate
  feedback; the charm blocks only on the next unrelated event, and removing the
  offending relation doesn't clear the block until another event fires.
- **Fix**: Observe nginx-route relation events and call `_update()` from the
  handler, e.g. `self.framework.observe(self.on["nginx-route"].relation_changed,
  self._update)` and similarly for `relation_broken`. Also call
  `_require_nginx_route()` from the handler to keep relation data fresh on
  config changes.
- **Linter rule**: "charm calls `require_nginx_route()` in `__init__` but does
  not observe nginx-route relation events" — mechanically checkable.

### Status stuck in maintenance between `_update` and `update-status` (also affects restart action)
- **Severity**: high
- **Kind**: ux
- **Where**: `src/charm.py:307-402` (`_update`), `src/charm.py:180`
  (`_on_restart`), `src/charm.py:186-211` (`_on_update_status`)
- **Evidence**: `_update()` unconditionally ends with
  `self.unit.status = MaintenanceStatus("replanning application")`.
  `_on_restart()` sets `MaintenanceStatus("restarting ui")`. Only
  `_on_update_status` (line 208-211) sets `ActiveStatus`, and it fires every 5
  minutes. After every config change, relation change, restart action, refresh,
  or pebble-ready, the charm shows `maintenance` for up to 5 minutes. Quantified
  this round: `active` for ~9 seconds (17:36:17-17:36:26) before a
  `ui-relation-changed` event re-set it to `maintenance`; next `update-status` at
  17:41:17 restored `active`. Cascading interaction with temporal-k8s (same
  pattern) pushes the end-to-end delay past 10 minutes.
- **Impact**: Operators watching `juju status`, and external monitoring reading
  it, see the charm as unhealthy most of the time.
- **Fix**: After `container.replan()`, check whether the service and check are
  up (as `_on_update_status` already does) and set `ActiveStatus` immediately if
  so, or emit a custom event to trigger immediate status re-evaluation.
- **Linter rule**: "hook handler unconditionally sets MaintenanceStatus without
  a path to ActiveStatus within the same hook or an immediate event emission" —
  partially checkable.

### Pebble crash loop invisible to charm — no observer for pebble-check-failed
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:59-99` (`__init__`), `src/charm.py:376-395` (Pebble
  layer), `src/charm.py:387` (`on-check-failure: ignore`)
- **Evidence**: No observer for `pebble-check-failed` or `pebble-check-recovered`.
  The layer sets `"on-check-failure": {"up": "ignore"}` (line 387). After killing
  `ui-server` 5 times rapidly, Pebble recovered the service each time and the
  charm showed `active` throughout. `juju debug-log` confirmed
  `temporal-ui-pebble-check-failed` fired at 17:31:02 UTC during initial deploy
  (missing config file) and `temporal-ui-pebble-check-recovered` fired at
  17:36:32 — both no-ops since no observer is registered.
- **Impact**: A repeated crash loop is invisible until the next
  `update-status` (up to 5 minutes later), and only if the check happens to be
  DOWN at that exact moment. With `on-check-failure: ignore`, the check may never
  register DOWN during a crash loop that recovers before the threshold is hit.
- **Fix**: Observe `pebble-check-failed`/`pebble-check-recovered`; set
  `MaintenanceStatus`/`WaitingStatus` on failure, track consecutive failures, and
  surface crash loops. Consider tightening or removing `on-check-failure: ignore`.
- **Linter rule**: "charm registers pebble_ready observer but not
  pebble-check-failed or pebble-check-recovered" — mechanically checkable.

### Restart action does not validate Pebble plan before restarting
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:169-183` (`_on_restart`)
- **Evidence**: `_on_restart` checks `container.can_connect()` but not whether
  the Pebble service is configured. On a freshly deployed (never-configured)
  charm, the action starts the service, which crashes with
  `"config file corrupted: no config files found within config"`; the operator
  gets a `ChangeError` traceback. On Juju 4.x: `"cannot perform the following
  tasks: Start service 'temporal-ui' (service start attempt: exited quickly with
  code 1, will restart)"`. On a previously-active charm (even if currently
  blocked), restart succeeds because the Pebble plan already exists.
- **Impact**: Running restart before the charm is fully configured produces a
  cryptic Pebble error instead of a clear message.
- **Fix**: Call `self._validate_pebble_plan(container)` before restarting, and
  `event.fail("Cannot restart: workload is not yet configured")` if invalid.
- **Linter rule**: "action handler calls container.start/restart/stop without
  prior pebble plan validation" — mechanically checkable.

### Restart action defers silently when container not ready
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:175-177`
- **Evidence**: When `container.can_connect()` returns False, the action defers
  without setting any event result. Line 176: `event.defer()` with no
  `event.set_results()`/`event.fail()` before it.
- **Impact**: Action output is empty, giving the operator no indication the
  restart didn't complete.
- **Fix**: Add `event.set_results({"result": "deferred: workload container not
  ready"})` or `event.fail(...)` before deferring.
- **Linter rule**: "action handler defers without setting event results or
  calling event.fail()" — mechanically checkable.

### Hardcoded WORKLOAD_VERSION is 12 minor versions behind actual image
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:25` (`WORKLOAD_VERSION = "2.27.1"`),
  `metadata.yaml:60` (`upstream-source: ... 2.39-24.04`)
- **Evidence**: The running container reports "Temporal UI version 2.39.0"
  (`ui-server --version`). The resource `upstream-source` comment says
  `2.39-24.04`. `juju status` shows `2.27.1` for both rev 31 and rev 32.
- **Impact**: Operators cannot determine the actual deployed workload version
  from `juju status`; if the OCI resource is upgraded without a charm code
  change, the reported version stays wrong indefinitely.
- **Fix**: Query the workload at runtime (e.g. `ui-server --version` at startup
  or parse Pebble service output) and call
  `self.unit.set_workload_version(actual_version)`.
- **Linter rule**: "WORKLOAD_VERSION constant defined at module level instead of
  being queried from workload" — mechanically checkable.

### Charmhub docs mismatch — discourse topic #9232 describes admin-tools, not web UI
- **Severity**: medium
- **Kind**: docs
- **Where**: `metadata.yaml:17` →
  `docs: https://discourse.charmhub.io/t/temporal-ui-documentation-overview/9232`
- **Evidence**: The linked topic says "This operator provides the Temporal admin
  tools, and consists of Python scripts which wraps the versions distributed by
  temporalio (admin-tools)". The charm is the web UI charm; the README correctly
  describes the web UI but the charmhub docs link points elsewhere.
- **Impact**: Operators following the charmhub docs link land on instructions for
  a different charm.
- **Fix**: Update discourse topic #9232, or create a new topic and point
  `metadata.yaml` at it.
- **Linter rule**: not established.

### README describes deprecated `server-name` that has never existed in this charm
- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md:25-31`
- **Evidence**: README states "If relation data is unavailable, the deprecated
  `server-name` config option is used..." and that it "will be removed in a
  future release." `server-name` does not appear in `config.yaml`,
  `src/charm.py`, or any code file; `git log --all -- config.yaml` shows no
  evidence it ever existed here. `TemporalHostInfoRequirer` is the sole source of
  the server address. Issue #14 (2025-08-12) confirms the temporal-k8s app name
  was previously hardcoded, resolved by adding the temporal-host-info relation in
  commit `e659f68`; the README text is likely a leftover from that era.
- **Impact**: Operators may try to use a config option that doesn't exist, and
  the README describes a migration that's already complete.
- **Fix**: Remove the `server-name` deprecation note from the README.
- **Linter rule**: not established.

### Nginx-route data not re-evaluated after config changes
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:84-108` (`_require_nginx_route`),
  `src/charm.py:59-99` (`__init__`)
- **Evidence**: `_require_nginx_route()` is called exactly once, from
  `__init__`. If `external-hostname` or `tls-secret-name` changes, the
  nginx-route data isn't updated because `_update()` doesn't call
  `_require_nginx_route()`. The initial write is correct (confirmed this round);
  the gap is only re-evaluation after config changes.
- **Impact**: Config changes to `external-hostname`/`tls-secret-name` aren't
  reflected in the relation data until the next `relation-changed` event, which
  may never fire.
- **Fix**: Call `_require_nginx_route()` from `_update()` or
  `_on_config_changed` when relevant config changes.
- **Linter rule**: not established.

### Integration test `test_ingress` (scenario) calls `_require_nginx_route()` manually — not representative of runtime
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/scenario/test_charm.py:68-104`
- **Evidence**: The test calls `manager.charm._require_nginx_route()` directly
  rather than through normal event flow; production code only calls it from
  `__init__`. The test therefore exercises code the runtime never re-invokes
  after init, masking the missing re-evaluation on config-changed/upgrade-charm.
- **Impact**: The test passes but doesn't validate actual runtime behaviour and
  hides the nginx-route bug above.
- **Fix**: Add `_require_nginx_route()` to `_on_config_changed`/`_update()` and
  test through those paths, or remove the manual call.
- **Linter rule**: not established.

### `TemporalHostInfoRequirer.port` property can raise ValueError on malformed port
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/temporal_k8s/v0/temporal_host_info.py:197`
- **Evidence**: `.port` property calls `return int(port_str)` with no
  try/except. `_update()` (line 368) uses `self.host_info.port` unguarded.
  `_on_host_info_relation_changed` (line 215) catches `KeyError` but not
  `ValueError` around `int(app_data["port"])`.
- **Impact**: A misbehaving or compromised provider could crash the requirer
  charm with an unhandled `ValueError`.
- **Fix**: Wrap `int(port_str)` in try/except ValueError, return None on
  failure; also catch ValueError in `_on_host_info_relation_changed`.
- **Linter rule**: "unchecked `int()` conversion on relation data value" —
  mechanically checkable.

### `_validate_pebble_plan` catches broad exception types
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:225`
- **Evidence**: `except (KeyError, pebble.ConnectionError): return False`
  treats a missing key (plan not yet applied) the same as a Pebble connection
  error, though these mean different things.
- **Impact**: A genuine Pebble connectivity issue is silently reported as an
  invalid plan; practical impact limited since the caller (`_on_update_status`,
  line 199) subsequently calls `_update()`, which checks `can_connect()` anyway.
- **Fix**: Separate the two cases or add a clarifying comment.
- **Linter rule**: not established.

### Terraform README input name `model` vs actual variable `model_uuid`
- **Severity**: low
- **Kind**: docs
- **Where**: `terraform/README.md` (input table), `terraform/variables.tf:13`
- **Evidence**: README lists input `model` (string, required, "Name of the model
  that the charm is deployed on"). `variables.tf` actually defines `model_uuid`
  ("UUID of Juju model where the application is to be deployed"). README usage
  examples use `model = ...`, which fails with "No variable named 'model'".
- **Impact**: Copy-pasting the README example produces a Terraform error; even
  correctly guessing `model_uuid`, an operator might supply a name instead of a
  UUID.
- **Fix**: Update README to reference `model_uuid` and describe it as a UUID.
- **Linter rule**: not established.

### Restart action returns wrong workload name
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:183`
- **Evidence**: `event.set_results({"result": "worker successfully restarted"})`
  — the charm deploys `ui-server`, not a "worker"; a copy-paste artifact from
  another charm.
- **Fix**: Change to `"temporal-ui successfully restarted"`.
- **Linter rule**: not established.

### No `pyrightconfig.json` or `mypy.ini` in repo
- **Severity**: nit
- **Kind**: lint
- **Where**: repo root
- **Evidence**: Neither file exists. The tox lint target runs mypy with
  `--ignore-missing-imports --follow-imports=skip --install-types
  --non-interactive` but no project-specific configuration; pyright isn't in the
  tox lint flow.
- **Impact**: Type-checking quality is degraded without project config.
- **Fix**: Add a `pyrightconfig.json` or `mypy.ini` with appropriate settings.
- **Linter rule**: not established.

### Ruff lint: 3 distinct issues in integration tests (not src/ or lib/)
- **Severity**: nit
- **Kind**: lint
- **Where**: `tests/integration/test_charm.py:115,120,137,150,179`,
  `tests/integration/test_traefik_ingress.py:80`
- **Evidence**: `ruff check tests/` found 7 issues: unused `# noqa: F821`
  directives (2), async functions calling blocking `requests.get()` (3), unused
  unpacked variables (2). `src/` is clean; `lib/` has 98 issues
  (annotation-modernization on vendored libraries, not actionable).
- **Fix**: Remove unused noqa directives, use `httpx`/`asyncio.to_thread` for
  HTTP calls in async tests, prefix unused variables with `_`.
- **Linter rule**: already caught by ruff.

### No scenario tests for restart action, config-changed, or nginx-route events
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/scenario/test_charm.py`
- **Evidence**: No test covers: restart action success path; restart action
  with an invalid Pebble plan; port out of range; invalid log-level;
  config-changed with auth partially configured; nginx-route
  relation-changed/relation-broken handling. 13 tests currently pass in 0.28s
  (blocked states, ready state, auth config, update-status up/down, incomplete
  Pebble plan recovery, traefik ingress).
- **Impact**: Three high-severity bugs (port range, restart-without-plan,
  mutual-exclusion bypass) and the maintenance-status UX issue went uncaught by
  existing tests.
- **Fix**: Add scenario tests for restart action (success and failure), invalid
  config values, and nginx-route relation events.
- **Linter rule**: not established.

### Integration tests use both jubilant and pytest-operator — migration in progress
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/conftest.py` (jubilant),
  `tests/integration/test_charm.py` (pytest-operator),
  `tests/integration/test_refresh.py` (jubilant)
- **Evidence**: Open issue #50 tracks the needed migration; `test_refresh.py`
  and `conftest.py` use jubilant, `test_charm.py`/`test_traefik_ingress.py` use
  the deprecated pytest-operator.
- **Impact**: Deprecated pytest-operator tests may break with future Juju
  versions; two frameworks increase maintenance burden.
- **Fix**: Complete migration to jubilant per issue #50.
- **Linter rule**: not established.

### Integration test `test_refresh` targets `latest/edge` — expected to fail
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/test_refresh.py`; open issue #52 (2026-07-15)
- **Evidence**: Issue #52 states the refresh test will fail because
  `latest/stable` was recently closed.
- **Impact**: Expected-to-fail tests make CI unreliable.
- **Fix**: Update the test to use available channels, or skip it until
  channels are available.
- **Linter rule**: not established.

## Worth copying

- **Scenario-test-based state transition testing**: `tests/scenario/` uses
  `ops.testing.Context` throughout, covering blocked states, ready state, auth
  config, update-status up/down, incomplete Pebble plan recovery, and traefik
  ingress. 13 tests, all pass in 0.28s, good fixture setup in `conftest.py`.
- **State encapsulation via `State` class**: `src/state.py` wraps peer relation
  data access with JSON serialization behind a clean attribute-style API.
  `is_ready()` prevents accessing uninitialized peer data.
- **Clear validation in `_validate()`**: preconditions are checked in a single
  method that raises `ValueError` with human-readable messages; `_update`
  catches these and sets `BlockedStatus`. Clean separation of validation and
  action.
- **Config-to-environment mapping**: `src/charm.py:325-346` maps config keys to
  env var names via an explicit dict, easy to audit. Auth section handled as a
  conditional addition.
- **Proxy environment passthrough**: `src/charm.py:353-363` reads
  `JUJU_CHARM_HTTP_PROXY`, `JUJU_CHARM_HTTPS_PROXY`, `JUJU_CHARM_NO_PROXY` and
  passes them to the workload — good for air-gapped deployments.
- **`log_event_handler` decorator**: `src/log.py` logs entry/exit of every event
  handler with `* running`/`* completed` messages; try/finally ensures the exit
  log always fires.
- **Terraform module**: `terraform/` provides a complete module with inputs,
  outputs, README, and a `justfile` for convenient testing.

## Common-practice notes

- **Follows**: ops framework idiom of `__init__` observer registration,
  `_update` reconciliation pattern, Jinja2 template rendering, Pebble layer
  management.
- **Follows**: `charmcraft.yaml` `platforms: ubuntu@24.04:amd64`, `uv` build
  plugin, `astral-uv` build-snap — current standard for charmcraft 3.x.
- **Follows**: `lib/charms/` for shared libraries with `LIBID`/`LIBAPI`/
  `LIBPATCH` metadata; `temporal_host_info.py` (v0) is a clean in-project
  provider/requirer library.
- **Follows**: `metadata.yaml` `assumes: juju >= 3.1` — the ecosystem is
  standardizing on `>=3.4`/`>=3.5`. The charm works on Juju 4.x, but full-stack
  testing is blocked by postgresql-k8s (`juju < 4.0.0` requirement).
- **Drifts**: `_update` unconditionally sets `MaintenanceStatus`, relying on
  `update-status` to set `ActiveStatus`. Most charms set `ActiveStatus`
  immediately once the workload is confirmed running; the 5-minute gap here
  creates cascading delays across the temporal charm family (~9s active window
  observed this round).
- **Drifts**: `State` uses `json.dumps`/`json.loads` rather than ops framework
  built-in JSON utilities, storing values as JSON-encoded strings (e.g.
  `server_status: '"ready"'`).
- **Notable absence**: no Juju secrets usage — `auth-client-secret` is passed as
  a plain environment variable, visible in `juju config` output.
- **Notable absence**: no observer for `pebble-check-failed`/
  `pebble-check-recovered`. Pebble auto-restarts on crash, but the charm has
  zero visibility into crash loops within a 5-minute update-status window.
- **Juju 4.x compatibility**: the charm itself works on Juju 4.0.5; full-stack
  testing is blocked by an ecosystem dependency (postgresql-k8s), not a charm
  defect.

## Tests

### Unit/scenario tests (13 tests, all pass)
```
tests/scenario/test_charm.py::test_smoke PASSED
tests/scenario/test_charm.py::test_blocked_by_temporal_server PASSED
tests/scenario/test_charm.py::test_blocked_when_host_info_absent PASSED
tests/scenario/test_charm.py::test_blocked_by_peer_relation_not_ready PASSED
tests/scenario/test_charm.py::test_ingress PASSED
tests/scenario/test_charm.py::test_ready PASSED
tests/scenario/test_charm.py::test_auth PASSED
tests/scenario/test_charm.py::test_update_status_up PASSED
tests/scenario/test_charm.py::test_update_status_down PASSED
tests/scenario/test_charm.py::test_incomplete_pebble_plan PASSED
tests/scenario/test_charm.py::test_missing_pebble_plan PASSED
tests/scenario/test_charm.py::test_blocked_on_two_ingresses PASSED
tests/scenario/test_charm.py::test_traefik_ingress_ready PASSED
```

Run: `PYTHONPATH=.:lib:src uv run pytest tests/scenario/ -v`. All pass in 0.28s.
Dependencies: `ops[testing]==2.21.1`, `pytest==7.1.3`, `pydantic>=2`,
`Jinja2==3.1.1`.

### Integration tests (not run — require k8s cluster with nginx ingress controller)
- `test_charm.py`: pytest-operator. Full temporal stack + nginx-ingress-integrator.
  Tests HTTP GET, ingress, restart action, scaling, host-info relation,
  relation removal.
- `test_traefik_ingress.py`: pytest-operator. Temporal stack + traefik-k8s.
- `test_refresh.py`: jubilant. Deploys from `latest/edge`, refreshes to local
  charm. Known to fail (issue #52).
- CI: `juju-channel: 3.6/stable`, `channel: 1.33-classic/stable`,
  `charmcraft-channel: latest/candidate`.

### Coverage gaps (from code review and runtime testing)
- No test for port out of range (port=99999 → error state, port=0 silently accepted)
- No test for invalid log-level config (accepted silently)
- No test for restart action (success or failure path)
- No test for restart action deferral when container not ready
- No test for nginx-route relation-changed/relation-broken events
- No test for nginx-route data re-send on config-changed or upgrade-charm
- No test for pebble-check-failed/pebble-check-recovered event handling
- No test for crash-loop scenario (Pebble backoff + charm remaining active)
- No test for mutual-exclusion violation when nginx-route is added after traefik
- No test for config-changed events

### Linters
- `ruff check src/`: all checks pass
- `ruff check tests/`: 7 issues (unused noqa, async/blocking HTTP, unused variables)
- `ruff check lib/`: 98 issues (annotation modernization in vendored libraries)
- `codespell`: clean on source code

## Docs

- **README.md**: mostly accurate. Stale `server-name` deprecation note (never
  existed in this charm). The "Temporal endpoint resolution" section is helpful
  but partially outdated — `temporal-host-info` is the sole server-address
  source, but the README still references the deprecated `server-name` path.
- **CONTRIBUTING.md**: brief, points to the temporal server charm for deploy
  instructions; tox commands listed are correct.
- **Charmhub docs**: linked discourse topic #9232 describes the admin-tools
  charm, not the web UI — significant mismatch.
- **Terraform README**: good API documentation with usage examples, but input
  `model` should be `model_uuid` — a doc/code mismatch that causes Terraform
  errors; description also wrong ("name" vs UUID).
- **No `docs/` directory**: all documentation lives in README.md and the
  terraform README.
- **`config.yaml` comments**: the `log-level` description says "gunicorn" but
  the workload is a Go binary (`ui-server`) — a copy-paste artifact.

## Open questions

1. **Is the `server-name` config option deliberately absent?** Confirmed: no
   git history shows `server-name` ever existing in this charm's `config.yaml`.
   Issue #14 (2025-08-12) confirms the temporal-k8s app name was previously
   hardcoded, resolved by adding the temporal-host-info relation. The README
   text appears to be a leftover from that transition.
2. **Should the charm observe `pebble-check-failed`?** Confirmed yes —
   `pebble-check-failed` fires on both Juju 3.6 and 4.x but with no observer is
   a no-op. With `on-check-failure: ignore`, the check may never register DOWN
   during a crash loop that recovers before the next update-status.
3. **Why is the `log-level` description in `config.yaml` wrong?** It says
   "Configures the log level of gunicorn" but the workload is a Go binary
   (`ui-server`), not a Python/gunicorn app — a copy-paste artifact.
4. **Does the template render correctly with auth-enabled=false?** Yes —
   Jinja2's default `Undefined` type silently renders empty strings for
   undefined variables (confirmed with Jinja2 3.1.1). The auth section renders
   with empty values, but since `enabled: false` the workload ignores them.
   Not a bug, but produces messy config files.
