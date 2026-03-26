# Skill: Upgrade Ops

Upgrade a Juju charm to take advantage of ops library features and address breaking changes, covering ops 2.7.0 (September 2023) through 3.6.0 (February 2026).

## When to Use

Use this skill when a charm's ops dependency is behind the latest release and could benefit from new features, or when you want to modernise a charm's ops usage patterns.

## Step 1: Assess the Current State

Before making any changes, analyse the charm:

1. **Check the ops version** in `pyproject.toml`, `requirements.txt`, or `tox.ini`. Note the current pin.
2. **Scan the charm code** for patterns that could be modernised (see the upgrade catalogue below).
3. **Check test infrastructure**: does the charm have unit tests using `ops.testing` (or the older `ops.testing.Harness`)? Integration tests?
4. **Check for tracing**: does the charm use `ops[tracing]`, `ops-tracing`, or the community `charm_tracing` library?
5. **Check for port management**: does the charm use `open_port()` / `close_port()`?
6. **Check for deferred lifecycle events**: does the charm defer `StopEvent`, `RemoveEvent`, `InstallEvent`, or other lifecycle events?

## Step 2: Identify Applicable Upgrades

Work through this catalogue and note which upgrades apply to this charm. Not every upgrade applies to every charm. Start with mandatory fixes (breaking changes), then high-impact features, then testing improvements.

### Mandatory Fixes (apply these first)

#### 0. Non-Deferrable Lifecycle Events — ops 2.11.0+

**Detect**: Search for `.defer()` in handlers for `StopEvent`, `RemoveEvent`, `InstallEvent`, `StartEvent`, `UpgradeCharmEvent`, `LeaderElectedEvent`, or other lifecycle events.

**What to do**: Remove `defer()` calls on lifecycle events. These now raise `RuntimeError`. Replace with alternative handling:
- Set a `WaitingStatus` and handle the condition in a later event.
- Do the work unconditionally (with error handling for failures).
- Move the logic to a non-lifecycle event where deferral is appropriate.

**Pattern**:
```python
# Before:
def _on_install(self, event: ops.InstallEvent):
    if not self._ready():
        event.defer()  # RuntimeError in ops 2.11.0+
        return
    self._do_install()

# After:
def _on_install(self, event: ops.InstallEvent):
    if not self._ready():
        self.unit.status = ops.WaitingStatus("Waiting for dependencies")
        return
    self._do_install()
```

### High-Impact Upgrades

#### A0. Declarative Port Management (`set_ports`) — ops 2.7.0+

**Detect**: Search for `open_port(` or `close_port(` in charm code.

**What to do**: Replace imperative `open_port()` / `close_port()` with declarative `Unit.set_ports()`.

**Pattern**:
```python
# Before:
for opened in self.unit.opened_ports():
    if opened.port != new_port:
        self.unit.close_port("tcp", opened.port)
self.unit.open_port("tcp", new_port)

# After:
self.unit.set_ports(ops.Port("tcp", new_port))
```

**Key details**:
- `set_ports()` replaces *all* open ports — pass the complete desired set.
- `set_ports()` with no arguments closes all ports.
- `OpenPort` was renamed to `Port` — use `ops.Port` in new code.
- Idempotent: calling with the same ports is a no-op.

#### A1. ops[tracing] Adoption — ops 2.21.0+

**Detect**: Search for `charm_tracing`, `trace_charm`, `TracingEndpointRequirer`, or `from charms.tempo_k8s` imports.

**What to do**: Replace community `charm_tracing` library with `ops.tracing.setup()`.

**Pattern**:
```python
# Before:
from charms.tempo_k8s.v2.tracing import charm_tracing, trace_charm

@trace_charm(tracing_endpoint="tracing_endpoint", extra_types=[...])
class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.tracing = TracingEndpointRequirer(self, relation_name="tracing")

# After:
import ops.tracing

class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        ops.tracing.setup(self, relation_name="tracing")
```

**Key details**:
- Remove the `@trace_charm` decorator.
- Remove the `TracingEndpointRequirer`.
- Delete `lib/charms/tempo_k8s/` charm library files.
- Add `ops[tracing]` to dependencies, remove `ops-tracing` if present.

### High-Impact Upgrades (continued)

#### A2. Pebble Check Events — ops 2.15.0+

**Detect**: Search for `get_checks(` in charm code, or health check polling in `_on_update_status`.

**What to do**: Replace health check polling with reactive `pebble-check-failed` and `pebble-check-recovered` event handlers.

**Pattern**:
```python
# Before (polling in update-status):
def _on_update_status(self, event):
    checks = container.get_checks(level=ops.pebble.CheckLevel.ALIVE)
    for name, check in checks.items():
        if check.status == ops.pebble.CheckStatus.DOWN:
            self.unit.status = ops.BlockedStatus(f"{name} failing")
            return

# After (reactive):
def __init__(self, *args):
    super().__init__(*args)
    self.framework.observe(self.on["myapp"].pebble_check_failed, self._on_check_failed)
    self.framework.observe(self.on["myapp"].pebble_check_recovered, self._on_check_recovered)

def _on_check_failed(self, event: ops.PebbleCheckFailedEvent):
    self.unit.status = ops.BlockedStatus(f"Check '{event.info.name}' failing")

def _on_check_recovered(self, event: ops.PebbleCheckRecoveredEvent):
    self.unit.status = ops.ActiveStatus()
```

**Key details**:
- Requires Pebble checks to be defined in the container's layer.
- Events fire based on the check's `threshold` setting (default 3 consecutive failures).
- `check-recovered` only fires after `check-failed` — don't rely on it for initial health.

#### A3. Pebble Custom Notices — ops 2.10.0+

**Detect**: Look for polling patterns in `update-status` where the charm checks workload state via `exec()` or file reads.

**What to do**: Replace workload polling with `PebbleCustomNoticeEvent` handlers. Requires workload changes to emit `pebble notify` calls.

**Pattern**:
```python
# Before (polling):
def _on_update_status(self, event):
    result = container.exec(["check-migration-status"]).wait_output()
    if "complete" in result[0]:
        self._handle_migration_complete()

# After (event-driven):
self.framework.observe(self.on["myapp"].pebble_custom_notice, self._on_notice)

def _on_notice(self, event: ops.PebbleCustomNoticeEvent):
    if event.notice.key == "example.com/migration-complete":
        self._handle_migration_complete()
```

**Key details**:
- Notice keys must use `domain/name` format.
- Workload must emit notices via `pebble notify domain/name`.
- Handlers should be idempotent — notices may be delivered more than once.
- Don't use notices for health checks — use Pebble check events instead.

#### B. Config Classes (`load_config`) — ops 2.23.0+

**Detect**: Search for `self.config[` or `self.config.get(` in charm code.

**What to do**: Define a dataclass or Pydantic `BaseModel` for the charm's config options, then replace raw dictionary access with `self.load_config(MyConfig)`.

**Pattern**:
```python
# Before:
log_level = self.config.get("log-level", "info")
port = int(self.config["port"])

# After:
import dataclasses

@dataclasses.dataclass(frozen=True)
class MyConfig:
    log_level: str = "info"
    port: int = 8080

    def __post_init__(self):
        if self.log_level not in {"info", "debug", "warning", "error", "critical"}:
            raise ValueError(f"Invalid log level: {self.log_level}")

# In the charm:
config = self.load_config(MyConfig, errors="blocked")
```

**Key details**:
- Dashes in Juju config names are automatically converted to underscores (`log-level` → `log_level`).
- `errors="blocked"` automatically sets `BlockedStatus` on validation failure.
- `errors="raise"` (default) raises the exception for manual handling.
- Both `dataclasses` and Pydantic `BaseModel` are supported. Pydantic gives richer validation but adds a dependency.
- The common pattern is `self.typed_config = self.load_config(MyConfig, errors="blocked")` in `__init__`, with the config class in a separate `src/config.py` module.

#### B. Action Classes (`load_params`) — ops 2.23.0+

**Detect**: Search for `event.params[` or `event.params.get(` in action handlers.

**What to do**: Define a dataclass or Pydantic model for each action's parameters, then replace raw dictionary access with `event.load_params(MyAction)`.

**Pattern**:
```python
# Before:
target = event.params.get("target", "/data")

# After:
@dataclasses.dataclass(frozen=True, kw_only=True)
class BackupParams:
    target: str = "/data"
    compress: bool = True

# In the handler:
params = event.load_params(BackupParams, errors="fail")
```

**Key details**:
- `errors="fail"` automatically calls `event.fail()` on validation failure.
- Dashes to underscores conversion is automatic.

#### C. Relation Data Classes (`Relation.save()`/`.load()`) — ops 2.23.0+

**Detect**: Search for `relation.data[self.app][`, `relation.data[self.unit][`, `json.dumps`/`json.loads` in relation data handling.

**What to do**: Define typed classes for relation data, then use `relation.save(obj, dst)` and `relation.load(cls, src)`.

**Pattern**:
```python
# Before:
event.relation.data[self.app]["endpoint"] = json.dumps({"host": "db.local", "port": 5432})
raw = event.relation.data[event.app].get("endpoint")
data = json.loads(raw) if raw else {}

# After:
@dataclasses.dataclass
class DatabaseEndpoint:
    host: str = ""
    port: int = 5432

event.relation.save(DatabaseEndpoint(host="db.local", port=5432), self.app)
data = event.relation.load(DatabaseEndpoint, event.app)
```

**Key details**:
- JSON serialisation/deserialisation is automatic (customisable via `encoder`/`decoder` params).
- Supports field aliases via `dataclasses.field(metadata={"alias": "secret-id"})` or Pydantic `Field(alias="secret-id")`.
- **Important**: only convert relation data that the charm owns. Don't convert relation data managed by charm libraries.
- Always check `unit.is_leader()` before calling `save()` on app data bags.

### Testing Upgrades

#### D0. Modern Action Testing (`run_action`) — ops 2.9.0+

**Detect**: Search for manual action event emission in tests (e.g. `harness.charm.on.backup_action.emit()`), or backend introspection for action results.

**What to do**: Replace with `harness.run_action()` which returns `ActionOutput` or raises `ActionFailed`.

**Pattern**:
```python
# Before:
harness.charm.on.backup_action.emit(params={"target": "/data"})
# Hard to inspect results

# After:
output = harness.run_action("backup", {"target": "/data"})
assert output.results["backup-file"] == "/data/backup.tar.gz"

# Testing failures:
with pytest.raises(ActionFailed):
    harness.run_action("backup", {"target": "/nonexistent"})
```

**Key details**:
- Action name without `-action` suffix: `"backup"`, not `"backup-action"`.
- Parameters use Juju naming (dashes), not Python (underscores).

#### D. Layer from Rockcraft (`testing.layer_from_rockcraft`) — ops 2.23.0+

**Detect**: Look for test files that manually construct `ops.pebble.Layer` objects with service definitions that duplicate what's in `rockcraft.yaml`.

**What to do**: Replace manual layer construction with `testing.layer_from_rockcraft("path/to/rockcraft.yaml")`.

**Pattern**:
```python
# Before:
layer = ops.pebble.Layer({"services": {"myapp": {"command": "/bin/myapp", ...}}})
container = testing.Container(name="workload", layers={"rock": layer})

# After:
from ops import testing
layer = testing.layer_from_rockcraft("rockcraft.yaml")
container = testing.Container(name="workload", layers={"rock": layer})
```

#### E. Bare Charm Errors (`SCENARIO_BARE_CHARM_ERRORS`) — ops 3.5.0+

**Detect**: Search for `UncaughtCharmError` in test files, or patterns like `e.__cause__` used to unwrap testing exceptions.

**What to do**: Set `SCENARIO_BARE_CHARM_ERRORS=true` in the test environment so exceptions propagate directly.

**Pattern**:
```ini
# In tox.ini:
[testenv:unit]
setenv =
    SCENARIO_BARE_CHARM_ERRORS=true
```

Then update tests that catch `UncaughtCharmError` to catch the actual exception type instead.

#### F. Context App Name and Unit ID — ops 3.1.0+

**Detect**: Look for tests that mock `self.app.name` or `self.unit.name`, or tests that need specific unit numbers.

**What to do**: Pass `app_name=` and/or `unit_id=` to `testing.Context()`.

```python
ctx = testing.Context(MyCharm, app_name="my-app", unit_id=2)
```

### Low-Impact / Niche Upgrades

#### G. PebbleClient PurePath Support — ops 3.4.0+

**Detect**: Search for `str(` wrapping path variables in Pebble container method calls.

**What to do**: Remove unnecessary `str()` conversions when passing `pathlib.PurePath` to container methods.

#### H. Deprecated `charm_spec` — ops 3.5.0+

**Detect**: Search for `charm_spec` in test files.

**What to do**: Remove direct `charm_spec` access; let Context handle metadata internally.

#### I. JujuContext — ops 3.3.0+

**Detect**: Search for `os.environ` / `os.getenv` with `JUJU_` prefixed variable names.

**What to do**: Replace with `ops.JujuContext.from_environ()` attribute access. Only relevant for charms that access Juju environment variables directly (rare).

## Step 3: Update the Ops Version Pin

After applying upgrades, bump the ops version pin:

```toml
# pyproject.toml
[project]
dependencies = [
    "ops>=3.6",
]
```

Or in `requirements.txt`:
```
ops>=3.6
```

Also check `tox.ini` for any version pins that need updating.

## Step 4: Verify

1. **Run linting**: `tox -e lint` (or equivalent)
2. **Run unit tests**: `tox -e unit`
3. **Check for deprecation warnings**: the test output may show warnings for any remaining deprecated patterns
4. **Review the diff**: ensure changes are minimal and focused — no unnecessary reformatting or unrelated changes

## Common Mistakes to Avoid

- **Don't convert relation data managed by charm libraries** (e.g. data from `charms.data_platform_libs`). Only convert data the charm writes directly.
- **Don't add Pydantic as a dependency unless the charm already uses it** or the validation benefits are clear. Dataclasses work fine for simple cases.
- **Don't change the serialisation format of relation data** if it would break compatibility with remote charms.
- **Don't mix old and new patterns** — if converting config to `load_config`, convert all config access, not just some.
- **Don't forget to update tests** — if the charm code changes, test assertions and setup may need updating too.
