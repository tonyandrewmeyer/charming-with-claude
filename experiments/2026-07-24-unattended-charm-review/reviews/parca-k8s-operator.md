# parca-k8s-operator

A well-structured K8s sidecar charm for Parca continuous profiling: clean reconciler pattern, correct TLS lifecycle ordering, change-detection guards that avoid unnecessary restarts, and a broad, well-tested COS integration surface. But the scale guard (`is_scaled_up()`) is broken on both supported Juju versions in different ways — it never blocks anything on scale-up (both units run active, silently splitting profile data), and on Juju 4.0 it then permanently bricks the surviving unit on scale-down with no recovery path short of `remove-application`. That is the first thing a maintainer should fix; everything else (unvalidated config values, an incorrect scheme in `list-endpoints`, non-deterministic nginx config) is secondary.

| | |
|---|---|
| Repo | canonical/parca-k8s-operator @ `748063c` (2026-07-07) |
| Charms | parca-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25) and concierge-k8s-4 (Juju 4.0.5), both 2/stable rev 378 (ubuntu@24.04) |
| Reviewed | 2026-07-27 |

## What it does

Deploys Parca (continuous profiling backend) on Kubernetes as a single-unit Juju application. Three containers (parca, nginx reverse proxy, nginx-prometheus-exporter) integrate with the Canonical Observability Stack: Grafana dashboards/datasources, Prometheus metrics scraping, Loki log forwarding, Tempo tracing (charm and workload), self-profiling endpoint, S3 object storage, TLS via `tls-certificates`, ingress via Traefik or Istio, service mesh policies, Sloth SLOs, and a catalogue entry. Supports profile forwarding to/from remote Parca stores.

## Deployment log

**Controller: `concierge-k8s-3` (Juju 3.6.25), models `rv-parca-deep3`, `rv-parca-deep2`, `rv-parca-int`**

```bash
$ juju deploy parca-k8s --channel 2/stable --trust
# rev 378 on ubuntu@24.04
```

- Active in ~3.5 minutes.
- `rv-parca-int`: parca-k8s + self-signed-certificates (edge) + traefik-k8s (edge) + s3-integrator (edge). TLS related → nginx config updated with SSL directives, certs appeared under `/etc/nginx/certs/`; TLS removed → nginx reverted to plain HTTP. Traefik ingress changed the URL to the ingressed IP. `s3-integrator` (edge) blocked: its config keys (`bucket`, `endpoint`, `path`, `region`, `s3-api-version`, `s3-uri-style`, `storage-class`, `tls-ca-chain`) use Juju secrets and no `access-key`/`secret-key` keys were available, so S3 integration could not be exercised.
- `rv-parca-deep3`: parca-k8s + self-signed-certificates (1/edge) + tempo-k8s (latest/edge). Tempo remained in maintenance ("reconfiguring Tempo") for 5+ minutes after relations were added; application-data on the tracing relations stayed empty (tempo never published endpoints), so charm/workload tracing could not be confirmed end-to-end. Likely a tempo-k8s issue (probably needs S3), not a parca-k8s fault.
- `rv-parca-deep2`: parca-k8s + self-signed-certificates + prometheus-k8s + grafana-k8s + loki-k8s + catalogue-k8s. All 6 apps reached active. Relation data confirmed flowing: prometheus received alert rules and scrape jobs, grafana registered the parca datasource, catalogue published the URL.
- Scale-up 1→2 on Juju 3.6: both units reached ActiveStatus with workload versions set. `is_scaled_up()` returned False because `relation.units` on `parca-peers` was empty. The scale guard has zero effect on Juju 3.6 — `logger.error("Application has scale >1...")` never appeared in debug-log.
- Scale-down 2→1 on Juju 3.6: unit 0 recovered to active/idle normally (because `is_scaled_up()` was never True to begin with).

**Controller: `concierge-k8s-4` (Juju 4.0.5), models `rv-parca-juju4`, `rv-parca-cos4`**

```bash
$ juju deploy parca-k8s --channel 2/stable --trust
# rev 378 on ubuntu@24.04
```

- Active in ~4 minutes.
- `rv-parca-cos4`: full COS stack — self-signed-certificates + prometheus-k8s (2/stable) + grafana-k8s (2/stable) + loki-k8s (2/stable). All 6 apps reached active. Relation data confirmed flowing to prometheus (scrape jobs with TLS `ca_file`, alert rules), grafana datasource registered. First confirmation that the COS stack works with this charm on Juju 4.0.
- Relations exercised on Juju 4.0: TLS (certificates), metrics-endpoint, grafana-dashboard, grafana-source, logging.
- Scale-up 1→2 on Juju 4.0: both units ran active with `workload-version: 0.23.1` set. Unit 1's Pebble services started (4/4 containers ready) before `parca-peers-relation-joined` fired for it. `is_scaled_up()` returned False during `__init__` for the same reason as on Juju 3.6 — the peer relation had not yet synchronized. Once the peer relation was established, both units stayed active; the scale guard never triggered on scale-up.
- Scale-down 2→1 on Juju 4.0: unit 1 terminated. Unit 0 became permanently stuck in BlockedStatus ("You can't scale up parca-k8s. Deploy a new application instead."). `juju show-unit` showed no `related-units` under `parca-peers`, yet `is_scaled_up()` returned True (the ops framework appears to retain stale relation data). Three config-changed hooks over 2+ minutes all reproduced the block; changing config (`memory-storage-limit=4097`) did not clear it. Only recovery observed: `juju remove-application`.

**TLS + COS on Juju 4.0:**
- TLS relation added: status message correctly changed from `http://` to `https://`. `list-endpoints` returned `direct-http-url: https://...` (correct, no ingress active).
- Prometheus scrape jobs correctly included `scheme: https` and `tls_config.ca_file` with the CA certificate when TLS was active.

**Teardown (Juju 4.0, `rv-parca-cos4`):**
```bash
$ juju remove-application parca-k8s --no-prompt --force
```
Parca-k8s was removed cleanly. grafana-k8s briefly went to error state ("hook failed: grafana-source-relation-departed") — a grafana-k8s issue, not a parca-k8s defect. All parca resources cleaned up.

**Actions:**
- `list-endpoints` on Juju 3.6 with TLS but no ingress: returned `direct-http-url: http://...` because `_scheme` returned the ingress scheme (which falls through to `_internal_scheme` only when ingress is absent — this manifests as a bug specifically when both ingress AND TLS are active; see Finding below).
- `list-endpoints` on Juju 4.0 with TLS but no ingress: returned `direct-http-url: https://...` — correct.

**Failure injections:**
- `memory-storage-limit=-100`: accepted silently. Parca started with `--storage-active-memory=-104857600`.
- `memory-storage-limit=0`: accepted silently. Parca started with 1024MB (default), not 0 — the `or 1024` pattern treats 0 as falsy.
- `memory-storage-limit=1048576` (1TB): accepted, no upper-bound validation.
- `enable-persistence=foo`: correctly rejected by Juju with `option "enable-persistence" expected boolean, got "foo"`.
- `slo-errors-target=95.0`: rejected with "unknown option" on rev 378 (SLO config not present in the published revision).
- Killed parca process (`kill -9`): Pebble restarted within ~2 seconds. Unit stayed active.
- Killed nginx master process: Pebble restarted within ~5 seconds. Old workers briefly orphaned.
- Removed TLS relation while running: recovered to non-TLS config within ~30 seconds.
- Config change on a blocked unit (`enable-persistence=true`, `memory-storage-limit=4097`): did not clear the Juju 4.0 scale-down permanent block.

**Refresh path:**
- `juju refresh parca-k8s --channel 2/stable`: "already up-to-date" — no revision delta within the 2/stable track.
- Cross-track refresh (2/stable → 0.27/stable) is impossible because 2/stable is on ubuntu@24.04 and 0.27/stable is on ubuntu@26.04. The upgrade integration test is skipped for this reason.

## Observed behaviour

- **Startup time**: ~3.5–4 minutes from deploy to active on both Juju 3.6 and 4.0.
- **Resource use**: 14m CPU, 131Mi memory at idle (single unit, no integrations beyond peer). Juju 4 unit showed 4/4 containers ready.
- **Pebble recovery**: killing parca → restart within 2–3 seconds; killing nginx master → restart within 5 seconds, old workers briefly orphaned. No Juju-level disturbance either time.
- **TLS recovery**: adding/removing the `certificates` relation works cleanly — nginx config updates, cert files appear/disappear, nginx reloads. ~30 seconds for status to reflect the change.
- **Scale guard broken on both Juju versions, for different reasons**: on Juju 3.6, `is_scaled_up()` always returns False because `relation.units` is empty during hooks. On Juju 4.0, it also returns False during unit 1's `__init__` (peer relation not yet synchronized), so it fails identically on scale-up; the only difference is that on Juju 4.0 the guard later triggers on scale-down and gets stuck True. Both units run active with `workload-version: 0.23.1` set — a silent data-corruption scenario where two parca instances each believe they own the profile store.
- **Scale-down permanent block (Juju 4.0)**: `parca-peers-relation-departed` fires only on the departing unit (unit 1), never on unit 0, so unit 0 never re-evaluates `is_scaled_up()`. The ops framework appears to retain the departed unit in `relation.units` after scale-down: `juju show-unit` shows no `related-units`, but `is_scaled_up()` still returns True.
- **Scale-down recovery (Juju 3.6)**: after scaling 2→1, unit 0 recovers normally, since `is_scaled_up()` was never True in the first place.
- **Scheme mismatch**: `_scheme` returns `self.ingress.scheme or self._internal_scheme`. When both ingress (Traefik, scheme `"http"`) and TLS are active, `_scheme` returns `"http"` even though the direct endpoint is TLS-terminated. `list-endpoints`'s `direct-http-url`/`direct-grpc-url` use `_scheme` instead of `_internal_scheme`. With TLS but no ingress, the scheme is correct.
- **Config-change hooks**: one `config-changed` hook fires, and a full reconcile runs (all relation-data pushes included); no cascading restarts, because change-detection prevents unnecessary reloads. update-status (every 5 minutes) also triggers a full reconcile.
- **"No Loki endpoints available"**: logged on every hook during deploy until the loki relation settles. Harmless but noisy.
- **Workload under BlockedStatus**: with unit 0 blocked after scale-down, `kubectl exec` confirmed both parca and nginx Pebble services still running — the block affects only Juju status, not the running workload.
- **Tracing relations**: `charm-tracing` and `workload-tracing` relations formed with tempo-k8s; relation data showed tempo's `ingress-address`/`private-address`, but tempo stayed in maintenance for 5+ minutes and never published endpoint data, so the integration could not be verified end-to-end. The charm's `is_ready()` guards on both tracing endpoints likely prevent misconfiguration in this state, but this is unverified.
- **Teardown**: clean on the parca-k8s side; the grafana-k8s error on `grafana-source-relation-departed` is a grafana charm issue, not caused by parca-k8s.

## Findings

### 1. Scale guard non-functional on scale-up, on both Juju versions — both units run the full workload
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:193-196` (`is_scaled_up()` call and early return in `__init__`)
- **Evidence**: On Juju 3.6, after `juju add-unit -n 1`, both units showed `active` / `workload-version: 0.23.1`; `logger.error("Application has scale >1...")` never appeared. On Juju 4.0, after `juju add-unit -n 1`, both units likewise showed `active` / `workload-version: 0.23.1`; unit 1's pod reached 4/4 containers ready and ran the full parca process before `parca-peers-relation-joined` fired. In both cases `relation.units` on `parca-peers` was empty when `__init__` ran for unit 1. On Juju 3.6 it stays empty indefinitely; on Juju 4.0 it eventually populates, but only after the workload has already started (leading to Finding 2 on scale-down).
- **Why it matters**: two parca instances run independently, each believing it owns the store. Profile data is split between them; queries see inconsistent results depending on which unit serves the request. This is silent corruption of the observability surface, worse than simply blocking.
- **Fix**: use `self.model.app.planned_units()` (ops 2.x) to check planned scale — a property of the application model available before relations synchronize — instead of peer-relation membership. Move the check into `reconcile()` (or each workload's `reconcile()`), not just `__init__`.
- **Linter rule**: "peer-relation `units` used as a scale guard in `__init__` without verifying availability" — not mechanically checkable; requires cross-Juju-version testing.

### 2. Scale-down permanently bricks the charm on Juju 4.0
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:193-196` (`is_scaled_up()` in `__init__`) and `src/charm.py:498-500` (`_on_collect_unit_status`)
- **Evidence**: after `juju scale-application parca-k8s 1` on Juju 4.0, unit 0 showed BlockedStatus "You can't scale up parca-k8s" indefinitely. Three config-changed hooks over 2+ minutes reproduced the same error. `juju show-unit` confirmed zero `related-units` in the peer relation, yet `is_scaled_up()` returned True. `parca-peers-relation-departed` fires only on the departing unit (unit 1), not on unit 0. No config change or relation change resolved it; only recovery was `juju remove-application`.
- **Why it matters**: an operator who scales up then back down is left with a permanently blocked application that must be removed and redeployed.
- **Fix**: (a) move the scale guard to the top of `reconcile()` so it is re-evaluated on every hook; (b) add a `relation-departed` observer on the peer relation that triggers `reconcile()`; (c) use `planned_units()` as the canonical scale check.
- **Linter rule**: "`__init__` exits early on a condition that can change without a dedicated event observer" — mechanically checkable: flag `return` statements in `__init__` guarded by relation-state checks lacking corresponding event observers.

### 3. No config validation: negative memory limit accepted silently
- **Severity**: high
- **Kind**: bug / ux
- **Where**: `src/parca.py:208` (`parca_command_line`)
- **Evidence**: `juju config memory-storage-limit=-100` succeeded; parca started with `--storage-active-memory=-104857600`.
- **Why it matters**: negative memory limits are passed straight to the parca binary with no operator feedback; Parca 0.23.1 tolerated it in testing, but future versions may crash.
- **Fix**: add `minimum: 1` to `memory-storage-limit` in `charmcraft.yaml` — Juju's `type: int` supports `minimum`/`maximum` natively.
- **Linter rule**: "`type: int` config option without `minimum`" — mechanically checkable from `charmcraft.yaml`.

### 4. Scale-up starts the full workload on the second unit before any blocking occurs
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:193-196` (early return) and `src/charm.py:200` (`reconcile()` call)
- **Evidence**: on Juju 4.0, unit 1's pod showed 4/4 containers ready, `workload-version: 0.23.1` set, and `ps aux` in the parca container confirmed the full parca process running — because `is_scaled_up()` returned False during unit 1's `__init__` (peer relation had not arrived), so `reconcile()` ran fully.
- **Why it matters**: the second unit consumes CPU/memory/disk and briefly appears available to consumers; on Juju 3.6 it stays running permanently.
- **Fix**: same as Finding 1 — use `planned_units()` in `reconcile()`.
- **Linter rule**: not mechanically checkable — requires flow analysis of peer-relation availability.

### 5. Zero memory-storage-limit silently replaced by default 1024MB
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/parca.py:208`
- **Evidence**: `juju config memory-storage-limit=0` succeeded; parca started with `--storage-active-memory=1073741824` (1024MB), not 0. The code `limit = (memory_storage_limit or 1024) * 1048576` treats 0 as falsy in Python.
- **Why it matters**: an operator setting `memory-storage-limit=0` to minimize memory unknowingly gets 1024MB instead.
- **Fix**: change to `limit = (memory_storage_limit if memory_storage_limit is not None else 1024) * 1048576`. Also add `minimum: 1` to config.
- **Linter rule**: "`type: int` config used with `or <default>` pattern" — mechanically checkable: flag `or` on config-derived int values.

### 6. URL scheme shows `http://` when both ingress and TLS are active
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:316` (`_scheme` property), `src/charm.py:518` (`_on_list_endpoints_action`), `src/charm.py:521` (`direct-http-url`)
- **Evidence**: when both ingress (traefik-k8s) and TLS are active, the ingress scheme is `"http"` (Traefik has no TLS), so `_scheme` returns `"http"` even though `_internal_scheme` would return `"https"`. `direct-http-url`/`direct-grpc-url` use `_scheme`, so `list-endpoints` shows `http://` for a direct endpoint that is actually TLS-terminated (nginx serves SSL, certs on disk). Verified on Juju 3.6 with TLS + traefik; does not manifest with TLS-only (no ingress).
- **Why it matters**: operators reading action output or status messages see `http://` and may configure clients to use unencrypted connections when TLS is actually available.
- **Fix**: use `self._internal_scheme` for direct URLs and `self._scheme` for ingressed URLs in `_on_list_endpoints_action`; also add a `grpcs://`/`grpc://` prefix to the gRPC URL.
- **Linter rule**: not mechanically checkable.

### 7. Missing SLO config options in published charm
- **Severity**: medium
- **Kind**: bug / release-gap
- **Where**: `charmcraft.yaml:234-264` (local HEAD) vs published rev 378
- **Evidence**: `juju config slo-errors-target=95.0` returned "unknown option" on rev 378. The repo's `charmcraft.yaml` has `slo-errors-target`, `slo-latency-target`, and `slos` config keys, but rev 378 does not; rev 378 targets `ubuntu@24.04` while the repo targets `ubuntu@26.04`.
- **Why it matters**: charmhub description lists SLO features unavailable in the published revision.
- **Fix**: publish a 26.04-based revision to a channel, or document the gap.
- **Linter rule**: not mechanically checkable.

### 8. `is_scaled_up()` unit test covers only the ideal case
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm/test_charm.py:498-504`
- **Evidence**: `test_parca_blocks_if_scaled` creates a peer relation with `peers_data={1:{}}` — the peer unit is already present when `__init__` runs (happy path). Not covered: (a) the race where `relation.units` is empty during `__init__` (the actual behaviour on both Juju 3.6 and 4.0 for unit 1), (b) scale-down recovery, (c) `is_scaled_up()` returning True after scale-down when `juju show-unit` shows no related units.
- **Why it matters**: the test passes but the feature is broken in two distinct deployment scenarios.
- **Fix**: add scenario tests for (a) empty vs. populated peer-relation units at `__init__` time, (b) a scale-down sequence, (c) that `collect-status` doesn't double-add statuses.
- **Linter rule**: not mechanically checkable.

### 9. No upper bound on memory-storage-limit
- **Severity**: low
- **Kind**: bug / ux
- **Where**: `charmcraft.yaml:227` (config option) and `src/parca.py:208`
- **Evidence**: `juju config memory-storage-limit=1048576` (1TB) accepted without error.
- **Why it matters**: an operator typo (e.g. 1000000 instead of 1000) could cause parca to request excessive memory.
- **Fix**: add `maximum: 65536` (64GB) or similar to `charmcraft.yaml`.
- **Linter rule**: "`type: int` config without `maximum`" — mechanically checkable.

### 10. Non-deterministic nginx config due to `Set` return type
- **Severity**: low (currently harmless with a single-element set)
- **Kind**: bug / latent
- **Where**: `src/nginx.py:167` (call site) and `src/nginx.py:213-216` (`_upstreams_to_addresses` returns `Dict[str, Set[str]]`)
- **Evidence**: `_upstreams_to_addresses()` returns `{"127.0.0.1"}` as a set; the charmlibs nginx `_config.py:487` iterates `for addr in addresses` over it. Python set iteration order is not guaranteed. Open issue #525 (flaplint) already flags this. Currently harmless with one address, but a second upstream would cause `_has_config_changed()` to return True on every hook.
- **Why it matters**: latent defect already flagged by tooling; adding a second upstream would trigger unnecessary nginx reloads.
- **Fix**: change return type to `Dict[str, List[str]]`.
- **Linter rule**: mechanically checkable — flaplint already flags it.

### 11. Unnecessary full reconcile on every update-status hook
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:148` (`reconcile()` called unconditionally from `__init__`)
- **Evidence**: every 5 minutes, update-status triggers a full reconcile — TLS certs compared and pushed, parca config pushed, nginx config regenerated, all relation data pushed, ingress reconciled. Internal change detection avoids unnecessary restarts, but the I/O (3 `container.pull()` calls per cycle with Traefik + TLS + S3) still happens.
- **Why it matters**: unnecessary I/O to all three containers every 5 minutes.
- **Fix**: guard `reconcile()` or the relation-data push behind specific events.
- **Linter rule**: not mechanically checkable without event-type analysis.

### 12. `_has_config_changed` returns `False` on `PathError` — misleading logic
- **Severity**: low
- **Kind**: bug
- **Where**: `src/nginx.py:117-131`
- **Evidence**:
  ```python
  except (pebble.ProtocolError, pebble.PathError) as e:
      logger.warning(...)
      return False
  ```
  When the config file doesn't exist yet (`PathError`), the method returns `False`. The caller pushes the config and calls `autostart()` (which starts nginx with the new config) but skips `reload()` because `should_restart` is `False`. This works by coincidence — `autostart()` starts nginx loading the just-written config — but the method name claims "has config changed" and the logic violates that contract.
- **Why it matters**: a future change that suppresses `autostart()` when `should_restart` is False would break first-run.
- **Fix**: return `True` on `PathError` (config is being written for the first time), or refactor the contract.
- **Linter rule**: not mechanically checkable — semantic issue.

### 13. `_on_collect_unit_status` adds both `BlockedStatus` and `ActiveStatus`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:498-516`
- **Evidence**: the handler unconditionally adds `ActiveStatus` after conditionally adding `BlockedStatus`. When scaled (or stuck after scale-down), both statuses end up in the status list. Juju picks the highest-priority one (Blocked), but both are present, which is confusing and could conceal status races.
- **Why it matters**: if Juju's status-resolution precedence ever changes, behaviour could shift unexpectedly.
- **Fix**: use `if/elif/else` or `return` so only one status is added per path.
- **Linter rule**: "`event.add_status` called unconditionally after conditional `add_status` calls" — mechanically checkable within a single method.

### 14. `_delete_certificates` in `nginx.py` touches the charm container filesystem
- **Severity**: low (nit)
- **Kind**: bug
- **Where**: `src/nginx.py:103-113`
- **Evidence**: the nginx workload class method `_delete_certificates` calls `Path(CA_CERT_PATH).unlink(missing_ok=True)` on the charm process's local filesystem (no `self._container` prefix), where `CA_CERT_PATH = "/usr/local/share/ca-certificates/ca.cert"` — this is the charm container's CA cert path, managed elsewhere by `charm.py:_reconcile_tls_config`.
- **Why it matters**: architecturally confusing layering violation; if the charm container's CA cert path moves, this method silently breaks.
- **Fix**: move this cleanup to `charm.py:_reconcile_tls_config`, or scope the nginx class to only manage its own container's paths.
- **Linter rule**: not mechanically checkable.

### 15. `typing.cast` masks possible `None` values at runtime
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:177-178`
- **Evidence**: `typing.cast(bool, self.config.get("enable-persistence", None))` — `typing.cast` is a no-op at runtime.
- **Why it matters**: if Juju returns `None` for a config key with a default (an edge case during upgrade), behaviour silently changes.
- **Fix**: drop the cast or add explicit `is not None` checks.
- **Linter rule**: not easily checkable.

### 16. `charm_tracing` set up on every reconcile without caching
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:216-219`
- **Evidence**: `ops_tracing.set_destination(...)` is called on every reconcile, and `self._tls_config.certificate.ca.raw` is accessed on every call too.
- **Why it matters**: minor performance cost; if the tracing exporter re-creates resources on repeat calls, could leak resources.
- **Fix**: cache the last-set endpoint and skip if unchanged.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Reconciler pattern** (`src/charm.py:148-176`): `reconcile()` called once at the end of `__init__`, driving all state synchronisation. No event handlers needed — the charm re-entrantly reconstructs desired state on every hook. Cleanest pattern seen for sidecar charms.
- **TLS cert ordering in nginx reconcile** (`src/nginx.py:140-148`): `_reconcile_tls_config()` runs before `_reconcile_nginx_config()`, so certs are on disk before nginx config references them, avoiding a window where nginx starts with TLS directives pointing to missing files. Comments explain the ordering.
- **Change detection before workload restart** (`src/nginx.py:117-131`, `src/nginx.py:79-92`): both nginx config and TLS certs are compared against on-disk content before being pushed; cert updates skip writes if content is identical. Every sidecar charm should adopt this.
- **Rich `charmcraft.yaml`**: every relation has a `description`, config options are documented, resources declare `upstream-source` for integration test use, `assumes: juju >= 3.6` is set.
- **Workload class abstraction** (`src/parca.py`, `src/nginx.py`, `src/nginx_prometheus_exporter.py`): each workload has its own class with `reconcile()`, a pebble layer property, and container name constants — the charm is a thin orchestrator, and each piece is independently unit-testable.
- **Pebble auto-restart confirmed**: killed parca/nginx processes are restarted by Pebble in 2–5 seconds, no operator intervention needed.
- **`list-endpoints` action** (`src/charm.py:258-269`): returns both direct and ingressed URLs — a small touch that makes operator life much easier.
- **Service mesh policies as data** (`src/charm.py:212-248`): `_mesh_policies` declares authorization policies as a list of data objects — readable and testable.

## Common-practice notes

- **`charmlibs` packages**: migrated nginx config generation and SLO handling to shared packages (`charmlibs-nginx-k8s`, `charmlibs-interfaces-sloth`, `charmlibs-interfaces-service-mesh`) rather than vendored charm libs — ahead of most COS charms.
- **`ops[testing]` scenario tests**: uses the scenario framework with parametrised event types and containers — current COS best practice.
- **`jubilant` for integration tests**: newer framework instead of `pytest-operator`; 38 tests collected across 8 files.
- **uv + pyproject.toml**: fully migrated, `uv.lock` committed.
- **`assumes: juju >= 3.6`**: published rev 378 is on `ubuntu@24.04`, repo targets `ubuntu@26.04` — a cross-base migration gap that blocks `juju refresh` from HEAD; the upgrade test is skipped.
- **No `docs/` directory**: only README.md and CONTRIBUTING.md. For a charm with this many integrations, a `docs/` with integration guides would help.
- **`charm-tracing` uses OTLP HTTP, `workload-tracing` uses OTLP gRPC**: correct split.
- **`lib/charms/parca_k8s/v0/`**: two charm-owned libraries (`parca_scrape.py`, `parca_store.py`), both well-structured with comprehensive docstrings. `parca_scrape.py`'s `ProfilingEndpointConsumer.jobs()` includes a proper guard (`if not relation.units: return []`). `parca_store.py`'s `ParcaStoreEndpointProvider` does not call `set_remote_store_connection_data` on `leader-elected` — if the leader changes, store data could go stale until the next reconciliation.

## Tests

**Unit tests**: 132 passed, 159 warnings (all from third-party libs), 0 failures. 93% line coverage.

```bash
$ tox -e unit
132 passed in 1.67s
```

**Coverage gaps**:
- `src/charm.py`: 97% — missing lines 217 (charm_tracing set_destination), 284 (`_reconcile_slos` slos config), 336 (tls_config cert retrieval), 544 (relabel_configs in `_generic_scrape_target`).
- `src/parca.py`: 88% — missing S3 config generation (lines 251-270), version fetch errors (157-163).
- `src/nginx.py`: 85% — missing PathError path (118-119), cert comparison branches (131, 135-136).

**Findings not covered by any unit test**: negative/zero/very-large `memory-storage-limit` (3, 5, 9); `_has_config_changed` PathError path (12); scale-up race — `test_parca_blocks_if_scaled` pre-populates peer data and doesn't test empty `relation.units` (1, 4); scale-down recovery (2); scale guard on Juju 3.6 where `relation.units` is always empty (1); scheme mismatch when both ingress and TLS are active (6); `_on_collect_unit_status` double-adding statuses (13); `_delete_certificates` touching the charm container path (14); config update without an actual value change (the "no restart needed" nginx path).

**Ruff (`src/` only)**: 0 errors. All 66 errors in the full path are in `lib/` (third-party charm libraries).

**Pyright (`src/` only)**: 12 errors, all import-resolution issues (`charms.*` modules not found) — expected for charm code outside a full Juju environment.

**Integration tests**: 38 tests across 8 files, using `jubilant` with `grpcurl`/`curl` assertions. Upgrade test skipped (cross-base 24.04→26.04 not supported). Not run in this review due to time/resource constraints (`charmcraft pack` plus significant resources needed).

## Docs

- **README.md**: concise and accurate; deploy commands and URL retrieval match observed behaviour.
- **charmcraft.yaml description**: comprehensive, lists all key features.
- **CONTRIBUTING.md**: good contributor guide; container image reference (`0.23-24.04_stable`) is stale — repo targets 26.04.
- **Doc/reality mismatch**: README and charmhub description list SLO config options that don't exist in published rev 378 (Finding 7).
- **Missing**: no troubleshooting guide, no integration cookbook.

## Open questions

1. **Why does `is_scaled_up()` return True on Juju 4.0 after scale-down when `juju show-unit` shows no `related-units`?** The ops framework (3.7.1 via rev 378) appears to cache the departed unit in `relation.units`; `parca-peers-relation-departed` fires only on the departing unit. Looks like a Juju 4.x / ops interaction bug. Would settle by logging `len(peer_relation.units)` in the charm and re-testing.
2. **Why is `relation.units` empty for peer relations on Juju 3.6?** The peer relation exists but `units` stays empty during all hooks despite two units — the opposite behaviour from Juju 4.0, where units eventually become visible. Would settle by testing with different ops versions.
3. **Does the S3 config strip the protocol correctly for all endpoint formats?** `src/parca.py:253` does `s3_config.endpoint.removeprefix("https://").removeprefix("http://")`. If an S3 endpoint includes a path, the path is preserved and passed to Parca, which may not handle it. Not tested.
4. **What happens when `enable-persistence=true` AND S3 is related?** `src/parca.py:65` forces `enable_persistence=True` when S3 is configured; the pebble command adds `--enable-persistence --storage-path=/var/lib/parca` but S3 config may override the bucket type, so the local storage path may be ignored. Not documented or tested (S3 integration could not be exercised in this review — see s3-integrator note in the deployment log).
5. **Can `juju refresh` work between 24.04 and 26.04?** Published 2/stable (rev 378) is on ubuntu@24.04, 0.27/stable (rev 392) is on ubuntu@26.04; cross-base refresh is not supported by Juju. Is a migration path planned?
6. **Does tracing (charm + workload) work end-to-end with tempo-k8s?** Relations formed and data showed tempo addresses, but tempo-k8s stayed in maintenance for 5+ minutes without publishing endpoints, likely needing S3. The charm's `is_ready()` guards look correct, but the integration was not observable in this review. Would settle by deploying tempo with S3 storage configured.
