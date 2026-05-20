# fix fmt tox env

**Repository**: operator
**Commit**: [870cdeff](https://github.com/canonical/operator/commit/870cdeff229f7331cc8b40d6fa44a675e50992cd)
**Date**: 2022-11-28

## Classification

| Field | Value |
|-------|-------|
| Bug Area | testing-framework |
| Bug Type | other |
| Severity | medium |
| Fix Category | ci-fix |

## Summary

fmt tox env

## Changed Files

- M	tox.ini

## Diff

```diff
diff --git a/tox.ini b/tox.ini
index 5c5d3e1..f9c5cbc 100644
--- a/tox.ini
+++ b/tox.ini
@@ -30,5 +30,5 @@ deps =
     black
     isort
 commands =
-    black tests scenario runtime
-    isort --profile black tests scenario runtime
+    black tests scenario scenario/runtime
+    isort --profile black tests scenario scenario/runtime
```
