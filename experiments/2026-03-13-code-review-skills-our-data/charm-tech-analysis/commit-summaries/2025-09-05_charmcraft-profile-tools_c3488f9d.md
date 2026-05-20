# fix name of charm checks

**Repository**: charmcraft-profile-tools
**Commit**: [c3488f9d](https://github.com/canonical/charmcraft-profile-tools/commit/c3488f9d922e23ec941b799fa5b930b4b89872fd)
**Date**: 2025-09-05

## Classification

| Field | Value |
|-------|-------|
| Bug Area | ci-build |
| Bug Type | config |
| Severity | low |
| Fix Category | ci-fix |

## Summary

GitHub workflow had wrong display name ('Code checks' instead of 'Charm checks')

## Changed Files

- M	.github/workflows/charm-checks.yaml

## Diff

```diff
diff --git a/.github/workflows/charm-checks.yaml b/.github/workflows/charm-checks.yaml
index 4d2e340..9cce82c 100644
--- a/.github/workflows/charm-checks.yaml
+++ b/.github/workflows/charm-checks.yaml
@@ -1,4 +1,4 @@
-name: Code checks
+name: Charm checks
 
 on:
   pull_request:
```
