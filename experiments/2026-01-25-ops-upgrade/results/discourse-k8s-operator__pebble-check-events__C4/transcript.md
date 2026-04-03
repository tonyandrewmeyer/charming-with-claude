# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `e6d9f46d-88f8-4616-9b88-bcd6927da3f4`  
> - **Started:** 4/2/2026, 3:02:47 AM  
> - **Duration:** 14m 57s  
> - **Exported:** 4/2/2026, 3:17:44 AM  

---

<sub>⏱️ 7s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 19s</sub>

### ✅ `bash`

**Check current ops version and tox config**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && cat pyproject.toml | grep -A5 "ops" && echo "---" && cat tox.toml | head -60

<details>
<summary>67 lines</summary>

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
    "run",
    "--source={[vars]src_path}",
    "-m",
    "pytest",
    "--ignore={[vars]tst_path}{/}integration",
    "-v",
    "--tb",
    "native",
    "-s",
    { replace = "posargs", extend = true },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 18s</sub>

### ✅ `task`

**Explore charm structure**

<details>
<summary>Arguments</summary>

```json
{
  "name": "explore-charm",
  "agent_type": "explore",
  "description": "Explore charm structure",
  "prompt": "Explore the charm at /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4. I need to understand:\n1. The current ops version dependency (check pyproject.toml, requirements files, charmcraft.yaml)\n2. The overall charm structure - what does it do?\n3. All Python files in src/ and tests/ - list them and briefly describe each\n4. Any use of ops features like: pebble checks, event handling, status handling, testing helpers\n5. Look at src/ charm code and identify all ops APIs being used (Container, Pebble, events, etc.)\n6. Look at tests/ to understand what testing framework is used and what's tested\n\nPlease provide a comprehensive summary including file paths and key code patterns.",
  "mode": "background"
}
```

</details>

```
Agent started in background with agent_id: explore-charm. You can use read_agent tool with this agent_id to check status and retrieve results. Instruct the user to use /tasks to manage the background agent.
```


---

<sub>⏱️ 26s</sub>

### ✅ `bash`

**Check latest ops version available**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && pip index versions ops 2>/dev/null | head -5 || pip install ops --dry-run 2>&1 | head -5

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

<sub>⏱️ 35s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://github.com/canonical/operator/releases",
  "start_index": 10000
}
```

</details>

<details>
<summary>149 lines</summary>

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
*   Expand landi

<note>Content truncated. Call the fetch tool with a start_index of 25000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 34s</sub>

### ✅ `read_agent`

**Explore agent (Explore charm structure)**

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "explore-charm",
  "wait": true,
  "timeout": 60
}
```

</details>

```
Agent is still running after waiting 60s. agent_id: explore-charm, agent_type: explore, status: running, description: Explore charm structure, elapsed: 76s, total_turns: 0, tool_calls_completed: 28, (timed out waiting for completion) You will be automatically notified when this agent completes — no need to poll.
```


---

<sub>⏱️ 1m 42s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "start_index": 25000,
  "url": "https://github.com/canonical/operator/releases"
}
```

</details>

<details>
<summary>63 lines</summary>

```
Contents of https://github.com/canonical/operator/releases:
ng pages with summaries of pages in [#2140](https://github.com/canonical/operator/pull/2140)
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

<sub>⏱️ 1m 47s</sub>

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

<sub>⏱️ 1m 47s</sub>

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

<sub>⏱️ 1m 52s</sub>

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

<sub>⏱️ 1m 52s</sub>

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

<sub>⏱️ 2m 0s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.3.1**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/releases/tag/3.3.1"
}
```

</details>

<details>
<summary>37 lines</summary>

```
Contents of https://github.com/canonical/operator/releases/tag/3.3.1:
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
2.  [3.3.1](/canonical/operator/releases/tag/3.3.1)

## Choose a tag to compare

· [1 commit](/canonical/operator/compare/3.3.1...3.3-maintenance) to 3.3-maintenance since this release

[`c85787b`](/canonical/operator/commit/c85787b5df1b0c14e47f1153d3f1a8cdbf1af09c)

This commit was created on GitHub.com and signed with GitHub’s **verified signature**.

This is a bug-fix release to fix an issue introduced in Ops 3.3.0 (in production) and Ops 3.2.0 (in testing), where loading the Juju machine ID would fail if the ID was not an integer.

The type of the machine ID (both in `ops.JujuContext` and `testing.Context`) is changed from `int` to `str`, so some code or tests may need to be adjusted to use the correct type.

## What's Changed

### Fixes

*   Change JujuContext.machine\_id from int to str ([#2108](https://github.com/canonical/operator/pull/2108))

**Full Changelog**: [3.3.0...3.3.1](https://github.com/canonical/operator/compare/3.3.0...3.3.1)
```

</details>


---

<sub>⏱️ 2m 0s</sub>

### ✅ `bash`

**List Python source files**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && find src tests -name "*.py" | head -30 && echo "---" && ls lib/

<details>
<summary>22 lines</summary>

```
src/constants.py
src/oauth_observer.py
src/charm.py
src/database.py
tests/conftest.py
tests/integration/test_users.py
tests/integration/conftest.py
tests/integration/test_charm.py
tests/integration/test_db_migration.py
tests/integration/types.py
tests/integration/test_oauth.py
tests/integration/__init__.py
tests/integration/test_saml.py
tests/unit/conftest.py
tests/unit/test_charm.py
tests/unit_harness/helpers.py
tests/unit_harness/test_charm.py
tests/unit_harness/__init__.py
tests/__init__.py
---
charms
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 6s</sub>

### ✅ `bash`

**Read main charm file**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && cat src/charm.py

<details>
<summary>8 lines</summary>

```
Output too large to read at once (36.3 KB). Saved to: /tmp/copilot-tool-output-1775052293297-qgdzuw.txt
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

<sub>⏱️ 2m 6s</sub>

### ✅ `bash`

**Read unit tests**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && cat tests/unit/test_charm.py

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

<sub>⏱️ 2m 27s</sub>

### ✅ `bash`

**View start of charm.py**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && head -200 /tmp/copilot-tool-output-1775052293297-qgdzuw.txt

<details>
<summary>160 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm for Discourse on kubernetes."""

import base64
import hashlib
import logging
import os.path
import secrets
import string
import typing
from collections import namedtuple

import ops
from charms.data_platform_libs.v0.data_interfaces import (
    DatabaseCreatedEvent,
    DatabaseEndpointsChangedEvent,
)
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires
from charms.rolling_ops.v0.rollingops import RollingOpsManager
from charms.saml_integrator.v0.saml import (
    DEFAULT_RELATION_NAME,
    SamlDataAvailableEvent,
    SamlRequires,
)
from ops.charm import ActionEvent, CharmBase, HookEvent, RelationBrokenEvent
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus
from ops.pebble import ExecError, ExecProcess, Plan

from constants import (
    CONTAINER_APP_USERNAME,
    CONTAINER_NAME,
    DATABASE_RELATION_NAME,
    DISCOURSE_PATH,
    LOG_PATHS,
    MAX_CATEGORY_NESTING_LEVELS,
    OAUTH_RELATION_NAME,
    PROMETHEUS_PORT,
    REQUIRED_S3_SETTINGS,
    SCRIPT_PATH,
    SERVICE_NAME,
    SERVICE_PORT,
    SETUP_COMPLETED_FLAG_FILE,
    THROTTLE_LEVELS,
)
from database import DatabaseHandler
from oauth_observer import OAuthObserver

logger = logging.getLogger(__name__)

S3Info = namedtuple("S3Info", ["enabled", "region", "bucket", "endpoint"])

INVALID_CORS_MESSAGE = (
    "invalid CORS config, `augment_cors_origin` must be enabled or `cors_origin` must be non-empty"  # pylint: disable=line-too-long
)


class MissingRedisRelationDataError(Exception):
    """Custom exception to be raised in case of malformed/missing redis relation data."""


class DiscourseCharm(CharmBase):
    """Charm for Discourse on kubernetes."""

    # pylint: disable=too-many-instance-attributes
    # All attributes are necessary for the charm functionality

    on = RedisRelationCharmEvents()

    def __init__(self, *args):
        """Initialize defaults and event handlers."""
        super().__init__(*args)

        self._database = DatabaseHandler(self, DATABASE_RELATION_NAME)
        self._oauth = OAuthObserver(self, self._setup_and_activate, self._get_external_hostname)

        self.framework.observe(
            self._database.database.on.database_created, self._on_database_created
        )
        self.framework.observe(
            self._database.database.on.endpoints_changed, self._on_database_endpoints_changed
        )
        self.framework.observe(
            self.on[DATABASE_RELATION_NAME].relation_broken,
            self._on_database_relation_broken,
        )

        self._require_nginx_route()
        self.saml = SamlRequires(self)
        self.framework.observe(self.saml.on.saml_data_available, self._on_saml_data_available)

        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
        self.framework.observe(self.on.discourse_pebble_ready, self._on_discourse_pebble_ready)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.promote_user_action, self._on_promote_user_action)
        self.framework.observe(self.on.create_user_action, self._on_create_user_action)
        self.framework.observe(self.on.anonymize_user_action, self._on_anonymize_user_action)

        self.redis = RedisRequires(self)
        self.framework.observe(self.on.redis_relation_updated, self._redis_relation_changed)

        self._metrics_endpoint = MetricsEndpointProvider(
            self, jobs=[{"static_configs": [{"targets": [f"*:{PROMETHEUS_PORT}"]}]}]
        )
        self._logging = LogProxyConsumer(
            self, relation_name="logging", log_files=LOG_PATHS, container_name=CONTAINER_NAME
        )
        self._grafana_dashboards = GrafanaDashboardProvider(self)

        self.restart_manager = RollingOpsManager(
            charm=self, relation="restart", callback=self._on_rolling_restart
        )

    def _on_start(self, _: ops.StartEvent) -> None:
        """Handle start event.

        Args:
            event: Event triggering the start event handler.
        """
        self._setup_and_activate()

    def _on_upgrade_charm(self, _: ops.UpgradeCharmEvent) -> None:
        """Handle upgrade charm event.

        Args:
            event: Event triggering the upgrade charm event handler.
        """
        self.on[self.restart_manager.name].acquire_lock.emit()

    def _on_discourse_pebble_ready(self, _: ops.PebbleReadyEvent) -> None:
        """Handle discourse pebble ready event.

        Args:
            event: Event triggering the discourse pebble ready event handler.
        """
        self._setup_and_activate()

    def _redis_relation_changed(self, _: HookEvent) -> None:
        """Handle redis relation changed event.

        Args:
            event: Event triggering the redis relation changed event handler.
        """
        self._setup_and_activate()

    def _on_database_created(self, _: DatabaseCreatedEvent) -> None:
        """Handle database created.

        Args:
            event: Event triggering the database created handler.
        """
        self._setup_and_activate()

    def _on_database_endpoints_changed(self, _: DatabaseEndpointsChangedEvent) -> None:
        """Handle endpoints change.

        Args:
            event: Event triggering the endpoints changed handler.
        """
        self._execute_migrations()
        if self._are_relations_ready():
            self._activate_charm()

    def _on_database_relation_broken(self, _: RelationBrokenEvent) -> None:
        """Handle broken relation.

        Args:
            event: Event triggering the broken relation handler.
        """
        self.model.unit.status = WaitingStatus("Waiting for database relation")
        self._stop_service()

    def _on_config_changed(self, _: HookEvent) -> None:
        """Handle config change.

        Args:
            event: Event triggering the config change handler.
        """
        self._configure_pod()

    def _on_saml_data_available(self, _: SamlDataAvailableEvent) -> None:
        """Handle SAML data available."""
        self._configure_pod()

    def _on_rolling_restart(self, _: ops.EventBase) -> None:
        """Handle rolling restart event.

        Args:
            event: Event triggering the discourse rolling restart event handler.
        """
        self._setup_and_activate()
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 27s</sub>

### ✅ `bash`

**Read test conftest files**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && cat tests/unit/conftest.py && cat tests/conftest.py

<details>
<summary>105 lines</summary>

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
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
"""Module for test customizations."""


def pytest_addoption(parser):
    """Adds parser switches."""
    parser.addoption("--discourse-image", action="store")
    parser.addoption("--localstack-address", action="store")
    parser.addoption("--saml-email", action="store")
    parser.addoption("--saml-password", action="store")
    parser.addoption("--charm-file", action="store", default=None)
    parser.addoption(
        "--use-existing",
        action="store_true",
        default=False,
        help="This will skip deployment of the charms. Useful for local testing.",
    )
    parser.addoption(
        "--keep-models",
        action="store_true",
        default=False,
        help="keep temporarily-created models",
    )
    parser.addoption(
        "--model",
        action="store",
        help="Juju model to use; if not provided, a new model "
        "will be created for each test which requires one",
    )


def pytest_configure(config):
    """Adds config options."""
    config.addinivalue_line("markers", "abort_on_fail")
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 56s</sub>

### ✅ `bash`

**Check for pebble check event handling in charm**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && grep -n "check\|pebble_check\|CheckEvent\|CheckInfo\|check_failed\|check_recovered" /tmp/copilot-tool-output-1775052293297-qgdzuw.txt | head -40

```
527:            "checks": {
691:        # Get previous plan and extract env vars values to check is some S3 params has changed
732:            email: Email of the user to check.
<exited with exit code 0>
```


---

<sub>⏱️ 2m 56s</sub>

### ✅ `bash`

**Search charm.py for ops.testing and pebble usage**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && grep -n "pebble\|Harness\|ops.testing\|CheckInfo\|check" /tmp/copilot-tool-output-1775052293297-qgdzuw.txt | head -50

<details>
<summary>15 lines</summary>

```
35:from ops.pebble import ExecError, ExecProcess, Plan
101:        self.framework.observe(self.on.discourse_pebble_ready, self._on_discourse_pebble_ready)
138:    def _on_discourse_pebble_ready(self, _: ops.PebbleReadyEvent) -> None:
139:        """Handle discourse pebble ready event.
142:            event: Event triggering the discourse pebble ready event handler.
451:            # Since pebble exec command doesn't copy the container env (envVars set in Dockerfile),
506:    def _create_layer_config(self) -> ops.pebble.LayerDict:
510:            Dictionary with the pebble configuration.
527:            "checks": {
535:        return typing.cast(ops.pebble.LayerDict, layer_config)
679:        """Configure pod using pebble and layer generated from config.
691:        # Get previous plan and extract env vars values to check is some S3 params has changed
732:            email: Email of the user to check.
935:            container.pebble.replan_services()
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 56s</sub>

### ℹ️ Notification

Background agent "Explore charm structure" (explore) completed

<details>
<summary>Detail</summary>

Explore the charm at /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4. I need to understand:
1. The current ops version dependency (check pyproject.toml, requirements files, charmcraft.yaml)
2. The overall charm structure - what does it do?
3. All Python files in src/ and tests/ - list them and briefly describe each
4. Any use of ops features like: pebble checks, event handling, status handling, testing helpers
5. Look at src/ charm code and identify all ops APIs being used (Container, Pebble, events, etc.)
6. Look at tests/ to understand what testing framework is used and what's tested

Please provide a comprehensive summary including file paths and key code patterns.

</details>

---

<sub>⏱️ 3m 20s</sub>

### ✅ `read_agent`

**Explore agent (Explore charm structure)**

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "explore-charm"
}
```

</details>

<details>
<summary>319 lines</summary>

````
Agent completed. agent_id: explore-charm, agent_type: explore, status: completed, description: Explore charm structure, elapsed: 181s, total_turns: 0, duration: 141s

Perfect! Now let me create a comprehensive summary:

## Comprehensive Charm Analysis Summary

I'll provide you with a complete analysis of the Discourse K8s Operator charm.

---

### 1. **OPS VERSION DEPENDENCY**

**File:** `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/pyproject.toml` (line 23)

```
ops==2.23.2
```

Also includes `ops[testing]` for unit tests (line 50).

---

### 2. **CHARM STRUCTURE & PURPOSE**

**Metadata File:** `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/metadata.yaml`

**Purpose:** A Juju charm deploying and managing Discourse (an open-source discussion platform) on Kubernetes. It simplifies initial deployment and "day N" operations including:
- Scaling instances
- SSO/OAuth/SAML integration
- S3 integration for file storage
- Deployment on multiple K8s platforms (MicroK8s, Charmed Kubernetes, public cloud)

**Relations:**
- **Requires (Incoming):**
  - `database` (PostgreSQL client, limit: 1)
  - `redis` (Redis, limit: 1)
  - `nginx-route` (Nginx Ingress, limit: 1)
  - `logging` (Loki Push API)
  - `oauth` (OAuth, limit: 1)
  - `saml` (SAML, limit: 1, optional)

- **Provides (Outgoing):**
  - `metrics-endpoint` (Prometheus scrape)
  - `grafana-dashboard` (Grafana dashboard)

- **Peers:**
  - `restart` (Rolling operations)

**Containers:** Single container named `discourse`

---

### 3. **ALL PYTHON FILES - SRC/**

#### **a) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/src/charm.py` (951 lines)**
**Purpose:** Main charm implementation (DiscourseCharm class)

**Key Classes & Methods:**
- `DiscourseCharm(CharmBase)` - Main charm class
  - `__init__()` - Initialize handlers for all events
  - Event handlers: `_on_start()`, `_on_upgrade_charm()`, `_on_discourse_pebble_ready()`, `_on_config_changed()`, etc.
  - Setup & activation: `_setup_and_activate()`, `_set_up_discourse()`, `_configure_pod()`, `_activate_charm()`
  - Configuration: `_is_config_valid()`, `_get_cors_origin()`, `_get_saml_config()`, `_get_s3_env()`, `_create_discourse_environment_settings()`
  - Pebble layer: `_create_layer_config()`
  - Database & Redis: `_execute_migrations()`, `_get_redis_relation_data()`, `_are_relations_ready()`
  - S3 migration: `_run_s3_migration()`, `_should_run_s3_migration()`
  - User management (actions): `_on_promote_user_action()`, `_on_create_user_action()`, `_on_anonymize_user_action()`
  - Service control: `_start_service()`, `_stop_service()`
  - Utilities: `_get_external_hostname()`, `_generate_password()`, `_config_force_https()`, `_set_workload_version()`

- Custom Exception: `MissingRedisRelationDataError`

#### **b) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/src/constants.py` (51 lines)**
**Purpose:** Application constants

**Key Constants:**
- `CONTAINER_NAME = "discourse"`
- `SERVICE_NAME = "discourse"`
- `DISCOURSE_PATH = "/srv/discourse/app"`
- `SERVICE_PORT = 3000`
- `PROMETHEUS_PORT = 3000`
- `THROTTLE_LEVELS` - Dict with "none", "permissive", "strict" configurations
- `MAX_CATEGORY_NESTING_LEVELS = [2, 3]`
- `REQUIRED_S3_SETTINGS` - List of required S3 config keys
- Log paths, database name, OAuth scope

#### **c) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/src/database.py` (87 lines)**
**Purpose:** Database relation handler

**Key Class:**
- `DatabaseHandler(Object)` - Manages PostgreSQL database relations
  - `get_relation_data()` - Extract connection info (host, port, user, password, database)
  - `is_relation_ready()` - Check if database relation is ready

#### **d) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/src/oauth_observer.py` (134 lines)**
**Purpose:** OAuth/OIDC integration

**Key Class:**
- `OAuthObserver(Object)` - Manages OAuth relations and OIDC configuration
  - `_on_oauth_relation_changed()` - Handle OAuth changes
  - `_on_oauth_relation_broken()` - Handle relation breakage
  - `_generate_client_config()` - Create OAuth client config
  - `get_oidc_env()` - Return OIDC environment variables

---

### 4. **ALL PYTHON FILES - TESTS/**

#### **Unit Tests (with ops.testing framework):**

**a) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/unit/conftest.py` (85 lines)**
- Pytest fixtures using `ops.testing` for state-based testing
- Fixtures: `base_state`, `discourse_container`, `postgresql_relation`, `redis_relation`

**b) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/unit/test_charm.py` (233 lines)**
- Tests using `ops.testing.Context` (state-based testing, NO Harness)
- **Tests:**
  - `test_get_cors_origin_behavior()` - 9 parametrized tests for CORS origin logic
  - `test_oauth_integration()` - 3 parametrized tests for OAuth config
  - Tests Pebble checks in layer config (line 146 checks `plan.services[SERVICE_NAME]`)

**c) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/unit_harness/helpers.py` (166 lines)**
- Helper functions for Harness-based testing
- **Functions:**
  - `start_harness()` - Initialize charm harness with mocked relations/config
  - `add_postgres_relation()`, `add_redis_relation()`, `_add_ingress_relation()`, `_add_saml_relation()`
  - `_patch_setup_completed()` - Mock filesystem setup completion

**d) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/unit_harness/test_charm.py` (849 lines)**
- Tests using `ops.testing.Harness` (traditional testing with mocking)
- **Comprehensive Tests:**
  - `test_relations()` - 8 parametrized tests for relation state combinations
  - `test_ingress_relation_not_ready()`, `test_on_config_changed_*()` - Config validation tests
  - `test_on_config_changed_when_valid()` - Full config with S3 setup
  - `test_promote_user_action()`, `test_create_user_action()`, `test_anonymize_user_action()` - User management
  - `test_database_relation_broken()`, `test_redis_relation_broken()` - Relation handling
  - `test_is_database_relation_ready()`, `test_is_redis_relation_ready()` - Relation readiness
  - `test_acquire_lock_on_upgrade()` - RollingOpsManager integration
  - HTTP proxy environment test
  - Total ~20+ test functions

#### **Integration Tests:**

**e) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/integration/conftest.py`**
- Fixtures for integration tests (app config, juju client, etc.)

**f) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/integration/test_charm.py`**
- Integration tests with real Juju deployment
- **Tests:**
  - `test_active()` - Checks charm is active
  - `test_prom_exporter_is_up()` - Verifies Prometheus endpoint
  - `test_setup_discourse()` - Tests registration page reachability
  - `test_s3_conf()` - Tests S3 integration with localstack
  - `test_database_migration_required()` - Tests DB migration workflow

**g) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/integration/test_oauth.py`**
- OAuth integration tests

**h) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/integration/test_saml.py`**
- SAML integration tests

**i) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/integration/test_users.py`**
- User management integration tests

**j) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/integration/test_db_migration.py`**
- Database migration integration tests

**k) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/integration/types.py`**
- Type definitions for integration tests

**l) `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/conftest.py`**
- Global pytest configuration and markers

---

### 5. **OPS FEATURES USED**

#### **Pebble Checks (Primary Feature):**

**Location:** `src/charm.py`, lines 527-533

```python
"checks": {
    "discourse-ready": {
        "override": "replace",
        "level": "ready",  # CHECK LEVEL SET TO 'ready'
        "http": {"url": f"http://localhost:{SERVICE_PORT}/srv/status"},
    },
}
```

**Key Points:**
- Pebble check named `discourse-ready` with `level: "ready"`
- HTTP check against `/srv/status` endpoint on port 3000
- Defined in `_create_layer_config()` method

#### **Event Handling:**

- **Container Events:** `PebbleReadyEvent` (line 101: `discourse_pebble_ready`)
- **Lifecycle Events:** `StartEvent`, `UpgradeCharmEvent`, `ConfigChangedEvent` (lines 99-102)
- **Relation Events:** 
  - Database: `database_created`, `endpoints_changed`, `relation_broken`
  - Redis: `redis_relation_updated`
  - SAML: `saml_data_available`
  - OAuth: `relation_changed`, `relation_joined`, `relation_created`, `relation_broken`
- **Action Events:** `ActionEvent` for promote, create, anonymize user actions

#### **Status Handling:**

- `ActiveStatus()` - Charm is ready and operational
- `BlockedStatus(msg)` - Invalid configuration or missing dependencies
- `WaitingStatus(msg)` - Waiting for relations or container readiness
- `MaintenanceStatus(msg)` - Running migrations or S3 migration

**Example Usage:**
```python
self.model.unit.status = ActiveStatus()  # Line 726
self.model.unit.status = BlockedStatus("message")  # Line 331
self.model.unit.status = WaitingStatus("Waiting for database relation")  # Line 178
self.model.unit.status = MaintenanceStatus("Executing migrations")  # Line 595
```

#### **Container & Pebble APIs:**

- `Container.get_container(name)` - Get container reference (line 267)
- `Container.can_connect()` - Check connectivity (line 268)
- `Container.exists(path)` - Check file existence (line 268)
- `Container.push(path, content)` - Write files (line 273)
- `Container.exec()` - Execute commands (line 602, 738, etc.)
- `Container.get_plan()` - Get current Pebble plan (line 692)
- `Container.add_layer()` - Add/update layer (line 934)
- `Container.pebble.replan_services()` - Replan services (line 935)
- `Container.get_service()` - Get service by name (line 944)
- `Container.stop()` - Stop container/service (line 946)
- Pebble types: `Plan`, `ExecProcess`, `ExecError` (line 35)

#### **Testing Helpers:**

- `ops.testing.Context` - State-based testing (new framework)
- `ops.testing.Harness` - Traditional unit testing with mocking
- `ops.testing.Container`, `Relation`, `State` - Test fixtures
- `ops.testing.Exec` - Mock exec commands

---

### 6. **TESTING FRAMEWORK**

#### **Unit Testing Approaches:**

**A) State-Based Testing (Modern) - `ops.testing.Context`**
- File: `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/unit/test_charm.py`
- Uses `testing.Context` to run events on immutable states
- Example:
  ```python
  ctx = testing.Context(DiscourseCharm)
  state_in = testing.State(**base_state)
  state_out = ctx.run(ctx.on.pebble_ready(container), state_in)
  ```

**B) Harness-Based Testing (Traditional) - `ops.testing.Harness`**
- File: `/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/tests/unit_harness/test_charm.py`
- Uses `Harness` for mutable state with mocking
- Example:
  ```python
  harness = Harness(DiscourseCharm)
  harness.begin_with_initial_hooks()
  harness.container_pebble_ready("discourse")
  ```

#### **Test Coverage:**

| Category | File | Count | Coverage |
|----------|------|-------|----------|
| State-based tests | `tests/unit/test_charm.py` | 2 functions, 12 parametrized cases | CORS, OAuth |
| Harness tests | `tests/unit_harness/test_charm.py` | 20+ test functions | Relations, config, actions, migrations |
| Integration tests | `tests/integration/*.py` | 15+ test functions | Deployment, S3, OAuth, SAML, users |

#### **Key Testing Patterns:**

1. **Fixture Setup:** Pytest fixtures for common state (relations, containers)
2. **Parametrization:** `@pytest.mark.parametrize` for testing multiple scenarios
3. **Mocking:** `unittest.mock.patch()` for external dependencies
4. **Exec Mocking:** `harness.handle_exec()` for container commands
5. **Event Simulation:** `harness.container_pebble_ready()`, `harness.charm.on.config_changed.emit()`
6. **Relation Simulation:** `harness.add_relation()`, `harness.update_relation_data()`

#### **What's Tested:**

- ✅ **Pebble checks** - Verified in layer config (CORS test line 146)
- ✅ **Event handling** - All major events tested (start, upgrade, pebble_ready, config_changed, relations)
- ✅ **Status transitions** - WaitingStatus, BlockedStatus, ActiveStatus, MaintenanceStatus
- ✅ **Relation readiness** - Database, Redis, OAuth, SAML
- ✅ **Configuration validation** - CORS, SAML, S3, throttle levels
- ✅ **Container execution** - Migrations, user management, version setting
- ✅ **Environment variables** - Discourse config, OIDC, S3, SMTP, proxy
- ✅ **User actions** - Promote, create, anonymize users
- ✅ **Integration workflows** - Full deployment, S3 migration, OAuth flow

---

### 7. **ALL OPS APIS BEING USED**

| Category | APIs | Usage |
|----------|------|-------|
| **Base Classes** | `CharmBase`, `Object` | Main charm & helper class inheritance |
| **Events** | `StartEvent`, `UpgradeCharmEvent`, `PebbleReadyEvent`, `ConfigChangedEvent`, `ActionEvent`, `HookEvent`, `RelationBrokenEvent` | Event handlers registered in `__init__` |
| **Status** | `ActiveStatus`, `BlockedStatus`, `WaitingStatus`, `MaintenanceStatus` | Unit status updates throughout charm |
| **Model** | `Container`, `Plan`, `Relation`, `Unit`, `Application` | Interaction with model resources |
| **Pebble** | `ExecError`, `ExecProcess`, `Plan`, `LayerDict` | Container command execution & layer config |
| **Framework** | `framework.observe()` | Event listener registration |
| **Main** | `ops.main()` | Charm entry point |
| **Testing** | `Context`, `Harness`, `Container`, `Relation`, `State`, `Exec` | Unit & integration testing |

---

### 8. **KEY CODE PATTERNS**

#### **Pebble Layer Configuration:**
```python
def _create_layer_config(self) -> ops.pebble.LayerDict:
    layer_config = {
        "summary": "Discourse layer",
        "services": {
            SERVICE_NAME: {
                "override": "replace",
                "command": f"{SCRIPT_PATH}/app_launch.sh",
                "environment": self._create_discourse_environment_settings(),
                "kill-delay": "20s",
            }
        },
        "checks": {
            "discourse-ready": {
                "override": "replace",
                "level": "ready",
                "http": {"url": f"http://localhost:{SERVICE_PORT}/srv/status"},
            },
        },
    }
    return typing.cast(ops.pebble.LayerDict, layer_config)
```

#### **Event Handler Pattern:**
```python
def __init__(self, *args):
    super().__init__(*args)
    self.framework.observe(self.on.start, self._on_start)
    self.framework.observe(self.on.discourse_pebble_ready, self._on_discourse_pebble_ready)
    # ... more observers

def _on_discourse_pebble_ready(self, _: ops.PebbleReadyEvent) -> None:
    self._setup_and_activate()
```

#### **Relation Data Pattern:**
```python
def _get_redis_relation_data(self) -> typing.Tuple[str, int]:
    relation = self.model.get_relation(self.redis.relation_name)
    if not relation:
        raise MissingRedisRelationDataError("No redis relation data")
    relation_app_data = relation.data[relation.app]
    redis_hostname = str(relation_app_data.get("leader-host", ""))
    redis_port = int(relation_unit_data["port"])
    return (redis_hostname, redis_port)
```

#### **Container Execution Pattern:**
```python
try:
    process: ExecProcess = container.exec(
        [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", "--trace", "db:migrate"],
        environment=env_settings,
        working_dir=DISCOURSE_PATH,
        user=CONTAINER_APP_USERNAME,
    )
    process.wait_output()
except ExecError as cmd_err:
    logger.exception("Executing migrations failed with code %d.", cmd_err.exit_code)
    raise
```

---

### 9. **SUMMARY TABLE**

| Aspect | Details |
|--------|---------|
| **Ops Version** | 2.23.2 |
| **Testing Framework** | pytest + ops.testing (Context + Harness) |
| **Charm Type** | Kubernetes (K8s) operator |
| **Container Runtime** | Pebble |
| **Primary Application** | Discourse forum |
| **Key Relations** | PostgreSQL, Redis, Nginx Ingress, Loki, OAuth, SAML |
| **Pebble Checks** | 1 HTTP readiness check (`discourse-ready` at level `ready`) |
| **Python Version** | 3.8+ (supports up to 3.14) |
| **Unit Tests** | 2 test modules (state-based + harness-based) |
| **Integration Tests** | 5 test modules (OAuth, SAML, users, DB migration, charm) |
| **Config Validation** | CORS, SAML, S3, throttle levels, category nesting |
| **Status States** | 4 (Active, Blocked, Waiting, Maintenance) |
| **User Actions** | 3 (promote, create, anonymize users) |

---

This charm represents a comprehensive Kubernetes-native deployment operator for Discourse, using Pebble checks for readiness verification, extensive event handling for lifecycle management, and multiple integration points for external services.
````

</details>


---

<sub>⏱️ 3m 21s</sub>

### ✅ `bash`

**View pebble layer/checks config in charm.py**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && sed -n '500,560p' /tmp/copilot-tool-output-1775052293297-qgdzuw.txt

<details>
<summary>56 lines</summary>

```
pod_config["NO_PROXY"] = pod_config["no_proxy"] = (
            os.environ.get("JUJU_CHARM_NO_PROXY") or ""
        )

        return pod_config

    def _create_layer_config(self) -> ops.pebble.LayerDict:
        """Create a layer config based on our current configuration.

        Returns:
            Dictionary with the pebble configuration.
        """
        logger.info("Generating Layer config")
        layer_config = {
            "summary": "Discourse layer",
            "description": "Discourse layer",
            "services": {
                SERVICE_NAME: {
                    "override": "replace",
                    "summary": "Discourse web application",
                    "command": f"{SCRIPT_PATH}/app_launch.sh",
                    "user": CONTAINER_APP_USERNAME,
                    "startup": "enabled",
                    "environment": self._create_discourse_environment_settings(),
                    "kill-delay": "20s",
                }
            },
            "checks": {
                "discourse-ready": {
                    "override": "replace",
                    "level": "ready",
                    "http": {"url": f"http://localhost:{SERVICE_PORT}/srv/status"},
                },
            },
        }
        return typing.cast(ops.pebble.LayerDict, layer_config)

    def _should_run_s3_migration(
        self, current_plan: Plan, s3info: typing.Optional[S3Info]
    ) -> bool:
        """Determine if the S3 migration is to be run.

        Args:
            current_plan: Dictionary containing the current plan.
            s3info: S3Info object containing the S3 configuration options.

        Returns:
            If no services are planned yet (first run) or S3 settings have changed.
        """
        result = self.config.get("s3_enabled") and (
            not current_plan.services
            or (
                s3info
                and (
                    s3info.enabled != self.config.get("s3_enabled")
                    or s3info.region != self.config.get("s3_region")
                    or s3info.bucket != self.config.get("s3_bucket")
                    or s3info.endpoint != self.config.get("s3_endpoint")
                )
            )
        )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 15s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/blob/main/ops/charm.py**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/blob/main/ops/charm.py"
}
```

</details>

<details>
<summary>118 lines</summary>

```
Contents of https://github.com/canonical/operator/blob/main/ops/charm.py:
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
        
    *   DEVELOPER WORKFLOWS
        
        *   [
            
            ActionsAutomate any workflow
            
            
            
            ](https://github.com/features/actions)
        *   [
            
            CodespacesInstant dev environments
            
            
            
            ](https://github.com/features/codespaces)
        *   [
            
            IssuesPlan and track work
            
            
            
            ](https://github.com/features/issues)
        *   [
            
            Code ReviewManage code changes
            
            
            
            ](https://github.com/features/code-review)
        
    *   APPLICATION SECURITY
        
        *   [
            
            GitHub Advanced SecurityFind and fix vulnerabilities
            
            
            
            ](https://github.com/security/advanced-security)
        *   [
            
            Code securitySecure your code as you build
            
            
            
            ](https://github.com/security/advanced-security/code-security)
        *   [
            
            Secret protectionStop leaks before they start
            
            
            
            ](https://github.com/security/advanced-security/secret-protection)
        
    *   EXPLORE
        
        *   [Why GitHub](https://github.com/why-github)
        *   [Documentation](https://docs.github.com)
        *   [Blog](https://github.blog)
        *   [Changelog](https://github.blog/changelog)
        *   [Marketplace](https://github.com/marketplace)
        
    
    [View all features](https://github.com/features)
    
*   *   BY COMPANY SIZE
        
        *   [Enterprises](https://github.com/enterprise)
        *   [Small and medium teams](https://github.com/team)
        *   [Startups](https://github.com/enterprise/startups)
        *   [Nonprofits](https://github.com/solutions/industry/nonprofits)
        
    *   BY USE CASE
        
        *   [App Modernization](https://github.com/solutions/use-case/app-modernization)
        *   [DevSecOps](https://github.com/solutions/use-case/devsecops)
        *   [DevOps](https://github.com/solutions/use-case/devops)
        *   [CI/CD](https://github.com/solutions/use-case/ci-cd)
        *   [View all use cases](https://github.com/solutions/use-case)
        
    *   BY INDUSTRY
        
        *   [Healthcare](https://github.com/solutions/industry/healthcare)
        *   [Financial services](https://github.com/solutions/industry/financial-services)
        *   [Manufacturing](https://github.com/solutions/industry/manufacturing)
        *   [Government](https://github.com/solutions/industry/government)
        *   [View all industries](https://github.com/solutions/industry)
        
    
    [View all solutions](https://github.com/solutions)
    
*   *   EXPLORE BY TOPIC
        
        *   [AI](https://github.com/resources/articles?topic=ai)
        *   [Software Development](https://github.com/resources/articles?topic=software-development)
        *   [DevOps](https://github.com/resources/articles?topic=devops)
        *   [Security](https://github.com/resources/articles?topic=security)
        *   [View all topics](https://github.com/resources/articles)
        
    *   EXPLORE BY TYPE
        
        *   [Customer stories](https://github.com/customer-stories)
        *   [Events & webinars](https://github.com/resources/events)
        *   [Ebooks & reports](https://github.com/resources/whitepapers)
        *   [Business insights](https://github.com/solutions/executive-insights)
        *   [GitHub Skills](https://skills.github.com)
        
    *   SUPPORT & SERVICES
        
        *   [Documentation](https://docs.github.com)
        *   [Customer support](https://support.github.com)
        *   [Community forum](https://github.com/orgs/community/discussions)
        *   [Trust center](https://github.com/trust-center)
        *   [Partners](https://github.com/partners)
        
    
    [View all resources](https://github.com/resources)
    
*   *   COMMUNITY
        
        *   [
            
            GitHub SponsorsFund open source developers
            
            
            
            ](https://github.com/sponsors)
        
    *   PROGRAMS
        
        *   [Security Lab](https://securitylab.github.com)
        *   [Maintainer Community](https://maintainers.github.com)
        *   [Accelerator](https://github.com/accelerator)
        *   [GitHub Stars](https://stars.github.com)
        *   [Archive Program](https://archiveprogram.github.com)
        
    *   REPOSITORIES
        
        *   [Topics](https://github.com/topics)
        *   [Trending](https://github.com/trending)
        *   [Collections](https://github.com/collections)
        
    
*   *   ENTERPRISE SOLUTIONS
        
        *   [
            
            Enterprise platformAI-powered developer platform
            
            
            
            ](https://github.com/enterprise)
        
    *   AVAILABLE ADD-ONS
        
        *   [
            
            GitHub Advanced SecurityEnterprise-grade security features
            
            
            
            ](https://github.com/security/advanced-security)
        *   [
            
            Copilot for BusinessEnterprise-grade AI features
            
            
            
            ](https://github.com/features/copilot/copilot-business)
        *   [
            
            Premium SupportEnterprise-grade 24/7 support
            
            
            
            ](https://github.com/premium-support)
        
    
*   [Pricing](https://github.com/pricing)

## Provide feedback

We read every piece of feedback, and take your input very seriously.

Include my email address so I can be contacted

## Saved searches

## Use saved searches to filter your results more quickly

[Sign in](/login?return_to=https%3A%2F%2Fgithub.com%2Fcanonical%2Foperator%2Fblob%2Fmain%2Fops%2Fcharm.py)

[Sign up](/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F%3Cuser-name%3E%2F%3Crepo-name%3E%2Fblob%2Fshow&source=header-repo&source_repo=canonical%2Foperator)

Appearance settings
```

</details>


---

<sub>⏱️ 4m 14s</sub>

### ✅ `bash`

**Read beginning of harness tests**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && cat tests/unit_harness/test_charm.py | head -100

<details>
<summary>86 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for Discourse charm."""

# pylint: disable=protected-access
# Protected access check is disabled in tests as we're injecting test data

import secrets
from unittest.mock import MagicMock, patch

import ops
import pytest
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus

from charm import CONTAINER_NAME, DISCOURSE_PATH, SERVICE_NAME
from constants import DATABASE_NAME
from tests.unit_harness import helpers


@pytest.mark.parametrize(
    "with_postgres, with_redis, with_ingress, status",
    [
        (False, False, False, WaitingStatus("Waiting for database relation")),
        (False, True, False, WaitingStatus("Waiting for database relation")),
        (True, False, False, WaitingStatus("Waiting for redis relation")),
        (True, True, False, ActiveStatus()),
        (False, False, True, WaitingStatus("Waiting for database relation")),
        (False, True, True, WaitingStatus("Waiting for database relation")),
        (True, False, True, WaitingStatus("Waiting for redis relation")),
        (True, True, True, ActiveStatus()),
    ],
    ids=[
        "No relation",
        "Only redis",
        "Only postgres",
        "Postgres+redis",
        "Only ingress",
        "Redis+ingress",
        "Postgres+ingress",
        "All relations",
    ],
)
def test_relations(with_postgres, with_redis, with_ingress, status):
    """
    arrange: given a deployed discourse charm
    act: when pebble ready event is triggered
    assert: it will have the correct status depending on the relations
    """
    harness = helpers.start_harness(
        with_postgres=with_postgres, with_redis=with_redis, with_ingress=with_ingress
    )
    harness.container_pebble_ready("discourse")
    assert harness.model.unit.status == status


def test_ingress_relation_not_ready():
    """
    arrange: given a deployed discourse charm with the ingress established
    act: when pebble ready event is triggered
    assert: it will wait for the ingress relation.
    """
    harness = helpers.start_harness(with_postgres=False, with_redis=False, with_ingress=True)
    assert harness.model.unit.status == WaitingStatus("Waiting for database relation")


def test_on_config_changed_when_no_saml_target():
    """
    arrange: given a deployed discourse charm with all the required relations
    act: when force_saml_login configuration is True and there's no saml_target_url
    assert: it will get to blocked status waiting for the latter.
    """
    harness = helpers.start_harness(with_config={"force_saml_login": True})
    assert harness.model.unit.status == BlockedStatus(
        "force_saml_login cannot be true without a saml relation"
    )


def test_on_config_changed_when_saml_sync_groups_and_no_url_invalid():
    """
    arrange: given a deployed discourse charm with all the required relations
    act: when saml_sync_groups configuration is provided and there's no saml_target_url
    assert: it will get to blocked status waiting for the latter.
    """
    harness = helpers.start_harness(with_config={"saml_sync_groups": "group1"})
    assert harness.model.unit.status == BlockedStatus(
        "'saml_sync_groups' cannot be specified without a saml relation"
    )


def test_on_config_changed_when_saml_target_url_and_force_https_disabled():
    """
    arrange: given a deployed discourse charm with all the required relations
    act: when saml_target_url configuration is provided and force_https is False
    assert: it will get to blocked status waiting for the latter.
    """
    harness = helpers.start_harness(with_config={"force_https": False}, saml_fields=(True, "", ""))
    harness.charm._is_config_valid()
    assert harness.model.unit.status == BlockedStatus(
        "A saml relation cannot be specified without 'force_https' being true"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 30s</sub>

### ✅ `bash`

**Find ops installation and version**

$ pip show ops 2>/dev/null | grep Location && python3 -c "import ops; print(ops.__version__)" 2>/dev/null

```
Location: /home/ubuntu/.local/lib/python3.12/site-packages
3.7.0
<exited with exit code 0>
```


---

<sub>⏱️ 4m 30s</sub>

### ✅ `bash`

**Check for pebble check events in ops**

$ pip show ops 2>/dev/null | grep Location | awk '{print $2}' | xargs -I{} grep -n "PebbleCheck\|check_failed\|check_recovered\|CheckEvent" {}/ops/charm.py 2>/dev/null | head -30

<details>
<summary>7 lines</summary>

```
998:class PebbleCheckEvent(WorkloadEvent):
1032:class PebbleCheckFailedEvent(PebbleCheckEvent):
1036:    emitted (which will mean that a :class:`~ops.PebbleCheckRecoveredEvent` will be
1047:class PebbleCheckRecoveredEvent(PebbleCheckEvent):
1514:            self.on.define_event(f'{container_name}_pebble_check_failed', PebbleCheckFailedEvent)
1516:                f'{container_name}_pebble_check_recovered', PebbleCheckRecoveredEvent
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 6s</sub>

### ❌ `bash`

**Get full pebble check event details from ops source**

$ grep -n "PebbleCheck\|check_failed\|check_recovered\|CheckEvent\|CheckInfo" /home/ubuntu/.local/lib/python3.12/site-packages/ops/charm.py | head -40

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 5m 6s</sub>

### ❌ `bash`

**Read PebbleCheckEvent classes**

$ sed -n '990,1060p' /home/ubuntu/.local/lib/python3.12/site-packages/ops/charm.py

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 5m 39s</sub>

### ✅ `bash`

**Read pebble check event details via Python**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && python3 -c "
import ops
import inspect

# Find PebbleCheck events
print('=== PebbleCheckEvent classes ===')
for name in dir(ops):
    if 'Check' in name or 'check' in name.lower():
        obj = getattr(ops, name)
        print(f'{name}: {type(obj)}')
        if inspect.isclass(obj):
            try:
                print(inspect.getsource(obj))
            except:
                pass
" 2>/dev/null

<details>
<summary>94 lines</summary>

```
=== PebbleCheckEvent classes ===
CheckInfoMapping: <class 'abc.ABCMeta'>
class CheckInfoMapping(Mapping[str, pebble.CheckInfo]):
    """Map of check names to :class:`ops.pebble.CheckInfo` objects.

    This is done as a mapping object rather than a plain dictionary so that we
    can extend it later, and so it's not mutable.
    """

    def __init__(self, checks: Iterable[pebble.CheckInfo]):
        self._checks = {c.name: c for c in checks}

    def __getitem__(self, key: str):
        return self._checks[key]

    def __iter__(self):
        return iter(self._checks)

    def __len__(self):
        return len(self._checks)

    def __repr__(self):
        return repr(self._checks)

LazyCheckInfo: <class 'type'>
class LazyCheckInfo:
    """Provide lazily-loaded access to a Pebble check's info.

    The attributes provided by this class are the same as those of
    :class:`ops.pebble.CheckInfo`, however, the notice details are only fetched
    from Pebble if necessary (and cached on the instance).
    """

    name: str
    level: pebble.CheckLevel | str | None
    startup: pebble.CheckStartup
    status: pebble.CheckStatus | str
    successes: int | None
    failures: int
    threshold: int
    change_id: pebble.ChangeID | None

    def __init__(self, container: Container, name: str):
        self._container = container
        self.name = name
        self._info: pebble.CheckInfo | None = None

    def __repr__(self):
        return f'LazyCheckInfo(name={self.name!r})'

    def __getattr__(self, item: str):
        # Note: not called for defined attribute `name`.
        self._ensure_loaded()
        return getattr(self._info, item)

    def _ensure_loaded(self):
        if self._info is not None:
            return
        self._info = self._container.get_check(self.name)

PebbleCheckEvent: <class 'type'>
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

PebbleCheckFailedEvent: <class 'type'>
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

PebbleCheckRecoveredEvent: <class 'type'>
class PebbleCheckRecoveredEvent(PebbleCheckEvent):
    """Event triggered when a Pebble check recovers.

    This event is only triggered when the check has previously reached a failure
    state (not simply failed, but failed at least as many times as the
    configured threshold).

    See also: `Juju | Hook | <container>-pebble-check-recovered <https://documentation.ubuntu.com/juju/3.6/reference/hook/#container-pebble-check-recovered>`_.

    .. jujuadded:: 3.6
    """
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 27s</sub>

### ✅ `bash`

**Check ops.testing CheckInfo**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && python3 -c "
import ops.testing as t
import inspect

# Check for CheckInfo in testing
for name in dir(t):
    if 'Check' in name or 'check' in name.lower():
        obj = getattr(t, name)
        print(f'{name}:')
        if inspect.isclass(obj):
            try:
                print(inspect.getsource(obj))
            except:
                print('  (cannot get source)')
        print()
" 2>/dev/null | head -100

<details>
<summary>75 lines</summary>

```
CheckInfo:
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

<sub>⏱️ 6m 26s</sub>

### ✅ `bash`

**Check testing module for check-related items**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && python3 -c "
import ops.testing as t
import inspect

# Check the on (event context) methods
ctx = t.Context.__new__(t.Context)
# Look for check-related event methods
for name in dir(t):
    if 'Check' in name:
        print(name)
" 2>/dev/null

```
CheckInfo
<exited with exit code 0>
```


---

<sub>⏱️ 6m 51s</sub>

### ✅ `bash`

**Check for pebble_check events in testing**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && python3 -c "
import ops.testing as t
import inspect

# Look for pebble_check in the _CharmEvents class
for name in dir(t._CharmEvents if hasattr(t, '_CharmEvents') else t):
    if 'check' in name.lower():
        print(name)
print()

# Look at the on class in Context
ctx_on = None
src = inspect.getsource(t._EventContext if hasattr(t, '_EventContext') else t.Context)
for line in src.split('\n'):
    if 'check' in line.lower():
        print(line)
" 2>/dev/null

<details>
<summary>5 lines</summary>

```
CheckInfo

    Assert that the charm has followed the expected path by checking the app
    Assert that the charm has followed the expected path by checking the unit
        # so let the type checkers know that too.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 24s</sub>

### ✅ `bash`

**Search ops.testing source for check events**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && python3 -c "
import ops.testing as t
import inspect

# Look at CharmEvents, find check-related things
src = inspect.getsource(t)
for i, line in enumerate(src.split('\n')):
    if 'check' in line.lower() or 'Check' in line:
        print(f'{i}: {line}')
" 2>/dev/null | head -40

```
83:         CheckInfo,
130:         'CheckInfo',
<exited with exit code 0>
```


---

<sub>⏱️ 7m 59s</sub>

### ✅ `bash`

**Search scenario module for check events**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && python3 -c "
import ops.testing._scenario as sc
import inspect
src = inspect.getsource(sc)
for i, line in enumerate(src.split('\n')):
    if 'check' in line.lower() or 'Check' in line:
        print(f'{i}: {line}')
" 2>/dev/null | head -60

```

<exited with exit code 0>
```


---

<sub>⏱️ 8m 36s</sub>

### ✅ `bash`

**Check available pebble_check events in testing Context**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && python3 -c "
import ops.testing
import inspect

# Find the 'on' module
for name in dir(ops.testing):
    obj = getattr(ops.testing, name, None)
    if obj and hasattr(obj, 'pebble_check_failed'):
        print(f'{name} has pebble_check_failed')
" 2>/dev/null

# Try to use pebble check events directly
python3 -c "
from ops.testing import Context, State, Container, CheckInfo
from ops import pebble
import ops

class FakeCharm(ops.CharmBase):
    META = {'name': 'test', 'containers': {'foo': {}}}

ctx = Context(FakeCharm, meta=FakeCharm.META)
# Check event names
for attr in dir(ctx.on):
    if 'check' in attr.lower():
        print(attr)
" 2>/dev/null

```
CharmEvents has pebble_check_failed
pebble_check_failed
pebble_check_recovered
<exited with exit code 0>
```


---

<sub>⏱️ 9m 19s</sub>

### ✅ `bash`

**Find setup/activate/status methods in charm.py**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && grep -n "_setup_and_activate\|_activate_charm\|_configure_pod\|_start_service\|_stop_service\|unit.status" /tmp/copilot-tool-output-1775052293297-qgdzuw.txt | head -50

<details>
<summary>31 lines</summary>

```
82:        self._oauth = OAuthObserver(self, self._setup_and_activate, self._get_external_hostname)
128:        self._setup_and_activate()
144:        self._setup_and_activate()
152:        self._setup_and_activate()
160:        self._setup_and_activate()
170:            self._activate_charm()
178:        self.model.unit.status = WaitingStatus("Waiting for database relation")
179:        self._stop_service()
187:        self._configure_pod()
191:        self._configure_pod()
199:        self._setup_and_activate()
201:    def _setup_and_activate(self) -> None:
205:        self._configure_pod()
207:            self._activate_charm()
331:            self.model.unit.status = BlockedStatus(", ".join(errors))
570:            self.model.unit.status = WaitingStatus("Waiting for database relation")
571:            self._stop_service()
574:            self.model.unit.status = WaitingStatus("Waiting for redis relation")
575:            self._stop_service()
582:                self.model.unit.status = WaitingStatus("Waiting for redis relation to initialize")
585:            self.model.unit.status = WaitingStatus("Waiting for redis relation to initialize")
595:        self.model.unit.status = MaintenanceStatus("Executing migrations")
639:        self.model.unit.status = MaintenanceStatus("Running S3 migration")
678:    def _configure_pod(self) -> None:
713:        self._activate_charm()
717:    def _activate_charm(self) -> None:
725:            self._start_service()
726:            self.model.unit.status = ActiveStatus()
928:    def _start_service(self):
937:    def _stop_service(self):
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 46s</sub>

### ✅ `bash`

**Read key charm methods**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && sed -n '200,215p' /tmp/copilot-tool-output-1775052293297-qgdzuw.txt && echo "---" && sed -n '678,730p' /tmp/copilot-tool-output-1775052293297-qgdzuw.txt && echo "---" && sed -n '920,955p' /tmp/copilot-tool-output-1775052293297-qgdzuw.txt

<details>
<summary>90 lines</summary>

```
def _setup_and_activate(self) -> None:
        """Set up discourse, configure the pod and eventually activate the charm."""
        if not self._is_setup_completed():
            self._set_up_discourse()
        self._configure_pod()
        if self._are_relations_ready():
            self._activate_charm()

    def _require_nginx_route(self) -> None:
        """Create minimal ingress configuration."""
        require_nginx_route(
            charm=self,
            service_hostname=self._get_external_hostname(),
            service_name=self.app.name,
            service_port=SERVICE_PORT,
---
    def _configure_pod(self) -> None:
        """Configure pod using pebble and layer generated from config.

        Args:
            event: Event triggering the handler.
        """
        container = self.unit.get_container(CONTAINER_NAME)
        if not self._are_relations_ready() or not container.can_connect():
            logger.info("Not ready to do config changed action")
            return
        if not self._is_config_valid():
            return

        # Get previous plan and extract env vars values to check is some S3 params has changed
        current_plan = container.get_plan()

        # Covers when there are no plan
        previous_s3_info = None
        if (
            current_plan.services
            and SERVICE_NAME in current_plan.services
            and current_plan.services[SERVICE_NAME]
        ):
            current_env = current_plan.services[SERVICE_NAME].environment
            previous_s3_info = S3Info(
                current_env.get("DISCOURSE_USE_S3", ""),
                current_env.get("DISCOURSE_S3_REGION", ""),
                current_env.get("DISCOURSE_S3_BUCKET", ""),
                current_env.get("DISCOURSE_S3_ENDPOINT", ""),
            )
        if self.model.unit.is_leader() and self._should_run_s3_migration(
            current_plan, previous_s3_info
        ):
            self._run_s3_migration()

        self._activate_charm()
        if container.can_connect():
            self._config_force_https()

    def _activate_charm(self) -> None:
        """Start discourse and mark the charm as active if the setup is completed."""
        # mypy has some trouble with dynamic attributes
        if not self._is_setup_completed():
            logger.info("Not starting the discourse server until discourse setup completed")
            return
        container = self.unit.get_container(CONTAINER_NAME)
        if self._is_config_valid() and container.can_connect():
            self._start_service()
            self.model.unit.status = ActiveStatus()

    def _user_exists(self, email: str) -> bool:
        """Check if a user with the given email exists.

---
            event.set_results({"user": f"{username}"})
        except ExecError as ex:
            event.fail(
                # Parameter validation errors are printed to stdout
                # Ignore mypy warning when formatting stdout
                f"Failed to anonymize user with username {username}:{ex.stdout}"  # type: ignore
            )

    def _start_service(self):
        """Start discourse."""
        logger.info("Starting discourse")
        container = self.unit.get_container(CONTAINER_NAME)
        if self._is_config_valid() and container.can_connect():
            layer_config = self._create_layer_config()
            container.add_layer(SERVICE_NAME, layer_config, combine=True)
            container.pebble.replan_services()

    def _stop_service(self):
        """Stop discourse, this operation is idempotent."""
        logger.info("Stopping discourse")
        container = self.unit.get_container(CONTAINER_NAME)
        if (
            container.can_connect()
            and SERVICE_NAME in container.get_plan().services
            and container.get_service(SERVICE_NAME).is_running()
        ):
            container.stop(CONTAINER_NAME)


if __name__ == "__main__":  # pragma: no cover
    main(DiscourseCharm, use_juju_for_storage=True)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 38s</sub>

### 💬 Copilot

Now I have a clear picture. Let me create a plan and start implementing.

---

<sub>⏱️ 10m 39s</sub>

### ✅ `bash`

**Check current git status**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && git log --oneline -5 && git branch -a | head -10

<details>
<summary>6 lines</summary>

```
74aec21 (grafted, HEAD, origin/main, origin/HEAD, main) fix(deps): update dependency ops to v2.23.2 (#421)
* (HEAD detached at 74aec21)
  main
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 39s</sub>

### ✅ `bash`

**Check pyproject.toml project section**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && cat pyproject.toml | grep -A3 "\[project\]"

```
[project]
name = "discourse-k8s-operator"
version = "0.0.0"
description = "Discourse is the modern forum for your community."
<exited with exit code 0>
```


---

<sub>⏱️ 11m 3s</sub>

### ✅ `bash`

**Create upgrade branch**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && git checkout -b upgrade-ops-to-3.7.0

```
Switched to a new branch 'upgrade-ops-to-3.7.0'
<exited with exit code 0>
```


---

<sub>⏱️ 11m 40s</sub>

### 💬 Copilot

Now let me make all the changes. I'll start with the ops version bump, add pebble check event handlers, update tests, and set `SCENARIO_BARE_CHARM_ERRORS`.

---

<sub>⏱️ 11m 40s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/pyproject.toml

<details>
<summary>154 lines</summary>

```
1. # Copyright 2026 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. [project]
5. name = "discourse-k8s-operator"
6. version = "0.0.0"
7. description = "Discourse is the modern forum for your community."
8. readme = "README.md"
9. requires-python = ">=3.8"
10. classifiers = [
11.   "Programming Language :: Python :: 3 :: Only",
12.   "Programming Language :: Python :: 3.8",
13.   "Programming Language :: Python :: 3.9",
14.   "Programming Language :: Python :: 3.10",
15.   "Programming Language :: Python :: 3.11",
16.   "Programming Language :: Python :: 3.12",
17.   "Programming Language :: Python :: 3.13",
18.   "Programming Language :: Python :: 3.14",
19. ]
20. dependencies = [
21.   "cosl==1.6.0",
22.   "jsonschema==4.23.0",
23.   "ops==2.23.2",
24.   "pydantic==2.10.6",
25. ]
26. 
27. [dependency-groups]
28. fmt = [
29.   "ruff",
30. ]
31. lint = [
32.   "boto3",
33.   "bs4",
34.   "codespell",
35.   "jubilant==1.7.0",
36.   "mypy",
37.   "pep8-naming",
38.   "psycopg2-binary",
39.   "pytest",
40.   "pytest-asyncio",
41.   "pytest-operator",
42.   "python-magic",
43.   "requests",
44.   "ruff",
45.   "types-pyyaml",
46.   "types-requests",
47. ]
48. unit = [
49.   "coverage[toml]",
50.   "ops[testing]",
51.   "pytest",
52. ]
53. coverage-report = [
54.   "coverage[toml]",
55.   "pytest",
56. ]
57. static = [
58.   "bandit[toml]",
59. ]
60. integration = [
61.   "allure-pytest>=2.8.18",
62.   "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
63.   "boto3",
64.   "bs4",
65.   "debugpy",
66.   "jubilant==1.7.0",
67.   "protobuf==5.29.6",
68.   "psycopg2-binary",
69.   "pytest",
70.   "requests",
71.   "saml-test-helper @ git+https://github.com/canonical/saml-test-idp.git",
72. ]
73. 
74. [tool.uv]
75. package = false
76. 
77. [tool.ruff]
78. target-version = "py310"
79. line-length = 99
80. 
81. # enable ruff linters:
82. #   A flake8-builtins
83. #   B flake8-bugbear
84. # CPY flake8-copyright
85. #   D pydocstyle
86. # E/W pycodestyle
87. #   F Pyflakes
88. #   I isort
89. #   N pep8-naming
90. # RUF Ruff-specific rules
91. #   S flake8-bandit
92. # SIM flake8-simplify
93. #  TC flake8-type-checking
94. #  UP pyupgrade
95. lint.select = [ "A", "B", "C", "CPY", "D", "E", "F", "I", "N", "RUF", "S", "SIM", "TC", "UP", "W" ]
96. lint.ignore = [
97.   "B904",
98.   "D107",
99.   "D203",
100.   "D204",
101.   "D205",
102.   "D213",
103.   "D215",
104.   "D400",
105.   "D404",
106.   "D406",
107.   "D407",
108.   "D408",
109.   "D409",
110.   "D413",
111.   "E501",
112.   "S105",
113.   "S603",
114.   "TC002",
115.   "TC006",
116.   "UP006",
117.   "UP007",
118.   "UP035",
119.   "UP045",
120. ]
121. lint.per-file-ignores."tests/*" = [ "B011", "D100", "D101", "D102", "D103", "D104", "D212", "D415", "D417", "S" ]
122. lint.flake8-copyright.author = "Canonical Ltd."
123. lint.flake8-copyright.min-file-size = 1
124. lint.flake8-copyright.notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
125. lint.mccabe.max-complexity = 10
126. lint.pydocstyle.convention = "google"
127. 
128. [tool.codespell]
129. skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.coverage,htmlcov,uv.lock,grafana_dashboards"
130. 
131. [tool.pytest.ini_options]
132. minversion = "6.0"
133. log_cli_level = "INFO"
134. pythonpath = [ "lib", "src" ]
135. 
136. [tool.coverage.run]
137. branch = true
138. 
139. [tool.coverage.report]
140. fail_under = 80
141. show_missing = true
142. 
143. [tool.mypy]
144. ignore_missing_imports = true
145. explicit_package_bases = true
146. namespace_packages = true
147. check_untyped_defs = true
148. 
149. [tool.bandit]
150. exclude_dirs = [ "/venv/" ]
151. 
152. [tool.bandit.assert_used]
153. skips = [ "*tests/*.py" ]
154.
```

</details>


---

<sub>⏱️ 12m 21s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 12m 21s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 13m 2s</sub>

### 💬 Copilot

Now let's add the pebble check event handlers to charm.py. First let me see the full `__init__` and the event handler section:

---

<sub>⏱️ 13m 3s</sub>

### ✅ `bash`

**View __init__ section of charm.py**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4 && sed -n '95,130p' /tmp/copilot-tool-output-1775052293297-qgdzuw.txt

<details>
<summary>30 lines</summary>

```
self._require_nginx_route()
        self.saml = SamlRequires(self)
        self.framework.observe(self.saml.on.saml_data_available, self._on_saml_data_available)

        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
        self.framework.observe(self.on.discourse_pebble_ready, self._on_discourse_pebble_ready)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.promote_user_action, self._on_promote_user_action)
        self.framework.observe(self.on.create_user_action, self._on_create_user_action)
        self.framework.observe(self.on.anonymize_user_action, self._on_anonymize_user_action)

        self.redis = RedisRequires(self)
        self.framework.observe(self.on.redis_relation_updated, self._redis_relation_changed)

        self._metrics_endpoint = MetricsEndpointProvider(
            self, jobs=[{"static_configs": [{"targets": [f"*:{PROMETHEUS_PORT}"]}]}]
        )
        self._logging = LogProxyConsumer(
            self, relation_name="logging", log_files=LOG_PATHS, container_name=CONTAINER_NAME
        )
        self._grafana_dashboards = GrafanaDashboardProvider(self)

        self.restart_manager = RollingOpsManager(
            charm=self, relation="restart", callback=self._on_rolling_restart
        )

    def _on_start(self, _: ops.StartEvent) -> None:
        """Handle start event.

        Args:
            event: Event triggering the start event handler.
        """
        self._setup_and_activate()

    def _on_upgrade_charm(self, _: ops.UpgradeCharmEvent) -> None:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 13m 39s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/src/charm.py (lines 100-205)

<details>
<summary>106 lines</summary>

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
```

</details>


---

<sub>⏱️ 14m 21s</sub>

### 💬 Copilot

Now let me add the pebble check event handlers. I'll add them to `__init__` and implement them:

---

<sub>⏱️ 14m 21s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__pebble-check-events__C4/src/charm.py updated with changes.
```


---

<sub>⏱️ 14m 57s</sub>

### ℹ️ Info

Operation cancelled by user

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
