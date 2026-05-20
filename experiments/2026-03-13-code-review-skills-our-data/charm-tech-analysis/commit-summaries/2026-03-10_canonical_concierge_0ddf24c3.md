# fix: only remove /run/containerd if we need to bootstrap k8s (#161)

**Repository**: canonical/concierge
**Commit**: [0ddf24c3](https://github.com/canonical/canonical/concierge/commit/0ddf24c3f7ba9d35ea0364a803f0c3b7aa092cbd)
**Date**: 2026-03-10T13:02:55+13:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | state-management |
| Severity | high |
| Fix Category | source-fix |

## Summary

Prevent removing /run/containerd when k8s is already bootstrapped, preserving idempotency

## Commit Message

If there is an existing `/run/containerd` from something like Docker
(like in the GitHub runner) then we need to remove that before we try to
install and bootstrap k8s ourselves.

*However*, if it exists because we already have a bootstrapped k8s, then
we should leave it alone. Concierge should be fairly idempotent, and
certainly should not break k8s if run twice.

## Changed Files

- M	internal/providers/k8s.go
- M	internal/providers/k8s_test.go
- A	tests/k8s-pre-bootstrapped/concierge.yaml
- A	tests/k8s-pre-bootstrapped/task.yaml

## Diff

```diff
diff --git a/internal/providers/k8s.go b/internal/providers/k8s.go
index bf4aac9..686d3eb 100644
--- a/internal/providers/k8s.go
+++ b/internal/providers/k8s.go
@@ -180,9 +180,8 @@ func (k *K8s) install() error {
 
 // init ensures that K8s is installed, minimally configured, and ready.
 func (k *K8s) init() error {
-	k.handleExistingContainerd()
-
 	if k.needsBootstrap() {
+		k.handleExistingContainerd()
 		cmd := system.NewCommand("k8s", []string{"bootstrap"})
 		_, err := system.RunWithRetries(k.system, cmd, 5*time.Minute)
 		if err != nil {
diff --git a/internal/providers/k8s_test.go b/internal/providers/k8s_test.go
index 33a90df..64f8335 100644
--- a/internal/providers/k8s_test.go
+++ b/internal/providers/k8s_test.go
@@ -126,7 +126,6 @@ func TestK8sPrepareCommandsAlreadyBootstrappedIptablesInstalled(t *testing.T) {
 		"which iptables",
 		fmt.Sprintf("snap install k8s --channel %s", defaultK8sChannel),
 		"snap install kubectl --channel stable",
-		"systemctl is-active containerd.service",
 		"k8s status",
 		"k8s status --wait-ready --timeout 270s",
 		"k8s set load-balancer.l2-mode=true",
diff --git a/tests/k8s-pre-bootstrapped/concierge.yaml b/tests/k8s-pre-bootstrapped/concierge.yaml
new file mode 100644
index 0000000..0af0f8e
--- /dev/null
+++ b/tests/k8s-pre-bootstrapped/concierge.yaml
@@ -0,0 +1,8 @@
+juju:
+  enable: false
+providers:
+  k8s:
+    enable: true
+    channel: 1.32-classic/stable
+    features:
+      local-storage:
diff --git a/tests/k8s-pre-bootstrapped/task.yaml b/tests/k8s-pre-bootstrapped/task.yaml
new file mode 100644
index 0000000..5a62cb6
--- /dev/null
+++ b/tests/k8s-pre-bootstrapped/task.yaml
@@ -0,0 +1,32 @@
+summary: Run concierge prepare on a K8s cluster that is already bootstrapped
+
+systems:
+  - ubuntu-24.04
+
+execute: |
+  pushd "${SPREAD_PATH}/${SPREAD_TASK}"
+
+  # Remove Docker/containerd from the runner so k8s can bootstrap cleanly.
+  sudo apt-get remove -y docker-ce docker-ce-cli containerd.io
+  sudo rm -rf /run/containerd
+
+  # Install and bootstrap k8s before concierge runs.
+  sudo snap install k8s --channel 1.32-classic/stable --classic
+  sudo k8s bootstrap
+  sudo k8s status --wait-ready --timeout 120s
+
+  # Now run concierge prepare against the already-bootstrapped cluster.
+  "$SPREAD_PATH"/concierge --trace prepare --extra-snaps="yq"
+
+  # Verify the cluster is still healthy after concierge prepare.
+  sudo k8s status --wait-ready --timeout 120s
+
+  sudo k8s status --output-format yaml | yq '.dns.enabled' | MATCH true
+
+  kubectl config current-context | MATCH "k8s"
+
+restore: |
+  if [[ -z "${CI:-}" ]]; then
+    "$SPREAD_PATH"/concierge --trace restore
+    sudo snap remove k8s --purge
+  fi
```
