# sloth-k8s

sloth-k8s deploys the Sloth SLI/SLO generator as a Kubernetes charm: it receives SLO specs over relations, runs `sloth generate`, and pushes the resulting Prometheus rules. The codebase is clean (0 ruff errors, 0 pyright errors, 83 passing unit tests, good separation between `charm.py` and the workload class), but the review found two critical bugs that make the charm unsafe to run in production as-is: scaling to 2+ units permanently bricks the unit (only recoverable via `kubectl delete pod`), and TLS certificate transfer writes certs to the wrong container, making that integration completely non-functional. A maintainer should fix the `__init__` early-return/scale-up bug first — it is a silent, permanent lockup with no operator-visible warning — then fix the cert_transfer container bug or remove the integration as tracked in issue #64.

| | |
|---|---|
| Repo | canonical/sloth-k8s-operator @ `861bd71` (2026-07-13) |
| Charms | sloth-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5, latest/edge rev 19) and concierge-k8s-3 (Juju 3.6.25, latest/edge rev 19) |
| Reviewed | 2026-07-28 |

## What it does

Sloth converts declarative SLO specifications into Prometheus recording and alerting rules. The charm runs the Sloth binary in a container, accepts SLO specs over the `sloth` relation (via the `charmlibs-interfaces-sloth` library with Pydantic validation), runs `sloth generate`, writes the rules to disk, and pushes them to Prometheus via `metrics-endpoint` and `remote-write`. It also provides Grafana dashboards via `grafana-dashboard`, supports configurable SLO period windows, handles TLS certificate transfer via `certificate_transfer` (see critical finding below), accepts logs via `loki_push_api`, supports charm tracing via `charm-tracing`, and registers with the COS Catalogue.

## Deployment log

### Juju 4 (concierge-k8s-4, models rv-sloth-deep3, rv-sloth-deep4, rv-sloth-deep5)

`juju deploy sloth-k8s --channel edge --trust` → revision 19, version 0.15.0, active in ~28–30 seconds. Deployed fresh five times across three models to test different scenarios.

### Juju 3 (concierge-k8s-3, earlier round)

Same deploy → revision 19, version 0.15.0, active in ~30 seconds. No behavioural differences observed between Juju versions.

### Config tests (confirmed fresh on rv-sloth-deep4 and rv-sloth-deep5)

- `slo-period=7d` without windows → **blocked**: `Custom slo-period '7d' requires slo-period-windows configuration` ✓
- `slo-period=30d` / `28d` → **active** ✓
- `slo-period=7d` + valid `slo-period-windows` YAML → **active** ✓
- `slo-period=7d` + invalid YAML (`not: valid: yaml: {{{`) → **active** (bug: error logged at ERROR, status unchanged)
- `slo-period=7d` + valid YAML missing required fields (no `ticket` section) → **active** (bug: same)
- `slo-period=7d` + 19KB YAML with 200+ unknown keys → **active** (Pydantic validation fails, logged at ERROR, status unchanged)
- Non-numeric `slo-period=banana` → **blocked** ✓
- `slo-period='30d; echo hacked'` → **blocked** (treated as unknown period, not specifically rejected as dangerous input)
- Negative/empty/very-large `slo-period` values → **blocked** ✓
- No-op config change (`slo-period=30d` when already `30d`) → full reconcile cycle fires (×4 with Juju 4 restarts), no guard against no-op changes

### Config-changed hook multiply-reconciles (fresh observation on rv-sloth-deep5)

A single `juju config sloth-k8s slo-period=30d` produces **4 copies** of `Collected 0 SLO specifications` in debug-log. On Juju 4, the charm process restarts mid-hook (`ops 3.6.0 up and running` appears twice per hook), and each restart triggers both the `__init__` reconcile (`charm.py:107`) and the event-handler reconcile (`charm.py:241`). Timestamps: reconciles at 13:16:09 (init), 13:16:22 (restart+init), 13:16:22 (event handler), 13:16:22 (second restart+event handler). With SLO providers present, `sloth generate` runs 4× per hook, Prometheus relation data is pushed 4×, and dashboard processing repeats 4×.

### Scale-up lockup test (fresh reproduction on rv-sloth-deep5, deeper investigation)

```
juju scale-application sloth-k8s 2
→ Both units go blocked "You can't scale up sloth-k8s."

juju scale-application sloth-k8s 1
→ Unit 1 removed. Unit 0 stays blocked.
→ juju exec --unit sloth-k8s/0 "relation-list -r sloth-peers:0"
    → OUTPUTS "sloth-k8s/1" — the departed unit is STILL in the peer relation!
→ juju config sloth-k8s slo-period=28d: still blocked.
→ juju debug-log shows "Application has scale >1" on every subsequent hook.
→ Only kubectl delete pod sloth-k8s-0 recovers.
```

Root cause confirmed: the `return` in `__init__` (`charm.py:100`) after the scale check prevents registration of `cosl.reconciler.observe_events`. Without that registration, no handler for `relation-departed` exists. When unit 1 departs, the hook does not execute, and the departed unit stays in `peer_relation.units` permanently (confirmed via `relation-list`). On every subsequent hook, `is_scaled_up()` still returns True because the ghost unit remains, and `__init__` hits the early return again — an unbreakable loop. Only a pod restart clears the peer relation and lets `is_scaled_up()` return False.

### Integration tests

All tested on rv-sloth-deep4 and rv-sloth-deep5:

- **certificate_transfer** (`self-signed-certificates` 1/edge rev 659): relation formed via `receive-ca-cert:send-ca-cert`. Certificate written to `/usr/local/share/ca-certificates/certificate_transfer-0.cert` in the **charm** container only — the workload container directory is empty. After removing the relation, `certificate_transfer-0.cert` persists — not cleaned up (the `else` branch only unlinks `ca.cert`, which was never created).
- **metrics-endpoint** (`prometheus-k8s` 2/stable rev 301, and 1/edge rev 247 in an earlier round): relation formed, rule files pushed to charm dir. Prometheus itself is blocked due to cloud RBAC limitations (cannot apply resource limit patches), unrelated to sloth; relation data flows correctly.
- **logging** (`loki-k8s` 2/stable rev 217, and 1/edge rev 207 earlier): relation formed via `loki_push_api`. Loki also blocked by the same cloud RBAC issue; relation plumbing works.
- **grafana-dashboard** (`grafana-k8s` 1/edge rev 160, earlier round): dashboard JSON pushed successfully.
- **ingress** (`traefik-k8s` edge rev 393, earlier round): relation formed, `application-data: {}` on the sloth side. No ingress route configured. No handler code exists.
- **catalogue**: could not test — `catalogue-k8s` requires `ubuntu@26.04`, unavailable on this cloud.
- **charm-tracing**: could not test — `tempo-coordinator-k8s` requires `ubuntu@26.04`.
- **sloth** (SLO provider, e.g. `parca-k8s`): could not test — `parca-k8s` `dev/edge` requires `ubuntu@26.04`.

### Failure injection

- **Delete sloth binary** (`kubectl exec -c sloth -- rm /usr/bin/sloth`): charm stays **active**. `ops.pebble.APIError`/`error attempting to fetch sloth version from container` logged at ERROR. Workload version becomes empty (was "0.15.0"). No BlockedStatus is ever set.
- **Corrupt generated rules file**: wrote invalid YAML to `/etc/sloth/rules/fake-service.yaml`. Charm stays **active** — the exception in `get_alert_rules` is caught and logged, not surfaced as status.
- **Restart unit (pod delete)**: recovers from the scale-up lockup; takes ~15s to reach active.
- **Remove cert_transfer relation while running**: sloth is unaffected (the write was always to the charm container). Stale cert files not cleaned up (confirmed on rv-sloth-deep5).

### Workload inspection (kubectl exec into sloth container)

- Pebble service `sloth` enabled but **inactive** (intentional — sloth is a CLI generator, not a server; `_reconcile_sloth_service` is dead code present in the class but never called)
- Resource usage: ~1m CPU, 31Mi memory
- Directories `/etc/sloth/slos/`, `/etc/sloth/rules/`, `/etc/sloth/windows/` created; empty when no SLO providers
- Binary `/usr/bin/sloth` (symlink from `/bin/sloth`), version 0.15.0 (from `ubuntu/sloth@sha256:23878bf0...`)

### Actions

`juju actions sloth-k8s` → "No actions defined." The `_on_list_endpoints_action` method exists in `charm.py:247` but is never registered via `self.framework.observe`, and no action is declared in `charmcraft.yaml`. Dead code.

### juju refresh

Only one revision (19) exists on charmhub, so inter-revision refresh could not be tested. The charm has no explicit `upgrade-charm` handler; it relies on `cosl.reconciler.observe_events` for all lifecycle events.

### Application removal

Clean removal observed. No stuck resources, no lingering pods. Relations depart cleanly, though stale `certificate_transfer-*.cert` files are left behind in the charm container.

## Findings

### Scale-up permanently bricks the charm via a permanent peer-relation ghost unit
- **Severity**: critical
- **Kind**: bug
- **Where**: `charm.py:89`, `charm.py:92-97`, `charm.py:100`
- **Evidence**:
  ```python
  # line 89: registered BEFORE the scale check
  self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)

  # lines 92-97: scale check with early return
  if self.is_scaled_up():
      logger.error(
          "Application has scale >1 but doesn't support scaling. "
          "Deploy a new application instead."
      )
      return  # prevents registration of cosl.reconciler.observe_events at line 100

  # line 100: never reached when scaled up
  cosl.reconciler.observe_events(self, cosl.reconciler.all_events, self._on_reconcile_event)
  ```
  The early `return` prevents `cosl.reconciler.observe_events` from registering, so no handler for `relation-departed` exists. When a peer unit departs on scale-down, the hook does not execute, and the departed unit stays in `peer_relation.units` permanently — confirmed via `juju exec --unit sloth-k8s/0 "relation-list -r sloth-peers:0"` returning `sloth-k8s/1` long after scale-down. On every subsequent hook, `__init__` runs, `is_scaled_up()` still returns True (ghost unit present), and the early return fires again — an unbreakable loop. Reproduced across Juju 4.0.5 and Juju 3.6.25 with identical behaviour. Unit tests only exercise single-unit states; `charm.py:93-100` has 0% branch coverage.
- **Why it matters**: An operator who scales up (even briefly, then back down) is left with a permanently broken charm. The log message "Deploy a new application instead" is misleading — after scale-down the operator already has one unit and it is locked. Only `kubectl delete pod` recovers it; the state survives config changes, relation changes, and update-status indefinitely.
- **Fix**: Move the scale check out of `__init__`; never return early there. Register all event handlers unconditionally, including `relation-departed`. Enforce the scale-up guard only as a status check in `_on_collect_unit_status`.
- **Linter rule**: `CharmBase.__init__` must not contain an early `return` before all `self.framework.observe` calls for lifecycle events (install, relation-departed, remove, etc.) — mechanically checkable.

### Certificate transfer writes certificates to the wrong container — completely non-functional
- **Severity**: critical
- **Kind**: bug
- **Where**: `charm.py:183-193` (`_reconcile_cert_transfer`), `charm.py:33` (`CA_CERT_PATH`)
- **Evidence**:
  ```python
  def _reconcile_cert_transfer(self) -> None:
      """Update the TLS certificates for the charm container."""  # docstring says "charm container"
      cacert_path = Path(CA_CERT_PATH)
      if certs := self.certificate_transfer.get_all_certificates():
          for index, cert in enumerate(certs):
              cacert_path.parent.mkdir(parents=True, exist_ok=True)
              cert_file = cacert_path.parent / f"certificate_transfer-{index}.cert"
              cert_file.write_text(cert)  # writes to the CHARM container's filesystem
      else:
          cacert_path.unlink(missing_ok=True)  # only removes ca.cert, not certificate_transfer-*.cert
  ```
  `Path.write_text()` writes to the charm container's filesystem, not the workload (`sloth`) container. On k8s charms these are separate filesystems, so the sloth binary can never read the certificate. Confirmed repeatedly: `kubectl exec -c charm -- ls /usr/local/share/ca-certificates/` shows `certificate_transfer-0.cert`; `kubectl exec -c sloth -- ls /usr/local/share/ca-certificates/` is empty. The unit-test conftest patches `CA_CERT_PATH` to a `tmp_path`, masking the container-boundary bug since `write_text()` succeeds in a single-filesystem test environment.
- **Why it matters**: TLS certificates transferred via `certificate_transfer` are completely inaccessible to the sloth binary. An operator sees the relation form successfully and assumes TLS is configured, but it never was. Open issue #64 notes the maintainers plan to remove this integration entirely since sloth has no UI yet.
- **Fix**: Either remove the integration (per #64) or replace `Path.write_text()`/`mkdir()`/`unlink()` with `self._sloth_container.push()`, `.make_dir()`, `.remove_path()` targeting the workload container. Also fix the `else` branch to clean up numbered `certificate_transfer-*.cert` files.
- **Linter rule**: on k8s charms, `Path().write_text()`/`mkdir()`/`unlink()` inside methods named `_reconcile_*` should be flagged if the target path is not clearly scoped to the charm container — mechanically checkable with path analysis.

### Quadruple reconciliation on every hook (Juju 4)
- **Severity**: high
- **Kind**: performance
- **Where**: `charm.py:107` and `charm.py:239-242`
- **Evidence**: A single `juju config sloth-k8s slo-period=30d` on Juju 4 produces 4 copies of `Collected 0 SLO specifications` in debug-log. The charm process restarts twice per hook (`ops 3.6.0 up and running` appears twice), and each restart triggers both `self.reconcile()` in `__init__` (line 107) and the reconcile registered via `cosl.reconciler.observe_events` (line 241): 2 restarts × 2 reconcilers = 4 reconciles per hook. On Juju 3, the process restarts only once (2× total).
- **Why it matters**: Every hook does 4× the work — runs `sloth generate` 4×, pushes to Prometheus 4×, logs everything 4×. With many SLO providers this is significant CPU churn and log spam.
- **Fix**: Remove the direct `self.reconcile()` call from `__init__` (line 107); the `cosl.reconciler.observe_events` registration is sufficient to trigger reconciliation on the first event.
- **Linter rule**: when `cosl.reconciler.observe_events` is used, `reconcile()` must not also be called directly in `__init__` — mechanically checkable.

### Missing sloth binary leaves charm active but non-functional
- **Severity**: high
- **Kind**: bug / ux
- **Where**: `sloth.py:344-349` (`version`), `charm.py:212` (`_on_collect_unit_status`), `charm.py:118-147` (`reconcile`)
- **Evidence**:
  ```python
  def version(self) -> str:
      try:
          version_out = self._container.exec([DEFAULT_BIN_PATH, "version"]).stdout
      except ops.pebble.Error:
          logger.exception("error attempting to fetch sloth version from container")
          return ""
  ```
  When the binary is missing, `version()` returns `""` and `set_workload_version()` shows an empty version. `reconcile()` calls into `_generate_rules_from_slo`, which raises `ops.pebble.ExecError` (caught and logged at WARNING). The charm continues with no rule generation but reports `ActiveStatus("")`. Confirmed after `kubectl exec -c sloth -- rm /usr/bin/sloth`: ERROR-level log, no status change. The conftest patches `Sloth.version` to always return `"0.11.0"`, so this path is never exercised in unit tests.
- **Why it matters**: A bad workload image (e.g. missing binary from a failed build) leaves the charm silently non-functional. An operator only discovers this when SLO rules stop updating; the empty workload version is the only hint and is easily missed.
- **Fix**: In `_on_collect_unit_status`, after `set_workload_version()`, check for an empty version and add `BlockedStatus("sloth binary not found at /usr/bin/sloth")`, or surface the failure from within `reconcile()`.
- **Linter rule**: methods that catch `ops.pebble.Error` and return a sentinel value must have that return value checked by callers to set status — partially checkable.

### Invalid slo-period-windows YAML silently ignored — no status change
- **Severity**: high
- **Kind**: bug / ux
- **Where**: `sloth.py:107-114` (`_reconcile_slo_period_windows`), `sloth.py:51-65` (`is_config_valid`), `charm.py:214-224` (`_on_collect_unit_status`)
- **Evidence**:
  ```python
  except yaml.YAMLError as e:
      logger.error(f"Invalid YAML in slo-period-windows config: {e}")
  except ValidationError as e:
      logger.error(f"Invalid AlertWindows specification in slo-period-windows config: {e}")
  ```
  Errors are logged but no blocking status is set. `is_config_valid()` only checks whether `slo-period-windows` is non-empty for custom periods, not whether its content is valid — so invalid YAML for a custom period still results in ActiveStatus. Confirmed with invalid YAML syntax, YAML missing a required `ticket` section, and a 19KB payload with 200+ unknown keys: all produced ERROR logs but stayed active. `sloth.py:107-114` has 0% branch coverage.
- **Why it matters**: An operator configuring a custom period with a typo in their windows YAML sees the charm go active and assumes the config is valid, only discovering the problem when alerts don't fire as expected.
- **Fix**: `is_config_valid()` should re-validate the YAML content, or `_reconcile_slo_period_windows` should return/cache a success flag and error string that `_on_collect_unit_status` reads to set `BlockedStatus` with the specific validation error.
- **Linter rule**: config reconciliation methods that validate and reject input must propagate validation failures to unit status — partially checkable.

### Ingress relation declared but never handled
- **Severity**: high
- **Kind**: bug
- **Where**: `charmcraft.yaml:100-105` (declares `requires: ingress: interface: ingress`), no handler in `charm.py`, `lib/charms/traefik_k8s/v0/traefik_route.py` (447 lines, never imported)
- **Evidence**: `grep -r "ingress\|traefik" src/` returns no matches. The `traefik_route` library is present but unused. When integrated with `traefik-k8s`, the relation forms but `application-data` on the sloth side stays `{}` — no route configuration is pushed. Open issue #64 (2026-07-02) explicitly requests removal of ingress along with catalogue and grafana-source.
- **Why it matters**: An operator relating sloth-k8s to traefik-k8s sees the relation form successfully but nothing happens — misleading, and it bloats the charm with an unused endpoint and library.
- **Fix**: Either implement ingress handling using `TraefikRouteRequirer`, or remove the `ingress` endpoint from `charmcraft.yaml` and the unused library, per #64.
- **Linter rule**: every `requires`/`provides` endpoint declared in `charmcraft.yaml` must have a corresponding import/handler in `src/charm.py` — mechanically checkable.

### Unused library files bloating the charm (2,100 lines dead code)
- **Severity**: medium
- **Kind**: lint / performance
- **Where**: `lib/charms/grafana_k8s/v0/grafana_source.py` (861 lines), `lib/charms/data_platform_libs/v0/s3.py` (792 lines), `lib/charms/traefik_k8s/v0/traefik_route.py` (447 lines)
- **Evidence**: None of these are imported anywhere under `src/`. Total library code is 9,544 lines, of which 2,100 are dead. Open issue #64 requests removal of grafana-source; open issue #87 flags `grafana_source` for a v0→v1 update that is wasted effort while unused.
- **Why it matters**: Dead code bloats the package, increases CI library-checking noise, and creates maintenance burden; contributors or agents may waste time trying to use it.
- **Fix**: Remove all three files.
- **Linter rule**: every `.py` file under `lib/charms/` must have a corresponding `import` statement in `src/` — mechanically checkable.

### Orphaned `certificate_transfer-*.cert` files never cleaned up
- **Severity**: medium
- **Kind**: bug
- **Where**: `charm.py:193-195`
- **Evidence**:
  ```python
  else:
      cacert_path.unlink(missing_ok=True)
  ```
  `CA_CERT_PATH = "/usr/local/share/ca-certificates/ca.cert"`, but written files are named `certificate_transfer-{index}.cert`. The `else` branch only unlinks `ca.cert`, which was never created; the numbered files persist. Confirmed after removing the cert_transfer relation on rv-sloth-deep5: `certificate_transfer-0.cert` still present.
- **Why it matters**: Orphaned files accumulate across relation cycles; while confined to the charm container, it's a stale-state bug and a minor security concern (old certs remaining on disk).
- **Fix**: In the `else` branch, glob and remove all `certificate_transfer-*.cert` files, or remove the whole method along with the integration per #64.
- **Linter rule**: not established.

### `_on_collect_unit_status` does not return after scale-up BlockedStatus
- **Severity**: medium
- **Kind**: performance / bug
- **Where**: `charm.py:202-206`
- **Evidence**:
  ```python
  def _on_collect_unit_status(self, event: ops.CollectStatusEvent):
      if self.is_scaled_up():
          event.add_status(ops.BlockedStatus(...))
      # no return — falls through to:
      if not self._sloth_container.can_connect():
          event.add_status(ops.WaitingStatus(...))
      else:
          self.unit.set_workload_version(self.sloth.version())  # called even when blocked
      # ... continues through config checks, SLO validation, finally ActiveStatus
  ```
  The framework picks the highest-priority status correctly, but `set_workload_version()`, `is_config_valid()`, and `validate_generated_rules()` run unnecessarily every hook while the charm is locked up.
- **Why it matters**: Wasted cycles on a blocked charm, and it muddies status-precedence logic for future maintainers rearranging the checks.
- **Fix**: Add `return` immediately after adding the scale-up `BlockedStatus`.
- **Linter rule**: in `_on_collect_unit_status`, every `event.add_status(ops.BlockedStatus(...))` should be followed by `return` unless a higher-priority status is intentionally also considered — mechanically checkable.

### Stale nginx references in AGENTS.md and integration test helpers
- **Severity**: medium
- **Kind**: docs / test-gap
- **Where**: `AGENTS.md:37`, `AGENTS.md:56`, `tests/integration/helpers.py:8-9,22-35`
- **Evidence**:
  - `AGENTS.md:37`: "Orchestrates nginx, sloth, and nginx-exporter workloads" — the charm has only one container (`sloth`).
  - `AGENTS.md:56`: "Port: 8080 (proxied via nginx on 7994)" — no nginx proxy exists.
  - `tests/integration/helpers.py:9`: `SLOTH_HTTP_PORT = 7994  # nginx proxy port for sloth`
  - `tests/integration/helpers.py:22-35`: `query_sloth_server()` builds curl commands against a nonexistent nginx proxy.
  - `tests/integration/helpers.py:8`: `CA_CERT_PATH = "/usr/local/share/ca-certificates/ca.cert"` — same wrong-container path as `charm.py`.
- **Why it matters**: AGENTS.md misleads developers and agents into implementing nginx handling that doesn't belong; the test helpers are dead code from a prior three-container architecture and would fail if run.
- **Fix**: Rewrite AGENTS.md to reflect the actual single-container, on-demand-generation architecture. Remove or rewrite `query_sloth_server` and the nginx constants in `helpers.py`.
- **Linter rule**: not established.

### Dead code: `_on_list_endpoints_action` never registered
- **Severity**: low
- **Kind**: bug
- **Where**: `charm.py:247-249`
- **Evidence**:
  ```python
  def _on_list_endpoints_action(self, event: ops.ActionEvent):
      """React to the list-endpoints action."""
      event.set_results({})  # TODO: Set endpoints after we have a UI
  ```
  Never registered via `self.framework.observe`, and no action is declared in `charmcraft.yaml`. `juju actions sloth-k8s` returns "No actions defined." — unreachable code.
- **Why it matters**: Confuses maintainers into thinking an action exists.
- **Fix**: Register the action in `charmcraft.yaml` and observe it, or remove the dead method.
- **Linter rule**: methods named `_on_*_action` must be registered via `self.framework.observe` for a corresponding action event — mechanically checkable.

### Hardcoded rule count assumption (17 rules per SLO)
- **Severity**: low
- **Kind**: bug
- **Where**: `sloth.py:233` (`rules_per_slo = 17`)
- **Evidence**: `validate_generated_rules` hardcodes `rules_per_slo = 17` (2 alerts + 7 meta + 8 sli). A future Sloth binary version that changes generated-rule counts would break this check silently.
- **Why it matters**: A sloth binary upgrade could cause false BlockedStatus for valid SLOs, or false ActiveStatus for failed ones.
- **Fix**: Check that each expected group type (alerts, meta_recordings, sli_recordings) exists and that each SLO spec has a corresponding rules file, instead of counting total rules.
- **Linter rule**: not established.

### Catalogue URL is meaningless without a UI
- **Severity**: low
- **Kind**: ux
- **Where**: `charm.py:64-70`
- **Evidence**: `CatalogueConsumer` registers with `url=self._fqdn`, but sloth has no UI or web server. Open issue #64 requests removal for this reason.
- **Why it matters**: The Catalogue entry is misleading — operators clicking it get nothing.
- **Fix**: Remove the Catalogue registration (per #64) or defer it until a UI exists.
- **Linter rule**: not established.

### No guard against no-op config changes
- **Severity**: low
- **Kind**: performance
- **Where**: `charm.py:118-147` (`reconcile` → `_reconcile_relations`)
- **Evidence**: Setting `slo-period=30d` when it was already `30d` still triggers a full (4×) reconcile cycle with file I/O and relation data pushes.
- **Why it matters**: Unnecessary I/O and relation churn on every config-changed hook, even with no actual change.
- **Fix**: In `_reconcile_relations`, check whether alert rules actually changed before calling `set_scrape_job_spec()`/`reload_alerts()` — `sloth.py` already has this content-change-detection pattern elsewhere (lines 93-95, 135-139); apply it in `charm.py` too.
- **Linter rule**: not established.

### Double reconcile visible in every unit test run
- **Severity**: low (confirmatory)
- **Kind**: test-gap
- **Where**: unit test output, all files
- **Evidence**: Every charm unit test run logs two copies of `Collected 0 SLO specifications`, confirming the double-reconcile is baked into `__init__` and is not purely a Juju-4-restart artifact. No test asserts reconcile runs exactly once.
- **Why it matters**: The test suite inadvertently accepts the double-reconcile as expected behaviour.
- **Fix**: Add a test that mocks the SLO requirer and asserts `collected_count == 1` per hook.
- **Linter rule**: not established.

## Worth copying

1. **Clean separation of charm and workload logic**: `charm.py` handles ops framework concerns; `sloth.py` is workload logic taking a plain `Container` object with no charm-level imports — independently testable (47 tests in `test_sloth.py`).
2. **Stale output file cleanup before generation**: `sloth.py:178-182` removes the previous output file before running `sloth generate`, so a failed generation leaves no stale rules and `validate_generated_rules` correctly detects the mismatch.
3. **Comprehensive Pydantic validation of user-facing config**: `alert_windows_models.py` validates duration formats, error budget ranges, and required fields, with 11 dedicated tests at 97% coverage.
4. **Content-change detection before pushing files**: `_reconcile_additional_slos` (`sloth.py:135-139`) and `_reconcile_slo_period_windows` (`sloth.py:93-95`) compare existing content before writing, limiting I/O churn even under repeated reconciles.
5. **Graceful container-not-ready handling**: the `reconcile()` call in `__init__` is wrapped in try/except with a comment noting this is expected during install; the charm goes to `WaitingStatus` instead of `ErrorStatus`.
6. **Thorough workload-level tests**: `test_sloth.py` covers 47 cases including missing output files, stale file cleanup, and partial SLO failures.
7. **No defer, no StoredState**: uses `cosl.reconciler.observe_events` and derives state from relations/config rather than `StoredState` — clean and modern.
8. **External charm library for shared interfaces**: uses `charmlibs-interfaces-sloth` rather than a local `lib/charms/sloth_k8s/` directory, following the emerging COS standard.

## Common-practice notes

- The `cosl.reconciler` pattern is correctly used, but combining it with an eager `self.reconcile()` in `__init__` causes the multiply-reconcile issue; standard COS practice is to let `observe_events` be the sole trigger.
- Uses the external `charmlibs-interfaces-sloth` package rather than a local library directory.
- Modern packaging with `uv` and `pyproject.toml`; tasks managed via `tox`.
- `ops.testing` (`Context`/`State`/`Container`) used for unit tests with an `assert_healthy()` helper; the conftest patches `CA_CERT_PATH`, `Sloth.version`, and `GenericSyncClient` — pragmatic, but it masks real container-boundary and missing-binary bugs.
- The `ingress`, `grafana_source`, `s3`, and `traefik_route` libraries are all dead weight (2,100 lines) — a common pattern in charms templated from a richer architecture; open issues #64 and #87 acknowledge this.
- `certificate_transfer_interface` v1 is the modern approach, but the implementation writes to the wrong container and #64 suggests removal anyway.
- No explicit `upgrade-charm` handler; relies on `cosl.reconciler.observe_events` — standard for a stateless charm.
- `collect_unit_status` uses `event.add_status()` for additive reporting correctly, though missing early returns after `BlockedStatus` slightly undermine the pattern.

## Tests

### Unit tests (ran successfully)

83 tests across 3 files, all pass in ~0.9s:
- `tests/unit/test_charm/test_charm.py` — 31 charm tests using `ops.testing`
- `tests/unit/test_workload/test_sloth.py` — 47 workload tests using `unittest.mock`
- `tests/unit/test_workload/test_alert_windows_models.py` — 11 Pydantic model tests

Coverage (`coverage report -m`):
- `charm.py`: 76% — missing scale-up path (93-97), init exception (105-108), reconcile exception (123), `can_connect` (130-131), `_update_alert_rules` (164-181), `_reconcile_cert_transfer` (188-191), scale-up branch in `_on_collect_unit_status` (203), `_on_reconcile_event` exception (243-244), `_on_list_endpoints_action` (249)
- `sloth.py`: 86% — missing `_reconcile_sloth_service` dead code (88-89), YAML error paths (106-109), stale-removal errors (156-157), `ExecError` handler (189), generic exceptions (200-201), version error paths (345-351)
- `alert_windows_models.py`: 97% — only line 114 (SLO period validator) missed

The conftest patches `CA_CERT_PATH` to a temp path, masking the cert_transfer container bug; patches `Sloth.version` to always return `"0.11.0"`, masking the missing-binary path; and patches `GenericSyncClient` to prevent Kubernetes API calls. Every unit test run logs two copies of `Collected 0 SLO specifications`.

### Lint (ran successfully)

`tox -e lint`: ruff 0 errors; pyright 0 errors, 0 warnings.

### Coverage gaps relative to findings

- No test for scale-up lockup — `charm.py:93-100` is 0% branch-covered.
- No test for missing sloth binary — `sloth.py:345-351` uncovered.
- No test for invalid slo-period-windows producing BlockedStatus — `sloth.py:107-114` uncovered.
- No test for `_reconcile_cert_transfer` — `charm.py:188-191` uncovered; conftest path patch masks the container-boundary bug.
- No test for `_update_alert_rules` (`charm.py:164-181`) uncovered.
- No test for `_on_list_endpoints_action` (`charm.py:249`) — unreachable.
- No test that reconcile runs exactly once per hook.

### Integration tests (not runnable — cloud limitations)

- `test_basic.py` — deploys sloth, waits for active, tears down; minimal but would pass.
- `test_slo_to_rules.py` — deploys full COS stack (sloth, grafana, prometheus, parca), integrates, checks generated rules; well-structured, but depends on `parca-k8s` `dev/edge` requiring `ubuntu@26.04`, not runnable on this cloud.
- `test_slo_validation.py` — BDD-style (`pytest-bdd`), configures an invalid SLO and checks BlockedStatus; good error-path coverage, same base-dependency issue.

`tests/integration/helpers.py` contains dead nginx-proxy code (port constants, `query_sloth_server()`).

## Docs

**README**: comprehensive — architecture with Mermaid diagram, two integration paths, full config documentation, troubleshooting section.

**Docs site** (`docs/`): full Sphinx documentation following Diátaxis (tutorial, how-to, reference, explanation), multiple integration scenarios documented.

**AGENTS.md**: stale and misleading — confirmed at source:
- Line 37: "Orchestrates nginx, sloth, and nginx-exporter workloads" — only one sloth container exists
- Line 56: "Port: 8080 (proxied via nginx on 7994)" — no nginx proxy exists
- References `sloth serve` running under Pebble — the service is not started; `_reconcile_sloth_service` is dead code

**Charmhub listing**: accurate on `edge` channel; only one revision; publisher is an individual.

**Registry mismatch**: none observed — `juju deploy sloth-k8s --trust --channel edge` works correctly.

## Open questions

1. Why is `ingress` still in `charmcraft.yaml`? Open issue #64 (2026-07-02, 26 days before this review) requests removal along with catalogue and grafana-source, and the maintainers have acknowledged but not acted on it.
2. Is the 4× reconcile causing real harm beyond log spam? Reconcile is mostly idempotent via content comparison in `sloth.py`, but running `sloth generate` 4× per hook with many SLO providers is wasteful CPU/I/O regardless.
3. How was the integration test suite validated in CI? `test_slo_to_rules.py` depends on `parca-k8s dev/edge`, which requires `ubuntu@26.04` — a base this charm (24.04) can't co-deploy with on this cloud. Unclear whether this test has ever run successfully.
4. Is `certificate_transfer` serving any purpose at all? Even with the container bug fixed, there's no evidence `sloth generate` consumes TLS configuration. Combined with issue #64, this looks like dead functionality that should be removed rather than repaired.
5. Why does the charm process restart twice per hook on Juju 4? (unverified as a Juju-4-specific framework behaviour — observed but root cause not confirmed.) Either way, removing `self.reconcile()` from `__init__` fixes the multiply-reconcile symptom regardless of restart count.
6. Does the charm need an explicit `upgrade-charm` handler? Not currently, since it's stateless and relies on `cosl.reconciler.observe_events`, but this would need revisiting if `StoredState` is ever introduced.
