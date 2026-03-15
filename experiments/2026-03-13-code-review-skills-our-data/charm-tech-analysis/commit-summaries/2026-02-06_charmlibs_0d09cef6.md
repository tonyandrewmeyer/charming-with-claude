# fix: correct type checking errors in tls-certificates lib (#326)

**Repository**: charmlibs
**Commit**: [0d09cef6](https://github.com/canonical/charmlibs/commit/0d09cef6540b89ea5421a659fd3dfd44183bda86)
**Date**: 2026-02-06

## Classification

| Field | Value |
|-------|-------|
| Bug Area | typing |
| Bug Type | type-error |
| Severity | low |
| Fix Category | source-fix |

## Summary

Fixed pyright type checking errors in tls-certificates lib including generic type parameters, Mapping vs MutableMapping, and pyright ignore comments.

## Commit Message

#325 resolves a CI issue that resulted in linting showing as green even
when individual checks fail. This masked `pyright` type checking errors
in the TLS Certificates library. In preparation for merging #325, this
PR resolves these errors. Please see individual comments for more
details.

To validate this PRs changes, you can check the details of the `CI /
package (interfaces/tls-certificates) / lint` jobs and verify that there
there are no type checking issues.

Presumably these type checking errors were not resulting in major user
facing issues, but they could still do with a release. If you think they
should be released on their own, I can add a patch version bump and
release notes to this PR. Otherwise they should be included in the next
release (e.g. #322).

## Changed Files

- M	interfaces/tls-certificates/interface/v1/schema.py
- M	interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_tls_certificates.py
- M	interfaces/tls-certificates/tests/unit/test_requires.py

## Diff

```diff
diff --git a/interfaces/tls-certificates/interface/v1/schema.py b/interfaces/tls-certificates/interface/v1/schema.py
index 74fd01e..024b40c 100644
--- a/interfaces/tls-certificates/interface/v1/schema.py
+++ b/interfaces/tls-certificates/interface/v1/schema.py
@@ -45,7 +45,7 @@ Examples:
         app:  <empty>
 """
 
-from interface_tester.schema_base import DataBagSchema  # pyright: ignore[reportMissingTypeStubs]
+from interface_tester.schema_base import DataBagSchema
 from pydantic import BaseModel, Field, Json
 
 
diff --git a/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_tls_certificates.py b/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_tls_certificates.py
index e6faf12..18727e4 100644
--- a/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_tls_certificates.py
+++ b/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_tls_certificates.py
@@ -32,7 +32,7 @@ from ops.jujuversion import JujuVersion
 from ops.model import Application, ModelError, Relation, SecretNotFoundError, Unit
 
 if TYPE_CHECKING:
-    from collections.abc import Collection, MutableMapping
+    from collections.abc import Collection, Mapping, MutableMapping
 
 # legacy Charmhub-hosted lib ID, used at runtime in this lib for labels
 LIBID = "afd8c2bccf834997afce12c2706d2ede"
@@ -61,7 +61,7 @@ class _OWASPLogEvent:
     def to_json(self) -> str:
         return json.dumps(self.to_dict(), ensure_ascii=False)
 
-    def to_dict(self) -> dict:
+    def to_dict(self) -> dict[str, str]:
         log_event = dict(asdict(self), **self.labels)
         log_event.pop("labels", None)
         return {k: v for k, v in log_event.items() if v is not None}
@@ -126,7 +126,7 @@ class _DatabagModel(pydantic.BaseModel):
     """Pydantic config."""
 
     @classmethod
-    def load(cls, databag: MutableMapping):
+    def load(cls, databag: Mapping[str, str]):
         """Load this model from a Juju databag."""
         if IS_PYDANTIC_V1:
             return cls._load_v1(databag)
@@ -154,17 +154,17 @@ class _DatabagModel(pydantic.BaseModel):
             raise DataValidationError(msg) from e
 
     @classmethod
-    def _load_v1(cls, databag: MutableMapping):
+    def _load_v1(cls, databag: Mapping[str, str]):
         """Load implementation for pydantic v1."""
         if cls._NEST_UNDER:
-            return cls.parse_obj(json.loads(databag[cls._NEST_UNDER]))
+            return cls.parse_obj(json.loads(databag[cls._NEST_UNDER]))  # pyright: ignore[reportDeprecated]
 
         try:
             data = {
                 k: json.loads(v)
                 for k, v in databag.items()
                 # Don't attempt to parse model-external values
-                if k in {f.alias for f in cls.__fields__.values()}
+                if k in {f.alias for f in cls.__fields__.values()}  # pyright: ignore[reportDeprecated]
             }
         except json.JSONDecodeError as e:
             msg = f"invalid databag contents: expecting json. {databag}"
@@ -178,7 +178,7 @@ class _DatabagModel(pydantic.BaseModel):
             logger.debug(msg, exc_info=True)
             raise DataValidationError(msg) from e
 
-    def dump(self, databag: MutableMapping | None = None, clear: bool = True):
+    def dump(self, databag: MutableMapping[str, str] | None = None, clear: bool = True):
         """Write the contents of this model to Juju databag.
 
         Args:
@@ -208,7 +208,7 @@ class _DatabagModel(pydantic.BaseModel):
         databag.update({k: json.dumps(v) for k, v in dct.items()})
         return databag
 
-    def _dump_v1(self, databag: MutableMapping | None = None, clear: bool = True):
+    def _dump_v1(self, databag: MutableMapping[str, str] | None = None, clear: bool = True):
         """Dump implementation for pydantic v1."""
         if clear and databag:
             databag.clear()
@@ -217,10 +217,10 @@ class _DatabagModel(pydantic.BaseModel):
             databag = {}
 
         if self._NEST_UNDER:
-            databag[self._NEST_UNDER] = self.json(by_alias=True, exclude_defaults=True)
+            databag[self._NEST_UNDER] = self.json(by_alias=True, exclude_defaults=True)  # pyright: ignore[reportDeprecated]
             return databag
 
-        dct = json.loads(self.json(by_alias=True, exclude_defaults=True))
+        dct = json.loads(self.json(by_alias=True, exclude_defaults=True))  # pyright: ignore[reportDeprecated]
         databag.update({k: json.dumps(v) for k, v in dct.items()})
 
         return databag
@@ -1251,7 +1251,7 @@ class CertificateAvailableEvent(EventBase):
         self.ca = ca
         self.chain = chain
 
-    def snapshot(self) -> dict:
+    def snapshot(self) -> dict[str, str]:
         """Return snapshot."""
         return {
             "certificate": str(self.certificate),
@@ -1260,7 +1260,7 @@ class CertificateAvailableEvent(EventBase):
             "chain": json.dumps([str(certificate) for certificate in self.chain]),
         }
 
-    def restore(self, snapshot: dict):
+    def restore(self, snapshot: dict[str, str]):
         """Restore snapshot."""
         self.certificate = Certificate.from_string(snapshot["certificate"])
         self.certificate_signing_request = CertificateSigningRequest.from_string(
@@ -1288,7 +1288,7 @@ class CertificateDeniedEvent(EventBase):
         self.certificate_signing_request = certificate_signing_request
         self.error = error
 
-    def snapshot(self) -> dict:
+    def snapshot(self) -> dict[str, str]:
         """Return snapshot."""
         error_json = self.error.json() if IS_PYDANTIC_V1 else self.error.model_dump_json()  # type: ignore[attr-defined]
         return {
@@ -1296,7 +1296,7 @@ class CertificateDeniedEvent(EventBase):
             "error": error_json,
         }
 
-    def restore(self, snapshot: dict):
+    def restore(self, snapshot: dict[str, str]):
         """Restore snapshot."""
         self.certificate_signing_request = CertificateSigningRequest.from_string(
             snapshot["certificate_signing_request"]
@@ -1537,7 +1537,7 @@ def generate_certificate(
 def _extract_subject_name_attributes(
     attributes: CertificateRequestAttributes,
 ) -> x509.Name | None:
-    subject_name_attributes = []
+    subject_name_attributes: list[x509.NameAttribute[str | bytes]] = []
     if attributes.common_name:
         subject_name_attributes.append(
             x509.NameAttribute(x509.NameOID.COMMON_NAME, attributes.common_name)
@@ -1588,7 +1588,7 @@ def _generate_certificate_request_extensions(
     authority_key_identifier: bytes,
     csr: x509.CertificateSigningRequest,
     is_ca: bool,
-) -> list[x509.Extension]:
+) -> list[x509.Extension[x509.ExtensionType]]:
     """Generate a list of certificate extensions from a CSR and other known information.
 
     Args:
@@ -1599,7 +1599,7 @@ def _generate_certificate_request_extensions(
     Returns:
         List[x509.Extension]: List of extensions
     """
-    cert_extensions_list: list[x509.Extension] = [
+    cert_extensions_list: list[x509.Extension[x509.ExtensionType]] = [
         x509.Extension(
             oid=ExtensionOID.AUTHORITY_KEY_IDENTIFIER,
             value=x509.AuthorityKeyIdentifier(
@@ -1656,7 +1656,7 @@ def _generate_certificate_request_extensions(
 
 def _generate_subject_alternative_name_extension(
     csr: x509.CertificateSigningRequest,
-) -> x509.Extension | None:
+) -> x509.Extension[x509.ExtensionType] | None:
     sans: list[x509.GeneralName] = []
     try:
         loaded_san_ext = csr.extensions.get_extension_for_class(x509.SubjectAlternativeName)
diff --git a/interfaces/tls-certificates/tests/unit/test_requires.py b/interfaces/tls-certificates/tests/unit/test_requires.py
index ed28727..9e81f37 100644
--- a/interfaces/tls-certificates/tests/unit/test_requires.py
+++ b/interfaces/tls-certificates/tests/unit/test_requires.py
@@ -1687,6 +1687,7 @@ class TestTLSCertificatesRequiresV4:
         state_out = self.ctx.run(self.ctx.on.relation_changed(certificates_relation), state_in)
 
         self.ctx.run(self.ctx.on.action("get-request-errors"), state_out)
+        assert self.ctx.action_results is not None
         errors = self.ctx.action_results["errors"]
         assert len(errors) == 2
         assert errors[0]["code"] == 101
@@ -1716,6 +1717,7 @@ class TestTLSCertificatesRequiresV4:
 
         state_out = self.ctx.run(self.ctx.on.action("get-private-key-secret-id"), state_in)
 
+        assert self.ctx.action_results is not None
         result_secret_id = self.ctx.action_results["secret-id"]
         assert result_secret_id != ""
         assert result_secret_id.startswith("secret:")
```
