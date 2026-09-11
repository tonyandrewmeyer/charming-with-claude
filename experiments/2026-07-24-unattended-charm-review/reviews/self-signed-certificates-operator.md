# self-signed-certificates

A compact, well-maintained machine charm (`src/charm.py`, ~370-430 lines) that issues self-signed X.509 certificates over the `tls-certificates` interface, using modern charm libraries (`charmlibs.interfaces.tls_certificates`) and good patterns (centralized status via `collect_unit_status`, config-vs-certificate identity comparison, provider capabilities advertisement). It deployed cleanly on Juju 4.0.5/LXD and reached active/idle in ~2 minutes with no errors. It is not, however, in a state a maintainer should ship blind: `tox -e unit` and `tox -e static` both fail out of the box because charm libraries are never fetched locally, and there's a real security-relevant bug where `certificate-limit: 0` is silently treated as "unlimited" instead of "issue nothing." Fix the fetch-libs gap and the certificate-limit bug first; the rest is polish.

| | |
|---|---|
| Repo | canonical/self-signed-certificates-operator @ a7ae78d (2026-07-22) |
| Charms | self-signed-certificates |
| Substrate | machine (also deployable on k8s via Juju "charm" type) |
| Deployed | yes — concierge-lxd-4 (Juju 4.0.5), 1/stable rev 586 |
| Reviewed | 2026-07-24 |

## What it does

Generates a self-signed root CA certificate and stores it in a Juju secret. Listens on the `certificates` relation for CSRs from requirer charms, signs them with the CA, and returns the signed certificate plus chain. Also provides a `send-ca-cert` relation (via the `certificate_transfer` interface) to distribute the CA cert to charms that only need trust. Supports actions `get-ca-certificate`, `get-issued-certificates`, `rotate-private-key`, and has optional tracing integration via the `tracing` relation. Config options control CA certificate attributes (common name, organization, validity periods).

## Deployment log

```bash
# Juju 4.0.5, LXD machine substrate
juju add-model rv-ssc-lxd4 --controller concierge-lxd-4
juju switch concierge-lxd-4:rv-ssc-lxd4
juju deploy self-signed-certificates --channel 1/stable  # rev 586, ubuntu@24.04
# Active/idle in ~2 minutes (machine start ~30s, install hook ~3s)

# Actions
juju run self-signed-certificates/0 get-ca-certificate      # OK, returns PEM
juju run self-signed-certificates/0 get-issued-certificates # OK: "No certificates issued yet."

# Config change triggers CA regeneration (observed in debug-log)
juju config self-signed-certificates ca-common-name="test-ca-name"
# Log: "all_certificates_revoked" -> new CA generated with CN "test-ca-name"
# Two config-changed hooks fired (19:40:50 and 19:40:51) — secret_changed cascades

# Bad config -> BlockedStatus with clear message
juju config self-signed-certificates ca-common-name=""
# -> BlockedStatus: "The following configuration values are not valid: ['ca-common-name']"

# CA validity constraint enforced
juju config self-signed-certificates root-ca-validity="10d" certificate-validity="90d"
# -> BlockedStatus: "The following configuration values are not valid: ['certificate-validity', 'root-ca-validity']"
# (root-ca-validity must be >= 2x certificate-validity)

# Restore and test rotate action
juju config self-signed-certificates ca-common-name="restored-ca"
juju run self-signed-certificates/0 rotate-private-key  # OK, new key+cert generated

# File check on the machine
juju exec --unit self-signed-certificates/0 'cat /tmp/ca-cert.pem'  # CA cert written correctly
```

Not tested: certificate signing flow with a real requirer charm, `send-ca-cert` relation, tracing relation, and scale up/down — no suitable requirer/tracing charm was deployed alongside it. Model was torn down cleanly at the end.

## Observed behaviour

- **Startup time**: ~2 min from deploy to active/idle. Machine provision ~30s, charm install hook ~3s.
- **Double hook fire on config change**: Changing `ca-common-name` triggered **two** `config-changed`-equivalent runs of `_configure` within 1 second, because `_set_juju_secret` → `secret.set_content()` fires `secret_changed`, which is also observed by `_configure`. The second run is a no-op (cert already matches config) but still consumes resources. Visible in `debug-log` as two consecutive hook executions.
- **Noisy tracing warning**: Every hook emits `WARNING unit.self-signed-certificates/0.juju-log <class ...>._tracing_server_cert is None; sending traces over INSECURE connection` when no tracing relation exists, from the `@trace_charm` decorator.
- **CA cert written to `/tmp/ca-cert.pem`**: file owned by root, mode 0644, used only by the tracing integration.
- **Charm size**: deployed revision 586 is ~87MB on disk.
- **No workload process**: pure ops-framework charm, no long-running service — all work happens in hooks.

## Findings

### `certificate-limit: 0` silently treated as unlimited
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:133-137` (`_config_certificate_limit`), `src/charm.py:442` (`_process_outstanding_certificate_requests`)
- **Evidence**: `_config_certificate_limit` does `if not value or not isinstance(value, int): return None`. When `certificate-limit` is `0`, `not 0` is `True`, so the method returns `None`. Downstream, `if self._config_certificate_limit and self._config_certificate_limit > -1` evaluates `if None and ...` → `False`, so limiting is skipped entirely. An operator setting `juju config self-signed-certificates certificate-limit=0` expecting zero issuance instead gets unlimited issuance.
- **Impact**: Security-sensitive misconfiguration — a documented "stop issuing certificates" knob does the opposite of what's expected.
- **Fix**: Change the guard to `if value is None or not isinstance(value, int): return None`, or simply `if not isinstance(value, int): return None`.
- **Linter rule**: "`not <int>` guard that conflates 0 with None" — flag `if not <var>` where `<var>` is typed `int | None`.

### Unit tests and static analysis cannot run without pre-fetched charm libraries
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tox.ini` (unit/static environments), `src/charm.py:26-27`
- **Evidence**: `tox -e unit` fails with `ModuleNotFoundError: No module named 'charms'` (cannot import `charms.tempo_coordinator_k8s.v0.charm_tracing`). `tox -e static` (pyright) fails the same way. Charm libs for tracing are declared in `charmcraft.yaml` under `charm-libs` and fetched at build time, but never materialized into a `lib/` directory for local dev. Tox's `PYTHONPATH` includes `{tox_root}/lib`, but that directory doesn't exist. `tox -e lint` passes.
- **Impact**: Developers must know to run `charmcraft fetch-libs` (undocumented in CONTRIBUTING.md) before local unit/static checks work; CI integration tests become the first line of defense for issues unit tests should catch earlier.
- **Fix**: Add a `charmcraft fetch-libs` step in tox (pre-command or a `[testenv:fetch-libs]`) or in the `justfile`, and document it in CONTRIBUTING.md.
- **Linter rule**: "`tox -e unit` fails with `ModuleNotFoundError`" — mechanically checkable by running `tox -e unit` in CI.

### Double hook execution on every config change that updates secrets
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:70-72`, `src/charm.py:394-402`
- **Evidence**: Changing `ca-common-name` caused two `config-changed`-triggered runs of `_configure` within 1 second. The first run's `_generate_root_certificate` → `_set_juju_secret` → `secret.set_content()` fires `secret_changed`, which `_configure` also observes (line 72), so it runs again. The second run finds the cert already matches config and only re-runs `_send_ca_cert` / `_process_outstanding_certificate_requests`. This repeats for any event that modifies a secret.
- **Impact**: Wastes hook-runner time and widens the window for edge cases; churn compounds with multiple relations/units.
- **Fix**: Track a `_reconfiguring` flag, or compare content before calling `secret.set_content()` to avoid no-op updates; alternatively split `_configure` so the `secret_changed` path only runs secret-specific logic.
- **Linter rule**: "Event `secret_changed` and `config_changed` both observe a handler that calls `secret.set_content`" — partially mechanically checkable.

### `_set_juju_secret` orders `set_info` before `set_content`, risking partial state
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:394-402`
- **Evidence**: When updating an existing secret, the method calls `secret.set_info(expire=...)` (line 399) before `secret.set_content(content)` (line 400). If `set_content` raises, expiry has already changed but content hasn't, with no retry/rollback. In the CA renewal path (`_renew_root_certificate` → `_move_active_ca_cert_to_expiring`) this could leave the expiring CA secret with a new expiry but stale content.
- **Impact**: Unlikely but possible inconsistent secret state (new expiry, old content); low probability given the local secret backend, but the ordering is nonetheless wrong.
- **Fix**: Swap the order — update content first, then set expiry, so a failed content update leaves expiry unchanged.
- **Linter rule**: not mechanically checkable without flow analysis.

### `_parse_config_time_string` docstring says "y for years" but code handles "w" for weeks
- **Severity**: low
- **Kind**: docs
- **Where**: `src/charm.py:219-221` (docstring), `src/charm.py:224-232` (implementation)
- **Evidence**: Docstring says "m for minutes, h for hours, d for days or y for years"; implementation handles "m", "h", "d", "w" (weeks) — no "y". `charmcraft.yaml`'s config description correctly lists "m/h/d/w".
- **Impact**: A developer reading the docstring could assume year suffixes are supported; not operator-facing but a maintenance hazard.
- **Fix**: Change docstring to "m for minutes, h for hours, d for days or w for weeks."
- **Linter rule**: "Docstring lists parameter values that do not match implementation" — not easily mechanically checkable.

### `_push_ca_cert_to_container` uses "container" terminology but there is no container
- **Severity**: low
- **Kind**: ux
- **Where**: `src/constants.py:9`, `src/charm.py:424-428`
- **Evidence**: `CA_CERT_PATH = "/tmp/ca-cert.pem"` and the method `_push_ca_cert_to_container` write to local disk on a machine charm with no workload container (`charms.json` shows `"containers": []`).
- **Impact**: Naming confusion for developers — on k8s this would be a container push, but here it's a local file write.
- **Fix**: Rename to `_write_ca_cert_to_disk` or similar.
- **Linter rule**: not mechanically checkable.

### Tracing warning emitted on every hook when no tracing relation exists
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:26-27` (`@trace_charm` decorator)
- **Evidence**: Every hook (`install`, `leader-elected`, `config-changed`, `start`, etc.) logs `WARNING ... _tracing_server_cert is None; sending traces over INSECURE connection`, from `charms.tempo_coordinator_k8s.v0.charm_tracing`, even when no tracing relation is configured.
- **Impact**: Clutters logs for operators who don't use tracing; could mask real warnings.
- **Fix**: The tracing library should demote this to INFO/DEBUG when no tracing relation exists — arguably a library issue rather than a charm issue.
- **Linter rule**: not mechanically checkable at charm level.

### Terraform README describes Kubernetes but charm also works on machines
- **Severity**: low
- **Kind**: docs
- **Where**: `terraform/README.md`
- **Evidence**: README says "deployment onto any Kubernetes environment managed by Juju" and lists "A Kubernetes cluster" as a prerequisite, but the charm is `type: charm` (universal) and works on both LXD machines and Kubernetes.
- **Impact**: Terraform users on LXD/bare-metal might assume the module is k8s-only and skip it.
- **Fix**: Update to "any Juju-managed environment" and list "A cloud substrate (e.g., LXD or Kubernetes) managed by Juju" as a prerequisite.
- **Linter rule**: not mechanically checkable.

### `_send_ca_cert` creates a new `CertificateTransferProvides` instance on every call
- **Severity**: nit
- **Kind**: performance
- **Where**: `src/charm.py:340`
- **Evidence**: `certificate_transfer = CertificateTransferProvides(self, SEND_CA_CERT_REL_NAME)` is instantiated inside `_send_ca_cert`, called from `_configure` on multiple events (config_changed, secret_changed, update_status, relation events), creating a new object each time. By contrast `TLSCertificatesProvidesV4` is created once in `__init__` as `self.tls_certificates`.
- **Impact**: Minor overhead; inconsistent with how the primary TLS library is handled.
- **Fix**: Move `CertificateTransferProvides` into `__init__` as `self.certificate_transfer`.
- **Linter rule**: "Library wrapper instantiated in hook handler instead of `__init__`" — mechanically checkable.

## Worth copying

- **`_root_certificate_matches_config`** (`src/charm.py:404-420`): Compares every stored CA certificate attribute against current config rather than a "generation number" or "dirty flag," so the charm correctly regenerates the CA even when config is changed back to a previous value. Structural comparison, not historical — the right approach for a state-reconciling charm.
- **`_provider_capabilities`** (`src/charm.py:143-160`): Single source of truth for what the charm advertises over the `certificates` relation; its docstring (lines 147-153) explicitly says that capability flags and request filtering must be updated together if filtering is ever added. Worth other TLS provider charms adopting.
- **`_invalid_configs` as a gate in `_configure`** (`src/charm.py:377`): `_configure` returns early on invalid config, and `_on_collect_unit_status` sets BlockedStatus, so the charm stays in its last known good state rather than half-generating certificates.
- **`_limit_requests` using a generator** (`src/charm.py:449-458`): Counts requests per relation and yields only up to the configured limit — clean, memory-efficient pattern.
- **Scenario-based unit tests** (`tests/unit/test_charm_configure.py`): Uses ops-scenario to simulate state transitions without a live Juju, verifying secret content, expiry, and relation data at the `State` level — the right approach for ops-framework charms.
- **Clean `charmcraft.yaml` structure**: metadata centralized in one file, charm-libs declared with version pins, config options documented including side effects of changing them. Good model for other charms.

## Common-practice notes

- **Follows convention**: `ops >= 3.6.0`, `charmlibs.interfaces.tls_certificates`, `collect_unit_status`, `charm-libs` section in `charmcraft.yaml` — all current ecosystem best practice.
- **Drifts from convention**: no `lib/` directory committed; most charms commit library dependencies under `lib/charms/...`. This charm relies on `charm-libs` in `charmcraft.yaml` fetched at build time (commit 98af0fd, "Migrate libs to the ones managed by charmcraft and pypi") — a valid choice, but it breaks local `tox` runs as noted above.
- **Leads convention on testing**: uses `jubilant` for integration tests instead of `pytest-operator`, giving a programmatic API instead of shelling out to the `juju` CLI. Integration tests also exercise certificate expiry with real `time.sleep(60)`/`time.sleep(120)` waits — unusual and valuable, though it makes the suite slow (3+ minutes of sleeping alone).
- **CI uses `continue-on-error` for Juju 4**: the integration test workflow sets `continue-on-error: ${{ matrix.juju-version == '4.0/stable' }}` (integration-test.yaml:23), citing instability. Open issue #591 attributes this to a Juju bug (juju/juju#22485) — acknowledged, tracked technical debt.
- **Secret label naming**: `CA_CERTIFICATES_SECRET_LABEL = "active-ca-certificates"` (`constants.py:6`). Open issue #335 describes a historical problem where a secret labeled "ca-certificates" got into a partially-created state; the rename to "active-ca-certificates" may be a fix, but this is unverified and worth confirming with the issue author.

## Tests

| Type | Framework | Status |
|---|---|---|
| Unit | ops-scenario (pytest) | **6 files, all fail to import** — `ModuleNotFoundError: No module named 'charms'` |
| Integration | jubilant | **Cannot run locally** without a Juju controller + built charm |
| Lint | ruff + codespell | **Passes** (`tox -e lint`: all checks passed) |
| Static | pyright | **Fails** — same import error as unit tests |

**Unit test coverage** (read, not executed, due to the import failure):
- `test_charm_configure.py`: config-changed → CA generation, secret storage, certificate revocation on config change, config mismatch triggers regeneration, CA expiry + renewal, certificate generation for outstanding CSRs, certificate limit enforcement, certificate transfer on send-ca-cert relations. Good happy-path coverage.
- `test_charm_collect_status.py`: invalid config → BlockedStatus, valid config → ActiveStatus, non-leader status. Good coverage.
- `test_charm_capabilities.py`: full capabilities advertised on leader, none on non-leader. Good.
- `test_charm_get_ca_certificate.py`, `test_charm_get_issued_certificates.py`, `test_charm_rotate_private_key.py`: action tests, not read in detail but likely cover action paths.

**Missing test coverage**:
- `_set_juju_secret` failure path (`SecretNotFoundError` handling)
- `_configure` on `secret_expired` event (skipped via `@pytest.mark.skip`, ops bug #1316)
- `_send_ca_cert` called with explicit `rel_id`
- Behaviour when `generate_ca`/`generate_certificate` raises
- `_parse_config_time_string` error path (malformed strings)
- Non-leader `_configure` early return
- `_is_ca_cert_active` with timezone-aware vs naive datetimes (both branches exist, neither has an explicit test)

**Integration tests**: deploy → active, relation → certificate provisioned, config change → new certificate, certificate expiry → renewal, CA expiry → new CA, scale up → no crash. Expiry tests use real `time.sleep(60)`/`time.sleep(120)` waits — thorough but slow.

## Docs

- **README.md**: brief, links to charmhub docs; doesn't stand alone.
- **docs/index.md**: detailed but says "deploying it to the local MicroK8s," implying k8s-only when the charm supports both machine and k8s. Its note that "scale up operation is not supported yet" is accurate — the charm blocks non-leader units with a clear message.
- **charmcraft.yaml config descriptions**: excellent — each option explains format and side effects (e.g., "Changing this value will trigger generation of a new CA certificate, revoking all previously issued certificates.").
- **terraform/README.md**: good module documentation but implies k8s-only, same issue as docs/index.md.
- **CONTRIBUTING.md**: standard Canonical template; doesn't mention the need to run `charmcraft fetch-libs` before `tox -e unit`.
- No mismatch found between charmhub page and observed deployed behaviour.

## Open questions

1. **Issue #335 — partially created secret**: describes a secret labeled "ca-certificates" getting into a partially-created state; current code uses label "active-ca-certificates". Unclear whether the rename fixed the issue or whether it persisted across the rename — issue is still open, root cause unconfirmed without reproduction.
2. **Issue #591 — Juju 4 integration test failure**: `continue-on-error`, tied to a Juju bug (juju/juju#22485). Would be resolved by retesting once the upstream bug is fixed.
3. **Missing `lib/` directory**: is the intent to eventually publish charm tracing libraries to PyPI (so `uv sync` resolves them), or should tox environments add a `charmcraft fetch-libs` step? Current state is in-between — `charm-libs` in `charmcraft.yaml` works for builds but not local dev.
