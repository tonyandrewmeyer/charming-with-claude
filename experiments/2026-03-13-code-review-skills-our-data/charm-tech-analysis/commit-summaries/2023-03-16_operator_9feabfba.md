# mount meta bugfix

**Repository**: operator
**Commit**: [9feabfba](https://github.com/canonical/operator/commit/9feabfba32f4e2a04e8f6febc47662e30456ba01)
**Date**: 2023-03-16

## Classification

| Field | Value |
|-------|-------|
| Bug Area | testing-framework |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

mount meta bugfix

## Changed Files

- M	pyproject.toml
- M	scenario/scripts/snapshot.py

## Diff

```diff
diff --git a/pyproject.toml b/pyproject.toml
index d18f8ba..2eb0f5d 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -5,7 +5,7 @@ build-backend = "setuptools.build_meta"
 [project]
 name = "ops-scenario"
 
-version = "2.1.3"
+version = "2.1.3.1"
 authors = [
     { name = "Pietro Pasotti", email = "pietro.pasotti@canonical.com" }
 ]
diff --git a/scenario/scripts/snapshot.py b/scenario/scripts/snapshot.py
index ce5a8e9..7e148b5 100644
--- a/scenario/scripts/snapshot.py
+++ b/scenario/scripts/snapshot.py
@@ -347,7 +347,7 @@ def get_mounts(
         return {}
 
     mount_spec = {}
-    for mt in mount_meta:
+    for mt in mount_meta or ():
         if name := mt.get("storage"):
             mount_spec[name] = mt["location"]
         else:
```
