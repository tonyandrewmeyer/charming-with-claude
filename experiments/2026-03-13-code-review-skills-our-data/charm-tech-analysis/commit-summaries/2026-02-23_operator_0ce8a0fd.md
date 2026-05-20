# fix: only show executable in ExecError.__str__, not full command line (#2336)

**Repository**: operator
**Commit**: [0ce8a0fd](https://github.com/canonical/operator/commit/0ce8a0fdbe89ce4d55b7f23fd245366d4d83698f)
**Date**: 2026-02-23

## Classification

| Field | Value |
|-------|-------|
| Bug Area | security |
| Bug Type | info-leak |
| Severity | high |
| Fix Category | source-fix |

## Summary

only show executable in execerror.__str__, not full command line

## Commit Message

This is to avoid credentials or sensitive data passed in command line
args showing up in exception messages and logs. Sensitive data
*shouldn't* be passed in command line args, but it sometimes is, so
better to be cautious here. We do something similar with tracing: only
send the executable name for pebble exec.

## Changed Files

- M	docs/howto/manage-containers/manage-the-workload-container.md
- M	ops/pebble.py
- M	test/test_pebble.py

## Diff

```diff
diff --git a/docs/howto/manage-containers/manage-the-workload-container.md b/docs/howto/manage-containers/manage-the-workload-container.md
index d1273a1..a1d62ec 100644
--- a/docs/howto/manage-containers/manage-the-workload-container.md
+++ b/docs/howto/manage-containers/manage-the-workload-container.md
@@ -554,7 +554,7 @@ Note that because sleep will exit via a signal, `wait()` will raise an `ExecErro
 ```
 Traceback (most recent call last):
   ...
-ops.pebble.ExecError: non-zero exit code 143 executing ['sleep', '10']
+ops.pebble.ExecError: non-zero exit code 143 executing 'sleep'
 ```
 
 ### Test command execution
diff --git a/ops/pebble.py b/ops/pebble.py
index bb507a1..0ff8c37 100644
--- a/ops/pebble.py
+++ b/ops/pebble.py
@@ -558,7 +558,7 @@ class ExecError(Error, Generic[AnyStr]):
         self.stderr = stderr
 
     def __str__(self):
-        message = f'non-zero exit code {self.exit_code} executing {self.command!r}'
+        message = f'non-zero exit code {self.exit_code} executing {self.command[0]!r}'
 
         for name, out in [('stdout', self.stdout), ('stderr', self.stderr)]:
             if out is None:
diff --git a/test/test_pebble.py b/test/test_pebble.py
index 99f420f..8b97f18 100644
--- a/test/test_pebble.py
+++ b/test/test_pebble.py
@@ -3360,25 +3360,23 @@ class TestExecError:
 
     def test_str(self):
         e = pebble.ExecError[str](['x'], 1, None, None)
-        assert str(e) == "non-zero exit code 1 executing ['x']"
+        assert str(e) == "non-zero exit code 1 executing 'x'"
 
         e = pebble.ExecError(['x'], 1, 'only-out', None)
-        assert str(e) == "non-zero exit code 1 executing ['x'], stdout='only-out'"
+        assert str(e) == "non-zero exit code 1 executing 'x', stdout='only-out'"
 
         e = pebble.ExecError(['x'], 1, None, 'only-err')
-        assert str(e) == "non-zero exit code 1 executing ['x'], stderr='only-err'"
+        assert str(e) == "non-zero exit code 1 executing 'x', stderr='only-err'"
 
-        e = pebble.ExecError(['a', 'b'], 1, 'out', 'err')
-        assert (
-            str(e) == "non-zero exit code 1 executing ['a', 'b'], " + "stdout='out', stderr='err'"
-        )
+        e = pebble.ExecError(['a', 'b', 'c'], 1, 'out', 'err')
+        assert str(e) == "non-zero exit code 1 executing 'a', " + "stdout='out', stderr='err'"
 
     def test_str_truncated(self):
         e = pebble.ExecError(['foo'], 2, 'longout', 'longerr')
         e.STR_MAX_OUTPUT = 5  # type: ignore
         assert (
             str(e)
-            == "non-zero exit code 2 executing ['foo'], "
+            == "non-zero exit code 2 executing 'foo', "
             + "stdout='longo' [truncated], stderr='longe' [truncated]"
         )
```
