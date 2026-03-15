# fixed error because pathlib.Path.rmdir will bork on nonempty dir

**Repository**: operator
**Commit**: [fb9ce8de](https://github.com/canonical/operator/commit/fb9ce8de5ffa46212210f9d9d2a2b82627be1fb5)
**Date**: 2023-09-08

## Classification

| Field | Value |
|-------|-------|
| Bug Area | error-handling |
| Bug Type | edge-case |
| Severity | medium |
| Fix Category | source-fix |

## Summary

ed error because pathlib.path.rmdir will bork on nonempty dir

## Changed Files

- M	scenario/mocking.py

## Diff

```diff
diff --git a/scenario/mocking.py b/scenario/mocking.py
index 15dd25f..12d7c23 100644
--- a/scenario/mocking.py
+++ b/scenario/mocking.py
@@ -3,6 +3,7 @@
 # See LICENSE file for licensing details.
 import datetime
 import random
+import shutil
 from io import StringIO
 from pathlib import Path
 from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Tuple, Union
@@ -414,7 +415,8 @@ class _MockPebbleClient(_TestingPebbleClient):
 
         # wipe just in case
         if container_root.exists():
-            container_root.rmdir()
+            # Path.rmdir will fail if root is nonempty
+            shutil.rmtree(container_root)
 
         # initialize simulated filesystem
         container_root.mkdir(parents=True)
```
