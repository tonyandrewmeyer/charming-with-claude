# fix: fix TypeError when running test.pebble_cli (#1245)

**Repository**: operator
**Commit**: [dcbe21bd](https://github.com/canonical/operator/commit/dcbe21bd3ffd21255cdb5e7ae5b4664fcbec3da1)
**Date**: 2024-06-05

## Classification

| Field | Value |
|-------|-------|
| Bug Area | pebble |
| Bug Type | type-error |
| Severity | low |
| Fix Category | test-fix |

## Summary

fix typeerror when running test.pebble_cli

## Commit Message

Without this fix, running this raises the following:

```
TypeError: catching classes that do not inherit from BaseException is not allowed
```

Not sure how to silence pyright without the type: ignores.

I guess we haven't used this script in a while. :-)

## Changed Files

- M	test/pebble_cli.py

## Diff

```diff
diff --git a/test/pebble_cli.py b/test/pebble_cli.py
index 5ae722d..0e7a207 100644
--- a/test/pebble_cli.py
+++ b/test/pebble_cli.py
@@ -246,9 +246,8 @@ def main():
                     if stderr:
                         print(repr(stderr), end='', file=sys.stderr)
                 sys.exit(0)
-            # The `[str]` here is to resolve the same issue as above.
-            except pebble.ExecError[str] as e:
-                print('ExecError:', e, file=sys.stderr)
+            except pebble.ExecError as e:  # type: ignore
+                print('ExecError:', e, file=sys.stderr)  # type: ignore
                 sys.exit(e.exit_code)
 
         elif args.command == 'ls':
```
