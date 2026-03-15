# fix!: return data rather than raising an exception on status-error (#120)

**Repository**: jubilant
**Commit**: [ae4efad6](https://github.com/canonical/jubilant/commit/ae4efad620e39b25b03d1f495a2c469b99d7c3ce)
**Date**: 2025-04-24T14:44:34+12:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | status-checking |
| Bug Type | error-handling |
| Severity | high |
| Fix Category | source-fix |

## Summary

StatusError exceptions on transient machine setup states crashed juju.wait() instead of allowing retry

## Commit Message

Juju can return the funky `{"status-error": ...}` object as a machine
status when a machine is still being set up. This causes the current
Jubilant code to raise `StatusError` and fail the test right away. This
is not what we want -- we just want `juju.wait()` to wait till the
machine has been set up and wait for the status they're looking for,
without raising an exception.

We set the status to "failed", which is a [valid Juju status
string](https://github.com/juju/juju/blob/5634dd4869129e1bf87e14afb586a28e97078729/core/status/status.go#L109),
but unlikely to ever be tested in integration tests. In particular, we
don't to use "error", which might need to be distinguished in
integration tests, and if people are using `Juju.wait` with
`error=jubilant.any_error`, will raise errors -- which we don't want for
transient failures like this where Juju is (say) setting up a machine.

Here's an [example
traceback](https://github.com/canonical/kafka-bundle/actions/runs/14587903350/job/40916796622#step:7:2367)
that shows this:

```
...
   File "/home/runner/work/kafka-bundle/kafka-bundle/tests/integration/e2e/test_backup.py", line 173, in test_new_cluster_migration
    juju.wait(lambda status: status.apps["new-zk"].is_active, timeout=3600, delay=10)
  File "/home/runner/work/kafka-bundle/kafka-bundle/.tox/integration-e2e-backup/lib/python3.10/site-packages/jubilant/_juju.py", line 830, in wait
    status = Status._from_dict(result)
  File "/home/runner/work/kafka-bundle/kafka-bundle/.tox/integration-e2e-backup/lib/python3.10/site-packages/jubilant/statustypes.py", line 720, in _from_dict
    machines={k: MachineStatus._from_dict(v) for k, v in d['machines'].items()},
  File "/home/runner/work/kafka-bundle/kafka-bundle/.tox/integration-e2e-backup/lib/python3.10/site-packages/jubilant/statustypes.py", line 720, in <dictcomp>
    machines={k: MachineStatus._from_dict(v) for k, v in d['machines'].items()},
  File "/home/runner/work/kafka-bundle/kafka-bundle/.tox/integration-e2e-backup/lib/python3.10/site-packages/jubilant/statustypes.py", line 570, in _from_dict
    StatusInfo._from_dict(d['juju-status']) if 'juju-status' in d else StatusInfo()
  File "/home/runner/work/kafka-bundle/kafka-bundle/.tox/integration-e2e-backup/lib/python3.10/site-packages/jubilant/statustypes.py", line 69, in _from_dict
    raise StatusError(d['status-error'])
jubilant.statustypes.StatusError: cannot get status: machine not found
```

I believe the issue Iman pointed out regarding checking `"my-app" in
status.apps` first is a red herring. This PR will solve the actual issue
of the `StatusError` being raised sometimes, presumably before Juju has
created the machine, and the `wait` will work as expected.

Fixes #118.

## Changed Files

- M	jubilant/statustypes.py
- A	tests/unit/test_statustypes.py

## Diff

```diff
diff --git a/jubilant/statustypes.py b/jubilant/statustypes.py
index 08bcdc0..3f692ed 100644
--- a/jubilant/statustypes.py
+++ b/jubilant/statustypes.py
@@ -25,7 +25,6 @@ __all__ = [
     'RemoteAppStatus',
     'RemoteEndpoint',
     'Status',
-    'StatusError',
     'StatusInfo',
     'StorageAttachments',
     'StorageInfo',
@@ -37,10 +36,6 @@ __all__ = [
 ]
 
 
-class StatusError(Exception):
-    """Raised when ``juju status`` returns a status-error for certain types."""
-
-
 @dataclasses.dataclass(frozen=True)
 class FormattedBase:
     name: str
@@ -66,7 +61,7 @@ class StatusInfo:
     @classmethod
     def _from_dict(cls, d: dict[str, Any]) -> StatusInfo:
         if 'status-error' in d:
-            raise StatusError(d['status-error'])
+            return cls(current='failed', message=d['status-error'])
         return cls(
             current=d.get('current') or '',
             message=d.get('message') or '',
@@ -108,7 +103,10 @@ class UnitStatus:
     @classmethod
     def _from_dict(cls, d: dict[str, Any]) -> UnitStatus:
         if 'status-error' in d:
-            raise StatusError(d['status-error'])
+            return cls(
+                workload_status=StatusInfo(current='failed', message=d['status-error']),
+                juju_status=StatusInfo(current='failed', message=d['status-error']),
+            )
         return cls(
             workload_status=(
                 StatusInfo._from_dict(d['workload-status'])
@@ -185,7 +183,14 @@ class AppStatus:
     @classmethod
     def _from_dict(cls, d: dict[str, Any]) -> AppStatus:
         if 'status-error' in d:
-            raise StatusError(d['status-error'])
+            return cls(
+                charm='<failed>',
+                charm_origin='<failed>',
+                charm_name='<failed>',
+                charm_rev=-1,
+                exposed=False,
+                app_status=StatusInfo(current='failed', message=d['status-error']),
+            )
         return cls(
             charm=d['charm'],
             charm_origin=d['charm-origin'],
@@ -564,7 +569,10 @@ class MachineStatus:
     @classmethod
     def _from_dict(cls, d: dict[str, Any]) -> MachineStatus:
         if 'status-error' in d:
-            raise StatusError(d['status-error'])
+            return cls(
+                juju_status=StatusInfo(current='failed', message=d['status-error']),
+                machine_status=StatusInfo(current='failed', message=d['status-error']),
+            )
         return cls(
             juju_status=(
                 StatusInfo._from_dict(d['juju-status']) if 'juju-status' in d else StatusInfo()
@@ -660,7 +668,7 @@ class OfferStatus:
     @classmethod
     def _from_dict(cls, d: dict[str, Any]) -> OfferStatus:
         if 'status-error' in d:
-            raise StatusError(d['status-error'])
+            return cls(app=f'<failed> ({d["status-error"]})', endpoints={})
         return cls(
             app=d['application'],
             endpoints={k: RemoteEndpoint._from_dict(v) for k, v in d['endpoints'].items()},
@@ -682,7 +690,10 @@ class RemoteAppStatus:
     @classmethod
     def _from_dict(cls, d: dict[str, Any]) -> RemoteAppStatus:
         if 'status-error' in d:
-            raise StatusError(d['status-error'])
+            return cls(
+                url='<failed>',
+                app_status=StatusInfo(current='failed', message=d['status-error']),
+            )
         return cls(
             url=d['url'],
             endpoints=(
diff --git a/tests/unit/test_statustypes.py b/tests/unit/test_statustypes.py
new file mode 100644
index 0000000..8bea284
--- /dev/null
+++ b/tests/unit/test_statustypes.py
@@ -0,0 +1,92 @@
+import json
+
+import jubilant
+
+STATUS_ERRORS_JSON = """
+{
+    "model": {
+        "name": "tt",
+        "type": "caas",
+        "controller": "microk8s-localhost",
+        "cloud": "microk8s",
+        "version": "3.6.1",
+        "model-status": {
+            "status-error": "model status error!"
+        }
+    },
+    "machines": {
+        "machine-failed": {
+            "status-error": "machine status error!"
+        }
+    },
+    "applications": {
+        "app-failed": {
+            "status-error": "app status error!"
+        },
+        "unit-failed": {
+            "charm": "unit-failed",
+            "charm-origin": "origin",
+            "charm-name": "unit-failed",
+            "charm-rev": 0,
+            "exposed": false,
+            "units": {
+                "unit-failed/0": {
+                    "status-error": "unit status error!"
+                }
+            }
+        }
+    },
+    "offers": {
+        "offer-failed": {
+            "status-error": "offer status error!"
+        }
+    },
+    "application-endpoints": {
+        "remote-app-failed": {
+            "status-error": "remote app status error!"
+        }
+    }
+}
+"""
+
+
+def test_juju_status_error():
+    status = jubilant.Status._from_dict(json.loads(STATUS_ERRORS_JSON))
+    assert status.model.model_status == jubilant.statustypes.StatusInfo(
+        current='failed',
+        message='model status error!',
+    )
+    assert status.apps['app-failed'] == jubilant.statustypes.AppStatus(
+        charm='<failed>',
+        charm_origin='<failed>',
+        charm_name='<failed>',
+        charm_rev=-1,
+        exposed=False,
+        app_status=jubilant.statustypes.StatusInfo(current='failed', message='app status error!'),
+    )
+    assert status.apps['unit-failed'].units['unit-failed/0'] == jubilant.statustypes.UnitStatus(
+        workload_status=jubilant.statustypes.StatusInfo(
+            current='failed', message='unit status error!'
+        ),
+        juju_status=jubilant.statustypes.StatusInfo(
+            current='failed', message='unit status error!'
+        ),
+    )
+    assert status.machines['machine-failed'] == jubilant.statustypes.MachineStatus(
+        machine_status=jubilant.statustypes.StatusInfo(
+            current='failed', message='machine status error!'
+        ),
+        juju_status=jubilant.statustypes.StatusInfo(
+            current='failed', message='machine status error!'
+        ),
+    )
+    assert status.offers['offer-failed'] == jubilant.statustypes.OfferStatus(
+        app='<failed> (offer status error!)',
+        endpoints={},
+    )
+    assert status.app_endpoints['remote-app-failed'] == jubilant.statustypes.RemoteAppStatus(
+        url='<failed>',
+        app_status=jubilant.statustypes.StatusInfo(
+            current='failed', message='remote app status error!'
+        ),
+    )
```
