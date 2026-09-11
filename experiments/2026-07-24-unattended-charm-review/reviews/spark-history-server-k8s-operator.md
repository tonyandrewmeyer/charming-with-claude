# spark-history-server-k8s

A mature, cleanly-layered Kubernetes charm from Canonical's Data Platform team for Apache Spark History Server. It deploys successfully on both Juju 3.6 and Juju 4.0, and integrates cleanly with Loki (Pebble log forwarding), Prometheus (JMX scrape targets + alert rules), and Grafana (JVM dashboards). The architecture (context → managers → events → workload) is a good example to copy. But the reconcile loop is not idempotent: every hook — including routine `update-status` — unconditionally stops and restarts the workload, S3/Azure "status checks" make live API calls that can mutate storage (create buckets/paths) and block for tens of seconds on a dead endpoint, the S3 region is captured but never propagated into the Spark configuration, and there's a confirmed intermittent crash (JMX port re-bind race) on relation removal. A maintainer's first move should be fixing `HistoryServerManager.update()` to diff config before deciding to stop/restart, and separating the read-only credential check from the status path so `update-status` stops doing writes and 40-second blocking calls.

| | |
|---|---|
| Repo | canonical/spark-history-server-k8s-operator @ `1f906d1` (2026-07-21) |
| Charms | spark-history-server-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3: ch:3/stable rev 122 and 3/edge rev 131 (via refresh); concierge-k8s-4: ch:4/edge rev 133 |
| Reviewed | 2026-07-31 |

## What it does

Deploys Apache Spark History Server on Kubernetes. Requires an object storage backend (S3 via s3-integrator or Azure Storage via azure-storage-integrator) to read completed Spark application event logs. Optionally integrates with traefik-k8s for ingress, Oathkeeper or oauth2-proxy for auth, Loki for log forwarding, Prometheus for metrics, and Grafana for dashboards. The charm writes `spark-properties.conf` into the workload container, manages TLS truststores for S3 connections, and configures an authorization servlet filter when an auth proxy is active.

## Deployment log

### concierge-k8s-3 (Juju 3.6.25) — primary test environment

**Basic deploy** (ch:3/stable rev 122):
```
juju add-model rv-spark-deep
juju deploy spark-history-server-k8s --channel 3/stable
```
Reached `BlockedStatus("Missing relation with storage")` in ~3 minutes (unit `waiting` ~90s then `blocked`).

**S3 + minio happy path**:
```
juju deploy minio --channel ckf-1.9/stable
juju config minio access-key=minioadmin secret-key=minioadmin
juju deploy s3-integrator --channel 1/stable s3
juju config s3 endpoint=http://<minio-ip>:9000 bucket=test-bucket path=test-path
juju run s3/0 sync-s3-credentials access-key=minioadmin secret-key=minioadmin
juju integrate spark-history-server-k8s s3
```
Bucket and path were created in minio, history-server started, charm reached `ActiveStatus`. Spark properties were written correctly. Confirmed: the S3 secret key appears in `spark-properties.conf` in plaintext, and `spark.hadoop.fs.s3a.endpoint.region` is absent.

**Ingress integration** (traefik-k8s latest/stable rev 377):
```
juju deploy traefik-k8s --channel latest/stable traefik
juju integrate spark-history-server-k8s traefik
```
The spark charm correctly sent ingress relation data (port 18080, host, IP). Traefik itself failed with a Kubernetes RBAC error (`services is forbidden` — the traefik service account could not list services at cluster scope) — a traefik/environment issue, not a spark bug. The spark charm handled the incomplete ingress gracefully; status remained `active` (S3 was working).

**Scale up/down**:
```
juju scale-application spark-history-server-k8s 2    # both units active with S3
juju scale-application spark-history-server-k8s 1    # scaled back, no errors
```

**Refresh** (3/stable rev 122 → 3/edge rev 131):
```
juju refresh spark-history-server-k8s --channel 3/edge
```
`upgrade-charm` fired implicitly (no explicit handler), followed by config-changed. The new pod took ~5 minutes to come up due to slow image pull from `registry.jujucharms.com`. Once ready, the charm reconciled and reached `active`.

**Kill workload process**:
```
kubectl exec spark-history-server-k8s-0 -c spark-history-server -- kill -9 <java_pid>
```
Pebble restarted the Java process automatically (new PID). Juju status stayed `active`.

**Config change with garbage `log-level`** (Juju 3 and Juju 4):
```
juju config spark-history-server-k8s log-level="INVALID"
```
Accepted without error. The config-changed hook ran but the value was silently ignored — the charm never reads `self.charm.config["log-level"]`. Status unchanged.

**Config change triggers full stop/restart** (confirmed via pebble changes):
```
juju config spark-history-server-k8s authorized-users="alice,bob"
```
Each config change produced this pebble change sequence: `Stop service "history-server"` → `Execute command "rm"` ×2 → `Restart service "history-server"`. This happens on every hook, regardless of whether config actually changed.

### concierge-k8s-4 (Juju 4.0.5)

**Basic deploy** (ch:4/edge rev 133):
```
juju add-model rv-spark-j4deep
juju deploy spark-history-server-k8s --channel 4/edge
```
Reached `BlockedStatus("Missing relation with storage")` in under a minute — faster than Juju 3 (likely pod-scheduling difference).

**S3 integration impossible on Juju 4**: s3-integrator 2/stable (rev 544) fails with `BlockedStatus("Invalid config(s): 'credentials'")` — Juju 4 injects a `credentials` config option of type `secret`, but s3-integrator's `config.yaml` doesn't define it. s3-integrator 1/stable works but requires the older v0 s3 library handshake. This is an s3-integrator CharmHub publication issue, not a spark-history-server bug.

No behavioural difference from Juju 3 was observed for the base blocked case.

### Loki / Prometheus / Grafana integration (concierge-k8s-3, ch:3/stable rev 122)

```
juju deploy loki-k8s --channel 2/stable --trust
juju deploy prometheus-k8s --channel 2/stable --trust
juju deploy grafana-k8s --channel 2/stable --trust
juju integrate spark-history-server-k8s loki-k8s
juju integrate spark-history-server-k8s prometheus-k8s
juju integrate spark-history-server-k8s grafana-k8s
```
All three integrations established cleanly while the charm was `blocked` (no S3):

- **Loki (LogForwarder)**: Pebble `log-targets` populated with the Loki push API endpoint (`http://loki-k8s-0.loki-k8s-endpoints.rv-spark-v2.svc.cluster.local:3100/loki/api/v1/push`) and Juju topology labels (`juju_application`, `juju_model`, `juju_model_uuid`, `juju_unit`, `product`). Uses Juju ≥3.4 Pebble log forwarding, not the older promtail-based `LogProxyConsumer`.
- **Prometheus (MetricsEndpointProvider)**: Scrape jobs at `*:9101` (JMX exporter) and `*:9102` (JMX CC), with three alert rules (`Spark History Server Missing`, `JvmMemory Filling Up`, `Spark History Server Threads Dead Locked`), correctly labelled with topology.
- **Grafana (GrafanaDashboardProvider)**: `jvm-metrics.json` (120KB) was published only after the relation settled and the charm reached `active` (initially `{}` while blocked).

### Full stack deployed (concierge-k8s-3, ch:3/stable rev 122)

minio + s3-integrator alongside loki/prometheus/grafana. After integrating S3, the full stack reached `active`: spark-history-server `active` (Java PID 64, ~305MB RSS, JMX on 9101); loki-k8s `active` forwarding logs from all Pebble services; prometheus-k8s `active` scraping JMX; grafana-k8s `active` with the JVM dashboard available.

Pebble plan observed via `kubectl exec`:
```yaml
services:
  history-server:
    startup: disabled
    environment:
      SPARK_DAEMON_JAVA_OPTS: -javaagent:/opt/spark/jars/jmx_prometheus_javaagent-0.20.0.jar=9101:/etc/spark/conf/jmx_prometheus.yaml
      SPARK_HISTORY_OPTS: ""
      SPARK_PROPERTIES_FILE: /etc/spark/conf/spark-properties.conf
log-targets:
  loki-k8s/0:
    type: loki
    location: http://loki-k8s-0.loki-k8s-endpoints.rv-spark-v2.svc.cluster.local:3100/loki/api/v1/push
    services: [all]
```

### Failure injection — junk S3 credentials

```
juju run s3/0 sync-s3-credentials access-key=badkey secret-key=badsecret
```
Correctly transitioned to `BlockedStatus("Invalid object storage credentials or permission issue. Please check logs.")`. However the service was stopped **before** credential verification (`HistoryServerManager.update()`: `stop()` → write config → `verify()` → conditional `start()`). On bad credentials, the service stops and stays stopped.

### Five rapid config changes
```bash
for i in 1 2 3 4 5; do
  juju config spark-history-server-k8s authorized-users="user${i}"
done
```
Each triggered the full stop → rm×2 → restart Pebble cycle. Service survived all five (the JMX port race is intermittent and did not fire here).

### Relation removal — two attempts, one crash

**Attempt 1** (earlier session): removing the S3 relation crashed history-server with `java.net.BindException: Address already in use` on JMX exporter port 9101. The Java process exited with code 134 (SIGABRT), pebble raised `ChangeError` ("exited quickly with code 134"), and the unit went into `error` state, with every subsequent `update-status` re-triggering the failure (recovery required manual `juju resolve`).

**Attempt 2** (later session): clean removal — service stopped, charm went to `BlockedStatus("Missing relation with storage")`, no crash. The race is intermittent (see the non-idempotent-restart finding).

## Observed behaviour

**Workload identity**: The container runs as root (uid=0). The charm declares `PEBBLE_USER = ("_daemon_", "_daemon_")` in `constants.py:8`, used for TLS truststore chown operations.

**Pebble plan / OCI image typo**: The base layer provides two services: `history-server` (startup: disabled, `/bin/bash /opt/pebble/history-server.sh`) and `sparkd` (startup: enabled, `/bin/bash /opt/pebble/sparkd.sh [ sleep ]`). The base layer has a typo: `SPARK_PROPERTIES_FILE: /etc/spark8t/conf/spark-defaults.conf` (`spark8t` instead of `spark`). The charm overrides this so it's harmless. `sparkd` has `on-success: shutdown` and `on-failure: shutdown` — if it exits, it never restarts, and observed `sparkd` was `inactive` while `history-server` was `active`.

**Full config when S3 active** (via `kubectl exec`):
```
spark.eventLog.dir=s3a://test-bucket/test-path
spark.eventLog.enabled=true
spark.hadoop.fs.s3a.access.key=minioadmin
spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider
spark.hadoop.fs.s3a.connection.ssl.enabled=false
spark.hadoop.fs.s3a.endpoint=http://10.152.183.111:9000
spark.hadoop.fs.s3a.path.style.access=true
spark.hadoop.fs.s3a.secret.key=minioadmin
spark.history.fs.logDirectory=s3a://test-bucket/test-path
```
`spark.hadoop.fs.s3a.secret.key` is plaintext. No `spark.hadoop.fs.s3a.endpoint.region` — the region bug is confirmed in live output.

**No Pebble health checks** are defined in the layer.

**Restart on every hook** (confirmed via pebble changes): every config-changed hook produces Stop → rm×2 → Restart. `HistoryServerManager.update()` unconditionally calls `self.workload.stop()` (line 126) then potentially `self.workload.start()` (line 158). The JMX exporter port (9101) re-bind carries an intermittent race — confirmed once as a real crash (`java.net.BindException`, pebble `ChangeError` code 134).

**Loki LogForwarder**: correctly configured Pebble log forwarding; `log-targets` populated with the Loki endpoint and topology labels; continued working after S3 relation removal/re-integration since it's independent of the history server's running state.

**Prometheus scrape targets**: statically configured at charm construction and published on pebble-ready, independent of S3 state — though metrics aren't actually scrapeable until history-server (and its embedded JMX exporter) is running.

**Grafana dashboards delayed**: relation data was `{}` while blocked; `jvm-metrics.json` (120KB, LZMA-compressed) appeared only after the charm reached `active`. Appears to be a race between `GrafanaDashboardProvider`'s initial scan and relation establishment: the provider publishes on `leader_elected` (fires before the grafana relation exists) and `relation_created` (fires when grafana first deploys but before the charm may have finished initialising). The dashboard appears after a later config-changed/update-status triggers `_update_all_dashboards_from_dir`.

**Java classpath contains the OCI-image typo even when the charm runs**: the JVM `-cp` includes `/etc/spark8t/conf/` alongside `/opt/spark/jars/*`. Harmless today since the charm overrides `SPARK_PROPERTIES_FILE`, but a latent defect in the image.

**Azure verify is more disciplined than S3 verify**: `AzureStorageManager.verify()` (line 88-99) calls `get_account_information()` — a read-only auth check — before mutating (`get_or_create_container`, `ensure_path`). `S3Manager.verify()` (line 107-151) calls `list_buckets()`, which can be expensive on accounts with many buckets. Both still create resources from status checks.

**`sparkd` dies permanently on any failure** — see above; not monitored by the charm.

**`upgrade-charm` fires implicitly**: no explicit observer is registered, but the implicit install/start/config-changed cycle on pod restart re-reconciles the charm anyway.

**No actions defined**: `juju actions spark-history-server-k8s` returns "No actions defined".

**Both Juju 3 and Juju 4 identical** for the base blocked case; no Juju-version-specific code paths found.

**`juju refresh` works**: new revision downloaded, pod recreated, hooks run, charm reconciles to active; took ~5 minutes, mostly image-pull latency.

**S3 verify called twice per reconciliation hook** (confirmed via log timestamps): once from `HistoryServerConfig._s3_conf` (line 84), once from `get_app_status()` (line 47). Against a live minio backend each call is ~1s; against a dead endpoint each call blocks ~38-40s (TCP connect timeout + boto3 retry), giving ~80s per hook and, with cascading relation-changed hooks (7 verification attempts observed over ~4 minutes, per timeline below), several minutes of unresponsive charm.

```
12:40:17 - S3 credentials-changed event
12:40:56 - 1st S3 error (~39s, from _s3_conf verify)
12:41:30 - 2nd S3 error (~34s, from get_app_status verify)
12:42:07 - 3rd S3 error (next hook cycle, ~37s)
12:42:46 - 4th S3 error (next hook cycle, ~39s); status: "Invalid object storage credentials"
12:43:21 - 5th S3 error
12:44:01 - 6th S3 error
12:44:41 - 7th S3 error
```

## Findings

### `HistoryServerManager.update()` restarts the workload on every hook — non-idempotent, with a confirmed crash on relation removal
- **Severity**: high
- **Kind**: bug
- **Where**: `src/managers/history_server.py:126-128` (and `:208-236`), `src/workload.py:85-103`
- **Evidence**: `update()` unconditionally calls `self.workload.stop()`, then conditionally calls `self.workload.start()`, which calls `self.container.restart(...)` (Pebble stop-then-start). Confirmed: every `juju config` change produces `Stop service "history-server"` → `Restart service "history-server"` in pebble changes, even when configuration hasn't actually changed. On relation removal in an earlier session this produced a real crash: JMX exporter re-bind on port 9101 raced with the old process's shutdown, `java.net.BindException: Address already in use`, Java exited with code 134 (SIGABRT), pebble raised `ChangeError` ("exited quickly with code 134"), and the unit stuck in `error` state with every subsequent `update-status` re-triggering the failure until manual `juju resolve`. A later relation-removal attempt did not reproduce it — the race is intermittent.
- **Impact**: Every `update-status` (5 min), config change, and relation-changed event unnecessarily restarts the Java process — roughly 288 unneeded restarts/week — with a standing risk of the JMX port-conflict crash that requires manual operator intervention to clear.
- **Fix**: Compare rendered config against the current config file before deciding to restart. Prefer `replan()` with a new layer over `stop()`+`restart()`. If a restart is genuinely needed, add a delay between stop and start. Move the verify check before `workload.stop()` so the service isn't stopped to discover credentials are invalid.
- **Linter rule**: "`update()` calls `stop()` unconditionally without checking if restart is needed" — not mechanically checkable.

### `get_app_status()` makes live S3/Azure API calls on every hook, blocking ~40s per call against a dead endpoint — confirmed in deployment
- **Severity**: high
- **Kind**: performance
- **Where**: `src/events/base.py:47-49`
- **Evidence**: `S3Manager.verify()` calls `s3.list_buckets()`, optionally creates a bucket, and creates a `.keep` object; called from `get_app_status`, which wraps every hook including `update-status` (every 5 minutes). Observed: with an unreachable S3 endpoint each `list_buckets()` call blocked ~38-40s; with two verify calls per hook, each relation-changed hook took ~80s, and cascaded relation-changed hooks (7 verification attempts) produced ~4-5 minutes of unresponsive charm. Even on the fast path (local minio) this costs ~2s of wasted time per hook.
- **Impact**: Every 5 minutes the charm blocks on network I/O; a transient S3 outage flips the charm to `BlockedStatus` even with valid credentials, and status checks mutate storage (see next finding).
- **Fix**: Cache the verification result, invalidating only when relation data changes. Add a shorter timeout to the boto3 client used in the status path.
- **Linter rule**: "`get_app_status` calls methods that perform I/O" — heuristic requiring `verify()`/network calls inside status methods.

### S3 region is not propagated to Spark configuration
- **Severity**: high
- **Kind**: bug
- **Where**: `src/managers/history_server.py:87-119` (`_s3_conf` property)
- **Evidence**: `_s3_conf` builds Spark configuration keys including `spark.hadoop.fs.s3a.endpoint` but never sets `spark.hadoop.fs.s3a.endpoint.region`, even though the region is available via `s3.connection_info.region` (`src/core/domain.py:50`) and is used by the boto3 client in `S3Manager.verify()` (`src/managers/s3.py:127`). Confirmed absent from the live-rendered `spark-properties.conf`.
- **Impact**: AWS S3 requires the correct signing region. Without `fs.s3a.endpoint.region`, Spark's S3A connector may use the wrong signing algorithm, causing `301` redirects or `SignatureDoesNotMatch` for buckets outside `us-east-1` — likely the cause behind open issue #133. The README's claim that the charm defaults to `us-east-1` for S3 requests is true only for the boto3 verify client, not for Spark's own Hadoop configuration — a doc/reality mismatch.
- **Fix**: Add `"spark.hadoop.fs.s3a.endpoint.region": s3.connection_info.region or "us-east-1"` to `_s3_conf`, or omit the key when region is unset.
- **Linter rule**: "S3 connection info `.region` is present but not propagated to Spark configuration keys" — mechanically checkable.

### `HistoryServerManager.update()` stops the service before verifying credentials
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/history_server.py:208-236`
- **Evidence**: `update()` calls `self.workload.stop()` unconditionally (line 208), then builds/writes config and resets TLS, and only afterwards verifies credentials (lines 224-227); if verification fails, the method returns without calling `start()`. Observed: `juju run s3/0 sync-s3-credentials access-key=badkey ...` stopped the running history-server and never restarted it.
- **Impact**: A transient S3 outage or a credential typo takes the history server down unnecessarily, even though the service was previously healthy.
- **Fix**: Move the verify check to before `self.workload.stop()`; only stop/restart if config has actually changed.
- **Linter rule**: "`stop()` called unconditionally before `verify()` in `update()`" — mechanically checkable.

### `verify()` in the status-check path has side effects (creates buckets and paths)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/s3.py:107-151`, `src/managers/azure_storage.py:79-98`
- **Evidence**: `S3Manager.verify()` calls `self.get_or_create_bucket(s3)` and `self.ensure_path(s3)`, both of which mutate the bucket. `AzureStorageManager.verify()` similarly calls `get_or_create_container()`/`ensure_path()`. Both run on every `get_app_status()` call.
- **Impact**: A status check should be read-only; creating buckets/`.keep` objects on every `update-status` is wasteful and could trigger provider rate limits.
- **Fix**: Split "verify credentials work" (read-only: `list_buckets`/`get_account_information`) from "ensure resources exist" (creation). Call only the read-only check from status; call the creation path only from reconcile.
- **Linter rule**: not mechanically checkable — requires understanding that `verify()` is called from a status method.

### S3 secret key written to config file in plaintext
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/history_server.py:78` (`_s3_conf` property)
- **Evidence**: `"spark.hadoop.fs.s3a.secret.key": s3.connection_info.secret_key` writes the secret key directly into `/etc/spark/conf/spark-properties.conf`; confirmed in the live deployment.
- **Impact**: Any process with filesystem access to the container can read the S3 secret key. This is the standard way Spark consumes S3 credentials, but Juju secrets exist to avoid exactly this pattern; other data-platform charms (e.g. postgresql-k8s) use Juju secrets for credentials.
- **Fix**: Consider Juju secrets plus an environment-variable injection instead of a plaintext config entry, or at minimum restrict file permissions.
- **Linter rule**: "Secret key value in relation data written to a config file" — mechanically checkable by scanning for `.secret_key`/`.access_key` in file-write paths.

### Azure storage config written even when credentials are invalid
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/history_server.py:137-157`
- **Evidence**: `_azure_storage_conf` (line 137) does not call `azure_storage.verify()`, unlike `_s3_conf` (line 84). Config is written (line 135) before the verify guard (lines 151-155), so Azure config keys (including the secret key) are written to `spark-properties.conf` even with invalid credentials, before the charm correctly avoids starting.
- **Impact**: Stale Azure credentials remain in the config file between hooks; the S3/Azure asymmetry is a maintenance hazard.
- **Fix**: Add a verify call to `_azure_storage_conf` for symmetry with S3, or move the config write to after the verify guard.
- **Linter rule**: not mechanically checkable.

### Config write happens before the verify check
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/history_server.py:217-227`
- **Evidence**: Config file write (line 217) and environment variable setup (lines 218-220) happen before the S3/Azure verify check (lines 224-227).
- **Impact**: A transient failure leaves the config file in a state inconsistent with the running (or stopped) service.
- **Fix**: Write config only after the verify guard, or only when the service will actually be started.
- **Linter rule**: not mechanically checkable.

### `_on_config_changed` duplicates status computation instead of using `@compute_status`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/events/history_server.py:59-71`
- **Evidence**: The handler manually sets `self.charm.unit.status`/`self.charm.app.status` via `self.get_app_status(...)` with the same arguments `@compute_status` would use, while every other change handler uses the decorator.
- **Impact**: If status logic changes, this path could diverge silently; extra duplication burden.
- **Fix**: Add `@compute_status` and remove the manual status-setting lines.
- **Linter rule**: "Handler calls `self.charm.unit.status = self.get_app_status(...)` instead of using `@compute_status`" — mechanically checkable.

### "Gone" event handlers inconsistently skip `@compute_status`
- **Severity**: low
- **Kind**: lint
- **Where**: `src/events/s3.py:46-61`, `src/events/azure_storage.py:47-62`, `src/events/ingress.py:78-117,122-137,142-157`
- **Evidence**: Five `_on_*_gone`/`_on_*_removed`/`_on_*_revoked` handlers manually compute status, passing `None` explicitly for the removed relation — correct, but fragile since each must be kept in sync with `get_app_status`'s signature individually.
- **Impact**: Maintenance burden across five call sites.
- **Fix**: Document the `None` pattern as intentional, or have `get_app_status` read from context so it self-invalidates on relation-departed.
- **Linter rule**: "Handler named `_on_*_gone`/`_on_*_removed` should use `@compute_status` or justify why not" — mechanically checkable.

### No explicit `upgrade-charm` event handler
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/charm.py` — no `self.framework.observe(self.charm.on.upgrade_charm, ...)`
- **Evidence**: The charm relies on the implicit pod-recreation cycle after `juju refresh`; the hook fires via Juju dispatch but no handler is registered. Reconciliation still works because install/config-changed/start re-run on the new pod.
- **Impact**: No hook for upgrade-specific logic (data migration, schema updates); works today but is fragile.
- **Fix**: Add an `upgrade-charm` handler that at minimum logs the event or re-runs `update(...)`.
- **Linter rule**: "Charm lacks `upgrade_charm` event observer" — mechanically checkable.

### No actions defined
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py` — no `actions.yaml`, no `@action` handlers
- **Evidence**: `juju actions spark-history-server-k8s` returns "No actions defined."
- **Impact**: No operator-triggered credential re-verify, restart, or config dump without waiting for `update-status` or editing config.
- **Fix**: Consider `get-spark-properties` and `reverify` actions.
- **Linter rule**: not mechanically checkable.

### `log-level` config option declared but never consumed
- **Severity**: low
- **Kind**: bug
- **Where**: `config.yaml:6-9`
- **Evidence**: `config.yaml` declares `log-level` (string, default `"info"`); no reference to `self.charm.config["log-level"]` exists in `src/`. Confirmed: changing it fires config-changed and an unnecessary restart, but has no effect (and accepts garbage values like `"INVALID"` without validation).
- **Impact**: Operators see a config option that appears functional but isn't; wastes a hook and triggers a needless restart.
- **Fix**: Either implement it (e.g. Spark's `spark.history.log.level` or JVM log level) or remove it; if consumed by the OCI image, document that.
- **Linter rule**: "Config option declared but never read in charm code" — mechanically checkable.

### `sparkd` pebble service has `on-failure: shutdown` — never restarts
- **Severity**: low
- **Kind**: ux
- **Where**: OCI image pebble layer (not charm source), confirmed via `pebble plan`
- **Evidence**: `sparkd` has `on-success: shutdown` and `on-failure: shutdown`; the charm only monitors `history-server`.
- **Impact**: If `sparkd` dies, it stays dead with no alerting.
- **Fix**: Remove the shutdown directives in the OCI image, or have the charm monitor `sparkd` health.
- **Linter rule**: not mechanically checkable.

### `s3-integrator` 2/stable incompatible with Juju 4
- **Severity**: low
- **Kind**: ux (environment issue)
- **Where**: n/a (external charm)
- **Evidence**: On concierge-k8s-4 (Juju 4.0.5), s3-integrator 2/stable (rev 544) reports `BlockedStatus("Invalid config(s): 'credentials'")` because Juju 4 injects a `credentials` secret-type config option that s3-integrator's `config.yaml` doesn't define.
- **Impact**: Operators on Juju 4 cannot use the recommended s3-integrator track from CharmHub.
- **Fix**: Not this charm's bug — fix belongs to s3-integrator's CharmHub publication.
- **Linter rule**: not established.

### Auth-proxy config threads `None` through methods that don't need it
- **Severity**: low
- **Kind**: bug
- **Where**: `src/core/context.py:50-53`
- **Evidence**: `authorized_users` returns `None` when no auth-proxy relation exists. `_auth_conf` (`src/managers/history_server.py:167`) correctly checks `if (users := self.authorized_users)` and skips the auth filter, but the `None` also flows into `_on_config_changed`/`get_app_status`, whose signatures don't use `authorized_users`.
- **Impact**: Confusing data flow across four method signatures; harmless in practice.
- **Fix**: Have `authorized_users` return `"*"` (all users) or have handlers that don't need it stop fetching it.
- **Linter rule**: not mechanically checkable.

### Grafana dashboards not immediately published on relation join
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/grafana_k8s/v0/grafana_dashboard.py:1187-1194` combined with `src/charm.py:57`
- **Evidence**: `GrafanaDashboardProvider` publishes on `leader_elected`, `upgrade_charm`, `config_changed`, `relation_created`. `leader_elected` fires before any grafana relation exists; `relation_created` may fire before the charm finishes initialising context. Observed: dashboard relation data was `{}` while blocked, populating only after the charm reached `active` via a later config-changed hook.
- **Impact**: Grafana may not see dashboards immediately on relation join; operators may wait for the next hook cycle.
- **Fix**: Explicitly call `_update_all_dashboards_from_dir()` after the grafana relation joins, or have the provider also observe `pebble_ready`.
- **Linter rule**: not mechanically checkable.

### `truststore_password` stored in plaintext in `/tmp/password`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/managers/tls.py:25-33`
- **Evidence**: Password written to `/tmp/password` with default (world-readable) permissions and passed as a CLI argument to `keytool`, visible in the process table. The code's own comment (line 23) acknowledges the pattern ("This could eventually go in a peer relation databag").
- **Impact**: Low risk since the truststore only protects public CA certificates, but a bad habit.
- **Fix**: Set `600` permissions; use `keytool`'s `-storepass:file`/`-storepass:env` instead of a CLI argument.
- **Linter rule**: not mechanically checkable.

### `cached_property` on `truststore_password` never invalidated
- **Severity**: nit
- **Kind**: bug
- **Where**: `src/managers/tls.py:25`
- **Evidence**: `@cached_property` decorates a method that reads from an external file (`/tmp/password`); if `/tmp` is cleared without a charm process restart, the cached value goes stale.
- **Impact**: Edge case — Pebble restarts also restart the charm process, so only relevant if `/tmp` is cleared independently.
- **Fix**: Use `@property` — the file read is cheap.
- **Linter rule**: "`@cached_property` on a method that reads from an external source" — mechanically checkable.

### `import_ca` catches `subprocess.CalledProcessError`, which is unreachable
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/managers/tls.py:6,57`
- **Evidence**: The `except` clause catches `(subprocess.CalledProcessError, ExecError)`, but `self.workload.exec()` raises `ops.pebble.ExecError` in K8s contexts, never `subprocess.CalledProcessError`.
- **Impact**: Dead code and a misleading import.
- **Fix**: Remove `subprocess.CalledProcessError` from the except clause and the `import subprocess`.
- **Linter rule**: "`except` clause includes exception type never raised by the try body" — mechanically checkable.

### Pebble base layer / OCI image contains `spark8t` typo
- **Severity**: nit
- **Kind**: lint
- **Where**: OCI image pebble layer (not charm source); also present in the JVM classpath (`-cp /etc/spark8t/conf/:/opt/spark/jars/*`)
- **Evidence**: `SPARK_PROPERTIES_FILE: /etc/spark8t/conf/spark-defaults.conf` and the equivalent classpath entry both reference `spark8t` instead of `spark`. The charm's override (`SPARK_PROPERTIES_FILE=/etc/spark/conf/spark-properties.conf`) makes this harmless today.
- **Impact**: Latent defect — if the charm ever needed to put JARs/classes on the classpath via its own config directory, they'd be silently ignored, since the typo'd path doesn't exist.
- **Fix**: Fix the typo in the rockcraft layer.
- **Linter rule**: mechanically checkable in the OCI image build pipeline.

### Test helper `set_s3_credentials` uses the Juju secrets API but is unused
- **Severity**: nit
- **Kind**: test-gap
- **Where**: `tests/integration/test_helpers.py:27-36`
- **Evidence**: `set_s3_credentials()` uses `juju.add_secret()`/`juju.grant_secret()` (the Juju 3.6+ credential-passing API for s3-integrator 2/stable), but no integration test calls it; all integration tests use s3-integrator 1/stable with action-based credential sync.
- **Impact**: Dead test code; if the charm is meant to support s3-integrator 2/stable, that path is untested.
- **Fix**: Add a test exercising s3-integrator 2/stable, or remove `set_s3_credentials`.
- **Linter rule**: "Function defined in `test_helpers.py` never called by any test" — mechanically checkable.

## Worth copying

- **Clean layered architecture**: `src/charm.py` → `src/events/` → `src/managers/` → `src/core/` → `src/common/`. Separation between context (state), managers (actions), events (triggers), and workload (substrate interaction) is clear and consistent.
- **`compute_status` decorator pattern**: `src/events/base.py:66-81` wraps status computation after event handlers; `defer_when_not_ready` (`src/events/base.py:84-95`) is a clean companion. (`_on_config_changed` doesn't use it — see finding.)
- **Thorough `is_proxy_skipped` utility**: `src/common/utils.py:64-87`, 27 parametrized test cases (`tests/unit/test_component_s3.py:94-187`) covering CIDR notation, domain suffixes, empty values, case insensitivity, multiple entries. Exemplary defensive coding.
- **`object_storage` charmlib extraction**: S3/Azure requirer logic is a pip dependency (`object-storage-charmlib`) rather than a vendored charm lib — good pattern for shared infrastructure code.
- **Integration tests that assert on application behaviour**: `tests/integration/test_charm.py` runs a real Spark job, queries the History Server API, tests ingress proxying, and the auth servlet filter with specific HTTP status codes (403, 401, 500). Much more thorough than most charm integration suites.
- **`charmcraft.yaml` part composition**: three-part build (`poetry-deps`, `charm-poetry`, `files`) with comments citing the upstream charmcraft issues that motivated each workaround.
- **S3 path/bucket creation with `.keep` objects and tenacity polling**: `S3Manager.ensure_path()` creates a `.keep` object and polls until visible — 20 retries at 5s is generous but appropriate for eventually-consistent storage.
- **Loki `LogForwarder` integration is clean and idiomatic**: a single-line instantiation (`src/charm.py:39-41`) gets zero-config Pebble log forwarding to Loki with proper topology labels, confirmed working live. A pattern other charms should copy.

## Common-practice notes

- Follows data-platform conventions: `src/` split into `common/`, `core/`, `events/`, `managers/`; poetry for deps; tox for tasks; `concierge.yaml`/`spread.yaml` for CI; jubilant for integration tests; renovate for dependency updates.
- Drifts from the `tls-certificates` interface convention: handles S3 TLS CA certificates via `keytool`/truststores directly rather than the standard relation — reasonable since the TLS is between Spark and S3, not the charm and its clients, but means the charm maintains its own cert-import logic.
- No `actions.yaml` — most mature data-platform charms provide operational actions; this is a gap.
- Uses the `charm-libs` stanza in `charmcraft.yaml` to declare library dependencies explicitly — modern practice.
- Non-idempotent reconcile: most mature charms diff desired vs actual state before restarting; this charm restarts on every hook unconditionally. This is the single biggest architectural weakness.

## Tests

**Unit tests**: 48 tests, all passing (0.58s), run via `PYTHONPATH=src:lib poetry run coverage run --source=src -m pytest tests/unit -v`. Coverage: 82% (873 statements, 127 missed).

Coverage by module:
- `src/charm.py`: 100%
- `src/events/history_server.py`: 79% — `_on_config_changed` body uncovered
- `src/events/ingress.py`: 69% — auth-proxy and oauth2-proxy handlers uncovered
- `src/managers/azure_storage.py`: 67% — verify failure paths uncovered
- `src/managers/s3.py`: 70% — error handling branches uncovered
- `src/managers/tls.py`: 75% — `import_ca` and `reset` uncovered
- `src/core/domain.py`: 74% — `StateBase`, `User`, some Azure properties uncovered
- `src/common/k8s.py`: 68% — `read`, `exec`, `write` with mode `"a"` uncovered

**Key coverage gaps**:
- `TLSManager` completely untested (no scenario tests for CA import, reset, truststore password)
- Ingress auth-proxy / oauth2-proxy handlers untested at unit level
- `HistoryServerConfig._azure_storage_conf` for `wasb`/`wasbs` untested — only `abfss` covered
- `AzureStorageManager.verify()` authentication-failure path untested
- `_s3_conf` proxy configuration paths only partially tested (no coverage of `_ssl_enabled` or error branches)
- The stop-before-verify pattern is untested: no unit test verifies `update()` skips the stop when verification would fail
- The non-idempotent restart is untested: no unit test verifies `update()` skips restart when config hasn't changed
- Grafana dashboard publishing delay is untested at the integration level (the logs integration test checks dashboards only after the full stack is already active)

**Integration tests** (could not be run in this environment — require S3/Azure/OIDC endpoints):
- `test_charm.py`: deploy + S3 + real Spark job + API verification + ingress + oauth2proxy auth servlet filter. Exceptionally thorough.
- `test_charm_tls.py`: TLS variant.
- `test_charm_azure.py`: Azure Storage variant, using real Azure credentials from CI secrets.
- `test_charm_logs.py`: Loki/Prometheus/Grafana integration, verifying labels, metrics, dashboards, alert rules via the COS stack behind traefik.
- `test_oauth2proxy.py`: full OAuth2 proxy flow with Playwright browser automation.
- `test_oathkeeper.py`: Oathkeeper variant with Dex external IDP.
- **`test_remove_oauth2proxy` is `@pytest.mark.skip`** at `test_charm.py:328` — the auth-proxy removal path is untested, and no reason is given. Notably, relation removal is exactly the path that triggered the JMX port crash observed in this review.

**Spread tests**: 6 suites in `tests/spread/` (integration-charm, integration-tls, integration-azure, integration-logs, integration-auth, integration-oathkeeper), wrapping the Python integration tests for CI (microk8s via `concierge prepare`). CI runner filtering: ARM64 runs only `integration-tls`; self-hosted jammy-large runs only `integration-tls` and `integration-logs`.

**Lint**: `poetry run ruff check src` — clean. `codespell` — clean. `mypy src` — clean (per tox lint config).

## Docs

- **README**: adequate for a basic deploy; includes a deploy-and-relate example with s3-integrator, documents S3 region defaulting, and notes s3-integrator track 1 vs 2. Missing: no Azure Storage example, no ingress/auth-proxy examples, no mention of `authorized-users`.
- **Charmhub description** (`metadata.yaml`): good summary, links to the Spark project page and charmed-spark docs.
- **CONTRIBUTING.md**: minimal (636 bytes); covers tox commands only, no architecture overview or integration-adding guidelines.
- **No `docs/` directory**: documentation lives externally at `https://canonical-charmed-spark.readthedocs-hosted.com/`.
- **Doc/reality mismatch on region**: README states the charm uses `us-east-1` for S3 requests — true for the boto3 client in `verify()`, but not propagated to Spark's Hadoop configuration (see finding). An operator would reasonably expect `spark.hadoop.fs.s3a.endpoint.region` to be set.
- **Doc/reality mismatch on relate syntax**: README example uses the older `juju relate` syntax; `juju integrate` works identically but isn't shown.

## Open questions

1. Does the missing S3 region cause real failures against non-`us-east-1` AWS buckets? Open issue #133 suggests confusion; would need a deployment against a real non-default-region bucket to confirm `301`/`SignatureDoesNotMatch` behaviour.
2. Why is `test_remove_oauth2proxy` permanently skipped, with no reason documented? Especially concerning given the confirmed relation-removal crash.
3. Does `log-level` have any effect at the OCI image level (e.g. via `history-server.sh`)? Confirmed to have none in charm code.
4. How often does the JMX port race actually trigger in practice? Observed once during relation removal; multiple later config-change cycles and a separate removal did not reproduce it. Depends on Java GC/shutdown timing vs. port-release speed, with `update-status` firing every 5 minutes creating repeated chances for the race.
5. Does the v0/v1 s3 library negotiation between s3-integrator 1/stable and this charm converge cleanly? Cascading relation-changed hooks (4-7 observed) eventually settle but waste minutes of hook processing even against a live endpoint, worse against a dead one.
6. Why doesn't `GrafanaDashboardProvider` publish on the first `relation_created`? Needs investigation into whether `_update_all_dashboards_from_dir` actually ran on that event.
7. Is the `spark8t` typo in the OCI image classpath purely cosmetic today, or would it bite if the charm ever added JARs via its own config directory?
8. Does `set_s3_credentials` work with s3-integrator 2/stable secret-based credentials? Currently untested and blocked on Juju 4 by the s3-integrator 2/stable incompatibility.
