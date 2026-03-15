# fix error handling

**Repository**: charmcraft-profile-tools
**Commit**: [8d4730bb](https://github.com/canonical/charmcraft-profile-tools/commit/8d4730bbedf0f6ea1acd32ccce83d81eaf51efb9)
**Date**: 2025-09-07

## Classification

| Field | Value |
|-------|-------|
| Bug Area | automation |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Typo in justfile checked for .ven instead of .venv, so venv existence check always failed

## Changed Files

- M	justfile

## Diff

```diff
diff --git a/justfile b/justfile
index 7a2bb11..ce77de9 100644
--- a/justfile
+++ b/justfile
@@ -41,7 +41,7 @@ _charmcraft-init +profiles:
         echo "CHARMCRAFT_DIR is not set"
         exit 1
     fi
-    if [ ! -d "$CHARMCRAFT_DIR/.ven" ]; then
+    if [ ! -d "$CHARMCRAFT_DIR/.venv" ]; then
         echo "Environment does not exist: $CHARMCRAFT_DIR/.venv"
         echo "Have you run 'make setup' in the Charmcraft directory?"
         exit 1
```
