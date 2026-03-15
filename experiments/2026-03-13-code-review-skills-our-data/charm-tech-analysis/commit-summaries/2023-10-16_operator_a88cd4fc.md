# Remove the temporary fix, which shouldn't be required any more. (#1046)

**Repository**: operator
**Commit**: [a88cd4fc](https://github.com/canonical/operator/commit/a88cd4fcf945f08fab94f44eaf4d937b15df5a04)
**Date**: 2023-10-16

## Classification

| Field | Value |
|-------|-------|
| Bug Area | ci-build |
| Bug Type | logic-error |
| Severity | low |
| Fix Category | ci-fix |

## Summary

remove the temporary fix, which shouldn't be required any more

## Changed Files

- M	.github/workflows/db-charm-tests.yaml

## Diff

```diff
diff --git a/.github/workflows/db-charm-tests.yaml b/.github/workflows/db-charm-tests.yaml
index 2877f14..46cef24 100644
--- a/.github/workflows/db-charm-tests.yaml
+++ b/.github/workflows/db-charm-tests.yaml
@@ -43,8 +43,3 @@ jobs:
 
       - name: Run the charm's unit tests
         run: tox -vve unit
-        # TODO: remove this once https://github.com/canonical/mysql-k8s-operator/pull/316 is fixed
-        env:
-          # This env var is only to indicate Juju version to "simulate" in the mysqk-k8s-operator
-          # unit tests. No libjuju is being actually used in unit testing.
-          LIBJUJU_VERSION_SPECIFIER: 3.1
```
