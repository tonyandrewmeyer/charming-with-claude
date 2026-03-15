# fix: install `iptables` for k8s provider if not present (#57)

**Repository**: canonical/concierge
**Commit**: [00102fd0](https://github.com/canonical/canonical/concierge/commit/00102fd0d311cebf659d0a75c6200173d0ae43f4)
**Date**: 2025-05-08T07:46:26+02:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | edge-case |
| Severity | high |
| Fix Category | source-fix |

## Summary

Install iptables dependency required by k8s snap when not already present on the system

## Commit Message

The k8s snap relies on `iptables` being present on the system, which is
some cases is not true.

In this change, the k8s provider is updated to first check if the
iptables command is present, and install it if not.

In a change from the norm, iptables is not then removed, as currently we
don't track state and removing the package if it was previously
installed would be a bad outcome!

Fixes #56

## Changed Files

- M	internal/providers/k8s.go
- M	internal/providers/k8s_test.go
- M	internal/system/mock_system.go

## Diff

```diff
diff --git a/internal/providers/k8s.go b/internal/providers/k8s.go
index 6ae753d..52a5b03 100644
--- a/internal/providers/k8s.go
+++ b/internal/providers/k8s.go
@@ -7,6 +7,8 @@ import (
 	"strings"
 	"time"
 
+	"golang.org/x/sync/errgroup"
+
 	"github.com/jnsgruk/concierge/internal/config"
 	"github.com/jnsgruk/concierge/internal/packages"
 	"github.com/jnsgruk/concierge/internal/system"
@@ -34,6 +36,9 @@ func NewK8s(r system.Worker, config *config.Config) *K8s {
 		modelDefaults:        config.Providers.K8s.ModelDefaults,
 		bootstrapConstraints: config.Providers.K8s.BootstrapConstraints,
 		system:               r,
+		debs: []*packages.Deb{
+			{Name: "iptables"},
+		},
 		snaps: []*system.Snap{
 			{Name: "k8s", Channel: channel},
 			{Name: "kubectl", Channel: "stable"},
@@ -51,6 +56,7 @@ type K8s struct {
 	bootstrapConstraints map[string]string
 
 	system system.Worker
+	debs   []*packages.Deb
 	snaps  []*system.Snap
 }
 
@@ -125,10 +131,35 @@ func (k *K8s) Restore() error {
 
 // install ensures that K8s is installed.
 func (k *K8s) install() error {
+	var eg errgroup.Group
+
+	// Prepare/restore package handlers concurrently
+	debHandler := packages.NewDebHandler(k.system, k.debs)
 	snapHandler := packages.NewSnapHandler(k.system, k.snaps)
 
-	err := snapHandler.Prepare()
-	if err != nil {
+	eg.Go(func() error {
+		// In some cases, iptables is not present on the system. In those cases,
+		// make sure it's installed.
+		cmd := system.NewCommand("which", []string{"iptables"})
+		_, err := k.system.Run(cmd)
+		if err != nil {
+			err := debHandler.Prepare()
+			if err != nil {
+				return err
+			}
+		}
+		return nil
+	})
+
+	eg.Go(func() error {
+		err := snapHandler.Prepare()
+		if err != nil {
+			return err
+		}
+		return nil
+	})
+
+	if err := eg.Wait(); err != nil {
 		return err
 	}
 
diff --git a/internal/providers/k8s_test.go b/internal/providers/k8s_test.go
index 6ec5075..8f0ad07 100644
--- a/internal/providers/k8s_test.go
+++ b/internal/providers/k8s_test.go
@@ -61,6 +61,7 @@ func TestNewK8s(t *testing.T) {
 
 		// Remove the snaps so the rest of the object can be compared
 		ck8s.snaps = nil
+		ck8s.debs = nil
 		if !reflect.DeepEqual(tc.expected, ck8s) {
 			t.Fatalf("expected: %v, got: %v", tc.expected, ck8s)
 		}
@@ -73,6 +74,9 @@ func TestK8sPrepareCommands(t *testing.T) {
 	config.Providers.K8s.Features = defaultFeatureConfig
 
 	expectedCommands := []string{
+		"which iptables",
+		"apt-get update",
+		"apt-get install -y iptables",
 		fmt.Sprintf("snap install k8s --channel %s", defaultK8sChannel),
 		"snap install kubectl --channel stable",
 		"k8s bootstrap",
@@ -92,6 +96,7 @@ func TestK8sPrepareCommands(t *testing.T) {
 
 	system := system.NewMockSystem()
 	system.MockCommandReturn("k8s status", []byte("Error: The node is not part of a Kubernetes cluster."), fmt.Errorf("command error"))
+	system.MockCommandReturn("which iptables", []byte(""), fmt.Errorf("command error"))
 
 	ck8s := NewK8s(system, config)
 	ck8s.Prepare()
@@ -108,12 +113,13 @@ func TestK8sPrepareCommands(t *testing.T) {
 	}
 }
 
-func TestK8sPrepareCommandsAlreadyBootstrapped(t *testing.T) {
+func TestK8sPrepareCommandsAlreadyBootstrappedIptablesInstalled(t *testing.T) {
 	config := &config.Config{}
 	config.Providers.K8s.Channel = ""
 	config.Providers.K8s.Features = defaultFeatureConfig
 
 	expectedCommands := []string{
+		"which iptables",
 		fmt.Sprintf("snap install k8s --channel %s", defaultK8sChannel),
 		"snap install kubectl --channel stable",
 		"k8s status --wait-ready",
@@ -131,6 +137,7 @@ func TestK8sPrepareCommandsAlreadyBootstrapped(t *testing.T) {
 	}
 
 	system := system.NewMockSystem()
+	system.MockCommandReturn("which iptables", []byte("/usr/sbin/iptables"), nil)
 	ck8s := NewK8s(system, config)
 	ck8s.Prepare()
 
diff --git a/internal/system/mock_system.go b/internal/system/mock_system.go
index 5041eb4..3770c23 100644
--- a/internal/system/mock_system.go
+++ b/internal/system/mock_system.go
@@ -4,6 +4,7 @@ import (
 	"fmt"
 	"os"
 	"os/user"
+	"sync"
 	"time"
 )
 
@@ -34,6 +35,9 @@ type MockSystem struct {
 	mockReturns      map[string]MockCommandReturn
 	mockSnapInfo     map[string]*SnapInfo
 	mockSnapChannels map[string][]string
+
+	// Used to guard access to the ExecutedCommands list
+	cmdMutex sync.Mutex
 }
 
 // MockCommandReturn sets a static return value representing command combined output,
@@ -73,6 +77,7 @@ func (r *MockSystem) User() *user.User {
 
 // Run executes the command, returning the stdout/stderr where appropriate.
 func (r *MockSystem) Run(c *Command) ([]byte, error) {
+	r.cmdMutex.Lock()
 	// Prevent the path of the test machine interfering with the test results.
 	path := os.Getenv("PATH")
 	defer os.Setenv("PATH", path)
@@ -81,6 +86,7 @@ func (r *MockSystem) Run(c *Command) ([]byte, error) {
 	cmd := c.CommandString()
 
 	r.ExecutedCommands = append(r.ExecutedCommands, cmd)
+	r.cmdMutex.Unlock()
 
 	val, ok := r.mockReturns[cmd]
 	if ok {
```
