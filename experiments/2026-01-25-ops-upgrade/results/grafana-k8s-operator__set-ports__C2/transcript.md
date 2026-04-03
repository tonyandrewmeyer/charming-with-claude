# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `2afa9ad2-8e8a-453b-be9f-6c94432cb29e`  
> - **Started:** 4/3/2026, 7:06:20 AM  
> - **Duration:** 3m 9s  
> - **Exported:** 4/3/2026, 7:09:29 AM  

---

<sub>⏱️ 5s</sub>

### 👤 User

ops 2.7.0 added a declarative Unit.set_ports() API that replaces the imperative open_port()/close_port() pattern. Instead of tracking which ports to open and close individually, charms declare the full set of desired ports and ops handles the diff. Learn how to use that feature and update this charm to make use of it.

---

<sub>⏱️ 14s</sub>

### 📦 task (Completed)

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2

<details>
<summary>20 lines</summary>

```
.git
.github
.gitignore
.jujuignore
CODEOWNERS
CONTRIBUTING.md
LICENSE
README.md
RELEASE.md
SECURITY.md
charmcraft.yaml
icon.svg
lib
probes
pyproject.toml
src
terraform
tests
tox.ini
uv.lock
```

</details>


### ✅ `grep`

**/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2**

"open_port|close_port|open_ports|set_ports" (/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2)

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py:        self._set_ports()
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py:    def _set_ports(self):
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py:            self.unit.close_port(p.protocol, p.port)
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py:            self.unit.open_port(p.protocol, p.port)
```


### ✅ `glob`

**/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2**

"**/pyproject.toml" in /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/pyproject.toml
```


### ✅ `glob`

**/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2**

"**/charmcraft.yaml" in /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/charmcraft.yaml
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/grafana-tester/charmcraft.yaml
```


### ✅ `glob`

**/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2**

"**/requirements*.txt" in /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/grafana-tester/requirements.txt
```


### 💬 Copilot

Good start! Now let me get the key files and search for more port-related code:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/pyproject.toml.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/pyproject.toml

<details>
<summary>100 lines</summary>

```
1. # Copyright 2021 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. [project]
4. name = "grafana-k8s"
5. version = "0.0"
6. requires-python = "~=3.8"
7. 
8. dependencies = [
9.   "ops>=2.17",
10.   "ops[tracing]",
11.   "pyyaml",
12.   "urllib3",
13.   "jsonschema",
14.   "cryptography",
15.   "jinja2<3",
16.   "markupsafe==2.0.1", # https://github.com/pallets/markupsafe/issues/371
17.   "lightkube>=0.11",
18.   # lib/charms/grafana_k8s/v0/grafana_dashboard.py
19.   # lib/charms/tempo_k8s/v1/charm_tracing.py
20.   "cosl",
21.   # lib/charms/istio_beacon_k8s/v0/service_mesh.py
22.   "charmed-service-mesh-helpers>=0.2.0",
23.   "lightkube-extensions",
24.   "pydantic[email]>=2.10.6",
25. ]
26. 
27. [project.optional-dependencies]
28. dev = [
29.   # Linting
30.   "ruff",
31.   "codespell",
32.   # Static
33.   "pyright",
34.   # Unit
35.   "pytest",
36.   "coverage[toml]",
37.   "responses",
38.   "cosl",
39.   "pydantic",
40.   # Integration
41.   "juju<=3.3.0,>=3.0",
42.   "websockets<14.0",
43.   "lightkube",
44.   "minio",
45.   "oauth-tools",
46.   "pytest-operator>=0.39",
47.   "ops[testing]",
48.   "pytest-asyncio",
49.   "pytest-playwright",
50.   "aiohttp!=3.11.13",  # Yanked
51.   "asyncstdlib",
52.   "sh",
53.   "tenacity",
54.   "jubilant",
55. ]
56. 
57. # Testing tools configuration
58. [tool.coverage.run]
59. branch = true
60. 
61. [tool.coverage.report]
62. show_missing = true
63. 
64. # Formatting tools configuration
65. [tool.black]
66. line-length = 99
67. target-version = ["py38"]
68. 
69. # Linting tools configuration
70. [tool.ruff]
71. line-length = 99
72. extend-exclude = ["__pycache__", "*.egg_info"]
73. 
74. [tool.ruff.lint]
75. select = ["E", "W", "F", "C", "N", "R", "D"]
76. # Ignore E501 because using black creates errors with this
77. # Ignore D107 Missing docstring in __init__
78. ignore = ["W505", "E501", "D107", "C901", "N818", "RET504"]
79. # D100, D101, D102, D103: Ignore missing docstrings in tests
80. per-file-ignores = {"tests/*" = ["D100","D101","D102","D103"]}
81. 
82. [tool.ruff.lint.pydocstyle]
83. convention = "google"
84. 
85. [tool.pyright]
86. extraPaths = ["lib"]
87. pythonVersion = "3.8"
88. pythonPlatform = "All"
89. 
90. [tool.pytest.ini_options]
91. asyncio_mode = "auto"
92. addopts = "--tb=native --verbose --capture=no --log-cli-level=INFO"
93. 
94. [tool.codespell]
95. skip = ".git,.tox,build,venv*"
96. ignore-words-list = "assertIn"
97. 
98. [tool.uv.sources]
99. oauth-tools = { git = "https://github.com/canonical/iam-bundle", rev = "oauth_tools-v0.1.2" }
100.
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/charmcraft.yaml.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/charmcraft.yaml

<details>
<summary>267 lines</summary>

```
1. # Copyright 2021 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. type: charm
5. name: grafana-k8s
6. summary: Data visualization and observability with Grafana
7. description: |
8.   Grafana provides dashboards for monitoring data and this
9.   charm is written to allow for HA on Kubernetes and can take
10.   multiple data sources (for example, Prometheus).
11. 
12. links:
13.   documentation: https://discourse.charmhub.io/t/grafana-operator-k8s-docs-index/5612
14.   website:
15.     - https://charmhub.io/grafana-k8s
16.   source:
17.     - https://github.com/canonical/grafana-k8s-operator
18.   issues:
19.     - https://github.com/canonical/grafana-k8s-operator/issues
20. 
21. assumes:
22.   - k8s-api
23.   - juju >= 3.6
24. 
25. containers:
26.   grafana:
27.     resource: grafana-image
28.     mounts:
29.       - storage: database
30.         location: /var/lib/grafana
31. 
32. storage:
33.   database:
34.     type: filesystem
35. 
36. requires:
37.   grafana-source:
38.     interface: grafana_datasource
39.     optional: true
40.   grafana-dashboard:
41.     interface: grafana_dashboard
42.     optional: true
43.   grafana-auth:
44.     interface: grafana_auth
45.     optional: true
46.   pgsql:
47.     interface: postgresql_client
48.     limit: 1
49.     optional: true
50.     description: |
51.       This endpoint allows using a PostgreSQL database backend for data storage.
52.       Using this endpoint overrides Grafana's usage of the embedded sqlite3 database
53.       for data storage and is required for more than one Grafana unit.
54.   catalogue:
55.     interface: catalogue
56.     optional: true
57.   ingress:
58.     interface: ingress
59.     limit: 1
60.     optional: true
61.   certificates:
62.     interface: tls-certificates
63.     limit: 1
64.     optional: true
65.     description: Certificate and key files for Grafana to use with TLS.
66.   receive-ca-cert:
67.     interface: certificate_transfer
68.     optional: true
69.     description: |
70.       Receive a CA cert for grafana to trust.
71.       This relation can be used with a local CA to obtain the CA cert that was used to sign proxied
72.       endpoints.
73.   oauth:
74.     interface: oauth
75.     limit: 1
76.     optional: true
77.     description: |
78.       Receive oauth server's info and a set of client credentials.
79.       This relation can be used to integrate grafana with an oAuth2/OIDC Provider.
80.   charm-tracing:
81.     description: |
82.       Enables sending charm traces to a distributed tracing backend such as Tempo.
83.     limit: 1
84.     optional: true
85.     interface: tracing
86.   workload-tracing:
87.     description: |
88.       Enables sending workload traces to a distributed tracing backend such as Tempo.
89.     limit: 1
90.     optional: true
91.     interface: tracing
92.   service-mesh:
93.     limit: 1
94.     interface: service_mesh
95.     description: |
96.       Subscribe this charm to a service mesh and create authorization policies.
97.   require-cmr-mesh:
98.     interface: cross_model_mesh
99.     description: |
100.       Allow a cross-model application access to this charm via the service mesh.
101.       This relation provides additional data required by the service mesh to enforce cross-model authorization policies.
102. 
103. provides:
104.   profiling-endpoint:
105.     interface: parca_scrape
106.     optional: true
107.     description: |
108.       Links to grafana's pprof endpoint. Can be used to integrate with parca to 
109.       profile the grafana server process.
110.   metrics-endpoint:
111.     interface: prometheus_scrape
112.     optional: true
113.     description: Links to grafana's own `/metrics` endpoint.
114.   grafana-metadata:
115.     interface: grafana_metadata
116.     optional: true
117.     description: |
118.       Provides metadata about the grafana instance, such as its URL and ID.
119.   provide-cmr-mesh:
120.     interface: cross_model_mesh
121.     description: |
122.       Access a cross-model application from this charm via the service mesh.
123.       This relation provides additional data required by the service mesh to enforce cross-model authorization policies.
124. 
125. peers:
126.   grafana:
127.     interface: grafana_peers
128.   replicas:
129.     # Peer relation used as storage for TLS data
130.     interface: grafana_replicas
131. 
132. resources:
133.   grafana-image:
134.     type: oci-image
135.     description: upstream docker image for Grafana
136.     upstream-source: docker.io/ubuntu/grafana@sha256:d2f26ddd1e0263cd84291375f9a2309dbc08abbd465e0554a5b678824a5f207a  # renovate: oci-image tag: 12.0-24.04
137. 
138. platforms:
139.   ubuntu@24.04:amd64:
140. 
141. parts:
142.   charm:
143.     source: .
144.     plugin: uv
145.     build-packages: [git]
146.     build-snaps: [astral-uv]
147.     override-build: |
148.       craftctl default
149.       git describe --always > $CRAFT_PART_INSTALL/version
150.   static-sqlite3:
151.     plugin: dump
152.     source: .
153.     build-packages:
154.       - curl
155.     override-pull: |
156.       curl -L https://github.com/CompuRoot/static-sqlite3/releases/latest/download/sqlite3 -o sqlite-static
157.       chmod +x sqlite-static
158.   cos-tool:
159.     plugin: dump
160.     source: .
161.     build-packages:
162.       - curl
163.     override-pull: |
164.       curl -L -O https://github.com/canonical/cos-tool/releases/latest/download/cos-tool-${CRAFT_ARCH_BUILD_FOR}
165.       chmod 775 cos-tool-*
166. 
167. actions:
168.   get-admin-password:
169.     description: |
170.       Get the dashboard url and initial admin password for the Grafana web interface. Initial
171.       admin password is generated at charm deployment time. If the password has been changed,
172.       a notice of that fact will be returned by this action instead.
173. 
174. config:
175.   options:
176.     allow_anonymous_access:
177.       type: boolean
178.       default: false
179.       description: |
180.         Whether Grafana should allow anonymous access to dashboards. Unless
181.         you have some other authentication mechanism in front of your deployment,
182.         you likely do not want to enable this.
183.     allow_embedding:
184.       type: boolean
185.       default: false
186.       description: |
187.         Whether Grafana should allow embedding dashboards using iframes. Unless
188.         you have a clear reason for doing so, you likely do not want to enable this.
189.     log_level:
190.       type: string
191.       description: |
192.         Logging level for Grafana. Options are “debug”, “info”,
193.         “warn”, “error”, and “critical”.
194.       default: info
195.     admin_user:
196.       description: The Grafana administrative user
197.       type: string
198.       default: admin
199.     web_external_url:
200.       description: |
201.         DEPRECATED. This config option is no longer used, in favor of "skipPrefix".
202. 
203.         The URL under which Grafana is externally reachable (for example,
204.         if Grafana is served via a reverse proxy).
205. 
206.         Used for generating relative and absolute links back to
207.         Grafana itself. If the URL has a path portion, it will be used to
208.         prefix all HTTP endpoints served by Grafana.
209. 
210.         If omitted, relevant URL components will be derived automatically.
211. 
212.         If provided, this should be a complete URI, including scheme, or a
213.         fully qualified subpath starting with `/`.
214. 
215.         If Grafana is being served directly from the root of a fully-qualified
216.         host or a bare A record, this may be omitted.
217.       type: string
218.       default: ""
219.     enable_auto_assign_org:
220.       description: |
221.         Set to true to automatically add new users to the main organization (id 1). When set to
222.         false, new users automatically cause a new organization to be created for that new user.
223.       type: boolean
224.       default: true
225.     datasource_query_timeout:
226.       description: |
227.         The default timeout for querying a Grafana datasource. Each datasource can
228.         also configure its own preferred timeout value through relation data. If the
229.         value configured through relation data is larger than datasource_query_timeout
230.         then that value is left unchanged. The value of this configuration option must
231.         be a positive integer representing the maximum number of seconds Grafana will
232.         wait for a datasource to respond to a query.
233.       type: int
234.       default: 300
235.     cpu:
236.       description: |
237.         K8s cpu resource limit, e.g. "1" or "500m". Default is unset (no limit). This value is used
238.         for the "limits" portion of the resource requirements (the "requests" portion is
239.         automatically deduced from it).
240.         See https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
241.       type: string
242.     memory:
243.       description: |
244.         K8s memory resource limit, e.g. "1Gi". Default is unset (no limit). This value is used
245.         for the "limits" portion of the resource requirements (the "requests" portion is
246.         automatically deduced from it).
247.         See https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
248.       type: string
249.     reporting_enabled:
250.       description: |
251.         When disabled, Grafana will be configured to not send anonymous usage statistics to stats.grafana.org, nor
252.         periodically check for updates.
253.         It is very helpful to the Grafana project, so please leave this enabled.
254.         
255.         When enabled, Grafana will use its default values for analytics.
256.         
257.         Ref: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#analytics
258.       type: boolean
259.       default: true
260.     custom_config:
261.       type: string
262.       description: |
263.         Additional configuration options to be added to grafana.ini.
264.         These options will be appended to the grafana.ini file, allowing for custom configuration.
265.         Note that this config option accepts only a small subset of the grafana.ini file.
266.         Currently supported sections:
267.         - [smtp], ref: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#smtp
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src

<details>
<summary>11 lines</summary>

```
charm.py
constants.py
custom_ini_config.py
grafana.py
grafana_client.py
grafana_config.py
models.py
prometheus_alert_rules
relation.py
secret_storage.py
self_dashboard.json
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py

```
File too large to read at once (26.6 KB). Consider using the grep tool to search within the file, or view with view_range to read specific sections.
```


### 💬 Copilot

Now let me get the specific port-related code from charm.py and search for more context:

### ✅ `bash`

**Search for all port-related lines in charm.py**

$ grep -n "port" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py | head -50

<details>
<summary>51 lines</summary>

```
20:import logging
21:import os
22:import socket
23:import subprocess
24:from pathlib import Path
25:from typing import Any, Dict, cast, Optional
26:from urllib.parse import urlparse
28:from cosl import JujuTopology
29:from cosl.reconciler import all_events, observe_events
30:from ops import ActiveStatus, BlockedStatus, CollectStatusEvent, RelationBrokenEvent, StatusBase, main
31:from ops.charm import (
36:from ops.model import Port
37:from secret_storage import SecretStorage
39:from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
40:from charms.certificate_transfer_interface.v1.certificate_transfer import (
43:from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
44:from charms.grafana_k8s.v0.grafana_auth import AuthRequirer, AuthRequirerCharmEvents
45:from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardConsumer
46:from charms.grafana_k8s.v0.grafana_metadata import GrafanaMetadataProvider
47:from charms.grafana_k8s.v0.grafana_source import (
50:from charms.hydra.v0.oauth import (
55:from charms.istio_beacon_k8s.v0.service_mesh import UnitPolicy, ServiceMeshConsumer
56:from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
61:from charms.parca_k8s.v0.parca_scrape import ProfilingEndpointProvider
62:from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
63:from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer
64:from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer, IngressPerAppReadyEvent, IngressPerAppRevokedEvent
65:from grafana import Grafana
66:from grafana_client import GrafanaClient, GrafanaCommError
67:from grafana_config import GrafanaConfig
68:from secret_storage import generate_password
69:from relation import Relation
70:from models import DatasourceConfig, PebbleEnvironment, TLSConfig
71:from charms.tls_certificates_interface.v4.tls_certificates import (
76:from constants import (
87:import ops_tracing
131:        self.ingress = IngressPerAppRequirer(self, port=WORKLOAD_PORT, scheme=self._scheme, strip_prefix=False)
139:                    ports=[WORKLOAD_PORT],
143:                    ports=[PROFILING_PORT],
209:                                            enable_reporting = bool(self.config["reporting_enabled"]),
428:        self._set_ports()
438:        self.ingress.provide_ingress_requirements(scheme=self._scheme, port=WORKLOAD_PORT)
648:    def _set_ports(self):
649:        """Open necessary (and close no longer needed) workload ports."""
650:        planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
651:        actual_ports = self.unit.opened_ports()
654:        ports_to_close = actual_ports.difference(planned_ports)
655:        for p in ports_to_close:
656:            self.unit.close_port(p.protocol, p.port)
658:        new_ports_to_open = planned_ports.difference(actual_ports)
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Show port management methods with context**

$ grep -n "_set_ports\|close_port\|open_port" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py -A 3 -B 1

<details>
<summary>22 lines</summary>

```
427-        """Unconditional control logic."""
428:        self._set_ports()
429-        self.unit.set_workload_version(self._grafana_service.grafana_version)
430-        if not self.resource_patch.is_ready():
431-            logger.debug("Resource patch not ready yet. Skipping cluster update step.")
--
647-
648:    def _set_ports(self):
649-        """Open necessary (and close no longer needed) workload ports."""
650-        planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
651-        actual_ports = self.unit.opened_ports()
--
655-        for p in ports_to_close:
656:            self.unit.close_port(p.protocol, p.port)
657-
658-        new_ports_to_open = planned_ports.difference(actual_ports)
659-        for p in new_ports_to_open:
660:            self.unit.open_port(p.protocol, p.port)
661-
662-    def _resource_reqs_from_config(self) -> ResourceRequirements:
663-        limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
<exited with exit code 0>
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py (lines 1-100)

<details>
<summary>100 lines</summary>

```
1. #! /usr/bin/env python3
2. # -*- coding: utf-8 -*-
3. #
4. #  Copyright 2021 Canonical Ltd.
5. #
6. #  Licensed under the Apache License, Version 2.0 (the "License");
7. #  you may not use this file except in compliance with the License.
8. #  You may obtain a copy of the License at
9. #
10. #      http://www.apache.org/licenses/LICENSE-2.0
11. #
12. #  Unless required by applicable law or agreed to in writing, software
13. #  distributed under the License is distributed on an "AS IS" BASIS,
14. #  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
15. #  See the License for the specific language governing permissions and
16. #  limitations under the License.
17. 
18. """A Kubernetes charm for Grafana."""
19. 
20. import logging
21. import os
22. import socket
23. import subprocess
24. from pathlib import Path
25. from typing import Any, Dict, cast, Optional
26. from urllib.parse import urlparse
27. 
28. from cosl import JujuTopology
29. from cosl.reconciler import all_events, observe_events
30. from ops import ActiveStatus, BlockedStatus, CollectStatusEvent, RelationBrokenEvent, StatusBase, main
31. from ops.charm import (
32.     ActionEvent,
33.     CharmBase,
34.     RelationChangedEvent,
35. )
36. from ops.model import Port
37. from secret_storage import SecretStorage
38. 
39. from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
40. from charms.certificate_transfer_interface.v1.certificate_transfer import (
41.     CertificateTransferRequires,
42. )
43. from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
44. from charms.grafana_k8s.v0.grafana_auth import AuthRequirer, AuthRequirerCharmEvents
45. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardConsumer
46. from charms.grafana_k8s.v0.grafana_metadata import GrafanaMetadataProvider
47. from charms.grafana_k8s.v0.grafana_source import (
48.     GrafanaSourceConsumer,
49. )
50. from charms.hydra.v0.oauth import (
51.     ClientConfig as OauthClientConfig,
52.     OAuthRequirer,
53.     OauthProviderConfig
54. )
55. from charms.istio_beacon_k8s.v0.service_mesh import UnitPolicy, ServiceMeshConsumer
56. from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
57.     KubernetesComputeResourcesPatch,
58.     ResourceRequirements,
59.     adjust_resource_requirements,
60. )
61. from charms.parca_k8s.v0.parca_scrape import ProfilingEndpointProvider
62. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
63. from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer
64. from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer, IngressPerAppReadyEvent, IngressPerAppRevokedEvent
65. from grafana import Grafana
66. from grafana_client import GrafanaClient, GrafanaCommError
67. from grafana_config import GrafanaConfig
68. from secret_storage import generate_password
69. from relation import Relation
70. from models import DatasourceConfig, PebbleEnvironment, TLSConfig
71. from charms.tls_certificates_interface.v4.tls_certificates import (
72.     CertificateRequestAttributes,
73.     TLSCertificatesRequiresV4,
74.     CertificateAvailableEvent,
75. )
76. from constants import (
77.     PEER_RELATION,
78.     WORKLOAD_PORT,
79.     OAUTH_SCOPES,
80.     CA_CERT_PATH,
81.     GRAFANA_WORKLOAD,
82.     PGSQL_RELATION,
83.     PROFILING_PORT,
84.     OAUTH_GRANT_TYPES,
85.     VALID_AUTHENTICATION_MODES,
86.     METRICS_PATH)
87. import ops_tracing
88. 
89. logger = logging.getLogger()
90. 
91. 
92. class GrafanaCharm(CharmBase):
93.     """Charm to run Grafana on Kubernetes.
94. 
95.     This charm allows for high-availability
96.     (as long as a non-sqlite database relation is present).
97. 
98.     Developers of this charm should be aware of the Grafana provisioning docs:
99.     https://grafana.com/docs/grafana/latest/administration/provisioning/
100.     """
```

</details>


### 💬 Copilot

Let me get more of the charm.py file to see the full _set_ports method and the constants:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py (lines 648-670)

<details>
<summary>22 lines</summary>

```
648.     def _set_ports(self):
649.         """Open necessary (and close no longer needed) workload ports."""
650.         planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
651.         actual_ports = self.unit.opened_ports()
652. 
653.         # Ports may change across an upgrade, so need to sync
654.         ports_to_close = actual_ports.difference(planned_ports)
655.         for p in ports_to_close:
656.             self.unit.close_port(p.protocol, p.port)
657. 
658.         new_ports_to_open = planned_ports.difference(actual_ports)
659.         for p in new_ports_to_open:
660.             self.unit.open_port(p.protocol, p.port)
661. 
662.     def _resource_reqs_from_config(self) -> ResourceRequirements:
663.         limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
664.         requests = {"cpu": "0.25", "memory": "200Mi"}
665.         return adjust_resource_requirements(limits, requests, adhere_to_requests=True)
666. 
667. if __name__ == "__main__":
668.     main(GrafanaCharm, use_juju_for_storage=True)
669.
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/constants.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/constants.py

<details>
<summary>29 lines</summary>

```
1. """Charm constants."""
2. 
3. REQUIRED_DATABASE_FIELDS = {
4.     "type",  # mysql, postgres or sqlite3 (sqlite3 doesn't work for HA)
5.     "host",  # in the form '<url_or_ip>:<port>', e.g. 127.0.0.1:3306
6.     "name",
7.     "user",
8.     "password",
9. }
10. PEER_RELATION = "grafana"
11. PGSQL_RELATION = "pgsql"
12. DATABASE_PATH = "/var/lib/grafana/grafana.db"
13. # https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/generic-oauth
14. OAUTH_SCOPES = "openid email offline_access"
15. OAUTH_GRANT_TYPES = ["authorization_code", "refresh_token"]
16. GRAFANA_WORKLOAD = "grafana"
17. VALID_AUTHENTICATION_MODES = {"proxy"}
18. CONFIG_PATH = "/etc/grafana/grafana-config.ini"
19. PROVISIONING_PATH = "/etc/grafana/provisioning"
20. DATASOURCES_PATH = "/etc/grafana/provisioning/datasources/datasources.yaml"
21. DASHBOARDS_DIR = f"{PROVISIONING_PATH}/dashboards"
22. GRAFANA_CRT_PATH = "/etc/grafana/grafana.crt"
23. GRAFANA_KEY_PATH = "/etc/grafana/grafana.key"
24. CA_CERT_PATH = "/usr/local/share/ca-certificates/cos-ca.crt"
25. TRUSTED_CA_CERT_PATH = "/usr/local/share/ca-certificates/trusted-ca-cert.crt"
26. PROFILING_PORT = 8080
27. WORKLOAD_PORT = 3000
28. METRICS_PATH = "/metrics"
29.
```

</details>


### ✅ `glob`

**/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests**

"**/*.py" in /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests

<details>
<summary>40 matches</summary>

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/scenario/test_admin_password.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_source_provider.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_source_consumer.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_grafana_metadata_lib.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_auth_proxy_provider.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_grafana_metadata_implementation.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_dashboard_consumer.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_custom_ini_config.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_config_reporting_enabled.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_oauth.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_charmed_dashboard.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_grafana_client.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_charm.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_dashboard_provider.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_dashboard_transform.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/helpers.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/conftest.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_auth_requirer.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_datasources.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_dashboard_collision.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_external_url.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_grafana_auth.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_grafana_oauth.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_kubectl_delete.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_trusted_certificates.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_multiple_units.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_grafana_dashboard.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_upgrade_charm.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/grafana-tester/src/charm.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_grafana_source.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_workload_tracing.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_get_password.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/helpers.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/workload.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/conftest.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_selfmonitoring_dashboard.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_resource_limits.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_ingress.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_external_url.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_tls_web.py
```

</details>


### 💬 Copilot

Now let me search for port-related tests and check if there are any other port management patterns:

### ✅ `bash`

**Search for port-related code in charm unit tests**

$ grep -r "port\|Port" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_charm.py | head -30

<details>
<summary>9 lines</summary>

```
from dataclasses import replace
import json
from unittest.mock import patch
from pytest import mark
import yaml
from ops.testing import (Relation,
import src.grafana_client as grafana_client
from src.constants import CONFIG_PATH, DATASOURCES_PATH, PROVISIONING_PATH
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Search for port management methods in tests**

$ grep -r "opened_ports\|close_port\|open_port\|set_ports" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests --include="*.py"

```

<exited with exit code 1>
```


### ✅ `bash`

**Show all port references in charm.py**

$ grep -n "Port\|port" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py | head -40

<details>
<summary>41 lines</summary>

```
20:import logging
21:import os
22:import socket
23:import subprocess
24:from pathlib import Path
25:from typing import Any, Dict, cast, Optional
26:from urllib.parse import urlparse
28:from cosl import JujuTopology
29:from cosl.reconciler import all_events, observe_events
30:from ops import ActiveStatus, BlockedStatus, CollectStatusEvent, RelationBrokenEvent, StatusBase, main
31:from ops.charm import (
36:from ops.model import Port
37:from secret_storage import SecretStorage
39:from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
40:from charms.certificate_transfer_interface.v1.certificate_transfer import (
43:from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
44:from charms.grafana_k8s.v0.grafana_auth import AuthRequirer, AuthRequirerCharmEvents
45:from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardConsumer
46:from charms.grafana_k8s.v0.grafana_metadata import GrafanaMetadataProvider
47:from charms.grafana_k8s.v0.grafana_source import (
50:from charms.hydra.v0.oauth import (
55:from charms.istio_beacon_k8s.v0.service_mesh import UnitPolicy, ServiceMeshConsumer
56:from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
61:from charms.parca_k8s.v0.parca_scrape import ProfilingEndpointProvider
62:from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
63:from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer
64:from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer, IngressPerAppReadyEvent, IngressPerAppRevokedEvent
65:from grafana import Grafana
66:from grafana_client import GrafanaClient, GrafanaCommError
67:from grafana_config import GrafanaConfig
68:from secret_storage import generate_password
69:from relation import Relation
70:from models import DatasourceConfig, PebbleEnvironment, TLSConfig
71:from charms.tls_certificates_interface.v4.tls_certificates import (
76:from constants import (
87:import ops_tracing
131:        self.ingress = IngressPerAppRequirer(self, port=WORKLOAD_PORT, scheme=self._scheme, strip_prefix=False)
139:                    ports=[WORKLOAD_PORT],
143:                    ports=[PROFILING_PORT],
209:                                            enable_reporting = bool(self.config["reporting_enabled"]),
<exited with exit code 0>
```

</details>


### 💬 Copilot

Let me search more specifically in the tests and get the full initialization context:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py (lines 100-200)

<details>
<summary>101 lines</summary>

```
100.     """
101. 
102.     def __init__(self, *args):
103.         super().__init__(*args)
104. 
105.         # -- initialize states --
106.         self._topology = JujuTopology.from_charm(self)
107.         self._fqdn = socket.getfqdn()
108.         self.peers = Relation(app=self.app, relation=self.model.get_relation(PEER_RELATION))
109.         self._secret_storage = SecretStorage(self, "admin-password",
110.                                              default=lambda: {"password": generate_password()})
111. 
112. 
113.         # -- certificates
114.         self._csr_attributes = CertificateRequestAttributes(
115.             # the `common_name` field is required but limited to 64 characters.
116.             # since it's overridden by sans, we can use a short,
117.             # constrained value like app name.
118.             common_name=self.app.name,
119.             sans_dns=frozenset((self._fqdn,)),
120.         )
121.         self._cert_requirer = TLSCertificatesRequiresV4(
122.             charm=self,
123.             relationship_name="certificates",
124.             certificate_requests=[self._csr_attributes],
125.         )
126. 
127.         # -- trusted_cert_transfer
128.         self.trusted_cert_transfer = CertificateTransferRequires(self, "receive-ca-cert")
129. 
130.         # -- ingress
131.         self.ingress = IngressPerAppRequirer(self, port=WORKLOAD_PORT, scheme=self._scheme, strip_prefix=False)
132. 
133.         # -- service mesh
134.         self.mesh = ServiceMeshConsumer(
135.             self,
136.             policies=[
137.                 UnitPolicy(
138.                     relation="metrics-endpoint",
139.                     ports=[WORKLOAD_PORT],
140.                 ),
141.                 UnitPolicy(
142.                     relation="profiling-endpoint",
143.                     ports=[PROFILING_PORT],
144.                 ),
145.             ],
146.         )
147. 
148. 
149.         self.metrics_endpoint = MetricsEndpointProvider(
150.             charm=self,
151.             jobs=self._metrics_scrape_jobs,
152.             refresh_event=[
153.                 self.on.grafana_pebble_ready,  # pyright: ignore
154.                 self.on.update_status,
155.             ],
156.         )
157.         self.charm_tracing = TracingEndpointRequirer(
158.             self, relation_name="charm-tracing", protocols=["otlp_http"]
159.         )
160.         self.workload_tracing = TracingEndpointRequirer(
161.             self, relation_name="workload-tracing", protocols=["otlp_grpc"]
162.         )
163. 
164.         self.profiling = ProfilingEndpointProvider(self, jobs=self._profiling_scrape_jobs)
165. 
166.         # -- grafana_source relation observations
167.         self.source_consumer = GrafanaSourceConsumer(
168.             self,
169.             grafana_uid=self.unique_name,
170.             grafana_base_url=self.external_url,
171.             relation_name="grafana-source",
172.         )
173. 
174.         # -- grafana_dashboard relation observations
175.         self.dashboard_consumer = GrafanaDashboardConsumer(self, "grafana-dashboard")
176. 
177. 
178.         # -- k8s resource patch
179.         self.resource_patch = KubernetesComputeResourcesPatch(
180.             self, GRAFANA_WORKLOAD, resource_reqs_func=self._resource_reqs_from_config
181.         )
182. 
183.         # oauth relation
184.         self.oauth = OAuthRequirer(self, self._oauth_client_config)
185.         self.catalog = CatalogueConsumer(charm=self, item=self._catalogue_item)
186.         self.grafana_auth_requirer = AuthRequirer(
187.             self,
188.             relation_name="grafana-auth",
189.             urls=[f"{self.app.name}:{WORKLOAD_PORT}"],
190.             refresh_event=self.on.grafana_pebble_ready,  # pyright: ignore
191.         )
192. 
193.         # -- database relation
194.         self._db_name = f"{self._topology.application}-grafana-k8s-{self._topology.model_uuid}"
195.         self._db = None
196.         self._db_type = "sqlite3"
197. 
198.         if self.model.relations[PGSQL_RELATION]:
199.             self._db = DatabaseRequires(self, relation_name=PGSQL_RELATION, database_name=self._db_name)
200.             self._db_type = "postgres"
```

</details>


### ✅ `bash`

**Find all uses of port constants**

$ grep -n "WORKLOAD_PORT\|PROFILING_PORT" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py

<details>
<summary>11 lines</summary>

```
78:    WORKLOAD_PORT,
83:    PROFILING_PORT,
131:        self.ingress = IngressPerAppRequirer(self, port=WORKLOAD_PORT, scheme=self._scheme, strip_prefix=False)
139:                    ports=[WORKLOAD_PORT],
143:                    ports=[PROFILING_PORT],
189:            urls=[f"{self.app.name}:{WORKLOAD_PORT}"],
268:        return f"{self._scheme}://{self._fqdn}:{WORKLOAD_PORT}"
287:        job = {"static_configs": [{"targets": [f"*:{PROFILING_PORT}"]}], "scheme": self._scheme}
438:        self.ingress.provide_ingress_requirements(scheme=self._scheme, port=WORKLOAD_PORT)
650:        planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Find test files that reference ports**

$ find /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests -name "*.py" -type f | xargs grep -l "port\|Port" | head -10

<details>
<summary>11 lines</summary>

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_tls_web.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_external_url.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_ingress.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_resource_limits.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_selfmonitoring_dashboard.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/conftest.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/workload.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/helpers.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_get_password.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/test_workload_tracing.py
<exited with exit code 0>
```

</details>


### 💬 Copilot

Now let me check some of these test files and also look at the test_charm.py for any port-related tests:

### ✅ `bash`

**Check test_charm.py for port references**

$ grep -n "port\|Port" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_charm.py -i | head -50

<details>
<summary>9 lines</summary>

```
4:from dataclasses import replace
5:import json
6:from unittest.mock import patch
8:from pytest import mark
9:import yaml
10:from ops.testing import (Relation,
21:import src.grafana_client as grafana_client
22:from src.constants import CONFIG_PATH, DATASOURCES_PATH, PROVISIONING_PATH
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Check integration workload.py for port usage**

$ grep -n "port\|Port" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/workload.py

<details>
<summary>8 lines</summary>

```
4:from typing import Optional
6:import aiohttp
7:from tenacity import retry
8:from urllib3 import make_headers
18:        port: Optional[int] = 3000,
27:            port: Optional port on which Grafana service is exposed, defaults to `3000`
33:        self.base_uri = "http://{}:{}{}".format(host, port, path)
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Check integration helpers for port usage**

$ grep -n "port\|Port" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/helpers.py

<details>
<summary>14 lines</summary>

```
4:import json
5:import logging
6:from pathlib import Path
7:from typing import Optional, Tuple
9:import requests
10:import yaml
11:from asyncstdlib import functools
12:from pytest_operator.plugin import OpsTest
13:from urllib.parse import urlparse
14:from workload import Grafana
15:from juju.unit import Unit
16:from tenacity import retry, stop_after_attempt, wait_exponential, wait_fixed
325:        f"{p.hostname}:{p.port or 443}:{ip_addr}",
<exited with exit code 0>
```

</details>


### 💬 Copilot

Let me check the integration tests more carefully and look at the full workload.py file:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/workload.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/workload.py

<details>
<summary>152 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2021 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. from typing import Optional
5. 
6. import aiohttp
7. from tenacity import retry
8. from urllib3 import make_headers
9. 
10. 
11. class Grafana:
12.     """A class which abstracts access to a running instance of Grafana."""
13. 
14.     def __init__(
15.         self,
16.         *,
17.         host: Optional[str] = "localhost",
18.         port: Optional[int] = 3000,
19.         path: Optional[str] = "",
20.         username: Optional[str] = "admin",
21.         pw: Optional[str] = "",
22.     ):
23.         """Utility to manage a Grafana application.
24. 
25.         Args:
26.             host: Optional host address of Grafana application, defaults to `localhost`
27.             port: Optional port on which Grafana service is exposed, defaults to `3000`
28.             path: Optional path (e.g. due to ingress).
29.             username: Optional username to connect with, defaults to `admin`
30.             pw: Optional password to connect with, defaults to `""`
31.         """
32.         path = ("/" + path.lstrip("/")) if path else ""
33.         self.base_uri = "http://{}:{}{}".format(host, port, path)
34.         self.headers = make_headers(basic_auth="{}:{}".format(username, pw))
35. 
36.     async def is_ready(self) -> bool:
37.         """Send a request to check readiness.
38. 
39.         Returns:
40.           True if Grafana is ready (returned database information OK); False otherwise.
41.         """
42.         res = await self.health()
43.         return res.get("database", "") == "ok" or False
44. 
45.     async def settings(self) -> dict:
46.         """Send a request to get Grafana global settings.
47. 
48.         Returns:
49.           All the settings as a dict
50.         """
51.         api_path = "api/admin/settings"
52.         uri = "{}/{}".format(self.base_uri, api_path)
53.         async with aiohttp.ClientSession(headers=self.headers) as session:
54.             async with session.get(uri) as response:
55.                 result = await response.json()
56.                 return result if response.status == 200 else {}
57. 
58.     @retry
59.     async def health(self) -> dict:
60.         """A convenience method which queries the API to see whether Grafana is really ready.
61. 
62.         Returns:
63.             Empty :dict: if it is not up, otherwise a dict containing basic API health
64.         """
65.         api_path = "api/health"
66.         uri = "{}/{}".format(self.base_uri, api_path)
67. 
68.         async with aiohttp.ClientSession(headers=self.headers) as session:
69.             async with session.get(uri) as response:
70.                 result = await response.json()
71.                 if response.status == 200:
72.                     return result
73.                 raise Exception("Grafana is not ready")
74. 
75.     async def datasources(self) -> list:
76.         """Fetch datasources.
77. 
78.         Returns:
79.           Configured datasources, if any
80.         """
81.         api_path = "api/datasources"
82.         uri = "{}/{}".format(self.base_uri, api_path)
83.         async with aiohttp.ClientSession(headers=self.headers) as session:
84.             async with session.get(uri) as response:
85.                 result = await response.json()
86.                 return result if response.status == 200 else []
87. 
88.     async def dashboards_all(self) -> list:
89.         """Try to get 'all' dashboards, since relation dashboards are not starred.
90. 
91.         Returns:
92.           Found dashboards, if any
93.         """
94.         api_path = "api/search"
95.         uri = "{}/{}".format(self.base_uri, api_path)
96.         async with aiohttp.ClientSession(headers=self.headers) as session:
97.             async with session.get(uri, params={"starred": "false"}) as response:
98.                 result = await response.json()
99.                 return result if response.status == 200 else []
100. 
101.     async def dashboard_search(self, query_str: str) -> list:
102.         """Fetch dashboards matching a string.
103. 
104.         Returns:
105.           Found dashboards, if any
106.         """
107.         api_path = "api/search"
108.         uri = "{}/{}".format(self.base_uri, api_path)
109.         async with aiohttp.ClientSession(headers=self.headers) as session:
110.             async with session.get(uri, params={"query": query_str}) as response:
111.                 result = await response.json()
112.                 return result if response.status == 200 else []
113. 
114.     async def fetch_dashboard(self, dashboard_uid: str) -> dict:
115.         """Get the JSON representation of a complete dashboard.
116. 
117.         Returns:
118.           A dashboard.
119.         """
120.         api_path = "api/dashboards/uid/{}".format(dashboard_uid)
121.         uri = "{}/{}".format(self.base_uri, api_path)
122.         async with aiohttp.ClientSession(headers=self.headers) as session:
123.             async with session.get(uri) as response:
124.                 result = await response.json()
125.                 return result if response.status == 200 else {}
126. 
127.     async def fetch_org(self, name: str) -> dict:
128.         """Get the JSON representation of orgs.
129. 
130.         Returns:
131.           Organisation.
132.         """
133.         api_path = f"/api/orgs/name/{name}"
134.         uri = f"{self.base_uri}{api_path}"
135.         async with aiohttp.ClientSession(headers=self.headers) as session:
136.             async with session.get(uri) as response:
137.                 result = await response.json()
138.                 return result if response.status == 200 else {}
139. 
140.     async def create_org(self, name: str) -> dict:
141.         """Create org.
142. 
143.         Returns:
144.           Dict containing the orgId.
145.         """
146.         api_path = "/api/orgs"
147.         uri = f"{self.base_uri}{api_path}"
148.         async with aiohttp.ClientSession(headers=self.headers) as session:
149.             async with session.post(uri, json={"name": name}) as response:
150.                 result = await response.json()
151.                 return result if response.status == 200 else {}
152.
```

</details>


### ✅ `bash`

**Check beginning of helpers.py**

$ head -100 /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/helpers.py

<details>
<summary>80 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
import json
import logging
from pathlib import Path
from typing import Optional, Tuple

import requests
import yaml
from asyncstdlib import functools
from pytest_operator.plugin import OpsTest
from urllib.parse import urlparse
from workload import Grafana
from juju.unit import Unit
from tenacity import retry, stop_after_attempt, wait_exponential, wait_fixed

logger = logging.getLogger(__name__)


@functools.cache
async def grafana_password(ops_test: OpsTest, app_name: str) -> str:
    """Get the admin password . Memoize it to reduce turnaround time.

    Args:
        ops_test: pytest-operator plugin
        app_name: string name of application

    Returns:
        admin password as a string
    """
    leader: Optional[Unit] = None
    for unit in ops_test.model.applications[app_name].units:  # type: ignore
        is_leader = await unit.is_leader_from_status()
        if is_leader:
            leader = unit
            break

    assert leader
    action = await leader.run_action("get-admin-password")
    action = await action.wait()
    return action.results["admin-password"]


async def unit_address(ops_test: OpsTest, app_name: str, unit_num: int) -> str:
    """Find unit address for any application.

    Args:
        ops_test: pytest-operator plugin
        app_name: string name of application
        unit_num: integer number of a juju unit

    Returns:
        unit address as a string
    """
    assert ops_test.model
    status = await ops_test.model.get_status()
    return status["applications"][app_name]["units"]["{}/{}".format(app_name, unit_num)]["address"]


async def check_grafana_is_ready(ops_test: OpsTest, app_name: str, unit_num: int) -> bool:
    """Check if Grafana server is up with good database status.

    Args:
        ops_test: pytest-operator plugin
        app_name: string name of Grafana application
        unit_num: integer number of a Grafana juju unit

    Returns:
        True if Grafana is responsive else False
    """
    host = await unit_address(ops_test, app_name, unit_num)
    pw = await grafana_password(ops_test, app_name)
    grafana = Grafana(host=host, pw=pw)
    is_ready = await grafana.is_ready()
    assert is_ready
    return is_ready


async def create_org(ops_test: OpsTest, app_name: str, unit_num: int, org_name: str) -> dict:
    """Create Organisation.

    Args:
        ops_test: pytest-operator plugin
        app_name: string name of Grafana application
        unit_num: integer number of a Grafana juju unit
        org_name: string name of Org.

    Returns:
        Oranisation created.
    """
    host = await unit_address(ops_test, app_name, unit_num)
    pw = await grafana_password(ops_test, app_name)
    grafana = Grafana(host=host, pw=pw)
    org = await grafana.create_org(name=org_name)
    return org


async def get_org(ops_test: OpsTest, app_name: str, unit_num: int, org_name: str) -> dict:
    """Fetch Organisation.
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Get full context of port management methods**

$ grep -B 5 -A 10 "opened_ports\|open_port\|close_port\|set_ports" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py

<details>
<summary>38 lines</summary>

```
return None
        return contents.get('password')

    def _reconcile(self):
        """Unconditional control logic."""
        self._set_ports()
        self.unit.set_workload_version(self._grafana_service.grafana_version)
        if not self.resource_patch.is_ready():
            logger.debug("Resource patch not ready yet. Skipping cluster update step.")
            return
        if self.charm_tracing.is_ready() and (endpoint:= self.charm_tracing.get_endpoint("otlp_http")):
            ops_tracing.set_destination(
                url=endpoint + "/v1/traces",
                ca=self._tls_config.ca if self._tls_config else None
            )
        self.ingress.provide_ingress_requirements(scheme=self._scheme, port=WORKLOAD_PORT)
--
        env_vars[mode_enabled_var] = "True"
        for var in conf[auth_mode].keys():
            env_vars[auth_var_prefix + str(var).upper()] = str(conf[auth_mode][var])
        return env_vars

    def _set_ports(self):
        """Open necessary (and close no longer needed) workload ports."""
        planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
        actual_ports = self.unit.opened_ports()

        # Ports may change across an upgrade, so need to sync
        ports_to_close = actual_ports.difference(planned_ports)
        for p in ports_to_close:
            self.unit.close_port(p.protocol, p.port)

        new_ports_to_open = planned_ports.difference(actual_ports)
        for p in new_ports_to_open:
            self.unit.open_port(p.protocol, p.port)

    def _resource_reqs_from_config(self) -> ResourceRequirements:
        limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
        requests = {"cpu": "0.25", "memory": "200Mi"}
        return adjust_resource_requirements(limits, requests, adhere_to_requests=True)

if __name__ == "__main__":
    main(GrafanaCharm, use_juju_for_storage=True)
<exited with exit code 0>
```

</details>


### 💬 Copilot

Perfect! Now let me check the structure to ensure I have comprehensive information:

### ✅ `bash`

**Find all Python files that use Port class**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2 && find . -name "*.py" -type f -exec grep -l "Port\(" {} \; | head -20

<details>
<summary>66 lines</summary>

```
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
grep: Unmatched ( or \(
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Check what's imported from ops.model**

$ grep -A 5 "ops.model import" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py

<details>
<summary>6 lines</summary>

```
from ops.model import Port
from secret_storage import SecretStorage

from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
from charms.certificate_transfer_interface.v1.certificate_transfer import (
    CertificateTransferRequires,
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Get total lines in charm.py**

$ wc -l /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py

```
668 /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py
<exited with exit code 0>
```


### 💬 Copilot

Let me fix the grep pattern:

### ✅ `bash`

**Check imports from ops.model across the repo**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2 && grep -r "from ops.model import" --include="*.py" | head -5

<details>
<summary>6 lines</summary>

```
lib/charms/observability_libs/v0/kubernetes_compute_resources_patch.py:from ops.model import StatusBase
lib/charms/tempo_coordinator_k8s/v0/tracing.py:from ops.model import ModelError, Relation
lib/charms/hydra/v0/oauth.py:from ops.model import Relation, Secret, SecretNotFoundError, TooManyRelatedAppsError
lib/charms/data_platform_libs/v0/data_interfaces.py:from ops.model import Application, ModelError, Relation, Unit
lib/charms/grafana_k8s/v0/grafana_dashboard.py:from ops.model import Relation
<exited with exit code 0>
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py (lines 425-445)

<details>
<summary>21 lines</summary>

```
425. 
426.     def _reconcile(self):
427.         """Unconditional control logic."""
428.         self._set_ports()
429.         self.unit.set_workload_version(self._grafana_service.grafana_version)
430.         if not self.resource_patch.is_ready():
431.             logger.debug("Resource patch not ready yet. Skipping cluster update step.")
432.             return
433.         if self.charm_tracing.is_ready() and (endpoint:= self.charm_tracing.get_endpoint("otlp_http")):
434.             ops_tracing.set_destination(
435.                 url=endpoint + "/v1/traces",
436.                 ca=self._tls_config.ca if self._tls_config else None
437.             )
438.         self.ingress.provide_ingress_requirements(scheme=self._scheme, port=WORKLOAD_PORT)
439.         if self._check_wrong_relations():
440.             return
441.         self._reconcile_relations()
442.         self._grafana_service.reconcile()
443.         self._reconcile_tls_config()
444. 
445.     def _check_wrong_relations(self) -> Optional[StatusBase]:
```

</details>


### 💬 Copilot

Perfect! Now let me create a comprehensive summary. Let me also check if there's a changelog or any related documentation:

### ✅ `bash`

**Look for release notes**

$ ls -la /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/ | grep -i release

```
-rw-rw-r--  1 ubuntu ubuntu    1888 Mar 12 16:15 RELEASE.md
<exited with exit code 0>
```


### ✅ `bash`

**Check release notes**

$ head -50 /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/RELEASE.md

<details>
<summary>19 lines</summary>

```
# Release Process

## Overview

At any given time there are three revisions of the Grafana charm [available on CharmHub.io](https://charmhub.io/grafana-k8s), for each of the following channels:

1. `latest/stable` is a well tested production ready version of the Charm.
2. `latest/candidate` is a feature ready next version of the stable release, currently in testing.
3. `latest/edge` is the bleeding edge developer version of the charm. While we really try not to, it may break and introduce regressions.

Currently, the Grafana charm does not make use of the `latest/beta` channel.
For more information about CharmHub channels, refer to the [Juju charm store](https://discourse.charmhub.io/t/the-juju-charm-store) documentation.

## When to create which revisions

* **Stable revisions** are done in consultation with product manager and engineering manager when the `candidate` revision has been well tested and is deemed ready for production.
* **Candidate revisions** are done when the charm reaches a state of feature completion with respect to the next planned `stable` release.
* **Edge revisions** are released at the developers discretion, potentially every time something is merged into `main` and the unit tests pass.

## How to publish revisions

Refer to the [Publish your operator in Charmhub](https://discourse.charmhub.io/t/publish-your-operator-in-charmhub) documentation.
After a `latest/stable` release, it is expected that the version of the charm is the same as the one in `latest/candidate`, and those two channels will diverge again when we are ramping up through `latest/candidate` releases for a new `latest/stable` release.

## A note on granularity of revisions

We believe in shipping often and with confidence.
It is perfectly acceptable to have a new `latest/stable` release containing just one bug fix or a small new feature with respect to the last one.
<exited with exit code 0>
```

</details>


### 💬 Copilot

Excellent! Now I have all the information. Let me compile a comprehensive answer:

## Comprehensive Codebase Exploration: Grafana K8s Operator Charm

### 1. **Ops Framework Version**

**File: `/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/pyproject.toml`**

The charm requires **ops \>= 2.17**:
```python
dependencies = [
  "ops\>=2.17",
  "ops[tracing]",
  ...
]
```

This is specified in the pyproject.toml at line 9.

---

### 2. **Port Management - Complete Analysis**

#### **Port Constants Defined**
**File: `/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/constants.py`**

```python
PROFILING_PORT = 8080  # Line 26
WORKLOAD_PORT = 3000   # Line 27
```

#### **Port Management Method: `_set_ports()`**
**File: `/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py`** (Lines 648-660)

```python
def _set_ports(self):
    """Open necessary (and close no longer needed) workload ports."""
    planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
    actual_ports = self.unit.opened_ports()

    # Ports may change across an upgrade, so need to sync
    ports_to_close = actual_ports.difference(planned_ports)
    for p in ports_to_close:
        self.unit.close_port(p.protocol, p.port)

    new_ports_to_open = planned_ports.difference(actual_ports)
    for p in new_ports_to_open:
        self.unit.open_port(p.protocol, p.port)
```

**Key Details:**
- Uses **`ops.model.Port`** class (imported at line 36)
- Only the **leader unit** opens ports on Kubernetes
- Non-leader units have an empty set of planned ports
- Automatically syncs ports during upgrades
- Uses **`self.unit.open_port(protocol, port)`** to open ports
- Uses **`self.unit.close_port(protocol, port)`** to close ports
- Uses **`self.unit.opened_ports()`** to get current ports

#### **When Port Management is Called**
**File: `/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py`** (Line 428)

In the `_reconcile()` method:
```python
def _reconcile(self):
    """Unconditional control logic."""
    self._set_ports()  # Called on every reconciliation
    self.unit.set_workload_version(self._grafana_service.grafana_version)
    # ... rest of reconciliation
```

---

### 3. **Charm Structure Overview**

**File: `/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/`**

Directory structure:
```
src/
├── charm.py                    # Main charm class (668 lines)
├── constants.py               # Charm constants (29 lines)
├── custom_ini_config.py       # Grafana config handling
├── grafana.py                 # Grafana workload management
├── grafana_client.py          # Grafana API client
├── grafana_config.py          # Grafana configuration
├── models.py                  # Data models
├── prometheus_alert_rules/    # Alert rules
├── relation.py                # Relation handling
├── secret_storage.py          # Secret storage
└── self_dashboard.json        # Default dashboard
```

**Main Charm Class: `GrafanaCharm`**
**File: `/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py`** (Lines 92-668)

The `GrafanaCharm` class extends `CharmBase` and manages:
- **Container management** (Pebble): Grafana workload on Kubernetes
- **Multiple relations**: datasources, dashboards, auth, ingress, certificates, OAuth, service mesh, database, etc.
- **Event handling**: charm lifecycle events via `@observe_events` decorator
- **Port management** via `_set_ports()` method

#### **Port Usage Throughout Charm**

1. **Ingress Configuration (Line 131):**
   ```python
   self.ingress = IngressPerAppRequirer(self, port=WORKLOAD_PORT, scheme=self._scheme, strip_prefix=False)
   ```

2. **Service Mesh Policies (Lines 134-146):**
   ```python
   self.mesh = ServiceMeshConsumer(
       self,
       policies=[
           UnitPolicy(
               relation="metrics-endpoint",
               ports=[WORKLOAD_PORT],
           ),
           UnitPolicy(
               relation="profiling-endpoint",
               ports=[PROFILING_PORT],
           ),
       ],
   )
   ```

3. **Auth URLs (Line 189):**
   ```python
   urls=[f"{self.app.name}:{WORKLOAD_PORT}"]
   ```

4. **Metrics/Profiling Configuration (Lines 287):**
   ```python
   job = {"static_configs": [{"targets": [f"*:{PROFILING_PORT}"]}], "scheme": self._scheme}
   ```

5. **Ingress Requirements (Line 438):**
   ```python
   self.ingress.provide_ingress_requirements(scheme=self._scheme, port=WORKLOAD_PORT)
   ```

---

### 4. **Port Import Statement**

**File: `/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py`** (Line 36)

```python
from ops.model import Port
```

This imports the `Port` class used to create port specifications in the `_set_ports()` method.

---

### 5. **Integration Testing - Port Usage**

**File: `/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/integration/workload.py`** (Lines 14-33)

The test utility `Grafana` class defaults to port 3000 (the WORKLOAD_PORT):
```python
class Grafana:
    def __init__(
        self,
        *,
        host: Optional[str] = "localhost",
        port: Optional[int] = 3000,  # Default to WORKLOAD_PORT
        path: Optional[str] = "",
        username: Optional[str] = "admin",
        pw: Optional[str] = "",
    ):
        path = ("/" + path.lstrip("/")) if path else ""
        self.base_uri = "http://{}:{}{}".format(host, port, path)
```

---

### 6. **Configuration Files**

**charmcraft.yaml** specifies the charm container and storage:
```yaml
containers:
  grafana:
    resource: grafana-image
    mounts:
      - storage: database
        location: /var/lib/grafana

storage:
  database:
    type: filesystem
```

---

## Summary Table

| Aspect | Details |
|--------|---------|
| **Ops Version** | \>= 2.17 |
| **Workload Port** | 3000 (TCP) |
| **Profiling Port** | 8080 |
| **Port Management** | `_set_ports()` method |
| **Port Methods** | `unit.open_port()`, `unit.close_port()`, `unit.opened_ports()` |
| **Leader-Only** | Yes, only leader units open ports on K8s |
| **Port Class** | `ops.model.Port` |
| **Automatic Sync** | Yes, during upgrades and reconciliation |
| **Called Every** | Reconciliation cycle (line 428) |

All port-related code is centralized in the `_set_ports()` method, which follows best practices for managing ports on Kubernetes where only the leader unit should expose services.


---

<sub>⏱️ 24s</sub>

### ✅ `web_search`

**ops 2.7.0 Unit.set_ports() API declarative ports charm documentation**

<details>
<summary>Arguments</summary>

```json
{
  "query": "ops 2.7.0 Unit.set_ports() API declarative ports charm documentation"
}
```

</details>

````
{"type":"text","text":{"value":"The ops 2.7.0 framework introduced a declarative API for managing open ports on Juju charms, simplifying the way charms expose ports for both machine and Kubernetes workloads.\n\n### `Unit.set_ports()` API\n\n- **Purpose:** The `Unit.set_ports()` method is the recommended, declarative way to specify exactly which ports a charm unit should keep open.\n- **How it works:** You declare all required ports at once. Ports not included in the most recent call to `set_ports()` will be closed, ensuring the unit only has the correct set of ports open.\n- **Basic usage:**  \n  In your charm's event handler (e.g., for `config-changed`), you might do:\n  ```python\n  def _on_config_changed(self, event):\n      port = self.config['server-port']\n      self.unit.set_ports(port)\n  ```\n  This will ensure only the selected port is open (defaulting to TCP unless specified).\n\n- **Declarative example:**  \n  You can open multiple ports and protocols:\n  ```python\n  self.unit.set_ports(8000, 8080, ops.Port('udp', 5353))\n  ```\n  This call opens TCP 8000, TCP 8080, and UDP 5353; previously opened ports not listed will be closed.\n\n- **Why use declarative (`set_ports`) over imperative (`open_port`/`close_port`)?**  \n  - Simpler and less error-prone.\n  - Ensures only the currently desired ports are open, avoiding possible configuration drift.\n  - **Imperative methods** (`open_port`, `close_port`): Useful if you need to open/close ports in response to non-declarative state changes, but usually not necessary for new charms.\n\n- **Testing:**  \n  For unit and integration testing, the framework provides tools to assert the current open ports. Example checks might look like:\n  ```python\n  assert harness.model.unit.opened_ports() == {ops.Port('tcp', 8000)}\n  ```\n  In integration tests, you might also attempt actual network connections to verify reachability【3:3†Set the opened ports of a charm - doc - Charmhub†https://discourse.charmhub.io/t/set-the-opened-ports-of-a-charm/15570】【3:0†How to manage opened ports - Ops 2.x documentation†https://documentation.ubuntu.com/ops/2.x/howto/manage-opened-ports/】.\n\nYou can find more comprehensive reference and additional usage patterns in:\n- The official [Ops 2.x documentation on managing opened ports](https://documentation.ubuntu.com/ops/2.x/howto/manage-opened-ports/)【3:0†source】\n- A community guide on [exposing ports in charm code](https://discourse.charmhub.io/t/set-the-opened-ports-of-a-charm/15570)【3:3†source】\n\n**Summary:**  \nUse `Unit.set_ports()` in your charm event handlers to declaratively control which ports are open. This is especially useful in modern Ops 2.7+ charms and works well for both machine and Kubernetes charms, minimizing side effects or accidental port exposure. For new charm development, always prefer the declarative pattern.","annotations":[{"text":"【3:3†Set the opened ports of a charm - doc - Charmhub†https://discourse.charmhub.io/t/set-the-opened-ports-of-a-charm/15570】","start_index":1840,"end_index":1964,"url_citation":{"title":"Set the opened ports of a charm - doc - Charmhub","url":"https://discourse.charmhub.io/t/set-the-opened-ports-of-a-charm/15570"}},{"text":"【3:0†How to manage opened ports - Ops 2.x documentation†https://documentation.ubuntu.com/ops/2.x/howto/manage-opened-ports/】","start_index":1964,"end_index":2088,"url_citation":{"title":"How to manage opened ports - Ops 2.x documentation","url":"https://documentation.ubuntu.com/ops/2.x/howto/manage-opened-ports/"}},{"text":"【3:0†source】","start_index":2299,"end_index":2311,"url_citation":{"title":"How to manage opened ports - Ops 2.x documentation","url":"https://documentation.ubuntu.com/ops/2.x/howto/manage-opened-ports/"}},{"text":"【3:3†source】","start_index":2436,"end_index":2448,"url_citation":{"title":"Set the opened ports of a charm - doc - Charmhub","url":"https://discourse.charmhub.io/t/set-the-opened-ports-of-a-charm/15570"}}]},"bing_searches":[{"text":"ops 2.7.0 Unit.set_ports() API declarative ports charm documentation","url":"https://www.bing.com/search?q=ops+2.7.0+Unit.set_ports%28%29+API+declarative+ports+charm+documentation"}],"annotations":null}
````


---

<sub>⏱️ 1m 42s</sub>

### 💬 Copilot

Now I have a clear picture. The current `_set_ports()` method manually diffs open/closed ports using `open_port()`/`close_port()`. I need to replace it with `Unit.set_ports()`.

---

<sub>⏱️ 1m 42s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py (lines 30-45)

<details>
<summary>16 lines</summary>

```
30. from ops import ActiveStatus, BlockedStatus, CollectStatusEvent, RelationBrokenEvent, StatusBase, main
31. from ops.charm import (
32.     ActionEvent,
33.     CharmBase,
34.     RelationChangedEvent,
35. )
36. from ops.model import Port
37. from secret_storage import SecretStorage
38. 
39. from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
40. from charms.certificate_transfer_interface.v1.certificate_transfer import (
41.     CertificateTransferRequires,
42. )
43. from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
44. from charms.grafana_k8s.v0.grafana_auth import AuthRequirer, AuthRequirerCharmEvents
45. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardConsumer
```

</details>


---

<sub>⏱️ 1m 42s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py (lines 645-668)

<details>
<summary>24 lines</summary>

```
645.             env_vars[auth_var_prefix + str(var).upper()] = str(conf[auth_mode][var])
646.         return env_vars
647. 
648.     def _set_ports(self):
649.         """Open necessary (and close no longer needed) workload ports."""
650.         planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
651.         actual_ports = self.unit.opened_ports()
652. 
653.         # Ports may change across an upgrade, so need to sync
654.         ports_to_close = actual_ports.difference(planned_ports)
655.         for p in ports_to_close:
656.             self.unit.close_port(p.protocol, p.port)
657. 
658.         new_ports_to_open = planned_ports.difference(actual_ports)
659.         for p in new_ports_to_open:
660.             self.unit.open_port(p.protocol, p.port)
661. 
662.     def _resource_reqs_from_config(self) -> ResourceRequirements:
663.         limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
664.         requests = {"cpu": "0.25", "memory": "200Mi"}
665.         return adjust_resource_requirements(limits, requests, adhere_to_requests=True)
666. 
667. if __name__ == "__main__":
668.     main(GrafanaCharm, use_juju_for_storage=True)
```

</details>


---

<sub>⏱️ 1m 42s</sub>

### ✅ `grep`

**/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests**

"open_port|close_port|set_ports|opened_ports" in **/*.py (/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests)

```
No matches found.
```


---

<sub>⏱️ 2m 0s</sub>

### ✅ `grep`

**/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py**

"Port" (/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py)

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py:36:from ops.model import Port
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py:650:        planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py:653:        # Ports may change across an upgrade, so need to sync
```


---

<sub>⏱️ 2m 7s</sub>

### 💬 Copilot

`Port` is only used in `_set_ports()`. With `set_ports()`, I can pass the port number directly (defaults to TCP), so the import can be removed too.

---

<sub>⏱️ 2m 7s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 2m 7s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 2m 11s</sub>

### 💬 Copilot

Now let's verify the changes and run the tests:

---

<sub>⏱️ 2m 11s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py (lines 30-40)

<details>
<summary>11 lines</summary>

```
30. from ops import ActiveStatus, BlockedStatus, CollectStatusEvent, RelationBrokenEvent, StatusBase, main
31. from ops.charm import (
32.     ActionEvent,
33.     CharmBase,
34.     RelationChangedEvent,
35. )
36. from secret_storage import SecretStorage
37. 
38. from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
39. from charms.certificate_transfer_interface.v1.certificate_transfer import (
40.     CertificateTransferRequires,
```

</details>


---

<sub>⏱️ 2m 11s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/src/charm.py (lines 645-660)

<details>
<summary>16 lines</summary>

```
645.         return env_vars
646. 
647.     def _set_ports(self):
648.         """Open necessary (and close no longer needed) workload ports."""
649.         if self.unit.is_leader():
650.             self.unit.set_ports(WORKLOAD_PORT)
651.         else:
652.             self.unit.set_ports()
653. 
654.     def _resource_reqs_from_config(self) -> ResourceRequirements:
655.         limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
656.         requests = {"cpu": "0.25", "memory": "200Mi"}
657.         return adjust_resource_requirements(limits, requests, adhere_to_requests=True)
658. 
659. if __name__ == "__main__":
660.     main(GrafanaCharm, use_juju_for_storage=True)
```

</details>


---

<sub>⏱️ 2m 16s</sub>

### 💬 Copilot

Good. Now let's run the unit tests:

---

<sub>⏱️ 2m 17s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2 && python -m pytest tests/unit/ -x -q 2>&1 | tail -30

```
bash: python: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 2m 21s</sub>

### ✅ `bash`

**Run unit tests with python3**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2 && python3 -m pytest tests/unit/ -x -q 2>&1 | tail -40

```
ImportError while loading conftest '/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/conftest.py'.
tests/unit/conftest.py:9: in <module>
    from charm import GrafanaCharm
E   ModuleNotFoundError: No module named 'charm'
<exited with exit code 0>
```


---

<sub>⏱️ 2m 26s</sub>

### ✅ `bash`

**Check tox configuration for unit tests**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2 && cat tox.ini | grep -A5 "unit"

<details>
<summary>20 lines</summary>

```
envlist = lint, static, unit

[vars]
src_path = {toxinidir}/src
tst_path = {toxinidir}/tests
lib_path = {toxinidir}/lib/charms/grafana_k8s
--
[testenv:unit]
description = Run unit tests
allowlist_externals =
  {[testenv]allowlist_externals}
  /usr/bin/env
commands =
    /usr/bin/env sh -c 'stat sqlite-static > /dev/null 2>&1 || curl -L https://github.com/CompuRoot/static-sqlite3/releases/latest/download/sqlite3 -o sqlite-static && chmod +x sqlite-static'
--
        {[vars]tst_path}/unit {posargs}
    uv run {[vars]uv_flags} coverage report

[testenv:integration]
description = Run integration tests
commands =
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 47s</sub>

### ✅ `bash`

**Run unit tests via tox**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2 && tox -e unit 2>&1 | tail -40

<details>
<summary>37 lines</summary>

```
self.harness = Harness(MimirProviderCharm, meta=CONSUMER_META)

tests/unit/test_source_provider.py::TestSourceProviderWithIngress::test_provider_unit_sets_scheme_if_not_provided
tests/unit/test_source_provider.py::TestSourceProviderWithIngress::test_provider_unit_sets_source_uri_if_provided
  /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_source_provider.py:154: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(ProviderCharmWithIngress, meta=CONSUMER_META)

tests/unit/test_source_provider.py::TestFollowerSourceProvider::test_ingressed_shares_uri
tests/unit/test_source_provider.py::TestFollowerSourceProvider::test_not_ingressed_does_not_share_uri
  /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_source_provider.py:188: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(ProviderCharmWithIngress, meta=CONSUMER_META)

tests/unit/test_source_provider.py::TestDashboardProviderNoRefreshEvent::test_provider_instantiates_correctly
  /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2/tests/unit/test_source_provider.py:239: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(ProviderCharmNoRefreshEvent, meta=CONSUMER_META)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 122 passed, 1 skipped, 112 warnings in 4.23s =================
unit: commands[3]> uv run --frozen --isolated --extra=dev coverage report
warning: The `requires-python` specifier (`~=3.8`) in `grafana-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 119 packages in 47ms
Name                                             Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------------------
lib/charms/grafana_k8s/v0/grafana_auth.py          149     19     40      8    86%   246-248, 252, 259-260, 331, 333, 351, 367, 473-474, 493, 570, 572, 574, 576, 589-590
lib/charms/grafana_k8s/v0/grafana_dashboard.py     701    254    288     39    59%   399-402, 414-423, 435-442, 470-487, 522, 528, 534, 539-543, 571->570, 618->641, 629->628, 646->642, 685, 689-693, 704, 710-728, 838, 842, 844-850, 872, 932->935, 960-963, 971-972, 1019-1021, 1023, 1077-1080, 1084, 1092-1094, 1171-1172, 1228->exit, 1230, 1243->exit, 1249-1251, 1255, 1266->exit, 1283->exit, 1308->1307, 1314->exit, 1325->exit, 1335-1346, 1373, 1451, 1467->1470, 1470->exit, 1475-1477, 1504-1507, 1527-1532, 1565-1566, 1587-1616, 1635, 1641-1645, 1709-1712, 1718-1719, 1776-1801, 1808-1809, 1813-1830, 1835-1842, 1846-1863, 1885-1920, 1924-1993, 2003-2029, 2032, 2053, 2057-2058, 2063-2082, 2086-2116, 2121, 2123-2124, 2141-2143, 2152-2154
lib/charms/grafana_k8s/v0/grafana_metadata.py       46      1      8      1    96%   162
lib/charms/grafana_k8s/v0/grafana_source.py        306     45    112     16    83%   183-187, 194-197, 209-218, 230-237, 262, 268, 274, 279-283, 393-394, 405->408, 440-445, 455, 617, 638-641, 683, 686, 724->727, 727->exit, 765, 770->exit, 797-803, 816-817
src/charm.py                                       289     51     68     17    77%   293, 330-331, 408, 430-431, 433, 439, 448, 457-461, 464-465, 501, 513, 528, 544-551, 563-604, 618, 619->exit, 621->exit, 637-638, 655-657, 660
src/constants.py                                    19      0      0      0   100%
src/custom_ini_config.py                            48      0      8      1    98%   79->78
src/grafana.py                                     213     48     70     16    75%   92-100, 147, 179, 188, 257->exit, 282, 300-304, 329-339, 342-343, 353-362, 365-367, 409->exit, 415->exit, 426, 432-438, 442, 467-471, 484-485, 507->exit, 509-510, 521-522
src/grafana_client.py                               35      9      2      0    76%   73-74, 89-99
src/grafana_config.py                              105     16     20      3    85%   62-64, 71-76, 114, 160-175
src/models.py                                       23      0      0      0   100%
src/relation.py                                     20      0      6      1    96%   24->exit
src/secret_storage.py                               37      4      4      0    90%   49-52
--------------------------------------------------------------------------------------------
TOTAL                                             1991    447    626    102    74%
  unit: OK (17.33=setup[0.11]+cmd[1.92,5.75,9.19,0.36] seconds)
  congratulations :) (17.35 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 53s</sub>

### 💬 Copilot

All 122 tests pass. Let me commit the changes:

---

<sub>⏱️ 2m 53s</sub>

### ✅ `bash`

**Show diff of changes**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2 && git --no-pager diff

<details>
<summary>32 lines</summary>

```diff
diff --git a/src/charm.py b/src/charm.py
index 71972f3..4d4d04c 100755
--- a/src/charm.py
+++ b/src/charm.py
@@ -33,7 +33,6 @@ from ops.charm import (
     CharmBase,
     RelationChangedEvent,
 )
-from ops.model import Port
 from secret_storage import SecretStorage
 
 from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
@@ -647,17 +646,10 @@ class GrafanaCharm(CharmBase):
 
     def _set_ports(self):
         """Open necessary (and close no longer needed) workload ports."""
-        planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
-        actual_ports = self.unit.opened_ports()
-
-        # Ports may change across an upgrade, so need to sync
-        ports_to_close = actual_ports.difference(planned_ports)
-        for p in ports_to_close:
-            self.unit.close_port(p.protocol, p.port)
-
-        new_ports_to_open = planned_ports.difference(actual_ports)
-        for p in new_ports_to_open:
-            self.unit.open_port(p.protocol, p.port)
+        if self.unit.is_leader():
+            self.unit.set_ports(WORKLOAD_PORT)
+        else:
+            self.unit.set_ports()
 
     def _resource_reqs_from_config(self) -> ResourceRequirements:
         limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 1s</sub>

### ✅ `bash`

**Commit changes**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C2 && git add src/charm.py && git commit -m "refactor: use Unit.set_ports() declarative API for port management

Replace the imperative open_port()/close_port() pattern with the
declarative Unit.set_ports() API introduced in ops 2.7.0.

The new API automatically handles the diff between desired and actual
open ports, eliminating the need to manually track opened_ports(),
compute the difference, and call open/close individually.

Also removes the now-unused Port import from ops.model.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[detached HEAD d35f2d7] refactor: use Unit.set_ports() declarative API for port management
 1 file changed, 4 insertions(+), 12 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 3m 9s</sub>

### 💬 Copilot

Done. Here's a summary of the changes:

**`src/charm.py`** — replaced the manual imperative pattern in `_set_ports()`:

| Before | After |
|--------|-------|
| Calls `unit.opened_ports()`, diffs against desired ports, loops to call `open_port()`/`close_port()` individually | Single call to `unit.set_ports(WORKLOAD_PORT)` (leader) or `unit.set_ports()` (non-leader) |
| Needed `from ops.model import Port` | Import removed (no longer needed) |

`set_ports()` handles the diff internally — ports not in the call are automatically closed, ports that are already open are left alone. All 122 unit tests pass.

---

<sub>⏱️ 3m 9s</sub>

### ✅ `task_complete`

**Replaced the imperative `open_port()`/`close_port()` patt...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Replaced the imperative `open_port()`/`close_port()` pattern in `_set_ports()` with the declarative `Unit.set_ports()` API (ops 2.7.0+). The method went from ~10 lines of manual diffing to 3 lines. Also removed the now-unused `Port` import from `ops.model`. All 122 unit tests pass."
}
```

</details>

```
Replaced the imperative `open_port()`/`close_port()` pattern in `_set_ports()` with the declarative `Unit.set_ports()` API (ops 2.7.0+). The method went from ~10 lines of manual diffing to 3 lines. Also removed the now-unused `Port` import from `ops.model`. All 122 unit tests pass.
```


---

<sub>⏱️ 3m 9s</sub>

### ✓ Task Complete

Replaced the imperative `open_port()`/`close_port()` pattern in `_set_ports()` with the declarative `Unit.set_ports()` API (ops 2.7.0+). The method went from ~10 lines of manual diffing to 3 lines. Also removed the now-unused `Port` import from `ops.model`. All 122 unit tests pass.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
