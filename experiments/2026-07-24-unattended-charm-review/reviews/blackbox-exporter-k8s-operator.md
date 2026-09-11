# blackbox-exporter-k8s

A well-structured, cleanly-written k8s charm for Prometheus Blackbox Exporter that deploys and operates correctly out of the box. It follows COS conventions well: a unified reconciliation pattern (`_common_exit_hook`), a decent test suite, and a terraform module. But the charm's own relation library (`blackbox_probes.py`) has a critical multi-relation bug that silently drops probe modules from all but one provider, the `--web.external-url` flag is permanently empty because it's hardcoded at construction time, the catalogue integration never picks up the external URL after ingress changes (open issue #74), and two distinct config-validation gaps turn recoverable input errors into unhandled hook crashes. A maintainer should first fix the `_update_modules` overwrite bug and the two config-crash paths (`probes_file`, semantically-invalid `config_file`), then fix `--web.external-url` and the catalogue staleness, then close the CI gap that hides 6 pyright errors in `lib/`.

| | |
|---|---|
| Repo | canonical/blackbox-exporter-k8s-operator @ `b34ec47` (2026-07-01) |
| Charms | blackbox-exporter-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), charmhub 0.28/stable rev 71 (HEAD is `b34ec47`, 2026-07-01; rev 71 is older, built from `77de287`, 2026-04-17). Also attempted concierge-k8s-4 (Juju 4.0.5) but base ubuntu@26.04 not supported on that controller. Deployed 4 times total: bare charm, multi-integration with traefik+prometheus+loki+certs, and catalogue+tls+traefik |
| Reviewed | 2026-07-28 |

## What it does

Deploys Prometheus Blackbox Exporter (v0.28.0) on Kubernetes, exposing a metrics endpoint and `/probe` endpoint for blackbox probing over HTTP(S), DNS, TCP, ICMP, gRPC, and SSH. Integrates with the COS stack: Prometheus (self-metrics + probes scrape jobs), Grafana (dashboards), Loki (log forwarding), Traefik (ingress), and Tempo (charm tracing). Supports probe configuration via Juju config (`config_file`, `probes_file`) and dynamically via the `probes` relation through the `blackbox_exporter_probes` interface. Also supports service mesh, catalogue, and TLS certificate transfer.

## Deployment log

```bash
# ===== Deploy 1: bare charm, Juju 4.x — failed (base not supported) =====
juju switch concierge-k8s-4
juju add-model rv-blackbox-4
juju deploy blackbox-exporter-k8s --channel 0.28/stable --trust -m rv-blackbox-4
# ERROR: the charm defined bases "ubuntu@26.04" not supported
# → Model destroyed.

# ===== Deploy 2: bare charm, Juju 3.6 =====
juju switch concierge-k8s-3
juju add-model rv-blackbox-3
juju deploy blackbox-exporter-k8s --channel 0.28/stable --trust -m rv-blackbox-3
# Deployed rev 71 on ubuntu@26.04/stable → active/idle in ~30s

# Config test: invalid YAML → blocked
juju config blackbox-exporter-k8s config_file="invalid: : yaml"
# → blocked "Failed to load config; invalid YAML"

# Config reset → recovered to active
juju config blackbox-exporter-k8s config_file=""
# → active/idle

# Probes file config (valid) → active
juju config blackbox-exporter-k8s probes_file='scrape_configs: [{"job_name":"test_http_probe","params":{"module":["http_2xx"]},"static_configs":[{"targets":["http://example.com"]}]}]'
# → active/idle

# Scale up → active, scale down → active
juju scale-application blackbox-exporter-k8s 2  # both active
juju scale-application blackbox-exporter-k8s 1  # active

# Traefik integration
juju deploy traefik-k8s traefik --channel latest/candidate --trust
juju relate blackbox-exporter-k8s:ingress traefik
# → both active/idle, traefik proxying

# Relation removal → recovered
juju remove-relation blackbox-exporter-k8s:ingress traefik
# → active/idle

# Action: show-config → returns default config yaml
juju run blackbox-exporter-k8s/0 show-config --wait=2m

# Kill workload process: Pebble auto-restarted, charm stayed ActiveStatus
kubectl exec ... -c blackbox -- sh -c "kill -9 \$(pgrep -f blackbox_exporter)"

# ===== Deploy 3: full integration test (rv-be-deep) =====
juju add-model rv-be-deep
juju deploy blackbox-exporter-k8s --channel 0.28/stable --trust
# → active/idle in ~30s

# Deploy integration partners
juju deploy traefik-k8s traefik --channel latest/candidate --trust
juju deploy prometheus-k8s prometheus --channel 3.11/stable --trust
juju deploy loki-k8s loki --channel 3.7/stable --trust
juju deploy self-signed-certificates --channel latest/stable

# Relate all integrations (4 concurrent)
juju relate blackbox-exporter-k8s:ingress traefik
juju relate blackbox-exporter-k8s:self-metrics-endpoint prometheus:metrics-endpoint
juju relate blackbox-exporter-k8s:logging loki
juju relate blackbox-exporter-k8s:receive-ca-cert self-signed-certificates:send-ca-cert

# All apps active/idle. Loki Pebble log forwarding confirmed via pebble plan.
# Traefik proxying confirmed: metrics accessible through traefik.
# Prometheus scrape job confirmed in prometheus.yml.

# Remove ingress → charm recovered to active (web.external-url reverted)
juju remove-relation blackbox-exporter-k8s:ingress traefik
# → active. Service restarted.

# Re-add ingress → charm recovered to active
juju relate blackbox-exporter-k8s:ingress traefik
# → active. But --web.external-url stayed empty (bug, see Findings).
# Also: catalogue relation data still shows internal URL, never updated (bug, see Findings).

# ===== Deploy 4: catalogue + TLS + traefik (rv-be-deep2) =====
juju add-model rv-be-deep2
juju deploy blackbox-exporter-k8s --channel 0.28/stable --trust
# → active/idle in ~30s

# Confirmed --web.external-url empty via kubectl exec:
# root ... blackbox_exporter --config.file=/etc/blackbox_exporter/config.yml
#   --web.listen-address=:9115 --web.external-url=

# Deploy catalogue (needed dev/edge for ubuntu@26.04), traefik, self-signed-certificates
juju deploy catalogue-k8s catalogue --channel dev/edge --trust
juju deploy traefik-k8s traefik --channel latest/candidate --trust
juju deploy self-signed-certificates --channel latest/stable

# Relate catalogue BEFORE ingress → catalogue gets internal URL
juju relate blackbox-exporter-k8s:catalogue catalogue:catalogue
# Catalogue app data shows: url=http://blackbox-exporter-k8s-0.blackbox-exporter-k8s-endpoints...
# (internal k8s service URL)

# Then relate ingress → external URL becomes available
juju relate blackbox-exporter-k8s:ingress traefik
# Traefik URL: http://10.43.45.0/rv-be-deep2-blackbox-exporter-k8s
# BUT: --web.external-url still empty in running process
# BUT: catalogue relation still shows internal URL (never updated)

# Relate TLS
juju relate blackbox-exporter-k8s:receive-ca-cert self-signed-certificates:send-ca-cert
# → active; no visible change (receive-ca-cert is for charm-tracing only)

# Config test: valid YAML but invalid blackbox structure
juju config blackbox-exporter-k8s config_file='{"not_modules": {"http_2xx": {"prober": "http"}}}'
# → ERROR "hook failed: config-changed" (see Findings)
# Recovery: --reset config_file + juju resolved

# Config test: non-existent prober module (accepted gracefully)
juju config blackbox-exporter-k8s config_file='{"modules":{"bad_probe":{"prober":"nonexistent"}}}'
# → active — blackbox lazily validates modules at probe time, not config time

# Remove application teardown
juju remove-application blackbox-exporter-k8s --force --no-wait
# → Clean removal: statefulset scaled to 0, no errors

# ===== Failure injections in rv-be-deep =====

# Invalid cpu config
juju config blackbox-exporter-k8s cpu="not-a-number"
# → blocked "Failed obtaining resource limit spec: Invalid limits spec: ..."
# Recovery: juju config --reset cpu (setting to "" does NOT recover)

# Invalid probes_file
juju config blackbox-exporter-k8s probes_file='{invalid yaml'
# → ERROR "hook failed: config-changed" — unhandled exception (see Findings)

# Kill pod (simulates node failure)
kubectl delete pod blackbox-exporter-k8s-0
# → pod recreated, new IP, charm recovered to active/idle

# Kill workload process (during multi-relation state)
kubectl exec ... -c blackbox -- kill -9 $(pgrep -f blackbox_exporter)
# → Pebble auto-restarted immediately, charm stayed ActiveStatus

# Attempt probes self-relation
juju deploy blackbox-exporter-k8s be-prober --channel 0.28/stable --trust
juju relate be-prober:probes blackbox-exporter-k8s:probes
# ERROR: no relations found — both endpoints are `requires` (same role)
# The probes interface needs a provider charm (neither charm implements BlackboxProbesProvider)

# juju refresh: no newer revision available in 0.28 track (rev 71 on all channels)
```

## Observed behaviour

- **Startup time**: ~30s from deploy to active/idle (Juju 3.6, k8s). Consistent across all deployments.
- **Resource usage**: Pod uses 38–43Mi memory (~1–2m CPU). Resource requests: 250m CPU, 200Mi memory. Limits: 1Gi memory (no CPU limit set). The 1Gi memory limit appears even though the `memory` config option defaults to empty string — `adjust_resource_requirements` generates a default limit from the empty/unset config.
- **Hook count**: Two config-changed hooks fire during initial deploy. pebble-ready fires twice (charm container then workload container). Two hot-reload attempts on initial start (reload is attempted, service restarts, reload is attempted again).
- **Config push ordering**: `_common_exit_hook` at `src/charm.py:224-238` correctly calls `push_config()` before `update_layer()`. The config file is written before the service starts via `replan()`.
- **`push_config` `PathError` risk**: `push_config` at `src/blackbox.py:214` calls `self._container.pull(self._config_path).read()`, which raises `PathError` if the file doesn't exist. On first deploy the config file does not exist yet, but `_common_exit_hook` catches only `ConfigUpdateFailure`, not `PathError`. In practice this hasn't triggered — the container image apparently has a default config file at that path — but it is a latent crash path.
- **Ingress and `--web.external-url`**: After relating to traefik, the `--web.external-url` flag in the running process is always empty. Confirmed live: `ps aux` shows `--web.external-url=` with no value. `WorkloadManager` is constructed with `web_external_url=""` (hardcoded at `src/charm.py:71`) and this value is never updated. Metadata/scrape configs use `_external_url` correctly via the property, but the Blackbox Exporter process itself never sees the external URL. PIDs change after relation updates (service restarts) but the flag stays empty.
- **Catalogue integration**: Deployed catalogue before ingress → catalogue relation data shows internal k8s URL (`http://blackbox-exporter-k8s-0.blackbox-exporter-k8s-endpoints...svc.cluster.local:9115/`). After connecting traefik ingress (external URL `http://10.43.45.0/rv-be-deep2-blackbox-exporter-k8s`), the catalogue data never updates — still shows the internal URL. `CatalogueItem` is created once in `__init__` with `self._external_url` at construction time and never updated on ingress change. This matches open issue #74.
- **Config validation asymmetry**: `config_file` with invalid YAML → blocked with clear message. `config_file` with valid YAML but blackbox-invalid structure (missing `modules` key) → error state with no message. `probes_file` with invalid YAML → error state with no message. Only `config_file` YAML parse errors get proper handling; everything else crashes the hook.
- **Service restart on relation change**: After adding/removing ingress, process PIDs change → service is restarted. After killing workload process, Pebble auto-restarts immediately (new PIDs). After killing the pod (`kubectl delete pod`), new pod gets a new IP and charm recovers to active. All restart scenarios handled correctly.
- **TLS integration (`receive-ca-cert`)**: Related successfully with self-signed-certificates, charm stayed active. No visible effect — this relation is consumed by `ops_tracing` for charm-to-Tempo TLS, not workload TLS.
- **Catalogue-k8s base availability**: `catalogue-k8s` does not publish `latest/stable` for `ubuntu@26.04`; had to use `dev/edge`. Ecosystem issue, not a charm bug, but operators would hit it.
- **Terraform channel validation**: The `dev/` prefix requirement in `terraform/variables.tf:16-18` would block deployment from `0.28/stable` or any other non-dev track. `terraform/outputs.tf:10-18` also omits `provide-cmr-mesh`, `charm-tracing`, `receive-ca-cert`, `service-mesh`, `require-cmr-mesh`.
- **Loki log forwarding**: Confirmed working. The Pebble plan includes a `log-targets` section forwarding all service logs to `loki-0.loki-endpoints.rv-be-deep.svc.cluster.local:3100/loki/api/v1/push` with appropriate Juju topology labels.
- **Prometheus scrape integration**: Confirmed working. `prometheus.yml` contains the self-metrics scrape job targeting the blackbox exporter service, plus alert rules.
- **File permissions**: Config file at `/etc/blackbox_exporter/config.yml` is `rw-r--r-- root:root` (644). Fine.
- **Pod restart recovery**: Deleting the pod → new pod with new IP → charm recovered to active/idle. Pebble websocket errors logged during restart (expected — connection closed while a hook was running).
- **Multi-relation stress**: 4 concurrent integrations (traefik, prometheus, loki, self-signed-certificates) all active simultaneously. No cross-interference observed.
- **Probes relation self-test**: Cannot self-relate two blackbox-exporter-k8s charms because both have `probes` as `requires` endpoints; no charm in the test environment implements `BlackboxProbesProvider`. The multi-relation `_update_modules` bug is therefore latent in practice — it only triggers when multiple provider charms relate.
- **Juju 4.x incompatibility**: The charm requires `ubuntu@26.04` base, which is not supported on the Juju 4.0.5 controller in this environment. Controller limitation, not a charm bug.

## Findings

### `_update_modules` overwrites modules from all but the last relation
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/blackbox_exporter_k8s/v0/blackbox_probes.py:734`
- **Evidence**: `blackbox_scrape_modules = databag.dict(exclude_unset=True)["scrape_modules"]` — assignment (`=`) instead of merge. Compare `_update_probes()` at line 689, which correctly uses `scrape_probes.extend(relation_scrape_probes)`. The `errors` accumulation is correct (uses `.append()` inside the loop).
- **Impact**: When multiple charms relate to blackbox-exporter over the `probes` relation, only the last relation's modules survive — all other providers' custom modules are silently discarded.
- **Fix**: Replace `=` with `blackbox_scrape_modules.update(...)`.
- **Linter rule**: "Assignment (=) in loop body where an accumulation pattern (.update()/.extend()) is expected" — AST check for reassignment of a loop-accumulator variable whose RHS doesn't reference itself.

### Invalid `probes_file` causes error state instead of blocked
- **Severity**: high
- **Kind**: bug
- **Where**: `src/scrape_config_builder.py:85`, `src/charm.py:295-301`
- **Evidence**: Observed live: `probes_file='{invalid yaml'` causes `hook failed: "config-changed"` (error state). Root cause: the `probes_scraping_jobs` property calls `ScrapeConfigBuilder.build_probes_scraping_jobs()`, which calls `yaml.safe_load(file_probes)` at `scrape_config_builder.py:85`. Bad YAML raises `yaml.YAMLError`, which is not caught by `_common_exit_hook`'s `try/except ConfigUpdateFailure` because the YAML parse happens inside `MetricsEndpointProvider`'s own config-changed handler, not inside `_common_exit_hook`.
- **Impact**: An operator providing invalid `probes_file` YAML gets an unexplained error state; the workload keeps running but the hook fails permanently. Recovery requires `juju config --reset probes_file` + `juju resolved`.
- **Fix**: Wrap the `yaml.safe_load` call in `build_probes_scraping_jobs` with try/except, or validate `probes_file` YAML in `_common_exit_hook` before `MetricsEndpointProvider` processes it.
- **Linter rule**: "`yaml.safe_load` on user-provided config must be wrapped in try/except" — mechanically checkable.

### Valid-YAML-but-blackbox-invalid `config_file` causes error state
- **Severity**: high
- **Kind**: bug
- **Where**: `src/blackbox.py:234-239` (`restart_service()`), `src/charm.py:226-235` (`_common_exit_hook` exception handling)
- **Evidence**: Observed live: `config_file='{"not_modules": {"http_2xx": {"prober": "http"}}}'` → `hook failed: "config-changed"`. The config is valid YAML so `build_config()` accepts it, but blackbox can't start without a `modules` key. The service restart raises an unhandled exception; `_common_exit_hook` only catches `ConfigUpdateFailure`.
- **Impact**: A syntactically-correct but semantically-invalid blackbox config produces an unhelpful error state with no message, unlike a bad-YAML `config_file` which gives a clear `BlockedStatus`. Recovery requires `--reset` + `juju resolved`.
- **Fix**: Catch `ChangeError` (and other Pebble exceptions) in `reload()`/`restart_service()` and convert to `ConfigUpdateFailure` with a descriptive message; alternatively validate presence of the `modules` key in `build_config()`.
- **Linter rule**: not mechanically checkable.

### `--web.external-url` flag always empty
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:71` (WorkloadManager construction), `src/blackbox.py:152` (layer command)
- **Evidence**: `WorkloadManager` is constructed with `web_external_url=""` hardcoded. `_blackbox_exporter_layer()` reads `self._web_external_url`, always `""`. Confirmed live via `kubectl exec`/`ps aux` after ingress connect: `--web.external-url=` empty. Confirmed again after remove/re-add ingress (PIDs changed 351→376, flag still empty). The `_external_url` property (`src/charm.py:248-252`) is used correctly elsewhere (scrape configs) but never passed to `WorkloadManager`.
- **Impact**: Blackbox Exporter's own UI/error-message links point to the internal URL rather than the external one when accessed through traefik.
- **Fix**: Update `WorkloadManager._web_external_url` before `update_layer()`, pass the current external URL as a parameter to `_blackbox_exporter_layer()`, or make it a property reading from the charm's `_external_url`.
- **Linter rule**: not mechanically checkable.

### Catalogue integration never updates after ingress changes
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:143-148` (CatalogueItem creation)
- **Evidence**: `url=self._external_url + "/"` evaluated once at `__init__`. Confirmed live: catalogue related before traefik shows internal URL `http://blackbox-exporter-k8s-0.blackbox-exporter-k8s-endpoints.rv-be-deep2.svc.cluster.local:9115/`; after relating traefik (external URL `http://10.43.45.0/rv-be-deep2-blackbox-exporter-k8s`), catalogue data still shows the internal URL. `_handle_ingress` (line 174) calls `_common_exit_hook()` but never updates the `CatalogueItem`. Matches open issue #74.
- **Impact**: If catalogue is related before ingress, the Catalogue link is unreachable and stays that way even after ingress connects.
- **Fix**: Re-create the `CatalogueItem` on `_handle_ingress`, or make the URL a property that dynamically reads `_external_url`.
- **Linter rule**: not mechanically checkable.

### Tox static check excludes `lib/` — 6 pyright errors invisible to CI
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tox.ini:23` (static command)
- **Evidence**: `[testenv:static]` runs `pyright {[vars]all_path}`, expanding to `src/ tests/` only. Running `pyright lib/charms/blackbox_exporter_k8s/` directly reveals 6 errors: `Any` not defined (line 572), type mismatches on `ApplicationDataModel` constructor (lines 481-482), incompatible type for `dict.update()` (line 757). Tox `static` passes with 0 errors.
- **Impact**: Real type errors in the charm's own library are invisible to CI, giving developers false confidence.
- **Fix**: Add `{toxinidir}/lib` to `all_path`, or run a separate pyright pass over `lib/`.
- **Linter rule**: "tox static targets must cover all Python paths including lib/" — mechanically checkable.

### `tox.ini` references undefined `lib_path` variable — lib version bump check is a no-op
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tox.ini:24`, `[vars]` section (missing `lib_path` definition)
- **Evidence**: The static env's second command runs `git diff main --name-only {[vars]lib_path}`, but `lib_path` is never defined in `[vars]`. Substitution yields an empty string, so the loop iterates over no files.
- **Impact**: Library version (`LIBPATCH`/`LIBAPI`) bump enforcement is silently disabled; a contributor can edit `blackbox_probes.py` without bumping the version and CI won't catch it.
- **Fix**: Add `lib_path = {toxinidir}/lib` to `[vars]`.
- **Linter rule**: "tox variable references must resolve to defined variables" — mechanically checkable.

### `push_config` raises unhandled `PathError` on first deploy
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/blackbox.py:214`, `src/charm.py:228-232`
- **Evidence**: `self._container.pull(self._config_path).read()` raises `ops.pebble.PathError` if the file doesn't exist. `_common_exit_hook` catches only `ConfigUpdateFailure`. Not observed to fail in this review because the container image already has a default config file at that path — latent, unverified whether it's actually reachable.
- **Impact**: If the container image ever ships without a default config file, the first pebble-ready hook crashes unhandled.
- **Fix**: Guard `pull()` with a `PathError` catch, treating a missing file as "no current config, always push".
- **Linter rule**: "`container.pull()` calls in config push methods must be guarded with `PathError` catch" — mechanically checkable.

### Config reset requires `--reset`; empty string doesn't restore defaults
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:155-162`, Juju config schema
- **Evidence**: Observed live: after a bad `cpu` value, setting `cpu=""` left the charm blocked ("Failed obtaining resource limit spec: Invalid limits spec: {'cpu': '', 'memory': None}"). Only `juju config --reset cpu` restored active status.
- **Impact**: An operator trying to "undo" a bad value by setting an empty string stays blocked; they must discover `--reset`. The status message doesn't explain this.
- **Fix**: Treat empty string as "unset" in `_resource_reqs_from_config`, or document the recovery procedure in the config description.
- **Linter rule**: not mechanically checkable.

### `_set_probes_spec` assigns `databag` but never uses it
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/blackbox_exporter_k8s/v0/blackbox_probes.py:480-484`
- **Evidence**: `databag = ApplicationDataModel(...).dump(relation.data[self._charm.app])` — the return value is assigned but never read. Ruff F841. `.dump()` has a side effect (writing the relation databag); discarding the return value is misleading.
- **Impact**: If `.dump()` is ever refactored to be pure (no side effects), this silently breaks.
- **Fix**: Drop the assignment.
- **Linter rule**: "local variable assigned but never used" — ruff F841.

### `_type_convert_stored` uses `Any` without importing it
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/blackbox_exporter_k8s/v0/blackbox_probes.py:572`
- **Evidence**: `rdict = {}  # type: Dict[Any, Any]` — `Any` used in a type comment but not imported. Pyright reports `"Any" is not defined`.
- **Impact**: Breaks static analysis; would raise `NameError` under runtime type evaluation.
- **Fix**: `from typing import Any`, or drop the type comment.
- **Linter rule**: mechanically checkable (pyright reportUndefinedVariable).

### `modules()` has incompatible type for `.update()` call
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/blackbox_exporter_k8s/v0/blackbox_probes.py:757`
- **Evidence**: `modules.update(_type_convert_stored(self._stored.blackbox_scrape_modules))` — `_type_convert_stored` can return `list | Dict | Unknown`, but `dict.update()` expects an iterable of tuples. Pyright reports `reportArgumentType`.
- **Impact**: If `_stored.blackbox_scrape_modules` is corrupted into a list, this raises `ValueError` at runtime.
- **Fix**: Add a type guard before calling `.update()`.
- **Linter rule**: mechanically checkable (pyright reportArgumentType).

### Terraform module requires `dev/` channel prefix
- **Severity**: medium
- **Kind**: bug
- **Where**: `terraform/variables.tf:16-18`
- **Evidence**: `validation { condition = startswith(var.channel, "dev/") ... }` — forces `dev/`, but the charm is published on tracks `0.28`, `1`, `2`, and `dev`.
- **Impact**: Operators using the terraform module cannot deploy from stable tracks like `0.28/stable`; forced onto `dev/edge`.
- **Fix**: Remove or relax the validation.
- **Linter rule**: "Terraform channel validation must match published charm tracks" — not mechanically checkable.

### Double import of `Object` from `ops` and `ops.framework`
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/blackbox_exporter_k8s/v0/blackbox_probes.py:206,214`
- **Evidence**: `from ops import Object` and `from ops.framework import ... Object ...` — ruff F811.
- **Impact**: Confusing; second import shadows the first.
- **Fix**: Remove the redundant import.
- **Linter rule**: ruff F811.

### Deprecated pydantic `class Config` pattern used throughout
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/blackbox_exporter_k8s/v0/blackbox_probes.py:318,329,350,356`
- **Evidence**: `class Config: extra = "allow"` — pydantic V2 deprecated class-based config in favor of `model_config = ConfigDict(...)`. `DatabagModel` already uses `model_config` correctly; subclasses regress.
- **Impact**: Will break under pydantic V3.
- **Fix**: Replace with `model_config = ConfigDict(extra="allow")`.
- **Linter rule**: mechanically checkable.

### `__fields__` and `.dict()` deprecated pydantic attributes
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/blackbox_exporter_k8s/v0/blackbox_probes.py:274` (`__fields__`), line 734 (`.dict()`)
- **Evidence**: `cls.__fields__.items()`, `databag.dict(exclude_unset=True)` — both deprecated in pydantic V2 in favor of `model_fields`/`model_dump`.
- **Impact**: Will break under pydantic V3.
- **Fix**: Use `model_fields`/`model_dump`.
- **Linter rule**: mechanically checkable.

### `get_status` in `BlackboxProbesProvider` has dead code
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/blackbox_exporter_k8s/v0/blackbox_probes.py:534-535`
- **Evidence**: `error_messages = "; ".join(self._stored.errors)` is computed then discarded; `return BlockedStatus(f"Errors occurred in probe configuration")` has no placeholders. Ruff F841 + F541.
- **Impact**: The `BlockedStatus` message omits the actual error details, unlike `BlackboxProbesRequirer.get_status()` at line 654, which does include them.
- **Fix**: `return BlockedStatus(f"Errors occurred in probe configuration: {error_messages}")`.
- **Linter rule**: ruff F541 + F841.

### Terraform module missing relation outputs
- **Severity**: low
- **Kind**: docs
- **Where**: `terraform/outputs.tf:10-18`
- **Evidence**: `requires` output lists only `catalogue`, `ingress`, `logging`, `probes`, omitting `charm-tracing`, `receive-ca-cert`, `service-mesh`, `require-cmr-mesh`. `provides` output omits `provide-cmr-mesh`.
- **Impact**: Operators using terraform cannot easily wire up the missing relations.
- **Fix**: Add the missing endpoint names to the outputs.
- **Linter rule**: "Terraform provides/requires outputs must match charmcraft.yaml" — mechanically checkable.

### `_resource_reqs_from_config` may produce unintended memory limit
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:155-162`
- **Evidence**: `limits = {"cpu": ..., "memory": ...}` return `None` when unset; `adjust_resource_requirements` still generates a 1Gi memory limit. Observed on the running pod: 1Gi limit despite no config set.
- **Impact**: Generous limit for a process using ~38Mi; wasteful on constrained clusters, not harmful.
- **Fix**: Treat empty/None config as "no limit" explicitly.
- **Linter rule**: not mechanically checkable.

### `_handle_ingress` unconditionally calls `_common_exit_hook` on both `ready` and `revoked`
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:174-178`
- **Evidence**: Both `ingress.on.ready` and `ingress.on.revoked` always call `_common_exit_hook()`, triggering a full config rebuild/push/reload even on revoke.
- **Impact**: Unnecessary work, not harmful given the idempotent reconciliation pattern.
- **Fix**: Optional — could skip the hook if the URL hasn't actually changed.
- **Linter rule**: not mechanically checkable.

### Typos in library docstrings; no codespell CI target
- **Severity**: nit
- **Kind**: lint
- **Where**: `lib/charms/blackbox_exporter_k8s/v0/blackbox_probes.py:749` and other locations
- **Evidence**: "modueles" (line 749), "Blakcbox" (line 22). `pyproject.toml` lists `codespell` as a dev dependency but there is no tox target running it.
- **Fix**: Add a `tox -e spell` target and fix the typos.
- **Linter rule**: "Run codespell in CI" — mechanically checkable.

## Worth copying

- **`_common_exit_hook` unified reconciliation**: `src/charm.py:198-236`. All events (config-changed, pebble-ready, update-status, upgrade-charm, ingress changes, probes changes) funnel through a single idempotent handler, correctly ordered push_config → update_layer → reload.
- **Hot reload before restart**: `src/blackbox.py:240-255`. `reload()` tries `POST /-/reload` first, falling back to a full service restart only if hot reload fails.
- **Scenario-based state-transition tests**: `tests/unit/conftest.py`, `tests/unit/test_tracing.py`. `ExitStack` fixture composition, `testing.State`/`testing.Container`/`testing.Relation`, `context.run()` for explicit transitions — the modern ops testing pattern.
- **`is_ready` property encapsulation**: `src/blackbox.py:114-116`. Wraps `container.can_connect()`; every method checks it before operating.
- **Workload version detection**: `src/blackbox.py:129-140`. Parses `blackbox_exporter --version` with a regex and sets the workload version on pebble-ready.
- **Config diff before push**: `src/blackbox.py:212-216`. `push_config` only writes when the content actually differs, avoiding unnecessary writes/reloads.
- **`charmcraft.yaml` as single source of truth**: Integration tests read app name, resources, and metadata from `charmcraft.yaml` instead of hardcoding.
- **`justfile` with `import? 'charms.just'`**: Uses the shared observability team justfile with a fallback guard.
- **`timed_memoizer` for integration test caching**: `tests/integration/conftest.py:31-45`. Caches expensive setup (e.g. charm build) within a session.
- **Templated Grafana dashboards**: `src/grafana_dashboards/blackbox.json.tmpl` — uses Juju topology templating.
- **Alert rules with specific thresholds**: `src/prometheus_alert_rules/` — `probe_failure.rule`, `blackbox_missing.rule`, `ssl_expiration.rule`, `unit_unavailable.rule`.
- **Pebble log forwarding**: Confirmed working in live deployment; the workload's stdout/stderr is captured to Loki without extra charm code.

## Common-practice notes

- **Follows COS conventions**: `charmcraft.yaml` as metadata source, `lib/charms/` layout, `src/` charm code, `justfile` with `charms.just`, `uv` for packaging, `ops_tracing` for charm tracing.
- **`ops_tracing` vs `ops[tracing]`**: Uses `ops_tracing.Tracing` directly (`src/charm.py:155`) rather than the newer `ops[tracing]` extras pattern. `charm-tracing` and `receive-ca-cert` are wired up cleanly.
- **Library versioning**: `lib/charms/blackbox_exporter_k8s/v0/blackbox_probes.py` follows the standard `LIBID`/`LIBAPI`/`LIBPATCH` convention. `PYDEPS = ["pydantic"]` but `pydantic` is not listed directly in `charmcraft.yaml` build-packages/dependencies — pulled in transitively via `cosl`/`ops`.
- **No `StoredState` in charm.py**: main charm uses none; the library uses it for caching relation data (the `_update_modules` bug lives there).
- **No `defer()` usage**: charm reconciles eagerly in `_common_exit_hook`; generally fine for k8s where pebble-ready will re-fire.
- **Port handling**: uses `self.unit.set_ports(self._port)`, the modern API.
- **Probes interface design**: both `BlackboxProbesProvider` and `BlackboxProbesRequirer` exist in the library, but the charm implements only the Requirer; `probes` is a `requires` endpoint in `charmcraft.yaml`. Standard COS design, but means two blackbox-exporter charms can't relate to each other for probe exchange.

## Tests

- **Unit tests**: 29 tests, all passing (~2.1s). Mix of `unittest`/`Harness` (deprecated) and `pytest`/`scenario` (modern). Migration to scenario incomplete.
- **Coverage**: 73% overall (`src/blackbox.py` 74%, `src/charm.py` 68%, `src/scrape_config_builder.py` 100%).
- **Ruff**: 25 issues across `src/` and `lib/` combined (F841, F811, F541, D101/D106, I001, W291, D202, C901 in upstream libs); 0 issues in `src/` alone; 20 in `lib/charms/blackbox_exporter_k8s/`. 5-6 auto-fixable.
- **Pyright**: 0 errors on `src/`+`tests/` (what tox actually checks). 6 errors when run directly against `lib/charms/blackbox_exporter_k8s/` — invisible to CI (see Findings).
- **Tox config gaps**: `[testenv:static]` excludes `lib/`; `lib_path` referenced but undefined, making the lib version-bump check a silent no-op. `[testenv:interface]` exists but `tests/interface/` doesn't — running it fails with "no tests found" rather than a clear error.
- **Test warnings**: 444 warnings, mostly pydantic V2 deprecations (`__fields__`, `.dict()`) and ops `Harness` deprecation.
- **Coverage gaps relative to findings**:
  - `_update_modules` bug: `test_multiple_provider_relations` (`tests/unit/test_probes_requirer.py:227-257`) exercises `_update_probes` via `probes()` but never calls `modules()`, which would have caught the overwrite bug.
  - `push_config` `PathError` path untested (mocked in unit tests).
  - `_handle_ingress` on `revoked` untested.
  - `_on_upgrade_charm` untested in unit or integration tests.
  - `show-config` action failure paths untested.
  - Invalid `probes_file` error-state path untested.
- **Integration tests**: `test_charm.py` (traefik/ingress, OpsTest), `test_prometheus_integration.py` (OpsTest), `test_charm_tracing.py` (Tempo, jubilant), `test_service_mesh.py`. Mixed OpsTest/jubilant patterns; open issue #97 tracks migration. Assertions check actual behaviour (probe_success, scrape targets, trace ingestion), not just active/idle.
- **No spread tests**.
- **PYTHONPATH gotcha**: `tox.ini` sets `PYTHONPATH=.:lib:src`; running `uv run pytest tests/unit` without it fails with `ModuleNotFoundError: No module named 'blackbox'`. Not documented in `CONTRIBUTING.md`.

## Docs

- **README**: good overview, deployment instructions, config examples. The `charmcraft status` example is outdated (shows track "latest" with ubuntu 22.04; charm is now on ubuntu 26.04 with tracks 0.28/1/2/dev).
- **CONTRIBUTING.md**: standard COS guide. References `tox -e scenario`, which doesn't exist in `tox.ini` (scenario tests run under `unit`). Also references `tox -e interface`, whose directory doesn't exist. Doesn't mention the `PYTHONPATH` requirement.
- **Charmhub description**: matches README, clear and accurate.
- **Terraform module**: has auto-generated README docs; functional but has the `dev/` channel restriction and missing relation outputs (see Findings).
- **Would a new operator succeed?**: yes, with minor friction. Basic deployment works, config options documented, probe format well-linked to upstream. The catalogue bug, empty `--web.external-url`, `probes_file` crash, and terraform restriction could cause confusion downstream.

## Open questions

1. Why doesn't the Juju 4.x controller support ubuntu@26.04? Likely a controller/cluster limitation, not a charm issue.
2. What is the exact exception raised for valid-YAML-but-blackbox-invalid config? The traceback wasn't visible in `debug-log`; `juju debug-code` or capturing hook output directly would confirm whether it's a Pebble `ChangeError`, a `ConnectionError` from hot-reload fallthrough, or something else.
3. Is the `push_config` `PathError` path actually reachable? Not observed in any of the four deployments; testing with a container image lacking a default config file would settle it. (unverified)
4. Does any charm in the wild currently provide modules via the `probes` relation? If none does, the `_update_modules` bug is latent; the commonly-used `_update_probes` path (which uses `.extend()`) is correct.
5. Why does `probes_file` crash but `config_file` (bad YAML) doesn't? `config_file` validation runs inside `_common_exit_hook`'s `ConfigUpdateFailure` handling; `probes_file` validation happens inside `MetricsEndpointProvider`'s own config-changed observer, which doesn't catch YAML errors.
6. Could the charm be tested on Juju 4.x? Not possible in this environment due to the controller's ubuntu@26.04 limitation.
