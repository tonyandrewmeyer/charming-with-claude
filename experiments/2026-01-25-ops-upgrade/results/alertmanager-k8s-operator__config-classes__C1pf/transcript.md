# 🤖 Copilot CLI Session

> **Session ID:** `dbc91bc5-d629-45ab-812e-a7bbddea645b`
> **Duration:** 10m 10s
> **Exported:** 3/11/2026, 1:14:07 PM

<sub>⏱️ 4s</sub>

### 👤 User

This charm could benefit from config classes (load_config). There is a skill available for applying this change.

---

<sub>⏱️ 11s</sub>

### ✅ `bash`

**Find Python source files and config options**

$ find /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src -type f -name "*.py" | head -20 && echo "---" && cat /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/charmcraft.yaml | grep -A 100 "^config:"

<details>
<summary>68 lines</summary>

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/alertmanager_client.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/alertmanager.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/config_builder.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py
---
config:
  options:
    config_file:
      type: string
      default: ""
      description: >
        Alertmanager configuration file (yaml), with the exclusion of the templates section.
        To send the contents of a file to this configuration option, the symbol `@` must be used.

        Usage: `juju config alertmanager config_file=@alertmanager.yaml`

        For more information on configuring the Alertmanager, refer to:
        https://www.prometheus.io/docs/alerting/latest/configuration/
    templates_file:
      type: string
      default: ""
      description: >
        Alertmanager templates definition file. This is a slight deviation from the official
        alertmanager config spec. All templates need to go into this single config option, instead of
        the 'templates' section of the main configuration file. The templates will be pushed to the
        workload container, and the configuration file will be updated accordingly. Templates can't
        be used without `config_file`.
        Refer to https://prometheus.io/docs/alerting/latest/notification_examples/ for more details
        on templates.
    web_external_url:
      type: string
      default: ""
      description: |
        DEPRECATED. This config option is no longer used, in favor of "skipPrefix".

        The URL under which Alertmanager is externally reachable (for example, if
        Alertmanager is served via a manually configured ingress).

        This config option is used for the `--web.external-url` alertmanager cli
        argument. If this charm config option is provided, it takes precedence over the
        URL provided over the "ingress" relation.

        Note: this config option shouldn't be included when you're using the "ingress"
        relation (e.g. traefik) - the charm will automatically assign an external url
        to `--web.external-url` when related to an ingress provider.

        This should be a complete URI, including scheme, or a  fully qualified subpath
        starting with `/`.
        If Alertmanager is being served directly from the root of a fully-qualified
        host or a bare A record, this may be omitted.
        If the URL has a path portion, Alertmanager will use it to prefix all HTTP
        endpoints.
    cpu:
      description: |
        K8s cpu resource limit, e.g. "1" or "500m". Default is unset (no limit). This value is used
        for the "limits" portion of the resource requirements (the "requests" portion is
        automatically deduced from it).
        See https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
      type: string
    memory:
      description: |
        K8s memory resource limit, e.g. "1Gi". Default is unset (no limit). This value is used
        for the "limits" portion of the resource requirements (the "requests" portion is
        automatically deduced from it).
        See https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
      type: string

actions:
  show-config:
    description: Show alertmanager config file.
  check-config:
    description: |
      Run `amtool` inside the workload to validate the configuration file, and
      return the resulting output. This can be useful for troubleshooting.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 15s</sub>

### ✅ `bash`

**Read the main charm file**

$ cat /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py

<details>
<summary>571 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

"""A Juju charm for alertmanager."""

import logging
import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import List, Optional, Tuple, cast
from urllib.parse import urlparse

import yaml
from charms.alertmanager_k8s.v0.alertmanager_remote_configuration import (
    RemoteConfigurationRequirer,
)
from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerProvider
from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.grafana_k8s.v0.grafana_source import GrafanaSourceProvider
from charms.istio_beacon_k8s.v0.service_mesh import ServiceMeshConsumer, UnitPolicy
from charms.karma_k8s.v0.karma_dashboard import KarmaProvider
from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
    K8sResourcePatchFailedEvent,
    KubernetesComputeResourcesPatch,
    ResourceRequirements,
    adjust_resource_requirements,
)
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
from charms.tls_certificates_interface.v4.tls_certificates import (
    CertificateRequestAttributes,
    TLSCertificatesRequiresV4,
)
from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer
from ops.charm import ActionEvent, CharmBase
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
    MaintenanceStatus,
    OpenedPort,
    Relation,
    WaitingStatus,
)
from ops.pebble import PathError, ProtocolError  # type: ignore

from alertmanager import (
    ConfigFileSystemState,
    ConfigUpdateFailure,
    WorkloadManager,
    WorkloadManagerError,
)
from config_builder import ConfigBuilder, ConfigError

logger = logging.getLogger(__name__)


@dataclass
class TLSConfig:
    """TLS configuration received by the charm over the `certificates` relation."""

    server_cert: str
    ca_cert: str
    private_key: str


@trace_charm(
    tracing_endpoint="_charm_tracing_endpoint",
    server_cert="_charm_tracing_ca_cert",
    extra_types=(
        AlertmanagerProvider,
        TLSCertificatesRequiresV4,
        IngressPerAppRequirer,
        KubernetesComputeResourcesPatch,
        RemoteConfigurationRequirer,
    ),
)
class AlertmanagerCharm(CharmBase):
    """A Juju charm for alertmanager."""

    # Container name must match metadata.yaml
    # Layer name is used for the layer label argument in container.add_layer
    # Service name matches charm name for consistency
    _container_name = _service_name = "alertmanager"
    _relations = SimpleNamespace(
        alerting="alerting", peer="replicas", remote_config="remote_configuration"
    )
    _ports = SimpleNamespace(api=9093, ha=9094)

    # path, inside the workload container, to the alertmanager and amtool configuration files
    # the amalgamated templates file goes in the same folder as the main configuration file
    _config_path = "/etc/alertmanager/alertmanager.yml"
    _web_config_path = "/etc/alertmanager/alertmanager-web-config.yml"
    _amtool_config_path = "/etc/amtool/config.yml"
    _templates_path = "/etc/alertmanager/templates.tmpl"

    _server_cert_path = "/etc/alertmanager/alertmanager.cert.pem"
    _key_path = "/etc/alertmanager/alertmanager.key.pem"
    _ca_cert_path = "/usr/local/share/ca-certificates/cos-ca.crt"

    def __init__(self, *args):
        super().__init__(*args)
        self.container = self.unit.get_container(self._container_name)
        self._fqdn = socket.getfqdn()

        self._csr_attributes = CertificateRequestAttributes(
            # the `common_name` field is required but limited to 64 characters.
            # since it's overridden by sans, we can use a short,
            # constrained value like app name.
            common_name=self.app.name,
            sans_dns=frozenset((self._fqdn,)),
        )
        self._cert_requirer = TLSCertificatesRequiresV4(
            charm=self,
            relationship_name="certificates",
            certificate_requests=[self._csr_attributes],
        )
        self.framework.observe(
            self._cert_requirer.on.certificate_available,  # pyright: ignore
            self._on_certificate_available,
        )

        self.ingress = IngressPerAppRequirer(
            self,
            port=self.api_port,
            scheme=self._scheme,
            strip_prefix=True,
            redirect_https=True,
        )
        self.framework.observe(self.ingress.on.ready, self._handle_ingress)  # pyright: ignore
        self.framework.observe(self.ingress.on.revoked, self._handle_ingress)  # pyright: ignore

        self.alertmanager_provider = AlertmanagerProvider(
            self,
            relation_name=self._relations.alerting,
            external_url=self._internal_url,  # TODO See 'TODO' below, about external_url
        )

        self.grafana_dashboard_provider = GrafanaDashboardProvider(charm=self)
        self.grafana_source_provider = GrafanaSourceProvider(
            charm=self,
            source_type="alertmanager",
            source_url=self.ingress.url or self._service_url,
            is_ingress_per_app=True, # We want only one alertmanager datasource (unit) to be listed in grafana.
            refresh_event=[
                self.ingress.on.ready,
                self.ingress.on.revoked,
                self.on.update_status,
                self._cert_requirer.on.certificate_available,
            ],
        )
        self.karma_provider = KarmaProvider(self, "karma-dashboard")
        self.remote_configuration = RemoteConfigurationRequirer(self)

        self.set_ports()

        self.resources_patch = KubernetesComputeResourcesPatch(
            self,
            self._container_name,
            resource_reqs_func=self._resource_reqs_from_config,
        )
        self.framework.observe(
            self.resources_patch.on.patch_failed,
            self._on_k8s_patch_failed,  # pyright: ignore
        )

        # Self-monitoring
        self._scraping = MetricsEndpointProvider(
            self,
            relation_name="self-metrics-endpoint",
            jobs=self.self_scraping_job,
            refresh_event=[
                self.on.update_status,
                self.ingress.on.ready,  # pyright: ignore
                self.ingress.on.revoked,  # pyright: ignore
                self.on["ingress"].relation_changed,
                self.on["ingress"].relation_departed,
                self._cert_requirer.on.certificate_available,  # pyright: ignore
            ],
        )
        self._tracing = TracingEndpointRequirer(self, protocols=["otlp_http"])
        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
            self._tracing, self._ca_cert_path
        )

        self.catalog = CatalogueConsumer(charm=self, item=self._catalogue_item)

        self._mesh = ServiceMeshConsumer(
            self,
            policies=[
                UnitPolicy(
                    relation="alerting",
                    ports=[self.api_port],
                ),
                UnitPolicy(
                    relation="grafana-source",
                    ports=[self.api_port],
                ),
                UnitPolicy(
                    relation="self-metrics-endpoint",
                    ports=[self.api_port],
                ),
            ],
        )

        # Core lifecycle events
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.start, self._on_start)

        peer_ha_netlocs = [
            f"{hostname}:{self._ports.ha}"
            for hostname in self._get_peer_hostnames(include_this_unit=False)
        ]

        self.alertmanager_workload = WorkloadManager(
            self,
            container_name=self._container_name,
            peer_netlocs=peer_ha_netlocs,
            api_port=self.api_port,
            ha_port=self._ports.ha,
            web_external_url=self._external_url,
            web_route_prefix="/",
            config_path=self._config_path,
            web_config_path=self._web_config_path,
            tls_enabled=lambda: self._tls_available,
            cafile=self._ca_cert_path if Path(self._ca_cert_path).exists() else None,
        )
        self.framework.observe(
            # The workload manager too observes pebble ready, but still need this here because
            # of the common exit hook (otherwise would need to pass the common exit hook as
            # a callback).
            self.on.alertmanager_pebble_ready,  # pyright: ignore
            self._on_pebble_ready,
        )
        self.framework.observe(self.on.update_status, self._on_update_status)
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)

        # Remote configuration events
        self.framework.observe(
            self.remote_configuration.on.remote_configuration_changed,  # pyright: ignore
            self._on_remote_configuration_changed,
        )

        # Peer relation events
        self.framework.observe(
            self.on[self._relations.peer].relation_joined, self._on_peer_relation_joined
        )
        self.framework.observe(
            self.on[self._relations.peer].relation_changed, self._on_peer_relation_changed
        )

        # Action events
        self.framework.observe(
            self.on.show_config_action,
            self._on_show_config_action,  # pyright: ignore
        )
        self.framework.observe(
            self.on.check_config_action,
            self._on_check_config,  # pyright: ignore
        )

    def set_ports(self):
        """Open necessary (and close no longer needed) workload ports."""
        planned_ports = {
            OpenedPort("tcp", self._ports.api),
            OpenedPort("tcp", self._ports.ha),
        }
        actual_ports = self.unit.opened_ports()

        # Ports may change across an upgrade, so need to sync
        ports_to_close = actual_ports.difference(planned_ports)
        for p in ports_to_close:
            self.unit.close_port(p.protocol, p.port)

        new_ports_to_open = planned_ports.difference(actual_ports)
        for p in new_ports_to_open:
            self.unit.open_port(p.protocol, p.port)

    @property
    def _catalogue_item(self) -> CatalogueItem:
        api_endpoints = {"Alerts": "/api/v2/alerts"}

        return CatalogueItem(
            name="Alertmanager",
            icon="bell-alert",
            url=self._external_url,
            description=(
                "Alertmanager receives alerts from supporting applications, such as "
                "Prometheus or Loki, then deduplicates, groups and routes them to "
                "the configured receiver(s)."
            ),
            api_docs="https://github.com/prometheus/alertmanager/blob/main/api/v2/openapi.yaml",
            api_endpoints={
                key: f"{self._external_url}{path}" for key, path in api_endpoints.items()
            },
        )

    @property
    def self_scraping_job(self):
        """The self-monitoring scrape job."""
        # We assume that scraping, especially self-monitoring, is in-cluster.
        # This assumption is necessary because the local CA signs CSRs with FQDN as the SAN DNS.
        # If prometheus were to scrape an ingress URL instead, it would error out with:
        # x509: cannot validate certificate.
        peer_api_netlocs = [
            f"{hostname}:{self._ports.api}"
            for hostname in self._get_peer_hostnames(include_this_unit=True)
        ]

        config = {
            "scheme": self._scheme,
            "metrics_path": "/metrics",
            "static_configs": [{"targets": peer_api_netlocs}],
        }

        return [config]

    def _resource_reqs_from_config(self) -> ResourceRequirements:
        limits = {
            "cpu": self.model.config.get("cpu"),
            "memory": self.model.config.get("memory"),
        }
        requests = {"cpu": "0.25", "memory": "200Mi"}
        return adjust_resource_requirements(limits, requests, adhere_to_requests=True)

    def _on_k8s_patch_failed(self, event: K8sResourcePatchFailedEvent):
        self.unit.status = BlockedStatus(str(event.message))

    def _handle_ingress(self, _):
        if url := self.ingress.url:
            logger.info("Ingress is ready: '%s'.", url)
        else:
            logger.info("Ingress revoked.")
        self._common_exit_hook()

    def _on_check_config(self, event: ActionEvent) -> None:
        """Runs `amtool check-config` inside the workload."""
        try:
            stdout, stderr = self.alertmanager_workload.check_config()
        except WorkloadManagerError as e:
            return event.fail(str(e))

        if not stdout and stderr:
            return event.fail(stderr)

        event.set_results({"result": stdout, "error-message": stderr, "valid": not stderr})
        return None

    def _on_show_config_action(self, event: ActionEvent):
        """Hook for the show-config action."""
        event.log(f"Fetching {self._config_path}")
        if not self.alertmanager_workload.is_ready:
            event.fail("Container not ready")

        filepaths = self._render_manifest().manifest.keys()

        try:
            results = [
                {
                    "path": filepath,
                    "content": str(self.container.pull(filepath).read()),
                }
                for filepath in filepaths
                if self.container.exists(filepath)
            ]
            content = self.container.pull(self._config_path)
            # juju requires keys to be lowercase alphanumeric (can't use self._config_path)
            event.set_results(
                {
                    "path": self._config_path,
                    "content": str(content.read()),
                    # This already includes the above, but keeping both for backwards compat.
                    "configs": str(results),
                }
            )
        except (ProtocolError, PathError) as e:
            event.fail(str(e))

    @property
    def api_port(self) -> int:
        """Get the API port number to use for alertmanager (default: 9093)."""
        return self._ports.api

    @property
    def peer_relation(self) -> Optional["Relation"]:
        """Helper function for obtaining the peer relation object.

        Returns: peer relation object
        (NOTE: would return None if called too early, e.g. during install).
        """
        return self.model.get_relation(self._relations.peer)

    def _get_remote_config(self) -> Optional[Tuple[Optional[dict], Optional[str]]]:
        remote_config, remote_templates = self.remote_configuration.config()
        if remote_config:
            templates = "\n".join(remote_templates) if remote_templates else None
            return remote_config, templates
        return None

    def _get_local_config(self) -> Optional[Tuple[Optional[dict], Optional[str]]]:
        config = self.config["config_file"]
        if config:
            local_config = yaml.safe_load(cast(str, config))

            # If `juju config` is executed like this `config_file=am.yaml` instead of
            # `config_file=@am.yaml` local_config will be the string `am.yaml` instead
            # of its content (dict).
            if not isinstance(local_config, dict):
                msg = f"Unable to set config from file. Use juju config {self.unit.name} config_file=@FILENAME"
                logger.error(msg)
                raise ConfigUpdateFailure(msg)

            local_templates = cast(str, self.config["templates_file"]) or None
            return local_config, local_templates
        return None

    def _get_raw_config_and_templates(
        self,
    ) -> Tuple[Optional[dict], Optional[str]]:
        # block if multiple config sources configured
        if self._get_remote_config() and self._get_local_config():
            logger.error("unable to use config from config_file and relation at the same time")
            raise ConfigUpdateFailure("Multiple configs detected")
        # if no config provided, use default config with a placeholder receiver
        if compound_config := self._get_remote_config():
            config, templates = compound_config
        elif compound_config := self._get_local_config():
            config, templates = compound_config
        else:
            config = None
            templates = None

        return config, templates

    def _render_manifest(self) -> ConfigFileSystemState:
        raw_config, raw_templates = self._get_raw_config_and_templates()

        # Note: A free function (with many args) would have the same functionality.
        config_suite = (
            ConfigBuilder(api_port=self.api_port)
            .set_config(raw_config)
            .set_tls_server_config(
                cert_file_path=self._server_cert_path, key_file_path=self._key_path
            )
            .set_templates(raw_templates, self._templates_path)
            .build()
        )
        tls_config = self._tls_config

        return ConfigFileSystemState(
            {
                self._config_path: config_suite.alertmanager,
                self._web_config_path: config_suite.web,
                self._templates_path: config_suite.templates,
                self._amtool_config_path: config_suite.amtool,
                self._server_cert_path: tls_config.server_cert if tls_config else None,
                self._key_path: tls_config.private_key if tls_config else None,
                self._ca_cert_path: tls_config.ca_cert if tls_config else None,
            }
        )

    def _common_exit_hook(self, update_ca_certs: bool = False) -> None:
        """Event processing hook that is common to all events to ensure idempotency."""
        if not self.resources_patch.is_ready():
            if isinstance(self.unit.status, ActiveStatus) or self.unit.status.message == "":
                self.unit.status = WaitingStatus("Waiting for resource limit patch to apply")
            return

        if not self.container.can_connect():
            self.unit.status = MaintenanceStatus("Waiting for pod startup to complete")
            return

        if update_ca_certs:
            self._update_ca_certs()

        # Make sure the external url is valid
        if external_url := self._external_url:
            parsed = urlparse(external_url)
            if not (parsed.scheme in ["http", "https"] and parsed.hostname):
                # This shouldn't happen
                logger.error(
                    "Invalid external url: '%s'; must include scheme and hostname.",
                    external_url,
                )
                self.unit.status = BlockedStatus(
                    f"Invalid external url: '{external_url}'; must include scheme and hostname."
                )
                return

        # TODO Conditionally update with the external URL if it's a CMR, or rely on "recv-ca-cert"
        #  on the prometheus side.
        #  - https://github.com/canonical/operator/issues/970
        #  - https://github.com/canonical/prometheus-k8s-operator/issues/530,
        self.alertmanager_provider.update(external_url=self._internal_url)

        self.grafana_source_provider.update_source(self._external_url)

        self.ingress.provide_ingress_requirements(scheme=self._scheme, port=self.api_port)
        self._scraping.update_scrape_job_spec(self.self_scraping_job)

        if self.peer_relation:
            # Could have simply used `socket.getfqdn()` here and add the path when reading this
            # relation data, but this way it is more future-proof in case we change from ingress
            # per app to ingress per unit.
            self.peer_relation.data[self.unit]["private_address"] = self._internal_url

        self.karma_provider.target = self._external_url

        # Update config file
        try:
            self.alertmanager_workload.update_config(self._render_manifest())
        except (ConfigUpdateFailure, ConfigError) as e:
            self.unit.status = BlockedStatus(str(e))
            return

        # Update pebble layer
        self.alertmanager_workload.update_layer()

        # Reload or restart the service
        try:
            self.alertmanager_workload.reload()
        except ConfigUpdateFailure as e:
            self.unit.status = BlockedStatus(str(e))
            return

        self.catalog.update_item(item=self._catalogue_item)

        self.unit.status = ActiveStatus()

    def _on_certificate_available(self, _):
        self._common_exit_hook(update_ca_certs=True)

    def _on_pebble_ready(self, _):
        """Event handler for PebbleReadyEvent."""
        self._common_exit_hook()

    def _on_config_changed(self, _):
        """Event handler for ConfigChangedEvent."""
        self._common_exit_hook(update_ca_certs=True)

    def _on_start(self, _):
        """Event handler for ConfigChangedEvent."""
        self._common_exit_hook(update_ca_certs=True)

    def _on_peer_relation_joined(self, _):
        """Event handler for replica's RelationChangedEvent."""
        self._common_exit_hook()

    def _on_peer_relation_changed(self, _):
        """Event handler for replica's RelationChangedEvent.

        `relation_changed` is needed in addition to `relation_joined` because when a second unit
        joins, the first unit must be restarted and provided with the second unit's IP address.
        when the first unit sees "joined", it is not guaranteed that the second unit already has
        an IP address.
        """
        self._common_exit_hook()

    def _on_remote_configuration_changed(self, _):
        """Event handler for remote configuration's RelationChangedEvent."""
        self._common_exit_hook()

    def _on_update_status(self, _):
        """Event handler for UpdateStatusEvent.

        Logs list of peers, uptime and version info.
        """
        try:
            status = self.alertmanager_workload.api.status()
            logger.info(
                "alertmanager %s is up and running (uptime: %s); cluster mode: %s, with %d peers",
                status["versionInfo"]["version"],
                status["uptime"],
                status["cluster"]["status"],
                len(status["cluster"]["peers"]),
            )
        except ConnectionError as e:
            logger.error("Failed to obtain status: %s", str(e))

        # Calling the common hook to make sure a single unit set its IP in case all events fired
        # before an IP address was ready, leaving UpdateStatue as the last resort.
        self._common_exit_hook()

    def _on_upgrade_charm(self, _):
        """Event handler for replica's UpgradeCharmEvent."""
        # After upgrade (refresh), the unit ip address is not guaranteed to remain the same, and
        # the config may need update. Calling the common hook to update.
        self._common_exit_hook()

    def _update_ca_certs(self):
        ca_cert_path = Path(self._ca_cert_path)
        if tls_config := self._tls_config:
            ca_cert_path.parent.mkdir(exist_ok=True, parents=True)
            ca_cert_path.write_text(tls_config.ca_cert)
        else:
            ca_cert_path.unlink(missing_ok=True)

        # Workload container
        self.container.exec(["update-ca-certificates", "--fresh"], timeout=30).wait()
        # Charm container
        subprocess.run(["update-ca-certificates", "--fresh"], check=True)

    def _get_peer_hostnames(self, include_this_unit=True) -> List[str]:
        """Returns a list of the hostnames of the peer units.

        An example of the return format is:
          ["alertmanager-1.alertmanager-endpoints.am.svc.cluster.local"]
        """
        addresses = []
        if include_this_unit:
            addresses.append(self._internal_url)
        if pr := self.peer_relation:
            for unit in pr.units:  # pr.units only holds peers (self.unit is not included)
                if address := pr.data[unit].get("private_address"):
                    addresses.append(address)

        # Save only the hostname part of the address
        # Sort the hostnames in case their order is not guaranteed, to reduce unnecessary updates
        hostnames = sorted([urlparse(address).hostname for address in addresses])

        return hostnames

    @property
    def _tls_config(self) -> Optional[TLSConfig]:
        certificates, key = self._cert_requirer.get_assigned_certificate(
            certificate_request=self._csr_attributes
        )
        if not (key and certificates):
            return None
        return TLSConfig(certificates.certificate.raw, certificates.ca.raw, key.raw)

    @property
    def _tls_available(self) -> bool:
        return bool(self._tls_config)

    @property
    def _internal_url(self) -> str:
        """Return the fqdn dns-based in-cluster (private) address of the alertmanager api server."""
        return f"{self._scheme}://{self._fqdn}:{self._ports.api}"

    @property
    def _service_url(self) -> str:
        """Return the FQDN DNS-based in-cluster (private) address of the service for Alertmanager.

        Since our goal is to ensure that we only send one datasource to Grafana when we have multiple units, we can't use the socket FQDN because that would include the AM unit e.g. `http://am-0.am-endpoints.otel.svc.cluster.local:9093`.
        The service URL as defined will remove the pod unit so (when ingress missing) the request goes to the K8s service at: http://am-endpoints.otel.svc.cluster.local:9093
        The service will then load balance between the units.
        This assumes that the FQDN is the interal FQDN for the socket and that the pod unit is always on the left side of the first ".". If those change, this code will need to be updated.
        """
        fqdn = self._fqdn.split(".", 1)[-1]

        return f"{self._scheme}://{fqdn}:{self._ports.api}"

    @property
    def _external_url(self) -> str:
        """Return the externally-reachable (public) address of the alertmanager api server."""
        return self.ingress.url or self._internal_url

    @property
    def _scheme(self) -> str:
        return "https" if self._tls_available else "http"


if __name__ == "__main__":
    main(AlertmanagerCharm)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 23s</sub>

### 💬 Copilot

Now let me check the tests and existing imports:

---

<sub>⏱️ 24s</sub>

### ✅ `bash`

**Find tests and all config access patterns**

$ find /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests -name "*.py" | head -20 && grep -r "self\.config\|model\.config" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/ --include="*.py" -n

<details>
<summary>25 lines</summary>

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/test_tls_web.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/conftest.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/helpers.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/remote_configuration_tester/lib/charms/alertmanager_k8s/v0/alertmanager_remote_configuration.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/remote_configuration_tester/src/charm.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/test_remote_configuration.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/test_grafana_source.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/test_persistence.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/test_upgrade_charm.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/test_templates.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/test_kubectl_delete.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/integration/test_rescale_charm.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/test_external_url.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/test_remote_configuration_requirer.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/test_remote_configuration_provider.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/conftest.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/helpers.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/test_charm.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/test_consumer.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/test_push_config_to_workload_on_startup.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py:325:            "cpu": self.model.config.get("cpu"),
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py:326:            "memory": self.model.config.get("memory"),
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py:406:        config = self.config["config_file"]
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py:418:            local_templates = cast(str, self.config["templates_file"]) or None
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 29s</sub>

### ✅ `bash`

**Check test config usage and pyproject dependencies**

$ grep -n "config" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/test_charm.py | head -40 && echo "---" && cat /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/pyproject.toml | grep -A5 "dependencies\|pydantic"

<details>
<summary>62 lines</summary>

```
23:    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
56:        self.assertIn("--config.file", command)
81:    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
84:    def test_topology_added_if_user_provided_config_without_group_by(self, *unused):
85:        new_config = yaml.dump({"not a real config": "but good enough for testing"})
86:        self.harness.update_config({"config_file": new_config})
87:        updated_config = yaml.safe_load(
88:            self.harness.charm.container.pull(self.harness.charm._config_path)
91:        self.assertEqual(updated_config["not a real config"], "but good enough for testing")
93:            sorted(updated_config["route"]["group_by"]),
97:    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
100:    def test_topology_added_if_user_provided_config_with_group_by(self, *unused):
101:        new_config = yaml.dump({"route": {"group_by": ["alertname", "juju_model"]}})
102:        self.harness.update_config({"config_file": new_config})
103:        updated_config = yaml.safe_load(
104:            self.harness.charm.container.pull(self.harness.charm._config_path)
108:            sorted(updated_config["route"]["group_by"]),
112:    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
115:    def test_topology_is_not_added_if_user_provided_config_with_ellipsis(self, *unused):
118:        Ref: https://prometheus.io/docs/alerting/latest/configuration/#route
120:        new_config = yaml.dump({"route": {"group_by": ["..."]}})
121:        self.harness.update_config({"config_file": new_config})
122:        updated_config = yaml.safe_load(
123:            self.harness.charm.container.pull(self.harness.charm._config_path)
127:            updated_config["route"]["group_by"],
131:    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
134:    def test_charm_blocks_if_user_provided_config_with_templates(self, *unused):
135:        new_config = yaml.dump({"templates": ["/what/ever/*.tmpl"]})
136:        self.harness.update_config({"config_file": new_config})
139:        new_config = yaml.dump({})
140:        self.harness.update_config({"config_file": new_config})
143:    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
146:    def test_templates_file_not_created_if_user_provides_templates_without_config(self, *unused):
148:        self.harness.update_config({"templates_file": templates})
157:    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
161:        new_config = yaml.dump({"route": {"group_by": ["alertname", "juju_model"]}})
162:        self.harness.update_config({"config_file": new_config})
164:        self.harness.update_config({"templates_file": templates})
168:        updated_config = yaml.safe_load(
169:            self.harness.charm.container.pull(self.harness.charm._config_path)
---
dependencies = [
  "ops",
  "pyyaml",
  "lightkube>=0.11",  # observability_libs
  "lightkube-models",  # observability_libs
  "jsonschema", # traefik_k8s, tls_certificates
--
  "pydantic>=2",  # traefik_k8s.v2.ingress
  "opentelemetry-exporter-otlp-proto-http>=1.21.0",  # tracing
  "tenacity",
  "cosl",
  "charmed-service-mesh-helpers>=0.2.0",
  "lightkube-extensions",
--
[project.optional-dependencies]
dev = [
  # Linting
  "ruff",
  "codespell",
  # Static
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 4s</sub>

### 💬 Copilot

Now I have a clear picture. Let me implement the config class:

---

<sub>⏱️ 1m 4s</sub>

### ✅ `create`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/config.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/config.py

```
Created file /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/config.py with 408 characters
```


---

<sub>⏱️ 1m 9s</sub>

### 💬 Copilot

Now update `charm.py`:

---

<sub>⏱️ 1m 9s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 13s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 19s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 23s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 32s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 36s</sub>

### 💬 Copilot

Now let's run the tests to verify:

---

<sub>⏱️ 1m 44s</sub>

### ✅ `bash`

**Run lint and unit tests**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf && tox -e lint,unit 2>&1 | tail -50

<details>
<summary>49 lines</summary>

```
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_valid_config_pushed_to_relation_data_bag_updates_alertmanager_config
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/test_remote_configuration_requirer.py:52: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = testing.Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_no_peers
tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/test_self_scrape_jobs.py:22: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(AlertmanagerCharm)

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
ERRORm tests/unit/test_server_scheme.py::TestServerScheme::test_alerting_relation_data_scheme[True-am-0.endpoints.cluster.local] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_server_scheme.py::TestServerScheme::test_alerting_relation_data_scheme[False-localhost] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
ERROR tests/unit/test_server_scheme.py::TestServerScheme::test_alerting_relation_data_scheme[False-am-0.endpoints.cluster.local] - scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeEr...
= 22 failed, 23 passed, 3 skipped, 4 xfailed, 32 warnings, 12 errors in 2.66s ==
unit: exit 1 (6.83 seconds) /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf> uv run --frozen --isolated --extra=dev coverage run --source=/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src,/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/lib/charms/alertmanager_k8s -m pytest /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit pid=6002
  lint: OK (0.27=setup[0.00]+cmd[0.27] seconds)
  unit: FAIL code 1 (6.86=setup[0.03]+cmd[6.83] seconds)
  evaluation failed :( (7.15 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 58s</sub>

### 💬 Copilot

The `load_config` method isn't available in the current ops version. Let me check:

---

<sub>⏱️ 2m 0s</sub>

### ✅ `bash`

**Check ops version**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf && uv run --frozen python -c "import ops; print(ops.__version__)"

```
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
2.21.1
<exited with exit code 0>
```


---

<sub>⏱️ 2m 6s</sub>

### ✅ `bash`

**Check ops dependency constraint**

$ grep "ops" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/pyproject.toml

```
"ops",
  "ops[testing]",
<exited with exit code 0>
```


---

<sub>⏱️ 2m 11s</sub>

### ✅ `bash`

**Check ops version in lockfile**

$ grep -A2 "name = \"ops\"" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/uv.lock | head -10

<details>
<summary>11 lines</summary>

```
{ name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.11.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
--
    { name = "ops", extra = ["testing"] },
    { name = "pyright" },
    { name = "pytest" },
--
    { name = "ops" },
    { name = "ops", extras = ["testing"], marker = "extra == 'dev'" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 15s</sub>

### ✅ `bash`

**Find ops package entry in lockfile**

$ grep -B2 -A5 '^name = "ops"' /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/uv.lock | head -30

<details>
<summary>8 lines</summary>

```
[[package]]
name = "ops"
version = "2.21.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "importlib-metadata", version = "8.5.0", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "importlib-metadata", version = "8.6.1", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 20s</sub>

### 💬 Copilot

I need to upgrade ops to \>= 2.23.0. Let me update the lockfile:

---

<sub>⏱️ 2m 24s</sub>

### ✅ `bash`

**Upgrade ops to >= 2.23.0**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf && uv add "ops>=2.23.0" 2>&1 | tail -20

<details>
<summary>7 lines</summary>

```
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Resolved 146 packages in 3.95s
Uninstalled 1 package in 0.64ms
Installed 1 package in 7ms
 - ops==2.21.1
 + ops==3.6.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 23s</sub>

### ✅ `bash`

**Run lint and unit tests again**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf && tox -e lint,unit 2>&1 | tail -30

<details>
<summary>27 lines</summary>

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/test_remote_configuration_requirer.py:52: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = testing.Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_no_peers
tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit/test_self_scrape_jobs.py:22: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/.cache/uv/builds-v0/.tmpujR9Vg/lib/python3.12/site-packages/ops/_private/harness.py:1109: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/1'.
    warnings.warn(

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/.cache/uv/builds-v0/.tmpujR9Vg/lib/python3.12/site-packages/ops/_private/harness.py:1109: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/2'.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_charm_blocks_if_user_provided_config_with_templates - AssertionError: ActiveStatus('') is not an instance of <class 'ops.model.Bl...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_templates_section_added_if_user_provided_templates - ops.pebble.PathError: not-found - stat /etc/alertmanager/templates.tmpl: no...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_with_group_by - AssertionError: Lists differ: ['juju_application', 'juju_model', 'juju_mode...
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_topology_added_if_user_provided_config_without_group_by - KeyError: 'not a real config'
FAILED tests/unit/test_charm.py::TestWithInitialHooks::test_topology_is_not_added_if_user_provided_config_with_ellipsis - AssertionError: Lists differ: ['juju_application', 'juju_model_uuid', 'juju...
FAILED tests/unit/test_push_config_to_workload_on_startup.py::TestInvalidConfig::test_charm_blocks_on_invalid_config_changed - AssertionError: ActiveStatus('') is not an instance of <class 'ops.model.Bl...
FAILED tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_configs_available_from_both_relation_data_bag_and_charm_config_block_charm - AssertionError: ActiveStatus('') != BlockedStatus('Multiple configs detected')
= 7 failed, 50 passed, 3 skipped, 4 xfailed, 310 warnings in 107.47s (0:01:47) =
unit: exit 1 (111.14 seconds) /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf> uv run --frozen --isolated --extra=dev coverage run --source=/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src,/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/lib/charms/alertmanager_k8s -m pytest /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/tests/unit pid=6323
  lint: OK (0.13=setup[0.00]+cmd[0.12] seconds)
  unit: FAIL code 1 (111.14=setup[0.01]+cmd[111.14] seconds)
  evaluation failed :( (111.29 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 34s</sub>

### 💬 Copilot

Let me check if these test failures pre-existed my changes:

---

<sub>⏱️ 6m 29s</sub>

### ✅ `bash`

**Check baseline test failures before changes**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf && git stash && tox -e unit 2>&1 | tail -20

<details>
<summary>21 lines</summary>

```
Saved working directory and index state WIP on (no branch): 422fbbe baseline for experiment
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====== 57 passed, 3 skipped, 4 xfailed, 311 warnings in 106.68s (0:01:46) ======
unit: commands[1]> uv run --frozen --isolated --extra=dev coverage report
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 110 packages in 36ms
Name                                                                  Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------------------------------------
lib/charms/alertmanager_k8s/v0/alertmanager_remote_configuration.py     124     15     20      2    88%   52-54, 184, 228-229, 377, 385, 405-406, 417, 449-451, 471-472
lib/charms/alertmanager_k8s/v1/alertmanager_dispatch.py                  98      8     16      4    89%   114, 123-132, 222->exit, 233->232, 239-241, 245
src/alertmanager.py                                                     133     22     28     11    78%   41, 45, 129, 144, 152, 161, 169-170, 230, 240-241, 257, 265-266, 277-278, 283-284, 297, 324, 336-337
src/alertmanager_client.py                                              124     30     10      3    74%   55, 73-74, 84, 114, 121-122, 162-167, 193-202, 314-323, 345-354
src/charm.py                                                            270     39     50     10    83%   278, 324-329, 332, 335-339, 343-352, 358, 381-382, 414-416, 470-472, 482->499, 486-493, 506->512, 527-529, 536, 575, 593, 598-599, 635, 670
src/config.py                                                             8      8      0      0     0%   6-18
src/config_builder.py                                                    67      3     16      2    92%   73->75, 133-135
-----------------------------------------------------------------------------------------------------------------
TOTAL                                                                   824    125    140     32    82%
  unit: OK (110.82=setup[0.01]+cmd[110.56,0.26] seconds)
  congratulations :) (110.84 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 35s</sub>

### 💬 Copilot

Good - baseline with ops 3.6.0 passes all tests. Let me restore my changes:

---

<sub>⏱️ 6m 36s</sub>

### ✅ `bash`

**Restore my changes**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf && git stash pop

<details>
<summary>14 lines</summary>

```
HEAD detached from 1005cde
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   pyproject.toml
	modified:   src/charm.py
	modified:   uv.lock

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.github/copilot-instructions.md
	src/config.py

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (6cbffa53972cf880ccfd161f59fd4d8d942d0512)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 29s</sub>

### 💬 Copilot

The issue is that `self.typed_config` in `__init__` becomes stale when Harness tests call `update_config`. I need to make it a property that calls `load_config` fresh each time:

---

<sub>⏱️ 7m 29s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 34s</sub>

### 💬 Copilot

Now add a `typed_config` property. I'll add it near the other properties:

---

<sub>⏱️ 7m 34s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf/src/charm.py updated with changes.
```


---

<sub>⏱️ 9m 28s</sub>

### ✅ `bash`

**Run lint and unit tests**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf && tox -e lint,unit 2>&1 | tail -20

<details>
<summary>20 lines</summary>

```
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====== 57 passed, 3 skipped, 4 xfailed, 311 warnings in 105.10s (0:01:45) ======
unit: commands[1]> uv run --frozen --isolated --extra=dev coverage report
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 110 packages in 44ms
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
  lint: OK (0.13=setup[0.00]+cmd[0.13] seconds)
  unit: OK (109.06=setup[0.01]+cmd[108.78,0.27] seconds)
  congratulations :) (109.20 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 34s</sub>

### 💬 Copilot

All 57 tests pass. Let me show the final diff:

---

<sub>⏱️ 9m 35s</sub>

### ✅ `bash`

**Show final diff**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__config-classes__C1pf && git --no-pager diff src/ pyproject.toml

<details>
<summary>70 lines</summary>

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
index ae92826..c54b92a 100755
--- a/src/charm.py
+++ b/src/charm.py
@@ -10,7 +10,7 @@ import subprocess
 from dataclasses import dataclass
 from pathlib import Path
 from types import SimpleNamespace
-from typing import List, Optional, Tuple, cast
+from typing import List, Optional, Tuple
 from urllib.parse import urlparse
 
 import yaml
@@ -55,6 +55,7 @@ from alertmanager import (
     WorkloadManager,
     WorkloadManagerError,
 )
+from config import AlertmanagerCharmConfig
 from config_builder import ConfigBuilder, ConfigError
 
 logger = logging.getLogger(__name__)
@@ -281,6 +282,11 @@ class AlertmanagerCharm(CharmBase):
         for p in new_ports_to_open:
             self.unit.open_port(p.protocol, p.port)
 
+    @property
+    def typed_config(self) -> AlertmanagerCharmConfig:
+        """Return the charm config as a typed object."""
+        return self.load_config(AlertmanagerCharmConfig, errors="blocked")
+
     @property
     def _catalogue_item(self) -> CatalogueItem:
         api_endpoints = {"Alerts": "/api/v2/alerts"}
@@ -322,8 +328,8 @@ class AlertmanagerCharm(CharmBase):
 
     def _resource_reqs_from_config(self) -> ResourceRequirements:
         limits = {
-            "cpu": self.model.config.get("cpu"),
-            "memory": self.model.config.get("memory"),
+            "cpu": self.typed_config.cpu,
+            "memory": self.typed_config.memory,
         }
         requests = {"cpu": "0.25", "memory": "200Mi"}
         return adjust_resource_requirements(limits, requests, adhere_to_requests=True)
@@ -403,9 +409,9 @@ class AlertmanagerCharm(CharmBase):
         return None
 
     def _get_local_config(self) -> Optional[Tuple[Optional[dict], Optional[str]]]:
-        config = self.config["config_file"]
+        config = self.typed_config.config_file
         if config:
-            local_config = yaml.safe_load(cast(str, config))
+            local_config = yaml.safe_load(config)
 
             # If `juju config` is executed like this `config_file=am.yaml` instead of
             # `config_file=@am.yaml` local_config will be the string `am.yaml` instead
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

<sub>⏱️ 9m 44s</sub>

### ✅ `task_complete`

**Applied the config classes (load_config) skill to alertmanager-k8s-operator:

1. **Created `src/config.py`** — defines `AlertmanagerCharmConfig` as a Pydantic model with all 5 config options (`config_file`, `templates_file`, `web_external_url`, `cpu`, `memory`).

2. **Updated `src/charm.py`**:
   - Imported `AlertmanagerCharmConfig`
   - Removed unused `cast` import
   - Added a `typed_config` property that calls `self.load_config(AlertmanagerCharmConfig, errors="blocked")` (as a property rather than in `__init__`, to ensure the config is always fresh — required for Harness-based tests where the charm instance is reused across events)
   - Replaced `self.model.config.get("cpu"/"memory")` with `self.typed_config.cpu/memory`
   - Replaced `self.config["config_file"]` and `cast(str, self.config["templates_file"])` with `self.typed_config.config_file/templates_file`

3. **Updated `pyproject.toml`** — bumped ops dependency to `>=2.23.0` (required for `load_config`), which upgraded from 2.21.1 to 3.6.0.

All 57 unit tests pass.**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Applied the config classes (load_config) skill to alertmanager-k8s-operator:\n\n1. **Created `src/config.py`** — defines `AlertmanagerCharmConfig` as a Pydantic model with all 5 config options (`config_file`, `templates_file`, `web_external_url`, `cpu`, `memory`).\n\n2. **Updated `src/charm.py`**:\n   - Imported `AlertmanagerCharmConfig`\n   - Removed unused `cast` import\n   - Added a `typed_config` property that calls `self.load_config(AlertmanagerCharmConfig, errors=\"blocked\")` (as a property rather than in `__init__`, to ensure the config is always fresh — required for Harness-based tests where the charm instance is reused across events)\n   - Replaced `self.model.config.get(\"cpu\"/\"memory\")` with `self.typed_config.cpu/memory`\n   - Replaced `self.config[\"config_file\"]` and `cast(str, self.config[\"templates_file\"])` with `self.typed_config.config_file/templates_file`\n\n3. **Updated `pyproject.toml`** — bumped ops dependency to `>=2.23.0` (required for `load_config`), which upgraded from 2.21.1 to 3.6.0.\n\nAll 57 unit tests pass."
}
```

</details>

<details>
<summary>10 lines</summary>

```
Applied the config classes (load_config) skill to alertmanager-k8s-operator:

1. **Created `src/config.py`** — defines `AlertmanagerCharmConfig` as a Pydantic model with all 5 config options (`config_file`, `templates_file`, `web_external_url`, `cpu`, `memory`).

2. **Updated `src/charm.py`**:
   - Imported `AlertmanagerCharmConfig`
   - Removed unused `cast` import
   - Added a `typed_config` property that calls `self.load_config(AlertmanagerCharmConfig, errors="blocked")` (as a property rather than in `__init__`, to ensure the config is always fresh — required for Harness-based tests where the charm instance is reused across events)
   - Replaced `self.model.config.get("cpu"/"memory")` with `self.typed_config.cpu/memory`
   - Replaced `self.config["config_file"]` and `cast(str, self.config["templates_file"])` with `self.typed_config.config_file/templates_file`

3. **Updated `pyproject.toml`** — bumped ops dependency to `>=2.23.0` (required for `load_config`), which upgraded from 2.21.1 to 3.6.0.

All 57 unit tests pass.
```

</details>


---

<sub>⏱️ 9m 49s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 9m 53s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 9m 57s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 10m 1s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 10m 6s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 10m 10s</sub>

### ❌ Error

Execution failed: Error: Failed to get response from the AI model; retried 5 times (total retry wait time: 6.13999259778355 seconds) Last error: Unknown error

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
