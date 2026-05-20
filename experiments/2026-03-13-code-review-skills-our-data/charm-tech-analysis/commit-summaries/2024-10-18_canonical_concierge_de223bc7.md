# fix: demote `$PATH` lookup logging to `DEBUG`

**Repository**: canonical/concierge
**Commit**: [de223bc7](https://github.com/canonical/canonical/concierge/commit/de223bc7bdeda90a823fb515d96931c9fd1d8736)
**Date**: 2024-10-18T20:26:29+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | cli |
| Bug Type | other |
| Severity | low |
| Fix Category | source-fix |

## Summary

Downgrade PATH lookup failure log from Warn to Debug to reduce noise

## Changed Files

- M	internal/runner/command.go

## Diff

```diff
diff --git a/internal/runner/command.go b/internal/runner/command.go
index 6e91ae7..9c7a146 100644
--- a/internal/runner/command.go
+++ b/internal/runner/command.go
@@ -52,7 +52,7 @@ func NewCommandAs(user string, group string, executable string, args []string) *
 func (c *Command) CommandString() string {
 	path, err := exec.LookPath(c.Executable)
 	if err != nil {
-		slog.Warn("Failed to lookup command in path", "command", c.Executable)
+		slog.Debug("Failed to lookup command in path", "command", c.Executable)
 		path = c.Executable
 	}
```
