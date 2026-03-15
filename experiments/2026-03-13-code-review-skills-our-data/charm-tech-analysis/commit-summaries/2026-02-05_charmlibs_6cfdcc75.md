# fix: correct silent CI lint failures + types for snap lib (#328)

**Repository**: charmlibs
**Commit**: [6cfdcc75](https://github.com/canonical/charmlibs/commit/6cfdcc75c0f8572e3a7460ccee5e4b827c407047)
**Date**: 2026-02-05

## Classification

| Field | Value |
|-------|-------|
| Bug Area | ci-build |
| Bug Type | error-handling |
| Severity | medium |
| Fix Category | ci-fix |

## Summary

Fixed CI lint script that silently swallowed failures (missing exit $FAILURES) and corrected Python 3.8-compatible typing imports for snap lib.

## Commit Message

This PR applies the CI fix from #325 to the `20.04-maintenance` branch,
revealing that there were some silent type checking failures on this
branch too. This PR therefore also corrects the Python 3.8 compatible
typing for the `snap` library, and updates its version and changelog for
a patch release.

## Changed Files

- M	justfile
- M	snap/CHANGELOG.md
- M	snap/src/charmlibs/snap/_snap.py
- M	snap/src/charmlibs/snap/_version.py

## Diff

```diff
diff --git a/justfile b/justfile
index da6b7d7..f8e12ad 100644
--- a/justfile
+++ b/justfile
@@ -77,6 +77,7 @@ lint package *pyright_args:
     just --justfile='{{justfile()}}' python='{{python}}' fast-lint || ((FAILURES+=$?))
     just --justfile='{{justfile()}}' python='{{python}}' static '{{package}}' "${@}" || ((FAILURES+=1))
     : "$FAILURES command(s) failed."
+    exit $FAILURES
 
 [doc('Run package specific static analysis only, e.g. `just python=3.10 static pathops`.')]
 [positional-arguments]  # pass recipe args to recipe script positionally (so we can get correct quoting)
diff --git a/snap/CHANGELOG.md b/snap/CHANGELOG.md
index 648b7e7..c6002e7 100644
--- a/snap/CHANGELOG.md
+++ b/snap/CHANGELOG.md
@@ -1,3 +1,7 @@
+# 0.8.1 - 5 February 026
+
+Import TypeAlias and builtin generic types from the correct location for Python 3.8.
+
 # 0.8.0 - 10 December 2025
 
 Release with Python 3.8 support. This is a 0.X release which does not guarantee extended support. Changes from the 1.0 release are purely `typing` related. This release is otherwise identical to the 1.0.1 release.
diff --git a/snap/src/charmlibs/snap/_snap.py b/snap/src/charmlibs/snap/_snap.py
index 587ace4..a61282b 100644
--- a/snap/src/charmlibs/snap/_snap.py
+++ b/snap/src/charmlibs/snap/_snap.py
@@ -48,10 +48,9 @@ import opentelemetry.trace
 
 if typing.TYPE_CHECKING:
     # avoid typing_extensions import at runtime
-    from collections.abc import Callable, Iterable, Sequence
-    from typing import TypeAlias
+    from typing import Callable, Iterable, Sequence
 
-    from typing_extensions import NotRequired, ParamSpec, Required, Self, Unpack
+    from typing_extensions import NotRequired, ParamSpec, Required, Self, TypeAlias, Unpack
 
     _P = ParamSpec('_P')
     _T = TypeVar('_T')
diff --git a/snap/src/charmlibs/snap/_version.py b/snap/src/charmlibs/snap/_version.py
index 4548791..5cd0b85 100644
--- a/snap/src/charmlibs/snap/_version.py
+++ b/snap/src/charmlibs/snap/_version.py
@@ -12,4 +12,4 @@
 # See the License for the specific language governing permissions and
 # limitations under the License.
 
-__version__ = '0.8.0'
+__version__ = '0.8.1'
```
