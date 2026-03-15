# fix consistency check

**Repository**: charmcraft-profile-tools
**Commit**: [3f9d8337](https://github.com/canonical/charmcraft-profile-tools/commit/3f9d8337a9e1bd3e59e82f251da33e3c7957b356)
**Date**: 2025-09-05

## Classification

| Field | Value |
|-------|-------|
| Bug Area | ci-build |
| Bug Type | config |
| Severity | medium |
| Fix Category | ci-fix |

## Summary

CI workflow missing tox and tox-uv installation step, causing consistency check to fail

## Changed Files

- M	.github/workflows/implemented.yaml

## Diff

```diff
diff --git a/.github/workflows/implemented.yaml b/.github/workflows/implemented.yaml
index c88e267..3f04a1a 100644
--- a/.github/workflows/implemented.yaml
+++ b/.github/workflows/implemented.yaml
@@ -15,6 +15,8 @@ jobs:
       - uses: actions/checkout@v4
       - name: Install uv
         uses: astral-sh/setup-uv@v6
+      - name: Install tox and tox-uv
+        run: uv tool install tox --with tox-uv
       - name: Implement kubernetes-extra
         run: uvx --from rust-just just kubernetes-extra
       - name: Make sure nothing changed
```
