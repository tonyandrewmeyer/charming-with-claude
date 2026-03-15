# Fix two typos in the readme (#145)

**Repository**: operator
**Commit**: [9efe3cc0](https://github.com/canonical/operator/commit/9efe3cc0e9eecc30a408cb017b71c0860cb96790)
**Date**: 2020-02-25

## Classification

| Field | Value |
|-------|-------|
| Bug Area | docs |
| Bug Type | other |
| Severity | low |
| Fix Category | docs-fix |

## Summary

two typos in the readme

## Changed Files

- M	README.md

## Diff

```diff
diff --git a/README.md b/README.md
index f684a82..effcee0 100644
--- a/README.md
+++ b/README.md
@@ -83,7 +83,7 @@ class MyCharm(CharmBase):
         super().__init__(*args)
         self.framework.observe(self.on.start, self.on_start)
 
-     def on_start(self, event):
+    def on_start(self, event):
         # Handle the start event here.
 ```
 
@@ -93,7 +93,7 @@ define your own events in your custom types.
 > The second argument to `observe` can be either the handler as a bound
 > method, or the observer itself if the handler is a method of the observer
 > that follows the conventional naming pattern. That is, in this case, we
-> could have called just `self.framework.obseve(self.on.start, self)`.
+> could have called just `self.framework.observe(self.on.start, self)`.
 
 The `hooks/` directory must contain a symlink to your `src/charm.py` entry
 point so that Juju can call it. You only need to set up the `hooks/install` link
```
