# Skill: Upgrade Ops

Upgrade a Juju charm to take advantage of recent ops library features and address deprecations.

## When to Use

Use this skill when a charm's ops dependency is behind the latest release and could benefit from new features, or when you want to modernise a charm's ops usage patterns.

## Step 1: Assess the Current State

Before making any changes, analyse the charm:

1. **Check the ops version** in `pyproject.toml`, `requirements.txt`, or `tox.ini`. Note the current pin.
2. **Scan the charm code** for patterns that could be modernised (see the upgrade catalogue below).
3. **Check test infrastructure**: does the charm have unit tests using `ops.testing` (or the older `ops.testing.Harness`)? Integration tests?
4. **Check for tracing**: does the charm use `ops[tracing]` or `ops-tracing`?

## Step 2: Identify Applicable Upgrades

Work through this catalogue and note which upgrades apply to this charm. Not every upgrade applies to every charm.

### High-Impact Upgrades (apply these first)

#### A. Config Classes (`load_config`) — ops 2.23.0+

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
