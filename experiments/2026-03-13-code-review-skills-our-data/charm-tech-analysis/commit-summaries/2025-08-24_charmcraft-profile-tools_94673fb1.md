# fix implemented integration test

**Repository**: charmcraft-profile-tools
**Commit**: [94673fb1](https://github.com/canonical/charmcraft-profile-tools/commit/94673fb182b7aa95655e4f84ee896f8d09bb88f1)
**Date**: 2025-08-24

## Classification

| Field | Value |
|-------|-------|
| Bug Area | testing |
| Bug Type | test-fix |
| Severity | low |
| Fix Category | test-fix |

## Summary

Integration test expected wrong workload version (3.14 placeholder instead of actual 1.0.0)

## Changed Files

- M	kubernetes-dev-jubilant-implemented/tests/integration/test_charm.py

## Diff

```diff
diff --git a/kubernetes-dev-jubilant-implemented/tests/integration/test_charm.py b/kubernetes-dev-jubilant-implemented/tests/integration/test_charm.py
index 38071b1..d13fbfe 100644
--- a/kubernetes-dev-jubilant-implemented/tests/integration/test_charm.py
+++ b/kubernetes-dev-jubilant-implemented/tests/integration/test_charm.py
@@ -31,4 +31,4 @@ def test_deploy(charm: pathlib.Path, juju: jubilant.Juju):
 def test_workload_version_is_set(juju: jubilant.Juju):
     """Check that the correct version of the workload is running."""
     version = juju.status().apps["my-application"].version
-    assert version == "3.14"  # Replace 3.14 by the expected version of the workload.
+    assert version == "1.0.0"  # (Bug) workload ought to return 1.0.1 instead.
```
