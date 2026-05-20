# Fix tests (fix code)

**Repository**: operator-libs-linux
**Commit**: [0ac58381](https://github.com/canonical/operator-libs-linux/commit/0ac5838107e8)
**Date**: 2021-12-06

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Snap install/refresh passed empty cohort string to subprocess causing errors
