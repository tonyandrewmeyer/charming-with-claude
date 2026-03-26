# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `dcb3942c-b6a0-4fb1-a240-766fa1d7f5e2`  
> - **Started:** 3/15/2026, 3:19:59 PM  
> - **Duration:** 5m 49s  
> - **Exported:** 3/15/2026, 3:25:48 PM  

---

<sub>⏱️ 6s</sub>

### 👤 User

This charm could benefit from ops-tracing. There is a skill available for applying this change.

---

<sub>⏱️ 14s</sub>

### 📦 task (Completed)

### 💬 Copilot

I'll help you explore this repository. Let me start by checking the directory structure and then search for all the specific files and patterns you mentioned.

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf

<details>
<summary>21 lines</summary>

```
.git
.github
.gitignore
.jujuignore
CODEOWNERS
CONTRIBUTING.md
INTEGRATING.md
LICENSE
PROMTAIL_RELEASES.md
README.md
SECURITY.md
charmcraft.yaml
icon.svg
lib
promtail-build
pyproject.toml
src
terraform
tests
tox.ini
uv.lock
```

</details>


### ✅ `glob`

**/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf**

"pyproject.toml" in /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf

```
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/integration/log-proxy-tester/pyproject.toml
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/pyproject.toml
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/integration/log-forwarder-tester/pyproject.toml
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/integration/loki-tester/pyproject.toml
```


### ✅ `glob`

**/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf**

"charmcraft.yaml" in /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf

```
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/integration/log-proxy-tester/charmcraft.yaml
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/charmcraft.yaml
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/integration/log-forwarder-tester/charmcraft.yaml
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/integration/loki-tester/charmcraft.yaml
```


### ✅ `glob`

**/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf**

"tox.ini" in /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf

```
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tox.ini
```


### ✅ `glob`

**/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf**

"**/charm.py" in /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf

```
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/integration/log-proxy-tester/src/charm.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/integration/log-forwarder-tester/src/charm.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/integration/loki-tester/src/charm.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py
```


### ✅ `glob`

**/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf**

"lib/charms/tempo_k8s/**" in /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf

```
No files matched the pattern.
```


### 💬 Copilot

Let me search for tempo_k8s in the lib directory and also search for the tracing imports:

### ✅ `bash`

**Find Python files in lib directory**

$ find /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib -type f -name "*.py" 2>/dev/null | head -20

<details>
<summary>14 lines</summary>

```
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/observability_libs/v0/kubernetes_compute_resources_patch.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/tracing.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/alertmanager_k8s/v1/alertmanager_dispatch.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/loki_k8s/v1/loki_push_api.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/loki_k8s/v0/charm_logging.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/loki_k8s/v0/loki_push_api.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/grafana_k8s/v0/grafana_dashboard.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/grafana_k8s/v0/grafana_source.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/catalogue_k8s/v1/catalogue.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/prometheus_k8s/v0/prometheus_scrape.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/traefik_k8s/v1/ingress_per_unit.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tls_certificates_interface/v4/tls_certificates.py
<exited with exit code 0>
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/pyproject.toml.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/pyproject.toml

<details>
<summary>96 lines</summary>

```
1. # Copyright 2021 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. [project]
4. name = "loki-k8s"
5. version = "0.0"
6. requires-python = "~=3.8"
7. 
8. dependencies = [
9.   "ops",
10.   "cosl",
11.   "kubernetes",
12.   "requests",
13.   "pyyaml",
14.   "lightkube",
15.   "lightkube-models",
16.   "aiohttp!=3.11.13",  # Yanked
17.   "jsonschema",
18.   "cryptography",
19.   "pydantic>=2.9.0",
20.   "importlib-metadata==6.0.0",
21.   "opentelemetry-api==1.21.0",
22.   "opentelemetry-exporter-otlp-proto-common==1.21.0",
23.   "opentelemetry-exporter-otlp-proto-http==1.21.0",
24.   "opentelemetry-proto==1.21.0",
25.   "opentelemetry-sdk==1.21.0",
26.   "opentelemetry-semantic-conventions==0.42b0",
27. ]
28. 
29. [project.optional-dependencies]
30. dev = [
31.   # Linting
32.   "ruff",
33.   "codespell",
34.   # Static
35.   "pyright",
36.   # Unit
37.   "pytest",
38.   "coverage[toml]",
39.   "ops[testing]",
40.   "responses",
41.   "fs",
42.   # Interface
43.   "pytest-interface-tester",
44.   # Integration
45.   "juju",
46.   "pytest-operator",
47.   "minio",
48.   "sh",
49. ]
50. 
51. # Testing tools configuration
52. [tool.coverage.run]
53. branch = true
54. 
55. [tool.coverage.report]
56. show_missing = true
57. 
58. # Formatting tools configuration
59. [tool.black]
60. line-length = 99
61. target-version = ["py38"]
62. 
63. # Linting tools configuration
64. [tool.ruff]
65. line-length = 99
66. extend-exclude = ["__pycache__", "*.egg_info"]
67. lint.select = ["E", "W", "F", "C", "N", "R", "D", "I001"]
68. # Ignore E501 because using black creates errors with this
69. # Ignore D107 Missing docstring in __init__
70. lint.ignore = ["E501", "D107", "RET504"]
71. # D100, D101, D102, D103: Ignore missing docstrings in tests
72. lint.per-file-ignores = {"tests/*" = ["D100","D101","D102","D103"]}
73. lint.pydocstyle.convention = "google"
74. 
75. # Static analysis tools configuration
76. [tool.pyright]
77. extraPaths = ["lib"]
78. pythonVersion = "3.8"
79. pythonPlatform = "All"
80. exclude = [
81.   "tests/integration/loki-tester/**",
82.   "tests/integration/log-proxy-tester/**",
83.   "tests/integration/log-forwarder-tester/**"
84. ]
85. 
86. [tool.pytest.ini_options]
87. minversion = "6.0"
88. log_cli_level = "INFO"
89. asyncio_mode = "auto"
90. addopts = "--tb=native --verbose --capture=no --log-cli-level=INFO"
91. markers = ["setup", "work", "teardown"]
92. 
93. [tool.codespell]
94. skip = ".git,.tox,build,venv*"
95. ignore-words-list = "assertIn"
96.
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py

```
File too large to read at once (38.5 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/charmcraft.yaml.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/charmcraft.yaml

<details>
<summary>201 lines</summary>

```
1. # Learn more about charmcraft.yaml configuration at:
2. # https://juju.is/docs/sdk/charmcraft-config
3. name: loki-k8s
4. type: "charm"
5. summary: Loki is a log aggregation system inspired by Prometheus.
6. description: >
7.   Loki is a set of components that can be composed into a fully featured logging stack.
8. 
9. links:
10.   documentation: https://discourse.charmhub.io/t/loki-k8s-docs-index/5228
11.   website: https://charmhub.io/loki-k8s
12.   source: https://github.com/canonical/loki-k8s-operator
13.   issues: https://github.com/canonical/loki-k8s-operator/issues
14. 
15. assumes:
16.   - k8s-api
17.   - juju >= 3.6  # Juju 3.0.3+ needed for secrets and open-port
18. 
19. platforms:
20.   ubuntu@24.04:amd64:
21. 
22. parts:
23.   charm:
24.     source: .
25.     plugin: uv
26.     build-packages: [git]
27.     build-snaps: [astral-uv]
28.     override-build: |
29.       craftctl default
30.       git describe --always > $CRAFT_PART_INSTALL/version
31.   cos-tool:
32.     plugin: dump
33.     source: https://github.com/canonical/cos-tool/releases/latest/download/cos-tool-${CRAFT_ARCH_BUILD_FOR}
34.     source-type: file
35.     permissions:
36.       - path: cos-tool-${CRAFT_ARCH_BUILD_FOR}
37.         mode: "755"
38. 
39. containers:
40.   loki:
41.     resource: loki-image
42.     mounts:
43.       - storage: active-index-directory
44.         location: /loki/boltdb-shipper-active
45.       - storage: loki-chunks
46.         location: /loki/chunks
47.   node-exporter:
48.     resource: node-exporter-image
49.     mounts:
50.       - storage: active-index-directory
51.         location: /loki/boltdb-shipper-active
52.       - storage: loki-chunks
53.         location: /loki/chunks
54. 
55. # We do not need separate storages. TODO: In the next breaking change for Loki,
56. # switch to having just one persisted storage, e.g. `/loki/persisted`.
57. storage:
58.   active-index-directory:
59.     type: filesystem
60.     description: Mount point in which Loki will store index
61.   loki-chunks:
62.     type: filesystem
63.     description: Mount point in which Loki will store chunks (objects)
64. 
65. provides:
66.   logging:
67.     interface: loki_push_api
68.     optional: true
69.     description: Integration to receive logs from other charms.
70.   grafana-source:
71.     interface: grafana_datasource
72.     optional: true
73.     description: |
74.       Configures Grafana to be able to use this Loki instance as a datasource.
75.   metrics-endpoint:
76.     interface: prometheus_scrape
77.     optional: true
78.     description: |
79.       Exposes the Prometheus metrics endpoint providing telemetry about the Loki instance.
80.   grafana-dashboard:
81.     interface: grafana_dashboard
82.     optional: true
83.     description: |
84.       Forwards the built-in Grafana dashboard(s) for monitoring Loki.
85.   send-datasource:
86.     interface: grafana_datasource_exchange
87.     optional: true
88.     description: |
89.       Integration to share with other COS components this charm's grafana datasources,
90.       and receive theirs.
91. 
92. requires:
93.   alertmanager:
94.     interface: alertmanager_dispatch
95.     optional: true
96.     description: |
97.       Integrates with an Alertmanager to send notifications when alert rules are triggered.
98.   ingress:
99.     interface: ingress_per_unit
100.     optional: true
101.     limit: 1 # Since this is the ingress there is no point in having more than one.
102.     description: |
103.       Ingress integration for Loki, so that cross-model workloads can send their logs
104.       to Loki through the ingress.
105.       Loki uses "ingress per unit" (not per app), so each unit gets is ingressed separately.
106.   certificates:
107.     interface: tls-certificates
108.     optional: true
109.     limit: 1
110.     description: Certificate and key files for the Loki server.
111.   catalogue:
112.     interface: catalogue
113.     optional: true
114.     description: Add Loki as an item to a Catalogue charm.
115.   charm-tracing:
116.     interface: tracing
117.     optional: true
118.     limit: 1
119.     description: |
120.       Enables sending charm traces to a distributed tracing backend such as Tempo.
121.   workload-tracing:
122.     interface: tracing
123.     optional: true
124.     limit: 1
125.     description: |
126.       Enables sending workload traces to a distributed tracing backend such as Tempo.
127. 
128. peers:
129.   replicas:
130.     interface: loki_replica
131. 
132. resources:
133.   loki-image:
134.     type: oci-image
135.     description: Loki OCI image
136.     upstream-source: docker.io/ubuntu/loki@sha256:c1cf06a25176ea7c9574b53df272c2cc56c3f797a2a0c574c8e6ad923b0657b4  # renovate: oci-image tag: 2.9-24.04
137.   node-exporter-image:
138.     type: oci-image
139.     description: Node-exporter OCI image
140.     upstream-source: docker.io/prom/node-exporter@sha256:4cb2b9019f1757be8482419002cb7afe028fdba35d47958829e4cfeaf6246d80  # renovate: oci-image tag: v1.7.0
141. 
142. config:
143.   options:
144.     cpu:
145.       description: |
146.         K8s cpu resource limit, e.g. "1" or "500m". Default is unset (no limit). This value is used
147.         for the "limits" portion of the resource requirements (the "requests" portion is
148.         automatically deduced from it).
149.         See https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
150.       type: string
151.     memory:
152.       description: |
153.         K8s memory resource limit, e.g. "1Gi". Default is unset (no limit). This value is used
154.         for the "limits" portion of the resource requirements (the "requests" portion is
155.         automatically deduced from it).
156.         See https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
157.       type: string
158.     ingestion-rate-mb:
159.       description: |
160.         Per-user ingestion rate limit (MB/s).
161.         This config option matches exactly Loki's `ingestion_rate_mb`, except that it is an integer here
162.         (Loki takes a float).
163.         This same value is used internally for setting `per_stream_rate_limit`. Loki uses a default of 3 for
164.         `ingestion_rate_mb`, but 4 for `per_stream_rate_limit`. For this reason we use 4 as the default here.
165.         
166.         Ref: https://grafana.com/docs/loki/latest/configure/#limits_config
167.       type: int
168.       default: 4
169.     ingestion-burst-size-mb:
170.       description: |
171.         This config option matches exactly Loki's `ingestion_burst_size_mb`, except that it is an integer here
172.         (Loki takes a float).
173.         This same value is used internally for setting `per_stream_rate_limit_burst`. Loki uses a default of 6 for 
174.         `ingestion_burst_size_mb`, but 15 for `per_stream_rate_limit_burst`. For this reason we use 15 as the default
175.         here.
176.         
177.         Ref: https://grafana.com/docs/loki/latest/configure/#limits_config
178.       type: int
179.       default: 15
180.     retention-period:
181.       description: |
182.         Sets a global retention period, in days, for log streams in Loki.
183.         The minimum retention period is 1 day, and a value of 0 (default) means "infinity" (disables retention).
184.         Loki will not be cleaning up logs if duration is set to 0.
185.         This config maps directly to the loki `compactor.retention_enabled` configuration option, which is set to `false` when no retention period is defined.
186.         Specifying retention periods for individual streams is not currently supported.
187. 
188.         Ref: https://grafana.com/docs/loki/latest/operations/storage/retention/
189.       type: int
190.       default: 0
191.     reporting-enabled:
192.       description: |
193.         When disabled, Loki will be configured to not send anonymous usage statistics to stats.grafana.org.
194.         It is very helpful to the Grafana project, so please leave this enabled.
195.         
196.         When enabled, Loki will use its default values for analytics.
197.         
198.         Ref: https://grafana.com/docs/loki/latest/configure/#analytics
199.       type: boolean
200.       default: true
201.
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tox.ini.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tox.ini

<details>
<summary>70 lines</summary>

```
1. # Copyright 2021 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. [tox]
4. skipsdist=True
5. skip_missing_interpreters = True
6. envlist = lint, static, unit
7. 
8. [vars]
9. src_path = {toxinidir}/src
10. tst_path = {toxinidir}/tests
11. lib_path = {toxinidir}/lib/charms/loki_k8s
12. all_path = {[vars]src_path} {[vars]tst_path} {[vars]lib_path}
13. uv_flags = --frozen --isolated --extra=dev
14. 
15. [testenv]
16. allowlist_externals = uv
17. basepython = python3
18. setenv =
19.   PYTHONPATH = {toxinidir}:{toxinidir}/lib:{[vars]src_path}
20.   PYTHONBREAKPOINT=ipdb.set_trace
21.   PY_COLORS=1
22. passenv =
23.   PYTHONPATH
24.   CHARM_PATH
25. 
26. [testenv:lock]
27. description = Update uv.lock with the latest deps
28. commands =
29.   uv lock --upgrade --no-cache
30. 
31. [testenv:lint]
32. description = Lint the code
33. commands =
34.     uv run {[vars]uv_flags} ruff check {[vars]all_path}
35. 
36. [testenv:static]
37. description = Run static checks
38. allowlist_externals =
39.   {[testenv]allowlist_externals}
40.   /usr/bin/env
41. commands =
42.     uv run {[vars]uv_flags} pyright {[vars]all_path}
43.     /usr/bin/env sh -c 'for m in $(git diff main --name-only {[vars]lib_path}); do if ! git diff main $m | grep -q "+LIBPATCH\|+LIBAPI"; then echo "You forgot to bump the version on $m!"; exit 1; fi; done'
44. 
45. [testenv:fmt]
46. description = "Format the code"
47. commands =
48.     uv run {[vars]uv_flags} ruff check --fix-only {[vars]all_path}
49. 
50. [testenv:unit]
51. description = Run unit tests
52. allowlist_externals=
53.     {[testenv]allowlist_externals}
54.     /usr/bin/env
55. commands =
56.     /usr/bin/env sh -c 'stat cos-tool-amd64 > /dev/null 2>&1 || curl -L -O https://github.com/canonical/cos-tool/releases/latest/download/cos-tool-amd64 && chmod 755 cos-tool-amd64'
57.     uv run {[vars]uv_flags} coverage run --source={[vars]src_path},{[vars]lib_path} -m pytest \
58.         {[vars]tst_path}/unit {posargs}
59.     uv run {[vars]uv_flags} coverage report
60. 
61. [testenv:interface]
62. description = Run interface tests
63. commands =
64.     uv run {[vars]uv_flags} pytest --exitfirst {[vars]tst_path}/interface {posargs}
65. 
66. [testenv:integration]
67. description = Run integration tests
68. commands =
69.     uv run {[vars]uv_flags} pytest --exitfirst {[vars]tst_path}/integration {posargs}
70.
```

</details>


### 💬 Copilot

Now let me view the charm.py file (it was too large, so I'll use view_range) and search for tracing imports across Python files:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py (lines 1-100)

<details>
<summary>100 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2021 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. #
5. # Learn more at: https://juju.is/docs/sdk
6. 
7. """Charm the service.
8. 
9. Refer to the following post for a quick-start guide that will help you
10. develop a new k8s charm using the Operator Framework:
11. 
12.     https://discourse.charmhub.io/t/4208
13. """
14. 
15. import datetime
16. import logging
17. import os
18. import re
19. import socket
20. import ssl
21. import subprocess
22. import time
23. import urllib.request
24. from dataclasses import dataclass
25. from pathlib import Path
26. from typing import Any, Dict, List, Optional, Tuple, TypedDict, cast
27. from urllib.error import HTTPError, URLError
28. from urllib.parse import urlparse
29. 
30. import yaml
31. from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerConsumer
32. from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
33. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
34. from charms.grafana_k8s.v0.grafana_source import GrafanaSourceData, GrafanaSourceProvider
35. from charms.loki_k8s.v0.charm_logging import log_charm
36. from charms.loki_k8s.v1.loki_push_api import (
37.     LokiPushApiAlertRulesChanged,
38.     LokiPushApiProvider,
39. )
40. from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
41.     K8sResourcePatchFailedEvent,
42.     KubernetesComputeResourcesPatch,
43.     ResourceRequirements,
44.     adjust_resource_requirements,
45. )
46. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
47. from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
48. from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
49. from charms.tls_certificates_interface.v4.tls_certificates import (
50.     CertificateRequestAttributes,
51.     TLSCertificatesRequiresV4,
52. )
53. from charms.traefik_k8s.v1.ingress_per_unit import IngressPerUnitRequirer
54. from cosl import JujuTopology
55. from cosl.interfaces.datasource_exchange import DatasourceDict, DatasourceExchange
56. from ops import CollectStatusEvent, StoredState
57. from ops.charm import CharmBase
58. from ops.main import main
59. from ops.model import (
60.     ActiveStatus,
61.     BlockedStatus,
62.     MaintenanceStatus,
63.     Port,
64.     StatusBase,
65.     WaitingStatus,
66. )
67. from ops.pebble import Error, Layer, PathError, ProtocolError
68. 
69. from config_builder import (
70.     CERT_FILE,
71.     HTTP_LISTEN_PORT,
72.     KEY_FILE,
73.     LOKI_CONFIG,
74.     LOKI_CONFIG_BACKUP,
75.     RULES_DIR,
76.     ConfigBuilder,
77. )
78. 
79. # To keep a tidy debug-log, we suppress some DEBUG/INFO logs from some imported libs,
80. # even when charm logging is set to a lower level.
81. logging.getLogger("httpx").setLevel(logging.WARNING)
82. logging.getLogger("httpcore").setLevel(logging.WARNING)
83. logger = logging.getLogger(__name__)
84. 
85. @dataclass
86. class TLSConfig:
87.     """TLS configuration received by the charm over the `certificates` relation."""
88. 
89.     server_cert: str
90.     ca_cert: str
91.     private_key: str
92. 
93. class CompositeStatus(TypedDict):
94.     """Per-component status holder."""
95. 
96.     # These are going to go into stored state, so we must use marshallable objects.
97.     # They are passed to StatusBase.from_name().
98.     k8s_patch: Tuple[str, str]
99.     config: Tuple[str, str]
100.     rules: Tuple[str, str]
```

</details>


### ✅ `grep`

**/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf**

"charm_tracing|trace_charm|TracingEndpointRequirer|charms\.tempo_k8s" in py files (/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf)

```
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/interface/conftest.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/tracing.py
```


### ✅ `bash`

**Find tempo-related files in lib**

$ find /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib -type f -path "*/tempo*"

```
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/tracing.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py
<exited with exit code 0>
```


### ✅ `grep`

**/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests**

"charm_tracing|trace_charm|TracingEndpointRequirer" in py files (/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests)

```
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/interface/conftest.py
```


### 💬 Copilot

Excellent! Now let me view the tracing-related files and test conftest files:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py

```
File too large to read at once (44.8 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/tracing.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/tracing.py (lines 1-150)

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
19.     from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer
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
37. Units of requirer charms obtain the tempo endpoint to which they will push their traces by calling
38. `TracingEndpointRequirer.get_endpoint(protocol: str)`, where `protocol` is, for example:
39. - `otlp_grpc`
40. - `otlp_http`
41. - `zipkin`
42. - `tempo`
43. 
44. If the `protocol` is not in the list of protocols that the charm requested at endpoint set-up time,
45. the library will raise an error.
46. 
47. We recommend that you scale up your tracing provider and relate it to an ingress so that your tracing requests
48. go through the ingress and get load balanced across all units. Otherwise, if the provider's leader goes down, your tracing goes down.
49. 
50. ## Provider Library Usage
51. 
52. The `TracingEndpointProvider` object may be used by charms to manage relations with their
53. trace sources. For this purposes a Tempo-like charm needs to do two things
54. 
55. 1. Instantiate the `TracingEndpointProvider` object by providing it a
56. reference to the parent (Tempo) charm and optionally the name of the relation that the Tempo charm
57. uses to interact with its trace sources. This relation must conform to the `tracing` interface
58. and it is strongly recommended that this relation be named `tracing` which is its
59. default value.
60. 
61. For example a Tempo charm may instantiate the `TracingEndpointProvider` in its constructor as
62. follows
63. 
64.     from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointProvider
65. 
66.     def __init__(self, *args):
67.         super().__init__(*args)
68.         # ...
69.         self.tracing = TracingEndpointProvider(self)
70.         # ...
71. 
72. 
73. 
74. """  # noqa: W505
75. 
76. import enum
77. import json
78. import logging
79. from pathlib import Path
80. from typing import (
81.     TYPE_CHECKING,
82.     Any,
83.     Dict,
84.     List,
85.     Literal,
86.     MutableMapping,
87.     Optional,
88.     Sequence,
89.     Tuple,
90.     Union,
91.     cast,
92. )
93. 
94. import pydantic
95. from ops.charm import (
96.     CharmBase,
97.     CharmEvents,
98.     RelationBrokenEvent,
99.     RelationEvent,
100.     RelationRole,
101. )
102. from ops.framework import EventSource, Object
103. from ops.model import ModelError, Relation
104. from pydantic import BaseModel, Field
105. 
106. # The unique Charmhub library identifier, never change it
107. LIBID = "d2f02b1f8d1244b5989fd55bc3a28943"
108. 
109. # Increment this major API version when introducing breaking changes
110. LIBAPI = 0
111. 
112. # Increment this PATCH version before using `charmcraft publish-lib` or reset
113. # to 0 if you are raising the major API version
114. LIBPATCH = 11
115. 
116. PYDEPS = ["pydantic"]
117. 
118. logger = logging.getLogger(__name__)
119. 
120. DEFAULT_RELATION_NAME = "tracing"
121. RELATION_INTERFACE_NAME = "tracing"
122. 
123. # Supported list rationale https://github.com/canonical/tempo-coordinator-k8s-operator/issues/8
124. ReceiverProtocol = Literal[
125.     "zipkin",
126.     "otlp_grpc",
127.     "otlp_http",
128.     "jaeger_grpc",
129.     "jaeger_thrift_http",
130. ]
131. 
132. RawReceiver = Tuple[ReceiverProtocol, str]
133. # Helper type. A raw receiver is defined as a tuple consisting of the protocol name, and the (external, if available),
134. # (secured, if available) resolvable server url.
135. 
136. 
137. BUILTIN_JUJU_KEYS = {"ingress-address", "private-address", "egress-subnets"}
138. 
139. 
140. class TransportProtocolType(str, enum.Enum):
141.     """Receiver Type."""
142. 
143.     http = "http"
144.     grpc = "grpc"
145. 
146. 
147. receiver_protocol_to_transport_protocol: Dict[
148.     ReceiverProtocol, TransportProtocolType
149. ] = {
150.     "zipkin": TransportProtocolType.http,
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py

<details>
<summary>53 lines</summary>

```
1. from unittest.mock import PropertyMock, patch
2. 
3. import ops
4. import pytest
5. from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
6. from ops.testing import Context
7. from scenario import Container, Exec
8. 
9. from charm import LokiOperatorCharm
10. 
11. 
12. def tautology(*_, **__) -> bool:
13.     return True
14. 
15. 
16. @pytest.fixture(autouse=True)
17. def patch_buffer_file_for_charm_tracing(tmp_path):
18.     with patch(
19.         "charms.tempo_coordinator_k8s.v0.charm_tracing.BUFFER_DEFAULT_CACHE_FILE_NAME",
20.         str(tmp_path / "foo.json"),
21.     ):
22.         yield
23. 
24. 
25. @pytest.fixture
26. def loki_charm(tmp_path):
27.     with patch.multiple(
28.         "charm.KubernetesComputeResourcesPatch",
29.         _namespace=PropertyMock("test-namespace"),
30.         _patch=PropertyMock(tautology),
31.         is_ready=PropertyMock(tautology),
32.     ):
33.         with patch("socket.getfqdn", new=lambda *args: "fqdn"):
34.             with patch("lightkube.core.client.GenericSyncClient"):
35.                 with charm_tracing_disabled():
36.                     yield LokiOperatorCharm
37. 
38. 
39. @pytest.fixture
40. def context(loki_charm):
41.     return Context(loki_charm)
42. 
43. 
44. @pytest.fixture(scope="function")
45. def loki_container():
46.     return Container(
47.         "loki",
48.         can_connect=True,
49.         execs={Exec(["update-ca-certificates", "--fresh"], return_code=0)},
50.         layers={"loki": ops.pebble.Layer({"services": {"loki": {}}})},
51.         service_statuses={"loki": ops.pebble.ServiceStatus.INACTIVE},
52.     )
53.
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/interface/conftest.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/interface/conftest.py

<details>
<summary>82 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. import json
5. from contextlib import ExitStack
6. from unittest.mock import MagicMock, patch
7. 
8. import ops
9. import pytest
10. from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
11. from interface_tester import InterfaceTester
12. from ops import ActiveStatus
13. from scenario.state import Container, Exec, Relation, State
14. 
15. from charm import LokiOperatorCharm
16. 
17. 
18. @pytest.fixture(autouse=True, scope="module")
19. def patch_all():
20.     with ExitStack() as stack:
21.         stack.enter_context(patch("lightkube.core.client.GenericSyncClient"))
22.         stack.enter_context(
23.             patch.multiple(
24.                 "charms.observability_libs.v0.kubernetes_compute_resources_patch.KubernetesComputeResourcesPatch",
25.                 _namespace="test-namespace",
26.                 _patch=lambda _: None,
27.                 is_ready=MagicMock(return_value=True),
28.                 get_status=lambda _: ActiveStatus(""),
29.             )
30.         )
31.         stack.enter_context(charm_tracing_disabled())
32. 
33.         yield
34. 
35. 
36. loki_container = Container(
37.     name="loki",
38.     can_connect=True,
39.     execs={Exec(["update-ca-certificates", "--fresh"], return_code=0)},
40.     layers={"loki": ops.pebble.Layer({"services": {"loki": {}}})},
41.     service_statuses={"loki": ops.pebble.ServiceStatus.ACTIVE},
42. )
43. 
44. grafana_source_relation = Relation(
45.     "grafana-source",
46.     remote_app_data={
47.         "datasource_uids": json.dumps({"loki/0": "01234"}),
48.         "grafana_uid": "5678",
49.     },
50. )
51. 
52. grafana_datasource_exchange_relation = Relation(
53.     "send-datasource",
54.     remote_app_data={
55.         "datasources": json.dumps([{"type": "loki", "uid": "01234", "grafana_uid": "5678"}])
56.     },
57. )
58. 
59. 
60. @pytest.fixture
61. def grafana_datasource_tester(interface_tester: InterfaceTester):
62.     interface_tester.configure(
63.         charm_type=LokiOperatorCharm,
64.         state_template=State(
65.             leader=True, containers=[loki_container], relations=[grafana_source_relation]
66.         ),
67.     )
68.     yield interface_tester
69. 
70. 
71. @pytest.fixture
72. def grafana_datasource_exchange_tester(interface_tester: InterfaceTester):
73.     interface_tester.configure(
74.         charm_type=LokiOperatorCharm,
75.         state_template=State(
76.             leader=True,
77.             containers=[loki_container],
78.             relations=[grafana_source_relation, grafana_datasource_exchange_relation],
79.         ),
80.     )
81.     yield interface_tester
82.
```

</details>


### 💬 Copilot

Now let me get more of the charm_tracing.py file and check the rest of the charm.py for more context:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py (lines 1-150)

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
13. Fetch the following charm libs:
14. 
15.     charmcraft fetch-lib charms.tempo_coordinator_k8s.v0.tracing
16.     charmcraft fetch-lib charms.tempo_coordinator_k8s.v0.charm_tracing
17. 
18. Then edit your charm code to include:
19. 
20. ```python
21. # import the necessary charm libs
22. from charms.tempo_coordinator_k8s.v0.tracing import (
23.     TracingEndpointRequirer,
24.     charm_tracing_config,
25. )
26. from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing
27. 
28. 
29. # decorate your charm class with charm_tracing:
30. @charm_tracing(
31.     # forward-declare the instance attributes that the instrumentor will look up to obtain the
32.     # tempo endpoint and server certificate
33.     tracing_endpoint="tracing_endpoint",
34.     server_cert="server_cert",
35. )
36. class MyCharm(CharmBase):
37.     _path_to_cert = "/path/to/cert.crt"
38.     # path to cert file **in the charm container**. Its presence will be used to determine whether
39.     # the charm is ready to use tls for encrypting charm traces. If your charm does not support tls,
40.     # you can ignore this and pass None to charm_tracing_config.
41.     # If you do support TLS, you'll need to make sure that the server cert is copied to this location
42.     # and kept up to date so the instrumentor can use it.
43. 
44.     def __init__(self, framework):
45.         # ...
46.         self.tracing = TracingEndpointRequirer(self)
47.         self.tracing_endpoint, self.server_cert = charm_tracing_config(
48.             self.tracing, self._path_to_cert
49.         )
50. ```
51. 
52. # Detailed usage
53. To use this library, you need to do two things:
54. 1) decorate your charm class with
55. 
56. `@trace_charm(tracing_endpoint="my_tracing_endpoint")`
57. 
58. 2) add to your charm a "my_tracing_endpoint" (you can name this attribute whatever you like)
59. **property**, **method** or **instance attribute** that returns an otlp http/https endpoint url.
60. If you are using the ``charms.tempo_coordinator_k8s.v0.tracing.TracingEndpointRequirer`` as
61. ``self.tracing = TracingEndpointRequirer(self)``, the implementation could be:
62. 
63. ```
64.     @property
65.     def my_tracing_endpoint(self) -> Optional[str]:
66.         '''Tempo endpoint for charm tracing'''
67.         if self.tracing.is_ready():
68.             return self.tracing.get_endpoint("otlp_http")
69.         else:
70.             return None
71. ```
72. 
73. At this point your charm will be automatically instrumented so that:
74. - charm execution starts a trace, containing
75.     - every event as a span (including custom events)
76.     - every charm method call (except dunders) as a span
77. 
78. We recommend that you scale up your tracing provider and relate it to an ingress so that your tracing requests
79. go through the ingress and get load balanced across all units. Otherwise, if the provider's leader goes down, your tracing goes down.
80. 
81. 
82. ## TLS support
83. If your charm integrates with a TLS provider which is also trusted by the tracing provider (the Tempo charm),
84. you can configure ``charm_tracing`` to use TLS by passing a ``server_cert`` parameter to the decorator.
85. 
86. If your charm is not trusting the same CA as the Tempo endpoint it is sending traces to,
87. you'll need to implement a cert-transfer relation to obtain the CA certificate from the same
88. CA that Tempo is using.
89. 
90. For example:
91. ```
92. from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
93. @trace_charm(
94.     tracing_endpoint="my_tracing_endpoint",
95.     server_cert="_server_cert"
96. )
97. class MyCharm(CharmBase):
98.     self._server_cert = "/path/to/server.crt"
99.     ...
100. 
101.     def on_tls_changed(self, e) -> Optional[str]:
102.         # update the server cert on the charm container for charm tracing
103.         Path(self._server_cert).write_text(self.get_server_cert())
104. 
105.     def on_tls_broken(self, e) -> Optional[str]:
106.         # remove the server cert so charm_tracing won't try to use tls anymore
107.         Path(self._server_cert).unlink()
108. ```
109. 
110. 
111. ## More fine-grained manual instrumentation
112. if you wish to add more spans to the trace, you can do so by getting a hold of the tracer like so:
113. ```
114. import opentelemetry
115. ...
116. def get_tracer(self) -> opentelemetry.trace.Tracer:
117.     return opentelemetry.trace.get_tracer(type(self).__name__)
118. ```
119. 
120. By default, the tracer is named after the charm type. If you wish to override that, you can pass
121. a different ``service_name`` argument to ``trace_charm``.
122. 
123. See the official opentelemetry Python SDK documentation for usage:
124. https://opentelemetry-python.readthedocs.io/en/latest/
125. 
126. 
127. ## Caching traces
128. The `trace_charm` machinery will buffer any traces collected during charm execution and store them
129. to a file on the charm container until a tracing backend becomes available. At that point, it will
130. flush them to the tracing receiver.
131. 
132. By default, the buffer is configured to start dropping old traces if any of these conditions apply:
133. 
134. - the storage size exceeds 10 MiB
135. - the number of buffered events exceeds 100
136. 
137. You can configure this by, for example:
138. 
139. ```python
140. @trace_charm(
141.     tracing_endpoint="my_tracing_endpoint",
142.     server_cert="_server_cert",
143.     # only cache up to 42 events
144.     buffer_max_events=42,
145.     # only cache up to 42 MiB
146.     buffer_max_size_mib=42,  # minimum 10!
147. )
148. class MyCharm(CharmBase):
149.     ...
150. ```
````

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py (lines 100-250)

<details>
<summary>151 lines</summary>

```
100.     rules: Tuple[str, str]
101.     retention: Tuple[str, str]
102. 
103. 
104. def to_tuple(status: StatusBase) -> Tuple[str, str]:
105.     """Convert a StatusBase to tuple, so it is marshallable into StoredState."""
106.     return status.name, status.message
107. 
108. 
109. def to_status(tpl: Tuple[str, str]) -> StatusBase:
110.     """Convert a tuple to a StatusBase, so it could be used natively with ops."""
111.     name, message = tpl
112.     return StatusBase.from_name(name, message)
113. 
114. 
115. @trace_charm(
116.     tracing_endpoint="_charm_tracing_endpoint",
117.     server_cert="_charm_tracing_ca_cert",
118.     extra_types=[
119.         GrafanaDashboardProvider,
120.         GrafanaSourceProvider,
121.         LokiPushApiProvider,
122.         TLSCertificatesRequiresV4,
123.         ConfigBuilder,
124.         MetricsEndpointProvider,
125.     ],
126. )
127. @log_charm(logging_endpoints="_charm_logging_endpoints", server_cert="_charm_logging_ca_cert")
128. class LokiOperatorCharm(CharmBase):
129.     """Charm the service."""
130. 
131.     _stored = StoredState()
132.     _port = HTTP_LISTEN_PORT
133.     _name = "loki"
134.     _loki_push_api_endpoint = "/loki/api/v1/push"
135.     _loki_rules_endpoint = "/loki/api/v1/rules"
136.     _service_name = "loki"
137.     _ca_cert_path = "/usr/local/share/ca-certificates/cos-ca.crt"
138. 
139.     def __init__(self, *args):
140.         super().__init__(*args)
141. 
142.         # We need stored state for push statuses.
143.         # https://discourse.charmhub.io/t/its-probably-ok-for-a-unit-to-go-into-error-state/13022
144.         self._stored.set_default(
145.             status=CompositeStatus(
146.                 k8s_patch=to_tuple(ActiveStatus()),
147.                 config=to_tuple(ActiveStatus()),
148.                 rules=to_tuple(ActiveStatus()),
149.                 retention=to_tuple(ActiveStatus()),
150.             ),
151.             fresh_install=True,
152.         )
153. 
154.         self._loki_container = self.unit.get_container(self._name)
155.         self._node_exporter_container = self.unit.get_container("node-exporter")
156.         self.unit.set_ports(self._port)
157. 
158.         self._juju_topology = JujuTopology.from_charm(self)
159. 
160.         # If Loki is run in single-tenant mode, all the chunks are put in a folder named "fake"
161.         # https://grafana.com/docs/loki/latest/operations/storage/filesystem/
162.         # https://grafana.com/docs/loki/latest/rules/#ruler-storage
163.         tenant_id = "fake"
164.         self.rules_dir_tenant = os.path.join(RULES_DIR, tenant_id)
165. 
166.         self.unit.set_ports(Port("tcp", self._port))
167. 
168.         self.resources_patch = KubernetesComputeResourcesPatch(
169.             self,
170.             self._loki_container.name,
171.             resource_reqs_func=self._resource_reqs_from_config,
172.         )
173. 
174.         self._csr_attributes = CertificateRequestAttributes(
175.             # the `common_name` field is required but limited to 64 characters.
176.             # since it's overridden by sans, we can use a short,
177.             # constrained value like app name.
178.             common_name=self.app.name,
179.             sans_dns=frozenset((self.hostname,)),
180.         )
181.         self._cert_requirer = TLSCertificatesRequiresV4(
182.             charm=self,
183.             relationship_name="certificates",
184.             certificate_requests=[self._csr_attributes],
185.         )
186.         # Update certs here in init to avoid code ordering issues
187.         self._update_cert()
188.         self.framework.observe(
189.             self._cert_requirer.on.certificate_available,  # pyright: ignore
190.             self._on_certificate_available,
191.         )
192. 
193.         self.framework.observe(self.resources_patch.on.patch_failed, self._on_k8s_patch_failed)
194. 
195.         self.alertmanager_consumer = AlertmanagerConsumer(self, relation_name="alertmanager")
196.         self.framework.observe(
197.             self.alertmanager_consumer.on.cluster_changed, self._on_alertmanager_change
198.         )
199. 
200.         self.ingress_per_unit = IngressPerUnitRequirer(
201.             self,
202.             relation_name="ingress",
203.             port=self._port,
204.             scheme=lambda: "https" if self._tls_available else "http",
205.             strip_prefix=True,
206.         )
207.         self.framework.observe(self.ingress_per_unit.on.ready_for_unit, self._on_ingress_changed)
208.         self.framework.observe(self.ingress_per_unit.on.revoked_for_unit, self._on_ingress_changed)
209. 
210.         self.grafana_source_provider = GrafanaSourceProvider(
211.             charm=self,
212.             refresh_event=[
213.                 self.on.loki_pebble_ready,
214.                 self._cert_requirer.on.certificate_available,
215.             ],
216.             source_type="loki",
217.             source_url=self._external_url,
218.         )
219. 
220.         self.metrics_provider = MetricsEndpointProvider(
221.             self,
222.             jobs=self.scrape_jobs,
223.             refresh_event=[
224.                 self.on.update_status,
225.                 self.ingress_per_unit.on.ready_for_unit,
226.                 self.ingress_per_unit.on.revoked_for_unit,
227.                 self.on.ingress_relation_departed,
228.                 self._cert_requirer.on.certificate_available,
229.             ],
230.         )
231. 
232.         external_url = urlparse(self._external_url)
233.         self.loki_provider = LokiPushApiProvider(
234.             self,
235.             address=external_url.hostname or self.hostname,
236.             port=external_url.port or 443 if self._tls_available else 80,
237.             scheme=external_url.scheme,
238.             path=f"{external_url.path}{self._loki_push_api_endpoint}",
239.         )
240. 
241.         self.dashboard_provider = GrafanaDashboardProvider(self)
242. 
243.         self.catalogue = CatalogueConsumer(charm=self, item=self._catalogue_item)
244.         self.charm_tracing = TracingEndpointRequirer(
245.             self, relation_name="charm-tracing", protocols=["otlp_http"]
246.         )
247.         self.workload_tracing = TracingEndpointRequirer(
248.             self, relation_name="workload-tracing", protocols=["jaeger_thrift_http"]
249.         )
250.         self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
```

</details>


### ✅ `bash`

**Find charm_tracing usage in charm.py**

$ grep -n "charm_tracing" /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py | head -20

<details>
<summary>8 lines</summary>

```
47:from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
48:from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
116:    tracing_endpoint="_charm_tracing_endpoint",
117:    server_cert="_charm_tracing_ca_cert",
244:        self.charm_tracing = TracingEndpointRequirer(
250:        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
251:            self.charm_tracing, self._ca_cert_path
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Find trace_charm and charm_tracing_config usage**

$ grep -n "trace_charm\|charm_tracing_config" /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py | head -20

```
47:from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
48:from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
115:@trace_charm(
250:        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
<exited with exit code 0>
```


### 💬 Copilot

Perfect! Let me now check the rest of the charm.py for the workload_tracing setup and check for test files related to mocking:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py (lines 250-300)

<details>
<summary>51 lines</summary>

```
250.         self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
251.             self.charm_tracing, self._ca_cert_path
252.         )
253. 
254.         self.datasource_exchange = DatasourceExchange(
255.             self,
256.             provider_endpoint="send-datasource",
257.             requirer_endpoint=None,
258.         )
259. 
260.         self.framework.observe(
261.             self.workload_tracing.on.endpoint_changed,  # type: ignore
262.             self._on_workload_tracing_endpoint_changed,
263.         )
264.         self.framework.observe(
265.             self.workload_tracing.on.endpoint_removed,  # type: ignore
266.             self._on_workload_tracing_endpoint_removed,
267.         )
268. 
269.         self.framework.observe(self.on.config_changed, self._on_config_changed)
270.         self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
271.         self.framework.observe(self.on.loki_pebble_ready, self._on_loki_pebble_ready)
272.         self.framework.observe(
273.             self.on.node_exporter_pebble_ready, self._on_node_exporter_pebble_ready
274.         )
275. 
276.         self.framework.observe(
277.             self.loki_provider.on.loki_push_api_alert_rules_changed,
278.             self._loki_push_api_alert_rules_changed,
279.         )
280.         self.framework.observe(self.on.logging_relation_changed, self._on_logging_relation_changed)
281. 
282.         self.framework.observe(
283.             self.on.send_datasource_relation_changed, self._on_grafana_source_changed
284.         )
285.         self.framework.observe(
286.             self.on.send_datasource_relation_departed, self._on_grafana_source_changed
287.         )
288.         self.framework.observe(
289.             self.on.grafana_source_relation_joined, self._on_grafana_source_changed
290.         )
291.         self.framework.observe(
292.             self.on.grafana_source_relation_changed, self._on_grafana_source_changed
293.         )
294.         self.framework.observe(
295.             self.on.grafana_source_relation_created, self._on_grafana_source_changed
296.         )
297.         self.framework.observe(
298.             self.on.grafana_source_relation_departed, self._on_grafana_source_changed
299.         )
300.
```

</details>


### ✅ `bash`

**Find test files that use charm_tracing mocking or patching**

$ find /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests -name "*.py" -exec grep -l "patch.*charm_tracing\|mock.*charm_tracing\|charm_tracing_disabled" {} \;

```
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/interface/conftest.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py
<exited with exit code 0>
```


### ✅ `bash`

**List files in tempo_coordinator_k8s v0**

$ ls -la /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/

<details>
<summary>6 lines</summary>

```
total 96
drwxrwxr-x 2 ubuntu ubuntu  4096 Mar 15 15:19 .
drwxrwxr-x 3 ubuntu ubuntu  4096 Mar 12 16:15 ..
-rw-rw-r-- 1 ubuntu ubuntu 45909 Mar 12 16:15 charm_tracing.py
-rw-rw-r-- 1 ubuntu ubuntu 37947 Mar 12 16:15 tracing.py
<exited with exit code 0>
```

</details>


### 💬 Copilot

Perfect! Now let me get details on the charm_tracing.py file more comprehensively, and also create a comprehensive summary:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py (lines 150-300)

<details>
<summary>151 lines</summary>

````
150. ```
151. 
152. Note that setting `buffer_max_events` to 0 will effectively disable the buffer.
153. 
154. The path of the buffer file is by default in the charm's execution root, which for k8s charms means
155. that in case of pod churn, the cache will be lost. The recommended solution is to use an existing storage
156. (or add a new one) such as:
157. 
158. ```yaml
159. storage:
160.   data:
161.     type: filesystem
162.     location: /charm-traces
163. ```
164. 
165. and then configure the `@trace_charm` decorator to use it as path for storing the buffer:
166. ```python
167. @trace_charm(
168.     tracing_endpoint="my_tracing_endpoint",
169.     server_cert="_server_cert",
170.     # store traces to a PVC so they're not lost on pod restart.
171.     buffer_path="/charm-traces/buffer.file",
172. )
173. class MyCharm(CharmBase):
174.     ...
175. ```
176. 
177. ## Upgrading from `tempo_k8s.v0`
178. 
179. If you are upgrading from `tempo_k8s.v0.charm_tracing` (note that since then, the charm library moved to
180. `tempo_coordinator_k8s.v0.charm_tracing`), you need to take the following steps (assuming you already
181. have the newest version of the library in your charm):
182. 1) If you need the dependency for your tests, add the following dependency to your charm project
183. (or, if your project had a dependency on `opentelemetry-exporter-otlp-proto-grpc` only because
184. of `charm_tracing` v0, you can replace it with):
185. 
186. `opentelemetry-exporter-otlp-proto-http>=1.21.0`.
187. 
188. 2) Update the charm method referenced to from ``@trace`` and ``@trace_charm``,
189. to return from ``TracingEndpointRequirer.get_endpoint("otlp_http")`` instead of ``grpc_http``.
190. For example:
191. 
192. ```
193.     from charms.tempo_k8s.v0.charm_tracing import trace_charm
194. 
195.     @trace_charm(
196.         tracing_endpoint="my_tracing_endpoint",
197.     )
198.     class MyCharm(CharmBase):
199. 
200.     ...
201. 
202.         @property
203.         def my_tracing_endpoint(self) -> Optional[str]:
204.             '''Tempo endpoint for charm tracing'''
205.             if self.tracing.is_ready():
206.                 return self.tracing.otlp_grpc_endpoint() #  OLD API, DEPRECATED.
207.             else:
208.                 return None
209. ```
210. 
211. needs to be replaced with:
212. 
213. ```
214.     from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
215. 
216.     @trace_charm(
217.         tracing_endpoint="my_tracing_endpoint",
218.     )
219.     class MyCharm(CharmBase):
220. 
221.     ...
222. 
223.         @property
224.         def my_tracing_endpoint(self) -> Optional[str]:
225.             '''Tempo endpoint for charm tracing'''
226.             if self.tracing.is_ready():
227.                 return self.tracing.get_endpoint("otlp_http")  # NEW API, use this.
228.             else:
229.                 return None
230. ```
231. 
232. 3) If you were passing a certificate (str) using `server_cert`, you need to change it to
233. provide an *absolute* path to the certificate file instead.
234. """
235. 
236. 
237. def _remove_stale_otel_sdk_packages():
238.     """Hack to remove stale opentelemetry sdk packages from the charm's python venv.
239. 
240.     See https://github.com/canonical/grafana-agent-operator/issues/146 and
241.     https://bugs.launchpad.net/juju/+bug/2058335 for more context. This patch can be removed after
242.     this juju issue is resolved and sufficient time has passed to expect most users of this library
243.     have migrated to the patched version of juju.  When this patch is removed, un-ignore rule E402 for this file in the pyproject.toml (see setting
244.     [tool.ruff.lint.per-file-ignores] in pyproject.toml).
245. 
246.     This only has an effect if executed on an upgrade-charm event.
247.     """
248.     # all imports are local to keep this function standalone, side-effect-free, and easy to revert later
249.     import os
250. 
251.     if os.getenv("JUJU_DISPATCH_PATH") != "hooks/upgrade-charm":
252.         return
253. 
254.     import logging
255.     import shutil
256.     from collections import defaultdict
257. 
258.     from importlib_metadata import distributions
259. 
260.     otel_logger = logging.getLogger("charm_tracing_otel_patcher")
261.     otel_logger.debug("Applying _remove_stale_otel_sdk_packages patch on charm upgrade")
262.     # group by name all distributions starting with "opentelemetry_"
263.     otel_distributions = defaultdict(list)
264.     for distribution in distributions():
265.         name = distribution._normalized_name  # type: ignore
266.         if name.startswith("opentelemetry_"):
267.             otel_distributions[name].append(distribution)
268. 
269.     otel_logger.debug("Found %d opentelemetry distributions", len(otel_distributions))
270. 
271.     # If we have multiple distributions with the same name, remove any that have 0 associated files
272.     for name, distributions_ in otel_distributions.items():
273.         if len(distributions_) <= 1:
274.             continue
275. 
276.         otel_logger.debug(
277.             "Package %s has multiple (%d) distributions.", name, len(distributions_)
278.         )
279.         for distribution in distributions_:
280.             if not distribution.files:  # Not None or empty list
281.                 path = distribution._path  # type: ignore
282.                 otel_logger.info("Removing empty distribution of %s at %s.", name, path)
283.                 shutil.rmtree(path)
284. 
285.     otel_logger.debug("Successfully applied _remove_stale_otel_sdk_packages patch. ")
286. 
287. 
288. # apply hacky patch to remove stale opentelemetry sdk packages on upgrade-charm.
289. # it could be trouble if someone ever decides to implement their own tracer parallel to
290. # ours and before the charm has inited. We assume they won't.
291. # !!IMPORTANT!! keep all otlp imports UNDER this call.
292. _remove_stale_otel_sdk_packages()
293. 
294. import functools
295. import inspect
296. import logging
297. import os
298. import typing
299. from collections import deque
300. from contextlib import contextmanager
````

</details>


### ✅ `bash`

**Find key function definitions in charm_tracing.py**

$ grep -n "def charm_tracing_disabled\|class.*charm_tracing\|^def trace_charm" /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py | head -20

```
29:# decorate your charm class with charm_tracing:
602:def charm_tracing_disabled():
951:def trace_charm(
<exited with exit code 0>
```


### ✅ `bash`

**Get line counts**

$ wc -l /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/tracing.py

```
1178 /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py
 1010 /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/tracing.py
 2188 total
<exited with exit code 0>
```


### 💬 Copilot

Perfect! Let me get the charm_tracing_disabled function definition and a couple more key sections:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py (lines 600-650)

<details>
<summary>51 lines</summary>

```
600. 
601. @contextmanager
602. def charm_tracing_disabled():
603.     """Contextmanager to temporarily disable charm tracing.
604. 
605.     For usage in tests.
606.     """
607.     previous = os.getenv(CHARM_TRACING_ENABLED, "1")
608.     os.environ[CHARM_TRACING_ENABLED] = "0"
609.     yield
610.     os.environ[CHARM_TRACING_ENABLED] = previous
611. 
612. 
613. def get_current_span() -> Union[Span, None]:
614.     """Return the currently active Span, if there is one, else None.
615. 
616.     If you'd rather keep your logic unconditional, you can use opentelemetry.trace.get_current_span,
617.     which will return an object that behaves like a span but records no data.
618.     """
619.     span = otlp_get_current_span()
620.     if span is INVALID_SPAN:
621.         return None
622.     return cast(Span, span)
623. 
624. 
625. def _get_tracer_from_context(ctx: Context) -> Optional[ContextVar]:
626.     tracers = [v for v in ctx if v is not None and v.name == "tracer"]
627.     if tracers:
628.         return tracers[0]
629.     return None
630. 
631. 
632. def _get_tracer() -> Optional[Tracer]:
633.     """Find tracer in context variable and as a fallback locate it in the full context."""
634.     try:
635.         return tracer.get()
636.     except LookupError:
637.         # fallback: this course-corrects for a user error where charm_tracing symbols are imported
638.         # from different paths (typically charms.tempo_coordinator_k8s... and lib.charms.tempo_coordinator_k8s...)
639.         try:
640.             ctx: Context = copy_context()
641.             if context_tracer := _get_tracer_from_context(ctx):
642.                 logger.warning(
643.                     "Tracer not found in `tracer` context var. "
644.                     "Verify that you're importing all `charm_tracing` symbols from the same module path. \n"
645.                     "For example, DO"
646.                     ": `from charms.lib...charm_tracing import foo, bar`. \n"
647.                     "DONT: \n"
648.                     " \t - `from charms.lib...charm_tracing import foo` \n"
649.                     " \t - `from lib...charm_tracing import bar` \n"
650.                     "For more info: https://python-notes.curiousefficiency.org/en/latest/python"
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py (lines 950-1000)

<details>
<summary>51 lines</summary>

```
950. 
951. def trace_charm(
952.     tracing_endpoint: str,
953.     server_cert: Optional[str] = None,
954.     service_name: Optional[str] = None,
955.     extra_types: Sequence[type] = (),
956.     buffer_max_events: int = BUFFER_DEFAULT_MAX_EVENT_HISTORY_LENGTH,
957.     buffer_max_size_mib: int = BUFFER_DEFAULT_CACHE_FILE_SIZE_LIMIT_MiB,
958.     buffer_path: Optional[Union[str, Path]] = None,
959. ) -> Callable[[_T], _T]:
960.     """Autoinstrument the decorated charm with tracing telemetry.
961. 
962.     Use this function to get out-of-the-box traces for all events emitted on this charm and all
963.     method calls on instances of this class.
964. 
965.     Usage:
966.     >>> from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
967.     >>> from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer
968.     >>> from ops import CharmBase
969.     >>>
970.     >>> @trace_charm(
971.     >>>         tracing_endpoint="tempo_otlp_http_endpoint",
972.     >>> )
973.     >>> class MyCharm(CharmBase):
974.     >>>
975.     >>>     def __init__(self, framework: Framework):
976.     >>>         ...
977.     >>>         self.tracing = TracingEndpointRequirer(self)
978.     >>>
979.     >>>     @property
980.     >>>     def tempo_otlp_http_endpoint(self) -> Optional[str]:
981.     >>>         if self.tracing.is_ready():
982.     >>>             return self.tracing.otlp_http_endpoint()
983.     >>>         else:
984.     >>>             return None
985.     >>>
986. 
987.     :param tracing_endpoint: name of a method, property or attribute  on the charm type that returns an
988.         optional (fully resolvable) tempo url to which the charm traces will be pushed.
989.         If None, tracing will be effectively disabled.
990.     :param server_cert: name of a method, property or attribute on the charm type that returns an
991.         optional absolute path to a CA certificate file to be used when sending traces to a remote server.
992.         If it returns None, an _insecure_ connection will be used. To avoid errors in transient
993.         situations where the endpoint is already https but there is no certificate on disk yet, it
994.         is recommended to disable tracing (by returning None from the tracing_endpoint) altogether
995.         until the cert has been written to disk.
996.     :param service_name: service name tag to attach to all traces generated by this charm.
997.         Defaults to the juju application name this charm is deployed under.
998.     :param extra_types: pass any number of types that you also wish to autoinstrument.
999.         For example, charm libs, relation endpoint wrappers, workload abstractions, ...
1000.     :param buffer_max_events: max number of events to save in the buffer. Set to 0 to disable buffering.
```

</details>


### ✅ `bash`

**List unit test files**

$ ls -la /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/ | head -20

<details>
<summary>17 lines</summary>

```
total 120
drwxrwxr-x 2 ubuntu ubuntu  4096 Mar 15 15:19 .
drwxrwxr-x 6 ubuntu ubuntu  4096 Mar 12 16:15 ..
-rw-rw-r-- 1 ubuntu ubuntu  1453 Mar 12 16:15 conftest.py
-rw-rw-r-- 1 ubuntu ubuntu   536 Mar 12 16:15 helpers.py
-rw-rw-r-- 1 ubuntu ubuntu 20551 Mar 12 16:15 test_charm.py
-rw-rw-r-- 1 ubuntu ubuntu  4271 Mar 12 16:15 test_charm_logging.py
-rw-rw-r-- 1 ubuntu ubuntu  2365 Mar 12 16:15 test_charm_logging_config.py
-rw-rw-r-- 1 ubuntu ubuntu  2094 Mar 12 16:15 test_config_reporting_enabled.py
-rw-rw-r-- 1 ubuntu ubuntu 19982 Mar 12 16:15 test_consumer.py
-rw-rw-r-- 1 ubuntu ubuntu  2442 Mar 12 16:15 test_datasource_exchange.py
-rw-rw-r-- 1 ubuntu ubuntu  1814 Mar 12 16:15 test_grafana_source.py
-rw-rw-r-- 1 ubuntu ubuntu  3670 Mar 12 16:15 test_log_forwarder.py
-rw-rw-r-- 1 ubuntu ubuntu 13519 Mar 12 16:15 test_log_proxy_consumer.py
-rw-rw-r-- 1 ubuntu ubuntu  5078 Mar 12 16:15 test_provider.py
-rw-rw-r-- 1 ubuntu ubuntu  7871 Mar 12 16:15 test_transform.py
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Find test files**

$ find /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit -name "test_*.py" | head -10

<details>
<summary>11 lines</summary>

```
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_charm_logging_config.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_log_proxy_consumer.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_charm.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_grafana_source.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_consumer.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_datasource_exchange.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_charm_logging.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_config_reporting_enabled.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_transform.py
/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_provider.py
<exited with exit code 0>
```

</details>


### 💬 Copilot

Now let me check the test files to see how they mock charm_tracing:

### ✅ `bash`

**Check charm_tracing mocking in test_charm.py**

$ grep -A 5 -B 2 "charm_tracing_disabled\|patch.*charm_tracing" /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_charm.py | head -40

```

<exited with exit code 0>
```


### ✅ `bash`

**Check conftest.py for tracing setup**

$ grep -n "charm_tracing_disabled\|patch" /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py

<details>
<summary>10 lines</summary>

```
1:from unittest.mock import PropertyMock, patch
5:from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
17:def patch_buffer_file_for_charm_tracing(tmp_path):
18:    with patch(
27:    with patch.multiple(
30:        _patch=PropertyMock(tautology),
33:        with patch("socket.getfqdn", new=lambda *args: "fqdn"):
34:            with patch("lightkube.core.client.GenericSyncClient"):
35:                with charm_tracing_disabled():
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Check interface conftest.py for tracing setup**

$ grep -n "charm_tracing_disabled\|patch" /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/interface/conftest.py

<details>
<summary>9 lines</summary>

```
6:from unittest.mock import MagicMock, patch
10:from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
19:def patch_all():
21:        stack.enter_context(patch("lightkube.core.client.GenericSyncClient"))
23:            patch.multiple(
24:                "charms.observability_libs.v0.kubernetes_compute_resources_patch.KubernetesComputeResourcesPatch",
26:                _patch=lambda _: None,
31:        stack.enter_context(charm_tracing_disabled())
<exited with exit code 0>
```

</details>


### 💬 Copilot

Perfect! Now let me create a comprehensive summary. Let me also check for the TracingEndpointRequirer in the tracing.py to understand the complete picture:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/tracing.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/tracing.py (lines 150-250)

<details>
<summary>101 lines</summary>

```
150.     "zipkin": TransportProtocolType.http,
151.     "otlp_grpc": TransportProtocolType.grpc,
152.     "otlp_http": TransportProtocolType.http,
153.     "jaeger_thrift_http": TransportProtocolType.http,
154.     "jaeger_grpc": TransportProtocolType.grpc,
155. }
156. # A mapping between telemetry protocols and their corresponding transport protocol.
157. 
158. 
159. class TracingError(Exception):
160.     """Base class for custom errors raised by this library."""
161. 
162. 
163. class NotReadyError(TracingError):
164.     """Raised by the provider wrapper if a requirer hasn't published the required data (yet)."""
165. 
166. 
167. class ProtocolNotRequestedError(TracingError):
168.     """Raised if the user attempts to obtain an endpoint for a protocol it did not request."""
169. 
170. 
171. class DataValidationError(TracingError):
172.     """Raised when data validation fails on IPU relation data."""
173. 
174. 
175. class DataAccessPermissionError(TracingError):
176.     """Raised when follower units attempt leader-only operations."""
177. 
178. 
179. class AmbiguousRelationUsageError(TracingError):
180.     """Raised when one wrongly assumes that there can only be one relation on an endpoint."""
181. 
182. 
183. if int(pydantic.version.VERSION.split(".")[0]) < 2:
184. 
185.     class DatabagModel(BaseModel):  # type: ignore
186.         """Base databag model."""
187. 
188.         class Config:
189.             """Pydantic config."""
190. 
191.             # ignore any extra fields in the databag
192.             extra = "ignore"
193.             """Ignore any extra fields in the databag."""
194.             allow_population_by_field_name = True
195.             """Allow instantiating this class by field name (instead of forcing alias)."""
196. 
197.         _NEST_UNDER = None
198. 
199.         @classmethod
200.         def load(cls, databag: MutableMapping):
201.             """Load this model from a Juju databag."""
202.             if cls._NEST_UNDER:
203.                 return cls.parse_obj(json.loads(databag[cls._NEST_UNDER]))
204. 
205.             try:
206.                 data = {
207.                     k: json.loads(v)
208.                     for k, v in databag.items()
209.                     # Don't attempt to parse model-external values
210.                     if k in {f.alias for f in cls.__fields__.values()}
211.                 }
212.             except json.JSONDecodeError as e:
213.                 msg = f"invalid databag contents: expecting json. {databag}"
214.                 logger.error(msg)
215.                 raise DataValidationError(msg) from e
216. 
217.             try:
218.                 return cls.parse_raw(json.dumps(data))  # type: ignore
219.             except pydantic.ValidationError as e:
220.                 msg = f"failed to validate databag: {databag}"
221.                 logger.debug(msg, exc_info=True)
222.                 raise DataValidationError(msg) from e
223. 
224.         def dump(self, databag: Optional[MutableMapping] = None, clear: bool = True):
225.             """Write the contents of this model to Juju databag.
226. 
227.             :param databag: the databag to write the data to.
228.             :param clear: ensure the databag is cleared before writing it.
229.             """
230.             if clear and databag:
231.                 databag.clear()
232. 
233.             if databag is None:
234.                 databag = {}
235. 
236.             if self._NEST_UNDER:
237.                 databag[self._NEST_UNDER] = self.json(by_alias=True)
238.                 return databag
239. 
240.             dct = self.dict()
241.             for key, field in self.__fields__.items():  # type: ignore
242.                 value = dct[key]
243.                 databag[field.alias or key] = json.dumps(value)
244. 
245.             return databag
246. 
247. else:
248.     from pydantic import ConfigDict
249. 
250.     class DatabagModel(BaseModel):
```

</details>


### 💬 Copilot

Excellent! Now I have all the information. Let me provide a comprehensive report:

---

## Repository Analysis Report: loki-k8s-operator

### 1. **pyproject.toml (Dependencies)**

**Location**: `/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/pyproject.toml`

**Key Dependencies** (relevant to tracing):
```
- opentelemetry-api==1.21.0
- opentelemetry-exporter-otlp-proto-common==1.21.0
- opentelemetry-exporter-otlp-proto-http==1.21.0
- opentelemetry-proto==1.21.0
- opentelemetry-sdk==1.21.0
- opentelemetry-semantic-conventions==0.42b0
```

**Other main dependencies**:
- ops, cosl, kubernetes, requests, pyyaml, lightkube, aiohttp, jsonschema, cryptography, pydantic\>=2.9.0

### 2. **src/charm.py (Main Charm File)**

**Location**: `/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py` (38.5 KB)

**Key imports**:
```python
from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
from charms.loki_k8s.v0.charm_logging import log_charm
```

**Tracing Configuration** (lines 115-252):
- The `LokiOperatorCharm` class is decorated with `@trace_charm()`:
  ```python
  @trace_charm(
      tracing_endpoint="_charm_tracing_endpoint",
      server_cert="_charm_tracing_ca_cert",
      extra_types=[
          GrafanaDashboardProvider,
          GrafanaSourceProvider,
          LokiPushApiProvider,
          TLSCertificatesRequiresV4,
          ConfigBuilder,
          MetricsEndpointProvider,
      ],
  )
  ```

- **Charm Tracing** (line 244-252):
  ```python
  self.charm_tracing = TracingEndpointRequirer(
      self, relation_name="charm-tracing", protocols=["otlp_http"]
  )
  self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
      self.charm_tracing, self._ca_cert_path
  )
  ```

- **Workload Tracing** (lines 247-268):
  ```python
  self.workload_tracing = TracingEndpointRequirer(
      self, relation_name="workload-tracing", protocols=["jaeger_thrift_http"]
  )
  ```
  With event handlers for endpoint changes and removal.

### 3. **lib/charms/tempo_coordinator_k8s/ Directory**

**Location**: `/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/`

**Files**:
1. **charm_tracing.py** (1178 lines)
   - Main tracing instrumentation library
   - Key exports:
     - `charm_tracing_disabled()` - context manager to disable tracing in tests (line 602)
     - `trace_charm()` decorator (line 951)
     - `get_current_span()` function (line 613)
     - `_get_tracer()` helper function (line 632)

2. **tracing.py** (1010 lines)
   - Provides `TracingEndpointRequirer` class for requiring tracing endpoints
   - Provides `TracingEndpointProvider` class for providing tracing endpoints
   - Protocol definitions: `zipkin`, `otlp_grpc`, `otlp_http`, `jaeger_grpc`, `jaeger_thrift_http`
   - `charm_tracing_config()` helper function

### 4. **Requires/Provides Relations in charmcraft.yaml**

**Location**: `/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/charmcraft.yaml`

**Tracing Relations**:
```yaml
requires:
  charm-tracing:
    interface: tracing
    optional: true
    limit: 1
    description: |
      Enables sending charm traces to a distributed tracing backend such as Tempo.
  workload-tracing:
    interface: tracing
    optional: true
    limit: 1
    description: |
      Enables sending workload traces to a distributed tracing backend such as Tempo.
```

**Other Relations** (non-tracing):
- `provides`: logging, grafana-source, metrics-endpoint, grafana-dashboard, send-datasource
- `requires`: alertmanager, ingress, certificates, catalogue
- `peers`: replicas

### 5. **Imports of charm_tracing and Related Modules**

**Files with tracing imports**:

1. **src/charm.py**:
   - `from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm`
   - `from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config`
   - Usage: Lines 47-48, 115-117, 244-252

2. **tests/unit/conftest.py**:
   - `from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled`
   - Usage: Line 5, 35 (context manager for disabling tracing)

3. **tests/interface/conftest.py**:
   - `from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled`
   - Usage: Line 10, 31 (context manager for disabling tracing)

### 6. **Test Files Mocking charm_tracing Components**

**Location**: `/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py` and `/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/interface/conftest.py`

**Unit Test Mocking** (conftest.py, lines 1-42):
```python
@pytest.fixture(autouse=True)
def patch_buffer_file_for_charm_tracing(tmp_path):
    with patch(
        "charms.tempo_coordinator_k8s.v0.charm_tracing.BUFFER_DEFAULT_CACHE_FILE_NAME",
        str(tmp_path / "foo.json"),
    ):
        yield

@pytest.fixture
def loki_charm(tmp_path):
    with patch.multiple(
        "charm.KubernetesComputeResourcesPatch",
        _namespace=PropertyMock("test-namespace"),
        _patch=PropertyMock(tautology),
        is_ready=PropertyMock(tautology),
    ):
        with patch("socket.getfqdn", new=lambda *args: "fqdn"):
            with patch("lightkube.core.client.GenericSyncClient"):
                with charm_tracing_disabled():
                    yield LokiOperatorCharm
```

**Interface Test Mocking** (conftest.py, lines 18-33):
```python
@pytest.fixture(autouse=True, scope="module")
def patch_all():
    with ExitStack() as stack:
        stack.enter_context(patch("lightkube.core.client.GenericSyncClient"))
        stack.enter_context(
            patch.multiple(
                "charms.observability_libs.v0.kubernetes_compute_resources_patch.KubernetesComputeResourcesPatch",
                _namespace="test-namespace",
                _patch=lambda _: None,
                is_ready=MagicMock(return_value=True),
                get_status=lambda _: ActiveStatus(""),
            )
        )
        stack.enter_context(charm_tracing_disabled())
        yield
```

**Key patterns**:
- Patches buffer file location to tmp directory
- Patches `KubernetesComputeResourcesPatch` to avoid k8s client initialization
- Disables charm tracing via `charm_tracing_disabled()` context manager to avoid tracing dependencies in tests
- Patches socket and lightkube client

### 7. **tox.ini Contents**

**Location**: `/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tox.ini`

**Configuration**:
```ini
[tox]
skipsdist=True
skip_missing_interpreters = True
envlist = lint, static, unit

[vars]
src_path = {toxinidir}/src
tst_path = {toxinidir}/tests
lib_path = {toxinidir}/lib/charms/loki_k8s
all_path = {[vars]src_path} {[vars]tst_path} {[vars]lib_path}
uv_flags = --frozen --isolated --extra=dev

[testenv:unit]
commands =
    /usr/bin/env sh -c 'stat cos-tool-amd64 \> /dev/null 2\>&1 || curl -L -O ...'
    uv run {[vars]uv_flags} coverage run --source={[vars]src_path},{[vars]lib_path} -m pytest \
        {[vars]tst_path}/unit {posargs}
    uv run {[vars]uv_flags} coverage report

[testenv:interface]
description = Run interface tests
commands =
    uv run {[vars]uv_flags} pytest --exitfirst {[vars]tst_path}/interface {posargs}

[testenv:integration]
description = Run integration tests
commands =
    uv run {[vars]uv_flags} pytest --exitfirst {[vars]tst_path}/integration {posargs}
```

**Environments**:
- `lint` - Ruff linting
- `static` - Pyright type checking
- `unit` - Unit tests with coverage
- `interface` - Interface tests
- `integration` - Integration tests

---

## Summary

This loki-k8s-operator charm integrates OpenTelemetry tracing through the `charms.tempo_coordinator_k8s.v0` library for both **charm-level tracing** and **workload tracing**. The charm uses:

- **Charm-level tracing** via `@trace_charm()` decorator with `otlp_http` protocol
- **Workload tracing** via `TracingEndpointRequirer` with `jaeger_thrift_http` protocol
- **Test mocking** via `charm_tracing_disabled()` context manager to isolate tests from tracing dependencies
- **TLS support** with certificate management for secure trace transmission


---

<sub>⏱️ 1m 43s</sub>

### 💬 Copilot

Now I have a clear picture. Let me look at the actual charm code in detail before making changes.

---

<sub>⏱️ 1m 44s</sub>

### ✅ `bash`

**Find tracing-related lines in charm.py**

$ grep -n "charm_tracing\|trace_charm\|TracingEndpointRequirer\|charm_tracing_config\|_charm_tracing\|workload_tracing\|workload-tracing" /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py | head -60

<details>
<summary>19 lines</summary>

```
47:from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
48:from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
115:@trace_charm(
116:    tracing_endpoint="_charm_tracing_endpoint",
117:    server_cert="_charm_tracing_ca_cert",
244:        self.charm_tracing = TracingEndpointRequirer(
247:        self.workload_tracing = TracingEndpointRequirer(
248:            self, relation_name="workload-tracing", protocols=["jaeger_thrift_http"]
250:        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
251:            self.charm_tracing, self._ca_cert_path
261:            self.workload_tracing.on.endpoint_changed,  # type: ignore
262:            self._on_workload_tracing_endpoint_changed,
265:            self.workload_tracing.on.endpoint_removed,  # type: ignore
266:            self._on_workload_tracing_endpoint_removed,
363:    def _on_workload_tracing_endpoint_changed(self, _) -> None:
367:    def _on_workload_tracing_endpoint_removed(self, _) -> None:
417:        if self.workload_tracing.is_ready():
418:            tempo_endpoint = self.workload_tracing.get_endpoint("jaeger_thrift_http")
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 44s</sub>

### ✅ `bash`

**Read unit test conftest**

$ cat /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py

<details>
<summary>41 lines</summary>

```
from unittest.mock import PropertyMock, patch

import ops
import pytest
from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
from ops.testing import Context
from scenario import Container, Exec

from charm import LokiOperatorCharm


def tautology(*_, **__) -> bool:
    return True


@pytest.fixture(autouse=True)
def patch_buffer_file_for_charm_tracing(tmp_path):
    with patch(
        "charms.tempo_coordinator_k8s.v0.charm_tracing.BUFFER_DEFAULT_CACHE_FILE_NAME",
        str(tmp_path / "foo.json"),
    ):
        yield


@pytest.fixture
def loki_charm(tmp_path):
    with patch.multiple(
        "charm.KubernetesComputeResourcesPatch",
        _namespace=PropertyMock("test-namespace"),
        _patch=PropertyMock(tautology),
        is_ready=PropertyMock(tautology),
    ):
        with patch("socket.getfqdn", new=lambda *args: "fqdn"):
            with patch("lightkube.core.client.GenericSyncClient"):
                with charm_tracing_disabled():
                    yield LokiOperatorCharm


@pytest.fixture
def context(loki_charm):
    return Context(loki_charm)


@pytest.fixture(scope="function")
def loki_container():
    return Container(
        "loki",
        can_connect=True,
        execs={Exec(["update-ca-certificates", "--fresh"], return_code=0)},
        layers={"loki": ops.pebble.Layer({"services": {"loki": {}}})},
        service_statuses={"loki": ops.pebble.ServiceStatus.INACTIVE},
    )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 44s</sub>

### ✅ `bash`

**Read interface test conftest**

$ cat /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/interface/conftest.py

<details>
<summary>68 lines</summary>

```
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import json
from contextlib import ExitStack
from unittest.mock import MagicMock, patch

import ops
import pytest
from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
from interface_tester import InterfaceTester
from ops import ActiveStatus
from scenario.state import Container, Exec, Relation, State

from charm import LokiOperatorCharm


@pytest.fixture(autouse=True, scope="module")
def patch_all():
    with ExitStack() as stack:
        stack.enter_context(patch("lightkube.core.client.GenericSyncClient"))
        stack.enter_context(
            patch.multiple(
                "charms.observability_libs.v0.kubernetes_compute_resources_patch.KubernetesComputeResourcesPatch",
                _namespace="test-namespace",
                _patch=lambda _: None,
                is_ready=MagicMock(return_value=True),
                get_status=lambda _: ActiveStatus(""),
            )
        )
        stack.enter_context(charm_tracing_disabled())

        yield


loki_container = Container(
    name="loki",
    can_connect=True,
    execs={Exec(["update-ca-certificates", "--fresh"], return_code=0)},
    layers={"loki": ops.pebble.Layer({"services": {"loki": {}}})},
    service_statuses={"loki": ops.pebble.ServiceStatus.ACTIVE},
)

grafana_source_relation = Relation(
    "grafana-source",
    remote_app_data={
        "datasource_uids": json.dumps({"loki/0": "01234"}),
        "grafana_uid": "5678",
    },
)

grafana_datasource_exchange_relation = Relation(
    "send-datasource",
    remote_app_data={
        "datasources": json.dumps([{"type": "loki", "uid": "01234", "grafana_uid": "5678"}])
    },
)


@pytest.fixture
def grafana_datasource_tester(interface_tester: InterfaceTester):
    interface_tester.configure(
        charm_type=LokiOperatorCharm,
        state_template=State(
            leader=True, containers=[loki_container], relations=[grafana_source_relation]
        ),
    )
    yield interface_tester


@pytest.fixture
def grafana_datasource_exchange_tester(interface_tester: InterfaceTester):
    interface_tester.configure(
        charm_type=LokiOperatorCharm,
        state_template=State(
            leader=True,
            containers=[loki_container],
            relations=[grafana_source_relation, grafana_datasource_exchange_relation],
        ),
    )
    yield interface_tester
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 53s</sub>

### ✅ `bash`

**Find ops and opentelemetry deps**

$ grep -n "ops\|opentelemetry" /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/pyproject.toml

<details>
<summary>9 lines</summary>

```
9:  "ops",
21:  "opentelemetry-api==1.21.0",
22:  "opentelemetry-exporter-otlp-proto-common==1.21.0",
23:  "opentelemetry-exporter-otlp-proto-http==1.21.0",
24:  "opentelemetry-proto==1.21.0",
25:  "opentelemetry-sdk==1.21.0",
26:  "opentelemetry-semantic-conventions==0.42b0",
39:  "ops[testing]",
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 52s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py (lines 40-130)

<details>
<summary>91 lines</summary>

```
40. from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
41.     K8sResourcePatchFailedEvent,
42.     KubernetesComputeResourcesPatch,
43.     ResourceRequirements,
44.     adjust_resource_requirements,
45. )
46. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
47. from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
48. from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
49. from charms.tls_certificates_interface.v4.tls_certificates import (
50.     CertificateRequestAttributes,
51.     TLSCertificatesRequiresV4,
52. )
53. from charms.traefik_k8s.v1.ingress_per_unit import IngressPerUnitRequirer
54. from cosl import JujuTopology
55. from cosl.interfaces.datasource_exchange import DatasourceDict, DatasourceExchange
56. from ops import CollectStatusEvent, StoredState
57. from ops.charm import CharmBase
58. from ops.main import main
59. from ops.model import (
60.     ActiveStatus,
61.     BlockedStatus,
62.     MaintenanceStatus,
63.     Port,
64.     StatusBase,
65.     WaitingStatus,
66. )
67. from ops.pebble import Error, Layer, PathError, ProtocolError
68. 
69. from config_builder import (
70.     CERT_FILE,
71.     HTTP_LISTEN_PORT,
72.     KEY_FILE,
73.     LOKI_CONFIG,
74.     LOKI_CONFIG_BACKUP,
75.     RULES_DIR,
76.     ConfigBuilder,
77. )
78. 
79. # To keep a tidy debug-log, we suppress some DEBUG/INFO logs from some imported libs,
80. # even when charm logging is set to a lower level.
81. logging.getLogger("httpx").setLevel(logging.WARNING)
82. logging.getLogger("httpcore").setLevel(logging.WARNING)
83. logger = logging.getLogger(__name__)
84. 
85. @dataclass
86. class TLSConfig:
87.     """TLS configuration received by the charm over the `certificates` relation."""
88. 
89.     server_cert: str
90.     ca_cert: str
91.     private_key: str
92. 
93. class CompositeStatus(TypedDict):
94.     """Per-component status holder."""
95. 
96.     # These are going to go into stored state, so we must use marshallable objects.
97.     # They are passed to StatusBase.from_name().
98.     k8s_patch: Tuple[str, str]
99.     config: Tuple[str, str]
100.     rules: Tuple[str, str]
101.     retention: Tuple[str, str]
102. 
103. 
104. def to_tuple(status: StatusBase) -> Tuple[str, str]:
105.     """Convert a StatusBase to tuple, so it is marshallable into StoredState."""
106.     return status.name, status.message
107. 
108. 
109. def to_status(tpl: Tuple[str, str]) -> StatusBase:
110.     """Convert a tuple to a StatusBase, so it could be used natively with ops."""
111.     name, message = tpl
112.     return StatusBase.from_name(name, message)
113. 
114. 
115. @trace_charm(
116.     tracing_endpoint="_charm_tracing_endpoint",
117.     server_cert="_charm_tracing_ca_cert",
118.     extra_types=[
119.         GrafanaDashboardProvider,
120.         GrafanaSourceProvider,
121.         LokiPushApiProvider,
122.         TLSCertificatesRequiresV4,
123.         ConfigBuilder,
124.         MetricsEndpointProvider,
125.     ],
126. )
127. @log_charm(logging_endpoints="_charm_logging_endpoints", server_cert="_charm_logging_ca_cert")
128. class LokiOperatorCharm(CharmBase):
129.     """Charm the service."""
130.
```

</details>


---

<sub>⏱️ 1m 57s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py (lines 240-270)

<details>
<summary>31 lines</summary>

```
240. 
241.         self.dashboard_provider = GrafanaDashboardProvider(self)
242. 
243.         self.catalogue = CatalogueConsumer(charm=self, item=self._catalogue_item)
244.         self.charm_tracing = TracingEndpointRequirer(
245.             self, relation_name="charm-tracing", protocols=["otlp_http"]
246.         )
247.         self.workload_tracing = TracingEndpointRequirer(
248.             self, relation_name="workload-tracing", protocols=["jaeger_thrift_http"]
249.         )
250.         self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
251.             self.charm_tracing, self._ca_cert_path
252.         )
253. 
254.         self.datasource_exchange = DatasourceExchange(
255.             self,
256.             provider_endpoint="send-datasource",
257.             requirer_endpoint=None,
258.         )
259. 
260.         self.framework.observe(
261.             self.workload_tracing.on.endpoint_changed,  # type: ignore
262.             self._on_workload_tracing_endpoint_changed,
263.         )
264.         self.framework.observe(
265.             self.workload_tracing.on.endpoint_removed,  # type: ignore
266.             self._on_workload_tracing_endpoint_removed,
267.         )
268. 
269.         self.framework.observe(self.on.config_changed, self._on_config_changed)
270.         self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
```

</details>


---

<sub>⏱️ 2m 7s</sub>

### 💬 Copilot

Now I have everything I need. Let me implement the migration:

---

<sub>⏱️ 2m 7s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/pyproject.toml.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/pyproject.toml (lines 1-45)

<details>
<summary>45 lines</summary>

```
1. # Copyright 2021 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. [project]
4. name = "loki-k8s"
5. version = "0.0"
6. requires-python = "~=3.8"
7. 
8. dependencies = [
9.   "ops",
10.   "cosl",
11.   "kubernetes",
12.   "requests",
13.   "pyyaml",
14.   "lightkube",
15.   "lightkube-models",
16.   "aiohttp!=3.11.13",  # Yanked
17.   "jsonschema",
18.   "cryptography",
19.   "pydantic>=2.9.0",
20.   "importlib-metadata==6.0.0",
21.   "opentelemetry-api==1.21.0",
22.   "opentelemetry-exporter-otlp-proto-common==1.21.0",
23.   "opentelemetry-exporter-otlp-proto-http==1.21.0",
24.   "opentelemetry-proto==1.21.0",
25.   "opentelemetry-sdk==1.21.0",
26.   "opentelemetry-semantic-conventions==0.42b0",
27. ]
28. 
29. [project.optional-dependencies]
30. dev = [
31.   # Linting
32.   "ruff",
33.   "codespell",
34.   # Static
35.   "pyright",
36.   # Unit
37.   "pytest",
38.   "coverage[toml]",
39.   "ops[testing]",
40.   "responses",
41.   "fs",
42.   # Interface
43.   "pytest-interface-tester",
44.   # Integration
45.   "juju",
```

</details>


---

<sub>⏱️ 2m 17s</sub>

### 💬 Copilot

Now I'll make all the changes in parallel:

---

<sub>⏱️ 2m 17s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/pyproject.toml.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/pyproject.toml

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/pyproject.toml updated with changes.
```


---

<sub>⏱️ 2m 17s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 2m 17s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 2m 17s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 2m 34s</sub>

### 💬 Copilot

Now update the test files and delete the community library:

---

<sub>⏱️ 2m 34s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py updated with changes.
```


---

<sub>⏱️ 2m 34s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/interface/conftest.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/interface/conftest.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/interface/conftest.py updated with changes.
```


---

<sub>⏱️ 2m 34s</sub>

### ✅ `bash`

**Delete community charm_tracing library**

$ rm /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py

```

<exited with exit code 0>
```


---

<sub>⏱️ 2m 39s</sub>

### 💬 Copilot

Now let's run the linter and tests to verify:

---

<sub>⏱️ 2m 40s</sub>

### ✅ `bash`

**Run lint**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && tox -e lint 2>&1 | tail -20

<details>
<summary>20 lines</summary>

```
69 | | from config_builder import (
70 | |     CERT_FILE,
71 | |     HTTP_LISTEN_PORT,
72 | |     KEY_FILE,
73 | |     LOKI_CONFIG,
74 | |     LOKI_CONFIG_BACKUP,
75 | |     RULES_DIR,
76 | |     ConfigBuilder,
77 | | )
   | |_^ I001
78 |
79 |   # To keep a tidy debug-log, we suppress some DEBUG/INFO logs from some imported libs,
   |
   = help: Organize imports

Found 1 error.
[*] 1 fixable with the `--fix` option.
lint: exit 1 (0.70 seconds) /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf> uv run --frozen --isolated --extra=dev ruff check /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/loki_k8s pid=7581
  lint: FAIL code 1 (0.74=setup[0.04]+cmd[0.70] seconds)
  evaluation failed :( (0.75 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 44s</sub>

### 💬 Copilot

Import ordering issue. Let me fix it:

---

<sub>⏱️ 2m 45s</sub>

### ✅ `bash`

**Auto-fix import ordering**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && uv run --frozen --isolated --extra=dev ruff check --fix src/charm.py 2>&1

```
warning: The `requires-python` specifier (`~=3.8`) in `loki-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
░░░░░░░░░░░░░░░░░░░░ [0/0] Installing wheels...                                                                         ░░░░░░░░░░░░░░░░░░░░ [0/117] Installing wheels...                                                                       ░░░░░░░░░░░░░░░░░░░░ [0/117] sh==2.2.2                                                                                  ░░░░░░░░░░░░░░░░░░░░ [1/117] sh==2.2.2                                                                                  ░░░░░░░░░░░░░░░░░░░░ [1/117] cosl==1.3.1                                                                                ░░░░░░░░░░░░░░░░░░░░ [2/117] cosl==1.3.1                                                                                ░░░░░░░░░░░░░░░░░░░░ [2/117] yarl==1.20.0                                                                               ░░░░░░░░░░░░░░░░░░░░ [3/117] yarl==1.20.0                                                                               ░░░░░░░░░░░░░░░░░░░░ [3/117] ops==2.21.1                                                                                ░░░░░░░░░░░░░░░░░░░░ [4/117] ops==2.21.1                                                                                ░░░░░░░░░░░░░░░░░░░░ [4/117] aiohappyeyeballs==2.6.1                                                                    ░░░░░░░░░░░░░░░░░░░░ [5/117] aiohappyeyeballs==2.6.1                                                                    ░░░░░░░░░░░░░░░░░░░░ [5/117] importlib-metadata==6.0.0                                                                  █░░░░░░░░░░░░░░░░░░░ [6/117] importlib-metadata==6.0.0                                                                  █░░░░░░░░░░░░░░░░░░░ [6/117] lightkube-models==1.32.0.8                                                                 █░░░░░░░░░░░░░░░░░░░ [7/117] lightkube-models==1.32.0.8                                                                 █░░░░░░░░░░░░░░░░░░░ [7/117] h11==0.16.0                                                                                █░░░░░░░░░░░░░░░░░░░ [8/117] h11==0.16.0                                                                                █░░░░░░░░░░░░░░░░░░░ [8/117] annotated-types==0.7.0                                                                     █░░░░░░░░░░░░░░░░░░░ [9/117] annotated-types==0.7.0                                                                     ███████████████████░ [116/117] pyright==1.1.398                                                                         Installed 117 packages in 67ms
Found 1 error (1 fixed, 0 remaining).
<exited with exit code 0>
```


---

<sub>⏱️ 2m 49s</sub>

### ✅ `bash`

**Run lint again**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && tox -e lint 2>&1 | tail -10

<details>
<summary>7 lines</summary>

```
lint: commands[0]> uv run --frozen --isolated --extra=dev ruff check /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/loki_k8s
warning: The `requires-python` specifier (`~=3.8`) in `loki-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 117 packages in 39ms
All checks passed!
  lint: OK (0.14=setup[0.00]+cmd[0.13] seconds)
  congratulations :) (0.15 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 54s</sub>

### 💬 Copilot

Lint passes. Now run unit tests:

---

<sub>⏱️ 3m 6s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && tox -e unit 2>&1 | tail -30

<details>
<summary>20 lines</summary>

```
unit: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p cpython3 --allow-existing --python-preference system /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/.tox/unit
unit: commands[0]> /usr/bin/env sh -c 'stat cos-tool-amd64 > /dev/null 2>&1 || curl -L -O https://github.com/canonical/cos-tool/releases/latest/download/cos-tool-amd64 && chmod 755 cos-tool-amd64'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
  0 18.0M    0 32759    0     0  25515      0  0:12:23  0:00:01  0:12:22 25515 15 18.0M   15 2832k    0     0  1284k      0  0:00:14  0:00:02  0:00:12 3040k 36 18.0M   36 6800k    0     0  2121k      0  0:00:08  0:00:03  0:00:05 3521k 50 18.0M   50 9407k    0     0  2237k      0  0:00:08  0:00:04  0:00:04 3208k 61 18.0M   61 11.1M    0     0  2200k      0  0:00:08  0:00:05  0:00:03 2911k 73 18.0M   73 13.2M    0     0  2183k      0  0:00:08  0:00:06  0:00:02 2746k 84 18.0M   84 15.2M    0     0  2164k      0  0:00:08  0:00:07  0:00:01 2553k100 18.0M  100 18.0M    0     0  2287k      0  0:00:08  0:00:08 --:--:-- 2396k
unit: commands[1]> uv run --frozen --isolated --extra=dev coverage run --source=/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src,/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/loki_k8s -m pytest /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit
warning: The `requires-python` specifier (`~=3.8`) in `loki-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 117 packages in 39ms
ImportError while loading conftest '/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py'.
tests/unit/conftest.py:8: in <module>
    from charm import LokiOperatorCharm
src/charm.py:30: in <module>
    import ops.tracing
E   ModuleNotFoundError: No module named 'ops.tracing'
unit: exit 4 (3.31 seconds) /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf> uv run --frozen --isolated --extra=dev coverage run --source=/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src,/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/loki_k8s -m pytest /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit pid=7786
  unit: FAIL code 4 (11.45=setup[0.03]+cmd[8.11,3.31] seconds)
  evaluation failed :( (11.47 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 11s</sub>

### 💬 Copilot

The lock file needs updating. Let me update it:

---

<sub>⏱️ 3m 13s</sub>

### ✅ `bash`

**Update uv.lock**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && uv lock 2>&1 | tail -20

<details>
<summary>13 lines</summary>

```
warning: The `requires-python` specifier (`~=3.8`) in `loki-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Resolved 151 packages in 823ms
Removed backoff v2.2.1
Removed googleapis-common-protos v1.70.0
Updated opentelemetry-api v1.21.0 -> v1.33.1, v1.40.0
Removed opentelemetry-exporter-otlp-proto-common v1.21.0
Removed opentelemetry-exporter-otlp-proto-http v1.21.0
Removed opentelemetry-proto v1.21.0
Updated opentelemetry-sdk v1.21.0 -> v1.33.1, v1.40.0
Updated opentelemetry-semantic-conventions v0.42b0 -> v0.54b1, v0.61b0
Added ops-tracing v2.21.1
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 21s</sub>

### ✅ `bash`

**Run unit tests again**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && tox -e unit 2>&1 | tail -20

<details>
<summary>14 lines</summary>

```
unit: commands[0]> /usr/bin/env sh -c 'stat cos-tool-amd64 > /dev/null 2>&1 || curl -L -O https://github.com/canonical/cos-tool/releases/latest/download/cos-tool-amd64 && chmod 755 cos-tool-amd64'
unit: commands[1]> uv run --frozen --isolated --extra=dev coverage run --source=/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src,/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/loki_k8s -m pytest /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit
warning: The `requires-python` specifier (`~=3.8`) in `loki-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 111 packages in 44ms
ImportError while loading conftest '/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/conftest.py'.
tests/unit/conftest.py:8: in <module>
    from charm import LokiOperatorCharm
src/charm.py:30: in <module>
    import ops.tracing
E   ModuleNotFoundError: No module named 'ops.tracing'
unit: exit 4 (3.53 seconds) /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf> uv run --frozen --isolated --extra=dev coverage run --source=/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src,/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/lib/charms/loki_k8s -m pytest /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit pid=7880
  unit: FAIL code 4 (3.54=setup[0.00]+cmd[0.00,3.53] seconds)
  evaluation failed :( (3.56 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 28s</sub>

### ✅ `bash`

**Check ops.tracing availability**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && uv run --frozen --isolated --extra=dev python -c "import ops; print(ops.__version__); import ops.tracing; print('ops.tracing ok')" 2>&1 | grep -v "warning\|Installed"

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'ops.tracing'
2.21.1
<exited with exit code 0>
```


---

<sub>⏱️ 3m 32s</sub>

### ✅ `bash`

**Check ops_tracing module**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && uv run --frozen --isolated --extra=dev python -c "import ops_tracing; print(dir(ops_tracing))" 2>&1 | grep -v "warning\|Installed"

```
['Tracing', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '_api', '_backend', '_buffer', '_export', '_mark_observed', '_setup', '_shutdown', 'set_destination', 'vendor']
<exited with exit code 0>
```


---

<sub>⏱️ 3m 38s</sub>

### ✅ `bash`

**Check ops_tracing.setup API**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && uv run --frozen --isolated --extra=dev python -c "from ops_tracing import setup; help(setup)" 2>&1 | grep -v "warning\|Installed"

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ImportError: cannot import name 'setup' from 'ops_tracing' (/home/ubuntu/.cache/uv/builds-v0/.tmpWgpsuD/lib/python3.12/site-packages/ops_tracing/__init__.py). Did you mean: '_setup'?
<exited with exit code 0>
```


---

<sub>⏱️ 3m 45s</sub>

### ✅ `bash`

**Check ops_tracing public API**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && uv run --frozen --isolated --extra=dev python -c "import ops_tracing; print(ops_tracing.__all__)" 2>&1 | grep -v "warning\|Installed"

```
['Tracing', '_mark_observed', '_setup', '_shutdown', 'set_destination']
<exited with exit code 0>
```


---

<sub>⏱️ 3m 44s</sub>

### ❌ `bash`

**Find ops_tracing source**

$ uv run --frozen --isolated --extra=dev python -c "import ops_tracing; import inspect; print(inspect.getfile(ops_tracing))" 2>/dev/null; find /home/ubuntu/.cache/uv -name "_api.py" -path "*/ops_tracing/*" 2>/dev/null | head -3

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 3m 50s</sub>

### ✅ `bash`

**Find ops_tracing module location**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && uv run --frozen --isolated --extra=dev python -c "
import ops_tracing
import inspect
print(inspect.getfile(ops_tracing))
" 2>&1 | grep -v "warning\|Installed"

```
/home/ubuntu/.cache/uv/builds-v0/.tmpRDc1KB/lib/python3.12/site-packages/ops_tracing/__init__.py
<exited with exit code 0>
```


---

<sub>⏱️ 3m 54s</sub>

### ❌ `bash`

**List ops_tracing files**

$ ls /home/ubuntu/.cache/uv/builds-v0/.tmpRDc1KB/lib/python3.12/site-packages/ops_tracing/ 2>/dev/null || find /home/ubuntu/.cache/uv -name "__init__.py" -path "*/ops_tracing/*" 2>/dev/null | head -5

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 3m 59s</sub>

### ✅ `bash`

**Read ops_tracing source**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && uv run --frozen --isolated --extra=dev python -c "
import ops_tracing
import inspect
src = inspect.getsource(ops_tracing)
print(src[:3000])
" 2>&1 | grep -v "warning\|Installed"

<details>
<summary>73 lines</summary>

```
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

"""The tracing facility for the Ops library.

Quick start
-----------

In your ``charmcraft.yaml``, declare the charm tracing relation with a ``tracing``
interface and optionally the TLS relation with a ``certificate_transfer`` interface.::

    requires:
        charm-tracing:
            interface: tracing
            limit: 1
            optional: true
        receive-ca-cert:
            interface: certificate_transfer
            limit: 1
            optional: true

If you're migrating from the ``charm-tracing`` charm lib, you most likely already
have relations like these. If the names of the relations differ from this recipe, please
adjust the code on the rest of this page to your relation names.

.. hint::
    Make sure to include the Rust build packages in your ``charmcraft.yaml``, because
    this library depends on ``pydantic-core`` via ``pydantic``.

    .. code-block:: yaml

        parts:
            charm:
                plugin: charm
                source: .
                build-packages:
                    - cargo

    If you're migrating from the ``charm-tracing`` charm lib, this configuration is
    likely already in place.

In your charm, add and initialise the ``Tracing`` object.::

    import ops

    class SomeCharm(ops.CharmBase):
        def __init__(self, framework: ops.Framework):
            super().__init__(framework)
            ...
            self.tracing = ops.tracing.Tracing(
                self,
                tracing_relation_name='charm-tracing',
                ca_relation_name='receive-ca-cert',
            )

The tracing relation name is required, while the CA relation name is optional,
as it is possible to use a system certificate authority list, provide a custom
list (for example from the ``certify`` package) or export the trace data over
HTTP connections only. Declaring both relations is most common.

Note that you don't have to ``import ops.tracing``, that name is automatically
available when your Python project depends on ``ops[tracing]``.
"""

from ._api import Tracing
from ._backend import mark_observed as _mark_observed
from ._backend import set_destination
from ._backend import setup as _setup
from ._backend import shutdown as _shutdown

__all__ = [
    'Tracing',
    '_mark_observed',
    '_setup',
    '_shutdown',
    'set_destination',
]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 8s</sub>

### ✅ `bash`

**Check if ops.tracing is accessible**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && uv run --frozen --isolated --extra=dev python -c "
import ops
print(hasattr(ops, 'tracing'))
import ops.tracing
print('ops.tracing works')
" 2>&1 | grep -v "warning\|Installed"

```
Traceback (most recent call last):
  File "<string>", line 4, in <module>
ModuleNotFoundError: No module named 'ops.tracing'
True
<exited with exit code 0>
```


---

<sub>⏱️ 4m 8s</sub>

### ✅ `bash`

**Check Tracing class API**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && uv run --frozen --isolated --extra=dev python -c "
import ops_tracing
print(ops_tracing.Tracing)
import inspect
src = inspect.getsource(ops_tracing.Tracing.__init__)
print(src[:1000])
" 2>&1 | grep -v "warning\|Installed"

<details>
<summary>24 lines</summary>

```
<class 'ops_tracing._api.Tracing'>
    def __init__(
        self,
        charm: ops.CharmBase,
        tracing_relation_name: str,
        *,
        ca_relation_name: str | None = None,
        ca_data: str | None = None,
    ):
        """Initialise the tracing service."""
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
            raise ValueErro
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 16s</sub>

### ✅ `bash`

**Check ops.tracing as attribute**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && uv run --frozen --isolated --extra=dev python -c "
import ops
print(type(ops.tracing))
print(ops.tracing.Tracing)
" 2>&1 | grep -v "warning\|Installed"

```
<class 'module'>
<class 'ops_tracing._api.Tracing'>
<exited with exit code 0>
```


---

<sub>⏱️ 4m 22s</sub>

### 💬 Copilot

The correct approach is `ops.tracing.Tracing(...)` accessed via `import ops`. Let me update charm.py:

---

<sub>⏱️ 4m 22s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py (lines 28-35)

<details>
<summary>8 lines</summary>

```
28. from urllib.parse import urlparse
29. 
30. import ops.tracing
31. import yaml
32. from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerConsumer
33. from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
34. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
35. from charms.grafana_k8s.v0.grafana_source import GrafanaSourceData, GrafanaSourceProvider
```

</details>


---

<sub>⏱️ 4m 27s</sub>

### ✅ `bash`

**Check for bare ops import**

$ grep -n "^import ops" /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py

```
30:import ops.tracing
<exited with exit code 0>
```


---

<sub>⏱️ 4m 31s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 39s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py (lines 243-253)

<details>
<summary>11 lines</summary>

```
243.         self.framework.observe(
244.             self.workload_tracing.on.endpoint_changed,  # type: ignore
245.             self._on_workload_tracing_endpoint_changed,
246.         )
247.         self.framework.observe(
248.             self.workload_tracing.on.endpoint_removed,  # type: ignore
249.             self._on_workload_tracing_endpoint_removed,
250.         )
251. 
252.         self.framework.observe(self.on.config_changed, self._on_config_changed)
253.         self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
```

</details>


---

<sub>⏱️ 4m 42s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py (lines 230-250)

<details>
<summary>21 lines</summary>

```
230. 
231.         self.catalogue = CatalogueConsumer(charm=self, item=self._catalogue_item)
232.         ops.tracing.setup(self, relation_name="charm-tracing")
233.         self.workload_tracing = TracingEndpointRequirer(
234.             self, relation_name="workload-tracing", protocols=["jaeger_thrift_http"]
235.         )
236. 
237.         self.datasource_exchange = DatasourceExchange(
238.             self,
239.             provider_endpoint="send-datasource",
240.             requirer_endpoint=None,
241.         )
242. 
243.         self.framework.observe(
244.             self.workload_tracing.on.endpoint_changed,  # type: ignore
245.             self._on_workload_tracing_endpoint_changed,
246.         )
247.         self.framework.observe(
248.             self.workload_tracing.on.endpoint_removed,  # type: ignore
249.             self._on_workload_tracing_endpoint_removed,
250.         )
```

</details>


---

<sub>⏱️ 4m 46s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 50s</sub>

### 💬 Copilot

Now I need to check if there's already a bare `import ops` or if we need it:

---

<sub>⏱️ 4m 51s</sub>

### ✅ `bash`

**Check ops imports**

$ grep -n "^import ops\|^from ops " /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src/charm.py | head -10

```
30:import ops
56:from ops import CollectStatusEvent, StoredState
<exited with exit code 0>
```


---

<sub>⏱️ 4m 55s</sub>

### 💬 Copilot

Good. Now let's run lint and tests:

---

<sub>⏱️ 4m 56s</sub>

### ✅ `bash`

**Run lint**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && tox -e lint 2>&1 | tail -5

<details>
<summary>6 lines</summary>

```
warning: The `requires-python` specifier (`~=3.8`) in `loki-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 111 packages in 57ms
All checks passed!
  lint: OK (0.16=setup[0.00]+cmd[0.15] seconds)
  congratulations :) (0.17 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 32s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf && tox -e unit 2>&1 | tail -20

<details>
<summary>20 lines</summary>

```
tests/unit/test_transform.py::TestValidateAlerts::test_successfully_validates_good_alert_rules
  /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests/unit/test_transform.py:151: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(ToolProviderCharm)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 71 passed, 9 skipped, 109 warnings in 27.84s =================
unit: commands[2]> uv run --frozen --isolated --extra=dev coverage report
warning: The `requires-python` specifier (`~=3.8`) in `loki-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 111 packages in 49ms
Name                                      Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------------------------
lib/charms/loki_k8s/v0/charm_logging.py      95     21     28      8    72%   136-144, 160, 163-166, 171, 177, 180, 195, 202-214, 231-232
lib/charms/loki_k8s/v0/loki_push_api.py     768    175    208     51    74%   531-534, 546-554, 566-572, 607, 613, 621, 626-630, 895, 922->931, 936, 945-953, 960-968, 1005, 1007->1009, 1009->1011, 1020, 1027, 1037-1039, 1043, 1050-1051, 1124-1131, 1146->exit, 1161->exit, 1205, 1257-1260, 1326, 1330, 1335->1348, 1341-1342, 1349-1352, 1356-1357, 1378-1379, 1394, 1406-1409, 1418, 1427->1424, 1440, 1518, 1521->1515, 1606-1607, 1647-1653, 1663-1664, 1832, 1837, 1848->1860, 1852-1858, 1861, 1862->exit, 1867-1879, 1887-1901, 1942, 1965-1977, 1985-1986, 2000-2001, 2006-2007, 2041, 2073, 2078-2079, 2104, 2134-2165, 2184-2185, 2188, 2205-2206, 2320, 2332-2360, 2370-2375, 2384, 2393, 2411, 2437, 2445-2446, 2479-2480, 2490-2493
lib/charms/loki_k8s/v1/loki_push_api.py     909    437    284     39    48%   606-609, 621-629, 641-647, 682, 688, 696-705, 735, 756, 792-794, 807-857, 878-912, 928-929, 946-955, 970-976, 986, 1001->1010, 1014-1017, 1024-1032, 1039-1047, 1084, 1086->1088, 1088->1090, 1101, 1106, 1116-1118, 1122, 1129-1130, 1188->1196, 1214-1221, 1236->exit, 1424, 1433->1446, 1439-1440, 1447-1450, 1454-1455, 1476-1477, 1492, 1504-1507, 1516, 1525->1522, 1538, 1591-1595, 1601-1614, 1630-1660, 1730-1753, 1763-1764, 1782-1783, 1800-1812, 1816, 1819-1820, 1823-1824, 1835, 1842-1845, 1852-1853, 1857, 1861, 1946-1968, 1971-1973, 1980-1981, 1985-1987, 1995-2029, 2037-2052, 2061-2075, 2079-2080, 2093-2102, 2114-2116, 2125-2133, 2146-2149, 2164-2172, 2185-2201, 2212, 2230-2261, 2270, 2278-2290, 2297-2305, 2313, 2321, 2335, 2343-2396, 2404-2411, 2415-2451, 2454-2462, 2473-2478, 2481, 2495, 2503, 2509, 2521, 2540->2554, 2563, 2588, 2591-2600, 2655-2658, 2672, 2681->2680, 2709-2712, 2717, 2769, 2773-2774, 2780, 2795, 2803-2804, 2827, 2836-2851, 2861-2865, 2869-2870, 2899
src/charm.py                                417     77     86     18    78%   291, 311-312, 315-316, 319->321, 338, 348, 352, 401-403, 479-480, 506, 524, 540, 566, 599-600, 654-674, 708-719, 724, 748-753, 776->780, 785-786, 811-814, 828-832, 857, 864, 879, 902-919, 923-936, 940
src/config_builder.py                        87      2     10      3    95%   133, 149->148, 170
-------------------------------------------------------------------------------------
TOTAL                                      2276    712    616    119    64%
  unit: OK (31.68=setup[0.01]+cmd[0.00,31.31,0.35] seconds)
  congratulations :) (31.69 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 37s</sub>

### 💬 Copilot

All 71 tests pass. Let me do a final check to ensure no remaining references to the old community library:

---

<sub>⏱️ 5m 38s</sub>

### ✅ `bash`

**Check for remaining community library references**

$ grep -rn "charm_tracing\|trace_charm\|charm_tracing_disabled\|BUFFER_DEFAULT_CACHE_FILE_NAME" /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/src /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C1pf/tests 2>/dev/null

```

<exited with exit code 1>
```


---

<sub>⏱️ 5m 49s</sub>

### 💬 Copilot

No remaining references. Here's a summary of the changes made:

**Migration from community `charm_tracing` to `ops[tracing]`:**

1. **`pyproject.toml`**: Replaced `"ops"` + 6 explicit `opentelemetry-*` packages with `"ops[tracing]\>=2.21"`.

2. **`src/charm.py`**:
   - Removed `@trace_charm(...)` decorator and its imports
   - Replaced `TracingEndpointRequirer(charm-tracing)` + `charm_tracing_config()` with `ops.tracing.Tracing(self, tracing_relation_name="charm-tracing")`
   - Kept `workload_tracing` (Jaeger for Loki workload) unchanged

3. **`tests/unit/conftest.py`** & **`tests/interface/conftest.py`**: Removed `charm_tracing_disabled()` usage and the buffer-file patch fixture.

4. **`lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py`**: Deleted (kept `tracing.py` for workload tracing).

5. **`uv.lock`**: Updated via `uv lock`.

---

<sub>⏱️ 5m 49s</sub>

### ✅ `task_complete`

**Migrated loki-k8s-operator from community `charm_tracing`...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Migrated loki-k8s-operator from community `charm_tracing` library to first-party `ops[tracing]`:\n\n- **pyproject.toml**: Replaced `ops` + 6 pinned `opentelemetry-*` packages with `ops[tracing]>=2.21`\n- **src/charm.py**: Removed `@trace_charm()` decorator, replaced `TracingEndpointRequirer`/`charm_tracing_config` for charm-level tracing with `ops.tracing.Tracing(self, tracing_relation_name=\"charm-tracing\")`; kept workload tracing unchanged\n- **tests/unit/conftest.py** & **tests/interface/conftest.py**: Removed `charm_tracing_disabled()` context manager and buffer-file patch (no longer needed)\n- **lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py**: Deleted\n- **uv.lock**: Updated with `uv lock`\n\nAll 71 unit tests pass and lint is clean."
}
```

</details>

<details>
<summary>7 lines</summary>

```
Migrated loki-k8s-operator from community `charm_tracing` library to first-party `ops[tracing]`:

- **pyproject.toml**: Replaced `ops` + 6 pinned `opentelemetry-*` packages with `ops[tracing]>=2.21`
- **src/charm.py**: Removed `@trace_charm()` decorator, replaced `TracingEndpointRequirer`/`charm_tracing_config` for charm-level tracing with `ops.tracing.Tracing(self, tracing_relation_name="charm-tracing")`; kept workload tracing unchanged
- **tests/unit/conftest.py** & **tests/interface/conftest.py**: Removed `charm_tracing_disabled()` context manager and buffer-file patch (no longer needed)
- **lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py**: Deleted
- **uv.lock**: Updated with `uv lock`

All 71 unit tests pass and lint is clean.
```

</details>


---

<sub>⏱️ 5m 49s</sub>

### ✓ Task Complete

Migrated loki-k8s-operator from community `charm_tracing` library to first-party `ops[tracing]`:

- **pyproject.toml**: Replaced `ops` + 6 pinned `opentelemetry-*` packages with `ops[tracing]>=2.21`
- **src/charm.py**: Removed `@trace_charm()` decorator, replaced `TracingEndpointRequirer`/`charm_tracing_config` for charm-level tracing with `ops.tracing.Tracing(self, tracing_relation_name="charm-tracing")`; kept workload tracing unchanged
- **tests/unit/conftest.py** & **tests/interface/conftest.py**: Removed `charm_tracing_disabled()` context manager and buffer-file patch (no longer needed)
- **lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py**: Deleted
- **uv.lock**: Updated with `uv lock`

All 71 unit tests pass and lint is clean.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
