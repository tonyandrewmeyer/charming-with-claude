# fix(apt): improve logic in apt.add_package function (#155)

**Repository**: operator-libs-linux
**Commit**: [c19d8b51](https://github.com/canonical/operator-libs-linux/commit/c19d8b515d060296c0aafab988d3292470bf8aa5)
**Date**: 2025-04-02

## Classification

| Field | Value |
|-------|-------|
| Bug Area | apt-package-management |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

apt.add_package retry logic was broken: failed packages not tracked and return value inconsistent for single package

## Commit Message

Fixes #154

---------

Co-authored-by: James Garner <james.garner@canonical.com>

## Changed Files

- M	lib/charms/operator_libs_linux/v0/apt.py
- M	tests/unit/test_apt.py

## Diff

```diff
diff --git a/lib/charms/operator_libs_linux/v0/apt.py b/lib/charms/operator_libs_linux/v0/apt.py
index 1911f3e..27ab939 100644
--- a/lib/charms/operator_libs_linux/v0/apt.py
+++ b/lib/charms/operator_libs_linux/v0/apt.py
@@ -124,7 +124,7 @@ LIBAPI = 0
 
 # Increment this PATCH version before using `charmcraft publish-lib` or reset
 # to 0 if you are raising the major API version
-LIBPATCH = 16
+LIBPATCH = 17
 
 
 VALID_SOURCE_TYPES = ("deb", "deb-src")
@@ -791,11 +791,14 @@ def add_package(
         pkg, _ = _add(p, version, arch)
         if isinstance(pkg, DebianPackage):
             succeeded.append(pkg)
-        else:
+        elif cache_refreshed:
             logger.warning("failed to locate and install/update '%s'", pkg)
+            failed.append(p)
+        else:
+            logger.warning("failed to locate and install/update '%s', will retry later", pkg)
             retry.append(p)
 
-    if retry and not cache_refreshed:
+    if retry:
         logger.info("updating the apt-cache and retrying installation of failed packages.")
         update()
 
@@ -809,7 +812,7 @@ def add_package(
     if failed:
         raise PackageError(f"Failed to install packages: {', '.join(failed)}")
 
-    return succeeded if len(succeeded) > 1 else succeeded[0]
+    return succeeded[0] if len(succeeded) == 1 else succeeded
 
 
 def _add(
diff --git a/tests/unit/test_apt.py b/tests/unit/test_apt.py
index 99c43ca..722263f 100644
--- a/tests/unit/test_apt.py
+++ b/tests/unit/test_apt.py
@@ -517,6 +517,24 @@ class TestAptBareMethods(unittest.TestCase):
         self.assertEqual(pkg.name, "aisleriot")
         self.assertEqual(pkg.present, True)
 
+    @patch("charms.operator_libs_linux.v0.apt.check_output")
+    @patch("charms.operator_libs_linux.v0.apt.subprocess.run")
+    def test_refreshes_apt_cache_before_apt_install(self, mock_subprocess, mock_subprocess_output):
+        mock_subprocess.return_value = 0
+        mock_subprocess_output.side_effect = [
+            "amd64",
+            subprocess.CalledProcessError(returncode=100, cmd=["dpkg", "-l", "nothere"]),
+            "amd64",
+            subprocess.CalledProcessError(returncode=100, cmd=["apt-cache", "show", "nothere"]),
+        ] * 2  # Double up for the retry before update
+        with self.assertRaises(apt.PackageError) as ctx:
+            apt.add_package("nothere", update_cache=True)
+        mock_subprocess.assert_any_call(
+            ["apt-get", "update", "--error-on=any"], capture_output=True, check=True
+        )
+        self.assertEqual("<charms.operator_libs_linux.v0.apt.PackageError>", ctx.exception.name)
+        self.assertIn("Failed to install packages: nothere", ctx.exception.message)
+
     @patch("charms.operator_libs_linux.v0.apt.check_output")
     @patch("charms.operator_libs_linux.v0.apt.subprocess.run")
     def test_raises_package_not_found_error(self, mock_subprocess, mock_subprocess_output):
```
