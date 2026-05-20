# fix: revert support of change-update notice due to Juju reversion (#1189)

**Repository**: operator
**Commit**: [dbb843eb](https://github.com/canonical/operator/commit/dbb843ebf9a91cf040ed8900e8a8b7f870501a82)
**Date**: 2024-04-12

## Classification

| Field | Value |
|-------|-------|
| Bug Area | testing-framework |
| Bug Type | version-compat |
| Severity | medium |
| Fix Category | source-fix |

## Summary

revert support of change-update notice due to juju reversion

## Commit Message

This reverts #1170 (commit b7e5ba33e7a18022b56535a4d3d84363e1091f5b) as
this feature has been reverted in Juju on the 3.5 branch, due to the
issues described at this PR: https://github.com/juju/juju/pull/17191

## Changed Files

- M	ops/__init__.py
- M	ops/charm.py
- M	ops/pebble.py
- M	ops/testing.py
- M	test/charms/test_main/src/charm.py
- M	test/test_charm.py
- M	test/test_main.py
- M	test/test_testing.py

## Diff

```diff
diff --git a/ops/__init__.py b/ops/__init__.py
index 77c6b82..60de7ad 100644
--- a/ops/__init__.py
+++ b/ops/__init__.py
@@ -66,7 +66,6 @@ __all__ = [  # noqa: RUF022 `__all__` is not sorted
     'LeaderSettingsChangedEvent',
     'MetadataLinks',
     'PayloadMeta',
-    'PebbleChangeUpdatedEvent',
     'PebbleCustomNoticeEvent',
     'PebbleNoticeEvent',
     'PebbleReadyEvent',
@@ -209,7 +208,6 @@ from .charm import (
     LeaderSettingsChangedEvent,
     MetadataLinks,
     PayloadMeta,
-    PebbleChangeUpdatedEvent,
     PebbleCustomNoticeEvent,
     PebbleNoticeEvent,
     PebbleReadyEvent,
diff --git a/ops/charm.py b/ops/charm.py
index aeb97c7..8ed3f7f 100644
--- a/ops/charm.py
+++ b/ops/charm.py
@@ -34,7 +34,7 @@ from typing import (
     cast,
 )
 
-from ops import model, pebble
+from ops import model
 from ops._private import yaml
 from ops.framework import (
     EventBase,
@@ -809,15 +809,6 @@ class PebbleCustomNoticeEvent(PebbleNoticeEvent):
     """Event triggered when a Pebble notice of type "custom" is created or repeats."""
 
 
-class PebbleChangeUpdatedEvent(PebbleNoticeEvent):
-    """Event triggered when a Pebble notice of type "change-update" is created or repeats."""
-
-    def get_change(self) -> pebble.Change:
-        """Get the Pebble change associated with this event."""
-        change_id = pebble.ChangeID(self.notice.key)
-        return self.workload.pebble.get_change(change_id)
-
-
 class SecretEvent(HookEvent):
     """Base class for all secret events."""
 
@@ -1197,9 +1188,6 @@ class CharmBase(Object):
             container_name = container_name.replace('-', '_')
             self.on.define_event(f"{container_name}_pebble_ready", PebbleReadyEvent)
             self.on.define_event(f"{container_name}_pebble_custom_notice", PebbleCustomNoticeEvent)
-            self.on.define_event(
-                f"{container_name}_pebble_change_updated",
-                PebbleChangeUpdatedEvent)
 
     @property
     def app(self) -> model.Application:
diff --git a/ops/pebble.py b/ops/pebble.py
index 0053bc2..638885f 100644
--- a/ops/pebble.py
+++ b/ops/pebble.py
@@ -1314,17 +1314,7 @@ class CheckInfo:
 class NoticeType(enum.Enum):
     """Enum of notice types."""
 
-    CHANGE_UPDATE = 'change-update'
-    """Recorded whenever a change is updated, that is, when it is first
-    spawned or its status was updated. The key for change-update notices is
-    the change ID.
-    """
-
     CUSTOM = 'custom'
-    """A custom notice reported via the Pebble client API or ``pebble notify``.
-    The key and data fields are provided by the user. The key must be in
-    the format ``example.com/path`` to ensure well-namespaced notice keys.
-    """
 
 
 class NoticesUsers(enum.Enum):
diff --git a/ops/testing.py b/ops/testing.py
index 505088f..e9f2c73 100644
--- a/ops/testing.py
+++ b/ops/testing.py
@@ -1168,13 +1168,8 @@ class Harness(Generic[CharmType]):
 
         id, new_or_repeated = client._notify(type, key, data=data, repeat_after=repeat_after)
 
-        if self._charm is not None and new_or_repeated:
-            if type == pebble.NoticeType.CUSTOM:
-                self.charm.on[container_name].pebble_custom_notice.emit(
-                    container, id, type.value, key)
-            elif type == pebble.NoticeType.CHANGE_UPDATE:
-                self.charm.on[container_name].pebble_change_updated.emit(
-                    container, id, type.value, key)
+        if self._charm is not None and type == pebble.NoticeType.CUSTOM and new_or_repeated:
+            self.charm.on[container_name].pebble_custom_notice.emit(container, id, type.value, key)
 
         return id
 
@@ -3450,6 +3445,10 @@ class _TestingPebbleClient:
 
         Return a tuple of (notice_id, new_or_repeated).
         """
+        if type != pebble.NoticeType.CUSTOM:
+            message = f'invalid type "{type.value}" (can only add "custom" notices)'
+            raise self._api_error(400, message)
+
         # The shape of the code below is taken from State.AddNotice in Pebble.
         now = datetime.datetime.now(tz=datetime.timezone.utc)
 
diff --git a/test/charms/test_main/src/charm.py b/test/charms/test_main/src/charm.py
index d10eb09..ccab5d6 100755
--- a/test/charms/test_main/src/charm.py
+++ b/test/charms/test_main/src/charm.py
@@ -59,7 +59,6 @@ class Charm(ops.CharmBase):
             on_collect_metrics=[],
             on_test_pebble_ready=[],
             on_test_pebble_custom_notice=[],
-            on_test_pebble_change_updated=[],
 
             on_log_critical_action=[],
             on_log_error_action=[],
@@ -93,8 +92,6 @@ class Charm(ops.CharmBase):
         self.framework.observe(self.on.test_pebble_ready, self._on_test_pebble_ready)
         self.framework.observe(self.on.test_pebble_custom_notice,
                                self._on_test_pebble_custom_notice)
-        self.framework.observe(self.on.test_pebble_change_updated,
-                               self._on_test_pebble_change_updated)
 
         self.framework.observe(self.on.secret_remove, self._on_secret_remove)
         self.framework.observe(self.on.secret_rotate, self._on_secret_rotate)
@@ -200,13 +197,6 @@ class Charm(ops.CharmBase):
         self._stored.observed_event_types.append(type(event).__name__)
         self._stored.test_pebble_custom_notice_data = event.snapshot()
 
-    def _on_test_pebble_change_updated(self, event: ops.PebbleChangeUpdatedEvent):
-        assert event.workload is not None
-        assert isinstance(event.notice, ops.LazyNotice)
-        self._stored.on_test_pebble_change_updated.append(type(event).__name__)
-        self._stored.observed_event_types.append(type(event).__name__)
-        self._stored.test_pebble_change_updated_data = event.snapshot()
-
     def _on_start_action(self, event: ops.ActionEvent):
         assert event.handle.kind == 'start_action', (
             'event action name cannot be different from the one being handled')
diff --git a/test/test_charm.py b/test/test_charm.py
index a7392ee..b471b37 100644
--- a/test/test_charm.py
+++ b/test/test_charm.py
@@ -18,14 +18,12 @@ import shutil
 import tempfile
 import typing
 import unittest
-import unittest.mock
 from pathlib import Path
 
 import yaml
 
 import ops
 import ops.charm
-from ops import pebble
 from ops.model import ModelError, _ModelBackend
 from ops.storage import SQLiteStorage
 
@@ -356,19 +354,7 @@ storage:
             'StorageAttachedEvent',
         ])
 
-    @unittest.mock.patch('ops.pebble.Client.get_change')
-    def test_workload_events(self, mock_get_change: unittest.mock.MagicMock):
-        def get_change(change_id: pebble.ChangeID) -> pebble.Change:
-            return pebble.Change.from_dict({
-                'id': pebble.ChangeID(change_id),
-                'kind': 'exec',
-                'ready': False,
-                'spawn-time': '2021-01-28T14:37:02.247202105+13:00',
-                'status': 'Doing',
-                'summary': 'Exec command "foo"',
-            })
-
-        mock_get_change.side_effect = get_change
+    def test_workload_events(self):
 
         class MyCharm(ops.CharmBase):
             def __init__(self, *args: typing.Any):
@@ -383,10 +369,6 @@ storage:
                         self.on[workload].pebble_custom_notice,
                         self.on_any_pebble_custom_notice,
                     )
-                    self.framework.observe(
-                        self.on[workload].pebble_change_updated,
-                        self.on_any_pebble_change_updated,
-                    )
 
             def on_any_pebble_ready(self, event: ops.PebbleReadyEvent):
                 self.seen.append(type(event).__name__)
@@ -394,12 +376,6 @@ storage:
             def on_any_pebble_custom_notice(self, event: ops.PebbleCustomNoticeEvent):
                 self.seen.append(type(event).__name__)
 
-            def on_any_pebble_change_updated(self, event: ops.PebbleChangeUpdatedEvent):
-                self.seen.append(type(event).__name__)
-                change = event.get_change()
-                assert change.id == event.notice.key
-                assert change.kind == 'exec'
-
         # language=YAML
         self.meta = ops.CharmMeta.from_yaml(metadata='''
 name: my-charm
@@ -423,18 +399,11 @@ containers:
         charm.on['containerb'].pebble_custom_notice.emit(
             charm.framework.model.unit.get_container('containerb'), '2', 'custom', 'y')
 
-        charm.on['container-a'].pebble_change_updated.emit(
-            charm.framework.model.unit.get_container('container-a'), '1', 'change-update', '42')
-        charm.on['containerb'].pebble_change_updated.emit(
-            charm.framework.model.unit.get_container('containerb'), '2', 'change-update', '42')
-
         self.assertEqual(charm.seen, [
             'PebbleReadyEvent',
             'PebbleReadyEvent',
             'PebbleCustomNoticeEvent',
             'PebbleCustomNoticeEvent',
-            'PebbleChangeUpdatedEvent',
-            'PebbleChangeUpdatedEvent',
         ])
 
     def test_relations_meta(self):
diff --git a/test/test_main.py b/test/test_main.py
index 4747f98..c22d0b5 100644
--- a/test/test_main.py
+++ b/test/test_main.py
@@ -608,16 +608,6 @@ class _TestMain(abc.ABC):
              'notice_id': '123',
              'notice_type': 'custom',
              'notice_key': 'example.com/a'},
-        ), (
-            EventSpec(ops.PebbleChangeUpdatedEvent, 'test_pebble_change_updated',
-                      workload_name='test',
-                      notice_id='456',
-                      notice_type='change-update',
-                      notice_key='42'),
-            {'container_name': 'test',
-             'notice_id': '456',
-             'notice_type': 'change-update',
-             'notice_key': '42'},
         ), (
             EventSpec(ops.SecretChangedEvent, 'secret_changed',
                       secret_id='secret:12345',
diff --git a/test/test_testing.py b/test/test_testing.py
index a276
... [truncated]
```
