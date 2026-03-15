# fix: use a channel in the override test that is likely to stick around (#112)

**Repository**: canonical/concierge
**Commit**: [6c6f2cb5](https://github.com/canonical/canonical/concierge/commit/6c6f2cb52d15a3c1dc44389eaf2ffd048f458b41)
**Date**: 2025-09-26T16:26:04+12:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | testing |
| Bug Type | test-fix |
| Severity | low |
| Fix Category | test-fix |

## Summary

Switch test to use latest/edge channel instead of removed 1.31-classic/beta channel

## Commit Message

The `overrides-env` test currently tries to use the environment to
override the default `k8s` channel to be `1.31-classic/beta`. This
channel appears to have been removed at some point, which causes the
test to now fail.

The PR changes the override to `latest/edge`, which seems likely to be
around for a long time (the default is currently "1.32-classic/stable").

## Changed Files

- M	tests/overrides-env/task.yaml

## Diff

```diff
diff --git a/tests/overrides-env/task.yaml b/tests/overrides-env/task.yaml
index 2a54ded..21dc5c7 100644
--- a/tests/overrides-env/task.yaml
+++ b/tests/overrides-env/task.yaml
@@ -9,14 +9,14 @@ execute: |
   export CONCIERGE_CHARMCRAFT_CHANNEL=latest/edge
   export CONCIERGE_ROCKCRAFT_CHANNEL=latest/edge
   export CONCIERGE_LXD_CHANNEL=latest/candidate
-  export CONCIERGE_K8S_CHANNEL=1.31-classic/beta
+  export CONCIERGE_K8S_CHANNEL=latest/edge
 
   export CONCIERGE_EXTRA_SNAPS="node/22/stable"
   export CONCIERGE_EXTRA_DEBS="make"
 
   "$SPREAD_PATH"/concierge --trace prepare -p k8s
 
-  for i in charmcraft rockcraft; do
+  for i in charmcraft rockcraft k8s; do
     list="$(snap list $i)"
     echo $list | MATCH $i
     echo $list | MATCH latest/edge
@@ -28,9 +28,6 @@ execute: |
   list="$(snap list lxd)"
   echo $list | MATCH latest/candidate
 
-  list="$(snap list k8s)"
-  echo $list | MATCH 1.31-classic/beta
-
   list="$(snap list node)"
   echo $list | MATCH 22/stable
```
