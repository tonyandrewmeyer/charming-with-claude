# fix TypeError: CharmBase.__init__() takes 2 positional arguments but 3 were given

**Repository**: operator
**Commit**: [caed680b](https://github.com/canonical/operator/commit/caed680b933c6c62e1305ec7773a9bf0c81e5661)
**Date**: 2023-01-26

## Classification

| Field | Value |
|-------|-------|
| Bug Area | error-handling |
| Bug Type | type-error |
| Severity | low |
| Fix Category | test-fix |

## Summary

typeerror: charmbase.__init__() takes 2 positional arguments but 3 were given

## Changed Files

- M	tests/test_e2e/test_state.py

## Diff

```diff
diff --git a/tests/test_e2e/test_state.py b/tests/test_e2e/test_state.py
index bce75a3..a0da370 100644
--- a/tests/test_e2e/test_state.py
+++ b/tests/test_e2e/test_state.py
@@ -49,8 +49,8 @@ def mycharm():
         called = False
         on = MyCharmEvents()
 
-        def __init__(self, framework: Framework, key: Optional[str] = None):
-            super().__init__(framework, key)
+        def __init__(self, framework: Framework):
+            super().__init__(framework)
             for evt in self.on.events().values():
                 self.framework.observe(evt, self._on_event)
```
