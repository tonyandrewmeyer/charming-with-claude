# jenkins-k8s

A well-structured k8s charm with a clean reconciliation pattern, comprehensive test coverage (309 passing unit tests, 98% branch coverage on `src/`, clean `ruff` on `src/`), and a solid state model. The published **stable** release (rev 201) is ten months behind HEAD: it lacks JCasC — the charm's flagship configuration mechanism — and carries a sticky-blocked-status bug and a Pebble health-check bug that are both fixed in **edge** (rev 338). Edge itself has two serious defects: a spacing bug in the Pebble command construction that silently drops the `-XX:MaxRAMPercentage=50.0` JVM flag whenever `system-properties` is set, and an unhandled `TimeoutError` in `wait_ready` that puts the charm into a permanent crash loop if JCasC config is cleared. Downgrading from edge to stable is also broken — it crash-loops on incompatible on-disk JCasC state. A maintainer should first fix the `wait_ready` crash loop and the Pebble command spacing bug, then promote a new stable release with JCasC support.

| | |
|---|---|
| Repo | canonical/jenkins-k8s-operator @ `1db52b1` (2026-07-23) |
| Charms | jenkins-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), latest/edge rev 338 (3 deployments: fresh, integration/refresh test, failure-injection); concierge-k8s-4 (Juju 4.0.5), stable rev 201 and edge rev 338 (earlier review pass) |
| Reviewed | 2026-08-04 |

## What it does

Deploys Jenkins on Kubernetes as a single unit. Manages the Jenkins workload container via Pebble, handles the OCI image (built with Rockcraft), installs required plugins, generates admin credentials stored in Juju secrets, and reconciles agent nodes from the `agent` relation. Integrations: ingress (traefik), auth-proxy (oauth2-proxy), COS (metrics, grafana dashboards, loki logging), HAProxy route, and a dedicated agent-discovery ingress. Actions: `get-admin-password`, `rotate-credentials`. Configuration-as-Code (JCasC) is the primary configuration mechanism in HEAD/edge (not present in stable rev 201): git-based JCasC repositories with auth tokens, environment-variable interpolation from Juju secrets, custom JVM system properties, and plugin allow-listing with automatic removal of unlisted plugins within a configurable restart window.

## Deployment log

### Deployment A — edge channel, Juju 3.6, fresh (`rv-jenkins-deep-4`)

```
juju switch concierge-k8s-3
juju add-model rv-jenkins-deep-4
juju deploy jenkins-k8s --channel edge          # rev 338, latest/edge, ubuntu@24.04
```

Charm went active; JCasC features present.

**Failure injections:**

- `juju config jenkins-k8s restart-time-range=99-100` → `BlockedStatus` "Invalid config value for restart-time range." (correct).
- `juju config jenkins-k8s restart-time-range=03-05` → recovered to active (correct).
- `juju config jenkins-k8s jcasc-environment-secrets="secret:not-a-real-secret-uri"` → Juju rejected at config level: "secret URI not valid" (correct).
- `juju config jenkins-k8s jcasc-repository="https://github.com/not/exists.git"` → `BlockedStatus` "jcasc-config and jcasc-repository are mutually exclusive; set only one" (correct — default `jcasc-config` must be cleared first).
- Cleared `jcasc-config`, set bad `jcasc-repository` → `BlockedStatus` "Failed to fetch JCasC repository configuration: Failed to clone repository https://github.com/not/exists.git" (correct, clear message).
- Cleared `jcasc-repository`, set `jcasc-config` to empty → **charm entered a crash loop** (see finding below). With both configs empty, `wait_ready` timed out after 300s and the uncaught `TimeoutError` crashed and restarted the hook, looping every ~310s indefinitely. A follow-up `juju config` with a valid `jcasc-config` did not break the loop — the config-changed event queued behind the crash-triggered events and was never processed.
- **Model destroyed after ~20 minutes of crash looping.**

### Deployment B — edge channel, Juju 3.6, fresh + refresh (`rv-jenkins-deep-36`)

```
juju switch concierge-k8s-3
juju add-model rv-jenkins-deep-36
juju deploy jenkins-k8s --channel edge          # rev 338
```

- Charm went active.
- `juju config jenkins-k8s system-properties="-XX:InvalidFlag"` → `BlockedStatus` "Invalid system-properties entry; expected key=value pairs separated by commas." (correct).
- `juju config jenkins-k8s system-properties=""` → recovered to active (correct).
- `juju ssh --container jenkins jenkins-k8s/0 "pkill -f jenkins.war"` → Pebble auto-restarted Jenkins within ~15s, charm remained active (correct).
- `juju relate jenkins-k8s:ingress traefik-k8s:ingress` → established, charm active.
- `juju relate jenkins-k8s:metrics-endpoint grafana-agent-k8s` → established, charm active.
- `juju remove-relation jenkins-k8s:ingress traefik-k8s:ingress` → charm active, handled gracefully.
- `juju remove-relation jenkins-k8s:metrics-endpoint grafana-agent-k8s` → charm active, handled gracefully.

**Refresh test (edge → stable downgrade):**

- `juju refresh jenkins-k8s --channel latest/stable` → downgraded to rev 201.
- **Charm entered a crash loop.** Rev 201 repeatedly failed with "Failed to bootstrap Jenkins" and "Uncaught exception while in charm code". Root cause: edge-generated JCasC state on disk is incompatible with stable code, which has no JCasC handling. After several cycles the charm reached `ErrorStatus` with "hook failed: update-status" — see finding.
- Model destroyed.

### Earlier deployments (first review pass)

### Deployment 1 — stable channel, Juju 4.x

```
juju switch concierge-k8s-4
juju add-model rv-jenkins-k8s
juju deploy jenkins-k8s --channel stable         # rev 201, latest/stable, ubuntu@24.04
```

- Container image pull took ~3 minutes.
- Pebble-ready hook ran at 20:08:16, charm active at 20:09:02.
- Version reported: `2.516.3` (HEAD `rockcraft.yaml` specifies 2.555.1).
- `juju run jenkins-k8s/0 get-admin-password` → succeeded, returned hex password.
- `juju run jenkins-k8s/0 rotate-credentials` → succeeded, sessions invalidated, new password returned.
- `juju config jenkins-k8s restart-time-range=99-100` → `BlockedStatus` (correct).
- `juju config jenkins-k8s restart-time-range=03-05` → stayed blocked (bug; fixed in edge).
- `juju config jenkins-k8s restart-time-range=""` → still blocked; config-changed fired but status never updated.
- `juju relate jenkins-k8s:ingress traefik-k8s:ingress` → recovered to active. Only the unrelated relation event unstuck it.
- `kubectl exec ... -- pkill -f jenkins.war` → Pebble restarted Jenkins, back to active in ~15s.
- `juju config jenkins-k8s jcasc-config` → key not found — confirms stable rev 201 has no JCasC options.

### Deployment 2 — edge channel, Juju 4.x

```
juju switch concierge-k8s-4
juju add-model rv-jenkins-edge
juju deploy jenkins-k8s --channel edge          # rev 338 (HEAD), latest/edge, ubuntu@24.04
```

- Charm active. JCasC env vars present: `CASC_JENKINS_CONFIG`, `JENKINS_ADMIN_PASSWORD`, `CONFIGURATION_HASH`.
- `jenkins.yaml` written to `/var/lib/jenkins/jenkins.yaml` with merged JCasC.
- Pebble health-check URL is `http://localhost:8080` (root URL, not login page — fixes issue #419).
- `juju config jenkins-k8s jcasc-config='invalid yaml'` → `BlockedStatus` "Invalid jcasc-config YAML: mapping values are not allowed here" (correct).
- `juju config jenkins-k8s jcasc-config=''` → recovered to active.
- `juju config jenkins-k8s jcasc-config='jenkins:\n  systemMessage: "TEST CHANGE"'` → full reconcile, `jenkins.yaml` rewritten, Pebble re-planned, ~60s to active.
- `juju config jenkins-k8s jcasc-config='this is not valid yaml: : :'` → `BlockedStatus` with clear message (correct).

### Deployment 3 — edge channel, Juju 3.6

```
juju switch concierge-k8s-3
juju add-model rv-jenkins-36
juju deploy jenkins-k8s --channel edge          # rev 338
```

- Charm active; same JCasC features as Juju 4.x deployment.
- `restart-time-range=99-100` → `BlockedStatus` (correct).
- `restart-time-range=03-05` → **recovered to active** (confirmed fixed in edge/HEAD).
- `system-properties=jenkins.model.Jenkins.crumbIssuerProxyCompatibility=true` → charm restarted and recovered to active.
- `rotate-credentials` → succeeded, new password returned.
- `juju add-unit jenkins-k8s` (scale to 2) → `jenkins-k8s/1` → `BlockedStatus` "The Jenkins charm supports only 1 unit of deployment." (correct); unit 0 stayed active. Scaled back to 1 successfully.
- Killed `jenkins.war` → Pebble auto-restarted within ~15s, remained active.
- `juju relate jenkins-k8s:metrics-endpoint grafana-agent-k8s` → established successfully.

## Observed behaviour

### Stable rev 201

- Deploy time: ~3 min from `juju deploy` to active (mostly OCI image pull).
- Memory: ~617 MiB for the jenkins container (no resource limits). Charm container: 1 GiB limit, 64 MiB request.
- Pebble plan: only `JENKINS_HOME` / `JENKINS_PREFIX`; no JCasC env vars.
- Pebble check uses `http://localhost:8080/login?from=%2F` (login page URL).
- No `jenkins.yaml` on disk.
- Disk-space warning: Jenkins logs "Only 0.729 Gb free" with default 1 GiB storage.
- Stuck-blocked bug: invalid config → correct config does not recover on config-changed; only an unrelated event (relation join) unsticks it.
- Recovery from workload kill: Pebble auto-restart within ~15s, remained active.

### Edge rev 338 (HEAD)

- JCasC env vars present: `CASC_JENKINS_CONFIG`, `JENKINS_ADMIN_PASSWORD`, `CONFIGURATION_HASH`.
- `jenkins.yaml` written to `/var/lib/jenkins/jenkins.yaml` with merged charm-managed + user-provided JCasC.
- Pebble health check fixed: uses root URL `http://localhost:8080` instead of login page (resolves issue #419).
- Config recovery works: invalid → `BlockedStatus` → correct → active on every config-changed.
- Invalid JCasC YAML caught by `_parse_jcasc_config`, mapped to `BlockedStatus` with clear message; recovery works.
- Semantically-invalid JCasC (parses, but produces a Jenkins configuration that won't start) causes Jenkins to serve 503. `wait_ready` times out after 300s with no interim status update; `BlockedStatus` only appears after the timeout.
- System-properties applied — `-D` flags appear on the Java command line, but a spacing bug drops `-XX:MaxRAMPercentage` when they are set (see findings).
- Scale-to-2: second unit → `BlockedStatus`; unit 0 stays active.
- Actions `get-admin-password` and `rotate-credentials` work correctly on both Juju versions.

### Integration and lifecycle behaviour (edge rev 338, Juju 3.6)

- Relation add/remove for `ingress` (traefik) and `metrics-endpoint` (grafana-agent) causes no disruption; relation data published/retracted correctly.
- Killing `jenkins.war` → Pebble auto-restarts within ~15s; charm remains active and `pebble-check-failed` triggers a successful health check.
- Scaling to 2 units → second unit blocked, first stays active.
- Invalid `system-properties` correctly blocks with a clear message; recovers on clearing.
- Invalid secret URIs for `jcasc-environment-secrets` rejected by Juju before the charm sees them.
- Invalid `jcasc-repository` URL → `BlockedStatus` with git error detail; valid repo recovers. Mutual exclusivity of `jcasc-config`/`jcasc-repository` enforced in `State.from_charm`.
- Refresh/downgrade from edge to stable is broken (see finding).

### Juju 3.6 vs 4.x differences

- On Juju 3.6, the charm's `logger.info()` calls ("Reconciling storage", "Getting jenkins version", "phase=wait_ready start", etc.) appear in `juju debug-log` as `unit.jenkins-k8s/0.juju-log` entries. On Juju 4.x these are absent — only `juju.worker.uniter` and `container-agent` logs appear. This is a Juju 4.x platform behaviour change, not a charm defect, but it affects operator debuggability.
- No other Juju-version-specific behaviour differences observed.

## Findings

### 1. Unhandled `TimeoutError` in `wait_ready` causes a permanent crash loop when JCasC config is cleared
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:251` (uncaught `TimeoutError`), `src/charm.py:624,638,643,652` (`jcasc-repository` handling), `src/jenkins.py:257-300` (`wait_ready` raises `TimeoutError`), `src/jenkins.py:1132` (`jcasc-config`)
- **Evidence**: With both `jcasc-config` and `jcasc-repository` empty, the charm generates a minimal admin-only JCasC config. The crumb-issuer endpoint never becomes reachable and `wait_ready(api_ready=True, timeout=300)` raises `TimeoutError`. `_reconcile` only catches `ReconcileBlockedError`, not `TimeoutError`, so the exception propagates, ops logs "Uncaught exception while in charm code", and the hook restarts and crashes again — a ~310s loop:
  ```
  21:01:16 WARNING phase=wait_ready timeout elapsed_s=310.79
  21:01:16 ERROR   Uncaught exception while in charm code:
  ...
  TimeoutError
  ...
  21:01:22 INFO    Running precondition check  # new hook cycle
  21:01:24 INFO    phase=wait_ready start       # same loop
  ```
  Observed on `rv-jenkins-deep-4`. A subsequent `juju config` with a valid `jcasc-config` queued behind the crash-triggered events and never broke the loop.
- **Impact**: An operator who clears their JCasC config, intentionally or by accident, gets a permanent crash loop that cannot be interrupted by further config changes. The charm is bricked until the model is destroyed.
- **Fix**: In `_reconcile`, catch `TimeoutError` from `wait_ready` and map it to `BlockedStatus` ("Jenkins API not reachable; check JCasC configuration."). Consider detecting the absence of both `jcasc-config` and `jcasc-repository` early and using `wait_ready(api_ready=False)` instead, since the minimal config may not stand up a security realm that supports the crumb issuer.
- **Linter rule**: not mechanically checkable; a scenario test that clears both JCasC configs and asserts the charm reaches `BlockedStatus` (not `ErrorStatus`) would catch it.

### 2. Edge-to-stable downgrade is broken: incompatible on-disk state crashes the charm
- **Severity**: high
- **Kind**: bug
- **Where**: upgrade/downgrade path — no explicit handler exists for it
- **Evidence**: On `rv-jenkins-deep-36`, `juju refresh jenkins-k8s --channel latest/stable` downgraded rev 338 (edge) to rev 201 (stable). Stable immediately crash-looped:
  ```
  21:12:28 ERROR Error installing Jenkins, Failed to bootstrap Jenkins.
  21:12:28 ERROR Uncaught exception while in charm code:
  21:13:06 ERROR Failed request at http://localhost:8080/api/python
  21:13:06 ERROR Uncaught exception while in charm code:
  ```
  Root cause: edge writes `jenkins.yaml` and uses `CASC_JENKINS_CONFIG`; stable has no JCasC handling and doesn't know about these files. The Jenkins instance bootstrapped under JCasC (consumed `initialAdminPassword`, different security realm) doesn't match what the stable charm expects. After several cycles the charm reached `ErrorStatus` with "hook failed: update-status".
- **Impact**: Operators cannot roll back from edge to stable if they hit issues with JCasC. No documented downgrade procedure, no migration path, no graceful degradation.
- **Fix**: Document that downgrade is unsupported and add a check that refuses to start on incompatible on-disk state, or add a migration path that cleans JCasC state and re-bootstraps Jenkins. At minimum, detect JCasC files and report a `BlockedStatus` explaining the incompatibility instead of crashing.
- **Linter rule**: not mechanically checkable.

### 3. Pebble command spacing bug silently drops `-XX:MaxRAMPercentage` when `system-properties` is set
- **Severity**: high
- **Kind**: bug
- **Where**: `src/pebble.py:43-46`
- **Evidence**: f-string concatenation:
  ```python
  "command": f"java -D{jenkins.SYSTEM_PROPERTY_HEADLESS} "
  f"-D{jenkins.SYSTEM_PROPERTY_LOGGING} "
  f"{system_props}"
  "-XX:MaxRAMPercentage=50.0 -XX:InitialRAMPercentage=50.0 "
  ```
  When `system_props` is non-empty (e.g. `-Djenkins.model.Jenkins.crumbIssuerProxyCompatibility=true`), there is no space before `-XX:MaxRAMPercentage`. Confirmed via `/proc/PID/cmdline` hex dump: `-Djenkins.model.Jenkins.crumbIssuerProxyCompatibility=true-XX:MaxRAMPercentage=50.0` is a single null-delimited argument — `-XX:MaxRAMPercentage=50.0` becomes part of the `-D` value and is silently ignored by the JVM.
- **Impact**: `-XX:MaxRAMPercentage=50.0` is meant to cap Jenkins memory at 50% of container memory. When `system-properties` is set, this is silently dropped and the JVM falls back to its default (25% for server-class machines) — a silent memory-configuration regression that can cause OOM or under-utilization in production.
- **Fix**: add the missing space, e.g. `f"{system_props} -XX:MaxRAMPercentage=50.0 -XX:InitialRAMPercentage=50.0 "`.
- **Linter rule**: not mechanically checkable for this exact pattern, but the existing test `test_get_pebble_layer_command` (`id="system-properties-present"`) does not verify a space between system-props and `-XX` flags — this is a test gap that a stronger assertion (checking for `" -XX:"` in the command) would catch.

### 4. Stable channel is missing JCasC entirely
- **Severity**: high
- **Kind**: bug / ux
- **Where**: deployed rev 201 vs HEAD; `charmcraft.yaml` config options `jcasc-config`, `jcasc-repository`, `jcasc-repository-token`, `jcasc-repository-config-path`, `jcasc-repository-branch`, `jcasc-environment-secrets` absent from stable
- **Evidence**: `juju config jenkins-k8s jcasc-config` returns "key not found" on stable. No `jenkins.yaml` on disk. Pebble plan has no `CASC_JENKINS_CONFIG` or `CONFIGURATION_HASH`. HEAD `charmcraft.yaml` defines `jcasc-config` and related options.
- **Impact**: JCasC is documented as the primary configuration mechanism and has a comprehensive default config, but the published stable channel doesn't support it at all — a significant gap between what the docs describe and what operators actually get.
- **Fix**: promote the edge build (which has JCasC) to stable, or publish a newer stable revision with JCasC support.
- **Linter rule**: not mechanically checkable — requires comparing published revision config options against HEAD `charmcraft.yaml`.

### 5. Charm stuck in `BlockedStatus` after config recovery (stable only; fixed in edge)
- **Severity**: medium (stable only)
- **Kind**: bug
- **Where**: `src/charm.py:_on_config_changed` in rev 201; fixed by the reconciliation loop at `src/charm.py:_reconcile` in HEAD
- **Evidence**: On stable, `restart-time-range=99-100` (invalid) → `BlockedStatus`; then `restart-time-range=03-05` (valid) → still blocked. Only recovered when `juju relate jenkins-k8s:ingress traefik-k8s` fired a new event. On edge the same sequence correctly recovers: invalid → blocked → valid → active, confirmed on both Juju 3.6 and 4.x.
- **Impact**: Operators on stable who correct an invalid config value are stuck blocked until an unrelated event fires.
- **Fix**: already fixed in HEAD; promote edge to stable.
- **Linter rule**: not mechanically checkable; a scenario test for invalid → valid config-changed → active would catch regressions.

### 6. Pebble check uses authenticated URL (stable only; fixed in edge)
- **Severity**: low (stable only)
- **Kind**: bug
- **Where**: `src/pebble.py:46-52` in rev 201; HEAD `src/pebble.py:57-58` uses the root URL
- **Evidence**: Stable Pebble plan check URL is `http://localhost:8080/login?from=%2F`; edge shows `http://localhost:8080`. When auth is configured the login page can return 403, causing Pebble to restart Jenkins. Matches open issue #419, filed 2026-07-23.
- **Impact**: authenticated Jenkins instances on stable can be restarted needlessly by failed health checks.
- **Fix**: already fixed in HEAD; promote edge to stable.
- **Linter rule**: not mechanically checkable.

### 7. Charm operational logging invisible in `juju debug-log` on Juju 4.x
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:44` (`logger = logging.getLogger(__name__)`)
- **Evidence**: On Juju 4.0.5, the charm's `logger.info()` calls ("Reconciling storage", "Getting jenkins version", "phase=wait_ready start", etc.) do not appear in `juju debug-log`. On Juju 3.6.25 the same calls appear as `unit.jenkins-k8s/0.juju-log` entries.
- **Impact**: operators debugging on Juju 4.x have no visibility into charm reconciliation; only plugin-lookup warnings from `update-status` are visible.
- **Fix**: this is a Juju platform behaviour, not a charm defect — document that operators should check `container-agent` logs directly on Juju 4.x.
- **Linter rule**: not mechanically checkable.

### 8. Long `wait_ready` timeout on semantically-invalid JCasC config
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:_reconcile` → `jenkins.Jenkins.wait_ready(api_ready=True, timeout=300)` at `src/jenkins.py:247`
- **Evidence**: When JCasC YAML parses but produces a configuration Jenkins can't start with, Jenkins serves 503 and the charm shows `active (config-changed)` for the full 300s before reaching `BlockedStatus`.
- **Impact**: 5-minute silent hang with no operator feedback after a bad JCasC change.
- **Fix**: add a JCasC semantic-validation step before applying, or shorten the timeout with intermediate status updates.
- **Linter rule**: not mechanically checkable.

### 9. Default 1 GiB storage too small for Jenkins
- **Severity**: low
- **Kind**: ux
- **Where**: `charmcraft.yaml` storage `jenkins-home` (filesystem, no minimum-size specified)
- **Evidence**: Jenkins logs "Only 0.729 Gb free" immediately after startup; `DiskSpaceMonitor` marks the built-in node offline (seen in `pebble logs`).
- **Impact**: a fresh default deployment immediately warns about disk space, and plugin/job data will consume the remainder quickly.
- **Fix**: set a minimum storage size of 5–10 GiB in `charmcraft.yaml`, or document the recommended minimum prominently.
- **Linter rule**: not mechanically checkable.

### 10. No resource limits on the Jenkins workload container
- **Severity**: low
- **Kind**: performance
- **Where**: `charmcraft.yaml` `containers.jenkins` (no `resources` field)
- **Evidence**: `kubectl get pod -o json` shows the jenkins container has no resource limits; the charm container has a 1 GiB limit. Jenkins container used 617 MiB in testing.
- **Impact**: unbounded memory/CPU usage can starve other pods on the node.
- **Fix**: add `resources` to the jenkins container in `charmcraft.yaml`.
- **Linter rule**: a charm linter could flag k8s charms with containers that have no resource limits.

### 11. Storage reconciliation runs `chown -R` on every event
- **Severity**: low
- **Kind**: performance
- **Where**: `src/storage.py:50-55`
- **Evidence**: `container.exec(["chown", "-R", "jenkins:jenkins", storage_path], timeout=120).wait()` is called from `_reconcile_storage()`, invoked on every reconcile. The comment at `src/charm.py:228` says "Storage ownership only needs correction on attach/upgrade events," but the code calls it unconditionally.
- **Impact**: `chown -R` on a potentially large Jenkins home directory on every config-changed/update-status/relation event is wasteful.
- **Fix**: track ownership-correctness in peer data, or guard the call with an event-type check (only `jenkins_home_storage_attached` and `upgrade_charm`).
- **Linter rule**: not mechanically checkable.

### 12. `check_now_within_bound_hours` uses deprecated `datetime.utcnow()`
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/timerange.py:82`
- **Evidence**: `current_hour = datetime.utcnow().time().hour` — deprecated since Python 3.12 in favor of `datetime.now(datetime.UTC)`.
- **Impact**: will break when the deprecated method is removed; currently emits a deprecation warning.
- **Fix**: replace with `datetime.now(datetime.UTC).time().hour`.
- **Linter rule**: ruff rule `UP017` (pyupgrade) would catch this, but is not enabled in the project's ruff config.

### 13. Plugin-not-found warnings fire on every `update-status`
- **Severity**: nit
- **Kind**: performance
- **Where**: `src/jenkins.py:_get_allowed_plugins` (line 1040); `src/charm.py:_reconcile_plugins`
- **Evidence**: 17 WARNING log lines per `update-status` hook, one for each allowed plugin not installed — observed across all deployments.
- **Impact**: log noise; operators may think something is wrong when it's expected (allowed plugins don't have to be installed).
- **Fix**: downgrade these messages to DEBUG, or log once per charm lifetime.
- **Linter rule**: not mechanically checkable.

### 14. Spelling error in docstring
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/state.py:124`
- **Evidence**: `"Check if there is an auth proxy integration.."` — double period.
- **Impact**: cosmetic.
- **Fix**: remove the extra period.
- **Linter rule**: not automatically catchable; manual review.

### 15. `CONTRIBUTING.md` references `tox` commands that don't exist
- **Severity**: nit
- **Kind**: docs
- **Where**: `CONTRIBUTING.md:143-148`
- **Evidence**: instructs `tox -e unit`, `tox -e lint`, `tox -e static`, etc.; there is no `tox.ini` in the repo. The project uses `uv` with `pyproject.toml` dependency groups.
- **Impact**: new contributors following the docs will hit errors.
- **Fix**: update `CONTRIBUTING.md` to the `uv`-based workflow (`uv run pytest tests/unit`, `uv run ruff check`), or add a `tox.ini` that delegates to `uv`.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Clean reconciliation pattern** (`src/charm.py:_reconcile`): all events funnel through a single method that re-derives state from config and relations every time — a pattern worth generalizing.
- **State model** (`src/state.py`): a frozen `State` dataclass with a `from_charm()` factory that parses all config/relation data in one place; Pydantic-based validation; typed exceptions mapped to `BlockedStatus`.
- **Precondition check** (`src/precondition.py`): a dedicated module gating all charm operations on container connectivity and storage availability, returning a simple `_CheckResult`.
- **Typed environment variables** (`src/jenkins.py:Environment`): a `TypedDict` for the Jenkins environment variables makes the charm/Pebble interface explicit.
- **Comprehensive unit test suite**: 309 tests covering state parsing, config validation, reconcile logic, agent management, auth proxy, ingress, JCasC, plugins, and time-range logic, with heavy use of parametrize.
- **Secret handling for admin password**: uses Juju secrets with `set_content` for in-place updates (avoiding secret-changed loops) and `add_secret` for initial creation; backwards-compatibility path migrates from container-stored credentials. `_on_secret_changed` only triggers reconciliation for `jcasc-environment-secrets`, avoiding an infinite loop from admin-password secret creation.
- **JCasC repository feature**: `fetch_jcasc_repository` with git clone, token auth via HTTP extra headers (token never appears in URL, process table, or `.git/config`), proxy support, and deterministic YAML merge order.
- **Integration test coverage**: plugins, agents (k8s and machine), ingress, auth proxy, COS, proxy config, upgrade, HAProxy route, external agents, JCasC invalid-YAML recovery, JCasC hot-reload, JCasC repository, and storage persistence, using `juju run` with `libfaketime` for time-dependent tests.

## Common-practice notes

- Uses `plugin: uv` in `charmcraft.yaml` — the modern approach for Python charm builds.
- No `tox.ini` — uses `uv` directly with dependency groups in `pyproject.toml`; `CONTRIBUTING.md` still references `tox` (misleading — see finding 15).
- Unit tests use the traditional `Harness` from `ops.testing` rather than `ops-scenario`; still widely used across the ecosystem.
- No `metadata.yaml` — uses `charmcraft.yaml` for all metadata, the canonical approach for modern charms.
- Charm libraries in `lib/charms/` follow the standard versioned-subdirectory layout.
- Flat `src/` layout, no `src/__init__.py` — common in charm repos, but requires `PYTHONPATH=src:lib` to run tests.
- Rockcraft-based OCI image — the modern Canonical approach for workload containers.
- Includes `terraform/charm/` and `terraform/product/` modules for Terraform-based operators.

## Tests

- **Unit tests**: 309 tests, all passing (4.88s runtime), 25 modules in `tests/unit/`.
- **Coverage** (`coverage run --source=src`): `charm.py` 98% (uncovered: lines 278, 497→509, 663→690, 674, 686-688), `jenkins.py` 97% (uncovered: 281, 811-812, 1090→1096, 1231-1233, 1348-1351, 1352→1340, 1371-1372), `state.py`/`pebble.py`/`precondition.py`/`storage.py`/`timerange.py` 100%. Overall 98%, meeting `fail_under = 98`. Uncovered lines are concentrated in action handlers, the secret-changed handler, `_is_shutdown`, cleanup finally-blocks, and exec error branches.
- **Linting**: `ruff check src/` passes clean; `ruff` on `lib/` has 124 findings, all in vendored standard charm libraries. `codespell` on `src/`, `lib/`, `tests/` finds 6 typos, all in `lib/charms/haproxy/v2/haproxy_route.py` (not charm-owned code). `mypy` configured with `disallow_untyped_defs = true` (not checked in this review). Bandit configured under the `static` dependency group (not checked in this review).
- **Integration tests**: 12 modules in `tests/integration/` covering auth proxy, COS, ingress, core Jenkins, k8s agents, machine agents, plugins (2 parts), proxy, upgrade, external agents, HAProxy route, using `pytest-operator` with scheduled `allure` reporting. `test_jcasc_invalid_yaml_blocks` (line 233) validates invalid→blocked→valid→active recovery; `test_jcasc_reload_without_restart` (line 267) validates hot-reload; `test_jcasc_repository_config_from_file` (line 319) validates the git repository JCasC feature.
- **Test gaps**:
  - Pebble layer spacing: `test_get_pebble_layer_command` (`id="system-properties-present"`) checks that `-Dfoo=bar` and `-Dbaz=qux` appear in the command, but not that a space exists before `-XX:MaxRAMPercentage` — this is exactly the gap that let finding 3 through.
  - No scenario/state-transition tests (e.g. blocked → valid config-changed → active) — `Harness` tests individual hook invocations only.
  - No unit tests for `_on_secret_changed` (`src/charm.py:782`).
  - No unit tests for the `_reconcile_haproxy_route` retraction path (`external_hostname` cleared while relation remains, line 498).

## Docs

- **README.md**: good overview with links to Charmhub docs; the "Get started" section links to the tutorial. A reference to "Jenkins-agent-k8s Operator" is slightly off in one sentence.
- **Charmhub docs**: extensive — tutorial, 11 how-to topics, reference docs (actions, architecture, config, external access, integrations), changelog. The tutorial (`docs/tutorial/getting-started.md`) walks through deployment, ingress, agent integration, and plugin management. All docs assume JCasC exists, which is only true for edge/HEAD, not stable.
- **CONTRIBUTING.md**: comprehensive (CLA/commit signing, `uv`-based dev setup, testing, PR checklist), but lines 143-148 reference nonexistent `tox` commands (see finding 15).
- **Terraform modules**: `terraform/charm/README.md` and `terraform/product/README.md` provide usage instructions.
- **Open issue #419**: "Jenkins health check fails when auth is configured" — confirms the stable Pebble check uses the login page URL; fixed in edge. Reported 2026-07-23, still open (fix unreleased).
- **Open issue #420**: "Update to Jenkins LTS 2.555.3" — deployed stable rev 201 runs Jenkins 2.516.3, which has known security vulnerabilities.

## Open questions

1. Why is stable still on rev 201 when edge (rev 338, same commit as HEAD) has JCasC, the fixed Pebble health check, and the fixed config-recovery bug? Ten months behind with no visible blocker.
2. Is the 98% branch-coverage target meant to include `lib/`? The overall coverage figure (62% including `lib/`) is much lower than `src/`'s 97-100%; `fail_under = 98` in `pyproject.toml` is only meaningful with `--source=src`.
3. Why does the charm install plugins on every reconcile? `install_plugins` (`src/charm.py:435`) runs the Java plugin manager JAR on every config-changed; it's a no-op when plugins are already present but still spawns a process and reads the filesystem. Could this be guarded with a plugin-installed check? (unverified whether this materially affects performance)
