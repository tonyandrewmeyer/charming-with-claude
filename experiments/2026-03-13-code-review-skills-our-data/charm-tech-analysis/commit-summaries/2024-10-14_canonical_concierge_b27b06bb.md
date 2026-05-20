# fix: report confinement status for correct snap channel when specified

**Repository**: canonical/concierge
**Commit**: [b27b06bb](https://github.com/canonical/canonical/concierge/commit/b27b06bbbd17f72c6ccf16ac733f1dc8fd9aa8e7)
**Date**: 2024-10-14T11:13:53+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Check confinement for the specified channel rather than the default channel

## Changed Files

- M	internal/packages/snap.go

## Diff

```diff
diff --git a/internal/packages/snap.go b/internal/packages/snap.go
index 8dd4ece..598e604 100644
--- a/internal/packages/snap.go
+++ b/internal/packages/snap.go
@@ -52,6 +52,11 @@ func (s *Snap) Classic() (bool, error) {
 		return false, fmt.Errorf("failed to find snap: %w", err)
 	}
 
+	channel, ok := snap.Channels[s.Channel]
+	if ok {
+		return channel.Confinement == "classic", nil
+	}
+
 	return snap.Confinement == "classic", nil
 }
```
