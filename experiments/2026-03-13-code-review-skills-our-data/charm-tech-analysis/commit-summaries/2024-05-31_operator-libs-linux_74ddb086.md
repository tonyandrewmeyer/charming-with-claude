# snap.py: fix snap.get optional key (#125)

**Repository**: operator-libs-linux
**Commit**: [74ddb086](https://github.com/canonical/operator-libs-linux/commit/74ddb086a64dd9c0c8c588aff293ef3d4c2274a4)
**Date**: 2024-05-31

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | edge-case |
| Severity | medium |
| Fix Category | source-fix |

## Summary

snap.get with falsy key (None) crashed instead of returning all config values

## Commit Message

Fix snap.get method to handle the case where the key is falsy. Treat it
as no key provided, which results in the expected behavior to get all
values from snap configs.

## Changed Files

- M	lib/charms/operator_libs_linux/v2/snap.py
- M	tests/integration/test_snap.py

## Diff

```diff
diff --git a/lib/charms/operator_libs_linux/v2/snap.py b/lib/charms/operator_libs_linux/v2/snap.py
index 6d4dc38..9d09a78 100644
--- a/lib/charms/operator_libs_linux/v2/snap.py
+++ b/lib/charms/operator_libs_linux/v2/snap.py
@@ -83,7 +83,7 @@ LIBAPI = 2
 
 # Increment this PATCH version before using `charmcraft publish-lib` or reset
 # to 0 if you are raising the major API version
-LIBPATCH = 6
+LIBPATCH = 7
 
 
 # Regex to locate 7-bit C1 ANSI sequences
@@ -319,7 +319,10 @@ class Snap(object):
                 Default is to return a string.
         """
         if typed:
-            config = json.loads(self._snap("get", ["-d", key]))
+            args = ["-d"]
+            if key:
+                args.append(key)
+            config = json.loads(self._snap("get", args))
             if key:
                 return config.get(key)
             return config
diff --git a/tests/integration/test_snap.py b/tests/integration/test_snap.py
index 640b568..c3597ae 100644
--- a/tests/integration/test_snap.py
+++ b/tests/integration/test_snap.py
@@ -116,6 +116,22 @@ def test_snap_set_and_get_with_typed():
 
     assert lxd.get("criu.enable", typed=True) == "true"
     assert lxd.get("ceph.external", typed=True) == "false"
+    assert lxd.get(None, typed=True) == {
+        "true": True,
+        "false": False,
+        "integer": 1,
+        "float": 2.0,
+        "list": [1, 2.0, True, False, None],
+        "dict": {
+            "true": True,
+            "false": False,
+            "integer": 1,
+            "float": 2.0,
+            "list": [1, 2.0, True, False, None],
+        },
+        "criu": {"enable": "true"},
+        "ceph": {"external": "false"},
+    }
 
 
 def test_snap_set_and_get_untyped():
```
