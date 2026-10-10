# vault-k8s-operator

A well-engineered charm for HashiCorp Vault on Kubernetes, with a clean split between a thin charm shell and the shared `vault-package` library, a consistent feature-manager pattern, and a broad integration-test suite. But the headline TLS integration mode (`tls-certificates-access` with an external CA) is completely broken on the k8s charm: a guard in `_configure` only ever passes in self-signed mode, and even if fixed, the TLS manager doesn't retry after the workload becomes ready. Since the production blueprint docs recommend this exact mode, any operator following the docs hits a wall immediately. Self-signed deployment works, scales, and recovers sensibly from a killed workload (it comes back sealed, and the charm reports it clearly). A maintainer should fix the TLS-integration guard and event-ordering bug first (findings #1–#2), then look at the S3 backup path/TLS-CA gaps and the unguarded `bootstrap-raft` action.

| | |
|---|---|
| Repo | canonical/vault-k8s-operator @ `c8f3f9b4` (2026-07-22) |
| Charms | vault-k8s (k8s), vault (machine), vault-kv-requirer (test helper) |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5) and concierge-k8s-3 (Juju 3.6.25), charmhub vault-k8s @ 2.0/edge rev 580 |
| Reviewed | 2026-08-09 |

## What it does

The vault-k8s charm deploys HashiCorp Vault on Kubernetes in HA mode using the Raft backend. It manages TLS certificates (self-signed or via `tls-certificates-access`), the PKI secret engine (self-signed or via `tls-certificates-pki`), the KV secrets engine, auto-unseal (provider and requirer), an ACME server, backup/restore to S3, ingress (per-app and per-unit), COS metrics/logging, tracing, and Grafana dashboards. The core logic lives in the shared `vault-package` pip package; the charm itself is a thin integration layer.

## Deployment log

**Juju 4.0.5 (concierge-k8s-4, model `rv-vault-k8s-deep`):**

```sh
juju add-model rv-vault-k8s-deep
juju deploy vault-k8s --channel 2.0/edge --trust -n 1
```

Self-signed mode (no TLS relation): charm progressed through `Waiting to be able to connect to vault unit` → `Waiting for CA certificate to be accessible in the charm` → `Waiting for vault to be available` → `Please initialize Vault or integrate with an auto-unseal provider`.

After manual `vault operator init` (1 key share, threshold 1) + `vault operator unseal` + `authorize-charm` action → **Active**. First `authorize-charm` attempt failed because the secret ID was passed as `secret://id` instead of the plain ID string; the charm expects a bare secret ID.

**Juju 3.6.25 (concierge-k8s-3, model `rv-vault-36`), ubuntu@24.04:**

```sh
juju add-model rv-vault-36
juju deploy vault-k8s --channel 2.0/edge --trust -n 1
```

Same flow: init/unseal/authorize → **Active**. No behavioural differences observed between Juju versions (status transitions, error messages, hook timing ~2s for config-changed).

**TLS integration attempt (both versions):** Deploying with `self-signed-certificates` and relating via `tls-certificates-access` → charm stuck at `Waiting for CA certificate to be accessible in the charm`. Relation was broken to fall back to self-signed mode. Root cause: see finding #1.

**`latest/edge` channel (rev 89):** Deploys on ubuntu@22.04, unit never reaches pebble-ready. Channel is unmaintained (open issue #905).

Models `rv-vault-k8s-deep` and `rv-vault-36` were destroyed after testing.

## Observed behaviour

### Deploy and resource usage
- Deploy time to active: ~15 minutes (including ~2m22s image pull), 23 hooks fired total.
- Idle resource usage: 99Mi memory, 103m CPU.
- Config change (`default_lease_ttl=200h`): ~0.2s, charm stayed active; Vault HCL re-rendered.
- Config-file comparison works correctly: logs "Existing config file is empty" on first push, no re-push on a second config-changed with identical values.

### Failure injection — workload process killed
- `pebble stop vault`: charm detected immediately → status `Waiting for vault to be available`.
- Pebble does **not** auto-restart the service after a manual stop (`startup: enabled` only starts it on pebble boot). `_set_pebble_plan()` only replans when the plan differs from the current layer, so a stopped-but-unchanged service triggers no replan.
- `pebble start vault`: Vault comes back **sealed** (shamir). Charm detects this correctly → status `Please unseal Vault`, which is correct UX since the charm cannot auto-unseal shamir vaults.
- If the process dies and pebble doesn't restart it, the charm just waits in `Waiting for vault to be available`; update-status re-evaluates but does not restart the stopped service.
- Identical behaviour on Juju 3.6 and 4.0.

### Failure injection — bad config values
- `default_lease_ttl=999999` (no unit suffix): accepted silently, no duration-format validation.
- `default_lease_ttl=999999h`: also accepted (valid unit).
- `totally_invalid_config_key=foo`: rejected by the Juju framework, never reaches the charm.

### Failure injection — PKI integration without required config
- Relating `tls-certificates-pki` without `pki_ca_common_name`: charm goes blocked with `pki_ca_common_name is not set in the charm config, cannot configure PKI secrets engine` — clear, actionable message.
- After setting `pki_ca_common_name`: charm immediately goes active; relation data flows correctly.

### Failure injection — removing a relation while sealed
- Removing `tls-certificates-pki` while vault is sealed: charm handles gracefully, stays blocked with `Please unseal Vault`. No traceback.

### Actions (tested on sealed vault with no S3 relation, both Juju versions)
- `list-backups`: clean failure — `Failed to list backups: S3 relation not created`.
- `create-backup`: clean failure — `Failed to create backup: S3 relation not created`.
- `restore-backup` (dummy backup-id): clean failure — `Failed to restore backup: S3 relation not created`.
- `bootstrap-raft` (single unit, sealed vault): **succeeded** — no check that vault is unsealed before raft bootstrap. Potentially dangerous.
- `authorize-charm` on a sealed vault: not tested.

### Scale-up (Juju 3.6, 1→3 units)
- Units 2 and 3 joined the peer relation and reached blocked `Please unseal Vault`. Scale operation completed correctly; all three units showed consistent status.

### Ingress integration (traefik-k8s on Juju 4)
- Traefik failed in this environment (`hook failed: config-changed`, no LoadBalancer IP provisioner) — an environment issue, not a vault charm bug.

## Findings

### `_configure` blocks on `ca_certificate_secret_exists()` — TLS integration mode broken on k8s

- **Severity**: critical
- **Kind**: bug
- **Where**: `k8s/src/charm.py:460` — `if not self.tls.ca_certificate_secret_exists(): return`
- **Evidence**: `ca_certificate_secret_exists()` (`vault-package/vault/vault_managers.py:594`) checks for a Juju secret labeled `self-signed-vault-ca-certificate`, which is only created in self-signed mode. In TLS integration mode the CA certificate comes from the relation and is pushed to the workload — no such secret is created. The machine charm avoids this with `ca_certificate_is_saved()` (`vault-package/vault/vault_managers.py:564-566`, and `machine/src/charm.py:650`), which checks `ca_certificate_secret_exists() OR tls_file_pushed_to_workload(File.CA)`.
- **Impact**: Any operator deploying Vault with an external TLS provider hits this immediately. Combined with finding #2, TLS integration mode is completely non-functional on the k8s charm — yet it's the mode recommended by `docs/reference/production_blueprint_k8s.md`.
- **Fix**: Change `k8s/src/charm.py:460` to use `self.tls.ca_certificate_is_saved()`, matching the machine charm.
- **Linter rule**: "Feature check in `_configure` that can only be satisfied in one code path"; specifically flag use of `ca_certificate_secret_exists()` in the k8s charm.

### TLSManager does not observe `pebble-ready` in TLS integration mode

- **Severity**: critical
- **Kind**: bug
- **Where**: `vault-package/vault/vault_managers.py:391` — `_configure_tls_integration` returns early when `workload.is_accessible()` is `False`
- **Evidence**: TLSManager's observed events for TLS integration only include `relation-changed` on the access relation. If that fires before the container is pebble-ready, the handler returns early and nothing retries. Observed log order: `tls-certificates-access-relation-changed` at 16:09:18, `pebble-ready` at 16:10:24 — after.
- **Impact**: Even with finding #1 fixed, TLS certs would never be pushed to the workload because the relevant event fires too early and is never retried.
- **Fix**: Add `self.charm.on.vault_pebble_ready` to TLSManager's observed events for TLS integration mode, or `defer()` the event when the workload isn't accessible.
- **Linter rule**: "Event handler that gates on workload accessibility but does not observe pebble-ready."

### S3 backup actions ignore `path` from the S3 relation

- **Severity**: high
- **Kind**: bug
- **Where**: `vault-package/vault/vault_managers.py:1892` (`_get_s3_parameters`), `:1785` (`create_backup`), `:1821` (`list_backups`)
- **Evidence**: `_get_s3_parameters()` returns `get_s3_connection_info()` with whitespace stripping only — the `path` field is never extracted. `create_backup` uses `Naming.backup_s3_key_name()` (`vault-backup-{model}-{timestamp}`, no path prefix); `list_backups` uses the bare prefix `Naming.backup_s3_key_prefix` ("vault-backup-"). Tracked as open issue #1035.
- **Impact**: Operators who configure `s3-integrator` with a path prefix (e.g. `vault/`) expect backups under that prefix. The charm silently writes to bucket root instead, risking collisions and violating operator intent.
- **Fix**: Extract `path` from the S3 relation data in `_get_s3_parameters()` and prefix all S3 key operations with it.
- **Linter rule**: not mechanically checkable — requires semantic understanding of the S3 relation protocol.

### S3 client does not use `tls-ca-chain` from the relation for self-signed endpoints

- **Severity**: high
- **Kind**: bug
- **Where**: `vault-package/vault/vault_s3.py:72-107` (`S3.__init__`)
- **Evidence**: The `S3` class accepts `access_key`, `secret_key`, `endpoint`, `application`, `region`, `skip_verify`, but no CA parameter. The boto3 client is built with `verify=False if skip_verify else None` — `None` falls back to the system CA bundle, and `tls-ca-chain` from the S3 relation is never consumed. Tracked as open issue #958.
- **Impact**: Backup/restore fails against S3-compatible storage with self-signed certs (e.g. Ceph RadosGW); the only workaround is `skip-verify: true`, which disables TLS verification entirely.
- **Fix**: Add a `ca_cert_path` parameter to `S3.__init__`, pass it to boto3's `verify` argument, and wire it from `BackupManager` off the S3 relation's `tls-ca-chain` field.
- **Linter rule**: not mechanically checkable.

### `bootstrap-raft` succeeds on a sealed vault without warning

- **Severity**: high
- **Kind**: bug
- **Where**: `vault-package/vault/vault_managers.py` (`RaftManager.bootstrap`)
- **Evidence**: Running `juju run vault-k8s/0 bootstrap-raft` against a sealed, single-unit vault returned `result: Raft cluster bootstrapped successfully.` with no warning about seal state.
- **Impact**: An operator troubleshooting a sealed vault might run this action expecting recovery help; it appears to succeed while potentially affecting Raft consensus state on a vault that isn't actually operable.
- **Fix**: Check seal state before bootstrapping and either reject with a clear message or emit a prominent warning.
- **Linter rule**: not mechanically checkable — requires domain knowledge that Raft bootstrap is sensitive to vault seal state.

### Vault workload not restarted when the process dies and the pebble plan is unchanged

- **Severity**: medium
- **Kind**: bug
- **Where**: `k8s/src/charm.py:1141-1147` (`_set_pebble_plan`)
- **Evidence**: `_set_pebble_plan()` only replans `if plan.services != layer.services`. A killed/stopped vault process doesn't change the plan, so `replan()` is never called, and pebble does not auto-restart a manually-stopped service. `_configure` only observes/reports vault's state — it never calls `start()`.
- **Impact**: If the vault process crashes, the charm may not restart it. Status stays `Waiting for vault to be available` indefinitely until an operator manually intervenes.
- **Fix**: In `_configure`, if `can_connect()` is true and the service isn't running, call `container.start(service_name)` before checking vault availability, or configure a pebble health check with `on-check-failure: restart`.
- **Linter rule**: "Charm checks workload availability but doesn't restart a stopped service."

### `default_lease_ttl` accepts values without a unit suffix — no config validation

- **Severity**: medium
- **Kind**: bug
- **Where**: `k8s/charmcraft.yaml` (config declaration), `k8s/src/charm.py:1055`
- **Evidence**: `default_lease_ttl` is declared `type: string` with no pattern validation, and rendered directly into the Vault HCL template. `999999` (no unit) is accepted silently; `999999h` (valid unit) also accepted.
- **Impact**: A malformed duration could cause Vault to start with unexpected lease durations or fail to start.
- **Fix**: Add a pattern (e.g. `^[0-9]+[hms]$`) to the config declaration in `charmcraft.yaml`, or validate explicitly in `_on_collect_status`.
- **Linter rule**: "Config option of type string with 'ttl' in the name has no pattern validation."

### `latest/edge` channel is broken and unmaintained

- **Severity**: medium
- **Kind**: ux
- **Where**: CharmHub — vault-k8s `latest/edge`, revision 89
- **Evidence**: `juju deploy vault-k8s --channel latest/edge` on Juju 4.0.5 pulls rev 89 on ubuntu@22.04; the unit never reaches pebble-ready. Tracked as open issue #905. `2.0/edge` deploys correctly.
- **Impact**: `latest/edge` is the channel many operators try first by default; a broken deployment wastes time and damages trust.
- **Fix**: Close the `latest/edge` channel or update it to a working revision.
- **Linter rule**: not mechanically checkable — CharmHub governance issue.

### Unit tests out of date: 16 failures from a missing `allow_bare_domains` argument

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `vault-package/tests/unit/test_vault_client.py` (~16 parametrized call sites)
- **Evidence**: `uv run pytest tests/unit/` in `vault-package` produces 16 `TypeError` failures: `VaultClient.role_config_matches_given_config() missing 1 required positional argument: 'allow_bare_domains'`. 112 of 128 tests pass; the 71 non-client tests (`test_vault_s3.py`, `test_vault_helpers.py`, etc.) all pass cleanly.
- **Impact**: These tests don't exercise the current code path — PKI role-config-matching coverage is effectively zero.
- **Fix**: Add `allow_bare_domains=...` to each affected parametrized call.
- **Linter rule**: "Test calls method with wrong number of arguments" — checkable with pyright on test files.

### K8s unit tests cannot run: missing `charms.data_platform_libs` dependency

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `k8s/tests/unit/` (all 13 test files)
- **Evidence**: `uv run pytest tests/unit/ --collect-only` in `k8s/` fails with `ModuleNotFoundError: No module named 'charms.data_platform_libs'` for every test file. Charm-libs declared in `charmcraft.yaml` are only fetched during `charmcraft pack`; `make vendor-shared-code` handles `vault-package` vendoring but not charm-libs.
- **Impact**: Developers cannot run the full unit-test suite from a fresh clone without extra steps; pre-commit testing is unreliable.
- **Fix**: Fetch charm-libs as a tox pre-command, or document the workaround in `k8s/CONTRIBUTING.md`.
- **Linter rule**: CI should verify `tox -e unit` passes after a fresh clone.

### `PKIManager` constructed twice per `_configure` invocation

- **Severity**: medium
- **Kind**: performance
- **Where**: `k8s/src/charm.py:507,511`
- **Evidence**: `_configure` calls `_configure_pki_secrets_engine(vault)` then `_sync_vault_pki(vault)`; both independently construct near-identical `PKIManager` instances, each reading the same config and hitting the Vault API.
- **Impact**: Every configure event doubles config reads and Vault API calls for PKI.
- **Fix**: Construct `PKIManager` once and call both `configure()` and `sync()` on the same instance.
- **Linter rule**: "Same class instantiated multiple times in one method body with identical arguments."

### `_sync_vault_pki` runs on non-leader units without a call-site leader guard

- **Severity**: low
- **Kind**: performance
- **Where**: `k8s/src/charm.py:511` (call site), `:771` (method definition, no leader check)
- **Evidence**: `_sync_vault_pki(vault)` is called unconditionally; the method itself has no leader guard (only `PKIManager.sync()` internally returns early for non-leaders). Contrast with `_sync_vault_kv` (line 510) and `_sync_vault_autounseal` (line 509), both of which guard on leadership before doing any work.
- **Impact**: Non-leader units in a multi-unit cluster do unnecessary work every `_configure` — minor CPU waste, and inconsistent with sibling sync methods.
- **Fix**: Add `if not self.unit.is_leader(): return` before calling `_sync_vault_pki`.
- **Linter rule**: "Feature manager sync called without leadership guard in charm code when sibling calls have one."

### No `upgrade-charm` handler

- **Severity**: low
- **Kind**: bug
- **Where**: `k8s/src/charm.py`, `machine/src/charm.py` (neither observes `upgrade-charm`)
- **Evidence**: Both charms rely on `config-changed` firing after upgrade to reconfigure.
- **Impact**: Acceptable today since both charms fully reconcile on config-changed, but any future upgrade-specific logic (data migration, removed config handling) has no hook to run in.
- **Fix**: Consider an `_on_upgrade_charm` handler that at minimum logs the upgrade, even if it delegates to `_configure`.
- **Linter rule**: "Charm has no upgrade-charm handler" — mechanically checkable but often intentional.

## Worth copying

- **Feature Manager pattern** (`vault-package/vault/vault_managers.py`): dedicated manager classes (TLSManager, PKIManager, KVManager, BackupManager, RaftManager, AutounsealProviderManager, ACMEManager) encapsulate feature logic behind `sync()`/`configure()`, keeping `_configure` manageable and features testable in isolation.
- **JujuFacade wrapper** (`vault-package/vault/juju_facade.py`): wraps the ops model API with typed exceptions distinguishing transient (`TransientJujuError`) from permanent errors (`NoSuchSecretError`, `NoSuchStorageError`, `SecretRemovedError`), enabling clean retry-vs-fail decisions upstream.
- **Security audit logging** (`vault-package/vault/security_logger.py`): structured JSON security events (key generation, certificate issuance, S3 operations), used from `VaultClient`, `TLSManager`, and `S3`.
- **Declarative charm-libs** (`k8s/charmcraft.yaml:151-192`): external libraries pinned under `charm-libs:` instead of vendored, making dependencies explicit and auditable.
- **Config validation at the edge** (`k8s/src/charm.py:255-313`, `_on_collect_status`): validation runs early with clear blocked messages before any operation is attempted; confirmed working (e.g. missing `pki_ca_common_name`).
- **NO_PROXY cluster-local protection** (`k8s/src/charm.py:1165-1183`): `.svc.cluster.local` is auto-appended to NO_PROXY when a proxy is configured, keeping internal k8s traffic off corporate proxies.
- **Idempotent config-file push** (`vault-package/vault/vault_helpers.py:config_file_content_matches`): compares parsed HCL trees, tolerating natural `retry_join` churn, avoiding unnecessary Vault restarts.
- **Clean Container abstraction** (`k8s/src/container.py`): thin adapter wrapping `ops.Container` into the shared `WorkloadBase` interface, enabling code sharing between k8s and machine charms.
- **Action error handling**: `list-backups`, `create-backup`, `restore-backup` all fail cleanly with clear messages ("S3 relation not created") when prerequisites are missing — no tracebacks.
- **Vault KV library** (`k8s/lib/charms/vault_k8s/v0/vault_kv.py`): pydantic-validated schema, proper event emissions, clean Requirer/Provider separation, functional documentation example.

## Common-practice notes

- **Monorepo structure**: k8s and machine charms plus shared `vault-package/` code; `.vendored/` for local dev and `charm-libs` for published charms — pragmatic and increasingly common.
- **`src/` layout**: follows modern charm convention.
- **`lib/charms/vault_k8s/v0/vault_kv.py`**: standard charm-library path; clean split between Juju-facing protocol and business logic in the shared package.
- **Terraform modules**: both `k8s/terraform/` and `machine/terraform/` exist for operator-driven deployment — increasingly standard for complex charms.
- **Scenario tests**: k8s charm uses `ops-scenario` (Scenario 7+) rather than `Harness`; machine charm has also migrated.
- **`collect-status`**: used consistently instead of deprecated per-hook status setting, with `event.add_status()`.
- **Drift between machine and k8s charms**: the `ca_certificate_secret_exists()` vs `ca_certificate_is_saved()` divergence (finding #1) is a textbook example of drift when charms independently guard against shared code; the shared package already provides the correct abstraction.
- **No `upgrade-charm` handler**: common across the ecosystem, acceptable but worth flagging (see finding above).

## Tests

### Unit tests
- **vault-package**: 128 collected, 112 pass, 16 fail (`test_vault_client.py`, missing `allow_bare_domains` argument on `VaultClient.role_config_matches_given_config()`). Non-client tests all pass cleanly.
- **k8s charm**: all 13 test files fail to collect (`ModuleNotFoundError: No module named 'charms.data_platform_libs'`) — charm-libs only available at `charmcraft pack` time.
- **Machine charm**: tests exist under `machine/tests/unit/` but were not run (environment not set up for machine substrate).
- **Lint**: `ruff check`, `ruff format --check`, `codespell` all pass cleanly.
- **Static analysis**: `pyright` fails with 10 import errors (missing charm-libs) but reports no type errors in charm or vault-package code.

### Integration tests
- Comprehensive suite: core (deploy/scale), PKI, ACME, auto-unseal, KV, backup/restore, COS, upgrade, self-signed PKI.
- Uses Jubilant (migrated from pytest-operator, git log at `7724c0ea`).
- ARM and s390x CI workflows exist alongside amd64.
- A dedicated `vault_kv_requirer_operator` test charm exercises the KV provider.

### Test gaps
- No integration test for TLS integration mode with an external certificate provider — would have caught findings #1 and #2.
- No test asserting `BackupManager` honours the S3 `path` prefix — would have caught finding #3.
- No test for `BackupManager` with S3 `tls-ca-chain` — would have caught finding #4.
- No integration test verifying `latest/edge` still deploys — would have caught the channel rot.
- No test for workload process crash recovery — would have caught the auto-restart gap.
- No test for `bootstrap-raft` on a sealed vault — would have caught the missing warning.
- No test for `default_lease_ttl` with an invalid format — would have caught the validation gap.

## Docs

- Comprehensive docs tree (`docs/`) with tutorials, how-tos, reference, and explanation sections — above average for charm repos.
- `README.md`: short and clear, links to docs and community info.
- CharmHub description: describes Vault's capabilities but not operational requirements.
- `docs/how-to/unseal_k8s.md`: accurate for self-signed mode; does not cover TLS integration mode. Documented `vault` CLI commands via `juju status` address parsing worked as described.
- `docs/how-to/upgrade.md`: brief but accurate; covers the 1.1x → 2.0 major upgrade path.
- `docs/reference/production_blueprint_k8s.md`: recommends TLS integration mode, which is broken in rev 580 (findings #1, #2).
- `k8s/terraform/README.md`: good `terraform apply` examples, well-documented variables.
- Missing: no doc mentions the S3 `path` limitation (finding #3) or the S3 `tls-ca-chain` limitation (finding #4) — operators would configure either to no effect.
- Contributing guide: multi-level (root `CONTRIBUTING.md` plus k8s/machine/vault-package specific guides); the k8s guide covers tox/test setup but not the charm-libs dependency issue.

## Open questions

1. Is the `config-changed` hang (#1029) the same root cause as finding #1 (`_configure` → `ca_certificate_secret_exists()` → early return)? Likely, given both hit the same code path — settle by reproducing with a cross-model TLS-provider relation.
2. Does the Ceph RadosGW TLS issue (#958) affect the machine charm too? `vault_s3.py` is shared, so probably yes — settle by testing against a real Ceph cluster from the machine charm.
3. Why is `latest/edge` still published given issue #905 has been open for months? Settle with the publishing team.
4. Does the `role_config_matches_given_config` signature drift (16 identical test failures from one change) indicate a broader brittleness in the parametrized test pattern? Settle by auditing other parametrized suites in the repo.
5. Does the machine charm's TLS integration mode actually work? It uses `ca_certificate_is_saved()` and (per notes) has no reported pebble-ready ordering issue — but this was not tested here (machine substrate unavailable in this environment) `(unverified)`.
6. Is `bootstrap-raft`'s permissiveness on a sealed vault intentional (e.g. for recovery scenarios), or an oversight? Settle with maintainers.
