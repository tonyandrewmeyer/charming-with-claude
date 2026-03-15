# fix: update import path to make it importable (#58)

**Repository**: canonical/concierge
**Commit**: [a8143a89](https://github.com/canonical/canonical/concierge/commit/a8143a89a4c2168a153a9260f18f455b966ad490)
**Date**: 2025-05-08T11:11:07+02:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | ci-build |
| Bug Type | config-parsing |
| Severity | medium |
| Fix Category | build-fix |

## Summary

Update Go module path from jnsgruk/concierge to canonical/concierge so the package is go-installable

## Commit Message

v1.0.0 and v1.0.1 are not `go install`able, due to the go.mod and import
paths not matching the repo, for example:

```
$ go install github.com/canonical/concierge@v1.0.0
go: downloading github.com/canonical/concierge v1.0.0
go: github.com/canonical/concierge@v1.0.0: version constraints conflict:
	github.com/canonical/concierge@v1.0.0: parsing go.mod:
	module declares its path as: github.com/jnsgruk/concierge
	        but was required as: github.com/canonical/concierge
```

This should fix that.

## Changed Files

- M	.goreleaser.yaml
- M	README.md
- M	cmd/prepare.go
- M	cmd/restore.go
- M	cmd/status.go
- M	go.mod
- M	internal/concierge/manager.go
- M	internal/concierge/plan.go
- M	internal/concierge/plan_test.go
- M	internal/concierge/plan_validators_test.go
- M	internal/juju/juju.go
- M	internal/juju/juju_test.go
- M	internal/packages/deb_handler.go
- M	internal/packages/deb_handler_test.go
- M	internal/packages/snap_handler.go
- M	internal/packages/snap_handler_test.go
- M	internal/providers/google.go
- M	internal/providers/google_test.go
- M	internal/providers/k8s.go
- M	internal/providers/k8s_test.go
- M	internal/providers/lxd.go
- M	internal/providers/lxd_test.go
- M	internal/providers/microk8s.go
- M	internal/providers/microk8s_test.go
- M	internal/providers/providers.go
- M	main.go

## Diff

```diff
diff --git a/.goreleaser.yaml b/.goreleaser.yaml
index c25ef00..f67ee56 100644
--- a/.goreleaser.yaml
+++ b/.goreleaser.yaml
@@ -15,7 +15,7 @@ builds:
       - amd64
       - arm64
     ldflags:
-      - -X github.com/jnsgruk/concierge/cmd.version={{ .Version }} -X github.com/jnsgruk/concierge/cmd.commit={{ .Commit }}
+      - -X github.com/canonical/concierge/cmd.version={{ .Version }} -X github.com/canonical/concierge/cmd.commit={{ .Commit }}
 archives:
   - builds:
       - default
@@ -48,7 +48,7 @@ snapcrafts:
       Each of the override flags has an environment variable equivalent, such as
       'CONCIERGE_JUJU_CHANNEL'.
 
-      More information at https://github.com/jnsgruk/concierge.
+      More information at https://github.com/canonical/concierge.
     extra_files:
       - source: .github/concierge.png
         destination: concierge.png
diff --git a/README.md b/README.md
index 6966f72..26fd47a 100644
--- a/README.md
+++ b/README.md
@@ -5,7 +5,7 @@
 <h1 align="center">concierge</h1>
 <p align="center">
   <a href="https://snapcraft.io/concierge"><img src="https://snapcraft.io/concierge/badge.svg" alt="Snap Status"></a>
-  <a href="https://github.com/jnsgruk/concierge/actions/workflows/release.yaml"><img src="https://github.com/jnsgruk/concierge/actions/workflows/release.yaml/badge.svg"></a>
+  <a href="https://github.com/canonical/concierge/actions/workflows/release.yaml"><img src="https://github.com/canonical/concierge/actions/workflows/release.yaml/badge.svg"></a>
 </p>
 
 `concierge` is an opinionated utility for provisioning charm development and testing machines.
@@ -35,13 +35,13 @@ sudo snap install --classic concierge
 Or, you can install `concierge` with the `go install` command:
 
 ```shell
-go install github.com/jnsgruk/concierge@latest
+go install github.com/canonical/concierge@latest
 ```
 
 Or you can clone, build and run like so:
 
 ```shell
-git clone https://github.com/jnsgruk/concierge
+git clone https://github.com/canonical/concierge
 cd concierge
 go build
 sudo ./concierge -h
@@ -363,7 +363,7 @@ You can get started by just using Go, or with `goreleaser`:
 
 ```shell
 # Clone the repository
-git clone https://github.com/jnsgruk/concierge
+git clone https://github.com/canonical/concierge
 cd concierge
 
 # Build/run with Go
diff --git a/cmd/prepare.go b/cmd/prepare.go
index 5dc4ce0..898dc7b 100644
--- a/cmd/prepare.go
+++ b/cmd/prepare.go
@@ -3,8 +3,8 @@ package cmd
 import (
 	"fmt"
 
-	"github.com/jnsgruk/concierge/internal/concierge"
-	"github.com/jnsgruk/concierge/internal/config"
+	"github.com/canonical/concierge/internal/concierge"
+	"github.com/canonical/concierge/internal/config"
 	"github.com/spf13/cobra"
 )
 
@@ -25,7 +25,7 @@ Some aspects of presets and config files can be overridden using flags such as '
 Each of the override flags has an environment variable equivalent, 
 such as 'CONCIERGE_JUJU_CHANNEL'.
 
-More information at https://github.com/jnsgruk/concierge.
+More information at https://github.com/canonical/concierge.
 `,
 		SilenceErrors: true,
 		SilenceUsage:  true,
diff --git a/cmd/restore.go b/cmd/restore.go
index 68e8222..7bf06b6 100644
--- a/cmd/restore.go
+++ b/cmd/restore.go
@@ -3,8 +3,8 @@ package cmd
 import (
 	"fmt"
 
-	"github.com/jnsgruk/concierge/internal/concierge"
-	"github.com/jnsgruk/concierge/internal/config"
+	"github.com/canonical/concierge/internal/concierge"
+	"github.com/canonical/concierge/internal/config"
 	"github.com/spf13/cobra"
 )
 
diff --git a/cmd/status.go b/cmd/status.go
index 8d460cb..9891e25 100644
--- a/cmd/status.go
+++ b/cmd/status.go
@@ -3,8 +3,8 @@ package cmd
 import (
 	"fmt"
 
-	"github.com/jnsgruk/concierge/internal/concierge"
-	"github.com/jnsgruk/concierge/internal/config"
+	"github.com/canonical/concierge/internal/concierge"
+	"github.com/canonical/concierge/internal/config"
 	"github.com/spf13/cobra"
 )
 
diff --git a/go.mod b/go.mod
index 14a0484..a2cfc45 100644
--- a/go.mod
+++ b/go.mod
@@ -1,4 +1,4 @@
-module github.com/jnsgruk/concierge
+module github.com/canonical/concierge
 
 go 1.23.0
 
diff --git a/internal/concierge/manager.go b/internal/concierge/manager.go
index 11d24ce..cd6d89b 100644
--- a/internal/concierge/manager.go
+++ b/internal/concierge/manager.go
@@ -5,8 +5,8 @@ import (
 	"log/slog"
 	"path"
 
-	"github.com/jnsgruk/concierge/internal/config"
-	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/canonical/concierge/internal/config"
+	"github.com/canonical/concierge/internal/system"
 	"gopkg.in/yaml.v3"
 )
 
diff --git a/internal/concierge/plan.go b/internal/concierge/plan.go
index 45d142e..b8464ea 100644
--- a/internal/concierge/plan.go
+++ b/internal/concierge/plan.go
@@ -4,11 +4,11 @@ import (
 	"fmt"
 	"log/slog"
 
-	"github.com/jnsgruk/concierge/internal/config"
-	"github.com/jnsgruk/concierge/internal/juju"
-	"github.com/jnsgruk/concierge/internal/packages"
-	"github.com/jnsgruk/concierge/internal/providers"
-	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/canonical/concierge/internal/config"
+	"github.com/canonical/concierge/internal/juju"
+	"github.com/canonical/concierge/internal/packages"
+	"github.com/canonical/concierge/internal/providers"
+	"github.com/canonical/concierge/internal/system"
 	"golang.org/x/sync/errgroup"
 )
 
diff --git a/internal/concierge/plan_test.go b/internal/concierge/plan_test.go
index 65fefb5..35fa008 100644
--- a/internal/concierge/plan_test.go
+++ b/internal/concierge/plan_test.go
@@ -4,7 +4,7 @@ import (
 	"reflect"
 	"testing"
 
-	"github.com/jnsgruk/concierge/internal/config"
+	"github.com/canonical/concierge/internal/config"
 )
 
 func TestGetSnapChannelOverride(t *testing.T) {
diff --git a/internal/concierge/plan_validators_test.go b/internal/concierge/plan_validators_test.go
index 246902f..b9489ee 100644
--- a/internal/concierge/plan_validators_test.go
+++ b/internal/concierge/plan_validators_test.go
@@ -3,8 +3,8 @@ package concierge
 import (
 	"testing"
 
-	"github.com/jnsgruk/concierge/internal/config"
-	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/canonical/concierge/internal/config"
+	"github.com/canonical/concierge/internal/system"
 )
 
 func TestSingleK8sValidator(t *testing.T) {
diff --git a/internal/juju/juju.go b/internal/juju/juju.go
index 49dc341..c58f067 100644
--- a/internal/juju/juju.go
+++ b/internal/juju/juju.go
@@ -9,10 +9,10 @@ import (
 	"strings"
 	"time"
 
-	"github.com/jnsgruk/concierge/internal/config"
-	"github.com/jnsgruk/concierge/internal/packages"
-	"github.com/jnsgruk/concierge/internal/providers"
-	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/canonical/concierge/internal/config"
+	"github.com/canonical/concierge/internal/packages"
+	"github.com/canonical/concierge/internal/providers"
+	"github.com/canonical/concierge/internal/system"
 	"github.com/sethvargo/go-retry"
 	"golang.org/x/sync/errgroup"
 	"gopkg.in/yaml.v3"
diff --git a/internal/juju/juju_test.go b/internal/juju/juju_test.go
index 859810b..c6129e3 100644
--- a/internal/juju/juju_test.go
+++ b/internal/juju/juju_test.go
@@ -5,9 +5,9 @@ import (
 	"reflect"
 	"testing"
 
-	"github.com/jnsgruk/concierge/internal/config"
-	"github.com/jnsgruk/concierge/internal/providers"
-	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/canonical/concierge/internal/config"
+	"github.com/canonical/concierge/internal/providers"
+	"github.com/canonical/concierge/internal/system"
 )
 
 var fakeGoogleCreds = []byte(`auth-type: oauth2
diff --git a/internal/packages/deb_handler.go b/internal/packages/deb_handler.go
index d30a6f2..73ce604 100644
--- a/internal/packages/deb_handler.go
+++ b/internal/packages/deb_handler.go
@@ -4,7 +4,7 @@ import (
 	"fmt"
 	"log/slog"
 
-	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/canonical/concierge/internal/system"
 )
 
 // NewDeb constructs a new Deb instance.
diff --git a/internal/packages/deb_handler_test.go b/internal/packages/deb_handler_test.go
index 9fb6f30..c36955a 100644
--- a/internal/packages/deb_handler_test.go
+++ b/internal/packages/deb_handler_test.go
@@ -4,7 +4,7 @@ import (
 	"reflect"
 	"testing"
 
-	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/canonical/concierge/internal/system"
 )
 
 func TestDebHandlerCommands(t *testing.T) {
diff --git a/internal/packages/snap_handler.go b/internal/packages/snap_handler.go
index 53693c8..ec70b42 100644
--- a/internal/packages/snap_handler.go
+++ b/internal/packages/snap_handler.go
@@ -5,7 +5,7 @@ import (
 	"log/slog"
 	"strings"
 
-	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/canonical/concierge/internal/system"
 )
 
 // NewSnapHandler constructs a new instance of a SnapHandler.
diff --git a/internal/packages/snap_handler_test.go b/internal/packages/snap_handler_test.go
index 9e2dcb6..8c095d8 100644
--- a/internal/packages/snap_handler_test.go
+++ b/internal/packages/snap_handler_test.go
@@ -4,7 +4,7 @@ import (
 	"reflect"
 	"testing"
 
-	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/canonical/concierge/internal/system"
 )
 
 func TestSnapHandlerCommands(t *testing.T) {
diff --git a/internal/providers/google.go b/internal/providers/google.go
index fa30de7..8676368 100644
--- a/internal/providers/google.go
+++ b/internal/providers/google.go
@@ -4,8 +4,8 @@ import (
 	"fmt"
 	"log/slog"
 
-	"github.com/jnsgruk/concierge/internal/config"
-	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/canonical/concierge/internal/config"
+	"github.com/canonical/concierge/internal/system"
 	"gopkg.in/yaml.v3"
 )
 
diff --git a/internal/providers/google_test.go b/internal/providers/google_test.go
index 5cdb373..854c491 100644
--- a/internal/providers/google_test.go
+++ b/internal/providers/google_test.go
@@ -4,8 +4,8 @@ import (
 	"reflect"
 	"testing"
 
-	"github.com/jnsgruk/concierge/internal/config"
-	"github.com/jnsgruk/concierge/internal/system"
+	"github.com/canonical/concierge/internal/config"
+	"github.com/canonical/concierge/internal/system"
 	"gopkg.in/yaml
... [truncated]
```
