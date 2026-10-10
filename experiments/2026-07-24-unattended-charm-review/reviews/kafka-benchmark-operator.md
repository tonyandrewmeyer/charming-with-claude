# kafka-benchmark-operator

A benchmarking charm for Apache Kafka using the OpenMessaging benchmark tool, maintained by the Canonical Data Platform team. It orchestrates distributed producer/consumer load generation across Juju units and exposes metrics to Prometheus via COS integration.

The lifecycle/state-machine architecture is clean and lint hygiene is good (`pyright` 0 errors, `ruff`/`codespell` clean), but the benchmark itself is broken in practice: `duration` and `run_count` config are effectively ignored due to two compounding bugs in the wrapper loop, `get-summary` has no handler, TLS has two independent defects, and a preflight check blocks the simplest single-unit deploy. Test coverage on the charm's own code (`charm.py`, `tls.py`, `models.py`) is 0%. A maintainer should first fix the `run_count`/`duration` wrapper bugs (findings #1–#2 below) since they invalidate the charm's core promise — a benchmark that runs for a configured duration — then wire up `get-summary` and fix the TLS secret handling.

| | |
|---|---|
| Repo | canonical/kafka-benchmark-operator @ `50c335a` (2026-06-18) |
| Charms | kafka-benchmark |
| Substrate | machine (k8s supported via Pebble workload) |
| Deployed | yes — concierge-lxd (Juju 3.6), latest/edge rev 4; concierge-k8s-3 (Juju 3.6), latest/edge rev 4. concierge-lxd-4 (Juju 4.0.5) attempted but failed to provision (machines stuck pending, no Juju agent installed) |
| Reviewed | 2026-07-31 |

## What it does

Deploy this charm alongside a Kafka cluster, prepare a benchmark topic via actions, then run distributed OpenMessaging benchmark workloads (workers on each unit, coordinator on the leader). Metrics are scraped by Prometheus via a `metrics-endpoint` relation and forwarded through `grafana-agent`. TLS to Kafka is supported via a `trusted-ca` integration (a workaround until Kafka shares certs through the client relation).

## Deployment log

### LXD on Juju 3.6 (concierge-lxd)

**First deployment** (model `rv-kafka-benchmark`):
```
juju add-model rv-kafka-benchmark --controller concierge-lxd
juju deploy kafka-benchmark --channel latest/edge     # rev 4
juju deploy kafka --channel 3/edge                     # rev 258
juju deploy zookeeper --channel 3/edge                 # rev 164
juju relate kafka zookeeper
juju relate kafka kafka-benchmark
juju config kafka-benchmark parallel_processes=2
```
~13 min to active. Preflight check blocked single-unit deploy with `parallel_processes=1`. Actions `prepare`/`run`/`stop`/`cleanup` worked. `get-summary` hung.

**Second deployment** (model `rv-kafka-deep`), same setup plus `self-signed-certificates`:
- Same action results as above, plus a TLS relation attempt (kafka went blocked — zookeeper also needs TLS), a kill-workload test (failure undetected for 5 min), and an invalid-config test (crash).

**Third deployment** (model `rv-kafka-v3`, deeper pass) — full lifecycle: prepare → run → stop → scale-up attempt → tear-down.
- `duration=30, run` started the benchmark (enters the loop via condition 1 with the wrapper's default `run_count=1`, not via the duration condition).
- `threads=0` config change crashed the charm with a `pydantic.ValidationError` (same bug class as finding #7 — the `ge=1` validator triggers unchecked). `threads=100000` was accepted with no upper bound. `duration=-1` was accepted by `juju config` but would presumably crash the next hook via a `ge=0` validator.
- Scale-up: second unit stuck at `pending` for >10 min — cloud-init running but no Juju agent installed. Unit removed and review continued.
- `remove-application`: clean tear-down; kafka and zookeeper remained running with no errors.

### Kubernetes on Juju 3.6 (concierge-k8s-3)

Model `rv-kafka-k8s`, kafka-benchmark + kafka-k8s + zookeeper-k8s:
- `prepare`: topic `benchmark_topic` created with 6 partitions, RF=1. Works correctly.
- `run`: Pebble layer added, service `dpe-benchmark` started, coordinator and 2 workers started in the same pod. **Benchmark exited after ~130ms** — the coordinator issued "Stop All" almost immediately, status showed "Benchmark finished." Root cause: the wrapper's `run_count` defaults to 1 and is never overridden from charm config, so it runs one workload cycle and the coordinator exits, which stops the Pebble service. On LXD the coordinator process is long-running, so the loop stays alive via the same default — the same underlying bug manifests oppositely on the two substrates.
- `get-summary`: confirmed non-functional — action completes with no result; nobody observes `get_summary_action`.
- `stop`: not tested on k8s.

### Juju 4.0.5 on LXD (concierge-lxd-4)

**Failed**: model `rv-kafka-4` — 3 LXD containers created and running, but all 3 machines stuck at `pending` for >5 min. Cloud-init status stayed "running," `/var/lib/juju/` never appeared (agent never installed). Model destroyed. Root cause not established — likely environmental, not charm-specific; concierge pins Juju 3.6/stable and there's no evidence the charm has been tested against 4.x.

## Observed behaviour

- **Install time**: ~11 min for kafka-benchmark (`apt install openjdk-18-jre` is the bottleneck). Total time to active with kafka+zookeeper: ~13–15 min.
- **Memory**: each Java worker JVM reserves 4GB heap but actual RSS is ~500–600MB per worker, ~300MB for the coordinator; total ~1.4GB RSS at `parallel_processes=2`.
- **Systemd on LXD**: runs as root (`User=root`); wrapper logs to `/var/log/dpe_benchmark_workload.log`.
- **Pebble on k8s**: service `dpe-benchmark` added via `pebble add --combine` then `pebble replan`; starts/stops inside the same `charm` container as `container-agent`.
- **Hook count**: `config-changed` triggers ~4–8 systemctl calls; each action triggers 4–8 systemctl calls.
- **KafkaAdminClient**: a new `KafkaConfigManager` (and `KafkaClient`) is created per hook execution, but connections are shared within a hook via `@cached_property`, so this is less wasteful than it first appears.
- **Config change during benchmark**: triggers stop → re-render → restart; `_check()` re-reads and re-renders both config files on every hook.
- **Prometheus metrics**: exposed on port 8008 via `prometheus_client.start_http_server(8008)` in the wrapper; port is NOT declared in `metadata.yaml`.
- **Action logs**: every action produces `WARNING:prometheus_scrape: 0 containers are present in metadata.yaml` and `WARNING:ops.framework: ActionsHandler has been garbage collected`.
- **`run_count`/wrapper mismatch**: charm config `run_count` defaults to 0 (indefinite), but neither the systemd nor the Pebble template passes `--run_count` to the wrapper. The wrapper's argparse defaults to `run_count=1`, so it always runs exactly one benchmark cycle and exits, regardless of configured `run_count`.
- **Duration bug confirmed live**: `juju config duration=120; juju run ... run` starts the benchmark via condition 1 (`run_count=1`), not via the duration condition, and then runs indefinitely because the coordinator never exits on its own and condition 1 stays true forever — `duration` is completely ignored. This matches open issue #29 ("Run never ends").
- **COS integration gap**: `COSAgentProvider` is initialized with empty `metrics_endpoints=[]` in `DPBenchmarkCharmBase.__init__`; scrape configs from `self.scrape_config()` go to `MetricsEndpointProvider` but not to `COSAgentProvider`, so COS metrics forwarding may not work as intended.
- **Juju 4.0.5 failure**: unresolved, likely environment-specific (unverified).

## Findings

### 1. `run_count` never passed from charm config to wrapper — wrapper always defaults to 1
- **Severity**: critical
- **Kind**: bug
- **Where**: `templates/kafka_benchmark.service.j2:8`, `templates/kafka_benchmark_pebble_layer.yaml.j2:7`, `src/benchmark/managers/config.py:97-110`
- **Evidence**: the service and Pebble templates pass `--duration={{ duration }}` but no `--run_count`. The wrapper's argparse defaults to `run_count=1`. `get_execution_options()` correctly computes `run_count=self.config.run_count` (default 0), but this value never reaches the wrapper CLI.
- **Impact**: the wrapper always runs exactly one benchmark cycle regardless of configured `run_count`. On k8s the coordinator exits quickly, so the benchmark "finishes" in ~130ms (confirmed live). On LXD the coordinator is long-lived, so condition 1 (`run_count < 1`) keeps the loop alive indefinitely — but the configured value is still ignored either way. This also masks finding #2: if `run_count` were correctly propagated as 0, the `>=` bug there would prevent the benchmark from ever starting when `duration > 0`.
- **Fix**: add `--run_count={{ run_count }}` to both templates; ensure `_service_args()` in `KafkaConfigManager` (and the base `_render_service()`) include `run_count` in the template context.
- **Linter rule**: not mechanically checkable — requires cross-referencing template variables against config keys.

### 2. Duration timer condition inverted — timed benchmarks never behave correctly
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/benchmark/wrapper/process.py:103-106`
- **Evidence**:
```python
while (
    (run_count < self.args.run_count and self.args.run_count != 0)
    or (int(time.time()) >= finish_time and self.args.duration != 0)   # should be <
    or (self.status() == ProcessStatus.RUNNING and self.args.duration == 0)
):
```
`>=` means "keep running AFTER the duration has expired" instead of "keep running WHILE there's time remaining." With `duration > 0` and `run_count = 0`, at t=0 all three conditions are false and the loop never enters — the benchmark never starts. In practice this is masked by finding #1 (wrapper defaults `run_count` to 1), which enters the loop via condition 1, but then `duration` is ignored entirely and the run never stops. Open issue #29 (2025-05-15), "Run never ends when duration>0," is explained by exactly this interaction.
- **Impact**: the `duration` feature described in `config.yaml` ("Time in seconds to run the benchmark, 0 means indefinitely") is completely broken — setting `duration=120` either prevents the benchmark from starting or has no effect.
- **Fix**: change `>=` to `<` on line 105. Combined with the fix for finding #1, `run_count=0, duration=120` would then run for 120s via condition 2 and exit correctly.
- **Linter rule**: not mechanically checkable — requires semantic understanding of loop invariants.

### 3. Secret reference stale after `add_secret()` — truststore password inaccessible in-hook
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/tls.py:188-197` (also referenced as `163-165` in notes)
- **Evidence**:
```python
@truststore_pwd.setter
def truststore_pwd(self, pwd: str) -> None:
    if not self.is_leader:
        return
    if not self.truststore_pwd:
        self.app.add_secret({TS_PASSWORD_KEY: pwd}, label=TRUSTSTORE_LABEL)
        # self.secret is never assigned; should be:
        # self.secret = self.app.add_secret(...)
        return
```
`self.secret` is never updated when the leader creates the secret, so a subsequent read of `truststore_pwd` within the same hook returns `None`. It becomes visible on the next hook because `JavaTlsHandler` is re-created per hook.
- **Impact**: `set_truststore()` fails silently within the hook that creates the secret. Combined with finding #11 (secret not refreshed on leader change) and a possible leader/non-leader timing race, this explains open issue #41 ("benchmarks not working with TLS").
- **Fix**: capture the return value: `self.secret = self.app.add_secret(...)`.
- **Linter rule**: "return value of side-effect function not captured" — mechanically checkable by some linters.

### 4. Overly restrictive preflight check blocks single-unit deploys
- **Severity**: high
- **Kind**: bug | ux
- **Where**: `src/charm.py:476-484`
- **Evidence**:
```python
if int(self.config.parallel_processes) * len(self.charm.peers.all_unit_states().keys()) < 2:
    logger.error("The number of parallel processes must be greater than 1.")
    self.unit.status = BlockedStatus(...)
    return False
```
With 1 unit and the default `parallel_processes=1`, `1 * 1 = 1 < 2` is true, so the charm blocks. `_on_collect_unit_status` does not run this check, so the `BlockedStatus` gets overwritten by "waiting" — the operator never sees the actual reason.
- **Impact**: a fresh deploy with default config cannot progress; only the integration test's `DEFAULT_NUM_UNITS=2` avoids hitting this.
- **Fix**: relax the condition, or surface the check consistently in `_on_collect_unit_status` with an accurate message.
- **Linter rule**: not mechanically checkable.

### 5. `get-summary` action defined but has no handler
- **Severity**: high
- **Kind**: bug | docs
- **Where**: `actions.yaml:17-31`, absent from `src/charm.py`
- **Evidence**: the action is declared with `output: [table, json]` parameters, but no handler exists in `src/`. Confirmed on both LXD and k8s: the event dispatches and the action completes with no result. Matches open issue #40.
- **Impact**: a documented, user-facing action silently does nothing.
- **Fix**: implement the handler, or remove the action declaration.
- **Linter rule**: "action declared in `actions.yaml` has no matching observer" — mechanically checkable.

### 6. Unhandled `pydantic.ValidationError` on invalid config
- **Severity**: high
- **Kind**: bug | ux
- **Where**: `lib/charms/data_platform_libs/v0/data_models.py:156` → `src/models.py:77` → `src/charm.py:540`
- **Evidence**: `TypedCharmBase.config` calls `self.config_type(**translated_keys)`. Any pydantic validator rejection propagates uncaught through `super().__init__()` → `ops.main()`. Reproduced with `workload_name=invalid` and `threads=0` (violates the `ge=1` validator in `structured_config.py`); `threads=100000` is accepted with no upper bound, and `duration=-1` is accepted by `juju config` but would presumably crash on the next hook via a `ge=0` validator.
- **Impact**: operators get a raw traceback and a "hook failed" error state instead of `BlockedStatus`; any deferred events are lost. Recoverable by correcting config and running `juju resolve`.
- **Fix**: catch `ValidationError` in `TypedCharmBase.config` and surface it as `BlockedStatus`.
- **Linter rule**: not mechanically checkable.

### 7. Duplicated observer binding for `relation_joined` fires handler twice
- **Severity**: high
- **Kind**: bug
- **Where**: `src/benchmark/events/peer.py:55-57`
- **Evidence**: the same `self.framework.observe(... relation_joined, self._on_new_peer_unit)` call is registered twice.
- **Impact**: doubled systemctl/pebble calls and status transitions on every peer join.
- **Fix**: remove the duplicate `observe` call.
- **Linter rule**: "duplicate `self.framework.observe` calls" — mechanically checkable.

### 8. Slow failure detection — workload death undetected for up to 5 minutes
- **Severity**: high
- **Kind**: bug | ux
- **Where**: `src/benchmark/managers/lifecycle.py:85-100`, default `update-status-hook-interval`
- **Evidence**: killed the workload via `systemctl stop dpe-benchmark`; charm continued reporting "Benchmark is running" for 30+ seconds, until the next `update-status` hook (model default interval 5 min). Integration tests use `update-status-hook-interval: 1m`, which masks the issue in CI.
- **Impact**: a JVM crash or manual stop goes unreported for up to 5 minutes on a default model.
- **Fix**: shorter polling interval, or systemd `WatchdogSec` integration.
- **Linter rule**: not mechanically checkable.

### 9. Base class observer registrations leaked — relation events fire twice
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:540-580` vs `src/benchmark/base_charm.py:95-115`
- **Evidence**: the base class creates `self.database = DatabaseRelationHandler(self, db_relation_name)`, which registers observers. The Kafka subclass then creates `self.database = KafkaDatabaseRelationHandler(self, CLIENT_RELATION_NAME)`, whose `super().__init__()` registers the same observers again. The original `DatabaseRelationHandler` is garbage-collected from `self.database` but remains registered as an `Object` in the ops framework, so both fire on a kafka relation event.
- **Impact**: doubled `_on_config_changed` calls, doubled systemd/pebble operations and config re-renders; extra churn on multi-unit deploys.
- **Fix**: don't create the base `DatabaseRelationHandler`, or let the base class accept an optional `database_handler` parameter.
- **Linter rule**: not mechanically checkable — requires cross-class init analysis.

### 10. `tls_ca` property: dead code, missing return
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:95-100`
- **Evidence**:
```python
@property
@override
def tls_ca(self) -> str | None:
    """Return the TLS CA."""
    if not super().tls_ca:
        return None
    self.tls_relation          # evaluated and discarded, no return
```
- **Impact**: `model().tls_ca` is always `None`. Downstream impact is limited today — the admin client checks for the CA file on disk and workers use `truststore_path`/`truststore_pwd`, not `tls_ca` — but it's latent dead code that would silently break any future consumer, and contributes to issue #41 alongside finding #3.
- **Fix**: add the missing `return`.
- **Linter rule**: "function with declared return type contains bare expression statement with no return/raise" — mechanically checkable; pyright did not catch this.

### 11. Secret not refreshed on leader change
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/tls.py:40-47`
- **Evidence**: `JavaTlsHandler.__init__` fetches the secret once. If the unit wasn't leader at init time, `self.tls_manager.secret` stays `None` forever; when it later becomes leader, the setter's `add_secret()` call fails because a secret with that label already exists.
- **Impact**: after a leader change, the truststore password can't be updated. Contributes to issue #41.
- **Fix**: re-fetch the secret in the getter using `model.get_secret(label=...)`.
- **Linter rule**: not mechanically checkable.

### 12. Topic creation errors swallowed at DEBUG level
- **Severity**: medium
- **Kind**: bug | ux
- **Where**: `src/charm.py:380-397`
- **Evidence**: all exceptions from topic creation are caught and logged at DEBUG. Operator sees "Failed to prepare the benchmark" with no root cause.
- **Fix**: log at ERROR level with exception details.
- **Linter rule**: not mechanically checkable.

### 13. Juju 4.0.5 LXD provisioning failed
- **Severity**: medium
- **Kind**: platform compatibility
- **Where**: deployment attempt on concierge-lxd-4
- **Evidence**: 3 LXD containers running but all machines stuck at `pending`; cloud-init running, no Juju agent installed. Concierge pins Juju 3.6/stable; no evidence of 4.x testing in the repo.
- **Fix**: test on Juju 4.x, or document the support boundary.
- **Linter rule**: not mechanically checkable.

### 14. `run_check_deferred` flag never reset across prepare/run cycles
- **Severity**: medium
- **Kind**: bug (latent)
- **Where**: `src/charm.py:579-603`
- **Evidence**: the flag is set `True` on first defer but never reset.
- **Fix**: reset it in `on_run_action` or `_on_prepare_action`.
- **Linter rule**: not mechanically checkable.

### 15. Wrapper line processing silently discards all parse errors
- **Severity**: medium
- **Kind**: bug (latent)
- **Where**: `src/wrapper.py:82-100`
- **Evidence**: `process_line` is wrapped in a blanket `try/except Exception: return None`. A change in OpenMessaging's output format would silently drop all metrics.
- **Fix**: log a warning on parse failure.
- **Linter rule**: not mechanically checkable.

### 16. `_peers_state()` accesses `self.peers[self.this_unit]` without guard
- **Severity**: low
- **Kind**: bug (latent)
- **Where**: `src/benchmark/managers/lifecycle.py:127`
- **Evidence**: `next_state = self.peers[self.this_unit].lifecycle` raises `KeyError` if `self.this_unit` isn't in `self.peers`.
- **Fix**: use `self.peers.get(self.this_unit, ...)` with a default.
- **Linter rule**: not mechanically checkable.

### 17. Pebble `_is_stopped()` fragile string parsing
- **Severity**: low
- **Kind**: bug (latent)
- **Where**: `src/benchmark/core/pebble_workload_base.py:188`
- **Evidence**: `status.splitlines()[1].split()[2] == "inactive"` assumes at least 2 lines and 3 columns; an `IndexError` is possible if output format changes.
- **Fix**: check lengths before indexing.
- **Linter rule**: "unchecked index access on split result" — mechanically checkable.

### 18. Base `ConfigManager._check()` compares an unused `target_hosts` value
- **Severity**: low
- **Kind**: lint
- **Where**: `src/benchmark/managers/config.py:237`
- **Evidence**: adds `"target_hosts": values.db_info.hosts` to the comparison dict even though the service template doesn't use it; the Kafka override correctly omits it.
- **Linter rule**: not mechanically checkable.

### 19. No `upgrade-charm` handler
- **Severity**: low
- **Kind**: bug (latent)
- **Where**: `src/charm.py` (absence)
- **Evidence**: the charm doesn't observe `upgrade_charm`, relying on `install` + `config_changed` for state init. `install` doesn't fire during `juju refresh`, so stale peer state may persist.
- **Fix**: add an `_on_upgrade_charm` handler.
- **Linter rule**: not mechanically checkable.

### 20. Unnecessary `rustup` in `charmcraft.yaml` build
- **Severity**: low
- **Kind**: performance (build)
- **Where**: `charmcraft.yaml:28`
- **Evidence**: `rustup default stable` and `build-snaps: [rustup]`, with no Rust source anywhere in the repo (possibly leftover from a replaced Rust wrapper, unverified).
- **Fix**: remove both.
- **Linter rule**: "`build-snaps` entry with no corresponding source" — mechanically checkable.

### 21. `prometheus_scrape` warnings on every hook
- **Severity**: low
- **Kind**: lint
- **Where**: observed in `juju debug-log` on every hook
- **Evidence**: `0 containers are present in metadata.yaml and refresh_event was not specified`.
- **Fix**: specify `refresh_events` in `MetricsEndpointProvider`.
- **Linter rule**: not mechanically checkable.

### 22. `ActionsHandler` garbage-collected warning
- **Severity**: low
- **Kind**: bug (latent)
- **Where**: observed on every action
- **Evidence**: `Reference to ops.Object at path KafkaBenchmarkOperator/ActionsHandler has been garbage collected`.
- **Fix**: investigate the reference chain keeping the handler from being retained.
- **Linter rule**: mechanically checkable.

### 23. Service runs as root
- **Severity**: low
- **Kind**: lint | security
- **Where**: `templates/kafka_benchmark.service.j2`, `src/literals.py`
- **Evidence**: no `User=` directive in the systemd template; `LINUX_USER = "root"` in literals.
- **Fix**: run as an unprivileged user if feasible.
- **Linter rule**: "systemd service template missing `User=` directive" — mechanically checkable.

### 24. Double initialization of base class managers
- **Severity**: low
- **Kind**: performance | bug
- **Where**: `src/charm.py:540-580` vs `src/benchmark/base_charm.py:100-130`
- **Evidence**: the base class creates 5+ manager objects that the Kafka subclass immediately replaces; the base instances are garbage-collected but their framework registrations remain (see finding #9).
- **Fix**: refactor to use factories or optional manager overrides.
- **Linter rule**: not mechanically checkable.

### 25. Pydantic v1-style validators
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/benchmark/core/models.py:77` (`@root_validator`), `src/benchmark/core/structured_config.py:26` (`@validator`)
- **Evidence**: unit tests report `PydanticDeprecatedSince20`.
- **Fix**: migrate to `@model_validator` / `@field_validator`.
- **Linter rule**: mechanically checkable with ruff `PYD`.

### 26. `CONTRIBUTING.md` references nonexistent tox environment `static`
- **Severity**: nit
- **Kind**: docs
- **Where**: `CONTRIBUTING.md:15`
- **Evidence**: lists `tox run -e static`, and describes `tox` as running `format, lint, static, unit`; actual `tox.ini` has no `static` env (default is `lint, unit`).
- **Fix**: update `CONTRIBUTING.md`.
- **Linter rule**: mechanically checkable.

## Worth copying

- **State-machine lifecycle**: `src/benchmark/managers/lifecycle.py` — clean state machine with `_LifecycleState` subclasses, each encapsulating its own transition rules, via an easily extensible `_LifecycleStateFactory`.
- **Workload abstraction**: `src/benchmark/core/workload_base.py` — clean ABC for workload operations with `DPBenchmarkSystemdWorkloadBase` and `DPBenchmarkPebbleWorkloadBase` implementations; a good pattern for dual-substrate charms.
- **Config-as-structured-model**: `KafkaBenchmarkCharmConfig` extends `BenchmarkCharmConfig` with workload-name validation through pydantic, giving type-safe config access.
- **Template rendering with diff-check**: `ConfigManager._check()` re-renders and compares against on-disk state to avoid unnecessary restarts.
- **Lint hygiene**: `pyright` 0 errors/0 warnings, `ruff` and `codespell` pass cleanly — above average for the ecosystem.

## Common-practice notes

- **Drift from convention**: uses a `src/benchmark/` subpackage with a full framework (`base_charm.py`, event handlers, managers) rather than a flat `src/`. `DPBenchmarkCharmBase` has no Kafka-specific code — if intended as a reusable benchmark platform, it should be extracted to a separate library.
- **Library versions**: `lib/charms/data_platform_libs/v0/data_interfaces.py` (KafkaRequires), `lib/charms/kafka/v0/client.py` (KafkaClient), `lib/charms/tls_certificates_interface/v3/tls_certificates.py`. Standard Data Platform libraries, used correctly.
- **`charmcraft.yaml`**: standard 2-part build with `charm-strict-dependencies: true`. Good.
- **Missing `docs/`**: no `docs/` directory, no discourse link (`TODO` in metadata); Charmhub description is minimal.
- **No `justfile`**: uses only `tox` and `concierge.yaml`. Non-standard for the Data Platform team, but acceptable.
- **Two wrapper entry points**: `src/wrapper.py` (Kafka) and `src/benchmark/wrapper/main.py` (base). Fragile split — the Kafka template points to the former, the base template to the latter, and their argparse defaults both happen to be `run_count=1`, which makes template/wrapper mismatches hard to catch.

## Tests

**Unit tests** (`tox -e unit`, 11 passed, 38% coverage):
- **0%** on `src/charm.py` (243 stmts), `src/tls.py` (105), `src/models.py` (40).
- 100% on `src/benchmark/literals.py` and `src/literals.py`; 90% on `src/benchmark/wrapper/core.py`.
- 49% on the lifecycle manager, 25% on the config manager, 44% on `src/wrapper.py`.
- **Zero unit tests** for: any charm event handler, any action handler, the TLS handler, Kafka client integration, database state modeling, the Kafka-specific config manager rendering, peer relation state management.
- The wrapper test `test_exec` uses `duration=0, run_count=1` — never exercises the broken `>=` condition (finding #2).

**Integration tests** (`tests/integration/test_charm.py`, 6 test functions):
- Cover prepare, run, stop, restart, clean on VM and k8s, with and without TLS.
- Assert action completion and service state, not benchmark output correctness.
- Use `DEFAULT_NUM_UNITS=2` and `parallel_processes=2` — the default-config single-unit case is never tested (finding #4).
- TLS variants assert the relation completes but don't verify encrypted connections.
- No test for `get-summary` (finding #5), invalid config (finding #6), or workload crash detection (finding #8).
- No scenario tests exist (`tests/scenario/` absent).

## Docs

- **README**: covers deploy, relate, actions, COS. Does not mention the `parallel_processes` single-unit requirement or valid `workload_name` values.
- **Charmhub description**: two sentences; metadata has a `TODO: Update docs`.
- **CONTRIBUTING.md**: references nonexistent `tox -e static` (finding #26).
- **No `docs/`**: no architecture docs, design decisions, or troubleshooting guide.
- **Doc/reality mismatches**: `get-summary` is documented but broken; `config.yaml` says `parallel_processes` "Minimum is 2" but the default is 1; `CONTRIBUTING.md` describes tox environments that don't exist.

## Open questions

1. What causes TLS to be broken (issue #41)? Two independent defects (findings #3, #10) plus a possible leader/non-leader race. The stale `self.secret` (finding #3) looks like the primary blocker; fixing both should resolve it, but this could not be verified end-to-end without a working TLS Kafka deployment.
2. Why does `rustup` remain in the build with no Rust source in the repo? Probably leftover from a replaced Rust wrapper (unverified).
3. What is the intended `parallel_processes` minimum? Config docs say 2, the default is 1, and the preflight check is `units × processes < 2` — misaligned.
4. Is `DPBenchmarkCharmBase` meant to be a reusable library? Architecture suggests yes, but it lives under `src/benchmark/` and the base class instantiates managers the subclass immediately replaces (finding #24).
5. Does Juju 4.x work with this charm? Could not verify — LXD provisioning failed in this environment; concierge is pinned to 3.6/stable.
6. Why only one commit in git history? A single squash at `50c335a` (2026-06-18) makes it impossible to trace when bugs were introduced.
7. Why does the k8s coordinator exit almost immediately? "Stop All" was observed ~130ms after workload start; possibly worker connectivity issues in the single-pod setup, but the dominant, confirmed cause of the "finished" status is the `run_count=1` wrapper default (finding #1).
