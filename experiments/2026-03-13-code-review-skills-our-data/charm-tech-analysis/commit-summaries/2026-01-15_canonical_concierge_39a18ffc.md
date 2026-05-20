# fix: don't dereference symlinks in recursive ownership change (#141)

**Repository**: canonical/concierge
**Commit**: [39a18ffc](https://github.com/canonical/canonical/concierge/commit/39a18ffcda54490203efa974d8433f8a7af253bc)
**Date**: 2026-01-15T07:42:02+08:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | provisioning |
| Bug Type | edge-case |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Use Lchown instead of Chown to avoid following symlinks during recursive ownership changes

## Commit Message

`ChownAll` is used for two purposes in the context of the calling user
(user outside of `sudo`):
- to fix `~/.local` directory permissions
- to fix permissions of newly created or overwritten files
(`~/.cache/concierge/concierge.yaml`, `~/.kube/config`,
`~/.local/share/juju/credentials.yaml`)

The second use is unaffected by the change, because these files are
supposed to be regular files.

The first use is recursive (arguably a bad practice to potentially
change `~/.local/**/*`) and fails before this PR, if there's a dangling
symlink (from some other tool, possibly broken tool, happened with `uv
tool` artefacts twice for me already). For entries in the subdir tree,
`os.Chown` and `os.Lchown` are equivalent for regular files and
directories, and for symlinks, we want to change the symlink itself and
not its target (which could be anywhere in the filesystem,
hypothetically `~/.local/resolve.conf --> /etc/resolve.conf`)

Fixes #91

## Changed Files

- M	internal/system/runner.go

## Diff

```diff
diff --git a/internal/system/runner.go b/internal/system/runner.go
index d07f080..56bcc3b 100644
--- a/internal/system/runner.go
+++ b/internal/system/runner.go
@@ -179,7 +179,7 @@ func (s *System) ChownAll(path string, user *user.User) error {
 			return err
 		}
 
-		err = os.Chown(path, uid, gid)
+		err = os.Lchown(path, uid, gid)
 		if err != nil {
 			return err
 		}
```
