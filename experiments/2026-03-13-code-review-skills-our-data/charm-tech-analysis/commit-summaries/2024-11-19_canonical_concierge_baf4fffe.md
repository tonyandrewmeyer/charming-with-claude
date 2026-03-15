# fix: ensure `k8s bootstrap` is idempotent

**Repository**: canonical/concierge
**Commit**: [baf4fffe](https://github.com/canonical/canonical/concierge/commit/baf4fffeb58c6b97b8610d04a07afa508568745f)
**Date**: 2024-11-19T15:58:00+00:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | state-management |
| Severity | high |
| Fix Category | source-fix |

## Summary

Check if k8s needs bootstrap before attempting it, making concierge prepare safe to re-run

## Changed Files

- M	internal/providers/k8s.go

## Diff

```diff
diff --git a/internal/providers/k8s.go b/internal/providers/k8s.go
index d68960e..0368afc 100644
--- a/internal/providers/k8s.go
+++ b/internal/providers/k8s.go
@@ -4,6 +4,7 @@ import (
 	"fmt"
 	"log/slog"
 	"path"
+	"strings"
 	"time"
 
 	"github.com/jnsgruk/concierge/internal/config"
@@ -136,14 +137,16 @@ func (k *K8s) install() error {
 
 // init ensures that K8s is installed, minimally configured, and ready.
 func (k *K8s) init() error {
-	cmd := system.NewCommand("k8s", []string{"bootstrap"})
-	_, err := k.system.RunWithRetries(cmd, (5 * time.Minute))
-	if err != nil {
-		return err
+	if k.needsBootstrap() {
+		cmd := system.NewCommand("k8s", []string{"bootstrap"})
+		_, err := k.system.RunWithRetries(cmd, (5 * time.Minute))
+		if err != nil {
+			return err
+		}
 	}
 
-	cmd = system.NewCommand("k8s", []string{"status", "--wait-ready"})
-	_, err = k.system.RunWithRetries(cmd, (5 * time.Minute))
+	cmd := system.NewCommand("k8s", []string{"status", "--wait-ready"})
+	_, err := k.system.RunWithRetries(cmd, (5 * time.Minute))
 
 	return err
 }
@@ -182,3 +185,14 @@ func (k *K8s) setupKubectl() error {
 
 	return k.system.WriteHomeDirFile(path.Join(".kube", "config"), result)
 }
+
+func (k *K8s) needsBootstrap() bool {
+	cmd := system.NewCommand("k8s", []string{"status"})
+	output, err := k.system.Run(cmd)
+
+	if err != nil && strings.Contains(string(output), "Error: The node is not part of a Kubernetes cluster.") {
+		return true
+	}
+
+	return false
+}
```
