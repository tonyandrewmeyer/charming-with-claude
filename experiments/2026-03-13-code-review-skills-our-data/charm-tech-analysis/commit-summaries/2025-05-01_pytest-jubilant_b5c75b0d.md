# fix: It's not walrus that's wrong, it's the expression

**Repository**: pytest-jubilant
**Commit**: [b5c75b0d](https://github.com/canonical/pytest-jubilant/commit/b5c75b0d8112c12d40b3e4ed47bb0ec3930498bd)
**Date**: 2025-05-01T14:52:24+02:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | charm-deployment |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Reverted de-walrusification and used meta.get('resources') to avoid KeyError when resources key is absent

## Changed Files

- M	pytest_jubilant/main.py

## Diff

```diff
diff --git a/pytest_jubilant/main.py b/pytest_jubilant/main.py
index c506bdf..30ebbac 100644
--- a/pytest_jubilant/main.py
+++ b/pytest_jubilant/main.py
@@ -197,11 +197,11 @@ def pack_charm(root: Union[Path, str] = "./") -> _Result:
         if (meta_yaml := Path(root) / meta_name).exists():
             logging.debug(f"found metadata file: {meta_yaml}")
             meta = yaml.safe_load(meta_yaml.read_text())
-            if "resources" in meta.keys():
+            if meta_resources := meta.get("resources"):
                 try:
                     resources = {
                         resource: res_meta["upstream-source"]
-                        for resource, res_meta in meta["resources"].items()
+                        for resource, res_meta in meta_resources.items()
                     }
                 except KeyError:
                     logging.exception(
```
