# fix bugs

**Repository**: charmcraft-profile-tools
**Commit**: [9b0ca370](https://github.com/canonical/charmcraft-profile-tools/commit/9b0ca370a77883f645ebdeb130d5a618eab7d5df)
**Date**: 2025-08-26

## Classification

| Field | Value |
|-------|-------|
| Bug Area | automation |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Multiple path handling bugs in implement script and justfile: wrong CWD assumptions, missing cleanup

## Changed Files

- M	implemented/implement-kubernetes-dev-jubilant.py
- M	justfile

## Diff

```diff
diff --git a/implemented/implement-kubernetes-dev-jubilant.py b/implemented/implement-kubernetes-dev-jubilant.py
index 246b6d9..76a80d5 100755
--- a/implemented/implement-kubernetes-dev-jubilant.py
+++ b/implemented/implement-kubernetes-dev-jubilant.py
@@ -1,22 +1,19 @@
-#!/usr/bin/env python
+#!/usr/bin/env python3
 
-import pathlib
 import subprocess
 
 import rewriter
 
-CHARM = pathlib.Path('kubernetes-dev-jubilant')
-
 
 def main():
-    r = rewriter.Rewriter(CHARM / 'charmcraft.yaml')
+    r = rewriter.Rewriter('charmcraft.yaml')
     r.next_by_prefix(
         prefix='    upstream-source: some-repo/some-image:some-tag',
         change='    upstream-source: ghcr.io/canonical/api_demo_server:1.0.1',
     )
     r.save()
 
-    r = rewriter.Rewriter(CHARM / 'src/charm.py')
+    r = rewriter.Rewriter('src/charm.py')
     r.next_by_prefix('    def _on_pebble_ready')
     r.insert(
         '        command = "uvicorn api_demo_server.app:app --host=0.0.0.0 --port=8000"'
@@ -27,7 +24,7 @@ def main():
     )
     r.save()
 
-    r = rewriter.Rewriter(CHARM / 'src/my_application.py')
+    r = rewriter.Rewriter('src/my_application.py')
     r.next_by_prefix('import logging')
     r.insert('')
     r.insert('import requests')
@@ -38,7 +35,7 @@ def main():
     r.insert('    return resonse_data["version"]')
     r.save()
 
-    r = rewriter.Rewriter(CHARM / 'tests/integration/test_charm.py')
+    r = rewriter.Rewriter('tests/integration/test_charm.py')
     r.next_by_prefix(prefix='@pytest.mark.skip', change='# @pytest.mark.skip')
     r.next_by_prefix('    assert version', remove_line=True)
     r.insert(
@@ -46,10 +43,8 @@ def main():
     )
     r.save()
 
-    subprocess.check_call(['uv', 'add', 'requests'], cwd=CHARM)
-    subprocess.check_call(['tox', '-e', 'format'], cwd=CHARM)
-    subprocess.check_call(['tox', '-e', 'lint'], cwd=CHARM)
-    subprocess.check_call(['tox', '-e', 'unit'], cwd=CHARM)
+    subprocess.check_call(['uv', 'add', 'requests'])
+    subprocess.check_call(['tox', '-e', 'format'])
 
 
 if __name__ == '__main__':
diff --git a/justfile b/justfile
index cf3bd6f..f1e5b83 100644
--- a/justfile
+++ b/justfile
@@ -9,6 +9,12 @@ init:
     profile="${dir%%-*}"  # For example, 'kubernetes' from 'kubernetes-dev'
     CHARMCRAFT_DEVELOPER=1 charmcraft init --profile "$profile" --name my-application
 
+[no-cd]
+check:
+    #!/usr/bin/env bash
+    tox -e lint
+    tox -e unit
+
 [no-cd]
 lock:
     #!/usr/bin/env bash
@@ -32,8 +38,17 @@ implement:
     fi
     shopt -s dotglob
     cp -r * "../implemented/$dir"
-    cd ../implemented
-    "./implement-$dir.py"
+    cd "../implemented/$dir"
+    rm -rf .ruff_cache .tox .coverage
+    "../implement-$dir.py"
+
+[no-cd]
+check-implemented:
+    #!/usr/bin/env bash
+    dir=$(basename "$PWD")
+    cd "../implemented/$dir"
+    tox -e lint
+    tox -e unit
 
 [no-cd]
 rm:
```
