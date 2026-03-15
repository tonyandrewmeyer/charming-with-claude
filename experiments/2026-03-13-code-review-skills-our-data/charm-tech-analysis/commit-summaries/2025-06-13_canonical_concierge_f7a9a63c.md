# fix: look for more a specific error in checkBootstrapped

**Repository**: canonical/concierge
**Commit**: [f7a9a63c](https://github.com/canonical/canonical/concierge/commit/f7a9a63cd62bdb36849caa5a54d9a64011f37cf1)
**Date**: 2025-06-13T17:05:48+12:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | error-handling |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Tighten error string matching in checkBootstrapped to avoid misidentifying transient errors as missing controllers

## Commit Message

Testing if the output contains just "not found" is too loose, as some
intermittent errors include phrases like "pod not found", for example:

Command: /snap/bin/juju show-controller concierge-microk8s
Output:
{}
ERROR opening API connection: starting proxy for api connection: connecting k8s proxy: forwarding ports: error upgrading connection: unable to upgrade connection: pod not found ("controller-0_controller-concierge-microk8s")

So look for the specific "controller <name> not found" error.

This bug was causing concierge to think the controller wasn't there,
and falling through to do the bootstrap, which then failed with
"controller ... already exists" and kept retrying.

Fixes #64

## Changed Files

- M	internal/juju/juju.go
- M	internal/juju/juju_test.go

## Diff

```diff
diff --git a/internal/juju/juju.go b/internal/juju/juju.go
index c58f067..437dbb2 100644
--- a/internal/juju/juju.go
+++ b/internal/juju/juju.go
@@ -276,9 +276,13 @@ func (j *JujuHandler) checkBootstrapped(controllerName string) (bool, error) {
 	return retry.DoValue(context.Background(), backoff, func(ctx context.Context) (bool, error) {
 		output, err := j.system.Run(cmd)
 		if err != nil {
-			// If the error message on checking contains "not found" then the controller
-			// is not actually there, so don't retry the check.
-			if strings.Contains(string(output), "not found") {
+			// If the error contains "controller <name> not found", it's not actually an error,
+			// so don't retry the check. It's important to not check just for "not found", as
+			// some intermittent errors include phrases like "pod not found", for example:
+			//
+			// ERROR opening API connection: ... unable to upgrade connection: pod not found ...
+			controllerNotFound := "controller " + controllerName + " not found"
+			if strings.Contains(string(output), controllerNotFound) {
 				return false, nil
 			}
 			// Otherwise, retry the check for a bootstrapped controller.
diff --git a/internal/juju/juju_test.go b/internal/juju/juju_test.go
index c6129e3..7fd276e 100644
--- a/internal/juju/juju_test.go
+++ b/internal/juju/juju_test.go
@@ -26,9 +26,21 @@ func setupHandlerWithPreset(preset string) (*system.MockSystem, *JujuHandler, er
 	var provider providers.Provider
 
 	system := system.NewMockSystem()
-	system.MockCommandReturn("sudo -u test-user juju show-controller concierge-lxd", []byte("not found"), fmt.Errorf("Test error"))
-	system.MockCommandReturn("sudo -u test-user juju show-controller concierge-microk8s", []byte("not found"), fmt.Errorf("Test error"))
-	system.MockCommandReturn("sudo -u test-user juju show-controller concierge-k8s", []byte("not found"), fmt.Errorf("Test error"))
+	system.MockCommandReturn(
+		"sudo -u test-user juju show-controller concierge-lxd",
+		[]byte("ERROR controller concierge-lxd not found"),
+		fmt.Errorf("Test error"),
+	)
+	system.MockCommandReturn(
+		"sudo -u test-user juju show-controller concierge-microk8s",
+		[]byte("ERROR controller concierge-microk8s not found"),
+		fmt.Errorf("Test error"),
+	)
+	system.MockCommandReturn(
+		"sudo -u test-user juju show-controller concierge-k8s",
+		[]byte("ERROR controller concierge-k8s not found"),
+		fmt.Errorf("Test error"),
+	)
 
 	cfg, err = config.Preset(preset)
 	if err != nil {
@@ -68,6 +80,7 @@ func setupHandlerWithGoogleProvider() (*system.MockSystem, *JujuHandler, error)
 	handler := NewJujuHandler(cfg, system, []providers.Provider{provider})
 	return system, handler, nil
 }
+
 func TestJujuHandlerCommandsPresets(t *testing.T) {
 	type test struct {
 		preset           string
```
