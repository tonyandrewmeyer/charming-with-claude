# fix: Avoid waiting indefinitely for providers. (#74)

**Repository**: canonical/concierge
**Commit**: [bce51017](https://github.com/canonical/canonical/concierge/commit/bce510174b10caf090d63a63527957bb7f2dae48)
**Date**: 2025-07-09T23:10:06+02:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | resource-leak |
| Severity | high |
| Fix Category | source-fix |

## Summary

Add timeouts to provider wait-ready commands to prevent indefinite hangs

## Commit Message

While there is code to retry commands up until a upper time limit, it
does not catch the condition where the executed command never returns.

Provider initialization may have external dependencies such as image
registries, and is subject to quotas, network connectivity among other
things.

Use a timeout when waiting for a provider, with a value lower than the
upper retry time limit.

Signed-off-by: Frode Nordahl <fnordahl@ubuntu.com>

## Changed Files

- M	internal/providers/k8s.go
- M	internal/providers/k8s_test.go
- M	internal/providers/lxd.go
- M	internal/providers/lxd_test.go
- M	internal/providers/microk8s.go
- M	internal/providers/microk8s_test.go

## Diff

```diff
diff --git a/internal/providers/k8s.go b/internal/providers/k8s.go
index 04fea75..d0ca218 100644
--- a/internal/providers/k8s.go
+++ b/internal/providers/k8s.go
@@ -176,7 +176,7 @@ func (k *K8s) init() error {
 		}
 	}
 
-	cmd := system.NewCommand("k8s", []string{"status", "--wait-ready"})
+	cmd := system.NewCommand("k8s", []string{"status", "--wait-ready", "--timeout", "270s"})
 	_, err := k.system.RunWithRetries(cmd, (5 * time.Minute))
 
 	return err
diff --git a/internal/providers/k8s_test.go b/internal/providers/k8s_test.go
index b6bc4e3..338e66a 100644
--- a/internal/providers/k8s_test.go
+++ b/internal/providers/k8s_test.go
@@ -80,7 +80,7 @@ func TestK8sPrepareCommands(t *testing.T) {
 		fmt.Sprintf("snap install k8s --channel %s", defaultK8sChannel),
 		"snap install kubectl --channel stable",
 		"k8s bootstrap",
-		"k8s status --wait-ready",
+		"k8s status --wait-ready --timeout 270s",
 		"k8s set load-balancer.l2-mode=true",
 		"k8s status",
 		"k8s set load-balancer.cidrs=10.43.45.1/32",
@@ -122,7 +122,7 @@ func TestK8sPrepareCommandsAlreadyBootstrappedIptablesInstalled(t *testing.T) {
 		"which iptables",
 		fmt.Sprintf("snap install k8s --channel %s", defaultK8sChannel),
 		"snap install kubectl --channel stable",
-		"k8s status --wait-ready",
+		"k8s status --wait-ready --timeout 270s",
 		"k8s set load-balancer.l2-mode=true",
 		"k8s status",
 		"k8s set load-balancer.cidrs=10.43.45.1/32",
diff --git a/internal/providers/lxd.go b/internal/providers/lxd.go
index d5d6d70..05dcbd7 100644
--- a/internal/providers/lxd.go
+++ b/internal/providers/lxd.go
@@ -134,7 +134,7 @@ func (l *LXD) install() error {
 // init ensures that LXD is minimally configured, and ready.
 func (l *LXD) init() error {
 	return l.system.RunMany(
-		system.NewCommand("lxd", []string{"waitready"}),
+		system.NewCommand("lxd", []string{"waitready", "--timeout", "270"}),
 		system.NewCommand("lxd", []string{"init", "--minimal"}),
 		system.NewCommand("lxc", []string{"network", "set", "lxdbr0", "ipv6.address", "none"}),
 	)
diff --git a/internal/providers/lxd_test.go b/internal/providers/lxd_test.go
index fcbb5ff..7ca2630 100644
--- a/internal/providers/lxd_test.go
+++ b/internal/providers/lxd_test.go
@@ -51,7 +51,7 @@ func TestLXDPrepareCommands(t *testing.T) {
 
 	expected := []string{
 		"snap install lxd",
-		"lxd waitready",
+		"lxd waitready --timeout 270",
 		"lxd init --minimal",
 		"lxc network set lxdbr0 ipv6.address none",
 		"chmod a+wr /var/snap/lxd/common/lxd/unix.socket",
@@ -76,7 +76,7 @@ func TestLXDPrepareCommandsLXDAlreadyInstalled(t *testing.T) {
 		"snap stop lxd",
 		"snap refresh lxd",
 		"snap start lxd",
-		"lxd waitready",
+		"lxd waitready --timeout 270",
 		"lxd init --minimal",
 		"lxc network set lxdbr0 ipv6.address none",
 		"chmod a+wr /var/snap/lxd/common/lxd/unix.socket",
diff --git a/internal/providers/microk8s.go b/internal/providers/microk8s.go
index 6595fbb..0bd53fb 100644
--- a/internal/providers/microk8s.go
+++ b/internal/providers/microk8s.go
@@ -149,7 +149,7 @@ func (m *MicroK8s) install() error {
 
 // init ensures that MicroK8s is installed, minimally configured, and ready.
 func (m *MicroK8s) init() error {
-	cmd := system.NewCommand("microk8s", []string{"status", "--wait-ready"})
+	cmd := system.NewCommand("microk8s", []string{"status", "--wait-ready", "--timeout", "270"})
 	_, err := m.system.RunWithRetries(cmd, (5 * time.Minute))
 
 	return err
diff --git a/internal/providers/microk8s_test.go b/internal/providers/microk8s_test.go
index 7074c96..7338fe1 100644
--- a/internal/providers/microk8s_test.go
+++ b/internal/providers/microk8s_test.go
@@ -93,7 +93,7 @@ func TestMicroK8sPrepareCommands(t *testing.T) {
 	expectedCommands := []string{
 		"snap install microk8s --channel 1.31-strict/stable",
 		"snap install kubectl --channel stable",
-		"microk8s status --wait-ready",
+		"microk8s status --wait-ready --timeout 270",
 		"microk8s enable hostpath-storage",
 		"microk8s enable dns",
 		"microk8s enable rbac",
```
