# Fix typo (#841)

**Repository**: operator
**Commit**: [da4a0ecc](https://github.com/canonical/operator/commit/da4a0eccdadf3539b04441154a5f1bcc56aa5480)
**Date**: 2022-11-14

## Classification

| Field | Value |
|-------|-------|
| Bug Area | docs |
| Bug Type | other |
| Severity | low |
| Fix Category | docs-fix |

## Summary

typo

## Changed Files

- M	ops/charm.py

## Diff

```diff
diff --git a/ops/charm.py b/ops/charm.py
index 4458281..a4cce35 100755
--- a/ops/charm.py
+++ b/ops/charm.py
@@ -288,7 +288,7 @@ class ConfigChangedEvent(HookEvent):
       (if the machine reboots and comes up with a different IP).
     - When the cloud admin reconfigures the charm via the juju CLI, i.e.
       `juju config my-charm foo=bar`. This event notifies the charm of
-      its new configuration. (The event itself, however, is now aware of *what*
+      its new configuration. (The event itself, however, is not aware of *what*
       specifically has changed in the config).
 
     Any callback method bound to this event cannot assume that the
```
