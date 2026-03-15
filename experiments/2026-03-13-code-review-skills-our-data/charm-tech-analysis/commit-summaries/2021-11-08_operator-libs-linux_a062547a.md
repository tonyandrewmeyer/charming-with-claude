# Fix GPG key handling (#15)

**Repository**: operator-libs-linux
**Commit**: [a062547a](https://github.com/canonical/operator-libs-linux/commit/a062547af253)
**Date**: 2021-11-08

## Classification

| Field | Value |
|-------|-------|
| Bug Area | apt-package-management |
| Bug Type | logic-error |
| Severity | high |
| Fix Category | source-fix |

## Summary

GPG key import for apt repositories used broken Popen communication; replaced with subprocess.run()
