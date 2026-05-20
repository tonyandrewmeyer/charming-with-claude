# fix: strip root user from `NewCommandAs` invocations

**Repository**: canonical/concierge
**Commit**: [1f7c0ec4](https://github.com/canonical/canonical/concierge/commit/1f7c0ec41ebb048298eae0b599ef28c69c74e650)
**Date**: 2024-10-15T21:22:08+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Skip sudo wrapper when command is already running as root to avoid unnecessary privilege escalation

## Changed Files

- M	internal/runner/command.go
- M	internal/runner/runner_test.go

## Diff

```diff
diff --git a/internal/runner/command.go b/internal/runner/command.go
index e0e8d4a..7a76d3c 100644
--- a/internal/runner/command.go
+++ b/internal/runner/command.go
@@ -35,6 +35,10 @@ func NewCommand(executable string, args []string) *Command {
 
 // NewCommandAs constructs a command to be run as the specified user/group.
 func NewCommandAs(user string, group string, executable string, args []string) *Command {
+	if user == "root" {
+		return NewCommand(executable, args)
+	}
+
 	return &Command{
 		Executable: executable,
 		Args:       args,
diff --git a/internal/runner/runner_test.go b/internal/runner/runner_test.go
index a73ee3f..9515b93 100644
--- a/internal/runner/runner_test.go
+++ b/internal/runner/runner_test.go
@@ -33,6 +33,20 @@ func TestNewCommandAs(t *testing.T) {
 	}
 }
 
+func TestNewCommandAsRoot(t *testing.T) {
+	expected := &Command{
+		Executable: "apt-get",
+		Args:       []string{"install", "-y", "cowsay"},
+		User:       "",
+		Group:      "",
+	}
+
+	command := NewCommandAs("root", "foo", "apt-get", []string{"install", "-y", "cowsay"})
+	if !reflect.DeepEqual(expected, command) {
+		t.Fatalf("expected: %+v, got: %+v", expected, command)
+	}
+}
+
 func TestCommandString(t *testing.T) {
 	type test struct {
 		command  *Command
```
