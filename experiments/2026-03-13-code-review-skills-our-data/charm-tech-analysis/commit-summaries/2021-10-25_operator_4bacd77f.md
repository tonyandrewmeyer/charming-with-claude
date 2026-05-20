# Fix for container.restart in older versions of Pebble (#657)

**Repository**: operator
**Commit**: [4bacd77f](https://github.com/canonical/operator/commit/4bacd77f819c409ef844fbec568735b64ef4f646)
**Date**: 2021-10-25

## Classification

| Field | Value |
|-------|-------|
| Bug Area | pebble |
| Bug Type | version-compat |
| Severity | medium |
| Fix Category | source-fix |

## Summary

for container.restart in older versions of pebble

## Changed Files

- M	ops/model.py

## Diff

```diff
diff --git a/ops/model.py b/ops/model.py
index dc1c2b3..adf748e 100644
--- a/ops/model.py
+++ b/ops/model.py
@@ -1135,9 +1135,9 @@ class Container:
             if e.code != 400:
                 raise e
             # support old Pebble instances that don't support the "restart" action
-            for svc in self.get_services(service_names):
+            for svc in self.get_services(*service_names).values():
                 if svc.is_running():
-                    self._pebble.stop_services(svc.name)
+                    self._pebble.stop_services((*[svc.name],))
             self._pebble.start_services(service_names)
 
     def stop(self, *service_names: str):
```
