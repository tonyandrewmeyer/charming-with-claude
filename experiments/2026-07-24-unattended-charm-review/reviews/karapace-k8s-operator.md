# karapace-k8s

Karapace is a schema registry for Apache Kafka. This charm deploys it as a scalable Kubernetes workload, connecting to `kafka-k8s` via `kafka_client`, optionally to `tls-certificates` for encryption, and exposing a `karapace_client` provider interface. The code itself is solid: well-structured, typed, lints clean, and karapace consistently handled every cascading failure correctly during testing (clear blocked/waiting statuses, no crashes). It has a handful of real, fixable defects — most notably a plaintext-secrets bypass in the password action, a broken TLS-cert cleanup, and an install-hook crash under missing RBAC — plus a slow relation-recovery path. A maintainer should fix the secrets bypass (#2) and the RBAC install crash (#5) first, then the TLS cleanup glob bug (#3) and the relation-recovery latency (#1). The charm could not be fully exercised end-to-end because `kafka-k8s`, not karapace, failed to reach a healthy state in every fresh deployment attempted for this review.

| | |
|---|---|
| Repo | canonical/karapace-k8s-operator @ `8c2a225` (2026-03-13) |
| Charms | karapace-k8s |
| Substrate | k8s |
| Deployed | partially — karapace-k8s itself deployed successfully in every attempt (charmhub rev 14, latest/edge), but no attempt produced a healthy kafka-k8s, so karapace never reached `active`. Scale, TLS, and action tests were exercised against a pre-existing working stack (model `rv-karapace-k8s`) left by a prior reviewer; this review did not itself stand up a working kafka stack. |
| Reviewed | 2026-08-05 |

## What it does

Deploys Karapace as a Kubernetes workload in a `karapace` OCI container. Connects to `kafka-k8s` via the `kafka_client` interface, supports optional TLS via `tls-certificates` (tested with `self-signed-certificates`), manages internal auth via a JSON authfile on disk, and provides `karapace_client` for downstream schema-registry access with user/ACL provisioning.

## Deployment log

### Deployment 1: concierge-k8s-4 (juju 4.0.5), model `rv-karapace-deep`

Fresh deploy: kafka-k8s (rev 27, latest/edge), zookeeper-k8s (rev 21), karapace-k8s (rev 14), self-signed-certificates (rev 633).

**Kafka blocked by AccessDeniedException:** kafka-k8s's data directory (`/var/lib/kafka/data/`) was root-owned with a `lost+found` dir, so the `kafka` user couldn't write its recovery checkpoint — pebble service went to `backoff` while the kafka-k8s charm status stayed misleadingly `active`. After a manual `chown -R kafka:kafka /var/lib/kafka/data/ && rm -rf lost+found`, kafka started, but kafka-k8s had already processed `kafka-client-relation-changed` while in backoff and never retried, so relation credentials were never written.

**Kafka relation-broken crash:** removing the kafka relation to force re-integration crashed kafka-k8s: `hook failed: "kafka-client-relation-broken"`, traceback through `provider.py:135` / `auth.py:188` / `utils.py:124` — `Invalid config(s): SCRAM-SHA-512`. Same crash reported by a prior reviewer. Force-removing and redeploying kafka-k8s then failed on a StatefulSet PVC name mismatch (`kafka-k8s-data-c6bb42` vs `kafka-k8s-data-25ec83`) — a Juju 4 PVC cleanup race after `--force` removal. All of this is a kafka-k8s defect, not karapace's.

**Karapace handled everything correctly:**
- Kafka in backoff, relation present: `waiting: kafka credentials not created yet`
- Kafka relation removed: `blocked: missing required kafka relation` (<5s)
- TLS: CSR sent, cert received, files written to `/etc/karapace/` (`cacert.pem`, `cert.pem`, `private.key`, all `root:root` mode 0644)
- Authfile written with operator user, hardcoded `salt: "placeholder"`
- Container image's default `karapace.config.json` (owned `_daemon_:_daemon_`) was correctly never overwritten, since kafka was never ready

**Actions tested (all functioned):**
- `get-password username=operator` — returns password from peer relation
- `set-password` — rewrites authfile, but bypasses Juju secrets (finding #2)
- `set-tls-private-key` — generated new key, correctly detected key/CSR mismatch and re-issued CSR

**TLS relation removal — `remove_stores()` bug confirmed:** after removing the certificates relation, `_tls_relation_broken` cleared peer data correctly, but all three TLS files persisted on disk. `TLSManager.remove_stores()` runs `rm -rf *.pem *.key` via pebble exec, which doesn't invoke a shell, so the glob never expands — confirms the FIXME at `src/managers/tls.py:65`.

### Deployment 2: concierge-k8s-4 (juju 4.0.5), model `rv-karapace-round2` — kafka/zookeeper at 3/stable

Used zookeeper-k8s (rev 78, 3/stable) and kafka-k8s (rev 82, 3/stable) to match integration-test channels.

**Rawfile provisioner exhaustion:** zookeeper's PVC failed with `rpc error: code = ResourceExhausted desc = Not enough disk space`. 31 orphaned PVC data directories under `/data/` from previous models had exhausted loop devices. After cleanup, provisioning succeeded and pods reached Running.

**Zookeeper/kafka credential handshake stalled:** zookeeper reached `active` (3.9.2) but kafka-k8s stayed at `waiting: zookeeper credentials not created yet` indefinitely. Zookeeper's relation data showed `requested-secrets` but never granted them — a zookeeper-k8s/kafka-k8s integration issue at 3/stable, not a karapace defect.

**Install hook crash — `_get_statefulset` 403:** karapace's `_on_install` crashed because `K8sManager._get_statefulset()` (`src/managers/k8s.py:79`) calls `self.client.get(StatefulSet, ...)`, which returns 403 when the service account lacks RBAC. The 403 guard (lines 69-74) only wraps the `patch` call, not the `get`. `juju trust karapace-k8s --scope=cluster` resolved it (finding #5).

After trust was granted, karapace reached `blocked: missing required kafka relation` correctly (kafka was still stuck waiting on zookeeper).

### Deployment 3: concierge-k8s-3 (juju 3.6.25), model `rv-karapace-36`

Same stack as deployment 1. All four apps deployed and obtained unit IPs (storage worked here, unlike the prior reviewer's k8s-3 attempt).

**Same AccessDeniedException pattern** on the kafka data directory; same manual fix; same missed credential write.

**Same relation-broken crash** on `juju remove-relation`, with the relation left in a dying-but-not-removed state.

**Cross-deployment conclusion:** kafka-k8s rev 27 consistently fails to write `username`/`password`/`endpoints` to the kafka-client relation when its workload isn't running at hook time, while showing `active` status regardless. Its `relation-broken` crash on SCRAM user deletion locks the relation permanently. None of this is a karapace defect — karapace handled every observed state correctly.

### Deployment 4 (round 1, pre-existing): concierge-k8s-4, model `rv-karapace-k8s`

Working kafka+zookeeper+karapace stack left by a prior reviewer, used for lifecycle observations not otherwise obtainable. Scale 1→3→1 worked cleanly. Kafka relation break/re-add: karapace went `blocked` immediately on break; re-integration recovery took ~5 minutes, bottlenecked on the `update-status` interval. A second relation removal reproduced the same kafka-k8s crash seen in deployments 1 and 3.

## Observed behaviour

### Timings
- Scale 1→3 (working kafka stack): ~60s to all active
- Kafka relation removal → `blocked`: <5s
- Kafka relation re-add → recovery: 5+ minutes, bottlenecked on `update-status` (`topic_created` never re-fires) — finding #1
- TLS cert provisioning: ~5s after `self-signed-certificates` becomes active
- TLS relation removal → files persisted: `remove_stores()` bug — finding #3

### Files on disk (confirmed via `kubectl exec` across three deployments)
- `authfile.json`: `root:root`, mode 0644, SHA-512 hash with `salt: "placeholder"`; always written by charm
- `karapace.config.json`: image ships a default (`_daemon_:_daemon_`) with `bootstrap_uri: localhost:9092`; only overwritten once kafka is ready with credentials — never happened here, correctly left as-is
- TLS files (`cacert.pem`, `cert.pem`, `private.key`): `root:root`, mode 0644; persisted after TLS relation removal (finding #3)

### Pebble layer (confirmed via `kubectl exec`)
- Service `karapace`, command `python3 -m karapace`, user/group `_daemon_`, `startup: enabled`, env injected from `/etc/environment`
- No health check configured (finding #12) — pebble restarts on exit but can't detect a hung process

### Service links
Kubernetes service links disabled via a `lightkube` StatefulSet patch on install (`enableServiceLinks: false`). Confirmed working — `karapace` env vars aren't clobbered by K8s service links.

### Hook count
`config-changed` fires on every trigger but only re-renders/restarts when the rendered config differs from the computed config (`src/charm.py:112`). With kafka absent it defers and does nothing further.

### Error-path behaviour
- Install hook without RBAC: `error: hook failed: "install"` (403 on StatefulSet GET), resolved by `juju trust` (finding #5); retried 3 times then errored, no self-recovery
- Kafka missing: `blocked: missing required kafka relation` — clear
- Kafka connected, no credentials: `waiting: kafka credentials not created yet` — clear
- TLS mismatch: `blocked: tls must be enabled on both karapace and kafka` — clear, unit-tested
- No peer relation: `maintenance: no peer relation yet`
- Container not ready: `maintenance: karapace container not ready`
- Service not running: `blocked: karapace service not running`

### Differences between Juju 4.0.5 and Juju 3.6.25
- Juju 4: the `enableServiceLinks: false` server-side-apply patch worked correctly, but only when `juju trust` was granted; without it the install hook crashed with 403 (finding #5)
- Juju 3.6: karapace deployed and reached `blocked` cleanly, and the install hook did **not** crash — suggesting the 3.6 controller grants different default RBAC to charm service accounts (unverified)
- Storage: both clusters use `rawfile.csi.openebs.io`. The 4.0.5 cluster had 31 orphaned PVC data directories causing `ResourceExhausted` (finding #13); the 3.6 cluster's provisioner worked on the first attempt
- kafka-k8s rev 27 (latest/edge) showed the same AccessDeniedException/relation-broken pattern on both Juju versions; rev 82 (3/stable) on Juju 4 instead stalled on the zookeeper credential handshake (finding #14)

## Findings

### 1. `_set_password_action` bypasses Juju secrets for `operator-password`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/events/password_actions.py:71`
- **Evidence**: `self.charm.context.cluster.relation_data.update({f"{username}-password": new_password})` writes directly to the raw `MutableMapping`, bypassing `KarapaceCluster.update()` (`src/core/models.py:145-158`), which routes `SECRETS_APP` fields — including `operator-password` (`src/literals.py:29`) — through `set_secret()`. Observed live: `juju run karapace-k8s/0 get-password` returned the password in cleartext in the action output, and `set-password` writes plaintext relation data.
- **Impact**: `operator-password` is declared as a Juju-secrets-protected field but is written and returned as plaintext, undermining that protection and leaking the password in `juju show-operation` output.
- **Fix**: Route through `self.charm.context.cluster.update({f"{username}-password": new_password})`; consider not echoing the password back in the action result.
- **Linter rule**: Flag `relation_data.update()` calls on `DataPeerData`-backed objects touching keys present in the charm's `SECRETS_APP` list.

### 2. Install hook crashes on `_get_statefulset` when service account lacks RBAC
- **Severity**: high
- **Kind**: bug
- **Where**: `src/managers/k8s.py:79`, called from `_on_install` via `disable_service_links()` (`src/charm.py:72`)
- **Evidence**: Observed live on concierge-k8s-4, model `rv-karapace-round2`. Install hook failed with `ApiError: statefulsets.apps "karapace-k8s" is forbidden ... cannot get resource "statefulsets"`. The 403 guard (`k8s.py:69-74`) only wraps the `patch` call, not the `get`. `juju trust karapace-k8s --scope=cluster` resolved it.
- **Impact**: unconditional first-boot failure on clusters where Juju doesn't grant `statefulsets.get` to the charm's service account — the operator sees only `error: hook failed: "install"` with no hint that `juju trust` fixes it.
- **Fix**: Have `_get_statefulset` return `None` on 403 and handle that in `disable_service_links` with a warning, or wrap `_on_install` in try/except directing the operator to `juju trust`.
- **Linter rule**: Flag `client.get`/`client.patch` calls on `lightkube.Client` not wrapped in `try/except ApiError`, or with an incomplete 403 handler.

### 3. `remove_stores()` silently fails — glob expansion not available in pebble exec
- **Severity**: high
- **Kind**: bug
- **Where**: `src/managers/tls.py:65-76`
- **Evidence**: `self.workload.exec(command="rm -rf *.pem *.key", ...)` — pebble `exec` doesn't invoke a shell, so `*` never expands. Acknowledged in code: `# FIXME: This method does not work since * is a bash thing.` Confirmed live on two deployments: after removing the certificates relation, all three TLS files persisted on disk at `/etc/karapace/`. Invoked from `_tls_relation_broken` (`src/events/tls.py:106`) on every TLS relation removal.
- **Impact**: stale certs/keys remain after TLS is disabled; if TLS is re-enabled with a different CA this could cause trust-chain confusion. Lower impact on K8s (ephemeral container fs) but the bug has been known and unfixed since it was written.
- **Fix**: `self.workload.exec(command="sh -c 'rm -f /etc/karapace/*.pem /etc/karapace/*.key'")`, or use `Container.remove_path()` on the individual files.
- **Linter rule**: Flag `workload.exec`/`container.exec` commands containing glob characters (`*`, `?`, `[`) whose first argument isn't a shell invocation.

### 4. No recovery from kafka relation break without an `update-status` cycle
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/events/kafka.py:18-54`
- **Evidence**: `KafkaHandler` only observes `bootstrap_server_changed`, `topic_created`, and `relation_broken`. There's no `relation_joined`/`relation_changed` observer. `topic_created` fires only when `_main_credentials_shared(diff)` detects new credentials (`lib/charms/data_platform_libs/v0/data_interfaces.py:4037-4050`); if kafka doesn't rewrite credentials on re-add, it never fires. Observed on the working stack: karapace stayed blocked through multiple `update-status` cycles after a relation remove/re-add.
- **Impact**: 5+ minutes of unnecessary downtime after a routine relation remove-and-re-add, even when kafka is healthy and immediately available.
- **Fix**: Observe `self.charm.on[KAFKA_REL].relation_joined` and emit `config_changed` to force reconciliation; consider a timeout that sets `Blocked` with a diagnostic message if credentials don't arrive within N cycles.
- **Linter rule**: Flag charms that rely solely on custom library events for relation-data population without a raw `relation_joined`/`relation_changed` fallback on the same endpoint.

### 5. `brokers_active()` leaks Kafka connections without calling `close()`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/managers/kafka.py:27-52`
- **Evidence**: creates a `KafkaClient` (which lazily initializes admin/producer/consumer clients) but never calls `.close()`. The object is local and garbage-collected, but `kafka-python` clients don't implement `__del__` cleanup. Every `update-status` (default every 5 min) opens new TCP connections.
- **Impact**: leaked file descriptors/TCP connections over a long-running deployment, potentially exhausting connection limits on brokers or the pod.
- **Fix**: wrap the `describe_topics()` call in `try/finally: client.close()`, or make `KafkaClient` a context manager.
- **Linter rule**: Flag client constructors like `KafkaClient(` not followed by `.close()` in the same scope.

### 6. Kafka-k8s `relation-broken` crash causes unrecoverable relation state (ecosystem)
- **Severity**: medium (high impact, but the bug is in kafka-k8s, not karapace)
- **Kind**: bug (upstream)
- **Where**: observed across 3 deployments with kafka-k8s rev 27 (latest/edge)
- **Evidence**: removing the `kafka_client` relation crashes kafka-k8s with `hook failed: "kafka-client-relation-broken"` → `Invalid config(s): SCRAM-SHA-512`. The error loop blocks relation cleanup, leaving it dying-but-not-removed. Observed on all three fresh deployments.
- **Impact**: an operator who removes the wrong relation faces an unrecoverable state requiring `juju remove-application --force` on kafka-k8s, losing kafka data. Directly affects karapace operators even though the defect is not in karapace.
- **Fix**: document as a known limitation in karapace's README; file/track against kafka-k8s.
- **Linter rule**: not mechanically checkable.

### 7. TLS toggling does not restart the workload
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/events/tls.py:87-90`, `:100-110`, `:114-128`
- **Evidence**: `_tls_relation_created`, `_tls_relation_broken`, and `_on_certificate_available` all mutate cert state/files but none emit `config_changed` or otherwise trigger a restart. Confirmed in deployment 1: TLS files were written but the karapace workload was never restarted to pick them up (though masked there by kafka being unready). Tracked upstream as issue #31.
- **Impact**: after adding or removing TLS, karapace keeps serving with the old security configuration until the next `update-status` (up to 5 min) or an unrelated event triggers reconciliation.
- **Fix**: emit `self.charm.on.config_changed.emit()` at the end of each of the three handlers.
- **Linter rule**: flag TLS relation/certificate-available handlers that change config-relevant state without emitting a reconciliation event.

### 8. Zookeeper/kafka credential handshake stalls at 3/stable (ecosystem)
- **Severity**: medium
- **Kind**: bug (upstream, kafka-k8s/zookeeper-k8s)
- **Where**: concierge-k8s-4, model `rv-karapace-round2`, zookeeper-k8s rev 78 / kafka-k8s rev 82 (3/stable)
- **Evidence**: zookeeper reached `active` (3.9.2) but kafka stayed `waiting: zookeeper credentials not created yet` indefinitely; zookeeper's relation data requested secrets but never granted them. Same failure shape seen with latest/edge, suggesting it isn't channel-specific.
- **Impact**: karapace integration testing depends on a working kafka stack; neither available cluster produced one without manual intervention, blocking end-to-end validation.
- **Fix**: file against kafka-k8s/zookeeper-k8s; document as a known dependency risk in karapace.
- **Linter rule**: not mechanically checkable.

### 9. Orphaned rawfile PVC data accumulates indefinitely, exhausting the provisioner (infrastructure)
- **Severity**: medium
- **Kind**: bug (upstream CSI/environment, affects karapace testing)
- **Where**: concierge-k8s-4 cluster's rawfile CSI provisioner
- **Evidence**: 31 orphaned PVC data directories from destroyed models remained on the host, exhausting loop devices (`max_loop=8`); new PVCs failed with `ResourceExhausted: Not enough disk space` despite 124GB free. Cleanup resolved it.
- **Impact**: charm testing/review on this cluster can be blocked by storage failures unrelated to the charm under test.
- **Fix**: document the cleanup procedure for the test environment; ideally fix orphan cleanup in the rawfile CSI driver.
- **Linter rule**: not mechanically checkable.

### 10. Kafka-k8s workload/charm status mismatch (ecosystem)
- **Severity**: medium (for kafka-k8s; affects karapace's observability)
- **Kind**: bug (upstream)
- **Where**: observed across 3 deployments, kafka-k8s rev 27
- **Evidence**: kafka-k8s shows `active` while its pebble service is `backoff` (stuck on the AccessDeniedException). karapace waits indefinitely for credentials that never arrive.
- **Impact**: `juju status` shows kafka `active` / karapace `waiting` with no indication anything is broken; debugging requires `kubectl exec`.
- **Fix**: in karapace, add an `update-status` timeout — if a kafka relation exists but `kafka_ready` has been false for N cycles, set `Blocked` with a diagnostic message.
- **Linter rule**: not mechanically checkable.

### 11. Dead no-op: `fetch_my_relation_data` referenced without parentheses
- **Severity**: low
- **Kind**: bug
- **Where**: `src/core/models.py:205`
- **Evidence**: `self.data_interface.fetch_my_relation_data` — bare method reference, never called; likely meant to refresh relation data before reading `tls`.
- **Impact**: `KarapaceCluster.tls_enabled` may read stale local-cache TLS state if data was updated via secrets, until some other event refreshes the cache.
- **Fix**: add the missing `()`.
- **Linter rule**: pyright `reportUnusedExpression` would catch a bare method reference as a no-op statement; the project's `typeCheckingMode: basic` does not.

### 12. `planned_units()` called as a method on an int property — latent TypeError
- **Severity**: low
- **Kind**: bug
- **Where**: `src/events/provider.py:91`
- **Evidence**: `not self.charm.app.planned_units() == 0` — `planned_units` is an int property, not callable. In practice this branch is unreachable because the preceding `or` clause is always true for a provider relation, so the call never executes.
- **Impact**: latent crash if this path were ever reached (e.g. a self-referential relation in tests); the `or` (likely meant to be `and`) also makes the check dead code today.
- **Fix**: `self.charm.app.planned_units == 0`; consider changing `or` to `and`.
- **Linter rule**: pyright `reportCallIssue` would catch this under stricter mode; targeted rule could flag `.planned_units(`.

### 13. Hardcoded salt for password hashing
- **Severity**: low
- **Kind**: bug
- **Where**: `src/literals.py:27`
- **Evidence**: `SALT = "placeholder"`, used in `KarapaceWorkload.mkpasswd()` (`src/workload.py:89`) for all users.
- **Impact**: static salt weakens the internal authfile's hashing, though this is internal charm-to-workload auth, not externally exposed.
- **Fix**: generate a random salt per user/deployment.
- **Linter rule**: flag hardcoded constants named/containing `SALT`.

### 14. No user-facing config options
- **Severity**: low
- **Kind**: ux
- **Where**: `src/core/structured_config.py:14-16`, no `config.yaml`
- **Evidence**: `CharmConfig` is an empty class (`pass`); all Karapace settings are hardcoded in `ConfigManager.config` (`src/managers/config.py:35-80`).
- **Impact**: operators cannot tune Karapace without modifying charm code.
- **Fix**: expose common tunables via `config.yaml`.
- **Linter rule**: not mechanically checkable without a config spec.

### 15. No `upgrade-charm` event handler
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/charm.py`
- **Evidence**: `grep upgrade_charm src/charm.py` returns nothing.
- **Impact**: no hook to handle peer-data/secrets migrations or reconciliation on refresh; other Data Platform charms typically wire one to at least `config_changed`.
- **Fix**: add a minimal `_on_upgrade_charm` that emits `config_changed`.
- **Linter rule**: flag charms without an `upgrade-charm` handler.

### 16. `_on_karapace_pebble_ready` does not emit `config_changed`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:77-93`
- **Evidence**: sets up credentials/authfile but relies on the automatic `config-changed` that follows `start`, rather than emitting explicitly.
- **Impact**: fragile if the automatic post-start `config-changed` is ever suppressed or if `pebble-ready` refires mid-lifecycle.
- **Fix**: emit `config_changed` explicitly at the end of the handler.
- **Linter rule**: flag `pebble-ready` handlers writing config-relevant data without emitting `config_changed`.

### 17. Sensitive credentials in world-readable files
- **Severity**: low
- **Kind**: ux
- **Where**: `src/managers/config.py:100-107` (`set_environment`), container filesystem
- **Evidence**: kafka SASL credentials written to `/etc/environment` and `karapace.config.json`, both mode 0644; confirmed via `kubectl exec`.
- **Impact**: any process in the container can read Kafka credentials.
- **Fix**: `chmod 0600` on sensitive files after writing.
- **Linter rule**: flag writes of secret-bearing keys to paths with no subsequent `chmod`.

### 18. No Pebble health check
- **Severity**: nit
- **Kind**: ux
- **Where**: `src/workload.py:107-125`
- **Evidence**: the pebble layer defines no `checks` section for the karapace service.
- **Impact**: a hung-but-running karapace process wouldn't be auto-restarted; only caught on the next `update-status`.
- **Fix**: add an HTTP check against `http://localhost:8081/` or a TCP check on port 8081.
- **Linter rule**: flag pebble layers lacking a `checks` section for core services.

### 19. No COS observability integration
- **Severity**: low
- **Kind**: test-gap
- **Where**: `metadata.yaml:41-49` (commented out), tracked upstream as issue #35
- **Evidence**: `metrics-endpoint`/`grafana-dashboard` relations are commented out.
- **Impact**: no metrics scraping or dashboards.
- **Fix**: implement per issue #35.
- **Linter rule**: not mechanically checkable.

### 20. No `certificate_expiring`/`certificate_invalidated`/`certificate_revoked` handlers
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/events/tls.py`
- **Evidence**: `TLSHandler` only observes `relation_created`, `relation_joined`, `relation_broken`, `certificate_available`, and `refresh_tls_certificates`.
- **Impact**: certificates nearing expiry aren't proactively renewed; recovery depends on the operator noticing and running `set-tls-private-key`.
- **Fix**: observe `certificate_expiring` and trigger `refresh_tls_certificates`.
- **Linter rule**: for charms using `TLSCertificatesRequiresV4`, flag missing `certificate_expiring` observer when other TLS events are observed.

## Worth copying

1. Typed charm base with structured config (`TypedCharmBase[CharmConfig]`) — clean separation even with an empty `CharmConfig`.
2. Handler/manager separation: thin `src/events/` handlers delegate to `src/managers/` — easy to unit-test.
3. `Status` enum with associated `StatusBase` and log level (`src/literals.py:39-57`), enforced via `_set_status` (`src/charm.py:153-159`) — single, grep-friendly source of truth for statuses.
4. Deferred-event handling with consistent precondition guards (peer relation, leadership, workload health) before proceeding.
5. Unit tests use `ops.testing.Context`/`State` (ops-scenario), not the older `Harness` API — fast (0.45s) with targeted mocks.
6. `enableServiceLinks: false` StatefulSet patch cleanly avoids env-var collisions from services named `karapace`.
7. `KarapaceAuth` loads the authfile into memory, mutates in place, writes only on explicit `write_authfile()` — avoids redundant I/O.
8. `WorkloadBase` ABC (`src/core/workload.py`) — clean interface (`start`/`stop`/`restart`/`read`/`write`/`exec`/`active`/`get_version`/`mkpasswd`), positions the code for a future machine-charm variant.
9. Recovered cleanly from an interrupted install: after the RBAC 403, `juju trust` + `juju resolve` let the retried hook complete without further intervention.
10. Integration tests exercise real behaviour — curl-based schema create/list, password rotation, TLS handshake checks — not just `active/idle` waits.

## Common-practice notes

- **Follows**: standard Canonical Data Platform layout (`src/charm.py`, `src/core/`, `src/events/`, `src/managers/`, `src/literals.py`, `src/workload.py`); `poetry` + `charmcraft.yaml` poetry plugin; `tox` for lint/unit/integration; `concierge.yaml` for CI environment.
- **Follows**: client relation passwords (`relation-{id}`) are correctly routed through Juju secrets via the `key.startswith("relation-")` check in `KarapaceCluster.update()`.
- **Drifts**: empty `CharmConfig` is unusual for Data Platform charms, which typically expose at least a few tunables.
- **Drifts**: hardcoded `SALT = "placeholder"` is poor practice compared to other Data Platform charms that generate random salts.
- **Drifts**: the acknowledged-but-unfixed FIXME in `remove_stores()` is rare — most Data Platform charms fix or remove known-broken code paths rather than leave a comment.
- **Drifts**: no `upgrade-charm` handler, unlike most Data Platform K8s charms.
- **Drifts**: `_on_karapace_pebble_ready` doesn't emit `config_changed` explicitly, unlike the common pattern.
- **Drifts**: `disable_service_links`'s `_get_statefulset()` call has no 403 guard, unlike the sibling `patch` call — crashes install on clusters that don't grant `statefulsets.get` RBAC.
- **Drifts**: `KafkaClient` in `kafka.py` is never `.close()`'d; other Data Platform charms using `kafka-python` typically close connections or use context managers.

## Tests

**Unit tests**: 20 tests, all passing in 0.41s (confirmed via `tox -e unit`). 70% coverage (961 statements). Good coverage of pebble-ready flows, config-changed under various readiness states, update-status, install, provider relation, and TLS blocked/SANs paths.

Coverage gaps mapped to findings:
- `events/password_actions.py`: 26% — finding #1 (secrets bypass) lives in untested code
- `events/tls.py`: 51% — finding #7 (no restart on TLS toggle) untested
- `events/kafka.py`: 63% — finding #4 (relation-break recovery) insufficiently tested
- `managers/tls.py`: 34% — finding #3 (`remove_stores`) untested
- `managers/kafka.py`: 41% — `brokers_active` (finding #5) entirely untested
- `managers/k8s.py`: 51% — `disable_service_links` is patched out in most tests via an autouse fixture

**Integration tests**: 4 files, 459 lines, well-structured, assert real behaviour (curl schema create/list, TLS handshake, password rotation). Use `ops_test.fast_forward()`. `test_scale_up_kafka` is `@pytest.mark.skip`-ped. Could not be run on either cluster available for this review, since neither produced a healthy kafka stack without manual intervention. The `app-charm` fixture correctly models a downstream `karapace_client` consumer via `karapace-client-admin`/`karapace-client-user` relations.

**Lint**: all pass — codespell clean, ruff clean, black clean (28 files unchanged), pyright 0 errors/0 warnings under `typeCheckingMode: basic` (which does not catch findings #11 or #12). `tls_certificates_interface`/`data_interfaces` library deprecation warnings for `JujuVersion.from_environ()` are library-level, not charm defects.

## Docs

- **README.md**: good deploy/TLS/password-rotation/relation coverage. References `tls-certificates-operator` for TLS while integration tests (and this review) used `self-signed-certificates`; both work but the README should mention both. Recommends `-n 3` for zookeeper though integration tests use a single unit.
- **CONTRIBUTING.md**: standard Canonical template.
- **Terraform module**: `terraform/main.tf`/`variables.tf`/`outputs.tf`/`versions.tf` using `juju_application` + `juju_offer` — clean.
- **No `docs/` directory** beyond README and code comments.
- **Missing known-issue documentation**: the kafka-k8s `relation-broken` crash (finding #6) is a severe operational hazard — an operator who removes the wrong relation can lose their kafka deployment — and should be called out as a known limitation in the README.

## Open questions

1. Is the empty `CharmConfig` intentional, or an oversight given Karapace's many upstream tunables?
2. Is the `remove_stores()` FIXME tracked as an issue, or just a stale comment?
3. Is the missing `()` on `fetch_my_relation_data()` a real bug or a deliberate placeholder? If intentional, it needs a comment.
4. Does the charm actually work end-to-end on Juju 3.6/k8s 1.32-classic as `concierge.yaml` targets? Neither cluster available for this review produced a working kafka stack, so this remains unverified.
5. Is kafka-k8s rev 27 (latest/edge) known-broken? The AccessDeniedException, misleading `active` status, and relation-broken crash were observed on 3 independent deployments across 2 clusters; rev 82 (3/stable) showed a different failure (stalled zookeeper handshake).
6. Why did the rawfile CSI provisioner report `ResourceExhausted` despite 124GB free? Likely loop-device exhaustion (`max_loop=8`) rather than actual disk space (unverified) — the provisioner's error message is misleading either way.
7. Does Juju 3.6 grant different default RBAC than Juju 4.0.5 to charm service accounts? The install hook's `_get_statefulset` call failed with 403 only on 4.0.5 in this review (unverified as a general rule).
