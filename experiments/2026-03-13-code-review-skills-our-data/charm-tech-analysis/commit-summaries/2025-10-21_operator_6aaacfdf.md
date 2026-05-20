# fix: raise ActionFailed when using Context as a context manager (#2121)

**Repository**: operator
**Commit**: [6aaacfdf](https://github.com/canonical/operator/commit/6aaacfdf7322ccc258c6fcdf19d74a3b3e25ade4)
**Date**: 2025-10-21

## Classification

| Field | Value |
|-------|-------|
| Bug Area | error-handling |
| Bug Type | exception-type |
| Severity | medium |
| Fix Category | test-fix |

## Summary

raise actionfailed when using context as a context manager

## Commit Message

This PR ensures that `ActionFailed` is raised both when using
`Context.run()` directly, and when it is used as a context manager, by
moving the relevant code to a method common to both techniques.

To reproduce the issue, start with this setup:

```python
>>> from ops import testing
>>> import ops
>>> class C(ops.CharmBase):
...     def __init__(self, framework):
...         super().__init__(framework)
...         framework.observe(self.on['act'].action, self._on_act)
...     def _on_act(self, event):
...         event.fail("Failed")
...         
```

With a regular run, when an action fails, `ActionFailed` is raised. This
is the expected behaviour:

```python
>>> ctx = testing.Context(C, meta={'name': 'foo'}, actions={'act': {}})
>>> ctx.run(ctx.on.action('act'), testing.State())
Traceback (most recent call last):
  File "<python-input-5>", line 1, in <module>
    ctx.run(ctx.on.action('act'), testing.State())
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/tameyer/w/operator/testing/src/scenario/context.py", line 830, in run
    raise ActionFailed(
    ...<2 lines>...
    )
ops._private.harness.ActionFailed: Failed
```

However, when using `Context` as a context manager, it is not:

```python
>>> with ctx(ctx.on.action('act'), testing.State()) as mgr:
...     mgr.run()
...     
State(config={}, relations=frozenset(), networks=frozenset(), containers=frozenset(), storages=frozenset(), opened_ports=frozenset(), leader=False, model=Model(name='dETzC56WsRPvSb3pDPY8', uuid='912539dd-57d4-453d-9e90-166d04fef696', type='kubernetes', cloud_spec=None), secrets=frozenset(), resources=frozenset(), planned_units=1, deferred=[], stored_states=frozenset({StoredState(name='_stored', owner_path=None, content={'event_count': 4}, _data_type_name='StoredStateData')}), app_status=UnknownStatus(), unit_status=UnknownStatus(), workload_version='')
```

The issue here is that `Manager.run()` and `Context.run()` use
`Context._run()` to call `ops.run()` (too many "run"s!), but the code
that handles raising `ActionFailed` (and setting the logs and action
messages) is only in `Context.run()`.

---------

Co-authored-by: James Garner <james.garner@canonical.com>

## Changed Files

- M	testing/src/scenario/context.py
- M	testing/tests/test_e2e/test_actions.py

## Diff

```diff
diff --git a/testing/src/scenario/context.py b/testing/src/scenario/context.py
index fd68c2c..71cf175 100644
--- a/testing/src/scenario/context.py
+++ b/testing/src/scenario/context.py
@@ -813,24 +813,11 @@ class Context(Generic[CharmType]):
                 'You should call the event method. Did you forget to add parentheses?',
             )
 
-        if event.action:
-            # Reset the logs, failure status, and results, in case the context
-            # is reused.
-            self.action_logs.clear()
-            if self.action_results is not None:
-                self.action_results.clear()
-            self._action_failure_message = None
         with self._run(event=event, state=state) as ops:
             ops.run()
         # We know that the output state will have been set by this point,
         # so let the type checkers know that too.
         assert self._output_state is not None
-        if event.action:
-            if self._action_failure_message is not None:
-                raise ActionFailed(
-                    self._action_failure_message,
-                    state=self._output_state,  # type: ignore
-                )
         return self._output_state
 
     @contextmanager
@@ -843,9 +830,23 @@ class Context(Generic[CharmType]):
             unit_id=self.unit_id,
             machine_id=self._machine_id,
         )
+        if event.action:
+            # Reset the logs, failure status, and results, in case the context
+            # is reused.
+            self.action_logs.clear()
+            if self.action_results is not None:
+                self.action_results.clear()
+            self._action_failure_message = None
+
         with runtime.exec(
             state=state,
             event=event,
-            context=self,  # type: ignore
+            context=self,
         ) as ops:
             yield ops
+
+        if event.action and self._action_failure_message is not None:
+            raise ActionFailed(
+                self._action_failure_message,
+                state=self._output_state,  # type: ignore
+            )
diff --git a/testing/tests/test_e2e/test_actions.py b/testing/tests/test_e2e/test_actions.py
index bd45cb4..40d65fc 100644
--- a/testing/tests/test_e2e/test_actions.py
+++ b/testing/tests/test_e2e/test_actions.py
@@ -109,6 +109,35 @@ def test_action_event_outputs(mycharm, res_value):
     assert ctx.action_logs == ['log1', 'log2']
 
 
+def test_action_event_fail(mycharm):
+    def handle_evt(_: CharmBase, evt: ActionEvent):
+        if not isinstance(evt, ActionEvent):
+            return
+        evt.fail('action failed!')
+
+    mycharm._evt_handler = handle_evt
+
+    ctx = Context(mycharm, meta={'name': 'foo'}, actions={'foo': {}})
+    with pytest.raises(ActionFailed) as exc_info:
+        ctx.run(ctx.on.action('foo'), State())
+    assert exc_info.value.message == 'action failed!'
+
+
+def test_action_event_fail_context_manager(mycharm):
+    def handle_evt(_: CharmBase, evt: ActionEvent):
+        if not isinstance(evt, ActionEvent):
+            return
+        evt.fail('action failed!')
+
+    mycharm._evt_handler = handle_evt
+
+    ctx = Context(mycharm, meta={'name': 'foo'}, actions={'foo': {}})
+    with pytest.raises(ActionFailed) as exc_info:
+        with ctx(ctx.on.action('foo'), State()):
+            assert False, 'ActionFailed should be raised in the context manager.'
+    assert exc_info.value.message == 'action failed!'
+
+
 def test_action_continues_after_fail():
     class MyCharm(CharmBase):
         def __init__(self, framework):
```
