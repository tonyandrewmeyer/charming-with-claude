# fix comparing types and use isinstance (#105)

**Repository**: operator-libs-linux
**Commit**: [57e7a6f9](https://github.com/canonical/operator-libs-linux/commit/57e7a6f929bcb849ddfda49564e7fab0c549fd0e)
**Date**: 2023-08-23

## Classification

| Field | Value |
|-------|-------|
| Bug Area | apt-package-management |
| Bug Type | type-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Used type() instead of isinstance() for type checks, failing for subclasses and allowing bool to pass as int

## Changed Files

- M	lib/charms/operator_libs_linux/v0/apt.py
- M	lib/charms/operator_libs_linux/v0/passwd.py
- M	lib/charms/operator_libs_linux/v2/snap.py

## Diff

```diff
diff --git a/lib/charms/operator_libs_linux/v0/apt.py b/lib/charms/operator_libs_linux/v0/apt.py
index 7afb183..2fc1dc7 100644
--- a/lib/charms/operator_libs_linux/v0/apt.py
+++ b/lib/charms/operator_libs_linux/v0/apt.py
@@ -748,7 +748,7 @@ def add_package(
 
     packages = {"success": [], "retry": [], "failed": []}
 
-    package_names = [package_names] if type(package_names) is str else package_names
+    package_names = [package_names] if isinstance(package_names, str) else package_names
     if not package_names:
         raise TypeError("Expected at least one package name to add, received zero!")
 
@@ -818,7 +818,7 @@ def remove_package(
     """
     packages = []
 
-    package_names = [package_names] if type(package_names) is str else package_names
+    package_names = [package_names] if isinstance(package_names, str) else package_names
     if not package_names:
         raise TypeError("Expected at least one package name to add, received zero!")
 
diff --git a/lib/charms/operator_libs_linux/v0/passwd.py b/lib/charms/operator_libs_linux/v0/passwd.py
index ed5a058..7eb83b2 100644
--- a/lib/charms/operator_libs_linux/v0/passwd.py
+++ b/lib/charms/operator_libs_linux/v0/passwd.py
@@ -58,9 +58,9 @@ def user_exists(user: Union[str, int]) -> Optional[pwd.struct_passwd]:
         TypeError: where neither a string or int is passed as the first argument
     """
     try:
-        if type(user) is int:
+        if isinstance(user, int) and not isinstance(user, bool):
             return pwd.getpwuid(user)
-        elif type(user) is str:
+        elif isinstance(user, str):
             return pwd.getpwnam(user)
         else:
             raise TypeError("specified argument '%r' should be a string or int", user)
@@ -79,9 +79,9 @@ def group_exists(group: Union[str, int]) -> Optional[grp.struct_group]:
         TypeError: where neither a string or int is passed as the first argument
     """
     try:
-        if type(group) is int:
+        if isinstance(group, int) and not isinstance(group, bool):
             return grp.getgrgid(group)
-        elif type(group) is str:
+        elif isinstance(group, str):
             return grp.getgrnam(group)
         else:
             raise TypeError("specified argument '%r' should be a string or int", group)
diff --git a/lib/charms/operator_libs_linux/v2/snap.py b/lib/charms/operator_libs_linux/v2/snap.py
index 16e0261..9814ecf 100644
--- a/lib/charms/operator_libs_linux/v2/snap.py
+++ b/lib/charms/operator_libs_linux/v2/snap.py
@@ -898,11 +898,11 @@ def add(
     if not channel and not revision:
         channel = "latest"
 
-    snap_names = [snap_names] if type(snap_names) is str else snap_names
+    snap_names = [snap_names] if isinstance(snap_names, str) else snap_names
     if not snap_names:
         raise TypeError("Expected at least one snap to add, received zero!")
 
-    if type(state) is str:
+    if isinstance(state, str):
         state = SnapState(state)
 
     return _wrap_snap_operations(snap_names, state, channel, classic, cohort, revision)
@@ -918,7 +918,7 @@ def remove(snap_names: Union[str, List[str]]) -> Union[Snap, List[Snap]]:
     Raises:
         SnapError if some snaps failed to install.
     """
-    snap_names = [snap_names] if type(snap_names) is str else snap_names
+    snap_names = [snap_names] if isinstance(snap_names, str) else snap_names
     if not snap_names:
         raise TypeError("Expected at least one snap to add, received zero!")
```
