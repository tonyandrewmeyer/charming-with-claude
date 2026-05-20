# fix: Correct Pietro's GitHub username (#49)

**Repository**: charmhub-listing-review
**Commit**: [b45e0d53](https://github.com/canonical/charmhub-listing-review/commit/b45e0d53a2d466d4aee8f07b714c8beca33c56f4)
**Date**: 2026-01-21

## Classification

| Field | Value |
|-------|-------|
| Bug Area | config |
| Bug Type | data-validation |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Incorrect GitHub username in reviewers.yaml caused review assignment to fail

## Commit Message

Either wrong in directory, which is currently down, or I copied it
incorrectly.

## Changed Files

- M	reviewers.yaml

## Diff

```diff
diff --git a/reviewers.yaml b/reviewers.yaml
index 7b80541..50d6241 100644
--- a/reviewers.yaml
+++ b/reviewers.yaml
@@ -10,7 +10,7 @@ reviewers:
     "@sed-i":
         name: "Leon Mintz"
         team: "Observability Core"
-    "@ppasotti":
+    "@pietropasotti":
         name: "Pietro Pasotti"
         team: "Observability Tracing"
     "@simskij":
```
