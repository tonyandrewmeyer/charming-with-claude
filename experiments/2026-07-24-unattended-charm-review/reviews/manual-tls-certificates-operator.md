# manual-tls-certificates

A machine charm that distributes X.509 certificates to requirer charms via the `tls-certificates` (V4) interface, and optionally distributes a trusted certificate bundle via `certificate_transfer`. Operators supply signed certificates through two Juju actions: `get-outstanding-certificate-requests` (read-only) and `provide-certificate` (write). The charm is a thin ops wrapper (~320 lines of custom logic) over `charmlibs-interfaces-tls-certificates`, `charmlibs-interfaces-certificate-transfer`, and `cryptography`.

It works on LXD: the core workflow (relation, CSR discovery, `provide-certificate` reaching the handler) was exercised and behaves correctly. On Kubernetes it is currently unusable — a bundled library call crashes `update-status` on the first relation and the unit is stuck in `error` state indefinitely, blocking the action that is the whole point of the charm. A maintainer should reproduce and fix the k8s `permission denied` crash before anything else, then publish local HEAD (which is well behind `1/edge`).

| | |
|---|---|
| Repo | canonical/manual-tls-certificates-operator @ `3754d13` (2026-07-10) |
| Charms | manual-tls-certificates |
| Substrate | machine (LXD) and k8s |
| Deployed | yes — `concierge-lxd-4`, rev 108 (`latest/stable`) and `concierge-k8s-4`, rev 187 (`latest/edge`) |
| Reviewed | 2026-09-01 |

## What it does

The charm waits for a `tls-certificates` relation. When a requirer (e.g. `tls-certificates-requirer`) requests a certificate, status changes to `ActiveStatus("N outstanding requests, use juju actions to provide certificates")`. The operator runs `get-outstanding-certificate-requests` to list CSRs, generates signed certificates externally, and calls `provide-certificate` with base64-encoded PEM data. An optional `trusted-certificate-bundle` config option exposes a CA certificate to charms via `certificate_transfer`. There is also an optional `tracing` interface requirer for observability.

## Deployment log

### LXD model (`rv-manual-tls`, `concierge-lxd-4`, rev 108)

```
juju add-model rv-manual-tls --controller concierge-lxd-4
juju deploy manual-tls-certificates --channel stable
→ Deployed rev 108 in ~3 minutes (machine allocation + install + start)

juju deploy tls-certificates-requirer --channel stable --constraints arch=amd64
juju integrate manual-tls-certificates tls-certificates-requirer

# Status updates on periodic collect_unit_status (~5 min after relation created)
→ 05:48:09 certificates-relation-changed fires
→ 05:52:22 update-status fires → status "1 outstanding requests"
→ juju run ... get-outstanding-certificate-requests
→ Returns: [{"relation_id": 4, "csr": "-----BEGIN CERTIFICATE REQUEST-----..."}]

# provide-certificate action test (rev 108)
juju run ... provide-certificate <test params>
→ "Action input is not valid." — params reach the charm handler; ValueError from cert parsing
# (params ARE received; the test cert was invalid)

juju remove-relation manual-tls-certificates tls-certificates-requirer
→ certificates-relation-departed → certificates-relation-broken → status "No outstanding requests."

juju integrate manual-tls-certificates tls-certificates-requirer
→ Status back to "1 outstanding requests" in ~5 min (periodic update)

juju add-unit manual-tls-certificates -n 2
→ Machines 3 and 4 allocated but stuck pending (LXD resource exhaustion)
juju remove-unit manual-tls-certificates/1 manual-tls-certificates/2

juju remove-application manual-tls-certificates
→ stop hook → remove hook → unit terminated cleanly
```

### k8s model (`rv-manual-tls-k8s`, `concierge-k8s-4`, rev 187)

```
juju deploy manual-tls-certificates --channel latest/edge
→ Deployed rev 187 in ~4 minutes (pod scheduling + install + start)

juju deploy tls-certificates-requirer --channel stable
juju integrate manual-tls-certificates tls-certificates-requirer

# tls-certificates-requirer goes into error state (k8s secrets RBAC issue — requirer charm bug)

# manual-tls-certificates goes into error state during update-status:
# 05:47:59 update-status → collect_unit_status → get_outstanding_certificate_requests()
#   → tls_certificates_interface._configure() → _remove_certificates_for_which_no_csr_exists()
#   → get_provider_certificates() → _load_provider_certificates()
#   → relation.data[self.charm.app].get()  ← ModelError: permission denied (unauthorized access)
# 05:48:04 update-status (retry) → same error
# 05:48:15 update-status (retry) → same error
# Unit status: error — "hook failed: 'update-status'", never recovers without juju resolve
```

## Observed behaviour

- **Install/start timing (LXD)**: ~9s from machine Running to unit active/idle.
- **Install/start timing (k8s)**: ~15s from pod scheduling to unit active/idle (until the relation trigger causes error state).
- **Hook sequence (LXD)**: `install → leader-elected → config-changed → start` fires reliably.
- **Hook sequence (k8s)**: Same startup sequence; then `certificates-relation-created → certificates-relation-joined → certificates-relation-changed` succeed, but the subsequent `update-status` (~5 min later) crashes with `ModelError: permission denied`.
- **Status correctness (LXD)**: `collect_unit_status` correctly reflects outstanding CSR count via periodic firing and relation-change events, but only updates ~5 minutes after a relation is created (next `update-status`), not immediately on relation-changed.
- **`get-outstanding-certificate-requests`**: works correctly on LXD (rev 108); returns the CSR list via `event.set_results({"result": json.dumps([...])})`.
- **`provide-certificate` (LXD, rev 108)**: params reach the handler correctly. Test with invalid placeholder cert data gave `"Action input is not valid."` (`ValueError` from `Certificate.from_string()`), confirming params reach the handler. Not tested with a real matching cert+CSR due to time constraints.
- **`provide-certificate` (k8s, rev 187)**: cannot be tested — the unit is in `error` state from the `update-status` crash and actions cannot be invoked on a unit in error state.
- **Relation removal (LXD)**: clean `certificates-relation-departed → certificates-relation-broken`, status updates within the same hook context, no traceback.
- **Unit restart (LXD)**: `juju-unit-agent` restart causes no issues; status reflects state correctly afterward.
- **Juju refresh (LXD, rev 108 → rev 187)**: `upgrade-charm` and `config-changed` fire, status preserved correctly.
- **Application removal (LXD)**: `stop` hook ("stopping charm software"), `remove` hook ("cleaning up prior to charm deletion"), unit reaches `terminated`.
- **Scale-up (LXD)**: `juju add-unit -n 2` allocates machines 3 and 4 but they stay `pending` — LXD resource exhaustion in the test environment, not a charm issue.
- **k8s `tls-certificates-requirer` integration**: the requirer charm (rev 143) fails its `certificates-relation-created` hook on k8s due to a k8s secrets RBAC issue (service account lacks `secrets patch`). This is a `tls-certificates-requirer` bug, not `manual-tls-certificates`.
- **`trusted-certificate-bundle` config**: present in local HEAD (`charmcraft.yaml` lines 59–62) and confirmed present in rev 187 on k8s; absent only in rev 108, which predates it.
- **`certificate_transfer` integration**: not tested — no suitable requirer charm available in this environment.
- **`tracing` interface**: not tested — no suitable tracing provider for machine or k8s substrate available.
- **Hook noise**: after `config-changed` with no material change, no unnecessary workload restarts observed.

## Findings

### k8s (rev 187): `update-status` crashes with `permission denied`, unit stuck in `error` state

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:86–98` (`_on_collect_unit_status`), triggered by `tls_certificates_interface` library internals (bundled at `lib/charms/tls_certificates_interface/v4/tls_certificates.py:1586`)
- **Evidence**: On k8s (rev 187, `concierge-k8s-4`), once a `certificates` relation exists, `update-status` fails every ~20s with:
  ```
  collect_unit_status → get_outstanding_certificate_requests()
    → _configure() → _remove_certificates_for_which_no_csr_exists()
    → get_provider_certificates() → _load_provider_certificates()
    → relation.data[self.charm.app].get()  ← ModelError: permission denied (unauthorized access)
  ```
  The library reads the provider's own application databag; on k8s this read fails. The exception is uncaught, the hook fails, and the unit goes to `error` — never recovering without manual `juju resolve`. Not reproduced on LXD (rev 108).
- **Impact**: The charm is unusable on Kubernetes: `provide-certificate` cannot be invoked once the unit is in `error`, so the whole operator workflow is blocked as soon as a requirer relation is integrated. Not caught by CI, which appears to run against LXD/machine substrate.
- **Fix**: Either fix the library (`_configure()` should not call `get_provider_certificates()` unconditionally, or should wrap the read in a try/except) or stop relying on `collect_unit_status` routing through `_configure()` — e.g. handle `certificates-relation-changed` directly and call `get_outstanding_certificate_requests()` without triggering the provider-certificate cleanup path.
- **Linter rule**: not mechanically checkable — requires a live k8s deployment to reproduce.

### `provide-certificate` action inaccessible/unverified on k8s (rev 187); confirmed working on LXD (rev 108)

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:195` (`_on_provide_certificate_action`)
- **Evidence**: On k8s the unit is in `error` state (see above), so `provide-certificate` cannot be invoked at all. On LXD, the action params reach the handler correctly — an earlier test with invalid cert data returned `"Action input is not valid."` (a `ValueError`) rather than a `KeyError` for missing params. That earlier `KeyError` observation was on rev 187/k8s, not rev 108, so it may be version- or substrate-specific. Tracked upstream as GitHub issue #527, still open.
- **Impact**: The core operator workflow — providing a signed certificate for a CSR — cannot be exercised on k8s deployments at all right now; on LXD it works for well-formed input.
- **Fix**: Investigate the interaction between `juju run` CLI params, the unit agent, and `ActionEvent` restoration on k8s specifically; compare against the `jubilant` code path used by integration tests, which is unaffected.
- **Linter rule**: not mechanically checkable — requires a live k8s integration test against the specific Juju/ops/charm-lib version combination.

### `CertificateTransferProvides.add_certificates` silently no-ops on non-leader

- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/charmlibs/interfaces/certificate_transfer/_certificate_transfer.py:240–241`
- **Evidence**:
  ```python
  if not self.charm.unit.is_leader():
      logger.warning("Only the leader unit can add certificates to this relation")
      return
  ```
  No status is set and no event is deferred; the relation data simply isn't updated.
- **Impact**: If the config-changed handler runs on a non-leader (e.g. after a unit-agent restart during leadership churn), the certificate bundle is never pushed to `certificate_transfer`. The requirer waits indefinitely with only `WaitingStatus` on its own side; the provider shows no error.
- **Fix**: Have the charm check leadership before calling `add_certificates` and set `BlockedStatus("Leader required to push certificate bundle")`, rather than relying on the library's silent return.
- **Linter rule**: "library method silently returns on non-leader without setting status or deferring" — mechanically checkable with a custom lint rule.

### Local HEAD (`3754d13`) is several weeks behind `1/edge` (rev 458)

- **Severity**: medium
- **Kind**: maintenance
- **Where**: `charmcraft.yaml`
- **Evidence**: Local HEAD is `3754d13` (2026-07-10); `1/edge` carries rev 458 (2026-08-17), roughly five weeks newer. The `trusted-certificate-bundle` config (commit `7b489d1`) is present in both local HEAD and rev 187 — the review's earlier internal claim that it was "never published" was wrong and is corrected here.
- **Impact**: Operators on `1/edge` may have fixes not present in local HEAD; whether rev 458 fixes the k8s crash above is unverified (untested — `1/edge` is arm64-only in this environment).
- **Fix**: Publish local HEAD to `1/edge` and confirm parity, or document the gap.
- **Linter rule**: not mechanically checkable.

### `_on_config_changed` does not set status when `trusted-certificate-bundle` is invalid

- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:123`
- **Evidence**:
  ```python
  except (KeyError, ValueError) as e:
      logger.warning("Trust certificate relation cannot be fulfilled: %s", e)
  ```
  Only a warning is logged; the unit status is unchanged. If there are no outstanding CSRs, status becomes `ActiveStatus("No outstanding requests.")`, which is misleading.
- **Impact**: An operator with a broken bundle config gets no visible signal unless they check the log, and would otherwise wait up to ~5 minutes for `collect_unit_status` to catch it on the next cycle.
- **Fix**: Set `BlockedStatus("Invalid trusted certificate bundle configured")` directly in `_on_config_changed` before logging.
- **Linter rule**: "hook handler catches an exception from config access and logs a warning without setting a status" — mechanically checkable.

### `parse_ca_chain` silently accepts a single-element chain

- **Severity**: low
- **Kind**: bug
- **Where**: `src/helpers.py:44–51`
- **Evidence**: `parse_ca_chain` iterates `zip(chain, chain[1:])`. For a single-element chain, `chain[1:]` is empty, the loop body never runs, and the lone certificate is returned with no validation that the chain has at least two elements.
- **Impact**: If an operator passes only a leaf certificate as `ca-chain` (a plausible mistake), `provide-certificate` succeeds but the resulting chain has no CA — TLS clients may fail to verify it.
- **Fix**: Add `if len(chain) < 2: raise ValueError("CA chain must contain at least one CA certificate")`.
- **Linter rule**: "function iterates `zip(a, a[1:])` without checking for single-element input" — mechanically checkable.

### `_relation_id_parameter_valid` type annotation mismatch

- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:286`
- **Evidence**: The action schema declares `relation-id` as `integer`; `event.params.get("relation-id")` returns `None` or `int`, but the function signature annotates `relation_id: Optional[str]`. The membership check `relation_id not in requirer_relation_ids` happens to be safe at runtime because `int`/`str` comparisons are always `False`, but the annotation is misleading.
- **Impact**: A future change relying on the stated type could pass a string and silently get wrong behaviour.
- **Fix**: Change the annotation to `Optional[int]`.
- **Linter rule**: pyright would catch this if the charm libs were in the type-checked path; currently suppressed via `reportMissingImports`.

### `get-outstanding-certificate-requests` result is double-JSON-encoded

- **Severity**: low
- **Kind**: docs
- **Where**: `src/charm.py:153`
- **Evidence**: `event.set_results({"result": json.dumps([...])})` — the `result` field is itself a JSON string, requiring callers to `json.loads(results["result"])`.
- **Impact**: Operators scripting against the action output will be surprised by the double-encoding.
- **Fix**: Return structured fields directly (e.g. `event.set_results({"csrs": [...]})`) or document the encoding clearly in the README.
- **Linter rule**: not mechanically checkable.

### Unit tests require manual mocks for `tempo_coordinator_k8s` libraries

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py`
- **Evidence**: Importing `ManualTLSCertificatesCharm` pulls in `charms.tempo_coordinator_k8s.v0.charm_tracing` and `tracing`, which are not present in a plain dev environment. All 28 scenario tests only run once these are mocked; without mocks the test module fails to import.
- **Impact**: Local test runs are fragile for anyone who hasn't built the charm (which fetches these libs).
- **Fix**: Add a `conftest.py` that patches the `tempo_coordinator_k8s` imports, or declare the libs as test dependencies.
- **Linter rule**: not mechanically checkable.

### Charm library pins are behind the latest available

- **Severity**: low
- **Kind**: maintenance
- **Where**: `pyproject.toml` (`charmlibs-interfaces-tls-certificates ~= 1.8`), `deps/charmlibs/interfaces/certificate_transfer/_certificate_transfer.py` (bundled at v1.15/1.0.0 per `_version.py`)
- **Evidence**: `~=1.8` permits 1.8.x but not the current PyPI 1.10.0. The bundled `tls_certificates_interface` in rev 187 may predate a fix for the k8s crash above — unverified.
- **Impact**: Blocks picking up upstream fixes, possibly including one relevant to the critical k8s finding.
- **Fix**: Bump to `~=1.10` and re-verify k8s compatibility.
- **Linter rule**: not mechanically checkable.

## Worth copying

1. **Centralized `collect_unit_status`** (`src/charm.py:86–98`): aggregating all status logic in one place with explicit precedence is good practice worth copying elsewhere.
2. **Dedicated helper module** (`src/helpers.py`): PEM/CA-chain parsing is separated from charm logic, so both are independently testable.
3. **Explicit, actionable error messages for every action failure path**: e.g. "Certificate and CSR do not match.", "CSR was not found in any requirer databags.", "Multiple requirers with the same CSR found."
4. **`KeyError`/`ValueError` separation in `_get_trusted_certificate_bundle`**: two distinct exception types cleanly signal "not configured" vs "configured but invalid", enabling different status messages.
5. **Mock patches use full import paths** in unit tests (e.g. `"charmlibs.interfaces.tls_certificates.TLSCertificatesProvidesV4.get_outstanding_certificate_requests"`), avoiding accidental cross-talk.
6. **`TestCharm._encode_in_base64` / `_decode_from_base64` helpers**: keep test cases readable instead of burying logic in raw base64 strings.

## Common-practice notes

- **Charm type**: machine charm, built for `ubuntu@22.04` and `ubuntu@24.04`; CI builds amd64 and arm64.
- **Structure**: `src/charm.py` + `src/helpers.py`, no subpackage — simple and conventional.
- **Charm libs**: `tempo_coordinator_k8s.v0.charm_tracing` / `tracing` declared in `charmcraft.yaml` under `charm-libs` and fetched at build time rather than vendored — the modern pattern.
- **ops usage**: standard `CharmBase`, `CollectStatusEvent`, `ActionEvent`, `RelationJoinedEvent`. No `StoredState`, no Pebble, no containers — lean.
- **Config**: single optional item (`trusted-certificate-bundle`), no secrets.
- **CI**: shared workflows (`canonical/identity-credentials-workflows@v3.1.2`), separate amd64/arm64 build jobs, lint + static analysis + integration tests, quality gate blocks publish.
- **Terraform**: a `terraform/` module exists with inputs/outputs for the Juju provider; not exercised in CI.
- **Dependency updates**: Renovate bot in use.
- **Library versioning**: `charmlibs-interfaces-tls-certificates ~=1.8` vs PyPI 1.10.0 current; `deps/` pins `certificate_transfer` at v1.15.
- **Upgrade path**: no custom `upgrade-charm` handler; default ops behaviour observed during refresh test, nothing unusual.
- **Lifecycle hooks observed**: `install`, `start`, `leader-elected`, `config-changed`, `certificates-relation-{created,joined,changed,departed,broken}`, `trust_certificate-relation-joined`, `stop`, `remove` — all standard.
- **pydantic pin**: `pyproject.toml` pins pydantic exactly (2.13.4) alongside `charmlibs` deps that also depend on pydantic; the `IS_PYDANTIC_V1` guard in `certificate_transfer` handles both major versions at runtime, so the exact pin isn't strictly necessary.

## Tests

**Unit tests** (`tests/unit/`):
- `test_helpers.py`: 4 tests for `parse_pem_bundle`/`parse_ca_chain`; all pass.
- `test_charm.py`: 28 scenario tests; all pass, but only with manual mocks for `tempo_coordinator_k8s` (see finding above). Coverage gaps: no scenario test for a non-leader unit's `collect_unit_status` path; none exercise the real `tls_certificates_interface._configure()` method (it's mocked throughout); none exercise `provide-certificate` through the CLI/unit-agent/ops pipeline (scenario tests pass params as Python dicts directly).

**Integration tests** (`tests/integration/test_integration.py`): use `jubilant`, calling the Juju API directly rather than the `juju run` CLI path. Not run in this review (requires a built `.charm`). Should plausibly have caught the k8s crash but apparently do not exercise a live `update-status` cycle after a `tls-certificates` relation is established with enough delay.

**Linting**:
- `ruff check src/` — 0 errors, 0 warnings.
- `ruff format --check src/` — clean.
- `codespell src/` — 0 errors.
- `pyright src/` — 2 `reportMissingImports` errors for the build-time-fetched `tempo_coordinator_k8s` libs; false positives in a dev environment without a full build.

## Docs

- **README.md**: minimal, one paragraph plus links to charmhub docs and contributing guide; canonical docs live on Discourse.
- **CONTRIBUTING.md**: brief, points to Juju SDK docs — adequate.
- **SECURITY.md**: present, standard policy.
- **Terraform README**: good — input/output tables, usage example, requirements; covers both `certificates` and `trust_certificate` endpoints.
- **charmcraft.yaml description**: accurate one-liner.
- **Issue #527** ("Input validation for manual-tls-certificates"): matches the action-input bug observed in this review; unassigned, still open at review time.

## Open questions

1. Root cause of the k8s "permission denied" read of the provider's own relation databag — library bug, Juju k8s issue, or version-specific to the bundle in rev 187 (vs rev 108)?
2. Whether rev 458 on `1/edge` fixes the k8s crash — untested here (arm64-only build, amd64 test environment).
3. Why scenario tests never catch the crash: they mock the `tls_certificates_interface` methods at the boundary, so `_configure()`'s internal databag read is never exercised.
4. `certificate_transfer` integration is untested — no suitable requirer charm available; upstream integration tests use `any-charm` with injected source.
5. `tracing` integration is untested — no compatible tracing provider available for machine or k8s substrate in this environment.
6. The `tls-certificates-requirer` k8s secrets RBAC failure is a bug in that charm, not in `manual-tls-certificates`, and out of scope here.
7. Status-update latency (~5 minutes, tied to `update-status` interval) is expected Juju behaviour but is worth calling out in docs since it surprises operators watching for "outstanding requests" right after integrating.
