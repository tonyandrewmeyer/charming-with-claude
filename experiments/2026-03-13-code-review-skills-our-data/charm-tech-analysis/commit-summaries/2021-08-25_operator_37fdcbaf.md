# Fix Container.restart() accidentally operating on strings, add a testcase (#590)

**Repository**: operator
**Commit**: [37fdcbaf](https://github.com/canonical/operator/commit/37fdcbaf8cf56f639c02de12685941bf9319a773)
**Date**: 2021-08-25

## Classification

| Field | Value |
|-------|-------|
| Bug Area | pebble |
| Bug Type | other |
| Severity | high |
| Fix Category | source-fix |

## Summary

container.restart() accidentally operating on strings, add a testcase

## Commit Message

* Fix Container.restart() accidentally operating on strings, add a testcase

* Make pep8 happy

## Changed Files

- M	ops/model.py
- M	test/test_model.py

## Diff

```diff
diff --git a/ops/model.py b/ops/model.py
index 2bf1d8e..c89d026 100644
--- a/ops/model.py
+++ b/ops/model.py
@@ -1118,7 +1118,7 @@ class Container:
         if not service_names:
             raise TypeError('restart expected at least 1 argument, got 0')
 
-        for svc in self.get_services(service_names):
+        for svc in self.get_services(*service_names).values():
             if svc.is_running():
                 self._pebble.stop_services(svc.name)
         self._pebble.start_services(service_names)
diff --git a/test/test_model.py b/test/test_model.py
index 3f80664..9070d88 100755
--- a/test/test_model.py
+++ b/test/test_model.py
@@ -828,6 +828,24 @@ containers:
         with self.assertRaises(TypeError):
             self.container.start()
 
+    def test_restart(self):
+        two_services = [
+            self._make_service('foo', 'enabled', 'active'),
+            self._make_service('bar', 'disabled', 'inactive'),
+        ]
+        self.pebble.responses.append(two_services)
+        self.container.restart('foo')
+        self.pebble.responses.append(two_services)
+        self.container.restart('foo', 'bar')
+        self.assertEqual(self.pebble.requests, [
+            ('get_services', ('foo',)),
+            ('stop', 'foo'),
+            ('start', ('foo',)),
+            ('get_services', ('foo', 'bar')),
+            ('stop', 'foo'),
+            ('start', ('foo', 'bar',)),
+        ])
+
     def test_stop(self):
         self.container.stop('foo')
         self.container.stop('foo', 'bar')
```
