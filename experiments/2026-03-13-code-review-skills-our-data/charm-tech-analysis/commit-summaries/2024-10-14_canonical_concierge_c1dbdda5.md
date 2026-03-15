# fix: more robust shell path detection for command execution

**Repository**: canonical/concierge
**Commit**: [c1dbdda5](https://github.com/canonical/canonical/concierge/commit/c1dbdda5bc8606618fa29f566e79c469eb33ca91)
**Date**: 2024-10-14T09:48:30+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | edge-case |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Fall back to bash/sh when SHELL env var is unset instead of failing command execution

## Changed Files

- M	internal/runner/runner.go

## Diff

```diff
diff --git a/internal/runner/runner.go b/internal/runner/runner.go
index 8513fc5..edde573 100644
--- a/internal/runner/runner.go
+++ b/internal/runner/runner.go
@@ -2,6 +2,7 @@ package runner
 
 import (
 	"bytes"
+	"errors"
 	"fmt"
 	"log/slog"
 	"os"
@@ -30,14 +31,19 @@ func (r *Runner) Run(c *Command) (*CommandResult, error) {
 		logger = slog.With("group", c.Group)
 	}
 
-	cmd := exec.Command(os.Getenv("SHELL"), "-c", c.commandString())
+	shell, err := getShellPath()
+	if err != nil {
+		return nil, fmt.Errorf("unable to determine shell path to run command")
+	}
+
+	cmd := exec.Command(shell, "-c", c.commandString())
 
 	var stdout, stderr bytes.Buffer
 	cmd.Stdout = &stdout
 	cmd.Stderr = &stderr
 
 	logger.Debug("Running command", "command", c.commandString())
-	err := cmd.Run()
+	err = cmd.Run()
 
 	if r.trace {
 		fmt.Print(generateTraceMessage(c.commandString(), stdout.String(), stderr.String()))
@@ -73,3 +79,30 @@ func generateTraceMessage(cmd, stdout, stderr string) string {
 	}
 	return result
 }
+
+// getShellPath tries to find the path to the user's preferred shell, as per the `SHELL“
+// environment variable. If that cannot be found, it looks for a path to "bash", and to
+// "sh" in that order. If no shell can be found, then an error is returned.
+func getShellPath() (string, error) {
+	// If the `SHELL` var is set, return that.
+	shellVar := os.Getenv("SHELL")
+	if len(shellVar) > 0 {
+		return shellVar, nil
+	}
+
+	// Try both the command name (to lookup in PATH), and common default paths.
+	for _, shell := range []string{"bash", "/bin/bash", "sh", "/bin/sh"} {
+		// Check if the shell path exists
+		if _, err := os.Stat(shell); errors.Is(err, os.ErrNotExist) {
+			// If the path doesn't exist, the lookup the value in the `PATH` variable
+			path, err := exec.LookPath(shell)
+			if err != nil {
+				continue
+			}
+			return path, nil
+		}
+		return shell, nil
+	}
+
+	return "", fmt.Errorf("could not find path to a shell")
+}
```
