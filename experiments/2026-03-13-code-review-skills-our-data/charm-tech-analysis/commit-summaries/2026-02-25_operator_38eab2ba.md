# fix: support Pydantic MISSING sentinel in ops.Relation.save (#2306)

**Repository**: operator
**Commit**: [38eab2ba](https://github.com/canonical/operator/commit/38eab2ba06670ae925e209d73509e9be98ac0cce)
**Date**: 2026-02-25

## Classification

| Field | Value |
|-------|-------|
| Bug Area | relation-data |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

support pydantic missing sentinel in ops.relation.save

## Commit Message

Support Pydantic's experimental `MISSING` sentinel field types and
values.

`ops.Relation.load()` does the right thing already.
`ops.Relation.save()` needs a small fix to erase missing fields

Check list:
- [x] core code change
- [x] unit tests pass
- [x] ruff format
- [x] docs update
- [x] test on real Juju --> https://github.com/dimaqq/hexanator/pull/7
- [x] separate new test case
- [x] make the new test conditional on being able to import MISSING
- [x] (whatever reviews bring)

Fixes #2299

## Changed Files

- M	ops/model.py
- M	test/test_model_relation_data_class.py

## Diff

```diff
diff --git a/ops/model.py b/ops/model.py
index 81e6250..a2c9cd3 100644
--- a/ops/model.py
+++ b/ops/model.py
@@ -1873,6 +1873,10 @@ class Relation:
                 # data.destination will be stored under the Juju relation key 'to'
                 relation.save(data, self.unit)
 
+        If a Pydantic model's ``model_dump`` method omits any field (e.g. if its
+        value is Pydantic's ``MISSING`` sentinel) the field will be erased from
+        the relation data.
+
         Args:
             obj: an object with attributes to save to the relation data, typically
                 a Pydantic ``BaseModel`` subclass or dataclass.
@@ -1915,7 +1919,11 @@ class Relation:
             values = {field: getattr(obj, field) for field in fields}
 
         # Encode each value, and then pass it over to Juju.
-        data = {field: encoder(values[attr]) for attr, field in sorted(fields.items())}
+        # Missing values are erased from the databag using empty string values.
+        data = {
+            field: encoder(values[attr]) if attr in values else ''
+            for attr, field in sorted(fields.items())
+        }
         self.data[dst].update(data)
 
 
diff --git a/test/test_model_relation_data_class.py b/test/test_model_relation_data_class.py
index d362dcf..7313e7e 100644
--- a/test/test_model_relation_data_class.py
+++ b/test/test_model_relation_data_class.py
@@ -31,6 +31,11 @@ try:
 except ImportError:
     pydantic = None
 
+try:
+    from pydantic.experimental.missing_sentinel import MISSING
+except ImportError:
+    MISSING = None  # type: ignore
+
 import ops
 from ops import testing
 
@@ -213,6 +218,34 @@ if pydantic:
     _test_classes.extend((MyPydanticDataclassCharm, MyPydanticBaseModelCharm))
 
 
+if pydantic and MISSING is not None:
+
+    class MissingPydanticDatabag(pydantic.BaseModel):
+        foo: str
+        bar: int = pydantic.Field(default=0, ge=0)
+        baz: list[str] = pydantic.Field(default_factory=list)
+        quux: Nested = pydantic.Field(default_factory=Nested)
+        miss: str | MISSING = MISSING  # type: ignore
+
+        @pydantic.field_validator('baz')
+        @classmethod
+        def check_foo_not_in_baz(cls, baz: list[str], values: Any):
+            data = cast('dict[str, Any]', values.data)
+            foo = data.get('foo')
+            if foo in baz:
+                raise ValueError('foo cannot be in baz')
+            return baz
+
+        model_config = pydantic.ConfigDict(validate_assignment=True)
+
+    class MissingPydanticBaseModelCharm(BaseTestCharm):
+        @property
+        def databag_class(self) -> type[DatabagProtocol]:
+            return MissingPydanticDatabag
+
+    _test_classes.append(MissingPydanticBaseModelCharm)
+
+
 @pytest.mark.parametrize('charm_class', _test_classes)
 def test_relation_load_simple(charm_class: type[BaseTestCharm]):
     class Charm(charm_class):
```
