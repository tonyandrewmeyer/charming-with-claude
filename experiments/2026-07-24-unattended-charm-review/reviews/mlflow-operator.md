# mlflow-server

mlflow-server is a Kubernetes sidecar charm that runs the MLflow tracking server plus a Prometheus exporter, backed by a MySQL database and an S3/MinIO artifact store. It is competently structured — a single reconciler (`_on_event`), clear `ErrorWithStatus`-driven status precedence, careful schema-migration-on-refresh handling, and a genuinely good integration-test suite. But the live work in this review surfaced four serious problems the code review alone would not have proved: **a routine pod restart (or any `juju refresh`) runs a non-idempotent `mlflow db upgrade` against the workload-auto-created schema, fails with "Duplicate column 'routing_strategy'", and leaves the charm `active` while the workload crash-loops**; the charm **deletes its own Kubernetes Service when you scale down** (a per-unit `remove` handler in the deprecated `kubernetes_service_patch` library); it reports `active` while the workload is crash-looping on an invalid port with no config validation; and it exposes an **unauthenticated, security-middleware-disabled MLflow server on a NodePort by default** (I created an experiment through it with a forged Referer and got 200). The migration-on-restart bug is the one to fix first, because it turns a routine operational event into a silent outage that needs manual DB surgery to recover.

| | |
|---|---|
| Repo | canonical/mlflow-operator @ 2e60c3d (2026-07-17) |
| Charms | mlflow-server |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (juju 3.6.25): `3.14/edge` rev 1445 full stack + observability + a `2.22/stable`→`3.14/edge` live upgrade; concierge-k8s-4 (juju 4.0.5): `3.14/edge` with MinIO (blocked on DB, see log) |
| Reviewed | 2026-08-15 |

## What it does

`mlflow-server` (k8s, two containers: `mlflow-server`, `mlflow-prometheus-exporter`) deploys MLflow 3.14 with a MySQL backend store (`relational-db` / `mysql_client`) and either an `object-storage` (MinIO) or `s3-credentials` (s3-integrator) artifact store. On refresh it auto-migrates the tracking DB schema (`mlflow db upgrade`, with a read-only `_verify_schema` probe and a `SET PERSIST log_bin_trust_function_creators` workaround for upstream MLflow issue #19943). It renders a K8s Secret and two `PodDefault`s and pushes them over `secrets`/`pod-defaults` relations to `resource-dispatcher` for user namespaces; supports `serve_artifacts` proxy mode, Istio ambient-mode ingress, a sidecar ingress relation, and COS metrics/dashboards/logging. The actual charm logic is all in `src/charm.py` (1217 lines) and `src/services/s3.py` (125 lines); the `deps/` directory is empty (no PyPI `single_kernel_*` logic to review). Vendored libraries under `lib/charms/...` are the standard chisme/COS/Kubeflow set.

## Deployment log

Commands that matter (models `rv-mlflow-deep`, `rv-mlflow-upg` on `concierge-k8s-3` juju 3.6.25; `rv-mlflow-4b` on `concierge-k8s-4` juju 4.0.5):

```
juju add-model -c concierge-k8s-3 rv-mlflow-deep
juju deploy mlflow-server --channel 3.14/edge --trust          # rev 1445
juju deploy mysql-k8s --channel 8.0/stable --trust --config profile=testing   # rev 423
juju deploy minio --channel latest/edge --trust --config access-key=minio --config secret-key=minio123 --config port=9000
juju integrate mysql-k8s mlflow-server
juju integrate minio:object-storage mlflow-server
# observability + dispatch:
juju deploy grafana-agent-k8s --channel 2/stable --trust
juju deploy resource-dispatcher --channel latest/edge --trust
juju deploy metacontroller-operator --channel latest/edge --trust   # provides the DecoratorController CRD resource-dispatcher needs
juju integrate grafana-agent-k8s:metrics-endpoint mlflow-server:metrics-endpoint
juju integrate grafana-agent-k8s:grafana-dashboards-consumer mlflow-server:grafana-dashboard
juju integrate grafana-agent-k8s:logging-provider mlflow-server:logging
juju integrate resource-dispatcher:secrets mlflow-server:secrets
juju integrate resource-dispatcher:pod-defaults mlflow-server:pod-defaults
```

- Deploy → active/idle took ~5 min (mysql init dominates). During relation formation the charm briefly shows a technical waiting message — `List of <ops.model.Relation object-storage:4> versions not found for apps: minio` — the raw `NoVersionsListed` error string from `_get_interfaces`; it resolves on its own but is not an operator-friendly message.
- Second model `rv-mlflow-upg` (same controller): `2.22/stable` rev 1252 deployed, then `juju refresh --channel 3.14/edge` — the live major-upgrade test (see findings 1 and 9).
- Third model `rv-mlflow-4b` on `concierge-k8s-4` (juju 4.0.5): `mysql-k8s 8.0/stable` refuses to deploy on juju 4 ("charm requires Juju version < 4.0.0"), and there is no amd64 juju-4 mysql-k8s build (8.4/edge is s390x only), so the full stack cannot run on juju 4. The mlflow-server charm itself installs and runs fine on juju 4, reaches the correct `blocked: Please add relation to the database`, and creates the MinIO bucket before blocking — so the charm is juju-4-compatible; its ecosystem dependency (mysql-k8s) is not.
- Published `3.14/edge` rev 1445 (2026-07-29) is ~12 days *ahead* of local HEAD (2026-07-17); rev 1445 is what I ran throughout. Behaviours attributed to HEAD below were observed on rev 1445. `latest/edge` is rev 1444 (one revision behind), so a downgrade refresh is possible but was not needed — the `2.22→3.14` upgrade covered the refresh path.

Failure injections performed live: see findings. Summary: `mlflow_port=70000` → `active` while crash-looping; `mlflow_prometheus_exporter_port=70000` → `blocked: Failed to replan` (different failure mode); `default_artifact_root="mlflow/subdir"` → hook error traceback; removing `object-storage` → clean `blocked` with actionable message; removing `relational-db` → `blocked: Please add relation to the database`, re-add → clean recovery; `kubectl delete pod` (simulated restart) → migration false-positive → bricked workload; `kill -9` of the workload PID → recovered cleanly by Pebble this time; `juju refresh 2.22→3.14` → blocked needing a relation re-create, then success after re-add; scale 1→2 → non-leader stuck `waiting`; scale 2→1 → **Service deleted while `active`**.

## Observed behaviour

Things only visible from running it:

- **Pod restart bricks the deployment (critical, finding 1).** After `kubectl delete pod mlflow-server-0`, Juju re-fires `upgrade-charm`. The migration reconciler decided the DB schema was out of date (`_verify_schema`: "found version 5d2d30f0abce, but expected b7e4c1a90f23"), ran `mlflow db upgrade`, which failed with `OperationalError: (1060, "Duplicate column name 'routing_strategy'")` on `ALTER TABLE endpoints ADD COLUMN routing_strategy`. The Blocked status set by `upgrade-charm` was then overwritten by the next `config-changed`/`pebble-ready` hooks (`_on_event` ends in `ActiveStatus()`), so the final observed state was **`active` with `pebble services` = backoff**. Recovery required manual DB surgery: my first attempt (`UPDATE alembic_version SET version_num='b7e4c1a90f23'` then `mlflow db upgrade`) left the workload crashing on `(1054, "Unknown column 'experiments.workspace'")` because that migration hadn't run; I had to `DROP DATABASE mlflow; CREATE DATABASE mlflow` and let the workload re-create it.
- **Unauthenticated write access on the NodePort (critical, finding 3).** `enable_mlflow_nodeport` defaults to `true`, so the charm's own K8s service is `NodePort` 31380/31381. `curl http://10.42.160.130:31380/` → 200, and `POST /api/2.0/mlflow/experiments/create` with `Referer: https://evil.example/` and no credentials → 200; the experiment appears in `experiments/search`. The workload's own log says it plainly: `[MLflow] WARNING: Security middleware is DISABLED. Your MLflow server is vulnerable to various attacks.` The exporter's `/metrics` is also on a public NodePort (31381).
- **Scale 2→1 deletes the `mlflow-server` Service (critical, finding 2).** Confirmed twice (two independent sessions). After `scale-application 2` then `1`, `kubectl get svc mlflow-server` → NotFound while `juju status` shows `active`. A later `config-changed` did not recreate it — recovery requires manual intervention.
- **NodePort collision leaves a broken placeholder service (medium, finding 6).** The k8s-3 and k8s-4 controllers share one physical cluster (confirmed: all model namespaces appear in one `kubectl get ns`). Every additional mlflow-server app on the cluster fails to allocate nodePort 31380: `Kubernetes service patch failed: Service "mlflow-server" is invalid: spec.ports[0].nodePort: Invalid value: 31380: provided port is already allocated` (HTTP 422, swallowed by the library), leaving its service as Juju's default `ClusterIP 65535/TCP` placeholder. The 422 is re-logged as ERROR every 5-minute `update_status` forever. Setting `mlflow_nodeport` to a free port recovers it.
- **NodePort config is deploy-time-only (finding 6, verified).** `mlflow_nodeport=31390` applied (PATCH succeeded), then `mlflow_nodeport=31395` was **silently ignored** — the service stayed on 31390 because the library's `_is_patched` compares only `(port, targetPort)`.
- **Invalid port ⇒ `active` while crash-looping (high, finding 4).** `juju config mlflow-server mlflow_port=70000` → charm `active`; `pebble logs` shows `OverflowError: bind(): port must be 0-65535`; the ServicePatch PATCH was rejected with HTTP 422 and the library swallowed it. `mlflow_prometheus_exporter_port=70000` behaves *differently*: the exporter's `--port` is in the Pebble command, so `replan` raises `ChangeError: Start service ... exited quickly with code 1` and chisme surfaces `blocked: Failed to replan` — caught, but the message doesn't name the port.
- **Nested bucket name ⇒ hook error (high, finding 5).** `default_artifact_root="mlflow/subdir"` → `hook failed: "config-changed"`, unit `error`, traceback `botocore.exceptions.ParamValidationError: Invalid bucket name "mlflow/subdir"`.
- **Scale 1→2 ⇒ dead, misleading second unit.** Unit 1 sits in `waiting` ("Waiting for leadership") forever; its Pebble layer is never applied (workload not started); app-level status becomes `waiting`. The charm is effectively single-unit but doesn't say so.
- **Observability integration works end-to-end.** The `metrics-endpoint` relation carries `scrape_jobs: [{"metrics_path": "/metrics", "static_configs": [{"targets": ["*:5000", "*:8000"]}]}]` plus both alert-rule groups; `grafana-dashboard` carries the dashboard JSON. Both `/metrics` endpoints serve (MLflow on 5000 emits `mlflow_http_request_total`, the exporter on 8000 emits `python_*`).
- **Secret/PodDefault dispatch works, and proxy mode re-shapes it correctly.** With `resource-dispatcher`, the `secrets` relation carries a K8s Secret `mlflow-server-minio-artifact` with the **plaintext** MinIO credentials, and `pod-defaults` carries two PodDefaults. After `serve_artifacts=true`, the Secret manifest is `[]` and the access PodDefault is dropped (only `mlflow-server-minio` with `MLFLOW_TRACKING_URI` remains); a new experiment gets `artifact_location: mlflow-artifacts:/1` instead of `s3://mlflow/0`. Verified with a real create + search round-trip.
- **The 2.22→3.14 upgrade works, but only with an undocumented manual step (finding 9).** `juju refresh --channel 3.14/edge` over a 2.22 deployment lands in `blocked: Database user lacks privileges to migrate the schema...` because the relation user was created without the `charmed_dba` role. Remove + re-add the `relational-db` relation and it completes: workload comes up on 3.14.0 and the pre-upgrade marker experiment survives (with `workspace: default`).
- **Kill the workload process** (`kill -9` of the `mlflow server` PID): Pebble restarted it cleanly (fresh `uvicorn --workers 4` + huey consumers), charm stayed `active`, serving 200. (An earlier session observed a nastier variant where orphaned uvicorn/huey workers held port 5000 so the restart crash-looped with "Address already in use"; the difference is which PID in the tree is killed. Both outcomes are silent from the charm's perspective — no status change.)
- **Resource use.** `kubectl top pod` on the mlflow-server pod: ~400m CPU, **~2.2 GiB memory**. The workload and exporter containers have **no** resource requests/limits in the pod spec (only the charm container, 64Mi request/1Gi limit).
- **Non-root confirmed.** Workload runs as uid 584792 (`_daemon_`), matching `charm-user: non-root`.
- **Deploy-time cost of 2.22.** The 2.22 oci-image took ~13 min to pull (PodInitializing) on this cluster; not a charm bug, but real deploy latency for the upgrade test.
- Not visible from code: the migration-on-restart false positive, the service-deletion-on-scale-down, the active-status-while-crashing, the NodePort-collision placeholder service, and the real end-to-end auth bypass. The unit tests assert none of these.

## Findings

### 1. A routine pod restart (or refresh) runs a non-idempotent DB migration and leaves the charm `active` while the workload crash-loops
- **Severity**: critical
- **Kind**: bug (availability, silent failure)
- **Where**: `src/charm.py:568` ("The `mlflow db upgrade` command is idempotent, so it is safe to run whenever the schema is detected as out of date"), `src/charm.py:532` (`def _is_database_schema_out_of_date(self, backend_store_uri: str) -> bool:`), `src/charm.py:565-605` (`_run_database_migration`), `src/charm.py:1057-1092` (`def _on_upgrade_charm(self, event) -> None:`), `src/charm.py:1196` (`self.model.unit.status = ActiveStatus()`)
- **Evidence**: On a fresh deploy the charm never runs `mlflow db upgrade` — the workload auto-creates the schema, stamped at alembic revision `5d2d30f0abce`, while MLflow 3.14.0's `_verify_schema` expects head `b7e4c1a90f23`. `kubectl delete pod mlflow-server-0` makes Juju re-fire `upgrade-charm`, which runs `mlflow db upgrade` and fails: `sqlalchemy.exc.OperationalError: (1060, "Duplicate column name 'routing_strategy'")` on `ALTER TABLE endpoints ADD COLUMN routing_strategy` (the auto-created schema already has that column). The charm set `blocked: Database schema migration failed...` during `upgrade-charm`, but the immediately-following `config-changed`/`pebble-ready` hooks run `_on_event`, which ends in `ActiveStatus()` unconditionally — observed final state: **`juju status` active, `pebble services` backoff**. Recovery needed `DROP DATABASE` + recreate (my first, gentler attempt to just re-stamp the version then re-run `mlflow db upgrade` left the workload crashing on a different "Unknown column 'experiments.workspace'" error, showing how fragile the partial migration state is).
- **Why it matters**: pod restarts are routine (node drain, OOM kill, image repull, `kubectl rollout`), and any `juju refresh` fires `upgrade-charm` too. Each one silently bricks the tracking server into a crash loop while the charm reports green. The docstring's idempotency claim is disproven for the fresh-deploy-then-restart path, and `_is_database_schema_out_of_date`'s "any other outcome returns False" reasoning is a false positive in practice.
- **Fix**: on fresh installs run `mlflow db upgrade` *before* starting the workload (so the schema is created by alembic, not by auto-init), or treat the specific "Duplicate column" / partial-migration failure as "already migrated" and stamp the version forward, and re-check the Pebble service state after every reconcile so `active` is never reported for a `backoff` service. The upstream stamping discrepancy (`5d2d30f0abce` vs `b7e4c1a90f23`) should be reported to MLflow.
- **Linter rule**: partially mechanical — "a hook handler calls `mlflow db upgrade`/a migration method whose result is not verified before `ActiveStatus()` is set" and "`_on_event` ends with an unconditional `ActiveStatus()` despite a `BlockedStatus` having been set by a prior hook in the same Juju operation". The idempotency-of-upgrade claim can't be linted.

### 2. Scaling down deletes the app's Kubernetes Service, and the charm never restores it
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/observability_libs/v1/kubernetes_service_patch.py:105` (`self.framework.observe(charm.on.remove, self._remove_service)`) + `:264-288` (`_remove_service`), used from `src/charm.py:352-385` (`def _create_service(self):`)
- **Evidence**: the library registers `_remove_service` on `charm.on.remove`, which Juju fires **per unit** on scale-down, not just on `remove-application`. `_remove_service` does `client.delete(Service, self.service_name, namespace=self._namespace)`. Because this charm patches the *default* service (service_name == app), the departing unit deletes the shared service. Observed twice: `kubectl get svc mlflow-server` → NotFound with `juju status` still `active`; `config-changed` does **not** restore it. Recovery is broken: `_is_patched` (`:216-232`) re-raises the 404 when `service_name == self._app`, and `_patch` (`:165-199`) catches `ApiError` and returns, so the service is never recreated.
- **Why it matters**: any scale-down (or unit removal, e.g. a failed node) silently takes MLflow's routing service away — the NodePort and in-cluster DNS entry vanish — while the charm reports healthy.
- **Fix**: stop patching the default Juju service, or gate the removal on application removal rather than unit removal. Short term: only delete when `self.unit.is_leader()` *and* the application is actually being removed, or switch off `kubernetes_service_patch` (deprecated, "removed in October 2025") in favour of `ops.Unit.set_ports`, and verify the service's existence in reconcile.
- **Linter rule**: mechanically checkable — "a charm observes `charm.on.remove` with a handler that calls `Client().delete` on a service whose name equals the app name" (the `-lb`/`!= app` pattern is the safe one). Or simply "`kubernetes_service_patch` used with `service_name == app`".

### 3. Default config exposes an unauthenticated, security-middleware-disabled MLflow server on a NodePort
- **Severity**: critical
- **Kind**: bug (security)
- **Where**: `config.yaml:30-34` (`enable_mlflow_nodeport`, default `true`), `src/charm.py:1016` (`"MLFLOW_SERVER_DISABLE_SECURITY_MIDDLEWARE": "true"`), `src/charm.py:352-358` (NodePort service patch)
- **Evidence**: `MLFLOW_SERVER_DISABLE_SECURITY_MIDDLEWARE` is hard-coded to `"true"` "as already provided by the outer Istio layer" — but the default deployment has no Istio and exposes NodePort 31380. Observed: unauthenticated `POST /api/2.0/mlflow/experiments/create` from the node network returned 200 and created experiment `rv-deep-proxy-test` (with `Referer: https://evil.example/`); `experiments/search` confirms it. MLflow 3.14's own startup banner logs the warning about the disabled middleware.
- **Why it matters**: a fresh `juju deploy mlflow-server` (with a DB + store) puts an unauthenticated tracking server — with full experiment/run/model write access and the DB behind it — on the cluster node's network, no password, no referrer/host checks. Anyone who can reach the node port can read and tamper with MLflow data.
- **Fix**: default `enable_mlflow_nodeport` to `false` (ClusterIP) and only enable the NodePort when the operator explicitly opts in, documenting that it is unauthenticated; or enable MLflow's own auth when no Istio layer is present. At minimum, surface a prominent warning in `README`/charmhub description.
- **Linter rule**: "`MLFLOW_SERVER_DISABLE_SECURITY_MIDDLEWARE` set to a truthy string while `enable_mlflow_nodeport` defaults to true" — mechanically checkable but with a high false-positive cost; the real fix is a config/description change.

### 4. No port validation: invalid `mlflow_port` leaves the workload crash-looping while the charm reports `active` (and the exporter port fails with an uninformative message)
- **Severity**: high
- **Kind**: bug | ux
- **Where**: `config.yaml:10-28` (all four `int` port options have no `minimum`/`maximum`), `src/charm.py:1013` (`"MLFLOW_PORT": self._mlflow_port`), `src/charm.py:352-385` (`_create_service`), `src/charm.py:424` (exporter command builds `--port {self._exporter_port}`)
- **Evidence**: `juju config mlflow-server mlflow_port=70000` → charm `active`; `pebble logs` shows `OverflowError: bind(): port must be 0-65535` and `pebble services` shows `backoff`; the ServicePatch PATCH was rejected with HTTP 422 (`spec.ports[0].port: Invalid value: 70000`) and swallowed by the library. `mlflow_prometheus_exporter_port=70000` → `blocked: Failed to replan` (pebble `ChangeError` surfaced via chisme `update_layer`) — correct status, but the message doesn't tell the operator the *port* is the problem, and the service PATCH 422 is again silently swallowed.
- **Why it matters**: a one-line config mistake produces a `green`/`active` charm with a dead workload and a mismatched service (for `mlflow_port`). The charm neither validates the port before applying it nor checks that the Pebble service actually started. This is exactly the class of "status lies" that erodes trust in the operator.
- **Fix**: add `minimum`/`maximum` (or a pattern) to the `int` config options, or validate in `_create_service`/`_on_event` and raise `BlockedStatus` on out-of-range values. Then check the Pebble service state after replan and surface non-`active` as blocked/error rather than `ActiveStatus()`.
- **Linter rule**: "config option of `type: int` named `*_port` has no `minimum`/`maximum`" — mechanically checkable against `config.yaml`.

### 5. Nested `default_artifact_root` (e.g. `mlflow/subdir`) crashes the hook with an uncaught exception
- **Severity**: high
- **Kind**: bug (failure behaviour)
- **Where**: `src/charm.py:907-945` (`_ensure_bucket_exists`), specifically the `except` tuple at `:937-943`; `src/charm.py:878-906` (`_resolve_bucket_name` uses the config value verbatim as bucket name)
- **Evidence**: `_ensure_bucket_exists` catches `SSLError`, `ClientError`, `ConnectTimeoutError`, `ReadTimeoutError`, `EndpointConnectionError` — but a name like `mlflow/subdir` makes boto3 raise `botocore.exceptions.ParamValidationError` (bucket-name regex), which is not caught. Observed: `hook failed: "config-changed"`, unit in `error`, traceback `ParamValidationError: Invalid bucket name "mlflow/subdir"`. Open issue #376 explicitly asks for nested bucket support; today it produces a hard crash instead of a `BlockedStatus`.
- **Why it matters**: an operator following the natural "prefix inside a bucket" interpretation of `default_artifact_root` gets a hook traceback and an `error` status rather than guidance.
- **Fix**: catch `botocore.exceptions.BotoCoreError` (or `ParamValidationError` specifically) and raise `ErrorWithStatus(..., BlockedStatus)` with a message about bucket naming; or validate the bucket name against the S3 rules before calling the client.
- **Linter rule**: "`except (botocore.exceptions.ClientError, ...)` around boto3 S3 calls does not include `ParamValidationError`/`BotoCoreError`" — mechanically checkable.

### 6. NodePort collisions across apps leave a broken placeholder service, and NodePort changes are deploy-time-only
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:352-385` (`_create_service`), lib `kubernetes_service_patch.py:216-232` (`_is_patched` compares only `(port, targetPort)`, ignoring `nodePort` and service type)
- **Evidence**: the k8s-3 and k8s-4 controllers share one physical cluster. The second mlflow-server app on the cluster got `422 ... spec.ports[0].nodePort: Invalid value: 31380: provided port is already allocated` (swallowed), leaving its service as Juju's default `ClusterIP 65535/TCP` placeholder, with the 422 re-logged every 5 minutes. Setting `mlflow_nodeport=31390/31391` recovered it (PATCH succeeded), but a *further* change `mlflow_nodeport=31395` was **silently ignored** — the service stayed on 31390, because `_is_patched` sees `(5000,5000),(8000,8000)` already equal and returns early.
- **Why it matters**: `mlflow_nodeport`/`mlflow_prometheus_exporter_nodeport` are only honoured at the moment of the first successful patch; later changes are no-ops, and two instances of the charm on one cluster silently break each other's default service.
- **Fix**: include `nodePort` and `type` in the "is patched" comparison, or drop the nodeport config knobs and document them as deploy-time-only; also surface the 422 instead of swallowing it.
- **Linter rule**: not mechanically checkable (library behaviour); a test comparing desired vs applied service spec would catch the drift.

### 7. `SET PERSIST` and S3 `head_bucket` run on every hook, including every 5-minute `update_status`
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:610-658` (`def _ensure_trigger_creation_allowed(self, backend_store_uri: str) -> None:`), `src/charm.py:1162` (`self._ensure_trigger_creation_allowed(self._get_backend_store_uri())`), `src/charm.py:185` (`self.framework.observe(self.on.update_status, self._on_event)`), `src/charm.py:907` (`def _ensure_bucket_exists(self) -> None:`)
- **Evidence**: every `_on_event` executes `_ensure_trigger_creation_allowed(self._get_backend_store_uri())` — a DB connection plus `SET PERSIST log_bin_trust_function_creators = ON` (a write persisted to `mysqld-auto.cnf`), and `_ensure_bucket_exists` which does an S3 `head_bucket`. `update_status` is bound to the same handler, so this repeats every 5 minutes per unit forever, even when nothing changed. `_get_artifact_store_data` is also recomputed ~5 times per reconcile (bucket check, env render, CA-bundle push, secrets context, poddefaults context).
- **Why it matters**: constant, needless load on the S3 store and — worse — a repeated server-level `SET PERSIST` against MySQL on a timer. The trigger workaround is a TODO for an upstream bug and should be run once (or only when migrating), not as a steady-state no-op write.
- **Fix**: memoize/cache the bucket-exists result per config generation, and gate `_ensure_trigger_creation_allowed` behind a flag (e.g. only on `upgrade-charm`/fresh install, or track "done" in stored state/peer data).
- **Linter rule**: "hook handler bound to `update_status` calls methods that open DB/S3 connections and issue mutating statements" — a proxy for it is mechanically checkable.

### 8. Non-leader units report `waiting: Waiting for leadership` forever and never start the workload
- **Severity**: medium
- **Kind**: ux | bug
- **Where**: `src/charm.py:964-968` (`_check_leader` raises `WaitingStatus("Waiting for leadership")`), `src/charm.py:1144` (first call in `_on_event`)
- **Evidence**: `scale-application mlflow-server 2` → `mlflow-server/1` is `waiting` with "Waiting for leadership", its Pebble plan remains the image default, and the app-level status drops to `waiting`. It never changes unless the leader dies.
- **Why it matters**: MLflow tracking is single-writer against one DB; a second unit adds nothing and permanently drags the app status to `waiting`. The message is misleading — it isn't waiting for leadership, it's waiting for a task that will never be assigned.
- **Fix**: either document single-unit (the terraform module already pins `units=1`) or give the non-leader a truthful status ("Not the leader unit; workload runs on unit 0"). Confirm whether multi-unit is even intended.
- **Linter rule**: "`_check_leader` raises `WaitingStatus` on a non-leader unit" — mechanically checkable; `waiting` means "healthy but waiting for something" while this is a terminal state for that unit.

### 9. The 2.x→3.x upgrade requires an undocumented manual relation re-create, and the blocked message doesn't say so
- **Severity**: medium
- **Kind**: ux | docs
- **Where**: `src/charm.py:638-651` (the 1227/`SYSTEM_VARIABLES_ADMIN` escape hatch), `docs/how-to/manage/upgrade/migrate-v215-v222.rst:30-35` (`juju refresh ... --channel` with no pre-step)
- **Evidence**: live `juju refresh 2.22→3.14` landed in `blocked: Database user lacks privileges to migrate the schema. Check the unit logs and act accordingly.` — the actual remediation ("Remove and re-add the 'relational-db' relation ...") is only in the unit logs and in a comment inside `tests/integration/test_charm_major_upgrade.py`, not in any user-facing doc (there is no 2.22→3.14 guide at all). After remove + re-add, the upgrade completed and the pre-upgrade experiment survived.
- **Why it matters**: the first thing a 2.x operator will do to reach 3.14 is `juju refresh`, which lands them in a blocked state whose message sends them to the logs. The CI knows the dance; the docs do not tell the operator.
- **Fix**: put the remove-and-re-add step (and *why*, incl. the mlflow#19943 pointer) in the upgrade docs and in the status message itself ("Remove and re-add the relational-db relation to grant the required privileges").
- **Linter rule**: not mechanical.

### 10. `_get_relational_db_data` splits `endpoints` on `:` without guarding against multi-endpoint or IPv6 values
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:506` (`host, port = val["endpoints"].split(":")`), `src/charm.py:513` (`except KeyError`)
- **Evidence**: the `except KeyError` at `:513` handles missing fields, but a `ValueError` from `"host1:3306,host2:3306".split(":")` (3 elements) or an IPv6 literal would propagate out of `_on_event` uncaught → hook error. Not observed (mysql-k8s single-unit provides `mysql-k8s-primary....svc.cluster.local.:3306`, which splits cleanly), so this is latent.
- **Why it matters**: any provider that emits the documented comma-separated endpoint list, or an IPv6 host, would crash the charm rather than producing a `BlockedStatus`.
- **Fix**: split on the *last* colon (`rsplit(":", 1)`) or parse with `urlparse`, and catch `ValueError` → `ErrorWithStatus(..., BlockedStatus)`.
- **Linter rule**: "`.split(":")` unpacking into exactly two names on relation data" — mechanically checkable.

### 11. `object-storage` schema marks `namespace` optional, but the charm indexes it unguarded
- **Severity**: low
- **Kind**: bug
- **Where**: `metadata.yaml` (object-storage `required` omits `namespace`), `src/charm.py:818` (`host = f"{obj['service']}.{obj['namespace']}"`)
- **Evidence**: the relation schema's `required` list is `access-key, port, secret-key, secure, service` — `namespace` may be absent (or null). `_get_artifact_store_data` then does `obj["namespace"]`, which raises `KeyError` (uncaught) instead of a `BlockedStatus`. MinIO always sends it, so not observed, but the schema explicitly permits its absence.
- **Why it matters**: a provider that omits `namespace` (e.g. cross-model, where the namespace isn't known) crashes the hook rather than blocking cleanly.
- **Fix**: `obj.get("namespace")` and handle null/empty when composing the host.
- **Linter rule**: "direct `obj[`key`]` access on SDI relation data where `key` is not in the schema `required` list" — mechanically checkable if the linter reads metadata.yaml.

### 12. DB password logged at DEBUG, and backend URI (with password) passed as process argv
- **Severity**: low
- **Kind**: bug (secret hygiene)
- **Where**: `src/charm.py:501` (`self.logger.debug("Got following database data: %s", data)`), `src/charm.py:573,626` (snippets/migration receive `backend_store_uri` as an argv element)
- **Evidence**: `data` is the raw `DatabaseRequires.fetch_relation_data()` dict including `password`. At the project's own `concierge.yaml` logging level (`unit=DEBUG`) this lands in `juju debug-log`. The URI is also passed as `sys.argv[1]` to `python3 -c ...` inside the container, so the password is visible in `ps` to anyone in the container (the charm already carefully avoids logging stderr for this reason — see the comment at `:587-588`).
- **Why it matters**: credential leakage to logs (DEBUG) and process listings. Low severity because the container is non-root and the DB user is a limited relation user, but it's avoidable.
- **Fix**: drop the debug log (or redact), and pass the URI via a temp file/stdin rather than argv.
- **Linter rule**: "`logger.debug` of `fetch_relation_data()` output" — mechanically checkable.

### 13. Minor: uncaught raise in `_on_pebble_ready`, broad `except Exception` in ingress handler, stale tool config, deprecated lib, action naming
- **Severity**: low / nit
- **Kind**: lint | ux
- **Where**: `src/charm.py:1096-1100` (`_on_pebble_ready` raises `ErrorWithStatus` outside any try/except → hook traceback if `can_connect()` is ever False), `src/charm.py:1207` (`except Exception as error` in `_on_ambient_mode_ingress_ready`), `pyproject.toml` `[tool.black] target-version = ["py38"]` (code uses 3.12-only nested same-quote f-strings at `src/charm.py:981-987`), `src/charm.py:865-876` (`get-minio-credentials` fails with "Minio is not reachable yet" even when the store is an s3-integrator)
- **Evidence**: `ruff check src/` → 20 errors (modernization/style: UP006/UP045/UP007/UP035, SIM210 ×2, SIM118, TRY201 ×3, RUF015, RUF100, RUF010 ×2, BLE001). `charmcraft analyse` on the packed charm reports `naming-conventions: [WARNING]` — all seven config options use snake_case against the style guide's kebab-case convention (a very common Kubeflow pattern, so low priority). It also emits a false-positive `entrypoint: [ERROR]` (poetry-plugin `${dispatch_path}` resolution; the charm demonstrably runs). The workload logs a deprecation warning every hook: `The kubernetes_service_patch v1 library is DEPRECATED and will be removed in October 2025`.
- **Why it matters**: the uncaught raise and the blind `except Exception` can mask real bugs; the py38 target is stale (charm runs on 24.04/3.12); the MinIO-specific action message is wrong for s3-backed deployments.
- **Fix**: wrap the raise in `_on_pebble_ready` in the same `ErrorWithStatus` handling (or call `_on_event`), narrow the exception, bump the tool target to 3.12, migrate off the deprecated lib (ties into finding 2), and make the action's failure text store-agnostic.
- **Linter rule**: already caught by ruff (`BLE001`, `UP*`); the action-message and uncaught-raise ones are not mechanical.

## Worth copying

- **`ErrorWithStatus`-driven reconciler with clear status precedence.** `_on_event` (`src/charm.py:1142-1196`) short-circuits through blocked/waiting states in a sensible order (leadership → interfaces → conflicting relations → bucket → container → DB → layer) and ends in a single `ActiveStatus()`. Readable and debuggable.
- **Schema migration on refresh with a read-only probe.** `_is_database_schema_out_of_date` (`src/charm.py:532-563`) runs MLflow's own `_verify_schema` read-only and only treats the *specific* "out of date" marker as needing migration; `_on_upgrade_charm` (`:1057-1092`) defers only on `Waiting` and hard-blocks on genuine migration failure. The design is right; the flaw is trusting the upstream check against a workload-auto-created schema (finding 1).
- **Trigger-privilege workaround with a blocked-status escape hatch.** `_ensure_trigger_creation_allowed` (`:610-658`) detects MySQL error 1227 (missing `SYSTEM_VARIABLES_ADMIN`, e.g. an in-place upgrade without `charmed_dba`) and surfaces a `BlockedStatus` with remediation in the logs instead of looping in `waiting` forever. The redaction of DB credentials from migration error output (`:587-588`, `:646-652`) is exemplary.
- **Integration tests assert real behaviour, not just idle.** `tests/integration/test_charm_object_storage.py` verifies exporter metrics contents, creates experiments through the mlflow library, round-trips artifacts through the tracking server in proxy mode, checks the dispatched Secret/PodDefault contents and their *clearing* when switching modes, and validates security contexts. Well above the ecosystem average.
- **Manifest templating that skips empty documents.** `_create_manifests` (`src/charm.py:1116-1127`) drops templates that render to empty YAML (proxy mode intentionally omits the Secret), with a unit test covering it.

## Common-practice notes

- **Conventions followed**: standard `src/` + `lib/charms/.../v<N>/` layout; `charmcraft.yaml` with the poetry plugin and `charm-user: non-root`; SDI for the object-storage interface; chisme `update_layer`; COS providers; terraform module with `units=1` and `trust=true`.
- **Drift**: `[tool.black] target-version = ["py38"]` while the code uses Python 3.12-only syntax, and `[project] requires-python = ">=3.12,<4.0"`. The tooling config hasn't caught up with the runtime.
- **Worse than convention**: patching the *default* Juju service to NodePort via the deprecated `kubernetes_service_patch` (findings 2, 6) — the modern ecosystem norm is `ops.Unit.set_ports`, and the default-service-patch + `remove` combination is what bites here. The plaintext S3 credentials in the dispatched Secret and the unauthenticated NodePort default are also behind where the security posture of comparable data charms has moved.
- **Leads**: the refresh-time DB migration + read-only schema probe and the deliberate Waiting-vs-Blocked distinction are patterns most data-adjacent charms could adopt — once the idempotency false-positive (finding 1) is fixed. The `charmed_dba`-role-based `SET PERSIST` trick (no root DB access) is a neat, well-commented idea.
- **Multi-version reality gap**: charm is juju-4-runnable, but its partner `mysql-k8s` has no amd64 juju-4 build, so a full 4.x deployment is impossible today. Worth stating in docs so operators don't pin juju 4 and get stuck. Also note: both `concierge-k8s-3` and `concierge-k8s-4` controllers point at one physical cluster, which is what makes the NodePort collision (finding 6) bite across what an operator would assume are separate environments.

## Tests

- **Unit**: 106 passed, ~1s (`PYTHONPATH=src:lib pytest tests/unit`). Warnings: `Harness is deprecated` (95×) — the suite still uses `ops.testing.Harness` rather than `ops.Scene`; and a deprecation from the vendored Loki lib (`JujuVersion.from_environ`).
- **Coverage thin spots relative to findings**: no unit test for `_get_relational_db_data` with a comma-separated/IPv6 `endpoints` value; no test for the `namespace`-missing branch of `_get_artifact_store_data`; no test that `_on_event` validates `mlflow_port`; no test asserting the K8s service still exists after `remove`/scale-down (the gap that let findings 1 and 2 through); no test for `_ensure_bucket_exists` receiving a non-S3-shaped bucket name (finding 5); no test that `upgrade-charm` is a no-op when the schema is already current (the gap that let finding 1 through). `_ensure_trigger_creation_allowed`'s success path is tested, but the "runs on every update_status" behaviour is not asserted.
- **Integration**: not run (needs the full concierge stack), but read in full — see "Worth copying". They assert real behaviour and would catch regressions in the storage/ingress/proxy paths. The one hole: none of them restarts the pod or scales the application, so the migration false-positive and the scale-down service deletion went uncaught. The major-upgrade test documents the relation re-create dance in comments but does not assert the *status message* tells the operator about it.
- **CI** (`.github/workflows/ci.yaml`): lint, unit, terraform-checks, build, and four integration matrices (object-storage, s3, ambient, major-upgrade) on ubuntu-24.04. Solid.
- **Static tooling**: `ruff check src/` → 20 errors (modernization/style, see finding 13); `codespell` → 1 hit (`lib/charms/data_platform_libs/v0/data_interfaces.py:612`, vendored lib — `re-using`); `pyright src/charm.py` with `PYTHONPATH=src:lib` → 14 errors: 5 import-resolution false positives (`serialized_data_interface`, `object_storage`, `charmed_kubeflow_chisme.*`) plus real nits (`_resolve_bucket_name(obj: dict)` called with the `ArtifactStoreData` TypedDict ×2, `proxy_mode` returns the config union typed as `bool`, `service_type` Literal in the lib excludes `"NodePort"`, `mesh_type` MethodType vs `MeshType`, region type, LayerDict ×2). `charmcraft pack` succeeds (~47 MB `.charm`).

## Docs

- `README.md` is a thin pointer to `documentation.ubuntu.com/charmed-mlflow` and is mostly fine, but its `get-minio-credentials` example shows the Juju 2.x action output shape (`UnitId`, `results`, `timing`); the real output on juju 3.6/4 is flat `access-key:`/`secret-access-key:` (I ran it). Minor but demonstrably stale.
- The tutorials (`docs/tutorial/mlflow.rst`, `mlflow-kubeflow.rst`) deploy the **`mlflow` bundle** at `2.22/stable`, while the charm HEAD and the `3.14/edge` channel are at 3.14. The upgrade docs stop at 2.15→2.22 and say only `juju refresh ... --channel` — there is **no 2.22→3.14 guide and no mention of the relation remove/re-add step** the upgrade actually needs (finding 9). The standalone-charm docs don't document `serve_artifacts` (proxy mode), the `s3-credentials` relation, or the `default_artifact_root`-must-be-a-bare-bucket-name constraint (finding 5). A new operator following the docs alone would not learn about the unauthenticated NodePort (finding 3) — the docs even advertise the NodePort as the way to reach the UI without warning that there is no auth.
- `docs/how-to/manage/backup.rst` and `restore.rst` correctly note the default bucket name.
- Terraform module README documents the API, and `outputs.tf` now lists `s3_credentials` (commit #451).

## Open questions

- **Why is `enable_mlflow_nodeport` defaulted on?** Given no auth and no Istio in the standalone path, this looks like legacy behaviour (open issue #11 dates to 2022). Settled by a design note; the fix direction is clear either way.
- **Is the restart-brick (finding 1) an upstream MLflow stamping bug or a charm-side gap?** The DB auto-created by the workload is stamped `5d2d30f0abce` while `_verify_schema` expects `b7e4c1a90f23`, and `mlflow db upgrade` then double-adds `routing_strategy`. Whether MLflow should stamp the head or the charm should run `mlflow db upgrade` first on fresh installs, the charm's "idempotent, safe to run" claim is the part a reviewer can hold it to. Settled by a fresh-install + `mlflow db upgrade` trace against upstream.
- **Is multi-unit ever intended?** The workload is a single-writer tracking server; unit 1 is dead weight in `waiting`. If the answer is "no", the charm should say so; if "yes", the non-leader handling and the scale-down service bug need real work.
- **s3-credentials live path**: my attempt to exercise it live was blocked by an s3-integrator 2/stable secret-grant quirk on juju 3.6, so I could not observe the s3 path end-to-end. It is covered by unit tests (`_parse_s3_endpoint`, `_get_s3_data`) and the `integration-s3` CI suite. A working AWS/minio-backed s3-integrator would settle whether `tls-ca-chain`/`region`/`bucket` flow as the charm expects.
