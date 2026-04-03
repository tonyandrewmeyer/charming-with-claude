# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `4a6950a0-5ac8-4641-a38a-0866419c3b7c`  
> - **Started:** 4/3/2026, 9:34:30 AM  
> - **Duration:** 5m 30s  
> - **Exported:** 4/3/2026, 9:40:00 AM  

---

<sub>⏱️ 6s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 15s</sub>

### ✅ `bash`

**Check current dependencies and charm config**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && cat pyproject.toml && echo "---" && cat charmcraft.yaml | head -60

<details>
<summary>98 lines</summary>

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
    upstream-source: ghcr.io/jnsgruk/zinc:0.4.10

peers:
  zinc-peers:
    interface: zinc_peers

provides:
  metrics-endpoint:
    interface: prometheus_scrape
  profiling-endpoint:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 14s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/src.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/src

```
charm.py
grafana_dashboards
loki_alert_rules
prometheus_alert_rules
zinc.py
```


---

<sub>⏱️ 21s</sub>

### ✅ `bash`

**Read charm source files**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && cat src/charm.py && echo "===" && cat src/zinc.py

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

<sub>⏱️ 21s</sub>

### ✅ `bash`

**Explore tests directory**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && ls tests/ && cat tests/test_charm.py 2>/dev/null | head -100

```
conftest.py  integration  spread  unit
<exited with exit code 0>
```


---

<sub>⏱️ 29s</sub>

### ✅ `web_search`

**ops Python charm library latest release notes changelog 2024 2025**

<details>
<summary>Arguments</summary>

```json
{
  "query": "ops Python charm library latest release notes changelog 2024 2025"
}
```

</details>

```
{"type":"text","text":{"value":"I was unable to find a changelog or release notes specifically for the \"ops\" Python charm library (often used for developing Charmed Operators, also known as charms, in the Operator Framework) covering 2024 and 2025 from major primary sources in the top search results.\n\n**How to Find Latest Release Notes and Changelog:**\n1. **Official Docs & PyPI**: The canonical location for the `ops` library’s release notes and changelog is typically its [GitHub repository](https://github.com/canonical/operator/) or the [PyPI page](https://pypi.org/project/opslib/ or https://pypi.org/project/ops/), where you can check tags, releases, and the file named `CHANGELOG.md` or `CHANGES.md`.\n2. **Canonical Discourse**: For important updates and discussions, the [Canonical Discourse forum](https://discourse.charmhub.io/c/operator-framework/ops-library/) often hosts announcement posts for new releases.\n3. **Charmhub**: The [Charmhub documentation](https://charmhub.io/docs/sdk) or its `ops` section may also relay recent version changes.\n\n**Recent Ops Library Changes (as of late 2023 and 2024-2025 trends):**\n- Previous releases have focused on improved support for Juju events, better state management and serialization, relation data enhancements, and clearer lifecycle hooks.\n- The project usually releases on an approximately monthly or quarterly basis, with detailed changelogs tracking API changes, deprecations, and new features.\n\n**Recommendation:**  \nVisit the [official Operator Framework GitHub Releases page](https://github.com/canonical/operator/releases) or the [canonical/operator changelog file](https://github.com/canonical/operator/blob/main/CHANGELOG.md) for the most accurate and up-to-date information. That will include all specific changes, new features, bug fixes, and compatibility notes for each version throughout 2024 and 2025.\n\nIf you have a particular version in mind or need highlights for certain releases, or if you want guidance on how to subscribe to future updates, let me know!","annotations":[]},"bing_searches":[{"text":"ops Python charm library latest release notes changelog 2024 2025","url":"https://www.bing.com/search?q=ops+Python+charm+library+latest+release+notes+changelog+2024+2025"}],"annotations":null}
```


---

<sub>⏱️ 36s</sub>

### ✅ `bash`

**Check current ops version in uv.lock**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && cat uv.lock | grep -A3 'name = "ops"'

<details>
<summary>31 lines</summary>

```
{ name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.12.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
--
name = "ops"
version = "2.23.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
--
    { name = "ops" },
    { name = "pyyaml" },
]
sdist = { url = "https://files.pythonhosted.org/packages/ee/e7/1514b9c27b9364ec1d04791b0fb76d1a629c8cc73f90fbf6dd867457c914/ops_scenario-7.23.2.tar.gz", hash = "sha256:327dda8b3c871ccf16246ed4f8c7e093526af42093549976596cede58cbc8488", size = 70017, upload-time = "2026-02-11T03:58:16.553Z" }
--
    { name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.12.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
]
--
    { name = "ops", extra = ["testing"] },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.12.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pytest", version = "8.3.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
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

<sub>⏱️ 37s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/releases",
  "max_length": 15000
}
```

</details>

<details>
<summary>149 lines</summary>

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

## 3.4.0: a low-l

<note>Content truncated. Call the fetch tool with a start_index of 15000 to get more content.</note>
```

</details>


---

<sub>⏱️ 45s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://github.com/canonical/operator/releases",
  "start_index": 15000
}
```

</details>

<details>
<summary>142 lines</summary>

```
Contents of https://github.com/canonical/operator/releases:
evel API for the Juju hook commands

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

*   Update referenced examples for managing interfaces in [#2068](h

<note>Content truncated. Call the fetch tool with a start_index of 30000 to get more content.</note>
```

</details>


---

<sub>⏱️ 45s</sub>

### ✅ `bash`

**Read unit tests**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && cat tests/unit/test_charm.py 2>/dev/null || cat tests/unit/*.py 2>/dev/null | head -200

<details>
<summary>84 lines</summary>

```
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 57s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.0.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://github.com/canonical/operator/releases/tag/3.0.0"
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

<sub>⏱️ 57s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.1.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/releases/tag/3.1.0"
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

<sub>⏱️ 57s</sub>

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

<sub>⏱️ 1m 4s</sub>

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

<sub>⏱️ 1m 4s</sub>

### ✅ `bash`

**Read test files**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && cat tests/unit/conftest.py 2>/dev/null && ls tests/integration/ 2>/dev/null && cat tests/integration/test_charm.py 2>/dev/null | head -60

```

<exited with exit code 1>
```


---

<sub>⏱️ 1m 58s</sub>

### ✅ `bash`

**Check ops-tracing and ops-scenario versions**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && grep -A5 'name = "ops-tracing"' uv.lock | head -20 && grep -A5 'name = "ops-scenario"' uv.lock | head -20

<details>
<summary>10 lines</summary>

```
{ name = "ops-scenario" },
]

[[package]]
name = "ops-scenario"
version = "7.23.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "ops" },
    { name = "pyyaml" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 59s</sub>

### ✅ `bash`

**Check latest available versions**

$ pip index versions ops 2>/dev/null | head -5 && pip index versions ops-tracing 2>/dev/null | head -5

<details>
<summary>9 lines</summary>

```
ops (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 2.20.0, 2.19.4, 2.19.0, 2.18.1, 2.18.0, 2.17.1, 2.17.0, 2.16.1, 2.16.0, 2.15.0, 2.14.1, 2.14.0, 2.13.0, 2.12.0, 2.11.0, 2.10.0, 2.9.0, 2.8.0, 2.7.0, 2.6.0, 2.5.1, 2.5.0, 2.4.1, 2.4.0, 2.3.0, 2.2.0, 2.1.1, 2.1.0, 2.0.0, 1.5.5, 1.5.4, 1.5.3, 1.5.2, 1.5.1, 1.5.0, 1.4.0, 1.3.0, 1.2.0, 1.1.0, 1.0.1, 1.0.0, 0.10.0, 0.9.0, 0.8.0, 0.7.0, 0.6.1, 0.6.0, 0.4.7, 0.4.6, 0.4.5, 0.4.4, 0.4.3, 0.4.2, 0.2.1, 0.2.0, 0.1.0
  INSTALLED: 3.7.0
  LATEST:    3.7.0
ops-tracing (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 0.9.6, 0.9.4, 0.9.3, 0.9.2, 0.9.1, 0.9.0
  INSTALLED: 3.7.0
  LATEST:    3.7.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 10s</sub>

### ✅ `bash`

**Check full charmcraft.yaml and search for tracing usage**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && cat charmcraft.yaml && grep -r "tracing\|ops-tracing" . --include="*.py" --include="*.yaml" --include="*.toml" | grep -v ".lock"

<details>
<summary>75 lines</summary>

```
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
    upstream-source: ghcr.io/jnsgruk/zinc:0.4.10

peers:
  zinc-peers:
    interface: zinc_peers

provides:
  metrics-endpoint:
    interface: prometheus_scrape
  profiling-endpoint:
    interface: parca_scrape
  grafana-dashboard:
    interface: grafana_dashboard

charm-libs:
  - lib: grafana_k8s.grafana_dashboard
    version: "0"
  - lib: loki_k8s.loki_push_api
    version: "0"
  - lib: parca_k8s.parca_scrape
    version: "0"
  - lib: traefik_k8s.ingress
    version: "2"

requires:
  log-proxy:
    interface: loki_push_api
    limit: 1
  ingress:
    interface: ingress
    limit: 1

storage:
  data:
    type: filesystem
    location: /zinc-data
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 2m 11s</sub>

### ✅ `bash`

**Check installed ops packages info**

$ pip show ops 2>/dev/null | head -5 && pip show ops-tracing 2>/dev/null | head -5

<details>
<summary>11 lines</summary>

```
Name: ops
Version: 3.7.0
Summary: The Python library behind great charms
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
Name: ops-tracing
Version: 3.7.0
Summary: The tracing facility for the Ops library.
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 44s</sub>

### 💬 Copilot

Now I have a clear understanding. Let me check the existing tests and conftest files:

---

<sub>⏱️ 2m 44s</sub>

### ✅ `bash`

**Check conftest files**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && cat tests/conftest.py 2>/dev/null; ls tests/unit/; cat tests/unit/conftest.py 2>/dev/null

<details>
<summary>8 lines</summary>

```
from _pytest.config.argparsing import Parser


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--charm-path",
        help="Pre-built charm file to deploy, rather than building from source",
    )
test_charm.py  test_zinc.py
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 2m 44s</sub>

### ✅ `bash`

**Check git status**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && git log --oneline -5 && git status

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

<sub>⏱️ 2m 51s</sub>

### ✅ `bash`

**Read zinc unit tests**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && cat tests/unit/test_zinc.py

<details>
<summary>43 lines</summary>

```
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

<sub>⏱️ 2m 51s</sub>

### ✅ `bash`

**Create new branch for upgrade**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && git checkout -b upgrade-ops-3.7.0 2>&1

```
Switched to a new branch 'upgrade-ops-3.7.0'
<exited with exit code 0>
```


---

<sub>⏱️ 2m 59s</sub>

### 💬 Copilot

Now let me run the existing tests first to establish a baseline, then make the changes:

---

<sub>⏱️ 2m 59s</sub>

### ✅ `bash`

**Run current tests as baseline**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && python -m pytest tests/unit/ -v 2>&1 | tail -30

```
bash: python: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 3m 6s</sub>

### ✅ `bash`

**Run current tests as baseline**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && python3 -m pytest tests/unit/ -v 2>&1 | tail -40

<details>
<summary>36 lines</summary>

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4
configfile: pyproject.toml
plugins: jubilant-1.1, interface-tester-3.4.1, hypothesis-6.151.9, asyncio-0.21.2, anyio-4.12.1, pytest_httpserver-1.1.5
asyncio: mode=Mode.STRICT
collecting ... collected 0 items / 2 errors

==================================== ERRORS ====================================
__________________ ERROR collecting tests/unit/test_charm.py ___________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/tests/unit/test_charm.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_charm.py:10: in <module>
    from charm import ZincCharm
E   ModuleNotFoundError: No module named 'charm'
___________________ ERROR collecting tests/unit/test_zinc.py ___________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/tests/unit/test_zinc.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_zinc.py:8: in <module>
    from zinc import Zinc
E   ModuleNotFoundError: No module named 'zinc'
=========================== short test summary info ============================
ERROR tests/unit/test_charm.py
ERROR tests/unit/test_zinc.py
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
============================== 2 errors in 0.11s ===============================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 12s</sub>

### ✅ `bash`

**Run current tests with src in PYTHONPATH**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && PYTHONPATH=src python3 -m pytest tests/unit/ -v 2>&1 | tail -40

<details>
<summary>27 lines</summary>

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4
configfile: pyproject.toml
plugins: jubilant-1.1, interface-tester-3.4.1, hypothesis-6.151.9, asyncio-0.21.2, anyio-4.12.1, pytest_httpserver-1.1.5
asyncio: mode=Mode.STRICT
collecting ... collected 5 items / 1 error

==================================== ERRORS ====================================
__________________ ERROR collecting tests/unit/test_charm.py ___________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/tests/unit/test_charm.py'.
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
=============================== 1 error in 0.10s ===============================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 18s</sub>

### ✅ `bash`

**Run tests with lib in PYTHONPATH too**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && PYTHONPATH=src:lib python3 -m pytest tests/unit/ -v 2>&1 | tail -40

<details>
<summary>22 lines</summary>

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4
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

<sub>⏱️ 3m 47s</sub>

### 💬 Copilot

Good - tests already pass with ops 3.7.0. Now let me make the changes:

---

<sub>⏱️ 3m 47s</sub>

### ✅ `bash`

**Check pytest paths config**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && grep -n "pythonpath\|testpaths" pyproject.toml

```

<exited with exit code 1>
```


---

<sub>⏱️ 3m 53s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 3m 59s</sub>

### 💬 Copilot

Now add `SCENARIO_BARE_CHARM_ERRORS=true` for the unit tests — the cleanest approach is to set it in the pytest config in `pyproject.toml`:

---

<sub>⏱️ 3m 59s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/pyproject.toml (lines 20-30)

<details>
<summary>11 lines</summary>

```
20. branch = true
21. 
22. [tool.coverage.report]
23. show_missing = true
24. 
25. [tool.pytest.ini_options]
26. minversion = "6.0"
27. log_cli_level = "INFO"
28. 
29. # Linting tools configuration
30. [tool.ruff]
```

</details>


---

<sub>⏱️ 4m 12s</sub>

### ✅ `bash`

**Check unit test directory contents**

$ ls /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/tests/unit/

```
__pycache__  test_charm.py  test_zinc.py
<exited with exit code 0>
```


---

<sub>⏱️ 4m 18s</sub>

### ✅ `create`

**create a new file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/tests/unit/conftest.py

```
Created file /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4/tests/unit/conftest.py with 324 characters
```


---

<sub>⏱️ 4m 22s</sub>

### 💬 Copilot

Now update the `uv.lock` to pin to ops 3.7.0:

---

<sub>⏱️ 4m 24s</sub>

### ✅ `bash`

**Update uv.lock for ops upgrade**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && uv lock --upgrade-package ops --upgrade-package ops-tracing 2>&1

<details>
<summary>23 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠙ zinc-k8s-operator==0.1.0                                                                                              ⠙ zinc-k8s-operator==0.1.0                                                                                              ⠹ zinc-k8s-operator==0.1.0                                                                                              ⠹ cosl==1.4.0                                                                                                           ⠸ cosl==1.4.0                                                                                                           ⠸ jsonschema==4.25.1                                                                                                    ⠸ ops==3.7.0                                                                                                            ⠸ ops==3.7.0                                                                                                            ⠼ ops==3.7.0                                                                                                            ⠼ ops-scenario==8.7.0                                                                                                   ⠼ pydantic==2.12.5                                                                                                      ⠼ pydantic-core==2.41.5                                                                                                 ⠼ coverage==7.10.7                                                                                                      ⠼ coverage==7.10.7                                                                                                      ⠼ jubilant==1.7.0                                                                                                       ⠼ pytest==9.0.1                                                                                                         ⠼ ruff==0.15.4                                                                                                          ⠼ pyyaml==6.0.3                                                                                                         ⠼ tenacity==9.1.2                                                                                                       ⠼ typing-extensions==4.15.0                                                                                             ⠼ attrs==25.3.0                                                                                                         ⠼ jsonschema-specifications==2025.9.1                                                                                   ⠼ referencing==0.36.2                                                                                                   ⠼ typing-extensions==4.15.0                                                                                             ⠼ rpds-py==0.27.1                                                                                                       ⠼ opentelemetry-api==1.37.0                                                                                             ⠼ websocket-client==1.8.0                                                                                               ⠼ annotated-types==0.7.0                                                                                                ⠼ typing-inspection==0.4.2                                                                                              ⠼ tomli==2.2.1                                                                                                          ⠼ tomli==2.2.1                                                                                                          Resolved 31 packages in 780ms
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

<sub>⏱️ 4m 36s</sub>

### ✅ `bash`

**Verify ops version in lockfile**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && grep -A5 'name = "ops"' uv.lock | head -30

<details>
<summary>30 lines</summary>

```
{ name = "ops" },
    { name = "pydantic" },
    { name = "pyyaml" },
    { name = "tenacity" },
    { name = "typing-extensions" },
]
--
name = "ops"
version = "3.7.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "opentelemetry-api" },
    { name = "pyyaml" },
--
    { name = "ops" },
    { name = "pyyaml" },
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/59/38/389a21258f32ecb3513686de889cdea9b02753cfa7f2becff4cef7e6350f/ops_scenario-8.7.0.tar.gz", hash = "sha256:0f17bbcac19e31cd0a408542c517fb22cf532bda1dc4f6133e50bafae0901e41", size = 78410, upload-time = "2026-03-30T05:17:17.573Z" }
wheels = [
--
    { name = "ops" },
    { name = "pydantic" },
]

[package.optional-dependencies]
dev = [
--
    { name = "ops", extra = ["testing"] },
    { name = "pydantic" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 42s</sub>

### ✅ `bash`

**Run tests after upgrade**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && PYTHONPATH=src:lib python3 -m pytest tests/unit/ -v 2>&1 | tail -30

<details>
<summary>22 lines</summary>

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4
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

============================== 11 passed in 0.13s ==============================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 50s</sub>

### 💬 Copilot

All 11 tests pass. Now let me run the linter to make sure everything is clean:

---

<sub>⏱️ 4m 51s</sub>

### ✅ `bash`

**Run ruff linter**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && python3 -m ruff check src/ tests/ 2>&1 | tail -20

```
All checks passed!
<exited with exit code 0>
```


---

<sub>⏱️ 4m 59s</sub>

### 💬 Copilot

Now commit the changes:

---

<sub>⏱️ 4m 59s</sub>

### ✅ `bash`

**Check what changed**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && git diff --stat HEAD

```
pyproject.toml |   2 +-
 uv.lock        | 852 +++++--------------------------------------------------------------------------------------------
 2 files changed, 44 insertions(+), 810 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 5m 13s</sub>

### ✅ `bash`

**Commit the upgrade**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C4 && git add pyproject.toml uv.lock tests/unit/conftest.py && git commit -m "build(deps): upgrade ops to 3.7.0

- Bump ops (and ops-scenario) from 2.23.2 to 3.7.0
- Update requires-python from >=3.8 to >=3.10, matching ops 3.x
  (ops 3.0 dropped Python 3.8 support; ops 3.4 removed 3.8/3.9
  compatibility code entirely)
- Add tests/unit/conftest.py setting SCENARIO_BARE_CHARM_ERRORS=true,
  opting in to the ops 3.5+ behaviour where charm exceptions propagate
  as-is in state-transition tests rather than being wrapped in
  UncaughtCharmError — easier debugging, and the future default

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[upgrade-ops-3.7.0 bd3b0b5] build(deps): upgrade ops to 3.7.0
 3 files changed, 52 insertions(+), 810 deletions(-)
 create mode 100644 tests/unit/conftest.py
<exited with exit code 0>
```


---

<sub>⏱️ 5m 30s</sub>

### ✅ `task_complete`

**## ops upgrade to 3.7.0 — branch `upgrade-ops-3.7.0`

###...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "## ops upgrade to 3.7.0 — branch `upgrade-ops-3.7.0`\n\n### Release notes analysis (ops 2.23.2 → 3.7.0)\n\n| Release | Change | Impact on this charm |\n|---------|--------|----------------------|\n| **3.0.0** | Python 3.8 support dropped | Must update `requires-python`; charm already targets Ubuntu 24.04 so 3.10+ is fine |\n| **3.1.0** | `testing.Context` gains `app_name`/`unit_id` attrs | No action — convenience feature |\n| **3.2.0** | Security event logging at TRACE level; `opentelemetry` log target | No action needed |\n| **3.3.0** | `ops.JujuContext` exposed | No action — not needed here |\n| **3.4.0** | `JujuContext.machine_id` int→str (breaking); `ops.hookcmds` added; testing Context-manager exception wrapping fixed | `machine_id` irrelevant on K8s; charm tests don't use Context as a context manager, so no breakage |\n| **3.5.0** | `SCENARIO_BARE_CHARM_ERRORS` env var; `Context.charm_spec` deprecated | **Adopted**: set `SCENARIO_BARE_CHARM_ERRORS=true` in unit test conftest; `charm_spec` not used |\n| **3.6.0** | Default Juju version in testing bumped to 3.6.14; `Model.get_binding()` type fix | No action needed |\n| **3.7.0** | `breakpoint` in testing; charmcraft extension autoloading; `State.get_relation` accepts relation objects; single-arg `Context` for charmcraft.yaml | No action needed — existing tests already use these patterns correctly |\n\n### Changes made\n\n1. **`pyproject.toml`** — `requires-python = \">=3.8\"` → `\">=3.10\"` (ops 3.x dropped Python 3.8 in 3.0 and removed compatibility shims in 3.4)\n2. **`uv.lock`** — ops bumped 2.23.2 → 3.7.0; ops-scenario bumped 7.23.2 → 8.7.0 (plus transitive updates)\n3. **`tests/unit/conftest.py`** (new) — sets `SCENARIO_BARE_CHARM_ERRORS=true`, opting into the ops 3.5+ behaviour where charm exceptions propagate as-is in state-transition tests (the future default)\n\nAll 11 unit tests pass; ruff reports no issues.\n"
}
```

</details>

<details>
<summary>17 lines</summary>

```
## ops upgrade to 3.7.0 — branch `upgrade-ops-3.7.0`

### Release notes analysis (ops 2.23.2 → 3.7.0)

| Release | Change | Impact on this charm |
|---------|--------|----------------------|
| **3.0.0** | Python 3.8 support dropped | Must update `requires-python`; charm already targets Ubuntu 24.04 so 3.10+ is fine |
| **3.1.0** | `testing.Context` gains `app_name`/`unit_id` attrs | No action — convenience feature |
| **3.2.0** | Security event logging at TRACE level; `opentelemetry` log target | No action needed |
| **3.3.0** | `ops.JujuContext` exposed | No action — not needed here |
| **3.4.0** | `JujuContext.machine_id` int→str (breaking); `ops.hookcmds` added; testing Context-manager exception wrapping fixed | `machine_id` irrelevant on K8s; charm tests don't use Context as a context manager, so no breakage |
| **3.5.0** | `SCENARIO_BARE_CHARM_ERRORS` env var; `Context.charm_spec` deprecated | **Adopted**: set `SCENARIO_BARE_CHARM_ERRORS=true` in unit test conftest; `charm_spec` not used |
| **3.6.0** | Default Juju version in testing bumped to 3.6.14; `Model.get_binding()` type fix | No action needed |
| **3.7.0** | `breakpoint` in testing; charmcraft extension autoloading; `State.get_relation` accepts relation objects; single-arg `Context` for charmcraft.yaml | No action needed — existing tests already use these patterns correctly |

### Changes made

1. **`pyproject.toml`** — `requires-python = ">=3.8"` → `">=3.10"` (ops 3.x dropped Python 3.8 in 3.0 and removed compatibility shims in 3.4)
2. **`uv.lock`** — ops bumped 2.23.2 → 3.7.0; ops-scenario bumped 7.23.2 → 8.7.0 (plus transitive updates)
3. **`tests/unit/conftest.py`** (new) — sets `SCENARIO_BARE_CHARM_ERRORS=true`, opting into the ops 3.5+ behaviour where charm exceptions propagate as-is in state-transition tests (the future default)

All 11 unit tests pass; ruff reports no issues.
```

</details>


---

<sub>⏱️ 5m 30s</sub>

### ✓ Task Complete

## ops upgrade to 3.7.0 — branch `upgrade-ops-3.7.0`

### Release notes analysis (ops 2.23.2 → 3.7.0)

| Release | Change | Impact on this charm |
|---------|--------|----------------------|
| **3.0.0** | Python 3.8 support dropped | Must update `requires-python`; charm already targets Ubuntu 24.04 so 3.10+ is fine |
| **3.1.0** | `testing.Context` gains `app_name`/`unit_id` attrs | No action — convenience feature |
| **3.2.0** | Security event logging at TRACE level; `opentelemetry` log target | No action needed |
| **3.3.0** | `ops.JujuContext` exposed | No action — not needed here |
| **3.4.0** | `JujuContext.machine_id` int→str (breaking); `ops.hookcmds` added; testing Context-manager exception wrapping fixed | `machine_id` irrelevant on K8s; charm tests don't use Context as a context manager, so no breakage |
| **3.5.0** | `SCENARIO_BARE_CHARM_ERRORS` env var; `Context.charm_spec` deprecated | **Adopted**: set `SCENARIO_BARE_CHARM_ERRORS=true` in unit test conftest; `charm_spec` not used |
| **3.6.0** | Default Juju version in testing bumped to 3.6.14; `Model.get_binding()` type fix | No action needed |
| **3.7.0** | `breakpoint` in testing; charmcraft extension autoloading; `State.get_relation` accepts relation objects; single-arg `Context` for charmcraft.yaml | No action needed — existing tests already use these patterns correctly |

### Changes made

1. **`pyproject.toml`** — `requires-python = ">=3.8"` → `">=3.10"` (ops 3.x dropped Python 3.8 in 3.0 and removed compatibility shims in 3.4)
2. **`uv.lock`** — ops bumped 2.23.2 → 3.7.0; ops-scenario bumped 7.23.2 → 8.7.0 (plus transitive updates)
3. **`tests/unit/conftest.py`** (new) — sets `SCENARIO_BARE_CHARM_ERRORS=true`, opting into the ops 3.5+ behaviour where charm exceptions propagate as-is in state-transition tests (the future default)

All 11 unit tests pass; ruff reports no issues.


---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
