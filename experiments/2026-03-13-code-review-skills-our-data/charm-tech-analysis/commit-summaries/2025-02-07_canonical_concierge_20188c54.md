# fix: don't retry SnapInfo lookup if snap not found

**Repository**: canonical/concierge
**Commit**: [20188c54](https://github.com/canonical/canonical/concierge/commit/20188c549be9fb1b4fcd877d5c86015250271dc8)
**Date**: 2025-02-07T09:13:56+00:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | error-handling |
| Severity | low |
| Fix Category | source-fix |

## Summary

Short-circuit retry loop when snap is definitively not found in the store

## Changed Files

- M	internal/system/snap.go

## Diff

```diff
diff --git a/internal/system/snap.go b/internal/system/snap.go
index 774b6bf..2a58a58 100644
--- a/internal/system/snap.go
+++ b/internal/system/snap.go
@@ -107,6 +107,9 @@ func (s *System) snapIsClassic(name, channel string) (bool, error) {
 	snap, err := s.withRetry(func(ctx context.Context) (*client.Snap, error) {
 		snap, _, err := s.snapd.FindOne(name)
 		if err != nil {
+			if strings.Contains(err.Error(), "snap not found") {
+				return nil, err
+			}
 			return nil, retry.RetryableError(err)
 		}
 		return snap, nil
```
