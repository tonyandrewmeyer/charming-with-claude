# airflow-core-operators

A mono-repo of four K8s sidecar charms (API server, Scheduler, Triggerer, DAG Processor) forming the Airflow core component set, all dependent on an external `airflow-coordinator` charm for configuration. The code is clean — a consistent reconciler pattern with no `defer()`, actionable status messages, decent scenario-test coverage — but a library bug in `AirflowCoordinatorCoreRequires` makes the charms **unusable on Juju 4.x (100% reproducible) and unreliable on Juju 3.6** (reproducible depending on event-ordering timing): the requirer stops observing `relation_joined`, so if `pebble_ready` fires before the coordinator relation is added, the charm never notices the relation and sticks at Blocked forever, recoverable only by deleting the pod. A maintainer should fix the missing `relation_joined` observation first — everything else (hard-coded version/hash fields, code duplication, missing actions) is secondary until charms can reliably detect their only required relation.

| | |
|---|---|
| Repo | canonical/airflow-core-operators @ `9a00452` (2026-07-17) |
| Charms | airflow-api-server-k8s, airflow-scheduler-k8s, airflow-dag-processor-k8s, airflow-triggerer-k8s |
| Substrate | k8s |
| Deployed | yes — full stack twice on concierge-k8s-3 (Juju 3.6.25) and core charms + coordinator twice on concierge-k8s-4 (Juju 4.0.5), channel 3.1/edge |
| Reviewed | 2026-08-02 |

## What it does

Each charm runs a single Airflow component (api-server, scheduler, triggerer, dag-processor) in a sidecar container. All four require the `airflow-coordinator` relation, through which they receive a Jinja2-rendered `airflow.cfg`, sensitive data via Juju secrets, optional Kubernetes executor pod specs, webserver OAuth config, and TLS CA chains. The coordinator charm (not in this repo) is the config hub. The API server additionally provides an `airflow-api-server` relation back to the coordinator and an `ingress` relation for Traefik.

All four charms use a single `_reconcile(event)` method: every observed event re-evaluates Pebble connectivity, required relations, config freshness, and service state from scratch. There is no use of `defer()`.

## Deployment log

### Juju 3.6 (concierge-k8s-3) — full stack

```
juju switch concierge-k8s-3
juju add-model rv-airflow-deep --config update-status-hook-interval=10s

juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy pgbouncer-k8s --trust
juju deploy airflow-coordinator-k8s --channel 3.1/edge
juju deploy airflow-api-server-k8s --channel 3.1/edge
juju deploy airflow-scheduler-k8s --channel 3.1/edge
juju deploy airflow-triggerer-k8s --channel 3.1/edge
juju deploy airflow-dag-processor-k8s --channel 3.1/edge

juju integrate pgbouncer-k8s:backend-database postgresql-k8s:database
juju integrate airflow-coordinator-k8s:postgres pgbouncer-k8s:database
juju integrate airflow-coordinator-k8s:airflow-api-server airflow-api-server-k8s:airflow-api-server
for app in airflow-api-server-k8s airflow-scheduler-k8s airflow-triggerer-k8s airflow-dag-processor-k8s; do
  juju integrate airflow-coordinator-k8s:airflow-coordinator $app:airflow-coordinator
done

# Coordinator blocked: "Waiting for fernet key secret configuration"
# Core charms waiting: "Waiting for relation data from coordinator"

FERNET_KEY=$(python3 -c "import cryptography.fernet; print(cryptography.fernet.Fernet.generate_key().decode())")
juju add-secret fernet-key-secret "fernet-key=$FERNET_KEY"
juju grant-secret fernet-key-secret airflow-coordinator-k8s
juju config airflow-coordinator-k8s fernet_key_secret=secret:...

# ~60s later: all 7 apps active
```

Traefik + TLS integration was also tested: `traefik-k8s` (latest/edge) integrated with `airflow-api-server-k8s:ingress`, `self-signed-certificates` integrated with `traefik-k8s:certificates`.

### Juju 4.0 (concierge-k8s-4) — core charms only

```
juju switch concierge-k8s-4
juju add-model rv-airflow-juju4
juju deploy airflow-api-server-k8s --channel 3.1/edge
juju deploy airflow-scheduler-k8s --channel 3.1/edge
juju deploy airflow-triggerer-k8s --channel 3.1/edge
juju deploy airflow-dag-processor-k8s --channel 3.1/edge
juju deploy airflow-coordinator-k8s --channel 3.1/edge
for app in airflow-api-server-k8s airflow-scheduler-k8s airflow-triggerer-k8s airflow-dag-processor-k8s; do
  juju integrate airflow-coordinator-k8s:airflow-coordinator $app:airflow-coordinator
done
```

`postgresql-k8s` 14/stable refuses to deploy on Juju 4.x (base constraints require Juju < 4.0.0), so the full stack cannot be tested there. All 4 core charms deploy and correctly reach Blocked "Missing airflow-coordinator relation" before integration.

### Juju 3.6, second full-stack deploy (rv-airflow-deep3) — all four charms stuck

```
juju add-model rv-airflow-deep3 --config update-status-hook-interval=5m
# same deploy/integrate sequence as above
# Result: ALL 4 core charms stuck at Blocked "Missing airflow-coordinator relation" despite all integrations present
# Event log: pebble_ready at 13:26:03 → Blocked, relation-created at 13:26:31, relation-joined at 13:26:32,
#   two relation-changed events — none triggered reconciliation
# Workaround: kubectl delete pod → pebble_ready re-fires with relation present → charms recover to Waiting
```

### Juju 4.x, second deploy (rv-airflow-j4) — confirmed reproduction

Same result: all 4 core charms permanently stuck at Blocked "Missing airflow-coordinator relation" after integration. Pod restart recovers them. Removing and re-adding the relation on a recovered charm gets it stuck again (`relation_joined` is also missing from `_relation_events`).

## Observed behaviour

**Deploy/converge timing**: Juju 3.6 full stack reaches all-Active in ~3 minutes from `juju deploy` (excluding postgresql install, ~5 min); bottleneck is the coordinator waiting for the fernet key, after which core charms converge within 60s. Juju 4.0 core charms reach Blocked "Missing airflow-coordinator relation" within ~30s.

**Resource usage** (`kubectl top`, idle): api-server 25m CPU/217Mi RAM, scheduler 69m CPU/386Mi RAM, triggerer 33m CPU/223Mi RAM, dag-processor 19m CPU/171Mi RAM.

**Charm size**: 6.0MB for api-server, packed locally with `charmcraft pack`.

**Hook frequency**: with `update-status-hook-interval=10s`, `update-status` fires every 10s per unit; no charm observes it, so it's a no-op but still incurs hook overhead (24 hooks/min across 4 units at that test interval). Not a concern at the 5m default.

**Process kill recovery**: SIGKILL to `airflow api-server`, `airflow triggerer`, and `airflow scheduler` processes all resulted in Pebble auto-restarting the process within seconds; charm status stayed `Active` throughout with no hook firing (Pebble handled it internally).

**Relation removal**: removing `airflow-coordinator` from scheduler, api-server, or triggerer individually produces the same cascade: the affected charm goes Blocked "Missing airflow-coordinator relation", the coordinator goes Blocked "Missing integrations with: `<charm>`", and the remaining core charms go Waiting "Waiting for relation data from coordinator". Re-integrating restored all to Active within 15–60s across trials.

**Bad config values**: `core_default_timezone="Invalid/Timezone"` (and `"Not/A/Timezone"` on a repeat run) → coordinator Blocked "Invalid value for `core_default_timezone` config"; core charms stayed Active on old config. `core_parallelism=-1`/`-5` → coordinator correctly Blocked "Invalid value for `core_parallelism` config" on repeat testing (an earlier run in this review incorrectly reported these values were silently accepted — that observation was wrong and is corrected here). In all cases, fixing the value restored Active immediately.

**Invalid fernet key secret**: pointing the coordinator at a secret with `fernet-key="this-is-not-a-valid-fernet-key"` → coordinator Blocked "Fernet key secret not valid"; core charms stayed Active on old config; restoring a valid secret recovered immediately. Correct behaviour — the coordinator validates the key before distributing it.

**Scale**: scheduler scaled 1→3→1 successfully, all 3 units reaching Active (health endpoint reports a single heartbeat from whichever replica last reported). API server scaled 1→3→1 successfully, each new unit reaching Active within ~30–90s; scale-down completed cleanly.

**Ingress (Traefik)**: requests routed via LoadBalancer IP `10.43.45.0` to the API server at path `/rv-airflow-deep-airflow-api-server-k8s`; health endpoint `https://10.43.45.0/rv-airflow-deep-airflow-api-server-k8s/api/v2/monitor/health` returned all components healthy; HTTP redirected to HTTPS (301). Traefik's status showed "Certificate not available yet" throughout despite the `self-signed-certificates:certificates → traefik-k8s:certificates` relation being present — Traefik kept serving its fallback default cert (confirmed via `openssl s_client`). This is a Traefik/self-signed-certificates integration issue, not an Airflow charm bug, but it means TLS for the Airflow UI does not work with this combination as tested.

**Pebble services**: all four charms run as `ubuntu:ubuntu`, startup `enabled`, with correct component-specific commands (`airflow api-server`, `airflow scheduler`, `airflow triggerer`, `airflow dag-processor`). Config file `/opt/airflow/airflow.cfg` owned by `ubuntu:ubuntu` on all charms.

**Juju 4.x relation-detection bug (root-caused)**: after integrating the coordinator with all four core charms on Juju 4.x, the core charms remained stuck at Blocked "Missing airflow-coordinator relation" for 10+ minutes. `juju status --relations` and `juju show-unit` confirmed the relations and their data (`airflow-version`, `component`, `workload-image-hash`) were present; `show-status-log` confirmed `relation-created`, `relation-joined`, and two `relation-changed` hooks all fired, and `debug-log` showed `pebble-check-failed` firing shortly after `pebble_ready` and before the relation hooks — but nothing updated the status. Traced to the library: `AirflowCoordinatorCoreRequires._no_relation_events()` and `_relation_events()` both drop `relation_joined` from the base class's event list, so the reconciler is never invoked by the relation being (re)established. A pod restart re-runs `__init__` with the relation already present, which is why it recovers.

**What could not be seen from code alone**: coordinator config propagation timing (~30s per change); Pebble auto-restart-on-kill behaviour; the cross-component status cascade on relation removal; idle memory footprint per workload; that Traefik's cert issue persists despite the certificates relation being present; that the coordinator validates fernet key and negative `core_parallelism`; that the Juju 4.x relation bug is 100% reproducible and shares its root cause with the intermittent Juju 3.6 failures; that a pod restart is an effective workaround; that re-adding a relation after removal also gets stuck (because `_relation_events` also lacks `relation_joined`); that new units from `juju scale-application` while a relation already exists initialize correctly; that non-ingress charms expose irrelevant Traefik config via a vendored library's auto-registration.

## Findings

### `AirflowCoordinatorCoreRequires` drops `relation_joined` from event observation — charms permanently blind to new relations
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/airflow_coordinator_k8s/v0/airflow_coordinator.py:877-878` (`_no_relation_events` override) and `:899-905` (`_relation_events` override), duplicated identically in all four charms
- **Evidence**: The base `AirflowCoordinatorRequires._no_relation_events()` (`:808-813`) returns `[relation_joined, relation_broken]`. `AirflowCoordinatorCoreRequires`'s override at `:877-878` drops `relation_joined`, returning only `[relation_broken]`. The same drop happens in `_relation_events()` (`:899-905`). Event logs from three separate deploys (two Juju 4.x, one Juju 3.6) confirm: after `pebble_ready` sets Blocked "Missing airflow-coordinator relation", the subsequent `relation-created`, `relation-joined`, and `relation-changed` hooks all execute but none trigger reconciliation. Relation data is confirmed flowing (`juju show-unit` shows `airflow-version`, `component`, `workload-image-hash` populated).
- **Impact**: On Juju 4.x the charms are 100% non-functional — integration never triggers reconciliation. On Juju 3.6 the same bug is systematic but masked by event-ordering timing; one deploy saw all 4 core charms stuck simultaneously, requiring a manual pod delete to recover. Even after recovery, removing and re-adding a relation reproduces the stuck state because `_relation_events` also lacks `relation_joined`. The `airflow_config_available` event only fires once the provider publishes config — if the coordinator itself can't configure yet (missing fernet key, no database), the core charms have no other signal that the relation exists.
- **Fix**: Add `self._charm.on[self._relation_name].relation_joined` back to both `_no_relation_events()` and `_relation_events()` in `AirflowCoordinatorCoreRequires`. Also observe `pebble-check-failed` and call `_reconcile` on it, since it fires between `pebble_ready` and the relation hooks and currently goes unhandled — this would provide a recovery path even without the `relation_joined` fix.
- **Linter rule**: "Override changes event observation set from base class" — mechanically checkable by diffing event lists between subclass overrides and the base class.

### Hard-coded Airflow version and image hash make consistency checks inert
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/airflow_coordinator_k8s/v0/airflow_coordinator.py:881-884` (all four charms)
- **Evidence**:
```python
# TODO: pull airflow_version and workload_image_hash from container
# after https://github.com/canonical/airflow-rocks/issues/13 is resolved
airflow_version = "3.1.0"
workload_image_hash = "somehash"
```
- **Impact**: Every core charm reports the same fake version and hash. The coordinator's `are_airflow_versions_consistent` and `are_workload_image_hashes_consistent` checks can never detect real inconsistencies, so mismatched image revisions or Airflow versions could be deployed together undetected, risking metadata-database corruption or silent failures. `INCONSISTENT_AIRFLOW_VERSION` and `INCONSISTENT_WORKLOAD_IMAGE_HASH` are effectively dead validation codes.
- **Fix**: Resolve canonical/airflow-rocks#13 and pull the real version/hash from the workload container or resource metadata.
- **Linter rule**: not mechanically checkable — requires understanding that a hard-coded literal feeds a consistency check.

### `ExitWithStatusError` duplicated across all four charms
- **Severity**: medium
- **Kind**: lint
- **Where**: `charms/api-server/src/charm.py:22`, `charms/scheduler/src/charm.py:21`, `charms/triggerer/src/charm.py:17`, `charms/dag-processor/src/charm.py:17`
- **Evidence**: Four near-identical copies of:
```python
class ExitWithStatusError(Exception):
    """Exception raised to exit with a specific status."""
    def __init__(self, msg: str, status_type):
        super().__init__(str(msg))
        self.msg = str(msg)
        self.status_type = status_type
    @property
    def status(self):
        return self.status_type(self.msg)
```
The scheduler's copy carries a `# TODO: abstract this to a diff module so all charms in this repo can use it`.
- **Impact**: Any change to this class must be made in four places and can drift.
- **Fix**: Move to a shared module (e.g. `lib/charms/airflow_core/`) and import it from all four charms.
- **Linter rule**: identical class definitions across `charms/*/src/charm.py` — mechanically checkable with AST diffing.

### No actions defined on any charm
- **Severity**: medium
- **Kind**: ux
- **Where**: all four charms (no `@ops.Action` / action metadata anywhere)
- **Evidence**: `juju actions airflow-api-server-k8s` (and scheduler, triggerer, dag-processor) returns "No actions defined".
- **Impact**: Operators have no Juju-native way to trigger `restart`, `check-db-connectivity`, `reserialize-dags`, or `rotate-fernet-key`; they must `juju ssh` and run `airflow` CLI commands manually. The integration tests already script `airflow dags reserialize` and `airflow db check` this way — these are clear action candidates.
- **Fix**: Add at minimum a `restart` action and a `health-check` action.
- **Linter rule**: "charm has no actions defined" — mechanically checkable.

### `pebble-check-failed` event is unhandled, compounding the `relation_joined` gap
- **Severity**: medium
- **Kind**: bug
- **Where**: all four charms (no observation of `pebble-check-failed`)
- **Evidence**: event logs across multiple deploys show `pebble-check-failed` firing between `pebble-ready` and the relation hooks (e.g. Juju 4.x: `pebble-ready` 13:40:51, `pebble-check-failed` 13:41:16, relation hooks from 13:42:11; Juju 3.6: `pebble-ready` 13:26:03, `pebble-check-failed` 13:26:28, relation hooks from 13:26:31). No handler, log entry, or status change results from it in any charm.
- **Impact**: it's a missed opportunity for a safety-net reconciliation trigger on Pebble reconnect, which would help even without the `relation_joined` fix, since a re-run of `_reconcile` would find `model.get_relation()` non-None and pass the required-relations check.
- **Fix**: observe `self.on[constants.CONTAINER_NAME].pebble_check_failed` and call `_reconcile`.
- **Linter rule**: not mechanically checkable.

### Scheduler, Triggerer, and DAG Processor inherit `IngressPerAppRequirer` config options despite not using ingress
- **Severity**: low
- **Kind**: bug
- **Where**: `charms/scheduler/src/charm.py`, `charms/triggerer/src/charm.py`, `charms/dag-processor/src/charm.py`
- **Evidence**: `juju config airflow-scheduler-k8s` lists 14 options (`juju-application-path`, `juju-external-hostname`, `kubernetes-ingress-allow-http`, `kubernetes-service-type`, etc.) sourced from `traefik_k8s.v2.ingress.IngressPerAppRequirer`, though the scheduler charm neither imports nor instantiates that class. The `juju config` output is identical across all four core charms except the API server, which legitimately uses ingress.
- **Impact**: operators see irrelevant config options; setting e.g. `juju-external-hostname` on the scheduler silently does nothing since the charm never observes it.
- **Fix**: identify the vendored library that auto-registers this config at import time and restrict it to the API server charm.
- **Linter rule**: "config key from library X present but charm doesn't import X" — mechanically checkable by comparing `charmcraft.yaml` config against imports.

### TLS CA chain write path untested in all four charms
- **Severity**: low
- **Kind**: test-gap
- **Where**: `_reconcile`'s `can_write_tls_ca_chain` / `write_tls_ca_chains` branch in all four charms
- **Evidence**: coverage reports show these lines uncovered (API server ~314, scheduler ~264, triggerer ~167, dag-processor ~167). No scenario test sets `tls_ca_chains` on the coordinator relation.
- **Impact**: TLS CA chain handling writes security-sensitive files to the workload container; without coverage, regressions (wrong permissions, broken diffing) won't be caught.
- **Fix**: add scenario tests that populate `tls_ca_chains` and assert the correct files land with correct contents and ownership.
- **Linter rule**: coverage gap on a TLS-related path — not mechanically checkable without coverage + semantic tagging.

### `can_write_airflow_config` accesses `provider_content` attributes without a None guard before `all()`
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/airflow_coordinator_k8s/v0/airflow_coordinator.py:953-957` (all four charms)
- **Evidence**:
```python
return all(
    condition
    for condition in [
        self._ready,
        self._requirer_handler.provider_content,           # may be None
        self._requirer_handler.provider_content.config_template,  # AttributeError if None
        self._requirer_handler.provider_content.sensitive_data,   # AttributeError if None
    ]
)
```
- **Impact**: the list is fully evaluated before `all()` sees it, so if `provider_content` is `None` (its declared type is `Optional[...]`), the next line raises `AttributeError` before `all()` can short-circuit. Currently masked because `data_interfaces` appears to always return a model with default fields rather than `None`, but nothing guarantees this.
- **Fix**: extract to a variable first: `content = self._requirer_handler.provider_content; return self._ready and content and content.config_template and content.sensitive_data`.
- **Linter rule**: "property access on Optional type without None guard inside a list literal preceding `all()`" — catchable with pyright strict mode.

### `_stop_service_and_remove_config` swallows the original Pebble exception in 3 of 4 charms
- **Severity**: low
- **Kind**: bug
- **Where**: `charms/api-server/src/charm.py:83-93`, `charms/triggerer/src/charm.py:38-48`, `charms/dag-processor/src/charm.py:38-48`
- **Evidence**:
```python
def _stop_service_and_remove_config(self) -> None:
    try:
        self._container.stop(constants.SERVICE_NAME)
    except ops.pebble.APIError:
        raise ExitWithStatusError(
            "Failed to stop pebble service",
            ops.BlockedStatus,
        )
```
- **Impact**: the original `APIError` (with the real Pebble error message, status code, body) is discarded, so the operator sees only "Failed to stop pebble service" with no diagnostic detail. The scheduler's equivalent correctly chains with `raise ... from e`.
- **Fix**: use `raise ExitWithStatusError(...) from e` (as the scheduler does), or include `str(e)` in the message.
- **Linter rule**: "bare `raise NewException` in `except` block without `from e`" — mechanically checkable with AST.

### Scheduler writes the Kubernetes executor pod spec before checking config writability
- **Severity**: low
- **Kind**: bug
- **Where**: `charms/scheduler/src/charm.py:234` (`_reconcile`)
- **Evidence**:
```python
def _reconcile(self, _) -> None:
    try:
        self._check_container_can_connect()
        self._check_required_relation_and_act()
        self._write_kubernetes_executor_pod_spec()   # before the can_write check
        if not self._config_requires.can_write_airflow_config:
            raise ExitWithStatusError("Waiting for relation data", ops.WaitingStatus)
```
- **Impact**: `_write_kubernetes_executor_pod_spec` internally checks `can_write_kubernetes_executor_pod_spec` (gated on `self._ready`), so this is currently a safe no-op, but the ordering is logically backwards — the spec write should happen only after coordinator config availability is confirmed. If `_ready` is ever relaxed independently of the config check, this ordering would let a pod spec write happen before config is guaranteed.
- **Fix**: move `_write_kubernetes_executor_pod_spec()` and `_remove_stale_kubernetes_executor_pod_spec()` to after the `can_write_airflow_config` check, alongside the TLS CA chain writes.
- **Linter rule**: not mechanically checkable.

### `codespell` misspelling in library docstring, duplicated 4×
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/airflow_coordinator_k8s/v0/airflow_coordinator.py:93` (all four charms)
- **Evidence**: `prerequisities` → should be `prerequisites`. Confirmed with `codespell` run across `src/` and `lib/`.
- **Impact**: minor doc-quality issue, quadrupled because the library is vendored per charm.
- **Fix**: fix in one copy and re-sync; bump `LIBPATCH`.
- **Linter rule**: already caught by `codespell`; verify CI lint covers `lib/`.

### Inconsistent method naming across charms
- **Severity**: nit
- **Kind**: lint
- **Where**: various charm files
- **Evidence**: the same Pebble-connection check is `_check_pebble_connection` in api-server/triggerer/dag-processor but `_check_container_can_connect` in scheduler; the relation check is `_check_required_relations` vs `_check_required_relation_and_act`; the stop routine is `_stop_service_and_remove_config` vs the split `_stop_service` + `_cleanup_airflow_home_contents`.
- **Impact**: makes it harder to see that all four charms share the same pattern.
- **Fix**: abstract the shared `_reconcile` flow into a common base class.
- **Linter rule**: not mechanically checkable without a reference model.

### Charm-level `tox.ini`/`pyproject.toml` files pin different ops/scenario versions
- **Severity**: low
- **Kind**: lint
- **Where**: `charms/*/tox.ini`, `charms/*/pyproject.toml`
- **Evidence**: api-server pins ops 3.8.1 + scenario per pyproject; scheduler downgrades to ops 3.0.0 + ops-scenario 8.0.0; triggerer uses ops 3.0.0; dag-processor uses ops 3.4.0 + ops-scenario 8.4.0. Running `pytest` outside `tox` fails with `_JujuContext` import errors due to globally-installed incompatible packages.
- **Impact**: contributors bypassing tox hit confusing import errors; no enforced consistency across charms in the same repo.
- **Fix**: consolidate to a shared root `pyproject.toml` dependency group, or at minimum align ops versions.
- **Linter rule**: "dependency version mismatch across charms in same repo" — mechanically checkable with a script.

### `ruff check` finds 26 issues in integration tests
- **Severity**: low
- **Kind**: lint
- **Where**: `tests/integration/conftest.py`, `test_charms.py`, `test_functional.py`, `test_dag_execution.py`, `test_ingress.py`, `helpers/airflow_helpers.py`, `helpers/constants.py`
- **Evidence**: `ruff check charms/*/src/` is fully clean; `ruff check charms/ tests/` reports 26 issues: import-ordering (`I001`) in 5 files, `PLR0402` in 6 files, `RUF015` in `helpers/constants.py:33`, and `DTZ001` (naive datetime) in a test DAG. The vendored `data_platform_libs` also carries `C901` complexity warnings in 12 spots, but that's third-party code.
- **Impact**: none block functionality; makes integration tests harder to read.
- **Fix**: `ruff check --fix` for the auto-fixable ones; manual fix for `RUF015`/`DTZ001`.
- **Linter rule**: already caught by `ruff`.

### `pyright` type mismatch in api-server Pebble layer construction
- **Severity**: low
- **Kind**: lint
- **Where**: `charms/api-server/src/charm.py:179`
- **Evidence**: `pyright` reports `Type "dict[str, dict[str, dict[Unknown, Unknown]]]" is not assignable to declared type "LayerDict"`.
- **Impact**: minor type-safety gap; no runtime effect since Pebble accepts plain dicts.
- **Fix**: add explicit annotations to the inner dicts, or build the layer with `ops.pebble.Layer` instead of raw dicts.
- **Linter rule**: already caught by `pyright`.

### `charmcraft analyse` can't find the entrypoint with the `uv` plugin
- **Severity**: nit
- **Kind**: lint
- **Where**: `charms/api-server/charmcraft.yaml` (all four)
- **Evidence**: `charmcraft analyse` reports "Cannot find the entrypoint file" and "framework: not based on any known Framework" because `plugin: uv` isn't recognised by the tool.
- **Impact**: confusing tool output for anyone running `charmcraft analyse`; no deployment impact.
- **Fix**: tool limitation, no charm-side fix available.
- **Linter rule**: not established.

### DAG Processor README has a copy-paste error and hyphenation typo
- **Severity**: low
- **Kind**: docs
- **Where**: `charms/dag-processor/README.md`
- **Evidence**: title line reads `# airflow-dag processor` (space instead of hyphen); overview says "The Airflow API Server charm:" instead of naming the DAG Processor; usage section has `juju deploy airflow-dag processor-k8s` (space) instead of `airflow-dag-processor-k8s`; status section references "API server" instead of "DAG Processor".
- **Impact**: an operator copy-pasting the deploy command gets a "charm not found" error; the wrong overview text confuses readers about which component this is.
- **Fix**: correct "API Server" → "DAG Processor" and fix the hyphenation in all three locations.
- **Linter rule**: "charm name in README doesn't match `charmcraft.yaml` name" — mechanically checkable with regex.

### Root README is a one-liner
- **Severity**: low
- **Kind**: docs
- **Where**: `README.md` (repo root)
- **Evidence**: full contents: `# airflow-core-operators\nMono-repo for Airflow Core Charms`.
- **Impact**: no description of the full deployment topology, the coordinator dependency, or DAG storage setup — a new operator has no guidance beyond individual charm READMEs.
- **Fix**: add a root README with a deployment diagram, quick-start, and links to each charm's README plus external docs.
- **Linter rule**: not mechanically checkable.

### Config-change detection re-renders and re-pulls the config file on every hook
- **Severity**: low
- **Kind**: performance
- **Where**: `lib/charms/airflow_coordinator_k8s/v0/airflow_coordinator.py` — `airflow_config_needs_update`
- **Evidence**:
```python
def airflow_config_needs_update(self, config_path: str) -> bool:
    provider_content = self._requirer_handler.provider_content
    rendered_config = jinja2.Template(provider_content.config_template).render(
        **json.loads(provider_content.sensitive_data)
    )
    if self._workload_container.exists(config_path):
        on_disk_config = self._workload_container.pull(config_path).read()
    else:
        on_disk_config = None
    return on_disk_config != rendered_config
```
- **Impact**: every config-related hook pulls the full rendered config from the container and re-renders the template to compare. Negligible for the current ~930-byte file, but the pattern wouldn't scale if the config grew. `webserver_config_needs_update` and `write_tls_ca_chains` share it.
- **Fix**: store a hash/checksum of the last written config (locally or in a peer relation) and compare against that instead of pulling the file each time.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Reconciler pattern without `defer()`**: a single `_reconcile(event)` recomputes desired state from current inputs every time, eliminating ordering bugs and missed-event risk. `charms/api-server/src/charm.py:277-295`.
- **Config-change detection before restart**: `airflow_config_needs_update` and `webserver_config_needs_update` compare rendered content against on-disk content before rewriting, avoiding unnecessary restarts.
- **TLS CA chain handling with per-file diffing**: `write_tls_ca_chains` only rewrites files whose contents actually differ. `lib/charms/airflow_coordinator_k8s/v0/airflow_coordinator.py:1070-1090`.
- **Clear, actionable status messages**: every blocked/waiting status is specific and actionable ("Missing airflow-coordinator relation", "Fernet key secret not valid", "Invalid value for `core_default_timezone` config"); no bare `BlockedStatus()`/`WaitingStatus()` was observed.
- **Scenario test coverage of error paths**: API server tests cover Pebble disconnection, missing relation, config/webserver-config write failure, config removal failure, and ingress path changes — 32 tests with explicit status assertions.
- **Inline leadership guards in library code**: the `airflow_api_server` and `airflow_coordinator` libraries check `self._charm.unit.is_leader()` before writing relation data. `lib/charms/airflow_api_server_k8s/v0/airflow_api_server.py:94`.
- **Consistent container naming**: containers are named for the component (`airflow-api-server`, etc.), avoiding the common `workload` anti-pattern.

## Common-practice notes

**Follows**: mono-repo layout with per-charm `charmcraft.yaml`, `src/charm.py`, `tests/scenario/`; `uv` plugin for building; `data_interfaces` v1 with pydantic models for relation data; `jinja2` for config templating shared with the coordinator.

**Drifts**: the `ExitWithStatusError`-based status pattern is unusual (most charms set `self.unit.status` directly) — cleaner for a reconciler but less familiar. Use of `ops.testing.Context` (scenario) rather than `Harness` is ahead of the ecosystem curve. The scheduler's split `_stop_service` + `_cleanup_airflow_home_contents` diverges from the other three charms' combined method, suggesting organic drift over time.

**Leads**: the no-`defer()` reconciler pattern combined with exception-based status setting is a strong example for the ecosystem. Integration tests use `jubilant` rather than `pytest-operator`, with real DAG execution and scaling tests. The coordinator's config validation (timezone, fernet key) gives clear, actionable blocked states rather than generic errors.

## Tests

**Unit tests (scenario)** — all passing:
- API server: 32 tests, 92% overall coverage, 94% on `src/charm.py`.
- Scheduler: 16 tests, 95% coverage on `src/charm.py`.
- Triggerer: 12 tests, 91% coverage on `src/charm.py`.
- DAG Processor: 11 tests, 91% coverage on `src/charm.py`.

**Integration tests** (read but not run — require self-hosted-runner CI environment):
- `test_charms.py` (5 tests): Pebble service checks, config file existence/ownership, API health endpoint, config CLI validation, relation-removal status checks, database-unavailable behaviour.
- `test_functional.py` (4 tests): config propagation on coordinator changes, database connectivity, config-change propagation + DAG reserialization, scheduler scaling (1→3→1).
- `test_dag_execution.py`: DAG file injection, discovery, execution.
- `test_ingress.py` (2 tests): HTTP/HTTPS health checks through Traefik.
- These are genuine behaviour assertions — they read config files, hit API endpoints, verify Pebble services, check file ownership, and trigger DAG runs.

**CI**: GitHub Actions (`tests.yaml`) runs lib-check, lint, unit-tests, and integration-tests on PRs; integration tests use self-hosted runners with `concierge prepare -p k8s`.

**Coverage gaps relative to findings**:
- No scenario test for `_stop_service_and_remove_config` when `container.exists()` raises `ConnectionError` (only the `stop`-raises-`APIError` path is tested).
- No scenario test for `_handle_ingress` clearing the path when the relation becomes unready.
- No scenario test for `can_write_tls_ca_chain` / `write_tls_ca_chains`.
- No integration test for charm upgrade/refresh.
- No integration test on Juju 4.x (would have caught the relation-detection bug).
- No test injecting invalid config values and asserting the coordinator blocks.
- `test_charm_statuses_on_missing_relation` only removes the scheduler relation, not api-server's or dag-processor's individually.
- No test for the invalid-fernet-key scenario (coordinator-side, not in this repo).

## Docs

Per-charm READMEs give an overview, a `juju deploy`/`juju integrate` usage example, and status behaviour; the scheduler's additionally documents the OCI image. Issues found: the DAG Processor README's copy-paste/hyphenation errors (see Findings); the root README is a one-liner with no topology or quick-start. Charmhub summaries in `charmcraft.yaml` are reasonable but missing contact/issue/source links. Each charm has a `terraform/` module (thin `juju_application` wrapper) with a well-written, table-and-example README.

**Would a new operator succeed?** Mostly, if they already know the topology. Missing: the fernet key secret requirement (only discoverable by seeing the coordinator blocked), the full postgresql+pgbouncer+coordinator+4-charm topology, DAG storage configuration (git-sync/S3), how to reach the UI via ingress, upgrade procedure, and TLS setup for the web UI (which didn't work in this review's testing).

## Open questions

1. **Does the coordinator charm belong in this repo?** It's the only charm that *provides* `airflow-coordinator`, and the core charms are useless without it; keeping it separate means cross-repo PRs for coordinated library changes. Depends on team repo strategy.
2. ~~**Why does `model.get_relation()` appear to return `None` on Juju 4.x?**~~ **SETTLED**: it doesn't — `model.get_relation()` returns correctly on both Juju versions. The bug is that `_no_relation_events()` drops `relation_joined`, so no event triggers the reconciler when the relation is created after `pebble_ready`. Confirmed via event-log tracing, library code, and pod-restart recovery.
3. **Why is the coordinator's "Waiting for fernet key" logged at ERROR level?** Observed: `ERROR unit.airflow-coordinator-k8s/0.juju-log Waiting for fernet key secret configuration` — a normal waiting condition, not an error. Needs a look at the coordinator charm's logging calls (not in this repo).
4. **Are the core charms testable in isolation without the coordinator?** Integration tests always deploy the full stack; there's no test that feeds a core charm invalid/partial coordinator config directly. Settled by adding a mocked-relation test.
5. **Is the Traefik TLS issue a Traefik charm bug or a config gap?** `self-signed-certificates` was integrated but Traefik kept serving its default cert. Settled by testing a different TLS provider or reviewing Traefik's expectations for the certificates relation.
6. **Why did the fernet key secret fail with "Fernet key secret not valid" in one run?** Possibly `secret-get --label fernet-key` behaving differently on Juju 3.6.25; the key itself was valid (generated via `cryptography.fernet.Fernet.generate_key()`). Unverified — would need to check the coordinator's secret-retrieval code (not in this repo).
</content>
