# landscape-debarchive-operator

A thin machine charm that installs the `landscape-debarchive` snap, manages its
configuration, and bridges it to PostgreSQL, an HAProxy front end, and
Landscape Server. All workload logic lives in the proprietary snap; the charm
itself is a config/relation shim. The code is clean and action error-handling
is good, but the charm is not production-ready: the published Charmhub
revision does not pin the snap revision (so `snap refresh`/`--hold=forever`
can silently jump to a different snap version), none of the three relations
have `relation-broken`/`relation-departed` handlers (the hooks do fire —
Juju dispatches them regardless — but nothing runs, so stale config and
secrets are left behind), `gateway-port` accepts out-of-range values with no
validation, CI is broken (29 of 75 unit tests fail because `ops>=3,<4`
resolves to 3.0.0 while `ops.testing.Context` needs 3.1.0), and
`_on_config_changed` can raise an unhandled `ValueError` out of
`_provide_haproxy_route_requirements()`. `start()` is an unimplemented stub.
A maintainer should first fix the CI pin (`ops>=3.1,<4`, one-line), then
publish a Charmhub revision that includes `src/snap_revisions.json`, then add
the three missing relation-broken handlers.

| | |
|---|---|
| Repo | canonical/landscape-debarchive-operator @ `5c7abd5` (2026-07-07) |
| Charms | landscape-debarchive |
| Substrate | machine (LXD) |
| Deployed | yes — concierge-lxd-4 (Juju 4.0.12, locally-packed rev 0); concierge-lxd (Juju 3.6.27, Charmhub edge rev 2) |
| Reviewed | 2026-08-19 |

## What it does

Installs the `landscape-debarchive` snap from the `edge` channel (locally
packed charm with `snap_revisions.json`) or `beta` channel (Charmhub
published charm rev 2, no revision pin); configures gateway port, log level,
and log format from Juju config; connects to PostgreSQL via the
`data_platform_libs` requirer; provides HAProxy route requirements via the
`haproxy-route` requirer; and receives a JWT secret token and hostname from a
`landscape-server` charm over a custom interface and Juju secret. Exposes
four actions: `show-config` (redacted), `check-health`, `show-version`,
`restart-snap`.

## Deployment log

### Juju 4.0.12 controller (concierge-lxd-4)

1. Model `rv-landscape-debarchive` created.
2. `juju deploy landscape-debarchive --channel edge` — deployed Charmhub rev 2.
3. Machine boot: pending ~90 s (00:04:59 → 00:06:26 for install hook).
4. Hooks fired: install → leader-elected → config-changed → start, all completed without error.
5. Unit active: version 283 (Charmhub rev 2, no snap revision pin), tracking `latest/beta`.

**Refresh to local charm**: `juju refresh --path=<local-charm>` upgraded to
locally-packed charm rev 0. `_on_upgrade_charm` fired, called
`debarchive.refresh()` → snap changed from rev 283 (beta) to rev 258 (edge,
pinned). Unit went `maintenance` ("refreshing workload snap") then back to
`active`; `juju status` version updated to 258. Confirms: (a) the upgrade
path works, (b) the published charm installs from beta with no revision pin,
(c) the local charm's `snap_revisions.json` pins correctly.

### Juju 3.6.27 controller (concierge-lxd)

1. Model `rv-landscape-debarchive-lxd3` created.
2. PostgreSQL deployed first: rev 1162, channel `14/stable`, ubuntu@22.04.
3. `landscape-debarchive` deployed at the same Charmhub rev 2.
4. `juju integrate landscape-debarchive:database postgresql:database`.
5. Both active: postgresql at `10.5.87.169:5432`; landscape-debarchive correctly received database credentials.
6. `juju remove-relation` — database config left stale in the snap (see Findings).

**Config changes tested**:
- `juju config log-level=debug gateway-port=8200` → snap config updated, `ActiveStatus` ✓
- `juju config log-level=verbose` → `BlockedStatus "Invalid log-level; expected debug, warn, error, info, trace, fatal"` ✓
- `juju config gateway-port=abc` → rejected by Juju type validation (`expected int, got "abc"`) ✓
- `juju config log-level=DEBUG` → accepted, normalized to lowercase `debug` by `configure()` (`src/debarchive.py:136`), snap config shows `"level": "debug"`, `ActiveStatus` ✓
- `juju config gateway-port=0` → **silently accepted**, snap config writes `gateway-port: "0"`, `ActiveStatus` ✓
- `juju config gateway-port=65536` → **silently accepted**, snap config writes `gateway-port: "65536"`, `ActiveStatus` ✓

**Actions tested on both units**:
- `show-config` → redacted correctly ✓
- `check-health` → `{"healthy": false, "message": "debarchive snap service is not active"}` ✓
- `show-version` → correct snap version/revision/channel ✓
- `restart-snap` → `{"restarted": "true"}` ✓

**`juju remove-application`**: machine destroyed cleanly, model empty; re-deploy after removal worked correctly with a fresh machine and clean install.

**`juju remove-relation` and `relation-broken` observation** (Juju 3.6):
- `database-relation-departed` hook fired ✓
- `database-relation-broken` hook fired ✓
- Charm went `ActiveStatus` despite no handler for either hook
- Snap config still showed old database credentials after both hooks completed

**HAProxy integration attempted**: Charmhub `haproxy` (rev 147, stable) exposes `reverseproxy`, not `haproxy-route`. No integration possible with that revision. The integration test suite uses `haproxy --channel 2.8/edge`, which may expose `haproxy-route`, but that revision was not available/testable in this environment.

## Observed behaviour

### Service inactive after deploy — `start()` is a stub
The `debarchive` service stays `inactive` after the charm reaches
`ActiveStatus`. `start()` in `src/debarchive.py:103` is a stub:

```python
def start() -> None:
    """Start the workload (by running a commamd, for example)."""
    # You'll need to implement this function.
```

`_on_start()` (`src/charm.py:99`) calls `debarchive.start()`, which does
nothing. The snap's `restart-condition: on-failure` means the service won't
start until the landscape-server relation supplies the JWT secret — likely
intentional, but the stub comment and the hook name suggest otherwise.

### ActiveStatus despite missing required relations
Both `_on_start` and `_on_config_changed` set `ActiveStatus` unconditionally,
never checking whether `database` or `landscape-server` relations exist.
Observed on both controllers: `active` status while the workload is not
running.

### Snap revision mismatch — confirmed on both controllers
The locally-packed charm (HEAD `5c7abd5`) ships `src/snap_revisions.json`
pinning snap revision 258 for amd64; the Charmhub-published charm (rev 2)
does not. After `juju refresh --path=<local-charm>` on Juju 4: snap changed
from rev 283 to rev 258 (edge, pinned) — a different version entirely, and
`juju status` reflected it.

### Database relation works but leaves stale config on removal
Tested on Juju 3.6 with postgresql 14.23. After integration, `show-config`
showed `host: 10.5.87.169`, `name: debarchive`, `user: relation-5`, `ssl:
disable` (`ssl: disable` is correct: the postgresql charm doesn't enable TLS
by default, `event.tls` is `None`, and `str(None).lower() = "none"` ≠
`"true"` → `ssl = "disable"` — the TLS comparison logic itself is correct).

After `juju remove-relation`:
- `database-relation-departed` fired at 00:54:36 ✓
- `database-relation-broken` fired at 00:54:37 ✓
- `show-config` **still showed the old credentials** (`host: 10.5.87.169`, `user: relation-5`) after both hooks completed
- Charm went `ActiveStatus` with no indication of stale config
- Confirmed by grep: no `database-relation-departed`/`-broken` handler in `src/charm.py:37-50`

Same pattern for the landscape-server and haproxy-route relations: no
`relation-departed`/`relation-broken` handler, and `_stored` values
(`hostname`, `secret_token`) are never cleared on relation removal.

### `relation-broken` hooks fire whether or not the charm has a handler
Juju dispatches the hook regardless of charm-side handling. Debug log (Juju
3.6):
```
unit-landscape-debarchive-0: 00:54:36 INFO ... ran "database-relation-departed" hook
unit-landscape-debarchive-0: 00:54:37 INFO ... ran "database-relation-broken" hook
unit-landscape-debarchive-0: 00:54:37 INFO juju.worker.uniter.relation unknown relation 5 resolving next op
```
Both hooks ran to completion and did nothing, because the charm has no
handler.

### `HaproxyRouteRequirer` fires `on.removed` on relation-broken; charm ignores it
`lib/charms/haproxy/v1/haproxy_route.py:1114-1118`:
```python
def _on_relation_broken(self, _: RelationBrokenEvent) -> None:
    """Handle relation broken event."""
    self.on.removed.emit()
```
The charm observes `self.debarchive_haproxy_route.on.ready` (`src/charm.py:61`)
but not `.on.removed`. When the relation breaks, the event fires into a void.
(The library's `data_removed` event on the provider side is informational
only and not equivalent to relation removal.)

### Config-changed hook count
Three `config-changed` hooks fired for three config changes (gateway-port +
log-level × 2). A scale-up triggered `config-changed` on both units
simultaneously; each hook completed in under 1 s.

### Scale behaviour
Scale-up (1→2): second machine provisioned in ~3 min, install hook ~90 s,
both units active, no peer-relation issues. Scale-down (2→1): unit removed
cleanly.

### `snap refresh --hold=forever` without a pinned revision
Run on the deployed unit (rev 283, beta, no pinned revision): the snap
changed to the `edge` channel's latest revision (258, version 0.4.0), not the
version that had been running (0.9.1). The hold applied to rev 258, but the
version jumped underneath the operator's feet. This is the core operational
risk of the published charm.

### `gateway-port` accepts out-of-range values silently
Juju validates the type (`type: int`) but not the range.
`configure()` (`src/debarchive.py:138`) validates log level but has no port
range check. Both `gateway-port=0` and `gateway-port=65536` were accepted,
written to snap config (`gateway-port: "0"` / `"65536"`), and the charm went
`ActiveStatus` with no feedback. The invalid value persisted after a
subsequent `juju refresh` to the local charm.

## Findings

Ordered by severity.

### 1. Published charm's snap install is unpinned — `snap_revisions.json` missing from Charmhub
- **Severity**: high
- **Kind**: bug
- **Where**: `src/snap_revisions.json` (added in `5c7abd5`, absent from Charmhub rev 2)
- **Evidence**: Deployed snap is rev 283 tracking `latest/beta` on both controllers. Local source has `{"channel": "edge", "revision": "258"}`. The published charm's `SNAPS_TO_INSTALL` has `{"channel": "beta"}` with no revision key. Unpacking the locally-built charm confirms `src/snap_revisions.json` is present with `{"landscape-debarchive": {"amd64": "258", "arm64": "259"}}`. After `juju refresh --path=<local-charm>`, the snap changed from rev 283 to rev 258, confirming the pin takes effect when present.
- **Impact**: Without a pinned revision the snap can auto-refresh; worse, `snap refresh --hold=forever` on an unpinned snap jumped from beta/283 to edge/258 — a different version (0.9.1 → 0.4.0). Hold can only protect a specific revision; without one it's a land mine, not a safety net.
- **Fix**: Re-publish the charm to Charmhub so it includes `snap_revisions.json`. Ensure CI publishes after every commit touching that file.
- **Linter rule**: not mechanically checkable without publishing and re-inspecting.

### 2. No relation-broken/relation-departed handlers for any of the three relations
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:34` (`_stored`), `src/charm.py:37-60` (no handlers registered for database/landscape-server/haproxy-route broken/departed)
- **Evidence**: `grep -n "relation-departed\|relation-broken" src/charm.py` returns nothing. After `juju remove-relation landscape-debarchive:database postgresql:database` on Juju 3.6: `database-relation-departed` (00:54:36) and `database-relation-broken` (00:54:37) hooks fired but `show-config` still showed the old credentials, and `_stored.hostname`/`_stored.secret_token` were never cleared. `data_platform_libs` (`lib/charms/data_platform_libs/v0/data_interfaces.py`) does not emit library-level events on relation removal (only `database_created`, `endpoints_changed`). `HaproxyRouteRequirer` does emit `self.on.removed` on relation-broken (`lib/charms/haproxy/v1/haproxy_route.py:1116-1118`), but the charm does not observe it.
- **Impact**: When the database relation is removed, the snap retains old credentials; if a new database is later related, `_provide_haproxy_route_requirements()` checks only whether `_stored.hostname` is already set and won't re-publish with a new hostname. The charm is left in a confused state with no signal to the operator.
- **Fix**: Add handlers for `database-relation-broken`, `landscape-server-relation-broken`, and `haproxy-route-relation-broken`. Each should clear the relevant snap config and reset `_stored` values.
- **Linter rule**: "Relation handlers exist for `relation_joined`/`relation_changed` but not `relation_departed`/`relation_broken`" — checkable by static analysis.

### 3. 29 of 75 unit tests fail — `ops` version mismatch
- **Severity**: high
- **Kind**: test-gap
- **Where**: `pyproject.toml` (`ops>=3,<4`), `tests/unit/test_charm.py`
- **Evidence**: `ops>=3,<4` resolves to ops 3.0.0; `ops.testing.Context` was introduced in 3.1.0. All 29 tests in `TestCharmInstallAndStartup`, `TestCharmUpgrade`, `TestCharmConfigChanged`, `TestDatabaseRelation`, `TestLandscapeServerRelation`, `TestHaproxyRouteRelation` fail with `AttributeError: module 'ops.testing' has no attribute 'Context'`. 46 `Harness`-based tests pass.
- **Impact**: 39% of the test suite cannot run, and it is exactly the suite covering install, upgrade, config-changed, and all three relation handlers — the highest-risk code.
- **Fix**: Change `pyproject.toml` from `"ops>=3,<4"` to `"ops>=3.1,<4"`. System Python has ops 3.6.0, which has `Context`, so the tighter constraint is unnecessarily loose.
- **Linter rule**: not applicable.

### 4. CI pipeline broken — same failures land in the pipeline
- **Severity**: high
- **Kind**: test-gap
- **Where**: `pyproject.toml`, `.github/workflows/unit-test.yaml`
- **Evidence**: The CI workflow runs `uv sync` from `pyproject.toml`, installing ops 3.0.0, then `make test` → `tox -e unit` → `coverage run ... pytest tests/unit/`. Pytest exits non-zero when any test fails. Verified locally: `PYTHONPATH=src:lib:deps/charmlibs .venv/bin/python -m pytest tests/unit/test_charm.py -v` → 29 failed, 46 passed.
- **Impact**: same 39% coverage loss as finding 3, but confirmed to be failing in CI, not just locally — the pipeline has been silently failing (or its failure has not been surfaced).
- **Fix**: same one-line change as finding 3.
- **Linter rule**: not applicable.

### 5. `start()` is a stub that doesn't start the workload
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/debarchive.py:103`
- **Evidence**: The function body is only a comment saying "You'll need to implement this function." Service stays `inactive` after deploy. `_on_start()` (`src/charm.py:99`) calls it and then sets `ActiveStatus` regardless. All tests covering `_on_start` monkeypatch `debarchive.start` to a `MagicMock`, so the stub is never exercised.
- **Impact**: The charm advertises a start hook that performs no start operation; `juju start landscape-debarchive`-style expectations are unmet.
- **Fix**: Either implement `start()` to call `debarchive.restart()`, or remove `_on_start` and document that the service is started once relations are established.
- **Linter rule**: "Hook handler does not perform the operation its name implies" — not mechanically checkable.

### 6. No WaitingStatus/BlockedStatus when required relations are absent
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:95` (`_on_start`), `src/charm.py:110` (`_on_config_changed`)
- **Evidence**: Both handlers set `ActiveStatus` unconditionally, never checking for `database`/`landscape-server` relations. Observed `active` status with the workload not running on both controllers.
- **Impact**: An operator must run `check-health` to discover a missing prerequisite that the status line should have surfaced.
- **Fix**: Check for required relations in `_on_config_changed`; set `WaitingStatus`/`BlockedStatus` accordingly and update when relations are added.
- **Linter rule**: "Charm sets ActiveStatus without verifying required relations are established" — not mechanically checkable.

### 7. `gateway-port` accepts out-of-range integer values without validation
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:113` (`_on_config_changed`), `src/debarchive.py:148` (port set), `src/debarchive.py:138` (log-level validated, for contrast)
- **Evidence**: `juju config gateway-port=0` and `gateway-port=65536` were both accepted, written into snap config, and left the charm `ActiveStatus`. `configure()` validates log level but has no port range check. `charmcraft.yaml`'s config schema uses `type: int` with no `range` constraint.
- **Impact**: A misconfigured `gateway-port` gets no feedback; the snap may fail silently or behave unexpectedly.
- **Fix**: Add a range check in `configure()` (`1 <= gateway_port <= 65535`, raising `ValueError` otherwise), optionally add `range: [1, 65535]` to the `charmcraft.yaml` schema.
- **Linter rule**: "Integer config value not validated against its valid range" — checkable by static analysis of schema vs. handler.

### 8. `configure()` returns silently when the snap is not present
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/debarchive.py:142`
- **Evidence**: `configure()` returns `None` early when `debarchive_snap.present` is `False`; confirmed by the `test_config_changed_snap_not_present` unit test — `snap.set` is not called, no error raised, charm goes `ActiveStatus`.
- **Impact**: If `config-changed` fires before install completes, or the snap is removed mid-deployment, the config change is silently dropped.
- **Fix**: Raise `snap.SnapNotFoundError` or set `BlockedStatus("debarchive snap not installed")` instead of returning silently.
- **Linter rule**: "Function returns without error when a required resource is absent" — mechanically checkable by static analysis.

### 9. `_on_config_changed` can raise an unhandled `ValueError` from `_provide_haproxy_route_requirements()`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:128` (called without its own exception handler), `src/debarchive.py:281` (`get_port()` does `int(debarchive_snap.get(...))`)
- **Evidence**: After the guarded `debarchive.configure()` call (`src/charm.py:120-126`), `_provide_haproxy_route_requirements()` runs unguarded. It calls `get_port()`, which does `int(snap.get("deb.archive.server.gateway-port"))`; if the key is absent, `snap.get()` returns `None` and `int(None)` raises `ValueError`.
- **Impact**: In the normal case the snap config is always written first, but if `configure()` returns early (finding 8) and this call still runs, the hook fails with an unhandled exception instead of reaching a clean blocked state.
- **Fix**: Wrap the call in try/except and set `BlockedStatus`, or check `debarchive_snap.present` before calling either function.
- **Linter rule**: "Code after a guarded block calls a function that can raise without its own exception handler" — not mechanically checkable without taint analysis.

### 10. `configure_database` has no guard for absent snap, unlike `configure()`
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/debarchive.py:116,121` (no `present` guard) vs. `src/debarchive.py:134,142` (`configure()` has one)
- **Evidence**: `configure_database()` proceeds to call `_set_snap_config_if_changed()` without checking `debarchive_snap.present`. `snap.set()` on a non-present snap raises `snap.SnapError`; the charm handler catches `Exception` (`src/charm.py:178`) and surfaces `BlockedStatus("Failed to configure database connection")`. `configure()` under the same precondition returns silently to `ActiveStatus` instead.
- **Impact**: The same precondition failure (snap absent) produces two different outcomes depending on which config path runs.
- **Fix**: Add the same `if not debarchive_snap.present: return` guard to `configure_database()`, or make both raise consistently so the charm handler can set status uniformly.
- **Linter rule**: "Two functions with the same preconditions have different error-handling behaviour" — not mechanically checkable.

### 11. `_stored` values not cleared on relation removal
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:35` (`_stored` init), `src/charm.py:207-248` (`_on_landscape_server_changed`)
- **Evidence**: `_stored.hostname`/`_stored.secret_token` are set here but never cleared anywhere. Confirmed alongside finding 2 that no relation-broken handler exists.
- **Impact**: `_provide_haproxy_route_requirements()` checks `_stored.hostname` before publishing; if a stale hostname remains after relation removal, a subsequent config change re-publishes stale route requirements instead of the new hostname.
- **Fix**: Clear `_stored` values in the relation-broken handlers added for finding 2.
- **Linter rule**: "StoredState not cleared on relation removal" — not mechanically checkable.

### 12. No unit tests for any relation-broken/departed behaviour
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py`
- **Evidence**: `grep -n "relation.broken\|relation_departed\|relation_broken" tests/unit/test_charm.py` returns nothing.
- **Impact**: The broken-path behaviour (stale config, stale `_stored`, missing status update) is entirely uncharacterised by tests.
- **Fix**: Add relation-broken tests per relation verifying snap config is cleared, `_stored` is reset, and status is correct.
- **Linter rule**: not applicable.

### 13. `configure_database` exception handler discards the original error
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:179`
- **Evidence**: `except Exception: self.unit.status = ops.BlockedStatus("Failed to configure database connection")` — the exception message is dropped.
- **Impact**: An operator can't tell if the failure was network, auth, or snapd-related from the status alone.
- **Fix**: `except Exception as e: self.unit.status = ops.BlockedStatus(f"Failed to configure database connection: {e}")`.
- **Linter rule**: "Bare except clause discards exception information" — checkable with ruff `E722`.

### 14. `relation_joined` and `relation_changed` share a handler for landscape-server, with an unhandled partial-update path
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:52,55`
- **Evidence**: Both events are observed with `_on_landscape_server_changed`. If a `relation_changed` carries only a hostname update (no secret), the handler defers on missing `secret_id` without setting any status, leaving the unit in whatever status it had before. In the normal case (both hostname and secret present) the handler runs twice, redundantly but harmlessly.
- **Impact**: Partial relation updates leave the unit's status ambiguous.
- **Fix**: Either stop observing `relation_changed` for this relation, or add an explicit `else: WaitingStatus(...)` branch.
- **Linter rule**: "Same handler registered for both relation_joined and relation_changed without distinction" — mechanically checkable.

### 15. `show-config` returns an empty dict silently when the snap is absent
- **Severity**: low
- **Kind**: ux
- **Where**: `src/debarchive.py:182-187`, `src/charm.py:135-137`
- **Evidence**: `get_config()` returns `{}` when `debarchive_snap.present` is `False`; the action handler passes that straight to `event.set_results()` with no error or status change.
- **Impact**: An operator running `show-config` after the snap is removed gets an empty result with no indication of why.
- **Fix**: `config = debarchive.get_config(); if not config: event.fail("debarchive snap is not installed")`.
- **Linter rule**: "Action returns empty result without indicating resource absence" — not mechanically checkable.

### 16. `charmlibs-snap` wraps revision/channel arguments in literal double quotes
- **Severity**: nit
- **Kind**: lint
- **Where**: `deps/charmlibs/snap/_snap.py:533,561` (`ensure()`, `_refresh()`)
- **Evidence**: `args.append(f'--revision="{revision}"')` / `f'--channel="{channel}"'`; since the command is passed as a list to `subprocess.check_output()`, the quotes become part of the literal argument value (e.g. `--revision="258"`). snapd tolerates this but it's unconventional.
- **Impact**: Confusing journal output; brittle if snapd's argument parsing ever changes.
- **Fix**: Drop the quotes (`f'--revision={revision}'`). This is a bundled-library bug, not charm code — pin/upgrade `charmlibs-snap` when a fix ships.
- **Linter rule**: "String interpolation includes unnecessary shell quoting in subprocess arguments" — checkable with a custom ruff rule.

## Worth copying

- **Config-change idempotency** (`src/debarchive.py:_set_snap_config_if_changed`): only writes snap config values that actually changed. Confirmed: `mock_snap.set` called once per change even with multiple values changing, and three passing unit tests verify unchanged keys are skipped.
- **Action error handling** (`src/charm.py`): all four actions that can fail have explicit try/except with informative `event.fail()` messages, verified for each action.
- **Redacted config display** (`src/debarchive.py:_redact_config`): `show-config` correctly redacts `password`/`secret` fields; the sensitive field list is centralized in `SENSITIVE_CONFIG_FIELDS` (`src/debarchive.py:38`).
- **Decomposition of charm logic**: `debarchive.py` is a pure Python module with no ops dependency, cleanly separated from `charm.py`'s relation logic — independently testable; all 32 debarchive-function tests pass.
- **Snap hold pattern** (`src/debarchive.py:_install_snap_packages`): the snap is held after install, unheld before refresh, re-held after — the correct pattern, confirmed working when a revision is actually pinned.
- **Secrets via ops API** (`src/charm.py:_on_landscape_server_changed`): uses `self.model.get_secret(id=secret_id, refresh=True)` rather than trusting event content — correct modern pattern.
- **Correct TLS string comparison** (`src/charm.py:172`): `ssl = "require" if str(event.tls).lower() == "true" else "disable"` correctly handles `"True"`, `"False"`, and `None` from the data platform library.
- **Defensive `unit_ip` property** (`src/charm.py:72-81`): handles `None` binding, `ModelError` on address lookup, and `None` bind_address, returning `None` cleanly in all three cases rather than raising.
- **`log-human-readable` boolean normalization** (`src/debarchive.py:148`): `str(bool(config["log-human-readable"])).lower()` correctly converts Juju's boolean config to snap-config-compatible `"true"`/`"false"`; confirmed against `juju config log-human-readable=true`.

## Common-practice notes

- **charmcraft.yaml layout**: follows current conventions; `parts:` uses the `uv` plugin correctly.
- **ops usage**: modern patterns (`StoredState`, `DatabaseRequires`, `HaproxyRouteRequirer`, `self.model.get_secret()`); does not observe `relation_departed`/`relation_broken` for any relation, a common but real omission.
- **Library versioning**: `charms.data_platform_libs.v0` and `charms.haproxy.v1` bundled in `lib/` as single files (standard pattern); `charmlibs-snap` is a standalone pip dependency via `pyproject.toml`, handled correctly by the `uv` plugin.
- **Test framework**: mixes `ops.testing.Harness` (46 passing) with `ops.testing.Context` (29 failing due to the ops pin). `tox.ini` uses `dependency_groups` and `uv-venv-lock-runner`.
- **CI**: unit tests only, no integration tests in CI (`tox -e integration` is manual). Currently broken per findings 3/4.
- **Drift**: the unimplemented `start()` stub and the absence of a service restart on config-changed are both unconventional for this class of charm, though may be intentional given the snap's own restart-on-failure behaviour.

## Tests

**Unit tests**: 75 total, 46 pass, 29 fail (see finding 3). Passing tests cover debarchive module functions (`check_health`, `configure`, `configure_database`, `restart`, `get_version`, `get_config`, `get_port`) and `Harness`-based action tests, all via monkeypatched snap operations. `ruff check src/` passes clean; `codespell src/` passes clean.

**CI pipeline**: broken and silently failing per finding 4; the fix is a one-character change to `pyproject.toml`.

**Integration tests** (`tests/integration/test_charm.py`, 4 tests):
- `test_deploy` — waits for `all_active`, no health assertion
- `test_snap_is_installed` — asserts snap name present in `snap list` only
- `test_database_relation` — asserts relation exists and `all_active`; does not verify snap config correctness
- `test_haproxy_route_relation` — asserts relation exists and unit active; uses `haproxy --channel 2.8/edge`, not the Charmhub-stable `haproxy` (which exposes `reverseproxy`, not `haproxy-route`)

None of the integration tests verify snap config correctness, service health, or invalid-config status transitions. Not run in CI — manual only via `tox -e integration`.

**Coverage gaps**:
- All three `relation_broken`/`relation_departed` handlers (no tests exist)
- `start()` stub behaviour (only exercised via monkeypatch, never directly)
- Database config clearing on relation removal (untested)
- Snap removed manually mid-deployment
- `gateway-port` range validation (unvalidated and untested)
- `show-config` behaviour when the snap is absent or relations are removed
- `haproxy-route`'s `on.removed` event (unhandled and untested)

## Docs

`README.md` is a template with no real content beyond boilerplate links.
`CONTRIBUTING.md` is minimal but functional (covers `tox`, `charmcraft pack`,
Makefile targets). The `charmcraft.yaml` description is accurate ("installs
and upgrades the debarchive snap", "keeps the debarchive service running and
its settings consistent") but does not document the required relations or
that the service won't start until they're established.

An operator deploying from the README alone would not know that:
1. The charm requires both a PostgreSQL database and a landscape-server relation before the workload will run.
2. The service stays `inactive` by design (snap `restart-condition: on-failure`) until landscape-server provides a JWT secret.
3. The published charm's snap revision is unpinned (no `snap_revisions.json`).

No `concierge.yaml`, `spread.yaml`, or other automated infra-test config exists. CI runs unit tests only, on `ubuntu-24.04`.

## Open questions

1. Is the `start()` stub intentional, or does it need implementing? On both controllers the service stayed inactive after deploy.
2. Is the hardcoded `"deb.archive.database.driver": "pgx"` correct for all Landscape deployments, or should it be configurable?
3. Should `charmlibs-snap>=1.0.1` in `pyproject.toml` be pinned to an exact version to prevent upstream regressions?
4. Should `charmcraft.yaml` add `range: [1, 65535]` for `gateway-port` so Juju rejects out-of-range values at the schema level?
5. No compatible `landscape-server` charm is available on Charmhub to test the JWT secret integration end to end — is one available privately for future review?
6. What is the intended behaviour when the haproxy relation is removed while the service is running — should the charm clear route requirements on `on.removed`?
7. Should `_on_config_changed` call `debarchive.restart()` after writing config, or does the snap watch its own config for changes?
