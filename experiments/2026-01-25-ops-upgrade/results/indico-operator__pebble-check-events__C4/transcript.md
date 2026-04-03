# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `b37912e2-831d-4f93-8eec-5ccdd03eb4a1`  
> - **Started:** 4/2/2026, 4:02:51 AM  
> - **Duration:** 14m 57s  
> - **Exported:** 4/2/2026, 4:17:48 AM  

---

<sub>⏱️ 6s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 14s</sub>

### ✅ `bash`

**Check current ops version and dependencies**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && cat requirements.txt && echo "---" && grep -E "ops" tox.ini | head -20

```
pydantic==1.10.26
ops>=2.0.0,<3.0.0
---
    ops[testing]==2.21.1
<exited with exit code 0>
```


---

<sub>⏱️ 15s</sub>

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

<sub>⏱️ 27s</sub>

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

<sub>⏱️ 26s</sub>

### ✅ `bash`

**Read main charm file and state**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && head -100 src/charm.py && echo "---" && head -50 src/state.py

<details>
<summary>119 lines</summary>

```
#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm for Indico on kubernetes."""

# pylint: disable=too-many-lines

import logging
import os
import secrets
import typing
from re import findall
from typing import Any, Dict, Iterator, List, Optional, Tuple
from urllib.parse import urlparse

import charms.loki_k8s.v0.loki_push_api
import ops
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires
from ops.charm import ActionEvent, CharmBase, HookEvent, PebbleReadyEvent, RelationDepartedEvent
from ops.jujuversion import JujuVersion
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, Container, MaintenanceStatus, WaitingStatus
from ops.pebble import ExecError

from database_observer import DatabaseObserver
from s3_observer import S3Observer
from saml_observer import SamlObserver
from smtp_observer import SmtpObserver
from state import CharmConfigInvalidError, ProxyConfig, State

logger = logging.getLogger(__name__)

CELERY_PROMEXP_PORT = "9808"
DATABASE_NAME = "indico"
EMAIL_LIST_MAX = 50
EMAIL_LIST_SEPARATOR = ","
INDICO_CUSTOMIZATION_DIR = "/srv/indico/custom"
NGINX_PROMEXP_PORT = "9113"
PORT = 8080
STATSD_PROMEXP_PORT = "9102"
SAML_GROUPS_PLUGIN_NAME = "saml_groups"

UWSGI_TOUCH_RELOAD = "/srv/indico/indico.wsgi"


class InvalidRedisNameError(Exception):
    """Represents invalid redis name error."""


class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attributes
    """Charm for Indico on kubernetes.

    Attrs:
        on: Redis relation charm events.
    """

    on = RedisRelationCharmEvents()

    def __init__(self, *args):
        """Construct.

        Args:
            args: Arguments passed to the CharmBase parent constructor.
        """
        super().__init__(*args)
        self.database = DatabaseObserver(self)
        self.s3 = S3Observer(self)
        self.smtp = SmtpObserver(self)
        self.saml = SamlObserver(self)
        try:
            self.state = State.from_charm(
                self,
                s3_relation_data=self.s3.s3.get_s3_connection_info(),
                smtp_relation_data=self.smtp.smtp.get_relation_data(),
                saml_relation_data=self.saml.saml.get_relation_data(),
            )
        except CharmConfigInvalidError as exc:
            self.unit.status = ops.BlockedStatus(exc.msg)
            return
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.leader_elected, self._on_leader_elected)
        self.framework.observe(self.on.indico_pebble_ready, self._on_pebble_ready)
        self.framework.observe(self.on.indico_nginx_pebble_ready, self._on_pebble_ready)
        self.framework.observe(
            self.on.refresh_external_resources_action, self._refresh_external_resources_action
        )
        # self.framework.observe(self.on.update_status, self._refresh_external_resources)
        self.framework.observe(self.on.add_admin_action, self._add_admin_action)
        self.framework.observe(self.on.anonymize_user_action, self._anonymize_user_action)
        self.redis_broker = RedisRequires(self, "redis-broker")
        self.framework.observe(
            self.redis_broker.charm.on.redis_relation_updated, self._on_config_changed
        )
        self.redis_cache = RedisRequires(self, "redis-cache")
---
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico states."""

import dataclasses
import logging
import os
from typing import Dict, List, Optional, Tuple

import ops
from charms.saml_integrator.v0.saml import SamlRelationData
from charms.smtp_integrator.v0.smtp import SmtpRelationData, TransportSecurity

# pylint: disable=no-name-in-module
from pydantic import AnyHttpUrl, BaseModel, Field, HttpUrl, ValidationError

logger = logging.getLogger(__name__)


class CharmStateBaseError(Exception):
    """Represents an error with charm state."""


class CharmConfigInvalidError(CharmStateBaseError):
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


class ProxyConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """Configuration for accessing Indico through proxy.

    Attributes:
        http_proxy: The http proxy URL.
        https_proxy: The https proxy URL.
        no_proxy: Comma separated list of hostnames to bypass proxy.
    """

    http_proxy: Optional[HttpUrl]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 51s</sub>

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

<sub>⏱️ 51s</sub>

### ✅ `bash`

**Check charm.py size and pebble check usage**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && cat src/charm.py | wc -l && grep -n "pebble_ready\|check\|on_check\|CheckEvent\|pebble_check\|ready_event\|pebble_ready" src/charm.py | head -30

<details>
<summary>12 lines</summary>

```
1003
88:        self.framework.observe(self.on.indico_pebble_ready, self._on_pebble_ready)
89:        self.framework.observe(self.on.indico_nginx_pebble_ready, self._on_pebble_ready)
213:    def _on_pebble_ready(self, event: PebbleReadyEvent) -> None:
315:            "checks": {
349:            "checks": {
381:            "checks": {
452:            "checks": {
482:            "checks": {
509:            "checks": {
895:        # check if the other end of a relation also supports secrets...
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 18s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 20000,
  "start_index": 40000,
  "url": "https://github.com/canonical/operator/releases"
}
```

</details>

```
Contents of https://github.com/canonical/operator/releases:
<error>No more content available.</error>
```


---

<sub>⏱️ 1m 18s</sub>

### ✅ `bash`

**Check for pebble check events usage**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && grep -n "pebble_check\|CheckEvent\|check_failed\|check_recovered\|check_ready" src/charm.py

```

<exited with exit code 1>
```


---

<sub>⏱️ 1m 46s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.0.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 20000,
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

<sub>⏱️ 1m 45s</sub>

### ✅ `bash`

**Check unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && cat tests/unit/test_charm.py 2>/dev/null | head -100 || echo "No unit test file"; ls tests/unit/

```
__init__.py  conftest.py  test_on_leader_elected.py
<exited with exit code 0>
```


---

<sub>⏱️ 2m 9s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.1.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 20000,
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

<sub>⏱️ 2m 9s</sub>

### ✅ `bash`

**Check unit test files**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && ls tests/unit_harness/ && cat tests/unit/conftest.py

<details>
<summary>32 lines</summary>

```
__init__.py  pre_run_script.sh	test_base.py  test_database_observer.py  test_saml_observer.py	test_state.py
conftest.py  test_actions.py	test_core.py  test_s3_observer.py	 test_smtp_observer.py
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for unit tests."""

import pytest
from ops import pebble, testing


@pytest.fixture(scope="function", name="base_state")
def base_state_fixture():
    """State with container and config file set."""
    pebble_layer = pebble.Layer(
        {
            "summary": "indico layer",
            "description": "pebble config layer for indico",
            "services": {
                "indico": {},
            },
        }
    )
    yield {
        "leader": True,
        "containers": {
            # mypy throws an error because it validates against ops.Container.
            testing.Container(  # type: ignore[call-arg]
                name="indico",
                can_connect=True,
                layers={"indico": pebble_layer},
                service_statuses={"indico": pebble.ServiceStatus.ACTIVE},
            )
        },
    }
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 39s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.2.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 20000,
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

<sub>⏱️ 2m 39s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.3.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 20000,
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

<sub>⏱️ 3m 13s</sub>

### 💬 Copilot

Now let me understand what pebble check events are in ops and look at the current charm's pebble checks:

---

<sub>⏱️ 3m 14s</sub>

### ✅ `bash`

**Check ops pebble check events**

$ pip show ops 2>/dev/null | grep -E "Version|Location" && python3 -c "import ops; import ops.pebble; print([x for x in dir(ops) if 'check' in x.lower() or 'Check' in x])" 2>/dev/null

```
Version: 3.7.0
Location: /home/ubuntu/.local/lib/python3.12/site-packages
['CheckInfoMapping', 'LazyCheckInfo', 'PebbleCheckEvent', 'PebbleCheckFailedEvent', 'PebbleCheckRecoveredEvent']
<exited with exit code 0>
```


---

<sub>⏱️ 3m 13s</sub>

### ✅ `bash`

**Look at pebble checks in charm**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && grep -n "checks" src/charm.py | head -40

<details>
<summary>7 lines</summary>

```
315:            "checks": {
349:            "checks": {
381:            "checks": {
452:            "checks": {
482:            "checks": {
509:            "checks": {
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 33s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4/src/charm.py (lines 300-540)

<details>
<summary>241 lines</summary>

```
300.         indico_env_config = self._get_indico_env_config(container)
301.         indico_env_config["INDICO_LOGGING_CONFIG_FILE"] = "indico.logging.yaml"
302.         layer = {
303.             "summary": "Indico layer",
304.             "description": "Indico layer",
305.             "services": {
306.                 "indico": {
307.                     "override": "replace",
308.                     "summary": "Indico service",
309.                     "command": "/srv/indico/start-indico.sh",
310.                     "startup": "enabled",
311.                     "user": "indico",
312.                     "environment": indico_env_config,
313.                 },
314.             },
315.             "checks": {
316.                 "indico-ready": {
317.                     "override": "replace",
318.                     "level": "ready",
319.                     "tcp": {"port": 8081},
320.                 },
321.             },
322.         }
323.         return typing.cast(ops.pebble.LayerDict, layer)
324. 
325.     def _get_celery_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
326.         """Generate pebble config for the celery container.
327. 
328.         Args:
329.             container: Celery container that has the target configuration.
330. 
331.         Returns:
332.             The pebble configuration for the container.
333.         """
334.         indico_env_config = self._get_indico_env_config(container)
335.         indico_env_config["INDICO_LOGGING_CONFIG_FILE"] = "celery.logging.yaml"
336.         layer = {
337.             "summary": "Indico celery layer",
338.             "description": "Indico celery layer",
339.             "services": {
340.                 "celery": {
341.                     "override": "replace",
342.                     "summary": "Indico celery",
343.                     "command": "/usr/bin/indico celery worker -B -E",
344.                     "startup": "enabled",
345.                     "user": "indico",
346.                     "environment": indico_env_config,
347.                 },
348.             },
349.             "checks": {
350.                 "ready": {
351.                     "override": "replace",
352.                     "level": "alive",
353.                     "period": "120s",
354.                     "timeout": "119s",
355.                     "exec": {
356.                         "command": "/usr/bin/indico celery inspect ping",
357.                         "environment": indico_env_config,
358.                     },
359.                 },
360.             },
361.         }
362.         return typing.cast(ops.pebble.LayerDict, layer)
363. 
364.     def _get_nginx_pebble_config(self, _) -> ops.pebble.LayerDict:
365.         """Generate pebble config for the indico-nginx container.
366. 
367.         Returns:
368.             The pebble configuration for the container.
369.         """
370.         layer = {
371.             "summary": "Indico nginx layer",
372.             "description": "Indico nginx layer",
373.             "services": {
374.                 "indico-nginx": {
375.                     "override": "replace",
376.                     "summary": "Nginx service",
377.                     "command": "/usr/sbin/nginx",
378.                     "startup": "enabled",
379.                 },
380.             },
381.             "checks": {
382.                 "nginx-ready": {
383.                     "override": "replace",
384.                     "level": "alive",
385.                     "http": {"url": "http://localhost:8080/health"},
386.                 },
387.             },
388.         }
389.         return typing.cast(ops.pebble.LayerDict, layer)
390. 
391.     def _get_redis_url(self, redis_name: str) -> Optional[str]:
392.         """Get Url for redis charm.
393. 
394.         Args:
395.             redis_name (str): Name of the redis charm to connect to.
396. 
397.         Returns:
398.             Url for the redis charm.
399. 
400.         Raises:
401.            InvalidRedisNameError: If redis name is invalid
402.         """
403.         if redis_name == "redis-broker":
404.             redis = self.redis_broker
405.         elif redis_name == "redis-cache":
406.             redis = self.redis_cache
407.         else:
408.             raise InvalidRedisNameError(f"Invalid Redis name: {redis_name}")
409. 
410.         relation = self.model.get_relation(redis.relation_name)
411.         if not relation:
412.             return None
413.         relation_app_data = relation.data[relation.app]
414.         relation_unit_data = redis.relation_data
415. 
416.         try:
417.             redis_hostname = str(
418.                 relation_app_data.get("leader-host", relation_unit_data["hostname"])
419.             )
420.             redis_port = int(relation_unit_data["port"])
421.             return f"redis://{redis_hostname}:{redis_port}"
422.         except KeyError:
423.             return None
424.         return None
425. 
426.     def _get_celery_prometheus_exporter_pebble_config(self, container) -> ops.pebble.LayerDict:
427.         """Generate pebble config for the celery-prometheus-exporter container.
428. 
429.         Args:
430.             container: Celery container that has the target configuration.
431. 
432.         Returns:
433.             The pebble configuration for the container.
434.         """
435.         indico_env_config = self._get_indico_env_config(container)
436.         layer = {
437.             "summary": "Celery prometheus exporter",
438.             "description": "Prometheus exporter for celery",
439.             "services": {
440.                 "celery-exporter": {
441.                     "override": "replace",
442.                     "summary": "Celery Exporter",
443.                     "command": (
444.                         "celery-exporter"
445.                         f" --broker-url={self._get_redis_url('redis-broker')}"
446.                         " --retry-interval=5"
447.                     ),
448.                     "environment": indico_env_config,
449.                     "startup": "enabled",
450.                 },
451.             },
452.             "checks": {
453.                 "celery-exporter-up": {
454.                     "override": "replace",
455.                     "level": "alive",
456.                     "http": {"url": "http://localhost:9808/health"},
457.                 },
458.             },
459.         }
460.         return typing.cast(ops.pebble.LayerDict, layer)
461. 
462.     def _get_nginx_prometheus_exporter_pebble_config(self, _) -> ops.pebble.LayerDict:
463.         """Generate pebble config for the nginx-prometheus-exporter container.
464. 
465.         Returns:
466.             The pebble configuration for the container.
467.         """
468.         layer = {
469.             "summary": "Nginx prometheus exporter",
470.             "description": "Prometheus exporter for nginx",
471.             "services": {
472.                 "nginx-prometheus-exporter": {
473.                     "override": "replace",
474.                     "summary": "Nginx Exporter",
475.                     "command": (
476.                         "nginx-prometheus-exporter"
477.                         " -nginx.scrape-uri=http://localhost:9080/stub_status"
478.                     ),
479.                     "startup": "enabled",
480.                 },
481.             },
482.             "checks": {
483.                 "nginx-exporter-up": {
484.                     "override": "replace",
485.                     "level": "alive",
486.                     "http": {"url": "http://localhost:9113/metrics"},
487.                 },
488.             },
489.         }
490.         return typing.cast(ops.pebble.LayerDict, layer)
491. 
492.     def _get_statsd_prometheus_exporter_pebble_config(self, _) -> ops.pebble.LayerDict:
493.         """Generate pebble config for the statsd-prometheus-exporter container.
494. 
495.         Returns:
496.             The pebble configuration for the container.
497.         """
498.         layer = {
499.             "summary": "Statsd prometheus exporter",
500.             "description": "Prometheus exporter for statsd",
501.             "services": {
502.                 "statsd-exporter": {
503.                     "override": "replace",
504.                     "summary": "Statsd Exporter",
505.                     "command": ("statsd_exporter"),
506.                     "startup": "enabled",
507.                 },
508.             },
509.             "checks": {
510.                 "statsd-exporter-up": {
511.                     "override": "replace",
512.                     "level": "alive",
513.                     "http": {"url": "http://localhost:9102/metrics"},
514.                 },
515.             },
516.         }
517.         return typing.cast(ops.pebble.LayerDict, layer)
518. 
519.     def _get_installed_plugins(self, container: Container) -> List[str]:
520.         """Return plugins currently installed.
521. 
522.         Args:
523.             container: Container for which the installed plugins will be retrieved.
524. 
525.         Returns:
526.             List containing the installed plugins.
527.         """
528.         process = container.exec(["indico", "setup", "list-plugins"], user="indico")
529.         output, _ = process.wait_output()
530.         # Parse output table, discarding header and footer rows and fetching first column value
531.         return [item.split("|")[1].strip() for item in output.split("\n")[3:-2]]
532. 
533.     def _get_indico_secret_key_from_relation(self) -> Optional[str]:
534.         """Return the Indico secret key needed to deploy multiple Indico instances.
535. 
536.         Returns:
537.             Indico secret key.
538.         """
539.         peer_relation = self.model.get_relation("indico-peers")
540.         assert peer_relation is not None  # nosec
```

</details>


---

<sub>⏱️ 4m 8s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4/src/charm.py (lines 213-300)

<details>
<summary>88 lines</summary>

```
213.     def _on_pebble_ready(self, event: PebbleReadyEvent) -> None:
214.         """Handle the on pebble ready event for the containers.
215. 
216.         Args:
217.             event: Event triggering the pebble ready handler.
218.         """
219.         if not self._are_relations_ready(event) or not event.workload.can_connect():
220.             event.defer()
221.             return
222.         self._config_pebble(event.workload)
223. 
224.     def _config_pebble(self, container: Container) -> None:
225.         """Apply pebble configurations to a container.
226. 
227.         Args:
228.             container: Container to be configured by Pebble.
229.         """
230.         self.unit.status = MaintenanceStatus(f"Adding {container.name} layer to pebble")
231.         if container.name == "indico":
232.             # Plugins need to be installed before adding the layer so that
233.             # they are included in the corresponding env vars
234.             plugins = (
235.                 typing.cast(str, self.config["external_plugins"]).split(",")
236.                 if self.config["external_plugins"]
237.                 else []
238.             )
239.             self._install_plugins(container, plugins)
240.             container.add_layer(container.name, self._get_logrotate_config(), combine=True)
241.             indico_config = self._get_indico_pebble_config(container)
242.             container.add_layer(container.name, indico_config, combine=True)
243.             peer_relation = self.model.get_relation("indico-peers")
244.             if (
245.                 not peer_relation
246.                 or peer_relation.data[self.app].get("celery-unit") == self.unit.name
247.             ):
248.                 celery_config = self._get_celery_pebble_config(container)
249.                 container.add_layer("celery", celery_config, combine=True)
250.                 celery_exporter_config = self._get_celery_prometheus_exporter_pebble_config(
251.                     container
252.                 )
253.                 container.add_layer("celery-exporter", celery_exporter_config, combine=True)
254.             statsd_config = self._get_statsd_prometheus_exporter_pebble_config(container)
255.             container.add_layer("statsd", statsd_config, combine=True)
256.             self._download_customization_changes(container)
257.         if container.name == "indico-nginx":
258.             nginx_config = self._get_nginx_pebble_config(container)
259.             container.add_layer(container.name, nginx_config, combine=True)
260.             nginx_exporter_config = self._get_nginx_prometheus_exporter_pebble_config(container)
261.             container.add_layer("nginx", nginx_exporter_config, combine=True)
262.         self.unit.status = MaintenanceStatus(f"Starting {container.name} container")
263.         container.pebble.replan_services()
264.         if self._are_pebble_instances_ready():
265.             self.unit.set_workload_version(self._get_indico_version())
266.             self.unit.status = ActiveStatus()
267.         else:
268.             self.unit.status = WaitingStatus("Waiting for pebble")
269. 
270.     def _get_logrotate_config(self) -> ops.pebble.LayerDict:
271.         """Generate logrotate pebble layer.
272. 
273.         Returns:
274.             The logrotate pebble layer configuration.
275.         """
276.         layer = {
277.             "summary": "Logrotate service",
278.             "description": "Logrotate service",
279.             "services": {
280.                 "logrotate": {
281.                     "override": "replace",
282.                     "command": 'bash -c "while :; '
283.                     "do sleep 3600; logrotate /srv/indico/logrotate.conf; "
284.                     'done"',
285.                     "startup": "enabled",
286.                 },
287.             },
288.         }
289.         return typing.cast(ops.pebble.LayerDict, layer)
290. 
291.     def _get_indico_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
292.         """Generate pebble config for the indico container.
293. 
294.         Args:
295.             container: Indico container that has the target configuration.
296. 
297.         Returns:
298.             The pebble configuration for the container.
299.         """
300.         indico_env_config = self._get_indico_env_config(container)
```

</details>


---

<sub>⏱️ 4m 9s</sub>

### ✅ `bash`

**Inspect pebble check event classes**

$ python3 -c "
import ops
# Check what pebble check events exist
import inspect
for name in ['PebbleCheckEvent', 'PebbleCheckFailedEvent', 'PebbleCheckRecoveredEvent']:
    cls = getattr(ops, name, None)
    if cls:
        print(f'{name}: {cls}')
        sig = inspect.signature(cls.__init__)
        print(f'  Fields: {list(sig.parameters.keys())}')
"

<details>
<summary>7 lines</summary>

```
PebbleCheckEvent: <class 'ops.charm.PebbleCheckEvent'>
  Fields: ['self', 'handle', 'workload', 'check_name']
PebbleCheckFailedEvent: <class 'ops.charm.PebbleCheckFailedEvent'>
  Fields: ['self', 'handle', 'workload', 'check_name']
PebbleCheckRecoveredEvent: <class 'ops.charm.PebbleCheckRecoveredEvent'>
  Fields: ['self', 'handle', 'workload', 'check_name']
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 40s</sub>

### ✅ `bash`

**List pebble-related events in ops.charm**

$ python3 -c "
import ops
# Check what events are on ops for pebble
import ops.charm
for name in dir(ops.charm):
    if 'pebble' in name.lower() or 'check' in name.lower():
        print(name)
"

<details>
<summary>8 lines</summary>

```
PebbleCheckEvent
PebbleCheckFailedEvent
PebbleCheckRecoveredEvent
PebbleCustomNoticeEvent
PebbleNoticeEvent
PebbleReadyEvent
TYPE_CHECKING
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 40s</sub>

### ✅ `bash`

**Inspect ContainerEvents class**

$ python3 -c "
import ops
# Check how pebble check events work on containers
import inspect
src = inspect.getsource(ops.charm.ContainerEvents)
print(src)
"

```
Traceback (most recent call last):
  File "<string>", line 5, in <module>
AttributeError: module 'ops.charm' has no attribute 'ContainerEvents'. Did you mean: 'ContainerMeta'?
<exited with exit code 1>
```


---

<sub>⏱️ 5m 13s</sub>

### ✅ `bash`

**Inspect PebbleCheckFailedEvent**

$ python3 -c "
import ops
import inspect
# How are check failed/recovered events accessed?
src = inspect.getsource(ops.PebbleCheckFailedEvent)
print(src[:2000])
"

<details>
<summary>11 lines</summary>

```
class PebbleCheckFailedEvent(PebbleCheckEvent):
    """Event triggered when a Pebble check exceeds the configured failure threshold.

    Note that the check may have started passing by the time this event is
    emitted (which will mean that a :class:`~ops.PebbleCheckRecoveredEvent` will be
    emitted next). If the handler is executing code that should only be done
    if the check is currently failing, check the current status with
    ``event.info.status == ops.pebble.CheckStatus.DOWN``.

    See also: `Juju | Hook | <container>-pebble-check-failed <https://documentation.ubuntu.com/juju/3.6/reference/hook/#container-pebble-check-failed>`_.

    .. jujuadded:: 3.6
    """
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 12s</sub>

### ✅ `bash`

**Check test files for pebble check events**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && grep -rn "pebble_check\|check_failed\|check_recovered\|on_check" tests/ | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 5m 52s</sub>

### ✅ `bash`

**Inspect PebbleCheckEvent source**

$ python3 -c "
import ops
import inspect
src = inspect.getsource(ops.PebbleCheckEvent)
print(src[:3000])
"

<details>
<summary>27 lines</summary>

```
class PebbleCheckEvent(WorkloadEvent):
    """Base class for Pebble check events."""

    info: model.LazyCheckInfo
    """Provide access to the check's current state."""

    def __init__(
        self,
        handle: Handle,
        workload: model.Container,
        check_name: str,
    ):
        super().__init__(handle, workload)
        self.info = model.LazyCheckInfo(workload, check_name)

    def snapshot(self) -> dict[str, Any]:
        """Used by the framework to serialize the event to disk.

        Not meant to be called by charm code.
        """
        d = super().snapshot()
        d['check_name'] = self.info.name
        return d

    def restore(self, snapshot: dict[str, Any]):
        """Used by the framework to deserialize the event from disk.

        Not meant to be called by charm code.
        """
        check_name = snapshot.pop('check_name')
        super().restore(snapshot)
        self.info = model.LazyCheckInfo(self.workload, check_name)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 52s</sub>

### ✅ `bash`

**Check how pebble check events are registered**

$ python3 -c "
import ops
# What are the on-events for pebble check?
# Check how to register check failed events
import inspect
src = inspect.getsource(ops.CharmBase)
# Find pebble check
lines = src.split('\n')
for i, line in enumerate(lines):
    if 'check' in line.lower() and ('pebble' in line.lower() or 'fail' in line.lower()):
        print(i, line)
" 2>/dev/null | head -20

```
65             self.on.define_event(f'{container_name}_pebble_check_failed', PebbleCheckFailedEvent)
67                 f'{container_name}_pebble_check_recovered', PebbleCheckRecoveredEvent
<exited with exit code 0>
```


---

<sub>⏱️ 6m 16s</sub>

### ✅ `bash`

**Check CharmBase pebble check event registration**

$ python3 -c "
import ops
import inspect
src = inspect.getsource(ops.CharmBase)
lines = src.split('\n')
# Print around line 60-80 
for i, line in enumerate(lines[50:90], start=50):
    print(i, line)
"

<details>
<summary>41 lines</summary>

```
50             self.on.define_event(f'{relation_name}_relation_broken', RelationBrokenEvent)
51 
52         for storage_name in self.framework.meta.storages:
53             storage_name = storage_name.replace('-', '_')
54             self.on.define_event(f'{storage_name}_storage_attached', StorageAttachedEvent)
55             self.on.define_event(f'{storage_name}_storage_detaching', StorageDetachingEvent)
56 
57         for action_name in self.framework.meta.actions:
58             action_name = action_name.replace('-', '_')
59             self.on.define_event(f'{action_name}_action', ActionEvent)
60 
61         for container_name in self.framework.meta.containers:
62             container_name = container_name.replace('-', '_')
63             self.on.define_event(f'{container_name}_pebble_ready', PebbleReadyEvent)
64             self.on.define_event(f'{container_name}_pebble_custom_notice', PebbleCustomNoticeEvent)
65             self.on.define_event(f'{container_name}_pebble_check_failed', PebbleCheckFailedEvent)
66             self.on.define_event(
67                 f'{container_name}_pebble_check_recovered', PebbleCheckRecoveredEvent
68             )
69 
70     @property
71     def app(self) -> model.Application:
72         """The application that this unit is part of."""
73         return self.framework.model.app
74 
75     @property
76     def unit(self) -> model.Unit:
77         """The current unit."""
78         return self.framework.model.unit
79 
80     @property
81     def meta(self) -> CharmMeta:
82         """Metadata of this charm."""
83         return self.framework.meta
84 
85     @property
86     def charm_dir(self) -> pathlib.Path:
87         """Root directory of the charm as it is running."""
88         return self.framework.charm_dir
89
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 50s</sub>

### 💬 Copilot

Now let me look at the full charm to understand status management and imports:

---

<sub>⏱️ 6m 50s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4/src/charm.py (lines 1-50)

<details>
<summary>50 lines</summary>

```
1. #!/usr/bin/env python3
2. 
3. # Copyright 2025 Canonical Ltd.
4. # See LICENSE file for licensing details.
5. 
6. """Charm for Indico on kubernetes."""
7. 
8. # pylint: disable=too-many-lines
9. 
10. import logging
11. import os
12. import secrets
13. import typing
14. from re import findall
15. from typing import Any, Dict, Iterator, List, Optional, Tuple
16. from urllib.parse import urlparse
17. 
18. import charms.loki_k8s.v0.loki_push_api
19. import ops
20. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
21. from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
22. from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route
23. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
24. from charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires
25. from ops.charm import ActionEvent, CharmBase, HookEvent, PebbleReadyEvent, RelationDepartedEvent
26. from ops.jujuversion import JujuVersion
27. from ops.main import main
28. from ops.model import ActiveStatus, BlockedStatus, Container, MaintenanceStatus, WaitingStatus
29. from ops.pebble import ExecError
30. 
31. from database_observer import DatabaseObserver
32. from s3_observer import S3Observer
33. from saml_observer import SamlObserver
34. from smtp_observer import SmtpObserver
35. from state import CharmConfigInvalidError, ProxyConfig, State
36. 
37. logger = logging.getLogger(__name__)
38. 
39. CELERY_PROMEXP_PORT = "9808"
40. DATABASE_NAME = "indico"
41. EMAIL_LIST_MAX = 50
42. EMAIL_LIST_SEPARATOR = ","
43. INDICO_CUSTOMIZATION_DIR = "/srv/indico/custom"
44. NGINX_PROMEXP_PORT = "9113"
45. PORT = 8080
46. STATSD_PROMEXP_PORT = "9102"
47. SAML_GROUPS_PLUGIN_NAME = "saml_groups"
48. 
49. UWSGI_TOUCH_RELOAD = "/srv/indico/indico.wsgi"
50.
```

</details>


---

<sub>⏱️ 6m 50s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4/src/charm.py (lines 800-1003)

<details>
<summary>204 lines</summary>

```
800.                         "git",
801.                         "clone",
802.                         typing.cast(str, self.config["customization_sources_url"]),
803.                         ".",
804.                     ],
805.                 )
806. 
807.     def _refresh_external_resources(self, _) -> Dict:
808.         """Pull changes from the remote repository and upgrade external plugins.
809. 
810.         Returns:
811.             Dictionary containing the execution results for each of the operations executed.
812.         """
813.         results = {
814.             "customization-changes": False,
815.             "plugin-updates": [],
816.         }
817.         container = self.unit.get_container("indico")
818.         if container.can_connect():
819.             self._download_customization_changes(container)
820.             if self.config["customization_sources_url"]:
821.                 logging.debug("Pulling changes from %s", self.config["customization_sources_url"])
822.                 self._exec_cmd_in_custom_dir(
823.                     container,
824.                     ["git", "pull"],
825.                 )
826.                 logging.debug("Reloading uWSGI")
827.                 self._exec_cmd_in_custom_dir(container, ["touch", UWSGI_TOUCH_RELOAD])
828.                 results["customization-changes"] = True
829.             if self.config["external_plugins"]:
830.                 logging.debug("Upgrading external plugins %s", self.config["external_plugins"])
831.                 plugins = typing.cast(str, self.config["external_plugins"]).split(",")
832.                 self._install_plugins(container, plugins)
833.                 results["plugin-updates"] = plugins
834.         return results
835. 
836.     def _refresh_external_resources_action(self, event: ActionEvent) -> None:
837.         """Refresh external resources and report action result.
838. 
839.         Args:
840.             event: Event triggering the refresh action.
841.         """
842.         results = self._refresh_external_resources(event)
843.         event.set_results(results)
844. 
845.     def _on_leader_elected(self, _) -> None:
846.         """Handle leader-elected event."""
847.         peer_relation = self.model.get_relation("indico-peers")
848.         secret_value = repr(os.urandom(32))
849.         if (
850.             peer_relation
851.             and not self._has_secrets()
852.             and not peer_relation.data[self.app].get("secret-key")
853.         ):
854.             peer_relation.data[self.app].update({"secret-key": secret_value})
855.         elif (
856.             peer_relation
857.             and self._has_secrets()
858.             and not peer_relation.data[self.app].get("secret-id")
859.         ):
860.             secret = self.app.add_secret({"secret-key": secret_value})
861.             peer_relation.data[self.app].update({"secret-id": typing.cast(str, secret.id)})
862.         if peer_relation and not peer_relation.data[self.app].get("celery-unit"):
863.             peer_relation.data[self.app].update({"celery-unit": self.unit.name})
864. 
865.     def _on_peer_relation_departed(self, event: RelationDepartedEvent) -> None:
866.         """Handle the peer relation departed event.
867. 
868.         Args:
869.             event: the event triggering the handler.
870.         """
871.         peer_relation = self.model.get_relation("indico-peers")
872.         if (
873.             self.unit.is_leader()
874.             and peer_relation
875.             and event.departing_unit
876.             and peer_relation.data[self.app].get("celery-unit") == event.departing_unit.name
877.         ):
878.             if self.unit != event.departing_unit:
879.                 peer_relation.data[self.app].update({"celery-unit": self.unit.name})
880.                 container = self.unit.get_container("indico")
881.                 if self._are_relations_ready(event) and container.can_connect():
882.                     self._config_pebble(container)
883.             else:
884.                 # Leadership election will select a new celery-unit
885.                 peer_relation.data[self.app].update({"celery-unit": ""})
886. 
887.     def _has_secrets(self) -> bool:
888.         """Check if current Juju version supports secrets.
889. 
890.         Returns:
891.             If secrets are supported or not.
892.         """
893.         juju_version = JujuVersion.from_environ()
894.         # Because we're only using secrets in a peer relation we don't need to
895.         # check if the other end of a relation also supports secrets...
896.         return juju_version.has_secrets
897. 
898.     def _add_admin_action(self, event: ActionEvent) -> None:
899.         """Add a new user to Indico.
900. 
901.         Args:
902.             event: Event triggered by the add_admin action
903.         """
904.         container = self.unit.get_container("indico")
905.         indico_env_config = self._get_indico_env_config_str(container)
906. 
907.         cmd = [
908.             "/usr/bin/indico",
909.             "autocreate",
910.             "admin",
911.             event.params["email"],
912.             event.params["password"],
913.         ]
914. 
915.         if container.can_connect():
916.             process = container.exec(
917.                 cmd,
918.                 user="indico",
919.                 working_dir="/srv/indico",
920.                 environment=indico_env_config,
921.             )
922.             try:
923.                 output = process.wait_output()
924.                 event.set_results({"user": f"{event.params['email']}", "output": output})
925.             except ExecError as ex:
926.                 logger.exception("Action add-admin failed: %s", ex.stdout)
927. 
928.                 event.fail(
929.                     # Parameter validation errors are printed to stdout
930.                     f"Failed to create admin {event.params['email']}: {ex.stdout!r}"
931.                 )
932. 
933.     def _execute_anonymize_cmd(self, event: ActionEvent) -> Iterator[str]:
934.         """Execute anonymize command for each email.
935. 
936.         Args:
937.             event (ActionEvent): Event triggered by the anonymize-user action
938. 
939.         Yields:
940.             Iterator[str]: Output of each command execution
941.         """
942.         container = self.unit.get_container("indico")
943.         indico_env_config = self._get_indico_env_config_str(container)
944.         for email in event.params["email"].split(EMAIL_LIST_SEPARATOR):
945.             cmd = [
946.                 "/usr/bin/indico",
947.                 "anonymize",
948.                 "user",
949.                 email,
950.             ]
951. 
952.             if not container.can_connect():
953.                 logger.error(
954.                     "Action anonymize-user failed: cannot connect to the Indico workload container"
955.                 )
956.                 self.unit.status = WaitingStatus(
957.                     "Waiting to be able to connect to workload container"
958.                 )
959.                 return
960. 
961.             process = container.exec(
962.                 cmd,
963.                 user="indico",
964.                 working_dir="/srv/indico",
965.                 environment=indico_env_config,
966.             )
967.             try:
968.                 out = process.wait_output()
969.                 yield out[0].replace("\n", "")
970.             except ExecError as ex:
971.                 logger.exception("Action anonymize-user failed: %s", ex.stdout)
972.                 fail_msg = f"Failed to anonymize user {event.params['email']}: {ex.stdout!r}"
973.                 event.fail("Failed to anonymize one or more users, please verify the results.")
974.                 yield fail_msg
975. 
976.     def _anonymize_user_action(self, event: ActionEvent) -> None:
977.         """Anonymize user in Indico.
978. 
979.         If find an error, the action will fail. All the results will be set until the error
980.         has happened.
981. 
982.         Args:
983.             event: Event triggered by the anonymize-user action
984.         """
985.         if len(event.params["email"].split(EMAIL_LIST_SEPARATOR)) > EMAIL_LIST_MAX:
986.             max_reached_msg = (
987.                 "Failed to anonymize user: "
988.                 f"List of more than {EMAIL_LIST_MAX} emails are not allowed"
989.             )
990.             logger.error("Action anonymize-user failed: %s", max_reached_msg)
991.             event.fail(max_reached_msg)
992.             return
993.         output_list = list(self._execute_anonymize_cmd(event))
994.         event.set_results(
995.             {
996.                 "user": f"{event.params['email']}",
997.                 "output": EMAIL_LIST_SEPARATOR.join(output_list),
998.             }
999.         )
1000. 
1001. 
1002. if __name__ == "__main__":  # pragma: no cover
1003.     main(IndicoOperatorCharm, use_juju_for_storage=True)
```

</details>


---

<sub>⏱️ 7m 22s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4/src/charm.py (lines 100-215)

<details>
<summary>116 lines</summary>

```
100.         self.redis_cache = RedisRequires(self, "redis-cache")
101.         self.framework.observe(
102.             self.redis_cache.charm.on.redis_relation_updated, self._on_config_changed
103.         )
104.         self.framework.observe(
105.             self.on["indico-peers"].relation_departed, self._on_peer_relation_departed
106.         )
107.         self._require_nginx_route()
108. 
109.         self._metrics_endpoint = MetricsEndpointProvider(
110.             self,
111.             jobs=[
112.                 {
113.                     "static_configs": [
114.                         {
115.                             "targets": [
116.                                 f"*:{NGINX_PROMEXP_PORT}",
117.                                 f"*:{STATSD_PROMEXP_PORT}",
118.                                 f"*:{CELERY_PROMEXP_PORT}",
119.                             ]
120.                         }
121.                     ]
122.                 }
123.             ],
124.         )
125.         self._grafana_dashboards = GrafanaDashboardProvider(self)
126.         # port 9080 conflicts with the nginx exporter
127.         charms.loki_k8s.v0.loki_push_api.HTTP_LISTEN_PORT = 9090
128.         self._logging = LogProxyConsumer(
129.             self,
130.             relation_name="logging",
131.             log_files="/srv/indico/log/*",
132.             container_name="indico",
133.         )
134. 
135.     def _require_nginx_route(self) -> None:
136.         """Require nginx ingress."""
137.         require_nginx_route(
138.             charm=self,
139.             service_hostname=self._get_external_hostname(),
140.             service_name=self.app.name,
141.             service_port=8080,
142.         )
143. 
144.     def _are_pebble_instances_ready(self) -> bool:
145.         """Check if all pebble instances are up and containers available.
146. 
147.         Returns:
148.             If the containers are up and available.
149.         """
150.         return all(
151.             self.unit.get_container(container_name).can_connect()
152.             for container_name in self.model.unit.containers
153.         )
154. 
155.     def _is_configuration_valid(self) -> Tuple[bool, str]:
156.         """Validate charm configuration.
157. 
158.         Returns:
159.             Tuple containing as first element whether the configuration is valid.
160.             and a string with the error, if any, as second element.
161.         """
162.         site_url = typing.cast(str, self.config["site_url"])
163.         if site_url and not urlparse(site_url).hostname:
164.             return False, "Configuration option site_url is not valid"
165.         return True, ""
166. 
167.     def _get_external_hostname(self) -> str:
168.         """Extract and return hostname from site_url or default to [application name].local.
169. 
170.         Returns:
171.             The site URL defined as part of the site_url configuration or a default value.
172.         """
173.         site_url = typing.cast(str, self.config["site_url"])
174.         if not site_url or not (hostname := urlparse(site_url).hostname):
175.             return f"{self.app.name}.local"
176.         return hostname
177. 
178.     def _get_external_scheme(self) -> str:
179.         """Extract and return schema from site_url.
180. 
181.         Returns:
182.             The HTTP schema.
183.         """
184.         site_url = typing.cast(str, self.config["site_url"])
185.         return urlparse(site_url).scheme if site_url else "http"
186. 
187.     def _get_external_port(self) -> Optional[int]:
188.         """Extract and return port from site_url.
189. 
190.         Returns:
191.             The port number.
192.         """
193.         site_url = typing.cast(str, self.config["site_url"])
194.         return urlparse(site_url).port
195. 
196.     def _are_relations_ready(self, _) -> bool:
197.         """Check if the needed relations are established.
198. 
199.         Returns:
200.             If the needed relations have been established.
201.         """
202.         if self.redis_broker.relation_data is None:
203.             self.unit.status = WaitingStatus("Waiting for redis-broker availability")
204.             return False
205.         if self.redis_cache.relation_data is None:
206.             self.unit.status = WaitingStatus("Waiting for redis-cache availability")
207.             return False
208.         if self.database.uri is None:
209.             self.unit.status = WaitingStatus("Waiting for database availability")
210.             return False
211.         return True
212. 
213.     def _on_pebble_ready(self, event: PebbleReadyEvent) -> None:
214.         """Handle the on pebble ready event for the containers.
215.
```

</details>


---

<sub>⏱️ 7m 22s</sub>

### ✅ `bash`

**Check tox.ini for ops version**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && cat tox.ini | grep -A 5 "ops\|testing"

<details>
<summary>7 lines</summary>

```
ops[testing]==2.21.1
    -r{toxinidir}/requirements.txt
commands =
    coverage run --source={[vars]src_path} \
        -m pytest --ignore={[vars]tst_path}integration -v --tb native -s {posargs}
    coverage report
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 19s</sub>

### 💬 Copilot

Now let me look at ops.JujuContext and existing tests more carefully:

---

<sub>⏱️ 8m 20s</sub>

### ✅ `bash`

**Inspect JujuContext class**

$ python3 -c "
import ops
import inspect
src = inspect.getsource(ops.JujuContext)
print(src[:3000])
"

<details>
<summary>65 lines</summary>

```
@dataclasses.dataclass(frozen=True, kw_only=True)
class JujuContext:
    """Provides the Juju hook context, primarily for charming approaches outside of Ops.

    Juju provides context for the hook in the form of environment variables.
    Rather than directly accessing the environment, charms should use
    :meth:`ops.JujuContext.from_environ` to create a ``JujuContext`` object that contains this
    information.

    Most of the information in ``JujuContext`` is exposed through the
    framework. For example :attr:`ops.JujuContext.model_name` is
    :attr:`ops.Model.name`, and :attr:`ops.JujuContext.action_uuid` is
    :attr:`ops.ActionEvent.id`. Typically, charms should not directly use the
    ``JujuContext`` class -- it is primarily provided to support charming
    approaches outside of the Ops framework.
    """

    # Source: https://documentation.ubuntu.com/juju/3.6/reference/hook/#hook-execution.
    # The HookVars function: https://github.com/juju/juju/blob/be9dce813b631a469eb8ca8b5c6bc3c0fe82b954/internal/worker/uniter/runner/context/context.go#L1398
    # Only a subset of the above source, because these are what are used in ops.

    # These variables are expected to be set in all hooks, and have no sensible default.

    dispatch_path: str
    """The dispatch path in the format of 'actions/do-something'.

    For example 'hooks/workload-pebble-ready' (from ``JUJU_DISPATCH_PATH``).
    """

    hook_name: str
    """The name of the hook.

    For example, 'install' (from ``JUJU_HOOK_NAME``). Note that this is the empty
    string for actions, and for relation, storage, and workload hooks the name
    will be prefixed with the name of the relation, storage, or workload.
    """

    model_name: str
    """The name of the model.

    For example 'foo' (from ``JUJU_MODEL_NAME``).
    """

    model_uuid: str
    """The uuid of the model.

    For example 'cdac5656-2423-4388-8f30-41854b4cca7d' (from ``JUJU_MODEL_UUID``).
    """

    unit_name: str
    """The name of the unit.

    For example 'myapp/0' (from ``JUJU_UNIT_NAME``).
    """

    version: JujuVersion
    """The version of Juju.

    For example '3.4.0' (from ``JUJU_VERSION``).
    """

    # These variables are expected to be set in all hooks, but have reasonable defaults.

    availability_zone: str | None = None
    """The availability zone.

    For example, 'zone1' (from ``JUJU_AVAILABILITY_ZONE``).
    """

    charm_dir: Path = dataclasses.field(
        default_factory=lambda: Path(f'{__file__}/../../..').resolve()
    )
    """The directory where the charm is running.

    For example '/var/lib/juju/agents/unit-bare-0/charm' (from ``JUJU_CHARM_DIR``).
    """

    debug: bool = False
    """Debug mode.

    If true, write logs to stderr as well as to juju-log (from ``JUJU_DEBUG``).
    """

    debug_at: set[str] = dataclasses.field(default_factory=set[str])
    """Where you want to stop when debugging.

    For example 'all' (from ``JUJU_DEBUG_AT``).
    """

    mac
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 20s</sub>

### ✅ `bash`

**Check existing unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && cat tests/unit/test_core.py | head -150

```
cat: tests/unit/test_core.py: No such file or directory
<exited with exit code 0>
```


---

<sub>⏱️ 8m 46s</sub>

### ✅ `bash`

**Check unit test files**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && ls tests/unit/ && cat tests/unit/test_on_leader_elected.py | head -80

<details>
<summary>27 lines</summary>

```
__init__.py  conftest.py  test_on_leader_elected.py
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico charm unit tests."""

from unittest.mock import MagicMock, patch

import ops
from ops import testing

from charm import IndicoOperatorCharm


@patch.object(ops.JujuVersion, "from_environ")
def test_on_leader_elected_when_secrets_supported(mock_juju_env, base_state: dict):
    """
    arrange: charm created, leader selected and secrets supported
    act: re-trigger the leader elected event
    assert: the peer relation containers the secret-key
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    base_state["relations"] = [testing.PeerRelation("indico-peers")]
    state = testing.State(**base_state)
    context = testing.Context(
        charm_type=IndicoOperatorCharm,
    )

    state = context.run(context.on.leader_elected(), state)

    secret_id = state.get_relations("indico-peers")[0].local_app_data["secret-id"]
    context.run(context.on.leader_elected(), state)

    assert state.get_relations("indico-peers")[0].local_app_data["secret-id"]
    assert secret_id == state.get_relations("indico-peers")[0].local_app_data["secret-id"]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 46s</sub>

### ✅ `bash`

**Check harness test files**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && ls tests/unit_harness/ && head -100 tests/unit_harness/test_core.py

<details>
<summary>89 lines</summary>

```
__init__.py  pre_run_script.sh	test_base.py  test_database_observer.py  test_saml_observer.py	test_state.py
conftest.py  test_actions.py	test_core.py  test_s3_observer.py	 test_smtp_observer.py
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico charm unit tests."""

# pylint:disable=duplicate-code,protected-access
from ast import literal_eval
from secrets import token_hex
from unittest.mock import MagicMock, patch

import ops
import pytest
from ops.testing import Harness

from charm import IndicoOperatorCharm
from state import S3Config, SamlConfig, SamlEndpoint, SmtpConfig
from tests.unit_harness.test_base import TestBase


def test_proxyconfig_invalid(monkeypatch: pytest.MonkeyPatch):
    """
    arrange: given a monkeypatched os.environ mapping that contains invalid proxy values.
    act: when charm is initialized.
    assert: the charm reaches blocked status.
    """
    monkeypatch.setenv("JUJU_CHARM_HTTP_PROXY", "INVALID_URL")
    harness = Harness(IndicoOperatorCharm)
    harness.begin()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


class TestCore(TestBase):  # pylint: disable=too-many-public-methods
    """Indico charm unit tests."""

    def test_redis_ha(self):
        """
        arrange: charm created
        act: change leader-host
        assert: the charm gets the changed url
        """
        self.setUp()
        broker_host = "broker-host"
        broker_port = "1010"
        cache_host = "cache-host"
        cache_port = "1011"

        redis_broker_relation_id = self.harness.add_relation(
            "redis-broker",
            "redis-broker",
            unit_data={"hostname": broker_host, "port": broker_port},
            app_data={"leader-host": broker_host},
        )
        self.harness.add_relation_unit(redis_broker_relation_id, "redis-broker/1")
        self.harness.update_relation_data(
            redis_broker_relation_id,
            "redis-broker/1",
            {"hostname": "broker-host-1", "port": broker_port},
        )
        redis_cache_relation_id = self.harness.add_relation(
            "redis-cache",
            "redis-cache",
            unit_data={"hostname": cache_host, "port": cache_port},
            app_data={"leader-host": cache_host},
        )
        self.harness.add_relation_unit(redis_cache_relation_id, "redis-cache/1")
        self.harness.update_relation_data(
            redis_cache_relation_id,
            "redis-cache/1",
            {"hostname": "cache-host-1", "port": cache_port},
        )

        broker_url = self.harness.charm._get_redis_url("redis-broker")
        cache_url = self.harness.charm._get_redis_url("redis-cache")
        self.assertEqual(broker_url, f"redis://{broker_host}:{broker_port}")
        self.assertEqual(cache_url, f"redis://{cache_host}:{cache_port}")
        broker_host = "broker-host-1"
        cache_host = "cache-host-1"

        self.harness.update_relation_data(
            redis_broker_relation_id,
            "redis-broker",
            {"leader-host": broker_host},
        )

        self.harness.update_relation_data(
            redis_cache_relation_id,
            "redis-cache",
            {"leader-host": cache_host},
        )
        broker_url = self.harness.charm._get_redis_url("redis-broker")
        cache_url = self.harness.charm._get_redis_url("redis-cache")
        self.assertEqual(broker_url, f"redis://{broker_host}:{broker_port}")
        self.assertEqual(cache_url, f"redis://{cache_host}:{cache_port}")

    def test_redis_ha_old(self):
        """
        arrange: charm created
        act: add redis relation with old redis databag
        assert: the charm gets the correct url
        """
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 14s</sub>

### ✅ `bash`

**Check JujuVersion usage**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && grep -n "JujuVersion\|from_environ\|has_secrets" src/charm.py src/state.py

<details>
<summary>8 lines</summary>

```
src/charm.py:26:from ops.jujuversion import JujuVersion
src/charm.py:541:        if not self._has_secrets():
src/charm.py:851:            and not self._has_secrets()
src/charm.py:857:            and self._has_secrets()
src/charm.py:887:    def _has_secrets(self) -> bool:
src/charm.py:893:        juju_version = JujuVersion.from_environ()
src/charm.py:896:        return juju_version.has_secrets
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 15s</sub>

### ✅ `bash`

**Check JujuVersion.has_secrets**

$ python3 -c "
import ops
import inspect
# Check if JujuVersion still exists in ops 3.x and its relationship to JujuContext
src = inspect.getsource(ops.JujuVersion)
# Find has_secrets property
lines = src.split('\n')
for i, line in enumerate(lines):
    if 'secrets' in line.lower():
        print(i, line)
"

```
107     def has_secrets(self) -> bool:
108         """Report whether this Juju version supports the "secrets" feature."""
109         # Juju version 3.0.0 had an initial version of secrets, but:
<exited with exit code 0>
```


---

<sub>⏱️ 9m 51s</sub>

### ✅ `bash`

**Read full tox.ini**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && cat tox.ini

<details>
<summary>169 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

[tox]
skipsdist=True
skip_missing_interpreters = True
envlist = lint, unit, static, coverage-report

[vars]
src_path = {toxinidir}/src/
tst_path = {toxinidir}/tests/
plugins_path = {toxinidir}/indico_rock/plugins/
;lib_path = {toxinidir}/lib/charms/operator_name_with_underscores
all_path = {[vars]src_path} {[vars]tst_path}

[testenv]
setenv =
  PYTHONPATH = {toxinidir}:{toxinidir}/lib:{[vars]src_path}
  PYTHONBREAKPOINT=ipdb.set_trace
  PY_COLORS=1
passenv =
  PYTHONPATH
  CHARM_BUILD_DIR
  MODEL_SETTINGS

[testenv:fmt]
description = Apply coding style standards to code
deps =
    black
    isort
commands =
    isort {[vars]all_path}
    black {[vars]all_path}

[testenv:lint]
basepython = py312
description = Check code against coding style standards
deps =
    black
    codespell
    flake8
    flake8-builtins
    flake8-copyright
    flake8-docstrings
    flake8-docstrings-complete
    flake8-test-docs
    isort
    mypy
    pep8-naming
    pydocstyle>=2.10
    pylint
    pyproject-flake8
    pytest
    pytest-asyncio
    pytest-operator
    requests
    types-PyYAML
    types-requests
    -r{toxinidir}/requirements.txt
commands =
    pydocstyle {[vars]src_path}
    # uncomment the following line if this charm owns a lib
    # codespell {[vars]lib_path}
    codespell {toxinidir} --skip {toxinidir}/.git --skip {toxinidir}/.tox \
      --skip {toxinidir}/build --skip {toxinidir}/lib --skip {toxinidir}/venv \
      --skip {toxinidir}/.mypy_cache --skip {toxinidir}/icon.svg
    # pflake8 wrapper supports config from pyproject.toml
    pflake8 {[vars]all_path} --ignore=W503
    isort --check-only --diff {[vars]all_path}
    black --check --diff {[vars]all_path}
    mypy {[vars]all_path}
    pylint {[vars]all_path}

[testenv:plugins]
# Requires python3.12 installed by pyenv
setenv =
  # patched path for github runners so that tox can find python3.12
  PATH = /home/runner/.pyenv/versions/3.12.2/bin:{env:PATH}
basepython = python3.12
description = Check plugins code against coding style standards
deps =
    black
    codespell
    flake8
    flake8-builtins
    flake8-copyright
    flake8-docstrings
    flake8-docstrings-complete
    flake8-test-docs
    indico==3.3.6
    isort
    mypy
    pep8-naming
    indico_rock/plugins/autocreate
    indico_rock/plugins/anonymize
    pydocstyle>=2.10
    pylint
    pyproject-flake8
    pytest
    pytest-asyncio
    pytest-operator
    requests
    types-PyYAML
    types-requests
    ; 2024/11/19 - there is an incompatibility issue with latest websockets lib release and pylib juju
    websockets<14.0 # https://github.com/juju/python-libjuju/issues/1184
    -r{toxinidir}/requirements.txt
commands =
    codespell {[vars]plugins_path} --skip {toxinidir}/.git --skip {toxinidir}/.tox \
      --skip {toxinidir}/build --skip {toxinidir}/lib --skip {toxinidir}/venv \
      --skip {toxinidir}/.mypy_cache --skip {toxinidir}/icon.svg \
      --skip {toxinidir}/indico_rock/plugins/autocreate/.mypy_cache \
      --skip {toxinidir}/indico_rock/plugins/anonymize/.mypy_cache
    # pflake8 is disabled temporarily due to it not working with python3.12
    # # pflake8 wrapper supports config from pyproject.toml
    # pflake8 {[vars]plugins_path} --ignore=W503
    isort --check-only --diff {[vars]plugins_path}
    black --check --diff {[vars]plugins_path}
    mypy {[vars]plugins_path}
    pylint {[vars]plugins_path} --ignore-paths {[vars]plugins_path}autocreate/build,{[vars]plugins_path}anonymize/build

[testenv:unit]
description = Run unit tests
deps =
    cosl
    coverage[toml]
    pytest
    pytest-mock
    ops[testing]==2.21.1
    -r{toxinidir}/requirements.txt
commands =
    coverage run --source={[vars]src_path} \
        -m pytest --ignore={[vars]tst_path}integration -v --tb native -s {posargs}
    coverage report

[testenv:coverage-report]
description = Create test coverage report
deps =
    coverage[toml]
    pytest
    -r{toxinidir}/requirements.txt
commands =
    coverage report

[testenv:static]
description = Run static analysis tests
deps =
    bandit[toml]
    -r{toxinidir}/requirements.txt
commands =
    bandit -c {toxinidir}/pyproject.toml -r {[vars]src_path} {[vars]tst_path}

[testenv:integration]
description = Run integration tests
deps =
    -r{toxinidir}/requirements.txt
    allure-pytest>=2.8.18
    cosl
    git+https://github.com/canonical/data-platform-workflows@v24.0.0\#subdirectory=python/pytest_plugins/allure_pytest_collection_report
    juju==2.9.49.0
    pytest
    pytest-asyncio
    pytest-operator
    websockets<14.0 # https://github.com/juju/python-libjuju/issues/1184
commands =
    pytest -v --tb native --ignore={[vars]tst_path}unit --log-cli-level=INFO -s {posargs}

[testenv:src-docs]
allowlist_externals=sh
setenv =
    PYTHONPATH = {toxinidir}:{toxinidir}/lib:{[vars]src_path}
description = Generate documentation for src
deps =
    cosl
    lazydocs
    -r{toxinidir}/requirements.txt
commands =
    ; can't run lazydocs directly due to needing to run it on src/* which produces an invocation error in tox
    sh generate-src-docs.sh
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 3s</sub>

### 💬 Copilot

Let me look at how to test pebble check events with ops.testing:

---

<sub>⏱️ 11m 4s</sub>

### ✅ `bash`

**Find check-related testing utilities**

$ python3 -c "
import ops.testing
import inspect
# Find check-related things in testing
for name in dir(ops.testing):
    if 'check' in name.lower() or 'Check' in name.lower():
        print(name)
"

```
CheckInfo
<exited with exit code 0>
```


---

<sub>⏱️ 11m 4s</sub>

### ✅ `bash`

**Inspect ops.testing.CheckInfo**

$ python3 -c "
import ops.testing
import inspect
# Inspect CheckInfo in testing
src = inspect.getsource(ops.testing.CheckInfo)
print(src)
"

<details>
<summary>74 lines</summary>

```
@dataclasses.dataclass(frozen=True, init=False)
class CheckInfo:
    """A health check for a Pebble workload container."""

    name: str
    """Name of the check."""

    level: pebble.CheckLevel | None
    """Level of the check."""

    startup: pebble.CheckStartup
    """Startup mode of the check."""

    status: pebble.CheckStatus
    """Status of the check.

    :attr:`ops.pebble.CheckStatus.UP` means the check is healthy (the number of
    failures is fewer than the threshold), :attr:`ops.pebble.CheckStatus.DOWN`
    means the check is unhealthy (the number of failures has reached the
    threshold), and :attr:`ops.pebble.CheckStatus.INACTIVE` means the check has
    been stopped, so is not currently running.
    """

    successes: int | None
    """Number of times this check has succeeded.

    Set this to None to simulate an older version of Pebble which doesn't have
    the ``successes`` field (introduced in Pebble v1.23.0).
    """

    failures: int
    """Number of failures since the check last succeeded."""

    threshold: int
    """Failure threshold.

    This is how many consecutive failures for the check to be considered 'down'.
    """

    change_id: pebble.ChangeID | None
    """The ID of the Pebble Change associated with this check.

    Passing ``None`` will automatically assign a new Change ID if the status is
    :attr:`ops.pebble.CheckStatus.UP` or :attr:`ops.pebble.CheckStatus.DOWN`.
    """

    def __init__(
        self,
        name: str,
        *,
        level: pebble.CheckLevel | str | None = None,
        startup: pebble.CheckStartup = pebble.CheckStartup.ENABLED,
        status: pebble.CheckStatus = pebble.CheckStatus.UP,
        successes: int | None = 0,
        failures: int = 0,
        threshold: int = 3,
        change_id: pebble.ChangeID | None = None,
    ):
        object.__setattr__(self, 'name', name)
        if level is not None:
            level = pebble.CheckLevel(level)
        object.__setattr__(self, 'level', level)
        object.__setattr__(self, 'startup', startup)
        object.__setattr__(self, 'status', status)
        object.__setattr__(self, 'successes', successes)
        object.__setattr__(self, 'failures', failures)
        object.__setattr__(self, 'threshold', threshold)
        if change_id is None:
            if self.status == pebble.CheckStatus.INACTIVE:
                change_id = ''
            else:
                change_id = pebble.ChangeID(_generate_new_change_id())
        object.__setattr__(self, 'change_id', change_id)

    def __hash__(self) -> int:
        return hash(self.name)

    def _to_ops(self) -> pebble.CheckInfo:
        return pebble.CheckInfo(
            name=self.name,
            level=self.level,
            startup=self.startup,
            status=self.status,
            successes=self.successes,
            failures=self.failures,
            threshold=self.threshold,
            change_id=self.change_id,
        )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 17s</sub>

### ✅ `bash`

**Find pebble check event methods in testing**

$ python3 -c "
import ops.testing
import inspect
# Find how to emit pebble check events in testing
for name in dir(ops.testing.Context.on):
    if 'check' in name.lower():
        print(name)
" 2>/dev/null || python3 -c "
import ops.testing
# Find the on object
ctx_on = ops.testing.Context.__dict__.get('on')
print(type(ctx_on))
import inspect
for name in dir(ops.testing):
    if 'Event' in name or 'event' in name:
        print(name)
"

```
<class 'NoneType'>
CharmEvents
DeferredEvent
<exited with exit code 0>
```


---

<sub>⏱️ 12m 1s</sub>

### ✅ `bash`

**Check testing CharmEvents for pebble check**

$ python3 -c "
import ops.testing
import inspect
from charm import IndicoOperatorCharm
ctx = ops.testing.Context(IndicoOperatorCharm)
print([m for m in dir(ctx.on) if 'check' in m.lower()])
" 2>/dev/null || echo "Need to check differently"

python3 -c "
import ops.testing
# What events does Context.on expose?
import inspect
src = inspect.getsource(ops.testing._CharmEvents)
print(src[:3000])
" 2>/dev/null || python3 -c "
import ops.testing
import inspect
# Find CharmEvents in testing
for name in dir(ops.testing):
    print(name)
" | grep -i charm

<details>
<summary>7 lines</summary>

```
Need to check differently
CharmBase
CharmEvents
CharmMeta
CharmType
charm
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12m 42s</sub>

### ✅ `bash`

**Inspect CharmEvents in testing**

$ python3 -c "
import ops.testing
import inspect
src = inspect.getsource(ops.testing.CharmEvents)
print(src[:4000])
"

<details>
<summary>98 lines</summary>

```
class CharmEvents:
    """Events generated by Juju or ops pertaining to the application lifecycle.

    The events listed as attributes of this class should be accessed via the
    :attr:`Context.on` attribute. For example::

        ctx.run(ctx.on.config_changed(), state)

    This behaves similarly to the :class:`ops.CharmEvents` class but is much
    simpler as there are no dynamically named attributes, and no ``__getattr__``
    version to get events. In addition, all of the attributes are methods,
    which are used to connect the event to the specific object that they relate
    to (or, for simpler events like "start" or "stop", take no arguments).
    """

    @staticmethod
    @_copy_doc(ops.InstallEvent)
    def install():  # noqa: D102
        return _Event('install')

    @staticmethod
    @_copy_doc(ops.StartEvent)
    def start():  # noqa: D102
        return _Event('start')

    @staticmethod
    @_copy_doc(ops.StopEvent)
    def stop():  # noqa: D102
        return _Event('stop')

    @staticmethod
    @_copy_doc(ops.RemoveEvent)
    def remove():  # noqa: D102
        return _Event('remove')

    @staticmethod
    @_copy_doc(ops.UpdateStatusEvent)
    def update_status():  # noqa: D102
        return _Event('update_status')

    @staticmethod
    @_copy_doc(ops.ConfigChangedEvent)
    def config_changed():  # noqa: D102
        return _Event('config_changed')

    @staticmethod
    @_copy_doc(ops.UpgradeCharmEvent)
    def upgrade_charm():  # noqa: D102
        return _Event('upgrade_charm')

    @staticmethod
    @_copy_doc(ops.PreSeriesUpgradeEvent)
    def pre_series_upgrade():  # noqa: D102
        return _Event('pre_series_upgrade')

    @staticmethod
    @_copy_doc(ops.PostSeriesUpgradeEvent)
    def post_series_upgrade():  # noqa: D102
        return _Event('post_series_upgrade')

    @staticmethod
    @_copy_doc(ops.LeaderElectedEvent)
    def leader_elected():  # noqa: D102
        return _Event('leader_elected')

    @staticmethod
    @_copy_doc(ops.SecretChangedEvent)
    def secret_changed(secret: Secret):  # noqa: D102
        if secret.owner:
            raise ValueError(
                'This unit will never receive secret-changed for a secret it owns.',
            )
        return _Event('secret_changed', secret=secret)

    @staticmethod
    @_copy_doc(ops.SecretExpiredEvent)
    def secret_expired(secret: Secret, *, revision: int):  # noqa: D102
        if not secret.owner:
            raise ValueError(
                'This unit will never receive secret-expire for a secret it does not own.',
            )
        return _Event('secret_expired', secret=secret, secret_revision=revision)

    @staticmethod
    @_copy_doc(ops.SecretRotateEvent)
    def secret_rotate(secret: Secret):  # noqa: D102
        if not secret.owner:
            raise ValueError(
                'This unit will never receive secret-rotate for a secret it does not own.',
            )
        return _Event('secret_rotate', secret=secret)

    @staticmethod
    @_copy_doc(ops.SecretRemoveEvent)
    def secret_remove(secret: Secret, *, revision: int):  # noqa: D102
        if not secret.owner:
            raise ValueError(
                'This unit will never receive secret-removed for a secret it does not own.',
            )
        return _Event('secret_remove', secret=secret, secret_revision=revision)

    @staticmethod
    def collect_app_status():
        """Event triggered at the end of every hook to collect app statuses for evaluation."""
        return _Event('collect_app_status')

    @staticmethod
    def collect_unit_status():
        """Event triggered at the end of every hook to collect unit statuses for evaluation."""
        return _Event('collect_unit_status')

    @staticmethod
    @_copy_doc(ops.RelationCreatedEvent)
    def relation_created(relation: RelationBase):  # noqa: D102
        return _Event(f'{relation.endpoint}_relation_created', relation=relation)

    @staticmethod
    @_copy_doc(ops.Relat
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 13m 23s</sub>

### ✅ `bash`

**Find pebble events in testing CharmEvents**

$ python3 -c "
import ops.testing
import inspect
src = inspect.getsource(ops.testing.CharmEvents)
# Find pebble_check
idx = src.find('pebble_check')
if idx >= 0:
    print(src[idx-200:idx+500])
else:
    idx = src.find('pebble_ready')
    if idx >= 0:
        print(src[idx-50:idx+1000])
"

<details>
<summary>21 lines</summary>

```
vent(
            f'{container.name}_pebble_custom_notice',
            container=container,
            notice=notice,
        )

    @staticmethod
    @_copy_doc(ops.PebbleCheckFailedEvent)
    def pebble_check_failed(container: Container, info: CheckInfo):  # noqa: D102
        return _Event(
            f'{container.name}_pebble_check_failed',
            container=container,
            check_info=info,
        )

    @staticmethod
    @_copy_doc(ops.PebbleCheckRecoveredEvent)
    def pebble_check_recovered(container: Container, info: CheckInfo):  # noqa: D102
        return _Event(
            f'{container.name}_pebble_check_recovered',
            container=container,
            chec
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 14m 6s</sub>

### 💬 Copilot

Now I have all the information needed. Let me also check the existing unit tests for patterns:

---

<sub>⏱️ 14m 7s</sub>

### ✅ `bash`

**Read existing unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && cat tests/unit/test_on_leader_elected.py && cat tests/unit/__init__.py

<details>
<summary>28 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico charm unit tests."""

from unittest.mock import MagicMock, patch

import ops
from ops import testing

from charm import IndicoOperatorCharm


@patch.object(ops.JujuVersion, "from_environ")
def test_on_leader_elected_when_secrets_supported(mock_juju_env, base_state: dict):
    """
    arrange: charm created, leader selected and secrets supported
    act: re-trigger the leader elected event
    assert: the peer relation containers the secret-key
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    base_state["relations"] = [testing.PeerRelation("indico-peers")]
    state = testing.State(**base_state)
    context = testing.Context(
        charm_type=IndicoOperatorCharm,
    )

    state = context.run(context.on.leader_elected(), state)

    secret_id = state.get_relations("indico-peers")[0].local_app_data["secret-id"]
    context.run(context.on.leader_elected(), state)

    assert state.get_relations("indico-peers")[0].local_app_data["secret-id"]
    assert secret_id == state.get_relations("indico-peers")[0].local_app_data["secret-id"]
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 14m 7s</sub>

### ✅ `bash`

**Read unit test conftest**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && cat tests/unit/conftest.py

<details>
<summary>30 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for unit tests."""

import pytest
from ops import pebble, testing


@pytest.fixture(scope="function", name="base_state")
def base_state_fixture():
    """State with container and config file set."""
    pebble_layer = pebble.Layer(
        {
            "summary": "indico layer",
            "description": "pebble config layer for indico",
            "services": {
                "indico": {},
            },
        }
    )
    yield {
        "leader": True,
        "containers": {
            # mypy throws an error because it validates against ops.Container.
            testing.Container(  # type: ignore[call-arg]
                name="indico",
                can_connect=True,
                layers={"indico": pebble_layer},
                service_statuses={"indico": pebble.ServiceStatus.ACTIVE},
            )
        },
    }
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 14m 57s</sub>

### ✅ `bash`

**Check containers in metadata.yaml**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C4 && grep -A 20 "containers:" metadata.yaml

<details>
<summary>19 lines</summary>

```
containers:
  indico:
    resource: indico-image
  indico-nginx:
    resource: indico-nginx-image

resources:
  indico-image:
    type: oci-image
    description: OCI image for Indico
  indico-nginx-image:
    type: oci-image
    description: OCI image for nginx Indico

provides:
  grafana-dashboard:
    interface: grafana_dashboard
  metrics-endpoint:
    interface: prometheus_scrape

requires:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 14m 57s</sub>

### ℹ️ Info

Operation cancelled by user

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
