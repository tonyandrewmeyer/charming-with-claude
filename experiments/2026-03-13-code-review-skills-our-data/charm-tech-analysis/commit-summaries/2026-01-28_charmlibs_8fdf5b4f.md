# fix: Renew expiring certs missed by the secret expired event handler (#311)

**Repository**: charmlibs
**Commit**: [8fdf5b4f](https://github.com/canonical/charmlibs/commit/8fdf5b4ff43c25a2c476e5a38db38c8212e31780)
**Date**: 2026-01-28

## Classification

| Field | Value |
|-------|-------|
| Bug Area | secrets |
| Bug Type | edge-case |
| Severity | high |
| Fix Category | source-fix |

## Summary

Added safety-net renewal check during relation-changed to catch expiring certificates that the secret_expired event handler missed, preventing certificate expiry and downtime.

## Commit Message

fixes https://github.com/canonical/tls-certificates-interface/issues/338

## Changed Files

- M	interfaces/tls-certificates/CHANGELOG.md
- M	interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_tls_certificates.py
- M	interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_version.py
- M	interfaces/tls-certificates/tests/unit/test_requires.py

## Diff

```diff
diff --git a/interfaces/tls-certificates/CHANGELOG.md b/interfaces/tls-certificates/CHANGELOG.md
index 1556052..7a456a0 100644
--- a/interfaces/tls-certificates/CHANGELOG.md
+++ b/interfaces/tls-certificates/CHANGELOG.md
@@ -1,3 +1,7 @@
+# 1.6.0 - 27 January 2025
+
+Add a safety net to ensure renewing expiring certificates.
+
 # 1.5.0 - 27 January 2025
 
 Add a public helper function to get the ID of the lib generated private key secret.
diff --git a/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_tls_certificates.py b/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_tls_certificates.py
index 15f81f7..e6faf12 100644
--- a/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_tls_certificates.py
+++ b/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_tls_certificates.py
@@ -1793,6 +1793,7 @@ class TLSCertificatesRequiresV4(Object):
         self._cleanup_certificate_requests()
         self._send_certificate_requests()
         self._find_available_certificates()
+        self._renew_expiring_certificates()
 
     def _mode_is_valid(self, mode: Mode) -> bool:
         return mode in [Mode.UNIT, Mode.APP]
@@ -2376,6 +2377,32 @@ class TLSCertificatesRequiresV4(Object):
                     "Removed CSR from relation data because it did not match the private key"
                 )
 
+    def _renew_expiring_certificates(self) -> None:
+        """Renew certificates approaching expiry that haven't been renewed yet.
+
+        This acts as a safety net for cases where secret_expired failed to trigger or complete.
+        Checks certificates at a threshold slightly after the configured renewal time but before
+        expiry to prevent downtime.
+        """
+        now = datetime.now(timezone.utc)
+        safety_threshold = min(0.99, self.renewal_relative_time + 0.05)
+
+        assigned_certificates, _ = self.get_assigned_certificates()
+
+        for provider_certificate in assigned_certificates:
+            cert = provider_certificate.certificate
+            validity_start = cert.validity_start_time
+            validity_end = cert.expiry_time
+            validity_period = validity_end - validity_start
+            safety_renewal_time = validity_start + (validity_period * safety_threshold)
+
+            if now >= safety_renewal_time and now < validity_end:
+                logger.warning(
+                    "Certificate approaching expiry but not renewed - "
+                    "triggering renewal as safety net"
+                )
+                self._renew_certificate_request(provider_certificate.certificate_signing_request)
+
     def _tls_relation_created(self) -> bool:
         relation = self.model.get_relation(self.relationship_name)
         if not relation:
diff --git a/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_version.py b/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_version.py
index ff131f0..6f592d9 100644
--- a/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_version.py
+++ b/interfaces/tls-certificates/src/charmlibs/interfaces/tls_certificates/_version.py
@@ -12,4 +12,4 @@
 # See the License for the specific language governing permissions and
 # limitations under the License.
 
-__version__ = "1.5.0"
+__version__ = "1.6.0"
diff --git a/interfaces/tls-certificates/tests/unit/test_requires.py b/interfaces/tls-certificates/tests/unit/test_requires.py
index 2488fd3..ed28727 100644
--- a/interfaces/tls-certificates/tests/unit/test_requires.py
+++ b/interfaces/tls-certificates/tests/unit/test_requires.py
@@ -10,7 +10,8 @@ from unittest.mock import MagicMock, patch
 import pytest
 import scenario
 import yaml
-from cryptography.hazmat.primitives import hashes
+from cryptography import x509
+from cryptography.hazmat.primitives import hashes, serialization
 from ops import testing
 from ops.testing import ActionFailed, Secret
 
@@ -1766,3 +1767,160 @@ class TestTLSCertificatesRequiresV4:
 
         self.ctx.run(self.ctx.on.action("get-private-key-secret-id"), state_in)
         assert self.ctx.action_results == {"secret-id": ""}
+
+    @patch(LIB_DIR + ".CertificateRequestAttributes.generate_csr")
+    def test_given_certificate_past_safety_threshold_when_configure_then_certificate_is_renewed(
+        self, mock_generate_csr: MagicMock
+    ):
+        validity_days = 365
+        days_elapsed = 362
+
+        private_key = generate_private_key()
+        csr = generate_csr(
+            private_key=private_key,
+            common_name="example.com",
+        )
+        provider_private_key = generate_private_key()
+        provider_ca_certificate = generate_ca(
+            private_key=provider_private_key,
+            common_name="example.com",
+            validity=datetime.timedelta(days=validity_days),
+        )
+
+        csr_object = x509.load_pem_x509_csr(csr.encode())
+        issuer = x509.load_pem_x509_certificate(provider_ca_certificate.encode()).issuer
+        ca_private_key_object = serialization.load_pem_private_key(
+            provider_private_key.encode(), password=None
+        )
+
+        now = datetime.datetime.now(datetime.timezone.utc)
+        not_valid_before = now - datetime.timedelta(days=days_elapsed)
+        not_valid_after = not_valid_before + datetime.timedelta(days=validity_days)
+
+        cert = (
+            x509.CertificateBuilder()
+            .subject_name(csr_object.subject)
+            .issuer_name(issuer)
+            .public_key(csr_object.public_key())
+            .serial_number(x509.random_serial_number())
+            .not_valid_before(not_valid_before)
+            .not_valid_after(not_valid_after)
+            .sign(ca_private_key_object, hashes.SHA256())  # type: ignore[arg-type]
+        )
+        certificate = cert.public_bytes(serialization.Encoding.PEM).decode().strip()
+
+        new_csr = generate_csr(
+            private_key=private_key,
+            common_name="example.com",
+        )
+        mock_generate_csr.return_value = new_csr
+
+        certificates_relation = testing.Relation(
+            endpoint="certificates",
+            interface="tls-certificates",
+            remote_app_name="certificate-provider",
+            local_unit_data={
+                "certificate_signing_requests": json.dumps([
+                    {
+                        "certificate_signing_request": str(csr),
+                        "ca": False,
+                    }
+                ])
+            },
+            remote_app_data={
+                "certificates": json.dumps([
+                    {
+                        "certificate": str(certificate),
+                        "certificate_signing_request": str(csr),
+                        "ca": str(provider_ca_certificate),
+                        "chain": [str(certificate), str(provider_ca_certificate)],
+                    }
+                ]),
+            },
+        )
+
+        private_key_secret = Secret(
+            {"private-key": str(private_key)},
+            label=f"{LIBID}-private-key-0-{certificates_relation.endpoint}",
+            owner="unit",
+        )
+
+        state_in = testing.State(
+            config={"common_name": "example.com"},
+            relations={certificates_relation},
+            secrets={private_key_secret},
+        )
+
+        state_out = self.ctx.run(self.ctx.on.relation_changed(certificates_relation), state_in)
+
+        updated_relation = state_out.get_relation(certificates_relation.id)
+        csrs_data = json.loads(updated_relation.local_unit_data["certificate_signing_requests"])
+        assert len(csrs_data) == 1
+        assert csrs_data[0]["certificate_signing_request"] == str(new_csr)
+        assert csrs_data[0]["certificate_signing_request"] != str(csr)
+
+    @patch(LIB_DIR + ".CertificateRequestAttributes.generate_csr")
+    def test_given_certificate_before_safety_threshold_when_configure_then_certificate_is_not_renewed(
+        self, mock_generate_csr: MagicMock
+    ):
+        private_key = generate_private_key()
+        csr = generate_csr(
+            private_key=private_key,
+            common_name="example.com",
+        )
+        provider_private_key = generate_private_key()
+        provider_ca_certificate = generate_ca(
+            private_key=provider_private_key,
+            common_name="example.com",
+            validity=datetime.timedelta(days=365),
+        )
+        certificate = generate_certificate(
+            ca=provider_ca_certificate,
+            ca_key=provider_private_key,
+            csr=csr,
+            validity=datetime.timedelta(days=365),
+        )
+
+        certificates_relation = testing.Relation(
+            endpoint="certificates",
+            interface="tls-certificates",
+            remote_app_name="certificate-provider",
+            local_unit_data={
+                "certificate_signing_requests": json.dumps([
+                    {
+                        "certificate_signing_request": str(csr),
+                        "ca": False,
+                    }
+                ])
+            },
+            remote_app_data={
+                "certificates": json.dumps([
+                    {
+                        "certificate": str(certificate),
+                        "certificate_signing_request": str(csr),
+                        "ca": str(provider_ca_certificate),
+                        "chain": [str(certificate), str(provider_ca_certificate)],
+                    }
+                ]),
+            },
+        )
+
+        private_key_secret = Secret(
+            {"private-key": str(private_key)},
+            label=f"{LIBID}-private-key-0-{certificates_relation.endpoint}",
+            owner="unit",
+        )
+
+        state_in = testing.State(
+            config={"common_name": "example.com"},
+            relations={certificates_relation},
+            secrets={private_key_secret},
+   
... [truncated]
```
