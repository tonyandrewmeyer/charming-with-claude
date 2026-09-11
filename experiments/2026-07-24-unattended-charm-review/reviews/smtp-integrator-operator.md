# smtp-integrator

SMTP Integrator is a workloadless Juju charm (`type: charm`, deployable on both Kubernetes and machines) that centralises SMTP configuration and distributes it to consumer charms via the `smtp` (Juju secrets) and `smtp-legacy` (plaintext password) relation interfaces. The reconciler pattern, secret lifecycle, and test coverage are solid, but there is one critical uncaught-exception bug that turns a routine misconfiguration (referencing a secret the charm can't read) into an indefinite crash loop with an opaque `Error` status, plus a `KeyError` hazard in the requirer library that can silently break event delivery. Fix `_validate_secret`'s exception handling first; everything else here is lower-priority hardening and test-gap closure.

| | |
|---|---|
| Repo | canonical/smtp-integrator-operator @ `554bcc9` (2026-07-21) |
| Charms | smtp-integrator |
| Substrate | machine **and** Kubernetes (both tested) |
| Deployed | yes — concierge-lxd-4 (Juju 4.0.12), concierge-lxd (Juju 3.6.27), concierge-k8s-4 (Juju 4.0.12), all latest/edge rev 128 |
| Reviewed | 2026-09-01 |

## What it does

SMTP Integrator receives SMTP connection configuration (host, port, auth, TLS, credentials, sender/recipients) via charm config, validates it with Pydantic, and propagates it through two relation interfaces:

- `smtp` — modern interface; password passed as a Juju secret ID, secret granted to the relation with view role
- `smtp-legacy` — legacy interface; password written in plaintext directly in the databag

The charm is workloadless (no OCI image, no systemd unit, no Pebble workload). On Kubernetes it runs as a pure operator pod (`container-agent` only). Leadership is required for reconciliation. A peer relation stores the Juju secret ID for password propagation. Requires Juju ≥ 3.1.0, Ubuntu 22.04.

## Deployment log

### Machine (Juju 4.x, concierge-lxd-4)

```bash
juju add-model rv-smtp-test -c concierge-lxd-4
juju deploy smtp-integrator --channel edge -m rv-smtp-test
# Machine juju-969a92-0: ~5 min to Running
# Blocked (no host) → juju config host=smtp.example.com → Active

juju deploy any-charm --channel beta -m rv-smtp-test
juju relate smtp-integrator:smtp any-charm:smtp
juju relate smtp-integrator:smtp-legacy any-charm:smtp-legacy
# Relation data: host, port, auth_type, transport_security, skip_ssl_verify
# Secret created and granted to any-charm with view role on smtp relation
# smtp-legacy: password in plaintext

# Failure injection:
juju config smtp-integrator transport_security=nonexisting  # Blocked ~10s later
juju config smtp-integrator auth_type=nonexisting             # Blocked ~10s later
juju config smtp-integrator auth_type=none                    # Active again

# Relation removal:
juju remove-relation smtp-integrator:smtp any-charm:smtp
# juju show-secret --reveal: access list empty (revoked) ✓

# Scale-up:
juju add-unit smtp-integrator -n 1 -m rv-smtp-test
# Machine juju-969a92-2: ~4 min to Running
# Unit 1 goes Active; unit 0 remains leader
# Peer secret correctly shared: unit 1 reads secret-id from peer databag

# Scale-down:
echo "y" | juju remove-unit smtp-integrator/1 -m rv-smtp-test
# Machine cleaned up, model returns to single-unit

# Scale-up again (2 units):
juju add-unit smtp-integrator -n 1 -m rv-smtp-test
# Both units Active; unit 0 leader, unit 2 follower
# Peer databag correctly read by both units

# juju refresh:
juju refresh smtp-integrator --channel edge -m rv-smtp-test
# "already up-to-date" ✓

# remove-application:
echo "y" | juju remove-application smtp-integrator -m rv-smtp-test
# Machine destroyed; model empties ✓
```

### Machine (Juju 3.6, concierge-lxd)

```bash
juju add-model rv-smtp-j3 -c concierge-lxd
juju deploy smtp-integrator --channel edge -m rv-smtp-j3
# Machine juju-757f77-0: ~6 min to Running
# Blocked (no host) → config → Active
# No differences observed between Juju 3.6 and 4.0 for this charm
```

### Kubernetes (Juju 4.x, concierge-k8s-4)

```bash
juju add-model rv-smtp-k8s -c concierge-k8s-4
juju deploy smtp-integrator --channel edge -m rv-smtp-k8s
# Pod smtp-integrator-0: ~1 min to Running (charm init container)
# Status: waiting "installing agent" → blocked "invalid configuration: host" → active

kubectl get pods -n rv-smtp-k8s
# modeloperator-xxx Running
# smtp-integrator-0     Running (1/1) — charm + charm-init containers

/charm/bin/pebble services
# container-agent: enabled, active (the only service — no workload)

juju config smtp-integrator host=smtp.example.com  # → Active
# Secret lifecycle identical to machine: peer secret stored in peer databag,
# grants issued to related apps with view role
```

## Observed behaviour

- **Machine provisioning**: ~5 min on both Juju 3.6 and 4.x (LXD container startup dominates)
- **Config validation latency**: ~10–15s from `juju config` to final status update (both leader and unit agent config-changed hooks)
- **Hook count for unchanged config**: 0 — Juju dedupes no-op config changes before delivering them
- **Hook count for real config change**: 2 × `config-changed` per change (leader + unit agent, confirmed live)
- **Hook count on scale-up unit 1**: `install → smtp-relation-created → smtp-peers-relation-created → config-changed → start → smtp-relation-joined → smtp-relation-changed → smtp-peers-relation-changed → smtp-peers-relation-joined → smtp-peers-relation-changed` (10 hooks total). Identical pattern on the second scale-up (unit 2).
- **Secret lifecycle on k8s**: identical to machine — peer secret stored in peer databag, grants issued per-relation with view role, revoked on relation removal
- **No workload on k8s**: Pebble plan shows only `container-agent` (the Juju operator); no application service
- **Failure recovery from bad config**: Bad config resolves to `BlockedStatus` with field name (e.g. "invalid configuration: port"); on fix, charm returns to `ActiveStatus` within ~10s
- **Failure recovery from `ModelError` crash**: When `_validate_secret` raises `ModelError` (secret inaccessible), charm enters `Error` status with an opaque "hook failed: config-changed". Recovery requires `juju config password_secret=''`. Charm auto-retries and re-crashes indefinitely until resolved; clearing the config lets it recover to Active on the next hook.
- **Relation removal while Blocked**: `smtp-relation-departed` and `smtp-relation-broken` hooks run cleanly. Secret access revoked from removed relation (confirmed via `juju show-secret --reveal`). Charm remains Blocked (no regression).
- **Relation removal while Active**: `smtp-relation-broken` hook runs cleanly on both units, secret access list empties, `any-charm` remains Active.
- **Secret permission denied**: When `password_secret` is a model-owned secret not granted to smtp-integrator, `_validate_secret` raises `ops.model.ModelError` (not `SecretNotFoundError`). Uncaught → hook crash → `Error` status, re-crashing indefinitely. CLI-level secret URI validation blocks some bad values (e.g. `secret:notexist123`) before they reach the charm. Recovery: `juju config password_secret=''`.
- **Unit restart**: Killing the `jujud machine` PID restarts the machine agent; unit resumes at the same status (Blocked, missing host). Reconciler runs correctly on restart — no state loss.
- **`juju refresh`**: Reports "already up-to-date" when channel is current.
- **`remove-application`**: Fully tears down — application, units, and machine are removed; model empties.
- **No custom actions**: `juju actions smtp-integrator` returns "No actions defined" — correct for a workloadless config-distribution charm.
- **Config propagation to both interfaces**: Changing `user` config updates both `smtp` and `smtp-legacy` relations simultaneously; `smtp-legacy` carries the plaintext password, `smtp` carries the secret ID.
- **`relation-changed` fires on consumer when provider config changes**: Provider uses `config_changed` → reconciler → `update_relation_data` → `relation-changed` fires on the consumer. No `relation_changed` observer on the provider — correct pattern for a config-driven charm.
- **Stale relation data while Blocked**: When `host` config is removed while a relation exists, smtp-integrator goes Blocked ("invalid configuration: host") but the relation databag retains stale previously-published data (`host: smtp.example.com` visible via `juju show-unit smtp-integrator/0` even while blocked). Consumer charms may read stale data until the provider recovers.
- **`literal_eval(None)` hazard**: The `skip_ssl_verify` event property calls `literal_eval(str(self.relation.data[self.relation.app].get("skip_ssl_verify")))`. If the key is absent, `.get()` returns `None`, `str(None)` → `"None"`, `literal_eval("None")` → Python `None` (`NoneType`, not `bool`, contradicting the return type annotation). A malformed value raises `ValueError`, uncaught, into the hook. Coverage lines 268–269 missed; no test exercises absent or malformed `skip_ssl_verify`.
- **Peer secret access**: Both leader and follower units correctly read the peer secret ID from the peer databag; follower unit 2 shows `secret-id: secret://...` in its `smtp-peers` application-data.
- **Secret revoked on relation removal**: `juju show-secret --reveal` confirms zero access list for the peer secret after `smtp` relation removal.
- **`skip_ssl_verify` stored as string `"True"`/`"False"`**: `to_relation_data` writes `str(self.skip_ssl_verify)` rather than a JSON boolean; Juju relation data conventions prefer bare `true`/`false`.

## Findings

### 1. `_validate_secret` catches `SecretNotFoundError` but not `ops.model.ModelError` — uncaught exception crashes the hook

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:195–213`
- **Evidence**:
  ```python
  def _validate_secret(self, secret_id: str) -> None:
      try:
          secret = self.model.get_secret(id=secret_id)        # line 205: raises ModelError if no read access
          content = secret.get_content()
          if "password" not in content:
              raise CharmConfigInvalidError(...)
      except ops.SecretNotFoundError as ex:                    # line 211: only catches NotFound, not ModelError
          raise CharmConfigInvalidError(f"Secret with id '{secret_id}' does not exist") from ex
  ```
  When `password_secret` references a valid secret the charm cannot read (e.g. a model-owned secret not granted to smtp-integrator), `model.get_secret()` raises `ops.model.ModelError`, which is not caught. The exception propagates to the uniter, producing `Error` status ("hook failed: config-changed"). The charm auto-retries and re-crashes indefinitely until the bad config is removed.

  Live reproduction on `concierge-lxd-4:rv-smtp-test`:
  1. `juju add-secret wrongsecret wrongkey=myvalue` → `secret:m5hq5n03v62pliipt81g`
  2. `juju config smtp-integrator password_secret=secret:m5hq5n03v62pliipt81g` → Error status within ~10s
  3. Debug-log: `ops.model.ModelError: ERROR "smtp-integrator/0" is not allowed to read this secret`
  4. Recovery: `juju config smtp-integrator password_secret=''` → auto-recovers to Active within ~50s
- **Impact**: An operator who references a model-owned secret in config will permanently break the charm with an obscure hook failure rather than an actionable Blocked status. The message "hook failed: config-changed" is opaque; only the debug log reveals the root cause. The only recovery path is clearing the config via CLI.
- **Fix**: Add `except ops.model.ModelError:` (or broaden to `except Exception:`) in `_validate_secret`, converting it into `CharmConfigInvalidError` so it maps to `BlockedStatus`.
- **Linter rule**: "`model.get_secret` calls that can raise `ModelError` should catch it alongside `SecretNotFoundError`" — mechanically checkable by searching for `model.get_secret` without a corresponding `ModelError` catch in the same function.

### 2. `_on_relation_changed` can raise `KeyError` on malformed databag before validation

- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/smtp_integrator/v0/smtp.py:428`
- **Evidence**:
  ```python
  relation_data = event.relation.data[event.relation.app]
  if relation_data:                                          # truthy if dict non-empty
      if relation_data["auth_type"] == AuthType.NONE.value:   # KeyError if key absent
          logger.warning('Insecure setting: auth_type has a value "none"')
  ```
  The handler checks `if relation_data:` then directly indexes `relation_data["auth_type"]` without a `.get()` guard. A provider on the `smtp` interface that writes a partial databag crashes the handler with `KeyError: 'auth_type'`. The `_is_relation_data_valid()` call, which would validate safely, runs after this direct access.
- **Impact**: A non-smtp-integrator provider that violates the interface contract crashes the handler, and `smtp_data_available` is never emitted for that relation — silently, with no visible operator error.
- **Fix**: Use `relation_data.get("auth_type")` and guard the subsequent check, or move the `_is_relation_data_valid` call ahead of the insecure-warning log block.
- **Linter rule**: "dictionary access on relation-data dict-like object without `.get()` for optional keys" — checkable via AST analysis.

### 3. `literal_eval("None")` in `skip_ssl_verify` event property returns `None`, not `bool`

- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/smtp_integrator/v0/smtp.py:283–286`
- **Evidence**:
  ```python
  @property
  def skip_ssl_verify(self) -> bool:
      assert self.relation.app
      return literal_eval(
          typing.cast(str, self.relation.data[self.relation.app].get("skip_ssl_verify"))
      )
  ```
  `.get("skip_ssl_verify")` returns `None` if the key is absent; `str(None)` → `"None"`; `literal_eval("None")` → `NoneType`, contradicting the `bool` return annotation. A malformed non-bool value (e.g. `"maybe"`) raises `ValueError`, uncaught, into the hook. Coverage lines 268–269 missed — no test provides absent or malformed `skip_ssl_verify`.
- **Impact**: A provider that omits `skip_ssl_verify` (valid — the Pydantic model treats it as `Optional[bool] = False`) causes the requirer to receive `None` instead of `False`, and downstream code expecting `bool` may misbehave. A malformed value crashes the hook.
- **Fix**: Replace `literal_eval()` with `json.loads(self.relation.data[self.relation.app].get("skip_ssl_verify", "false"))`.
- **Linter rule**: "`literal_eval` on relation data without prior type guard" — mechanically checkable.

### 4. `SmtpRequires._is_relation_data_valid` silently swallows invalid data with only a log line

- **Severity**: medium
- **Kind**: ux
- **Where**: `lib/charms/smtp_integrator/v0/smtp.py:399–415`
- **Evidence**:
  ```python
  except ValidationError as ex:
      error_fields = set(...)
      logger.warning("Error validation the relation data %s", error_field_str)  # typo
      return False
  ```
  When relation data fails validation, the requirer logs a warning and returns `False`. No `SmtpDataAvailableEvent` fires, and no status is set — the requirer silently has no SMTP configuration. The log message also has a typo ("Error validation") and omits the relation ID, making it hard to correlate in multi-relation deployments.
- **Impact**: Consumer charms relying on SMTP will silently not work; the root cause is invisible from `juju status`.
- **Fix**: Emit `BlockedStatus` or a custom warning event when validation fails; fix the typo and include `relation.id` in the log.
- **Linter rule**: not mechanically checkable.

### 5. Relation data not cleared when provider is Blocked

- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:62–70` (reconciler), `src/charm.py:85` (`_reconcile`)
- **Evidence**: When `_reconcile` raises `CharmConfigInvalidError`, the reconciler exits and sets `BlockedStatus` without clearing existing relation data. Confirmed live on `concierge-lxd-4:rv-smtp-test`: `juju config host=''` → Blocked ("invalid configuration: host") → `juju show-unit smtp-integrator/0` still shows `host: smtp.example.com` in both `smtp` and `smtp-legacy` databags.
- **Impact**: Consumer charms see the last-known-good SMTP configuration even after the provider is in an invalid state. If a credential is compromised or wrong, consumers keep using it.
- **Fix**: Clear relation data (at minimum the password ID) before setting Blocked, or explicitly document the last-known-good behaviour as intentional.
- **Linter rule**: not mechanically checkable.

### 6. Architecture doc claims `update-status` is observed; code does not register that hook

- **Severity**: medium
- **Kind**: docs
- **Where**: `docs/reference/charm-architecture.md:20–22`; `src/charm.py:48–49`
- **Evidence**: The doc states: "`[update-status]`: Fired periodically. **Action**: validate the configuration and propagate the SMTP configuration through the relation." The `__init__` observers registered are:
  ```python
  self.framework.observe(peer_events.relation_created, self._reconcile_event)
  self.framework.observe(peer_events.relation_changed, self._reconcile_event)
  self.framework.observe(legacy_events.relation_created, self._reconcile_event)
  self.framework.observe(smtp_events.relation_created, self._reconcile_event)
  self.framework.observe(smtp_events.relation_broken, self._on_relation_broken)
  self.framework.observe(self.on.config_changed, self._reconcile_event)
  ```
  No `update-status` observer; `grep -n "update.status" src/charm.py` returns nothing.
- **Impact**: An operator reading the doc will expect the charm to self-heal on the periodic `update-status` hook. It won't — reconciliation only happens on `config_changed` and relation events, which is acceptable behaviour, but the doc misrepresents it and could mislead an operator waiting for auto-recovery.
- **Fix**: Remove the `update-status` bullet from the architecture doc, or add `self.framework.observe(self.on.update_status, self._reconcile_event)`.
- **Linter rule**: "docs reference an event that the charm does not observe" — checkable by diffing the doc's event list against registered observers in `__init__`.

### 7. Getting-started tutorial covers Kubernetes only, leaving machine users with no path

- **Severity**: medium
- **Kind**: docs
- **Where**: `docs/tutorial/getting-started.md`
- **Evidence**: The tutorial states "We'll be deploying the charm on top of Kubernetes" and uses `kubectl get pods`, with no machine/LXD equivalent, despite the architecture doc stating the charm supports both substrates and `charmcraft.yaml` using `type: charm`.
- **Impact**: An operator following the tutorial on a machine cloud has no guidance without kubectl-equivalent instructions.
- **Fix**: Add a machine/LXD section, or a prominent note that the tutorial is Kubernetes-specific and machine deployment follows the same `juju status`-driven pattern.
- **Linter rule**: not mechanically checkable.

### 8. Untested secret revoke on password removal

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/charm.py:105` (`secret.revoke(relation=relation)`)
- **Evidence**: Coverage line 105 missed. This line runs when a peer secret exists and config changes to remove the password (`new_data.password_id` becomes `None`), and the secret should be revoked from existing relations. No unit test sets up this scenario.
- **Impact**: If this path regresses, a relation retains access to the peer secret after the password is removed.
- **Fix**: Add a test that establishes a relation with a password, removes the password config, and asserts `secret.revoke` is called on the relation.
- **Linter rule**: not mechanically checkable.

### 9. Untested `_on_relation_broken` leader path (`secret.revoke`)

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/charm.py:157` (`secret.revoke(event.relation)` inside the `if self.unit.is_leader()` block)
- **Evidence**: Coverage line 154 missed. The existing test `test_provider_charm_revoke_secret_on_broken` verifies the side effect via `harness.remove_relation()`, but Harness's own cleanup may trigger the revoke rather than the charm's handler; the leader-vs-non-leader path and the direct `secret.revoke` call are not asserted separately.
- **Impact**: If this path regresses, a relation retains secret access after being broken.
- **Fix**: Add a test that sets `harness.set_leader(True)` and explicitly verifies `secret.revoke` is called with the correct relation in `_on_relation_broken`.
- **Linter rule**: not mechanically checkable.

### 10. `parse_recipients` bracketless/JSON `ValueError` and `TypeError` paths untested

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `lib/charms/smtp_integrator/v0/smtp.py:537, 547, 554`
- **Evidence**: Coverage misses lines 537 (`TypeError("recipients must be a string, list, or None")`), 547 (`ValueError` in the JSON-list branch), and 554 (`ValueError("recipients must decode to a list")` in the bracketless JSON branch). Existing tests cover the happy path for bracketless JSON but not the error paths.
- **Impact**: If bracketless JSON parsing raises at runtime for unexpected external provider input, no test would catch a regression.
- **Fix**: Add tests exercising `parse_recipients` with a non-string/non-list input (should raise `TypeError`) and JSON that decodes to a non-list (should raise `ValueError`, both branches).
- **Linter rule**: not mechanically checkable.

### 11. `skip_ssl_verify` stored as string `"True"/"False"` not JSON `true`/`false`

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/smtp_integrator/v0/smtp.py:200` (`to_relation_data`), `smtp.py:283–286` (event property)
- **Evidence**: `to_relation_data` writes `str(self.skip_ssl_verify)` → `"True"`/`"False"`; the event property decodes with `literal_eval()`. Juju relation data conventions favour bare JSON booleans.
- **Impact**: Non-Python consumers must special-case Python-style string booleans instead of JSON unmarshalling.
- **Fix**: Store with `json.dumps(self.skip_ssl_verify)` → `true`/`false`.
- **Linter rule**: "Boolean fields in relation data should use JSON `true`/`false`, not string `'True'`/`'False'`" — mechanically checkable.

### 12. Untested `to_relation_data` `smtp_sender` branch

- **Severity**: low
- **Kind**: test-gap
- **Where**: `lib/charms/smtp_integrator/v0/smtp.py:214` (`if self.smtp_sender: result["smtp_sender"] = str(self.smtp_sender)`)
- **Evidence**: Coverage line 115 missed. No unit test calls `to_relation_data()` with `smtp_sender` set; only the end-to-end integration test exercises this field.
- **Impact**: A regression in this transformation would only be caught by integration tests.
- **Fix**: Add a unit test creating `SmtpRelationData(smtp_sender="no-reply@example.com")` and asserting `result["smtp_sender"]`.
- **Linter rule**: not mechanically checkable.

### 13. `_on_secret_changed` `ModelError` catch and `secret.id` access untested

- **Severity**: low
- **Kind**: test-gap
- **Where**: `lib/charms/smtp_integrator/v0/smtp.py:464–465, 468`
- **Evidence**: Coverage misses lines 464–465 (`except ops.ModelError: continue`) and 468 (`secret_uri = secret.id`). The existing test monkeypatches the requirer-side `model.get_secret` to always raise, which exercises a different code path than `_on_secret_changed`'s own try/except and `secret.id` read.
- **Impact**: If `secret.id` returns unexpectedly or `ModelError` occurs on this path, it is not exercised by tests.
- **Fix**: Add a test where `get_secret` succeeds and the `secret.id` read is exercised.
- **Linter rule**: not mechanically checkable.

### 14. `_secret_uri_equal` fully-qualified URI branch untested

- **Severity**: low
- **Kind**: test-gap
- **Where**: `lib/charms/smtp_integrator/v0/smtp.py:444–445`
- **Evidence**: Coverage misses lines 454, 457. `test_secret_uri_equal` compares URIs that always differ in the ID part, so the `if "/" in left_without_protocol and "/" in right_without_protocol: return left_without_protocol == right_without_protocol` branch never runs.
- **Impact**: Comparing two fully-qualified secret URLs with different IDs is untested.
- **Fix**: Add a test case comparing two fully-qualified URIs with different IDs.
- **Linter rule**: not mechanically checkable.

### 15. Interface test skipped due to upstream bug

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/interface/test_smtp.py`
- **Evidence**: Entire test module decorated `@pytest.mark.skip` referencing an upstream issue; the `smtp` interface contract is never verified by CI.
- **Fix**: Track the upstream issue and re-enable when resolved.
- **Linter rule**: not mechanically checkable.

### 16. `parse_recipients` return type uses `list[str]` PEP 585 syntax against a stated Python 3.8 target

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/smtp_integrator/v0/smtp.py:506`
- **Evidence**: `def parse_recipients(raw: Any) -> list[str]:` uses PEP 585 generics (Python 3.9+), while `pyproject.toml` declares `target-version = ["py38"]` for black.
- **Impact**: Under strict type checking targeting Python 3.8, this annotation is invalid.
- **Fix**: Use `List[str]` from `typing`.
- **Linter rule**: checkable with `pyright --pythonversion 3.8` or an equivalent ruff rule scoped to py38 targets.

### 17. Redundant `and secret is not None` check

- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:104`
- **Evidence**: `if secret and not new_data.password_id and secret is not None:` — `if secret` already implies `secret is not None`.
- **Fix**: `if secret and not new_data.password_id:`
- **Linter rule**: not in ruff or pylint by default.

## Worth copying

- **Clean reconciler pattern with explicit error mapping** — `src/charm.py:62–70`: `_reconcile_event` wraps the reconciler in try/except mapping `CharmConfigInvalidError → BlockedStatus`, `NotReadyError → WaitingStatus`, success → `ActiveStatus`.
- **Leadership check at reconciler entry** — `src/charm.py:74–76`: `if not self.unit.is_leader(): return` at the top of `_reconcile()`.
- **Pydantic v1/v2 compatibility at module load time** — `lib/charms/smtp_integrator/v0/smtp.py:68–101`: decorator selected at import, not in hot validation paths; covered by a test monkeypatching pydantic to force the v1 path.
- **Secret lifecycle correctly managed** — `src/charm.py:94–108`: grant on relation join, revoke on relation broken, grant/revoke on config change as `password_id` appears/disappears; confirmed live on both k8s and machine.
- **Idempotent `update_relation_data`** — `lib/charms/smtp_integrator/v0/smtp.py:492–500`: only writes to databag when data actually changed (`dict(relation_data) != dict(new_data)`), avoiding spurious relation-changed events.
- **`parse_recipients` handles multiple input formats** — `lib/charms/smtp_integrator/v0/smtp.py:516–562`: normalises `None`, list, JSON string, JSON-without-brackets, comma-separated, and single-address inputs into a consistent `list[str]`.

## Common-practice notes

- **`type: charm`** (not `type: machine`): confirmed deployable on both k8s and machine substrates; the architecture doc correctly states both are supported.
- **ops framework**: ops 3.8.0, standard patterns throughout; `ops.testing.Harness` is used for testing (deprecated in ops 3.x but still the established ecosystem pattern).
- **Library versioning**: standard LIBID/LIBAPI/LIBPATCH convention, currently v0/21.
- **Testing**: 108 unit tests via `tox -e unit`; coverage 93% library / 96% charm. One critical path is not covered: `_validate_secret` when the secret exists but the charm cannot read it (raises `ModelError`, not `SecretNotFoundError`) — Harness-based tests always grant the secret before testing.
- **CI**: operator-workflows v24.0.0; integration tests target Juju 3.6 on `1.35-strict/stable`.
- **`assumes`**: `"juju >= 3.1.0"` declared; Juju 3.6 and 4.x both confirmed working.
- **`relation_changed` not observed on provider**: intentional — config changes propagate via `config_changed` → reconciler → `update_relation_data`, which fires `relation_changed` on the consumer.
- **No actions**: correct for a workloadless config-distribution charm; no `actions.yaml`.
- **Terraform module**: minimal but correct, with tests.

## Tests

### Unit tests — 108 passed, 40 warnings (`PendingDeprecationWarning` about Harness), 0 failures

Run with `tox -e unit` (PYTHONPATH set by tox to `lib` + `src`).

Coverage:
- `lib/charms/smtp_integrator/v0/smtp.py`: 93% (14 statements missed: 96–98, 115, 268–269, 454, 457, 464–465, 468, 537, 547, 554)
- `src/charm.py`: 96% (statements missed: 105, 154, 156→exit/pragma nocover)

Missed-line notes:
- **96–98** (pydantic v2 path): environment has pydantic v1, so this branch is never taken naturally; only exercised via monkeypatch in `test_smtp_module_imports_without_field_validator`, and even that doesn't cover the real v2 import path.
- **115, 268–269, 454/457, 464–465/468, 537/547/554**: as detailed in findings 3, 10, 12, 13, 14 above.
- **charm.py 105, 154**: as detailed in findings 8 and 9 above.

### Integration tests — 3 tests (CI only, not run in this review)

CI targets Juju 3.6 on `1.35-strict/stable`. All three assert actual relation data content (sender, recipients, auth_type), not just active/idle status. Uses `any-charm` (bundled copy of the smtp lib via `src-overwrite`) as the requirer. `test_relation` skips on Juju 2.x.

### Interface tests — skipped

`tests/interface/test_smtp.py` entirely `@pytest.mark.skip` due to an upstream bug — the `smtp` interface contract is not verified by CI.

### Linting

- `ruff --ignore E402`: clean (only D104 missing docstrings in `__init__.py` packages)
- `codespell`: clean
- `pyright`: 3 errors — `on` property override in `SmtpRequires` (intentional ops pattern), config value type mismatches (false positives, Pydantic raises on invalid input), `parse_recipients` return type using PEP 585 syntax on a py38-targeted project

## Docs

- **README.md**: clean, appropriate.
- **`docs/`**: complete — how-to (configure, contribute, upgrade), tutorial, reference (architecture, configurations, integrations) all present.
- **Getting-started tutorial**: valid for Kubernetes; machine users are left without a path (finding 7).
- **Contributing guide**: present, links to discourse and GitHub.
- **Terraform README**: adequate.
- **Security policy**: present.
- **`docs/how-to/upgrade.md`**: minimal but correct — "stateless charm, use juju refresh."
- **`docs/reference/charm-architecture.md`**: correctly states both k8s and machine are supported, but incorrectly lists `update-status` as an observed hook (finding 6).

## Open questions

1. **Peer secret retention**: the peer secret is never deleted, only access is revoked. On `password` config removal, the secret content remains in the peer databag (`secret.destroy()` is never called). Likely intentional to avoid churn, but unverified.
2. **Relation data staleness while Blocked**: may be an intentional "last-known-good is better than nothing" design, but is a security concern if credentials were compromised (see finding 5).
3. **`any-charm` on k8s**: the `any-charm` requirer is only published to machine clouds; no k8s-based smtp requirer was available on charmhub to test full k8s integration end-to-end. Secret and relation-data behaviour is identical to machine by code inspection and operator behaviour (unverified for k8s-specific requirer interaction).
