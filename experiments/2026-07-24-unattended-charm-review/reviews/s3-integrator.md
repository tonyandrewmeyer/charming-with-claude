# s3-integrator

A thin operator charm that acts as an S3 credential broker for consumer charms. It
stores S3 connection parameters (endpoint, bucket, region, credentials, TLS CA chain,
etc.) in its peer-relation databag and fans them out to any charm related over the
`s3-credentials` interface. The charm itself never connects to S3. Track 1 (this repo)
uses the peer-relation databag for credential storage; track 2 (separate
`object-storage-integrators` repo) uses Juju-native secrets.

**Verdict**: the code is clean, well-structured, and deploys correctly on both machine
(LXD) and Kubernetes. But it is not robust to bad input: four correctness bugs were
found and confirmed live on both substrates. The most serious is that a malformed
`tls-ca-chain` config value drives the charm into `ErrorStatus` instead of
`BlockedStatus` via an uncaught exception (three distinct exception types, one of
which — `ValueError` — is already tracked as issue #237, the other two are new).
Two further bugs mean `juju config --reset` on `tls-ca-chain` or
`experimental-delete-older-than-days` does not clear the peer databag, leaving stale
data behind; for the retention-days case this produces a `BlockedStatus` that cannot
be cleared by config alone. A maintainer should fix the missing try/except around the
`tls-ca-chain` parsing path first — it is a one-block change that resolves the
critical finding and is directly reachable by any operator typing a bad value.

| | |
|---|---|
| Repo | `canonical/s3-integrator` @ `051ef46` (2026-07-21) |
| Charms | s3-integrator (machine/k8s), application (integration test harness) |
| Substrate | machine (LXD) + Kubernetes (k8s) |
| Deployed | yes — concierge-lxd-4 (rev 628) + concierge-k8s-4 (rev 628) |
| Reviewed | 2026-09-01 |

## What it does

Deploy `s3-integrator`, configure S3 parameters via `juju config` or the
`sync-s3-credentials` action, then relate consumer charms to receive credentials over
the `s3-credentials` interface. The charm stores all parameters in its peer-relation
databag and fans them out to every connected requirer.

## Deployment log

**LXD (concierge-lxd-4, model rv-s3-integrator-test):**
```
juju deploy s3-integrator --channel 1/edge  # rev 628, local HEAD: 051ef46
# Machine juju-0da8e3-0 provisioned; ~6 min first-boot (snap refresh)
# Unit immediately: BlockedStatus("Missing parameters: ['access-key', 'secret-key']")
juju run s3-integrator/0 sync-s3-credentials access-key=test-key secret-key=test-secret
# Unit: ActiveStatus
juju config s3-integrator region=us-west-2 endpoint=s3.us-west-2.amazonaws.com bucket=test-bucket
# Unit: ActiveStatus
# Also set: s3-uri-style=path, s3-api-version=2006-03-01
# Test actions on non-leader (s3-integrator/2 after scale-up):
#   sync-s3-credentials -> fails with "The action can be run only on leader unit."
#   get-s3-connection-info -> succeeds, shows masked keys
# Scale up: juju add-unit s3-integrator/1 -> ~2 min, both ActiveStatus
# Scale down: juju remove-unit s3-integrator/1 -> removed
# juju refresh --channel 1/edge -> "already up-to-date" (no newer revision)
# juju relate s3-integrator data-integrator -> correctly rejected (incompatible interfaces)
# Application-charm (integration test harness) packed locally:
#   charmcraft pack (Ubuntu 22.04 managed LXD) -> application_ubuntu@22.04-amd64.charm
# Deployed application-charm to LXD model:
#   Machine juju-0da8e3-5 provisioned (~12 min from zero); application/1 active
# Related application:first-s3-credentials -> s3-integrator:s3-credentials:
#   Application received: bucket='MY-OPERATOR-BUCKET' (operator's config value)
#   Relation databag has operator's bucket, NOT requirer's 'relation-5'
# Related application:second-s3-credentials -> s3-integrator:s3-credentials:
#   Application received: bucket='test-bucket' (both operator and requirer set this)
# juju remove-application s3-integrator --force -> aborts (interactive confirmation,
#   cannot be suppressed even with --force; Juju CLI TTY limitation, not a charm bug)
# tls-ca-chain set with valid base64 cert: ActiveStatus
# tls-ca-chain confirmed in peer databag via get-s3-connection-info
# --reset tls-ca-chain: config cleared, BUT peer databag retains old cert value [BUG]
# experimental-delete-older-than-days=0: BlockedStatus
# experimental-delete-older-than-days=9999999 (MAX): ActiveStatus
# experimental-delete-older-than-days=10000000 (MAX+1): BlockedStatus
# experimental-delete-older-than-days=10000000 stored in peer databag
# --reset experimental-delete-older-than-days: config cleared, BUT peer databag
#   retains 10000000 -> persistent BlockedStatus [BUG] (cannot recover with config alone)
```

**Kubernetes (concierge-k8s-4, model rv-s3-k8s-test):**
```
juju deploy s3-integrator --channel 1/edge  # rev 628
# Pod s3-integrator-0: Running ~25s
# Unit: BlockedStatus("Missing parameters: ['access-key', 'secret-key']")
juju run s3-integrator/0 sync-s3-credentials access-key=k8s-key secret-key=k8s-secret
# Unit: ActiveStatus
# pebble present at /charm/bin/pebble but no Pebble layer defined -- pure operator
# Actions tested: sync-s3-credentials, get-s3-connection-info, get-s3-credentials -- all succeed
# Relation to application-k8s:first-s3-credentials established
# application-k8s went from waiting -> active
# juju remove-relation application-k8s s3-integrator: application-k8s -> waiting;
#   s3-integrator remained active
# Bad tls-ca-chain -> ErrorStatus (binascii.Error, UnicodeDecodeError) confirmed
# Recovery: juju config --reset && juju resolve
```

**Failure injection (both LXD and k8s):**
```
# Invalid base64 tls-ca-chain -> binascii.Error -> ErrorStatus, retries every 5s
# Valid base64, non-UTF-8 tls-ca-chain -> UnicodeDecodeError -> ErrorStatus, retries
# Invalid PEM tls-ca-chain -> ValueError -> ErrorStatus, retries
# recovery: juju config --reset tls-ca-chain && juju resolve s3-integrator/0 -> ActiveStatus
# Invalid experimental-delete-older-than-days=-5 -> BlockedStatus
# experimental-delete-older-than-days=0 -> BlockedStatus
# experimental-delete-older-than-days=10000000 (MAX+1) -> BlockedStatus
# juju relate s3-integrator data-integrator -> "no compatible endpoints found"
# cos-configuration-k8s deployed to k8s model -> no s3 interface, cannot relate
```

**Charmcraft local pack:**
```
charmcraft pack (s3-integrator): OK after LXD instance cleanup (prior "device already exists")
charmcraft analyse: entrypoint ERROR (false positive: ${dispatch_path} not expanded by analyse)
charmcraft analyse: juju-actions OK, juju-config OK, metadata OK, naming OK, pip-check OK
```

**Unit tests (PYTHONPATH=./src:./lib required):**
```
PYTHONPATH=./src:./lib python3 -m pytest tests/unit/test_charm.py -v
# 5 passed, 5 warnings (PendingDeprecationWarning for Harness)
# Branch coverage on src/charm.py: 58% (105/169 statements missed)
```

## Observed behaviour

| Scenario | Expected | Observed |
|---|---|---|
| Deploy without credentials (LXD) | BlockedStatus | BlockedStatus("Missing parameters: ...") |
| Deploy without credentials (k8s) | BlockedStatus | BlockedStatus("Missing parameters: ...") |
| `sync-s3-credentials` action | ActiveStatus | ActiveStatus (LXD + k8s) |
| `get-s3-connection-info` action (with creds) | Masked keys | Masked keys shown (LXD + k8s) |
| `get-s3-connection-info` action (without creds) | Action fails | Action fails |
| `get-s3-credentials` action (without creds) | Action fails | Action fails |
| `sync-s3-credentials` from non-leader | Action fails | "The action can be run only on leader unit." |
| `get-s3-connection-info` on non-leader | Shows data | Masked keys shown |
| Config change (region, bucket, endpoint, s3-uri-style, s3-api-version) | ActiveStatus | ActiveStatus |
| `tls-ca-chain` invalid base64 (LXD/k8s) | BlockedStatus | **ErrorStatus** — `binascii.Error`, retries every 5s |
| `tls-ca-chain` valid base64, non-UTF-8 (LXD/k8s) | BlockedStatus | **ErrorStatus** — `UnicodeDecodeError`, retries every 5s |
| `tls-ca-chain` valid base64, no certs (LXD/k8s) | BlockedStatus | **ErrorStatus** — `ValueError`, retries every 5s |
| `experimental-delete-older-than-days=-5` | BlockedStatus | BlockedStatus |
| `experimental-delete-older-than-days=0` | BlockedStatus | BlockedStatus |
| `experimental-delete-older-than-days=9999999` (MAX) | ActiveStatus | ActiveStatus |
| `experimental-delete-older-than-days=10000000` (MAX+1) | BlockedStatus | BlockedStatus |
| Empty `bucket` config | ActiveStatus | ActiveStatus (key removed from peer databag) |
| Empty `region`/`storage-class`/`path` config | ActiveStatus | ActiveStatus (key removed from peer databag) |
| Empty `access-key` config | Silently ignored | Silently ignored (KEYS_LIST guard) |
| `attributes=""` (empty string) | ActiveStatus | ActiveStatus |
| `attributes="a1:v1,a2:v2"` | Stored as list | Stored as `["a1:v1", "a2:v2"]` |
| `attributes="a1: v1 , a2:v2"` (whitespace) | Stored as-is | Stored as `["a1: v1 ", "  a2:v2"]` (not trimmed) |
| Non-integer `experimental-delete-older-than-days` | Rejected by Juju | "expected int, got 'abc'" (Juju-level validation) |
| `sync-s3-credentials` update creds | ActiveStatus | ActiveStatus |
| Scale up to 2 units (LXD) | Both ActiveStatus | Both ActiveStatus; peer databag shared |
| Scale down to 1 unit (LXD) | Remaining ActiveStatus | Remaining ActiveStatus |
| `juju resolve` + `--reset tls-ca-chain` after bad tls-ca-chain | Recovers | Recovers to ActiveStatus (LXD + k8s) |
| `juju refresh --channel 1/edge` | No newer rev | "already up-to-date" |
| `juju relate s3-integrator data-integrator` | Fails | "no compatible endpoints found" |
| Relation creation: application-k8s relates to s3-integrator | application -> active | application-k8s: waiting -> active |
| Relation removal: `juju remove-relation` | application -> waiting | application-k8s: active -> waiting; s3-integrator stays active |
| Machine provisioning (first unit, LXD) | — | ~6 min (first-boot snap refresh) |
| Machine provisioning (second unit, LXD) | — | ~2 min (no snap refresh on subsequent units) |
| Application-charm relate (first-s3-credentials, operator bucket set) | Requirer gets operator's bucket | `bucket='MY-OPERATOR-BUCKET'` |
| Application-charm relate (second-s3-credentials, bucket=test-bucket) | Both operator & requirer set test-bucket | `bucket='test-bucket'` |
| LXD machine from zero | — | ~12 min (machine 5, application-charm) |
| `tls-ca-chain` set, then `--reset tls-ca-chain` | Peer databag cleared | **Peer databag retains old value** |
| `experimental-delete-older-than-days=10000000` set, then `--reset` | Peer databag cleared | **Persistent BlockedStatus** (cannot recover via config alone) |
| `experimental-delete-older-than-days` BlockedStatus message | Shows current config value | Shows **peer databag value** (misleading when config was reset) |

## Findings

### `tls-ca-chain` config raises uncaught exceptions, causing ErrorStatus instead of BlockedStatus

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:126-130`
- **Evidence**: The `tls-ca-chain` config path has three uncaught exception types:
  1. `binascii.Error` — malformed base64 (`Incorrect padding`); confirmed on LXD (08:38:41) and k8s (08:54:37).
  2. `UnicodeDecodeError` — decoded bytes are not valid UTF-8 (`'utf-8' codec can't decode byte 0xff in position 0`); confirmed on LXD (08:39:12) and k8s (08:55:01) using base64 of `bytes([0xff, 0xfe, 0xfd])`.
  3. `ValueError` — decoded string contains no certificates (`No certificate found in chain file`), known issue #237.

  All three propagate uncaught through `_on_config_changed`, causing the hook to exit
  with status 1. The unit enters `ErrorStatus` and the hook retries every ~5 seconds.
  Recovery requires `juju config --reset tls-ca-chain && juju resolve <unit>`.
- **Impact**: Any operator who supplies a malformed `tls-ca-chain` — wrong encoding,
  binary data, or a PEM with no certificates — gets an unrecoverable `ErrorStatus`
  loop instead of a clean `BlockedStatus`, and cannot fix it via config alone. The
  `ValueError` case is already tracked (#237); `binascii.Error` and `UnicodeDecodeError`
  are additional, previously unreported failure modes with the same root cause.
- **Fix**: Wrap the whole `tls-ca-chain` block in a try/except:
  ```python
  elif option == "tls-ca-chain":
      try:
          ca_chain = self.parse_ca_chain(
              base64.b64decode(self.config[option]).decode("utf-8")
          )
      except (ValueError, UnicodeDecodeError, binascii.Error) as e:
          logger.warning("Invalid CA chain: %s", e)
          self.unit.status = BlockedStatus(f"Invalid tls-ca-chain: {e}")
          return
      update_config.update({option: ca_chain})
      self.set_secret("app", option, json.dumps(ca_chain))
  ```
- **Linter rule**: "Hook handler must not let `ValueError`, `UnicodeDecodeError`,
  `binascii.Error`, `TypeError`, or `KeyError` propagate to the hook runner; set
  `BlockedStatus` instead." — mechanically checkable with a custom AST rule.

---

### `--reset tls-ca-chain` leaves stale value in peer databag (credential revocation incomplete)

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:77-138`
- **Evidence**: When `tls-ca-chain` is cleared (`self.config["tls-ca-chain"] == ""`),
  `_on_config_changed` hits `continue` and never calls
  `self.set_secret("app", "tls-ca-chain", None)`; the old value remains in the peer
  databag. Live confirmed (LXD, rev 628): after setting a valid `tls-ca-chain`,
  `get-s3-connection-info` shows two certificates; after `juju config --reset
  tls-ca-chain`, `get-s3-connection-info` **still** shows the same two certificates.
- **Impact**: An operator who revokes a CA chain via config reset believes the
  credentials are cleared, but requirers polling `get_s3_connection_info()` (rather
  than reacting to `credentials_changed`) continue to receive the revoked chain — a
  security-relevant data consistency issue.
- **Fix**: In the `tls-ca-chain` branch, handle the empty-string case explicitly:
  ```python
  elif option == "tls-ca-chain":
      if self.config[option] == "":
          self.set_secret("app", option, None)
          if self.s3_provider.relations:
              for relation in self.s3_provider.relations:
                  relation.data[self.app].pop(option, None)
          continue
      # existing try/except path for non-empty value
  ```
- **Linter rule**: not mechanically checkable without instrumentation.

---

### `--reset experimental-delete-older-than-days` leaves stale value, creating persistent BlockedStatus

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:100-105`
- **Evidence**: Setting `experimental-delete-older-than-days` to an invalid value
  (e.g. `10000000`, above `MAX_RETENTION_DAYS` of `9999999`) sets `BlockedStatus` and
  `continue`s without removing the stale value from the peer databag.
  `juju config --reset` does not trigger `config-changed`, so the stale value
  persists. `_on_peer_relation_changed` (fired on every peer-relation-changed event,
  including `update-status`) re-reads the peer databag, finds the stale value, and
  because it is not in `S3_MANDATORY_OPTIONS` the unit stays active — but the
  `BlockedStatus` message still shown before the reset references the stale value.
  Live confirmed (LXD, rev 628):
  ```
  juju config s3-integrator experimental-delete-older-than-days=10000000
  # -> BlockedStatus "Option delete-older-than-days value 10000000 outside allowed range"
  juju config s3-integrator --reset experimental-delete-older-than-days
  # -> Status still BlockedStatus "Option delete-older-than-days value 10000000..."
  ```
  Recovery requires setting a valid value (e.g. `experimental-delete-older-than-days=30`
  gives `ActiveStatus`); a config-only fix via `--reset` is impossible.
- **Impact**: An operator who sets an invalid retention value and tries to reset it
  via `juju config --reset` cannot recover without setting a valid replacement value.
  The reset appears to succeed (no error) but `BlockedStatus` persists — confusing
  and undocumented.
- **Fix**: Remove the stale value from the peer databag when the option is rejected:
  ```python
  if config_value > 0 and config_value <= MAX_RETENTION_DAYS:
      update_config.update({option: str(config_value)})
      self.set_secret("app", option, str(config_value))
      self.unit.status = ActiveStatus()
  else:
      logger.warning("Invalid value %s for config '%s'", config_value, option)
      self.set_secret("app", option, None)
      self.unit.status = BlockedStatus(
          f"Option {option} value {config_value} outside allowed range [1, {MAX_RETENTION_DAYS}]."
      )
  ```
- **Linter rule**: "Config options with restricted ranges must remove stale
  peer-databag values when the value is rejected, to allow `juju config --reset` to
  recover." — not mechanically checkable.

---

### Bucket-overwrite guard has inverted logic, writes spurious peer-databag keys

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:147-152`
- **Evidence**: Comment and code intent are inverted:
  ```python
  # if bucket name is already specified ignore the one provided by the requirer app
  if self.get_secret("app", bucket) is None:
      self.set_secret("app", "bucket", bucket)
  ```
  The lookup key is the **bucket value** (e.g. `"my-bucket"`), not the literal key
  `"bucket"`; it should check `get_secret("app", "bucket") is not None`.

  Live confirmation via requirer charm: operator set `bucket=MY-OPERATOR-BUCKET`;
  requirer proposed `relation-5`. After `relation-joined`, the application received
  `bucket='MY-OPERATOR-BUCKET'` — the correct end state (operator's value wins).
  However, `get_secret("app", "MY-OPERATOR-BUCKET")` returned `None`, so
  `set_secret("app", "MY-OPERATOR-BUCKET", "relation-5")` wrote a **spurious key**
  into the peer databag. That key is invisible to `get-s3-connection-info` (which
  only iterates `S3_OPTIONS`) and to `update_connection_info` (which only reads the
  peer databag's `"bucket"` key), so it survives indefinitely and unnoticed. When
  operator and requirer bucket names coincide, the bug is not observable at all
  except for the spurious key.
- **Impact**: The comment is directly wrong and the peer databag is polluted with a
  spurious key on every requirer join. If the peer databag is ever dumped or
  migrated, these extra keys will be present. One-character fix.
- **Fix**:
  ```python
  # if bucket name is already specified ignore the one provided by the requirer app
  if self.get_secret("app", "bucket") is None:
      self.set_secret("app", "bucket", bucket)
  ```
- **Linter rule**: "Secret key name must be a string literal, not a variable value."
  — mechanically checkable with a custom AST rule.

---

### `assert bucket is not None` in production hook handler

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:149`
- **Evidence**: `bucket` is always set (`get_secret` returns a string or `None`; if
  `None`, `event.bucket`, always a string from the S3 requirer library, is
  substituted), so the assert cannot fire under normal Juju operation. It only
  signals developer uncertainty about the logic.
- **Impact**: Dead assert in production code. If a future change introduces a path
  where `bucket` can be `None`, the result is an unhelpful `AssertionError -> ErrorStatus`.
- **Fix**: Remove the `assert`; if defensive checking is wanted:
  ```python
  if not bucket:
      logger.error("No bucket name available")
      return
  ```
- **Linter rule**: "No bare `assert` statements in production hook handlers." —
  mechanically checkable with ruff `SIM108`.

---

### BlockedStatus for invalid retention shows peer databag value, not current config value

- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:91-94`
- **Evidence**: After `juju config --reset experimental-delete-older-than-days`, the
  status message still reads `"Option delete-older-than-days value 10000000 outside
  allowed range"`. `10000000` comes from the peer databag, not the current (reset)
  config.
- **Impact**: Misleading status message implies the invalid config value is still
  set when it has been cleared.
- **Fix**: Show the value that was actually rejected at the time of the last
  `config-changed` run, or store the last-rejected value separately for display.
- **Linter rule**: not established.

---

### `S3Provider.update_connection_info` silently no-ops for missing relations

- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/data_platform_libs/v0/s3.py:336-349`
- **Evidence**:
  ```python
  def update_connection_info(self, relation_id: int, connection_data: dict) -> None:
      ...
      relation = self.charm.model.get_relation(self.relation_name, relation_id)
      if not relation:
          return  # silently returns, no logging
      ...
  ```
  If `relation_id` refers to a relation that no longer exists, the method returns
  silently. Calls from `sync-s3-credentials` (which iterates existing relations) are
  unaffected, but any call with a stale `relation_id` produces no warning.
- **Impact**: An operator seeing the action's `"ok"` success message would believe
  credentials were propagated when they were not.
- **Fix**:
  ```python
  if not relation:
      logger.warning("Relation %d not found, skipping update", relation_id)
      return
  ```
- **Linter rule**: "Methods that silently return on error should log a warning." —
  not mechanically checkable without data-flow analysis.

---

### `_on_peer_relation_changed` is not leader-guarded, causing redundant work on non-leaders

- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:218-226`
- **Evidence**: `_on_config_changed` is correctly leader-guarded
  (`if not self.unit.is_leader(): return`), but `_on_peer_relation_changed` is not.
  Every non-leader unit runs `get_missing_parameters()` (O(n) peer databag read) and
  sets `unit.status` on every peer-relation-changed event. On k8s, `update-status`
  runs every 5 minutes but does not itself fire `peer-relation-changed`, so the
  impact is limited to actual peer databag changes, but the reads are still
  unnecessary on non-leaders.
- **Impact**: Redundant work on multi-unit deployments; the status write itself is
  harmless (each unit writes its own status).
- **Fix**: Add `if not self.unit.is_leader(): return` at the start of
  `_on_peer_relation_changed`.
- **Linter rule**: "Hook handlers that write shared state must be leader-guarded." —
  mechanically checkable (flag `self.app_peer_data` writes without a leader guard).

---

### `s3_list_options` duplicated in library and constants module

- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/data_platform_libs/v0/s3.py:337-338`, `:561-564` and `src/constants.py:25`
- **Evidence**: `S3Provider.update_connection_info` and
  `S3Requirer.update_connection_info` each hard-code
  `s3_list_options = ["attributes", "tls-ca-chain"]` locally; `src/constants.py`
  separately defines `S3_LIST_OPTIONS = ["attributes", "tls-ca-chain"]`. Three
  copies must be kept in sync manually.
- **Impact**: A future developer adding a new list-type option to the charm would
  need to update the constant and both library copies; forgetting the library copy
  causes `update_connection_info` to JSON-serialize the new option incorrectly
  (wrapping it in an extra layer).
- **Fix**: Import `S3_LIST_OPTIONS` from `constants` into the library, or pass it as
  a parameter to `update_connection_info`.
- **Linter rule**: "Hard-coded lists that duplicate module-level constants are a
  maintenance hazard." — partially checkable with ruff `F811` if the constant is
  imported but unused.

---

### No upgrade-charm hook handler

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py` (missing handler)
- **Evidence**: No `upgrade-charm` handler exists. `_on_start` checks for missing
  mandatory parameters but does not re-validate
  `experimental-delete-older-than-days` or other restricted-range options.
- **Impact**: If an upgrade introduces a new restricted option or a tightened range,
  a stale peer-databag value would not be detected until `config-changed` or
  `peer-relation-changed` next fires.
- **Fix**:
  ```python
  def _on_upgrade_charm(self, event: UpgradeCharmEvent) -> None:
      if not self.unit.is_leader():
          return
      self._on_config_changed(ConfigChangedEvent())
  ```
- **Linter rule**: "Charms with restricted-range config options should have an
  upgrade-charm handler that re-validates stored values." — not mechanically checkable.

---

### `CredentialsGoneEvent` lacks `bucket` property that sibling events have

- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/data_platform_libs/v0/s3.py:49`
- **Evidence**: `CredentialsChangedEvent` extends `S3Event`, which has a `bucket`
  property. `CredentialsGoneEvent` extends `RelationEvent` directly and has no
  `bucket` property. The application-charm test harness does not access `bucket` in
  its `credentials_gone` handler, so this has not been observed to fail in practice.
- **Impact**: A consumer charm accessing `event.bucket` in a `credentials_gone`
  handler gets `AttributeError`. Inconsistent event interface within the same family.
- **Fix**:
  ```python
  @property
  def bucket(self) -> Optional[str]:
      if not self.relation.app:
          return None
      return self.relation.data[self.relation.app].get("bucket")
  ```
- **Linter rule**: "All events in the same event family must have the same property
  interface." — not mechanically checkable.

---

### `diff()` function has known race condition on side-effect write (DPE-412)

- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/data_platform_libs/v0/s3.py:164-193`
- **Evidence**: `event.relation.data[bucket].update({"data": json.dumps(new_data)})`
  writes the diff snapshot as a side effect of computing the diff. If the charm
  crashes or the hook exits before this line (e.g. due to the `parse_ca_chain`
  `ValueError`), the old snapshot is preserved but the actual relation data has
  changed, corrupting the next diff. Acknowledged in code: `# TODO: evaluate the
  possibility of losing the diff if some error happens in the charm before the diff
  is completely checked (DPE-412)`.
- **Impact**: Under the `tls-ca-chain` crash modes, if the error occurs between the
  `diff()` call and the snapshot write, diff tracking is corrupted; subsequent
  relation changes may not trigger expected `credentials_changed` events.
- **Fix**: Tracked upstream as DPE-412. Write the snapshot before processing, not after.
- **Linter rule**: not mechanically checkable.

---

### Unused imports in the S3 library (ruff F401)

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/data_platform_libs/v0/s3.py:119-121`
- **Evidence**: `import ops.framework` and `import ops.model` are unused —
  leftovers from the commented-out `_diff` method (lines 259-286). `ruff check
  lib/charms/data_platform_libs/v0/s3.py` exits 1.
- **Fix**: Remove the two imports (`ruff check --fix`).
- **Linter rule**: ruff `F401` already catches this.

---

### Dead code: commented-out `_diff` method in library

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/data_platform_libs/v0/s3.py:259-286` (commented)
- **Evidence**: An entire old `_diff` method is commented out, superseded by the
  module-level `diff()` helper.
- **Fix**: Delete the commented-out method.
- **Linter rule**: not mechanically checkable.

---

### Unit tests use deprecated `Harness` API

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py:16`
- **Evidence**: `self.harness = Harness(S3IntegratorCharm)` emits
  `PendingDeprecationWarning`. No tracked migration issue exists.
- **Fix**: Migrate to `Manager` (ops 3 testing API).
- **Linter rule**: not mechanically checkable.

---

### `charmcraft analyse` reports false-positive entrypoint error

- **Severity**: low
- **Kind**: lint
- **Where**: `dispatch` file
- **Evidence**: The dispatch file resolves its entrypoint via `$(realpath $0)` at
  runtime; `charmcraft analyse` reports
  `entrypoint: [ERROR] Cannot find the entrypoint file: '.../${dispatch_path}/src/charm.py'`
  because `${dispatch_path}` is not expanded by the static analyser. The charm runs
  correctly in Juju and was packed successfully.
- **Fix**: Not a charm bug; charmcraft should handle `$(...)` dispatch paths, or use
  a static dispatch path.
- **Linter rule**: not applicable (charmcraft issue).

---

### Spelling errors in `README.md`

- **Severity**: nit
- **Kind**: docs
- **Where**: `README.md:8`
- **Evidence**: `"allows to configure the S3 bucket informations using Juju actions,
  and it is publishes"` — "informations" should be "information"; "it is publishes"
  should read "it publishes" or "it is published".
- **Fix**: `s/informations/information/; s/it is publishes/it publishes/`
- **Linter rule**: `codespell` catches "informations".

---

### Typo in `config.yaml` description

- **Severity**: nit
- **Kind**: docs
- **Where**: `config.yaml:43`
- **Evidence**: `"backups happens imediatelly after finishing..."` — "imediatelly"
  should be "immediately".
- **Fix**: `s/imediatelly/immediately/`
- **Linter rule**: `codespell` catches "imediatelly".

---

### Grammar error in `config.yaml` description

- **Severity**: nit
- **Kind**: docs
- **Where**: `config.yaml:45`
- **Evidence**: `"When full backup expires, the all differential..."` — "the all"
  should read "all the".
- **Fix**: `s/the all/all/`
- **Linter rule**: not established.

## Test coverage gaps

| Untested code path | Evidence |
|---|---|
| `parse_ca_chain` with non-cert input → `ValueError` | Uncaught → ErrorStatus (live confirmed LXD + k8s) |
| `base64.b64decode` malformed input → `binascii.Error` | Uncaught → ErrorStatus (live confirmed LXD + k8s) |
| `decode("utf-8")` non-UTF-8 → `UnicodeDecodeError` | Uncaught → ErrorStatus (live confirmed LXD + k8s) |
| `if self.get_secret("app", bucket) is None:` (wrong key) | Spurious key written; end state correct (live confirmed) |
| `--reset tls-ca-chain` → peer databag not cleared | Peer databag retains old value after reset (live confirmed) |
| `--reset experimental-delete-older-than-days` → persistent BlockedStatus | Stale peer databag value causes persistent BlockedStatus (live confirmed) |
| `experimental-delete-older-than-days` boundary (0, MAX, MAX+1) | Partially tested; 0 and MAX+1 confirmed via live test |
| `_on_credential_requested` handler | No unit test assertions on relation data content |
| `_on_peer_relation_changed` handler | No unit test assertions on status changes |
| Clearing credentials via config while requirer is connected | Stale relation databag (unverified — not tested live) |
| `S3Provider.update_connection_info` for missing relation | Silent no-op (no warning logged) |
| `is_relation_broken` helper | Always returns `False` (live confirmed) |
| `CredentialsGoneEvent.bucket` property | Missing from event class |
| `diff()` race condition (DPE-412) | Snapshot write as side effect |
| Non-leader behavior for `sync-s3-credentials` action | Correctly fails (mock-based unit test) |
| Leader-only behavior for `_on_config_changed` | Correctly guarded (code review) |
| Bucket config update propagation to existing relation | Covered by integration test (cannot run in this environment) |
| `sync-s3-credentials` after relation removal | Not tested |
| `upgrade-charm` hook | Not defined (no handler) |
| `tls-ca-chain` with valid cert → peer databag updated | Live confirmed via `get-s3-connection-info` (shows cert chain) |

## Worth copying

- **Clean separation of concerns**: the charm is thin; all S3 provider logic lives in
  `charms.data_platform_libs.v0.s3`. The charm owns lifecycle and configuration, the
  library owns the wire protocol.
- **Status precedence in `_on_start`** (`src/charm.py:68-73`): checks missing
  mandatory parameters on every start, not just on config-changed, handling upgrades
  cleanly.
- **`get_secret`/`set_secret` abstraction** (`src/charm.py:161-182`): clean wrapper
  over the peer-relation databag that avoids direct `relation.data` calls in charm
  logic, easing a future migration to real Juju secrets (track 2).
- **`tox.ini` `test_charm_libs_path` exclusion**: correctly excludes vendored test
  charm libraries from lint/coverage, avoiding false positives.
- **`skip_missing_interpreters = True`** in tox.ini: prevents failures when a Python
  version is not installed.
- **Leader guard on `_on_config_changed`**: correctly ensures only the leader
  processes config changes and updates relations.
- **Integration test structure** (`tests/integration/`): well-structured, uses proper
  `pytest` patterns, has thorough assertions on relation data content (not just
  status polling), and includes both positive and negative test cases.
- **`is_relation_joined` helper**: correctly checks that both endpoints are present in
  the relation's endpoints list.
- **Juju-level type validation**: non-integer `experimental-delete-older-than-days`
  is rejected by Juju before reaching the charm.

## Common-practice notes

| Aspect | This charm | Ecosystem convention |
|---|---|---|
| Source layout | `src/charm.py`, `src/constants.py` (flat) | `src/charms/<name>/` subdir — **drifts** |
| Library layout | `lib/charms/data_platform_libs/v0/s3.py` (vendored) | Standard |
| Config structure | `config.yaml` + `constants.py` | Standard |
| Actions | `actions.yaml` + handler methods | Standard |
| Metadata | `metadata.yaml` with `provides`/`peers` | Standard |
| Python packaging | Poetry | Standard in newer charms |
| Testing harness | `ops.testing.Harness` (deprecated) | Migration to `Manager` in progress |
| Linter | ruff | Standard |
| Charmcraft version | 3 (migration done at commit 64f0754) | Standard for new charms |
| ops version | `^3.8.0` | Standard |
| CI | GitHub Actions with `canonical/data-platform-workflows` | Standard for canonical charms |
| Terraform module | Not present | Gap (tracked in issue #274) |
| Juju secrets | Not used (track 1 uses peer databag) | Intentional for track 1; track 2 uses native secrets |
| k8s deployment | Sidecar-less operator (charm container only, pebble in PATH but no workload layer) | Standard for pure-operator charms |
| Unit test PYTHONPATH | Requires `PYTHONPATH=./src:./lib` | Convention: `tox` handles this, `pytest` alone fails |
| Integration test charm | Packaged locally for CI | Standard for integration test harnesses |
| Hard-coded list options | Duplicated in library AND `constants.py` | Maintenance hazard — not standard |

## Tests

| Suite | Type | Run result | Notes |
|---|---|---|---|
| `tests/unit/test_charm.py` | Unit (Harness, deprecated) | 5/5 PASS | 58% branch coverage on `src/charm.py`; large gaps (see above) |
| `tests/integration/test_s3_charm.py` | Integration (pytest-operator) | Cannot run against Juju 4.x — `pytest-operator 0.37.0` doesn't support Juju `4.0.12`; Juju 3.6 LXD provisioning too slow for a full CI-style run in this environment | Thorough; tests relation lifecycle, config propagation, actions with real assertions; would catch the credential-clearing bug |
| `tests/spread/` | End-to-end | Not run | Single spread test: runs integration tests via tox |

```
PYTHONPATH=./src:./lib python3 -m pytest tests/unit/ -v
# 5 passed, 5 warnings in 0.19s (PendingDeprecationWarning for Harness)
ruff check src/charm.py: All checks passed
ruff check lib/.../s3.py: 2 errors (F401 unused imports: ops.framework, ops.model)
codespell README.md: "informations" flagged
codespell config.yaml: "imediatelly" flagged
charmcraft analyse s3-integrator.charm:
  entrypoint: [ERROR] (false positive -- ${dispatch_path} not expanded by analyse)
  juju-actions: [OK]
  juju-config: [OK]
  metadata: [OK]
  naming-conventions: [OK]
  pip-check: [OK]
  pydeps: [OK]
```

The unit test suite is thin: 5 tests, no parametrization, no assertions on several
critical code paths (see Test coverage gaps above). The integration tests are
thorough but blocked by the pytest-operator/Juju version mismatch in this
environment (unverified whether they pass in the project's own CI, though commit
history is consistent with passing checks there).

## Docs

- **README.md**: good overview, covers deploy-from-source and deploy-from-charmhub,
  action examples, relation examples. Duplicated "Configuring the Integrator"
  section. Two spelling/grammar errors (see findings).
- **charmhub description**: matches the README closely and is consistent with
  observed behaviour.
- **CONTRIBUTING.md**: present, standard canonical template.
- **SECURITY.md**: present.
- **`config.yaml` descriptions**: contain a spelling error ("imediatelly") and a
  grammar error ("the all").
- **docs URL** (`discourse.charmhub.io/t/s3-integrator-documentation/10947`): not
  checked (network access required).

## Open questions

1. **Bucket-overwrite bug intent**: the comment says "ignore the one provided by the
   requirer app" but the code always processes the bucket and writes a spurious key
   to the peer databag. The end state (operator's bucket in the relation databag) is
   correct when values differ. Maintainers should confirm the intended semantics.
2. **ops 3 `Manager` migration**: unit tests use the deprecated `Harness`. No tracked
   migration issue exists.
3. **Track 1 end-of-life**: README states `latest/stable` will be removed after
   26.10. Is track 1 still receiving bug fixes, or is it in maintenance mode?
4. **Terraform module** (issue #274): not present; tracked as an enhancement request.
5. **DPE-412 side-effect race**: the `diff()` snapshot write is a known issue, and it
   is triggerable by any of the three `tls-ca-chain` crash modes.
6. **Integration test portability**: can the `application-charm` test harness be
   published to charmhub so integration tests can run without local charm packing?
7. **pytest-operator / Juju 4.x**: integration tests fail against Juju `4.0.12`.
   `pyproject.toml` requires `pytest-operator = "^0.43.2"` and `juju = "^3.5.2.0"`,
   but the environment used for this review has `pytest-operator 0.37.0` installed.
8. **BlockedStatus recovery after invalid retention**: the stale peer-databag value
   cannot be cleared by `juju config --reset` (reset doesn't trigger config-changed).
   Is there a Juju-recommended pattern for this, or should the charm add an
   upgrade-charm handler that re-validates all restricted options?
</content>
