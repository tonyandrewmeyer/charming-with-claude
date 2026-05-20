# fixed builder again

**Repository**: operator
**Commit**: [f6daaab3](https://github.com/canonical/operator/commit/f6daaab3c66906b197a866677b0c6962d2087510)
**Date**: 2023-02-02

## Classification

| Field | Value |
|-------|-------|
| Bug Area | ci-build |
| Bug Type | logic-error |
| Severity | low |
| Fix Category | ci-fix |

## Summary

ed builder again

## Changed Files

- M	.github/workflows/build_wheels.yaml

## Diff

```diff
diff --git a/.github/workflows/build_wheels.yaml b/.github/workflows/build_wheels.yaml
index 59fc86c..70de271 100644
--- a/.github/workflows/build_wheels.yaml
+++ b/.github/workflows/build_wheels.yaml
@@ -16,8 +16,8 @@ jobs:
 
       - uses: actions/setup-python@v3
 
-      - name: Install wheel
-        run: pip install wheel
+      - name: Install build
+        run: pip install build
 
       - name: Build wheel
         run: python -m build
```
