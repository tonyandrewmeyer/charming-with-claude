# fix copying to kubernetes-extra

**Repository**: charmcraft-profile-tools
**Commit**: [6cf99f61](https://github.com/canonical/charmcraft-profile-tools/commit/6cf99f61f5205f1c09a83181c2156b1e260402a6)
**Date**: 2025-09-07

## Classification

| Field | Value |
|-------|-------|
| Bug Area | automation |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Copying to kubernetes-extra included stale build artifacts (.coverage, .ruff_cache, .tox, .venv)

## Changed Files

- M	justfile

## Diff

```diff
diff --git a/justfile b/justfile
index 339035f..4c0c1b3 100644
--- a/justfile
+++ b/justfile
@@ -64,6 +64,7 @@ _init-kubernetes-extra:
     @test -d kubernetes
     @rm -rf kubernetes-extra
     @cp -r kubernetes kubernetes-extra
+    @cd kubernetes-extra && rm -rf .coverage .ruff_cache .tox .venv
 
 _tox charm envs:
     #!/bin/sh
```
