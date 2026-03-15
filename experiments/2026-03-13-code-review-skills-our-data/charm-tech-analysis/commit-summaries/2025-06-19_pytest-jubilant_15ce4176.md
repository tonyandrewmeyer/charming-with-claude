# fix imports

**Repository**: pytest-jubilant
**Commit**: [15ce4176](https://github.com/canonical/pytest-jubilant/commit/15ce4176ebf12348cbff488a8ab56c47725bc46a)
**Date**: 2025-06-19T09:33:30+02:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | packaging |
| Bug Type | logic-error |
| Severity | high |
| Fix Category | source-fix |

## Summary

pack and get_resources were listed in __all__ but not imported in __init__.py, causing ImportError

## Changed Files

- M	README.md
- M	pytest_jubilant/__init__.py
- A	tests/test_smoke.py

## Diff

```diff
diff --git a/README.md b/README.md
index 50b5a22..3c95bb5 100644
--- a/README.md
+++ b/README.md
@@ -178,4 +178,18 @@ resources:
     type: oci-image
     description: OCI image for nginx-prometheus-exporter
     upstream-source: nginx/nginx-prometheus-exporter:1.1.0
-```
\ No newline at end of file
+```
+
+# DEVELOPERS
+
+To release:
+```bash
+# obtain the current latest version out there
+git tag | tail -n 1
+
+new_tag="v0.5"  # for example!
+git tag $new_tag -m "new fancy feature"
+git push origin head --tag
+```
+
+Once the PR is merged, the release CI will kick in and put the tag in `pytest_jubilant.version.py`
\ No newline at end of file
diff --git a/pytest_jubilant/__init__.py b/pytest_jubilant/__init__.py
index d97f6db..a37a2b5 100644
--- a/pytest_jubilant/__init__.py
+++ b/pytest_jubilant/__init__.py
@@ -4,6 +4,6 @@
 
 """Welcome to pytest-jubilant!"""
 
-from pytest_jubilant.main import pack_charm
+from pytest_jubilant.main import pack_charm, pack, get_resources
 
 __all__ = ["pack_charm", "pack", "get_resources"]
diff --git a/tests/test_smoke.py b/tests/test_smoke.py
new file mode 100644
index 0000000..a445c81
--- /dev/null
+++ b/tests/test_smoke.py
@@ -0,0 +1,3 @@
+def test_imports():
+    from pytest_jubilant import pack, pack_charm, get_resources
+    assert pack and pack_charm and get_resources
\ No newline at end of file
```
