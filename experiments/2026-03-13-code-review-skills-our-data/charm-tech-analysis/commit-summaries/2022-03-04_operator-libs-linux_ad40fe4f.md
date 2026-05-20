# Fix issues with apt methods (add_package/remove_package) (#41)

**Repository**: operator-libs-linux
**Commit**: [ad40fe4f](https://github.com/canonical/operator-libs-linux/commit/ad40fe4f5664)
**Date**: 2022-03-04

## Classification

| Field | Value |
|-------|-------|
| Bug Area | apt-package-management |
| Bug Type | logic-error |
| Severity | high |
| Fix Category | source-fix |

## Summary

apt add_package/remove_package failed to check dpkg install status, treating uninstalled packages as installed
