# fix: Workaround LXD refresh issue

**Repository**: canonical/concierge
**Commit**: [fea22ef2](https://github.com/canonical/canonical/concierge/commit/fea22ef23d1f57a05101bad44939c5149b74b98a)
**Date**: 2024-11-20T09:25:42-05:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | lxd |
| Bug Type | edge-case |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Stop LXD before snap refresh to work around missing socket file issue during refresh

## Changed Files

- M	internal/providers/lxd.go

## Diff

```diff
diff --git a/internal/providers/lxd.go b/internal/providers/lxd.go
index b1a83fa..fb62103 100644
--- a/internal/providers/lxd.go
+++ b/internal/providers/lxd.go
@@ -104,9 +104,14 @@ func (l *LXD) Restore() error {
 
 // install ensures that LXD is installed.
 func (l *LXD) install() error {
+	err := l.workaroundRefresh()
+	if err != nil {
+		return err
+	}
+
 	snapHandler := packages.NewSnapHandler(l.system, l.snaps)
 
-	err := snapHandler.Prepare()
+	err = snapHandler.Prepare()
 	if err != nil {
 		return err
 	}
@@ -142,3 +147,24 @@ func (l *LXD) deconflictFirewall() error {
 		system.NewCommand("iptables", []string{"-P", "FORWARD", "ACCEPT"}),
 	)
 }
+
+// workaroundRefresh checks if LXD will be refreshed and stops it first.
+// This is a workaround for an issue in the LXD snap sometimes failing
+// on refresh because of a missing snap socket file.
+func (l *LXD) workaroundRefresh() error {
+	snapInfo, err := l.system.SnapInfo(l.Name(), l.Channel)
+	if err != nil {
+		return fmt.Errorf("failed to lookup snap details: %w", err)
+	}
+
+	if snapInfo.Installed {
+		args := []string{"stop", l.Name()}
+		cmd := system.NewCommand("snap", args)
+		_, err = l.system.RunExclusive(cmd)
+		if err != nil {
+			return fmt.Errorf("command failed: %w", err)
+		}
+	}
+
+	return nil
+}
```
