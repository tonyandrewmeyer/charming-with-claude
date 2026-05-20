# Fix file operations in unit tests (#103)

**Repository**: operator-libs-linux
**Commit**: [8c3034cc](https://github.com/canonical/operator-libs-linux/commit/8c3034ccbf2805b6018cfb18902c28a86d076a71)
**Date**: 2023-08-06

## Classification

| Field | Value |
|-------|-------|
| Bug Area | sysctl |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

sysctl tests used == instead of calling f.write() and f.read(), and source used string path instead of Path for discard

## Commit Message

* fix file operations in unit tests

* increase lib patch

## Changed Files

- M	lib/charms/operator_libs_linux/v0/sysctl.py
- M	tests/unit/test_sysctl.py

## Diff

```diff
diff --git a/lib/charms/operator_libs_linux/v0/sysctl.py b/lib/charms/operator_libs_linux/v0/sysctl.py
index 16b0159..8245835 100644
--- a/lib/charms/operator_libs_linux/v0/sysctl.py
+++ b/lib/charms/operator_libs_linux/v0/sysctl.py
@@ -84,7 +84,7 @@ LIBAPI = 0
 
 # Increment this PATCH version before using `charmcraft publish-lib` or reset
 # to 0 if you are raising the major API version
-LIBPATCH = 3
+LIBPATCH = 4
 
 CHARM_FILENAME_PREFIX = "90-juju-"
 SYSCTL_DIRECTORY = Path("/etc/sysctl.d")
@@ -220,7 +220,7 @@ class Config(Dict):
         data = [SYSCTL_HEADER]
         paths = set(SYSCTL_DIRECTORY.glob(f"{CHARM_FILENAME_PREFIX}*"))
         if not add_own_charm:
-            paths.discard(self.charm_filepath.as_posix())
+            paths.discard(self.charm_filepath)
 
         for path in paths:
             with open(path, "r") as f:
diff --git a/tests/unit/test_sysctl.py b/tests/unit/test_sysctl.py
index e9337e0..471ce50 100644
--- a/tests/unit/test_sysctl.py
+++ b/tests/unit/test_sysctl.py
@@ -135,13 +135,13 @@ class TestSysctlConfig(unittest.TestCase):
         mock_load.return_value = self.loaded_values
         config = sysctl.Config("test")
         with open(self.tmp_dir / "90-juju-othercharm", "w") as f:
-            f.write == TEST_OTHER_CHARM_FILE
+            f.write(TEST_OTHER_CHARM_FILE)
 
         config._merge()
 
         assert (self.tmp_dir / "95-juju-sysctl.conf").exists
         with open(self.tmp_dir / "95-juju-sysctl.conf", "r") as f:
-            f.read == TEST_OTHER_CHARM_MERGED
+            assert f.read() == TEST_OTHER_CHARM_MERGED
 
     @patch("charms.operator_libs_linux.v0.sysctl.Config._load_data")
     def test_merge_without_own_file(self, mock_load):
@@ -149,15 +149,15 @@ class TestSysctlConfig(unittest.TestCase):
         config = sysctl.Config("test")
 
         with open(self.tmp_dir / "90-juju-test", "w") as f:
-            f.write == "# test\nvalue=1\n"
+            f.write("# test\nvalue=1\n")
         with open(self.tmp_dir / "90-juju-othercharm", "w") as f:
-            f.write == TEST_OTHER_CHARM_FILE
+            f.write(TEST_OTHER_CHARM_FILE)
 
         config._merge(add_own_charm=False)
 
         assert (self.tmp_dir / "95-juju-sysctl.conf").exists
         with open(self.tmp_dir / "95-juju-sysctl.conf", "r") as f:
-            f.read == TEST_OTHER_CHARM_MERGED
+            assert f.read() == TEST_OTHER_CHARM_MERGED
 
     @patch("charms.operator_libs_linux.v0.sysctl.Config._load_data")
     def test_validate_different_keys(self, mock_load):
```
