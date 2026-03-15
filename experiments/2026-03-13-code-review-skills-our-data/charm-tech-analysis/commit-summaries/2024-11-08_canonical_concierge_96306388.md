# fix: use 1.31-classic/candidate channel by default for k8s

**Repository**: canonical/concierge
**Commit**: [96306388](https://github.com/canonical/canonical/concierge/commit/963063881b90158f12ff049b279109f2ecd06d06)
**Date**: 2024-11-08T10:04:19+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | config |
| Bug Type | config-parsing |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Correct default k8s snap channel from 1.31/candidate to 1.31-classic/candidate

## Changed Files

- M	README.md
- M	internal/providers/k8s.go
- M	internal/providers/k8s_test.go
- M	tests/provider-k8s/concierge.yaml
- M	tests/provider-k8s/task.yaml

## Diff

```diff
diff --git a/README.md b/README.md
index 0c360e4..b2209d2 100644
--- a/README.md
+++ b/README.md
@@ -308,7 +308,7 @@ providers:
   k8s:
     enable: true
     bootstrap: true
-    channel: 1.31/candidate
+    channel: 1.31-classic/candidate
     features:
       local-storage:
       load-balancer:
diff --git a/internal/providers/k8s.go b/internal/providers/k8s.go
index 9d8e969..d68960e 100644
--- a/internal/providers/k8s.go
+++ b/internal/providers/k8s.go
@@ -12,7 +12,7 @@ import (
 )
 
 // Default channel from which K8s is installed.
-const defaultK8sChannel = "1.31/candidate"
+const defaultK8sChannel = "1.31-classic/candidate"
 
 // NewK8s constructs a new K8s provider instance.
 func NewK8s(r system.Worker, config *config.Config) *K8s {
diff --git a/internal/providers/k8s_test.go b/internal/providers/k8s_test.go
index a9f1adf..5d08dd6 100644
--- a/internal/providers/k8s_test.go
+++ b/internal/providers/k8s_test.go
@@ -37,7 +37,7 @@ func TestNewK8s(t *testing.T) {
 	tests := []test{
 		{
 			config:   noOverrides,
-			expected: &K8s{Channel: "1.31/candidate", system: system},
+			expected: &K8s{Channel: "1.31-classic/candidate", system: system},
 		},
 		{
 			config:   channelInConfig,
@@ -71,7 +71,7 @@ func TestK8sPrepareCommands(t *testing.T) {
 	config.Providers.K8s.Features = defaultFeatureConfig
 
 	expectedCommands := []string{
-		"snap install k8s --channel 1.31/candidate",
+		"snap install k8s --channel 1.31-classic/candidate",
 		"snap install kubectl --channel stable",
 		"k8s bootstrap",
 		"k8s status --wait-ready",
diff --git a/tests/provider-k8s/concierge.yaml b/tests/provider-k8s/concierge.yaml
index b12d875..b9c72db 100644
--- a/tests/provider-k8s/concierge.yaml
+++ b/tests/provider-k8s/concierge.yaml
@@ -2,7 +2,7 @@ providers:
   k8s:
     enable: true
     bootstrap: true
-    channel: 1.31/candidate
+    channel: 1.31-classic/candidate
     features:
       local-storage:
       load-balancer:
diff --git a/tests/provider-k8s/task.yaml b/tests/provider-k8s/task.yaml
index 4602f5e..ce9d60e 100644
--- a/tests/provider-k8s/task.yaml
+++ b/tests/provider-k8s/task.yaml
@@ -9,7 +9,7 @@ execute: |
 
   list="$(snap list k8s)"
   echo $list | MATCH k8s
-  echo $list | MATCH 1.31/candidate
+  echo $list | MATCH 1.31-classic/candidate
 
   list="$(snap list)"
   echo $list | MATCH juju
```
