# fix: assorted fixes for Pebble layer merging in Harness and Scenario (#1627)

**Repository**: operator
**Commit**: [3dda5b5f](https://github.com/canonical/operator/commit/3dda5b5f64bdea21d43a42431edcca62669c3173)
**Date**: 2025-03-14

## Classification

| Field | Value |
|-------|-------|
| Bug Area | pebble |
| Bug Type | mutability |
| Severity | high |
| Fix Category | source-fix |

## Summary

assorted fixes for pebble layer merging in harness and scenario

## Commit Message

* When merging `pebble.Check`s, an unset `startup` should not override a
set `startup`. (Once set you can't go back to unset - you need to
explicitly use enabled).
* When rendering services, checks, and log targets from a series of
layers, Harness and Scenario were combining after sorting the items by
name. Although Pebble uses filename sorting when reading initial layers
from a directory, future layers are combined in the order they are added
via the API. For Harness and Scenario, we need to use the order in which
they were added - if the caller wants to simulate loading from the
filesystem, they need to do that by calling `add_layer` in that order.
The plan itself still sorts the services, checks, and log targets.
* When rendering services, checks, and log targets, if there are
multiple services/checks/log-targets with the same name, and `override`
is set to `merge`, the service/check/log-target needs to merge rather
than replace. This was already done when adding layers with the same
name (in `add_layer`) but not when there were differently named layers.
* The Scenario `Container.plan` property was ignoring any defined checks
and log targets. Those are now included.
* The Scenario `Container` service, check, and log target rendering also
needed the (no) sorting and merging fixes from above.
* When adding a layer in Harness or Scenario, update any existing
`CheckInfo`s to match changes to the plan - in real Pebble the startup,
level, and threshold fields are always pulled from the plan but we bake
them in when testing, so need to make sure they continually track what's
in the combined plan.

Also adds a `__repr__` for `pebble.Plan` - this helped while debugging
issues, and it seems reasonable to keep it.

---------

Co-authored-by: Ben Hoyt <benhoyt@gmail.com>

## Changed Files

- M	ops/_private/harness.py
- M	ops/pebble.py
- M	test/test_pebble.py
- M	test/test_testing.py
- M	testing/src/scenario/state.py
- M	testing/tests/test_e2e/test_pebble.py

## Diff

```diff
diff --git a/ops/_private/harness.py b/ops/_private/harness.py
index bcf7a5f..9bb57a7 100644
--- a/ops/_private/harness.py
+++ b/ops/_private/harness.py
@@ -41,6 +41,7 @@ from typing import (
     Callable,
     ClassVar,
     Dict,
+    Final,
     Generic,
     Iterable,
     List,
@@ -3106,6 +3107,8 @@ class _TestingPebbleClient:
     as the only public methods of this type are for implementing Client.
     """
 
+    _DEFAULT_CHECK_THRESHOLD: Final[int] = 3
+
     def __init__(self, backend: _TestingModelBackend, container_root: pathlib.Path):
         self._backend = _TestingModelBackend
         self._layers: Dict[str, pebble.Layer] = {}
@@ -3200,12 +3203,15 @@ class _TestingPebbleClient:
                 continue
             info = self._check_infos.get(name)
             if info is None:
+                threshold = (
+                    self._DEFAULT_CHECK_THRESHOLD if check.threshold is None else check.threshold
+                )
                 info = pebble.CheckInfo(
                     name=name,
                     level=check.level,
                     status=pebble.CheckStatus.UP,
                     failures=0,
-                    threshold=3 if check.threshold is None else check.threshold,
+                    threshold=threshold,
                     startup=check.startup,
                 )
                 self._check_infos[name] = info
@@ -3318,6 +3324,20 @@ class _TestingPebbleClient:
     ) -> pebble.Change:
         raise NotImplementedError(self.wait_change)
 
+    def _update_check_infos_from_plan(self):
+        # In testing, the check info has the level, threshold, and startup
+        # from the check baked in, so we need to update the info when the plan
+        # changes.
+        for check in self.get_plan().checks.values():
+            info = self._check_infos.get(check.name)
+            if not info:
+                continue
+            info.level = check.level
+            info.threshold = (
+                self._DEFAULT_CHECK_THRESHOLD if check.threshold is None else check.threshold
+            )
+            info.startup = check.startup
+
     def add_layer(
         self,
         label: str,
@@ -3418,42 +3438,58 @@ class _TestingPebbleClient:
                     if check.startup == pebble.CheckStartup.DISABLED
                     else pebble.CheckStatus.UP
                 )
+                threshold = (
+                    self._DEFAULT_CHECK_THRESHOLD if check.threshold is None else check.threshold
+                )
                 info = pebble.CheckInfo(
                     name,
                     level=check.level,
+                    startup=check.startup,
                     status=status,
+                    threshold=threshold,
                     failures=0,
                     change_id=pebble.ChangeID(''),
                 )
                 self._check_infos[name] = info
-            info.level = check.level
-            info.threshold = 3 if check.threshold is None else check.threshold
-            info.startup = check.startup
             if info.startup != pebble.CheckStartup.DISABLED and not info.change_id:
                 self._new_perform_check(info)
+        self._update_check_infos_from_plan()
 
     def _render_services(self) -> Dict[str, pebble.Service]:
         services: Dict[str, pebble.Service] = {}
-        for key in sorted(self._layers.keys()):
-            layer = self._layers[key]
+        # Note that this must done in the order that the layers were added to
+        # the dictionary, *not* sorted. If Pebble loads the layers from a
+        # directory on startup, then the order of the checks is alphabetical
+        # using the 001 style prefix. However, when adding layers via the API,
+        # the order is the order in which the API calls were made. If using this
+        # testing class to simulate the former, then care must be taken to run
+        # the add_layer calls in alphabetical (by filename) order.
+        for layer in self._layers.values():
             for name, service in layer.services.items():
-                services[name] = service
+                if name in services and service.override == 'merge':
+                    services[name]._merge(service)
+                else:
+                    services[name] = service
         return services
 
     def _render_checks(self) -> Dict[str, pebble.Check]:
         checks: Dict[str, pebble.Check] = {}
-        for key in sorted(self._layers.keys()):
-            layer = self._layers[key]
+        for layer in self._layers.values():
             for name, check in layer.checks.items():
-                checks[name] = check
+                if name in checks and check.override == 'merge':
+                    checks[name]._merge(check)
+                else:
+                    checks[name] = check
         return checks
 
     def _render_log_targets(self) -> Dict[str, pebble.LogTarget]:
         log_targets: Dict[str, pebble.LogTarget] = {}
-        for key in sorted(self._layers.keys()):
-            layer = self._layers[key]
+        for layer in self._layers.values():
             for name, log_target in layer.log_targets.items():
-                log_targets[name] = log_target
+                if name in log_targets and log_target.override == 'merge':
+                    log_targets[name]._merge(log_target)
+                else:
+                    log_targets[name] = log_target
         return log_targets
 
     def get_plan(self) -> pebble.Plan:
diff --git a/ops/pebble.py b/ops/pebble.py
index 460832f..0cf2c67 100644
--- a/ops/pebble.py
+++ b/ops/pebble.py
@@ -876,6 +876,9 @@ class Plan:
 
     __str__ = to_yaml
 
+    def __repr__(self):
+        return f'Plan({self.to_dict()!r})'
+
     def __eq__(self, other: Union[PlanDict, Plan]) -> bool:
         if isinstance(other, dict):
             return self.to_dict() == other
@@ -1210,6 +1213,9 @@ class Check:
         attributes take precedence.
         """
         for name, value in other.__dict__.items():
+            # 'not value' is safe here because a threshold of 0 is valid but
+            # inconsistently applied and not of any actual use, and the other
+            # fields are strings where the empty string means 'not in the layer'.
             if not value or name == 'name':
                 continue
             if name == 'http':
@@ -1218,6 +1224,11 @@ class Check:
                 self._merge_tcp(value)
             elif name == 'exec':
                 self._merge_exec(value)
+            elif name == 'startup' and value == CheckStartup.UNSET:
+                continue
+            # Note that CheckLevel.UNSET has a different meaning to
+            # CheckStartup.UNSET. In the former, it means 'there is no level';
+            # in the latter it means 'use the default'.
             else:
                 setattr(self, name, value)
 
diff --git a/test/test_pebble.py b/test/test_pebble.py
index e7cdc20..62d1e3c 100644
--- a/test/test_pebble.py
+++ b/test/test_pebble.py
@@ -1063,6 +1063,7 @@ class TestCheck:
         assert check.name == name
         assert check.override == ''
         assert check.level == pebble.CheckLevel.UNSET
+        assert check.startup == pebble.CheckStartup.UNSET
         assert check.period == ''
         assert check.timeout == ''
         assert check.threshold is None
@@ -1078,6 +1079,7 @@ class TestCheck:
         d: pebble.CheckDict = {
             'override': 'replace',
             'level': 'alive',
+            'startup': 'enabled',
             'period': '10s',
             'timeout': '3s',
             'threshold': 5,
@@ -1091,6 +1093,7 @@ class TestCheck:
         assert check.name == 'chk-http'
         assert check.override == 'replace'
         assert check.level == pebble.CheckLevel.ALIVE
+        assert check.startup == pebble.CheckStartup.ENABLED
         assert check.period == '10s'
         assert check.timeout == '3s'
         assert check.threshold == 5
@@ -1139,7 +1142,6 @@ class TestCheck:
         assert two == two.to_dict()
         d['level'] = 'ready'
         assert one != d
-
         assert one != 5
 
 
diff --git a/test/test_testing.py b/test/test_testing.py
index 9f370a2..8685802 100644
--- a/test/test_testing.py
+++ b/test/test_testing.py
@@ -7119,6 +7119,178 @@ class TestChecks:
             assert info.status == pebble.CheckStatus.UP
             assert info.change_id, 'Change ID should not be None or the empty string'
 
+    @pytest.mark.parametrize(
+        'combine,new_layer_name',
+        [
+            (False, 'new-layer'),
+            (True, 'base'),
+            # This doesn't have anything to combine with, but for completeness:
+            (True, 'new-layer'),
+        ],
+    )
+    @pytest.mark.parametrize(
+        'new_layer_dict',
+        [
+            {
+                'checks': {
+                    'server-ready': {
+                        'override': 'merge',
+                        'level': 'ready',
+                        'http': {'url': 'http://localhost:5050/version'},
+                    }
+                }
+            },
+            {
+                'checks': {
+                    'server-ready': {
+                        'override': 'merge',
+                        'level': 'alive',
+                        'threshold': 30,
+                        'startup': 'disabled',
+                        'http': {'url': 'http://localhost:5050/version'},
+                    }
+                }
+            },
+        ],
+    )
+    def test_add_layer_merge_check(
+        self,
+        request: pytest.FixtureRequest,
+        new_layer_name: str,
+        combine: bool,
+        new_layer_dict: ops.pebble.LayerDict,
+    ):
+        class MyCharm(ops.CharmBase):
+            def __init__(self, framework: ops.Framework):
+                super().__init__(framework)
+                framework.observe(self.on['my-container'].pebble_ready, self._on_pebble_ready)
+
+  
... [truncated]
```
