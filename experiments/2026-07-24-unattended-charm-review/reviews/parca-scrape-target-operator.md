# parca-scrape-target

A workloadless machine charm that bridges external (non-Juju) profiling endpoints into the
Canonical Observability Stack via the `parca_scrape` interface. Configured with external
`host:port` targets, it exposes them to a `parca` or `parca-k8s` charm over the
`profiling-endpoint` relation. The charm's own code is lean (~218 lines) and well-structured;
almost all of the significant bugs live in the shared library it wraps
(`lib/charms/parca_k8s/v0/parca_scrape.py`).

The library conflates two roles: a charm that *exposes* its own profiling endpoint (which has a
unit-level address to publish) and a charm that only *references* external endpoints (which has
none). `parca-scrape-target` is the second kind, but the library was built for the first, and
that mismatch produces several confirmed failure modes — most importantly, a `Blocked`
`parca-scrape-target` still publishes a `DEFAULT_JOB` that makes `parca` scrape a non-resolving
machine hostname. On top of that, `collect_unit_status` shows only the first of several
simultaneous configuration errors, and forcible removal of the related `parca` application
(`--force`) puts the charm into a permanent error state on Juju 4.0.12 (recoverable on Juju
3.6.27). A maintainer should fix the `DEFAULT_JOB`/hostname-publishing pair first — it silently
poisons scrape data even when the charm is doing exactly what it was told (nothing) — then
address the `--force` crash and the status-aggregation bug.

| | |
|---|---|
| Repo | canonical/parca-scrape-target-operator @ `7924b82` (2026-06-30) |
| Charms | parca-scrape-target |
| Substrate | machine |
| Deployed | yes — `concierge-lxd-4` rev 87, `concierge-lxd` rev 87, `rv-force-remove`/`rv-parca-juju3` (concierge-lxd) rev 87 |
| Reviewed | 2026-08-26 |

## What it does

The charm reads `targets`, `scheme`, `tls_ca_cert`, `tls_server_name`, and
`tls_insecure_skip_verify` from Juju config, builds a Parca scrape job, and publishes it to the
`profiling-endpoint` relation via `charms.parca_k8s.v0.parca_scrape`. No targets configured →
`Blocked`; valid targets → `Active`. No workload runs on the machine — the charm is purely a
configuration bridge.

## Deployment log

**Juju 3.6 / concierge-lxd (model: `rv-parca-juju3`):**
```
juju deploy parca-scrape-target --channel 3.0/stable --base ubuntu@24.04
# Machine provisioned in ~5 min, charm went Blocked (no targets)
juju deploy parca --channel latest/edge --base ubuntu@22.04
# parca machine provisioned (~5 min), Active
juju relate parca-scrape-target parca
# Relation created, parca-scrape-target stays Blocked, parca stays Active
# juju show-unit parca/0:
#   scrape_jobs: [{"static_configs": [{"targets": ["*:80"]}]}]  <- DEFAULT_JOB
#   parca_scrape_unit_address: juju-306d47-0.lxd                <- machine hostname
#   parca_scrape_unit_name: parca-scrape-target/0

# Bad config injection
juju config parca-scrape-target scheme="httpz" targets="10.5.87.24:7070"
-> Blocked ("Invalid `scheme` provided.") -- correct, no traceback
juju config parca-scrape-target scheme="https" tls_ca_cert="not-a-cert"
-> Blocked ("Invalid certificate provided for `tls_ca_cert`.") -- correct, no traceback
juju config parca-scrape-target scheme="" targets="10.5.87.24:7070"
-> Blocked ("Invalid `scheme` provided.") -- correct

# Relation removal
juju remove-relation parca-scrape-target parca
-> parca-scrape-target stays Blocked, parca stays Active -- both handle correctly

# Multi-blocker injections (status shows only the first error)
juju config parca-scrape-target targets="" scheme="httpz"
-> Blocked "No targets specified." (hides scheme error)
juju config parca-scrape-target targets="invalid" scheme="ftp"
-> Blocked "Targets config invalid. See logs for more." (hides scheme error)
juju config parca-scrape-target targets="invalid" scheme="ftp" tls_ca_cert="x"
-> Blocked "Invalid `scheme` provided." (hides targets and CA errors)

# Scale-up
juju add-unit parca-scrape-target
-> Machine 2 provisioned (~4 min), both units go Blocked; unit 2 publishes juju-306d47-2.lxd

# Scale-down
echo "y" | juju remove-unit parca-scrape-target/0
-> parca-scrape-target -> unknown at scale 0; machine 0 destroyed; parca unaffected

# remove-application (no --force)
echo "y" | juju remove-application parca-scrape-target
-> Unit removed, machine destroyed, parca stays Active

# Actions
juju actions parca-scrape-target -> {}  (empty, confirmed)
```

**Juju 4 / concierge-lxd-4**: Earlier run confirmed identical behaviour (same hook sequence, same
relation data, same status messages), except forcible relation removal (see below).

**juju refresh**: `juju refresh parca-scrape-target --channel 3.0/edge` -> "already up-to-date".
No newer revision exists in any 3.0 channel.

**Force-removal, round 1 (Juju 4.0.12, `rv-parca-scrape-target`):** `juju remove-application
parca --force` leaves both `parca-scrape-target` units in permanent `error` with `hook failed:
"config-changed"` (traceback below, under Findings). `juju resolved` does not clear it.

**Force-removal, round 2 (Juju 3.6.27, `rv-force-remove`):**
```
juju remove-application parca --force
21:57:06 INFO profiling-endpoint-relation-departed
21:57:07 INFO profiling-endpoint-relation-broken
21:57:07 INFO unknown relation 0 resolving next op (x2)
-> parca-scrape-target stays Active, no crash
-> Subsequent juju config -> config_changed succeeds
-> Machine 1 destroyed cleanly
```

**Juju 3.6 vs 4.0 conclusion**: the permanent-error crash on forcible removal occurs only on Juju
4.0.12; on Juju 3.6.27 `relation-broken` fires and the unit recovers. Non-force removal works
correctly on both versions.

## Observed behaviour

### Lifecycle (correct)
- Deploy with no config → `Blocked` with actionable message.
- Set valid `targets` → `Active` after next `update_status` (~5 min).
- Relation joined → relation data published immediately (`relation_joined` hook fires).
- `juju remove-relation` → charm stays `Blocked` (no relation required); `parca` stays `Active`.
- `juju remove-application parca` (no `--force`) → relation-broken hooks fire cleanly; relation
  removed from model; `parca-scrape-target` stays `Active` (still has valid targets); subsequent
  `config_changed` succeeds.
- Scale up/down → works correctly; machine destroyed on scale-down.
- `juju remove-application parca-scrape-target` → clean teardown; `parca` unaffected.
- Invalid scheme / invalid CA cert / explicit empty scheme → `Blocked` with specific message, no
  traceback.
- Recovery after fixing config: status corrects on next `update_status` (~5 min).

### grpcurl confirmation of DEFAULT_JOB and hostname issues
Direct inspection of parca's scrape API (`grpcurl -plaintext 10.5.87.43:7070
parca.scrape.v1alpha1.ScrapeService/Targets`) confirms the relation-data findings:
- When `parca-scrape-target` is `Blocked` (targets cleared), parca receives
  `http://juju-306d47-3.lxd:80/debug/pprof/...` with `HEALTH_BAD` — the hostname does not
  resolve.
- With invalid targets `foo:1234` set, parca receives both hostname-based `DEFAULT_JOB` targets
  and `foo:1234`-based targets (both `HEALTH_BAD`).
- The `juju_unit` label on hostname-based targets is `parca-scrape-target/2`, confirming these
  are not parca's own self-profiling job.
- The `scheme` field is preserved in scrape jobs (`scheme` is in `ALLOWED_KEYS`,
  `parca_scrape.py:199`).

### Status update lag
`config_changed` fires on `juju config`, and relation data is updated within ~20s (confirmed by
grpcurl). But `collect_unit_status` only runs on `update_status` (default interval 5 min), so
unit status can lag the relation data by up to 5 minutes. `_set_unit_ip` is driven by the
library's `refresh_event`, which for a machine charm without containers is `update_status`
(`parca_scrape.py:748`). The exact mechanism by which relation data updates faster than the
observed hooks (`relation_joined`, `relation_changed`, `upgrade_charm`, `leader_elected`) is
unclear — `config_changed` is not among the events the library observes for
`_publish_all_relation_data` (unverified — the update path was not fully traced).

### Hook activity
```
unit-parca-scrape-target-1: install
unit-parca-scrape-target-1: leader-elected
unit-parca-scrape-target-1: config-changed
unit-parca-scrape-target-1: start
unit-parca-scrape-target-1: profiling-endpoint-relation-created
unit-parca-scrape-target-1: profiling-endpoint-relation-joined
unit-parca-scrape-target-1: profiling-endpoint-relation-changed
unit-parca-scrape-target-1: update-status   (fires ~every 5 min)
```
`upgrade_charm` correctly triggers `_publish_all_relation_data` via the library's observer
(`parca_scrape.py:757`).

## Findings

### Blocked charm still publishes DEFAULT_JOB with unreachable scrape targets
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:69`, `lib/charms/parca_k8s/v0/parca_scrape.py:838`
- **Evidence**: with `targets=""`, `_scrape_jobs` in the charm returns `None`
  (`src/charm.py:69`). The library's `_scrape_jobs` property returns `[DEFAULT_JOB]` whenever
  `self._jobs` is falsy (`parca_scrape.py:838`). Confirmed via grpcurl against parca's scrape API
  while `parca-scrape-target` was `Blocked`: parca receives
  `http://juju-306d47-3.lxd:80/debug/pprof/...` with `HEALTH_BAD` — the hostname does not
  resolve. `parca` stays `Active` throughout. The unit test
  `test_charm_removes_job_when_empty_targets_are_specified` explicitly asserts `scrape_jobs ==
  DEFAULT_JOB` after targets become empty, documenting the buggy contract rather than catching it.
- **Impact**: a `Blocked` charm — the operator's explicit signal that nothing should be
  scraped — still poisons the profiling pipeline. Parca scrapes an unreachable hostname tagged
  with the `parca-scrape-target` topology labels, and the operator has no indication this is
  happening.
- **Fix**: pass `[]` (not `None`) from `ParcaScrapeTargetCharm._scrape_jobs` when there are no
  targets, and have the library return `[]` (not `DEFAULT_JOB`) when `self._jobs` is empty. The
  library change is a breaking change for other `parca_scrape` consumers and needs a LIBPATCH
  bump.
- **Linter rule**: not mechanically checkable without a schema for what jobs this charm role
  should publish.

### Forcible relation removal causes permanent error on Juju 4.0.12
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/parca_k8s/v0/parca_scrape.py:798` (`_set_unit_ip`)
- **Evidence**: `juju remove-application parca --force` on Juju 4.0.12 (model
  `rv-parca-scrape-target`) puts both `parca-scrape-target` units into `error` with `hook
  failed: "config-changed"`, permanently:
  ```
  File "parca_scrape.py", line 798, in _set_unit_ip
      relation.data[self._charm.unit]["parca_scrape_unit_address"] = socket.getfqdn()
  File "ops/model.py", line 2148, in __setitem__
      self.update({key: value})
  File "ops/model.py", line 2188, in update
      if (key not in self and val != '') or (key in self and val != self[key])
  File "ops/model.py", line 888, in _data
      data = self._lazy_data = self._load()
  File "ops/model.py", line 2050, in _load
      return self._backend.relation_get(self.relation.id, ...)
  ops.model.ModelError: ERROR permission denied
  ```
  `--force` deletes the remote app's relation data without firing `relation-broken`. The relation
  metadata persists in `model.relations` while the data is gone; the next `config_changed` calls
  `_set_unit_ip`, which reads the (now-inaccessible) databag and raises. `juju resolved` does not
  break the cycle — confirmed no recovery path short of destroying the model. On Juju 3.6.27
  (`rv-force-remove`), `relation-broken` fires successfully instead and the unit stays `Active`;
  non-force removal works cleanly on both versions.
- **Impact**: any operator who force-removes the related `parca`/`parca-k8s` application on Juju
  4.0.12 loses the `parca-scrape-target` unit permanently.
- **Fix**: wrap the databag read/write in `_set_unit_ip` with a `try/except ops.model.ModelError`
  guard, or have `ProfilingEndpointProvider` observe `relation_broken`/`relation_departed` to
  detect and skip broken relations before writing.
- **Linter rule**: "relation databag write not guarded against ModelError" — checkable.

### Library publishes machine hostname, not IP address, as unit scrape address
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/parca_k8s/v0/parca_scrape.py:798`
- **Evidence**: `_set_unit_ip` unconditionally sets `parca_scrape_unit_address =
  socket.getfqdn()`. On a machine charm this is the machine hostname (`juju-306d47-3.lxd`),
  confirmed unresolvable by grpcurl (`HEALTH_BAD` targets). The library has
  `_is_valid_unit_address()` (`parca_scrape.py:803`), which validates via
  `ipaddress.ip_address()`, but it is never called anywhere in the codebase.
- **Impact**: the library's stated purpose is to publish "the unit host address ... for the
  Parca charm" — a hostname is not guaranteed routable across containers/machines. Any consumer
  charm on a substrate where hostname ≠ routable address hits the same failure.
- **Fix**: resolve to an IP (e.g. `socket.gethostbyname(socket.getfqdn())`) or source the address
  from Juju's bind-address data; alternatively call `_is_valid_unit_address` in `_relation_hosts`
  and log a warning when it fails.
- **Linter rule**: "`socket.getfqdn()` used as a unit address without IP validation" — checkable.

### Invalid targets from any provider crash the downstream `parca` charm
- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/parca_k8s/v0/parca_scrape.py:558`
- **Evidence**: `host, port = target.split(":")` in `_labeled_static_job_config` — a target
  without a colon (e.g. `"invalid-target"`) raises `ValueError: not enough values to unpack`,
  uncaught, in the `profiling-endpoint-relation-changed` hook of the *consuming* `parca` charm,
  which then goes to `error` and retries indefinitely. `parca-scrape-target` itself validates
  targets before publishing, so this cannot be triggered from this charm alone, but the library
  provides no such guard for other `parca_scrape` providers.
- **Impact**: a misconfigured target on any `parca_scrape` provider charm (not just this one) can
  take the entire `parca` charm into error.
- **Fix**: validate each target string in the library before splitting — require at least one
  colon and reject or skip malformed entries with a log message rather than raising.
- **Linter rule**: "target string from relation data is split without checking for a colon" —
  checkable.

### `_labeled_static_job_config` crashes on IPv6 targets
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/parca_k8s/v0/parca_scrape.py:558`
- **Evidence**: `host, port = target.split(":")` on an IPv6 target like `[::1]:8080` splits into
  more than two parts, so the unpack fails and/or `port` fails an integer cast. Confirmed by code
  inspection; not exercised in a live deployment. The same target-validation fix as above also
  covers this.
- **Impact**: IPv6 addresses cannot be used as scrape targets.
- **Fix**: parse targets with a dedicated parser (e.g. `urllib.parse.urlparse` with a scheme
  prefix) that handles bracketed IPv6 literals.
- **Linter rule**: "`target.split(':')` used for host:port parsing is not IPv6-safe" —
  checkable.

### `collect_unit_status` hides all but the first `BlockedStatus`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:192-213`
- **Evidence**: `_on_collect_unit_status` calls `event.add_status()` up to four times with
  different `BlockedStatus` messages before a final `ActiveStatus()`; each call replaces the
  previous, so only the first true condition is visible. Confirmed by injection: `targets=""
  scheme="httpz"` → shows only `"No targets specified."`; `targets="invalid" scheme="ftp"` →
  shows only `"Targets config invalid. See logs for more."`; `targets="invalid" scheme="ftp"
  tls_ca_cert="x"` → shows only `"Invalid \`scheme\` provided."`. Priority order observed:
  `no_targets` → `targets_invalid` → `scheme` → `CA`.
- **Impact**: operators fixing configuration must iterate one error at a time, each fix costing
  an `update_status` wait (~5 min) to reveal the next hidden error.
- **Fix**: aggregate all failing checks into one `BlockedStatus` message, e.g.:
  ```python
  blockers = []
  if no_targets: blockers.append("No targets specified...")
  if targets_invalid: blockers.append("Targets config invalid...")
  if not self._is_scheme_valid(): blockers.append("Invalid scheme...")
  if not self._is_tls_ca_valid(): blockers.append("Invalid certificate...")
  if blockers:
      event.add_status(ops.BlockedStatus("; ".join(blockers)))
  else:
      event.add_status(ops.ActiveStatus())
  ```
- **Linter rule**: "multiple `add_status` calls in `collect_unit_status` without aggregation" —
  checkable by static analysis.

### Library silently drops units with a missing address; validator is dead code
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/parca_k8s/v0/parca_scrape.py:798` (and `:803`)
- **Evidence**: `if unit_name and unit_address: hosts.update({unit_name: unit_address})` — if
  either field is absent, the unit is silently dropped, with no log message.
  `_is_valid_unit_address()` (line 803), which checks via `ipaddress.ip_address()`, exists but is
  never called from any code path.
- **Impact**: a unit with a missing or hostname-only address disappears from scrape targets with
  no diagnostic trail.
- **Fix**: call `_is_valid_unit_address` on `unit_address` and log a warning when it fails; log
  when `unit_name`/`unit_address` are absent.
- **Linter rule**: "address from unit relation data used without validation" — checkable.

### `ProfilingEndpointProvider` does not observe `relation_departed`
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/parca_k8s/v0/parca_scrape.py:735-736`
- **Evidence**: the provider observes `relation_joined`, `relation_changed`, `upgrade_charm`, and
  `leader_elected` but never `relation_departed`. When a `parca-scrape-target` unit departs
  (e.g. scale-down), its unit relation data (`parca_scrape_unit_address`,
  `parca_scrape_unit_name`) remains in the databag indefinitely. The consumer
  (`ProfilingEndpointConsumer`) iterates `relation.units` (which excludes departed units) so
  `parca` does not attempt to scrape the stale entry directly, but the orphaned data persists.
- **Impact**: stale databag entries after scale-down are inconsistent with the live unit set and
  could confuse other consumers of the raw relation data.
- **Fix**: observe `relation_departed` and clear the departing unit's address/name from the
  databag.
- **Linter rule**: "unit relation data written without a `relation_departed` cleanup handler" —
  checkable.

### TLS config always sets `insecure_skip_verify: false`, even with no TLS options set
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:76`
- **Evidence**: `job["tls_config"] = self._tls_config` runs unconditionally whenever
  `scheme=="https"`, and `_tls_config` defaults to `{"insecure_skip_verify": False}`. Observed:
  `scheme="https"` with no other TLS options set → relation data published
  `{"tls_config": {"insecure_skip_verify": false}}`.
- **Impact**: omitting `tls_config` in Parca means "use system default TLS verification";
  explicitly publishing `insecure_skip_verify: false` instead forces certificate verification
  against system CAs, which can break scraping of targets with self-signed certificates the
  operator expected to be accepted.
- **Fix**: only include `tls_config` when at least one option differs from default: `if ca or
  server_name or tls_insecure_skip_verify: job["tls_config"] = tls_config`.
- **Linter rule**: not mechanically checkable without a schema for defaults.

### Unreachable targets are silently dropped and misreported as "no targets specified"
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:198`
- **Evidence**: `_load_and_validate_targets()` drops targets that pass format validation
  (`_validated_address()`) but are unreachable, without setting `targets_invalid`. Confirmed on
  `rv-parca-juju3`: `targets="10.5.87.216:7070"` pointed at a destroyed machine produced
  `_targets == []`, which then triggers `no_targets = True` in `collect_unit_status` and shows
  `"No targets specified."`, even though a target was explicitly configured.
- **Impact**: operators with an unreachable target (e.g. a destroyed VM) get a misleading message
  telling them to add targets they already have.
- **Fix**: raise `TargetValidationError` for unreachable targets so `targets_invalid` is set and
  the message becomes `"Targets config invalid. See logs for more."`, or track "explicitly
  provided but dropped" separately from "none provided".
- **Linter rule**: not mechanically checkable without a connectivity check.

### Library uses deprecated `meta.series` for k8s/machine detection
- **Severity**: medium
- **Kind**: lint
- **Where**: `lib/charms/parca_k8s/v0/parca_scrape.py:740`
- **Evidence**: `if "kubernetes" in self._charm.meta.series:` — `meta.series` was deprecated in
  favour of `meta.containers` as of Juju 2.9. For this charm `meta.series == ""`, so the check
  currently resolves correctly to the machine branch, but the mechanism is fragile.
- **Impact**: if `meta.series` support is removed from `ops`/Juju, k8s detection breaks silently
  for every consumer of this library, not just this charm.
- **Fix**: replace with `if self._charm.meta.containers: # k8s` / `else: # machine`.
- **Linter rule**: "`meta.series` usage" — checkable with `ruff` or a custom lint rule.

### `_scheme` config accessor bypasses default on explicit empty string
- **Severity**: nit
- **Kind**: bug
- **Where**: `src/charm.py:95`
- **Evidence**: `_scheme` computes `str(self.model.config.get("scheme", "http"))`. `juju config
  scheme=""` returns `""` rather than falling back to `"http"`, so `_is_scheme_valid()` correctly
  returns `False` and the unit blocks with `"Invalid \`scheme\` provided."` — the outcome is
  correct, but only by coincidence of the `str()` cast, not by design.
- **Impact**: low as-is; fragile if the intended semantics ("empty means default") were ever
  assumed elsewhere.
- **Fix**: `value = self.model.config.get("scheme"); return value if value else "http"`, made
  explicit.
- **Linter rule**: not mechanically checkable without knowing the intended semantics.

## Worth copying

- `collect_unit_status` messages that include the exact fixing CLI command
  (`juju config ...`) — excellent UX; every blocked charm should do this.
- `TypedDict` classes (`TLSConfig`, `ScrapeJobsConfig`) for scrape configuration shapes give
  self-documenting type safety.
- Config property accessors (`_scheme`, `_tls_ca_cert`, etc.) wrapping `model.config.get` — clean,
  testable pattern for defaults/coercion.
- `_validated_address` using `urlparse` for target validation is a solid, standard approach.
- The library uses `ops.Object` (not `ops.CharmBase`) for provider/consumer objects, keeping them
  decoupled from charm lifecycle.
- Integration tests make real HTTP requests against the Parca API rather than asserting only on
  `juju status` — the right standard, even though (see Tests) they don't check enough.
- Using `ops.CollectStatusEvent.add_status` rather than setting status directly in handlers is the
  correct pattern for multi-concern status charms — undermined here only by the overwrite bug
  above.

## Common-practice notes

- `assumes: juju >= 3.6` in `charmcraft.yaml`; tested on both Juju 3.6.27 and 4.0.12 with no
  behavioural differences except the force-removal crash.
- Workloadless on machine substrate — no containers, no Pebble, no systemd units; the charm's
  sole job is config → relation data.
- No actions defined (`juju actions parca-scrape-target` returns `{}`) — appropriate for a
  configuration-only charm.
- `lib/charms/parca_k8s/v0/parca_scrape` is at `LIBPATCH=6`, shared with `parca` and `parca-k8s`.
  It conflates "provider of a profiling endpoint" (needs a unit address) with "integrator of
  external targets" (doesn't) — the root cause of the hostname and `DEFAULT_JOB` issues.
- `cosl>=0.0.51` supplies `JujuTopology` for relation metadata.
- Uses `uv` for dependency management, `tox.ini` for CI; `ruff` and `pyright` both clean.
- `justfile` delegates to `charms.just`, the centralized CI blueprint from
  `canonical/observability`.

## Tests

**Unit tests (17 tests, all passed):**
```
$ PYTHONPATH=".:./lib:./src" python3 -m pytest tests/unit/test_charm.py -v
# 17/17 PASSED in 0.17s
```
Covers `test_charm_blocks_if_no_targets_specified`,
`test_charm_sets_relation_data_for_valid_targets` (4 cases),
`test_non_leader_does_not_modify_relation_data`, `test_charm_blocks_if_target_invalid` (3 cases),
`test_charm_blocks_if_scheme_invalid` (6 cases), `test_charm_blocks_if_ca_invalid` (2 cases),
`test_charm_removes_job_when_empty_targets_are_specified`.

**Linters (all passed):**
- `ruff check .` — 0 errors
- `ruff format --check .` — 0 errors (11 files)
- `PYTHONPATH=.:./lib:./src pyright src/charm.py lib/charms/parca_k8s/v0/parca_scrape.py` — 0
  errors, 0 warnings
- `codespell` — 0 errors

**Integration tests**: `tests/integration/test_charm.py` (machine `parca`) and
`tests/integration/test_tls.py` (k8s `parca-k8s`) use `jubilant` against a real Juju model.
`test_deploy` sets `targets="10.10.10.10:7070"` and only waits for `all_active`, never asserting
the scrape job is actually well-formed. `test_profiling_is_configured` checks only that the
`PARCA_TARGET` string appears in Parca's metrics response — it does not check for absence of
`DEFAULT_JOB`, correct address format, or unreachable-hostname handling. Not executed in this
review (`test_tls.py` requires a k8s cluster; the machine integration test does not assert scrape
target correctness even when run).

**Test gaps relative to the findings above:**
- `test_charm_removes_job_when_empty_targets_are_specified` documents the `DEFAULT_JOB` bug as
  expected behaviour rather than catching it — fixing the bug requires updating this test too.
- `_relation_hosts` silent-drop behaviour, hostname publishing, and dead `_is_valid_unit_address`
  are entirely untested in the library.
- No test exercises `collect_unit_status` with two or more simultaneous `BlockedStatus`
  conditions.
- No test covers the unreachable-targets → "no targets" misclassification.
- No test covers the missing `relation_departed` observer.
- No test covers IPv6 target parsing or the missing-colon crash in
  `_labeled_static_job_config`.
- The forcible-removal crash has no test — would require `juju remove-application --force`, which
  jubilant/spread-based harnesses don't support.
- `_set_unit_ip` writing to a broken relation would need `ops.testing` support for simulating
  broken relations, not currently exercised.

## Docs

- **README.md**: good overview and usage example, mentions the `parca_scrape` interface. Does not
  mention the ~5-minute status-update latency, that the relation should be set up before setting
  targets, or the always-set TLS behaviour.
- **CONTRIBUTING.md**: documents the tox/microk8s workflow; references Ubuntu 22.04 for microk8s
  while the charm itself targets 24.04 — minor drift.
- **charmcraft.yaml description**: most complete of the docs, links to Prometheus scrape-config
  docs for TLS options; no mention of status latency.
- No published docs on Charmhub discourse.
- No Terraform module exists for this charm.

## Open questions

1. Is the `DEFAULT_JOB` fallback intentional for integrator-style providers, or should the
   library return `[]` when passed no jobs? Settling this needs a maintainer decision, since a
   unit test currently encodes the former as correct.
2. Was `_is_valid_unit_address` meant to be wired into `_relation_hosts`? It exists but is dead
   code.
3. Should the library validate reachability of targets, or only format, given
   `_load_and_validate_targets` currently only checks format?
4. Should the library be tolerant of relations broken by `--force` (guard `ModelError`, or add a
   `relation_departed`/`relation_broken` observer)? Currently it crashes.
5. The exact mechanism by which relation data updates within ~20s of `juju config` despite
   `config_changed` not being an observed event for `_publish_all_relation_data` was not
   conclusively traced (unverified).
