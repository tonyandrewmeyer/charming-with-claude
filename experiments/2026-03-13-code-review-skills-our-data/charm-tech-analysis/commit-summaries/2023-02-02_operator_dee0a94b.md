# fixed asset paths

**Repository**: operator
**Commit**: [dee0a94b](https://github.com/canonical/operator/commit/dee0a94b1c693f3dfb0aeb45b53fe2ec130683fa)
**Date**: 2023-02-02

## Classification

| Field | Value |
|-------|-------|
| Bug Area | ci-build |
| Bug Type | logic-error |
| Severity | low |
| Fix Category | ci-fix |

## Summary

ed asset paths

## Changed Files

- M	.github/workflows/build_wheels.yaml

## Diff

```diff
diff --git a/.github/workflows/build_wheels.yaml b/.github/workflows/build_wheels.yaml
index 2e22a30..132e97a 100644
--- a/.github/workflows/build_wheels.yaml
+++ b/.github/workflows/build_wheels.yaml
@@ -51,8 +51,8 @@ jobs:
           GITHUB_TOKEN: ${{ github.token }}
         with:
           upload_url: ${{ steps.create_release.outputs.upload_url }}
-          asset_path: ./dist/scenario-${{ steps.get_version.outputs.VERSION }}-py3-none-any.whl
-          asset_name: scenario-${{ steps.get_version.outputs.VERSION }}-py3-none-any.whl
+          asset_path: ./dist/ops_scenario-${{ steps.get_version.outputs.VERSION }}-py3-none-any.whl
+          asset_name: ops_scenario-${{ steps.get_version.outputs.VERSION }}-py3-none-any.whl
           asset_content_type: application/wheel
 
       - name: Publish to TestPyPI
```
