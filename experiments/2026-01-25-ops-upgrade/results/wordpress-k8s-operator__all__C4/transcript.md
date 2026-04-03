# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `cba0ffea-96a7-4122-85af-a63adac05d88`  
> - **Started:** 4/3/2026, 12:34:55 PM  
> - **Duration:** 6m 16s  
> - **Exported:** 4/3/2026, 12:41:12 PM  

---

<sub>⏱️ 5s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 13s</sub>

### ✅ `bash`

**Check current ops version and charm config**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && cat pyproject.toml | grep -A5 "ops" && echo "---" && cat charmcraft.yaml | head -50

<details>
<summary>23 lines</summary>

```
"ops==3.5.1",
  "pydantic==2.12.5",
  "requests==2.32.5",
]

[dependency-groups]
---
# Copyright 2024 Canonical Ltd.
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 13s</sub>

### ✅ `bash`

**List source files**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && find src tests -name "*.py" | head -30 && echo "---" && ls src/

<details>
<summary>24 lines</summary>

```
src/exceptions.py
src/types_.py
src/state.py
src/charm.py
src/cos.py
tests/conftest.py
tests/integration/test_machine.py
tests/integration/test_ingress.py
tests/integration/conftest.py
tests/integration/test_cos_grafana.py
tests/integration/test_cos_loki.py
tests/integration/test_cos_prometheus.py
tests/integration/helper.py
tests/integration/test_external.py
tests/integration/test_addon.py
tests/integration/test_core.py
tests/unit/conftest.py
tests/unit/test_charm.py
tests/unit/wordpress_mock.py
tests/unit/__init__.py
tests/__init__.py
---
charm.py  cos.py  exceptions.py  grafana_dashboards  loki_alert_rules  state.py  types_.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 18s</sub>

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

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Read main charm file**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && cat src/charm.py

<details>
<summary>25 lines</summary>

```
Output too large to read at once (63.1 KB). Saved to: /tmp/copilot-tool-output-1775172913567-9dpixl.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm for WordPress on kubernetes."""

import itertools
import json
import logging
import os
import re
import secrets
import string
import textwrap
import time
import traceback
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union, cast

import mysql.connector
import ops.charm
import ops.pebble
import yaml
from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
f
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 25s</sub>

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

<sub>⏱️ 24s</sub>

### ✅ `bash`

**Read charm imports and class setup**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && cat src/charm.py | head -150

<details>
<summary>133 lines</summary>

```
#!/usr/bin/env python3

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm for WordPress on kubernetes."""

import itertools
import json
import logging
import os
import re
import secrets
import string
import textwrap
import time
import traceback
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union, cast

import mysql.connector
import ops.charm
import ops.pebble
import yaml
from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from ops.charm import ActionEvent, CharmBase, HookEvent, PebbleReadyEvent, UpgradeCharmEvent
from ops.framework import EventBase
from ops.main import main
from ops.model import ActiveStatus, RelationDataContent, WaitingStatus
from ops.pebble import ExecProcess
from yaml import safe_load

import exceptions
import types_
from cos import (
    _APACHE_EXPORTER_PEBBLE_SERVICE,
    APACHE_LOG_PATHS,
    PROM_EXPORTER_PEBBLE_CONFIG,
    ApacheLogProxyConsumer,
)
from state import CharmConfigInvalidError, State

# MySQL logger prints database credentials on debug level, silence it
logging.getLogger(mysql.connector.__name__).setLevel(logging.WARNING)
logger = logging.getLogger()


class WordpressCharm(CharmBase):
    """Charm for WordPress on kubernetes."""

    class _ReplicaRelationNotReady(Exception):  # noqa: N818 (private exception used internally)
        """Replica databag was accessed before peer relations are established."""

    _WP_CONFIG_PATH = "/var/www/html/wp-config.php"
    _WP_UPLOADS_PATH = "/var/www/html/wp-content/uploads"
    _PHP_INI_PATH = "/etc/php/8.3/apache2/php.ini"
    _CONTAINER_NAME = "wordpress"
    _SERVICE_NAME = "wordpress"
    _WORDPRESS_USER = "_daemon_"
    _WORDPRESS_GROUP = "_daemon_"
    _WORDPRESS_DB_CHARSET = "utf8mb4"
    _DATABASE_RELATION_NAME = "database"
    _DEFAULT_MYSQL_PORT = 3306

    # Default themes and plugins are installed in oci image build time and defined in Dockerfile
    _WORDPRESS_DEFAULT_THEMES: ClassVar[List[str]] = [
        "launchpad",
        "light-wordpress-theme",
        "mscom",
        "thematic",
        "twentytwentyfive",
        "twentytwentyfour",
        "twentytwentythree",
        "twentytwentytwo",
        "ubuntu-cloud-website",
        "ubuntu-community-wordpress-theme/ubuntu-community",
        "ubuntu-community/ubuntu-community",
        "ubuntu-fi",
        "ubuntu-light",
        "ubuntustudio-wp/ubuntustudio-wp",
        "xubuntu-website/xubuntu-eighteen",
        "xubuntu-website/xubuntu-fifteen",
        "xubuntu-website/xubuntu-fourteen",
        "xubuntu-website/xubuntu-thirteen",
    ]

    _WORDPRESS_DEFAULT_PLUGINS: ClassVar[List[str]] = [
        "404page",
        "akismet",
        "all-in-one-event-calendar",
        "powerpress",
        "coschedule-by-todaymade",
        "elementor",
        "essential-addons-for-elementor-lite",
        "favicon-by-realfavicongenerator",
        "feedwordpress",
        "genesis-columns-advanced",
        "hello",
        "line-break-shortcode",
        "wp-mastodon-share",
        "no-category-base-wpml",
        "openid",
        "wordpress-launchpad-integration",
        "wordpress-teams-integration",
        "openstack-objectstorage-k8s",
        "post-grid",
        "redirection",
        "relative-image-urls",
        "rel-publisher",
        "safe-svg",
        "show-current-template",
        "simple-301-redirects",
        "simple-custom-css",
        "so-widgets-bundle",
        "svg-support",
        "syntaxhighlighter",
        "wordpress-importer",
        "wp-markdown",
        "wp-polls",
        "wp-font-awesome",
        "wp-lightbox-2",
        "wp-statistics",
        "xubuntu-team-members",
        "wordpress-seo",
    ]

    _DB_CHECK_INTERVAL = 5
    _DB_CHECK_TIMEOUT = 60 * 10

    def __init__(self, *args, **kwargs):
        """Initialize the instance.

        Args:
            args: arguments passed into Charmbase superclass.
            kwargs: keyword arguments passed into Charmbase superclass.
        """
        super().__init__(*args, **kwargs)

        try:
            self.state = State.from_charm(self)
        except CharmConfigInvalidError as exc:
            self.unit.status = ops.BlockedStatus(exc.msg)
            return

        self.database = DatabaseRequires(
            self, relation_name=self._DATABASE_RELATION_NAME, database_name=self.app.name
        )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 33s</sub>

### ✅ `bash`

**Read unit test files**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && cat tests/unit/conftest.py && echo "===" && head -100 tests/unit/test_charm.py

<details>
<summary>337 lines</summary>

```
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for WordPress charm unit tests."""

import typing
import unittest
import unittest.mock

import ops.pebble
import ops.testing
import pytest

from charm import WordpressCharm
from tests.unit.wordpress_mock import WordpressPatch


@pytest.fixture(scope="function", name="patch")
def patch_fixture():
    """Enable WordPress patch system, used in combine with :class:`ops.testing.Harness`.

    Yields:
        The instance of :class:`tests.unit.wordpress_mock.WordpressPatch`, which can be used to
        inspect the WordPress mocking system (mocking db, mocking file system, etc).
    """
    patch = WordpressPatch()
    patch.start()
    yield patch
    patch.stop()


@pytest.fixture(scope="function", name="harness")
def harness_fixture(patch: WordpressPatch):  # pylint: disable=unused-argument
    """Enable ops test framework harness."""
    harness = ops.testing.Harness(WordpressCharm)
    yield harness
    harness.cleanup()


@pytest.fixture(scope="function", name="app_name")
def app_name_fixture():
    """The name of the charm application."""
    return "wordpress-k8s"


@pytest.fixture(scope="function", name="setup_replica_consensus")
def setup_replica_consensus_fixture(harness: ops.testing.Harness, app_name: str):
    """Returns a function that can be used to set up peer relation.

    After calling the yielded function, the replica consensus including WordPress salt keys and
    secrets will be populated. The unit will become a leader unit in this process.
    """

    def _setup_replica_consensus():
        """Function to set up peer relation. See fixture docstring for more information.

        Returns:
            Relation data for WordPress peers. Includes WordPress salt keys and secrets.
        """
        replica_relation_id = harness.add_relation("wordpress-replica", app_name)
        harness.add_storage("uploads")
        harness.set_leader()
        harness.begin_with_initial_hooks()
        harness.framework.reemit()
        consensus = harness.get_relation_data(replica_relation_id, app_name)
        return consensus

    return _setup_replica_consensus


@pytest.fixture(scope="function", name="example_database_host_port")
def example_database_host_port_fixture():
    """An example database connection host and port tuple."""
    return ("test_database_host", "3306")


@pytest.fixture(scope="function", name="example_database_info")
def example_database_info_fixture(example_database_host_port: typing.Tuple[str, str]):
    """An example database connection info from mysql_client interface."""
    return {
        "endpoints": ":".join(example_database_host_port),
        "database": "test_database_name",
        "username": "test_database_user",
        "password": "test_database_password",
    }


@pytest.fixture(scope="function", name="example_invalid_database_info")
def example_invalid_database_info_fixture():
    """An example database connection info from mysql_client interface."""
    return {
        "endpoints": "test_database_host:1234",
        "database": "test_database_name",
        "username": "test_database_user",
        "password": "test_database_password",
    }


@pytest.fixture(scope="function", name="example_database_info_no_port")
def example_database_info_no_port_fixture():
    """An example database connection info from mysql_client interface."""
    return {
        "endpoints": "test_database_host",
        "database": "test_database_name",
        "username": "test_database_user",
        "password": "test_database_password",
    }


@pytest.fixture(scope="function", name="example_database_info_no_port_diff_host")
def example_database_info_no_port_diff_host_fixture():
    """An example database connection info from mysql_client interface."""
    return {
        "endpoints": "test_database_host2",
        "database": "test_database_name",
        "username": "test_database_user",
        "password": "test_database_password",
    }


@pytest.fixture(scope="function", name="example_database_info_connection_error")
def example_database_info_connection_error_fixture():
    """An example database connection info from mysql_client interface."""
    return {
        "endpoints": "a",
        "database": "b",
        "username": "c",
        "password": "d",
    }


@pytest.fixture(scope="function")
def setup_database_relation(
    harness: ops.testing.Harness, example_database_info: typing.Dict[str, str]
):
    """Returns a function that can be used to set up database relation.

    After calling the yielded function, a database relation will be set up. example_database_info
    will be used as the relation data. Return a tuple of relation id and the relation data.
    """

    def _setup_database_relation():
        """Function to set up database relation. See fixture docstring for more information.

        Returns:
            Tuple of relation id and relation data.
        """
        db_relation_id = harness.add_relation("database", "mysql")
        harness.add_relation_unit(db_relation_id, "mysql/0")
        harness.update_relation_data(db_relation_id, "mysql", example_database_info)
        return db_relation_id, example_database_info

    return _setup_database_relation


@pytest.fixture(scope="function", name="setup_database_relation_no_port")
def setup_database_relation_no_port_fixture(
    harness: ops.testing.Harness, example_database_info_no_port: typing.Dict[str, str]
):
    """Returns a function that can be used to set up database relation.

    After calling the yielded function, a database relation will be set up. example_database_info
    will be used as the relation data. Return a tuple of relation id and the relation data.
    """

    def _setup_database_relation():
        """Function to set up database relation. See fixture docstring for more information.

        Returns:
            Tuple of relation id and relation data.
        """
        db_relation_id = harness.add_relation("database", "mysql")
        harness.add_relation_unit(db_relation_id, "mysql/0")
        harness.update_relation_data(db_relation_id, "mysql", example_database_info_no_port)
        return db_relation_id, example_database_info_no_port

    return _setup_database_relation


@pytest.fixture(scope="function")
def setup_database_relation_invalid_port(
    harness: ops.testing.Harness, example_invalid_database_info: typing.Dict[str, str]
):
    """Returns a function that can be used to set up database relation with a non 3306 port.

    After calling the yielded function, a database relation will be set up. example_database_info
    will be used as the relation data. Return a tuple of relation id and the relation data.
    """

    def _setup_database_relation():
        """Function to set up database relation. See fixture docstring for more information.

        Returns:
            Tuple of relation id and relation data.
        """
        db_relation_id = harness.add_relation("database", "mysql")
        harness.add_relation_unit(db_relation_id, "mysql/0")
        harness.update_relation_data(db_relation_id, "mysql", example_invalid_database_info)
        return db_relation_id, example_invalid_database_info

    return _setup_database_relation


@pytest.fixture(scope="function")
def setup_database_relation_connection_error(
    harness: ops.testing.Harness, example_database_info_connection_error: typing.Dict[str, str]
):
    """Returns a function that can be used to set up database relation with a non 3306 port.

    After calling the yielded function, a database relation will be set up.
    example_database_info_connection_error will be used as the relation data.
    Return a tuple of relation id and the relation data.
    """

    def _setup_database_relation():
        """Function to set up database relation. See fixture docstring for more information.

        Returns:
            Tuple of relation id and relation data.
        """
        db_relation_id = harness.add_relation("database", "mysql")
        harness.add_relation_unit(db_relation_id, "mysql/0")
        harness.update_relation_data(
            db_relation_id, "mysql", example_database_info_connection_error
        )
        return db_relation_id, example_database_info_connection_error

    return _setup_database_relation


@pytest.fixture(scope="function")
def action_event_mock():
    """Creates a mock object for :class:`ops.charm.ActionEvent`."""
    event_mock = unittest.mock.MagicMock()
    event_mock.set_results = unittest.mock.MagicMock()
    event_mock.fail = unittest.mock.MagicMock()
    return event_mock


@pytest.fixture(scope="function")
def run_standard_plugin_test(
    patch: WordpressPatch,
    harness: ops.testing.Harness,
    setup_replica_consensus: typing.Callable[[], dict],
    setup_database_relation_no_port: typing.Callable[[], typing.Tuple[int, dict]],
):
    """Returns a function that can be used to perform some general test for different plugins."""

    def _run_standard_plugin_test(
        plugin: str,
        plugin_config: typing.Dict[str, str],
        excepted_options: typing.Dict[str, typing.Any],
        excepted_options_after_removed: typing.Optional[typing.Dict[str, str]] = None,
        additional_check_after_install: typing.Optional[typing.Callable] = None,
    ):
        """Function to perform standard plugins test.

        Args:
            plugin: Name of WordPress standard plugin to test.
            plugin_config: Configurable parameters for WordPress plugins. See config.yaml for
                configuration details.
            excepted_options: Expected configurations of a given plugin.
            excepted_options_after_removed: Remaining options after plugin deactivation.
            additional_check_after_install: Callback to additional checks to perform after
                installation.
        """
        plugin_config_keys = list(plugin_config.keys())
        harness.set_can_connect(harness.model.unit.containers["wordpress"], True)
        setup_replica_consensus()
        _, db_info = setup_database_relation_no_port()
        patch.database.prepare_database(
            host=db_info["endpoints"],
            database=db_info["database"],
            user=db_info["username"],
            password=db_info["password"],
        )

        harness.update_config(plugin_config)

        database_instance = patch.database.get_wordpress_database(
            host="test_database_host", database="test_database_name"
        )
        assert database_instance
        assert (
            database_instance.activated_plugins == {plugin}
            if isinstance(plugin, str)
            else set(plugin)
        ), f"{plugin} should be activated after {plugin_config_keys} being set"
        assert database_instance.options == excepted_options, (
            f"options of plugin {plugin} should be set correctly"
        )

        if additional_check_after_install is not None:
            additional_check_after_install()

        harness.update_config(dict.fromkeys(plugin_config, ""))
        assert database_instance.activated_plugins == set(), (
            f"{plugin} should be deactivated after {plugin_config_keys} being reset"
        )
        assert (
            database_instance.options == {}
            if excepted_options_after_removed is None
            else excepted_options_after_removed
        ), f"{plugin} options should be removed after {plugin_config_keys} being reset"

    return _run_standard_plugin_test


@pytest.fixture(scope="function")
def attach_storage(
    patch: WordpressPatch,
):
    """Attach the "upload" storage to the mock container."""
    patch.container.fs["/proc/mounts"] = "/var/www/html/wp-content/uploads"
    yield
    patch.container.fs["/proc/mounts"] = ""
===
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""WordPress charm unit tests."""

# pylint:disable=protected-access

import json
import secrets
import textwrap
import typing
import unittest.mock

import ops.charm
import ops.testing
import pytest

import types_
from charm import WordpressCharm
from cos import REQUEST_DURATION_MICROSECONDS_BUCKETS
from exceptions import WordPressBlockedStatusException, WordPressWaitingStatusException
from tests.unit.wordpress_mock import WordpressContainerMock, WordpressPatch

BLOCKED_STATUS = "blocked"
TEST_PROXY_HOST = "http://proxy.internal"
TEST_PROXY_PORT = "3128"
TEST_NO_PROXY = "127.0.0.1,::1"


def test_generate_wp_secret_keys(harness: ops.testing.Harness):
    """
    arrange: no pre-condition.
    act: generate a group of WordPress secrets from scratch.
    assert: generated secrets should be safe.
    """
    harness.begin()
    charm: WordpressCharm = typing.cast(WordpressCharm, harness.charm)
    wordpress_secrets = charm._generate_wp_secret_keys()
    assert "default_admin_password" in wordpress_secrets, (
        "WordPress should generate a default admin password"
    )

    del wordpress_secrets["default_admin_password"]
    key_values = list(wordpress_secrets.values())
    assert set(wordpress_secrets.keys()) == set(charm._wordpress_secret_key_fields()), (
        "generated WordPress secrets should contain all required fields"
    )
    assert len(key_values) == len(set(key_values)), "no two secret values should be the same"
    for value in key_values:
        assert not (value.isalnum() or len(value) < 64), "secret values should not be too simple"


@pytest.mark.usefixtures("attach_storage")
def test_replica_consensus(
    harness: ops.testing.Harness, setup_replica_consensus: typing.Callable[[], dict]
):
    """
    arrange: deploy a new wordpress-k8s application.
    act: simulate peer relation creating and leader electing during the start of deployment.
    assert: units should reach consensus after leader elected.
    """
    setup_replica_consensus()
    charm: WordpressCharm = typing.cast(WordpressCharm, harness.charm)
    assert charm._replica_consensus_reached(), (
        "units in application should reach consensus once leadership established"
    )


@pytest.mark.usefixtures("attach_storage")
def test_replica_consensus_stable_after_leader_reelection(
    harness: ops.testing.Harness, app_name: str
):
    """
    arrange: deploy a new wordpress-k8s application.
    act: simulate a leader re-election after application deployed.
    assert: consensus should not change.
    """
    replica_relation_id = harness.add_relation("wordpress-replica", app_name)
    non_leader_peer_name = "wordpress-k8s/1"
    harness.add_relation_unit(replica_relation_id, non_leader_peer_name)
    harness.begin_with_initial_hooks()
    charm: WordpressCharm = typing.cast(WordpressCharm, harness.charm)

    assert not charm._replica_consensus_reached(), (
        "units in application should not reach consensus before leadership established"
    )
    harness.set_leader()
    assert charm._replica_consensus_reached(), (
        "units in application should reach consensus once leadership established"
    )
    consensus = harness.get_relation_data(replica_relation_id, app_name)
    # The harness will emit a leader-elected event when calling ``set_leader(True)`` no matter
    # what the situation is, ``set_leader(False)`` does nothing here currently, just for the
    # aesthetic.
    harness.set_leader(False)
    harness.set_leader(True)
    assert harness.get_relation_data(replica_relation_id, app_name) == consensus, (
        "consensus once established should not change after leadership changed"
    )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 33s</sub>

### ✅ `bash`

**Check tox configuration**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && cat tox.toml

<details>
<summary>155 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

skipsdist = true
envlist = [ "lint", "unit", "static", "coverage-report" ]
skip_missing_interpreters = true
requires = [ "tox>=4.21" ]
no_package = true

[env_run_base]
passenv = [ "PYTHONPATH", "CHARM_BUILD_DIR", "MODEL_SETTINGS" ]
allowlist_externals = [ "docker" ]
runner = "uv-venv-lock-runner"

[env_run_base.setenv]
PYTHONPATH = "{toxinidir}:{toxinidir}/lib:{[vars]src_path}"
PYTHONBREAKPOINT = "ipdb.set_trace"
PY_COLORS = "1"

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

[env.static]
description = "Run static analysis tests"
commands = [ [ "bandit", "-c", "{toxinidir}/pyproject.toml", "-r", "{[vars]src_path}", "{[vars]tst_path}" ] ]
dependency_groups = [ "static" ]

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

[env.integration]
description = "Run integration tests"
commands = [
  [
    "pytest",
    "{[vars]tst_path}",
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

[env.integration-juju3]
description = "Run integration tests using Juju 3"
commands = [
  [
    "pytest",
    "{[vars]tst_path}",
    "-v",
    "--tb",
    "native",
    "--ignore={[vars]tst_path}unit",
    "--log-cli-level=INFO",
    "-s",
    { replace = "posargs", extend = "true" },
  ],
]
dependency_groups = [ "integration-juju3" ]

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

<sub>⏱️ 40s</sub>

### ✅ `bash`

**Read full pyproject.toml**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && cat pyproject.toml

<details>
<summary>157 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

[project]
name = "wordpress-k8s-operator"
version = "0.0.0"
description = "WordPress is an OSS to create a beautiful website."
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
  "cosl==1.4.0",
  "mysql-connector-python==9.5.0",
  "ops==3.5.1",
  "pydantic==2.12.5",
  "requests==2.32.5",
]

[dependency-groups]
fmt = [
  "ruff",
]
lint = [
  "codespell",
  "juju>=3.6,<4",
  "kubernetes",
  "mypy",
  "pep8-naming",
  "pillow",
  "pytest==9.0.2",
  "pytest-cov",
  "pytest-operator",
  "python-keystoneclient",
  "python-swiftclient",
  "ruff",
  "types-pyyaml",
  "types-requests",
  "websockets<17",
]
static = [
  "bandit[toml]",
  "toml",
]
unit = [
  "coverage[toml]",
  "pytest",
]
coverage-report = [
  "coverage[toml]",
  "pytest",
]
integration = [
  "allure-pytest>=2.8.18",
  "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
  "juju>=2.9,<3",
  "kubernetes",
  "pillow",
  "pytest==9.0.2",
  "pytest-cov",
  "pytest-operator",
  "python-keystoneclient",
  "python-swiftclient",
  "types-pyyaml",
  "types-requests",
  "websockets<17",
]
integration-juju3 = [
  "juju==3.6.1.3",
  "kubernetes",
  "macaroonbakery==1.3.4",
  "pillow",
  "pytest==9.0.2",
  "pytest-cov",
  "pytest-operator",
  "python-keystoneclient",
  "python-swiftclient",
  "types-pyyaml",
  "types-requests",
]

[tool.uv]
package = false
conflicts = [ [ { group = "integration" }, { group = "integration-juju3" }, { group = "lint" } ] ]

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

[tool.pytest.ini_options]
markers = [
  "slow: marks slow and not very important tests",
  "requires_secret: mark tests that require external secrets",
]

[tool.coverage.run]
branch = true

[tool.coverage.report]
fail_under = 90
show_missing = true

[tool.mypy]
ignore_missing_imports = true
allow_redefinition = true
plugins = [ "pydantic.mypy" ]

[tool.bandit]
exclude_dirs = [ "/venv/" ]

[tool.bandit.assert_used]
skips = [ "*/integration/helper.py", "*/*test*" ]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 40s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.6.0**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/releases/tag/3.6.0",
  "max_length": 8000
}
```

</details>

<details>
<summary>23 lines</summary>

```
Contents of https://github.com/canonical/operator/releases/tag/3.6.0:
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
```

</details>


---

<sub>⏱️ 57s</sub>

### ✅ `bash`

**Check ops-scenario and ops-tracing versions**

$ pip show ops-scenario ops-tracing 2>&1 | head -30

<details>
<summary>22 lines</summary>

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
---
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

<sub>⏱️ 56s</sub>

### ✅ `bash`

**Check for ops.testing and ops-scenario usage**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && grep -r "ops.testing\|ops_scenario\|scenario\|ops.tracing\|ops_tracing" src/ tests/ --include="*.py" -l

```
tests/unit/conftest.py
tests/unit/test_charm.py
tests/unit/wordpress_mock.py
<exited with exit code 0>
```


---

<sub>⏱️ 1m 10s</sub>

### ✅ `bash`

**Read cos.py and state.py**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && cat src/cos.py && echo "===" && cat src/state.py

<details>
<summary>194 lines</summary>

```
#!/usr/bin/env python3

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""COS integration for WordPress charm."""

from typing import Dict, List, TypedDict

from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
from ops.pebble import Check, Layer, Service


class PrometheusStaticConfig(TypedDict, total=False):
    """Configuration parameters for prometheus metrics endpoint scraping.

    For more information, see:
    https://prometheus.io/docs/prometheus/latest/configuration/configuration/#static_config

    Attrs:
        targets: list of hosts to scrape, e.g. "*:8080", every unit's port 8080
        labels: labels assigned to all metrics scraped from the targets.
    """

    targets: List[str]
    labels: Dict[str, str]


class PrometheusMetricsJob(TypedDict, total=False):
    """Configuration parameters for prometheus metrics scraping job.

    For more information, see:
    https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config

    Attrs:
        metrics_path: The HTTP resource path on which to fetch metrics from targets.
        static_configs: List of labeled statically configured targets for this job.
    """

    metrics_path: str
    static_configs: List[PrometheusStaticConfig]


APACHE_PROMETHEUS_SCRAPE_PORT = "9117"
_APACHE_EXPORTER_PEBBLE_SERVICE = Service(
    name="apache-exporter",
    raw={
        "override": "replace",
        "summary": "Apache Exporter",
        "command": "apache_exporter",
        "startup": "enabled",
    },
)
_APACHE_EXPORTER_PEBBLE_CHECK = Check(
    name="apache-exporter-up",
    raw={
        "override": "replace",
        "level": "alive",
        "http": {"url": f"http://localhost:{APACHE_PROMETHEUS_SCRAPE_PORT}/metrics"},
    },
)
PROM_EXPORTER_PEBBLE_CONFIG = Layer(
    {
        "summary": "Apache prometheus exporter",
        "description": "Prometheus exporter for apache",
        "services": {
            _APACHE_EXPORTER_PEBBLE_SERVICE.name: _APACHE_EXPORTER_PEBBLE_SERVICE.to_dict()
        },
        "checks": {_APACHE_EXPORTER_PEBBLE_CHECK.name: _APACHE_EXPORTER_PEBBLE_CHECK.to_dict()},
    }
)

APACHE_LOG_PATHS = [
    "/var/log/apache2/access.*.log",
    "/var/log/apache2/error.*.log",
]

REQUEST_DURATION_MICROSECONDS_BUCKETS = [
    10000,
    25000,
    50000,
    100000,
    200000,
    300000,
    400000,
    500000,
    750000,
    1000000,
    1500000,
    2000000,
    2500000,
    5000000,
    10000000,
]


class ApacheLogProxyConsumer(LogProxyConsumer):
    """Extends LogProxyConsumer to add a metrics pipeline to promtail."""

    def _scrape_configs(self) -> dict:
        """Generate the scrape_configs section of the Promtail config file.

        Returns:
            A dict representing the `scrape_configs` section.
        """
        scrape_configs = super()._scrape_configs()
        scrape_configs["scrape_configs"].append(
            {
                "job_name": "access_log_exporter",
                "static_configs": [{"labels": {"__path__": "/var/log/apache2/access.*.log"}}],
                "pipeline_stages": [
                    {
                        "logfmt": {
                            "mapping": {
                                "request_duration_microseconds": "request_duration_microseconds",
                                "content_type": "content_type",
                                "path": "path",
                            }
                        }
                    },
                    {"labels": {"content_type": "content_type", "path": "path"}},
                    {
                        "match": {
                            "selector": '{path=~"^/server-status.*$"}',
                            "action": "drop",
                        }
                    },
                    {"labeldrop": ["filename", "path"]},
                    {
                        "metrics": {
                            "request_duration_microseconds": {
                                "type": "Histogram",
                                "source": "request_duration_microseconds",
                                "prefix": "apache_access_log_",
                                "config": {"buckets": REQUEST_DURATION_MICROSECONDS_BUCKETS},
                            }
                        }
                    },
                    {"drop": {"expression": ".*"}},
                ],
            }
        )
        return scrape_configs
===
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Wordpress charm state."""

import dataclasses
import logging
import os
import typing

import ops

# pylint: disable=no-name-in-module
from pydantic import BaseModel, HttpUrl, ValidationError

logger = logging.getLogger(__name__)


class CharmConfigInvalidError(Exception):
    """Exception raised when a charm configuration is found to be invalid.

    Attributes:
        msg: Explanation of the error.
    """

    def __init__(self, msg: str):
        """Initialize a new instance of the CharmConfigInvalidError exception.

        Args:
            msg: Explanation of the error.
        """
        self.msg = msg


class ProxyConfig(BaseModel):
    """Configuration for external access through proxy.

    Attributes:
        http_proxy: The http proxy URL.
        https_proxy: The https proxy URL.
        no_proxy: Comma separated list of hostnames to bypass proxy.
    """

    http_proxy: typing.Optional[HttpUrl]
    https_proxy: typing.Optional[HttpUrl]
    no_proxy: typing.Optional[str]

    @classmethod
    def from_env(cls) -> typing.Optional["ProxyConfig"]:
        """Instantiate ProxyConfig from juju charm environment.

        Returns:
            ProxyConfig if proxy configuration is provided, None otherwise.
        """
        http_proxy = os.environ.get("JUJU_CHARM_HTTP_PROXY")
        https_proxy = os.environ.get("JUJU_CHARM_HTTPS_PROXY")
        no_proxy = os.environ.get("JUJU_CHARM_NO_PROXY")

        if not http_proxy and not https_proxy:
            return None

        return cls(
            http_proxy=http_proxy if http_proxy else None,
            https_proxy=https_proxy if https_proxy else None,
            no_proxy=no_proxy,
        )


@dataclasses.dataclass(frozen=True)
class State:
    """The Wordpress k8s operator charm state.

    Attributes:
        proxy_config: Proxy configuration to access Jenkins upstream through.
    """

    proxy_config: typing.Optional[ProxyConfig]

    @classmethod
    def from_charm(cls, _: ops.CharmBase) -> "State":
        """Initialize the state from charm.

        Returns:
            Current state of the charm.

        Raises:
            CharmConfigInvalidError: if invalid state values were encountered.
        """
        try:
            proxy_config = ProxyConfig.from_env()
        except ValidationError as exc:
            logger.error("Invalid juju model proxy configuration, %s", exc)
            raise CharmConfigInvalidError("Invalid model proxy configuration.") from exc

        return cls(
            proxy_config=proxy_config,
        )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 18s</sub>

### ✅ `bash`

**Check latest ops-scenario and ops-tracing versions**

$ pip index versions ops-scenario 2>/dev/null | head -3; pip index versions ops-tracing 2>/dev/null | head -3

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

<sub>⏱️ 1m 17s</sub>

### ✅ `bash`

**Check ExecError and container.exec usage**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && grep -r "ExecError\|exec_process\|container\.exec\|_exec\b" src/ --include="*.py" -n | head -30

```
src/charm.py:556:        except ops.pebble.ExecError as error:
<exited with exit code 0>
```


---

<sub>⏱️ 1m 49s</sub>

### ✅ `bash`

**Read metadata and charmcraft config**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && cat metadata.yaml && echo "===" && cat charmcraft.yaml

<details>
<summary>77 lines</summary>

```
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
name: wordpress-k8s
display-name: WordPress
summary: WordPress is an OSS to create a beautiful website.
description: |
  A [Juju](https://juju.is/) [charm](https://documentation.ubuntu.com/juju/3.6/reference/charm/) deploying and managing
  WordPress on Kubernetes. [WordPress](https://wordpress.com/) is the world's most popular website
  builder, and it's free and open-source. 

  This charm simplifies initial deployment and operations of WordPress on Kubernetes, including scaling
  the number of instances, integration with SSO, access to OpenStack Swift object storage for redundant
  file storage, and more. It allows for deployment on many different Kubernetes platforms, from
  [MicroK8s](https://microk8s.io/) to [Charmed Kubernetes](https://ubuntu.com/kubernetes) to public
  cloud Kubernetes offerings.

  This charm will make operating WordPress straightforward for DevOps or SRE teams through Juju's clean
  interface. It will allow deployment into multiple environments to test changes and support scaling out
  for enterprise deployments.

  For information about how to deploy, integrate, and manage this charm, see the Official
  [WordPress K8s charm documentation](https://documentation.ubuntu.com/wordpress-k8s-charm/latest/).
docs: https://documentation.ubuntu.com/wordpress-k8s-charm/latest/
maintainers:
  - https://launchpad.net/~canonical-is-devops
issues: https://github.com/canonical/wordpress-k8s-operator/issues
source: https://github.com/canonical/wordpress-k8s-operator
tags:
  - applications
  - blog
assumes:
  - k8s-api

containers:
  wordpress:
    resource: wordpress-image
    mounts:
      - storage: uploads
        location: /var/www/html/wp-content/uploads

storage:
  uploads:
    type: filesystem
    location: /var/www/html/wp-content/uploads

peers:
  wordpress-replica:
    interface: wordpress-replica

resources:
  wordpress-image:
    type: oci-image
    description: OCI image for wordpress

provides:
  metrics-endpoint:
    interface: prometheus_scrape
  grafana-dashboard:
    interface: grafana_dashboard

requires:
  database:
    interface: mysql_client
  nginx-route:
    interface: nginx-route
    limit: 1
  logging:
    interface: loki_push_api
===
# Copyright 2024 Canonical Ltd.
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 49s</sub>

### ✅ `bash`

**Check ops.testing available APIs**

$ pip show ops-scenario 2>&1 | grep -i "location\|version" && python -c "import ops.testing; print(dir(ops.testing))" 2>&1 | tr ',' '\n' | grep -i "context\|state\|scenario"

```
Version: 8.7.0
Location: /home/ubuntu/.local/lib/python3.12/site-packages
<exited with exit code 1>
```


---

<sub>⏱️ 1m 56s</sub>

### ✅ `bash`

**Check ops.testing public API**

$ python -c "import ops.testing; print([x for x in dir(ops.testing) if not x.startswith('_')])"

```
bash: python: command not found
<exited with exit code 127>
```


---

<sub>⏱️ 1m 56s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.7.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
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

<sub>⏱️ 2m 8s</sub>

### 💬 Copilot

Let me fetch the ops-tracing release notes to understand what's available:

---

<sub>⏱️ 2m 9s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/operator/blob/main/ops-tracing/CHANGELOG.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 12000,
  "url": "https://github.com/canonical/operator/blob/main/ops-tracing/CHANGELOG.md"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/operator/blob/main/ops-tracing/CHANGELOG.md - status code 404
```


---

<sub>⏱️ 2m 9s</sub>

### ✅ `bash`

**Check ops-tracing details**

$ pip3 show ops-tracing 2>&1 && python3 -c "import ops_tracing; print(dir(ops_tracing))" 2>&1 | head -5

<details>
<summary>12 lines</summary>

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
['Tracing', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '_api', '_backend', '_buffer', '_export', '_mark_observed', '_setup', '_shutdown', 'set_destination', 'vendor']
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 14s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/operator/tree/main/ops-tracing**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://github.com/canonical/operator/tree/main/ops-tracing"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/operator/tree/main/ops-tracing - status code 404
```


---

<sub>⏱️ 2m 14s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/ops-tracing/releases**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 12000,
  "url": "https://github.com/canonical/ops-tracing/releases"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/ops-tracing/releases - status code 404
```


---

<sub>⏱️ 2m 20s</sub>

### ✅ `bash`

**Find ops-tracing homepage**

$ pip3 show ops-tracing 2>&1 | grep "Home\|Source\|Project"

```
Home-page:
<exited with exit code 0>
```


---

<sub>⏱️ 2m 20s</sub>

### ✅ `bash`

**Find ops-scenario homepage**

$ pip3 show ops-scenario 2>&1 | grep "Home\|Source\|Project"

```
Home-page:
<exited with exit code 0>
```


---

<sub>⏱️ 2m 26s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/ops-tracing/#history**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://pypi.org/project/ops-tracing/#history"
}
```

</details>

```
Contents of https://pypi.org/project/ops-tracing/#history:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 2m 26s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/ops-scenario/#history**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://pypi.org/project/ops-scenario/#history"
}
```

</details>

```
Contents of https://pypi.org/project/ops-scenario/#history:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 2m 33s</sub>

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

<sub>⏱️ 2m 34s</sub>

### ✅ `web_fetch`

**https://pypi.org/pypi/ops-scenario/json**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://pypi.org/pypi/ops-scenario/json"
}
```

</details>

````
Content type application/json cannot be simplified to markdown. Here is the raw content:
Contents of https://pypi.org/pypi/ops-scenario/json:
{"info":{"author":null,"author_email":"Pietro Pasotti <pietro.pasotti@canonical.com>","bugtrack_url":null,"classifiers":["Development Status :: 5 - Production/Stable","Framework :: Pytest","Intended Audience :: Developers","Topic :: Software Development :: Quality Assurance","Topic :: Software Development :: Testing","Topic :: Utilities"],"description":"# ops-scenario, the unit testing framework for ops charms\n\n`ops-scenario` is a Python library that provides state-transition testing for\n[Ops](https://documentation.ubuntu.com/ops/latest/) charms. These tests are higher level than\ntypical unit tests, but run at similar speeds and are the recommended approach\nfor testing charms within requiring a full [Juju](https://canonical.com/juju) installation.\n\nTest are written in the arrange/act/assert pattern, arranging an object\nrepresenting the current Juju state, acting by emulating an event from Juju, and\nthen asserting on the (simulated) output Juju state.\n\n## Writing tests\n\nHere's a test that verifies that a unit is active after the `start` event, with a very minimal initial state:\n\n```python\nfrom ops import testing\n\n# 'src/charm.py' typically contains the charm class.\nfrom charm import MyCharm\n\ndef test_start():\n    ctx = testing.Context(MyCharm)\n    state_in = testing.State()\n    state_out = ctx.run(ctx.on.start(), state_in)\n    assert state_out.unit_status == testing.ActiveStatus()\n```\n\nMore comprehensive tests will include relations, containers, secrets, and other\ncomponents in the input state, and assertions against both the output state and\nthe context. The 'act' stage remains a simple single call, although additional\narguments may be required for the event, such as the relation or container that\ntriggered it. For example:\n\n```python\nimport pytest\nfrom ops import testing\n\nfrom charm import MyCharm\n\n@pytest.mark.parametrize(\n    'leader',\n    [pytest.param(True, id='leader'), pytest.param(False, id='non-leader')],\n)\ndef test_(leader: bool):\n    # Arrange:\n    ctx = testing.Context(MyCharm)\n    relation = testing.Relation('db', local_app_data={'hostname': 'example.com'})\n    peer_relation = testing.PeerRelation('peer')\n    container = testing.Container('workload', can_connect=True)\n    relation_secret = testing.Secret({'certificate': 'xxxxxxxx'})\n    user_secret = testing.Secret({'username': 'admin', 'password': 'xxxxxxxx'})\n    config = {'port': 8443, 'admin-credentials': 'secret:1234'}\n    state_in = testing.State(\n        leader=leader,\n        config=config,\n        relations={relation, peer_relation},\n        containers={container},\n        secrets={relation_secret, user_secret},\n        unit_status=testing.BlockedStatus(),\n        workload_version='1.0.1',\n    )\n\n    # Act:\n    state_out = ctx.run(ctx.on.relation_changed(relation), state_in)\n\n    # Assert:\n    assert testing.JujuLogLine(level='INFO', message='Distributing secret.') in ctx.juju_log\n    peer_relation_out = state_out.get_relation(peer_relation.id)\n    assert peer_relation_out.peers_data[0] == {'secret_id': relation_secret.id}\n```\n\nYou don't have to use pytest for your charm tests, but it's what we recommend.\npytest's `assert`-based approach is a straightforward way to write tests, and\nits fixtures are helpful for structuring setup and teardown.\n\n## Installation\n\nFor charm tests, install the testing framework by adding the `testing` extra of\nops in your unit testing environment. For example, in `pyproject.toml`:\n\n```toml\n[dependency-groups]\ntest = ['ops[testing]<4.0']\n```\n\nOps checks if `ops-scenario` is installed, and, if so, makes the classes\n(such as `Context`, `State`, and `Relation`) available in the `ops.testing`\nnamespace. Use `from ops import testing` rather than importing the `scenario`\npackage.\n\n`ops-scenario` supports the same platforms and Python versions as ops itself.\n\n## Documentation\n\n * To get started, work through our ['Write your first Kubernetes charm' tutorial](https://documentation.ubuntu.com/ops/latest/tutorial/from-zero-to-hero-write-your-first-kubernetes-charm/create-a-minimal-kubernetes-charm/#write-unit-tests-for-your-charm), following the instructions for adding\n   unit tests at the end of each chapter.\n * When you need to write a test that involves specific ops functionality,\n   refer to our [how-to guides](https://documentation.ubuntu.com/ops/latest/howto/)\n   which all conclude with examples of tests of the ops functionality.\n * Use our extensive [reference documentation](https://documentation.ubuntu.com/ops/latest/reference/ops-testing/#ops-testing) when you need to know how each `testing` object works. These\n   docs are also available via the standard Python `help()` functionality and in\n   your IDE.\n\n[**Read the full documentation**](https://documentation.ubuntu.com/ops/latest/)\n\n## Community\n\n`ops-scenario` is a member of the Charming family. It's an open source project\nthat warmly welcomes community contributions, suggestions, fixes and\nconstructive feedback.\n\n* Read our [code of conduct](https://ubuntu.com/community/ethos/code-of-conduct):\n  As a community we adhere to the Ubuntu code of conduct.\n* [Get support](https://discourse.charmhub.io/): Discourse is the go-to forum\n  for all Ops-related discussions, including around testing.\n* Join our [online chat](https://matrix.to/#/#charmhub-charmdev:ubuntu.com):\n  Meet us in the #charmhub-charmdev channel on Matrix.\n* [Report bugs](https://github.com/canonical/operator/issues): We want to know\n  about the problems so we can fix them.\n* [Contribute docs](https://github.com/canonical/operator/blob/main/HACKING.md#contributing-documentation):\n  Get started on GitHub.\n\n## Contributing and developing\n\nAnyone can contribute to ops and `ops-scenario`. It's best to start by\n[opening an issue](https://github.com/canonical/operator/issues) with a clear\ndescription of the problem or feature request, but you can also\n[open a pull request](https://github.com/canonical/operator/pulls) directly.\n\nRead our [guide](./CONTRIBUTING.md) for more details on how to work on and\ncontribute to `ops-scenario`.\n\nCurrently, releases of `ops-scenario` are done in lockstep with releases of ops\nitself, with matching minor and bugfix release numbers. The ops documentation\noutlines how to create a new release.\n","description_content_type":"text/markdown","docs_url":null,"download_url":null,"downloads":{"last_day":-1,"last_month":-1,"last_week":-1},"dynamic":null,"home_page":null,"keywords":"juju, test","license":null,"license_expression":"Apache-2.0","license_files":null,"maintainer":"The Charm Tech team at Canonical Ltd.","maintainer_email":null,"name":"ops-scenario","package_url":"https://pypi.org/project/ops-scenario/","platform":null,"project_url":"https://pypi.org/project/ops-scenario/","project_urls":{"Bug Tracker":"https://github.com/canonical/operator/issues","Homepage":"https://github.com/canonical/operator"},"provides_extra":null,"release_url":"https://pypi.org/project/ops-scenario/8.7.0/","requires_dist":["ops==3.7.0","PyYAML>=6.0.1","typing_extensions>=4.9.0"],"requires_python":">=3.10","summary":"Python library providing a state-transition testing API for Operator Framework charms.","version":"8.7.0","yanked":false,"yanked_reason":null},"last_serial":35607420,"ownership":{"organization":null,"roles":[{"role":"Owner","user":"benhoyt"},{"role":"Owner","user":"jnsgruk"},{"role":"Owner","user":"ppasotti"},{"role":"Maintainer","user":"tonyandrewmeyer"}]},"releases":{"2.0.0":[{"comment_text":"","digests":{"blake2b_256":"4d60f988a17df49a4407f010f87e36c0bc61c1eb6e3279367064b1b0fdf5987d","md5":"216ad99861147310c647ab5eec8126b9","sha256":"d28bc1db74a2bd179b1057e3e445023942d9e8a4a689a7b7edbc644ebe4634a3"},"downloads":-1,"filename":"ops_scenario-2.0.0-py3-none-any.whl","has_sig":false,"md5_digest":"216ad99861147310c647ab5eec8126b9","packagetype":"bdist_wheel","python_version":"py3","requires_python":">=3.8","size":22434,"upload_time":"2023-02-02T09:06:20","upload_time_iso_8601":"2023-02-02T09:06:20.571464Z","url":"https://files.pythonhosted.org/packages/4d/60/f988a17df49a4407f010f87e36c0bc61c1eb6e3279367064b1b0fdf5987d/ops_scenario-2.0.0-py3-none-any.whl","yanked":false,"yanked_reason":null}],"2.0.4":[{"comment_text":"","digests":{"blake2b_256":"cb44520944ccb39359e8c6d7a46c7ce44e7e2e6f73a5ee02aedab597eed2a83e","md5":"5e29e902afdb5104f7d95653e99d8538","sha256":"2972ccb42d04f7904b12319adaa66db36529402b38b94477f48f0c3290abfe16"},"downloads":-1,"filename":"ops_scenario-2.0.4-py3-none-any.whl","has_sig":false,"md5_digest":"5e29e902afdb5104f7d95653e99d8538","packagetype":"bdist_wheel","python_version":"py3","requires_python":">=3.8","size":22428,"upload_time":"2023-02-02T09:58:40","upload_time_iso_8601":"2023-02-02T09:58:40.828631Z","url":"https://files.pythonhosted.org/packages/cb/44/520944ccb39359e8c6d7a46c7ce44e7e2e6f73a5ee02aedab597eed2a83e/ops_scenario-2.0.4-py3-none-any.whl","yanked":false,"yanked_reason":null},{"comment_text":"","digests":{"blake2b_256":"346f102481e8ff7391bc39a46167e0793ebaaab8adabcf9c158341f9b84ed38a","md5":"06d0e5d7260c2561bab2103e86a57dfd","sha256":"52f84de222010a7b358617045941c74bc895b3ffd6b3835cf865b9d0bfa41340"},"downloads":-1,"filename":"ops-scenario-2.0.4.tar.gz","has_sig":false,"md5_digest":"06d0e5d7260c2561bab2103e86a57dfd","packagetype":"sdist","python_version":"source","requires_python":">=3.8","size":19744,"upload_time":"2023-02-02T09:58:42","upload_time_iso_8601":"2023-02-02T09:58:42.389094Z","url":"https://files.pythonhosted.org/packages/34/6f/102481e8ff7391bc39a46167e0793ebaaab8adabcf9c158341f9b84ed38a/ops-scenario-2.0.4.tar.gz","yanked":false,"yanked_reason":null}],"2.0.5":[{"comment_text":"","digests":{"blake2b_256":"6e46a8cdb41ac5968d265b671a639fd3038a80d3b847f2ef80c4f21cd6e8f58a","md5":"307718aa02f2e1d5ef4a61980ee53910","sha256":"79ff31cd07664506c9b0c3d28fb163580323908826fbc7e8ad12aba4aa8ea91d"},"downloads":-1,"filename

<note>Content truncated. Call the fetch tool with a start_index of 10000 to get more content.</note>
````


---

<sub>⏱️ 2m 51s</sub>

### 💬 Copilot

Let me fetch the full ops changelog to understand all changes:

---

<sub>⏱️ 2m 52s</sub>

### ✅ `web_fetch`

**https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 12000,
  "url": "https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md"
}
```

</details>

<details>
<summary>224 lines</summary>

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
* Update 

<note>Content truncated. Call the fetch tool with a start_index of 12000 to get more content.</note>
```

</details>


---

<sub>⏱️ 2m 52s</sub>

### ✅ `bash`

**Check relevant usage patterns in charm.py**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && cat src/charm.py | grep -n "ExecError\|traceback\|get_binding\|secret\|StorageMeta" | head -30

<details>
<summary>31 lines</summary>

```
13:import secrets
17:import traceback
183:            self.on.rotate_wordpress_secrets_action, self._on_rotate_wordpress_secrets_action
236:    def _on_rotate_wordpress_secrets_action(self, event: ActionEvent):
237:        """Handle the rotate-wordpress_secrets action.
239:        This action is for rotating the secrets of WordPress. The leader unit is the one handling
241:        event and update the secrets via the application `relation_changed` event.
248:                "Action on-rotate-wordpress-secrets failed. Replica consensus not reached."
260:        # Update the secrets in peer relation.
262:        wordpress_secrets = self._generate_wp_secret_keys()
263:        for secret_key, secret_value in wordpress_secrets.items():
264:            replica_relation_data[secret_key] = secret_value
315:    def _wordpress_secret_key_fields():
316:        """Field names of secrets required for instantiation of WordPress.
318:        These secrets are used by WordPress to enhance the security by encrypting information.
335:    def _generate_wp_secret_keys(self) -> Dict[str, str]:
336:        """Generate random secure secrets for each secret required by WordPress.
339:            WordPress secret-value pairs.
352:            return "".join(secrets.choice(characters) for _ in range(length))
354:        wp_secrets = {
355:            field: _wp_generate_password() for field in self._wordpress_secret_key_fields()
357:        wp_secrets["default_admin_password"] = secrets.token_urlsafe(32)
358:        return wp_secrets
363:        The relation data content object is used to share (read and write) necessary secret data
385:        fields = self._wordpress_secret_key_fields()
404:            new_replica_data = self._generate_wp_secret_keys()
405:            for secret_key, secret_value in new_replica_data.items():
406:                replica_relation_data[secret_key] = secret_value
458:        for secret_key in self._wordpress_secret_key_fields():
459:            secret_value = replica_relation_data[secret_key]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 23s</sub>

### 💬 Copilot

Let me look at the specific ExecError usage in charm.py:

---

<sub>⏱️ 3m 24s</sub>

### ✅ `bash`

**Read ExecError handling in charm.py**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && sed -n '540,580p' src/charm.py

<details>
<summary>40 lines</summary>

```
Returns:
            A named tuple with three fields: return code, stdout and stderr. Stdout and stderr are
            both string.
        """
        process: ExecProcess = self._container().exec(
            cmd,
            user=user,
            group=group,
            working_dir=working_dir,
            combine_stderr=combine_stderr,
            timeout=timeout,
        )
        try:
            stdout, stderr = process.wait_output()
            result = types_.CommandExecResult(return_code=0, stdout=stdout, stderr=stderr)
        except ops.pebble.ExecError as error:
            result = types_.CommandExecResult(
                error.exit_code,
                cast(Union[str, bytes], error.stdout),
                cast(Union[str, bytes, None], error.stderr),
            )
        return_code = result.return_code
        if combine_stderr:
            logger.debug(
                "Run command: %s return code %s\noutput: %s", cmd, return_code, result.stdout
            )
        else:
            logger.debug(
                "Run command: %s, return code %s\nstdout: %s\nstderr:%s",
                cmd,
                return_code,
                result.stdout,
                result.stderr,
            )
        return result

    def _run_wp_cli(
        self, cmd: List[str], timeout: int = 60, combine_stderr: bool = False
    ) -> types_.CommandExecResult:
        """Execute a wp-cli command, this is a wrapper of :meth:`charm.WordpressCharm._run_cli`.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 24s</sub>

### ✅ `bash`

**Check for ops.testing Context usage in tests**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && grep -n "Context\|charm_spec\|ops.testing" tests/ -r --include="*.py" | head -20

<details>
<summary>21 lines</summary>

```
tests/unit/conftest.py:11:import ops.testing
tests/unit/conftest.py:20:    """Enable WordPress patch system, used in combine with :class:`ops.testing.Harness`.
tests/unit/conftest.py:35:    harness = ops.testing.Harness(WordpressCharm)
tests/unit/conftest.py:47:def setup_replica_consensus_fixture(harness: ops.testing.Harness, app_name: str):
tests/unit/conftest.py:134:    harness: ops.testing.Harness, example_database_info: typing.Dict[str, str]
tests/unit/conftest.py:158:    harness: ops.testing.Harness, example_database_info_no_port: typing.Dict[str, str]
tests/unit/conftest.py:182:    harness: ops.testing.Harness, example_invalid_database_info: typing.Dict[str, str]
tests/unit/conftest.py:206:    harness: ops.testing.Harness, example_database_info_connection_error: typing.Dict[str, str]
tests/unit/conftest.py:243:    harness: ops.testing.Harness,
tests/unit/test_charm.py:15:import ops.testing
tests/unit/test_charm.py:30:def test_generate_wp_secret_keys(harness: ops.testing.Harness):
tests/unit/test_charm.py:55:    harness: ops.testing.Harness, setup_replica_consensus: typing.Callable[[], dict]
tests/unit/test_charm.py:71:    harness: ops.testing.Harness, app_name: str
tests/unit/test_charm.py:104:    harness: ops.testing.Harness,
tests/unit/test_charm.py:136:def test_wp_config_before_consensus(harness: ops.testing.Harness):
tests/unit/test_charm.py:150:    harness: ops.testing.Harness,
tests/unit/test_charm.py:186:    harness: ops.testing.Harness, setup_replica_consensus: typing.Callable[[], dict]
tests/unit/test_charm.py:220:def test_core_reconciliation_before_storage_ready(harness: ops.testing.Harness):
tests/unit/test_charm.py:240:def test_core_reconciliation_before_peer_relation_ready(harness: ops.testing.Harness):
tests/unit/test_charm.py:265:    harness: ops.testing.Harness, setup_replica_consensus: typing.Callable[[], dict]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 47s</sub>

### ✅ `bash`

**Check traceback usage in charm.py**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && grep -n "traceback" src/charm.py

```
17:import traceback
715:                logger.debug("MySQL connection test failed, traceback: %s", traceback.format_exc())
<exited with exit code 0>
```


---

<sub>⏱️ 3m 47s</sub>

### ✅ `bash`

**Check git log**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && git log --oneline -5

```
367d6c7 (grafted, HEAD, origin/main, origin/HEAD, main) Update issue and enhancement templates (#356)
<exited with exit code 0>
```


---

<sub>⏱️ 3m 56s</sub>

### 💬 Copilot

Now I have everything I need. Let me create a branch and make the upgrade:

---

<sub>⏱️ 3m 57s</sub>

### ✅ `bash`

**Create upgrade branch**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && git checkout -b upgrade-ops-3.7.0

```
Switched to a new branch 'upgrade-ops-3.7.0'
<exited with exit code 0>
```


---

<sub>⏱️ 4m 4s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 4m 11s</sub>

### 💬 Copilot

Now update the lockfile:

---

<sub>⏱️ 4m 13s</sub>

### ✅ `bash`

**Update uv.lock**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && uv lock 2>&1

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠙ wordpress-k8s-operator==0.0.0                                                                                         ⠙ wordpress-k8s-operator==0.0.0                                                                                         ⠙ wordpress-k8s-operator==0.0.0                                                                                         ⠙ wordpress-k8s-operator==0.0.0                                                                                         ⠙ wordpress-k8s-operator==0.0.0                                                                                         ⠙ wordpress-k8s-operator==0.0.0                                                                                         ⠹ wordpress-k8s-operator==0.0.0                                                                                         ⠹ cosl==1.4.0                                                                                                           ⠹ mysql-connector-python==9.5.0                                                                                         ⠹ ops==3.7.0                                                                                                            ⠹ pydantic==2.12.5                                                                                                      ⠹ requests==2.32.5                                                                                                      ⠹ pytest==9.0.2                                                                                                         ⠹ pydantic-core==2.41.5                                                                                                 ⠹ coverage==7.12.0                                                                                                      ⠹ coverage==7.12.0                                                                                                      ⠹ ruff==0.14.6                                                                                                          ⠹ codespell==2.4.1                                                                                                      ⠹ juju==3.6.1.3                                                                                                         ⠹ kubernetes==30.1.0                                                                                                    ⠹ mypy==1.18.2                                                                                                          ⠹ pep8-naming==0.15.1                                                                                                   ⠹ pillow==12.0.0                                                                                                        ⠹ pytest-cov==7.0.0                                                                                                     ⠸ tomli==2.3.0                                                                                                          ⠼ tomli==2.3.0                                                                                                          ⠼ backports-datetime-fromisoformat==2.0.3                                                                               ⠼ hvac==2.4.0                                                                                                           ⠼ macaroonbakery==1.3.4                                                                                                 ⠼ paramiko==2.12.0                                                                                                      ⠴ protobuf==6.33.1                                                                                                      ⠴ pymacaroons==0.13.0                                                                                                   ⠴ pynacl==1.6.1                                                                                                         ⠴ pyrfc3339==1.1                                                                                                        ⠴ bcrypt==5.0.0                                                                                                         ⠴ cryptography==46.0.3                                                                                                  ⠴ exceptiongroup==1.3.1                                                                                                 ⠦ backports-datetime-fromisoformat==2.0.3                                                                               ⠧ backports-datetime-fromisoformat==2.0.3                                                                               ⠧ backports-strenum==1.3.1                                                                                              ⠧ backports-strenum==1.3.1                                                                                              ⠧ hvac==2.4.0                                                                                                           ⠇ ruff==0.14.6                                                                                                          ⠇ allure-pytest==2.15.0                                                                                                 ⠋ allure-pytest==2.15.0                                                                                                 ⠋ allure-python-commons==2.15.0                                                                                         ⠋ juju==2.9.49.1                                                                                                        ⠋ kubernetes==30.1.0                                                                                                    ⠋ pillow==12.0.0                                                                                                        ⠋ pytest-cov==7.0.0                                                                                                     ⠋ pytest-operator==0.43.2                                                                                               ⠋ python-keystoneclient==5.7.0                                                                                          ⠋ python-swiftclient==4.9.0                                                                                             ⠋ jujubundlelib==0.5.7                                                                                                  Resolved 125 packages in 1.81s
Updated ops v3.5.1 -> v3.7.0
<exited with exit code 0>
```


---

<sub>⏱️ 4m 20s</sub>

### 💬 Copilot

The lockfile is updated. Now let's run the unit tests to verify nothing broke:

---

<sub>⏱️ 4m 24s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && tox -e unit 2>&1

<details>
<summary>82 lines</summary>

```
unit: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/.tox/unit
unit: uv-sync> uv sync --locked --python-preference system --no-default-groups --group unit -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
unit: commands[0]> coverage run --source=/tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/src/ -m pytest --ignore=/tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/tests/integration -v --tb native -s
================================================= test session starts ==================================================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/.tox/unit/bin/python3
cachedir: .tox/unit/.pytest_cache
rootdir: /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4
configfile: pyproject.toml
collecting ... collecting 43 items                                                                                                    collected 43 items                                                                                                     

tests/unit/test_charm.py::test_generate_wp_secret_keys PASSED
tests/unit/test_charm.py::test_replica_consensus PASSED
tests/unit/test_charm.py::test_replica_consensus_stable_after_leader_reelection PASSED
tests/unit/test_charm.py::test_database_relation PASSED
tests/unit/test_charm.py::test_wp_config_before_consensus PASSED
tests/unit/test_charm.py::test_wp_config PASSED
tests/unit/test_charm.py::test_wp_install_cmd PASSED
tests/unit/test_charm.py::test_core_reconciliation_before_storage_ready PASSED
tests/unit/test_charm.py::test_core_reconciliation_before_peer_relation_ready PASSED
tests/unit/test_charm.py::test_core_reconciliation_before_database_ready PASSED
tests/unit/test_charm.py::test_addon_reconciliation_fail PASSED
tests/unit/test_charm.py::test_core_reconciliation PASSED
tests/unit/test_charm.py::test_get_initial_password_action_before_replica_consensus PASSED
tests/unit/test_charm.py::test_get_initial_password_action PASSED
tests/unit/test_charm.py::test_rotate_wordpress_secrets_before_pebble_connect PASSED
tests/unit/test_charm.py::test_rotate_wordpress_secrets_before_replica_consensus PASSED
tests/unit/test_charm.py::test_rotate_wordpress_secrets_as_follower PASSED
tests/unit/test_charm.py::test_rotate_wordpress_secrets PASSED
tests/unit/test_charm.py::test_update_database PASSED
tests/unit/test_charm.py::test_update_database_fail PASSED
tests/unit/test_charm.py::test_theme_reconciliation PASSED
tests/unit/test_charm.py::test_plugin_reconciliation PASSED
tests/unit/test_charm.py::test_team_map PASSED
tests/unit/test_charm.py::test_swift_config PASSED
tests/unit/test_charm.py::test_akismet_plugin PASSED
tests/unit/test_charm.py::test_openid_plugin PASSED
tests/unit/test_charm.py::test_swift_plugin PASSED
tests/unit/test_charm.py::test_ingress PASSED
tests/unit/test_charm.py::test_defensive_programing[_check_addon_type-test_args0] PASSED
tests/unit/test_charm.py::test_defensive_programing[_wp_addon_install-test_args1] PASSED
tests/unit/test_charm.py::test_defensive_programing[_wp_addon_list-test_args2] PASSED
tests/unit/test_charm.py::test_defensive_programing[_wp_addon_uninstall-test_args3] PASSED
tests/unit/test_charm.py::test_defensive_programing[_perform_plugin_activate_or_deactivate-test_args4] PASSED
tests/unit/test_charm.py::test_missing_peer_relation PASSED
tests/unit/test_charm.py::test_mysql_connection_error PASSED
tests/unit/test_charm.py::test_wordpress_version_set PASSED
tests/unit/test_charm.py::test_waiting_for_leader_installation_timeout PASSED
tests/unit/test_charm.py::test_valid_proxy_config PASSED
tests/unit/test_charm.py::test_invalid_proxy_config PASSED
tests/unit/test_charm.py::test_only_valid_http_proxy_config PASSED
tests/unit/test_charm.py::test_only_valid_https_proxy_config PASSED
tests/unit/test_charm.py::test_wordpress_promtail_config PASSED
tests/unit/test_charm.py::test_php_ini PASSED

=================================================== warnings summary ===================================================
tests/unit/test_charm.py: 42 warnings
  /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/tests/unit/conftest.py:35: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = ops.testing.Harness(WordpressCharm)

tests/unit/test_charm.py::test_database_relation
tests/unit/test_charm.py::test_core_reconciliation
tests/unit/test_charm.py::test_theme_reconciliation
tests/unit/test_charm.py::test_plugin_reconciliation
tests/unit/test_charm.py::test_akismet_plugin
tests/unit/test_charm.py::test_openid_plugin
tests/unit/test_charm.py::test_swift_plugin
tests/unit/test_charm.py::test_mysql_connection_error
tests/unit/test_charm.py::test_waiting_for_leader_installation_timeout
  /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/lib/charms/data_platform_libs/v0/data_interfaces.py:1167: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================================== 43 passed, 51 warnings in 2.63s ============================================
unit: commands[1]> coverage report
Name                Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------
src/charm.py          576     35    178     34    91%   162, 204-207, 299->302, 414, 473->477, 627, 658, 664, 681-685, 715, 750-751, 811, 820, 968->981, 980, 982, 987-988, 1048, 1068, 1075, 1165, 1174, 1186, 1207, 1216, 1235, 1239, 1268, 1309, 1441, 1463, 1470->1472, 1515->exit, 1527, 1537, 1575
src/cos.py             20      0      0      0   100%
src/exceptions.py      16      1      2      1    89%   42
src/state.py           33      0      2      0   100%
src/types_.py          15      0      0      0   100%
---------------------------------------------------------------
TOTAL                 660     36    182     35    92%
  unit: OK (3.29=setup[0.09]+cmd[3.11,0.09] seconds)
  congratulations :) (3.30 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 37s</sub>

### 💬 Copilot

There's a `PendingDeprecationWarning` for `Harness`. Let me check when this was introduced:

---

<sub>⏱️ 4m 37s</sub>

### ✅ `web_fetch`

**https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md",
  "start_index": 12000
}
```

</details>

<details>
<summary>307 lines</summary>

```
Content type text/plain; charset=utf-8 cannot be simplified to markdown. Here is the raw content:
Contents of https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md:
how-to to feature Jubilant (#2000, #2004)
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

* Add a docs link to the Harness deprecation warning (#1513)
* Add best practices and a "manage charms" how-to (#1615)
* Add section about services with long startup time (#1604)
* Clarify how to use mounts in `ops.testing.Container` (#1637)
* Fix code snippet indentation (#1649)
* Fix Scenario example (#1616)
* Move hooks-based charm migration guide (#1636)
* Putting test into each chapter of the tutorial (#1647)
* Refactor how-to unit test according to comments (#1642)
* Refactor test docs to 1 explanation and 2 how-tos (#1628)
* Remove the charm-tech@lists.launchpad.net email address (#1632)
* Remove tutorial chapters that are covered by the how-to guide (#1511)
* Stack args vertically for long signature lines (#1641)
* Testing explanation (#1635)
* Unify charm test docs how to (#1639)

## CI

* Exclude vault-k8s-operator until the system can handle monorepos (#1650)
* Use the latest version of ops-scenario in the compatibility tests (#1608)

# 2.19.0 - 27 Feb 2025

## Features

* Expose the Juju version via Model objects (#1563)
* Support starting and stopping Pebble checks, and the checks enabled field (#1560)

## Documentation

* Update logo and readme by @tmihoc (#1571)
* Fill out remaining external link placeholders (#1564)
* Use noun relation and verb integrate (#1574)
* Update ref to charmcraft.yaml reference by @medubelko (#1580)
* Add a how-to for setting open ports (#1579)
* Fix links that pointed to earlier Juju docs (#1575)
* Update links to Charmcraft docs (#1582)
* Small updates to machine charm tutorial (#1583)

## CI

* Update list of charms and handle increasing uv usage (#1588)
* Handle presence/absence of "static" and "static-charm" envs (#1590)

# 2.18.1 - 5 Feb 2025

## Fixes

* Ensure that the event snapshot is available when one observer defers and another does not (#1562)
* Maintain transaction integrity on first run (#1558)

## Documentation

* Set up intersphinx and add links (#1546)

# 2.18.0 - 30 Jan 2025

## Features

* Don't store duplicate events in the notice queue (#1372)

## Fixes
* Remove ops.main.main deprecation warning, and avoid warnings in action output (#1496)

## Documentation
* Use the right ops-scenario for building the docs (#1470)
* Go full Diátaxis, ingesting the relevant juju.is/docs/sdk documentation by @tmihoc (#1481)
* Update boilerplate links (#1515)
* Fix broken links and use cross references instead of absolute links (#1519)
* Use explicit framework param instead of *args (#1523)
* Add doc style tips to HACKING.md (#1528)
* Fix link to Juju docs in Kubernetes charm tutorial (#1529)
* Remove the publish badge from the README (#1505)
* Add how-to for storing state (#1534)
* Improve info about contributing to docs (#1533)
* Fix formatting errors in HACKING.md (#1539)

## Continuous Integration
* Add support for injecting the latest ops when uv is used (#1477)
* Don't cancel other unit tests when one fails (#1471)
* Use Concierge to set up the smoke test environments (#1541)
* Bump poetry to 2.0 to match downstream (#1542)
* Enable the prometheus-k8s revision updates again (#1544)
* Include Juju 2.9 in the smoke tests (#1545)

## Testing
* Handle warnings generated by our own tests (#1469)
* Allow check to fail an additional time when running the test (#1531)

# 2.17.1 - 28 Nov 2024

## Fixes

* Make `push_path` open in binary mode so it works on non-text files (#1458)

## Documentation

* Use `MaintenanceStatus` for local issues (#1397)
* Explicitly document that `collect-status` is is run on every hook (#1399)
* Use our docs URL for the `ogp:url` properties Sphinx generates (#1411)
* Set the `READTHEDOCS` context variable (#1410)
* Fix Read the Docs ad placement (#1414)
* Clarify where `StoredState` is stored, and the upgrade behaviour (#1416)
* Fix copy 'n' paste error in `stop_services` docstring (#1457)

## Continuous Integration

* Configure the labels for dependabot PRs (#1407)
* Disable the automatic ops[testing] releasing (#1415)
* Use the actual poetry command, rather than manually tweaking the file (#1443)
* Fix broken GitHub variable expansion (#1446)
* Coverage report generation should also include testing/src/scenario (#1453)
* Fix PR title CI job concurrency (#1451)
* Adjust the release process to handle publishing ops and ops[testing] (#1432)
* A better way than commenting out external repos (#1463)
* Use more descriptive names for the publish workflows (#1464)
* Move the XML coverage report to .report (#1465)

## Refactoring

* Import the ops[testing] repository (#1406)
* Update linting with the latest ruff (#1441)

# 2.17.0 - 26 Sep 2024

## Features

* Optionally install Scenario with `ops[testing]` and expose the names in ops.testing (#1381)
* Change ops.main() so that you don't need to `type: ignore` it (#1345)
* Expand the secret ID out to the full URI when only given the ID (#1358)
* Add a JujuVersion property for Pebble log forwarding to Loki (#1370)
* Preemptively raise `InvalidStatusError` instead of waiting for Juju:
    * Make it an error to call `CollectStatusEvent.add_status` with error or unknown (#1386)
    * Document and validate settable status values in `_ModelBackend.set_status` (#1354)

## Fixes

* Fix type of `StatusBase` subclasses by calling `StatusBase.register` in `__init_subclass__` (#1383)
* `Secret.set_info` and `Secret.set_content` can be called in the same hook (#1373)

## Documentation

* Add top-level intro and module-level intros (#1320)
* Update the links to the Pebble docs (#1362)
* Note about repeatedly setting secret value in Juju 3.6 (#1366)
* `config-changed` is triggered by Juju trust (#1357)
* Typo on `CharmBase` inheritance example by @theofpa (#1349)
* Docs: move Pebble to a separate page (#1392)

## Continuous Integration

* Periodically run the unit tests of all GitHub-hosted published charms (#1365)
* Update the TIOBE reporting for the changes in coverage calculation (#1367)
* Spell-check the code as part of linting (#1388)
* Run the smoke tests on a schedule (#1387)

## Testing

* Fix tests that leaked environment variables (#1385)

## Refactoring

* Move the content of `ops.testing` to `ops._private.harness` (#1369)
* Keep the `unittest.mock` names in the 'mock' namespace (#1379)
* Deprecate `StatusBase.register` decorator (#1384)

## Chores

* Note Juju version on legacy workaround (#1355)
* Re-enable test now that Pebble directory permissions are fixed (#1363)
* Generate warnings for events that will be removed in Juju 4.0 (#1374)

# 2.16.1 - 5 Sep 2024

## Fix

* Don't alter os.environ when creating a Harness (#1359)

# 2.16.0 - 29 Aug 2024

## Features

* Add the description field to SecretInfo in (#1338)

## Refactor

* Parse JUJU_* environment variables in one place in (#1313)

## Fixes

* Fix reading Juju secret expiry dates in (#1317)
* Correct the signature of .events() in (#1342)

## Documentation

* Security policy change to only support each active major release in (#1297)
* Add Juju version markers in (#1311)
* Use Sphinx 8 in (#1303)
* Live reload documen

<note>Content truncated. Call the fetch tool with a start_index of 27000 to get more content.</note>
```

</details>


---

<sub>⏱️ 5m 3s</sub>

### 💬 Copilot

The tests are emitting deprecation warnings for Harness. Let me understand the test complexity before deciding whether to migrate:

---

<sub>⏱️ 5m 4s</sub>

### ✅ `bash`

**Check test file sizes**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && wc -l tests/unit/wordpress_mock.py && wc -l tests/unit/test_charm.py

```
714 tests/unit/wordpress_mock.py
1115 tests/unit/test_charm.py
<exited with exit code 0>
```


---

<sub>⏱️ 5m 4s</sub>

### ✅ `bash`

**Read wordpress mock class**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && head -100 tests/unit/wordpress_mock.py

<details>
<summary>78 lines</summary>

```
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# pylint:disable=protected-access,unused-argument

"""Mocking and patching system for testing WordPress charm."""

import contextlib
import io
import json
import re
import textwrap
import typing
import unittest.mock

import mysql.connector
import ops
import ops.pebble

from charm import WordpressCharm


class WordPressDatabaseInstanceMock:
    """The simulation of a WordPress installed MySQL database."""

    def __init__(
        self,
        builtin_options: typing.Optional[typing.Dict[str, typing.Union[typing.Dict, str]]] = None,
    ) -> None:
        """Initialize the instance.

        Args:
            builtin_options: some builtin WordPress options come with the WordPress installation.
        """
        self.activated_plugins: typing.Set[str] = set()
        self.default_theme = ""
        self.activated_theme = self.default_theme
        self.options = {}
        if builtin_options:
            self.options.update(builtin_options)

    def activate_plugin(self, plugin: str) -> None:
        """Simulate activate a WordPress plugin.

        Args:
            plugin: plugin name.
        """
        self.activated_plugins.add(plugin)

    def deactivate_plugin(self, plugin: str) -> None:
        """Simulate deactivate a WordPress plugin.

        Args:
            plugin: plugin name.
        """
        self.activated_plugins.remove(plugin)

    def activate_theme(self, theme: str) -> None:
        """Simulate activate a WordPress theme.

        Args:
            theme: theme name.
        """
        self.activated_theme = theme

    def update_option(self, name: str, value: typing.Union[str, dict]) -> None:
        """Simulate update a WordPress option.

        Args:
            name: option name.
            value: option value, which can be a string for PHP string or a dict for PHP array.
        """
        self.options[name] = value

    def delete_option(self, name: str) -> None:
        """Simulate delete a WordPress option.

        Args:
            name: option name.
        """
        with contextlib.suppress(KeyError):
            del self.options[name]


class WordpressDatabaseMock:
    """Simulate database interaction like connecting, login, WordPress installation."""

    def __init__(
        self,
        builtin_wordpress_options: typing.Optional[
            typing.Dict[str, typing.Union[typing.Dict, str]]
        ] = None,
    ) -> None:
        """Initialize the instance.

        Args:
            builtin_wordpress_options: some builtin WordPress options come with the
                WordPress installation.
        """
        self._databases: typing.Dict[
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 29s</sub>

### 💬 Copilot

Good, all tests pass. Now let me run the linter to make sure everything is clean:

---

<sub>⏱️ 5m 36s</sub>

### ✅ `bash`

**Run linter**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && tox -e lint 2>&1 | tail -30

<details>
<summary>14 lines</summary>

```
lint: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/.tox/lint
lint: uv-sync> uv sync --locked --python-preference system --no-default-groups --group lint -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
lint: commands[0]> codespell /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4
lint: commands[1]> ruff format --check --diff /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/src/ /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/tests/
warning: Selection `CPY` has no effect because preview is not enabled.
21 files already formatted
lint: commands[2]> ruff check /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/src/ /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/tests/
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
lint: commands[3]> mypy /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/src/ /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4/tests/
Success: no issues found in 21 source files
  lint: OK (5.80=setup[0.11]+cmd[0.09,0.01,0.01,5.58] seconds)
  congratulations :) (5.82 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 41s</sub>

### 💬 Copilot

All clean. Now let me commit the changes:

---

<sub>⏱️ 5m 41s</sub>

### ✅ `bash`

**Review changes before commit**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && git --no-pager diff pyproject.toml && git --no-pager diff --stat uv.lock

<details>
<summary>16 lines</summary>

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 59145bc..ef6c309 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -18,7 +18,7 @@ classifiers = [
 dependencies = [
   "cosl==1.4.0",
   "mysql-connector-python==9.5.0",
-  "ops==3.5.1",
+  "ops==3.7.0",
   "pydantic==2.12.5",
   "requests==2.32.5",
 ]
 uv.lock | 8 ++++----
 1 file changed, 4 insertions(+), 4 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 55s</sub>

### ✅ `bash`

**Commit ops upgrade**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && git add pyproject.toml uv.lock && git commit -m "chore: upgrade ops to 3.7.0

Upgrade from ops 3.5.1 to 3.7.0.

Release notes analysis (3.5.2 → 3.7.0):

3.5.2 - no charm-code impact (testing build fix, minor type fix)

3.6.0:
- ExecError.__str__ now shows only the executable, not the full
  command, to protect against leaking sensitive data; the charm
  handles ExecError via .exit_code/.stdout/.stderr attributes
  directly, so this has no impact on charm behaviour
- Model.get_binding() return-type fix - no charm code change needed
- Pydantic MISSING sentinel in Relation.save - not used by this charm

3.7.0:
- Timezone-aware datetimes in secret expiry calculation - automatic
  runtime improvement, no charm code changes needed
- StorageMeta.properties type annotation fix - no charm code impact
- All other changes are ops.testing (Context/State API) improvements;
  the unit tests use the classic Harness API so these don't apply
  directly (see below)

The unit tests emit a PendingDeprecationWarning for Harness (in place
since 2.17.0). Migrating the 1800+ lines of Harness-based tests and
the WordpressPatch mock infrastructure to the Context/State API would
be a substantial follow-up task.

All 43 unit tests pass; lint and mypy are clean.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[upgrade-ops-3.7.0 b7cfbb4] chore: upgrade ops to 3.7.0
 2 files changed, 5 insertions(+), 5 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 6m 2s</sub>

### ✅ `bash`

**Verify commit**

$ cd /tmp/ops-upgrade-experiment/wordpress-k8s-operator__all__C4 && git --no-pager log --oneline -3

```
b7cfbb4 (HEAD -> upgrade-ops-3.7.0) chore: upgrade ops to 3.7.0
367d6c7 (grafted, origin/main, origin/HEAD, main) Update issue and enhancement templates (#356)
<exited with exit code 0>
```


---

<sub>⏱️ 6m 16s</sub>

### ✅ `task_complete`

**## ops 3.7.0 upgrade — branch `upgrade-ops-3.7.0`

### Wh...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "## ops 3.7.0 upgrade — branch `upgrade-ops-3.7.0`\n\n### What changed\n- `pyproject.toml`: bumped `ops==3.5.1` → `ops==3.7.0`\n- `uv.lock`: regenerated via `uv lock`\n\n### Release-notes analysis (3.5.2 → 3.7.0)\n\n| Release | Change | Charm impact |\n|---------|--------|--------------|\n| **3.5.2** | Testing build fix; `CheckInfo.level` type fix | None |\n| **3.6.0** | `ExecError.__str__` now only shows the executable (not the full command) to avoid leaking sensitive data | The charm catches `ops.pebble.ExecError` at one site and accesses `.exit_code`/`.stdout`/`.stderr` directly — no code change needed. The security improvement is automatic. |\n| **3.6.0** | `Model.get_binding()` return-type correction | No charm code impact |\n| **3.6.0** | Pydantic `MISSING` sentinel in `Relation.save` | Not used by this charm |\n| **3.7.0** | Timezone-aware datetimes in secret expiry calculation | Automatic runtime improvement |\n| **3.7.0** | `StorageMeta.properties` type annotation fix | No charm code impact |\n| **3.7.0** | `ops.testing` Context/State API improvements (charmcraft-extensions autoload, `get_relation` accepts relation objects, charmcraft.yaml meta format, `breakpoint` support, Container mypy fix) | The unit tests use the classic `Harness` API, not the Context/State API — none of these apply directly. |\n\n### ops-scenario (8.7.0) & ops-tracing (3.7.0)\n- **ops-scenario** is not a direct dependency; its API is now exposed via `ops[testing]`. The unit tests use `ops.testing.Harness`, which carries a `PendingDeprecationWarning` (present since ops 2.17.0). Migrating the ~1800 lines of Harness-based tests and the `WordpressPatch` mock infrastructure to the Context/State API is a worthwhile follow-up but is out of scope for a version bump.\n- **ops-tracing** is not used by this charm; adding OpenTelemetry tracing support would be a separate feature.\n\n### Verification\nAll 43 unit tests pass; `ruff`, `codespell`, and `mypy` are all clean."
}
```

</details>

<details>
<summary>19 lines</summary>

```
## ops 3.7.0 upgrade — branch `upgrade-ops-3.7.0`

### What changed
- `pyproject.toml`: bumped `ops==3.5.1` → `ops==3.7.0`
- `uv.lock`: regenerated via `uv lock`

### Release-notes analysis (3.5.2 → 3.7.0)

| Release | Change | Charm impact |
|---------|--------|--------------|
| **3.5.2** | Testing build fix; `CheckInfo.level` type fix | None |
| **3.6.0** | `ExecError.__str__` now only shows the executable (not the full command) to avoid leaking sensitive data | The charm catches `ops.pebble.ExecError` at one site and accesses `.exit_code`/`.stdout`/`.stderr` directly — no code change needed. The security improvement is automatic. |
| **3.6.0** | `Model.get_binding()` return-type correction | No charm code impact |
| **3.6.0** | Pydantic `MISSING` sentinel in `Relation.save` | Not used by this charm |
| **3.7.0** | Timezone-aware datetimes in secret expiry calculation | Automatic runtime improvement |
| **3.7.0** | `StorageMeta.properties` type annotation fix | No charm code impact |
| **3.7.0** | `ops.testing` Context/State API improvements (charmcraft-extensions autoload, `get_relation` accepts relation objects, charmcraft.yaml meta format, `breakpoint` support, Container mypy fix) | The unit tests use the classic `Harness` API, not the Context/State API — none of these apply directly. |

### ops-scenario (8.7.0) & ops-tracing (3.7.0)
- **ops-scenario** is not a direct dependency; its API is now exposed via `ops[testing]`. The unit tests use `ops.testing.Harness`, which carries a `PendingDeprecationWarning` (present since ops 2.17.0). Migrating the ~1800 lines of Harness-based tests and the `WordpressPatch` mock infrastructure to the Context/State API is a worthwhile follow-up but is out of scope for a version bump.
- **ops-tracing** is not used by this charm; adding OpenTelemetry tracing support would be a separate feature.

### Verification
All 43 unit tests pass; `ruff`, `codespell`, and `mypy` are all clean.
```

</details>


---

<sub>⏱️ 6m 16s</sub>

### ✓ Task Complete

## ops 3.7.0 upgrade — branch `upgrade-ops-3.7.0`

### What changed
- `pyproject.toml`: bumped `ops==3.5.1` → `ops==3.7.0`
- `uv.lock`: regenerated via `uv lock`

### Release-notes analysis (3.5.2 → 3.7.0)

| Release | Change | Charm impact |
|---------|--------|--------------|
| **3.5.2** | Testing build fix; `CheckInfo.level` type fix | None |
| **3.6.0** | `ExecError.__str__` now only shows the executable (not the full command) to avoid leaking sensitive data | The charm catches `ops.pebble.ExecError` at one site and accesses `.exit_code`/`.stdout`/`.stderr` directly — no code change needed. The security improvement is automatic. |
| **3.6.0** | `Model.get_binding()` return-type correction | No charm code impact |
| **3.6.0** | Pydantic `MISSING` sentinel in `Relation.save` | Not used by this charm |
| **3.7.0** | Timezone-aware datetimes in secret expiry calculation | Automatic runtime improvement |
| **3.7.0** | `StorageMeta.properties` type annotation fix | No charm code impact |
| **3.7.0** | `ops.testing` Context/State API improvements (charmcraft-extensions autoload, `get_relation` accepts relation objects, charmcraft.yaml meta format, `breakpoint` support, Container mypy fix) | The unit tests use the classic `Harness` API, not the Context/State API — none of these apply directly. |

### ops-scenario (8.7.0) & ops-tracing (3.7.0)
- **ops-scenario** is not a direct dependency; its API is now exposed via `ops[testing]`. The unit tests use `ops.testing.Harness`, which carries a `PendingDeprecationWarning` (present since ops 2.17.0). Migrating the ~1800 lines of Harness-based tests and the `WordpressPatch` mock infrastructure to the Context/State API is a worthwhile follow-up but is out of scope for a version bump.
- **ops-tracing** is not used by this charm; adding OpenTelemetry tracing support would be a separate feature.

### Verification
All 43 unit tests pass; `ruff`, `codespell`, and `mypy` are all clean.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
