# Attempt to fix model.py for Python 3.5.2 (default on Xenial) (#520)

**Repository**: operator
**Commit**: [be1fdf06](https://github.com/canonical/operator/commit/be1fdf0698e33ed2274eb417da5b64f2656239fb)
**Date**: 2021-04-23

## Classification

| Field | Value |
|-------|-------|
| Bug Area | security |
| Bug Type | version-compat |
| Severity | high |
| Fix Category | source-fix |

## Summary

attempt to fix model.py for python 3.5.2 (default on xenial)

## Commit Message

Fixes #517

## Changed Files

- M	ops/model.py

## Diff

```diff
diff --git a/ops/model.py b/ops/model.py
index d4e9b08..f80eb52 100644
--- a/ops/model.py
+++ b/ops/model.py
@@ -1049,8 +1049,10 @@ class Container:
         """Stop given service(s) by name."""
         self._pebble.stop_services(service_names)
 
-    def add_layer(self, label: str, layer: typing.Union[str, typing.Dict, 'pebble.Layer'], *,
-                  combine: bool = False):
+    # TODO(benhoyt) - should be: layer: typing.Union[str, typing.Dict, 'pebble.Layer'],
+    # but this breaks on Python 3.5.2 (the default on Xenial). See:
+    # https://github.com/canonical/operator/issues/517
+    def add_layer(self, label: str, layer, *, combine: bool = False):
         """Dynamically add a new layer onto the Pebble configuration layers.
 
         Args:
```
