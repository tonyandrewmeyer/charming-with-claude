# fix(framework): add warning on lost observer weakref (#1142)

**Repository**: operator
**Commit**: [bc0bf8fe](https://github.com/canonical/operator/commit/bc0bf8feb1b4795f6ceb8d6d550e48c45607a5fa)
**Date**: 2024-03-10

## Classification

| Field | Value |
|-------|-------|
| Bug Area | event-framework |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

framework): add warning on lost observer weakref

## Changed Files

- M	ops/framework.py
- M	test/test_charm.py

## Diff

```diff
diff --git a/ops/framework.py b/ops/framework.py
index cc84436..645abdc 100644
--- a/ops/framework.py
+++ b/ops/framework.py
@@ -954,6 +954,13 @@ class Framework(Object):
                             # Regular call to the registered method.
                             custom_handler(event)
 
+            else:
+                logger.warning(
+                    f"Reference to ops.Object at path {observer_path} has been garbage collected "
+                    "between when the charm was initialised and when the event was emitted. "
+                    "Make sure sure you store a reference to the observer."
+                )
+
             if event.deferred:
                 deferred = True
             else:
diff --git a/test/test_charm.py b/test/test_charm.py
index 627d2d5..7ebbce2 100644
--- a/test/test_charm.py
+++ b/test/test_charm.py
@@ -128,6 +128,30 @@ class TestCharm(unittest.TestCase):
         # check that the event has been seen by the observer
         self.assertIsInstance(charm.seen, ops.StartEvent)
 
+    def test_observer_not_referenced_warning(self):
+        class MyObj(ops.Object):
+            def __init__(self, charm: ops.CharmBase):
+                super().__init__(charm, "obj")
+                framework.observe(charm.on.start, self._on_start)
+
+            def _on_start(self, _: ops.StartEvent):
+                raise RuntimeError()  # never reached!
+
+        class MyCharm(ops.CharmBase):
+            def __init__(self, *args: typing.Any):
+                super().__init__(*args)
+                MyObj(self)  # not assigned!
+                framework.observe(self.on.start, self._on_start)
+
+            def _on_start(self, _: ops.StartEvent):
+                pass  # is reached
+
+        framework = self.create_framework()
+        c = MyCharm(framework)
+        with self.assertLogs() as logs:
+            c.on.start.emit()
+        assert any('Reference to ops.Object' in log for log in logs.output)
+
     def test_empty_action(self):
         meta = ops.CharmMeta.from_yaml('name: my-charm', '')
         self.assertEqual(meta.actions, {})
```
