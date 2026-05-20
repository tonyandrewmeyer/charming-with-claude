# Fix logging in can_connect, add tests; remove pebble.Error methods (#860)

**Repository**: operator
**Commit**: [516abffb](https://github.com/canonical/operator/commit/516abffb8c60af8de4d4ef7efb5671fd52cdd872)
**Date**: 2022-11-30

## Classification

| Field | Value |
|-------|-------|
| Bug Area | pebble |
| Bug Type | test-divergence |
| Severity | medium |
| Fix Category | source-fix |

## Summary

logging in can_connect, add tests; remove pebble.error methods

## Commit Message

The debug logging in the FileNotFoundError case raises an exception
while logging due to a missing "%s". In addition, we don't need str(e)
or e.message(): %s with just "e" handles the formatting.

Also, can_connect wasn't very well tested, so add test cases for the
various exception cases.

Also remove the other use of pebble.Error.message() and remove the
pebble.Error.name() and .message() methods as per #777.

Also: Clean up ops-harness temp dir on call to cleanup.
This fixes ResourceWarning issue in tests on Windows Python 3.5.

Fixes #759

Fixes #777

## Changed Files

- M	ops/model.py
- M	ops/pebble.py
- M	ops/testing.py
- M	test/test_model.py
- M	test/test_pebble.py

## Diff

```diff
diff --git a/ops/model.py b/ops/model.py
index 9412ae9..79af88f 100644
--- a/ops/model.py
+++ b/ops/model.py
@@ -1418,17 +1418,17 @@ class Container:
             #  instance that is in fact 'ready'.
             self._pebble.get_system_info()
         except pebble.ConnectionError as e:
-            logger.debug("Pebble API is not ready; ConnectionError: %s", e.message())
+            logger.debug("Pebble API is not ready; ConnectionError: %s", e)
             return False
         except FileNotFoundError as e:
             # In some cases, charm authors can attempt to hit the Pebble API before it has had the
             # chance to create the UNIX socket in the shared volume.
-            logger.debug("Pebble API is not ready; UNIX socket not found:", str(e))
+            logger.debug("Pebble API is not ready; UNIX socket not found: %s", e)
             return False
         except pebble.APIError as e:
             # An API error is only raised when the Pebble API returns invalid JSON, or the response
             # cannot be read. Both of these are a likely indicator that something is wrong.
-            logger.warning("Pebble API is not ready; APIError: %s", str(e))
+            logger.warning("Pebble API is not ready; APIError: %s", e)
             return False
         return True
 
diff --git a/ops/pebble.py b/ops/pebble.py
index 71de6fb..0c15c3d 100644
--- a/ops/pebble.py
+++ b/ops/pebble.py
@@ -333,14 +333,6 @@ class Error(Exception):
     def __repr__(self):
         return '<{}.{} {}>'.format(type(self).__module__, type(self).__name__, self.args)
 
-    def name(self):
-        """Return a string representation of the model plus class."""
-        return '<{}.{}>'.format(type(self).__module__, type(self).__name__)
-
-    def message(self):
-        """Return the message passed as an argument."""
-        return self.args[0]
-
 
 class TimeoutError(TimeoutError, Error):
     """Raised when a polling timeout occurs."""
diff --git a/ops/testing.py b/ops/testing.py
index d92609b..98507a5 100755
--- a/ops/testing.py
+++ b/ops/testing.py
@@ -1406,6 +1406,7 @@ class _TestingModelBackend:
         if self._resource_dir is not None:
             self._resource_dir.cleanup()
             self._resource_dir = None
+        self._harness_tmp_dir.cleanup()
 
     def _get_resource_dir(self) -> pathlib.Path:
         if self._resource_dir is None:
diff --git a/test/test_model.py b/test/test_model.py
index 173168f..e1ff14d 100755
--- a/test/test_model.py
+++ b/test/test_model.py
@@ -33,7 +33,14 @@ import ops.testing
 from ops import model
 from ops._private import yaml
 from ops.charm import RelationMeta, RelationRole
-from ops.pebble import APIError, FileInfo, FileType, ServiceInfo
+from ops.pebble import (
+    APIError,
+    ConnectionError,
+    FileInfo,
+    FileType,
+    ServiceInfo,
+    SystemInfo,
+)
 
 
 class TestModel(unittest.TestCase):
@@ -1354,8 +1361,9 @@ containers:
         self.container.replan()
         self.assertEqual(self.pebble.requests, [('replan',)])
 
-    def test_get_system_info(self):
-        self.container.can_connect()
+    def test_can_connect(self):
+        self.pebble.responses.append(SystemInfo.from_dict({'version': '1.0.0'}))
+        self.assertTrue(self.container.can_connect())
         self.assertEqual(self.pebble.requests, [('get_system_info',)])
 
     def test_start(self):
@@ -1687,10 +1695,37 @@ containers:
             ('remove_path', '/path/2', True),
         ])
 
-    def test_bare_can_connect_call(self):
-        self.pebble.responses.append('dummy')
+    def test_can_connect_simple(self):
+        self.pebble.responses.append(SystemInfo.from_dict({'version': '1.0.0'}))
         self.assertTrue(self.container.can_connect())
 
+    def test_can_connect_connection_error(self):
+        def raise_error():
+            raise ConnectionError('connection error!')
+        self.pebble.get_system_info = raise_error
+        with self.assertLogs('ops.model', level='DEBUG') as cm:
+            self.assertFalse(self.container.can_connect())
+        self.assertEqual(len(cm.output), 1)
+        self.assertRegex(cm.output[0], r'DEBUG:ops.model:.*: connection error!')
+
+    def test_can_connect_file_not_found_error(self):
+        def raise_error():
+            raise FileNotFoundError('file not found!')
+        self.pebble.get_system_info = raise_error
+        with self.assertLogs('ops.model', level='DEBUG') as cm:
+            self.assertFalse(self.container.can_connect())
+        self.assertEqual(len(cm.output), 1)
+        self.assertRegex(cm.output[0], r'DEBUG:ops.model:.*: file not found!')
+
+    def test_can_connect_api_error(self):
+        def raise_error():
+            raise APIError('body', 404, 'status', 'api error!')
+        self.pebble.get_system_info = raise_error
+        with self.assertLogs('ops.model') as cm:
+            self.assertFalse(self.container.can_connect())
+        self.assertEqual(len(cm.output), 1)
+        self.assertRegex(cm.output[0], r'WARNING:ops.model:.*: api error!')
+
     def test_exec(self):
         self.pebble.responses.append('fake_exec_process')
         p = self.container.exec(
@@ -1759,6 +1794,7 @@ class MockPebbleClient:
 
     def get_system_info(self):
         self.requests.append(('get_system_info',))
+        return self.responses.pop(0)
 
     def replan_services(self):
         self.requests.append(('replan',))
diff --git a/test/test_pebble.py b/test/test_pebble.py
index 924d110..d076795 100644
--- a/test/test_pebble.py
+++ b/test/test_pebble.py
@@ -1248,7 +1248,7 @@ class TestMultipartParser(unittest.TestCase):
                     if not test.error:
                         self.fail('unexpected error:', err)
                         break
-                    self.assertEqual(test.error, err.message())
+                    self.assertEqual(test.error, str(err))
                 else:
                     if test.error:
                         self.fail('missing expected error: {!r}'.format(test.error))
```
