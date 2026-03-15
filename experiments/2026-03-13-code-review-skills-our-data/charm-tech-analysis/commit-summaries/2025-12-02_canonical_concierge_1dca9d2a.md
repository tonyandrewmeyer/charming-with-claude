# fix: avoid LXD stop to speed up subsequent "prepare" calls (#124)

**Repository**: canonical/concierge
**Commit**: [1dca9d2a](https://github.com/canonical/canonical/concierge/commit/1dca9d2a9c749b7e9b09cadf8bbf3a68616d5a25)
**Date**: 2025-12-02T09:54:49+13:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | lxd |
| Bug Type | state-management |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Skip unnecessary LXD stop/restart when snap channel already matches, saving ~90s on re-runs

## Commit Message

`concierge prepare` took ~90 seconds on every subsequent run because
`workaroundRefresh()` unconditionally stopped LXD whenever installed,
triggering MicroK8s restarts even when no changes were needed.

## Changes

- **Extended `SnapInfo`** to include `TrackingChannel` field capturing
the snap's current channel
- **Added `snapInstalledInfo()`** helper returning installation status
and tracking channel in one call
- **Modified `workaroundRefresh()`** to compare tracking vs target
channel:
  - Channels match → skip stop (no-op path)
  - Channels differ → stop before refresh (preserves workaround)
  - No target channel → skip stop (no refresh occurs)

```go
// Before: always stopped LXD if installed
if snapInfo.Installed {
    args := []string{"stop", l.Name()}
    cmd := system.NewCommand("snap", args)
    _, err = l.system.RunExclusive(cmd)
    // ...
}

// After: only stop when channel will change
if snapInfo.Installed {
    if l.Channel == "" || snapInfo.TrackingChannel == l.Channel {
        return false, nil  // Fast path: no refresh needed
    }
    // Stop only when refresh will actually happen
    args := []string{"stop", l.Name()}
    // ...
}
```

Second+ runs now complete in ~2s instead of ~90s when system is already
configured correctly.

- Fixes canonical/concierge#69

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: tonyandrewmeyer <826522+tonyandrewmeyer@users.noreply.github.com>
Co-authored-by: Tony Meyer <tony.meyer@canonical.com>
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

## Changed Files

- M	internal/providers/lxd.go
- M	internal/providers/lxd_test.go
- M	internal/system/mock_system.go
- M	internal/system/snap.go

## Diff

```diff
diff --git a/internal/providers/lxd.go b/internal/providers/lxd.go
index 05dcbd7..2b45569 100644
--- a/internal/providers/lxd.go
+++ b/internal/providers/lxd.go
@@ -169,7 +169,21 @@ func (l *LXD) workaroundRefresh() (bool, error) {
 		return false, fmt.Errorf("failed to lookup snap details: %w", err)
 	}
 
+	// Only stop LXD if it's installed AND needs to be refreshed (channel mismatch).
 	if snapInfo.Installed {
+		// If no channel is specified, snapd will refresh on the current channel without changing it.
+		// If the tracking channel matches the target channel, the refresh won't change channels.
+		// In both cases, no stop is needed since the channel isn't changing.
+        if l.Channel == "" || snapInfo.TrackingChannel == l.Channel {
+		    slog.Debug("Skipping LXD stop - no channel change required",
+				"tracking", snapInfo.TrackingChannel, "target", l.Channel)
+			return false, nil
+		}
+
+		// Channel mismatch detected - LXD will be refreshed, so stop it first
+		// to work around a snap refresh issue with missing socket files.
+		slog.Debug("LXD channel mismatch, stopping for refresh",
+			"tracking", snapInfo.TrackingChannel, "target", l.Channel)
 		args := []string{"stop", l.Name()}
 		cmd := system.NewCommand("snap", args)
 		_, err = l.system.RunExclusive(cmd)
diff --git a/internal/providers/lxd_test.go b/internal/providers/lxd_test.go
index 7ca2630..897657c 100644
--- a/internal/providers/lxd_test.go
+++ b/internal/providers/lxd_test.go
@@ -72,10 +72,9 @@ func TestLXDPrepareCommands(t *testing.T) {
 func TestLXDPrepareCommandsLXDAlreadyInstalled(t *testing.T) {
 	config := &config.Config{}
 
+	// When LXD is already installed on the same channel, it should not be stopped.
 	expected := []string{
-		"snap stop lxd",
 		"snap refresh lxd",
-		"snap start lxd",
 		"lxd waitready --timeout 270",
 		"lxd init --minimal",
 		"lxc network set lxdbr0 ipv6.address none",
@@ -96,6 +95,35 @@ func TestLXDPrepareCommandsLXDAlreadyInstalled(t *testing.T) {
 	}
 }
 
+func TestLXDPrepareCommandsLXDChannelChange(t *testing.T) {
+	config := &config.Config{}
+	config.Providers.LXD.Channel = "latest/edge"
+
+	// When LXD is installed but on a different channel, it should be stopped before refresh.
+	expected := []string{
+		"snap stop lxd",
+		"snap refresh lxd --channel latest/edge",
+		"snap start lxd",
+		"lxd waitready --timeout 270",
+		"lxd init --minimal",
+		"lxc network set lxdbr0 ipv6.address none",
+		"chmod a+wr /var/snap/lxd/common/lxd/unix.socket",
+		"usermod -a -G lxd test-user",
+		"iptables -F FORWARD",
+		"iptables -P FORWARD ACCEPT",
+	}
+
+	system := system.NewMockSystem()
+	system.MockSnapStoreLookup("lxd", "latest/stable", false, true)
+
+	lxd := NewLXD(system, config)
+	lxd.Prepare()
+
+	if !reflect.DeepEqual(expected, system.ExecutedCommands) {
+		t.Fatalf("expected: %v, got: %v", expected, system.ExecutedCommands)
+	}
+}
+
 func TestLXDRestore(t *testing.T) {
 	config := &config.Config{}
 
diff --git a/internal/system/mock_system.go b/internal/system/mock_system.go
index 3770c23..b869a20 100644
--- a/internal/system/mock_system.go
+++ b/internal/system/mock_system.go
@@ -53,9 +53,14 @@ func (r *MockSystem) MockFile(filePath string, contents []byte) {
 
 // MockSnapStoreLookup gets a new test snap and adds a mock snap into the mock test
 func (r *MockSystem) MockSnapStoreLookup(name, channel string, classic, installed bool) *Snap {
+	trackingChannel := ""
+	if installed {
+		trackingChannel = channel
+	}
 	r.mockSnapInfo[name] = &SnapInfo{
-		Installed: installed,
-		Classic:   classic,
+		Installed:       installed,
+		Classic:         classic,
+		TrackingChannel: trackingChannel,
 	}
 	return &Snap{Name: name, Channel: channel}
 }
diff --git a/internal/system/snap.go b/internal/system/snap.go
index c490757..6f89763 100644
--- a/internal/system/snap.go
+++ b/internal/system/snap.go
@@ -16,8 +16,9 @@ import (
 
 // SnapInfo represents information about a snap fetched from the snapd API.
 type SnapInfo struct {
-	Installed bool
-	Classic   bool
+	Installed       bool
+	Classic         bool
+	TrackingChannel string
 }
 
 // Snap represents a given snap on a given channel.
@@ -51,10 +52,10 @@ func (s *System) SnapInfo(snap string, channel string) (*SnapInfo, error) {
 		return nil, err
 	}
 
-	installed := s.snapInstalled(snap)
+	installed, trackingChannel := s.snapInstalledInfo(snap)
 
-	slog.Debug("Queried snapd API", "snap", snap, "installed", installed, "classic", classic)
-	return &SnapInfo{Installed: installed, Classic: classic}, nil
+	slog.Debug("Queried snapd API", "snap", snap, "installed", installed, "classic", classic, "tracking", trackingChannel)
+	return &SnapInfo{Installed: installed, Classic: classic, TrackingChannel: trackingChannel}, nil
 }
 
 // SnapChannels returns the list of channels available for a given snap.
@@ -93,8 +94,11 @@ func (s *System) SnapChannels(snap string) ([]string, error) {
 	return channels, nil
 }
 
-// snapInstalled is a helper that reports if the snap is currently Installed.
-func (s *System) snapInstalled(name string) bool {
+// snapInstalledInfo is a helper that reports if the snap is currently installed
+// and returns its tracking channel. The tracking channel is the channel the snap
+// is currently following (e.g., "latest/stable"). Returns empty string if the
+// snap is not installed or if the tracking channel cannot be determined.
+func (s *System) snapInstalledInfo(name string) (bool, string) {
 	snap, err := s.withRetry(func(ctx context.Context) (*client.Snap, error) {
 		snap, _, err := s.snapd.Snap(name)
 		if err != nil && strings.Contains(err.Error(), "snap not installed") {
@@ -105,10 +109,18 @@ func (s *System) snapInstalled(name string) bool {
 		return snap, nil
 	})
 	if err != nil || snap == nil {
-		return false
+		return false, ""
 	}
 
-	return snap.Status == client.StatusActive
+	if snap.Status == client.StatusActive {
+		trackingChannel := snap.TrackingChannel
+		if trackingChannel == "" {
+			trackingChannel = snap.Channel
+		}
+		return true, trackingChannel
+	}
+
+	return false, ""
 }
 
 // snapIsClassic reports whether or not the snap at the tip of the specified channel uses
```
