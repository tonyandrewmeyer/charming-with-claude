# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `ade6e9cf-7976-418a-92aa-0712bf9e92b9`  
> - **Started:** 3/15/2026, 3:39:36 PM  
> - **Duration:** 12m 19s  
> - **Exported:** 3/15/2026, 3:51:55 PM  

---

<sub>⏱️ 5s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 12s</sub>

### ✅ `bash`

**Check current ops version and project structure**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && cat pyproject.toml | head -60 && echo "---" && cat charmcraft.yaml | head -40

<details>
<summary>92 lines</summary>

```
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
[project]
name = "loki-k8s"
version = "0.0"
requires-python = "~=3.8"

dependencies = [
  "ops",
  "cosl",
  "kubernetes",
  "requests",
  "pyyaml",
  "lightkube",
  "lightkube-models",
  "aiohttp!=3.11.13",  # Yanked
  "jsonschema",
  "cryptography",
  "pydantic>=2.9.0",
  "importlib-metadata==6.0.0",
  "opentelemetry-api==1.21.0",
  "opentelemetry-exporter-otlp-proto-common==1.21.0",
  "opentelemetry-exporter-otlp-proto-http==1.21.0",
  "opentelemetry-proto==1.21.0",
  "opentelemetry-sdk==1.21.0",
  "opentelemetry-semantic-conventions==0.42b0",
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
  "ops[testing]",
  "responses",
  "fs",
  # Interface
  "pytest-interface-tester",
  # Integration
  "juju",
  "pytest-operator",
  "minio",
  "sh",
]

# Testing tools configuration
[tool.coverage.run]
branch = true

[tool.coverage.report]
show_missing = true

# Formatting tools configuration
[tool.black]
line-length = 99
---
# Learn more about charmcraft.yaml configuration at:
# https://juju.is/docs/sdk/charmcraft-config
name: loki-k8s
type: "charm"
summary: Loki is a log aggregation system inspired by Prometheus.
description: >
  Loki is a set of components that can be composed into a fully featured logging stack.

links:
  documentation: https://discourse.charmhub.io/t/loki-k8s-docs-index/5228
  website: https://charmhub.io/loki-k8s
  source: https://github.com/canonical/loki-k8s-operator
  issues: https://github.com/canonical/loki-k8s-operator/issues

assumes:
  - k8s-api
  - juju >= 3.6  # Juju 3.0.3+ needed for secrets and open-port

platforms:
  ubuntu@24.04:amd64:

parts:
  charm:
    source: .
    plugin: uv
    build-packages: [git]
    build-snaps: [astral-uv]
    override-build: |
      craftctl default
      git describe --always > $CRAFT_PART_INSTALL/version
  cos-tool:
    plugin: dump
    source: https://github.com/canonical/cos-tool/releases/latest/download/cos-tool-${CRAFT_ARCH_BUILD_FOR}
    source-type: file
    permissions:
      - path: cos-tool-${CRAFT_ARCH_BUILD_FOR}
        mode: "755"

containers:
  loki:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12s</sub>

### ✅ `bash`

**List Python files in lib and src**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && find lib -name "*.py" | head -30 && echo "---" && find src -name "*.py" | head -20

<details>
<summary>17 lines</summary>

```
lib/charms/observability_libs/v0/kubernetes_compute_resources_patch.py
lib/charms/tempo_coordinator_k8s/v0/tracing.py
lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py
lib/charms/alertmanager_k8s/v1/alertmanager_dispatch.py
lib/charms/loki_k8s/v1/loki_push_api.py
lib/charms/loki_k8s/v0/charm_logging.py
lib/charms/loki_k8s/v0/loki_push_api.py
lib/charms/grafana_k8s/v0/grafana_dashboard.py
lib/charms/grafana_k8s/v0/grafana_source.py
lib/charms/catalogue_k8s/v1/catalogue.py
lib/charms/prometheus_k8s/v0/prometheus_scrape.py
lib/charms/traefik_k8s/v1/ingress_per_unit.py
lib/charms/tls_certificates_interface/v4/tls_certificates.py
---
src/config_builder.py
src/charm.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Check current ops version**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && pip show ops 2>/dev/null | head -5 && echo "---" && cat uv.lock | grep -A3 'name = "ops"' | head -20

<details>
<summary>27 lines</summary>

```
Name: ops
Version: 2.23.2
Summary: The Python library behind great charms
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
---
    { name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.11.4", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
--
    { name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.11.4", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
--
    { name = "ops", extra = ["testing"] },
    { name = "pyright" },
    { name = "pytest" },
    { name = "pytest-interface-tester" },
--
    { name = "ops" },
    { name = "ops", extras = ["testing"], marker = "extra == 'dev'" },
    { name = "pydantic", specifier = ">=2.9.0" },
    { name = "pyright", marker = "extra == 'dev'" },
    { name = "pytest", marker = "extra == 'dev'" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Check available ops versions**

$ pip index versions ops 2>/dev/null | head -5 || pip install ops --dry-run 2>&1 | head -10

```
ops (3.6.0)
Available versions: 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 2.20.0, 2.19.4, 2.19.0, 2.18.1, 2.18.0, 2.17.1, 2.17.0, 2.16.1, 2.16.0, 2.15.0, 2.14.1, 2.14.0, 2.13.0, 2.12.0, 2.11.0, 2.10.0, 2.9.0, 2.8.0, 2.7.0, 2.6.0, 2.5.1, 2.5.0, 2.4.1, 2.4.0, 2.3.0, 2.2.0, 2.1.1, 2.1.0, 2.0.0, 1.5.5, 1.5.4, 1.5.3, 1.5.2, 1.5.1, 1.5.0, 1.4.0, 1.3.0, 1.2.0, 1.1.0, 1.0.1, 1.0.0, 0.10.0, 0.9.0, 0.8.0, 0.7.0, 0.6.1, 0.6.0, 0.4.7, 0.4.6, 0.4.5, 0.4.4, 0.4.3, 0.4.2, 0.2.1, 0.2.0, 0.1.0
  INSTALLED: 2.23.2
  LATEST:    3.6.0
<exited with exit code 0>
```


---

<sub>⏱️ 43s</sub>

### ✅ `bash`

**Check ops-scenario version**

$ pip show ops-scenario 2>/dev/null | head -5 && pip index versions ops-scenario 2>/dev/null | head -3

<details>
<summary>9 lines</summary>

```
Name: ops-scenario
Version: 7.23.2
Summary: Python library providing a state-transition testing API for Operator Framework charms.
Home-page: 
Author: 
ops-scenario (8.6.0)
Available versions: 8.6.0, 8.5.2, 8.5.1, 8.5.0, 8.4.0, 8.3.1, 8.3.0, 8.2.0, 8.1.0, 8.0.0, 7.23.2, 7.23.1, 7.23.0, 7.22.0, 7.21.1, 7.21.0, 7.20.0, 7.19.4, 7.2.0, 7.1.3, 7.1.2, 7.1.1, 7.0.5, 7.0.4, 7.0.3, 7.0.2, 7.0.1, 7.0.0, 6.1.7, 6.1.6, 6.1.5, 6.1.4, 6.1.3, 6.1.2, 6.1.1, 6.1.0, 6.0.5, 6.0.4, 6.0.3, 6.0.2, 6.0.1, 6.0, 5.8.1, 5.8, 5.7.1, 5.7, 5.6.2, 5.6.1, 5.6, 5.5, 5.4.1, 5.4, 5.3.1, 5.3, 5.2.2, 5.2.1, 5.2, 5.1.3, 5.1.2, 5.1.1, 5.1.0, 5.0, 4.0.4.1, 4.0.4, 4.0.3, 4.0.2, 4.0.1, 4.0, 3.1, 3.0.2, 3.0.1, 2.2, 2.1.3.5, 2.1.3.4, 2.1.3.3, 2.1.3.2, 2.1.3.1, 2.1.3, 2.1.2.5, 2.1.2.4, 2.1.2.3, 2.1.2.2, 2.1.2.1, 2.1.1, 2.1.0, 2.0.5, 2.0.4, 2.0.0
  INSTALLED: 7.23.2
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 43s</sub>

### ✅ `bash`

**Check ops-tracing version**

$ pip show ops-tracing 2>/dev/null | head -5 && pip index versions ops-tracing 2>/dev/null | head -3

<details>
<summary>9 lines</summary>

```
Name: ops-tracing
Version: 2.23.2
Summary: The tracing facility for the Ops library.
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
ops-tracing (3.6.0)
Available versions: 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 0.9.6, 0.9.4, 0.9.3, 0.9.2, 0.9.1, 0.9.0
  INSTALLED: 2.23.2
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 48s</sub>

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
*   Document how to extract the charm instance from the testing context in [#2084](https://github.com/canonical/oper

<note>Content truncated. Call the fetch tool with a start_index of 15000 to get more content.</note>
```

</details>


---

<sub>⏱️ 48s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/ops-scenario/releases**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/ops-scenario/releases",
  "max_length": 10000
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

<sub>⏱️ 53s</sub>

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
<summary>135 lines</summary>

```
Contents of https://github.com/canonical/operator/releases:
ator/pull/2084)
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

## 3.3.1: fix loading the Juju machine ID

16 Oct 01:45

This is a bug-fix release to fix an issue introduced in Ops 3.3.0 (in production) and Ops 3.2.0 (in testing), where loading the Juju machine ID would fail if the ID was not an integer.

The type of the machine ID (both in `ops.JujuContext` and `testing.Context`) is changed from `int` to `str`, so some code or tests may need to be adjusted to use the correct type.

## What's Changed

### Fixes

*   Change JujuContext.machine\_id from int to str ([#2108](https://github.com/canonical/operator/pull/2108))

**Full Changelog**: [3.3.0...3.3.1](https://github.com/canonical/operator/compare/3.3.0...3.3.1)
```

</details>


---

<sub>⏱️ 54s</sub>

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
*   [Star 259](/login?return_to=%2Fcanonical%2Foperator)
    

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

<sub>⏱️ 1m 0s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.1.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
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

<sub>⏱️ 1m 1s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.2.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
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

<sub>⏱️ 1m 1s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.3.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
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

<sub>⏱️ 1m 6s</sub>

### 💬 Copilot

Now let me look at the ops-tracing releases and examine the current charm code in detail:

---

<sub>⏱️ 1m 7s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/operator/releases/tag/ops-tracing-3.0.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://github.com/canonical/operator/releases/tag/ops-tracing-3.0.0"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/operator/releases/tag/ops-tracing-3.0.0 - status code 404
```


---

<sub>⏱️ 1m 7s</sub>

### ✅ `bash`

**Read main charm file**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && cat src/charm.py

<details>
<summary>9 lines</summary>

```
Output too large to read at once (38.8 KB). Saved to: /tmp/copilot-tool-output-1773542443461-i5tewn.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
#
#
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 13s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases?q=ops-tracing**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://github.com/canonical/operator/releases?q=ops-tracing"
}
```

</details>

<details>
<summary>135 lines</summary>

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
*   Add 

<note>Content truncated. Call the fetch tool with a start_index of 15000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 11s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py

```
File too large to read at once (38.5 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


---

<sub>⏱️ 1m 19s</sub>

### ✅ `bash`

**View start of charm.py**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && head -100 src/charm.py

<details>
<summary>90 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import datetime
import logging
import os
import re
import socket
import ssl
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

import yaml
from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerConsumer
from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.grafana_k8s.v0.grafana_source import GrafanaSourceData, GrafanaSourceProvider
from charms.loki_k8s.v0.charm_logging import log_charm
from charms.loki_k8s.v1.loki_push_api import (
    LokiPushApiAlertRulesChanged,
    LokiPushApiProvider,
)
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
from charms.traefik_k8s.v1.ingress_per_unit import IngressPerUnitRequirer
from cosl import JujuTopology
from cosl.interfaces.datasource_exchange import DatasourceDict, DatasourceExchange
from ops import CollectStatusEvent, StoredState
from ops.charm import CharmBase
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
    MaintenanceStatus,
    Port,
    StatusBase,
    WaitingStatus,
)
from ops.pebble import Error, Layer, PathError, ProtocolError

from config_builder import (
    CERT_FILE,
    HTTP_LISTEN_PORT,
    KEY_FILE,
    LOKI_CONFIG,
    LOKI_CONFIG_BACKUP,
    RULES_DIR,
    ConfigBuilder,
)

# To keep a tidy debug-log, we suppress some DEBUG/INFO logs from some imported libs,
# even when charm logging is set to a lower level.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

@dataclass
class TLSConfig:
    """TLS configuration received by the charm over the `certificates` relation."""

    server_cert: str
    ca_cert: str
    private_key: str

class CompositeStatus(TypedDict):
    """Per-component status holder."""

    # These are going to go into stored state, so we must use marshallable objects.
    # They are passed to StatusBase.from_name().
    k8s_patch: Tuple[str, str]
    config: Tuple[str, str]
    rules: Tuple[str, str]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 20s</sub>

### ✅ `bash`

**Check ops-tracing package info**

$ pip show ops-tracing 2>/dev/null && pip index versions ops-tracing 2>/dev/null && python3 -c "import ops_tracing; help(ops_tracing)" 2>&1 | head -50

<details>
<summary>53 lines</summary>

```
Name: ops-tracing
Version: 2.23.2
Summary: The tracing facility for the Ops library.
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
Author-email: 
License: 
Location: /home/ubuntu/.local/lib/python3.12/site-packages
Requires: opentelemetry-sdk, ops, pydantic
Required-by: 
ops-tracing (3.6.0)
Available versions: 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 0.9.6, 0.9.4, 0.9.3, 0.9.2, 0.9.1, 0.9.0
  INSTALLED: 2.23.2
  LATEST:    3.6.0
Help on package ops_tracing:

NAME
    ops_tracing - The tracing facility for the Ops library.

DESCRIPTION
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 27s</sub>

### ✅ `bash`

**Get full ops-tracing help**

$ python3 -c "import ops_tracing; help(ops_tracing)" 2>&1 | head -200

<details>
<summary>166 lines</summary>

```
Help on package ops_tracing:

NAME
    ops_tracing - The tracing facility for the Ops library.

DESCRIPTION
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

PACKAGE CONTENTS
    _api
    _backend
    _buffer
    _export
    _mock

SUBMODULES
    vendor

CLASSES
    ops.framework.Object(builtins.object)
        ops_tracing._api.Tracing

    class Tracing(ops.framework.Object)
     |  Tracing(charm: 'ops.CharmBase', tracing_relation_name: 'str', *, ca_relation_name: 'str | None' = None, ca_data: 'str | None' = None)
     |
     |  Initialise the tracing service.
     |
     |  Usage:
     |      - Include ``ops[tracing]`` in your dependencies.
     |      - Declare the relations that the charm supports.
     |      - Initialise ``Tracing`` with the names of these relations.
     |
     |  Example::
     |
     |      # charmcraft.yaml
     |      requires:
     |          charm-tracing:
     |              interface: tracing
     |              limit: 1
     |              optional: true
     |          receive-ca-cert:
     |              interface: certificate_transfer
     |              limit: 1
     |              optional: true
     |
     |      # src/charm.py
     |      import ops.tracing
     |
     |      class SomeCharm(ops.CharmBase):
     |          def __init__(self, framework: ops.Framework):
     |              ...
     |              self.tracing = ops.tracing.Tracing(
     |                  self,
     |                  tracing_relation_name="charm-tracing",
     |                  ca_relation_name="receive-ca-cert",
     |              )
     |
     |  Args:
     |      charm: your charm instance
     |      tracing_relation_name: the name of the relation that provides the
     |          destination to send trace data to.
     |      ca_relation_name: the name of the relation that provides the CA
     |          list to validate the tracing destination against.
     |      ca_data: a fixed CA list (PEM bundle, a multi-line string).
     |
     |  If the destination is resolved to an HTTPS URL, a CA list is required
     |  to establish a secure connection.
     |
     |  The CA list can be provided over a relation via the ``ca_relation_name``
     |  argument, as a fixed string via the ``ca_data`` argument, or the system CA
     |  list will be used if the earlier two are both ``None``.
     |
     |  Method resolution order:
     |      Tracing
     |      ops.framework.Object
     |      builtins.object
     |
     |  Methods defined here:
     |
     |  __init__(self, charm: 'ops.CharmBase', tracing_relation_name: 'str', *, ca_relation_name: 'str | None' = None, ca_data: 'str | None' = None)
     |      Initialise the tracing service.
     |
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |
     |  __annotations__ = {}
     |
     |  ----------------------------------------------------------------------
     |  Readonly properties inherited from ops.framework.Object:
     |
     |  model
     |      Shortcut for more simple access the model.
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from ops.framework.Object:
     |
     |  __dict__
     |      dictionary for instance variables
     |
     |  __weakref__
     |      list of weak references to the object
     |
     |  ----------------------------------------------------------------------
     |  Data and other attributes inherited from ops.framework.Object:
     |
     |  handle_kind = 'Tracing'

FUNCTIONS
    _mark_observed = mark_observed() -> 'None'
        Mark the trace data collected in this dispatch as higher priority.

    _setup = setup(juju_context: '_JujuContext', charm_class_name: 'str') -> 'None'
        Set up the tracing subsystem and configure OpenTelemetry.

        Args:
            juju_context: the context for this dispatch, for annotation
            charm_class_name: the name of the charm class, for annotation

    _shutdown = shutdown() -> 'None'
        Shutdown tracing, which is expected to flush the buffered data out.

    set_destination(url: 'str | None', ca: 'str | None') -> 'None'
        Configure the destination service for trace data.

        Args:
            url: the URL of the telemetry service to send trace data to.
                An example could be ``http://localhost/v1/traces``.
                None or empty string disables sending out the data, which is still buffered.
            ca: the CA list (PEM bundle, a multi-line string), only used for HTTPS URLs.

DATA
    __all__ = ['Tracing', '_mark_observed', '_setup', '_shutdown', 'set_de...

FILE
    /home/ubuntu/.local/lib/python3.12/site-packages/ops_tracing/__init__.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 28s</sub>

### ✅ `bash`

**Install new ops-tracing and get help**

$ pip install ops-tracing==3.6.0 --quiet && python3 -c "import ops_tracing; help(ops_tracing)" 2>&1 | head -300

<details>
<summary>16 lines</summary>

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.
    
    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.
    
    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 1m 36s</sub>

### ✅ `bash`

**Find tracing usage in charm**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "tracing\|trace_charm\|TracingEndpoint\|charm_tracing_config\|charm_logging\|log_charm" src/charm.py | head -40

<details>
<summary>29 lines</summary>

```
35:from charms.loki_k8s.v0.charm_logging import log_charm
47:from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
48:from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
115:@trace_charm(
116:    tracing_endpoint="_charm_tracing_endpoint",
117:    server_cert="_charm_tracing_ca_cert",
127:@log_charm(logging_endpoints="_charm_logging_endpoints", server_cert="_charm_logging_ca_cert")
244:        self.charm_tracing = TracingEndpointRequirer(
245:            self, relation_name="charm-tracing", protocols=["otlp_http"]
247:        self.workload_tracing = TracingEndpointRequirer(
248:            self, relation_name="workload-tracing", protocols=["jaeger_thrift_http"]
250:        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
251:            self.charm_tracing, self._ca_cert_path
261:            self.workload_tracing.on.endpoint_changed,  # type: ignore
262:            self._on_workload_tracing_endpoint_changed,
265:            self.workload_tracing.on.endpoint_removed,  # type: ignore
266:            self._on_workload_tracing_endpoint_removed,
363:    def _on_workload_tracing_endpoint_changed(self, _) -> None:
364:        """Adds workload tracing information to loki's config."""
367:    def _on_workload_tracing_endpoint_removed(self, _) -> None:
368:        """Removes workload tracing information from loki's config."""
417:        if self.workload_tracing.is_ready():
418:            tempo_endpoint = self.workload_tracing.get_endpoint("jaeger_thrift_http")
689:            # (and charm tracing and logging TLS)
884:    def _charm_logging_endpoints(self) -> List[str]:
888:            scheme = "https" if self._charm_logging_ca_cert else "http"
893:    def _charm_logging_ca_cert(self) -> Optional[str]:
894:        """Server CA certificate path for TLS tracing."""
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 36s</sub>

### ✅ `bash`

**Find test files using scenario/ops.testing**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && find tests -name "*.py" | xargs grep -l "scenario\|ops.testing\|Context\|Harness" 2>/dev/null

<details>
<summary>14 lines</summary>

```
tests/integration/helpers.py
tests/interface/conftest.py
tests/unit/conftest.py
tests/unit/test_log_proxy_consumer.py
tests/unit/test_charm.py
tests/unit/test_grafana_source.py
tests/unit/test_consumer.py
tests/unit/test_datasource_exchange.py
tests/unit/test_charm_logging.py
tests/unit/test_config_reporting_enabled.py
tests/unit/test_transform.py
tests/unit/test_provider.py
tests/unit/test_log_forwarder.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 41s</sub>

### ✅ `bash`

**Check test imports and setup**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && head -50 tests/unit/conftest.py && echo "---" && head -30 tests/unit/test_charm.py

<details>
<summary>65 lines</summary>

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
---
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import json
import os
import unittest
from io import BytesIO
from unittest.mock import Mock, PropertyMock, patch
from urllib.error import HTTPError, URLError

import yaml
from helpers import FakeProcessVersionCheck, k8s_resource_multipatch
from ops.model import ActiveStatus, BlockedStatus, Container, MaintenanceStatus
from ops.testing import Harness

from charm import LOKI_CONFIG as LOKI_CONFIG_PATH  # type: ignore
from charm import LokiOperatorCharm  # type: ignore

METADATA = {
    "model": "consumer-model",
    "model_uuid": "20ce8299-3634-4bef-8bd8-5ace6c8816b4",
    "application": "promtail",
    "charm_name": "charm-k8s",
}

ALERT_RULES = {
    "groups": [
        {
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 41s</sub>

### ✅ `bash`

**Check tox configuration**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && cat tox.ini

<details>
<summary>61 lines</summary>

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
lib_path = {toxinidir}/lib/charms/loki_k8s
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
allowlist_externals=
    {[testenv]allowlist_externals}
    /usr/bin/env
commands =
    /usr/bin/env sh -c 'stat cos-tool-amd64 > /dev/null 2>&1 || curl -L -O https://github.com/canonical/cos-tool/releases/latest/download/cos-tool-amd64 && chmod 755 cos-tool-amd64'
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 47s</sub>

### ✅ `bash`

**Find scenario and ops.testing imports in tests**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "scenario\|from ops.testing" tests/unit/*.py | grep -v "^Binary" | head -40

<details>
<summary>13 lines</summary>

```
tests/unit/conftest.py:6:from ops.testing import Context
tests/unit/conftest.py:7:from scenario import Container, Exec
tests/unit/test_charm.py:16:from ops.testing import Harness
tests/unit/test_charm_logging.py:7:from ops.testing import Container, Exec, Relation, State
tests/unit/test_config_reporting_enabled.py:2:from ops.testing import Container, Exec, State, pebble
tests/unit/test_consumer.py:15:from ops.testing import Harness
tests/unit/test_datasource_exchange.py:12:from scenario import Relation, State
tests/unit/test_grafana_source.py:7:from scenario import Relation, State
tests/unit/test_log_forwarder.py:10:from ops.testing import Harness
tests/unit/test_log_proxy_consumer.py:18:from ops.testing import Harness
tests/unit/test_provider.py:11:from ops.testing import Harness
tests/unit/test_transform.py:10:from ops.testing import Harness
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 47s</sub>

### ✅ `bash`

**Check ops version in lock file**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && cat uv.lock | grep -A5 'name = "ops"' | head -30

<details>
<summary>31 lines</summary>

```
{ name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.11.4", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
    { name = "tenacity", version = "9.0.0", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "tenacity", version = "9.1.2", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
--
    { name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.11.4", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
    { name = "requests" },
]
--
    { name = "ops", extra = ["testing"] },
    { name = "pyright" },
    { name = "pytest" },
    { name = "pytest-interface-tester" },
    { name = "pytest-operator" },
    { name = "responses" },
--
    { name = "ops" },
    { name = "ops", extras = ["testing"], marker = "extra == 'dev'" },
    { name = "pydantic", specifier = ">=2.9.0" },
    { name = "pyright", marker = "extra == 'dev'" },
    { name = "pytest", marker = "extra == 'dev'" },
    { name = "pytest-interface-tester", marker = "extra == 'dev'" },
    { name = "pytest-operator", marker = "extra == 'dev'" },
--
name = "ops"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 53s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/ops-tracing/3.0.0/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://pypi.org/project/ops-tracing/3.0.0/"
}
```

</details>

```
Contents of https://pypi.org/project/ops-tracing/3.0.0/:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 1m 53s</sub>

### ✅ `bash`

**Find charm_tracing and charm_logging usage**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "charm_tracing\|charm_logging\|log_charm" src/charm.py | head -30

<details>
<summary>13 lines</summary>

```
35:from charms.loki_k8s.v0.charm_logging import log_charm
47:from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
48:from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
116:    tracing_endpoint="_charm_tracing_endpoint",
117:    server_cert="_charm_tracing_ca_cert",
127:@log_charm(logging_endpoints="_charm_logging_endpoints", server_cert="_charm_logging_ca_cert")
244:        self.charm_tracing = TracingEndpointRequirer(
250:        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
251:            self.charm_tracing, self._ca_cert_path
884:    def _charm_logging_endpoints(self) -> List[str]:
888:            scheme = "https" if self._charm_logging_ca_cert else "http"
893:    def _charm_logging_ca_cert(self) -> Optional[str]:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 28s</sub>

### ✅ `bash`

**View charm.py tracing setup**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && view src/charm.py 110,270

<details>
<summary>72 lines</summary>

```
2 files to edit
"src/charm.py" [readonly] 957L, 39397B▽             #!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.# See LICENSE file for licensing details.#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import datetime
import logging
import os
import re
import socket
import ssl
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

import yaml
from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerConsumer
from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.grafana_k8s.v0.grafana_source import GrafanaSourceData, GrafanaSourceProvider
from charms.loki_k8s.v0.charm_logging import log_charm
from charms.loki_k8s.v1.loki_push_api import (
    LokiPushApiAlertRulesChanged,
    LokiPushApiProvider,
)
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
from charms.traefik_k8s.v1.ingress_per_unit import IngressPerUnitRequirer
from cosl import JujuTopology
from cosl.interfaces.datasource_exchange import DatasourceDict, DatasourceExchange
from ops import CollectStatusEvent, StoredState
from ops.charm import CharmBase
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
    MaintenanceStatus,
    Port,
    StatusBase,
    WaitingStatus,
)
from ops.pebble import Error, Layer, PathError, ProtocolError

from config_builder import (
    CERT_FILE,
    HTTP_LISTEN_PORT,
    KEY_FILE,
    LOKI_CONFIG,
    LOKI_CONFIG_BACKUP,
    RULES_DIR,
    ConfigBuilder,
)

# To keep a tidy debug-log, we suppress some DEBUG/INFO logs from some imported libs,1,1Top+q436f\+q6b75\+q6b64\+q6b72\+q6b6c\+q2332\+q2334\+q2569\+q2a37\+q6b31\
<command with shellId: 18 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 2m 28s</sub>

### ✅ `bash`

**View charm_tracing_endpoint and related methods**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && view src/charm.py 880,900

<details>
<summary>72 lines</summary>

```
2 files to edit
"src/charm.py" [readonly] 957L, 39397B▽             #!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.# See LICENSE file for licensing details.#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import datetime
import logging
import os
import re
import socket
import ssl
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

import yaml
from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerConsumer
from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.grafana_k8s.v0.grafana_source import GrafanaSourceData, GrafanaSourceProvider
from charms.loki_k8s.v0.charm_logging import log_charm
from charms.loki_k8s.v1.loki_push_api import (
    LokiPushApiAlertRulesChanged,
    LokiPushApiProvider,
)
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
from charms.traefik_k8s.v1.ingress_per_unit import IngressPerUnitRequirer
from cosl import JujuTopology
from cosl.interfaces.datasource_exchange import DatasourceDict, DatasourceExchange
from ops import CollectStatusEvent, StoredState
from ops.charm import CharmBase
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
    MaintenanceStatus,
    Port,
    StatusBase,
    WaitingStatus,
)
from ops.pebble import Error, Layer, PathError, ProtocolError

from config_builder import (
    CERT_FILE,
    HTTP_LISTEN_PORT,
    KEY_FILE,
    LOKI_CONFIG,
    LOKI_CONFIG_BACKUP,
    RULES_DIR,
    ConfigBuilder,
)

# To keep a tidy debug-log, we suppress some DEBUG/INFO logs from some imported libs,1,1Top+q436f\+q6b75\+q6b64\+q6b72\+q6b6c\+q2332\+q2334\+q2569\+q2a37\+q6b31\
<command with shellId: 19 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 2m 32s</sub>

### ✅ `stop_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "18"
}
```

</details>

```
<command with id: 18 stopped>
```


---

<sub>⏱️ 2m 32s</sub>

### ✅ `stop_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "19"
}
```

</details>

```
<command with id: 19 stopped>
```


---

<sub>⏱️ 2m 38s</sub>

### ✅ `bash`

**Read charm.py tracing section**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && sed -n '110,270p' src/charm.py

<details>
<summary>140 lines</summary>

```
"""Convert a tuple to a StatusBase, so it could be used natively with ops."""
    name, message = tpl
    return StatusBase.from_name(name, message)


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
@log_charm(logging_endpoints="_charm_logging_endpoints", server_cert="_charm_logging_ca_cert")
class LokiOperatorCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()
    _port = HTTP_LISTEN_PORT
    _name = "loki"
    _loki_push_api_endpoint = "/loki/api/v1/push"
    _loki_rules_endpoint = "/loki/api/v1/rules"
    _service_name = "loki"
    _ca_cert_path = "/usr/local/share/ca-certificates/cos-ca.crt"

    def __init__(self, *args):
        super().__init__(*args)

        # We need stored state for push statuses.
        # https://discourse.charmhub.io/t/its-probably-ok-for-a-unit-to-go-into-error-state/13022
        self._stored.set_default(
            status=CompositeStatus(
                k8s_patch=to_tuple(ActiveStatus()),
                config=to_tuple(ActiveStatus()),
                rules=to_tuple(ActiveStatus()),
                retention=to_tuple(ActiveStatus()),
            ),
            fresh_install=True,
        )

        self._loki_container = self.unit.get_container(self._name)
        self._node_exporter_container = self.unit.get_container("node-exporter")
        self.unit.set_ports(self._port)

        self._juju_topology = JujuTopology.from_charm(self)

        # If Loki is run in single-tenant mode, all the chunks are put in a folder named "fake"
        # https://grafana.com/docs/loki/latest/operations/storage/filesystem/
        # https://grafana.com/docs/loki/latest/rules/#ruler-storage
        tenant_id = "fake"
        self.rules_dir_tenant = os.path.join(RULES_DIR, tenant_id)

        self.unit.set_ports(Port("tcp", self._port))

        self.resources_patch = KubernetesComputeResourcesPatch(
            self,
            self._loki_container.name,
            resource_reqs_func=self._resource_reqs_from_config,
        )

        self._csr_attributes = CertificateRequestAttributes(
            # the `common_name` field is required but limited to 64 characters.
            # since it's overridden by sans, we can use a short,
            # constrained value like app name.
            common_name=self.app.name,
            sans_dns=frozenset((self.hostname,)),
        )
        self._cert_requirer = TLSCertificatesRequiresV4(
            charm=self,
            relationship_name="certificates",
            certificate_requests=[self._csr_attributes],
        )
        # Update certs here in init to avoid code ordering issues
        self._update_cert()
        self.framework.observe(
            self._cert_requirer.on.certificate_available,  # pyright: ignore
            self._on_certificate_available,
        )

        self.framework.observe(self.resources_patch.on.patch_failed, self._on_k8s_patch_failed)

        self.alertmanager_consumer = AlertmanagerConsumer(self, relation_name="alertmanager")
        self.framework.observe(
            self.alertmanager_consumer.on.cluster_changed, self._on_alertmanager_change
        )

        self.ingress_per_unit = IngressPerUnitRequirer(
            self,
            relation_name="ingress",
            port=self._port,
            scheme=lambda: "https" if self._tls_available else "http",
            strip_prefix=True,
        )
        self.framework.observe(self.ingress_per_unit.on.ready_for_unit, self._on_ingress_changed)
        self.framework.observe(self.ingress_per_unit.on.revoked_for_unit, self._on_ingress_changed)

        self.grafana_source_provider = GrafanaSourceProvider(
            charm=self,
            refresh_event=[
                self.on.loki_pebble_ready,
                self._cert_requirer.on.certificate_available,
            ],
            source_type="loki",
            source_url=self._external_url,
        )

        self.metrics_provider = MetricsEndpointProvider(
            self,
            jobs=self.scrape_jobs,
            refresh_event=[
                self.on.update_status,
                self.ingress_per_unit.on.ready_for_unit,
                self.ingress_per_unit.on.revoked_for_unit,
                self.on.ingress_relation_departed,
                self._cert_requirer.on.certificate_available,
            ],
        )

        external_url = urlparse(self._external_url)
        self.loki_provider = LokiPushApiProvider(
            self,
            address=external_url.hostname or self.hostname,
            port=external_url.port or 443 if self._tls_available else 80,
            scheme=external_url.scheme,
            path=f"{external_url.path}{self._loki_push_api_endpoint}",
        )

        self.dashboard_provider = GrafanaDashboardProvider(self)

        self.catalogue = CatalogueConsumer(charm=self, item=self._catalogue_item)
        self.charm_tracing = TracingEndpointRequirer(
            self, relation_name="charm-tracing", protocols=["otlp_http"]
        )
        self.workload_tracing = TracingEndpointRequirer(
            self, relation_name="workload-tracing", protocols=["jaeger_thrift_http"]
        )
        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
            self.charm_tracing, self._ca_cert_path
        )

        self.datasource_exchange = DatasourceExchange(
            self,
            provider_endpoint="send-datasource",
            requirer_endpoint=None,
        )

        self.framework.observe(
            self.workload_tracing.on.endpoint_changed,  # type: ignore
            self._on_workload_tracing_endpoint_changed,
        )
        self.framework.observe(
            self.workload_tracing.on.endpoint_removed,  # type: ignore
            self._on_workload_tracing_endpoint_removed,
        )

        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 38s</sub>

### ✅ `bash`

**Read charm_tracing properties**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && sed -n '875,900p' src/charm.py

<details>
<summary>24 lines</summary>

```
version_output, _ = self._loki_container.exec(["/usr/bin/loki", "-version"]).wait_output()
        # Output looks like this:
        # loki, version 2.4.1 (branch: HEAD, ...
        result = re.search(r"version (\d*\.\d*\.\d*)", version_output)
        if result is None:
            return result
        return result.group(1)

    @property
    def _charm_logging_endpoints(self) -> List[str]:
        """Loki endpoint for charm logging."""
        container = self._loki_container
        if container.can_connect() and container.get_service(self._name).is_running():
            scheme = "https" if self._charm_logging_ca_cert else "http"
            return [f"{scheme}://localhost:3100" + self._loki_push_api_endpoint]
        return []

    @property
    def _charm_logging_ca_cert(self) -> Optional[str]:
        """Server CA certificate path for TLS tracing."""
        if self._tls_available:
            return self._ca_cert_path
        return None

    @property
    def _tsdb_versions_migration_dates(self) -> List[Dict[str, str]]:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 4s</sub>

### ✅ `bash`

**Check ops-scenario in pyproject and lock**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -A2 '"ops-scenario"' pyproject.toml && grep "ops-scenario" uv.lock | head -5

```

<exited with exit code 1>
```


---

<sub>⏱️ 3m 4s</sub>

### ✅ `bash`

**Check ops-scenario package details**

$ pip show ops-scenario 2>/dev/null | head -10

<details>
<summary>11 lines</summary>

```
Name: ops-scenario
Version: 7.23.2
Summary: Python library providing a state-transition testing API for Operator Framework charms.
Home-page: 
Author: 
Author-email: Pietro Pasotti <pietro.pasotti@canonical.com>
License: Apache-2.0
Location: /home/ubuntu/.local/lib/python3.12/site-packages
Requires: ops, PyYAML
Required-by: pytest-interface-tester
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 10s</sub>

### ✅ `bash`

**Check ops-scenario in pyproject and lock file**

$ grep "ops-scenario\|scenario" pyproject.toml && echo "---" && cat uv.lock | grep -B2 -A5 'name = "ops-scenario"' | head -30

```

<exited with exit code 1>
```


---

<sub>⏱️ 3m 11s</sub>

### ✅ `bash`

**Check scenario package location and contents**

$ python3 -c "import scenario; print(scenario.__file__)" 2>/dev/null && python3 -c "import scenario; print(dir(scenario))" 2>/dev/null | tr ',' '\n' | grep -i "container\|exec\|relation\|state\|context" 2>/dev/null

<details>
<summary>14 lines</summary>

```
/home/ubuntu/.local/lib/python3.12/site-packages/scenario/__init__.py
 'Container'
 'Context'
 'Exec'
 'PeerRelation'
 'Relation'
 'RelationBase'
 'State'
 'StateValidationError'
 'StoredState'
 'SubordinateRelation'
 'context'
 'state']
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 16s</sub>

### ✅ `bash`

**Check scenario version**

$ python3 -c "import scenario; print(scenario.__version__)" 2>/dev/null && python3 -c "import scenario.state; print(scenario.state.__file__)"

```

<exited with exit code 1>
```


---

<sub>⏱️ 3m 15s</sub>

### ❌ `bash`

**Check if scenario is a wrapper for ops.testing**

$ cat /home/ubuntu/.local/lib/python3.12/site-packages/scenario/__init__.py | head -50

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 3m 22s</sub>

### ✅ `bash`

**Check scenario source location**

$ python3 -c "
import scenario
import inspect
print(inspect.getfile(scenario))
print(inspect.getfile(scenario.Container))
" 2>/dev/null

```
/home/ubuntu/.local/lib/python3.12/site-packages/scenario/__init__.py
/home/ubuntu/.local/lib/python3.12/site-packages/scenario/state.py
<exited with exit code 0>
```


---

<sub>⏱️ 3m 22s</sub>

### ✅ `bash`

**Check if scenario re-exports from ops.testing**

$ python3 -c "
import scenario
import ops.testing
# check if they are the same objects
print('scenario.Container is ops.testing.Container:', scenario.Container is ops.testing.Container)
print('scenario.Relation is ops.testing.Relation:', scenario.Relation is ops.testing.Relation)
print('scenario.State is ops.testing.State:', scenario.State is ops.testing.State)
" 2>/dev/null

```
scenario.Container is ops.testing.Container: True
scenario.Relation is ops.testing.Relation: True
scenario.State is ops.testing.State: True
<exited with exit code 0>
```


---

<sub>⏱️ 3m 44s</sub>

### ✅ `bash`

**Check tracing-related relations in charmcraft.yaml**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -A5 "charm-tracing\|workload-tracing\|receive-ca\|certificate" charmcraft.yaml | head -50

<details>
<summary>21 lines</summary>

```
certificates:
    interface: tls-certificates
    optional: true
    limit: 1
    description: Certificate and key files for the Loki server.
  catalogue:
    interface: catalogue
--
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 44s</sub>

### ✅ `bash`

**Read more charm.py**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && sed -n '400,500p' src/charm.py

<details>
<summary>88 lines</summary>

```
def _loki_command(self):
        """Construct command to launch Loki.

        Returns:
            a string consisting of Loki command and associated
            command line options.
        """
        return f"/usr/bin/loki -config.expand-env=true -config.file={LOKI_CONFIG}"

    @property
    def _loki_pebble_layer(self) -> Layer:
        """Construct the pebble layer.

        Returns:
            a Pebble layer specification for the Loki workload container.
        """
        env = {}
        if self.workload_tracing.is_ready():
            tempo_endpoint = self.workload_tracing.get_endpoint("jaeger_thrift_http")
            topology = self._juju_topology
            env.update(
                {
                    "JAEGER_ENDPOINT": (f"{tempo_endpoint}/api/traces?format=jaeger.thrift"),
                    "JAEGER_SAMPLER_PARAM": "1",
                    "JAEGER_SAMPLER_TYPE": "const",
                    "JAEGER_TAGS": f"juju_application={topology.application},juju_model={topology.model}"
                    + f",juju_model_uuid={topology.model_uuid},juju_unit={topology.unit},juju_charm={topology.charm_name}",
                },
            )

        pebble_layer = Layer(
            {
                "summary": "Loki layer",
                "description": "pebble config layer for Loki",
                "services": {
                    self._service_name: {
                        "override": "replace",
                        "summary": "loki",
                        "command": self._loki_command,
                        "startup": "disabled",
                        "environment": env,
                    },
                },
            }
        )

        return pebble_layer

    @property
    def _node_exporter_pebble_layer(self) -> Layer:
        """Construct the pebble layer.

        Returns:
            a Pebble layer specification for the Loki workload container.
        """
        pebble_layer = Layer(
            {
                "summary": "Node Exporter layer",
                "description": "pebble config layer for Node Exporter",
                "services": {
                    "node-exporter": {
                        "override": "replace",
                        "summary": "node exporter",
                        "command": f"/bin/node_exporter {self._node_exporter_args}",
                        "startup": "enabled",
                    },
                },
            }
        )

        return pebble_layer

    @property
    def _node_exporter_args(self) -> str:
        args = [
            "--collector.disable-defaults",
            "--collector.filesystem",
        ]

        return " ".join(args)

    @property
    def hostname(self) -> str:
        """Unit's hostname."""
        return socket.getfqdn()

    @property
    def internal_url(self):
        """Fqdn plus appropriate scheme and server port."""
        scheme = "https" if self._tls_available else "http"
        return f"{scheme}://{self.hostname}:{self._port}"

    @property
    def _external_url(self) -> str:
        """Return the external hostname to be passed to ingress via the relation."""
        if ingress_url := self.ingress_per_unit.url:
            logger.debug("This unit's ingress URL: %s", ingress_url)
            return ingress_url

        # If we do not have an ingress, then use the pod hostname.
        # The reason to prefer this over the pod name (which is the actual
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 50s</sub>

### ✅ `bash`

**Find CA cert usage in charm**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "_ca_cert_path\|_tls_available\|_update_cert\|ca_cert" src/charm.py | head -30

<details>
<summary>31 lines</summary>

```
90:    ca_cert: str
117:    server_cert="_charm_tracing_ca_cert",
127:@log_charm(logging_endpoints="_charm_logging_endpoints", server_cert="_charm_logging_ca_cert")
137:    _ca_cert_path = "/usr/local/share/ca-certificates/cos-ca.crt"
187:        self._update_cert()
204:            scheme=lambda: "https" if self._tls_available else "http",
236:            port=external_url.port or 443 if self._tls_available else 80,
250:        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
251:            self.charm_tracing, self._ca_cert_path
332:        self._update_cert()
489:        scheme = "https" if self._tls_available else "http"
522:        if self._tls_available:
544:    def _tls_available(self) -> bool:
590:        self._update_cert()
600:            http_tls=self._tls_available,
631:            scheme="https" if self._tls_available else "http", port=self._port
658:    def _update_cert(self):
663:        # We also need the resources_patch because the _update_cert method is called outside of the resource ready guard we have in the _configure method.
668:        ca_cert_path = Path(self._ca_cert_path)
683:                ca_cert_path,
684:                tls_config.ca_cert,
690:            ca_cert_path.parent.mkdir(exist_ok=True, parents=True)
691:            ca_cert_path.write_text(tls_config.ca_cert)
695:            self._loki_container.remove_path(ca_cert_path, recursive=True)
698:            ca_cert_path.unlink(missing_ok=True)
812:        scheme = "https" if self._tls_available else "http"
818:            cafile=self._ca_cert_path if Path(self._ca_cert_path).exists() else None,
888:            scheme = "https" if self._charm_logging_ca_cert else "http"
893:    def _charm_logging_ca_cert(self) -> Optional[str]:
895:        if self._tls_available:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 50s</sub>

### ✅ `bash`

**Find cert-related methods**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "def _update_cert\|def _tls_available\|def _ca_cert" src/charm.py

```
544:    def _tls_available(self) -> bool:
658:    def _update_cert(self):
<exited with exit code 0>
```


---

<sub>⏱️ 3m 54s</sub>

### ✅ `bash`

**Read TLS methods in charm**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && sed -n '544,700p' src/charm.py

<details>
<summary>135 lines</summary>

```
def _tls_available(self) -> bool:
        return bool(self._tls_config)

    ##############################################
    #             UTILITY METHODS                #
    ##############################################
    def _configure(self):  # noqa: C901
        """Configure Loki charm."""
        # "is_ready" is a racy check, so we do it once here (instead of in collect-status)
        if self.resources_patch.is_ready():
            self._stored.status["k8s_patch"] = to_tuple(ActiveStatus())
        else:
            if isinstance(to_status(self._stored.status["k8s_patch"]), ActiveStatus):
                self._stored.status["k8s_patch"] = to_tuple(
                    WaitingStatus("Waiting for resource limit patch to apply")
                )

            # Note: there could be a race between the resource patch and pebble operations (charm
            # code proceeds beyond a can_connect guard, and then lightkube patches the statefulset
            # and the workload is no longer available). After a statefulset patch we're guaranteed
            # to get at least upgrade-charm + config-changed + pebble-ready. Ideally, we'd like to
            # defer relation events before we "return".
            # Unfortunately, we can't do an isinstance check on an Event type, because relations
            # are managed by libs, and libs emit custom events.
            # So, returning early and relying on the holistic nature of the reconciler.
            return

        # "can_connect" is a racy check, so we do it once here (instead of in collect-status)
        if self._loki_container.can_connect():
            self._stored.status["config"] = to_tuple(ActiveStatus())

        # The config validity check does not return on error because if a lifecycle event
        # comes in after a config change, we still want Loki to continue to function even
        # with the invalid config.
        else:
            self._stored.status["config"] = to_tuple(MaintenanceStatus("Configuring Loki"))
            return

        if 0 > int(self.config["retention-period"]):
            self._stored.status["retention"] = to_tuple(
                BlockedStatus("Please provide a non-negative retention duration")
            )

        # We need to have the certs in place before rendering the config.
        # At this point we're already after the can_connect guard, so if the following pebble
        # operations fail, better to let the charm go into error state than setting blocked.
        self._update_cert()

        source_data = self._sorted_source_data()
        config = ConfigBuilder(
            instance_addr=self.hostname,
            alertmanager_url=self._alerting_config(),
            external_url=self._external_url,
            ingestion_rate_mb=int(self.config["ingestion-rate-mb"]),
            ingestion_burst_size_mb=int(self.config["ingestion-burst-size-mb"]),
            retention_period=int(self.config["retention-period"]),
            http_tls=self._tls_available,
            tsdb_versions_migration_dates=self._tsdb_versions_migration_dates,
            reporting_enabled=bool(self.config["reporting-enabled"]),
            grafana_external_url=source_data.external_url,
            datasource_uid=source_data.get_unit_uid(self.unit.name),
        ).build()

        # Add a layer so we can check if the service is running
        self._loki_container.add_layer(self._name, self._loki_pebble_layer, combine=True)

        if self._update_config(config):
            self._loki_container.restart(self._name)
            logger.info("Loki restarted. There was a change to the configuration.")

        # Now that we for sure have a layer, we can check if the service is running
        elif not self._loki_container.get_service(self._service_name).is_running():
            self._loki_container.restart(self._name)
            logger.info("Loki restarted. The service was not in the active state.")

        # trigger replan to notice if it was the pebble layer itself that changed
        self._loki_container.replan()

        if isinstance(to_status(self._stored.status["rules"]), BlockedStatus):
            # Wait briefly for Loki to come back up and re-check the alert rules
            # in case an upgrade/refresh caused the check to occur when it wasn't
            # ready yet. TODO: use custom pebble notice for "workload ready" event.
            time.sleep(2)
            self._check_alert_rules()
            return  # TODO: why do we have a return here?

        self.ingress_per_unit.provide_ingress_requirements(
            scheme="https" if self._tls_available else "http", port=self._port
        )
        self.metrics_provider.update_scrape_job_spec(self.scrape_jobs)
        self.grafana_source_provider.update_source(source_url=self._external_url)
        self.loki_provider.update_endpoint(url=self._external_url)
        self.catalogue.update_item(item=self._catalogue_item)

    def _sorted_source_data(self) -> GrafanaSourceData:
        """From the `grafana-source` relation, pick the first Grafana instance in the sorted list for consistency.

        Given multiple Grafana instances:
            1. The Loki ruler config can only accept 1 'external_url' and 'datasource_uid' to render the link in the Alertmanager UI
            2. Loki is the datasource so it doesn't matter which Grafana UI shows the query
        """
        nested_data = self.grafana_source_provider.get_source_data()
        return nested_data[sorted(nested_data)[0]] if nested_data else GrafanaSourceData({}, None)

    def _update_config(self, config: dict) -> bool:
        if self._running_config() != config:
            config_as_yaml = yaml.safe_dump(config)
            self._loki_container.push(LOKI_CONFIG, config_as_yaml, make_dirs=True)
            self._loki_container.push(LOKI_CONFIG_BACKUP, config_as_yaml, make_dirs=True)
            logger.info("Pushed new configuration")
            return True

        return False

    def _update_cert(self):
        # If Pebble is not ready, we do not proceed.
        # This code will end up running anyway when Pebble is ready, because
        # it will eventually be called from the `_configure()` method.

        # We also need the resources_patch because the _update_cert method is called outside of the resource ready guard we have in the _configure method.
        # Also see the comment about this inside the _configure method.
        if not self._loki_container.can_connect() or not self.resources_patch.is_ready():
            return

        ca_cert_path = Path(self._ca_cert_path)
        if tls_config := self._tls_config:
            # Save the workload certificates
            self._loki_container.push(
                CERT_FILE,
                tls_config.server_cert,
                make_dirs=True,
            )
            self._loki_container.push(
                KEY_FILE,
                tls_config.private_key,
                make_dirs=True,
            )
            # Save the CA among the trusted CAs and trust it
            self._loki_container.push(
                ca_cert_path,
                tls_config.ca_cert,
                make_dirs=True,
            )

            # Repeat for the charm container. We need it there for loki client requests.
            # (and charm tracing and logging TLS)
            ca_cert_path.parent.mkdir(exist_ok=True, parents=True)
            ca_cert_path.write_text(tls_config.ca_cert)
        else:
            self._loki_container.remove_path(CERT_FILE, recursive=True)
            self._loki_container.remove_path(KEY_FILE, recursive=True)
            self._loki_container.remove_path(ca_cert_path, recursive=True)

            # Repeat for the charm container.
            ca_cert_path.unlink(missing_ok=True)

        self._loki_container.exec(["update-ca-certificates", "--fresh"]).wait()
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 35s</sub>

### ✅ `bash`

**Check ops-tracing mock module**

$ python3 -c "import ops_tracing._mock; help(ops_tracing._mock)" 2>&1 | head -50

<details>
<summary>15 lines</summary>

```
Help on module ops_tracing._mock in ops_tracing:

NAME
    ops_tracing._mock - Mock implementations for testing.

FUNCTIONS
    patch_tracing() -> 'Generator[InMemorySpanExporter, None, None]'
        Patch ops[tracing] for unit tests.

        Replaces the real buffer and exporter with an in-memory store.
        This effectively removes the requirement for unique directories for each unit test.

DATA
    Generator = typing.Generator
        A generic version of collections.abc.Generator.

    SPAN_PROCESSOR = <opentelemetry.sdk.trace.export.SimpleSpanProcessor o...

FILE
    /home/ubuntu/.local/lib/python3.12/site-packages/ops_tracing/_mock.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 35s</sub>

### ✅ `bash`

**Check charm_tracing_disabled usage in tests**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "charm_tracing_disabled\|BUFFER_DEFAULT_CACHE" tests/unit/conftest.py

```
5:from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
19:        "charms.tempo_coordinator_k8s.v0.charm_tracing.BUFFER_DEFAULT_CACHE_FILE_NAME",
35:                with charm_tracing_disabled():
<exited with exit code 0>
```


---

<sub>⏱️ 4m 41s</sub>

### ✅ `bash`

**Read patch_tracing source**

$ python3 -c "
import ops_tracing._mock as m
import inspect
print(inspect.getsource(m.patch_tracing))
" 2>/dev/null

<details>
<summary>26 lines</summary>

```
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 41s</sub>

### ✅ `bash`

**Read full conftest.py**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && cat tests/unit/conftest.py

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

<sub>⏱️ 4m 48s</sub>

### ✅ `bash`

**Find all scenario imports in unit tests**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "from scenario import\|import scenario" tests/unit/*.py

```
tests/unit/conftest.py:7:from scenario import Container, Exec
tests/unit/test_datasource_exchange.py:12:from scenario import Relation, State
tests/unit/test_grafana_source.py:7:from scenario import Relation, State
<exited with exit code 0>
```


---

<sub>⏱️ 4m 48s</sub>

### ✅ `bash`

**Read test files using scenario imports**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && cat tests/unit/test_datasource_exchange.py | head -30 && echo "---" && head -20 tests/unit/test_grafana_source.py

<details>
<summary>41 lines</summary>

```
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import json

import pytest
from cosl.interfaces.datasource_exchange import (
    DatasourceExchange,
    DSExchangeAppData,
    GrafanaDatasource,
)
from scenario import Relation, State

from src.charm import LokiOperatorCharm

ds_tempo = [
    {"type": "tempo", "uid": "3", "grafana_uid": "4"},
]

ds_mimir = [
    {"type": "prometheus", "uid": "8", "grafana_uid": "9"},
]

mimir_dsx = Relation(
    "send-datasource",
    remote_app_data=dict(DSExchangeAppData(datasources=json.dumps(ds_mimir)).dump()),
)
tempo_dsx = Relation(
    "send-datasource",
    remote_app_data=dict(DSExchangeAppData(datasources=json.dumps(ds_tempo)).dump()),
---
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import json

from charms.grafana_k8s.v0.grafana_source import GrafanaSourceData
from scenario import Relation, State

from src.charm import LokiOperatorCharm


def test_sorted_source_data(context, loki_container):
    # GIVEN multiple "grafana-source" relations
    rel_1 = Relation(
        "grafana-source",
        remote_app_name="grafana_one",
        remote_app_data={
            "grafana_uid": "1",
            "datasource_uids": json.dumps({"loki/0": "first"}),
            "grafana_base_url": "http://one",
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 1s</sub>

### 💬 Copilot

Now I have a thorough understanding. Let me create the plan and execute the changes:

---

<sub>⏱️ 5m 1s</sub>

### ✅ `sql`

**Create todos for upgrade tasks**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create todos for upgrade tasks",
  "query": "INSERT INTO todos (id, title, description, status) VALUES\n('create-branch', 'Create upgrade branch', 'Create git branch ops-upgrade for the changes', 'pending'),\n('update-pyproject', 'Update pyproject.toml', 'Bump ops to ops[tracing]>=3.6.0, remove opentelemetry deps (now bundled in ops-tracing), update requires-python to >=3.10. Also update dev deps to remove scenario and ops-tracing separately.', 'pending'),\n('update-charm-tracing', 'Migrate charm tracing to ops.tracing', 'Replace @trace_charm decorator + TracingEndpointRequirer(charm-tracing) + charm_tracing_config with ops.tracing.Tracing(self, tracing_relation_name=\"charm-tracing\"). Keep workload_tracing TracingEndpointRequirer as-is (it serves a different purpose). Remove _charm_tracing_endpoint and _charm_tracing_ca_cert init assignments.', 'pending'),\n('update-test-imports', 'Update scenario imports to ops.testing', 'Replace `from scenario import Container, Exec` and `from scenario import Relation, State` with `from ops.testing import ...` in conftest.py, test_datasource_exchange.py, test_grafana_source.py. Also update conftest.py to replace charm_tracing_disabled with ops_tracing.patch_tracing() and remove BUFFER_DEFAULT_CACHE_FILE_NAME patch.', 'pending'),\n('update-lock', 'Update uv.lock', 'Run uv lock to update the lock file with new versions', 'pending'),\n('run-tests', 'Run tests to verify', 'Run tox -e lint,unit to verify everything works', 'pending');\n\nINSERT INTO todo_deps (todo_id, depends_on) VALUES\n('update-pyproject', 'create-branch'),\n('update-charm-tracing', 'create-branch'),\n('update-test-imports', 'create-branch'),\n('update-lock', 'update-pyproject'),\n('run-tests', 'update-charm-tracing'),\n('run-tests', 'update-test-imports'),\n('run-tests', 'update-lock');"
}
```

</details>

<details>
<summary>5 lines</summary>

```
Executed 2 statement(s):

1. INSERT
   6 row(s) inserted. Last inserted row ID: 6.

2. INSERT
   7 row(s) inserted. Last inserted row ID: 7.
```

</details>


---

<sub>⏱️ 5m 6s</sub>

### ✅ `bash`

**Create upgrade branch**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && git checkout -b ops-upgrade && git status

```
Switched to a new branch 'ops-upgrade'
On branch ops-upgrade
nothing to commit, working tree clean
<exited with exit code 0>
```


---

<sub>⏱️ 5m 10s</sub>

### ✅ `sql`

**Mark create-branch done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark create-branch done",
  "query": "UPDATE todos SET status = 'done' WHERE id = 'create-branch';"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 5m 15s</sub>

### 💬 Copilot

Now let me look at the pyproject.toml and the opentelemetry deps more carefully:

---

<sub>⏱️ 5m 15s</sub>

### ✅ `bash`

**Read full pyproject.toml**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && cat pyproject.toml

<details>
<summary>87 lines</summary>

```
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
[project]
name = "loki-k8s"
version = "0.0"
requires-python = "~=3.8"

dependencies = [
  "ops",
  "cosl",
  "kubernetes",
  "requests",
  "pyyaml",
  "lightkube",
  "lightkube-models",
  "aiohttp!=3.11.13",  # Yanked
  "jsonschema",
  "cryptography",
  "pydantic>=2.9.0",
  "importlib-metadata==6.0.0",
  "opentelemetry-api==1.21.0",
  "opentelemetry-exporter-otlp-proto-common==1.21.0",
  "opentelemetry-exporter-otlp-proto-http==1.21.0",
  "opentelemetry-proto==1.21.0",
  "opentelemetry-sdk==1.21.0",
  "opentelemetry-semantic-conventions==0.42b0",
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
  "ops[testing]",
  "responses",
  "fs",
  # Interface
  "pytest-interface-tester",
  # Integration
  "juju",
  "pytest-operator",
  "minio",
  "sh",
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
lint.select = ["E", "W", "F", "C", "N", "R", "D", "I001"]
# Ignore E501 because using black creates errors with this
# Ignore D107 Missing docstring in __init__
lint.ignore = ["E501", "D107", "RET504"]
# D100, D101, D102, D103: Ignore missing docstrings in tests
lint.per-file-ignores = {"tests/*" = ["D100","D101","D102","D103"]}
lint.pydocstyle.convention = "google"

# Static analysis tools configuration
[tool.pyright]
extraPaths = ["lib"]
pythonVersion = "3.8"
pythonPlatform = "All"
exclude = [
  "tests/integration/loki-tester/**",
  "tests/integration/log-proxy-tester/**",
  "tests/integration/log-forwarder-tester/**"
]

[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"
asyncio_mode = "auto"
addopts = "--tb=native --verbose --capture=no --log-cli-level=INFO"
markers = ["setup", "work", "teardown"]

[tool.codespell]
skip = ".git,.tox,build,venv*"
ignore-words-list = "assertIn"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 22s</sub>

### ✅ `bash`

**Check ops-tracing dependencies**

$ pip show ops-tracing 2>/dev/null | head -10 && python3 -c "
import ops_tracing.vendor as v
import os
print([d for d in dir(v) if not d.startswith('_')])
" 2>/dev/null

<details>
<summary>12 lines</summary>

```
Name: ops-tracing
Version: 2.23.2
Summary: The tracing facility for the Ops library.
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
Author-email: 
License: 
Location: /home/ubuntu/.local/lib/python3.12/site-packages
Requires: opentelemetry-sdk, ops, pydantic
Required-by: 
['charms', 'otlp_json']
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 22s</sub>

### ✅ `bash`

**Check ops-tracing requirements**

$ pip show ops-tracing 2>/dev/null | grep Requires

```
Requires: opentelemetry-sdk, ops, pydantic
<exited with exit code 0>
```


---

<sub>⏱️ 5m 31s</sub>

### ✅ `bash`

**Check opentelemetry usage in charm libs**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "opentelemetry" lib/charms/loki_k8s/v0/charm_logging.py | head -10 && grep -n "opentelemetry" lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py | head -10

<details>
<summary>11 lines</summary>

```
5:"""This charm library contains utilities to instrument your Charm with opentelemetry tracing data collection.
114:import opentelemetry
116:def get_tracer(self) -> opentelemetry.trace.Tracer:
117:    return opentelemetry.trace.get_tracer(type(self).__name__)
123:See the official opentelemetry Python SDK documentation for usage:
124:https://opentelemetry-python.readthedocs.io/en/latest/
183:(or, if your project had a dependency on `opentelemetry-exporter-otlp-proto-grpc` only because
186:`opentelemetry-exporter-otlp-proto-http>=1.21.0`.
238:    """Hack to remove stale opentelemetry sdk packages from the charm's python venv.
262:    # group by name all distributions starting with "opentelemetry_"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 36s</sub>

### ✅ `bash`

**Check charm_logging imports**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "^import\|^from" lib/charms/loki_k8s/v0/charm_logging.py | head -30

<details>
<summary>11 lines</summary>

```
72:import functools
73:import logging
74:import os
75:from contextlib import contextmanager
76:from pathlib import Path
77:from typing import (
86:from cosl import JujuTopology
87:from cosl.loki_logger import LokiHandler  # pyright:ignore[reportMissingImports]
88:from ops.charm import CharmBase
89:from ops.framework import Framework
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 36s</sub>

### ✅ `bash`

**Check charm_tracing imports**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "^import\|^from" lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py | head -30

<details>
<summary>28 lines</summary>

```
22:from charms.tempo_coordinator_k8s.v0.tracing import (
26:from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing
92:from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
114:import opentelemetry
294:import functools
295:import inspect
296:import logging
297:import os
298:import typing
299:from collections import deque
300:from contextlib import contextmanager
301:from contextvars import Context, ContextVar, copy_context
302:from pathlib import Path
303:from typing import (
316:import opentelemetry
317:import ops
318:from opentelemetry.exporter.otlp.proto.common._internal.trace_encoder import (  # type: ignore
321:from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # type: ignore
322:from opentelemetry.sdk.resources import Resource
323:from opentelemetry.sdk.trace import ReadableSpan, Span, TracerProvider
324:from opentelemetry.sdk.trace.export import (
329:from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
330:from opentelemetry.trace import (
334:from opentelemetry.trace import get_current_span as otlp_get_current_span
335:from opentelemetry.trace import (
341:from ops.charm import CharmBase
342:from ops.framework import Framework
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 0s</sub>

### ✅ `bash`

**Check ops extras**

$ pip show ops 2>/dev/null | grep "Requires\|Version" && echo "---" && python3 -c "
import importlib.metadata as m
# Check extras for ops
dist = m.distribution('ops')
# Find extras
extras = dist.metadata.get_all('Provides-Extra', [])
print('Extras:', extras)
req = [r for r in dist.metadata.get_all('Requires-Dist', []) or [] if 'tracing' in r.lower()]
print('Tracing deps:', req)
" 2>/dev/null

<details>
<summary>6 lines</summary>

```
Version: 2.23.2
Requires: importlib-metadata, opentelemetry-api, PyYAML, websocket-client
---
Extras: ['testing', 'tracing', 'harness']
Tracing deps: ['ops-tracing==2.23.2; extra == "tracing"']
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 36s</sub>

### 💬 Copilot

Now I'll implement all changes. Let me start with all the modifications in parallel:

---

<sub>⏱️ 6m 36s</sub>

### ✅ `sql`

**Mark tasks in progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark tasks in progress",
  "query": "UPDATE todos SET status = 'in_progress' WHERE id IN ('update-pyproject', 'update-charm-tracing', 'update-test-imports');"
}
```

</details>

```
3 row(s) updated.
```


---

<sub>⏱️ 6m 46s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 6m 46s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 6m 46s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 6m 51s</sub>

### 💬 Copilot

Now update `src/charm.py` - remove the `@trace_charm` decorator and related code, replace with `ops.tracing.Tracing`:

---

<sub>⏱️ 6m 51s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 6m 56s</sub>

### ✅ `bash`

**Check imports area**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && sed -n '50,65p' src/charm.py

<details>
<summary>17 lines</summary>

```
TLSCertificatesRequiresV4,
)
from charms.traefik_k8s.v1.ingress_per_unit import IngressPerUnitRequirer
from cosl import JujuTopology
from cosl.interfaces.datasource_exchange import DatasourceDict, DatasourceExchange
from ops import CollectStatusEvent, StoredState
from ops.charm import CharmBase
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
    MaintenanceStatus,
    Port,
    StatusBase,
    WaitingStatus,
)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 1s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 5s</sub>

### 💬 Copilot

Now remove the `@trace_charm` decorator:

---

<sub>⏱️ 7m 6s</sub>

### ✅ `bash`

**View the decorator area**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && sed -n '112,130p' src/charm.py

<details>
<summary>17 lines</summary>

```
return StatusBase.from_name(name, message)


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
@log_charm(logging_endpoints="_charm_logging_endpoints", server_cert="_charm_logging_ca_cert")
class LokiOperatorCharm(CharmBase):
    """Charm the service."""
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 11s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 16s</sub>

### 💬 Copilot

Now replace the charm_tracing `TracingEndpointRequirer` and `charm_tracing_config` in `__init__`:

---

<sub>⏱️ 7m 16s</sub>

### ✅ `bash`

**View the tracing setup in __init__**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && sed -n '235,260p' src/charm.py

<details>
<summary>24 lines</summary>

```
self.workload_tracing = TracingEndpointRequirer(
            self, relation_name="workload-tracing", protocols=["jaeger_thrift_http"]
        )
        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
            self.charm_tracing, self._ca_cert_path
        )

        self.datasource_exchange = DatasourceExchange(
            self,
            provider_endpoint="send-datasource",
            requirer_endpoint=None,
        )

        self.framework.observe(
            self.workload_tracing.on.endpoint_changed,  # type: ignore
            self._on_workload_tracing_endpoint_changed,
        )
        self.framework.observe(
            self.workload_tracing.on.endpoint_removed,  # type: ignore
            self._on_workload_tracing_endpoint_removed,
        )

        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
        self.framework.observe(self.on.loki_pebble_ready, self._on_loki_pebble_ready)
        self.framework.observe(
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 21s</sub>

### ✅ `bash`

**View charm_tracing definition**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && sed -n '228,242p' src/charm.py

<details>
<summary>13 lines</summary>

```
self.dashboard_provider = GrafanaDashboardProvider(self)

        self.catalogue = CatalogueConsumer(charm=self, item=self._catalogue_item)
        self.charm_tracing = TracingEndpointRequirer(
            self, relation_name="charm-tracing", protocols=["otlp_http"]
        )
        self.workload_tracing = TracingEndpointRequirer(
            self, relation_name="workload-tracing", protocols=["jaeger_thrift_http"]
        )
        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
            self.charm_tracing, self._ca_cert_path
        )

        self.datasource_exchange = DatasourceExchange(
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 27s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 37s</sub>

### 💬 Copilot

Now update the test files:

---

<sub>⏱️ 7m 37s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py updated with changes.
```


---

<sub>⏱️ 7m 43s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py updated with changes.
```


---

<sub>⏱️ 7m 50s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py updated with changes.
```


---

<sub>⏱️ 7m 56s</sub>

### 💬 Copilot

Now update the scenario imports in other test files:

---

<sub>⏱️ 7m 56s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/test_datasource_exchange.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/test_datasource_exchange.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/test_datasource_exchange.py updated with changes.
```


---

<sub>⏱️ 7m 56s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/test_grafana_source.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/test_grafana_source.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/test_grafana_source.py updated with changes.
```


---

<sub>⏱️ 8m 0s</sub>

### 💬 Copilot

Now update the uv.lock:

---

<sub>⏱️ 8m 0s</sub>

### ✅ `sql`

**Mark lock update in progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark lock update in progress",
  "query": "UPDATE todos SET status = 'in_progress' WHERE id = 'update-lock';"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 8m 6s</sub>

### ✅ `bash`

**Update uv.lock**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && uv lock 2>&1

<details>
<summary>41 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠙ loki-k8s==0.0                                                                                                         ⠙ loki-k8s==0.0                                                                                                         ⠙ aiohttp==3.11.18                                                                                                      ⠙ cosl==1.3.1                                                                                                           ⠙ cryptography==44.0.3                                                                                                  ⠙ jsonschema==4.23.0                                                                                                    ⠙ kubernetes==32.0.1                                                                                                    ⠙ lightkube==0.17.1                                                                                                     ⠙ lightkube-models==1.32.0.8                                                                                            ⠙ ops==2.21.1                                                                                                           ⠙ ops==2.21.1                                                                                                           ⠙ ops-tracing==2.21.1                                                                                                   ⠙ ops==2.21.1                                                                                                           ⠙ ops-scenario==7.21.1                                                                                                  ⠙ pydantic==2.11.4                                                                                                      ⠙ pydantic-core==2.33.2                                                                                                 ⠙ pyyaml==6.0.2                                                                                                         ⠙ requests==2.32.3                                                                                                      Resolved 117 packages in 24ms
Updated aiohappyeyeballs v2.4.4, v2.6.1 -> v2.6.1
Updated aiohttp v3.10.11, v3.11.18 -> v3.11.18
Updated aiosignal v1.3.1, v1.3.2 -> v1.3.2
Updated anyio v4.5.2, v4.9.0 -> v4.9.0
Removed appnope v0.1.4
Removed backcall v0.2.0
Removed backoff v2.2.1
Updated coverage v7.6.1, v7.8.0 -> v7.8.0
Removed deprecated v1.2.18
Updated frozenlist v1.5.0, v1.6.0 -> v1.6.0
Removed googleapis-common-protos v1.70.0
Removed importlib-resources v6.4.5
Updated ipython v8.12.3, v8.18.1, v8.36.0, v9.2.0 -> v8.36.0, v9.2.0
Updated jsonschema-specifications v2023.12.1, v2025.4.1 -> v2025.4.1
Updated markupsafe v2.1.5, v3.0.2 -> v3.0.2
Updated minio v7.2.7, v7.2.10, v7.2.15 -> v7.2.15
Updated multidict v6.1.0, v6.4.3 -> v6.4.3
Updated opentelemetry-api v1.21.0 -> v1.40.0
Removed opentelemetry-exporter-otlp-proto-common v1.21.0
Removed opentelemetry-exporter-otlp-proto-http v1.21.0
Removed opentelemetry-proto v1.21.0
Updated opentelemetry-sdk v1.21.0 -> v1.40.0
Updated opentelemetry-semantic-conventions v0.42b0 -> v0.61b0
Added ops-tracing v2.21.1
Removed pickleshare v0.7.5
Removed pkgutil-resolve-name v1.3.10
Updated propcache v0.2.0, v0.3.1 -> v0.3.1
Updated pydantic v2.10.6, v2.11.4 -> v2.11.4
Updated pydantic-core v2.27.2, v2.33.2 -> v2.33.2
Updated referencing v0.35.1, v0.36.2 -> v0.36.2
Updated rpds-py v0.20.1, v0.24.0 -> v0.24.0
Updated setuptools v75.3.2, v80.3.1 -> v80.3.1
Updated sh v1.14.3, v2.2.2 -> v2.2.2
Updated tenacity v9.0.0, v9.1.2 -> v9.1.2
Updated urllib3 v2.2.3, v2.4.0 -> v2.4.0
Removed wrapt v1.17.2
Updated yarl v1.15.2, v1.20.0 -> v1.20.0
Updated zipp v3.20.2, v3.21.0 -> v3.21.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 17s</sub>

### 💬 Copilot

The lock resolved to an older ops version. We need to pin a minimum version:

---

<sub>⏱️ 8m 17s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 8m 23s</sub>

### ✅ `bash`

**Re-resolve with new ops constraint**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && uv lock 2>&1 | tail -30

<details>
<summary>6 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Resolved 117 packages in 27ms
Updated ops v2.21.1 -> v3.6.0
Updated ops-scenario v7.21.1 -> v8.6.0
Updated ops-tracing v2.21.1 -> v3.6.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 28s</sub>

### 💬 Copilot

Now ops 3.6.0 is properly locked. Let me run the tests:

---

<sub>⏱️ 8m 28s</sub>

### ✅ `sql`

**Mark tasks done and run-tests in progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark tasks done and run-tests in progress",
  "query": "UPDATE todos SET status = 'done' WHERE id IN ('update-pyproject', 'update-charm-tracing', 'update-test-imports', 'update-lock');\nUPDATE todos SET status = 'in_progress' WHERE id = 'run-tests';"
}
```

</details>

<details>
<summary>5 lines</summary>

```
Executed 2 statement(s):

1. UPDATE
   4 row(s) updated.

2. UPDATE
   1 row(s) updated.
```

</details>


---

<sub>⏱️ 8m 34s</sub>

### ✅ `bash`

**Run lint checks**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev ruff check src/ tests/unit/ lib/charms/loki_k8s/ 2>&1 | head -40

<details>
<summary>41 lines</summary>

```
Installed 111 packages in 50ms
src/charm.py:15:1: I001 [*] Import block is un-sorted or un-formatted
   |
13 |   """
14 |
15 | / import datetime
16 | | import logging
17 | | import os
18 | | import re
19 | | import socket
20 | | import ssl
21 | | import subprocess
22 | | import time
23 | | import urllib.request
24 | | from dataclasses import dataclass
25 | | from pathlib import Path
26 | | from typing import Any, Dict, List, Optional, Tuple, TypedDict, cast
27 | | from urllib.error import HTTPError, URLError
28 | | from urllib.parse import urlparse
29 | |
30 | | import yaml
31 | | from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerConsumer
32 | | from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
33 | | from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
34 | | from charms.grafana_k8s.v0.grafana_source import GrafanaSourceData, GrafanaSourceProvider
35 | | from charms.loki_k8s.v0.charm_logging import log_charm
36 | | from charms.loki_k8s.v1.loki_push_api import (
37 | |     LokiPushApiAlertRulesChanged,
38 | |     LokiPushApiProvider,
39 | | )
40 | | from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
41 | |     K8sResourcePatchFailedEvent,
42 | |     KubernetesComputeResourcesPatch,
43 | |     ResourceRequirements,
44 | |     adjust_resource_requirements,
45 | | )
46 | | from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
47 | | from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer
48 | | from charms.tls_certificates_interface.v4.tls_certificates import (
49 | |     CertificateRequestAttributes,
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 44s</sub>

### ✅ `bash`

**Auto-fix import sorting in charm.py**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev ruff check --fix-only src/charm.py 2>&1

```
░░░░░░░░░░░░░░░░░░░░ [0/0] Installing wheels...                                                                         ░░░░░░░░░░░░░░░░░░░░ [0/111] Installing wheels...                                                                       ░░░░░░░░░░░░░░░░░░░░ [0/111] multidict==6.4.3                                                                           ░░░░░░░░░░░░░░░░░░░░ [1/111] multidict==6.4.3                                                                           ░░░░░░░░░░░░░░░░░░░░ [1/111] pluggy==1.5.0                                                                              ░░░░░░░░░░░░░░░░░░░░ [2/111] pluggy==1.5.0                                                                              ░░░░░░░░░░░░░░░░░░░░ [2/111] pymacaroons==0.13.0                                                                        ░░░░░░░░░░░░░░░░░░░░ [3/111] pymacaroons==0.13.0                                                                        ░░░░░░░░░░░░░░░░░░░░ [3/111] fs==2.4.16                                                                                 ░░░░░░░░░░░░░░░░░░░░ [4/111] fs==2.4.16                                                                                 ░░░░░░░░░░░░░░░░░░░░ [4/111] typer==0.7.0                                                                               ░░░░░░░░░░░░░░░░░░░░ [5/111] typer==0.7.0                                                                               ░░░░░░░░░░░░░░░░░░░░ [5/111] requests-oauthlib==2.0.0                                                                   █░░░░░░░░░░░░░░░░░░░ [6/111] requests-oauthlib==2.0.0                                                                   █░░░░░░░░░░░░░░░░░░░ [6/111] aiohttp==3.11.18                                                                           █░░░░░░░░░░░░░░░░░░░ [7/111] aiohttp==3.11.18                                                                           █░░░░░░░░░░░░░░░░░░░ [7/111] cosl==1.3.1                                                                                █░░░░░░░░░░░░░░░░░░░ [8/111] cosl==1.3.1                                                                                █░░░░░░░░░░░░░░░░░░░ [8/111] referencing==0.36.2                                                                        █░░░░░░░░░░░░░░░░░░░ [9/111] referencing==0.36.2                                                                        ███████████████████░ [110/111] pyright==1.1.398                                                                         Installed 111 packages in 63ms
Fixed 1 error.
<exited with exit code 0>
```


---

<sub>⏱️ 8m 49s</sub>

### ✅ `bash`

**Check lint again**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev ruff check src/ tests/unit/ lib/charms/loki_k8s/ 2>&1 | head -20

```
Installed 111 packages in 45ms
All checks passed!
<exited with exit code 0>
```


---

<sub>⏱️ 8m 54s</sub>

### 💬 Copilot

Now run unit tests:

---

<sub>⏱️ 9m 0s</sub>

### ✅ `bash`

**Ensure cos-tool is available**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && stat cos-tool-amd64 > /dev/null 2>&1 || curl -L -O -s https://github.com/canonical/cos-tool/releases/latest/download/cos-tool-amd64 && chmod 755 cos-tool-amd64 && echo "cos-tool ready"

```
cos-tool ready
<exited with exit code 0>
```


---

<sub>⏱️ 9m 8s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev pytest tests/unit/ -x --tb=short 2>&1 | tail -50

<details>
<summary>6 lines</summary>

```
Installed 111 packages in 48ms
ImportError while loading conftest '/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py'.
tests/unit/conftest.py:8: in <module>
    from charm import LokiOperatorCharm
E   ModuleNotFoundError: No module named 'charm'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 16s</sub>

### ✅ `bash`

**Run unit tests with PYTHONPATH**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && PYTHONPATH=.:lib:src uv run --frozen --isolated --extra=dev pytest tests/unit/ -x --tb=short 2>&1 | tail -60

<details>
<summary>8 lines</summary>

```
Installed 111 packages in 51ms
ImportError while loading conftest '/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py'.
tests/unit/conftest.py:8: in <module>
    from charm import LokiOperatorCharm
src/charm.py:30: in <module>
    import ops.tracing
E   ModuleNotFoundError: No module named 'ops.tracing'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 26s</sub>

### ✅ `bash`

**Check which ops version is being used**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && PYTHONPATH=.:lib:src uv run --frozen --isolated --extra=dev python3 -c "import ops; print(ops.__version__); import ops_tracing; print(ops_tracing.__version__)" 2>&1

<details>
<summary>6 lines</summary>

```
░░░░░░░░░░░░░░░░░░░░ [0/0] Installing wheels...                                                                         ░░░░░░░░░░░░░░░░░░░░ [0/111] Installing wheels...                                                                       ░░░░░░░░░░░░░░░░░░░░ [0/111] referencing==0.36.2                                                                        ░░░░░░░░░░░░░░░░░░░░ [1/111] referencing==0.36.2                                                                        ░░░░░░░░░░░░░░░░░░░░ [1/111] multidict==6.4.3                                                                           ░░░░░░░░░░░░░░░░░░░░ [2/111] multidict==6.4.3                                                                           ░░░░░░░░░░░░░░░░░░░░ [2/111] pymacaroons==0.13.0                                                                        ░░░░░░░░░░░░░░░░░░░░ [3/111] pymacaroons==0.13.0                                                                        ░░░░░░░░░░░░░░░░░░░░ [3/111] requests-oauthlib==2.0.0                                                                   ░░░░░░░░░░░░░░░░░░░░ [4/111] ipython-pygments-lexers==1.1.1                                                             ░░░░░░░░░░░░░░░░░░░░ [5/111] ipython-pygments-lexers==1.1.1                                                             ░░░░░░░░░░░░░░░░░░░░ [5/111] ipython-pygments-lexers==1.1.1                                                             ░░░░░░░░░░░░░░░░░░░░ [5/111] tenacity==9.1.2                                                                            █░░░░░░░░░░░░░░░░░░░ [6/111] pluggy==1.5.0                                                                              █░░░░░░░░░░░░░░░░░░░ [7/111] pluggy==1.5.0                                                                              █░░░░░░░░░░░░░░░░░░░ [7/111] pluggy==1.5.0                                                                              █░░░░░░░░░░░░░░░░░░░ [7/111] annotated-types==0.7.0                                                                     █░░░░░░░░░░░░░░░░░░░ [8/111] annotated-types==0.7.0                                                                     █░░░░░░░░░░░░░░░░░░░ [8/111] aiohttp==3.11.18                                                                           █░░░░░░░░░░░░░░░░░░░ [9/111] aiohttp==3.11.18                                                                           ███████████████████░ [110/111] pyright==1.1.398                                                                         Installed 111 packages in 51ms
3.6.0
Traceback (most recent call last):
  File "<string>", line 1, in <module>
AttributeError: module 'ops_tracing' has no attribute '__version__'
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 9m 33s</sub>

### ✅ `bash`

**Check ops.tracing availability**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && PYTHONPATH=.:lib:src uv run --frozen --isolated --extra=dev python3 -c "import ops; print(dir(ops))" 2>&1 | tail -5 && uv run --frozen --isolated --extra=dev python3 -c "import ops.tracing; print(ops.tracing)" 2>&1 | tail -5

<details>
<summary>7 lines</summary>

```
Installed 111 packages in 47ms
['ActionEvent', 'ActionMeta', 'ActiveStatus', 'Application', 'Binding', 'BindingMapping', 'BlockedStatus', 'BoundEvent', 'BoundStoredState', 'CharmBase', 'CharmEvents', 'CharmMeta', 'CheckInfoMapping', 'CloudCredential', 'CloudSpec', 'CollectMetricsEvent', 'CollectStatusEvent', 'CommitEvent', 'ConfigChangedEvent', 'ConfigData', 'ConfigMeta', 'Container', 'ContainerBase', 'ContainerMapping', 'ContainerMeta', 'ContainerStorageMeta', 'ErrorStatus', 'EventBase', 'EventSource', 'Framework', 'FrameworkEvents', 'Handle', 'HandleKind', 'HookEvent', 'InstallEvent', 'InvalidStatusError', 'JujuAssumes', 'JujuAssumesCondition', 'JujuContext', 'JujuVersion', 'LazyCheckInfo', 'LazyMapping', 'LazyNotice', 'LeaderElectedEvent', 'LeaderSettingsChangedEvent', 'LifecycleEvent', 'MaintenanceStatus', 'MetadataLinks', 'Model', 'ModelError', 'MultiPushPullError', 'Network', 'NetworkInterface', 'NoTypeError', 'Object', 'ObjectEvents', 'OpenedPort', 'PayloadMeta', 'PebbleCheckEvent', 'PebbleCheckFailedEvent', 'PebbleCheckRecoveredEvent', 'PebbleCustomNoticeEvent', 'PebbleNoticeEvent', 'PebbleReadyEvent', 'Pod', 'Port', 'PostSeriesUpgradeEvent', 'PreCommitEvent', 'PreSeriesUpgradeEvent', 'PrefixedEvents', 'Relation', 'RelationBrokenEvent', 'RelationChangedEvent', 'RelationCreatedEvent', 'RelationData', 'RelationDataAccessError', 'RelationDataContent', 'RelationDataError', 'RelationDataTypeError', 'RelationDepartedEvent', 'RelationEvent', 'RelationJoinedEvent', 'RelationMapping', 'RelationMeta', 'RelationNotFoundError', 'RelationRole', 'RemoteModel', 'RemoveEvent', 'ResourceMeta', 'Resources', 'Secret', 'SecretChangedEvent', 'SecretEvent', 'SecretExpiredEvent', 'SecretInfo', 'SecretNotFoundError', 'SecretRemoveEvent', 'SecretRotate', 'SecretRotateEvent', 'Serializable', 'ServiceInfoMapping', 'StartEvent', 'StatusBase', 'StatusName', 'StopEvent', 'Storage', 'StorageAttachedEvent', 'StorageDetachingEvent', 'StorageEvent', 'StorageMapping', 'StorageMeta', 'StoredDict', 'StoredList', 'StoredSet', 'StoredState', 'StoredStateData', 'TooManyRelatedAppsError', 'Unit', 'UnknownStatus', 'UpdateStatusEvent', 'UpgradeCharmEvent', 'WaitingStatus', 'WorkloadEvent', '_Main', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '__version__', '_legacy_main', '_main', '_private', 'annotations', 'charm', 'framework', 'hookcmds', 'jujucontext', 'jujuversion', 'log', 'main', 'model', 'pebble', 'storage', 'tracing', 'version']
Installed 111 packages in 45ms
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'ops.tracing'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 40s</sub>

### ✅ `bash`

**Check ops.tracing type**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && PYTHONPATH=.:lib:src uv run --frozen --isolated --extra=dev python3 -c "
import ops
t = ops.tracing
print(type(t))
print(t)
" 2>&1 | tail -5

```
Installed 111 packages in 47ms
<class 'module'>
<module 'ops_tracing' from '/home/ubuntu/.cache/uv/builds-v0/.tmp9avR6o/lib/python3.12/site-packages/ops_tracing/__init__.py'>
<exited with exit code 0>
```


---

<sub>⏱️ 9m 49s</sub>

### 💬 Copilot

`ops.tracing` is set as an attribute on the `ops` module, not a real subpackage. I need to access it via `ops.tracing` after `import ops`:

---

<sub>⏱️ 9m 49s</sub>

### ✅ `bash`

**Check ops imports in charm**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "import ops" src/charm.py | head -10

```
30:import ops.tracing
<exited with exit code 0>
```


---

<sub>⏱️ 9m 54s</sub>

### ✅ `bash`

**Check ops-related imports**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "^from ops\|^import ops" src/charm.py | head -15

<details>
<summary>7 lines</summary>

```
30:import ops.tracing
56:from ops import CollectStatusEvent, StoredState
57:from ops.charm import CharmBase
58:from ops.main import main
59:from ops.model import (
67:from ops.pebble import Error, Layer, PathError, ProtocolError
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 59s</sub>

### ❌ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py

```
No match found
```


---

<sub>⏱️ 10m 4s</sub>

### ✅ `bash`

**See exact context around the import**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && sed -n '28,32p' src/charm.py

<details>
<summary>5 lines</summary>

```
from urllib.parse import urlparse

import ops.tracing
import yaml
from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerConsumer
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 9s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 10m 14s</sub>

### ✅ `bash`

**Check ops imports again**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && grep -n "^from ops\|^import ops" src/charm.py | head -15

<details>
<summary>7 lines</summary>

```
30:import ops
56:from ops import CollectStatusEvent, StoredState
57:from ops.charm import CharmBase
58:from ops.main import main
59:from ops.model import (
67:from ops.pebble import Error, Layer, PathError, ProtocolError
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 22s</sub>

### ✅ `bash`

**Auto-fix and check lint**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev ruff check --fix-only src/charm.py 2>&1 | tail -5 && uv run --frozen --isolated --extra=dev ruff check src/charm.py 2>&1 | tail -10

```
Installed 111 packages in 48ms
Installed 111 packages in 54ms
All checks passed!
<exited with exit code 0>
```


---

<sub>⏱️ 10m 31s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && PYTHONPATH=.:lib:src uv run --frozen --isolated --extra=dev pytest tests/unit/ -x --tb=short 2>&1 | tail -60

<details>
<summary>40 lines</summary>

```
Installed 111 packages in 49ms
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-8.3.5, pluggy-1.5.0 -- /home/ubuntu/.cache/uv/builds-v0/.tmpA41u8B/bin/python
cachedir: .pytest_cache
rootdir: /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4
configfile: pyproject.toml
plugins: interface-tester-3.3.1, operator-0.42.0, anyio-4.9.0, asyncio-0.21.2
asyncio: mode=Mode.AUTO
collecting ... 
----------------------------- live log collection ------------------------------
INFO     charm_logging:charm_logging.py:345 instrumenting <class 'src.charm.LokiOperatorCharm'>
collected 80 items

tests/unit/test_charm.py::TestCharm::test__alerting_config ERROR

==================================== ERRORS ====================================
______________ ERROR at setup of TestCharm.test__alerting_config _______________
tests/unit/conftest.py:17: in patch_ops_tracing
    with ops_tracing.patch_tracing():
E   AttributeError: module 'ops_tracing' has no attribute 'patch_tracing'
=============================== warnings summary ===============================
../../../home/ubuntu/.cache/uv/builds-v0/.tmpA41u8B/lib/python3.12/site-packages/fs/__init__.py:4
  /home/ubuntu/.cache/uv/builds-v0/.tmpA41u8B/lib/python3.12/site-packages/fs/__init__.py:4: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
    __import__("pkg_resources").declare_namespace(__name__)  # type: ignore

../../../home/ubuntu/.cache/uv/builds-v0/.tmpA41u8B/lib/python3.12/site-packages/fs/__init__.py:4
  /home/ubuntu/.cache/uv/builds-v0/.tmpA41u8B/lib/python3.12/site-packages/fs/__init__.py:4: DeprecationWarning: Deprecated call to `pkg_resources.declare_namespace('fs')`.
  Implementing implicit namespace packages (as specified in PEP 420) is preferred to `pkg_resources.declare_namespace`. See https://setuptools.pypa.io/en/latest/references/keywords.html#keyword-namespace-packages
    __import__("pkg_resources").declare_namespace(__name__)  # type: ignore

../../../home/ubuntu/.cache/uv/builds-v0/.tmpA41u8B/lib/python3.12/site-packages/fs/opener/__init__.py:6
  /home/ubuntu/.cache/uv/builds-v0/.tmpA41u8B/lib/python3.12/site-packages/fs/opener/__init__.py:6: DeprecationWarning: Deprecated call to `pkg_resources.declare_namespace('fs.opener')`.
  Implementing implicit namespace packages (as specified in PEP 420) is preferred to `pkg_resources.declare_namespace`. See https://setuptools.pypa.io/en/latest/references/keywords.html#keyword-namespace-packages
    __import__("pkg_resources").declare_namespace(__name__)  # type: ignore

../../../home/ubuntu/.cache/uv/builds-v0/.tmpA41u8B/lib/python3.12/site-packages/pkg_resources/__init__.py:2559
  /home/ubuntu/.cache/uv/builds-v0/.tmpA41u8B/lib/python3.12/site-packages/pkg_resources/__init__.py:2559: DeprecationWarning: Deprecated call to `pkg_resources.declare_namespace('fs')`.
  Implementing implicit namespace packages (as specified in PEP 420) is preferred to `pkg_resources.declare_namespace`. See https://setuptools.pypa.io/en/latest/references/keywords.html#keyword-namespace-packages
    declare_namespace(parent)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
ERROR tests/unit/test_charm.py::TestCharm::test__alerting_config - AttributeE...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
========================= 4 warnings, 1 error in 0.18s =========================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 38s</sub>

### ✅ `bash`

**Check ops_tracing contents for v3.6.0**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && PYTHONPATH=.:lib:src uv run --frozen --isolated --extra=dev python3 -c "
import ops_tracing
print(dir(ops_tracing))
import ops_tracing._mock as m
print(dir(m))
" 2>&1 | tail -5

```
Installed 111 packages in 61ms
['Tracing', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '_api', '_backend', '_buffer', '_export', '_mark_observed', '_setup', '_shutdown', 'set_destination', 'vendor']
['Generator', 'InMemorySpanExporter', 'Resource', 'SPAN_PROCESSOR', 'SimpleSpanProcessor', 'TracerProvider', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', '_backend', '_create_provider', 'annotations', 'contextlib', 'opentelemetry', 'patch_tracing', 'pathlib']
<exited with exit code 0>
```


---

<sub>⏱️ 10m 43s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py updated with changes.
```


---

<sub>⏱️ 10m 49s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py

```
File /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/conftest.py updated with changes.
```


---

<sub>⏱️ 11m 24s</sub>

### ✅ `bash`

**Run unit tests again**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && PYTHONPATH=.:lib:src uv run --frozen --isolated --extra=dev pytest tests/unit/ -x --tb=short 2>&1 | tail -40

<details>
<summary>35 lines</summary>

```
self.harness = Harness(

tests/unit/test_log_proxy_consumer.py::TestTypeValidation::test_log_files_various_invalid_types
tests/unit/test_log_proxy_consumer.py::TestTypeValidation::test_log_files_various_invalid_types
  /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/test_log_proxy_consumer.py:365: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(ConsumerCharm, meta=ConsumerCharm.metadata_yaml)

tests/unit/test_log_proxy_consumer.py::TestTypeValidation::test_log_files_various_valid_types
tests/unit/test_log_proxy_consumer.py::TestTypeValidation::test_log_files_various_valid_types
tests/unit/test_log_proxy_consumer.py::TestTypeValidation::test_log_files_various_valid_types
tests/unit/test_log_proxy_consumer.py::TestTypeValidation::test_log_files_various_valid_types
tests/unit/test_log_proxy_consumer.py::TestTypeValidation::test_log_files_various_valid_types
  /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/test_log_proxy_consumer.py:357: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(ConsumerCharm, meta=ConsumerCharm.metadata_yaml)

tests/unit/test_provider.py::TestLokiPushApiProvider::test__on_logging_relation_changed
tests/unit/test_provider.py::TestLokiPushApiProvider::test__on_logging_relation_created_and_broken
tests/unit/test_provider.py::TestLokiPushApiProvider::test_alerts
tests/unit/test_provider.py::TestLokiPushApiProvider::test_relation_data
  /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/test_provider.py:109: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(FakeLokiCharm, meta=FakeLokiCharm.metadata_yaml)

tests/unit/test_transform.py::TestTransform::test_disable_on_invalid_arch
tests/unit/test_transform.py::TestTransform::test_fetches_the_correct_expression
tests/unit/test_transform.py::TestTransform::test_gives_path_on_valid_arch
tests/unit/test_transform.py::TestTransform::test_handles_comparisons
tests/unit/test_transform.py::TestTransform::test_handles_multiple_labels
tests/unit/test_transform.py::TestTransform::test_returns_original_expression_when_subprocess_call_errors
tests/unit/test_transform.py::TestTransform::test_setup_transformer
tests/unit/test_transform.py::TestTransform::test_uses_original_expression_when_binary_missing
  /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/test_transform.py:27: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(ToolProviderCharm)

tests/unit/test_transform.py::TestValidateAlerts::test_returns_errors_on_bad_rule_file
tests/unit/test_transform.py::TestValidateAlerts::test_successfully_validates_good_alert_rules
  /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4/tests/unit/test_transform.py:151: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(ToolProviderCharm)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 71 passed, 9 skipped, 109 warnings in 26.61s =================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 30s</sub>

### 💬 Copilot

All 71 tests pass (9 skipped are pre-existing). Now let me also run the lint check on test files:

---

<sub>⏱️ 11m 31s</sub>

### ✅ `bash`

**Final lint check**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev ruff check src/ tests/unit/ lib/charms/loki_k8s/ 2>&1 | tail -10

```
Installed 111 packages in 51ms
All checks passed!
<exited with exit code 0>
```


---

<sub>⏱️ 11m 36s</sub>

### 💬 Copilot

All checks pass. Let me verify the final state of the key changed files and commit:

---

<sub>⏱️ 11m 37s</sub>

### ✅ `bash`

**Check what files were changed**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && git diff --stat

<details>
<summary>8 lines</summary>

```
pyproject.toml                         |   15 +-
 src/charm.py                           |   23 +-
 tests/unit/conftest.py                 |   15 +-
 tests/unit/test_datasource_exchange.py |    2 +-
 tests/unit/test_grafana_source.py      |    2 +-
 uv.lock                                | 2010 ++++--------------------------------------------------------------------
 6 files changed, 122 insertions(+), 1945 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 51s</sub>

### ❌ `bash`

**Commit all changes**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && git add -A && git commit -m "Upgrade to ops 3.6.0 / ops-tracing 3.6.0 / ops-scenario 8.6.0

- Bump ops dependency to ops[tracing]>=3.6.0, using the built-in
  tracing package (ops-tracing) instead of the vendored charm lib

- Replace @trace_charm decorator + TracingEndpointRequirer(charm-tracing)
  + charm_tracing_config with ops.tracing.Tracing, the new first-class
  tracing API introduced with ops 3.x. The workload-tracing relation
  (Jaeger/Tempo) keeps using TracingEndpointRequirer unchanged.

- Drop explicit opentelemetry-* version pins: these are now managed
  transitively by ops-tracing, which vendors or pins what it needs.
  Also drop importlib-metadata, which is in the stdlib since Python 3.10.

- Bump requires-python from ~=3.8 to >=3.10, matching the ops 3.x
  minimum (ops 3.0.0 dropped Python 3.8/3.9 support, and ops 3.4.0
  removed 3.8/3.9 compatibility shims).  Update pyright pythonVersion
  and black target-version accordingly.

- Update unit-test fixtures: replace charm_tracing_disabled() +
  BUFFER_DEFAULT_CACHE_FILE_NAME patch with ops_tracing._mock.patch_tracing(),
  the idiomatic ops-tracing testing helper.

- Replace bare `from scenario import …` with `from ops.testing import …`
  in conftest.py, test_datasource_exchange.py and test_grafana_source.py.
  The ops-scenario package (now at 8.x, mirroring ops 3.x) is a
  compatibility shim; ops.testing is the canonical location.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
Command blocked: contains dangerous shell expansion patterns (e.g., parameter transformation, indirect expansion, or nested command substitution) that could enable arbitrary code execution. Please rewrite the command without these expansion patterns.
```


---

<sub>⏱️ 12m 0s</sub>

### ✅ `bash`

**Commit all changes**

$ cd /tmp/ops-upgrade-experiment/loki-k8s-operator__ops-tracing__C4 && git add -A && git commit -F - <<'COMMIT_MSG'
Upgrade to ops 3.6.0 / ops-tracing 3.6.0 / ops-scenario 8.6.0

- Bump ops dependency to ops[tracing]>=3.6.0, using the built-in
  tracing package (ops-tracing) instead of the vendored charm lib

- Replace @trace_charm decorator + TracingEndpointRequirer(charm-tracing)
  + charm_tracing_config with ops.tracing.Tracing, the new first-class
  tracing API introduced with ops 3.x. The workload-tracing relation
  (Jaeger/Tempo) keeps using TracingEndpointRequirer unchanged.

- Drop explicit opentelemetry-* version pins: these are now managed
  transitively by ops-tracing, which vendors or pins what it needs.
  Also drop importlib-metadata, which is in the stdlib since Python 3.10.

- Bump requires-python from ~=3.8 to >=3.10, matching the ops 3.x
  minimum (ops 3.0.0 dropped Python 3.8/3.9 support, and ops 3.4.0
  removed 3.8/3.9 compatibility shims). Update pyright pythonVersion
  and black target-version accordingly.

- Update unit-test fixtures: replace charm_tracing_disabled() +
  BUFFER_DEFAULT_CACHE_FILE_NAME patch with ops_tracing._mock.patch_tracing(),
  the idiomatic ops-tracing testing helper.

- Replace bare 'from scenario import ...' with 'from ops.testing import ...'
  in conftest.py, test_datasource_exchange.py and test_grafana_source.py.
  The ops-scenario package (now at 8.x, mirroring ops 3.x) is a
  compatibility shim; ops.testing is the canonical location.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
COMMIT_MSG

```
[ops-upgrade 2392bf7] Upgrade to ops 3.6.0 / ops-tracing 3.6.0 / ops-scenario 8.6.0
 6 files changed, 122 insertions(+), 1945 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 12m 5s</sub>

### ✅ `sql`

**Mark all todos done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark all todos done",
  "query": "UPDATE todos SET status = 'done' WHERE id = 'run-tests';"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 12m 19s</sub>

### ✅ `task_complete`

**Created branch `ops-upgrade` with a single commit upgradi...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Created branch `ops-upgrade` with a single commit upgrading from ops 2.23.2 → 3.6.0, ops-tracing 2.23.2 → 3.6.0, and ops-scenario 7.23.2 → 8.6.0.\n\n**Analysis of each release item and how it was addressed:**\n\n| Item | Impact | Action |\n|---|---|---|\n| ops 3.0.0: drops Python 3.8/3.9 | Breaking | `requires-python` → `>=3.10`; updated `pyright.pythonVersion` and `black.target-version` |\n| ops 3.0.0–3.6.0: no other charm-visible breaking changes | None | No action needed |\n| ops-tracing 3.x: new `ops.tracing.Tracing` first-class API | Feature to adopt | Replaced `@trace_charm` + `TracingEndpointRequirer(charm-tracing)` + `charm_tracing_config` with `ops.tracing.Tracing(self, tracing_relation_name=\"charm-tracing\")`. TLS works via system CAs (the charm already runs `update-ca-certificates`). |\n| ops-tracing 3.x: opentelemetry managed internally | Simplification | Removed all pinned `opentelemetry-*` and `importlib-metadata` entries from `pyproject.toml` |\n| ops-scenario 8.x: compatibility shim over ops.testing | Cleanup | Updated `from scenario import …` → `from ops.testing import …` in all three affected test files |\n| ops.testing (3.5.0): `SCENARIO_BARE_CHARM_ERRORS` env var | Informational | No code change needed; can be set in CI if desired |\n| ops.testing (3.4.0): context-manager exception wrapping fix | Potentially breaking | No `with Context()` pattern used in this charm's tests |\n| ops 3.3.0: `ops.JujuContext` exposed | Feature | Not needed by this charm |\n| ops 3.4.0: `ops.hookcmds` | Low-level API | Not needed by charm code |\n| Test fixture update | Required | Replaced `charm_tracing_disabled()` + buffer-file patch with `ops_tracing._mock.patch_tracing()` autouse fixture |\n\nAll 71 unit tests pass, lint is clean."
}
```

</details>

<details>
<summary>15 lines</summary>

```
Created branch `ops-upgrade` with a single commit upgrading from ops 2.23.2 → 3.6.0, ops-tracing 2.23.2 → 3.6.0, and ops-scenario 7.23.2 → 8.6.0.

**Analysis of each release item and how it was addressed:**

| Item | Impact | Action |
|---|---|---|
| ops 3.0.0: drops Python 3.8/3.9 | Breaking | `requires-python` → `>=3.10`; updated `pyright.pythonVersion` and `black.target-version` |
| ops 3.0.0–3.6.0: no other charm-visible breaking changes | None | No action needed |
| ops-tracing 3.x: new `ops.tracing.Tracing` first-class API | Feature to adopt | Replaced `@trace_charm` + `TracingEndpointRequirer(charm-tracing)` + `charm_tracing_config` with `ops.tracing.Tracing(self, tracing_relation_name="charm-tracing")`. TLS works via system CAs (the charm already runs `update-ca-certificates`). |
| ops-tracing 3.x: opentelemetry managed internally | Simplification | Removed all pinned `opentelemetry-*` and `importlib-metadata` entries from `pyproject.toml` |
| ops-scenario 8.x: compatibility shim over ops.testing | Cleanup | Updated `from scenario import …` → `from ops.testing import …` in all three affected test files |
| ops.testing (3.5.0): `SCENARIO_BARE_CHARM_ERRORS` env var | Informational | No code change needed; can be set in CI if desired |
| ops.testing (3.4.0): context-manager exception wrapping fix | Potentially breaking | No `with Context()` pattern used in this charm's tests |
| ops 3.3.0: `ops.JujuContext` exposed | Feature | Not needed by this charm |
| ops 3.4.0: `ops.hookcmds` | Low-level API | Not needed by charm code |
| Test fixture update | Required | Replaced `charm_tracing_disabled()` + buffer-file patch with `ops_tracing._mock.patch_tracing()` autouse fixture |

All 71 unit tests pass, lint is clean.
```

</details>


---

<sub>⏱️ 12m 19s</sub>

### ✓ Task Complete

Created branch `ops-upgrade` with a single commit upgrading from ops 2.23.2 → 3.6.0, ops-tracing 2.23.2 → 3.6.0, and ops-scenario 7.23.2 → 8.6.0.

**Analysis of each release item and how it was addressed:**

| Item | Impact | Action |
|---|---|---|
| ops 3.0.0: drops Python 3.8/3.9 | Breaking | `requires-python` → `>=3.10`; updated `pyright.pythonVersion` and `black.target-version` |
| ops 3.0.0–3.6.0: no other charm-visible breaking changes | None | No action needed |
| ops-tracing 3.x: new `ops.tracing.Tracing` first-class API | Feature to adopt | Replaced `@trace_charm` + `TracingEndpointRequirer(charm-tracing)` + `charm_tracing_config` with `ops.tracing.Tracing(self, tracing_relation_name="charm-tracing")`. TLS works via system CAs (the charm already runs `update-ca-certificates`). |
| ops-tracing 3.x: opentelemetry managed internally | Simplification | Removed all pinned `opentelemetry-*` and `importlib-metadata` entries from `pyproject.toml` |
| ops-scenario 8.x: compatibility shim over ops.testing | Cleanup | Updated `from scenario import …` → `from ops.testing import …` in all three affected test files |
| ops.testing (3.5.0): `SCENARIO_BARE_CHARM_ERRORS` env var | Informational | No code change needed; can be set in CI if desired |
| ops.testing (3.4.0): context-manager exception wrapping fix | Potentially breaking | No `with Context()` pattern used in this charm's tests |
| ops 3.3.0: `ops.JujuContext` exposed | Feature | Not needed by this charm |
| ops 3.4.0: `ops.hookcmds` | Low-level API | Not needed by charm code |
| Test fixture update | Required | Replaced `charm_tracing_disabled()` + buffer-file patch with `ops_tracing._mock.patch_tracing()` autouse fixture |

All 71 unit tests pass, lint is clean.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
