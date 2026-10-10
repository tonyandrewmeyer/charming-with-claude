# notary-k8s

Notary k8s is a sidecar charm that bridges the `tls-certificates` interface to the Notary certificate-management workload: it forwards requirers' CSRs into Notary and distributes approved certificates back over the relation. Code quality is good — clean status precedence, idempotent config push, 88 passing scenario tests, clean ruff/pyright/codespell — but the charm is **broken on Juju 4.x by a hardcoded storage path**, and its default Charmhub channel (`latest/edge`) is ~22 months stale because CI only publishes to `0/edge`. A maintainer should fix the CA-path bug and the channel/publishing mismatch first, then close the missing upgrade-migration and CSR-rejection paths.

| | |
|---|---|
| Repo | canonical/notary-k8s-operator @ `a02e839` (2026-07-15) |
| Charms | notary-k8s |
| Substrate | k8s |
| Deployed | yes — active on concierge-k8s-3 (Juju 3.6.25, `edge` rev 22); stuck `waiting` on concierge-k8s-4 (Juju 4.0.5) for rev 22, rev 57, and a locally packed HEAD build |
| Reviewed | 2026-08-14 |

## What it does

Deploys `ghcr.io/canonical/notary` in a single `notary` container with two filesystem storages (`config` 5M for certs/config, `database` 1G for the cert DB). Provides `certificates` (tls-certificates provider), `send-access-ca-certificate` (certificate_transfer), `metrics` (prometheus_scrape) and `grafana-dashboard`; requires `access-certificates` (tls-certificates requirer for its own server cert), `logging`, `tracing` and `ingress`. On deploy it generates self-signed server certs, creates a first admin account in Notary, stores the credentials in a Juju secret, logs in for a token, and reconciles the tls-certificates relation data against Notary's certificate-request API on every hook. TLS access certificates from a real provider replace the self-signed cert once that relation is added.

## Deployment log

Commands that matter (all against Charmhub unless noted):

```
juju switch concierge-k8s-4 && juju add-model rv-notary-k8s
juju deploy notary-k8s --channel edge --trust        # -> rev 22, latest/edge
```
Result: stuck forever at `waiting: Notary server not yet available`. Debug log repeats:
`couldn't complete HTTP request: Could not find a suitable TLS CA certificate bundle, invalid path: /var/lib/juju/storage/config/0/ca.pem`.
The workload itself is healthy — `curl -sk https://localhost:2111/status` from the unit returns `{"result":{"initialized":false,"version":"0.0.3"}}` — so the charm's client can't reach it only because it passes a CA file path that does not exist. On Juju 4.0.5 the charm container mounts storage at `/var/lib/juju/storage/config-0/` (verified with `juju ssh` + `mount`), not `/var/lib/juju/storage/config/0/`.

```
juju switch concierge-k8s-3 && juju add-model rv-notary-k3
juju deploy notary-k8s --channel edge --trust        # -> rev 22
```
Result: goes `active` in ~90 s, workload version 0.0.3. Storage is at `/var/lib/juju/storage/config/0/` on 3.6.25, so the hardcoded path is correct there.

To prove the bug is in current code and not just the stale rev 22:
- `juju deploy notary-k8s --channel 0/edge --trust` on concierge-k8s-4 → rev 57, stuck at `waiting: server not yet available`, same CA-path error.
- `charmcraft pack` of local HEAD, then `juju deploy ./notary-k8s_ubuntu@24.04-amd64.charm --resource notary-image=ghcr.io/canonical/notary:1.0.0` on concierge-k8s-4 → stuck the same way.

On the working 3.6 model (rev 22):
- `juju deploy self-signed-certificates --channel stable --trust` and `juju deploy tls-certificates-requirer --channel stable --trust`.
- `juju integrate notary-k8s:access-certificates self-signed-certificates:certificates` → the charm replaced the self-signed server cert with the provider cert (CA file changed, service restarted).
- `juju integrate notary-k8s:certificates tls-certificates-requirer:certificates` → the requirer's CSR appears in Notary (verified via `curl -H "Authorization: Bearer <token>" .../certificate_requests`); requirer reports `0/1 certificate requests are fulfilled`, which is correct — Notary holds the CSR until an admin approves it.
- `juju remove-relation notary-k8s:access-certificates self-signed-certificates:certificates` → cert files regenerated (self-signed CA re-created, timestamp 20:26:29).
- `juju scale-application notary-k8s 2` → unit/1 shows `waiting: multiple units not supported` (by design), unit/0 stays active.
- `juju config notary-k8s external-hostname=...` → rejected: `unknown option "external-hostname"`. Rev 22 does not have that config (it exists in HEAD and rev 57).
- Deploy without `--trust` on 3.6 (`rv-notary-notrust`) also reaches active, so `--trust` is not required for basic operation.
- `kubectl top pod` (3.6): notary pod ~44m CPU / 61 MiB. Charm size: 21 MB packed.
- No actions are defined (`juju actions notary-k8s` → "No actions defined").

## Observed behaviour

- On Juju 4.x the charm never progresses past "server not yet available"; every hook emits the TLS-CA-bundle error above plus `WARNING failed to login with the existing admin credentials` and `WARNING couldn't distribute certificates: not logged in`. None of this is visible from reading the code alone — the path string only fails against the actual 4.x mount layout.
- On Juju 3.6 the charm initialises Notary itself (creates first user, logs in, stores token). The admin secret on rev 22 is `{username, password, token}` — note `username`, while HEAD code reads `email` (see finding 3). Token JWT `exp` was ~1 h after issuance.
- Notary receives `GET /accounts/me` + `GET /certificate_requests` every update-status (10 s in my model), i.e. a bounded ~4 HTTP calls/hook; with the default 5-minute interval this is negligible.
- Removing the access-certificates relation correctly re-generates a fresh self-signed CA+cert+key and restarts the workload.
- Removing the `certificates` provider relation leaves the requirer's CSR in Notary's DB (id 1 still present afterwards) — nothing is ever deleted.

## Findings

### 1. Hardcoded Juju 3.6 storage path breaks the charm on Juju 4.x
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:52` (`CHARM_PATH = "/var/lib/juju/storage"`), `src/charm.py:137` (`f"{CHARM_PATH}/{CONFIG_MOUNT}/0/ca.pem"`), also `tests/integration/test_charm.py:243`
- **Evidence**: `self.client = Notary(f"https://{socket.getfqdn()}:{self.port}", f"{CHARM_PATH}/{CONFIG_MOUNT}/0/ca.pem")`. On Juju 3.6 storage is mounted at `/var/lib/juju/storage/config/0/`, but on Juju 4.0.x it is `/var/lib/juju/storage/config-0/`. Observed: every hook on concierge-k8s-4 fails with `Could not find a suitable TLS CA certificate bundle, invalid path: /var/lib/juju/storage/config/0/ca.pem`, while the workload answers on 2111. Reproduced on rev 22, rev 57 (`0/edge`), and a locally packed HEAD build; the 3.6 controller goes active.
- **Impact**: The charm cannot talk to its own workload on any Juju 4.x controller, so it never initialises Notary, never logs in, and can never distribute certificates. Anyone deploying the default channel on Juju 4.x gets a permanently waiting charm.
- **Fix**: Derive the path from the real storage mount instead of hardcoding, e.g. iterate `self.model.storages["config"]` and use `storage.location` (or use `Path("/var/lib/juju/storage").glob("config-*")` / a helper), and do the same in the integration test helper.
- **Linter rule**: mechanically checkable — flag absolute `/var/lib/juju/storage/<name>/<id>/` string literals in charm code (storage IDs are opaque and filesystem layout is Juju-version dependent); a CI `grep` for `storage/config/[0-9]` would catch it.

### 2. Default channel is ~22 months stale; CI publishes to `0/edge`, not `latest/edge`
- **Severity**: high
- **Kind**: docs / release-process
- **Where**: `.github/workflows/main.yaml` `publish-charm` job (`destination_channel: 0/edge`); `.github/workflows/integration-test.yaml:46` (`juju-channel: 3.6/stable`)
- **Evidence**: `latest/edge` (the default `--channel edge`) is rev 22, released 2024-10-08; `0/edge` is rev 57, released 2026-04-24. Observed: rev 22 has no `external-hostname` config option, uses a `username` secret key, and reports "Notary server not yet available"; rev 57/HEAD have `external-hostname`, `email`, and "server not yet available". The repo's own publish workflow targets `0/edge` only.
- **Impact**: An operator doing the natural `juju deploy notary-k8s --channel edge` gets a charm ~22 months behind HEAD, missing config, and with a different secret schema. Any docs written against HEAD (e.g. `external-hostname`) don't match the default deployment. Because CI tests only Juju 3.6, the Juju 4.x breakage in finding 1 is also invisible to CI.
- **Fix**: Publish current releases to `latest/edge` (or retire the `latest` track), and add a Juju 4.x lane to the integration matrix.
- **Linter rule**: not mechanically checkable (release-policy).

### 3. Secret schema migration missing: `username` → `email` breaks admin login on upgrade
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:66-76` (writes `email`) and `src/charm.py:472` (`email = secret_content.get("email", "")`)
- **Evidence**: HEAD writes/reads `email`; the published rev 22 secret observed on the 3.6 model contains `username`, `password`, `token` (no `email`). There is no migration or fallback (no `username` references in `src/`). The token is the same key, so the break only bites when the token expires (JWT `exp` observed ~1 h after issuance).
- **Impact**: An operator who upgrades rev 22 → current gets `email=""` from the existing secret; once the stored token expires the charm calls `login("", password)`, fails, and permanently logs `failed to login with the existing admin credentials` / `couldn't distribute certificates: not logged in`, silently stopping certificate distribution.
- **Fix**: Read both keys (`secret_content.get("email") or secret_content.get("username")`) and rewrite the secret in the new shape, or add a one-time migration on the first read.
- **Linter rule**: not mechanically checkable.

### 4. `assert` in production code crashes the hook on duplicate CSRs
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:297` (`assert len(notary_certificate_requests_with_matching_csr) < 2`)
- **Evidence**: two identical CSRs in Notary (operator-submitted duplicate, or two requirers sharing the same CN+key) make `len(...) == 2` and the assert raises `AssertionError` uncaught in `configure`, putting the unit into error state on every hook.
- **Impact**: One duplicate entry turns a benign reconcile into a permanent charm error with no operator-actionable message.
- **Fix**: Replace with a defensive `if len(...) > 1: log warning; continue` (or reconcile each match).
- **Linter rule**: mechanically checkable — flag bare `assert` statements in `src/` charm handlers (comparable to bugbear B011).

### 5. Rejected/revoked CSRs are never reported to the requirer when no cert was issued
- **Severity**: medium
- **Kind**: ux / bug
- **Where**: `src/charm.py:304-321`
- **Evidence**: the reject/revoke branch only fires `if len(certificates_provided_for_csr) > 0`, and it never calls `self.tls.set_relation_error(...)` anywhere in `src/charm.py`. The tls-certificates V4 library exposes `set_relation_error`/`ProviderCertificateError` specifically for this (`deps/charmlibs/interfaces/tls_certificates/_tls_certificates.py:3473`).
- **Impact**: If an admin rejects a requirer's CSR in Notary before any cert was ever provided, the requirer sits in "0/1 certificate requests are fulfilled" forever with no error databag entry — indistinguishable from "still waiting", and nothing tells the operator why.
- **Fix**: On `status == "Rejected"` call `set_relation_error(ProviderCertificateError(..., error=...))` so the requirer's tls-certificates lib reports the denial.
- **Linter rule**: not mechanically checkable.

### 6. CSRs and issued certificates are never removed from Notary when requirers leave
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:144-149` (relation_departed/broken all routed to `configure`) — no delete logic exists anywhere in `src/` (`src/notary.py` has a `DeleteCertificateRequestResponse` dataclass but no delete method)
- **Evidence**: after `juju remove-relation notary-k8s:certificates tls-certificates-requirer:certificates`, `GET /certificate_requests` still returned the requirer's CSR (id 1).
- **Impact**: CSR/cert entries accumulate in Notary's DB forever, cluttering the approval UI and leaking cert material for departed requirers; operators must clean up manually.
- **Fix**: On relation_departed/broken, delete the departed relation's CSRs from Notary (add a `delete_certificate_request` client method).
- **Linter rule**: not mechanically checkable.

### 7. Unguarded `container.pull` in two code paths can crash a hook
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:399-402` (`saved_cert = self.container.pull(...).read()`), `src/charm.py:346-348` (`with self.container.pull(...) as ca_cert_file:`)
- **Evidence**: both calls lack the `try/except ops.pebble.PathError` guard that `_self_signed_certificates_generated` (`:432-435`) and `_certificates_available` (`:457-458`) use. If `certificate.pem` is absent (first path) or `ca.pem` is absent (second path) — e.g. first configure with an already-active access relation, or an operator deleted the file — the hook raises `PathError`.
- **Impact**: Error-state instead of a clean retry/BlockedStatus in a reachable edge case.
- **Fix**: Wrap in `except ops.pebble.PathError: return False` as the neighbouring methods do.
- **Linter rule**: mechanically checkable — hook handlers must guard `container.pull` with a `PathError` catch (or `can_connect`); a linter can flag `pull` calls not inside a `try`.

### 8. Self-signed cert not regenerated when the pod FQDN changes (no external-hostname set)
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:441-444`
- **Evidence**: `_self_signed_certificates_generated` returns `True` immediately when `current_hostname is None`, skipping the SAN check — but `_generate_csr_sans_dns` always includes `socket.getfqdn()`. After rescheduling (new pod FQDN), the existing self-signed cert keeps the old FQDN SAN and is never regenerated.
- **Impact**: Clients connecting by FQDN get a hostname-mismatch on a re-scheduled pod, silently, because the check short-circuits.
- **Fix**: When external-hostname is unset, validate the FQDN SAN too (e.g. compare against `socket.getfqdn()` rather than returning early).
- **Linter rule**: not mechanically checkable.

### 9. Config description overstates what `external-hostname` does
- **Severity**: nit
- **Kind**: docs
- **Where**: `charmcraft.yaml` config `external-hostname` ("the subject in the generated self-signed certificates") vs `src/charm.py:417-419` (common_name is the fixed `CERTIFICATE_COMMON_NAME`; the hostname is only added to `sans_dns`)
- **Evidence**: `generate_csr(common_name=CERTIFICATE_COMMON_NAME, sans_dns=self._generate_csr_sans_dns())` — external-hostname is a SAN, not the subject.
- **Impact**: Operators reasoning about the generated cert subject will be misled.
- **Fix**: Change the description to "a SAN in the generated self-signed certificate".
- **Linter rule**: not mechanically checkable.

### 10. Wrong auth-mechanism comment in the Notary client
- **Severity**: nit
- **Kind**: docs
- **Where**: `src/notary.py:138-139` ("Notary 1.0 authenticates API requests through the session cookie, not the Authorization header.")
- **Evidence**: live API tested: `curl -H "Authorization: Bearer <token>"` succeeds, while `curl -H "Cookie: user_token=<token>"` returns `{"error":"Unauthorized"}`. The code works because it sends both, but the comment describing why is backwards.
- **Impact**: Misleading comment for future maintainers touching auth.
- **Fix**: Correct or delete the comment.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Status precedence** (`src/charm.py:177-196`): one ordered list of `CollectStatusEvent` checks (leader → container → storages → certs → API → initialized) with actionable messages; easy to read and extend.
- **Idempotent config push** (`src/charm.py:205-243`): pulls the existing file, compares, and only pushes/restarts on real change — the right pattern for `config-changed`/`update-status`.
- **Reconciler discipline**: `configure()` is driven entirely by re-deriving desired state from relation data + the Notary API, with `PathError`/`SecretNotFoundError` handling; no `StoredState`, no `defer()`.
- **Clean HTTP client isolation** (`src/notary.py`): typed dataclasses per endpoint and a single `_make_request` error path keep the charm readable; every network error is converted to `None` rather than an exception.
- **Scenario test matrix** (`tests/unit/test_charm.py`): systematically exercises the storage×container×network×workload-state combinations for `configure` and `collect_status`; the mock-the-boundary style (patching `notary.Notary.__new__`) is effective.
- **Modern tooling**: `charmcraft.yaml` with `charm-libs` + PyPI-managed interface libs, `uv`/`tox`, `ruff` + `pyright` (strict missing-param check) + `codespell` all wired into CI — all green locally.

## Common-practice notes

- Follows current ecosystem conventions: single `charmcraft.yaml` (no `metadata.yaml`), `platforms` with multi-base shorthand, OCI resource with `upstream-source`, `uv` lockfile, GitHub shared workflows, jubilant-based integration tests. No drift to flag there.
- The `0/edge` vs `latest/edge` split is the one clear divergence from convention: most charms publish the default `latest` track, so `--channel edge` gets current code; here the default track is effectively abandoned.
- Depending on PyPI `charmlibs-interfaces-*` packages (instead of vendoring `lib/charms/...` under the repo) is newer-but-fine practice; the `charmcraft fetch-libs` step is still needed for the grafana/loki/prometheus/traefik libs, so the repo has two library delivery mechanisms side by side (mildly inconsistent but not wrong).
- The wildcard Prometheus target `*:2111` (`src/charm.py:122`) is a standard k8s-charm idiom; fine.
- No self-owned `lib/charms/<charm>/v<N>/` libraries — nothing to version here.

## Tests

- Unit: 88 scenario tests pass (`PYTHONPATH=src:lib uv run --group test pytest tests/unit` → `88 passed in 3.78s`). They will not run from a bare `uv run pytest` (need `charmcraft fetch-libs` first and `src`/`lib` on `PYTHONPATH`); `tox -e unit` fails out of the box without the `tox-uv` plugin's `uv-venv-lock-runner` (`HandledError: runner 'uv-venv-lock-runner' is not available`). CONTRIBUTING.md does document `uv tool install tox --with tox-uv`, so this is a setup gap, not a doc gap.
- Linters: `ruff check src tests` clean, `ruff format --check` clean, `codespell` clean, `pyright src` → 0 errors/warnings. `charmcraft analyse` of the packed charm passes everything except `pydeps`, which crashes with a charmcraft tooling error (`'StopIteration' object has no attribute 'rstrip'`), not a charm defect.
- Integration tests (`tests/integration/test_charm.py`) assert real behaviour (CA changes across relation add/remove, CSR posted, certificate distributed end-to-end, ingress endpoint reachable) rather than only active/idle, but the loki/prometheus test only waits for active/idle and never checks that logs/metrics actually flow.
- Coverage gaps relative to the findings: no test for Juju 4.x storage layout (finding 1); no test for the duplicate-CSR assert path (finding 4); no test for rejection-before-issuance (finding 5); no test for relation departure cleanup (finding 6); no test that a secret written by an old revision (`username`) is still readable (finding 3). The unit tests themselves set the secret to the stale shape `{"username": "hello", ...}` (`tests/unit/test_charm.py:3143` and nearby) while the charm reads `email`, so the mock matches neither the old nor new code faithfully and would not catch finding 3.

## Docs

- README is minimal (3 paragraphs + links); the charmhub description is two sentences. A new operator cannot get started from the repo docs alone — nothing explains the two storage volumes, the admin secret (`Notary Login Details`), how to approve a CSR, that CSRs queue in Notary until manually approved, or the single-unit limitation.
- The charmhub description ("automatically receive CSRs and distribute certificates") is accurate about the happy path but omits the manual-approval step that the requirer's "0/1 certificate requests are fulfilled" status implies.
- `external-hostname` docstring/config text drift is covered in finding 9; `_get_external_hostname_config`'s docstring ("or socket fqdn if it was not set") also contradicts the implementation which returns `None` (`src/charm.py:517-526`).
- CONTRIBUTING.md is accurate and current (uv/tox/charmcraft steps all work as written).

## Open questions

- Whether the `username`→`email` break (finding 3) is a live migration concern depends on how many rev-22 deployments upgrade; the fix is trivial either way, so it should be done regardless.
- Whether Notary's API really ignores the `Authorization` header in some future version (the comment in `src/notary.py`) — observed behaviour today is the opposite; settling it would just mean deleting the comment.
- Whether ingress requires `--trust` — basic deploy worked without it, but the traefik ingress relation was not exercised without trust; running the ingress integration test without `trust=True` would settle it.
