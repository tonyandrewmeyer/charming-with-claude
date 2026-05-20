# Fix deploy error due to new pip / old setuptools conflict

**Repository**: charm-ubuntu
**Commit**: [e03c398b](https://github.com/canonical/charm-ubuntu/commit/e03c398b5c941c349c315878cbb8f36ab7e8e6c1)
**Date**: 2019-08-19

## Classification

| Field | Value |
|-------|-------|
| Bug Area | packaging |
| Bug Type | edge-case |
| Severity | high |
| Fix Category | source-fix |

## Summary

Newer pip conflicted with older system setuptools when include_system_packages was true, breaking deploys

## Commit Message

Newer versions of pip (>=19.0) don't work with older versions of
setuptools (<40) due to an attribute error.  If
`include_system_packages` is `false` (now the default), this is not an
issue because of the newer setuptools that gets installed into the venv.
However, when it's `true`, which is required for some charms, the
install fails because pip somehow prefers the older system-installed
setuptools over the newer one in the venv. Pinning pip avoids the
problem until we can find a better solution.

See:
  * https://discourse.jujucharms.com/t/wheel-building-fails-during-charm-deployment/1947
  * https://github.com/pypa/pip/issues/6164

## Changed Files

- M	layer.yaml

## Diff

```diff
diff --git a/layer.yaml b/layer.yaml
index d77fa0c..cbb7d60 100644
--- a/layer.yaml
+++ b/layer.yaml
@@ -1,3 +1,6 @@
 includes:
  - 'layer:basic'
 repo: https://github.com/juju-solutions/charm-ubuntu
+options:
+  basic:
+    include_system_packages: true
```
