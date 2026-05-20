# fix: retry bootstrap check on on controllers when there are errors

**Repository**: canonical/concierge
**Commit**: [1668e372](https://github.com/canonical/canonical/concierge/commit/1668e372c9f63bc1a57113af512cb000772569f6)
**Date**: 2025-02-24T12:06:28+00:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | error-handling |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Add retry with backoff for juju controller status checks to handle transient API failures

## Commit Message

At the moment, when concierge checks for a bootstrapped controller, if
the command fails the check is considered a failure, and thus that the
controller doesn't exist.

In some cases, that is correct, and we can tell that from the error
message. In other cases, the check fails because the controller fails
to respond.

This commit introduces a retry with backoff on that check.

## Changed Files

- M	internal/juju/juju.go

## Diff

```diff
diff --git a/internal/juju/juju.go b/internal/juju/juju.go
index 492d3d4..49dc341 100644
--- a/internal/juju/juju.go
+++ b/internal/juju/juju.go
@@ -1,6 +1,7 @@
 package juju
 
 import (
+	"context"
 	"fmt"
 	"log/slog"
 	"path"
@@ -12,6 +13,7 @@ import (
 	"github.com/jnsgruk/concierge/internal/packages"
 	"github.com/jnsgruk/concierge/internal/providers"
 	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/sethvargo/go-retry"
 	"golang.org/x/sync/errgroup"
 	"gopkg.in/yaml.v3"
 )
@@ -264,14 +266,27 @@ func (j *JujuHandler) checkBootstrapped(controllerName string) (bool, error) {
 	user := j.system.User().Username
 	cmd := system.NewCommandAs(user, "", "juju", []string{"show-controller", controllerName})
 
-	result, err := j.system.Run(cmd)
-	if err != nil && strings.Contains(string(result), "not found") {
-		return false, nil
-	} else if err != nil {
-		return false, err
-	}
+	// Configure a back-off for retrying the assessment of controller status.
+	backoff := retry.WithMaxRetries(10, retry.NewExponential(1*time.Second))
+
+	// Run a function, with retries/backoff, to assess whether the controller exists.
+	// This retry works around an issue where a given controller may not respond, causing the
+	// tool to conclude that the controller doesn't exist, rather than the controller simply
+	// not responding.
+	return retry.DoValue(context.Background(), backoff, func(ctx context.Context) (bool, error) {
+		output, err := j.system.Run(cmd)
+		if err != nil {
+			// If the error message on checking contains "not found" then the controller
+			// is not actually there, so don't retry the check.
+			if strings.Contains(string(output), "not found") {
+				return false, nil
+			}
+			// Otherwise, retry the check for a bootstrapped controller.
+			return false, retry.RetryableError(err)
+		}
 
-	return true, nil
+		return true, nil
+	})
 }
 
 // sortedKeys gets an alphabetically sorted list of keys from a map.
```
