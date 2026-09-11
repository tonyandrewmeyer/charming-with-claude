# prometheus-scrape-target-k8s-operator

A workloadless integrator charm that registers external (non-Juju) metrics endpoints as Prometheus scrape jobs by writing `scrape_jobs` relation data to the `metrics-endpoint` relation. No containers, no workload process — conceptually clean. In practice, three separate config-validation failures are silently swallowed and the charm reports `ActiveStatus` while feeding Prometheus incorrect or incomplete scrape configuration. A maintainer should first fix the status-overwrite bug pattern in `_scrape_jobs()`/`_update_prometheus_jobs()` (affects `basic_auth`, `labels`, and `targets` validation) and add the missing unit tests that would have caught it — the existing suite passes at 81% coverage precisely because it skips all three error paths.

| | |
|---|---|
| Repo | canonical/prometheus-scrape-target-k8s-operator @ `ffd425c` (2026-06-29) |
| Charms | prometheus-scrape-target-k8s |
| Substrate | k8s (deployed on concierge-k8s-4 / Juju 4.0.12; `charms.json` says `"machine"` but the charm runs as a k8s workload) |
| Deployed | yes — concierge-k8s-4, 3.0/edge rev 42 (matches HEAD) |
| Reviewed | 2026-08-27 |

## What it does

The charm reads Juju config (`targets`, `labels`, `job_name`, `metrics_path`, `scheme`, `params`, `basic_auth`, TLS options), builds a Prometheus scrape job dict, and writes it as JSON to the `metrics-endpoint` relation's application data. Prometheus reads this and scrapes the configured external targets. The charm has no workload — it is purely a configuration bridge.

## Deployment log

```
# Controllers available
concierge-k8s-4  Juju 4.0.12   k8s
concierge-k8s-3  Juju 3.6      k8s
concierge-lxd-4  Juju 4.0.12   LXD
concierge-lxd    Juju 3.6      LXD

# Created model
juju add-model rv-prom-scrape-target   # k8s model on concierge-k8s-4

# Deployed
juju deploy prometheus-k8s --channel dev/edge --trust  # rev 320, active
juju deploy prometheus-scrape-target-k8s --channel 3.0/edge  # rev 42, blocked (no targets)
juju relate prometheus-k8s prometheus-scrape-target-k8s

# Initial config — scheme, metrics_path tested
juju config prometheus-scrape-target-k8s targets="192.168.5.2:7000" \
  scheme="https" metrics_path="/custom/metrics"  # active ✓

# Additional runtime tests (see Observed behaviour below):
- Valid config: works, scrape_jobs written to relation with scheme and metrics_path
- Invalid basic_auth (no colon): status Blocked→Active within same hook; basic_auth dropped
- Invalid labels (no colon): status Blocked→Active within same hook; labels dropped
- Bad params YAML: hook FAILS with uncaught yaml.YAMLError → ErrorStatus
- scheme="ftp": passed through unvalidated; prometheus goes Blocked
- Partial TLS (cert_file without key_file): passed through without cross-field validation
- Relation removal: relation-departed + relation-broken fire cleanly; charm stays Active
- juju refresh (same rev): upgrade-charm hook fires (no handler); charm recovers via start hook
- Unit restart (refresh): unit IP changes, config preserved, relation data restored
- Scale up to 2 units: non-leader goes WaitingStatus("inactive unit")
- Scale down: works
- remove-application: works

# Unit tests with coverage: 11/11 pass, coverage 81% (meets documented 80% minimum)
```

## Observed behaviour

### What only running it reveals

- **Status overwrite within a single hook**: the status log shows, within one `config-changed` hook execution, status set to Blocked (e.g. "Invalid basic_auth") then immediately overwritten to Active. Not visible from static code review without tracing status precedence.
- **Double `config-changed` hooks**: every config change fires two `config-changed` hooks ~1 second apart. Observed at 00:04:02, 00:04:24, 00:05:12, 00:05:50, 00:07:18. Charm is idempotent so no functional failure, but it doubles hook count.
- **`params` YAML parse failure → ErrorStatus**: bad YAML in `params` causes an unhandled `yaml.YAMLError`, putting the charm into `error` state; hook fails with `exit status 1`. Recovery confirmed: setting `params=""` restored `ActiveStatus`.
- **Prometheus correctly receives scrape jobs**: after valid config, Prometheus's `/api/v1/status/config` contains the scrape job with the configured target:
  ```yaml
  job_name: juju_rv-prom-scrape-target_7ba67c3_prometheus-scrape-target-k8s_external_jobs
  scrape_interval: 1m
  scrape_timeout: 10s
  static_configs:
  - targets:
    - 1.2.3.4
  ```

### Timings

- Deploy to Active (with relation): ~2 minutes
- Config change to ActiveStatus: <10 seconds
- Unit tests: 0.12s (11/11 pass)
- `juju refresh` (same rev): ~15 seconds (stop → download → upgrade-charm → config-changed → start)

### Lifecycle — `juju refresh` (same revision)

`juju refresh` to the same channel/revision fires `upgrade-charm` (no handler registered → no-op), then `config-changed`, then `start`. The charm does not register `self.framework.observe(self.on.upgrade_charm, ...)`, so `upgrade-charm` does nothing. `config-changed` and `start` both call `_update_prometheus_jobs`, restoring correct state. Unit gets a new pod IP; config and relation data are preserved. Upgrade-safe for same-revision refreshes.

### Lifecycle — unit restart (implicit, via `juju refresh`)

Pod recreated with new IP (10.1.0.108 → 10.1.0.217). Hook sequence: `stop` → `start` → `leader-elected` → `config-changed` → `metrics-endpoint-relation-changed`. `_update_prometheus_jobs` (via `start`) restores the scrape job to relation data; Prometheus receives the updated address. Clean recovery.

### Lifecycle — relation removal

`juju remove-relation prometheus-k8s prometheus-scrape-target-k8s` fires `relation-departed` then `relation-broken` on both units. The `relation-broken` handler calls `_update_prometheus_jobs`, which writes `scrape_jobs="[]"` to the dying relation (harmless). After removal, the scrape target stays `Active` if targets are configured, even though it has no relations — misleading but not broken.

### Lifecycle — `scheme="ftp"` propagates to Prometheus

Setting `scheme="ftp"` writes `"scheme": "ftp"` into the scrape job. Prometheus rejects this at config load with `Invalid scrape jobs`, going `BlockedStatus`. The scrape target charm itself stays `Active` — it does no validation of `scheme`. Recovery: reset `scheme` to empty.

### Lifecycle — partial TLS config (cert without key)

Setting `tls_config_cert_file="/tmp/cert.pem"` (no `tls_config_key_file`) writes `"tls_config": {"cert_file": "/tmp/cert.pem"}` to the scrape job. Prometheus rejects this. Same pattern as `scheme`: scrape target stays `Active`, Prometheus goes `Blocked`. No cross-field validation exists in the charm.

### Scale test

- `juju add-unit`: second unit goes `WaitingStatus("inactive unit")`; leader continues to write correct scrape data.
- `juju scale-application` down: works.
- `juju remove-application`: works.

## Findings

### Invalid `basic_auth` silently dropped; charm reports Active

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:135-143` + `src/charm.py:166`
- **Evidence**: In `_scrape_jobs()`, the `basic_auth` block catches `ValueError` and sets `BlockedStatus("Invalid basic_auth config option; use \`user:password\` format")`, then falls through to `return [job]` (job without `basic_auth`). Back in `_update_prometheus_jobs()`, `jobs = [job]` is truthy, so it writes the incomplete job to relation data and sets `ActiveStatus()`, overwriting the BlockedStatus. Confirmed live: status log at 00:05:12 shows Blocked then Active within one hook; relation data contains no `basic_auth`.
- **Impact**: An operator sets `basic_auth="admin:secret"` intending secure scraping. The charm reports Active, but Prometheus receives no credentials — the target is scraped without auth, with no operator-visible indication.
- **Fix**: Return `None` from `_scrape_jobs()` when validation fails, and check for `None` in `_update_prometheus_jobs()` before defaulting to "No targets specified". Alternatively raise a custom exception caught by `_update_prometheus_jobs()`.
- **Linter rule**: not mechanically checkable without control-flow analysis of status precedence across function boundaries.

### Invalid `labels` silently dropped; charm reports Active

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:171-194` + `src/charm.py:193`
- **Evidence**: Same pattern as `basic_auth`. `_labels()` sets `BlockedStatus("Invalid labels, see debug-logs")` and returns `{}` when labels are malformed; `_scrape_jobs()` proceeds without labels; `_update_prometheus_jobs()` sets `ActiveStatus()`. Confirmed live: status log at 00:05:50 shows Blocked("Invalid labels") then Active within one hook; relation data has no `labels` field.
- **Impact**: Operator-specified labels are silently dropped. Prometheus scrapes without the intended labels, breaking alerting/filtering with no operator-visible indication.
- **Fix**: Same as `basic_auth` — return a sentinel from `_scrape_jobs()` when validation fails.
- **Linter rule**: same as above.

### Uncaught `yaml.YAMLError` from `params` config

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:114-116`
- **Evidence**: `val = yaml.safe_load(typing.cast(str, params))` has no try/except. Setting `params="not valid yaml: [unclosed"` fails the hook with `exit status 1`, and the charm enters `ErrorStatus("hook failed: config-changed")`. Recovery confirmed by setting `params=""`.
- **Impact**: Any operator who mistypes the `params` YAML puts the charm into Error state, and the hook fails repeatedly until the operator notices and corrects the config.
- **Fix**: Wrap `yaml.safe_load()` in try/except, catch `yaml.YAMLError`, set `BlockedStatus("Invalid params YAML: ...")` and return `[]`/`None`.
- **Linter rule**: "`yaml.safe_load` called without surrounding try/except for `yaml.YAMLError`" — mechanically checkable with a simple AST rule.

### Unit tests miss all three validation failure modes

- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py`
- **Evidence**: Tests cover invalid `targets` (port/scheme/path) but not invalid `basic_auth` format, invalid `labels` format, or valid targets + invalid labels combined. No test asserts BlockedStatus persists after the handler returns. Coverage report confirms lines 136-143 (`basic_auth` ValueError handling), 181-193 (`_labels()` invalid-label path), 114-116 (`params` YAML), 120-133 (TLS options), and 107-112 (`scheme`) are uncovered.
- **Impact**: The three critical bugs above went uncaught — the suite passes with these bugs present.
- **Fix**: Add tests for: `basic_auth="badformat"` → BlockedStatus, no `basic_auth` in relation data; `labels="baddata"` → BlockedStatus, no `labels` in relation data; valid targets + invalid labels → BlockedStatus (not Active); `params="not: [yaml"` → BlockedStatus not ErrorStatus; `scheme="ftp"` → BlockedStatus; `tls_config_cert_file` without `tls_config_key_file` → BlockedStatus.
- **Linter rule**: not applicable.

### Invalid `targets` overwrites more informative BlockedStatus

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:163-167`
- **Evidence**: `_targets()` sets `BlockedStatus("Invalid targets, see debug-logs")` when it finds unparseable targets and returns `[]`; `_scrape_jobs()` returns `[]`; `_update_prometheus_jobs()` writes `scrape_jobs = "[]"` and sets `BlockedStatus("No targets specified")`. Status log at 00:04:24 shows "Invalid targets" then "No targets specified" within one hook.
- **Impact**: The operator sees "No targets specified" — indistinguishable from having configured no targets at all — and has no way to tell a config typo from a missing config without reading debug logs.
- **Fix**: Return a sentinel from `_scrape_jobs()`, or track an `is_valid` flag; in `_update_prometheus_jobs()`, only set "No targets specified" when no targets were configured at all (vs. invalid targets configured).
- **Linter rule**: "status set in a sub-function is overwritten by a subsequent unconditional status assignment in the caller without checking the prior value" — not mechanically checkable.

### No validation of `scheme`; invalid scheme breaks Prometheus

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:107-112`
- **Evidence**: `scheme` is passed through to the scrape job without validation. `scheme="ftp"` writes `"scheme": "ftp"`; Prometheus rejects the config and goes `BlockedStatus("Invalid scrape jobs")` while the scrape target stays `Active`. Observed live.
- **Impact**: A typo in `scheme` (e.g. `httpx`) causes a Prometheus outage with no indication from the scrape target charm; the operator must read Prometheus's debug log to find the cause.
- **Fix**: Validate `scheme` is `"http"` or `"https"`; set `BlockedStatus("Invalid scheme; must be 'http' or 'https'")` otherwise.
- **Linter rule**: "config option with restricted enum values passed through without range check" — not mechanically checkable without schema metadata.

### No cross-field validation for TLS config; partial cert/key breaks Prometheus

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:120-133`
- **Evidence**: Each TLS option (`tls_config_cert_file`, `tls_config_key_file`, etc.) is independently accepted, but there is no check that `cert_file` and `key_file` are both present together. `tls_config_cert_file="/tmp/cert.pem"` alone writes `"tls_config": {"cert_file": "/tmp/cert.pem"}`; Prometheus rejects it. Observed live.
- **Impact**: Same pattern as `scheme`: Prometheus goes `Blocked` while the scrape target stays `Active`, forcing the operator to diagnose via Prometheus logs.
- **Fix**: After building `tls_config`, require `cert_file` and `key_file` together; set `BlockedStatus("tls_config: both cert_file and key_file must be set together")` if not.
- **Linter rule**: not mechanically checkable.

### README example uses wrong application name

- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md:24`
- **Evidence**: `juju config prometheus-scrape-target targets="192.168.5.2:7000"` — actual charm name is `prometheus-scrape-target-k8s`. Running the command produces `ERROR application "prometheus-scrape-target" not found`.
- **Impact**: New users following the README hit a confusing error and cannot proceed.
- **Fix**: Change `prometheus-scrape-target` to `prometheus-scrape-target-k8s` in the README.
- **Linter rule**: not mechanically checkable.

### Open issue #54: config update after bad YAML validation requires relation remove/re-add

- **Severity**: medium
- **Kind**: bug
- **Where**: not established (issue describes behaviour, not a code location)
- **Evidence**: GitHub issue #54: "Updating configuration after a failed yaml validation requires removing and readding the relation." Not reproduced during this review — the observed `params` YAML error causes a hook failure (ErrorStatus), and fixing the config recovers the charm normally. The issue may only manifest with YAML that is syntactically valid but semantically wrong.
- **Impact**: (unverified) The issue is open and describes poor UX; not confirmed against current HEAD.
- **Fix**: Not investigated — needs targeted testing with various YAML structures.
- **Linter rule**: not applicable.

### Double `config-changed` hooks on every config change

- **Severity**: medium
- **Kind**: performance / ux
- **Where**: Juju/k8s substrate interaction, not charm code
- **Evidence**: Debug log shows two `config-changed` hooks ~1 second apart on every config change, at 00:04:02, 00:04:24, 00:05:12, 00:05:50, 00:07:18, 00:14:29, 00:17:19, on Juju 4.0.12 k8s.
- **Impact**: Hook execution doubles; harmless here because the charm is idempotent, but noisy.
- **Fix**: No charm-side fix available — this is Juju 4.x k8s substrate behaviour. Could deduplicate work in the handler if desired.
- **Linter rule**: not applicable.

### Charm stays `Active` when relation is removed but targets remain configured

- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:87-94`
- **Evidence**: When all relations are removed, `_update_prometheus_jobs()` has no relations to write to; `jobs` is still truthy (targets configured), so `ActiveStatus()` is set. Observed live.
- **Impact**: Misleading status — operator sees Active with no actual consumers for the scrape jobs.
- **Fix**: Check `self.model.relations[self._prometheus_relation]` and set `WaitingStatus("no relations")` or `BlockedStatus("no metrics-endpoint relation")` when there are none.
- **Linter rule**: not mechanically checkable.

### `upgrade_charm` hook has no handler

- **Severity**: low
- **Kind**: maintenance
- **Where**: `src/charm.py:51-75`
- **Evidence**: No `self.framework.observe(self.on.upgrade_charm, ...)`. `juju refresh` fires `upgrade-charm` as a no-op; the charm recovers via `config-changed` and `start`. Confirmed in debug log.
- **Impact**: No functional failure today — upgrade-safe for same-revision refreshes — but no place exists to add upgrade-specific migration/cleanup logic.
- **Fix**: Add a handler if upgrade-specific logic is ever needed; otherwise document that none is required.
- **Linter rule**: not mechanically checkable.

### Integration tests don't assert charm status after relation changes

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py`
- **Evidence**: `test_unconfigured_scrape_config_does_not_affect_prometheus` asserts `prom`'s status but not the scrape target's; `test_scrape_config_is_ingested_by_prometheus` asserts Prometheus config but not the scrape target's status.
- **Impact**: A status regression on the scrape target after a relation event would not be caught.
- **Fix**: Add `assert ops_test.model.applications["st"].units[0].workload_status == "active"` in relevant tests.
- **Linter rule**: not applicable.

### `Harness` is deprecated in current `ops`

- **Severity**: low
- **Kind**: maintenance
- **Where**: `tests/unit/test_charm.py:18, 222`
- **Evidence**: pytest output shows `PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/`.
- **Impact**: The test harness will eventually be removed; tests will need migration.
- **Fix**: Migrate tests to the modern `ops` testing approach.
- **Linter rule**: not mechanically checkable.

### `upgrade_charm` integration test is permanently skipped

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/test_upgrade_charm.py:20`
- **Evidence**: `pytestmark = pytest.mark.skip(reason="Cross-base upgrade from 24.04 to 26.04 not supported")`. The test is meant to verify config survives a refresh but always skips.
- **Impact**: The upgrade path is untested; config could be lost on a future cross-base refresh without detection.
- **Fix**: Implement a within-base upgrade test (e.g. 26.04 → 26.04 local), or clearly document the limitation.
- **Linter rule**: not applicable.

### `_job_name()` uses `config["key"]` instead of `config.get("key")`

- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:198`
- **Evidence**: `self.model.config["job_name"]` while all other config accesses use `self.model.config.get(option)`. `job_name` has a default in `charmcraft.yaml`, so this never raises `KeyError`, but it's inconsistent.
- **Impact**: Inconsistent access style makes future maintenance more error-prone if a no-default option is accessed the same way.
- **Fix**: Use `self.model.config.get("job_name", "external_jobs")` for consistency.
- **Linter rule**: "use of `model.config[key]` instead of `model.config.get(key)`" — mechanically checkable (e.g. ruff prefer-getitem-over-get style rule).

## Worth copying

- **`_validated_address()` using `urlparse`** (`src/charm.py:17-42`): cleaner and more robust than regex for address validation.
- **Leader-only relation data writes** (`src/charm.py:79-80`): `if not self.unit.is_leader()` → `WaitingStatus("inactive unit")` is correctly implemented; non-leaders don't write relation data.
- **No `StoredState` or `defer()`**: the charm is stateless — each hook is a pure function of current config and relations. Appropriate for a workloadless aggregator.
- **Status precedence is conceptually correct**: Blocked > Waiting > Active; the bug is in the implementation (status set in a sub-function then overwritten), not the design.
- **Separate validation functions** (`_targets()`, `_labels()`): clean separation of concerns.
- **CI uses reusable workflows** from `canonical/observability` (`.github/workflows/pull-request.yaml`, `release.yaml`): right pattern for charm repos — shared CI maintained centrally.
- **`.github/.jira_sync_config.yaml`**: Jira issue sync configured, helps issue tracking.
- **`SECURITY.md`**: proper security disclosure process documented.

## Common-practice notes

- **Substrate mismatch**: `charms.json` declares `"kind": "machine"` but the charm runs on k8s (workloadless — Juju supports this). CI (`charm-pull-request.yaml`) tests on both k8s and machine substrates.
- **No `lib/charms/` layout**: no local charm libraries needed — it only provides the `metrics-endpoint` relation via `prometheus_scrape`, sourced from the Prometheus charm itself.
- **`src/` layout**: standard modern charm layout, `src/charm.py` as entry point.
- **No terraform module**: reasonable for a single-purpose integrator charm.
- **`uv.lock` with `requires-python = "==3.14.*"`**: consistent with `platforms: ubuntu@26.04` in `charmcraft.yaml`.
- **`tox.ini` + `uv`**: modern setup; lint, static, unit environments all properly configured.
- **Test coverage target 80%**: `CONTRIBUTING.md` specifies 80% minimum; the run in this review hit exactly 81%.
- **Release workflow**: `canonical/observability` reusable workflow, `default-track: dev`; multiple tracks (1, 2, 3.0, dev) matching Juju base versions.

## Tests

- **Unit tests** (`tests/unit/test_charm.py`): 11 tests, all passing, 81% line coverage. Missing coverage on exactly the critical bug paths: `_labels()` invalid-label path (lines 181-193), `basic_auth` `ValueError` handling (136-143), `yaml.safe_load` for `params` (114-116), TLS config options (120-133), `scheme` validation (107-112), and the `__main__` guard (203).
- **Integration tests** (`tests/integration/test_charm.py`): 3 tests. `test_build_and_deploy` asserts initial blocked state. `test_unconfigured_scrape_config_does_not_affect_prometheus` verifies Prometheus stays active when the scrape target has no config. `test_scrape_config_is_ingested_by_prometheus` fetches Prometheus config over HTTP and asserts the scrape job is present — a genuinely good integration test.
- **Integration test skipped** (`test_upgrade_charm.py`): permanently skipped due to a cross-base upgrade limitation.
- **lint / static / codespell**: all clean — ruff, pyright, codespell report no issues.
- **Harness deprecation**: unit tests use deprecated `ops.testing.Harness`; migration to the modern approach will be needed eventually.
- **CI**: `canonical/observability` reusable workflow (`charm-pull-request.yaml@v2`); tests run on k8s substrate; no spread tests in this repo (not needed — handled by the workflow).

## Docs

- **`README.md`**: brief but adequate; lists the provides relation and a usage example. Bug: example uses `prometheus-scrape-target` instead of `prometheus-scrape-target-k8s` (see finding above).
- **`CONTRIBUTING.md`**: development setup, linting, testing instructions; references `virtualenv` while `tox.ini` actually uses `uv` — slightly stale.
- **`RELEASE.md`**: clear explanation of channel strategy (stable/candidate/edge).
- **`SECURITY.md`**: proper security disclosure process via GitHub private reports or email.
- **CharmHub description** (`charmcraft.yaml`): detailed and accurate; correctly notes "workloadless charm".
- **Discourse docs**: referenced in charmhub metadata but not present in the repo itself.

## Open questions

1. **Issue #54** (config update after bad YAML validation): not reproduced in this review — observed `params` YAML errors cause a hook failure (ErrorStatus) and recover cleanly on config fix. The issue may only manifest with YAML that is syntactically valid but semantically wrong. Needs more targeted testing.
2. **Root cause of double `config-changed` hooks**: consistently observed on k8s/Juju 4.0.12; appears to be a Juju 4.x k8s substrate behaviour, harmless here due to idempotency but not confirmed as a general Juju issue.
3. **Cross-base upgrade support**: charm targets Ubuntu 26.04 (Python 3.14); `test_upgrade_charm.py` documents the cross-base limitation but does not test within-base upgrades, which remain untested.
4. **`scheme`/TLS validation strategy**: the charm passes `scheme` and TLS options through unvalidated, relying on Prometheus to reject bad configs (shifting the failure from the scrape target to Prometheus). Not documented whether this is deliberate or an oversight.
5. **Machine substrate**: `charms.json` says `"kind": "machine"` but CI and the live deployment both use k8s; the machine substrate path was not exercised in this review (LXD was not available on the review machine).
