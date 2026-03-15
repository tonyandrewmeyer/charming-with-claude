# fix: add missing vars section in tox.ini (#43)

**Repository**: charmhub-listing-review
**Commit**: [a7acfeeb](https://github.com/canonical/charmhub-listing-review/commit/a7acfeeb4a5132f078f14108c9c96e17d28db151)
**Date**: 2026-01-20

## Classification

| Field | Value |
|-------|-------|
| Bug Area | ci-build |
| Bug Type | config |
| Severity | medium |
| Fix Category | build-fix |

## Summary

Missing [vars] section in tox.ini broke test runs; also fixed test mock to JSON-encode output

## Commit Message

Adds the `[vars]` section in `tox.ini`, since it's referred to to get
the source location.

Also a drive-by to fix one test, which was failing to JSON encode mock
output.

Fixes #36

## Changed Files

- M	src/charmhub_listing_review/update_issue.py
- M	tests/unit/test_update_issue.py
- M	tox.ini

## Diff

```diff
diff --git a/src/charmhub_listing_review/update_issue.py b/src/charmhub_listing_review/update_issue.py
index 610111b..d9068de 100755
--- a/src/charmhub_listing_review/update_issue.py
+++ b/src/charmhub_listing_review/update_issue.py
@@ -190,9 +190,7 @@ def get_details_from_issue(issue_number: int):
     return cast('_IssueData', issue_data)
 
 
-def assign_review(
-    issue_number: int, reviewers_file: pathlib.Path, dry_run: bool = False
-):
+def assign_review(issue_number: int, reviewers_file: pathlib.Path, dry_run: bool = False):
     """Assign the issue to a team.
 
     We assign the issue to a single person (generally the manager) from a
diff --git a/tests/unit/test_update_issue.py b/tests/unit/test_update_issue.py
index 32cb8de..f7ec8a1 100644
--- a/tests/unit/test_update_issue.py
+++ b/tests/unit/test_update_issue.py
@@ -14,6 +14,7 @@
 
 """Test the issue comment generation."""
 
+import json
 import pathlib
 from unittest import mock
 
@@ -104,7 +105,7 @@ https://ci.example.com/integration
 ### Documentation Link
 https://docs.example.com
 """
-    mock_subprocess_run.return_value = mock.Mock(stdout=issue_body)
+    mock_subprocess_run.return_value = mock.Mock(stdout=json.dumps({'body': issue_body}))
     details = update_issue.get_details_from_issue(123)
     assert details['name'] == 'my-charm'
     assert details['demo_url'] == 'https://demo.example.com'
diff --git a/tox.ini b/tox.ini
index 9724e21..b48b564 100644
--- a/tox.ini
+++ b/tox.ini
@@ -17,6 +17,9 @@ skipsdist=True
 skip_missing_interpreters = True
 envlist = lint, unit
 
+[vars]
+src_path = {toxinidir}/src
+
 [testenv]
 runner = uv-venv-lock-runner
 setenv =
```
