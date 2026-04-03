# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `19e2463f-0946-41d4-b435-df6a2bae2b5a`  
> - **Started:** 4/3/2026, 12:41:15 PM  
> - **Duration:** 14m 57s  
> - **Exported:** 4/3/2026, 12:56:13 PM  

---

<sub>⏱️ 6s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Read pyproject.toml and tox.toml**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && cat pyproject.toml && echo "---" && cat tox.toml

<details>
<summary>262 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

[project]
name = "content-cache-k8s-operator"
version = "0.0.0"
description = "HTTP cache service useful for building CDNs.\n"
readme = "README.md"
requires-python = ">=3.10"
classifiers = [
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Programming Language :: Python :: 3.14",
]
dependencies = [
  "cosl==1.6.1",
  "ops==3.6.0",
  "tabulate==0.10.0",
]

[dependency-groups]
fmt = [
  "ruff",
]
lint = [
  "codespell",
  "mypy",
  "pep8-naming",
  "ruff",
]
unit = [
  "coverage[toml]",
  "pytest",
]
coverage-report = [
  "coverage[toml]",
  "pytest",
]
static = [
  "bandit[toml]",
]
integration = [
  "allure-pytest>=2.8.18",
  "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
  "juju",
  "pillow",
  "pytest",
  "pytest-cov",
  "pytest-operator",
  "python-keystoneclient",
  "python-swiftclient",
  "requests",
]

[tool.uv]
package = false

[tool.ruff]
target-version = "py310"
line-length = 99

# enable ruff linters:
#   A flake8-builtins
#   B flake8-bugbear
# CPY flake8-copyright
#   D pydocstyle
# E/W pycodestyle
#   F Pyflakes
#   I isort
#   N pep8-naming
# RUF Ruff-specific rules
#   S flake8-bandit
# SIM flake8-simplify
#  TC flake8-type-checking
#  UP pyupgrade
lint.select = [ "A", "B", "C", "CPY", "D", "E", "F", "I", "N", "RUF", "S", "SIM", "TC", "UP", "W" ]
lint.ignore = [
  "B904",
  "D107",
  "D203",
  "D204",
  "D205",
  "D213",
  "D215",
  "D400",
  "D404",
  "D406",
  "D407",
  "D408",
  "D409",
  "D413",
  "E501",
  "S105",
  "S603",
  "TC002",
  "TC006",
  "UP006",
  "UP007",
  "UP035",
  "UP045",
]
lint.per-file-ignores."tests/*" = [ "B011", "D100", "D101", "D102", "D103", "D104", "D212", "D415", "D417", "S" ]
lint.flake8-copyright.author = "Canonical Ltd."
lint.flake8-copyright.min-file-size = 1
lint.flake8-copyright.notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
lint.mccabe.max-complexity = 10
lint.pydocstyle.convention = "google"

[tool.codespell]
skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.coverage,htmlcov,uv.lock,grafana_dashboards"

[tool.mypy]
exclude = [ "^tests/integration/conftest\\.py$" ]
ignore_missing_imports = true
follow_imports = "silent"

[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"

[tool.coverage.run]
branch = true

[tool.coverage.report]
fail_under = 88
show_missing = true

[tool.bandit]
exclude_dirs = [ "/venv/", "tests/integration/any_charm.py" ]

[tool.bandit.assert_used]
skips = [ "*/*test.py", "*/test_*.py" ]
---
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

skipsdist = true
skip_missing_interpreters = true
envlist = [ "lint", "unit", "static", "coverage-report" ]
requires = [ "tox>=4.21" ]
no_package = true

[env_run_base]
passenv = [ "PYTHONPATH", "CHARM_BUILD_DIR", "MODEL_SETTINGS" ]
runner = "uv-venv-lock-runner"

[env_run_base.setenv]
PYTHONPATH = "{toxinidir}:{toxinidir}/lib:{[vars]src_path}"
PYTHONBREAKPOINT = "ipdb.set_trace"
PY_COLORS = "1"
TZ = "UTC"

[env.fmt]
description = "Apply coding style standards to code"
commands = [
  [
    "ruff",
    "check",
    "--fix",
    "--select",
    "I",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
  [
    "ruff",
    "format",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
]
dependency_groups = [ "fmt" ]

[env.lint]
description = "Check code against coding style standards"
commands = [
  [
    "codespell",
    "{toxinidir}",
  ],
  [
    "ruff",
    "format",
    "--check",
    "--diff",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
  [
    "ruff",
    "check",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
  [
    "mypy",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
]
dependency_groups = [ "lint" ]

[env.unit]
description = "Run unit tests"
commands = [
  [
    "coverage",
    "run",
    "--source={[vars]src_path}",
    "-m",
    "pytest",
    "--ignore={[vars]tst_path}integration",
    "-v",
    "--tb",
    "native",
    "-s",
    { replace = "posargs", extend = "true" },
  ],
  [
    "coverage",
    "report",
  ],
]
dependency_groups = [ "unit" ]

[env.coverage-report]
description = "Create test coverage report"
commands = [ [ "coverage", "report" ] ]
dependency_groups = [ "coverage-report" ]

[env.static]
description = "Run static analysis tests"
commands = [ [ "bandit", "-c", "{toxinidir}/pyproject.toml", "-r", "{[vars]src_path}", "{[vars]tst_path}" ] ]
dependency_groups = [ "static" ]

[env.integration]
description = "Run integration tests"
commands = [
  [
    "pytest",
    "-v",
    "--tb",
    "native",
    "--ignore={[vars]tst_path}unit",
    "--log-cli-level=INFO",
    "-s",
    { replace = "posargs", extend = "true" },
  ],
]
dependency_groups = [ "integration" ]

[env.lint-fix]
description = "Apply coding style standards to code"
commands = [
  [
    "ruff",
    "check",
    "--fix",
    "--fix-only",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
]
dependency_groups = [ "lint" ]

[vars]
src_path = "{toxinidir}/src/"
tst_path = "{toxinidir}/tests/"
all_path = [ "{toxinidir}/src/", "{toxinidir}/tests/" ]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 17s</sub>

### ✅ `bash`

**List Python source files**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && find src tests -name "*.py" | head -30 && echo "---" && ls src/ tests/

<details>
<summary>13 lines</summary>

```
src/charm.py
src/file_reader.py
tests/conftest.py
tests/integration/conftest.py
tests/integration/any_charm.py
tests/integration/test_core.py
tests/unit/test_charm.py
---
src/:
charm.py  file_reader.py  grafana_dashboards  loki_alert_rules	prometheus_alert_rules

tests/:
conftest.py  files  integration  unit
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 23s</sub>

### ✅ `bash`

**Read charm source**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && cat src/charm.py

<details>
<summary>403 lines</summary>

```
#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm for Content-cache on Kubernetes."""

import hashlib
import itertools
import logging
from collections import Counter
from datetime import datetime, timedelta
from urllib.parse import urlparse

import ops.pebble
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
from charms.nginx_ingress_integrator.v0.nginx_route import (
    _NginxRouteCharmEvents,
    provide_nginx_route,
    require_nginx_route,
)
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from ops.charm import ActionEvent, CharmBase, ConfigChangedEvent, UpgradeCharmEvent
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus
from tabulate import tabulate  # type: ignore[import-untyped]

from file_reader import readlines_reverse

logger = logging.getLogger(__name__)

CACHE_PATH = "/var/lib/nginx/proxy/cache"
CONTAINER_NAME = "content-cache"
EXPORTER_CONTAINER_NAME = "nginx-prometheus-exporter"
CONTAINER_PORT = 8080
REQUIRED_JUJU_CONFIGS = ["backend"]
REQUIRED_INGRESS_RELATION_FIELDS = {"service-hostname", "service-name", "service-port"}


class ContentCacheCharm(CharmBase):
    """Charm the service.

    Attrs:
        on: Ingress Charm Events
        ERROR_LOG_PATH: NGINX error log
        ACCESS_LOG_PATH: NGINX access log
        _metrics_endpoint: Provider of metrics for Prometheus charm
        _logging: Requirer of logs for Loki charm
        _grafana_dashboards: Dashboard Provider for Grafana charm
        unit: Charm's designated juju unit
        model: Charm's designated juju model
    """

    on = _NginxRouteCharmEvents()
    ERROR_LOG_PATH = "/var/log/nginx/error.log"
    ACCESS_LOG_PATH = "/var/log/nginx/access.log"

    def __init__(self, *args):
        """Init function for the charm.

        Args:
            args: Variable list of positional arguments passed to the parent constructor.
        """
        super().__init__(*args)

        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
        self.framework.observe(
            self.on.report_visits_by_ip_action, self._report_visits_by_ip_action
        )
        self.framework.observe(
            self.on.content_cache_pebble_ready, self._on_content_cache_pebble_ready
        )
        # Provide ability for Content-cache to be scraped by Prometheus using prometheus_scrape
        self._metrics_endpoint = MetricsEndpointProvider(
            self, jobs=[{"static_configs": [{"targets": ["*:9113"]}]}]
        )

        # Enable log forwarding for Loki and other charms that implement loki_push_api
        self._logging = LogProxyConsumer(
            self,
            relation_name="logging",
            log_files=[self.ACCESS_LOG_PATH, self.ERROR_LOG_PATH],
            container_name=CONTAINER_NAME,
        )

        # Provide grafana dashboards over a relation interface
        self._grafana_dashboards = GrafanaDashboardProvider(
            self, relation_name="grafana-dashboard"
        )
        ingress_config = self._make_ingress_config()
        require_nginx_route(
            charm=self,
            max_body_size=ingress_config.get("max-body-size", None),
            service_hostname=ingress_config.get("service-hostname"),
            service_name=ingress_config.get("service-name"),
            service_port=ingress_config.get("service-port"),
            tls_secret_name=ingress_config.get("tls-secret-name", None),
        )
        provide_nginx_route(
            charm=self,
            on_nginx_route_available=self._on_config_changed,
            on_nginx_route_broken=self._on_config_changed,
            nginx_route_relation_name="nginx-proxy",
        )
        self.framework.observe(self.on.nginx_route_available, self._on_config_changed)

    def _on_content_cache_pebble_ready(self, event) -> None:
        """Handle content_cache_pebble_ready event and configure workload container.

        Args:
            event: Event triggering the pebble ready hook for the content-cache container.
        """
        msg = "Configuring workload container (content-cache-pebble-ready)"
        logger.info(msg)
        self.model.unit.status = MaintenanceStatus(msg)
        self.on.config_changed.emit()

    def _on_start(self, event) -> None:
        """Handle workload container started.

        Args:
            event: start event.
        """
        logger.info("Starting workload container (start)")
        self.model.unit.status = ActiveStatus()

    def _on_config_changed(self, event) -> None:
        """Handle config_changed event and reconfigure workload container.

        Args:
            event: config-changed event.
        """
        msg = "Configuring workload container (config-changed)"
        logger.info(msg)
        self.model.unit.status = MaintenanceStatus(msg)
        self.configure_workload_container(event)

    def _report_visits_by_ip_action(self, event: ActionEvent) -> None:
        """Handle the report-visits-by-ip action.

        Args:
            event: the Juju action event fired when the action executes.
        """
        results = self._report_visits_by_ip()
        event.set_results({"ips": tabulate(results, headers=["IP", "Requests"], tablefmt="grid")})

    @staticmethod
    def _filter_lines(line: str) -> bool:
        """Filter the log lines by date.

        Args:
            line: A log line from the log file.

        Returns:
            Indicates if the line must be included or not.
        """
        line_elements = line.split()

        if len(line_elements) < 4:
            return False

        timestamp_str = line_elements[3].lstrip("[").rstrip("]")
        try:
            timestamp = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S")
        except ValueError:
            return False

        return timestamp > (datetime.now() - timedelta(minutes=20))

    def _get_ip(self, line: str) -> str:
        """Return the IP address of a log line.

        Args:
            line: The log line previously filtered.

        Returns:
            an IP address.

        Raises:
            ValueError: if the method encounters an empty line,
                filtering should happen in filter_lines anyway.
        """
        if line:
            return line.split()[0]
        raise ValueError

    def _report_visits_by_ip(self) -> list[tuple[str, int]]:
        """Report requests to nginx grouped and ordered by IP and report action result.

        Returns:
            A list of tuples composed of an IP address and the number of visits to that IP.
        """
        container = self.unit.get_container(CONTAINER_NAME)
        reversed_lines = filter(None, readlines_reverse(container.pull(self.ACCESS_LOG_PATH)))
        line_list = itertools.takewhile(self._filter_lines, reversed_lines)
        ip_list = map(self._get_ip, line_list)

        return Counter(ip_list).most_common()

    def _on_upgrade_charm(self, event: UpgradeCharmEvent) -> None:
        """Handle upgrade_charm event and reconfigure workload container.

        Args:
            event: upgrade-charm event.
        """
        msg = "Configuring workload container (upgrade-charm)"
        logger.info(msg)
        self.model.unit.status = MaintenanceStatus(msg)
        self.configure_workload_container(event)

    def configure_workload_container(self, event: ConfigChangedEvent | UpgradeCharmEvent) -> None:
        """Configure/set up workload container inside pod.

        Args:
            event: config-changed or upgrade-charm event.
        """
        missing = sorted(self._missing_charm_configs())
        if missing:
            msg = f"Required config(s) empty: {', '.join(missing)}"
            logger.warning(msg)
            self.unit.status = BlockedStatus(msg)
            return
        env_config = self._make_env_config()
        if env_config is None:
            logger.debug("Ingress hasn't been configured yet, waiting")
            event.defer()
            return
        pebble_config = self._make_pebble_config(env_config)
        nginx_config = self._make_nginx_config(env_config)
        exporter_config = self._get_nginx_prometheus_exporter_pebble_config()

        container = self.unit.get_container(CONTAINER_NAME)
        if container.can_connect():
            msg = "Updating Nginx site config"
            logger.info(msg)
            self.unit.status = MaintenanceStatus(msg)
            container.push("/etc/nginx/sites-enabled/default", nginx_config)
            container.make_dir(CACHE_PATH, make_parents=True)

            services = container.get_plan().to_dict().get("services", {})
            if services != pebble_config["services"]:
                msg = "Updating pebble layer config"
                logger.info(msg)
                self.unit.status = MaintenanceStatus(msg)
                container.add_layer(CONTAINER_NAME, pebble_config, combine=True)  # type: ignore[arg-type]
                container.add_layer(EXPORTER_CONTAINER_NAME, exporter_config, combine=True)  # type: ignore[arg-type]
                container.pebble.replan_services()
        else:
            self.unit.status = WaitingStatus("Waiting for Pebble to start")
            event.defer()
            return

        msg = "Ready"
        logger.info(msg)
        self.unit.status = ActiveStatus(msg)

    def _generate_keys_zone(self, name):
        """Generate hashed name to be used by Nginx's key zone.

        Args:
            name: Site name to be encoded.

        Returns:
            A hashed name to be used by Nginx's key zone.
        """
        hashed_value = hashlib.md5(name.encode("UTF-8"), usedforsecurity=False)
        hashed_name = hashed_value.hexdigest()[0:12]
        return f"{hashed_name}-cache"

    def _get_nginx_prometheus_exporter_pebble_config(self) -> ops.pebble.LayerDict:
        """Generate pebble config for the nginx-prometheus-exporter container.

        Returns:
            Pebble layer config for the nginx-prometheus-exporter layer.
        """
        return {
            "summary": "Nginx prometheus exporter",
            "description": "Prometheus exporter for nginx",
            "services": {
                EXPORTER_CONTAINER_NAME: {
                    "override": "replace",
                    "summary": "Nginx Prometheus Exporter",
                    "command": (
                        "nginx-prometheus-exporter"
                        f" -nginx.scrape-uri=http://localhost:{CONTAINER_PORT}/stub_status"
                    ),
                    "startup": "enabled",
                    "requires": [CONTAINER_NAME],
                },
            },
            "checks": {
                "nginx-exporter-up": {
                    "override": "replace",
                    "level": "alive",
                    "http": {"url": "http://localhost:9113/metrics"},
                },
            },
        }

    def _make_ingress_config(self) -> dict:
        """Return an assembled K8s ingress.

        Returns:
            An Ingress config dict.
        """
        config = self.model.config

        ingress = {
            "service-hostname": "mysite.local",
            "service-name": self.app.name,
            "service-port": CONTAINER_PORT,
        }

        site = config.get("site")

        relation = self.model.get_relation("nginx-proxy")
        if relation:
            # in case the relation app is not available yet
            prev_site = site
            site = relation.data[relation.app].get("service-hostname", prev_site)

        if site:
            ingress["service-hostname"] = site

        client_max_body_size = config.get("client_max_body_size")
        if client_max_body_size:
            ingress["max-body-size"] = client_max_body_size

        tls_secret_name = config.get("tls_secret_name")
        if tls_secret_name:
            ingress["tls-secret-name"] = tls_secret_name

        return ingress

    def _make_env_config(self, domain="svc.cluster.local") -> dict | None:
        """Return dict to be used as as runtime environment variables.

        Args:
            domain: domain used for the content-cache

        Returns:
            Charm's environment config
        """
        config = self.model.config
        relation = self.model.get_relation("nginx-proxy")
        if relation and relation.data[relation.app] and relation.units:
            if any(
                relation.data[relation.app].get(nginx_config) is None
                for nginx_config in REQUIRED_INGRESS_RELATION_FIELDS
            ):
                return None
            site = relation.data[relation.app].get("service-hostname")
            svc_name = relation.data[relation.app].get("service-name")
            svc_port = relation.data[relation.app].get("service-port")
            backend_site_name = relation.data[relation.app].get("service-hostname")
            clients = []
            for peer in relation.units:
                unit_name = peer.name.replace("/", "-")
                service_url = f"{unit_name}.{svc_name}-endpoints.{self.model.name}.{domain}"
                clients.append(f"http://{service_url}:{svc_port}")
            # XXX: Will need to deal with multiple units at some point
            backend = clients[0]
        elif relation:
            return None
        else:
            backend = str(config["backend"])
            backend_site_name = (
                str(config["backend_site_name"]) if config.get("backend_site_name") else None
            )
            if not backend_site_name:
                backend_site_name = urlparse(backend).hostname
            site = str(config["site"]) if config.get("site") else self.app.name

        cache_all_configs = ""
        if not config["cache_all"]:
            cache_all_configs = "proxy_ignore_headers Cache-Control Expires"

        client_max_body_size = config["client_max_body_size"]

        proxy_cache_revalidate = "off"
        if config.get("proxy_cache_revalidate", False):
            proxy_cache_revalidate = "on"

        env_config = {
            "CONTAINER_PORT": CONTAINER_PORT,
            "CONTENT_CACHE_BACKEND": backend,
            "CONTENT_CACHE_SITE": site,
            # https://bugs.launchpad.net/juju/+bug/1894782
            "JUJU_POD_NAME": self.unit.name,
            "JUJU_POD_NAMESPACE": self.model.name,
            "JUJU_POD_SERVICE_ACCOUNT": self.app.name,
            # Include nginx / charm configs as environment variables
            # to pass to the pebble services and ensure it restarts
            # nginx on changes.
            "NGINX_BACKEND": backend,
            "NGINX_CACHE_ALL": cache_all_configs,
            "NGINX_BACKEND_SITE_NAME": backend_site_name,
            "NGINX_CACHE_INACTIVE_TIME": config.get("cache_inactive_time", "10m"),
            "NGINX_CACHE_MAX_SIZE": config.get("cache_max_size", "10G"),
            "NGINX_CACHE_PATH": CACHE_PATH,
            "NGINX_CACHE_REVALIDATE": proxy_cache_revalidate,
            "NGINX_CACHE_USE_STALE": config["cache_use_stale"],
            "NGINX_CACHE_VALID": config["cache_valid"],
            "NGINX_CLIENT_MAX_BODY_SIZE": client_max_body_size,
            "NGINX_KEYS_ZONE": self._generate_keys_zone(site),
            "NGINX_SITE_NAME": site,
        }

        return env_config

    def _make_pebble_config(self, env_config) -> dict:
        """Generate our pebble config layer.

        Args:
            env_config: Charm's environment config

        Returns:
            content-cache container pebble layer config
        """
        pebble_config = {
            "summary": "content-cache layer",
            "description": "Pebble config layer for content-cache",
            "services": {
                CONTAINER_NAME: {
                    "override": "replace",
                    "summary": "content-cache",
                    "command": "/srv/content-cache/entrypoint.sh",
                    "startup": "enabled",
                    "environment": env_config,
                },
            },
            "checks": {
                CONTAINER_NAME: {
                    "override": "replace",
                    "exec": {"command": "ps -A | grep nginx"},
                    "threshold": 1,
                }
            },
        }
        return pebble_config

    def _make_nginx_config(self, env_config: dict) -> str:
        """Grab the NGINX template and fill it with our env config.

        Args:
            env_config: Charm's environment config

        Returns:
            A fully configured NGINX conf file
        """
        with open("content-cache_rock/nginx_cfg.tmpl", encoding="utf-8") as file:
            content = file.read()

        nginx_config = content.format(**env_config)
        return nginx_config

    def _missing_charm_configs(self) -> list[str]:
        """Check and return list of required but missing configs.

        Returns:
            Missing settings in the required juju configs.
        """
        relation = self.model.get_relation("nginx-proxy")
        if relation:
            return []
        config = self.model.config
        missing = [
            setting
            for setting in REQUIRED_JUJU_CONFIGS
            if setting not in config or not config[setting]
        ]

        return sorted(missing)


if __name__ == "__main__":  # pragma: no cover
    main(ContentCacheCharm, use_juju_for_storage=True)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 24s</sub>

### ✅ `bash`

**Check available ops versions**

$ pip show ops 2>/dev/null | grep -E "^(Name|Version)" && pip index versions ops 2>/dev/null | head -5

<details>
<summary>7 lines</summary>

```
Name: ops
Version: 3.7.0
ops (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 2.20.0, 2.19.4, 2.19.0, 2.18.1, 2.18.0, 2.17.1, 2.17.0, 2.16.1, 2.16.0, 2.15.0, 2.14.1, 2.14.0, 2.13.0, 2.12.0, 2.11.0, 2.10.0, 2.9.0, 2.8.0, 2.7.0, 2.6.0, 2.5.1, 2.5.0, 2.4.1, 2.4.0, 2.3.0, 2.2.0, 2.1.1, 2.1.0, 2.0.0, 1.5.5, 1.5.4, 1.5.3, 1.5.2, 1.5.1, 1.5.0, 1.4.0, 1.3.0, 1.2.0, 1.1.0, 1.0.1, 1.0.0, 0.10.0, 0.9.0, 0.8.0, 0.7.0, 0.6.1, 0.6.0, 0.4.7, 0.4.6, 0.4.5, 0.4.4, 0.4.3, 0.4.2, 0.2.1, 0.2.0, 0.1.0
  INSTALLED: 3.7.0
  LATEST:    3.7.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 30s</sub>

### 💬 Copilot

Now let me check the ops 3.7.0 release notes and look at the test files:

---

<sub>⏱️ 30s</sub>

### ✅ `bash`

**Read unit test file**

$ cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/tests/unit/test_charm.py

<details>
<summary>19 lines</summary>

```
Output too large to read at once (23.7 KB). Saved to: /tmp/copilot-tool-output-1775173306134-mi8ss3.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
import copy
import io
from datetime import datetime, timedelta
from unittest import mock

import pytest
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from ops.testing import Harness

from charm import CONTAINER_PORT, ContentCacheCharm

BASE_CONFIG = {
    "site": "mysite.local",
    "backend": "http://mybackend.local:80",
    "cache_max_size": "10G",
    "cache_use_stale": "error timeout updating htt
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 31s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.7.0**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/releases/tag/3.7.0"
}
```

</details>

<details>
<summary>33 lines</summary>

```
Contents of https://github.com/canonical/operator/releases/tag/3.7.0:
This release brings usability improvement in state transition testing: charmcraft extensions are now expanded, which means easier testing of [12-factor charms](https://canonical-12-factor-app-support.readthedocs-hosted.com/latest/explanation/); breakpoint is supported; .get\_relation can be called with a relation object; a single argument to Context can be used for metadata, actions and config declarations. Additionally, there are fixes for the run-time: secret expiration time zone, typing: StorageMeta.properties and state transition testing: mypy support, cleaner ownership for state data and a warning when unit test potentially relies on container data.

## What's Changed

### Features

*   Enable interactive debugging via `breakpoint` in testing in [#2363](https://github.com/canonical/operator/pull/2363)
*   ops.testing autoload support for charmcraft extensions in [#2367](https://github.com/canonical/operator/pull/2367)
*   Allow testing.State.get\_relation to accept relation objects in [#2359](https://github.com/canonical/operator/pull/2359)
*   Support charmcraft.yaml format as meta for testing.Context in [#2296](https://github.com/canonical/operator/pull/2296)

### Fixes

*   Correct type annotation for StorageMeta.properties in [#2348](https://github.com/canonical/operator/pull/2348)
*   Move the testing.Container compatibility import so that mypy style checkers understand it in [#2343](https://github.com/canonical/operator/pull/2343)
*   Hold only copies of user provided meta/config/actions in testing.Context in [#2349](https://github.com/canonical/operator/pull/2349)
*   Deep-copy layer objects during testing.State plan rendering in [#2380](https://github.com/canonical/operator/pull/2380)
*   Return copies from testing.State secret\_get and action\_get in [#2379](https://github.com/canonical/operator/pull/2379)
*   Use timezone-aware datetimes in expiry calculation in [#2378](https://github.com/canonical/operator/pull/2378)
*   Warn before clearing non-empty container in testing in [#2365](https://github.com/canonical/operator/pull/2365)

### Documentation

*   Replace links to juju.is by canonical.com/juju in [#2368](https://github.com/canonical/operator/pull/2368)
*   Refactor homepage to better put Ops in context in [#2370](https://github.com/canonical/operator/pull/2370)
*   Add pytest-operator migration guide from Jubilant docs in [#2381](https://github.com/canonical/operator/pull/2381)
*   Add a tip about AI help in the Jubilant migration guide in [#2382](https://github.com/canonical/operator/pull/2382)
*   Mention jhack scenario snapshot in [#2351](https://github.com/canonical/operator/pull/2351)
*   Update integration testing how-to guide in [#2390](https://github.com/canonical/operator/pull/2390)
*   Explain K8s charms briefly at the start of the tutorial in [#2392](https://github.com/canonical/operator/pull/2392)
*   Juju secrets identifier is now an opaque string in [#2387](https://github.com/canonical/operator/pull/2387)

### Tests

*   Extend the type checking of the ops-scenario tests in [#2230](https://github.com/canonical/operator/pull/2230)

### CI

*   Run ruff check --fix in tox -e format in [#2369](https://github.com/canonical/operator/pull/2369)
*   Check example charms with mypy in CI in [#2360](https://github.com/canonical/operator/pull/2360)
*   Update the list of published charms in the compatibility tests in [#2384](https://github.com/canonical/operator/pull/2384)
*   Adjust minimum Python version in broad charm compatibility tests in [#2317](https://github.com/canonical/operator/pull/2317)

**Full Changelog**: [3.6.0...3.7.0](https://github.com/canonical/operator/compare/3.6.0...3.7.0)
```

</details>


---

<sub>⏱️ 36s</sub>

### ✅ `bash`

**View unit test head**

$ head -100 /tmp/copilot-tool-output-1775173306134-mi8ss3.txt

<details>
<summary>92 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
import copy
import io
from datetime import datetime, timedelta
from unittest import mock

import pytest
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from ops.testing import Harness

from charm import CONTAINER_PORT, ContentCacheCharm

BASE_CONFIG = {
    "site": "mysite.local",
    "backend": "http://mybackend.local:80",
    "cache_max_size": "10G",
    "cache_use_stale": "error timeout updating http_500 http_502 http_503 http_504",
    "cache_valid": "200 1h",
}
CACHE_PATH = "/var/lib/nginx/proxy/cache"
CONTAINER_NAME = "content-cache"
JUJU_ENV_CONFIG = {
    "JUJU_POD_NAME": "content-cache-k8s/0",
    "JUJU_POD_NAMESPACE": None,
    "JUJU_POD_SERVICE_ACCOUNT": "content-cache-k8s",
    "NGINX_BACKEND_SITE_NAME": "mybackend.local",
    "NGINX_CACHE_ALL": False,
    "NGINX_CACHE_INACTIVE_TIME": "10m",
    "NGINX_CACHE_MAX_SIZE": "10G",
    "NGINX_CACHE_PATH": "/var/lib/nginx/proxy/cache",
    "NGINX_CACHE_REVALIDATE": "off",
    "NGINX_CACHE_USE_STALE": "error timeout updating http_500 http_502 http_503 http_504",
    "NGINX_CACHE_VALID": "200 1h",
    "NGINX_CLIENT_MAX_BODY_SIZE": "1m",
}
INGRESS_CONFIG = {
    "max-body-size": "1m",
    "service-hostname": "mysite.local",
    "service-name": "content-cache-k8s",
    "service-port": CONTAINER_PORT,
}
PEBBLE_CONFIG = {
    "summary": "content-cache layer",
    "description": "Pebble config layer for content-cache",
    "services": {
        CONTAINER_NAME: {
            "override": "replace",
            "summary": "content-cache",
            "command": "/srv/content-cache/entrypoint.sh",
            "startup": "enabled",
            "environment": "",
        },
    },
    "checks": {
        CONTAINER_NAME: {
            "override": "replace",
            "exec": {"command": "ps -A | grep nginx"},
            "threshold": 1,
        }
    },
}

DATE_NOW = datetime.now().strftime("%d/%b/%Y:%H:%M:%S")
DATE_20 = (datetime.now() - timedelta(minutes=20, seconds=5)).strftime("%d/%b/%Y:%H:%M:%S")
DATE_19 = (datetime.now() - timedelta(minutes=19, seconds=55)).strftime("%d/%b/%Y:%H:%M:%S")


class TestCharm:
    """Unit test battery for the content-cache charm.

    Attrs:
        config: Base configuration for content-cache charm.
        harness: Test harness.
    """

    @pytest.fixture(autouse=True)
    def init_tests(self):
        self.config = copy.deepcopy(BASE_CONFIG)
        self.harness = Harness(ContentCacheCharm)
        self.harness.begin()
        yield
        self.harness.cleanup()

    @mock.patch("charm.ContentCacheCharm.configure_workload_container")
    def test_on_content_cache_pebble_ready(self, configure_workload_container):
        """
        arrange: content_cache_pebble_ready event is received
        act: configure workload container
        assert: workload is called just once
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        harness.update_config(config)
        harness.charm.on.content_cache_pebble_ready.emit(mock.Mock())
        assert harness.charm.unit.status == MaintenanceStatus(
            "Configuring workload container (config-changed)"
        )
        configure_workload_container.assert_called_once()
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 37s</sub>

### ✅ `bash`

**Read conftest.py**

$ cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/tests/conftest.py

<details>
<summary>27 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""General configuration module for tests."""

import pytest


def pytest_addoption(parser: pytest.Parser):
    """Process parameters for integration tests.

    Args:
        parser: Pytest parser used to add arguments to console commands
    """
    # --openstack-rc points to an openstack credential file in the "rc" file style
    # Here's an example of that file
    # $ echo ~/openrc
    # export OS_REGION_NAME=RegionOne
    # export OS_PROJECT_DOMAIN_ID=default
    # export OS_AUTH_URL=http://10.0.0.1/identity
    # export OS_TENANT_NAME=demo
    # export OS_USER_DOMAIN_ID=default
    # export OS_USERNAME=demo
    # export OS_VOLUME_API_VERSION=3
    # export OS_AUTH_TYPE=password
    # export OS_PROJECT_NAME=demo
    # export OS_PASSWORD=nomoresecret
    # export OS_IDENTITY_API_VERSION=3
    parser.addoption("--charm-file", action="store")
    parser.addoption("--openstack-rc", action="store", default="")
    parser.addoption("--content-cache-image", action="store", default="")
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 51s</sub>

### ✅ `bash`

**View full unit test file**

$ cat /tmp/copilot-tool-output-1775173306134-mi8ss3.txt

<details>
<summary>19 lines</summary>

```
Output too large to read at once (23.7 KB). Saved to: /tmp/copilot-tool-output-1775173327189-m1qud1.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
import copy
import io
from datetime import datetime, timedelta
from unittest import mock

import pytest
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from ops.testing import Harness

from charm import CONTAINER_PORT, ContentCacheCharm

BASE_CONFIG = {
    "site": "mysite.local",
    "backend": "http://mybackend.local:80",
    "cache_max_size": "10G",
    "cache_use_stale": "error timeout updating htt
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 51s</sub>

### ✅ `bash`

**Read metadata and charmcraft yaml**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && cat metadata.yaml && cat charmcraft.yaml | head -60

<details>
<summary>77 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

name: content-cache-k8s
display-name: Content-cache
description: |
  A [Juju](https://juju.is/) [charm](https://juju.is/docs/olm/charmed-operators) deploying and managing
  service for caching content, built on top of [Nginx](https://www.nginx.com/), configurable to cache
  any http or https web site and useful for building content delivery networks (CDN).

  This charm simplifies initial deployment and caching operations on Kubernetes,
  such as scaling the number of cache instances and cache configuration changes.
  It allows for deployment on many different Kubernetes platforms, from [MicroK8s](https://microk8s.io) to
  [Charmed Kubernetes](https://ubuntu.com/kubernetes) and public cloud Kubernetes
  offerings.

  This service was developed to provide front-end caching for web sites run by
  Canonical's IS team, and to reduce the need for third-party CDNs by providing
  high-bandwidth access to web sites via this caching front-end. 
  
  Currently used for a number of services including [the Snap Store](https://snapcraft.io/store),
  the majority of Canonical's web properties including [ubuntu.com](https://ubuntu.com) and
  [canonical.com](https://canonical.com), and [Ubuntu Extended Security Maintenance](https://ubuntu.com/security/esm).
  For DevOps or SRE teams this charm will make operating it simple and straightforward through Juju's clean interface.
summary: |
  HTTP cache service useful for building CDNs.
docs: https://discourse.charmhub.io/t/content-cache-documentation-overview/3992
maintainers:
  - https://launchpad.net/~content-cache-charmers
assumes:
  - k8s-api
issues: https://github.com/canonical/content-cache-k8s-operator/issues
source: https://github.com/canonical/content-cache-k8s-operator

containers:
  content-cache:
    resource: content-cache-image

resources:
  content-cache-image:
    type: oci-image
    description: Docker image for content-cache to run

provides:
  metrics-endpoint:
    interface: prometheus_scrape
    optional: true
  grafana-dashboard:
    interface: grafana_dashboard
    optional: true
  nginx-proxy:
    interface: nginx-route
    limit: 1

requires:
  logging:
    interface: loki_push_api
    limit: 1
    optional: true
  nginx-route:
    interface: nginx-route
    limit: 1
    optional: true
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

type: charm
bases:
  - build-on:
      - name: "ubuntu"
        channel: "22.04"
    run-on:
      - name: "ubuntu"
        channel: "22.04"
parts:
  charm:
    source: .
    plugin: uv
    build-snaps:
    - astral-uv
  rock_data:
    plugin: dump
    source: .
    prime:
    - content-cache_rock/nginx_cfg.tmpl
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 24s</sub>

### ✅ `bash`

**Check ops version in uv.lock**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && grep -A2 "name = \"ops\"" uv.lock | head -20 && echo "---" && grep "ops-tracing\|ops-scenario\|scenario" uv.lock | head -20

<details>
<summary>17 lines</summary>

```
{ name = "ops" },
    { name = "tabulate" },
]
--
    { name = "ops", specifier = "==3.6.0" },
    { name = "tabulate", specifier = "==0.10.0" },
]
--
    { name = "ops" },
    { name = "pydantic" },
    { name = "pyyaml" },
--
name = "ops"
version = "3.6.0"
source = { registry = "https://pypi.org/simple" }
---
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 25s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/blob/main/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/blob/main/CHANGES.md"
}
```

</details>

<details>
<summary>107 lines</summary>

```
Contents of https://github.com/canonical/operator/blob/main/CHANGES.md:
## 3.7.0 - 30 March 2026

[](#370---30-march-2026)

## Features

[](#features)

*   Enable interactive debugging via `breakpoint` in testing (#2363)
*   ops.testing autoload support for charmcraft extensions (#2367)
*   Allow testing.State.get\_relation to accept relation objects (#2359)
*   Support charmcraft.yaml format as meta for testing.Context (#2296)

## Fixes

[](#fixes)

*   Correct type annotation for StorageMeta.properties (#2348)
*   Move the testing.Container compatibility import so that mypy style checkers understand it (#2343)
*   Hold only copies of user provided meta/config/actions in testing.Context (#2349)
*   Deep-copy layer objects during testing.State plan rendering (#2380)
*   Return copies from testing.State secret\_get and action\_get (#2379)
*   Use timezone-aware datetimes in expiry calculation (#2378)
*   Warn before clearing non-empty container in testing (#2365)

## Documentation

[](#documentation)

*   Replace links to juju.is by canonical.com/juju (#2368)
*   Refactor homepage to better put Ops in context (#2370)
*   Add pytest-operator migration guide from Jubilant docs (#2381)
*   Add a tip about AI help in the Jubilant migration guide (#2382)
*   Mention jhack scenario snapshot (#2351)
*   Update integration testing how-to guide (#2390)
*   Explain K8s charms briefly at the start of the tutorial (#2392)
*   Juju secrets identifier is now an opaque string (#2387)

## Tests

[](#tests)

*   Extend the type checking of the ops-scenario tests (#2230)

## CI

[](#ci)

*   Run ruff check --fix in tox -e format (#2369)
*   Check example charms with mypy in CI (#2360)
*   Update the list of published charms in the compatibility tests (#2384)
*   Adjust minimum Python version in broad charm compatibility tests (#2317)

## 3.6.0 - 26 February 2026

[](#360---26-february-2026)

## Features

[](#features-1)

*   Bump default Juju version in `ops.testing.Context` to 3.6.14 (#2316)

## Fixes

[](#fixes-1)

*   Correct the `Model.get_binding()` return type (#2329)
*   Only show executable in `ExecError.__str__`, not full command line (#2336)
*   Support Pydantic `MISSING` sentinel in `ops.Relation.save` (#2306)

## Documentation

[](#documentation-1)

*   Add how-to subcategory for managing containers (#2309)
*   Remove 2.19 version in docs, tweak ops.testing title (#2332)
*   Use "true" and "false" consistently in the reference documentation (#2330)
*   Add CLI args as another place to not put sensitive data (#2334)
*   Fix remote unit kwarg in testing example (#2342)
*   Clarify that secret labels are not names (#2337)

## Tests

[](#tests-1)

*   Set `SCENARIO_BARE_CHARM_ERRORS=true` in Ops tests that care (#2314)

## CI

[](#ci-1)

*   Fix releasing on branches with no `versions.md` doc (#2323)

## 3.5.2 - 11 February 2026

[](#352---11-february-2026)

## Fixes

[](#fixes-2)

*   Make testing.CheckInfo level arg type match pebble.CheckInfo.level (#2274)
*   Make testing consistency check aware that `credential-get` is available on k8s in newer Juju (#2307)
*   Drop unused `setuptools_scm` build dependency (#2310)

## Documentation

[](#documentation-2)

*   Update Pebble version in Juju 3.6 (#2295)
*   Refresh K8s tutorial to use Concierge and uv-based Charmcraft profile (#2285)
*   Add missing "How to" in page titles (#2289)
*   Fix and improve observability part of K8s tutorial (#2305)

## 3.5.1 - 28 January 2026

[](#351---28-january-2026)

## Fixes

[](#fixes-3)

*   Use `parse_rfc3339` for datetime parsing to support Juju 4 (#2264)
*   Correct the value of `additional_properties` in the action meta in Juju 4 (#2250)
*   Prevent `KeyError` on `auth-type` when creating `CloudCredential` object (#2268)
*   `_checks_action` should return empty list when there are no changes (#2270)

## Documentation

[](#documentation-3)

*   Provide examples in unit testing how-to, and other small improvements (#2251)
*   Update the action how-to to explain the additionalProperties default flip (#2249)
*   For state-transition tests, clarify about immutability and reusing state (#2153)
*   Fix and clarify holistic example of handling storage (#2098)
*   Remove comments from K8s tutorial and clarify about persisting data (#2253)
*   Clarify handling of postgres relation data in K8s tutorial (#2256)
*   Improve unit tests of httpbin demo charm (#2254)
*   Add version information for tools in the charming ecosystem (#2231)
*   Avoid emojis that render differently across platforms (#2273)
*   Secrets over CMR comment added (#2271)
*   Fix charm name in httpbin deploy command (#2276)
*   Updated [security@ubuntu.com](mailto:security@ubuntu.com) PGP key (#2286)

## Tests

[](#tests-2)

*   Remove unnecessary test module (#2247)

## CI

[](#ci-2)

*   Replace git reference injection with wheel artifacts in charm test workflows (#2252)
*   Explicitly provide the charmcraft repo location in CI (#2277)
*   Remove outdated custom signature generation (#2280)

## 3.5.0 - 18 December 2025

[](#350---18-decembe

<note>Content truncated. Call the fetch tool with a start_index of 5000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 40s</sub>

### ✅ `bash`

**Check cosl package**

$ pip show cosl 2>/dev/null | grep -E "^(Name|Version|Requires)" && pip index versions cosl 2>/dev/null | head -3

<details>
<summary>7 lines</summary>

```
Name: cosl
Version: 1.4.0
Requires: ops, pydantic, pyyaml, tenacity, typing-extensions
cosl (1.9.1)
Available versions: 1.9.1, 1.9.0, 1.8.0, 1.7.0, 1.6.1, 1.6.0, 1.5.0, 1.4.0, 1.3.2, 1.3.1, 1.3.0, 1.2.0, 1.1.0, 1.0.0, 0.1.1, 0.1.0, 0.0.57, 0.0.56, 0.0.55, 0.0.54, 0.0.51, 0.0.50, 0.0.49, 0.0.48, 0.0.47, 0.0.46, 0.0.45, 0.0.43, 0.0.42, 0.0.41, 0.0.40, 0.0.39, 0.0.38, 0.0.37, 0.0.36, 0.0.34, 0.0.33, 0.0.32, 0.0.31, 0.0.30, 0.0.29, 0.0.28, 0.0.27, 0.0.26, 0.0.25, 0.0.24, 0.0.23, 0.0.22, 0.0.21, 0.0.20, 0.0.19, 0.0.18, 0.0.17, 0.0.16, 0.0.15, 0.0.14, 0.0.13, 0.0.12, 0.0.11, 0.0.10, 0.0.9, 0.0.8, 0.0.7, 0.0.6, 0.0.5, 0.0.4, 0.0.3, 0.0.2, 0.0.1
  INSTALLED: 1.4.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 39s</sub>

### ✅ `bash`

**Check for ops.testing usage and tracing**

$ grep -r "ops.testing\|from ops.testing\|import ops.testing\|ops-scenario\|ops-tracing\|tracing" /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/src/ /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/tests/unit/ 2>/dev/null | head -20

```
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/tests/unit/test_charm.py:from ops.testing import Harness
<exited with exit code 0>
```


---

<sub>⏱️ 1m 47s</sub>

### ✅ `bash`

**Check ops-scenario and ops-tracing packages**

$ pip index versions ops-scenario 2>/dev/null | head -3 && pip index versions ops-tracing 2>/dev/null | head -3

<details>
<summary>7 lines</summary>

```
ops-scenario (8.7.0)
Available versions: 8.7.0, 8.6.0, 8.5.2, 8.5.1, 8.5.0, 8.4.0, 8.3.1, 8.3.0, 8.2.0, 8.1.0, 8.0.0, 7.23.2, 7.23.1, 7.23.0, 7.22.0, 7.21.1, 7.21.0, 7.20.0, 7.19.4, 7.2.0, 7.1.3, 7.1.2, 7.1.1, 7.0.5, 7.0.4, 7.0.3, 7.0.2, 7.0.1, 7.0.0, 6.1.7, 6.1.6, 6.1.5, 6.1.4, 6.1.3, 6.1.2, 6.1.1, 6.1.0, 6.0.5, 6.0.4, 6.0.3, 6.0.2, 6.0.1, 6.0, 5.8.1, 5.8, 5.7.1, 5.7, 5.6.2, 5.6.1, 5.6, 5.5, 5.4.1, 5.4, 5.3.1, 5.3, 5.2.2, 5.2.1, 5.2, 5.1.3, 5.1.2, 5.1.1, 5.1.0, 5.0, 4.0.4.1, 4.0.4, 4.0.3, 4.0.2, 4.0.1, 4.0, 3.1, 3.0.2, 3.0.1, 2.2, 2.1.3.5, 2.1.3.4, 2.1.3.3, 2.1.3.2, 2.1.3.1, 2.1.3, 2.1.2.5, 2.1.2.4, 2.1.2.3, 2.1.2.2, 2.1.2.1, 2.1.1, 2.1.0, 2.0.5, 2.0.4, 2.0.0
  INSTALLED: 8.7.0
ops-tracing (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 0.9.6, 0.9.4, 0.9.3, 0.9.2, 0.9.1, 0.9.0
  INSTALLED: 3.7.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 46s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/blob/main/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/blob/main/CHANGES.md",
  "start_index": 5000
}
```

</details>

<details>
<summary>94 lines</summary>

```
Contents of https://github.com/canonical/operator/blob/main/CHANGES.md:
r-2025)

## Features

[](#features-2)

*   Env var to control exception wrapping in tests (#2142)
*   Deprecate testing.Context.charm\_spec (#2219)

## Documentation

[](#documentation-4)

*   Fix charmcraft init command (#2210)
*   Update CI examples to use uv and tox-uv (#2213)
*   Update and clarify info about environment prep (#2217)
*   Match Charmcraft profiles in tox.ini example for integration testing (#2221)
*   Use base 24.04 for httpbin-demo charm (#2222)
*   Clarify parts of the machine charm tutorial (#2223)
*   Match Charmcraft profiles in "Write and structure charm code" (#2220)
*   Use cosl binary in K8s tutorial charm to work around error (#2232)
*   Fix URL issues by updating doc starter pack (#2238)

## Tests

[](#tests-3)

*   Don't skip tests if ops\[testing\] isn't installed (#2215)
*   Switch the integration test charms to use the uv plugin (#2218)

## CI

[](#ci-3)

*   Avoid jitter in the best practice doc PRs (#2193)
*   Ignore PERF401 (manual list comprehension) across the repo (#2201)
*   The git commands need to be run in the operator directory as well (#2197)
*   Have cycle in the sbomber manifests use the default value (#2209)
*   Add pytest.warns to note an expected warning (#2092)
*   Update release script to handle non-final versions (#2199)
*   Add ops-tracing as a dependency for the observability tests (#2239)
*   Add scheduled workflow for packing and integration testing example charms (#2233)

## 3.4.0 - 27 November 2025

[](#340---27-november-2025)

## Breaking Changes

[](#breaking-changes)

*   Fix: Change JujuContext.machine\_id from int to str (#2108)
*   Fix: Ensure that the testing context manager is exited when an exception occurs (#2117)

## Features

[](#features-3)

*   Add a low-level API for the Juju hook commands (#2019)
*   Make PebbleClient file methods also accept pathlib.PurePath (#2097)
*   Log the total number of deferred events (#2161)
*   Allow setting the Juju availability zone and principal unit in the testing Context (#2187)

## Fixes

[](#fixes-4)

*   Allow actions without params or descriptions in ops\[testing\] (#2090)
*   Ensure `ops.Pebble.pull` cleans up temporary files if it errors (#2087)
*   Make secret info description visible to the charm in ops\[testing\] (#2115)
*   Raise ActionFailed when using Context as a context manager (#2121)
*   Detect categories with an exclamation mark indicating breaking changes (#2132)
*   Normalise Secret.owner to 'app' for ops\[testing\] output state (#2127)
*   Don't cache secret metadata in Ops (#2143)
*   Secret-info-get cannot be provided with both an ID and a label (#2170)
*   Minor hookcmds fixes (#2175)

## Documentation

[](#documentation-5)

*   Update referenced examples for managing interfaces (#2068)
*   Tidy up spelling and formatting in several places (#2060)
*   Add missing assignment to state\_out in unit tests how-to (#2075)
*   Update the holistic/delta explanation with the reconciler pattern (#2029)
*   Fix broken setup/teardown links in README (#2094)
*   Update info about release docs, mark testing changelog as not maintained (#2074)
*   Switch to makefile for building the docs (#2073)
*   Document how to extract the charm instance from the testing context (#2084)
*   Add a how-to guide for migrating away from Harness (#2062)
*   Rename hook tools to hook commands (#2114)
*   Remove legacy how-to guide for Harness (#2122)
*   Update the Juju release the metrics functionality is removed from 4.0 to 3.6.11 (#2126)
*   Clarify that Context is the testing context not only the Juju context (#2123)
*   Explain the Charmhub public listing process and add a reference list of best practices (#1989)
*   Expand next steps for K8s tutorial (#2034)
*   Remove mention of the `simple` Charmcraft profile (#2138)
*   Expand landing pages with summaries of pages (#2140)
*   Update environment setup for integration tests and K8s tutorial (#2124)
*   Replace machine charm tutorial by an improved tutorial (#2119)
*   Change HACKING.md instructions for maintaining Charmcraft profiles (#2151)
*   In integration tests, use consistent approach to logging and packing (#2150)
*   In integration testing how-to, clarify that Juju model is destroyed after all tests in the model complete (#2154)
*   Remove Charmcraft channel specifier from machine charm tutorial (#2148)
*   Add AI contribution note and style guideline for type annotation of return values (#2168)
*   Add ops\[testing\] to the ops.testing docstring (#2171)
*   Add links to the Juju hook from each event class (#2176)
*   Add a short umask note (#2184)

## Tests

[](#tests-4)

*   Re-enable testing consistency checks after disabling them (#2141)
*   Expand secrets integration and state transition tests (#2130)

## Refactoring

[](#refactoring)

*   Use ops.hookcmds in \_ModelBackend (#2116)
*   Don't get the storage details from --help (#2172)
*   Drop 3.8 and 3.9 compatibility code (#2173)
*   Use json.dumps to produce the YAML in relation-set and 

<note>Content truncated. Call the fetch tool with a start_index of 10000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 57s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/ops-tracing/releases/tag/3.7.0**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/ops-tracing/releases/tag/3.7.0"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/ops-tracing/releases/tag/3.7.0 - status code 404
```


---

<sub>⏱️ 1m 57s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/ops-scenario/releases/tag/8.7.0**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/ops-scenario/releases/tag/8.7.0"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/ops-scenario/releases/tag/8.7.0 - status code 404
```


---

<sub>⏱️ 2m 3s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/ops-tracing**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/ops-tracing"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/ops-tracing - status code 404
```


---

<sub>⏱️ 2m 3s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/ops-tracing/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://pypi.org/project/ops-tracing/"
}
```

</details>

```
Contents of https://pypi.org/project/ops-tracing/:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 2m 9s</sub>

### ✅ `web_fetch`

**https://pypi.org/pypi/ops-tracing/json**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://pypi.org/pypi/ops-tracing/json",
  "max_length": 5000
}
```

</details>

```
Content type application/json cannot be simplified to markdown. Here is the raw content:
Contents of https://pypi.org/pypi/ops-tracing/json:
{"info":{"author":"The Charm Tech team at Canonical Ltd.","author_email":null,"bugtrack_url":null,"classifiers":["Development Status :: 5 - Production/Stable","Framework :: OpenTelemetry","Intended Audience :: Developers","Intended Audience :: System Administrators","Natural Language :: English","Operating System :: MacOS :: MacOS X","Operating System :: POSIX :: Linux","Programming Language :: Python","Programming Language :: Python :: 3","Programming Language :: Python :: 3 :: Only","Programming Language :: Python :: 3.10","Programming Language :: Python :: 3.11","Programming Language :: Python :: 3.12","Programming Language :: Python :: 3.13","Programming Language :: Python :: 3.14","Programming Language :: Python :: Implementation :: CPython","Programming Language :: Python :: Implementation :: PyPy","Topic :: Software Development :: Libraries"],"description":"# ops-tracing\n\n**First-party OpenTelemetry integration for the [Ops](https://pypi.org/project/ops/) library.**\nThis package adds tracing capabilities to Ops, enabling you to observe the performance of your applications.\n\n---\n\n## Overview\n\n- Seamless integration with [ops](https://pypi.org/project/ops/)\n- Built on OpenTelemetry\n- Enables tracing of your charm code\n\nPlease add `ops[tracing]` to your charm's dependencies, rather than this package directly.\n\n---\n\n## Documentation\n\nComprehensive documentation for the Ops library, including the tracing feature, is available at:\n[Ops documentation](https://documentation.ubuntu.com/ops/latest/).\n\nYou’ll find setup instructions, usage examples, and best practices for leveraging the tracing functionality.\n\n---\n\n## Community and Support\n\n- **Matrix Chat**: [Charm Tech](https://matrix.to/#/#charmhub-ops:ubuntu.com)\n- **Forum**: [Charmhub - Discuss Python operator development](https://discourse.charmhub.io/)\n- **Issue Tracker**: See [GitHub issues](https://github.com/canonical/ops/issues)\n- **Further Links**: See the [ops PyPI page](https://pypi.org/project/ops/)\n\nFeedback, contributions, and bug reports are always welcome.\nPlease follow the guidelines in the [main repository](https://github.com/canonical/ops/)\nfor the Ops library.\n\n---\n\n## License\n\nThis project is licensed under the same license as `ops`.\nRefer to the `ops` repository for full details.\n\n---\n\nHappy tracing!\n","description_content_type":"text/markdown","docs_url":null,"download_url":null,"downloads":{"last_day":-1,"last_month":-1,"last_week":-1},"dynamic":null,"home_page":null,"keywords":null,"license":null,"license_expression":"Apache-2.0","license_files":null,"maintainer":null,"maintainer_email":null,"name":"ops-tracing","package_url":"https://pypi.org/project/ops-tracing/","platform":null,"project_url":"https://pypi.org/project/ops-tracing/","project_urls":{"Changelog":"https://github.com/canonical/operator/blob/main/CHANGES.md","Documentation":"https://documentation.ubuntu.com/ops/latest/","Issues":"https://github.com/canonical/operator/issues","Repository":"https://github.com/canonical/operator"},"provides_extra":null,"release_url":"https://pypi.org/project/ops-tracing/3.7.0/","requires_dist":["opentelemetry-api~=1.0","opentelemetry-sdk~=1.30","ops==3.7.0","pydantic"],"requires_python":">=3.10","summary":"The tracing facility for the Ops library.","version":"3.7.0","yanked":false,"yanked_reason":null},"last_serial":35607421,"ownership":{"organization":null,"roles":[{"role":"Owner","user":"benhoyt"},{"role":"Owner","user":"dimaqq"},{"role":"Owner","user":"tonyandrewmeyer"}]},"releases":{"0.9.0":[{"comment_text":null,"digests":{"blake2b_256":"f3305281bb0f4ce105df8fe68ab68d5c4452e7044eb9a42d1cc555ac38667478","md5":"6305191cebb2a01ea1dec92f74589028","sha256":"59c537ec7210257976c1efb1dd5fe0b8bb45b3181829f618b5d234f47285039c"},"downloads":-1,"filename":"ops_tracing-0.9.0-py3-none-any.whl","has_sig":false,"md5_digest":"6305191cebb2a01ea1dec92f74589028","packagetype":"bdist_wheel","python_version":"py3","requires_python":">=3.8","size":29753,"upload_time":"2025-03-12T12:25:49","upload_time_iso_8601":"2025-03-12T12:25:49.470085Z","url":"https://files.pythonhosted.org/packages/f3/30/5281bb0f4ce105df8fe68ab68d5c4452e7044eb9a42d1cc555ac38667478/ops_tracing-0.9.0-py3-none-any.whl","yanked":false,"yanked_reason":null},{"comment_text":null,"digests":{"blake2b_256":"811252bbbe33c10ed9fb89cd7bd45c348df1c3c88b4e2ee2cca6642f5ba6ab55","md5":"b48ce607c43ccb229c7dcf2156eeb3f9","sha256":"b2bd18e889b0cd4e30f2b7e52c7ba8dd5146d68f9bf3907d65018792545ef5ea"},"downloads":-1,"filename":"ops_tracing-0.9.0.tar.gz","has_sig":false,"md5_digest":"b48ce607c43ccb229c7dcf2156eeb3f9","packagetype":"sdist","python_version":"source","requires_python":">=3.8","size":23189,"upload_time":"2025-03-12T12:25:51","upload_time_iso_8601":"2025-03-12T12:25:51.149624Z","url":"https://files.pythonhosted.org/packages/81/12/52bbbe33c10ed9fb89cd7bd45c348df1c3c88b4e2ee2cca6642f5ba6ab55/ops_tracing-0.9.0.tar.gz","yanked":false,"yanked_reason":null}],

<note>Content truncated. Call the fetch tool with a start_index of 5000 to get more content.</note>
```


---

<sub>⏱️ 2m 9s</sub>

### ✅ `web_fetch`

**https://pypi.org/pypi/ops-scenario/json**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://pypi.org/pypi/ops-scenario/json",
  "max_length": 3000
}
```

</details>

````
Content type application/json cannot be simplified to markdown. Here is the raw content:
Contents of https://pypi.org/pypi/ops-scenario/json:
{"info":{"author":null,"author_email":"Pietro Pasotti <pietro.pasotti@canonical.com>","bugtrack_url":null,"classifiers":["Development Status :: 5 - Production/Stable","Framework :: Pytest","Intended Audience :: Developers","Topic :: Software Development :: Quality Assurance","Topic :: Software Development :: Testing","Topic :: Utilities"],"description":"# ops-scenario, the unit testing framework for ops charms\n\n`ops-scenario` is a Python library that provides state-transition testing for\n[Ops](https://documentation.ubuntu.com/ops/latest/) charms. These tests are higher level than\ntypical unit tests, but run at similar speeds and are the recommended approach\nfor testing charms within requiring a full [Juju](https://canonical.com/juju) installation.\n\nTest are written in the arrange/act/assert pattern, arranging an object\nrepresenting the current Juju state, acting by emulating an event from Juju, and\nthen asserting on the (simulated) output Juju state.\n\n## Writing tests\n\nHere's a test that verifies that a unit is active after the `start` event, with a very minimal initial state:\n\n```python\nfrom ops import testing\n\n# 'src/charm.py' typically contains the charm class.\nfrom charm import MyCharm\n\ndef test_start():\n    ctx = testing.Context(MyCharm)\n    state_in = testing.State()\n    state_out = ctx.run(ctx.on.start(), state_in)\n    assert state_out.unit_status == testing.ActiveStatus()\n```\n\nMore comprehensive tests will include relations, containers, secrets, and other\ncomponents in the input state, and assertions against both the output state and\nthe context. The 'act' stage remains a simple single call, although additional\narguments may be required for the event, such as the relation or container that\ntriggered it. For example:\n\n```python\nimport pytest\nfrom ops import testing\n\nfrom charm import MyCharm\n\n@pytest.mark.parametrize(\n    'leader',\n    [pytest.param(True, id='leader'), pytest.param(False, id='non-leader')],\n)\ndef test_(leader: bool):\n    # Arrange:\n    ctx = testing.Context(MyCharm)\n    relation = testing.Relation('db', local_app_data={'hostname': 'example.com'})\n    peer_relation = testing.PeerRelation('peer')\n    container = testing.Container('workload', can_connect=True)\n    relation_secret = testing.Secret({'certificate': 'xxxxxxxx'})\n    user_secret = testing.Secret({'username': 'admin', 'password': 'xxxxxxxx'})\n    config = {'port': 8443, 'admin-credentials': 'secret:1234'}\n    state_in = testing.State(\n        leader=leader,\n        config=config,\n        relations={relation, peer_relation},\n        containers={container},\n        secrets={relation_secret, user_secret},\n        unit_status=testing.BlockedStatus(),\n        workload_version='1.0.1',\n    )\n\n    # Act:\n    state_out = ctx.run(ctx.on.relation_changed(relation), state_in)\n\n    # Assert:\n    assert testing.JujuLogLine(level='INFO', message='Distributing secret.') in ctx.juju_log\n    peer_relation_out = sta

<note>Content truncated. Call the fetch tool with a start_index of 3000 to get more content.</note>
````


---

<sub>⏱️ 2m 24s</sub>

### ✅ `web_fetch`

**https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md",
  "max_length": 20000
}
```

</details>

<details>
<summary>386 lines</summary>

```
Content type text/plain; charset=utf-8 cannot be simplified to markdown. Here is the raw content:
Contents of https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md:
# 3.7.0 - 30 March 2026

## Features

* Enable interactive debugging via `breakpoint` in testing (#2363)
* ops.testing autoload support for charmcraft extensions (#2367)
* Allow testing.State.get_relation to accept relation objects (#2359)
* Support charmcraft.yaml format as meta for testing.Context (#2296)

## Fixes

* Correct type annotation for StorageMeta.properties (#2348)
* Move the testing.Container compatibility import so that mypy style checkers understand it (#2343)
* Hold only copies of user provided meta/config/actions in testing.Context (#2349)
* Deep-copy layer objects during testing.State plan rendering (#2380)
* Return copies from testing.State secret_get and action_get (#2379)
* Use timezone-aware datetimes in expiry calculation (#2378)
* Warn before clearing non-empty container in testing (#2365)

## Documentation

* Replace links to juju.is by canonical.com/juju (#2368)
* Refactor homepage to better put Ops in context (#2370)
* Add pytest-operator migration guide from Jubilant docs (#2381)
* Add a tip about AI help in the Jubilant migration guide (#2382)
* Mention jhack scenario snapshot (#2351)
* Update integration testing how-to guide (#2390)
* Explain K8s charms briefly at the start of the tutorial (#2392)
* Juju secrets identifier is now an opaque string (#2387)

## Tests

* Extend the type checking of the ops-scenario tests (#2230)

## CI

* Run ruff check --fix in tox -e format (#2369)
* Check example charms with mypy in CI (#2360)
* Update the list of published charms in the compatibility tests (#2384)
* Adjust minimum Python version in broad charm compatibility tests (#2317)

# 3.6.0 - 26 February 2026

## Features

* Bump default Juju version in `ops.testing.Context` to 3.6.14 (#2316)

## Fixes

* Correct the `Model.get_binding()` return type (#2329)
* Only show executable in `ExecError.__str__`, not full command line (#2336)
* Support Pydantic `MISSING` sentinel in `ops.Relation.save` (#2306)

## Documentation

* Add how-to subcategory for managing containers (#2309)
* Remove 2.19 version in docs, tweak ops.testing title (#2332)
* Use "true" and "false" consistently in the reference documentation (#2330)
* Add CLI args as another place to not put sensitive data (#2334)
* Fix remote unit kwarg in testing example (#2342)
* Clarify that secret labels are not names (#2337)

## Tests

* Set `SCENARIO_BARE_CHARM_ERRORS=true` in Ops tests that care (#2314)

## CI

* Fix releasing on branches with no `versions.md` doc (#2323)

# 3.5.2 - 11 February 2026

## Fixes

* Make testing.CheckInfo level arg type match pebble.CheckInfo.level (#2274)
* Make testing consistency check aware that `credential-get` is available on k8s in newer Juju (#2307)
* Drop unused `setuptools_scm` build dependency (#2310)

## Documentation

* Update Pebble version in Juju 3.6 (#2295)
* Refresh K8s tutorial to use Concierge and uv-based Charmcraft profile (#2285)
* Add missing "How to" in page titles (#2289)
* Fix and improve observability part of K8s tutorial (#2305)

# 3.5.1 - 28 January 2026

## Fixes

* Use `parse_rfc3339` for datetime parsing to support Juju 4 (#2264)
* Correct the value of `additional_properties` in the action meta in Juju 4 (#2250)
* Prevent `KeyError` on `auth-type` when creating `CloudCredential` object (#2268)
* `_checks_action` should return empty list when there are no changes (#2270)

## Documentation

* Provide examples in unit testing how-to, and other small improvements (#2251)
* Update the action how-to to explain the additionalProperties default flip (#2249)
* For state-transition tests, clarify about immutability and reusing state (#2153)
* Fix and clarify holistic example of handling storage (#2098)
* Remove comments from K8s tutorial and clarify about persisting data (#2253)
* Clarify handling of postgres relation data in K8s tutorial (#2256)
* Improve unit tests of httpbin demo charm (#2254)
* Add version information for tools in the charming ecosystem (#2231)
* Avoid emojis that render differently across platforms (#2273)
* Secrets over CMR comment added (#2271)
* Fix charm name in httpbin deploy command (#2276)
* Updated security@ubuntu.com PGP key (#2286)

## Tests

* Remove unnecessary test module (#2247)

## CI

* Replace git reference injection with wheel artifacts in charm test workflows (#2252)
* Explicitly provide the charmcraft repo location in CI (#2277)
* Remove outdated custom signature generation (#2280)

# 3.5.0 - 18 December 2025

## Features

* Env var to control exception wrapping in tests (#2142)
* Deprecate testing.Context.charm_spec (#2219)

## Documentation

* Fix charmcraft init command (#2210)
* Update CI examples to use uv and tox-uv (#2213)
* Update and clarify info about environment prep (#2217)
* Match Charmcraft profiles in tox.ini example for integration testing (#2221)
* Use base 24.04 for httpbin-demo charm (#2222)
* Clarify parts of the machine charm tutorial (#2223)
* Match Charmcraft profiles in "Write and structure charm code" (#2220)
* Use cosl binary in K8s tutorial charm to work around error (#2232)
* Fix URL issues by updating doc starter pack (#2238)

## Tests

* Don't skip tests if ops[testing] isn't installed (#2215)
* Switch the integration test charms to use the uv plugin (#2218)

## CI

* Avoid jitter in the best practice doc PRs (#2193)
* Ignore PERF401 (manual list comprehension) across the repo (#2201)
* The git commands need to be run in the operator directory as well (#2197)
* Have cycle in the sbomber manifests use the default value (#2209)
* Add pytest.warns to note an expected warning (#2092)
* Update release script to handle non-final versions (#2199)
* Add ops-tracing as a dependency for the observability tests (#2239)
* Add scheduled workflow for packing and integration testing example charms (#2233)

# 3.4.0 - 27 November 2025

## Breaking Changes

* Fix: Change JujuContext.machine_id from int to str (#2108)
* Fix: Ensure that the testing context manager is exited when an exception occurs (#2117)

## Features

* Add a low-level API for the Juju hook commands (#2019)
* Make PebbleClient file methods also accept pathlib.PurePath (#2097)
* Log the total number of deferred events (#2161)
* Allow setting the Juju availability zone and principal unit in the testing Context (#2187)

## Fixes

* Allow actions without params or descriptions in ops[testing] (#2090)
* Ensure `ops.Pebble.pull` cleans up temporary files if it errors (#2087)
* Make secret info description visible to the charm in ops[testing] (#2115)
* Raise ActionFailed when using Context as a context manager (#2121)
* Detect categories with an exclamation mark indicating breaking changes (#2132)
* Normalise Secret.owner to 'app' for ops[testing] output state (#2127)
* Don't cache secret metadata in Ops (#2143)
* Secret-info-get cannot be provided with both an ID and a label (#2170)
* Minor hookcmds fixes (#2175)

## Documentation

* Update referenced examples for managing interfaces (#2068)
* Tidy up spelling and formatting in several places (#2060)
* Add missing assignment to state_out in unit tests how-to (#2075)
* Update the holistic/delta explanation with the reconciler pattern (#2029)
* Fix broken setup/teardown links in README (#2094)
* Update info about release docs, mark testing changelog as not maintained (#2074)
* Switch to makefile for building the docs (#2073)
* Document how to extract the charm instance from the testing context (#2084)
* Add a how-to guide for migrating away from Harness (#2062)
* Rename hook tools to hook commands (#2114)
* Remove legacy how-to guide for Harness (#2122)
* Update the Juju release the metrics functionality is removed from 4.0 to 3.6.11 (#2126)
* Clarify that Context is the testing context not only the Juju context (#2123)
* Explain the Charmhub public listing process and add a reference list of best practices (#1989)
* Expand next steps for K8s tutorial (#2034)
* Remove mention of the `simple` Charmcraft profile (#2138)
* Expand landing pages with summaries of pages (#2140)
* Update environment setup for integration tests and K8s tutorial (#2124)
* Replace machine charm tutorial by an improved tutorial (#2119)
* Change HACKING.md instructions for maintaining Charmcraft profiles (#2151)
* In integration tests, use consistent approach to logging and packing (#2150)
* In integration testing how-to, clarify that Juju model is destroyed after all tests in the model complete (#2154)
* Remove Charmcraft channel specifier from machine charm tutorial (#2148)
* Add AI contribution note and style guideline for type annotation of return values (#2168)
* Add ops[testing] to the ops.testing docstring (#2171)
* Add links to the Juju hook from each event class (#2176)
* Add a short umask note (#2184)

## Tests

* Re-enable testing consistency checks after disabling them (#2141)
* Expand secrets integration and state transition tests (#2130)

## Refactoring

* Use ops.hookcmds in _ModelBackend (#2116)
* Don't get the storage details from --help (#2172)
* Drop 3.8 and 3.9 compatibility code (#2173)
* Use json.dumps to produce the YAML in relation-set and state-set (#2174)
* Rely on type annotations instead of casts in hookcmds (#2179)

## CI

* Add integration and state transition tests for the secrets API (#2078)
* Temporarily disable tracing integration tests (#2102)
* Add secrets tests follow-up (#2105)
* Support monorepos in ops charm compatibility testing (#2100)
* Test both Charmcraft 3 and Charmcraft 4 profiles (#2103)
* Add automated doc checks (and related starter pack updates) (#2099)
* Clean up accidental workflow trigger (#2144)
* Test if package versions match dependency versions before publishing (#2139)
* Update spelling (#2167)
* Test against 4.0/stable (#2186)
* Store charmcraft logs if smoke tests fail (#2192)
* Use Juju channel 4/stable in Ops smoke tests (#2190)

# 3.3.0 - 29 September 2025

## Features

* Expose the Juju hook context in ops.JujuContext (#1996)

## Fixes

* In testing, separate relation data cache from mock Juju backend (#2052)

## Documentation

* Use uv for testing and packing the httpbin charm (#2011)
* Improve intro to ops.testing reference (#2023)
* In httpbin charm integration tests, add env var for charm file to deploy (#2018)
* Update get_cloud_spec doc now that credential-get works on K8s (#2031)
* Note that arbitrary_types_allowed is required when ops.Secret is used in a Pydantic class (#2038)
* Clean up Resources.fetch docstring, add ModelError exception (#2039)
* Note that the peer databag isn't usable during the install event (#2051)
* Fix testing code in actions how-to guide (#2054)

## CI

* Nicer logging output in the release script using rich (#2017)
* Clean up PYTHONPATH in tox.ini (#2058)

# 3.2.0 - 28 August 2025

## Features

* Add security event logging (#1905)
* Surface JUJU_MACHINE_ID envvar in testing env (#1961)
* Add a new log target type opentelemetry (#1937)

## Documentation

* Update links and config for switch to documentation.ubuntu.com/ops (#1940)
* Update the required Python version and note the 2.x documentation site (#1946)
* Be consistent with recommending self.config (#1947)
* Use latest styles from starter pack and remove .html extensions (#1951)
* Remove .html extensions from hardcoded links (#1955)
* Fix broken URLs in sitemap (#1956)
* Add related doc links to homepage (#1959)
* Use classes from ops instead of ops.<submodule> (#1968)
* Fix unstyled error pages (#1969)
* Add Google Analyics integration and cookie consent banner (#1971)
* Refresh docs homepage with more context about Ops (#1964)
* Update link to Charmlibs docs (#1985)
* Remove unnecessary pages from sitemap (#1979)
* Update the httpbin example charm to Jubilant (#1987)
* Update the Zero to Hero tutorial to Jubilant (#1988)
* Add model-config best practice note (#1990)
* Change some best practices to tips (#2001)
* Add integration test for invalid config in httpbin charm (#2002)
* Make a `Layer` instead of a `LayerDict` in the httpbin charm (#2003)
* Update how-to to feature Jubilant (#2000, #2004)
* Use Charmcraft-style format and lint for example charms, not Ops-style (#2008)
* Update broken link to HookVars source code (#2006)

## CI

* Fixes for the SBOM and security scan workflow, and trigger it on publishing (#1916)
* Store the charmcraft logs if packing fails (#1936)
* Install release dependencies for the TIOBE analysis (#1930)
* Add Juju 4/beta to the smoke test matrix (#1963)
* Adjust permissions block in publish workflow (#1984)
* Update actions/checkout to v5 (#1993)
* Enable doctests (#1991)
* Ignore juju/4 timeouts (#1998)
* Remove the token for SBOM and security scan workflow (#2009)
* Speed up integration test (#1978)

# 3.1.0 - 30 July 2025

## Features

* Release automation script (#1855)
* Add app_name and unit_id attributes to testing.context (#1920)
## Fixes

* If an event ends with _abort(0) tests should behave as if it ended successfully (#1887)
* If self.app is not actually set avoid a new crash location (#1897)
* Only add the remote unit for departed and broken relation events, fix ordering (#1918)
* Add the remote unit to relation.data but not relation.units (#1925)
## Documentation

* Use load_config in the httpbin example charm (#1852)
* Update HACKING.md with how to bump `ops` version in Charmcraft profiles (#1872)
* Change title of docs site (#1890)
* Use config and action classes in the Kubernetes tutorial (#1891)
* Reference example charms from K8s tutorial and fix consistency (#1898)
* Update style guide (#1720)
* Fix issues in how-to guide for stored state (#1901)
* Link out to the 12-factor tutorials from the tutorial index page (#1902)
* Replace broken link in testing explanation (#1913)
* Expand the storage how-to with content from Juju docs scheduled for removal (#1915)
* Ops tracing how to (#1853)
* Add a security explanation doc (#1904)


## Tests

* Replace Python version to 3.10 for observability charm tests (#1914)
## CI

* Use httpbin demo charm for the Charmcraft pack test (#1895)
* Move TIOBE workflow to self-hosted runners (#1912)
* Add SBOM generation and secscan workflow (#1906)
* Build and publish in one step (#1857)
* Update the name and email when updating the charm pins (#1924)
* Drop smoke test against 20.04 (#1923)

# 3.0.0 - 02 July 2025

The minimum version of Python for Ops 3.x is 3.10.

## Documentation

* Be consistent with recommending self.app and self.unit (#1856)

## CI

* Hotfix, publish job for ops-tracing (#1865)

# 2.23.0 - 30 June 2025

## Features

* Support for config schema as Python classes (#1741)
* Support for action parameter schema as Python classes (#1756)
* Ops[tracing] compatibility with jhack (#1806)
* Support for relation data schema as Python classes (#1701)
* Add CheckInfo.successes field and .has_run property (#1819)
* Provide a method to create a testing.State from a testing.Context (#1797)
* Expose trace data in testing (#1842)
* Add a helper to generate a Layer from rockcraft.yaml (#1831)

## Fixes

* Correctly load an empty Juju config options map (#1778)
* Fix type annotation of container check_infos in ops.testing (#1784)
* Restrict the version of a dependency, opentelemetry-sdk (#1794)
* Remote unit data is available in relation-departed (#1364)
* Juju allows access to the remote app databag in relation-broken, so Harness should too (#1787)
* Don't use private OpenTelemetry API (#1798)
* Do not return this unit in a mocked peer relation (#1828)
* Testing.PeerRelation properly defaults to no peers (#1832)
* In meter-status-changed JUJU_VERSION is not set (#1840)
* Only provide the units belonging to the app in Relation.units (#1837)

## Documentation

* Remove two best practices, and drop two to tips (#1758)
* Update link to Charmcraft for managing app config (#1763)
* Update link to Juju documentation for setting up deployment (#1781)
* Fix external OTLP link (#1786)
* Distribute the ops-scenario README content across the ops docs (#1773)
* Improve testing.errors.UncaughtCharmError message (#1795)
* In the "manage the charm version" how-to, give an example of using override-build (#1802)
* Small adjustments to the 'how to trace charm code' doc (#1792)
* Replace Harness example and fix links in README (#1820)
* Add httpbin charm from Charmcraft as an example charm (#1743)
* Fix on_collect mistake in sample code (#1829)
* Update code in K8s tutorial, with source in repo (part 2) (#1734)
* Update Loki section on charming zero-to-hero tutorial (#1847)
* Remove expandable boxes of text (#1844)
* Improve httpbin charm by removing defer() and adding collect_status (#1833)
* Move {posargs} to the end of pytest command lines in tox.ini (#1854)

## CI

* Install the ops[tracing] dependencies for the TIOBE action (#1761)
* Add ops-scenario and ops-tracing as explicit installs for TIOBE (#1764)
* Persist credentials for update-charm-pins workflow (#1766)
* Stop smoke testing Charmcraft 2 (#1782)
* Use Charmcraft 3.x for smoke testing 20.04 and 22.04 (#1821)
* Enable xdist for the 'unit' tox environments (#1830)

# 2.22.0 - 29 May 2025

## Features

* Add Juju topology labels (#1744)

## Fixes

* Turn on databag access validation in `__init__` (#1737)
* Allow event suffixes to appear in event names in `ops.testing` (#1754)

## Documentation

* Document how to manage metrics (#1692)
* Link to our docs from the top of our README (#1710)
* Update code in K8s tutorial, with source in repo (part 1) (#1719)
* Update links to juju.is/docs (#1725)
* Fix link in breakpoint output, remove link from Harness error message (#1726)
* Update Matrix channel name to Charm Tech (#1740)
* Rename configurations to configuration (#1746)
* Fix typos in code snippets by @MattiaSarti (#1750)

## CI

* Add `ops[tracing]` integration tests (#1686)
* Pin workflows by hash (#1721)
* Disable alertmanager compatibility tests until upstream fix (#1745)
* Remove explicit scopes and update HACKING.md (#1748)
* Pin trusted workflows by tag (#1752)
* Re-enable `alertmanager-k8s-operator` in observability charm tests (#1753)
* Fix reporting to TIOBE after `ops[tracing]` addition (#1755)

# 2.21.1 - 1 May 2025

## Reverted

* Reverting "run deferred events with fresh charm instances" (#1711)

## Documentation

* Add best practices about status (#1689)

# 2.21.0 - 30 Apr 2025

## Features

* Ops[tracing] (with a first-party charm lib) (#1612)
* Pebble identities (#1672)
* Run deferred events with fresh charm instances (#1631)

## Fixes

* Allow TLS 1.2 in ops-tracing (#1705)
* Try to fix flaky pebble exec test (#1664)

## Documentation

* Add best practice note around using tooling provided by the charmcraft profile (#1700)
* Clarify guidance about designing python modules (#1670)
* Fix a bug in the k8s tutorial doc about unit test (#1688)
* Fix broken link in readme (#1679)
* Fix links to juju docs (#1681)
* Fix tox command in hacking.md (#1661)
* Improve landing page of kubernetes charm tutorial (#1660)

## CI

* Add zizmor to static check github workflows (#1656)
* Change prerelease setting used to add latest ops and scenario (#1682)
* Don't pin release jobs to github environments (#1683)
* Don't run tests within the publish job (#1684)
* Fix smoke test (#1698)
* Post-release versioning, release process update + workflow fix (#1658)
* Rename "tox -e fmt" to "tox -e format" (#1668)

## Tests

* Fix overly specific test that fails sometimes with tracing (#1695)

# 2.20.0 - 31 Mar 2025

## Features

* Add a `remove_revision()` method to `SecretRemoveEvent` and `SecretExpiredEvent` (#1624)
* Add `Relation.remote_model` property (#1610)
* Efficient implementation of `RelationDataContent.update` (#1586)
* Expose the config metadata in `CharmMeta` (#1648)
* Add the ability to emit custom events in unit tests (#1589)
* Check that the check-infos in `testing.Container` match the plan (#1630)
* `ops.testing.State` components are less mutable (#1617)

## Fixes

* Assorted fixes for Pebble layer merging in Harness and Scenario (#1627)

## Documentation

* Add a docs link

<note>Content truncated. Call the fetch tool with a start_index of 20000 to get more content.</note>
```

</details>


---

<sub>⏱️ 2m 54s</sub>

### ✅ `bash`

**Check test file structure**

$ wc -l /tmp/copilot-tool-output-1775173306134-mi8ss3.txt && grep -n "def test_\|class Test" /tmp/copilot-tool-output-1775173306134-mi8ss3.txt

<details>
<summary>33 lines</summary>

```
651 /tmp/copilot-tool-output-1775173306134-mi8ss3.txt
69:class TestCharm:
86:    def test_on_content_cache_pebble_ready(self, configure_workload_container):
102:    def test_on_start(self):
113:    def test_on_config_changed(self, configure_workload_container):
128:    def test_on_upgrade_charm(self, configure_workload_container):
150:    def test_configure_workload_container(
201:    def test_report_visits_by_ip(self, mock_pull, test_input, expected):
214:    def test_get_ip(self, test_input, expected):
231:    def test_filter_lines(self, test_input, expected):
246:    def test_configure_workload_container_container_not_running(
270:    def test_configure_workload_container_pebble_services_already_configured(
305:    def test_configure_workload_container_has_cache_directory(
340:    def test_configure_workload_container_empty_config(
365:    def test_configure_workload_container_missing_configs(self, make_pebble_config):
378:    def test_generate_keys_zone(self):
396:    def test_make_ingress_config(self):
409:    def test_make_ingress_config_client_max_body_size(self):
424:    def test_make_ingress_config_tls_secret(self):
439:    def test_make_ingress_config_with_proxy_relation(self):
459:    def test_make_env_config(self):
479:    def test_make_env_config_with_proxy_relation(self):
504:    def test_make_pebble_config(self):
519:    def test_make_nginx_config(self):
534:    def test_make_nginx_config_backend_site_name(self):
550:    def test_make_nginx_config_client_max_body_size(self):
566:    def test_missing_charm_configs(self):
580:    def test_missing_charm_configs_missing_all(self):
594:    def test_missing_charm_configs_unset_all(self):
608:    def test_make_env_config_with_proxy_cache_revalidate(self):
622:    def test_make_env_config_without_proxy_cache_revalidate(self):
636:    def test_make_nginx_config_proxy_cache_revalidate(self):
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 9s</sub>

### ✅ `bash`

**View core test methods**

$ sed -n '150,350p' /tmp/copilot-tool-output-1775173306134-mi8ss3.txt

<details>
<summary>193 lines</summary>

```
def test_configure_workload_container(
        self,
        can_connect,
        pebble,
        get_plan,
        push,
        make_dir,
        get_service,
        add_layer,
        make_pebble_config,
        make_nginx_config,
    ):
        """
        arrange: config is changed
        act: configure workload container
        assert: unit status is Ready
        """
        config = self.config
        harness = self.harness
        harness.update_config(config)
        make_pebble_config.assert_called_once()
        make_nginx_config.assert_called_once()
        assert add_layer.call_count == 2
        assert harness.charm.unit.status, ActiveStatus("Ready")

    @mock.patch("ops.model.Container.pull")
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("", []),
            (
                f"10.10.10.11 - - [{DATE_NOW}\n"
                f"10.10.10.11 - - [{DATE_NOW}\n"
                f"10.10.10.11 - - [{DATE_NOW}\n"
                f"10.10.10.12 - - [{DATE_NOW}\n"
                f"10.10.10.12 - - [{DATE_NOW}",
                [("10.10.10.11", 3), ("10.10.10.12", 2)],
            ),
            (
                f"10.10.10.11 - - [{DATE_NOW}\n"
                f"10.10.10.11 - - [{DATE_NOW}\n"
                f"10.10.10.11 - - [{DATE_NOW}",
                [("10.10.10.11", 3)],
            ),
            (f"10.10.10.11 - - [{DATE_NOW}", [("10.10.10.11", 1)]),
            (
                f"10.10.10.12 - - [{DATE_20}\n10.10.10.10 - - [{DATE_19}\n",
                [("10.10.10.10", 1)],
            ),
        ],
    )
    def test_report_visits_by_ip(self, mock_pull, test_input, expected):
        """
        arrange: some nginx log lines are simulated
        act: process the log line
        assert: only the log lines logged less than 20 minutes ago are accepted
        """
        mock_pull.return_value = io.StringIO(test_input)
        action = self.harness.charm._report_visits_by_ip()
        assert action == expected

    @pytest.mark.parametrize(
        "test_input,expected", [(f"10.10.10.11 - - [{DATE_NOW}", "10.10.10.11")]
    )
    def test_get_ip(self, test_input, expected):
        """
        arrange: some nginx log lines are simulated
        act: process the log line
        assert: return the IP of the log line
        """
        action = self.harness.charm._get_ip(test_input)
        assert action == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (f"10.10.10.11 - - [{DATE_19}", True),
            ("", False),
            (f"10.10.10.11 - - [{DATE_20}", False),
        ],
    )
    def test_filter_lines(self, test_input, expected):
        """
        arrange: a nginx log line is simulated
        act: process the log line
        assert: only the line logged less than 20 minutes ago is accepted.
        """
        action = self.harness.charm._filter_lines(test_input)
        assert action == expected

    @mock.patch("charm.ContentCacheCharm._make_pebble_config")
    @mock.patch("ops.model.Container.add_layer")
    @mock.patch("ops.model.Container.get_service")
    @mock.patch("ops.model.Container.make_dir")
    @mock.patch("ops.model.Container.push")
    @mock.patch("ops.model.Container.pebble")
    def test_configure_workload_container_container_not_running(
        self, pebble, push, make_dir, get_service, add_layer, make_pebble_config
    ):
        """
        arrange: config is changed
        act: check if service is running and is not
        assert: services are not replanned
        """
        config = self.config
        harness = self.harness
        harness.update_config(config)
        make_pebble_config.assert_called_once()
        get_service.return_value.is_running.return_value = False
        harness.update_config(config)
        pebble.replan_services().assert_not_called()

    @mock.patch("charm.ContentCacheCharm._make_pebble_config")
    @mock.patch("ops.model.Container.add_layer")
    @mock.patch("ops.model.Container.get_service")
    @mock.patch("ops.model.Container.make_dir")
    @mock.patch("ops.model.Container.push")
    @mock.patch("ops.model.Container.get_plan")
    @mock.patch("ops.model.Container.pebble")
    @mock.patch("ops.model.Container.can_connect")
    def test_configure_workload_container_pebble_services_already_configured(
        self,
        can_connect,
        pebble,
        get_plan,
        push,
        make_dir,
        get_service,
        add_layer,
        make_pebble_config,
    ):
        """
        arrange: config is changed
        act: check if current config is different
        assert: services are replanned again
        """
        config = self.config
        harness = self.harness

        config = copy.deepcopy(BASE_CONFIG)
        make_pebble_config.return_value = {"services": "content-cache"}
        harness.update_config(config)
        make_pebble_config.assert_called_once()
        assert add_layer.call_count == 2
        assert harness.charm.unit.status == ActiveStatus("Ready")

    @mock.patch("charm.ContentCacheCharm._make_pebble_config")
    @mock.patch("ops.model.Container.add_layer")
    @mock.patch("ops.model.Container.get_service")
    @mock.patch("ops.model.Container.make_dir")
    @mock.patch("ops.model.Container.push")
    @mock.patch("ops.model.Container.get_plan")
    @mock.patch("ops.model.Container.pebble")
    @mock.patch("ops.model.Container.can_connect")
    @mock.patch("ops.model.Container.isdir")
    def test_configure_workload_container_has_cache_directory(
        self,
        can_connect,
        pebble,
        get_plan,
        push,
        make_dir,
        get_service,
        add_layer,
        make_pebble_config,
        isdir,
    ):
        """
        arrange: workload container is ready
        act: check if cache dir is created
        assert: cache directory is created
        """
        config = self.config
        harness = self.harness

        config = copy.deepcopy(BASE_CONFIG)
        harness.update_config(config)
        assert make_pebble_config.call_count == 2
        assert harness.charm.unit.status == ActiveStatus("Ready")
        container = harness.charm.unit.get_container(CONTAINER_NAME)
        assert container.isdir(CACHE_PATH)

    @mock.patch("charm.ContentCacheCharm._make_pebble_config")
    @mock.patch("ops.model.Container.add_layer")
    @mock.patch("ops.model.Container.get_service")
    @mock.patch("ops.model.Container.make_dir")
    @mock.patch("ops.model.Container.push")
    @mock.patch("ops.model.Container.get_plan")
    @mock.patch("ops.model.Container.pebble")
    @mock.patch("ops.model.Container.can_connect")
    def test_configure_workload_container_empty_config(
        self,
        can_connect,
        pebble,
        get_plan,
        push,
        make_dir,
        get_service,
        add_layer,
        make_pebble_config,
    ):
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 9s</sub>

### ✅ `bash`

**View remaining test methods**

$ sed -n '350,651p' /tmp/copilot-tool-output-1775173306134-mi8ss3.txt

<details>
<summary>283 lines</summary>

```
):
        """
        arrange: config is changed
        act: there is no change
        assert: charm replans services charm is ready as expected
        """
        config = self.config
        harness = self.harness

        config = copy.deepcopy(BASE_CONFIG)
        make_pebble_config.return_value = {"services": {}}
        harness.update_config(config)
        assert harness.charm.unit.status == ActiveStatus("Ready")

    @mock.patch("charm.ContentCacheCharm._make_pebble_config")
    def test_configure_workload_container_missing_configs(self, make_pebble_config):
        """
        arrange: config is empty
        act: raises exception
        assert: unit status is Blocked
        """
        config = self.config
        harness = self.harness
        config["backend"] = None
        harness.update_config(config)
        make_pebble_config.assert_not_called()
        assert harness.charm.unit.status == BlockedStatus("Required config(s) empty: backend")

    def test_generate_keys_zone(self):
        """
        arrange: set value for env variable NGINX_KEYS_ZONE
        act: generate keys zone
        assert: keys zone is generated as expected
        """
        harness = self.harness
        harness.disable_hooks()
        expected = "39c631ffb52d-cache"
        assert harness.charm._generate_keys_zone("mysite.local") == expected
        expected = "8b79f9e4b3e8-cache"
        assert (
            harness.charm._generate_keys_zone("my-really-really-really-long-site-name.local")
            == expected
        )
        expected = "d41d8cd98f00-cache"
        assert harness.charm._generate_keys_zone("") == expected

    def test_make_ingress_config(self):
        """
        arrange: set ingress config
        act: generate ingress config
        assert: ingress config is generated as expected
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        harness.update_config(config)
        expected = copy.deepcopy(INGRESS_CONFIG)
        assert harness.charm._make_ingress_config() == expected

    def test_make_ingress_config_client_max_body_size(self):
        """
        arrange: set ingress config overriding client_max_body_size
        act: generate ingress config
        assert: client_max_body_size is overridden as expected
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        config["client_max_body_size"] = "50m"
        harness.update_config(config)
        expected = copy.deepcopy(INGRESS_CONFIG)
        expected["max-body-size"] = "50m"
        assert harness.charm._make_ingress_config() == expected

    def test_make_ingress_config_tls_secret(self):
        """
        arrange: set tls_secret_name ingress config
        act: generate tls_secret_name ingress config
        assert: tls_secret_name is correct
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        config["tls_secret_name"] = "mysite-com-tls"  # nosec
        harness.update_config(config)
        expected = copy.deepcopy(INGRESS_CONFIG)
        expected["tls-secret-name"] = "mysite-com-tls"  # nosec
        assert harness.charm._make_ingress_config() == expected

    def test_make_ingress_config_with_proxy_relation(self):
        """
        arrange: set nginx-proxy relation
        act: verify ingress config
        assert: ingress config is generated as expected
        """
        harness = self.harness
        expected = copy.deepcopy(INGRESS_CONFIG)
        assert harness.charm._make_ingress_config() == expected
        relation_id = harness.add_relation("nginx-proxy", "hello-kubecon")
        harness.add_relation_unit(relation_id, "hello-kubecon/0")
        relations_data = {
            "service-name": "test-proxy",
            "service-hostname": "foo.internal",
            "service-port": "80",
        }
        harness.update_relation_data(relation_id, "hello-kubecon", relations_data)
        new_ingress_config = harness.charm._make_ingress_config()
        assert new_ingress_config["service-hostname"] == relations_data["service-hostname"]

    def test_make_env_config(self):
        """
        arrange: define env variables
        act: set env variables
        assert: env variables are correct
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        harness.update_config(config)
        expected = JUJU_ENV_CONFIG
        expected["CONTAINER_PORT"] = 8080
        expected["CONTENT_CACHE_BACKEND"] = "http://mybackend.local:80"
        expected["CONTENT_CACHE_SITE"] = "mysite.local"
        expected["NGINX_BACKEND"] = "http://mybackend.local:80"
        expected["NGINX_KEYS_ZONE"] = harness.charm._generate_keys_zone("mysite.local")
        expected["NGINX_SITE_NAME"] = "mysite.local"
        expected["NGINX_CACHE_ALL"] = "proxy_ignore_headers Cache-Control Expires"
        assert harness.charm._make_env_config() == expected

    def test_make_env_config_with_proxy_relation(self):
        """
        arrange: set nginx-proxy relation
        act: verify env config
        assert: env config is generated as expected
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        harness.update_config(config)
        current_env_config = harness.charm._make_env_config()
        current_site = current_env_config["CONTENT_CACHE_SITE"]
        assert current_site == "mysite.local"
        relation_id = harness.add_relation("nginx-proxy", "hello-kubecon")
        harness.add_relation_unit(relation_id, "hello-kubecon/0")
        relations_data = {
            "service-name": "test-proxy",
            "service-hostname": "foo.internal",
            "service-port": "80",
        }
        harness.update_relation_data(relation_id, "hello-kubecon", relations_data)
        new_env_config = harness.charm._make_env_config()
        new_site = new_env_config["CONTENT_CACHE_SITE"]
        assert new_site == relations_data["service-hostname"]

    def test_make_pebble_config(self):
        """
        arrange: define pebble config
        act: set pebble config
        assert: pebble config is correct
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        harness.update_config(config)
        env_config = harness.charm._make_env_config()
        expected = PEBBLE_CONFIG
        expected["services"]["content-cache"]["environment"] = harness.charm._make_env_config()
        assert harness.charm._make_pebble_config(env_config) == expected

    def test_make_nginx_config(self):
        """
        arrange: define nginx config
        act: set nginx config
        assert: ensure envConfig returned is correct
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        harness.update_config(config)
        env_config = harness.charm._make_env_config()
        with open("tests/files/nginx_config.txt") as f:
            expected = f.read()
            assert harness.charm._make_nginx_config(env_config) == expected

    def test_make_nginx_config_backend_site_name(self):
        """
        arrange: define nginx config with charm config backend_site_config
        act: set nginx config
        assert: ensure envConfig returned is correct
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        config["backend_site_name"] = "myoverridebackendsitename.local"
        harness.update_config(config)
        env_config = harness.charm._make_env_config()
        with open("tests/files/nginx_config_backend_site_name.txt") as f:
            expected = f.read()
            assert harness.charm._make_nginx_config(env_config) == expected

    def test_make_nginx_config_client_max_body_size(self):
        """
        arrange: define nginx config with charm config client_max_body_size
        act: set nginx config
        assert: ensure envConfig returned is correct
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        config["client_max_body_size"] = "50m"
        harness.update_config(config)
        env_config = harness.charm._make_env_config()
        with open("tests/files/nginx_config_client_max_body_size.txt") as f:
            expected = f.read()
            assert harness.charm._make_nginx_config(env_config) == expected

    def test_missing_charm_configs(self):
        """
        arrange: define charm config with missing field
        act: set charm config
        assert: ensure required configs present and return those missing
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        # None missing, all required configs set.
        harness.update_config(config)
        expected = []
        assert harness.charm._missing_charm_configs() == expected

    def test_missing_charm_configs_missing_all(self):
        """
        arrange: define charm config with all missing
        act: set charm config
        assert: ensure required configs present and return those missing
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        config.pop("backend")
        harness.update_config(config)
        expected = ["backend"]
        assert harness.charm._missing_charm_configs() == expected

    def test_missing_charm_configs_unset_all(self):
        """
        arrange: define charm config with all unset
        act: set charm config
        assert: ensure required configs present and return those missing
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        config["backend"] = None
        harness.update_config(config)
        expected = ["backend"]
        assert harness.charm._missing_charm_configs() == expected

    def test_make_env_config_with_proxy_cache_revalidate(self):
        """
        arrange: define configuration with proxy_cache_revalidate enabled
        act: generate environment configuration
        assert: env variable NGINX_CACHE_REVALIDATE is set correctly
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        config["proxy_cache_revalidate"] = True
        harness.update_config(config)
        env_config = harness.charm._make_env_config()
        assert env_config["NGINX_CACHE_REVALIDATE"] == "on"

    def test_make_env_config_without_proxy_cache_revalidate(self):
        """
        arrange: define configuration with proxy_cache_revalidate disabled
        act: generate environment configuration
        assert: env variable NGINX_CACHE_REVALIDATE is set to off
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        config["proxy_cache_revalidate"] = False
        harness.update_config(config)
        env_config = harness.charm._make_env_config()
        assert env_config["NGINX_CACHE_REVALIDATE"] == "off"

    def test_make_nginx_config_proxy_cache_revalidate(self):
        """
        arrange: define nginx config with proxy_cache_revalidate enabled
        act: set nginx config
        assert: ensure nginx config contains proxy_cache_revalidate on
        """
        config = self.config
        harness = self.harness
        harness.disable_hooks()
        config["proxy_cache_revalidate"] = True
        harness.update_config(config)
        env_config = harness.charm._make_env_config()
        with open("tests/files/nginx_config_proxy_cache_revalidate.txt") as f:
            expected = f.read()
            assert harness.charm._make_nginx_config(env_config) == expected
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 31s</sub>

### ✅ `bash`

**Check config.yaml and test files**

$ cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/config.yaml && ls /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/tests/files/

<details>
<summary>72 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

options:
  site:
    type: string
    description: >
      Required if no nginx-proxy relation is established. The site name, e.g. "mysite.local".
      If the backend is set and this option is empty then the site will default to the application
      name.
  backend:
    type: string
    description: >
      Required if no nginx-proxy relation is established. The backend to use for site, e.g. "http://mybackend.local:80".
    default: ""
  backend_site_name:
    type: string
    description: >
      Backend site name, e.g. mybackend.local. If none given, will
      work out from the configured 'backend' config above.
    default: ""
  cache_all:
    type: boolean
    description: >
      By default, we respect upstream cache headers (Cache-Control
      and Expires). This overrides that and enables caching even if
      upstream tells us not to.
      WARNING: It won't cache when Vary: * and Set-Cookies headers are sent in the responses.
      This option overrides the backend cache time instructions (Expires or max-age) by setting
      a cache time to 1h (which could be less than the caching instructed by the backend)
    default: False
  cache_inactive_time:
    type: string
    description: >
      The maximum age/time inactive objects are stored in cache.
    default: "10m"
  cache_max_size:
    type: string
    description: >
      The size of the Nginx storage cache.
    default: "10G"
  cache_use_stale:
    type: string
    description: >
      Determines in which cases a stale cached response can be used
      during communication with the proxied server.
    default: "error timeout updating http_500 http_502 http_503 http_504"
  cache_valid:
    type: string
    description: >
      Sets caching time for different response codes.
    default: "200 1h"
  client_max_body_size:
    type: string
    description: >
      Override max. request body size (default 1m).
    default: "1m"
  tls_secret_name:
    type: string
    description: >
      The name of the K8s secret to be associated with the ingress resource.
    default: ""
  proxy_cache_revalidate:
    type: boolean
    description: >
      Enables revalidation of expired cache items using conditional requests with the
      "If-Modified-Since" and "If-None-Match" header fields.
      If the proxied server returns 304 (Not Modified), the cached item will be updated
      without re-downloading the entire content, improving performance.
    default: False
nginx_config.txt		    nginx_config_client_max_body_size.txt
nginx_config_backend_site_name.txt  nginx_config_proxy_cache_revalidate.txt
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 0s</sub>

### ✅ `bash`

**View full charmcraft.yaml**

$ cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/charmcraft.yaml

<details>
<summary>22 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

type: charm
bases:
  - build-on:
      - name: "ubuntu"
        channel: "22.04"
    run-on:
      - name: "ubuntu"
        channel: "22.04"
parts:
  charm:
    source: .
    plugin: uv
    build-snaps:
    - astral-uv
  rock_data:
    plugin: dump
    source: .
    prime:
    - content-cache_rock/nginx_cfg.tmpl
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 0s</sub>

### ✅ `bash`

**Check git status**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && git log --oneline -5 && git status

```
c32e9d6 (grafted, HEAD, origin/main, origin/HEAD, main) fix(deps): update dependency cosl to v1.6.1 (#168)
HEAD detached at c32e9d6
nothing to commit, working tree clean
<exited with exit code 0>
```


---

<sub>⏱️ 4m 21s</sub>

### 💬 Copilot

Now I have full context. Let me set up the branch and implement the changes:

---

<sub>⏱️ 4m 21s</sub>

### ✅ `bash`

**Create upgrade branch**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && git checkout -b upgrade-ops-3.7.0

```
Switched to a new branch 'upgrade-ops-3.7.0'
<exited with exit code 0>
```


---

<sub>⏱️ 4m 21s</sub>

### ✅ `bash`

**Run existing tests to check baseline**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && python -m tox -e unit -- --tb=short -q 2>&1 | tail -20

```
bash: python: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 4m 28s</sub>

### ✅ `bash`

**Run existing tests baseline**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && tox -e unit -- --tb=short -q 2>&1 | tail -20

<details>
<summary>18 lines</summary>

```
collected 36 items

tests/unit/test_charm.py ....................................

=============================== warnings summary ===============================
tests/unit/test_charm.py: 36 warnings
  /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/tests/unit/test_charm.py:80: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(ContentCacheCharm)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 36 passed, 36 warnings in 0.69s ========================
unit: commands[1]> coverage report
Name                 Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------
src/charm.py           189     11     36      8    92%   147-148, 168-169, 188, 228-230, 244->256, 329->332, 354, 367, 378->381, 468
src/file_reader.py      17      0      4      0   100%
----------------------------------------------------------------
TOTAL                  206     11     40      8    92%
  unit: OK (1.28=setup[0.08]+cmd[1.13,0.06] seconds)
  congratulations :) (1.29 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 48s</sub>

### 💬 Copilot

Now I have a complete picture. Let me implement the changes:

---

<sub>⏱️ 7m 48s</sub>

### ✅ `sql`

**Create task plan**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create task plan",
  "query": "INSERT INTO todos (id, title, description, status) VALUES\n('bump-version', 'Bump ops version', 'Change ops==3.6.0 to ops==3.7.0 in pyproject.toml', 'pending'),\n('update-lockfile', 'Update uv.lock', 'Run uv lock to regenerate lockfile with ops 3.7.0', 'pending'),\n('migrate-tests', 'Migrate tests to ops.testing Context/State', 'Replace Harness-based tests in tests/unit/test_charm.py with the recommended Context/State pattern (ops-scenario). This is the key \"new feature\" to adopt from ops 3.7.0.', 'pending'),\n('verify', 'Verify all tests pass', 'Run tox -e unit and tox -e lint to confirm everything works', 'pending'),\n('commit', 'Create git commit', 'Commit all changes with a descriptive message', 'pending')"
}
```

</details>

```
5 row(s) inserted. Last inserted row ID: 5.
```


---

<sub>⏱️ 7m 55s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 8m 1s</sub>

### ✅ `bash`

**Update uv.lock**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && uv lock 2>&1

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
⠋ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠙ content-cache-k8s-operator==0.0.0                                                                                     ⠙ content-cache-k8s-operator==0.0.0                                                                                     ⠙ content-cache-k8s-operator==0.0.0                                                                                     ⠙ content-cache-k8s-operator==0.0.0                                                                                     ⠙ content-cache-k8s-operator==0.0.0                                                                                     ⠙ content-cache-k8s-operator==0.0.0                                                                                     ⠙ content-cache-k8s-operator==0.0.0                                                                                     ⠙ allure-pytest-collection-report==0.1.0                                                                                ⠙ cosl==1.6.1                                                                                                           ⠙ ops==3.7.0                                                                                                            ⠙ tabulate==0.10.0                                                                                                      ⠙ coverage==7.12.0                                                                                                      ⠙ coverage==7.12.0                                                                                                      ⠙ pytest==9.0.1                                                                                                         ⠙ ruff==0.14.6                                                                                                          ⠙ allure-pytest==2.15.0                                                                                                 ⠙ allure-python-commons==2.15.0                                                                                         ⠙ juju==3.6.1.3                                                                                                         ⠙ pillow==12.0.0                                                                                                        ⠙ pytest-cov==7.0.0                                                                                                     ⠙ pydantic-core==2.41.5                                                                                                 ⠹ pathspec==0.12.1                                                                                                      ⠸ pathspec==0.12.1                                                                                                      ⠸ flake8==7.3.0                                                                                                         ⠸ rich==14.2.0                                                                                                          ⠸ annotated-types==0.7.0                                                                                                ⠸ mdurl==0.1.2                                                                                                          Resolved 119 packages in 481ms
Updated ops v3.6.0 -> v3.7.0
<exited with exit code 0>
```


---

<sub>⏱️ 8m 8s</sub>

### ✅ `sql`

**Mark bump and lockfile done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark bump and lockfile done",
  "query": "UPDATE todos SET status = 'done' WHERE id IN ('bump-version', 'update-lockfile')"
}
```

</details>

```
2 row(s) updated.
```


---

<sub>⏱️ 8m 23s</sub>

### 💬 Copilot

Now let me understand the exact model.name that `testing.Context` will provide, and check the testing.Container filesystem API:

---

<sub>⏱️ 8m 24s</sub>

### ✅ `bash`

**Test the Context defaults**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && python3 -c "
from ops import testing
from charm import ContentCacheCharm

ctx = testing.Context(ContentCacheCharm)
container = testing.Container('content-cache', can_connect=True)
state_in = testing.State(containers={container})
with ctx(ctx.on.start(), state_in) as mgr:
    out = mgr.run()
    charm = mgr.charm
    print('model.name:', repr(charm.model.name))
    print('unit.name:', repr(charm.unit.name))
    print('app.name:', repr(charm.app.name))
"


```
Traceback (most recent call last):
  File "<string>", line 3, in <module>
ModuleNotFoundError: No module named 'charm'
<exited with exit code 1>
```


---

<sub>⏱️ 8m 31s</sub>

### ✅ `bash`

**Test Context defaults**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && PYTHONPATH=src python3 -c "
from ops import testing
from charm import ContentCacheCharm

ctx = testing.Context(ContentCacheCharm)
container = testing.Container('content-cache', can_connect=True)
state_in = testing.State(containers={container})
with ctx(ctx.on.start(), state_in) as mgr:
    out = mgr.run()
    charm = mgr.charm
    print('model.name:', repr(charm.model.name))
    print('unit.name:', repr(charm.unit.name))
    print('app.name:', repr(charm.app.name))
"


<details>
<summary>6 lines</summary>

```
Traceback (most recent call last):
  File "<string>", line 3, in <module>
  File "/tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/src/charm.py", line 16, in <module>
    from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
ModuleNotFoundError: No module named 'charms'
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 8m 37s</sub>

### ✅ `bash`

**List lib directory**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && ls lib/

```
charms
<exited with exit code 0>
```


---

<sub>⏱️ 8m 43s</sub>

### ✅ `bash`

**Test Context defaults with full PYTHONPATH**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && PYTHONPATH=src:lib python3 -c "
from ops import testing
from charm import ContentCacheCharm

ctx = testing.Context(ContentCacheCharm)
container = testing.Container('content-cache', can_connect=True)
state_in = testing.State(containers={container})
with ctx(ctx.on.start(), state_in) as mgr:
    out = mgr.run()
    charm = mgr.charm
    print('model.name:', repr(charm.model.name))
    print('unit.name:', repr(charm.unit.name))
    print('app.name:', repr(charm.app.name))
" 2>&1

<details>
<summary>7 lines</summary>

```
Traceback (most recent call last):
  File "<string>", line 3, in <module>
  File "/tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/src/charm.py", line 27, in <module>
    from tabulate import tabulate  # type: ignore[import-untyped]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'tabulate'
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 8m 49s</sub>

### ❌ `bash`

**Test Context with tox venv**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && .tox/unit/bin/python -c "
from ops import testing
from charm import ContentCacheCharm

ctx = testing.Context(ContentCacheCharm)
container = testing.Container('content-cache', can_connect=True)
state_in = testing.State(containers={container})
with ctx(ctx.on.start(), state_in) as mgr:
    out = mgr.run()
    charm = mgr.charm
    print('model.name:', repr(charm.model.name))
    print('unit.name:', repr(charm.unit.name))
    print('app.name:', repr(charm.app.name))
" 2>&1

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 8m 54s</sub>

### ✅ `bash`

**Find tox venv python**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && find .tox -name "python3" 2>/dev/null | head -3 && ls .tox/

```
.tox/unit/bin/python3
CACHEDIR.TAG  unit
<exited with exit code 0>
```


---

<sub>⏱️ 9m 1s</sub>

### ✅ `bash`

**Try running a quick check**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && tox -e unit -- -c "
import sys; sys.exit(0)
" 2>&1 | head -5

<details>
<summary>6 lines</summary>

```
unit: uv-sync> uv sync --locked --python-preference system --no-default-groups --group unit -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
unit: commands[0]> coverage run --source=/tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/src/ -m pytest --ignore=/tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/tests/integration -v --tb native -s -c '
import sys; sys.exit(0)
'
============================= test session starts ==============================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 0s</sub>

### ❌ `bash`

**Find available python**

$ which python3 && ls /usr/bin/python3*

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 9m 11s</sub>

### ✅ `bash`

**Test Context with uv run**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && uv run --group unit python3 -c "
from ops import testing
from charm import ContentCacheCharm

ctx = testing.Context(ContentCacheCharm)
container = testing.Container('content-cache', can_connect=True)
state_in = testing.State(containers={container})
with ctx(ctx.on.start(), state_in) as mgr:
    out = mgr.run()
    charm = mgr.charm
    print('model.name:', repr(charm.model.name))
    print('unit.name:', repr(charm.unit.name))
    print('app.name:', repr(charm.app.name))
" 2>&1

<details>
<summary>7 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: .venv
░░░░░░░░░░░░░░░░░░░░ [0/0] Installing wheels...                                                                         ░░░░░░░░░░░░░░░░░░░░ [0/20] Installing wheels...                                                                        ░░░░░░░░░░░░░░░░░░░░ [0/20] pyyaml==6.0.3                                                                               █░░░░░░░░░░░░░░░░░░░ [1/20] pyyaml==6.0.3                                                                               █░░░░░░░░░░░░░░░░░░░ [1/20] pluggy==1.6.0                                                                               ██░░░░░░░░░░░░░░░░░░ [2/20] pluggy==1.6.0                                                                               ██░░░░░░░░░░░░░░░░░░ [2/20] ops==3.7.0                                                                                  ███░░░░░░░░░░░░░░░░░ [3/20] ops==3.7.0                                                                                  ███░░░░░░░░░░░░░░░░░ [3/20] typing-extensions==4.15.0                                                                   ████░░░░░░░░░░░░░░░░ [4/20] typing-extensions==4.15.0                                                                   ████░░░░░░░░░░░░░░░░ [4/20] annotated-types==0.7.0                                                                      █████░░░░░░░░░░░░░░░ [5/20] annotated-types==0.7.0                                                                      █████░░░░░░░░░░░░░░░ [5/20] iniconfig==2.3.0                                                                            ██████░░░░░░░░░░░░░░ [6/20] iniconfig==2.3.0                                                                            ██████░░░░░░░░░░░░░░ [6/20] tenacity==9.1.2                                                                             ███████░░░░░░░░░░░░░ [7/20] tenacity==9.1.2                                                                             ███████░░░░░░░░░░░░░ [7/20] packaging==25.0                                                                             ████████░░░░░░░░░░░░ [8/20] packaging==25.0                                                                             ████████░░░░░░░░░░░░ [8/20] cosl==1.6.1                                                                                 █████████░░░░░░░░░░░ [9/20] cosl==1.6.1                                                                                 Installed 20 packages in 5ms
Traceback (most recent call last):
  File "<string>", line 3, in <module>
ModuleNotFoundError: No module named 'charm'
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 9m 18s</sub>

### ✅ `bash`

**Test Context with uv run and PYTHONPATH**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && PYTHONPATH=src:lib uv run --group unit python3 -c "
from ops import testing
from charm import ContentCacheCharm

ctx = testing.Context(ContentCacheCharm)
container = testing.Container('content-cache', can_connect=True)
state_in = testing.State(containers={container})
with ctx(ctx.on.start(), state_in) as mgr:
    out = mgr.run()
    charm = mgr.charm
    print('model.name:', repr(charm.model.name))
    print('unit.name:', repr(charm.unit.name))
    print('app.name:', repr(charm.app.name))
print('ops version:', __import__('ops').__version__)
" 2>&1

```
Traceback (most recent call last):
  File "<string>", line 5, in <module>
AttributeError: module 'ops.testing' has no attribute 'Context'
<exited with exit code 1>
```


---

<sub>⏱️ 9m 24s</sub>

### ✅ `bash`

**Check installed ops version**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && PYTHONPATH=src:lib uv run --group unit python3 -c "import ops; print(ops.__version__)" 2>&1

```
3.7.0
<exited with exit code 0>
```


---

<sub>⏱️ 9m 33s</sub>

### ✅ `bash`

**Check ops.testing API**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && PYTHONPATH=src:lib uv run --group unit python3 -c "import ops.testing; print(dir(ops.testing))" 2>&1

```
['ActionFailed', 'ActionOutput', 'AppUnitOrName', 'CharmBase', 'CharmMeta', 'CharmType', 'Container', 'ExecArgs', 'ExecHandler', 'ExecProcess', 'ExecResult', 'Harness', 'ReadableBuffer', 'RelationNotFoundError', 'RelationRole', 'YAMLStringOrFile', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', '_compatibility_names', 'annotations', 'charm', 'framework', 'model', 'pebble', 'storage']
<exited with exit code 0>
```


---

<sub>⏱️ 9m 46s</sub>

### ✅ `bash`

**Check ops package extras**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && PYTHONPATH=src:lib uv run --group unit pip show ops 2>&1 | grep -E "Requires|Extras"

```
Requires: opentelemetry-api, PyYAML, websocket-client
<exited with exit code 0>
```


---

<sub>⏱️ 9m 46s</sub>

### ✅ `bash`

**Check ops-scenario install**

$ pip show ops 2>/dev/null | grep -E "Requires|Location" && pip show ops-scenario 2>/dev/null | head -5

<details>
<summary>8 lines</summary>

```
Location: /home/ubuntu/.local/lib/python3.12/site-packages
Requires: opentelemetry-api, PyYAML, websocket-client
Name: ops-scenario
Version: 8.7.0
Summary: Python library providing a state-transition testing API for Operator Framework charms.
Home-page: 
Author:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 57s</sub>

### ✅ `bash`

**Check ops testing module location**

$ pip show ops 2>/dev/null | grep -A5 "Provides-Extra" ; python3 -c "import ops.testing; print(ops.testing.__file__)"

```
/home/ubuntu/.local/lib/python3.12/site-packages/ops/testing.py
<exited with exit code 0>
```


---

<sub>⏱️ 9m 57s</sub>

### ✅ `bash`

**Test if Context is available**

$ python3 -c "from ops import testing; print(testing.Context)" 2>&1

```
<class 'scenario.context.Context'>
<exited with exit code 0>
```


---

<sub>⏱️ 10m 4s</sub>

### ❌ `bash`

**Check ops extras**

$ pip show ops 2>/dev/null | cat && cat /home/ubuntu/.local/lib/python3.12/site-packages/ops-3.7.0.dist-info/METADATA 2>/dev/null | grep -A30 "Provides-Extra"

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 10m 10s</sub>

### ✅ `bash`

**Check ops distribution extras**

$ python3 -c "
import importlib.metadata
dist = importlib.metadata.distribution('ops')
print(dist.metadata.get_all('Requires-Dist'))
print(dist.metadata.get_all('Provides-Extra'))
"

```
['PyYAML==6.*', 'websocket-client==1.*', 'opentelemetry-api~=1.0', 'ops-scenario==8.7.0; extra == "testing"', 'ops-tracing==3.7.0; extra == "tracing"']
['testing', 'tracing', 'harness']
<exited with exit code 0>
```


---

<sub>⏱️ 10m 33s</sub>

### 💬 Copilot

Now I understand the full picture. `ops[testing]` installs `ops-scenario==8.7.0` which provides the `Context`/`State` testing API. Let me now migrate the tests:

---

<sub>⏱️ 10m 33s</sub>

### ✅ `sql`

**Mark migrate tests in progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark migrate tests in progress",
  "query": "UPDATE todos SET status = 'in_progress' WHERE id = 'migrate-tests'"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 10m 39s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 10m 46s</sub>

### ✅ `bash`

**Update lockfile with new dependency**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && uv lock 2>&1 | tail -5

```
Resolved 120 packages in 371ms
Added ops-scenario v8.7.0
<exited with exit code 0>
```


---

<sub>⏱️ 10m 51s</sub>

### 💬 Copilot

Now let me write the new test file using Context/State:

---

<sub>⏱️ 10m 51s</sub>

### ✅ `bash`

**Check test fixture files**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4 && cat tests/files/nginx_config.txt | head -5 && echo "---" && ls tests/files/

<details>
<summary>8 lines</summary>

```
proxy_cache_path /var/lib/nginx/proxy/cache use_temp_path=off levels=1:2 keys_zone=39c631ffb52d-cache:10m inactive=10m max_size=10G;

server {
    server_name mysite.local;
    listen 8080;
---
nginx_config.txt		    nginx_config_client_max_body_size.txt
nginx_config_backend_site_name.txt  nginx_config_proxy_cache_revalidate.txt
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 55s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/tests/unit/test_charm.py.**

/tmp/ops-upgrade-experiment/content-cache-k8s-operator__all__C4/tests/unit/test_charm.py (lines 1-80)

<details>
<summary>80 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. import copy
4. import io
5. from datetime import datetime, timedelta
6. from unittest import mock
7. 
8. import pytest
9. from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
10. from ops.testing import Harness
11. 
12. from charm import CONTAINER_PORT, ContentCacheCharm
13. 
14. BASE_CONFIG = {
15.     "site": "mysite.local",
16.     "backend": "http://mybackend.local:80",
17.     "cache_max_size": "10G",
18.     "cache_use_stale": "error timeout updating http_500 http_502 http_503 http_504",
19.     "cache_valid": "200 1h",
20. }
21. CACHE_PATH = "/var/lib/nginx/proxy/cache"
22. CONTAINER_NAME = "content-cache"
23. JUJU_ENV_CONFIG = {
24.     "JUJU_POD_NAME": "content-cache-k8s/0",
25.     "JUJU_POD_NAMESPACE": None,
26.     "JUJU_POD_SERVICE_ACCOUNT": "content-cache-k8s",
27.     "NGINX_BACKEND_SITE_NAME": "mybackend.local",
28.     "NGINX_CACHE_ALL": False,
29.     "NGINX_CACHE_INACTIVE_TIME": "10m",
30.     "NGINX_CACHE_MAX_SIZE": "10G",
31.     "NGINX_CACHE_PATH": "/var/lib/nginx/proxy/cache",
32.     "NGINX_CACHE_REVALIDATE": "off",
33.     "NGINX_CACHE_USE_STALE": "error timeout updating http_500 http_502 http_503 http_504",
34.     "NGINX_CACHE_VALID": "200 1h",
35.     "NGINX_CLIENT_MAX_BODY_SIZE": "1m",
36. }
37. INGRESS_CONFIG = {
38.     "max-body-size": "1m",
39.     "service-hostname": "mysite.local",
40.     "service-name": "content-cache-k8s",
41.     "service-port": CONTAINER_PORT,
42. }
43. PEBBLE_CONFIG = {
44.     "summary": "content-cache layer",
45.     "description": "Pebble config layer for content-cache",
46.     "services": {
47.         CONTAINER_NAME: {
48.             "override": "replace",
49.             "summary": "content-cache",
50.             "command": "/srv/content-cache/entrypoint.sh",
51.             "startup": "enabled",
52.             "environment": "",
53.         },
54.     },
55.     "checks": {
56.         CONTAINER_NAME: {
57.             "override": "replace",
58.             "exec": {"command": "ps -A | grep nginx"},
59.             "threshold": 1,
60.         }
61.     },
62. }
63. 
64. DATE_NOW = datetime.now().strftime("%d/%b/%Y:%H:%M:%S")
65. DATE_20 = (datetime.now() - timedelta(minutes=20, seconds=5)).strftime("%d/%b/%Y:%H:%M:%S")
66. DATE_19 = (datetime.now() - timedelta(minutes=19, seconds=55)).strftime("%d/%b/%Y:%H:%M:%S")
67. 
68. 
69. class TestCharm:
70.     """Unit test battery for the content-cache charm.
71. 
72.     Attrs:
73.         config: Base configuration for content-cache charm.
74.         harness: Test harness.
75.     """
76. 
77.     @pytest.fixture(autouse=True)
78.     def init_tests(self):
79.         self.config = copy.deepcopy(BASE_CONFIG)
80.         self.harness = Harness(ContentCacheCharm)
```

</details>


---

<sub>⏱️ 14m 57s</sub>

### ℹ️ Info

Operation cancelled by user

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
