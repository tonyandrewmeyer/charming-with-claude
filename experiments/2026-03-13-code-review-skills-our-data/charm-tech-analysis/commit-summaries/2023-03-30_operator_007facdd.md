# fixed relation-list for subs

**Repository**: operator
**Commit**: [007facdd](https://github.com/canonical/operator/commit/007facdda55203285b15367c393ddb3e1ad35181)
**Date**: 2023-03-30

## Classification

| Field | Value |
|-------|-------|
| Bug Area | relation-data |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

ed relation-list for subs

## Changed Files

- M	scenario/mocking.py

## Diff

```diff
diff --git a/scenario/mocking.py b/scenario/mocking.py
index db9370b..e2e2776 100644
--- a/scenario/mocking.py
+++ b/scenario/mocking.py
@@ -130,7 +130,7 @@ class _MockModelBackend(_ModelBackend):
             if rel.endpoint == relation_name
         ]
 
-    def relation_list(self, relation_id: int):
+    def relation_list(self, relation_id: int) -> Tuple[str]:
         relation = self._get_relation_by_id(relation_id)
         relation_type = getattr(relation, "__type__", "<no type>")
         if relation_type == "regular":
@@ -142,7 +142,7 @@ class _MockModelBackend(_ModelBackend):
             return tuple(f"{self.app_name}/{unit_id}" for unit_id in relation.peers_ids)
 
         elif relation_type == "subordinate":
-            return tuple(f"{relation.primary_name}")
+            return f"{relation.primary_name}",
         else:
             raise RuntimeError(
                 f"Invalid relation type: {relation_type}; should be one of "
```
