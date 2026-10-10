# tempo-operators (tempo-coordinator-k8s, tempo-worker-k8s)

Mature, well-structured pair of charms deploying Grafana Tempo on Kubernetes with the coordinated-workers pattern: the coordinator owns all external integrations and runs an nginx reverse proxy, the worker runs Tempo in a configurable role. Code is clean, tests pass (163 coordinator + 43 worker, 93%/94% coverage), lint/type checks are clean, and three full deploy/teardown cycles confirmed TLS, S3, ingress, scaling, and failure recovery all work. The charm is production-viable but has one data-destructive gap (unvalidated `retention-period`) and an intermittent hook-failure loop on worker scale-down that a maintainer should fix before wider rollout. It is also currently undeployable on Juju 4.x controllers lacking ubuntu@26.04 — worth flagging to users even if not fixable quickly.

| | |
|---|---|
| Repo | canonical/tempo-operators @ `85a88de` (2026-07-07) |
| Charms | tempo-coordinator-k8s, tempo-worker-k8s |
| Substrate | k8s |
| Deployed | yes, three times — rv-tempo (concierge-k8s-3, seaweedfs+S3, TLS, worker-querier scale-down), rv-tempo2 (concierge-k8s-3, seaweedfs+S3, TLS, Traefik ingress, worker scale-down), rv-tempo3 (concierge-k8s-3, seaweedfs+S3, TLS, Traefik ingress, metrics-generator worker, pod deletion recovery, S3 remove/re-add). All on 2.10/edge, rev 162 (coordinator) / rev 117 (worker). Also attempted on concierge-k8s-4 (juju 4.0.5): deploy impossible — neither 2.10/edge nor dev/edge (rev 160) publishes an ubuntu@24.04 build. |
| Reviewed | 2026-07-28 |

## What it does

Two k8s charms implementing Grafana Tempo:

- **tempo-coordinator-k8s** (`coordinator/`): manages S3 storage, TLS certificates, nginx reverse-proxy routing, trace ingestion endpoints (OTLP gRPC/HTTP, Jaeger, Zipkin), Grafana datasource/dashboard provisioning, Prometheus metrics, Loki logging, Blackbox probes, service mesh (Istio), ingress (Traefik + Istio), and a catalogue entry. Distributes generated Tempo config to workers over the `tempo-cluster` relation. Two workload containers: `nginx` and `nginx-prometheus-exporter`.
- **tempo-worker-k8s** (`worker/`): runs a single Tempo role (querier, query-frontend, ingester, distributor, compactor, metrics-generator, or the `all` meta-role for scalable-single-binary). Config comes exclusively from the coordinator via `tempo-cluster`. One `tempo` workload container plus a `wal` filesystem storage.

The coordinator is the primary subject; the worker is a thin wrapper around `coordinated_workers.worker.Worker`. Both use the `cosl.reconciler` `observe_events`/`all_events` pattern.

## Deployment log

**Model `rv-tempo`** on `concierge-k8s-3` (juju 3.6.25):

```bash
juju add-model rv-tempo
juju model-config default-base=ubuntu@26.04
juju deploy seaweedfs-k8s --channel edge --base ubuntu@24.04 --trust
juju deploy tempo-coordinator-k8s --channel 2.10/edge --trust --base ubuntu@26.04
juju deploy tempo-worker-k8s --channel 2.10/edge --trust --base ubuntu@26.04
juju integrate tempo-coordinator-k8s:s3 seaweedfs-k8s:s3-credentials
juju integrate tempo-coordinator-k8s:tempo-cluster tempo-worker-k8s:tempo-cluster
```

- seaweedfs-k8s at rev 9 (ubuntu@24.04, no 26.04 build). Coordinator rev 162, worker rev 117.
- Both charms reached **active/idle** within ~90s.

**Model `rv-tempo2`** on `concierge-k8s-3` (same deploy sequence, after rv-tempo was swept):

- Worker pod was killed and recreated during initial startup (agent lost → new pod) — normal k8s behaviour, but drove the worker into the ring-stabilization blocked cycle.
- Both charms reached active; coordinator ~90s, worker required 2–5 min for ring stabilization.

**TLS** (rv-tempo2):

```bash
juju deploy self-signed-certificates --channel 1/stable --base ubuntu@24.04
juju integrate tempo-coordinator-k8s:certificates self-signed-certificates:certificates
```

- Certs appeared at `/etc/nginx/certs/server.{cert,key}`; nginx reconfigured with `ssl` on all ports (16 `ssl_` directives). Coordinator stayed active.
- `list-receivers` action returned `https://` URL.
- `juju remove-relation` reverted nginx to non-SSL (0 `ssl_` directives); action returned `http://`. Cert directory was emptied but not removed. Coordinator stayed active throughout.

**Traefik ingress** (rv-tempo2):

```bash
juju deploy traefik-k8s --channel stable --trust
juju integrate tempo-coordinator-k8s:ingress traefik-k8s:traefik-route
```

- Traefik at rev 378 on ubuntu@26.04 — one of the few ecosystem charms with a 26.04 build.
- `list-receivers` returned `http://10.43.45.0:4318` (Traefik external IP) immediately after integration.
- Worker restarted for the config change; ring re-stabilization took ~60s.

**Worker role scaling** (rv-tempo, rv-tempo2):

```bash
juju deploy tempo-worker-k8s --channel 2.10/edge --base ubuntu@26.04 --trust tempo-worker-querier \
  --config role-all=false --config role-querier=true
juju integrate tempo-coordinator-k8s:tempo-cluster tempo-worker-querier:tempo-cluster
juju trust tempo-worker-querier --scope cluster
```

- Worker correctly required `--trust` for k8s resource patching; blocked with a clear message until trusted.
- After trust + integration: querier reached `active — querier ready.`
- nginx config updated with a new `worker-telemetry-proxy-tempo-worker-querier-0` upstream.

**Juju 4.x attempt** (concierge-k8s-4, juju 4.0.5):

- `juju model-config default-base=ubuntu@26.04` → rejected: base not supported.
- `juju deploy tempo-coordinator-k8s --channel 2.10/edge` → rejected: no ubuntu@24.04 build.
- `juju deploy tempo-coordinator-k8s --channel dev/edge` → also rejected: dev/edge is also 26.04-only (`juju info`: dev/edge rev 160, ubuntu@26.04).
- The charm is unavailable on any Juju 4.x controller lacking ubuntu@26.04 support. `2/stable` has 24.04 builds but predates the coordinated-workers split.

**Model `rv-tempo3`** on `concierge-k8s-3` (juju 3.6.25), used to deepen the review — same base deploy plus self-signed-certificates, traefik-k8s, and a metrics-generator worker:

- All three worker departures (querier ×2, metrics-generator ×1) succeeded without hook failure — confirming the intermittency of the hook-failure bug seen in rv-tempo/rv-tempo2.
- `juju debug-log --replay | grep -c '502\|Tracing collector'` returned **461** — the charm tracing 502 storm is larger than initially observed.
- Metrics-generator worker correctly entered `blocked: No prometheus remote-write relation configured on the coordinator` without ever starting the Tempo process.
- Worker pod deletion (`kubectl delete pod`) triggered clean recreation: unit went `maintenance (stop)` then recovered through the normal cycle (Pebble check DOWN → ring stabilization → active).
- Removing the S3 relation: coordinator blocked immediately, but the existing worker **stayed active** on its last valid config — correct behaviour. Re-adding S3 restored full function within ~2 min.

## Observed behaviour

### Status and performance
- Pebble services: coordinator runs `nginx` + `nginx-prometheus-exporter` (both active). Worker runs `tempo -target scalable-single-binary` when role=all, at `/bin/tempo -config.file=/etc/worker/config.yaml`.
- Memory at idle (`kubectl top`): coordinator ~66Mi, worker ~109Mi, seaweedfs ~53Mi.
- CPU at idle: coordinator ~479m (nginx + exporter + charm agent — high for doing nothing), worker ~10m.
- Tempo readiness check hits `http://...:3200/ready`; during ring stabilization (compactor waits 1–5 min) this returns 503, which the charm turns into `BlockedStatus`.

### Config mutations observed live
- `retention-period=-1`: accepted silently, produces `block_retention: "-1h"` in the worker's Tempo config (confirmed via `kubectl exec`). Tempo started successfully anyway. No validation, no blocked status.
- `retention-period=0`: accepted silently, produces `block_retention: "0h"` — tells the compactor to retain blocks for zero hours (immediate data loss on compaction). No validation.
- `role-all=true role-ingester=true`: correctly produces `blocked: cannot have more than 1 enabled role: ['all', 'ingester']`.

### Worker departure — hook failure (rv-tempo, rv-tempo2; NOT reproduced in rv-tempo3)
- In the first two deployments, `juju remove-application tempo-worker-querier --force` caused the coordinator's `tempo-cluster-relation-departed` hook to fail 3 times at ~10s intervals, then error with `hook failed: "tempo-cluster-relation-departed"`.
- In rv-tempo3, three separate worker removals (querier, metrics-generator, another querier) all completed without a hook failure — confirming the bug is **intermittent**, likely a race on whether the departing unit's databag is already empty when validation runs.
- `juju show-status-log` shows the hook running for only ~1s before failing — an unhandled exception in the `coordinated_workers` library validating an empty databag.
- After `juju resolve --no-retry`, the coordinator returned to active but left stale nginx upstream entries (`worker-telemetry-proxy-tempo-worker-querier-0`) pointing to a non-existent pod. The stale entry persists until the next `update-status` triggers `_reconcile` (up to 5 minutes) — during that window nginx DNS resolution for that server block fails, likely producing 502s for telemetry-proxy traffic. Confirmed cleaned up after later reconciliation.

### Charm tracing 502 error storm
- The coordinator's charm tracing sends its own traces through nginx to workers. When no worker is healthy (ring stabilization, restart, removal), nginx returns 502 and the tracing client retries aggressively at ERROR level.
- rv-tempo2: 60 lines of 502 errors during worker ring stabilization. rv-tempo3: 461 lines matching `502`/`Tracing collector` in one ~20-minute deploy/teardown cycle.
- Noisy, not harmful — the library buffers and retries — but generates ERROR-level spam on every worker restart or config change that restarts workers.
- Also observed: `no tracing relations: Tempo has no receivers configured` when the only tracing requirer is removed — a deliberate design choice, but it adds to the noise.

### TLS
- Confirmed in both rv-tempo2 and rv-tempo3: certs populate `/etc/nginx/certs/`, nginx gets `ssl_certificate`, `ssl_certificate_key`, `ssl_protocols` on all listeners. Removal reverts cleanly to non-SSL; cert directory stays but empty. `list-receivers` tracks scheme correctly. With Traefik active, the receiver URL switches from internal cluster IP to the Traefik external IP.

### S3
- seaweedfs integration: coordinator moved from `blocked: [s3] Missing S3 integration` to active within ~30s.
- Removing S3 while running (rv-tempo3): coordinator immediately blocked; the running worker stayed active on its last valid config — correct, since the coordinator doesn't push a config change while inconsistent. Re-adding S3 restored full function, worker restarted and recovered after ~60s.

### Process kill, pod deletion, recovery
- `pkill -9 nginx`: Pebble restarted within ~3s, coordinator stayed active (rv-tempo2, rv-tempo3).
- `pkill -9 tempo`: Pebble restarted within ~5s; readiness check went DOWN, worker blocked `Pebble check [ready] is 'DOWN'` for ~60s until ring stabilized, then recovered (rv-tempo2).
- `kubectl delete pod tempo-worker-k8s-0`: unit went `maintenance (stop)`, StatefulSet recreated the pod, unit ran the full startup cycle and recovered to active with no charm/juju error states (rv-tempo3).

### Nginx config
- Correctly generates upstream blocks for otlp-http, zipkin, tempo-http, tempo-grpc, and per-worker telemetry proxies.
- Duplicate map blocks: `map $status $loggable` and `map $http_x_scope_orgid $ensured_x_scope_orgid` each appear twice (`grep "map " | sort | uniq -c` → count 2). Root cause: `_build_nginx_config` in `coordinated_workers/coordinator.py:1118-1125` builds a second `NginxConfig` with `map_configs=config._map_configs` (already containing the defaults), and `NginxConfig.__init__` (external `charmlibs.nginx_k8s._config.py`) prepends the defaults again.
- Default `conf.d/default.conf` is untouched — the charm writes its config directly to `nginx.conf`.

### 26.04 ecosystem friction
- Only traefik-k8s (rev 378) among the tested related charms has a 26.04 build. seaweedfs-k8s and self-signed-certificates both needed `--base ubuntu@24.04`.
- 2.10 track is 26.04-only, blocking deployment on Juju 4.x controllers without 26.04 support.
- `2/stable` has 24.04 builds (rev 143 coordinator, rev 93 worker) but predates the coordinated-workers architecture.

### Refresh test
- Not possible within 2.10: stable/candidate/beta/edge all publish identical revisions (162/117). No intra-track refresh path to test.

## Findings

### `retention-period` accepts negative and zero values, producing data-destructive or malformed Tempo config
- **Severity**: critical
- **Kind**: bug / ux
- **Where**: `coordinator/src/charm.py:616-619`, `coordinator/src/tempo.py:270`, `coordinator/src/tempo_config.py:232`
- **Evidence**: `return cast(int, self.config["retention-period"])` at `charm.py:619` — no validation. `block_retention=f"{self._retention_period_hours}h"` at `tempo.py:270` formats the raw int with an `h` suffix. The Pydantic model at `tempo_config.py:232` declares `block_retention: str` with no validator. `retention-period=-1` produces `block_retention: "-1h"`; Tempo started successfully with it (confirmed via `kubectl exec`). `retention-period=0` produces `block_retention: "0h"` — the compactor deletes blocks immediately after compaction. Charm stayed `active` in both cases.
- **Impact**: `retention-period=0` causes silent data loss; `-1` puts Tempo in an undefined state. No blocked status alerts the operator. Open issue #362 tracks the `0` case but proposes treating it as "infinite retention," which would make this even less obvious.
- **Fix**: add `minimum: 1` to the config option in `charmcraft.yaml`, plus a validator on the `Compaction` model (`tempo_config.py:227`) rejecting non-positive values. If `0` should mean "infinite" per #362, omit `block_retention` entirely rather than emitting `"0h"`.
- **Linter rule**: "config option with type=int has no `minimum` constraint and feeds directly into a workload config value" — mechanically checkable from `charmcraft.yaml` plus a trace of the config variable's usage.

### Coordinator hook-failure loop on worker departure leaves stale nginx config (intermittent)
- **Severity**: high
- **Kind**: bug
- **Where**: `coordinated_workers` library, `tempo-cluster-relation-departed` hook
- **Evidence**: In rv-tempo and rv-tempo2, removing `tempo-worker-querier` caused the `tempo-cluster-relation-departed` hook to fail 3 times (`juju show-status-log`), with `invalid databag contents: failed to validate databag: {}` — the departing worker's databag was empty and the library's Pydantic model rejected it with an unhandled exception. After `juju resolve --no-retry` the coordinator recovered but nginx retained a stale upstream. In rv-tempo3, three consecutive worker removals all succeeded, confirming the bug is intermittent — likely a race on whether the departing unit's databag has cleared before validation runs.
- **Impact**: On trigger, the coordinator enters an error loop on a normal operation (worker scale-down). The stale nginx upstream causes DNS resolution failures for that server block, which can surface as 502s on telemetry-proxy traffic until the next `update-status` (up to 5 minutes).
- **Fix**: the library's relation-departed handler should tolerate empty/partial databags from departing units — skip validation for departing units and just clear cached state.
- **Linter rule**: not mechanically checkable from charm source alone — bug lives in the external `coordinated_workers` package.

### Worker reports BlockedStatus during normal Tempo startup/recovery
- **Severity**: medium
- **Kind**: ux / bug
- **Where**: `coordinated_workers/worker.py:276` (external package)
- **Evidence**: When the Pebble ready check is DOWN — normal during Tempo's 1–5 minute ring-stabilization — `Worker._on_collect_status` appends `BlockedStatus(f"Pebble check [{self.readiness_check_name}] is 'DOWN'.")`. Observed during worker config changes (S3 reconnect, TLS changes), process restart (`pkill tempo`), and initial startup; in all cases the worker recovered to active on its own.
- **Impact**: operators may attempt unnecessary corrective action on a status that implies intervention is needed. It can also mask genuine blocked states in the log output, though the charm's own statuses take priority in the final `collect_status` result (per `worker/src/charm.py:74` comment).
- **Fix**: change the status to `WaitingStatus` or `MaintenanceStatus` — a transient DOWN readiness check means "not ready yet," not "operator must act."
- **Linter rule**: not mechanically checkable — requires understanding of the workload's startup semantics.

### Ingress redirect middleware applied to gRPC routes
- **Severity**: medium
- **Kind**: bug
- **Where**: `coordinator/src/charm.py:699-725`
- **Evidence**: `self.tempo.all_ports.items()` at line 699 iterates over all ports including gRPC (otlp_grpc, jaeger_grpc, tempo_grpc). When `self.ingress.scheme == "https"`, the `redirect_middleware` (HTTP `redirectScheme`) is applied to every router at lines 714 and 724-725, with no protocol filter. gRPC uses HTTP/2 and cannot follow HTTP redirects.
- **Impact**: with both TLS and Traefik ingress enabled, gRPC trace-ingestion endpoints get a useless redirect middleware, and gRPC clients cannot send traces through the ingress.
- **Fix**: filter `self.tempo.all_ports` to exclude gRPC protocols before adding the redirect middleware, reusing `_is_protocol_grpc()` (already used for the `h2c` handling at lines 728-733).
- **Linter rule**: "HTTP redirect middleware added to all entrypoints including gRPC" — mechanically checkable if `all_ports` is used unfiltered for a gRPC-aware middleware.

### Stale nginx upstreams after worker departure
- **Severity**: medium
- **Kind**: bug
- **Where**: coordinator's generated nginx config, follow-on effect of the hook-failure finding above
- **Evidence**: after the querier worker was removed and the coordinator recovered via `juju resolve`, the nginx config still contained `upstream worker-telemetry-proxy-tempo-worker-querier-0 { server ... }` pointing at the removed worker, observed for over 20 seconds post-recovery.
- **Impact**: nginx DNS resolution fails for the stale server block until the next `update-status` fires `_reconcile` (up to 5 minutes), during which telemetry-proxy traffic could see errors.
- **Fix**: fixing the relation-departed crash (above) would let reconciliation happen immediately instead of waiting for update-status.
- **Linter rule**: not mechanically checkable.

### Charm tracing produces ERROR-level 502 log storm during worker restarts
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `coordinator/src/charm.py:106-117` (`_setup_charm_tracing`)
- **Evidence**: rv-tempo2 logged 60 lines of `ERROR ... Tracing collector rejected our data, e.code=502 resp='<html>...502 Bad Gateway...</html>'` during ring stabilization; rv-tempo3 logged 461 matching lines in one ~20-minute cycle. Charm tracing sends to `https://localhost:4318/v1/traces`, which routes through nginx to the worker; a DOWN worker readiness check produces nginx 502s that the tracing library retries at ERROR level.
- **Impact**: every worker restart or config change bursts ERROR-level logs that look like a serious failure but are a normal transient, obscuring genuine problems.
- **Fix**: send charm self-tracing directly to localhost, bypassing nginx, or log 502s at DEBUG/WARNING instead of ERROR, or suppress the error during known-transient windows.
- **Linter rule**: not mechanically checkable.

### Charm unavailable on Juju 4.x controllers without ubuntu@26.04
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `charmcraft.yaml` platform declaration (both charms)
- **Evidence**: `concierge-k8s-4` (juju 4.0.5) rejected `default-base=ubuntu@26.04` outright. 2.10/edge and dev/edge (rev 160) both publish only ubuntu@26.04; `2/stable` is a different architecture (pre-split, no coordinated-workers).
- **Impact**: operators on Juju 4.x controllers without 26.04 support cannot deploy this charm at all; the only workaround is a controller with 26.04 support, effectively locking the charm to Juju 3.6.
- **Fix**: publish 24.04 builds alongside 26.04 in the 2.10 track, or ensure `dev/edge` provides one.
- **Linter rule**: not mechanically checkable from a single-architecture charm.

### Worker `SERVICE_START_RETRY_STOP = 60s` may be shorter than Tempo ring stabilization
- **Severity**: medium
- **Kind**: bug / performance
- **Where**: `worker/src/tempo.py:28`
- **Evidence**: `SERVICE_START_RETRY_STOP = tenacity.stop_after_delay(60)` gives the worker 60 seconds to restart Tempo. Observed live: compactor ring stabilization takes 1–5 minutes (`waiting until compactor ring topology is stable min_waiting=1m0s max_waiting=5m0s`), during which `/ready` returns 503. Issue #348 reports this causing permanent failure after model migration (unverified — not tested directly in this review).
- **Impact**: if the 60s retry window expires while Tempo is still stabilizing, the worker may enter a permanent maintenance/waiting state. Combined with the BlockedStatus-vs-WaitingStatus finding above, the operator sees a confusing "blocked" message for a transient condition.
- **Fix**: raise `SERVICE_START_RETRY_STOP` to at least 360s (covering the 5-minute max wait), or check Pebble process status independently of the readiness endpoint and report `WaitingStatus` instead of timing out.
- **Linter rule**: not mechanically checkable.

### Duplicate `map` blocks in generated nginx config
- **Severity**: low
- **Kind**: bug
- **Where**: `coordinated_workers/coordinator.py:1118-1125` (external package), triggered from `coordinator/src/charm.py:276-279`
- **Evidence**: the running coordinator's nginx config shows `map $status $loggable` and `map $http_x_scope_orgid $ensured_x_scope_orgid` twice each (`grep "map " | sort | uniq -c` → 2). `_build_nginx_config` passes `config._map_configs` (already containing the two defaults) into a new `NginxConfig`, whose `__init__` (`charmlibs.nginx_k8s._config.py`) prepends the same defaults again.
- **Impact**: nginx tolerates the duplication (no error), but the config is bloated and confusing to debug; if the maps ever diverged, nginx would silently use the last one.
- **Fix**: deduplicate maps when merging `NginxConfig` objects, or pass `map_configs=[]` for the worker-telemetry-proxy `NginxConfig` since the defaults are already present.
- **Linter rule**: not mechanically checkable from charm source.

### `subprocess.getoutput` is deprecated in Python 3.12+, targeted for removal
- **Severity**: low
- **Kind**: lint / future-compat
- **Where**: `coordinator/src/charm.py:12` (import), lines 809-810 (usage)
- **Evidence**: `from subprocess import CalledProcessError, getoutput` used in `is_workload_ready()` to run `curl` for the Tempo readiness check. `getoutput` is deprecated as of 3.12 and flagged for future removal; the charm targets Python 3.14 on ubuntu@26.04.
- **Impact**: if removed in a future Python release, `is_workload_ready()` breaks with an `ImportError`.
- **Fix**: replace with `subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()`.
- **Linter rule**: "uses deprecated `subprocess.getoutput`" — checkable with ruff or a custom AST check.

### README badges reference old/unmaintained repos
- **Severity**: nit
- **Kind**: docs
- **Where**: `coordinator/README.md`, `worker/README.md`
- **Evidence**: badges link to `canonical/tempo-coordinator-k8s-operator` and `canonical/tempo-worker-k8s-operator`; the actual repo is `canonical/tempo-operators`.
- **Impact**: badge links 404.
- **Fix**: update badge URLs to `canonical/tempo-operators`.
- **Linter rule**: "badge URL links to a different GitHub repo than the git remote" — mechanically checkable.

### `HACKING.md` references ubuntu@22.04 and the old single-charm architecture
- **Severity**: low
- **Kind**: docs
- **Where**: `coordinator/HACKING.md`
- **Evidence**: references `tempo-k8s_ubuntu-22.04-amd64.charm`, `tempo-image=grafana/tempo:2.4.0`, and a single-charm deploy command, none matching the current coordinator/worker split or ubuntu@26.04 base.
- **Impact**: a developer following it builds the wrong base and uses a years-old image.
- **Fix**: rewrite to show coordinator+worker deployment, the current base, and current OCI images.
- **Linter rule**: "HACKING.md references a base that doesn't match `charmcraft.yaml` platforms" — mechanically checkable.

### metrics-generator gets ActiveStatus instead of BlockedStatus when remote-write is missing (`all` role)
- **Severity**: low
- **Kind**: ux
- **Where**: `coordinator/src/charm.py:306-311`, `worker/src/charm.py:58-63`
- **Evidence**: with the `all` role active and no remote-write relation, the worker sets `ActiveStatus("metrics-generator disabled. No prometheus remote-write relation configured on the coordinator")`; the coordinator sets a similar `ActiveStatus`. The dedicated `metrics-generator` role correctly refuses to start (`worker/src/tempo.py:71-75`) and shows `BlockedStatus`, but the `all` role degrades to an informational `ActiveStatus`.
- **Impact**: an operator expecting metrics-generator to run gets no blocked status flagging the missing relation — easy to miss when the unit is otherwise `active`.
- **Fix**: consider whether the `all` role's metrics-generator subsystem deserves a more prominent status; this is a design tradeoff, not a clear-cut bug.
- **Linter rule**: not mechanically checkable.

### `restart()` correctly refuses to start metrics-generator without remote-write
- **Severity**: N/A — correct design, noted for completeness
- **Kind**: good-practice
- **Where**: `worker/src/tempo.py:71-75`
- **Evidence**: `restart()` checks `if "metrics-generator" in (roles or ()): if not self.cluster.get_remote_write_endpoints(): logger.error(...); return` before calling `super().restart()`. In rv-tempo3 the metrics-generator worker showed `blocked: No prometheus remote-write relation configured on the coordinator` with no `tempo` Pebble service ever started.
- **Impact**: avoids Tempo starting and immediately failing for lack of a remote-write target.
- **Linter rule**: not mechanically checkable — requires semantic understanding of the restart flow.

## Worth copying

- **Status precedence via `CollectStatusEvent`**: the worker sets its own status before delegating to `Worker.set_status(e)`, with the comment `# the worker will set its status after we've set ours, so in case of a conflict ours will prevail` (`worker/src/charm.py:56`) — correct pattern for status priority.
- **`can_connect()` guard before container filesystem access**: `are_certificates_on_disk` (`coordinator/src/charm.py:443`) checks `nginx_container.can_connect()` before `nginx_container.exists()`.
- **Graceful degradation with clear blocked messages**: `blocked: [s3] S3 not ready (probably misconfigured).`, `blocked: [consistency] Missing any worker relation.`, `blocked: Node offline: no role assigned. Please configure this worker to enable a role.` — specific and actionable.
- **Config distribution via the `coordinated-workers` package**: worker config generation, role consistency checking, and ready detection are delegated to a standalone PyPI package; the charm itself is mostly integration wiring.
- **Comprehensive Terraform module**: `terraform/` deploys the full microservices topology (7 worker apps, one per role) with per-role unit counts, storage directives, and anti-affinity, documented with `tfdocs`.
- **Pydantic-typed Tempo config**: `tempo_config.py` models the full Tempo YAML with `Field` aliases bridging Juju naming (`bucket_name` → `bucket`) to Tempo's upstream keys. `_strip_default_port` (`tempo_config.py:272`) fixes a real upstream Go client IPv6-parsing bug.
- **GitHub issue tracking for TODOs**: `charm.py:793` — `# TODO: publish information about TLS also if the protocol_type is gRPC. See https://github.com/canonical/tempo-operators/issues/241.`
- **Guarding against inconsistent-state event processing**: `coordinator/src/charm.py:264` — `if not self.coordinator.can_handle_events: return`.

## Common-practice notes

- **Reconciler pattern**: `cosl.reconciler.observe_events`/`all_events` is the COS team's standard. `_reconcile` runs on every event including update-status, generating extra relation-changed events on related apps; the tradeoff is acknowledged in a code comment (`charm.py:876-878`).
- **`charmcraft.yaml` as single source of truth**: no separate `metadata.yaml` — modern standard.
- **Library layout**: libraries under `lib/charms/<name>/v<N>/`; owns `tempo_coordinator_k8s/v0/tracing.py` and `tempo_coordinator_k8s/v0/tempo_api.py`, both well documented.
- **Monorepo structure**: separate per-charm `charmcraft.yaml`, `tox.ini`, `pyproject.toml`, `uv.lock`, with a top-level `tox.ini`/`tests/` coordinating cross-charm integration tests — consistent with other Canonical observability monorepos.
- **ubuntu@26.04 base**: bleeding edge — most COS charms are on 24.04. Being first causes friction with ecosystem charms (seaweedfs-k8s, self-signed-certificates, s3-integrator) lacking 26.04 builds. Both 2.10 and `dev/edge` are confirmed 26.04-only via `juju info`.
- **`assumes: juju >= 3.6.0`**: consistent with `collect_unit_status`, secrets, and other modern `ops` features.
- **Library version-bump check**: the tox `static` environment runs `git diff main` to verify LIBPATCH/LIBAPI is bumped on library changes — good practice.

## Tests

### Unit tests (`tox -e unit`)
- Coordinator: 163 tests, all passing in 3.3s, 93% line coverage. Uncovered branches at `charm.py:93, 102, 347, 440-442, 494, 528-529, 534, 623, 629-635, 777->775, 800-812, 816, 1015->1020, 1020->1022` — mostly error paths and the `is_workload_ready()` curl invocation. `nginx_config.py` and `tempo_config.py` at 100%.
- Worker: 43 tests, all passing in 0.5s, 94% coverage. Uncovered branches at `tempo.py:71-75` (metrics-generator restart guard) and `tempo.py:83->85, 103` (juju topology addition for metrics-generator). 917 deprecation warnings from libraries (Pydantic v2 migration warnings via `cosl`).
- Interface tests: 2 passed, 1 skipped (`test_grafana_source.py`). Validate databag contents for tempo-cluster, grafana-source, and grafana-datasource-exchange relations.

### Integration tests (`tests/integration/`)
- 13 modules: distributed deployment, monolithic, TLS, self-monitoring (3 variants), self-tracing, tracing integration, ingress, telemetry correlation, worker deployment, juju-doctor probes, tracing mesh (xfailed — issue #331). Use `jubilant` against a real Tempo deployment with `seaweedfs-k8s` as S3 backend.
- Did not run — requires a real cluster and significant resources.

### Lint and static checks
- `ruff check`: 0 errors, 0 warnings on both charms' `src/`.
- `pyright`: 0 errors, 0 warnings, 0 informations on both charms' `src/` and `lib/charms/tempo_coordinator_k8s/`.
- Library version-bump check: passes.

### Coverage gaps relative to findings
- No test for `retention-period` boundary validation (negative/zero).
- No test verifying worker departure doesn't crash the coordinator's relation-departed handler.
- No test for `_reconcile` idempotency.
- No test for `is_workload_ready()`'s curl invocation, error handling, or TLS/non-TLS branches.
- No test that gRPC routes are excluded from the ingress HTTP redirect middleware.
- No test for charm tracing's handling of worker-down 502s.

## Docs

- Top-level README: brief description of the coordinated-workers pattern, links to discourse — thin but adequate.
- `coordinator/README.md`: badge URLs point to old repos; the "Usage" section shows a single `juju deploy` command with no mention of S3, workers, TLS, or the 26.04 base requirement — insufficient to deploy successfully from.
- `worker/README.md`: similarly terse, describes the role architecture but gives no deployment instructions.
- `coordinator/HACKING.md`: severely outdated (ubuntu@22.04, old image tags, pre-split architecture).
- Terraform READMEs (`terraform/README.md`, `coordinator/terraform/README.md`, `worker/terraform/README.md`): comprehensive, auto-generated via `tfdocs`.
- `CONTRIBUTING.md`: covers environment setup, OCI images, testing, PR guidelines.
- `charmcraft.yaml` descriptions: well-written for relations and config options; `role-X` options document mutual exclusivity clearly.
- Doc/reality gap: neither README mentions the ubuntu@26.04 base requirement, which is a hard requirement that errors on a default model.

## Open questions

1. **Post-migration recovery (issue #348)**: `juju migrate` was not tested. `SERVICE_START_RETRY_STOP = stop_after_delay(60)` gives Tempo only 60s to start against a 1–5 minute ring-stabilization window — consistent with #348's report of permanent maintenance state after migration, but not directly verified here (unverified).
2. **Multiple ingresses (issue #245)**: the charm blocks when both `ingress` and `istio-ingress` are active, with a message ("Remove one of the two") giving no guidance on which to keep. Not tested.
3. **Tempo 3.0 / Kafka migration (issue #333)**: Tempo 3.0 requires Kafka in distributed mode; the charm has no Kafka integration today.
4. **Tracing gRPC TLS information (issue #241)**: `get_receiver_url` strips the scheme for gRPC protocols, so requirer charms can't tell if TLS is required (tracked at `charm.py:793`).
5. **Stale nginx upstream window**: confirmed live, but exactly how long clients would see errors, and whether telemetry-proxy traffic is actually routed through the stale upstream during that window, was not measured.
6. **Charm tracing 502 volume**: is the error count fixed or proportional to restart duration? If a worker is down for 5 minutes, log volume could scale into the thousands.
7. **No 24.04 build anywhere in the coordinated-workers tracks**: confirmed via `juju info` that `dev/edge` (rev 160) is also 26.04-only. Unclear if there is a plan to add a 24.04 build.
