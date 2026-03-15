# fix: inherit environment before adding new keys (#61)

**Repository**: operator-libs-linux
**Commit**: [a063d947](https://github.com/canonical/operator-libs-linux/commit/a063d947072f14e9c9b33e2a5c5a6c0e1d8e7f3a)
**Date**: 2023-01-23

## Classification

| Field | Value |
|-------|-------|
| Bug Area | apt-package-management |
| Bug Type | state-management |
| Severity | high |
| Fix Category | source-fix |

## Summary

apt subprocess calls did not inherit the parent environment, losing PATH and other required env vars
