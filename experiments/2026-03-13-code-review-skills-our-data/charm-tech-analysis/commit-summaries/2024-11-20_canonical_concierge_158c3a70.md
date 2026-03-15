# fix: ensure that `lxd` is started again after refresh

**Repository**: canonical/concierge
**Commit**: [158c3a70](https://github.com/canonical/canonical/concierge/commit/158c3a708b05f98b6f6e98e9fc98b1a816842373)
**Date**: 2024-11-20T17:16:36+00:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | lxd |
| Bug Type | state-management |
| Severity | high |
| Fix Category | source-fix |

## Summary

Restart LXD snap after stopping it for refresh workaround to avoid leaving it in stopped state

## Changed Files

- M	internal/providers/lxd.go
- M	internal/providers/lxd_test.go

## Diff

```diff
diff --git a/internal/providers/lxd.go b/internal/providers/lxd.go
index fb62103..469f52d 100644
--- a/internal/providers/lxd.go
+++ b/internal/providers/lxd.go
@@ -104,7 +104,8 @@ func (l *LXD) Restore() error {
 
 // install ensures that LXD is installed.
 func (l *LXD) install() error {
-	err := l.workaroundRefresh()
+	// Check if LXD is already installed, and stop the snap if it is.
+	restart, err := l.workaroundRefresh()
 	if err != nil {
 		return err
 	}
@@ -116,6 +117,17 @@ func (l *LXD) install() error {
 		return err
 	}
 
+	// If we stopped the LXD snap, make sure we start it again now the refresh
+	// has happened.
+	if restart {
+		args := []string{"start", l.Name()}
+		cmd := system.NewCommand("snap", args)
+		_, err = l.system.RunExclusive(cmd)
+		if err != nil {
+			return err
+		}
+	}
+
 	return nil
 }
 
@@ -151,10 +163,10 @@ func (l *LXD) deconflictFirewall() error {
 // workaroundRefresh checks if LXD will be refreshed and stops it first.
 // This is a workaround for an issue in the LXD snap sometimes failing
 // on refresh because of a missing snap socket file.
-func (l *LXD) workaroundRefresh() error {
+func (l *LXD) workaroundRefresh() (bool, error) {
 	snapInfo, err := l.system.SnapInfo(l.Name(), l.Channel)
 	if err != nil {
-		return fmt.Errorf("failed to lookup snap details: %w", err)
+		return false, fmt.Errorf("failed to lookup snap details: %w", err)
 	}
 
 	if snapInfo.Installed {
@@ -162,9 +174,10 @@ func (l *LXD) workaroundRefresh() error {
 		cmd := system.NewCommand("snap", args)
 		_, err = l.system.RunExclusive(cmd)
 		if err != nil {
-			return fmt.Errorf("command failed: %w", err)
+			return false, fmt.Errorf("command failed: %w", err)
 		}
+		return true, nil
 	}
 
-	return nil
+	return false, nil
 }
diff --git a/internal/providers/lxd_test.go b/internal/providers/lxd_test.go
index 2eb5d1b..f870ab2 100644
--- a/internal/providers/lxd_test.go
+++ b/internal/providers/lxd_test.go
@@ -75,6 +75,7 @@ func TestLXDPrepareCommandsLXDAlreadyInstalled(t *testing.T) {
 	expected := []string{
 		"snap stop lxd",
 		"snap refresh lxd",
+		"snap start lxd",
 		"lxd waitready",
 		"lxd init --minimal",
 		"lxc network set lxdbr0 ipv6.address none",
```
