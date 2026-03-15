# fix: show debug logs when either `-v` or `--trace` are used

**Repository**: canonical/concierge
**Commit**: [dd30fa88](https://github.com/canonical/canonical/concierge/commit/dd30fa88eb9faa5c68219bd4c941dde0d14de3a2)
**Date**: 2024-10-15T10:57:30+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | cli |
| Bug Type | logic-error |
| Severity | low |
| Fix Category | source-fix |

## Summary

Fix boolean condition from AND to OR so debug logs show with either -v or --trace flag

## Changed Files

- M	cmd/main.go

## Diff

```diff
diff --git a/cmd/main.go b/cmd/main.go
index b6bc94a..4934199 100644
--- a/cmd/main.go
+++ b/cmd/main.go
@@ -31,7 +31,7 @@ func parseLoggingFlags(flags *pflag.FlagSet) {
 
 	// Set the default log level to "DEBUG" if verbose is specified.
 	level := slog.LevelInfo
-	if !verbose && trace {
+	if verbose || trace {
 		level = slog.LevelDebug
 	}
```
