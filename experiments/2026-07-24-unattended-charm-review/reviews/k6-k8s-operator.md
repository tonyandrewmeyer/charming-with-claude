# k6-k8s

A well-structured, two-file k8s charm that wraps Grafana k6 for distributed load testing. The peer-relation-based coordination, execution-segment load splitting, and Pebble notice lifecycle are clever and largely correct. However, the charm has two critical runtime bugs that make the `start` action effectively broken on every deployment tested: a config-parsing crash on environment values containing commas/equals signs, and an unguarded HTTP call that races with Pebble service startup. Both are confirmed on the published charm (1.7/edge rev 12) and on local HEAD. A maintainer should fix these two bugs first — until then, `start` reliably crashes the hook and, on Juju 4.0, leaves the unit stuck in error with no automatic recovery. Secondary issues: the documented `--paused` flag is missing from the implementation, the `list` action produces no output in the common case, and the Loki/Prometheus/Tempo integration tests can't run on this 24.04 cluster. Fixing the two critical bugs would make this a strong, production-ready charm.

| | |
|---|---|
| Repo | canonical/k6-k8s-operator @ `4ec1f6a` (2026-07-13) |
| Charms | k6-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 with published charm (1.7/edge rev 12) and concierge-k8s-4 with locally packed HEAD (ubuntu@24.04). Both controllers tested. |
| Reviewed | 2026-07-29 |

## What it does

Deploys Grafana k6 as a Kubernetes workload, coordinated across multiple units via a peer relation. Each unit runs a proportional slice of the total test using k6's native `--execution-segment` and `--execution-segment-sequence` flags. The leader writes test configuration to the peer app databag; non-leader units react by building a Pebble layer, starting k6, and reporting status. Integrations exist for Prometheus remote write, Loki log push, k6 test scripts from other charms, service mesh, and charm tracing.

## Deployment log

### Juju 3.6 — published charm (1.7/edge, rev 12)

1. **Deploy**: `juju deploy k6-k8s --channel 1.7/edge` on concierge-k8s-3 (Juju 3.6.25). The published charm supports `ubuntu@26.04` but the cluster nodes are `ubuntu@24.04`. Despite the base mismatch, Juju accepted the deploy and the charm started. Reached active/idle in ~30s with `k6 status: idle`.

2. **Config and start → crash**: Set `load-test` config, then `juju run k6-k8s/leader start`. The start action succeeded (wrote peer data), but `k6-relation-changed` crashed with `urllib.error.URLError: [Errno 111] Connection refused`. The hook retried 5 times and failed identically each time. The unit entered error state. k6 did run and complete (Pebble logs show `Recorded notice 12` and a completed test run), and the Pebble custom notice handler fired on Juju 3.6, setting the unit back to idle. But the cascading failure means the app data was never cleared — the operator must manually run `juju run k6-k8s/0 stop` and `juju resolve` to recover.

3. **Environment config crash**: Set `environment="URL=http://host:80/path?x=1,y=2"` → `ValueError: dictionary update sequence element #0 has length 3; 2 is required`. Confirmed on the published charm. The `k6-relation-changed` hook crashes, retries indefinitely, with no actionable error message.

4. **Scale to 2 units**: `juju scale-application k6-k8s 2` → both units active. `start` action → leader unit (k6-k8s/0) crashed with the `URLError`, unit 1's k6 service started and ran (Pebble shows `active`). The leader's crash prevented `_start_test_if_ready()` from completing the resume loop for all units.

5. **Scale down**: `juju scale-application k6-k8s 1` → unit 1 terminated cleanly. No issues.

6. **Kill workload**: Not tested on Juju 3.6 (the charm was already in an error state from the `URLError`).

### Juju 4.0 — local build from HEAD

1. **Local pack**: Modified `charmcraft.yaml` to add `ubuntu@24.04:amd64` platform, changed `upstream-source` to `ubuntu/xk6:1.7-24.04`. `requires-python` was already relaxed to `>=3.12` from an earlier review pass. Packed `k6-k8s_ubuntu@24.04-amd64.charm`.

2. **Deploy**: `juju deploy ./k6-k8s_ubuntu@24.04-amd64.charm k6 --resource k6-image=ubuntu/xk6:1.7-24.04` on concierge-k8s-4 (Juju 4.0.5). Reached active/idle in ~30s. Version reported as 1.7.1.

3. **Config and start → same crash**: Set `load-test` config, `juju run k6/0 start`. The `k6-relation-changed` hook crashed with the same `urllib.error.URLError: [Errno 111] Connection refused`. k6 ran and completed (Pebble logs show `Recorded notice 12`), but the hook crash loop continued. On Juju 4.0, the Pebble custom notice handler did not fire (or was suppressed by the retry loop) — unlike Juju 3.6, where it did. This is a Juju-version difference worth flagging.

4. **Pebble plan verified**: `pebble plan` confirmed no `--paused` flag, `-o experimental-prometheus-rw` always present, `K6_PROMETHEUS_RW_SERVER_URL: ""` in environment.

**Note on earlier observations**: An initial, shorter review pass reported a successful test cycle on Juju 4.0. That could not be reproduced in this deepened pass — the `URLError` crash occurred deterministically on both Juju versions and both builds. The discrepancy may be due to the earlier pass not checking unit status after the hook chain completed, a fluke where k6 bound its HTTP port before `resume()` was called, or a different charm version (unverified). The finding as stated is confirmed on both controllers in this pass.

### Cross-version observations

- The `URLError` crash (Finding 2) is deterministic on both Juju versions and both builds — `container.start()` returns before k6 binds its HTTP port, and the immediate `K6Api.resume()` call always fails.
- The environment config crash (Finding 1) is a code-level bug independent of Juju version.
- The Pebble custom notice handler works on Juju 3.6 but not on Juju 4.0 during this hook-retry-loop scenario (unverified whether this is a general Juju 4.0 regression or specific to the retry condition).
- Loki/Prometheus/Tempo integrations could not be tested — all those charms are `ubuntu@26.04`-only.

## Observed behaviour

- **Deploy to active/idle**: ~30s for single unit on both Juju 3.6 and 4.0.
- **Start action always crashes**: On both Juju 3.6 (published rev 12) and Juju 4.0 (local HEAD), `juju run ... start` results in `k6-relation-changed` failing with `urllib.error.URLError: [Errno 111] Connection refused]`. The action itself succeeds (writes peer data), but the subsequent hook crashes. k6 does run and complete despite the crash — Pebble logs show the test completing and `Recorded notice N` being emitted.
- **Recovery from `URLError` crash**: On Juju 3.6, the Pebble `k6.com/done` notice fires and the charm's notice handler sets the unit back to idle, but the app data is never cleared (the leader never reaches the `app_status == busy && all idle` check). The operator must manually run `stop` and `juju resolve`. On Juju 4.0, the Pebble notice handler did not fire, so the unit stays in error state with no automatic recovery.
- **Test run time**: A trivial k6 script takes ~0s to execute (one iteration and exit). Pebble restarts the service on each hook retry, causing repeated executions.
- **Charm size**: 9.2 MB packed (amd64) for the local build. Published charm is similar.
- **Pebble plan at idle**: `{}` — no services defined. During a test attempt: one `k6` service with `startup: disabled`, `command: /bin/sh -c 'k6 run ... ; pebble notify k6.com/done'`.
- **No `--paused` flag**: Confirmed in Pebble plan on both published and local builds. The k6 command starts execution immediately.
- **Prometheus remote write always active**: `-o experimental-prometheus-rw` in every Pebble command, with `K6_PROMETHEUS_RW_SERVER_URL: ""` in service environment. k6 logs show `Failed to send the time series data to the endpoint` and `Prometheus remote write (http://localhost:9090/api/v1/write)` errors.
- **Ports**: `6565/tcp` opened for the k6 HTTP API.
- **Status reporting**: `collect_unit_status` and `collect_app_status` work correctly — unit showed `k6 status: busy` on the first test run (before the hook crash), app showed `k6 status: busy (1/1 units)`.
- **`list` action**: On a charm with no relations providing tests, `juju run k6-k8s/0 list` produces no output at all. The code enters `if not tests: return` before reaching `event.log()`.
- **Execution segments**: Verified on the Pebble plan — `--execution-segment '0/1:1/1'` for single unit. The mechanism is correct but untestable end-to-end due to the `URLError` crash.
- **Service mesh library**: `service_mesh.py` is large (1190 lines), imports `lightkube`, `pydantic`, `httpx`, `charmed-service-mesh-helpers`, and `lightkube-extensions`, all mocked in unit tests. Heavy dependency footprint for a charm that only needs a simple port-access policy.

## Findings

### 1. `K6Api.resume()` lacks exception handling and races with service startup
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/k6.py:38-49` (`_request`), `src/k6.py:52-55` (`resume`), `src/k6.py:322-337` (`_start_test_if_ready`), `src/k6.py:209-242` (`_on_relation_changed`)
- **Evidence**: `K6Api._request()` calls `urllib.request.urlopen(request)` with no `try/except`. Observed on both Juju 3.6 (published rev 12) and Juju 4.0 (local HEAD): `urllib.error.URLError: <urlopen error [Errno 111] Connection refused>`. Deterministic on every `start` action — `container.start()` returns before k6 binds its HTTP port, and `_start_test_if_ready()` calls `K6Api.resume()` immediately after. The hook crashes, retries, and crashes identically each time. k6 does run and complete (Pebble logs confirm), but the charm never tracks it because the unit is never set to busy and the app data is never cleared.
- **Impact**: The `start` action is effectively broken. Every invocation leaves the unit in an error state. The operator sees "hook failed: k6-relation-changed" with no actionable message. On Juju 3.6 the Pebble notice handler partially recovers (sets unit to idle) but app data persists, requiring manual `stop` + `resolve`. On Juju 4.0 the notice handler does not fire, so the unit stays in error indefinitely. The published charm (rev 12) is unusable for `start`.
- **Fix**: Wrap the `urlopen` call in `try/except (URLError, HTTPError)` with retries (e.g. 5 attempts, 1s backoff). If all retries fail, log the error and set a blocked/error status with a clear message. Alternatively, add the documented `--paused` flag, start the service, and wait for the k6 API to become reachable before calling `resume()`.
- **Linter rule**: `urllib.request.urlopen` (or `http.client` / raw socket connect) called without `try/except` — mechanically checkable.

### 2. Environment config parsing crashes on values containing `=` or `,`
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/k6.py:312-313`
- **Evidence**: `environment = dict(item.split("=") for item in environment_raw.split(","))`. With `environment="URL=http://host:80/path?x=1,y=2"`, splitting by comma yields `['URL=http://host:80/path?x=1', 'y=2']`; splitting the first item by `=` yields `['URL', 'http://host:80/path?x', '1']` (length 3), and `dict()` raises `ValueError: dictionary update sequence element #0 has length 3; 2 is required`. This propagates uncaught from `_pebble_layer()` through `_on_relation_changed()`, crashing the hook. Confirmed on the published charm.
- **Impact**: The charm enters error state and cannot recover; the hook retries indefinitely and fails identically each time, with only "hook failed" and no actionable message. Any environment value containing `=` (URL query strings, base64) or `,` (list values, multi-URL strings) triggers this.
- **Fix**: Use a structured parser (e.g. `shlex` with quoting support, or switch to a YAML/JSON config value), or at minimum split only on the first `=` with `item.split("=", 1)`. Add validation in `config-changed` that catches parse errors and sets `BlockedStatus` naming the offending value.
- **Linter rule**: String `.split(",")` used to parse key-value config near a `dict(...)` construction in config-handling code — mechanically checkable via pattern match.

### 3. `--paused` flag missing — documented design vs implementation mismatch
- **Severity**: high
- **Kind**: bug
- **Where**: `src/k6.py:178-184` (Pebble command), `docs/explanation/architecture.md`
- **Evidence**: The architecture doc states k6 "starts in `--paused` mode." The Pebble layer command does not include `--paused`. Observed in deployment: k6 runs immediately, not paused. `K6Api.resume()` sends `PATCH /v1/status` with `{"data": {"attributes": {"paused": true}}}`, which per k6 docs toggles pause state; since k6 isn't paused, the PATCH either pauses a running test or has no effect.
- **Impact**: Without `--paused`, the coordinated start described in the architecture doc doesn't happen. Units start their tests at different times as they each process `relation-changed`, so multi-unit load is unsynchronized — some units finish earlier than others, and the aggregate load pattern doesn't match operator intent.
- **Fix**: Add `--paused` to the k6 command in `_pebble_layer()`. The resume PATCH in `_start_test_if_ready()` then correctly unpauses all units simultaneously.
- **Linter rule**: not established (doc/code consistency, not mechanically checkable).

### 4. Unit tests don't cover `K6Api` or `_start_test_if_ready`
- **Severity**: high
- **Kind**: test-gap
- **Where**: `src/k6.py:38-49` (`K6Api._request`), `src/k6.py:52-55` (`K6Api.resume`), `src/k6.py:322-337` (`_start_test_if_ready`)
- **Evidence**: Coverage report shows lines 37-55 and 286-312 as missed — exactly where Findings 1-3 manifest. Scenario tests patch `K6Api.resume` with `unittest.mock.patch`, so the HTTP call is never exercised.
- **Impact**: The two most serious runtime bugs sit in code paths with zero unit test coverage. Tests for `_start_test_if_ready` or `_pebble_layer` with non-trivial environment values would have caught Finding 2 before merge.
- **Fix**: Add unit tests for `_pebble_layer` with environment values containing `=` and `,`. Add tests for `_start_test_if_ready` against a mock HTTP server (or at minimum verify exception handling). Add an integration test for `start` with non-trivial environment config.
- **Linter rule**: not established (coverage gap, not mechanically checkable).

### 5. `list` action returns no output when no relations provide tests
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:123-127`
- **Evidence**: `_on_list_action` builds `available_tests` with one entry (the config-loaded script), then checks `if not tests: return` where `tests = self.k6_tests.tests`. When no relations provide tests, `tests` is `{}` (falsy), so the method returns before reaching `event.log()`. Observed: `juju run k6-k8s/0 list` on the published charm with no relations produced no output whatsoever, not even the config-script entry.
- **Impact**: An operator running `list` to discover available tests gets silence, with no indication of whether the action failed or the charm just has nothing to report. The config-loaded test is always available but never shown.
- **Fix**: Move `event.log()` after the guard, or restructure so the list is always printed even if it only contains the config-script entry.
- **Linter rule**: Action method that builds a list and returns before logging — partially checkable (pattern: mid-function `return` before a later `event.log`).

### 6. Prometheus remote write enabled unconditionally without an endpoint
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/k6.py:176`
- **Evidence**: `-o experimental-prometheus-rw` is always included in the k6 command, even when `self.prometheus_endpoint` is `None`. Without a Prometheus relation, `K6_PROMETHEUS_RW_SERVER_URL` is set to `""`, and k6 defaults to `http://localhost:9090/api/v1/write`. Logs show `Prometheus remote write (http://localhost:9090/api/v1/write)` connection errors.
- **Impact**: Every test run produces connection errors to `localhost:9090`. Doesn't break the test but clutters logs and wastes resources; operators without Prometheus integrated have no way to suppress this.
- **Fix**: Only include `-o experimental-prometheus-rw` when `self.prometheus_endpoint` is set.
- **Linter rule**: Output flag included unconditionally when the endpoint may be `None` — partially checkable (flag gated on a variable with a None default).

### 7. Pebble custom notice handler does not fire on Juju 4.0 during hook retry loops
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/k6.py:243-248` (`_on_pebble_custom_notice`), observed on Juju 4.0 only
- **Evidence**: On Juju 3.6, the `k6.com/done` notice handler fired after k6 completed, setting the unit to idle. On Juju 4.0, the same notice was recorded by Pebble (`Recorded notice 12`) but `_on_pebble_custom_notice` never appeared to run — the `k6-pebble-custom-notice` hook never fired in `juju debug-log`.
- **Impact**: On Juju 4.0, the charm cannot self-recover from the `URLError` crash. The operator must always manually intervene with `stop` and `resolve`.
- **Fix**: Likely a Juju-side issue rather than a charm bug, but fixing Finding 1 (avoiding the crash/retry loop) would sidestep it — verify the notice handler fires normally once the retry loop is avoided.
- **Linter rule**: not established (runtime behaviour difference between Juju versions, not mechanically checkable).

### 8. Integration tests don't exercise the environment values that trigger the parsing bug
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_self_monitoring.py:113-114`
- **Evidence**: The integration test sets `environment` to `f"LOKI_URL={LOKI_URL},K6_PROMETHEUS_RW_SERVER_URL={PROMETHEUS_RW_URL},TARGET_URL={PROMETHEUS_URL}"` — all clean `http://host:port` values with no embedded `,` or extra `=`. The test never exercises the case that triggers Finding 2.
- **Impact**: Even where these integration tests can run, they wouldn't catch Finding 2, since they only exercise the happy path for environment config.
- **Fix**: Add a test case (unit or integration) that sets `environment` with embedded `=` and `,` characters and asserts the charm either parses it correctly or reports a clear `BlockedStatus`.
- **Linter rule**: not established.

### 9. `pyproject.toml` requires Python 3.14 but pyright config targets 3.11
- **Severity**: medium
- **Kind**: lint
- **Where**: `pyproject.toml:5`, `pyproject.toml:48`
- **Evidence**: `requires-python = "~=3.14.0"` at line 5, `pythonVersion = "3.11"` in `[tool.pyright]` at line 48. Unit tests cannot run on a 24.04 system (Python 3.12) without modifying the lock file.
- **Impact**: Contributors on Ubuntu 24.04 (current LTS) cannot run `tox -e unit` without manual intervention — a barrier to contribution.
- **Fix**: Either pin to `>=3.12` and maintain the lockfile for both, or provide a `just` recipe that regenerates the lockfile for local development.
- **Linter rule**: `requires-python` stricter than the test environment's Python version — mechanically checkable by comparing `tox.ini` and `pyproject.toml`.

### 10. `--tag` key=value format can produce empty values in labels
- **Severity**: low
- **Kind**: bug
- **Where**: `src/k6.py:133`
- **Evidence**: `f"--tag {key}={value}"` where `value` can be `""` (fallback from `data["labels"].get("test_uuid") or ""` at line 294), producing `--tag test_uuid=`.
- **Impact**: Minor — empty label values can confuse downstream consumers (Prometheus, Loki) or trigger k6 warnings.
- **Fix**: Filter out label entries with empty values before building `labels_args`.
- **Linter rule**: f-string with `key}={value}` where value can be empty from a fallback — partially checkable.

### 11. `_reconcile` is called on every hook including `relation-changed`
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:56-57`
- **Evidence**: `_reconcile()` runs on every hook invocation, pushing the config script and relation tests and setting ports/version each time. On `relation-changed` (which fires multiple times during a test cycle), this repeats `container.push`/`container.remove_path` redundantly.
- **Impact**: Small performance cost per hook; contributes to hook latency but not severe.
- **Fix**: Only call `_reconcile` from hooks where config or relations actually change, or cache a hash to skip no-op pushes.
- **Linter rule**: not established.

### 12. Spelling: "acces" should be "access"
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:57`
- **Evidence**: Comment reads "...allow the source (...) to acces the status port." Flagged by `codespell`.
- **Impact**: Cosmetic.
- **Fix**: `s/acces/access/`
- **Linter rule**: Caught by `codespell`, but `tox -e lint` appears to run only `ruff`/`pyright`, not `codespell`, so this slips through CI.

### 13. Unused import in charm library
- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/k6_k8s/v0/k6_test.py:13`
- **Evidence**: `from pathlib import Path` imported but never used. Flagged by `ruff` as F401.
- **Impact**: Cosmetic.
- **Fix**: Remove the import.
- **Linter rule**: Already caught by `ruff`.

## Worth copying

- **Peer-relation-based coordination** (`src/k6.py:61-380`): Using the peer relation app/unit databags as a state machine with `idle`/`busy` statuses is clean and avoids leader-as-bottleneck patterns.
- **Execution segment distribution** (`src/k6.py:269-287`): Using k6's native `--execution-segment` with lexicographic unit-name sorting splits load without parsing test scripts, and is robust to non-contiguous unit numbers after scale-down.
- **Pebble notices for lifecycle** (`src/k6.py:243-248`): `; pebble notify k6.com/done` as a trailer on the k6 command is a reliable, low-latency way to detect test completion without polling.
- **Scenario-based testing** (`tests/unit/test_k6_scenario.py`): Comprehensive use of `ops-scenario` for the stateful parts of the charm; readable helpers (`_peer()`, `_container()`, `_unit_data()`, `_app_data()`).
- **Status collection** (`src/k6.py:185-221`): `collect_unit_status` and `collect_app_status` cleanly separate unit- and app-level status.
- **Architecture documentation** (`docs/explanation/architecture.md`): Excellent sequence diagram and explanation of the test lifecycle — assuming it matches the implementation (see Finding 3).

## Common-practice notes

- **Follows**: Two-file layout (`charm.py` + helper module) under `src/`. Standard ops library usage (`ops.Object`, `CollectStatusEvent`, Pebble notices). Library layout under `lib/charms/<name>/v<N>/`. Terraform module provided. `uv` plugin for charmcraft. `tox` for test environments. `justfile` for task running.
- **Drifts**: `requires-python ~=3.14.0` is ahead of the ecosystem (most charms target 3.12 on 24.04). `pyright` targets 3.11 while production is 3.14 — an unusual mismatch.
- **Leads**: The peer-relation state machine and execution-segment approach are more sophisticated than typical sidecar charms; use of Pebble custom notices for workload lifecycle is sharp.

## Tests

| Layer | Status | Notes |
|---|---|---|
| Unit (`test_charm.py`) | 15 pass | Covers container disconnected, reconcile, start/stop/list actions |
| Unit (`test_k6.py`) | 7 pass | Covers execution segment args for various unit counts/orderings |
| Unit (`test_k6_scenario.py`) | 22 pass | Scenario coverage of init, relation-changed, Pebble layer content, Pebble notice, status collection, start/stop actions |
| Unit (`test_charm_tracing.py`) | 6 pass | Covers charm-tracing and CA cert relations |
| Integration | Not run (see below) | |
| Lint (`ruff`) | 1 finding | F401 unused import in `lib/charms/k6_k8s/v0/k6_test.py:13` |
| Static (`pyright`) | Clean | 0 errors |
| Spelling (`codespell`) | 1 finding | "acces" in `src/charm.py:57` |

**Integration tests not run**: `tests/integration/test_self_monitoring.py` deploys loki-k8s and prometheus-k8s, both `ubuntu@26.04`-only; `tests/integration/test_charm_tracing.py` deploys the Tempo stack, also 26.04-only. None can run on this 24.04 cluster. The suite uses `jubilant` + `pytest-jubilant`, a good modern setup.

**Coverage gaps relative to risks found**:
- `K6Api._request()`/`resume()` (lines 37-55): untested — the HTTP call that crashes deterministically in production.
- `_start_test_if_ready()` (line 324): untested — the leader's synchronized resume logic.
- `_pebble_layer()` with non-trivial environment config (lines 140-143): tests only use simple `key=value` pairs (`BASE_URL=http://example.com,TIMEOUT=30`), never values with embedded `=` or `,`.
- `_on_list_action` output: `test_leader_lists` only checks the action doesn't fail, doesn't assert output — Finding 5 is untested.
- `_on_relation_changed`'s app-status-idle branch (`container.start()` + `_start_test_if_ready()`) never exercises the real HTTP resume path — it's patched out with `unittest.mock.patch`.
- No integration test for environment config values containing `,` or `=` (Finding 8).

## Docs

- **README.md**: Brief but adequate — links to charmhub, shows deploy command, mentions OCI image. Missing a link to `docs/`, no troubleshooting section, no mention of environment config format limitations.
- **docs/explanation/architecture.md**: Excellent sequence diagram and lifecycle explanation, but the `--paused` claim doesn't match the code (Finding 3).
- **docs/how-to/load-test.md**: Practical and complete, covering both side-load and relation-based test provision. Uses the old `juju relate` syntax (should be `juju integrate`). The `--trust` note says "when Kubernetes has RBAC enabled" but k6 doesn't require `--trust` (unverified against actual RBAC requirements).
- **terraform/README.md**: Standard terraform-docs output.
- **charmhub description**: Matches `charmcraft.yaml`.
- **Mismatch with observed behaviour**: The how-to doc shows `environment="LOKI_URL=10.1.15.133,RATE=500"` without warning that values containing commas or equals signs will break the config parser (Finding 2). The architecture doc's `--paused` claim doesn't match the code (Finding 3).

## Open questions

1. Is `--paused` intentionally omitted, or was it lost during refactoring? The architecture doc describes it and the resume mechanism is wired up, but the flag is missing from the Pebble command.
2. Why `python ~=3.14.0`? No 3.14-only API appears to be in use; may just be forward-looking for the 26.04 target, but it blocks building/testing on 24.04.
3. Does the Pebble notice handler fire on Juju 4.0 outside a hook-retry-loop scenario? Needs investigating on a cluster where the charm isn't already crashing.
4. What happens when a unit joins mid-test? `_on_relation_changed` only acts on `status: idle`, so a unit joining during a `busy` test appears to do nothing until the test finishes — plausible but untested.
5. Does `_start_test_if_ready` correctly skip the resume step for single-unit deploys? The `if not self.peers` early return suggests yes, but this means single-unit tests never go through `--paused`/resume even if that flag were added — inconsistent with the documented design.
6. Is the `ubuntu@24.04` platform officially supported? The `1.7-24.04` OCI image exists, but `charmcraft.yaml` only lists `ubuntu@26.04` platforms, so operators on 24.04 clusters must build from source and modify `charmcraft.yaml` themselves.
