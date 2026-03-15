# fix: Fileinfo.{user,group} are typed optional but should always be present (#43)

**Repository**: charmlibs
**Commit**: [00aea1c0](https://github.com/canonical/charmlibs/commit/00aea1c0)
**Date**: 2025-04-15

## Classification

| Field | Value |
|-------|-------|
| Bug Area | typing |
| Bug Type | type-error |
| Severity | low |
| Fix Category | source-fix |

## Summary

Replaced silent fallback to empty string with assertion that FileInfo.user/group are never None, fixing incorrect Optional typing.
