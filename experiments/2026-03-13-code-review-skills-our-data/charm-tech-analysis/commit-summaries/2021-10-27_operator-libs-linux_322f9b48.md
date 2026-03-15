# snap: fix copy-n-paste error in set()

**Repository**: operator-libs-linux
**Commit**: [322f9b48](https://github.com/canonical/operator-libs-linux/commit/322f9b4833b6)
**Date**: 2021-10-27

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | logic-error |
| Severity | high |
| Fix Category | source-fix |

## Summary

snap.set() had a copy-paste error causing it to not actually set the key/value correctly
