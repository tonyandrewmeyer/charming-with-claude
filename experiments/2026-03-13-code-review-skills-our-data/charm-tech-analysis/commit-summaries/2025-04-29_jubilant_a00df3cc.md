# fix!: make "reset" an explicit arg for config/model_config (#125)

**Repository**: jubilant
**Commit**: [a00df3cc](https://github.com/canonical/jubilant/commit/a00df3ccc5194beed77761c71c30cba7c15e43b8)
**Date**: 2025-04-29T14:48:43+12:00

## Classification

| Field | Value |
|-------|-------|
| Bug Area | config |
| Bug Type | api-contract |
| Severity | medium |
| Fix Category | source-fix |

## Summary

Breaking API change: config reset via None values replaced with explicit 'reset' keyword argument

## Commit Message

This is per our API discussion, to make this a bit clearer/explicit, and
more like the Juju CLI.

I needed a third `@overlord` to make the reset-only option work.

## Changed Files

- M	jubilant/_juju.py
- M	tests/integration/test_config.py
- M	tests/unit/test_config.py
- M	tests/unit/test_model_config.py
- M	tests/unit/test_scp.py
- M	tests/unit/test_ssh.py

## Diff

```diff
diff --git a/jubilant/_juju.py b/jubilant/_juju.py
index 409b1b9..b02cb21 100644
--- a/jubilant/_juju.py
+++ b/jubilant/_juju.py
@@ -242,29 +242,40 @@ class Juju:
     def config(self, app: str, *, app_config: bool = False) -> Mapping[str, ConfigValue]: ...
 
     @overload
-    def config(self, app: str, values: Mapping[str, ConfigValue | None]) -> None: ...
+    def config(
+        self,
+        app: str,
+        values: Mapping[str, ConfigValue],
+        *,
+        reset: str | Iterable[str] = (),
+    ) -> None: ...
+
+    @overload
+    def config(self, app: str, *, reset: str | Iterable[str]) -> None: ...
 
     def config(
         self,
         app: str,
-        values: Mapping[str, ConfigValue | None] | None = None,
+        values: Mapping[str, ConfigValue] | None = None,
         *,
         app_config: bool = False,
+        reset: str | Iterable[str] = (),
     ) -> Mapping[str, ConfigValue] | None:
         """Get or set the configuration of a deployed application.
 
         If called with only the *app* argument, get the config and return it.
 
-        If called with the *values* argument, set the config values and return None.
-        For values in *values* that are None, reset them to their defaults.
+        If called with the *values* or *reset* arguments, set the config values and return None,
+        and reset any keys in *reset* to their defaults.
 
         Args:
             app: Application name to get or set config for.
-            values: Mapping of config names to values to set. Reset values that are None.
+            values: Mapping of config names to values to set.
             app_config: When getting config, set this to True to get the
                 (poorly-named) "application-config" values instead of charm config.
+            reset: Key or list of keys to reset to their defaults.
         """
-        if values is None:
+        if values is None and not reset:
             stdout = self.cli('config', '--format', 'json', app)
             outer = json.loads(stdout)
             inner = outer['application-config'] if app_config else outer['settings']
@@ -275,15 +286,13 @@ class Juju:
             }
             return result
 
-        reset: list[str] = []
         args = ['config', app]
-        for k, v in values.items():
-            if v is None:
-                reset.append(k)
-            else:
-                args.append(_format_config(k, v))
+        if values:
+            args.extend(_format_config(k, v) for k, v in values.items())
         if reset:
-            args.extend(['--reset', ','.join(reset)])
+            if not isinstance(reset, str):
+                reset = ','.join(reset)
+            args.extend(['--reset', reset])
 
         self.cli(*args)
 
@@ -526,36 +535,40 @@ class Juju:
     def model_config(self) -> Mapping[str, ConfigValue]: ...
 
     @overload
-    def model_config(self, values: Mapping[str, ConfigValue | None]) -> None: ...
+    def model_config(
+        self, values: Mapping[str, ConfigValue], *, reset: str | Iterable[str] = ()
+    ) -> None: ...
+
+    @overload
+    def model_config(self, *, reset: str | Iterable[str]) -> None: ...
 
     def model_config(
-        self, values: Mapping[str, ConfigValue | None] | None = None
+        self, values: Mapping[str, ConfigValue] | None = None, reset: str | Iterable[str] = ()
     ) -> Mapping[str, ConfigValue] | None:
         """Get or set the configuration of the model.
 
         If called with no arguments, get the model config and return it.
 
-        If called with the *values* argument, set the model config values and return None.
-        For values in *values* that are None, reset them to their defaults.
+        If called with the *values* or *reset* arguments, set the model config values and return
+        None, and reset any keys in *reset* to their defaults.
 
         Args:
             values: Mapping of model config names to values to set, for example
-                ``{'update-status-hook-interval': '10s'}``. Reset values that are None.
+                ``{'update-status-hook-interval': '10s'}``.
+            reset: Key or list of keys to reset to their defaults.
         """
-        if values is None:
+        if values is None and not reset:
             stdout = self.cli('model-config', '--format', 'json')
             result = json.loads(stdout)
             return {k: v['Value'] for k, v in result.items() if 'Value' in v}
 
-        reset: list[str] = []
         args = ['model-config']
-        for k, v in values.items():
-            if v is None:
-                reset.append(k)
-            else:
-                args.append(_format_config(k, v))
+        if values:
+            args.extend(_format_config(k, v) for k, v in values.items())
         if reset:
-            args.extend(['--reset', ','.join(reset)])
+            if not isinstance(reset, str):
+                reset = ','.join(reset)
+            args.extend(['--reset', reset])
 
         self.cli(*args)
 
@@ -808,6 +821,10 @@ class Juju:
             host_key_checks: Set to False to disable host key checking (insecure).
             scp_options: ``scp`` client options, for example ``['-r', '-C']``.
         """
+        # Need this check because str is also an iterable of str.
+        if isinstance(scp_options, str):
+            raise TypeError('scp_options must be an iterable of str, not str')
+
         args = ['scp']
         if container is not None:
             args.extend(['--container', container])
@@ -988,6 +1005,8 @@ class Juju:
 
 
 def _format_config(k: str, v: ConfigValue) -> str:
+    if v is None:  # type: ignore
+        raise TypeError(f'unexpected None value for config key {k!r}')
     if isinstance(v, bool):
         v = 'true' if v else 'false'
     return f'{k}={v}'
diff --git a/tests/integration/test_config.py b/tests/integration/test_config.py
index 704ddc0..00381cf 100644
--- a/tests/integration/test_config.py
+++ b/tests/integration/test_config.py
@@ -25,16 +25,19 @@ def test_config(juju: jubilant.Juju):
     config = juju.config('testdb')
     assert config['testoption'] == 'foobar'
 
+    juju.config('testdb', reset=['testoption'])
+    config = juju.config('testdb')
+    assert config['testoption'] == ''
+
 
 @contextlib.contextmanager
 def fast_forward(juju: jubilant.Juju):
     """Context manager that temporarily speeds up update-status hooks."""
-    old = juju.model_config()['update-status-hook-interval']
     juju.model_config({'update-status-hook-interval': '10s'})
     try:
         yield
     finally:
-        juju.model_config({'update-status-hook-interval': old})
+        juju.model_config(reset=['update-status-hook-interval'])
 
 
 def test_model_config(juju: jubilant.Juju):
diff --git a/tests/unit/test_config.py b/tests/unit/test_config.py
index 300bd98..2c159c1 100644
--- a/tests/unit/test_config.py
+++ b/tests/unit/test_config.py
@@ -1,3 +1,5 @@
+import pytest
+
 import jubilant
 
 from . import mocks
@@ -94,11 +96,19 @@ def test_set_with_model(run: mocks.Run):
     assert retval is None
 
 
-def test_reset(run: mocks.Run):
+def test_reset_str(run: mocks.Run):
+    run.handle(['juju', 'config', 'app1', '--reset', 'rst'])
+
+    juju = jubilant.Juju()
+    retval = juju.config('app1', reset='rst')
+    assert retval is None
+
+
+def test_reset_list(run: mocks.Run):
     run.handle(['juju', 'config', 'app1', '--reset', 'x,why,zed'])
 
     juju = jubilant.Juju()
-    retval = juju.config('app1', {'x': None, 'why': None, 'zed': None})
+    retval = juju.config('app1', reset=['x', 'why', 'zed'])
     assert retval is None
 
 
@@ -106,5 +116,11 @@ def test_set_with_reset(run: mocks.Run):
     run.handle(['juju', 'config', 'app1', 'foo=bar', '--reset', 'baz,buzz'])
 
     juju = jubilant.Juju()
-    retval = juju.config('app1', {'foo': 'bar', 'baz': None, 'buzz': None})
+    retval = juju.config('app1', {'foo': 'bar'}, reset=['baz', 'buzz'])
     assert retval is None
+
+
+def test_format_config_type_error():
+    juju = jubilant.Juju()
+    with pytest.raises(TypeError):
+        juju.config('app1', {'foo': None})  # type: ignore
diff --git a/tests/unit/test_model_config.py b/tests/unit/test_model_config.py
index 9652f07..b5f6d55 100644
--- a/tests/unit/test_model_config.py
+++ b/tests/unit/test_model_config.py
@@ -69,11 +69,19 @@ def test_set_with_model(run: mocks.Run):
     assert retval is None
 
 
-def test_reset(run: mocks.Run):
+def test_reset_str(run: mocks.Run):
+    run.handle(['juju', 'model-config', '--reset', 'rst'])
+
+    juju = jubilant.Juju()
+    retval = juju.model_config(reset='rst')
+    assert retval is None
+
+
+def test_reset_list(run: mocks.Run):
     run.handle(['juju', 'model-config', '--reset', 'x,why,zed'])
 
     juju = jubilant.Juju()
-    retval = juju.model_config({'x': None, 'why': None, 'zed': None})
+    retval = juju.model_config(reset=['x', 'why', 'zed'])
     assert retval is None
 
 
@@ -81,5 +89,5 @@ def test_set_with_reset(run: mocks.Run):
     run.handle(['juju', 'model-config', 'foo=bar', '--reset', 'baz,buzz'])
 
     juju = jubilant.Juju()
-    retval = juju.model_config({'foo': 'bar', 'baz': None, 'buzz': None})
+    retval = juju.model_config({'foo': 'bar'}, reset=['baz', 'buzz'])
     assert retval is None
diff --git a/tests/unit/test_scp.py b/tests/unit/test_scp.py
index f13db8f..6d4c126 100644
--- a/tests/unit/test_scp.py
+++ b/tests/unit/test_scp.py
@@ -1,5 +1,7 @@
 import pathlib
 
+import pytest
+
 import jubilant
 
 from . import mocks
@@ -44,3 +46,10 @@ def test_path_destination(run: mocks.Run):
     juju = jubilant.Juju()
 
     juju.scp('SRC', pathlib.Path('DST'))
+
+
+def test_type_error():
+    juju = jubilant.Juju()
+
+    with pytest.raises(TypeError):
+        juju.scp('src', 'dst', scp_options='invalid')
diff --git a/tests/unit/test_ssh.py b/tests/unit/test_ssh.py
index 1508146..801e3c3 100644
--- a/tests/unit/test_ssh.py
+++ b/tests/unit/test_ssh.py
@@ -66,7 +66,7 @@ def test_s
... [truncated]
```
