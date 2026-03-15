# fix: better logging for removal of packages during restore

**Repository**: canonical/concierge
**Commit**: [b220ba99](https://github.com/canonical/canonical/concierge/commit/b220ba991d4e4e3b5dff68c298a72f1667637a05)
**Date**: 2024-10-15T12:55:14+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | cli |
| Bug Type | other |
| Severity | low |
| Fix Category | source-fix |

## Summary

Add log messages for successful package and snap removal during restore

## Changed Files

- M	internal/handlers/deb.go
- M	internal/handlers/snap.go

## Diff

```diff
diff --git a/internal/handlers/deb.go b/internal/handlers/deb.go
index 98add77..37b6044 100644
--- a/internal/handlers/deb.go
+++ b/internal/handlers/deb.go
@@ -86,6 +86,7 @@ func (h *DebHandler) removeDeb(d *packages.Deb) error {
 		return fmt.Errorf("failed to remove apt package '%s': %w", d.Name, err)
 	}
 
+	slog.Info("Removed apt package", "package", d.Name)
 	return nil
 }
 
diff --git a/internal/handlers/snap.go b/internal/handlers/snap.go
index 115de3a..06e78f6 100644
--- a/internal/handlers/snap.go
+++ b/internal/handlers/snap.go
@@ -97,5 +97,6 @@ func (h *SnapHandler) removeSnap(s *packages.Snap) error {
 		return fmt.Errorf("failed to remove snap '%s': %w", s.Name, err)
 	}
 
+	slog.Info("Removed snap", "snap", s.Name)
 	return nil
 }
```
