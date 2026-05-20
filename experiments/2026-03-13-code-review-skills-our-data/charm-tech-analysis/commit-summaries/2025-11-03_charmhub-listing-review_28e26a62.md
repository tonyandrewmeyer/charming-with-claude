# Fix code review issues and duplication problem

**Repository**: charmhub-listing-review
**Commit**: [28e26a62](https://github.com/canonical/charmhub-listing-review/commit/28e26a62356c03424e8d1334ccf0856f26dc8d85)
**Date**: 2025-11-03

## Classification

| Field | Value |
|-------|-------|
| Bug Area | automation |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Automated checks duplicated checklist items instead of updating them in place

## Commit Message

- Use dataclasses.dataclass style instead of importing dataclass directly
- Restore noqa comment for subprocess import (S404)
- Fix apply_automated_checks to update items in place instead of duplicating
- Update test to match new behavior where items are updated not appended
- Remove unused CheckResult import from update_issue.py

Co-authored-by: tonyandrewmeyer <826522+tonyandrewmeyer@users.noreply.github.com>

## Changed Files

- M	src/charmhub_listing_review/evaluate.py
- M	src/charmhub_listing_review/update_issue.py
- M	tests/unit/test_update_issue.py

## Diff

```diff
diff --git a/src/charmhub_listing_review/evaluate.py b/src/charmhub_listing_review/evaluate.py
index 9198e8c..d36fac6 100644
--- a/src/charmhub_listing_review/evaluate.py
+++ b/src/charmhub_listing_review/evaluate.py
@@ -23,6 +23,7 @@ for the reviewer, and is also a way for charm publishers to check their charm
 against the listing requirements before submitting a listing request.
 """
 
+import dataclasses
 import hashlib
 import pathlib
 import re
@@ -31,14 +32,13 @@ import subprocess
 import tempfile
 import tomllib
 import xml.etree.ElementTree as ET
-from dataclasses import dataclass
 from typing import Any
 
 import requests
 import yaml
 
 
-@dataclass
+@dataclasses.dataclass
 class CheckResult:
     """Result of an automated check.
 
diff --git a/src/charmhub_listing_review/update_issue.py b/src/charmhub_listing_review/update_issue.py
index 11b956b..b719cd0 100755
--- a/src/charmhub_listing_review/update_issue.py
+++ b/src/charmhub_listing_review/update_issue.py
@@ -33,14 +33,14 @@ import json
 import pathlib
 import random
 import re
-import subprocess
+import subprocess  # noqa: S404
 import urllib.error
 import urllib.request
 from typing import TypedDict, cast
 
 import yaml
 
-from .evaluate import CheckResult, evaluate
+from .evaluate import evaluate
 
 BEST_PRACTICE_SOURCE = 'https://raw.githubusercontent.com/canonical/operator/refs/heads/main/docs/reuse/best-practices.txt'
 
@@ -309,13 +309,9 @@ def apply_automated_checks(issue_data: _IssueData, comment: str) -> str:
         issue_data['security_link'],
     )
 
-    # Create a mapping of check IDs to their results
-    check_results: dict[str, CheckResult] = {result.id: result for result in results}
-
-    # Build the automated checks section with IDs embedded as HTML comments
-    automated_section_lines: list[str] = []
-    for check_id, result in check_results.items():
-        # Determine checkbox state based on result
+    # Update existing checklist items by adding IDs and updating checkbox state.
+    for result in results:
+        # Determine checkbox state based on result.
         if result.passed is True:
             checkbox = '* [x]'
         elif result.passed is False:
@@ -323,41 +319,22 @@ def apply_automated_checks(issue_data: _IssueData, comment: str) -> str:
         else:  # result.passed is None
             checkbox = '* [ ]'
 
-        # Add the check with an ID embedded as an HTML comment
-        automated_section_lines.append(
-            f'<!-- check-id: {check_id} -->{checkbox} {result.description}'
-        )
+        # Create the line with ID embedded as an HTML comment.
+        result_line = f'<!-- check-id: {result.id} -->{checkbox} {result.description}'
 
-    if automated_section_lines:
-        # Insert the automated checks section after "Best practices" heading
-        best_practices_marker = '### Best practices'
-        if best_practices_marker in comment:
-            # Find where to insert (after the best practices intro text)
-            parts = comment.split(best_practices_marker, 1)
-            if len(parts) == 2:
-                # Split the second part to find where the list starts
-                after_header = parts[1]
-                # Find the end of the intro paragraph
-                intro_end = after_header.find('\n\n')
-                if intro_end != -1:
-                    intro = after_header[:intro_end]
-                    rest = after_header[intro_end:]
-                    comment = (
-                        parts[0]
-                        + best_practices_marker
-                        + intro
-                        + '\n\n'
-                        + '\n'.join(automated_section_lines)
-                        + rest
-                    )
-    else:
-        # No automated checks, just add them at the end before closing
-        close_marker = '\n```\n</details>\n'
-        if close_marker in comment:
-            comment = comment.replace(
-                close_marker,
-                '\n\n' + '\n'.join(automated_section_lines) + close_marker,
-            )
+        # Try to find and replace the matching checklist item.
+        # Match pattern: "* [ ] " followed by the description.
+        pattern = rf'\* \[ \] {re.escape(result.description)}'
+        if re.search(pattern, comment):
+            # Replace the item with the version that has ID and updated checkbox.
+            comment = re.sub(pattern, result_line, comment, count=1)
+        else:
+            # Check if it already has an ID (from a previous run).
+            id_pattern = rf'<!-- check-id: {re.escape(result.id)} -->\*\s*\[[x ]\]'
+            if re.search(id_pattern, comment):
+                # Update the existing item with the new checkbox state.
+                replacement = f'<!-- check-id: {result.id} -->{checkbox}'
+                comment = re.sub(id_pattern, replacement, comment, count=1)
 
     return comment
 
diff --git a/tests/unit/test_update_issue.py b/tests/unit/test_update_issue.py
index c95175d..da48c43 100644
--- a/tests/unit/test_update_issue.py
+++ b/tests/unit/test_update_issue.py
@@ -142,12 +142,16 @@ def test_apply_automated_checks():
         security_link='https://github.com/canonical/test-charm/blob/main/SECURITY.md',
     )
 
-    # Create a comment with a placeholder section
+    # Create a comment with checklist items that can be auto-checked.
     comment = """
 ### Best practices
 
 The following best practices are recommended for all charms.
 
+* [ ] The charm provides contribution guidelines.
+* [ ] The charm provides a license statement.
+* [ ] The charm provides a security statement.
+
 ```
 </details>
 """
@@ -174,7 +178,7 @@ The following best practices are recommended for all charms.
     with mock.patch('charmhub_listing_review.update_issue.evaluate', return_value=mock_results):
         result = update_issue.apply_automated_checks(issue_data, comment)
 
-    # Verify that the result contains the checks with IDs
+    # Verify that the result contains the checks with IDs and updated checkbox states.
     assert (
         '<!-- check-id: contribution-guidelines -->* [x] '
         'The charm provides contribution guidelines.' in result
```
