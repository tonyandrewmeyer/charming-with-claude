# opentelemetry-collector-k8s

A well-engineered k8s charm with a clean reconciler pattern, 19 integration endpoints, 94% test coverage, and zero lint issues. Runtime testing on both Juju 3.6 and 4.x (four separate deployments) confirmed robust recovery from TLS churn, workload kills, pod deletion, and scaling. Two defects stand out: bad `processors` YAML drives the charm into a silent error loop instead of `BlockedStatus`, and the guard meant to warn operators about data duplication when scaling without ingress (open issue #188) never fires in practice, despite being confirmed present in the code. Numeric config options (`queue_size`, `max_elapsed_time_min`, `tracing_sampling_rate_*`) also accept out-of-range values silently. A maintainer should fix the `processors` error handling first (one-line try/except, matches an existing sibling pattern) and then investigate why the ingress-missing check never triggers, since it protects against a known data-loss scenario. The architecture underneath — reconciler pattern, config-hash restart trigger, `ConfigBuilder` abstraction, internal telemetry loop breaker — is worth studying as a reference implementation.

| | |
|---|---|
| Repo | canonical/opentelemetry-collector-k8s-operator @ `856c030` (2026-07-23) |
| Charms | opentelemetry-collector-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5) and concierge-k8s-3 (Juju 3.6.25), both charmhub 2/edge rev 210, four separate models over two rounds |
| Reviewed | 2026-07-26 |

## What it does

Deploys the OpenTelemetry Collector as a Juju-managed workload on Kubernetes. It receives metrics, logs, traces, and profiles from related charms (via `receive-otlp`, `receive-loki-logs`, `receive-traces`, `metrics-endpoint`, etc.) and forwards them to backends like Prometheus/Mimir, Loki, Tempo, and Grafana Cloud. It also handles TLS termination, ingress via Traefik/Istio, Grafana dashboard aggregation, and cross-model OTLP forwarding.

## Deployment log

```bash
# First round: quick smoke test
juju add-model rv-otel4 --controller concierge-k8s-4
juju deploy opentelemetry-collector-k8s --channel 2/edge otelcol
juju trust otelcol --scope=cluster
# → rev 210 on ubuntu@24.04/stable, Active, workload 0.130.1

juju add-model rv-otel3 --controller concierge-k8s-3
juju deploy opentelemetry-collector-k8s --channel 2/edge otelcol
juju trust otelcol --scope=cluster
# → rev 210 on ubuntu@24.04/stable, Active

# Second round: deeper experiments (after first models destroyed)
juju add-model rv-otel-deep1 --controller concierge-k8s-3
juju add-model rv-otel-deep2 --controller concierge-k8s-4
juju deploy opentelemetry-collector-k8s --channel 2/edge otelcol --model concierge-k8s-3:rv-otel-deep1
juju trust otelcol --scope=cluster --model concierge-k8s-3:rv-otel-deep1
juju deploy opentelemetry-collector-k8s --channel 2/edge otelcol --model concierge-k8s-4:rv-otel-deep2
juju trust otelcol --scope=cluster --model concierge-k8s-4:rv-otel-deep2
# → both Active, workload 0.130.1

# TLS integration
juju deploy self-signed-certificates --channel 1/edge ssc
juju relate otelcol:receive-server-cert ssc:certificates
juju relate otelcol:receive-ca-cert ssc:send-ca-cert
# → WaitingStatus "CSR sent; otelcol down while waiting for a cert" ~15s, then Active
```

## Observed behaviour

### Both Juju versions (3.6 and 4.x)
Identical behaviour on both controllers. No Juju-version-specific differences observed in any test.

### Resource usage at idle
6m CPU, 55Mi memory for the otelcol container with only self-monitoring and OTLP receiver active.

### Startup time
~40 seconds from pod creation to active status (install → pebble-ready → config-changed → start → pebble-ready → active).

### TLS integration (both Juju versions, two separate deployment rounds)
- Adding `receive-server-cert` to `self-signed-certificates`: charm goes to `WaitingStatus("CSR sent; otelcol down while waiting for a cert")` for ~15s, workload stops, then Active once the cert is issued. Good: stops the workload rather than running with incomplete TLS.
- Cert files written to `/etc/otelcol/otelcol-server-cert.crt` and `/etc/otelcol/otelcol-private-key.key`.
- Rendered config gets `tls: {cert_file: ..., key_file: ...}` blocks under both grpc and http OTLP protocols.
- CA certs from `receive-ca-cert` written to `/usr/local/share/ca-certificates/juju_receive-ca-cert/`.
- Removing `server-cert`: cert files cleaned up, TLS blocks removed, charm stays Active.
- Removing `ca-cert`: CA certs cleaned up, charm stays Active.
- Removing and re-adding both relations repeatedly: clean transition every time.
- Killing the workload while TLS is active: Pebble restarts it, TLS config stays intact.

### Workload kill
- Single kill (`kubectl exec ... -- pkill -9 otelcol`): Pebble auto-restarts within 3–5s. Charm stays Active throughout.
- Three rapid kills (< 1s apart): all three recovered, Pebble service "active" after each. Charm never left Active.
- Confirmed on both Juju 3.6 and 4.x.

### Pod restart (unit-level recovery)
- `kubectl delete pod otelcol-0`: StatefulSet recreates the pod within ~11s. Charm goes through the install cycle and reaches Active within ~30s of deletion (including Juju agent reconnection).
- No data-loss risk observed (`file_storage` extension is configured but no storage relations existed in this test).

### Scale up/down (confirmed across four deployments, both Juju versions)
- Scale to 2: both units Active. **No "Ingress missing" BlockedStatus appears on the leader** — see findings.
- Scale to 3: all three units Active. Still no ingress warning.
- Scale down to 1: extra units terminate cleanly, leader stays Active.
- Scale to 2 with TLS active: unit/1 goes to `WaitingStatus("CSR sent...")` for ~20s until ssc issues its cert, then Active.
- The guard at `src/charm.py:382-391` (`self.app.planned_units() > 1 and not otelcol_address.ingress`) never fired across four separate scaling events on both Juju versions, with and without TLS. Leader status was confirmed True via `juju exec --unit otelcol/0 -- is-leader`.

### Config validation — failure injection
- `global_scrape_interval="invalid"` → **BlockedStatus** with a clear message; recovers when fixed. ✓
- `processors="{invalid"` (bad YAML) → **error state**, "hook failed: config-changed", retried every ~5s. No BlockedStatus. Recovery after fixing takes ~20s (Juju 3.6) to ~30s (Juju 4.x). See finding below.
- `queue_size=-1` → **silently accepted**, stays Active.
- `max_elapsed_time_min=-1` → **silently accepted**.
- `tracing_sampling_rate_charm=-1.0` → **silently accepted**.
- `cpu="not-a-cpu-value"` → **BlockedStatus** from library validation.
- `cpu=""` → **BlockedStatus** from library validation (catches empty string).
- `memory="not-a-memory-value"` → **BlockedStatus** from library validation.
- `tls_insecure_skip_verify=true` → toggle works, service restarts with updated config.

### Config change / restart efficiency
- Setting a config option to its current default (`queue_size=1000`→1000, `max_elapsed_time_min=5`→5): rendered config YAML is byte-identical, `_reload` hash unchanged, Pebble does **not** restart the workload. Good — avoids unnecessary restarts.
- Setting `queue_size=999`: hash changes, Pebble restarts the service (~2s to replan).

### Actions
- `reconcile`: completes in ~2s on both leader and non-leader units, exit code 0. Triggers full re-reconciliation (config rewrite + Pebble replan). Only action available.

### Config file (`/etc/otelcol/config.yaml`)
With no relations: OTLP receiver on `0.0.0.0:4317`/`4318`, self-monitoring prometheus scraper on `:8888`, health check extension on `:13133`, nop exporters on all three pipelines. With TLS: `tls` blocks under receiver protocols. Unit-specific job names and labels. File owned by `root:root`, `644` permissions.

### Pebble checks
Two checks: `up` (HTTP health on `:13133`, `level=alive`, `period=30s`) and `valid-config` (`otelcol validate --config=/etc/otelcol/config.yaml`, `level=alive`). Both pass on all units.

### Ports
All 8 ports opened unconditionally (`3500, 4317-4318, 8888, 9411, 13133, 14250, 14268`), including for protocols with no active relations. A TODO at `src/charm.py:357` acknowledges this.

### Ingress integration attempt
Deployed `traefik-k8s` on Juju 4.x, but traefik needs cluster-scoped permissions to list services (403 Forbidden) on this cluster — an RBAC limitation, not a charm bug. Ingress code path was not exercised at runtime.

### Juju refresh
Only revision 210 exists across all channels (2/stable, candidate, beta, edge). Multi-revision upgrade path could not be tested.

### Teardown
`juju remove-application otelcol` and `juju destroy-model` both terminate cleanly. Pods, services, secrets, storage all removed. No stuck resources.

## Findings

### Bad `processors` YAML causes an error loop instead of BlockedStatus
- **Severity**: critical
- **Kind**: bug / ux
- **Where**: `src/config_manager.py:624` (the `yaml.safe_load()` call inside `add_custom_processors()`), call site `src/charm.py:341`
- **Evidence**: Setting `processors="{invalid"` causes `yaml.safe_load(processors_raw)` to raise `yaml.YAMLError`, which propagates uncaught through the reconcile method and fails the `config-changed` hook. Juju retries every ~5s. Observed on both Juju 3.6 and 4.x. The parse traceback is only visible in `juju debug-log`, not `juju status`. The sibling method `add_external_configs()` (`src/config_manager.py:705-708`) already wraps the same call in try/except with `logger.error` and a graceful skip.
- **Impact**: An operator tweaking `processors` can lock the charm in a permanent error state with no actionable status message; they must dig through debug-log to find the cause.
- **Fix**: Wrap `yaml.safe_load(processors_raw)` in try/except `yaml.YAMLError`, set `BlockedStatus(f"Invalid processors YAML: {e}")`, and return early — mirroring `add_external_configs()`.
- **Linter rule**: "`yaml.safe_load()`/`json.loads()` of a config value without try/except in a reconciler" — mechanically checkable.

### Ingress-missing BlockedStatus never fires — confirmed defect across all deployments
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:382-391`
- **Evidence**: Across four separate deployments (rv-otel3, rv-otel4, rv-otel-deep1, rv-otel-deep2), at scales 2 and 3, on both Juju 3.6 and 4.x, with and without TLS, the leader unit never showed `BlockedStatus("Ingress missing - routing only to leader; see debug-log")`, and the corresponding `logger.warning()` never appeared in debug-log:
  ```python
  if self.model.unit.is_leader():
      if self.app.planned_units() > 1 and not otelcol_address.ingress:
          self.unit.status = BlockedStatus(
              "Ingress missing - routing only to leader; see debug-log"
          )
          logger.warning(
              "without ingress and planned_units > 1, all data is forwarded to the leader "
              "unit, with nothing sent to non-leader units."
          )
  ```
  Leader status was confirmed True (`juju exec --unit otelcol/0 -- is-leader`), and `otelcol_address.ingress` was False (no ingress relation) in every case.
- **Impact**: Operators who scale beyond 1 unit without ingress get no warning that non-leader units' telemetry is effectively duplicated/misrouted. This is the exact scenario documented in open issue #188 (open since 2026-04-13), which the guard was meant to catch — the protection exists in the code but has evidently never worked at runtime.
- **Fix**: Instrument the charm to log `planned_units()` and `otelcol_address.ingress` during reconciliation to find why the branch isn't reached (candidates: `planned_units()` returning 1 unexpectedly, or `_reconcile()` exiting early at an earlier status check). A locally packed charm with added logging would settle it.
- **Linter rule**: not mechanically checkable.

### Config values silently accept out-of-range inputs
- **Severity**: high
- **Kind**: bug
- **Where**: `charmcraft.yaml` config section; `src/charm.py:238,309-313`; `src/config_manager.py:153-163`
- **Evidence**: Five numeric config options declare bare `int`/`float` with no `minimum`/`maximum`: `queue_size` (int, default 1000), `max_elapsed_time_min` (int, default 5), `tracing_sampling_rate_charm`/`tracing_sampling_rate_workload`/`tracing_sampling_rate_error` (float, defaults 100.0/1.0/100.0). `queue_size=-1` and `max_elapsed_time_min=-1` were both silently accepted in testing and would render `queue_size: -1` / `max_elapsed_time: -1m` into `sending_queue` config blocks if a non-nop exporter were configured — these would fail otelcol at startup.
- **Impact**: Operators can set values that produce an invalid otelcol config with no charm-level warning; the workload only fails on its next restart.
- **Fix**: Add `minimum: 1` to `queue_size`, `minimum: 0` to `max_elapsed_time_min`, and `minimum: 0.0, maximum: 100.0` to the three `tracing_sampling_rate_*` options in `charmcraft.yaml`, so Juju rejects out-of-range values before they reach the charm.
- **Linter rule**: "Config option of type int/float without a `minimum` constraint" — mechanically checkable via static analysis of `charmcraft.yaml`.

### `cast(bool, …)` on float tracing-rate config values
- **Severity**: medium
- **Kind**: bug / lint
- **Where**: `src/charm.py:309-313`
- **Evidence**:
  ```python
  sampling_rate_charm=cast(bool, self.config.get("tracing_sampling_rate_charm")),
  sampling_rate_workload=cast(bool, self.config.get("tracing_sampling_rate_workload")),
  sampling_rate_error=cast(bool, self.config.get("tracing_sampling_rate_error")),
  ```
  These options are declared `type: float` in `charmcraft.yaml`; `config_manager.add_traces_processing()` expects `sampling_rate_charm: float`. `cast()` is a no-op at runtime, so values flow through correctly, but the annotation is wrong.
- **Impact**: Harmless today, but a future refactor that makes `cast` meaningful (or a static checker that trusts it) could silently break sampling-rate handling.
- **Fix**: Replace `cast(bool, ...)` with `cast(float, ...)`.
- **Linter rule**: "`cast()` type argument must match the declared config option type" — checkable by cross-referencing `charmcraft.yaml`.

### Dashboard filename accumulation (open #237)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/integrations.py:429-454`
- **Evidence**: Open issue #237, unaddressed since 2026-04-30: repeated `storage-attached` hook failures cause `grafana_dashboards/` filenames to accumulate `juju_file:` prefixes, eventually hitting `OSError: [Errno 36] File name too long`. (unverified at runtime — not reproduced in this review, taken from the issue tracker.)
- **Impact**: Storage-attached hook retries can fill the filesystem with garbage filenames.
- **Fix**: Strip accumulated `juju_file:` prefixes before writing, or write to a temp path and atomically rename.
- **Linter rule**: not mechanically checkable.

### `send_otlp()` instantiates `OtlpRequirer` twice
- **Severity**: low
- **Kind**: performance
- **Where**: `src/integrations.py:596-604`
- **Evidence**:
  ```python
  OtlpRequirer(charm, ..., rules=rules, ...).publish()  # first instance
  return OtlpRequirer(charm, protocols=[...], ...).endpoints  # second instance
  ```
- **Impact**: Doubles the relation-data walking work on every reconciliation.
- **Fix**: Create a single `OtlpRequirer` instance, call `.publish()`, then return its `.endpoints`.
- **Linter rule**: "Sequential instantiation of the same library class in the same function" — mechanically checkable.

### Unconditional log processors injected into pipeline
- **Severity**: low
- **Kind**: performance
- **Where**: `src/config_manager.py:248-280`
- **Evidence**: `resource/send-loki-logs` and `attributes/send-loki-logs` processors are added to the logs pipeline unconditionally, even with no log ingestion or forwarding configured. Comment in code: `# TODO: Luca: this was gated by having outgoing logs. Do we need that?`.
- **Impact**: Wasted CPU processing LogRecords that go straight to a nop exporter.
- **Fix**: Gate the processors on `if self._incoming_logs or any_loki_endpoints`.
- **Linter rule**: not mechanically checkable.

### No explicit `upgrade-charm` handler; revision not in the reload hash
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:139-147`, `src/charm.py:347-354`, `charmcraft.yaml` build step
- **Evidence**: `charmcraft.yaml` writes `git describe --always > $CRAFT_PART_INSTALL/version` during build, but the charm code never reads that file. The `_reload` Pebble env-var hash is derived from config hash + cert hashes only, not charm revision.
- **Impact**: A bug-fix charm upgrade that doesn't change rendered config won't restart the workload; the operator must manually run the `reconcile` action.
- **Fix**: Include the charm revision or version-file content in the `_reload` hash, or observe `upgrade-charm` and force a restart.
- **Linter rule**: "Reconciler charm with no upgrade-charm handler and no version/revision in the restart hash" — partially checkable.

### `add_custom_processors` lacks the error handling present in sibling `add_external_configs`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/config_manager.py:618-624` vs `src/config_manager.py:705-708`
- **Evidence**: `add_external_configs()` wraps its `yaml.safe_load()` in `try: ... except yaml.YAMLError as e: logger.error(...); continue`; `add_custom_processors()` performs the same kind of parse with no such guard.
- **Impact**: Same root cause as the critical `processors` finding above — recorded separately because it documents an inconsistency between two otherwise-parallel methods, suggesting an oversight rather than a deliberate design choice.
- **Fix**: Apply the same try/except pattern from `add_external_configs()` to `add_custom_processors()`.
- **Linter rule**: "Sibling methods with inconsistent error handling for the same operation" — mechanically checkable.

### xpassed test: `test_incoming_rules_forwarded_to_send_otlp [metrics-endpoint-to-send-otlp-False]`
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_otlp.py:374`
- **Evidence**: The `forward_rules=False` sub-case xpasses because `expected_alerts` is `{"ScrapeEndpointAlert"}` regardless of `forward_rules`; when forwarding is disabled no rules leak, so the assertion passes vacuously. The `True` sub-case correctly xfails against a real forwarding bug.
- **Fix**: Make `expected_alerts` conditional (`{"ScrapeEndpointAlert"} if forward_rules else set()`) and mark the xfail `strict=True`.
- **Linter rule**: not mechanically checkable.

### `_otelcol_version` regex overly permissive
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:528`
- **Evidence**: `r"version (\d*\.\d*\.\d*)"` uses `\d*` (zero-or-more), which matches empty strings.
- **Fix**: Use `\d+`: `r"version (\d+\.\d+\.\d+)"`.
- **Linter rule**: "Regex with `\d*` in a version capture group" — mechanically checkable.

### `key_value_pair_string_to_dict` error paths uncovered
- **Severity**: nit
- **Kind**: test-gap
- **Where**: `src/integrations.py:200-201, 206-207, 209-210`
- **Evidence**: 0% coverage on error-handling branches (empty key, empty value, missing separator).
- **Fix**: Add unit tests for these edge cases.
- **Linter rule**: not mechanically checkable.

## Worth copying

* **Reconciler pattern** (`src/charm.py:139-148`): the entire charm state is rebuilt from scratch on every hook inside `_reconcile()`. No event handlers, no deferred events, no stored state. Clean for a charm with 19 integration endpoints.
* **Config hash as Pebble restart trigger** (`src/charm.py:347-354`): a hash of the rendered config plus cert hashes is stored in a Pebble environment variable `_reload`; Pebble restarts the service only when it changes. Verified: no-op config changes leave the hash unchanged and don't trigger a restart.
* **`ConfigBuilder` abstraction** (`src/config_builder.py`): builds otelcol config as a Python dict and serializes to YAML only at the end; `add_component()` handles both component definition and pipeline wiring — cleaner than template-based generation.
* **Internal telemetry loop breaker** (`src/config_builder.py:210-255`): feeds the collector's own logs back into its log pipeline but prevents infinite recursion with a filter processor that drops logs originating from any exporter on the logs pipeline, with filter conditions populated dynamically at build time.
* **Multiple ingress support with clean error** (`src/charm.py:204-206`): returns `MultipleIngressesConfigured` with a clear message when both Traefik and Istio are active, handled with `match/case`.
* **Comprehensive integration test matrix** (10 test files): covers standalone deployment, tracing across multiple backends, logs, metrics, OTLP with TLS, CA certs, profiling, and ingress, each against real partner charms with data assertions, not just status checks.
* **Status precedence** (`src/charm.py:170-391`): a clear order — resource patch → validation → active → mandatory relations → cyclic check → ingress check — with later checks overriding earlier ones. No races observed.
* **TLS workload stoppage** (`src/charm.py:365-368`): stops the otelcol workload and sets `WaitingStatus` while waiting for a cert, avoiding running with invalid TLS.
* **Pebble `valid-config` check** (`src/charm.py:449-456`): runs `otelcol validate --config=...` as a Pebble health check, catching config problems that slip past charm-level validation.

## Common-practice notes

* **Library versioning**: standard `lib/charms/<name>/v<N>/` convention; 14 charm libraries, kept up to date.
* **charmcraft.yaml**: modern `platforms` syntax (`ubuntu@26.04:amd64`, `arm64`); `assumes: [k8s-api, juju >= 3.6]`; UX plugin for Python deps.
* **No `metadata.yaml`**: single source of truth in `charmcraft.yaml` — modern convention.
* **charmlibs external dependency**: `charmlibs.pathops` and `charmlibs.interfaces.otlp` come from pip rather than being vendored under `lib/charms/` — deliberate for a shared OTLP interface.
* **Config-driven design**: almost all behaviour is controlled via Juju config and relation data; `processors` config allows arbitrary YAML injection.
* **Config validation inconsistency**: `global_scrape_interval` is validated inline via regex, `cpu`/`memory` via library validation (`KubernetesComputeResourcesPatch`), while `processors`, `queue_size`, `max_elapsed_time_min`, and `tracing_sampling_rate_*` have no validation at all — bad values can produce `BlockedStatus`, an error loop, or silent acceptance depending on which option is misconfigured.
* **Leader-only operations**: tracing receivers, profiling endpoints, dashboard forwarding, and ingress config are all gated on `is_leader()` — standard practice.
* **cos-tool binary**: fetched from GitHub releases at build time rather than built from source — practical but unusual.

## Tests

**Unit tests** (`tox -e unit`, 136 passed, 1 skipped, 1 xfailed, 1 xpassed, ran cleanly):
- Framework: `ops-scenario` (state-transition testing), not `unittest`+`Harness`.
- Coverage: 94% overall (`src/config_builder.py` 98%, `src/integrations.py` 93%, `src/charm.py` 93%, `src/config_manager.py` 92%).
- Gaps matching the findings above: no test for bad `processors` YAML → status; no test for `key_value_pair_string_to_dict` edge cases; no test for the ingress/scaling check; no test for negative config values; no test for upgrade-charm behaviour; `add_custom_processors` loop body has 0% coverage.

**Integration tests** (10 files, `jubilant` framework, not run — require a full Juju environment with partner charms):
- `test_charm.py`: smoke test (Pebble checks).
- `test_tracing.py`: full traces pipeline (grafana → otelcol → tempo) with data assertions across multiple tempo backends.
- `test_logs.py`, `test_metrics.py`, `test_forwarding_otlp_telemetry.py`: log/metric/OTLP pipelines.
- `test_otlp_tls.py`, `test_recv_ca_cert.py`: TLS-specific.
- `test_profiling.py`, `test_ingress.py`: profiling and ingress features.

**Static analysis**: ruff (0 issues), pyright (0 errors, 0 warnings). codespell is configured but not enforced in CI.

## Docs

* **README.md**: good — explains the design (reconciler pattern, "all telemetry to all exporters"), usage examples, OCI images, sample deployment with a mermaid diagram.
* **charmhub description**: comprehensive, matches observed behaviour.
* **CONTRIBUTING.md**: functional, minimal; points to Juju SDK docs and `tox` commands.
* **Terraform module** (`terraform/`): README, `main.tf`, `variables.tf`, `outputs.tf`, integration tests; supports Juju provider v1 and v2; good variable documentation.
* **`.github/copilot/`**: five markdown files for LLM-oriented code overview — unusual but useful.
* **Doc/reality gap**: README says to deploy with `--resource opentelemetry-collector-image=...` but charmhub auto-resolves the resource. HEAD builds target `ubuntu@26.04` while deployed rev 210 is on `24.04` — a base transition in progress.

## Open questions

* **Why doesn't `self.app.planned_units()` trigger the ingress check?** Confirmed non-firing at scales 2 and 3, on both Juju versions, across four deployments. Settled by instrumenting the charm to log `planned_units()` during reconciliation, or tracing the exact code path with a locally packed charm.
* **Does omitting charm revision from the `_reload` hash cause real problems?** The build-time `version` file is never read by the charm. Settled by a multi-revision upgrade test — not possible currently since only one revision (210) exists on charmhub.
* **Dashboard filename accumulation (open #237)**: unaddressed since 2026-04-30. Settled by reproducing the storage-attached hook failure directly (not attempted in this review; flagged `(unverified)` at runtime).
* **`cast(bool, float)` — intentional or copy-paste?** Three sampling-rate reads use `cast(bool, ...)` against `type: float` config. Settled by asking the author.
