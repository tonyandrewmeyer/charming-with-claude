# prometheus-scrape-config-k8s-operator

A workloadless adapter charm that intercepts Prometheus scrape job configs from upstream metrics providers and forwards them downstream to Prometheus with operator-configured overrides (scrape interval, timeout, relabeling, limits). The core implementation is clean, correct, and well-tested for the happy path. The most serious finding is a missing `consumer_events.relation_broken` observer that leaves the charm silently stuck at `active` after a downstream consumer is removed — confirmed on both Juju 3.6 and 4.x. Secondary concerns are the absence of input validation on YAML and duration config values (which causes hard ErrorState on operator typos). The unit test suite (16 tests) passes completely but covers none of the bugs found. The charm-tracing integration with Tempo works correctly (verified via scenario tests and live deploy). The `receive-ca-cert` relation requires a `certificate_transfer` provider — none was available in this environment, but the wiring is covered by scenario tests. The machine/LXD substrate is functionally correct.

| | |
|---|---|
| Repo | canonical/prometheus-scrape-config-k8s-operator @ 2b1754c (2026-06-29) |
| Charms | prometheus-scrape-config-k8s |
| Substrate | k8s and machine (LXD); tested on both |
| Deployed | yes — `concierge-k8s-4` (Juju 4.0.12, k8s), `concierge-k8s-3` (Juju 3.6.25, k8s), `concierge-lxd` (Juju 3.6.27, LXD); all at 3.0/stable rev 75 |
| Reviewed | 2026-08-22 |

## What it does

Workloadless adapter charm. Upstream charms relate over `configurable-scrape-jobs` (prometheus_scrape interface); downstream Prometheus relates over `metrics-endpoint`. The charm reads scrape job configs from providers, merges in its own config options (scrape_interval, relabel_configs YAML, etc.), and writes the merged result to the consumer relation. Alert rules from providers are forwarded (toggleable via `forward_alert_rules`) to consumers. The charm correctly enforces leader-only writes, proper status precedence (leader check → consumers → providers → do work → active), and idempotent reconciliation on every hook.

Optional relations: `charm-tracing` (ops_tracing, sends hook traces to Tempo) and `receive-ca-cert` (TLS CA for tracing backend).

## Deployment log

### K8s substrate (`concierge-k8s-4`, Juju 4.0.12)
```
# Model rv-prom-scrape-config
juju deploy prometheus-scrape-config-k8s --channel 3.0/stable  # rev 75 ✅
juju deploy prometheus-k8s --channel 3.11/stable --trust ✅
juju deploy avalanche-k8s --channel 0.7/edge ✅
juju relate prometheus-scrape-config-k8s:metrics-endpoint prometheus-k8s:metrics-endpoint ✅
juju relate avalanche-k8s:metrics-endpoint prometheus-scrape-config-k8s:configurable-scrape-jobs ✅

# Config changes
juju config prometheus-scrape-config-k8s scrape_interval=20s scrape_timeout=15s  # ✅ applied, confirmed via Prometheus HTTP API
juju config prometheus-scrape-config-k8s forward_alert_rules=false  # ✅ removes alert_rules from downstream

# grafana-agent-k8s integration
juju deploy grafana-agent-k8s --channel stable  # rev 233 ✅
juju relate grafana-agent-k8s:metrics-endpoint prometheus-scrape-config-k8s:metrics-endpoint  # ✅ charm stays active; grafana-agent-k8s blocked on its own missing config

# Scale to 2 units
juju scale-application prometheus-scrape-config-k8s 2  # ✅ leader=active, non-leader=waiting "inactive unit"
juju scale-application prometheus-scrape-config-k8s 1  # ✅ back to 1 unit

# Remove upstream provider relation
juju remove-relation avalanche-k8s prometheus-scrape-config-k8s  # ✅ blocked "missing metrics provider" after hook fires
juju relate avalanche-k8s:metrics-endpoint prometheus-scrape-config-k8s:configurable-scrape-jobs  # ✅ active again

# Remove consumer relation (critical finding)
juju remove-relation prometheus-scrape-config-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint  # ❌ charm stays active instead of blocked!
juju remove-relation prometheus-scrape-config-k8s:metrics-endpoint prometheus-k8s:metrics-endpoint  # ❌ still active
# Both grafana-agent-k8s and prometheus-k8s removed as consumers → charm was still "active"
# Only went blocked after: juju config prometheus-scrape-config-k8s scrape_interval=30s (forced config-changed hook)

# charm-tracing integration (Tempo)
juju deploy tempo-k8s --channel latest/stable  # rev 71 ✅
juju relate tempo-k8s:tracing prometheus-scrape-config-k8s:charm-tracing  # ✅ charm stayed active, tempo stayed active
# charm-tracing-relation-changed fired on scrape-config → handled correctly (optional relation)
# charm-tracing-relation-departed and charm-tracing-relation-broken fired → handled correctly

# Break charm-tracing relation
juju remove-relation tempo-k8s:tracing prometheus-scrape-config-k8s:charm-tracing  # ✅ charm stayed active
# charm-tracing-relation-departed and charm-tracing-relation-broken fired correctly

# Bad YAML config → ErrorState
juju config prometheus-scrape-config-k8s relabel_configs="[not: valid"  # ❌ ErrorState "hook failed: config-changed"
juju config prometheus-scrape-config-k8s relabel_configs=""  # ✅ recovers

# Invalid scrape_interval (non-duration string)
juju config prometheus-scrape-config-k8s scrape_interval=abc  # ⚠️ silently accepted, "abc" written to relation

# juju refresh to edge
juju refresh prometheus-scrape-config-k8s --channel 3.0/edge  # "already up-to-date" — edge is rev 75, same as stable

# remove-application teardown
yes | juju remove-application prometheus-scrape-config-k8s  # ✅ maintenance "stopping charm software", cleanly removed
```

### K8s substrate (`concierge-k8s-3`, Juju 3.6.25)
```
# Model rv-prom-scrape-config-v3
juju deploy prometheus-scrape-config-k8s --channel 3.0/stable  # rev 75 ✅
# → blocked "missing metrics consumer" ✅ (same as Juju 4.x)

# Deploy and relate (same as above)
juju deploy prometheus-k8s --channel 3.11/stable --trust ✅
juju deploy avalanche-k8s --channel 0.7/edge ✅
juju relate prometheus-scrape-config-k8s:metrics-endpoint prometheus-k8s:metrics-endpoint  # ✅
juju relate avalanche-k8s:metrics-endpoint prometheus-scrape-config-k8s:configurable-scrape-jobs  # ✅ active

# Consumer removal bug — SAME as Juju 4.x
juju remove-relation prometheus-scrape-config-k8s:metrics-endpoint prometheus-k8s:metrics-endpoint
# metrics-endpoint-relation-broken fires → juju-unit idle → workload status stays ACTIVE ❌
# Only went blocked after: juju config scrape_interval=30s

# Provider removal → correctly goes blocked "missing metrics provider" ✅ (via targets_changed)

# Bad YAML + provider re-add on Juju 3.6
juju config prometheus-scrape-config-k8s relabel_configs="[not: valid"
# Provider relation re-added with bad config → charm goes ERROR ✅
# Error: hook failed: "configurable-scrape-jobs-relation-created" (Juju 3.6 error message format)
# juju resolve prometheus-scrape-config-k8s/0 → charm recovers to active ✅ (Juju 3.6)

# juju resolve to recover from error
juju resolve prometheus-scrape-config-k8s/0  # ✅ successfully recovered from error state
```

### LXD/machine substrate (`concierge-lxd`, Juju 3.6.27)
```
juju deploy prometheus-scrape-config-k8s --channel 3.0/stable  # rev 75 ✅
# → blocked "missing metrics consumer" ✅ (correct)
# prometheus-k8s and avalanche-k8s are k8s-only → cannot test full relation chain
# grafana-agent (machine, rev 827) does NOT provide metrics-endpoint → cannot test integration
```

## Observed behaviour

- **Lifecycle (Juju 4.x and 3.6)**: deploy → blocked (no relations) → active (both relations) → blocked (upstream removed) → active (re-added). Correct at every step. No behavioural difference between Juju versions.
- **Config changes**: `scrape_interval=20s scrape_timeout=15s` correctly written to downstream scrape_jobs. Verified both in relation data and via Prometheus HTTP API (`/api/v1/status/config`). Prometheus shows `scrape_interval: 20s` and `scrape_timeout: 15s` for the avalanche-k8s job.
- **Status messages**: "missing metrics consumer (relate to prometheus?)" and "missing metrics provider (relate to upstream charm?)" are clear and actionable.
- **Non-leader units**: Set `WaitingStatus("inactive unit")`. Scale to 2 units: leader stays `active`, follower stays `waiting`. Scale back to 1: back to single active unit.
- **Prometheus targets**: The avalanche-k8s target shows state "unknown" immediately after relation setup — expected transient.
- **Bad YAML config**: Unhandled `yaml.parser.ParserError` propagates out of hook → charm goes to `ErrorStatus`. On Juju 4.x: `"hook failed: config-changed"`. On Juju 3.6: `"hook failed: configurable-scrape-jobs-relation-created"`. Recovery by correcting config + `juju resolve` works on both versions. **Confirmed bug.**
- **Invalid duration string scrape_interval**: `scrape_interval="abc"` is silently accepted. The value `"abc"` is written to the relation data and forwarded to Prometheus. Charm stays `active`. **Confirmed bug.**
- **Negative duration string scrape_interval**: `scrape_interval="-5s"` is silently accepted. **Confirmed bug.**
- **Empty string scrape_interval**: Accepted without error. The value `""` is forwarded to the downstream relation, overriding any upstream scrape_interval. **Confirmed bug.**
- **Negative integer sample_limit**: `sample_limit=-1` is accepted without error. **Confirmed bug.**
- **Duplicate hook firing**: `configurable-scrape-jobs-relation-changed` fires 3-5 times in quick succession when the upstream relation is established. This is a property of the upstream (avalanche-k8s), not this charm. The charm handles it correctly.
- **grafana-agent-k8s integration**: Relating `grafana-agent-k8s` as a second downstream consumer works correctly — the charm sends scrape jobs to both prometheus-k8s and grafana-agent-k8s. grafana-agent-k8s goes blocked on its own (missing `grafana-cloud-config`) but the scrape-config charm stays `active`. This is correct behavior.
- **charm-tracing + Tempo integration**: Deployed tempo-k8s and related to `charm-tracing`. The charm-tracing-relation-changed hook fired, charm stayed active (optional relation). Breaking the relation fired charm-tracing-relation-departed and charm-tracing-relation-broken, charm stayed active. The `ops_tracing.Tracing` object handles these hooks internally. **Confirmed correct.**
- **`receive-ca-cert`**: Requires a `certificate_transfer` interface provider. No such charm was available in this environment. Scenario tests cover the wiring with a simulated `certificate_transfer` relation. **Cannot test live, but scenario tests confirm correct behavior.**
- **Consumer relation removal (critical finding — confirmed on both Juju 3.6 and 4.x)**: Removing the last downstream consumer relation does NOT trigger a status update. The charm stays at its previous status (`active`) even though `_has_consumers()` now returns `False`. Only a subsequent unrelated hook (like `config-changed`) fires the reconciliation and correctly sets `BlockedStatus("missing metrics consumer")`. Status log proof (Juju 4.x): at 08:35:08 `metrics-endpoint-relation-broken` fires (grafana-agent-k8s removed) → `juju-unit idle` with no status change. At 08:35:38 `metrics-endpoint-relation-broken` fires again (prometheus-k8s removed) → still `active`. At 08:36:04 `config-changed` fires → finally blocked. Same pattern confirmed on Juju 3.6 at 08:59:37.
- **Provider `relation-broken` works via `targets_changed`**: When the provider (avalanche-k8s) is removed, the `MetricsEndpointConsumer` library fires `targets_changed` on `relation_broken` (`lib/charms/prometheus_k8s/v0/prometheus_scrape.py:1000–1006`). The charm observes `targets_changed` → `_update_all_metrics_consumers` → correctly goes blocked "missing metrics provider". Confirmed on both Juju 3.6 and 4.x.
- **`juju resolve` on error state**: On Juju 3.6, after the charm went to `error` with bad YAML config, `juju resolve prometheus-scrape-config-k8s/0` successfully re-ran the failed hook with the corrected config and the charm recovered to `active`. **Confirmed.**
- **`update-status` hook**: Fires roughly every 5 minutes. When relations exist, correctly returns `ActiveStatus()`. Observed on both Juju 3.6 and 4.x.
- **`juju remove-application` teardown**: Fires `relation-broken` on downstream consumers (prometheus-k8s processes it), charm goes to `maintenance "stopping charm software"`, cleanly removed. Confirmed on Juju 4.x.
- **Hook count per config change**: A single `juju config` triggers one `config-changed` hook. No unnecessary hook firings.
- **No actions defined**: The charm declares no Juju actions. Nothing to run.
- **Machine substrate (LXD)**: Charm correctly blocks on LXD with no relations. Cannot deploy prometheus-k8s or avalanche-k8s (k8s-only). grafana-agent (machine) does not provide `metrics-endpoint`. Full relation chain untestable on LXD with available charms.

## Findings

### `consumer_events.relation_broken` not observed — charm stuck at active after consumer removal
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:60–69`
- **Evidence**: The observed event list includes `provider_events.relation_broken` but NOT `consumer_events.relation_broken`. When a downstream consumer relation is broken:
  ```python
  # Observed:
  provider_events.relation_created,
  provider_events.relation_joined,
  provider_events.relation_broken,   # ← observed for provider
  consumer_events.relation_created,
  consumer_events.relation_changed,   # ← NO consumer_events.relation_broken
  ```
- **Observed on both Juju 3.6 and 4.x**: Removed both downstream consumers (grafana-agent-k8s and prometheus-k8s) — the charm stayed `active` with no message. Only after `juju config prometheus-scrape-config-k8s scrape_interval=30s` (forcing a `config-changed` hook) did the charm correctly go to `blocked "missing metrics consumer"`. Status log shows `metrics-endpoint-relation-broken` fires but the workload status does not change until a subsequent unrelated hook fires.
- **Why it matters**: In normal operation, when an operator removes a consumer (e.g., `juju remove-application prometheus-k8s`), this charm will silently stay `active` indefinitely — giving no indication that it is no longer serving any purpose. An operator might not notice until Prometheus stops receiving metrics.
- **Fix**: Add `consumer_events.relation_broken` to the observed events list at `src/charm.py:68`.
- **Linter rule**: "Consumer relation broken event not observed" — mechanically checkable by verifying `consumer_events.relation_broken` is in the `framework.observe` calls.

### Bad YAML in relabel_configs/metric_relabel_configs causes ErrorState
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:139`
- **Evidence**: `config[key] = yaml.safe_load(str(as_yaml))` — `yaml.safe_load` raises `yaml.parser.ParserError` on malformed YAML. When this happens, the exception propagates out of `_prometheus_configurations` → `_update_all_metrics_consumers` → the hook handler. The hook exits with non-zero status → charm goes to `ErrorStatus`. On Juju 4.x: `"hook failed: config-changed"`. On Juju 3.6: `"hook failed: configurable-scrape-jobs-relation-created"` (the hook that happens to fire when the provider re-connects with the bad config still set). Operator sees no actionable error message; only the traceback in debug logs.
- **Observed**: Set `relabel_configs="[not: valid"` → charm immediately went to `error`. On Juju 3.6, when the provider was re-added after setting bad YAML, the charm went to `error "hook failed: configurable-scrape-jobs-relation-created"`. Recovery via `juju config relabel_configs=""` + `juju resolve` succeeds — the next hook runs successfully and charm returns to `active`.
- **Why it matters**: Any operator typo in YAML config breaks the charm hard. There is no graceful degradation.
- **Fix**: Wrap `yaml.safe_load` in try/except. On error, set `BlockedStatus("invalid YAML in {key}: <error message>")` and return before writing relation data.
- **Linter rule**: "YAML config parsed without try/except" — mechanically checkable by AST analysis.

### Non-duration string scrape_interval/scrape_timeout silently forwarded to Prometheus
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:143`
- **Evidence**: `job.update(config)` — the `config` dict is built from `self.model.config.items()` with no validation that string values are valid Prometheus duration strings. `scrape_interval="abc"` is accepted, written to relation data, and forwarded to Prometheus. Charm stays `active`.
- **Observed**: Set `scrape_interval=abc` → relation data showed `"scrape_interval": "abc"`. Charm stayed `active`. Prometheus received the invalid value.
- **Why it matters**: An operator setting an invalid scrape interval gets silently wrong behavior. Prometheus may silently fall back to its global default or fail to scrape, with no indication from the charm.
- **Fix**: Add a duration validation helper and raise `ValueError` (caught as `BlockedStatus`) for invalid duration strings. Prometheus duration format is `[0-9]+(ms|s|m|h|d|w|y)`.
- **Linter rule**: "String scrape config option declared without format validation" — mechanically checkable.

### Negative duration string scrape_interval silently forwarded to Prometheus
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:143`
- **Evidence**: Same as above — no validation. `scrape_interval="-5s"` is accepted and forwarded.
- **Observed**: Set `scrape_interval=-5s` → relation data showed `"scrape_interval": "-5s"`. Charm stayed `active`.
- **Why it matters**: Same as above — silent misinterpretation by Prometheus.
- **Fix**: Same as above.
- **Linter rule**: Same as above.

### Empty string scrape_interval / scrape_timeout silently overrides upstream config
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:136`
- **Evidence**: `config = {k: v for k, v in self.model.config.items() if k not in [...]}`. For string-type config options, `v` can be `""`. The resulting `config` dict contains `{"scrape_interval": ""}`. Then `job.update(config)` (line 143) overwrites the upstream's `scrape_interval` with `""`. Prometheus receives an empty string and falls back to its global default, silently removing the operator's intended override. Known issue #31 (open).
- **Observed**: Set `scrape_interval=""` → relation data showed `"scrape_interval": ""`. Upstream's original `scrape_interval: "15s"` was overridden.
- **Why it matters**: An operator who accidentally clears `scrape_interval` loses their configuration silently. No error or warning.
- **Fix**: After building the `config` dict, strip empty-string values: `config = {k: v for k, v in config.items() if v != ""}`.
- **Linter rule**: "String config keys not validated for empty values before being applied as scrape config overrides" — mechanically checkable.

### `MetricsEndpointConsumer.jobs()` silently drops jobs when upstream config fails Prometheus validation
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/prometheus_k8s/v0/prometheus_scrape.py:1053–1059`
- **Evidence**: `jobs()` calls `self._tool.validate_scrape_jobs(static_scrape_jobs)`. If validation fails (raises `subprocess.CalledProcessError`), the error is written to `relation.data[self._charm.app]["event"]["scrape_job_errors"]` and the jobs from that relation are NOT added to `scrape_jobs`. The charm does NOT set a `BlockedStatus` and does NOT alert the operator. The charm stays `ActiveStatus` with no scrape jobs for that consumer.
- **Why it matters**: If an upstream provider sends scrape jobs with duplicate job names or other Prometheus validation failures, the charm silently stops forwarding jobs with no indication to the operator. Prometheus will have no target from that provider.
- **Fix**: After calling `self._metrics_providers.jobs()`, check if the result is empty (or compare with what the upstream advertised). If empty but providers exist, set `BlockedStatus("invalid scrape config from upstream: <provider>")`.
- **Linter rule**: not mechanically checkable without simulating invalid upstream data.

### BSON 16MB relation data limit causes ErrorState (known issue #70)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:118–119` (relation writes); `lib/charms/prometheus_k8s/v0/prometheus_scrape.py:1053–1059`
- **Evidence**: Open issue #70: "BSONObj size: 17970819 is invalid. Size must be between 0 and 16793600(16MB)". The charm writes `scrape_jobs` and `alert_rules` (JSON-serialized) into relation application data. Large alert rule sets accumulated over ~a year of operation exceed the 16MB BSON limit, causing a traceback rather than a `BlockedStatus` with an actionable message.
- **Why it matters**: After extended operation, the charm becomes undebuggable for operators who don't have access to the traceback logs.
- **Fix**: Validate total payload size before writing and set `BlockedStatus("alert rules too large for relation data")` if the limit would be exceeded. This is a systemic issue in the `prometheus_scrape` library.
- **Linter rule**: not mechanically checkable.

### Negative integer config values silently forwarded to Prometheus
- **Severity**: medium
- **Kind**: bug
- **Where**: `charmcraft.yaml:config.options.sample_limit`, etc.; `src/charm.py:136`
- **Evidence**: `config = {k: v for k, v in self.model.config.items() if k not in [...]}` — no range validation on integer options. `sample_limit=-1` is accepted, forwarded to downstream, and Prometheus may accept it or silently misinterpret it.
- **Observed**: Set `sample_limit=-1` → relation data showed `"sample_limit": -1`. Charm stayed `active` without warning.
- **Why it matters**: An operator setting a negative sample limit has silently wrong behaviour. Prometheus may interpret `-1` differently from `0` (unlimited).
- **Fix**: Validate integer config options: `if isinstance(v, int) and v < 0: raise ValueError(f"{k} must be non-negative")`.
- **Linter rule**: "Integer config option declared without range validation" — mechanically checkable against charmcraft.yaml config schema.

### Upgrade test permanently skipped
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_upgrade_charm.py:19`
- **Evidence**: `pytestmark = pytest.mark.skip(reason="Cross-base upgrade from 24.04 to 26.04 not supported")`. The test is entirely skipped. No same-base upgrade test exists.
- **Why it matters**: Charm upgrades are a critical operational path with no automated coverage.
- **Fix**: Enable same-base upgrade tests, or file a tracked issue and add a comment with a link to it.
- **Linter rule**: not applicable.

### `_prometheus_configurations` evaluated per-consumer in a loop
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:101` (in `_update_all_metrics_consumers`)
- **Evidence**: `_update_all_metrics_consumers` calls `_update_metrics_consumer_relation` for each consumer relation, and each call re-evaluates `_prometheus_configurations` (a `@property`). For N downstream consumers, the same upstream jobs are processed N times.
- **Why it matters**: Unnecessary repeated work. For a charm with few relations this is not significant, but it is architecturally wrong.
- **Fix**: Cache `_prometheus_configurations` at the start of `_update_all_metrics_consumers`: `configs = self._prometheus_configurations`, then pass `configs` to `_update_metrics_consumer_relation`.
- **Linter rule**: "Property accessed inside a loop without caching" — mechanically checkable.

### CONTRIBUTING.md commands don't match actual project tooling
- **Severity**: low
- **Kind**: docs
- **Where**: `CONTRIBUTING.md`
- **Evidence**: The linting section says `tox -e lint` but the project uses `uv run ruff`. The testing section says `tox -e unit` but the project uses `uv run pytest`. The setup section shows `virtualenv -p python3 venv` but the project uses `uv`. The build section shows `charmcraft pack` but the project uses `uv` in the charmcraft plugin.
- **Why it matters**: A new contributor following the CONTRIBUTING.md will use the wrong commands and be confused.
- **Fix**: Update CONTRIBUTING.md to use `uv run ruff check` and `uv run pytest`.
- **Linter rule**: not applicable.

### `observability_libs.v0.juju_topology` is deprecated in unit tests
- **Severity**: low
- **Kind**: lint
- **Where**: `tests/unit/test_charm.py:11`
- **Evidence**: Unit tests import from `charms.observability_libs.v0.juju_topology`. The installed `cosl` package deprecates this in favor of `cosl.JujuTopology`. The test runs with a deprecation warning: "observability_libs.v0.juju_topology is deprecated. Please import the library from `cosl` instead".
- **Why it matters**: Using deprecated APIs risks breaking in future versions. The `cosl` package is already a direct dependency.
- **Fix**: Change import to `from cosl import JujuTopology`.
- **Linter rule**: "Import from deprecated library" — mechanically checkable.

### Test runner requires manual PYTHONPATH setup
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/conftest.py:11`; `tox.ini`; `charms.just`
- **Evidence**: `conftest.py` imports `from charm import PrometheusScrapeConfigCharm`, but the file is at `src/charm.py`. Running `uv run pytest tests/unit/` directly fails with `ModuleNotFoundError: No module named 'charm'`. The `justfile` sets `PYTHONPATH := ".:./lib:./src"` (dot means root, but `charm.py` is at `src/charm.py`, so this is also wrong — `.` would only work if `charm.py` were at the root). The `tox.ini` sets `PYTHONPATH = {toxinidir}:{toxinidir}/lib:{[vars]src_path}` (root + lib + src) which works. When `PYTHONPATH=src:lib` is set manually, all 16 tests pass.
- **Observed**: `PYTHONPATH=src:lib uv run pytest tests/unit/` → 16 passed. `uv run pytest tests/unit/` (no PYTHONPATH) → ModuleNotFoundError.
- **Why it matters**: A contributor running `uv run pytest` out of the box will get a confusing import error. The tox environment works correctly; direct pytest invocation does not.
- **Fix**: Either (a) move `src/charm.py` to `charm.py` at the root, or (b) add `PYTHONPATH` to the `pyproject.toml` pytest config, or (c) add a `conftest.py` at the root that sets sys.path, or (d) fix the conftest import to `from src.charm import`.
- **Linter rule**: not mechanically checkable.

### `self._forward_alert_rules` cache at `__init__` is redundant
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:39`
- **Evidence**: `self._forward_alert_rules = cast(bool, self.config["forward_alert_rules"])` is assigned at `__init__` and read at line 148 (`if self._forward_alert_rules:`). The cache is not stale — Juju calls `__init__` fresh on every hook dispatch — but it is redundant with `self.config["forward_alert_rules"]`. Inconsistent with the rest of the codebase, which reads `self.config` directly without caching.
- **Why it matters**: The redundant cache adds an attribute that looks like it might be stale between hook dispatches, misleading code reviewers.
- **Fix**: Remove `self._forward_alert_rules` and its `cast`. Replace `if self._forward_alert_rules:` at line 148 with `if self.config["forward_alert_rules"]:`.
- **Linter rule**: "Config value cached at `__init__` without justification" — not mechanically checkable without semantic analysis.

### Dead `is_leader()` guard in `_update_metrics_consumer_relation`
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:108–111`
- **Evidence**: `_update_metrics_consumer_relation` has `if not self.unit.is_leader(): self.unit.status = WaitingStatus("inactive unit"); return`. But this method is only called from `_update_all_metrics_consumers`, which already returns early if not leader (line 87–89). The inner guard is unreachable from any call path.
- **Why it matters**: Dead code confuses maintainers.
- **Fix**: Remove the inner guard, or document why it exists as a defensive measure against future misuse.
- **Linter rule**: "Unreachable `is_leader()` guard in internal method" — not mechanically checkable without whole-program analysis.

### INTEGRATING.md typo: "promethehus"
- **Severity**: nit
- **Kind**: docs
- **Where**: `INTEGRATING.md` (table footnotes, "promethehus" instead of "prometheus")
- **Evidence**: Line "`global`         | promethehus" in the config section table.
- **Why it matters**: Typos in documentation reduce credibility.
- **Fix**: Fix the typo.
- **Linter rule**: not applicable.

### `CosTool` uses `noinspection` PyCharm directive before try/except (corrected)
- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/prometheus_k8s/v0/prometheus_scrape.py:1906, 1949`
- **Evidence** (corrected): My earlier draft incorrectly said these used bare `except:`. In fact, both `validate_alert_rules` (line 1906) and `inject_label_matchers` (line 1949) use `# noinspection PyBroadException` as a PyCharm directive, and the actual `except:` clause is `except subprocess.CalledProcessError as e:` — a specific exception. The `# noinspection` comment is just to suppress PyCharm's warning about catching a broad exception type. This is correct behavior. The `validate_scrape_jobs` method (line 1937) uses a plain `try/except subprocess.CalledProcessError` without the `# noinspection` comment. **No bug here.**
- **Fix**: none — the code is correct. The `noinspection` comment is a PyCharm-specific lint suppression, not a code defect.
- **Linter rule**: not applicable.

### `targets_changed` event handler discards `relation_id` (not a useful optimization)
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:61`
- **Evidence**: The charm observes `self._metrics_providers.on.targets_changed` and calls `self._update_all_metrics_consumers(self._)`, discarding the event's `relation_id`. The `TargetsChangedEvent` carries a `relation_id` snapshot (`lib/charms/prometheus_k8s/v0/prometheus_scrape.py:926–936`) identifying which provider relation changed.
- **Why it matters** (corrected): My earlier draft said the `relation_id` could be used to update only the affected consumer. This is incorrect — the `relation_id` identifies the PROVIDER that changed, not a consumer. All consumers still need to be re-rendered (and the `_has_providers()` check must run against all provider relations). The `relation_id` is genuinely useless in this handler. The current implementation is correct; the parameter is simply irrelevant to what the handler needs to do.
- **Fix**: Remove the parameter from the lambda signature, or accept it with an underscore: `lambda e: self._update_all_metrics_consumers(_)`.
- **Linter rule**: not mechanically checkable without semantic analysis.

## Worth copying

- **Clean single-property reconciler**: `_prometheus_configurations` as a `@property` that derives scrape jobs from upstream jobs + config — simple, testable, and idempotent.
- **Correct status precedence**: `_update_all_metrics_consumers` checks `is_leader()` → `_has_consumers()` → `_has_providers()` → do work → `ActiveStatus`. This is the correct ordering.
- **`test_config_keys_were_mindfully_added`**: Explicit regression test listing all config keys and their intended handling, with a comment requiring confirmation before adding new keys. Prevents silent config key mishandling.
- **Well-documented blocked states**: README explains exactly why the charm blocks and what to do, with concrete `juju status` output examples.
- **Clean relation event registration**: Using `for e in [...]` to register all events that trigger reconciliation is more readable than separate `self.framework.observe()` calls.
- **Prometheus HTTP API helper**: `tests/integration/helpers.py`'s `Prometheus` class wrapping the Prometheus HTTP API is a clean pattern for integration test assertions.
- **Scenario tests for charm-tracing**: The 4 `test_tracing.py` scenario tests properly verify the charm-tracing relation wiring (publishes `receivers` on relation-changed, withdraws on relation-broken, stays active with or without TLS).
- **`juju resolve` works correctly**: The charm recovers cleanly from error state when the config is corrected and `juju resolve` is run. Tested on both Juju 3.6 and 4.x.
- **`upgrade_charm` hook observed**: The charm observes `self.on.upgrade_charm` and triggers `_update_all_metrics_consumers` on it. This is correct — the upgrade path re-renders config for all consumers.

## Common-practice notes

- **Workloadless k8s charm**: Despite the "k8s" in the name, the charm has no containers, no Pebble, and `type: charm` (not podspec). It is effectively a machine charm that runs on k8s controller. This is correct but potentially confusing — the name suggests k8s-specific behavior.
- **`ops_tracing`**: Uses `ops_tracing.Tracing` for distributed tracing, following the canonical pattern with optional `charm-tracing` and `receive-ca-cert` relations. Correct. The `charm-tracing-relation-changed/departed/broken` hooks are handled by `ops_tracing.Tracing` internally; the charm's status is unaffected by these relations.
- **`receive-ca-cert` relation**: Uses the `certificate_transfer` interface. No charm in this environment provided this interface. Scenario tests (`tests/unit/test_tracing.py`) cover the wiring with a simulated `certificate_transfer` relation. The charm correctly treats this as optional.
- **Library in `lib/` tree**: The `prometheus_scrape` library at `lib/charms/prometheus_k8s/v0/prometheus_scrape.py` is a bundled local copy, not imported from a `charms/` sub-tree. This is common practice but means the library version in the repo may diverge from what `charmcraft.yaml` declares.
- **`relation_joined` not observed on consumer side**: The charm observes `provider_events.relation_joined` but NOT `consumer_events.relation_joined`. This is fine because `relation_created` fires first and triggers the reconciliation; `relation_changed` fires when the consumer reads the data.
- **`targets_changed` relation_id**: The charm discards the `relation_id` from `TargetsChangedEvent`. This is correct — the `relation_id` identifies the provider that changed, not a consumer. All consumers must be re-rendered in every case.
- **Test setup with justfile**: The project uses a centralized `justfile` (`charms.just`) from the `canonical/observability` org. The `tox.ini` is also present and works correctly (sets PYTHONPATH correctly).
- **Juju version parity**: The charm behaves identically on Juju 3.6 and 4.x for all tested scenarios. Error message format differs slightly (Juju 3.6 includes the hook name in quotes: `"hook failed: configurable-scrape-jobs-relation-created"` vs Juju 4.x: `"hook failed: config-changed"`), but this is a Juju version difference, not a charm bug.
- **LXD machine charm testability**: Since prometheus-k8s and avalanche-k8s are k8s-only, the full relation chain cannot be tested on LXD. grafana-agent (machine) doesn't provide `metrics-endpoint`. This is a limitation of the available charms, not a charm bug.

## Tests

### Unit tests — all 16 pass
- **`tests/unit/test_charm.py`**: 12 tests using deprecated `Harness`. Covers: single/multiple upstreams and downstreams, blocked/waiting status, alert rules, workload version. **Gap**: no test for YAML config validation failure, no test for empty-string scrape_interval, no test for negative integer config values, no test for invalid duration strings, no test for `relation_broken` on the consumer side, no test for recovery from ErrorState, no test for `targets_changed` event.
- **`tests/unit/test_config_key.py`**: Regression test verifying all config keys are intentionally handled. Passes.
- **`tests/unit/test_tracing.py`**: 4 scenario tests using `ops.testing.Context`. All 4 PASS. Tests: (1) charm goes active with charm-tracing relation (HTTP), (2) charm goes active with charm-tracing relation + TLS (HTTPS + CA cert), (3) charm publishes `receivers: ["otlp_http"]` on relation-changed, (4) charm withdraws `receivers` on relation-broken.
- **Test runner setup issue**: Running `uv run pytest tests/unit/` without `PYTHONPATH=src:lib` fails with `ModuleNotFoundError`. The `tox.ini` sets PYTHONPATH correctly (root + lib + src); direct pytest invocation does not pick it up.
- **Scenario test warnings**: 9 warnings during scenario test run — all ops-level issues: `(1)` ops_scenario consistency checker warning about implicit remote unit in `charm_tracing_relation_changed` fixture; `(2)` ops `Charm.on` snapshot warnings (`'app' expected but not received`, `'app_name' expected in snapshot but not found`) linked to LP bug #1960934. None of these are charm bugs.
- **Pydantic deprecation warnings**: ops_tracing vendor code uses deprecated Pydantic V2 APIs (`model_fields` on instance, `__fields__`, `.dict()` instead of `.model_dump()`). These are in vendored code, not the charm.
- **Linter/tool results**: `ruff check src/ tests/` → All checks passed. `pyright src/` → 0 errors, 0 warnings, 0 informations. `codespell` → only finds issues in `icon.svg` (SVG artifact text), not Python code.

### Integration tests — not run
- `tests/integration/test_charm.py`: Deploys prometheus-k8s + zinc-k8s + scrape-config charm, tests basic relation and alert rules. Requires `pytest-operator` and a live Juju model.
- `tests/integration/test_charm_tracing.py`: Tests charm-tracing integration with tempo-k8s. Not run (requires live model).
- `tests/integration/test_upgrade_charm.py`: Permanently skipped due to cross-base upgrade limitation.

### Test gaps (what the 16 passing tests don't cover)

1. **`consumer_events.relation_broken` not triggering status update** — no test exercises `relation-broken` on the consumer side. This is the most critical runtime bug found in this review.
2. **YAML config validation failure** — no test sets `relabel_configs="[not: valid"` and asserts `BlockedStatus` or graceful degradation.
3. **Invalid duration strings** — no test sets `scrape_interval="abc"` or `"-5s"` and asserts the charm sets `BlockedStatus`.
4. **Empty string scrape_interval** — no test sets `""` and asserts empty values are stripped or causes a `BlockedStatus`. This is known issue #31 (open).
5. **Negative integer config values** — no test sets `sample_limit=-1` and asserts range validation.
6. **Recovery from ErrorState** — no test verifies that correcting a bad YAML config + `juju resolve` returns the charm to `active`.
7. **`targets_changed` event** — no test fires `self._metrics_providers.on.targets_changed` and asserts the charm re-renders configs for all consumers.
8. **BSON 16MB limit** — cannot be tested in unit tests (requires year-scale accumulated data). This is known issue #70 (open).
9. **`prometheus_scrape` library silently dropping jobs** — no test simulates invalid upstream scrape config and asserts the charm sets `BlockedStatus`.

## Docs

- **`README.md`**: Mostly clear and correct. The "blocked state" section is correct — "only to prometheus" means only consumer (prometheus), no provider → blocked "missing metrics provider". The `juju status` examples match observed behavior.
- **`INTEGRATING.md`**: Mermaid diagrams, config provision table. Good. **Typo found**: `promethehus` instead of `prometheus` in the table footnotes.
- **`CONTRIBUTING.md`**: Mentions `tox -e lint` and `tox -e unit` but the project uses `uv run ruff` and `uv run pytest`. The `CONTRIBUTING.md` also shows `virtualenv -p python3 venv` and `charmcraft pack` as the build path. The project uses `uv` throughout (`uv run pytest`, `uv run ruff`, `charmcraft.yaml` with `plugin: uv`). This is a doc/reality mismatch.
- **`charmcraft.yaml` description**: Matches observed behavior. Workloadless nature is correctly described.
- **Charmhub**: Published at 3.0/stable rev 75. Channels, bases, and links all correct.
- **`charms.just` PYTHONPATH bug**: `charms.just:5` sets `export PYTHONPATH := ".:./lib:./src"`. The leading `.` (repo root) is correct but misleading — `charm.py` is at `src/charm.py`, not at the root. Not exercised since `just` is not installed.

## Open questions

1. **Why is `consumer_events.relation_broken` missing?** Was this intentional? The asymmetry with `provider_events.relation_broken` being observed suggests an oversight rather than a design decision. The `targets_changed` event fires on provider `relation_broken` via the library, but there is no equivalent for consumer `relation_broken`. Git history shows commit `111e4ec Observe start too (#28)` added `self.on.start` but never added consumer `relation_broken`.
2. **The `receive-ca-cert` relation**: Requires a `certificate_transfer` interface provider. No such charm was available in this environment. What charm provides `certificate_transfer`? Is there a canonical choice in the COS stack?
3. **The observability_libs deprecation in tests**: The tests still use `charms.observability_libs.v0.juju_topology` despite `cosl` being a direct dependency. This should be migrated.
4. **LXD machine charm testability**: Since prometheus-k8s and avalanche-k8s are k8s-only, the full relation chain cannot be tested on LXD. grafana-agent (machine) doesn't provide `metrics-endpoint`. Is there any machine-compatible charm that provides `prometheus_scrape` and could be used for integration testing on LXD?
5. **Upgrade path**: The `upgrade_charm` hook is observed and triggers `_update_all_metrics_consumers`. The permanently skipped upgrade test is due to cross-base (24.04→26.04) not being supported by `juju refresh`. A same-base upgrade test would be valuable.
6. **`juju resolve` vs auto-recovery**: The charm goes to error state on bad YAML and requires `juju resolve` to recover. Would a try/except in the YAML parsing allow the charm to stay blocked (more graceful) instead of crashing?
