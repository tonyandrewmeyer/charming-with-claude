# Fix URLs in HACKING.md (#892)

**Repository**: operator
**Commit**: [dc8e0f3e](https://github.com/canonical/operator/commit/dc8e0f3ee5cc35ff0da3bfafa7d45d6a9737307e)
**Date**: 2023-01-17

## Classification

| Field | Value |
|-------|-------|
| Bug Area | docs |
| Bug Type | other |
| Severity | low |
| Fix Category | docs-fix |

## Summary

urls in hacking.md

## Changed Files

- M	HACKING.md

## Diff

```diff
diff --git a/HACKING.md b/HACKING.md
index c50d715..dff0026 100644
--- a/HACKING.md
+++ b/HACKING.md
@@ -55,7 +55,7 @@ pytest
 The framework has some tests that interact with a real/live pebble server.  To
 run these tests, you must have (pebble)[https://github.com/canonical/pebble]
 installed and available in your path.  If you have the Go toolchain installed,
-you can run `go install github.com/canonical/pebble@latest`.  This will
+you can run `go install github.com/canonical/pebble/cmd/pebble@latest`.  This will
 install pebble to `$GOBIN` if it is set or `$HOME/go/bin` otherwise.  Add
 `$GOBIN` to your path (e.g. `export PATH=$PATH:$GOBIN` or `export
 PATH=$PATH:$HOME/go/bin` in your `.bashrc`) and you are ready to run the real
@@ -118,7 +118,7 @@ To make a release of the Operator Framework, do the following:
 
 This will trigger an automatic build for the Python package and publish it to PyPI (the API token/secret is already set up in the repository settings).
 
-See [.github/workflows/publish.yml](https://github.com/canonical/operator/blob/main/.github/workflows/publish.yml) for details. (Note that the versions in publish.yml refer to versions of the github actions, not the versions of the Operator Framework.)
+See [.github/workflows/publish.yml](.github/workflows/publish.yml) for details. (Note that the versions in publish.yml refer to versions of the github actions, not the versions of the Operator Framework.)
 
 You can troubleshoot errors on the [Actions Tab](https://github.com/canonical/operator/actions).
```
