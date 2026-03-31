# Skill: Adopt Relation Data Classes

Replace raw `relation.data[app/unit]["key"]` dictionary access with typed Python classes using `Relation.save()` and `Relation.load()`.

## When to Use

Use this when a charm reads or writes relation data bags directly using string keys and manual JSON serialisation. **Do not** convert relation data that is managed by a charm library.

## Prerequisites

- ops >= 2.23.0
- The charm has relations defined in `charmcraft.yaml` (or `metadata.yaml`)

## Step 1: Identify Convertible Relation Data

1. List all relations in the charm's metadata.
2. For each relation, search charm code for direct data access:
   - `relation.data[self.app]["key"]` (writing app data)
   - `relation.data[self.unit]["key"]` (writing unit data)
   - `relation.data[event.app]` / `relation.data[event.unit]` (reading)
   - `json.dumps`/`json.loads` used for serialisation
3. **Exclude** any relation data managed by charm libraries (e.g. `charms.data_platform_libs`, `charms.observability_libs`). Those libraries own the data format.

## Step 2: Define Data Classes

For each relation endpoint where the charm owns the data format, define a typed class.

```python
import dataclasses


@dataclasses.dataclass
class DatabaseProviderData:
    host: str = ""
    port: int = 5432
    credentials_secret_id: str = ""
```

For Pydantic (recommended for complex data or when you need validation):

```python
import pydantic


class DatabaseProviderData(pydantic.BaseModel):
    host: str = ""
    port: int = pydantic.Field(default=5432, ge=1, le=65535)
    credentials_secret_id: str = pydantic.Field(default="", alias="credentials-secret-id")
```

### Alias Support

Relation data keys may use dashes or other conventions. Use aliases to map them:

```python
# Dataclass:
secret_id: str = dataclasses.field(default="", metadata={"alias": "secret-id"})

# Pydantic:
secret_id: str = pydantic.Field(default="", alias="secret-id")
```

## Step 3: Update Charm Code

### Writing relation data

```python
# Before:
event.relation.data[self.app]["host"] = "db.local"
event.relation.data[self.app]["port"] = json.dumps(5432)

# After:
data = DatabaseProviderData(host="db.local", port=5432)
event.relation.save(data, self.app)
```

**Important**: always check `self.unit.is_leader()` before saving to app data bags.

### Reading relation data

```python
# Before:
raw = event.relation.data[event.app].get("host", "")
port = json.loads(event.relation.data[event.app].get("port", "5432"))

# After:
data = event.relation.load(DatabaseProviderData, event.app)
# data.host, data.port are properly typed
```

### Custom serialisation

The default encoder/decoder is `json.dumps`/`json.loads`. For custom formats:

```python
relation.save(data, self.app, encoder=yaml.dump)
data = relation.load(MyClass, event.app, decoder=yaml.safe_load)
```

## Step 4: Update Tests

Tests that set relation data in `testing.Relation` should use the same serialised format that `save()` produces:

```python
relation = testing.Relation(
    endpoint="database",
    remote_app_data={"host": '"db.local"', "port": "5432"},
    # Note: values are JSON-encoded strings, matching what save() writes
)
```

## Step 5: Verify

1. Run unit tests to verify relation data is correctly read and written.
2. **Crucially**: verify that the serialised format hasn't changed. The remote charm must be able to read the data. Run `juju show-unit` to compare the data bag format before and after.

## Exemplar Charms

- **[charmlibs](https://github.com/canonical/charmlibs)** (interfaces/sloth) — Pydantic with custom YAML encoder/decoder for complex nested data.
- **[hive-metastore-k8s-operator](https://github.com/canonical/hive-metastore-k8s-operator)** — Pydantic with aliases and a custom decoder that resolves Juju secrets.
- **[falco-operators](https://github.com/canonical/falco-operators)** (interfaces/falcosidekick_http_endpoint) — Clean minimal example with `HttpUrl` validation.

## Common Mistakes

- **Don't change the wire format.** The serialised keys and value formats must remain compatible with what remote charms expect. Test this carefully.
- **Don't convert library-managed relation data.** If a charm library (e.g. from `charms.data_platform_libs`) handles the relation, leave it alone.
- **Don't forget leader gating.** Only the leader unit can write to app data bags.
- **Do handle `pydantic.ValidationError`** (or `ValueError` for dataclasses) gracefully when loading data from remote charms — the remote may send unexpected data.
