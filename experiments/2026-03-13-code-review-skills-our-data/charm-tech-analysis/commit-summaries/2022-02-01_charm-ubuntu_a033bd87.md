# Latest release of operator framework includes fix for GH#517

**Repository**: charm-ubuntu
**Commit**: [a033bd87](https://github.com/canonical/charm-ubuntu/commit/a033bd87b7e567940ac9beec36bc12707fc8103b)
**Date**: 2022-02-01

## Classification

| Field | Value |
|-------|-------|
| Bug Area | packaging |
| Bug Type | config |
| Severity | medium |
| Fix Category | build-fix |

## Summary

requirements.txt pinned to git master for ops framework bug workaround; switched back to released version

## Changed Files

- M	requirements.txt

## Diff

```diff
diff --git a/requirements.txt b/requirements.txt
index ad56269..a52fc1e 100644
--- a/requirements.txt
+++ b/requirements.txt
@@ -1,4 +1 @@
-# ops>=1.0,<2.0
-# Needed due to https://github.com/canonical/operator/issues/517 not yet being
-# included in a released version.
-git+https://github.com/canonical/operator/#egg=ops
+ops>=1.0,<2.0
```
