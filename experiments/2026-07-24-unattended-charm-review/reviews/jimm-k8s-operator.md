# juju-jimm-k8s

JIMM is a k8s charm wrapping the JIMM Go server (`ghcr.io/canonical/jimm:v3.4.3`) as a
centralized authorization gateway and multi-controller management interface for Juju. It is
relation-heavy (PostgreSQL, OpenFGA, Hydra/OAuth, Vault, TLS, ingress) but well-engineered:
sophisticated JWKS rotation, clean status precedence, decent test coverage (82% on
`src/charm.py`). The charm itself is a thin orchestration layer with no business logic.

It is **not currently deployable on Juju 4.x**: the install hook fails indefinitely due to a
Juju 4.x K8s secrets RBAC regression, and `postgresql-k8s` (a required dependency) refuses to
deploy on Juju 4.x at all, making the database integration impossible on that Juju version
without a workaround. On Juju 3.6 it deploys and behaves correctly. A separate, Juju-version-independent
bug crashes the charm (rather than blocking it) on invalid `dns-name` config. A maintainer
should first fix the uncaught `ClientConfigError` on bad `dns-name`, then decide whether to
carry the Juju 4.x RBAC workaround in charm docs/tooling until Juju fixes the regression, and
resolve the duplicate `secret-changed` observer causing doubled reconciliation on Juju 4.x.

| | |
|---|---|
| Repo | canonical/jimm-k8s-operator @ `18c23ac` (2026-07-17) |
| Charms | juju-jimm-k8s |
| Substrate | Kubernetes only |
| Deployed | yes — (a) concierge-k8s-4 (Juju 4.0.12), 3/edge rev 120, required a manual K8s RBAC workaround before the install hook would succeed; (b) concierge-k8s-3 (Juju 3.6.25), 3/edge rev 120, clean install with no workaround. PostgreSQL-k8s (rev 925), Hydra (rev 404), OpenFGA-k8s (rev 128), and grafana-agent-k8s (rev 243) deployed alongside for integration testing. |
| Reviewed | 2026-08-17 |

## What it does

JIMM acts as an authorization gateway and central access point for Juju controllers. It
requires a cluster of related services: PostgreSQL (database), OpenFGA (authorization store),
Hydra (OAuth provider), Vault (secret storage, optional), TLS certificates, and Traefik
ingress. The charm manages JWKS key rotation (90-day period with 7-day pre-publication),
session key management, host SSH key management, OpenFGA authorization model provisioning,
trusted CA certificate injection via `update-ca-certificates`, and Pebble-based workload
lifecycle management.

## Deployment log

### concierge-k8s-4 (Juju 4.0.12)

1. Created model `rv-jimm-pars`. Deployed `juju-jimm-k8s --channel edge` (rev 120). Pod pulled
   the `jimm-image` OCI resource (265 MB, ~6 min).
2. **Install hook failed repeatedly** with:
   ```
   hook "install" failed: saving content for secret "k57audos2vai23p08eg0":
   attempt count exceeded: secrets "k57audos2vai23p08eg0-1" is forbidden:
   User "system:serviceaccount:rv-jimm-pars:juju-secret-consumer-f427d211..."
   cannot patch resource "secrets"
   ```
   Root cause: Juju 4.x creates per-secret `Role` objects granting only `namespaces/get,list`
   to the charm's consumer ServiceAccounts; the SA cannot `patch` secrets in its own
   namespace. `self-signed-certificates` (rev 586) hit the same error loop on the same model.
3. Applied a permissive `ClusterRole` (`juju-secret-consumer-all`, granting `secrets/get,list,
   create,patch,delete`) plus a `ClusterRoleBinding` and a background auto-bind loop for new
   `juju-secret-consumer-*` SAs in the namespace. Fixed the issue permanently for this model.
4. After the fix: install → leader-elected → jimm-pebble-ready → config-changed → start →
   peer-relation-changed completed. Charm settled into `blocked/Waiting for OAuth relation`.
5. Added `self-signed-certificates` (rev 586) and `traefik-k8s` (rev 397) as minimal partners.
   TLS certificate and ingress relations established.
6. Refreshed to 3/stable (rev 105): stop+install+start cycle, relations preserved. Refreshed
   back to 3/edge (rev 120): same clean cycle.
7. Refresh to 4/edge (rev 118) **failed**: `ERROR: one or more of the provided endpoints
   "certificates, dashboard, ..." do not exist` — 4/edge lacks `tracing` and `nginx-route`
   interfaces present in 3/edge.
8. Scaled to 2 units: jimm/1 required a new SA and hit the same RBAC issue, resolved by the
   auto-bind loop after ~3 minutes.
9. **Invalid DNS name config**: `juju config jimm dns-name="not-a-dns-name"` crashed
   `config-changed` with an uncaught `ClientConfigError` (see Findings). Unit entered an error
   retry loop; resetting `dns-name=""` recovered it.
10. Removed TLS, CA cert, and ingress relations — all `-broken` hooks handled cleanly.

### concierge-k8s-3 (Juju 3.6.25) — extended testing

1. Deployed `juju-jimm-k8s --channel 3/edge` (rev 120) to model `test-charm-xac2`.
2. **Install hook ran cleanly and immediately** — no RBAC issue. Full lifecycle completed in
   ~18 seconds.
3. Blocked at `Waiting for OAuth relation` — correct.
4. Same invalid `dns-name` produced the same `ClientConfigError` crash on Juju 3.6.
5. **Invalid `ssh-port`** (string `"not-a-number"`): Juju API rejects the type before the
   charm sees it — `ERROR: option "ssh-port" expected int, got "not-a-number"`.
6. **Invalid `jwt-expiry`** (`"not-a-duration"`): accepted by the Juju API, stored as env var
   `JIMM_JWT_EXPIRY`. Since JIMM never started (charm blocked on OAuth), the value is never
   validated by JIMM. Latent bug if JIMM starts with it.
7. **PostgreSQL integration**: deployed `postgresql-k8s` (rev 925, 14/stable, ~5 min to
   active). `juju relate juju-jimm-k8s postgresql-k8s` fired `database-relation-created →
   joined → changed` (×2). Charm progressed through the database check, remained blocked on
   OAuth. `juju remove-relation` fired `database-relation-departed → broken`; unit returned to
   idle.
8. **OAuth integration (Hydra)**: deployed `hydra` (rev 404, latest/edge), requiring
   `pg-database` and `public-route`. Related it to postgresql-k8s and traefik-k8s (rev 397).
   Hydra blocked on `Missing required relation with ui-endpoint-info`. Adding the OAuth
   relation to JIMM fired `oauth-relation-created → joined → changed`; JIMM correctly stayed
   blocked (Hydra never sent provider info because it was itself blocked). Removing the
   relation fired `oauth-relation-departed → broken` on both units; JIMM returned to
   `blocked/Waiting for OAuth relation`.
9. **`rotate-session-key` action**: action → `secret-changed` → `secret-remove` (old revision)
   fired correctly; session key rotated rev 1 → rev 2. Ran twice more later, both idempotent,
   <1s, `completed` status each time.
10. **`juju remove-application juju-jimm-k8s`**: pod deleted within seconds. All 4 Juju
    secrets (`session_key`, two JWKS keys, `nonce`) were garbage collected — not visible in
    `juju secrets` after removal. Clean teardown.
11. **Scale-down** (on k8s-4): `juju remove-unit jimm --num-units 1` reduced 2→1 units.
    Remaining unit settled to blocked/idle without issues.
12. **Full integration suite** — all six integrations established simultaneously:
    - `postgresql-k8s` (rev 925) → `database` relation: fires `created → joined → changed`
      (×2); DSN built correctly from Juju secrets (`secret-user`, `secret-tls`).
      `openfga-k8s` (rev 128) related to the same PostgreSQL and became `active`.
    - `self-signed-certificates` (rev 586) → `certificates` relation established.
    - `traefik-k8s` (rev 397) → `ingress` relation; ingress URL `http://10.43.45.0` published.
      `internal-ingress` also established.
    - `openfga-k8s` (rev 128) → `openfga` relation; HTTP API URL
      `http://openfga-k8s.test-charm-xac2.svc.cluster.local:8080` in relation data. `store_id`
      not yet present (store creation pending).
    - `hydra` (rev 404) → `oauth` relation; endpoints present
      (`authorization_endpoint: http://10.43.45.0/oauth2/auth`, `token_endpoint`,
      `introspection_endpoint`, `jwks_endpoint`, `userinfo_endpoint`). Hydra blocked on
      `ui-endpoint-info`, so JIMM stays blocked on OAuth.
    - `grafana-agent-k8s` (rev 243) → `metrics-endpoint`, `grafana-dashboard`, `logging` all
      established. grafana-agent-k8s itself blocked on `grafana-cloud-config` — expected, not a
      JIMM bug. Dashboards (`jaas-logs.json`, `jaas-metrics.json`) received and
      `updating dashboards` logged.
    - Removing the `postgresql-k8s` relation while JIMM was blocked on OAuth fired
      `database-relation-departed → broken` cleanly; unit stayed on
      `blocked/Waiting for OAuth relation`.

### Key Juju version difference

| | Juju 3.6 | Juju 4.0 |
|---|---|---|
| Install hook | Clean, immediate | Fails with K8s secrets RBAC issue |
| Config-changed (bad DNS) | Crash + retry loop | Crash + retry loop |
| Double `config-changed` per `juju config` call | 1 | 2 (charm bug) |

The Juju 4.x secrets RBAC issue is a regression not present in Juju 3.6, and affects
`self-signed-certificates` on the same cluster too — it is not specific to this charm and
would affect any charm calling `add_secret()` in an install hook on Juju 4.x.

## Observed behaviour

**Lifecycle correctness**: on Juju 3.6 the full hook sequence runs correctly with no errors
(install hook ~13-18s). On Juju 4.x, install fails repeatedly until the RBAC workaround is
applied, after which lifecycle hooks complete cleanly.

**Blocked-state messaging**: while waiting for OAuth, the unit correctly reports
`blocked/Waiting for OAuth relation`; each missing prerequisite has its own `BlockedStatus`
message. `_update_workload` status precedence is OAuth readiness → database → OpenFGA →
oauth provider info → JWKS secret → Vault (or insecure mode). Known gap: when `dns_name` is
empty, `_update_workload` logs a warning and returns without setting any status.

**Pebble readiness check**: the `jimm-check` HTTP check
(`http://localhost:8080/debug/status`, 1-minute period) returns HTTP 418 while JIMM is not
running (charm blocked on OAuth); after 3 failures Pebble triggers its recovery action.

**`_stop` ERROR log pollution while blocked**: on k8s-3, every `config-changed` (and
`_on_update_status`) call while JIMM is blocked fires `failed to stop the jimm service:
service 'jimm' not found` at `ERROR` level. Counted 22+ occurrences in ~10 minutes. This is
expected (JIMM hasn't started), and is caused by `_stop()` catching a broad `Exception`.

**HTTP OAuth redirect URL warning — repeated on every reconcile**: with no TLS relation
(traefik-k8s serving at `http://10.43.45.0`), the OAuth redirect URL uses HTTP. The hydra
library logs `Provided Redirect URL uses http scheme. Don't do this in production` on every
`_update_workload` call — observed at 09:59, 10:02, 10:03, 10:04, 10:05, multiple times per
minute. The warning is correct but excessively repeated.

**Invalid config handling, summarized**:
- `ssh-port="not-a-number"` — rejected at the Juju API layer, charm never sees it.
- `ssh-port=70000` (out of range) — accepted by the Juju API, passed to the Pebble layer
  unchecked. Latent runtime failure if JIMM tries to bind an invalid port.
- `log-level="invalid-log-level"` — accepted; would be handled (or not) at JIMM runtime.
- `jwt-expiry="not-a-duration"` — accepted, stored as env var, never validated because JIMM
  never started in these tests.
- `dns-name="not-a-dns-name"` — uncaught `ClientConfigError`, charm crash (see Findings).
- `dns-name="localhost"` — accepted; URL `https://localhost/auth/callback` was **not**
  rejected in testing even though the OAuth library's URL-validation regex appears to require
  a dot in the hostname. The reviewer could not fully reconcile this with the regex and flags
  the discrepancy as `(unverified)` — worth a maintainer check rather than a confirmed finding.

**Application teardown / scale-down**: `juju remove-application juju-jimm-k8s` deleted the pod
within seconds and garbage-collected all 4 Juju secrets. `juju remove-unit jimm --num-units 1`
reduced 2→1 units cleanly; each new unit added during scale-up requires the Juju 4.x RBAC
workaround again (new SA created), confirming the fix is cluster-wide via the auto-bind loop
rather than per-SA.

## Findings

### 1. Invalid `dns-name` config causes uncaught `ClientConfigError` — crash instead of block
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:420` → `lib/charms/hydra/v0/oauth.py:255` (upstream library)
- **Evidence**: `juju config jimm dns-name="not-a-dns-name"` produces
  `charms.hydra.v0.oauth.ClientConfigError: Invalid URL https://not-a-dns-name/auth/callback`.
  `config-changed` exits with status 1; the unit enters an error retry loop. Confirmed on both
  Juju 3.6 and 4.0.
- **Impact**: any operator who mistypes `dns-name`, or sets a value the library's URL
  validation rejects, crashes the charm into an unrecoverable retry loop with no descriptive
  `BlockedStatus`. The only recovery is resetting the config from a separate session.
- **Fix**: wrap the `update_client_config` call in a try/except that catches
  `ClientConfigError` and sets `BlockedStatus("Invalid dns-name config: <detail>")` instead of
  letting it propagate.
- **Linter rule**: not mechanically checkable — requires an integration test with invalid DNS.

### 2. `postgresql-k8s` incompatible with Juju 4.x — database integration impossible
- **Severity**: high
- **Kind**: bug / ux
- **Where**: deployment dependency, tested on concierge-k8s-4 (Juju 4.0.12)
- **Evidence**: `juju deploy postgresql-k8s` on Juju 4.0.12 fails with
  `ERROR: not supported Charm cannot be deployed because: charm requires all of the following:
  charm requires Juju version < 3.5.0, model has version 4.0.12` (the machine `postgresql`
  charm fails identically).
- **Impact**: JIMM requires a database relation. With `postgresql-k8s` unable to deploy on
  Juju 4.x, the full JIMM stack cannot be stood up on Juju 4.x without an alternative database
  charm.
- **Fix**: use a `postgresql-k8s` revision that supports Juju 4.x if one exists, or document
  that Juju 4.x deployments need a different database backend.
- **Linter rule**: not applicable.

### 3. Juju 4.x K8s secrets RBAC regression blocks the install hook
- **Severity**: high
- **Kind**: bug (upstream Juju regression, not charm-specific)
- **Where**: `src/charm.py:339–344` (`self.unit.add_secret()` in `_on_install`); also observed
  affecting `self-signed-certificates` rev 586 on the same cluster
- **Evidence**: `hook "install" failed: attempt count exceeded: secrets "..." is forbidden:
  User "juju-secret-consumer-..." cannot patch resource "secrets"`.
- **Impact**: on Juju 4.x, every charm calling `add_secret()` in the install hook fails. The
  workaround (ClusterRole + ClusterRoleBinding) requires cluster-admin permissions and must be
  applied per model/namespace.
- **Fix**: the fix belongs in Juju's controller/K8s backend; document the ClusterRole
  workaround for operators until Juju fixes the regression.
- **Linter rule**: not applicable.

### 4. `on_secret_changed` registered twice — doubled hook invocations on Juju 4.x
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:181` and `src/charm.py:297`
- **Evidence**: live observation on Juju 4.x confirmed two `config-changed` hooks per `juju
  config` call. Code shows two registrations of `secret_changed`:
  ```python
  self.framework.observe(self.on.secret_changed, self.on_secret_changed)   # line 181
  self.framework.observe(self.on.secret_changed, self._on_secret_changed)  # line 297
  ```
  `on_secret_changed` runs `_update_workload` unconditionally on every secret change;
  `_on_secret_changed` only runs it when `ssh-host-key-secret-id` is configured. Only one of
  the two fires on Juju 3.6; both fire on Juju 4.x.
- **Impact**: on Juju 4.x every `juju config` doubles Pebble layer pushes and secret fetches.
- **Fix**: remove one of the two registrations, or fold the SSH-specific handling into a
  single handler called once.
- **Linter rule**: "a charm must not register the same event more than once" — mechanically
  checkable by static analysis of `framework.observe` calls.

### 5. `ingress` and `internal_ingress` share the same ready handler — double reconciliation
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:237` and `src/charm.py:243`
- **Evidence**:
  ```python
  self.framework.observe(self.ingress.on.ready, self._on_ingress_ready)           # line 237
  self.framework.observe(self.internal_ingress.on.ready, self._on_ingress_ready)  # line 243
  ```
  Both `IngressPerAppRequirer` instances fire `ready` for the same event, calling
  `_on_ingress_ready` (and therefore `_update_workload`) twice per readiness event.
- **Impact**: doubled reconciliation work when both ingresses become ready together, which is
  the typical case.
- **Fix**: deduplicate in `_on_ingress_ready` (e.g. a set/counter), or register distinct
  handlers.
- **Linter rule**: "two different relation observers must not both call the same handler that
  invokes `_update_workload`" — not mechanically checkable.

### 6. `_on_update_status` accesses `event.relation` on `UpdateStatusEvent` — silently no-ops
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:698`
- **Evidence**: `UpdateStatusEvent` has no `relation` attribute; accessing it raises
  `AttributeError`, caught and swallowed by a broad `except Exception`. The intended
  `vault.request_credentials(event.relation, ...)` call never executes.
- **Impact**: periodic vault credential re-requests on `update-status` silently never happen.
- **Fix**: remove the `vault.request_credentials` call from `_on_update_status`; request
  credentials only on vault lifecycle events (`connected`, `ready`).
- **Linter rule**: "hook handler must not access `event.relation` on an event type without a
  relation attribute" — checkable via strict event type checking (e.g. pyright).

### 7. `_stop` logs ERROR for expected "service not found" condition while blocked
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:680–686`
- **Evidence**: every reconcile while JIMM is blocked (not started) causes `_stop()` to log
  `failed to stop the jimm service: service 'jimm' not found` at `ERROR`. Observed 22+ times
  in ~10 minutes on k8s-3. Caused by a broad `except Exception` catching the `KeyError`/
  `pebble.APIError` from `get_service().is_running()` on a nonexistent service.
- **Impact**: ERROR-level log pollution masks real failures from operators monitoring logs.
- **Fix**: guard with `if container.get_service(JIMM_SERVICE_NAME) is not None` before calling
  `.is_running()`, or catch `pebble.APIError` explicitly and log at DEBUG/INFO.
- **Linter rule**: not mechanically checkable.

### 8. `_update_workload` returns without setting status when `dns_name` is empty
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:442–444`
- **Evidence**:
  ```python
  dns_name = self._get_dns_name(event)
  if not dns_name:
      logger.warning("dns name not set")
      return
  ```
  No `BlockedStatus` is set; the unit retains its previous status.
- **Impact**: if DNS were the sole blocking factor (OAuth ready but no `dns-name`), the
  operator would see no actionable status — only a log warning.
- **Fix**: set `BlockedStatus("dns-name not configured")` before returning.
- **Linter rule**: not mechanically checkable.

### 9. TLS verification disabled in OpenFGA client
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/openfga_client.py:17`
- **Evidence**: `verify=False` hardcoded; the client `__init__` accepts a `verify` parameter
  but the charm always constructs the client with it disabled and no config to enable it.
- **Impact**: MITM risk for OpenFGA communication in production, with no way to opt into
  verification.
- **Fix**: default `verify=True`, allow override via charm config.
- **Linter rule**: not mechanically checkable.

### 10. `_vault_config` raises bare `RuntimeError` without setting status
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:374–376`
- **Evidence**:
  ```python
  except TooManyRelatedAppsError:
      logger.error("too many vault relations detected")
      raise RuntimeError("More than one relations are defined. Please provide a relation_id")
  ```
  No `BlockedStatus` set before raising.
- **Impact**: operator sees an unhandled exception rather than an actionable block message.
- **Fix**: set `BlockedStatus("Too many vault relations (limit: 1)")` before raising.
- **Linter rule**: "hook handler must not raise a bare RuntimeError without setting
  BlockedStatus" — not mechanically checkable.

### 11. Missing resource limits in metadata
- **Severity**: medium
- **Kind**: ux
- **Where**: `metadata.yaml` (absent `resources` section for CPU/memory)
- **Evidence**: upstream issue #74 (2025-05-19) requests pod resource requests/limits; none
  present.
- **Impact**: no scheduling constraint — JIMM can be placed on overcrowded nodes.
- **Fix**: add a `resources` section for the jimm container, following the
  `grafana-agent-k8s` pattern.
- **Linter rule**: "k8s charm metadata.yaml must define `resources.containers[*].{limits,
  requests}`" — not currently mechanically checkable.

### 12. Cross-channel refresh fails due to changed relation interfaces
- **Severity**: medium
- **Kind**: bug
- **Where**: upgrade path, `3/edge` → `4/edge`
- **Evidence**: `juju refresh jimm --channel 4/edge` (rev 118) failed with
  `ERROR: one or more of the provided endpoints "certificates, dashboard, ..." do not exist` —
  4/edge lacks `tracing` and `nginx-route` interfaces present in 3/edge.
- **Impact**: within-track refreshes work; cross-track refreshes require tearing down all
  relations first.
- **Fix**: align 4/edge interfaces with 3/edge, or document the incompatibility.
- **Linter rule**: not applicable.

### 13. Integration tests disabled in CI
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `test.yaml` CI workflow; commit `d5960ff` "ci: skip integration test workflow (#106)"
- **Evidence**: `test_jimm_oauth_browser_login` (Playwright) is the only end-to-end OAuth
  validation and is disabled; the bundle used for it (`identity-bundle.yaml`) pins
  `hydra@401`, `postgresql-k8s@774`, `traefik-k8s@298` — older than the revisions used in this
  review (hydra rev 404, which itself blocks on `ui-endpoint-info`).
- **Impact**: regressions in OAuth flows, JWKS rotation, and relation ordering are invisible
  to CI.
- **Fix**: re-enable with metallb configuration and registry credentials; refresh the bundle
  pins.
- **Linter rule**: not applicable.

### 14. `_on_certificate_expiring` not tested
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/charm.py:849–865` (uncovered; charm.py at 82% coverage)
- **Impact**: certificate renewal path is unvalidated by tests.
- **Fix**: add a test firing `CertificateExpiringEvent` and verifying CSR renewal.
- **Linter rule**: not applicable.

### 15. OAuth redirect URL uses HTTP when no TLS is configured — warning repeated excessively
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/hydra/v0/oauth.py:259`; `src/charm.py:420`
- **Evidence**: with traefik-k8s serving `http://10.43.45.0` (no TLS/metallb), every
  `_update_workload` call logs `Provided Redirect URL uses http scheme. Don't do this in
  production` — observed multiple times per minute in container logs.
- **Impact**: correct but noisy; obscures other log messages.
- **Fix**: log the warning once, or set `BlockedStatus("TLS certificates relation required for
  secure OAuth")`.
- **Linter rule**: not mechanically checkable.

### 16. `on_ingress_ssh_ready`/`_on_ingress_ssh_revoked` never call `_update_workload`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:898–904`
- **Evidence**:
  ```python
  def _on_ingress_ssh_ready(self, event):   # line 898
      logger.info(f"Ingress for SSH at {event.url}")
  def _on_ingress_ssh_revoked(self, _):     # line 902
      logger.info("This app no longer has SSH ingress")
  ```
  By contrast `_on_ingress_ready`/`_on_ingress_revoked` (HTTP ingress) both call
  `_update_workload`.
- **Impact** *(unverified whether JIMM actually consumes the SSH ingress URL from the Pebble
  layer)*: if it does, a changed SSH ingress URL would go stale.
- **Fix**: add `_update_workload` calls to these handlers, or confirm JIMM does not need the
  SSH ingress URL propagated.
- **Linter rule**: not mechanically checkable.

### 17. `_egress_subnets` raises unhandled `ValueError` for `None` binding
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:1103` (per notes, also referenced at lines 957–960 elsewhere)
- **Evidence**: `raise ValueError("unknown egress subnet")` when binding is `None`; path is
  untested. Called from `_on_update_status`, where it would be caught by a broad `except
  Exception` and logged only as a generic warning.
- **Fix**: return `[]` or log a specific message instead of raising.
- **Linter rule**: not mechanically checkable.

### 18. Certificate CA processing double-extracts from two data bag locations
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:1047–1060`
- **Evidence**: `get_all_certificates()` reads the app data bag; a manual loop separately reads
  the remote unit data bag — different keys. The comment "deal with v0 relations" is
  misleading since the app-bag read already covers v0.
- **Fix**: remove the manual loop and verify `get_all_certificates()` handles v0 correctly.
- **Linter rule**: not mechanically checkable.

### 19. Dead assignment in `_update_trusted_ca_certs`
- **Severity**: nit
- **Kind**: bug
- **Where**: `src/charm.py:1063` (immediately overwritten by line 1069)
- **Evidence**:
  ```python
  ca_bundle = "\n".join(ca_certs)          # line 1063 — dead
  ...
  ca_bundle = "\n".join(sorted(ca_certs))  # line 1069 — overwrites
  ```
- **Fix**: remove line 1063.
- **Linter rule**: not mechanically checkable (variable assigned twice without intervening use).

### 20. `requires_state_setter` silently does nothing on non-leader
- **Severity**: low
- **Kind**: ux
- **Where**: `src/state.py:10–18`
- **Evidence**: returns `None` silently when the unit isn't leader or state isn't ready. This
  also means `_on_database_relation_broken` does nothing if the peer relation is already gone
  — the review's status-log observation of the unit going to idle (not blocked) after
  database-relation-broken is consistent with this.
- **Fix**: add a `logger.debug` indicating the handler was skipped.
- **Linter rule**: not mechanically checkable.

### 21. No Prometheus alert rules defined
- **Severity**: low
- **Kind**: docs / test-gap
- **Where**: `src/prometheus_alert_rules/` — README only, no rule files
- **Impact**: operators have no alerting for JIMM down, certificate expiry, or JWKS rotation
  failures.
- **Fix**: add `jimm_down.rule`, `certificate_expiring.rule`, `jwks_rotation_stalled.rule`.
- **Linter rule**: "charm declaring `metrics-endpoint` provides must have alert rule files" —
  not currently checked.

### 22. `_on_ingress_ready`/`_on_ingress_revoked` not tested
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/charm.py:894–908`
- **Fix**: add a scenario test for `IngressPerAppReadyEvent`/`IngressPerAppRevokedEvent`.
- **Linter rule**: not applicable.

### 23. `_on_secret_remove` not tested
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/charm.py:929–931`
- **Fix**: add a test firing `SecretRemoveEvent` and verifying `event.remove_revision()`.
- **Linter rule**: not applicable.

### 24. `_egress_subnets` `ValueError` path not tested
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/charm.py:957–960`
- **Fix**: mock `get_binding("vault-kv")` to return `None` and verify handling.
- **Linter rule**: not applicable.

### 25. `_update_workload_certificates` v0 relation path not tested
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/charm.py:1066–1067`
- **Fix**: add a test with a v0 certificate-transfer relation.
- **Linter rule**: not applicable.

### 26. `_on_certificate_revoked` not tested
- **Severity**: low
- **Kind**: test-gap
- **Where**: `src/charm.py:869–890`
- **Evidence**: only `_on_certificate_available` is exercised (`test_add_certificates_relation`).
- **Fix**: add a test firing `CertificateRevokedEvent` and verifying CSR re-issue.
- **Linter rule**: not applicable.

### 27. `test_proxy_settings` pollutes `os.environ`
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py::test_proxy_settings`
- **Evidence**: direct `os.environ` mutation without a cleanup guarantee.
- **Fix**: use the pytest `monkeypatch` fixture.
- **Linter rule**: "test must not directly set `os.environ` without `monkeypatch`".

### 28. BLE001: blind `except Exception`
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:478, 685, 699, 1283, 1287`
- **Evidence**: ruff BLE001 flags these (`_get_host_key`, `_stop`,
  `vault.request_credentials`, `is_valid_private_key` PEM/SSH format checks).
- **Fix**: replace with specific exceptions (`ValueError`/`TypeError` for key validation,
  `pebble.APIError` for Pebble, an appropriate vault exception/`AttributeError`).
- **Linter rule**: BLE001 — mechanically checkable, already flagged by ruff.

### 29. `PIE790` false positive on `DeferError` class body
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:150`
- **Evidence**: `class DeferError(Exception): "..."; pass` — ruff flags the `pass` as
  unnecessary, but Python syntax requires a body statement after a bare docstring.
- **Fix**: suppress with `# noqa: PIE790`.
- **Linter rule**: ruff PIE790 should exclude exception classes with only a docstring (ruff
  issue).

### 30. RUF100: unused `noqa` directives
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:1259, 1266` (`# noqa: N802` on `ensureFQDN`/`ensureAbsoluteURL` —
  N802 is not enabled)
- **Fix**: remove the unused `noqa` comments.
- **Linter rule**: RUF100 — mechanically checkable by ruff.

### 31. UP032: f-string instead of `.format()`
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:686`, `src/charm.py:773`
- **Fix**: convert to f-strings.
- **Linter rule**: UP032 — mechanically checkable, fixable with `ruff --fix`.

### 32. RUF010: `repr(e)` should be `e!r`
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:700`
- **Fix**: `f"... {e!r}"`.
- **Linter rule**: RUF010 — mechanically checkable.

## Worth copying

- **JWKS rotation design**: 90-day rotation with 7-day pre-publication and a 6-hour
  propagation delay is sophisticated and well-documented. Two fixed secret labels
  (`jwks-key-0`, `jwks-key-1`) and a reconciler run on leader + update-status cleanly implement
  a four-phase lifecycle. `test_jwks_rotation_lifecycle` exercises the full two-cycle lifecycle
  with time-mocking.
- **Peer-relation-backed State class**: `services/charms/` provides a clean State class that
  transparently JSON-encodes values over the peer relation, with `requires_state`/
  `requires_state_setter` decorators expressing "this hook needs the peer relation first" —
  avoids the common mistake of using `StoredState` for this.
- **Comprehensive unit test suite**: 45 tests covering Pebble layer generation, OAuth config,
  dashboard relations, full JWKS rotation lifecycle, secret rotation, host key management, FGA
  auth model, proxy settings, CORS config, SSH config, certificate handling, and lifecycle
  events, with clean time/secret mocking.
- **OpenFGA client 404 handling**: `src/openfga_client.py` handles
  `authorization_model_not_found` (HTTP 404) gracefully, returning `None` instead of raising.
- **Terraform module completeness**: `terraform/` integrates JIMM with PostgreSQL, OpenFGA,
  Vault, OAuth, and Ingress via `juju_integration` resources, and uses `random_uuid` to
  auto-generate JIMM's UUID.
- **`can_connect` guard**: `_update_workload` opens with `if not container.can_connect():
  event.defer(); return`, correctly preventing `pebble.PathError` from deferred hooks.

## Common-practice notes

- Two separate ingress relations (`ingress`, `internal-ingress`) separate public and internal
  traffic; `ingress-ssh` deliberately uses `IngressPerUnit` (per-unit TCP routing) while HTTP
  ingress uses `IngressPerApp` — a reasonable design split.
- Uses `requests` directly for OpenFGA rather than an ops HTTP abstraction — pragmatic but
  bypasses ops HTTP retry/error handling.
- Libraries under `lib/charms/` use v0/v1 versioning consistently, all stable.
- No `requirements.txt`; `charmcraft.yaml` uses `charm-strict-dependencies: true` with PyPI
  packages declared in `charm-binary-python-packages` — a modern, reasonable approach.
- Test suite uses `Harness` throughout (deprecated in favour of `ops-scenario`); new tests
  should migrate.

## Tests

**Unit tests**: 45 passed in ~19-21s. Coverage: 82% `src/charm.py`, 75%
`src/openfga_client.py`, 87% `src/state.py`. Run with `pytest tests/unit/ -v --cov=src
--cov-report=term-missing`. Notable uncovered lines: `_on_install` vault nonce creation
(350–352), `_on_certificate_expiring` (849–865), `_on_certificate_revoked` (869–890),
`_on_ingress_ready`/`_on_ingress_revoked` (894–908), `_egress_subnets` None-binding path
(957–960), `_update_trusted_ca_certs` v0 path (1066–1067), JWKS file writing (592–595, 606).

**Lint**: `ruff check` reports 18 issues (12 fixable with `--fix`): 5× BLE001 (blind `except
Exception`, lines 478/685/699/1283/1287), 1× PIE790 false positive (line 150), 2× UP032 (lines
686/773), 2× RUF100 (unused `noqa` N802, lines 1259/1266), 1× RUF010 (line 700), plus 5×
UP032/UP045/EXE001 issues in `tests/integration/`.

**Integration tests**: disabled in CI since commit `d5960ff` ("ci: skip integration test
workflow (#106)"). `test_jimm_oauth_browser_login` (Playwright) is the only end-to-end OAuth
validation and requires the full IAM bundle (Hydra, PostgreSQL-k8s, OpenFGA, Vault, Traefik
×2), metallb IP ranges, and private registry credentials — not runnable in this review
environment. `test_openfga_integration` is similarly gated on a fully-deployed IAM platform.
`identity-bundle.yaml` pins `hydra@401`, `postgresql-k8s@774`, `traefik-k8s@298`; the Hydra
revision deployed in this review (404) is newer and blocked on `ui-endpoint-info`, so the
bundle's pinned revision may have different requirements.

## Docs

- `README.md`: brief but adequate — links to canonical-jaas-documentation, describes what JIMM
  does and how to deploy it, but not deploy-time prerequisites (relations/config needed).
- `CONTRIBUTING.md`: good developer guide (tox workflow, required relations, integration test
  setup); slightly stale — refers to `requirements-dev.txt` but actual deps live in
  `tox.ini`.
- `terraform/README.md`: minimal, links to external docs; the module itself
  (`main.tf`/`integrations.tf`/`variables.tf`) is well-commented.
- Charmhub description matches `metadata.yaml` and links to jaas documentation.
- No `SECURITY.md` and no dedicated operations guide for common failure scenarios.

## Open questions

1. Is the `on_secret_changed` double registration intentional? The two handlers behave
   differently (unconditional vs. SSH-secret-gated `_update_workload`); needs maintainer
   confirmation, especially given the Juju-version-dependent firing behaviour observed.
2. Is `verify=False` in the OpenFGA client intentional for some deployment model, or should it
   be configurable/default-`True`?
3. Why are integration tests still disabled after `d5960ff`? Is the test infrastructure
   (IAM bundle, metallb, registry) unmaintainable, or just deprioritized? The bundle pins are
   already stale relative to charmhub.
4. Does the Juju 4.x K8s secrets RBAC issue affect other charms ecosystem-wide? Observed
   affecting `self-signed-certificates` on the same cluster — likely systemic to Juju 4.x, not
   charm-specific.
5. Does `database.fetch_relation_data()` handle all PostgreSQL relation data formats,
   including any v0 unit-data-bag path? Untested.
6. Should `_on_database_relation_broken` behave differently if the peer relation is already
   gone when the database relation breaks? Current behaviour (silent no-op via
   `requires_state_setter`) is consistent with the observed idle (not blocked) status after
   database-relation-broken, but worth confirming as intentional.
7. Should SSH ingress readiness/revocation trigger `_update_workload` the way HTTP ingress
   does? Depends on whether JIMM reads the SSH ingress URL from the Pebble layer — unconfirmed.
8. `dns-name="localhost"` was accepted in testing despite the OAuth library's URL-validation
   regex appearing to require a dot in the hostname (as with the rejected
   `"not-a-dns-name"`). The reviewer could not fully explain this discrepancy; flagged
   `(unverified)` and worth a maintainer check rather than treated as a confirmed distinct bug.
