# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `073b08e5-b1f4-4d1c-937d-d461ed24f0ff`  
> - **Started:** 4/3/2026, 12:56:18 PM  
> - **Duration:** 7m 2s  
> - **Exported:** 4/3/2026, 1:03:21 PM  

---

<sub>⏱️ 5s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 12s</sub>

### ✅ `bash`

**Read pyproject.toml and charmcraft.yaml**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && cat pyproject.toml && echo "---" && cat charmcraft.yaml | head -50

<details>
<summary>90 lines</summary>

```
[project]
name = "zinc-k8s-operator"
version = "0.1.0"
requires-python = ">=3.8"

dependencies = ["ops", "jsonschema", "pydantic", "cosl"]

[project.optional-dependencies]
dev = [
    "cosl",
    "coverage[toml]",
    "pydantic",
    "pytest",
    "ruff",
    "jubilant",
    "ops[testing]",
]

[tool.coverage.run]
branch = true

[tool.coverage.report]
show_missing = true

[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"

# Linting tools configuration
[tool.ruff]
line-length = 99
extend-exclude = ["__pycache__", "*.egg_info"]

[tool.ruff.lint]
select = ["E", "W", "F", "C", "N", "D", "I001"]
ignore = ["E501", "D107"]
extend-ignore = [
    "D203",
    "D204",
    "D213",
    "D215",
    "D400",
    "D404",
    "D406",
    "D407",
    "D408",
    "D409",
    "D413",
]
per-file-ignores = { "tests/*" = ["D100", "D101", "D102", "D103", "D104"] }

[tool.ruff.lint.mccabe]
max-complexity = 10
---
# Copyright 2024 Jon Seager (@jnsgruk)
# See LICENSE file for licensing details.
name: zinc-k8s
description: |
  Zinc is a search engine that does full text indexing. It is a lightweight alternative to
  elasticsearch and runs in less than 100 MB of RAM. It uses bluge as the underlying indexing
  library.

  It is very simple and easy to operate as opposed to elasticsearch which requires a couple dozen
  knobs to understand and tune.

  It is a drop-in replacement for elasticsearch if you are just ingesting data using APIs and
  searching using kibana (Kibana is not supported with zinc. Zinc provides its own UI).
summary: |
  Zinc is a search engine that does full text indexing. It is a lightweight alternative to
  elasticsearch and runs in less than 100 MB of RAM. It uses bluge as the underlying indexing
  library.

type: charm
base: ubuntu@24.04
platforms:
  amd64:

parts:
  zinc-charm:
    plugin: uv
    source: .
    build-packages:
      - git
    build-snaps:
      - astral-uv
    override-build: |
      craftctl default
      git describe --always > $CRAFT_PART_INSTALL/version

assumes:
  - juju >= 3.1

containers:
  zinc:
    resource: zinc-image
    mounts:
      - storage: data
        location: /var/lib/zincsearch

resources:
  zinc-image:
    type: oci-image
    description: OCI image for zinc
    # Included for simplicity in integration tests
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src

```
charm.py
grafana_dashboards
loki_alert_rules
prometheus_alert_rules
zinc.py
```


---

<sub>⏱️ 11s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests

```
conftest.py
integration
spread
unit
```


---

<sub>⏱️ 19s</sub>

### ✅ `bash`

**Read charm source files**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && cat src/charm.py && echo "===" && cat src/zinc.py

<details>
<summary>153 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2024 Jon Seager (@jnsgruk)
# See LICENSE file for licensing details.

"""Charmed Operator for Zinc; a lightweight elasticsearch alternative."""

import logging
import secrets

import ops
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
from charms.parca_k8s.v0.parca_scrape import ProfilingEndpointProvider
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer

from zinc import Zinc

logger = logging.getLogger(__name__)


class ZincCharm(ops.CharmBase):
    """Charmed Operator for Zinc; a lightweight elasticsearch alternative."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.zinc_pebble_ready, self._on_zinc_pebble_ready)
        self.framework.observe(self.on.update_status, self._on_update_status)

        self._container = self.unit.get_container("zinc")
        self._zinc = Zinc()

        # Provide ability for Zinc to be scraped by Prometheus using prometheus_scrape
        self._scraping = MetricsEndpointProvider(
            self,
            relation_name="metrics-endpoint",
            jobs=[{"static_configs": [{"targets": [f"*:{self._zinc.port}"]}]}],
        )

        # Enable log forwarding for Loki and other charms that implement loki_push_api
        self._logging = LogProxyConsumer(
            self, relation_name="log-proxy", log_files=[self._zinc.log_path]
        )

        # Provide grafana dashboards over a relation interface
        self._grafana_dashboards = GrafanaDashboardProvider(
            self, relation_name="grafana-dashboard"
        )

        # Enable profiling over a relation with Parca
        self._profiling = ProfilingEndpointProvider(
            self, jobs=[{"static_configs": [{"targets": [f"*:{self._zinc.port}"]}]}]
        )

        self._ingress = IngressPerAppRequirer(
            self,
            host=f"{self.app.name}.{self.model.name}.svc.cluster.local",
            port=self._zinc.port,
            strip_prefix=True,
        )

    def _on_zinc_pebble_ready(self, event: ops.WorkloadEvent):
        """Define and start a workload using the Pebble API."""
        password = self._generated_password()
        self._container.make_dir(self._zinc.log_dir, make_parents=True, permissions=0o755)
        self._container.add_layer("zinc", self._zinc.pebble_layer(password), combine=True)
        self._container.replan()

        self.unit.set_workload_version(self._zinc.version)
        self.unit.open_port(protocol="tcp", port=self._zinc.port)

        self.unit.status = ops.ActiveStatus()

    def _on_update_status(self, _):
        """Update the status of the application."""
        if self._container.can_connect() and self._container.get_services("zinc"):
            self.unit.set_workload_version(self._zinc.version)

    def _generated_password(self) -> str:
        """Report the generated admin password; generate one if it doesn't exist."""
        # If the peer relation is not ready, just return an empty string
        relation = self.model.get_relation("zinc-peers")
        if not relation:
            return ""

        # If the secret already exists, grab its content and return it
        secret_id = relation.data[self.app].get("initial-admin-password", None)
        if secret_id:
            secret = self.model.get_secret(id=secret_id)
            return secret.peek_content().get("password")

        if self.unit.is_leader():
            content = {"password": secrets.token_urlsafe(24)}
            secret = self.app.add_secret(content)
            # Store the secret id in the peer relation for other units if required
            relation.data[self.app]["initial-admin-password"] = secret.id
            return content["password"]
        else:
            return ""


if __name__ == "__main__":  # pragma: nocover
    ops.main(ZincCharm)
===
#!/usr/bin/env python3
# Copyright 2024 Jon Seager (@jnsgruk)
# See LICENSE file for licensing details.

"""Assist with client interactions with Zinc."""

import json
import logging
import time
import urllib.request

logger = logging.getLogger(__name__)


class Zinc:
    """Represent a Zinc instance in the workload."""

    _port = 4080
    _log_path = "/var/lib/zincsearch/zinc.log"
    _log_dir = "/var/lib/zincsearch"

    def pebble_layer(self, initial_password) -> dict:
        """Return a Pebble layer for managing Zinc."""
        return {
            "services": {
                "zinc": {
                    "override": "replace",
                    "summary": "zinc",
                    # go-runner achieves the equivalent of:`bash -c '/bin/zinc | tee PATH'`, but
                    # without including bash etc. in the image.
                    "command": f"/bin/go-runner --log-file={self.log_path} --also-stdout=true --redirect-stderr=true /bin/zincsearch",
                    "startup": "enabled",
                    "environment": {
                        "ZINC_DATA_PATH": "/var/lib/zincsearch",
                        "ZINC_FIRST_ADMIN_USER": "admin",
                        "ZINC_FIRST_ADMIN_PASSWORD": initial_password,
                        "ZINC_PROMETHEUS_ENABLE": True,
                        "ZINC_TELEMETRY": False,
                        "ZINC_PROFILER": True,
                    },
                }
            },
        }

    @property
    def log_path(self) -> str:
        """Report the path that Zinc is configured to output logs."""
        return self._log_path

    @property
    def log_dir(self) -> str:
        """Report the directory that Zinc is configured to output logs."""
        return self._log_dir

    @property
    def port(self) -> int:
        """Report the TCP port that Zinc is bound to."""
        return self._port

    @property
    def version(self) -> str:
        """Reports the current Zinc version."""
        try:
            return self._request_version()
        # Catching Exception is not ideal, but we don't care much for the error here, and just
        # default to setting a blank version since there isn't much the admin can do!
        except Exception as e:
            logger.warning("unable to get version from API: %s", str(e))
            logger.debug(e, exc_info=True)
            return ""

    def _request_version(self) -> str:
        """Fetch the version from the running workload using the Zinc API."""
        retries = 0
        while True:
            try:
                res = urllib.request.urlopen(f"http://localhost:{self._port}/version")
                return json.loads(res.read().decode())["version"]
            except Exception:
                if retries == 3:
                    raise
                retries += 1
                time.sleep(3)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 19s</sub>

### ✅ `bash`

**Read unit tests**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && ls tests/unit/ && cat tests/unit/*.py 2>/dev/null | head -200

<details>
<summary>127 lines</summary>

```
test_charm.py  test_zinc.py
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import PropertyMock, patch

import pytest
from ops.pebble import ServiceStatus
from ops.testing import ActiveStatus, Container, Context, PeerRelation, Secret, State, TCPPort

from charm import ZincCharm
from zinc import Zinc


@pytest.fixture
def charm():
    with patch("charm.Zinc.version", new_callable=PropertyMock(return_value="0.2.6")):
        yield ZincCharm


@pytest.fixture
def loaded_ctx(charm):
    ctx = Context(charm)
    container = Container(name="zinc", can_connect=True)
    return (ctx, container)


def _fetch_zinc_password_from_pebble_plan(state: State):
    return (
        state.get_container("zinc")
        .layers["zinc"]
        .services["zinc"]
        .environment["ZINC_FIRST_ADMIN_PASSWORD"]
    )


def test_zinc_pebble_ready(loaded_ctx):
    ctx, container = loaded_ctx
    state = State(containers=[container])

    result = ctx.run(ctx.on.pebble_ready(container=container), state)

    assert result.get_container("zinc").layers["zinc"] == Zinc().pebble_layer("")
    assert result.get_container("zinc").service_statuses == {"zinc": ServiceStatus.ACTIVE}
    assert result.opened_ports == frozenset({TCPPort(4080)})
    assert result.workload_version == "0.2.6"
    assert result.unit_status == ActiveStatus()


def test_update_status(loaded_ctx):
    ctx, container = loaded_ctx
    state = State(containers=[container])

    result = ctx.run(ctx.on.pebble_ready(container=container), state)
    assert result.workload_version == "0.2.6"

    with patch("charm.Zinc.version", new_callable=PropertyMock(return_value="0.4.0")):
        result = ctx.run(ctx.on.update_status(), result)
        assert result.workload_version == "0.4.0"

    assert result.unit_status == ActiveStatus()


def test_zinc_password_no_relation(loaded_ctx):
    ctx, container = loaded_ctx
    state = State(containers=[container])

    result = ctx.run(ctx.on.pebble_ready(container=container), state)

    password = _fetch_zinc_password_from_pebble_plan(result)
    assert len(password) == 0


def test_zinc_password_from_relation(loaded_ctx):
    ctx, container = loaded_ctx
    secret = Secret(tracked_content={"password": "deadbeef"}, owner="app")
    state = State(
        containers=[container],
        secrets={secret},
        relations=[
            PeerRelation(
                endpoint="zinc-peers", local_app_data={"initial-admin-password": secret.id}
            )
        ],
    )

    result = ctx.run(ctx.on.pebble_ready(container=container), state)

    password = _fetch_zinc_password_from_pebble_plan(result)
    assert password == "deadbeef"


def test_zinc_password_create_as_leader(loaded_ctx):
    ctx, container = loaded_ctx
    state = State(
        containers=[container],
        leader=True,
        relations=[PeerRelation(endpoint="zinc-peers", local_app_data={})],
    )

    result = ctx.run(ctx.on.pebble_ready(container=container), state)

    password = _fetch_zinc_password_from_pebble_plan(result)
    assert len(password) == 32


def test_zinc_password_create_as_non_leader(loaded_ctx):
    ctx, container = loaded_ctx
    state = State(
        containers=[container],
        leader=False,
        relations=[PeerRelation(endpoint="zinc-peers", local_app_data={})],
    )

    result = ctx.run(ctx.on.pebble_ready(container=container), state)

    password = _fetch_zinc_password_from_pebble_plan(result)
    assert len(password) == 0
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest

from zinc import Zinc


@pytest.fixture()
def zinc():
    return Zinc()


def test_property_pebble_layer(zinc):
    expected = {
        "services": {
            "zinc": {
                "override": "replace",
                "summary": "zinc",
                "command": "/bin/go-runner --log-file=/var/lib/zincsearch/zinc.log --also-stdout=true --redirect-stderr=true /bin/zincsearch",
                "startup": "enabled",
                "environment": {
                    "ZINC_DATA_PATH": "/var/lib/zincsearch",
                    "ZINC_FIRST_ADMIN_USER": "admin",
                    "ZINC_FIRST_ADMIN_PASSWORD": "password",
                    "ZINC_PROMETHEUS_ENABLE": True,
                    "ZINC_TELEMETRY": False,
                    "ZINC_PROFILER": True,
                },
            }
        },
    }
    assert zinc.pebble_layer("password") == expected


def test_property_port_returns_int(zinc):
    assert isinstance(zinc.port, int)


def test_property_port_returns_str(zinc):
    assert isinstance(zinc.log_path, str)
    assert zinc.log_path[0] == "/"


@patch("charm.Zinc._request_version", lambda x: "0.2.6")
def test_version_returns_str(zinc):
    assert isinstance(zinc.version, str)
    assert zinc.version == "0.2.6"


@patch("charm.Zinc._request_version")
def test_version_returns_empty_string_when_request_fails(request_version, zinc):
    request_version.side_effect = Exception
    assert isinstance(zinc.version, str)
    assert zinc.version == ""
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 20s</sub>

### ✅ `bash`

**Check current ops version**

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

### ✅ `bash`

**Check ops version in uv.lock**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && grep -E "ops" uv.lock | head -30

<details>
<summary>14 lines</summary>

```
{ name = "ops" },
name = "ops"
sdist = { url = "https://files.pythonhosted.org/packages/93/98/84789a5e15ad76e043301bbd70b4d39cffaa717ae6eecb662fd0dd0cc7af/ops-2.23.2.tar.gz", hash = "sha256:a69b0c5bc65ebd91720fc96459e81b969df851f3a6c9c855ee73de7004205987", size = 528074, upload-time = "2026-02-11T03:58:15.565Z" }
    { url = "https://files.pythonhosted.org/packages/e0/00/65da7c96d0f9e13c4de3bdd2e3717259fe723ff4bd4e5dc714164f851032/ops-2.23.2-py3-none-any.whl", hash = "sha256:9cab0c6bc46eeff2e96777128200c3ef872b55641b12f07dc4fd6fe3103954be", size = 188415, upload-time = "2026-02-11T03:58:13.693Z" },
    { name = "ops-scenario" },
name = "ops-scenario"
    { name = "ops" },
sdist = { url = "https://files.pythonhosted.org/packages/ee/e7/1514b9c27b9364ec1d04791b0fb76d1a629c8cc73f90fbf6dd867457c914/ops_scenario-7.23.2.tar.gz", hash = "sha256:327dda8b3c871ccf16246ed4f8c7e093526af42093549976596cede58cbc8488", size = 70017, upload-time = "2026-02-11T03:58:16.553Z" }
    { url = "https://files.pythonhosted.org/packages/01/15/3b59993cad1b2838c9bb20f6f2ed5297fcf490025b1ffecc27d06be1daba/ops_scenario-7.23.2-py3-none-any.whl", hash = "sha256:024b638e0ea94e8f2e3c642d4f96031b0c7ac4f39117b97107dc9a09503651b4", size = 64328, upload-time = "2026-02-11T03:58:14.916Z" },
    { name = "ops" },
    { name = "ops", extra = ["testing"] },
    { name = "ops" },
    { name = "ops", extras = ["testing"], marker = "extra == 'dev'" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 31s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/releases",
  "max_length": 20000
}
```

</details>

<details>
<summary>194 lines</summary>

```
Contents of https://github.com/canonical/operator/releases:
## 3.7.0: ops.testing usability improvements

30 Mar 05:16

Immutable release. Only release title and notes can be modified.

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

## 3.6.0: Use Juju 3.6.14 as the default version in ops.testing

26 Feb 04:18

In this release, the `ops.testing` `Context` sets the mock Juju version to `3.6.14` (you can [customise](https://documentation.ubuntu.com/ops/latest/reference/ops-testing/#ops.testing.Context) this if needed).

If you're using Pebble's `exec` to run commands in containers, and the `exec` failed (with a timeout, for example), the exception would previously include the entire command that was attempted; it now only includes the first item, to protect against sensitive data leaking into exceptions. However, we _strongly_ recommend against passing sensitive data in the command line - use other methods (such as environment variables) whenever possible.

If you'd like to use [Pydantic's experimental `MISSING` sentinel](https://docs.pydantic.dev/latest/concepts/experimental/#missing-sentinel), that will now work with `Relation.save` (ops will consider a value of `MISSING` to mean "delete from Juju").

## What's Changed

### Features

*   Bump default Juju version in `ops.testing.Context` to 3.6.14 in [#2316](https://github.com/canonical/operator/pull/2316)

### Fixes

*   Correct the `Model.get_binding()` return type in [#2329](https://github.com/canonical/operator/pull/2329)
*   Only show executable in `ExecError.__str__`, not full command line in [#2336](https://github.com/canonical/operator/pull/2336)
*   Support Pydantic `MISSING` sentinel in `ops.Relation.save` in [#2306](https://github.com/canonical/operator/pull/2306)

### Documentation

*   Add how-to subcategory for managing containers in [#2309](https://github.com/canonical/operator/pull/2309)
*   Remove 2.19 version in docs, tweak ops.testing title in [#2332](https://github.com/canonical/operator/pull/2332)
*   Use "true" and "false" consistently in the reference documentation in [#2330](https://github.com/canonical/operator/pull/2330)
*   Add CLI args as another place to not put sensitive data in [#2334](https://github.com/canonical/operator/pull/2334)
*   Fix remote unit kwarg in testing example in [#2342](https://github.com/canonical/operator/pull/2342)
*   Clarify that secret labels are not names in [#2337](https://github.com/canonical/operator/pull/2337)

### Tests

*   Set `SCENARIO_BARE_CHARM_ERRORS=true` in Ops tests that care in [#2314](https://github.com/canonical/operator/pull/2314)

### CI

*   Fix releasing on branches with no `versions.md` doc in [#2323](https://github.com/canonical/operator/pull/2323)

**Full Changelog**: [3.5.2...3.6.0](https://github.com/canonical/operator/compare/3.5.2...3.6.0)

## 3.5.2: fixes for testing package build and more

11 Feb 01:49

This release is prompted by a fix to recent build failures for `ops[testing]`. The release also includes a couple of minor fixes for the testing framework itself: making the `level` argument of `testing.CheckInfo` type checking compatible with `pebble.CheckInfo.level`, and baking in the knowledge that `credential-get` is available on K8s in newer Juju versions.

## What's Changed

### Fixes

*   Make testing.CheckInfo level arg type match pebble.CheckInfo.level in [#2274](https://github.com/canonical/operator/pull/2274)
*   Make testing consistency check aware that `credential-get` is available on k8s in newer Juju in [#2307](https://github.com/canonical/operator/pull/2307)
*   Drop unused `setuptools_scm` build dependency in [#2310](https://github.com/canonical/operator/pull/2310)

### Documentation

*   Update Pebble version in Juju 3.6 in [#2295](https://github.com/canonical/operator/pull/2295)
*   Refresh K8s tutorial to use Concierge and uv-based Charmcraft profile in [#2285](https://github.com/canonical/operator/pull/2285)
*   Add missing "How to" in page titles in [#2289](https://github.com/canonical/operator/pull/2289)
*   Fix and improve observability part of K8s tutorial in [#2305](https://github.com/canonical/operator/pull/2305)

**Full Changelog**: [3.5.1...3.5.2](https://github.com/canonical/operator/compare/3.5.1...3.5.2)

## 2.23.2: fix testing package build

11 Feb 03:57

## What's Changed

This release fixes a recent build failure for `ops[testing]`.

## Fixes

*   Drop unused `setuptools_scm` build dependency in [#2318](https://github.com/canonical/operator/pull/2318)

## Documentation

*   For 2.23, update links and config for switch to documentation.ubuntu.com/ops in [#1942](https://github.com/canonical/operator/pull/1942)
*   For 2.x, fix site title and unstyled error pages in [#1945](https://github.com/canonical/operator/pull/1945)
*   For 2.x, remove .html extensions in [#1954](https://github.com/canonical/operator/pull/1954)
*   For 2.x, fix unstyled error pages in [#1973](https://github.com/canonical/operator/pull/1973)

**Full Changelog**: [2.23.1...2.23.2](https://github.com/canonical/operator/compare/2.23.1...2.23.2)

## 3.5.1: fixes and documentation improvements

28 Jan 03:10

This is a maintenance release that includes work on Ops internals and documentation.

## What's Changed

### Fixes

*   Use `parse_rfc3339` for datetime parsing to support Juju 4 in [#2264](https://github.com/canonical/operator/pull/2264)
*   Correct the value of `additional_properties` in the action meta in Juju 4 in [#2250](https://github.com/canonical/operator/pull/2250)
*   Prevent `KeyError` on `auth-type` when creating `CloudCredential` object in [#2268](https://github.com/canonical/operator/pull/2268)
*   `_checks_action` should return empty list when there are no changes in [#2270](https://github.com/canonical/operator/pull/2270)

### Documentation

*   Provide examples in unit testing how-to, and other small improvements in [#2251](https://github.com/canonical/operator/pull/2251)
*   Update the action how-to to explain the additionalProperties default flip in [#2249](https://github.com/canonical/operator/pull/2249)
*   For state-transition tests, clarify about immutability and reusing state in [#2153](https://github.com/canonical/operator/pull/2153)
*   Fix and clarify holistic example of handling storage in [#2098](https://github.com/canonical/operator/pull/2098)
*   Remove comments from K8s tutorial and clarify about persisting data in [#2253](https://github.com/canonical/operator/pull/2253)
*   Clarify handling of postgres relation data in K8s tutorial in [#2256](https://github.com/canonical/operator/pull/2256)
*   Improve unit tests of httpbin demo charm in [#2254](https://github.com/canonical/operator/pull/2254)
*   Add version information for tools in the charming ecosystem in [#2231](https://github.com/canonical/operator/pull/2231)
*   Avoid emojis that render differently across platforms in [#2273](https://github.com/canonical/operator/pull/2273)
*   Secrets over CMR comment added in [#2271](https://github.com/canonical/operator/pull/2271)
*   Fix charm name in httpbin deploy command in [#2276](https://github.com/canonical/operator/pull/2276)
*   Updated [security@ubuntu.com](mailto:security@ubuntu.com) PGP key in [#2286](https://github.com/canonical/operator/pull/2286)

### Tests

*   Remove unnecessary test module in [#2247](https://github.com/canonical/operator/pull/2247)

### CI

*   Replace git reference injection with wheel artifacts in charm test workflows in [#2252](https://github.com/canonical/operator/pull/2252)
*   Explicitly provide the charmcraft repo location in CI in [#2277](https://github.com/canonical/operator/pull/2277)
*   Remove outdated custom signature generation in [#2280](https://github.com/canonical/operator/pull/2280)

**Full Changelog**: [3.5.0...3.5.1](https://github.com/canonical/operator/compare/3.5.0...3.5.1)

## 3.5.0: env var to control extension wrapping in testing

18 Dec 02:25

This is a small release with some user-facing changes to `ops.testing`.

We've added an environment variable to disable the use of `UncaughtCharmError` in testing. By default, exceptions raised from charm code are wrapped in an `UncaughtCharmError` in state-transition tests. This makes debugging harder and adds extra steps to making assertions about expected errors in tests. Set `SCENARIO_BARE_CHARM_ERRORS=true` to have exceptions be propagated to your test code as-is instead. This may become the default behaviour in a future major `ops` release. You can lock in the current default behaviour explicitly by setting `SCENARIO_BARE_CHARM_ERRORS=false` in your test runners.

Additionally, the `ops.testing.Context.charm_spec` attribute is now deprecated -- this is intended for internal use only, and was not widely used, so the warning should steer new users in the right direction.

## What's Changed

### Features

*   Env var to control exception wrapping in tests in [#2142](https://github.com/canonical/operator/pull/2142)
*   Deprecate testing.Context.charm\_spec in [#2219](https://github.com/canonical/operator/pull/2219)

### Documentation

*   Fix charmcraft init command in [#2210](https://github.com/canonical/operator/pull/2210)
*   Update CI examples to use uv and tox-uv in [#2213](https://github.com/canonical/operator/pull/2213)
*   Update and clarify info about environment prep in [#2217](https://github.com/canonical/operator/pull/2217)
*   Match Charmcraft profiles in tox.ini example for integration testing in [#2221](https://github.com/canonical/operator/pull/2221)
*   Use base 24.04 for httpbin-demo charm in [#2222](https://github.com/canonical/operator/pull/2222)
*   Clarify parts of the machine charm tutorial in [#2223](https://github.com/canonical/operator/pull/2223)
*   Match Charmcraft profiles in "Write and structure charm code" in [#2220](https://github.com/canonical/operator/pull/2220)
*   Use cosl binary in K8s tutorial charm to work around error in [#2232](https://github.com/canonical/operator/pull/2232)
*   Fix URL issues by updating doc starter pack in [#2238](https://github.com/canonical/operator/pull/2238)

### Tests

*   Don't skip tests if ops\[testing\] isn't installed in [#2215](https://github.com/canonical/operator/pull/2215)
*   Switch the integration test charms to use the uv plugin in [#2218](https://github.com/canonical/operator/pull/2218)

### CI

*   Avoid jitter in the best practice doc PRs in [#2193](https://github.com/canonical/operator/pull/2193)
*   Ignore PERF401 (manual list comprehension) across the repo in [#2201](https://github.com/canonical/operator/pull/2201)
*   The git commands need to be run in the operator directory as well in [#2197](https://github.com/canonical/operator/pull/2197)
*   Have cycle in the sbomber manifests use the default value in [#2209](https://github.com/canonical/operator/pull/2209)
*   Add pytest.warns to note an expected warning in [#2092](https://github.com/canonical/operator/pull/2092)
*   Update release script to handle non-final versions in [#2199](https://github.com/canonical/operator/pull/2199)
*   Add ops-tracing as a dependency for the observability tests in [#2239](https://github.com/canonical/operator/pull/2239)
*   Add scheduled workflow for packing and integration testing example charms in [#2233](https://github.com/canonical/operator/pull/2233)

**Full Changelog**: [3.4.0...3.5.0](https://github.com/canonical/operator/compare/3.4.0...3.5.0)

## 3.4.0: a low-level API for the Juju hook commands

27 Nov 04:45

The main feature in this release is the introduction of `ops.hookcmds`, which provides an API to the Juju hook commands. The API is low-level, complete (other than deprecated commands), and generally a 1-1 mapping to the hook commands, but providing a Pythonic interface.

Additionally, the length of the defer queue is now logged; more arguments can be passed as paths to `ops.Container` and `ops.PebbleClient` methods; and state transition testing `Context` has gained optional availability zone and principal unit arguments.

## What's Changed

### Breaking Changes

There are breaking changes in this release. Please review them carefully:

*   Fix: Change `JujuContext.machine_id` from `int` to `str` in [#2108](https://github.com/canonical/operator/pull/2108)
    *   Note that this fix was already included in Ops 3.3.1
    *   If you use this field, you may need to adjust type hints in your code
*   Fix: Ensure that the testing context manager is exited when an exception occurs in [#2117](https://github.com/canonical/operator/pull/2117)
    *   If you use `ops.testing.Context` as a context manager and expect the charm to raise an exception, you need to adjust the expected exception type.

### Features

*   Add a low-level API for the Juju hook commands in [#2019](https://github.com/canonical/operator/pull/2019)
*   Make PebbleClient file methods also accept pathlib.PurePath in [#2097](https://github.com/canonical/operator/pull/2097)
*   Log the total number of deferred events in [#2161](https://github.com/canonical/operator/pull/2161)
*   Allow setting the Juju availability zone and principal unit in the testing Context in [#2187](https://github.com/canonical/operator/pull/2187)

### Fixes

*   Allow actions without params or descriptions in ops\[testing\] in [#2090](https://github.com/canonical/operator/pull/2090)
*   Ensure `ops.Pebble.pull` cleans up temporary files if it errors in [#2087](https://github.com/canonical/operator/pull/2087)
*   Make secret info description visible to the charm in ops\[testing\] in [#2115](https://github.com/canonical/operator/pull/2115)
*   Raise ActionFailed when using Context as a context manager in [#2121](https://github.com/canonical/operator/pull/2121)
*   Detect categories with an explanation mark indicating breaking changes in [#2132](https://github.com/canonical/operator/pull/2132)
*   Normalise Secret.owner to 'app' for ops\[testing\] output state in [#2127](https://github.com/canonical/operator/pull/2127)
*   Don't cache secret metadata in Ops in [#2143](https://github.com/canonical/operator/pull/2143)
*   Secret-info-get cannot be provided with both an ID and a label in [#2170](https://github.com/canonical/operator/pull/2170)
*   Minor hookcmds fixes in [#2175](https://github.com/canonical/operator/pull/2175)

### Documentation

*   Update referenced examples for managing interfaces in [#2068](https://github.com/canonical/operator/pull/2068)
*   Tidy up spelling and formatting in several places in [#2060](https://github.com/canonical/operator/pull/2060)
*   Add missing assignment to state\_out in unit tests how-to in [#2075](https://github.com/canonical/operator/pull/2075)
*   Update the holistic/delta explanation with the reconciler pattern in [#2029](https://github.com/canonical/operator/pull/2029)
*   Fix broken setup/teardown links in README in [#2094](https://github.com/canonical/operator/pull/2094)
*   Update info about release docs, mark testing changelog as not maintained in [#2074](https://github.com/canonical/operator/pull/2074)
*   Switch to makefile for building the docs in [#2073](https://github.com/canonical/operator/pull/2073)
*   Document how to extract the charm instance from the testing context in [#2084](https://github.com/canonical/operator/pull/2084)
*   Add a how-to guide for migrating away from Harness in [#2062](https://github.com/canonical/operator/pull/2062)
*   Rename hook tools to hook commands in [#2114](https://github.com/canonical/operator/pull/2114)
*   Remove legacy how-to guide for Harness in [#2122](https://github.com/canonical/operator/pull/2122)
*   Update the Juju release the metrics functionality is removed from 4.0 to 3.6.11 in [#2126](https://github.com/canonical/operator/pull/2126)
*   Clarify that Context is the testing context not only the Juju context in [#2123](https://github.com/canonical/operator/pull/2123)
*   Explain the Charmhub public listing process and add a reference list of best practices in [#1989](https://github.com/canonical/operator/pull/1989)
*   Expand next steps for K8s tutorial in [#2034](https://github.com/canonical/operator/pull/2034)
*   Remove mention of the `simple` Charmcraft profile in [#2138](https://github.com/canonical/operator/pull/2138)
*   Expand landing pages with summaries of pages in [#2140](https://github.com/canonical/operator/pull/2140)
*   Update environment setup for integration tests and K8s tutorial in [#2124](https://github.com/ca

<note>Content truncated. Call the fetch tool with a start_index of 20000 to get more content.</note>
```

</details>


---

<sub>⏱️ 36s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 20000,
  "url": "https://github.com/canonical/operator/releases",
  "start_index": 20000
}
```

</details>

<details>
<summary>117 lines</summary>

```
Contents of https://github.com/canonical/operator/releases:
nonical/operator/pull/2124)
*   Replace machine charm tutorial by an improved tutorial in [#2119](https://github.com/canonical/operator/pull/2119)
*   Change HACKING.md instructions for maintaining Charmcraft profiles in [#2151](https://github.com/canonical/operator/pull/2151)
*   In integration tests, use consistent approach to logging and packing in [#2150](https://github.com/canonical/operator/pull/2150)
*   In integration testing how-to, clarify that Juju model is destroyed after module all tests in the module complete in [#2154](https://github.com/canonical/operator/pull/2154)
*   Remove Charmcraft channel specifier from machine charm tutorial in [#2148](https://github.com/canonical/operator/pull/2148)
*   Add AI contribution note and style guideline for type annotation of return values in [#2168](https://github.com/canonical/operator/pull/2168)
*   Add ops\[testing\] to the ops.testing docstring in [#2171](https://github.com/canonical/operator/pull/2171)
*   Add links to the Juju hook from each event class in [#2176](https://github.com/canonical/operator/pull/2176)
*   Add a short umask note in [#2184](https://github.com/canonical/operator/pull/2184)

### Tests

*   Re-enable testing consistency checks after disabling them in [#2141](https://github.com/canonical/operator/pull/2141)
*   Expand secrets integration and state transition tests in [#2130](https://github.com/canonical/operator/pull/2130)

### Refactoring

*   Use ops.hookcmds in \_ModelBackend in [#2116](https://github.com/canonical/operator/pull/2116)
*   Don't get the storage details from --help in [#2172](https://github.com/canonical/operator/pull/2172)
*   Drop 3.8 and 3.9 compatibility code in [#2173](https://github.com/canonical/operator/pull/2173)
*   Use json.dumps to produce the YAML in relation-set and state-set in [#2174](https://github.com/canonical/operator/pull/2174)
*   Rely on type annotations instead of casts in hookcmds in [#2179](https://github.com/canonical/operator/pull/2179)

### CI

*   Add integration and state transition tests for the secrets API in [#2078](https://github.com/canonical/operator/pull/2078)
*   Temporarily disable tracing integration tests in [#2102](https://github.com/canonical/operator/pull/2102)
*   Add secrets tests follow-up in [#2105](https://github.com/canonical/operator/pull/2105)
*   Support monorepos in ops charm compatibility testing in [#2100](https://github.com/canonical/operator/pull/2100)
*   Test both Charmcraft 3 and Charmcraft 4 profiles in [#2103](https://github.com/canonical/operator/pull/2103)
*   Add automated doc checks (and related starter pack updates) in [#2099](https://github.com/canonical/operator/pull/2099)
*   Clean up accidental workflow trigger in [#2144](https://github.com/canonical/operator/pull/2144)
*   Test if package versions match dependency versions before publishing in [#2139](https://github.com/canonical/operator/pull/2139)
*   Update spelling in [#2167](https://github.com/canonical/operator/pull/2167)
*   Test against 4.0/stable in [#2186](https://github.com/canonical/operator/pull/2186)
*   Store charmcraft logs if smoke tests fail in [#2192](https://github.com/canonical/operator/pull/2192)
*   Use Juju channel 4/stable in Ops smoke tests in [#2190](https://github.com/canonical/operator/pull/2190)

**Full Changelog**: [3.3.0...3.4.0](https://github.com/canonical/operator/compare/3.3.0...3.4.0)

## 3.4.0b3 Fix dependency version in testing extra

18 Nov 04:51

Pre-release

3.4.0b2 was not released to PyPI, as there was an error in the `testing` optional extra. This release is otherwise identical to 3.4.0b2.

## 3.4.0b2 Small hookcmds fixes

18 Nov 04:09

Pre-release

This second beta for the 3.4.0 release fixes one significant bug with the new `ops.hookcmds` usage in the model backend, where getting secret info when the secret object had both ID and label set would fail.

In addition, we now include the size of the defer queue in the (debug-level) log message when processing deferrals.

## What's Changed

### Features

*   Log the total number of deferred events in [#2161](https://github.com/canonical/operator/pull/2161)

### Fixes

*   Normalise `Secret.owner` to 'app' for ops\[testing\] output state in [#2127](https://github.com/canonical/operator/pull/2127)
*   Don't cache secret metadata in Ops in [#2143](https://github.com/canonical/operator/pull/2143)
*   `secret-info-get` cannot be provided with both an ID and a label in [#2170](https://github.com/canonical/operator/pull/2170)
*   Minor hookcmds fixes in [#2175](https://github.com/canonical/operator/pull/2175)

### Documentation

*   Explain the Charmhub public listing process and add a reference list of best practices in [#1989](https://github.com/canonical/operator/pull/1989)
*   Expand next steps for K8s tutorial in [#2034](https://github.com/canonical/operator/pull/2034)
*   Remove mention of the `simple` Charmcraft profile in [#2138](https://github.com/canonical/operator/pull/2138)
*   Expand landing pages with summaries of pages in [#2140](https://github.com/canonical/operator/pull/2140)
*   Update environment setup for integration tests and K8s tutorial in [#2124](https://github.com/canonical/operator/pull/2124)
*   Replace machine charm tutorial by an improved tutorial in [#2119](https://github.com/canonical/operator/pull/2119)
*   Change HACKING.md instructions for maintaining Charmcraft profiles in [#2151](https://github.com/canonical/operator/pull/2151)
*   In integration tests, use consistent approach to logging and packing in [#2150](https://github.com/canonical/operator/pull/2150)
*   In integration testing how-to, clarify that Juju model is destroyed after module in [#2154](https://github.com/canonical/operator/pull/2154)
*   Remove Charmcraft channel specifier from machine charm tutorial in [#2148](https://github.com/canonical/operator/pull/2148)
*   Add AI contribution note and style guideline for type annotation of return values in [#2168](https://github.com/canonical/operator/pull/2168)
*   Add ops\[testing\] to the ops.testing docstring in [#2171](https://github.com/canonical/operator/pull/2171)
*   Add links to the Juju hook from each event class in [#2176](https://github.com/canonical/operator/pull/2176)

### Tests

*   Re-enable ops\[testing\] consistency checks after disabling them in [#2141](https://github.com/canonical/operator/pull/2141)
*   Expand secrets integration and state transition tests in [#2130](https://github.com/canonical/operator/pull/2130)

### Refactoring

*   Don't get the storage details from `--help` in [#2172](https://github.com/canonical/operator/pull/2172)
*   Drop Python 3.8 and 3.9 compatibility code in [#2173](https://github.com/canonical/operator/pull/2173)

### CI

*   Clean up accidental workflow trigger in [#2144](https://github.com/canonical/operator/pull/2144)
*   Test if package versions match dependency versions before publishing in [#2139](https://github.com/canonical/operator/pull/2139)
*   Update spelling in [#2167](https://github.com/canonical/operator/pull/2167)

**Full Changelog**: [3.4.0b1...3.4.0b2](https://github.com/canonical/operator/compare/3.4.0b1...3.4.0b2)

## 3.4.0b1: ops.hookcmds - a low-level API for the Juju hook commands

22 Oct 03:44

Pre-release

The main feature in this release is the introduction of `ops.hookcmds`, which provides an API to the Juju hook commands. The API is low-level, complete (other than deprecated commands), and generally a 1-1 mapping to the hook commands, but providing a Pythonic interface.

The intention is that this makes it easier to build experimental charm APIs or frameworks (in particular, having the Juju knowledge encapsulated in Ops) rather than for charms to use the `ops.hookcmds` package directly. This new API is also used by the Ops model, which is the primary reason we are doing a beta release. We're confident that there will be no charm-visible differences, but this is at the heart of the framework, so we would really appreciate you trying it out and letting us know if there are any issues. We expect to release a 3.4.0 final in mid November 2025.

There is also a breaking change to `ops.testing` as part of a bug fix in this release. Previously, if using `testing.Context()` as a context manager, cleanup was not properly run. This meant that exceptions did not get wrapped in `UncaughtCharmError` as with a regular `run()`, `ActionFailed` wasn't raised if the action failed, the environment wasn't properly cleaned up, and so on. If you have tests that are using `testing.Context()` in this way, and are doing a `pytest.raises` with the actual exception, you'll need to update those to expect `UncaughtCharmError`.

There are also the usual set of bug fixes, documentation improvements, and also one small feature: if you're using `ops.pebble.Client` directly (most of you probably use `ops.Container`), you can now pass in `pathlib.Path` objects rather than just `str`.

## What's Changed

### Breaking Changes

*   Fix: Ensure that the testing context manager is exited when an exception occurs in [#2117](https://github.com/canonical/operator/pull/2117)

### Features

*   Add a low-level API for the Juju hook commands in [#2019](https://github.com/canonical/operator/pull/2019)
*   Make Pebble `Client` file methods also accept `pathlib.PurePath` in [#2097](https://github.com/canonical/operator/pull/2097)

### Fixes

*   Allow actions without params or descriptions in `ops[testing]` in [#2090](https://github.com/canonical/operator/pull/2090)
*   Ensure `ops.Pebble.pull` cleans up temporary files if it errors in [#2087](https://github.com/canonical/operator/pull/2087)
*   Make secret info description visible to the charm in `ops[testing]` in [#2115](https://github.com/canonical/operator/pull/2115)
*   Raise `ActionFailed` when using `Context` as a context manager in [#2121](https://github.com/canonical/operator/pull/2121)

### Documentation

*   Update referenced examples for managing interfaces in [#2068](https://github.com/canonical/operator/pull/2068)
*   Tidy up spelling and formatting in several places in [#2060](https://github.com/canonical/operator/pull/2060)
*   Add missing assignment to `state_out` in unit tests how-to in [#2075](https://github.com/canonical/operator/pull/2075)
*   Update the holistic/delta explanation with the reconciler pattern in [#2029](https://github.com/canonical/operator/pull/2029)
*   Fix broken setup/teardown links in README in [#2094](https://github.com/canonical/operator/pull/2094)
*   Switch to Makefile for building the docs in [#2073](https://github.com/canonical/operator/pull/2073)
*   Document how to extract the charm instance from the testing context in [#2084](https://github.com/canonical/operator/pull/2084)
*   Add a how-to guide for migrating away from Harness in [#2062](https://github.com/canonical/operator/pull/2062)
*   Rename hook tools to hook commands in [#2114](https://github.com/canonical/operator/pull/2114)
*   Remove legacy how-to guide for Harness in [#2122](https://github.com/canonical/operator/pull/2122)
*   Update the Juju release in which the metrics functionality is removed from 4.0 to 3.6.11 in [#2126](https://github.com/canonical/operator/pull/2126)
*   Clarify that `Context` is the testing context not only the Juju context in [#2123](https://github.com/canonical/operator/pull/2123)

### Refactoring

*   Use `ops.hookcmds` in `_ModelBackend` in [#2116](https://github.com/canonical/operator/pull/2116)

### CI

*   Add integration and state transition tests for the secrets API in [#2078](https://github.com/canonical/operator/pull/2078)
*   Temporarily disable tracing integration tests in [#2102](https://github.com/canonical/operator/pull/2102)
*   Add secrets tests follow-up in [#2105](https://github.com/canonical/operator/pull/2105)
*   Support monorepos in Ops charm compatibility testing in [#2100](https://github.com/canonical/operator/pull/2100)
*   Test both Charmcraft 3 and Charmcraft 4 profiles in [#2103](https://github.com/canonical/operator/pull/2103)
*   Add automated doc checks (and related starter pack updates) in [#2099](https://github.com/canonical/operator/pull/2099)

**Full Changelog**: [3.3.0...3.4.0b1](https://github.com/canonical/operator/compare/3.3.0...3.4.0b1)
```

</details>


---

<sub>⏱️ 48s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.0.0**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/releases/tag/3.0.0",
  "max_length": 15000
}
```

</details>

<details>
<summary>37 lines</summary>

```
Contents of https://github.com/canonical/operator/releases/tag/3.0.0:
[Skip to content](#start-of-content)

## Navigation Menu

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
        
    
    [View all features](https://github.com/features)
    

*   [Pricing](https://github.com/pricing)

## Provide feedback

## Saved searches

## Use saved searches to filter your results more quickly

[Sign up](/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F%3Cuser-name%3E%2F%3Crepo-name%3E%2Freleases%2Fshow&source=header-repo&source_repo=canonical%2Foperator)

*   [Notifications](/login?return_to=%2Fcanonical%2Foperator) You must be signed in to change notification settings
*   [Fork 129](/login?return_to=%2Fcanonical%2Foperator)
*   [Star 260](/login?return_to=%2Fcanonical%2Foperator)
    

1.  [Releases](/canonical/operator/releases)
2.  [3.0.0](/canonical/operator/releases/tag/3.0.0)

## Choose a tag to compare

[`5e0d22b`](/canonical/operator/commit/5e0d22b003ce42b32db66aa707b28f58da3d28d2)

This commit was created on GitHub.com and signed with GitHub’s **verified signature**.

This release removes support for Python 3.8 and Ubuntu 20.04, but is otherwise compatible with Ops 2. If you have a charm that needs to support Python 3.8, you can continue to use Ops 2, which will still receive security and critical bug fixes.

## What's Changed

### Documentation

*   Be consistent with recommending self.app and self.unit in [#1856](https://github.com/canonical/operator/pull/1856)

### CI

*   Hotfix, publish job for ops-tracing in [#1865](https://github.com/canonical/operator/pull/1865)

**Full Changelog**: [2.23.0...3.0.0](https://github.com/canonical/operator/compare/2.23.0...3.0.0)
```

</details>


---

<sub>⏱️ 48s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.1.0**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/releases/tag/3.1.0",
  "max_length": 10000
}
```

</details>

<details>
<summary>34 lines</summary>

```
Contents of https://github.com/canonical/operator/releases/tag/3.1.0:
This release exposes the app name and unit ID in the testing Context. In addition, a number of bugs are fixed, particularly ones introduced with the recent change to exposing the relation data of departed units.

## What's Changed

### Features

*   Release automation script in [#1855](https://github.com/canonical/operator/pull/1855)
*   Add app\_name and unit\_id attributes to testing.context in [#1920](https://github.com/canonical/operator/pull/1920)

### Fixes

*   If an event ends with `_Abort(0)` tests should behave as if it ended successfully in [#1887](https://github.com/canonical/operator/pull/1887)
*   If `self.app` is not actually set avoid a new crash location in [#1897](https://github.com/canonical/operator/pull/1897)
*   Only add the remote unit for departed and broken relation events, fix ordering in [#1918](https://github.com/canonical/operator/pull/1918)
*   Add the remote unit to `Relation.data` but not `Relation.units` in [#1925](https://github.com/canonical/operator/pull/1925)

### Documentation

*   Use `load_config` in the httpbin example charm in [#1852](https://github.com/canonical/operator/pull/1852)
*   Update `HACKING.md` with how to bump ops version in Charmcraft profiles in [#1872](https://github.com/canonical/operator/pull/1872)
*   Change title of docs site in [#1890](https://github.com/canonical/operator/pull/1890)
*   Use config and action classes in the Kubernetes tutorial in [#1891](https://github.com/canonical/operator/pull/1891)
*   Reference example charms from K8s tutorial and fix consistency in [#1898](https://github.com/canonical/operator/pull/1898)
*   Update style guide in [#1720](https://github.com/canonical/operator/pull/1720)
*   Fix issues in how-to guide for stored state in [#1901](https://github.com/canonical/operator/pull/1901)
*   Link out to the 12-factor tutorials from the tutorial index page in [#1902](https://github.com/canonical/operator/pull/1902)
*   Replace broken link in testing explanation in [#1913](https://github.com/canonical/operator/pull/1913)
*   Expand the storage how-to with content from juju docs scheduled for removal in [#1915](https://github.com/canonical/operator/pull/1915)
*   Ops tracing how to in [#1853](https://github.com/canonical/operator/pull/1853)
*   Add a security explanation doc in [#1904](https://github.com/canonical/operator/pull/1904)

### Tests

*   Replace Python version to 3.10 for observability charm tests in [#1914](https://github.com/canonical/operator/pull/1914)

### CI

*   Use httpbin demo charm for the `charmcraft pack` test in [#1895](https://github.com/canonical/operator/pull/1895)
*   Move TIOBE workflow to self-hosted runners in [#1912](https://github.com/canonical/operator/pull/1912)
*   Add SBOM generation and secscan workflow in [#1906](https://github.com/canonical/operator/pull/1906)
*   Build and publish in one step in [#1857](https://github.com/canonical/operator/pull/1857)
*   Update the name and email when updating the charm pins in [#1924](https://github.com/canonical/operator/pull/1924)
*   Drop smoke test against 20.04 in [#1923](https://github.com/canonical/operator/pull/1923)

**Full Changelog**: [3.0.0...3.1.0](https://github.com/canonical/operator/compare/3.0.0...3.1.0)
```

</details>


---

<sub>⏱️ 52s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.2.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/releases/tag/3.2.0"
}
```

</details>

<details>
<summary>46 lines</summary>

```
Contents of https://github.com/canonical/operator/releases/tag/3.2.0:
With this release, Ops will send security event logs to Juju's log; for example, when there is a permission error getting relation or secret data. This is logged at TRACE level, so should not be noticeable in most cases, and is intended to be used in later work rather than by charms themselves.

A typing-only change has been made to support Pebble's new `opentelemetry` log target.

On the testing front, `scenario` now supports setting the `JUJU_MACHINE_ID` variable in the mocked environment.

Over the last month, we refreshed the Ops docs landing page, moved to documentation.ubuntu.com/ops, and removed the .html suffix from pages. We expect that this will be the last big renaming for the docs for a while now.

## What's Changed

### Features

*   Add security event logging in [#1905](https://github.com/canonical/operator/pull/1905)
*   Surface JUJU\_MACHINE\_ID envvar in testing env in [#1961](https://github.com/canonical/operator/pull/1961)
*   Add a new log target type opentelemetry in [#1937](https://github.com/canonical/operator/pull/1937)

### Documentation

*   Update links and config for switch to documentation.ubuntu.com/ops in [#1940](https://github.com/canonical/operator/pull/1940)
*   Update the required Python version and note the 2.x documentation site in [#1946](https://github.com/canonical/operator/pull/1946)
*   Be consistent with recommending self.config in [#1947](https://github.com/canonical/operator/pull/1947)
*   Use latest styles from starter pack and remove .html extensions in [#1951](https://github.com/canonical/operator/pull/1951)
*   Remove .html extensions from hardcoded links in [#1955](https://github.com/canonical/operator/pull/1955)
*   Fix broken URLs in sitemap in [#1956](https://github.com/canonical/operator/pull/1956)
*   Add related doc links to homepage in [#1959](https://github.com/canonical/operator/pull/1959)
*   Use classes from ops instead of ops. in [#1968](https://github.com/canonical/operator/pull/1968)
*   Fix unstyled error pages in [#1969](https://github.com/canonical/operator/pull/1969)
*   Add Google Analyics integration and cookie consent banner in [#1971](https://github.com/canonical/operator/pull/1971)
*   Refresh docs homepage with more context about Ops in [#1964](https://github.com/canonical/operator/pull/1964)
*   Update link to Charmlibs docs in [#1985](https://github.com/canonical/operator/pull/1985)
*   Remove unnecessary pages from sitemap in [#1979](https://github.com/canonical/operator/pull/1979)
*   Update the httpbin charm to jubilant in [#1987](https://github.com/canonical/operator/pull/1987)
*   Update zero to hero to jubilant in [#1988](https://github.com/canonical/operator/pull/1988)
*   Add model-config best practice note in [#1990](https://github.com/canonical/operator/pull/1990)
*   Change some best practices to tips in [#2001](https://github.com/canonical/operator/pull/2001)
*   Add integration test for invalid config in httpbin charm in [#2002](https://github.com/canonical/operator/pull/2002)
*   Make a `Layer` instead of a `LayerDict` in the httpbin charm in [#2003](https://github.com/canonical/operator/pull/2003)
*   Update how-to to feature Jubilant (1/2) in [#2000](https://github.com/canonical/operator/pull/2000)
*   Use Charmcraft-style format and lint for example charms, not Ops-style in [#2008](https://github.com/canonical/operator/pull/2008)
*   Update broken link to HookVars source code in [#2006](https://github.com/canonical/operator/pull/2006)
*   Update how-to to feature Jubilant (2/2) in [#2004](https://github.com/canonical/operator/pull/2004)

### CI

*   Fixes for the sbom and secscan workflow, and trigger it on publishing in [#1916](https://github.com/canonical/operator/pull/1916)
*   Store the charmcraft logs if packing fails in [#1936](https://github.com/canonical/operator/pull/1936)
*   Install release dependencies for the TIOBE analysis in [#1930](https://github.com/canonical/operator/pull/1930)
*   Add Juju 4/beta to the smoke test matrix in [#1963](https://github.com/canonical/operator/pull/1963)
*   Adjust permissions block in publish workflow in [#1984](https://github.com/canonical/operator/pull/1984)
*   Update actions/checkout to v5 in [#1993](https://github.com/canonical/operator/pull/1993)
*   Enable doctests in [#1991](https://github.com/canonical/operator/pull/1991)
*   Ignore juju/4 timeouts in [#1998](https://github.com/canonical/operator/pull/1998)
*   Remove the token for SBOM and secscan on publish in [#2009](https://github.com/canonical/operator/pull/2009)
*   Speed up integration test in [#1978](https://github.com/canonical/operator/pull/1978)

**Full Changelog**: [3.1.0...3.2.0](https://github.com/canonical/operator/compare/3.1.0...3.2.0)
```

</details>


---

<sub>⏱️ 52s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.3.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/releases/tag/3.3.0"
}
```

</details>

<details>
<summary>20 lines</summary>

```
Contents of https://github.com/canonical/operator/releases/tag/3.3.0:
This is a small maintenance release that includes work on `ops` and testing internals and documentation.

## What's Changed

### Features

*   Expose the Juju hook context in ops.JujuContext in [#1996](https://github.com/canonical/operator/pull/1996)

### Fixes

*   In testing, separate relation data cache from mock Juju backend in [#2052](https://github.com/canonical/operator/pull/2052)

### Documentation

*   Use uv for testing and packing the httpbin charm in [#2011](https://github.com/canonical/operator/pull/2011)
*   Improve intro to ops.testing reference in [#2023](https://github.com/canonical/operator/pull/2023)
*   In httpbin charm integration tests, add env var for charm file to deploy in [#2018](https://github.com/canonical/operator/pull/2018)
*   Update get\_cloud\_spec doc now that credential-get works on K8s in [#2031](https://github.com/canonical/operator/pull/2031)
*   Note that arbitrary\_types\_allowed is required when ops.Secret is used in a Pydantic class in [#2038](https://github.com/canonical/operator/pull/2038)
*   Clean up Resources.fetch docstring, add ModelError exception in [#2039](https://github.com/canonical/operator/pull/2039)
*   Note that the peer databag isn't usable during the install event in [#2051](https://github.com/canonical/operator/pull/2051)
*   Fix testing code in actions how-to guide in [#2054](https://github.com/canonical/operator/pull/2054)

### CI

*   Nicer logging output in the release script using rich in [#2017](https://github.com/canonical/operator/pull/2017)
*   Clean up PYTHONPATH in tox.ini in [#2058](https://github.com/canonical/operator/pull/2058)

**Full Changelog**: [3.2.0...3.3.0](https://github.com/canonical/operator/compare/3.2.0...3.3.0)
```

</details>


---

<sub>⏱️ 1m 36s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases?q=ops-tracing**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/releases?q=ops-tracing"
}
```

</details>

<details>
<summary>93 lines</summary>

```
Contents of https://github.com/canonical/operator/releases?q=ops-tracing:
10 releases found

## 3.5.0: env var to control extension wrapping in testing

18 Dec 02:25

This is a small release with some user-facing changes to `ops.testing`.

We've added an environment variable to disable the use of `UncaughtCharmError` in testing. By default, exceptions raised from charm code are wrapped in an `UncaughtCharmError` in state-transition tests. This makes debugging harder and adds extra steps to making assertions about expected errors in tests. Set `SCENARIO_BARE_CHARM_ERRORS=true` to have exceptions be propagated to your test code as-is instead. This may become the default behaviour in a future major `ops` release. You can lock in the current default behaviour explicitly by setting `SCENARIO_BARE_CHARM_ERRORS=false` in your test runners.

Additionally, the `ops.testing.Context.charm_spec` attribute is now deprecated -- this is intended for internal use only, and was not widely used, so the warning should steer new users in the right direction.

## What's Changed

### Features

*   Env var to control exception wrapping in tests in [#2142](https://github.com/canonical/operator/pull/2142)
*   Deprecate testing.Context.charm\_spec in [#2219](https://github.com/canonical/operator/pull/2219)

### Documentation

*   Fix charmcraft init command in [#2210](https://github.com/canonical/operator/pull/2210)
*   Update CI examples to use uv and tox-uv in [#2213](https://github.com/canonical/operator/pull/2213)
*   Update and clarify info about environment prep in [#2217](https://github.com/canonical/operator/pull/2217)
*   Match Charmcraft profiles in tox.ini example for integration testing in [#2221](https://github.com/canonical/operator/pull/2221)
*   Use base 24.04 for httpbin-demo charm in [#2222](https://github.com/canonical/operator/pull/2222)
*   Clarify parts of the machine charm tutorial in [#2223](https://github.com/canonical/operator/pull/2223)
*   Match Charmcraft profiles in "Write and structure charm code" in [#2220](https://github.com/canonical/operator/pull/2220)
*   Use cosl binary in K8s tutorial charm to work around error in [#2232](https://github.com/canonical/operator/pull/2232)
*   Fix URL issues by updating doc starter pack in [#2238](https://github.com/canonical/operator/pull/2238)

### Tests

*   Don't skip tests if ops\[testing\] isn't installed in [#2215](https://github.com/canonical/operator/pull/2215)
*   Switch the integration test charms to use the uv plugin in [#2218](https://github.com/canonical/operator/pull/2218)

### CI

*   Avoid jitter in the best practice doc PRs in [#2193](https://github.com/canonical/operator/pull/2193)
*   Ignore PERF401 (manual list comprehension) across the repo in [#2201](https://github.com/canonical/operator/pull/2201)
*   The git commands need to be run in the operator directory as well in [#2197](https://github.com/canonical/operator/pull/2197)
*   Have cycle in the sbomber manifests use the default value in [#2209](https://github.com/canonical/operator/pull/2209)
*   Add pytest.warns to note an expected warning in [#2092](https://github.com/canonical/operator/pull/2092)
*   Update release script to handle non-final versions in [#2199](https://github.com/canonical/operator/pull/2199)
*   Add ops\-tracing as a dependency for the observability tests in [#2239](https://github.com/canonical/operator/pull/2239)
*   Add scheduled workflow for packing and integration testing example charms in [#2233](https://github.com/canonical/operator/pull/2233)

**Full Changelog**: [3.4.0...3.5.0](https://github.com/canonical/operator/compare/3.4.0...3.5.0)

## 3.4.0: a low-level API for the Juju hook commands

27 Nov 04:45

The main feature in this release is the introduction of `ops.hookcmds`, which provides an API to the Juju hook commands. The API is low-level, complete (other than deprecated commands), and generally a 1-1 mapping to the hook commands, but providing a Pythonic interface.

Additionally, the length of the defer queue is now logged; more arguments can be passed as paths to `ops.Container` and `ops.PebbleClient` methods; and state transition testing `Context` has gained optional availability zone and principal unit arguments.

## What's Changed

### Breaking Changes

There are breaking changes in this release. Please review them carefully:

*   Fix: Change `JujuContext.machine_id` from `int` to `str` in [#2108](https://github.com/canonical/operator/pull/2108)
    *   Note that this fix was already included in Ops 3.3.1
    *   If you use this field, you may need to adjust type hints in your code
*   Fix: Ensure that the testing context manager is exited when an exception occurs in [#2117](https://github.com/canonical/operator/pull/2117)
    *   If you use `ops.testing.Context` as a context manager and expect the charm to raise an exception, you need to adjust the expected exception type.

### Features

*   Add a low-level API for the Juju hook commands in [#2019](https://github.com/canonical/operator/pull/2019)
*   Make PebbleClient file methods also accept pathlib.PurePath in [#2097](https://github.com/canonical/operator/pull/2097)
*   Log the total number of deferred events in [#2161](https://github.com/canonical/operator/pull/2161)
*   Allow setting the Juju availability zone and principal unit in the testing Context in [#2187](https://github.com/canonical/operator/pull/2187)

### Fixes

*   Allow actions without params or descriptions in ops\[testing\] in [#2090](https://github.com/canonical/operator/pull/2090)
*   Ensure `ops.Pebble.pull` cleans up temporary files if it errors in [#2087](https://github.com/canonical/operator/pull/2087)
*   Make secret info description visible to the charm in ops\[testing\] in [#2115](https://github.com/canonical/operator/pull/2115)
*   Raise ActionFailed when using Context as a context manager in [#2121](https://github.com/canonical/operator/pull/2121)
*   Detect categories with an explanation mark indicating breaking changes in [#2132](https://github.com/canonical/operator/pull/2132)
*   Normalise Secret.owner to 'app' for ops\[testing\] output state in [#2127](https://github.com/canonical/operator/pull/2127)
*   Don't cache secret metadata in Ops in [#2143](https://github.com/canonical/operator/pull/2143)
*   Secret-info-get cannot be provided with both an ID and a label in [#2170](https://github.com/canonical/operator/pull/2170)
*   Minor hookcmds fixes in [#2175](https://github.com/canonical/operator/pull/2175)

### Documentation

*   Update referenced examples for managing interfaces in [#2068](https://github.com/canonical/operator/pull/2068)
*   Tidy up spelling and formatting in several places in [#2060](https://github.com/canonical/operator/pull/2060)
*   Add missing assignment to state\_out in unit tests how-to in [#2075](https://github.com/canonical/operator/pull/2075)
*   Update the holistic/delta explanation with the reconciler pattern in [#2029](https://github.com/canonical/operator/pull/2029)
*   Fix broken setup/teardown links in README in [#2094](https://github.com/canonical/operator/pull/2094)
*   Update info about release docs, mark testing changelog as not maintained in [#2074](https://github.com/canonical/operator/pull/2074)
*   Switch to makefile for building the docs in [#2073](https://github.com/canonical/operator/pull/2073)
*   Document how to extract the charm instance from the testing context in [#2084](https://github.com/canonical/operator/pull/2084)
*   Add a how-to guide for migrating away from Harness in [#2062](https://github.com/canonical/operator/pull/2062)
*   Rename hook tools to hook commands in [#2114](https://github.com/canonical/operator/pull/2114)
*   Remove legacy how-to guide for Harness in [#2122](https://github.com/canonical/operator/pull/2122)
*   Update the Juju release the metrics functionality is removed from 4.0 to 3.6.11 in [#2126](https://github.com/canonical/operator/pull/2126)
*   Clarify that Context is the testing context not only the Juju context in [#2123](https://github.com/canonical/operator/pull/2123)
*   Explain the Charmhub public listing process and add a reference list of best practices in [#1989](https://github.com/canonical/operator/pull/1989)
*   Expand next steps for K8s tutorial in [#2034](https://github.com/canonical/operator/pull/2034)
*   Remove mention of the `simple` Charmcraft profile in [#2138](https://github.com/canonical/operator/pull/2138)
*   Expand landing pages with summaries of pages in [#2140](https://github.com/canonical/operator/pull/2140)
*   Update environment setup for integration tests and K8s tutorial in [#2124](https://github.com/canonical/operator/pull/2124)
*   Replace machine charm tutorial by an improved tutorial in [#2119](https://github.com/canonical/operator/pull/2119)
*   Change HACKING.md instructions for maintaining Charmcraft profiles in [#2151](https://github.com/canonical/operator/pull/2151)
*   In integration tests, use consistent approach to logging and packing in [#2150](https://github.com/canonical/operator/pull/2150)
*   In integration testing how-to, clarify that Juju model is destroyed after module all tests in the module complete in [#2154](https://github.com/canonical/operator/pull/2154)
*   Remove Charmcraft channel specifier from machine charm tutorial in [#2148](https://github.com/canonical/operator/pull/2148)
*   Add AI contribution note and style guideline for type annotation of return values in [#2168](https://github.com/canonical/operator/pull/2168)
*   Add ops\[testing\] to the ops.testing docstring in [#2171](https://github.com/canonical/operator/pull/2171)
*   Add links to the Juju hook from each event class in [#2176](https://github.com/canonical/operator/pull/2176)
*   Add a short umask note in [#2184](https://github.com/canonical/operator/pull/2184)

### Tests

*   Re-enable testing consistency checks after disabling them in [#2141](https://github.com/canonical/operator/pull/2141)
*   Expand secrets integration and state transition tests in [#2130](https://github.com/canonica

<note>Content truncated. Call the fetch tool with a start_index of 10000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 35s</sub>

### ✅ `bash`

**Check full ops section in uv.lock**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && cat uv.lock | grep -A5 "name = \"ops\"" | head -40

<details>
<summary>40 lines</summary>

```
{ name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.12.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
    { name = "tenacity", version = "9.0.0", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "tenacity", version = "9.1.2", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
--
name = "ops"
version = "2.23.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "importlib-metadata", version = "8.5.0", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "importlib-metadata", version = "8.7.0", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
--
    { name = "ops" },
    { name = "pyyaml" },
]
sdist = { url = "https://files.pythonhosted.org/packages/ee/e7/1514b9c27b9364ec1d04791b0fb76d1a629c8cc73f90fbf6dd867457c914/ops_scenario-7.23.2.tar.gz", hash = "sha256:327dda8b3c871ccf16246ed4f8c7e093526af42093549976596cede58cbc8488", size = 70017, upload-time = "2026-02-11T03:58:16.553Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/01/15/3b59993cad1b2838c9bb20f6f2ed5297fcf490025b1ffecc27d06be1daba/ops_scenario-7.23.2-py3-none-any.whl", hash = "sha256:024b638e0ea94e8f2e3c642d4f96031b0c7ac4f39117b97107dc9a09503651b4", size = 64328, upload-time = "2026-02-11T03:58:14.916Z" },
--
    { name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.12.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
]

[package.optional-dependencies]
--
    { name = "ops", extra = ["testing"] },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.12.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pytest", version = "8.3.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pytest", version = "8.4.2", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version == '3.9.*'" },
    { name = "pytest", version = "9.0.1", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.10'" },
--
    { name = "ops" },
    { name = "ops", extras = ["testing"], marker = "extra == 'dev'" },
    { name = "pydantic" },
    { name = "pydantic", marker = "extra == 'dev'" },
    { name = "pytest", marker = "extra == 'dev'" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 55s</sub>

### ✅ `bash`

**Check ops section in uv.lock in detail**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && cat uv.lock | grep -A30 "^name = \"ops\"" | head -50

<details>
<summary>30 lines</summary>

```
name = "ops"
version = "2.23.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "importlib-metadata", version = "8.5.0", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "importlib-metadata", version = "8.7.0", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "opentelemetry-api", version = "1.33.1", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "opentelemetry-api", version = "1.37.0", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
    { name = "websocket-client" },
]
sdist = { url = "https://files.pythonhosted.org/packages/93/98/84789a5e15ad76e043301bbd70b4d39cffaa717ae6eecb662fd0dd0cc7af/ops-2.23.2.tar.gz", hash = "sha256:a69b0c5bc65ebd91720fc96459e81b969df851f3a6c9c855ee73de7004205987", size = 528074, upload-time = "2026-02-11T03:58:15.565Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/e0/00/65da7c96d0f9e13c4de3bdd2e3717259fe723ff4bd4e5dc714164f851032/ops-2.23.2-py3-none-any.whl", hash = "sha256:9cab0c6bc46eeff2e96777128200c3ef872b55641b12f07dc4fd6fe3103954be", size = 188415, upload-time = "2026-02-11T03:58:13.693Z" },
]

[package.optional-dependencies]
testing = [
    { name = "ops-scenario" },
]

[[package]]
name = "ops-scenario"
version = "7.23.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "ops" },
    { name = "pyyaml" },
]
sdist = { url = "https://files.pythonhosted.org/packages/ee/e7/1514b9c27b9364ec1d04791b0fb76d1a629c8cc73f90fbf6dd867457c914/ops_scenario-7.23.2.tar.gz", hash = "sha256:327dda8b3c871ccf16246ed4f8c7e093526af42093549976596cede58cbc8488", size = 70017, upload-time = "2026-02-11T03:58:16.553Z" }
wheels = [
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 56s</sub>

### ✅ `bash`

**Check installed ops and ops-scenario**

$ pip show ops-scenario 2>/dev/null | grep -E "^(Name|Version)" && pip show ops 2>/dev/null | grep -E "^(Name|Version|Requires)"

<details>
<summary>6 lines</summary>

```
Name: ops-scenario
Version: 8.7.0
Name: ops
Version: 3.7.0
Requires: opentelemetry-api, PyYAML, websocket-client
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 6s</sub>

### ✅ `bash`

**Check ops-tracing version**

$ pip show ops-tracing 2>/dev/null | grep -E "^(Name|Version)" && pip index versions ops-tracing 2>/dev/null | head -5

<details>
<summary>7 lines</summary>

```
Name: ops-tracing
Version: 3.7.0
ops-tracing (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 0.9.6, 0.9.4, 0.9.3, 0.9.2, 0.9.1, 0.9.0
  INSTALLED: 3.7.0
  LATEST:    3.7.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 6s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases?q=tracing**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/releases?q=tracing"
}
```

</details>

<details>
<summary>93 lines</summary>

```
Contents of https://github.com/canonical/operator/releases?q=tracing:
10 releases found

## 3.5.0: env var to control extension wrapping in testing

18 Dec 02:25

This is a small release with some user-facing changes to `ops.testing`.

We've added an environment variable to disable the use of `UncaughtCharmError` in testing. By default, exceptions raised from charm code are wrapped in an `UncaughtCharmError` in state-transition tests. This makes debugging harder and adds extra steps to making assertions about expected errors in tests. Set `SCENARIO_BARE_CHARM_ERRORS=true` to have exceptions be propagated to your test code as-is instead. This may become the default behaviour in a future major `ops` release. You can lock in the current default behaviour explicitly by setting `SCENARIO_BARE_CHARM_ERRORS=false` in your test runners.

Additionally, the `ops.testing.Context.charm_spec` attribute is now deprecated -- this is intended for internal use only, and was not widely used, so the warning should steer new users in the right direction.

## What's Changed

### Features

*   Env var to control exception wrapping in tests in [#2142](https://github.com/canonical/operator/pull/2142)
*   Deprecate testing.Context.charm\_spec in [#2219](https://github.com/canonical/operator/pull/2219)

### Documentation

*   Fix charmcraft init command in [#2210](https://github.com/canonical/operator/pull/2210)
*   Update CI examples to use uv and tox-uv in [#2213](https://github.com/canonical/operator/pull/2213)
*   Update and clarify info about environment prep in [#2217](https://github.com/canonical/operator/pull/2217)
*   Match Charmcraft profiles in tox.ini example for integration testing in [#2221](https://github.com/canonical/operator/pull/2221)
*   Use base 24.04 for httpbin-demo charm in [#2222](https://github.com/canonical/operator/pull/2222)
*   Clarify parts of the machine charm tutorial in [#2223](https://github.com/canonical/operator/pull/2223)
*   Match Charmcraft profiles in "Write and structure charm code" in [#2220](https://github.com/canonical/operator/pull/2220)
*   Use cosl binary in K8s tutorial charm to work around error in [#2232](https://github.com/canonical/operator/pull/2232)
*   Fix URL issues by updating doc starter pack in [#2238](https://github.com/canonical/operator/pull/2238)

### Tests

*   Don't skip tests if ops\[testing\] isn't installed in [#2215](https://github.com/canonical/operator/pull/2215)
*   Switch the integration test charms to use the uv plugin in [#2218](https://github.com/canonical/operator/pull/2218)

### CI

*   Avoid jitter in the best practice doc PRs in [#2193](https://github.com/canonical/operator/pull/2193)
*   Ignore PERF401 (manual list comprehension) across the repo in [#2201](https://github.com/canonical/operator/pull/2201)
*   The git commands need to be run in the operator directory as well in [#2197](https://github.com/canonical/operator/pull/2197)
*   Have cycle in the sbomber manifests use the default value in [#2209](https://github.com/canonical/operator/pull/2209)
*   Add pytest.warns to note an expected warning in [#2092](https://github.com/canonical/operator/pull/2092)
*   Update release script to handle non-final versions in [#2199](https://github.com/canonical/operator/pull/2199)
*   Add ops-tracing as a dependency for the observability tests in [#2239](https://github.com/canonical/operator/pull/2239)
*   Add scheduled workflow for packing and integration testing example charms in [#2233](https://github.com/canonical/operator/pull/2233)

**Full Changelog**: [3.4.0...3.5.0](https://github.com/canonical/operator/compare/3.4.0...3.5.0)

## 3.4.0: a low-level API for the Juju hook commands

27 Nov 04:45

The main feature in this release is the introduction of `ops.hookcmds`, which provides an API to the Juju hook commands. The API is low-level, complete (other than deprecated commands), and generally a 1-1 mapping to the hook commands, but providing a Pythonic interface.

Additionally, the length of the defer queue is now logged; more arguments can be passed as paths to `ops.Container` and `ops.PebbleClient` methods; and state transition testing `Context` has gained optional availability zone and principal unit arguments.

## What's Changed

### Breaking Changes

There are breaking changes in this release. Please review them carefully:

*   Fix: Change `JujuContext.machine_id` from `int` to `str` in [#2108](https://github.com/canonical/operator/pull/2108)
    *   Note that this fix was already included in Ops 3.3.1
    *   If you use this field, you may need to adjust type hints in your code
*   Fix: Ensure that the testing context manager is exited when an exception occurs in [#2117](https://github.com/canonical/operator/pull/2117)
    *   If you use `ops.testing.Context` as a context manager and expect the charm to raise an exception, you need to adjust the expected exception type.

### Features

*   Add a low-level API for the Juju hook commands in [#2019](https://github.com/canonical/operator/pull/2019)
*   Make PebbleClient file methods also accept pathlib.PurePath in [#2097](https://github.com/canonical/operator/pull/2097)
*   Log the total number of deferred events in [#2161](https://github.com/canonical/operator/pull/2161)
*   Allow setting the Juju availability zone and principal unit in the testing Context in [#2187](https://github.com/canonical/operator/pull/2187)

### Fixes

*   Allow actions without params or descriptions in ops\[testing\] in [#2090](https://github.com/canonical/operator/pull/2090)
*   Ensure `ops.Pebble.pull` cleans up temporary files if it errors in [#2087](https://github.com/canonical/operator/pull/2087)
*   Make secret info description visible to the charm in ops\[testing\] in [#2115](https://github.com/canonical/operator/pull/2115)
*   Raise ActionFailed when using Context as a context manager in [#2121](https://github.com/canonical/operator/pull/2121)
*   Detect categories with an explanation mark indicating breaking changes in [#2132](https://github.com/canonical/operator/pull/2132)
*   Normalise Secret.owner to 'app' for ops\[testing\] output state in [#2127](https://github.com/canonical/operator/pull/2127)
*   Don't cache secret metadata in Ops in [#2143](https://github.com/canonical/operator/pull/2143)
*   Secret-info-get cannot be provided with both an ID and a label in [#2170](https://github.com/canonical/operator/pull/2170)
*   Minor hookcmds fixes in [#2175](https://github.com/canonical/operator/pull/2175)

### Documentation

*   Update referenced examples for managing interfaces in [#2068](https://github.com/canonical/operator/pull/2068)
*   Tidy up spelling and formatting in several places in [#2060](https://github.com/canonical/operator/pull/2060)
*   Add missing assignment to state\_out in unit tests how-to in [#2075](https://github.com/canonical/operator/pull/2075)
*   Update the holistic/delta explanation with the reconciler pattern in [#2029](https://github.com/canonical/operator/pull/2029)
*   Fix broken setup/teardown links in README in [#2094](https://github.com/canonical/operator/pull/2094)
*   Update info about release docs, mark testing changelog as not maintained in [#2074](https://github.com/canonical/operator/pull/2074)
*   Switch to makefile for building the docs in [#2073](https://github.com/canonical/operator/pull/2073)
*   Document how to extract the charm instance from the testing context in [#2084](https://github.com/canonical/operator/pull/2084)
*   Add a how-to guide for migrating away from Harness in [#2062](https://github.com/canonical/operator/pull/2062)
*   Rename hook tools to hook commands in [#2114](https://github.com/canonical/operator/pull/2114)
*   Remove legacy how-to guide for Harness in [#2122](https://github.com/canonical/operator/pull/2122)
*   Update the Juju release the metrics functionality is removed from 4.0 to 3.6.11 in [#2126](https://github.com/canonical/operator/pull/2126)
*   Clarify that Context is the testing context not only the Juju context in [#2123](https://github.com/canonical/operator/pull/2123)
*   Explain the Charmhub public listing process and add a reference list of best practices in [#1989](https://github.com/canonical/operator/pull/1989)
*   Expand next steps for K8s tutorial in [#2034](https://github.com/canonical/operator/pull/2034)
*   Remove mention of the `simple` Charmcraft profile in [#2138](https://github.com/canonical/operator/pull/2138)
*   Expand landing pages with summaries of pages in [#2140](https://github.com/canonical/operator/pull/2140)
*   Update environment setup for integration tests and K8s tutorial in [#2124](https://github.com/canonical/operator/pull/2124)
*   Replace machine charm tutorial by an improved tutorial in [#2119](https://github.com/canonical/operator/pull/2119)
*   Change HACKING.md instructions for maintaining Charmcraft profiles in [#2151](https://github.com/canonical/operator/pull/2151)
*   In integration tests, use consistent approach to logging and packing in [#2150](https://github.com/canonical/operator/pull/2150)
*   In integration testing how-to, clarify that Juju model is destroyed after module all tests in the module complete in [#2154](https://github.com/canonical/operator/pull/2154)
*   Remove Charmcraft channel specifier from machine charm tutorial in [#2148](https://github.com/canonical/operator/pull/2148)
*   Add AI contribution note and style guideline for type annotation of return values in [#2168](https://github.com/canonical/operator/pull/2168)
*   Add ops\[testing\] to the ops.testing docstring in [#2171](https://github.com/canonical/operator/pull/2171)
*   Add links to the Juju hook from each event class in [#2176](https://github.com/canonical/operator/pull/2176)
*   Add a short umask note in [#2184](https://github.com/canonical/operator/pull/2184)

### Tests

*   Re-enable testing consistency checks after disabling them in [#2141](https://github.com/canonical/operator/pull/2141)
*   Expand secrets integration and state transition tests in [#2130](https://github.com/canonical

<note>Content truncated. Call the fetch tool with a start_index of 10000 to get more content.</note>
```

</details>


---

<sub>⏱️ 2m 15s</sub>

### ✅ `web_fetch`

**https://pypi.org/pypi/ops-tracing/json**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://pypi.org/pypi/ops-tracing/json"
}
```

</details>

```
Content type application/json cannot be simplified to markdown. Here is the raw content:
Contents of https://pypi.org/pypi/ops-tracing/json:
{"info":{"author":"The Charm Tech team at Canonical Ltd.","author_email":null,"bugtrack_url":null,"classifiers":["Development Status :: 5 - Production/Stable","Framework :: OpenTelemetry","Intended Audience :: Developers","Intended Audience :: System Administrators","Natural Language :: English","Operating System :: MacOS :: MacOS X","Operating System :: POSIX :: Linux","Programming Language :: Python","Programming Language :: Python :: 3","Programming Language :: Python :: 3 :: Only","Programming Language :: Python :: 3.10","Programming Language :: Python :: 3.11","Programming Language :: Python :: 3.12","Programming Language :: Python :: 3.13","Programming Language :: Python :: 3.14","Programming Language :: Python :: Implementation :: CPython","Programming Language :: Python :: Implementation :: PyPy","Topic :: Software Development :: Libraries"],"description":"# ops-tracing\n\n**First-party OpenTelemetry integration for the [Ops](https://pypi.org/project/ops/) library.**\nThis package adds tracing capabilities to Ops, enabling you to observe the performance of your applications.\n\n---\n\n## Overview\n\n- Seamless integration with [ops](https://pypi.org/project/ops/)\n- Built on OpenTelemetry\n- Enables tracing of your charm code\n\nPlease add `ops[tracing]` to your charm's dependencies, rather than this package directly.\n\n---\n\n## Documentation\n\nComprehensive documentation for the Ops library, including the tracing feature, is available at:\n[Ops documentation](https://documentation.ubuntu.com/ops/latest/).\n\nYou’ll find setup instructions, usage examples, and best practices for leveraging the tracing functionality.\n\n---\n\n## Community and Support\n\n- **Matrix Chat**: [Charm Tech](https://matrix.to/#/#charmhub-ops:ubuntu.com)\n- **Forum**: [Charmhub - Discuss Python operator development](https://discourse.charmhub.io/)\n- **Issue Tracker**: See [GitHub issues](https://github.com/canonical/ops/issues)\n- **Further Links**: See the [ops PyPI page](https://pypi.org/project/ops/)\n\nFeedback, contributions, and bug reports are always welcome.\nPlease follow the guidelines in the [main repository](https://github.com/canonical/ops/)\nfor the Ops library.\n\n---\n\n## License\n\nThis project is licensed under the same license as `ops`.\nRefer to the `ops` repository for full details.\n\n---\n\nHappy tracing!\n","description_content_type":"text/markdown","docs_url":null,"download_url":null,"downloads":{"last_day":-1,"last_month":-1,"last_week":-1},"dynamic":null,"home_page":null,"keywords":null,"license":null,"license_expression":"Apache-2.0","license_files":null,"maintainer":null,"maintainer_email":null,"name":"ops-tracing","package_url":"https://pypi.org/project/ops-tracing/","platform":null,"project_url":"https://pypi.org/project/ops-tracing/","project_urls":{"Changelog":"https://github.com/canonical/operator/blob/main/CHANGES.md","Documentation":"https://documentation.ubuntu.com/ops/latest/","Issues":"https://github.com/canonical/operator/issues","Repository":"https://github.com/canonical/operator"},"provides_extra":null,"release_url":"https://pypi.org/project/ops-tracing/3.7.0/","requires_dist":["opentelemetry-api~=1.0","opentelemetry-sdk~=1.30","ops==3.7.0","pydantic"],"requires_python":">=3.10","summary":"The tracing facility for the Ops library.","version":"3.7.0","yanked":false,"yanked_reason":null},"last_serial":35607421,"ownership":{"organization":null,"roles":[{"role":"Owner","user":"benhoyt"},{"role":"Owner","user":"dimaqq"},{"role":"Owner","user":"tonyandrewmeyer"}]},"releases":{"0.9.0":[{"comment_text":null,"digests":{"blake2b_256":"f3305281bb0f4ce105df8fe68ab68d5c4452e7044eb9a42d1cc555ac38667478","md5":"6305191cebb2a01ea1dec92f74589028","sha256":"59c537ec7210257976c1efb1dd5fe0b8bb45b3181829f618b5d234f47285039c"},"downloads":-1,"filename":"ops_tracing-0.9.0-py3-none-any.whl","has_sig":false,"md5_digest":"6305191cebb2a01ea1dec92f74589028","packagetype":"bdist_wheel","python_version":"py3","requires_python":">=3.8","size":29753,"upload_time":"2025-03-12T12:25:49","upload_time_iso_8601":"2025-03-12T12:25:49.470085Z","url":"https://files.pythonhosted.org/packages/f3/30/5281bb0f4ce105df8fe68ab68d5c4452e7044eb9a42d1cc555ac38667478/ops_tracing-0.9.0-py3-none-any.whl","yanked":false,"yanked_reason":null},{"comment_text":null,"digests":{"blake2b_256":"811252bbbe33c10ed9fb89cd7bd45c348df1c3c88b4e2ee2cca6642f5ba6ab55","md5":"b48ce607c43ccb229c7dcf2156eeb3f9","sha256":"b2bd18e889b0cd4e30f2b7e52c7ba8dd5146d68f9bf3907d65018792545ef5ea"},"downloads":-1,"filename":"ops_tracing-0.9.0.tar.gz","has_sig":false,"md5_digest":"b48ce607c43ccb229c7dcf2156eeb3f9","packagetype":"sdist","python_version":"source","requires_python":">=3.8","size":23189,"upload_time":"2025-03-12T12:25:51","upload_time_iso_8601":"2025-03-12T12:25:51.149624Z","url":"https://files.pythonhosted.org/packages/81/12/52bbbe33c10ed9fb89cd7bd45c348df1c3c88b4e2ee2cca6642f5ba6ab55/ops_tracing-0.9.0.tar.gz","yanked":false,"yanked_reason":null}],"0.9.1":[{"comment_text":null,"digests":{"blake2b_256":"fb6fe0c298f364539f0dac7242bf8cd8f5fea931f4b2b1fd371d93a630b949a1","md5":"c47d11668fe100dd49ffbad5ea3445d1","sha256":"8a54e14bbd91a85abe13ad8c26adb6a67fd6c9e73673848ef7e5d8b5139c55d4"},"downloads":-1,"filename":"ops_tracing-0.9.1-py3-none-any.whl","has_sig":false,"md5_digest":"c47d11668fe100dd49ffbad5ea3445d1","packagetype":"bdist_wheel","python_version":"py3","requires_python":">=3.8","size":30655,"upload_time":"2025-03-13T04:33:06","upload_time_iso_8601":"2025-03-13T04:33:06.020204Z","url":"https://files.pythonhosted.org/packages/fb/6f/e0c298f364539f0dac7242bf8cd8f5fea931f4b2b1fd371d93a630b949a1/ops_tracing-0.9.1-py3-none-any.whl","yanked":false,"yanked_reason":null},{"comment_text":null,"digests":{"blake2b_256":"56bbd23322ba7ed836bbb9f7e5c9287c62f50c644b67726602ac2c516699a6b2","md5":"9436e66157c8dbfeac4b90cf8e215779","sha256":"9ebe4dc8bdaaf3d51432ea43356c7a23a8f1e7d6e9bfd8ea8956775313ab2580"},"downloads":-1,"filename":"ops_tracing-0.9.1.tar.gz","has_sig":false,"md5_digest":"9436e66157c8dbfeac4b90cf8e215779","packagetype":"sdist","python_version":"source","requires_python":">=3.8","size":24008,"upload_time":"2025-03-13T04:33:07","upload_time_iso_8601":"2025-03-13T04:33:07.495088Z","url":"https://files.pythonhosted.org/packages/56/bb/d23322ba7ed836bbb9f7e5c9287c62f50c644b67726602ac2c516699a6b2/ops_tracing-0.9.1.tar.gz","yanked":false,"yanked_reason":null}],"0.9.2":[{"comment_text":null,"digests":{"blake2b_256":"26dd05e6c321e9342a5b37feac25f34dc2813793e09a108c31a7b6d5bfdef0f1","md5":"b89c7568fa3c427bbc0d3a0448064930","sha256":"736f9e1d1661622cb0ad59222dd57d4bc223b6eb6254cb9d8625a6d7674fc45e"},"downloads":-1,"filename":"ops_tracing-0.9.2-py3-none-any.whl","has_sig":false,"md5_digest":"b89c7568fa3c427bbc0d3a0448064930","packagetype":"bdist_wheel","python_version":"py3","requires_python":">=3.8","size":30815,"upload_time":"2025-03-13T05:31:30","upload_time_iso_8601":"2025-03-13T05:31:30.754366Z","url":"https://files.pythonhosted.org/packages/26/dd/05e6c321e9342a5b37feac25f34dc2813793e09a108c31a7b6d5bfdef0f1/ops_tracing-0.9.2-py3-none-any.whl","yanked":false,"yanked_reason":null},{"comment_text":null,"digests":{"blake2b_256":"ddd8506e90d3339dacd04b00fd6e11eb8e6b531d282d667fe7c197f232eef481","md5":"f904c426e15b00b5bf300c433c462748","sha256":"6932008968779aaef3c55caf360a0c221041b3ae1547d207ef5f6036358ed5d3"},"downloads":-1,"filename":"ops_tracing-0.9.2.tar.gz","has_sig":false,"md5_digest":"f904c426e15b00b5bf300c433c462748","packagetype":"sdist","python_version":"source","requires_python":">=3.8","size":24092,"upload_time":"2025-03-13T05:31:32","upload_time_iso_8601":"2025-03-13T05:31:32.316655Z","url":"https://files.pythonhosted.org/packages/dd/d8/506e90d3339dacd04b00fd6e11eb8e6b531d282d667fe7c197f232eef481/ops_tracing-0.9.2.tar.gz","yanked":false,"yanked_reason":null}],"0.9.3":[{"comment_text":null,"digests":{"blake2b_256":"701be82512f6eec16da891b3cc632691f500955c245e6023f156820fb97e5376","md5":"b1a3e0ad200ba5aa8cb182dba9d561c7","sha256":"0cfadbabbfabffbefbe0d29ecb681a2900d00054c9fae9a64e0344726d865060"},"downloads":-1,"filename":"ops_tracing-0.9.3-py3-none-any.whl","has_sig":false,"md5_digest":"b1a3e0ad200ba5aa8cb182dba9d561c7","packagetype":"bdist_wheel","python_version":"py3","requires_python":">=3.8","size":30814,"upload_time":"2025-03-13T06:55:22","upload_time_iso_8601":"2025-03-13T06:55:22.671607Z","url":"https://files.pythonhosted.org/packages/70/1b/e82512f6eec16da891b3cc632691f500955c245e6023f156820fb97e5376/ops_tracing-0.9.3-py3-none-any.whl","yanked":false,"yanked_reason":null},{"comment_text":null,"digests":{"blake2b_256":"794be38ebf05483118a7403f7b467de7a1f2097f0fbec18f9e63f5b97022993d","md5":"8e2e4192e7f44062afda394d9ffe0ec3","sha256":"36e253c1c0b240a9ded564404d406811a93f9733374626654c150da3acc8469a"},"downloads":-1,"filename":"ops_tracing-0.9.3.tar.gz","has_sig":false,"md5_digest":"8e2e4192e7f44062afda394d9ffe0ec3","packagetype":"sdist","python_version":"source","requires_python":">=3.8","size":26015,"upload_time":"2025-03-13T06:55:24","upload_time_iso_8601":"2025-03-13T06:55:24.103580Z","url":"https://files.pythonhosted.org/packages/79/4b/e38ebf05483118a7403f7b467de7a1f2097f0fbec18f9e63f5b97022993d/ops_tracing-0.9.3.tar.gz","yanked":false,"yanked_reason":null}],"0.9.4":[{"comment_text":null,"digests":{"blake2b_256":"0293c4d3cd3dd008b164180ca94b71f13a98faec80da350887eb21e8cf7254e1","md5":"0df3b35e3a018d056a58a9206a124ef9","sha256":"969dbdf02726ffd8e5ea09f1305b3fc98a39e247b47765aa735557cca3839a2d"},"downloads":-1,"filename":"ops_tracing-0.9.4-py3-none-any.whl","has_sig":false,"md5_digest":"0df3b35e3a018d056a58a9206a124ef9","packagetype":"bdist_wheel","python_version":"py3","requires_python":">=3.8","size":30781,"upload_time":"2025-03-14T01:46:15","upload_time_iso_8601":"2025-03-14T01:46:15.627977Z","url":"https://files.pythonhosted.org/packages/02/93/c4d3cd3dd008b164180ca94b71f13a98faec80da350887eb21e8cf7254e1/ops_tracing-0.9.4-py3-none-any.whl"

<note>Content truncated. Call the fetch tool with a start_index of 10000 to get more content.</note>
```


---

<sub>⏱️ 2m 15s</sub>

### ✅ `bash`

**Check if charm uses ops-tracing**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && grep -r "tracing\|ops_tracing\|ops-tracing" . --include="*.py" --include="*.yaml" --include="*.toml" -l 2>/dev/null

```

<exited with exit code 1>
```


---

<sub>⏱️ 3m 4s</sub>

### 💬 Copilot

Now I have a full picture. Let me check the current test status and look at pebble.Layer equality behavior:

---

<sub>⏱️ 3m 4s</sub>

### ✅ `bash`

**Test pebble.Layer equality with dict**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && python3 -c "import ops.pebble as p; l = p.Layer({'services': {'a': {'command': 'foo', 'override': 'replace', 'summary': 'a'}}}); print(type(l)); print(l == {'services': {'a': {'command': 'foo', 'override': 'replace', 'summary': 'a'}}})"

```
<class 'ops.pebble.Layer'>
True
<exited with exit code 0>
```


---

<sub>⏱️ 3m 4s</sub>

### ✅ `bash`

**Check how Container.layers works in ops.testing**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && python3 -c "import ops.testing as t; import inspect; print(inspect.getsource(t.Container))" 2>/dev/null | grep -A10 "layers" | head -30

<details>
<summary>28 lines</summary>

```
# This is the base plan. On top of it, one can add layers.
    # We need to model pebble in this way because it's impossible to retrieve the layers from
    # pebble or derive them from the resulting plan (which one CAN get from pebble).
    # So if we are instantiating Container by fetching info from a 'live' charm, the 'layers'
    # will be unknown. all that we can know is the resulting plan (the 'computed plan').
    _base_plan: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    # We expect most of the user-facing testing to be covered by this 'layers' attribute,
    # as it is all that will be known when unit-testing.
    layers: Mapping[str, pebble.Layer] = dataclasses.field(default_factory=dict)
    """All :class:`ops.pebble.Layer` definitions that have already been added to the container.

    Note that the layers should be added to the dictionary in the order in which they would have
    been added to Pebble. For layers loaded on Pebble start from the filesystem, this means adding
    them to the dictionary in alphabetical order by filename. For layers loaded via the Pebble API,
    this means adding them in the order of the API calls.
    """

    service_statuses: Mapping[str, pebble.ServiceStatus] = dataclasses.field(
        default_factory=dict,
    )
    """The current status of each Pebble service running in the container."""

    mounts: Mapping[str, Mount] = dataclasses.field(default_factory=dict)
    """Provides access to the contents of the simulated container filesystem.
--
        for layer in self.layers.values():
            for name, service in layer.services.items():
                if name in services and service.override == 'merge':
                    # Safe: _merge only mutates the target (already a copy), not the source.
                    services[name]._merge(service)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 30s</sub>

### ✅ `bash`

**Read conftest.py**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && cat tests/conftest.py && echo "---" && cat tests/unit/test_charm.py | head -10

<details>
<summary>15 lines</summary>

```
from _pytest.config.argparsing import Parser


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--charm-path",
        help="Pre-built charm file to deploy, rather than building from source",
    )
---
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import PropertyMock, patch

import pytest
from ops.pebble import ServiceStatus
from ops.testing import ActiveStatus, Container, Context, PeerRelation, Secret, State, TCPPort

from charm import ZincCharm
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 30s</sub>

### ✅ `bash`

**Check git status**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && git log --oneline -5 && git status

<details>
<summary>8 lines</summary>

```
d3bb738 (HEAD) test: update ip fetching for zinc units in bash tests
7415bc1 test: use `jubilant` in place of `juju wait-for`
b4d4a3e ci: cache wheels in the integration test phase
b856e4c build(deps): bump ops from 2.23.1 to 2.23.2 (#400)
a7fcce8 build(deps): bump ruff from 0.14.14 to 0.15.4 in the uv-deps group (#399)
HEAD detached at d3bb738
nothing to commit, working tree clean
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 49s</sub>

### 💬 Copilot

Now I have all the information I need. Let me create the upgrade branch and implement the changes:

---

<sub>⏱️ 3m 50s</sub>

### ✅ `bash`

**Create upgrade branch**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && git checkout -b ops-3.7.0-upgrade

```
Switched to a new branch 'ops-3.7.0-upgrade'
<exited with exit code 0>
```


---

<sub>⏱️ 3m 57s</sub>

### 💬 Copilot

Now let me make all the code changes:

---

<sub>⏱️ 3m 57s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 3m 57s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 4m 11s</sub>

### ✅ `bash`

**Check pytest-env availability**

$ python3 -c "import pytest; print(pytest.__version__)" && python3 -c "import pytest_env; print('pytest-env available')" 2>/dev/null || echo "pytest-env not available"

```
9.0.2
pytest-env not available
<exited with exit code 0>
```


---

<sub>⏱️ 4m 30s</sub>

### 💬 Copilot

`pytest-env` isn't available, so the `env` key won't work natively. Let me fix that and use `conftest.py` instead:

---

<sub>⏱️ 4m 30s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 4m 36s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests/conftest.py.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests/conftest.py

<details>
<summary>9 lines</summary>

```
1. from _pytest.config.argparsing import Parser
2. 
3. 
4. def pytest_addoption(parser: Parser):
5.     parser.addoption(
6.         "--charm-path",
7.         help="Pre-built charm file to deploy, rather than building from source",
8.     )
9.
```

</details>


---

<sub>⏱️ 4m 43s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests/conftest.py.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests/conftest.py

```
File /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests/conftest.py updated with changes.
```


---

<sub>⏱️ 4m 52s</sub>

### 💬 Copilot

Now update `zinc.py` to use `ops.pebble.Layer` instead of a plain dict:

---

<sub>⏱️ 4m 52s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py

```
File /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py updated with changes.
```


---

<sub>⏱️ 4m 52s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py

```
File /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py updated with changes.
```


---

<sub>⏱️ 4m 52s</sub>

### ❌ `edit`

**edit the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py

```
No match found
```


---

<sub>⏱️ 4m 57s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py

<details>
<summary>86 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2024 Jon Seager (@jnsgruk)
3. # See LICENSE file for licensing details.
4. 
5. """Assist with client interactions with Zinc."""
6. 
7. import json
8. import logging
9. import time
10. import urllib.request
11. 
12. import ops
13. 
14. logger = logging.getLogger(__name__)
15. 
16. 
17. class Zinc:
18.     """Represent a Zinc instance in the workload."""
19. 
20.     _port = 4080
21.     _log_path = "/var/lib/zincsearch/zinc.log"
22.     _log_dir = "/var/lib/zincsearch"
23. 
24.     def pebble_layer(self, initial_password) -> ops.pebble.Layer:
25.         """Return a Pebble layer for managing Zinc."""
26.         return ops.pebble.Layer({
27.             "services": {
28.                 "zinc": {
29.                     "override": "replace",
30.                     "summary": "zinc",
31.                     # go-runner achieves the equivalent of:`bash -c '/bin/zinc | tee PATH'`, but
32.                     # without including bash etc. in the image.
33.                     "command": f"/bin/go-runner --log-file={self.log_path} --also-stdout=true --redirect-stderr=true /bin/zincsearch",
34.                     "startup": "enabled",
35.                     "environment": {
36.                         "ZINC_DATA_PATH": "/var/lib/zincsearch",
37.                         "ZINC_FIRST_ADMIN_USER": "admin",
38.                         "ZINC_FIRST_ADMIN_PASSWORD": initial_password,
39.                         "ZINC_PROMETHEUS_ENABLE": True,
40.                         "ZINC_TELEMETRY": False,
41.                         "ZINC_PROFILER": True,
42.                     },
43.                 }
44.             },
45.         }
46. 
47.     @property
48.     def log_path(self) -> str:
49.         """Report the path that Zinc is configured to output logs."""
50.         return self._log_path
51. 
52.     @property
53.     def log_dir(self) -> str:
54.         """Report the directory that Zinc is configured to output logs."""
55.         return self._log_dir
56. 
57.     @property
58.     def port(self) -> int:
59.         """Report the TCP port that Zinc is bound to."""
60.         return self._port
61. 
62.     @property
63.     def version(self) -> str:
64.         """Reports the current Zinc version."""
65.         try:
66.             return self._request_version()
67.         # Catching Exception is not ideal, but we don't care much for the error here, and just
68.         # default to setting a blank version since there isn't much the admin can do!
69.         except Exception as e:
70.             logger.warning("unable to get version from API: %s", str(e))
71.             logger.debug(e, exc_info=True)
72.             return ""
73. 
74.     def _request_version(self) -> str:
75.         """Fetch the version from the running workload using the Zinc API."""
76.         retries = 0
77.         while True:
78.             try:
79.                 res = urllib.request.urlopen(f"http://localhost:{self._port}/version")
80.                 return json.loads(res.read().decode())["version"]
81.             except Exception:
82.                 if retries == 3:
83.                     raise
84.                 retries += 1
85.                 time.sleep(3)
86.
```

</details>


---

<sub>⏱️ 5m 7s</sub>

### 💬 Copilot

The Layer constructor call is missing the closing `)`. Let me fix it:

---

<sub>⏱️ 5m 7s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py

```
File /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src/zinc.py updated with changes.
```


---

<sub>⏱️ 5m 12s</sub>

### 💬 Copilot

Now update the lock file to upgrade ops to 3.7.0:

---

<sub>⏱️ 5m 13s</sub>

### ✅ `bash`

**Upgrade ops in lock file**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && uv lock --upgrade-package ops 2>&1

<details>
<summary>23 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0/0⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠙ zinc-k8s-operator==0.1.0                                                                                              ⠙ zinc-k8s-operator==0.1.0                                                                                              ⠙ cosl==1.4.0                                                                                                           ⠙ jsonschema==4.25.1                                                                                                    ⠙ ops==3.7.0                                                                                                            ⠙ ops==3.7.0                                                                                                            ⠙ ops-scenario==8.7.0                                                                                                   ⠙ pydantic==2.12.5                                                                                                      ⠹ pydantic==2.12.5                                                                                                      ⠹ pydantic-core==2.41.5                                                                                                 ⠹ coverage==7.10.7                                                                                                      ⠹ coverage==7.10.7                                                                                                      ⠹ jubilant==1.7.0                                                                                                       ⠹ pytest==9.0.1                                                                                                         ⠹ ruff==0.15.4                                                                                                          ⠹ pyyaml==6.0.3                                                                                                         ⠹ tenacity==9.1.2                                                                                                       ⠹ typing-extensions==4.15.0                                                                                             ⠹ attrs==25.3.0                                                                                                         ⠹ jsonschema-specifications==2025.9.1                                                                                   ⠹ referencing==0.36.2                                                                                                   ⠹ typing-extensions==4.15.0                                                                                             ⠹ rpds-py==0.27.1                                                                                                       ⠹ colorama==0.4.6                                                                                                       Resolved 31 packages in 345ms
Updated coverage v7.6.1, v7.10.7 -> v7.10.7
Removed deprecated v1.2.18
Updated importlib-metadata v8.5.0, v8.7.0 -> v8.7.0
Removed importlib-resources v6.4.5
Updated jsonschema v4.23.0, v4.25.1 -> v4.25.1
Updated jsonschema-specifications v2023.12.1, v2025.9.1 -> v2025.9.1
Updated opentelemetry-api v1.33.1, v1.37.0 -> v1.37.0
Updated ops v2.23.2 -> v3.7.0
Updated ops-scenario v7.23.2 -> v8.7.0
Removed pkgutil-resolve-name v1.3.10
Updated pluggy v1.5.0, v1.6.0 -> v1.6.0
Updated pydantic v2.10.6, v2.12.5 -> v2.12.5
Updated pydantic-core v2.27.2, v2.41.5 -> v2.41.5
Updated pytest v8.3.5, v8.4.2, v9.0.1 -> v9.0.1
Updated referencing v0.35.1, v0.36.2 -> v0.36.2
Updated rpds-py v0.20.1, v0.27.1 -> v0.27.1
Updated tenacity v9.0.0, v9.1.2 -> v9.1.2
Updated typing-extensions v4.13.2, v4.15.0 -> v4.15.0
Removed wrapt v1.17.3
Updated zipp v3.20.2, v3.23.0 -> v3.23.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 21s</sub>

### 💬 Copilot

Lock file updated. Now let's run the tests to verify:

---

<sub>⏱️ 5m 22s</sub>

### ✅ `bash`

**Run unit tests with upgraded ops**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && uv run pytest tests/unit/ -v 2>&1

<details>
<summary>39 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: .venv
░░░░░░░░░░░░░░░░░░░░ [0/0] Installing wheels...                                                                         ░░░░░░░░░░░░░░░░░░░░ [0/18] Installing wheels...                                                                        ░░░░░░░░░░░░░░░░░░░░ [0/18] typing-extensions==4.15.0                                                                   █░░░░░░░░░░░░░░░░░░░ [1/18] typing-extensions==4.15.0                                                                   █░░░░░░░░░░░░░░░░░░░ [1/18] rpds-py==0.27.1                                                                             ██░░░░░░░░░░░░░░░░░░ [2/18] rpds-py==0.27.1                                                                             ██░░░░░░░░░░░░░░░░░░ [2/18] annotated-types==0.7.0                                                                      ███░░░░░░░░░░░░░░░░░ [3/18] annotated-types==0.7.0                                                                      ███░░░░░░░░░░░░░░░░░ [3/18] referencing==0.36.2                                                                         ████░░░░░░░░░░░░░░░░ [4/18] referencing==0.36.2                                                                         ████░░░░░░░░░░░░░░░░ [4/18] tenacity==9.1.2                                                                             █████░░░░░░░░░░░░░░░ [5/18] tenacity==9.1.2                                                                             █████░░░░░░░░░░░░░░░ [5/18] pyyaml==6.0.3                                                                               ██████░░░░░░░░░░░░░░ [6/18] pyyaml==6.0.3                                                                               ██████░░░░░░░░░░░░░░ [6/18] attrs==25.3.0                                                                               ███████░░░░░░░░░░░░░ [7/18] attrs==25.3.0                                                                               ███████░░░░░░░░░░░░░ [7/18] typing-inspection==0.4.2                                                                    ████████░░░░░░░░░░░░ [8/18] typing-inspection==0.4.2                                                                    ████████░░░░░░░░░░░░ [8/18] cosl==1.4.0                                                                                 ██████████░░░░░░░░░░ [9/18] cosl==1.4.0                                                                                 Installed 18 packages in 32ms
================================================= test session starts ==================================================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4
configfile: pyproject.toml
plugins: jubilant-1.1, interface-tester-3.4.1, hypothesis-6.151.9, asyncio-0.21.2, anyio-4.12.1, pytest_httpserver-1.1.5
asyncio: mode=Mode.STRICT
collecting ... collected 0 items / 2 errors                                                                                           

======================================================== ERRORS ========================================================
______________________________________ ERROR collecting tests/unit/test_charm.py _______________________________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests/unit/test_charm.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_charm.py:10: in <module>
    from charm import ZincCharm
E   ModuleNotFoundError: No module named 'charm'
_______________________________________ ERROR collecting tests/unit/test_zinc.py _______________________________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests/unit/test_zinc.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_zinc.py:8: in <module>
    from zinc import Zinc
E   ModuleNotFoundError: No module named 'zinc'
=============================================== short test summary info ================================================
ERROR tests/unit/test_charm.py
ERROR tests/unit/test_zinc.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
================================================== 2 errors in 0.14s ===================================================
<exited with exit code 2>
```

</details>


---

<sub>⏱️ 5m 30s</sub>

### ✅ `bash`

**Run tests with src in path**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && uv run pytest tests/unit/ -v --import-mode=importlib --pythonpath src 2>&1 | tail -30

```
ERROR: usage: pytest [options] [file_or_dir] [file_or_dir] [...]
pytest: error: unrecognized arguments: --pythonpath src
  inifile: /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/pyproject.toml
  rootdir: /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4
<exited with exit code 0>
```


---

<sub>⏱️ 5m 37s</sub>

### ✅ `bash`

**Run tests with PYTHONPATH set**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && PYTHONPATH=src uv run pytest tests/unit/ -v 2>&1 | tail -40

<details>
<summary>27 lines</summary>

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4
configfile: pyproject.toml
plugins: jubilant-1.1, interface-tester-3.4.1, hypothesis-6.151.9, asyncio-0.21.2, anyio-4.12.1, pytest_httpserver-1.1.5
asyncio: mode=Mode.STRICT
collecting ... collected 5 items / 1 error

==================================== ERRORS ====================================
__________________ ERROR collecting tests/unit/test_charm.py ___________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests/unit/test_charm.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_charm.py:10: in <module>
    from charm import ZincCharm
src/charm.py:11: in <module>
    from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
E   ModuleNotFoundError: No module named 'charms'
=========================== short test summary info ============================
ERROR tests/unit/test_charm.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.13s ===============================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 44s</sub>

### ✅ `bash`

**Run tests with both src and lib in path**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && ls lib/ && PYTHONPATH=src:lib uv run pytest tests/unit/ -v 2>&1 | tail -40

<details>
<summary>23 lines</summary>

```
charms
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4
configfile: pyproject.toml
plugins: jubilant-1.1, interface-tester-3.4.1, hypothesis-6.151.9, asyncio-0.21.2, anyio-4.12.1, pytest_httpserver-1.1.5
asyncio: mode=Mode.STRICT
collecting ... collected 11 items

tests/unit/test_charm.py::test_zinc_pebble_ready PASSED                  [  9%]
tests/unit/test_charm.py::test_update_status PASSED                      [ 18%]
tests/unit/test_charm.py::test_zinc_password_no_relation PASSED          [ 27%]
tests/unit/test_charm.py::test_zinc_password_from_relation PASSED        [ 36%]
tests/unit/test_charm.py::test_zinc_password_create_as_leader PASSED     [ 45%]
tests/unit/test_charm.py::test_zinc_password_create_as_non_leader PASSED [ 54%]
tests/unit/test_zinc.py::test_property_pebble_layer PASSED               [ 63%]
tests/unit/test_zinc.py::test_property_port_returns_int PASSED           [ 72%]
tests/unit/test_zinc.py::test_property_port_returns_str PASSED           [ 81%]
tests/unit/test_zinc.py::test_version_returns_str PASSED                 [ 90%]
tests/unit/test_zinc.py::test_version_returns_empty_string_when_request_fails PASSED [100%]

============================== 11 passed in 0.17s ==============================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 50s</sub>

### 💬 Copilot

All 11 tests pass. Let me also run the linter:

---

<sub>⏱️ 5m 50s</sub>

### ✅ `bash`

**Check how tests/linting are normally run**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && cat Makefile | grep -A5 "test\|lint"

<details>
<summary>32 lines</summary>

```
TESTS := $(PROJECT)tests
ALL := $(SRC) $(TESTS)

export PYTHONPATH = $(PROJECT):$(PROJECT)/lib:$(SRC)

update-dependencies:
--
lint:
	uv tool run ruff check $(ALL)
	uv tool run ruff format --check --diff $(ALL)

format:
	uv tool run ruff check --fix $(ALL)
--
		-m pytest \
		--ignore=$(TESTS)/integration \
		--tb native \
		-v \
		-s \
		$(ARGS)
--
		pytest \
		-v \
		-x \
		-s \
		--tb native \
		--ignore=$(TESTS)/unit \
--
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .venv
	rm -rf *.charm
	rm -rf *.rock
	rm -rf **/__pycache__
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 56s</sub>

### ✅ `bash`

**Run linter**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && make lint 2>&1

<details>
<summary>56 lines</summary>

```diff
uv tool run ruff check /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests
⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠙ ruff==0.15.9                                                                                                          ⠙                                                                                                                       ░░░░░░░░░░░░░░░░░░░░ [0/0] Installing wheels...                                                                         ░░░░░░░░░░░░░░░░░░░░ [0/1] Installing wheels...                                                                         ░░░░░░░░░░░░░░░░░░░░ [0/1] ruff==0.15.9                                                                                 ████████████████████ [1/1] ruff==0.15.9                                                                                 Installed 1 package in 4ms
All checks passed!
uv tool run ruff format --check --diff /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests
⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠙ ruff==0.15.9                                                                                                          ⠙                                                                                                                       --- src/zinc.py
+++ src/zinc.py
@@ -23,26 +23,28 @@
 
     def pebble_layer(self, initial_password) -> ops.pebble.Layer:
         """Return a Pebble layer for managing Zinc."""
-        return ops.pebble.Layer({
-            "services": {
-                "zinc": {
-                    "override": "replace",
-                    "summary": "zinc",
-                    # go-runner achieves the equivalent of:`bash -c '/bin/zinc | tee PATH'`, but
-                    # without including bash etc. in the image.
-                    "command": f"/bin/go-runner --log-file={self.log_path} --also-stdout=true --redirect-stderr=true /bin/zincsearch",
-                    "startup": "enabled",
-                    "environment": {
-                        "ZINC_DATA_PATH": "/var/lib/zincsearch",
-                        "ZINC_FIRST_ADMIN_USER": "admin",
-                        "ZINC_FIRST_ADMIN_PASSWORD": initial_password,
-                        "ZINC_PROMETHEUS_ENABLE": True,
-                        "ZINC_TELEMETRY": False,
-                        "ZINC_PROFILER": True,
-                    },
-                }
-            },
-        })
+        return ops.pebble.Layer(
+            {
+                "services": {
+                    "zinc": {
+                        "override": "replace",
+                        "summary": "zinc",
+                        # go-runner achieves the equivalent of:`bash -c '/bin/zinc | tee PATH'`, but
+                        # without including bash etc. in the image.
+                        "command": f"/bin/go-runner --log-file={self.log_path} --also-stdout=true --redirect-stderr=true /bin/zincsearch",
+                        "startup": "enabled",
+                        "environment": {
+                            "ZINC_DATA_PATH": "/var/lib/zincsearch",
+                            "ZINC_FIRST_ADMIN_USER": "admin",
+                            "ZINC_FIRST_ADMIN_PASSWORD": initial_password,
+                            "ZINC_PROMETHEUS_ENABLE": True,
+                            "ZINC_TELEMETRY": False,
+                            "ZINC_PROFILER": True,
+                        },
+                    }
+                },
+            }
+        )
 
     @property
     def log_path(self) -> str:

1 file would be reformatted, 11 files already formatted
make: *** [Makefile:18: lint] Error 1
<exited with exit code 2>
```

</details>


---

<sub>⏱️ 6m 5s</sub>

### ✅ `bash`

**Auto-format code**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && make format 2>&1 | tail -5

```
uv tool run ruff check --fix /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests
All checks passed!
uv tool run ruff format /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests
1 file reformatted, 11 files left unchanged
<exited with exit code 0>
```


---

<sub>⏱️ 6m 12s</sub>

### ✅ `bash`

**Final lint and test run**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && make lint 2>&1 | tail -5 && PYTHONPATH=src:lib uv run pytest tests/unit/ -v 2>&1 | tail -20

<details>
<summary>23 lines</summary>

```
uv tool run ruff check /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests
All checks passed!
uv tool run ruff format --check --diff /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/src /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4/tests
12 files already formatted
hypothesis profile 'default'
rootdir: /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4
configfile: pyproject.toml
plugins: jubilant-1.1, interface-tester-3.4.1, hypothesis-6.151.9, asyncio-0.21.2, anyio-4.12.1, pytest_httpserver-1.1.5
asyncio: mode=Mode.STRICT
collecting ... collected 11 items

tests/unit/test_charm.py::test_zinc_pebble_ready PASSED                  [  9%]
tests/unit/test_charm.py::test_update_status PASSED                      [ 18%]
tests/unit/test_charm.py::test_zinc_password_no_relation PASSED          [ 27%]
tests/unit/test_charm.py::test_zinc_password_from_relation PASSED        [ 36%]
tests/unit/test_charm.py::test_zinc_password_create_as_leader PASSED     [ 45%]
tests/unit/test_charm.py::test_zinc_password_create_as_non_leader PASSED [ 54%]
tests/unit/test_zinc.py::test_property_pebble_layer PASSED               [ 63%]
tests/unit/test_zinc.py::test_property_port_returns_int PASSED           [ 72%]
tests/unit/test_zinc.py::test_property_port_returns_str PASSED           [ 81%]
tests/unit/test_zinc.py::test_version_returns_str PASSED                 [ 90%]
tests/unit/test_zinc.py::test_version_returns_empty_string_when_request_fails PASSED [100%]

============================== 11 passed in 0.14s ==============================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 18s</sub>

### 💬 Copilot

All clean. Now commit everything:

---

<sub>⏱️ 6m 19s</sub>

### ✅ `bash`

**Show changed files**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && git diff --stat

<details>
<summary>6 lines</summary>

```
pyproject.toml    |   4 +-
 src/zinc.py       |  46 +++---
 tests/conftest.py |   8 +
 uv.lock           | 854 +++++-----------------------------------------------------------------------------------------
 4 files changed, 79 insertions(+), 833 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 38s</sub>

### ✅ `bash`

**Commit all changes**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__all__C4 && git add -A && git commit -m "chore: upgrade ops from 2.23.2 to 3.7.0

Reviewed all release notes from ops 3.0.0 through 3.7.0, plus
ops-tracing 3.7.0, and applied the following changes:

ops 3.0.0 – drops Python 3.8:
- Raise requires-python lower bound to >=3.10 (3.9 was also dropped
  in 3.4.0 internals).

ops 3.2.0 – pebble.Layer best practice:
- Change Zinc.pebble_layer() return type from dict to ops.pebble.Layer.
  pebble.Layer.__eq__ handles dict comparison, so all existing test
  assertions continue to work without modification.

ops 3.5.0 – SCENARIO_BARE_CHARM_ERRORS:
- Set the SCENARIO_BARE_CHARM_ERRORS=true env var in conftest.py so
  that exceptions raised inside charm code propagate directly to test
  functions instead of being wrapped in UncaughtCharmError, making
  test failures easier to diagnose.  This will become the default in a
  future major ops release.

ops 3.7.0 (and ops-scenario 8.7.0):
- No breaking changes affect this charm.
- New features (charmcraft extension autoload, get_relation accepting
  relation objects, breakpoint support) require no code changes but are
  available automatically.

ops-tracing 3.7.0:
- The charm does not use tracing; no changes required.

Dependencies:
- ops: 2.23.2 → 3.7.0 (pyproject.toml lower bound + uv.lock)
- ops-scenario: 7.23.2 → 8.7.0 (transitive via ops[testing])
- Various transitive packages simplified (no more Python 3.8/3.9
  version markers or importlib-metadata/wrapt back-ports).

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[ops-3.7.0-upgrade 2600067] chore: upgrade ops from 2.23.2 to 3.7.0
 4 files changed, 79 insertions(+), 833 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 6m 47s</sub>

### ❌ `store_memory`

<details>
<summary>Arguments</summary>

```json
{
  "subject": "testing setup",
  "fact": "Tests require PYTHONPATH=src:lib to find charm modules. Use `make test` (sets PYTHONPATH via Makefile) or `PYTHONPATH=src:lib uv run pytest tests/unit/`.",
  "citations": "Makefile:17 (export PYTHONPATH = $(PROJECT):$(PROJECT)/lib:$(SRC))",
  "reason": "Needed for running unit tests correctly; anyone running pytest directly without the Makefile will hit ModuleNotFoundError for 'charm' and 'zinc'."
}
```

</details>

```
Unable to store memory. The repository may not exist or you may not have write access to it. You can continue with your task without storing this information.
```


---

<sub>⏱️ 7m 2s</sub>

### ✅ `task_complete`

**## ops 2.23.2 → 3.7.0 upgrade on branch `ops-3.7.0-upgrad...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "## ops 2.23.2 → 3.7.0 upgrade on branch `ops-3.7.0-upgrade`\n\n### Release notes analysis\n\n| Version | Change | Impact on charm |\n|---------|--------|-----------------|\n| **3.0.0** | Drops Python 3.8 | Update `requires-python` |\n| **3.2.0** | `pebble.Layer` preferred over raw dicts | Update `pebble_layer()` |\n| **3.3.0** | `ops.JujuContext` exposed | No changes needed |\n| **3.4.0** | `ops.hookcmds` added; Python 3.9 compat code dropped | No changes needed; `requires-python` bump covers this |\n| **3.4.0** | **Breaking**: context-manager + exception tests need `UncaughtCharmError` | Not affected (charm tests don't use that pattern) |\n| **3.5.0** | `SCENARIO_BARE_CHARM_ERRORS=true` env var for cleaner test errors | Added to `conftest.py` |\n| **3.5.0** | `testing.Context.charm_spec` deprecated | Not used by this charm |\n| **3.6.0** | Default Juju version in testing bumped to 3.6.14 | No changes needed |\n| **3.7.0** | `State.get_relation` accepts relation objects; charmcraft.yaml autoload; breakpoint support | No changes needed; features available automatically |\n| **ops-tracing 3.7.0** | Parallel versioned tracing library | Charm doesn't use tracing; no changes needed |\n\n### Changes made\n\n- **`pyproject.toml`**: `requires-python` raised to `>=3.10`; `ops` lower bound set to `>=3.7.0`\n- **`src/zinc.py`**: `pebble_layer()` now returns `ops.pebble.Layer(...)` instead of a plain `dict` — the current best practice; test assertions work unchanged because `Layer.__eq__` handles dict comparison\n- **`tests/conftest.py`**: `SCENARIO_BARE_CHARM_ERRORS=true` set at module load time, opting into clearer exception propagation in state-transition tests (ops 3.5.0 feature)\n- **`uv.lock`**: `ops` 2.23.2 → 3.7.0, `ops-scenario` 7.23.2 → 8.7.0; several Python-version-marker back-ports removed\n\nAll 11 unit tests pass; linter clean."
}
```

</details>

<details>
<summary>20 lines</summary>

```
## ops 2.23.2 → 3.7.0 upgrade on branch `ops-3.7.0-upgrade`

### Release notes analysis

| Version | Change | Impact on charm |
|---------|--------|-----------------|
| **3.0.0** | Drops Python 3.8 | Update `requires-python` |
| **3.2.0** | `pebble.Layer` preferred over raw dicts | Update `pebble_layer()` |
| **3.3.0** | `ops.JujuContext` exposed | No changes needed |
| **3.4.0** | `ops.hookcmds` added; Python 3.9 compat code dropped | No changes needed; `requires-python` bump covers this |
| **3.4.0** | **Breaking**: context-manager + exception tests need `UncaughtCharmError` | Not affected (charm tests don't use that pattern) |
| **3.5.0** | `SCENARIO_BARE_CHARM_ERRORS=true` env var for cleaner test errors | Added to `conftest.py` |
| **3.5.0** | `testing.Context.charm_spec` deprecated | Not used by this charm |
| **3.6.0** | Default Juju version in testing bumped to 3.6.14 | No changes needed |
| **3.7.0** | `State.get_relation` accepts relation objects; charmcraft.yaml autoload; breakpoint support | No changes needed; features available automatically |
| **ops-tracing 3.7.0** | Parallel versioned tracing library | Charm doesn't use tracing; no changes needed |

### Changes made

- **`pyproject.toml`**: `requires-python` raised to `>=3.10`; `ops` lower bound set to `>=3.7.0`
- **`src/zinc.py`**: `pebble_layer()` now returns `ops.pebble.Layer(...)` instead of a plain `dict` — the current best practice; test assertions work unchanged because `Layer.__eq__` handles dict comparison
- **`tests/conftest.py`**: `SCENARIO_BARE_CHARM_ERRORS=true` set at module load time, opting into clearer exception propagation in state-transition tests (ops 3.5.0 feature)
- **`uv.lock`**: `ops` 2.23.2 → 3.7.0, `ops-scenario` 7.23.2 → 8.7.0; several Python-version-marker back-ports removed

All 11 unit tests pass; linter clean.
```

</details>


---

<sub>⏱️ 7m 2s</sub>

### ✓ Task Complete

## ops 2.23.2 → 3.7.0 upgrade on branch `ops-3.7.0-upgrade`

### Release notes analysis

| Version | Change | Impact on charm |
|---------|--------|-----------------|
| **3.0.0** | Drops Python 3.8 | Update `requires-python` |
| **3.2.0** | `pebble.Layer` preferred over raw dicts | Update `pebble_layer()` |
| **3.3.0** | `ops.JujuContext` exposed | No changes needed |
| **3.4.0** | `ops.hookcmds` added; Python 3.9 compat code dropped | No changes needed; `requires-python` bump covers this |
| **3.4.0** | **Breaking**: context-manager + exception tests need `UncaughtCharmError` | Not affected (charm tests don't use that pattern) |
| **3.5.0** | `SCENARIO_BARE_CHARM_ERRORS=true` env var for cleaner test errors | Added to `conftest.py` |
| **3.5.0** | `testing.Context.charm_spec` deprecated | Not used by this charm |
| **3.6.0** | Default Juju version in testing bumped to 3.6.14 | No changes needed |
| **3.7.0** | `State.get_relation` accepts relation objects; charmcraft.yaml autoload; breakpoint support | No changes needed; features available automatically |
| **ops-tracing 3.7.0** | Parallel versioned tracing library | Charm doesn't use tracing; no changes needed |

### Changes made

- **`pyproject.toml`**: `requires-python` raised to `>=3.10`; `ops` lower bound set to `>=3.7.0`
- **`src/zinc.py`**: `pebble_layer()` now returns `ops.pebble.Layer(...)` instead of a plain `dict` — the current best practice; test assertions work unchanged because `Layer.__eq__` handles dict comparison
- **`tests/conftest.py`**: `SCENARIO_BARE_CHARM_ERRORS=true` set at module load time, opting into clearer exception propagation in state-transition tests (ops 3.5.0 feature)
- **`uv.lock`**: `ops` 2.23.2 → 3.7.0, `ops-scenario` 7.23.2 → 8.7.0; several Python-version-marker back-ports removed

All 11 unit tests pass; linter clean.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
