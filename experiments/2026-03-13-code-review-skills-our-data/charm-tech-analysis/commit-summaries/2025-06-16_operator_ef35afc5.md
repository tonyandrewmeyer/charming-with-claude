# fix: do not return current unit in a mocked peer relation (#1828)

**Repository**: operator
**Commit**: [ef35afc5](https://github.com/canonical/operator/commit/ef35afc5824e74ccd58aac24b26072f63ea578a7)
**Date**: 2025-06-16

## Classification

| Field | Value |
|-------|-------|
| Bug Area | relation-data |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | test-fix |

## Summary

do not return current unit in a mocked peer relation

## Commit Message

This PR filters out the current unit from being returned by Scenario in
the case of a peer relation, to align with Juju's behaviour. A follow up PR
will fix the underlying buggy behaviour that leads to Scenario's peer
relations dict being populated with an entry for the current unit.

## Changed Files

- M	testing/src/scenario/mocking.py
- M	testing/tests/test_e2e/test_relations.py

## Diff

```diff
diff --git a/testing/src/scenario/mocking.py b/testing/src/scenario/mocking.py
index d3bbe19..f731546 100644
--- a/testing/src/scenario/mocking.py
+++ b/testing/src/scenario/mocking.py
@@ -294,7 +294,12 @@ class _MockModelBackend(_ModelBackend):  # type: ignore
         relation = self._get_relation_by_id(relation_id)
 
         if isinstance(relation, PeerRelation):
-            return tuple(f'{self.app_name}/{unit_id}' for unit_id in relation.peers_data)
+            this_unit = int(self.unit_name.split('/')[-1])
+            return tuple(
+                f'{self.app_name}/{unit_id}'
+                for unit_id in relation.peers_data
+                if unit_id != this_unit
+            )
         remote_name = self.relation_remote_app_name(relation_id)
         return tuple(f'{remote_name}/{unit_id}' for unit_id in relation._remote_unit_ids)
 
diff --git a/testing/tests/test_e2e/test_relations.py b/testing/tests/test_e2e/test_relations.py
index a33be02..f9491f8 100644
--- a/testing/tests/test_e2e/test_relations.py
+++ b/testing/tests/test_e2e/test_relations.py
@@ -738,3 +738,33 @@ def test_relation_remote_model():
         mgr.run()
         assert mgr.charm.remote_model_uuid == 'UUID'
         assert mgr.charm.remote_model_uuid != mgr.charm.model.uuid
+
+
+def test_peer_relation_units_does_not_contain_this_unit():
+    relation_name = 'relation-name'
+
+    class Charm(CharmBase):
+        def __init__(self, framework: Framework):
+            super().__init__(framework)
+            framework.observe(self.on.update_status, self._update_status)
+
+        def _update_status(self, _: EventBase):
+            rel = self.model.get_relation(relation_name)
+            assert rel is not None
+            assert self.unit not in rel.units
+            data = rel.data[self.unit]
+            data['this-unit'] = str(self.unit)
+
+    ctx = Context(
+        Charm,
+        meta={
+            'name': 'charm-name',
+            'peers': {relation_name: {'interface': 'interface-name'}},
+        },
+    )
+    rel_in = PeerRelation(
+        endpoint=relation_name,
+    )
+    state = ctx.run(ctx.on.update_status(), State(relations={rel_in}))
+    rel_out = state.get_relation(rel_in.id)
+    assert rel_out.local_unit_data.get('this-unit') == '<ops.model.Unit charm-name/0>'
```
