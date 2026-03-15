# fix: add retry to Snap channel lookup

**Repository**: canonical/concierge
**Commit**: [1ba95fa8](https://github.com/canonical/canonical/concierge/commit/1ba95fa802870e56af634d79ecd8e682953b84c2)
**Date**: 2025-02-07T09:16:29+00:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | error-handling |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Add retry with backoff to snap channel lookups to handle transient snapd API errors

## Changed Files

- M	internal/system/snap.go

## Diff

```diff
diff --git a/internal/system/snap.go b/internal/system/snap.go
index ae72ea9..c490757 100644
--- a/internal/system/snap.go
+++ b/internal/system/snap.go
@@ -64,7 +64,17 @@ func (s *System) SnapChannels(snap string) ([]string, error) {
 		return nil, err
 	}
 
-	storeSnap, _, err := s.snapd.FindOne(snap)
+	storeSnap, err := s.withRetry(func(ctx context.Context) (*client.Snap, error) {
+		snap, _, err := s.snapd.FindOne(snap)
+		if err != nil {
+			if strings.Contains(err.Error(), "snap not found") {
+				return nil, err
+			}
+			return nil, retry.RetryableError(err)
+
+		}
+		return snap, nil
+	})
 	if err != nil {
 		return nil, err
 	}
```
