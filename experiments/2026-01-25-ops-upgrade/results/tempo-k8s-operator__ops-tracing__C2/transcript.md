# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `4498afc9-91b4-41e9-bd82-134810d6392b`  
> - **Started:** 4/1/2026, 10:22:30 PM  
> - **Duration:** 24m 57s  
> - **Exported:** 4/1/2026, 10:47:28 PM  

---

<sub>⏱️ 6s</sub>

### 👤 User

ops 2.21.0 introduced ops[tracing] as the first-party charm tracing library, replacing the community charm_tracing / charms.tempo_k8s.v2.tracing library approach. Charms can now add OpenTelemetry tracing with pip install ops[tracing] and a single ops.tracing.setup() or ops.tracing.Tracing() call. Learn how to use that feature and update this charm to make use of it.

---

<sub>⏱️ 22s</sub>

### 📦 task (Completed)

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2

<details>
<summary>18 lines</summary>

```
.git
.github
.gitignore
.jujuignore
CODEOWNERS
CONTRIBUTING.md
HACKING.md
LICENSE
README.md
charmcraft.yaml
icon.svg
lib
pyproject.toml
requirements.txt
scripts
src
tests
tox.ini
```

</details>


### ✅ `glob`

**/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2**

"**/*.py" in /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2

<details>
<summary>43 matches</summary>

```
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_provider.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm_scaling.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_legacy.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm_tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_a_charm_tracer_multi_import_warning.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/helpers.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/conftest.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/unit/test_tempo.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/unit/test_charm.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/test_tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester/src/charm.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/conftest.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_tls.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester/src/resources/webserver.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_ingressed_tls.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_scaling_monolithic.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/helpers.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester-grpc/src/charm.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester-grpc/src/resources/webserver.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_integration.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/scripts/tracegen.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/parca/v0/parca_scrape.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/loki_k8s/v0/loki_push_api.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/traefik_route_k8s/v0/traefik_route.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/grafana_k8s/v0/grafana_dashboard.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/data_platform_libs/v0/s3.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/grafana_k8s/v0/grafana_source.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/observability_libs/v0/kubernetes_service_patch.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/observability_libs/v0/juju_topology.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/prometheus_k8s/v0/prometheus_scrape.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tls_certificates_interface/v3/tls_certificates.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/observability_libs/v1/cert_handler.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/traefik_k8s/v2/ingress.py
```

</details>


### ✅ `glob`

**/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2**

"**/charmcraft.yaml" in /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2

```
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester/charmcraft.yaml
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester-grpc/charmcraft.yaml
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/charmcraft.yaml
```


### ✅ `glob`

**/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2**

"**/requirements.txt" in /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2

```
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/requirements.txt
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester/requirements.txt
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester-grpc/requirements.txt
```


### ✅ `glob`

**/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2**

"**/pyproject.toml" in /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2

```
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/pyproject.toml
```


### 💬 Copilot

Now let me search for tracing imports and read the key files in parallel:

### ✅ `grep`

**/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2**

"charm_tracing|charms\.tempo_k8s|from charms\.tempo_k8s" in **/*.py (/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2)

<details>
<summary>17 matches</summary>

```
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_provider.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm_tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_a_charm_tracer_multi_import_warning.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_legacy.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/conftest.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester/src/charm.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester-grpc/src/charm.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/charmcraft.yaml.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/charmcraft.yaml

<details>
<summary>119 lines</summary>

```
1. # Copyright 2022 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. name: tempo-k8s
4. type: charm
5. 
6. assumes:
7.   - k8s-api
8. 
9.   # Juju 3.4.0 needed for pebble notify
10.   - juju >= 3.4.0
11. 
12. description: |
13.   Tempo is a distributed tracing backend by Grafana, supporting Jaeger,
14.   Zipkin, and OpenTelemetry protocols.
15. 
16. summary: |
17.   Tempo is a distributed tracing backend by Grafana.
18. 
19. links:
20.   documentation: https://discourse.charmhub.io/t/tempo-k8s-docs-index/14005
21.   website:
22.     - https://charmhub.io/tempo-k8s
23.   source:
24.     - https://github.com/canonical/tempo-k8s-operator
25.   issues:
26.     - https://github.com/canonical/tempo-k8s-operator/issues
27. 
28. containers:
29.   tempo:
30.     resource: tempo-image
31.     mounts:
32.       - storage: data
33.         location: /tmp/tempo
34. 
35. resources:
36.   tempo-image:
37.     type: oci-image
38.     description: OCI image for Tempo
39.     # Included for simplicity in integration tests
40.     # see https://hub.docker.com/r/grafana/tempo/tags
41.     upstream-source: grafana/tempo:2.4.0
42. 
43. provides:
44.   grafana-dashboard:
45.     interface: grafana_dashboard
46.     description: |
47.       Forwards the built-in grafana dashboard(s) for monitoring Tempo.
48.   grafana-source:
49.     interface: grafana_datasource
50.     description: |
51.       Configures Grafana to be able to use this Tempo instance as a datasource.
52.   metrics-endpoint:
53.     interface: prometheus_scrape
54.     description: |
55.       Exposes the Prometheus metrics endpoint providing telemetry about the
56.       Tempo instance.
57.   tracing:
58.     interface: tracing
59.     description: |
60.       Integration to offer other charms the possibility to send traces to Tempo.
61. 
62. 
63. requires:
64.   s3:
65.     interface: s3
66.     limit: 1
67.     description: |
68.       Obtains access to the s3 bucket for data storage.
69.   logging:
70.     interface: loki_push_api
71.     description: |
72.       Integration with Loki to push Tempo logs to the observability stack.
73.   ingress:
74.     interface: traefik_route
75.     description: |
76.       Ingress integration for Tempo server and Tempo receiver endpoints,
77.       so that cross-model workloads can send their traces to Tempo through the ingress.
78.       Uses `traefik_route` to open ports on Traefik host for tracing ingesters.
79.   certificates:
80.     interface: tls-certificates
81.     limit: 1
82.     description: |
83.       Certificate and key files for securing Tempo internal and external 
84.       communications with TLS.
85. 
86. storage:
87.   data:
88.     type: filesystem
89.     location: /tempo-data
90. 
91. actions:
92.   list-receivers:
93.     description: |
94.       Returns a list of all enabled receiver endpoints.
95. 
96. peers:
97.   tempo-peers:
98.     interface: tempo_peers
99.     description: |
100.       peer relation for internal coordination
101.       
102. 
103. bases:
104.   - build-on:
105.       - name: "ubuntu"
106.         channel: "22.04"
107.     run-on:
108.       - name: "ubuntu"
109.         channel: "22.04"
110. 
111. parts:
112.   charm:
113.     charm-binary-python-packages:
114.       - "pydantic>=2"
115.       - "cryptography"
116.       - "jsonschema"
117.       - "opentelemetry-exporter-otlp-proto-http==1.21.0"
118. 
119.
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/requirements.txt.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/requirements.txt

<details>
<summary>20 lines</summary>

```
1. # pin importlib-metadata version else charmcraft pack will fail to resolve the dependencies for the pydeps-installed otlp library
2. importlib-metadata~=6.0.0
3. ops
4. jsonschema==4.17.0
5. lightkube==0.11.0
6. lightkube-models==1.24.1.4
7. tenacity==8.2.3
8. 
9. # PYDEPS
10. # lib/charms/tempo_k8s/v1/charm_tracing.py
11. opentelemetry-exporter-otlp-proto-http==1.21.0
12. 
13. # lib/charms/tls_certificates_interface/v2/tls_certificates.py
14. jsonschema
15. cryptography
16. # lib/charms/tempo_k8s/v1/tracing.py
17. pydantic>=2
18. # lib/charms/prometheus_k8s/v0/prometheus_scrape.py
19. cosl
20.
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/pyproject.toml.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/pyproject.toml

<details>
<summary>74 lines</summary>

```
1. # Copyright 2022 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. [project]
4. name = "tempo-k8s"
5. version = "0.1"  # this is in fact irrelevant
6. 
7. [project.optional-dependencies]
8. lib_pydeps = [
9. ]
10. 
11. [tool.pyright]
12. extraPaths = ["lib"]
13. pythonVersion = "3.8"
14. pythonPlatform = "All"
15. 
16. [build]
17. build-base = "/tmp/build"
18. 
19. [egg_info]
20. egg-base = "/tmp"
21. 
22. # Testing tools configuration
23. [tool.coverage.run]
24. branch = true
25. 
26. [tool.coverage.report]
27. show_missing = true
28. 
29. [tool.pytest.ini_options]
30. minversion = "6.0"
31. log_cli_level = "INFO"
32. markers = ["setup", "teardown"]
33. 
34. # Formatting tools configuration
35. [tool.isort]
36. profile = "black"
37. 
38. [tool.black]
39. line-length = 99
40. target-version = ["py38"]
41. 
42. # Linting tools configuration
43. [tool.ruff]
44. line-length = 99
45. extend-exclude = ["__pycache__", "*.egg_info", "*integration/tester*"]
46. 
47. [tool.ruff.lint]
48. select = ["E", "W", "F", "C", "N", "D", "I001"]
49. extend-ignore = [
50.     "D203",
51.     "D204",
52.     "D213",
53.     "D215",
54.     "D400",
55.     "D404",
56.     "D406",
57.     "D407",
58.     "D408",
59.     "D409",
60.     "D413",
61. ]
62. ignore = ["E501", "D107"]
63. 
64. [tool.ruff.lint.per-file-ignores]
65. "tests/*" = ["D100","D101","D102","D103","D104"]
66. # Remove charm_tracing.py E402 when _remove_stale_otel_sdk_packages() is removed
67. # from the library
68. "lib/charms/tempo_k8s/v1/charm_tracing.py" = ["E402"]
69. 
70. [lint.mccabe]
71. max-complexity = 10
72. 
73. [tool.codespell]
74. skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.vscode,.coverage"
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py

```
File too large to read at once (23.5 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


### 💬 Copilot

Let me view the charm.py file in parts:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py (lines 1-100)

<details>
<summary>100 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2024 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Charmed Operator for Tempo; a lightweight object storage based tracing backend."""
6. 
7. import logging
8. import re
9. import socket
10. from pathlib import Path
11. from typing import Optional, Set, Tuple
12. 
13. import ops
14. from charms.data_platform_libs.v0.s3 import S3Requirer
15. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
16. from charms.grafana_k8s.v0.grafana_source import GrafanaSourceProvider
17. from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
18. from charms.observability_libs.v0.kubernetes_service_patch import KubernetesServicePatch
19. from charms.observability_libs.v1.cert_handler import CertHandler
20. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
21. from charms.tempo_k8s.v1.charm_tracing import trace_charm
22. from charms.tempo_k8s.v2.tracing import (
23.     ReceiverProtocol,
24.     RequestEvent,
25.     TracingEndpointProvider,
26. )
27. from charms.traefik_route_k8s.v0.traefik_route import TraefikRouteRequirer
28. from ops.charm import (
29.     CharmBase,
30.     CollectStatusEvent,
31.     PebbleNoticeEvent,
32.     RelationEvent,
33.     WorkloadEvent,
34. )
35. from ops.main import main
36. from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus
37. from ops.pebble import APIError
38. 
39. from tempo import Tempo
40. 
41. logger = logging.getLogger(__name__)
42. 
43. 
44. @trace_charm(
45.     tracing_endpoint="tempo_otlp_http_endpoint",
46.     server_cert="server_cert",
47.     extra_types=(Tempo, TracingEndpointProvider),
48. )
49. class TempoCharm(CharmBase):
50.     """Charmed Operator for Tempo; a distributed tracing backend."""
51. 
52.     def __init__(self, *args):
53.         super().__init__(*args)
54.         self.tempo = tempo = Tempo(
55.             self.unit.get_container("tempo"),
56.             external_host=self.hostname,
57.             # we need otlp_http receiver for charm_tracing
58.             enable_receivers=["otlp_http"],
59.         )
60. 
61.         # TODO:
62.         #  ingress route provisioning a separate TCP ingress for each receiver if GRPC doesn't work directly
63.         self.ingress = TraefikRouteRequirer(self, self.model.get_relation("ingress"), "ingress")  # type: ignore
64. 
65.         self.cert_handler = CertHandler(
66.             self,
67.             key="tempo-server-cert",
68.             sans=[self.hostname],
69.         )
70. 
71.         self.s3_requirer = S3Requirer(self, Tempo.s3_relation_name, Tempo.s3_bucket_name)
72. 
73.         # configure this tempo as a datasource in grafana
74.         self.grafana_source_provider = GrafanaSourceProvider(
75.             self,
76.             source_type="tempo",
77.             source_url=self._external_http_server_url,
78.             refresh_event=[
79.                 # refresh the source url when TLS config might be changing
80.                 self.on[self.cert_handler.certificates_relation_name].relation_changed,
81.                 # or when ingress changes
82.                 self.ingress.on.ready,
83.             ],
84.         )
85.         # # Patch the juju-created Kubernetes service to contain the right ports
86.         external_ports = tempo.get_external_ports(self.app.name)
87.         self._service_patcher = KubernetesServicePatch(self, external_ports)
88.         # Provide ability for Tempo to be scraped by Prometheus using prometheus_scrape
89.         self._scraping = MetricsEndpointProvider(
90.             self,
91.             relation_name="metrics-endpoint",
92.             jobs=[{"static_configs": [{"targets": [f"*:{tempo.tempo_http_server_port}"]}]}],
93.         )
94.         # Enable log forwarding for Loki and other charms that implement loki_push_api
95.         self._logging = LogProxyConsumer(
96.             self, relation_name="logging", log_files=[self.tempo.log_path], container_name="tempo"
97.         )
98.         self._grafana_dashboards = GrafanaDashboardProvider(
99.             self, relation_name="grafana-dashboard"
100.         )
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py (lines 1-80)

<details>
<summary>80 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2024 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Tempo workload configuration and client."""
6. import logging
7. import re
8. import socket
9. from pathlib import Path
10. from subprocess import CalledProcessError, getoutput
11. from typing import Dict, List, Optional, Sequence, Tuple
12. from urllib.parse import urlparse
13. 
14. import ops
15. import tenacity
16. import yaml
17. from charms.tempo_k8s.v2.tracing import (
18.     ReceiverProtocol,
19.     receiver_protocol_to_transport_protocol,
20. )
21. from charms.traefik_route_k8s.v0.traefik_route import TraefikRouteRequirer
22. from ops import ModelError
23. from ops.pebble import Layer
24. 
25. logger = logging.getLogger(__name__)
26. 
27. 
28. class Tempo:
29.     """Class representing the Tempo client workload configuration."""
30. 
31.     config_path = "/etc/tempo/tempo.yaml"
32. 
33.     # cert path on charm container
34.     server_cert_path = "/usr/local/share/ca-certificates/ca.crt"
35. 
36.     # cert paths on tempo container
37.     tls_cert_path = "/etc/tempo/tls/server.crt"
38.     tls_key_path = "/etc/tempo/tls/server.key"
39.     tls_ca_path = "/usr/local/share/ca-certificates/ca.crt"
40. 
41.     _tls_min_version = ""
42.     # cfr https://grafana.com/docs/enterprise-traces/latest/configure/reference/#supported-contents-and-default-values
43.     # "VersionTLS12"
44. 
45.     wal_path = "/etc/tempo/tempo_wal"
46.     log_path = "/var/log/tempo.log"
47.     tempo_ready_notice_key = "canonical.com/tempo/workload-ready"
48. 
49.     s3_relation_name = "s3"
50.     s3_bucket_name = "tempo"
51. 
52.     memberlist_port = 7946
53. 
54.     server_ports = {
55.         "tempo_http": 3200,
56.         "tempo_grpc": 9096,  # default grpc listen port is 9095, but that conflicts with promtail.
57.     }
58. 
59.     receiver_ports: Dict[str, int] = {
60.         "zipkin": 9411,
61.         "otlp_grpc": 4317,
62.         "otlp_http": 4318,
63.         "jaeger_thrift_http": 14268,
64.         # todo if necessary add support for:
65.         #  "kafka": 42,
66.         #  "jaeger_grpc": 14250,
67.         #  "opencensus": 43,
68.         #  "jaeger_thrift_compact": 44,
69.         #  "jaeger_thrift_binary": 45,
70.     }
71. 
72.     all_ports = {**server_ports, **receiver_ports}
73. 
74.     def __init__(
75.         self,
76.         container: ops.Container,
77.         external_host: Optional[str] = None,
78.         enable_receivers: Optional[Sequence[ReceiverProtocol]] = None,
79.     ):
80.         # ports source: https://github.com/grafana/tempo/blob/main/example/docker-compose/local/docker-compose.yaml
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib

```
charms
```


### 💬 Copilot

Let me explore the lib directory and view the tracing libraries:

### ✅ `bash`

**List Python files in lib directory**

$ find /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib -type f -name "*.py" | head -20

<details>
<summary>16 lines</summary>

```
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/observability_libs/v1/cert_handler.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/observability_libs/v0/juju_topology.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/observability_libs/v0/kubernetes_service_patch.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/parca/v0/parca_scrape.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/data_platform_libs/v0/s3.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/loki_k8s/v0/loki_push_api.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/grafana_k8s/v0/grafana_dashboard.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/grafana_k8s/v0/grafana_source.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/prometheus_k8s/v0/prometheus_scrape.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/traefik_k8s/v2/ingress.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tls_certificates_interface/v3/tls_certificates.py
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/traefik_route_k8s/v0/traefik_route.py
<exited with exit code 0>
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s

```
v1
v2
```


### ✅ `grep`

**/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src**

"TracingEndpointProvider|tracing" in **/*.py (/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src)

<details>
<summary>37 matches</summary>

```
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:"""Charmed Operator for Tempo; a lightweight object storage based tracing backend."""
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:from charms.tempo_k8s.v1.charm_tracing import trace_charm
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:from charms.tempo_k8s.v2.tracing import (
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    TracingEndpointProvider,
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    tracing_endpoint="tempo_otlp_http_endpoint",
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    extra_types=(Tempo, TracingEndpointProvider),
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    """Charmed Operator for Tempo; a distributed tracing backend."""
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:            # we need otlp_http receiver for charm_tracing
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        self.tracing = TracingEndpointProvider(self, external_url=self._external_url)
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        self.framework.observe(self.tracing.on.request, self._on_tracing_request)
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        self.framework.observe(self.tracing.on.broken, self._on_tracing_broken)
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    def _on_tracing_broken(self, _):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        """Update tracing relations' databags once one relation is removed."""
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        self._update_tracing_relations()
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        # technically, because of charm tracing, this will be called first thing on each event
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        self._update_tracing_relations()
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        """Make sure the traefik route and tracing relation data are up-to-date."""
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:                self._update_tracing_relations()
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    def _on_tracing_request(self, e: RequestEvent):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        """Handle a remote requesting a tracing endpoint."""
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        logger.debug(f"received tracing request from {e.relation.app}: {e.requested_receivers}")
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        self._update_tracing_relations()
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    def _update_tracing_relations(self):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        tracing_relations = self.model.relations["tracing"]
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        if not tracing_relations:
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:            logger.warning("no tracing relations: Tempo has no receivers configured.")
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:            self.tracing.publish_receivers(
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        """List what receivers we should activate, based on the active tracing relations."""
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        requested_protocols = set(self.tracing.requested_protocols())
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        # whenever there's a change in ingress, we need to update all tracing relations
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        self._update_tracing_relations()
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        # whenever there's a change in ingress, we need to update all tracing relations
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        self._update_tracing_relations()
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        """For charm tracing."""
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        """Server certificate for charm tracing tls, if tls is enabled."""
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        """Endpoint at which the charm tracing information will be forwarded."""
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py:from charms.tempo_k8s.v2.tracing import (
```

</details>


### 💬 Copilot

Now let me view the key tracing library files:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py

```
File too large to read at once (28.5 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py (lines 1-150)

<details>
<summary>150 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. """## Overview.
4. 
5. This document explains how to integrate with the Tempo charm for the purpose of pushing traces to a
6. tracing endpoint provided by Tempo. It also explains how alternative implementations of the Tempo charm
7. may maintain the same interface and be backward compatible with all currently integrated charms.
8. 
9. ## Requirer Library Usage
10. 
11. Charms seeking to push traces to Tempo, must do so using the `TracingEndpointRequirer`
12. object from this charm library. For the simplest use cases, using the `TracingEndpointRequirer`
13. object only requires instantiating it, typically in the constructor of your charm. The
14. `TracingEndpointRequirer` constructor requires the name of the relation over which a tracing endpoint
15.  is exposed by the Tempo charm, and a list of protocols it intends to send traces with.
16.  This relation must use the `tracing` interface.
17.  The `TracingEndpointRequirer` object may be instantiated as follows
18. 
19.     from charms.tempo_k8s.v2.tracing import TracingEndpointRequirer
20. 
21.     def __init__(self, *args):
22.         super().__init__(*args)
23.         # ...
24.         self.tracing = TracingEndpointRequirer(self,
25.             protocols=['otlp_grpc', 'otlp_http', 'jaeger_http_thrift']
26.         )
27.         # ...
28. 
29. Note that the first argument (`self`) to `TracingEndpointRequirer` is always a reference to the
30. parent charm.
31. 
32. Alternatively to providing the list of requested protocols at init time, the charm can do it at
33. any point in time by calling the
34. `TracingEndpointRequirer.request_protocols(*protocol:str, relation:Optional[Relation])` method.
35. Using this method also allows you to use per-relation protocols.
36. 
37. Units of provider charms obtain the tempo endpoint to which they will push their traces by calling
38. `TracingEndpointRequirer.get_endpoint(protocol: str)`, where `protocol` is, for example:
39. - `otlp_grpc`
40. - `otlp_http`
41. - `zipkin`
42. - `tempo`
43. 
44. If the `protocol` is not in the list of protocols that the charm requested at endpoint set-up time,
45. the library will raise an error.
46. 
47. ## Requirer Library Usage
48. 
49. The `TracingEndpointProvider` object may be used by charms to manage relations with their
50. trace sources. For this purposes a Tempo-like charm needs to do two things
51. 
52. 1. Instantiate the `TracingEndpointProvider` object by providing it a
53. reference to the parent (Tempo) charm and optionally the name of the relation that the Tempo charm
54. uses to interact with its trace sources. This relation must conform to the `tracing` interface
55. and it is strongly recommended that this relation be named `tracing` which is its
56. default value.
57. 
58. For example a Tempo charm may instantiate the `TracingEndpointProvider` in its constructor as
59. follows
60. 
61.     from charms.tempo_k8s.v2.tracing import TracingEndpointProvider
62. 
63.     def __init__(self, *args):
64.         super().__init__(*args)
65.         # ...
66.         self.tracing = TracingEndpointProvider(self)
67.         # ...
68. 
69. 
70. 
71. """  # noqa: W505
72. import enum
73. import json
74. import logging
75. from pathlib import Path
76. from typing import (
77.     TYPE_CHECKING,
78.     Any,
79.     Dict,
80.     List,
81.     Literal,
82.     MutableMapping,
83.     Optional,
84.     Sequence,
85.     Tuple,
86.     Union,
87.     cast,
88. )
89. 
90. import pydantic
91. from ops.charm import (
92.     CharmBase,
93.     CharmEvents,
94.     RelationBrokenEvent,
95.     RelationEvent,
96.     RelationRole,
97. )
98. from ops.framework import EventSource, Object
99. from ops.model import ModelError, Relation
100. from pydantic import BaseModel, Field
101. 
102. # The unique Charmhub library identifier, never change it
103. LIBID = "12977e9aa0b34367903d8afeb8c3d85d"
104. 
105. # Increment this major API version when introducing breaking changes
106. LIBAPI = 2
107. 
108. # Increment this PATCH version before using `charmcraft publish-lib` or reset
109. # to 0 if you are raising the major API version
110. LIBPATCH = 10
111. 
112. PYDEPS = ["pydantic"]
113. 
114. logger = logging.getLogger(__name__)
115. 
116. DEFAULT_RELATION_NAME = "tracing"
117. RELATION_INTERFACE_NAME = "tracing"
118. 
119. # Supported list rationale https://github.com/canonical/tempo-coordinator-k8s-operator/issues/8
120. ReceiverProtocol = Literal[
121.     "zipkin",
122.     "otlp_grpc",
123.     "otlp_http",
124.     "jaeger_grpc",
125.     "jaeger_thrift_http",
126. ]
127. 
128. RawReceiver = Tuple[ReceiverProtocol, str]
129. """Helper type. A raw receiver is defined as a tuple consisting of the protocol name, and the (external, if available),
130. (secured, if available) resolvable server url.
131. """
132. 
133. BUILTIN_JUJU_KEYS = {"ingress-address", "private-address", "egress-subnets"}
134. 
135. 
136. class TransportProtocolType(str, enum.Enum):
137.     """Receiver Type."""
138. 
139.     http = "http"
140.     grpc = "grpc"
141. 
142. 
143. receiver_protocol_to_transport_protocol: Dict[ReceiverProtocol, TransportProtocolType] = {
144.     "zipkin": TransportProtocolType.http,
145.     "otlp_grpc": TransportProtocolType.grpc,
146.     "otlp_http": TransportProtocolType.http,
147.     "jaeger_thrift_http": TransportProtocolType.http,
148.     "jaeger_grpc": TransportProtocolType.grpc,
149. }
150. """A mapping between telemetry protocols and their corresponding transport protocol.
```

</details>


### 💬 Copilot

Let me continue viewing the tracing library and the charm_tracing file:

### ✅ `bash`

**Check file lengths**

$ wc -l /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py

```
760 /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py
  996 /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py
 1756 total
<exited with exit code 0>
```


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py (lines 1-150)

<details>
<summary>150 lines</summary>

````
1. #!/usr/bin/env python3
2. # Copyright 2022 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """This charm library contains utilities to instrument your Charm with opentelemetry tracing data collection.
6. 
7. (yes! charm code, not workload code!)
8. 
9. This means that, if your charm is related to, for example, COS' Tempo charm, you will be able to inspect
10. in real time from the Grafana dashboard the execution flow of your charm.
11. 
12. # Quickstart
13. Fetch the following charm libs (and ensure the minimum version/revision numbers are satisfied):
14. 
15.     charmcraft fetch-lib charms.tempo_k8s.v2.tracing  # >= 1.10
16.     charmcraft fetch-lib charms.tempo_k8s.v1.charm_tracing  # >= 2.7
17. 
18. Then edit your charm code to include:
19. 
20. ```python
21. # import the necessary charm libs
22. from charms.tempo_k8s.v2.tracing import TracingEndpointRequirer, charm_tracing_config
23. from charms.tempo_k8s.v1.charm_tracing import charm_tracing
24. 
25. # decorate your charm class with charm_tracing:
26. @charm_tracing(
27.     # forward-declare the instance attributes that the instrumentor will look up to obtain the
28.     # tempo endpoint and server certificate
29.     tracing_endpoint="tracing_endpoint",
30.     server_cert="server_cert"
31. )
32. class MyCharm(CharmBase):
33.     _path_to_cert = "/path/to/cert.crt"
34.     # path to cert file **in the charm container**. Its presence will be used to determine whether
35.     # the charm is ready to use tls for encrypting charm traces. If your charm does not support tls,
36.     # you can ignore this and pass None to charm_tracing_config.
37.     # If you do support TLS, you'll need to make sure that the server cert is copied to this location
38.     # and kept up to date so the instrumentor can use it.
39. 
40.     def __init__(self, ...):
41.         ...
42.         self.tracing = TracingEndpointRequirer(self, ...)
43.         self.tracing_endpoint, self.server_cert = charm_tracing_config(self.tracing, self._path_to_cert)
44. ```
45. 
46. # Detailed usage
47. To use this library, you need to do two things:
48. 1) decorate your charm class with
49. 
50. `@trace_charm(tracing_endpoint="my_tracing_endpoint")`
51. 
52. 2) add to your charm a "my_tracing_endpoint" (you can name this attribute whatever you like)
53. **property**, **method** or **instance attribute** that returns an otlp http/https endpoint url.
54. If you are using the ``charms.tempo_k8s.v2.tracing.TracingEndpointRequirer`` as
55. ``self.tracing = TracingEndpointRequirer(self)``, the implementation could be:
56. 
57. ```
58.     @property
59.     def my_tracing_endpoint(self) -> Optional[str]:
60.         '''Tempo endpoint for charm tracing'''
61.         if self.tracing.is_ready():
62.             return self.tracing.get_endpoint("otlp_http")
63.         else:
64.             return None
65. ```
66. 
67. At this point your charm will be automatically instrumented so that:
68. - charm execution starts a trace, containing
69.     - every event as a span (including custom events)
70.     - every charm method call (except dunders) as a span
71. 
72. 
73. ## TLS support
74. If your charm integrates with a TLS provider which is also trusted by the tracing provider (the Tempo charm),
75. you can configure ``charm_tracing`` to use TLS by passing a ``server_cert`` parameter to the decorator.
76. 
77. If your charm is not trusting the same CA as the Tempo endpoint it is sending traces to,
78. you'll need to implement a cert-transfer relation to obtain the CA certificate from the same
79. CA that Tempo is using.
80. 
81. For example:
82. ```
83. from charms.tempo_k8s.v1.charm_tracing import trace_charm
84. @trace_charm(
85.     tracing_endpoint="my_tracing_endpoint",
86.     server_cert="_server_cert"
87. )
88. class MyCharm(CharmBase):
89.     self._server_cert = "/path/to/server.crt"
90.     ...
91. 
92.     def on_tls_changed(self, e) -> Optional[str]:
93.         # update the server cert on the charm container for charm tracing
94.         Path(self._server_cert).write_text(self.get_server_cert())
95. 
96.     def on_tls_broken(self, e) -> Optional[str]:
97.         # remove the server cert so charm_tracing won't try to use tls anymore
98.         Path(self._server_cert).unlink()
99. ```
100. 
101. 
102. ## More fine-grained manual instrumentation
103. if you wish to add more spans to the trace, you can do so by getting a hold of the tracer like so:
104. ```
105. import opentelemetry
106. ...
107. def get_tracer(self) -> opentelemetry.trace.Tracer:
108.     return opentelemetry.trace.get_tracer(type(self).__name__)
109. ```
110. 
111. By default, the tracer is named after the charm type. If you wish to override that, you can pass
112. a different ``service_name`` argument to ``trace_charm``.
113. 
114. See the official opentelemetry Python SDK documentation for usage:
115. https://opentelemetry-python.readthedocs.io/en/latest/
116. 
117. ## Upgrading from `v0`
118. 
119. If you are upgrading from `charm_tracing` v0, you need to take the following steps (assuming you already
120. have the newest version of the library in your charm):
121. 1) If you need the dependency for your tests, add the following dependency to your charm project
122. (or, if your project had a dependency on `opentelemetry-exporter-otlp-proto-grpc` only because
123. of `charm_tracing` v0, you can replace it with):
124. 
125. `opentelemetry-exporter-otlp-proto-http>=1.21.0`.
126. 
127. 2) Update the charm method referenced to from ``@trace`` and ``@trace_charm``,
128. to return from ``TracingEndpointRequirer.get_endpoint("otlp_http")`` instead of ``grpc_http``.
129. For example:
130. 
131. ```
132.     from charms.tempo_k8s.v0.charm_tracing import trace_charm
133. 
134.     @trace_charm(
135.         tracing_endpoint="my_tracing_endpoint",
136.     )
137.     class MyCharm(CharmBase):
138. 
139.     ...
140. 
141.         @property
142.         def my_tracing_endpoint(self) -> Optional[str]:
143.             '''Tempo endpoint for charm tracing'''
144.             if self.tracing.is_ready():
145.                 return self.tracing.otlp_grpc_endpoint() #  OLD API, DEPRECATED.
146.             else:
147.                 return None
148. ```
149. 
150. needs to be replaced with:
````

</details>


### 💬 Copilot

Let me continue viewing the charm.py file to see how tracing is used in the complete context:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py (lines 100-250)

<details>
<summary>151 lines</summary>

```
100.         )
101. 
102.         self.tracing = TracingEndpointProvider(self, external_url=self._external_url)
103. 
104.         if not self.is_consistent():
105.             logger.error(
106.                 f"Inconsistent deployment. {self.unit.name} will be shutting down. "
107.                 "This likely means you need to add an s3 integration. "
108.                 "This charm will be unresponsive and refuse to handle any event until "
109.                 "the situation is resolved by the cloud admin, to avoid data loss."
110.             )
111.             self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)
112. 
113.             if self.tempo.is_tempo_service_defined:
114.                 self.tempo.shutdown()
115. 
116.             return  # refuse to handle any other event as we can't possibly know what to do.
117. 
118.         self.framework.observe(
119.             self.on["ingress"].relation_created, self._on_ingress_relation_created
120.         )
121.         self.framework.observe(
122.             self.on["ingress"].relation_joined, self._on_ingress_relation_joined
123.         )
124.         self.framework.observe(self.on.leader_elected, self._on_leader_elected)
125.         self.framework.observe(self.on.leader_settings_changed, self._on_leader_settings_changed)
126.         self.framework.observe(self.ingress.on.ready, self._on_ingress_ready)
127. 
128.         self.framework.observe(self.on.tempo_pebble_ready, self._on_tempo_pebble_ready)
129.         self.framework.observe(
130.             self.on.tempo_pebble_custom_notice, self._on_tempo_pebble_custom_notice
131.         )
132.         self.framework.observe(self.on.update_status, self._on_update_status)
133.         self.framework.observe(
134.             self.s3_requirer.on.credentials_changed, self._on_s3_credentials_changed
135.         )
136.         self.framework.observe(self.s3_requirer.on.credentials_gone, self._on_s3_credentials_gone)
137.         self.framework.observe(self.tracing.on.request, self._on_tracing_request)
138.         self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)
139.         self.framework.observe(self.on.list_receivers_action, self._on_list_receivers_action)
140.         self.framework.observe(self.cert_handler.on.cert_changed, self._on_cert_handler_changed)
141.         self.framework.observe(self.on.config_changed, self._on_config_changed)
142.         self.framework.observe(self.tracing.on.broken, self._on_tracing_broken)
143.         self.framework.observe(
144.             self.on.tempo_peers_relation_created, self._on_tempo_peers_relation_created
145.         )
146.         self.framework.observe(
147.             self.on.tempo_peers_relation_changed, self._on_tempo_peers_relation_changed
148.         )
149. 
150.     @property
151.     def _external_http_server_url(self) -> str:
152.         """External url of the http(s) server."""
153.         return f"{self._external_url}:{self.tempo.tempo_http_server_port}"
154. 
155.     @property
156.     def _external_url(self) -> str:
157.         """Return the external url."""
158.         if self.ingress.is_ready():
159.             ingress_url = f"{self.ingress.scheme}://{self.ingress.external_host}"
160.             logger.debug("This unit's ingress URL: %s", ingress_url)
161.             return ingress_url
162. 
163.         # If we do not have an ingress, then use the pod hostname.
164.         # The reason to prefer this over the pod name (which is the actual
165.         # hostname visible from the pod) or a K8s service, is that those
166.         # are routable virtually exclusively inside the cluster (as they rely)
167.         # on the cluster's DNS service, while the ip address is _sometimes_
168.         # routable from the outside, e.g., when deploying on MicroK8s on Linux.
169.         return self._internal_url
170. 
171.     @property
172.     def _internal_url(self) -> str:
173.         scheme = "https" if self.tls_available else "http"
174.         return f"{scheme}://{self.hostname}"
175. 
176.     @property
177.     def tls_available(self) -> bool:
178.         """Return True if tls is enabled and the necessary certs are found."""
179.         return (
180.             self.cert_handler.enabled
181.             and (self.cert_handler.server_cert is not None)
182.             and (self.cert_handler.private_key is not None)
183.             and (self.cert_handler.ca_cert is not None)
184.         )
185. 
186.     @property
187.     def _s3_config(self) -> Optional[dict]:
188.         if not self.s3_requirer.relations:
189.             return None
190.         s3_config = self.s3_requirer.get_s3_connection_info()
191.         if (
192.             s3_config
193.             and "bucket" in s3_config
194.             and "endpoint" in s3_config
195.             and "access-key" in s3_config
196.             and "secret-key" in s3_config
197.         ):
198.             return s3_config
199.         return None
200. 
201.     def _on_tracing_broken(self, _):
202.         """Update tracing relations' databags once one relation is removed."""
203.         self._update_tracing_relations()
204. 
205.     def _on_cert_handler_changed(self, _):
206.         was_ready = self.tempo.tls_ready
207. 
208.         if self.tls_available:
209.             logger.debug("enabling TLS")
210.             self.tempo.configure_tls(
211.                 cert=self.cert_handler.server_cert,  # type: ignore
212.                 key=self.cert_handler.private_key,  # type: ignore
213.                 ca=self.cert_handler.ca_cert,  # type: ignore
214.             )
215.         else:
216.             logger.debug("disabling TLS")
217.             self.tempo.clear_tls_config()
218. 
219.         if was_ready != self.tempo.tls_ready:
220.             # tls readiness change means config change.
221.             self._update_tempo_config()
222.             # sync scheme change with traefik and related consumers
223.             self._configure_ingress()
224. 
225.             if self.tempo.is_tempo_service_defined:
226.                 self.tempo.restart()
227. 
228.         # sync the server cert with the charm container.
229.         # technically, because of charm tracing, this will be called first thing on each event
230.         self._update_server_cert()
231. 
232.         # update relations to reflect the new certificate
233.         self._update_tracing_relations()
234. 
235.     def _configure_ingress(self) -> None:
236.         """Make sure the traefik route and tracing relation data are up-to-date."""
237.         if not self.unit.is_leader():
238.             return
239. 
240.         if self.ingress.is_ready():
241.             self.ingress.submit_to_traefik(
242.                 self._ingress_config, static=self._static_ingress_config
243.             )
244.             if self.ingress.external_host:
245.                 self._update_tracing_relations()
246. 
247.     def _on_tracing_request(self, e: RequestEvent):
248.         """Handle a remote requesting a tracing endpoint."""
249.         logger.debug(f"received tracing request from {e.relation.app}: {e.requested_receivers}")
250.         self._update_tracing_relations()
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py (lines 250-400)

<details>
<summary>151 lines</summary>

```
250.         self._update_tracing_relations()
251. 
252.     def _on_ingress_relation_created(self, _: RelationEvent):
253.         self._configure_ingress()
254. 
255.     def _on_ingress_relation_joined(self, _: RelationEvent):
256.         self._configure_ingress()
257. 
258.     def _on_leader_settings_changed(self, _: ops.LeaderSettingsChangedEvent):
259.         if not self._is_s3_ready():
260.             logger.error(
261.                 "Losing leadership without s3. " "This unit will soon be in an inconsistent state."
262.             )
263. 
264.     def _on_leader_elected(self, _: ops.LeaderElectedEvent):
265.         # as traefik_route goes through app data, we need to take lead of traefik_route if our leader dies.
266.         self._configure_ingress()
267. 
268.     def _on_s3_credentials_changed(self, _):
269.         self._on_s3_changed()
270. 
271.     def _on_s3_credentials_gone(self, _):
272.         self._on_s3_changed()
273. 
274.     def _on_s3_changed(self):
275.         could_scale_before = self.tempo.can_scale()
276. 
277.         self._update_tempo_config()
278. 
279.         can_scale_now = self.tempo.can_scale()
280.         # if we had s3, and we don't anymore, we need to replan from 'scaling-monolithic' to 'all'
281.         # if we didn't have s3, and now we do, we can replan from 'all' to 'scaling-monolithic'
282.         if could_scale_before != can_scale_now:
283.             if self.tempo.is_tempo_service_defined:
284.                 self.tempo.plan()
285.             else:
286.                 # assume that this will be handled at the next pebble-ready
287.                 logger.debug("Cannot reconfigure/restart tempo at this time.")
288. 
289.     def _on_tempo_peers_relation_created(self, event: ops.RelationCreatedEvent):
290.         if self._local_ip:
291.             event.relation.data[self.unit]["local-ip"] = self._local_ip
292. 
293.     def _on_tempo_peers_relation_changed(self, _):
294.         if self._update_tempo_config():
295.             self.tempo.restart()
296. 
297.     def _update_tempo_config(self) -> bool:
298.         peers = self.peers()
299.         relation = self.model.get_relation("tempo-peers")
300.         # get unit addresses for all the other units from a databag
301.         if peers and relation:
302.             addresses = [relation.data[unit].get("local-ip") for unit in peers]
303.             addresses = list(filter(None, addresses))
304.         else:
305.             addresses = []
306. 
307.         # add own address
308.         if self._local_ip:
309.             addresses.append(self._local_ip)
310. 
311.         return self.tempo.update_config(self._requested_receivers(), self._s3_config, addresses)
312. 
313.     @property
314.     def _local_ip(self) -> Optional[str]:
315.         binding = self.model.get_binding("tempo-peers")
316.         if binding and binding._relation_id:
317.             return str(binding.network.bind_address)
318.         return None
319. 
320.     def _on_config_changed(self, _):
321.         # check if certificate files haven't disappeared and recreate them if needed
322.         if self.tls_available and not self.tempo.tls_ready:
323.             logger.debug("enabling TLS")
324.             self.tempo.configure_tls(
325.                 cert=self.cert_handler.server_cert,  # type: ignore
326.                 key=self.cert_handler.private_key,  # type: ignore
327.                 ca=self.cert_handler.ca_cert,  # type: ignore
328.             )
329. 
330.     def _update_tracing_relations(self):
331.         tracing_relations = self.model.relations["tracing"]
332.         if not tracing_relations:
333.             # todo: set waiting status and configure tempo to run without receivers if possible,
334.             #  else perhaps postpone starting the workload at all.
335.             logger.warning("no tracing relations: Tempo has no receivers configured.")
336.             return
337. 
338.         requested_receivers = self._requested_receivers()
339.         # publish requested protocols to all relations
340.         if self.unit.is_leader():
341.             self.tracing.publish_receivers(
342.                 [(p, self.tempo.get_receiver_url(p, self.ingress)) for p in requested_receivers]
343.             )
344. 
345.         self._restart_if_receivers_changed()
346. 
347.     def _restart_if_receivers_changed(self):
348.         # if the receivers have changed, we need to reconfigure tempo
349.         self.unit.status = MaintenanceStatus("reconfiguring Tempo...")
350.         updated = self._update_tempo_config()
351.         if not updated:
352.             logger.debug("Config not updated; skipping tempo restart")
353.         if updated:
354.             restarted = self.tempo.is_tempo_service_defined and self.tempo.restart()
355.             if not restarted:
356.                 # assume that this will be handled at the next pebble-ready
357.                 logger.debug("Cannot reconfigure/restart tempo at this time.")
358. 
359.     def _requested_receivers(self) -> Tuple[ReceiverProtocol, ...]:
360.         """List what receivers we should activate, based on the active tracing relations."""
361.         # we start with the sum of the requested endpoints from the requirers
362.         requested_protocols = set(self.tracing.requested_protocols())
363. 
364.         # and publish only those we support
365.         requested_receivers = requested_protocols.intersection(set(self.tempo.receiver_ports))
366.         requested_receivers.update(self.tempo.enabled_receivers)
367.         return tuple(requested_receivers)
368. 
369.     def _on_tempo_pebble_custom_notice(self, event: PebbleNoticeEvent):
370.         if event.notice.key == self.tempo.tempo_ready_notice_key:
371.             # collect-unit-status should now report ready.
372.             logger.debug("pebble api reports ready")
373. 
374.             try:
375.                 self.tempo.container.stop("tempo-ready")
376.                 # ops will fire APIError but ops.testing._TestingPebbleClient will fire RuntimeError.
377.             except (APIError, RuntimeError):
378.                 # see https://matrix.to/#/!xzmWHtGpPfVCXKivIh:ubuntu.com/
379.                 #  $d42wOu61e5mqMhnDRUB6K8eV4kUAPQ_yhIQmqq5Q_cs?via=ubuntu.com&
380.                 #  via=matrix.org&via=matrix.debian.social
381.                 # issue: on sleep/resume, we get this event but there's no tempo-ready
382.                 # service in pebble (somehow?)
383.                 logger.debug(
384.                     "`tempo-ready` service cannot be stopped at this time (probably doesn't exist)."
385.                 )
386. 
387.     def _on_tempo_pebble_ready(self, event: WorkloadEvent):
388.         if not self.tempo.container.can_connect():
389.             logger.warning("container not ready, cannot configure; will retry soon")
390.             return event.defer()
391. 
392.         self._update_tempo_config()
393.         self.tempo.plan()
394. 
395.         self.unit.set_workload_version(self.version)
396.         self.unit.status = ActiveStatus()
397. 
398.     def _on_update_status(self, _):
399.         """Update the status of the application."""
400.         self.unit.set_workload_version(self.version)
```

</details>


### 💬 Copilot

Now let me view the rest and get more specific tracing endpoints info:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py (lines 400-550)

<details>
<summary>151 lines</summary>

```
400.         self.unit.set_workload_version(self.version)
401. 
402.     def _on_ingress_ready(self, _event):
403.         # whenever there's a change in ingress, we need to update all tracing relations
404.         self._update_tracing_relations()
405. 
406.     def _on_ingress_revoked(self, _event):
407.         # whenever there's a change in ingress, we need to update all tracing relations
408.         self._update_tracing_relations()
409. 
410.     @property
411.     def version(self) -> str:
412.         """Reports the current Tempo version."""
413.         container = self.unit.get_container("tempo")
414.         if container.can_connect() and container.get_services("tempo"):
415.             try:
416.                 return self._get_version() or ""
417.             # Catching Exception is not ideal, but we don't care much for the error here, and just
418.             # default to setting a blank version since there isn't much the admin can do!
419.             except Exception as e:
420.                 logger.warning("unable to get version from API: %s", str(e))
421.                 logger.debug(e, exc_info=True)
422.                 return ""
423.         return ""
424. 
425.     def _get_version(self) -> Optional[str]:
426.         """Fetch the version from the running workload using the Tempo CLI.
427. 
428.         Helper function.
429.         """
430.         container = self.unit.get_container("tempo")
431.         proc = container.exec(["/tempo", "-version"])
432.         out, err = proc.wait_output()
433. 
434.         # example output:
435.         # / # /tempo --version
436.         # tempo, version  (branch: HEAD, revision: fd5743d5d)
437.         #   build user:
438.         #   build date:
439.         #   go version:       go1.18.5
440.         #   platform:         linux/amd64
441. 
442.         if version_head := re.search(r"tempo, version (.*) \(branch: (.*), revision: (.*)\)", out):
443.             v_head, b_head, r_head = version_head.groups()
444.             version = f"{v_head}:{b_head}/{r_head}"
445.         elif version_headless := re.search(r"tempo, version (\S+)", out):
446.             version = version_headless.groups()[0]
447.         else:
448.             logger.warning(
449.                 f"unable to determine tempo workload version: output {out} "
450.                 f"does not match any known pattern"
451.             )
452.             return
453.         return version
454. 
455.     def server_cert(self):
456.         """For charm tracing."""
457.         self._update_server_cert()
458.         return self.tempo.server_cert_path
459. 
460.     def _update_server_cert(self):
461.         """Server certificate for charm tracing tls, if tls is enabled."""
462.         server_cert = Path(self.tempo.server_cert_path)
463.         if self.tls_available:
464.             if not server_cert.exists():
465.                 server_cert.parent.mkdir(parents=True, exist_ok=True)
466.                 if self.cert_handler.server_cert:
467.                     server_cert.write_text(self.cert_handler.server_cert)
468.         else:  # tls unavailable: delete local cert
469.             server_cert.unlink(missing_ok=True)
470. 
471.     def tempo_otlp_http_endpoint(self) -> Optional[str]:
472.         """Endpoint at which the charm tracing information will be forwarded."""
473.         # the charm container and the tempo workload container have apparently the same
474.         # IP, so we can talk to tempo at localhost.
475.         if self.tempo.is_ready():
476.             return f"{self._internal_url}:{self.tempo.receiver_ports['otlp_http']}"
477. 
478.         return None
479. 
480.     def is_scaled(self) -> bool:
481.         """Check whether Tempo is deployed with scale > 1."""
482.         # TODO write ADR for deployment model: tempo-k8s monolithic + scalable monolithic + coordinator
483.         relation = self.model.get_relation("tempo-peers")
484.         if not relation:
485.             return False
486. 
487.         # self is not included in relation.units
488.         return bool(relation.units)
489. 
490.     def peers(self) -> Optional[Set[ops.model.Unit]]:
491.         """Return charm's peer units."""
492.         relation = self.model.get_relation("tempo-peers")
493.         if not relation:
494.             return None
495. 
496.         # self is not included in relation.units
497.         return relation.units
498. 
499.     def is_consistent(self):
500.         """Check deployment consistency."""
501.         if self.is_scaled() and not self._is_s3_ready():
502.             return False
503.         return True
504. 
505.     def _is_s3_ready(self) -> bool:
506.         return bool(self._s3_config)
507. 
508.     def _on_collect_unit_status(self, e: CollectStatusEvent):
509.         if not self.is_consistent():
510.             e.add_status(
511.                 BlockedStatus(
512.                     "Unit *disabled*. Cannot scale Tempo without adding an s3 integration."
513.                 )
514.             )
515.         if not self.tempo.container.can_connect():
516.             e.add_status(WaitingStatus("Tempo container not ready"))
517.         if not self.tempo.is_ready():
518.             e.add_status(WaitingStatus("Tempo API not ready just yet..."))
519. 
520.         e.add_status(ActiveStatus())
521. 
522.     @property
523.     def hostname(self) -> str:
524.         """Unit's hostname."""
525.         return socket.getfqdn()
526. 
527.     def _on_list_receivers_action(self, event: ops.ActionEvent):
528.         res = {}
529.         for receiver in self._requested_receivers():
530.             res[receiver.replace("_", "-")] = (
531.                 f"{self.ingress.external_host or self.tempo.url}:{self.tempo.receiver_ports[receiver]}"
532.             )
533.         event.set_results(res)
534. 
535.     @property
536.     def _static_ingress_config(self) -> dict:
537.         entry_points = {}
538.         for protocol, port in self.tempo.all_ports.items():
539.             sanitized_protocol = protocol.replace("_", "-")
540.             entry_points[sanitized_protocol] = {"address": f":{port}"}
541. 
542.         return {"entryPoints": entry_points}
543. 
544.     @property
545.     def _ingress_config(self) -> dict:
546.         """Build a raw ingress configuration for Traefik."""
547.         http_routers = {}
548.         http_services = {}
549.         for protocol, port in self.tempo.all_ports.items():
550.             sanitized_protocol = protocol.replace("_", "-")
```

</details>


### ✅ `grep`

**/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src**

"tempo_otlp_http_endpoint|server_cert" (/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src)

<details>
<summary>20 matches</summary>

```
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    tracing_endpoint="tempo_otlp_http_endpoint",
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    server_cert="server_cert",
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:            and (self.cert_handler.server_cert is not None)
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:                cert=self.cert_handler.server_cert,  # type: ignore
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        self._update_server_cert()
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:                cert=self.cert_handler.server_cert,  # type: ignore
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    def server_cert(self):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        self._update_server_cert()
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        return self.tempo.server_cert_path
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    def _update_server_cert(self):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:        server_cert = Path(self.tempo.server_cert_path)
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:            if not server_cert.exists():
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:                server_cert.parent.mkdir(parents=True, exist_ok=True)
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:                if self.cert_handler.server_cert:
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:                    server_cert.write_text(self.cert_handler.server_cert)
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:            server_cert.unlink(missing_ok=True)
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py:    def tempo_otlp_http_endpoint(self) -> Optional[str]:
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py:    server_cert_path = "/usr/local/share/ca-certificates/ca.crt"
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py:        Path(self.server_cert_path).write_text(ca)
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py:            tls, s = f" --cacert {self.server_cert_path}", "s"
```

</details>


### 💬 Copilot

Perfect! Now let me get more details on the tracing endpoints and protocols:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py (lines 150-350)

<details>
<summary>201 lines</summary>

```
150. """A mapping between telemetry protocols and their corresponding transport protocol.
151. """
152. 
153. 
154. class TracingError(Exception):
155.     """Base class for custom errors raised by this library."""
156. 
157. 
158. class NotReadyError(TracingError):
159.     """Raised by the provider wrapper if a requirer hasn't published the required data (yet)."""
160. 
161. 
162. class ProtocolNotRequestedError(TracingError):
163.     """Raised if the user attempts to obtain an endpoint for a protocol it did not request."""
164. 
165. 
166. class DataValidationError(TracingError):
167.     """Raised when data validation fails on IPU relation data."""
168. 
169. 
170. class AmbiguousRelationUsageError(TracingError):
171.     """Raised when one wrongly assumes that there can only be one relation on an endpoint."""
172. 
173. 
174. if int(pydantic.version.VERSION.split(".")[0]) < 2:
175. 
176.     class DatabagModel(BaseModel):  # type: ignore
177.         """Base databag model."""
178. 
179.         class Config:
180.             """Pydantic config."""
181. 
182.             # ignore any extra fields in the databag
183.             extra = "ignore"
184.             """Ignore any extra fields in the databag."""
185.             allow_population_by_field_name = True
186.             """Allow instantiating this class by field name (instead of forcing alias)."""
187. 
188.         _NEST_UNDER = None
189. 
190.         @classmethod
191.         def load(cls, databag: MutableMapping):
192.             """Load this model from a Juju databag."""
193.             if cls._NEST_UNDER:
194.                 return cls.parse_obj(json.loads(databag[cls._NEST_UNDER]))
195. 
196.             try:
197.                 data = {
198.                     k: json.loads(v)
199.                     for k, v in databag.items()
200.                     # Don't attempt to parse model-external values
201.                     if k in {f.alias for f in cls.__fields__.values()}
202.                 }
203.             except json.JSONDecodeError as e:
204.                 msg = f"invalid databag contents: expecting json. {databag}"
205.                 logger.error(msg)
206.                 raise DataValidationError(msg) from e
207. 
208.             try:
209.                 return cls.parse_raw(json.dumps(data))  # type: ignore
210.             except pydantic.ValidationError as e:
211.                 msg = f"failed to validate databag: {databag}"
212.                 logger.debug(msg, exc_info=True)
213.                 raise DataValidationError(msg) from e
214. 
215.         def dump(self, databag: Optional[MutableMapping] = None, clear: bool = True):
216.             """Write the contents of this model to Juju databag.
217. 
218.             :param databag: the databag to write the data to.
219.             :param clear: ensure the databag is cleared before writing it.
220.             """
221.             if clear and databag:
222.                 databag.clear()
223. 
224.             if databag is None:
225.                 databag = {}
226. 
227.             if self._NEST_UNDER:
228.                 databag[self._NEST_UNDER] = self.json(by_alias=True)
229.                 return databag
230. 
231.             dct = self.dict()
232.             for key, field in self.__fields__.items():  # type: ignore
233.                 value = dct[key]
234.                 databag[field.alias or key] = json.dumps(value)
235. 
236.             return databag
237. 
238. else:
239.     from pydantic import ConfigDict
240. 
241.     class DatabagModel(BaseModel):
242.         """Base databag model."""
243. 
244.         model_config = ConfigDict(
245.             # ignore any extra fields in the databag
246.             extra="ignore",
247.             # Allow instantiating this class by field name (instead of forcing alias).
248.             populate_by_name=True,
249.             # Custom config key: whether to nest the whole datastructure (as json)
250.             # under a field or spread it out at the toplevel.
251.             _NEST_UNDER=None,  # type: ignore
252.         )
253.         """Pydantic config."""
254. 
255.         @classmethod
256.         def load(cls, databag: MutableMapping):
257.             """Load this model from a Juju databag."""
258.             nest_under = cls.model_config.get("_NEST_UNDER")  # type: ignore
259.             if nest_under:
260.                 return cls.model_validate(json.loads(databag[nest_under]))  # type: ignore
261. 
262.             try:
263.                 data = {
264.                     k: json.loads(v)
265.                     for k, v in databag.items()
266.                     # Don't attempt to parse model-external values
267.                     if k in {(f.alias or n) for n, f in cls.__fields__.items()}
268.                 }
269.             except json.JSONDecodeError as e:
270.                 msg = f"invalid databag contents: expecting json. {databag}"
271.                 logger.error(msg)
272.                 raise DataValidationError(msg) from e
273. 
274.             try:
275.                 return cls.model_validate_json(json.dumps(data))  # type: ignore
276.             except pydantic.ValidationError as e:
277.                 msg = f"failed to validate databag: {databag}"
278.                 logger.debug(msg, exc_info=True)
279.                 raise DataValidationError(msg) from e
280. 
281.         def dump(self, databag: Optional[MutableMapping] = None, clear: bool = True):
282.             """Write the contents of this model to Juju databag.
283. 
284.             :param databag: the databag to write the data to.
285.             :param clear: ensure the databag is cleared before writing it.
286.             """
287.             if clear and databag:
288.                 databag.clear()
289. 
290.             if databag is None:
291.                 databag = {}
292.             nest_under = self.model_config.get("_NEST_UNDER")
293.             if nest_under:
294.                 databag[nest_under] = self.model_dump_json(  # type: ignore
295.                     by_alias=True,
296.                     # skip keys whose values are default
297.                     exclude_defaults=True,
298.                 )
299.                 return databag
300. 
301.             dct = self.model_dump()  # type: ignore
302.             for key, field in self.model_fields.items():  # type: ignore
303.                 value = dct[key]
304.                 if value == field.default:
305.                     continue
306.                 databag[field.alias or key] = json.dumps(value)
307. 
308.             return databag
309. 
310. 
311. # todo use models from charm-relation-interfaces
312. if int(pydantic.version.VERSION.split(".")[0]) < 2:
313. 
314.     class ProtocolType(BaseModel):  # type: ignore
315.         """Protocol Type."""
316. 
317.         class Config:
318.             """Pydantic config."""
319. 
320.             use_enum_values = True
321.             """Allow serializing enum values."""
322. 
323.         name: str = Field(
324.             ...,
325.             description="Receiver protocol name. What protocols are supported (and what they are called) "
326.             "may differ per provider.",
327.             examples=["otlp_grpc", "otlp_http", "tempo_http"],
328.         )
329. 
330.         type: TransportProtocolType = Field(
331.             ...,
332.             description="The transport protocol used by this receiver.",
333.             examples=["http", "grpc"],
334.         )
335. 
336. else:
337. 
338.     class ProtocolType(BaseModel):
339.         """Protocol Type."""
340. 
341.         model_config = ConfigDict(  # type: ignore
342.             # Allow serializing enum values.
343.             use_enum_values=True
344.         )
345.         """Pydantic config."""
346. 
347.         name: str = Field(
348.             ...,
349.             description="Receiver protocol name. What protocols are supported (and what they are called) "
350.             "may differ per provider.",
```

</details>


### ✅ `bash`

**Find key tracing interface methods**

$ grep -n "receiver_protocol_to_transport_protocol\|ReceiverProtocol\|get_endpoint\|publish_receivers\|class TracingEndpointProvider" /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py | head -40

<details>
<summary>19 lines</summary>

```
38:`TracingEndpointRequirer.get_endpoint(protocol: str)`, where `protocol` is, for example:
120:ReceiverProtocol = Literal[
128:RawReceiver = Tuple[ReceiverProtocol, str]
143:receiver_protocol_to_transport_protocol: Dict[ReceiverProtocol, TransportProtocolType] = {
392:    receivers: List[ReceiverProtocol]
548:    def requested_receivers(self) -> List[ReceiverProtocol]:
562:class TracingEndpointProviderEvents(CharmEvents):
569:class TracingEndpointProvider(Object):
666:    def publish_receivers(self, receivers: Sequence[RawReceiver]):
679:                                type=receiver_protocol_to_transport_protocol[protocol],
735:        protocols: Optional[List[ReceiverProtocol]] = None,
784:        self, protocols: Sequence[ReceiverProtocol], relation: Optional[Relation] = None
881:    def _get_endpoint(
882:        self, relation: Optional[Relation], protocol: ReceiverProtocol
902:    def get_endpoint(
903:        self, protocol: ReceiverProtocol, relation: Optional[Relation] = None
915:        endpoint = self._get_endpoint(relation or self._relation, protocol=protocol)
981:    endpoint = endpoint_requirer.get_endpoint("otlp_http")
<exited with exit code 0>
```

</details>


### 💬 Copilot

Great! Now let me get a comprehensive view of the charm_tracing decorator and check imports across the codebase:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py (lines 150-300)

<details>
<summary>151 lines</summary>

````
150. needs to be replaced with:
151. 
152. ```
153.     from charms.tempo_k8s.v1.charm_tracing import trace_charm
154. 
155.     @trace_charm(
156.         tracing_endpoint="my_tracing_endpoint",
157.     )
158.     class MyCharm(CharmBase):
159. 
160.     ...
161. 
162.         @property
163.         def my_tracing_endpoint(self) -> Optional[str]:
164.             '''Tempo endpoint for charm tracing'''
165.             if self.tracing.is_ready():
166.                 return self.tracing.get_endpoint("otlp_http")  # NEW API, use this.
167.             else:
168.                 return None
169. ```
170. 
171. 3) If you were passing a certificate (str) using `server_cert`, you need to change it to
172. provide an *absolute* path to the certificate file instead.
173. """
174. 
175. 
176. def _remove_stale_otel_sdk_packages():
177.     """Hack to remove stale opentelemetry sdk packages from the charm's python venv.
178. 
179.     See https://github.com/canonical/grafana-agent-operator/issues/146 and
180.     https://bugs.launchpad.net/juju/+bug/2058335 for more context. This patch can be removed after
181.     this juju issue is resolved and sufficient time has passed to expect most users of this library
182.     have migrated to the patched version of juju.  When this patch is removed, un-ignore rule E402 for this file in the pyproject.toml (see setting
183.     [tool.ruff.lint.per-file-ignores] in pyproject.toml).
184. 
185.     This only has an effect if executed on an upgrade-charm event.
186.     """
187.     # all imports are local to keep this function standalone, side-effect-free, and easy to revert later
188.     import os
189. 
190.     if os.getenv("JUJU_DISPATCH_PATH") != "hooks/upgrade-charm":
191.         return
192. 
193.     import logging
194.     import shutil
195.     from collections import defaultdict
196. 
197.     from importlib_metadata import distributions
198. 
199.     otel_logger = logging.getLogger("charm_tracing_otel_patcher")
200.     otel_logger.debug("Applying _remove_stale_otel_sdk_packages patch on charm upgrade")
201.     # group by name all distributions starting with "opentelemetry_"
202.     otel_distributions = defaultdict(list)
203.     for distribution in distributions():
204.         name = distribution._normalized_name  # type: ignore
205.         if name.startswith("opentelemetry_"):
206.             otel_distributions[name].append(distribution)
207. 
208.     otel_logger.debug(f"Found {len(otel_distributions)} opentelemetry distributions")
209. 
210.     # If we have multiple distributions with the same name, remove any that have 0 associated files
211.     for name, distributions_ in otel_distributions.items():
212.         if len(distributions_) <= 1:
213.             continue
214. 
215.         otel_logger.debug(f"Package {name} has multiple ({len(distributions_)}) distributions.")
216.         for distribution in distributions_:
217.             if not distribution.files:  # Not None or empty list
218.                 path = distribution._path  # type: ignore
219.                 otel_logger.info(f"Removing empty distribution of {name} at {path}.")
220.                 shutil.rmtree(path)
221. 
222.     otel_logger.debug("Successfully applied _remove_stale_otel_sdk_packages patch. ")
223. 
224. 
225. _remove_stale_otel_sdk_packages()
226. 
227. import functools
228. import inspect
229. import logging
230. import os
231. from contextlib import contextmanager
232. from contextvars import Context, ContextVar, copy_context
233. from pathlib import Path
234. from typing import (
235.     Any,
236.     Callable,
237.     Generator,
238.     Optional,
239.     Sequence,
240.     Type,
241.     TypeVar,
242.     Union,
243.     cast,
244. )
245. 
246. import opentelemetry
247. import ops
248. from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
249. from opentelemetry.sdk.resources import Resource
250. from opentelemetry.sdk.trace import Span, TracerProvider
251. from opentelemetry.sdk.trace.export import BatchSpanProcessor
252. from opentelemetry.trace import (
253.     INVALID_SPAN,
254.     Tracer,
255.     get_tracer,
256.     get_tracer_provider,
257.     set_span_in_context,
258.     set_tracer_provider,
259. )
260. from opentelemetry.trace import get_current_span as otlp_get_current_span
261. from ops.charm import CharmBase
262. from ops.framework import Framework
263. 
264. # The unique Charmhub library identifier, never change it
265. LIBID = "cb1705dcd1a14ca09b2e60187d1215c7"
266. 
267. # Increment this major API version when introducing breaking changes
268. LIBAPI = 1
269. 
270. # Increment this PATCH version before using `charmcraft publish-lib` or reset
271. # to 0 if you are raising the major API version
272. 
273. LIBPATCH = 15
274. 
275. PYDEPS = ["opentelemetry-exporter-otlp-proto-http==1.21.0"]
276. 
277. logger = logging.getLogger("tracing")
278. dev_logger = logging.getLogger("tracing-dev")
279. 
280. # set this to 0 if you are debugging/developing this library source
281. dev_logger.setLevel(logging.CRITICAL)
282. 
283. _CharmType = Type[CharmBase]  # the type CharmBase and any subclass thereof
284. _C = TypeVar("_C", bound=_CharmType)
285. _T = TypeVar("_T", bound=type)
286. _F = TypeVar("_F", bound=Type[Callable])
287. tracer: ContextVar[Tracer] = ContextVar("tracer")
288. _GetterType = Union[Callable[[_CharmType], Optional[str]], property]
289. 
290. CHARM_TRACING_ENABLED = "CHARM_TRACING_ENABLED"
291. 
292. 
293. def is_enabled() -> bool:
294.     """Whether charm tracing is enabled."""
295.     return os.getenv(CHARM_TRACING_ENABLED, "1") == "1"
296. 
297. 
298. @contextmanager
299. def charm_tracing_disabled():
300.     """Contextmanager to temporarily disable charm tracing.
````

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py (lines 300-450)

<details>
<summary>151 lines</summary>

```
300.     """Contextmanager to temporarily disable charm tracing.
301. 
302.     For usage in tests.
303.     """
304.     previous = os.getenv(CHARM_TRACING_ENABLED, "1")
305.     os.environ[CHARM_TRACING_ENABLED] = "0"
306.     yield
307.     os.environ[CHARM_TRACING_ENABLED] = previous
308. 
309. 
310. def get_current_span() -> Union[Span, None]:
311.     """Return the currently active Span, if there is one, else None.
312. 
313.     If you'd rather keep your logic unconditional, you can use opentelemetry.trace.get_current_span,
314.     which will return an object that behaves like a span but records no data.
315.     """
316.     span = otlp_get_current_span()
317.     if span is INVALID_SPAN:
318.         return None
319.     return cast(Span, span)
320. 
321. 
322. def _get_tracer_from_context(ctx: Context) -> Optional[ContextVar]:
323.     tracers = [v for v in ctx if v is not None and v.name == "tracer"]
324.     if tracers:
325.         return tracers[0]
326.     return None
327. 
328. 
329. def _get_tracer() -> Optional[Tracer]:
330.     """Find tracer in context variable and as a fallback locate it in the full context."""
331.     try:
332.         return tracer.get()
333.     except LookupError:
334.         # fallback: this course-corrects for a user error where charm_tracing symbols are imported
335.         # from different paths (typically charms.tempo_k8s... and lib.charms.tempo_k8s...)
336.         try:
337.             ctx: Context = copy_context()
338.             if context_tracer := _get_tracer_from_context(ctx):
339.                 logger.warning(
340.                     "Tracer not found in `tracer` context var. "
341.                     "Verify that you're importing all `charm_tracing` symbols from the same module path. \n"
342.                     "For example, DO"
343.                     ": `from charms.lib...charm_tracing import foo, bar`. \n"
344.                     "DONT: \n"
345.                     " \t - `from charms.lib...charm_tracing import foo` \n"
346.                     " \t - `from lib...charm_tracing import bar` \n"
347.                     "For more info: https://python-notes.curiousefficiency.org/en/latest/python"
348.                     "_concepts/import_traps.html#the-double-import-trap"
349.                 )
350.                 return context_tracer.get()
351.             else:
352.                 return None
353.         except LookupError:
354.             return None
355. 
356. 
357. @contextmanager
358. def _span(name: str) -> Generator[Optional[Span], Any, Any]:
359.     """Context to create a span if there is a tracer, otherwise do nothing."""
360.     if tracer := _get_tracer():
361.         with tracer.start_as_current_span(name) as span:
362.             yield cast(Span, span)
363.     else:
364.         yield None
365. 
366. 
367. class TracingError(RuntimeError):
368.     """Base class for errors raised by this module."""
369. 
370. 
371. class UntraceableObjectError(TracingError):
372.     """Raised when an object you're attempting to instrument cannot be autoinstrumented."""
373. 
374. 
375. class TLSError(TracingError):
376.     """Raised when the tracing endpoint is https but we don't have a cert yet."""
377. 
378. 
379. def _get_tracing_endpoint(
380.     tracing_endpoint_attr: str,
381.     charm_instance: object,
382.     charm_type: type,
383. ):
384.     _tracing_endpoint = getattr(charm_instance, tracing_endpoint_attr)
385.     if callable(_tracing_endpoint):
386.         tracing_endpoint = _tracing_endpoint()
387.     else:
388.         tracing_endpoint = _tracing_endpoint
389. 
390.     if tracing_endpoint is None:
391.         return
392. 
393.     elif not isinstance(tracing_endpoint, str):
394.         raise TypeError(
395.             f"{charm_type.__name__}.{tracing_endpoint_attr} should resolve to a tempo endpoint (string); "
396.             f"got {tracing_endpoint} instead."
397.         )
398. 
399.     dev_logger.debug(f"Setting up span exporter to endpoint: {tracing_endpoint}/v1/traces")
400.     return f"{tracing_endpoint}/v1/traces"
401. 
402. 
403. def _get_server_cert(
404.     server_cert_attr: str,
405.     charm_instance: ops.CharmBase,
406.     charm_type: Type[ops.CharmBase],
407. ):
408.     _server_cert = getattr(charm_instance, server_cert_attr)
409.     if callable(_server_cert):
410.         server_cert = _server_cert()
411.     else:
412.         server_cert = _server_cert
413. 
414.     if server_cert is None:
415.         logger.warning(
416.             f"{charm_type}.{server_cert_attr} is None; sending traces over INSECURE connection."
417.         )
418.         return
419.     elif not Path(server_cert).is_absolute():
420.         raise ValueError(
421.             f"{charm_type}.{server_cert_attr} should resolve to a valid tls cert absolute path (string | Path)); "
422.             f"got {server_cert} instead."
423.         )
424.     return server_cert
425. 
426. 
427. def _setup_root_span_initializer(
428.     charm_type: _CharmType,
429.     tracing_endpoint_attr: str,
430.     server_cert_attr: Optional[str],
431.     service_name: Optional[str] = None,
432. ):
433.     """Patch the charm's initializer."""
434.     original_init = charm_type.__init__
435. 
436.     @functools.wraps(original_init)
437.     def wrap_init(self: CharmBase, framework: Framework, *args, **kwargs):
438.         # we're using 'self' here because this is charm init code, makes sense to read what's below
439.         # from the perspective of the charm. Self.unit.name...
440. 
441.         original_init(self, framework, *args, **kwargs)
442.         # we call this from inside the init context instead of, say, _autoinstrument, because we want it to
443.         # be checked on a per-charm-instantiation basis, not on a per-type-declaration one.
444.         if not is_enabled():
445.             # this will only happen during unittesting, hopefully, so it's fine to log a
446.             # bit more verbosely
447.             logger.info("Tracing DISABLED: skipping root span initialization")
448.             return
449. 
450.         # already init some attrs that will be reinited later by calling original_init:
```

</details>


### ✅ `bash`

**Find key definitions in charm_tracing**

$ grep -n "^def trace_charm\|^class\|receiver_ports\|enable_receivers" /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py | head -30

<details>
<summary>7 lines</summary>

```
32:class MyCharm(CharmBase):
88:class MyCharm(CharmBase):
367:class TracingError(RuntimeError):
371:class UntraceableObjectError(TracingError):
375:class TLSError(TracingError):
553:def trace_charm(
<exited with exit code 0>
```

</details>


### 💬 Copilot

Perfect! Now let me get the complete trace_charm decorator definition:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py (lines 553-680)

<details>
<summary>128 lines</summary>

```
553. def trace_charm(
554.     tracing_endpoint: str,
555.     server_cert: Optional[str] = None,
556.     service_name: Optional[str] = None,
557.     extra_types: Sequence[type] = (),
558. ) -> Callable[[_T], _T]:
559.     """Autoinstrument the decorated charm with tracing telemetry.
560. 
561.     Use this function to get out-of-the-box traces for all events emitted on this charm and all
562.     method calls on instances of this class.
563. 
564.     Usage:
565.     >>> from charms.tempo_k8s.v1.charm_tracing import trace_charm
566.     >>> from charms.tempo_k8s.v1.tracing import TracingEndpointRequirer
567.     >>> from ops import CharmBase
568.     >>>
569.     >>> @trace_charm(
570.     >>>         tracing_endpoint="tempo_otlp_http_endpoint",
571.     >>> )
572.     >>> class MyCharm(CharmBase):
573.     >>>
574.     >>>     def __init__(self, framework: Framework):
575.     >>>         ...
576.     >>>         self.tracing = TracingEndpointRequirer(self)
577.     >>>
578.     >>>     @property
579.     >>>     def tempo_otlp_http_endpoint(self) -> Optional[str]:
580.     >>>         if self.tracing.is_ready():
581.     >>>             return self.tracing.otlp_http_endpoint()
582.     >>>         else:
583.     >>>             return None
584.     >>>
585. 
586.     :param tracing_endpoint: name of a method, property or attribute  on the charm type that returns an
587.         optional (fully resolvable) tempo url to which the charm traces will be pushed.
588.         If None, tracing will be effectively disabled.
589.     :param server_cert: name of a method, property or attribute on the charm type that returns an
590.         optional absolute path to a CA certificate file to be used when sending traces to a remote server.
591.         If it returns None, an _insecure_ connection will be used. To avoid errors in transient
592.         situations where the endpoint is already https but there is no certificate on disk yet, it
593.         is recommended to disable tracing (by returning None from the tracing_endpoint) altogether
594.         until the cert has been written to disk.
595.     :param service_name: service name tag to attach to all traces generated by this charm.
596.         Defaults to the juju application name this charm is deployed under.
597.     :param extra_types: pass any number of types that you also wish to autoinstrument.
598.         For example, charm libs, relation endpoint wrappers, workload abstractions, ...
599.     """
600. 
601.     def _decorator(charm_type: _T) -> _T:
602.         """Autoinstrument the wrapped charmbase type."""
603.         _autoinstrument(
604.             charm_type,
605.             tracing_endpoint_attr=tracing_endpoint,
606.             server_cert_attr=server_cert,
607.             service_name=service_name,
608.             extra_types=extra_types,
609.         )
610.         return charm_type
611. 
612.     return _decorator
613. 
614. 
615. def _autoinstrument(
616.     charm_type: _T,
617.     tracing_endpoint_attr: str,
618.     server_cert_attr: Optional[str] = None,
619.     service_name: Optional[str] = None,
620.     extra_types: Sequence[type] = (),
621. ) -> _T:
622.     """Set up tracing on this charm class.
623. 
624.     Use this function to get out-of-the-box traces for all events emitted on this charm and all
625.     method calls on instances of this class.
626. 
627.     Usage:
628. 
629.     >>> from charms.tempo_k8s.v1.charm_tracing import _autoinstrument
630.     >>> from ops.main import main
631.     >>> _autoinstrument(
632.     >>>         MyCharm,
633.     >>>         tracing_endpoint_attr="tempo_otlp_http_endpoint",
634.     >>>         service_name="MyCharm",
635.     >>>         extra_types=(Foo, Bar)
636.     >>> )
637.     >>> main(MyCharm)
638. 
639.     :param charm_type: the CharmBase subclass to autoinstrument.
640.     :param tracing_endpoint_attr: name of a method, property or attribute  on the charm type that returns an
641.         optional (fully resolvable) tempo url to which the charm traces will be pushed.
642.         If None, tracing will be effectively disabled.
643.     :param server_cert_attr: name of a method, property or attribute on the charm type that returns an
644.         optional absolute path to a CA certificate file to be used when sending traces to a remote server.
645.         If it returns None, an _insecure_ connection will be used. To avoid errors in transient
646.         situations where the endpoint is already https but there is no certificate on disk yet, it
647.         is recommended to disable tracing (by returning None from the tracing_endpoint) altogether
648.         until the cert has been written to disk.
649.     :param service_name: service name tag to attach to all traces generated by this charm.
650.         Defaults to the juju application name this charm is deployed under.
651.     :param extra_types: pass any number of types that you also wish to autoinstrument.
652.         For example, charm libs, relation endpoint wrappers, workload abstractions, ...
653.     """
654.     dev_logger.info(f"instrumenting {charm_type}")
655.     _setup_root_span_initializer(
656.         charm_type,
657.         tracing_endpoint_attr,
658.         server_cert_attr=server_cert_attr,
659.         service_name=service_name,
660.     )
661.     trace_type(charm_type)
662.     for type_ in extra_types:
663.         trace_type(type_)
664. 
665.     return charm_type
666. 
667. 
668. def trace_type(cls: _T) -> _T:
669.     """Set up tracing on this class.
670. 
671.     Use this decorator to get out-of-the-box traces for all method calls on instances of this class.
672.     It assumes that this class is only instantiated after a charm type decorated with `@trace_charm`
673.     has been instantiated.
674.     """
675.     dev_logger.info(f"instrumenting {cls}")
676.     for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
677.         dev_logger.info(f"discovered {method}")
678. 
679.         if method.__name__.startswith("__"):
680.             dev_logger.info(f"skipping {method} (dunder)")
```

</details>


### ✅ `bash`

**Get TracingEndpointProvider class definition**

$ grep -A 5 "class TracingEndpointProvider" /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py | head -20

<details>
<summary>10 lines</summary>

```
class TracingEndpointProviderEvents(CharmEvents):
    """TracingEndpointProvider events."""

    request = EventSource(RequestEvent)
    broken = EventSource(BrokenEvent)

--
class TracingEndpointProvider(Object):
    """Class representing a trace receiver service."""

    on = TracingEndpointProviderEvents()  # type: ignore

    def __init__(
<exited with exit code 0>
```

</details>


### 💬 Copilot

Excellent! Now let me create a comprehensive summary by checking the tempo.py file for receiver configuration details:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py (lines 1-120)

<details>
<summary>120 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2024 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Tempo workload configuration and client."""
6. import logging
7. import re
8. import socket
9. from pathlib import Path
10. from subprocess import CalledProcessError, getoutput
11. from typing import Dict, List, Optional, Sequence, Tuple
12. from urllib.parse import urlparse
13. 
14. import ops
15. import tenacity
16. import yaml
17. from charms.tempo_k8s.v2.tracing import (
18.     ReceiverProtocol,
19.     receiver_protocol_to_transport_protocol,
20. )
21. from charms.traefik_route_k8s.v0.traefik_route import TraefikRouteRequirer
22. from ops import ModelError
23. from ops.pebble import Layer
24. 
25. logger = logging.getLogger(__name__)
26. 
27. 
28. class Tempo:
29.     """Class representing the Tempo client workload configuration."""
30. 
31.     config_path = "/etc/tempo/tempo.yaml"
32. 
33.     # cert path on charm container
34.     server_cert_path = "/usr/local/share/ca-certificates/ca.crt"
35. 
36.     # cert paths on tempo container
37.     tls_cert_path = "/etc/tempo/tls/server.crt"
38.     tls_key_path = "/etc/tempo/tls/server.key"
39.     tls_ca_path = "/usr/local/share/ca-certificates/ca.crt"
40. 
41.     _tls_min_version = ""
42.     # cfr https://grafana.com/docs/enterprise-traces/latest/configure/reference/#supported-contents-and-default-values
43.     # "VersionTLS12"
44. 
45.     wal_path = "/etc/tempo/tempo_wal"
46.     log_path = "/var/log/tempo.log"
47.     tempo_ready_notice_key = "canonical.com/tempo/workload-ready"
48. 
49.     s3_relation_name = "s3"
50.     s3_bucket_name = "tempo"
51. 
52.     memberlist_port = 7946
53. 
54.     server_ports = {
55.         "tempo_http": 3200,
56.         "tempo_grpc": 9096,  # default grpc listen port is 9095, but that conflicts with promtail.
57.     }
58. 
59.     receiver_ports: Dict[str, int] = {
60.         "zipkin": 9411,
61.         "otlp_grpc": 4317,
62.         "otlp_http": 4318,
63.         "jaeger_thrift_http": 14268,
64.         # todo if necessary add support for:
65.         #  "kafka": 42,
66.         #  "jaeger_grpc": 14250,
67.         #  "opencensus": 43,
68.         #  "jaeger_thrift_compact": 44,
69.         #  "jaeger_thrift_binary": 45,
70.     }
71. 
72.     all_ports = {**server_ports, **receiver_ports}
73. 
74.     def __init__(
75.         self,
76.         container: ops.Container,
77.         external_host: Optional[str] = None,
78.         enable_receivers: Optional[Sequence[ReceiverProtocol]] = None,
79.     ):
80.         # ports source: https://github.com/grafana/tempo/blob/main/example/docker-compose/local/docker-compose.yaml
81. 
82.         # fqdn, if an ingress is not available, else the ingress address.
83.         self._external_hostname = external_host or socket.getfqdn()
84.         self.container = container
85.         self.enabled_receivers = enable_receivers or []
86. 
87.     @property
88.     def tempo_http_server_port(self) -> int:
89.         """Return the receiver port for the built-in tempo_http protocol."""
90.         return self.server_ports["tempo_http"]
91. 
92.     @property
93.     def tempo_grpc_server_port(self) -> int:
94.         """Return the receiver port for the built-in tempo_http protocol."""
95.         return self.server_ports["tempo_grpc"]
96. 
97.     def get_external_ports(self, service_name_prefix: str) -> List[Tuple[str, int, int]]:
98.         """List of service names and port mappings for the kubernetes service patch.
99. 
100.         Includes the tempo server as well as the receiver ports.
101.         """
102.         # todo allow remapping ports?
103.         all_ports = {**self.server_ports}
104.         return [
105.             (
106.                 (f"{service_name_prefix}-{service_name}").replace("_", "-"),
107.                 all_ports[service_name],
108.                 all_ports[service_name],
109.             )
110.             for service_name in all_ports
111.         ]
112. 
113.     @property
114.     def url(self) -> str:
115.         """Base url at which the tempo server is locally reachable over http."""
116.         scheme = "https" if self.tls_ready else "http"
117.         return f"{scheme}://{self._external_hostname}"
118. 
119.     def get_receiver_url(self, protocol: ReceiverProtocol, ingress: TraefikRouteRequirer):
120.         """Return the receiver endpoint URL based on the protocol.
```

</details>


### ✅ `bash`

**Find receiver configuration methods**

$ grep -n "def get_receiver_url\|receiver_ports\|enable_receivers" /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py | head -20

<details>
<summary>7 lines</summary>

```
59:    receiver_ports: Dict[str, int] = {
72:    all_ports = {**server_ports, **receiver_ports}
78:        enable_receivers: Optional[Sequence[ReceiverProtocol]] = None,
85:        self.enabled_receivers = enable_receivers or []
119:    def get_receiver_url(self, protocol: ReceiverProtocol, ingress: TraefikRouteRequirer):
127:        receiver_port = self.receiver_ports[protocol]
<exited with exit code 0>
```

</details>


### 💬 Copilot

Perfect! Now let me get the get_receiver_url method and create a final summary:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py (lines 119-200)

<details>
<summary>82 lines</summary>

```
119.     def get_receiver_url(self, protocol: ReceiverProtocol, ingress: TraefikRouteRequirer):
120.         """Return the receiver endpoint URL based on the protocol.
121. 
122.         if ingress is used, return endpoint provided by the ingress instead.
123.         """
124.         protocol_type = receiver_protocol_to_transport_protocol.get(protocol)
125.         # ingress.is_ready returns True even when traefik hasn't sent any data yet
126.         has_ingress = ingress.is_ready() and ingress.external_host and ingress.scheme
127.         receiver_port = self.receiver_ports[protocol]
128. 
129.         if has_ingress:
130.             url = (
131.                 ingress.external_host
132.                 if protocol_type == "grpc"
133.                 else f"{ingress.scheme}://{ingress.external_host}"
134.             )
135.         else:
136.             url = self._external_hostname if protocol_type == "grpc" else self.url
137. 
138.         return f"{url}:{receiver_port}"
139. 
140.     def plan(self):
141.         """Update pebble plan and start the tempo-ready service."""
142.         self.container.add_layer("tempo", self.pebble_layer, combine=True)
143.         self.container.add_layer("tempo-ready", self.tempo_ready_layer, combine=True)
144.         try:
145.             self.container.replan()
146.             # is not autostart-enabled, we just run it once on pebble-ready.
147.             self.container.start("tempo-ready")
148.         except ops.pebble.ChangeError:
149.             # replan failed likely because address was still in use. try to (re)start tempo with backoff as a fallback
150.             restart_result = self.restart()
151.             if not restart_result:
152.                 logger.exception(
153.                     "Starting tempo failed with a ChangeError and restart attempts didn't resolve the issue"
154.                 )
155. 
156.     def update_config(
157.         self,
158.         requested_receivers: Sequence[ReceiverProtocol],
159.         s3_config: Optional[dict] = None,
160.         peers: Optional[List[str]] = None,
161.     ) -> bool:
162.         """Generate a config and push it to the container it if necessary."""
163.         container = self.container
164.         if not container.can_connect():
165.             logger.debug("Container can't connect: config update skipped.")
166.             return False
167. 
168.         new_config = self.generate_config(requested_receivers, s3_config, peers)
169. 
170.         if self.get_current_config() != new_config:
171.             logger.debug("Pushing new config to container...")
172.             container.push(
173.                 self.config_path,
174.                 yaml.safe_dump(new_config),
175.                 make_dirs=True,
176.             )
177.             return True
178.         return False
179. 
180.     @property
181.     def is_tempo_service_defined(self) -> bool:
182.         """Check that the tempo service is present in the plan."""
183.         try:
184.             self.container.get_service("tempo")
185.             return True
186.         except (ModelError, ops.pebble.ConnectionError):
187.             return False
188. 
189.     @tenacity.retry(
190.         # if restart FAILS (this function returns False)
191.         retry=tenacity.retry_if_result(lambda r: r is False),
192.         # we wait 3, 9, 27... up to 40 seconds between tries
193.         wait=tenacity.wait_exponential(multiplier=3, min=1, max=40),
194.         # we give up after 20 attempts
195.         stop=tenacity.stop_after_attempt(20),
196.         # if there's any exceptions throughout, raise them
197.         reraise=True,
198.     )
199.     def restart(self) -> bool:
200.         """Try to restart the tempo service."""
```

</details>


### ✅ `bash`

**Check file sizes**

$ wc -l /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py

```
578 /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py
  526 /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py
 1104 total
<exited with exit code 0>
```


### 💬 Copilot

Perfect! Now I have all the information I need. Let me create a comprehensive summary:

## Comprehensive Analysis: Tempo-K8s Charm Tracing Usage

I've explored the charm and here's a complete breakdown of how it uses tracing:

---

### 1. **TRACING USAGE IN THE CHARM**

The Tempo-K8s charm uses tracing in **two distinct ways**:

#### A. **As a Tracing Provider** (Main role)
- Provides tracing endpoints to other charms via the `tracing` relation interface
- Implements `TracingEndpointProvider` from `charms.tempo_k8s.v2.tracing`
- **File:** `/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py` (lines 102, 137, 142)

#### B. **As a Tracing Consumer** (Self-instrumentation)
- Instruments its own charm code with OpenTelemetry tracing
- Sends charm execution traces to its own Tempo instance
- Uses `@trace_charm` decorator from `charms.tempo_k8s.v1.charm_tracing`
- **File:** `/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py` (lines 44-48)

---

### 2. **ALL FILES IMPORTING TRACING-RELATED LIBRARIES**

**Main Source Files:**
- `/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py` - Imports and uses tracing provider/decorator
- `/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py` - Imports receiver protocol types

**Library Files:**
- `/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/charm_tracing.py` - Core charm instrumentation library (760 lines)
- `/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v2/tracing.py` - Tracing endpoint interface library (996 lines)
- `/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/lib/charms/tempo_k8s/v1/tracing.py` - Legacy tracing library (v1)

**Test Files (14 files):**
- `/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_*.py`
- `/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester/src/charm.py`
- Integration/test charms that demonstrate tracing usage

---

### 3. **MAIN ENTRY POINT**

**File:** `/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py` (578 lines)

**Key Components:**
- **Class:** `TempoCharm(CharmBase)` decorated with `@trace_charm`
- **Main Initialization (lines 44-48):**
```python
@trace_charm(
    tracing_endpoint="tempo_otlp_http_endpoint",
    server_cert="server_cert",
    extra_types=(Tempo, TracingEndpointProvider),
)
class TempoCharm(CharmBase):
    # ...
```

- **Tracing Provider Setup (line 102):**
```python
self.tracing = TracingEndpointProvider(self, external_url=self._external_url)
```

---

### 4. **TRACING ENDPOINTS & RECEIVERS CONFIGURATION**

**Available Receiver Ports (from `tempo.py`, lines 59-70):**
```python
receiver_ports: Dict[str, int] = {
    "zipkin": 9411,
    "otlp_grpc": 4317,
    "otlp_http": 4318,
    "jaeger_thrift_http": 14268,
}
```

**Supported Receiver Protocols (from `tracing.py`, line 120):**
```python
ReceiverProtocol = Literal[
    "zipkin",
    "otlp_grpc",
    "otlp_http",
    "jaeger_grpc",
    "jaeger_thrift_http",
]
```

**Charm Tracing Endpoint (line 471-478 in `charm.py`):**
```python
def tempo_otlp_http_endpoint(self) -\> Optional[str]:
    """Endpoint at which the charm tracing information will be forwarded."""
    if self.tempo.is_ready():
        return f"{self._internal_url}:{self.tempo.receiver_ports['otlp_http']}"
    return None
```
- Uses **OTLP HTTP** protocol (port **4318**) for charm tracing
- Endpoint format: `http(s)://hostname:4318` or with ingress: `https://ingress-url:4318`

**Charm Initialization Receivers (line 58):**
```python
enable_receivers=["otlp_http"],  # Required for charm_tracing
```

---

### 5. **CONFIGURATION FILES**

#### **charmcraft.yaml** (119 lines)
```yaml
provides:
  tracing:
    interface: tracing
    description: |
      Integration to offer other charms the possibility to send traces to Tempo.

requires:
  certificates:
    interface: tls-certificates
    limit: 1
    description: |
      Certificate and key files for securing Tempo internal and external 
      communications with TLS.

actions:
  list-receivers:
    description: |
      Returns a list of all enabled receiver endpoints.

charm-binary-python-packages:
  - "pydantic\>=2"
  - "cryptography"
  - "jsonschema"
  - "opentelemetry-exporter-otlp-proto-http==1.21.0"
```

#### **requirements.txt** (20 lines)
```
importlib-metadata~=6.0.0
ops
jsonschema==4.17.0
lightkube==0.11.0
lightkube-models==1.24.1.4
tenacity==8.2.3

# PYDEPS
# lib/charms/tempo_k8s/v1/charm_tracing.py
opentelemetry-exporter-otlp-proto-http==1.21.0

# lib/charms/tls_certificates_interface/v2/tls_certificates.py
jsonschema
cryptography
# lib/charms/tempo_k8s/v1/tracing.py
pydantic\>=2
# lib/charms/prometheus_k8s/v0/prometheus_scrape.py
cosl
```

#### **pyproject.toml** (74 lines)
```toml
[project]
name = "tempo-k8s"
version = "0.1"

[tool.ruff.lint.per-file-ignores]
"lib/charms/tempo_k8s/v1/charm_tracing.py" = ["E402"]  # Special handling for charm_tracing
```

---

### 6. **LIB DIRECTORY STRUCTURE**

**Tracing-Related Libraries:**
```
lib/charms/tempo_k8s/
├── v1/
│   ├── charm_tracing.py    (760 lines) - Charm instrumentation decorator
│   └── tracing.py          (Legacy tracing interface - v1)
└── v2/
    └── tracing.py          (996 lines) - Current tracing interface with
                                         TracingEndpointProvider & Requirer
```

**Key Classes in `v2/tracing.py`:**
- `TracingEndpointProvider` - Manages tracing relations (provider side)
- `TracingEndpointRequirer` - Requests tracing endpoints (requirer side)
- `ReceiverProtocol` - Type for supported protocols
- `TransportProtocolType` - Enum: http/grpc
- `receiver_protocol_to_transport_protocol` - Protocol mapping dict

---

### 7. **CHARM TRACING INTEGRATION DETAILS**

**Decorator Parameters (lines 553-558):**
```python
@trace_charm(
    tracing_endpoint: str,           # Attribute name for endpoint getter
    server_cert: Optional[str],      # Attribute name for cert getter
    service_name: Optional[str],     # Service name for traces
    extra_types: Sequence[type]      # Additional types to instrument
)
```

**Implementation in TempoCharm:**
- **Endpoint Method:** `tempo_otlp_http_endpoint()` (lines 471-478)
- **Certificate Method:** `server_cert()` (lines 455-458)
- **Extra Types:** `(Tempo, TracingEndpointProvider)` - both get auto-instrumented
- **TLS Support:** Yes, via `CertHandler` (lines 65-69, 205-233)

**Tracing Features:**
1. Auto-instruments all charm events as spans
2. Auto-instruments all charm methods as spans (except dunders)
3. Instruments extra types (Tempo class, TracingEndpointProvider)
4. Uses OpenTelemetry OTLP HTTP exporter (`opentelemetry-exporter-otlp-proto-http==1.21.0`)
5. Sends traces to charm's own Tempo instance via internal network

---

### 8. **KEY INTERACTIONS WITH TRACING RELATIONS**

**From `charm.py` (lines 330-368):**

```python
def _update_tracing_relations(self):
    """Update tracing relations' databags with receiver endpoints."""
    tracing_relations = self.model.relations["tracing"]
    requested_receivers = self._requested_receivers()
    
    # Publish receivers to all related charms
    self.tracing.publish_receivers(
        [(p, self.tempo.get_receiver_url(p, self.ingress)) 
         for p in requested_receivers]
    )

def _requested_receivers(self) -\> Tuple[ReceiverProtocol, ...]:
    """List receivers based on active tracing relations."""
    requested_protocols = set(self.tracing.requested_protocols())
    requested_receivers = requested_protocols.intersection(
        set(self.tempo.receiver_ports)
    )
    requested_receivers.update(self.tempo.enabled_receivers)
    return tuple(requested_receivers)
```

**Event Handlers:**
- `on.tracing.request` → `_on_tracing_request()` - Remote charm requests endpoint
- `on.tracing.broken` → `_on_tracing_broken()` - Tracing relation removed
- Ingress changes trigger `_update_tracing_relations()` to refresh endpoints

---

### **SUMMARY TABLE**

| Aspect | Details |
|--------|---------|
| **Charm Role** | Provider (exposes endpoints) + Consumer (self-traces) |
| **Interface** | `tracing` (v2) |
| **Main Classes** | `TempoCharm`, `Tempo`, `TracingEndpointProvider` |
| **Charm Tracing Protocol** | OTLP HTTP (port 4318) |
| **Other Supported Protocols** | Zipkin, OTLP gRPC, Jaeger Thrift HTTP, Jaeger gRPC |
| **TLS Support** | Yes (via CertHandler) |
| **Key Dependency** | `opentelemetry-exporter-otlp-proto-http==1.21.0` |
| **Auto-Instrumentation** | Events + methods + extra types (Tempo, Provider) |
| **Action** | `list-receivers` - displays all enabled receiver endpoints |


---

<sub>⏱️ 34s</sub>

### ✅ `web_search`

**ops[tracing] ops.tracing.setup() ops.tracing.Tracing() charm OpenTelemetry ops 2.21.0 usage example**

<details>
<summary>Arguments</summary>

```json
{
  "query": "ops[tracing] ops.tracing.setup() ops.tracing.Tracing() charm OpenTelemetry ops 2.21.0 usage example"
}
```

</details>

````
{"type":"text","text":{"value":"To use OpenTelemetry tracing in a Python Juju charm using the ops library (version 2.21.0+) with the new first-party tracing support (ops[tracing]), follow these steps:\n\n### 1. Add Dependencies\nIn your `requirements.txt` or `pyproject.toml`, include:\n```\nops[tracing]>=2.21.0\n```\nThis will ensure tracing features and dependencies are pulled in.\n\n### 2. Declare Relations in `charmcraft.yaml`\nAdd the required tracing relations:\n```yaml\nrequires:\n  charm-tracing:\n    interface: tracing\n    limit: 1\n    optional: true\n  receive-ca-cert:\n    interface: certificate_transfer\n    limit: 1\n    optional: true\n```\n- `charm-tracing` enables sending trace data to an OpenTelemetry backend.\n- `receive-ca-cert` allows securely updating the CA certificates if sending traces over HTTPS (optional but recommended).\n\n### 3. Setup Rust Build Packages (if using pydantic-core)\nAdd Rust toolchain for certain dependencies:\n```yaml\nparts:\n  charm:\n    plugin: charm\n    source: .\n    build-packages:\n      - cargo\n```\n\n### 4. Use Tracing in the Charm Class\n\nYou do NOT need to explicitly import `ops.tracing`, just use it after ensuring your dependencies include `ops[tracing]`. Initialize tracing in your charm like this:\n```python\nimport ops\n\nclass MyCharm(ops.CharmBase):\n    def __init__(self, *args):\n        super().__init__(*args)\n        self.tracing = ops.tracing.Tracing(\n            self,\n            tracing_relation_name='charm-tracing',\n            ca_relation_name='receive-ca-cert',  # Optional\n        )\n        ...\n\n    # Example usage in an event handler\n    def _on_start(self, event):\n        with self.tracing.start_as_current_span(\"start-event\"):\n            self.unit.status = ops.ActiveStatus(\"Hello, world!\")\n```\n- The `tracing_relation_name` is the name of the Juju relation that delivers OpenTelemetry configuration.\n- You can also pass a hardcoded certificate bundle as `ca_data`. If both `ca_relation_name` and `ca_data` are omitted, the system CA bundle is used.\n\n### 5. Best Practices and Further Reading\n\n- The tracing context and spans will be automatically started and propagated through your event handlers if initialized as above.\n- You can instrument arbitrary blocks of code with `with self.tracing.start_as_current_span(\"my-span\")`.\n\nSee official comprehensive documentation and use cases for more advanced configuration and troubleshooting:  \n- [Ops library tracing docs (reference & examples)](https://documentation.ubuntu.com/ops/latest/reference/ops-tracing/)【3:1†source】\n- [Ops-tracing package and usage on PyPI](https://pypi.org/project/ops-tracing/)【3:0†source】\n- [Announcement with migration and caveats on Charmhub](https://discourse.charmhub.io/t/ops-2-21-0-ops-tracing-2-21-0-and-ops-scenario-7-21-0-released-ops-tracing-and-pebble-identities/17487)【3:3†source】\n- [Implementation in the canonical/operator repo](https://github.com/canonical/operator/tree/main/tracing/ops_tracing)【3:2†source】\n\n**Summary of Minimal Example:**\n```yaml\n# charmcraft.yaml snippet\nrequires:\n  charm-tracing:\n    interface: tracing\n    limit: 1\n    optional: true\n  receive-ca-cert:\n    interface: certificate_transfer\n    limit: 1\n    optional: true\n```\n```python\n# src/charm.py\nimport ops\n\nclass MyCharm(ops.CharmBase):\n    def __init__(self, *args):\n        super().__init__(*args)\n        self.tracing = ops.tracing.Tracing(\n            self, \n            tracing_relation_name=\"charm-tracing\",\n            ca_relation_name=\"receive-ca-cert\"\n        )\n```\n\nYou are now ready for out-of-the-box distributed tracing with OpenTelemetry inside your charm!","annotations":[{"text":"【3:1†source】","start_index":2489,"end_index":2501,"url_citation":{"title":"ops.tracing - Ops documentation","url":"https://documentation.ubuntu.com/ops/latest/reference/ops-tracing/"}},{"text":"【3:0†source】","start_index":2582,"end_index":2594,"url_citation":{"title":"ops-tracing · PyPI","url":"https://pypi.org/project/ops-tracing/"}},{"text":"【3:3†source】","start_index":2786,"end_index":2798,"url_citation":{"title":"ops 2.21.0, ops-tracing 2.21.0 and ops-scenario 7.21.0 released: ops ...","url":"https://discourse.charmhub.io/t/ops-2-21-0-ops-tracing-2-21-0-and-ops-scenario-7-21-0-released-ops-tracing-and-pebble-identities/17487"}},{"text":"【3:2†source】","start_index":2917,"end_index":2929,"url_citation":{"title":"operator/tracing/ops_tracing at main · canonical/operator","url":"https://github.com/canonical/operator/tree/main/tracing/ops_tracing"}}]},"bing_searches":[{"text":"ops[tracing] ops.tracing.setup() ops.tracing.Tracing() charm OpenTelemetry ops 2.21.0 usage example","url":"https://www.bing.com/search?q=ops%5Btracing%5D+ops.tracing.setup%28%29+ops.tracing.Tracing%28%29+charm+OpenTelemetry+ops+2.21.0+usage+example"}],"annotations":null}
````


---

<sub>⏱️ 1m 59s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/ops/latest/reference/ops-tracing/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://documentation.ubuntu.com/ops/latest/reference/ops-tracing/",
  "max_length": 10000
}
```

</details>

<details>
<summary>101 lines</summary>

```
Contents of https://documentation.ubuntu.com/ops/latest/reference/ops-tracing/:
The tracing facility for the Ops library.

## Quick start[¶](#quick-start "Link to this heading")

In your `charmcraft.yaml`, declare the charm tracing relation with a `tracing` interface and optionally the TLS relation with a `certificate_transfer` interface.:

requires:
    charm\-tracing:
        interface: tracing
        limit: 1
        optional: true
    receive\-ca\-cert:
        interface: certificate\_transfer
        limit: 1
        optional: true

If you’re migrating from the `charm-tracing` charm lib, you most likely already have relations like these. If the names of the relations differ from this recipe, please adjust the code on the rest of this page to your relation names.

Hint

Make sure to include the Rust build packages in your `charmcraft.yaml`, because this library depends on `pydantic-core` via `pydantic`.

parts:
    charm:
        plugin: charm
        source: .
        build-packages:
            \- cargo

If you’re migrating from the `charm-tracing` charm lib, this configuration is likely already in place.

In your charm, add and initialise the `Tracing` object.:

import ops

class SomeCharm(ops.CharmBase):
    def \_\_init\_\_(self, framework: ops.Framework):
        super().\_\_init\_\_(framework)
        ...
        self.tracing \= ops.tracing.Tracing(
            self,
            tracing\_relation\_name\='charm-tracing',
            ca\_relation\_name\='receive-ca-cert',
        )

The tracing relation name is required, while the CA relation name is optional, as it is possible to use a system certificate authority list, provide a custom list (for example from the `certify` package) or export the trace data over HTTP connections only. Declaring both relations is most common.

Note that you don’t have to `import ops.tracing`, that name is automatically available when your Python project depends on `ops[tracing]`.

_class_ ops\_tracing.Tracing(

_charm: [CharmBase](../ops/#ops.CharmBase "ops.charm.CharmBase")_,

_tracing\_relation\_name: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_,

_\*_,

_ca\_relation\_name: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)") \= None_,

_ca\_data: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)") \= None_,

)[\[source\]](../../_modules/ops_tracing/_api/#Tracing)[¶](#ops_tracing.Tracing "Link to this definition")

Bases: [`Object`](../ops/#ops.Object "ops.framework.Object")

Initialise the tracing service.

Usage:

*   Include `ops[tracing]` in your dependencies.
    
*   Declare the relations that the charm supports.
    
*   Initialise `Tracing` with the names of these relations.
    

Example:

\# charmcraft.yaml
requires:
    charm\-tracing:
        interface: tracing
        limit: 1
        optional: true
    receive\-ca\-cert:
        interface: certificate\_transfer
        limit: 1
        optional: true

\# src/charm.py
import ops.tracing

class SomeCharm(ops.CharmBase):
    def \_\_init\_\_(self, framework: ops.Framework):
        ...
        self.tracing \= ops.tracing.Tracing(
            self,
            tracing\_relation\_name\="charm-tracing",
            ca\_relation\_name\="receive-ca-cert",
        )

Parameters:

*   **charm** – your charm instance
    
*   **tracing\_relation\_name** – the name of the relation that provides the destination to send trace data to.
    
*   **ca\_relation\_name** – the name of the relation that provides the CA list to validate the tracing destination against.
    
*   **ca\_data** – a fixed CA list (PEM bundle, a multi-line string).
    

If the destination is resolved to an HTTPS URL, a CA list is required to establish a secure connection.

The CA list can be provided over a relation via the `ca_relation_name` argument, as a fixed string via the `ca_data` argument, or the system CA list will be used if the earlier two are both `None`.

ops\_tracing.set\_destination(_url: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)")_, _ca: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)")_) → [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)")[\[source\]](../../_modules/ops_tracing/_backend/#set_destination)[¶](#ops_tracing.set_destination "Link to this definition")

Configure the destination service for trace data.

Parameters:

*   **url** – the URL of the telemetry service to send trace data to. An example could be `http://localhost/v1/traces`. None or empty string disables sending out the data, which is still buffered.
    
*   **ca** – the CA list (PEM bundle, a multi-line string), only used for HTTPS URLs.
    

## Open Telemetry resource attributes[¶](#open-telemetry-resource-attributes "Link to this heading")

The following [well-known](https://opentelemetry.io/docs/specs/semconv/resource/#service) resource attributes are set:

*   `service.namespace` the UUID of the Juju model.
    
*   `service.namespace.name` the name of the Juju model.
    
*   `service.name` the application name, like `user_db`.
    
*   `service.instance.id` the unit number, like `0`.
    

The following [Juju topology](https://discourse.charmhub.io/t/juju-topology-labels/8874) resources attributes are also set:

*   `charm` the charm name, like `database-operator-k8s`.
    
*   `charm_type` the charm class name, like `DbCharm`.
    
*   `juju_model` the name of the Juju model.
    
*   `juju_model_uuid` the UUID of the Juju model.
    
*   `juju_application` the application name, like `user_db`.
    
*   `juju_unit` the unit name, like `user_db/0`.
    

## Security considerations[¶](#security-considerations "Link to this heading")

The trace data can be sent out over HTTP or HTTPS. If your charm uses the `ops.tracing.Tracing()` object, the protocol is determined by the URL that the charm tracing integration counterpart posts in the databag.

This release supports TLS 1.2 and 1.3 for HTTPS connections.

## Tracing behaviour across test frameworks[¶](#tracing-behaviour-across-test-frameworks "Link to this heading")

**ops\[testing\]** (formerly Scenario) replaces the OpenTelemetry tracer provider with a mocked version that keeps the emitted spans in memory. This data is not presently exposed to the tests. See `ops_tracing._mock.patch_tracing` for details.

**Harness** (legacy) is not affected. This framework does not have a Manager and does not call `ops.main()` and therefore the tracing subsystem remains uninitialised. It is still safe to create OpenTelemetry spans and events, as the root span is a `NonRecordingSpan` in this case.
```

</details>


---

<sub>⏱️ 1m 58s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py

```
File too large to read at once (23.5 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


---

<sub>⏱️ 2m 8s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py (lines 1-120)

<details>
<summary>120 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2024 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Charmed Operator for Tempo; a lightweight object storage based tracing backend."""
6. 
7. import logging
8. import re
9. import socket
10. from pathlib import Path
11. from typing import Optional, Set, Tuple
12. 
13. import ops
14. from charms.data_platform_libs.v0.s3 import S3Requirer
15. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
16. from charms.grafana_k8s.v0.grafana_source import GrafanaSourceProvider
17. from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
18. from charms.observability_libs.v0.kubernetes_service_patch import KubernetesServicePatch
19. from charms.observability_libs.v1.cert_handler import CertHandler
20. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
21. from charms.tempo_k8s.v1.charm_tracing import trace_charm
22. from charms.tempo_k8s.v2.tracing import (
23.     ReceiverProtocol,
24.     RequestEvent,
25.     TracingEndpointProvider,
26. )
27. from charms.traefik_route_k8s.v0.traefik_route import TraefikRouteRequirer
28. from ops.charm import (
29.     CharmBase,
30.     CollectStatusEvent,
31.     PebbleNoticeEvent,
32.     RelationEvent,
33.     WorkloadEvent,
34. )
35. from ops.main import main
36. from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus
37. from ops.pebble import APIError
38. 
39. from tempo import Tempo
40. 
41. logger = logging.getLogger(__name__)
42. 
43. 
44. @trace_charm(
45.     tracing_endpoint="tempo_otlp_http_endpoint",
46.     server_cert="server_cert",
47.     extra_types=(Tempo, TracingEndpointProvider),
48. )
49. class TempoCharm(CharmBase):
50.     """Charmed Operator for Tempo; a distributed tracing backend."""
51. 
52.     def __init__(self, *args):
53.         super().__init__(*args)
54.         self.tempo = tempo = Tempo(
55.             self.unit.get_container("tempo"),
56.             external_host=self.hostname,
57.             # we need otlp_http receiver for charm_tracing
58.             enable_receivers=["otlp_http"],
59.         )
60. 
61.         # TODO:
62.         #  ingress route provisioning a separate TCP ingress for each receiver if GRPC doesn't work directly
63.         self.ingress = TraefikRouteRequirer(self, self.model.get_relation("ingress"), "ingress")  # type: ignore
64. 
65.         self.cert_handler = CertHandler(
66.             self,
67.             key="tempo-server-cert",
68.             sans=[self.hostname],
69.         )
70. 
71.         self.s3_requirer = S3Requirer(self, Tempo.s3_relation_name, Tempo.s3_bucket_name)
72. 
73.         # configure this tempo as a datasource in grafana
74.         self.grafana_source_provider = GrafanaSourceProvider(
75.             self,
76.             source_type="tempo",
77.             source_url=self._external_http_server_url,
78.             refresh_event=[
79.                 # refresh the source url when TLS config might be changing
80.                 self.on[self.cert_handler.certificates_relation_name].relation_changed,
81.                 # or when ingress changes
82.                 self.ingress.on.ready,
83.             ],
84.         )
85.         # # Patch the juju-created Kubernetes service to contain the right ports
86.         external_ports = tempo.get_external_ports(self.app.name)
87.         self._service_patcher = KubernetesServicePatch(self, external_ports)
88.         # Provide ability for Tempo to be scraped by Prometheus using prometheus_scrape
89.         self._scraping = MetricsEndpointProvider(
90.             self,
91.             relation_name="metrics-endpoint",
92.             jobs=[{"static_configs": [{"targets": [f"*:{tempo.tempo_http_server_port}"]}]}],
93.         )
94.         # Enable log forwarding for Loki and other charms that implement loki_push_api
95.         self._logging = LogProxyConsumer(
96.             self, relation_name="logging", log_files=[self.tempo.log_path], container_name="tempo"
97.         )
98.         self._grafana_dashboards = GrafanaDashboardProvider(
99.             self, relation_name="grafana-dashboard"
100.         )
101. 
102.         self.tracing = TracingEndpointProvider(self, external_url=self._external_url)
103. 
104.         if not self.is_consistent():
105.             logger.error(
106.                 f"Inconsistent deployment. {self.unit.name} will be shutting down. "
107.                 "This likely means you need to add an s3 integration. "
108.                 "This charm will be unresponsive and refuse to handle any event until "
109.                 "the situation is resolved by the cloud admin, to avoid data loss."
110.             )
111.             self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)
112. 
113.             if self.tempo.is_tempo_service_defined:
114.                 self.tempo.shutdown()
115. 
116.             return  # refuse to handle any other event as we can't possibly know what to do.
117. 
118.         self.framework.observe(
119.             self.on["ingress"].relation_created, self._on_ingress_relation_created
120.         )
```

</details>


---

<sub>⏱️ 2m 8s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/requirements.txt.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/requirements.txt

<details>
<summary>20 lines</summary>

```
1. # pin importlib-metadata version else charmcraft pack will fail to resolve the dependencies for the pydeps-installed otlp library
2. importlib-metadata~=6.0.0
3. ops
4. jsonschema==4.17.0
5. lightkube==0.11.0
6. lightkube-models==1.24.1.4
7. tenacity==8.2.3
8. 
9. # PYDEPS
10. # lib/charms/tempo_k8s/v1/charm_tracing.py
11. opentelemetry-exporter-otlp-proto-http==1.21.0
12. 
13. # lib/charms/tls_certificates_interface/v2/tls_certificates.py
14. jsonschema
15. cryptography
16. # lib/charms/tempo_k8s/v1/tracing.py
17. pydantic>=2
18. # lib/charms/prometheus_k8s/v0/prometheus_scrape.py
19. cosl
20.
```

</details>


---

<sub>⏱️ 2m 8s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/charmcraft.yaml.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/charmcraft.yaml

<details>
<summary>119 lines</summary>

```
1. # Copyright 2022 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. name: tempo-k8s
4. type: charm
5. 
6. assumes:
7.   - k8s-api
8. 
9.   # Juju 3.4.0 needed for pebble notify
10.   - juju >= 3.4.0
11. 
12. description: |
13.   Tempo is a distributed tracing backend by Grafana, supporting Jaeger,
14.   Zipkin, and OpenTelemetry protocols.
15. 
16. summary: |
17.   Tempo is a distributed tracing backend by Grafana.
18. 
19. links:
20.   documentation: https://discourse.charmhub.io/t/tempo-k8s-docs-index/14005
21.   website:
22.     - https://charmhub.io/tempo-k8s
23.   source:
24.     - https://github.com/canonical/tempo-k8s-operator
25.   issues:
26.     - https://github.com/canonical/tempo-k8s-operator/issues
27. 
28. containers:
29.   tempo:
30.     resource: tempo-image
31.     mounts:
32.       - storage: data
33.         location: /tmp/tempo
34. 
35. resources:
36.   tempo-image:
37.     type: oci-image
38.     description: OCI image for Tempo
39.     # Included for simplicity in integration tests
40.     # see https://hub.docker.com/r/grafana/tempo/tags
41.     upstream-source: grafana/tempo:2.4.0
42. 
43. provides:
44.   grafana-dashboard:
45.     interface: grafana_dashboard
46.     description: |
47.       Forwards the built-in grafana dashboard(s) for monitoring Tempo.
48.   grafana-source:
49.     interface: grafana_datasource
50.     description: |
51.       Configures Grafana to be able to use this Tempo instance as a datasource.
52.   metrics-endpoint:
53.     interface: prometheus_scrape
54.     description: |
55.       Exposes the Prometheus metrics endpoint providing telemetry about the
56.       Tempo instance.
57.   tracing:
58.     interface: tracing
59.     description: |
60.       Integration to offer other charms the possibility to send traces to Tempo.
61. 
62. 
63. requires:
64.   s3:
65.     interface: s3
66.     limit: 1
67.     description: |
68.       Obtains access to the s3 bucket for data storage.
69.   logging:
70.     interface: loki_push_api
71.     description: |
72.       Integration with Loki to push Tempo logs to the observability stack.
73.   ingress:
74.     interface: traefik_route
75.     description: |
76.       Ingress integration for Tempo server and Tempo receiver endpoints,
77.       so that cross-model workloads can send their traces to Tempo through the ingress.
78.       Uses `traefik_route` to open ports on Traefik host for tracing ingesters.
79.   certificates:
80.     interface: tls-certificates
81.     limit: 1
82.     description: |
83.       Certificate and key files for securing Tempo internal and external 
84.       communications with TLS.
85. 
86. storage:
87.   data:
88.     type: filesystem
89.     location: /tempo-data
90. 
91. actions:
92.   list-receivers:
93.     description: |
94.       Returns a list of all enabled receiver endpoints.
95. 
96. peers:
97.   tempo-peers:
98.     interface: tempo_peers
99.     description: |
100.       peer relation for internal coordination
101.       
102. 
103. bases:
104.   - build-on:
105.       - name: "ubuntu"
106.         channel: "22.04"
107.     run-on:
108.       - name: "ubuntu"
109.         channel: "22.04"
110. 
111. parts:
112.   charm:
113.     charm-binary-python-packages:
114.       - "pydantic>=2"
115.       - "cryptography"
116.       - "jsonschema"
117.       - "opentelemetry-exporter-otlp-proto-http==1.21.0"
118. 
119.
```

</details>


---

<sub>⏱️ 2m 54s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py (lines 440-530)

<details>
<summary>91 lines</summary>

```
440.         #   platform:         linux/amd64
441. 
442.         if version_head := re.search(r"tempo, version (.*) \(branch: (.*), revision: (.*)\)", out):
443.             v_head, b_head, r_head = version_head.groups()
444.             version = f"{v_head}:{b_head}/{r_head}"
445.         elif version_headless := re.search(r"tempo, version (\S+)", out):
446.             version = version_headless.groups()[0]
447.         else:
448.             logger.warning(
449.                 f"unable to determine tempo workload version: output {out} "
450.                 f"does not match any known pattern"
451.             )
452.             return
453.         return version
454. 
455.     def server_cert(self):
456.         """For charm tracing."""
457.         self._update_server_cert()
458.         return self.tempo.server_cert_path
459. 
460.     def _update_server_cert(self):
461.         """Server certificate for charm tracing tls, if tls is enabled."""
462.         server_cert = Path(self.tempo.server_cert_path)
463.         if self.tls_available:
464.             if not server_cert.exists():
465.                 server_cert.parent.mkdir(parents=True, exist_ok=True)
466.                 if self.cert_handler.server_cert:
467.                     server_cert.write_text(self.cert_handler.server_cert)
468.         else:  # tls unavailable: delete local cert
469.             server_cert.unlink(missing_ok=True)
470. 
471.     def tempo_otlp_http_endpoint(self) -> Optional[str]:
472.         """Endpoint at which the charm tracing information will be forwarded."""
473.         # the charm container and the tempo workload container have apparently the same
474.         # IP, so we can talk to tempo at localhost.
475.         if self.tempo.is_ready():
476.             return f"{self._internal_url}:{self.tempo.receiver_ports['otlp_http']}"
477. 
478.         return None
479. 
480.     def is_scaled(self) -> bool:
481.         """Check whether Tempo is deployed with scale > 1."""
482.         # TODO write ADR for deployment model: tempo-k8s monolithic + scalable monolithic + coordinator
483.         relation = self.model.get_relation("tempo-peers")
484.         if not relation:
485.             return False
486. 
487.         # self is not included in relation.units
488.         return bool(relation.units)
489. 
490.     def peers(self) -> Optional[Set[ops.model.Unit]]:
491.         """Return charm's peer units."""
492.         relation = self.model.get_relation("tempo-peers")
493.         if not relation:
494.             return None
495. 
496.         # self is not included in relation.units
497.         return relation.units
498. 
499.     def is_consistent(self):
500.         """Check deployment consistency."""
501.         if self.is_scaled() and not self._is_s3_ready():
502.             return False
503.         return True
504. 
505.     def _is_s3_ready(self) -> bool:
506.         return bool(self._s3_config)
507. 
508.     def _on_collect_unit_status(self, e: CollectStatusEvent):
509.         if not self.is_consistent():
510.             e.add_status(
511.                 BlockedStatus(
512.                     "Unit *disabled*. Cannot scale Tempo without adding an s3 integration."
513.                 )
514.             )
515.         if not self.tempo.container.can_connect():
516.             e.add_status(WaitingStatus("Tempo container not ready"))
517.         if not self.tempo.is_ready():
518.             e.add_status(WaitingStatus("Tempo API not ready just yet..."))
519. 
520.         e.add_status(ActiveStatus())
521. 
522.     @property
523.     def hostname(self) -> str:
524.         """Unit's hostname."""
525.         return socket.getfqdn()
526. 
527.     def _on_list_receivers_action(self, event: ops.ActionEvent):
528.         res = {}
529.         for receiver in self._requested_receivers():
530.             res[receiver.replace("_", "-")] = (
```

</details>


---

<sub>⏱️ 2m 54s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py (lines 120-200)

<details>
<summary>81 lines</summary>

```
120.         )
121.         self.framework.observe(
122.             self.on["ingress"].relation_joined, self._on_ingress_relation_joined
123.         )
124.         self.framework.observe(self.on.leader_elected, self._on_leader_elected)
125.         self.framework.observe(self.on.leader_settings_changed, self._on_leader_settings_changed)
126.         self.framework.observe(self.ingress.on.ready, self._on_ingress_ready)
127. 
128.         self.framework.observe(self.on.tempo_pebble_ready, self._on_tempo_pebble_ready)
129.         self.framework.observe(
130.             self.on.tempo_pebble_custom_notice, self._on_tempo_pebble_custom_notice
131.         )
132.         self.framework.observe(self.on.update_status, self._on_update_status)
133.         self.framework.observe(
134.             self.s3_requirer.on.credentials_changed, self._on_s3_credentials_changed
135.         )
136.         self.framework.observe(self.s3_requirer.on.credentials_gone, self._on_s3_credentials_gone)
137.         self.framework.observe(self.tracing.on.request, self._on_tracing_request)
138.         self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)
139.         self.framework.observe(self.on.list_receivers_action, self._on_list_receivers_action)
140.         self.framework.observe(self.cert_handler.on.cert_changed, self._on_cert_handler_changed)
141.         self.framework.observe(self.on.config_changed, self._on_config_changed)
142.         self.framework.observe(self.tracing.on.broken, self._on_tracing_broken)
143.         self.framework.observe(
144.             self.on.tempo_peers_relation_created, self._on_tempo_peers_relation_created
145.         )
146.         self.framework.observe(
147.             self.on.tempo_peers_relation_changed, self._on_tempo_peers_relation_changed
148.         )
149. 
150.     @property
151.     def _external_http_server_url(self) -> str:
152.         """External url of the http(s) server."""
153.         return f"{self._external_url}:{self.tempo.tempo_http_server_port}"
154. 
155.     @property
156.     def _external_url(self) -> str:
157.         """Return the external url."""
158.         if self.ingress.is_ready():
159.             ingress_url = f"{self.ingress.scheme}://{self.ingress.external_host}"
160.             logger.debug("This unit's ingress URL: %s", ingress_url)
161.             return ingress_url
162. 
163.         # If we do not have an ingress, then use the pod hostname.
164.         # The reason to prefer this over the pod name (which is the actual
165.         # hostname visible from the pod) or a K8s service, is that those
166.         # are routable virtually exclusively inside the cluster (as they rely)
167.         # on the cluster's DNS service, while the ip address is _sometimes_
168.         # routable from the outside, e.g., when deploying on MicroK8s on Linux.
169.         return self._internal_url
170. 
171.     @property
172.     def _internal_url(self) -> str:
173.         scheme = "https" if self.tls_available else "http"
174.         return f"{scheme}://{self.hostname}"
175. 
176.     @property
177.     def tls_available(self) -> bool:
178.         """Return True if tls is enabled and the necessary certs are found."""
179.         return (
180.             self.cert_handler.enabled
181.             and (self.cert_handler.server_cert is not None)
182.             and (self.cert_handler.private_key is not None)
183.             and (self.cert_handler.ca_cert is not None)
184.         )
185. 
186.     @property
187.     def _s3_config(self) -> Optional[dict]:
188.         if not self.s3_requirer.relations:
189.             return None
190.         s3_config = self.s3_requirer.get_s3_connection_info()
191.         if (
192.             s3_config
193.             and "bucket" in s3_config
194.             and "endpoint" in s3_config
195.             and "access-key" in s3_config
196.             and "secret-key" in s3_config
197.         ):
198.             return s3_config
199.         return None
200.
```

</details>


---

<sub>⏱️ 3m 55s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py (lines 200-380)

<details>
<summary>181 lines</summary>

```
200. 
201.     def _on_tracing_broken(self, _):
202.         """Update tracing relations' databags once one relation is removed."""
203.         self._update_tracing_relations()
204. 
205.     def _on_cert_handler_changed(self, _):
206.         was_ready = self.tempo.tls_ready
207. 
208.         if self.tls_available:
209.             logger.debug("enabling TLS")
210.             self.tempo.configure_tls(
211.                 cert=self.cert_handler.server_cert,  # type: ignore
212.                 key=self.cert_handler.private_key,  # type: ignore
213.                 ca=self.cert_handler.ca_cert,  # type: ignore
214.             )
215.         else:
216.             logger.debug("disabling TLS")
217.             self.tempo.clear_tls_config()
218. 
219.         if was_ready != self.tempo.tls_ready:
220.             # tls readiness change means config change.
221.             self._update_tempo_config()
222.             # sync scheme change with traefik and related consumers
223.             self._configure_ingress()
224. 
225.             if self.tempo.is_tempo_service_defined:
226.                 self.tempo.restart()
227. 
228.         # sync the server cert with the charm container.
229.         # technically, because of charm tracing, this will be called first thing on each event
230.         self._update_server_cert()
231. 
232.         # update relations to reflect the new certificate
233.         self._update_tracing_relations()
234. 
235.     def _configure_ingress(self) -> None:
236.         """Make sure the traefik route and tracing relation data are up-to-date."""
237.         if not self.unit.is_leader():
238.             return
239. 
240.         if self.ingress.is_ready():
241.             self.ingress.submit_to_traefik(
242.                 self._ingress_config, static=self._static_ingress_config
243.             )
244.             if self.ingress.external_host:
245.                 self._update_tracing_relations()
246. 
247.     def _on_tracing_request(self, e: RequestEvent):
248.         """Handle a remote requesting a tracing endpoint."""
249.         logger.debug(f"received tracing request from {e.relation.app}: {e.requested_receivers}")
250.         self._update_tracing_relations()
251. 
252.     def _on_ingress_relation_created(self, _: RelationEvent):
253.         self._configure_ingress()
254. 
255.     def _on_ingress_relation_joined(self, _: RelationEvent):
256.         self._configure_ingress()
257. 
258.     def _on_leader_settings_changed(self, _: ops.LeaderSettingsChangedEvent):
259.         if not self._is_s3_ready():
260.             logger.error(
261.                 "Losing leadership without s3. " "This unit will soon be in an inconsistent state."
262.             )
263. 
264.     def _on_leader_elected(self, _: ops.LeaderElectedEvent):
265.         # as traefik_route goes through app data, we need to take lead of traefik_route if our leader dies.
266.         self._configure_ingress()
267. 
268.     def _on_s3_credentials_changed(self, _):
269.         self._on_s3_changed()
270. 
271.     def _on_s3_credentials_gone(self, _):
272.         self._on_s3_changed()
273. 
274.     def _on_s3_changed(self):
275.         could_scale_before = self.tempo.can_scale()
276. 
277.         self._update_tempo_config()
278. 
279.         can_scale_now = self.tempo.can_scale()
280.         # if we had s3, and we don't anymore, we need to replan from 'scaling-monolithic' to 'all'
281.         # if we didn't have s3, and now we do, we can replan from 'all' to 'scaling-monolithic'
282.         if could_scale_before != can_scale_now:
283.             if self.tempo.is_tempo_service_defined:
284.                 self.tempo.plan()
285.             else:
286.                 # assume that this will be handled at the next pebble-ready
287.                 logger.debug("Cannot reconfigure/restart tempo at this time.")
288. 
289.     def _on_tempo_peers_relation_created(self, event: ops.RelationCreatedEvent):
290.         if self._local_ip:
291.             event.relation.data[self.unit]["local-ip"] = self._local_ip
292. 
293.     def _on_tempo_peers_relation_changed(self, _):
294.         if self._update_tempo_config():
295.             self.tempo.restart()
296. 
297.     def _update_tempo_config(self) -> bool:
298.         peers = self.peers()
299.         relation = self.model.get_relation("tempo-peers")
300.         # get unit addresses for all the other units from a databag
301.         if peers and relation:
302.             addresses = [relation.data[unit].get("local-ip") for unit in peers]
303.             addresses = list(filter(None, addresses))
304.         else:
305.             addresses = []
306. 
307.         # add own address
308.         if self._local_ip:
309.             addresses.append(self._local_ip)
310. 
311.         return self.tempo.update_config(self._requested_receivers(), self._s3_config, addresses)
312. 
313.     @property
314.     def _local_ip(self) -> Optional[str]:
315.         binding = self.model.get_binding("tempo-peers")
316.         if binding and binding._relation_id:
317.             return str(binding.network.bind_address)
318.         return None
319. 
320.     def _on_config_changed(self, _):
321.         # check if certificate files haven't disappeared and recreate them if needed
322.         if self.tls_available and not self.tempo.tls_ready:
323.             logger.debug("enabling TLS")
324.             self.tempo.configure_tls(
325.                 cert=self.cert_handler.server_cert,  # type: ignore
326.                 key=self.cert_handler.private_key,  # type: ignore
327.                 ca=self.cert_handler.ca_cert,  # type: ignore
328.             )
329. 
330.     def _update_tracing_relations(self):
331.         tracing_relations = self.model.relations["tracing"]
332.         if not tracing_relations:
333.             # todo: set waiting status and configure tempo to run without receivers if possible,
334.             #  else perhaps postpone starting the workload at all.
335.             logger.warning("no tracing relations: Tempo has no receivers configured.")
336.             return
337. 
338.         requested_receivers = self._requested_receivers()
339.         # publish requested protocols to all relations
340.         if self.unit.is_leader():
341.             self.tracing.publish_receivers(
342.                 [(p, self.tempo.get_receiver_url(p, self.ingress)) for p in requested_receivers]
343.             )
344. 
345.         self._restart_if_receivers_changed()
346. 
347.     def _restart_if_receivers_changed(self):
348.         # if the receivers have changed, we need to reconfigure tempo
349.         self.unit.status = MaintenanceStatus("reconfiguring Tempo...")
350.         updated = self._update_tempo_config()
351.         if not updated:
352.             logger.debug("Config not updated; skipping tempo restart")
353.         if updated:
354.             restarted = self.tempo.is_tempo_service_defined and self.tempo.restart()
355.             if not restarted:
356.                 # assume that this will be handled at the next pebble-ready
357.                 logger.debug("Cannot reconfigure/restart tempo at this time.")
358. 
359.     def _requested_receivers(self) -> Tuple[ReceiverProtocol, ...]:
360.         """List what receivers we should activate, based on the active tracing relations."""
361.         # we start with the sum of the requested endpoints from the requirers
362.         requested_protocols = set(self.tracing.requested_protocols())
363. 
364.         # and publish only those we support
365.         requested_receivers = requested_protocols.intersection(set(self.tempo.receiver_ports))
366.         requested_receivers.update(self.tempo.enabled_receivers)
367.         return tuple(requested_receivers)
368. 
369.     def _on_tempo_pebble_custom_notice(self, event: PebbleNoticeEvent):
370.         if event.notice.key == self.tempo.tempo_ready_notice_key:
371.             # collect-unit-status should now report ready.
372.             logger.debug("pebble api reports ready")
373. 
374.             try:
375.                 self.tempo.container.stop("tempo-ready")
376.                 # ops will fire APIError but ops.testing._TestingPebbleClient will fire RuntimeError.
377.             except (APIError, RuntimeError):
378.                 # see https://matrix.to/#/!xzmWHtGpPfVCXKivIh:ubuntu.com/
379.                 #  $d42wOu61e5mqMhnDRUB6K8eV4kUAPQ_yhIQmqq5Q_cs?via=ubuntu.com&
380.                 #  via=matrix.org&via=matrix.debian.social
```

</details>


---

<sub>⏱️ 3m 56s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/blob/main/tracing/ops_tracing/_api.py**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/blob/main/tracing/ops_tracing/_api.py",
  "raw": false,
  "max_length": 10000
}
```

</details>

<details>
<summary>118 lines</summary>

```
Contents of https://github.com/canonical/operator/blob/main/tracing/ops_tracing/_api.py:
*   *   AI CODE CREATION
        
        *   [
            
            GitHub CopilotWrite better code with AI
            
            
            
            ](https://github.com/features/copilot)
        *   [
            
            GitHub SparkBuild and deploy intelligent apps
            
            
            
            ](https://github.com/features/spark)
        *   [
            
            GitHub ModelsManage and compare prompts
            
            
            
            ](https://github.com/features/models)
        *   [
            
            MCP RegistryNewIntegrate external tools
            
            
            
            ](https://github.com/mcp)
        
    *   DEVELOPER WORKFLOWS
        
        *   [
            
            ActionsAutomate any workflow
            
            
            
            ](https://github.com/features/actions)
        *   [
            
            CodespacesInstant dev environments
            
            
            
            ](https://github.com/features/codespaces)
        *   [
            
            IssuesPlan and track work
            
            
            
            ](https://github.com/features/issues)
        *   [
            
            Code ReviewManage code changes
            
            
            
            ](https://github.com/features/code-review)
        
    *   APPLICATION SECURITY
        
        *   [
            
            GitHub Advanced SecurityFind and fix vulnerabilities
            
            
            
            ](https://github.com/security/advanced-security)
        *   [
            
            Code securitySecure your code as you build
            
            
            
            ](https://github.com/security/advanced-security/code-security)
        *   [
            
            Secret protectionStop leaks before they start
            
            
            
            ](https://github.com/security/advanced-security/secret-protection)
        
    *   EXPLORE
        
        *   [Why GitHub](https://github.com/why-github)
        *   [Documentation](https://docs.github.com)
        *   [Blog](https://github.blog)
        *   [Changelog](https://github.blog/changelog)
        *   [Marketplace](https://github.com/marketplace)
        
    
    [View all features](https://github.com/features)
    
*   *   BY COMPANY SIZE
        
        *   [Enterprises](https://github.com/enterprise)
        *   [Small and medium teams](https://github.com/team)
        *   [Startups](https://github.com/enterprise/startups)
        *   [Nonprofits](https://github.com/solutions/industry/nonprofits)
        
    *   BY USE CASE
        
        *   [App Modernization](https://github.com/solutions/use-case/app-modernization)
        *   [DevSecOps](https://github.com/solutions/use-case/devsecops)
        *   [DevOps](https://github.com/solutions/use-case/devops)
        *   [CI/CD](https://github.com/solutions/use-case/ci-cd)
        *   [View all use cases](https://github.com/solutions/use-case)
        
    *   BY INDUSTRY
        
        *   [Healthcare](https://github.com/solutions/industry/healthcare)
        *   [Financial services](https://github.com/solutions/industry/financial-services)
        *   [Manufacturing](https://github.com/solutions/industry/manufacturing)
        *   [Government](https://github.com/solutions/industry/government)
        *   [View all industries](https://github.com/solutions/industry)
        
    
    [View all solutions](https://github.com/solutions)
    
*   *   EXPLORE BY TOPIC
        
        *   [AI](https://github.com/resources/articles?topic=ai)
        *   [Software Development](https://github.com/resources/articles?topic=software-development)
        *   [DevOps](https://github.com/resources/articles?topic=devops)
        *   [Security](https://github.com/resources/articles?topic=security)
        *   [View all topics](https://github.com/resources/articles)
        
    *   EXPLORE BY TYPE
        
        *   [Customer stories](https://github.com/customer-stories)
        *   [Events & webinars](https://github.com/resources/events)
        *   [Ebooks & reports](https://github.com/resources/whitepapers)
        *   [Business insights](https://github.com/solutions/executive-insights)
        *   [GitHub Skills](https://skills.github.com)
        
    *   SUPPORT & SERVICES
        
        *   [Documentation](https://docs.github.com)
        *   [Customer support](https://support.github.com)
        *   [Community forum](https://github.com/orgs/community/discussions)
        *   [Trust center](https://github.com/trust-center)
        *   [Partners](https://github.com/partners)
        
    
    [View all resources](https://github.com/resources)
    
*   *   COMMUNITY
        
        *   [
            
            GitHub SponsorsFund open source developers
            
            
            
            ](https://github.com/sponsors)
        
    *   PROGRAMS
        
        *   [Security Lab](https://securitylab.github.com)
        *   [Maintainer Community](https://maintainers.github.com)
        *   [Accelerator](https://github.com/accelerator)
        *   [GitHub Stars](https://stars.github.com)
        *   [Archive Program](https://archiveprogram.github.com)
        
    *   REPOSITORIES
        
        *   [Topics](https://github.com/topics)
        *   [Trending](https://github.com/trending)
        *   [Collections](https://github.com/collections)
        
    
*   *   ENTERPRISE SOLUTIONS
        
        *   [
            
            Enterprise platformAI-powered developer platform
            
            
            
            ](https://github.com/enterprise)
        
    *   AVAILABLE ADD-ONS
        
        *   [
            
            GitHub Advanced SecurityEnterprise-grade security features
            
            
            
            ](https://github.com/security/advanced-security)
        *   [
            
            Copilot for BusinessEnterprise-grade AI features
            
            
            
            ](https://github.com/features/copilot/copilot-business)
        *   [
            
            Premium SupportEnterprise-grade 24/7 support
            
            
            
            ](https://github.com/premium-support)
        
    
*   [Pricing](https://github.com/pricing)

## Provide feedback

We read every piece of feedback, and take your input very seriously.

Include my email address so I can be contacted

## Saved searches

## Use saved searches to filter your results more quickly

[Sign in](/login?return_to=https%3A%2F%2Fgithub.com%2Fcanonical%2Foperator%2Fblob%2Fmain%2Ftracing%2Fops_tracing%2F_api.py)

[Sign up](/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F%3Cuser-name%3E%2F%3Crepo-name%3E%2Fblob%2Fshow&source=header-repo&source_repo=canonical%2Foperator)

Appearance settings
```

</details>


---

<sub>⏱️ 4m 6s</sub>

### ✅ `web_fetch`

**https://raw.githubusercontent.com/canonical/operator/main/tracing/ops_tracing/_api.py**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://raw.githubusercontent.com/canonical/operator/main/tracing/ops_tracing/_api.py"
}
```

</details>

<details>
<summary>179 lines</summary>

```
Content type text/plain; charset=utf-8 cannot be simplified to markdown. Here is the raw content:
Contents of https://raw.githubusercontent.com/canonical/operator/main/tracing/ops_tracing/_api.py:
# Copyright 2025 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The tracing API for the charms."""

from __future__ import annotations

import logging

import opentelemetry.trace
import ops

from ._buffer import Destination
from .vendor.charms.certificate_transfer_interface.v1.certificate_transfer import (
    CertificateTransferRequires,
)
from .vendor.charms.tempo_coordinator_k8s.v0.tracing import (
    AmbiguousRelationUsageError,
    ProtocolNotRequestedError,
    TracingEndpointRequirer,
)

logger = logging.getLogger(__name__)
tracer = opentelemetry.trace.get_tracer('ops.tracing')


class Tracing(ops.Object):
    """Initialise the tracing service.

    Usage:
        - Include ``ops[tracing]`` in your dependencies.
        - Declare the relations that the charm supports.
        - Initialise ``Tracing`` with the names of these relations.

    Example::

        # charmcraft.yaml
        requires:
            charm-tracing:
                interface: tracing
                limit: 1
                optional: true
            receive-ca-cert:
                interface: certificate_transfer
                limit: 1
                optional: true

        # src/charm.py
        import ops.tracing

        class SomeCharm(ops.CharmBase):
            def __init__(self, framework: ops.Framework):
                ...
                self.tracing = ops.tracing.Tracing(
                    self,
                    tracing_relation_name="charm-tracing",
                    ca_relation_name="receive-ca-cert",
                )

    Args:
        charm: your charm instance
        tracing_relation_name: the name of the relation that provides the
            destination to send trace data to.
        ca_relation_name: the name of the relation that provides the CA
            list to validate the tracing destination against.
        ca_data: a fixed CA list (PEM bundle, a multi-line string).

    If the destination is resolved to an HTTPS URL, a CA list is required
    to establish a secure connection.

    The CA list can be provided over a relation via the ``ca_relation_name``
    argument, as a fixed string via the ``ca_data`` argument, or the system CA
    list will be used if the earlier two are both ``None``.
    """

    def __init__(
        self,
        charm: ops.CharmBase,
        tracing_relation_name: str,
        *,
        ca_relation_name: str | None = None,
        ca_data: str | None = None,
    ):
        """Initialise the tracing service."""
        with tracer.start_as_current_span('ops.tracing.Tracing'):
            super().__init__(charm, f'{tracing_relation_name}+{ca_relation_name}')
            self.charm = charm
            self.tracing_relation_name = tracing_relation_name
            self.ca_relation_name = ca_relation_name
            self.ca_data = ca_data

            if ca_relation_name is not None and ca_data is not None:
                raise ValueError('At most one of ca_relation_name, ca_data is allowed')

            # Validate the arguments manually to raise exceptions with helpful messages.
            relation = self.charm.meta.relations.get(tracing_relation_name)
            if not relation:
                raise ValueError(f'{tracing_relation_name=} is not declared in charm metadata')

            if relation.role is not ops.RelationRole.requires:
                raise ValueError(
                    f"{tracing_relation_name=} {relation.role=} when 'requires' is expected"
                )

            if relation.interface_name != 'tracing':
                raise ValueError(
                    f"{tracing_relation_name=} {relation.interface_name=} when 'tracing' is"
                    f' expected'
                )

            self._tracing = TracingEndpointRequirer(
                self.charm,
                tracing_relation_name,
                protocols=['otlp_http'],
            )

            for event in (
                self.charm.on.start,
                self.charm.on.upgrade_charm,
                self._tracing.on.endpoint_changed,
                self._tracing.on.endpoint_removed,
            ):
                self.framework.observe(event, self._reconcile)

            if ca_relation_name:
                relation = self.charm.meta.relations.get(ca_relation_name)
                if not relation:
                    raise ValueError(f'{ca_relation_name=} is not declared in charm metadata')

                if relation.role is not ops.RelationRole.requires:
                    raise ValueError(
                        f"{ca_relation_name=} {relation.role=} when 'requires' is expected"
                    )
                if relation.interface_name != 'certificate_transfer':
                    raise ValueError(
                        f'{ca_relation_name=} {relation.interface_name=} when'
                        f" 'certificate_transfer' is expected"
                    )

                self._certificate_transfer = CertificateTransferRequires(charm, ca_relation_name)

                for event in (
                    self._certificate_transfer.on.certificate_set_updated,
                    self._certificate_transfer.on.certificates_removed,
                ):
                    self.framework.observe(event, self._reconcile)
            else:
                self._certificate_transfer = None

    def _reconcile(self, _event: ops.EventBase):
        dst = self._get_destination()
        ops.tracing.set_destination(url=dst.url, ca=dst.ca)

    def _get_destination(self) -> Destination:
        try:
            if not self._tracing.is_ready():
                return Destination(None, None)

            base_url = self._tracing.get_endpoint('otlp_http')

            if not base_url:
                return Destination(None, None)

            if not base_url.startswith(('http://', 'https://')):
                logger.warning('The base_url=%s must be an HTTP or an HTTPS URL', base_url)
                return Destination(None, None)

            url = f'{base_url.rstrip("/")}/v1/traces'

            if url.startswith('http://'):
                return Destination(url, None)

            if not self._certificate_transfer:
                return Destination(url, self.ca_data)

            ca = self._get_ca()
            if not ca:
                return Destination(None, None)

            return Destination(url, ca)
        except (
            ops.TooManyRelatedAppsError,
            AmbiguousRelationUsageError,
            ProtocolNotRequestedError,
        ):
            # These should not really happen, as we've set up a single relation
            # and requested the protocol explicitly.
            logger.exception('Error getting the tracing destination')
            return Destination(None, None)

    def _get_ca(self) -> str | None:
        if not self.ca_relation_name:
            return None

        ca_rel = self.model.get_relation(self.ca_relation_name)
        if not ca_rel:
            return None

        if not self._certificate_transfer:
            return None

        if not self._certificate_transfer.is_ready(ca_rel):
            return None

        ca_list = self._certificate_transfer.get_all_certificates(ca_rel.id)
        if not ca_list:
            return None

        return '\n'.join(sorted(ca_list))
```

</details>


---

<sub>⏱️ 4m 6s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py (lines 380-455)

<details>
<summary>76 lines</summary>

```
380.                 #  via=matrix.org&via=matrix.debian.social
381.                 # issue: on sleep/resume, we get this event but there's no tempo-ready
382.                 # service in pebble (somehow?)
383.                 logger.debug(
384.                     "`tempo-ready` service cannot be stopped at this time (probably doesn't exist)."
385.                 )
386. 
387.     def _on_tempo_pebble_ready(self, event: WorkloadEvent):
388.         if not self.tempo.container.can_connect():
389.             logger.warning("container not ready, cannot configure; will retry soon")
390.             return event.defer()
391. 
392.         self._update_tempo_config()
393.         self.tempo.plan()
394. 
395.         self.unit.set_workload_version(self.version)
396.         self.unit.status = ActiveStatus()
397. 
398.     def _on_update_status(self, _):
399.         """Update the status of the application."""
400.         self.unit.set_workload_version(self.version)
401. 
402.     def _on_ingress_ready(self, _event):
403.         # whenever there's a change in ingress, we need to update all tracing relations
404.         self._update_tracing_relations()
405. 
406.     def _on_ingress_revoked(self, _event):
407.         # whenever there's a change in ingress, we need to update all tracing relations
408.         self._update_tracing_relations()
409. 
410.     @property
411.     def version(self) -> str:
412.         """Reports the current Tempo version."""
413.         container = self.unit.get_container("tempo")
414.         if container.can_connect() and container.get_services("tempo"):
415.             try:
416.                 return self._get_version() or ""
417.             # Catching Exception is not ideal, but we don't care much for the error here, and just
418.             # default to setting a blank version since there isn't much the admin can do!
419.             except Exception as e:
420.                 logger.warning("unable to get version from API: %s", str(e))
421.                 logger.debug(e, exc_info=True)
422.                 return ""
423.         return ""
424. 
425.     def _get_version(self) -> Optional[str]:
426.         """Fetch the version from the running workload using the Tempo CLI.
427. 
428.         Helper function.
429.         """
430.         container = self.unit.get_container("tempo")
431.         proc = container.exec(["/tempo", "-version"])
432.         out, err = proc.wait_output()
433. 
434.         # example output:
435.         # / # /tempo --version
436.         # tempo, version  (branch: HEAD, revision: fd5743d5d)
437.         #   build user:
438.         #   build date:
439.         #   go version:       go1.18.5
440.         #   platform:         linux/amd64
441. 
442.         if version_head := re.search(r"tempo, version (.*) \(branch: (.*), revision: (.*)\)", out):
443.             v_head, b_head, r_head = version_head.groups()
444.             version = f"{v_head}:{b_head}/{r_head}"
445.         elif version_headless := re.search(r"tempo, version (\S+)", out):
446.             version = version_headless.groups()[0]
447.         else:
448.             logger.warning(
449.                 f"unable to determine tempo workload version: output {out} "
450.                 f"does not match any known pattern"
451.             )
452.             return
453.         return version
454. 
455.     def server_cert(self):
```

</details>


---

<sub>⏱️ 11m 33s</sub>

### 💬 Copilot

Now I have a clear picture. Let me look at what tests exist and the remaining charm file sections before making changes.

---

<sub>⏱️ 11m 33s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/pyproject.toml.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/pyproject.toml

<details>
<summary>74 lines</summary>

```
1. # Copyright 2022 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. [project]
4. name = "tempo-k8s"
5. version = "0.1"  # this is in fact irrelevant
6. 
7. [project.optional-dependencies]
8. lib_pydeps = [
9. ]
10. 
11. [tool.pyright]
12. extraPaths = ["lib"]
13. pythonVersion = "3.8"
14. pythonPlatform = "All"
15. 
16. [build]
17. build-base = "/tmp/build"
18. 
19. [egg_info]
20. egg-base = "/tmp"
21. 
22. # Testing tools configuration
23. [tool.coverage.run]
24. branch = true
25. 
26. [tool.coverage.report]
27. show_missing = true
28. 
29. [tool.pytest.ini_options]
30. minversion = "6.0"
31. log_cli_level = "INFO"
32. markers = ["setup", "teardown"]
33. 
34. # Formatting tools configuration
35. [tool.isort]
36. profile = "black"
37. 
38. [tool.black]
39. line-length = 99
40. target-version = ["py38"]
41. 
42. # Linting tools configuration
43. [tool.ruff]
44. line-length = 99
45. extend-exclude = ["__pycache__", "*.egg_info", "*integration/tester*"]
46. 
47. [tool.ruff.lint]
48. select = ["E", "W", "F", "C", "N", "D", "I001"]
49. extend-ignore = [
50.     "D203",
51.     "D204",
52.     "D213",
53.     "D215",
54.     "D400",
55.     "D404",
56.     "D406",
57.     "D407",
58.     "D408",
59.     "D409",
60.     "D413",
61. ]
62. ignore = ["E501", "D107"]
63. 
64. [tool.ruff.lint.per-file-ignores]
65. "tests/*" = ["D100","D101","D102","D103","D104"]
66. # Remove charm_tracing.py E402 when _remove_stale_otel_sdk_packages() is removed
67. # from the library
68. "lib/charms/tempo_k8s/v1/charm_tracing.py" = ["E402"]
69. 
70. [lint.mccabe]
71. max-complexity = 10
72. 
73. [tool.codespell]
74. skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.vscode,.coverage"
```

</details>


---

<sub>⏱️ 11m 34s</sub>

### ✅ `bash`

**Find tracing references in tests**

$ grep -rn "charm_tracing\|trace_charm\|tracing_endpoint\|server_cert\|tempo_otlp_http_endpoint\|enable_receivers" /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/ 2>/dev/null | head -40

<details>
<summary>41 lines</summary>

```
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_tls.py:60:def server_cert(ops_test: OpsTest):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_tls.py:82:        f"TRACEGEN_CERT={Tempo.server_cert_path if use_cert else ''} "
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_tls.py:135:async def test_verify_trace_http_no_tls_fails(ops_test: OpsTest, server_cert, nonce):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_tls.py:145:async def test_verify_trace_http_tls(ops_test: OpsTest, nonce, server_cert):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_tls.py:153:async def test_verify_traces_grpc_tls(ops_test: OpsTest, nonce, server_cert):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/conftest.py:38:        "tempo_k8s/v1/charm_tracing.py",
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_ingressed_tls.py:36:def server_cert(ops_test: OpsTest):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_ingressed_tls.py:80:        f"TRACEGEN_CERT={Tempo.server_cert_path if use_cert else ''} "
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_ingressed_tls.py:151:async def test_verify_ingressed_trace_http_tls(ops_test: OpsTest, nonce, server_cert):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/test_ingressed_tls.py:161:async def test_verify_ingressed_traces_grpc_tls(ops_test: OpsTest, nonce, server_cert):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester/src/charm.py:9:from charms.tempo_k8s.v1.charm_tracing import trace_charm
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester/src/charm.py:26:@trace_charm(tracing_endpoint="tempo_otlp_http_endpoint", service_name=TRACING_APP_NAME)
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester/src/charm.py:102:            "TEMPO_ENDPOINT": str(self.tempo_otlp_http_endpoint or ""),
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/integration/tester/src/charm.py:257:    def tempo_otlp_http_endpoint(self) -> Optional[str]:
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py:6:from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py:23:        with charm_tracing_disabled():
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py:5:from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py:22:    with charm_tracing_disabled():
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py:5:from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py:28:    with charm_tracing_disabled(), patch.object(Tempo, "tls_ready", local_has_tls):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py:42:def test_tracing_endpoints_with_tls(
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py:75:def test_tracing_endpoints_tls_added_then_removed(context, base_state, has_ingress):
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py:6:from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py:28:    with charm_tracing_disabled():
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py:34:    with charm_tracing_disabled():
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_a_charm_tracer_multi_import_warning.py:12:from charms.tempo_k8s.v1.charm_tracing import _autoinstrument as autoinstrument
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_a_charm_tracer_multi_import_warning.py:17:from lib.charms.tempo_k8s.v1.charm_tracing import trace
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm_tracing.py:8:from charms.tempo_k8s.v1.charm_tracing import CHARM_TRACING_ENABLED, get_current_span, trace
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm_tracing.py:9:from charms.tempo_k8s.v1.charm_tracing import _autoinstrument as autoinstrument
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm_tracing.py:158:        # assert "quietly disabling charm_tracing for the run." in caplog.text
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm_tracing.py:420:    """Verify that the charm errors out (even with charm_tracing disabled) if the tempo() call raises."""
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm_tracing.py:456:    """Verify that the charm exits 1 (even with charm_tracing disabled) if the tempo() call returns bad values."""
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm_tracing.py:463:    # traceback from the TypeError raised by _get_tracing_endpoint
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_legacy.py:4:from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_legacy.py:18:    with charm_tracing_disabled():
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_provider.py:2:from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_provider.py:38:    with charm_tracing_disabled():
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py:4:from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py:47:    with charm_tracing_disabled():
/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py:76:    with charm_tracing_disabled():
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 33s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py (lines 530-578)

<details>
<summary>49 lines</summary>

```
530.             res[receiver.replace("_", "-")] = (
531.                 f"{self.ingress.external_host or self.tempo.url}:{self.tempo.receiver_ports[receiver]}"
532.             )
533.         event.set_results(res)
534. 
535.     @property
536.     def _static_ingress_config(self) -> dict:
537.         entry_points = {}
538.         for protocol, port in self.tempo.all_ports.items():
539.             sanitized_protocol = protocol.replace("_", "-")
540.             entry_points[sanitized_protocol] = {"address": f":{port}"}
541. 
542.         return {"entryPoints": entry_points}
543. 
544.     @property
545.     def _ingress_config(self) -> dict:
546.         """Build a raw ingress configuration for Traefik."""
547.         http_routers = {}
548.         http_services = {}
549.         for protocol, port in self.tempo.all_ports.items():
550.             sanitized_protocol = protocol.replace("_", "-")
551.             http_routers[f"juju-{self.model.name}-{self.model.app.name}-{sanitized_protocol}"] = {
552.                 "entryPoints": [sanitized_protocol],
553.                 "service": f"juju-{self.model.name}-{self.model.app.name}-service-{sanitized_protocol}",
554.                 # TODO better matcher
555.                 "rule": "ClientIP(`0.0.0.0/0`)",
556.             }
557.             if sanitized_protocol.endswith("grpc") and not self.tls_available:
558.                 # to send traces to unsecured GRPC endpoints, we need h2c
559.                 # see https://doc.traefik.io/traefik/v2.0/user-guides/grpc/#with-http-h2c
560.                 http_services[
561.                     f"juju-{self.model.name}-{self.model.app.name}-service-{sanitized_protocol}"
562.                 ] = {"loadBalancer": {"servers": [{"url": f"h2c://{self.hostname}:{port}"}]}}
563.             else:
564.                 # anything else, including secured GRPC, can use _internal_url
565.                 # ref https://doc.traefik.io/traefik/v2.0/user-guides/grpc/#with-https
566.                 http_services[
567.                     f"juju-{self.model.name}-{self.model.app.name}-service-{sanitized_protocol}"
568.                 ] = {"loadBalancer": {"servers": [{"url": f"{self._internal_url}:{port}"}]}}
569.         return {
570.             "http": {
571.                 "routers": http_routers,
572.                 "services": http_services,
573.             },
574.         }
575. 
576. 
577. if __name__ == "__main__":  # pragma: nocover
578.     main(TempoCharm)
```

</details>


---

<sub>⏱️ 11m 56s</sub>

### ✅ `bash`

**List scenario tests**

$ ls /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/

```
conftest.py				     test_charm.py	    test_ingressed_tracing.py  test_tracing_provider.py
helpers.py				     test_charm_scaling.py  test_tls.py		       test_tracing_requirer.py
test_a_charm_tracer_multi_import_warning.py  test_charm_tracing.py  test_tracing_legacy.py
<exited with exit code 0>
```


---

<sub>⏱️ 11m 55s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py

<details>
<summary>205 lines</summary>

```
1. from pathlib import Path
2. from unittest.mock import MagicMock
3. 
4. import pytest
5. import yaml
6. from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
7. from charms.tempo_k8s.v2.tracing import TracingRequirerAppData
8. from ops import pebble
9. from scenario import Container, Mount, Relation, State
10. from scenario.sequences import check_builtin_sequences
11. from scenario.state import Notice, _BoundNotice
12. 
13. from tempo import Tempo
14. from tests.scenario.helpers import get_tempo_config
15. 
16. TEMPO_CHARM_ROOT = Path(__file__).parent.parent.parent
17. 
18. 
19. @pytest.fixture(params=(True, False))
20. def base_state(request):
21.     return State(
22.         leader=request.param,
23.         containers=[Container("tempo", can_connect=True)],
24.     )
25. 
26. 
27. def test_builtin_sequences(tempo_charm, base_state):
28.     with charm_tracing_disabled():
29.         check_builtin_sequences(tempo_charm, template_state=base_state)
30. 
31. 
32. def test_start(context, base_state):
33.     # verify the charm runs at all with and without leadership
34.     with charm_tracing_disabled():
35.         context.run("start", base_state)
36. 
37. 
38. @pytest.mark.parametrize("requested_protocol", ("otlp_grpc", "zipkin"))
39. def test_tempo_restart_on_ingress_v2_changed(context, tmp_path, requested_protocol):
40.     # GIVEN
41.     # an initial configuration with an otlp_http receiver
42.     container, tempo = _tempo_mock_with_initial_config(tmp_path)
43. 
44.     # the remote end requests an otlp_grpc endpoint
45.     ingress = Relation(
46.         "tracing",
47.         remote_app_data=TracingRequirerAppData(receivers=[requested_protocol]).dump(),
48.     )
49. 
50.     # WHEN
51.     # the charm receives an ingress(v2) relation-changed requesting an otlp_grpc receiver
52.     state = State(leader=True, containers=[tempo], relations=[ingress])
53.     context.run(ingress.changed_event, state)
54. 
55.     # THEN
56.     # Tempo pushes a new config to the container filesystem
57.     new_config = get_tempo_config(tempo, context)
58.     expected_config = Tempo(container).generate_config(
59.         ["otlp_http", requested_protocol],
60.     )
61.     assert new_config == expected_config
62.     # AND restarts the pebble service.
63.     assert (
64.         context.output_state.get_container("tempo").service_status["tempo"]
65.         is pebble.ServiceStatus.ACTIVE
66.     )
67. 
68. 
69. def _tempo_mock_with_initial_config(tmp_path, tempo_ready_svc_exists: bool = True):
70.     tempo_config = tmp_path / "tempo.yaml"
71.     container = MagicMock()
72.     container.can_connect = lambda: True
73.     # prevent tls_ready from reporting True
74.     container.exists = lambda path: (
75.         False if path in [Tempo.tls_cert_path, Tempo.tls_key_path, Tempo.tls_ca_path] else True
76.     )
77.     initial_config = Tempo(container).generate_config(["otlp_http"])
78.     tempo_config.write_text(yaml.safe_dump(initial_config))
79.     layer_raw = {
80.         "summary": "tempo layer",
81.         "description": "foo",
82.         "services": {
83.             "tempo": {"startup": "enabled"},
84.         },
85.     }
86.     if tempo_ready_svc_exists:
87.         layer_raw["services"]["tempo-ready"] = {"startup": "disabled"}
88. 
89.     tempo = Container(
90.         "tempo",
91.         can_connect=True,
92.         layers={
93.             "tempo": pebble.Layer(
94.                 layer_raw,
95.             ),
96.         },
97.         service_status={
98.             # we don't have a way to check if the service has been restarted: all that scenario does ATM is set it to
99.             # 'active'.
100.             # so as a way to check that it's been restarted, we must set it to inactive here.
101.             "tempo": pebble.ServiceStatus.INACTIVE,
102.         },
103.         mounts={
104.             "data": Mount("/etc/tempo/tempo.yaml", tempo_config),
105.         },
106.     )
107.     return container, tempo
108. 
109. 
110. def test_tempo_tracing_created_before_pebble_ready(context, tmp_path):
111.     # GIVEN there is no plan yet
112.     tempo = Container(
113.         "tempo",
114.         can_connect=True,
115.     )
116. 
117.     # WHEN
118.     # the charm receives a tracing-relation-created requesting an otlp_grpc receiver
119.     tracing = Relation(
120.         "tracing",
121.         remote_app_data={"receivers": '["otlp_http"]'},
122.         local_app_data={
123.             "receivers": '[{"protocol": {"name": "otlp_grpc", "type": "grpc"} , "url": "foo.com:10"}, '
124.             '{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://foo.com:11"}, ',
125.         },
126.     )
127.     state = State(leader=True, containers=[tempo], relations=[tracing])
128.     state_out = context.run(tracing.created_event, state)
129. 
130.     # THEN
131.     # tempo still has no services
132.     tempo_out = state_out.get_container("tempo")
133.     assert not tempo_out.services
134. 
135. 
136. def test_tracing_storage_is_configured_to_local_without_relation(context, tmp_path):
137.     # GIVEN tempo mock
138.     container, tempo = _tempo_mock_with_initial_config(tmp_path)
139. 
140.     # WHEN any event comes in
141.     state = State(leader=True, containers=[tempo], relations=[])
142.     context.run("update-status", state)
143. 
144.     # THEN tempo's config has a local storage configured
145.     config = get_tempo_config(tempo, context)
146.     expected_config = Tempo(container).generate_config(["otlp_http"])
147.     assert config == expected_config
148.     assert config["storage"]["trace"]["backend"] == "local"
149. 
150. 
151. @pytest.mark.parametrize(
152.     "relation_data",
153.     (
154.         {},
155.         {
156.             "access-key": "key",
157.             "bucket": "tempo",
158.             "endpoint": "http://1.2.3.4:9000",
159.             "secret-key": "soverysecret",
160.         },
161.     ),
162. )
163. def test_tracing_storage_is_configured_to_s3_if_s3_relation_filled(
164.     context,
165.     tmp_path,
166.     relation_data,
167. ):
168.     # GIVEN tempo mock
169.     container, tempo = _tempo_mock_with_initial_config(tmp_path)
170. 
171.     # WHEN a charm receives an s3 relation
172.     s3_relation = Relation(
173.         "s3",
174.         remote_app_data=relation_data,
175.         local_app_data={"bucket": "tempo"},
176.     )
177. 
178.     state = State(leader=True, containers=[tempo], relations=[s3_relation])
179.     context.run(s3_relation.changed_event, state)
180. 
181.     # THEN
182.     # Tempo's config contains the data from the relation
183.     new_config = get_tempo_config(tempo, context)
184.     expected_config = Tempo(container).generate_config(["otlp_http"], relation_data)
185.     assert new_config == expected_config
186. 
187. 
188. def test_ready_check_on_resume(context, tmp_path, caplog, monkeypatch):
189.     # GIVEN the charm has no tempo-ready service
190.     container, tempo = _tempo_mock_with_initial_config(tmp_path, tempo_ready_svc_exists=False)
191. 
192.     state = State(leader=True, containers=[tempo])
193. 
194.     # WHEN we receive a custom-notice event
195.     with caplog.at_level("DEBUG"):
196.         monkeypatch.setenv("SCENARIO_SKIP_CONSISTENCY_CHECKS", "1")
197.         # scenario doesn't play nice in this very edge case
198.         context.run(_BoundNotice(Notice(Tempo.tempo_ready_notice_key), tempo).event, state)
199.         monkeypatch.delenv("SCENARIO_SKIP_CONSISTENCY_CHECKS")
200. 
201.     # THEN we get a debug-log but the charm doesn't error
202.     assert "`tempo-ready` service cannot be stopped at this time (probably doesn't exist)." in {
203.         r.message for r in caplog.records
204.     }
205.
```

</details>


---

<sub>⏱️ 12m 21s</sub>

### 💬 Copilot

Let me look at all the affected test files:

---

<sub>⏱️ 12m 21s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/conftest.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/conftest.py

<details>
<summary>19 lines</summary>

```
1. from unittest.mock import patch
2. 
3. import pytest
4. from scenario import Context
5. 
6. from charm import TempoCharm
7. 
8. 
9. @pytest.fixture
10. def tempo_charm():
11.     with patch("charm.KubernetesServicePatch"):
12.         with patch("lightkube.core.client.GenericSyncClient"):
13.             yield TempoCharm
14. 
15. 
16. @pytest.fixture(scope="function")
17. def context(tempo_charm):
18.     return Context(charm_type=tempo_charm)
19.
```

</details>


---

<sub>⏱️ 12m 21s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py

<details>
<summary>134 lines</summary>

```
1. import socket
2. from unittest.mock import patch
3. 
4. import pytest
5. from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
6. from charms.tempo_k8s.v2.tracing import TracingProviderAppData, TracingRequirerAppData
7. from scenario import Container, Relation, State
8. 
9. from charm import Tempo
10. 
11. 
12. @pytest.fixture
13. def base_state():
14.     return State(leader=True, containers=[Container("tempo", can_connect=False)])
15. 
16. 
17. def update_relations_tls_and_verify(
18.     base_state,
19.     context,
20.     has_ingress,
21.     local_has_tls,
22.     local_scheme,
23.     relations,
24.     remote_scheme,
25.     tracing,
26. ):
27.     state = base_state.replace(relations=relations)
28.     with charm_tracing_disabled(), patch.object(Tempo, "tls_ready", local_has_tls):
29.         out = context.run(tracing.changed_event, state)
30.     tracing_provider_app_data = TracingProviderAppData.load(
31.         out.get_relations(tracing.endpoint)[0].local_app_data
32.     )
33.     actual_url = tracing_provider_app_data.receivers[0].url
34.     expected_url = f"{remote_scheme if has_ingress else local_scheme}://{socket.getfqdn() if not has_ingress else 'foo.com.org'}:4318"
35.     assert actual_url == expected_url
36.     return out
37. 
38. 
39. @pytest.mark.parametrize("remote_has_tls", (True, False))
40. @pytest.mark.parametrize("local_has_tls", (True, False))
41. @pytest.mark.parametrize("has_ingress", (True, False))
42. def test_tracing_endpoints_with_tls(
43.     context, base_state, has_ingress, local_has_tls, remote_has_tls
44. ):
45.     tracing = Relation(
46.         "tracing",
47.         remote_app_data=TracingRequirerAppData(receivers=["otlp_http"]).dump(),
48.     )
49.     relations = [tracing]
50. 
51.     local_scheme = "https" if local_has_tls else "http"
52.     remote_scheme = "https" if remote_has_tls else "http"
53. 
54.     if has_ingress:
55.         relations.append(
56.             Relation(
57.                 "ingress",
58.                 remote_app_data={"scheme": remote_scheme, "external_host": "foo.com.org"},
59.             )
60.         )
61. 
62.     update_relations_tls_and_verify(
63.         base_state,
64.         context,
65.         has_ingress,
66.         local_has_tls,
67.         local_scheme,
68.         relations,
69.         remote_scheme,
70.         tracing,
71.     )
72. 
73. 
74. @pytest.mark.parametrize("has_ingress", (True, False))
75. def test_tracing_endpoints_tls_added_then_removed(context, base_state, has_ingress):
76.     tracing = Relation(
77.         "tracing",
78.         remote_app_data=TracingRequirerAppData(receivers=["otlp_http"]).dump(),
79.     )
80.     relations = [tracing]
81. 
82.     local_scheme = "http"
83.     remote_scheme = "http"
84. 
85.     if has_ingress:
86.         relations.append(
87.             Relation(
88.                 "ingress",
89.                 remote_app_data={"scheme": remote_scheme, "external_host": "foo.com.org"},
90.             )
91.         )
92. 
93.     result_state = update_relations_tls_and_verify(
94.         base_state, context, has_ingress, False, local_scheme, relations, remote_scheme, tracing
95.     )
96. 
97.     # then we check the scenario where TLS gets enabled
98. 
99.     local_scheme = "https"
100.     remote_scheme = "https"
101. 
102.     if has_ingress:
103.         # as remote_scheme changed, we need to update the ingress relation
104.         relations.pop()
105.         relations.append(
106.             Relation(
107.                 "ingress",
108.                 remote_app_data={"scheme": remote_scheme, "external_host": "foo.com.org"},
109.             )
110.         )
111. 
112.     result_state = update_relations_tls_and_verify(
113.         result_state, context, has_ingress, True, local_scheme, relations, remote_scheme, tracing
114.     )
115. 
116.     # then we again remove TLS and compare the same thing
117. 
118.     local_scheme = "http"
119.     remote_scheme = "http"
120. 
121.     if has_ingress:
122.         # as remote_scheme changed, we need to update the ingress relation
123.         relations.pop()
124.         relations.append(
125.             Relation(
126.                 "ingress",
127.                 remote_app_data={"scheme": remote_scheme, "external_host": "foo.com.org"},
128.             )
129.         )
130. 
131.     update_relations_tls_and_verify(
132.         result_state, context, has_ingress, False, local_scheme, relations, remote_scheme, tracing
133.     )
134.
```

</details>


---

<sub>⏱️ 12m 30s</sub>

### ✅ `bash`

**Read affected test files**

$ cat /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py
cat /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_legacy.py
cat /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_provider.py
cat /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py
cat /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py

<details>
<summary>365 lines</summary>

```
from unittest.mock import patch

import pytest
import yaml
from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
from scenario import Container, Relation, State

from tempo import Tempo


@pytest.fixture
def base_state():
    return State(leader=True, containers=[Container("tempo", can_connect=False)])


def test_external_url_present(context, base_state):
    # WHEN ingress is related with external_host
    tracing = Relation("tracing", remote_app_data={"receivers": "[]"})
    ingress = Relation("ingress", remote_app_data={"external_host": "1.2.3.4", "scheme": "http"})
    state = base_state.replace(relations=[tracing, ingress])

    with charm_tracing_disabled():
        out = context.run(getattr(tracing, "created_event"), state)

    # THEN external_url is present in tracing relation databag
    tracing_out = out.get_relations(tracing.endpoint)[0]
    assert tracing_out.local_app_data == {
        "receivers": '[{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://1.2.3.4:4318"}]',
    }


@patch("socket.getfqdn", lambda: "1.2.3.4")
def test_ingress_relation_set_with_dynamic_config(context, base_state):
    # WHEN ingress is related with external_host
    ingress = Relation("ingress", remote_app_data={"external_host": "1.2.3.4", "scheme": "http"})
    state = base_state.replace(relations=[ingress])

    with patch.object(Tempo, "is_ready", lambda _: False):
        out = context.run(ingress.joined_event, state)

    expected_rel_data = {
        "http": {
            "routers": {
                f"juju-{state.model.name}-tempo-k8s-jaeger-thrift-http": {
                    "entryPoints": ["jaeger-thrift-http"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-jaeger-thrift-http",
                },
                f"juju-{state.model.name}-tempo-k8s-otlp-http": {
                    "entryPoints": ["otlp-http"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-otlp-http",
                },
                f"juju-{state.model.name}-tempo-k8s-tempo-http": {
                    "entryPoints": ["tempo-http"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-tempo-http",
                },
                f"juju-{state.model.name}-tempo-k8s-zipkin": {
                    "entryPoints": ["zipkin"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-zipkin",
                },
                f"juju-{state.model.name}-tempo-k8s-otlp-grpc": {
                    "entryPoints": ["otlp-grpc"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-otlp-grpc",
                },
                f"juju-{state.model.name}-tempo-k8s-tempo-grpc": {
                    "entryPoints": ["tempo-grpc"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-tempo-grpc",
                },
            },
            "services": {
                f"juju-{state.model.name}-tempo-k8s-service-jaeger-thrift-http": {
                    "loadBalancer": {"servers": [{"url": "http://1.2.3.4:14268"}]}
                },
                f"juju-{state.model.name}-tempo-k8s-service-otlp-http": {
                    "loadBalancer": {"servers": [{"url": "http://1.2.3.4:4318"}]}
                },
                f"juju-{state.model.name}-tempo-k8s-service-tempo-http": {
                    "loadBalancer": {"servers": [{"url": "http://1.2.3.4:3200"}]}
                },
                f"juju-{state.model.name}-tempo-k8s-service-zipkin": {
                    "loadBalancer": {"servers": [{"url": "http://1.2.3.4:9411"}]}
                },
                f"juju-{state.model.name}-tempo-k8s-service-otlp-grpc": {
                    "loadBalancer": {"servers": [{"url": "h2c://1.2.3.4:4317"}]},
                },
                f"juju-{state.model.name}-tempo-k8s-service-tempo-grpc": {
                    "loadBalancer": {"servers": [{"url": "h2c://1.2.3.4:9096"}]}
                },
            },
        },
    }

    # THEN dynamic config is present in ingress relation
    ingress_out = out.get_relations(ingress.endpoint)[0]
    assert yaml.safe_load(ingress_out.local_app_data["config"]) == expected_rel_data
import socket

import pytest
from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
from scenario import Container, Relation, State


@pytest.fixture
def base_state():
    return State(leader=True, containers=[Container("tempo", can_connect=False)])


@pytest.mark.parametrize("evt_name", ("changed", "created", "joined"))
def test_tracing_v2_endpoint_published(context, evt_name, base_state):
    tracing = Relation("tracing", remote_app_data={"receivers": "[]"})
    state = base_state.replace(relations=[tracing])

    with charm_tracing_disabled():
        with context.manager(getattr(tracing, f"{evt_name}_event"), state) as mgr:
            assert len(mgr.charm._requested_receivers()) == 1
            out = mgr.run()

    tracing_out = out.get_relations(tracing.endpoint)[0]
    assert tracing_out.local_app_data == {
        "receivers": f'[{{"protocol": {{"name": "otlp_http", "type": "http"}}, "url": "http://{socket.getfqdn()}:4318"}}]',
    }
import pytest
from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
from charms.tempo_k8s.v2.tracing import ProtocolType, TracingProviderAppData
from scenario import Container, Context, Relation, State


@pytest.fixture
def context(tempo_charm):
    return Context(
        charm_type=tempo_charm,
    )


def test_receivers_removed_on_relation_broken(context):
    tracing_grpc = Relation(
        "tracing",
        remote_app_data={"receivers": '["otlp_grpc"]'},
        local_app_data={
            "receivers": '[{"protocol": {"name": "otlp_grpc", "type": "grpc"} , "url": "foo.com:10"}, '
            '{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://foo.com:11"}, '
        },
    )
    tracing_http = Relation(
        "tracing",
        remote_app_data={"receivers": '["otlp_http"]'},
        local_app_data={
            "receivers": '[{"protocol": {"name": "otlp_grpc", "type": "grpc"} , "url": "foo.com:10"}, '
            '{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://foo.com:11"}, '
        },
    )

    state = State(
        leader=True,
        relations=[tracing_grpc, tracing_http],
        containers=[Container("tempo", can_connect=False)],
    )

    with charm_tracing_disabled():
        with context.manager(tracing_grpc.broken_event, state) as mgr:
            charm = mgr.charm
            assert charm._requested_receivers() == ("otlp_http",)

    state_out = mgr.output
    r_out = [r for r in state_out.relations if r.relation_id == tracing_http.relation_id][0]
    # "otlp_grpc" is gone from the databag
    assert [r.protocol for r in TracingProviderAppData.load(r_out.local_app_data).receivers] == [
        ProtocolType(name="otlp_http", type="http")
    ]
import socket

import pytest
from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
from charms.tempo_k8s.v2.tracing import (
    EndpointChangedEvent,
    EndpointRemovedEvent,
    ProtocolNotRequestedError,
    TracingEndpointRequirer,
)
from ops import CharmBase, Framework, RelationBrokenEvent, RelationChangedEvent
from scenario import Context, Relation, State

from tempo import Tempo


class MyCharm(CharmBase):
    def __init__(self, framework: Framework):
        super().__init__(framework)
        self.tracing = TracingEndpointRequirer(self, protocols=["otlp_grpc"])
        framework.observe(self.tracing.on.endpoint_changed, self._on_endpoint_changed)

    def _on_endpoint_changed(self, e):
        pass


@pytest.fixture
def context():
    return Context(
        charm_type=MyCharm,
        meta={"name": "jolly", "requires": {"tracing": {"interface": "tracing", "limit": 1}}},
    )


def test_requirer_api(context):
    host = socket.getfqdn()
    tracing = Relation(
        "tracing",
        remote_app_data={
            "receivers": f'[{{"protocol": {{"name": "otlp_grpc", "type": "grpc"}}, "url": "{host}:4317"}}, '
            f'{{"protocol": {{"name": "otlp_http", "type": "http"}}, "url": "http://{host}:4318"}}, '
            f'{{"protocol": {{"name": "zipkin", "type": "http"}}, "url": "http://{host}:9411" }}]',
        },
    )
    state = State(leader=True, relations=[tracing])

    with charm_tracing_disabled():
        with context.manager(tracing.changed_event, state) as mgr:
            charm = mgr.charm
            assert charm.tracing.get_endpoint("otlp_grpc") == f"{host}:4317"
            assert charm.tracing.get_endpoint("otlp_http") == f"http://{host}:4318"
            assert charm.tracing.get_endpoint("zipkin") == f"http://{host}:9411"

            rel = charm.model.get_relation("tracing")
            assert charm.tracing.is_ready(rel)

    rchanged, epchanged = context.emitted_events
    assert isinstance(epchanged, EndpointChangedEvent)
    assert epchanged.receivers[0].protocol.name == "otlp_grpc"
    assert epchanged.receivers[1].protocol.name == "otlp_http"
    assert epchanged.receivers[2].protocol.name == "zipkin"


def test_requirer_api_with_internal_scheme(context):
    host = socket.getfqdn()
    tracing = Relation(
        "tracing",
        remote_app_data={
            "receivers": f'[{{"protocol": {{"name": "otlp_grpc", "type": "grpc"}} , "url": "{host}:4317"}}, '
            f'{{"protocol": {{"name": "otlp_http", "type": "http"}}, "url": "https://{host}:4318"}}, '
            f'{{"protocol": {{"name": "zipkin", "type": "http"}}, "url":  "https://{host}:9411"}}]',
        },
    )
    state = State(leader=True, relations=[tracing])

    with charm_tracing_disabled():
        with context.manager(tracing.changed_event, state) as mgr:
            charm = mgr.charm
            assert charm.tracing.get_endpoint("otlp_grpc") == f"{host}:4317"
            assert charm.tracing.get_endpoint("otlp_http") == f"https://{host}:4318"
            assert charm.tracing.get_endpoint("zipkin") == f"https://{host}:9411"

            rel = charm.model.get_relation("tracing")
            assert charm.tracing.is_ready(rel)

    rchanged, epchanged = context.emitted_events
    assert isinstance(epchanged, EndpointChangedEvent)
    assert epchanged.receivers[0].protocol.name == "otlp_grpc"


def test_ingressed_requirer_api(context):
    # WHEN external_url is present in remote app databag
    external_url = "http://1.2.3.4"
    tracing = Relation(
        "tracing",
        remote_app_data={
            "receivers": f'[{{"protocol": {{"name": "otlp_grpc", "type": "grpc"}}, "url": "{external_url.split("://")[1]}:4317" }}, '
            f'{{"protocol": {{"name": "otlp_http", "type": "http"}} , "url": "{external_url}:4318" }}, '
            f'{{"protocol": {{"name": "zipkin", "type": "http"}} , "url": "{external_url}:9411" }}]',
        },
    )
    state = State(leader=True, relations=[tracing])

    # THEN get_endpoint uses external URL instead of the host
    with charm_tracing_disabled():
        with context.manager(tracing.changed_event, state) as mgr:
            charm = mgr.charm
            assert (
                charm.tracing.get_endpoint("otlp_grpc")
                == f"{external_url.split('://')[1]}:{Tempo.receiver_ports['otlp_grpc']}"
            )
            for proto in ["otlp_http", "zipkin"]:
                assert (
                    charm.tracing.get_endpoint(proto)
                    == f"{external_url}:{Tempo.receiver_ports[proto]}"
                )

            rel = charm.model.get_relation("tracing")
            assert charm.tracing.is_ready(rel)

    rchanged, epchanged = context.emitted_events
    assert isinstance(epchanged, EndpointChangedEvent)
    assert epchanged.receivers[0].protocol.name == "otlp_grpc"


@pytest.mark.parametrize(
    "data",
    (
        {
            "ingesters": '[{"protocol": "otlp_grpc", "port": 9999}]',
            "bar": "baz",
        },
        {
            "host": "foo.com",
            "bar": "baz",
        },
        {
            "ingesters": '[{"burp": "barp", "port": 3200}]',
            "host": "foo.com",
        },
        {
            "ingesters": '[{"protocol": "tempo", "burp": "borp"}]',
            "host": "foo.com",
        },
    ),
)
def test_invalid_data(context, data):
    tracing = Relation(
        "tracing",
        remote_app_data=data,
    )
    state = State(leader=True, relations=[tracing])

    def post_event(charm: MyCharm):
        rel = charm.model.get_relation("tracing")
        assert not charm.tracing.is_ready(rel)

    with charm_tracing_disabled():
        context.run(tracing.changed_event, state, post_event=post_event)

    emitted_events = context.emitted_events
    assert len(emitted_events) == 2
    rchanged, rremoved = emitted_events
    assert isinstance(rchanged, RelationChangedEvent)
    assert isinstance(rremoved, EndpointRemovedEvent)


def test_broken(context):
    tracing = Relation("tracing")
    state = State(leader=True, relations=[tracing])

    with charm_tracing_disabled():
        context.run(tracing.broken_event, state)

    emitted_events = context.emitted_events
    assert len(emitted_events) == 2
    rchanged, ebroken = emitted_events
    assert isinstance(rchanged, RelationBrokenEvent)
    assert isinstance(ebroken, EndpointRemovedEvent)


def test_requested_not_yet_replied(context):
    tracing = Relation("tracing")
    state = State(leader=True, relations=[tracing])

    with charm_tracing_disabled():
        with context.manager(tracing.created_event, state) as mgr:
            charm = mgr.charm
            charm.tracing.request_protocols(["otlp_http"])
            charm.tracing.get_endpoint("otlp_http")


def test_not_requested_raises(context):
    tracing = Relation("tracing")
    state = State(leader=True, relations=[tracing])

    with charm_tracing_disabled():
        with context.manager(tracing.created_event, state) as mgr:
            charm = mgr.charm
            with pytest.raises(ProtocolNotRequestedError):
                charm.tracing.get_endpoint("otlp_http")
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
from unittest.mock import patch

import pytest
from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
from interface_tester import InterfaceTester
from ops.pebble import Layer
from scenario.state import Container, State

from charm import TempoCharm


# Interface tests are centrally hosted at https://github.com/canonical/charm-relation-interfaces.
# this fixture is used by the test runner of charm-relation-interfaces to test tempo's compliance
# with the interface specifications.
# DO NOT MOVE OR RENAME THIS FIXTURE! If you need to, you'll need to open a PR on
# https://github.com/canonical/charm-relation-interfaces and change tempo's test configuration
# to include the new identifier/location.
@pytest.fixture
def interface_tester(interface_tester: InterfaceTester):
    with patch("charm.KubernetesServicePatch"):
        with charm_tracing_disabled():
            interface_tester.configure(
                charm_type=TempoCharm,
                state_template=State(
                    leader=True,
                    containers=[
                        Container(
                            name="tempo",
                            can_connect=True,
                            layers={
                                "foo": Layer(
                                    {
                                        "summary": "foo",
                                        "description": "bar",
                                        "services": {
                                            "tempo": {
                                                "startup": "enabled",
                                                "current": "active",
                                                "name": "tempo",
                                            },
                                            "tempo-ready": {
                                                "startup": "enabled",
                                                "current": "active",
                                                "name": "tempo-ready",
                                            },
                                        },
                                        "checks": {},
                                    }
                                )
                            },
                        )
                    ],
                ),
            )
            yield interface_tester
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12m 55s</sub>

### 💬 Copilot

Let me check the Tempo class to understand `enable_receivers`:

---

<sub>⏱️ 12m 55s</sub>

### ✅ `bash`

**Find enable_receivers usage in tempo.py**

$ grep -n "enable_receivers\|enabled_receivers\|generate_config" /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py | head -30

<details>
<summary>6 lines</summary>

```
78:        enable_receivers: Optional[Sequence[ReceiverProtocol]] = None,
85:        self.enabled_receivers = enable_receivers or []
168:        new_config = self.generate_config(requested_receivers, s3_config, peers)
306:    def generate_config(
481:        # it already includes self.enabled_receivers: receivers we have to enable because *this charm* will use them.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 13m 0s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py (lines 75-95)

<details>
<summary>21 lines</summary>

```
75.         self,
76.         container: ops.Container,
77.         external_host: Optional[str] = None,
78.         enable_receivers: Optional[Sequence[ReceiverProtocol]] = None,
79.     ):
80.         # ports source: https://github.com/grafana/tempo/blob/main/example/docker-compose/local/docker-compose.yaml
81. 
82.         # fqdn, if an ingress is not available, else the ingress address.
83.         self._external_hostname = external_host or socket.getfqdn()
84.         self.container = container
85.         self.enabled_receivers = enable_receivers or []
86. 
87.     @property
88.     def tempo_http_server_port(self) -> int:
89.         """Return the receiver port for the built-in tempo_http protocol."""
90.         return self.server_ports["tempo_http"]
91. 
92.     @property
93.     def tempo_grpc_server_port(self) -> int:
94.         """Return the receiver port for the built-in tempo_http protocol."""
95.         return self.server_ports["tempo_grpc"]
```

</details>


---

<sub>⏱️ 13m 0s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/tempo.py (lines 475-490)

<details>
<summary>16 lines</summary>

```
475.             return False
476.         return out == "ready"
477. 
478.     def _build_receivers_config(self, receivers: Sequence[ReceiverProtocol]):  # noqa: C901
479.         # receivers: the receivers we have to enable because the requirers we're related to
480.         # intend to use them
481.         # it already includes self.enabled_receivers: receivers we have to enable because *this charm* will use them.
482.         receivers_set = set(receivers)
483. 
484.         if not receivers_set:
485.             logger.warning("No receivers set. Tempo will be up but not functional.")
486. 
487.         if self.tls_ready:
488.             receiver_config = {
489.                 "tls": {
490.                     "ca_file": str(self.tls_ca_path),
```

</details>


---

<sub>⏱️ 16m 5s</sub>

### 💬 Copilot

Now I have a complete picture. Let me implement all the changes systematically.

---

<sub>⏱️ 16m 5s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/requirements.txt.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/requirements.txt

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/requirements.txt updated with changes.
```


---

<sub>⏱️ 16m 18s</sub>

### 💬 Copilot

Now update `charmcraft.yaml` — add the two new `requires` relations, add `cargo` to build-packages, and remove the opentelemetry package from `charm-binary-python-packages`:

---

<sub>⏱️ 16m 18s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/charmcraft.yaml.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/charmcraft.yaml

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/charmcraft.yaml updated with changes.
```


---

<sub>⏱️ 16m 28s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/charmcraft.yaml.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/charmcraft.yaml

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/charmcraft.yaml updated with changes.
```


---

<sub>⏱️ 16m 40s</sub>

### 💬 Copilot

Now update `src/charm.py` — remove `@trace_charm` and related methods, add `ops.tracing.Tracing`:

---

<sub>⏱️ 16m 40s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 16m 46s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 16m 53s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 17m 1s</sub>

### 💬 Copilot

Now add the `ops.tracing.Tracing` initialization in `__init__` after `self.tracing`:

---

<sub>⏱️ 17m 1s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 17m 10s</sub>

### 💬 Copilot

Remove `self._update_server_cert()` call from `_on_cert_handler_changed`, and remove the three methods (`server_cert`, `_update_server_cert`, `tempo_otlp_http_endpoint`):

---

<sub>⏱️ 17m 10s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 17m 19s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 17m 29s</sub>

### 💬 Copilot

Now check if `Path` is still needed (it was used in `_update_server_cert`):

---

<sub>⏱️ 17m 30s</sub>

### ✅ `bash`

**Check if Path is still used**

$ grep -n "^from pathlib import Path\|Path(" /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py

```
10:from pathlib import Path
<exited with exit code 0>
```


---

<sub>⏱️ 17m 37s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 17m 44s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 18m 6s</sub>

### 💬 Copilot

Now update the scenario tests. First, `test_charm.py`:

---

<sub>⏱️ 18m 6s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 18m 15s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 18m 22s</sub>

### 💬 Copilot

Update the expected config in `test_tempo_restart_on_ingress_v2_changed` (no longer includes `otlp_http` since `enable_receivers` is removed):

---

<sub>⏱️ 18m 22s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 18m 33s</sub>

### 💬 Copilot

Update `test_tracing_storage_is_configured_to_s3_if_s3_relation_filled` expected config:

---

<sub>⏱️ 18m 33s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 18m 41s</sub>

### 💬 Copilot

Now update `test_ingressed_tracing.py`:

---

<sub>⏱️ 18m 41s</sub>

### ❌ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py

```
No match found
```


---

<sub>⏱️ 18m 51s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py (lines 1-30)

<details>
<summary>30 lines</summary>

```
1. from unittest.mock import patch
2. 
3. import pytest
4. import yaml
5. from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
6. from scenario import Container, Relation, State
7. 
8. from tempo import Tempo
9. 
10. 
11. @pytest.fixture
12. def base_state():
13.     return State(leader=True, containers=[Container("tempo", can_connect=False)])
14. 
15. 
16. def test_external_url_present(context, base_state):
17.     # WHEN ingress is related with external_host
18.     tracing = Relation("tracing", remote_app_data={"receivers": "[]"})
19.     ingress = Relation("ingress", remote_app_data={"external_host": "1.2.3.4", "scheme": "http"})
20.     state = base_state.replace(relations=[tracing, ingress])
21. 
22.     with charm_tracing_disabled():
23.         out = context.run(getattr(tracing, "created_event"), state)
24. 
25.     # THEN external_url is present in tracing relation databag
26.     tracing_out = out.get_relations(tracing.endpoint)[0]
27.     assert tracing_out.local_app_data == {
28.         "receivers": '[{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://1.2.3.4:4318"}]',
29.     }
30.
```

</details>


---

<sub>⏱️ 19m 7s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py updated with changes.
```


---

<sub>⏱️ 19m 28s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_ingressed_tracing.py updated with changes.
```


---

<sub>⏱️ 19m 39s</sub>

### 💬 Copilot

Now update `test_tls.py`:

---

<sub>⏱️ 19m 39s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py updated with changes.
```


---

<sub>⏱️ 20m 44s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tls.py updated with changes.
```


---

<sub>⏱️ 21m 32s</sub>

### 💬 Copilot

Now update `test_tracing_legacy.py`:

---

<sub>⏱️ 21m 32s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_legacy.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_legacy.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_legacy.py updated with changes.
```


---

<sub>⏱️ 21m 37s</sub>

### 💬 Copilot

Now update `test_tracing_provider.py`:

---

<sub>⏱️ 21m 37s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_provider.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_provider.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_provider.py updated with changes.
```


---

<sub>⏱️ 21m 49s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_provider.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_provider.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_provider.py updated with changes.
```


---

<sub>⏱️ 21m 57s</sub>

### 💬 Copilot

Now update `test_tracing_requirer.py`:

---

<sub>⏱️ 21m 57s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py updated with changes.
```


---

<sub>⏱️ 22m 10s</sub>

### 💬 Copilot

Now remove all `with charm_tracing_disabled():` wrappers from test_tracing_requirer.py:

---

<sub>⏱️ 22m 10s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py (lines 44-120)

<details>
<summary>77 lines</summary>

```
44.     state = State(leader=True, relations=[tracing])
45. 
46.     with charm_tracing_disabled():
47.         with context.manager(tracing.changed_event, state) as mgr:
48.             charm = mgr.charm
49.             assert charm.tracing.get_endpoint("otlp_grpc") == f"{host}:4317"
50.             assert charm.tracing.get_endpoint("otlp_http") == f"http://{host}:4318"
51.             assert charm.tracing.get_endpoint("zipkin") == f"http://{host}:9411"
52. 
53.             rel = charm.model.get_relation("tracing")
54.             assert charm.tracing.is_ready(rel)
55. 
56.     rchanged, epchanged = context.emitted_events
57.     assert isinstance(epchanged, EndpointChangedEvent)
58.     assert epchanged.receivers[0].protocol.name == "otlp_grpc"
59.     assert epchanged.receivers[1].protocol.name == "otlp_http"
60.     assert epchanged.receivers[2].protocol.name == "zipkin"
61. 
62. 
63. def test_requirer_api_with_internal_scheme(context):
64.     host = socket.getfqdn()
65.     tracing = Relation(
66.         "tracing",
67.         remote_app_data={
68.             "receivers": f'[{{"protocol": {{"name": "otlp_grpc", "type": "grpc"}} , "url": "{host}:4317"}}, '
69.             f'{{"protocol": {{"name": "otlp_http", "type": "http"}}, "url": "https://{host}:4318"}}, '
70.             f'{{"protocol": {{"name": "zipkin", "type": "http"}}, "url":  "https://{host}:9411"}}]',
71.         },
72.     )
73.     state = State(leader=True, relations=[tracing])
74. 
75.     with charm_tracing_disabled():
76.         with context.manager(tracing.changed_event, state) as mgr:
77.             charm = mgr.charm
78.             assert charm.tracing.get_endpoint("otlp_grpc") == f"{host}:4317"
79.             assert charm.tracing.get_endpoint("otlp_http") == f"https://{host}:4318"
80.             assert charm.tracing.get_endpoint("zipkin") == f"https://{host}:9411"
81. 
82.             rel = charm.model.get_relation("tracing")
83.             assert charm.tracing.is_ready(rel)
84. 
85.     rchanged, epchanged = context.emitted_events
86.     assert isinstance(epchanged, EndpointChangedEvent)
87.     assert epchanged.receivers[0].protocol.name == "otlp_grpc"
88. 
89. 
90. def test_ingressed_requirer_api(context):
91.     # WHEN external_url is present in remote app databag
92.     external_url = "http://1.2.3.4"
93.     tracing = Relation(
94.         "tracing",
95.         remote_app_data={
96.             "receivers": f'[{{"protocol": {{"name": "otlp_grpc", "type": "grpc"}}, "url": "{external_url.split("://")[1]}:4317" }}, '
97.             f'{{"protocol": {{"name": "otlp_http", "type": "http"}} , "url": "{external_url}:4318" }}, '
98.             f'{{"protocol": {{"name": "zipkin", "type": "http"}} , "url": "{external_url}:9411" }}]',
99.         },
100.     )
101.     state = State(leader=True, relations=[tracing])
102. 
103.     # THEN get_endpoint uses external URL instead of the host
104.     with charm_tracing_disabled():
105.         with context.manager(tracing.changed_event, state) as mgr:
106.             charm = mgr.charm
107.             assert (
108.                 charm.tracing.get_endpoint("otlp_grpc")
109.                 == f"{external_url.split('://')[1]}:{Tempo.receiver_ports['otlp_grpc']}"
110.             )
111.             for proto in ["otlp_http", "zipkin"]:
112.                 assert (
113.                     charm.tracing.get_endpoint(proto)
114.                     == f"{external_url}:{Tempo.receiver_ports[proto]}"
115.                 )
116. 
117.             rel = charm.model.get_relation("tracing")
118.             assert charm.tracing.is_ready(rel)
119. 
120.     rchanged, epchanged = context.emitted_events
```

</details>


---

<sub>⏱️ 22m 17s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py (lines 120-185)

<details>
<summary>66 lines</summary>

```
120.     rchanged, epchanged = context.emitted_events
121.     assert isinstance(epchanged, EndpointChangedEvent)
122.     assert epchanged.receivers[0].protocol.name == "otlp_grpc"
123. 
124. 
125. @pytest.mark.parametrize(
126.     "data",
127.     (
128.         {
129.             "ingesters": '[{"protocol": "otlp_grpc", "port": 9999}]',
130.             "bar": "baz",
131.         },
132.         {
133.             "host": "foo.com",
134.             "bar": "baz",
135.         },
136.         {
137.             "ingesters": '[{"burp": "barp", "port": 3200}]',
138.             "host": "foo.com",
139.         },
140.         {
141.             "ingesters": '[{"protocol": "tempo", "burp": "borp"}]',
142.             "host": "foo.com",
143.         },
144.     ),
145. )
146. def test_invalid_data(context, data):
147.     tracing = Relation(
148.         "tracing",
149.         remote_app_data=data,
150.     )
151.     state = State(leader=True, relations=[tracing])
152. 
153.     def post_event(charm: MyCharm):
154.         rel = charm.model.get_relation("tracing")
155.         assert not charm.tracing.is_ready(rel)
156. 
157.     with charm_tracing_disabled():
158.         context.run(tracing.changed_event, state, post_event=post_event)
159. 
160.     emitted_events = context.emitted_events
161.     assert len(emitted_events) == 2
162.     rchanged, rremoved = emitted_events
163.     assert isinstance(rchanged, RelationChangedEvent)
164.     assert isinstance(rremoved, EndpointRemovedEvent)
165. 
166. 
167. def test_broken(context):
168.     tracing = Relation("tracing")
169.     state = State(leader=True, relations=[tracing])
170. 
171.     with charm_tracing_disabled():
172.         context.run(tracing.broken_event, state)
173. 
174.     emitted_events = context.emitted_events
175.     assert len(emitted_events) == 2
176.     rchanged, ebroken = emitted_events
177.     assert isinstance(rchanged, RelationBrokenEvent)
178.     assert isinstance(ebroken, EndpointRemovedEvent)
179. 
180. 
181. def test_requested_not_yet_replied(context):
182.     tracing = Relation("tracing")
183.     state = State(leader=True, relations=[tracing])
184. 
185.     with charm_tracing_disabled():
```

</details>


---

<sub>⏱️ 22m 31s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py (lines 185-210)

<details>
<summary>17 lines</summary>

```
185.     with charm_tracing_disabled():
186.         with context.manager(tracing.created_event, state) as mgr:
187.             charm = mgr.charm
188.             charm.tracing.request_protocols(["otlp_http"])
189.             charm.tracing.get_endpoint("otlp_http")
190. 
191. 
192. def test_not_requested_raises(context):
193.     tracing = Relation("tracing")
194.     state = State(leader=True, relations=[tracing])
195. 
196.     with charm_tracing_disabled():
197.         with context.manager(tracing.created_event, state) as mgr:
198.             charm = mgr.charm
199.             with pytest.raises(ProtocolNotRequestedError):
200.                 charm.tracing.get_endpoint("otlp_http")
201.
```

</details>


---

<sub>⏱️ 22m 44s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py updated with changes.
```


---

<sub>⏱️ 23m 18s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py updated with changes.
```


---

<sub>⏱️ 23m 31s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py updated with changes.
```


---

<sub>⏱️ 23m 52s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py updated with changes.
```


---

<sub>⏱️ 24m 0s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py updated with changes.
```


---

<sub>⏱️ 24m 11s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py updated with changes.
```


---

<sub>⏱️ 24m 22s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/scenario/test_tracing_requirer.py updated with changes.
```


---

<sub>⏱️ 24m 29s</sub>

### 💬 Copilot

Now update `tests/interface/conftest.py`:

---

<sub>⏱️ 24m 29s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py updated with changes.
```


---

<sub>⏱️ 24m 39s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py updated with changes.
```


---

<sub>⏱️ 24m 44s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__ops-tracing__C2/tests/interface/conftest.py

<details>
<summary>56 lines</summary>

```
1. # Copyright 2022 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. from unittest.mock import patch
4. 
5. import pytest
6. from interface_tester import InterfaceTester
7. from ops.pebble import Layer
8. from scenario.state import Container, State
9. 
10. from charm import TempoCharm
11. 
12. 
13. # Interface tests are centrally hosted at https://github.com/canonical/charm-relation-interfaces.
14. # this fixture is used by the test runner of charm-relation-interfaces to test tempo's compliance
15. # with the interface specifications.
16. # DO NOT MOVE OR RENAME THIS FIXTURE! If you need to, you'll need to open a PR on
17. # https://github.com/canonical/charm-relation-interfaces and change tempo's test configuration
18. # to include the new identifier/location.
19. @pytest.fixture
20. def interface_tester(interface_tester: InterfaceTester):
21.     with patch("charm.KubernetesServicePatch"):
22.         interface_tester.configure(
23.                 charm_type=TempoCharm,
24.                 state_template=State(
25.                     leader=True,
26.                     containers=[
27.                         Container(
28.                             name="tempo",
29.                             can_connect=True,
30.                             layers={
31.                                 "foo": Layer(
32.                                     {
33.                                         "summary": "foo",
34.                                         "description": "bar",
35.                                         "services": {
36.                                             "tempo": {
37.                                                 "startup": "enabled",
38.                                                 "current": "active",
39.                                                 "name": "tempo",
40.                                             },
41.                                             "tempo-ready": {
42.                                                 "startup": "enabled",
43.                                                 "current": "active",
44.                                                 "name": "tempo-ready",
45.                                             },
46.                                         },
47.                                         "checks": {},
48.                                     }
49.                                 )
50.                             },
51.                         )
52.                     ],
53.                 ),
54.             )
55.             yield interface_tester
56.
```

</details>


---

<sub>⏱️ 24m 57s</sub>

### ℹ️ Info

Operation cancelled by user

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
