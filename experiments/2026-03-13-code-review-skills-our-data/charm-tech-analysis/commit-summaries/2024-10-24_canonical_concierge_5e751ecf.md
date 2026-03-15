# fix: add retry to snapd client requests

**Repository**: canonical/concierge
**Commit**: [5e751ecf](https://github.com/canonical/canonical/concierge/commit/5e751ecf3e9d47a9303402718af433aa1802b9e1)
**Date**: 2024-10-24T09:51:56+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | error-handling |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Add exponential backoff retry to snapd client requests to handle 'too many requests' errors

## Commit Message

In the spread tests, occasionally a test will fail due to the
snapd client responding with "too many requests". This change
introduces the ability for snapd client lookups to be retried
with an exponential backoff pattern to avoid those failures.

## Changed Files

- M	internal/packages/snap.go

## Diff

```diff
diff --git a/internal/packages/snap.go b/internal/packages/snap.go
index bcf8c4c..425c243 100644
--- a/internal/packages/snap.go
+++ b/internal/packages/snap.go
@@ -1,10 +1,13 @@
 package packages
 
 import (
+	"context"
 	"fmt"
 	"log/slog"
 	"strings"
+	"time"
 
+	retry "github.com/sethvargo/go-retry"
 	"github.com/snapcore/snapd/client"
 )
 
@@ -62,8 +65,16 @@ func (s *Snap) SetChannel(c string) { s.channel = c }
 func (s *Snap) Installed() bool {
 	slog.Debug("Querying snap install status", "snap", s.name)
 
-	snap, _, err := s.client.Snap(s.name)
-	if err != nil {
+	snap, err := s.withRetry(func(ctx context.Context) (*client.Snap, error) {
+		snap, _, err := s.client.Snap(s.name)
+		if err != nil && strings.Contains(err.Error(), "snap not installed") {
+			return snap, nil
+		} else if err != nil {
+			return nil, retry.RetryableError(err)
+		}
+		return snap, nil
+	})
+	if err != nil || snap == nil {
 		return false
 	}
 
@@ -75,7 +86,13 @@ func (s *Snap) Installed() bool {
 func (s *Snap) Classic() (bool, error) {
 	slog.Debug("Querying snap confinement", "snap", s.name)
 
-	snap, _, err := s.client.FindOne(s.name)
+	snap, err := s.withRetry(func(ctx context.Context) (*client.Snap, error) {
+		snap, _, err := s.client.FindOne(s.name)
+		if err != nil {
+			return nil, retry.RetryableError(err)
+		}
+		return snap, nil
+	})
 	if err != nil {
 		return false, fmt.Errorf("failed to find snap: %w", err)
 	}
@@ -92,7 +109,13 @@ func (s *Snap) Classic() (bool, error) {
 func (s *Snap) Tracking() (string, error) {
 	slog.Debug("Querying snap channel tracking", "snap", s.name)
 
-	snap, _, err := s.client.Snap(s.name)
+	snap, err := s.withRetry(func(ctx context.Context) (*client.Snap, error) {
+		snap, _, err := s.client.Snap(s.name)
+		if err != nil {
+			return nil, retry.RetryableError(err)
+		}
+		return snap, nil
+	})
 	if err != nil {
 		return "", fmt.Errorf("failed to find snap: %w", err)
 	}
@@ -103,3 +126,10 @@ func (s *Snap) Tracking() (string, error) {
 		return "", fmt.Errorf("snap '%s' is not installed", s.name)
 	}
 }
+
+func (s *Snap) withRetry(f func(ctx context.Context) (*client.Snap, error)) (*client.Snap, error) {
+	backoff := retry.NewExponential(1 * time.Second)
+	backoff = retry.WithMaxRetries(10, backoff)
+	ctx := context.Background()
+	return retry.DoValue(ctx, backoff, f)
+}
```
