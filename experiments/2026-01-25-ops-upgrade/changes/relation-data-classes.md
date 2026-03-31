# relation-data-classes

## Version
ops 2.23.0

## Type
Feature

## Summary
Relation data can now be serialised to and deserialised from Python dataclasses or Pydantic models via `Relation.save()` and `Relation.load()`, replacing raw dictionary manipulation of relation data bags.

## Before
```python
import json

import ops


class MyCharm(ops.CharmBase):
    def _on_database_relation_joined(self, event: ops.RelationJoinedEvent):
        # Writing: manual JSON serialisation into the string-keyed data bag
        event.relation.data[self.app]["endpoint"] = json.dumps({
            "host": "db.local",
            "port": 5432,
        })
        event.relation.data[self.app]["version"] = "14"

    def _on_database_relation_changed(self, event: ops.RelationChangedEvent):
        # Reading: manual JSON deserialisation, no type safety
        raw = event.relation.data[event.app].get("endpoint")
        if raw:
            endpoint = json.loads(raw)
            host = endpoint["host"]
            port = int(endpoint["port"])
```

## After
```python
import dataclasses

import ops


@dataclasses.dataclass
class DatabaseEndpoint:
    host: str = ""
    port: int = 5432
    version: str = ""


class MyCharm(ops.CharmBase):
    def _on_database_relation_joined(self, event: ops.RelationJoinedEvent):
        # Writing: save a typed object directly to the relation data bag
        data = DatabaseEndpoint(host="db.local", port=5432, version="14")
        event.relation.save(data, self.app)

    def _on_database_relation_changed(self, event: ops.RelationChangedEvent):
        # Reading: load relation data into a typed object
        data = event.relation.load(DatabaseEndpoint, event.app)
        # data.host, data.port, data.version are typed
```

Alias support for dashes in relation data keys:
```python
@dataclasses.dataclass
class Data:
    secret_id: str = dataclasses.field(metadata={"alias": "secret-id"})

# Or with Pydantic:
class Data(pydantic.BaseModel):
    secret_id: str = pydantic.Field(alias="secret-id")
```

## Why Upgrade
- **Type safety**: relation data fields are typed, eliminating manual JSON parsing and type conversion.
- **Serialisation**: `save()` handles JSON encoding automatically; `load()` handles JSON decoding.
- **Pydantic support**: for richer validation and field aliasing.
- **Cleaner code**: replaces ad-hoc `json.dumps`/`json.loads` patterns with a structured API.

## Complexity
Significant

## Detection
Search for patterns like:
- `relation.data[self.app][` or `relation.data[self.unit][` (writing)
- `relation.data[event.app]` or `relation.data[event.unit]` (reading)
- `json.dumps` / `json.loads` used in relation data handling

Charms with complex relation interfaces (multiple fields, structured data) benefit most.

## Exemplar Charms
- [canonical/charmlibs](https://github.com/canonical/charmlibs) (interfaces/sloth) -- Pydantic models with custom YAML encoder/decoder for complex nested SLO data. Most sophisticated usage found.
- [canonical/hive-metastore-k8s-operator](https://github.com/canonical/hive-metastore-k8s-operator) (src/charm.py, src/hive_metastore.py) -- Pydantic with `Field(alias="secret-tls")` for hyphenated keys, plus a custom decoder that resolves Juju secret URIs inline.
- [canonical/falco-operators](https://github.com/canonical/falco-operators) (interfaces/falcosidekick_http_endpoint) -- Clean, minimal Pydantic example with `HttpUrl` validation. Good introductory reference.
- [canonical/pyroscope-operators](https://github.com/canonical/pyroscope-operators) (coordinator/lib/.../profiling.py) -- Published charmlib using Pydantic for the databag model; catches both `ModelError` and `ValidationError` on load.
- [canonical/litmus-operators](https://github.com/canonical/litmus-operators) (libs/src/litmus_libs/interfaces/) -- Versioned databag base pattern with `pydantic.ConfigDict(extra="ignore")` for forward compatibility.

**Notable**: every exemplar found uses Pydantic (not dataclasses) for relation data models. Leader gating before `save()` to app databags is consistent across all.

## Pitfalls
- **Interface compatibility**: the serialised format must be compatible with what the remote charm expects. If the remote charm reads raw relation data, the schema class must produce matching keys and value formats.
- **Custom codecs**: `save()` accepts an `encoder` and `load()` accepts a `decoder` for custom serialisation (default is `json.dumps`/`json.loads`).
- **Pydantic `MISSING` sentinel**: ops 3.6.0 added support for Pydantic's `MISSING` sentinel in `Relation.save`, allowing fields to be explicitly omitted from the data bag.
- **Scope**: `save()` and `load()` take a `src`/`dst` parameter (`Unit` or `Application`) to specify which data bag to read from or write to.
- **Partial adoption**: can be adopted incrementally — start with one relation endpoint while keeping raw access for others.
- **Charm library compatibility**: if the charm uses charm libraries that manage relation data, the library may need updating to use the new API. Don't convert relation data handling that's managed by a library.
