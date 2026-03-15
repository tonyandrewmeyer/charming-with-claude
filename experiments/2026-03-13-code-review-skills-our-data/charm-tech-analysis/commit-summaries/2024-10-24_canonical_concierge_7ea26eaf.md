# fix: add cli flag to override Canonical K8s channel

**Repository**: canonical/concierge
**Commit**: [7ea26eaf](https://github.com/canonical/canonical/concierge/commit/7ea26eafa9181a78dfe1c10bb93357c28b3598b1)
**Date**: 2024-10-24T09:07:13+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | cli |
| Bug Type | edge-case |
| Severity | low |
| Fix Category | source-fix |

## Summary

Add missing CLI flag to allow overriding the Canonical K8s snap channel

## Changed Files

- M	cmd/prepare.go

## Diff

```diff
diff --git a/cmd/prepare.go b/cmd/prepare.go
index 6bf7af3..9c26302 100644
--- a/cmd/prepare.go
+++ b/cmd/prepare.go
@@ -62,6 +62,7 @@ More information at https://github.com/jnsgruk/concierge.
 	flags.StringP("config", "c", "", "path to a specific config file to use")
 	flags.StringP("preset", "p", "", "config preset to use (k8s | machine | dev)")
 	flags.String("juju-channel", "", "override the snap channel for juju")
+	flags.String("canonical-k8s-channel", "", "override snap channel for Canonical K8s")
 	flags.String("microk8s-channel", "", "override snap channel for microk8s")
 	flags.String("lxd-channel", "", "override snap channel for lxd")
 	flags.String("charmcraft-channel", "", "override snap channel for charmcraft")
```
