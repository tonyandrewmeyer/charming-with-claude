# Fix failing test.

**Repository**: operator-libs-linux
**Commit**: [0e086ee9](https://github.com/canonical/operator-libs-linux/commit/0e086ee94ecc)
**Date**: 2021-11-19

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | test-fix |
| Severity | low |
| Fix Category | test-fix |

## Summary

Unit test reached out to real snapd, failing on systems without it; added mock
