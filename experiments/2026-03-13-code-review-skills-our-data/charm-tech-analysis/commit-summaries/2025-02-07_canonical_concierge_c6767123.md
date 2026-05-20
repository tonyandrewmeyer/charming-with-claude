# fix: lookup channels for correct snap in SnapChannels

**Repository**: canonical/concierge
**Commit**: [c6767123](https://github.com/canonical/canonical/concierge/commit/c67671234929b42f52d6e279aa715aef2e480fa3)
**Date**: 2025-02-07T09:14:25+00:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | logic-error |
| Severity | high |
| Fix Category | source-fix |

## Summary

Fix hardcoded 'microk8s' snap name in SnapChannels to use the actual requested snap name

## Changed Files

- M	internal/system/snap.go

## Diff

```diff
diff --git a/internal/system/snap.go b/internal/system/snap.go
index 2a58a58..ae72ea9 100644
--- a/internal/system/snap.go
+++ b/internal/system/snap.go
@@ -64,7 +64,7 @@ func (s *System) SnapChannels(snap string) ([]string, error) {
 		return nil, err
 	}
 
-	storeSnap, _, err := s.snapd.FindOne("microk8s")
+	storeSnap, _, err := s.snapd.FindOne(snap)
 	if err != nil {
 		return nil, err
 	}
```
