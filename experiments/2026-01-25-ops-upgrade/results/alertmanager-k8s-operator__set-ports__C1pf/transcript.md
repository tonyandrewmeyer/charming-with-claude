# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `69d84c6e-9312-4346-be87-510ae3d5fcd1`  
> - **Started:** 4/2/2026, 5:49:13 AM  
> - **Duration:** 5m 23s  
> - **Exported:** 4/2/2026, 5:54:36 AM  

---

<sub>⏱️ 5s</sub>

### 👤 User

This charm could benefit from set-ports. There is a skill available for applying this change.

---

<sub>⏱️ 14s</sub>

### ✅ `grep`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src**

"open_port|close_port|opened_ports|set_ports" (/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src)

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:160:        self.set_ports()
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:267:    def set_ports(self):
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:273:        actual_ports = self.unit.opened_ports()
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:278:            self.unit.close_port(p.protocol, p.port)
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:282:            self.unit.open_port(p.protocol, p.port)
```


---

<sub>⏱️ 14s</sub>

### ✅ `grep`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/tests**

"open_port|close_port|opened_ports|set_ports" (/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/tests)

```
No matches found.
```


---

<sub>⏱️ 18s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py (lines 155-170)

<details>
<summary>16 lines</summary>

```
155.             ],
156.         )
157.         self.karma_provider = KarmaProvider(self, "karma-dashboard")
158.         self.remote_configuration = RemoteConfigurationRequirer(self)
159. 
160.         self.set_ports()
161. 
162.         self.resources_patch = KubernetesComputeResourcesPatch(
163.             self,
164.             self._container_name,
165.             resource_reqs_func=self._resource_reqs_from_config,
166.         )
167.         self.framework.observe(
168.             self.resources_patch.on.patch_failed,
169.             self._on_k8s_patch_failed,  # pyright: ignore
170.         )
```

</details>


---

<sub>⏱️ 18s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py (lines 260-295)

<details>
<summary>36 lines</summary>

```
260.             self._on_show_config_action,  # pyright: ignore
261.         )
262.         self.framework.observe(
263.             self.on.check_config_action,
264.             self._on_check_config,  # pyright: ignore
265.         )
266. 
267.     def set_ports(self):
268.         """Open necessary (and close no longer needed) workload ports."""
269.         planned_ports = {
270.             OpenedPort("tcp", self._ports.api),
271.             OpenedPort("tcp", self._ports.ha),
272.         }
273.         actual_ports = self.unit.opened_ports()
274. 
275.         # Ports may change across an upgrade, so need to sync
276.         ports_to_close = actual_ports.difference(planned_ports)
277.         for p in ports_to_close:
278.             self.unit.close_port(p.protocol, p.port)
279. 
280.         new_ports_to_open = planned_ports.difference(actual_ports)
281.         for p in new_ports_to_open:
282.             self.unit.open_port(p.protocol, p.port)
283. 
284.     @property
285.     def _catalogue_item(self) -> CatalogueItem:
286.         api_endpoints = {"Alerts": "/api/v2/alerts"}
287. 
288.         return CatalogueItem(
289.             name="Alertmanager",
290.             icon="bell-alert",
291.             url=self._external_url,
292.             description=(
293.                 "Alertmanager receives alerts from supporting applications, such as "
294.                 "Prometheus or Loki, then deduplicates, groups and routes them to "
295.                 "the configured receiver(s)."
```

</details>


---

<sub>⏱️ 26s</sub>

### ✅ `grep`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py**

"OpenedPort|^import ops|^from ops|_ports" (/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py)

<details>
<summary>21 matches</summary>

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:40:from ops.charm import ActionEvent, CharmBase
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:41:from ops.main import main
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:42:from ops.model import (
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:46:    OpenedPort,
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:50:from ops.pebble import PathError, ProtocolError  # type: ignore
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:93:    _ports = SimpleNamespace(api=9093, ha=9094)
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:160:        self.set_ports()
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:216:            f"{hostname}:{self._ports.ha}"
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:225:            ha_port=self._ports.ha,
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:267:    def set_ports(self):
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:269:        planned_ports = {
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:270:            OpenedPort("tcp", self._ports.api),
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:271:            OpenedPort("tcp", self._ports.ha),
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:273:        actual_ports = self.unit.opened_ports()
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:276:        ports_to_close = actual_ports.difference(planned_ports)
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:280:        new_ports_to_open = planned_ports.difference(actual_ports)
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:281:        for p in new_ports_to_open:
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:311:            f"{hostname}:{self._ports.api}"
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:387:        return self._ports.api
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:644:        return f"{self._scheme}://{self._fqdn}:{self._ports.api}"
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py:657:        return f"{self._scheme}://{fqdn}:{self._ports.api}"
```

</details>


---

<sub>⏱️ 34s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py (lines 40-52)

<details>
<summary>13 lines</summary>

```
40. from ops.charm import ActionEvent, CharmBase
41. from ops.main import main
42. from ops.model import (
43.     ActiveStatus,
44.     BlockedStatus,
45.     MaintenanceStatus,
46.     OpenedPort,
47.     Relation,
48.     WaitingStatus,
49. )
50. from ops.pebble import PathError, ProtocolError  # type: ignore
51. 
52. from alertmanager import (
```

</details>


---

<sub>⏱️ 56s</sub>

### ✅ `grep`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py**

"^import ops" (/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py)

```
No matches found.
```


---

<sub>⏱️ 1m 5s</sub>

### 💬 Copilot

Now I have all the context. Here's the plan:
1. Add `import ops` 
2. Remove `OpenedPort` from imports
3. Replace the `set_ports()` method body with a single `self.unit.set_ports()` call

---

<sub>⏱️ 1m 5s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py (lines 38-42)

```
38. )
39. from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer
40. from ops.charm import ActionEvent, CharmBase
41. from ops.main import main
42. from ops.model import (
```


---

<sub>⏱️ 1m 12s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 27s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 39s</sub>

### 💬 Copilot

Now let's verify and run the tests:

---

<sub>⏱️ 1m 39s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py (lines 38-52)

<details>
<summary>15 lines</summary>

```
38. )
39. from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer
40. import ops
41. from ops.charm import ActionEvent, CharmBase
42. from ops.main import main
43. from ops.model import (
44.     ActiveStatus,
45.     BlockedStatus,
46.     MaintenanceStatus,
47.     Relation,
48.     WaitingStatus,
49. )
50. from ops.pebble import PathError, ProtocolError  # type: ignore
51. 
52. from alertmanager import (
```

</details>


---

<sub>⏱️ 1m 39s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py (lines 267-278)

<details>
<summary>12 lines</summary>

```
267.     def set_ports(self):
268.         """Open necessary (and close no longer needed) workload ports."""
269.         self.unit.set_ports(
270.             ops.Port("tcp", self._ports.api),
271.             ops.Port("tcp", self._ports.ha),
272.         )
273. 
274.     @property
275.     def _catalogue_item(self) -> CatalogueItem:
276.         api_endpoints = {"Alerts": "/api/v2/alerts"}
277. 
278.         return CatalogueItem(
```

</details>


---

<sub>⏱️ 1m 50s</sub>

### 💬 Copilot

The `import ops` should come before third-party imports. Let me fix the ordering:

---

<sub>⏱️ 1m 50s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py (lines 1-45)

<details>
<summary>45 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2021 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """A Juju charm for alertmanager."""
6. 
7. import logging
8. import socket
9. import subprocess
10. from dataclasses import dataclass
11. from pathlib import Path
12. from types import SimpleNamespace
13. from typing import List, Optional, Tuple, cast
14. from urllib.parse import urlparse
15. 
16. import yaml
17. from charms.alertmanager_k8s.v0.alertmanager_remote_configuration import (
18.     RemoteConfigurationRequirer,
19. )
20. from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerProvider
21. from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
22. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
23. from charms.grafana_k8s.v0.grafana_source import GrafanaSourceProvider
24. from charms.istio_beacon_k8s.v0.service_mesh import ServiceMeshConsumer, UnitPolicy
25. from charms.karma_k8s.v0.karma_dashboard import KarmaProvider
26. from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
27.     K8sResourcePatchFailedEvent,
28.     KubernetesComputeResourcesPatch,
29.     ResourceRequirements,
30.     adjust_resource_requirements,
31. )
32. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
33. from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
34. from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
35. from charms.tls_certificates_interface.v4.tls_certificates import (
36.     CertificateRequestAttributes,
37.     TLSCertificatesRequiresV4,
38. )
39. from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer
40. import ops
41. from ops.charm import ActionEvent, CharmBase
42. from ops.main import main
43. from ops.model import (
44.     ActiveStatus,
45.     BlockedStatus,
```

</details>


---

<sub>⏱️ 2m 4s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 2m 24s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 2m 34s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src/charm.py (lines 14-52)

<details>
<summary>39 lines</summary>

```
14. from urllib.parse import urlparse
15. 
16. import ops
17. import yaml
18. from charms.alertmanager_k8s.v0.alertmanager_remote_configuration import (
19.     RemoteConfigurationRequirer,
20. )
21. from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerProvider
22. from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
23. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
24. from charms.grafana_k8s.v0.grafana_source import GrafanaSourceProvider
25. from charms.istio_beacon_k8s.v0.service_mesh import ServiceMeshConsumer, UnitPolicy
26. from charms.karma_k8s.v0.karma_dashboard import KarmaProvider
27. from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
28.     K8sResourcePatchFailedEvent,
29.     KubernetesComputeResourcesPatch,
30.     ResourceRequirements,
31.     adjust_resource_requirements,
32. )
33. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
34. from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
35. from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
36. from charms.tls_certificates_interface.v4.tls_certificates import (
37.     CertificateRequestAttributes,
38.     TLSCertificatesRequiresV4,
39. )
40. from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer
41. from ops.charm import ActionEvent, CharmBase
42. from ops.main import main
43. from ops.model import (
44.     ActiveStatus,
45.     BlockedStatus,
46.     MaintenanceStatus,
47.     Relation,
48.     WaitingStatus,
49. )
50. from ops.pebble import PathError, ProtocolError  # type: ignore
51. 
52. from alertmanager import (
```

</details>


---

<sub>⏱️ 2m 47s</sub>

### 💬 Copilot

Good. Now let's run lint and unit tests:

---

<sub>⏱️ 2m 48s</sub>

### ✅ `bash`

**Run lint**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf && tox -e lint 2>&1 | tail -30

<details>
<summary>8 lines</summary>

```
lint: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p cpython3 --allow-existing --python-preference system /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/.tox/lint
lint: commands[0]> uv run --frozen --isolated --extra=dev ruff check /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/src /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/tests /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/lib/charms/alertmanager_k8s
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 110 packages in 87ms
All checks passed!
  lint: OK (0.28=setup[0.03]+cmd[0.25] seconds)
  congratulations :) (0.29 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 0s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf && tox -e unit 2>&1 | tail -30

<details>
<summary>28 lines</summary>

```
tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_no_peers
tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf/tests/unit/test_self_scrape_jobs.py:22: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/.cache/uv/builds-v0/.tmpBa8EYh/lib/python3.12/site-packages/ops/_private/harness.py:1112: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/1'.
    warnings.warn(

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/.cache/uv/builds-v0/.tmpBa8EYh/lib/python3.12/site-packages/ops/_private/harness.py:1112: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/2'.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====== 57 passed, 3 skipped, 4 xfailed, 311 warnings in 106.84s (0:01:46) ======
unit: commands[1]> uv run --frozen --isolated --extra=dev coverage report
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 110 packages in 40ms
Name                                                                  Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------------------------------------
lib/charms/alertmanager_k8s/v0/alertmanager_remote_configuration.py     124     15     20      2    88%   52-54, 184, 228-229, 377, 385, 405-406, 417, 449-451, 471-472
lib/charms/alertmanager_k8s/v1/alertmanager_dispatch.py                  98      8     16      4    89%   114, 123-132, 222->exit, 233->232, 239-241, 245
src/alertmanager.py                                                     133     22     28     11    78%   41, 45, 129, 144, 152, 161, 169-170, 230, 240-241, 257, 265-266, 277-278, 283-284, 297, 324, 336-337
src/alertmanager_client.py                                              124     30     10      3    74%   55, 73-74, 84, 114, 121-122, 162-167, 193-202, 314-323, 345-354
src/charm.py                                                            264     38     46      9    83%   314-319, 322, 325-329, 333-342, 348, 371-372, 404-406, 460-462, 472->489, 476-483, 496->502, 517-519, 526, 565, 583, 588-589, 625, 660
src/config_builder.py                                                    67      3     16      2    92%   73->75, 133-135
-----------------------------------------------------------------------------------------------------------------
TOTAL                                                                   810    116    136     31    83%
  unit: OK (111.53=setup[0.03]+cmd[111.23,0.27] seconds)
  congratulations :) (111.54 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 6s</sub>

### 💬 Copilot

All 57 tests pass. Now let me commit the changes:

---

<sub>⏱️ 5m 7s</sub>

### ✅ `bash`

**Show diff**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf && git --no-pager diff

<details>
<summary>43 lines</summary>

```diff
diff --git a/src/charm.py b/src/charm.py
index ae92826..639b5b1 100755
--- a/src/charm.py
+++ b/src/charm.py
@@ -13,6 +13,7 @@ from types import SimpleNamespace
 from typing import List, Optional, Tuple, cast
 from urllib.parse import urlparse
 
+import ops
 import yaml
 from charms.alertmanager_k8s.v0.alertmanager_remote_configuration import (
     RemoteConfigurationRequirer,
@@ -43,7 +44,6 @@ from ops.model import (
     ActiveStatus,
     BlockedStatus,
     MaintenanceStatus,
-    OpenedPort,
     Relation,
     WaitingStatus,
 )
@@ -266,20 +266,10 @@ class AlertmanagerCharm(CharmBase):
 
     def set_ports(self):
         """Open necessary (and close no longer needed) workload ports."""
-        planned_ports = {
-            OpenedPort("tcp", self._ports.api),
-            OpenedPort("tcp", self._ports.ha),
-        }
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
+        self.unit.set_ports(
+            ops.Port("tcp", self._ports.api),
+            ops.Port("tcp", self._ports.ha),
+        )
 
     @property
     def _catalogue_item(self) -> CatalogueItem:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 17s</sub>

### ✅ `bash`

**Commit changes**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C1pf && git add src/charm.py && git commit -m "refactor: replace imperative port management with set_ports()

Replace the manual open_port()/close_port() diff logic in set_ports()
with the declarative Unit.set_ports() API (available since ops 2.7.0).

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[detached HEAD 6fc846f] refactor: replace imperative port management with set_ports()
 1 file changed, 5 insertions(+), 15 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 5m 23s</sub>

### ✅ `task_complete`

**Replaced the imperative port management in `src/charm.py`...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Replaced the imperative port management in `src/charm.py` with the declarative `Unit.set_ports()` API:\n\n- Added `import ops` \n- Removed `OpenedPort` from `from ops.model import ...`\n- Replaced the 13-line `set_ports()` method body (manual diff with `open_port`/`close_port` loops) with a single `self.unit.set_ports(ops.Port(\"tcp\", ...), ops.Port(\"tcp\", ...))` call\n\nLint and all 57 unit tests pass."
}
```

</details>

<details>
<summary>5 lines</summary>

```
Replaced the imperative port management in `src/charm.py` with the declarative `Unit.set_ports()` API:

- Added `import ops` 
- Removed `OpenedPort` from `from ops.model import ...`
- Replaced the 13-line `set_ports()` method body (manual diff with `open_port`/`close_port` loops) with a single `self.unit.set_ports(ops.Port("tcp", ...), ops.Port("tcp", ...))` call

Lint and all 57 unit tests pass.
```

</details>


---

<sub>⏱️ 5m 23s</sub>

### ✓ Task Complete

Replaced the imperative port management in `src/charm.py` with the declarative `Unit.set_ports()` API:

- Added `import ops` 
- Removed `OpenedPort` from `from ops.model import ...`
- Replaced the 13-line `set_ports()` method body (manual diff with `open_port`/`close_port` loops) with a single `self.unit.set_ports(ops.Port("tcp", ...), ops.Port("tcp", ...))` call

Lint and all 57 unit tests pass.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
