# fix: ensure command path is looked up in `Command.commandString`

**Repository**: canonical/concierge
**Commit**: [e92db26c](https://github.com/canonical/canonical/concierge/commit/e92db26c4587d3ef1c0d9ed860f4bcd8b015729b)
**Date**: 2024-10-12T09:28:39+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Move PATH lookup into commandString so commands resolve correctly when run via shell

## Changed Files

- M	internal/runner/command.go
- M	internal/runner/runner.go
- M	internal/runner/runner_test.go

## Diff

```diff
diff --git a/internal/runner/command.go b/internal/runner/command.go
index 186a218..ff6ff98 100644
--- a/internal/runner/command.go
+++ b/internal/runner/command.go
@@ -2,6 +2,8 @@ package runner
 
 import (
 	"bytes"
+	"log/slog"
+	"os/exec"
 	"os/user"
 	"strings"
 )
@@ -65,6 +67,12 @@ func NewCommandWithGroup(executable string, args []string, group string) *Comman
 // commandString puts together a command to be executed in a shell, including the `sudo`
 // command and its arguments where appropriate.
 func (c *Command) commandString() string {
+	path, err := exec.LookPath(c.Executable)
+	if err != nil {
+		slog.Warn("Failed to lookup command in path", "command", c.Executable)
+		path = c.Executable
+	}
+
 	cmdArgs := []string{}
 
 	if len(c.User) > 0 || len(c.Group) > 0 {
@@ -79,7 +87,7 @@ func (c *Command) commandString() string {
 		cmdArgs = append(cmdArgs, "-g", c.Group)
 	}
 
-	cmdArgs = append(cmdArgs, c.Executable)
+	cmdArgs = append(cmdArgs, path)
 	cmdArgs = append(cmdArgs, c.Args...)
 
 	return strings.Join(cmdArgs, " ")
diff --git a/internal/runner/runner.go b/internal/runner/runner.go
index ecd7844..8513fc5 100644
--- a/internal/runner/runner.go
+++ b/internal/runner/runner.go
@@ -6,7 +6,6 @@ import (
 	"log/slog"
 	"os"
 	"os/exec"
-	"strings"
 
 	"github.com/fatih/color"
 )
@@ -23,11 +22,6 @@ type Runner struct {
 
 // Run executes the command, returning the stdout/stderr where appropriate.
 func (r *Runner) Run(c *Command) (*CommandResult, error) {
-	path, err := exec.LookPath(c.Executable)
-	if err != nil {
-		return nil, fmt.Errorf("could not find '%s' command in path: %w", c.Executable, err)
-	}
-
 	logger := slog.Default()
 	if len(c.User) > 0 {
 		logger = slog.With("user", c.User)
@@ -42,8 +36,8 @@ func (r *Runner) Run(c *Command) (*CommandResult, error) {
 	cmd.Stdout = &stdout
 	cmd.Stderr = &stderr
 
-	logger.Debug("Running command", "command", fmt.Sprintf("%s %s", path, strings.Join(c.Args, " ")))
-	err = cmd.Run()
+	logger.Debug("Running command", "command", c.commandString())
+	err := cmd.Run()
 
 	if r.trace {
 		fmt.Print(generateTraceMessage(c.commandString(), stdout.String(), stderr.String()))
diff --git a/internal/runner/runner_test.go b/internal/runner/runner_test.go
index dc28731..394c0e6 100644
--- a/internal/runner/runner_test.go
+++ b/internal/runner/runner_test.go
@@ -53,18 +53,19 @@ func TestCommandString(t *testing.T) {
 		expected string
 	}
 
+	// Use CONCIERGE_TEST_COMMAND to avoid $PATH lookups making tests flaky
 	tests := []test{
 		{
-			command:  NewCommand("juju", []string{"add-model", "testing"}),
-			expected: "juju add-model testing",
+			command:  NewCommand("CONCIERGE_TEST_COMMAND", []string{"add-model", "testing"}),
+			expected: "CONCIERGE_TEST_COMMAND add-model testing",
 		},
 		{
-			command:  NewCommandSudo("apt-get", []string{"install", "-y", "cowsay"}),
-			expected: "sudo -u root apt-get install -y cowsay",
+			command:  NewCommandSudo("CONCIERGE_TEST_COMMAND", []string{"install", "-y", "cowsay"}),
+			expected: "sudo -u root CONCIERGE_TEST_COMMAND install -y cowsay",
 		},
 		{
-			command:  NewCommandWithGroup("apt-get", []string{"install", "-y", "cowsay"}, "apters"),
-			expected: "sudo -g apters apt-get install -y cowsay",
+			command:  NewCommandWithGroup("CONCIERGE_TEST_COMMAND", []string{"install", "-y", "cowsay"}, "apters"),
+			expected: "sudo -g apters CONCIERGE_TEST_COMMAND install -y cowsay",
 		},
 	}
```
