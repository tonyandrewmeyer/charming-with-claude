# fix: explicitly provide the path to the reviewers file (#42)

**Repository**: charmhub-listing-review
**Commit**: [72b60724](https://github.com/canonical/charmhub-listing-review/commit/72b60724737dc6142b4da199cb537fe6cc54f58a)
**Date**: 2026-01-20

## Classification

| Field | Value |
|-------|-------|
| Bug Area | automation |
| Bug Type | api-contract |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Reviewers file path was hardcoded to CI runner path; made it a required CLI argument

## Commit Message

Tidy up the use of the reviewers.json file by explicitly providing the
path to it when used (most typically by the GitHub actions workflow).

Refs #13

## Changed Files

- M	.github/workflows/review-request.yaml
- M	src/charmhub_listing_review/update_issue.py
- M	tests/unit/test_update_issue.py

## Diff

```diff
diff --git a/.github/workflows/review-request.yaml b/.github/workflows/review-request.yaml
index 8e9aab7..6b1aee5 100644
--- a/.github/workflows/review-request.yaml
+++ b/.github/workflows/review-request.yaml
@@ -34,8 +34,6 @@ jobs:
         env:
             GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
         run: |
-            # TODO: This is not the best way to run the script, we should clean this up, but just
-            # getting it working for now.
             uv venv
             uv pip install .
-            uv run update-issue --issue-number "${{ github.event.issue.number }}"
+            uv run update-issue --issue-number "${{ github.event.issue.number }}" --reviewers-file "${{ github.workspace }}/reviewers.yaml"
diff --git a/src/charmhub_listing_review/update_issue.py b/src/charmhub_listing_review/update_issue.py
index fd50be4..610111b 100755
--- a/src/charmhub_listing_review/update_issue.py
+++ b/src/charmhub_listing_review/update_issue.py
@@ -190,7 +190,9 @@ def get_details_from_issue(issue_number: int):
     return cast('_IssueData', issue_data)
 
 
-def assign_review(issue_number: int, dry_run: bool = False):
+def assign_review(
+    issue_number: int, reviewers_file: pathlib.Path, dry_run: bool = False
+):
     """Assign the issue to a team.
 
     We assign the issue to a single person (generally the manager) from a
@@ -204,10 +206,6 @@ def assign_review(issue_number: int, dry_run: bool = False):
     are expected to simply ping them in a comment. Once they have submitted
     their review, the author can interact with them in the usual way.
     """
-    # TODO: Figure out where this should be and how the script should locate it.
-    reviewers_file = pathlib.Path(
-        '/home/runner/work/charmhub-listing-review/charmhub-listing-review/reviewers.yaml'
-    )
     with reviewers_file.open('r') as f:
         reviewers_data = yaml.safe_load(f)
     reviewers = reviewers_data['reviewers']
@@ -226,7 +224,13 @@ def assign_review(issue_number: int, dry_run: bool = False):
     return reviewer
 
 
-def update_gh_issue(issue_number: int, summary: str, comment: str, dry_run: bool = False):
+def update_gh_issue(
+    issue_number: int,
+    summary: str,
+    comment: str,
+    reviewers_file: pathlib.Path,
+    dry_run: bool = False,
+):
     """Update the specified GitHub issue with the latest generated comment."""
     # Update the issue title.
     if dry_run:
@@ -245,7 +249,11 @@ def update_gh_issue(issue_number: int, summary: str, comment: str, dry_run: bool
         text=True,
     )
     assignees = json.loads(gh.stdout.strip()).get('assignees', [])
-    manager = assignees[0]['login'] if assignees else assign_review(issue_number, dry_run)
+    manager = (
+        assignees[0]['login']
+        if assignees
+        else assign_review(issue_number, reviewers_file, dry_run)
+    )
     request_review = re.sub(
         r'\s',
         ' ',
@@ -318,6 +326,12 @@ def main():
     parser.add_argument(
         '--issue-number', type=int, help='The issue number to update', required=True
     )
+    parser.add_argument(
+        '--reviewers-file',
+        type=pathlib.Path,
+        help='Path to the reviewers YAML file',
+        required=True,
+    )
     parser.add_argument(
         '--dry-run', action='store_true', help='Do not update the issue, just print the output'
     )
@@ -335,7 +349,13 @@ def main():
     )
     comment = apply_automated_checks(issue_data, comment)
 
-    update_gh_issue(args.issue_number, summary, comment, dry_run=args.dry_run)
+    update_gh_issue(
+        args.issue_number,
+        summary,
+        comment,
+        args.reviewers_file,
+        dry_run=args.dry_run,
+    )
 
 
 if __name__ == '__main__':
diff --git a/tests/unit/test_update_issue.py b/tests/unit/test_update_issue.py
index 98e8c25..32cb8de 100644
--- a/tests/unit/test_update_issue.py
+++ b/tests/unit/test_update_issue.py
@@ -14,6 +14,7 @@
 
 """Test the issue comment generation."""
 
+import pathlib
 from unittest import mock
 
 import charmhub_listing_review.update_issue as update_issue
@@ -37,7 +38,7 @@ def test_assign_review_multiple_teams(
     mock_open.return_value.__enter__.return_value = mock.Mock()
     mock_subprocess_run.return_value = mock.Mock()
     mock_random_choice.return_value = '@bob'
-    reviewer = update_issue.assign_review(42)
+    reviewer = update_issue.assign_review(42, pathlib.Path('reviewers.yaml'))
     assert reviewer == '@bob'
     mock_subprocess_run.assert_called_once_with(
         [
@@ -64,7 +65,7 @@ def test_assign_review_single_team(mock_open, mock_yaml_load, mock_subprocess_ru
     mock_yaml_load.return_value = reviewers_yaml
     mock_open.return_value.__enter__.return_value = mock.Mock()
     mock_subprocess_run.return_value = mock.Mock()
-    reviewer = update_issue.assign_review(99)
+    reviewer = update_issue.assign_review(99, pathlib.Path('reviewers.yaml'))
     assert reviewer == '@alice'
     mock_subprocess_run.assert_called_once_with(
         [
```
