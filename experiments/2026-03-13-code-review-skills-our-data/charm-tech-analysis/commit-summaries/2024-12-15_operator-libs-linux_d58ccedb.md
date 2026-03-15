# fix: Task status can be `Do` and should not raise an error. (#140)

**Repository**: operator-libs-linux
**Commit**: [d58ccedb](https://github.com/canonical/operator-libs-linux/commit/d58ccedb1aef66eee55f7008dcc5bebabf94e7e1)
**Date**: 2024-12-15

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | edge-case |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Snap task status 'Do' (ready but not started) was treated as an error instead of a valid pending state

## Commit Message

Resolves #139

* fix: Task status can be Do.

The task status can be `Do` and should not be considered an error.
This status means that the task is ready to start but hasn't started yet.

* chore: Bump libpatch

## Changed Files

- M	lib/charms/operator_libs_linux/v2/snap.py
- M	tests/unit/test_snap.py

## Diff

```diff
diff --git a/lib/charms/operator_libs_linux/v2/snap.py b/lib/charms/operator_libs_linux/v2/snap.py
index d84b7d8..d14f864 100644
--- a/lib/charms/operator_libs_linux/v2/snap.py
+++ b/lib/charms/operator_libs_linux/v2/snap.py
@@ -84,7 +84,7 @@ LIBAPI = 2
 
 # Increment this PATCH version before using `charmcraft publish-lib` or reset
 # to 0 if you are raising the major API version
-LIBPATCH = 8
+LIBPATCH = 9
 
 
 # Regex to locate 7-bit C1 ANSI sequences
@@ -787,7 +787,7 @@ class SnapClient:
             status = response["status"]
             if status == "Done":
                 return response.get("data")
-            if status == "Doing":
+            if status == "Doing" or status == "Do":
                 time.sleep(0.1)
                 continue
             if status == "Wait":
diff --git a/tests/unit/test_snap.py b/tests/unit/test_snap.py
index 0c02def..4368b18 100644
--- a/tests/unit/test_snap.py
+++ b/tests/unit/test_snap.py
@@ -701,6 +701,7 @@ class TestSocketClient(unittest.TestCase):
             shutdown()
 
     def test_wait_changes(self):
+        change_started = False
         change_finished = False
 
         def _request_raw(
@@ -711,6 +712,7 @@ class TestSocketClient(unittest.TestCase):
             data: bytes = None,
         ) -> typing.IO[bytes]:
             nonlocal change_finished
+            nonlocal change_started
             if method == "PUT" and path == "snaps/test/conf":
                 return io.BytesIO(
                     json.dumps(
@@ -723,6 +725,36 @@ class TestSocketClient(unittest.TestCase):
                         }
                     ).encode("utf-8")
                 )
+            if method == "GET" and path == "changes/97" and not change_started:
+                change_started = True
+                return io.BytesIO(
+                    json.dumps(
+                        {
+                            "type": "sync",
+                            "status-code": 200,
+                            "status": "OK",
+                            "result": {
+                                "id": "97",
+                                "kind": "configure-snap",
+                                "summary": 'Change configuration of "test" snap',
+                                "status": "Do",
+                                "tasks": [
+                                    {
+                                        "id": "1028",
+                                        "kind": "run-hook",
+                                        "summary": 'Run configure hook of "test" snap',
+                                        "status": "Do",
+                                        "progress": {"label": "", "done": 0, "total": 1},
+                                        "spawn-time": "2024-11-28T20:02:47.498399651+00:00",
+                                        "data": {"affected-snaps": ["test"]},
+                                    }
+                                ],
+                                "ready": False,
+                                "spawn-time": "2024-11-28T20:02:47.49842583+00:00",
+                            },
+                        }
+                    ).encode("utf-8")
+                )
             if method == "GET" and path == "changes/97" and not change_finished:
                 change_finished = True
                 return io.BytesIO(
```
