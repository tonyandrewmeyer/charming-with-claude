# fix: add a temporary fix for running the workflow (#11)

**Repository**: charmhub-listing-review
**Commit**: [b3fec634](https://github.com/canonical/charmhub-listing-review/commit/b3fec63427d1184333a13b889d92ec2f70dc32f7)
**Date**: 2025-08-28

## Classification

| Field | Value |
|-------|-------|
| Bug Area | ci-build |
| Bug Type | config |
| Severity | medium |
| Fix Category | ci-fix |

## Summary

GitHub workflow ran script directly instead of installing package first, causing import failures

## Commit Message

This was tested previously in my test repo, but I missed copying it over
to here.

This is definitely not the right solution, but it works and so suffices
for now. I'll work on a proper solution as part of the PR for letting
people run the evaluation themselves.

## Changed Files

- M	.github/workflows/review-request.yaml

## Diff

```diff
diff --git a/.github/workflows/review-request.yaml b/.github/workflows/review-request.yaml
index 11cbdbf..93ab769 100644
--- a/.github/workflows/review-request.yaml
+++ b/.github/workflows/review-request.yaml
@@ -50,4 +50,8 @@ jobs:
         env:
             GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
         run: |
-            uv run src/charmhub_listing_review/update_issue.py --issue-number "${{ github.event.issue.number }}" --path-to-ops=operator --path-to-charmcraft=charmcraft
+            # TODO: This is not the best way to run the script, we should clean this up, but just
+            # getting it working for now.
+            uv venv
+            uv pip install .
+            uv run update-issue --issue-number "${{ github.event.issue.number }}" --path-to-ops=operator --path-to-charmcraft=charmcraft
```
