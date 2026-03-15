# fix: rework ops.main type hints to allow different flavours (callable class) (#1345)

**Repository**: operator
**Commit**: [cdfd10f3](https://github.com/canonical/operator/commit/cdfd10f34f2d8338fb18dea1185cdd70ea082252)
**Date**: 2024-09-03

## Classification

| Field | Value |
|-------|-------|
| Bug Area | type-annotations |
| Bug Type | none-guard |
| Severity | high |
| Fix Category | source-fix |

## Summary

rework ops.main type hints to allow different flavours (callable class)

## Commit Message

Merge readiness check
- [x] implementation
- [x] tests
- [x] docs
- [x] re-export some symbols

Release readiness check
- [ ] full super-tox
- [ ] jhack PR or decision to re-export symbols + small PR
- [ ] 2 Scenario PRs or decision to re-export symbols
- [ ] `canonical/hardware-observer-operator` PR

Slated for ops==2.17.0

https://warthogs.atlassian.net/browse/CHARMTECH-232

## Changed Files

- M	docs/index.rst
- M	ops/__init__.py
- A	ops/_main.py
- M	ops/main.py
- M	pyproject.toml
- M	test/test_main.py
- A	test/test_main_invocation.py
- A	test/test_main_type_hint.py

## Diff

```diff
diff --git a/docs/index.rst b/docs/index.rst
index 3903983..af4de65 100644
--- a/docs/index.rst
+++ b/docs/index.rst
@@ -10,12 +10,19 @@ ops module
 ==========
 
 .. automodule:: ops
+   :exclude-members: main
 
 
-main
------------
+ops.main entry point
+====================
+.. autofunction:: ops.main
+
+
+legacy main module
+------------------
 
 .. automodule:: ops.main
+   :noindex:
 
 
 ops.pebble module
diff --git a/ops/__init__.py b/ops/__init__.py
index 8fccdc6..19679cf 100644
--- a/ops/__init__.py
+++ b/ops/__init__.py
@@ -173,6 +173,7 @@ __all__ = [  # noqa: RUF022 `__all__` is not sorted
 # The isort command wants to rearrange the nicely-formatted imports below;
 # just skip it for this file.
 # isort:skip_file
+from typing import Optional, Type
 
 # Import pebble explicitly. It's the one module we don't import names from below.
 from . import pebble
@@ -180,11 +181,10 @@ from . import pebble
 # Also import charm explicitly. This is not strictly necessary as the
 # "from .charm" import automatically does that, but be explicit since this
 # import was here previously
-from . import charm  # type: ignore # noqa: F401 `.charm` imported but unused
+from . import charm
 
-# Import the main module, which we've overriden in main.py to be callable.
-# This allows "import ops; ops.main(Charm)" to work as expected.
-from . import main
+from . import _main
+from . import main as _legacy_main
 
 # Explicitly import names from submodules so users can just "import ops" and
 # then use them as "ops.X".
@@ -321,3 +321,44 @@ from .model import (
 # rather than a runtime concern.
 
 from .version import version as __version__
+
+
+class _Main:
+    def __call__(
+        self, charm_class: Type[charm.CharmBase], use_juju_for_storage: Optional[bool] = None
+    ):
+        return _main.main(charm_class=charm_class, use_juju_for_storage=use_juju_for_storage)
+
+    def main(
+        self, charm_class: Type[charm.CharmBase], use_juju_for_storage: Optional[bool] = None
+    ):
+        return _legacy_main.main(
+            charm_class=charm_class, use_juju_for_storage=use_juju_for_storage
+        )
+
+
+main = _Main()
+"""Set up the charm and dispatch the observed event.
+
+Recommended usage:
+
+.. code-block:: python
+
+    import ops
+
+    class SomeCharm(ops.CharmBase): ...
+
+    if __name__ == "__main__":
+        ops.main(SomeCharm)
+
+Args:
+    charm_class: the charm class to instantiate and receive the event.
+    use_juju_for_storage: whether to use controller-side storage.
+        The default is ``False`` for most charms.
+        Podspec charms that haven't previously used local storage and that
+        are running on a new enough Juju default to controller-side storage,
+        and local storage otherwise.
+
+.. jujuremoved:: 4.0
+    The ``use_juju_for_storage`` argument is not available from Juju 4.0
+"""
diff --git a/ops/_main.py b/ops/_main.py
new file mode 100644
index 0000000..a492846
--- /dev/null
+++ b/ops/_main.py
@@ -0,0 +1,545 @@
+# Copyright 2019 Canonical Ltd.
+#
+# Licensed under the Apache License, Version 2.0 (the "License");
+# you may not use this file except in compliance with the License.
+# You may obtain a copy of the License at
+#
+# http://www.apache.org/licenses/LICENSE-2.0
+#
+# Unless required by applicable law or agreed to in writing, software
+# distributed under the License is distributed on an "AS IS" BASIS,
+# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+# See the License for the specific language governing permissions and
+# limitations under the License.
+
+"""Implement the main entry point to the framework."""
+
+import logging
+import os
+import shutil
+import subprocess
+import sys
+import warnings
+from pathlib import Path
+from typing import Any, Dict, List, Optional, Tuple, Type, Union, cast
+
+import ops.charm
+import ops.framework
+import ops.model
+import ops.storage
+from ops.charm import CharmMeta
+from ops.jujucontext import _JujuContext
+from ops.log import setup_root_logging
+
+CHARM_STATE_FILE = '.unit-state.db'
+
+
+logger = logging.getLogger()
+
+
+def _exe_path(path: Path) -> Optional[Path]:
+    """Find and return the full path to the given binary.
+
+    Here path is the absolute path to a binary, but might be missing an extension.
+    """
+    p = shutil.which(path.name, mode=os.F_OK, path=str(path.parent))
+    if p is None:
+        return None
+    return Path(p)
+
+
+def _create_event_link(
+    charm: 'ops.charm.CharmBase',
+    bound_event: 'ops.framework.BoundEvent',
+    link_to: Union[str, Path],
+):
+    """Create a symlink for a particular event.
+
+    Args:
+        charm: A charm object.
+        bound_event: An event for which to create a symlink.
+        link_to: What the event link should point to
+    """
+    # type guard
+    assert bound_event.event_kind, f'unbound BoundEvent {bound_event}'
+
+    if issubclass(bound_event.event_type, ops.charm.HookEvent):
+        event_dir = charm.framework.charm_dir / 'hooks'
+        event_path = event_dir / bound_event.event_kind.replace('_', '-')
+    elif issubclass(bound_event.event_type, ops.charm.ActionEvent):
+        if not bound_event.event_kind.endswith('_action'):
+            raise RuntimeError(f'action event name {bound_event.event_kind} needs _action suffix')
+        event_dir = charm.framework.charm_dir / 'actions'
+        # The event_kind is suffixed with "_action" while the executable is not.
+        event_path = event_dir / bound_event.event_kind[: -len('_action')].replace('_', '-')
+    else:
+        raise RuntimeError(
+            f'cannot create a symlink: unsupported event type {bound_event.event_type}'
+        )
+
+    event_dir.mkdir(exist_ok=True)
+    if not event_path.exists():
+        target_path = os.path.relpath(link_to, str(event_dir))
+
+        # Ignore the non-symlink files or directories
+        # assuming the charm author knows what they are doing.
+        logger.debug(
+            'Creating a new relative symlink at %s pointing to %s', event_path, target_path
+        )
+        event_path.symlink_to(target_path)
+
+
+def _setup_event_links(charm_dir: Path, charm: 'ops.charm.CharmBase', juju_context: _JujuContext):
+    """Set up links for supported events that originate from Juju.
+
+    Whether a charm can handle an event or not can be determined by
+    introspecting which events are defined on it.
+
+    Hooks or actions are created as symlinks to the charm code file
+    which is determined by inspecting symlinks provided by the charm
+    author at hooks/install or hooks/start.
+
+    Args:
+        charm_dir: A root directory of the charm.
+        charm: An instance of the Charm class.
+        juju_context: An instance of the _JujuContext class.
+
+    """
+    link_to = os.path.realpath(juju_context.dispatch_path or sys.argv[0])
+    for bound_event in charm.on.events().values():
+        # Only events that originate from Juju need symlinks.
+        if issubclass(bound_event.event_type, (ops.charm.HookEvent, ops.charm.ActionEvent)):
+            _create_event_link(charm, bound_event, link_to)
+
+
+def _emit_charm_event(charm: 'ops.charm.CharmBase', event_name: str, juju_context: _JujuContext):
+    """Emits a charm event based on a Juju event name.
+
+    Args:
+        charm: A charm instance to emit an event from.
+        event_name: A Juju event name to emit on a charm.
+        juju_context: An instance of the _JujuContext class.
+    """
+    event_to_emit = None
+    try:
+        event_to_emit = getattr(charm.on, event_name)
+    except AttributeError:
+        logger.debug('Event %s not defined for %s.', event_name, charm)
+
+    # If the event is not supported by the charm implementation, do
+    # not error out or try to emit it. This is to support rollbacks.
+    if event_to_emit is not None:
+        args, kwargs = _get_event_args(charm, event_to_emit, juju_context)
+        logger.debug('Emitting Juju event %s.', event_name)
+        event_to_emit.emit(*args, **kwargs)
+
+
+def _get_event_args(
+    charm: 'ops.charm.CharmBase',
+    bound_event: 'ops.framework.BoundEvent',
+    juju_context: _JujuContext,
+) -> Tuple[List[Any], Dict[str, Any]]:
+    event_type = bound_event.event_type
+    model = charm.framework.model
+
+    relation = None
+    if issubclass(event_type, ops.charm.WorkloadEvent):
+        workload_name = juju_context.workload_name
+        assert workload_name is not None
+        container = model.unit.get_container(workload_name)
+        args: List[Any] = [container]
+        if issubclass(event_type, ops.charm.PebbleNoticeEvent):
+            notice_id = juju_context.notice_id
+            notice_type = juju_context.notice_type
+            notice_key = juju_context.notice_key
+            args.extend([notice_id, notice_type, notice_key])
+        elif issubclass(event_type, ops.charm.PebbleCheckEvent):
+            check_name = juju_context.pebble_check_name
+            args.append(check_name)
+        return args, {}
+    elif issubclass(event_type, ops.charm.SecretEvent):
+        args: List[Any] = [
+            juju_context.secret_id,
+            juju_context.secret_label,
+        ]
+        if issubclass(event_type, (ops.charm.SecretRemoveEvent, ops.charm.SecretExpiredEvent)):
+            args.append(juju_context.secret_revision)
+        return args, {}
+    elif issubclass(event_type, ops.charm.StorageEvent):
+        # Before JUJU_STORAGE_ID exists, take the event name as
+        # <storage_name>_storage_<attached|detached> and replace it with <storage_name>
+        storage_name = juju_context.storage_name or '-'.join(
+            bound_event.event_kind.split('_')[:-2]
+        )
+
+        storages = model.storages[storage_name]
+        index, storage_location = model._backend._storage_event_details()
+        if len(storages) == 1:
+            storage = storages[0]
+        else:
+            # If there's more than one value, pick the right one
... [truncated]
```
