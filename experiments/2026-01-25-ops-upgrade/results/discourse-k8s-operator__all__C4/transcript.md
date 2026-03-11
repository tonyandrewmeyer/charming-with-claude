# 🤖 Copilot CLI Session

> **Session ID:** `d63c8c93-ccb5-4b1f-87d7-ba15f6275d70`
> **Duration:** 11m 4s
> **Exported:** 3/11/2026, 4:13:24 PM

<sub>⏱️ 4s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 11s</sub>

### ✅ `bash`

**Check current ops version and tox config**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && cat pyproject.toml | grep -A5 -i ops && echo "---" && cat tox.toml | head -50

<details>
<summary>57 lines</summary>

```
"ops==2.23.2",
  "pydantic==2.10.6",
]

[dependency-groups]
fmt = [
--
  "ops[testing]",
  "pytest",
]
coverage-report = [
  "coverage[toml]",
  "pytest",
---
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

no_package = true
skip_missing_interpreters = true
env_list = [ "lint", "unit", "static", "coverage-report" ]

requires = [ "tox>=4.22", "tox-uv>=1.29.0" ]

[env_run_base]
pass_env = [
  "PYTHONPATH",
  "CHARM_BUILD_DIR",
  "MODEL_SETTINGS",
  "CHARM_FILE",
  "ROCK_IMAGE",
  "OCI_RESOURCE_NAME",
  "JUJU_DEPLOY_BASE",
  "TOX_CMD_PREFIX",
]
runner = "uv-venv-lock-runner"

[env_run_base.set_env]
PYTHONPATH = "{tox_root}{:}{tox_root}{/}lib{:}{tox_root}{/}{[vars]src_path}"
PYTHONBREAKPOINT = "ipdb.set_trace"
PY_COLORS = "1"

[env.fmt]
description = "Apply coding style standards to code"
commands = [
  [ "ruff", "check", "--fix", "--select", "I", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
  [ "ruff", "format", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
]
dependency_groups = [ "fmt" ]

[env.lint]
description = "Check code against coding style standards"
commands = [
  [ "codespell", "{tox_root}" ],
  [ "ruff", "format", "--check", "--diff", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
  [ "ruff", "check", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
  [ "mypy", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
]
dependency_groups = [ "lint" ]

[env.unit]
description = "Run unit tests"
commands = [
  [
    "coverage",
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11s</sub>

### ✅ `bash`

**List source and test files**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && find . -name "*.py" | head -20 && ls src/ tests/

<details>
<summary>25 lines</summary>

```
./lib/charms/rolling_ops/v0/rollingops.py
./lib/charms/observability_libs/v0/juju_topology.py
./lib/charms/redis_k8s/v0/redis.py
./lib/charms/nginx_ingress_integrator/v0/nginx_route.py
./lib/charms/hydra/v0/oauth.py
./lib/charms/data_platform_libs/v0/data_interfaces.py
./lib/charms/loki_k8s/v0/loki_push_api.py
./lib/charms/grafana_k8s/v0/grafana_dashboard.py
./lib/charms/prometheus_k8s/v0/prometheus_scrape.py
./lib/charms/saml_integrator/v0/saml.py
./src/constants.py
./src/oauth_observer.py
./src/charm.py
./src/database.py
./tests/conftest.py
./tests/integration/test_users.py
./tests/integration/conftest.py
./tests/integration/test_charm.py
./tests/integration/test_db_migration.py
./tests/integration/types.py
src/:
charm.py  constants.py	database.py  grafana_dashboards  loki_alert_rules  oauth_observer.py  prometheus_alert_rules

tests/:
__init__.py  conftest.py  integration  unit  unit_harness
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 15s</sub>

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

<sub>⏱️ 15s</sub>

### ✅ `bash`

**Read main charm file**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && cat src/charm.py

<details>
<summary>8 lines</summary>

```
Output too large to read at once (36.3 KB). Saved to: /tmp/copilot-tool-output-1773198155543-a2jz9k.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

""
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 21s</sub>

### ✅ `bash`

**Read charm.py content**

$ cat /tmp/copilot-tool-output-1773198155543-a2jz9k.txt

<details>
<summary>8 lines</summary>

```
Output too large to read at once (36.3 KB). Saved to: /tmp/copilot-tool-output-1773198161583-t7dlhf.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

""
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 22s</sub>

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

<sub>⏱️ 27s</sub>

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

<sub>⏱️ 27s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 1-100)

<details>
<summary>100 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2026 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Charm for Discourse on kubernetes."""
6. 
7. import base64
8. import hashlib
9. import logging
10. import os.path
11. import secrets
12. import string
13. import typing
14. from collections import namedtuple
15. 
16. import ops
17. from charms.data_platform_libs.v0.data_interfaces import (
18.     DatabaseCreatedEvent,
19.     DatabaseEndpointsChangedEvent,
20. )
21. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
22. from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
23. from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route
24. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
25. from charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires
26. from charms.rolling_ops.v0.rollingops import RollingOpsManager
27. from charms.saml_integrator.v0.saml import (
28.     DEFAULT_RELATION_NAME,
29.     SamlDataAvailableEvent,
30.     SamlRequires,
31. )
32. from ops.charm import ActionEvent, CharmBase, HookEvent, RelationBrokenEvent
33. from ops.main import main
34. from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus
35. from ops.pebble import ExecError, ExecProcess, Plan
36. 
37. from constants import (
38.     CONTAINER_APP_USERNAME,
39.     CONTAINER_NAME,
40.     DATABASE_RELATION_NAME,
41.     DISCOURSE_PATH,
42.     LOG_PATHS,
43.     MAX_CATEGORY_NESTING_LEVELS,
44.     OAUTH_RELATION_NAME,
45.     PROMETHEUS_PORT,
46.     REQUIRED_S3_SETTINGS,
47.     SCRIPT_PATH,
48.     SERVICE_NAME,
49.     SERVICE_PORT,
50.     SETUP_COMPLETED_FLAG_FILE,
51.     THROTTLE_LEVELS,
52. )
53. from database import DatabaseHandler
54. from oauth_observer import OAuthObserver
55. 
56. logger = logging.getLogger(__name__)
57. 
58. S3Info = namedtuple("S3Info", ["enabled", "region", "bucket", "endpoint"])
59. 
60. INVALID_CORS_MESSAGE = (
61.     "invalid CORS config, `augment_cors_origin` must be enabled or `cors_origin` must be non-empty"  # pylint: disable=line-too-long
62. )
63. 
64. 
65. class MissingRedisRelationDataError(Exception):
66.     """Custom exception to be raised in case of malformed/missing redis relation data."""
67. 
68. 
69. class DiscourseCharm(CharmBase):
70.     """Charm for Discourse on kubernetes."""
71. 
72.     # pylint: disable=too-many-instance-attributes
73.     # All attributes are necessary for the charm functionality
74. 
75.     on = RedisRelationCharmEvents()
76. 
77.     def __init__(self, *args):
78.         """Initialize defaults and event handlers."""
79.         super().__init__(*args)
80. 
81.         self._database = DatabaseHandler(self, DATABASE_RELATION_NAME)
82.         self._oauth = OAuthObserver(self, self._setup_and_activate, self._get_external_hostname)
83. 
84.         self.framework.observe(
85.             self._database.database.on.database_created, self._on_database_created
86.         )
87.         self.framework.observe(
88.             self._database.database.on.endpoints_changed, self._on_database_endpoints_changed
89.         )
90.         self.framework.observe(
91.             self.on[DATABASE_RELATION_NAME].relation_broken,
92.             self._on_database_relation_broken,
93.         )
94. 
95.         self._require_nginx_route()
96.         self.saml = SamlRequires(self)
97.         self.framework.observe(self.saml.on.saml_data_available, self._on_saml_data_available)
98. 
99.         self.framework.observe(self.on.start, self._on_start)
100.         self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
```

</details>


---

<sub>⏱️ 31s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 100-250)

<details>
<summary>151 lines</summary>

```
100.         self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
101.         self.framework.observe(self.on.discourse_pebble_ready, self._on_discourse_pebble_ready)
102.         self.framework.observe(self.on.config_changed, self._on_config_changed)
103.         self.framework.observe(self.on.promote_user_action, self._on_promote_user_action)
104.         self.framework.observe(self.on.create_user_action, self._on_create_user_action)
105.         self.framework.observe(self.on.anonymize_user_action, self._on_anonymize_user_action)
106. 
107.         self.redis = RedisRequires(self)
108.         self.framework.observe(self.on.redis_relation_updated, self._redis_relation_changed)
109. 
110.         self._metrics_endpoint = MetricsEndpointProvider(
111.             self, jobs=[{"static_configs": [{"targets": [f"*:{PROMETHEUS_PORT}"]}]}]
112.         )
113.         self._logging = LogProxyConsumer(
114.             self, relation_name="logging", log_files=LOG_PATHS, container_name=CONTAINER_NAME
115.         )
116.         self._grafana_dashboards = GrafanaDashboardProvider(self)
117. 
118.         self.restart_manager = RollingOpsManager(
119.             charm=self, relation="restart", callback=self._on_rolling_restart
120.         )
121. 
122.     def _on_start(self, _: ops.StartEvent) -> None:
123.         """Handle start event.
124. 
125.         Args:
126.             event: Event triggering the start event handler.
127.         """
128.         self._setup_and_activate()
129. 
130.     def _on_upgrade_charm(self, _: ops.UpgradeCharmEvent) -> None:
131.         """Handle upgrade charm event.
132. 
133.         Args:
134.             event: Event triggering the upgrade charm event handler.
135.         """
136.         self.on[self.restart_manager.name].acquire_lock.emit()
137. 
138.     def _on_discourse_pebble_ready(self, _: ops.PebbleReadyEvent) -> None:
139.         """Handle discourse pebble ready event.
140. 
141.         Args:
142.             event: Event triggering the discourse pebble ready event handler.
143.         """
144.         self._setup_and_activate()
145. 
146.     def _redis_relation_changed(self, _: HookEvent) -> None:
147.         """Handle redis relation changed event.
148. 
149.         Args:
150.             event: Event triggering the redis relation changed event handler.
151.         """
152.         self._setup_and_activate()
153. 
154.     def _on_database_created(self, _: DatabaseCreatedEvent) -> None:
155.         """Handle database created.
156. 
157.         Args:
158.             event: Event triggering the database created handler.
159.         """
160.         self._setup_and_activate()
161. 
162.     def _on_database_endpoints_changed(self, _: DatabaseEndpointsChangedEvent) -> None:
163.         """Handle endpoints change.
164. 
165.         Args:
166.             event: Event triggering the endpoints changed handler.
167.         """
168.         self._execute_migrations()
169.         if self._are_relations_ready():
170.             self._activate_charm()
171. 
172.     def _on_database_relation_broken(self, _: RelationBrokenEvent) -> None:
173.         """Handle broken relation.
174. 
175.         Args:
176.             event: Event triggering the broken relation handler.
177.         """
178.         self.model.unit.status = WaitingStatus("Waiting for database relation")
179.         self._stop_service()
180. 
181.     def _on_config_changed(self, _: HookEvent) -> None:
182.         """Handle config change.
183. 
184.         Args:
185.             event: Event triggering the config change handler.
186.         """
187.         self._configure_pod()
188. 
189.     def _on_saml_data_available(self, _: SamlDataAvailableEvent) -> None:
190.         """Handle SAML data available."""
191.         self._configure_pod()
192. 
193.     def _on_rolling_restart(self, _: ops.EventBase) -> None:
194.         """Handle rolling restart event.
195. 
196.         Args:
197.             event: Event triggering the discourse rolling restart event handler.
198.         """
199.         self._setup_and_activate()
200. 
201.     def _setup_and_activate(self) -> None:
202.         """Set up discourse, configure the pod and eventually activate the charm."""
203.         if not self._is_setup_completed():
204.             self._set_up_discourse()
205.         self._configure_pod()
206.         if self._are_relations_ready():
207.             self._activate_charm()
208. 
209.     def _require_nginx_route(self) -> None:
210.         """Create minimal ingress configuration."""
211.         require_nginx_route(
212.             charm=self,
213.             service_hostname=self._get_external_hostname(),
214.             service_name=self.app.name,
215.             service_port=SERVICE_PORT,
216.             session_cookie_max_age=3600,
217.         )
218. 
219.     def _get_external_hostname(self) -> str:
220.         """Extract and return hostname from site_url or default to [application name].
221. 
222.         Returns:
223.             The site hostname defined as part of the site_url configuration or a default value.
224.         """
225.         return (
226.             typing.cast(str, self.config["external_hostname"])
227.             if self.config["external_hostname"]
228.             else self.app.name
229.         )
230. 
231.     def _get_cors_origin(self) -> str:
232.         """Return the combined CORS origins.
233. 
234.         Return the combined CORS origins from 'cors_origin' and, if enabled,
235.         'external_hostname' and 's3_cdn_url'. Skips augmentation if 'cors_origin' is '*'.
236. 
237.         Returns:
238.             Comma-separated CORS origins string.
239.         """
240.         user_value = str(self.config.get("cors_origin", "")).strip()
241.         if user_value == "*":
242.             # No need to augment if all origins allowed
243.             return "*"
244. 
245.         origins: set[str] = set()
246.         if user_value:
247.             origins.update(s for s in (o.strip() for o in user_value.split(",")) if s)
248. 
249.         if self.config.get("augment_cors_origin"):
250.             ext = self._get_external_hostname()
```

</details>


---

<sub>⏱️ 32s</sub>

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

<sub>⏱️ 37s</sub>

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

<sub>⏱️ 36s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 250-450)

<details>
<summary>201 lines</summary>

```
250.             ext = self._get_external_hostname()
251.             if ext:
252.                 scheme = "https" if self.config.get("force_https") else "http"
253.                 origins.add(f"{scheme}://{ext}")
254. 
255.             cdn = str(self.config.get("s3_cdn_url"))
256.             if cdn:
257.                 origins.add(cdn)
258. 
259.         return ",".join(sorted(origins)) if origins else ""
260. 
261.     def _is_setup_completed(self) -> bool:
262.         """Check if the _set_up_discourse process has finished.
263. 
264.         Returns:
265.             True if the _set_up_discourse process has finished.
266.         """
267.         container = self.unit.get_container(CONTAINER_NAME)
268.         return container.can_connect() and container.exists(SETUP_COMPLETED_FLAG_FILE)
269. 
270.     def _set_setup_completed(self) -> None:
271.         """Mark the _set_up_discourse process as completed."""
272.         container = self.unit.get_container(CONTAINER_NAME)
273.         container.push(SETUP_COMPLETED_FLAG_FILE, "", make_dirs=True)
274. 
275.     def _is_config_valid(self) -> bool:
276.         """Check that the provided config is valid.
277. 
278.         Returns:
279.             If config is valid.
280.         """
281.         errors = []
282. 
283.         if (
284.             self.config.get("enable_cors")
285.             and self.config.get("cors_origin") == ""
286.             and not self.config.get("augment_cors_origin")
287.         ):
288.             errors.append(INVALID_CORS_MESSAGE)
289. 
290.         if self.config["throttle_level"] not in THROTTLE_LEVELS:
291.             errors.append(f"throttle_level must be one of: {' '.join(THROTTLE_LEVELS.keys())}")
292. 
293.         if (
294.             self.config["force_saml_login"]
295.             and self.model.get_relation(DEFAULT_RELATION_NAME) is None
296.         ):
297.             errors.append("force_saml_login cannot be true without a saml relation")
298.         if self.config["max_category_nesting"] not in MAX_CATEGORY_NESTING_LEVELS:
299.             errors.append(
300.                 "max_category_nesting must be one of: "
301.                 f"{', '.join(map(str, MAX_CATEGORY_NESTING_LEVELS))}"
302.             )
303.         if (
304.             self.config["saml_sync_groups"]
305.             and self.model.get_relation(DEFAULT_RELATION_NAME) is None
306.         ):
307.             errors.append("'saml_sync_groups' cannot be specified without a saml relation")
308. 
309.         if (
310.             self.model.get_relation(DEFAULT_RELATION_NAME) is not None
311.             and not self.config["force_https"]
312.         ):
313.             errors.append("A saml relation cannot be specified without 'force_https' being true")
314. 
315.         if (
316.             self.model.get_relation(OAUTH_RELATION_NAME) is not None
317.             and not self.config["force_https"]
318.         ):
319.             errors.append(
320.                 "An oauth relation cannot be established without 'force_https' being true"
321.             )
322. 
323.         if self.config.get("s3_enabled"):
324.             errors.extend(
325.                 f"'s3_enabled' requires '{s3_config}'"
326.                 for s3_config in REQUIRED_S3_SETTINGS
327.                 if not self.config[s3_config]
328.             )
329. 
330.         if errors:
331.             self.model.unit.status = BlockedStatus(", ".join(errors))
332.         return not errors
333. 
334.     def _get_saml_config(self) -> typing.Dict[str, typing.Any]:
335.         """Get SAML configuration.
336. 
337.         Returns:
338.             Dictionary with the SAML configuration settings.
339.         """
340.         relation_data = self.saml.get_relation_data()
341.         if relation_data is None:
342.             return {}
343. 
344.         saml_config = {}
345. 
346.         sso_redirect_endpoint = next(
347.             e
348.             for e in relation_data.endpoints
349.             if e.name == "SingleSignOnService"
350.             and e.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
351.         )
352. 
353.         saml_config["DISCOURSE_SAML_TARGET_URL"] = str(sso_redirect_endpoint.url)
354.         certificate = relation_data.certificates[0]
355.         # discourse needs SHA1 fingerprint
356.         saml_config["DISCOURSE_SAML_CERT_FINGERPRINT"] = (
357.             hashlib.sha1(base64.b64decode(certificate)).digest().hex(":").upper()  # noqa: S324  # nosec
358.         )
359. 
360.         saml_config["DISCOURSE_SAML_FULL_SCREEN_LOGIN"] = (
361.             "true" if self.config["force_saml_login"] else "false"
362.         )
363.         saml_sync_groups = [
364.             x.strip()
365.             for x in typing.cast(str, self.config["saml_sync_groups"]).split(",")
366.             if x.strip()
367.         ]
368.         if saml_sync_groups:
369.             # Per https://github.com/discourse/discourse-saml setting this to `true`
370.             # means the assigned groups will be completely synced including adding
371.             # AND removing groups based on the SAML provider.
372.             saml_config["DISCOURSE_SAML_GROUPS_FULLSYNC"] = "false"
373.             saml_config["DISCOURSE_SAML_SYNC_GROUPS"] = "true"
374.             saml_config["DISCOURSE_SAML_SYNC_GROUPS_LIST"] = "|".join(saml_sync_groups)
375. 
376.         return saml_config
377. 
378.     def _get_s3_env(self) -> typing.Dict[str, typing.Any]:
379.         """Get the list of S3-related environment variables from charm's configuration.
380. 
381.         Returns:
382.             Dictionary with all the S3 environment settings.
383.         """
384.         s3_env = {
385.             "DISCOURSE_S3_ACCESS_KEY_ID": self.config["s3_access_key_id"],
386.             "DISCOURSE_S3_BUCKET": self.config["s3_bucket"],
387.             "DISCOURSE_S3_ENDPOINT": self.config.get("s3_endpoint", "s3.amazonaws.com"),
388.             "DISCOURSE_S3_REGION": self.config["s3_region"],
389.             "DISCOURSE_S3_SECRET_ACCESS_KEY": self.config["s3_secret_access_key"],
390.             "DISCOURSE_S3_INSTALL_CORS_RULE": str(
391.                 self.config.get("s3_install_cors_rule", True)
392.             ).lower(),
393.             "DISCOURSE_USE_S3": "true",
394.         }
395.         if self.config.get("s3_backup_bucket"):
396.             s3_env["DISCOURSE_BACKUP_LOCATION"] = "s3"
397.             s3_env["DISCOURSE_S3_BACKUP_BUCKET"] = self.config["s3_backup_bucket"]
398.         if self.config.get("s3_cdn_url"):
399.             s3_env["DISCOURSE_S3_CDN_URL"] = self.config["s3_cdn_url"]
400.         if self.config.get("s3_enabled"):
401.             # We force assets to be uploaded to S3
402.             # This should be considered as a workaround and revisited later
403.             s3_env["FORCE_S3_UPLOADS"] = "true"
404. 
405.         return s3_env
406. 
407.     def _get_redis_relation_data(self) -> typing.Tuple[str, int]:
408.         """Get the hostname and port from the redis relation data.
409. 
410.         Returns:
411.             Tuple with the hostname and port of the related redis
412.         Raises:
413.             MissingRedisRelationDataError if the some of redis relation data is malformed/missing
414.         """
415.         relation = self.model.get_relation(self.redis.relation_name)
416.         if not relation:
417.             raise MissingRedisRelationDataError("No redis relation data")
418.         relation_app_data = relation.data[relation.app]
419.         relation_unit_data = self.redis.relation_data
420. 
421.         try:
422.             redis_hostname = str(
423.                 relation_app_data["leader-host"]
424.                 if relation_app_data.get("leader-host")
425.                 else relation_unit_data["hostname"]
426.             )
427.             redis_port = int(relation_unit_data["port"])
428.         except (KeyError, ValueError) as exc:
429.             raise MissingRedisRelationDataError(
430.                 "Either 'leader-host' or 'hostname' and 'port' are mandatory"
431.             ) from exc
432. 
433.         logger.debug(
434.             "Got redis connection details from relation of %s:%s", redis_hostname, redis_port
435.         )
436.         return (redis_hostname, redis_port)
437. 
438.     def _create_discourse_environment_settings(self) -> typing.Dict[str, str]:
439.         """Create a layer config based on our current configuration.
440. 
441.         Returns:
442.             Dictionary with all the environment settings.
443.         """
444.         database_relation_data = self._database.get_relation_data()
445. 
446.         # The following could fail if the data is malformed.
447.         # We/don't catch it because we don't want to silently fail in those cases
448.         redis_relation_data = self._get_redis_relation_data()
449. 
450.         pod_config = {
```

</details>


---

<sub>⏱️ 43s</sub>

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

<sub>⏱️ 42s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 450-650)

<details>
<summary>201 lines</summary>

```
450.         pod_config = {
451.             # Since pebble exec command doesn't copy the container env (envVars set in Dockerfile),
452.             # I need to take the required envVars for the application to work properly
453.             "CONTAINER_APP_NAME": CONTAINER_NAME,
454.             "CONTAINER_APP_ROOT": "/srv/discourse",
455.             "CONTAINER_APP_USERNAME": CONTAINER_APP_USERNAME,
456.             "DISCOURSE_CORS_ORIGIN": self._get_cors_origin(),
457.             "DISCOURSE_DB_HOST": database_relation_data["POSTGRES_HOST"],
458.             "DISCOURSE_DB_NAME": database_relation_data["POSTGRES_DB"],
459.             "DISCOURSE_DB_PASSWORD": database_relation_data["POSTGRES_PASSWORD"],
460.             "DISCOURSE_DB_USERNAME": database_relation_data["POSTGRES_USER"],
461.             "DISCOURSE_DEVELOPER_EMAILS": self.config["developer_emails"],
462.             "DISCOURSE_ENABLE_CORS": str(self.config["enable_cors"]).lower(),
463.             "DISCOURSE_HOSTNAME": self._get_external_hostname(),
464.             "DISCOURSE_MAX_CATEGORY_NESTING": str(self.config["max_category_nesting"]),
465.             "DISCOURSE_REDIS_HOST": redis_relation_data[0],
466.             "DISCOURSE_REDIS_PORT": str(redis_relation_data[1]),
467.             "DISCOURSE_REFRESH_MAXMIND_DB_DURING_PRECOMPILE_DAYS": "0",
468.             "DISCOURSE_SERVE_STATIC_ASSETS": "true",
469.             "DISCOURSE_SMTP_ADDRESS": self.config["smtp_address"],
470.             "DISCOURSE_SMTP_AUTHENTICATION": self.config["smtp_authentication"],
471.             "DISCOURSE_SMTP_DOMAIN": self.config["smtp_domain"],
472.             "DISCOURSE_SMTP_ENABLE_START_TLS": self.config["smtp_enable_start_tls"],
473.             "DISCOURSE_SMTP_FORCE_TLS": self.config["smtp_force_tls"],
474.             "DISCOURSE_SMTP_OPENSSL_VERIFY_MODE": self.config["smtp_openssl_verify_mode"],
475.             "DISCOURSE_SMTP_PASSWORD": self.config["smtp_password"],
476.             "DISCOURSE_SMTP_PORT": str(self.config["smtp_port"]),
477.             "DISCOURSE_SMTP_USER_NAME": self.config["smtp_username"],
478.             "RAILS_ENV": "production",
479.             "UNICORN_SIDEKIQ_MAX_RSS": str(self.config["sidekiq_max_memory"]),
480.         }
481.         pod_config.update(self._get_saml_config())
482.         # Add OIDC env vars if oauth relation is established
483.         pod_config.update(self._oauth.get_oidc_env())
484. 
485.         if self.config.get("s3_enabled"):
486.             pod_config.update(self._get_s3_env())
487. 
488.         # We only get valid throttle levels here, otherwise it would be caught
489.         # by `_is_config_valid()`.
490.         # self.config return an Any type
491.         pod_config.update(THROTTLE_LEVELS.get(self.config["throttle_level"]))  # type: ignore
492. 
493.         # Update environment with proxy settings
494.         pod_config["HTTP_PROXY"] = pod_config["http_proxy"] = (
495.             os.environ.get("JUJU_CHARM_HTTP_PROXY") or ""
496.         )
497.         pod_config["HTTPS_PROXY"] = pod_config["https_proxy"] = (
498.             os.environ.get("JUJU_CHARM_HTTPS_PROXY") or ""
499.         )
500.         pod_config["NO_PROXY"] = pod_config["no_proxy"] = (
501.             os.environ.get("JUJU_CHARM_NO_PROXY") or ""
502.         )
503. 
504.         return pod_config
505. 
506.     def _create_layer_config(self) -> ops.pebble.LayerDict:
507.         """Create a layer config based on our current configuration.
508. 
509.         Returns:
510.             Dictionary with the pebble configuration.
511.         """
512.         logger.info("Generating Layer config")
513.         layer_config = {
514.             "summary": "Discourse layer",
515.             "description": "Discourse layer",
516.             "services": {
517.                 SERVICE_NAME: {
518.                     "override": "replace",
519.                     "summary": "Discourse web application",
520.                     "command": f"{SCRIPT_PATH}/app_launch.sh",
521.                     "user": CONTAINER_APP_USERNAME,
522.                     "startup": "enabled",
523.                     "environment": self._create_discourse_environment_settings(),
524.                     "kill-delay": "20s",
525.                 }
526.             },
527.             "checks": {
528.                 "discourse-ready": {
529.                     "override": "replace",
530.                     "level": "ready",
531.                     "http": {"url": f"http://localhost:{SERVICE_PORT}/srv/status"},
532.                 },
533.             },
534.         }
535.         return typing.cast(ops.pebble.LayerDict, layer_config)
536. 
537.     def _should_run_s3_migration(
538.         self, current_plan: Plan, s3info: typing.Optional[S3Info]
539.     ) -> bool:
540.         """Determine if the S3 migration is to be run.
541. 
542.         Args:
543.             current_plan: Dictionary containing the current plan.
544.             s3info: S3Info object containing the S3 configuration options.
545. 
546.         Returns:
547.             If no services are planned yet (first run) or S3 settings have changed.
548.         """
549.         result = self.config.get("s3_enabled") and (
550.             not current_plan.services
551.             or (
552.                 s3info
553.                 and (
554.                     s3info.enabled != self.config.get("s3_enabled")
555.                     or s3info.region != self.config.get("s3_region")
556.                     or s3info.bucket != self.config.get("s3_bucket")
557.                     or s3info.endpoint != self.config.get("s3_endpoint")
558.                 )
559.             )
560.         )
561.         return bool(result)
562. 
563.     def _are_relations_ready(self) -> bool:
564.         """Check if the needed database relations are established.
565. 
566.         Returns:
567.             If the needed relations have been established.
568.         """
569.         if not self._database.is_relation_ready():
570.             self.model.unit.status = WaitingStatus("Waiting for database relation")
571.             self._stop_service()
572.             return False
573.         if not self.redis.relation_data:
574.             self.model.unit.status = WaitingStatus("Waiting for redis relation")
575.             self._stop_service()
576.             return False
577.         try:
578.             if (
579.                 self._get_redis_relation_data()[0] in ("", "None")
580.                 or self._get_redis_relation_data()[1] == 0
581.             ):
582.                 self.model.unit.status = WaitingStatus("Waiting for redis relation to initialize")
583.                 return False
584.         except MissingRedisRelationDataError:
585.             self.model.unit.status = WaitingStatus("Waiting for redis relation to initialize")
586.             return False
587.         return True
588. 
589.     def _execute_migrations(self) -> None:
590.         container = self.unit.get_container(CONTAINER_NAME)
591.         if not self._are_relations_ready() or not container.can_connect():
592.             logger.info("Not ready to execute migrations")
593.             return
594.         env_settings = self._create_discourse_environment_settings()
595.         self.model.unit.status = MaintenanceStatus("Executing migrations")
596.         # The rails migration task is idempotent and concurrent-safe, from
597.         # https://stackoverflow.com/questions/17815769/are-rake-dbcreate-and-rake-dbmigrate-idempotent
598.         # and https://github.com/rails/rails/pull/22122
599.         # Thus it's safe to run this task on all units to
600.         # avoid complications with how juju schedules charm upgrades
601.         try:
602.             migration_process: ExecProcess = container.exec(
603.                 [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", "--trace", "db:migrate"],
604.                 environment=env_settings,
605.                 working_dir=DISCOURSE_PATH,
606.                 user=CONTAINER_APP_USERNAME,
607.             )
608.             migration_process.wait_output()
609.         except ExecError as cmd_err:
610.             logger.exception("Executing migrations failed with code %d.", cmd_err.exit_code)
611.             raise
612. 
613.     def _set_workload_version(self) -> None:
614.         container = self.unit.get_container(CONTAINER_NAME)
615.         if not self._are_relations_ready() or not container.can_connect():
616.             logger.info("Not ready to set workload version")
617.             return
618.         env_settings = self._create_discourse_environment_settings()
619.         try:
620.             logger.info("Setting workload version")
621.             get_version_process = container.exec(
622.                 [f"{DISCOURSE_PATH}/bin/rails", "runner", "puts Discourse::VERSION::STRING"],
623.                 environment=env_settings,
624.                 working_dir=DISCOURSE_PATH,
625.                 user=CONTAINER_APP_USERNAME,
626.             )
627.             version, _ = get_version_process.wait_output()
628.             self.unit.set_workload_version(version)
629.         except ExecError as cmd_err:
630.             logger.exception("Setting workload version failed with code %d.", cmd_err.exit_code)
631.             raise
632. 
633.     def _run_s3_migration(self) -> None:
634.         container = self.unit.get_container(CONTAINER_NAME)
635.         if not self._are_relations_ready() or not container.can_connect():
636.             logger.info("Not ready to run S3 migration")
637.             return
638.         env_settings = self._create_discourse_environment_settings()
639.         self.model.unit.status = MaintenanceStatus("Running S3 migration")
640.         logger.info("Running S3 migration")
641.         try:
642.             process = container.exec(
643.                 [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", "s3:upload_assets"],
644.                 environment=env_settings,
645.                 working_dir=DISCOURSE_PATH,
646.                 user=CONTAINER_APP_USERNAME,
647.             )
648.             process.wait_output()
649.         except ExecError as cmd_err:
650.             logger.exception("S3 migration failed with code %d.", cmd_err.exit_code)
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

<sub>⏱️ 47s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 650-800)

<details>
<summary>151 lines</summary>

```
650.             logger.exception("S3 migration failed with code %d.", cmd_err.exit_code)
651.             raise
652. 
653.     def _set_up_discourse(self) -> None:
654.         """Run Discourse migrations and recompile assets.
655. 
656.         Args:
657.             event: Event triggering the handler.
658.         """
659.         container = self.unit.get_container(CONTAINER_NAME)
660.         if not self._are_relations_ready() or not container.can_connect():
661.             logger.info("Pebble or relations not ready, not attempting to setup discourse")
662.             return
663.         logger.info(
664.             "Relations are ready and can connect to container, attempting to set up discourse."
665.         )
666.         try:
667.             logger.info("Discourse setup: about to execute migrations")
668.             self._execute_migrations()
669.             logger.info("Discourse setup: about to mark the discourse setup process as complete")
670.             self._set_setup_completed()
671.             logger.info("Discourse setup: about to set workload version")
672.             self._set_workload_version()
673.             logger.info("Discourse setup: completed")
674.         except ExecError as cmd_err:
675.             logger.exception("Setting up discourse failed with code %d.", cmd_err.exit_code)
676.             raise
677. 
678.     def _configure_pod(self) -> None:
679.         """Configure pod using pebble and layer generated from config.
680. 
681.         Args:
682.             event: Event triggering the handler.
683.         """
684.         container = self.unit.get_container(CONTAINER_NAME)
685.         if not self._are_relations_ready() or not container.can_connect():
686.             logger.info("Not ready to do config changed action")
687.             return
688.         if not self._is_config_valid():
689.             return
690. 
691.         # Get previous plan and extract env vars values to check is some S3 params has changed
692.         current_plan = container.get_plan()
693. 
694.         # Covers when there are no plan
695.         previous_s3_info = None
696.         if (
697.             current_plan.services
698.             and SERVICE_NAME in current_plan.services
699.             and current_plan.services[SERVICE_NAME]
700.         ):
701.             current_env = current_plan.services[SERVICE_NAME].environment
702.             previous_s3_info = S3Info(
703.                 current_env.get("DISCOURSE_USE_S3", ""),
704.                 current_env.get("DISCOURSE_S3_REGION", ""),
705.                 current_env.get("DISCOURSE_S3_BUCKET", ""),
706.                 current_env.get("DISCOURSE_S3_ENDPOINT", ""),
707.             )
708.         if self.model.unit.is_leader() and self._should_run_s3_migration(
709.             current_plan, previous_s3_info
710.         ):
711.             self._run_s3_migration()
712. 
713.         self._activate_charm()
714.         if container.can_connect():
715.             self._config_force_https()
716. 
717.     def _activate_charm(self) -> None:
718.         """Start discourse and mark the charm as active if the setup is completed."""
719.         # mypy has some trouble with dynamic attributes
720.         if not self._is_setup_completed():
721.             logger.info("Not starting the discourse server until discourse setup completed")
722.             return
723.         container = self.unit.get_container(CONTAINER_NAME)
724.         if self._is_config_valid() and container.can_connect():
725.             self._start_service()
726.             self.model.unit.status = ActiveStatus()
727. 
728.     def _user_exists(self, email: str) -> bool:
729.         """Check if a user with the given email exists.
730. 
731.         Args:
732.             email: Email of the user to check.
733. 
734.         Returns:
735.             True if the user exists, False otherwise.
736.         """
737.         container = self.unit.get_container(CONTAINER_NAME)
738.         user_exists = container.exec(
739.             [os.path.join(DISCOURSE_PATH, "bin/bundle"), "exec", "rake", f"users:exists[{email}]"],
740.             working_dir=DISCOURSE_PATH,
741.             user=CONTAINER_APP_USERNAME,
742.             environment=self._create_discourse_environment_settings(),
743.         )
744.         try:
745.             user_exists.wait_output()
746.             return True
747.         except ExecError as ex:
748.             if ex.exit_code == 2:
749.                 return False
750.             raise
751. 
752.     def _activate_user(self, email: str) -> bool:
753.         """Activate a user with the given email.
754. 
755.         Args:
756.             email: Email of the user to activate.
757.         """
758.         container = self.unit.get_container(CONTAINER_NAME)
759.         activate_process = container.exec(
760.             [
761.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
762.                 "exec",
763.                 "rake",
764.                 f"users:activate[{email}]",
765.             ],
766.             working_dir=DISCOURSE_PATH,
767.             user=CONTAINER_APP_USERNAME,
768.             environment=self._create_discourse_environment_settings(),
769.         )
770.         try:
771.             activate_process.wait_output()
772.             return True
773.         except ExecError as ex:
774.             if ex.exit_code == 2:
775.                 return False
776.             raise
777. 
778.     def _on_promote_user_action(self, event: ActionEvent) -> None:
779.         """Promote a user to a specific trust level.
780. 
781.         Args:
782.             event: Event triggering the promote_user action.
783.         """
784.         container = self.unit.get_container(CONTAINER_NAME)
785.         if not container.can_connect():
786.             event.fail("Unable to connect to container, container is not ready")
787.             return
788. 
789.         email = event.params["email"]
790. 
791.         if not self._user_exists(email):
792.             event.fail(f"User with email {email} does not exist")
793.             return
794. 
795.         process = container.exec(
796.             [
797.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
798.                 "exec",
799.                 "rake",
800.                 "admin:create",
```

</details>


---

<sub>⏱️ 56s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 800-1000)

<details>
<summary>151 lines</summary>

```
800.                 "admin:create",
801.             ],
802.             stdin=f"{email}\nn\nY\n",
803.             working_dir=DISCOURSE_PATH,
804.             user=CONTAINER_APP_USERNAME,
805.             environment=self._create_discourse_environment_settings(),
806.             timeout=60,
807.         )
808.         try:
809.             process.wait_output()
810.             event.set_results({"user": email})
811.         except ExecError as ex:
812.             event.fail(
813.                 f"Failed to make user with email {email} an admin: {ex.stdout}"  # type: ignore
814.             )
815. 
816.     def _on_create_user_action(self, event: ActionEvent) -> None:
817.         """Create a new user in Discourse.
818. 
819.         Args:
820.             event: Event triggering the create_user action.
821.         """
822.         container = self.unit.get_container(CONTAINER_NAME)
823.         if not container.can_connect():
824.             event.fail("Unable to connect to container, container is not ready")
825.             return
826. 
827.         email = event.params["email"]
828.         password = self._generate_password(16)
829. 
830.         if self._user_exists(email):
831.             event.fail(f"User with email {email} already exists")
832.             return
833. 
834.         # Admin flag is optional, if it is true, the user will be created as an admin
835.         admin_flag = "Y" if event.params.get("admin") else "N"
836. 
837.         process = container.exec(
838.             [
839.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
840.                 "exec",
841.                 "rake",
842.                 "admin:create",
843.             ],
844.             stdin=f"{email}\n{password}\n{password}\n{admin_flag}\n",
845.             working_dir=DISCOURSE_PATH,
846.             user=CONTAINER_APP_USERNAME,
847.             environment=self._create_discourse_environment_settings(),
848.             timeout=60,
849.         )
850.         try:
851.             process.wait_output()
852.         except ExecError as ex:
853.             event.fail(f"Failed to make user with email {email}: {ex.stdout}")  # type: ignore
854.             return
855. 
856.         if (
857.             not event.params.get("admin")
858.             and event.params.get("active")
859.             and not self._activate_user(email)
860.         ):
861.             event.fail(f"Could not find user {email} to activate")
862.             return
863. 
864.         event.set_results({"user": email, "password": password})
865. 
866.     def _generate_password(self, length: int) -> str:
867.         """Generate a random password.
868. 
869.         Args:
870.             length: Length of the password to generate.
871. 
872.         Returns:
873.             Random password.
874.         """
875.         choices = string.ascii_letters + string.digits
876.         password = "".join([secrets.choice(choices) for _ in range(length)])
877.         return password
878. 
879.     def _config_force_https(self) -> None:
880.         """Config Discourse to force_https option based on charm configuration."""
881.         container = self.unit.get_container(CONTAINER_NAME)
882.         force_bool = str(self.config["force_https"]).lower()
883.         process = container.exec(
884.             [
885.                 os.path.join(DISCOURSE_PATH, "bin/rails"),
886.                 "runner",
887.                 f"SiteSetting.force_https={force_bool}",
888.             ],
889.             working_dir=DISCOURSE_PATH,
890.             user=CONTAINER_APP_USERNAME,
891.             environment=self._create_discourse_environment_settings(),
892.         )
893.         process.wait_output()
894. 
895.     def _on_anonymize_user_action(self, event: ActionEvent) -> None:
896.         """Anonymize data from a user.
897. 
898.         Args:
899.             event: Event triggering the anonymize_user action.
900.         """
901.         username = event.params["username"]
902.         container = self.unit.get_container(CONTAINER_NAME)
903.         if not container.can_connect():
904.             event.fail("Unable to connect to container, container is not ready")
905.             return
906. 
907.         process = container.exec(
908.             [
909.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
910.                 "exec",
911.                 "rake",
912.                 f"users:anonymize[{username}]",
913.             ],
914.             working_dir=DISCOURSE_PATH,
915.             user=CONTAINER_APP_USERNAME,
916.             environment=self._create_discourse_environment_settings(),
917.         )
918.         try:
919.             process.wait_output()
920.             event.set_results({"user": f"{username}"})
921.         except ExecError as ex:
922.             event.fail(
923.                 # Parameter validation errors are printed to stdout
924.                 # Ignore mypy warning when formatting stdout
925.                 f"Failed to anonymize user with username {username}:{ex.stdout}"  # type: ignore
926.             )
927. 
928.     def _start_service(self):
929.         """Start discourse."""
930.         logger.info("Starting discourse")
931.         container = self.unit.get_container(CONTAINER_NAME)
932.         if self._is_config_valid() and container.can_connect():
933.             layer_config = self._create_layer_config()
934.             container.add_layer(SERVICE_NAME, layer_config, combine=True)
935.             container.pebble.replan_services()
936. 
937.     def _stop_service(self):
938.         """Stop discourse, this operation is idempotent."""
939.         logger.info("Stopping discourse")
940.         container = self.unit.get_container(CONTAINER_NAME)
941.         if (
942.             container.can_connect()
943.             and SERVICE_NAME in container.get_plan().services
944.             and container.get_service(SERVICE_NAME).is_running()
945.         ):
946.             container.stop(CONTAINER_NAME)
947. 
948. 
949. if __name__ == "__main__":  # pragma: no cover
950.     main(DiscourseCharm, use_juju_for_storage=True)
```

</details>


---

<sub>⏱️ 57s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/2.23.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
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

<sub>⏱️ 1m 4s</sub>

### ✅ `bash`

**Check unit tests structure**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && ls tests/unit/ tests/unit_harness/ && cat tests/unit/test_charm.py | head -60

<details>
<summary>60 lines</summary>

```
tests/unit/:
conftest.py  test_charm.py

tests/unit_harness/:
__init__.py  helpers.py  test_charm.py
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Discourse K8s operator charm unit tests."""

import pytest
from ops import testing
from ops.model import ActiveStatus, BlockedStatus

from charm import (
    CONTAINER_NAME,
    INVALID_CORS_MESSAGE,
    OAUTH_RELATION_NAME,
    SERVICE_NAME,
    DiscourseCharm,
)


@pytest.mark.parametrize(
    "config, expected_origin, expected_status",
    [
        pytest.param(
            {
                "cors_origin": "*",
                "augment_cors_origin": True,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "https://cdn.test",
            },
            "*",
            ActiveStatus(),
            id="Wildcard disables augmentation",
        ),
        pytest.param(
            {
                "cors_origin": "",
                "augment_cors_origin": False,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "https://cdn.test",
            },
            "*",
            BlockedStatus(INVALID_CORS_MESSAGE),
            id="Raise error when invalid CORS config",
        ),
        pytest.param(
            {
                "cors_origin": "",
                "augment_cors_origin": True,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "",
            },
            "https://example.com",
            ActiveStatus(),
            id="Augment only with external_hostname (HTTPS)",
        ),
        pytest.param(
            {
                "cors_origin": "",
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 5s</sub>

### ✅ `bash`

**Check ops-tracing and ops-scenario versions**

$ pip index versions ops-tracing 2>/dev/null | head -3 && pip index versions ops-scenario 2>/dev/null | head -3

<details>
<summary>6 lines</summary>

```
ops-tracing (3.6.0)
Available versions: 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 0.9.6, 0.9.4, 0.9.3, 0.9.2, 0.9.1, 0.9.0
ops-scenario (8.6.0)
Available versions: 8.6.0, 8.5.2, 8.5.1, 8.5.0, 8.4.0, 8.3.1, 8.3.0, 8.2.0, 8.1.0, 8.0.0, 7.23.2, 7.23.1, 7.23.0, 7.22.0, 7.21.1, 7.21.0, 7.20.0, 7.19.4, 7.2.0, 7.1.3, 7.1.2, 7.1.1, 7.0.5, 7.0.4, 7.0.3, 7.0.2, 7.0.1, 7.0.0, 6.1.7, 6.1.6, 6.1.5, 6.1.4, 6.1.3, 6.1.2, 6.1.1, 6.1.0, 6.0.5, 6.0.4, 6.0.3, 6.0.2, 6.0.1, 6.0, 5.8.1, 5.8, 5.7.1, 5.7, 5.6.2, 5.6.1, 5.6, 5.5, 5.4.1, 5.4, 5.3.1, 5.3, 5.2.2, 5.2.1, 5.2, 5.1.3, 5.1.2, 5.1.1, 5.1.0, 5.0, 4.0.4.1, 4.0.4, 4.0.3, 4.0.2, 4.0.1, 4.0, 3.1, 3.0.2, 3.0.1, 2.2, 2.1.3.5, 2.1.3.4, 2.1.3.3, 2.1.3.2, 2.1.3.1, 2.1.3, 2.1.2.5, 2.1.2.4, 2.1.2.3, 2.1.2.2, 2.1.2.1, 2.1.1, 2.1.0, 2.0.5, 2.0.4, 2.0.0
  INSTALLED: 7.23.2
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 21s</sub>

### ✅ `bash`

**Check unit test conftest and size**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && cat tests/unit/conftest.py && echo "---" && cat tests/unit/test_charm.py | wc -l

<details>
<summary>76 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Discourse K8s operator charm fixtures."""

import pytest
from ops import testing

from charm import CONTAINER_NAME
from constants import DATABASE_NAME


@pytest.fixture(name="base_state")
def base_state_fixture(discourse_container, postgresql_relation, redis_relation):
    input_state = {
        "leader": True,
        "config": {},
        "containers": {discourse_container},
        "relations": [postgresql_relation, redis_relation],
    }
    yield input_state


@pytest.fixture(name="discourse_container")
def discourse_container_fixture():
    """Discourse container fixture."""
    yield testing.Container(
        name=CONTAINER_NAME,
        can_connect=True,
        execs=[
            testing.Exec(
                command_prefix=[
                    "/srv/discourse/app/bin/bundle",
                    "exec",
                    "rake",
                    "--trace",
                    "db:migrate",
                ],
                return_code=0,
                stdout="Migration successful\n",
                stderr="",
            ),
            testing.Exec(
                command_prefix=["/srv/discourse/app/bin/rails", "runner"],
                return_code=0,
                stdout="successful\n",
                stderr="",
            ),
        ],
    )  # type: ignore[call-arg]


@pytest.fixture(name="postgresql_relation")
def postgresql_relation_fixture():
    """Postgresql relation fixture."""
    relation_data = {
        "database": DATABASE_NAME,
        "endpoints": "dbhost:5432,dbhost-2:5432",
        "password": "somepasswd",  # nosec
        "username": "someuser",
    }
    yield testing.Relation(
        endpoint="database",
        interface="postgresql_client",
        remote_app_data=relation_data,
    )


@pytest.fixture(name="redis_relation")
def redis_relation_fixture():
    """Redis relation fixture."""
    relation_data = {
        0: {
            "hostname": "redis-host",
            "port": "1010",
        },
    }
    yield testing.Relation(
        endpoint="redis",
        interface="redis",
        remote_app_name="redis",
        remote_units_data=relation_data,
        remote_app_data={"leader-host": "redis-host"},
    )
---
233
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 21s</sub>

### ✅ `bash`

**Check for deprecated testing.Context.charm_spec usage**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && grep -n "charm_spec\|Context\|SCENARIO_BARE" tests/unit/test_charm.py | head -20

```
138:    ctx = testing.Context(DiscourseCharm)
183:    ctx = testing.Context(DiscourseCharm)
<exited with exit code 0>
```


---

<sub>⏱️ 1m 26s</sub>

### ✅ `bash`

**Read full unit test file**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && cat tests/unit/test_charm.py

<details>
<summary>216 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Discourse K8s operator charm unit tests."""

import pytest
from ops import testing
from ops.model import ActiveStatus, BlockedStatus

from charm import (
    CONTAINER_NAME,
    INVALID_CORS_MESSAGE,
    OAUTH_RELATION_NAME,
    SERVICE_NAME,
    DiscourseCharm,
)


@pytest.mark.parametrize(
    "config, expected_origin, expected_status",
    [
        pytest.param(
            {
                "cors_origin": "*",
                "augment_cors_origin": True,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "https://cdn.test",
            },
            "*",
            ActiveStatus(),
            id="Wildcard disables augmentation",
        ),
        pytest.param(
            {
                "cors_origin": "",
                "augment_cors_origin": False,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "https://cdn.test",
            },
            "*",
            BlockedStatus(INVALID_CORS_MESSAGE),
            id="Raise error when invalid CORS config",
        ),
        pytest.param(
            {
                "cors_origin": "",
                "augment_cors_origin": True,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "",
            },
            "https://example.com",
            ActiveStatus(),
            id="Augment only with external_hostname (HTTPS)",
        ),
        pytest.param(
            {
                "cors_origin": "",
                "augment_cors_origin": True,
                "external_hostname": "",
                "force_https": True,
                "s3_cdn_url": "",
            },
            "https://discourse-k8s",
            ActiveStatus(),
            id="Augment with external_hostname not explicitly defined",
        ),
        pytest.param(
            {
                "cors_origin": "",
                "augment_cors_origin": True,
                "external_hostname": "example.com",
                "force_https": False,
                "s3_cdn_url": "https://cdn.test",
            },
            "http://example.com,https://cdn.test",
            ActiveStatus(),
            id="Augment with both external_hostname (HTTP) and s3_cdn_url",
        ),
        pytest.param(
            {
                "cors_origin": "https://custom.origin",
                "augment_cors_origin": False,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "https://cdn.test",
            },
            "https://custom.origin",
            ActiveStatus(),
            id="User-defined cors_origin, no augmentation",
        ),
        pytest.param(
            {
                "cors_origin": "https://custom.origin",
                "augment_cors_origin": True,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "https://cdn.test",
            },
            "https://cdn.test,https://custom.origin,https://example.com",
            ActiveStatus(),
            id="User-defined cors_origin with augmentation enabled",
        ),
        pytest.param(
            {
                "cors_origin": "https://foo.com, https://bar.com",
                "augment_cors_origin": True,
                "external_hostname": "example.com",
                "force_https": False,
                "s3_cdn_url": "https://cdn.test",
            },
            "http://example.com,https://bar.com,https://cdn.test,https://foo.com",
            ActiveStatus(),
            id="Multiple user-defined cors_origins with augmentation",
        ),
        pytest.param(
            {
                "cors_origin": " https://foo.com , https://foo.com ",
                "augment_cors_origin": True,
                "external_hostname": "foo.com",
                "force_https": True,
                "s3_cdn_url": "https://foo.com",
            },
            "https://foo.com",
            ActiveStatus(),
            id="Duplicated origins across cors_origin and augmentation",
        ),
    ],
)
def test_get_cors_origin_behavior(config, expected_origin, expected_status, base_state):
    """
    arrange: deploy charm with CORS-related config
    act: configure charm with varying CORS inputs
    assert: DISCOURSE_CORS_ORIGIN matches expected result
    """
    ctx = testing.Context(DiscourseCharm)

    base_state["config"] = config

    state_in = testing.State(**base_state)
    container = state_in.get_container(CONTAINER_NAME)

    state_out = ctx.run(ctx.on.pebble_ready(container), state_in)
    plan_out = state_out.get_container(container.name).plan

    assert state_out.unit_status == expected_status
    if expected_status == ActiveStatus():  # plan is empty when in BlockedStatus
        assert (
            plan_out.services[SERVICE_NAME].environment["DISCOURSE_CORS_ORIGIN"] == expected_origin
        )


@pytest.mark.parametrize(
    "config, expected_status",
    [
        pytest.param(
            {"external_hostname": "discourse.example.com", "force_https": True},
            ActiveStatus(),
            id="Valid config",
        ),
        pytest.param(
            {"external_hostname": "discourse.example.com", "force_https": False},
            BlockedStatus(
                "An oauth relation cannot be established without 'force_https' being true"
            ),
            id="Missing force_https",
        ),
        pytest.param(
            {"force_https": True},
            BlockedStatus("Invalid OAuth client config, check the logs for more info."),
            id="external_hostname not set",
        ),
    ],
)
def test_oauth_integration(base_state, config, expected_status):
    """
    arrange: deploy charm and add oauth relation with provider data.
    act: trigger pebble ready or relation changed.
    assert: charm configures OIDC environment variables in the container.
    """
    ctx = testing.Context(DiscourseCharm)

    # Define the relation
    oauth_relation = testing.Relation(
        endpoint=OAUTH_RELATION_NAME,
        interface="oauth",
        remote_app_data={
            "issuer_url": "https://auth.example.com",
            "authorization_endpoint": "https://auth.example.com/auth",
            "token_endpoint": "https://auth.example.com/token",  # nosec B105
            "introspection_endpoint": "https://auth.example.com/introspect",
            "userinfo_endpoint": "https://auth.example.com/userinfo",
            "jwks_endpoint": "https://auth.example.com/jwks",
            "scope": "openid email",
            "client_id": "my-client-id",
            "client_secret": "my-super-secret",  # nosec B105
        },
    )

    base_state["relations"].append(oauth_relation)
    base_state["config"] = config

    state_in = testing.State(**base_state)

    # Run the charm
    state_out = ctx.run(ctx.on.relation_joined(oauth_relation), state_in)

    assert state_out.unit_status == expected_status
    if expected_status == ActiveStatus():
        # Check if OIDC env vars are set in the plan
        plan = state_out.get_container(CONTAINER_NAME).plan
        env = plan.services[SERVICE_NAME].environment

        assert env["DISCOURSE_OPENID_CONNECT_ENABLED"] == "true"
        assert (
            env["DISCOURSE_OPENID_CONNECT_DISCOVERY_DOCUMENT"]
            == "https://auth.example.com/.well-known/openid-configuration"
        )
        assert env["DISCOURSE_OPENID_CONNECT_CLIENT_ID"] == "my-client-id"
        assert env["DISCOURSE_OPENID_CONNECT_CLIENT_SECRET"] == "my-super-secret"
        assert env["DISCOURSE_OPENID_CONNECT_AUTHORIZE_SCOPE"] == "openid email"

        # Also check if the charm sent its client config
        relation = next(r for r in state_out.relations if r.id == oauth_relation.id)
        assert (
            relation.local_app_data["redirect_uri"]
            == "https://discourse.example.com/auth/oidc/callback"
        )
        assert relation.local_app_data["scope"] == "openid email"
        assert relation.local_app_data["grant_types"] == '["authorization_code"]'
        assert relation.local_app_data["token_endpoint_auth_method"] == "client_secret_basic"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 31s</sub>

### ✅ `bash`

**Read full pyproject.toml**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && cat pyproject.toml

<details>
<summary>142 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

[project]
name = "discourse-k8s-operator"
version = "0.0.0"
description = "Discourse is the modern forum for your community."
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.8",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Programming Language :: Python :: 3.14",
]
dependencies = [
  "cosl==1.6.0",
  "jsonschema==4.23.0",
  "ops==2.23.2",
  "pydantic==2.10.6",
]

[dependency-groups]
fmt = [
  "ruff",
]
lint = [
  "boto3",
  "bs4",
  "codespell",
  "jubilant==1.7.0",
  "mypy",
  "pep8-naming",
  "psycopg2-binary",
  "pytest",
  "pytest-asyncio",
  "pytest-operator",
  "python-magic",
  "requests",
  "ruff",
  "types-pyyaml",
  "types-requests",
]
unit = [
  "coverage[toml]",
  "ops[testing]",
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
  "boto3",
  "bs4",
  "debugpy",
  "jubilant==1.7.0",
  "protobuf==5.29.6",
  "psycopg2-binary",
  "pytest",
  "requests",
  "saml-test-helper @ git+https://github.com/canonical/saml-test-idp.git",
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

[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"
pythonpath = [ "lib", "src" ]

[tool.coverage.run]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true

[tool.mypy]
ignore_missing_imports = true
explicit_package_bases = true
namespace_packages = true
check_untyped_defs = true

[tool.bandit]
exclude_dirs = [ "/venv/" ]

[tool.bandit.assert_used]
skips = [ "*tests/*.py" ]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 31s</sub>

### ✅ `bash`

**Read oauth_observer and database files**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && cat src/oauth_observer.py && echo "---" && cat src/database.py

<details>
<summary>185 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""OAuth integration for Discourse."""

import logging
import typing

from charms.hydra.v0.oauth import (
    ClientConfig,
    ClientConfigError,
    OauthProviderConfig,
    OAuthRequirer,
)
from ops.charm import RelationBrokenEvent, RelationChangedEvent
from ops.framework import Object
from ops.model import BlockedStatus

from constants import OAUTH_RELATION_NAME, OAUTH_SCOPE

logger = logging.getLogger(__name__)


class OAuthObserver(Object):
    """OAuth integration for Discourse."""

    def __init__(
        self,
        charm,
        setup_and_activate_callback: typing.Callable[[], None],
        external_hostname_callback: typing.Callable[[], str],
    ):
        """Initialize OAuth integration.

        Args:
            charm: The charm object.
            setup_and_activate_callback: Callback to run setup and activation.
            external_hostname_callback: Callback to get the external hostname.
        """
        super().__init__(charm, OAUTH_RELATION_NAME)
        self.charm = charm
        self._oauth = OAuthRequirer(self.charm, relation_name=OAUTH_RELATION_NAME)
        self._setup_and_activate_callback = setup_and_activate_callback
        self._external_hostname_callback = external_hostname_callback
        self.client_config: ClientConfig | None = None
        self._generate_client_config()

        self.framework.observe(
            self.charm.on[OAUTH_RELATION_NAME].relation_changed, self._on_oauth_relation_changed
        )
        self.framework.observe(
            self.charm.on[OAUTH_RELATION_NAME].relation_joined, self._on_oauth_relation_changed
        )
        self.framework.observe(
            self.charm.on[OAUTH_RELATION_NAME].relation_created, self._on_oauth_relation_changed
        )
        self.framework.observe(
            self.charm.on[OAUTH_RELATION_NAME].relation_broken, self._on_oauth_relation_broken
        )

    def _on_oauth_relation_changed(self, _: RelationChangedEvent) -> None:
        """Handle oauth relation changed event."""
        self._generate_client_config()
        if not self.client_config:
            return
        try:
            self.client_config.validate()
        except ClientConfigError as e:
            # Block charm
            self.charm.unit.status = BlockedStatus(
                "Invalid OAuth client config, check the logs for more info."
            )
            logger.error("Invalid OAuth client config: %s", e)
            return
        self._oauth.update_client_config(self.client_config)
        self._setup_and_activate_callback()

    def _on_oauth_relation_broken(self, _: RelationBrokenEvent) -> None:
        """Handle the breaking of the oauth relation."""
        self._generate_client_config()
        self._setup_and_activate_callback()

    def _generate_client_config(self) -> None:
        """Generate OAuth client configuration."""
        if self.charm.model.get_relation(OAUTH_RELATION_NAME):
            self.client_config = ClientConfig(
                redirect_uri=f"https://{self._external_hostname_callback()}/auth/oidc/callback",
                scope=OAUTH_SCOPE,
                grant_types=["authorization_code"],
                token_endpoint_auth_method="client_secret_basic",  # nosec # noqa: S106
            )
        else:
            self.client_config = None

    def get_oidc_env(self) -> typing.Dict[str, typing.Any]:
        """Get the list of OIDC-related environment variables from the OAuth relation.

        If the oauth relation is not established, self.client_config will be None,
        and no env vars will be passed to Discourse.

        Similarly, if the relation is broken, Discourse will not be provided these env vars
        and unset the existing ones, effectively disabling OIDC.

        Returns:
            Dictionary with all the OIDC environment settings.
        """
        if self.client_config is None:
            return {}
        provider_info: OauthProviderConfig | None = self._oauth.get_provider_info()
        if not provider_info:
            return {}
        try:
            self.client_config.validate()
        except ClientConfigError as e:
            # Block charm if the client config is invalid
            # Client config should only fail if the external hostname is invalid,
            # i.e. not satisfying the regex URL from oauth library.
            # Other cases should not happen as the values are provided by the charm
            self.charm.unit.status = BlockedStatus(
                "Invalid OAuth client config, check the logs for more info."
            )
            logger.error("Invalid OAuth client config: %s", e)
            return {}
        oidc_env = {
            "DISCOURSE_OPENID_CONNECT_ENABLED": "true",
            "DISCOURSE_OPENID_CONNECT_DISCOVERY_DOCUMENT": f"{provider_info.issuer_url}"
            "/.well-known/openid-configuration",
            "DISCOURSE_OPENID_CONNECT_CLIENT_ID": provider_info.client_id,
            "DISCOURSE_OPENID_CONNECT_CLIENT_SECRET": provider_info.client_secret,
            "DISCOURSE_OPENID_CONNECT_AUTHORIZE_SCOPE": OAUTH_SCOPE,
            "DISCOURSE_OPENID_CONNECT_MATCH_BY_EMAIL": "true",
        }
        return oidc_env
---
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Provide the DatabaseObserver class to handle database relation and state."""

import typing

from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
from ops.charm import CharmBase
from ops.framework import Object

DATABASE_NAME = "discourse"


class DatabaseHandler(Object):
    """The Database relation observer."""

    def __init__(self, charm: CharmBase, relation_name):
        """Initialize the observer and register event handlers.

        Args:
            charm: The parent charm to attach the observer to.
            relation_name: The name of the database relation.
        """
        super().__init__(charm, "database-observer")
        self._charm = charm
        self.relation_name = relation_name
        self.database = DatabaseRequires(
            self._charm,
            relation_name=self.relation_name,
            database_name=DATABASE_NAME,
        )

    def get_relation_data(self) -> typing.Dict[str, str]:
        """Get database data from relation.

        Returns:
            Dict: Information needed for setting environment variables.
            Returns default if the relation data is not correctly initialized.
        """
        default = {
            "POSTGRES_USER": "",
            "POSTGRES_PASSWORD": "",  # nosec B105
            "POSTGRES_HOST": "",
            "POSTGRES_PORT": "",
            "POSTGRES_DB": "",
        }

        if self.model.get_relation(self.relation_name) is None:
            return default

        relation_id = self.database.relations[0].id
        relation_data = self.database.fetch_relation_data()[relation_id]

        endpoints = relation_data.get("endpoints", "").split(",")
        if len(endpoints) < 1:
            return default

        primary_endpoint = endpoints[0].split(":")
        if len(primary_endpoint) < 2:
            return default

        data = {
            "POSTGRES_USER": relation_data.get("username"),
            "POSTGRES_PASSWORD": relation_data.get("password"),
            "POSTGRES_HOST": primary_endpoint[0],
            "POSTGRES_PORT": primary_endpoint[1],
            "POSTGRES_DB": relation_data.get("database"),
        }

        if None in (
            data["POSTGRES_USER"],
            data["POSTGRES_PASSWORD"],
            data["POSTGRES_DB"],
        ):
            return default

        return data

    def is_relation_ready(self) -> bool:
        """Check if the relation is ready.

        Returns:
            bool: returns True if the relation is ready.
        """
        return self.get_relation_data()["POSTGRES_HOST"] != ""
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 38s</sub>

### 💬 Copilot

Now I have a thorough understanding. Let me check the config.yaml and actions.yaml and then look at what's available in ops 3.x for typed schemas.

---

<sub>⏱️ 1m 38s</sub>

### ✅ `bash`

**Check config and actions schemas**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && head -80 config.yaml && echo "---" && cat actions.yaml

<details>
<summary>112 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
options:
  augment_cors_origin:
    type: boolean
    description: |
      Appends external_hostname (with http/https) and s3_cdn_url to the list of
      allowed CORS origins. Has no effect if 'cors_origin' is "*". 
      To rely only on automatic cors origins, set 'cors_origin' to an empty string.
    default: true
  cors_origin:
    type: string
    description: |
      Comma-separated list of allowed CORS origins. Defaults to "*", allowing all
      origins. To restrict access, provide specific origins or set to an empty string
      to rely solely on 'augment_cors_origin' if enabled.
    default: ""
  developer_emails:
    type: string
    description: "Comma delimited list of email addresses that should have developer level access."
    default: ""
  enable_cors:
    type: boolean
    description: "Enable Cross-origin Resource Sharing (CORS) at the application level (required for SSO)."
    default: true
  external_hostname:
    type: string
    description: "External hostname this discourse instance responds to. Defaults to application name."
    default: ""
  force_https:
    type: boolean
    description: Configure Discourse to use https.
    default: false
  force_saml_login:
    type: boolean
    description: "Force SAML login (full screen, no local database logins)."
    default: false
  max_category_nesting:
    type: int
    description: "Maximum category nesting allowed. Minimum is 2, maximum is 3."
    default: 2
  saml_sync_groups:
    type: string
    description: "Comma-separated list of groups to sync from SAML provider."
    default: ""
  smtp_address:
    type: string
    description: "Hostname / IP that should be used to send SMTP mail."
    default: ""
  smtp_authentication:
    type: string
    description: "Type of smtp authentication to use. Valid values: none, login, plain, cram_md5."
    default: "none"
  smtp_domain:
    type: string
    description: "Hostname that email sent by this discourse should appear to come from."
    default: ""
  smtp_enable_start_tls:
    type: string
    description: "Enable TLS encryption for smtp connections."
    default: "true"
  smtp_force_tls:
    type: string
    description: "Force implicit TLS as per RFC 8314 3.3."
    default: "false"
  smtp_openssl_verify_mode:
    type: string
    description: "Should discourse verify SSL certs."
    default: "none"
  smtp_password:
    type: string
    description: "Password to use when sending mail via SMTP."
    default: ""
  smtp_port:
    type: int
    description: "Port to use when connecting to SMTP server."
    default: 587
  smtp_username:
    type: string
    description: "Username to use when sending mail via SMTP."
---
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
anonymize-user:
  description: Anonymize a user.
  params:
    username:
      type: string
      description: The unique identifier of the user to anonymize.
  required: [username]
create-user:
  description: Create a new user.
  params:
    email:
      type: string
      description: User email.
    admin:
      type: boolean
      description: Whether the user should be an admin.
    active:
      type: boolean
      description: Whether the user should be email-verified and active.
      default: true
  required: [email]
promote-user:
  description: Promote a user to admin.
  params:
    email:
      type: string
      description: User email.
  required: [email]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 38s</sub>

### ✅ `bash`

**Read constants file**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && cat src/constants.py

<details>
<summary>48 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Constants for Discourse charm."""

import typing
from collections import defaultdict

DATABASE_NAME = "discourse"
DISCOURSE_PATH = "/srv/discourse/app"
THROTTLE_LEVELS: typing.Dict = defaultdict(dict)
THROTTLE_LEVELS["none"] = {
    "DISCOURSE_MAX_REQS_PER_IP_MODE": "none",
    "DISCOURSE_MAX_REQS_RATE_LIMIT_ON_PRIVATE": "false",
}
THROTTLE_LEVELS["permissive"] = {
    "DISCOURSE_MAX_REQS_PER_IP_MODE": "warn+block",
    "DISCOURSE_MAX_REQS_PER_IP_PER_MINUTE": "1000",
    "DISCOURSE_MAX_REQS_PER_IP_PER_10_SECONDS": "100",
    "DISCOURSE_MAX_USER_API_REQS_PER_MINUTE": "3000",
    "DISCOURSE_MAX_ASSET_REQS_PER_IP_PER_10_SECONDS": "400",
    "DISCOURSE_MAX_REQS_RATE_LIMIT_ON_PRIVATE": "false",
    "DISCOURSE_MAX_USER_API_REQS_PER_DAY": "30000",
    "DISCOURSE_MAX_ADMIN_API_REQS_PER_KEY_PER_MINUTE": "3000",
}
THROTTLE_LEVELS["strict"] = {
    "DISCOURSE_MAX_REQS_PER_IP_MODE": "block",
    "DISCOURSE_MAX_REQS_PER_IP_PER_MINUTE": "200",
    "DISCOURSE_MAX_REQS_PER_IP_PER_10_SECONDS": "50",
    "DISCOURSE_MAX_USER_API_REQS_PER_MINUTE": "100",
    "DISCOURSE_MAX_ASSET_REQS_PER_IP_PER_10_SECONDS": "200",
    "DISCOURSE_MAX_REQS_RATE_LIMIT_ON_PRIVATE": "false",
}
LOG_PATHS = [
    f"{DISCOURSE_PATH}/log/production.log",
    f"{DISCOURSE_PATH}/log/unicorn.stderr.log",
    f"{DISCOURSE_PATH}/log/unicorn.stdout.log",
]
MAX_CATEGORY_NESTING_LEVELS = [2, 3]
PROMETHEUS_PORT = 3000
REQUIRED_S3_SETTINGS = ["s3_access_key_id", "s3_bucket", "s3_region", "s3_secret_access_key"]
SCRIPT_PATH = "/srv/scripts"
SERVICE_NAME = "discourse"
CONTAINER_NAME = "discourse"
CONTAINER_APP_USERNAME = "_daemon_"
SERVICE_PORT = 3000
SETUP_COMPLETED_FLAG_FILE = "/run/discourse-k8s-operator/setup_completed"
DATABASE_RELATION_NAME = "database"
OAUTH_RELATION_NAME = "oauth"
OAUTH_SCOPE = "openid email"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 0s</sub>

### ✅ `bash`

**Check ops.ConfigBase API**

$ pip show ops 2>/dev/null | grep Location && python3 -c "import ops; help(ops.ConfigBase)" 2>/dev/null | head -40 || pip install ops==3.6.0 -q && python3 -c "import ops; help(ops.ConfigBase)" 2>/dev/null | head -60

```
Location: /home/ubuntu/.local/lib/python3.12/site-packages
<exited with exit code 0>
```


---

<sub>⏱️ 2m 4s</sub>

### ✅ `bash`

**Install ops 3.6.0 and check config-related API**

$ pip install "ops==3.6.0" -q && python3 -c "import ops; print(dir(ops))" 2>/dev/null | tr ',' '\n' | grep -i -E "config|action|relation" | head -20

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

<sub>⏱️ 2m 10s</sub>

### ✅ `bash`

**Check ops API in uv environment**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && uv run --group unit python -c "import ops; print(dir(ops))" 2>/dev/null | tr ',' '\n' | grep -i -E "config|action" | head -20

<details>
<summary>6 lines</summary>

```
['ActionEvent'
 'ActionMeta'
 'ConfigChangedEvent'
 'ConfigData'
 'ConfigMeta'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 17s</sub>

### ✅ `bash`

**Check current ops version and available features**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && uv run --group unit python -c "
import inspect, ops
# Check if ConfigBase exists in ops 2.23.2
print('Has ConfigBase:', hasattr(ops, 'ConfigBase'))
print('Has ActionParams:', hasattr(ops, 'ActionParams'))
# Check what ops version we have
print('ops version:', ops.version_info if hasattr(ops, 'version_info') else 'unknown')
import importlib.metadata
print('ops version:', importlib.metadata.version('ops'))
"

```
Has ConfigBase: False
Has ActionParams: False
ops version: unknown
ops version: 2.23.2
<exited with exit code 0>
```


---

<sub>⏱️ 2m 24s</sub>

### ✅ `bash`

**Check ops API for config/action base classes**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && uv run --group unit python -c "
import ops
# check what's in ops
attrs = [a for a in dir(ops) if 'Config' in a or 'Action' in a or 'Params' in a or 'Base' in a]
print(attrs)
"

```
['ActionEvent', 'ActionMeta', 'CharmBase', 'ConfigChangedEvent', 'ConfigData', 'ConfigMeta', 'ContainerBase', 'EventBase', 'StatusBase']
<exited with exit code 0>
```


---

<sub>⏱️ 2m 31s</sub>

### ✅ `bash`

**Install ops 3.6.0 in a venv and check API**

$ cd /tmp && python3 -m venv ops_new && ops_new/bin/pip install "ops==3.6.0" -q && ops_new/bin/python -c "
import ops
attrs = [a for a in dir(ops) if 'Config' in a or 'Action' in a or 'Params' in a or 'Base' in a or 'Schema' in a]
print(sorted(attrs))
" 2>&1

<details>
<summary>8 lines</summary>

```
The virtual environment was not created successfully because ensurepip is not
available.  On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.

    apt install python3.12-venv

You may need to use sudo with that command.  After installing the python3-venv
package, recreate your virtual environment.

Failing command: /tmp/ops_new/bin/python3
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 2m 36s</sub>

### ✅ `bash`

**Install ops 3.6.0 in uv venv and check API**

$ uv venv /tmp/ops36-venv && /tmp/ops36-venv/bin/pip install "ops==3.6.0" -q 2>&1 | tail -3 && /tmp/ops36-venv/bin/python -c "
import ops
attrs = [a for a in dir(ops) if 'Config' in a or 'Action' in a or 'Params' in a or 'Base' in a or 'Schema' in a]
print(sorted(attrs))
"

<details>
<summary>8 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: /tmp/ops36-venv
Activate with: source /tmp/ops36-venv/bin/activate
bash: /tmp/ops36-venv/bin/pip: No such file or directory
Traceback (most recent call last):
  File "<string>", line 2, in <module>
ModuleNotFoundError: No module named 'ops'
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 3m 14s</sub>

### ✅ `bash`

**Install ops 3.6.0 properly in uv venv**

$ uv venv /tmp/ops36-venv && uv pip install --python /tmp/ops36-venv "ops==3.6.0" -q 2>&1 | tail -3 && /tmp/ops36-venv/bin/python -c "
import ops, importlib.metadata
print('ops version:', importlib.metadata.version('ops'))
attrs = [a for a in dir(ops) if 'Config' in a or 'Action' in a or 'Params' in a or 'Base' in a or 'Schema' in a]
print(sorted(attrs))
"

<details>
<summary>5 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: /tmp/ops36-venv
? A virtual environment already exists at `/tmp/ops36-venv`. Do you want to replace it? [y/n] › yes

hint: Use the `--clear` flag or set `UV_VENV_CLEAR=1` to skip this prompt
<command with shellId: 21 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 3m 18s</sub>

### ✅ `write_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "21",
  "input": "y\n",
  "delay": 15
}
```

</details>

<details>
<summary>8 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: /tmp/ops36-venv
? A virtual environment already exists at `/tmp/ops36-venv`. Do you want to replace it? [y/n] › yes

hint: Use the `--clear` flag or set `UV_VENV_CLEAR=1` to skip this prompt✔ A virtual environment already exists at `/tmp/ops36-venv`. Do you want to replace it? · yes
Activate with: source /tmp/ops36-venv/bin/activate
ops version: 3.6.0
['ActionEvent', 'ActionMeta', 'CharmBase', 'ConfigChangedEvent', 'ConfigData', 'ConfigMeta', 'ContainerBase', 'EventBase', 'StatusBase']
<command with id: 21 exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 24s</sub>

### ✅ `bash`

**Inspect config and action related classes in ops 3.6.0**

$ /tmp/ops36-venv/bin/python -c "
import ops
# Look for config/action related classes
import inspect
for name, obj in inspect.getmembers(ops):
    if inspect.isclass(obj) and ('config' in name.lower() or 'action' in name.lower() or 'param' in name.lower()):
        print(name, obj.__bases__)
"

<details>
<summary>6 lines</summary>

```
ActionEvent (<class 'ops.framework.EventBase'>,)
ActionMeta (<class 'object'>,)
ConfigChangedEvent (<class 'ops.charm.HookEvent'>,)
ConfigData (<class 'ops.model._GenericLazyMapping'>,)
ConfigMeta (<class 'object'>,)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 29s</sub>

### ✅ `bash`

**Look at ops.testing contents**

$ /tmp/ops36-venv/bin/python -c "
from ops._private import harness
import inspect
# Look at all modules
import ops.charm, ops.model, ops.testing
print('ops.testing dir:', [x for x in dir(ops.testing) if not x.startswith('_')])
"

```
ops.testing dir: ['ActionFailed', 'ActionOutput', 'AppUnitOrName', 'CharmBase', 'CharmMeta', 'CharmType', 'Container', 'ExecArgs', 'ExecHandler', 'ExecProcess', 'ExecResult', 'Harness', 'ReadableBuffer', 'RelationNotFoundError', 'RelationRole', 'YAMLStringOrFile', 'annotations', 'charm', 'framework', 'model', 'pebble', 'storage']
<exited with exit code 0>
```


---

<sub>⏱️ 3m 35s</sub>

### ✅ `bash`

**Install ops[testing] and check testing API**

$ uv pip install --python /tmp/ops36-venv "ops[testing]==3.6.0" -q 2>&1 | tail -3 && /tmp/ops36-venv/bin/python -c "
from ops import testing
print([x for x in dir(testing) if not x.startswith('_')])
"

```
['ActionFailed', 'ActionOutput', 'ActiveStatus', 'Address', 'AnyJson', 'AppUnitOrName', 'BindAddress', 'BlockedStatus', 'CharmBase', 'CharmEvents', 'CharmMeta', 'CharmType', 'CheckInfo', 'CloudCredential', 'CloudSpec', 'Container', 'Context', 'DeferredEvent', 'ErrorStatus', 'Exec', 'ExecArgs', 'ExecHandler', 'ExecProcess', 'ExecResult', 'Harness', 'ICMPPort', 'JujuLogLine', 'MaintenanceStatus', 'Manager', 'Model', 'Mount', 'Network', 'Notice', 'PeerRelation', 'Port', 'RawDataBagContents', 'RawSecretRevisionContents', 'ReadableBuffer', 'Relation', 'RelationBase', 'RelationNotFoundError', 'RelationRole', 'Resource', 'Secret', 'State', 'Storage', 'StoredState', 'SubordinateRelation', 'TCPPort', 'UDPPort', 'UnitID', 'UnknownStatus', 'WaitingStatus', 'YAMLStringOrFile', 'annotations', 'charm', 'errors', 'framework', 'layer_from_rockcraft', 'model', 'pebble', 'storage']
<exited with exit code 0>
```


---

<sub>⏱️ 3m 41s</sub>

### ✅ `bash`

**Check for config-as-class API in ops 3.6.0**

$ /tmp/ops36-venv/bin/python -c "
import ops
# Check if 'load_config' exists
print('load_config:', hasattr(ops, 'load_config'))
print('CharmBase.load_config:', hasattr(ops.CharmBase, 'load_config'))
# Look for config-as-class related APIs
import inspect
for name in dir(ops.charm):
    if 'config' in name.lower() or 'load' in name.lower():
        print('charm module:', name)
for name in dir(ops.model):
    if 'config' in name.lower() or 'load' in name.lower():
        print('model module:', name)
"

<details>
<summary>10 lines</summary>

```
load_config: False
CharmBase.load_config: True
charm module: ConfigChangedEvent
charm module: ConfigMeta
charm module: PayloadMeta
charm module: WorkloadEvent
charm module: __loader__
model module: ConfigData
model module: __loader__
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 45s</sub>

### ✅ `bash`

**Check CharmBase.load_config signature**

$ /tmp/ops36-venv/bin/python -c "
import ops, inspect
# Check CharmBase.load_config
print(inspect.getsource(ops.CharmBase.load_config))
"

<details>
<summary>84 lines</summary>

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
                    backend=self.model._backend,
                    id=value,
                )
            config[attr] = value
        try:
            return cls(*args, **config)
        except ValueError as e:
            if errors == 'raise':
                raise
            # We exit with a zero code because we don't want Juju to retry
            # (the config needs to be fixed by the Juju user), and we don't
            # want the status we just set to be overridden by an error
            # status.
            self.unit.status = model.BlockedStatus(f'Invalid config: {e}')
            raise _Abort(0) from e
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 51s</sub>

### ✅ `bash`

**Check ActionEvent params attribute**

$ /tmp/ops36-venv/bin/python -c "
import ops, inspect
# Check ActionEvent params as class
ev = ops.ActionEvent
print(inspect.getsource(ev.params.fget if hasattr(ev.params, 'fget') else ev.params))
" 2>&1 | head -30

```
Traceback (most recent call last):
  File "<string>", line 5, in <module>
AttributeError: type object 'ActionEvent' has no attribute 'params'
<exited with exit code 0>
```


---

<sub>⏱️ 3m 55s</sub>

### ✅ `bash`

**Check ActionEvent.load_params**

$ /tmp/ops36-venv/bin/python -c "
import ops, inspect
# Check ActionEvent.load_params
print(hasattr(ops.ActionEvent, 'load_params'))
if hasattr(ops.ActionEvent, 'load_params'):
    print(inspect.getsource(ops.ActionEvent.load_params))
"

<details>
<summary>61 lines</summary>

```
True
    def load_params(
        self,
        cls: type[_T],
        *args: Any,
        errors: Literal['raise', 'fail'] = 'raise',
        **kwargs: Any,
    ) -> _T:
        """Load the action parameters into an instance of an action class.

        The raw Juju action parameters are passed to the action class's
        ``__init__`` method as keyword arguments, with dashes in names
        converted to underscores.

        For dataclasses and Pydantic ``BaseModel`` subclasses, only fields in
        the Juju action parameters that have a matching field in the class are
        passed as arguments.

        For example::

            class BackupParams(pydantic.BaseModel):
                filename: str

            def _on_do_backup(self, event: ops.ActionEvent):
                params = event.load_params(BackupParams)
                # params.filename contains the value passed by the Juju user.

        Any additional positional or keyword arguments will be passed through to
        the action class ``__init__``.

        Args:
            cls: A class that will accept the Juju parameters as keyword
                arguments, and raise ``ValueError`` if validation fails.
            errors: what to do if the parameters are invalid. If ``fail``, this
                will set the action to failed with an appropriate message and
                then immediately exit. If ``raise``, ``load_params`` will not
                catch any exceptions, leaving the charm to handle errors.
            args: positional arguments to pass through to the action class.
            kwargs: keyword arguments to pass through to the action class.

        Returns:
            An instance of the action class that was provided in the ``cls``
            argument with the provided parameter values.

        Raises:
            ValueError: if ``errors`` is set to ``raise`` and instantiating the
                action class raises a ValueError.
        """
        try:
            fields = _juju_fields(cls)
        except ValueError:
            fields = None
        params: dict[str, Any] = kwargs.copy()
        for key, value in sorted(self.params.items()):
            attr = key.replace('-', '_')
            if fields is None:
                params[attr] = value
            else:
                if attr not in fields:
                    continue
                params[fields[attr]] = value
        try:
            return cls(*args, **params)
        except ValueError as e:
            if errors == 'raise':
                raise
            self.fail(f'Error in action parameters: {e}')
            from ._main import _Abort

            raise _Abort(0) from e
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 35s</sub>

### ✅ `bash`

**Read full config.yaml**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && cat config.yaml

<details>
<summary>151 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
options:
  augment_cors_origin:
    type: boolean
    description: |
      Appends external_hostname (with http/https) and s3_cdn_url to the list of
      allowed CORS origins. Has no effect if 'cors_origin' is "*". 
      To rely only on automatic cors origins, set 'cors_origin' to an empty string.
    default: true
  cors_origin:
    type: string
    description: |
      Comma-separated list of allowed CORS origins. Defaults to "*", allowing all
      origins. To restrict access, provide specific origins or set to an empty string
      to rely solely on 'augment_cors_origin' if enabled.
    default: ""
  developer_emails:
    type: string
    description: "Comma delimited list of email addresses that should have developer level access."
    default: ""
  enable_cors:
    type: boolean
    description: "Enable Cross-origin Resource Sharing (CORS) at the application level (required for SSO)."
    default: true
  external_hostname:
    type: string
    description: "External hostname this discourse instance responds to. Defaults to application name."
    default: ""
  force_https:
    type: boolean
    description: Configure Discourse to use https.
    default: false
  force_saml_login:
    type: boolean
    description: "Force SAML login (full screen, no local database logins)."
    default: false
  max_category_nesting:
    type: int
    description: "Maximum category nesting allowed. Minimum is 2, maximum is 3."
    default: 2
  saml_sync_groups:
    type: string
    description: "Comma-separated list of groups to sync from SAML provider."
    default: ""
  smtp_address:
    type: string
    description: "Hostname / IP that should be used to send SMTP mail."
    default: ""
  smtp_authentication:
    type: string
    description: "Type of smtp authentication to use. Valid values: none, login, plain, cram_md5."
    default: "none"
  smtp_domain:
    type: string
    description: "Hostname that email sent by this discourse should appear to come from."
    default: ""
  smtp_enable_start_tls:
    type: string
    description: "Enable TLS encryption for smtp connections."
    default: "true"
  smtp_force_tls:
    type: string
    description: "Force implicit TLS as per RFC 8314 3.3."
    default: "false"
  smtp_openssl_verify_mode:
    type: string
    description: "Should discourse verify SSL certs."
    default: "none"
  smtp_password:
    type: string
    description: "Password to use when sending mail via SMTP."
    default: ""
  smtp_port:
    type: int
    description: "Port to use when connecting to SMTP server."
    default: 587
  smtp_username:
    type: string
    description: "Username to use when sending mail via SMTP."
    default: ""
  s3_access_key_id:
    type: string
    description: |
      The S3 access key ID to use.

      Sets DISCOURSE_S3_ACCESS_KEY_ID.
      Required if s3_enabled is true.
    default: ""
  s3_backup_bucket:
    type: string
    description: |
      The S3 bucket to use for backups.

      Sets DISCOURSE_S3_BACKUP_BUCKET.
      Also sets DISCOURSE_BACKUP_LOCATION=s3.
    default: ""
  s3_bucket:
    type: string
    description: |
      The S3 bucket to use.

      Sets DISCOURSE_S3_BUCKET.
      Required if s3_enabled is true.
    default: ""
  s3_cdn_url:
    type: string
    description: |
      The S3 Content Delivery Network URL.

      Sets DISCOURSE_S3_CDN_URL.
    default: ""
  s3_enabled:
    type: boolean
    description: |
      Store uploaded objects in an S3-compatible object storage service instead of a local directory.

      If true, sets DISCOURSE_USE_S3=true.
      Check https://meta.discourse.org/t/using-object-storage-for-uploads-s3-clones/148916 for more details.
    default: false
  s3_endpoint:
    type: string
    description: |
      The S3 endpoint to use.  This may be a non-Amazon S3-compatible endpoint.

      Sets DISCOURSE_S3_ENDPOINT
    default: "https://s3.amazonaws.com"
  s3_region:
    type: string
    description: |
      The S3 region to use.

      Sets DISCOURSE_S3_REGION.
      Required if s3_enabled is true.
    default: ""
  s3_secret_access_key:
    type: string
    description: |
      The S3 secret key to use.

      Sets DISCOURSE_S3_SECRET_ACCESS_KEY.
      Required if s3_enabled is true.
    default: ""
  s3_install_cors_rule:
    type: boolean
    description: |
      Will discourse set cors rule on the S3 bucket.

      Sets DISCOURSE_S3_INSTALL_CORS_RULE
    default: true
  throttle_level:
    type: string
    description: "Throttle level - blocks excessive usage by ip. Accepted values: none, permissive, strict."
    default: none
  sidekiq_max_memory:
    description: Maximum memory for sidekiq in megabytes. This configuration
      will set the UNICORN_SIDEKIQ_MAX_RSS environment variable.
    type: int
    default: 1000
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 12s</sub>

### 💬 Copilot

Now I have a complete picture. Let me set up the plan and create the branch.

---

<sub>⏱️ 5m 12s</sub>

### ✅ `sql`

**Create todo items**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create todo items",
  "query": "\nINSERT INTO todos (id, title, description, status) VALUES\n  ('branch', 'Create upgrade branch', 'Create git branch upgrade-ops-3.6.0', 'pending'),\n  ('pyproject', 'Bump ops version in pyproject.toml', 'Update ops==2.23.2 to ops==3.6.0; update requires-python to >=3.10; remove Python 3.8 and 3.9 classifiers', 'pending'),\n  ('tox-env', 'Set SCENARIO_BARE_CHARM_ERRORS in tox.toml', 'Add SCENARIO_BARE_CHARM_ERRORS=true to unit test env in tox.toml so test exceptions are not wrapped in UncaughtCharmError', 'pending'),\n  ('config-class', 'Add typed DiscourseConfig class', 'Define DiscourseConfig dataclass covering all config.yaml options; add _charm_config property to DiscourseCharm; replace all self.config[...] accesses with typed attributes', 'pending'),\n  ('action-params', 'Add typed action param classes', 'Define PromoteUserParams, CreateUserParams, AnonymizeUserParams dataclasses; update action handlers to use event.load_params()', 'pending'),\n  ('uv-lock', 'Update uv.lock', 'Run uv lock to regenerate uv.lock after ops version bump', 'pending'),\n  ('tests', 'Run tests to verify', 'Run tox -e unit to verify all tests pass after changes', 'pending');\n\nINSERT INTO todo_deps (todo_id, depends_on) VALUES\n  ('pyproject', 'branch'),\n  ('tox-env', 'branch'),\n  ('config-class', 'pyproject'),\n  ('action-params', 'pyproject'),\n  ('uv-lock', 'pyproject'),\n  ('tests', 'config-class'),\n  ('tests', 'action-params'),\n  ('tests', 'tox-env'),\n  ('tests', 'uv-lock');\n"
}
```

</details>

```
0 row(s) inserted.
```


---

<sub>⏱️ 5m 17s</sub>

### ✅ `bash`

**Create upgrade branch**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && git checkout -b upgrade-ops-3.6.0

```
Switched to a new branch 'upgrade-ops-3.6.0'
<exited with exit code 0>
```


---

<sub>⏱️ 5m 21s</sub>

### ✅ `sql`

**Mark branch done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark branch done",
  "query": "UPDATE todos SET status = 'done' WHERE id = 'branch';"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 5m 29s</sub>

### 💬 Copilot

Now let me update pyproject.toml:

---

<sub>⏱️ 5m 29s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/pyproject.toml**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 5m 35s</sub>

### 💬 Copilot

Now add SCENARIO_BARE_CHARM_ERRORS to tox.toml:

---

<sub>⏱️ 5m 35s</sub>

### ✅ `bash`

**Find unit test env in tox.toml**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && grep -n "unit\|SCENARIO\|set_env" tox.toml | head -30

<details>
<summary>8 lines</summary>

```
6:env_list = [ "lint", "unit", "static", "coverage-report" ]
23:[env_run_base.set_env]
46:[env.unit]
47:description = "Run unit tests"
64:dependency_groups = [ "unit" ]
84:    "--ignore={[vars]tst_path}{/}unit",
85:    "--ignore={[vars]tst_path}{/}unit_harness",
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 39s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tox.toml**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tox.toml (lines 46-70)

<details>
<summary>25 lines</summary>

```
46. [env.unit]
47. description = "Run unit tests"
48. commands = [
49.   [
50.     "coverage",
51.     "run",
52.     "--source={[vars]src_path}",
53.     "-m",
54.     "pytest",
55.     "--ignore={[vars]tst_path}{/}integration",
56.     "-v",
57.     "--tb",
58.     "native",
59.     "-s",
60.     { replace = "posargs", extend = true },
61.   ],
62.   [ "coverage", "report" ],
63. ]
64. dependency_groups = [ "unit" ]
65. 
66. [env.coverage-report]
67. description = "Create test coverage report"
68. commands = [ [ "coverage", "report" ] ]
69. dependency_groups = [ "coverage-report" ]
70.
```

</details>


---

<sub>⏱️ 5m 44s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tox.toml**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tox.toml

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tox.toml updated with changes.
```


---

<sub>⏱️ 5m 49s</sub>

### 💬 Copilot

Now let me implement the typed config class and action params. First, let me create a `DiscourseConfig` dataclass in constants.py or a new config.py file:

---

<sub>⏱️ 5m 49s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 1-60)

<details>
<summary>60 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2026 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Charm for Discourse on kubernetes."""
6. 
7. import base64
8. import hashlib
9. import logging
10. import os.path
11. import secrets
12. import string
13. import typing
14. from collections import namedtuple
15. 
16. import ops
17. from charms.data_platform_libs.v0.data_interfaces import (
18.     DatabaseCreatedEvent,
19.     DatabaseEndpointsChangedEvent,
20. )
21. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
22. from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
23. from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route
24. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
25. from charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires
26. from charms.rolling_ops.v0.rollingops import RollingOpsManager
27. from charms.saml_integrator.v0.saml import (
28.     DEFAULT_RELATION_NAME,
29.     SamlDataAvailableEvent,
30.     SamlRequires,
31. )
32. from ops.charm import ActionEvent, CharmBase, HookEvent, RelationBrokenEvent
33. from ops.main import main
34. from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus
35. from ops.pebble import ExecError, ExecProcess, Plan
36. 
37. from constants import (
38.     CONTAINER_APP_USERNAME,
39.     CONTAINER_NAME,
40.     DATABASE_RELATION_NAME,
41.     DISCOURSE_PATH,
42.     LOG_PATHS,
43.     MAX_CATEGORY_NESTING_LEVELS,
44.     OAUTH_RELATION_NAME,
45.     PROMETHEUS_PORT,
46.     REQUIRED_S3_SETTINGS,
47.     SCRIPT_PATH,
48.     SERVICE_NAME,
49.     SERVICE_PORT,
50.     SETUP_COMPLETED_FLAG_FILE,
51.     THROTTLE_LEVELS,
52. )
53. from database import DatabaseHandler
54. from oauth_observer import OAuthObserver
55. 
56. logger = logging.getLogger(__name__)
57. 
58. S3Info = namedtuple("S3Info", ["enabled", "region", "bucket", "endpoint"])
59. 
60. INVALID_CORS_MESSAGE = (
```

</details>


---

<sub>⏱️ 6m 35s</sub>

### 💬 Copilot

Now I'll implement the full refactoring. Let me update charm.py with the new typed config and action param classes:

---

<sub>⏱️ 6m 35s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 6m 41s</sub>

### 💬 Copilot

Now add the `_charm_config` property to `DiscourseCharm` and update all methods. Let me update the class methods:

---

<sub>⏱️ 6m 41s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 118-145)

<details>
<summary>28 lines</summary>

```
118. class AnonymizeUserParams:
119.     """Typed parameters for the anonymize-user action."""
120. 
121.     username: str
122. 
123. 
124. class MissingRedisRelationDataError(Exception):
125.     """Custom exception to be raised in case of malformed/missing redis relation data."""
126. 
127. 
128. class DiscourseCharm(CharmBase):
129.     """Charm for Discourse on kubernetes."""
130. 
131.     # pylint: disable=too-many-instance-attributes
132.     # All attributes are necessary for the charm functionality
133. 
134.     on = RedisRelationCharmEvents()
135. 
136.     def __init__(self, *args):
137.         """Initialize defaults and event handlers."""
138.         super().__init__(*args)
139. 
140.         self._database = DatabaseHandler(self, DATABASE_RELATION_NAME)
141.         self._oauth = OAuthObserver(self, self._setup_and_activate, self._get_external_hostname)
142. 
143.         self.framework.observe(
144.             self._database.database.on.database_created, self._on_database_created
145.         )
```

</details>


---

<sub>⏱️ 6m 45s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 175-310)

<details>
<summary>136 lines</summary>

```
175.         self._grafana_dashboards = GrafanaDashboardProvider(self)
176. 
177.         self.restart_manager = RollingOpsManager(
178.             charm=self, relation="restart", callback=self._on_rolling_restart
179.         )
180. 
181.     def _on_start(self, _: ops.StartEvent) -> None:
182.         """Handle start event.
183. 
184.         Args:
185.             event: Event triggering the start event handler.
186.         """
187.         self._setup_and_activate()
188. 
189.     def _on_upgrade_charm(self, _: ops.UpgradeCharmEvent) -> None:
190.         """Handle upgrade charm event.
191. 
192.         Args:
193.             event: Event triggering the upgrade charm event handler.
194.         """
195.         self.on[self.restart_manager.name].acquire_lock.emit()
196. 
197.     def _on_discourse_pebble_ready(self, _: ops.PebbleReadyEvent) -> None:
198.         """Handle discourse pebble ready event.
199. 
200.         Args:
201.             event: Event triggering the discourse pebble ready event handler.
202.         """
203.         self._setup_and_activate()
204. 
205.     def _redis_relation_changed(self, _: HookEvent) -> None:
206.         """Handle redis relation changed event.
207. 
208.         Args:
209.             event: Event triggering the redis relation changed event handler.
210.         """
211.         self._setup_and_activate()
212. 
213.     def _on_database_created(self, _: DatabaseCreatedEvent) -> None:
214.         """Handle database created.
215. 
216.         Args:
217.             event: Event triggering the database created handler.
218.         """
219.         self._setup_and_activate()
220. 
221.     def _on_database_endpoints_changed(self, _: DatabaseEndpointsChangedEvent) -> None:
222.         """Handle endpoints change.
223. 
224.         Args:
225.             event: Event triggering the endpoints changed handler.
226.         """
227.         self._execute_migrations()
228.         if self._are_relations_ready():
229.             self._activate_charm()
230. 
231.     def _on_database_relation_broken(self, _: RelationBrokenEvent) -> None:
232.         """Handle broken relation.
233. 
234.         Args:
235.             event: Event triggering the broken relation handler.
236.         """
237.         self.model.unit.status = WaitingStatus("Waiting for database relation")
238.         self._stop_service()
239. 
240.     def _on_config_changed(self, _: HookEvent) -> None:
241.         """Handle config change.
242. 
243.         Args:
244.             event: Event triggering the config change handler.
245.         """
246.         self._configure_pod()
247. 
248.     def _on_saml_data_available(self, _: SamlDataAvailableEvent) -> None:
249.         """Handle SAML data available."""
250.         self._configure_pod()
251. 
252.     def _on_rolling_restart(self, _: ops.EventBase) -> None:
253.         """Handle rolling restart event.
254. 
255.         Args:
256.             event: Event triggering the discourse rolling restart event handler.
257.         """
258.         self._setup_and_activate()
259. 
260.     def _setup_and_activate(self) -> None:
261.         """Set up discourse, configure the pod and eventually activate the charm."""
262.         if not self._is_setup_completed():
263.             self._set_up_discourse()
264.         self._configure_pod()
265.         if self._are_relations_ready():
266.             self._activate_charm()
267. 
268.     def _require_nginx_route(self) -> None:
269.         """Create minimal ingress configuration."""
270.         require_nginx_route(
271.             charm=self,
272.             service_hostname=self._get_external_hostname(),
273.             service_name=self.app.name,
274.             service_port=SERVICE_PORT,
275.             session_cookie_max_age=3600,
276.         )
277. 
278.     def _get_external_hostname(self) -> str:
279.         """Extract and return hostname from site_url or default to [application name].
280. 
281.         Returns:
282.             The site hostname defined as part of the site_url configuration or a default value.
283.         """
284.         return (
285.             typing.cast(str, self.config["external_hostname"])
286.             if self.config["external_hostname"]
287.             else self.app.name
288.         )
289. 
290.     def _get_cors_origin(self) -> str:
291.         """Return the combined CORS origins.
292. 
293.         Return the combined CORS origins from 'cors_origin' and, if enabled,
294.         'external_hostname' and 's3_cdn_url'. Skips augmentation if 'cors_origin' is '*'.
295. 
296.         Returns:
297.             Comma-separated CORS origins string.
298.         """
299.         user_value = str(self.config.get("cors_origin", "")).strip()
300.         if user_value == "*":
301.             # No need to augment if all origins allowed
302.             return "*"
303. 
304.         origins: set[str] = set()
305.         if user_value:
306.             origins.update(s for s in (o.strip() for o in user_value.split(",")) if s)
307. 
308.         if self.config.get("augment_cors_origin"):
309.             ext = self._get_external_hostname()
310.             if ext:
```

</details>


---

<sub>⏱️ 6m 49s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 310-460)

<details>
<summary>151 lines</summary>

```
310.             if ext:
311.                 scheme = "https" if self.config.get("force_https") else "http"
312.                 origins.add(f"{scheme}://{ext}")
313. 
314.             cdn = str(self.config.get("s3_cdn_url"))
315.             if cdn:
316.                 origins.add(cdn)
317. 
318.         return ",".join(sorted(origins)) if origins else ""
319. 
320.     def _is_setup_completed(self) -> bool:
321.         """Check if the _set_up_discourse process has finished.
322. 
323.         Returns:
324.             True if the _set_up_discourse process has finished.
325.         """
326.         container = self.unit.get_container(CONTAINER_NAME)
327.         return container.can_connect() and container.exists(SETUP_COMPLETED_FLAG_FILE)
328. 
329.     def _set_setup_completed(self) -> None:
330.         """Mark the _set_up_discourse process as completed."""
331.         container = self.unit.get_container(CONTAINER_NAME)
332.         container.push(SETUP_COMPLETED_FLAG_FILE, "", make_dirs=True)
333. 
334.     def _is_config_valid(self) -> bool:
335.         """Check that the provided config is valid.
336. 
337.         Returns:
338.             If config is valid.
339.         """
340.         errors = []
341. 
342.         if (
343.             self.config.get("enable_cors")
344.             and self.config.get("cors_origin") == ""
345.             and not self.config.get("augment_cors_origin")
346.         ):
347.             errors.append(INVALID_CORS_MESSAGE)
348. 
349.         if self.config["throttle_level"] not in THROTTLE_LEVELS:
350.             errors.append(f"throttle_level must be one of: {' '.join(THROTTLE_LEVELS.keys())}")
351. 
352.         if (
353.             self.config["force_saml_login"]
354.             and self.model.get_relation(DEFAULT_RELATION_NAME) is None
355.         ):
356.             errors.append("force_saml_login cannot be true without a saml relation")
357.         if self.config["max_category_nesting"] not in MAX_CATEGORY_NESTING_LEVELS:
358.             errors.append(
359.                 "max_category_nesting must be one of: "
360.                 f"{', '.join(map(str, MAX_CATEGORY_NESTING_LEVELS))}"
361.             )
362.         if (
363.             self.config["saml_sync_groups"]
364.             and self.model.get_relation(DEFAULT_RELATION_NAME) is None
365.         ):
366.             errors.append("'saml_sync_groups' cannot be specified without a saml relation")
367. 
368.         if (
369.             self.model.get_relation(DEFAULT_RELATION_NAME) is not None
370.             and not self.config["force_https"]
371.         ):
372.             errors.append("A saml relation cannot be specified without 'force_https' being true")
373. 
374.         if (
375.             self.model.get_relation(OAUTH_RELATION_NAME) is not None
376.             and not self.config["force_https"]
377.         ):
378.             errors.append(
379.                 "An oauth relation cannot be established without 'force_https' being true"
380.             )
381. 
382.         if self.config.get("s3_enabled"):
383.             errors.extend(
384.                 f"'s3_enabled' requires '{s3_config}'"
385.                 for s3_config in REQUIRED_S3_SETTINGS
386.                 if not self.config[s3_config]
387.             )
388. 
389.         if errors:
390.             self.model.unit.status = BlockedStatus(", ".join(errors))
391.         return not errors
392. 
393.     def _get_saml_config(self) -> typing.Dict[str, typing.Any]:
394.         """Get SAML configuration.
395. 
396.         Returns:
397.             Dictionary with the SAML configuration settings.
398.         """
399.         relation_data = self.saml.get_relation_data()
400.         if relation_data is None:
401.             return {}
402. 
403.         saml_config = {}
404. 
405.         sso_redirect_endpoint = next(
406.             e
407.             for e in relation_data.endpoints
408.             if e.name == "SingleSignOnService"
409.             and e.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
410.         )
411. 
412.         saml_config["DISCOURSE_SAML_TARGET_URL"] = str(sso_redirect_endpoint.url)
413.         certificate = relation_data.certificates[0]
414.         # discourse needs SHA1 fingerprint
415.         saml_config["DISCOURSE_SAML_CERT_FINGERPRINT"] = (
416.             hashlib.sha1(base64.b64decode(certificate)).digest().hex(":").upper()  # noqa: S324  # nosec
417.         )
418. 
419.         saml_config["DISCOURSE_SAML_FULL_SCREEN_LOGIN"] = (
420.             "true" if self.config["force_saml_login"] else "false"
421.         )
422.         saml_sync_groups = [
423.             x.strip()
424.             for x in typing.cast(str, self.config["saml_sync_groups"]).split(",")
425.             if x.strip()
426.         ]
427.         if saml_sync_groups:
428.             # Per https://github.com/discourse/discourse-saml setting this to `true`
429.             # means the assigned groups will be completely synced including adding
430.             # AND removing groups based on the SAML provider.
431.             saml_config["DISCOURSE_SAML_GROUPS_FULLSYNC"] = "false"
432.             saml_config["DISCOURSE_SAML_SYNC_GROUPS"] = "true"
433.             saml_config["DISCOURSE_SAML_SYNC_GROUPS_LIST"] = "|".join(saml_sync_groups)
434. 
435.         return saml_config
436. 
437.     def _get_s3_env(self) -> typing.Dict[str, typing.Any]:
438.         """Get the list of S3-related environment variables from charm's configuration.
439. 
440.         Returns:
441.             Dictionary with all the S3 environment settings.
442.         """
443.         s3_env = {
444.             "DISCOURSE_S3_ACCESS_KEY_ID": self.config["s3_access_key_id"],
445.             "DISCOURSE_S3_BUCKET": self.config["s3_bucket"],
446.             "DISCOURSE_S3_ENDPOINT": self.config.get("s3_endpoint", "s3.amazonaws.com"),
447.             "DISCOURSE_S3_REGION": self.config["s3_region"],
448.             "DISCOURSE_S3_SECRET_ACCESS_KEY": self.config["s3_secret_access_key"],
449.             "DISCOURSE_S3_INSTALL_CORS_RULE": str(
450.                 self.config.get("s3_install_cors_rule", True)
451.             ).lower(),
452.             "DISCOURSE_USE_S3": "true",
453.         }
454.         if self.config.get("s3_backup_bucket"):
455.             s3_env["DISCOURSE_BACKUP_LOCATION"] = "s3"
456.             s3_env["DISCOURSE_S3_BACKUP_BUCKET"] = self.config["s3_backup_bucket"]
457.         if self.config.get("s3_cdn_url"):
458.             s3_env["DISCOURSE_S3_CDN_URL"] = self.config["s3_cdn_url"]
459.         if self.config.get("s3_enabled"):
460.             # We force assets to be uploaded to S3
```

</details>


---

<sub>⏱️ 6m 55s</sub>

### 💬 Copilot

Now I'll make the targeted edits to replace all `self.config[...]` usages with `self._charm_config.field`:

---

<sub>⏱️ 6m 55s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 14s</sub>

### 💬 Copilot

Now replace `_get_external_hostname`:

---

<sub>⏱️ 7m 14s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 23s</sub>

### 💬 Copilot

Now replace `_get_cors_origin`:

---

<sub>⏱️ 7m 23s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 37s</sub>

### 💬 Copilot

Now replace `_is_config_valid`:

---

<sub>⏱️ 7m 37s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 43s</sub>

### 💬 Copilot

Now replace `_get_saml_config`:

---

<sub>⏱️ 7m 43s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 53s</sub>

### 💬 Copilot

Now replace `_get_s3_env`:

---

<sub>⏱️ 7m 53s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 7m 58s</sub>

### 💬 Copilot

Now replace `_create_discourse_environment_settings`:

---

<sub>⏱️ 7m 58s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 510-590)

<details>
<summary>81 lines</summary>

```
510. 
511.         pod_config = {
512.             # Since pebble exec command doesn't copy the container env (envVars set in Dockerfile),
513.             # I need to take the required envVars for the application to work properly
514.             "CONTAINER_APP_NAME": CONTAINER_NAME,
515.             "CONTAINER_APP_ROOT": "/srv/discourse",
516.             "CONTAINER_APP_USERNAME": CONTAINER_APP_USERNAME,
517.             "DISCOURSE_CORS_ORIGIN": self._get_cors_origin(),
518.             "DISCOURSE_DB_HOST": database_relation_data["POSTGRES_HOST"],
519.             "DISCOURSE_DB_NAME": database_relation_data["POSTGRES_DB"],
520.             "DISCOURSE_DB_PASSWORD": database_relation_data["POSTGRES_PASSWORD"],
521.             "DISCOURSE_DB_USERNAME": database_relation_data["POSTGRES_USER"],
522.             "DISCOURSE_DEVELOPER_EMAILS": self.config["developer_emails"],
523.             "DISCOURSE_ENABLE_CORS": str(self.config["enable_cors"]).lower(),
524.             "DISCOURSE_HOSTNAME": self._get_external_hostname(),
525.             "DISCOURSE_MAX_CATEGORY_NESTING": str(self.config["max_category_nesting"]),
526.             "DISCOURSE_REDIS_HOST": redis_relation_data[0],
527.             "DISCOURSE_REDIS_PORT": str(redis_relation_data[1]),
528.             "DISCOURSE_REFRESH_MAXMIND_DB_DURING_PRECOMPILE_DAYS": "0",
529.             "DISCOURSE_SERVE_STATIC_ASSETS": "true",
530.             "DISCOURSE_SMTP_ADDRESS": self.config["smtp_address"],
531.             "DISCOURSE_SMTP_AUTHENTICATION": self.config["smtp_authentication"],
532.             "DISCOURSE_SMTP_DOMAIN": self.config["smtp_domain"],
533.             "DISCOURSE_SMTP_ENABLE_START_TLS": self.config["smtp_enable_start_tls"],
534.             "DISCOURSE_SMTP_FORCE_TLS": self.config["smtp_force_tls"],
535.             "DISCOURSE_SMTP_OPENSSL_VERIFY_MODE": self.config["smtp_openssl_verify_mode"],
536.             "DISCOURSE_SMTP_PASSWORD": self.config["smtp_password"],
537.             "DISCOURSE_SMTP_PORT": str(self.config["smtp_port"]),
538.             "DISCOURSE_SMTP_USER_NAME": self.config["smtp_username"],
539.             "RAILS_ENV": "production",
540.             "UNICORN_SIDEKIQ_MAX_RSS": str(self.config["sidekiq_max_memory"]),
541.         }
542.         pod_config.update(self._get_saml_config())
543.         # Add OIDC env vars if oauth relation is established
544.         pod_config.update(self._oauth.get_oidc_env())
545. 
546.         if self.config.get("s3_enabled"):
547.             pod_config.update(self._get_s3_env())
548. 
549.         # We only get valid throttle levels here, otherwise it would be caught
550.         # by `_is_config_valid()`.
551.         # self.config return an Any type
552.         pod_config.update(THROTTLE_LEVELS.get(self.config["throttle_level"]))  # type: ignore
553. 
554.         # Update environment with proxy settings
555.         pod_config["HTTP_PROXY"] = pod_config["http_proxy"] = (
556.             os.environ.get("JUJU_CHARM_HTTP_PROXY") or ""
557.         )
558.         pod_config["HTTPS_PROXY"] = pod_config["https_proxy"] = (
559.             os.environ.get("JUJU_CHARM_HTTPS_PROXY") or ""
560.         )
561.         pod_config["NO_PROXY"] = pod_config["no_proxy"] = (
562.             os.environ.get("JUJU_CHARM_NO_PROXY") or ""
563.         )
564. 
565.         return pod_config
566. 
567.     def _create_layer_config(self) -> ops.pebble.LayerDict:
568.         """Create a layer config based on our current configuration.
569. 
570.         Returns:
571.             Dictionary with the pebble configuration.
572.         """
573.         logger.info("Generating Layer config")
574.         layer_config = {
575.             "summary": "Discourse layer",
576.             "description": "Discourse layer",
577.             "services": {
578.                 SERVICE_NAME: {
579.                     "override": "replace",
580.                     "summary": "Discourse web application",
581.                     "command": f"{SCRIPT_PATH}/app_launch.sh",
582.                     "user": CONTAINER_APP_USERNAME,
583.                     "startup": "enabled",
584.                     "environment": self._create_discourse_environment_settings(),
585.                     "kill-delay": "20s",
586.                 }
587.             },
588.             "checks": {
589.                 "discourse-ready": {
590.                     "override": "replace",
```

</details>


---

<sub>⏱️ 8m 12s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 8m 18s</sub>

### 💬 Copilot

Now replace `_should_run_s3_migration`:

---

<sub>⏱️ 8m 18s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 600-640)

<details>
<summary>41 lines</summary>

```
600.     ) -> bool:
601.         """Determine if the S3 migration is to be run.
602. 
603.         Args:
604.             current_plan: Dictionary containing the current plan.
605.             s3info: S3Info object containing the S3 configuration options.
606. 
607.         Returns:
608.             If no services are planned yet (first run) or S3 settings have changed.
609.         """
610.         result = self.config.get("s3_enabled") and (
611.             not current_plan.services
612.             or (
613.                 s3info
614.                 and (
615.                     s3info.enabled != self.config.get("s3_enabled")
616.                     or s3info.region != self.config.get("s3_region")
617.                     or s3info.bucket != self.config.get("s3_bucket")
618.                     or s3info.endpoint != self.config.get("s3_endpoint")
619.                 )
620.             )
621.         )
622.         return bool(result)
623. 
624.     def _are_relations_ready(self) -> bool:
625.         """Check if the needed database relations are established.
626. 
627.         Returns:
628.             If the needed relations have been established.
629.         """
630.         if not self._database.is_relation_ready():
631.             self.model.unit.status = WaitingStatus("Waiting for database relation")
632.             self._stop_service()
633.             return False
634.         if not self.redis.relation_data:
635.             self.model.unit.status = WaitingStatus("Waiting for redis relation")
636.             self._stop_service()
637.             return False
638.         try:
639.             if (
640.                 self._get_redis_relation_data()[0] in ("", "None")
```

</details>


---

<sub>⏱️ 8m 24s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 8m 29s</sub>

### 💬 Copilot

Now replace `_config_force_https`:

---

<sub>⏱️ 8m 29s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 935-1010)

<details>
<summary>76 lines</summary>

```
935.         """
936.         choices = string.ascii_letters + string.digits
937.         password = "".join([secrets.choice(choices) for _ in range(length)])
938.         return password
939. 
940.     def _config_force_https(self) -> None:
941.         """Config Discourse to force_https option based on charm configuration."""
942.         container = self.unit.get_container(CONTAINER_NAME)
943.         force_bool = str(self.config["force_https"]).lower()
944.         process = container.exec(
945.             [
946.                 os.path.join(DISCOURSE_PATH, "bin/rails"),
947.                 "runner",
948.                 f"SiteSetting.force_https={force_bool}",
949.             ],
950.             working_dir=DISCOURSE_PATH,
951.             user=CONTAINER_APP_USERNAME,
952.             environment=self._create_discourse_environment_settings(),
953.         )
954.         process.wait_output()
955. 
956.     def _on_anonymize_user_action(self, event: ActionEvent) -> None:
957.         """Anonymize data from a user.
958. 
959.         Args:
960.             event: Event triggering the anonymize_user action.
961.         """
962.         username = event.params["username"]
963.         container = self.unit.get_container(CONTAINER_NAME)
964.         if not container.can_connect():
965.             event.fail("Unable to connect to container, container is not ready")
966.             return
967. 
968.         process = container.exec(
969.             [
970.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
971.                 "exec",
972.                 "rake",
973.                 f"users:anonymize[{username}]",
974.             ],
975.             working_dir=DISCOURSE_PATH,
976.             user=CONTAINER_APP_USERNAME,
977.             environment=self._create_discourse_environment_settings(),
978.         )
979.         try:
980.             process.wait_output()
981.             event.set_results({"user": f"{username}"})
982.         except ExecError as ex:
983.             event.fail(
984.                 # Parameter validation errors are printed to stdout
985.                 # Ignore mypy warning when formatting stdout
986.                 f"Failed to anonymize user with username {username}:{ex.stdout}"  # type: ignore
987.             )
988. 
989.     def _start_service(self):
990.         """Start discourse."""
991.         logger.info("Starting discourse")
992.         container = self.unit.get_container(CONTAINER_NAME)
993.         if self._is_config_valid() and container.can_connect():
994.             layer_config = self._create_layer_config()
995.             container.add_layer(SERVICE_NAME, layer_config, combine=True)
996.             container.pebble.replan_services()
997. 
998.     def _stop_service(self):
999.         """Stop discourse, this operation is idempotent."""
1000.         logger.info("Stopping discourse")
1001.         container = self.unit.get_container(CONTAINER_NAME)
1002.         if (
1003.             container.can_connect()
1004.             and SERVICE_NAME in container.get_plan().services
1005.             and container.get_service(SERVICE_NAME).is_running()
1006.         ):
1007.             container.stop(CONTAINER_NAME)
1008. 
1009. 
1010. if __name__ == "__main__":  # pragma: no cover
```

</details>


---

<sub>⏱️ 8m 34s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 8m 38s</sub>

### 💬 Copilot

Now update the action handlers to use `event.load_params()`. Let me view the current action handlers:

---

<sub>⏱️ 8m 38s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py (lines 840-940)

<details>
<summary>101 lines</summary>

```
840.         """Promote a user to a specific trust level.
841. 
842.         Args:
843.             event: Event triggering the promote_user action.
844.         """
845.         container = self.unit.get_container(CONTAINER_NAME)
846.         if not container.can_connect():
847.             event.fail("Unable to connect to container, container is not ready")
848.             return
849. 
850.         email = event.params["email"]
851. 
852.         if not self._user_exists(email):
853.             event.fail(f"User with email {email} does not exist")
854.             return
855. 
856.         process = container.exec(
857.             [
858.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
859.                 "exec",
860.                 "rake",
861.                 "admin:create",
862.             ],
863.             stdin=f"{email}\nn\nY\n",
864.             working_dir=DISCOURSE_PATH,
865.             user=CONTAINER_APP_USERNAME,
866.             environment=self._create_discourse_environment_settings(),
867.             timeout=60,
868.         )
869.         try:
870.             process.wait_output()
871.             event.set_results({"user": email})
872.         except ExecError as ex:
873.             event.fail(
874.                 f"Failed to make user with email {email} an admin: {ex.stdout}"  # type: ignore
875.             )
876. 
877.     def _on_create_user_action(self, event: ActionEvent) -> None:
878.         """Create a new user in Discourse.
879. 
880.         Args:
881.             event: Event triggering the create_user action.
882.         """
883.         container = self.unit.get_container(CONTAINER_NAME)
884.         if not container.can_connect():
885.             event.fail("Unable to connect to container, container is not ready")
886.             return
887. 
888.         email = event.params["email"]
889.         password = self._generate_password(16)
890. 
891.         if self._user_exists(email):
892.             event.fail(f"User with email {email} already exists")
893.             return
894. 
895.         # Admin flag is optional, if it is true, the user will be created as an admin
896.         admin_flag = "Y" if event.params.get("admin") else "N"
897. 
898.         process = container.exec(
899.             [
900.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
901.                 "exec",
902.                 "rake",
903.                 "admin:create",
904.             ],
905.             stdin=f"{email}\n{password}\n{password}\n{admin_flag}\n",
906.             working_dir=DISCOURSE_PATH,
907.             user=CONTAINER_APP_USERNAME,
908.             environment=self._create_discourse_environment_settings(),
909.             timeout=60,
910.         )
911.         try:
912.             process.wait_output()
913.         except ExecError as ex:
914.             event.fail(f"Failed to make user with email {email}: {ex.stdout}")  # type: ignore
915.             return
916. 
917.         if (
918.             not event.params.get("admin")
919.             and event.params.get("active")
920.             and not self._activate_user(email)
921.         ):
922.             event.fail(f"Could not find user {email} to activate")
923.             return
924. 
925.         event.set_results({"user": email, "password": password})
926. 
927.     def _generate_password(self, length: int) -> str:
928.         """Generate a random password.
929. 
930.         Args:
931.             length: Length of the password to generate.
932. 
933.         Returns:
934.             Random password.
935.         """
936.         choices = string.ascii_letters + string.digits
937.         password = "".join([secrets.choice(choices) for _ in range(length)])
938.         return password
939. 
940.     def _config_force_https(self) -> None:
```

</details>


---

<sub>⏱️ 8m 48s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 8m 57s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 9m 7s</sub>

### 💬 Copilot

Now update `_on_anonymize_user_action`:

---

<sub>⏱️ 9m 7s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 9m 13s</sub>

### 💬 Copilot

Now let's run uv lock to update the lockfile:

---

<sub>⏱️ 9m 14s</sub>

### ✅ `bash`

**Update uv.lock with new ops version**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && uv lock 2>&1 | tail -5

<details>
<summary>6 lines</summary>

```
Updated urllib3 v2.2.3, v2.5.0 -> v2.5.0
Updated websocket-client v1.8.0, v1.9.0 -> v1.9.0
Updated websockets v13.1, v15.0.1 -> v15.0.1
Removed wrapt v2.0.1
Updated zipp v3.20.2, v3.23.0 -> v3.23.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 19s</sub>

### 💬 Copilot

Now let's run the unit tests to verify everything works:

---

<sub>⏱️ 9m 22s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && tox -e unit 2>&1 | tail -40

<details>
<summary>37 lines</summary>

```
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_charm.py: 43 warnings
  /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/helpers.py:41: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(DiscourseCharm)

tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
  /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/lib/charms/saml_integrator/v0/saml.py:142: PydanticDeprecatedSince20: `parse_obj_as` is deprecated. Use `pydantic.TypeAdapter.validate_python` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    parse_obj_as(AnyHttpUrl, relation_data[f"{prefix}url"])

tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
  /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/lib/charms/saml_integrator/v0/saml.py:211: PydanticDeprecatedSince20: `parse_obj_as` is deprecated. Use `pydantic.TypeAdapter.validate_python` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    parse_obj_as(AnyHttpUrl, relation_data.get("metadata_url"))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 55 passed, 106 warnings in 2.15s =======================
unit: commands[1]> coverage report
Name                    Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------
src/charm.py              427     42     96     15    89%   234, 242-243, 255, 312->316, 361, 430->438, 461->466, 478, 670-672, 677-678, 690-692, 697-698, 710-712, 735-737, 775->exit, 834-837, 847-848, 872-873, 885-886, 913-915, 922-923, 964-965, 983-984, 994->exit, 1008
src/constants.py           21      0      0      0   100%
src/database.py            29      1      8      1    95%   57
src/oauth_observer.py      54      8      8      2    84%   65, 80-81, 111, 114-123
-------------------------------------------------------------------
TOTAL                     531     51    112     18    89%
  unit: OK (2.81=setup[0.08]+cmd[2.66,0.08] seconds)
  congratulations :) (2.83 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 27s</sub>

### 💬 Copilot

All 55 tests pass. Let's also run the lint check to catch any issues:

---

<sub>⏱️ 9m 28s</sub>

### ✅ `bash`

**Run lint checks**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && tox -e lint 2>&1 | tail -30

<details>
<summary>28 lines</summary>

```
"An oauth relation cannot be established without 'force_https' being true"
             )
@@ -423,9 +407,7 @@
             "true" if self._charm_config.force_saml_login else "false"
         )
         saml_sync_groups = [
-            x.strip()
-            for x in self._charm_config.saml_sync_groups.split(",")
-            if x.strip()
+            x.strip() for x in self._charm_config.saml_sync_groups.split(",") if x.strip()
         ]
         if saml_sync_groups:
             # Per https://github.com/discourse/discourse-saml setting this to `true`
@@ -914,11 +896,7 @@
             event.fail(f"Failed to make user with email {params.email}: {ex.stdout}")  # type: ignore
             return
 
-        if (
-            not params.admin
-            and params.active
-            and not self._activate_user(params.email)
-        ):
+        if not params.admin and params.active and not self._activate_user(params.email):
             event.fail(f"Could not find user {params.email} to activate")
             return
 

lint: exit 1 (0.01 seconds) /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4> ruff format --check --diff src tests pid=24567
  lint: FAIL code 1 (0.19=setup[0.10]+cmd[0.08,0.01] seconds)
  evaluation failed :( (0.21 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 33s</sub>

### ✅ `bash`

**Auto-fix formatting issues**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && tox -e fmt 2>&1 | tail -10

<details>
<summary>11 lines</summary>

```
fmt: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/.tox/fmt
fmt: uv-sync> uv sync --locked --python-preference system --no-default-groups --group fmt -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
fmt: commands[0]> ruff check --fix --select I src tests
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
fmt: commands[1]> ruff format src tests
warning: Selection `CPY` has no effect because preview is not enabled.
1 file reformatted, 18 files left unchanged
  fmt: OK (0.10=setup[0.08]+cmd[0.01,0.01] seconds)
  congratulations :) (0.11 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 41s</sub>

### ✅ `bash`

**Run lint again after formatting**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && tox -e lint 2>&1 | tail -20

<details>
<summary>13 lines</summary>

```
lint: uv-sync> uv sync --locked --python-preference system --no-default-groups --group lint -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
lint: commands[0]> codespell /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4
lint: commands[1]> ruff format --check --diff src tests
warning: Selection `CPY` has no effect because preview is not enabled.
19 files already formatted
lint: commands[2]> ruff check src tests
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
lint: commands[3]> mypy src tests
Success: no issues found in 19 source files
  lint: OK (2.46=setup[0.02]+cmd[0.08,0.01,0.01,2.34] seconds)
  congratulations :) (2.47 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 45s</sub>

### 💬 Copilot

All lint checks pass. Let's run the unit tests one more time to confirm everything still works after formatting:

---

<sub>⏱️ 9m 48s</sub>

### ✅ `bash`

**Final unit test run**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && tox -e unit 2>&1 | tail -15

<details>
<summary>15 lines</summary>

```
parse_obj_as(AnyHttpUrl, relation_data.get("metadata_url"))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 55 passed, 106 warnings in 1.82s =======================
unit: commands[1]> coverage report
Name                    Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------
src/charm.py              427     42     96     15    89%   234, 242-243, 255, 312->316, 354, 412->420, 443->448, 460, 652-654, 659-660, 672-674, 679-680, 692-694, 717-719, 757->exit, 816-819, 829-830, 854-855, 867-868, 895-897, 900-901, 942-943, 961-962, 972->exit, 986
src/constants.py           21      0      0      0   100%
src/database.py            29      1      8      1    95%   57
src/oauth_observer.py      54      8      8      2    84%   65, 80-81, 111, 114-123
-------------------------------------------------------------------
TOTAL                     531     51    112     18    89%
  unit: OK (2.23=setup[0.02]+cmd[2.13,0.08] seconds)
  congratulations :) (2.24 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 53s</sub>

### 💬 Copilot

All 55 tests pass. Now let's commit the changes:

---

<sub>⏱️ 9m 54s</sub>

### ✅ `bash`

**Stage all changes and show diff stat**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && git add -A && git diff --cached --stat

<details>
<summary>7 lines</summary>

```
.baseline_commit |    1 +
 pyproject.toml   |    6 +-
 src/charm.py     |  232 +++++----
 tox.toml         |    1 +
 uv.lock          | 2512 ++++++----------------------------------------------------------------------------------------
 5 files changed, 281 insertions(+), 2471 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 5s</sub>

### ✅ `bash`

**Commit all changes**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && git commit -m "Upgrade to ops 3.6.0 and adopt new features

- Bump ops from 2.23.2 to 3.6.0 (ops 3.0 dropped Python 3.8/3.9 support;
  no other breaking changes affect this charm)
- Update requires-python to >=3.10 and remove Python 3.8/3.9 classifiers
  to match ops 3.x requirements
- Add DiscourseConfig dataclass and use CharmBase.load_config() (new in
  ops 2.23.0) to replace all self.config[...] accesses with a typed,
  attribute-based API, improving IDE support and reducing runtime errors
- Add PromoteUserParams, CreateUserParams, AnonymizeUserParams dataclasses
  and use ActionEvent.load_params() (new in ops 2.23.0) for typed action
  parameter access in all three action handlers
- Set SCENARIO_BARE_CHARM_ERRORS=true in the unit test tox environment
  (new in ops 3.5.0) so exceptions from charm code propagate directly to
  test code without being wrapped in UncaughtCharmError, making test
  failures easier to debug
- Update uv.lock

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[upgrade-ops-3.6.0 7384566] Upgrade to ops 3.6.0 and adopt new features
 5 files changed, 281 insertions(+), 2471 deletions(-)
 create mode 100644 .baseline_commit
<exited with exit code 0>
```


---

<sub>⏱️ 10m 11s</sub>

### ✅ `sql`

**Mark all todos done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark all todos done",
  "query": "UPDATE todos SET status = 'done';"
}
```

</details>

```
7 row(s) updated.
```


---

<sub>⏱️ 10m 20s</sub>

### ❌ `store_memory`

<details>
<summary>Arguments</summary>

```json
{
  "subject": "testing practices",
  "fact": "Set SCENARIO_BARE_CHARM_ERRORS=true in the unit test tox env to make exceptions from charm code propagate directly without UncaughtCharmError wrapping.",
  "citations": "tox.toml:[env.unit]; ops 3.5.0 release notes",
  "reason": "This is a project-specific testing practice adopted for all future unit tests. Any new test environments should also set this variable. Future code review or test writing tasks should know this is the expected behavior.",
  "category": "general"
}
```

</details>

```
Unable to store memory. You can continue with your task without storing this information.
```


---

<sub>⏱️ 10m 21s</sub>

### ❌ `store_memory`

<details>
<summary>Arguments</summary>

```json
{
  "subject": "config access",
  "fact": "Config is accessed via self._charm_config (a property calling self.load_config(DiscourseConfig)) returning a typed DiscourseConfig dataclass, not self.config[...].",
  "citations": "src/charm.py:186-188",
  "reason": "This pattern is used throughout the charm. Future code changes that need to read config must use self._charm_config.field_name. New config options must be added to both config.yaml and DiscourseConfig. Important for any future charm feature work.",
  "category": "file_specific"
}
```

</details>

```
Unable to store memory. You can continue with your task without storing this information.
```


---

<sub>⏱️ 10m 33s</sub>

### ✅ `task_complete`

**Created branch `upgrade-ops-3.6.0` with the following changes based on analysis of ops 3.0.0–3.6.0 (and ops-tracing/ops-scenario, which track the same version numbers) release notes:

**Release notes analysis:**
- **ops 3.0.0**: Dropped Python 3.8/3.9 — updated `requires-python` to `>=3.10` and removed those classifiers
- **ops 2.23.0 (first used in 3.x)**: `CharmBase.load_config()` and `ActionEvent.load_params()` for typed config/action schemas — adopted both
- **ops 3.5.0**: `SCENARIO_BARE_CHARM_ERRORS` env var for cleaner test exceptions — enabled in unit test env
- **ops 3.4.0 breaking**: `testing.Context` context-manager exception wrapping change — not applicable (tests don't use Context as context manager)
- **ops 3.5.0 deprecation**: `testing.Context.charm_spec` deprecated — not used by this charm
- **ops 3.6.0**: Minor fixes (ExecError, Pydantic MISSING, Juju version bump) — no charm-side changes needed

**Changes made:**
1. **`pyproject.toml`**: `ops==2.23.2` → `ops==3.6.0`; `requires-python>=3.8` → `>=3.10`; removed Python 3.8/3.9 classifiers
2. **`src/charm.py`**: Added `DiscourseConfig` dataclass covering all 30 config options; added `_charm_config` property using `self.load_config(DiscourseConfig)`; replaced all `self.config[...]` accesses with typed attributes. Added `PromoteUserParams`, `CreateUserParams`, `AnonymizeUserParams` dataclasses; updated all three action handlers to use `event.load_params()`
3. **`tox.toml`**: Added `set_env.SCENARIO_BARE_CHARM_ERRORS = "true"` to the unit test environment
4. **`uv.lock`**: Regenerated

All 55 unit tests pass, lint and mypy clean.**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Created branch `upgrade-ops-3.6.0` with the following changes based on analysis of ops 3.0.0–3.6.0 (and ops-tracing/ops-scenario, which track the same version numbers) release notes:\n\n**Release notes analysis:**\n- **ops 3.0.0**: Dropped Python 3.8/3.9 — updated `requires-python` to `>=3.10` and removed those classifiers\n- **ops 2.23.0 (first used in 3.x)**: `CharmBase.load_config()` and `ActionEvent.load_params()` for typed config/action schemas — adopted both\n- **ops 3.5.0**: `SCENARIO_BARE_CHARM_ERRORS` env var for cleaner test exceptions — enabled in unit test env\n- **ops 3.4.0 breaking**: `testing.Context` context-manager exception wrapping change — not applicable (tests don't use Context as context manager)\n- **ops 3.5.0 deprecation**: `testing.Context.charm_spec` deprecated — not used by this charm\n- **ops 3.6.0**: Minor fixes (ExecError, Pydantic MISSING, Juju version bump) — no charm-side changes needed\n\n**Changes made:**\n1. **`pyproject.toml`**: `ops==2.23.2` → `ops==3.6.0`; `requires-python>=3.8` → `>=3.10`; removed Python 3.8/3.9 classifiers\n2. **`src/charm.py`**: Added `DiscourseConfig` dataclass covering all 30 config options; added `_charm_config` property using `self.load_config(DiscourseConfig)`; replaced all `self.config[...]` accesses with typed attributes. Added `PromoteUserParams`, `CreateUserParams`, `AnonymizeUserParams` dataclasses; updated all three action handlers to use `event.load_params()`\n3. **`tox.toml`**: Added `set_env.SCENARIO_BARE_CHARM_ERRORS = \"true\"` to the unit test environment\n4. **`uv.lock`**: Regenerated\n\nAll 55 unit tests pass, lint and mypy clean."
}
```

</details>

<details>
<summary>14 lines</summary>

```
Created branch `upgrade-ops-3.6.0` with the following changes based on analysis of ops 3.0.0–3.6.0 (and ops-tracing/ops-scenario, which track the same version numbers) release notes:

**Release notes analysis:**
- **ops 3.0.0**: Dropped Python 3.8/3.9 — updated `requires-python` to `>=3.10` and removed those classifiers
- **ops 2.23.0 (first used in 3.x)**: `CharmBase.load_config()` and `ActionEvent.load_params()` for typed config/action schemas — adopted both
- **ops 3.5.0**: `SCENARIO_BARE_CHARM_ERRORS` env var for cleaner test exceptions — enabled in unit test env
- **ops 3.4.0 breaking**: `testing.Context` context-manager exception wrapping change — not applicable (tests don't use Context as context manager)
- **ops 3.5.0 deprecation**: `testing.Context.charm_spec` deprecated — not used by this charm
- **ops 3.6.0**: Minor fixes (ExecError, Pydantic MISSING, Juju version bump) — no charm-side changes needed

**Changes made:**
1. **`pyproject.toml`**: `ops==2.23.2` → `ops==3.6.0`; `requires-python>=3.8` → `>=3.10`; removed Python 3.8/3.9 classifiers
2. **`src/charm.py`**: Added `DiscourseConfig` dataclass covering all 30 config options; added `_charm_config` property using `self.load_config(DiscourseConfig)`; replaced all `self.config[...]` accesses with typed attributes. Added `PromoteUserParams`, `CreateUserParams`, `AnonymizeUserParams` dataclasses; updated all three action handlers to use `event.load_params()`
3. **`tox.toml`**: Added `set_env.SCENARIO_BARE_CHARM_ERRORS = "true"` to the unit test environment
4. **`uv.lock`**: Regenerated

All 55 unit tests pass, lint and mypy clean.
```

</details>


---

<sub>⏱️ 10m 38s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 10m 43s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 10m 48s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 10m 53s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 10m 58s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 11m 4s</sub>

### ❌ Error

Execution failed: Error: Failed to get response from the AI model; retried 5 times (total retry wait time: 5.668396081507919 seconds) Last error: Unknown error

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
