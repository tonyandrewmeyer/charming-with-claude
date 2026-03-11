# 🤖 Copilot CLI Session

> **Session ID:** `98242861-867c-478c-9cbb-c77b6b8e44e2`
> **Duration:** 8m 27s
> **Exported:** 3/11/2026, 1:34:10 PM

<sub>⏱️ 4s</sub>

### 👤 User

ops 2.23.0 added support for defining charm config options as Python dataclasses or Pydantic models, loaded via CharmBase.load_config(). The conserver-charm (https://github.com/canonical/conserver-charm) already uses this feature -- look at how they did it in src/config.py and update this charm similarly.

---

<sub>⏱️ 11s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src

<details>
<summary>6 lines</summary>

```
alertmanager.py
alertmanager_client.py
charm.py
config_builder.py
grafana_dashboards
prometheus_alert_rules
```

</details>


---

<sub>⏱️ 12s</sub>

### ✅ `github-mcp-server-get_file_contents`

**src/config.py**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "repo": "conserver-charm",
  "path": "src/config.py"
}
```

</details>

<details>
<summary>13 lines</summary>

```
successfully downloaded text file (SHA: fdc494ffd00c97767902feeedfd62df615c7eec5)# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
"""Charm configuration."""

from pydantic import Base64Str, BaseModel

PASSWD_FILE = """\
# Conserver passwd file
# Format: username:$1$Y0ZjMm2h$oMX5UyLi1/y0Q9IRWf3v/0
# you can generate the hashed password using `openssl passwd -1`
"""


class ConserverConfig(BaseModel):
    """Conserver Charm configuration."""

    config_file: Base64Str = ""
    passwd_file: Base64Str = PASSWD_FILE
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py

<details>
<summary>671 lines</summary>

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
53.     ConfigFileSystemState,
54.     ConfigUpdateFailure,
55.     WorkloadManager,
56.     WorkloadManagerError,
57. )
58. from config_builder import ConfigBuilder, ConfigError
59. 
60. logger = logging.getLogger(__name__)
61. 
62. 
63. @dataclass
64. class TLSConfig:
65.     """TLS configuration received by the charm over the `certificates` relation."""
66. 
67.     server_cert: str
68.     ca_cert: str
69.     private_key: str
70. 
71. 
72. @trace_charm(
73.     tracing_endpoint="_charm_tracing_endpoint",
74.     server_cert="_charm_tracing_ca_cert",
75.     extra_types=(
76.         AlertmanagerProvider,
77.         TLSCertificatesRequiresV4,
78.         IngressPerAppRequirer,
79.         KubernetesComputeResourcesPatch,
80.         RemoteConfigurationRequirer,
81.     ),
82. )
83. class AlertmanagerCharm(CharmBase):
84.     """A Juju charm for alertmanager."""
85. 
86.     # Container name must match metadata.yaml
87.     # Layer name is used for the layer label argument in container.add_layer
88.     # Service name matches charm name for consistency
89.     _container_name = _service_name = "alertmanager"
90.     _relations = SimpleNamespace(
91.         alerting="alerting", peer="replicas", remote_config="remote_configuration"
92.     )
93.     _ports = SimpleNamespace(api=9093, ha=9094)
94. 
95.     # path, inside the workload container, to the alertmanager and amtool configuration files
96.     # the amalgamated templates file goes in the same folder as the main configuration file
97.     _config_path = "/etc/alertmanager/alertmanager.yml"
98.     _web_config_path = "/etc/alertmanager/alertmanager-web-config.yml"
99.     _amtool_config_path = "/etc/amtool/config.yml"
100.     _templates_path = "/etc/alertmanager/templates.tmpl"
101. 
102.     _server_cert_path = "/etc/alertmanager/alertmanager.cert.pem"
103.     _key_path = "/etc/alertmanager/alertmanager.key.pem"
104.     _ca_cert_path = "/usr/local/share/ca-certificates/cos-ca.crt"
105. 
106.     def __init__(self, *args):
107.         super().__init__(*args)
108.         self.container = self.unit.get_container(self._container_name)
109.         self._fqdn = socket.getfqdn()
110. 
111.         self._csr_attributes = CertificateRequestAttributes(
112.             # the `common_name` field is required but limited to 64 characters.
113.             # since it's overridden by sans, we can use a short,
114.             # constrained value like app name.
115.             common_name=self.app.name,
116.             sans_dns=frozenset((self._fqdn,)),
117.         )
118.         self._cert_requirer = TLSCertificatesRequiresV4(
119.             charm=self,
120.             relationship_name="certificates",
121.             certificate_requests=[self._csr_attributes],
122.         )
123.         self.framework.observe(
124.             self._cert_requirer.on.certificate_available,  # pyright: ignore
125.             self._on_certificate_available,
126.         )
127. 
128.         self.ingress = IngressPerAppRequirer(
129.             self,
130.             port=self.api_port,
131.             scheme=self._scheme,
132.             strip_prefix=True,
133.             redirect_https=True,
134.         )
135.         self.framework.observe(self.ingress.on.ready, self._handle_ingress)  # pyright: ignore
136.         self.framework.observe(self.ingress.on.revoked, self._handle_ingress)  # pyright: ignore
137. 
138.         self.alertmanager_provider = AlertmanagerProvider(
139.             self,
140.             relation_name=self._relations.alerting,
141.             external_url=self._internal_url,  # TODO See 'TODO' below, about external_url
142.         )
143. 
144.         self.grafana_dashboard_provider = GrafanaDashboardProvider(charm=self)
145.         self.grafana_source_provider = GrafanaSourceProvider(
146.             charm=self,
147.             source_type="alertmanager",
148.             source_url=self.ingress.url or self._service_url,
149.             is_ingress_per_app=True, # We want only one alertmanager datasource (unit) to be listed in grafana.
150.             refresh_event=[
151.                 self.ingress.on.ready,
152.                 self.ingress.on.revoked,
153.                 self.on.update_status,
154.                 self._cert_requirer.on.certificate_available,
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
171. 
172.         # Self-monitoring
173.         self._scraping = MetricsEndpointProvider(
174.             self,
175.             relation_name="self-metrics-endpoint",
176.             jobs=self.self_scraping_job,
177.             refresh_event=[
178.                 self.on.update_status,
179.                 self.ingress.on.ready,  # pyright: ignore
180.                 self.ingress.on.revoked,  # pyright: ignore
181.                 self.on["ingress"].relation_changed,
182.                 self.on["ingress"].relation_departed,
183.                 self._cert_requirer.on.certificate_available,  # pyright: ignore
184.             ],
185.         )
186.         self._tracing = TracingEndpointRequirer(self, protocols=["otlp_http"])
187.         self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
188.             self._tracing, self._ca_cert_path
189.         )
190. 
191.         self.catalog = CatalogueConsumer(charm=self, item=self._catalogue_item)
192. 
193.         self._mesh = ServiceMeshConsumer(
194.             self,
195.             policies=[
196.                 UnitPolicy(
197.                     relation="alerting",
198.                     ports=[self.api_port],
199.                 ),
200.                 UnitPolicy(
201.                     relation="grafana-source",
202.                     ports=[self.api_port],
203.                 ),
204.                 UnitPolicy(
205.                     relation="self-metrics-endpoint",
206.                     ports=[self.api_port],
207.                 ),
208.             ],
209.         )
210. 
211.         # Core lifecycle events
212.         self.framework.observe(self.on.config_changed, self._on_config_changed)
213.         self.framework.observe(self.on.start, self._on_start)
214. 
215.         peer_ha_netlocs = [
216.             f"{hostname}:{self._ports.ha}"
217.             for hostname in self._get_peer_hostnames(include_this_unit=False)
218.         ]
219. 
220.         self.alertmanager_workload = WorkloadManager(
221.             self,
222.             container_name=self._container_name,
223.             peer_netlocs=peer_ha_netlocs,
224.             api_port=self.api_port,
225.             ha_port=self._ports.ha,
226.             web_external_url=self._external_url,
227.             web_route_prefix="/",
228.             config_path=self._config_path,
229.             web_config_path=self._web_config_path,
230.             tls_enabled=lambda: self._tls_available,
231.             cafile=self._ca_cert_path if Path(self._ca_cert_path).exists() else None,
232.         )
233.         self.framework.observe(
234.             # The workload manager too observes pebble ready, but still need this here because
235.             # of the common exit hook (otherwise would need to pass the common exit hook as
236.             # a callback).
237.             self.on.alertmanager_pebble_ready,  # pyright: ignore
238.             self._on_pebble_ready,
239.         )
240.         self.framework.observe(self.on.update_status, self._on_update_status)
241.         self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
242. 
243.         # Remote configuration events
244.         self.framework.observe(
245.             self.remote_configuration.on.remote_configuration_changed,  # pyright: ignore
246.             self._on_remote_configuration_changed,
247.         )
248. 
249.         # Peer relation events
250.         self.framework.observe(
251.             self.on[self._relations.peer].relation_joined, self._on_peer_relation_joined
252.         )
253.         self.framework.observe(
254.             self.on[self._relations.peer].relation_changed, self._on_peer_relation_changed
255.         )
256. 
257.         # Action events
258.         self.framework.observe(
259.             self.on.show_config_action,
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
296.             ),
297.             api_docs="https://github.com/prometheus/alertmanager/blob/main/api/v2/openapi.yaml",
298.             api_endpoints={
299.                 key: f"{self._external_url}{path}" for key, path in api_endpoints.items()
300.             },
301.         )
302. 
303.     @property
304.     def self_scraping_job(self):
305.         """The self-monitoring scrape job."""
306.         # We assume that scraping, especially self-monitoring, is in-cluster.
307.         # This assumption is necessary because the local CA signs CSRs with FQDN as the SAN DNS.
308.         # If prometheus were to scrape an ingress URL instead, it would error out with:
309.         # x509: cannot validate certificate.
310.         peer_api_netlocs = [
311.             f"{hostname}:{self._ports.api}"
312.             for hostname in self._get_peer_hostnames(include_this_unit=True)
313.         ]
314. 
315.         config = {
316.             "scheme": self._scheme,
317.             "metrics_path": "/metrics",
318.             "static_configs": [{"targets": peer_api_netlocs}],
319.         }
320. 
321.         return [config]
322. 
323.     def _resource_reqs_from_config(self) -> ResourceRequirements:
324.         limits = {
325.             "cpu": self.model.config.get("cpu"),
326.             "memory": self.model.config.get("memory"),
327.         }
328.         requests = {"cpu": "0.25", "memory": "200Mi"}
329.         return adjust_resource_requirements(limits, requests, adhere_to_requests=True)
330. 
331.     def _on_k8s_patch_failed(self, event: K8sResourcePatchFailedEvent):
332.         self.unit.status = BlockedStatus(str(event.message))
333. 
334.     def _handle_ingress(self, _):
335.         if url := self.ingress.url:
336.             logger.info("Ingress is ready: '%s'.", url)
337.         else:
338.             logger.info("Ingress revoked.")
339.         self._common_exit_hook()
340. 
341.     def _on_check_config(self, event: ActionEvent) -> None:
342.         """Runs `amtool check-config` inside the workload."""
343.         try:
344.             stdout, stderr = self.alertmanager_workload.check_config()
345.         except WorkloadManagerError as e:
346.             return event.fail(str(e))
347. 
348.         if not stdout and stderr:
349.             return event.fail(stderr)
350. 
351.         event.set_results({"result": stdout, "error-message": stderr, "valid": not stderr})
352.         return None
353. 
354.     def _on_show_config_action(self, event: ActionEvent):
355.         """Hook for the show-config action."""
356.         event.log(f"Fetching {self._config_path}")
357.         if not self.alertmanager_workload.is_ready:
358.             event.fail("Container not ready")
359. 
360.         filepaths = self._render_manifest().manifest.keys()
361. 
362.         try:
363.             results = [
364.                 {
365.                     "path": filepath,
366.                     "content": str(self.container.pull(filepath).read()),
367.                 }
368.                 for filepath in filepaths
369.                 if self.container.exists(filepath)
370.             ]
371.             content = self.container.pull(self._config_path)
372.             # juju requires keys to be lowercase alphanumeric (can't use self._config_path)
373.             event.set_results(
374.                 {
375.                     "path": self._config_path,
376.                     "content": str(content.read()),
377.                     # This already includes the above, but keeping both for backwards compat.
378.                     "configs": str(results),
379.                 }
380.             )
381.         except (ProtocolError, PathError) as e:
382.             event.fail(str(e))
383. 
384.     @property
385.     def api_port(self) -> int:
386.         """Get the API port number to use for alertmanager (default: 9093)."""
387.         return self._ports.api
388. 
389.     @property
390.     def peer_relation(self) -> Optional["Relation"]:
391.         """Helper function for obtaining the peer relation object.
392. 
393.         Returns: peer relation object
394.         (NOTE: would return None if called too early, e.g. during install).
395.         """
396.         return self.model.get_relation(self._relations.peer)
397. 
398.     def _get_remote_config(self) -> Optional[Tuple[Optional[dict], Optional[str]]]:
399.         remote_config, remote_templates = self.remote_configuration.config()
400.         if remote_config:
401.             templates = "\n".join(remote_templates) if remote_templates else None
402.             return remote_config, templates
403.         return None
404. 
405.     def _get_local_config(self) -> Optional[Tuple[Optional[dict], Optional[str]]]:
406.         config = self.config["config_file"]
407.         if config:
408.             local_config = yaml.safe_load(cast(str, config))
409. 
410.             # If `juju config` is executed like this `config_file=am.yaml` instead of
411.             # `config_file=@am.yaml` local_config will be the string `am.yaml` instead
412.             # of its content (dict).
413.             if not isinstance(local_config, dict):
414.                 msg = f"Unable to set config from file. Use juju config {self.unit.name} config_file=@FILENAME"
415.                 logger.error(msg)
416.                 raise ConfigUpdateFailure(msg)
417. 
418.             local_templates = cast(str, self.config["templates_file"]) or None
419.             return local_config, local_templates
420.         return None
421. 
422.     def _get_raw_config_and_templates(
423.         self,
424.     ) -> Tuple[Optional[dict], Optional[str]]:
425.         # block if multiple config sources configured
426.         if self._get_remote_config() and self._get_local_config():
427.             logger.error("unable to use config from config_file and relation at the same time")
428.             raise ConfigUpdateFailure("Multiple configs detected")
429.         # if no config provided, use default config with a placeholder receiver
430.         if compound_config := self._get_remote_config():
431.             config, templates = compound_config
432.         elif compound_config := self._get_local_config():
433.             config, templates = compound_config
434.         else:
435.             config = None
436.             templates = None
437. 
438.         return config, templates
439. 
440.     def _render_manifest(self) -> ConfigFileSystemState:
441.         raw_config, raw_templates = self._get_raw_config_and_templates()
442. 
443.         # Note: A free function (with many args) would have the same functionality.
444.         config_suite = (
445.             ConfigBuilder(api_port=self.api_port)
446.             .set_config(raw_config)
447.             .set_tls_server_config(
448.                 cert_file_path=self._server_cert_path, key_file_path=self._key_path
449.             )
450.             .set_templates(raw_templates, self._templates_path)
451.             .build()
452.         )
453.         tls_config = self._tls_config
454. 
455.         return ConfigFileSystemState(
456.             {
457.                 self._config_path: config_suite.alertmanager,
458.                 self._web_config_path: config_suite.web,
459.                 self._templates_path: config_suite.templates,
460.                 self._amtool_config_path: config_suite.amtool,
461.                 self._server_cert_path: tls_config.server_cert if tls_config else None,
462.                 self._key_path: tls_config.private_key if tls_config else None,
463.                 self._ca_cert_path: tls_config.ca_cert if tls_config else None,
464.             }
465.         )
466. 
467.     def _common_exit_hook(self, update_ca_certs: bool = False) -> None:
468.         """Event processing hook that is common to all events to ensure idempotency."""
469.         if not self.resources_patch.is_ready():
470.             if isinstance(self.unit.status, ActiveStatus) or self.unit.status.message == "":
471.                 self.unit.status = WaitingStatus("Waiting for resource limit patch to apply")
472.             return
473. 
474.         if not self.container.can_connect():
475.             self.unit.status = MaintenanceStatus("Waiting for pod startup to complete")
476.             return
477. 
478.         if update_ca_certs:
479.             self._update_ca_certs()
480. 
481.         # Make sure the external url is valid
482.         if external_url := self._external_url:
483.             parsed = urlparse(external_url)
484.             if not (parsed.scheme in ["http", "https"] and parsed.hostname):
485.                 # This shouldn't happen
486.                 logger.error(
487.                     "Invalid external url: '%s'; must include scheme and hostname.",
488.                     external_url,
489.                 )
490.                 self.unit.status = BlockedStatus(
491.                     f"Invalid external url: '{external_url}'; must include scheme and hostname."
492.                 )
493.                 return
494. 
495.         # TODO Conditionally update with the external URL if it's a CMR, or rely on "recv-ca-cert"
496.         #  on the prometheus side.
497.         #  - https://github.com/canonical/operator/issues/970
498.         #  - https://github.com/canonical/prometheus-k8s-operator/issues/530,
499.         self.alertmanager_provider.update(external_url=self._internal_url)
500. 
501.         self.grafana_source_provider.update_source(self._external_url)
502. 
503.         self.ingress.provide_ingress_requirements(scheme=self._scheme, port=self.api_port)
504.         self._scraping.update_scrape_job_spec(self.self_scraping_job)
505. 
506.         if self.peer_relation:
507.             # Could have simply used `socket.getfqdn()` here and add the path when reading this
508.             # relation data, but this way it is more future-proof in case we change from ingress
509.             # per app to ingress per unit.
510.             self.peer_relation.data[self.unit]["private_address"] = self._internal_url
511. 
512.         self.karma_provider.target = self._external_url
513. 
514.         # Update config file
515.         try:
516.             self.alertmanager_workload.update_config(self._render_manifest())
517.         except (ConfigUpdateFailure, ConfigError) as e:
518.             self.unit.status = BlockedStatus(str(e))
519.             return
520. 
521.         # Update pebble layer
522.         self.alertmanager_workload.update_layer()
523. 
524.         # Reload or restart the service
525.         try:
526.             self.alertmanager_workload.reload()
527.         except ConfigUpdateFailure as e:
528.             self.unit.status = BlockedStatus(str(e))
529.             return
530. 
531.         self.catalog.update_item(item=self._catalogue_item)
532. 
533.         self.unit.status = ActiveStatus()
534. 
535.     def _on_certificate_available(self, _):
536.         self._common_exit_hook(update_ca_certs=True)
537. 
538.     def _on_pebble_ready(self, _):
539.         """Event handler for PebbleReadyEvent."""
540.         self._common_exit_hook()
541. 
542.     def _on_config_changed(self, _):
543.         """Event handler for ConfigChangedEvent."""
544.         self._common_exit_hook(update_ca_certs=True)
545. 
546.     def _on_start(self, _):
547.         """Event handler for ConfigChangedEvent."""
548.         self._common_exit_hook(update_ca_certs=True)
549. 
550.     def _on_peer_relation_joined(self, _):
551.         """Event handler for replica's RelationChangedEvent."""
552.         self._common_exit_hook()
553. 
554.     def _on_peer_relation_changed(self, _):
555.         """Event handler for replica's RelationChangedEvent.
556. 
557.         `relation_changed` is needed in addition to `relation_joined` because when a second unit
558.         joins, the first unit must be restarted and provided with the second unit's IP address.
559.         when the first unit sees "joined", it is not guaranteed that the second unit already has
560.         an IP address.
561.         """
562.         self._common_exit_hook()
563. 
564.     def _on_remote_configuration_changed(self, _):
565.         """Event handler for remote configuration's RelationChangedEvent."""
566.         self._common_exit_hook()
567. 
568.     def _on_update_status(self, _):
569.         """Event handler for UpdateStatusEvent.
570. 
571.         Logs list of peers, uptime and version info.
572.         """
573.         try:
574.             status = self.alertmanager_workload.api.status()
575.             logger.info(
576.                 "alertmanager %s is up and running (uptime: %s); cluster mode: %s, with %d peers",
577.                 status["versionInfo"]["version"],
578.                 status["uptime"],
579.                 status["cluster"]["status"],
580.                 len(status["cluster"]["peers"]),
581.             )
582.         except ConnectionError as e:
583.             logger.error("Failed to obtain status: %s", str(e))
584. 
585.         # Calling the common hook to make sure a single unit set its IP in case all events fired
586.         # before an IP address was ready, leaving UpdateStatue as the last resort.
587.         self._common_exit_hook()
588. 
589.     def _on_upgrade_charm(self, _):
590.         """Event handler for replica's UpgradeCharmEvent."""
591.         # After upgrade (refresh), the unit ip address is not guaranteed to remain the same, and
592.         # the config may need update. Calling the common hook to update.
593.         self._common_exit_hook()
594. 
595.     def _update_ca_certs(self):
596.         ca_cert_path = Path(self._ca_cert_path)
597.         if tls_config := self._tls_config:
598.             ca_cert_path.parent.mkdir(exist_ok=True, parents=True)
599.             ca_cert_path.write_text(tls_config.ca_cert)
600.         else:
601.             ca_cert_path.unlink(missing_ok=True)
602. 
603.         # Workload container
604.         self.container.exec(["update-ca-certificates", "--fresh"], timeout=30).wait()
605.         # Charm container
606.         subprocess.run(["update-ca-certificates", "--fresh"], check=True)
607. 
608.     def _get_peer_hostnames(self, include_this_unit=True) -> List[str]:
609.         """Returns a list of the hostnames of the peer units.
610. 
611.         An example of the return format is:
612.           ["alertmanager-1.alertmanager-endpoints.am.svc.cluster.local"]
613.         """
614.         addresses = []
615.         if include_this_unit:
616.             addresses.append(self._internal_url)
617.         if pr := self.peer_relation:
618.             for unit in pr.units:  # pr.units only holds peers (self.unit is not included)
619.                 if address := pr.data[unit].get("private_address"):
620.                     addresses.append(address)
621. 
622.         # Save only the hostname part of the address
623.         # Sort the hostnames in case their order is not guaranteed, to reduce unnecessary updates
624.         hostnames = sorted([urlparse(address).hostname for address in addresses])
625. 
626.         return hostnames
627. 
628.     @property
629.     def _tls_config(self) -> Optional[TLSConfig]:
630.         certificates, key = self._cert_requirer.get_assigned_certificate(
631.             certificate_request=self._csr_attributes
632.         )
633.         if not (key and certificates):
634.             return None
635.         return TLSConfig(certificates.certificate.raw, certificates.ca.raw, key.raw)
636. 
637.     @property
638.     def _tls_available(self) -> bool:
639.         return bool(self._tls_config)
640. 
641.     @property
642.     def _internal_url(self) -> str:
643.         """Return the fqdn dns-based in-cluster (private) address of the alertmanager api server."""
644.         return f"{self._scheme}://{self._fqdn}:{self._ports.api}"
645. 
646.     @property
647.     def _service_url(self) -> str:
648.         """Return the FQDN DNS-based in-cluster (private) address of the service for Alertmanager.
649. 
650.         Since our goal is to ensure that we only send one datasource to Grafana when we have multiple units, we can't use the socket FQDN because that would include the AM unit e.g. `http://am-0.am-endpoints.otel.svc.cluster.local:9093`.
651.         The service URL as defined will remove the pod unit so (when ingress missing) the request goes to the K8s service at: http://am-endpoints.otel.svc.cluster.local:9093
652.         The service will then load balance between the units.
653.         This assumes that the FQDN is the interal FQDN for the socket and that the pod unit is always on the left side of the first ".". If those change, this code will need to be updated.
654.         """
655.         fqdn = self._fqdn.split(".", 1)[-1]
656. 
657.         return f"{self._scheme}://{fqdn}:{self._ports.api}"
658. 
659.     @property
660.     def _external_url(self) -> str:
661.         """Return the externally-reachable (public) address of the alertmanager api server."""
662.         return self.ingress.url or self._internal_url
663. 
664.     @property
665.     def _scheme(self) -> str:
666.         return "https" if self._tls_available else "http"
667. 
668. 
669. if __name__ == "__main__":
670.     main(AlertmanagerCharm)
671.
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/charmcraft.yaml**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/charmcraft.yaml

<details>
<summary>224 lines</summary>

```
1. # Copyright 2021 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. name: alertmanager-k8s
4. type: charm
5. summary: Alertmanager handles alerts sent by client applications.
6. description: >
7.   Alertmanager handles alerts sent by client applications such as the Prometheus server.
8.   It takes care of deduplicating, grouping, and routing them to the correct receiver integrations
9.   such as email, PagerDuty, or OpsGenie. It also takes care of silencing and inhibition of alerts.
10. 
11. links:
12.   documentation: https://discourse.charmhub.io/t/alertmanager-k8s-docs-index/5788
13.   website: https://charmhub.io/alertmanager-k8s
14.   source: https://github.com/canonical/alertmanager-k8s-operator
15.   issues: https://github.com/canonical/alertmanager-k8s-operator/issues
16. 
17. assumes:
18.   - k8s-api
19.   - juju >= 3.6
20. 
21. platforms:
22.   ubuntu@24.04:amd64:
23. 
24. parts:
25.   charm:
26.     source: .
27.     plugin: uv
28.     build-packages: [git]
29.     build-snaps: [astral-uv]
30.     override-build: |
31.       craftctl default
32.       git describe --always > $CRAFT_PART_INSTALL/version
33. 
34. containers:
35.   alertmanager:  # container key used by pebble
36.     resource: alertmanager-image
37.     mounts:
38.       - storage: data
39.         # nflogs and silences files go here. With a mounted storage for silences, they persist
40.         # across container restarts.
41.         # This path is passed to alertmanager via the `--storage.path` cli argument.
42.         location: /alertmanager
43. 
44. storage:
45.   data:
46.     type: filesystem
47.     description: >
48.       Storage path passed to alertmanager via --storage.path argument and used for nflog and silences snapshot
49. 
50. provides:
51.   alerting:
52.     # The provider (alertmanager) adds the following key-value pair to the relation data bag of
53.     # every alertmanager unit:
54.     #   "public_address": <ip_address>:<port>
55.     interface: alertmanager_dispatch
56.     optional: true
57.     description: |
58.       Integrates with other charms to send notifications when alert rules are triggered.
59.   karma-dashboard:
60.     interface: karma_dashboard
61.     optional: true
62.     description: |
63.       Links an entire Alertmanager cluster to a Karma[1] dashboard.
64.       Scaling alertmanager would automatically cause karma to group alerts by cluster.
65. 
66.       [1] https://charmhub.io/karma-k8s
67.   self-metrics-endpoint:
68.     interface: prometheus_scrape
69.     optional: true
70.     description: |
71.       Exposes the Prometheus metrics endpoint providing telemetry about the Alertmanager instance.
72.   grafana-dashboard:
73.     interface: grafana_dashboard
74.     optional: true
75.     description: |
76.       Forwards the built-in Grafana dashboard(s) for monitoring Alertmanager.
77.   grafana-source:
78.     interface: grafana_datasource
79.     optional: true
80.     description: |
81.       Configures Grafana to be able to use this Alertmanager instance as a datasource.
82.   provide-cmr-mesh:  # server-side-for-cmr-mesh
83.     interface: cross_model_mesh
84.     description: |
85.       Allow cross-model applications to make HTTP requests to alertmanager via the service mesh.
86.       This relation provides additional data required by the service mesh to create cross-model authorization policies
87. 
88.       Announce a subset of juju topology to the other side because a CMR obfuscates identity.
89.       Each pair of charm would need a separate relation of this kind, e.g. otelcol to loki and to prom.
90. 
91.       To make use of this relation, you also must have either the service-mesh relation in place (e.g. istio-beacon) or
92.       have the istio-beacon enroll the entire model (via its config option).
93.       (The service_mesh charm library manages both of these relations.)
94. 
95. requires:
96.   ingress:
97.     interface: ingress
98.     optional: true
99.     limit: 1
100.     description: |
101.       Alertmanager typically needs a "per app" ingress, which is available in the traefik charm[1].
102. 
103.       [1] https://charmhub.io/traefik-k8s
104.   remote-configuration:
105.     interface: alertmanager_remote_configuration
106.     optional: true
107.     limit: 1
108.   catalogue:
109.     interface: catalogue
110.     optional: true
111.     description: Add Alertmanager as an item to a Catalogue charm.
112.   certificates:
113.     interface: tls-certificates
114.     optional: true
115.     limit: 1
116.     description: |
117.       Certificate and key files for the alertmanager server to use to authenticate to client.
118.   tracing:
119.     interface: tracing
120.     optional: true
121.     limit: 1
122.     description: |
123.       Enables sending workload traces to a distributed tracing backend such as Tempo.
124.   service-mesh:
125.     limit: 1
126.     interface: service_mesh
127.     description: |
128.       Subscribe this charm into a service mesh and create authorization policies.
129.       We forward to the beacon our authorization policies.
130.       The beacon sends the pod and service labels required by this charm to join the mesh.
131.       This relation is a pre-requisite for using the provide-cmr-mesh relation.
132.   require-cmr-mesh:
133.     # TODO: remove this relation when this is fixed:
134.     #   https://github.com/canonical/istio-beacon-k8s-operator/issues/91
135.     interface: cross_model_mesh
136.     description: |
137.       Allow a cross-model application access to alertmanager via the service mesh.
138.       This relation provides additional data required by the service mesh to enforce cross-model authorization policies.
139. 
140. peers:
141.   replicas:
142.     interface: alertmanager_replica
143.     # assumed network type: private
144. 
145. resources:
146.   alertmanager-image:
147.     type: oci-image
148.     description: |
149.       OCI image for alertmanager. This charms makes the following assumptions about the image:
150.       - location of executable "alertmanager" is in the path
151.       - has `update-ca-certificates`
152.     upstream-source: ubuntu/alertmanager@sha256:822dd355903bd3ce7412502b7e4450c829a0b15e70ffa68381fc12630a6ed765  # renovate: oci-image tag: 0.31-24.04
153. 
154. config:
155.   options:
156.     config_file:
157.       type: string
158.       default: ""
159.       description: >
160.         Alertmanager configuration file (yaml), with the exclusion of the templates section.
161.         To send the contents of a file to this configuration option, the symbol `@` must be used.
162. 
163.         Usage: `juju config alertmanager config_file=@alertmanager.yaml`
164. 
165.         For more information on configuring the Alertmanager, refer to:
166.         https://www.prometheus.io/docs/alerting/latest/configuration/
167.     templates_file:
168.       type: string
169.       default: ""
170.       description: >
171.         Alertmanager templates definition file. This is a slight deviation from the official
172.         alertmanager config spec. All templates need to go into this single config option, instead of
173.         the 'templates' section of the main configuration file. The templates will be pushed to the
174.         workload container, and the configuration file will be updated accordingly. Templates can't
175.         be used without `config_file`.
176.         Refer to https://prometheus.io/docs/alerting/latest/notification_examples/ for more details
177.         on templates.
178.     web_external_url:
179.       type: string
180.       default: ""
181.       description: |
182.         DEPRECATED. This config option is no longer used, in favor of "skipPrefix".
183. 
184.         The URL under which Alertmanager is externally reachable (for example, if
185.         Alertmanager is served via a manually configured ingress).
186. 
187.         This config option is used for the `--web.external-url` alertmanager cli
188.         argument. If this charm config option is provided, it takes precedence over the
189.         URL provided over the "ingress" relation.
190. 
191.         Note: this config option shouldn't be included when you're using the "ingress"
192.         relation (e.g. traefik) - the charm will automatically assign an external url
193.         to `--web.external-url` when related to an ingress provider.
194. 
195.         This should be a complete URI, including scheme, or a  fully qualified subpath
196.         starting with `/`.
197.         If Alertmanager is being served directly from the root of a fully-qualified
198.         host or a bare A record, this may be omitted.
199.         If the URL has a path portion, Alertmanager will use it to prefix all HTTP
200.         endpoints.
201.     cpu:
202.       description: |
203.         K8s cpu resource limit, e.g. "1" or "500m". Default is unset (no limit). This value is used
204.         for the "limits" portion of the resource requirements (the "requests" portion is
205.         automatically deduced from it).
206.         See https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
207.       type: string
208.     memory:
209.       description: |
210.         K8s memory resource limit, e.g. "1Gi". Default is unset (no limit). This value is used
211.         for the "limits" portion of the resource requirements (the "requests" portion is
212.         automatically deduced from it).
213.         See https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
214.       type: string
215. 
216. actions:
217.   show-config:
218.     description: Show alertmanager config file.
219.   check-config:
220.     description: |
221.       Run `amtool` inside the workload to validate the configuration file, and
222.       return the resulting output. This can be useful for troubleshooting.
223. 
224.
```

</details>


---

<sub>⏱️ 22s</sub>

### 💬 Copilot

Now let me look at how conserver-charm uses `load_config()` in their charm.py:

---

<sub>⏱️ 23s</sub>

### ✅ `github-mcp-server-get_file_contents`

**src/charm.py**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "src/charm.py",
  "repo": "conserver-charm"
}
```

</details>

<details>
<summary>56 lines</summary>

```
successfully downloaded text file (SHA: aebe22463d11e710268a0aa0679114bc6acef057)#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm the application."""

import logging

import ops

from config import ConserverConfig
from conserver import Conserver

logger = logging.getLogger(__name__)


class ConserverCharm(ops.CharmBase):
    """Charm the application."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self.typed_config = self.load_config(ConserverConfig, errors="blocked")
        self.conserver = Conserver()
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.stop, self._on_stop)

    def _on_install(self, _):
        """Handle install event."""
        self.unit.status = ops.MaintenanceStatus("Installing conserver-server")
        self.conserver.install()

    def _on_config_changed(self, _):
        """Handle changes in configuration."""
        self.unit.status = ops.MaintenanceStatus("Updating configuration")
        self.conserver.write_conserver_config(self.typed_config.config_file)
        self.conserver.write_passwd_file(self.typed_config.passwd_file)
        # Restart service to apply changes
        self.conserver.reload(restart_on_failure=True, ignore_errors=True)
        self.set_status()

    def _on_start(self, _):
        """Handle start event."""
        self.conserver.start(ignore_errors=True)
        self.unit.set_workload_version(self.conserver.version)
        self.set_status()

    def _on_stop(self, _):
        """Handle stop event."""
        self.conserver.stop(ignore_errors=True)
        self.conserver.uninstall()

    def set_status(self):
        """Calculate and set the unit status."""
        if not self.typed_config.config_file:
            self.unit.status = ops.BlockedStatus("Missing config-file in config")
            return
        if not self.typed_config.passwd_file:
            self.unit.status = ops.BlockedStatus("Missing passwd-file in config")
            return

        if self.conserver.running:
            self.unit.status = ops.ActiveStatus()
        elif self.conserver.failed:
            self.unit.status = ops.BlockedStatus("Conserver service has failed")
        else:
            self.unit.status = ops.MaintenanceStatus()


if __name__ == "__main__":  # pragma: nocover
    ops.main(ConserverCharm)  # type: ignore
```

</details>


---

<sub>⏱️ 33s</sub>

### ✅ `bash`

**Check ops and pydantic versions**

$ grep -E "ops|pydantic" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/pyproject.toml

```
"ops",
  "pydantic>=2",  # traefik_k8s.v2.ingress
  "ops[testing]",
<exited with exit code 0>
```


---

<sub>⏱️ 44s</sub>

### ✅ `grep`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py**

"self\.config\[|model\.config\.get|web_external_url" (/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py)

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py:            web_external_url=self._external_url,
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py:            "cpu": self.model.config.get("cpu"),
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py:            "memory": self.model.config.get("memory"),
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py:        config = self.config["config_file"]
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py:            local_templates = cast(str, self.config["templates_file"]) or None
```


---

<sub>⏱️ 52s</sub>

### 💬 Copilot

Now I'll create the config module and update the charm:

---

<sub>⏱️ 52s</sub>

### ✅ `create`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/config.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/config.py

```
Created file /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/config.py with 395 characters
```


---

<sub>⏱️ 57s</sub>

### 💬 Copilot

Now update `charm.py` to import and use `AlertmanagerConfig`:

---

<sub>⏱️ 57s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 1s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 5s</sub>

### 💬 Copilot

Now update the three places that access config values:

---

<sub>⏱️ 1m 5s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 14s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 18s</sub>

### 💬 Copilot

Now let me check if `cast` is still needed elsewhere or can be removed:

---

<sub>⏱️ 1m 18s</sub>

### ✅ `grep`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py**

"cast" (/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py)

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py:from typing import List, Optional, Tuple, cast
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py:            local_config = yaml.safe_load(cast(str, config))
```


---

<sub>⏱️ 1m 27s</sub>

### 💬 Copilot

Let me run the tests to verify nothing is broken:

---

<sub>⏱️ 1m 28s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && python -m pytest tests/unit/ -x -q 2>&1 | head -80

```
bash: python: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 1m 32s</sub>

### ✅ `bash`

**Run unit tests with python3**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && python3 -m pytest tests/unit/ -x -q 2>&1 | tail -30

```
ImportError while loading conftest '/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/tests/unit/conftest.py'.
tests/unit/conftest.py:4: in <module>
    from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
E   ModuleNotFoundError: No module named 'charms'
<exited with exit code 0>
```


---

<sub>⏱️ 1m 39s</sub>

### ✅ `bash`

**Run unit tests via uv**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && uv run python -m pytest tests/unit/ -x -q 2>&1 | tail -30

<details>
<summary>10 lines</summary>

```
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/.venv/lib/python3.12/site-packages/paramiko/pkey.py:82: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  "cipher": algorithms.TripleDES,
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/.venv/lib/python3.12/site-packages/paramiko/transport.py:253: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  "class": algorithms.TripleDES,
ImportError while loading conftest '/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/tests/unit/conftest.py'.
tests/unit/conftest.py:4: in <module>
    from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
E   ModuleNotFoundError: No module named 'charms'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 50s</sub>

### ✅ `bash`

**Run unit tests via tox**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && uv run --with ops tox -e unit 2>&1 | tail -40

<details>
<summary>41 lines</summary>

```
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit/test_brute_isolated.py::test_startup_shutdown_sequence - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_charm_blocks_if_user_provided_config_with_templates - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_num_peers - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_pebble_layer_added - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_relation_data_provides_public_address - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_templates_file_not_created_if_user_provides_templates_without_config - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_templates_section_added_if_user_provided_templates - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_with_group_by - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_without_group_by - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_topology_is_not_added_if_user_provided_config_with_ellipsis - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_charm.py::TestWithoutInitialHooks::test_unit_status_around_pebble_ready - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_charm.py::TestActions::test_show_config - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_push_config_to_workload_on_startup.py::TestPushConfigToWorkloadOnStartup::test_charm_blocks_on_connection_error - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_push_config_to_workload_on_startup.py::TestPushConfigToWorkloadOnStartup::test_single_unit_cluster - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_push_config_to_workload_on_startup.py::TestInvalidConfig::test_charm_blocks_on_invalid_config_changed - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_push_config_to_workload_on_startup.py::TestInvalidConfig::test_charm_blocks_on_invalid_config_on_startup - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_configs_available_from_both_relation_data_bag_and_charm_config_block_charm - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_invalid_config_pushed_to_the_relation_data_bag_does_not_update_alertmanager_config - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_templates_pushed_to_relation_data_bag_are_saved_to_templates_file_in_alertmanager - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_valid_config_pushed_to_relation_data_bag_updates_alertmanager_config - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_no_peers - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
FAILED tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers - AttributeError: 'AlertmanagerCharm' object has no attribute 'load_config'. ...
ERROR tests/unit/test_brute_isolated.py::TestAlertingRelationDataUniformity::test_relation_data_is_the_same_for_all_related_apps[True-localhost] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_brute_isolated.py::TestAlertingRelationDataUniformity::test_relation_data_is_the_same_for_all_related_apps[True-am-0.endpoints.cluster.local] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_brute_isolated.py::TestAlertingRelationDataUniformity::test_relation_data_is_the_same_for_all_related_apps[False-localhost] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_brute_isolated.py::TestAlertingRelationDataUniformity::test_relation_data_is_the_same_for_all_related_apps[False-am-0.endpoints.cluster.local] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_server_scheme.py::TestServerScheme::test_initial_state_has_http_scheme_in_pebble_layer[True-localhost] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_server_scheme.py::TestServerScheme::test_initial_state_has_http_scheme_in_pebble_layer[True-am-0.endpoints.cluster.local] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_server_scheme.py::TestServerScheme::test_initial_state_has_http_scheme_in_pebble_layer[False-localhost] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_server_scheme.py::TestServerScheme::test_initial_state_has_http_scheme_in_pebble_layer[False-am-0.endpoints.cluster.local] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_server_scheme.py::TestServerScheme::test_alerting_relation_data_scheme[True-localhost] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_server_scheme.py::TestServerScheme::test_alerting_relation_data_scheme[True-am-0.endpoints.cluster.local] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_server_scheme.py::TestServerScheme::test_alerting_relation_data_scheme[False-localhost] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_server_scheme.py::TestServerScheme::test_alerting_relation_data_scheme[False-am-0.endpoints.cluster.local] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
= 22 failed, 23 passed, 3 skipped, 4 xfailed, 32 warnings, 12 errors in 2.63s ==
unit: exit 1 (6.33 seconds) /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3> uv run --frozen --isolated --extra=dev coverage run --source=/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src,/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/lib/charms/alertmanager_k8s -m pytest /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/tests/unit pid=10652
  unit: FAIL code 1 (6.41=setup[0.08]+cmd[6.33] seconds)
  evaluation failed :( (6.43 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 55s</sub>

### ✅ `bash`

**Check ops version**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && uv run python3 -c "import ops; print(ops.__version__)"

```
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
2.21.1
<exited with exit code 0>
```


---

<sub>⏱️ 1m 59s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/pyproject.toml**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/pyproject.toml

<details>
<summary>92 lines</summary>

```
1. # Copyright 2021 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. [project]
4. name = "alertmanager-k8s"
5. version = "0.0"
6. requires-python = "~=3.8"
7. 
8. dependencies = [
9.   "ops",
10.   "pyyaml",
11.   "lightkube>=0.11",  # observability_libs
12.   "lightkube-models",  # observability_libs
13.   "jsonschema", # traefik_k8s, tls_certificates
14.   "cryptography",  # tls_certificates
15.   "pydantic>=2",  # traefik_k8s.v2.ingress
16.   "opentelemetry-exporter-otlp-proto-http>=1.21.0",  # tracing
17.   "tenacity",
18.   "cosl",
19.   "charmed-service-mesh-helpers>=0.2.0",
20.   "lightkube-extensions",
21. ]
22. 
23. [project.optional-dependencies]
24. dev = [
25.   # Linting
26.   "ruff",
27.   "codespell",
28.   # Static
29.   "pyright<1.1.399", # 1.1.399 vendors typeshed that dropped Python 3.8 support
30.   # Unit
31.   "pytest",
32.   "coverage[toml]",
33.   "deepdiff",
34.   "hypothesis",
35.   "validators>=0.21.2",
36.   "ops[testing]",
37.   "pytest-interface-tester>0.3",
38.   # Integration
39.   "juju<=3.3.0,>=3.0",
40.   "websockets<14.0",
41.   "pytest-operator",
42.   "pytest-httpserver",
43.   "sh",
44. ]
45. 
46. # Testing tools configuration
47. [tool.coverage.run]
48. branch = true
49. 
50. [tool.coverage.report]
51. show_missing = true
52. 
53. # Formatting tools configuration
54. [tool.black]
55. line-length = 99
56. target-version = ["py38"]
57. 
58. # Linting tools configuration
59. [tool.ruff]
60. line-length = 99
61. extend-exclude = ["__pycache__", "*.egg_info"]
62. 
63. [tool.ruff.lint]
64. select = ["E", "W", "F", "C", "N", "R", "D", "I001"]
65. # Ignore E501 because using black creates errors with this
66. # Ignore D107 Missing docstring in __init__
67. ignore = ["E501", "D107", "N818", "RET504"]
68. # D100, D101, D102, D103: Ignore missing docstrings in tests
69. per-file-ignores = {"tests/*" = ["D100","D101","D102","D103"]}
70. 
71. [tool.ruff.lint.pydocstyle]
72. convention = "google"
73. 
74. # Static analysis tools configuration
75. [tool.pyright]
76. extraPaths = ["src", "lib"]
77. pythonVersion = "3.8"
78. pythonPlatform = "All"
79. exclude = [
80.   "tests/integration/remote_configuration_tester/**",
81. ]
82. 
83. [tool.pytest.ini_options]
84. minversion = "6.0"
85. log_cli_level = "INFO"
86. asyncio_mode = "auto"
87. addopts = "--tb=native --verbose --capture=no --log-cli-level=INFO"
88. 
89. [tool.codespell]
90. skip = ".git,.tox,build,venv*"
91. ignore-words-list = "assertIn"
92.
```

</details>


---

<sub>⏱️ 2m 3s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/pyproject.toml**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/pyproject.toml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/pyproject.toml updated with changes.
```


---

<sub>⏱️ 2m 8s</sub>

### ✅ `bash`

**Update ops in lock file**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && uv lock --upgrade-package ops 2>&1 | tail -5

```
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Resolved 146 packages in 345ms
Updated ops v2.21.1 -> v2.23.2, v3.6.0
Updated ops-scenario v7.21.1 -> v7.23.2, v8.6.0
<exited with exit code 0>
```


---

<sub>⏱️ 2m 13s</sub>

### ✅ `bash`

**Sync dependencies**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && uv sync 2>&1 | tail -5

<details>
<summary>6 lines</summary>

```
- typing-inspect==0.9.0
 - validators==0.35.0
 - wcwidth==0.2.13
 - websockets==13.1
 - werkzeug==3.1.3
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 17s</sub>

### ✅ `bash`

**Verify ops version updated**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && uv run python3 -c "import ops; print(ops.__version__)"

```
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
3.6.0
<exited with exit code 0>
```


---

<sub>⏱️ 3m 21s</sub>

### ✅ `bash`

**Run unit tests again**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && uv run tox -e unit 2>&1 | tail -20

```
<command with shellId: 9 is still running after 60 seconds. The command is still running but hasn't produced output yet. It may be waiting for input or still processing. Use read_bash to continue waiting, write_bash if you think it needs input, or stop_bash to stop it.>
```


---

<sub>⏱️ 4m 17s</sub>

### ✅ `read_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "9",
  "delay": 60
}
```

</details>

<details>
<summary>19 lines</summary>

```
/home/ubuntu/.cache/uv/builds-v0/.tmpm9DiBK/lib/python3.12/site-packages/ops/_private/harness.py:1109: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/1'.
    warnings.warn(

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/.cache/uv/builds-v0/.tmpm9DiBK/lib/python3.12/site-packages/ops/_private/harness.py:1109: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/2'.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_charm_blocks_if_user_provided_config_with_templates - AssertionError: ActiveStatus('') is not an instance of <class 'ops.model.Bl...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_templates_section_added_if_user_provided_templates - ops.pebble.PathError: not-found - stat /etc/alertmanager/templates.tmpl: no...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_with_group_by - AssertionError: Lists differ: ['juju_application', 'juju_model', 'juju_mode...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_without_group_by - KeyError: 'not a real config'
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_topology_is_not_added_if_user_provided_config_with_ellipsis - AssertionError: Lists differ: ['juju_model', 'juju_application', 'juju_mode...
FAILED tests/unit/test_push_config_to_workload_on_startup.py::TestInvalidConfig::test_charm_blocks_on_invalid_config_changed - AssertionError: ActiveStatus('') is not an instance of <class 'ops.model.Bl...
FAILED tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_configs_available_from_both_relation_data_bag_and_charm_config_block_charm - AssertionError: ActiveStatus('') != BlockedStatus('Multiple configs detected')
= 7 failed, 50 passed, 3 skipped, 4 xfailed, 310 warnings in 107.94s (0:01:47) =
unit: exit 1 (111.80 seconds) /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3> uv run --frozen --isolated --extra=dev coverage run --source=/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src,/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/lib/charms/alertmanager_k8s -m pytest /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/tests/unit pid=10988
  unit: FAIL code 1 (111.80=setup[0.01]+cmd[111.80] seconds)
  evaluation failed :( (111.82 seconds)
<command with id: 9 exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 30s</sub>

### 💬 Copilot

Let me check the failing tests to understand what's happening:

---

<sub>⏱️ 4m 38s</sub>

### ✅ `bash`

**Run failing test with details**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && uv run tox -e unit -- tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_without_group_by -s 2>&1 | tail -30

<details>
<summary>26 lines</summary>

```
WARNING  alertmanager:alertmanager.py:335 cannot determine if reload succeeded
=============================== warnings summary ===============================
../../../home/ubuntu/.cache/uv/builds-v0/.tmpq5Gfk6/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
  /home/ubuntu/.cache/uv/builds-v0/.tmpq5Gfk6/lib/python3.12/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

../../../home/ubuntu/.cache/uv/builds-v0/.tmpq5Gfk6/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:293
  /home/ubuntu/.cache/uv/builds-v0/.tmpq5Gfk6/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:293: PydanticDeprecatedSince20: `json_encoders` is deprecated. See https://docs.pydantic.dev/2.11/concepts/serialization/#custom-serializers for alternatives. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(

tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_without_group_by
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/tests/unit/test_charm.py:29: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_without_group_by
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/lib/charms/tls_certificates_interface/v4/tls_certificates.py:1717: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    if not JujuVersion.from_environ().has_secrets:

tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_without_group_by
tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_without_group_by
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/lib/charms/karma_k8s/v0/karma_dashboard.py:332: PydanticDeprecatedSince20: The `dict` method is deprecated; use `model_dump` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    as_dict = data.dict()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_without_group_by - KeyError: 'not a real config'
======================== 1 failed, 6 warnings in 3.13s =========================
unit: exit 1 (6.86 seconds) /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3> uv run --frozen --isolated --extra=dev coverage run --source=/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src,/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/lib/charms/alertmanager_k8s -m pytest /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/tests/unit tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_without_group_by -s pid=11825
  unit: FAIL code 1 (6.86=setup[0.01]+cmd[6.86] seconds)
  evaluation failed :( (6.88 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 44s</sub>

### ✅ `bash`

**Find the 'not a real config' test code**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && grep -n "not a real config" tests/unit/test_charm.py

```
85:        new_config = yaml.dump({"not a real config": "but good enough for testing"})
91:        self.assertEqual(updated_config["not a real config"], "but good enough for testing")
<exited with exit code 0>
```


---

<sub>⏱️ 4m 48s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/tests/unit/test_charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/tests/unit/test_charm.py (lines 75-120)

<details>
<summary>46 lines</summary>

```
75.             "url": "http://fqdn:9093",
76.             "public_address": expected_address,
77.             "scheme": "http",
78.         }
79.         self.assertEqual(expected_rel_data, rel.data[self.harness.charm.unit])
80. 
81.     @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
82.     @k8s_resource_multipatch
83.     @patch.object(AlertmanagerCharm, "_update_ca_certs", lambda *a, **kw: None)
84.     def test_topology_added_if_user_provided_config_without_group_by(self, *unused):
85.         new_config = yaml.dump({"not a real config": "but good enough for testing"})
86.         self.harness.update_config({"config_file": new_config})
87.         updated_config = yaml.safe_load(
88.             self.harness.charm.container.pull(self.harness.charm._config_path)
89.         )
90. 
91.         self.assertEqual(updated_config["not a real config"], "but good enough for testing")
92.         self.assertListEqual(
93.             sorted(updated_config["route"]["group_by"]),
94.             sorted(["juju_model", "juju_application", "juju_model_uuid"]),
95.         )
96. 
97.     @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
98.     @k8s_resource_multipatch
99.     @patch.object(AlertmanagerCharm, "_update_ca_certs", lambda *a, **kw: None)
100.     def test_topology_added_if_user_provided_config_with_group_by(self, *unused):
101.         new_config = yaml.dump({"route": {"group_by": ["alertname", "juju_model"]}})
102.         self.harness.update_config({"config_file": new_config})
103.         updated_config = yaml.safe_load(
104.             self.harness.charm.container.pull(self.harness.charm._config_path)
105.         )
106. 
107.         self.assertListEqual(
108.             sorted(updated_config["route"]["group_by"]),
109.             sorted(["alertname", "juju_model", "juju_application", "juju_model_uuid"]),
110.         )
111. 
112.     @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
113.     @k8s_resource_multipatch
114.     @patch.object(AlertmanagerCharm, "_update_ca_certs", lambda *a, **kw: None)
115.     def test_topology_is_not_added_if_user_provided_config_with_ellipsis(self, *unused):
116.         """The special value '...' effectively disables aggregation entirely.
117. 
118.         Ref: https://prometheus.io/docs/alerting/latest/configuration/#route
119.         """
120.         new_config = yaml.dump({"route": {"group_by": ["..."]}})
```

</details>


---

<sub>⏱️ 5m 24s</sub>

### 💬 Copilot

The issue is that `self.typed_config` set in `__init__` becomes stale in harness tests when config changes. I need to make it a property instead:

---

<sub>⏱️ 5m 24s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 29s</sub>

### 💬 Copilot

Now add a `typed_config` property. I'll add it near the other properties after `_resource_reqs_from_config`:

---

<sub>⏱️ 5m 29s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 33s</sub>

### 💬 Copilot

Wait, I need to add the property separately. Let me fix this properly:

---

<sub>⏱️ 5m 33s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py (lines 284-340)

<details>
<summary>57 lines</summary>

```
284. 
285.     @property
286.     def _catalogue_item(self) -> CatalogueItem:
287.         api_endpoints = {"Alerts": "/api/v2/alerts"}
288. 
289.         return CatalogueItem(
290.             name="Alertmanager",
291.             icon="bell-alert",
292.             url=self._external_url,
293.             description=(
294.                 "Alertmanager receives alerts from supporting applications, such as "
295.                 "Prometheus or Loki, then deduplicates, groups and routes them to "
296.                 "the configured receiver(s)."
297.             ),
298.             api_docs="https://github.com/prometheus/alertmanager/blob/main/api/v2/openapi.yaml",
299.             api_endpoints={
300.                 key: f"{self._external_url}{path}" for key, path in api_endpoints.items()
301.             },
302.         )
303. 
304.     @property
305.     def self_scraping_job(self):
306.         """The self-monitoring scrape job."""
307.         # We assume that scraping, especially self-monitoring, is in-cluster.
308.         # This assumption is necessary because the local CA signs CSRs with FQDN as the SAN DNS.
309.         # If prometheus were to scrape an ingress URL instead, it would error out with:
310.         # x509: cannot validate certificate.
311.         peer_api_netlocs = [
312.             f"{hostname}:{self._ports.api}"
313.             for hostname in self._get_peer_hostnames(include_this_unit=True)
314.         ]
315. 
316.         config = {
317.             "scheme": self._scheme,
318.             "metrics_path": "/metrics",
319.             "static_configs": [{"targets": peer_api_netlocs}],
320.         }
321. 
322.         return [config]
323. 
324.     def _resource_reqs_from_config(self) -> ResourceRequirements:
325.         limits = {
326.             "cpu": self.typed_config.cpu,
327.             "memory": self.typed_config.memory,
328.         }
329.         limits = {
330.             "cpu": self.typed_config.cpu,
331.             "memory": self.typed_config.memory,
332.         }
333.         requests = {"cpu": "0.25", "memory": "200Mi"}
334.         return adjust_resource_requirements(limits, requests, adhere_to_requests=True)
335. 
336.     def _on_k8s_patch_failed(self, event: K8sResourcePatchFailedEvent):
337.         self.unit.status = BlockedStatus(str(event.message))
338. 
339.     def _handle_ingress(self, _):
340.         if url := self.ingress.url:
```

</details>


---

<sub>⏱️ 5m 39s</sub>

### 💬 Copilot

I see there's a duplication issue. Let me fix it:

---

<sub>⏱️ 5m 39s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 39s</sub>

### ✅ `bash`

**Run unit tests again**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && uv run tox -e unit 2>&1 | tail -20

<details>
<summary>20 lines</summary>

```
warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====== 57 passed, 3 skipped, 4 xfailed, 311 warnings in 105.60s (0:01:45) ======
unit: commands[1]> uv run --frozen --isolated --extra=dev coverage report
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 110 packages in 51ms
Name                                                                  Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------------------------------------
lib/charms/alertmanager_k8s/v0/alertmanager_remote_configuration.py     124     15     20      2    88%   52-54, 184, 228-229, 377, 385, 405-406, 417, 449-451, 471-472
lib/charms/alertmanager_k8s/v1/alertmanager_dispatch.py                  98      8     16      4    89%   114, 123-132, 222->exit, 233->232, 239-241, 245
src/alertmanager.py                                                     133     22     28     11    78%   41, 45, 129, 144, 152, 161, 169-170, 230, 240-241, 257, 265-266, 277-278, 283-284, 297, 324, 336-337
src/alertmanager_client.py                                              124     30     10      3    74%   55, 73-74, 84, 114, 121-122, 162-167, 193-202, 314-323, 345-354
src/charm.py                                                            274     39     50     10    83%   279, 330-335, 338, 341-345, 349-358, 364, 387-388, 420-422, 476-478, 488->505, 492-499, 512->518, 533-535, 542, 581, 599, 604-605, 641, 676
src/config.py                                                             8      0      0      0   100%
src/config_builder.py                                                    67      3     16      2    92%   73->75, 133-135
-----------------------------------------------------------------------------------------------------------------
TOTAL                                                                   828    117    140     32    83%
  unit: OK (109.78=setup[0.01]+cmd[109.49,0.29] seconds)
  congratulations :) (109.80 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 44s</sub>

### 💬 Copilot

All 57 tests pass. Let me verify the final state of the changes:

---

<sub>⏱️ 7m 44s</sub>

### ✅ `bash`

**Show changed files**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && git --no-pager diff --stat

```
pyproject.toml |  2 +-
 src/charm.py   | 14 ++++++++++----
 uv.lock        | 93 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-------------------
 3 files changed, 85 insertions(+), 24 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 7m 49s</sub>

### ✅ `bash`

**Show diff of code changes**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C3 && git --no-pager diff pyproject.toml src/charm.py

<details>
<summary>54 lines</summary>

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 140d222..7fc19ad 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -6,7 +6,7 @@ version = "0.0"
 requires-python = "~=3.8"
 
 dependencies = [
-  "ops",
+  "ops>=2.23.0",
   "pyyaml",
   "lightkube>=0.11",  # observability_libs
   "lightkube-models",  # observability_libs
diff --git a/src/charm.py b/src/charm.py
index ae92826..6982878 100755
--- a/src/charm.py
+++ b/src/charm.py
@@ -55,6 +55,7 @@ from alertmanager import (
     WorkloadManager,
     WorkloadManagerError,
 )
+from config import AlertmanagerConfig
 from config_builder import ConfigBuilder, ConfigError
 
 logger = logging.getLogger(__name__)
@@ -320,10 +321,15 @@ class AlertmanagerCharm(CharmBase):
 
         return [config]
 
+    @property
+    def typed_config(self) -> AlertmanagerConfig:
+        """Return the current charm configuration as a typed object."""
+        return self.load_config(AlertmanagerConfig, errors="blocked")
+
     def _resource_reqs_from_config(self) -> ResourceRequirements:
         limits = {
-            "cpu": self.model.config.get("cpu"),
-            "memory": self.model.config.get("memory"),
+            "cpu": self.typed_config.cpu,
+            "memory": self.typed_config.memory,
         }
         requests = {"cpu": "0.25", "memory": "200Mi"}
         return adjust_resource_requirements(limits, requests, adhere_to_requests=True)
@@ -403,7 +409,7 @@ class AlertmanagerCharm(CharmBase):
         return None
 
     def _get_local_config(self) -> Optional[Tuple[Optional[dict], Optional[str]]]:
-        config = self.config["config_file"]
+        config = self.typed_config.config_file
         if config:
             local_config = yaml.safe_load(cast(str, config))
 
@@ -415,7 +421,7 @@ class AlertmanagerCharm(CharmBase):
                 logger.error(msg)
                 raise ConfigUpdateFailure(msg)
 
-            local_templates = cast(str, self.config["templates_file"]) or None
+            local_templates = self.typed_config.templates_file or None
             return local_config, local_templates
         return None
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 59s</sub>

### 💬 Copilot

All tests pass. Here's a summary of the changes made:

1. **`src/config.py`** (new file): Defines `AlertmanagerConfig(BaseModel)` with all five charm config options as typed Pydantic fields (`config_file`, `templates_file`, `web_external_url` as `str`, and `cpu`, `memory` as `Optional[str]`).

2. **`src/charm.py`**: 
   - Imports `AlertmanagerConfig` from the new module
   - Adds a `typed_config` property that calls `self.load_config(AlertmanagerConfig, errors="blocked")` (as a property rather than an `__init__` assignment, so it's always current in harness tests)
   - Replaces `self.model.config.get("cpu")` / `self.model.config.get("memory")` with `self.typed_config.cpu` / `self.typed_config.memory`
   - Replaces `self.config["config_file"]` and `cast(str, self.config["templates_file"])` with `self.typed_config.config_file` and `self.typed_config.templates_file`

3. **`pyproject.toml`** / **`uv.lock`**: Bumped the `ops` dependency to `\>=2.23.0` (which introduced `load_config()`) and updated the lock file accordingly.

---

<sub>⏱️ 7m 59s</sub>

### ✅ `task_complete`

**Created `src/config.py` with a Pydantic `AlertmanagerConfig(BaseModel)` class mirroring all charm config options. Updated `src/charm.py` to import it, add a `typed_config` property using `self.load_config(AlertmanagerConfig, errors="blocked")`, and replace all `self.config[...]`/`self.model.config.get(...)` accesses with `self.typed_config.*`. Bumped `ops` to `>=2.23.0` in `pyproject.toml` and updated `uv.lock`. All 57 unit tests pass.**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Created `src/config.py` with a Pydantic `AlertmanagerConfig(BaseModel)` class mirroring all charm config options. Updated `src/charm.py` to import it, add a `typed_config` property using `self.load_config(AlertmanagerConfig, errors=\"blocked\")`, and replace all `self.config[...]`/`self.model.config.get(...)` accesses with `self.typed_config.*`. Bumped `ops` to `>=2.23.0` in `pyproject.toml` and updated `uv.lock`. All 57 unit tests pass."
}
```

</details>

```
Created `src/config.py` with a Pydantic `AlertmanagerConfig(BaseModel)` class mirroring all charm config options. Updated `src/charm.py` to import it, add a `typed_config` property using `self.load_config(AlertmanagerConfig, errors="blocked")`, and replace all `self.config[...]`/`self.model.config.get(...)` accesses with `self.typed_config.*`. Bumped `ops` to `>=2.23.0` in `pyproject.toml` and updated `uv.lock`. All 57 unit tests pass.
```


---

<sub>⏱️ 8m 3s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 8m 8s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 8m 12s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 8m 17s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 8m 22s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 8m 27s</sub>

### ❌ Error

Execution failed: Error: Failed to get response from the AI model; retried 5 times (total retry wait time: 5.99327948352514 seconds) Last error: Unknown error

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
