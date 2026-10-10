# Working notes for opentelemetry-collector review
## 2026-08-09 (deepened, second pass)

### Key corrections from deepening

1. **Finding #1 CORRECTED**: The server CA cert IS written to disk, at `/usr/local/share/ca-certificates/juju_receive-ca-cert/cos-ca.crt` (defined as `SERVER_CA_CERT_PATH` in constants.py:12). The original review claimed `otelcol-server-ca.crt` was missing, but that file was never part of the design. TLS data reaches disk correctly (cert, key, CA cert all present). However, the `TLSCertificatesRequiresV4` GC issue is still real — cert renewal via `certificate_available` events is broken.

2. **Finding #2 UPDATED**: Stop hook traceback is Juju-version specific. On Juju 3.6, stop hook runs cleanly (confirmed during `remove-unit ubuntu/2` test). On Juju 4.x, `config-get` is unavailable during stop.

3. **New finding #4**: Scale-up snap-start failure loop. New subordinate units joining a machine that already has the snap installed hit repeated `snap start` failures (exit status 1). Unit enters error state permanently. Confirmed in rv-otel-d2: otelcol/4 failed 7+ times.

4. **New finding #7**: `queue_size`, `tracing_sampling_rate_*`, `max_elapsed_time_min` accept invalid values without validation. `queue_size=-10` and `tracing_sampling_rate_workload=200` were accepted.

5. **Updated status/precedence finding**: Confirmed the active→blocked(memory)→blocked(relations) sequence in status history on rv-otel-d2.

### Deployment rounds

#### Round 3 (rv-otel-d2, Juju 3.6): 3-unit scale test
- Deployed ubuntu ×3 + otelcol + self-signed-certificates
- All 3 units reached blocked state after ~120s
- Scale down (remove unit ubuntu/2): clean stop hook, no errors
- Scale up (add unit ubuntu): NEW UNIT otelcol/4 entered error state
- Snap start failure loop observed
- Remove-application: stuck due to error state, needed --force
- Model destroyed

### Config testing additions
- `always_enable_zipkin=true` → port 9411 opened ✓
- `tracing_sampling_rate_workload=200` → accepted without validation ✗
- `queue_size=-10` → accepted without validation ✗
- `processors=@file.yaml` → custom processors merged correctly ✓ (only works from $HOME, not /tmp — snap confinement)

### Code deep-dive

#### TLS cert flow (corrected understanding):
1. `receive_ca_cert()`: CertificateTransferRequires, writes trust CAs to `/usr/local/share/ca-certificates/juju_receive-ca-cert/{0,1,...}.crt`
2. `receive_server_cert()`: TLSCertificatesRequiresV4, writes:
   - Server cert → `/var/snap/.../otelcol-server-cert.crt` (SERVER_CERT_PATH)
   - Private key → `/var/snap/.../otelcol-private-key.key` (SERVER_CERT_PRIVATE_KEY_PATH)
   - Server CA → `/usr/local/share/ca-certificates/.../cos-ca.crt` (SERVER_CA_CERT_PATH)
3. `refresh_certs()`: runs `update-ca-certificates` which picks up all certs in trust store
4. Order in reconcile: receive_ca_cert FIRST (cleans + rewrites), receive_server_cert SECOND (writes cos-ca.crt), refresh_certs LAST

#### _Certificate model (tls_certificates.py:271-293):
```python
class _Certificate(pydantic.BaseModel):
    ca: str  # REQUIRED field
    certificate_signing_request: str
    certificate: str
    chain: Optional[List[str]] = None
    revoked: Optional[bool] = None
```
CA is always provided by self-signed-certificates in the `certificates` JSON array.

#### Snap start failure analysis:
Line 555 in charm.py: `self.snap("opentelemetry-collector").start()` is called unconditionally.
Intended to resume after CSR waiting state, but fires on every reconcile for every unit.
When a new subordinate joins a machine with the snap already running, this fails.

#### event() function (charm.py:126-133):
```python
def event() -> str:
    return os.environ.get("JUJU_HOOK_NAME") or os.environ.get("JUJU_ACTION_NAME", "")
```
Reads hook name from environment — no framework.observe() calls anywhere.

### Tests
- 171 passed, 1 skipped (test_https_endpoint_is_provided)
- 118 deprecation warnings
- PYTHONPATH=.:lib:src required for test discovery
- All tests use Scenario (ops.testing)
- No stop/remove hook tests in test_charm_lifecycle.py
- No TLS end-to-end test (all mocks)

### Static analysis
- Pyright: 0 errors, 0 warnings
- Ruff: All checks passed
- Codespell: configured

### Cleanup
- rv-otel-d2 destroyed (timed out, background cleanup)

## 2026-08-09 (deepened, third pass, ~60 min)

### Controller issues
- concierge-lxd controller became unresponsive after the first two deployment rounds
- Destroyed rv-otel-deep (stuck at pending machines) and rv-otel-f3
- All Juju Controllers timing out - both juju (4.0.12) and juju_3 (3.6.27) snaps
- Controller processes visible but API unreachable
- Pivoted to code-only review for the remainder

### New findings added to review (findings #13-#18):
13. mdadm.rules YAML syntax error (description on same line as summary closing quote) - silently drops RAID alerts
14. send_otlp double-OtlpRequirer (race between rules publish and endpoint retrieval)
15. send_profiles and receive_profiles GC pattern (same as #1, #3)
16. conftest autouse mocks hide real bugs (6 autouse fixtures masking critical code paths)
17. Juju 4.x LXD subordinate hang (renumbered from #13)
18. TLS tests mock entire library (renumbered from #14)

### Ruff findings corrected
- Earlier claim "All checks passed" was wrong - ran on full codebase found 11 RET505/RET502/RET507 issues in lib/charms/
- Pyright still clean: 0 errors, 0 warnings

### Tests run
- Unit tests: 171 passed, 1 skipped (same as before)
- Observed mdadm.rules ERROR and GC WARNING in test output
- pyright: 0 errors
- ruff: 11 violations (all in library code)

### Code reviewed this session
- snap_fstab.py: clean Fstab parser
- snap_management.py: SnapMap architecture-pinning, install logic
- utils.py: memory/CA hash helpers
- singleton_snap.py: clean file-based coordination
- deps/charmlibs/pathops: excellent path-abstraction library
- integrations.py: found OtlpRequirer ×2 and Profile GC issues
- conftest.py: documented 6 problematic autouse mocks
- test_removal_hooks.py: thorough integration tests asserting on disk state
- open-issues.txt: reviewed all 26 open issues, noted #79, #341, #236, #256, #365
