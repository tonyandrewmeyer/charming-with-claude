# Fix up parsing more complex sources..list lines (#11)

**Repository**: operator-libs-linux
**Commit**: [3e8a1b56](https://github.com/canonical/operator-libs-linux/commit/3e8a1b5614c2)
**Date**: 2021-11-03

## Classification

| Field | Value |
|-------|-------|
| Bug Area | apt-package-management |
| Bug Type | parsing |
| Severity | high |
| Fix Category | source-fix |

## Summary

apt sources.list parser failed on lines with options like [arch=amd64] and raised error on partial parse failures
