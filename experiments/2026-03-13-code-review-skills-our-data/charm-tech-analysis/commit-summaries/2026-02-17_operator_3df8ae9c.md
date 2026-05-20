# fix: correct the `Model.get_binding()` return type (#2329)

**Repository**: operator
**Commit**: [3df8ae9c](https://github.com/canonical/operator/commit/3df8ae9c665256d36f60e835ece4b4ac4ae22cef)
**Date**: 2026-02-17

## Classification

| Field | Value |
|-------|-------|
| Bug Area | type-annotations |
| Bug Type | type-error |
| Severity | low |
| Fix Category | source-fix |

## Summary

correct the `model.get_binding()` return type

## Commit Message

Although the `._bindings` attribute is a mapping, and we are using
`get()`, the implementation never returns `None`, it always creates a
new `Binding` if there isn't one. The signature for `get()` is correct
and does not include `None` as a possible return type. This PR extends
that to the `get_binding()` method.

Issue reported by @Gu1nness on Matrix.

## Changed Files

- M	ops/model.py

## Diff

```diff
diff --git a/ops/model.py b/ops/model.py
index 00ea326..f6b422c 100644
--- a/ops/model.py
+++ b/ops/model.py
@@ -259,7 +259,7 @@ class Model:
         """
         return self.relations._get_unique(relation_name, relation_id)
 
-    def get_binding(self, binding_key: str | Relation) -> Binding | None:
+    def get_binding(self, binding_key: str | Relation) -> Binding:
         """Get a network space binding.
 
         Args:
```
