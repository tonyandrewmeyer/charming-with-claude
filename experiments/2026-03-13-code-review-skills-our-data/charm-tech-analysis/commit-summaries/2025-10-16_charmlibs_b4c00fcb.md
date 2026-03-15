# fix: Log correct renewal_relative_time in error message (#226)

**Repository**: charmlibs
**Commit**: [b4c00fcb](https://github.com/canonical/charmlibs/commit/b4c00fcb)
**Date**: 2025-10-16

## Classification

| Field | Value |
|-------|-------|
| Bug Area | other |
| Bug Type | logic-error |
| Severity | low |
| Fix Category | source-fix |

## Summary

Corrected error message to say 'between 0.5 and 1.0' instead of 'between 0.0 and 1.0' to match the actual validation check.
