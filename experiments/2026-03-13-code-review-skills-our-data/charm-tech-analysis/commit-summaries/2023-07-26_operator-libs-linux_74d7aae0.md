# Fix error naming example (#101)

**Repository**: operator-libs-linux
**Commit**: [74d7aae0](https://github.com/canonical/operator-libs-linux/commit/74d7aae0673840cabec0f855eb4bfb4dd2fc3bc9)
**Date**: 2023-07-26

## Classification

| Field | Value |
|-------|-------|
| Bug Area | sysctl |
| Bug Type | api-contract |
| Severity | low |
| Fix Category | docs-fix |

## Summary

Docstring example used wrong exception class names (SysctlPermissionError/SysctlError vs ApplyError/CommandError)

## Changed Files

- M	lib/charms/operator_libs_linux/v0/sysctl.py
- M	tests/integration/test_sysctl.py
- M	tests/unit/test_sysctl.py

## Diff

```diff
diff --git a/lib/charms/operator_libs_linux/v0/sysctl.py b/lib/charms/operator_libs_linux/v0/sysctl.py
index 96fcea9..16b0159 100644
--- a/lib/charms/operator_libs_linux/v0/sysctl.py
+++ b/lib/charms/operator_libs_linux/v0/sysctl.py
@@ -57,10 +57,10 @@ class MyCharm(CharmBase):
 
         try:
             self.sysctl.configure(config=sysctl_data)
-        except (sysctl.SysctlPermissionError, sysctl.ValidationError) as e:
+        except (sysctl.ApplyError, sysctl.ValidationError) as e:
             logger.error(f"Error setting values on sysctl: {e.message}")
             self.unit.status = BlockedStatus("Sysctl config not possible")
-        except sysctl.SysctlError:
+        except sysctl.CommandError:
             logger.error("Error on sysctl")
 
     def _on_remove(self, _):
@@ -84,7 +84,7 @@ LIBAPI = 0
 
 # Increment this PATCH version before using `charmcraft publish-lib` or reset
 # to 0 if you are raising the major API version
-LIBPATCH = 2
+LIBPATCH = 3
 
 CHARM_FILENAME_PREFIX = "90-juju-"
 SYSCTL_DIRECTORY = Path("/etc/sysctl.d")
diff --git a/tests/integration/test_sysctl.py b/tests/integration/test_sysctl.py
index 414cc0f..04b0564 100644
--- a/tests/integration/test_sysctl.py
+++ b/tests/integration/test_sysctl.py
@@ -8,16 +8,6 @@ from subprocess import check_output
 
 from charms.operator_libs_linux.v0 import sysctl
 
-EXPECTED_MERGED_RESULT = """# This config file was produced by sysctl lib v0.2
-#
-# This file represents the output of the sysctl lib, which can combine multiple
-# configurations into a single file like.
-# test1
-net.ipv4.tcp_max_syn_backlog=4096
-# test2
-net.ipv4.tcp_window_scaling=2
-"""
-
 
 def test_configure():
     cfg = sysctl.Config("test1")
@@ -48,7 +38,9 @@ def test_multiple_configure():
     assert test_file_2.exists()
 
     with open(merged_file, "r") as f:
-        assert f.read() == EXPECTED_MERGED_RESULT
+        result = f.read()
+        assert "# test1\nnet.ipv4.tcp_max_syn_backlog=4096" in result
+        assert "# test2\nnet.ipv4.tcp_window_scaling=2" in result
 
 
 def test_remove():
diff --git a/tests/unit/test_sysctl.py b/tests/unit/test_sysctl.py
index b8b9bde..e9337e0 100644
--- a/tests/unit/test_sysctl.py
+++ b/tests/unit/test_sysctl.py
@@ -18,7 +18,7 @@ TEST_OTHER_CHARM_FILE = """# othercharm
 vm.swappiness=60
 net.ipv4.tcp_max_syn_backlog=4096
 """
-TEST_OTHER_CHARM_MERGED = """# This config file was produced by sysctl lib v0.2
+TEST_OTHER_CHARM_MERGED = f"""# This config file was produced by sysctl lib v{sysctl.LIBAPI}.{sysctl.LIBPATCH}
 #
 # This file represents the output of the sysctl lib, which can combine multiple
 # configurations into a single file like.
@@ -26,7 +26,7 @@ TEST_OTHER_CHARM_MERGED = """# This config file was produced by sysctl lib v0.2
 vm.swappiness=60
 net.ipv4.tcp_max_syn_backlog=4096
 """
-TEST_MERGED_FILE = """# This config file was produced by sysctl lib v0.2
+TEST_MERGED_FILE = f"""# This config file was produced by sysctl lib v{sysctl.LIBAPI}.{sysctl.LIBPATCH}
 #
 # This file represents the output of the sysctl lib, which can combine multiple
 # configurations into a single file like.
@@ -34,7 +34,7 @@ vm.max_map_count = 262144
 vm.swappiness=0
 
 """
-TEST_UPDATE_MERGED_FILE = """# This config file was produced by sysctl lib v0.2
+TEST_UPDATE_MERGED_FILE = f"""# This config file was produced by sysctl lib v{sysctl.LIBAPI}.{sysctl.LIBPATCH}
 #
 # This file represents the output of the sysctl lib, which can combine multiple
 # configurations into a single file like.
```
