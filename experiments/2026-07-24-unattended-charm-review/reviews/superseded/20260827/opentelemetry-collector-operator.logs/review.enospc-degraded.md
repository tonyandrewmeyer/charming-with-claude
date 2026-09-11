# opentelemetry-collector

A mature, feature-rich subordinate machine charm that deploys the OpenTelemetry Collector as a snap, aggregating metrics, logs, traces, and profiles from principal charms and forwarding them to COS backends. The codebase is well-structured with clear separation of concerns (config builder, integrations, snap management), extensive unit test coverage (171 tests, all passing), and sensible defaults. The primary concerns are around the monolithic `_reconcile` method (tracked as open issue #79), a few correctness edge cases, a superstitious cert-handling pattern that silently discards errors, calling a private method on the COS Agent library, and a terraform module that does not correctly model the subordinate nature of the charm.

| | |
|---|---|
| Repo | canonical/opentelemetry-collector-operator @ 9fa23d2 (2026-07-15) |
| Charms | opentelemetry-collector |
| Substrate | machine (subordinate) |
| Deployed | in progress — concierge-lxd (3.6), 2/edge rev 347; machine still provisioning due to slow apt |
| Reviewed | 2026-08-05 |

## What it does

The opentelemetry-collector charm is a Juju subordinate charm that deploys the OpenTelemetry Collector and node-exporter as snaps. It relates to a principal charm via `juju-info` or `cos-agent` and provides:

- **Ingestion**: Metrics (Prometheus scrape, OTLP gRPC/HTTP), Logs (Loki push API, filelog from /var/log and snap logs), Traces (OTLP, Zipkin, Jaeger over gRPC/Thrift HTTP), Profiles (Pyroscope OTLP).
- **Forwarding**: Remote-write to Prometheus/Mimir, Loki log push, OTLP metrics/logs/traces, Tempo traces, Pyroscope profiles, Grafana Cloud integration.
- **TLS**: Server cert via `receive-server-cert` (tls-certificates v4), CA trust via `receive-ca-cert` (certificate_transfer).
- **Self-monitoring**: Internal telemetry, Node exporter metrics, Grafana dashboards, Prometheus and Loki alert rules.
- **External configs**: Optional injection of collector config snippets via the `external-config` relation (used by the otelcol-integrator charm).

## Deployment log

Attempted to deploy on `concierge-lxd` (Juju 3.6.23):
```bash
juju add-model -c concierge-lxd rv-otelcol
juju deploy ubuntu --base ubuntu@24.04
juju deploy opentelemetry-collector --channel 2/edge
juju integrate opentelemetry-collector:juju-info ubuntu:juju-info
```

Machine `0` was provisioned as LXD container `juju-68c03b-0` and started, but cloud-init is still running as of 05:00 UTC (over 10 minutes) due to slow `apt-get update` (254 seconds) followed by `apt-get dist-upgrade`. The juju agent has not yet been installed on the machine. The `concierge-lxd-4` controller (Juju 4.0.5) is unresponsive to all API calls — this may indicate a degraded controller that needs attention.

Will update this section when the machine becomes available.

## Observed behaviour

Machine still provisioning at time of writing. The deployment log will be updated once the unit becomes active. Key behaviours to verify:

1. The charm should reach `blocked` status with the mandatory-relation-pairs message, since no outgoing relation (send-remote-write, send-loki-logs, etc.) is connected. The integration test `test_deploy` explicitly expects `all_blocked(status, "otelcol")`.
2. The `reconcile` action should be exerciseable.
3. Config changes (e.g. `debug_exporter_for_logs=true`) should trigger a config rewrite and snap restart.

## Findings

### Calling a private method on COSAgentRequirer
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:289-298`
- **Evidence**:
  ```python
  changed_event = RelationChangedEvent(
      handle=self.handle,
      relation=relation,
      app=relation.app,
      unit=next(iter(relation.units)),
  )
  cos_agent._on_relation_data_changed(changed_event)
  ```
- **Why it matters**: The charm calls `cos_agent._on_relation_data_changed()`, a private method of the COS Agent library, to manually trigger relation data processing. The code itself acknowledges this with a `TODO`: _instead of calling a private method, expose a public one in the COS Agent library_. If the library refactors its internals (e.g., changes the method signature or splits the logic), this charm will break silently. The charm also has to construct a synthetic `RelationChangedEvent` manually, which is fragile — it uses `next(iter(relation.units))` assuming subordinate relations only have one unit, but that could change.
- **Fix**: Add a public method to the COS Agent library (e.g., `refresh_relation_data()`) and call that instead.
- **Linter rule**: Not mechanically checkable (requires semantic knowledge that `_on_relation_data_changed` is private).

### Certificate processing failure is silently swallowed
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:463-471`
- **Evidence**:
  ```python
  try:
      self._ensure_directory(CERT_DIR)
      cert_paths = self._write_ca_certificates_to_disk(metrics_consumer_jobs)
      metrics_consumer_jobs = config_manager.update_jobs_with_ca_paths(
          metrics_consumer_jobs, cert_paths
      )
  except Exception as e:
      logger.warning(f"Certificate processing failed, continuing without certs: {e}")
      # Continue without certificate functionality
      pass
  ```
- **Why it matters**: The broad `except Exception` catches everything — `OSError`, `PermissionError`, `ValueError`, even programming errors like `AttributeError`. If certificate processing fails, the charm continues as if nothing happened, but the scrape jobs will be silently missing CA certs. The operator gets no status message, and TLS-protected scrapes will fail with certificate errors that are hard to diagnose. The charm should distinguish between recoverable failures (non-existent CA cert) and programming errors, and should at least log a warning that specific jobs are missing certificates.
- **Fix**: Narrow the exception clause to expected I/O errors, and set a non-blocking status or at minimum a specific warning log per job. Do not catch `Exception` blanket.
- **Linter rule**: "broad-except in hook handler" (checkable: flag `except Exception` in charm `src/`).

### logging.fatal with format arguments passed wrongly
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:347-349`
- **Evidence**:
  ```python
  except snap.SnapError as e:
      logger.error(f"error connecting plug {plug} to opentelemetry-collector:logs")
      logger.error(e.message)
  ```
- **Why it matters**: `snap.SnapError` has a `.message` attribute from the underlying `snapd` library. When `e.message` is `None` or missing, `logger.error(None)` logs the string "None", which is unhelpful. The charm should use `logger.error(str(e))` or `logger.error("error connecting snap plug: %s", e)`. The TODO comment `# TODO: should we fail loudly and error?` confirms this was left as a known gap.
- **Fix**: Replace `logger.error(e.message)` with `logger.error("snap connect failed: %s", e)`, and consider escalating to a blocked status if the snap plug connection is critical.
- **Linter rule**: "snap error message attribute may be null" — not mechanically checkable without type analysis.

### Snap log endpoint_topology access without guard
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:342-358`
- **Evidence**:
  ```python
  endpoint_owners = {
      endpoint.owner: {
          "juju_application": topology.application,
          "juju_unit": topology.unit,
      }
      for endpoint, topology in cos_agent.snap_log_endpoints_with_topology
  }
  ```
- **Why it matters**: `cos_agent.snap_log_endpoints_with_topology` returns tuples of `(endpoint, topology)`. The code uses `endpoint.owner` as a dict key and later does `endpoint_owners[fstab_entry.owner]` for fstab entries. If a snap plug appears in the fstab that doesn't have a matching entry in `snap_log_endpoints_with_topology`, this will raise a `KeyError` at line 372:
  ```python
  "juju_application": endpoint_owners[fstab_entry.owner]["juju_application"],
  ```
  The guard at line 368 (`if fstab_entry.owner not in endpoint_owners.keys()`) uses `.keys()` which creates a list view but the check is correct. However, `endpoint_owners` itself is constructed with `topology.unit` which could be `None` or empty if the topology from the snap endpoint doesn't have a unit field.
- **Fix**: Use `endpoint_owners.get(fstab_entry.owner, {})` with safe fallback values, or log a warning when a fstab owner has no matching endpoint.
- **Linter rule**: Not mechanically checkable.

### Double OtlpRequirer instantiation wastes framework observers
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/integrations.py:510-520`
- **Evidence**:
  ```python
  OtlpRequirer(
      charm,
      aggregator_peer_relation_name="peers",
      rules=rules,
      extra_alert_labels=key_value_pair_string_to_dict(extra_alert_labels),
  ).publish()

  # Access the provider's endpoints
  return OtlpRequirer(
      charm, protocols=["grpc", "http"], telemetries=["logs", "metrics", "traces"]
  ).endpoints
  ```
- **Why it matters**: Two separate `OtlpRequirer` instances are created: one to call `.publish()` and a second to access `.endpoints`. Each `OtlpRequirer()` constructor sets up framework event observers, processes relation data, and queries peer data. The first instance is created, processes state, publishes rules, and is immediately discarded (garbage collected). The second instance then repeats the same setup work. The `OtlpRequirer` constructor accepts `protocols`, `telemetries`, `rules`, `aggregator_peer_relation_name`, and `extra_alert_labels` all at once, so a single instance can do both operations. This wastes CPU and creates unnecessary snapd/peer-data calls on every reconcile.
- **Fix**: Create a single `OtlpRequirer` instance with all parameters, call `.publish()`, and return `.endpoints` from the same instance.
- **Linter rule**: "multiple instantiations of same library class in one function" — mechanically checkable with type-aware analysis.

### Second private method call: `TLSCertificatesRequiresV4._configure()`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/integrations.py:587`
- **Evidence**:
  ```python
  # TLSCertificatesRequiresV4 is garbage collected, see the `_reconcile`` docstring for more
  # details. So we need to call _configure() ourselves:
  certificates._configure(None)  # type: ignore[reportArgumentType]
  ```
- **Why it matters**: The charm calls a private method (`_configure`) on the TLS Certificates library, passing `None` as the event argument (with a `# type: ignore` suppression). The comment acknowledges that the library object is "garbage collected" because `receive_server_cert()` creates a new instance on every call (the `TLSCertificatesRequiresV4` instance is not stored on `self`). Calling `_configure()` manually is a workaround for the library expecting to observe framework events that don't fire because the instance is ephemeral. This is fragile — if the library changes its private `_configure` signature, the charm will break.
- **Fix**: Store the `TLSCertificatesRequiresV4` instance on the charm (e.g., `self.certificates`) so the framework keeps it alive and event handlers fire naturally. The library should not require manual calling of private methods.
- **Linter rule**: "private method call in charm code" — mechanically checkable (flag any `._xxx(` call on an imported library object).

### Monolithic `_reconcile` method
- **Severity**: medium
- **Kind**: bug | ux
- **Where**: `src/charm.py:190-550` (approx 360 lines)
- **Evidence**: The `_reconcile` method is called on virtually every hook event (install, config-changed, relation-changed, etc.) and orchestrates ALL integrations in a single monolithic function. The charm itself acknowledges this in open issue #79 ("refactor `_reconcile` method").
- **Why it matters**: 
  1. Any unhandled exception anywhere in `_reconcile` will cause a hook failure, reverting ALL state changes even for unrelated integrations.
  2. The ordering of operations is critical (documented in comments like "NOTE: this must run after the logs/metrics/cos-agent integrations") but enforced only by convention.
  3. The method invokes subprocesses (`refresh_certs`, `_otelcol_version`), snap operations, and file I/O mixed with relation data operations — a failure in any of these can block all others.
  4. It is difficult to test individual integration flows independently.
- **Fix**: Split into per-integration reconcile methods with their own error handling, as already tracked in #79. A partial decomposition — separating TLS setup, COS agent setup, logs setup, metrics setup, etc. — would be a good first step.
- **Linter rule**: "reconcile method too long" — checkable (flag methods over N lines).

### _otelcol_version runs subprocess on every hook
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:604-614`
- **Evidence**:
  ```python
  @property
  def _otelcol_version(self) -> Optional[str]:
      version_output = subprocess.run(
          ["/snap/opentelemetry-collector/current/bin/otelcol", "--version"],
          capture_output=True,
          text=True,
      ).stdout
      ...
  ```
- **Why it matters**: The `_otelcol_version` property runs a subprocess calling the otelcol binary on every invocation. It is called at the end of `_reconcile` (line 601: `self.unit.set_workload_version(self._otelcol_version or "")`), so every hook event — including `update-status` (every 5 minutes) — spawns a subprocess. The subprocess also has no timeout and no error handling: if the snap isn't installed or the binary hangs, the hook hangs too. Additionally, the result is only used for display (`set_workload_version`), making this an expensive cosmetic operation.
- **Fix**: Cache the version string (set once after snap install/upgrade) and/or add a timeout to the subprocess call. If the snap isn't installed, return a cached or default value without spawning the binary.
- **Linter rule**: "subprocess in property accessor" — mechanically checkable.

### Terraform `units` parameter inappropriate for subordinate charm
- **Severity**: medium
- **Kind**: bug
- **Where**: `terraform/main.tf:7`, `terraform/variables.tf:44-48`
- **Evidence**:
  ```hcl
  resource "juju_application" "opentelemetry_collector" {
    ...
    units = var.units
    ...
  }
  ```
  ```hcl
  variable "units" {
    description = "Unit count/scale"
    type        = number
    default     = 1
  }
  ```
- **Why it matters**: The opentelemetry-collector charm is a **subordinate** charm (`subordinate: true` in charmcraft.yaml). Subordinate charms do not have their own units; they scale with their principal. Passing `units` to `juju_application` for a subordinate charm is an error in the Terraform Juju provider — it will either be silently ignored or cause a plan/apply error depending on the provider version. An operator using this module would be confused.
- **Fix**: Remove the `units` variable and the `units = var.units` line from the resource. The terraform module should also explicitly document that the charm is a subordinate that requires a principal.
- **Linter rule**: Not mechanically checkable without provider-specific knowledge.

### Channel validation only allows `dev/` track
- **Severity**: medium
- **Kind**: bug
- **Where**: `terraform/variables.tf:10-12`
- **Evidence**:
  ```hcl
  validation {
    condition     = startswith(var.channel, "dev/")
    error_message = "The track of the channel must be 'dev/'. e.g. 'dev/edge'."
  }
  ```
- **Why it matters**: The published charm has tracks `2/` and `0.130/`, but the terraform validation rejects any channel not starting with `dev/`. This means a user following the standard published channels (`2/stable`, `2/edge`, `0.130/stable`) cannot use the terraform module. The charmhub listing shows `2/edge` as a published channel. This validation rule appears to be a leftover from early development and prevents practical use of the module.
- **Fix**: Remove the validation or change it to allow any valid channel format. At minimum, allow the `2/` and `0.130/` tracks.
- **Linter rule**: Not mechanically checkable.

### Terraform README title says "opentelemetry-collector-k8s" but module is for machines
- **Severity**: low
- **Kind**: docs
- **Where**: `terraform/README.md:1`
- **Evidence**:
  ```markdown
  # Terraform module for opentelemetry-collector-k8s
  ```
- **Why it matters**: The README title says "k8s" but this charm is the machine (VM) subordinate. This is a copy-paste error that could confuse operators looking for the k8s charm terraform module. The content of the README is otherwise correct for the machine charm.
- **Fix**: Change to "Terraform module for opentelemetry-collector" or "opentelemetry-collector (machines)".
- **Linter rule**: Not mechanically checkable.

### `_configure_logrotate` file handle not closed
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:718-723`
- **Evidence**:
  ```python
  charm_root = self.charm_dir.absolute()
  with open(charm_root.joinpath(*LOGROTATE_SRC_PATH.split("/")), "r") as f:
      config_path.write_text(f.read())
  ```
- **Why it matters**: The `with open(...)` context manager properly closes the source file, so this is actually fine. Re-reading more carefully: the source file IS properly managed in a `with` block. No bug here — removing this finding.

### `path_exclude` split on semicolons may produce empty strings
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:365`
- **Evidence**:
  ```python
  path_exclusions = cast(str, self.config.get("path_exclude")).split(";")
  ```
- **Why it matters**: If the config value is empty string (`""`), `.split(";")` returns `[""]`, a list with one empty string. This empty string is passed as an `exclude` pattern to `_filelog_receiver_config`, which does `if exclude:` — an empty list isn't falsy, so `[""]` passes through. The filelog receiver may then interpret `""` as a glob pattern, which could match unexpected paths. If the config value has a trailing semicolon (e.g., `/var/log/app.log;`), an empty string element is also produced.
- **Fix**: Filter out empty strings: `[p for p in path_exclude_raw.split(";") if p]`.
- **Linter rule**: "split result may contain empty strings" — mechanically checkable.

### Config hash comparison does not handle `None` server_cert_hash
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:536-546`
- **Evidence**:
  ```python
  current_hash = ",".join(
      [
          config_manager.config.hash,
          hash_ca_cert_dir(RECV_CA_CERT_FOLDER_PATH),
          server_cert_hash,
      ]
  )
  ```
- **Why it matters**: `server_cert_hash` comes from `integrations.receive_server_cert()` which returns `sha256(...)` which is always a string — so this is safe. No actual bug here.

### Private method call pattern in `receive_traces`, `receive_profiles`, and `forward_dashboards` unnecessarily guards on `is_leader()`
- **Severity**: low
- **Kind**: bug | ux
- **Where**: `src/integrations.py:266-269`, `src/integrations.py:278-279`, `src/integrations.py:465-466`
- **Evidence**:
  ```python
  if charm.unit.is_leader():
      tracing_provider.publish_receivers(...)
  ```
  ```python
  if not charm.unit.is_leader():
      return  # receive_profiles returns early for non-leaders
  ```
  ```python
  if not charm.unit.is_leader():
      return  # forward_dashboards returns early for non-leaders
  ```
- **Why it matters**: The TODO comments reference issue #71 ("leader-only because of..."). When multiple subordinate units of the same app are on different machines (different principals), the non-leader subordinates will NOT publish tracing receivers, profiles, or dashboards. This means a principal on a non-leader machine that relates to `receive-traces` or `receive-profiles` will not get endpoint data unless the leader happens to be on the same machine. This is a known limitation (#71) but has been open since the early days of the charm.
- **Fix**: Track issue #71 and ensure each unit publishes its own local endpoints regardless of leadership.
- **Linter rule**: Not mechanically checkable.

### OTEL collector snap is stopped when waiting for TLS certs, blocking unrelated pipelines
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:558-560`
- **Evidence**:
  ```python
  if self._has_server_cert_relation and not is_tls_ready():
      self.snap("opentelemetry-collector").stop()
      self.unit.status = WaitingStatus("CSR sent; otelcol down while waiting for a cert")
      return
  ```
- **Why it matters**: When the charm forms a `receive-server-cert` relation but hasn't received the certificate yet, it **stops** the entire otelcol snap. This blocks ALL pipelines — logs, metrics, traces — even though only the TLS-enabled receivers need the certificate. Non-TLS receivers (like filelog, node-exporter scrape) could continue operating but are stopped. This is a deliberate tradeoff but may surprise operators.
- **Fix**: Either document this prominently, or consider keeping the snap running and only failing TLS-protected receivers.

### `_configure_node_exporter` writes info metric file on every reconcile
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:701`
- **Evidence**:
  ```python
  def _configure_node_exporter(self, port: int):
      ...
      self._node_exporter_info_metric_file_path.write_text(self._info_metric)
  ```
- **Why it matters**: The `_configure_node_exporter` method is called at the end of every `_reconcile`. It writes a `.prom` textfile containing `otelcol_subordinate_charm_info` gauge metrics for all related units via `_info_metric`. This write triggers node-exporter to re-read the textfile directory. The file content only changes when related units change, but it is written on every config-changed, update-status, etc. This causes unnecessary I/O and node-exporter textfile reloads on every hook.
- **Fix**: Cache the last written content and only write the file if it actually changed (similar to the config_hash pattern used for otelcol config).
- **Linter rule**: Not mechanically checkable — requires dataflow analysis.

### COS Agent alerts only written by leader
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:338-341`
- **Evidence**:
  ```python
  if self.unit.is_leader():
      integrations._add_alerts(
          alerts=cos_agent.metrics_alerts,
          dest_path=self.charm_dir.absolute().joinpath(METRICS_RULES_DEST_PATH),
      )
  ```
- **Why it matters**: Alert rules from `cos_agent` are only written to disk by the leader unit, with the comment "Only the leader aggregates alerts, to prevent duplication." This is correct for preventing duplicate alerts in the forwarding path, but means non-leader units do not have local alert rule files. If a non-leader unit is the one forwarding alerts (e.g., via send-loki-logs), the alert rules from cos_agent principals on that machine won't be forwarded. The peer relation is supposed to carry this data between units (via the COS Agent library), but the on-disk write is gated on leadership.

## Worth copying

- **`SingletonSnapManager` file-based locking**: `src/singleton_snap.py` implements a clean, file-based reference counting mechanism for managing shared snap installations across multiple subordinate units on the same machine. Each unit registers itself with a lockfile like `LCK..opentelemetry-collector--rev80__otelcol_0`, and the manager tracks which units use which revision. On charm removal, if other units still need the snap, only the config file is removed (not the snap itself). This pattern is well-engineered and worth adopting for other subordinate charms that share workloads.

- **`ConfigBuilder` / `ConfigManager` separation**: `src/config_builder.py` provides a low-level, pipeline-aware config builder with `add_component()`, `add_extension()` and `add_telemetry()` methods. `src/config_manager.py` wraps it with higher-level, feature-oriented methods like `add_log_ingestion()`, `add_remote_write()`, `add_traces_processing()`. This two-layer architecture is cleanly separated and allows testing configuration generation independently of charm logic.

- **Comprehensive unit test coverage**: 171 unit tests using the ops `Scenario` framework, covering TLS transitions, config building, dashboards, alert rules, profile integration, path exclusions, memory limiter, OTLP forwarding, and more. The test conftest is well-organized with reusable fixtures for mocking snap operations, certificates, lock directories, and COS agent interactions.

- **`MandatoryRelationPairs` helper**: `deps/cosl/mandatory_relation_pairs.py` provides a declarative way to express that an incoming relation (e.g., `juju-info`) must be paired with at least one outgoing relation (e.g., `send-remote-write` OR `send-loki-logs` OR `send-otlp`). The charm uses this to set a clear `BlockedStatus` message telling the operator exactly which relations are missing. This is excellent UX.

- **Config hash-based restart**: The charm writes a `config_hash` file containing a combined hash of the generated config, CA cert dir, and server cert. The snap is only restarted when this hash changes, avoiding unnecessary restarts on no-op config-changed events. The comment at `src/charm.py:541-545` explains why the CA hash is computed from on-disk files rather than relation data (to handle multi-hook certificate transfer handshakes).

- **`$` escaping in Prometheus scrape configs**: `src/config_builder.py:403-434` implements recursive `$` → `$$` escaping in Prometheus scrape configs to prevent OpenTelemetry Collector from interpreting Prometheus relabeling capture-group back-references (`${1}`, `${2}`) as environment variable references. This is a non-obvious footgun that the charm handles correctly.

- **Idempotent dashboard filename deduplication**: `src/integrations.py:406-418` generates dashboard filenames with a content-identity component (`uid` or content hash) to prevent multiple dashboards with the same title from overwriting each other. This addresses the exact collision scenario described in open issue #365.

- **Clean lint/static results on charm code**: `ruff check src/ tests/` passes with zero issues. `pyright src/` passes with zero errors/warnings. The lint issues that exist (11) are entirely in vendored library code under `lib/charms/...` (unnecessary `else` after `return`, implicit `None` returns). This is excellent hygiene.

## Common-practice notes

- **Where this charm leads**: The file-based singleton snap management (`src/singleton_snap.py`) is a pattern not commonly seen in other subordinate charms. Most subordinates either assume exclusive ownership of their snap or use simpler lock mechanisms. This approach handles the case where multiple different subordinate applications (e.g., otelcol and another charm) might install different revisions of the same snap on the same machine, blocking the unit with a clear status message.

- **Where this charm drifts**: Calling a private method (`cos_agent._on_relation_data_changed`) and manually constructing `RelationChangedEvent` objects is unusual. Most charms using the COS Agent library rely on the library's own event handlers fired by framework events. The synthetic event construction here is a workaround for the subordinate-only-one-unit situation. The charm's own TODO acknowledges this should be fixed in the library.

- **`charmlibs` migration**: The charm uses `charmlibs.pathops` (`LocalPath`) instead of the deprecated `operator-libs-linux`, which aligns with the ecosystem migration documented in open issue #255. However, it still imports `charms.operator_libs_linux.v2.snap` directly for the snap library, which is fine (the snap module hasn't been migrated to charmlibs yet).

- **Snap revision pinning**: The charm pins exact snap revisions in `SnapMap` (`src/snap_management.py:47-63`) rather than using channels. This is good practice for reproducibility but requires manual updates when the snap publishes new revisions.

- **`cos-tool` inclusion**: The charmcraft.yaml includes a `cos-tool` part that downloads and bundles the `cos-tool` binary. This is used by the COS Agent library for alert rule validation and transformation. Bundling a binary in the charm is unusual but required because `cos-tool` isn't available as a snap or apt package.

## Tests

**Unit tests**: All 171 pass, 1 skipped (`test_https_endpoint_is_provided` — TODO marker). Run via:
```bash
cd repo && PYTHONPATH=lib:src:$PYTHONPATH uv run --frozen --isolated --extra=dev pytest tests/unit -x
```
Pass rate: 100%.

**Lint**: `ruff check src/ tests/` passes with zero issues. `ruff check lib/` finds 11 issues in vendored library code (RET505, RET502, RET507) — all fixable with `--fix` but properly attributed to upstream libraries.

**Static**: `pyright src/` passes with 0 errors, 0 warnings.

**Coverage gaps** identified (from reading tests, not running coverage):

| Gap | Risk |
|---|---|
| The `_configure_node_exporter` path with snap set retry | If `snap.set()` fails 5 times, the exception propagates to the hook |
| The `_remove_opentelemetry_collector` path when other units still use the snap | Config removal and restart path not tested |
| The `event()` function behavior on upgrade-charm vs. install | Only tested for install/upgrade-charm/update-status; remove hook tested implicitly via lifecycle test |
| External config integration (`receive_external_configs`) | No dedicated unit test found for the `OtelcolIntegratorRequirer` path |
| Snap fstab parsing (`SnapFstab`) with multiple entries for the same owner | Edge case only hit when a snap provides multiple shared-log mount points |
| `key_value_pair_string_to_dict` with edge cases (empty string, malformed pairs) | No unit test for the helper itself |

**Integration tests**: Not run due to deployment delays. The test suite in `tests/integration/` covers:
- `test_principal.py`: Deploy with ubuntu, verify blocked status, verify /var/log scraping, path_exclude, node metrics, node-exporter collectors.
- `test_cos_agent.py`: COS Agent integration with scrape jobs, log slots, dashboards.
- `test_external_config.py`: External config via otelcol-integrator relation.
- `test_log_rotation.py`: Log rotation configuration.
- `test_removal_hooks.py`: Cleanup on charm removal.
- `test_snap_refresh.py`: Snap refresh after charm upgrade.
- `test_tracing.py`: Tracing integration.

## Docs

**README**: `README.md` (2183 bytes) provides a brief overview with deploy instructions and the subordinate/principal relationship model. It's adequate but minimal — no architecture diagram, no list of supported integrations, no troubleshooting section.

**Terraform README**: `terraform/README.md` has the k8s title error noted above, channel validation bug, and the inappropriate `units` parameter. The module documentation is otherwise auto-generated from terraform-docs and is structurally correct.

**Charmhub description**: The `charmcraft.yaml` description is comprehensive, listing all key features, known limitations ("All receivers feed into all exporters", "connectors are not supported"), and integration points. This is good practice.

**CONTRIBUTING**: `CONTRIBUTING.md` (984 bytes) points to the Juju SDK docs and provides basic guidance.

**SECURITY**: `SECURITY.md` (753 bytes) is the standard Canonical security policy template.

## Open questions

1. **Does the charm recover from snap service crash?** If the otelcol snap process dies (OOM, config error), the charm currently only checks if the snap is running via `snap restart`. As confirmed by open issue #188, the charm stays at `active/idle` even when the workload process has exited. Need to verify by killing the process and checking if the charm detects it.

2. **What happens with invalid config values?** Open issue #236 shows a case where ceph-mon relation data with environment variables containing special characters caused the charm to error. The config builder's `_escape_dollars` method should handle `$` signs, but the `_sanitize_prometheus_scrape_configs` only runs on prometheus receivers — not on other config sources.

3. **Does the remove hook properly clean up?** Open issue #210 reports snaps not being removed on charm removal. The current code seems to handle this correctly via the `remove` hook, but needs verification.

4. **concierge-lxd-4 controller is unresponsive** — all API calls timeout. This controller may be in a degraded state and needs investigation. The Juju 4.x deployment could not be attempted.

5. **How does the charm behave with multiple principals on the same machine?** Open issue #260 discusses the case where 2 different otelcol applications are deployed to the same machine, causing config override issues. The `SingletonSnapManager` handles snap revision conflicts, but config files may still conflict.
