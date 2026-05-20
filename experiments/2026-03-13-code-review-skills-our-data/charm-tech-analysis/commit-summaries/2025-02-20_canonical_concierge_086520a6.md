# fix: ensure disabled juju warning is shown

**Repository**: canonical/concierge
**Commit**: [086520a6](https://github.com/canonical/canonical/concierge/commit/086520a698fd165cae5277cc9b4884ad61ffa2d0)
**Date**: 2025-02-20T13:48:38+00:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | config |
| Bug Type | logic-error |
| Severity | low |
| Fix Category | source-fix |

## Summary

Reference correct config field so disabled-juju warning is actually displayed

## Changed Files

- M	internal/concierge/plan.go

## Diff

```diff
diff --git a/internal/concierge/plan.go b/internal/concierge/plan.go
index cdb3ac0..45d142e 100644
--- a/internal/concierge/plan.go
+++ b/internal/concierge/plan.go
@@ -57,7 +57,7 @@ func NewPlan(cfg *config.Config, worker system.Worker) *Plan {
 
 			// Warn if the configuration specifies to bootstrap the provider, but the config or
 			// overrides disable Juju.
-			if plan.config.Juju.Disable && p.Bootstrap() {
+			if cfg.Overrides.DisableJuju && p.Bootstrap() {
 				slog.Warn("provider will not be bootstrapped because juju is disabled", "provider", providerName)
 			}
 		}
```
