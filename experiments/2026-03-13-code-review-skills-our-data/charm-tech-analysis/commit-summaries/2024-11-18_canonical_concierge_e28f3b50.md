# fix: log command output on failure (#16)

**Repository**: canonical/concierge
**Commit**: [e28f3b50](https://github.com/canonical/canonical/concierge/commit/e28f3b50e52d7aad40c17728625c3142332c6f85)
**Date**: 2024-11-18T16:58:28-05:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | cli |
| Bug Type | error-handling |
| Severity | low |
| Fix Category | source-fix |

## Summary

Always log command output when a command fails, not just in trace mode

## Changed Files

- M	internal/system/runner.go

## Diff

```diff
diff --git a/internal/system/runner.go b/internal/system/runner.go
index 621533c..bf4abf5 100644
--- a/internal/system/runner.go
+++ b/internal/system/runner.go
@@ -68,7 +68,7 @@ func (s *System) Run(c *Command) ([]byte, error) {
 
 	output, err := cmd.CombinedOutput()
 
-	if s.trace {
+	if s.trace || err != nil {
 		fmt.Print(generateTraceMessage(c.CommandString(), output))
 	}
```
