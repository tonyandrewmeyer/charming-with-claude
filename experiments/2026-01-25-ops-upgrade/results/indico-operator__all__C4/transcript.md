# 🤖 Copilot CLI Session

> **Session ID:** `a121a659-cff5-4137-b9c9-c08f6cf9b4b4`
> **Duration:** 11m 0s
> **Exported:** 3/11/2026, 4:41:54 PM

<sub>⏱️ 4s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 11s</sub>

### ✅ `bash`

**Check current ops version and project config**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && cat requirements.txt && echo "---" && cat pyproject.toml | head -60

<details>
<summary>51 lines</summary>

```
pydantic==1.10.26
ops>=2.0.0,<3.0.0
---
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

[tool.bandit]
exclude_dirs = ["/venv/"]
[tool.bandit.assert_used]
skips = ["*/*test.py", "*/test_*.py", "*tests/*.py"]

# Testing tools configuration
[tool.coverage.run]
branch = true

# Formatting tools configuration
[tool.black]
line-length = 99
target-version = ["py38"]

[tool.coverage.report]
fail_under = 97
show_missing = true

# Linting tools configuration
[tool.flake8]
max-line-length = 99
max-doc-length = 99
max-complexity = 10
exclude = [".git", "__pycache__", ".tox", "build", "dist", "*.egg_info", "venv"]
select = ["E", "W", "F", "C", "N", "R", "D", "H"]
# Ignore W503, E501 because using black creates errors with this
# Ignore D107 Missing docstring in __init__
ignore = ["W503", "E501", "D107"]
# D100, D101, D102, D103: Ignore missing docstrings in tests
per-file-ignores = ["tests/*:D100,D101,D102,D103,D104,D205,D212,D415"]
docstring-convention = "google"
# Check for properly formatted copyright header in each file
copyright-check = "True"
copyright-author = "Canonical Ltd."
copyright-regexp = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+%(author)s"

[tool.isort]
line_length = 99
profile = "black"

[tool.mypy]
ignore_missing_imports = true
explicit_package_bases = true
namespace_packages = true

[tool.pylint]
disable = "wrong-import-order"

[tool.pytest.ini_options]
pythonpath = [
  "lib",
  "src"
]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11s</sub>

### ✅ `bash`

**Check installed ops version**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && pip show ops 2>/dev/null | grep Version

```
Version: 2.23.2
<exited with exit code 0>
```


---

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Check available ops versions**

$ pip index versions ops 2>/dev/null | head -5

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

**List Python source files**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && find . -name "*.py" | grep -v __pycache__ | grep -v ".tox" | head -20 && echo "---" && ls src/

<details>
<summary>24 lines</summary>

```
./lib/charms/observability_libs/v0/juju_topology.py
./lib/charms/redis_k8s/v0/redis.py
./lib/charms/nginx_ingress_integrator/v0/nginx_route.py
./lib/charms/data_platform_libs/v0/data_interfaces.py
./lib/charms/data_platform_libs/v0/s3.py
./lib/charms/loki_k8s/v0/loki_push_api.py
./lib/charms/grafana_k8s/v0/grafana_dashboard.py
./lib/charms/prometheus_k8s/v0/prometheus_scrape.py
./lib/charms/saml_integrator/v0/saml.py
./lib/charms/smtp_integrator/v0/smtp.py
./src/saml_observer.py
./src/smtp_observer.py
./src/database_observer.py
./src/state.py
./src/charm.py
./src/s3_observer.py
./indico_rock/plugins/anonymize/anonymize/plugin.py
./indico_rock/plugins/anonymize/anonymize/__init__.py
./indico_rock/plugins/anonymize/anonymize/cli.py
./indico_rock/plugins/anonymize/setup.py
---
charm.py	      grafana_dashboards      s3_observer.py	smtp_observer.py
database_observer.py  prometheus_alert_rules  saml_observer.py	state.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 24s</sub>

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

<sub>⏱️ 23s</sub>

### ✅ `bash`

**Read main charm file**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && cat src/charm.py

<details>
<summary>8 lines</summary>

```
Output too large to read at once (39.1 KB). Saved to: /tmp/copilot-tool-output-1773199877514-jqfkfl.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 29s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/releases",
  "start_index": 20000,
  "max_length": 20000
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

<sub>⏱️ 29s</sub>

### ✅ `bash`

**Read charm.py content**

$ cat /tmp/copilot-tool-output-1773199877514-jqfkfl.txt

<details>
<summary>8 lines</summary>

```
Output too large to read at once (39.1 KB). Saved to: /tmp/copilot-tool-output-1773199883635-kvoaui.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 34s</sub>

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

<sub>⏱️ 34s</sub>

### ✅ `bash`

**Read charm.py beginning**

$ cat /tmp/copilot-tool-output-1773199883635-kvoaui.txt | head -200

<details>
<summary>170 lines</summary>

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
        self.framework.observe(
            self.redis_cache.charm.on.redis_relation_updated, self._on_config_changed
        )
        self.framework.observe(
            self.on["indico-peers"].relation_departed, self._on_peer_relation_departed
        )
        self._require_nginx_route()

        self._metrics_endpoint = MetricsEndpointProvider(
            self,
            jobs=[
                {
                    "static_configs": [
                        {
                            "targets": [
                                f"*:{NGINX_PROMEXP_PORT}",
                                f"*:{STATSD_PROMEXP_PORT}",
                                f"*:{CELERY_PROMEXP_PORT}",
                            ]
                        }
                    ]
                }
            ],
        )
        self._grafana_dashboards = GrafanaDashboardProvider(self)
        # port 9080 conflicts with the nginx exporter
        charms.loki_k8s.v0.loki_push_api.HTTP_LISTEN_PORT = 9090
        self._logging = LogProxyConsumer(
            self,
            relation_name="logging",
            log_files="/srv/indico/log/*",
            container_name="indico",
        )

    def _require_nginx_route(self) -> None:
        """Require nginx ingress."""
        require_nginx_route(
            charm=self,
            service_hostname=self._get_external_hostname(),
            service_name=self.app.name,
            service_port=8080,
        )

    def _are_pebble_instances_ready(self) -> bool:
        """Check if all pebble instances are up and containers available.

        Returns:
            If the containers are up and available.
        """
        return all(
            self.unit.get_container(container_name).can_connect()
            for container_name in self.model.unit.containers
        )

    def _is_configuration_valid(self) -> Tuple[bool, str]:
        """Validate charm configuration.

        Returns:
            Tuple containing as first element whether the configuration is valid.
            and a string with the error, if any, as second element.
        """
        site_url = typing.cast(str, self.config["site_url"])
        if site_url and not urlparse(site_url).hostname:
            return False, "Configuration option site_url is not valid"
        return True, ""

    def _get_external_hostname(self) -> str:
        """Extract and return hostname from site_url or default to [application name].local.

        Returns:
            The site URL defined as part of the site_url configuration or a default value.
        """
        site_url = typing.cast(str, self.config["site_url"])
        if not site_url or not (hostname := urlparse(site_url).hostname):
            return f"{self.app.name}.local"
        return hostname

    def _get_external_scheme(self) -> str:
        """Extract and return schema from site_url.

        Returns:
            The HTTP schema.
        """
        site_url = typing.cast(str, self.config["site_url"])
        return urlparse(site_url).scheme if site_url else "http"

    def _get_external_port(self) -> Optional[int]:
        """Extract and return port from site_url.

        Returns:
            The port number.
        """
        site_url = typing.cast(str, self.config["site_url"])
        return urlparse(site_url).port

    def _are_relations_ready(self, _) -> bool:
        """Check if the needed relations are established.

        Returns:
            If the needed relations have been established.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 41s</sub>

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

<sub>⏱️ 41s</sub>

### ✅ `bash`

**Read charm.py end**

$ cat /tmp/copilot-tool-output-1773199883635-kvoaui.txt | tail -200

<details>
<summary>175 lines</summary>

```
def _refresh_external_resources(self, _) -> Dict:
        """Pull changes from the remote repository and upgrade external plugins.

        Returns:
            Dictionary containing the execution results for each of the operations executed.
        """
        results = {
            "customization-changes": False,
            "plugin-updates": [],
        }
        container = self.unit.get_container("indico")
        if container.can_connect():
            self._download_customization_changes(container)
            if self.config["customization_sources_url"]:
                logging.debug("Pulling changes from %s", self.config["customization_sources_url"])
                self._exec_cmd_in_custom_dir(
                    container,
                    ["git", "pull"],
                )
                logging.debug("Reloading uWSGI")
                self._exec_cmd_in_custom_dir(container, ["touch", UWSGI_TOUCH_RELOAD])
                results["customization-changes"] = True
            if self.config["external_plugins"]:
                logging.debug("Upgrading external plugins %s", self.config["external_plugins"])
                plugins = typing.cast(str, self.config["external_plugins"]).split(",")
                self._install_plugins(container, plugins)
                results["plugin-updates"] = plugins
        return results

    def _refresh_external_resources_action(self, event: ActionEvent) -> None:
        """Refresh external resources and report action result.

        Args:
            event: Event triggering the refresh action.
        """
        results = self._refresh_external_resources(event)
        event.set_results(results)

    def _on_leader_elected(self, _) -> None:
        """Handle leader-elected event."""
        peer_relation = self.model.get_relation("indico-peers")
        secret_value = repr(os.urandom(32))
        if (
            peer_relation
            and not self._has_secrets()
            and not peer_relation.data[self.app].get("secret-key")
        ):
            peer_relation.data[self.app].update({"secret-key": secret_value})
        elif (
            peer_relation
            and self._has_secrets()
            and not peer_relation.data[self.app].get("secret-id")
        ):
            secret = self.app.add_secret({"secret-key": secret_value})
            peer_relation.data[self.app].update({"secret-id": typing.cast(str, secret.id)})
        if peer_relation and not peer_relation.data[self.app].get("celery-unit"):
            peer_relation.data[self.app].update({"celery-unit": self.unit.name})

    def _on_peer_relation_departed(self, event: RelationDepartedEvent) -> None:
        """Handle the peer relation departed event.

        Args:
            event: the event triggering the handler.
        """
        peer_relation = self.model.get_relation("indico-peers")
        if (
            self.unit.is_leader()
            and peer_relation
            and event.departing_unit
            and peer_relation.data[self.app].get("celery-unit") == event.departing_unit.name
        ):
            if self.unit != event.departing_unit:
                peer_relation.data[self.app].update({"celery-unit": self.unit.name})
                container = self.unit.get_container("indico")
                if self._are_relations_ready(event) and container.can_connect():
                    self._config_pebble(container)
            else:
                # Leadership election will select a new celery-unit
                peer_relation.data[self.app].update({"celery-unit": ""})

    def _has_secrets(self) -> bool:
        """Check if current Juju version supports secrets.

        Returns:
            If secrets are supported or not.
        """
        juju_version = JujuVersion.from_environ()
        # Because we're only using secrets in a peer relation we don't need to
        # check if the other end of a relation also supports secrets...
        return juju_version.has_secrets

    def _add_admin_action(self, event: ActionEvent) -> None:
        """Add a new user to Indico.

        Args:
            event: Event triggered by the add_admin action
        """
        container = self.unit.get_container("indico")
        indico_env_config = self._get_indico_env_config_str(container)

        cmd = [
            "/usr/bin/indico",
            "autocreate",
            "admin",
            event.params["email"],
            event.params["password"],
        ]

        if container.can_connect():
            process = container.exec(
                cmd,
                user="indico",
                working_dir="/srv/indico",
                environment=indico_env_config,
            )
            try:
                output = process.wait_output()
                event.set_results({"user": f"{event.params['email']}", "output": output})
            except ExecError as ex:
                logger.exception("Action add-admin failed: %s", ex.stdout)

                event.fail(
                    # Parameter validation errors are printed to stdout
                    f"Failed to create admin {event.params['email']}: {ex.stdout!r}"
                )

    def _execute_anonymize_cmd(self, event: ActionEvent) -> Iterator[str]:
        """Execute anonymize command for each email.

        Args:
            event (ActionEvent): Event triggered by the anonymize-user action

        Yields:
            Iterator[str]: Output of each command execution
        """
        container = self.unit.get_container("indico")
        indico_env_config = self._get_indico_env_config_str(container)
        for email in event.params["email"].split(EMAIL_LIST_SEPARATOR):
            cmd = [
                "/usr/bin/indico",
                "anonymize",
                "user",
                email,
            ]

            if not container.can_connect():
                logger.error(
                    "Action anonymize-user failed: cannot connect to the Indico workload container"
                )
                self.unit.status = WaitingStatus(
                    "Waiting to be able to connect to workload container"
                )
                return

            process = container.exec(
                cmd,
                user="indico",
                working_dir="/srv/indico",
                environment=indico_env_config,
            )
            try:
                out = process.wait_output()
                yield out[0].replace("\n", "")
            except ExecError as ex:
                logger.exception("Action anonymize-user failed: %s", ex.stdout)
                fail_msg = f"Failed to anonymize user {event.params['email']}: {ex.stdout!r}"
                event.fail("Failed to anonymize one or more users, please verify the results.")
                yield fail_msg

    def _anonymize_user_action(self, event: ActionEvent) -> None:
        """Anonymize user in Indico.

        If find an error, the action will fail. All the results will be set until the error
        has happened.

        Args:
            event: Event triggered by the anonymize-user action
        """
        if len(event.params["email"].split(EMAIL_LIST_SEPARATOR)) > EMAIL_LIST_MAX:
            max_reached_msg = (
                "Failed to anonymize user: "
                f"List of more than {EMAIL_LIST_MAX} emails are not allowed"
            )
            logger.error("Action anonymize-user failed: %s", max_reached_msg)
            event.fail(max_reached_msg)
            return
        output_list = list(self._execute_anonymize_cmd(event))
        event.set_results(
            {
                "user": f"{event.params['email']}",
                "output": EMAIL_LIST_SEPARATOR.join(output_list),
            }
        )


if __name__ == "__main__":  # pragma: no cover
    main(IndicoOperatorCharm, use_juju_for_storage=True)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 46s</sub>

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

<sub>⏱️ 47s</sub>

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

<sub>⏱️ 52s</sub>

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

<sub>⏱️ 52s</sub>

### ✅ `bash`

**Read state.py**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && cat src/state.py

<details>
<summary>196 lines</summary>

```
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
    https_proxy: Optional[HttpUrl]
    no_proxy: Optional[str]

    @classmethod
    def from_env(cls) -> Optional["ProxyConfig"]:
        """Instantiate ProxyConfig from juju charm environment.

        Returns:
            ProxyConfig if proxy configuration is provided, None otherwise.
        """
        http_proxy = os.environ.get("JUJU_CHARM_HTTP_PROXY")
        https_proxy = os.environ.get("JUJU_CHARM_HTTPS_PROXY")
        no_proxy = os.environ.get("JUJU_CHARM_NO_PROXY")
        if not http_proxy and not https_proxy:
            return None
        # Mypy doesn't understand str is supposed to be converted to HttpUrl by Pydantic.
        return cls(
            http_proxy=http_proxy, https_proxy=https_proxy, no_proxy=no_proxy  # type: ignore
        )


class S3Config(BaseModel):  # pylint: disable=too-few-public-methods
    """S3 configuration.

    Attributes:
        bucket: the S3 bucket.
        host: S3 host.
        access_key: S3 access key.
        secret_key: S3 secret key.
    """

    bucket: str
    host: Optional[str]
    access_key: str
    secret_key: str

    def get_connection_string(self) -> str:
        """Retrieve a connection string for this instance.

        Returns: the connection string for this instance.
        """
        connection_string = (
            f"s3:bucket={self.bucket},access_key={self.access_key},"
            f"secret_key={self.secret_key},proxy=true"
        )
        if self.host:
            connection_string = f"{connection_string},host={self.host}"
        return connection_string


class SamlEndpoint(BaseModel):  # pylint: disable=too-few-public-methods
    """SAML configuration.

    Attributes:
        name: Endpoint name.
        url: Endpoint URL.
        binding: Endpoint binding.
        response_url: URL to address the response to.
    """

    name: str = Field(..., min_length=1)
    url: AnyHttpUrl
    binding: str = Field(..., min_length=1)
    response_url: Optional[AnyHttpUrl]


class SamlConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """SAML configuration.

    Attributes:
        entity_id: SAML entity ID.
        metadata_url: Metadata URL.
        certificates: List of x509 certificates.
        endpoints: List of endpoints.
    """

    entity_id: str = Field(..., min_length=1)
    metadata_url: AnyHttpUrl
    certificates: Tuple[str, ...]
    endpoints: Tuple[SamlEndpoint, ...]


class SmtpConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """SMTP configuration.

    Attributes:
        login: SMTP user.
        password: SMTP passwaord.
        port: SMTP port.
        host: SMTP host.
        use_tls: whether TLS is enabled.
    """

    login: Optional[str]
    password: Optional[str]
    port: int = Field(None, ge=1, le=65536)
    host: str = Field(..., min_length=1)
    use_tls: bool


@dataclasses.dataclass()
class State:  # pylint: disable=too-few-public-methods
    """The Indico operator charm state.

    Attributes:
        proxy_config: Proxy configuration.
        saml_config: SAML configuration.
        smtp_config: SMTP configuration.
        s3_config: S3 configuration.
    """

    proxy_config: Optional[ProxyConfig]
    saml_config: Optional[SamlConfig]
    smtp_config: Optional[SmtpConfig]
    s3_config: Optional[S3Config]

    # pylint: disable=unused-argument
    @classmethod
    def from_charm(
        cls,
        charm: ops.CharmBase,
        s3_relation_data: Optional[Dict[str, str]] = None,
        saml_relation_data: Optional[SamlRelationData] = None,
        smtp_relation_data: Optional[SmtpRelationData] = None,
    ) -> "State":
        """Initialize the state from charm.

        Args:
            charm: The charm root IndicoOperatorCharm.
            s3_relation_data: S3 relation data.
            saml_relation_data: SAML relation data.
            smtp_relation_data: SMTP relation data.

        Returns:
            Current state of Indico.

        Raises:
            CharmConfigInvalidError: if invalid state values were encountered.
        """
        try:
            saml_config = None
            if saml_relation_data:
                endpoints: List[SamlEndpoint] = []
                for endpoint in saml_relation_data.endpoints:
                    endpoints.append(
                        SamlEndpoint(
                            name=endpoint.name,
                            url=endpoint.url,
                            binding=endpoint.binding,
                            response_url=endpoint.response_url,
                        )
                    )
                saml_config = SamlConfig(
                    entity_id=saml_relation_data.entity_id,
                    metadata_url=saml_relation_data.metadata_url,
                    certificates=saml_relation_data.certificates,
                    endpoints=tuple(endpoints),
                )
            proxy_config = ProxyConfig.from_env()
            smtp_config = (
                SmtpConfig(
                    host=smtp_relation_data.host,
                    port=smtp_relation_data.port,
                    login=smtp_relation_data.user,
                    password=smtp_relation_data.password,
                    use_tls=smtp_relation_data.transport_security is not TransportSecurity.NONE,
                )
                if smtp_relation_data
                else None
            )
            s3_config = (
                S3Config(
                    bucket=s3_relation_data["bucket"],
                    host=s3_relation_data["endpoint"],
                    access_key=s3_relation_data["access-key"],
                    secret_key=s3_relation_data["secret-key"],
                )
                if s3_relation_data and "access-key" in s3_relation_data
                else None
            )
        except ValidationError as exc:
            logger.error("Invalid juju model proxy configuration, %s", exc)
            raise CharmConfigInvalidError("Invalid model proxy configuration.") from exc
        return cls(
            proxy_config=proxy_config,
            smtp_config=smtp_config,
            saml_config=saml_config,
            s3_config=s3_config,
        )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 0s</sub>

### ✅ `bash`

**List test files**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && ls tests/ && echo "---" && ls tests/unit/ 2>/dev/null || true && ls tests/integration/ 2>/dev/null || true

```
conftest.py  integration  unit	unit_harness  zap
---
__init__.py  conftest.py  test_on_leader_elected.py
__init__.py  conftest.py  test_actions.py  test_charm.py  test_loki.py	test_s3.py  test_saml.py
<exited with exit code 0>
```


---

<sub>⏱️ 1m 0s</sub>

### ✅ `bash`

**Read tox.ini**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && cat tox.ini

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

<sub>⏱️ 1m 12s</sub>

### ✅ `bash`

**Check test files for testing framework**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && head -50 tests/unit/test_charm.py && echo "---" && head -50 tests/unit_harness/test_charm.py 2>/dev/null || echo "NO HARNESS TESTS"

```
head: cannot open 'tests/unit/test_charm.py' for reading: No such file or directory
NO HARNESS TESTS
<exited with exit code 0>
```


---

<sub>⏱️ 1m 12s</sub>

### ✅ `bash`

**Check imports in unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && grep -r "from ops" tests/unit/ | head -20 && echo "---" && grep -r "Harness\|scenario\|ops.testing\|Context" tests/unit/ | head -20

```
tests/unit/conftest.py:from ops import pebble, testing
tests/unit/test_on_leader_elected.py:from ops import testing
---
tests/unit/test_on_leader_elected.py:    context = testing.Context(
<exited with exit code 0>
```


---

<sub>⏱️ 1m 17s</sub>

### ✅ `bash`

**Read unit test files**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && cat tests/unit/conftest.py && echo "---" && cat tests/unit/test_on_leader_elected.py

<details>
<summary>56 lines</summary>

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
---
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

<sub>⏱️ 1m 17s</sub>

### ✅ `bash`

**List unit test files**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && ls tests/unit/

```
__init__.py  conftest.py  test_on_leader_elected.py
<exited with exit code 0>
```


---

<sub>⏱️ 1m 39s</sub>

### 💬 Copilot

Now let me look at the ops-tracing releases and check the charm's full test suite:

---

<sub>⏱️ 1m 39s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/operator/releases/tag/ops-tracing-0.2.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://github.com/canonical/operator/releases/tag/ops-tracing-0.2.0"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/operator/releases/tag/ops-tracing-0.2.0 - status code 404
```


---

<sub>⏱️ 1m 40s</sub>

### ✅ `bash`

**Check for tracing references**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && grep -r "ops.tracing\|ops-tracing\|ops_tracing\|tracing" src/ requirements.txt tox.ini charmcraft.yaml 2>/dev/null | grep -v ".pyc" | head -30

```

<exited with exit code 0>
```


---

<sub>⏱️ 1m 44s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/ops-tracing/#history**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://pypi.org/project/ops-tracing/#history"
}
```

</details>

```
Contents of https://pypi.org/project/ops-tracing/#history:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 1m 44s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/ops-scenario/#history**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://pypi.org/project/ops-scenario/#history"
}
```

</details>

<details>
<summary>69 lines</summary>

```
Contents of https://pypi.org/project/ops-scenario/#history:
## ops-scenario, the unit testing framework for ops charms

`ops-scenario` is a Python library that provides state-transition testing for [Ops](https://documentation.ubuntu.com/ops/latest/) charms. These tests are higher level than typical unit tests, but run at similar speeds and are the recommended approach for testing charms within requiring a full [Juju](https://juju.is) installation.

Test are written in the arrange/act/assert pattern, arranging an object representing the current Juju state, acting by emulating an event from Juju, and then asserting on the (simulated) output Juju state.

## Writing tests

Here's a test that verifies that a unit is active after the `start` event, with a very minimal initial state:

from ops import testing

\# 'src/charm.py' typically contains the charm class.
from charm import MyCharm

def test\_start():
    ctx \= testing.Context(MyCharm)
    state\_in \= testing.State()
    state\_out \= ctx.run(ctx.on.start(), state\_in)
    assert state\_out.unit\_status \== testing.ActiveStatus()

More comprehensive tests will include relations, containers, secrets, and other components in the input state, and assertions against both the output state and the context. The 'act' stage remains a simple single call, although additional arguments may be required for the event, such as the relation or container that triggered it. For example:

import pytest
from ops import testing

from charm import MyCharm

@pytest.mark.parametrize(
    'leader',
    \[pytest.param(True, id\='leader'), pytest.param(False, id\='non-leader')\],
)
def test\_(leader: bool):
    \# Arrange:
    ctx \= testing.Context(MyCharm)
    relation \= testing.Relation('db', local\_app\_data\={'hostname': 'example.com'})
    peer\_relation \= testing.PeerRelation('peer')
    container \= testing.Container('workload', can\_connect\=True)
    relation\_secret \= testing.Secret({'certificate': 'xxxxxxxx'})
    user\_secret \= testing.Secret({'username': 'admin', 'password': 'xxxxxxxx'})
    config \= {'port': 8443, 'admin-credentials': 'secret:1234'}
    state\_in \= testing.State(
        leader\=leader,
        config\=config,
        relations\={relation, peer\_relation},
        containers\={container},
        secrets\={relation\_secret, user\_secret},
        unit\_status\=testing.BlockedStatus(),
        workload\_version\='1.0.1',
    )

    \# Act:
    state\_out \= ctx.run(ctx.on.relation\_changed(relation), state\_in)

    \# Assert:
    assert testing.JujuLogLine(level\='INFO', message\='Distributing secret.') in ctx.juju\_log
    peer\_relation\_out \= state\_out.get\_relation(peer\_relation.id)
    assert peer\_relation\_out.peers\_data\[0\] \== {'secret\_id': relation\_secret.id}

You don't have to use pytest for your charm tests, but it's what we recommend. pytest's `assert`\-based approach is a straightforward way to write tests, and its fixtures are helpful for structuring setup and teardown.

## Installation

For charm tests, install the testing framework by adding the `testing` extra of ops in your unit testing environment. For example, in `pyproject.toml`:

\[dependency-groups\]
test \= \['ops\[testing\]<4.0'\]

Ops checks if `ops-scenario` is installed, and, if so, makes the classes (such as `Context`, `State`, and `Relation`) available in the `ops.testing` namespace. Use `from ops import testing` rather than importing the `scenario` package.

`ops-scenario` supports the same platforms and Python versions as ops itself.

## Documentation

*   To get started, work through our ['Write your first Kubernetes charm' tutorial](https://documentation.ubuntu.com/ops/latest/tutorial/from-zero-to-hero-write-your-first-kubernetes-charm/create-a-minimal-kubernetes-charm/#write-unit-tests-for-your-charm), following the instructions for adding unit tests at the end of each chapter.
*   When you need to write a test that involves specific ops functionality, refer to our [how-to guides](https://documentation.ubuntu.com/ops/latest/howto/) which all conclude with examples of tests of the ops functionality.
*   Use our extensive [reference documentation](https://documentation.ubuntu.com/ops/latest/reference/ops-testing/#ops-testing) when you need to know how each `testing` object works. These docs are also available via the standard Python `help()` functionality and in your IDE.

[**Read the full documentation**](https://documentation.ubuntu.com/ops/latest/)

## Community

`ops-scenario` is a member of the Charming family. It's an open source project that warmly welcomes community contributions, suggestions, fixes and constructive feedback.

*   Read our [code of conduct](https://ubuntu.com/community/ethos/code-of-conduct): As a community we adhere to the Ubuntu code of conduct.
*   [Get support](https://discourse.charmhub.io/): Discourse is the go-to forum for all Ops-related discussions, including around testing.
*   Join our [online chat](https://matrix.to/#/#charmhub-charmdev:ubuntu.com): Meet us in the #charmhub-charmdev channel on Matrix.
*   [Report bugs](https://github.com/canonical/operator/issues): We want to know about the problems so we can fix them.
*   [Contribute docs](https://github.com/canonical/operator/blob/main/HACKING.md#contributing-documentation): Get started on GitHub.

## Contributing and developing

Anyone can contribute to ops and `ops-scenario`. It's best to start by [opening an issue](https://github.com/canonical/operator/issues) with a clear description of the problem or feature request, but you can also [open a pull request](https://github.com/canonical/operator/pulls) directly.

Read our [guide](./CONTRIBUTING.md) for more details on how to work on and contribute to `ops-scenario`.

Currently, releases of `ops-scenario` are done in lockstep with releases of ops itself, with matching minor and bugfix release numbers. The ops documentation outlines how to create a new release.
```

</details>


---

<sub>⏱️ 1m 51s</sub>

### ✅ `bash`

**Check ops-tracing and ops-scenario versions**

$ pip index versions ops-tracing 2>/dev/null | head -5 && pip index versions ops-scenario 2>/dev/null | head -5

<details>
<summary>7 lines</summary>

```
ops-tracing (3.6.0)
Available versions: 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 0.9.6, 0.9.4, 0.9.3, 0.9.2, 0.9.1, 0.9.0
ops-scenario (8.6.0)
Available versions: 8.6.0, 8.5.2, 8.5.1, 8.5.0, 8.4.0, 8.3.1, 8.3.0, 8.2.0, 8.1.0, 8.0.0, 7.23.2, 7.23.1, 7.23.0, 7.22.0, 7.21.1, 7.21.0, 7.20.0, 7.19.4, 7.2.0, 7.1.3, 7.1.2, 7.1.1, 7.0.5, 7.0.4, 7.0.3, 7.0.2, 7.0.1, 7.0.0, 6.1.7, 6.1.6, 6.1.5, 6.1.4, 6.1.3, 6.1.2, 6.1.1, 6.1.0, 6.0.5, 6.0.4, 6.0.3, 6.0.2, 6.0.1, 6.0, 5.8.1, 5.8, 5.7.1, 5.7, 5.6.2, 5.6.1, 5.6, 5.5, 5.4.1, 5.4, 5.3.1, 5.3, 5.2.2, 5.2.1, 5.2, 5.1.3, 5.1.2, 5.1.1, 5.1.0, 5.0, 4.0.4.1, 4.0.4, 4.0.3, 4.0.2, 4.0.1, 4.0, 3.1, 3.0.2, 3.0.1, 2.2, 2.1.3.5, 2.1.3.4, 2.1.3.3, 2.1.3.2, 2.1.3.1, 2.1.3, 2.1.2.5, 2.1.2.4, 2.1.2.3, 2.1.2.2, 2.1.2.1, 2.1.1, 2.1.0, 2.0.5, 2.0.4, 2.0.0
  INSTALLED: 7.23.2
  LATEST:    8.6.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 50s</sub>

### ✅ `bash`

**Find JujuVersion usage**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && grep -r "JujuVersion\|has_secrets" src/ tests/

<details>
<summary>32 lines</summary>

```
src/charm.py:from ops.jujuversion import JujuVersion
src/charm.py:        if not self._has_secrets():
src/charm.py:            and not self._has_secrets()
src/charm.py:            and self._has_secrets()
src/charm.py:    def _has_secrets(self) -> bool:
src/charm.py:        juju_version = JujuVersion.from_environ()
src/charm.py:        return juju_version.has_secrets
tests/unit/test_on_leader_elected.py:@patch.object(ops.JujuVersion, "from_environ")
tests/unit/test_on_leader_elected.py:    mock_juju_env.return_value = MagicMock(has_secrets=True)
tests/unit_harness/test_core.py:    @patch.object(ops.JujuVersion, "from_environ")
tests/unit_harness/test_core.py:        mock_juju_env.return_value = MagicMock(has_secrets=False)
tests/unit_harness/test_core.py:    @patch.object(ops.JujuVersion, "from_environ")
tests/unit_harness/test_core.py:        mock_juju_env.return_value = MagicMock(has_secrets=True)
tests/unit_harness/test_core.py:    @patch.object(ops.JujuVersion, "from_environ")
tests/unit_harness/test_core.py:        mock_juju_env.return_value = MagicMock(has_secrets=False)
tests/unit_harness/test_core.py:    @patch.object(ops.JujuVersion, "from_environ")
tests/unit_harness/test_core.py:        mock_juju_env.return_value = MagicMock(has_secrets=True)
tests/unit_harness/test_core.py:    @patch.object(ops.JujuVersion, "from_environ")
tests/unit_harness/test_core.py:        mock_juju_env.return_value = MagicMock(has_secrets=True)
tests/unit_harness/test_core.py:    @patch.object(ops.JujuVersion, "from_environ")
tests/unit_harness/test_core.py:        mock_juju_env.return_value = MagicMock(has_secrets=True)
tests/unit_harness/test_core.py:    @patch.object(ops.JujuVersion, "from_environ")
tests/unit_harness/test_core.py:        mock_juju_env.return_value = MagicMock(has_secrets=True)
tests/unit_harness/test_core.py:    @patch.object(ops.JujuVersion, "from_environ")
tests/unit_harness/test_core.py:        mock_juju_env.return_value = MagicMock(has_secrets=True)
tests/unit_harness/test_core.py:    @patch.object(ops.JujuVersion, "from_environ")
tests/unit_harness/test_core.py:        mock_juju_env.return_value = MagicMock(has_secrets=True)
tests/unit_harness/test_core.py:    @patch.object(ops.JujuVersion, "from_environ")
tests/unit_harness/test_core.py:        mock_juju_env.return_value = MagicMock(has_secrets=False)
tests/unit_harness/test_core.py:    @patch.object(ops.JujuVersion, "from_environ")
tests/unit_harness/test_core.py:        mock_juju_env.return_value = MagicMock(has_secrets=False)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 19s</sub>

### 💬 Copilot

Let me check the metadata and also look for the ops-tracing/ops-scenario changelog more carefully:

---

<sub>⏱️ 2m 20s</sub>

### ✅ `bash`

**Read metadata and charmcraft config**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && cat metadata.yaml && cat charmcraft.yaml

<details>
<summary>95 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

name: indico
display-name: Indico
summary: Indico web application.
description: |
  A [Juju](https://juju.is/) [charm](https://juju.is/docs/olm/charmed-operators)
  deploying and managing [Indico](https://getindico.io/) on Kubernetes. Indico is an
  open-source tool for event organisation, archival and collaboration.

  This charm simplifies initial deployment and "day N" operations of Indico
  on Kubernetes, such as scaling the number of instances, integration with SSO,
  access to S3 for redundant file storage and more. It allows for deployment on
  many different Kubernetes platforms, from [MicroK8s](https://microk8s.io) to
  [Charmed Kubernetes](https://ubuntu.com/kubernetes) and public cloud Kubernetes
  offerings.

  As such, the charm makes it easy for those looking to take control of their own
  events management system whilst keeping operations simple, and gives them the
  freedom to deploy on the Kubernetes platform of their choice.

  For DevOps or SRE teams this charm will make operating Indico simple and
  straightforward through Juju's clean interface. It will allow easy deployment
  into multiple environments for testing of changes, and supports scaling out for
  enterprise deployments.
docs: https://discourse.charmhub.io/t/indico-documentation-overview/7571
issues: https://github.com/canonical/indico-operator/issues
maintainers:
  - https://launchpad.net/~canonical-is-devops
source: https://github.com/canonical/indico-operator
assumes:
  - k8s-api
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
  database:
    interface: postgresql_client
    limit: 1
    optional: false
  nginx-route:
    interface: nginx-route
    limit: 1
    optional: false
  redis-broker:
    interface: redis
    limit: 1
    optional: false
  redis-cache:
    interface: redis
    limit: 1
    optional: false
  s3:
    interface: s3
    limit: 1
    optional: true
  saml:
    interface: saml
    limit: 1
    optional: true
  smtp-legacy:
    interface: smtp
    limit: 1
    optional: true
  logging:
    interface: loki_push_api
    optional: true

peers:
  indico-peers:
    interface: indico-instance
    optional: true
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# Learn more about charmcraft.yaml configuration at:
# https://juju.is/docs/sdk/charmcraft-config
type: "charm"
bases:
  - build-on:
    - name: "ubuntu"
      channel: "20.04"
    run-on:
    - name: "ubuntu"
      channel: "20.04"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 20s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/blob/main/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/blob/main/CHANGES.md"
}
```

</details>

<details>
<summary>200 lines</summary>

```
Contents of https://github.com/canonical/operator/blob/main/CHANGES.md:
## 3.6.0 - 26 February 2026

[](#360---26-february-2026)

## Features

[](#features)

*   Bump default Juju version in `ops.testing.Context` to 3.6.14 (#2316)

## Fixes

[](#fixes)

*   Correct the `Model.get_binding()` return type (#2329)
*   Only show executable in `ExecError.__str__`, not full command line (#2336)
*   Support Pydantic `MISSING` sentinel in `ops.Relation.save` (#2306)

## Documentation

[](#documentation)

*   Add how-to subcategory for managing containers (#2309)
*   Remove 2.19 version in docs, tweak ops.testing title (#2332)
*   Use "true" and "false" consistently in the reference documentation (#2330)
*   Add CLI args as another place to not put sensitive data (#2334)
*   Fix remote unit kwarg in testing example (#2342)
*   Clarify that secret labels are not names (#2337)

## Tests

[](#tests)

*   Set `SCENARIO_BARE_CHARM_ERRORS=true` in Ops tests that care (#2314)

## CI

[](#ci)

*   Fix releasing on branches with no `versions.md` doc (#2323)

## 3.5.2 - 11 February 2026

[](#352---11-february-2026)

## Fixes

[](#fixes-1)

*   Make testing.CheckInfo level arg type match pebble.CheckInfo.level (#2274)
*   Make testing consistency check aware that `credential-get` is available on k8s in newer Juju (#2307)
*   Drop unused `setuptools_scm` build dependency (#2310)

## Documentation

[](#documentation-1)

*   Update Pebble version in Juju 3.6 (#2295)
*   Refresh K8s tutorial to use Concierge and uv-based Charmcraft profile (#2285)
*   Add missing "How to" in page titles (#2289)
*   Fix and improve observability part of K8s tutorial (#2305)

## 3.5.1 - 28 January 2026

[](#351---28-january-2026)

## Fixes

[](#fixes-2)

*   Use `parse_rfc3339` for datetime parsing to support Juju 4 (#2264)
*   Correct the value of `additional_properties` in the action meta in Juju 4 (#2250)
*   Prevent `KeyError` on `auth-type` when creating `CloudCredential` object (#2268)
*   `_checks_action` should return empty list when there are no changes (#2270)

## Documentation

[](#documentation-2)

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

[](#tests-1)

*   Remove unnecessary test module (#2247)

## CI

[](#ci-1)

*   Replace git reference injection with wheel artifacts in charm test workflows (#2252)
*   Explicitly provide the charmcraft repo location in CI (#2277)
*   Remove outdated custom signature generation (#2280)

## 3.5.0 - 18 December 2025

[](#350---18-december-2025)

## Features

[](#features-1)

*   Env var to control exception wrapping in tests (#2142)
*   Deprecate testing.Context.charm\_spec (#2219)

## Documentation

[](#documentation-3)

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

[](#tests-2)

*   Don't skip tests if ops\[testing\] isn't installed (#2215)
*   Switch the integration test charms to use the uv plugin (#2218)

## CI

[](#ci-2)

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

[](#features-2)

*   Add a low-level API for the Juju hook commands (#2019)
*   Make PebbleClient file methods also accept pathlib.PurePath (#2097)
*   Log the total number of deferred events (#2161)
*   Allow setting the Juju availability zone and principal unit in the testing Context (#2187)

## Fixes

[](#fixes-3)

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

[](#documentation-4)

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

[](#tests-3)

*   Re-enable testing consistency checks after disabling them (#2141)
*   Expand secrets integration and state transition tests (#2130)

## Refactoring

[](#refactoring)

*   Use ops.hookcmds in \_ModelBackend (#2116)
*   Don't get the storage details from --help (#2172)
*   Drop 3.8 and 3.9 compatibility code (#2173)
*   Use json.dumps to produce the YAML in relation-set and state-set (#2174)
*   Rely on type annotations instead of casts in hookcmds (#2179)

## CI

[](#ci-3)

*   Add integration and state transition tests for the secrets API (#2078)
*   Temporarily disable tracing integration tests (#2102)
*   Add secrets tests follow-up (#2105)
*   Support monorepos in ops charm compatibility testing (#2100)
*   Test both Charmcraft 3 and Charmcraft 4 profiles (#2103)
*   Add automated doc checks (and related starter pack updates) (#2099)
*   Clean up accidental workflow trigger (#2144)
*   Test if package versions match dependency versions before publishing (#2139)
*   Update spelling (#2167)
*   Test against 4.0/stable (#2186)
*   Store charmcraft logs if smoke tests fail (#2192)
*   Use Juju channel 4/stable in Ops smoke tests (#2190)

## 3.3.0 - 29 September 2025

[](#330---29-september-2025)

## Features

[](#features-3)

*   Expose the Juju hook context in ops.JujuContext (#1996)

## Fixes

[](#fixes-4)

*   In testing, separate relation data cache from mock Juju backend (#2052)

## Documentation

[](#documentation-5)

*   Use uv for testing and packing the httpbin charm (#2011)
*   Improve intro to ops.testing reference (#2023)
*   In httpbin charm integration tests, add env var for charm file to deploy (#2018)
*   Update get\_cloud\_spec doc now that credential-get works on K8s (#2031)
*   Note that arbitrary\_types\_allowed is required when ops.Secret is used in a Pydantic class (#2038)
*   Clean up Resources.fetch docstring, add ModelError exception (#2039)
*   Note that the peer databag isn't usable during the install event (#2051)
*   Fix testing code in actions how-to guide (#2054)

## CI

[](#ci-4)

*   Nicer logging output in the release script using rich (#2017)
*   Clean up PYTHONPATH in tox.ini (#2058)

## 3

<note>Content truncated. Call the fetch tool with a start_index of 10000 to get more content.</note>
```

</details>


---

<sub>⏱️ 2m 30s</sub>

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

<sub>⏱️ 2m 30s</sub>

### ✅ `bash`

**Check harness test structure**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && cat tests/unit_harness/test_core.py | head -100

<details>
<summary>87 lines</summary>

```
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

<sub>⏱️ 2m 35s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/operator/tree/main/ops-tracing**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/tree/main/ops-tracing"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/operator/tree/main/ops-tracing - status code 404
```


---

<sub>⏱️ 2m 35s</sub>

### ✅ `bash`

**Check ops-tracing info**

$ pip show ops-tracing 2>/dev/null

```

<exited with exit code 1>
```


---

<sub>⏱️ 2m 39s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/ops-tracing/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://pypi.org/project/ops-tracing/"
}
```

</details>

```
Contents of https://pypi.org/project/ops-tracing/:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 2m 46s</sub>

### ✅ `bash`

**Check ops-tracing package info**

$ pip show ops-tracing --index-url https://pypi.org/simple 2>/dev/null || pip install ops-tracing==3.6.0 --dry-run 2>&1 | head -20

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 53s</sub>

### ✅ `bash`

**Download and examine ops-tracing package**

$ pip download ops-tracing==3.6.0 --no-deps -d /tmp/ops-tracing-pkg 2>/dev/null --break-system-packages && ls /tmp/ops-tracing-pkg/ && python3 -m zipfile -l /tmp/ops-tracing-pkg/*.whl 2>/dev/null | head -20

```

<exited with exit code 2>
```


---

<sub>⏱️ 2m 58s</sub>

### ✅ `bash`

**Download ops-tracing package**

$ pip download ops-tracing==3.6.0 --no-deps -d /tmp/ops-tracing-pkg --break-system-packages 2>&1 && ls /tmp/ops-tracing-pkg/ && python3 -m zipfile -l /tmp/ops-tracing-pkg/*.whl 2>/dev/null | head -20

<details>
<summary>8 lines</summary>

```
Usage:   
  pip download [options] <requirement specifier> [package-index-options] ...
  pip download [options] -r <requirements file> [package-index-options] ...
  pip download [options] <vcs project url> ...
  pip download [options] <local project path> ...
  pip download [options] <archive url/path> ...

no such option: --break-system-packages
<exited with exit code 2>
```

</details>


---

<sub>⏱️ 3m 4s</sub>

### ✅ `bash`

**Download ops-tracing package**

$ cd /tmp && pip download ops-tracing==3.6.0 --no-deps -d /tmp/ops-tracing-pkg 2>&1 | tail -5 && ls /tmp/ops-tracing-pkg/ && python3 -m zipfile -l /tmp/ops-tracing-pkg/*.whl 2>/dev/null | head -30

<details>
<summary>23 lines</summary>

```
Collecting ops-tracing==3.6.0
  Downloading ops_tracing-3.6.0-py3-none-any.whl.metadata (3.0 kB)
Downloading ops_tracing-3.6.0-py3-none-any.whl (31 kB)
Saved ./ops-tracing-pkg/ops_tracing-3.6.0-py3-none-any.whl
Successfully downloaded ops-tracing
ops_tracing-3.6.0-py3-none-any.whl
File Name                                             Modified             Size
ops_tracing/__init__.py                        2020-02-02 00:00:00         2910
ops_tracing/_api.py                            2020-02-02 00:00:00         7826
ops_tracing/_backend.py                        2020-02-02 00:00:00         4264
ops_tracing/_buffer.py                         2020-02-02 00:00:00        10512
ops_tracing/_export.py                         2020-02-02 00:00:00         7101
ops_tracing/_mock.py                           2020-02-02 00:00:00         2820
ops_tracing/py.typed                           2020-02-02 00:00:00            0
ops_tracing/vendor/charms/certificate_transfer_interface/v1/certificate_transfer.py 2020-02-02 00:00:00        15328
ops_tracing/vendor/charms/tempo_coordinator_k8s/v0/tracing.py 2020-02-02 00:00:00        37318
ops_tracing/vendor/otlp_json/__init__.py       2020-02-02 00:00:00         6316
ops_tracing/vendor/otlp_json/py.typed          2020-02-02 00:00:00            0
ops_tracing/vendor/otlp_json/readme.md         2020-02-02 00:00:00           44
ops_tracing-3.6.0.dist-info/METADATA           2020-02-02 00:00:00         3025
ops_tracing-3.6.0.dist-info/WHEEL              2020-02-02 00:00:00           87
ops_tracing-3.6.0.dist-info/RECORD             2020-02-02 00:00:00         1305
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 9s</sub>

### ✅ `bash`

**Extract and read ops-tracing __init__.py**

$ python3 -m zipfile -e /tmp/ops-tracing-pkg/ops_tracing-3.6.0-py3-none-any.whl /tmp/ops-tracing-extracted/ 2>/dev/null && cat /tmp/ops-tracing-extracted/ops_tracing/__init__.py

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

<sub>⏱️ 3m 42s</sub>

### 💬 Copilot

Let me check all test files and run existing tests to understand the baseline:

---

<sub>⏱️ 3m 42s</sub>

### ✅ `bash`

**Find test framework usage**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && find tests/ -name "*.py" -exec grep -l "charm_spec\|Context\|Harness\|testing" {} \;

<details>
<summary>10 lines</summary>

```
tests/integration/conftest.py
tests/unit/conftest.py
tests/unit/test_on_leader_elected.py
tests/unit_harness/test_base.py
tests/unit_harness/test_saml_observer.py
tests/unit_harness/test_database_observer.py
tests/unit_harness/test_smtp_observer.py
tests/unit_harness/test_s3_observer.py
tests/unit_harness/test_core.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 42s</sub>

### ✅ `bash`

**Check has_secrets usage in harness tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && cat tests/unit_harness/test_core.py | grep "has_secrets\|_has_secrets" | head -20

<details>
<summary>12 lines</summary>

```
mock_juju_env.return_value = MagicMock(has_secrets=False)
        mock_juju_env.return_value = MagicMock(has_secrets=True)
        mock_juju_env.return_value = MagicMock(has_secrets=False)
        mock_juju_env.return_value = MagicMock(has_secrets=True)
        mock_juju_env.return_value = MagicMock(has_secrets=True)
        mock_juju_env.return_value = MagicMock(has_secrets=True)
        mock_juju_env.return_value = MagicMock(has_secrets=True)
        mock_juju_env.return_value = MagicMock(has_secrets=True)
        mock_juju_env.return_value = MagicMock(has_secrets=True)
        mock_juju_env.return_value = MagicMock(has_secrets=False)
        mock_juju_env.return_value = MagicMock(has_secrets=False)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 18s</sub>

### ✅ `bash`

**Check ops namespace for JujuVersion**

$ python3 -c "import ops; print([x for x in dir(ops) if 'version' in x.lower() or 'Version' in x])"

```
['JujuVersion', '__version__', 'jujuversion', 'version']
<exited with exit code 0>
```


---

<sub>⏱️ 4m 18s</sub>

### ✅ `bash`

**Download ops 3.6.0 and list contents**

$ pip download ops==3.6.0 --no-deps -d /tmp/ops-pkg 2>&1 | tail -3 && ls /tmp/ops-pkg/ && python3 -m zipfile -l /tmp/ops-pkg/ops-3.6.0-py3-none-any.whl 2>/dev/null | grep -v ".pyc" | head -40

<details>
<summary>41 lines</summary>

```
Using cached ops-3.6.0-py3-none-any.whl (211 kB)
Saved /tmp/ops-pkg/ops-3.6.0-py3-none-any.whl
Successfully downloaded ops
ops-3.6.0-py3-none-any.whl
File Name                                             Modified             Size
ops/__init__.py                                2026-02-26 04:18:50         9906
ops/_main.py                                   2026-02-26 04:18:50        20147
ops/charm.py                                   2026-02-26 04:18:50        88307
ops/framework.py                               2026-02-26 04:18:50        59080
ops/jujucontext.py                             2026-02-26 04:18:50        14047
ops/jujuversion.py                             2026-02-26 04:18:50         6888
ops/log.py                                     2026-02-26 04:18:50         6496
ops/main.py                                    2026-02-26 04:18:50         1461
ops/model.py                                   2026-02-26 04:18:50       166308
ops/pebble.py                                  2026-02-26 04:18:50       134028
ops/py.typed                                   2026-02-26 04:18:50            0
ops/storage.py                                 2026-02-26 04:18:50        16025
ops/testing.py                                 2026-02-26 04:18:50         4871
ops/version.py                                 2026-02-26 04:18:50          724
ops/_private/__init__.py                       2026-02-26 04:18:50          726
ops/_private/harness.py                        2026-02-26 04:18:50       171056
ops/_private/timeconv.py                       2026-02-26 04:18:50         4800
ops/_private/yaml.py                           2026-02-26 04:18:50         1232
ops/hookcmds/__init__.py                       2026-02-26 04:18:50         3609
ops/hookcmds/_action.py                        2026-02-26 04:18:50         4811
ops/hookcmds/_other.py                         2026-02-26 04:18:50         6894
ops/hookcmds/_port.py                          2026-02-26 04:18:50         6182
ops/hookcmds/_relation.py                      2026-02-26 04:18:50         6789
ops/hookcmds/_secret.py                        2026-02-26 04:18:50        10041
ops/hookcmds/_state.py                         2026-02-26 04:18:50         2462
ops/hookcmds/_status.py                        2026-02-26 04:18:50         2612
ops/hookcmds/_storage.py                       2026-02-26 04:18:50         2702
ops/hookcmds/_types.py                         2026-02-26 04:18:50        11214
ops/hookcmds/_utils.py                         2026-02-26 04:18:50         1900
ops/lib/__init__.py                            2026-02-26 04:18:50        10036
ops-3.6.0.dist-info/licenses/LICENSE.txt       2026-02-26 04:18:50        11358
ops-3.6.0.dist-info/METADATA                   2026-02-26 04:18:50         7141
ops-3.6.0.dist-info/WHEEL                      2026-02-26 04:18:50           91
ops-3.6.0.dist-info/top_level.txt              2026-02-26 04:18:50            4
ops-3.6.0.dist-info/RECORD                     2026-02-26 04:18:50         2650
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 24s</sub>

### ✅ `bash`

**Check ops 3.6.0 flat namespace**

$ python3 -m zipfile -e /tmp/ops-pkg/ops-3.6.0-py3-none-any.whl /tmp/ops-3.6.0/ 2>/dev/null && python3 -c "import sys; sys.path.insert(0, '/tmp/ops-3.6.0'); import ops; print([x for x in ops.__all__ if not x.startswith('_')])" | tr ',' '\n' | head -60

<details>
<summary>61 lines</summary>

```
['main'
 'tracing'
 'pebble'
 'ActionEvent'
 'ActionMeta'
 'CharmBase'
 'CharmEvents'
 'CharmMeta'
 'CollectMetricsEvent'
 'CollectStatusEvent'
 'ConfigChangedEvent'
 'ConfigMeta'
 'ContainerBase'
 'ContainerMeta'
 'ContainerStorageMeta'
 'HookEvent'
 'InstallEvent'
 'JujuAssumes'
 'JujuAssumesCondition'
 'LeaderElectedEvent'
 'LeaderSettingsChangedEvent'
 'MetadataLinks'
 'PayloadMeta'
 'PebbleCheckEvent'
 'PebbleCheckFailedEvent'
 'PebbleCheckRecoveredEvent'
 'PebbleCustomNoticeEvent'
 'PebbleNoticeEvent'
 'PebbleReadyEvent'
 'PostSeriesUpgradeEvent'
 'PreSeriesUpgradeEvent'
 'RelationBrokenEvent'
 'RelationChangedEvent'
 'RelationCreatedEvent'
 'RelationDepartedEvent'
 'RelationEvent'
 'RelationJoinedEvent'
 'RelationMeta'
 'RelationRole'
 'RemoveEvent'
 'RemoteModel'
 'ResourceMeta'
 'SecretChangedEvent'
 'SecretEvent'
 'SecretExpiredEvent'
 'SecretRemoveEvent'
 'SecretRotateEvent'
 'StartEvent'
 'StopEvent'
 'StorageAttachedEvent'
 'StorageDetachingEvent'
 'StorageEvent'
 'StorageMeta'
 'UpdateStatusEvent'
 'UpgradeCharmEvent'
 'WorkloadEvent'
 'BoundEvent'
 'BoundStoredState'
 'CommitEvent'
 'EventBase'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 29s</sub>

### ✅ `bash`

**More of ops.__all__**

$ python3 -c "import sys; sys.path.insert(0, '/tmp/ops-3.6.0'); import ops; print([x for x in ops.__all__ if not x.startswith('_')])" | tr ',' '\n' | tail -60

<details>
<summary>61 lines</summary>

```
'NoTypeError'
 'Object'
 'ObjectEvents'
 'PreCommitEvent'
 'PrefixedEvents'
 'Serializable'
 'StoredDict'
 'StoredList'
 'StoredSet'
 'StoredState'
 'StoredStateData'
 'StatusName'
 'JujuContext'
 'JujuVersion'
 'ActiveStatus'
 'Application'
 'Binding'
 'BindingMapping'
 'BlockedStatus'
 'CheckInfoMapping'
 'CloudCredential'
 'CloudSpec'
 'ConfigData'
 'Container'
 'ContainerMapping'
 'ErrorStatus'
 'InvalidStatusError'
 'LazyCheckInfo'
 'LazyMapping'
 'LazyNotice'
 'MaintenanceStatus'
 'Model'
 'ModelError'
 'MultiPushPullError'
 'Network'
 'NetworkInterface'
 'OpenedPort'
 'Pod'
 'Port'
 'Relation'
 'RelationData'
 'RelationDataAccessError'
 'RelationDataContent'
 'RelationDataError'
 'RelationDataTypeError'
 'RelationMapping'
 'RelationNotFoundError'
 'Resources'
 'Secret'
 'SecretInfo'
 'SecretNotFoundError'
 'SecretRotate'
 'ServiceInfoMapping'
 'StatusBase'
 'Storage'
 'StorageMapping'
 'TooManyRelatedAppsError'
 'Unit'
 'UnknownStatus'
 'WaitingStatus']
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 0s</sub>

### 💬 Copilot

Now I have a clear picture. Let me set up the branch and make all required changes:

---

<sub>⏱️ 5m 0s</sub>

### ✅ `sql`

**Create todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create todos",
  "query": "INSERT INTO todos (id, title, description) VALUES\n  ('create-branch', 'Create upgrade branch', 'Create git branch ops-3.6.0-upgrade for the ops upgrade'),\n  ('update-requirements', 'Update requirements.txt', 'Change ops>=2.0.0,<3.0.0 to ops>=3.0.0'),\n  ('update-tox', 'Update tox.ini', 'Change ops[testing]==2.21.1 to ops[testing]==3.6.0; add SCENARIO_BARE_CHARM_ERRORS=true'),\n  ('update-pyproject', 'Update pyproject.toml', 'Change target-version [\"py38\"] to [\"py310\"] since ops 3.x dropped Python 3.8'),\n  ('update-charmcraft', 'Update charmcraft.yaml', 'Change Ubuntu 20.04 base to 22.04 since ops 3.x dropped Ubuntu 20.04 support'),\n  ('update-charm-imports', 'Update charm.py imports', 'Remove specific imports from ops.charm/ops.main/ops.model/ops.jujuversion, use flat ops namespace'),\n  ('run-tests', 'Run unit tests', 'Verify all tests pass after the upgrade'),\n  ('commit', 'Commit changes', 'Commit all changes to the branch')"
}
```

</details>

```
8 row(s) inserted. Last inserted row ID: 8.
```


---

<sub>⏱️ 5m 6s</sub>

### ✅ `bash`

**Create upgrade branch**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && git checkout -b ops-3.6.0-upgrade && git status

<details>
<summary>7 lines</summary>

```
Switched to a new branch 'ops-3.6.0-upgrade'
On branch ops-3.6.0-upgrade
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.baseline_commit

nothing added to commit but untracked files present (use "git add" to track)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 10s</sub>

### ✅ `sql`

**Update branch todo**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Update branch todo",
  "query": "UPDATE todos SET status = 'done' WHERE id = 'create-branch'"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 5m 18s</sub>

### 💬 Copilot

Now let me make all the changes:

---

<sub>⏱️ 5m 18s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__all__C4/requirements.txt**

/tmp/ops-upgrade-experiment/indico-operator__all__C4/requirements.txt

```
File /tmp/ops-upgrade-experiment/indico-operator__all__C4/requirements.txt updated with changes.
```


---

<sub>⏱️ 5m 18s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__all__C4/pyproject.toml**

/tmp/ops-upgrade-experiment/indico-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/indico-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 5m 18s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__all__C4/charmcraft.yaml**

/tmp/ops-upgrade-experiment/indico-operator__all__C4/charmcraft.yaml

```
File /tmp/ops-upgrade-experiment/indico-operator__all__C4/charmcraft.yaml updated with changes.
```


---

<sub>⏱️ 5m 23s</sub>

### 💬 Copilot

Now update tox.ini with the new ops[testing] version and add SCENARIO_BARE_CHARM_ERRORS:

---

<sub>⏱️ 5m 23s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini**

/tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini

```
File /tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini updated with changes.
```


---

<sub>⏱️ 5m 27s</sub>

### 💬 Copilot

Now add `SCENARIO_BARE_CHARM_ERRORS=true` to the unit test environment:

---

<sub>⏱️ 5m 27s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini**

/tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini (lines 38-55)

<details>
<summary>18 lines</summary>

```
38. deps =
39.     black
40.     codespell
41.     flake8
42.     flake8-builtins
43.     flake8-copyright
44.     flake8-docstrings
45.     flake8-docstrings-complete
46.     flake8-test-docs
47.     isort
48.     mypy
49.     pep8-naming
50.     pydocstyle>=2.10
51.     pylint
52.     pyproject-flake8
53.     pytest
54.     pytest-asyncio
55.     pytest-operator
```

</details>


---

<sub>⏱️ 5m 31s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini**

/tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini (lines 80-100)

<details>
<summary>21 lines</summary>

```
80. description = Check plugins code against coding style standards
81. deps =
82.     black
83.     codespell
84.     flake8
85.     flake8-builtins
86.     flake8-copyright
87.     flake8-docstrings
88.     flake8-docstrings-complete
89.     flake8-test-docs
90.     indico==3.3.6
91.     isort
92.     mypy
93.     pep8-naming
94.     indico_rock/plugins/autocreate
95.     indico_rock/plugins/anonymize
96.     pydocstyle>=2.10
97.     pylint
98.     pyproject-flake8
99.     pytest
100.     pytest-asyncio
```

</details>


---

<sub>⏱️ 5m 36s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini**

/tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini (lines 116-135)

<details>
<summary>20 lines</summary>

```
116.     # pflake8 {[vars]plugins_path} --ignore=W503
117.     isort --check-only --diff {[vars]plugins_path}
118.     black --check --diff {[vars]plugins_path}
119.     mypy {[vars]plugins_path}
120.     pylint {[vars]plugins_path} --ignore-paths {[vars]plugins_path}autocreate/build,{[vars]plugins_path}anonymize/build
121. 
122. [testenv:unit]
123. description = Run unit tests
124. deps =
125.     cosl
126.     coverage[toml]
127.     pytest
128.     pytest-mock
129.     ops[testing]==3.6.0
130.     -r{toxinidir}/requirements.txt
131. commands =
132.     coverage run --source={[vars]src_path} \
133.         -m pytest --ignore={[vars]tst_path}integration -v --tb native -s {posargs}
134.     coverage report
135.
```

</details>


---

<sub>⏱️ 5m 41s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini**

/tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini

```
File /tmp/ops-upgrade-experiment/indico-operator__all__C4/tox.ini updated with changes.
```


---

<sub>⏱️ 5m 45s</sub>

### 💬 Copilot

Now update the charm.py imports to use the modern flat `ops` namespace:

---

<sub>⏱️ 5m 45s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__all__C4/src/charm.py (lines 1-40)

<details>
<summary>40 lines</summary>

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
```

</details>


---

<sub>⏱️ 5m 52s</sub>

### ❌ `edit`

<details>
<summary>Arguments</summary>

```json
{
  "new_str": "import charms.loki_k8s.v0.loki_push_api\nimport ops\nfrom charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider\nfrom charms.loki_k8s.v0.loki_push_api import LogProxyConsumer\nfrom charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route\nfrom charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider\nfrom charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires",
  "old_str": "import charms.loki_k8s.v0.loki_push_api\nimport ops\nfrom charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider\nfrom charms.loki_k8s.v0.loki_push_api import LogProxyConsumer\nfrom charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route\nfrom charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider\nfrom charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires\nfrom ops.charm import ActionEvent, CharmBase, HookEvent, PebbleReadyEvent, RelationDepartedEvent\nfrom ops.jujuversion import JujuVersion\nfrom ops.main import main\nfrom ops.model import ActiveStatus, BlockedStatus, Container, MaintenanceStatus, WaitingStatus\nfrom ops.pebble import ExecError"
}
```

</details>

```
"path": Required
```


---

<sub>⏱️ 5m 59s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 6m 5s</sub>

### 💬 Copilot

Now I need to update all usages of the removed imports throughout charm.py:

---

<sub>⏱️ 6m 6s</sub>

### ✅ `bash`

**Find all usages of removed imports in charm.py**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && grep -n "ActionEvent\|CharmBase\|HookEvent\|PebbleReadyEvent\|RelationDepartedEvent\|JujuVersion\|^from ops.main\|ActiveStatus\|BlockedStatus\|Container\|MaintenanceStatus\|WaitingStatus\|ExecError\b\|^    main(" src/charm.py

<details>
<summary>43 lines</summary>

```
51:class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attributes
64:            args: Arguments passed to the CharmBase parent constructor.
79:            self.unit.status = ops.BlockedStatus(exc.msg)
198:            self.unit.status = WaitingStatus("Waiting for redis-broker availability")
201:            self.unit.status = WaitingStatus("Waiting for redis-cache availability")
204:            self.unit.status = WaitingStatus("Waiting for database availability")
208:    def _on_pebble_ready(self, event: PebbleReadyEvent) -> None:
219:    def _config_pebble(self, container: Container) -> None:
223:            container: Container to be configured by Pebble.
225:        self.unit.status = MaintenanceStatus(f"Adding {container.name} layer to pebble")
257:        self.unit.status = MaintenanceStatus(f"Starting {container.name} container")
261:            self.unit.status = ActiveStatus()
263:            self.unit.status = WaitingStatus("Waiting for pebble")
286:    def _get_indico_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
320:    def _get_celery_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
514:    def _get_installed_plugins(self, container: Container) -> List[str]:
518:            container: Container for which the installed plugins will be retrieved.
544:    def _get_indico_env_config(self, container: Container) -> Dict:
548:            container: Container for which the configuration will be retrieved.
646:    def _get_indico_env_config_str(self, container: Container) -> Dict[str, str]:
675:    def _on_config_changed(self, event: HookEvent) -> None:
684:            self.unit.status = WaitingStatus("Waiting for pebble")
686:        self.model.unit.status = MaintenanceStatus("Configuring pod")
689:            self.model.unit.status = BlockedStatus(error)
709:        except ExecError as ex:
713:    def _install_plugins(self, container: Container, plugins: List[str]) -> None:
717:            container: Container where the plugins will be installed.
754:    def _exec_cmd_in_custom_dir(self, container: Container, command: List[str]) -> None:
758:            container: Container in which the command will be executed.
770:    def _download_customization_changes(self, container: Container) -> None:
774:            container: Container in which the download will be performed.
831:    def _refresh_external_resources_action(self, event: ActionEvent) -> None:
860:    def _on_peer_relation_departed(self, event: RelationDepartedEvent) -> None:
888:        juju_version = JujuVersion.from_environ()
893:    def _add_admin_action(self, event: ActionEvent) -> None:
920:            except ExecError as ex:
928:    def _execute_anonymize_cmd(self, event: ActionEvent) -> Iterator[str]:
932:            event (ActionEvent): Event triggered by the anonymize-user action
951:                self.unit.status = WaitingStatus(
965:            except ExecError as ex:
971:    def _anonymize_user_action(self, event: ActionEvent) -> None:
998:    main(IndicoOperatorCharm, use_juju_for_storage=True)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 20s</sub>

### 💬 Copilot

Let me read all the relevant sections of charm.py to make precise replacements:

---

<sub>⏱️ 6m 21s</sub>

### ✅ `bash`

**Update event type annotations in charm.py**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && sed -i \
  's/class IndicoOperatorCharm(CharmBase):/class IndicoOperatorCharm(ops.CharmBase):/' \
  src/charm.py && \
sed -i \
  's/def _on_pebble_ready(self, event: PebbleReadyEvent)/def _on_pebble_ready(self, event: ops.PebbleReadyEvent)/' \
  src/charm.py && \
sed -i \
  's/def _on_config_changed(self, event: HookEvent)/def _on_config_changed(self, event: ops.HookEvent)/' \
  src/charm.py && \
sed -i \
  's/def _on_peer_relation_departed(self, event: RelationDepartedEvent)/def _on_peer_relation_departed(self, event: ops.RelationDepartedEvent)/' \
  src/charm.py && \
sed -i \
  's/def _refresh_external_resources_action(self, event: ActionEvent)/def _refresh_external_resources_action(self, event: ops.ActionEvent)/' \
  src/charm.py && \
sed -i \
  's/def _add_admin_action(self, event: ActionEvent)/def _add_admin_action(self, event: ops.ActionEvent)/' \
  src/charm.py && \
sed -i \
  's/def _execute_anonymize_cmd(self, event: ActionEvent)/def _execute_anonymize_cmd(self, event: ops.ActionEvent)/' \
  src/charm.py && \
sed -i \
  's/def _anonymize_user_action(self, event: ActionEvent)/def _anonymize_user_action(self, event: ops.ActionEvent)/' \
  src/charm.py
echo "Done"

```
Done
<exited with exit code 0>
```


---

<sub>⏱️ 6m 30s</sub>

### ✅ `bash`

**Update Container type hints and status class references**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && \
# Replace Container type annotations - careful as 'Container' is also in docstrings
# The type annotations are in function signatures: ": Container"
sed -i \
  's/, container: Container\b/, container: ops.Container/g' \
  src/charm.py && \
# Also handle "container: Container" at start of param
python3 -c "
import re
with open('src/charm.py', 'r') as f:
    content = f.read()
# Replace status classes  
content = content.replace('WaitingStatus(', 'ops.WaitingStatus(')
content = content.replace('ActiveStatus(', 'ops.ActiveStatus(')
content = content.replace('MaintenanceStatus(', 'ops.MaintenanceStatus(')
content = content.replace('BlockedStatus(', 'ops.BlockedStatus(')
# Fix double ops.ops. that might have happened
content = content.replace('ops.ops.', 'ops.')
with open('src/charm.py', 'w') as f:
    f.write(content)
print('Done')
"

```
Done
<exited with exit code 0>
```


---

<sub>⏱️ 6m 37s</sub>

### ✅ `bash`

**Replace ExecError, JujuVersion, and main references**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && \
python3 -c "
with open('src/charm.py', 'r') as f:
    content = f.read()
# Replace ExecError
content = content.replace('except ExecError as ex:', 'except ops.pebble.ExecError as ex:')
# Replace JujuVersion
content = content.replace('JujuVersion.from_environ()', 'ops.JujuVersion.from_environ()')
# Replace main() call at the end
content = content.replace('    main(IndicoOperatorCharm, use_juju_for_storage=True)', '    ops.main.main(IndicoOperatorCharm, use_juju_for_storage=True)')
with open('src/charm.py', 'w') as f:
    f.write(content)
print('Done')
"

```
Done
<exited with exit code 0>
```


---

<sub>⏱️ 6m 43s</sub>

### ✅ `bash`

**Verify import replacements**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && grep -n "ActionEvent\|CharmBase\b\|HookEvent\|PebbleReadyEvent\|RelationDepartedEvent\|JujuVersion\b\|^from ops\.\|ActiveStatus\|BlockedStatus\|MaintenanceStatus\|WaitingStatus\|ExecError\|^    main(" src/charm.py | head -40

<details>
<summary>27 lines</summary>

```
51:class IndicoOperatorCharm(ops.CharmBase):  # pylint: disable=too-many-instance-attributes
64:            args: Arguments passed to the CharmBase parent constructor.
79:            self.unit.status = ops.BlockedStatus(exc.msg)
198:            self.unit.status = ops.WaitingStatus("Waiting for redis-broker availability")
201:            self.unit.status = ops.WaitingStatus("Waiting for redis-cache availability")
204:            self.unit.status = ops.WaitingStatus("Waiting for database availability")
208:    def _on_pebble_ready(self, event: ops.PebbleReadyEvent) -> None:
225:        self.unit.status = ops.MaintenanceStatus(f"Adding {container.name} layer to pebble")
257:        self.unit.status = ops.MaintenanceStatus(f"Starting {container.name} container")
261:            self.unit.status = ops.ActiveStatus()
263:            self.unit.status = ops.WaitingStatus("Waiting for pebble")
675:    def _on_config_changed(self, event: ops.HookEvent) -> None:
684:            self.unit.status = ops.WaitingStatus("Waiting for pebble")
686:        self.model.unit.status = ops.MaintenanceStatus("Configuring pod")
689:            self.model.unit.status = ops.BlockedStatus(error)
709:        except ops.pebble.ExecError as ex:
831:    def _refresh_external_resources_action(self, event: ops.ActionEvent) -> None:
860:    def _on_peer_relation_departed(self, event: ops.RelationDepartedEvent) -> None:
888:        juju_version = ops.JujuVersion.from_environ()
893:    def _add_admin_action(self, event: ops.ActionEvent) -> None:
920:            except ops.pebble.ExecError as ex:
928:    def _execute_anonymize_cmd(self, event: ops.ActionEvent) -> Iterator[str]:
932:            event (ActionEvent): Event triggered by the anonymize-user action
951:                self.unit.status = ops.WaitingStatus(
965:            except ops.pebble.ExecError as ex:
971:    def _anonymize_user_action(self, event: ops.ActionEvent) -> None:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 48s</sub>

### ✅ `bash`

**Check for remaining Container and main references**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && grep -n "^    main(\|Container\b" src/charm.py | grep -v "ops\.\|#\|docstr\|\"" | head -20

<details>
<summary>7 lines</summary>

```
223:            container: Container to be configured by Pebble.
518:            container: Container for which the installed plugins will be retrieved.
548:            container: Container for which the configuration will be retrieved.
717:            container: Container where the plugins will be installed.
758:            container: Container in which the command will be executed.
774:            container: Container in which the download will be performed.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 54s</sub>

### ✅ `bash`

**Check for remaining unqualified Container type hints**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && tail -5 src/charm.py && grep -n "Container\b" src/charm.py | grep "def \|: Container" | head -20

<details>
<summary>19 lines</summary>

```
)


if __name__ == "__main__":  # pragma: no cover
    ops.main.main(IndicoOperatorCharm, use_juju_for_storage=True)
219:    def _config_pebble(self, container: ops.Container) -> None:
223:            container: Container to be configured by Pebble.
286:    def _get_indico_pebble_config(self, container: ops.Container) -> ops.pebble.LayerDict:
320:    def _get_celery_pebble_config(self, container: ops.Container) -> ops.pebble.LayerDict:
514:    def _get_installed_plugins(self, container: ops.Container) -> List[str]:
518:            container: Container for which the installed plugins will be retrieved.
544:    def _get_indico_env_config(self, container: ops.Container) -> Dict:
548:            container: Container for which the configuration will be retrieved.
646:    def _get_indico_env_config_str(self, container: ops.Container) -> Dict[str, str]:
713:    def _install_plugins(self, container: ops.Container, plugins: List[str]) -> None:
717:            container: Container where the plugins will be installed.
754:    def _exec_cmd_in_custom_dir(self, container: ops.Container, command: List[str]) -> None:
758:            container: Container in which the command will be executed.
770:    def _download_customization_changes(self, container: ops.Container) -> None:
774:            container: Container in which the download will be performed.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 0s</sub>

### 💬 Copilot

All Container type hints are now qualified with `ops.`. The docstring references like `container: Container` (in docstrings, not type hints) are fine - those are just descriptions.

Now let me also update the `_has_secrets` return type annotation and verify the imports are clean:

---

<sub>⏱️ 7m 0s</sub>

### ✅ `bash`

**View updated imports section**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && head -35 src/charm.py

<details>
<summary>28 lines</summary>

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

from database_observer import DatabaseObserver
from s3_observer import S3Observer
from saml_observer import SamlObserver
from smtp_observer import SmtpObserver
from state import CharmConfigInvalidError, ProxyConfig, State

logger = logging.getLogger(__name__)

CELERY_PROMEXP_PORT = "9808"
DATABASE_NAME = "indico"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 9s</sub>

### 💬 Copilot

Now let's install ops 3.6.0 and run the unit tests to verify:

---

<sub>⏱️ 7m 9s</sub>

### ✅ `bash`

**Create venv and install deps**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && python3 -m venv /tmp/test-venv && /tmp/test-venv/bin/pip install -q "ops[testing]==3.6.0" pydantic==1.10.26 cosl pytest pytest-mock coverage 2>&1 | tail -5

<details>
<summary>8 lines</summary>

```
The virtual environment was not created successfully because ensurepip is not
available.  On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.

    apt install python3.12-venv

You may need to use sudo with that command.  After installing the python3-venv
package, recreate your virtual environment.

Failing command: /tmp/test-venv/bin/python3
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 7m 30s</sub>

### ✅ `bash`

**Install python3-venv and create test venv**

$ sudo apt install -y python3.12-venv 2>&1 | tail -3 && python3 -m venv /tmp/test-venv && /tmp/test-venv/bin/pip install -q "ops[testing]==3.6.0" pydantic==1.10.26 cosl pytest pytest-mock coverage 2>&1 | tail -5

```
No user sessions are running outdated binaries.

No VM guests are running outdated hypervisor (qemu) binaries on this host.
<exited with exit code 0>
```


---

<sub>⏱️ 7m 34s</sub>

### ❌ `read_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "s1",
  "delay": 60
}
```

</details>

```
Invalid shell ID: s1. Please supply a valid shell ID to read output from.

<no active shell sessions>
```


---

<sub>⏱️ 7m 39s</sub>

### ✅ `bash`

**Install python3-venv**

$ sudo apt install -y python3.12-venv 2>&1 | tail -3

```
Reading state information...
python3.12-venv is already the newest version (3.12.3-1ubuntu0.12).
0 upgraded, 0 newly installed, 0 to remove and 8 not upgraded.
<exited with exit code 0>
```


---

<sub>⏱️ 7m 45s</sub>

### ✅ `bash`

**Create venv**

$ python3 -m venv /tmp/test-venv && echo "venv OK"

```
venv OK
<exited with exit code 0>
```


---

<sub>⏱️ 7m 51s</sub>

### ✅ `bash`

**Install test dependencies**

$ /tmp/test-venv/bin/pip install -q "ops[testing]==3.6.0" "pydantic==1.10.26" cosl pytest pytest-mock coverage 2>&1 | tail -5

```

<exited with exit code 0>
```


---

<sub>⏱️ 7m 58s</sub>

### ✅ `bash`

**Run scenario-based unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && SCENARIO_BARE_CHARM_ERRORS=true PYTHONPATH=".:lib:src" /tmp/test-venv/bin/python -m pytest tests/unit/ -v --tb short 2>&1

<details>
<summary>10 lines</summary>

```
================================================= test session starts ==================================================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /tmp/test-venv/bin/python
cachedir: .pytest_cache
rootdir: /tmp/ops-upgrade-experiment/indico-operator__all__C4
configfile: pyproject.toml
plugins: mock-3.15.1
collecting ... collected 1 item                                                                                                       

tests/unit/test_on_leader_elected.py::test_on_leader_elected_when_secrets_supported PASSED                       [100%]

================================================== 1 passed in 0.11s ===================================================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 6s</sub>

### ✅ `bash`

**Run harness-based unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && PYTHONPATH=".:lib:src" /tmp/test-venv/bin/python -m pytest tests/unit_harness/ -v --tb short 2>&1 | tail -40

<details>
<summary>31 lines</summary>

```
juju_version = ops.JujuVersion.from_environ()

tests/unit_harness/test_core.py::test_proxyconfig_invalid
  /tmp/ops-upgrade-experiment/indico-operator__all__C4/tests/unit_harness/test_core.py:27: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_database_observer.py::test_database_created_emits_config_changed_event
  /tmp/ops-upgrade-experiment/indico-operator__all__C4/tests/unit_harness/test_database_observer.py:48: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_database_observer.py::test_endpoints_changed_emits_config_changed_event
  /tmp/ops-upgrade-experiment/indico-operator__all__C4/tests/unit_harness/test_database_observer.py:64: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_database_observer.py::test_uri
  /tmp/ops-upgrade-experiment/indico-operator__all__C4/tests/unit_harness/test_database_observer.py:80: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_database_observer.py::test_uri_when_no_relation_data
  /tmp/ops-upgrade-experiment/indico-operator__all__C4/tests/unit_harness/test_database_observer.py:104: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_s3_observer.py::test_credentials_changed_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__all__C4/tests/unit_harness/test_s3_observer.py:60: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_s3_observer.py::test_credentials_gone_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__all__C4/tests/unit_harness/test_s3_observer.py:78: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_saml_observer.py::test_saml_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__all__C4/tests/unit_harness/test_saml_observer.py:66: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_smtp_observer.py::test_smtp_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__all__C4/tests/unit_harness/test_smtp_observer.py:63: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 41 passed, 97 warnings in 0.44s ========================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 25s</sub>

### ✅ `bash`

**Check ProxyConfig usage in charm.py**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && grep -n "ProxyConfig\b" src/charm.py

```
30:from state import CharmConfigInvalidError, ProxyConfig, State
658:    def _get_http_proxy_configuration(self, proxy: Optional[ProxyConfig] = None) -> Dict[str, str]:
<exited with exit code 0>
```


---

<sub>⏱️ 8m 30s</sub>

### 💬 Copilot

Good, `ProxyConfig` is still used. Now let me commit the changes and verify the full picture:

---

<sub>⏱️ 8m 30s</sub>

### ✅ `bash`

**Show changed files**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && git diff --stat

<details>
<summary>7 lines</summary>

```
charmcraft.yaml  |  4 ++--
 pyproject.toml   |  2 +-
 requirements.txt |  2 +-
 src/charm.py     | 71 +++++++++++++++++++++++++++++++++--------------------------------------
 tox.ini          |  5 ++++-
 5 files changed, 41 insertions(+), 43 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 4s</sub>

### ✅ `bash`

**Review full diff**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && git diff

<details>
<summary>75 lines</summary>

```diff
diff --git a/charmcraft.yaml b/charmcraft.yaml
index 23ac971..f0fcea5 100644
--- a/charmcraft.yaml
+++ b/charmcraft.yaml
@@ -7,7 +7,7 @@ type: "charm"
 bases:
   - build-on:
     - name: "ubuntu"
-      channel: "20.04"
+      channel: "22.04"
     run-on:
     - name: "ubuntu"
-      channel: "20.04"
+      channel: "22.04"
diff --git a/pyproject.toml b/pyproject.toml
index 185119a..1e6b640 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -13,7 +13,7 @@ branch = true
 # Formatting tools configuration
 [tool.black]
 line-length = 99
-target-version = ["py38"]
+target-version = ["py310"]
 
 [tool.coverage.report]
 fail_under = 97
diff --git a/requirements.txt b/requirements.txt
index d0c8a70..981dbbf 100644
--- a/requirements.txt
+++ b/requirements.txt
@@ -1,2 +1,2 @@
 pydantic==1.10.26
-ops>=2.0.0,<3.0.0
+ops>=3.0.0
diff --git a/src/charm.py b/src/charm.py
index 1040d7d..231bf3e 100755
--- a/src/charm.py
+++ b/src/charm.py
@@ -22,11 +22,6 @@ from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
 from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route
 from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
 from charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires
-from ops.charm import ActionEvent, CharmBase, HookEvent, PebbleReadyEvent, RelationDepartedEvent
-from ops.jujuversion import JujuVersion
-from ops.main import main
-from ops.model import ActiveStatus, BlockedStatus, Container, MaintenanceStatus, WaitingStatus
-from ops.pebble import ExecError
 
 from database_observer import DatabaseObserver
 from s3_observer import S3Observer
@@ -53,7 +48,7 @@ class InvalidRedisNameError(Exception):
     """Represents invalid redis name error."""
 
 
-class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attributes
+class IndicoOperatorCharm(ops.CharmBase):  # pylint: disable=too-many-instance-attributes
     """Charm for Indico on kubernetes.
 
     Attrs:
@@ -200,17 +195,17 @@ class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attri
             If the needed relations have been established.
         """
         if self.redis_broker.relation_data is None:
-            self.unit.status = WaitingStatus("Waiting for redis-broker availability")
+            self.unit.status = ops.WaitingStatus("Waiting for redis-broker availability")
             return False
         if self.redis_cache.relation_data is None:
-            self.unit.status = WaitingStatus("Waiting for redis-cache availability")
+            self.unit.status = ops.WaitingStatus("Waiting for redis-cache availability")
             return False
         if self.database.uri is None:
-            self.unit.status = WaitingStatus("Waiting for database availability")
+            self.unit.status = ops.WaitingStatus("Waiting for database availability")
             return False
         return True
 
-    def _on_pebble_ready(self, event: PebbleReadyEvent) -> None:
+    def _on_pebble_ready(self, event: ops.PebbleReadyEvent) -> None:
:
<command with shellId: 50 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 9m 10s</sub>

### ✅ `bash`

**View end of diff**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && git diff --no-pager | tail -100

<details>
<summary>34 lines</summary>

```
error: invalid option: --no-pager
usage: git diff [<options>] [<commit>] [--] [<path>...]
   or: git diff [<options>] --cached [--merge-base] [<commit>] [--] [<path>...]
   or: git diff [<options>] [--merge-base] <commit> [<commit>...] <commit> [--] [<path>...]
   or: git diff [<options>] <commit>...<commit> [--] [<path>...]
   or: git diff [<options>] <blob> <blob>
   or: git diff [<options>] --no-index [--] <path> <path>

common diff options:
  -z            output diff-raw with lines terminated with NUL.
  -p            output patch format.
  -u            synonym for -p.
  --patch-with-raw
                output both a patch and the diff-raw format.
  --stat        show diffstat instead of patch.
  --numstat     show numeric diffstat instead of patch.
  --patch-with-stat
                output a patch and prepend its diffstat.
  --name-only   show only names of changed files.
  --name-status show names and status of changed files.
  --full-index  show full object name on index lines.
  --abbrev=<n>  abbreviate object names in diff-tree header and diff-raw.
  -R            swap input file pairs.
  -B            detect complete rewrites.
  -M            detect renames.
  -C            detect copies.
  --find-copies-harder
                try unchanged files as candidate for copy detection.
  -l<n>         limit rename attempts up to <n> paths.
  -O<file>      reorder diffs according to the <file>.
  -S<string>    find filepair whose only one side contains the string.
  --pickaxe-all
                show all files diff when -S is used and hit is found.
  -a  --text    treat all files as text.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 15s</sub>

### ✅ `bash`

**View key diff lines**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && git --no-pager diff 2>&1 | grep "^[+-]" | grep -v "^---\|^+++" | head -80

<details>
<summary>81 lines</summary>

```
-      channel: "20.04"
+      channel: "22.04"
-      channel: "20.04"
+      channel: "22.04"
-target-version = ["py38"]
+target-version = ["py310"]
-ops>=2.0.0,<3.0.0
+ops>=3.0.0
-from ops.charm import ActionEvent, CharmBase, HookEvent, PebbleReadyEvent, RelationDepartedEvent
-from ops.jujuversion import JujuVersion
-from ops.main import main
-from ops.model import ActiveStatus, BlockedStatus, Container, MaintenanceStatus, WaitingStatus
-from ops.pebble import ExecError
-class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attributes
+class IndicoOperatorCharm(ops.CharmBase):  # pylint: disable=too-many-instance-attributes
-            self.unit.status = WaitingStatus("Waiting for redis-broker availability")
+            self.unit.status = ops.WaitingStatus("Waiting for redis-broker availability")
-            self.unit.status = WaitingStatus("Waiting for redis-cache availability")
+            self.unit.status = ops.WaitingStatus("Waiting for redis-cache availability")
-            self.unit.status = WaitingStatus("Waiting for database availability")
+            self.unit.status = ops.WaitingStatus("Waiting for database availability")
-    def _on_pebble_ready(self, event: PebbleReadyEvent) -> None:
+    def _on_pebble_ready(self, event: ops.PebbleReadyEvent) -> None:
-    def _config_pebble(self, container: Container) -> None:
+    def _config_pebble(self, container: ops.Container) -> None:
-        self.unit.status = MaintenanceStatus(f"Adding {container.name} layer to pebble")
+        self.unit.status = ops.MaintenanceStatus(f"Adding {container.name} layer to pebble")
-        self.unit.status = MaintenanceStatus(f"Starting {container.name} container")
+        self.unit.status = ops.MaintenanceStatus(f"Starting {container.name} container")
-            self.unit.status = ActiveStatus()
+            self.unit.status = ops.ActiveStatus()
-            self.unit.status = WaitingStatus("Waiting for pebble")
+            self.unit.status = ops.WaitingStatus("Waiting for pebble")
-    def _get_indico_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
+    def _get_indico_pebble_config(self, container: ops.Container) -> ops.pebble.LayerDict:
-    def _get_celery_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
+    def _get_celery_pebble_config(self, container: ops.Container) -> ops.pebble.LayerDict:
-    def _get_installed_plugins(self, container: Container) -> List[str]:
+    def _get_installed_plugins(self, container: ops.Container) -> List[str]:
-    def _get_indico_env_config(self, container: Container) -> Dict:
+    def _get_indico_env_config(self, container: ops.Container) -> Dict:
-    def _get_indico_env_config_str(self, container: Container) -> Dict[str, str]:
+    def _get_indico_env_config_str(self, container: ops.Container) -> Dict[str, str]:
-    def _on_config_changed(self, event: HookEvent) -> None:
+    def _on_config_changed(self, event: ops.HookEvent) -> None:
-            self.unit.status = WaitingStatus("Waiting for pebble")
+            self.unit.status = ops.WaitingStatus("Waiting for pebble")
-        self.model.unit.status = MaintenanceStatus("Configuring pod")
+        self.model.unit.status = ops.MaintenanceStatus("Configuring pod")
-            self.model.unit.status = BlockedStatus(error)
+            self.model.unit.status = ops.BlockedStatus(error)
-        except ExecError as ex:
+        except ops.pebble.ExecError as ex:
-    def _install_plugins(self, container: Container, plugins: List[str]) -> None:
+    def _install_plugins(self, container: ops.Container, plugins: List[str]) -> None:
-    def _exec_cmd_in_custom_dir(self, container: Container, command: List[str]) -> None:
+    def _exec_cmd_in_custom_dir(self, container: ops.Container, command: List[str]) -> None:
-    def _download_customization_changes(self, container: Container) -> None:
+    def _download_customization_changes(self, container: ops.Container) -> None:
-    def _refresh_external_resources_action(self, event: ActionEvent) -> None:
+    def _refresh_external_resources_action(self, event: ops.ActionEvent) -> None:
-    def _on_peer_relation_departed(self, event: RelationDepartedEvent) -> None:
+    def _on_peer_relation_departed(self, event: ops.RelationDepartedEvent) -> None:
-        juju_version = JujuVersion.from_environ()
+        juju_version = ops.JujuVersion.from_environ()
-    def _add_admin_action(self, event: ActionEvent) -> None:
+    def _add_admin_action(self, event: ops.ActionEvent) -> None:
-            except ExecError as ex:
+            except ops.pebble.ExecError as ex:
-    def _execute_anonymize_cmd(self, event: ActionEvent) -> Iterator[str]:
+    def _execute_anonymize_cmd(self, event: ops.ActionEvent) -> Iterator[str]:
-                self.unit.status = WaitingStatus(
+                self.unit.status = ops.WaitingStatus(
-            except ExecError as ex:
+            except ops.pebble.ExecError as ex:
-    def _anonymize_user_action(self, event: ActionEvent) -> None:
+    def _anonymize_user_action(self, event: ops.ActionEvent) -> None:
-    main(IndicoOperatorCharm, use_juju_for_storage=True)
+    ops.main.main(IndicoOperatorCharm, use_juju_for_storage=True)
+setenv =
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 33s</sub>

### 💬 Copilot

All changes look good. Now let me commit:

---

<sub>⏱️ 9m 35s</sub>

### ✅ `bash`

**Commit the upgrade changes**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && git add -A && git commit -m "Upgrade from ops 2.x to ops 3.6.0

ops 3.0.0 dropped support for Python 3.8 and Ubuntu 20.04 but is
otherwise API-compatible with ops 2.x. Subsequent releases added
new features and some testing-framework fixes.

Changes made:

requirements.txt:
- Relax the ops version constraint from >=2.0.0,<3.0.0 to >=3.0.0,
  allowing the latest 3.x release to be resolved.

tox.ini:
- Upgrade ops[testing] from 2.21.1 to 3.6.0.
- Set SCENARIO_BARE_CHARM_ERRORS=true in the unit test environment.
  Added in ops 3.5.0, this causes charm exceptions to propagate
  directly to test code rather than being wrapped in
  UncaughtCharmError, making failures easier to diagnose. This is
  expected to become the default in a future ops major release.

charmcraft.yaml:
- Update the build/run base from Ubuntu 20.04 to 22.04, since ops
  3.x requires Python 3.10+ (Ubuntu 20.04 ships Python 3.8).

pyproject.toml:
- Update black's target-version from py38 to py310, consistent with
  dropping Python 3.8 support.

src/charm.py:
- Remove the now-redundant per-module imports from ops.charm,
  ops.main, ops.model, ops.jujuversion, and ops.pebble. All of
  these symbols are available directly from the top-level ops
  namespace (e.g. ops.CharmBase, ops.WaitingStatus, ops.JujuVersion,
  ops.pebble.ExecError), which is the recommended style in ops 3.x.

Notes:
- The _has_secrets() helper (using ops.JujuVersion.from_environ()
  .has_secrets) is retained because ops 3.x still supports Juju 2.x
  deployments where secrets are unavailable; the runtime check
  remains necessary.
- The Harness-based tests in tests/unit_harness/ continue to pass
  but emit PendingDeprecationWarning. Harness is deprecated in ops
  3.x in favour of ops.testing (scenario). Migration of those tests
  is left for a follow-up.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[ops-3.6.0-upgrade 88cc6ed] Upgrade from ops 2.x to ops 3.6.0
 6 files changed, 42 insertions(+), 43 deletions(-)
 create mode 100644 .baseline_commit
<exited with exit code 0>
```


---

<sub>⏱️ 9m 40s</sub>

### ✅ `bash`

**Verify commit**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && git log --oneline -3

```
88cc6ed (HEAD -> ops-3.6.0-upgrade) Upgrade from ops 2.x to ops 3.6.0
6c86e38 baseline for experiment
ad61761 (grafted, tag: rev302, origin/main, origin/HEAD, main) chore(deps): update dependency indico to v301 (#721)
<exited with exit code 0>
```


---

<sub>⏱️ 9m 45s</sub>

### ✅ `sql`

**Mark remaining todos done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark remaining todos done",
  "query": "UPDATE todos SET status = 'done' WHERE id IN ('update-requirements', 'update-tox', 'update-pyproject', 'update-charmcraft', 'update-charm-imports', 'run-tests', 'commit')"
}
```

</details>

```
7 row(s) updated.
```


---

<sub>⏱️ 9m 53s</sub>

### ❌ `store_memory`

<details>
<summary>Arguments</summary>

```json
{
  "subject": "ops upgrade",
  "fact": "ops 3.x recommends using the flat ops namespace (ops.CharmBase, ops.WaitingStatus, ops.JujuVersion, etc.) rather than per-module imports (from ops.charm import CharmBase). Harness is deprecated in ops 3.x in favour of ops.testing (scenario).",
  "citations": "src/charm.py, https://github.com/canonical/operator/releases/tag/3.0.0",
  "reason": "Future ops-related changes to this charm or code reviews should follow the flat namespace import style and avoid introducing new Harness usage. This convention is a key ops 3.x best practice that isn't obvious from reading a small code sample.",
  "category": "general"
}
```

</details>

```
Unable to store memory. You can continue with your task without storing this information.
```


---

<sub>⏱️ 10m 4s</sub>

### 💬 Copilot

\<task_complete\>
\<parameter name="summary"\>Created branch `ops-3.6.0-upgrade` with the following changes to upgrade from ops 2.x to ops 3.6.0:

**requirements.txt** – Relaxed `ops\>=2.0.0,\<3.0.0` → `ops\>=3.0.0`

**tox.ini** – Upgraded `ops[testing]==2.21.1` → `ops[testing]==3.6.0`; added `SCENARIO_BARE_CHARM_ERRORS=true` to the `[testenv:unit]` environment (new in ops 3.5.0 – propagates charm exceptions directly rather than wrapping them in `UncaughtCharmError`, intended to become the default)

**charmcraft.yaml** – Updated build/run base from Ubuntu `20.04` → `22.04` (ops 3.x requires Python 3.10+; 20.04 ships Python 3.8 which ops 3.x dropped)

**pyproject.toml** – Updated black `target-version` from `["py38"]` → `["py310"]`

**src/charm.py** – Removed the redundant per-module imports (`from ops.charm import …`, `from ops.model import …`, `from ops.main import main`, `from ops.jujuversion import JujuVersion`, `from ops.pebble import ExecError`) and replaced every usage with the flat `ops.*` namespace (`ops.CharmBase`, `ops.WaitingStatus`, `ops.JujuVersion.from_environ()`, `ops.pebble.ExecError`, `ops.main.main(…)`, etc.) — the recommended style in ops 3.x.

**Retained as-is:**
- `_has_secrets()` helper: ops 3.x still supports Juju 2.x runtimes where secrets are unavailable; the runtime check remains necessary.
- Harness-based tests in `tests/unit_harness/`: they pass (with `PendingDeprecationWarning`) and migration to ops.testing is a separate, larger task.

All unit tests (both scenario-based and Harness-based) pass with `ops[testing]==3.6.0`.\</parameter\>
\</invoke\>

---

<sub>⏱️ 10m 4s</sub>

### ℹ️ Info

Continuing autonomously (1 premium request)

---

<sub>⏱️ 10m 12s</sub>

### ✅ `bash`

**Verify branch and commit state**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && git log --oneline -3 && echo "---" && git branch

<details>
<summary>7 lines</summary>

```
88cc6ed (HEAD -> ops-3.6.0-upgrade) Upgrade from ops 2.x to ops 3.6.0
6c86e38 baseline for experiment
ad61761 (grafted, tag: rev302, origin/main, origin/HEAD, main) chore(deps): update dependency indico to v301 (#721)
---
  main
* ops-3.6.0-upgrade
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 18s</sub>

### 💬 Copilot

The branch exists with the commit. Let me do a final verification that tests pass:

---

<sub>⏱️ 10m 19s</sub>

### ✅ `bash`

**Final test run verification**

$ cd /tmp/ops-upgrade-experiment/indico-operator__all__C4 && SCENARIO_BARE_CHARM_ERRORS=true PYTHONPATH=".:lib:src" /tmp/test-venv/bin/python -m pytest tests/unit/ tests/unit_harness/ -q 2>&1 | tail -10

<details>
<summary>9 lines</summary>

```
tests/unit_harness/test_saml_observer.py::test_saml_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__all__C4/tests/unit_harness/test_saml_observer.py:66: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_smtp_observer.py::test_smtp_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__all__C4/tests/unit_harness/test_smtp_observer.py:63: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
42 passed, 97 warnings in 0.46s
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 32s</sub>

### 💬 Copilot

All 42 tests pass. The work is complete.

\<task_complete\>
\<parameter name="summary"\>Created branch `ops-3.6.0-upgrade` upgrading from ops 2.x to ops 3.6.0. Here's a summary of what was analysed and changed:

**Release notes analysis (ops 2.23.2 → 3.6.0):**
- **ops 3.0.0**: Drops Python 3.8 and Ubuntu 20.04; otherwise API-compatible with ops 2.x
- **ops 3.3.0**: Exposes `ops.JujuContext`
- **ops 3.4.0**: New `ops.hookcmds` low-level API; testing context-manager behaviour fix (breaking — not applicable here since tests use `context.run()`); `JujuContext.machine_id` type changed to `str` (not used by this charm)
- **ops 3.5.0**: `SCENARIO_BARE_CHARM_ERRORS` env var; `testing.Context.charm_spec` deprecated
- **ops 3.6.0**: `ExecError.__str__` only shows executable (not full command line — logging uses `ex.stdout`, unaffected); Pydantic `MISSING` sentinel support

**Files changed:**

- **`requirements.txt`**: `ops\>=2.0.0,\<3.0.0` → `ops\>=3.0.0`
- **`tox.ini`**: `ops[testing]==2.21.1` → `ops[testing]==3.6.0`; added `SCENARIO_BARE_CHARM_ERRORS=true` to `[testenv:unit]` (new in 3.5.0 — propagates charm exceptions directly rather than wrapping in `UncaughtCharmError`)
- **`charmcraft.yaml`**: Build/run base `20.04` → `22.04` (ops 3.x dropped Python 3.8/Ubuntu 20.04)
- **`pyproject.toml`**: Black `target-version` `["py38"]` → `["py310"]`
- **`src/charm.py`**: Removed per-module imports (`from ops.charm import …`, `from ops.model import …`, `from ops.main import main`, `from ops.jujuversion import JujuVersion`, `from ops.pebble import ExecError`) and replaced all usages with the flat `ops.*` namespace — the ops 3.x recommended style

**Deliberately kept unchanged:**
- `_has_secrets()` — ops 3.x still supports Juju 2.x where secrets are unavailable; the runtime check remains necessary
- Harness-based tests in `tests/unit_harness/` — they pass with deprecation warnings; migration to the new `ops.testing` framework is a separate, substantial task

All 42 tests pass (1 scenario + 41 harness).\</parameter\>
\</task_complete\>

---

<sub>⏱️ 10m 32s</sub>

### ℹ️ Info

Continuing autonomously (1 premium request)

---

<sub>⏱️ 10m 41s</sub>

### ✅ `task_complete`

**Created branch `ops-3.6.0-upgrade` upgrading from ops 2.x to ops 3.6.0. Changes made:

- **requirements.txt**: `ops>=2.0.0,<3.0.0` → `ops>=3.0.0`
- **tox.ini**: `ops[testing]==2.21.1` → `ops[testing]==3.6.0`; added `SCENARIO_BARE_CHARM_ERRORS=true` to `[testenv:unit]` (new in ops 3.5.0)
- **charmcraft.yaml**: Build/run base `20.04` → `22.04` (ops 3.x dropped Python 3.8/Ubuntu 20.04)
- **pyproject.toml**: Black `target-version` `["py38"]` → `["py310"]`
- **src/charm.py**: Removed per-module imports from `ops.charm`, `ops.model`, `ops.main`, `ops.jujuversion`, `ops.pebble` and replaced all usages with the flat `ops.*` namespace (ops 3.x recommended style)

All 42 tests pass on ops[testing]==3.6.0. The `_has_secrets()` helper is retained since ops 3.x still supports Juju 2.x. The Harness-based tests in `tests/unit_harness/` continue to work but emit deprecation warnings — migration to `ops.testing` is a follow-up task.</parameter>
</invoke>**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Created branch `ops-3.6.0-upgrade` upgrading from ops 2.x to ops 3.6.0. Changes made:\n\n- **requirements.txt**: `ops>=2.0.0,<3.0.0` → `ops>=3.0.0`\n- **tox.ini**: `ops[testing]==2.21.1` → `ops[testing]==3.6.0`; added `SCENARIO_BARE_CHARM_ERRORS=true` to `[testenv:unit]` (new in ops 3.5.0)\n- **charmcraft.yaml**: Build/run base `20.04` → `22.04` (ops 3.x dropped Python 3.8/Ubuntu 20.04)\n- **pyproject.toml**: Black `target-version` `[\"py38\"]` → `[\"py310\"]`\n- **src/charm.py**: Removed per-module imports from `ops.charm`, `ops.model`, `ops.main`, `ops.jujuversion`, `ops.pebble` and replaced all usages with the flat `ops.*` namespace (ops 3.x recommended style)\n\nAll 42 tests pass on ops[testing]==3.6.0. The `_has_secrets()` helper is retained since ops 3.x still supports Juju 2.x. The Harness-based tests in `tests/unit_harness/` continue to work but emit deprecation warnings — migration to `ops.testing` is a follow-up task.</parameter>\n</invoke>"
}
```

</details>

<details>
<summary>8 lines</summary>

```
Created branch `ops-3.6.0-upgrade` upgrading from ops 2.x to ops 3.6.0. Changes made:

- **requirements.txt**: `ops>=2.0.0,<3.0.0` → `ops>=3.0.0`
- **tox.ini**: `ops[testing]==2.21.1` → `ops[testing]==3.6.0`; added `SCENARIO_BARE_CHARM_ERRORS=true` to `[testenv:unit]` (new in ops 3.5.0)
- **charmcraft.yaml**: Build/run base `20.04` → `22.04` (ops 3.x dropped Python 3.8/Ubuntu 20.04)
- **pyproject.toml**: Black `target-version` `["py38"]` → `["py310"]`
- **src/charm.py**: Removed per-module imports from `ops.charm`, `ops.model`, `ops.main`, `ops.jujuversion`, `ops.pebble` and replaced all usages with the flat `ops.*` namespace (ops 3.x recommended style)

All 42 tests pass on ops[testing]==3.6.0. The `_has_secrets()` helper is retained since ops 3.x still supports Juju 2.x. The Harness-based tests in `tests/unit_harness/` continue to work but emit deprecation warnings — migration to `ops.testing` is a follow-up task.</parameter>
</invoke>
```

</details>


---

<sub>⏱️ 10m 46s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 10m 51s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 11m 0s</sub>

### 💬 Copilot

The task is complete. Here's a summary of what was done:

## ops 3.6.0 upgrade — branch `ops-3.6.0-upgrade`

### Release notes analysis

| Version | Impact on this charm |
|---------|---------------------|
| 3.0.0 | Drops Python 3.8 / Ubuntu 20.04 — requires updating charmcraft.yaml and black config |
| 3.3.0 | `ops.JujuContext` exposed — no action needed (charm still uses `JujuVersion`) |
| 3.4.0 | Testing context-manager behaviour fix — not applicable (tests use `context.run()`); `JujuContext.machine_id` type change — not used |
| 3.5.0 | `SCENARIO_BARE_CHARM_ERRORS` env var — adopted in tox.ini |
| 3.6.0 | `ExecError.__str__` truncation — charm logs `ex.stdout`, unaffected |

### Changes made

- **`requirements.txt`** — `ops\>=2.0.0,\<3.0.0` → `ops\>=3.0.0`  
- **`tox.ini`** — `ops[testing]==2.21.1` → `ops[testing]==3.6.0`; `SCENARIO_BARE_CHARM_ERRORS=true` added  
- **`charmcraft.yaml`** — base `20.04` → `22.04`  
- **`pyproject.toml`** — black `target-version` `["py38"]` → `["py310"]`  
- **`src/charm.py`** — replaced per-module ops imports with the flat `ops.*` namespace (ops 3.x recommended style)

All 42 tests pass. The `_has_secrets()` helper is kept because ops 3.x still runs on Juju 2.x. Harness deprecation warnings in `tests/unit_harness/` are expected — migration is a separate follow-up task.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
