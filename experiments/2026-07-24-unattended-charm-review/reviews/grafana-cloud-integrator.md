# grafana-cloud-integrator

A thin machine/k8s charm that translates Juju config (username, password, URL endpoints, TLS CA) into relation data on the `grafana-cloud-config` interface, acting as a configuration bridge between the `grafana-agent` subordinate and Grafana Cloud. It has no workload process. The code is small and readable, but has real correctness bugs: status precedence is wrong (a missing-credentials condition can hide a missing-outputs `BlockedStatus`), the provider library caches config at `__init__` and writes stale relation data for several seconds after a config change (confirmed live), `tls-ca` unconditionally overwrites the databag with an empty string when unset, and the provider library has zero tests — the one scenario test that could catch the stale-config bug gives a false negative because it recreates the charm on every event, unlike real Juju. A maintainer should fix the status-precedence bug and the stale-config caching first (both are user-visible and both stem from the same root cause: the provider reads config once in `__init__` instead of on each write), then add provider-library tests that use a persistent charm instance across events.

| | |
|---|---|
| Repo | canonical/grafana-cloud-integrator @ `bbf9604` (2026-06-30) |
| Charms | grafana-cloud-integrator |
| Substrate | machine (LXD) + k8s |
| Deployed | yes — `concierge-lxd-4` (3.0/edge rev 84) and `concierge-k8s-4` (3.0/edge rev 84) |
| Reviewed | 2026-08-25 |

## What it does

The charm provides `grafana-cloud-config`. Operators set `username`, `password`, and one or more of `prometheus-url`/`loki-url`/`tempo-url` (plus optional `tls-ca`). `collect_unit_status` reports `BlockedStatus` when no outputs are configured, `ActiveStatus` otherwise. On relation events it writes config to the relation app databag.

The intended consumer is the `grafana-agent` subordinate, which **requires** `grafana-cloud-config` (confirmed from `canonical/grafana-agent-operator`'s `charmcraft.yaml`, which sets `limit: 1`, `optional: true`). On k8s it runs as a subordinate in the same container-agent pod; on LXD, on the same machine. The relation established cleanly in testing on both substrates.

## Deployment log

### LXD (model `rv-gci-lxd`, controller `concierge-lxd-4`)

```
juju add-model rv-gci-lxd --controller concierge-lxd-4
juju deploy grafana-cloud-integrator --channel 3.0/edge --model rv-gci-lxd
# Machine provision: ~5 min to active (container → agent → install → status)
# First blocked: "No outputs configured"

juju config grafana-cloud-integrator prometheus-url=... loki-url=... username=... password=...
# active at ~+2 min — message "Traces disabled" (tempo-url not set)

# All URLs configured: active with " disabled" (leading space — bug)
# Empty credentials: still active — "username/password not configured."
# Both missing: active with "username/password not configured." (blocker hidden)
# Whitespace URLs ("   "): correctly treated as empty → BlockedStatus "No outputs configured"
# Bad/malformed URLs: accepted silently — no validation
# Recovery (set credentials back): active, correct message

juju integrate grafana-agent:grafana-cloud-config grafana-cloud-integrator:grafana-cloud-config
# Relation established; grafana-agent shows "blocked" (missing cos-agent, unrelated to this charm)

juju remove-relation grafana-agent:grafana-cloud-config grafana-cloud-integrator:grafana-cloud-config
# Hook log: grafana-cloud-config-relation-departed → grafana-cloud-config-relation-broken ✓

juju remove-application grafana-cloud-integrator
# Hook log: relation-departed → stop → remove → "unit shutting down" ✓
# Machines removed cleanly, no traceback
```

### k8s (model `rv-gci-k8s`, controller `concierge-k8s-4`)

```
juju add-model rv-gci-k8s k8s --controller concierge-k8s-4
juju deploy grafana-cloud-integrator --channel 3.0/edge --model rv-gci-k8s
# Pod up in ~15s, active in ~30s — same blocked status as LXD

# grafana-agent relation: established; grafana-agent shows "unknown" (subordinate waiting on cos-agent)
# Databag visible via `juju show-unit`

# Double config-changed hooks per config change (k8s only):
# 13:08:12 ran config-changed
# 13:08:13 ran config-changed
# Same pattern on every subsequent config change; not observed on LXD

# Stale-config bug — live confirmation:
juju config grafana-cloud-integrator tempo-url=UNIQUE-TEST-VALUE
# At 1s:  juju show-unit → relation databag still shows OLD value (tempo-new.example.com)
# At 10s: juju show-unit → relation databag shows NEW value (UNIQUE-TEST-VALUE)

# Scale up (add-unit): second unit's readiness probe fails HTTP 418 "unit removed"
# Scale to 1: unit-1 removed cleanly

# kubectl delete pod grafana-cloud-integrator-0 → pod respawns ~30s, charm active ~1min later; clean recovery

# Application removal: scales to 0, pods terminate cleanly
```

## Observed behaviour

- **Install/start**: LXD ~5 min (machine dominates); k8s ~30s.
- **Config change**: fires `config-changed`. Provider writes databag from stored (stale) values; confirmed live at 1s stale / 10s correct (see above).
- **Double config-changed on k8s**: every `juju config` fires two `config-changed` hooks ~1s apart; not seen on LXD. Likely a container-agent/CAAS provisioner quirk, not charm code.
- **Relation join**: fires `-relation-created`, `-relation-joined`, `-relation-changed`; provider writes databag immediately.
- **Relation leave**: fires `-relation-broken`; provider correctly no-ops (iterates an empty `model.relations[...]`).
- **No credentials**: `ActiveStatus("username/password not configured.")` on both substrates.
- **No outputs**: `BlockedStatus("No outputs configured")` — correct.
- **Both missing**: `ActiveStatus("username/password not configured.")` — credential check overwrites the blocked status (bug).
- **All outputs configured**: `ActiveStatus(" disabled")` — leading space from generator exhaustion.
- **Bad URLs**: accepted silently, no validation. Whitespace URLs correctly treated as empty in `collect_unit_status`.
- **tls-ca**: always written to databag, even empty, erasing any previous value. Confirmed on LXD.
- **Scale up/down (k8s)**: works; removed unit shows HTTP 418 on readiness probe while terminating (normal Juju behaviour).
- **Memory/CPU**: no workload; k8s pod ~50MB RAM, negligible CPU.
- **k8s vs LXD**: identical behaviour except the double config-changed on k8s.
- **k8s pod restart**: clean recovery, ~30s to respawn, ~1min to active.
- **grafana-agent relation**: functional on both substrates; grafana-agent shows `unknown` (k8s) / `blocked` (LXD) because it's waiting on a separate `cos-agent` relation, unrelated to this charm.
- **Application removal (LXD)**: clean teardown, no traceback, machines removed.
- **Application removal (k8s)**: scales to 0, pods terminate cleanly.
- **tox lint/static**: `ruff check src/ lib/ tests/` — all checks passed. `pyright src/ lib/` — 0 errors, 0 warnings.
- **tox unit**: 11/11 passed in 0.18s.
- **Integration tests**: do not run — `pytest-operator` fails with "juju server-version 4.0.12 not supported." Even if they ran, they only assert `status="active"` — no databag or behaviour assertions.
- **Actions**: `juju actions grafana-cloud-integrator` → "No actions defined."

## Findings

### Provider library caches config at `__init__` — writes stale relation data after config change (live confirmed)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:20-27`; `lib/charms/grafana_cloud_integrator/v0/cloud_config_provider.py:35-36`
- **Evidence**: `GrafanaCloudConfigProvider.__init__` stores `self._prometheus_url = prometheus_url` etc. from arguments passed once at charm `__init__` time (`src/charm.py:20-27` reads `self.config.get()` there). `_on_relation_changed` writes the stored instance vars, not fresh config. `collect_unit_status` (`src/charm.py:42-47`), by contrast, reads `self.config.get()` directly and always shows current values. Live confirmation on k8s: set `tempo-url=UNIQUE-TEST-VALUE`; at 1s the relation databag (via `juju show-unit`) still holds the old value; at 10s it holds the new value.
- **Impact**: A consumer charm reading the relation databag within ~10 seconds of a config change gets stale endpoints/credentials — e.g. grafana-agent could push telemetry to the wrong endpoint — and the operator cannot detect this from status, since status always shows current config.
- **Fix**: Have `_on_relation_changed` read `self._charm.config.get(...)` directly instead of the cached instance variables, eliminating the stale copy entirely.
- **Linter rule**: relation databag write uses charm config but config is not re-read after `config-changed` — checkable with dataflow analysis.

### Status precedence bug: credential-missing `ActiveStatus` overwrites `BlockedStatus`
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:47-54`
- **Evidence**: `collect_unit_status` calls `event.add_status` twice: first `ActiveStatus("username/password not configured.")` when credentials are missing, then `BlockedStatus("No outputs configured")` when no outputs are set. `ops`'s `add_status` is last-write-wins, but the credential check's `ActiveStatus` is observed to win in practice — confirmed live on both LXD and k8s: with no URLs and no credentials configured, the charm shows `active`, not `blocked`.
- **Impact**: On a fresh deploy with no config — the expected first-run state — the charm shows `active` with a misleading message, hiding the fact that it is not functional.
- **Fix**: Use an early return: check credentials first and `return` after adding `BlockedStatus`, or otherwise ensure only one status is added.
- **Linter rule**: multiple `add_status` calls in the same `collect_unit_status` handler without early return — checkable by counting `add_status` calls.

### No `BlockedStatus` when credentials are missing (tracked in issue #35)
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:47-49`
- **Evidence**: `if not (self.config.get("username", "") and self.config.get("password", "")): event.add_status(ActiveStatus("username/password not configured."))`, with a `# FIXME: should this be blocked in fact?` comment. Issue #35 tracks this as unresolved. Confirmed live on LXD: unset credentials with a URL configured → `active` with "username/password not configured."
- **Impact**: An operator who forgets credentials sees `active` and may not notice telemetry isn't shipping.
- **Fix**: Change to `BlockedStatus("Missing credentials: username and password are required")`.
- **Linter rule**: not mechanically checkable without semantic analysis (add_status(ActiveStatus) in a guard for missing required config).

### `tls-ca` always written to databag, including empty string
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/grafana_cloud_integrator/v0/cloud_config_provider.py:70`
- **Evidence**: `databag["tls-ca"] = self._charm.config.get("tls-ca", "")` has no guard, unlike the URL fields which are gated by `if self._tempo_url:` etc. Confirmed on LXD: setting `tls-ca` to a cert value, then `juju config grafana-cloud-integrator tls-ca=""`, overwrites the databag entry with an empty string.
- **Impact**: Silent data corruption — unsetting `tls-ca` erases any previously configured value and TLS verification on the consumer side stops working with no warning.
- **Fix**: Guard the write: `if (tls_ca := self._charm.config.get("tls-ca", "")): databag["tls-ca"] = tls_ca`.
- **Linter rule**: relation databag write without a corresponding is-set guard — checkable by flagging `databag[...] =` reads from config without an `if` guard.

### Generator exhaustion produces garbled " disabled" status message
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:53-54`
- **Evidence**: `elif any_unset := (k for k, v in output_configs.items() if not v): event.add_status(ActiveStatus(f"{', '.join(any_unset)} disabled"))`. When all outputs are configured the generator is empty, `', '.join([])` is `""`, giving the message `" disabled"` (leading space). Confirmed on both LXD and k8s when all three URLs are configured.
- **Impact**: Operator sees `active` with an unreadable " disabled" message and can't confirm the charm is fully configured.
- **Fix**: Build a list, not a generator, and handle the "all configured" case explicitly, e.g. emit `"Ready"` when the disabled list is empty.
- **Linter rule**: not mechanically checkable (generator expression used as boolean in conditional) without semantic analysis.

### Requirer library silently returns only the first relation's data
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/grafana_cloud_integrator/v0/cloud_config_requirer.py:167-170`
- **Evidence**: `_data` property iterates `self._charm.model.relations[self._relation_name]` and returns on the first match; `charmcraft.yaml` sets `optional: true` without a `limit`, so multiple simultaneous relations are permitted at the metadata level.
- **Impact**: A charm relating to multiple grafana-cloud-integrator instances (e.g. two Grafana Cloud accounts) would silently use only the first relation's data.
- **Fix**: Set `limit: 1` in the interface metadata, or aggregate data across all relations properly.
- **Linter rule**: relation iterator returns only first relation without limit enforcement — checkable by requiring `limit` in metadata for single-relation interfaces.

### Provider library (`GrafanaCloudConfigProvider`) has no tests
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `lib/charms/grafana_cloud_integrator/v0/cloud_config_provider.py` (whole file)
- **Evidence**: `tests/unit/test_grafana_cloud_integrator_lib.py` covers only `GrafanaCloudConfigRequirer`. Issue #16 explicitly notes the provider side has no dedicated tests. Its several branches (leader guard, relation loop, credential write, URL writes, tls-ca write) are untested.
- **Impact**: The stale-config, always-written-tls-ca, and always-true-credentials-guard bugs would all have been caught by a basic databag-content test.
- **Fix**: Add scenario tests asserting databag contents after relation creation, non-leader no-write behaviour, tls-ca omission when unset, and databag updates after config change.
- **Linter rule**: not mechanically checkable without coverage analysis (ops handler with side effects lacking a corresponding test).

### Scenario test gives a false negative on the stale-config bug
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_grafana_cloud_integrator_lib.py`
- **Evidence**: The scenario tests create a new charm instance on each `ctx.run()`, so `GrafanaCloudConfigProvider.__init__` always runs with the current config, masking the caching bug entirely. In real Juju the charm instance persists across hook invocations. A test that reuses one charm instance across `relation-changed` then `config-changed` reproduces the live-confirmed bug; the existing per-event-recreated test does not.
- **Impact**: Any future test relying on this pattern to "verify" config-change propagation will give a false pass.
- **Fix**: Add a test using a single charm instance across multiple events (or an integration test asserting databag contents after a config change).
- **Linter rule**: not mechanically checkable (scenario/Harness test recreates the charm instance between events being tested).

### Integration tests are too thin to be useful
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_charm.py`
- **Evidence**: Only deploys, sets config, waits for `status="active"`. No assertions on databag contents, message text, failure recovery, or relation to grafana-agent. Additionally fails to collect: `pytest-operator` reports the juju client library incompatible with the deployed server version 4.0.12.
- **Impact**: The test would pass even if the charm published wrong relation data or crashed on every hook.
- **Fix**: Add databag-content assertions and a `conftest.py` targeting the correct controller/juju version.
- **Linter rule**: not applicable.

### `if self._credentials:` is always true — dead code, causes empty credentials to be written
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/grafana_cloud_integrator/v0/cloud_config_provider.py:61`
- **Evidence**: `self._credentials` is a `Credentials` object with no `__bool__` override, so it is always truthy; a FIXME comment acknowledges this. Consequence: credentials are always written to the databag (including empty strings), while URL fields are properly guarded — an inconsistency.
- **Fix**: Replace with `if self._credentials.username and self._credentials.password:`, or remove the guard and always write.
- **Linter rule**: `if <object>` where the class has no `__bool__` is always true — checkable with pyright/ruff.

### `Credentials` class duplicated in provider and requirer libs
- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/grafana_cloud_integrator/v0/cloud_config_provider.py:13-16`; `lib/charms/grafana_cloud_integrator/v0/cloud_config_requirer.py:16-19`
- **Evidence**: Both files define an identical `class Credentials:`. Issue #35 tracks removing it.
- **Fix**: Remove the duplicate; use a plain tuple or pass username/password separately.
- **Linter rule**: duplicate class definition across library files — checkable with a custom lint.

### No URL validation before writing to relation databag
- **Severity**: low
- **Kind**: ux
- **Where**: `lib/charms/grafana_cloud_integrator/v0/cloud_config_provider.py:45-53`
- **Evidence**: URL strings are written to the databag with no validation; `prometheus-url="not-a-url"` was accepted silently in testing. Whitespace-only values are correctly treated as empty by `collect_unit_status`, but the raw config value would still be written to the databag if set to a non-whitespace invalid string.
- **Impact**: A typo in a URL is silently published to the relation; the consumer may fail confusingly.
- **Fix**: Validate with `urllib.parse.urlparse` and set `BlockedStatus` on invalid input.
- **Linter rule**: not mechanically checkable (config value used as URL without validation).

### Requirer `_data` property logs on every access
- **Severity**: low
- **Kind**: performance
- **Where**: `lib/charms/grafana_cloud_integrator/v0/cloud_config_requirer.py:168`
- **Evidence**: `logger.info("%s %s %s", relation, self._relation_name, relation.data[relation.app])` runs on every call to `_data`, which every public property (`loki_url`, `prometheus_url`, `credentials`, etc.) invokes.
- **Impact**: Any charm using the requirer floods its logs with relation data on every status evaluation.
- **Fix**: Remove, or downgrade to `logger.debug()`.
- **Linter rule**: not mechanically checkable (logger.info/warning/error inside a frequently-accessed property).

### `limit: 1` present in test metadata but not in `charmcraft.yaml`
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_grafana_cloud_integrator_lib.py:14` vs `charmcraft.yaml`
- **Evidence**: The test `Context` sets `"limit": 1` on the interface; the actual `charmcraft.yaml` does not, so the charm permits multiple simultaneous relations in practice while the tests assume single-relation behaviour. The multi-relation bug (above) cannot be reproduced by existing tests.
- **Fix**: Either add `limit: 1` to `charmcraft.yaml` if single-relation is intended, or update tests to cover multi-relation behaviour.
- **Linter rule**: test metadata `limit` does not match `charmcraft.yaml` `limit` — checkable by comparing the two files.

### `CloudConfigRevokedEvent` docstring is wrong
- **Severity**: low
- **Kind**: docs
- **Where**: `lib/charms/grafana_cloud_integrator/v0/cloud_config_requirer.py:34-36`
- **Evidence**: Docstring reads "Event emitted when cloud config is available." — a copy-paste error from `CloudConfigAvailableEvent`.
- **Fix**: Correct to "Event emitted when cloud config is revoked."
- **Linter rule**: not mechanically checkable (docstring text mismatch across event classes).

### Unit tests use deprecated `ops.testing.Harness`
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:20`
- **Evidence**: `self.harness = Harness(GrafanaCloudIntegratorCharm)`; pyright warns "Harness is deprecated."
- **Fix**: Migrate to `scenario.Context`, as already done in `test_grafana_cloud_integrator_lib.py`.
- **Linter rule**: use of deprecated `Harness` in test code — checkable by import.

### No idempotency in provider databag writes
- **Severity**: low
- **Kind**: performance
- **Where**: `lib/charms/grafana_cloud_integrator/v0/cloud_config_provider.py:42-70`
- **Evidence**: `_on_relation_changed` fires on `relation_joined`, `relation_created`, `relation_changed`, and `config_changed`, and unconditionally rewrites all fields even with no actual change.
- **Impact**: Wastes API calls and hook time, and causes unnecessary downstream `relation-changed` events. Minor given the small payload.
- **Fix**: Compare before writing, or hash the config and skip unchanged writes.
- **Linter rule**: not mechanically checkable (relation databag write without change detection in a hot-path handler).

### No `upgrade_charm` handler
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py` (no observer registered)
- **Evidence**: No `on_upgrade_charm` handler exists. Largely fine for a stateless charm today, but the charm is under active development (track 3.0, refactor planned per issue #35).
- **Fix**: Add an `on_upgrade_charm` handler as the charm gains state.
- **Linter rule**: not applicable.

### Double `config-changed` hook on k8s (substrate-specific, not charm code)
- **Severity**: low
- **Kind**: bug
- **Where**: container-agent / CAAS provisioner, not charm code
- **Evidence**: Every `juju config` on k8s triggers two `config-changed` hook invocations ~1 second apart (observed via `juju debug-log --include-module juju.worker.uniter`); not seen on LXD.
- **Impact**: Doubles `_on_relation_changed` work and databag writes per config change on k8s.
- **Fix**: Not charm-fixable; report as a Juju/container-agent issue if it causes problems downstream.
- **Linter rule**: not applicable.

## Worth copying

- `collect_unit_status` pattern (`src/charm.py`): using `ops.CollectStatusEvent` and separating status concerns from hook logic is the modern, clean approach.
- Early-return-on-no-outputs intent (`src/charm.py:38-47`): the intended priority order (blocked when no outputs) is correct in design, just undermined by the credential-check ordering bug above.
- Scenario tests (`tests/unit/test_grafana_cloud_integrator_lib.py`): clean use of `scenario.Context`/`State`/`Relation` with leadership parametrization — the right modern pattern, just incomplete (provider untested).
- CI delegated to `canonical/observability` reusable workflows — the right pattern for a charm in a shared org.
- Provider library is a proper `ops.framework.Object` subclass with correctly registered observers.
- Leader guard in the provider: correctly checks `is_leader()` before writing to the app databag, avoiding races with multiple units.

## Common-practice notes

- Deployed charm uses ops 3.7.1 (bundled by charmcraft); local dev uses ops 2.23.1 — the gap is why local `pytest-operator` is incompatible with the server.
- Lint/static: `ruff check` clean, `pyright` clean (0/0). `tox.ini` also runs a `git diff main` check that `LIBPATCH` was bumped.
- Unit tests: 11/11 pass in 0.18s; deprecation warning printed for `Harness`.
- Library versions: provider `LIBAPI=0, LIBPATCH=5`; requirer `LIBAPI=0, LIBPATCH=8`.
- k8s vs LXD parity: identical correctness behaviour; k8s deploys much faster (~30s vs ~5 min); only observed difference is the double `config-changed` on k8s.
- No workload: purely a config-bridge charm — no Pebble workload layer, no systemd units, no snaps.
- Config options are all plain strings with no validation or pattern enforcement.
- Interface: `grafana-cloud-config` provided here, required by `grafana-agent` (confirmed from grafana-agent's `charmcraft.yaml`); relation works on both substrates, though grafana-agent itself shows `unknown`/`blocked` pending its own `cos-agent` relation, unrelated to this charm.
- Databag key naming: config uses hyphens (`loki-url`), databag uses underscores (`loki_url`) — handled correctly.
- Application removal is clean on both substrates, with proper hook sequencing and no tracebacks.

## Tests

### Unit tests (runnable)
- `tests/unit/test_charm.py`: 7 Harness-based tests, all pass, but use deprecated `Harness`. Covers status-reporting paths (no URLs → blocked; various credential/URL combinations → active) but none check message text (e.g. the leading-space bug), status precedence, or databag contents.
- `tests/unit/test_grafana_cloud_integrator_lib.py`: 4 scenario-based tests, all pass, covering the requirer library only (relation-changed/broken, parametrized by leadership). Provider library has zero tests.

### Integration tests (not runnable)
- `tests/integration/test_charm.py`: fails to collect (juju client/server version mismatch). Even if it ran, only asserts `status="active"` — no databag, failure-recovery, or grafana-agent-relation assertions.

### Coverage gaps
- Provider library: zero tests.
- `collect_unit_status` message text: never asserted.
- Status precedence bug: not tested.
- `tls-ca` always-written behaviour: not tested.
- Databag contents after relation creation: never asserted.
- Stale-config propagation: scenario test gives a false negative; integration test doesn't check databag.
- Non-leader unit behaviour for the provider: not tested.
- URL validation: not tested (none exists).
- grafana-agent integration: not tested at all.

## Docs

- README.md: minimal — description, one-paragraph "Getting Started," a deploy command. No relation-interface explanation, no example databag, no troubleshooting, no example of relating to grafana-agent.
- CONTRIBUTING.md: very brief (~900 bytes), references Juju SDK docs.
- `charmcraft.yaml` `links` points to `https://discourse.charmhub.io/t/grafana-cloud-integrator-docs-index/14793` — unreachable during this review (unverified whether this is transient).
- No `terraform/` directory or Terraform reference in `charmcraft.yaml`.
- SECURITY.md: standard, points to GitHub security advisories.
- Library docstrings have no usage documentation (issue #15 tracks this); `CloudConfigRevokedEvent` docstring is wrong (see Findings).

## Open questions

1. Mechanism of the stale-config bug: confirmed by live testing (databag stale for ~10s after a config change), but the exact trigger for the eventual correct write is unclear — possibly a delayed container-agent restart. Monitoring the Pebble "Since" timestamp across a config change would help confirm this (unverified).
2. Whether removing the `Credentials` class (issue #35) is planned to resolve the always-true-guard and duplication issues as a side effect.
3. Whether the k8s double-`config-changed` behaviour is worth reporting upstream to Juju/container-agent maintainers.
4. LXD machine restart recovery: not tested in this review.
5. Track strategy: only track 3.0 has stable releases (tracks 1/2 exist with none); tied to a COS Lite 3.x dependency.
6. The linked Discourse docs page returned an error during this review; whether this is transient is unverified.
