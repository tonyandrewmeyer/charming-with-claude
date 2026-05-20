# fix: remove explicit snap start for microk8s

**Repository**: canonical/concierge
**Commit**: [89522a66](https://github.com/canonical/canonical/concierge/commit/89522a66915f693928f98fc70b0904cb20ecb037)
**Date**: 2024-10-18T21:33:54+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | multipass |
| Bug Type | logic-error |
| Severity | low |
| Fix Category | source-fix |

## Summary

Remove redundant explicit snap start for microk8s since install already starts it

## Changed Files

- M	internal/providers/microk8s.go
- M	internal/providers/microk8s_test.go

## Diff

```diff
diff --git a/internal/providers/microk8s.go b/internal/providers/microk8s.go
index dafa2cf..616e30c 100644
--- a/internal/providers/microk8s.go
+++ b/internal/providers/microk8s.go
@@ -142,14 +142,8 @@ func (m *MicroK8s) install() error {
 
 // init ensures that MicroK8s is installed, minimally configured, and ready.
 func (m *MicroK8s) init() error {
-	cmd := runner.NewCommand("snap", []string{"start", "microk8s"})
-	_, err := m.runner.Run(cmd)
-	if err != nil {
-		return err
-	}
-
-	cmd = runner.NewCommand("microk8s", []string{"status", "--wait-ready"})
-	_, err = m.runner.RunWithRetries(cmd, (5 * time.Minute))
+	cmd := runner.NewCommand("microk8s", []string{"status", "--wait-ready"})
+	_, err := m.runner.RunWithRetries(cmd, (5 * time.Minute))
 
 	return err
 }
diff --git a/internal/providers/microk8s_test.go b/internal/providers/microk8s_test.go
index ed36feb..507424b 100644
--- a/internal/providers/microk8s_test.go
+++ b/internal/providers/microk8s_test.go
@@ -99,7 +99,6 @@ func TestMicroK8sPrepareCommands(t *testing.T) {
 
 	expectedCommands := []string{
 		"snap install microk8s --channel 1.31-strict/stable",
-		"snap start microk8s",
 		"microk8s status --wait-ready",
 		"microk8s enable hostpath-storage",
 		"microk8s enable dns",
```
