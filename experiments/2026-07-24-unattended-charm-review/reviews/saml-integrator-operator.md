# saml-integrator

A workloadless charm (machine + k8s) that fetches SAML IdP metadata from `metadata_url` or inline `metadata`, validates it (signature/fingerprint), and propagates `entity_id`, certificates, and SSO/SLO endpoints over a `saml` relation interface. The real logic lives in the `saml-integrator` PyPI package (`signxml` + `lxml` + `pydantic`).

Code quality is solid — 20/20 unit tests pass, `ruff`/`mypy`/`codespell` clean — but the charm has multiple correctness bugs that undermine its core job of reporting trustworthy status: a bad `metadata_url` is silently accepted while no relation exists, then crashes the hook (uncaught `CharmConfigInvalidError`) the moment a relation is created; a wrong `entity_id` is accepted with `ActiveStatus` while writing corrupt, certificate-less relation data that then crashes the requirer charm. The charm reports "fine" in exactly the scenarios where it is not. A maintainer should first fix the three uncaught-exception/silent-corruption paths (findings 1–3 below), then release a new stable channel — stable rev 66 is ~10 months behind edge.

| | |
|---|---|
| Repo | canonical/saml-integrator-operator @ `576c220` (2026-07-21) |
| Charms | saml-integrator (machine + k8s) |
| Substrate | machine + k8s (both tested) |
| Deployed | yes — concierge-lxd-4 (Juju 4.x, machine), concierge-k8s-4 (Juju 4.x, k8s), concierge-lxd (Juju 3.6, machine), concierge-k8s-3 (Juju 3.6, k8s); charmhub stable rev 66, refreshed to edge rev 168 on k8s-4 |
| Reviewed | 2026-09-02 |

## What it does

The charm fetches SAML IdP metadata from either `metadata_url` or inline `metadata`, validates it (signature + fingerprint if provided), extracts `entity_id`, X.509 certificates, and SSO/SLO endpoints from the XML, and writes them into the databag of every `saml` relation. It publishes `charms.saml_integrator.v0.saml` as a library for requirer charms. There is no workload container — pure Python running in the unit agent. The charm provides `saml` and requires nothing.

## Deployment log

### LXD (machine substrate, Juju 4.x)
```
juju add-model rv-saml-lxd4 --controller concierge-lxd-4
juju deploy saml-integrator --channel stable
# Machine 0 (juju-d1893c-0, LXD container) created, unit agents installed
# Initial status: blocked "invalid configuration: entity_id" (expected, no config set)

juju config saml-integrator entity_id="https://login.staging.ubuntu.com" \
  metadata_url="https://login.staging.ubuntu.com/saml/metadata"
# Config-changed hook fired after ~45s, status → active

juju add-unit saml-integrator  # unit/1
# unit/1: install+config-changed+start in ~6s total

# Deployed any-charm and related it
juju integrate any-charm:require-saml saml-integrator:saml
# Relation created successfully. Databag confirmed:
#   entity_id, metadata_url, x509certs, SSO/SLO URLs all present and correct.

# Failure injection: metadata_url=https://this-domain-does-not-exist-xyz789.com/metadata
# Status remained active! (bug — see Findings)
# Restored valid URL → active

# Failure injection: entity_id=https://WRONG-ENTITY-ID.example.com (with relation live)
# Status remained active! Relation databag had wrong entity_id + correct URLs.
# x509certs field was ABSENT from databag (silently dropped by Juju).
# Bug — see Findings.

juju scale-application saml-integrator --scale -1  # removed unit/1
# Scale down succeeded, machine 2 cleaned up.
```

**Hook timing (unit/0, cold start, Juju 4.x):**
| Hook | Wall clock |
|---|---|
| Unit agent start → install hook | ~12 s |
| install → leader-elected | 1 s |
| leader-elected → config-changed | <1 s |
| config-changed → start | 1 s |
| `juju config` → config-changed fires | ~45 s |
| install hook duration | ~1 s |

### LXD (machine substrate, Juju 3.6)
```
juju add-model rv-saml-lxd3 --controller concierge-lxd
juju deploy saml-integrator --channel latest/edge  # rev 168
# Machine provisioning took ~6-10 min (slower than Juju 4.x)
# Initial status: blocked "invalid configuration: entity_id"

juju config saml-integrator entity_id="https://login.staging.ubuntu.com" \
  metadata_url="https://login.staging.ubuntu.com/saml/metadata"
# config-changed fired ~1 min after config set (faster than k8s 4.x's ~34s)
# status → active

# Deployed any-charm (rev 175, beta) and related it
# relation-created hook: maintenance → active (correct)

# Failure injection: bad metadata_url with live relation
#   config-changed hook: maintenance "Configuring charm" → hook failed exit 1
#   Unit in error: "hook failed: config-changed"
#   Retry every ~10s (faster than k8s 4.x's ~30s)
# Restored URL → hook succeeded → active (auto-recovery confirmed)

# debug-log confirmed:
#   "awaiting error resolution for config-changed" every ~10s
#   "hook config-changed failed: exit status 1"
#   After fix: "ran config-changed hook"
```

### Kubernetes (k8s substrate, Juju 4.x)

**Initial deploy (rev 168, edge)**
```
juju add-model rv-saml-k8s4 --controller concierge-k8s-4
juju deploy saml-integrator --channel latest/edge
# Pod saml-integrator-0 created in rv-saml-k8s4 namespace
# Uses ghcr.io/juju/charm-base:ubuntu-22.04
# Pod starts in ~10s from deploy to active (vs ~13s machine)
# Initial status: blocked "invalid configuration: entity_id"

juju config saml-integrator entity_id="https://login.staging.ubuntu.com" \
  metadata_url="https://login.staging.ubuntu.com/saml/metadata"
# Config-changed fires ~34s after config set, status → active
```

**Refresh (stable rev 66 → edge rev 168)**
```
juju refresh saml-integrator --channel latest/edge
# old unit/0 (10.1.0.202) shut down at 01:09:06 (stop hook)
# new pod started at 01:09:09 (start hook)
# upgrade-charm + config-changed + start hooks ran successfully
# Status: maintenance → active through each hook
# Edge rev 168 has LIBPATCH=11, matching source
```

**Scale up/down (k8s)**
```
juju add-unit saml-integrator -n 2
# 3 units active in ~10s total (no OCI image to pull)
# Leader: unit/0. Non-leaders do not process relations.
juju scale-application saml-integrator 1
# Scaled back to 1 unit cleanly
```

**Failure injection: bad metadata_url with live relation (edge rev 168)**
```
juju config saml-integrator metadata_url=https://this-domain-does-not-exist-xyz999.com/metadata
# No relations: status stayed active (no-op in _update_relations)
# With live relation (any-charm integrated):
#   saml-relation-created hook fired on saml-integrator/0
#   Hook set MaintenanceStatus("Update integrations") then raised CharmConfigInvalidError
#   Hook failed with exit status 1 — uncaught exception
#   Unit stuck in error: "hook failed: saml-relation-created"
#   any-charm/0 side: showed active but relation data was never written
# Fixed by restoring URL → hook retried and succeeded → unit recovered
```

**Failure injection: bad metadata_url without relation (edge rev 168)**
```
# Same bad URL with no relations → status stayed active
# _update_relations() iterates self.saml.relations (empty) → returns immediately
# metadata property never accessed → URL never fetched
# Same bug as in stable rev 66
```

**Teardown**
```
juju scale-application saml-integrator 0
# Pods terminated cleanly
# any-charm removed via juju remove-application
# Model rv-saml-k8s4 empty after teardown
```

### Kubernetes (k8s substrate, Juju 3.6)
```
juju add-model rv-saml-k8s3 --controller concierge-k8s-3
juju deploy saml-integrator --channel latest/edge  # rev 168
# Pod created in ~25s from deploy to blocked (entity_id not set)

juju config entity_id + metadata_url → active after ~34s

# Deployed any-charm (rev 175, beta) and related it
# Hook sequence confirmed:
#   saml-relation-created (sets maintenance → active)
#   saml-relation-joined (no handler, no-op)
#   saml-relation-changed (no handler, no-op)

# Failure injection: bad metadata_url with live relation
#   config-changed hook: maintenance "Configuring charm" → hook failed exit 1
#   Unit in error: "hook failed: config-changed"
#   Retry every ~10s
# Restored URL → hook succeeded → active

# Scale up: juju add-unit saml-integrator -n 2 → 3 units active in ~15s
# Scale down: juju scale-application saml-integrator 1 → 1 unit cleanly
```

## Observed behaviour

- **Install/start speed**: ~13s machine, ~10s k8s. Fast because no OCI image to pull.
- **Hook idempotency**: repeated `config-changed` does not re-render; `_update_relations()` re-writes the same data every call.
- **Leader election**: no `leader-elected` hook when scaling 1→2 (unit/0 already leader); unit/1 took ~6s total for install+config-changed+start.
- **Bad `metadata_url` silently accepted (no relations)**: confirmed on LXD 3.6, LXD 4, k8s 3.6, k8s 4. `_update_relations()` iterates `self.saml.relations` (empty) and returns; `metadata` property never accessed.
- **Bad `metadata_url` with live relation crashes hook**: when a relation exists and `metadata_url` is unreachable, `relation-created`, `config-changed`, and `update_status` all access `metadata`, which calls `urlopen` and raises `CharmConfigInvalidError`. Not caught in any of the three handlers. Hook exits 1, unit stuck in error until the URL is fixed. Juju retries every ~10s (LXD 3.6) or ~30s (k8s 4). Recovery on retry once the URL is restored; no `juju resolved` needed.
- **Wrong `entity_id` silently accepted (with live relation)**: charm stays `active`. Relation databag written with wrong `entity_id` but correct SSO/SLO URLs from the real IdP metadata; `x509certs` silently dropped (empty tuple → `""` → Juju drops empty-string values). Requiring charm gets corrupted data with no error signal.
- **`from_relation_data` crashes when `x509certs` is absent**: `relation_data.get("x509certs")` → `None` → `None.split(",")` → `AttributeError`, crashing the requirer charm's event handler.
- **`from_relation_data` with empty `x509certs` present**: when the key is present as `""`, `.split(",")` returns `("",)` — semantically wrong (empty cert accepted) but does not crash.
- **`from_relation_data` with missing `entity_id`**: `None` → pydantic `ValidationError` → crash, less confusing than the `AttributeError` case but still a crash.
- **`metadata_url` takes precedence over inline `metadata`**: when both are set, `metadata_url` wins (checked first in the `metadata` property); inline `metadata` is silently ignored, no error raised.
- **`fingerprint` accepts any string**: no format validation at config time; malformed values (e.g. `"NOT_HEX"`) are accepted and fail later with "The metadata's signing certificate does not match the provided fingerprint".
- **Relation data with correct config**: databag correctly populated with `entity_id`, `metadata_url`, `x509certs` (comma-separated), `single_sign_on_service_redirect_url`/`_binding`, `single_logout_service_redirect_url`/`_binding`, and `response_url` per endpoint.
- **`update_status` hook**: fires every ~5 min; at HEAD (rev 168) sets `MaintenanceStatus` → `ActiveStatus`. On error (bad URL, live relation) it fails with the same uncaught `CharmConfigInvalidError`.
- **Juju 3.6 vs 4.x**: identical behaviour for all tested scenarios — same hook sequence, same error propagation. Machine provisioning on LXD 3.6 is significantly slower (~6-10 min vs ~2 min on LXD 4). Retry intervals slightly faster on 3.6 (~10s vs ~30s on k8s 4).
- **Relation hook sequence (both Juju versions)**: `relation-created` (handled, maintenance → active), `relation-joined`/`relation-changed`/`relation-departed`/`relation-broken` (no handler, no-op). All fire correctly.
- **No file operations**: charm never writes to disk — metadata fetched from URL or config, parsed in memory, written to relation databags.
- **K8s Pebble behaviour**: `container-agent` Pebble service runs (Juju unit agent). Readiness check returns HTTP 418 (intentional, workloadless charm). `pebble` binary at `/charm/bin/pebble`, not in PATH.
- **`remove-relation`**: works; `relation-broken`/`relation-departed` fire on provider, `relation-changed` on requirer.
- **`stop` hook**: fires during refresh (old pod torn down before new one starts) and on application removal; charm goes `maintenance` before stopping.
- **`juju refresh` upgrade path**: old pod stopped, new pod starts, `upgrade-charm` + `config-changed` run on new pod; no custom upgrade handler; status transitions `maintenance → active` cleanly.

## Findings

### 1. Uncaught `CharmConfigInvalidError` in all three hook handlers — unit stuck in error, no `BlockedStatus`
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py` — `_on_relation_created`, `_on_update_status`, `_on_config_changed` (source at HEAD matches deployed edge rev 168)
- **Evidence**: set `metadata_url` to an unreachable domain with a live relation (any-charm integrated). `saml-relation-created` fired, set `MaintenanceStatus("Update integrations")`, called `_update_relations()` → `get_saml_data()` → `SamlIntegrator.certificates` → `SamlIntegrator.tree` → `CharmState.metadata` → `urlopen(bad_url)` → raised `CharmConfigInvalidError`, uncaught, hook exit 1:
  ```
  02 Sep 2026 01:21:27+12:00  workload   maintenance  Update integrations
  02 Sep 2026 01:21:27+12:00  juju-unit  error        hook failed: "saml-relation-created"
  ```
  Unit retried every ~10s until the URL was restored, then recovered automatically.
- **Impact**: the operator sees "hook failed: saml-relation-created" with no actionable message; the unit never reaches `BlockedStatus`. The requirer (any-charm) shows `active` but has no relation data — any SAML-using functionality in the requirer silently fails. Same failure mode affects `config-changed` (when a relation exists) and `update_status`.
- **Fix**: wrap `_update_relations()` in a try/except in all three handlers, e.g.
  ```python
  def _on_relation_created(self, _) -> None:
      self.unit.status = ops.MaintenanceStatus("Update integrations")
      try:
          self._update_relations()
      except CharmConfigInvalidError as exc:
          self.unit.status = ops.BlockedStatus(exc.msg)
          return
      self.unit.status = ops.ActiveStatus()
  ```
- **Linter rule**: "Hook handlers that call `_update_relations()` must catch `CharmConfigInvalidError` and set `BlockedStatus`." Not mechanically checkable without runtime behaviour analysis.

### 2. `SamlRelationData.from_relation_data` crashes with `AttributeError` when `x509certs` is absent
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/saml_integrator/v0/saml.py:214-215`
- **Evidence**: in the wrong-`entity_id` scenario, `certificates=[]` → `",".join([]) = ""` → Juju drops the empty-string value from the databag. A requirer calling `from_relation_data(relation_data)` hits:
  ```python
  certificates=tuple(relation_data.get("x509certs").split(","))  # line 214-215
  # relation_data.get("x509certs") → None (key absent)
  # None.split(",") → AttributeError
  ```
  Confirmed with `PYTHONPATH="lib:src" uv run python3 -c "..."`, producing `AttributeError: 'NoneType' object has no attribute 'split'`.
- **Impact**: a requirer charm that successfully relates crashes in its own event handler when reading relation data. The operator sees the requirer charm in error with no indication saml-integrator is the root cause.
- **Fix**:
  ```python
  certs_str = relation_data.get("x509certs")
  certificates = tuple(certs_str.split(",")) if certs_str else ()
  ```
- **Linter rule**: "Relation data access must handle absent keys gracefully." Checkable: `from_relation_data` must not crash on missing keys.

### 3. Wrong `entity_id` silently accepted with live relation — corrupt SAML data served to requirer
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/saml.py` `certificates`/`endpoints` (XPath returns empty on no match); `src/charm.py:_update_relations` (no entity_id validation)
- **Evidence**: set `entity_id="https://this-entity-does-not-exist.in.metadata.example.com"` with a live relation. Charm stayed `active`. Databag:
  ```json
  {
    "entity_id": "https://this-entity-does-not-exist.in.metadata.example.com",
    "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
    "single_sign_on_service_redirect_url": "https://login.staging.ubuntu.com/saml/",
    "single_sign_on_service_redirect_binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
    "single_logout_service_redirect_url": "https://login.staging.ubuntu.com/+logout",
    "single_logout_service_redirect_binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    // x509certs ABSENT — empty tuple silently dropped
  }
  ```
  SSO/SLO URLs still point at the real IdP but are now tied to a wrong `entity_id`. Combined with finding 2, a requirer will crash reading this data.
- **Impact**: charm reports `active` while serving broken SAML data to every requirer; no signal until a requirer crashes or auth fails.
- **Fix**: after parsing metadata, validate that at least one of `certificates`/`endpoints` is non-empty; raise `CharmConfigInvalidError` ("entity_id not found in IdP metadata") if both are empty.
- **Linter rule**: "XPath query for entity_id must not silently return zero results." Checkable: assert `len(certificates) > 0 or len(endpoints) > 0` after the XPath queries.

### 4. Charm stays active with unreachable `metadata_url` when no relations exist
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:_update_relations`
- **Evidence**: `for relation in self.saml.relations:` — empty list means the loop body, and thus the metadata fetch, never runs. Confirmed on LXD (rev 66) and k8s (rev 168); status stays `active` despite an unreachable URL.
- **Impact**: the operator sets a broken `metadata_url`, sees `active`, and only discovers the problem when a requirer joins and the `relation-created` hook fails (finding 1) — no prior warning.
- **Fix**: validate `metadata_url` (attempt the fetch) in `CharmState.from_charm()` rather than lazily in the `metadata` property, so `BlockedStatus` is set at config time.
- **Linter rule**: "Charm must not reach ActiveStatus when `metadata_url` is set but unreachable." Not mechanically checkable without network access.

### 5. No unit test for `from_relation_data` / `SamlEndpoint.from_relation_data`
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_library_saml.py` (absent coverage)
- **Evidence**: `rg "from_relation_data" tests/unit/` returns no matches. The only library test for `SamlRelationData` covers `to_relation_data`, not `from_relation_data`. The crash paths in findings 2 and the entity_id/`x509certs` edge cases have zero unit test coverage.
- **Impact**: these are exactly the failure modes found in the field; a simple unit test would have caught all of them.
- **Fix**: add parametrized tests for `from_relation_data` covering normal data, missing `x509certs`, present-but-empty `x509certs`, missing `entity_id`, empty `entity_id`, missing URL.
- **Linter rule**: "Relation data deserialisation methods must have unit tests covering missing and empty key paths." Checkable by coverage tools + mutation analysis.

### 6. `metadata_url` fetch does not clearly respect Juju proxy settings (issue #248)
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm_state.py` `metadata` property
- **Evidence**: `with urllib.request.urlopen(str(...), timeout=10)` — bare call, no explicit proxy config. GitHub issue #248 open since 2026-06-24. On k8s, logs showed a `"unable to set snap core settings"` warning; Juju proxy env vars were not confirmed present in the container (unverified whether this actually breaks the fetch — no proxy environment was available to test against).
- **Impact**: in egress-filtered environments the charm may be unable to fetch metadata even where Juju has proxy config set.
- **Fix**: use `requests` with `session.trust_env = True` / `get_environment_proxies()`, or otherwise explicitly honour Juju's proxy configuration.
- **Linter rule**: "HTTP requests in charm code must use a client that respects Juju's proxy configuration." Not mechanically checkable without a proxy environment.

### 7. Empty `metadata_url=""` produces misleading pydantic error message
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm_state.py` `SamlIntegratorConfig` / `from_charm`
- **Evidence**: set `metadata="NOT XML AT ALL" metadata_url=""`. Status became `blocked "invalid configuration: metadata_url"` because pydantic's `AnyHttpUrl` rejects `""` even though the field is `Optional`. The real problem was the invalid inline metadata, but the message points at the URL field.
- **Impact**: an operator using inline metadata who forgets to clear `metadata_url` gets a confusing error pointing at the wrong field.
- **Fix**: add a pre-validator coercing empty string to `None` for `metadata_url`.
- **Linter rule**: "Optional URL fields must not reject empty strings as validation errors." Not mechanically checkable.

### 8. `urlopen` fetch has no explicit DNS-resolution timeout
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm_state.py` `metadata` property
- **Evidence**: `timeout=10` is passed to `urlopen`, but that applies to the HTTP request, not DNS lookup; for a non-existent domain DNS resolution can exceed 10s on some networks.
- **Impact**: a bad `metadata_url` can block the hook for longer than expected before failing.
- **Fix**: resolve with `socket.getaddrinfo` under a short timeout first, or catch `socket.gaierror` explicitly.
- **Linter rule**: "HTTP fetch must have explicit DNS resolution timeout." Not mechanically checkable.

### 9. `FutureWarning` from lxml element truth-testing
- **Severity**: low
- **Kind**: lint
- **Where**: `src/saml.py:80` (`if self.signing_certificate and self.signature:`); likely also `src/saml.py:142`/`161` (`etree.QName(result).localname`)
- **Evidence**: `self.signature` is an lxml `Element`; Python 3.12+ deprecates truth-testing lxml elements. Confirmed in unit test output: `FutureWarning: Truth-testing of elements was a source of confusion...` (2 occurrences).
- **Impact**: works today, will break on a future Python/lxml version.
- **Fix**: use `is not None` explicitly; pass `result.tag` rather than the element to `etree.QName`.
- **Linter rule**: `S324` (bandit) or a custom rule for lxml element truth-tests. Mechanically checkable.

### 10. Empty-string relation data values silently dropped by Juju
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/saml_integrator/v0/saml.py` `to_relation_data`
- **Evidence**: when `certificates` is empty, `",".join([])` produces `""`, which Juju drops from the databag entirely. Confirmed via `juju show-unit saml-integrator/0` after setting a wrong `entity_id` — no `x509certs` key appears.
- **Impact**: leads directly to the `None.split(",")` crash in finding 2.
- **Fix**: skip writing `x509certs` when `certificates` is empty, or write a sentinel value.
- **Linter rule**: "Relation data write must not produce semantically different data after Juju storage." Not mechanically checkable without Juju.

### 11. `from_relation_data` accepts empty certificate string as `("",)`
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/saml_integrator/v0/saml.py:214`
- **Evidence**: when `x509certs` is present as `""`, `.split(",")` returns `("",)` — a one-element tuple with an empty string, accepted by pydantic's `Tuple[str, ...]` with no element-level validation.
- **Impact**: an empty certificate is semantically invalid but indistinguishable from a valid single-cert case; downstream SAML validation may fail confusingly.
- **Fix**: add element-level validation rejecting empty strings.
- **Linter rule**: "Tuple fields with certificate-like data must not accept empty-string elements." Not mechanically checkable without domain knowledge.

### 12. `metadata_url` silently takes precedence over inline `metadata`
- **Severity**: low
- **Kind**: bug / ux
- **Where**: `src/charm_state.py` `metadata` property
- **Evidence**: `if self._saml_integrator_config.metadata_url:` checks `metadata_url` first; if set, inline `metadata` is never accessed, and no error is raised for the conflicting config. Confirmed by running with both options set.
- **Impact**: an operator relying on inline metadata for offline use may be silently overridden by a stale `metadata_url` value.
- **Fix**: raise `CharmConfigInvalidError` in `from_charm` when both are non-empty.
- **Linter rule**: "Mutually exclusive options must not both be accepted silently." Not mechanically checkable without domain knowledge.

### 13. Stable channel (rev 66) ~10 months behind edge (rev 168)
- **Severity**: low
- **Kind**: docs / ops
- **Where**: N/A — operational gap
- **Evidence**: `juju info saml-integrator` shows `latest/stable: 66 (2024-09-20)`, `latest/edge: 168 (2026-09-01)`. Source HEAD (`576c220`, 2026-07-21) maps to stable rev 66; edge is well ahead. Notably edge has `_on_relation_created` setting `MaintenanceStatus`→`ActiveStatus` (commit `9da5b84`), stable does not; edge library is `LIBPATCH=11`, stable is `LIBPATCH=10`.
- **Impact**: users on the stable channel get inferior status handling and a library one patch behind.
- **Fix**: publish a new stable release.
- **Linter rule**: not applicable.

## Worth copying

- Clean separation of concerns: `CharmState` (config parsing/validation), `SamlIntegrator` (XML parsing/signature validation), `SamlProvides`/`SamlRequires` (relation data) are three distinct classes with clear responsibilities.
- Pydantic for config validation: `SamlIntegratorConfig` with `Field(..., min_length=1)` and `AnyHttpUrl` gives structured, typed validation with clear error messages, wrapped by `CharmConfigInvalidError`.
- Cached properties for expensive operations: `SamlIntegrator.tree`, `certificates`, `endpoints` are `@cached_property` — XML parsed once, reused.
- Library versioning with interface schema: `SamlRelationData`, `SamlEndpoint`, `SamlDataAvailableEvent` give a well-typed, self-documenting interface for requirer charms.
- Leadership guard: `_update_relations` returns early if not leader, avoiding unnecessary work on follower units.
- Endpoint sorting: `from_relation_data` sorts endpoints by name before constructing the model, ensuring deterministic output regardless of databag key order.

## Common-practice notes

- Follows ecosystem norms — `src/` layout, `lib/charms/<name>/v<N>/` library versioning, `charmcraft.yaml` with `parts.uv`, `pyproject.toml` dependency groups, `uv` directly instead of `tox.ini`.
- `charmcraft.yaml` uses `plugin: uv` with `build-snaps: [astral-uv]` — newer than `plugin: charm`, correct for uv-based charms.
- Library version: LIBAPI=0, LIBPATCH=11 (edge/source); published stable (rev 66) is LIBPATCH=10.
- Test suite uses `ops.testing.Harness`, which is deprecated in favour of `scenario`; test output shows `PendingDeprecationWarning` across the board — known migration gap.
- No `__init__.py` in `lib/`/`src/` — implicit namespace packages (PEP 420). Works with `uv run`/pytest's `pythonpath` config, but not with plain `PYTHONPATH` without the `uv run` wrapper.
- Workloadless charm behaves identically on machine and k8s; the only visible difference is the Pebble readiness check (418 on k8s) and the snap proxy warning (harmless on k8s).
- No actions defined (`actions.yaml` absent); no action testing performed.
- K8s scaling uses `juju scale-application`; LXD uses `juju add-unit`/`remove-unit` with named units — charm code itself is substrate-agnostic.
- Juju 3.6 vs 4.x: identical charm behaviour; machine provisioning slower on 3.6 LXD (~6-10 min vs ~2 min); hook retry intervals slightly faster on 3.6 (~10s vs ~30s on k8s 4).

## Tests

- Unit tests: 20/20 pass via `uv run --with pytest --with pytest-asyncio python3 -m pytest tests/unit/ -v`. Plain `python3 -m pytest` fails due to the namespace-package structure. 504 warnings in output (500× `pytest-asyncio` `DeprecationWarning` + 2× lxml `FutureWarning`).
- Linters: `ruff` passes all checks (including bandit/`S`); `mypy` clean; `codespell` clean.
- Integration tests require `any-charm` + custom library injection via `src-overwrite`; cannot be run without `charmcraft pack`. `test_active`/`test_relation` only assert `ActiveStatus`, not databag content or error recovery.
- Interface tests (`tests/interface/test_saml.py`) delegate to `canonical/charm-relation-interfaces`; not run in this environment.
- CI (`test.yaml`) uses `canonical/operator-workflows` with `with-uv: true`; integration tests run against Juju `1.35-strict/stable`.
- Key untested paths confirmed by reading test files + code: `from_relation_data` with missing/empty `x509certs`; `from_relation_data` with missing `entity_id`; `SamlEndpoint.from_relation_data` with missing `_url`/`_binding`; wrong-`entity_id` corrupt relation data; `_on_config_changed`/`_on_update_status` raising `CharmConfigInvalidError` with a live relation; automatic recovery after URL restore; `metadata_url` precedence over inline `metadata`; `relation-broken` hook (only indirectly covered by integration test).

## Docs

- README.md: minimal, one paragraph plus links to the charmhub tutorial. Thin but acceptable for a library-style charm.
- `docs/reference/charm-architecture.md`: explains the three-layer design, event model, and data flow — good primary reading for contributors.
- `docs/how-to/configure-saml.md`: correctly describes `entity_id` and `metadata_url` as the two mandatory options, matching observed behaviour.
- `docs/tutorial/getting-started.md`: links to charmhub; not independently verified.
- Terraform module present at `terraform/charm/` and `terraform/product/` with tests; not reviewed in detail.
- Charmhub description matches actual behaviour (workloadless, machine + k8s).
- The proxy issue (#248) is not documented anywhere.

## Open questions

1. Does the proxy fetch in `urlopen` actually fail against a real Juju-configured proxy, or only show a cosmetic snap warning on k8s? Not verified against a live proxy.
2. Is the silent XPath-empty behaviour for a non-matching `entity_id` intentional, or should the charm validate the entity is present in the metadata?
3. Is Juju's dropping of empty-string relation values ("") the intended platform behaviour, or should the library avoid writing empty keys?
4. When will the test suite migrate from `ops.testing.Harness` to `scenario`?
5. Why is the stable channel (rev 66, 2024-09-20) ~10 months behind edge (rev 168, 2026-09-01) and source HEAD (2026-07-21)? Is a stable release planned?
6. Is `metadata_url` silently taking precedence over inline `metadata` the intended behaviour, or should conflicting config raise an error?
