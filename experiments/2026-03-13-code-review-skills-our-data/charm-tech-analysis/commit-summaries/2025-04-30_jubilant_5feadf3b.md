# fix: fix format of --bind argument for deploy (#132)

**Repository**: jubilant
**Commit**: [5feadf3b](https://github.com/canonical/jubilant/commit/5feadf3b7f68801ed89edfba1ff0123780805f39)
**Date**: 2025-04-30T18:47:45-03:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | charm-deployment |
| Bug Type | api-contract |
| Severity | high |
| Fix Category | source-fix |

## Summary

Deploy --bind used comma-separated format but Juju CLI expects space-separated key=value pairs

## Commit Message

Fix the format of the `--bind` argument to deploy from comma-separated
to space-separated key=value pairs. See [Juju
source](https://github.com/juju/juju/blob/214723de24e82f5d14fd255de0885092e0a4dd7c/cmd/juju/application/binding.go#L17-L24).

---------

Co-authored-by: Ben Hoyt <ben.hoyt@canonical.com>

## Changed Files

- M	jubilant/__init__.py
- M	jubilant/_juju.py
- M	tests/unit/test_deploy.py

## Diff

```diff
diff --git a/jubilant/__init__.py b/jubilant/__init__.py
index 25d4c4a..559cf17 100644
--- a/jubilant/__init__.py
+++ b/jubilant/__init__.py
@@ -43,4 +43,4 @@ __all__ = [
     'temp_model',
 ]
 
-__version__ = '1.0.0'
+__version__ = '1.0.1'
diff --git a/jubilant/_juju.py b/jubilant/_juju.py
index b02cb21..6ec21ce 100644
--- a/jubilant/_juju.py
+++ b/jubilant/_juju.py
@@ -364,7 +364,7 @@ class Juju:
             args.extend(['--base', base])
         if bind is not None:
             if not isinstance(bind, str):
-                bind = ','.join(f'{k}={v}' for k, v in bind.items())
+                bind = ' '.join(f'{k}={v}' for k, v in bind.items())
             args.extend(['--bind', bind])
         if channel is not None:
             args.extend(['--channel', channel])
diff --git a/tests/unit/test_deploy.py b/tests/unit/test_deploy.py
index da293ae..19d46f2 100644
--- a/tests/unit/test_deploy.py
+++ b/tests/unit/test_deploy.py
@@ -31,7 +31,7 @@ def test_all_args(run: mocks.Run):
             '--base',
             'ubuntu@22.04',
             '--bind',
-            'end1=space1,end2=space2',
+            'end1=space1 end2=space2',
             '--channel',
             'latest/edge',
             '--config',
```
