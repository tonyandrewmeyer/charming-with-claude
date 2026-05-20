# fix: ensure logging is consistently capitalised

**Repository**: canonical/concierge
**Commit**: [921fcc6c](https://github.com/canonical/canonical/concierge/commit/921fcc6c9481abf69c2143affd14f52a76e64919)
**Date**: 2024-10-11T16:40:06+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | cli |
| Bug Type | other |
| Severity | low |
| Fix Category | source-fix |

## Summary

Capitalize first letter of all log messages for consistent formatting

## Changed Files

- M	internal/concierge/manager.go
- M	internal/config/config.go
- M	internal/packages/snap.go
- M	internal/runner/runner.go

## Diff

```diff
diff --git a/internal/concierge/manager.go b/internal/concierge/manager.go
index 7376668..cde582c 100644
--- a/internal/concierge/manager.go
+++ b/internal/concierge/manager.go
@@ -84,7 +84,7 @@ func (m *Manager) recordRuntimeConfig() error {
 		return fmt.Errorf("failed to write config record file: %w", err)
 	}
 
-	slog.Debug("merged runtime configuration saved", "path", recordPath)
+	slog.Debug("Merged runtime configuration saved", "path", recordPath)
 
 	return nil
 }
@@ -115,7 +115,7 @@ func (m *Manager) loadRuntimeConfig() error {
 
 	m.config = &config
 
-	slog.Debug("loaded previous runtime configuration", "path", recordPath)
+	slog.Debug("Loaded previous runtime configuration", "path", recordPath)
 
 	return nil
 }
diff --git a/internal/config/config.go b/internal/config/config.go
index d7b9699..718dd3a 100644
--- a/internal/config/config.go
+++ b/internal/config/config.go
@@ -151,7 +151,7 @@ func bindFlags(cmd *cobra.Command) {
 		// Apply the viper config value to the flag when the flag is not set and viper has a value
 		if !f.Changed && viper.IsSet(f.Name) {
 			val := viper.Get(f.Name)
-			slog.Debug("override detected in environment", "override", f.Name, "value", fmt.Sprintf("%v", val), "env_var", flagToEnvVar(f.Name))
+			slog.Debug("Override detected in environment", "override", f.Name, "value", fmt.Sprintf("%v", val), "env_var", flagToEnvVar(f.Name))
 			cmd.Flags().Set(f.Name, fmt.Sprintf("%v", val))
 		}
 	})
diff --git a/internal/packages/snap.go b/internal/packages/snap.go
index b7c1195..8dd4ece 100644
--- a/internal/packages/snap.go
+++ b/internal/packages/snap.go
@@ -32,7 +32,7 @@ type Snap struct {
 
 // Installed is a helper that reports if the snap is currently Installed.
 func (s *Snap) Installed() bool {
-	slog.Debug("querying snap install status", "snap", s.Name)
+	slog.Debug("Querying snap install status", "snap", s.Name)
 
 	snap, _, err := snapdClient.New(nil).Snap(s.Name)
 	if err != nil {
@@ -45,7 +45,7 @@ func (s *Snap) Installed() bool {
 // Classic reports whether or not the snap at the tip of the specified channel uses
 // Classic confinement or not.
 func (s *Snap) Classic() (bool, error) {
-	slog.Debug("querying snap confinement", "snap", s.Name)
+	slog.Debug("Querying snap confinement", "snap", s.Name)
 
 	snap, _, err := snapdClient.New(nil).FindOne(s.Name)
 	if err != nil {
@@ -57,7 +57,7 @@ func (s *Snap) Classic() (bool, error) {
 
 // tracking reports which channel an installed snap is tracking.
 func (s *Snap) Tracking() (string, error) {
-	slog.Debug("querying snap channel tracking", "snap", s.Name)
+	slog.Debug("Querying snap channel tracking", "snap", s.Name)
 
 	snap, _, err := snapdClient.New(nil).Snap(s.Name)
 	if err != nil {
diff --git a/internal/runner/runner.go b/internal/runner/runner.go
index 4810dd3..ecd7844 100644
--- a/internal/runner/runner.go
+++ b/internal/runner/runner.go
@@ -42,7 +42,7 @@ func (r *Runner) Run(c *Command) (*CommandResult, error) {
 	cmd.Stdout = &stdout
 	cmd.Stderr = &stderr
 
-	logger.Debug("running command", "command", fmt.Sprintf("%s %s", path, strings.Join(c.Args, " ")))
+	logger.Debug("Running command", "command", fmt.Sprintf("%s %s", path, strings.Join(c.Args, " ")))
 	err = cmd.Run()
 
 	if r.trace {
```
