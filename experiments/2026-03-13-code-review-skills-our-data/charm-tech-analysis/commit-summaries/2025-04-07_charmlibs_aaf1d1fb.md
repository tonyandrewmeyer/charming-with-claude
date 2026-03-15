# fix: strip whitespace from runtime version string (#34)

**Repository**: charmlibs
**Commit**: [aaf1d1fb](https://github.com/canonical/charmlibs/commit/aaf1d1fb)
**Date**: 2025-04-07

## Classification

| Field | Value |
|-------|-------|
| Bug Area | packaging |
| Bug Type | edge-case |
| Severity | low |
| Fix Category | source-fix |

## Summary

Added .strip() when reading _version.txt to remove trailing newline that caused version string to contain whitespace.
