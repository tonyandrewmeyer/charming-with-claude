# yaml lint fix (valid default)

**Repository**: charm-ubuntu
**Commit**: [3250c6ec](https://github.com/canonical/charm-ubuntu/commit/3250c6ec2e0ff3f8b479edb0c5f866b6c6bc036d)
**Date**: 2020-05-29

## Classification

| Field | Value |
|-------|-------|
| Bug Area | config |
| Bug Type | data-validation |
| Severity | low |
| Fix Category | source-fix |

## Summary

config.yaml had empty default value instead of empty string, causing charm lint warning

## Commit Message

Charm tool complained
proof: I: config.yaml: option hostname has no default value

## Changed Files

- M	config.yaml

## Diff

```diff
diff --git a/config.yaml b/config.yaml
index ebd3cab..fe0a7df 100644
--- a/config.yaml
+++ b/config.yaml
@@ -1,6 +1,6 @@
 options:
   hostname:
     type: string
-    default: 
+    default: ""
     description: Override hostname of machine, when empty uses default machine hostname
```
