# fix: retry microk8s wait-ready command

**Repository**: canonical/concierge
**Commit**: [ca30333f](https://github.com/canonical/canonical/concierge/commit/ca30333f0340f75cd83c0bd4219387bc3531d847)
**Date**: 2024-10-15T21:31:03+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | error-handling |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Add retry with timeout to microk8s wait-ready instead of single-shot execution

## Changed Files

- M	internal/providers/microk8s.go

## Diff

```diff
diff --git a/internal/providers/microk8s.go b/internal/providers/microk8s.go
index 0eeea14..98cb82e 100644
--- a/internal/providers/microk8s.go
+++ b/internal/providers/microk8s.go
@@ -118,10 +118,16 @@ func (m *MicroK8s) Restore() error {
 
 // init ensures that MicroK8s is installed, minimally configured, and ready.
 func (m *MicroK8s) init() error {
-	return m.runner.RunMany(
-		runner.NewCommand("snap", []string{"start", "microk8s"}),
-		runner.NewCommand("microk8s", []string{"status", "--wait-ready"}),
-	)
+	cmd := runner.NewCommand("snap", []string{"start", "microk8s"})
+	_, err := m.runner.Run(cmd)
+	if err != nil {
+		return err
+	}
+
+	cmd = runner.NewCommand("microk8s", []string{"status", "--wait-ready"})
+	_, err = m.runner.RunWithRetries(cmd, (5 * time.Minute))
+
+	return err
 }
 
 // enableAddons iterates over the specified addons, enabling and configuring them.
```
