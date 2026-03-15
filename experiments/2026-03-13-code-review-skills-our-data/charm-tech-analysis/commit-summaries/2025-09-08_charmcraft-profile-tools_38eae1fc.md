# fix spelling

**Repository**: charmcraft-profile-tools
**Commit**: [38eae1fc](https://github.com/canonical/charmcraft-profile-tools/commit/38eae1fcbca76170e1b9ac4161574bb57e2160c7)
**Date**: 2025-09-08

## Classification

| Field | Value |
|-------|-------|
| Bug Area | other |
| Bug Type | other |
| Severity | low |
| Fix Category | docs-fix |

## Summary

Fixed two spelling typos in README (maintaing -> maintaining, locaed -> located)

## Changed Files

- M	README.md

## Diff

```diff
diff --git a/README.md b/README.md
index 823e6e1..62dfb3e 100644
--- a/README.md
+++ b/README.md
@@ -1,4 +1,4 @@
-This repo contains tools for maintaing the `kubernetes` and `machine` profiles of [Charmcraft](https://github.com/canonical/charmcraft). The tools are primarily intended to be used by the Charm Tech team at Canonical.
+This repo contains tools for maintaining the `kubernetes` and `machine` profiles of [Charmcraft](https://github.com/canonical/charmcraft). The tools are primarily intended to be used by the Charm Tech team at Canonical.
 
 In the Charmcraft source, profiles are stored as .j2 template files. For example, [charm.py.j2](https://github.com/canonical/charmcraft/blob/main/charmcraft/templates/init-kubernetes/src/charm.py.j2). This makes it possible for `charmcraft init` to fill in details such as the charm name, but testing the profiles can be awkward.
 
@@ -6,7 +6,7 @@ In the Charmcraft source, profiles are stored as .j2 template files. For example
 
 You'll need:
 
-  - The Charmcraft source. We'll assume this is locaed at `~/charmcraft`.
+  - The Charmcraft source. We'll assume this is located at `~/charmcraft`.
 
   - A virtual environment in the Charmcraft source. To create a virtual environment:
```
