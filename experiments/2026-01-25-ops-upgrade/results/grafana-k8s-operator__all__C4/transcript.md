# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `de009f77-5a5e-4f65-879c-e95080813dcb`  
> - **Started:** 4/3/2026, 12:04:53 PM  
> - **Duration:** 14m 58s  
> - **Exported:** 4/3/2026, 12:19:51 PM  

---

<sub>⏱️ 6s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 14s</sub>

### ✅ `bash`

**Check current ops version and charm config**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat pyproject.toml | grep -A5 "ops" && echo "---" && cat charmcraft.yaml | head -60

<details>
<summary>70 lines</summary>

```
"ops>=2.17",
  "ops[tracing]",
  "pyyaml",
  "urllib3",
  "jsonschema",
  "cryptography",
  "jinja2<3",
--
  "ops[testing]",
  "pytest-asyncio",
  "pytest-playwright",
  "aiohttp!=3.11.13",  # Yanked
  "asyncstdlib",
  "sh",
---
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

type: charm
name: grafana-k8s
summary: Data visualization and observability with Grafana
description: |
  Grafana provides dashboards for monitoring data and this
  charm is written to allow for HA on Kubernetes and can take
  multiple data sources (for example, Prometheus).

links:
  documentation: https://discourse.charmhub.io/t/grafana-operator-k8s-docs-index/5612
  website:
    - https://charmhub.io/grafana-k8s
  source:
    - https://github.com/canonical/grafana-k8s-operator
  issues:
    - https://github.com/canonical/grafana-k8s-operator/issues

assumes:
  - k8s-api
  - juju >= 3.6

containers:
  grafana:
    resource: grafana-image
    mounts:
      - storage: database
        location: /var/lib/grafana

storage:
  database:
    type: filesystem

requires:
  grafana-source:
    interface: grafana_datasource
    optional: true
  grafana-dashboard:
    interface: grafana_dashboard
    optional: true
  grafana-auth:
    interface: grafana_auth
    optional: true
  pgsql:
    interface: postgresql_client
    limit: 1
    optional: true
    description: |
      This endpoint allows using a PostgreSQL database backend for data storage.
      Using this endpoint overrides Grafana's usage of the embedded sqlite3 database
      for data storage and is required for more than one Grafana unit.
  catalogue:
    interface: catalogue
    optional: true
  ingress:
    interface: ingress
    limit: 1
    optional: true
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 14s</sub>

### ✅ `bash`

**Explore source structure**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && ls src/ && echo "---" && ls tests/

```
charm.py      custom_ini_config.py  grafana_client.py  models.py	       relation.py	  self_dashboard.json
constants.py  grafana.py	    grafana_config.py  prometheus_alert_rules  secret_storage.py
---
integration  manual  scenario  unit
<exited with exit code 0>
```


---

<sub>⏱️ 22s</sub>

### ✅ `bash`

**Check installed ops version**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && pip show ops 2>/dev/null | grep Version && python -c "import ops; print(ops.__version__)" 2>/dev/null || echo "ops not installed in current env"

```
Version: 3.7.0
ops not installed in current env
<exited with exit code 0>
```


---

<sub>⏱️ 22s</sub>

### ✅ `bash`

**Check latest ops version on PyPI**

$ pip index versions ops 2>/dev/null | head -5 || pip install ops --dry-run 2>&1 | head -10

```
ops (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 2.20.0, 2.19.4, 2.19.0, 2.18.1, 2.18.0, 2.17.1, 2.17.0, 2.16.1, 2.16.0, 2.15.0, 2.14.1, 2.14.0, 2.13.0, 2.12.0, 2.11.0, 2.10.0, 2.9.0, 2.8.0, 2.7.0, 2.6.0, 2.5.1, 2.5.0, 2.4.1, 2.4.0, 2.3.0, 2.2.0, 2.1.1, 2.1.0, 2.0.0, 1.5.5, 1.5.4, 1.5.3, 1.5.2, 1.5.1, 1.5.0, 1.4.0, 1.3.0, 1.2.0, 1.1.0, 1.0.1, 1.0.0, 0.10.0, 0.9.0, 0.8.0, 0.7.0, 0.6.1, 0.6.0, 0.4.7, 0.4.6, 0.4.5, 0.4.4, 0.4.3, 0.4.2, 0.2.1, 0.2.0, 0.1.0
  INSTALLED: 3.7.0
  LATEST:    3.7.0
<exited with exit code 0>
```


---

<sub>⏱️ 31s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/releases",
  "max_length": 10000
}
```

</details>

<details>
<summary>102 lines</summary>

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
*   Remove comments from K8s tutorial and clarify about persisting data in [#2253](https:

<note>Content truncated. Call the fetch tool with a start_index of 10000 to get more content.</note>
```

</details>


---

<sub>⏱️ 29s</sub>

### ✅ `bash`

**Look at main charm file**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat src/charm.py | head -100

<details>
<summary>92 lines</summary>

```
#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Copyright 2021 Canonical Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""A Kubernetes charm for Grafana."""

import logging
import os
import socket
import subprocess
from pathlib import Path
from typing import Any, Dict, cast, Optional
from urllib.parse import urlparse

from cosl import JujuTopology
from cosl.reconciler import all_events, observe_events
from ops import ActiveStatus, BlockedStatus, CollectStatusEvent, RelationBrokenEvent, StatusBase, main
from ops.charm import (
    ActionEvent,
    CharmBase,
    RelationChangedEvent,
)
from ops.model import Port
from secret_storage import SecretStorage

from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
from charms.certificate_transfer_interface.v1.certificate_transfer import (
    CertificateTransferRequires,
)
from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
from charms.grafana_k8s.v0.grafana_auth import AuthRequirer, AuthRequirerCharmEvents
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardConsumer
from charms.grafana_k8s.v0.grafana_metadata import GrafanaMetadataProvider
from charms.grafana_k8s.v0.grafana_source import (
    GrafanaSourceConsumer,
)
from charms.hydra.v0.oauth import (
    ClientConfig as OauthClientConfig,
    OAuthRequirer,
    OauthProviderConfig
)
from charms.istio_beacon_k8s.v0.service_mesh import UnitPolicy, ServiceMeshConsumer
from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
    KubernetesComputeResourcesPatch,
    ResourceRequirements,
    adjust_resource_requirements,
)
from charms.parca_k8s.v0.parca_scrape import ProfilingEndpointProvider
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer
from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer, IngressPerAppReadyEvent, IngressPerAppRevokedEvent
from grafana import Grafana
from grafana_client import GrafanaClient, GrafanaCommError
from grafana_config import GrafanaConfig
from secret_storage import generate_password
from relation import Relation
from models import DatasourceConfig, PebbleEnvironment, TLSConfig
from charms.tls_certificates_interface.v4.tls_certificates import (
    CertificateRequestAttributes,
    TLSCertificatesRequiresV4,
    CertificateAvailableEvent,
)
from constants import (
    PEER_RELATION,
    WORKLOAD_PORT,
    OAUTH_SCOPES,
    CA_CERT_PATH,
    GRAFANA_WORKLOAD,
    PGSQL_RELATION,
    PROFILING_PORT,
    OAUTH_GRANT_TYPES,
    VALID_AUTHENTICATION_MODES,
    METRICS_PATH)
import ops_tracing

logger = logging.getLogger()


class GrafanaCharm(CharmBase):
    """Charm to run Grafana on Kubernetes.

    This charm allows for high-availability
    (as long as a non-sqlite database relation is present).

    Developers of this charm should be aware of the Grafana provisioning docs:
    https://grafana.com/docs/grafana/latest/administration/provisioning/
    """
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 38s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/releases",
  "start_index": 10000
}
```

</details>

<details>
<summary>95 lines</summary>

```
Contents of https://github.com/canonical/operator/releases:
//github.com/canonical/operator/pull/2253)
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

<sub>⏱️ 38s</sub>

### ✅ `bash`

**Read rest of charm.py**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat src/charm.py | wc -l && cat src/charm.py | tail -600

<details>
<summary>24 lines</summary>

```
Output too large to read at once (24.3 KB). Saved to: /tmp/copilot-tool-output-1775171131682-2mnzar.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
668
from relation import Relation
from models import DatasourceConfig, PebbleEnvironment, TLSConfig
from charms.tls_certificates_interface.v4.tls_certificates import (
    CertificateRequestAttributes,
    TLSCertificatesRequiresV4,
    CertificateAvailableEvent,
)
from constants import (
    PEER_RELATION,
    WORKLOAD_PORT,
    OAUTH_SCOPES,
    CA_CERT_PATH,
    GRAFANA_WORKLOAD,
    PGSQL_RELATION,
    PROFILING_PORT,
    OAUTH_GRANT_TYPES,
    VALID_AUTHENTICATION_MODES,
    METRICS_PATH)
i
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 44s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "start_index": 20000,
  "url": "https://github.com/canonical/operator/releases"
}
```

</details>

<details>
<summary>97 lines</summary>

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

*   Update referenced examples for managing interfaces in [#2068](h

<note>Content truncated. Call the fetch tool with a start_index of 30000 to get more content.</note>
```

</details>


---

<sub>⏱️ 45s</sub>

### ✅ `bash`

**Scan charm.py for key patterns**

$ cat /tmp/copilot-tool-output-1775171131682-2mnzar.txt | grep -n "def \|class \|CollectStatus\|secret\|Secret\|Port\|pebble\|Pebble\|tracing\|Tracing" | head -60

<details>
<summary>61 lines</summary>

```
3:from models import DatasourceConfig, PebbleEnvironment, TLSConfig
20:import ops_tracing
25:class GrafanaCharm(CharmBase):
35:    def __init__(self, *args):
42:        self._secret_storage = SecretStorage(self, "admin-password",
86:                self.on.grafana_pebble_ready,  # pyright: ignore
90:        self.charm_tracing = TracingEndpointRequirer(
91:            self, relation_name="charm-tracing", protocols=["otlp_http"]
93:        self.workload_tracing = TracingEndpointRequirer(
94:            self, relation_name="workload-tracing", protocols=["otlp_grpc"]
123:            refresh_event=self.on.grafana_pebble_ready,  # pyright: ignore
144:                                            tracing_endpoint=self._workload_tracing_endpoint,
151:                                        pebble_env=self._pebble_env,
195:    def _scheme(self) -> str:
199:    def internal_url(self) -> str:
204:    def external_url(self) -> str:
209:    def _metrics_scrape_jobs(self) -> list:
219:    def _profiling_scrape_jobs(self) -> list:
225:    def _trusted_ca_certs(self) -> Optional[str]:
231:    def unique_name(self):
241:    def _catalogue_item(self) -> CatalogueItem:
262:    def _workload_tracing_endpoint(self) -> Optional[str]:
263:        if self.workload_tracing.is_ready():
264:            endpoint = self.workload_tracing.get_endpoint("otlp_grpc")
269:    def _datasource_config(self) -> DatasourceConfig:
276:    def _pebble_env(self) -> PebbleEnvironment:
278:        tracing_resource_attrs = ((f"juju_application={topology.application},juju_model={topology.model}" + \
280:                            if self._workload_tracing_endpoint
282:        return PebbleEnvironment(
289:            tracing_resource_attributes=tracing_resource_attrs,
295:    def _provision_own_dashboard(self) -> bool:
304:    def _enable_external_db(self) -> bool:
309:    def _db_config(self) -> Optional[Dict[str, str]]:
318:    def _oauth_client_config(self) -> OauthClientConfig:
326:    def _oauth_config(self) -> Optional[OauthProviderConfig]:
332:    def _auth_env_vars(self):
336:    def _tls_config(self) -> Optional[TLSConfig]:
348:    def _tls_available(self) -> bool:
352:    def admin_password(self) -> Optional[str]:
354:        contents = self._secret_storage.contents
359:    def _reconcile(self):
366:        if self.charm_tracing.is_ready() and (endpoint:= self.charm_tracing.get_endpoint("otlp_http")):
367:            ops_tracing.set_destination(
378:    def _check_wrong_relations(self) -> Optional[StatusBase]:
386:    def _reconcile_tls_config(self) -> None:
401:    def _reconcile_relations(self):
409:    def _reconcile_grafana_metadata(self):
432:    def _on_collect_unit_status(self, e: CollectStatusEvent):
440:    def _on_database_changed(self, event: RelationChangedEvent) -> None:
468:    def _on_database_broken(self, _: RelationBrokenEvent) -> None:
473:        to the Pebble container.
487:    class GetAdminPWDFailures:
495:    def _on_get_admin_password(self, event: ActionEvent):
540:    def _on_grafana_auth_conf_available(self, event: AuthRequirerCharmEvents):
559:    def _on_grafana_source_changed(self, _) -> None:
563:    def _generate_auth_env_vars(self, conf: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
581:    def _set_ports(self):
583:        planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
586:        # Ports may change across an upgrade, so need to sync
595:    def _resource_reqs_from_config(self) -> ResourceRequirements:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 52s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "start_index": 30000,
  "url": "https://github.com/canonical/operator/releases"
}
```

</details>

<details>
<summary>23 lines</summary>

```
Contents of https://github.com/canonical/operator/releases:
ttps://github.com/canonical/operator/pull/2068)
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

<sub>⏱️ 53s</sub>

### ✅ `bash`

**Look at key methods in charm**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat src/charm.py | grep -A 20 "def _set_ports\|def _reconcile\b\|def _on_collect\|def admin_password"

<details>
<summary>63 lines</summary>

```
def admin_password(self) -> Optional[str]:
        """The admin password."""
        contents = self._secret_storage.contents
        if not contents:
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
        if self._check_wrong_relations():
            return
        self._reconcile_relations()
        self._grafana_service.reconcile()
        self._reconcile_tls_config()

    def _check_wrong_relations(self) -> Optional[StatusBase]:
        """Check that relations are configured properly."""
--
    def _on_collect_unit_status(self, e: CollectStatusEvent):
        e.add_status(ActiveStatus())
        if status := self._check_wrong_relations():
            e.add_status(status)
        e.add_status(self.resource_patch.get_status())
        e.add_status(self._grafana_config.get_status())


    def _on_database_changed(self, event: RelationChangedEvent) -> None:
        """Sets configuration information for database connection.

        Args:
            event: A :class:`RelationChangedEvent` from a `database` source
        """
        if not self.unit.is_leader():
            return

        if self._enable_external_db and self._db is not None:
            # fetch_relation_data() returns a dict of {relation_id: {values}}. Since there is only one db relation, we can
            # just take the 0 element
            data = list(self._db.fetch_relation_data().values())[0]
--
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


---

<sub>⏱️ 1m 1s</sub>

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

<sub>⏱️ 1m 2s</sub>

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

<sub>⏱️ 1m 6s</sub>

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

<sub>⏱️ 1m 6s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.0.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
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

<sub>⏱️ 1m 13s</sub>

### 💬 Copilot

Now let me check the ops-tracing and ops-scenario releases, and look at more of the charm code:

---

<sub>⏱️ 1m 14s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/2.23.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/releases/tag/2.23.0"
}
```

</details>

<details>
<summary>49 lines</summary>

```
Contents of https://github.com/canonical/operator/releases/tag/2.23.0:
This release introduces enhancements focused on improving developer experience and code reliability. Key features include support for defining configuration, action, and relation data schemas using Python classes, streamlining data validation and reducing boilerplate. The release also enhanced testing and tracing capabilities, such as improved access to trace data and utilities for creating testing states, alongside several bug fixes addressing issues in relation handling, OpenTelemetry integration, and testing mocks.

This is the last feature release in the 2.x series, with only security and critical bugfixes in the future. Ops 3 will not support Python 3.8 and Ubuntu 20.04. Otherwise, Ops 3 will be backwards compatible with Ops 2.

## What's Changed

### Features

*   Support for config schema as Python classes in [#1741](https://github.com/canonical/operator/pull/1741)
*   Support for action parameter schema as Python classes in [#1756](https://github.com/canonical/operator/pull/1756)
*   Ops\[tracing\] compatibility with jhack in [#1806](https://github.com/canonical/operator/pull/1806)
*   Support for relation data schema as Python classes in [#1701](https://github.com/canonical/operator/pull/1701)
*   Add CheckInfo.successes field and .has\_run property in [#1819](https://github.com/canonical/operator/pull/1819)
*   Provide a method to create a testing.State from a testing.Context in [#1797](https://github.com/canonical/operator/pull/1797)
*   Expose trace data in testing in [#1842](https://github.com/canonical/operator/pull/1842)
*   Add a helper to generate a Layer from rockcraft.yaml in [#1831](https://github.com/canonical/operator/pull/1831)

### Fixes

*   Correctly load an empty Juju config options map in [#1778](https://github.com/canonical/operator/pull/1778)
*   Fix type annotation of container check\_infos in ops.testing in [#1784](https://github.com/canonical/operator/pull/1784)
*   Restrict the version of a dependency, opentelemetry-sdk in [#1794](https://github.com/canonical/operator/pull/1794)
*   Remote unit data is available in relation-departed in [#1364](https://github.com/canonical/operator/pull/1364)
*   Juju allows access to the remote app databag in relation-broken, so Harness should too in [#1787](https://github.com/canonical/operator/pull/1787)
*   Don't use private OpenTelemetry API in [#1798](https://github.com/canonical/operator/pull/1798)
*   Do not return this unit in a mocked peer relation in [#1828](https://github.com/canonical/operator/pull/1828)
*   Testing.PeerRelation properly defaults to no peers in [#1832](https://github.com/canonical/operator/pull/1832)
*   In meter-status-changed JUJU\_VERSION is not set in [#1840](https://github.com/canonical/operator/pull/1840)
*   Only provide the units belonging to the app in Relation.units in [#1837](https://github.com/canonical/operator/pull/1837)

### Documentation

*   Remove two best practices, and drop two to tips in [#1758](https://github.com/canonical/operator/pull/1758)
*   Update link to Charmcraft for managing app config in [#1763](https://github.com/canonical/operator/pull/1763)
*   Update link to Juju documentation for setting up deployment in [#1781](https://github.com/canonical/operator/pull/1781)
*   Fix external OTLP link in [#1786](https://github.com/canonical/operator/pull/1786)
*   Distribute the ops-scenario README content across the ops docs in [#1773](https://github.com/canonical/operator/pull/1773)
*   Improve testing.errors.UncaughtCharmError message in [#1795](https://github.com/canonical/operator/pull/1795)
*   In the "manage the charm version" how-to, give an example of using override-build in [#1802](https://github.com/canonical/operator/pull/1802)
*   Small adjustments to the 'how to trace charm code' doc in [#1792](https://github.com/canonical/operator/pull/1792)
*   Replace Harness example and fix links in README in [#1820](https://github.com/canonical/operator/pull/1820)
*   Add httpbin charm from Charmcraft as an example charm in [#1743](https://github.com/canonical/operator/pull/1743)
*   Fix on\_collect mistake in sample code in [#1829](https://github.com/canonical/operator/pull/1829)
*   Update code in K8s tutorial, with source in repo (part 2) in [#1734](https://github.com/canonical/operator/pull/1734)
*   Update Loki section on charming zero-to-hero tutorial in [#1847](https://github.com/canonical/operator/pull/1847)
*   Remove expandable boxes of text in [#1844](https://github.com/canonical/operator/pull/1844)
*   Improve httpbin charm by removing defer() and adding collect\_status in [#1833](https://github.com/canonical/operator/pull/1833)
*   Move {posargs} to the end of pytest command lines in tox.ini in [#1854](https://github.com/canonical/operator/pull/1854)

### CI

*   Install the ops\[tracing\] dependencies for the TIOBE action in [#1761](https://github.com/canonical/operator/pull/1761)
*   Add ops-scenario and ops-tracing as explicit installs for TIOBE in [#1764](https://github.com/canonical/operator/pull/1764)
*   Persist credentials for update-charm-pins workflow in [#1766](https://github.com/canonical/operator/pull/1766)
*   Stop smoke testing Charmcraft 2 in [#1782](https://github.com/canonical/operator/pull/1782)
*   Use Charmcraft 3.x for smoke testing 20.04 and 22.04 in [#1821](https://github.com/canonical/operator/pull/1821)
*   Enable xdist for the 'unit' tox environments in [#1830](https://github.com/canonical/operator/pull/1830)

**Full Changelog**: [2.22.0...2.23.0](https://github.com/canonical/operator/compare/2.22.0...2.23.0)
```

</details>


---

<sub>⏱️ 1m 15s</sub>

### ✅ `bash`

**Check ops-tracing version**

$ pip show ops-tracing 2>/dev/null | grep -E "Version|Location" && pip index versions ops-tracing 2>/dev/null | head -3

<details>
<summary>6 lines</summary>

```
Version: 3.7.0
Location: /home/ubuntu/.local/lib/python3.12/site-packages
ops-tracing (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 0.9.6, 0.9.4, 0.9.3, 0.9.2, 0.9.1, 0.9.0
  INSTALLED: 3.7.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 34s</sub>

### 💬 Copilot

Let me look at the tests, config schemas, and other relevant parts:

---

<sub>⏱️ 1m 34s</sub>

### ✅ `bash`

**Look at test directory structure**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && ls tests/scenario/ && ls tests/unit/

<details>
<summary>10 lines</summary>

```
test_admin_password.py
conftest.py		     test_config_reporting_enabled.py  test_grafana_client.py
dashboard_templates	     test_custom_ini_config.py	       test_grafana_metadata_implementation.py
helpers.py		     test_dashboard_collision.py       test_grafana_metadata_lib.py
manual_dashboards	     test_dashboard_consumer.py        test_oauth.py
test_auth_proxy_provider.py  test_dashboard_provider.py        test_source_consumer.py
test_auth_requirer.py	     test_dashboard_transform.py       test_source_provider.py
test_charm.py		     test_datasources.py
test_charmed_dashboard.py    test_external_url.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 34s</sub>

### ✅ `bash`

**Look at config options in charmcraft.yaml**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat charmcraft.yaml | grep -A 200 "^config:" | head -100

<details>
<summary>88 lines</summary>

```
config:
  options:
    allow_anonymous_access:
      type: boolean
      default: false
      description: |
        Whether Grafana should allow anonymous access to dashboards. Unless
        you have some other authentication mechanism in front of your deployment,
        you likely do not want to enable this.
    allow_embedding:
      type: boolean
      default: false
      description: |
        Whether Grafana should allow embedding dashboards using iframes. Unless
        you have a clear reason for doing so, you likely do not want to enable this.
    log_level:
      type: string
      description: |
        Logging level for Grafana. Options are “debug”, “info”,
        “warn”, “error”, and “critical”.
      default: info
    admin_user:
      description: The Grafana administrative user
      type: string
      default: admin
    web_external_url:
      description: |
        DEPRECATED. This config option is no longer used, in favor of "skipPrefix".

        The URL under which Grafana is externally reachable (for example,
        if Grafana is served via a reverse proxy).

        Used for generating relative and absolute links back to
        Grafana itself. If the URL has a path portion, it will be used to
        prefix all HTTP endpoints served by Grafana.

        If omitted, relevant URL components will be derived automatically.

        If provided, this should be a complete URI, including scheme, or a
        fully qualified subpath starting with `/`.

        If Grafana is being served directly from the root of a fully-qualified
        host or a bare A record, this may be omitted.
      type: string
      default: ""
    enable_auto_assign_org:
      description: |
        Set to true to automatically add new users to the main organization (id 1). When set to
        false, new users automatically cause a new organization to be created for that new user.
      type: boolean
      default: true
    datasource_query_timeout:
      description: |
        The default timeout for querying a Grafana datasource. Each datasource can
        also configure its own preferred timeout value through relation data. If the
        value configured through relation data is larger than datasource_query_timeout
        then that value is left unchanged. The value of this configuration option must
        be a positive integer representing the maximum number of seconds Grafana will
        wait for a datasource to respond to a query.
      type: int
      default: 300
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
    reporting_enabled:
      description: |
        When disabled, Grafana will be configured to not send anonymous usage statistics to stats.grafana.org, nor
        periodically check for updates.
        It is very helpful to the Grafana project, so please leave this enabled.
        
        When enabled, Grafana will use its default values for analytics.
        
        Ref: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#analytics
      type: boolean
      default: true
    custom_config:
      type: string
      description: |
        Additional configuration options to be added to grafana.ini.
        These options will be appended to the grafana.ini file, allowing for custom configuration.
        Note that this config option accepts only a small subset of the grafana.ini file.
        Currently supported sections:
        - [smtp], ref: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#smtp
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 40s</sub>

### ✅ `bash`

**Look at scenario test conftest**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat tests/scenario/conftest.py

```
cat: tests/scenario/conftest.py: No such file or directory
<exited with exit code 1>
```


---

<sub>⏱️ 1m 40s</sub>

### ✅ `bash`

**Look at test files**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && head -80 tests/scenario/test_admin_password.py && echo "---" && head -60 tests/unit/test_charm.py

<details>
<summary>114 lines</summary>

```
import re
from contextlib import ExitStack, contextmanager
from unittest.mock import patch, PropertyMock

import pytest
from ops import testing

from charm import GrafanaCharm, generate_password


@contextmanager
def grafana_ready(ready: bool):
    with patch("grafana_client.Grafana.is_ready", PropertyMock(return_value=ready)):
        yield


@contextmanager
def password_changed(changed: bool):
    with patch("grafana_client.Grafana.password_has_been_changed", return_value=changed):
        yield


@pytest.fixture(autouse=True)
def patch_all():
    with ExitStack() as stack:
        for p in [
            patch("lightkube.core.client.GenericSyncClient"),
            patch("socket.getfqdn", new=lambda *args: "grafana-k8s-0.testmodel.svc.cluster.local"),
            patch("socket.gethostbyname", new=lambda *args: "1.2.3.4"),
            patch.multiple(
                "charm.KubernetesComputeResourcesPatch",
                _namespace="test-namespace",
                _patch=lambda *a, **kw: True,
                is_ready=lambda *a, **kw: True,
            ),
            patch.object(GrafanaCharm, "grafana_version", "0.1.0"),
        ]:
            stack.enter_context(p)

        yield


@pytest.fixture
def ctx():
    return testing.Context(GrafanaCharm)


def test_generate_password():
    # run this test some 1000 times since generate_password is stochastic
    for n in range(1000):
        pwd = generate_password()
        assert len(pwd) == 12
        assert re.match(r"[A-Za-z0-9]{12}", pwd)


def test_can_get_password(ctx):
    # GIVEN a grafana leader unit
    state = testing.State(leader=True)

    # WHEN we receive any hook
    with ctx(ctx.on.update_status(), state) as mgr:
        # THEN the .admin_password attribute returns something
        pwd = mgr.charm.admin_password
        state_out = mgr.run()

    # AND THEN the output state contains a secret with the expected contents
    assert len(state_out.secrets) == 1
    secret = list(state_out.secrets)[0]
    assert pwd, "password is empty"
    assert secret.latest_content['password'] == pwd


@pytest.mark.parametrize("leader", (True, False))
def test_action_happy_path(ctx, leader):
    # GIVEN a grafana unit with the secret created already
    pwd = "abcde"
    state = testing.State(leader=leader, secrets={
        testing.Secret(tracked_content={"password": pwd}, label="admin-password")})

    # WHEN we run the get-admin-password action
---
# Copyright 2020 Canonical Ltd.
# See LICENSE file for licensing details.

from dataclasses import replace
import json
from unittest.mock import patch

from pytest import mark
import yaml
from ops.testing import (Relation,
                        Context,
                        Model,
                        Network,
                        BindAddress,
                        Address,
                        CharmEvents,
                        PeerRelation,
                        Secret,
                        State)

import src.grafana_client as grafana_client
from src.constants import CONFIG_PATH, DATASOURCES_PATH, PROVISIONING_PATH

MINIMAL_DATASOURCES_CONFIG = {
    "apiVersion": 1,
    "datasources": [],
    "deleteDatasources": [],
}

BASIC_DATASOURCES = [
    {
        "access": "proxy",
        "isDefault": "false",
        "name": "juju_test-model_abcdef_prometheus_0",
        "orgId": "1",
        "type": "prometheus",
        "url": "http://1.2.3.4:1234",
        "jsonData": {"timeout": 300},
    }
]

SOURCE_DATA = {
    "model": "test-model",
    "model_uuid": "abcdef",
    "application": "prometheus",
    "type": "prometheus",
}

DASHBOARD_CONFIG = {
    "apiVersion": 1,
    "providers": [
        {
            "name": "Default",
            "updateIntervalSeconds": "5",
            "type": "file",
            "options": {"path": "/etc/grafana/provisioning/dashboards"},
        }
    ],
}
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 46s</sub>

### ✅ `bash`

**Look at scenario tests**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && ls tests/scenario/ && head -80 tests/scenario/test_admin_password.py

<details>
<summary>62 lines</summary>

```
test_admin_password.py
import re
from contextlib import ExitStack, contextmanager
from unittest.mock import patch, PropertyMock

import pytest
from ops import testing

from charm import GrafanaCharm, generate_password


@contextmanager
def grafana_ready(ready: bool):
    with patch("grafana_client.Grafana.is_ready", PropertyMock(return_value=ready)):
        yield


@contextmanager
def password_changed(changed: bool):
    with patch("grafana_client.Grafana.password_has_been_changed", return_value=changed):
        yield


@pytest.fixture(autouse=True)
def patch_all():
    with ExitStack() as stack:
        for p in [
            patch("lightkube.core.client.GenericSyncClient"),
            patch("socket.getfqdn", new=lambda *args: "grafana-k8s-0.testmodel.svc.cluster.local"),
            patch("socket.gethostbyname", new=lambda *args: "1.2.3.4"),
            patch.multiple(
                "charm.KubernetesComputeResourcesPatch",
                _namespace="test-namespace",
                _patch=lambda *a, **kw: True,
                is_ready=lambda *a, **kw: True,
            ),
            patch.object(GrafanaCharm, "grafana_version", "0.1.0"),
        ]:
            stack.enter_context(p)

        yield


@pytest.fixture
def ctx():
    return testing.Context(GrafanaCharm)


def test_generate_password():
    # run this test some 1000 times since generate_password is stochastic
    for n in range(1000):
        pwd = generate_password()
        assert len(pwd) == 12
        assert re.match(r"[A-Za-z0-9]{12}", pwd)


def test_can_get_password(ctx):
    # GIVEN a grafana leader unit
    state = testing.State(leader=True)

    # WHEN we receive any hook
    with ctx(ctx.on.update_status(), state) as mgr:
        # THEN the .admin_password attribute returns something
        pwd = mgr.charm.admin_password
        state_out = mgr.run()

    # AND THEN the output state contains a secret with the expected contents
    assert len(state_out.secrets) == 1
    secret = list(state_out.secrets)[0]
    assert pwd, "password is empty"
    assert secret.latest_content['password'] == pwd


@pytest.mark.parametrize("leader", (True, False))
def test_action_happy_path(ctx, leader):
    # GIVEN a grafana unit with the secret created already
    pwd = "abcde"
    state = testing.State(leader=leader, secrets={
        testing.Secret(tracked_content={"password": pwd}, label="admin-password")})

    # WHEN we run the get-admin-password action
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 46s</sub>

### ✅ `bash`

**Check Context usage in tests**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -r "charm_spec\|Context(" tests/ | grep -v "Binary\|#" | head -30

<details>
<summary>7 lines</summary>

```
tests/unit/test_datasources.py:    ctx = Context(MyProviderCharm, MyProviderCharm.META)
tests/unit/test_datasources.py:    ctx = Context(MyProviderCharm, MyProviderCharm.META)
tests/unit/conftest.py:    yield Context(GrafanaCharm)
tests/unit/test_grafana_metadata_lib.py:    return Context(charm_type=GrafanaMetadataProviderCharm, meta=GrafanaMetadataProviderCharm.META)
tests/unit/test_grafana_metadata_lib.py:    return Context(charm_type=GrafanaMetadataRequirerCharm, meta=GrafanaMetadataRequirerCharm.META)
tests/scenario/test_admin_password.py:    return testing.Context(GrafanaCharm)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 53s</sub>

### ✅ `bash`

**Look at unit test conftest and tox.ini**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat tests/unit/conftest.py && echo "===" && grep -r "SCENARIO_BARE_CHARM_ERRORS\|tox.ini" tox.ini 2>/dev/null | head -20

<details>
<summary>53 lines</summary>

```
from unittest.mock import MagicMock, patch

from ops import ActiveStatus
from ops.testing import PeerRelation, Container, State, Exec

import pytest
from ops.testing import Context

from charm import GrafanaCharm
from grafana import Grafana


GRAFANA_FQDN = "grafana-k8s-0.testmodel.svc.cluster.local"

def tautology(*_, **__) -> bool:
    return True



@pytest.fixture
def ctx():
    patches = (
        patch("grafana.Grafana._push_sqlite_static", new=lambda _: None),
        patch("lightkube.core.client.GenericSyncClient"),
        patch("socket.getfqdn", new=lambda *args: GRAFANA_FQDN),
        patch("socket.gethostbyname", new=lambda *args: "1.2.3.4"),
        patch.multiple(
            "charm.KubernetesComputeResourcesPatch",
            _namespace="test-namespace",
            _patch=tautology,
            get_status=MagicMock(return_value=ActiveStatus()),
            is_ready=tautology,
        ),
        patch.object(Grafana, "grafana_version", "0.1.0"),
    )
    for p in patches:
        p.__enter__()

    yield Context(GrafanaCharm)

    for p in patches:
        p.__exit__(None, None, None)

@pytest.fixture
def peer_relation():
    return PeerRelation("grafana")

@pytest.fixture(scope="function")
def grafana_container():
    return Container(
        "grafana",
        can_connect=True,
        execs={Exec(("update-ca-certificates", "--fresh"))}
    )


@pytest.fixture
def containers(grafana_container):
    return {grafana_container}

@pytest.fixture
def base_state(containers, peer_relation):
    return State(
        leader=True,
        containers=containers,
        relations={peer_relation},
    )
===
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 53s</sub>

### ✅ `bash`

**Look at tox.ini**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat tox.ini

<details>
<summary>59 lines</summary>

```
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
[tox]
skipsdist=True
skip_missing_interpreters = True
envlist = lint, static, unit

[vars]
src_path = {toxinidir}/src
tst_path = {toxinidir}/tests
lib_path = {toxinidir}/lib/charms/grafana_k8s
all_path = {[vars]src_path} {[vars]tst_path} {[vars]lib_path}
uv_flags = --frozen --isolated --extra=dev

[testenv]
allowlist_externals = uv
basepython = python3
setenv =
  PYTHONPATH = {toxinidir}:{toxinidir}/lib:{[vars]src_path}
  PYTHONBREAKPOINT=ipdb.set_trace
  PY_COLORS=1
passenv =
  PYTHONPATH
  CHARM_PATH

[testenv:lock]
description = Update uv.lock with the latest deps
commands =
  uv lock --upgrade --no-cache

[testenv:lint]
description = Lint the code
commands =
    uv run {[vars]uv_flags} ruff check {[vars]all_path}

[testenv:static]
description = Run static checks
allowlist_externals =
  {[testenv]allowlist_externals}
  /usr/bin/env
commands =
    uv run {[vars]uv_flags} pyright {[vars]all_path}
    /usr/bin/env sh -c 'for m in $(git diff main --name-only {[vars]lib_path}); do if ! git diff main $m | grep -q "+LIBPATCH\|+LIBAPI"; then echo "You forgot to bump the version on $m!"; exit 1; fi; done'

[testenv:fmt]
description = "Format the code"
commands =
    uv run {[vars]uv_flags} ruff check --fix-only {[vars]all_path}

[testenv:unit]
description = Run unit tests
allowlist_externals =
  {[testenv]allowlist_externals}
  /usr/bin/env
commands =
    /usr/bin/env sh -c 'stat sqlite-static > /dev/null 2>&1 || curl -L https://github.com/CompuRoot/static-sqlite3/releases/latest/download/sqlite3 -o sqlite-static && chmod +x sqlite-static'
    /usr/bin/env sh -c 'stat cos-tool-amd64 > /dev/null 2>&1 || curl -L -O https://github.com/canonical/cos-tool/releases/latest/download/cos-tool-amd64 && chmod 755 cos-tool-amd64'
    uv run {[vars]uv_flags} coverage run --source={[vars]src_path},{[vars]lib_path} -m pytest \
        {[vars]tst_path}/unit {posargs}
    uv run {[vars]uv_flags} coverage report

[testenv:integration]
description = Run integration tests
commands =
    uv run {[vars]uv_flags} playwright install
    uv run {[vars]uv_flags} pytest --exitfirst {[vars]tst_path}/integration {posargs}
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 2s</sub>

### ✅ `bash`

**Look at actions in charmcraft.yaml**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat charmcraft.yaml | grep -A 50 "^actions:"

<details>
<summary>46 lines</summary>

```
actions:
  get-admin-password:
    description: |
      Get the dashboard url and initial admin password for the Grafana web interface. Initial
      admin password is generated at charm deployment time. If the password has been changed,
      a notice of that fact will be returned by this action instead.

config:
  options:
    allow_anonymous_access:
      type: boolean
      default: false
      description: |
        Whether Grafana should allow anonymous access to dashboards. Unless
        you have some other authentication mechanism in front of your deployment,
        you likely do not want to enable this.
    allow_embedding:
      type: boolean
      default: false
      description: |
        Whether Grafana should allow embedding dashboards using iframes. Unless
        you have a clear reason for doing so, you likely do not want to enable this.
    log_level:
      type: string
      description: |
        Logging level for Grafana. Options are “debug”, “info”,
        “warn”, “error”, and “critical”.
      default: info
    admin_user:
      description: The Grafana administrative user
      type: string
      default: admin
    web_external_url:
      description: |
        DEPRECATED. This config option is no longer used, in favor of "skipPrefix".

        The URL under which Grafana is externally reachable (for example,
        if Grafana is served via a reverse proxy).

        Used for generating relative and absolute links back to
        Grafana itself. If the URL has a path portion, it will be used to
        prefix all HTTP endpoints served by Grafana.

        If omitted, relevant URL components will be derived automatically.

        If provided, this should be a complete URI, including scheme, or a
        fully qualified subpath starting with `/`.

        If Grafana is being served directly from the root of a fully-qualified
        host or a bare A record, this may be omitted.
      type: string
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 2s</sub>

### ✅ `bash`

**Check config usage in charm**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -n "model.config\|self.config\[" src/charm.py | head -30

<details>
<summary>10 lines</summary>

```
209:                                            enable_reporting = bool(self.config["reporting_enabled"]),
340:            query_timeout=int(self.model.config.get("datasource_query_timeout", 0)),
351:            log_level=str(self.model.config["log_level"]),
352:            allow_embedding=bool(self.model.config["allow_embedding"]),
353:            allow_anonymous_access=bool(self.model.config["allow_anonymous_access"]),
354:            enable_auto_assign_org=bool(self.model.config["enable_auto_assign_org"]),
358:            admin_user = str(self.model.config["admin_user"]),
579:                cast(str, self.model.config["admin_user"]), admin_password
663:        limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 9s</sub>

### ✅ `bash`

**Look at grafana_config.py**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat src/grafana_config.py | head -100

<details>
<summary>85 lines</summary>

```
# Copyright 2025 Canonical
# See LICENSE file for licensing details.
"""Grafana config generator."""

import logging
import yaml
from models import DatasourceConfig
from typing import Callable, Optional, Dict, Any
from charms.hydra.v0.oauth import (
    OauthProviderConfig
)
from ops import ActiveStatus, BlockedStatus
from constants import DATABASE_PATH, DASHBOARDS_DIR
import configparser
from io import StringIO

import custom_ini_config


logger = logging.getLogger()


class GrafanaConfig:
    """Grafana config generator."""

    def __init__(self,
                datasources_config: DatasourceConfig,
                oauth_config: Optional[OauthProviderConfig] = None,
                auth_env_config: Callable[[],Any] = lambda: {},
                db_config: Callable[[],Optional[Dict[str, str]]]  = lambda: None,
                db_type: str = "",
                enable_reporting: bool = True,
                enable_external_db: bool = False,
                tracing_endpoint: Optional[str] = None,
                custom_config: Optional[str] = None,
                 ):
        self._datasources_config = datasources_config
        self._oauth_config = oauth_config
        self._auth_env_config = auth_env_config
        self._db_config = db_config
        self._db_type = db_type
        self._enable_reporting = enable_reporting
        self._enable_external_db = enable_external_db
        self._tracing_endpoint = tracing_endpoint
        self._custom_config = custom_config


    @property
    def oauth_config(self) -> Optional[OauthProviderConfig]:
        """Generate oauth config."""
        return self._oauth_config

    @property
    def auth_env_config(self) -> Any:
        """Generate auth environment config."""
        return self._auth_env_config()

    def get_status(self):
        """Intended to be called by collect-unit-status."""
        try:
            custom_ini_config.validate(self._custom_config)
        except ValueError as e:
            logger.error("Invalid custom_config: %s", e)
            return BlockedStatus("Invalid custom_config; see debug-log")
        return ActiveStatus()

    def generate_grafana_config(self) -> str:
        """Generate a configuration for Grafana."""
        configs = [self._generate_tracing_config(), self._generate_analytics_config(), self._generate_database_config()]
        if self._custom_config is not None:
            try:
                custom_ini_config.validate(self._custom_config)
            except ValueError:
                pass
            else:
                configs.append(self._custom_config)

        if not self._enable_external_db:
            with StringIO() as data:
                config_ini = configparser.ConfigParser()
                config_ini["database"] = {
                    "type": "sqlite3",
                    "path": DATABASE_PATH,
                }
                config_ini.write(data)
                data.seek(0)
                configs.append(data.read())
        return "\n".join(filter(bool, configs))

    def generate_datasource_config(self) -> str:
        """Template out a Grafana datasource config.

        Template using the sources (and removed sources) the consumer knows about, and dump it to
        YAML.

        Returns:
            A string-dumped YAML config for the datasources
        """
        # Boilerplate for the config file
        datasources_dict = {"apiVersion": 1, "datasources": [], "deleteDatasources": []}
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 9s</sub>

### ✅ `bash`

**Check testing imports in tests**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -rn "ops.testing\|from ops import testing\|import testing" tests/ | grep -v "Binary" | head -20

<details>
<summary>19 lines</summary>

```
tests/unit/test_external_url.py:13:from ops.testing import Model, Relation, CharmEvents
tests/unit/test_dashboard_collision.py:8:from ops.testing import Context, PeerRelation, State
tests/unit/test_datasources.py:4:from ops.testing import State, Relation, Context
tests/unit/test_auth_requirer.py:10:from ops import testing
tests/unit/conftest.py:4:from ops.testing import PeerRelation, Container, State, Exec
tests/unit/conftest.py:7:from ops.testing import Context
tests/unit/test_dashboard_transform.py:21:from ops.testing import Harness
tests/unit/test_dashboard_provider.py:16:from ops.testing import Harness
tests/unit/test_charm.py:10:from ops.testing import (Relation,
tests/unit/test_oauth.py:5:from ops.testing import Relation, Secret
tests/unit/test_config_reporting_enabled.py:2:from ops.testing import State
tests/unit/test_dashboard_consumer.py:20:from ops.testing import Harness, Relation, PeerRelation, Context, State
tests/unit/test_grafana_metadata_implementation.py:5:from ops.testing import Relation
tests/unit/test_auth_proxy_provider.py:10:from ops import testing
tests/unit/test_grafana_metadata_lib.py:7:from ops.testing import Context, Relation, State
tests/unit/test_source_consumer.py:11:from ops.testing import Harness
tests/unit/test_source_provider.py:11:from ops.testing import Harness
tests/scenario/test_admin_password.py:6:from ops import testing
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 18s</sub>

### ✅ `bash`

**Read full pyproject.toml**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat pyproject.toml

<details>
<summary>88 lines</summary>

```
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
[project]
name = "grafana-k8s"
version = "0.0"
requires-python = "~=3.8"

dependencies = [
  "ops>=2.17",
  "ops[tracing]",
  "pyyaml",
  "urllib3",
  "jsonschema",
  "cryptography",
  "jinja2<3",
  "markupsafe==2.0.1", # https://github.com/pallets/markupsafe/issues/371
  "lightkube>=0.11",
  # lib/charms/grafana_k8s/v0/grafana_dashboard.py
  # lib/charms/tempo_k8s/v1/charm_tracing.py
  "cosl",
  # lib/charms/istio_beacon_k8s/v0/service_mesh.py
  "charmed-service-mesh-helpers>=0.2.0",
  "lightkube-extensions",
  "pydantic[email]>=2.10.6",
]

[project.optional-dependencies]
dev = [
  # Linting
  "ruff",
  "codespell",
  # Static
  "pyright",
  # Unit
  "pytest",
  "coverage[toml]",
  "responses",
  "cosl",
  "pydantic",
  # Integration
  "juju<=3.3.0,>=3.0",
  "websockets<14.0",
  "lightkube",
  "minio",
  "oauth-tools",
  "pytest-operator>=0.39",
  "ops[testing]",
  "pytest-asyncio",
  "pytest-playwright",
  "aiohttp!=3.11.13",  # Yanked
  "asyncstdlib",
  "sh",
  "tenacity",
  "jubilant",
]

# Testing tools configuration
[tool.coverage.run]
branch = true

[tool.coverage.report]
show_missing = true

# Formatting tools configuration
[tool.black]
line-length = 99
target-version = ["py38"]

# Linting tools configuration
[tool.ruff]
line-length = 99
extend-exclude = ["__pycache__", "*.egg_info"]

[tool.ruff.lint]
select = ["E", "W", "F", "C", "N", "R", "D"]
# Ignore E501 because using black creates errors with this
# Ignore D107 Missing docstring in __init__
ignore = ["W505", "E501", "D107", "C901", "N818", "RET504"]
# D100, D101, D102, D103: Ignore missing docstrings in tests
per-file-ignores = {"tests/*" = ["D100","D101","D102","D103"]}

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.pyright]
extraPaths = ["lib"]
pythonVersion = "3.8"
pythonPlatform = "All"

[tool.pytest.ini_options]
asyncio_mode = "auto"
addopts = "--tb=native --verbose --capture=no --log-cli-level=INFO"

[tool.codespell]
skip = ".git,.tox,build,venv*"
ignore-words-list = "assertIn"

[tool.uv.sources]
oauth-tools = { git = "https://github.com/canonical/iam-bundle", rev = "oauth_tools-v0.1.2" }
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 18s</sub>

### ✅ `bash`

**Check explicit meta usage in Context**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -rn "charm_spec\|meta=\|Context(" tests/ | grep -v "Binary\|test_grafana_metadata_lib\|test_datasources\|#" | head -30

<details>
<summary>21 lines</summary>

```
tests/unit/test_auth_requirer.py:51:        self.harness = testing.Harness(RequirerCharm, meta=METADATA)
tests/unit/test_auth_requirer.py:172:        harness = testing.Harness(RequirerCharm, meta=meta)
tests/unit/test_auth_requirer.py:211:        harness = testing.Harness(RequirerCharmRefreshEvent, meta=meta)
tests/unit/conftest.py:39:    yield Context(GrafanaCharm)
tests/unit/test_dashboard_transform.py:328:        self.harness = Harness(ConsumerCharm, meta=meta)
tests/unit/test_dashboard_provider.py:116:        self.harness = Harness(ProviderCharm, meta=CONSUMER_META)
tests/unit/test_dashboard_consumer.py:467:        self.harness = Harness(ConsumerCharm, meta=meta)
tests/unit/test_auth_proxy_provider.py:45:        self.harness = testing.Harness(DefaultAuthProxyProviderCharm, meta=METADATA)
tests/unit/test_auth_proxy_provider.py:169:        harness = testing.Harness(DefaultAuthProxyProviderCharm, meta=meta)
tests/unit/test_auth_proxy_provider.py:208:        harness = testing.Harness(DefaultAuthProxyProviderCharmRefreshEvent, meta=meta)
tests/unit/test_auth_proxy_provider.py:241:        self.harness = testing.Harness(ProviderNonDefaultCharm, meta=METADATA)
tests/unit/test_auth_proxy_provider.py:274:        self.harness = testing.Harness(MissingModeProviderCharm, meta=METADATA)
tests/unit/test_source_consumer.py:83:        self.harness = Harness(GrafanaCharm, meta=meta)
tests/unit/test_source_provider.py:71:        self.harness = Harness(ProviderCharm, meta=CONSUMER_META)
tests/unit/test_source_provider.py:106:        self.harness = Harness(AlertManagerProviderCharm, meta=CONSUMER_META)
tests/unit/test_source_provider.py:125:        self.harness = Harness(MimirProviderCharm, meta=CONSUMER_META)
tests/unit/test_source_provider.py:154:        self.harness = Harness(ProviderCharmWithIngress, meta=CONSUMER_META)
tests/unit/test_source_provider.py:188:        self.harness = Harness(ProviderCharmWithIngress, meta=CONSUMER_META)
tests/unit/test_source_provider.py:239:        self.harness = Harness(ProviderCharmNoRefreshEvent, meta=CONSUMER_META)
tests/scenario/test_admin_password.py:45:    return testing.Context(GrafanaCharm)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 40s</sub>

### 💬 Copilot

Let me look at the ops config schema Python class feature more carefully:

---

<sub>⏱️ 2m 42s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/ops/latest/reference/ops/#ops.ConfigBase**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 8000,
  "url": "https://documentation.ubuntu.com/ops/latest/reference/ops/#ops.ConfigBase"
}
```

</details>

<details>
<summary>69 lines</summary>

```
Contents of https://documentation.ubuntu.com/ops/latest/reference/ops/#ops.ConfigBase:
The API to respond to Juju events and manage the application.

This API provides core features to your charm, including:

*   [`CharmBase`](#ops.CharmBase "ops.CharmBase"), the base class for charms and [`Object`](#ops.Object "ops.Object"), the base class for charm libraries.
    
*   [`EventBase`](#ops.EventBase "ops.framework.EventBase") class and individual event types, like the [`ActionEvent`](#ops.ActionEvent "ops.ActionEvent") class.
    
*   [`Framework`](#ops.Framework "ops.Framework") class, the main interface for the charm to ops library infrastructure, including:
    
    *   [`on`](#ops.Framework.on "ops.Framework.on") shorthand property used to [`observe()`](#ops.Framework.observe "ops.Framework.observe") and react to Juju events.
        
    *   [`model`](#ops.Framework.model "ops.Framework.model") attribute to get hold of the Model instance.
        
*   [`Model`](#ops.Model "ops.model.Model") class that represents the Juju model, accessible as `self.model` in a charm, including:
    
    *   [`app`](#ops.Model.app "ops.Model.app") attribute, representing the application associated with the charm.
        
    *   [`unit`](#ops.Model.unit "ops.Model.unit") attribute, representing the unit of the application the charm is running on.
        
    *   [`relations`](#ops.Model.relations "ops.Model.relations") attribute, which provides access to relations (integrations) defined in the charm, allowing interaction with other applications.
        
*   [`Container`](#ops.Container "ops.Container") class to control Kubernetes workloads, including:
    
    *   [`add_layer()`](#ops.Container.add_layer "ops.Container.add_layer") and [`replan()`](#ops.Container.replan "ops.Container.replan") methods to update Pebble configuration.
        
    *   [`pull()`](#ops.Container.pull "ops.Container.pull") and [`push()`](#ops.Container.push "ops.Container.push") methods to copy data to and from a container, respectively.
        
    *   [`exec()`](#ops.Container.exec "ops.Container.exec") method to run arbitrary commands inside the container.
        
*   [`StatusBase`](#ops.StatusBase "ops.StatusBase") class and individual status types, like the [`ActiveStatus`](#ops.ActiveStatus "ops.ActiveStatus") class.
    

_class_ ops.ActionEvent(_handle: [Handle](#ops.Handle "ops.framework.Handle")_, _id: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)") \= None_)[\[source\]](../../_modules/ops/charm/#ActionEvent)[¶](#ops.ActionEvent "Link to this definition")

Bases: [`EventBase`](#ops.EventBase "ops.framework.EventBase")

Events raised by Juju when an administrator invokes a Juju Action.

This class is the data type of events triggered when an administrator invokes a Juju Action. Callbacks bound to these events may be used for responding to the administrator’s Juju Action request.

To read the parameters for the action, see the instance variable [`params`](#ops.ActionEvent.params "ops.ActionEvent.params"). To respond with the result of the action, call [`set_results()`](#ops.ActionEvent.set_results "ops.ActionEvent.set_results"). To add progress messages that are visible as the action is progressing use [`log()`](#ops.ActionEvent.log "ops.ActionEvent.log").

defer() → [NoReturn](https://docs.python.org/3/library/typing.html#typing.NoReturn "(in Python v3.14)")[\[source\]](../../_modules/ops/charm/#ActionEvent.defer)[¶](#ops.ActionEvent.defer "Link to this definition")

Action events are not deferrable like other events.

This is because an action runs synchronously and the administrator is waiting for the result.

Raises:

[**RuntimeError**](https://docs.python.org/3/library/exceptions.html#RuntimeError "(in Python v3.14)") – always.

fail(_message: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") \= ''_)[\[source\]](../../_modules/ops/charm/#ActionEvent.fail)[¶](#ops.ActionEvent.fail "Link to this definition")

Report that this action has failed.

Parameters:

**message** – Optional message to record why it has failed.

id_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_ _\= ''_[¶](#ops.ActionEvent.id "Link to this definition")

The Juju ID of the action invocation.

load\_params(

_cls: [type](https://docs.python.org/3/library/functions.html#type "(in Python v3.14)")\[\_T\]_,

_\*args: [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")_,

_errors: [Literal](https://docs.python.org/3/library/typing.html#typing.Literal "(in Python v3.14)")\['raise', 'fail'\] \= 'raise'_,

_\*\*kwargs: [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")_,

) → \_T[\[source\]](../../_modules/ops/charm/#ActionEvent.load_params)[¶](#ops.ActionEvent.load_params "Link to this definition")

Load the action parameters into an instance of an action class.

The raw Juju action parameters are passed to the action class’s `__init__` method as keyword arguments, with dashes in names converted to underscores.

For dataclasses and Pydantic `BaseModel` subclasses, only fields in the Juju action parameters that have a matching field in the class are passed as arguments.

For example:

class BackupParams(pydantic.BaseModel):
    filename: str

def \_on\_do\_backup(self, event: ops.ActionEvent):
    params \= event.load\_params(BackupParams)
    \# params.filename contains the value passed by the Juju user.

Any additional positional or keyword arguments will be passed through to the action class `__init__`.

Parameters:

*   **cls** – A class that will accept the Juju parameters as keyword arguments, and raise `ValueError` if validation fails.
    
*   **errors** – what to do if the parameters are invalid. If `fail`, this will set the action to failed with an appropriate message and then immediately exit. If `raise`, `load_params` will not catch any exceptions, leaving the charm to handle errors.
    
*   **args** – positional arguments to pass through to the action class.
    
*   **kwargs** – keyword arguments to pass through to the action class.
    

Returns:

An instance of the action class that was provided in the `cls` argument with the provided parameter values.

Raises:

[**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError "(in Python v3.14)") – if `errors` is set to `raise` and instantiating the action class raises a ValueError.

log(_message: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_)[\[source\]](../../_modules/ops/charm/#ActionEvent.log)[¶](#ops.ActionEvent.log "Link to this definition")

Send a message that a user will see while the action is running.

Parameters:

**message** – The message for the user.

params_: [dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")\]_[¶](#ops.ActionEvent.params "Link to this definition")

The parameters passed to the action.

restore(_snapshot: [dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")\]_)[\[source\]](../../_modules/ops/charm/#ActionEvent.restore)[¶](#ops.ActionEvent.restore "Link to this definition")

Used by the framework to record the action.

Not meant to be called directly by charm code.

set\_results(_results: [dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")\]_)[\[source\]](../../_modules/ops/charm/#ActionEvent.set_results)[¶](#ops.ActionEvent.set_results "L

<note>Content truncated. Call the fetch tool with a start_index of 8000 to get more content.</note>
```

</details>


---

<sub>⏱️ 2m 41s</sub>

### ✅ `bash`

**Check ops.ConfigBase API**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && python3 -c "import ops; help(ops.ConfigBase)" 2>/dev/null | head -60 || python3 -c "import ops; print(dir(ops))" | tr ',' '\n' | grep -i "config\|Config"

```

<exited with exit code 0>
```


---

<sub>⏱️ 2m 50s</sub>

### ✅ `bash`

**Check ops.ConfigBase help**

$ python3 -c "import ops; cb = ops.ConfigBase; help(cb)" 2>/dev/null | head -80

```

<exited with exit code 0>
```


---

<sub>⏱️ 2m 50s</sub>

### ✅ `bash`

**Look at ConfigBase source**

$ python3 -c "import inspect, ops; print(inspect.getsource(ops.ConfigBase))" 2>/dev/null | head -60

```

<exited with exit code 0>
```


---

<sub>⏱️ 2m 55s</sub>

### ✅ `bash`

**Check ops config-related attributes**

$ python3 -c "import ops; print(ops.__version__); print([x for x in dir(ops) if 'config' in x.lower() or 'Config' in x])"

```
3.7.0
['ConfigChangedEvent', 'ConfigData', 'ConfigMeta']
<exited with exit code 0>
```


---

<sub>⏱️ 3m 6s</sub>

### ✅ `bash`

**Check ops base/schema classes**

$ python3 -c "import ops; print([x for x in dir(ops) if 'Base' in x or 'Schema' in x or 'Class' in x])"

```
['CharmBase', 'ContainerBase', 'EventBase', 'StatusBase']
<exited with exit code 0>
```


---

<sub>⏱️ 3m 6s</sub>

### ✅ `bash`

**Check ops charm/model for schema-related attributes**

$ python3 -c "
import ops
# Look for how config/relation/action schema is done
import ops.charm
print([x for x in dir(ops.charm) if 'Schema' in x or 'Config' in x or 'Action' in x])
print([x for x in dir(ops.model) if 'Schema' in x or 'Config' in x])
"

```
['ActionEvent', 'ActionMeta', 'ConfigChangedEvent', 'ConfigMeta']
['ConfigData']
<exited with exit code 0>
```


---

<sub>⏱️ 3m 15s</sub>

### ✅ `bash`

**Check Model.load_config**

$ python3 -c "
import ops.model as m
import inspect
# find load_config
for name in dir(m):
    obj = getattr(m, name)
    if hasattr(obj, 'load_config') or 'load_config' in str(obj):
        print(name)
# Check Model.load_config
if hasattr(m.Model, 'load_config'):
    print(inspect.getsource(m.Model.load_config))
"

```

<exited with exit code 0>
```


---

<sub>⏱️ 3m 21s</sub>

### ✅ `bash`

**Check ConfigData class**

$ python3 -c "
import ops
# Check ConfigData
import inspect
# look for 'load' methods in ConfigData
print(dir(ops.ConfigData))
if hasattr(ops.ConfigData, 'load'):
    print(inspect.getsource(ops.ConfigData.load))
"

```
['__abstractmethods__', '__annotations__', '__class__', '__class_getitem__', '__contains__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__ne__', '__new__', '__orig_bases__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__weakref__', '_abc_impl', '_data', '_invalidate', '_lazy_data', '_load', 'get', 'items', 'keys', 'values']
<exited with exit code 0>
```


---

<sub>⏱️ 3m 29s</sub>

### ✅ `bash`

**Search ops.model source for config class patterns**

$ python3 -c "
# Find where config-as-class is explained in the ops source
import ops.model
import inspect
src = inspect.getsource(ops.model)
# search for 'load_config' or 'ConfigBase' or class-based config
import re
matches = [(m.start(), src[max(0,m.start()-50):m.start()+200]) for m in re.finditer(r'load_config|ConfigBase|config_cls', src)]
for start, snippet in matches[:5]:
    print(snippet)
    print('---')
"

<details>
<summary>7 lines</summary>

```
that this unit is part of, use :meth:`CharmBase.load_config` or :attr:`CharmBase.config`.
    """

    def __init__(self, backend: _ModelBackend):
        self._backend = backend

    def _load(self) -> dict[str, bool | int | float | str]:
        
---
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 36s</sub>

### ✅ `bash`

**Check CharmBase.load_config**

$ python3 -c "
import ops.charm, inspect
# Check CharmBase for load_config
if hasattr(ops.CharmBase, 'load_config'):
    print(inspect.getsource(ops.CharmBase.load_config))
else:
    print('No load_config on CharmBase')
    # Search in charm.py source
    src = inspect.getsource(ops.charm)
    import re
    for m in re.finditer(r'load_config|ConfigBase', src):
        print(src[max(0,m.start()-100):m.start()+300])
        print('---')
" 2>/dev/null | head -80

<details>
<summary>69 lines</summary>

```
def load_config(
        self,
        cls: type[_T],
        *args: Any,
        errors: Literal['raise', 'blocked'] = 'raise',
        **kwargs: Any,
    ) -> _T:
        """Load the config into an instance of a config class.

        The raw Juju config is passed to the config class's ``__init__``, as
        keyword arguments, with the following changes:

        * ``secret`` type options have a :class:`model.Secret` value rather
          than the secret ID. Note that the secret object is not validated by
          Juju at this time, so may raise :class:`SecretNotFoundError` when it
          is used later (if the secret does not exist or the unit does not have
          permission to access it).
        * dashes in names are converted to underscores.

        For dataclasses and Pydantic ``BaseModel`` subclasses, only fields in
        the Juju config that have a matching field in the class are passed as
        arguments. Pydantic fields that have an ``alias``, or dataclasses that
        have a ``metadata{'alias'=}``, will have the alias applied when loading.

        For example::

            class Config(pydantic.BaseModel):
                # This field is called 'class' in the Juju config options.
                workload_class: str = pydantic.Field(alias='class')

            def _on_config_changed(self, event: ops.ConfigChangedEvent):
                data = self.load_config(Config, errors='blocked')
                # `data.workload_class` has the value of the Juju option `class`

        Pydantic classes that have fields that are not simple or
        Pydantic types, such as :class:`ops.Secret`, require setting
        ``arbitrary_types_allowed`` in the Pydantic model config.

        Any additional positional or keyword arguments to this method will be
        passed through to the config class ``__init__``.

        Args:
            cls: A class that will accept the Juju options as keyword arguments,
                and raise ``ValueError`` if validation fails.
            errors: what to do if the config is invalid. If ``blocked``, this
                will set the unit status to blocked with an appropriate message
                and then exit successfully (this informs Juju that
                the event was handled and it will not be retried).
                If ``raise``, ``load_config``
                will not catch any exceptions, leaving the charm to handle
                errors.
            args: positional arguments to pass through to the config class.
            kwargs: keyword arguments to pass through to the config class.

        Returns:
            An instance of the config class that was passed in the ``cls`` argument
            with the current config values.

        Raises:
            ValueError: if the configuration is invalid and ``errors`` is set to
                ``raise``.
        """
        from ._main import _Abort

        config: dict[str, bool | int | float | str | model.Secret] = kwargs.copy()
        try:
            fields = set(_juju_fields(cls))
        except ValueError:
            fields = None
        for key, value in self.config.items():
            attr = key.replace('-', '_')
            if fields is not None and attr not in fields:
                continue
            option_type = self.meta.config.get(key)
            # Convert secret IDs to secret objects. We create the object rather
            # that using model.get_secret so that it's entirely lazy, in the
            # same way that SecretEvent.secret is.
            if option_type and option_type.type == 'secret':
                assert isinstance(value, str)  # Juju will have made sure of this.
                value = model.Secret(
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 58s</sub>

### 💬 Copilot

Let me look at the full config options and all their usages:

---

<sub>⏱️ 3m 58s</sub>

### ✅ `bash`

**Find all config usages in src**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -rn "self\.config\b\|self\.model\.config" src/ | grep -v "^.*#" | head -50

<details>
<summary>11 lines</summary>

```
src/charm.py:209:                                            enable_reporting = bool(self.config["reporting_enabled"]),
src/charm.py:212:                                            custom_config=cast(Optional[str], self.config.get("custom_ini_config")),
src/charm.py:340:            query_timeout=int(self.model.config.get("datasource_query_timeout", 0)),
src/charm.py:351:            log_level=str(self.model.config["log_level"]),
src/charm.py:352:            allow_embedding=bool(self.model.config["allow_embedding"]),
src/charm.py:353:            allow_anonymous_access=bool(self.model.config["allow_anonymous_access"]),
src/charm.py:354:            enable_auto_assign_org=bool(self.model.config["enable_auto_assign_org"]),
src/charm.py:358:            admin_user = str(self.model.config["admin_user"]),
src/charm.py:579:                cast(str, self.model.config["admin_user"]), admin_password
src/charm.py:663:        limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 58s</sub>

### ✅ `bash`

**Look at remaining config options**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat charmcraft.yaml | grep -A 200 "custom_config:" | head -50

<details>
<summary>9 lines</summary>

```
custom_config:
      type: string
      description: |
        Additional configuration options to be added to grafana.ini.
        These options will be appended to the grafana.ini file, allowing for custom configuration.
        Note that this config option accepts only a small subset of the grafana.ini file.
        Currently supported sections:
        - [smtp], ref: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#smtp
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 6s</sub>

### ✅ `bash`

**List all config option names and types**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat charmcraft.yaml | grep "type:\|^\s\s[a-z]" | grep -A1 "type:" | head -40

<details>
<summary>21 lines</summary>

```
type: charm
  charm is written to allow for HA on Kubernetes and can take
--
    type: filesystem
  grafana-source:
--
    type: oci-image
  ubuntu@24.04:amd64:
--
      type: boolean
      type: boolean
      type: string
      type: string
      type: string
      type: boolean
      type: int
      type: string
      type: string
      type: boolean
      type: string
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 6s</sub>

### ✅ `bash`

**List all config options with their types**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && python3 -c "
import yaml
with open('charmcraft.yaml') as f:
    data = yaml.safe_load(f)
for name, opts in data.get('config', {}).get('options', {}).items():
    print(f'{name}: type={opts[\"type\"]}, default={opts.get(\"default\", \"<unset>\")}')
"

<details>
<summary>12 lines</summary>

```
allow_anonymous_access: type=boolean, default=False
allow_embedding: type=boolean, default=False
log_level: type=string, default=info
admin_user: type=string, default=admin
web_external_url: type=string, default=
enable_auto_assign_org: type=boolean, default=True
datasource_query_timeout: type=int, default=300
cpu: type=string, default=<unset>
memory: type=string, default=<unset>
reporting_enabled: type=boolean, default=True
custom_config: type=string, default=<unset>
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 13s</sub>

### ✅ `bash`

**Look at charm.py lines 200-220**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && sed -n '200,220p' src/charm.py

<details>
<summary>21 lines</summary>

```
self._db_type = "postgres"

        self._grafana_client = GrafanaClient(self.internal_url)
        self._grafana_config = GrafanaConfig(
                                            datasources_config=self._datasource_config,
                                            oauth_config = self._oauth_config,
                                            auth_env_config = lambda: self._auth_env_vars,
                                            db_config=lambda: self._db_config,
                                            db_type=self._db_type,
                                            enable_reporting = bool(self.config["reporting_enabled"]),
                                            enable_external_db=self._enable_external_db,
                                            tracing_endpoint=self._workload_tracing_endpoint,
                                            custom_config=cast(Optional[str], self.config.get("custom_ini_config")),
                                            )
        self._grafana_service = Grafana(
                                        container=self.unit.get_container("grafana"),
                                        is_leader= self.unit.is_leader(),
                                        grafana_config_generator=self._grafana_config,
                                        pebble_env=self._pebble_env,
                                        tls_config = self._tls_config,
                                        trusted_ca_certs = self._trusted_ca_certs,
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 42s</sub>

### ✅ `bash`

**Look at models.py**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat src/models.py

<details>
<summary>30 lines</summary>

```
# Copyright 2025 Canonical
# See LICENSE file for licensing details.

"""Data models class."""

import dataclasses
from typing import Callable, List, Optional

@dataclasses.dataclass
class TLSConfig:
    """TLS config model."""
    certificate: str
    key: str
    ca: str

@dataclasses.dataclass
class DatasourceConfig:
    """Grafana datasource config."""
    datasources: Callable[[], List[dict]]
    datasources_to_delete: Callable[[],List[str]]
    query_timeout: int = 0

@dataclasses.dataclass
class PebbleEnvironment:
    """Grafana pebble service environment config."""
    external_url: str
    log_level:str = "info"
    allow_embedding: bool = False
    allow_anonymous_access: bool = False
    enable_auto_assign_org: bool = True
    enable_profiling: bool = False
    tracing_resource_attributes: Optional[str] = None
    admin_user: Optional[str] = None
    admin_password: Optional[str] = None
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 42s</sub>

### ✅ `bash`

**Look at grafana.py**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && head -60 src/grafana.py

<details>
<summary>56 lines</summary>

```
#  Copyright 2021 Canonical Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""A module used for interacting with a running Grafana instance."""
import time
from pathlib import Path
import os
import hashlib
import logging
from typing import Callable, Dict, List, Optional, cast
from ops import Container
import re
from ops.pebble import (
    APIError,
    ConnectionError,
    ChangeError,
    ExecError,
    Layer,
    PathError,
    ProtocolError,
)
from models import TLSConfig
from constants import (
    GRAFANA_KEY_PATH,
    DATABASE_PATH,
    CA_CERT_PATH,
    GRAFANA_CRT_PATH,
    OAUTH_SCOPES,
    PROFILING_PORT,
    GRAFANA_WORKLOAD,
    CONFIG_PATH,
    WORKLOAD_PORT,
    PROVISIONING_PATH,
    DATASOURCES_PATH,
    DASHBOARDS_DIR,
    TRUSTED_CA_CERT_PATH
)
from grafana_config import GrafanaConfig

logger = logging.getLogger()


class Grafana:
    """Grafana workload."""

    def __init__(self,
                container: Container,
                is_leader: bool,
                grafana_config_generator: GrafanaConfig,
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 5s</sub>

### ✅ `bash`

**Read charm __init__ method**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && sed -n '35,180p' src/charm.py

<details>
<summary>127 lines</summary>

```
)
from ops.model import Port
from secret_storage import SecretStorage

from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
from charms.certificate_transfer_interface.v1.certificate_transfer import (
    CertificateTransferRequires,
)
from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
from charms.grafana_k8s.v0.grafana_auth import AuthRequirer, AuthRequirerCharmEvents
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardConsumer
from charms.grafana_k8s.v0.grafana_metadata import GrafanaMetadataProvider
from charms.grafana_k8s.v0.grafana_source import (
    GrafanaSourceConsumer,
)
from charms.hydra.v0.oauth import (
    ClientConfig as OauthClientConfig,
    OAuthRequirer,
    OauthProviderConfig
)
from charms.istio_beacon_k8s.v0.service_mesh import UnitPolicy, ServiceMeshConsumer
from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
    KubernetesComputeResourcesPatch,
    ResourceRequirements,
    adjust_resource_requirements,
)
from charms.parca_k8s.v0.parca_scrape import ProfilingEndpointProvider
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer
from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer, IngressPerAppReadyEvent, IngressPerAppRevokedEvent
from grafana import Grafana
from grafana_client import GrafanaClient, GrafanaCommError
from grafana_config import GrafanaConfig
from secret_storage import generate_password
from relation import Relation
from models import DatasourceConfig, PebbleEnvironment, TLSConfig
from charms.tls_certificates_interface.v4.tls_certificates import (
    CertificateRequestAttributes,
    TLSCertificatesRequiresV4,
    CertificateAvailableEvent,
)
from constants import (
    PEER_RELATION,
    WORKLOAD_PORT,
    OAUTH_SCOPES,
    CA_CERT_PATH,
    GRAFANA_WORKLOAD,
    PGSQL_RELATION,
    PROFILING_PORT,
    OAUTH_GRANT_TYPES,
    VALID_AUTHENTICATION_MODES,
    METRICS_PATH)
import ops_tracing

logger = logging.getLogger()


class GrafanaCharm(CharmBase):
    """Charm to run Grafana on Kubernetes.

    This charm allows for high-availability
    (as long as a non-sqlite database relation is present).

    Developers of this charm should be aware of the Grafana provisioning docs:
    https://grafana.com/docs/grafana/latest/administration/provisioning/
    """

    def __init__(self, *args):
        super().__init__(*args)

        # -- initialize states --
        self._topology = JujuTopology.from_charm(self)
        self._fqdn = socket.getfqdn()
        self.peers = Relation(app=self.app, relation=self.model.get_relation(PEER_RELATION))
        self._secret_storage = SecretStorage(self, "admin-password",
                                             default=lambda: {"password": generate_password()})


        # -- certificates
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

        # -- trusted_cert_transfer
        self.trusted_cert_transfer = CertificateTransferRequires(self, "receive-ca-cert")

        # -- ingress
        self.ingress = IngressPerAppRequirer(self, port=WORKLOAD_PORT, scheme=self._scheme, strip_prefix=False)

        # -- service mesh
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


        self.metrics_endpoint = MetricsEndpointProvider(
            charm=self,
            jobs=self._metrics_scrape_jobs,
            refresh_event=[
                self.on.grafana_pebble_ready,  # pyright: ignore
                self.on.update_status,
            ],
        )
        self.charm_tracing = TracingEndpointRequirer(
            self, relation_name="charm-tracing", protocols=["otlp_http"]
        )
        self.workload_tracing = TracingEndpointRequirer(
            self, relation_name="workload-tracing", protocols=["otlp_grpc"]
        )

        self.profiling = ProfilingEndpointProvider(self, jobs=self._profiling_scrape_jobs)

        # -- grafana_source relation observations
        self.source_consumer = GrafanaSourceConsumer(
            self,
            grafana_uid=self.unique_name,
            grafana_base_url=self.external_url,
            relation_name="grafana-source",
        )

        # -- grafana_dashboard relation observations
        self.dashboard_consumer = GrafanaDashboardConsumer(self, "grafana-dashboard")


        # -- k8s resource patch
        self.resource_patch = KubernetesComputeResourcesPatch(
            self, GRAFANA_WORKLOAD, resource_reqs_func=self._resource_reqs_from_config
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 10s</sub>

### ✅ `bash`

**Read more of __init__**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && sed -n '180,260p' src/charm.py

<details>
<summary>71 lines</summary>

```
self, GRAFANA_WORKLOAD, resource_reqs_func=self._resource_reqs_from_config
        )

        # oauth relation
        self.oauth = OAuthRequirer(self, self._oauth_client_config)
        self.catalog = CatalogueConsumer(charm=self, item=self._catalogue_item)
        self.grafana_auth_requirer = AuthRequirer(
            self,
            relation_name="grafana-auth",
            urls=[f"{self.app.name}:{WORKLOAD_PORT}"],
            refresh_event=self.on.grafana_pebble_ready,  # pyright: ignore
        )

        # -- database relation
        self._db_name = f"{self._topology.application}-grafana-k8s-{self._topology.model_uuid}"
        self._db = None
        self._db_type = "sqlite3"

        if self.model.relations[PGSQL_RELATION]:
            self._db = DatabaseRequires(self, relation_name=PGSQL_RELATION, database_name=self._db_name)
            self._db_type = "postgres"

        self._grafana_client = GrafanaClient(self.internal_url)
        self._grafana_config = GrafanaConfig(
                                            datasources_config=self._datasource_config,
                                            oauth_config = self._oauth_config,
                                            auth_env_config = lambda: self._auth_env_vars,
                                            db_config=lambda: self._db_config,
                                            db_type=self._db_type,
                                            enable_reporting = bool(self.config["reporting_enabled"]),
                                            enable_external_db=self._enable_external_db,
                                            tracing_endpoint=self._workload_tracing_endpoint,
                                            custom_config=cast(Optional[str], self.config.get("custom_ini_config")),
                                            )
        self._grafana_service = Grafana(
                                        container=self.unit.get_container("grafana"),
                                        is_leader= self.unit.is_leader(),
                                        grafana_config_generator=self._grafana_config,
                                        pebble_env=self._pebble_env,
                                        tls_config = self._tls_config,
                                        trusted_ca_certs = self._trusted_ca_certs,
                                        dashboards = self.dashboard_consumer.dashboards,
                                        provision_own_dashboard = self._provision_own_dashboard,
                                        scheme=self._scheme,
                                        ingress_ready=self.ingress.is_ready(),
                                        )

        self.framework.observe(
            self.on.get_admin_password_action,  # pyright: ignore
            self._on_get_admin_password,
        )

        # FIXME: we still need to observe these events as they contain the required data
        # update the charm lib to work with the reconcile approach
        if self._db is not None:
            self.framework.observe(self._db.on.database_created, self._on_database_changed)
            self.framework.observe(self._db.on.endpoints_changed, self._on_database_changed)
        self.framework.observe(
            self.grafana_auth_requirer.on.auth_conf_available,  # pyright: ignore
            self._on_grafana_auth_conf_available,
        )

        # FIXME: we still need to call reconcile since the lib updates peer data on specific events
        # update the charm lib to work with the reconcile approach
        self.framework.observe(
            self.source_consumer.on.sources_changed,  # pyright: ignore
            self._on_grafana_source_changed,
        )
        self.framework.observe(
            self.source_consumer.on.sources_to_delete_changed,  # pyright: ignore
            self._on_grafana_source_changed,
        )

        self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)

        all_events.add(IngressPerAppReadyEvent)
        all_events.add(IngressPerAppRevokedEvent)
        all_events.add(CertificateAvailableEvent)
        observe_events(self, all_events, self._reconcile)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 15s</sub>

### ✅ `bash`

**Read datasource_config and pebble_env properties**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && sed -n '330,410p' src/charm.py

<details>
<summary>72 lines</summary>

```
if self.workload_tracing.is_ready():
            endpoint = self.workload_tracing.get_endpoint("otlp_grpc")
            return endpoint
        return None

    @property
    def _datasource_config(self) -> DatasourceConfig:
        return DatasourceConfig(
            datasources=lambda : self.source_consumer.sources,
            datasources_to_delete=lambda : self.source_consumer.sources_to_delete,
            query_timeout=int(self.model.config.get("datasource_query_timeout", 0)),
        )

    def _pebble_env(self) -> PebbleEnvironment:
        topology = self._topology
        tracing_resource_attrs = ((f"juju_application={topology.application},juju_model={topology.model}" + \
                                f",juju_model_uuid={topology.model_uuid},juju_unit={topology.unit},juju_charm={topology.charm_name}") \
                            if self._workload_tracing_endpoint
                            else None)
        return PebbleEnvironment(
            external_url=self.external_url,
            log_level=str(self.model.config["log_level"]),
            allow_embedding=bool(self.model.config["allow_embedding"]),
            allow_anonymous_access=bool(self.model.config["allow_anonymous_access"]),
            enable_auto_assign_org=bool(self.model.config["enable_auto_assign_org"]),
            enable_profiling=bool(self.model.relations.get("profiling-endpoint")),
            tracing_resource_attributes=tracing_resource_attrs,
            admin_password = self.admin_password,
            admin_user = str(self.model.config["admin_user"]),
        )

    @property
    def _provision_own_dashboard(self) -> bool:
        source_related_apps = [rel.app for rel in self.model.relations["grafana-source"]]
        scrape_related_apps = [rel.app for rel in self.model.relations["metrics-endpoint"]]

        return any(
            source for source in source_related_apps if source in scrape_related_apps
        )

    @property
    def _enable_external_db(self) -> bool:
        """Only consider a DB connection if we have config info."""
        return bool(self.model.get_relation(PGSQL_RELATION))

    @property
    def _db_config(self) -> Optional[Dict[str, str]]:
        if self._enable_external_db:
            peer_data = self.peers.get_app_data("database")
            if not peer_data:
                return None
            return peer_data
        return None

    @property
    def _oauth_client_config(self) -> OauthClientConfig:
        return OauthClientConfig(
            os.path.join(self.external_url, "login/generic_oauth"),
            OAUTH_SCOPES,
            OAUTH_GRANT_TYPES,
        )

    @property
    def _oauth_config(self) -> Optional[OauthProviderConfig]:
        if self.oauth.is_client_created():
            return self.oauth.get_provider_info()
        return None

    @property
    def _auth_env_vars(self):
        return self.peers.get_app_data("auth_conf_env_vars")

    @property
    def _tls_config(self) -> Optional[TLSConfig]:
        certificates, key = self._cert_requirer.get_assigned_certificate(
            certificate_request=self._csr_attributes
        )
        if not (key and certificates):
            return None
        return TLSConfig(
            certificate=certificates.certificate.raw,
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 36s</sub>

### ✅ `bash`

**Look at config-related tests**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat tests/unit/test_config_reporting_enabled.py && echo "===" && cat tests/unit/test_custom_ini_config.py | head -50

<details>
<summary>69 lines</summary>

```
from configparser import ConfigParser
from ops.testing import State


def test_reporting_enabled(ctx, containers):
    # GIVEN the "reporting_enabled" config option is set to True
    state = State(leader=True, config={"reporting_enabled": True}, containers=containers)

    # WHEN config-changed fires
    out = ctx.run(ctx.on.config_changed(), state)

    # THEN the config file is written WITHOUT the [analytics] section being rendered
    simulated_pebble_filesystem = out.get_container("grafana").get_filesystem(ctx)
    grafana_config_path = simulated_pebble_filesystem / "etc/grafana/grafana-config.ini"

    config = ConfigParser()
    config.read(grafana_config_path)
    assert "analytics" not in config


def test_reporting_disabled(ctx, containers):
    # GIVEN the "reporting_enabled" config option is set to False
    state = State(leader=True, config={"reporting_enabled": False}, containers=containers)

    # WHEN config-changed fires
    out = ctx.run(ctx.on.config_changed(), state)

    # THEN the config file is written WITH the [analytics] section being rendered
    simulated_pebble_filesystem = out.get_container("grafana").get_filesystem(ctx)
    grafana_config_path = simulated_pebble_filesystem / "etc/grafana/grafana-config.ini"

    config = ConfigParser()
    config.read(grafana_config_path)
    assert "analytics" in config
    assert dict(config["analytics"]) == {
        "reporting_enabled": "false",
        "check_for_updates": "false",
        "check_for_plugin_updates": "false",
    }

    # AND the "grafana" service is restarted
    # TODO Does it make sense to check this if the charm under test's lifetime is only for the config-changed?
    # TODO How to assert this?
===
#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for custom_ini_config module."""

import pytest

from src.custom_ini_config import validate


def test_validate_without_args():
    # WHEN validate called without args
    r1 = validate()
    r2 = validate(None)

    # THEN returns None
    assert r1 is None
    assert r2 is None


def test_validate_with_invalid_string():
    # GIVEN string without sections
    ini = "hello"

    # WHEN validate called
    # THEN ValueError is raised
    with pytest.raises(ValueError, match="Invalid ini sections"):
        validate(ini)


def test_validate_with_invalid_section():
    # GIVEN valid ini but invalid schema
    ini = """[section]
    key = value
    """

    # WHEN validate called with
    # THEN ValueError is raised.
    with pytest.raises(ValueError, match="unallowed sections"):
        validate(ini)


def test_validate_with_valid_smtp_section():
    # GIVEN a valid ini with valid schema
    ini = """[smtp]
    enabled = true"""

    # WHEN validate called
    # THEN returns None
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 42s</sub>

### ✅ `bash`

**Check all usages of custom config options**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -rn "custom_ini_config\|custom_config" tests/ src/ | grep -v ".pyc"

<details>
<summary>13 lines</summary>

```
tests/unit/test_custom_ini_config.py:5:"""Unit tests for custom_ini_config module."""
tests/unit/test_custom_ini_config.py:9:from src.custom_ini_config import validate
src/grafana_config.py:17:import custom_ini_config
src/grafana_config.py:35:                custom_config: Optional[str] = None,
src/grafana_config.py:45:        self._custom_config = custom_config
src/grafana_config.py:61:            custom_ini_config.validate(self._custom_config)
src/grafana_config.py:63:            logger.error("Invalid custom_config: %s", e)
src/grafana_config.py:64:            return BlockedStatus("Invalid custom_config; see debug-log")
src/grafana_config.py:70:        if self._custom_config is not None:
src/grafana_config.py:72:                custom_ini_config.validate(self._custom_config)
src/grafana_config.py:76:                configs.append(self._custom_config)
src/charm.py:212:                                            custom_config=cast(Optional[str], self.config.get("custom_ini_config")),
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 59s</sub>

### ✅ `bash`

**Check for UncaughtCharmError usage in tests**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -rn "UncaughtCharmError\|pytest.raises" tests/unit/ tests/scenario/ | head -20

<details>
<summary>7 lines</summary>

```
tests/unit/test_custom_ini_config.py:28:    with pytest.raises(ValueError, match="Invalid ini sections"):
tests/unit/test_custom_ini_config.py:40:    with pytest.raises(ValueError, match="unallowed sections"):
tests/unit/test_custom_ini_config.py:63:    with pytest.raises(ValueError, match="Invalid \\[smtp\\] section"):
tests/unit/test_source_consumer.py:219:        with pytest.raises(KeyError):
tests/scenario/test_admin_password.py:96:            with pytest.raises(testing.ActionFailed) as failure:
tests/scenario/test_admin_password.py:113:        with pytest.raises(testing.ActionFailed) as failure:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 59s</sub>

### ✅ `bash`

**Check for pytest.raises in tests**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -rn "pytest.raises" tests/unit/ tests/scenario/ | head -20

<details>
<summary>7 lines</summary>

```
tests/unit/test_custom_ini_config.py:28:    with pytest.raises(ValueError, match="Invalid ini sections"):
tests/unit/test_custom_ini_config.py:40:    with pytest.raises(ValueError, match="unallowed sections"):
tests/unit/test_custom_ini_config.py:63:    with pytest.raises(ValueError, match="Invalid \\[smtp\\] section"):
tests/unit/test_source_consumer.py:219:        with pytest.raises(KeyError):
tests/scenario/test_admin_password.py:96:            with pytest.raises(testing.ActionFailed) as failure:
tests/scenario/test_admin_password.py:113:        with pytest.raises(testing.ActionFailed) as failure:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 11s</sub>

### ✅ `bash`

**Check if ops-scenario is separate package**

$ pip show ops-scenario 2>/dev/null || echo "ops-scenario not installed"

<details>
<summary>11 lines</summary>

```
Name: ops-scenario
Version: 8.7.0
Summary: Python library providing a state-transition testing API for Operator Framework charms.
Home-page: 
Author: 
Author-email: Pietro Pasotti <pietro.pasotti@canonical.com>
License: 
Location: /home/ubuntu/.local/lib/python3.12/site-packages
Requires: ops, PyYAML, typing_extensions
Required-by: pytest-interface-tester
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 11s</sub>

### ✅ `bash`

**Check scenario references in config files**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -rn "scenario" tox.ini pyproject.toml

```

<exited with exit code 1>
```


---

<sub>⏱️ 6m 18s</sub>

### ✅ `bash`

**Check ops-scenario versions available**

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

<sub>⏱️ 6m 28s</sub>

### 💬 Copilot

Let me check ops-scenario releases:

---

<sub>⏱️ 6m 29s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/ops-scenario/releases**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 6000,
  "url": "https://github.com/canonical/ops-scenario/releases"
}
```

</details>

<details>
<summary>48 lines</summary>

```
Contents of https://github.com/canonical/ops-scenario/releases:
This repository was archived by the owner on Apr 10, 2025. It is now read-only.

## 7.0.5

19 Sep 23:55

Merge pull request #198 from tonyandrewmeyer/anyjson-stricter-type

feat: use a slightly more strict type for \`AnyJson\`

## 7.0.4

18 Sep 10:28

Merge pull request #195 from tonyandrewmeyer/add-py-typed

chore: add py.typed file

## 7.0.3

18 Sep 07:06

Merge pull request #194 from tonyandrewmeyer/fix-get\_relation-keyerro…

## 7.0.2

12 Sep 23:19

Merge pull request #191 from tonyandrewmeyer/support-ops-2-17

chore: handle the changes coming in ops 2.17

## 7.0.1

09 Sep 09:01

Merge pull request #188 from tonyandrewmeyer/fix-3.8-inspect-compat

fix: adjust the inspect.signature behaviour to work with Python 3.8

## 7.0.0

09 Sep 07:55

Merge pull request #183 from canonical/7.0

7.0 - API adjustments, Pebble check events, and container exec improvements

## 6.1.7

09 Sep 06:09

Merge pull request #186 from tonyandrewmeyer/limit-6-to-ops-16

chore: limit Scenario 6 to use ops 2.12-2.16

## 6.1.6

26 Aug 20:45

chore: add compatibility with the next ops release (#178)

The next release of ops has some backwards-incompatible changes to
private methods. This PR does the minimum to keep Scenario working with
the current version of ops and the next release.

I'll open a ticket for doing a nicer version of this where the new
\`\_JujuContext\` class is used (which would presumably mean requiring the
new version of ops). But this will let people continue upgrading their
ops as long as they're using the latest 6.x of Scenario.

The relevant ops PR is: https://github.com/canonical/operator/pull/1313

## 6.1.5

01 Aug 06:20

Merge pull request #166 from canonical/fix-juju-info-network-get

ulterior fix

## 6.1.4

31 Jul 10:59

Merge pull request #165 from canonical/fix-juju-info-network-get

fixed juju-info network
```

</details>


---

<sub>⏱️ 6m 28s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/ops-tracing/releases**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 6000,
  "url": "https://github.com/canonical/ops-tracing/releases"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/ops-tracing/releases - status code 404
```


---

<sub>⏱️ 6m 37s</sub>

### ✅ `bash`

**Check ops-scenario package details**

$ python3 -c "import ops_scenario; print(ops_scenario.__version__)" 2>/dev/null || python3 -c "import scenario; print(scenario.__version__)" 2>/dev/null || echo "checking..."
python3 -c "
import pkg_resources
try:
    pkg = pkg_resources.get_distribution('ops-scenario')
    print('ops-scenario:', pkg.version, 'location:', pkg.location)
except Exception as e:
    print(e)
"

```
checking...
<string>:2: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
ops-scenario: 8.7.0 location: /home/ubuntu/.local/lib/python3.12/site-packages
<exited with exit code 0>
```


---

<sub>⏱️ 6m 43s</sub>

### ❌ `bash`

**Find ops-scenario package files**

$ ls /home/ubuntu/.local/lib/python3.12/site-packages/ | grep -i "scenario\|ops_scenario"

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 6m 48s</sub>

### ✅ `bash`

**Show ops-scenario package files**

$ pip show -f ops-scenario 2>/dev/null | head -20

<details>
<summary>21 lines</summary>

```
Name: ops-scenario
Version: 8.7.0
Summary: Python library providing a state-transition testing API for Operator Framework charms.
Home-page: 
Author: 
Author-email: Pietro Pasotti <pietro.pasotti@canonical.com>
License: 
Location: /home/ubuntu/.local/lib/python3.12/site-packages
Requires: ops, PyYAML, typing_extensions
Required-by: pytest-interface-tester
Files:
  ops_scenario-8.7.0.dist-info/INSTALLER
  ops_scenario-8.7.0.dist-info/METADATA
  ops_scenario-8.7.0.dist-info/RECORD
  ops_scenario-8.7.0.dist-info/REQUESTED
  ops_scenario-8.7.0.dist-info/WHEEL
  ops_scenario-8.7.0.dist-info/top_level.txt
  scenario/__init__.py
  scenario/__pycache__/__init__.cpython-312.pyc
  scenario/__pycache__/_charmcraft_extensions.cpython-312.pyc
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 56s</sub>

### ✅ `bash`

**List ops-scenario files**

$ pip show -f ops-scenario 2>/dev/null | grep "^  scenario/" | head -20

<details>
<summary>21 lines</summary>

```
scenario/__init__.py
  scenario/__pycache__/__init__.cpython-312.pyc
  scenario/__pycache__/_charmcraft_extensions.cpython-312.pyc
  scenario/__pycache__/_consistency_checker.cpython-312.pyc
  scenario/__pycache__/_ops_main_mock.cpython-312.pyc
  scenario/__pycache__/_runtime.cpython-312.pyc
  scenario/__pycache__/context.cpython-312.pyc
  scenario/__pycache__/errors.cpython-312.pyc
  scenario/__pycache__/logger.cpython-312.pyc
  scenario/__pycache__/mocking.cpython-312.pyc
  scenario/__pycache__/state.cpython-312.pyc
  scenario/_charmcraft_extensions.py
  scenario/_consistency_checker.py
  scenario/_ops_main_mock.py
  scenario/_runtime.py
  scenario/context.py
  scenario/errors.py
  scenario/logger.py
  scenario/mocking.py
  scenario/py.typed
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 7s</sub>

### ✅ `bash`

**Check ops-tracing module**

$ python3 -c "import ops_tracing; print(dir(ops_tracing))" 2>/dev/null && pip show ops-tracing | head -5

<details>
<summary>10 lines</summary>

```
['Tracing', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '_api', '_backend', '_buffer', '_export', '_mark_observed', '_setup', '_shutdown', 'set_destination', 'vendor']
Name: ops-tracing
Version: 3.7.0
Summary: The tracing facility for the Ops library.
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
ERROR: Pipe to stdout was broken
Exception ignored in: <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>
BrokenPipeError: [Errno 32] Broken pipe
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 13s</sub>

### ✅ `bash`

**Find ops-tracing location**

$ python3 -c "import inspect, ops_tracing; print(inspect.getfile(ops_tracing))"

```
/home/ubuntu/.local/lib/python3.12/site-packages/ops_tracing/__init__.py
<exited with exit code 0>
```


---

<sub>⏱️ 7m 21s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/operator/blob/main/ops-tracing/CHANGELOG.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 8000,
  "url": "https://github.com/canonical/operator/blob/main/ops-tracing/CHANGELOG.md"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/operator/blob/main/ops-tracing/CHANGELOG.md - status code 404
```


---

<sub>⏱️ 7m 26s</sub>

### ❌ `bash`

**Look at ops-tracing metadata**

$ cat /home/ubuntu/.local/lib/python3.12/site-packages/ops_tracing-*.dist-info/METADATA 2>/dev/null | head -60 || find /home/ubuntu/.local/lib/python3.12/site-packages -name "*.dist-info" -type d 2>/dev/null | grep tracing

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 7m 32s</sub>

### ✅ `bash`

**Get ops-tracing details**

$ pip show ops-tracing 2>/dev/null

<details>
<summary>11 lines</summary>

```
Name: ops-tracing
Version: 3.7.0
Summary: The tracing facility for the Ops library.
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
Author-email: 
License: 
Location: /home/ubuntu/.local/lib/python3.12/site-packages
Requires: opentelemetry-api, opentelemetry-sdk, ops, pydantic
Required-by:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 39s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/operator/tree/main/ops-tracing**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 5000,
  "url": "https://github.com/canonical/operator/tree/main/ops-tracing"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/operator/tree/main/ops-tracing - status code 404
```


---

<sub>⏱️ 7m 45s</sub>

### ✅ `bash`

**List ops-tracing files**

$ pip show -f ops-tracing 2>/dev/null | head -30

<details>
<summary>31 lines</summary>

```
Name: ops-tracing
Version: 3.7.0
Summary: The tracing facility for the Ops library.
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
Author-email: 
License: 
Location: /home/ubuntu/.local/lib/python3.12/site-packages
Requires: opentelemetry-api, opentelemetry-sdk, ops, pydantic
Required-by: 
Files:
  ops_tracing-3.7.0.dist-info/INSTALLER
  ops_tracing-3.7.0.dist-info/METADATA
  ops_tracing-3.7.0.dist-info/RECORD
  ops_tracing-3.7.0.dist-info/WHEEL
  ops_tracing/__init__.py
  ops_tracing/__pycache__/__init__.cpython-312.pyc
  ops_tracing/__pycache__/_api.cpython-312.pyc
  ops_tracing/__pycache__/_backend.cpython-312.pyc
  ops_tracing/__pycache__/_buffer.cpython-312.pyc
  ops_tracing/__pycache__/_export.cpython-312.pyc
  ops_tracing/__pycache__/_mock.cpython-312.pyc
  ops_tracing/_api.py
  ops_tracing/_backend.py
  ops_tracing/_buffer.py
  ops_tracing/_export.py
  ops_tracing/_mock.py
  ops_tracing/py.typed
  ops_tracing/vendor/charms/certificate_transfer_interface/v1/__pycache__/certificate_transfer.cpython-312.pyc
  ops_tracing/vendor/charms/certificate_transfer_interface/v1/certificate_transfer.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 50s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/ops-tracing/#history**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 8000,
  "url": "https://pypi.org/project/ops-tracing/#history"
}
```

</details>

```
Contents of https://pypi.org/project/ops-tracing/#history:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 7m 55s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/ops-tracing/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 8000,
  "url": "https://pypi.org/project/ops-tracing/"
}
```

</details>

```
Contents of https://pypi.org/project/ops-tracing/:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 8m 3s</sub>

### ✅ `bash`

**Check ops-tracing mock module**

$ python3 -c "
import inspect, ops_tracing._mock as m
print(dir(m))
print(inspect.getsource(m))
" 2>/dev/null | head -40

<details>
<summary>32 lines</summary>

```
['Generator', 'InMemorySpanExporter', 'Resource', 'SPAN_PROCESSOR', 'SimpleSpanProcessor', 'TracerProvider', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', '_backend', '_create_provider', 'annotations', 'contextlib', 'opentelemetry', 'patch_tracing', 'pathlib']
# Copyright 2025 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Mock implementations for testing."""

from __future__ import annotations

import contextlib
import pathlib
from typing import Generator

import opentelemetry.trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from . import _backend

# A global SPAN_PROCESSOR that will be captured by every tracer object
# (ops._private.tracer, charm.tracer, lib.charms.foo.tracer) on first use.
# The dummy argument is mandatory and will be overridden in patch_tracing().
SPAN_PROCESSOR = SimpleSpanProcessor(InMemorySpanExporter())


@contextlib.contextmanager
def patch_tracing() -> Generator[InMemorySpanExporter, None, None]:
    """Patch ops[tracing] for unit tests.

    Replaces the real buffer and exporter with an in-memory store.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 13s</sub>

### ✅ `bash`

**Get full ops_tracing mock source**

$ python3 -c "
import inspect, ops_tracing._mock as m
print(inspect.getsource(m))
" 2>/dev/null

<details>
<summary>57 lines</summary>

```
# Copyright 2025 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""Mock implementations for testing."""

from __future__ import annotations

import contextlib
import pathlib
from typing import Generator

import opentelemetry.trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from . import _backend

# A global SPAN_PROCESSOR that will be captured by every tracer object
# (ops._private.tracer, charm.tracer, lib.charms.foo.tracer) on first use.
# The dummy argument is mandatory and will be overridden in patch_tracing().
SPAN_PROCESSOR = SimpleSpanProcessor(InMemorySpanExporter())


@contextlib.contextmanager
def patch_tracing() -> Generator[InMemorySpanExporter, None, None]:
    """Patch ops[tracing] for unit tests.

    Replaces the real buffer and exporter with an in-memory store.
    This effectively removes the requirement for unique directories for each unit test.
    """
    # Work around OpenTelemetry tracer provider singleton enforcement.
    real_otel_provider = opentelemetry.trace._TRACER_PROVIDER
    real_otel_once_done = opentelemetry.trace._TRACER_PROVIDER_SET_ONCE._done
    real_create_provider = _backend._create_provider
    real_exporter = _backend._exporter
    dummy_exporter = SPAN_PROCESSOR.span_exporter

    # An exporter that accumulates trace data from one Scenario context.run().
    exporter = InMemorySpanExporter()
    SPAN_PROCESSOR.span_exporter = exporter

    _backend._create_provider = _create_provider
    _backend._exporter = None
    try:
        yield exporter
    finally:
        SPAN_PROCESSOR.span_exporter = dummy_exporter
        _backend._exporter = real_exporter
        _backend._create_provider = real_create_provider
        opentelemetry.trace._TRACER_PROVIDER = real_otel_provider
        opentelemetry.trace._TRACER_PROVIDER_SET_ONCE._done = real_otel_once_done


def _create_provider(resource: Resource, charm_dir: pathlib.Path) -> TracerProvider:
    """Create an OpenTelemetry tracing provider suitable for testing."""
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(SPAN_PROCESSOR)
    return provider
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 13s</sub>

### ✅ `bash`

**Check tracing usage in tests**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -rn "ops_tracing\|tracing" tests/ | grep -v "#\|Binary\|tempo\|charm_tracing\|workload_tracing\|tracing_endpoint\|tracing-\|tracing_resource" | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 8m 43s</sub>

### ✅ `bash`

**Check Relation data schema APIs**

$ python3 -c "
import inspect, ops
# Check Relation class for data schema methods
r = ops.Relation
for name in dir(r):
    if 'load' in name.lower() or 'save' in name.lower() or 'schema' in name.lower():
        print(name)
print('---')
# Look for RelationDataSchema or similar
for name in dir(ops):
    if 'schema' in name.lower() or 'Schema' in name:
        print('ops.' + name)
"

```
load
save
---
<exited with exit code 0>
```


---

<sub>⏱️ 8m 51s</sub>

### ✅ `bash`

**Check Relation.load and Relation.save**

$ python3 -c "
import inspect, ops
# Check Relation.load and Relation.save
print(inspect.getsource(ops.RelationData.load))
print('---')
print(inspect.getsource(ops.RelationData.save))
" 2>/dev/null | head -60

```

<exited with exit code 0>
```


---

<sub>⏱️ 8m 58s</sub>

### ✅ `bash`

**Find Relation load/save methods**

$ python3 -c "
import inspect, ops.model
src = inspect.getsource(ops.model)
import re
# Find load/save on relation data classes
for m in re.finditer(r'def (load|save)\b', src):
    start = max(0, m.start() - 200)
    end = min(len(src), m.start() + 500)
    print(src[start:end])
    print('===')
" 2>/dev/null | head -100

<details>
<summary>39 lines</summary>

```
""
        if self._remote_model is None:
            d = self._backend.relation_model_get(self.id)
            self._remote_model = RemoteModel(uuid=d['uuid'])
        return self._remote_model

    def load(
        self,
        cls: type[_T],
        src: Unit | Application,
        *args: Any,
        decoder: Callable[[str], Any] | None = None,
        **kwargs: Any,
    ) -> _T:
        """Load the data for this relation into an instance of a data class.

        The raw Juju relation data is passed to the data class's ``__init__``
        method as keyword arguments, with values decoded using the provided
        decoder function, or :func:`json.loads` if no decoder is provided.

   
===
alue = decoder(value)
            if fields is None:
                data[key] = value
            elif key in fields:
                data[fields[key]] = value
        return cls(*args, **data)

    def save(
        self,
        obj: object,
        dst: Unit | Application,
        *,
        encoder: Callable[[Any], str] | None = None,
    ):
        """Save the data from the provided object to the Juju relation data.

        For example::

            relation = self.model.get_relation('tracing')
            data = TracingRequirerData(receivers=['otlp_http'])
            relation.save(data, self.app)

        For dataclasses and Pydantic ``BaseModel`` subclasses, only the class's
     
===
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 6s</sub>

### ✅ `bash`

**Look at relation.py**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat src/relation.py

<details>
<summary>28 lines</summary>

```
# Copyright 2025 Canonical
# See LICENSE file for licensing details.
"""Relation class."""
import json
from typing import Any, Optional
import ops

class Relation:
    """A helper class to manage relation data."""

    def __init__(self, app:ops.Application, relation: Optional[ops.Relation]):
        self._relation = relation
        self._app = app

    @property
    def data(self):
        """Return relation data."""
        if self._relation:
            return self._relation.data
        return None

    def set_app_data(self, key: str, data: Any) -> None:
        """Put information into the app data bucket."""
        if self.data:
            self.data[self._app][key] = json.dumps(data)

    def get_app_data(self, key: str) -> Any:
        """Retrieve information from the app data bucket."""
        if not self.data:
            return {}
        data = self.data[self._app].get(key, "")
        return json.loads(data) if data else {}
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 18s</sub>

### ✅ `bash`

**Check ops-tracing backend**

$ python3 -c "
import inspect, ops_tracing._backend as b
src = inspect.getsource(b)
print(src[:3000])
"

<details>
<summary>64 lines</summary>

```
# Copyright 2025 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

"""The global implementation of the ops-tracing extension."""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_tracer_provider, set_tracer_provider
from ops._private import yaml

if TYPE_CHECKING:
    from ops import JujuContext

from ._buffer import Destination
from ._export import BufferingSpanExporter

BUFFER_FILENAME: str = '.tracing-data.db'
"""Name of the buffer file where the trace data is stored, next to .unit-state.db."""

_exporter: BufferingSpanExporter | None = None
"""A reference to the exporter that we passed to OpenTelemetry SDK at setup."""


def setup(juju_context: JujuContext, charm_class_name: str) -> None:
    """Set up the tracing subsystem and configure OpenTelemetry.

    Args:
        juju_context: the context for this dispatch, for annotation
        charm_class_name: the name of the charm class, for annotation
    """
    app_name, unit_number = juju_context.unit_name.split('/', 1)
    try:
        meta = yaml.safe_load((juju_context.charm_dir / 'metadata.yaml').read_text())
        charmhub_charm_name = meta['name']
    except FileNotFoundError:
        charmhub_charm_name = '[unknown]'

    resource = Resource.create(
        attributes={
            'service.namespace': juju_context.model_uuid,
            'service.namespace.name': juju_context.model_name,
            'service.name': app_name,
            'service.instance.id': unit_number,
            'charm': charmhub_charm_name,
            'charm_type': charm_class_name,
            'juju_model': juju_context.model_name,
            'juju_model_uuid': juju_context.model_uuid,
            'juju_application': app_name,
            'juju_unit': juju_context.unit_name,
        }
    )
    set_tracer_provider(_create_provider(resource, juju_context.charm_dir))


def _create_provider(resource: Resource, charm_dir: pathlib.Path) -> TracerProvider:
    """Create the OpenTelemetry tracer provider."""
    # Separate function so that it's easy to override in tests
    global _exporter
    _exporter = BufferingSpanExporter(charm_dir / BUFFER_FILENAME)
    span_processor = BatchSpanProcessor(_exporter)
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(span
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 31s</sub>

### ✅ `bash`

**Check ops_tracing __init__ to understand setup**

$ python3 -c "
import inspect, ops_tracing
src = inspect.getsource(ops_tracing)
print(src[:2000])
"

<details>
<summary>50 lines</summary>

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
            self.tracing = ops.tracin
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 41s</sub>

### ✅ `bash`

**Check ops_tracing _api module**

$ python3 -c "
import inspect, ops_tracing._api as api
src = inspect.getsource(api)
print(src[:3000])
"

<details>
<summary>79 lines</summary>

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
        """Initialise the tracing
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 2s</sub>

### ✅ `bash`

**Get rest of ops_tracing API source**

$ python3 -c "
import inspect, ops_tracing._api as api
# Get full source to understand what Tracing class does
src = inspect.getsource(api)
print(src[3000:])
"

<details>
<summary>101 lines</summary>

```
service."""
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 18s</sub>

### ✅ `bash`

**Look at TLS-related relations**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && cat charmcraft.yaml | grep -A 6 "charm-tracing\|receive-ca-cert\|certificates"

<details>
<summary>21 lines</summary>

```
certificates:
    interface: tls-certificates
    limit: 1
    optional: true
    description: Certificate and key files for Grafana to use with TLS.
  receive-ca-cert:
    interface: certificate_transfer
    optional: true
    description: |
      Receive a CA cert for grafana to trust.
      This relation can be used with a local CA to obtain the CA cert that was used to sign proxied
      endpoints.
--
  charm-tracing:
    description: |
      Enables sending charm traces to a distributed tracing backend such as Tempo.
    limit: 1
    optional: true
    interface: tracing
  workload-tracing:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 36s</sub>

### ✅ `bash`

**Check ops_tracing API**

$ python3 -c "
import ops_tracing
print('set_destination:', hasattr(ops_tracing, 'set_destination'))
print('Tracing:', hasattr(ops_tracing, 'Tracing'))
import inspect
if hasattr(ops_tracing, 'set_destination'):
    print(inspect.getsource(ops_tracing.set_destination))
"

<details>
<summary>20 lines</summary>

```
set_destination: True
Tracing: True
def set_destination(url: str | None, ca: str | None) -> None:
    """Configure the destination service for trace data.

    Args:
        url: the URL of the telemetry service to send trace data to.
            An example could be ``http://localhost/v1/traces``.
            None or empty string disables sending out the data, which is still buffered.
        ca: the CA list (PEM bundle, a multi-line string), only used for HTTPS URLs.
    """
    if url and not url.startswith(('http://', 'https://')):
        raise ValueError('Only HTTP and HTTPS tracing destinations are supported.')

    config = Destination(url, ca)

    if not _exporter:
        # Perhaps our tracer provider was never set up.
        return

    if config == _exporter.buffer.load_destination():
        return
    _exporter.buffer.save_destination(config)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 27s</sub>

### 💬 Copilot

Let me now check how ops.testing Context finds the metadata and whether the tests currently work:

---

<sub>⏱️ 11m 27s</sub>

### ✅ `bash`

**Check how Context finds metadata**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && python3 -c "
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'lib')
import ops.testing as t
import inspect
# Check how Context.__init__ finds metadata
src = inspect.getsource(t.Context.__init__)
print(src[:3000])
" 2>/dev/null | head -80

<details>
<summary>50 lines</summary>

```
def __init__(
        self,
        charm_type: type[CharmType],
        meta: dict[str, Any] | None = None,
        *,
        actions: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
        charm_root: str | pathlib.Path | None = None,
        juju_version: str = _DEFAULT_JUJU_VERSION,
        capture_deferred_events: bool = False,
        capture_framework_events: bool = False,
        app_name: str | None = None,
        unit_id: int | None = 0,
        machine_id: str | None = None,
        availability_zone: str | None = None,
        principal_unit: str | None = None,
        app_trusted: bool = False,
    ):
        """Represents a simulated charm's execution context.

        If the charm, say, expects a ``./src/foo/bar.yaml`` file present relative to the
        execution cwd, you need to use the ``charm_root`` argument. For example::

            import tempfile
            virtual_root = tempfile.TemporaryDirectory()
            local_path = Path(local_path.name)
            (local_path / 'foo').mkdir()
            (local_path / 'foo' / 'bar.yaml').write_text('foo: bar')
            Context(... charm_root=virtual_root).run(...)

        :arg charm_type: the :class:`ops.CharmBase` subclass to handle the event.
        :arg meta: charm metadata to use. Needs to be a valid metadata.yaml format (as a dict).
            Alternatively, can be a full ``charmcraft.yaml`` dict, in which case ``config`` and
            ``actions`` will be automatically extracted from it (if not explicitly provided).
            Otherwise, if no meta, actions, or config were provided, will be loaded from the
            ``charmcraft.yaml`` file in the charm root (falling back to ``metadata.yaml``).
            If the ``charmcraft.yaml`` contains an ``extensions`` key (e.g.
            ``extensions: [flask-framework]``), the extension's metadata,
            config, and actions will be automatically merged in.
        :arg actions: charm actions to use. Needs to be a valid actions.yaml format (as a dict).
            If none is provided, will be extracted from ``meta`` if present.
            Otherwise, if no meta, actions, or config were provided, will be loaded from the
            ``charmcraft.yaml`` file in the charm root (falling back to ``actions.yaml``).
        :arg config: charm config to use. Needs to be a valid config.yaml format (as a dict).
            If none is provided, will be extracted from ``meta`` if present
            Otherwise, if no meta, actions, or config were provided, will be loaded from the
            ``charmcraft.yaml`` file in the charm root (falling back to ``config.yaml``).
        :arg juju_version: Juju agent version to simulate.
        :arg app_name: App name that this charm is deployed as. Defaults to the charm name as
            defined in the metadata.
        :arg unit_id: Unit ID that this charm is deployed as, surfaced to the charm in the
            JUJU_UNIT_NAME envvar. Defaults to 0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 47s</sub>

### ✅ `bash`

**Check how charm_root is determined in Context**

$ python3 -c "
import sys
sys.path.insert(0, '/tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/src')
sys.path.insert(0, '/tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/lib')
import ops.testing as t
import inspect
src = inspect.getsource(t.Context.__init__)
# Find where charm_root is determined
idx = src.find('charm_root')
print(src[idx:idx+2000])
" 2>/dev/null | head -60

<details>
<summary>33 lines</summary>

```
charm_root: str | pathlib.Path | None = None,
        juju_version: str = _DEFAULT_JUJU_VERSION,
        capture_deferred_events: bool = False,
        capture_framework_events: bool = False,
        app_name: str | None = None,
        unit_id: int | None = 0,
        machine_id: str | None = None,
        availability_zone: str | None = None,
        principal_unit: str | None = None,
        app_trusted: bool = False,
    ):
        """Represents a simulated charm's execution context.

        If the charm, say, expects a ``./src/foo/bar.yaml`` file present relative to the
        execution cwd, you need to use the ``charm_root`` argument. For example::

            import tempfile
            virtual_root = tempfile.TemporaryDirectory()
            local_path = Path(local_path.name)
            (local_path / 'foo').mkdir()
            (local_path / 'foo' / 'bar.yaml').write_text('foo: bar')
            Context(... charm_root=virtual_root).run(...)

        :arg charm_type: the :class:`ops.CharmBase` subclass to handle the event.
        :arg meta: charm metadata to use. Needs to be a valid metadata.yaml format (as a dict).
            Alternatively, can be a full ``charmcraft.yaml`` dict, in which case ``config`` and
            ``actions`` will be automatically extracted from it (if not explicitly provided).
            Otherwise, if no meta, actions, or config were provided, will be loaded from the
            ``charmcraft.yaml`` file in the charm root (falling back to ``metadata.yaml``).
            If the ``charmcraft.yaml`` contains an ``extensions`` key (e.g.
            ``extensions: [flask-framework]``), the extension's metadata,
            config, and actions will be automatically merged in.
        :arg actions: charm actions to use. Needs to be a valid actions.yaml format (as a dict).
            If none is provided, will be extracted from ``meta`` if present.
            Otherwise, if no meta, actions, or config were provided, will be loaded from th
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12m 2s</sub>

### 💬 Copilot

Let me now run the existing tests to establish a baseline:

---

<sub>⏱️ 12m 2s</sub>

### ✅ `bash`

**Check if uv dependencies are ready**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && uv run --frozen --isolated --extra=dev --no-sync -- python -c "import ops; print(ops.__version__)" 2>/dev/null || echo "uv run failed - let me check"

```
uv run failed - let me check
<exited with exit code 0>
```


---

<sub>⏱️ 12m 18s</sub>

### ✅ `bash`

**Try running with uv**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && uv run --extra=dev python -c "import ops; print(ops.__version__)" 2>&1 | head -20

<details>
<summary>6 lines</summary>

```
warning: The `requires-python` specifier (`~=3.8`) in `grafana-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: .venv
Installed 119 packages in 52ms
3.3.1
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 13m 14s</sub>

### ✅ `bash`

**Check trusted_cert_transfer usage**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -n "trusted_cert_transfer\|trusted_ca_certs" src/charm.py

<details>
<summary>6 lines</summary>

```
127:        # -- trusted_cert_transfer
128:        self.trusted_cert_transfer = CertificateTransferRequires(self, "receive-ca-cert")
220:                                        trusted_ca_certs = self._trusted_ca_certs,
292:    def _trusted_ca_certs(self) -> Optional[str]:
293:        if certs := self.trusted_cert_transfer.get_all_certificates():
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 13m 20s</sub>

### ✅ `bash`

**Check _trusted_ca_certs property**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && sed -n '292,300p' src/charm.py

<details>
<summary>9 lines</summary>

```
def _trusted_ca_certs(self) -> Optional[str]:
        if certs := self.trusted_cert_transfer.get_all_certificates():
            return "\n".join(certs)
        return None

    @property
    def unique_name(self):
        """Returns a unique identifier for this application."""
        return "juju_{}_{}_{}_{}".format(
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 13m 39s</sub>

### ✅ `bash`

**Check TracingEndpointRequirer class**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -n "class TracingEndpointRequirer" lib/charms/tempo_coordinator_k8s/v0/tracing.py | head -5

```
734:class TracingEndpointRequirerEvents(CharmEvents):
741:class TracingEndpointRequirer(Object):
<exited with exit code 0>
```


---

<sub>⏱️ 13m 39s</sub>

### ✅ `bash`

**Check TracingEndpointRequirer init**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -n "def __init__" lib/charms/tempo_coordinator_k8s/v0/tracing.py | head -10

<details>
<summary>10 lines</summary>

```
21:    def __init__(self, *args):
66:    def __init__(self, *args):
413:    def __init__(self, handle, relation, *args, **kwargs):
451:    def __init__(self, relation_name: str):
460:    def __init__(
479:    def __init__(
587:    def __init__(
746:    def __init__(
974:    >>>     def __init__(self, ...):
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 13m 45s</sub>

### ✅ `bash`

**Check TracingEndpointRequirer __init__**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && sed -n '746,800p' lib/charms/tempo_coordinator_k8s/v0/tracing.py

<details>
<summary>48 lines</summary>

```
def __init__(
        self,
        charm: CharmBase,
        relation_name: str = DEFAULT_RELATION_NAME,
        protocols: Optional[List[ReceiverProtocol]] = None,
    ):
        """Construct a tracing requirer for a Tempo charm.

        If your application supports pushing traces to a distributed tracing backend, the
        `TracingEndpointRequirer` object enables your charm to easily access endpoint information
        exchanged over a `tracing` relation interface.

        Args:
            charm: a `CharmBase` object that manages this
                `TracingEndpointRequirer` object. Typically, this is `self` in the instantiating
                class.
            relation_name: an optional string name of the relation between `charm`
                and the Tempo charmed service. The default is "tracing". It is strongly
                advised not to change the default, so that people deploying your charm will have a
                consistent experience with all other charms that provide tracing endpoints.
            protocols: optional list of protocols that the charm intends to send traces with.
                The provider will enable receivers for these and only these protocols,
                so be sure to enable all protocols the charm or its workload are going to need.

        Raises:
            RelationNotFoundError: If there is no relation in the charm's metadata.yaml
                with the same name as provided via `relation_name` argument.
            RelationInterfaceMismatchError: The relation with the same name as provided
                via `relation_name` argument does not have the `tracing` relation
                interface.
            RelationRoleMismatchError: If the relation with the same name as provided
                via `relation_name` argument does not have the `RelationRole.provides`
                role.
        """
        _validate_relation_by_interface_and_direction(
            charm, relation_name, RELATION_INTERFACE_NAME, RelationRole.requires
        )

        super().__init__(charm, relation_name)

        self._is_single_endpoint = charm.meta.relations[relation_name].limit == 1

        self._charm = charm
        self._relation_name = relation_name

        events = self._charm.on[self._relation_name]
        self.framework.observe(
            events.relation_changed, self._on_tracing_relation_changed
        )
        self.framework.observe(events.relation_broken, self._on_tracing_relation_broken)

        if protocols and self._charm.unit.is_leader():
            # we can't be sure that the current event context supports read/writing relation data for this relation,
            # so we catch ModelErrors. This is because we're doing this in init.
            try:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 14m 5s</sub>

### ✅ `bash`

**Find all charm_tracing usages**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -n "charm_tracing" src/charm.py

```
157:        self.charm_tracing = TracingEndpointRequirer(
433:        if self.charm_tracing.is_ready() and (endpoint:= self.charm_tracing.get_endpoint("otlp_http")):
<exited with exit code 0>
```


---

<sub>⏱️ 14m 13s</sub>

### ✅ `bash`

**Check TracingEndpointRequirer and workload_tracing usage**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && grep -n "TracingEndpointRequirer\|workload_tracing" src/charm.py

<details>
<summary>9 lines</summary>

```
63:from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer
157:        self.charm_tracing = TracingEndpointRequirer(
160:        self.workload_tracing = TracingEndpointRequirer(
211:                                            tracing_endpoint=self._workload_tracing_endpoint,
329:    def _workload_tracing_endpoint(self) -> Optional[str]:
330:        if self.workload_tracing.is_ready():
331:            endpoint = self.workload_tracing.get_endpoint("otlp_grpc")
347:                            if self._workload_tracing_endpoint
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 14m 25s</sub>

### 💬 Copilot

Now I have a complete picture. Let me create a branch and implement all the changes:

---

<sub>⏱️ 14m 25s</sub>

### ✅ `bash`

**Create upgrade branch**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4 && git checkout -b ops-upgrade-3.7

```
Switched to a new branch 'ops-upgrade-3.7'
<exited with exit code 0>
```


---

<sub>⏱️ 14m 32s</sub>

### 💬 Copilot

Now let me make all the changes:

---

<sub>⏱️ 14m 32s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 14m 39s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 14m 39s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 14m 47s</sub>

### 💬 Copilot

Now add `SCENARIO_BARE_CHARM_ERRORS=true` to tox.ini:

---

<sub>⏱️ 14m 47s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/tox.ini.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/tox.ini

```
File /tmp/ops-upgrade-experiment/grafana-k8s-operator__all__C4/tox.ini updated with changes.
```


---

<sub>⏱️ 14m 57s</sub>

### 💬 Copilot

Now add `CharmConfig` to `src/models.py`:

---

<sub>⏱️ 14m 57s</sub>

### ❌ `edit`

**edit file**

<details>
<summary>Arguments</summary>

```json
{
  "new_str": "# Copyright 2025 Canonical\n# See LICENSE file for licensing details.\n\n\"\"\"Data models class.\"\"\"\n\nimport dataclasses\nfrom typing import Callable, List, Optional\n\n\n@dataclasses.dataclass\nclass CharmConfig:\n    \"\"\"Typed representation of the charm's Juju config options.\"\"\"\n\n    allow_anonymous_access: bool = False\n    allow_embedding: bool = False\n    log_level: str = \"info\"\n    admin_user: str = \"admin\"\n    web_external_url: str = \"\"\n    enable_auto_assign_org: bool = True\n    datasource_query_timeout: int = 300\n    cpu: Optional[str] = None\n    memory: Optional[str] = None\n    reporting_enabled: bool = True\n    custom_config: Optional[str] = None",
  "old_str": "# Copyright 2025 Canonical\n# See LICENSE file for licensing details.\n\n\"\"\"Data models class.\"\"\"\n\nimport dataclasses\nfrom typing import Callable, List, Optional"
}
```

</details>

```
"path": Required
```


---

<sub>⏱️ 14m 57s</sub>

### ℹ️ Info

Operation cancelled by user

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
