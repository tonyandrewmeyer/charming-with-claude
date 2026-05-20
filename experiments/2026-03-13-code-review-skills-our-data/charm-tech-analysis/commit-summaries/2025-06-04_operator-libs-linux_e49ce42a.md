# fix: refresh with classic (#161)

**Repository**: operator-libs-linux
**Commit**: [e49ce42a](https://github.com/canonical/operator-libs-linux/commit/e49ce42a6ab4b3be85405d8a43a31ff2a5906880)
**Date**: 2025-06-04

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | logic-error |
| Severity | high |
| Fix Category | source-fix |

## Summary

Snap refresh was missing --classic flag for classically-confined snaps

## Changed Files

- M	.gitignore
- M	lib/charms/operator_libs_linux/v2/snap.py
- M	tests/unit/test_snap.py

## Diff

```diff
diff --git a/.gitignore b/.gitignore
index 3f4db9c..867032f 100644
--- a/.gitignore
+++ b/.gitignore
@@ -3,6 +3,7 @@ build/
 *.charm
 *.orig
 .coverage
+.report
 **/__pycache__/
 *.py[cod]
 .idea/
diff --git a/lib/charms/operator_libs_linux/v2/snap.py b/lib/charms/operator_libs_linux/v2/snap.py
index 5cd0ffd..3623d1d 100644
--- a/lib/charms/operator_libs_linux/v2/snap.py
+++ b/lib/charms/operator_libs_linux/v2/snap.py
@@ -102,7 +102,7 @@ LIBAPI = 2
 
 # Increment this PATCH version before using `charmcraft publish-lib` or reset
 # to 0 if you are raising the major API version
-LIBPATCH = 10
+LIBPATCH = 11
 
 
 # Regex to locate 7-bit C1 ANSI sequences
@@ -577,6 +577,9 @@ class Snap:
         if revision:
             args.append(f'--revision="{revision}"')
 
+        if self.confinement == 'classic':
+            args.append('--classic')
+
         if devmode:
             args.append("--devmode")
 
diff --git a/tests/unit/test_snap.py b/tests/unit/test_snap.py
index 5570466..3c9fa98 100644
--- a/tests/unit/test_snap.py
+++ b/tests/unit/test_snap.py
@@ -3,6 +3,8 @@
 
 # pyright: reportPrivateUsage=false
 
+from __future__ import annotations
+
 import datetime
 import io
 import json
@@ -10,10 +12,11 @@ import time
 import typing
 import unittest
 from subprocess import CalledProcessError
-from typing import Any, Dict, Iterable, Optional
+from typing import Any, Iterable
 from unittest.mock import MagicMock, mock_open, patch
 
 import fake_snapd as fake_snapd
+import pytest
 from charms.operator_libs_linux.v2 import snap
 
 patch("charms.operator_libs_linux.v2.snap._cache_init", lambda x: x).start()
@@ -621,6 +624,43 @@ class TestSnapCache(unittest.TestCase):
         )
 
 
+@patch('charms.operator_libs_linux.v2.snap.subprocess.check_output')
+@pytest.mark.parametrize(
+    'confinement,classic,expected_flag',
+    [
+        ('classic', False, ['--classic']),
+        ('classic', True, ['--classic']),
+        ('strict', False, []),
+        ('strict', True, ['--classic']),
+    ],
+)
+def test_refresh_classic(
+    mock_subprocess: MagicMock, confinement: str, classic: bool, expected_flag: list[str]
+):
+    """Test that ensure and _refresh add the --classic flag with confinement set to classic."""
+    foo = snap.Snap(
+        name='foo',
+        state=snap.SnapState.Present,
+        channel='stable',
+        revision='1',
+        confinement=confinement,
+        apps=None,
+        cohort='A',
+    )
+    foo.ensure(snap.SnapState.Latest, revision='2', classic=classic)
+    mock_subprocess.assert_called_with(
+        [
+            'snap',
+            'refresh',
+            'foo',
+            '--revision="2"',
+            *expected_flag,
+            '--cohort="A"',
+        ],
+        text=True,
+    )
+
+
 class TestSocketClient(unittest.TestCase):
     def test_socket_not_found(self):
         client = snap.SnapClient(socket_path="/does/not/exist")
@@ -707,8 +747,8 @@ class TestSocketClient(unittest.TestCase):
         def _request_raw(
             method: str,
             path: str,
-            query: Dict = None,
-            headers: Dict = None,
+            query: dict = None,
+            headers: dict = None,
             data: bytes = None,
         ) -> typing.IO[bytes]:
             nonlocal change_finished
@@ -818,8 +858,8 @@ class TestSocketClient(unittest.TestCase):
         def _request_raw(
             method: str,
             path: str,
-            query: Dict = None,
-            headers: Dict = None,
+            query: dict = None,
+            headers: dict = None,
             data: bytes = None,
         ) -> typing.IO[bytes]:
             if method == "PUT" and path == "snaps/test/conf":
@@ -884,7 +924,7 @@ class TestSnapBareMethods(unittest.TestCase):
         self.assertTrue(foo.present)
         snap.add("curl", state="latest")  # cover string conversion path
         mock_subprocess.assert_called_with(
-            ["snap", "refresh", "curl", '--channel="latest"'],
+            ["snap", "refresh", "curl", '--channel="latest"', '--classic'],
             text=True,
         )
         with self.assertRaises(TypeError):  # cover error path
@@ -925,6 +965,7 @@ class TestSnapBareMethods(unittest.TestCase):
                 "refresh",
                 "curl",
                 '--channel="latest/beta"',
+                '--classic',
                 '--cohort="+"',
             ],
             text=True,
@@ -1011,7 +1052,7 @@ class TestSnapBareMethods(unittest.TestCase):
         An invalid key will raise an error if typed=False, but return None if typed=True.
         """
 
-        def fake_snap(command: str, optargs: Optional[Iterable[str]] = None) -> str:
+        def fake_snap(command: str, optargs: Iterable[str] | None) -> str:
             """Snap._snap would normally call subprocess.check_output(["snap", ...], ...).
 
             Here we only handle the "get" commands generated by Snap.get:
@@ -1040,7 +1081,7 @@ class TestSnapBareMethods(unittest.TestCase):
 
         foo = snap.Snap("foo", snap.SnapState.Latest, "stable", "1", "classic")
         foo._snap = MagicMock(side_effect=fake_snap)
-        keys_and_values: Dict[str, Any] = {
+        keys_and_values: dict[str, Any] = {
             "key_w_string_value": "string",
             "key_w_float_value": 4.2,
             "key_w_int_value": 13,
```
