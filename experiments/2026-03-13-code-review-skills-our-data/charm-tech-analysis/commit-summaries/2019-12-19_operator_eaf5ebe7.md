# Fix ResourceMeta for oci-image type resources (#93)

**Repository**: operator
**Commit**: [eaf5ebe7](https://github.com/canonical/operator/commit/eaf5ebe7e8aa61457c0bd2a8a217a78316f6f337)
**Date**: 2019-12-19

## Classification

| Field | Value |
|-------|-------|
| Bug Area | resources |
| Bug Type | other |
| Severity | medium |
| Fix Category | source-fix |

## Summary

resourcemeta for oci-image type resources

## Commit Message

Resources of the type `oci-image` do not actually define a filename,
since they are actually just metadata about an image in a registry.

## Changed Files

- M	ops/charm.py

## Diff

```diff
diff --git a/ops/charm.py b/ops/charm.py
index 3ccca13..1c172da 100755
--- a/ops/charm.py
+++ b/ops/charm.py
@@ -229,7 +229,7 @@ class ResourceMeta:
     def __init__(self, name, raw):
         self.resource_name = name
         self.type = raw['type']
-        self.filename = raw['filename']
+        self.filename = raw.get('filename', None)
         self.description = raw.get('description', '')
```
