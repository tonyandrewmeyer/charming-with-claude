# fix: allow the library to work on Python 3.8+ (#80)

**Repository**: jubilant
**Commit**: [5b0c1bef](https://github.com/canonical/jubilant/commit/5b0c1bef45cb67ca2d752a049b946b318c708f24)
**Date**: 2025-04-04T14:19:23+13:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | packaging |
| Bug Type | other |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Library required Python 3.12+ due to typing syntax and dataclass features; backported to 3.8+

## Commit Message

This includes:

- mostly typing tweaks
- avoid use kw_only=True in dataclasses
- avoid use of Exception.add_note in Juju.wait

We've decided we lose almost nothing by having the minimum set back to
Python 3.8, and it doesn't add any serious ugliness to the code. It's
going to cause charmers who start using Jubilant less annoyance, so just
go ahead and do it.

## Changed Files

- M	.github/workflows/ci.yaml
- M	README.md
- M	docs/tutorial/getting-started.md
- M	jubilant/_all_any.py
- M	jubilant/_juju.py
- M	jubilant/_pretty.py
- M	jubilant/_task.py
- M	jubilant/_test_helpers.py
- M	jubilant/_yaml.py
- M	jubilant/statustypes.py
- M	pyproject.toml
- M	tests/integration/charms/testapp/pyproject.toml
- M	tests/integration/charms/testapp/uv.lock
- M	tests/integration/charms/testdb/pyproject.toml
- M	tests/integration/charms/testdb/uv.lock
- M	tests/integration/conftest.py
- M	tests/unit/conftest.py
- M	tests/unit/mocks.py
- M	tests/unit/test_all_any.py
- M	tests/unit/test_run.py
- M	tests/unit/test_wait.py
- M	uv.lock

## Diff

```diff
diff --git a/.github/workflows/ci.yaml b/.github/workflows/ci.yaml
index 340777f..0e299a7 100644
--- a/.github/workflows/ci.yaml
+++ b/.github/workflows/ci.yaml
@@ -42,7 +42,7 @@ jobs:
       fail-fast: false
       matrix:
         os: [ubuntu-latest, macos-latest]
-        python-version: ["3.12", "3.13"]
+        python-version: ["3.8", "3.10", "3.12", "3.13"]
 
     steps:
       - name: Check out repo
diff --git a/README.md b/README.md
index b28f46a..079cef7 100644
--- a/README.md
+++ b/README.md
@@ -4,8 +4,6 @@ Jubilant is a Python library that wraps the [Juju](https://juju.is/) CLI for use
 
 You should consider switching to Jubilant if your integration tests currently use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) (and they probably do). Jubilant has an API you'll pick up quickly, and it avoids some of the pain points of [python-libjuju](https://github.com/juju/python-libjuju/), such as websocket failures and having to use `async`. Read our [design goals](https://canonical-jubilant.readthedocs-hosted.com/explanation/design-goals).
 
-Jubilant requires Python 3.12 or above. If your charm uses an Ubuntu base with an older Python version, run your integration tests with Python 3.12+ and install Jubilant with the requirement `jubilant;python_version>='3.12'` ([see an example](https://github.com/jnsgruk/zinc-k8s-operator/pull/355/files)).
-
 Jubilant is currently in pre-release or "beta" phase (see [PyPI releases](https://pypi.org/project/jubilant/#history)). Our intention is to release version 1.0.0 in May 2025.
 
 [**Read the full documentation**](https://canonical-jubilant.readthedocs-hosted.com/)
diff --git a/docs/tutorial/getting-started.md b/docs/tutorial/getting-started.md
index f5d8f06..7a78e74 100644
--- a/docs/tutorial/getting-started.md
+++ b/docs/tutorial/getting-started.md
@@ -15,7 +15,7 @@ $ pip install jubilant
 $ uv add jubilant
 ```
 
-Jubilant requires Python 3.12 or above. If your charm uses an Ubuntu base with an older Python version, run your integration tests with Python 3.12+ and install Jubilant with the requirement `jubilant;python_version>='3.12'` ([see an example](https://github.com/jnsgruk/zinc-k8s-operator/pull/355/files)).
+Like the [Ops](https://github.com/canonical/operator) framework used by charms, Jubilant requires Python 3.8 or above.
 
 
 ## Check your setup
diff --git a/jubilant/_all_any.py b/jubilant/_all_any.py
index d1e91d5..42f862f 100644
--- a/jubilant/_all_any.py
+++ b/jubilant/_all_any.py
@@ -116,7 +116,7 @@ def any_waiting(status: Status, apps: Iterable[str] | None = None) -> bool:
 
 
 def _all_statuses_are(expected: str, status: Status, apps: Iterable[str] | None) -> bool:
-    if isinstance(apps, str | bytes):
+    if isinstance(apps, (str, bytes)):
         raise TypeError('"apps" must be an iterable of names (like a list), not a string')
 
     if apps is None:
@@ -135,7 +135,7 @@ def _all_statuses_are(expected: str, status: Status, apps: Iterable[str] | None)
 
 
 def _any_status_is(expected: str, status: Status, apps: Iterable[str] | None) -> bool:
-    if isinstance(apps, str | bytes):
+    if isinstance(apps, (str, bytes)):
         raise TypeError('"apps" must be an iterable of names (like a list), not a string')
 
     if apps is None:
diff --git a/jubilant/_juju.py b/jubilant/_juju.py
index d324a14..13a72bb 100644
--- a/jubilant/_juju.py
+++ b/jubilant/_juju.py
@@ -10,7 +10,7 @@ import subprocess
 import tempfile
 import time
 from collections.abc import Callable, Iterable, Mapping
-from typing import Any, overload
+from typing import Any, Union, overload
 
 from . import _yaml
 from ._task import Task
@@ -39,7 +39,7 @@ class SecretURI(str):
     """A string subclass that represents a secret URI ("secret:...")."""
 
 
-type ConfigValue = bool | int | float | str | SecretURI
+ConfigValue = Union[bool, int, float, str, SecretURI]
 """The possible types a charm config value can be."""
 
 
@@ -657,9 +657,7 @@ class Juju:
                 logger.info('wait: status changed:\n%s', status)
 
             if error is not None and error(status):
-                exc = WaitError(f'error function {error.__qualname__} returned false')
-                exc.add_note(str(status))
-                raise exc
+                raise WaitError(f'error function {error.__qualname__} returned false\n{status}')
 
             if ready(status):
                 success_count += 1
@@ -670,10 +668,9 @@ class Juju:
 
             time.sleep(delay)
 
-        exc = TimeoutError(f'wait timed out after {timeout}s')
-        if status is not None:
-            exc.add_note(str(status))
-        raise exc
+        if status is None:
+            raise TimeoutError(f'wait timed out after {timeout}s')
+        raise TimeoutError(f'wait timed out after {timeout}s\n{status}')
 
     @functools.cached_property
     def _juju_is_snap(self) -> bool:
diff --git a/jubilant/_pretty.py b/jubilant/_pretty.py
index 2c783f7..f725238 100644
--- a/jubilant/_pretty.py
+++ b/jubilant/_pretty.py
@@ -1,3 +1,5 @@
+from __future__ import annotations
+
 import dataclasses
 from typing import cast
 
@@ -42,7 +44,7 @@ def _dump(value: object, indent: str = '') -> str:
         return f'{class_name}(\n{lines_str}\n{indent})'
 
     elif isinstance(value, list):
-        value = cast(list[object], value)
+        value = cast('list[object]', value)
         is_simple = all(isinstance(v, _SIMPLE_TYPES) for v in value)
         if is_simple:
             single_line = repr(value)
@@ -54,7 +56,7 @@ def _dump(value: object, indent: str = '') -> str:
         return f'[\n{lines_str}\n{indent}]'
 
     elif isinstance(value, dict):
-        value = cast(dict[str, object], value)
+        value = cast('dict[str, object]', value)
         is_simple = all(isinstance(v, _SIMPLE_TYPES) for v in value.values())
         if is_simple:
             single_line = repr(value)
diff --git a/jubilant/_task.py b/jubilant/_task.py
index fe7c652..81d8eaa 100644
--- a/jubilant/_task.py
+++ b/jubilant/_task.py
@@ -4,7 +4,7 @@ import dataclasses
 from typing import Any, Literal
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class Task:
     """A task holds the results of Juju running an action or exec command on a single unit."""
 
diff --git a/jubilant/_test_helpers.py b/jubilant/_test_helpers.py
index 220a15c..d534fb9 100644
--- a/jubilant/_test_helpers.py
+++ b/jubilant/_test_helpers.py
@@ -1,6 +1,6 @@
 import contextlib
 import secrets
-from collections.abc import Generator
+from typing import Generator
 
 from ._juju import Juju
 
diff --git a/jubilant/_yaml.py b/jubilant/_yaml.py
index 8f9073e..9ddb32e 100644
--- a/jubilant/_yaml.py
+++ b/jubilant/_yaml.py
@@ -1,6 +1,6 @@
 from __future__ import annotations
 
-from typing import Any, Protocol, TypeVar, overload
+from typing import Any, Protocol, TypeVar, Union, overload
 
 import yaml
 
@@ -13,7 +13,7 @@ class SupportsRead(Protocol[_T_co]):
     def read(self, length: int = ..., /) -> _T_co: ...
 
 
-type _ReadStream = str | bytes | SupportsRead[str] | SupportsRead[bytes]
+_ReadStream = Union[str, bytes, SupportsRead[str], SupportsRead[bytes]]
 
 _T_contra = TypeVar('_T_contra', str, bytes, contravariant=True)
 
diff --git a/jubilant/statustypes.py b/jubilant/statustypes.py
index a90e1fd..9477b1a 100644
--- a/jubilant/statustypes.py
+++ b/jubilant/statustypes.py
@@ -41,7 +41,7 @@ class StatusError(Exception):
     """Raised when ``juju status`` returns a status-error for certain types."""
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class FormattedBase:
     name: str
     channel: str
@@ -54,7 +54,7 @@ class FormattedBase:
         )
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class StatusInfo:
     current: str = ''
     message: str = ''
@@ -77,7 +77,7 @@ class StatusInfo:
         )
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class AppStatusRelation:
     related_app: str = ''
     interface: str = ''
@@ -92,7 +92,7 @@ class AppStatusRelation:
         )
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class UnitStatus:
     workload_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
     juju_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
@@ -158,7 +158,7 @@ class UnitStatus:
         return self.workload_status.current == 'waiting'
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class AppStatus:
     charm: str
     charm_origin: str
@@ -250,7 +250,7 @@ class AppStatus:
         return self.app_status.current == 'waiting'
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class EntityStatus:
     current: str = ''
     message: str = ''
@@ -265,7 +265,7 @@ class EntityStatus:
         )
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class UnitStorageAttachment:
     machine: str = ''
     location: str = ''
@@ -280,7 +280,7 @@ class UnitStorageAttachment:
         )
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class StorageAttachments:
     units: dict[str, UnitStorageAttachment]
 
@@ -291,7 +291,7 @@ class StorageAttachments:
         )
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class StorageInfo:
     kind: str
     status: EntityStatus
@@ -313,7 +313,7 @@ class StorageInfo:
         )
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class FilesystemAttachment:
     mount_point: str
     read_only: bool
@@ -329,7 +329,7 @@ class FilesystemAttachment:
         )
 
 
-@dataclasses.dataclass(frozen=True, kw_only=True)
+@dataclasses.dataclass(frozen=True)
 class FilesystemAttachments:
     machines: dict[str
... [truncated]
```
