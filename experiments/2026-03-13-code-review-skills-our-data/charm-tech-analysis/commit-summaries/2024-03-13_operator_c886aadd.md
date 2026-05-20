# fix(pebble)!: change select=all to users=all for pebble get_notices (#1146)

**Repository**: operator
**Commit**: [c886aadd](https://github.com/canonical/operator/commit/c886aadd865e2241d59df3201633d67fa116a290)
**Date**: 2024-03-13

## Classification

| Field | Value |
|-------|-------|
| Bug Area | pebble |
| Bug Type | api-contract |
| Severity | medium |
| Fix Category | source-fix |

## Summary

pebble)!: change select=all to users=all for pebble get_notices

## Commit Message

Pebble added support for notices, aggregated events that are recorded with a type and key. The `/v1/notices` API had a parameter "select=all" to show notices for all users, and the parameter name is changed to "users=all" in recent [release v1.9.0](https://github.com/canonical/pebble/releases/tag/v1.9.0).

This PR is the corresponding changes to the ops framework.

Related doc: [OP042 - User ID features for Pebble Notices
](https://docs.google.com/document/d/1tQwUxz-rV-NjH-UodDbSDhGcMJGfD3OSoTnBLI9aoGU/edit#heading=h.kavgppauvkj5)

See here: https://github.com/canonical/operator/issues/1132

## Changed Files

- M	CHANGES.md
- M	ops/model.py
- M	ops/pebble.py
- M	ops/testing.py
- M	test/test_model.py
- M	test/test_pebble.py

## Diff

```diff
diff --git a/CHANGES.md b/CHANGES.md
index 6fd7d6c..e2d5768 100644
--- a/CHANGES.md
+++ b/CHANGES.md
@@ -1,3 +1,7 @@
+# 2.12.0
+
+* Updated Pebble Notices `get_notices` parameter name to `users=all` (previously `select=all`).
+
 # 2.11.0
 
 * `StopEvent`, `RemoveEvent`, and all `LifeCycleEvent`s are no longer deferrable, and will raise a `RuntimeError` if `defer()` is called on the event object.
diff --git a/ops/model.py b/ops/model.py
index 92eac06..c2a42b2 100644
--- a/ops/model.py
+++ b/ops/model.py
@@ -2757,7 +2757,7 @@ class Container:
     def get_notices(
         self,
         *,
-        select: Optional[pebble.NoticesSelect] = None,
+        users: Optional[pebble.NoticesUsers] = None,
         user_id: Optional[int] = None,
         types: Optional[Iterable[Union[pebble.NoticeType, str]]] = None,
         keys: Optional[Iterable[str]] = None,
@@ -2768,7 +2768,7 @@ class Container:
         parameters.
         """
         return self._pebble.get_notices(
-            select=select,
+            users=users,
             user_id=user_id,
             types=types,
             keys=keys,
diff --git a/ops/pebble.py b/ops/pebble.py
index 0b96d59..60bb9d7 100644
--- a/ops/pebble.py
+++ b/ops/pebble.py
@@ -1316,11 +1316,11 @@ class NoticeType(enum.Enum):
     CUSTOM = 'custom'
 
 
-class NoticesSelect(enum.Enum):
-    """Enum of :meth:`Client.get_notices` ``select`` values."""
+class NoticesUsers(enum.Enum):
+    """Enum of :meth:`Client.get_notices` ``users`` values."""
 
     ALL = 'all'
-    """Select notices from all users (any user ID, including public notices).
+    """Return notices from all users (any user ID, including public notices).
 
     This only works for Pebble admins (for example, root).
     """
@@ -2803,7 +2803,7 @@ class Client:
     def get_notices(
         self,
         *,
-        select: Optional[NoticesSelect] = None,
+        users: Optional[NoticesUsers] = None,
         user_id: Optional[int] = None,
         types: Optional[Iterable[Union[NoticeType, str]]] = None,
         keys: Optional[Iterable[str]] = None,
@@ -2824,7 +2824,7 @@ class Client:
         type has nanosecond precision).
 
         Args:
-            select: Select which notices to return (instead of returning
+            users: Change which users' notices to return (instead of returning
                 notices for the current user).
             user_id: Filter for notices for the specified user, including
                 public notices (only works for Pebble admins).
@@ -2832,8 +2832,8 @@ class Client:
             keys: Filter for notices with any of the specified keys.
         """
         query: Dict[str, Union[str, List[str]]] = {}
-        if select is not None:
-            query['select'] = select.value
+        if users is not None:
+            query['users'] = users.value
         if user_id is not None:
             query['user-id'] = str(user_id)
         if types is not None:
diff --git a/ops/testing.py b/ops/testing.py
index 3bb040f..d8e821d 100644
--- a/ops/testing.py
+++ b/ops/testing.py
@@ -3361,7 +3361,7 @@ class _TestingPebbleClient:
     def get_notices(
         self,
         *,
-        select: Optional[pebble.NoticesSelect] = None,
+        users: Optional[pebble.NoticesUsers] = None,
         user_id: Optional[int] = None,
         types: Optional[Iterable[Union[pebble.NoticeType, str]]] = None,
         keys: Optional[Iterable[str]] = None,
@@ -3371,9 +3371,9 @@ class _TestingPebbleClient:
         filter_user_id = 0  # default is to filter by request UID (root)
         if user_id is not None:
             filter_user_id = user_id
-        if select is not None:
+        if users is not None:
             if user_id is not None:
-                raise self._api_error(400, 'cannot use both "select" and "user_id"')
+                raise self._api_error(400, 'cannot use both "users" and "user_id"')
             filter_user_id = None
 
         if types is not None:
diff --git a/test/test_model.py b/test/test_model.py
index 588b3e2..9155217 100644
--- a/test/test_model.py
+++ b/test/test_model.py
@@ -1977,7 +1977,7 @@ containers:
 
         notices = self.container.get_notices(
             user_id=1000,
-            select=pebble.NoticesSelect.ALL,
+            users=pebble.NoticesUsers.ALL,
             types=[pebble.NoticeType.CUSTOM],
             keys=['example.com/a', 'example.com/b'],
         )
@@ -1988,7 +1988,7 @@ containers:
 
         self.assertEqual(self.pebble.requests, [('get_notices', dict(
             user_id=1000,
-            select=pebble.NoticesSelect.ALL,
+            users=pebble.NoticesUsers.ALL,
             types=[pebble.NoticeType.CUSTOM],
             keys=['example.com/a', 'example.com/b'],
         ))])
diff --git a/test/test_pebble.py b/test/test_pebble.py
index 7c7f429..ccd96d0 100644
--- a/test/test_pebble.py
+++ b/test/test_pebble.py
@@ -3032,7 +3032,7 @@ bad path\r
 
         notices = self.client.get_notices(
             user_id=1000,
-            select=pebble.NoticesSelect.ALL,
+            users=pebble.NoticesUsers.ALL,
             types=[pebble.NoticeType.CUSTOM],
             keys=['example.com/a', 'example.com/b'],
         )
@@ -3042,7 +3042,7 @@ bad path\r
 
         query = {
             'user-id': '1000',
-            'select': 'all',
+            'users': 'all',
             'types': ['custom'],
             'keys': ['example.com/a', 'example.com/b'],
         }
```
