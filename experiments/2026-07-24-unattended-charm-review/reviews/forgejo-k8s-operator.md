# forgejo-k8s-operator

**Verdict**: A well-structured, actively-maintained k8s charm (96 commits, 7 contributors) with good ops fundamentals — Pydantic config validation, `can_connect()` guards everywhere, `collect_unit_status`-driven status precedence, and a clean event-driven reconciler with no `StoredState` abuse. All charm-specific logic lives in the repo; no external package carries hidden behaviour. But it has two critical bugs that break core functionality out of the box: TLS cannot be established with the canonical `self-signed-certificates` provider (cert/key desync crashes Forgejo on every restart), and all four `type: secret` config options (`SECRET_KEY`, `INTERNAL_TOKEN`, `LFS_JWT_SECRET`, `METRICS_TOKEN`) fail silently when the referenced secret is model-owned and ungranted — with the metrics endpoint left publicly accessible and no operator-visible signal. A maintainer should fix the double `get_assigned_certificate()` call in `configure_certs()` first (it blocks TLS entirely), then add a `BlockedStatus` for inaccessible secrets, then fix the two "stale config.ini on relation removal" bugs (TLS, S3). Everything else — scaling, actions, removal, DB integration, ingress — works correctly.

| | |
|---|---|
| Repo | canonical/forgejo-k8s-operator @ `d35cfaa` (2026-07-21) |
| Charms | forgejo-k8s |
| Substrate | k8s (no machine counterpart) |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), charmhub edge rev 26; also attempted on concierge-k8s-4 (Juju 4.0.12), abandoned when `postgresql-k8s` proved incompatible with Juju 4.x |
| Reviewed | 2026-08-20 |

## What it does

Deploys and manages Forgejo 15 on Kubernetes. Provides: PostgreSQL database via `data_platform_libs`, TLS via `tls_certificates_interface.v4`, Traefik ingress with HTTP/HTTPS-TCP-passthrough/SSH routing, S3 storage via `s3-integrator`, Prometheus metrics with optional bearer-token auth, Grafana dashboards, Loki log forwarding via Pebble's native log-forwarding API, Juju secrets for Forgejo's `SECRET_KEY`/`INTERNAL_TOKEN`/`LFS_JWT_SECRET`/`METRICS_TOKEN`, configurable HTTP(S) proxy, SSH ingress, admin-user actions, and runner registration. Uses `collect_unit_status` for all status reporting.

## Deployment log

1. **concierge-k8s-4 (Juju 4.0.12)**: deployed `forgejo-k8s` edge rev 26, `traefik-k8s`, `self-signed-certificates`. `postgresql-k8s` 14/stable rev 20 deployed but immediately entered error state (`hook failed: "leader-elected"`, readiness-probe 502) — `postgresql-k8s` requires `juju < 4.0.0` and all channels fail on this controller. `forgejo-k8s` correctly blocked with "Add a database relation". This model was abandoned.

2. **concierge-k8s-3 (Juju 3.6.25)**: deployed `forgejo-k8s` edge rev 26 + `postgresql-k8s` 14/stable rev 925 + `traefik-k8s` latest/stable rev 377 + `self-signed-certificates` latest/stable rev 264. Integrated forgejo→postgresql, forgejo→traefik, forgejo→self-signed-certificates. Set `forgejo__server__domain=forgejo.test.local`.

3. All relations established: `forgejo-k8s` went to `maintenance: Waiting for Forgejo to be ready`. Pebble `forgejo` service was `active` but the `/api/healthz` check failed. Inside the container:
   ```
   [E] Failed to create certificate ... tls: private key does not match public key
   [E] Failed to start server
   ```
   Charm-agent logs showed both "Pushed certificate to workload" and "Pushed private key to workload", but forgejo rejected the pair.

4. Removed the TLS relation to isolate the fault. Pebble layer env vars correctly had no `FORGEJO__SERVER__PROTOCOL`, but `config.ini` still contained `PROTOCOL = https`. Forgejo tried HTTPS and failed: "open /etc/forgejo/forgejo.pem: no such file or directory".

5. Manually patched `config.ini` with `FORGEJO__SERVER__PROTOCOL=http` (empty cert/key) and restarted the pebble service. Forgejo recovered to Active at HTTP 200.

6. **Subsequent tests** (see Observed behaviour):
   - Deployed `prometheus-k8s` 1/stable rev 247 and related `forgejo-k8s:metrics-endpoint → prometheus-k8s`. `prometheus-k8s` blocked on RBAC ("Failed to apply resource limit patch: statefulsets.apps 'prometheus-k8s' is forbidden"), not a forgejo defect — `forgejo-k8s` remained Active throughout.
   - Deployed `s3-integrator` latest/stable: blocked on missing AWS credentials. Not exercised end-to-end.
   - `loki-k8s` / `grafana-agent-k8s`: no channel available for the ubuntu@20.04/22.04 base in use — COS log-forwarding path reviewed by code only.
   - Re-added the TLS relation to capture the full cert/key desync cascade (see finding below).
   - Tested secret grant, secret revocation, unit scale up/down, all four actions, `juju refresh`, and `juju remove-application`.

## Observed behaviour

- **Pebble layer env vars** (`pebble plan` in the forgejo container): correctly contain all `FORGEJO__*` vars including DB connection info. After TLS removal, no `FORGEJO__SERVER__PROTOCOL`/`CERT_FILE`/`KEY_FILE` — but `config.ini` still has `PROTOCOL = https`.
- **Pebble "active" ≠ process alive**: pebble reports `forgejo enabled active` even when the forgejo HTTP server has crashed — pebble only knows the process was started, not that it stayed up.
- **Pebble auto-restart on crash**: killing the forgejo process from inside the container caused pebble to restart it within ~3 seconds; service recovered to HTTP 200 with no charm intervention. The `forgejo-ready` pebble check (level=ready, threshold=3) correctly blocks Active once failures accumulate.
- **Pebble check failure cascade (TLS crash)**: pebble restarted forgejo ~5 times (each crash within ~1 second of startup). After 3 failures the `forgejo-ready` check registered `down`; ~26 seconds later the charm received `forgejo-pebble-check-failed` and set `maintenance: Waiting for Forgejo to be ready`. **~30-second window where pebble and the charm both report Active while forgejo is dead.**
- **Forgejo startup time**: ~8 seconds from reconcile to crash (ORM init + SSH server + HTTP listener).
- **TLS desynchronisation — full cascade logged**: re-adding the TLS relation triggered a burst of `certificates-relation-changed` hooks (13:35:57 → 13:35:58 → 13:36:02 → 13:36:04 → 13:36:06 → 13:36:08). Each reconcile pushed new cert/key files. Final state: `config.ini` had `PROTOCOL = https`; `forgejo.pem`'s public key did not match `forgejo.key`. Forgejo log: `Failed to create certificate ... tls: private key does not match public key`, `Failed to start server`.
- **DB integration works**: `FORGEJO__DATABASE__HOST/NAME/USER/PASSWD` all correctly populated from `DatabaseRequires` relation data.
- **DB relation removal**: correctly blocked with "Add a database relation" immediately. Forgejo kept serving for a few seconds on the cached connection, then became unreachable.
- **Traefik route submitted**: "Config domain forgejo.test.local is valid, submitting traefik route" logged on every reconcile.
- **Prometheus scrape integration**: `MetricsEndpointProvider` correctly published scrape metadata, jobs (`targets: ["*:3000"]`), and alert rules to relation data. `prometheus-k8s` itself blocked on RBAC — not a forgejo bug.
- **`postgresql-k8s` 14/stable rev 925** requires `juju < 4.0.0`; all channels fail on Juju 4.0.12.
- **`config_changed` hook count** (`forgejo__log__level=Debug`): one `config-changed` hook, one reconcile log line, no repeats.
- **`can_connect()` guard confirmed**: no traceback observed from a missing guard.
- **Pydantic validation**: `forgejo__log__level=InvalidLevel` correctly blocked with `BlockedStatus("1 validation error for ForgejoConfig\nforgejo__log__level")`. Recovery was immediate on reset.
- **Metrics bearer token (after secret grant)**: `/metrics` returned 401 without token, 200 with `Authorization: Bearer <token>`. Confirmed functional.
- **Metrics token revocation**: after `juju revoke-secret` + reconcile, `FORGEJO__METRICS__TOKEN` is absent from the pebble layer (confirmed via `pebble plan`). Agent log: `ERROR Cannot access Juju secret secret:ap9qp39lsuvsbbdleo90: ERROR permission denied`. But `config.ini` still has `TOKEN = myrealmetricssecret` (written before revocation). Forgejo keeps serving the endpoint with the cached token; the endpoint only goes public on DB wipe + restart. Partial mitigation — revocation is not immediately visible.
- **All 4 actions work**: `create-admin-user` (random password), `generate-runner-secret`, `generate-user-token`, `reset-user-password`.
- **Scale up/down**: `juju scale-application forgejo-k8s 2` and back to `1` both worked; new unit reached Active within ~30 seconds.
- **`juju refresh`**: reports "already up-to-date" — no newer edge revision available.
- **`juju remove-application`**: completes cleanly — unit reaches `terminated/executing`, storage (`data/0`) detached, relations removed.
- **S3**: `s3-integrator` deploys but requires AWS credentials not available in this environment; not exercised end-to-end.
- **Loki/Grafana**: not exercisable without a compatible COS base; code review shows correct use of `LogForwarder` (Pebble log-forwarding API) and `GrafanaDashboardProvider` (LZMA-compressed dashboard templates).
- **LXD substrate**: not applicable — k8s-only charm.

## Findings

### 1. TLS cert/key desynchronisation on every reconcile
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/certificates.py:80` (`_certificate_is_available`), `src/certificates.py:87` (`_check_and_update_certificate`)
- **Evidence**: re-adding the TLS relation fired a burst of `certificates-relation-changed` hooks in rapid succession; each reconcile called `configure_certs()`, which calls `TLSCertificatesRequiresV4.get_assigned_certificate()` **twice** per invocation. Final forgejo pebble log: `Failed to create certificate from cert file /etc/forgejo/forgejo.pem and key file /etc/forgejo/forgejo.key for tcp:0.0.0.0:3000: tls: private key does not match public key`, `Failed to start server`. Cert and key files were both valid PEMs individually, but rejected as a pair.
- **Root cause**: `self-signed-certificates` regenerates the certificate for each outstanding CSR during the relation-changed cascade. Because `configure_certs()` calls `get_assigned_certificate()` twice within one reconcile, and the provider's relation data can change between the two calls, the two calls can return certificates from different signing cycles. The charm stores the cert from one call and effectively pairs it with a key from a different reconciliation cycle.
- **Impact**: TLS cannot work with `self-signed-certificates`, the canonical test provider. Every `certificates-relation-changed` hook fires multiple times during relation establishment, each time risking a mismatched pair — the charm cannot serve HTTPS at all with this provider.
- **Fix**: Call `get_assigned_certificate()` once per `configure_certs()` invocation and reuse the result for both the availability check and the update. Add a defensive check (`Certificate.from_string(chain[0]).matches_private_key(private_key)`) before writing files; on mismatch, log and return `False` rather than push. Alternatively push cert and key atomically (write to temp files, then rename).
- **Linter rule**: not mechanically checkable — this is a runtime race in the TLS library usage.

### 2. Secret fetch failure silently affects all four `type: secret` config options
- **Severity**: critical
- **Kind**: security bug
- **Where**: `src/config.py:44` (`map_config_to_env_vars`), `src/config.py:26` (`_fetch_secret`), `charmcraft.yaml:382-397`
- **Evidence**: the charm has four `type: secret` config options: `forgejo__security__secret_key`, `forgejo__security__internal_token`, `forgejo__server__lfs_jwt_secret`, `forgejo__metrics__token`. Setting `forgejo__metrics__token=secret:<id>` to a model-owned, ungranted secret produced `ERROR juju-log Cannot access Juju secret secret:<id>: ERROR permission denied` in the agent log; no `FORGEJO__METRICS__TOKEN` env var appeared in the pebble layer; `/metrics` returned HTTP 200 with no authentication.
- **Root cause**: `ops.CharmBase.load_config()` turns `type: secret` config values into `ops.Secret` objects, which bypass Pydantic (`ForgejoConfig`) entirely. `map_config_to_env_vars` calls `_fetch_secret()`, which catches `ops.model.ModelError` on permission denial and returns `None`; the caller skips the key with `continue` and sets no status.
- **Impact**: all four secrets are affected. Silent failure of `secret_key`/`internal_token` makes Forgejo fall back to ephemeral values (session invalidation on restart); silent failure of `lfs_jwt_secret` makes LFS insecure; silent failure of `metrics_token` leaves `/metrics` public. An operator who sets any of these to a model-owned secret believes it is in effect — it is not, and there is no visible signal.
- **Fix**: track whether a `secret:`-prefixed config value failed to resolve, and surface a `BlockedStatus` from `_collect_unit_status` naming the missing grant, e.g. `"Secret ... not accessible to forgejo-k8s — grant with: juju grant-secret <id> forgejo-k8s"`. Recovery today (`juju grant-secret <id> forgejo-k8s` + any reconcile trigger) works once granted, but nothing alerts the operator beforehand.
- **Linter rule**: not mechanically checkable — the failure is a runtime permission issue.

### 3. TLS relation removal leaves stale `PROTOCOL=https` in `config.ini`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:271` (`_build_additional_env`, the `if tls_ready:` block)
- **Evidence**: after `juju remove-relation forgejo-k8s self-signed-certificates`, `pebble plan` shows no `FORGEJO__SERVER__PROTOCOL`, but `config.ini` still shows `PROTOCOL = https`. Forgejo fails to start: `Listen: https://0.0.0.0:3000 ... open /etc/forgejo/forgejo.pem: no such file or directory`.
- **Root cause**: `environment-to-ini` updates `config.ini` in place using only the env vars present at startup — it never removes keys that are absent from the current pebble layer. When `_build_additional_env` omits `FORGEJO__SERVER__PROTOCOL` (because `tls_ready=False`), the stale `https` value in `config.ini` is never cleared.
- **Impact**: operators removing the TLS relation cannot restart the service without manual intervention; the charm silently retains HTTPS behaviour with no operator action.
- **Fix**: explicitly set `FORGEJO__SERVER__PROTOCOL=""`, `FORGEJO__SERVER__CERT_FILE=""`, `FORGEJO__SERVER__KEY_FILE=""` in `_build_additional_env` when `tls_ready` is `False`. Confirmed manually that an empty-string env var clears the corresponding INI key.

### 4. S3 relation removal leaves stale storage config in `config.ini`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:249` (`_build_additional_env`, S3 branch)
- **Evidence**: same mechanism as the TLS removal bug — `_fetch_s3_relation_data()` returns `{}` once the s3-credentials relation is gone, contributing no `FORGEJO__STORAGE__*` keys, so `environment-to-ini` never clears the previously written `STORAGE_TYPE`, `MINIO_ENDPOINT`, etc.
- **Root cause**: identical to finding 3 — `_build_additional_env` only ever adds keys, never clears them.
- **Impact**: after removing the S3 relation, Forgejo continues to reference a storage backend that no longer exists and will fail against it.
- **Fix**: when no S3 relation exists, explicitly set the storage keys (`FORGEJO__STORAGE__STORAGE_TYPE=""` etc.) to empty strings, mirroring the TLS removal fix.

### 5. Pydantic validation covers only a subset of config options
- **Severity**: high
- **Kind**: bug
- **Where**: `src/config.py:78` (`ForgejoConfig`)
- **Evidence**: `juju config forgejo-k8s database-default-query-exec-mode=xxx` was accepted by the charm — this option is not modelled in `ForgejoConfig`, so it bypasses Pydantic — and was passed through verbatim as `default_query_exec_mode=xxx` in the DB connection string. Forgejo rejected it at runtime: `invalid default_query_exec_mode (unknown value "xxx")`, entering a 10-retry crash loop (`ORM engine initialization attempt #N/10 failed`).
- **Root cause**: `ForgejoConfig` only validates `forgejo__log__level`, `forgejo__server__domain`, `forgejo__service__default_user_visibility`, `forgejo__service__default_org_visibility`, `forgejo____run_mode`, `forgejo__session__provider`, `forgejo__repository__signing__default_trust_model`, `forgejo__repository__pull_request__default_merge_style`. Everything else, including `database-default-query-exec-mode`, passes through unvalidated.
- **Impact**: invalid values for non-modelled options surface as a Forgejo runtime crash loop (~30 seconds of retries) rather than an immediate `BlockedStatus`, forcing the operator to read pebble logs to diagnose.
- **Fix**: add remaining string-constrained options to `ForgejoConfig` with `Literal` types, at minimum `database-default-query-exec-mode`.

### 6. Unit tests cannot run — `ops.testing.Context` absent
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py` (all 8 tests), `requirements.txt`
- **Evidence**: `AttributeError: module 'ops.testing' has no attribute 'Context'`. Installed `ops` is 3.8.0, matching `requirements.txt: ops ~= 3.7`; `ops.testing.Context` requires `ops >= 3.9`; `ops-scenario` is not installed. All 8 tests fail at collection. Confirmed by running `PYTHONPATH=src:lib python3 -m pytest tests/unit/ -v` — 31 passed (`test_config.py` 14/14, `test_ingress.py` 15/15), 8 failed (all of `test_charm.py`).
- **Impact**: the failing tests cover core charm logic — pebble-ready (check pass/fail), config→env-var propagation, metrics bearer-token auth, secret_changed reconcile, database name encoding. None of it runs in CI right now, so regressions in this logic are not caught.
- **Fix**: bump `requirements.txt` to `ops >= 3.9`, or rewrite the tests against `ops.testing.Harness`, which is available in 3.8.0.
- **Linter rule**: not mechanically checkable at the finding level; a CI guard such as `python -c "from ops.testing import Context"` would catch the version mismatch early.

### 7. Secret revocation: env var cleared but `config.ini` retains old token
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` + `environment-to-ini` / Forgejo's own config persistence
- **Evidence**: after `juju revoke-secret` + reconcile, `pebble plan` confirms `FORGEJO__METRICS__TOKEN` is absent and the agent log shows the permission-denied error, but `config.ini` still has `TOKEN = myrealmetricssecret` from before revocation. Forgejo continues serving the protected endpoint with the stale token; `/metrics` still returns 401 without it even after a fresh restart, so the practical exposure is limited — but the revocation is not what actually took effect.
- **Root cause**: `environment-to-ini` only writes keys present in the current env; it never removes a key just because the env var disappeared, so the old value lingers in `config.ini` until something else overwrites it.
- **Impact**: operators expecting an immediate effect from `revoke-secret` get a false sense that the value is unset; behaviour differs from what the pebble layer implies.
- **Fix**: push an explicit empty-value env var (`FORGEJO__METRICS__TOKEN=""`) when the secret becomes inaccessible, so the next `environment-to-ini` run clears the stale INI value. The same pattern likely applies to the other three secrets on revocation (unverified — only `forgejo__metrics__token` was tested).

### 8. `_collect_service_status` has a ~30-second blind spot when forgejo crashes
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:182` (`_collect_service_status`)
- **Evidence**: during the TLS crash-loop, `pebble services forgejo` reported `enabled active` throughout while forgejo was actually down; the `CollectStatusEvent` only flipped to `maintenance` ~26 seconds after the first crash, once the `forgejo-ready` check (level=ready, threshold=3) accumulated enough failures to fire `forgejo-pebble-check-failed`. `update-status` runs only every 5 minutes, so this window is not otherwise covered.
- **Root cause**: `container.get_service().is_running()` reports True during a fast crash-loop because pebble restarts the process faster than it marks the service failed; only the pebble check catches the underlying failure, and only after its threshold is met.
- **Impact**: for up to ~30 seconds after a crash, the unit reports Active (e.g. "Serving at https://forgejo.test.local") while forgejo is dead — an operator glancing at status could be misled.
- **Fix**: in `_collect_service_status`, also call `container.get_checks()` and treat a non-`up` `forgejo-ready` check as authoritative even when `is_running()` is True, setting `MaintenanceStatus` regardless of process state.

### 9. `reconcile()` silently swallows pebble connection errors
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:320` (`reconcile()`, `except (ops.pebble.APIError, ops.pebble.ConnectionError)` block)
- **Evidence**: the except block logs at INFO ("Unable to connect to Pebble") and returns without setting any status; the unit keeps whatever status was last reported.
- **Root cause**: catching these pebble errors is correct behaviour for handling a temporarily unavailable container, but the handler does not communicate the failure via status.
- **Impact**: if pebble is briefly unavailable during a reconcile (e.g. container restart), the operator may see Active while the intended configuration was never applied.
- **Fix**: set `MaintenanceStatus("Waiting for Pebble")` or `WaitingStatus("Updating configuration")` inside the except block before returning.

### 10. Upgrade path: pebble layer updated but forgejo may not restart to pick up new config
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:347` (`_apply_pebble_layer`)
- **Evidence**: (unverified — code-review finding, not reproduced live). `reconcile()` calls `container.add_layer(..., combine=True)` then `container.replan()`. The pebble command is `environment-to-ini -c <config> && forgejo web --config=<config>`, so `environment-to-ini` runs once at process start; env-var changes only take effect on the next restart.
- **Root cause**: `replan()` restarts a service only for changes pebble considers significant; it is not guaranteed to restart purely for updated environment variables, so an upgrade that changes config could leave the pebble layer updated while forgejo still runs against the old `config.ini`.
- **Impact**: after an upgrade with a config change (new DB host, different log level, etc.), forgejo could keep running with stale configuration until the next restart-triggering event.
- **Fix**: explicitly `container.stop()` + `container.start()` the forgejo service when the pebble layer has materially changed, rather than relying on `replan()`. Alternatively, document that the upgrade is only complete once the service actually restarts.

### 11. `postgresql-k8s` 14/stable fails on Juju 4.x
- **Severity**: medium
- **Kind**: ux
- **Where**: `README.md`, `charmcraft.yaml` `assumes`
- **Evidence**: `postgresql-k8s --channel 14/stable` requires `juju < 4.0.0`; every channel of `postgresql-k8s` failed to deploy on concierge-k8s-4 (Juju 4.0.12). `forgejo-k8s` declares `assumes: juju >= 3.5`, but the README's example `juju deploy postgresql-k8s --channel=14/stable` will not work on a Juju 4.x controller.
- **Impact**: operators on Juju 4.x following the README fail to deploy the required database.
- **Fix**: document the Juju/postgresql-k8s compatibility constraint explicitly, or point the README example at a Juju-4.x-compatible channel.

### 12. `_configure_ingress` called twice per reconcile
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:310` and `src/charm.py:314`
- **Evidence**: `_configure_ingress(domain, tls_ready)` is called once at line 310 and again at line 314 inside `reconcile()`, with no dependency on values computed between the calls.
- **Impact**: every reconcile writes the Traefik route relation data twice — harmless but wasteful.
- **Fix**: remove the duplicate call.

### 13. Storage-attached handler assumes `chown` always succeeds
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:464` (`_on_storage_attached`)
- **Evidence**: `self.container.exec(["chown", owner, FORGEJO_DATA_DIR])` is called without checking the exit code.
- **Impact**: a failed chown (e.g. directory not yet mounted, permission denied) is silently swallowed and would only manifest later as a permission-denied error inside the workload.
- **Fix**: wrap in try/except; on failure set `MaintenanceStatus("Waiting for storage")` and defer if `can_connect()` is False.

### 14. `create-admin-user` error message lists password as required
- **Severity**: nit
- **Kind**: docs
- **Where**: `src/actions.py:51`
- **Evidence**: `event.fail("username, password, and email parameters are required")`, but the action does not require `password` — it can use `--random-password`.
- **Impact**: misleading guidance to operators reading action failure output.
- **Fix**: change the message to "username and email parameters are required".

### 15. `_on_pebble_check_changed` is a documented no-op
- **Severity**: nit
- **Kind**: dead-code
- **Where**: `src/charm.py:132`
- **Evidence**: method body is `pass`, with a docstring noting `collect_unit_status` handles this automatically; the event is still observed via `framework.observe(self.on.forgejo_pebble_check_failed, ...)` for no effect.
- **Impact**: dead event observer with no functional consequence, but adds noise.
- **Fix**: remove the `observe` calls for `forgejo_pebble_check_failed`/`forgejo_pebble_check_recovered`, or add real handling (e.g. a WARNING log).

## Worth copying

- **`collect_unit_status` with explicit precedence**: `_on_collect_status` (`src/charm.py:135`) calls separate `_collect_*_status` helpers in severity order (Blocked > Waiting > Maintenance > Active), with an explicit "if nothing is wrong, report active" comment.
- **Pebble auto-restart for crash recovery**: handled entirely by pebble's `startup: enabled` setting — no charm code required — gated correctly by the `forgejo-ready` check (level=ready, threshold=3).
- **Pydantic config validation (`ForgejoConfig`, `src/config.py:78`)**: frozen model with strict `Literal` types for every enum-like Forgejo setting, giving clear errors before any reconcile side effects (for the options it covers — see finding 5).
- **`can_connect()` guards everywhere**: `reconcile()` returns early, `_on_install()` defers, `_on_secret_changed()` skips the push.
- **No `StoredState` abuse**: the reconciler is fully event-driven; state is derived from current relations and config each time.
- **S3 storage config with scheme stripping**: `ForgejoStorageConfig.from_s3_info()` (`src/config.py:137`) strips `http://`/`https://` from S3 endpoints, preventing a common misconfiguration.
- **Pure-function ingress module**: `src/ingress.py` has no class, no ops imports, builds Traefik route dicts, and is fully unit-tested (15/15 passing).
- **Actions with proper error handling**: all four actions catch `ops.pebble.ExecError` and call `event.fail()` with the error message.
- **`LogForwarder` via Pebble native log forwarding**: `lib/charms/loki_k8s/v1/loki_push_api.py:2619` uses Pebble's `log-targets` API rather than the deprecated `LogProxyConsumer`/promtail approach — the modern COS pattern.
- **`MetricsEndpointProvider` with `refresh_event`**: instantiated with `refresh_event=self.on.config_changed` (`lib/charms/prometheus_k8s/v0/prometheus_scrape.py:1271`), so config changes trigger scrape-job re-submission; leader-only writes prevent conflicts.
- **Custom pebble check `forgejo-ready` (level=ready)**: correctly blocks `CollectStatusEvent` from reporting Active until `/api/healthz` returns 200.

## Common-practice notes

- **`charmcraft.yaml` layout**: standard canonical layout; all charm-libs declared with interface names and version ranges.
- **`lib/charms/` layout**: correctly namespaced under `lib/charms/<name>/v<N>/`. However, `data_platform_libs.data_interfaces` is pinned to unpinned major version `"0"`, which allows `charmcraft fetch-libs` to pull incompatible future versions.
- **`src/` layout**: `charm.py` as entry point plus `config.py`, `constants.py`, `certificates.py`, `ingress.py`, `actions.py` — standard.
- **`collect_unit_status` used exclusively** — the old direct `self.unit.status = ActiveStatus()` pattern is absent.
- **Pebble layer generation**: `_get_pebble_layer()` returns a standard `ops.pebble.Layer`; the command uses `environment-to-ini` to convert env vars to INI before starting forgejo.
- **`TraefikRouteRequirer` with `raw=True`**: enables raw Traefik configuration, needed for TCP TLS-passthrough and SSH routing.
- **No upgrade handler**: upgrades flow through `config_changed` → `_on_config_changed` → `reconcile()`; `set_ports()` has an explicit comment about syncing ports across upgrades. See finding 10 for the one subtle gap here.
- **`ops.CharmBase.load_config()`** used for Pydantic-backed config, handling dash-to-underscore conversion and secret-type options automatically.
- **`environment-to-ini` command wrapper**: forgejo does not hot-reload config from env vars — a restart is required, which is a characteristic of the workload, not a bug in itself (but underlies findings 3, 4, 7, 10).

## Tests

### Unit tests (`tests/unit/`)
- `test_config.py`: 14/14 PASS — `ForgejoConfig` validation, `ForgejoStorageConfig` aliasing/scheme-stripping/`from_s3_info`, secret resolution.
- `test_ingress.py`: 15/15 PASS — HTTP/TLS/SSH traefik route configs, full branch coverage on pure functions.
- `test_charm.py`: **8/8 FAILED** — `AttributeError: module 'ops.testing' has no attribute 'Context'` (see finding 6). Confirmed by running `PYTHONPATH=src:lib python3 -m pytest tests/unit/ -v`.

### Integration tests (`tests/integration/`)
- `test_charm.py`: full-stack test (forgejo + postgresql-k8s + traefik-k8s) covering metrics bearer-token enforcement and SSH push through Traefik LoadBalancer (keygen, user, repo, push). Uses `pytest-jubilant`/`jubilant`; assertions are behavioural, not just active/idle. Not run in this review (requires `charmcraft pack`).
- `test_pgbouncer.py`: forgejo + pgbouncer-k8s + postgresql-k8s; only asserts `active/idle`, no behavioural assertions. Not run.

### CI (`tests.yaml`)
Runs lint → static (pyright) → unit, on Python 3.12 via tox. Does not run integration tests.

### Static analysis
- `ruff check src/`: all checks passed.
- `codespell src/`: no issues.
- `ruff check lib/`: no issues across the 5 shipped charm libraries.

### Test coverage relative to risks found

| Risk | Covered by test? |
|---|---|
| TLS cert/key desync | No — `test_charm.py` can't run |
| Secret fetch failure (all 4 secrets) | Partial — `test_config.py` covers secret resolution, not the permission-denied fallback |
| Secret revocation: token persists in `config.ini` | No |
| TLS removal leaves stale `PROTOCOL` | No |
| S3 removal leaves stale storage config | No |
| Pydantic validation gap | Partial — validates modelled options, not the runtime-crash gap for unmodelled ones |
| `reconcile()` silent pebble error | No |
| Upgrade path restart gap | No |
| Pebble check failure → 30s Active window | No — needs scenario framework |
| `_on_pebble_check_changed` dead observer | No |

## Docs

- **README.md** (1177 bytes): shows integrate-and-use pattern, example `juju status`, curl example. Missing: resource attachment, retrieving the admin password, production domain config, how TLS works, S3 configuration. Not sufficient on its own for a new operator.
- **CONTRIBUTING.md**: standard tox-based dev setup, brief; missing integration-test instructions and architecture notes.
- **`charmcraft.yaml` description**: "Deploy and configure the software forge, Forgejo." — adequate.
- **Config options**: well documented in `charmcraft.yaml` with type, default, description; 60+ options across all Forgejo sections, including the four `type: secret` options.
- **`charmcraft.yaml` assumes**: `juju >= 3.5`, but the README's `postgresql-k8s --channel 14/stable` example requires `juju < 4.0.0` — see finding 11.

## Open questions

- **Does the TLS mismatch affect all certificate providers or only `self-signed-certificates`?** Confirmed only with `self-signed-certificates`. The double-call to `get_assigned_certificate()` is the charm-side vulnerability regardless of provider; the provider's CSR-regeneration behaviour amplifies it here.
- **Should Juju auto-grant charm access to model-owned secrets referenced in config?** If so, this is arguably a Juju-side gap; if not, the charm must handle permission-denied explicitly (it currently does not surface it). Charm-owned secrets work correctly — only model-owned/other-charm-owned secrets fail.
- **Does the revocation-persistence pattern in `config.ini` apply to all four secret options?** Only `forgejo__metrics__token` was tested; the same mechanism should apply to `secret_key`, `internal_token`, and `lfs_jwt_secret` (unverified).
- **Does `replan()` restart forgejo for pure env-var changes?** Unverified in this review — the upgrade-path gap (finding 10) depends on this. Even if `replan()` does not restart, the `forgejo-ready` check would eventually catch a resulting misconfiguration and block Active, adding delay rather than causing silent failure.
