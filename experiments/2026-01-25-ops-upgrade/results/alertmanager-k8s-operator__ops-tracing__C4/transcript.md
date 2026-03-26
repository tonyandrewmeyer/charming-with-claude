# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `3feb9851-6e25-44f1-be59-aa87d65b79b6`  
> - **Started:** 3/15/2026, 3:06:57 PM  
> - **Duration:** 12m 56s  
> - **Exported:** 3/15/2026, 3:19:54 PM  

---

<sub>⏱️ 5s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 12s</sub>

### ✅ `bash`

**Check current ops version and recent git history**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && cat pyproject.toml | grep -A5 "ops" && echo "---" && cat charmcraft.yaml | grep -A5 "ops" && echo "---" && git --no-pager log --oneline -5

<details>
<summary>15 lines</summary>

```
"ops",
  "pyyaml",
  "lightkube>=0.11",  # observability_libs
  "lightkube-models",  # observability_libs
  "jsonschema", # traefik_k8s, tls_certificates
  "cryptography",  # tls_certificates
--
  "ops[testing]",
  "pytest-interface-tester>0.3",
  # Integration
  "juju<=3.3.0,>=3.0",
  "websockets<14.0",
  "pytest-operator",
---
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 12s</sub>

### ✅ `bash`

**Check latest ops version available**

$ pip index versions ops 2>/dev/null | head -5 || pip install ops --dry-run 2>&1 | head -10

```
ops (3.6.0)
Available versions: 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 2.20.0, 2.19.4, 2.19.0, 2.18.1, 2.18.0, 2.17.1, 2.17.0, 2.16.1, 2.16.0, 2.15.0, 2.14.1, 2.14.0, 2.13.0, 2.12.0, 2.11.0, 2.10.0, 2.9.0, 2.8.0, 2.7.0, 2.6.0, 2.5.1, 2.5.0, 2.4.1, 2.4.0, 2.3.0, 2.2.0, 2.1.1, 2.1.0, 2.0.0, 1.5.5, 1.5.4, 1.5.3, 1.5.2, 1.5.1, 1.5.0, 1.4.0, 1.3.0, 1.2.0, 1.1.0, 1.0.1, 1.0.0, 0.10.0, 0.9.0, 0.8.0, 0.7.0, 0.6.1, 0.6.0, 0.4.7, 0.4.6, 0.4.5, 0.4.4, 0.4.3, 0.4.2, 0.2.1, 0.2.0, 0.1.0
  INSTALLED: 2.23.2
  LATEST:    3.6.0
<exited with exit code 0>
```


---

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Read full pyproject.toml**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && cat pyproject.toml

<details>
<summary>81 lines</summary>

```
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
[project]
name = "alertmanager-k8s"
version = "0.0"
requires-python = "~=3.8"

dependencies = [
  "ops",
  "pyyaml",
  "lightkube>=0.11",  # observability_libs
  "lightkube-models",  # observability_libs
  "jsonschema", # traefik_k8s, tls_certificates
  "cryptography",  # tls_certificates
  "pydantic>=2",  # traefik_k8s.v2.ingress
  "opentelemetry-exporter-otlp-proto-http>=1.21.0",  # tracing
  "tenacity",
  "cosl",
  "charmed-service-mesh-helpers>=0.2.0",
  "lightkube-extensions",
]

[project.optional-dependencies]
dev = [
  # Linting
  "ruff",
  "codespell",
  # Static
  "pyright<1.1.399", # 1.1.399 vendors typeshed that dropped Python 3.8 support
  # Unit
  "pytest",
  "coverage[toml]",
  "deepdiff",
  "hypothesis",
  "validators>=0.21.2",
  "ops[testing]",
  "pytest-interface-tester>0.3",
  # Integration
  "juju<=3.3.0,>=3.0",
  "websockets<14.0",
  "pytest-operator",
  "pytest-httpserver",
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

[tool.ruff.lint]
select = ["E", "W", "F", "C", "N", "R", "D", "I001"]
# Ignore E501 because using black creates errors with this
# Ignore D107 Missing docstring in __init__
ignore = ["E501", "D107", "N818", "RET504"]
# D100, D101, D102, D103: Ignore missing docstrings in tests
per-file-ignores = {"tests/*" = ["D100","D101","D102","D103"]}

[tool.ruff.lint.pydocstyle]
convention = "google"

# Static analysis tools configuration
[tool.pyright]
extraPaths = ["src", "lib"]
pythonVersion = "3.8"
pythonPlatform = "All"
exclude = [
  "tests/integration/remote_configuration_tester/**",
]

[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"
asyncio_mode = "auto"
addopts = "--tb=native --verbose --capture=no --log-cli-level=INFO"

[tool.codespell]
skip = ".git,.tox,build,venv*"
ignore-words-list = "assertIn"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 17s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src

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

<sub>⏱️ 23s</sub>

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

<sub>⏱️ 23s</sub>

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
<summary>199 lines</summary>

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

This second beta for the 3.4.0 release fixes one significant bug with the new `ops.hookcmds` usage in the model backend, where getting

<note>Content truncated. Call the fetch tool with a start_index of 20000 to get more content.</note>
```

</details>


---

<sub>⏱️ 28s</sub>

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
<summary>85 lines</summary>

```
Contents of https://github.com/canonical/operator/releases:
 secret info when the secret object had both ID and label set would fail.

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

<sub>⏱️ 28s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py

```
File too large to read at once (26.0 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


---

<sub>⏱️ 34s</sub>

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

<sub>⏱️ 33s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py (lines 1-100)

<details>
<summary>100 lines</summary>

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
```

</details>


---

<sub>⏱️ 39s</sub>

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

<sub>⏱️ 39s</sub>

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

<sub>⏱️ 45s</sub>

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

<sub>⏱️ 45s</sub>

### ✅ `bash`

**Check ops-tracing versions**

$ pip index versions ops-tracing 2>/dev/null | head -3 && pip show ops-tracing 2>/dev/null | head -5

<details>
<summary>9 lines</summary>

```
ops-tracing (3.6.0)
Available versions: 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 0.9.6, 0.9.4, 0.9.3, 0.9.2, 0.9.1, 0.9.0
  INSTALLED: 2.23.2
Name: ops-tracing
Version: 2.23.2
Summary: The tracing facility for the Ops library.
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 56s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/operator/releases/tag/ops-tracing-3.6.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 20000,
  "url": "https://github.com/canonical/operator/releases/tag/ops-tracing-3.6.0"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/operator/releases/tag/ops-tracing-3.6.0 - status code 404
```


---

<sub>⏱️ 57s</sub>

### ✅ `bash`

**Check ops-scenario info**

$ pip index versions ops-scenario 2>/dev/null | head -3 && pip show ops-scenario 2>/dev/null | head -5

<details>
<summary>9 lines</summary>

```
ops-scenario (8.6.0)
Available versions: 8.6.0, 8.5.2, 8.5.1, 8.5.0, 8.4.0, 8.3.1, 8.3.0, 8.2.0, 8.1.0, 8.0.0, 7.23.2, 7.23.1, 7.23.0, 7.22.0, 7.21.1, 7.21.0, 7.20.0, 7.19.4, 7.2.0, 7.1.3, 7.1.2, 7.1.1, 7.0.5, 7.0.4, 7.0.3, 7.0.2, 7.0.1, 7.0.0, 6.1.7, 6.1.6, 6.1.5, 6.1.4, 6.1.3, 6.1.2, 6.1.1, 6.1.0, 6.0.5, 6.0.4, 6.0.3, 6.0.2, 6.0.1, 6.0, 5.8.1, 5.8, 5.7.1, 5.7, 5.6.2, 5.6.1, 5.6, 5.5, 5.4.1, 5.4, 5.3.1, 5.3, 5.2.2, 5.2.1, 5.2, 5.1.3, 5.1.2, 5.1.1, 5.1.0, 5.0, 4.0.4.1, 4.0.4, 4.0.3, 4.0.2, 4.0.1, 4.0, 3.1, 3.0.2, 3.0.1, 2.2, 2.1.3.5, 2.1.3.4, 2.1.3.3, 2.1.3.2, 2.1.3.1, 2.1.3, 2.1.2.5, 2.1.2.4, 2.1.2.3, 2.1.2.2, 2.1.2.1, 2.1.1, 2.1.0, 2.0.5, 2.0.4, 2.0.0
  INSTALLED: 7.23.2
Name: ops-scenario
Version: 7.23.2
Summary: Python library providing a state-transition testing API for Operator Framework charms.
Home-page: 
Author:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 4s</sub>

### ✅ `bash`

**Check what ops-tracing 3.6.0 would install**

$ pip show ops-tracing 2>/dev/null && pip install ops-tracing==3.6.0 --dry-run 2>&1 | grep "Would install"

<details>
<summary>11 lines</summary>

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
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 1m 3s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/ops-tracing/#history**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 20000,
  "url": "https://pypi.org/project/ops-tracing/#history"
}
```

</details>

```
Contents of https://pypi.org/project/ops-tracing/#history:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 1m 8s</sub>

### ✅ `web_fetch`

**https://pypi.org/pypi/ops-tracing/3.6.0/json**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://pypi.org/pypi/ops-tracing/3.6.0/json"
}
```

</details>

```
Content type application/json cannot be simplified to markdown. Here is the raw content:
Contents of https://pypi.org/pypi/ops-tracing/3.6.0/json:
{"info":{"author":"The Charm Tech team at Canonical Ltd.","author_email":null,"bugtrack_url":null,"classifiers":["Development Status :: 5 - Production/Stable","Framework :: OpenTelemetry","Intended Audience :: Developers","Intended Audience :: System Administrators","Natural Language :: English","Operating System :: MacOS :: MacOS X","Operating System :: POSIX :: Linux","Programming Language :: Python","Programming Language :: Python :: 3","Programming Language :: Python :: 3 :: Only","Programming Language :: Python :: 3.10","Programming Language :: Python :: 3.11","Programming Language :: Python :: 3.12","Programming Language :: Python :: 3.13","Programming Language :: Python :: 3.14","Programming Language :: Python :: Implementation :: CPython","Programming Language :: Python :: Implementation :: PyPy","Topic :: Software Development :: Libraries"],"description":"# ops-tracing\n\n**First-party OpenTelemetry integration for the [Ops](https://pypi.org/project/ops/) library.**\nThis package adds tracing capabilities to Ops, enabling you to observe the performance of your applications.\n\n---\n\n## Overview\n\n- Seamless integration with [ops](https://pypi.org/project/ops/)\n- Built on OpenTelemetry\n- Enables tracing of your charm code\n\nPlease add `ops[tracing]` to your charm's dependencies, rather than this package directly.\n\n---\n\n## Documentation\n\nComprehensive documentation for the Ops library, including the tracing feature, is available at:\n[Ops documentation](https://documentation.ubuntu.com/ops/latest/).\n\nYou’ll find setup instructions, usage examples, and best practices for leveraging the tracing functionality.\n\n---\n\n## Community and Support\n\n- **Matrix Chat**: [Charm Tech](https://matrix.to/#/#charmhub-ops:ubuntu.com)\n- **Forum**: [Charmhub - Discuss Python operator development](https://discourse.charmhub.io/)\n- **Issue Tracker**: See [GitHub issues](https://github.com/canonical/ops/issues)\n- **Further Links**: See the [ops PyPI page](https://pypi.org/project/ops/)\n\nFeedback, contributions, and bug reports are always welcome.\nPlease follow the guidelines in the [main repository](https://github.com/canonical/ops/)\nfor the Ops library.\n\n---\n\n## License\n\nThis project is licensed under the same license as `ops`.\nRefer to the `ops` repository for full details.\n\n---\n\nHappy tracing!\n","description_content_type":"text/markdown","docs_url":null,"download_url":null,"downloads":{"last_day":-1,"last_month":-1,"last_week":-1},"dynamic":null,"home_page":null,"keywords":null,"license":null,"license_expression":"Apache-2.0","license_files":null,"maintainer":null,"maintainer_email":null,"name":"ops-tracing","package_url":"https://pypi.org/project/ops-tracing/","platform":null,"project_url":"https://pypi.org/project/ops-tracing/","project_urls":{"Changelog":"https://github.com/canonical/operator/blob/main/CHANGES.md","Documentation":"https://documentation.ubuntu.com/ops/latest/","Issues":"https://github.com/canonical/operator/issues","Repository":"https://github.com/canonical/operator"},"provides_extra":null,"release_url":"https://pypi.org/project/ops-tracing/3.6.0/","requires_dist":["opentelemetry-api~=1.0","opentelemetry-sdk~=1.30","ops==3.6.0","pydantic"],"requires_python":">=3.10","summary":"The tracing facility for the Ops library.","version":"3.6.0","yanked":false,"yanked_reason":null},"last_serial":34627579,"ownership":{"organization":null,"roles":[{"role":"Owner","user":"benhoyt"},{"role":"Owner","user":"dimaqq"},{"role":"Owner","user":"tonyandrewmeyer"}]},"urls":[{"comment_text":null,"digests":{"blake2b_256":"270ba255e805f367abb16743343d9fd720f828210bbca7eebe9c29fd05b8a945","md5":"7cbc461ba457d43017b71dd2ddd62bf9","sha256":"68703d602fb5d5bd026dfbb579bf9abcf25a24efeae4dfe4c2b9b0edfeec3515"},"downloads":-1,"filename":"ops_tracing-3.6.0-py3-none-any.whl","has_sig":false,"md5_digest":"7cbc461ba457d43017b71dd2ddd62bf9","packagetype":"bdist_wheel","python_version":"py3","requires_python":">=3.10","size":31557,"upload_time":"2026-02-26T04:19:11","upload_time_iso_8601":"2026-02-26T04:19:11.122032Z","url":"https://files.pythonhosted.org/packages/27/0b/a255e805f367abb16743343d9fd720f828210bbca7eebe9c29fd05b8a945/ops_tracing-3.6.0-py3-none-any.whl","yanked":false,"yanked_reason":null},{"comment_text":null,"digests":{"blake2b_256":"ab26cafd474e6b5b9515b3a630b810f47f6db5e83617a7d7646c1abd029c4098","md5":"aadb63924926820985f00f0720439914","sha256":"0f94623a13e9d146116a2603bf0ebf7dadf0ffb3a9c9d53ff8026531d43ea7d4"},"downloads":-1,"filename":"ops_tracing-3.6.0.tar.gz","has_sig":false,"md5_digest":"aadb63924926820985f00f0720439914","packagetype":"sdist","python_version":"source","requires_python":">=3.10","size":28572,"upload_time":"2026-02-26T04:19:16","upload_time_iso_8601":"2026-02-26T04:19:16.367641Z","url":"https://files.pythonhosted.org/packages/ab/26/cafd474e6b5b9515b3a630b810f47f6db5e83617a7d7646c1abd029c4098/ops_tracing-3.6.0.tar.gz","yanked":false,"yanked_reason":null}],"vulnerabilities":[]}

```


---

<sub>⏱️ 1m 8s</sub>

### ✅ `web_fetch`

**https://pypi.org/pypi/ops-scenario/8.6.0/json**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://pypi.org/pypi/ops-scenario/8.6.0/json"
}
```

</details>

````
Content type application/json cannot be simplified to markdown. Here is the raw content:
Contents of https://pypi.org/pypi/ops-scenario/8.6.0/json:
{"info":{"author":null,"author_email":"Pietro Pasotti <pietro.pasotti@canonical.com>","bugtrack_url":null,"classifiers":["Development Status :: 5 - Production/Stable","Framework :: Pytest","Intended Audience :: Developers","Topic :: Software Development :: Quality Assurance","Topic :: Software Development :: Testing","Topic :: Utilities"],"description":"# ops-scenario, the unit testing framework for ops charms\n\n`ops-scenario` is a Python library that provides state-transition testing for\n[Ops](https://documentation.ubuntu.com/ops/latest/) charms. These tests are higher level than\ntypical unit tests, but run at similar speeds and are the recommended approach\nfor testing charms within requiring a full [Juju](https://juju.is) installation.\n\nTest are written in the arrange/act/assert pattern, arranging an object\nrepresenting the current Juju state, acting by emulating an event from Juju, and\nthen asserting on the (simulated) output Juju state.\n\n## Writing tests\n\nHere's a test that verifies that a unit is active after the `start` event, with a very minimal initial state:\n\n```python\nfrom ops import testing\n\n# 'src/charm.py' typically contains the charm class.\nfrom charm import MyCharm\n\ndef test_start():\n    ctx = testing.Context(MyCharm)\n    state_in = testing.State()\n    state_out = ctx.run(ctx.on.start(), state_in)\n    assert state_out.unit_status == testing.ActiveStatus()\n```\n\nMore comprehensive tests will include relations, containers, secrets, and other\ncomponents in the input state, and assertions against both the output state and\nthe context. The 'act' stage remains a simple single call, although additional\narguments may be required for the event, such as the relation or container that\ntriggered it. For example:\n\n```python\nimport pytest\nfrom ops import testing\n\nfrom charm import MyCharm\n\n@pytest.mark.parametrize(\n    'leader',\n    [pytest.param(True, id='leader'), pytest.param(False, id='non-leader')],\n)\ndef test_(leader: bool):\n    # Arrange:\n    ctx = testing.Context(MyCharm)\n    relation = testing.Relation('db', local_app_data={'hostname': 'example.com'})\n    peer_relation = testing.PeerRelation('peer')\n    container = testing.Container('workload', can_connect=True)\n    relation_secret = testing.Secret({'certificate': 'xxxxxxxx'})\n    user_secret = testing.Secret({'username': 'admin', 'password': 'xxxxxxxx'})\n    config = {'port': 8443, 'admin-credentials': 'secret:1234'}\n    state_in = testing.State(\n        leader=leader,\n        config=config,\n        relations={relation, peer_relation},\n        containers={container},\n        secrets={relation_secret, user_secret},\n        unit_status=testing.BlockedStatus(),\n        workload_version='1.0.1',\n    )\n\n    # Act:\n    state_out = ctx.run(ctx.on.relation_changed(relation), state_in)\n\n    # Assert:\n    assert testing.JujuLogLine(level='INFO', message='Distributing secret.') in ctx.juju_log\n    peer_relation_out = state_out.get_relation(peer_relation.id)\n    assert peer_relation_out.peers_data[0] == {'secret_id': relation_secret.id}\n```\n\nYou don't have to use pytest for your charm tests, but it's what we recommend.\npytest's `assert`-based approach is a straightforward way to write tests, and\nits fixtures are helpful for structuring setup and teardown.\n\n## Installation\n\nFor charm tests, install the testing framework by adding the `testing` extra of\nops in your unit testing environment. For example, in `pyproject.toml`:\n\n```toml\n[dependency-groups]\ntest = ['ops[testing]<4.0']\n```\n\nOps checks if `ops-scenario` is installed, and, if so, makes the classes\n(such as `Context`, `State`, and `Relation`) available in the `ops.testing`\nnamespace. Use `from ops import testing` rather than importing the `scenario`\npackage.\n\n`ops-scenario` supports the same platforms and Python versions as ops itself.\n\n## Documentation\n\n * To get started, work through our ['Write your first Kubernetes charm' tutorial](https://documentation.ubuntu.com/ops/latest/tutorial/from-zero-to-hero-write-your-first-kubernetes-charm/create-a-minimal-kubernetes-charm/#write-unit-tests-for-your-charm), following the instructions for adding\n   unit tests at the end of each chapter.\n * When you need to write a test that involves specific ops functionality,\n   refer to our [how-to guides](https://documentation.ubuntu.com/ops/latest/howto/)\n   which all conclude with examples of tests of the ops functionality.\n * Use our extensive [reference documentation](https://documentation.ubuntu.com/ops/latest/reference/ops-testing/#ops-testing) when you need to know how each `testing` object works. These\n   docs are also available via the standard Python `help()` functionality and in\n   your IDE.\n\n[**Read the full documentation**](https://documentation.ubuntu.com/ops/latest/)\n\n## Community\n\n`ops-scenario` is a member of the Charming family. It's an open source project\nthat warmly welcomes community contributions, suggestions, fixes and\nconstructive feedback.\n\n* Read our [code of conduct](https://ubuntu.com/community/ethos/code-of-conduct):\n  As a community we adhere to the Ubuntu code of conduct.\n* [Get support](https://discourse.charmhub.io/): Discourse is the go-to forum\n  for all Ops-related discussions, including around testing.\n* Join our [online chat](https://matrix.to/#/#charmhub-charmdev:ubuntu.com):\n  Meet us in the #charmhub-charmdev channel on Matrix.\n* [Report bugs](https://github.com/canonical/operator/issues): We want to know\n  about the problems so we can fix them.\n* [Contribute docs](https://github.com/canonical/operator/blob/main/HACKING.md#contributing-documentation):\n  Get started on GitHub.\n\n## Contributing and developing\n\nAnyone can contribute to ops and `ops-scenario`. It's best to start by\n[opening an issue](https://github.com/canonical/operator/issues) with a clear\ndescription of the problem or feature request, but you can also\n[open a pull request](https://github.com/canonical/operator/pulls) directly.\n\nRead our [guide](./CONTRIBUTING.md) for more details on how to work on and\ncontribute to `ops-scenario`.\n\nCurrently, releases of `ops-scenario` are done in lockstep with releases of ops\nitself, with matching minor and bugfix release numbers. The ops documentation\noutlines how to create a new release.\n","description_content_type":"text/markdown","docs_url":null,"download_url":null,"downloads":{"last_day":-1,"last_month":-1,"last_week":-1},"dynamic":null,"home_page":null,"keywords":"juju, test","license":null,"license_expression":"Apache-2.0","license_files":null,"maintainer":"The Charm Tech team at Canonical Ltd.","maintainer_email":null,"name":"ops-scenario","package_url":"https://pypi.org/project/ops-scenario/","platform":null,"project_url":"https://pypi.org/project/ops-scenario/","project_urls":{"Bug Tracker":"https://github.com/canonical/operator/issues","Homepage":"https://github.com/canonical/operator"},"provides_extra":null,"release_url":"https://pypi.org/project/ops-scenario/8.6.0/","requires_dist":["ops==3.6.0","PyYAML>=6.0.1","typing_extensions>=4.9.0"],"requires_python":">=3.10","summary":"Python library providing a state-transition testing API for Operator Framework charms.","version":"8.6.0","yanked":false,"yanked_reason":null},"last_serial":34627577,"ownership":{"organization":null,"roles":[{"role":"Owner","user":"benhoyt"},{"role":"Owner","user":"jnsgruk"},{"role":"Owner","user":"ppasotti"},{"role":"Maintainer","user":"tonyandrewmeyer"}]},"urls":[{"comment_text":null,"digests":{"blake2b_256":"ead2fb3176805339d3aa95b9d6e43478d0e34355c6c46f27723249f46bb8d19d","md5":"cf38ad41c9f875f4ad6410a87e00fc3e","sha256":"469490a042dc45eca24eef7aa1b9214704d97d67503ad8465414ab68dc989d30"},"downloads":-1,"filename":"ops_scenario-8.6.0-py3-none-any.whl","has_sig":false,"md5_digest":"cf38ad41c9f875f4ad6410a87e00fc3e","packagetype":"bdist_wheel","python_version":"py3","requires_python":">=3.10","size":64241,"upload_time":"2026-02-26T04:19:09","upload_time_iso_8601":"2026-02-26T04:19:09.579990Z","url":"https://files.pythonhosted.org/packages/ea/d2/fb3176805339d3aa95b9d6e43478d0e34355c6c46f27723249f46bb8d19d/ops_scenario-8.6.0-py3-none-any.whl","yanked":false,"yanked_reason":null},{"comment_text":null,"digests":{"blake2b_256":"63c815d9f91eafa46d1dfa7f580be3274c22399f941724b74e274334de9468bb","md5":"6f5f31cf80da583ae029dae47beea504","sha256":"5a40a91fd5e9b6c8249933944dfc6e807ad2ddbd36a68c800746b9bb8a0eabfb"},"downloads":-1,"filename":"ops_scenario-8.6.0.tar.gz","has_sig":false,"md5_digest":"6f5f31cf80da583ae029dae47beea504","packagetype":"sdist","python_version":"source","requires_python":">=3.10","size":71728,"upload_time":"2026-02-26T04:19:15","upload_time_iso_8601":"2026-02-26T04:19:15.340189Z","url":"https://files.pythonhosted.org/packages/63/c8/15d9f91eafa46d1dfa7f580be3274c22399f941724b74e274334de9468bb/ops_scenario-8.6.0.tar.gz","yanked":false,"yanked_reason":null}],"vulnerabilities":[]}

````


---

<sub>⏱️ 1m 15s</sub>

### 💬 Copilot

Now let me look at the existing tests and the charm in detail to understand the impact better.

---

<sub>⏱️ 1m 15s</sub>

### ✅ `web_fetch`

**https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md"
}
```

</details>

<details>
<summary>282 lines</summary>

```
Content type text/plain; charset=utf-8 cannot be simplified to markdown. Here is the raw content:
Contents of https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md:
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
* Move {posargs} to the end of pytest comma

<note>Content truncated. Call the fetch tool with a start_index of 15000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 15s</sub>

### ✅ `bash`

**List test files**

$ find /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests -name "*.py" | head -20 && ls /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/

<details>
<summary>22 lines</summary>

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/test_tls_web.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/conftest.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/helpers.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/remote_configuration_tester/lib/charms/alertmanager_k8s/v0/alertmanager_remote_configuration.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/remote_configuration_tester/src/charm.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/test_remote_configuration.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/test_grafana_source.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/test_persistence.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/test_upgrade_charm.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/test_templates.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/test_kubectl_delete.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/integration/test_rescale_charm.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_external_url.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_remote_configuration_requirer.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_remote_configuration_provider.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/helpers.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_charm.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_consumer.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_push_config_to_workload_on_startup.py
integration  manual  unit
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 33s</sub>

### 💬 Copilot

Now let me look at the ops-tracing changes and the existing test files:

---

<sub>⏱️ 1m 33s</sub>

### ❌ `web_fetch`

**https://raw.githubusercontent.com/canonical/operator/main/ops-tracing/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://raw.githubusercontent.com/canonical/operator/main/ops-tracing/CHANGES.md"
}
```

</details>

```
Error: Failed to fetch https://raw.githubusercontent.com/canonical/operator/main/ops-tracing/CHANGES.md - status code 404
```


---

<sub>⏱️ 1m 33s</sub>

### ✅ `bash`

**Look at main test file**

$ head -150 /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_charm.py

<details>
<summary>124 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
import unittest
from unittest.mock import patch

import ops
import yaml
from helpers import k8s_resource_multipatch
from ops import pebble
from ops.model import ActiveStatus, BlockedStatus
from ops.testing import Harness

from alertmanager import WorkloadManager
from charm import AlertmanagerCharm

ops.testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore


class TestWithInitialHooks(unittest.TestCase):
    container_name: str = "alertmanager"

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @patch("socket.getfqdn", new=lambda *args: "fqdn")
    @k8s_resource_multipatch
    @patch("lightkube.core.client.GenericSyncClient")
    @patch.object(WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0"))
    def setUp(self, *unused):
        self.harness = Harness(AlertmanagerCharm)
        self.addCleanup(self.harness.cleanup)

        self.relation_id = self.harness.add_relation("alerting", "otherapp")
        self.harness.add_relation_unit(self.relation_id, "otherapp/0")
        self.harness.set_leader(True)

        self.harness.begin_with_initial_hooks()

    def test_num_peers(self):
        self.assertEqual(0, len(self.harness.charm.peer_relation.units))  # type: ignore

    @patch("socket.getfqdn", new=lambda *args: "fqdn")
    def test_pebble_layer_added(self, *unused):
        plan = self.harness.get_container_pebble_plan(self.container_name)

        # Check we've got the plan as expected
        self.assertIsNotNone(plan.services)
        self.assertIsNotNone(service := plan.services.get(self.harness.charm._service_name))
        self.assertIsNotNone(command := service.command)  # pyright: ignore

        # Check command is as expected
        self.assertEqual(
            plan.services, self.harness.charm.alertmanager_workload._alertmanager_layer().services
        )

        # Check command contains key arguments
        self.assertIn("--config.file", command)
        self.assertIn("--storage.path", command)
        self.assertIn("--web.listen-address", command)
        self.assertIn("--cluster.listen-address", command)

        # Check the service was started
        service = self.harness.model.unit.get_container("alertmanager").get_service("alertmanager")
        self.assertTrue(service.is_running())

    @patch("socket.getfqdn", new=lambda *args: "fqdn")
    def test_relation_data_provides_public_address(self):
        # to suppress mypy error: Item "None" of "Optional[Any]" has no attribute "get_relation"
        model = self.harness.charm.framework.model
        assert model is not None

        rel = model.get_relation("alerting", self.relation_id)
        assert rel is not None  # for static checker
        expected_address = "fqdn:{}".format(self.harness.charm.api_port)
        expected_rel_data = {
            "url": "http://fqdn:9093",
            "public_address": expected_address,
            "scheme": "http",
        }
        self.assertEqual(expected_rel_data, rel.data[self.harness.charm.unit])

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    @patch.object(AlertmanagerCharm, "_update_ca_certs", lambda *a, **kw: None)
    def test_topology_added_if_user_provided_config_without_group_by(self, *unused):
        new_config = yaml.dump({"not a real config": "but good enough for testing"})
        self.harness.update_config({"config_file": new_config})
        updated_config = yaml.safe_load(
            self.harness.charm.container.pull(self.harness.charm._config_path)
        )

        self.assertEqual(updated_config["not a real config"], "but good enough for testing")
        self.assertListEqual(
            sorted(updated_config["route"]["group_by"]),
            sorted(["juju_model", "juju_application", "juju_model_uuid"]),
        )

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    @patch.object(AlertmanagerCharm, "_update_ca_certs", lambda *a, **kw: None)
    def test_topology_added_if_user_provided_config_with_group_by(self, *unused):
        new_config = yaml.dump({"route": {"group_by": ["alertname", "juju_model"]}})
        self.harness.update_config({"config_file": new_config})
        updated_config = yaml.safe_load(
            self.harness.charm.container.pull(self.harness.charm._config_path)
        )

        self.assertListEqual(
            sorted(updated_config["route"]["group_by"]),
            sorted(["alertname", "juju_model", "juju_application", "juju_model_uuid"]),
        )

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    @patch.object(AlertmanagerCharm, "_update_ca_certs", lambda *a, **kw: None)
    def test_topology_is_not_added_if_user_provided_config_with_ellipsis(self, *unused):
        """The special value '...' effectively disables aggregation entirely.

        Ref: https://prometheus.io/docs/alerting/latest/configuration/#route
        """
        new_config = yaml.dump({"route": {"group_by": ["..."]}})
        self.harness.update_config({"config_file": new_config})
        updated_config = yaml.safe_load(
            self.harness.charm.container.pull(self.harness.charm._config_path)
        )

        self.assertListEqual(
            updated_config["route"]["group_by"],
            sorted(["..."]),
        )

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    @patch.object(AlertmanagerCharm, "_update_ca_certs", lambda *a, **kw: None)
    def test_charm_blocks_if_user_provided_config_with_templates(self, *unused):
        new_config = yaml.dump({"templates": ["/what/ever/*.tmpl"]})
        self.harness.update_config({"config_file": new_config})
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        new_config = yaml.dump({})
        self.harness.update_config({"config_file": new_config})
        self.assertIsInstance(self.harness.charm.unit.status, ActiveStatus)

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    @patch.object(AlertmanagerCharm, "_update_ca_certs", lambda *a, **kw: None)
    def test_templates_file_not_created_if_user_provides_templates_without_config(self, *unused):
        templates = '{{ define "some.tmpl.variable" }}whatever it is{{ end}}'
        self.harness.update_config({"templates_file": templates})

        # The testing harness's pull() used to raise FileNotFoundError, but
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 42s</sub>

### ✅ `bash`

**Look at unit test conftest and helpers**

$ cat /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py && echo "---" && head -50 /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/helpers.py

<details>
<summary>72 lines</summary>

```
from unittest.mock import patch

import pytest
from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
from ops.testing import Context

from src.alertmanager import WorkloadManager
from src.charm import AlertmanagerCharm


@pytest.fixture(autouse=True)
def patch_buffer_file_for_charm_tracing(tmp_path):
    with patch(
        "charms.tempo_coordinator_k8s.v0.charm_tracing.BUFFER_DEFAULT_CACHE_FILE_NAME",
        str(tmp_path / "foo.json"),
    ):
        yield


@pytest.fixture(autouse=True)
def silence_tracing():
    with charm_tracing_disabled():
        yield


def tautology(*_, **__) -> bool:
    return True


@pytest.fixture(autouse=True)
def alertmanager_charm():
    with patch("lightkube.core.client.GenericSyncClient"), patch.multiple(
        "charm.KubernetesComputeResourcesPatch",
        _namespace="test-namespace",
        _patch=tautology,
        is_ready=tautology,
    ), patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", "")), patch.object(
        WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0")
    ), patch("subprocess.run"):
        yield AlertmanagerCharm


@pytest.fixture(scope="function")
def context(alertmanager_charm):
    return Context(charm_type=alertmanager_charm)
---
#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

"""Helper functions for writing tests."""

import dataclasses
from unittest.mock import patch

from ops.testing import Container, Context, Exec, PeerRelation, Relation, State


def no_op(*_, **__) -> None:
    pass


def tautology(*_, **__) -> bool:
    return True


def cli_arg(plan, cli_opt):
    plan_dict = plan.to_dict()
    args = plan_dict["services"]["alertmanager"]["command"].split()
    for arg in args:
        opt_list = arg.split("=")
        if len(opt_list) == 2 and opt_list[0] == cli_opt:
            return opt_list[1]
        if len(opt_list) == 1 and opt_list[0] == cli_opt:
            return opt_list[0]
    return None


k8s_resource_multipatch = patch.multiple(
    "charm.KubernetesComputeResourcesPatch",
    _namespace="test-namespace",
    _patch=tautology,
    is_ready=tautology,
)


def begin_with_initial_hooks_isolated(context: Context, *, leader: bool = True) -> State:
    container = Container(
        "alertmanager",
        can_connect=False,
        execs={
            Exec(["update-ca-certificates", "--fresh"]),
            Exec(
                ["alertmanager", "--version"],
                stdout="alertmanager, version 0.23.0 (branch: HEAD, ...",
            ),
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 42s</sub>

### ✅ `bash`

**Check which testing approaches are used**

$ grep -r "charm_spec\|Harness\|from ops.testing\|import scenario\|from scenario\|ops.testing.Context\|testing.Context" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/ --include="*.py" -l

<details>
<summary>12 lines</summary>

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_external_url.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_remote_configuration_requirer.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_remote_configuration_provider.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/helpers.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_charm.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_consumer.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_push_config_to_workload_on_startup.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_self_scrape_jobs.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_server_scheme.py
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_brute_isolated.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 49s</sub>

### ✅ `bash`

**Check ops-tracing install deps**

$ pip install ops-tracing --dry-run 2>&1 | head -5

<details>
<summary>5 lines</summary>

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 49s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/operator/blob/main/ops-tracing/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://github.com/canonical/operator/blob/main/ops-tracing/CHANGES.md"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/operator/blob/main/ops-tracing/CHANGES.md - status code 404
```


---

<sub>⏱️ 1m 54s</sub>

### ❌ `bash`

**Look at installed ops-tracing files**

$ pip show ops-tracing 2>/dev/null | grep Location && ls $(pip show ops-tracing 2>/dev/null | grep Location | awk '{print $2}')/ops_tracing/ 2>/dev/null || find /home/ubuntu/.local/lib -name "*.py" -path "*/ops_tracing/*" 2>/dev/null | head -10

```
Command blocked: contains dangerous shell expansion patterns (e.g., parameter transformation, indirect expansion, or nested command substitution) that could enable arbitrary code execution. Please rewrite the command without these expansion patterns.
```


---

<sub>⏱️ 1m 54s</sub>

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

<sub>⏱️ 2m 0s</sub>

### ❌ `bash`

**Find ops-tracing files**

$ find /home/ubuntu/.local/lib -name "*.py" -path "*/ops_tracing/*" 2>/dev/null | head -10 && find /usr/lib -name "*.py" -path "*/ops_tracing/*" 2>/dev/null | head -10

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 2m 0s</sub>

### ✅ `web_fetch`

**https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md",
  "start_index": 15000
}
```

</details>

<details>
<summary>309 lines</summary>

```
Content type text/plain; charset=utf-8 cannot be simplified to markdown. Here is the raw content:
Contents of https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md:
nd lines in tox.ini (#1854)

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
* Live reload documentation with sphinx-autobuild in (#1323)

## Tests

* Update the smoke test series/bases in (#1318)
* Run pytest in parallel with pytest xdist in (#1319)
* Bump Pyright to 1.1.377 in (#1332)
* Run tests on Python 3.12 and the install test on Python 3.13 in (#1315)

## CI

* Add a workflow that runs the TIOBE quality checks in (#1301)
* Allow executing the TIOBE workflow manually in (#1321)
* Make Pyright report unnecessary type ignore comments in (#1333)
* Enable linting of docs/custom_conf.py in (#1330)

# 2.15.0 - 22 Jul 2024

## Features

* Add support for Pebble check-failed and check-recovered events (#1281)

## Fixes

* Pass secret data to Juju via files, rather than as command-line values (#1290) fixing CVE-2024-41129
* Include checks and log targets when merging layers in ops.testing (#1268)

## Documentation

* Clarify distinction between maintenance and waiting status (#1148)

## CI

* Bump the Go version to match Pebble (#1285)
* Run ruff format over charm pin update code (#1278)
* Bump certifi from 2024.2.2 to 2024.7.4 in /docs (#1282)
* Update charm pins (#1269)

# 2.14.1 - 27 Jun 2024

## Fixes

* Add connect timeout for exec websockets to avoid hanging (#1247)
* Adjust Harness secret behaviour to align with Juju (#1248)

## Tests

* Fix TypeError when running test.pebble_cli (#1245)
* Properly clean up after running setup_root_logging in test_log (#1259)
* Verify that defer() is not usable on stop,remove,secret-expired,secret-rotate (#1233)

## Documentation

* Fix HACKING.md link on PyPI, and internal links (#1261, #1236)
* Add a section to HACKING.md on PR titles (commit messages to main) (#1252)
* Add release step to update pinned charm tests (#1213)
* Add a security policy (#1266)

## CI

* Only run tests once on push to PR (#1242)
* Validate PR title against conventional commit rules in (#1262)
* Only update ops, not all dependencies, in charm tests in (#1275)
* Add artefact attestation (#1267)

# 2.14.0 - 29 May 2024

## Features

* Add a `__str__` to ActionFailed, for better unexpected failure output (#1209)

## Fixes

* The `other` argument to `RelatationDataContent.update(...)` should be optional (#1226)

## Documentation

* Use the actual emoji character rather than GitHub markup, to show properly on PyPI (#1221)
* Clarify that SecretNotFound may be raised for permission errors (#1231)

## Refactoring

* Refactor tests to pytest style (#1199, #1200, #1203, #1206)
* Use `ruff` formatter and reformat all code (#1224)
* Don't use f-strings in logging calls (#1227, 1234)

# 2.13.0 - 30 Apr 2024

## Features

* Added support for user secrets in Harness (#1176)

## Fixes

* Corrected the model config types (#1183)
* In Harness, only inspect the source file if it will be used - this fixed using Harness in a Python REPL (#1181)

## Documentation

* Updated publishing a release in HACKING.md (#1173)
* Added `tox -e docs-deps` to compile requirements.txt (#1172)
* Updated doc to note deprecated functionality in (#1178)

## Tests

* First stage of converting tests from unittest to pytest (#1191, #1192, #1196, #1193, #1195)
* Added `pebble.CheckInfo.change_id` field (#1197)

# 2.12.0 - 28 Mar 2024

## Features

* Added `Model.get_cloud_spec` which uses the `credential-get` hook command to get details of the cloud where the model is deployed (#1152)

## Fixes

* Update Pebble Notices `get_notices` parameter name to `users=all` (previously `select=all`) (#1146)
* Warn when an observer weakref is lost (#1142)
* More robust validation of observer signatures (#1147)
* Change `Model.relation.app` type from `Application|None` to `Application` (#1151)
* Fix attaching storage in Harness before `begin` (#1150)
* Fixed an issue where `pebble.Client.exec` might leak a `socket.timeout` (`builtins.TimeoutError`) exception (#1155)
* Add a consistency check and default network to `add_relation` (#1138)
* Don't special-case `get_relation` behaviour in `leader-elected` (#1156)
* Accept `type: secret` for config options (#1167)

## Refactoring

* Refactor main.py, creating a new `_Manager` class (#1085)

## Documentation

* Use "integrate with" rather than "relate to" (#1145)
* Updated code examples in the docstring of `ops.testing` from unittest to pytest style (#1157)
* Add peer relation details in `Harness.add_relation` docstring (#1168)
* Update Read the Docs Sphinx Furo theme to use Canonical's latest styling (#1163, #1164, #1165)

# 2.11.0 - 29 Feb 2024

## Features

* `StopEvent`, `RemoveEvent`, and all `LifecycleEvent`s are no longer deferrable, and will raise a `RuntimeError` if `defer()` is called on the event object (#1122)
* Add `ActionEve

<note>Content truncated. Call the fetch tool with a start_index of 30000 to get more content.</note>
```

</details>


---

<sub>⏱️ 2m 16s</sub>

### ✅ `bash`

**Read tox configuration**

$ cat /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tox.ini

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
lib_path = {toxinidir}/lib/charms/alertmanager_k8s
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
setenv =
  {[testenv]setenv}
  JUJU_VERSION=3.0.3
passenv = 
    PYTHONPATH
allowlist_externals =
  {[testenv]allowlist_externals}
  /usr/bin/env
commands =
    uv run {[vars]uv_flags} coverage run --source={[vars]src_path},{[vars]lib_path} -m pytest \
        {[vars]tst_path}/unit {posargs}
    uv run {[vars]uv_flags} coverage report

[testenv:integration]
description = Run integration tests
commands =
    uv run {[vars]uv_flags} pytest --exitfirst {[vars]tst_path}/integration {posargs}
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 16s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py (lines 100-250)

<details>
<summary>151 lines</summary>

```
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
```

</details>


---

<sub>⏱️ 2m 23s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py (lines 250-450)

<details>
<summary>201 lines</summary>

```
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
```

</details>


---

<sub>⏱️ 2m 24s</sub>

### ✅ `bash`

**List charm libs**

$ ls /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/

```
alertmanager_k8s  grafana_k8s	    karma_k8s		prometheus_k8s	       tls_certificates_interface
catalogue_k8s	  istio_beacon_k8s  observability_libs	tempo_coordinator_k8s  traefik_k8s
<exited with exit code 0>
```


---

<sub>⏱️ 2m 33s</sub>

### ✅ `bash`

**Look at tracing charm libs**

$ ls /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/tempo_coordinator_k8s/v0/

```
charm_tracing.py  tracing.py
<exited with exit code 0>
```


---

<sub>⏱️ 2m 33s</sub>

### ✅ `bash`

**Look at charm_tracing lib**

$ head -60 /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py

<details>
<summary>47 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""This charm library contains utilities to instrument your Charm with opentelemetry tracing data collection.

WARNING this library is deprecated and will be discontinued in 27.04.
Instead, please use the new `ops[tracing]` library.

See this migration guide: https://discourse.charmhub.io/t/18076
See this deprecation announcement: https://discourse.charmhub.io/t/19669
"""


def _remove_stale_otel_sdk_packages():
    """Hack to remove stale opentelemetry sdk packages from the charm's python venv.

    See https://github.com/canonical/grafana-agent-operator/issues/146 and
    https://bugs.launchpad.net/juju/+bug/2058335 for more context. This patch can be removed after
    this juju issue is resolved and sufficient time has passed to expect most users of this library
    have migrated to the patched version of juju.  When this patch is removed, un-ignore rule E402 for this file in the pyproject.toml (see setting
    [tool.ruff.lint.per-file-ignores] in pyproject.toml).

    This only has an effect if executed on an upgrade-charm event.
    """
    # all imports are local to keep this function standalone, side-effect-free, and easy to revert later
    import os

    if os.getenv("JUJU_DISPATCH_PATH") != "hooks/upgrade-charm":
        return

    import logging
    import shutil
    from collections import defaultdict

    from importlib_metadata import distributions

    otel_logger = logging.getLogger("charm_tracing_otel_patcher")
    otel_logger.debug("Applying _remove_stale_otel_sdk_packages patch on charm upgrade")
    # group by name all distributions starting with "opentelemetry_"
    otel_distributions = defaultdict(list)
    for distribution in distributions():
        name = distribution._normalized_name  # type: ignore
        if name.startswith("opentelemetry_"):
            otel_distributions[name].append(distribution)

    otel_logger.debug("Found %d opentelemetry distributions", len(otel_distributions))

    # If we have multiple distributions with the same name, remove any that have 0 associated files
    for name, distributions_ in otel_distributions.items():
        if len(distributions_) <= 1:
            continue

        otel_logger.debug(
            "Package %s has multiple (%d) distributions.", name, len(distributions_)
        )
        for distribution in distributions_:
            if not distribution.files:  # Not None or empty list
                path = distribution._path  # type: ignore
                otel_logger.info("Removing empty distribution of %s at %s.", name, path)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 45s</sub>

### ✅ `web_fetch`

**https://discourse.charmhub.io/t/18076**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://discourse.charmhub.io/t/18076"
}
```

</details>

<details>
<summary>78 lines</summary>

````
Contents of https://discourse.charmhub.io/t/18076:
`charm_tracing`, your trusted charm library for autoinstrumenting charm code and submitting charm traces to a distributed tracing backend such as Tempo is being deprecated, and replaced by less cowboy-coded, even more trusted native `ops` functionality.

Deprecation timeline:

*   now, we’ve released a `v0.8` that pops a friendly deprecation warning
*   next cycle (25.10) we’ll release a `v0.9` that raises a not-so-friendly exception

Luckily, migrating the base functionality isn’t difficult.

## [](#p-38027-before-1)Before

If you were using `charm_tracing`, your charm likely looked something like this:

```
# charmcraft.yaml
[...]

requires:
  charm-tracing:
    interface: tracing
  certificates:
    interface: tls-certificates
```

```
# charm.py

from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config

@trace_charm(
    tracing_endpoint="_charm_tracing_endpoint",
    server_cert="_charm_tracing_cert",
    extra_types=[TempoWorker],
)
class Foo(CharmBase):
    def __init__(...):
            self.charm_tracing = TracingEndpointRequirer(
                self, relation  _name="charm-tracing", protocols=["otlp_http"]
            )
        self._charm_tracing_endpoint, self._charm_tracing_cert = charm_tracing_config(
            self.charm_tracing, Path("/path/to/cacert")
        )
```

## [](#p-38027-after-2)After

In order to switch over to `ops[tracing]`, you will have to make the following changes:

```
# charmcraft.yaml
[...]

requires:
  charm-tracing:
    interface: tracing
  receive-ca-cert:
    interface: certificate_transfer
```

```
# charm.py

from ops.tracing import Tracing

class Foo(CharmBase):
    def __init__(...):
            self.tracing = Tracing(
                tracing_relation_name='charm-tracing', 
                ca_relation_name='receive-ca-cert'
            )
```

If your charm does not integrate with `tracing` directly but obtains a tracing ingestion endpoint by other means (such as a grafana-agent or opentelemetry collector integration, typically), `ops[tracing]` offers the `set_endpoint` API to directly configure a tracing endpoint traces will be pushed to.

```
# charm.py

from ops.tracing import set_destination

class Foo(CharmBase):
    def __init__(...):

        # obtain the tracing endpoint from a relation endpoint, charm config, or wherever 
        # don't forget the /v1/traces suffix!
        endpoint = "https://<hostname>/v1/traces"
        ops_tracing.set_destination(
            url=url,
            # optionally, pass a CA certificate for tls-encryption
            # ca=ca_cert
        )
```

Note that you’ll need to call `set_destination` _on every single event_ (we recommend using a reconciler).

## [](#p-38027-removing-the-charm_tracing-lib-and-its-dependencies-3)Removing the `charm_tracing` lib and its dependencies

Now you can delete the charm\_tracing charm lib and remove any direct dependencies you had on `opentelemetry-exporter-otlp-proto-http`, as that is now baked into `ops[tracing]`. You also don’t need the `tracing` or `certificate-exchange` charm libs (unless you’re using them directly in other ways as well!), because they too are baked into `ops[tracing]`.

## [](#p-38027-autoinstrumentation-changes-4)(Auto)Instrumentation changes

The good news is that `ops` is now natively instrumented and gives much better traces at all external IO endpoints (hook tool calls & pebble calls), as well at the charm event interface (every event fired on the charm has its own span).

The less good news is that the `charm_tracing` autoinstrumentation behaviour that automatically created a span for each public method on the charm class (and other objects you could point it to) is now gone for good.

The good news is that you can relatively easily use [otel’s python sdk](https://opentelemetry.io/docs/languages/python/getting-started/#traces) to manually instrument your critical paths. (Or write your own autoinstrumentation wrapper (or probably even somehow keep using or copy-pasta the one from the `charm_tracing` library), but you didn’t hear that from me.)
````

</details>


---

<sub>⏱️ 2m 39s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py (lines 450-600)

<details>
<summary>151 lines</summary>

```
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
```

</details>


---

<sub>⏱️ 2m 51s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py (lines 600-700)

<details>
<summary>71 lines</summary>

```
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
```

</details>


---

<sub>⏱️ 2m 52s</sub>

### ✅ `bash`

**Find all tracing references in charm.py**

$ grep -n "tracing\|TracingEndpoint\|charm_tracing\|trace_charm\|otlp" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py

<details>
<summary>9 lines</summary>

```
33:from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
34:from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
72:@trace_charm(
73:    tracing_endpoint="_charm_tracing_endpoint",
74:    server_cert="_charm_tracing_ca_cert",
186:        self._tracing = TracingEndpointRequirer(self, protocols=["otlp_http"])
187:        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
188:            self._tracing, self._ca_cert_path
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 58s</sub>

### ✅ `bash`

**Check charmcraft.yaml for tracing relation**

$ cat /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/charmcraft.yaml | grep -A5 -B2 "tracing\|certificates\|receive-ca\|cert"

<details>
<summary>28 lines</summary>

```
optional: true
    description: Add Alertmanager as an item to a Catalogue charm.
  certificates:
    interface: tls-certificates
    optional: true
    limit: 1
    description: |
      Certificate and key files for the alertmanager server to use to authenticate to client.
  tracing:
    interface: tracing
    optional: true
    limit: 1
    description: |
      Enables sending workload traces to a distributed tracing backend such as Tempo.
  service-mesh:
    limit: 1
    interface: service_mesh
    description: |
      Subscribe this charm into a service mesh and create authorization policies.
--
      OCI image for alertmanager. This charms makes the following assumptions about the image:
      - location of executable "alertmanager" is in the path
      - has `update-ca-certificates`
    upstream-source: ubuntu/alertmanager@sha256:822dd355903bd3ce7412502b7e4450c829a0b15e70ffa68381fc12630a6ed765  # renovate: oci-image tag: 0.31-24.04

config:
  options:
    config_file:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 58s</sub>

### ✅ `bash`

**Find tracing in charmcraft.yaml**

$ grep -rn "tracing\|charm_tracing\|charm-tracing" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/charmcraft.yaml

```
118:  tracing:
119:    interface: tracing
123:      Enables sending workload traces to a distributed tracing backend such as Tempo.
<exited with exit code 0>
```


---

<sub>⏱️ 3m 44s</sub>

### 💬 Copilot

Now I have enough information to create a plan. Let me look at what the new `ops.tracing` API looks like:

---

<sub>⏱️ 3m 45s</sub>

### ✅ `bash`

**Download ops 3.6.0 to inspect**

$ pip download ops==3.6.0 -d /tmp/ops_download --no-deps -q 2>&1 && ls /tmp/ops_download/ 2>/dev/null

```
ops-3.6.0-py3-none-any.whl
<exited with exit code 0>
```


---

<sub>⏱️ 3m 44s</sub>

### ✅ `bash`

**Check git status**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && git --no-pager log --oneline -3 && git --no-pager status

```
6101e73 (grafted, HEAD, origin/main, origin/HEAD, main) chore: update charm libraries (#394)
HEAD detached at 6101e73
nothing to commit, working tree clean
<exited with exit code 0>
```


---

<sub>⏱️ 3m 49s</sub>

### ✅ `bash`

**Inspect ops 3.6.0 for tracing module**

$ cd /tmp && unzip -q ops_download/ops-3.6.0-py3-none-any.whl -d ops_36 && ls ops_36/ops/ | grep -i trac

```
bash: unzip: command not found
<exited with exit code 127>
```


---

<sub>⏱️ 3m 55s</sub>

### ✅ `bash`

**List tracing files in ops 3.6.0**

$ cd /tmp && python3 -c "import zipfile; z=zipfile.ZipFile('ops_download/ops-3.6.0-py3-none-any.whl'); names=[n for n in z.namelist() if 'tracing' in n.lower() or 'testing' in n.lower()]; print('\n'.join(names))"

```
ops/testing.py
<exited with exit code 0>
```


---

<sub>⏱️ 4m 0s</sub>

### ✅ `bash`

**List all files in ops 3.6.0**

$ cd /tmp && python3 -c "import zipfile; z=zipfile.ZipFile('ops_download/ops-3.6.0-py3-none-any.whl'); names=[n for n in z.namelist()]; print('\n'.join(names))"

<details>
<summary>36 lines</summary>

```
ops/__init__.py
ops/_main.py
ops/charm.py
ops/framework.py
ops/jujucontext.py
ops/jujuversion.py
ops/log.py
ops/main.py
ops/model.py
ops/pebble.py
ops/py.typed
ops/storage.py
ops/testing.py
ops/version.py
ops/_private/__init__.py
ops/_private/harness.py
ops/_private/timeconv.py
ops/_private/yaml.py
ops/hookcmds/__init__.py
ops/hookcmds/_action.py
ops/hookcmds/_other.py
ops/hookcmds/_port.py
ops/hookcmds/_relation.py
ops/hookcmds/_secret.py
ops/hookcmds/_state.py
ops/hookcmds/_status.py
ops/hookcmds/_storage.py
ops/hookcmds/_types.py
ops/hookcmds/_utils.py
ops/lib/__init__.py
ops-3.6.0.dist-info/licenses/LICENSE.txt
ops-3.6.0.dist-info/METADATA
ops-3.6.0.dist-info/WHEEL
ops-3.6.0.dist-info/top_level.txt
ops-3.6.0.dist-info/RECORD
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 8s</sub>

### ✅ `bash`

**Inspect ops-tracing 3.6.0 package contents**

$ pip download ops-tracing==3.6.0 -d /tmp/ops_tracing_download --no-deps -q 2>&1 && ls /tmp/ops_tracing_download/ && python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/ops_tracing_download/ops_tracing-3.6.0-py3-none-any.whl'); print('\n'.join(z.namelist()))"

<details>
<summary>17 lines</summary>

```
ops_tracing-3.6.0-py3-none-any.whl
ops_tracing/__init__.py
ops_tracing/_api.py
ops_tracing/_backend.py
ops_tracing/_buffer.py
ops_tracing/_export.py
ops_tracing/_mock.py
ops_tracing/py.typed
ops_tracing/vendor/charms/certificate_transfer_interface/v1/certificate_transfer.py
ops_tracing/vendor/charms/tempo_coordinator_k8s/v0/tracing.py
ops_tracing/vendor/otlp_json/__init__.py
ops_tracing/vendor/otlp_json/py.typed
ops_tracing/vendor/otlp_json/readme.md
ops_tracing-3.6.0.dist-info/METADATA
ops_tracing-3.6.0.dist-info/WHEEL
ops_tracing-3.6.0.dist-info/RECORD
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 14s</sub>

### ✅ `bash`

**Read ops_tracing __init__.py**

$ python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/ops_tracing_download/ops_tracing-3.6.0-py3-none-any.whl'); print(z.read('ops_tracing/__init__.py').decode())"

<details>
<summary>73 lines</summary>

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
"""

from ._api import Tracing
from ._backend import mark_observed as _mark_observed
from ._backend import set_destination
from ._backend import setup as _setup
from ._backend import shutdown as _shutdown

__all__ = [
    'Tracing',
    '_mark_observed',
    '_setup',
    '_shutdown',
    'set_destination',
]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 19s</sub>

### ✅ `bash`

**Read ops_tracing _api.py**

$ python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/ops_tracing_download/ops_tracing-3.6.0-py3-none-any.whl'); print(z.read('ops_tracing/_api.py').decode())"

<details>
<summary>178 lines</summary>

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
        """Initialise the tracing service."""
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

<sub>⏱️ 4m 25s</sub>

### ✅ `bash`

**Read ops_tracing _mock.py for testing support**

$ python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/ops_tracing_download/ops_tracing-3.6.0-py3-none-any.whl'); print(z.read('ops_tracing/_mock.py').decode())"

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

<sub>⏱️ 4m 38s</sub>

### ✅ `bash`

**Check ops __init__.py for tracing exports**

$ python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/ops_download/ops-3.6.0-py3-none-any.whl'); content=z.read('ops/__init__.py').decode(); print(content[:3000])"

<details>
<summary>71 lines</summary>

```
# Copyright 2020 Canonical Ltd.
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

"""The API to respond to Juju events and manage the application.

This API provides core features to your charm, including:

- :class:`~ops.CharmBase`, the base class for charms and :class:`~ops.Object`,
  the base class for charm libraries.
- :class:`~ops.framework.EventBase` class and individual event types, like
  the :class:`~ops.ActionEvent` class.
- :class:`~ops.Framework` class, the main interface for the charm to `ops` library
  infrastructure, including:

  - :attr:`~ops.Framework.on` shorthand property used to
    :meth:`~ops.Framework.observe` and react to Juju events.
  - :attr:`~ops.Framework.model` attribute to get hold of the Model instance.

- :class:`~ops.model.Model` class that represents the Juju model, accessible as
  ``self.model`` in a charm, including:

  - :attr:`~ops.Model.app` attribute, representing the application associated
    with the charm.
  - :attr:`~ops.Model.unit` attribute, representing the unit of the application
    the charm is running on.
  - :attr:`~ops.Model.relations` attribute, which provides access to relations
    (integrations) defined in the charm, allowing interaction with other applications.

- :class:`~ops.Container` class to control Kubernetes workloads, including:

  - :meth:`~ops.Container.add_layer` and :meth:`~ops.Container.replan` methods
    to update Pebble configuration.
  - :meth:`~ops.Container.pull` and :meth:`~ops.Container.push` methods to copy
    data to and from a container, respectively.
  - :meth:`~ops.Container.exec` method to run arbitrary commands inside the
    container.

- :class:`~ops.StatusBase` class and individual status types, like the
  :class:`~ops.ActiveStatus` class.
"""

from __future__ import annotations

# The "from .X import Y" imports below don't explicitly tell Pyright (or MyPy)
# that those symbols are part of the public API, so we have to add __all__.
__all__ = [  # noqa: RUF022 `__all__` is not sorted
    '__version__',
    'main',
    'tracing',
    'pebble',
    # From charm.py
    'ActionEvent',
    'ActionMeta',
    'CharmBase',
    'CharmEvents',
    'CharmMeta',
    'CollectMetricsEvent',
    'CollectStatusEvent',
    'ConfigChangedEvent',
    'ConfigMeta',
    'ContainerBase',
    'ContainerMeta',
    'ContainerStorageMeta',
    'HookEvent',
    'InstallEvent',
    'JujuAssumes',
    'JujuAssumesCondition',
    'LeaderElectedEvent',
    'LeaderSettingsChangedEvent',
    'MetadataLin
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 38s</sub>

### ✅ `bash`

**Check rest of ops __init__.py**

$ python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/ops_download/ops-3.6.0-py3-none-any.whl'); content=z.read('ops/__init__.py').decode(); print(content[3000:])"

<details>
<summary>288 lines</summary>

```
ks',
    'PayloadMeta',
    'PebbleCheckEvent',
    'PebbleCheckFailedEvent',
    'PebbleCheckRecoveredEvent',
    'PebbleCustomNoticeEvent',
    'PebbleNoticeEvent',
    'PebbleReadyEvent',
    'PostSeriesUpgradeEvent',
    'PreSeriesUpgradeEvent',
    'RelationBrokenEvent',
    'RelationChangedEvent',
    'RelationCreatedEvent',
    'RelationDepartedEvent',
    'RelationEvent',
    'RelationJoinedEvent',
    'RelationMeta',
    'RelationRole',
    'RemoveEvent',
    'RemoteModel',
    'ResourceMeta',
    'SecretChangedEvent',
    'SecretEvent',
    'SecretExpiredEvent',
    'SecretRemoveEvent',
    'SecretRotateEvent',
    'StartEvent',
    'StopEvent',
    'StorageAttachedEvent',
    'StorageDetachingEvent',
    'StorageEvent',
    'StorageMeta',
    'UpdateStatusEvent',
    'UpgradeCharmEvent',
    'WorkloadEvent',
    # From framework.py
    'BoundEvent',
    'BoundStoredState',
    'CommitEvent',
    'EventBase',
    'EventSource',
    'Framework',
    'FrameworkEvents',
    'Handle',
    'HandleKind',
    'LifecycleEvent',
    'NoTypeError',
    'Object',
    'ObjectEvents',
    'PreCommitEvent',
    'PrefixedEvents',
    'Serializable',
    'StoredDict',
    'StoredList',
    'StoredSet',
    'StoredState',
    'StoredStateData',
    # From hookcmds.py
    'StatusName',
    # From jujucontext.py
    'JujuContext',
    # From jujuversion.py
    'JujuVersion',
    # From model.py
    'ActiveStatus',
    'Application',
    'Binding',
    'BindingMapping',
    'BlockedStatus',
    'CheckInfoMapping',
    'CloudCredential',
    'CloudSpec',
    'ConfigData',
    'Container',
    'ContainerMapping',
    'ErrorStatus',
    'InvalidStatusError',
    'LazyCheckInfo',
    'LazyMapping',
    'LazyNotice',
    'MaintenanceStatus',
    'Model',
    'ModelError',
    'MultiPushPullError',
    'Network',
    'NetworkInterface',
    'OpenedPort',
    'Pod',
    'Port',
    'Relation',
    'RelationData',
    'RelationDataAccessError',
    'RelationDataContent',
    'RelationDataError',
    'RelationDataTypeError',
    'RelationMapping',
    'RelationNotFoundError',
    'Resources',
    'Secret',
    'SecretInfo',
    'SecretNotFoundError',
    'SecretRotate',
    'ServiceInfoMapping',
    'StatusBase',
    'Storage',
    'StorageMapping',
    'TooManyRelatedAppsError',
    'Unit',
    'UnknownStatus',
    'WaitingStatus',
]

# The isort command wants to rearrange the nicely-formatted imports below;
# just skip it for this file.
# isort:skip_file

# Import pebble explicitly. It's the one module we don't import names from below.
from . import pebble

# Also import charm explicitly. This is not strictly necessary as the
# "from .charm" import automatically does that, but be explicit since this
# import was here previously
from . import charm

from . import _main
from . import main as _legacy_main

# Explicitly import names from submodules so users can just "import ops" and
# then use them as "ops.X".
from .charm import (
    ActionEvent,
    ActionMeta,
    CharmBase,
    CharmEvents,
    CharmMeta,
    CollectMetricsEvent,
    CollectStatusEvent,
    ConfigChangedEvent,
    ConfigMeta,
    ContainerBase,
    ContainerMeta,
    ContainerStorageMeta,
    HookEvent,
    InstallEvent,
    JujuAssumes,
    JujuAssumesCondition,
    LeaderElectedEvent,
    LeaderSettingsChangedEvent,
    MetadataLinks,
    PayloadMeta,
    PebbleCheckEvent,
    PebbleCheckFailedEvent,
    PebbleCheckRecoveredEvent,
    PebbleCustomNoticeEvent,
    PebbleNoticeEvent,
    PebbleReadyEvent,
    PostSeriesUpgradeEvent,
    PreSeriesUpgradeEvent,
    RelationBrokenEvent,
    RelationChangedEvent,
    RelationCreatedEvent,
    RelationDepartedEvent,
    RelationEvent,
    RelationJoinedEvent,
    RelationMeta,
    RelationRole,
    RemoveEvent,
    ResourceMeta,
    SecretChangedEvent,
    SecretEvent,
    SecretExpiredEvent,
    SecretRemoveEvent,
    SecretRotateEvent,
    StartEvent,
    StopEvent,
    StorageAttachedEvent,
    StorageDetachingEvent,
    StorageEvent,
    StorageMeta,
    UpdateStatusEvent,
    UpgradeCharmEvent,
    WorkloadEvent,
)

from .framework import (
    BoundEvent,
    BoundStoredState,
    CommitEvent,
    EventBase,
    EventSource,
    Framework,
    FrameworkEvents,
    Handle,
    HandleKind,
    LifecycleEvent,
    NoTypeError,
    Object,
    ObjectEvents,
    PreCommitEvent,
    PrefixedEvents,
    Serializable,
    StoredDict,
    StoredList,
    StoredSet,
    StoredState,
    StoredStateData,
)

from .hookcmds import StatusName
from .jujucontext import JujuContext
from .jujuversion import JujuVersion

from .model import (
    ActiveStatus,
    Application,
    Binding,
    BindingMapping,
    BlockedStatus,
    CheckInfoMapping,
    CloudCredential,
    CloudSpec,
    ConfigData,
    Container,
    ContainerMapping,
    ErrorStatus,
    InvalidStatusError,
    LazyCheckInfo,
    LazyMapping,
    LazyNotice,
    MaintenanceStatus,
    Model,
    ModelError,
    MultiPushPullError,
    Network,
    NetworkInterface,
    OpenedPort,
    Pod,
    Port,
    Relation,
    RelationData,
    RelationDataAccessError,
    RelationDataContent,
    RelationDataError,
    RelationDataTypeError,
    RelationMapping,
    RelationNotFoundError,
    RemoteModel,
    Resources,
    Secret,
    SecretInfo,
    SecretNotFoundError,
    SecretRotate,
    ServiceInfoMapping,
    StatusBase,
    Storage,
    StorageMapping,
    TooManyRelatedAppsError,
    Unit,
    UnknownStatus,
    WaitingStatus,
)

# NOTE: don't import testing or Harness here, as that's a test-time concern
# rather than a runtime concern.

from .version import version as __version__

try:
    # Note that ops_tracing vendors charm libs that depend on ops.
    # We import it last, after all re-exported symbols.
    import ops_tracing as tracing
except ImportError:
    tracing = None


class _Main:
    def __call__(
        self, charm_class: type[charm.CharmBase], use_juju_for_storage: bool | None = None
    ):
        return _main.main(charm_class=charm_class, use_juju_for_storage=use_juju_for_storage)

    def main(self, charm_class: type[charm.CharmBase], use_juju_for_storage: bool | None = None):
        return _legacy_main.main(
            charm_class=charm_class, use_juju_for_storage=use_juju_for_storage
        )


main = _Main()
"""Set up the charm and dispatch the observed event.

Recommended usage:

.. code-block:: python

    import ops

    class SomeCharm(ops.CharmBase): ...

    if __name__ == "__main__":
        ops.main(SomeCharm)

Args:
    charm_class: the charm class to instantiate and receive the event.
    use_juju_for_storage: whether to use controller-side storage.
        The default is ``False`` for most charms.
        Podspec charms that haven't previously used local storage and that
        are running on a new enough Juju default to controller-side storage,
        and local storage otherwise.
"""
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 8s</sub>

### ✅ `bash`

**Read charmcraft.yaml**

$ cat /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/charmcraft.yaml | head -200

<details>
<summary>180 lines</summary>

```
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
name: alertmanager-k8s
type: charm
summary: Alertmanager handles alerts sent by client applications.
description: >
  Alertmanager handles alerts sent by client applications such as the Prometheus server.
  It takes care of deduplicating, grouping, and routing them to the correct receiver integrations
  such as email, PagerDuty, or OpsGenie. It also takes care of silencing and inhibition of alerts.

links:
  documentation: https://discourse.charmhub.io/t/alertmanager-k8s-docs-index/5788
  website: https://charmhub.io/alertmanager-k8s
  source: https://github.com/canonical/alertmanager-k8s-operator
  issues: https://github.com/canonical/alertmanager-k8s-operator/issues

assumes:
  - k8s-api
  - juju >= 3.6

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

containers:
  alertmanager:  # container key used by pebble
    resource: alertmanager-image
    mounts:
      - storage: data
        # nflogs and silences files go here. With a mounted storage for silences, they persist
        # across container restarts.
        # This path is passed to alertmanager via the `--storage.path` cli argument.
        location: /alertmanager

storage:
  data:
    type: filesystem
    description: >
      Storage path passed to alertmanager via --storage.path argument and used for nflog and silences snapshot

provides:
  alerting:
    # The provider (alertmanager) adds the following key-value pair to the relation data bag of
    # every alertmanager unit:
    #   "public_address": <ip_address>:<port>
    interface: alertmanager_dispatch
    optional: true
    description: |
      Integrates with other charms to send notifications when alert rules are triggered.
  karma-dashboard:
    interface: karma_dashboard
    optional: true
    description: |
      Links an entire Alertmanager cluster to a Karma[1] dashboard.
      Scaling alertmanager would automatically cause karma to group alerts by cluster.

      [1] https://charmhub.io/karma-k8s
  self-metrics-endpoint:
    interface: prometheus_scrape
    optional: true
    description: |
      Exposes the Prometheus metrics endpoint providing telemetry about the Alertmanager instance.
  grafana-dashboard:
    interface: grafana_dashboard
    optional: true
    description: |
      Forwards the built-in Grafana dashboard(s) for monitoring Alertmanager.
  grafana-source:
    interface: grafana_datasource
    optional: true
    description: |
      Configures Grafana to be able to use this Alertmanager instance as a datasource.
  provide-cmr-mesh:  # server-side-for-cmr-mesh
    interface: cross_model_mesh
    description: |
      Allow cross-model applications to make HTTP requests to alertmanager via the service mesh.
      This relation provides additional data required by the service mesh to create cross-model authorization policies

      Announce a subset of juju topology to the other side because a CMR obfuscates identity.
      Each pair of charm would need a separate relation of this kind, e.g. otelcol to loki and to prom.

      To make use of this relation, you also must have either the service-mesh relation in place (e.g. istio-beacon) or
      have the istio-beacon enroll the entire model (via its config option).
      (The service_mesh charm library manages both of these relations.)

requires:
  ingress:
    interface: ingress
    optional: true
    limit: 1
    description: |
      Alertmanager typically needs a "per app" ingress, which is available in the traefik charm[1].

      [1] https://charmhub.io/traefik-k8s
  remote-configuration:
    interface: alertmanager_remote_configuration
    optional: true
    limit: 1
  catalogue:
    interface: catalogue
    optional: true
    description: Add Alertmanager as an item to a Catalogue charm.
  certificates:
    interface: tls-certificates
    optional: true
    limit: 1
    description: |
      Certificate and key files for the alertmanager server to use to authenticate to client.
  tracing:
    interface: tracing
    optional: true
    limit: 1
    description: |
      Enables sending workload traces to a distributed tracing backend such as Tempo.
  service-mesh:
    limit: 1
    interface: service_mesh
    description: |
      Subscribe this charm into a service mesh and create authorization policies.
      We forward to the beacon our authorization policies.
      The beacon sends the pod and service labels required by this charm to join the mesh.
      This relation is a pre-requisite for using the provide-cmr-mesh relation.
  require-cmr-mesh:
    # TODO: remove this relation when this is fixed:
    #   https://github.com/canonical/istio-beacon-k8s-operator/issues/91
    interface: cross_model_mesh
    description: |
      Allow a cross-model application access to alertmanager via the service mesh.
      This relation provides additional data required by the service mesh to enforce cross-model authorization policies.

peers:
  replicas:
    interface: alertmanager_replica
    # assumed network type: private

resources:
  alertmanager-image:
    type: oci-image
    description: |
      OCI image for alertmanager. This charms makes the following assumptions about the image:
      - location of executable "alertmanager" is in the path
      - has `update-ca-certificates`
    upstream-source: ubuntu/alertmanager@sha256:822dd355903bd3ce7412502b7e4450c829a0b15e70ffa68381fc12630a6ed765  # renovate: oci-image tag: 0.31-24.04

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 41s</sub>

### ℹ️ Info

Request failed due to a transient API error. Retrying...

---

<sub>⏱️ 6m 7s</sub>

### ℹ️ Info

Request failed due to a transient API error. Retrying...

---

<sub>⏱️ 6m 25s</sub>

### ✅ `bash`

**Find tracing lib references in tests**

$ grep -rn "tempo_coordinator_k8s\|charm_tracing\|TracingEndpoint" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/ --include="*.py"

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py:4:from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py:12:def patch_buffer_file_for_charm_tracing(tmp_path):
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py:14:        "charms.tempo_coordinator_k8s.v0.charm_tracing.BUFFER_DEFAULT_CACHE_FILE_NAME",
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py:22:    with charm_tracing_disabled():
<exited with exit code 0>
```


---

<sub>⏱️ 6m 25s</sub>

### ✅ `bash`

**Find all tracing lib references in src**

$ grep -rn "tempo_coordinator_k8s\|charm_tracing\|TracingEndpoint\|trace_charm" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/ --include="*.py"

<details>
<summary>8 lines</summary>

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py:33:from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py:34:from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py:72:@trace_charm(
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py:73:    tracing_endpoint="_charm_tracing_endpoint",
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py:74:    server_cert="_charm_tracing_ca_cert",
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py:186:        self._tracing = TracingEndpointRequirer(self, protocols=["otlp_http"])
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py:187:        self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 40s</sub>

### 💬 Copilot

Now I have everything I need. Let me create the plan and implement changes:

---

<sub>⏱️ 6m 40s</sub>

### ✅ `sql`

**Create todos for the upgrade**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create todos for the upgrade",
  "query": "INSERT INTO todos (id, title, description, status) VALUES\n  ('branch', 'Create upgrade branch', 'Create a new git branch for the ops upgrade', 'pending'),\n  ('python-version', 'Update Python version requirement', 'Update requires-python from ~=3.8 to >=3.10 in pyproject.toml; update pythonVersion in pyright config; update target-version in ruff/black', 'pending'),\n  ('deps-update', 'Update ops dependency', 'Replace \"ops\" + \"opentelemetry-exporter-otlp-proto-http>=1.21.0\" with \"ops[tracing]>=3.0\" in pyproject.toml', 'pending'),\n  ('tracing-charm', 'Migrate charm.py to ops[tracing]', 'Remove @trace_charm decorator, TracingEndpointRequirer, charm_tracing_config; add ops.tracing.Tracing(self, tracing_relation_name=\"tracing\", ca_relation_name=\"receive-ca-cert\")', 'pending'),\n  ('tracing-charmcraft', 'Add receive-ca-cert relation', 'Add receive-ca-cert relation (interface: certificate_transfer) to charmcraft.yaml requires section', 'pending'),\n  ('tracing-libs', 'Remove deprecated charm libs', 'Delete lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py and lib/charms/tempo_coordinator_k8s/v0/tracing.py', 'pending'),\n  ('tracing-tests', 'Update unit test conftest for tracing', 'Replace charm_tracing_disabled() fixtures with ops.tracing._mock.patch_tracing()', 'pending'),\n  ('scenario-bare', 'Add SCENARIO_BARE_CHARM_ERRORS', 'Add SCENARIO_BARE_CHARM_ERRORS=true to the unit testenv in tox.ini to get cleaner error output in scenario tests', 'pending'),\n  ('lock', 'Update uv.lock', 'Run uv lock to update uv.lock with new dependencies', 'pending'),\n  ('tests', 'Run tests', 'Run unit tests to verify all changes work', 'pending'),\n  ('commit', 'Commit changes', 'Make a git commit with all changes on the upgrade branch', 'pending');"
}
```

</details>

```
11 row(s) inserted. Last inserted row ID: 11.
```


---

<sub>⏱️ 6m 46s</sub>

### ✅ `bash`

**Create upgrade branch**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && git checkout -b ops-upgrade-3.6.0 && git --no-pager branch

```
Switched to a new branch 'ops-upgrade-3.6.0'
  main
* ops-upgrade-3.6.0
<exited with exit code 0>
```


---

<sub>⏱️ 6m 53s</sub>

### ✅ `sql`

**Mark branch todo done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark branch todo done",
  "query": "UPDATE todos SET status = 'done' WHERE id = 'branch';"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 7m 0s</sub>

### 💬 Copilot

Now let me implement all the changes. I'll do them in parallel where possible:

---

<sub>⏱️ 7m 0s</sub>

### ✅ `sql`

**Mark todos in progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark todos in progress",
  "query": "UPDATE todos SET status = 'in_progress' WHERE id IN ('python-version', 'deps-update', 'tracing-charm', 'tracing-charmcraft', 'tracing-libs', 'tracing-tests', 'scenario-bare');"
}
```

</details>

```
7 row(s) updated.
```


---

<sub>⏱️ 7m 8s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 7m 8s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 7m 20s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 7m 20s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 7m 26s</sub>

### 💬 Copilot

Now update charm.py to remove the deprecated tracing libs and use the new ops.tracing API:

---

<sub>⏱️ 7m 26s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 33s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 39s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 45s</sub>

### 💬 Copilot

Now add the `receive-ca-cert` relation to charmcraft.yaml:

---

<sub>⏱️ 7m 45s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/charmcraft.yaml.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/charmcraft.yaml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/charmcraft.yaml updated with changes.
```


---

<sub>⏱️ 7m 50s</sub>

### 💬 Copilot

Now remove the deprecated charm lib files:

---

<sub>⏱️ 7m 51s</sub>

### ✅ `bash`

**Remove deprecated charm lib files**

$ rm /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/tempo_coordinator_k8s/v0/tracing.py && ls /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/tempo_coordinator_k8s/v0/

```

<exited with exit code 0>
```


---

<sub>⏱️ 7m 56s</sub>

### ✅ `bash`

**Check remaining tempo libs**

$ ls /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/tempo_coordinator_k8s/

```
v0
<exited with exit code 0>
```


---

<sub>⏱️ 8m 3s</sub>

### ✅ `bash`

**Remove empty tempo_coordinator_k8s directories**

$ find /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/tempo_coordinator_k8s -type f && rmdir /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/tempo_coordinator_k8s/v0 && rmdir /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/tempo_coordinator_k8s && ls /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/

```
alertmanager_k8s  grafana_k8s	    karma_k8s		prometheus_k8s		    traefik_k8s
catalogue_k8s	  istio_beacon_k8s  observability_libs	tls_certificates_interface
<exited with exit code 0>
```


---

<sub>⏱️ 8m 11s</sub>

### 💬 Copilot

Now update the test conftest.py:

---

<sub>⏱️ 8m 11s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py updated with changes.
```


---

<sub>⏱️ 8m 17s</sub>

### 💬 Copilot

Now update tox.ini to add `SCENARIO_BARE_CHARM_ERRORS`:

---

<sub>⏱️ 8m 17s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tox.ini.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tox.ini

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tox.ini updated with changes.
```


---

<sub>⏱️ 8m 23s</sub>

### ✅ `sql`

**Mark most todos done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark most todos done",
  "query": "UPDATE todos SET status = 'done' WHERE id IN ('python-version', 'deps-update', 'tracing-charm', 'tracing-charmcraft', 'tracing-libs', 'tracing-tests', 'scenario-bare');"
}
```

</details>

```
7 row(s) updated.
```


---

<sub>⏱️ 8m 29s</sub>

### 💬 Copilot

Now let me check if there are any remaining imports from the `from ops.charm` and `from ops.main` style (the charm uses old import paths) - these still work fine in ops 3.x, so I'll leave them. Let me also verify the charm.py changes look correct:

---

<sub>⏱️ 8m 29s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py (lines 1-95)

<details>
<summary>95 lines</summary>

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
33. import ops.tracing
34. from charms.tls_certificates_interface.v4.tls_certificates import (
35.     CertificateRequestAttributes,
36.     TLSCertificatesRequiresV4,
37. )
38. from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer
39. from ops.charm import ActionEvent, CharmBase
40. from ops.main import main
41. from ops.model import (
42.     ActiveStatus,
43.     BlockedStatus,
44.     MaintenanceStatus,
45.     OpenedPort,
46.     Relation,
47.     WaitingStatus,
48. )
49. from ops.pebble import PathError, ProtocolError  # type: ignore
50. 
51. from alertmanager import (
52.     ConfigFileSystemState,
53.     ConfigUpdateFailure,
54.     WorkloadManager,
55.     WorkloadManagerError,
56. )
57. from config_builder import ConfigBuilder, ConfigError
58. 
59. logger = logging.getLogger(__name__)
60. 
61. 
62. @dataclass
63. class TLSConfig:
64.     """TLS configuration received by the charm over the `certificates` relation."""
65. 
66.     server_cert: str
67.     ca_cert: str
68.     private_key: str
69. 
70. 
71. class AlertmanagerCharm(CharmBase):
72.     """A Juju charm for alertmanager."""
73. 
74.     # Container name must match metadata.yaml
75.     # Layer name is used for the layer label argument in container.add_layer
76.     # Service name matches charm name for consistency
77.     _container_name = _service_name = "alertmanager"
78.     _relations = SimpleNamespace(
79.         alerting="alerting", peer="replicas", remote_config="remote_configuration"
80.     )
81.     _ports = SimpleNamespace(api=9093, ha=9094)
82. 
83.     # path, inside the workload container, to the alertmanager and amtool configuration files
84.     # the amalgamated templates file goes in the same folder as the main configuration file
85.     _config_path = "/etc/alertmanager/alertmanager.yml"
86.     _web_config_path = "/etc/alertmanager/alertmanager-web-config.yml"
87.     _amtool_config_path = "/etc/amtool/config.yml"
88.     _templates_path = "/etc/alertmanager/templates.tmpl"
89. 
90.     _server_cert_path = "/etc/alertmanager/alertmanager.cert.pem"
91.     _key_path = "/etc/alertmanager/alertmanager.key.pem"
92.     _ca_cert_path = "/usr/local/share/ca-certificates/cos-ca.crt"
93. 
94.     def __init__(self, *args):
95.         super().__init__(*args)
```

</details>


---

<sub>⏱️ 8m 39s</sub>

### 💬 Copilot

I need to fix the import ordering - `import ops.tracing` should be near the other `ops` imports:

---

<sub>⏱️ 8m 39s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 8m 45s</sub>

### 💬 Copilot

Now update uv.lock:

---

<sub>⏱️ 8m 45s</sub>

### ✅ `sql`

**Mark lock todo in progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark lock todo in progress",
  "query": "UPDATE todos SET status = 'in_progress' WHERE id = 'lock';"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 8m 46s</sub>

### ✅ `bash`

**Update uv.lock**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && uv lock 2>&1 | tail -20

<details>
<summary>21 lines</summary>

```
Removed opentelemetry-exporter-otlp-proto-http v1.33.1
Removed opentelemetry-proto v1.33.1
Updated ops v2.21.1 -> v3.6.0
Updated ops-scenario v7.21.1 -> v8.6.0
Added ops-tracing v3.6.0
Removed pickleshare v0.7.5
Removed pkgutil-resolve-name v1.3.10
Updated pluggy v1.5.0, v1.6.0 -> v1.6.0
Updated pydantic v2.10.6, v2.11.5 -> v2.11.5
Updated pydantic-core v2.27.2, v2.33.2 -> v2.33.2
Updated pytest-httpserver v1.1.1, v1.1.3 -> v1.1.3
Updated referencing v0.35.1, v0.36.2 -> v0.36.2
Updated rpds-py v0.20.1, v0.25.1 -> v0.25.1
Updated sh v1.14.3, v2.2.2 -> v2.2.2
Updated tenacity v9.0.0, v9.1.2 -> v9.1.2
Updated urllib3 v2.2.3, v2.4.0 -> v2.4.0
Updated validators v0.34.0, v0.35.0 -> v0.35.0
Updated websockets v8.1, v9.1, v13.1 -> v13.1
Updated werkzeug v3.0.6, v3.1.3 -> v3.1.3
Updated zipp v3.20.2, v3.21.0 -> v3.21.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 51s</sub>

### ✅ `sql`

**Mark lock done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark lock done",
  "query": "UPDATE todos SET status = 'done' WHERE id = 'lock';"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 8m 56s</sub>

### 💬 Copilot

Now let's run the unit tests:

---

<sub>⏱️ 8m 56s</sub>

### ✅ `sql`

**Mark tests in progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark tests in progress",
  "query": "UPDATE todos SET status = 'in_progress' WHERE id = 'tests';"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 8m 59s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev pytest tests/unit/ -x -q 2>&1 | tail -40

<details>
<summary>10 lines</summary>

```
Installed 107 packages in 46ms
/home/ubuntu/.cache/uv/builds-v0/.tmpxcHf3I/lib/python3.12/site-packages/paramiko/pkey.py:82: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  "cipher": algorithms.TripleDES,
/home/ubuntu/.cache/uv/builds-v0/.tmpxcHf3I/lib/python3.12/site-packages/paramiko/transport.py:253: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  "class": algorithms.TripleDES,
ImportError while loading conftest '/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py'.
tests/unit/conftest.py:6: in <module>
    from src.alertmanager import WorkloadManager
E   ModuleNotFoundError: No module named 'src'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 12s</sub>

### ✅ `bash`

**Run tests via uv with correct env**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev pytest tests/unit/ -x -q --tb=short 2>&1 | grep -v "CryptographyDeprecation" | tail -50

<details>
<summary>8 lines</summary>

```
Installed 107 packages in 52ms
  "cipher": algorithms.TripleDES,
  "class": algorithms.TripleDES,
ImportError while loading conftest '/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py'.
tests/unit/conftest.py:6: in <module>
    from src.alertmanager import WorkloadManager
E   ModuleNotFoundError: No module named 'src'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 12s</sub>

### ✅ `bash`

**Run unit tests with correct PYTHONPATH**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && PYTHONPATH=/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4:/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib:/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src uv run --frozen --isolated --extra=dev pytest tests/unit/ -x -q --tb=short 2>&1 | grep -v "CryptographyDeprecation" | tail -60

<details>
<summary>10 lines</summary>

```
Installed 107 packages in 61ms
  "cipher": algorithms.TripleDES,
  "class": algorithms.TripleDES,
ImportError while loading conftest '/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/conftest.py'.
tests/unit/conftest.py:7: in <module>
    from src.charm import AlertmanagerCharm
src/charm.py:38: in <module>
    import ops.tracing
E   ModuleNotFoundError: No module named 'ops.tracing'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 24s</sub>

### ✅ `bash`

**Check if ops.tracing is available in uv env**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev python -c "import ops; print(ops.__version__); import ops.tracing; print('tracing ok')" 2>&1 | grep -v "Cryptography"

<details>
<summary>6 lines</summary>

```
Installed 107 packages in 54ms
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'ops.tracing'
3.6.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 31s</sub>

### ✅ `bash`

**Check uv.lock for ops packages**

$ grep "ops-tracing\|ops-scenario\|name = \"ops\"" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/uv.lock | head -20

<details>
<summary>14 lines</summary>

```
{ name = "ops", extra = ["tracing"] },
    { name = "ops", extra = ["testing"] },
    { name = "ops", extras = ["testing"], marker = "extra == 'dev'" },
    { name = "ops", extras = ["tracing"], specifier = ">=3.0" },
    { name = "ops" },
name = "ops"
    { name = "ops-scenario" },
    { name = "ops-tracing" },
name = "ops-scenario"
    { name = "ops" },
name = "ops-tracing"
    { name = "ops" },
    { name = "ops-scenario" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 32s</sub>

### ✅ `bash`

**Check if ops_tracing is importable**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev python -c "import ops_tracing; print('ops_tracing ok')" 2>&1 | grep -v "Cryptography"

```
Installed 107 packages in 52ms
ops_tracing ok
<exited with exit code 0>
```


---

<sub>⏱️ 9m 45s</sub>

### ✅ `bash`

**Test correct way to import ops.tracing**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev python -c "from ops import tracing; print(tracing.Tracing)" 2>&1 | grep -v "Cryptography"

```
Installed 107 packages in 46ms
<class 'ops_tracing._api.Tracing'>
<exited with exit code 0>
```


---

<sub>⏱️ 9m 51s</sub>

### 💬 Copilot

I need to fix the import - `ops.tracing` is an attribute, not a submodule:

---

<sub>⏱️ 9m 51s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py

```
No changes made: old_str and new_str are the same
```


---

<sub>⏱️ 9m 55s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py (lines 32-50)

<details>
<summary>19 lines</summary>

```
32. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
33. from charms.tls_certificates_interface.v4.tls_certificates import (
34.     CertificateRequestAttributes,
35.     TLSCertificatesRequiresV4,
36. )
37. from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer
38. import ops.tracing
39. from ops.charm import ActionEvent, CharmBase
40. from ops.main import main
41. from ops.model import (
42.     ActiveStatus,
43.     BlockedStatus,
44.     MaintenanceStatus,
45.     OpenedPort,
46.     Relation,
47.     WaitingStatus,
48. )
49. from ops.pebble import PathError, ProtocolError  # type: ignore
50.
```

</details>


---

<sub>⏱️ 10m 1s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 10m 7s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 12m 3s</sub>

### ✅ `bash`

**Run unit tests again**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && PYTHONPATH=/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4:/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib:/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/src uv run --frozen --isolated --extra=dev pytest tests/unit/ -x -q --tb=short 2>&1 | grep -v "CryptographyDeprecation\|cipher\|class" | tail -50

<details>
<summary>42 lines</summary>

```
/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/lib/charms/tls_certificates_interface/v4/tls_certificates.py:1289: DeprecationWarning: generate_private_key() is deprecated. Use PrivateKey.generate() instead.
    warnings.warn(

tests/unit/test_consumer.py::TestConsumer::test_cluster_is_empty_after_relation_breaks
tests/unit/test_consumer.py::TestConsumer::test_cluster_updated_after_alertmanager_unit_leaves
tests/unit/test_consumer.py::TestConsumer::test_cluster_updated_after_alertmanager_units_join
tests/unit/test_consumer.py::TestConsumer::test_relation_changed
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_consumer.py:60: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(SampleConsumerCharm, meta=SampleConsumerCharm.metadata_yaml)

tests/unit/test_push_config_to_workload_on_startup.py::TestPushConfigToWorkloadOnStartup::test_charm_blocks_on_connection_error
tests/unit/test_push_config_to_workload_on_startup.py::TestPushConfigToWorkloadOnStartup::test_single_unit_cluster
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_push_config_to_workload_on_startup.py:40: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_push_config_to_workload_on_startup.py::TestInvalidConfig::test_charm_blocks_on_invalid_config_changed
tests/unit/test_push_config_to_workload_on_startup.py::TestInvalidConfig::test_charm_blocks_on_invalid_config_on_startup
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_push_config_to_workload_on_startup.py:121: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_config_with_templates_updates_both_alertmanager_config_and_alertmanager_templates_in_the_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_config_without_templates_updates_only_alertmanager_config_in_the_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_empty_config_file_clears_relation_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_invalid_config_clears_relation_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_invalid_config_emits_remote_configuration_broken_event
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_remote_configuration_provider.py:87: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = testing.Harness(RemoteConfigurationProviderCharm, meta=METADATA)

tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_configs_available_from_both_relation_data_bag_and_charm_config_block_charm
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_invalid_config_pushed_to_the_relation_data_bag_does_not_update_alertmanager_config
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_templates_pushed_to_relation_data_bag_are_saved_to_templates_file_in_alertmanager
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_valid_config_pushed_to_relation_data_bag_updates_alertmanager_config
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_remote_configuration_requirer.py:52: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = testing.Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_no_peers
tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4/tests/unit/test_self_scrape_jobs.py:22: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/.cache/uv/builds-v0/.tmp9jJnFS/lib/python3.12/site-packages/ops/_private/harness.py:1109: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/1'.
    warnings.warn(

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/.cache/uv/builds-v0/.tmp9jJnFS/lib/python3.12/site-packages/ops/_private/harness.py:1109: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/2'.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====== 57 passed, 3 skipped, 4 xfailed, 311 warnings in 102.83s (0:01:42) ======
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12m 9s</sub>

### 💬 Copilot

All 57 tests pass. Now let me also run the linting to check the import ordering:

---

<sub>⏱️ 12m 10s</sub>

### ✅ `bash`

**Check import ordering with ruff**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev ruff check src/ tests/unit/conftest.py --select I001 2>&1 | head -20

```
Installed 107 packages in 49ms
All checks passed!
<exited with exit code 0>
```


---

<sub>⏱️ 12m 15s</sub>

### ✅ `bash`

**Full lint check**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && uv run --frozen --isolated --extra=dev ruff check src/ tests/unit/ 2>&1 | head -30

```
Installed 107 packages in 47ms
All checks passed!
<exited with exit code 0>
```


---

<sub>⏱️ 12m 21s</sub>

### 💬 Copilot

Clean. Now let me commit:

---

<sub>⏱️ 12m 21s</sub>

### ✅ `sql`

**Mark tests done, commit in progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark tests done, commit in progress",
  "query": "UPDATE todos SET status = 'done' WHERE id = 'tests';\nUPDATE todos SET status = 'in_progress' WHERE id = 'commit';"
}
```

</details>

<details>
<summary>5 lines</summary>

```
Executed 2 statement(s):

1. UPDATE
   1 row(s) updated.

2. UPDATE
   1 row(s) updated.
```

</details>


---

<sub>⏱️ 12m 21s</sub>

### ✅ `bash`

**Review all changed files**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && git --no-pager diff --stat HEAD

<details>
<summary>10 lines</summary>

```
charmcraft.yaml                                      |    9 +-
 lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py |  971 ------------------------------------------
 lib/charms/tempo_coordinator_k8s/v0/tracing.py       | 1010 --------------------------------------------
 pyproject.toml                                       |    9 +-
 src/charm.py                                         |   21 +-
 tests/unit/conftest.py                               |   15 +-
 tox.ini                                              |    1 +
 uv.lock                                              | 1319 ++++------------------------------------------------------
 8 files changed, 112 insertions(+), 3243 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12m 35s</sub>

### ✅ `bash`

**Commit all changes**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && git add -A && git commit -m "chore: upgrade to ops 3.6.0

- Bump ops from 2.x to ops[tracing]>=3.0 (resolves to 3.6.0)
- Drop Python 3.8/3.9 support (ops 3.0+ requires Python >=3.10)
- Migrate charm tracing from deprecated charm_tracing charmlib to
  the native ops[tracing] API (ops.tracing.Tracing). The old library
  warned it would be discontinued in 27.04 [1].
- Add receive-ca-cert relation (certificate_transfer interface) to
  charmcraft.yaml so ops.tracing.Tracing can validate the TLS
  connection to the tracing backend
- Remove deprecated charm libs: tempo_coordinator_k8s/v0/charm_tracing
  and tempo_coordinator_k8s/v0/tracing (now vendored by ops-tracing)
- Remove direct opentelemetry-exporter-otlp-proto-http dep (now
  bundled in ops-tracing)
- Update unit test fixtures: replace charm_tracing_disabled() with
  ops_tracing._mock.patch_tracing() for clean test isolation
- Set SCENARIO_BARE_CHARM_ERRORS=true in unit test env so scenario
  exceptions propagate as-is without UncaughtCharmError wrapping [2]

[1] https://discourse.charmhub.io/t/18076
[2] https://github.com/canonical/operator/pull/2142

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[ops-upgrade-3.6.0 4234a37] chore: upgrade to ops 3.6.0
 8 files changed, 112 insertions(+), 3243 deletions(-)
 delete mode 100644 lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py
 delete mode 100644 lib/charms/tempo_coordinator_k8s/v0/tracing.py
<exited with exit code 0>
```


---

<sub>⏱️ 12m 40s</sub>

### ✅ `sql`

**Mark commit done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark commit done",
  "query": "UPDATE todos SET status = 'done' WHERE id = 'commit';"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 12m 45s</sub>

### ✅ `bash`

**Verify final git log**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__ops-tracing__C4 && git --no-pager log --oneline -3

```
4234a37 (HEAD -> ops-upgrade-3.6.0) chore: upgrade to ops 3.6.0
6101e73 (grafted, origin/main, origin/HEAD, main) chore: update charm libraries (#394)
<exited with exit code 0>
```


---

<sub>⏱️ 12m 56s</sub>

### ✅ `task_complete`

**Created branch `ops-upgrade-3.6.0` with the following cha...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Created branch `ops-upgrade-3.6.0` with the following changes based on analysis of ops 2.23.2 → 3.6.0 release notes:\n\n**ops 3.0**: Dropped Python 3.8/3.9 — updated `requires-python` from `~=3.8` to `>=3.10`, and updated `pythonVersion`/`target-version` in pyright/ruff/black configs.\n\n**ops-tracing migration** (most impactful): The `charm_tracing` charmlib is explicitly deprecated (warning added in v0.8, exception planned for 27.04). Migrated to the native `ops[tracing]` API:\n- Replaced `@trace_charm` decorator + `TracingEndpointRequirer` + `charm_tracing_config` with `ops_tracing.Tracing(self, tracing_relation_name=\"tracing\", ca_relation_name=\"receive-ca-cert\")`\n- Added `receive-ca-cert` (interface: `certificate_transfer`) relation to `charmcraft.yaml`\n- Removed deprecated `lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py` and `tracing.py` (now vendored by `ops-tracing`)\n- Replaced `opentelemetry-exporter-otlp-proto-http` dep with `ops[tracing]>=3.0` (which bundles it)\n- Updated test conftest to use `ops_tracing._mock.patch_tracing()` instead of `charm_tracing_disabled()`\n\n**ops 3.5**: Added `SCENARIO_BARE_CHARM_ERRORS=true` to the unit test environment in `tox.ini` so scenario exceptions propagate without `UncaughtCharmError` wrapping.\n\nAll 57 unit tests pass; linting is clean."
}
```

</details>

<details>
<summary>10 lines</summary>

```
Created branch `ops-upgrade-3.6.0` with the following changes based on analysis of ops 2.23.2 → 3.6.0 release notes:

**ops 3.0**: Dropped Python 3.8/3.9 — updated `requires-python` from `~=3.8` to `>=3.10`, and updated `pythonVersion`/`target-version` in pyright/ruff/black configs.

**ops-tracing migration** (most impactful): The `charm_tracing` charmlib is explicitly deprecated (warning added in v0.8, exception planned for 27.04). Migrated to the native `ops[tracing]` API:
- Replaced `@trace_charm` decorator + `TracingEndpointRequirer` + `charm_tracing_config` with `ops_tracing.Tracing(self, tracing_relation_name="tracing", ca_relation_name="receive-ca-cert")`
- Added `receive-ca-cert` (interface: `certificate_transfer`) relation to `charmcraft.yaml`
- Removed deprecated `lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py` and `tracing.py` (now vendored by `ops-tracing`)
- Replaced `opentelemetry-exporter-otlp-proto-http` dep with `ops[tracing]>=3.0` (which bundles it)
- Updated test conftest to use `ops_tracing._mock.patch_tracing()` instead of `charm_tracing_disabled()`

**ops 3.5**: Added `SCENARIO_BARE_CHARM_ERRORS=true` to the unit test environment in `tox.ini` so scenario exceptions propagate without `UncaughtCharmError` wrapping.

All 57 unit tests pass; linting is clean.
```

</details>


---

<sub>⏱️ 12m 56s</sub>

### ✓ Task Complete

Created branch `ops-upgrade-3.6.0` with the following changes based on analysis of ops 2.23.2 → 3.6.0 release notes:

**ops 3.0**: Dropped Python 3.8/3.9 — updated `requires-python` from `~=3.8` to `>=3.10`, and updated `pythonVersion`/`target-version` in pyright/ruff/black configs.

**ops-tracing migration** (most impactful): The `charm_tracing` charmlib is explicitly deprecated (warning added in v0.8, exception planned for 27.04). Migrated to the native `ops[tracing]` API:
- Replaced `@trace_charm` decorator + `TracingEndpointRequirer` + `charm_tracing_config` with `ops_tracing.Tracing(self, tracing_relation_name="tracing", ca_relation_name="receive-ca-cert")`
- Added `receive-ca-cert` (interface: `certificate_transfer`) relation to `charmcraft.yaml`
- Removed deprecated `lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py` and `tracing.py` (now vendored by `ops-tracing`)
- Replaced `opentelemetry-exporter-otlp-proto-http` dep with `ops[tracing]>=3.0` (which bundles it)
- Updated test conftest to use `ops_tracing._mock.patch_tracing()` instead of `charm_tracing_disabled()`

**ops 3.5**: Added `SCENARIO_BARE_CHARM_ERRORS=true` to the unit test environment in `tox.ini` so scenario exceptions propagate without `UncaughtCharmError` wrapping.

All 57 unit tests pass; linting is clean.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
