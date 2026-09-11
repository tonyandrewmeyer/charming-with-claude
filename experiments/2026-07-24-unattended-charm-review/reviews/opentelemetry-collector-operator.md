# opentelemetry-collector-operator

**Verdict**: A well-structured machine subordinate charm (clean builder/manager separation, thorough config validation, strong test fixtures) undermined by a handful of exception-handling gaps that turn operator config mistakes into unrecoverable `ErrorStatus`. The most urgent problem is that a single malformed bundled alert-rules file (`mdadm.rules`) fails YAML parsing and logs an ERROR on *every* hook invocation, and any operator who mistypes the `processors` config crashes the charm into `ErrorStatus` with no self-recovery. Two separate instances of the same `ops.Object`-as-local-variable anti-pattern (COSAgentRequirer, TLSCertificatesRequiresV4) generate GC warnings on every relevant hook and rely on private library APIs that may vanish. A maintainer should first fix the `mdadm.rules` YAML syntax and wrap `config_manager.py:634`'s `yaml.safe_load(processors_raw)` in exception handling — both are small, mechanical fixes with outsized operational impact — then address the two GC/local-variable patterns before the underlying libraries' private APIs change.

| | |
|---|---|
| Repo | canonical/opentelemetry-collector-operator @ `9fa23d2` (2026-07-15) |
| Charms | opentelemetry-collector |
| Substrate | machine (LXD, MAAS) |
| Deployed | yes — concierge-lxd-4 (Juju 4.0.12), 0.130/edge rev 438; concierge-lxd (Juju 3.6.27), 0.130/edge rev 438 |
| Reviewed | 2026-08-31 |

## What it does

A subordinate charm that deploys alongside a principal charm (via `juju-info` or `cos-agent` relations) and runs the OpenTelemetry Collector snap. It:
- Scrapes node-exporter metrics from the host machine
- Collects logs from `/var/log` and snap log endpoints
- Forwards telemetry to Prometheus (remote-write), Loki, Tempo, and OTLP endpoints
- Provides receive endpoints for traces, logs, and profiles from other charms
- Manages TLS certificates for secure communication
- Exposes Grafana dashboards and Prometheus alert rules

## Deployment log

### concierge-lxd-4 (Juju 4.0.12)

```
16:18:00 - juju deploy ubuntu --channel latest/stable
16:18:30 - juju deploy opentelemetry-collector --channel 0.130/edge (rev 438)
16:19:00 - juju integrate ubuntu opentelemetry-collector
16:23:00 - opentelemetry-collector enters maintenance (installing node-exporter snap)
16:25:00 - opentelemetry-collector reaches blocked state
           "['cloud-config']|['send-loki-logs']|['send-otlp']|['send-remote-write'] for juju-info"
16:25:07 - ERROR in debug-log: "Failed to read rules from mdadm.rules" (YAML parse error)
16:25:07 - WARNING: Generic aggregator rules were requested, but no peer relation was found
16:25:07 - WARNING: Reference to ops.Object at path .../COSAgentRequirer[cos-agent] has been garbage collected

Later tests:
16:34:46 - Removed juju-info relation
           - stop hook ran: removed cert directory, uninstalled snaps
           - remove hook ran with "cleaning up prior to charm deletion"
16:34:50 - Re-integrated ubuntu opentelemetry-collector
           - New unit opentelemetry-collector/1* came up in blocked state
16:41:08 - Set processors="invalid yaml: ["
           - Hook crashed: "hook failed: 'config-changed'"
           - Charm went to ErrorStatus
16:41:52 - Reset processors="" → charm recovered to BlockedStatus
17:04:58 - Ran reconcile action
           - update-ca-certificates ran successfully
           - Charm returned to BlockedStatus (no change)
17:11:59 - Set processors="[1, 2, 3]"
           - Hook crashed: "hook failed: 'config-changed'"
           - Charm went to ErrorStatus
17:12:35 - Reset processors="" → charm recovered to BlockedStatus
17:12:40 - Ran reconcile action
           - update-ca-certificates ran successfully
           - Charm returned to BlockedStatus
```

### concierge-lxd (Juju 3.6.27)

```
16:51:00 - juju add-model rv-otelcol-3x
16:51:15 - juju deploy ubuntu --channel latest/stable
16:52:15 - juju deploy opentelemetry-collector --channel 0.130/edge (rev 438)
16:53:00 - juju integrate ubuntu opentelemetry-collector
16:55:26 - Installing opentelemetry-collector snap, revision 80
16:55:51 - Snap installed successfully
16:55:51 - ERROR: Failed to read rules from mdadm.rules (YAML parse error)
16:55:51 - WARNING: Generic aggregator rules were requested, but no peer relation was found
16:56:05 - WARNING: Reference to ops.Object .../COSAgentRequirer[cos-agent] has been garbage collected
16:56:06 - config-changed hook ran
16:56:06 - ERROR: Failed to read rules from mdadm.rules
16:56:25 - Reached blocked state: ['cloud-config']|['send-loki-logs']|...
16:56:25 - Set processors="invalid yaml: ["
           - Hook crashed: "hook failed: 'config-changed'"
           - Charm went to ErrorStatus
           - Traceback confirmed: yaml.parser.ParserError in config_manager.py:634
17:10:13 - Ran reconcile action
           - update-ca-certificates ran successfully
           - charm remained in ErrorStatus
17:11:33 - config-changed hook ran (auto-retry)
           - Charm recovered to BlockedStatus
```

## Observed behaviour

1. **Deploy timeline**: ~7 minutes from deploy to blocked status on Juju 4.x; ~3 minutes on Juju 3.6 (snap installation dominates both).
2. **Snaps installed correctly**: node-exporter rev 2154, opentelemetry-collector rev 80.
3. **Juju version parity**: identical behaviour on 3.6.27 and 4.0.12 — same hook sequence, same errors, same blocked-state messages. No regression introduced by Juju 4.x.
4. **Status behaviour**: correctly enters blocked state when no outgoing relation exists, with an actionable message listing required relation pairs.
5. **mdadm.rules parse failure**: fires on EVERY hook invocation — install, upgrade-charm, config-changed, juju-info-relation-changed, peers-relation-changed, leader-elected, start, stop, remove. Same on Juju 3.6 and 4.x.
6. **COS Agent GC warning**: fires on every config-changed hook on both Juju 3.6 and 4.x: `Reference to ops.Object at path OpenTelemetryCollectorCharm/COSAgentRequirer[cos-agent] has been garbage collected.`
7. **TLS GC warning (confirmed)**: same GC warning fires for TLSCertificatesRequiresV4 on `receive-server-cert` relation-changed hooks. Observed at 17:32:04 and 17:32:08 in debug-log. Same root cause as COSAgentRequirer — local variable pattern in `integrations.py:574`.
8. **TLS certificate lifecycle (live test)**: related to `self-signed-certificates` on `rv-otelcol2`. CSR sent; `WaitingStatus` visible in status history at 17:32:00. Cert written to disk at 17:32:01. Charm returned to `BlockedStatus` (still needs mandatory outgoing relations). The `rehash` WARNING "skipping ca-certificates.crt, it does not contain exactly one certificate or CRL" is benign — the CA cert dir has multiple entries.
9. **TLS relation removal**: handled gracefully. Both `receive-server-cert-relation-departed` and `receive-server-cert-relation-broken` hooks ran. Charm returned to `BlockedStatus`. No `ErrorStatus`.
10. **Generic aggregator warning**: fires on every hook when no peer relation data is set — expected if using multiple principals with cos-agent.
11. **Invalid processors config (YAML syntax error)**: causes `ErrorStatus` on both Juju 3.6 and 4.x. Traceback confirms `yaml.parser.ParserError` at `config_manager.py:634`. Recovery: setting the config value to empty string triggers auto-retry (Juju 4.x) or a reconcile action (both versions).
12. **Invalid processors config (wrong YAML type)**: `processors="[1, 2, 3]"` causes `AttributeError: 'list' object has no attribute 'items'` → `ErrorStatus`. Same recovery path.
13. **Invalid extra_alert_labels**: ERROR logged but charm stays `BlockedStatus`. Correctly handled.
14. **memory_limit_percentage=-10**: WARNING logged, default (100%) used. Charm stays blocked. Correctly handled.
15. **debug_exporter_for_logs=true (valid change)**: applied. config-changed hook ran. Charm stayed blocked (correct).
16. **Relation removal**: stop hook runs gracefully, removes certs and uninstalls snaps.
17. **Workload killed (snap stop)**: `juju exec --unit opentelemetry-collector/1 'sudo snap stop opentelemetry-collector'` stopped the snap successfully. No hook was triggered. Charm did NOT notice — stayed in `BlockedStatus`, snap remained stopped. The charm only monitors workload health via config-hash-based restart detection (triggers on config change, not process death). Latent failure mode: a crashed workload is invisible until the next config change or manual reconcile.
18. **reconcile action**: runs successfully on both Juju 3.6 and 4.x, triggers `update-ca-certificates`. On Juju 3.6, required a second auto-retry before clearing `ErrorStatus`. Recovery confirmed on both versions.
19. **juju refresh**: reports "already up-to-date" — no newer revision available on charmhub edge.
20. **Codespell findings**: three spelling errors — "agregating" (`charmcraft.yaml:190`), "Incomming" (`overview-dashboard.json:494`), "groupping" (`overview-dashboard.json:1875`). The "groupping" typo is linked to issue #344.
21. **Hook error for ceph-mon relation**: confirmed by issue #236 — `ErrorStatus` from bad relation data (metric names violate OTEL regex).

## Findings

### Invalid `processors` config causes ErrorStatus (unhandled YAML + type exception)

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/config_manager.py:634`
- **Evidence**: `add_custom_processors` passes the raw config string directly to `yaml.safe_load()` with no exception handling:
  ```python
  for processor_name, processor_config in yaml.safe_load(processors_raw).items():  # line 634
  ```
  Two distinct failure modes confirmed on both Juju 3.6 and 4.x:
  1. Invalid YAML syntax — `processors="invalid yaml: ["` → `yaml.parser.ParserError` → `ErrorStatus`. Full traceback confirmed at `config_manager.py:634`.
  2. Wrong YAML type — `processors="[1, 2, 3]"` (valid YAML but a list, not a dict) → `AttributeError: 'list' object has no attribute 'items'` → `ErrorStatus`:
     ```
     File ".../config_manager.py", line 634, in add_custom_processors
       for processor_name, processor_config in yaml.safe_load(processors_raw).items():
     AttributeError: 'list' object has no attribute 'items'
     ```
  This exact line is uncovered in unit tests — no test exercises invalid YAML or wrong-type input for `processors`.
- **Impact**: An operator who sets an invalid `processors` value crashes the hook, putting the charm in `ErrorStatus`. Unlike `BlockedStatus`, `ErrorStatus` requires the hook to succeed before the charm can recover, and no error message tells the operator what went wrong. Recovery is operator-initiated (reset config, or reconcile action + auto-retry) — the charm is effectively wedged until then.
- **Fix**: Wrap `yaml.safe_load(processors_raw)` in `try/except (yaml.YAMLError, AttributeError, TypeError)`, set `BlockedStatus(f"Invalid processors config: {e}")`, and return early.
- **Linter rule**: "YAML loading from config without exception handling" — mechanically checkable by AST analysis for `yaml.safe_load` without an enclosing try/except.

### Broken YAML in bundled alert rules

- **Severity**: high
- **Kind**: bug
- **Where**: `src/prometheus_alert_rules/mdadm.rules:10,18,24,33,37`
- **Evidence**: the file contains `summary: "...)" description: >-` with no newline between the `summary` value and the `description` key, on 4 of 5 alert entries. YAML reads the quoted `summary` scalar as continuing to end-of-line, so `description:` becomes a second mapping key on the same line — a syntax error. Fires on every hook invocation on both Juju 3.6 and 4.x:
  ```
  ERROR unit.opentelemetry-collector/1.juju-log Failed to read rules from mdadm.rules: while parsing a block mapping
    in "...prometheus_alert_rules/mdadm.rules", line 10, column 9
  expected <block end>, but found '<scalar>'
    in "...prometheus_alert_rules/mdadm.rules", line 10, column 149
  ```
  Confirmed with `python3 -c "import yaml; yaml.safe_load(open('src/prometheus_alert_rules/mdadm.rules'))"` — only `mdadm.rules` fails; the other 12 `*.rules` files parse correctly. The error also fires during unit test execution.
- **Impact**: mdadm-based alert rules are silently dropped on every hook. Operators with software RAID will not receive expected disk-failure alerts. The ERROR log on every hook adds noise and can mask real issues.
- **Fix**: insert a newline between the `summary` value and the `description:` key in each of the four affected alerts.
- **Linter rule**: "YAML parse validation in CI for `*.rules` files" — mechanically checkable with `yaml.safe_load()` in a pre-commit hook or CI step.

### COSAgentRequirer local variable causes GC warning and fragile design

- **Severity**: high
- **Kind**: bug / maintenance-risk
- **Where**: `src/charm.py:280-299`
- **Evidence**: `cos_agent` is instantiated as a local variable inside `_reconcile`, then used to call the private method `_on_relation_data_changed`:
  ```python
  cos_agent = COSAgentRequirer(self, is_tracing_ready=lambda: True)  # line 280
  # ...
  cos_agent._on_relation_data_changed(changed_event)  # line 298 — private API
  ```
  After `_reconcile` returns, `cos_agent` is garbage collected. On every `config-changed` hook, ops warns:
  ```
  WARNING Reference to ops.Object at path
  OpenTelemetryCollectorCharm/COSAgentRequirer[cos-agent] has been garbage collected
  between when the charm was initialised and when the event was emitted.
  ```
  Confirmed on both Juju 3.6 and 4.x. Issue #391 tracks migrating the private `_on_relation_data_changed` API to `charmlibs`; there is currently no public replacement.
- **Impact**: the private API call happens on a partially-collected object, risking `AttributeError` if library internals change. A new `COSAgentRequirer` instance is created and discarded on every hook — wasteful and fragile.
- **Fix**: store `self._cos_agent` as a charm instance variable. Track issue #391 for the public API replacement.
- **Linter rule**: "ops.Object subclass instantiated as local variable in hook handler" — not mechanically checkable without library knowledge.

### TLSCertificatesRequiresV4 local variable causes GC warning (same pattern as COSAgentRequirer)

- **Severity**: high
- **Kind**: bug / maintenance-risk
- **Where**: `src/integrations.py:574`
- **Evidence**: same pattern as the COSAgentRequirer finding. `certificates` is created as a local variable inside `receive_server_cert`:
  ```python
  certificates = TLSCertificatesRequiresV4(  # line 574
      charm=charm,
      relationship_name="receive-server-cert",
      certificate_requests=[csr_attrs],
      mode=Mode.UNIT,
  )
  certificates._configure(None)  # type: ignore  # line 584 — private API
  provider_certificate, private_key = certificates.get_assigned_certificate(...)  # line 586
  ```
  After the function returns, `certificates` is garbage collected. On every `receive-server-cert-relation-changed` hook, ops warns:
  ```
  WARNING Reference to ops.Object at path
  OpenTelemetryCollectorCharm/TLSCertificatesRequiresV4[receive-server-cert] has been
  garbage collected between when the charm was initialised and when the event was emitted.
  ```
  Observed at 17:32:04 and 17:32:08 in debug-log. A comment at line 582 already acknowledges the GC ("TLSCertificatesRequiresV4 is garbage collected, see the `_reconcile` docstring for more details").
- **Impact**: same as COSAgentRequirer — the private `_configure()` call and the subsequent `get_assigned_certificate()` call use a partially-collected object, risking `AttributeError` if library internals change.
- **Fix**: store `self._tls_certificates` as a charm instance variable. The private `_configure()` call needs a public API replacement (no issue currently tracks this specifically).
- **Linter rule**: "ops.Object subclass instantiated as local variable" — not mechanically checkable without library knowledge.

### Deprecated TLS certificates library with private API usage

- **Severity**: high
- **Kind**: maintenance-risk
- **Where**: `lib/charms/tls_certificates_interface/v4/tls_certificates.py:6-15`, `src/integrations.py:584`
- **Evidence**: the bundled `tls_certificates_interface/v4` library is explicitly deprecated:
  ```python
  """Legacy Charmhub-hosted lib, deprecated in favour of ``charmlibs.interfaces.tls_certificates``.
  WARNING: This library is deprecated.
  It will not receive feature updates or bugfixs.
  """
  ```
  The charm calls the private `certificates._configure(None)` (line 584, with a `# type: ignore` comment) to force certificate requests, on the same object that gets garbage collected (see above finding). Deprecation warnings fire in test runs for `generate_private_key()`, `generate_csr()`, `generate_ca()`, `generate_certificate()`, and `JujuVersion.from_environ()`. The migration dependency `charmlibs-interfaces-tls-certificates~=1.0` is already in `pyproject.toml`.
- **Impact**: a deprecated library with private API calls means the charm will break when the library is removed or updated; the private `_configure()` call has no public equivalent yet.
- **Fix**: migrate to `charmlibs.interfaces.tls_certificates`. The same migration pattern applies as for the cos_agent issue (#391).
- **Linter rule**: "Import from deprecated charm library" — mechanically checkable by scanning for `tls_certificates_interface` in imports.

### `install_snap` has unhandled exception from snap library

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/snap_management.py:120,130,136,137`
- **Evidence**: `install_snap` makes three unguarded calls after a guarded lookup:
  ```python
  revision = SnapMap.get_revision(snap_name, classic=classic)  # line 120 — KeyError IS caught (121-124)
  snap.ensure(state=snap_lib.SnapState.Present, revision=str(revision), classic=classic)  # line 130 — NO handler
  if config:
      snap.set(config)   # line 136 — NO handler
  snap.hold()            # line 137 — NO handler
  ```
  Any `snap_lib.SnapError` from these three calls propagates unhandled to `src/charm.py:624` (`_install_snaps`), then to the install/upgrade-charm hook. `SnapInstallError` is defined at `src/snap_management.py:91` but never raised. 55% coverage for this file — the entire install path is untested.
- **Impact**: on network-restricted machines, when snapd is unavailable, or if the hold fails, the install hook crashes with an unhandled exception; the operator sees `ErrorStatus` with only a traceback, no actionable message.
- **Fix**: wrap the install block in `try/except snap_lib.SnapError`, set `MaintenanceStatus(f"Failed to install {snap_name}: {e}")`, return early; raise `SnapInstallError` instead of letting `SnapError` propagate.
- **Linter rule**: "Subprocess/snap call without exception handling in install path" — mechanically checkable by AST analysis.

### Unguarded relation data access in `_get_dashboards`

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/integrations.py:394`
- **Evidence**:
  ```python
  dashboards = json.loads(rel.data[rel.app].get("dashboards", "{}"))  # line 394
  ```
  No check that `rel.app` is not `None`, no try/except around the access. This line is uncovered in unit tests. `rel.app` is also used directly on lines 395-401 without null guards.
- **Impact**: if the relation is broken mid-iteration or `rel.app` is `None`, `rel.data[None]` raises `KeyError`, propagating through `_get_dashboards` → `forward_dashboards` → `_reconcile` with no catch in the outer loop. Requires a rare broken-relation state, but leaves an unhandled exception during reconcile.
- **Fix**: add `if rel.app is None: continue` before the access, and wrap the `json.loads` call in try/except.
- **Linter rule**: "relation.data access without null/app guard" — mechanically checkable by AST analysis.

### Snap connection failures are silently swallowed

- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:351-354`
- **Evidence**:
  ```python
  except snap.SnapError as e:
      logger.error(f"error connecting plug {plug} to opentelemetry-collector:logs")
      logger.error(e.message)
      # TODO: should we fail loudly and error?
  ```
  Lines 351-353 are missing from unit test coverage. The error is logged as ERROR but the charm continues with no status change.
- **Impact**: if a snap log endpoint connection fails, the charm continues without that log source. The operator sees only an ERROR log, not a charm status change; there is no recovery path and the data is silently dropped.
- **Fix**: if the snap log endpoint is required for a relation, set `WaitingStatus` or `BlockedStatus` indicating which connection failed.
- **Linter rule**: not established.

### Bare `except Exception` swallows errors in certificate processing

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:474`
- **Evidence**:
  ```python
  except Exception as e:
      logger.warning(f"Certificate processing failed, continuing without certs: {e}")
  ```
  Lines 473-476 are missing from unit test coverage. This catches all exceptions, including `KeyboardInterrupt`, `SystemExit`, `MemoryError`, and programming errors.
- **Impact**: unexpected errors during certificate processing are masked; the operator only sees a warning log and the charm silently continues without certificates.
- **Fix**: catch specific exceptions, e.g. `except (OSError, PermissionError, ValueError, json.JSONDecodeError) as e:`.
- **Linter rule**: "Bare `except Exception` outside of test code" — mechanically checkable with ruff.

### `os.chown` in `_ensure_lock_dir_exists` has no error handling

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/singleton_snap.py:134`
- **Evidence**:
  ```python
  os.chown(cls.LOCK_DIR, os.geteuid(), os.getegid())  # line 134
  ```
  No try/except around the call; lines 147-148 are missing from unit test coverage. `SingletonSnapManager.__init__` runs during install hooks (in `_install_snaps`) and during snap removal in remove hooks.
- **Impact**: `os.chown` requires elevated privilege; works in LXD (root) but in non-root Juju agents or strictly-confined snaps this raises `PermissionError` and crashes snap manager initialization.
- **Fix**: wrap in try/except `PermissionError`, log a warning if it fails, but do not fail — `makedirs` already created the directory correctly.
- **Linter rule**: "os.chown without PermissionError guard" — mechanically checkable.

### Secret files written with world-readable permissions

- **Severity**: medium
- **Kind**: security / bug
- **Where**: `src/charm.py:813`
- **Evidence**:
  ```python
  filepath.write_text(secret, mode=0o644)  # line 813
  ```
  External config secrets (`render=file`) are written to `EXTERNAL_CONFIG_SECRETS_DIR` with mode `0o644` — world-readable; the directory itself is `0o755`. `_write_secrets_to_disk` writes all secrets with the same permissions regardless of sensitivity. `_write_ca_certificates_to_disk` also writes with `0o644`, but that is acceptable since certificates aren't secret.
- **Impact**: secret content on disk is accessible by any local user. In a shared-machine environment (the subordinate charm runs alongside other workloads on the same host), this is a real exposure — the code comment "snap confinement restricts access" is an assumption, not a guarantee.
- **Fix**: write secrets with mode `0o600` (owner-only). Leave CA certificate permissions as-is.
- **Linter rule**: "Secret content written with mode 0o644 or broader" — mechanically checkable.

### Status precedence issue — intermediate ActiveStatus visible

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:576-587`
- **Evidence**: `ActiveStatus()` is set first, then immediately overwritten by `BlockedStatus` for memory limit or missing relations:
  ```python
  self.unit.status = ActiveStatus()        # line 576
  if not valid_mem_limit:                  # line 577
      self.unit.status = BlockedStatus(...) # line 579
  if missing_relations := _get_missing_mandatory_relations(self):  # line 583
      self.unit.status = BlockedStatus(missing_relations)         # line 585
  ```
  Lines 571-580 and 587 are missing from unit test coverage. The snap-revision-mismatch path (line 575) correctly avoids this via early return.
- **Impact**: monitoring systems watching `juju status` could observe a brief `ActiveStatus` before the correct `BlockedStatus` is set.
- **Fix**: check blocking conditions first and return early if blocked; only set `ActiveStatus()` at the end.
- **Linter rule**: "Multiple unit.status assignments in same method without early return" — mechanically checkable.

### Charm does not detect or recover from workload crashes

- **Severity**: low
- **Kind**: bug / ux
- **Where**: `src/charm.py` (no health monitoring)
- **Evidence**: `juju exec --unit opentelemetry-collector/1 'sudo snap stop opentelemetry-collector'` stopped the snap; no hook triggered; the snap remained stopped indefinitely and the charm stayed in `BlockedStatus` with no indication the workload was down. The only health signal is config-hash-based restart detection in `_reconcile`, which fires only on config changes — no pebble watch, health check, or periodic polling.
- **Impact**: if the collector snap crashes or is killed, the charm continues reporting `BlockedStatus`/`ActiveStatus` while the workload is actually down; an operator watching `juju status` has no way to know telemetry collection has stopped.
- **Fix**: consider a periodic health check or polling of the snap service status; at minimum, surface workload state in the unit message when the snap is not running.
- **Linter rule**: not established.

### Non-leader units accumulate stale dashboard files

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:195-197` (leader-only cleanup), `src/charm.py:496` (all-units write)
- **Evidence**: `integrations.cleanup()` is called only for the leader (lines 195-197), but `integrations.forward_dashboards()` → `_add_dashboards()` is called for all units (line 496). Issue #365 tracks this explicitly.
- **Impact**: when a dashboard-providing relation is removed, only the leader cleans up its destination directory; non-leader units accumulate stale dashboard files.
- **Fix**: call `cleanup` for all units, or add a non-leader-specific cleanup path for the dashboards directory.
- **Linter rule**: not established.

### Flapping due to unsorted iteration (issue #356)

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:449-450`, `src/integrations.py:163`
- **Evidence**: `loki_endpoints` is built from an unsorted iteration over a set or dict, producing non-deterministic order that gets written to the on-disk config file. Issue #356 tracks this.
- **Impact**: the config file's content changes on every reconcile purely due to ordering, changing the config hash and triggering unnecessary workload restarts.
- **Fix**: sort `loki_endpoints` before writing to disk.
- **Linter rule**: "Unsorted iteration feeding into on-disk file" — mechanically checkable by linting tools.

### Deprecation warnings in bundled charm libraries

- **Severity**: low
- **Kind**: maintenance-risk
- **Where**: multiple bundled libraries
- **Evidence**: unit test runs produce deprecation warnings:
  1. `tls_certificates.py:1310` — `generate_private_key()` deprecated → use `PrivateKey.generate()`
  2. `tls_certificates.py:1396` — `generate_csr()` deprecated
  3. `tls_certificates.py:1448` — `generate_ca()` deprecated
  4. `tls_certificates.py:1508` — `generate_certificate()` deprecated
  5. `tls_certificates.py:1738` — `JujuVersion.from_environ()` deprecated
  6. `cos_agent.py` + `tracing.py` — Pydantic v1 `.json()` deprecated → use `model_dump_json()`
  7. `tracing.py:276` — Pydantic v1 `__fields__` deprecated → use `model_fields`
- **Impact**: these APIs will break when Pydantic v2/newer ops is required; noisy test output today, breaking change risk later.
- **Fix**: update bundled libraries to versions using current APIs.
- **Linter rule**: "Deprecation warnings in test runs" — mechanically checkable.

### `_reconcile` method is too long

- **Severity**: low
- **Kind**: maintainability
- **Where**: `src/charm.py:197-595` (~400 lines)
- **Evidence**: issue #79 explicitly calls out the 300+ line `_reconcile` method as needing refactoring.
- **Impact**: hard to test, review, and maintain; multiple concerns interleaved.
- **Fix**: extract per-integration methods, status-setting logic, and hash-checking/restart logic.
- **Linter rule**: "Method longer than 200 lines" — mechanically checkable.

### Three spelling errors (codespell)

- **Severity**: low
- **Kind**: lint / docs
- **Where**: `charmcraft.yaml:190`, `src/grafana_dashboards/overview-dashboard.json:494,1875`
- **Evidence**:
  1. `charmcraft.yaml:190`: "agregating" → "aggregating"
  2. `overview-dashboard.json:494`: "Incomming" → "Incoming"
  3. `overview-dashboard.json:1875`: "groupping" → "grouping"
  Found with `codespell -q 3 .`. The "groupping" typo is linked to open issue #344 — the Grafana dashboard's `sum by` expression breaks when the `grouping` variable contains commas (Grafana's `group` parameter does not accept commas in the variable definition).
- **Impact**: the dashboard bug means the "Additional grouping" feature is broken for any user with comma-containing grouping labels.
- **Fix**: fix the three typos; fix the dashboard `sum by` expression per issue #344.
- **Linter rule**: "codespell failures" — mechanically checkable with `codespell` in CI.

## Worth copying

1. **ConfigBuilder pattern** (`src/config_builder.py`): clean, extensible builder pattern for constructing the OTEL config, with good separation between low-level YAML construction (`ConfigBuilder`) and high-level feature methods (`ConfigManager`). 97% coverage.
2. **SingletonSnapManager** (`src/singleton_snap.py`): file-based registration for coordinating snap installation across multiple units on a shared machine. Well-documented, comprehensive error handling for malformed lockfiles. 96% coverage.
3. **Config merge handling**: `add_external_configs` in `ConfigManager` validates and merges externally-supplied configuration with proper error handling (`yaml.YAMLError` caught, logged, skipped).
4. **Port map validation** (`config_builder.py:build_port_map`): comprehensive validation of port override strings with clear error messages.
5. **Hash-based restart detection**: config hash includes CA cert directory hash, server cert hash, and config hash, and only restarts when something actually changed.
6. **Integration test assertions** (`tests/integration/test_principal.py`): actually assert behaviour (debug-log patterns, node metrics scraping, snap service status) rather than just waiting for active/idle.
7. **Snap refresh regression test** (`tests/integration/test_snap_refresh.py`): good coverage of the upgrade path — deploys old revision, refreshes to current, verifies no snap revision mismatches.
8. **Memory limiter documentation**: `memory_limit_percentage` config option includes a clear table documenting input/output behaviour for all edge cases (negative, 0, 50, 100).
9. **Removal hooks integration tests** (`tests/integration/test_removal_hooks.py`): comprehensive scenarios (1 subordinate/1 machine, 2 subordinates/1 machine, 2 subordinates/2 machines, co-located metrics) verifying actual disk state.
10. **`opentelemetry_collector_integrator` library** (`lib/charms/opentelemetry_collector_integrator/v0/`): well-written, proper error handling, Pydantic validation, secret URI parsing, comprehensive docstrings.
11. **Test conftest fixture setup** (`tests/unit/conftest.py`): 20+ fixtures, autouse patches for common operations (snap, hostname, certs, directories, OTEL version), proper Scenario Context setup with virtual charm_root.

## Common-practice notes

1. Standard `lib/charms/<interface>/<version>/` layout — follows convention.
2. ops framework usage (`CharmBase`, event types, status types) is correct throughout.
3. Thorough config validation (ports, time formats, memory limits, extra_alert_labels) with actionable `BlockedStatus` messages — except for `processors`.
4. Correctly uses `scope: container` for `juju-info` and `cos-agent` relations.
5. Good separation into `tests/unit/` and `tests/integration/`, with pytest-bdd for feature files.
6. Uses `uv` for dependency management with `pyproject.toml`.
7. Has a terraform module under `terraform/`.
8. Ships 12 bundled charm libraries under `lib/charms/` — heavy, but follows the pattern for charms needing stable interfaces across Juju versions.
9. Unit tests use `ops.testing.Context` (Scenario) with comprehensive conftest fixtures; the venv's Scenario/ops version mismatch is masked by fixture overrides (see Open questions).

## Tests

### Unit tests

**Status**: 171 passed, 1 skipped, 208 warnings in 61.0s (venv with ops 3.8.1 + `charmlibs-interfaces-otlp` installed). All tests pass.

**Coverage by file**:

| File | Coverage |
|---|---|
| `src/charm.py` | 77% (89 stmts missing) |
| `src/integrations.py` | 87% (20 stmts missing) |
| `src/config_manager.py` | 81% (24 stmts missing) |
| `src/config_builder.py` | 97% |
| `src/singleton_snap.py` | 96% |
| `src/snap_fstab.py` | 80% |
| `src/snap_management.py` | 55% (entire install path untested) |
| `src/utils.py` | 88% |

**Key uncovered paths** (relevant to findings):
- `src/config_manager.py:634` — `yaml.safe_load(processors_raw).items()`, no test with invalid YAML or wrong type. Critical gap: this is the exact line that causes `ErrorStatus` in production.
- `src/charm.py:351-353` — snap plug connection error handling.
- `src/charm.py:474-476` — bare `except Exception` swallowing errors.
- `src/charm.py:571-580,587` — status precedence / multiple ActiveStatus assignments.
- `src/charm.py:638-640` — `os.chown` in `_ensure_lock_dir_exists`.
- `src/charm.py:100-123` — install/upgrade-charm/remove hook code paths (mocked, not unit-tested).
- `src/integrations.py:396` — unguarded `rel.data[rel.app]` access.
- `src/snap_management.py:119-137` — `install_snap`, entirely untested.
- `src/charm.py:601-612` — `_otelcol_version` subprocess call, mocked in all tests.
- `src/charm.py:808-815` — `_write_secrets_to_disk` / `_write_ca_certificates_to_disk` error paths.

### Integration tests

**Status**: not run in this review (requires a long-running Juju model with related charms and `pytest-jubilant`). Individual scenarios were instead exercised live against a deployed charm (see Deployment log and Observed behaviour).

Suite is comprehensive on inspection:
- `test_principal.py` — deploys principal, relates, verifies node metrics scraped, `/var/log` scraped, path exclusions applied, node-exporter collectors running.
- `test_removal_hooks.py` — 4 scenarios (1s/1m, 2s/1m, 2s/2m, co-located metrics), verifies actual disk state.
- `test_snap_refresh.py` — upgrade path, verifies no snap revision mismatches.
- `test_external_config.py`, `test_log_rotation.py`, `test_tracing.py`, `test_cos_agent.py` — cover external config, log rotation, OTLP tracing, and cos-agent aggregation (metrics, logs, alerts, dashboards).
- `test_tls_certificates.py` — tests `WaitingStatus` during cert wait and the HTTP→HTTPS→HTTP transition; the HTTPS endpoint provision test is skipped (ops bug #1858).

**Live integration tests performed in this review**: TLS relation with `self-signed-certificates` — CSR sent, `WaitingStatus` observed in status history, certificate written to disk, relation removed gracefully.

### Linting

- `ruff` on `src/`: all checks passed.
- `ruff` on `lib/`: 11 `RET505` (unnecessary `elif` after `return`) in the bundled `tls_certificates_interface/v4/tls_certificates.py` library; none in the charm's own code.
- `pyright` on `src/`: 2 import resolution errors for `charmlibs.interfaces.otlp` — a pyright venv-configuration issue, not a real code error (the module is installed and importable).
- `codespell` on repo: 3 spelling errors (see finding above).
- YAML validation on `*.rules`: only `mdadm.rules` fails to parse (see finding above).

### Skipped tests

- `test_https_endpoint_is_provided` (`test_tls_certificates.py`): skipped due to [operator#1858](https://github.com/canonical/operator/issues/1858). The charm's ability to provide its TLS endpoint over `receive-loki-logs` is not verified by the test suite — a feature gap, not just a test gap.

### Open issues confirmed

- **#391** — migrate cos_agent to charmlibs; confirms the private API usage / GC warning finding.
- **#365** — stale dashboard files on non-leader; confirms that finding.
- **#356** — flapping due to unsorted iteration; confirms that finding.
- **#344** — dashboard grouping variable typo; confirms the "groupping" codespell finding.
- **#341** — `update-ca-certificates` not triggered after `receive-ca-cert` added; the `reconcile` action works around this (fixed by adding `reconcile` to the events triggering `refresh_certs()`, `git log 82e2436`).
- **#388** — filesystem collector reports incorrect mount point sizes (snap confinement namespace collision).
- **#329** — otelcol cannot check disk utilization of `/var` on CIS-hardened environments.
- **#267** — `node_filesystem_*` metrics missing for encrypted/LVM filesystems (snap restrictions on `/dev/mapper/`).
- **#256** — snap permissions to read `/sys/fs/cgroup/memory.max` (AppArmor denies this, breaking the memory limiter processor).
- **#281** — alerts unclear and too critical.
- **#371** — should block otelcol on invalid cos_agent scrape jobs.
- **#273** — open question: should the charm be Blocked if only `external-config` is established?
- **#236** — hook error with ceph-mon relation (confirmed in observed behaviour).
- **#79** — refactor `_reconcile` method; confirms that finding.
- **#71** — leader-only tracing publish, acknowledged known issue.

## Docs

- **README.md**: clear usage instructions explaining the subordinate charm pattern; brief snap description; points to CONTRIBUTING.md.
- **charmcraft.yaml**: comprehensive description of relations, config options, and features; good documentation of known limitations; contains the "agregating" typo (see spelling finding).
- **CONTRIBUTING.md**: brief but useful developer guidance.
- **terraform/README.md**: explains module usage with examples.
- **Charmhub description**: comprehensive, matches `charmcraft.yaml`, explains key features and limitations.

## Open questions

1. **ops 4.x / Scenario requirement**: `pyproject.toml`'s `charmlibs-pathops` and `cosl` constrain ops to <= 3.8.1, but `ops.testing.Context` (Scenario) requires ops >= 4.0. The venv resolves this enough to run unit tests (with `charmlibs-interfaces-otlp` installed), but the mismatch is masked by fixture overrides rather than actually resolved.
2. **Secret file permissions**: secrets are written world-readable (`0o644`). May be intentional given snap confinement, but should be documented explicitly or tightened to `0o600`.
3. **snapd availability**: `os.chown` and snap operations are used extensively; no fallback if snapd is unavailable.
4. **`_configure()` public alternative**: `certificates._configure(None)` (`integrations.py:584`) needs a public API replacement once the TLS certificates library is migrated; no issue currently tracks this specifically.
5. **`_get_dashboards` severity**: the `rel.app is None` case would require a relation in a broken/removal state, which is rare in practice — but the resulting error propagates through the entire reconcile, so it warrants a guard regardless.
6. **k8s substrate**: no k8s support; integration tests don't cover k8s scenarios. The bundled `cosl` library has unused k8s-specific paths.
7. **`install_snap` crash severity**: `snap.ensure()` can raise `snap_lib.SnapError` for network/snapd failures; visible in hook output during install/upgrade-charm, but leaves the charm in `ErrorStatus` with no actionable message.
8. **Skipped HTTPS endpoint test**: `test_https_endpoint_is_provided` is important for charms that need to discover the OTEL collector's receive endpoint over TLS; currently skipped due to an ops framework bug, not verified.
