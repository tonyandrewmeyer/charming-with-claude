# ulterior fix

**Repository**: operator
**Commit**: [de641eca](https://github.com/canonical/operator/commit/de641ecaeae225233b4782e6e37916262476804e)
**Date**: 2024-07-31

## Classification

| Field | Value |
|-------|-------|
| Bug Area | testing-framework |
| Bug Type | logic-error |
| Severity | medium |
| Fix Category | source-fix |

## Summary

ulterior fix

## Changed Files

- M	pyproject.toml
- M	scenario/consistency_checker.py
- M	tests/test_e2e/test_network.py

## Diff

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 0d16c44..f83a101 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -8,7 +8,7 @@ build-backend = "setuptools.build_meta"
 [project]
 name = "ops-scenario"
 
-version = "6.1.4"
+version = "6.1.5"
 
 authors = [
     { name = "Pietro Pasotti", email = "pietro.pasotti@canonical.com" }
diff --git a/scenario/consistency_checker.py b/scenario/consistency_checker.py
index c4397ef..895e6f8 100644
--- a/scenario/consistency_checker.py
+++ b/scenario/consistency_checker.py
@@ -429,7 +429,7 @@ def check_network_consistency(
     meta_bindings = set(charm_spec.meta.get("extra-bindings", ()))
     # add the implicit juju-info binding so we can override its network without
     # having to declare a relation for it in metadata
-    meta_bindings.add("juju-info")
+    implicit_bindings = {"juju-info"}
     all_relations = charm_spec.get_all_relations()
     non_sub_relations = {
         endpoint
@@ -438,7 +438,9 @@ def check_network_consistency(
     }
 
     state_bindings = set(state.networks)
-    if diff := state_bindings.difference(meta_bindings.union(non_sub_relations)):
+    if diff := state_bindings.difference(
+        meta_bindings.union(non_sub_relations).union(implicit_bindings),
+    ):
         errors.append(
             f"Some network bindings defined in State are not in metadata.yaml: {diff}.",
         )
diff --git a/tests/test_e2e/test_network.py b/tests/test_e2e/test_network.py
index 0722347..28a4133 100644
--- a/tests/test_e2e/test_network.py
+++ b/tests/test_e2e/test_network.py
@@ -154,3 +154,20 @@ def test_juju_info_network_override(mycharm):
             str(mgr.charm.model.get_binding("juju-info").network.bind_address)
             == "4.4.4.4"
         )
+
+
+def test_explicit_juju_info_network_override(mycharm):
+    ctx = Context(
+        mycharm,
+        meta={
+            "name": "foo",
+            # this charm for whatever reason explicitly defines a juju-info endpoint
+            "requires": {"juju-info": {"interface": "juju-info"}},
+        },
+    )
+
+    with ctx.manager(
+        "update_status",
+        State(),
+    ) as mgr:
+        assert mgr.charm.model.get_binding("juju-info").network.bind_address
```
