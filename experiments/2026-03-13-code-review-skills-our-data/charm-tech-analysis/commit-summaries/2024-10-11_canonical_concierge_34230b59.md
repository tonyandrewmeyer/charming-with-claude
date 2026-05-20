# fix: construct `Manager` correctly in `restore` subcommand

**Repository**: canonical/concierge
**Commit**: [34230b59](https://github.com/canonical/canonical/concierge/commit/34230b5927bcff28d7013b732897707e6e7703f2)
**Date**: 2024-10-11T16:10:26+01:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | cli |
| Bug Type | logic-error |
| Severity | high |
| Fix Category | source-fix |

## Summary

Initialize Manager with proper config in restore command instead of using empty struct

## Changed Files

- M	cmd/restore.go

## Diff

```diff
diff --git a/cmd/restore.go b/cmd/restore.go
index 401534b..4880d1c 100644
--- a/cmd/restore.go
+++ b/cmd/restore.go
@@ -1,7 +1,10 @@
 package cmd
 
 import (
+	"fmt"
+
 	"github.com/jnsgruk/concierge/internal/concierge"
+	"github.com/jnsgruk/concierge/internal/config"
 	"github.com/spf13/cobra"
 )
 
@@ -22,7 +25,14 @@ var restoreCmd = &cobra.Command{
 		setupLogging(verbose)
 	},
 	RunE: func(cmd *cobra.Command, args []string) error {
-		mgr := &concierge.Manager{}
+		flags := cmd.Flags()
+
+		conf, err := config.NewConfig(cmd, flags)
+		if err != nil {
+			return fmt.Errorf("failed to configure concierge: %w", err)
+		}
+
+		mgr := concierge.NewManager(conf)
 		return mgr.Restore()
 	},
 }
```
