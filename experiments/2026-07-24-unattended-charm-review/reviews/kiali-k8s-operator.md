# kiali-k8s-operator

A thin, well-structured k8s charm wrapping the official Kiali rock, integrating with the COS stack via seven relations (`prometheus-api`, `istio-metadata`, `grafana-metadata`, `tempo-api`, `ingress`, `logging`, `service-mesh`). The reconcile pattern built on `StatusManager` is clean and worth copying. However, the charm was never observed reaching Active in this review: the test cluster's admission policy blocked `istio-k8s`'s CRD install, and separately `prometheus-k8s` established a relation but published no `prometheus-api` data — either blocker alone would keep kiali permanently Blocked. Two real bugs were confirmed by reading the code (a missing `raise` that turns a Waiting condition into a misleading Blocked one, and a dead exception handler that always evaluates true). A third, higher-severity claim about a unit-test topology bug in the tempo-datasource-exchange flow is contradicted by the reviewer's own follow-up analysis in the notes and should be treated as unresolved. A maintainer should first fix the missing `raise` (one-line fix, currently masks real Waiting conditions as Blocked), then get a real end-to-end deployment (working istio + prometheus publishing data) to confirm the pebble-layer/config-path interaction, which is unverified in Active state.

| | |
|---|---|
| Repo | canonical/kiali-k8s-operator @ `1e46c3b` (2026-07-17) |
| Charms | kiali-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4, channel 2/edge rev 13 (local HEAD matches rev 13); never reached Active (istio-k8s CRD admission error, then empty `prometheus-api` data) |
| Reviewed | 2026-08-21 |

## What it does

Deploys the Kiali service mesh dashboard as a k8s workload container, wiring it to required relations (Prometheus for metrics source, Istio for namespace info) and optional relations (Grafana for deep-dive links, Tempo for distributed tracing, Traefik ingress). When relations are complete, the charm generates a Kiali config from relation data, pushes it to the container, and manages the Pebble service. Exposes its own `/metrics` endpoint via `metrics-endpoint` provide, and a tempo datasource via `tempo-datasource-exchange`.

## Deployment log

```bash
# Created model
juju add-model rv-kiali-k8s --controller concierge-k8s-4

# Deployed kiali-k8s alone — immediately blocked as expected
juju deploy kiali-k8s --channel 2/edge --trust --model rv-kiali-k8s
# → blocked: "Missing required relation to prometheus provider"

# Deployed integrations
juju deploy istio-k8s --channel 2/edge --trust --model rv-kiali-k8s
juju deploy prometheus-k8s --channel 2/edge --trust --model rv-kiali-k8s
juju deploy istio-ingress-k8s --channel 2/edge --trust --model rv-kiali-k8s

# Related everything
juju relate istio-k8s prometheus-k8s
juju relate kiali-k8s:prometheus-api prometheus-k8s
juju relate kiali-k8s:istio-metadata istio-k8s
juju relate istio-ingress-k8s:ingress kiali-k8s:ingress
```

`istio-k8s` entered error state: `leader-elected` hook failed with `customresourcedefinitions.apiextensions.k8s.io "gatewayclasses.gateway.networking.k8s.io" is forbidden: ValidatingAdmissionPolicy "safe-upgrades.gateway.networking.k8s.io" ... denied request: Installing CRDs with version before v1.5.0 is prohibited by default`. This is a cluster-level admission policy blocking old CRD versions — an environment issue, not a kiali bug. `istio-metadata` relation data never became available. Kiali correctly stayed **Blocked** with the right message throughout. `prometheus-k8s` became Active. The kiali unit never left Blocked because the required Istio data was never published.

```bash
$ kubectl top pod -n rv-kiali-k8s
NAME                CPU(cores)  MEMORY(bytes)
kiali-k8s-0         1m          34Mi      ← charm + workload combined
```

34 MB memory, ~1m CPU — very lean when idle. The Pebble service is correctly `inactive` (stopped) because there is no valid config without Istio data. The rock's default config at `/etc/kiali/kiali-local-config.yaml` is present (owned root:root, mode 0664).

### Additional deployment steps (later session)

```bash
# Added grafana-k8s and related to kiali
juju deploy grafana-k8s --channel 2/edge --trust --model rv-kiali-k8s
juju relate kiali-k8s:grafana-metadata grafana-k8s
# → grafana-k8s: active (oscillating with upgrade-charm errors, recovers), kiali stays Blocked

# Added tempo-coordinator-k8s and related tempo-api
juju deploy tempo-coordinator-k8s --channel 2/edge --trust --model rv-kiali-k8s
juju relate kiali-k8s:tempo-api tempo-coordinator-k8s
# → tempo-coordinator-k8s: maintenance (setting up), kiali stays Blocked

# Added loki-k8s and related logging
juju deploy loki-k8s --channel 2/edge --trust --model rv-kiali-k8s
juju relate kiali-k8s loki-k8s
# → loki-k8s: active, kiali logging configured via pebble log-targets

# Scale up kiali to 2 units
juju scale-application kiali-k8s 2
# → both units Blocked "Cannot configure Kiali - no related istio available"
# → kiali-k8s/1 briefly showed "Missing required relation to istio provider" during drain

# Removed prometheus relation while running
juju remove-relation kiali-k8s:prometheus-api prometheus-k8s
# → prometheus-api-relation-departed → prometheus-api-relation-broken (both clean)
# → kiali goes Blocked "Missing required relation to prometheus provider"

# Re-related prometheus
juju relate kiali-k8s:prometheus-api prometheus-k8s
# → prometheus-api-relation-created → istio-metadata-relation-created
# → kiali still Blocked "Missing required relation to prometheus provider" ← prometheus not publishing data

# Scale back down to 0 (remove all units)
juju scale-application kiali-k8s 0
# → all units terminated cleanly

# Remove application
juju remove-application --force kiali-k8s
# Requires interactive y/N confirmation; in automated context use `yes | juju remove-application`
```

## Observed behaviour

- **Install time**: ~3 min from deploy to pod Running (including image pull of 77 MB kiali rock).
- **Block on missing relations**: correct `BlockedStatus` at every stage, with specific messages per missing relation.
- **Stopping on incomplete config**: when `kiali_config` is `None` (no Istio data), `_configure_kiali_workload` correctly stops the service rather than starting it with garbage config.
- **Hook churn**: `relation-changed` fires twice for prometheus (joined + changed), once for istio — no extra spurious hooks observed.
- **`StatusManager` context**: all relation fetches are inside `with status_manager:` blocks; exceptions are caught and the worst status is set at the end of reconcile — clean pattern.
- **`No Loki endpoints available` warning**: appears on every reconcile while the `logging` relation is not connected. Harmless but noisy.
- **Ingress relation**: `istio-ingress-k8s` was in error state from deployment, so the ingress relation was never established and no ingress data was published to kiali. The `_prefix` property therefore always returned `"/"` (the default) throughout this review. `IngressPerAppRequirer` observes `ready` and `revoked` events but neither was triggered.
- **Pebble plan mismatch**: the running container's pebble plan only ever showed the rock's layer (`command: /opt/kiali/kiali -config /etc/kiali/kiali-local-config.yaml`), never the charm's layer (`/kiali-configuration/config.yaml`), because the charm never called `add_layer` (it was always Blocked, `new_config` was always `None`). The 418 ("I'm a teapot") response seen in container logs is Kiali's own default-config response. Whether the charm's layer correctly overrides the rock's when the charm reaches Active is **unresolved** — not confirmed in this review. See Finding (pebble layer / config path mismatch).
- **`update-status` hook**: fires every 5 minutes (`12:25:47`, `12:30:01`, `12:34:47`). Each run reconciles and confirms the correct Blocked status. No spurious hook executions observed.
- **Relation removal**: `juju remove-relation kiali-k8s:prometheus-api prometheus-k8s` fires `prometheus-api-relation-departed` → `prometheus-api-relation-broken`, both clean. kiali goes Blocked "Missing required relation to prometheus provider" — correct.
- **Relation re-establishment**: re-relating prometheus fires `config-changed` → `prometheus-api-relation-created` → `-joined` → `-changed`. Status message updates depending on which check runs first in reconcile order.
- **Grafana optional relation**: adding `grafana-k8s` and relating `kiali-k8s:grafana-metadata` fires the standard created/joined/changed sequence. The charm logs "Grafana integration disabled - no grafana relation found" on the first reconcile, then `GrafanaMissingError` is caught and the grafana branch is skipped gracefully. `grafana-k8s` becomes Active but publishes no `grafana-metadata` data (`application-data: {}` via `juju show-unit`); kiali handles this correctly via `WaitingStatusError`.
- **Tempo-api optional relation**: adding `tempo-coordinator-k8s` and relating `kiali-k8s:tempo-api` fires `-created` → `-joined`. `tempo-coordinator-k8s` enters maintenance (bootstrap), no data published yet. `_get_tempo_api` raises `WaitingStatusError("Waiting on related tempo application's metadata")`, correctly caught as Waiting.
- **Loki logging integration**: after establishing the `loki-k8s` relation, pebble log-targets are correctly configured:
  ```
  log-targets:
      loki-k8s/0:
          type: loki
          location: http://loki-k8s-0.loki-k8s-endpoints.rv-kiali-k8s.svc.cluster.local:3100/loki/api/v1/push
          services:
              - all
  ```
  Hooks fire correctly (`logging-relation-created` → `-joined` → `-changed`). The "No Loki endpoints available" warning is emitted during the reconcile before loki-k8s becomes active and publishes its endpoint.
- **Config change**: `juju config kiali-k8s view-only-mode=false` fires `config-changed`; charm correctly stays Blocked because istio is still in error. Juju rejects non-boolean values before they reach the charm.
- **Scale lifecycle**: scaling 1→2 creates both units Blocked. Scaling to 0 drains cleanly; the draining unit briefly showed "Missing required relation to istio provider" before termination.
- **Container kill**: `kill 1` inside the kiali container causes a pod restart (1 restart observed). After restart, the charm fires `kiali-pebble-ready` → reconcile → returns to Blocked. Pebble service stays `inactive`. Recovery is clean.
- **Workload binary location**: rock's kiali binary at `/opt/kiali/kiali`; container has no `curl`/`wget`. Pebble layer command references the binary correctly.
- **No `juju refresh` path**: channel 2/edge has only revision 13 — no newer revision to test an upgrade.
- **No actions defined**: `juju actions kiali-k8s` returns "No actions defined for kiali-k8s".
- **TLS integration**: `juju relate kiali-k8s self-signed-certificates` correctly rejected at the Juju layer ("no compatible endpoints found"); charm has no `tls-certificates` requirer.
- **grafana-k8s oscillating error/recovery**: `grafana-k8s` enters error ("hook failed: 'upgrade-charm'") roughly every 3 minutes, then recovers to Active. Consistent, does not affect kiali's behaviour. Likely a grafana-k8s rev 180 issue, unrelated to kiali (unverified — not confirmed against grafana-k8s's own tracker).
- **`prometheus-api` relation data is empty**: even after `prometheus-k8s` is Active and the relation is established, `juju show-unit prometheus-k8s/0` shows `application-data: {}` on the `prometheus-api` endpoint. kiali's `PrometheusApiRequirer.get_data()` returns `None`, so kiali stays Blocked on "Missing required relation to prometheus provider" regardless of istio state. Most significant live-behaviour finding — see Findings below.
- **Unit test coverage**: 16 tests, all passing (re-run confirmed). Ruff and pyright both clean for `src/` when run with `PYTHONPATH={toxinidir}:{toxinidir}/lib:{src_path}` (matches tox). `lib/charms/` has 48 ruff issues (bundled upstream libraries).
- **Istio relation removal**: removing `kiali-k8s:istio-metadata` fires `-departed` → `-broken`; kiali correctly goes Blocked "Missing required relation to istio provider".
- **Juju CLI type validation**: `juju config kiali-k8s view-only-mode=notabool` rejected by the Juju CLI before reaching the charm.
- **`cosl` unpinned**: `pyproject.toml` declares `"cosl"` with no version constraint; `ops` and `pydantic` are also unpinned; `observability-charm-tools` is pinned to `git+main`.
- **`codespell` skips `lib/`**: the 8 bundled charm libraries are never spell-checked; ruff has no such exclusion and catches the 48 violations.
- **`grafana_source` library confirmed present**: `lib/charms/grafana_k8s/v0/grafana_source.py` exists (34,758 bytes); the `charm-libs` entry in `charmcraft.yaml` is correct.

## Findings

### Missing `raise` in `_get_tempo_datasource_uid` — Waiting condition silently becomes Blocked

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:461-462`
- **Evidence**:
  ```python
  if len(tempo_datasources) == 0:
      WaitingStatusError("Tempo datasource relation exists, but no data has been provided")
  ```
  The `raise` keyword is absent — a `WaitingStatusError` object is created and immediately discarded; execution falls through to the `grafana_uid` check or the `for` loop.
- **Impact**: When a Tempo relation exists but has not yet sent data, the charm silently continues instead of signalling Waiting. If `grafana_uid` is also `None`, it raises a misleading `BlockedStatusError("Tempo datasource relation exists, but no grafana metadata is available")`. If `grafana_uid` exists, it loops over an empty list and raises `BlockedStatusError("Tempo datasources exist, but none match the related Grafana")`. Either way, the real "waiting for Tempo data" condition is hidden and the operator sees an un-actionable Blocked message instead of Waiting. No unit test covers this exact branch.
- **Fix**: Add `raise` before `WaitingStatusError(...)`.
- **Linter rule**: not a standard rule; a custom AST check for "bare `*StatusError(...)` construction not wrapped in a `raise` statement" is mechanically checkable.

### `_is_prometheus_source_available` catches the wrong exception and is unused dead code

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:479-484`
- **Evidence**:
  ```python
  def _is_prometheus_source_available(self):
      try:
          self._get_prometheus_source_url()
          return True
      except PrometheusSourceError:   # ← wrong exception type
          return False
  ```
  `_get_prometheus_source_url()` raises `BlockedStatusError` or `WaitingStatusError`, never `PrometheusSourceError`. `PrometheusSourceError` is defined (`src/charm.py:551`) but never raised anywhere in the file. `grep -rn "_is_prometheus_source_available"` returns only the definition — no call sites.
- **Impact**: The method always returns `True` (the `except` clause is dead) and is never called. As dead code it does no harm today but misleads future maintainers who may assume it gates a real code path.
- **Fix**: Delete the method (preferred, since unused), or fix the caught exception to `except (BlockedStatusError, WaitingStatusError)` if it is meant to be used.
- **Linter rule**: "method defined but never called" and "exception handler catches a type never raised in the function" are both mechanically checkable.

### Unit test scenario for `tempo-datasource-exchange` may misconfigure relation topology (unverified)

- **Severity**: high
- **Kind**: bug / test-gap
- **Where**: `tests/unit/test_charm.py:88` (`mock_tempo_datasource_exchange()`)
- **Evidence**:
  ```python
  def mock_tempo_datasource_exchange() -> Relation:
      return Relation(
          endpoint="tempo-datasource-exchange",
          interface="grafana-datasource-exchange",
          remote_app_name="tempo",
          remote_app_data={
              "datasources": json.dumps(
                  [{"type": "tempo", "uid": "tempo-datasource-uid", "grafana_uid": GRAFANA_UID}]
              )
          },
      )
  ```
  The draft review asserts that because `tempo-datasource-exchange` is a `provides` endpoint in kiali's `charmcraft.yaml`, `scenario.Relation` should set `relation.app` to the local app (kiali), so the mock's `remote_app_name="tempo"` places data on the wrong side and masks a production bug where `DatasourceExchange.received_datasources()` would read kiali's own (empty) databag.
- **Impact (unverified)**: this claim is contradicted by the reviewer's own later analysis in the working notes, which traces the actual relation direction (`kiali:tempo-datasource-exchange → tempo:receive-datasource`) and concludes the test's topology **does** match production — tempo is the requirer of `grafana_datasource_exchange`, and the real-world failure is that `tempo-coordinator-k8s` in this environment never publishes data to `receive-datasource` (it was Blocked on "[consistency] Missing any worker relation"), which is an environment issue, not a kiali bug. Both conclusions cannot be right; this needs re-verification against the actual `DatasourceExchange` implementation and a working tempo-coordinator-k8s deployment before it can be treated as a confirmed bug.
- **Fix**: Re-derive the relation direction from `deps/cosl/interfaces/datasource_exchange.py` and `charmcraft.yaml` `provides`/`requires` blocks, then confirm with a real tempo-coordinator-k8s that is publishing datasources whether `received_datasources()` reads the correct databag.
- **Linter rule**: not mechanically checkable without resolving the relation-direction question.

### Dead peer relation `grafana` with unresolved TODO

- **Severity**: medium
- **Kind**: lint
- **Where**: `charmcraft.yaml:34-36`
- **Evidence**:
  ```yaml
  peers:
    # TODO: Can we remove this?  Required for the grafana_datasource lib, but not for features we use.
    grafana:
      interface: grafana_peers
  ```
  This peer relation exists solely to satisfy the `grafana_datasource_exchange` library's metadata requirement, not for any peer communication the charm actually performs (`grep` confirms `src/charm.py` never reads or writes it — the only "grafana" relation used is `grafana-metadata`).
- **Impact**: Confuses operators about whether the charm participates in Grafana peer gossip; dead metadata if the library requirement ever changes.
- **Fix**: Confirm with the library maintainers whether the peer relation is still required; remove it if not.
- **Linter rule**: "charm defines a peer relation never referenced in code" — mechanically checkable by cross-referencing `charmcraft.yaml` relations against `self.model.relations` usage.

### Pebble layer / config path mismatch with official rock — unverified in Active state

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:47` (constant) and rock's embedded pebble layer at `/var/lib/pebble/default/layers/001-kiali.yaml`
- **Evidence**:
  - Charm constant: `KIALI_CONFIG_PATH = Path("/kiali-configuration/config.yaml")`.
  - Charm's generated pebble layer command: `/opt/kiali/kiali -config /kiali-configuration/config.yaml` (`_generate_kiali_layer()`, ~line 303-315).
  - Rock's pebble layer command: `/opt/kiali/kiali -config /etc/kiali/kiali-local-config.yaml`.
  - Observed running pebble plan showed only the rock's layer command.
  - `/kiali-configuration/` does not exist in the deployed container; `/etc/kiali/kiali-local-config.yaml` exists with the rock's default config.
  - Because the charm was always Blocked, `_configure_kiali_workload` always received `new_config=None` and never called `add_layer` — the charm's layer was simply never added during this review, so the mismatch as observed proves nothing about behaviour in Active state.
- **Impact**: When the charm eventually reaches Active, it will call `add_layer` with `combine=True`; since both layers define the same service with `override: replace`, the later-added (charm) layer should win, and `restart()` should apply it. This is plausible but **not observed**. If the ordering or restart sequence does not behave as expected, Kiali could keep serving the rock's default config instead of the charm's generated one.
- **Fix**: Simplest — change `KIALI_CONFIG_PATH` to match the rock's convention (`/etc/kiali/kiali-local-config.yaml`), removing the dependency on layer-merge ordering. Alternatively, add an integration test that verifies the pebble layer and served config after the charm reaches Active.
- **Linter rule**: not mechanically checkable without running the charm to Active.

### `prometheus-api` relation carries no data despite prometheus-k8s being Active

- **Severity**: medium
- **Kind**: ux
- **Where**: cross-charm integration (prometheus-k8s rev 301 ↔ kiali-k8s rev 13)
- **Evidence**: `prometheus-k8s` reaches Active (`workload-version: 2.55.1`); the relation `prometheus-k8s:prometheus-api → kiali-k8s:prometheus-api` exists in `juju status --relations`, but `juju show-unit prometheus-k8s/0` shows `application-data: {}` on the `prometheus-api` endpoint. kiali's `PrometheusApiRequirer.get_data()` returns `None` and kiali stays Blocked on "Missing required relation to prometheus provider" regardless of istio state.
- **Impact**: kiali cannot reach Active in this environment even if the istio CRD issue is resolved, because the prometheus integration itself is not functioning. An operator deploying kiali + prometheus-k8s from charmhub would hit the same wall. Root cause may sit in prometheus-k8s or in interpretation of the `prometheus_api` interface spec — not established in this review.
- **Fix**: Investigate why prometheus-k8s rev 301 does not publish `prometheus_api` application data; this needs a follow-up review of prometheus-k8s. As a possible workaround, kiali could consider the `metrics-endpoint` (`prometheus_scrape`) interface that prometheus-k8s already provides.
- **Linter rule**: not mechanically checkable from the kiali charm alone.

### Integration test never asserts the tempo datasource actually appears in Kiali's config

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_tempo_integration.py`
- **Evidence**: The test sets up the full stack (kiali + istio + prometheus + grafana + tempo) and only asserts `kiali_is_available(ops_test)` returns HTTP 200. It never inspects the pebble config pushed to the container, checks the Kiali API for a tempo datasource, or verifies `tempo-datasource-exchange` relation data. The file has its own TODO: `# TODO: This confirms the charms assemble together, not that tracing is actually visible in Kiali.`
- **Impact**: If the `DatasourceExchange` provider flow is broken, the integration test would not catch it — the charm would reach Active (HTTP 200) with no tempo tracing actually visible in Kiali.
- **Fix**: Add an assertion that reads the Kiali container config (or the Kiali `/api/config` endpoint) and verifies `external_services.tracing.tempo_config` is populated with the correct `datasource_uid`.
- **Linter rule**: not mechanically checkable.

### `cosl` dependency unpinned

- **Severity**: medium
- **Kind**: bug
- **Where**: `pyproject.toml:11`
- **Evidence**:
  ```toml
  dependencies = [
      "cosl",
      "ops",
      "pydantic",
      "requests",
      "observability-charm-tools@git+https://github.com/canonical/observability-charm-tools@main",
  ]
  ```
  `cosl` has no version constraint; `ops` and `pydantic` are likewise unpinned; `observability-charm-tools` is pinned to the `main` branch rather than a tag.
- **Impact**: A future `cosl` release could change the `DatasourceExchange` interface and break `received_datasources()`/`publish()` without warning. The bundled `deps/cosl/` used at build time may diverge from what `pyproject.toml` would resolve, giving false confidence from static analysis.
- **Fix**: Pin `cosl` to a specific version or range (e.g. `"cosl>=0.42"`); pin `ops` and `pydantic` similarly.
- **Linter rule**: "dependency not pinned" — mechanically checkable.

### `grafana_source` library correction — retracts an earlier false finding

- **Severity**: nit
- **Kind**: docs
- **Where**: `lib/charms/grafana_k8s/v0/grafana_source.py`
- **Evidence**: The file exists (34,758 bytes) and the `charmcraft.yaml` `charm-libs` entry for `grafana_k8s.grafana_source` version `0` is correct — this charm publishes that library for Grafana consumers, and `src/` does not import it (expected, since it is a provide-side library).
- **Impact**: none — this corrects a false claim from an earlier pass of this review; no action needed.
- **Fix**: none.
- **Linter rule**: not established.

### `TempoMissingError` not in `StatusManager`'s default status map

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:160`, `_get_tempo_api` (raises at ~line 431), `deps/observability_charm_tools/status_handling/status_manager.py`
- **Evidence**:
  ```python
  DEFAULT_STATUS_MAP = {
      BlockedStatusError: BlockedStatus,
      WaitingStatusError: WaitingStatus,
      MaintenanceStatusError: MaintenanceStatus,
  }
  ```
  `TempoMissingError` is defined and raised by `_get_tempo_api`, called inside `with status_manager:` at `_get_tempo_configuration`. `_get_tempo_configuration` currently catches `TempoMissingError` internally and returns `None`, so the unmapped-exception escape path is not currently reachable.
- **Impact**: fragile — if the internal `try/except` in `_get_tempo_configuration` is ever removed during refactoring, `TempoMissingError` would escape `with status_manager:` and crash the hook.
- **Fix**: add `TempoMissingError` to the status map (requires an `observability_charm_tools` change), or have `_get_tempo_api` raise `BlockedStatusError`/`WaitingStatusError` instead.
- **Linter rule**: "exception raised inside a `with StatusManager:` block is not in the default status map" — mechanically checkable by static analysis.

### Wrong docstring on `TempoMissingError`

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:560-561`
- **Evidence**:
  ```python
  class TempoMissingError(Exception):
      """Raised when the Grafana data is not available."""
  ```
  Says "Grafana data" but is raised when Tempo data is missing.
- **Impact**: misleading during debugging/review.
- **Fix**: change to `"Raised when the Tempo data is not available."`
- **Linter rule**: not established.

### Stale docstring on `_get_tempo_api`

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:427-429`
- **Evidence**:
  ```python
  def _get_tempo_api(self) -> TempoApiAppData:
      """Get the Tempo api urls (internal and external).

      Raises:
          ConfigurationWaitingError: If a Tempo is related...
      """
  ```
  `ConfigurationWaitingError` does not exist anywhere in the codebase; the method actually raises `TempoMissingError` and `WaitingStatusError`.
- **Impact**: incorrect documentation for callers.
- **Fix**: update the docstring to list `TempoMissingError` and `WaitingStatusError`.
- **Linter rule**: not established.

### Local TODO patch in bundled `prometheus_api` library

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/mimir_coordinator_k8s/v0/prometheus_api.py:150`
- **Evidence**:
  ```python
  # TODO: This signature was patched locally to fix a type error.
  #  Revert back to the standard version once this is fixed in mimir-coordinator
  def get_data(self) -> Optional[PrometheusApiAppData]:
  ```
- **Impact**: future upstream updates to this library may not apply cleanly, and the charm could miss upstream fixes.
- **Fix**: resolve the underlying type error upstream so the local patch can be reverted, or explicitly fork/own the local version.
- **Linter rule**: not established.

### Ruff violations in bundled charm libraries

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/grafana_k8s/v0/grafana_metadata.py:77`, `lib/charms/mimir_coordinator_k8s/v0/prometheus_api.py:76`, plus 42 more across `lib/charms/loki_k8s/v1/loki_push_api.py`, `lib/charms/prometheus_k8s/v0/prometheus_scrape.py`, `lib/charms/traefik_k8s/v2/ingress.py`
- **Evidence**: `ruff check lib/charms/` reports 44 errors: `I001` (2, fixable — import order in `grafana_metadata.py` and `prometheus_api.py`), `D401` (37, imperative-mood docstrings), `RET504` (5, unnecessary assignment before return), `C901` (1, `expand_wildcard_targets_into_individual_jobs` complexity 14 > 10).
- **Impact**: clutters lint output for bundled upstream code; the two `I001` issues are trivially fixable.
- **Fix**: run `ruff check --fix` for the `I001` issues, or add an explicit `extend-ignore`/exclusion for bundled `lib/` code to acknowledge these are upstream conventions.
- **Linter rule**: `I001` is mechanically fixable with `ruff check --fix`.

### `codespell` skips `lib/` — bundled libraries never spell-checked

- **Severity**: low
- **Kind**: test-gap
- **Where**: `pyproject.toml`
- **Evidence**:
  ```toml
  [tool.codespell]
  skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.coverage"
  ```
- **Impact**: typos in bundled library docstrings/comments go undetected.
- **Fix**: remove `lib` from the skip list, or configure a separate `codespell` pass for `lib/`.
- **Linter rule**: not established.

### No `juju refresh` / upgrade path tested

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py`, `tests/integration/test_tempo_integration.py`
- **Evidence**: no test exercises `juju refresh` or `upgrade-charm`. Channel 2/edge on charmhub has only revision 13, so no newer revision is currently available to test against.
- **Impact**: the charm was refactored to use a reconcile pattern (e.g. commits `4410259`, `d123043`) and had a relation renamed (`dea9f9c`); an upgrade that changes relation data shapes could leave the charm in a bad state without an explicit upgrade handler or test coverage.
- **Fix**: add a `test_upgrade` integration test that refreshes mid-flight and asserts recovery to Active; monitor for new 2/edge revisions to test against.
- **Linter rule**: not established.

### Unit tests don't cover the empty-datasources branch of `_get_tempo_datasource_uid`

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py`
- **Evidence**: `test_e2e_charm_configuration` always includes a `tempo-datasource-exchange` relation with data via `mock_tempo_datasource_exchange()`; no test exercises the empty-datasources branch (`src/charm.py:461-462`).
- **Impact**: the missing-`raise` bug (first finding above) would have been caught by a test on this exact branch.
- **Fix**: add a scenario test with an empty tempo-datasource-exchange relation asserting Waiting (not Blocked); also test `grafana_uid is None` with a non-empty tempo-datasource-exchange.
- **Linter rule**: not established.

### Unit tests don't cover the grafana relation-with-data branch

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py::test_kiali_config`
- **Evidence**: `test_kiali_config` only tests the grafana-optional path (`grafana_internal_url`/`grafana_external_url` both `None`); the branch where both URLs are provided (`src/charm.py:252-260`) is exercised only by e2e tests that mock internals and don't assert config content, including the trailing-slash-stripping behaviour and the `LOGGER.info` warning.
- **Impact**: a regression in URL-stripping or the info-log warning would go undetected.
- **Fix**: add a unit test with `grafana_internal_url="http://grafana:3000/"` asserting the stripped URL and the log message.
- **Linter rule**: not established.

## Worth copying

- **`StatusManager` context-manager pattern for reconcile** (`src/charm.py:151-209`): each step is wrapped in `with status_manager: step()`, and `self.unit.status = status_manager.worst()` is set once at the end. Cleaner than nested try/except or setting status at every failure point — every step can contribute a status and the worst wins.
- **Pydantic config schemas** (`src/workload_config.py`, `src/charm_config.py`): all Kiali configuration modelled as Pydantic `BaseModel` classes, giving validation, serialization, and a clear schema.
- **Single reconcile method driven by all events** (`src/charm.py:154`): every interesting event (`config_changed`, `start`, `kiali_pebble_ready`, all relation `*_changed`/`*_broken`) funnels into one `reconcile()` method. Stateless between hooks, no `defer()`, no `StoredState`.
- **Config-diffing before restart** (`src/charm.py:235-242`): `_is_container_file_equal_to` compares rendered config against the current container file before restarting, avoiding unnecessary workload restarts.
- **Proper `container.can_connect()` guard** (`src/charm.py:221-223`): `_configure_kiali_workload` checks this before any container operation and raises `WaitingStatusError` otherwise — the correct pattern for k8s charms where Pebble may not be ready.
- **Graceful optional-relation handling** (`src/charm.py:166-174`): `_get_grafana_metadata` raises `GrafanaMissingError` when no grafana relation exists; the reconcile loop catches it with a log-and-continue rather than escalating to Waiting/Blocked.

## Common-practice notes

- `ops` declared as a direct dependency, consistent with modern charm practice.
- All eight bundled charm libraries under `lib/charms/` are v0/v1 and at latest stable; `charmcraft.yaml`'s `charm-libs` entry (`grafana_k8s.grafana_source` v0) is correct and auto-managed.
- Follows the modern `src/` layout (`charm.py`, `charm_config.py`, `workload_config.py`).
- `charmcraft.yaml` is notably clean: `assumes: juju >= 3.6`, proper `resources` block with `upstream-source`, `links` section with docs/website/source/issues, and `parts.override-build` stamping a version via `git describe`.
- `rustc`/`cargo` correctly declared as `build-packages` to compile pydantic.
- `peers.grafana` is unusual for a k8s charm — most have no peer relations. The stated reason (satisfying the `grafana_datasource` library) is plausible but the relation is unused (see Findings).
- No `storage` declarations, consistent with a pure-API workload.
- CI delegates to the shared `canonical/observability/.github/workflows/charm-quality-gates.yaml@v2` workflow, running tox lint/static/unit — a pattern used across the observability team.
- `cosl` is a direct PyPI dependency rather than a charm library, appropriate since it is general-purpose observability tooling, not relation-specific.
- `juju remove-application` requires interactive y/N confirmation even with `--force`; use `yes | juju remove-application` in scripts.
- K8s-only charm (`containers.kiali`); no machine/LXD substrate testing possible.
- `view-only-mode` is the only charm config option; all other behaviour is relation-driven — a clean, intentionally declarative design.

## Tests

- **Unit tests**: 16 tests in `tests/unit/`, all passing, using `ops-scenario`. Good fixture isolation (`disable_requests_get_autouse`). See the unit-test topology finding above for an unresolved question about `mock_tempo_datasource_exchange()`.
- **tox lint**: `ruff check src/ lib/charms/` — 2 fixable `I001` errors, 46 non-fixable (`D401`, `RET504`) in bundled upstream libraries; `src/` is clean.
- **tox static**: `pyright src/charm.py` with correct `PYTHONPATH` — 0 errors. Without it, 8 `reportMissingImports` for `charms.*` imports (expected — `pyproject.toml` correctly scopes `include = ["src/**.py"]` so CI runs with the right path).
- **Integration tests**: `test_charm.py` (7 tests) and `test_tempo_integration.py` (full stack: Tempo + Grafana + Istio + Kiali), using `pytest-operator`. `test_kiali_is_available` asserts HTTP 200; `test_remove_relation_prometheus` asserts Blocked after removal. `test_tempo_integration.py` does not assert the tempo datasource actually appears in Kiali's config (see Finding above), and has a `ModuleNotFoundError: No module named 'tests'` when collected directly rather than via `tox -e integration`.
- **Coverage gaps**: empty tempo-datasources branch; grafana-with-data branch; upgrade path; pebble layer/rock interaction in Active state; `DatasourceExchange` provider/consumer data-path direction.
- **CI**: shared workflow, runs tox lint/static/unit; no spread tests in this repo.
- **Terraform tests**: `terraform/tests/example/kiali.tf` exists but is not run in CI; no `terraform validate`/`test` in tox.

## Docs

- **README.md**: thin — one paragraph, links to charmhub. No usage instructions, config reference, or relation diagram.
- **CONTRIBUTING.md**: points to `tox devenv -e integration`, but the tox envlist is only `lint, static, unit, integration` — no `devenv` environment exists. Out of date.
- **charmcraft.yaml links**: docs, website, source, issues all present and correct.
- **Terraform module**: `terraform/README.md` (terraform-docs generated) is thorough; `main.tf`/`variables.tf`/`outputs.tf`/`version.tf` look correct; channel validation added in commit `833eb52`.
- **charmhub description**: thin — "Kiali is a dashboard for Istio, providing visualization and control of your service mesh." Doesn't describe relations, config options, or the `--trust` requirement.
- **Open issue #15** (error handling without `--trust`): the charm does not assert `--trust` availability at runtime; failure manifests as generic hook errors rather than a clear message.
- **Open issue #51** (authenticated Grafana): code logs at INFO "Grafana integration only works when connected to unauthenticated grafana instances" — documented in code, not in the charmhub description.
- **Open issue #53** (grpc for Tempo): `workload_config.py:27` has `use_grpc`/`grpc_port` fields that are declared but never populated; not currently a bug.
- **`No Loki endpoints available` warning**: seen on every reconcile while establishing the loki-k8s relation; expected behaviour from `LogForwarder._update_logging()`, harmless but could be suppressed during initial relation establishment.

## Open questions

1. **Pebble layer interaction with the official rock**: unverified because the charm never reached Active and never called `add_layer` in this review. Needs a fully-related deployment (working istio-k8s and prometheus-k8s both publishing data) to confirm the charm's layer overrides the rock's and Kiali serves the charm's config.
2. **Tempo grpc vs http (issue #53)**: `use_grpc`/`grpc_port` exist but are unused; tracked upstream, not a bug today.
3. **Grafana authenticated integration (issue #51)**: documented in code, not charmhub description; untested here since grafana-k8s published no metadata.
4. **`TempoMissingError` status mapping**: whether it should be added to `StatusManager`'s map, or whether catching it internally is the intended design. The escape path is currently unreachable but fragile.
5. **`_is_prometheus_source_available` future intent**: currently always returns `True` due to the wrong caught exception; unclear if it was meant for a readiness probe that was never wired up.
6. **`prometheus-api` empty data**: whether this is a prometheus-k8s rev 301 bug or requires additional configuration; needs a follow-up review of prometheus-k8s.
7. **`DatasourceExchange` provider/requirer topology**: directly contradictory conclusions exist between the draft review and the reviewer's own working notes about whether the unit test's relation topology matches production. This must be resolved by re-reading `deps/cosl/interfaces/datasource_exchange.py` against `charmcraft.yaml`'s `provides`/`requires` blocks and observing a real tempo-coordinator-k8s that is actually publishing datasources.
8. **grafana-k8s oscillating error pattern**: consistent, does not affect kiali; likely a grafana-k8s rev 180 issue worth confirming against grafana-k8s's own tracker.
9. **Integration test tempo-datasource assertion**: closing this gap requires reading Kiali's served config or API and asserting the datasource UID is present.
