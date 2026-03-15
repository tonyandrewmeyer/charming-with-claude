# fixed decompose

**Repository**: operator
**Commit**: [fe61cb5f](https://github.com/canonical/operator/commit/fe61cb5fbca3d1a9aada62898d0a9b913c18e933)
**Date**: 2023-02-02

## Classification

| Field | Value |
|-------|-------|
| Bug Area | testing-framework |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

ed decompose

## Changed Files

- M	pyproject.toml
- M	scenario/sequences.py

## Diff

```diff
diff --git a/pyproject.toml b/pyproject.toml
index fe24e16..092210b 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -5,7 +5,7 @@ build-backend = "setuptools.build_meta"
 [project]
 name = "ops-scenario"
 
-version = "2.0.2"
+version = "2.0.3"
 authors = [
     { name = "Pietro Pasotti", email = "pietro.pasotti@canonical.com" }
 ]
diff --git a/scenario/sequences.py b/scenario/sequences.py
index 2752b93..7f259d4 100644
--- a/scenario/sequences.py
+++ b/scenario/sequences.py
@@ -32,11 +32,11 @@ def decompose_meta_event(meta_event: Event, state: State):
     if meta_event.name in [CREATE_ALL_RELATIONS, BREAK_ALL_RELATIONS]:
         for relation in state.relations:
             event = Event(
-                relation.meta.endpoint + META_EVENTS[meta_event.name],
+                relation.endpoint + META_EVENTS[meta_event.name],
                 args=(
                     # right now, the Relation object hasn't been created by ops yet, so we can't pass it down.
                     # this will be replaced by a Relation instance before the event is fired.
-                    InjectRelation(relation.meta.endpoint, relation.meta.relation_id),
+                    InjectRelation(relation.endpoint, relation.relation_id),
                 ),
             )
             logger.debug(f"decomposed meta {meta_event.name}: {event}")
```
