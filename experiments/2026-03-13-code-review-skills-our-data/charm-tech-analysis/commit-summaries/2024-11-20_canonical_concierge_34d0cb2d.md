# fix: ensure `network` is enabled for k8s presets (#19)

**Repository**: canonical/concierge
**Commit**: [34d0cb2d](https://github.com/canonical/canonical/concierge/commit/34d0cb2d126e44eb1784fb68dac3ffc6fe3797ad)
**Date**: 2024-11-20T09:11:59+00:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | config |
| Bug Type | config-parsing |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Add missing 'network' feature to k8s preset configurations

## Changed Files

- M	internal/config/presets.go
- M	internal/providers/k8s_test.go

## Diff

```diff
diff --git a/internal/config/presets.go b/internal/config/presets.go
index b8c8b8b..2a2d635 100644
--- a/internal/config/presets.go
+++ b/internal/config/presets.go
@@ -68,6 +68,7 @@ var defaultK8sConfig k8sConfig = k8sConfig{
 			"cidrs":   "10.43.45.0/28",
 		},
 		"local-storage": {},
+		"network":       {},
 	},
 }
 
diff --git a/internal/providers/k8s_test.go b/internal/providers/k8s_test.go
index a546428..591543b 100644
--- a/internal/providers/k8s_test.go
+++ b/internal/providers/k8s_test.go
@@ -16,6 +16,7 @@ var defaultFeatureConfig = map[string]map[string]string{
 		"cidrs":   "10.43.45.1/32",
 	},
 	"local-storage": {},
+	"network":       {},
 }
 
 func TestNewK8s(t *testing.T) {
@@ -81,6 +82,7 @@ func TestK8sPrepareCommands(t *testing.T) {
 		"k8s set load-balancer.cidrs=10.43.45.1/32",
 		"k8s enable load-balancer",
 		"k8s enable local-storage",
+		"k8s enable network",
 		"k8s kubectl config view --raw",
 	}
 
@@ -120,6 +122,7 @@ func TestK8sPrepareCommandsAlreadyBootstrapped(t *testing.T) {
 		"k8s set load-balancer.cidrs=10.43.45.1/32",
 		"k8s enable load-balancer",
 		"k8s enable local-storage",
+		"k8s enable network",
 		"k8s kubectl config view --raw",
 	}
```
