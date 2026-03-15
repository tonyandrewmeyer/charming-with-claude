# Fix branch for actions-operator

**Repository**: charm-ubuntu
**Commit**: [89a3e4cf](https://github.com/canonical/charm-ubuntu/commit/89a3e4cf86490b231ae040979e1e7676246b33a0)
**Date**: 2022-02-02

## Classification

| Field | Value |
|-------|-------|
| Bug Area | ci-build |
| Bug Type | config |
| Severity | medium |
| Fix Category | ci-fix |

## Summary

CI referenced 'master' branch of actions-operator which was renamed to 'main'

## Commit Message

It was renamed to "main" upstream.

## Changed Files

- M	.github/workflows/tests.yml

## Diff

```diff
diff --git a/.github/workflows/tests.yml b/.github/workflows/tests.yml
index 694ee1f..fb2f6e1 100644
--- a/.github/workflows/tests.yml
+++ b/.github/workflows/tests.yml
@@ -52,6 +52,6 @@ jobs:
         run: |
           pip install tox
       - name: Setup operator environment
-        uses: charmed-kubernetes/actions-operator@master
+        uses: charmed-kubernetes/actions-operator@main
       - name: Run test
         run: tox -e integration
```
