# fix: de-walrusify

**Repository**: pytest-jubilant
**Commit**: [520e1cc4](https://github.com/canonical/pytest-jubilant/commit/520e1cc4b9e448d2e8edb4a5479c8584588cedb6)
**Date**: 2025-05-01T14:35:01+02:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | charm-deployment |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Attempted fix for resource parsing by removing walrus operator; later found incorrect and reverted

## Changed Files

- M	pytest_jubilant/main.py

## Diff

```diff
diff --git a/pytest_jubilant/main.py b/pytest_jubilant/main.py
index 7fcfaff..c506bdf 100644
--- a/pytest_jubilant/main.py
+++ b/pytest_jubilant/main.py
@@ -197,11 +197,11 @@ def pack_charm(root: Union[Path, str] = "./") -> _Result:
         if (meta_yaml := Path(root) / meta_name).exists():
             logging.debug(f"found metadata file: {meta_yaml}")
             meta = yaml.safe_load(meta_yaml.read_text())
-            if meta_resources := meta["resources"]:
+            if "resources" in meta.keys():
                 try:
                     resources = {
                         resource: res_meta["upstream-source"]
-                        for resource, res_meta in meta_resources.items()
+                        for resource, res_meta in meta["resources"].items()
                     }
                 except KeyError:
                     logging.exception(
```
