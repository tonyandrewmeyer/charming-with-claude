# airbyte-k8s

The airbyte-k8s charm (2/edge, rev 30) is a Kubernetes operator for Airbyte Server v2.0.0 (community edition), orchestrating 8 workload containers in a single pod. It derives all desired state live from config and relation data through a single `reconcile()` entry point — no `StoredState`, no `defer()`. The code is clean and well-tested (29 passing unit tests, thorough integration tests), but the charm has one blocking defect and several UX problems that undermine an otherwise solid design: it never reaches `active` without a separately-deployed Temporal instance that also needs a `default` namespace created out-of-band via `temporal-admin-k8s`, and none of this is enforced through a relation or surfaced in charm status. On top of that, its mandatory `postgresql-k8s` dependency cannot be deployed on Juju 4.x, making the whole stack effectively unusable on current stable Juju. A maintainer should fix the Temporal dependency handling first (declare it or validate it explicitly with an actionable `BlockedStatus`), then address the Juju 4 blocker with the postgresql-k8s team, then clean up the `maintenance`-status lag that makes every routine operation look like a multi-minute outage.

| | |
|---|---|
| Repo | canonical/airbyte-k8s-operator @ 36d796a (2026-07-17) |
| Charms | airbyte-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3, 2/edge rev 30 (store image rev 15), 4 deployments tested |
| Reviewed | 2026-08-01 |

## What it does

Deploys Airbyte Server on Kubernetes: 8 containers (bootloader, server, workers, cron, workload-api-server, workload-launcher, connector-builder-server, pod-sweeper) sharing a single large OCI rock image. The charm derives its entire desired state from config and live relation data on every `reconcile()` call. Integrates with postgresql-k8s (db), minio (object-storage), s3-integrator (optional), traefik (ingress), COS (loki, grafana-dashboard, otlp metrics), and provides an airbyte-server relation for a companion UI charm.

## Deployment log

Four deployments performed: three on concierge-k8s-3 (Juju 3.6.25) and one aborted attempt on concierge-k8s-4 (Juju 4.0.5).

### First deployment (rv-airbyte-k8s, initial)
```
juju add-model rv-airbyte-k8s --controller concierge-k8s-3
juju deploy airbyte-k8s --channel 2/edge --trust
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy minio --channel ckf-1.10/stable --trust
juju relate airbyte-k8s postgresql-k8s:database
juju relate airbyte-k8s minio
```
No Temporal deployed. The charm stayed in `maintenance` with `Status check: 'airbyte-workload-launcher' DOWN` — never reached `active`. Destroyed afterward.

### Juju 4 attempt (rv-airbyte-juju4, aborted)
```
juju add-model rv-airbyte-juju4 --controller concierge-k8s-4
juju deploy airbyte-k8s --channel 2/edge --trust
juju deploy postgresql-k8s --channel 14/stable --trust
# ERROR: charm requires Juju version < 4.0.0, model has version 4.0.5
```
Also tried postgresql-k8s channels 14/edge, 16/stable, 16/edge — all block on Juju < 4.0.0. MinIO and temporal-k8s deployed successfully. Model destroyed; this is a blocking incompatibility.

### Second deployment (rv-airbyte-deep, deep observation)
Complete dependency chain deployed:
```
juju deploy airbyte-k8s --channel 2/edge --trust
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy minio --channel ckf-1.10/stable --trust
juju deploy temporal-k8s --channel 1.23/stable
juju deploy temporal-admin-k8s --channel 1.23/stable
juju relate airbyte-k8s postgresql-k8s:database
juju relate airbyte-k8s minio
juju config temporal-k8s num-history-shards=4  # required, not default
juju relate temporal-k8s:db postgresql-k8s:database
juju relate temporal-k8s:visibility postgresql-k8s:database
juju relate temporal-k8s:admin temporal-admin-k8s:admin
juju relate temporal-k8s:temporal-host-info temporal-admin-k8s:temporal-host-info
juju run temporal-admin-k8s/0 cli args="operator namespace --namespace default create" --wait=2m
```

**Image pull**: 21m31s for the 2,785,494,965-byte (2.8GB) rock image from `registry.jujucharms.com`. The pod went from PodInitializing → 9/9 Running once the image was pulled — a significant UX issue, since an operator sees "installing agent"/"waiting" for 20+ minutes with no progress indication beyond the kubelet's Pulling event.

**Time to active**: ~25 minutes from `juju deploy` to `active` (21 min image pull + ~4 min for dependency setup and Temporal namespace creation), provided PostgreSQL, MinIO, and Temporal (with a `default` namespace) are all ready.

**Without Temporal namespace**: the charm stays permanently in `maintenance` / `Status check: 'airbyte-cron' DOWN` because the server, cron, and workers all wait on the `default` Temporal namespace. The charm provides no guidance about this requirement.

### Third deployment (rv-airbyte-full, integrations deep-dive)
Full stack plus traefik, loki, grafana, grafana-agent, self-signed-certificates:
```
juju deploy airbyte-k8s --channel 2/edge --trust
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy minio --channel ckf-1.10/stable --trust
juju deploy temporal-k8s --channel 1.23/stable
juju deploy temporal-admin-k8s --channel 1.23/stable
juju deploy traefik-k8s --channel latest/stable --trust
juju deploy loki-k8s --channel 2/stable --trust
juju deploy grafana-k8s --channel 2/stable --trust
juju deploy grafana-agent-k8s --channel 0.40/stable --trust
juju deploy self-signed-certificates --channel latest/stable
# airbyte↔postgresql, airbyte↔minio, airbyte↔traefik, airbyte↔loki, airbyte↔grafana
# Temporal: num-history-shards=4, all relations, default namespace via CLI
```
- **Ingress**: `http://10.43.45.0/rv-airbyte-full-airbyte-k8s/api/v1/health` returned HTTP 200.
- **Grafana dashboard**: dashboard JSON (`airbyte.json`) confirmed transmitted over `grafana-dashboard` relation.
- **Loki logging**: promtail binary URLs confirmed transmitted over the `logging` relation.
- **send-otlp**: could not be connected — grafana-agent-k8s uses the `tracing` interface; airbyte-k8s uses `otlp`. No compatible consumer among deployed charms.
- **Scaling**: 1→2→1. Both units reached 9/9 Running; second unit paid the full 21m image-pull penalty; scale-down clean.
- **juju refresh**: 2/edge rev 30 → latest/edge rev 28 accepted, no endpoint changes. Version stayed v2.0.0 (image-determined, not charm code).
- **Process kill (SIGKILL)**: `kill -9` on the airbyte-server Java process — Pebble restarted it within seconds.
- **Remove-application**: `juju remove-application --force --no-wait --destroy-storage --no-prompt` removed the charm cleanly, no leftover pods/secrets/storage. grafana-k8s showed a transient `hook failed: grafana-dashboard-relation-departed` — a grafana charm issue, not airbyte's.

### Fourth deployment (rv-airbyte-deep2, failure injection deep-dive)
Same dependency chain as the second deployment, plus targeted injections:
- **Postgresql relation removal/re-add**: correct `BlockedStatus` "database relation not ready" → recovered.
- **Workload-launcher `pebble stop`**: same issue as airbyte-server — charm stays `active` with a dead service. Confirmed on a second service type.
- **Workload-launcher `pebble stop` then `pebble start`**: charm never noticed either event; stayed `active` throughout.
- **Secret with missing keys**: secret created with only `aws-access-key` (missing `aws-secret-access-key`). Charm produced `BlockedStatus: secret '…' missing keys: ['aws-secret-access-key']` — clear message.
- **Invalid `temporal-host` config**: set to `nonexistent:7233`. After the next update-status, charm showed `maintenance: Status check: 'airbyte-cron' DOWN`, correctly detecting the broken connectivity. Reverted and recovered to `active` ~5 minutes later at the next update-status cycle.
- **3 rapid simultaneous config changes** (`log-level=DEBUG`, `max-sync-workers=10`, `temporal-host=temporal-k8s:7233`): processed without errors, reached `active`. ~2 hooks per config change; reasonable.
- **Pebble check vs. charm status**: while charm showed `maintenance: Status check: 'airbyte-cron' DOWN`, `pebble checks` on the cron container showed `up` with 7 successes — confirming the 5-minute status lag.

## Observed behaviour

- **Image pull time**: 21m31s for the 2.8GB rock image, consistent across three separate deployments. Cold-pull penalty on every new node or model restart.
- **Memory/CPU**: pod at idle: 32m CPU, 3706Mi RAM (~3.6GB); airbyte-server Java process ~749MB RSS; 8 containers sharing one image.
- **Hook count**: 138 hooks over ~40 minutes; 160+ over a full integration test with scaling and refresh.
- **Cannot reach `active` without Temporal**: `TEMPORAL_HOST` defaults to `temporal-k8s:7233` with no relation to enforce the dependency. Needs a running Temporal plus a `default` namespace created via `temporal-admin-k8s`. Without it, `airbyte-cron` returns 503 (`{"status":"DOWN"}`) and the charm sits in `maintenance`.
- **0–5 minutes in `maintenance` after every change**: `reconcile()` always ends with `MaintenanceStatus("replanning application")`; only `_on_update_status` (every 5 min by default) promotes to `ActiveStatus`. Confirmed: after minio re-relation, charm entered maintenance at 21:01:58 and stayed there until update-status fired at 21:06:30.
- **`WORKLOAD_API_BEARER_TOKEN` is a literal Helm template artifact**: `".Values.workload-api.bearerToken"` observed in the pebble plan environment across all deployments.
- **Stopped service not detected by update-status**: `pebble stop airbyte-server` left the service inactive while the charm remained `active`. `container.get_check("up")` raises when a service is stopped, the exception is swallowed by `_validate_pebble_plan`, and `replan()` doesn't restart unchanged services. Only recovered on a config change. By contrast, `kill -9` of the Java process was correctly recovered by Pebble within seconds.
- **Ingress works correctly**: traefik URL returned HTTP 200; `AIRBYTE_URL` correctly includes the model-name prefix.
- **Grafana dashboard and Loki logging relations work**: content confirmed transmitted in both directions.
- **`send-otlp` has no compatible consumer**: grafana-agent-k8s uses `tracing`; airbyte uses `otlp`.
- **Config validation is good**: invalid enum values produce clear pydantic `ValidationError` messages; bad secret IDs produce actionable `BlockedStatus` messages; both recover correctly.
- **Scaling and refresh are clean**: 1→2→1 works, both units reach 9/9 Running (second pays the image-pull cost again). Refresh 2/edge rev 30 → latest/edge rev 28 accepted without disruption; version unchanged (image-determined).
- **Remove-application teardown is clean**: no leftover pods, secrets, or storage.

### Failure injection results

| Injection | Result | Recovery |
|---|---|---|
| `storage-type=INVALID` | `BlockedStatus` with pydantic validation error | Recovered on revert |
| `aws-credentials-secret-id=doesnotexist` | `BlockedStatus` "secret not found or not granted" + grant-secret hint | Recovered on clear |
| Remove minio relation while active | `BlockedStatus` "minio relation not ready" within seconds | Recovered after re-relating |
| Remove postgresql relation while active | `BlockedStatus` "database relation not ready" within seconds | Recovered after re-relating |
| Kill `airbyte-server` via `pebble stop` | Charm stayed `active`; service not auto-restarted | Only restarted on next config change (replan) |
| Kill `airbyte-workload-launcher` via `pebble stop` | Charm stayed `active`; same issue confirmed on different service | Only restarted on next config change (replan) |
| Kill airbyte-server Java process (SIGKILL) | Pebble restarted within seconds; charm unaffected | Automatic |
| No Temporal namespace | `maintenance` "Status check: 'airbyte-cron' DOWN" indefinitely | Recovered after creating namespace |
| Remove and re-add minio relation | `BlockedStatus` → `active` cycle | Clean, ~5 min for full recovery due to update-status lag |
| Scale 1→2→1 | Both units active; scale-down clean | Normal |
| juju refresh 2/edge→latest/edge | Refresh accepted; no disruption | Normal |
| Remove application | Clean teardown; no leftover resources | N/A |
| Secret missing required keys (`aws-secret-access-key`) | `BlockedStatus` "secret '…' missing keys: ['aws-secret-access-key']" | Recovered on clear |
| Invalid `temporal-host` (`nonexistent:7233`) | `maintenance` "Status check: 'airbyte-cron' DOWN" after next update-status | Recovered ~5 min after reverting config |
| 3 rapid simultaneous config changes | Charm handled churn; reached active | Normal |
| `pebble stop` then `pebble start` airbyte-workload-launcher | Charm stayed `active` throughout, never detected either event | N/A — never detected |

## Findings

### Temporal dependency is undeclared and blocks the charm from reaching active
- **Severity**: high
- **Kind**: bug
- **Where**: `charmcraft.yaml` (no temporal relation), `src/charm.py` (`reconcile`), `src/literals.py:46` (`TEMPORAL_HOST` default)
- **Evidence**: The charm configures `TEMPORAL_HOST=temporal-k8s:7233` as a config default but has no `requires: temporal` endpoint. Server, cron, and workers hang on `Waiting for namespace default to be initialized in temporal...`. The cron health check returns 503 `{"status":"DOWN"}` until the namespace is created via a `temporal-admin-k8s` CLI action. An operator must independently know to deploy temporal-k8s, deploy temporal-admin-k8s, set `num-history-shards`, and run the CLI action to create the default namespace — none of this is surfaced in charm status.
- **Impact**: An operator following the README, which lists Temporal as a key dependency, finds the charm never goes active because there is no relation to enforce Temporal deployment. The tutorial additionally references a `temporal relation not ready` status that cannot exist.
- **Fix**: Add a `requires: temporal` relation endpoint, or add a `_check_temporal_ready()` method in `_validate()` that tests connectivity and the existence of the default namespace, producing a `BlockedStatus` with actionable instructions.
- **Linter rule**: "Config option referencing a remote service without a corresponding relation" — not mechanically checkable.

### Juju 4.x compatibility blocked by postgresql-k8s dependency
- **Severity**: high
- **Kind**: bug / compat
- **Where**: `charmcraft.yaml` (bases: ubuntu@22.04), postgresql-k8s channel restrictions
- **Evidence**: airbyte-k8s 2/edge rev 30 deploys successfully on Juju 4.0.5 (concierge-k8s-4). However, postgresql-k8s — its mandatory database dependency — cannot be deployed on Juju 4.x: all channels (14/stable, 14/edge, 16/stable, 16/edge) fail with `charm requires Juju version < 4.0.0, model has version 4.0.5`. MinIO and temporal-k8s deploy fine on Juju 4.
- **Impact**: Operators on Juju 4.x (the current stable line) cannot deploy this charm's full dependency stack, even though the charm's own metadata doesn't restrict Juju version.
- **Fix**: Declare `assumes: juju < 4.0` in `charmcraft.yaml` until postgresql-k8s supports Juju 4, or work with the postgresql-k8s team on a compatible revision.
- **Linter rule**: "Charm deploys on Juju version where required relations are blocked by version constraints" — partially checkable by inspecting relation charms' `assumes` at publish time.

### WORKLOAD_API_BEARER_TOKEN is a literal Helm template artifact
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm_helpers.py:156`
- **Evidence**: `"WORKLOAD_API_BEARER_TOKEN": ".Values.workload-api.bearerToken"` — a Helm values-template path copied verbatim from the upstream Airbyte Helm chart. Confirmed in the pebble plan on the running pod via `kubectl exec` across all deployments.
- **Impact**: The workload API bearer token is a static placeholder string rather than a real secret — the workload API is either unprotected or may reject the value, breaking internal API communication.
- **Fix**: Generate a random bearer token (e.g. `secrets.token_hex()`) and store it consistently, or set it to an empty string if the workload API is internal-only with authentication handled elsewhere.
- **Linter rule**: "Helm template artifact detected in non-Helm context" — could detect `".Values."` / `"{{ .Values."` patterns in Python strings under `src/`.

### MinIO relation helper mutates charm metadata (destructive hack)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/relations/minio.py:105`
- **Evidence**:
  ```python
  if "airbyte-peer" in charm.meta.relations:
      del charm.meta.relations["airbyte-peer"]
  ```
  This deletes the `airbyte-peer` entry from the live `charm.meta.relations` dict on every `get_interfaces()` call, called on every reconcile.
- **Impact**: Mutating `charm.meta` is a persistent side effect. Any code path that later accesses `charm.meta.relations["airbyte-peer"]` will raise `KeyError`. It's a fragile, unguarded workaround for an upstream interface library issue (`serialized-data-interface`).
- **Fix**: Use a shallow copy (`dict(charm.meta.relations)`) before deleting, or fix the upstream `get_interfaces()` to skip peer relations.
- **Linter rule**: "Mutation of charm.meta.relations detected" — mechanically checkable (detect `del charm.meta.relations[` or assignment to `charm.meta`).

### Charm stays in `maintenance` for up to 5 minutes after successful reconcile
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/charm.py:514-515`, `src/charm.py:285-290`
- **Evidence**: `reconcile()` always ends with `self.unit.status = MaintenanceStatus("replanning application")`. Only `_on_update_status` (fires every 5 minutes by default) can set `ActiveStatus`. Observed: after minio re-relation at 21:01:58, charm showed `maintenance` until 21:06:30 when update-status set `active`, despite all 8 containers being healthy throughout.
- **Impact**: Every operator interaction (e.g. `juju config`) appears as a 0–5 minute outage even though no work is actually pending, undermining confidence in the charm.
- **Fix**: In `reconcile()`, after successfully replanning, check whether all services and pebble checks are healthy and set `ActiveStatus` directly; keep `_on_update_status` as periodic revalidation.
- **Linter rule**: "`ActiveStatus` only set in update-status, never in reconcile" — mechanically checkable by pattern-matching.

### Stopped services not detected; charm stays `active` with dead processes
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:255-290` (`_on_update_status`)
- **Evidence**: `pebble stop airbyte-server` left the server inactive; the charm remained `active` (confirmed at 20:53:57, 2+ minutes after the kill). `container.get_check("up")` raises when a service is stopped, but the exception is swallowed by `_validate_pebble_plan`, which returns `False` and triggers `reconcile()` — but `reconcile()` calls `container.replan()`, which only restarts services whose plan changed, so an unchanged-but-stopped service stays stopped. The server only restarted at 20:54:24 when a config change triggered a real layer update. Confirmed on a second service (`airbyte-workload-launcher`) in the fourth deployment.
- **Impact**: A deliberately or accidentally stopped service is invisible to the charm — it looks healthy while a core service is dead.
- **Fix**: In `_on_update_status`, check that all services in `CONTAINER_HEALTH_CHECK_MAP` are actually running (via `container.get_services()`), not just that the pebble plan is valid; restart or reconcile if not.
- **Linter rule**: "Pebble plan validated but service liveness not checked" — not mechanically checkable.

### Invalid `temporal-host` config silently breaks connectivity; no validation in `_validate()`
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/charm.py:318-359` (`_validate`), `src/charm.py:536` (`reconcile`), `src/structured_config.py` (no `temporal_host` field validator), `src/literals.py:46`
- **Evidence**: Setting `temporal-host=nonexistent:7233` triggered no `BlockedStatus`. The charm accepted the config, entered `MaintenanceStatus("replanning application")`, and only the next `update-status` (up to 5 minutes later) surfaced `Status check: 'airbyte-cron' DOWN`. `_validate()` only checks relational dependencies (db, minio, s3), not the `temporal-host` config, which is a hard runtime dependency.
- **Impact**: A misconfigured Temporal host (typo, wrong port, wrong app name) leaves the operator with a generic "replanning application" message for up to 5 minutes before any actionable signal appears.
- **Fix**: Add a `_check_temporal_ready()` method that tests TCP connectivity to `temporal-host` during `_validate()`, or at minimum validate the host:port format with a pydantic field validator.
- **Linter rule**: not mechanically checkable.

### Pebble-check status lag confirmed: checks UP while charm shows DOWN
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:285-290` (`_on_update_status`), `src/charm.py:514-515` (`reconcile`)
- **Evidence**: After reverting `temporal-host` from invalid→valid at 22:00:45, the cron container's pebble check reported `up` with 7 successes by 22:01:30, but the charm continued showing `maintenance: Status check: 'airbyte-cron' DOWN` until update-status fired at ~22:05:39 — 4+ minutes of false-degraded status while the workload was healthy. Verified by comparing `pebble checks` output inside the container with `juju status`.
- **Impact**: Combined with the stopped-service issue above, this shows a systemic pattern: charm status reflects the last update-status snapshot, not current reality — for up to 5 minutes after any change.
- **Fix**: Same as the maintenance-lag fix — set `ActiveStatus` directly in `reconcile()` after confirming checks pass, or reduce `update-status-hook-interval` to 60s (as the integration tests do).
- **Linter rule**: not mechanically checkable.

### Bare `except Exception` in multiple locations
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/relations/minio.py:131`, `src/s3_helpers.py:38`, `src/charm_helpers.py:267,295`
- **Evidence**: All four sites catch bare `Exception`, including things like `MemoryError` and `SystemExit`. `s3_helpers.py:38` converts any failure in session creation to a generic `ValueError("Failed to create a session")`; `charm_helpers.py:267,295` do the same for proxy URL and URL-splitting logic.
- **Impact**: Unexpected errors are silently swallowed or converted, losing the original stack trace context.
- **Fix**: Catch specific exception types — e.g. `(KeyError, ValueError, TypeError)` in `minio.py:131`, `(ClientError, EndpointConnectionError)` in `s3_helpers.py:38`, `ValueError` specifically in `charm_helpers.py`.
- **Linter rule**: "Bare `except Exception` in non-logging/non-cleanup context" — mechanically checkable (ruff `broad-exception-caught` / pylint W0703).

### OCI image is ~2.8GB, causing 21+ minute cold-pull times
- **Severity**: medium
- **Kind**: performance
- **Where**: `airbyte_rock/rockcraft.yaml`, the OCI resource at `registry.jujucharms.com`
- **Evidence**: `kubectl describe pod` showed `Successfully pulled image ... in 21m31.318s. Image size: 2785494965 bytes.` The rockcraft.yaml's `assemble` part runs a full Gradle build with OpenJDK 21, npm, and kubectl, then `organize-tars` extracts only 8 directories from the build — the rest (gradle caches, source, build intermediates, full JDK rather than JRE) remain in the image.
- **Impact**: Every new deployment, new node, or pod reschedule incurs a 21-minute image-pull penalty, dominating time-to-active and giving a poor first impression.
- **Fix**: Trim the final image to just the extracted `airbyte-app` tars and a JRE (not a full JDK with headers); consider a multi-stage rock or split-part approach to roughly halve image size.
- **Linter rule**: not mechanically checkable.

### `error_code` comparison in bucket creation is likely broken
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/s3_helpers.py:58-65`
- **Evidence**:
  ```python
  except ClientError as e:
      error_code = int(e.response["Error"]["Code"])
      if error_code == 404:
  ```
  `Error.Code` in S3 responses is a string like `"404"` or `"NoSuchBucket"`, not necessarily numeric. `int("NoSuchBucket")` raises `ValueError`, which is unhandled here.
- **Impact**: An S3-compatible store returning a non-numeric error code (common for MinIO, Ceph, others) would crash `reconcile()` with an unhandled exception instead of a clean `BlockedStatus`.
- **Fix**: Use string comparison (`if e.response["Error"]["Code"] == "404"`) or the HTTP status code (`e.response["ResponseMetadata"]["HTTPStatusCode"] == 404`).
- **Linter rule**: not mechanically checkable — requires semantic knowledge of S3 error payloads.

### Documentation references non-existent config options
- **Severity**: medium
- **Kind**: docs
- **Where**: `documentation/how-to/secure-airbyte-deployments.md:43-44`
- **Evidence**: The how-to instructs `juju config airbyte-k8s tls-secret-name=airbyte-tls` and `juju config airbyte-k8s external-hostname=<YOUR_HOSTNAME>`, but neither option exists in `charmcraft.yaml` config or `src/structured_config.py` (confirmed by grep).
- **Impact**: The documented TLS configuration path cannot work with the current charm, eroding operator trust.
- **Fix**: Implement `tls-secret-name`/`external-hostname`, or rewrite the docs to describe the actual TLS flow via the standard `ingress` relation (traefik/nginx-ingress-integrator).
- **Linter rule**: "Config option referenced in docs but not present in charm" — not mechanically checkable without cross-referencing charmcraft.yaml.

### `extra_user_roles: admin` incompatible with postgresql-k8s 16/stable
- **Severity**: medium
- **Kind**: bug / compat
- **Where**: `src/charm.py:129`
- **Evidence**: `self.db = DatabaseRequires(self, relation_name="db", database_name="airbyte-k8s_db", extra_user_roles="admin")`. Open issue #54 confirms postgresql-k8s 16/stable rejects `admin` as an extra user role, expecting `charmed_admin` instead. Integration tests pin to postgresql-k8s revision 381 (14/stable, from 2024), so this is not caught in CI.
- **Impact**: Operators upgrading or deploying against postgresql-k8s 16/stable see the database relation fail with `"invalid role(s) for extra user roles"`.
- **Fix**: Make `extra_user_roles` configurable, or detect the PostgreSQL version and switch between `admin` (14) and `charmed_admin` (16+).
- **Linter rule**: not mechanically checkable.

### `send-otlp` relation has no compatible consumer in the standard COS stack
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `charmcraft.yaml` (`send-otlp` uses `otlp` interface), `src/charm.py:167-170`
- **Evidence**: `send-otlp` is defined with `interface: otlp`. grafana-agent-k8s — the standard COS metrics collector — exposes `tracing`, not `otlp`. `juju relate grafana-agent-k8s airbyte-k8s:send-otlp` fails with "no relations found". The README points to `opentelemetry-collector-k8s` as the intended consumer, but this charm was not tested in this review.
- **Impact**: Of the three documented COS relations, only two (logging, grafana-dashboard) work with the standard COS charms; the third requires a less-common charm operators may not know about.
- **Fix**: Document clearly that `send-otlp` requires `opentelemetry-collector-k8s`, not `grafana-agent-k8s`; or add a `tracing`-interface relation for grafana-agent-k8s compatibility.
- **Linter rule**: not mechanically checkable.

### Tutorial contains multiple factual errors
- **Severity**: medium
- **Kind**: docs
- **Where**: `documentation/tutorial/04-deploy-airbyte.md:54,76,79,1`
- **Evidence**: The tutorial claims the charm will show a `temporal relation not ready` blocked status, which cannot exist since there's no temporal relation. Sample `juju status` output (line 76) references `airbyte-webhooks-k8s`, a charm that does not exist on Charmhub, and (line 79) uses `postgresql` (machine charm) instead of `postgresql-k8s`. The deploy command uses `--channel edge` rather than a track-specific channel like `2/edge`. The tutorial does not document the critical Temporal namespace creation step or the `num-history-shards=4` requirement.
- **Impact**: An operator following the tutorial hits status messages that don't match, tries to deploy a non-existent charm, and gets stuck without ever learning about the Temporal namespace step.
- **Fix**: Update the tutorial to reflect actual behaviour: document the namespace-creation step, use correct charm names/channels, and remove references to non-existent charms/statuses.
- **Linter rule**: not mechanically checkable.

### Charm source version drifts from published revision; Juju 4 metadata gap
- **Severity**: medium
- **Kind**: test-gap / docs
- **Where**: `src/literals.py:10` (`AIRBYTE_VERSION = "1.7.0"`), `charmcraft.yaml` (no `assumes` restriction for Juju 4)
- **Evidence**: The git HEAD (`36d796a`, 2026-07-17) declares version 1.7.0 and builds Airbyte platform tag `v1.7.0`, but the deployed `2/edge` charm (rev 30, commit `6f8d5d96`, published 2026-07-28) shows v2.0.0 at runtime — published from a commit not present in this repo's history. Integration test helpers pin PostgreSQL to revision 381, while `14/stable` is revision 925 — a 500+ revision gap.
- **Impact**: The local repo and integration tests do not reflect the published charm's actual version or dependency revisions, and nothing in `charmcraft.yaml` documents the Juju 4 incompatibility caused by postgresql-k8s.
- **Fix**: Keep the repo and published channels traceable to each other, or document which branches/tags map to which tracks. Add `assumes: juju < 4.0` until postgresql-k8s supports Juju 4.
- **Linter rule**: not mechanically checkable.

### `_on_update_status` silently swallows validation failures
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:259-261`
- **Evidence**:
  ```python
  try:
      self._validate()
  except ValueError:
      return
  ```
  If a relation breaks between reconciles, `_validate()` raises `ValueError` and the handler returns without updating status — the charm stays at whatever status `reconcile()` last set (typically `maintenance`) instead of transitioning to `blocked`.
- **Impact**: The operator sees "replanning application" for up to 5 minutes when the charm should show an actionable "minio relation not ready"-style message. Purely a visibility gap — the next relation change would still trigger a correct `reconcile()`.
- **Fix**: In the `except ValueError` block, set `self.unit.status = BlockedStatus(str(err))` before returning.
- **Linter rule**: "ValueError caught in update-status but not reflected in status" — mechanically checkable.

### No actions defined
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py` (no `@action` decorators or observers)
- **Evidence**: `juju actions airbyte-k8s` returns "No actions defined for airbyte-k8s."
- **Impact**: For a complex 8-container workload, operators have no `juju run`-based way to check health, restart services, or view per-component logs; they must fall back to `kubectl exec`.
- **Fix**: Add at minimum a `health`/`status` action reporting Pebble service state, and optionally a `restart-service` action.
- **Linter rule**: "K8s charm with multiple containers has no actions" — mechanically checkable.

### `pebble-check-failed` events fire but are not handled by the charm
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py` (no observer for `pebble_check_failed`/`pebble_check_recovered`)
- **Evidence**: `juju show-status-log` recorded `running airbyte-server-pebble-check-failed hook` at 20:51:56 and `running airbyte-server-pebble-check-recovered hook` at 20:54:36. These fire and are logged by Juju, but the charm has no handler — no log message, no status change, no automated recovery attempt.
- **Impact**: A flapping service goes unnoticed for up to 5 minutes (until the next update-status).
- **Fix**: Add observers for `pebble_check_failed`/`pebble_check_recovered` that log the event and optionally trigger an immediate reconcile for the affected container.
- **Linter rule**: "Pebble health check defined but no check-failed handler registered" — mechanically checkable by comparing `CONTAINER_HEALTH_CHECK_MAP` entries with observed framework events.

### `reconcile()` repeats S3 bucket/lifecycle operations on every call
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:255-295` (`_on_update_status`), `src/charm.py:462-490` (`reconcile`)
- **Evidence**: `reconcile()` unconditionally creates S3 buckets and sets lifecycle policies every time it runs, including reconciles triggered from `_on_update_status`. Logs show `Bucket airbyte-dev-logs exists. Skipping creation.` firing on every reconcile even when buckets already exist and `put_bucket_lifecycle_configuration` re-applying the same policy each time.
- **Impact**: Harmless but unnecessary repeated work on every reconcile.
- **Fix**: Move bucket creation/lifecycle setup to a one-time initialization step, or guard it so it only runs once per deployment.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Single reconciler pattern**: `src/charm.py:450-515` (`reconcile()`) is the sole entry point for all observers. No state is persisted — every call derives the desired state live from config + relations, eliminating state-drift bugs.
- **Structured config with pydantic**: `src/structured_config.py` defines a full `CharmConfig` model with field validators (`blank_string`, `greater_than_zero`, `cpu_validator`, `memory_validator`). Invalid values produce clear pydantic `ValidationError` messages that propagate to `BlockedStatus`. Tested thoroughly in `tests/unit/test_structured_config.py`.
- **`ReconcileData` dataclass**: `src/connections.py:55-63` — `_validate()` returns a frozen dataclass with all live-derived connection details as an immutable snapshot, preventing accidental mutation mid-reconcile.
- **Auth secret startup gating**: `src/charm.py:506-515` — runtime containers are skipped until the bootloader-created `airbyte-auth-secrets` exists, with `update-status` as the retry mechanism, correctly handling the sequencing dependency without blocking the deploy.
- **Unit tests with scenario**: `tests/unit/test_charm.py` covers 24 scenarios (blocked states, relation data derivation, ingress, secrets, auth secret presence/absence, pebble plan validation) using ops `testing.Context`/`testing.State` rather than the deprecated Harness.
- **Clean relation modules**: each `src/relations/*.py` is an independent `framework.Object` delegating to `self.charm.reconcile()`.
- **Observability integration**: all three COS relations wired up in a dedicated `_setup_observability()` method; OTLP endpoint construction correctly normalizes scheme and path.
- **Grafana dashboard**: `src/grafana_dashboards/airbyte.json.tmpl` provides a log-based health dashboard using Loki queries, with honest documentation that community edition emits no application metrics over OTLP.
- **Terraform product module with Temporal namespace creation**: `terraform/product/tests/create_namespace/create-namespace.sh` handles namespace creation via a Terraform `external` data source with retries and idempotency (tolerates "already exists"). `terraform/product/main.tf` orchestrates the full deployment (airbyte + postgresql + temporal + temporal-admin + minio) as a single deployable Terraform artifact, avoiding manual CLI steps.

## Common-practice notes

- **Structured config over `config.yaml`**: follows the modern convention of pydantic-driven runtime validation, with `charmcraft.yaml` retained only for Charmhub display.
- **No `metadata.yaml`**: `charmcraft.yaml` is the single source of truth — current ecosystem convention.
- **`TypedCharmBase`**: uses `charms.data_platform_libs.v0.data_models.TypedCharmBase` for typed config access, the current recommended data-platform pattern.
- **Library versions**: pins specific versions in `pyproject.toml` (`ops ~= 3.7`, `boto3 == 1.34.31`, `kubernetes == 24.2.0`). Some are old (`kubernetes == 24.2.0` from 2022). `uv.lock` provides reproducible builds.
- **Integration test tooling**: uses `jubilant` (v1.8.0) rather than `pytest-operator`, an emerging pattern in Commercial Systems charms; `deploy_full_stack()` deploys the whole dependency chain and runs a real Airbyte sync job — more thorough than typical "wait for active" tests.
- **Status stuck in maintenance is atypical**: most charms set `ActiveStatus` from `reconcile()`/`_on_config_changed()` once healthy, rather than only from `update-status`.
- **Missing Temporal relation reflects an ecosystem convention gap**: some data-platform charms use config to point at dependent services rather than relations, but Juju convention leans toward relations for anything with its own charm. Temporal straddles this line and is currently unenforced either way.

## Tests

- **Unit tests**: 29 tests, all passing (`PYTHONPATH=src:lib uv run --group test pytest tests/unit/`, 2.94s). Covers blocked states, relation data derivation, MinIO/S3 storage types, ingress (ready/revoked/absent), credential secrets (AWS, GCP, Vault), missing secret keys, auth secret presence/absence, pebble plan validation, config parsing.
- **Integration tests**: 3 files (`test_charm.py`, `test_upgrade.py`, `test_scaling.py`) using `jubilant`. Deploy the full stack, run a sample Temporal workflow, create an Airbyte source/destination/connection, run a sync job, verify the health endpoint, test ingress via Traefik, refresh from published charm, and scale 1→3→1 — genuine behaviour assertions, and correctly handle Temporal namespace creation.
- **Static analysis**: `ruff check src/ tests/ --select E,F,B` shows only 4 E501 line-length violations; `--select F,B` and `--select SIM` pass clean; `codespell src/ tests/` passes clean.
- **Coverage gaps relative to findings**:
  - No test for the `WORKLOAD_API_BEARER_TOKEN` Helm artifact.
  - No test for the `charm.meta.relations` mutation side effect in `MinioRelation.get_interfaces()`.
  - No test for the S3 `error_code` int-conversion bug (`src/s3_helpers.py:60`).
  - No test for missing Temporal namespace (integration tests always create it).
  - No test for the stopped-service-not-detected issue (unit tests mock check status, don't simulate stopped services).
  - No test for the 0–5 minute maintenance window after successful reconcile.
  - No test for invalid `temporal-host` config values.
- **Test infrastructure**: CI uses `canonical/operator-workflows` with self-hosted runners and `canonical-k8s`, building the OCI rock as part of the integration test pipeline.
- **Known issue**: open issue #54 documents `extra-user-roles: admin` incompatibility with postgresql-k8s 16/stable (see finding above).

## Docs

- **README**: good — lists key dependencies, features, and observability notes; accurately describes COS integration and community edition's lack of OTLP metrics. Lists Temporal as a key dependency without explaining how to deploy or configure it.
- **Tutorial**: structured 4-part walkthrough. Step 4 contains the most errors — see findings above (non-existent `temporal relation not ready` status, non-existent `airbyte-webhooks-k8s` sample output, `postgresql` vs `postgresql-k8s`, missing namespace-creation step).
- **How-to (secure deployments)**: TLS and OAuth2 sections reference non-existent `tls-secret-name`/`external-hostname` config options. The OAuth2 section references `oauth2-proxy-k8s` (a real charm) but the charm has no corresponding relation, requiring manual external configuration.
- **Reference (architecture)**: accurately describes ecosystem components and deployment topology.
- **Contributing guide**: clear `uv`/`tox`/`make` instructions.
- **Charmhub description**: matches `charmcraft.yaml` summary/description and lists correct relations.
- **Would a new operator succeed from docs alone?** No. They would get stuck on Temporal — the charm never goes active without it, the docs describe a non-existent relation status, and the namespace-creation step is undocumented. They would also fail configuring TLS via the documented `tls-secret-name` option. They could eventually succeed by discovering the `num-history-shards` requirement and namespace-creation CLI step independently.

## Open questions

- Is the missing Temporal relation deliberate, or planned? Integration tests deploy and require temporal-k8s, but the charm only references it via config.
- What is the correct `WORKLOAD_API_BEARER_TOKEN` value meant to be — generated, derived from a Juju secret, or intentionally empty?
- Why is the OCI image 2.8GB, and could a multi-stage rock reduce it below 1GB?
- Does the `2/edge` track (rev 30, commit `6f8d5d96`) correspond to a different branch not present in this repo's history? (unverified)
- When will postgresql-k8s support Juju 4? The charm is effectively pinned to Juju 3.x until it does.
- Will `extra_user_roles` be fixed for postgresql-k8s 16/stable — made configurable, auto-detected, or is 14/stable the indefinite target?
- What is the intended consumer for `send-otlp`? If it requires a non-standard charm (`opentelemetry-collector-k8s`), should the charm also expose a `tracing` relation for grafana-agent-k8s compatibility?
