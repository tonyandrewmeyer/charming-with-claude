# fix(model): make Secret.set_content invalidate local cache (#1001)

**Repository**: operator
**Commit**: [b6ffaf09](https://github.com/canonical/operator/commit/b6ffaf09254ad8488aecb9ae749509ea1d318e91)
**Date**: 2023-08-30

## Classification

| Field | Value |
|-------|-------|
| Bug Area | secrets |
| Bug Type | caching |
| Severity | medium |
| Fix Category | source-fix |

## Summary

model): make secret.set_content invalidate local cache

## Commit Message

This is so that if get_content() is called after set_content(), it fetches and
returns the expected new content. We could also set self._content to
the new content, but re-fetching it from Juju seems better.

## Changed Files

- M	ops/model.py
- M	test/test_model.py

## Diff

```diff
diff --git a/ops/model.py b/ops/model.py
index 906b463..304af8f 100644
--- a/ops/model.py
+++ b/ops/model.py
@@ -1225,6 +1225,7 @@ class Secret:
         if self._id is None:
             self._id = self.get_info().id
         self._backend.secret_set(typing.cast(str, self.id), content=content)
+        self._content = None  # invalidate cache so it's refetched next get_content()
 
     def set_info(self, *,
                  label: Optional[str] = None,
diff --git a/test/test_model.py b/test/test_model.py
index d74dd17..8b64347 100755
--- a/test/test_model.py
+++ b/test/test_model.py
@@ -3116,6 +3116,24 @@ class TestSecretClass(unittest.TestCase):
         self.assertEqual(fake_script_calls(self, clear=True),
                          [['secret-get', 'secret:z', '--format=json']])
 
+    def test_set_content_invalidates_cache(self):
+        fake_script(self, 'secret-get', """echo '{"foo": "bar"}'""")
+        fake_script(self, 'secret-set', """exit 0""")
+
+        secret = self.make_secret(id='z')
+        old_content = secret.get_content()
+        self.assertEqual(old_content, {'foo': 'bar'})
+        secret.set_content({'new': 'content'})
+        fake_script(self, 'secret-get', """echo '{"new": "content"}'""")
+        new_content = secret.get_content()
+        self.assertEqual(new_content, {'new': 'content'})
+
+        self.assertEqual(fake_script_calls(self, clear=True), [
+            ['secret-get', 'secret:z', '--format=json'],
+            ['secret-set', 'secret:z', 'new=content'],
+            ['secret-get', 'secret:z', '--format=json'],
+        ])
+
     def test_peek_content(self):
         fake_script(self, 'secret-get', """echo '{"foo": "peeked"}'""")
```
