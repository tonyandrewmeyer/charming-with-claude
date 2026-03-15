# fix: temporarily hard-code the CI location for the reviewers file (#12)

**Repository**: charmhub-listing-review
**Commit**: [c8be66a8](https://github.com/canonical/charmhub-listing-review/commit/c8be66a8a934ed93f80b6f54381fb7879137035d)
**Date**: 2025-08-28

## Classification

| Field | Value |
|-------|-------|
| Bug Area | automation |
| Bug Type | config |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Reviewers file path resolution using __file__ did not work in CI; hardcoded as temporary fix

## Commit Message

Copying this temporary fix from my test repo.

This is definitely not the right fix long term, but I'm not sure where
the reviewers file should live, or the best way for the script to find
it (and maybe it should just use CODEOWNERs or the GitHub list of users
with the right access?).

For now, this lets the workflow run.

## Changed Files

- M	src/charmhub_listing_review/update_issue.py

## Diff

```diff
diff --git a/src/charmhub_listing_review/update_issue.py b/src/charmhub_listing_review/update_issue.py
index ed2d709..540f42c 100755
--- a/src/charmhub_listing_review/update_issue.py
+++ b/src/charmhub_listing_review/update_issue.py
@@ -272,7 +272,10 @@ def assign_review(issue_number: int, dry_run: bool = False):
     are expected to simply ping them in a comment. Once they have submitted
     their review, the author can interact with them in the usual way.
     """
-    reviewers_file = pathlib.Path(__file__).parent.parent.parent / 'reviewers.yaml'
+     # TODO: Figure out where this should be and how the script should locate it.
+    reviewers_file = pathlib.Path(
+        '/home/runner/work/charmhub-listing-review/charmhub-listing-review/reviewers.yaml'
+    )
     with reviewers_file.open('r') as f:
         reviewers_data = yaml.safe_load(f)
     reviewers = reviewers_data['reviewers']
```
