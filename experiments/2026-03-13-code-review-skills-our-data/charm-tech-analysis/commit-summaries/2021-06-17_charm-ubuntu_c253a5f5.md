# Update Black and fix formatting

**Repository**: charm-ubuntu
**Commit**: [c253a5f5](https://github.com/canonical/charm-ubuntu/commit/c253a5f502c662acc7d2b39f61ba4cf405177d7c)
**Date**: 2021-06-17

## Classification

| Field | Value |
|-------|-------|
| Bug Area | testing |
| Bug Type | other |
| Severity | low |
| Fix Category | source-fix |

## Summary

New Black version enforced spaces around docstrings; updated formatting

## Commit Message

A new version of Black started enforcing spaces around docstrings.

## Changed Files

- M	tests/integration/test_charm.py

## Diff

```diff
diff --git a/tests/integration/test_charm.py b/tests/integration/test_charm.py
index 33ed4bc..807f9a0 100644
--- a/tests/integration/test_charm.py
+++ b/tests/integration/test_charm.py
@@ -18,7 +18,7 @@ async def test_build_and_deploy(ops_test):
 
 
 async def test_app_versions(ops_test):
-    """ Validate that the app versions are correct. """
+    """Validate that the app versions are correct."""
     expected = {
         "focal": "20.04",
         "bionic": "18.04",
```
