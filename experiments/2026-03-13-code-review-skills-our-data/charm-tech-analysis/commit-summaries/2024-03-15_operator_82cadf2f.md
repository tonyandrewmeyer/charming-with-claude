# fix(model): change model.relation.app type from optional to mandatory (#1151)

**Repository**: operator
**Commit**: [82cadf2f](https://github.com/canonical/operator/commit/82cadf2f3717dfd01b80b22138344cf199453f3c)
**Date**: 2024-03-15

## Classification

| Field | Value |
|-------|-------|
| Bug Area | relation-data |
| Bug Type | type-error |
| Severity | high |
| Fix Category | source-fix |

## Summary

model): change model.relation.app type from optional to mandatory

## Commit Message

fix(model): change model.relation.app type from optional to mandatory

## Changed Files

- M	ops/model.py
- M	ops/testing.py

## Diff

```diff
diff --git a/ops/model.py b/ops/model.py
index c2a42b2..bc87b3b 100644
--- a/ops/model.py
+++ b/ops/model.py
@@ -1448,7 +1448,7 @@ class Relation:
     id: int
     """The identifier for a particular relation."""
 
-    app: Optional[Application]
+    app: Application
     """Represents the remote application of this relation.
 
     For peer relations, this will be the local application.
@@ -1478,32 +1478,32 @@ class Relation:
             backend: '_ModelBackend', cache: '_ModelCache', active: bool = True):
         self.name = relation_name
         self.id = relation_id
-        self.app: Optional[Application] = None
         self.units: Set[Unit] = set()
         self.active = active
 
-        if is_peer:
-            # For peer relations, both the remote and the local app are the same.
-            self.app = our_unit.app
+        # For peer relations, both the remote and the local app are the same.
+        app = our_unit.app if is_peer else None
 
         try:
             for unit_name in backend.relation_list(self.id):
                 unit = cache.get(Unit, unit_name)
                 self.units.add(unit)
-                if self.app is None:
+                if app is None:
                     # Use the app of one of the units if available.
-                    self.app = unit.app
+                    app = unit.app
         except RelationNotFoundError:
             # If the relation is dead, just treat it as if it has no remote units.
             self.active = False
 
         # If we didn't get the remote app via our_unit.app or the units list,
         # look it up via JUJU_REMOTE_APP or "relation-list --app".
-        if self.app is None:
+        if app is None:
             app_name = backend.relation_remote_app_name(relation_id)
             if app_name is not None:
-                self.app = cache.get(Application, app_name)
+                app = cache.get(Application, app_name)
 
+        # self.app will not be None and always be set because of the fallback mechanism above.
+        self.app = typing.cast(Application, app)
         self.data = RelationData(self, our_unit, backend)
 
     def __repr__(self):
diff --git a/ops/testing.py b/ops/testing.py
index d8e821d..9e144cb 100644
--- a/ops/testing.py
+++ b/ops/testing.py
@@ -958,7 +958,7 @@ class Harness(Generic[CharmType]):
                                'but no relation matching that name was found.')
 
         self._backend._relation_data_raw[relation_id][remote_unit_name] = {}
-        app = cast(model.Application, relation.app)  # should not be None since we're testing
+        app = relation.app
         if not remote_unit_name.startswith(app.name):
             warnings.warn(
                 'Remote unit name invalid: the remote application of {} is called {!r}; '
```
