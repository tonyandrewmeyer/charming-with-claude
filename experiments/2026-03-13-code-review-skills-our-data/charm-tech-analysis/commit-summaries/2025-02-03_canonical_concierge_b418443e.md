# fix: lookup snap in store and bail early if not exists in SnapInfo (#34)

**Repository**: canonical/concierge
**Commit**: [b418443e](https://github.com/canonical/canonical/concierge/commit/b418443ec6289f03bb369915a9359ab5cc7f0b52)
**Date**: 2025-02-03T16:50:21+00:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | data-validation |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Pre-check snap existence in store before entering retry loop to fail fast on invalid snap names

## Commit Message

This is a simple fix that ensures that non-existent snaps don't get
repeatedly looked up with the retry mechanism used to establish more
detailed Snap information.

The primary motivation for this is failing fast rather than keeping
the user waiting if they specify a non-existent snap.

## Changed Files

- M	internal/system/snap.go

## Diff

```diff
diff --git a/internal/system/snap.go b/internal/system/snap.go
index 774b6bf..998c194 100644
--- a/internal/system/snap.go
+++ b/internal/system/snap.go
@@ -46,6 +46,12 @@ func NewSnapFromString(snap string) *Snap {
 // SnapInfo returns information about a given snap, looking up details in the snap
 // store using the snapd client API where necessary.
 func (s *System) SnapInfo(snap string, channel string) (*SnapInfo, error) {
+	// Simple check to see if the snap actually exists in the store.
+	_, _, err := s.snapd.FindOne(snap)
+	if err != nil {
+		return nil, fmt.Errorf("unable to find snap '%s' in store: %w", snap, err)
+	}
+
 	classic, err := s.snapIsClassic(snap, channel)
 	if err != nil {
 		return nil, err
```
