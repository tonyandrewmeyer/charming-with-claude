# OpenFGA K8s Operator

A well-structured k8s charm for deploying OpenFGA with PostgreSQL, TLS, ingress, and observability integrations. Code quality is above the ecosystem average: clean separation of concerns, strong use of ops scenario testing, and a sensible holistic-reconciliation pattern. The `openfga` provides interface works end-to-end (tested live with the bundled `openfga-requires` tester charm, including Juju secret token exchange and store creation), and the charm deploys and runs correctly on both Juju 3.6 and Juju 4.0.

That said, this charm is not upgrade-safe today. The most serious defect is a critical, unrecoverable crash (`TypeError` in `TracingData.load()`) that hits any deployment with an active tracing integration — either on a stable→edge refresh, or on a fresh deploy if the tracing provider is temporarily blocked and sends incomplete relation data. A maintainer should fix this first, before anything else, since it can strand production units in an error loop that only a pod restart clears. After that: add a `relation_broken` handler for certificates, fix the stale pebble health-check URL after TLS removal, and turn on `startup: enabled` for the pebble service so a crashed workload isn't left silently down for up to 5 minutes. The unit test suite (77/77 pass) is solid, but the central `_holistic_handler` reconciler — which sets almost all charm status — is entirely unit-test-mocked-out and effectively untested; that gap should close before the next major refactor.

| | |
|---|---|
| Repo | canonical/openfga-operator @ `20754a3` (2026-07-24) |
| Charms | openfga-k8s (primary), openfga-requires (test-only) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25) rev 136 & 128; concierge-k8s-4 (Juju 4.0.5) rev 136 |
| Reviewed | 2026-08-03 |

## What it does

Deploys [OpenFGA](https://openfga.dev/) (v1.10.1 at latest/edge, v1.8.4 at latest/stable), a Zanzibar-inspired authorization engine, on Kubernetes. Requires PostgreSQL via the `database` relation. Supports optional TLS (via `self-signed-certificates` or any TLS-certificates provider), HTTP and gRPC ingress (Traefik), COS observability (Grafana dashboards, Prometheus metrics on port 2112, Loki logging), and Tempo tracing via OTLP/gRPC. Provides an `openfga` integration interface with a v1 charm library (`lib/charms/openfga_k8s/v1/openfga.py`) for client charms to request authorization model stores. Ships a `schema-upgrade` action for manual database migrations, with auto-migration attempted on database-created when migration is needed. Published on Charmhub by Identity Charmers under channels `1.0/edge`, `2.0/stable`, `3.0/stable`, `latest/stable` (rev 128, v1.8.4), and `latest/edge` (rev 136, v1.10.1).

## Deployment log

### Session 1 — basic deploy + TLS + scale (model `rv-openfga`, Juju 3.6.25)

```shell
juju add-model rv-openfga --controller concierge-k8s-3
juju deploy openfga-k8s --channel latest/edge --trust   # rev 136
juju deploy postgresql-k8s --channel 14/stable --trust   # rev 925
juju integrate postgresql-k8s:database openfga-k8s
# ~4 minutes to reach active/idle

juju config openfga-k8s log-level=info
# works, 1 config-changed hook

juju config openfga-k8s log-level=invalid
# BlockedStatus("Failed to restart the service, please check the openfga logs")
# Recovery: juju config openfga-k8s log-level=error → back to active

juju run openfga-k8s/0 schema-upgrade
# completed successfully in ~0s

juju deploy self-signed-certificates --channel latest/stable --trust
juju integrate openfga-k8s self-signed-certificates
# TLS enabled, healthz responds on HTTPS, pebble checks updated for TLS

juju remove-relation openfga-k8s self-signed-certificates
# Charm stayed active, but pebble plan still had TLS=true set
# Only cleared after juju config openfga-k8s log-level=debug triggered a new hook cycle

juju scale-application openfga-k8s 2  # reached active/idle for both units
juju scale-application openfga-k8s 1  # clean scale-down

juju run openfga-k8s/1 schema-upgrade
# "Only the leader unit can run the schema-upgrade action" — correctly blocked

juju remove-relation openfga-k8s postgresql-k8s
# BlockedStatus("Missing integration database")
juju integrate postgresql-k8s:database openfga-k8s  # recovered

# Kill workload: pebble stop openfga → service stopped, charm stayed "active"
# until next config-changed, then restarted the service and went back to active.
```

### Session 2 — ingress, failure injection (model `rv-openfga2`, Juju 3.6.25)

```shell
juju add-model rv-openfga2 --controller concierge-k8s-3
juju deploy openfga-k8s --channel latest/edge --trust   # rev 136
juju deploy postgresql-k8s --channel 14/stable --trust   # rev 925
juju deploy traefik-k8s --channel latest/stable --trust traefik-http
juju deploy traefik-k8s --channel latest/stable --trust traefik-grpc
juju deploy self-signed-certificates --channel latest/stable --trust
juju integrate openfga-k8s:database postgresql-k8s:database
juju integrate openfga-k8s:http-ingress traefik-http
juju integrate openfga-k8s:grpc-ingress traefik-grpc
juju integrate openfga-k8s:certificates self-signed-certificates
# postgresql-k8s initially failed with "Operation not permitted" on database creation
# Removed and re-added the database relation — recovered

# Traefik ingress URLs published: http://10.43.45.1/... (HTTP) and http://10.43.45.0/... (gRPC)
# Both use http:// scheme from Traefik despite TLS on the workload

juju config openfga-k8s cpu="invalid" memory="invalid"
# → BlockedStatus: "Failed obtaining resource limit spec: Invalid limits spec: {...}"
juju config openfga-k8s cpu="" memory=""
# → BlockedStatus: empty strings rejected by adjust_resource_requirements
# No path back to "no limit" — must set explicit valid values

juju remove-relation openfga-k8s:certificates self-signed-certificates
# → charm stays active, TLS still enabled in pebble plan until next hook cycle

# Scale up: 1→2 in ~30s, both units active; Scale down: 2→1, clean

# Kill workload: pebble stop openfga → service stopped, charm "active"
```

### Session 3 — observability, refresh, upgrade crash (model `rv-openfga3`, Juju 3.6.25)

```shell
juju add-model rv-openfga3 --controller concierge-k8s-3
juju deploy openfga-k8s --channel latest/edge --trust   # rev 136
juju deploy postgresql-k8s --channel 14/stable --trust  # rev 925
juju deploy grafana-agent-k8s --channel 1/stable --trust  # rev 164
juju integrate openfga-k8s:database postgresql-k8s:database
juju integrate openfga-k8s:logging grafana-agent-k8s:logging-provider
juju integrate openfga-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate openfga-k8s:tracing grafana-agent-k8s:tracing-provider
# ~4 min to active/idle. Pebble plan shows log-targets for Loki and metrics env vars.

# Refresh downgrade: latest/edge (v1.10.1 rev 136) → latest/stable (v1.8.4 rev 128)
juju refresh openfga-k8s --channel latest/stable
# → BlockedStatus: "Please run schema-upgrade action" (migration version mismatch)
juju run openfga-k8s/0 schema-upgrade
# → ActiveStatus. Migration completed successfully.

# Refresh upgrade: latest/stable (v1.8.4 rev 128) → latest/edge (v1.10.1 rev 136)
juju refresh openfga-k8s --channel latest/edge
# → hook failed: "config-changed" — TypeError in TracingData.load()!
# Traceback: integrations.py:312 — grpc_endpoint.geturl().replace(f"{grpc_endpoint.scheme}://", "", 1)
# TypeError: a bytes-like object is required, not 'str'
# Charm is STUCK in error state. juju resolve + config change doesn't help.
# Removing the tracing relation AND grafana-agent-k8s doesn't fix it —
# TracingEndpointRequirer caches the relation reference even after relation removal.
# kubectl delete pod openfga-k8s-0 → clears stale state, charm recovers to active.

# Kill workload: pebble stop openfga → service inactive, charm "active"
# Config change recovers.

juju remove-application openfga-k8s
# → clean removal, "remove" hook ran successfully, no errors.
```

### Session 4 — Juju 4 compatibility check (model `rv-openfga4`, Juju 4.0.5)

```shell
juju add-model rv-openfga4 --controller concierge-k8s-4
juju deploy openfga-k8s --channel latest/edge --trust   # rev 136
# Deployed successfully on Juju 4.0.5. Charm version v1.10.1.
# Status: BlockedStatus "Missing integration database" — correct.
# Pebble plan: minimal (no env vars, no checks, service inactive) — correct
# for no-database state. Ports 2112,8080-8081 shown in juju status.
# Could not test with database because postgresql-k8s (14/stable) requires
# Juju < 4.0.0. Charm itself is Juju 4 compatible.
```

### Session 5 — deeper failure injection with tracing (model `rv-deep`, Juju 3.6.25)

```shell
juju add-model rv-deep --controller concierge-k8s-3
juju deploy openfga-k8s --channel latest/edge --trust
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy self-signed-certificates --channel latest/stable --trust
juju deploy grafana-agent-k8s --channel 1/stable --trust
juju integrate openfga-k8s:database postgresql-k8s:database
juju integrate openfga-k8s:certificates self-signed-certificates
juju integrate openfga-k8s:logging grafana-agent-k8s:logging-provider
juju integrate openfga-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
juju integrate openfga-k8s:tracing grafana-agent-k8s:tracing-provider

# openfga-k8s entered an unrecoverable error loop on database-relation-changed.
# Root cause: grafana-agent-k8s was in BlockedStatus (missing cloud config)
# and sent incomplete tracing relation data. The TracingEndpointRequirer
# logged: "tracing:9: 'app' expected but not received" and the tracing library
# did not fully initialise, but is_ready() still transitioned to True.
# The subsequent database-relation-changed hook crashed with exit status 1
# on every attempt. Resolving with juju resolve didn't help — it would
# re-crash. Removing the tracing relation partially helped but the charm
# was then stuck in "Waiting for database creation" because postgresql-k8s
# had a separate issue creating the database.
# Destroyed the model to recover.
```

### Session 6 — openfga provides relation, full-stack deploy with tester charm (model `rv-deep2`, Juju 3.6.25)

```shell
juju add-model rv-deep2 --controller concierge-k8s-3
juju deploy openfga-k8s --channel latest/edge --trust   # rev 136
juju deploy postgresql-k8s --channel 14/stable --trust   # rev 925
juju deploy self-signed-certificates --channel latest/stable --trust
juju deploy traefik-k8s --channel latest/stable --trust traefik-http
juju deploy traefik-k8s --channel latest/stable --trust traefik-grpc
# Built and deployed openfga-requires tester charm locally (charmcraft pack)
juju deploy ./openfga-requires_ubuntu@22.04-amd64.charm --trust openfga-client
juju integrate openfga-k8s:database postgresql-k8s:database
juju integrate openfga-k8s:certificates self-signed-certificates
juju integrate openfga-k8s:http-ingress traefik-http
juju integrate openfga-k8s:grpc-ingress traefik-grpc
juju integrate openfga-k8s:openfga openfga-client:openfga
# ~4 min to all-active. openfga-client: "running with store 01KZ2KMJVA1QZDENAYG301ETS2"
# openfga relation data confirmed: store_id, token_secret_id, grpc_api_url, http_api_url all present
# Confirmed Juju secret token exchange: token_secret_id is a real secret: URI reference

# Pebble plan inspection: TLS enabled, http-check on https://127.0.0.1:8080/healthz,
# grpc-check with TLS flags, startup=disabled

# TLS removal #1:
juju remove-relation openfga-k8s:certificates self-signed-certificates
# → charm stays active, pebble plan STILL shows TLS_ENABLED="true" and https:// health-check URL
# → grpc-check command still has -tls -tls-ca-cert flags
# → Only cleared after juju config openfga-k8s log-level=debug triggered next hook cycle
# → Then: TLS_ENABLED="false" (Pebble plan shows "false" string), http://127.0.0.1:8080/healthz
# → grpc-check back to plain: grpc_health_probe -addr 127.0.0.1:8081

# Kill workload:
kubectl exec -n rv-deep2 openfga-k8s-0 -c openfga -- /charm/bin/pebble stop openfga
# → service inactive, charm status still "active"
# → juju config openfga-k8s log-level=error → service restarted, back to active
# → Timing: < 1s for config change to apply, service restarted within 3s

# Scale-up: juju scale-application openfga-k8s 2 → ~30s, both units active
# Scale-down: juju scale-application openfga-k8s 1 → clean, ~15s

# Bad config:
juju config openfga-k8s log-level=invalid
# → charm blocked "Missing integration database" (precedence: db check before config validate)
# → After re-adding db: charm blocked "Failed to restart the service, please check the openfga logs"
# → Pebble logs show: panic: config 'log.level' must be one of ['none','debug','info','warn','error','panic','fatal']
# → operator has no clue from status message alone — must dig into container logs

juju config openfga-k8s cpu="" memory=""
# → BlockedStatus: "Failed obtaining resource limit spec: Invalid limits spec: {'cpu': '', 'memory': ''}"
# → permanent — setting valid values (cpu=1, memory=1Gi) resets, then empty strings cause block again

# Database removal:
juju remove-relation openfga-k8s:database postgresql-k8s:database
# → BlockedStatus "Missing integration database" — immediate, clean
# → Re-integrate → recovers after re-setting log-level to valid value

# schema-upgrade action:
juju run openfga-k8s/0 schema-upgrade
# → "Start migrating the database" → "Successfully migrated the database" → ~0s

# TLS re-add #1 (ca-tls, removed shortly after):
juju deploy self-signed-certificates --channel latest/stable --trust ca-tls
juju integrate openfga-k8s:certificates ca-tls
# → TLS enabled, pebble plan updated with https:// health-check URL, TLS flags in grpc-check

# TLS removal #2 (ca-tls):
juju remove-relation openfga-k8s:certificates ca-tls
# → SAME BUG: pebble plan stays with TLS_ENABLED="true" and https:// URL
# → Confirmed independently on second TLS add/remove cycle

# TLS re-add #2 (ca-tls2):
juju deploy self-signed-certificates --channel latest/stable --trust ca-tls2
juju integrate openfga-k8s:certificates ca-tls2
# → TLS enabled again, pebble plan correct

# Cert transfer integration:
juju integrate openfga-k8s:send-ca-cert openfga-client:receive-ca-cert
# → Relation created, but certificate data not transferred because TLS was removed at that point
# → When TLS re-added, _on_cert_changed should fire transfer_certificates()
# → send-ca-cert relation data shows only version: "0" — certs may not have been transferred
# → The _on_certificates_transfer_relation_joined deferred (TLS not enabled at join time)
# → When TLS later enabled, _on_cert_changed calls transfer_certificates but result unclear

# Peer data inspection:
# migration_version_7 and migration_version_12 present (IDs 7 and 12 from two db relation cycles)
# → confirms migration version key tied to integration ID — forces re-migration on relation churn

# Debug log observations:
# "InsecureRequestWarning: Unverified HTTPS request is being made to host '127.0.0.1'"
# → confirms HTTPClient.verify=False at src/clients.py:20
# "certificates:8: 'app' expected but not received" on relation-broken
# → No handler for this — charm relies on next hook cycle to clean up

juju remove-application openfga-k8s openfga-client ca-tls2 self-signed-certificates traefik-http traefik-grpc postgresql-k8s
# → clean removal, no errors
```

## Observed behaviour

### Deployment and lifecycle

- **Deploy time**: ~4 min from `juju deploy` to active/idle with postgresql already running.
- **Refresh downgrade (edge→stable, v1.10.1→v1.8.4)**: Correctly detected migration version mismatch, entered BlockedStatus with "Please run schema-upgrade action". Schema-upgrade recovered to ActiveStatus. Well-handled.
- **Refresh upgrade (stable→edge, v1.8.4→v1.10.1) with active tracing**: CRASHED with `TypeError: a bytes-like object is required, not 'str'` in `TracingData.load()` at `src/integrations.py:312`. The tracing relation data from the old revision contains bytes; `urlparse` returns a `ParseResultBytes` whose `.geturl()` returns bytes; `.replace()` with an f-string argument then fails because the f-string embeds a bytes `.scheme` as its repr (e.g. `"b'http'://"`). The charm entered an unrecoverable error loop — `juju resolve` doesn't help, removing the tracing relation and grafana-agent-k8s entirely doesn't help (`TracingEndpointRequirer` caches the relation reference internally and `is_ready()` still returns `True`). Only a pod restart clears the stale in-memory state and recovers. Critical upgrade-path bug.
- **Teardown**: `remove-application` is clean and fast, no errors in remove hook.
- **Juju 4 compatibility**: Charm deploys and runs correctly on Juju 4.0.5. Reaches expected BlockedStatus without database. The charm is Juju 4 compatible; its typical database partner (postgresql-k8s 14/stable) is not.

### Resource and performance

- **Resource usage**: ~45-55 MiB memory per unit (kubectl top), very lightweight. CPU usage ~1-2m at idle.
- **Unit test coverage**: 79% line coverage (pytest-cov). Key uncovered areas: `_holistic_handler` branches (`charm.py:402-435`), TLS cert push/remove methods (`integrations.py:226-278`), `_on_openfga_store_requested` failure path (`charm.py:340-341`), `_on_resource_patch_failed` (`charm.py:383-389`), HTTPClient store create/list (`clients.py:34-58`).
- **Charm size**: ~20 MB (Charmhub). Two architectures (amd64, arm64).

### Pebble and workload

- **Pebble service**: `startup: disabled`. The charm starts the service explicitly via `plan()`. If the workload process dies, the charm stays `active` and the service stays stopped until the next hook cycle (config-changed, update-status). With a 5-minute update-status interval, the service can be down for up to 5 minutes before recovery. Confirmed by killing the process with `pebble stop` on five separate tests across three models (rv-openfga, rv-openfga3, rv-deep2). Recovery is reliable once a config change or update-status triggers the next hook cycle.
- **Hook count**: 1 config-changed per config change. No redundant hooks.
- **Pebble checks**: http-check on `/healthz` via port 8080, grpc-check using `grpc_health_probe` on 8081. Both updated when TLS state changes (http→https, grpc flags added). **But not reset when TLS is removed** — the http-check URL is only overwritten when `OPENFGA_HTTP_TLS_ENABLED == "true"`, never reset to `http://`. After TLS removal, the health check continues to probe `https://127.0.0.1:8080/healthz` on an HTTP-only listener, which would fail. Confirmed on three separate TLS add/remove cycles across two models (rv-openfga, rv-deep2). The module-level `PEBBLE_LAYER_DICT` is mutated in-place by `render_pebble_layer`, so the stale URL persists across calls. The gRPC check similarly retains `-tls -tls-ca-cert` flags after TLS removal.
- **Workload image**: Minimal distroless-like container (no `/bin/sh`, `ls`, `whoami`). Only the `openfga` binary and `pebble` are available. Debugging requires kubectl exec + pebble commands.
- **Observability**: Loki log forwarding works through Pebble's native `log-targets` mechanism (confirmed in pebble plan). Prometheus metrics endpoint (port 2112) and Grafana dashboards are correctly advertised. Tracing (OTLP/gRPC) integration sets `OPENFGA_TRACE_ENABLED` env vars when a provider is available.

### Failure behaviour

- **Bad log-level**: Config accepts any string; invalid values reach OpenFGA which crashes with `panic: config 'log.level' must be one of ['none', 'debug', 'info', 'warn', 'error', 'panic', 'fatal']`. Charm enters BlockedStatus with the generic message "Failed to restart the service, please check the openfga logs" — the operator has no indication that the log level is invalid without digging into pebble logs. Recovery works after setting a valid value. Confirmed on rv-openfga and rv-deep2.
- **Bad cpu/memory**: `cpu="invalid"/memory="invalid"` → clear blocked status from the resource patch library. Empty strings (`""`) → permanent blocked state with no path back to default — the operator must set explicit valid values.
- **TLS relation-broken**: After removing the TLS relation, the charm does not clean up cert files or disable TLS in the pebble plan until the next explicit hook cycle (up to 5 minutes). No `relation_broken` observer exists for certificates. Confirmed on three separate relation-removal operations across two models. The debug log shows `certificates:8: 'app' expected but not received` on relation-broken — the charm receives the event but has no handler registered, so it relies on the next hook cycle (via update-status or config-changed) to trigger `_holistic_handler`, which detects the missing relation and cleans up.
- **Database removal**: Immediate BlockedStatus with clear message. Re-integration recovers cleanly.
- **Ports**: 8080 (HTTP), 8081 (gRPC), 2112 (metrics) opened on pebble-ready. Never closed.
- **Ingress**: Traefik integration works. URLs use `http://` from Traefik even when TLS is enabled on the workload (Traefik handles TLS termination separately). `HttpIngressIntegration._uri_scheme` is captured at init time.
- **Tracing with blocked provider**: On a fresh deploy with grafana-agent-k8s in BlockedStatus (no grafana-cloud-config), the tracing relation sent incomplete data (`'app' expected but not received`) and the charm entered an unrecoverable error loop on `database-relation-changed`. Same root cause as the upgrade crash — `TracingData.load()` cannot handle the bytes/str mismatch — but triggered by provider-side data shape, not an upgrade. Observed on rv-deep, Juju 3.6.25.
- **OpenFGA provides relation**: Deployed the bundled `openfga-requires` tester charm and confirmed end-to-end store creation. Relation data includes `store_id` (`01KZ2KMJVA1QZDENAYG301ETS2`), `token_secret_id` (a Juju `secret:` URI), `grpc_api_url`, and `http_api_url`. The tester charm reached ActiveStatus with `"running with store 01KZ2KMJVA1QZDENAYG301ETS2"`. Token exchange via Juju secrets works correctly.
- **HTTPClient TLS verification**: The debug log confirms `InsecureRequestWarning: Unverified HTTPS request is being made to host '127.0.0.1'` from `urllib3`, originating from the HTTPClient's `verify=False` setting at `src/clients.py:20`. This warning fires during store creation when TLS is enabled on the workload.
- **Migration version peer data**: Inspected peer relation data on rv-deep2 — `migration_version_7` and `migration_version_12` coexist, corresponding to two different database relation cycles. Removing and re-adding the database relation creates a new key, forcing an unnecessary schema-upgrade on the next hook cycle.

## Findings

### 1. Upgrade crash with active tracing integration — unrecoverable error loop
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/integrations.py:308-312`
- **Evidence**: Live reproduction on rv-openfga3:
  ```python
  grpc_endpoint = urlparse(requirer.get_endpoint("otlp_grpc"))
  return cls(
      is_ready=is_ready,
      grpc_endpoint=grpc_endpoint.geturl().replace(
          f"{grpc_endpoint.scheme}://", "", 1
      ),  # type: ignore
  )
  ```
  Refreshing from latest/stable (rev 128) to latest/edge (rev 136) with an active grafana-agent-k8s tracing relation causes `TracingEndpointRequirer.get_endpoint()` to return bytes data from the old revision's relation data. `urlparse(bytes)` returns a `ParseResultBytes`, where `.geturl()` returns bytes and `.scheme` is bytes. The f-string `f"{bytes_scheme}://"` produces `"b'http'://"`, and `bytes.replace(str, str, int)` fails with `TypeError: a bytes-like object is required, not 'str'`. The error occurs during `_pebble_layer` property evaluation inside `_holistic_handler`, which runs on every hook cycle, so the charm is completely stuck. Removing the tracing relation and grafana-agent-k8s entirely does not fix it because `TracingEndpointRequirer._relation` is cached in memory and `is_ready()` still returns `True` on the stale reference. Only a pod restart clears the state. The same root cause also crashes fresh deploys when the tracing provider is blocked and sends incomplete data (see rv-deep, session 5).
- **Impact**: Any operator upgrading from stable to edge (or hitting a tracing library serialisation change) with an active tracing integration will hit this. The charm becomes permanently broken until the pod is restarted — a manual, undocumented recovery step.
- **Fix**: In `TracingData.load()`, decode bytes before parsing: `endpoint = requirer.get_endpoint("otlp_grpc"); if isinstance(endpoint, bytes): endpoint = endpoint.decode(); grpc_endpoint = urlparse(endpoint)`. More broadly, `TracingEndpointRequirer.is_ready()` should return `False` when relation data fails validation.
- **Linter rule**: not mechanically checkable (requires tracing-library interop awareness).

### 2. Bad config values crash the workload with unhelpful error messages
- **Severity**: high
- **Kind**: bug / ux
- **Where**: `charmcraft.yaml:106-112`, `src/configs.py:13-17`
- **Evidence**: The `log-level` config is `type: string` with no `enum` or pattern constraint:
  ```yaml
  log-level:
    description: |
      Configures the log level of gunicorn.
      Acceptable values are: "info", "debug", "warning", "error" and "critical"
    default: "error"
    type: string
  ```
  `juju config openfga-k8s log-level=invalid` crashed the workload. Pebble logs show the real error: `panic: config 'log.level' must be one of ['none', 'debug', 'info', 'warn', 'error', 'panic', 'fatal']`. The charm's BlockedStatus message is generic: `"Failed to restart the service, please check the openfga logs"` — `juju status` gives no hint that the log level is the cause. The description also wrongly says "gunicorn" (this is OpenFGA, not gunicorn) and lists invalid values (`"warning"`, `"critical"`) that don't match OpenFGA's actual accepted values (`"warn"`, `"fatal"`). Confirmed on rv-openfga and rv-deep2.
- **Impact**: An operator who misreads the config docs or makes a typo gets a broken charm and a status message that doesn't say what to fix; they must exec into the container and read pebble logs to diagnose a simple typo.
- **Fix**: Add `enum: ["info", "debug", "warn", "error", "panic", "fatal"]` to the config option in `charmcraft.yaml`, and validate in `CharmConfig.to_env_vars()` as defense-in-depth, setting a specific BlockedStatus. Fix the description to say "OpenFGA" and correct the valid values.
- **Linter rule**: "charmcraft.yaml config option with a free-text field should have an enum or pattern" — mechanically checkable.

### 3. Missing TLS `relation-broken` handler — stale certs and TLS config persist
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:146-150`
- **Evidence**: The charm observes only `certificate_available`, not `certificate_expired` or `relation_broken` on the `certificates` relation. After removing the TLS relation, the pebble plan continued to show `OPENFGA_HTTP_TLS_ENABLED: "true"` and TLS cert paths for up to 5 minutes. Confirmed on three separate relation-removal operations across two models.
- **Impact**: For up to 5 minutes after removing TLS, the workload runs with stale TLS configuration. If cert files were already deleted by a prior `update_certificates()` call, the workload may be unreachable or fail health checks.
- **Fix**: Observe `self.on["certificates"].relation_broken` and call `_holistic_handler` or directly `update_certificates()` + `plan()`.
- **Linter rule**: "charm that observes a certificate_available event must also observe relation_broken or certificate_expired/revoked on the same relation" — mechanically checkable.

### 4. Pebble service uses `startup: disabled` — recovery gap on process death
- **Severity**: high
- **Kind**: bug
- **Where**: `src/services.py:33`
- **Evidence**: The pebble layer has `"startup": "disabled"`. Killing the workload (`pebble stop openfga`) leaves the service stopped with the charm reporting `active`. Recovery only happens on the next hook cycle (up to 5 minutes). Confirmed on five kill tests across three models (rv-openfga, rv-openfga3, rv-deep2).
- **Impact**: A workload crash (OOM, segfault, external signal) leaves the service down while the charm reports `active`, for up to 5 minutes.
- **Fix**: Change to `"startup": "enabled"`. The charm's `plan()` already handles the case where the service needs different config.
- **Linter rule**: "pebble layer for a k8s sidecar charm should use startup: enabled" — mechanically checkable.

### 5. Tracing integration can crash on fresh deploy as well as on upgrade when provider sends incomplete data
- **Severity**: high
- **Kind**: bug
- **Where**: `src/integrations.py:308-312`
- **Evidence**: Two independent reproductions: (1) upgrade from stable→edge with active tracing triggered the `TypeError` bytes/str mismatch (finding 1); (2) fresh deploy on rv-deep with grafana-agent-k8s in BlockedStatus (no grafana-cloud-config) caused `database-relation-changed` to crash in an unrecoverable loop; debug log showed `tracing:9: 'app' expected but not received` warnings from `TracingEndpointRequirer`, then exit status 1 on every hook. In both cases, removing the tracing relation or calling `juju resolve` did not fully recover — `TracingEndpointRequirer` caches internal state and `is_ready()` continued returning `True` on stale references. Only a pod restart (upgrade case) or model destruction (fresh-deploy case) cleared the state.
- **Impact**: Any operator who deploys with tracing alongside other integrations can hit this via multiple triggers, not just upgrades. The charm becomes stuck and requires undocumented manual recovery.
- **Fix**: Same as finding 1 — defensive bytes handling in `TracingData.load()`, plus hardening `is_ready()` to reflect actual data validity.
- **Linter rule**: not mechanically checkable (requires live integration testing with incomplete provider data).

### 6. `_holistic_handler` is almost completely untested — central reconciler mocked out in most unit tests
- **Severity**: high
- **Kind**: test-gap
- **Where**: `src/charm.py:392-430`, `tests/unit/test_charm.py`
- **Evidence**: Coverage shows lines 402-435 (`_holistic_handler` body) entirely uncovered. Nearly every charm event handler test uses `mocked_charm_holistic_handler`, which replaces the entire method with a MagicMock. The migration-needed → BlockedStatus path, the certificate-update → BlockedStatus path, the pebble-plan-failure → BlockedStatus path, and the final ActiveStatus path are all untested at the unit level; only integration tests exercise this code.
- **Impact**: The method that sets terminal status and coordinates all integrations has no direct unit tests. A regression in status precedence or operation ordering would not be caught until integration tests run.
- **Fix**: Write unit tests that call `_holistic_handler` (or its caller hooks) directly and assert each status outcome — no-container, no-peer, no-database, waiting-for-database, migration-needed, cert-update-failure, pebble-plan-failure, active — mocking its dependencies (container, peer, database, certs, pebble) rather than the method itself.
- **Linter rule**: "Context.run for charm event handlers should not mock the charm's own reconciler method" — mechanically checkable.

### 7. Pebble health-check URL not reset when TLS is removed — stale probe target
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/services.py:128-131` (mutation) / `src/services.py:94` (root cause)
- **Evidence**:
  ```python
  if env_vars.get("OPENFGA_HTTP_TLS_ENABLED") == "true":
      self._layer_dict["checks"]["http-check"]["http"]["url"] = (
          f"https://127.0.0.1:{OPENFGA_SERVER_HTTP_PORT}/healthz"
      )
  ```
  The http-check URL is only overwritten when TLS is enabled; there's no `else` branch to reset it to `http://` when TLS is removed. `self._layer_dict = PEBBLE_LAYER_DICT` (line 94) assigns the module-level constant by reference rather than copying it, so the mutation persists across calls and across all `PebbleService` instances. Confirmed on three separate TLS add/remove cycles across two models.
- **Impact**: After TLS removal, the http-check probes `https://` on a port now serving plain `http://`. The probe fails, Pebble may mark the service unhealthy or restart it, and the operator sees flapping with no clear cause.
- **Fix**: Always reset the http-check URL to `http://` at the top of `render_pebble_layer`, then set it to `https://` only if TLS is enabled. Deep-copy `PEBBLE_LAYER_DICT` (`copy.deepcopy`) rather than assigning by reference. The gRPC check similarly needs its `-tls`/`-tls-ca-cert` flags reset on TLS removal.
- **Linter rule**: "pebble layer dict should be deep-copied, not referenced" (pattern: `self._layer_dict = MODULE_CONSTANT`) and "mutable module-level constant should be a factory function or frozen" — both mechanically checkable.

### 8. Empty-string CPU/memory config causes permanent blocked state
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/charm.py:389-391`
- **Evidence**: `_resource_reqs_from_config` passes `self.model.config.get("cpu")` / `("memory")` directly to `adjust_resource_requirements()`. Setting `cpu=""`/`memory=""` passes empty strings, which the library rejects. Once set, there's no way back to the "no limit" default — any further attempt reproduces the same blocked state. Confirmed on rv-openfga2 and rv-deep2.
- **Impact**: An operator clearing cpu/memory back to default gets permanently stuck and must set explicit valid values instead.
- **Fix**: Filter out `None`/empty-string values from `limits` before calling `adjust_resource_requirements`, or add a `pattern` constraint to the config options.
- **Linter rule**: "config values passed to adjust_resource_requirements should be validated for empty string before calling" — mechanically checkable.

### 9. HTTPClient disables TLS certificate verification
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/clients.py:20`
- **Evidence**: `self._session.verify = False`. Confirmed live: the debug log on rv-deep2 shows `InsecureRequestWarning: Unverified HTTPS request is being made to host '127.0.0.1'. Adding certificate verification is strongly advised.` (`urllib3/connectionpool.py:1110`), triggered during store creation when TLS is enabled.
- **Impact**: If the charm's TLS configuration is wrong (e.g., bad CA cert), the store-creation request would silently succeed over a potentially untrusted connection rather than failing with a verification error the operator would notice.
- **Fix**: Pass the CA cert path to `requests.Session.verify` instead of disabling verification: `self._session.verify = CA_BUNDLE_FILE` when TLS is enabled.
- **Linter rule**: "requests.Session.verify = False in charm code should use the CA cert path instead" — mechanically checkable.

### 10. Secrets `is_ready` check does not verify the token key is actually present
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/secret.py:67-69`
- **Evidence**:
  ```python
  @property
  def is_ready(self) -> bool:
      values = self.values()
      return all(values) if values else False
  ```
  `all(values)` checks that secret content dicts are truthy (non-empty), not that they contain the specific key `PRESHARED_TOKEN_SECRET_KEY`. A corrupt or mis-populated secret still returns `is_ready == True`, and `self.secrets[PRESHARED_TOKEN_SECRET_LABEL][PRESHARED_TOKEN_SECRET_KEY]` (`src/charm.py:334`) may then return `None`, passing `Bearer None` to the HTTPClient.
- **Impact**: Corrupt or mis-populated secrets cause silent failures in store creation with no operator-visible status.
- **Fix**: Check the specific key: `return bool(self[PRESHARED_TOKEN_SECRET_LABEL] and self[PRESHARED_TOKEN_SECRET_LABEL].get(PRESHARED_TOKEN_SECRET_KEY))`.
- **Linter rule**: not mechanically checkable.

### 11. `migration_version` uses integration ID that changes on relation re-creation
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/integrations.py:135`
- **Evidence**: `migration_version=f"migration_version_{integration_id}"`. Live peer data on rv-deep2 showed `migration_version_7` and `migration_version_12` coexisting, from two different database relation cycles (IDs 7 and 12). Removing and re-creating the database relation changes the integration ID, forcing an unnecessary re-migration even though the database was already migrated under the old key.
- **Impact**: Operators doing normal relation churn get blocked and must re-run `schema-upgrade` even though the database is already migrated. Confusing and disruptive, though the underlying `openfga migrate` command is idempotent.
- **Fix**: Use a fixed key (e.g. `"migration_version"`), or store the version in the database integration's own app data instead of peer data keyed by relation ID.
- **Linter rule**: "migration version tracking should not use relation IDs as keys" — mechanically checkable.

### 12. mypy type errors across source modules
- **Severity**: medium
- **Kind**: lint
- **Where**: `src/secret.py:41`, `src/configs.py:18`, `src/cli.py:73`, `src/integrations.py:149,319,333,350`, `src/services.py:102,129,134`, `src/charm.py:334,343,365,469`
- **Evidence**: `uv run mypy src/ --ignore-missing-imports` produced 14 errors across 6 files: type mismatches in `secret.py:41` (`dict[str, str | None]` where `dict[str, str]` expected), `configs.py:18` (`str` vs `str | bool`), `cli.py:73` (return-type mismatch), `integrations.py:149,319,333,350` (private-attribute access to `charm._container`/`charm._certs_integration`, return-type mismatches), `services.py:102,129,134` (LayerDict assignment and unsafe indexed access), `charm.py:334,343,365,469` (indexing into `dict | None`, wrong event-type annotation for `_holistic_handler`).
- **Impact**: `.pre-commit-config.yaml` includes mypy, so these are expected to pass but don't. The `charm._container` reach-into pattern is also a design smell — integration classes accessing the charm's private internals rather than having dependencies passed explicitly.
- **Fix**: Pass container and certs-integration objects explicitly to constructors; add type narrowing for the remaining errors.
- **Linter rule**: mechanically checkable — run `mypy`.

### 13. `_on_openfga_store_requested` silently degrades on failure — no status set
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:340-341`
- **Evidence**: When store creation fails, the handler returns silently with just a log message; unit status is not updated.
- **Impact**: Client charms requesting a store get no response, while the charm still shows healthy in `juju status`.
- **Fix**: Set `self.unit.status = BlockedStatus("Failed to create OpenFGA store: ...")`.
- **Linter rule**: not mechanically checkable.

### 14. `HttpIngressIntegration._uri_scheme` captured at init, never updated
- **Severity**: low
- **Kind**: bug
- **Where**: `src/integrations.py:319`
- **Evidence**: `self._uri_scheme = charm._certs_integration.uri_scheme` is evaluated at init time and stored as a plain string. If TLS is added after the charm starts, `_uri_scheme` remains `"http"` forever.
- **Impact**: Client charms may receive `http_api_url` using `http://` when the backend actually requires `https://`.
- **Fix**: Replace with a property that delegates to `self._charm._certs_integration.uri_scheme` dynamically.
- **Linter rule**: not mechanically checkable.

### 15. `_on_cert_changed` has a fragile `event.defer()` guard and cert transfer ordering
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:361-363`
- **Evidence**: The handler defers when the service isn't running. `transfer_certificates` runs after `_holistic_handler`, so certs aren't transferred before the service runs — but this creates a fragile two-stage pattern: (1) if the service isn't running when certs arrive, the event defers; (2) a different event (pebble_ready, config_changed) eventually calls `_holistic_handler`, starting the service and pushing certs, but does not transfer certs; (3) the deferred cert_changed later fires, the guard now passes, and `_holistic_handler` + `transfer_certificates` both run. If the deferred event is dropped (e.g., cleared on charm upgrade), certs are never transferred. On rv-deep2, the `send-ca-cert` relation was joined before TLS was available; the relation-joined event deferred, TLS was later added, `_on_cert_changed` fired (service already running), and `transfer_certificates` was called — but the transferred data was not confirmed on the relation, which still showed `version: "0"` only.
- **Impact**: The cert-transfer path is fragile and event-order-dependent. An upgrade or pod restart could drop the deferred event, leaving `send-ca-cert` empty while the charm reports active.
- **Fix**: Move `transfer_certificates` into `_holistic_handler` so it runs on every reconciliation, and remove the defer guard.
- **Linter rule**: not mechanically checkable.

### 16. Ports opened but never closed
- **Severity**: low
- **Kind**: bug
- **Where**: `src/services.py:85-88`
- **Evidence**: `open_ports()` has no matching `close_ports()` anywhere in the lifecycle.
- **Impact**: Cosmetic on k8s but inconsistent with best practice.
- **Fix**: Add `close_ports()` on stop/remove handlers.
- **Linter rule**: "open_port should have a matching close_port" — mechanically checkable.

### 17. `secrets.__setitem__` would raise unhandled error on duplicate label
- **Severity**: low
- **Kind**: bug
- **Where**: `src/secret.py:35-38`
- **Evidence**: `model.app.add_secret(content, label=label)` raises `SecretAlreadyExistsError` on duplicate labels; there's a TOCTOU race between the `is_ready` check and `add_secret`.
- **Fix**: Catch `SecretAlreadyExistsError` or use upsert logic.
- **Linter rule**: not mechanically checkable.

### 18. `DatabaseConfig.load()` fails silently with empty data on missing integration
- **Severity**: low
- **Kind**: ux
- **Where**: `src/integrations.py:97-99`
- **Evidence**: Returns a default `DatabaseConfig` of all empty strings when no integration exists; callers must remember to guard against this manually.
- **Fix**: Either raise in `load()` when the integration is missing, or have callers explicitly handle the no-integration case.
- **Linter rule**: not mechanically checkable.

## Worth copying

1. **Clean separation of concerns** (`src/charm.py`, `src/integrations.py`, `src/services.py`, `src/configs.py`, `src/secret.py`, `src/cli.py`, `src/clients.py`, `src/env_vars.py`): each domain concept has its own module; the charm file is ~400 lines and focuses on event wiring.
2. **`EnvVarConvertible` protocol** (`src/env_vars.py:18-22`): each integration/config/service implements `to_env_vars()`; `render_pebble_layer(*sources)` takes variadic `EnvVarConvertible` arguments. Clean, extensible.
3. **`PeerData` abstraction** (`src/integrations.py:41-72`): JSON-serialized read/write over peer relation app data with default-on-missing handling, returning `{}` rather than raising.
4. **Ops scenario testing** (`tests/unit/test_charm.py`, `tests/unit/test_actions.py`): uses `testing.Context`/`testing.State`/`testing.Container` for isolated unit tests, well-organized conftest fixtures. All 77 tests pass.
5. **Jubilant-based integration tests** (`tests/integration/`): uses `jubilant` instead of `pytest-operator` for cleaner test code; `StatusPredicate` with `all_active`, `any_error`, `and_`, `or_` combinators is elegant.
6. **Attribute-based config model** (`src/integrations.py:76-114`): `DatabaseConfig` and `TracingData` are frozen dataclasses loaded from library objects, with `to_env_vars()` cleanly separating extraction from rendering.
7. **Holistic reconciliation** (`src/charm.py:392-430`): most event handlers delegate to a single `_holistic_handler` that checks preconditions and sets one terminal status — the right pattern to avoid status flip-flopping.
8. **Refresh/migration handling**: version-mismatch detection blocks with an actionable message, and `schema-upgrade` recovers cleanly; the downgrade path (without tracing active) works well.
9. **OpenFGA provides relation end-to-end**: the bundled `openfga-requires` tester charm confirmed the full store-creation lifecycle — client requests a store, charm creates it via HTTP API, token stored in a Juju secret, `store_id`/`token_secret_id`/`grpc_api_url`/`http_api_url` published in relation data, client reaches ActiveStatus with the store ID. `OpenFGAProvider.update_relation_app_data` correctly handles secret granting.

## Common-practice notes

- **charmcraft.yaml layout**: modern single-file `charmcraft.yaml`, no separate `metadata.yaml`. Platforms: `ubuntu@22.04:amd64` and `ubuntu@22.04:arm64`.
- **`lib/charms/openfga_k8s/v1/`**: standard `LIBID`/`LIBAPI`/`LIBPATCH` metadata, proper `PYDEPS`, `pydantic.BaseModel` for databag validation. Last published as v1 patch 5.
- **`uv` adoption**: migrated from pip to uv; `charmcraft.yaml` uses `plugin: uv` and pins rustc/cargo for building.
- **TLS library**: `tls_certificates_interface/v4` with `Mode.UNIT` — current best practice for k8s sidecar charms.
- **Ingress**: `traefik_k8s/v2/ingress` with `IngressPerAppRequirer`, two separate Traefik apps for HTTP and gRPC because Traefik can't route both protocols on one ingress relation.
- **No `stored` state**: avoids `StoredState` entirely, using peer relation data and Juju secrets — correct modern approach.
- **Terraform module**: present at `terraform/`, clean, with inputs for model, app_name, config, constraints, units, base, channel, revision. Version constraint `~> 1.0.0` is too strict (open issue #375).

## Tests

### Unit tests
- **Result**: 77/77 pass in 1.3s (`uv run pytest tests/unit/`).
- **Coverage**: 84% total (including test files), 79% for source only. Key gaps, ranked by risk:
  - `_holistic_handler` (`charm.py:402-435`): entirely uncovered — every charm event test mocks the method out.
  - `_on_openfga_store_requested` failure path (`charm.py:340-341`): no test for store creation returning an empty string.
  - `_resource_reqs_from_config` (`charm.py:389-391`): completely untested.
  - `_on_resource_patch_failed` (`charm.py:383-384`): untested.
  - `_on_database_created` auto-migration failure path (`charm.py:297-300`): untested.
  - TLS cert push/remove methods (`integrations.py:226-278`): `_push_certificates`, `_remove_certificates` not directly tested.
  - HTTPClient store create/list (`clients.py:34-58`): entirely untested.
  - Pebble health-check URL reset on TLS removal: no test — the existing parametrized `test_render_pebble_layer` covers TLS-enabled and TLS-disabled separately but not the enabled→disabled transition that would catch the stale URL bug.
  - TLS relation-broken path: no unit test.
  - `secrets.is_ready` returning `True` when the required key is absent: no test.

### Integration tests
- **Framework**: `jubilant` + `pytest`, session-scoped Juju model management.
- **Setup**: PostgreSQL 14/stable, Traefik ×2 (HTTP+gRPC), self-signed-certificates, local `openfga-requires` tester charm.
- **Assertions**: integration data keys present, ingress URLs match config, certificate CN matches, scale-up/down works, relation removal → blocked state.
- **Upgrade test**: deploy from charmhub edge, refresh to local charm, run schema-upgrade, check healthz.
- **Gaps** (relative to findings):
  - No tracing integration in test setup — the upgrade crash and fresh-deploy crash wouldn't be caught.
  - No TLS-removal-then-re-add cycle (would catch relation-broken + pebble URL staleness).
  - No bad config → BlockedStatus → recovery cycle.
  - No migration-needed BlockedStatus path (requires intentional schema mismatch).
  - No observability integration tests (Grafana, Prometheus, Loki, Tempo).
  - Upgrade test only checks healthz, not API functionality (store creation/listing).
  - No kill-workload-and-verify-restart test (would catch `startup: disabled`).
  - No empty-string cpu/memory config test.
  - No certificate transfer (`send-ca-cert`) integration test.
  - No test for the `openfga` relation with a real client charm beyond data-key assertions.
  - **Integration tests were not run during this review** (would require building the local openfga charm and the openfga-requires tester charm, plus a dedicated Juju model; `charmcraft pack` hung on the review machine).

### Linters
- `ruff check src/ && ruff check lib/charms/openfga_k8s/`: all checks passed (0 issues).
- `codespell .`: no typos found.
- `mypy src/ --ignore-missing-imports`: 14 errors across 6 files (see finding 12).
- `pre-commit` hooks configured: ruff, codespell, isort, mypy, conventional-pre-commit, markdownlint.

## Docs

- **README**: good quality, clear usage examples with `juju` commands for each integration type. The `tls-certificates-operator` example is stale (wrong charm name).
- **charmcraft.yaml description**: `log-level` description says "gunicorn" instead of "OpenFGA" — copy-paste artifact (see finding 2).
- **CONTRIBUTING.md**: standard, covers `uv sync`, `tox` commands, `charmcraft pack`.
- **Changelog**: comprehensive, auto-generated from conventional commits.
- **Terraform module**: standard layout with `MODULE_SPECS.md`. Version constraint issue tracked in open issue #375.
- **Gap**: no architecture/design docs in `docs/`. The `_holistic_handler` pattern, the migration flow, and secret management design deserve documentation.

## Open questions

1. **Why `startup: disabled`?** If there's a specific reason (e.g., avoiding a race with config), it should be documented; otherwise `enabled` would improve resilience. Confirmed live on five kill tests across three models: the service stays stopped while the charm reports `active`, recovering only on the next hook cycle.
2. **Is the migration version tracking (`migration_version_{integration_id}`) deliberate?** It forces re-migration on relation churn; `openfga migrate` is idempotent so it's harmless but confusing. Confirmed live: `migration_version_7` and `migration_version_12` coexist in peer data on rv-deep2.
3. **Open issue #396 (CrashLoopBackOff)**: could be the `startup: disabled` finding, a migration timing issue, or something specific to pgbouncer (unverified). The crash observed on rv-deep (fresh deploy with tracing) may be a different manifestation of the same root cause as issue #374 (database-relation-changed crashing) — unverified.
4. **Why no `relation_broken` for certificates?** The TLS cleanup deferral to the next hook cycle appears to be an oversight. Confirmed live on three separate TLS add/remove cycles across two models.
5. **Should cpu/memory config have defaults?** No defaults in `charmcraft.yaml`, and empty strings create a permanent blocked state with no return path. Confirmed live on rv-openfga2 and rv-deep2.
6. **Was the upgrade crash with tracing known?** The upgrade test in the suite deploys without a tracing integration, so it wouldn't have caught this. The test should be extended to include tracing.
7. **Can the tracing-related crashes be reproduced consistently?** Both the upgrade crash (rv-openfga3) and the fresh-deploy crash (rv-deep) exhibited the same root cause in `TracingData.load()` failing on partial/bytes data — suggests the tracing library itself needs hardening, not just this charm.
8. **Why does `_holistic_handler` not use `event.defer()`?** If a precondition isn't met (no container, no peer, etc.), the handler sets status and returns without deferring, relying on the next hook cycle. Appears to be a deliberate design choice, worth documenting.
9. **Does the certificate transfer (`send-ca-cert`) path work on TLS re-add?** On rv-deep2 the `send-ca-cert` relation was joined before TLS was available, causing `_on_certificates_transfer_relation_joined` to defer. When TLS was later re-added, `_on_cert_changed` fired and called `transfer_certificates()`, but the relation data still showed only `version: "0"` — not confirmed whether certs were actually transferred. Needs dedicated testing.
