# Fix repo URL in layer.yaml

**Repository**: charm-ubuntu
**Commit**: [11ad6edf](https://github.com/canonical/charm-ubuntu/commit/11ad6edf050164b0732b331e90b50e4fec3c64e5)
**Date**: 2019-08-06

## Classification

| Field | Value |
|-------|-------|
| Bug Area | config |
| Bug Type | config |
| Severity | low |
| Fix Category | source-fix |

## Summary

layer.yaml pointed to old repo URL (marcoceppi) instead of current (juju-solutions)

## Changed Files

- M	layer.yaml

## Diff

```diff
diff --git a/layer.yaml b/layer.yaml
index ad0a115..d77fa0c 100644
--- a/layer.yaml
+++ b/layer.yaml
@@ -1,3 +1,3 @@
 includes:
  - 'layer:basic'
-repo: https://github.com/marcoceppi/charm-ubuntu
+repo: https://github.com/juju-solutions/charm-ubuntu
```
