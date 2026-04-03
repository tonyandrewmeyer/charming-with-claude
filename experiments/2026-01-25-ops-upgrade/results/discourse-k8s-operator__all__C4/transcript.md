# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `1649aa7e-b29e-4e58-8659-edfab0e39ef9`  
> - **Started:** 4/2/2026, 2:02:43 AM  
> - **Duration:** 14m 57s  
> - **Exported:** 4/2/2026, 2:17:41 AM  

---

<sub>⏱️ 5s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 16s</sub>

### ✅ `bash`

**Check current ops version**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && cat pyproject.toml | grep -A5 ops && echo "---" && cat uv.lock | grep -A3 "name = \"ops\""

<details>
<summary>45 lines</summary>

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
    { name = "ops" },
    { name = "pydantic" },
    { name = "pyyaml" },
    { name = "tenacity", version = "9.0.0", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
--
    { name = "ops" },
    { name = "pydantic" },
]

--
    { name = "ops", extra = ["testing"] },
    { name = "pytest", version = "8.3.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pytest", version = "8.4.2", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version == '3.9.*'" },
    { name = "pytest", version = "9.0.1", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.10'" },
--
    { name = "ops", specifier = "==2.23.2" },
    { name = "pydantic", specifier = "==2.10.6" },
]

--
    { name = "ops", extras = ["testing"] },
    { name = "pytest" },
]

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `bash`

**Check available ops versions**

$ pip index versions ops 2>/dev/null | head -5 || pip install ops --dry-run 2>&1 | head -10

```
ops (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 2.20.0, 2.19.4, 2.19.0, 2.18.1, 2.18.0, 2.17.1, 2.17.0, 2.16.1, 2.16.0, 2.15.0, 2.14.1, 2.14.0, 2.13.0, 2.12.0, 2.11.0, 2.10.0, 2.9.0, 2.8.0, 2.7.0, 2.6.0, 2.5.1, 2.5.0, 2.4.1, 2.4.0, 2.3.0, 2.2.0, 2.1.1, 2.1.0, 2.0.0, 1.5.5, 1.5.4, 1.5.3, 1.5.2, 1.5.1, 1.5.0, 1.4.0, 1.3.0, 1.2.0, 1.1.0, 1.0.1, 1.0.0, 0.10.0, 0.9.0, 0.8.0, 0.7.0, 0.6.1, 0.6.0, 0.4.7, 0.4.6, 0.4.5, 0.4.4, 0.4.3, 0.4.2, 0.2.1, 0.2.0, 0.1.0
  INSTALLED: 3.7.0
  LATEST:    3.7.0
<exited with exit code 0>
```


---

<sub>⏱️ 24s</sub>

### ✅ `bash`

**Check ops-scenario and ops-tracing versions**

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

<sub>⏱️ 23s</sub>

### ✅ `bash`

**Check current ops-scenario and ops-tracing versions**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && cat uv.lock | grep -E "name = \"ops-(scenario|tracing)\"" -A 3

<details>
<summary>8 lines</summary>

```
{ name = "ops-scenario" },
]

[[package]]
name = "ops-scenario"
version = "7.23.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 34s</sub>

### ✅ `bash`

**Check if ops-tracing is used**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && grep -r "ops.tracing\|ops-tracing\|tracing" pyproject.toml tox.toml charmcraft.yaml 2>/dev/null | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 34s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src

<details>
<summary>7 lines</summary>

```
charm.py
constants.py
database.py
grafana_dashboards
loki_alert_rules
oauth_observer.py
prometheus_alert_rules
```

</details>


---

<sub>⏱️ 43s</sub>

### ✅ `bash`

**List Python files and lib directory**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && find . -name "*.py" | head -30 && echo "---" && ls lib/

<details>
<summary>32 lines</summary>

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
./tests/integration/test_oauth.py
./tests/integration/__init__.py
./tests/integration/test_saml.py
./tests/unit/conftest.py
./tests/unit/test_charm.py
./tests/unit_harness/helpers.py
./tests/unit_harness/test_charm.py
./tests/unit_harness/__init__.py
./tests/__init__.py
---
charms
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

<sub>⏱️ 53s</sub>

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

<sub>⏱️ 1m 2s</sub>

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

<sub>⏱️ 1m 25s</sub>

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

<sub>⏱️ 1m 25s</sub>

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

<sub>⏱️ 1m 46s</sub>

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

<sub>⏱️ 1m 46s</sub>

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

<sub>⏱️ 2m 23s</sub>

### 💬 Copilot

Now let me read the charm code and tests to understand what needs to change:

---

<sub>⏱️ 2m 23s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py

```
File too large to read at once (36.0 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


---

<sub>⏱️ 2m 23s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit/test_charm.py.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit/test_charm.py

<details>
<summary>234 lines</summary>

```
1. # Copyright 2026 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Discourse K8s operator charm unit tests."""
5. 
6. import pytest
7. from ops import testing
8. from ops.model import ActiveStatus, BlockedStatus
9. 
10. from charm import (
11.     CONTAINER_NAME,
12.     INVALID_CORS_MESSAGE,
13.     OAUTH_RELATION_NAME,
14.     SERVICE_NAME,
15.     DiscourseCharm,
16. )
17. 
18. 
19. @pytest.mark.parametrize(
20.     "config, expected_origin, expected_status",
21.     [
22.         pytest.param(
23.             {
24.                 "cors_origin": "*",
25.                 "augment_cors_origin": True,
26.                 "external_hostname": "example.com",
27.                 "force_https": True,
28.                 "s3_cdn_url": "https://cdn.test",
29.             },
30.             "*",
31.             ActiveStatus(),
32.             id="Wildcard disables augmentation",
33.         ),
34.         pytest.param(
35.             {
36.                 "cors_origin": "",
37.                 "augment_cors_origin": False,
38.                 "external_hostname": "example.com",
39.                 "force_https": True,
40.                 "s3_cdn_url": "https://cdn.test",
41.             },
42.             "*",
43.             BlockedStatus(INVALID_CORS_MESSAGE),
44.             id="Raise error when invalid CORS config",
45.         ),
46.         pytest.param(
47.             {
48.                 "cors_origin": "",
49.                 "augment_cors_origin": True,
50.                 "external_hostname": "example.com",
51.                 "force_https": True,
52.                 "s3_cdn_url": "",
53.             },
54.             "https://example.com",
55.             ActiveStatus(),
56.             id="Augment only with external_hostname (HTTPS)",
57.         ),
58.         pytest.param(
59.             {
60.                 "cors_origin": "",
61.                 "augment_cors_origin": True,
62.                 "external_hostname": "",
63.                 "force_https": True,
64.                 "s3_cdn_url": "",
65.             },
66.             "https://discourse-k8s",
67.             ActiveStatus(),
68.             id="Augment with external_hostname not explicitly defined",
69.         ),
70.         pytest.param(
71.             {
72.                 "cors_origin": "",
73.                 "augment_cors_origin": True,
74.                 "external_hostname": "example.com",
75.                 "force_https": False,
76.                 "s3_cdn_url": "https://cdn.test",
77.             },
78.             "http://example.com,https://cdn.test",
79.             ActiveStatus(),
80.             id="Augment with both external_hostname (HTTP) and s3_cdn_url",
81.         ),
82.         pytest.param(
83.             {
84.                 "cors_origin": "https://custom.origin",
85.                 "augment_cors_origin": False,
86.                 "external_hostname": "example.com",
87.                 "force_https": True,
88.                 "s3_cdn_url": "https://cdn.test",
89.             },
90.             "https://custom.origin",
91.             ActiveStatus(),
92.             id="User-defined cors_origin, no augmentation",
93.         ),
94.         pytest.param(
95.             {
96.                 "cors_origin": "https://custom.origin",
97.                 "augment_cors_origin": True,
98.                 "external_hostname": "example.com",
99.                 "force_https": True,
100.                 "s3_cdn_url": "https://cdn.test",
101.             },
102.             "https://cdn.test,https://custom.origin,https://example.com",
103.             ActiveStatus(),
104.             id="User-defined cors_origin with augmentation enabled",
105.         ),
106.         pytest.param(
107.             {
108.                 "cors_origin": "https://foo.com, https://bar.com",
109.                 "augment_cors_origin": True,
110.                 "external_hostname": "example.com",
111.                 "force_https": False,
112.                 "s3_cdn_url": "https://cdn.test",
113.             },
114.             "http://example.com,https://bar.com,https://cdn.test,https://foo.com",
115.             ActiveStatus(),
116.             id="Multiple user-defined cors_origins with augmentation",
117.         ),
118.         pytest.param(
119.             {
120.                 "cors_origin": " https://foo.com , https://foo.com ",
121.                 "augment_cors_origin": True,
122.                 "external_hostname": "foo.com",
123.                 "force_https": True,
124.                 "s3_cdn_url": "https://foo.com",
125.             },
126.             "https://foo.com",
127.             ActiveStatus(),
128.             id="Duplicated origins across cors_origin and augmentation",
129.         ),
130.     ],
131. )
132. def test_get_cors_origin_behavior(config, expected_origin, expected_status, base_state):
133.     """
134.     arrange: deploy charm with CORS-related config
135.     act: configure charm with varying CORS inputs
136.     assert: DISCOURSE_CORS_ORIGIN matches expected result
137.     """
138.     ctx = testing.Context(DiscourseCharm)
139. 
140.     base_state["config"] = config
141. 
142.     state_in = testing.State(**base_state)
143.     container = state_in.get_container(CONTAINER_NAME)
144. 
145.     state_out = ctx.run(ctx.on.pebble_ready(container), state_in)
146.     plan_out = state_out.get_container(container.name).plan
147. 
148.     assert state_out.unit_status == expected_status
149.     if expected_status == ActiveStatus():  # plan is empty when in BlockedStatus
150.         assert (
151.             plan_out.services[SERVICE_NAME].environment["DISCOURSE_CORS_ORIGIN"] == expected_origin
152.         )
153. 
154. 
155. @pytest.mark.parametrize(
156.     "config, expected_status",
157.     [
158.         pytest.param(
159.             {"external_hostname": "discourse.example.com", "force_https": True},
160.             ActiveStatus(),
161.             id="Valid config",
162.         ),
163.         pytest.param(
164.             {"external_hostname": "discourse.example.com", "force_https": False},
165.             BlockedStatus(
166.                 "An oauth relation cannot be established without 'force_https' being true"
167.             ),
168.             id="Missing force_https",
169.         ),
170.         pytest.param(
171.             {"force_https": True},
172.             BlockedStatus("Invalid OAuth client config, check the logs for more info."),
173.             id="external_hostname not set",
174.         ),
175.     ],
176. )
177. def test_oauth_integration(base_state, config, expected_status):
178.     """
179.     arrange: deploy charm and add oauth relation with provider data.
180.     act: trigger pebble ready or relation changed.
181.     assert: charm configures OIDC environment variables in the container.
182.     """
183.     ctx = testing.Context(DiscourseCharm)
184. 
185.     # Define the relation
186.     oauth_relation = testing.Relation(
187.         endpoint=OAUTH_RELATION_NAME,
188.         interface="oauth",
189.         remote_app_data={
190.             "issuer_url": "https://auth.example.com",
191.             "authorization_endpoint": "https://auth.example.com/auth",
192.             "token_endpoint": "https://auth.example.com/token",  # nosec B105
193.             "introspection_endpoint": "https://auth.example.com/introspect",
194.             "userinfo_endpoint": "https://auth.example.com/userinfo",
195.             "jwks_endpoint": "https://auth.example.com/jwks",
196.             "scope": "openid email",
197.             "client_id": "my-client-id",
198.             "client_secret": "my-super-secret",  # nosec B105
199.         },
200.     )
201. 
202.     base_state["relations"].append(oauth_relation)
203.     base_state["config"] = config
204. 
205.     state_in = testing.State(**base_state)
206. 
207.     # Run the charm
208.     state_out = ctx.run(ctx.on.relation_joined(oauth_relation), state_in)
209. 
210.     assert state_out.unit_status == expected_status
211.     if expected_status == ActiveStatus():
212.         # Check if OIDC env vars are set in the plan
213.         plan = state_out.get_container(CONTAINER_NAME).plan
214.         env = plan.services[SERVICE_NAME].environment
215. 
216.         assert env["DISCOURSE_OPENID_CONNECT_ENABLED"] == "true"
217.         assert (
218.             env["DISCOURSE_OPENID_CONNECT_DISCOVERY_DOCUMENT"]
219.             == "https://auth.example.com/.well-known/openid-configuration"
220.         )
221.         assert env["DISCOURSE_OPENID_CONNECT_CLIENT_ID"] == "my-client-id"
222.         assert env["DISCOURSE_OPENID_CONNECT_CLIENT_SECRET"] == "my-super-secret"
223.         assert env["DISCOURSE_OPENID_CONNECT_AUTHORIZE_SCOPE"] == "openid email"
224. 
225.         # Also check if the charm sent its client config
226.         relation = next(r for r in state_out.relations if r.id == oauth_relation.id)
227.         assert (
228.             relation.local_app_data["redirect_uri"]
229.             == "https://discourse.example.com/auth/oidc/callback"
230.         )
231.         assert relation.local_app_data["scope"] == "openid email"
232.         assert relation.local_app_data["grant_types"] == '["authorization_code"]'
233.         assert relation.local_app_data["token_endpoint_auth_method"] == "client_secret_basic"
234.
```

</details>


---

<sub>⏱️ 2m 34s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit/conftest.py

<details>
<summary>85 lines</summary>

```
1. # Copyright 2026 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Discourse K8s operator charm fixtures."""
5. 
6. import pytest
7. from ops import testing
8. 
9. from charm import CONTAINER_NAME
10. from constants import DATABASE_NAME
11. 
12. 
13. @pytest.fixture(name="base_state")
14. def base_state_fixture(discourse_container, postgresql_relation, redis_relation):
15.     input_state = {
16.         "leader": True,
17.         "config": {},
18.         "containers": {discourse_container},
19.         "relations": [postgresql_relation, redis_relation],
20.     }
21.     yield input_state
22. 
23. 
24. @pytest.fixture(name="discourse_container")
25. def discourse_container_fixture():
26.     """Discourse container fixture."""
27.     yield testing.Container(
28.         name=CONTAINER_NAME,
29.         can_connect=True,
30.         execs=[
31.             testing.Exec(
32.                 command_prefix=[
33.                     "/srv/discourse/app/bin/bundle",
34.                     "exec",
35.                     "rake",
36.                     "--trace",
37.                     "db:migrate",
38.                 ],
39.                 return_code=0,
40.                 stdout="Migration successful\n",
41.                 stderr="",
42.             ),
43.             testing.Exec(
44.                 command_prefix=["/srv/discourse/app/bin/rails", "runner"],
45.                 return_code=0,
46.                 stdout="successful\n",
47.                 stderr="",
48.             ),
49.         ],
50.     )  # type: ignore[call-arg]
51. 
52. 
53. @pytest.fixture(name="postgresql_relation")
54. def postgresql_relation_fixture():
55.     """Postgresql relation fixture."""
56.     relation_data = {
57.         "database": DATABASE_NAME,
58.         "endpoints": "dbhost:5432,dbhost-2:5432",
59.         "password": "somepasswd",  # nosec
60.         "username": "someuser",
61.     }
62.     yield testing.Relation(
63.         endpoint="database",
64.         interface="postgresql_client",
65.         remote_app_data=relation_data,
66.     )
67. 
68. 
69. @pytest.fixture(name="redis_relation")
70. def redis_relation_fixture():
71.     """Redis relation fixture."""
72.     relation_data = {
73.         0: {
74.             "hostname": "redis-host",
75.             "port": "1010",
76.         },
77.     }
78.     yield testing.Relation(
79.         endpoint="redis",
80.         interface="redis",
81.         remote_app_name="redis",
82.         remote_units_data=relation_data,
83.         remote_app_data={"leader-host": "redis-host"},
84.     )
85.
```

</details>


---

<sub>⏱️ 2m 34s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py.**

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

<sub>⏱️ 3m 1s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py.**

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

<sub>⏱️ 3m 1s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/pyproject.toml

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

<sub>⏱️ 3m 34s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/test_charm.py.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/test_charm.py

```
File too large to read at once (32.0 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


---

<sub>⏱️ 3m 34s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tox.toml.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tox.toml

<details>
<summary>133 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. no_package = true
5. skip_missing_interpreters = true
6. env_list = [ "lint", "unit", "static", "coverage-report" ]
7. 
8. requires = [ "tox>=4.22", "tox-uv>=1.29.0" ]
9. 
10. [env_run_base]
11. pass_env = [
12.   "PYTHONPATH",
13.   "CHARM_BUILD_DIR",
14.   "MODEL_SETTINGS",
15.   "CHARM_FILE",
16.   "ROCK_IMAGE",
17.   "OCI_RESOURCE_NAME",
18.   "JUJU_DEPLOY_BASE",
19.   "TOX_CMD_PREFIX",
20. ]
21. runner = "uv-venv-lock-runner"
22. 
23. [env_run_base.set_env]
24. PYTHONPATH = "{tox_root}{:}{tox_root}{/}lib{:}{tox_root}{/}{[vars]src_path}"
25. PYTHONBREAKPOINT = "ipdb.set_trace"
26. PY_COLORS = "1"
27. 
28. [env.fmt]
29. description = "Apply coding style standards to code"
30. commands = [
31.   [ "ruff", "check", "--fix", "--select", "I", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
32.   [ "ruff", "format", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
33. ]
34. dependency_groups = [ "fmt" ]
35. 
36. [env.lint]
37. description = "Check code against coding style standards"
38. commands = [
39.   [ "codespell", "{tox_root}" ],
40.   [ "ruff", "format", "--check", "--diff", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
41.   [ "ruff", "check", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
42.   [ "mypy", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
43. ]
44. dependency_groups = [ "lint" ]
45. 
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
71. [env.static]
72. description = "Run static analysis tests"
73. commands = [ [ "bandit", "-c", "{tox_root}{/}pyproject.toml", "-r", "{[vars]src_path}", "{[vars]tst_path}" ] ]
74. dependency_groups = [ "static" ]
75. 
76. [env.integration]
77. description = "Run integration tests"
78. commands = [
79.   [
80.     "pytest",
81.     "-v",
82.     "--tb",
83.     "native",
84.     "--ignore={[vars]tst_path}{/}unit",
85.     "--ignore={[vars]tst_path}{/}unit_harness",
86.     "--log-cli-level=INFO",
87.     "-s",
88.     { replace = "posargs", extend = true },
89.   ],
90. ]
91. dependency_groups = [ "integration" ]
92. 
93. [env.lint-docs]
94. description = "Check documentation links"
95. package = "skip"
96. runner = "uv-venv-runner"
97. 
98. allowlist_externals = [ "curl", "tar", "chmod", "echo", "sh", "{envtmpdir}{/}lychee" ]
99. 
100. commands_pre = [
101.   [ "echo", "Download URL: {[vars]lychee_download_url}" ],
102.   [ "curl", "-L", "{[vars]lychee_download_url}", "-o", "{envtmpdir}{/}lychee.tar.gz" ],
103.   [ "sh", "-c", "echo '{[vars]lychee_sha256}  {envtmpdir}{/}lychee.tar.gz' | sha256sum -c -" ],
104.   [ "tar", "-xzf", "{envtmpdir}{/}lychee.tar.gz", "-C", "{envtmpdir}" ],
105.   [ "chmod", "+x", "{envtmpdir}{/}lychee" ],
106. ]
107. commands = [ [ "{envtmpdir}{/}lychee", "--max-concurrency", "2", "README.md", "{[vars]docs_path}" ] ]
108. 
109. [env.lint-fix]
110. description = "Apply coding style standards to code"
111. commands = [
112.   [
113.     "ruff",
114.     "check",
115.     "--fix",
116.     "--fix-only",
117.     { replace = "ref", of = [
118.       "vars",
119.       "all_path",
120.     ], extend = true },
121.   ],
122. ]
123. dependency_groups = [ "lint" ]
124. 
125. [vars]
126. src_path = "src"
127. tst_path = "tests"
128. docs_path = "docs"
129. all_path = [ "src", "tests" ]
130. lychee_version = "0.19.1"
131. lychee_sha256 = "537bcfbb0f3bf997f4cbdab259cc5500f2804b69614140ac3edebb4de94b3574"
132. lychee_download_url = "https://github.com/lycheeverse/lychee/releases/download/lychee-v{[vars]lychee_version}/lychee-x86_64-unknown-linux-gnu.tar.gz"
133.
```

</details>


---

<sub>⏱️ 4m 20s</sub>

### ✅ `bash`

**Check harness tests**

$ head -60 /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/test_charm.py && echo "---" && grep -n "Harness\|harness\|from ops" /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/test_charm.py | head -20

<details>
<summary>73 lines</summary>

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
---
14:from ops.model import ActiveStatus, BlockedStatus, WaitingStatus
18:from tests.unit_harness import helpers
50:    harness = helpers.start_harness(
53:    harness.container_pebble_ready("discourse")
54:    assert harness.model.unit.status == status
63:    harness = helpers.start_harness(with_postgres=False, with_redis=False, with_ingress=True)
64:    assert harness.model.unit.status == WaitingStatus("Waiting for database relation")
73:    harness = helpers.start_harness(with_config={"force_saml_login": True})
74:    assert harness.model.unit.status == BlockedStatus(
85:    harness = helpers.start_harness(with_config={"saml_sync_groups": "group1"})
86:    assert harness.model.unit.status == BlockedStatus(
97:    harness = helpers.start_harness(with_config={"force_https": False}, saml_fields=(True, "", ""))
98:    harness.charm._is_config_valid()
99:    assert harness.model.unit.status == BlockedStatus(
110:    harness = helpers.start_harness(with_config={"cors_origin": ""})
111:    assert harness.charm._database.get_relation_data() is not None, (
114:    assert harness.charm._database.get_relation_data().get("POSTGRES_DB") == DATABASE_NAME, (
125:    harness = helpers.start_harness(with_config={"throttle_level": "Scream"})
126:    assert isinstance(harness.model.unit.status, BlockedStatus)
127:    assert "none permissive strict" in harness.model.unit.status.message
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 20s</sub>

### ✅ `bash`

**Check harness helpers**

$ cat /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/helpers.py

<details>
<summary>127 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""helpers for the unit tests."""

import contextlib
import typing
import unittest.mock

from ops.model import Container
from ops.testing import Harness

from charm import DiscourseCharm

DATABASE_NAME = "discourse"


def start_harness(  # pylint: disable=too-many-arguments
    *,
    saml_fields: tuple = (False, ""),
    with_postgres: bool = True,
    with_redis: bool = True,
    with_ingress: bool = False,
    with_config: typing.Optional[typing.Dict[str, typing.Any]] = None,
    run_initial_hooks=True,
):
    """Start a harness discourse charm.

    This is also a workaround for the fact that Harness
    doesn't reinitialize the charm as expected.
    Ref: https://github.com/canonical/operator/issues/736

    Args:
        - with_postgres: should a postgres relation be added
        - with_redis: should a redis relation be added
        - with_ingress: should a ingress relation be added
        - with_config: apply some configuration to the charm

    Returns: a ready to use harness instance
    """
    harness = Harness(DiscourseCharm)
    if run_initial_hooks:
        harness.begin_with_initial_hooks()
    else:
        harness.begin()

    # We catch all exec calls to the container by default
    harness.handle_exec("discourse", [], result=0)

    if with_postgres:
        add_postgres_relation(harness)

    if with_redis:
        add_redis_relation(harness)

    if with_ingress:
        _add_ingress_relation(harness)

    if saml_fields[0]:
        _add_saml_relation(harness, saml_fields[1])

    if with_config is not None:
        harness.update_config(with_config)

    return harness


@contextlib.contextmanager
def _patch_setup_completed():
    """Patch filesystem calls in the _is_setup_completed and _set_setup_completed functions."""
    setup_completed = False

    def exists(*_args, **_kwargs):
        return setup_completed

    def push(*_args, **_kwargs):
        nonlocal setup_completed
        setup_completed = True

    with unittest.mock.patch.multiple(Container, exists=exists, push=push):
        yield


def add_postgres_relation(harness):
    """Add postgresql relation and relation data to the charm.

    Args:
        - A harness instance

    Returns: the same harness instance with an added relation
    """
    relation_data = {
        "database": DATABASE_NAME,
        "endpoints": "dbhost:5432,dbhost-2:5432",
        "password": "somepasswd",  # nosec
        "username": "someuser",
    }

    harness.db_relation_id = harness.add_relation("database", "postgresql")
    harness.add_relation_unit(harness.db_relation_id, "postgresql/0")
    harness.update_relation_data(
        harness.db_relation_id,
        "postgresql",
        relation_data,
    )


def add_redis_relation(harness, relation_data=None, app_data=None):
    """Add redis relation and relation data to the charm.

    Args:
        - A harness instance

    Returns: the same harness instance with an added relation
    """
    redis_relation_id = harness.add_relation(
        "redis",
        "redis",
        app_data={"leader-host": "redis-host"} if app_data is None else app_data,
    )
    harness.add_relation_unit(redis_relation_id, "redis/0")
    harness.update_relation_data(
        redis_relation_id,
        "redis/0",
        {"hostname": "redis-host", "port": "1010"} if relation_data is None else relation_data,
    )


def _add_ingress_relation(harness):
    """Add ingress relation and relation data to the charm.

    Args:
        - A harness instance

    Returns: the same harness instance with an added relation
    """
    nginx_route_relation_id = harness.add_relation("nginx-route", "ingress")
    harness.add_relation_unit(nginx_route_relation_id, "ingress/0")


def _add_saml_relation(harness, saml_target):
    """Add ingress relation and relation data to the charm.

    Args:
        - A harness instance

    Returns: the same harness instance with an added relation
    """
    harness.set_leader(True)
    saml_relation_id = harness.add_relation("saml", "saml-integrator")
    harness.add_relation_unit(saml_relation_id, "saml-integrator/0")
    harness.disable_hooks()
    binding = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    harness.update_relation_data(
        relation_id=saml_relation_id,
        app_or_unit="saml-integrator",
        key_values={
            "entity_id": saml_target,
            "metadata_url": f"{saml_target}/saml/metadata",
            "x509certs": "test",
            "single_sign_on_service_redirect_url": f"{saml_target}/+saml",
            "single_sign_on_service_redirect_binding": binding,
        },
    )
    harness.enable_hooks()
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 48s</sub>

### ✅ `bash`

**Check for deprecated features in tests**

$ grep -n "charm_spec\|from ops.testing\|testing.Context\|Harness" /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit/test_charm.py /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit/conftest.py 2>/dev/null

```
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit/test_charm.py:138:    ctx = testing.Context(DiscourseCharm)
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit/test_charm.py:183:    ctx = testing.Context(DiscourseCharm)
<exited with exit code 0>
```


---

<sub>⏱️ 5m 47s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/charmcraft.yaml.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/charmcraft.yaml

<details>
<summary>22 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. # Learn more about charmcraft.yaml configuration at:
4. # https://juju.is/docs/sdk/charmcraft-config
5. type: "charm"
6. bases:
7.   - build-on:
8.     - name: "ubuntu"
9.       channel: "20.04"
10.     run-on:
11.     - name: "ubuntu"
12.       channel: "20.04"
13. parts:
14.   charm:
15.     source: .
16.     plugin: uv
17.     build-snaps:
18.     - astral-uv
19. charm-libs:
20.   - lib: hydra.oauth
21.     version: "0"
22.
```

</details>


---

<sub>⏱️ 5m 54s</sub>

### ✅ `bash`

**Check metadata.yaml**

$ cat /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/metadata.yaml

<details>
<summary>68 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
name: discourse-k8s
display-name: Discourse
summary: Discourse is the modern forum for your community.
description: |
  A [Juju](https://juju.is/) [charm](https://juju.is/docs/olm/charmed-operators)
  deploying and managing [Discourse](https://www.discourse.org/) on Kubernetes.
  Discourse is the 100% open source discussion platform. Use it as a mailing list,
  discussion forum or long-form chat room.

  This charm simplifies initial deployment and "day N" operations of Discourse
  on Kubernetes, such as scaling the number of instances, integration with SSO,
  access to S3 for redundant file storage and more. It allows for deployment on
  many different Kubernetes platforms, from [MicroK8s](https://microk8s.io) or
  [Charmed Kubernetes](https://ubuntu.com/kubernetes) and public cloud Kubernetes
  offerings.

  As such, the charm makes it easy for those looking to take control of their own
  discussion platform whilst keeping operations simple, and gives them the
  freedom to deploy on the Kubernetes platform of their choice.

  For DevOps or SRE teams this charm will make operating Discourse simple and
  straightforward through Juju's clean interface. It will allow easy deployment
  into multiple environments for testing of changes, and supports scaling out for
  enterprise deployments.
docs: https://discourse.charmhub.io/t/discourse-documentation-overview/3773
maintainers:
  - https://launchpad.net/~canonical-is-devops
issues: https://github.com/canonical/discourse-k8s-operator/issues
source: https://github.com/canonical/discourse-k8s-operator
tags:
  - applications
  - forum

provides:
  metrics-endpoint:
    interface: prometheus_scrape
  grafana-dashboard:
    interface: grafana_dashboard

requires:
  redis:
    interface: redis
    limit: 1
  database:
    interface: postgresql_client
    limit: 1
  nginx-route:
    interface: nginx-route
    limit: 1
  logging:
    interface: loki_push_api
  oauth:
    interface: oauth
    limit: 1
  saml:
    interface: saml
    limit: 1
    optional: true
assumes:
  - k8s-api

peers:
  restart:
    interface: rolling_op

containers:
  discourse:
    resource: discourse-image

resources:
  discourse-image:
    type: oci-image
    description: OCI image for discourse
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 18s</sub>

### 💬 Copilot

Now I have a comprehensive understanding. Let me check for Python version-specific code and look at the ops-scenario/ops-tracing changes:

---

<sub>⏱️ 6m 18s</sub>

### ✅ `bash`

**Check for pre-3.10 typing syntax**

$ grep -rn "Optional\[" /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/ && echo "---" && grep -n "typing.Dict\|typing.List\|typing.Optional\|typing.Tuple\|typing.Set\|Union\[" /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/ /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/ -r

<details>
<summary>12 lines</summary>

```
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py:538:        self, current_plan: Plan, s3info: typing.Optional[S3Info]
---
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/constants.py:11:THROTTLE_LEVELS: typing.Dict = defaultdict(dict)
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/oauth_observer.py:95:    def get_oidc_env(self) -> typing.Dict[str, typing.Any]:
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py:334:    def _get_saml_config(self) -> typing.Dict[str, typing.Any]:
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py:378:    def _get_s3_env(self) -> typing.Dict[str, typing.Any]:
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py:407:    def _get_redis_relation_data(self) -> typing.Tuple[str, int]:
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py:438:    def _create_discourse_environment_settings(self) -> typing.Dict[str, str]:
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py:538:        self, current_plan: Plan, s3info: typing.Optional[S3Info]
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/database.py:34:    def get_relation_data(self) -> typing.Dict[str, str]:
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/helpers.py:24:    with_config: typing.Optional[typing.Dict[str, typing.Any]] = None,
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 19s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/blob/main/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://github.com/canonical/operator/blob/main/CHANGES.md"
}
```

</details>

<details>
<summary>301 lines</summary>

```
Contents of https://github.com/canonical/operator/blob/main/CHANGES.md:
## 3.7.0 - 30 March 2026

[](#370---30-march-2026)

## Features

[](#features)

*   Enable interactive debugging via `breakpoint` in testing (#2363)
*   ops.testing autoload support for charmcraft extensions (#2367)
*   Allow testing.State.get\_relation to accept relation objects (#2359)
*   Support charmcraft.yaml format as meta for testing.Context (#2296)

## Fixes

[](#fixes)

*   Correct type annotation for StorageMeta.properties (#2348)
*   Move the testing.Container compatibility import so that mypy style checkers understand it (#2343)
*   Hold only copies of user provided meta/config/actions in testing.Context (#2349)
*   Deep-copy layer objects during testing.State plan rendering (#2380)
*   Return copies from testing.State secret\_get and action\_get (#2379)
*   Use timezone-aware datetimes in expiry calculation (#2378)
*   Warn before clearing non-empty container in testing (#2365)

## Documentation

[](#documentation)

*   Replace links to juju.is by canonical.com/juju (#2368)
*   Refactor homepage to better put Ops in context (#2370)
*   Add pytest-operator migration guide from Jubilant docs (#2381)
*   Add a tip about AI help in the Jubilant migration guide (#2382)
*   Mention jhack scenario snapshot (#2351)
*   Update integration testing how-to guide (#2390)
*   Explain K8s charms briefly at the start of the tutorial (#2392)
*   Juju secrets identifier is now an opaque string (#2387)

## Tests

[](#tests)

*   Extend the type checking of the ops-scenario tests (#2230)

## CI

[](#ci)

*   Run ruff check --fix in tox -e format (#2369)
*   Check example charms with mypy in CI (#2360)
*   Update the list of published charms in the compatibility tests (#2384)
*   Adjust minimum Python version in broad charm compatibility tests (#2317)

## 3.6.0 - 26 February 2026

[](#360---26-february-2026)

## Features

[](#features-1)

*   Bump default Juju version in `ops.testing.Context` to 3.6.14 (#2316)

## Fixes

[](#fixes-1)

*   Correct the `Model.get_binding()` return type (#2329)
*   Only show executable in `ExecError.__str__`, not full command line (#2336)
*   Support Pydantic `MISSING` sentinel in `ops.Relation.save` (#2306)

## Documentation

[](#documentation-1)

*   Add how-to subcategory for managing containers (#2309)
*   Remove 2.19 version in docs, tweak ops.testing title (#2332)
*   Use "true" and "false" consistently in the reference documentation (#2330)
*   Add CLI args as another place to not put sensitive data (#2334)
*   Fix remote unit kwarg in testing example (#2342)
*   Clarify that secret labels are not names (#2337)

## Tests

[](#tests-1)

*   Set `SCENARIO_BARE_CHARM_ERRORS=true` in Ops tests that care (#2314)

## CI

[](#ci-1)

*   Fix releasing on branches with no `versions.md` doc (#2323)

## 3.5.2 - 11 February 2026

[](#352---11-february-2026)

## Fixes

[](#fixes-2)

*   Make testing.CheckInfo level arg type match pebble.CheckInfo.level (#2274)
*   Make testing consistency check aware that `credential-get` is available on k8s in newer Juju (#2307)
*   Drop unused `setuptools_scm` build dependency (#2310)

## Documentation

[](#documentation-2)

*   Update Pebble version in Juju 3.6 (#2295)
*   Refresh K8s tutorial to use Concierge and uv-based Charmcraft profile (#2285)
*   Add missing "How to" in page titles (#2289)
*   Fix and improve observability part of K8s tutorial (#2305)

## 3.5.1 - 28 January 2026

[](#351---28-january-2026)

## Fixes

[](#fixes-3)

*   Use `parse_rfc3339` for datetime parsing to support Juju 4 (#2264)
*   Correct the value of `additional_properties` in the action meta in Juju 4 (#2250)
*   Prevent `KeyError` on `auth-type` when creating `CloudCredential` object (#2268)
*   `_checks_action` should return empty list when there are no changes (#2270)

## Documentation

[](#documentation-3)

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

[](#tests-2)

*   Remove unnecessary test module (#2247)

## CI

[](#ci-2)

*   Replace git reference injection with wheel artifacts in charm test workflows (#2252)
*   Explicitly provide the charmcraft repo location in CI (#2277)
*   Remove outdated custom signature generation (#2280)

## 3.5.0 - 18 December 2025

[](#350---18-december-2025)

## Features

[](#features-2)

*   Env var to control exception wrapping in tests (#2142)
*   Deprecate testing.Context.charm\_spec (#2219)

## Documentation

[](#documentation-4)

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

[](#tests-3)

*   Don't skip tests if ops\[testing\] isn't installed (#2215)
*   Switch the integration test charms to use the uv plugin (#2218)

## CI

[](#ci-3)

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

[](#features-3)

*   Add a low-level API for the Juju hook commands (#2019)
*   Make PebbleClient file methods also accept pathlib.PurePath (#2097)
*   Log the total number of deferred events (#2161)
*   Allow setting the Juju availability zone and principal unit in the testing Context (#2187)

## Fixes

[](#fixes-4)

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

[](#documentation-5)

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

[](#tests-4)

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

[](#ci-4)

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

[](#features-4)

*   Expose the Juju hook context in ops.JujuContext (#1996)

## Fixes

[](#fixes-5)

*   In testing, separate relation data cache from mock Juju backend (#2052)

## Documentation

[](#documentation-6)

*   Use uv for testing and packing the httpbin charm (#2011)
*   Improve intro to ops.testing reference (#2023)
*   In httpbin charm integration tests, add env var for charm file to deploy (#2018)
*   Update get\_cloud\_spec doc now that credential-get works on K8s (#2031)
*   Note that arbitrary\_types\_allowed is required when ops.Secret is used in a Pydantic class (#2038)
*   Clean up Resources.fetch docstring, add ModelError exception (#2039)
*   Note that the peer databag isn't usable during the install event (#2051)
*   Fix testing code in actions how-to guide (#2054)

## CI

[](#ci-5)

*   Nicer logging output in the release script using rich (#2017)
*   Clean up PYTHONPATH in tox.ini (#2058)

## 3.2.0 - 28 August 2025

[](#320---28-august-2025)

## Features

[](#features-5)

*   Add security event logging (#1905)
*   Surface JUJU\_MACHINE\_ID envvar in testing env (#1961)
*   Add a new log target type opentelemetry (#1937)

## Documentation

[](#documentation-7)

*   Update links and config for switch to documentation.ubuntu.com/ops (#1940)
*   Update the required Python version and note the 2.x documentation site (#1946)
*   Be consistent with recommending self.config (#1947)
*   Use latest styles from starter pack and remove .html extensions (#1951)
*   Remove .html extensions from hardcoded links (#1955)
*   Fix broken URLs in sitemap (#1956)
*   Add related doc links to homepage (#1959)
*   Use classes from ops instead of ops. (#1968)
*   Fix unstyled error pages (#1969)
*   Add Google Analyics integration and cookie consent banner (#1971)
*   Refresh docs homepage with more context about Ops (#1964)
*   Update link to Charmlibs docs (#1985)
*   Remove unnecessary pages from sitemap (#1979)
*   Update the httpbin example charm to Jubilant (#1987)
*   Update the Zero to Hero tutorial to Jubilant (#1988)
*   Add model-config best practice note (#1990)
*   Change some best practices to tips (#2001)
*   Add integration test for invalid config in httpbin charm (#2002)
*   Make a `Layer` instead of a `LayerDict` in the httpbin charm (#2003)
*   Update how-to to feature Jubilant (#2000, #2004)
*   Use Charmcraft-style format and lint for example charms, not Ops-style (#2008)
*   Update broken link to HookVars source code (#2006)

## CI

[](#ci-6)

*   Fixes for the SBOM and security scan workflow, and trigger it on publishing (#1916)
*   Store the charmcraft logs if packing fails (#1936)
*   Install release dependencies for the TIOBE analysis (#1930)
*   Add Juju 4/beta to the smoke test matrix (#1963)
*   Adjust permissions block in publish workflow (#1984)
*   Update actions/checkout to v5 (#1993)
*   Enable doctests (#1991)
*   Ignore juju/4 timeouts (#1998)
*   Remove the token for SBOM and security scan workflow (#2009)
*   Speed up integration test (#1978)

## 3.1.0 - 30 July 2025

[](#310---30-july-2025)

## Features

[](#features-6)

*   Release automation script (#1855)
*   Add app\_name and unit\_id attributes to testing.context (#1920)

## Fixes

[](#fixes-6)

*   If an event ends with \_abort(0) tests should behave as if it ended successfully (#1887)
*   If self.app is not actually set avoid a new crash location (#1897)
*   Only add the remote unit for departed and broken relation events, fix ordering (#1918)
*   Add the remote unit to relation.data but not relation.units (#1925)

## Documentation

[](#documentation-8)

*   Use load\_config in the httpbin example charm (#1852)
*   Update HACKING.md with how to bump `ops` version in Charmcraft profiles (#1872)
*   Change title of docs site (#1890)
*   Use config and action classes in the Kubernetes tutorial (#1891)
*   Reference example charms from K8s tutorial and fix consistency (#1898)
*   Update style guide (#1720)
*   Fix issues in how-to guide for stored state (#1901)
*   Link out to the 12-factor tutorials from the tutorial index page (#1902)
*   Replace broken link in testing explan

<note>Content truncated. Call the fetch tool with a start_index of 15000 to get more content.</note>
```

</details>


---

<sub>⏱️ 6m 49s</sub>

### ✅ `bash`

**Check if Harness is deprecated in ops 3.7**

$ pip show ops 2>/dev/null && python3 -c "import ops.testing; help(ops.testing.Harness)" 2>&1 | head -20

<details>
<summary>30 lines</summary>

```
Name: ops
Version: 3.7.0
Summary: The Python library behind great charms
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
Author-email: 
License: 
Location: /home/ubuntu/.local/lib/python3.12/site-packages
Requires: opentelemetry-api, PyYAML, websocket-client
Required-by: alertmanager-k8s, charmed-service-mesh-helpers, cosl, ops-scenario, ops-tracing
Help on class Harness in module ops._private.harness:

class Harness(typing.Generic)
 |  Harness(charm_cls: 'type[CharmType]', *, meta: 'YAMLStringOrFile | None' = None, actions: 'YAMLStringOrFile | None' = None, config: 'YAMLStringOrFile | None' = None)
 |
 |  This class represents a way to build up the model that will drive a test suite.
 |
 |  The model created is from the viewpoint of the charm that is being tested.
 |
 |  Always call ``harness.cleanup()`` after creating a :class:`Harness`::
 |
 |      @pytest.fixture()
 |      def harness():
 |          harness = Harness(MyCharm)
 |          yield harness
 |          harness.cleanup()
 |
 |  Below is an example test using :meth:`begin_with_initial_hooks` that ensures
 |  the charm responds correctly to config changes (the parameter ``harness`` in the
 |  test function is a pytest fixture that does setup/teardown, see :class:`Harness`)::
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 48s</sub>

### ✅ `bash`

**Check for deprecation warnings from Harness**

$ python3 -c "import warnings; warnings.simplefilter('always'); import ops.testing; h = ops.testing.Harness" 2>&1 | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 7m 17s</sub>

### ✅ `bash`

**Check Container init signature**

$ python3 -c "from ops.testing import Container; help(Container.__init__)" 2>&1 | head -30

```
Help on function __init__ in module scenario.state:

__init__(self, name: 'str', *, can_connect: 'bool' = False, _base_plan: 'Mapping[str, Any]' = <factory>, layers: 'Mapping[str, pebble.Layer]' = <factory>, service_statuses: 'Mapping[str, pebble.ServiceStatus]' = <factory>, mounts: 'Mapping[str, Mount]' = <factory>, execs: 'Iterable[Exec]' = frozenset(), notices: 'Sequence[Notice]' = <factory>, check_infos: 'Iterable[CheckInfo]' = frozenset()) -> None
    Initialize self.  See help(type(self)) for accurate signature.
<exited with exit code 0>
```


---

<sub>⏱️ 8m 16s</sub>

### 💬 Copilot

Now I have enough information. Let me plan and execute the upgrade:

---

<sub>⏱️ 8m 16s</sub>

### ✅ `sql`

**Create upgrade todo list**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create upgrade todo list",
  "query": "INSERT INTO todos (id, title, description) VALUES\n  ('bump-ops-version', 'Bump ops to 3.7.0', 'Update ops==2.23.2 to ops==3.7.0 in pyproject.toml'),\n  ('update-python-version', 'Update Python version requirements', 'Change requires-python from >=3.8 to >=3.10 and remove 3.8/3.9 classifiers (ops 3.0 drops Python 3.8 support)'),\n  ('remove-type-ignore', 'Remove type: ignore[call-arg] in conftest', 'ops 3.7 fix #2343 moves the testing.Container compatibility import so mypy understands it'),\n  ('add-bare-charm-errors', 'Add SCENARIO_BARE_CHARM_ERRORS=true to unit test env', 'ops 3.5 introduced this env var to avoid wrapping exceptions in UncaughtCharmError for cleaner test errors'),\n  ('uv-lock', 'Update uv.lock', 'Run uv lock to regenerate the lockfile with the new ops version'),\n  ('run-tests', 'Run tests to verify', 'Run tox -e unit to verify all tests pass with the new ops version'),\n  ('create-branch', 'Create git branch', 'Create ops-upgrade branch with all changes')"
}
```

</details>

```
7 row(s) inserted. Last inserted row ID: 7.
```


---

<sub>⏱️ 8m 58s</sub>

### ✅ `bash`

**Create upgrade branch**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && git checkout -b ops-upgrade-3.7.0

```
Switched to a new branch 'ops-upgrade-3.7.0'
<exited with exit code 0>
```


---

<sub>⏱️ 10m 16s</sub>

### 💬 Copilot

Now make the changes:

---

<sub>⏱️ 10m 16s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 10m 16s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit/conftest.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit/conftest.py updated with changes.
```


---

<sub>⏱️ 10m 30s</sub>

### 💬 Copilot

Now add `SCENARIO_BARE_CHARM_ERRORS = "true"` to the unit test environment in tox.toml:

---

<sub>⏱️ 10m 30s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tox.toml.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tox.toml

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tox.toml updated with changes.
```


---

<sub>⏱️ 11m 12s</sub>

### 💬 Copilot

Now update the lockfile:

---

<sub>⏱️ 11m 14s</sub>

### ✅ `bash`

**Update uv.lock**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && uv lock 2>&1

<details>
<summary>55 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠹ Resolving dependencies...                                                                                             ⠸ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ allure-pytest-collection-report==0.1.0                                                                                ⠙ saml-test-helper==0.2.0                                                                                               ⠙ cosl==1.6.0                                                                                                           ⠙ jsonschema==4.23.0                                                                                                    ⠙ ops==3.7.0                                                                                                            ⠙ allure-pytest-collection-report==0.1.0                                                                                ⠙ saml-test-helper==0.2.0                                                                                               ⠙ cosl==1.6.0                                                                                                           ⠙ jsonschema==4.23.0                                                                                                    ⠙ ops==3.7.0                                                                                                            ⠙ ops==3.7.0                                                                                                            ⠙ pydantic==2.10.6                                                                                                      ⠹ pydantic==2.10.6                                                                                                      ⠹ jubilant==1.7.0                                                                                                       ⠹ protobuf==5.29.6                                                                                                      ⠸ allure-pytest==2.15.0                                                                                                 ⠸ allure-python-commons==2.15.0                                                                                         ⠸ boto3==1.41.3                                                                                                         ⠸ bs4==0.0.2                                                                                                            ⠸ debugpy==1.8.17                                                                                                       ⠼ pygments==2.19.2                                                                                                      ⠼ botocore==1.41.3                                                                                                      ⠼ jmespath==1.0.1                                                                                                       ⠼ soupsieve==2.8                                                                                                        ⠴ markupsafe==3.0.3                                                                                                     ⠴ backports-datetime-fromisoformat==2.0.3                                                                               ⠴ hvac==2.4.0                                                                                                           ⠴ macaroonbakery==1.3.4                                                                                                 ⠴ paramiko==4.0.0                                                                                                       ⠦ traitlets==5.14.3                                                                                                     ⠦ pymacaroons==0.13.0                                                                                                   ⠦ pynacl==1.6.1                                                                                                         ⠦ pyrfc3339==1.1                                                                                                        ⠧ backports-datetime-fromisoformat==2.0.3                                                                               ⠧ backports-strenum==1.3.1                                                                                              ⠧ backports-strenum==1.3.1                                                                                              ⠧ hvac==2.4.0                                                                                                           ⠧ macaroonbakery==1.3.4                                                                                                 Resolved 115 packages in 1.81s
Removed appnope v0.1.4
Updated attrs v25.3.0, v25.4.0 -> v25.4.0
Removed backcall v0.2.0
Updated bandit v1.7.10, v1.8.6, v1.9.2 -> v1.9.2
Updated boto3 v1.7.84, v1.41.3 -> v1.41.3
Updated botocore v1.10.84, v1.41.3 -> v1.41.3
Updated cachetools v5.5.2, v6.2.2 -> v6.2.2
Updated cffi v1.17.1, v2.0.0 -> v2.0.0
Updated coverage v7.6.1, v7.10.7, v7.12.0 -> v7.12.0
Removed deprecated v1.3.1
Removed docutils v0.20.1, v0.22.3
Updated flake8 v5.0.4, v7.1.2, v7.3.0 -> v7.3.0
Updated importlib-metadata v8.5.0, v8.7.0 -> v8.7.0
Removed importlib-resources v6.4.5
Updated iniconfig v2.1.0, v2.3.0 -> v2.3.0
Updated ipython v8.12.3, v8.18.1, v8.37.0, v9.7.0 -> v8.37.0, v9.7.0
Updated jmespath v0.10.0, v1.0.1 -> v1.0.1
Updated jsonschema-specifications v2023.12.1, v2025.9.1 -> v2025.9.1
Updated juju v3.5.2.1, v3.6.1.3 -> v3.6.1.3
Updated markdown-it-py v3.0.0, v4.0.0 -> v4.0.0
Updated markupsafe v2.1.5, v3.0.3 -> v3.0.3
Updated matplotlib-inline v0.1.7, v0.2.1 -> v0.2.1
Updated mypy v1.14.1, v1.18.2 -> v1.18.2
Updated opentelemetry-api v1.33.1, v1.38.0 -> v1.38.0
Updated ops v2.23.2 -> v3.7.0
Updated ops-scenario v7.23.2 -> v8.7.0
Updated paramiko v3.5.1, v4.0.0 -> v4.0.0
Removed pbr v7.0.3
Updated pep8-naming v0.14.1, v0.15.1 -> v0.15.1
Removed pickleshare v0.7.5
Removed pkgutil-resolve-name v1.3.10
Updated pluggy v1.5.0, v1.6.0 -> v1.6.0
Updated psycopg2-binary v2.9.10, v2.9.11 -> v2.9.11
Updated pycodestyle v2.9.1, v2.12.1, v2.14.0 -> v2.14.0
Updated pyflakes v2.5.0, v3.2.0, v3.4.0 -> v3.4.0
Updated pytest v8.3.5, v8.4.2, v9.0.1 -> v9.0.1
Updated referencing v0.35.1, v0.36.2, v0.37.0 -> v0.37.0
Updated requests v2.32.4, v2.32.5 -> v2.32.5
Updated rpds-py v0.20.1, v0.27.1, v0.30.0 -> v0.30.0
Updated s3transfer v0.1.13, v0.15.0 -> v0.15.0
Removed setuptools v75.3.2
Updated soupsieve v2.7, v2.8 -> v2.8
Updated stevedore v5.3.0, v5.5.0, v5.6.0 -> v5.6.0
Updated tenacity v9.0.0, v9.1.2 -> v9.1.2
Updated types-pyyaml v6.0.12.20241230, v6.0.12.20250915 -> v6.0.12.20250915
Updated types-requests v2.32.0.20241016, v2.32.4.20250913 -> v2.32.4.20250913
Updated typing-extensions v4.13.2, v4.15.0 -> v4.15.0
Updated urllib3 v2.2.3, v2.5.0 -> v2.5.0
Updated websocket-client v1.8.0, v1.9.0 -> v1.9.0
Updated websockets v13.1, v15.0.1 -> v15.0.1
Removed wrapt v2.0.1
Updated zipp v3.20.2, v3.23.0 -> v3.23.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 53s</sub>

### 💬 Copilot

Now let's run the unit tests:

---

<sub>⏱️ 11m 57s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4 && tox -e unit 2>&1

<details>
<summary>104 lines</summary>

```
unit: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/.tox/unit
unit: uv-sync> uv sync --locked --python-preference system --no-default-groups --group unit -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
unit: commands[0]> coverage run --source=src -m pytest --ignore=tests/integration -v --tb native -s
================================================= test session starts ==================================================
platform linux -- Python 3.12.3, pytest-9.0.1, pluggy-1.6.0 -- /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/.tox/unit/bin/python3
cachedir: .tox/unit/.pytest_cache
rootdir: /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4
configfile: pyproject.toml
collecting ... collecting 12 items                                                                                                    collected 55 items                                                                                                     

tests/unit/test_charm.py::test_get_cors_origin_behavior[Wildcard disables augmentation] PASSED
tests/unit/test_charm.py::test_get_cors_origin_behavior[Raise error when invalid CORS config] PASSED
tests/unit/test_charm.py::test_get_cors_origin_behavior[Augment only with external_hostname (HTTPS)] PASSED
tests/unit/test_charm.py::test_get_cors_origin_behavior[Augment with external_hostname not explicitly defined] PASSED
tests/unit/test_charm.py::test_get_cors_origin_behavior[Augment with both external_hostname (HTTP) and s3_cdn_url] PASSED
tests/unit/test_charm.py::test_get_cors_origin_behavior[User-defined cors_origin, no augmentation] PASSED
tests/unit/test_charm.py::test_get_cors_origin_behavior[User-defined cors_origin with augmentation enabled] PASSED
tests/unit/test_charm.py::test_get_cors_origin_behavior[Multiple user-defined cors_origins with augmentation] PASSED
tests/unit/test_charm.py::test_get_cors_origin_behavior[Duplicated origins across cors_origin and augmentation] PASSED
tests/unit/test_charm.py::test_oauth_integration[Valid config] PASSED
tests/unit/test_charm.py::test_oauth_integration[Missing force_https] PASSED
tests/unit/test_charm.py::test_oauth_integration[external_hostname not set] PASSED
tests/unit_harness/test_charm.py::test_relations[No relation] PASSED
tests/unit_harness/test_charm.py::test_relations[Only redis] PASSED
tests/unit_harness/test_charm.py::test_relations[Only postgres] PASSED
tests/unit_harness/test_charm.py::test_relations[Postgres+redis] PASSED
tests/unit_harness/test_charm.py::test_relations[Only ingress] PASSED
tests/unit_harness/test_charm.py::test_relations[Redis+ingress] PASSED
tests/unit_harness/test_charm.py::test_relations[Postgres+ingress] PASSED
tests/unit_harness/test_charm.py::test_relations[All relations] PASSED
tests/unit_harness/test_charm.py::test_ingress_relation_not_ready PASSED
tests/unit_harness/test_charm.py::test_on_config_changed_when_no_saml_target PASSED
tests/unit_harness/test_charm.py::test_on_config_changed_when_saml_sync_groups_and_no_url_invalid PASSED
tests/unit_harness/test_charm.py::test_on_config_changed_when_saml_target_url_and_force_https_disabled PASSED
tests/unit_harness/test_charm.py::test_on_config_changed_when_no_cors PASSED
tests/unit_harness/test_charm.py::test_on_config_changed_when_throttle_mode_invalid PASSED
tests/unit_harness/test_charm.py::test_on_config_changed_when_s3_and_no_bucket_invalid PASSED
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid_no_s3_backup_nor_cdn PASSED
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid PASSED
tests/unit_harness/test_charm.py::test_db_relation PASSED
tests/unit_harness/test_charm.py::test_promote_user_success PASSED
tests/unit_harness/test_charm.py::test_promote_user_fail PASSED
tests/unit_harness/test_charm.py::test_create_user_success PASSED
tests/unit_harness/test_charm.py::test_create_user_fail PASSED
tests/unit_harness/test_charm.py::test_anonymize_user PASSED
tests/unit_harness/test_charm.py::test_sidekiq_env_variable PASSED
tests/unit_harness/test_charm.py::test_handle_pebble_ready_event PASSED
tests/unit_harness/test_charm.py::test_handle_redis_relation_changed_event PASSED
tests/unit_harness/test_charm.py::test_start_when_leader PASSED
tests/unit_harness/test_charm.py::test_start_when_not_leader PASSED
tests/unit_harness/test_charm.py::test_is_database_relation_ready[relation_data0-True] PASSED
tests/unit_harness/test_charm.py::test_is_database_relation_ready[relation_data1-False] PASSED
tests/unit_harness/test_charm.py::test_is_database_relation_ready[relation_data2-False] PASSED
tests/unit_harness/test_charm.py::test_is_redis_relation_ready[relation_data0-app_data0-True] PASSED
tests/unit_harness/test_charm.py::test_is_redis_relation_ready[relation_data1-app_data1-True] PASSED
tests/unit_harness/test_charm.py::test_is_redis_relation_ready[relation_data2-app_data2-False] PASSED
tests/unit_harness/test_charm.py::test_is_redis_relation_ready[relation_data3-app_data3-False] PASSED
tests/unit_harness/test_charm.py::test_is_redis_relation_ready[relation_data4-app_data4-False] PASSED
tests/unit_harness/test_charm.py::test_is_redis_relation_ready[relation_data5-app_data5-False] PASSED
tests/unit_harness/test_charm.py::test_is_redis_relation_ready[relation_data6-app_data6-False] PASSED
tests/unit_harness/test_charm.py::test_is_redis_relation_ready[relation_data7-app_data7-False] PASSED
tests/unit_harness/test_charm.py::test_relate_database_at_the_end PASSED
tests/unit_harness/test_charm.py::test_http_proxy_env PASSED
tests/unit_harness/test_charm.py::test_acquire_lock_on_upgrade PASSED
tests/unit_harness/test_charm.py::test_setup_and_activate_on_upgrade PASSED

=================================================== warnings summary ===================================================
tests/unit/test_charm.py: 11 warnings
tests/unit_harness/test_charm.py: 38 warnings
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
=========================================== 55 passed, 106 warnings in 2.15s ===========================================
unit: commands[1]> coverage report
Name                    Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------
src/charm.py              377     42     96     15    88%   170, 178-179, 191, 251->255, 299, 368->376, 400->405, 417, 609-611, 616-617, 629-631, 636-637, 649-651, 674-676, 714->exit, 773-776, 786-787, 811-812, 824-825, 852-854, 861-862, 904-905, 921-922, 932->exit, 946
src/constants.py           21      0      0      0   100%
src/database.py            29      1      8      1    95%   57
src/oauth_observer.py      54      8      8      2    84%   65, 80-81, 111, 114-123
-------------------------------------------------------------------
TOTAL                     481     51    112     18    88%
  unit: OK (2.85=setup[0.10]+cmd[2.67,0.08] seconds)
  congratulations :) (2.87 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12m 41s</sub>

### 💬 Copilot

`Harness` now emits a `PendingDeprecationWarning`. I should migrate those tests to `ops.testing`. Let me review the full harness test suite:

---

<sub>⏱️ 12m 41s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/test_charm.py.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/test_charm.py (lines 1-150)

<details>
<summary>150 lines</summary>

```
1. # Copyright 2026 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Unit tests for Discourse charm."""
5. 
6. # pylint: disable=protected-access
7. # Protected access check is disabled in tests as we're injecting test data
8. 
9. import secrets
10. from unittest.mock import MagicMock, patch
11. 
12. import ops
13. import pytest
14. from ops.model import ActiveStatus, BlockedStatus, WaitingStatus
15. 
16. from charm import CONTAINER_NAME, DISCOURSE_PATH, SERVICE_NAME
17. from constants import DATABASE_NAME
18. from tests.unit_harness import helpers
19. 
20. 
21. @pytest.mark.parametrize(
22.     "with_postgres, with_redis, with_ingress, status",
23.     [
24.         (False, False, False, WaitingStatus("Waiting for database relation")),
25.         (False, True, False, WaitingStatus("Waiting for database relation")),
26.         (True, False, False, WaitingStatus("Waiting for redis relation")),
27.         (True, True, False, ActiveStatus()),
28.         (False, False, True, WaitingStatus("Waiting for database relation")),
29.         (False, True, True, WaitingStatus("Waiting for database relation")),
30.         (True, False, True, WaitingStatus("Waiting for redis relation")),
31.         (True, True, True, ActiveStatus()),
32.     ],
33.     ids=[
34.         "No relation",
35.         "Only redis",
36.         "Only postgres",
37.         "Postgres+redis",
38.         "Only ingress",
39.         "Redis+ingress",
40.         "Postgres+ingress",
41.         "All relations",
42.     ],
43. )
44. def test_relations(with_postgres, with_redis, with_ingress, status):
45.     """
46.     arrange: given a deployed discourse charm
47.     act: when pebble ready event is triggered
48.     assert: it will have the correct status depending on the relations
49.     """
50.     harness = helpers.start_harness(
51.         with_postgres=with_postgres, with_redis=with_redis, with_ingress=with_ingress
52.     )
53.     harness.container_pebble_ready("discourse")
54.     assert harness.model.unit.status == status
55. 
56. 
57. def test_ingress_relation_not_ready():
58.     """
59.     arrange: given a deployed discourse charm with the ingress established
60.     act: when pebble ready event is triggered
61.     assert: it will wait for the ingress relation.
62.     """
63.     harness = helpers.start_harness(with_postgres=False, with_redis=False, with_ingress=True)
64.     assert harness.model.unit.status == WaitingStatus("Waiting for database relation")
65. 
66. 
67. def test_on_config_changed_when_no_saml_target():
68.     """
69.     arrange: given a deployed discourse charm with all the required relations
70.     act: when force_saml_login configuration is True and there's no saml_target_url
71.     assert: it will get to blocked status waiting for the latter.
72.     """
73.     harness = helpers.start_harness(with_config={"force_saml_login": True})
74.     assert harness.model.unit.status == BlockedStatus(
75.         "force_saml_login cannot be true without a saml relation"
76.     )
77. 
78. 
79. def test_on_config_changed_when_saml_sync_groups_and_no_url_invalid():
80.     """
81.     arrange: given a deployed discourse charm with all the required relations
82.     act: when saml_sync_groups configuration is provided and there's no saml_target_url
83.     assert: it will get to blocked status waiting for the latter.
84.     """
85.     harness = helpers.start_harness(with_config={"saml_sync_groups": "group1"})
86.     assert harness.model.unit.status == BlockedStatus(
87.         "'saml_sync_groups' cannot be specified without a saml relation"
88.     )
89. 
90. 
91. def test_on_config_changed_when_saml_target_url_and_force_https_disabled():
92.     """
93.     arrange: given a deployed discourse charm with all the required relations
94.     act: when saml_target_url configuration is provided and force_https is False
95.     assert: it will get to blocked status waiting for the latter.
96.     """
97.     harness = helpers.start_harness(with_config={"force_https": False}, saml_fields=(True, "", ""))
98.     harness.charm._is_config_valid()
99.     assert harness.model.unit.status == BlockedStatus(
100.         "A saml relation cannot be specified without 'force_https' being true"
101.     )
102. 
103. 
104. def test_on_config_changed_when_no_cors():
105.     """
106.     arrange: given a deployed discourse charm with all the required relations
107.     act: when cors_origin configuration is empty
108.     assert: it will get to blocked status waiting for it.
109.     """
110.     harness = helpers.start_harness(with_config={"cors_origin": ""})
111.     assert harness.charm._database.get_relation_data() is not None, (
112.         "database name should be set after relation joined"
113.     )
114.     assert harness.charm._database.get_relation_data().get("POSTGRES_DB") == DATABASE_NAME, (
115.         "database name should be set after relation joined"
116.     )
117. 
118. 
119. def test_on_config_changed_when_throttle_mode_invalid():
120.     """
121.     arrange: given a deployed discourse charm with all the required relations
122.     act: when throttle_level configuration is invalid
123.     assert: it will get to blocked status waiting for a valid value to be provided.
124.     """
125.     harness = helpers.start_harness(with_config={"throttle_level": "Scream"})
126.     assert isinstance(harness.model.unit.status, BlockedStatus)
127.     assert "none permissive strict" in harness.model.unit.status.message
128. 
129. 
130. def test_on_config_changed_when_s3_and_no_bucket_invalid():
131.     """
132.     arrange: given a deployed discourse charm with all the required relations
133.     act: when s3_enabled configuration is True and there's no s3_bucket
134.     assert: it will get to blocked status waiting for the latter.
135.     """
136.     harness = helpers.start_harness(
137.         with_config={
138.             "s3_access_key_id": "3|33+",
139.             "s3_enabled": True,
140.             "s3_endpoint": "s3.endpoint",
141.             "s3_region": "the-infinite-and-beyond",
142.             "s3_secret_access_key": "s|kI0ure_k3Y",  # nosec B105
143.         }
144.     )
145.     assert harness.model.unit.status == BlockedStatus("'s3_enabled' requires 's3_bucket'")
146. 
147. 
148. def test_on_config_changed_when_valid_no_s3_backup_nor_cdn():
149.     """
150.     arrange: given a deployed discourse charm with all the required relations
```

</details>


---

<sub>⏱️ 12m 41s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/src/charm.py.**

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

<sub>⏱️ 13m 24s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/test_charm.py.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/test_charm.py (lines 150-500)

<details>
<summary>351 lines</summary>

```
150.     arrange: given a deployed discourse charm with all the required relations
151.     act: when a valid configuration is provided
152.     assert: the appropriate configuration values are passed to the pod and the unit
153.         reaches Active status.
154.     """
155.     harness = helpers.start_harness()
156. 
157.     # We catch the exec call that we expect to register it and make sure that the
158.     # args passed to it are correct.
159.     expected_exec_call_was_made = False
160. 
161.     def bundle_handler(args: ops.testing.ExecArgs) -> None:
162.         nonlocal expected_exec_call_was_made
163.         expected_exec_call_was_made = True
164.         if (
165.             args.environment != harness.charm._create_discourse_environment_settings()
166.             or args.working_dir != DISCOURSE_PATH
167.             or args.user != "_daemon_"
168.         ):
169.             raise ValueError("Exec rake s3:upload_assets wasn't made with the correct args.")
170. 
171.     harness.handle_exec(
172.         SERVICE_NAME,
173.         [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", "s3:upload_assets"],
174.         handler=bundle_handler,
175.     )
176. 
177.     harness.set_leader(True)
178.     harness.update_config(
179.         {
180.             "s3_access_key_id": "3|33+",
181.             "s3_bucket": "who-s-a-good-bucket?",
182.             "s3_enabled": True,
183.             "s3_endpoint": "s3.endpoint",
184.             "s3_region": "the-infinite-and-beyond",
185.             "s3_secret_access_key": "s|kI0ure_k3Y",  # nosec B105
186.         }
187.     )
188.     harness.container_pebble_ready(SERVICE_NAME)
189.     harness.framework.reemit()
190. 
191.     assert harness.charm
192.     assert expected_exec_call_was_made
193.     assert isinstance(harness.model.unit.status, ActiveStatus)
194. 
195.     updated_plan = harness.get_container_pebble_plan(SERVICE_NAME).to_dict()
196.     updated_plan_env = updated_plan["services"][SERVICE_NAME]["environment"]
197.     assert "DISCOURSE_BACKUP_LOCATION" not in updated_plan_env
198.     assert updated_plan_env["DISCOURSE_CORS_ORIGIN"] == "http://discourse-k8s"
199.     assert updated_plan_env["DISCOURSE_DB_HOST"] == "dbhost"
200.     assert updated_plan_env["DISCOURSE_DB_NAME"] == DATABASE_NAME
201.     assert updated_plan_env["DISCOURSE_DB_PASSWORD"] == "somepasswd"
202.     assert updated_plan_env["DISCOURSE_DB_USERNAME"] == "someuser"
203.     assert updated_plan_env["DISCOURSE_ENABLE_CORS"]
204.     assert updated_plan_env["DISCOURSE_HOSTNAME"] == "discourse-k8s"
205.     assert updated_plan_env["DISCOURSE_MAX_CATEGORY_NESTING"] == "2"
206.     assert updated_plan_env["DISCOURSE_REDIS_HOST"] == "redis-host"
207.     assert updated_plan_env["DISCOURSE_REDIS_PORT"] == "1010"
208.     assert updated_plan_env["DISCOURSE_SERVE_STATIC_ASSETS"]
209.     assert updated_plan_env["DISCOURSE_S3_ACCESS_KEY_ID"] == "3|33+"
210.     assert "DISCOURSE_S3_BACKUP_BUCKET" not in updated_plan_env
211.     assert "DISCOURSE_S3_CDN_URL" not in updated_plan_env
212.     assert updated_plan_env["DISCOURSE_S3_BUCKET"] == "who-s-a-good-bucket?"
213.     assert updated_plan_env["DISCOURSE_S3_ENDPOINT"] == "s3.endpoint"
214.     assert updated_plan_env["DISCOURSE_S3_REGION"] == "the-infinite-and-beyond"
215.     assert updated_plan_env["DISCOURSE_S3_SECRET_ACCESS_KEY"] == "s|kI0ure_k3Y"
216.     assert updated_plan_env["DISCOURSE_USE_S3"]
217. 
218. 
219. def test_on_config_changed_when_valid():
220.     """
221.     arrange: given a deployed discourse charm with all the required relations
222.     act: when a valid configuration is provided
223.     assert: the appropriate configuration values are passed to the pod and the unit
224.         reaches Active status.
225.     """
226.     harness = helpers.start_harness(
227.         with_config={
228.             "developer_emails": "user@foo.internal",
229.             "enable_cors": True,
230.             "external_hostname": "discourse.local",
231.             "force_saml_login": True,
232.             "saml_sync_groups": "group1",
233.             "smtp_address": "smtp.internal",
234.             "smtp_domain": "foo.internal",
235.             "smtp_password": "OBV10USLYF4K3",  # nosec B105
236.             "smtp_username": "apikey",
237.             "s3_access_key_id": "3|33+",
238.             "s3_backup_bucket": "back-bucket",
239.             "s3_bucket": "who-s-a-good-bucket?",
240.             "s3_cdn_url": "s3.cdn",
241.             "s3_enabled": True,
242.             "s3_endpoint": "s3.endpoint",
243.             "s3_region": "the-infinite-and-beyond",
244.             "s3_secret_access_key": "s|kI0ure_k3Y",  # nosec B105
245.             "force_https": True,
246.         },
247.         saml_fields=(True, "https://login.ubuntu.com", "fingerprint"),
248.     )
249.     harness.container_pebble_ready(SERVICE_NAME)
250.     assert isinstance(harness.model.unit.status, ActiveStatus)
251. 
252.     updated_plan = harness.get_container_pebble_plan(SERVICE_NAME).to_dict()
253.     updated_plan_env = updated_plan["services"][SERVICE_NAME]["environment"]
254.     assert updated_plan_env["DISCOURSE_BACKUP_LOCATION"] == "s3"
255.     assert updated_plan_env["DISCOURSE_CORS_ORIGIN"] == "https://discourse.local,s3.cdn"
256.     assert updated_plan_env["DISCOURSE_DB_HOST"] == "dbhost"
257.     assert updated_plan_env["DISCOURSE_DB_NAME"] == DATABASE_NAME
258.     assert updated_plan_env["DISCOURSE_DB_PASSWORD"] == "somepasswd"
259.     assert updated_plan_env["DISCOURSE_DB_USERNAME"] == "someuser"
260.     assert updated_plan_env["DISCOURSE_DEVELOPER_EMAILS"] == "user@foo.internal"
261.     assert updated_plan_env["DISCOURSE_ENABLE_CORS"]
262.     assert updated_plan_env["DISCOURSE_HOSTNAME"] == "discourse.local"
263.     assert updated_plan_env["DISCOURSE_MAX_CATEGORY_NESTING"] == "2"
264.     assert updated_plan_env["DISCOURSE_REDIS_HOST"] == "redis-host"
265.     assert updated_plan_env["DISCOURSE_REDIS_PORT"] == "1010"
266.     assert updated_plan_env["DISCOURSE_SAML_CERT_FINGERPRINT"] is not None
267.     assert updated_plan_env["DISCOURSE_SAML_FULL_SCREEN_LOGIN"] == "true"
268.     assert updated_plan_env["DISCOURSE_SAML_TARGET_URL"] == "https://login.ubuntu.com/+saml"
269.     assert updated_plan_env["DISCOURSE_SAML_GROUPS_FULLSYNC"] == "false"
270.     assert updated_plan_env["DISCOURSE_SAML_SYNC_GROUPS"] == "true"
271.     assert updated_plan_env["DISCOURSE_SAML_SYNC_GROUPS_LIST"] == "group1"
272.     assert updated_plan_env["DISCOURSE_SERVE_STATIC_ASSETS"]
273.     assert updated_plan_env["DISCOURSE_S3_ACCESS_KEY_ID"] == "3|33+"
274.     assert updated_plan_env["DISCOURSE_S3_BACKUP_BUCKET"] == "back-bucket"
275.     assert updated_plan_env["DISCOURSE_S3_CDN_URL"] == "s3.cdn"
276.     assert updated_plan_env["DISCOURSE_S3_BUCKET"] == "who-s-a-good-bucket?"
277.     assert updated_plan_env["DISCOURSE_S3_ENDPOINT"] == "s3.endpoint"
278.     assert updated_plan_env["DISCOURSE_S3_REGION"] == "the-infinite-and-beyond"
279.     assert updated_plan_env["DISCOURSE_S3_SECRET_ACCESS_KEY"] == "s|kI0ure_k3Y"
280.     assert updated_plan_env["DISCOURSE_SMTP_ADDRESS"] == "smtp.internal"
281.     assert updated_plan_env["DISCOURSE_SMTP_AUTHENTICATION"] == "none"
282.     assert updated_plan_env["DISCOURSE_SMTP_DOMAIN"] == "foo.internal"
283.     assert updated_plan_env["DISCOURSE_SMTP_OPENSSL_VERIFY_MODE"] == "none"
284.     assert updated_plan_env["DISCOURSE_SMTP_PASSWORD"] == "OBV10USLYF4K3"
285.     assert updated_plan_env["DISCOURSE_SMTP_PORT"] == "587"
286.     assert updated_plan_env["DISCOURSE_SMTP_USER_NAME"] == "apikey"
287.     assert updated_plan_env["DISCOURSE_USE_S3"]
288.     assert updated_plan_env["FORCE_S3_UPLOADS"]
289. 
290. 
291. def test_db_relation():
292.     """
293.     arrange: given a deployed discourse charm
294.     act: when the database relation is added
295.     assert: the appropriate database name is set.
296.     """
297.     harness = helpers.start_harness()
298.     harness.set_leader(True)
299. 
300.     db_relation_data = harness.get_relation_data(
301.         # This attribute was defined in the helpers
302.         harness.db_relation_id,  # pylint: disable=no-member
303.         "postgresql",
304.     )
305. 
306.     assert db_relation_data.get("database") == DATABASE_NAME, (
307.         "database name should be set after relation joined"
308.     )
309.     assert harness.charm._database.get_relation_data().get("POSTGRES_DB") == DATABASE_NAME, (
310.         "database name should be set after relation joined"
311.     )
312. 
313. 
314. def test_promote_user_success():
315.     """
316.     arrange: an email and a password
317.     act: when the _on_promote_user_action method is executed
318.     assert: the underlying rake command to add the user is executed
319.         with the appropriate parameters.
320.     """
321.     harness = helpers.start_harness()
322. 
323.     # We catch the exec call that we expect to register it and make sure that the
324.     # args passed to it are correct.
325.     expected_exec_call_was_made = False
326. 
327.     def bundle_handler(args: ops.testing.ExecArgs) -> None:
328.         nonlocal expected_exec_call_was_made
329.         expected_exec_call_was_made = True
330.         if (
331.             args.environment != harness.charm._create_discourse_environment_settings()
332.             or args.working_dir != DISCOURSE_PATH
333.             or args.user != "_daemon_"
334.             or args.stdin != f"{email}\nn\nY\n"
335.             or args.timeout != 60
336.         ):
337.             raise ValueError(f"{args.command} wasn't made with the correct args.")
338. 
339.     harness.handle_exec(
340.         SERVICE_NAME,
341.         [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", "admin:create"],
342.         handler=bundle_handler,
343.     )
344. 
345.     email = "sample@email.com"
346.     harness.run_action("promote-user", {"email": email})
347.     assert expected_exec_call_was_made
348. 
349. 
350. def test_promote_user_fail():
351.     """
352.     arrange: an email
353.     act: when the _on_create_user_action method is executed
354.     assert: the create user rake command is executed upon failure of the user existence check.
355.     """
356.     harness = helpers.start_harness()
357. 
358.     # We catch the exec call that we expect to register it and make sure that the
359.     # args passed to it are correct.
360.     expected_exec_call_was_made = False
361.     email = "sample@email.com"
362. 
363.     def mock_create_user(args: ops.testing.ExecArgs) -> None:
364.         nonlocal expected_exec_call_was_made
365.         expected_exec_call_was_made = True
366.         if (
367.             args.environment != harness.charm._create_discourse_environment_settings()
368.             or args.working_dir != DISCOURSE_PATH
369.             or email not in str(args.stdin)
370.             or args.user != "_daemon_"
371.             or args.timeout != 60
372.         ):
373.             raise ValueError(f"{args.command} wasn't made with the correct args.")
374. 
375.     harness.handle_exec(
376.         SERVICE_NAME,
377.         [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", "admin:create"],
378.         handler=mock_create_user,
379.     )
380. 
381.     stdout = "ERROR: User with email f{email} not found"
382. 
383.     # Exit code 2 means that the user cannot be found in the rake task.
384.     harness.handle_exec(
385.         SERVICE_NAME,
386.         [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", f"users:exists[{email}]"],
387.         result=ops.testing.ExecResult(exit_code=2, stdout=stdout, stderr=""),
388.     )
389.     try:
390.         harness.run_action("promote-user", {"email": email})
391.         assert False
392.     except ops.testing.ActionFailed as e:
393.         assert e.message == f"User with email {email} does not exist"
394. 
395.     # Exit code 1 means that the rake task failed.
396.     harness.handle_exec(
397.         SERVICE_NAME,
398.         [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", f"users:exists[{email}]"],
399.         result=ops.testing.ExecResult(exit_code=1, stdout=stdout, stderr=""),
400.     )
401.     try:
402.         harness.run_action("promote-user", {"email": email})
403.         assert False
404.     except ops.pebble.ExecError as e:
405.         assert "non-zero exit code 1" in str(e)
406. 
407. 
408. def test_create_user_success():
409.     """
410.     arrange: an email
411.     act: when the _on_create_user_action method is executed
412.     assert: the create user rake command is executed upon failure of the user existence check.
413.     """
414.     harness = helpers.start_harness()
415. 
416.     # We catch the exec call that we expect to register it and make sure that the
417.     # args passed to it are correct.
418.     expected_exec_call_was_made = False
419.     email = "sample@email.com"
420. 
421.     def mock_create_user(args: ops.testing.ExecArgs) -> None:
422.         nonlocal expected_exec_call_was_made
423.         expected_exec_call_was_made = True
424.         if (
425.             args.environment != harness.charm._create_discourse_environment_settings()
426.             or args.working_dir != DISCOURSE_PATH
427.             or email not in str(args.stdin)
428.             or args.user != "_daemon_"
429.             or args.timeout != 60
430.         ):
431.             raise ValueError(f"{args.command} wasn't made with the correct args.")
432. 
433.     harness.handle_exec(
434.         SERVICE_NAME,
435.         [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", "admin:create"],
436.         handler=mock_create_user,
437.     )
438. 
439.     stdout = "ERROR: User with email f{email} not found"
440.     harness.handle_exec(
441.         SERVICE_NAME,
442.         [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", f"users:exists[{email}]"],
443.         result=ops.testing.ExecResult(exit_code=2, stdout=stdout, stderr=""),
444.     )
445. 
446.     harness.run_action("create-user", {"email": email})
447.     assert expected_exec_call_was_made
448. 
449. 
450. def test_create_user_fail():
451.     """
452.     arrange: an email
453.     act: when the _on_create_user_action method is executed
454.     assert: the create user rake command is executed upon failure of the user existence check.
455.     """
456.     harness = helpers.start_harness()
457. 
458.     # We catch the exec call that we expect to register it and make sure that the
459.     # args passed to it are correct.
460.     expected_exec_call_was_made = False
461.     email = "sample@email.com"
462. 
463.     def mock_create_user(args: ops.testing.ExecArgs) -> None:
464.         nonlocal expected_exec_call_was_made
465.         expected_exec_call_was_made = True
466.         if (
467.             args.environment != harness.charm._create_discourse_environment_settings()
468.             or args.working_dir != DISCOURSE_PATH
469.             or email not in str(args.stdin)
470.             or args.user != "_daemon_"
471.             or args.timeout != 60
472.         ):
473.             raise ValueError(f"{args.command} wasn't made with the correct args.")
474. 
475.     harness.handle_exec(
476.         SERVICE_NAME,
477.         [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", "admin:create"],
478.         handler=mock_create_user,
479.     )
480. 
481.     try:
482.         harness.run_action("create-user", {"email": email})
483.         assert False
484.     except ops.testing.ActionFailed as e:
485.         assert e.message == f"User with email {email} already exists"
486. 
487. 
488. def test_anonymize_user():
489.     """
490.     arrange: set up discourse
491.     act: execute the _on_anonymize_user_action method
492.     assert: the underlying rake command to anonymize the user is executed
493.         with the appropriate parameters.
494.     """
495.     harness = helpers.start_harness()
496.     username = "someusername"
497. 
498.     # We catch the exec call that we expect to register it and make sure that the
499.     # args passed to it are correct.
500.     expected_exec_call_was_made = False
```

</details>


---

<sub>⏱️ 14m 10s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/test_charm.py.**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C4/tests/unit_harness/test_charm.py (lines 500-800)

<details>
<summary>301 lines</summary>

```
500.     expected_exec_call_was_made = False
501. 
502.     def bundle_handler(args: ops.testing.ExecArgs) -> None:
503.         nonlocal expected_exec_call_was_made
504.         expected_exec_call_was_made = True
505.         if (
506.             args.environment != harness.charm._create_discourse_environment_settings()
507.             or args.working_dir != DISCOURSE_PATH
508.             or args.user != "_daemon_"
509.         ):
510.             raise ValueError(f"{args.command} wasn't made with the correct args.")
511. 
512.     harness.handle_exec(
513.         SERVICE_NAME,
514.         [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", f"users:anonymize[{username}]"],
515.         handler=bundle_handler,
516.     )
517. 
518.     harness.run_action("anonymize-user", {"username": username})
519.     assert expected_exec_call_was_made
520. 
521. 
522. def test_sidekiq_env_variable():
523.     """
524.     arrange: given a deployed discourse charm with all the required relations
525.     act: trigger the pebble ready event on a leader unit
526.     assert: the pebble plan gets updated
527.     """
528.     harness = helpers.start_harness(run_initial_hooks=False)
529. 
530.     harness.set_can_connect(CONTAINER_NAME, True)
531.     harness.container_pebble_ready(CONTAINER_NAME)
532.     plan_before_set_config = (
533.         harness.get_container_pebble_plan(CONTAINER_NAME).services["discourse"].environment
534.     )
535.     harness.update_config({"sidekiq_max_memory": 500})
536.     plan_after_set_config = (
537.         harness.get_container_pebble_plan(CONTAINER_NAME).services["discourse"].environment
538.     )
539.     assert plan_before_set_config != plan_after_set_config
540.     assert "1000" in plan_before_set_config["UNICORN_SIDEKIQ_MAX_RSS"]
541.     assert "500" in plan_after_set_config["UNICORN_SIDEKIQ_MAX_RSS"]
542. 
543. 
544. def test_handle_pebble_ready_event():
545.     """
546.     arrange: given a deployed discourse charm with all the required relations
547.     act: trigger the pebble ready event on a leader unit
548.     assert: the pebble plan gets updated
549.     """
550.     harness = helpers.start_harness(run_initial_hooks=False)
551. 
552.     harness.set_can_connect(CONTAINER_NAME, True)
553.     plan_before_event = harness.get_container_pebble_plan(CONTAINER_NAME)
554.     harness.container_pebble_ready(CONTAINER_NAME)
555.     plan_after_event = harness.get_container_pebble_plan(CONTAINER_NAME)
556.     assert plan_before_event.__dict__ != plan_after_event.__dict__
557.     assert "_services" in plan_after_event.__dict__
558.     assert "discourse" in plan_after_event.__dict__["_services"]
559. 
560. 
561. def test_handle_redis_relation_changed_event():
562.     """
563.     arrange: given a deployed discourse charm with all the required relations
564.     act: trigger the pebble ready event on a leader unit
565.     assert: the pebble plan gets updated
566.     """
567.     harness = helpers.start_harness(with_redis=False)
568. 
569.     harness.container_pebble_ready(CONTAINER_NAME)
570.     plan_before_event = harness.get_container_pebble_plan(CONTAINER_NAME)
571.     helpers.add_redis_relation(harness)
572.     harness.charm.on.redis_relation_updated.emit()
573.     plan_after_event = harness.get_container_pebble_plan(CONTAINER_NAME)
574.     assert plan_before_event.__dict__ != plan_after_event.__dict__
575.     assert "_services" in plan_after_event.__dict__
576.     assert "discourse" in plan_after_event.__dict__["_services"]
577. 
578. 
579. def test_start_when_leader():
580.     """
581.     arrange: given a deployed discourse charm with all the required relations
582.     act: trigger the start event on a leader unit
583.     assert: migrations are executed and assets are precompiled.
584.     """
585.     harness = helpers.start_harness(run_initial_hooks=False)
586. 
587.     # exec calls that we want to monitor
588.     exec_calls = [
589.         [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", "--trace", "db:migrate"],
590.         [f"{DISCOURSE_PATH}/bin/rails", "runner", "puts Discourse::VERSION::STRING"],
591.     ]
592. 
593.     # construct the dict to store if those calls were executed
594.     expected_exec_call_was_made = {" ".join(call): False for call in exec_calls}
595. 
596.     # We catch the exec calls that we expect to register
597.     # it and make sure that the args passed to it are correct.
598.     def exec_handler(args: ops.testing.ExecArgs) -> None:
599.         nonlocal expected_exec_call_was_made
600. 
601.         # set the call as executed
602.         expected_exec_call_was_made[" ".join(args.command)] = True
603. 
604.         if (
605.             args.environment != harness.charm._create_discourse_environment_settings()
606.             or args.working_dir != DISCOURSE_PATH
607.             or args.user != "_daemon_"
608.         ):
609.             raise ValueError(f"{args.command} wasn't made with the correct args.")
610. 
611.     for call in exec_calls:
612.         harness.handle_exec(SERVICE_NAME, call, handler=exec_handler)
613. 
614.     # The leader-elected event will cause rollingops to fail because the RollingOpsManager has not
615.     # yet been initialised in the charm's __init__ method.
616.     harness.disable_hooks()
617.     harness.set_leader(True)
618.     harness.enable_hooks()
619.     harness.container_pebble_ready(SERVICE_NAME)
620.     # A few events are not emitted, like config_changed.
621.     harness.charm.on.start.emit()
622.     harness.framework.reemit()
623. 
624.     assert all(expected_exec_call_was_made.values())
625. 
626. 
627. def test_start_when_not_leader():
628.     """
629.     arrange: given a deployed discourse charm with all the required relations
630.     act: trigger the start event on a leader unit
631.     assert: migrations are executed and assets are precompiled.
632.     """
633.     harness = helpers.start_harness(run_initial_hooks=False)
634. 
635.     # exec calls that we want to monitor
636.     exec_calls = [
637.         [f"{DISCOURSE_PATH}/bin/rails", "runner", "puts Discourse::VERSION::STRING"],
638.     ]
639. 
640.     # construct the dict to store if those calls were executed
641.     expected_exec_call_was_made = {" ".join(call): False for call in exec_calls}
642. 
643.     # We catch the exec calls that we expect to register
644.     # it and make sure that the args passed to it are correct.
645.     def exec_handler(args: ops.testing.ExecArgs) -> None:
646.         nonlocal expected_exec_call_was_made
647. 
648.         # set the call as executed
649.         expected_exec_call_was_made[" ".join(args.command)] = True
650. 
651.         if (
652.             args.environment != harness.charm._create_discourse_environment_settings()
653.             or args.working_dir != DISCOURSE_PATH
654.             or args.user != "_daemon_"
655.         ):
656.             raise ValueError(f"{args.command} wasn't made with the correct args.")
657. 
658.     for call in exec_calls:
659.         harness.handle_exec(SERVICE_NAME, call, handler=exec_handler)
660. 
661.     harness.set_leader(False)
662.     harness.container_pebble_ready(SERVICE_NAME)
663.     harness.charm.on.start.emit()
664.     harness.framework.reemit()
665. 
666.     assert all(expected_exec_call_was_made.values())
667. 
668. 
669. @pytest.mark.parametrize(
670.     "relation_data, should_be_ready",
671.     [
672.         (
673.             {
674.                 "database": DATABASE_NAME,
675.                 "endpoints": "dbhost:5432,dbhost-2:5432",
676.                 "password": secrets.token_hex(16),
677.                 "username": "someuser",
678.             },
679.             True,
680.         ),
681.         (
682.             {
683.                 "database": DATABASE_NAME,
684.                 "endpoints": "foo",
685.                 "password": secrets.token_hex(16),
686.                 "username": "someuser",
687.             },
688.             False,
689.         ),
690.         (
691.             {
692.                 "database": DATABASE_NAME,
693.                 "endpoints": "dbhost:5432,dbhost-2:5432",
694.                 "password": "",  # nosec B105
695.                 "username": "someuser",
696.             },
697.             False,
698.         ),
699.     ],
700. )
701. def test_is_database_relation_ready(relation_data, should_be_ready):
702.     """
703.     arrange: given a deployed discourse charm and some relation data
704.     act: add the postgresql relation to the charm
705.     assert: the charm should wait for some correct relation data
706.     """
707.     harness = helpers.start_harness(with_postgres=False, with_redis=False)
708.     db_relation_id = harness.add_relation("database", "postgresql")
709.     harness.add_relation_unit(db_relation_id, "postgresql/0")
710.     harness.update_relation_data(
711.         db_relation_id,
712.         "postgresql",
713.         relation_data,
714.     )
715.     if should_be_ready:
716.         assert harness.model.unit.status == WaitingStatus("Waiting for redis relation")
717.     else:
718.         assert harness.model.unit.status == WaitingStatus("Waiting for database relation")
719. 
720. 
721. @pytest.mark.parametrize(
722.     "relation_data, app_data, should_be_ready",
723.     [
724.         (
725.             {"hostname": "redis-host", "port": "1010"},
726.             {"leader-host": "redis-host"},
727.             True,
728.         ),
729.         (
730.             {"hostname": "redis-host", "port": "1010"},
731.             {},
732.             True,
733.         ),
734.         (
735.             {"hostname": "redis-host", "port": "0"},
736.             {"leader-host": ""},
737.             False,
738.         ),
739.         (
740.             {"hostname": "", "port": "1010"},
741.             {"leader-host": ""},
742.             False,
743.         ),
744.         (
745.             {"hostname": "redis-host"},
746.             {},
747.             False,
748.         ),
749.         (
750.             {},
751.             {},
752.             False,
753.         ),
754.         (
755.             {"port": "6379"},
756.             {},
757.             False,
758.         ),
759.         (
760.             {"hostname": "redis-port"},
761.             {},
762.             False,
763.         ),
764.     ],
765. )
766. def test_is_redis_relation_ready(relation_data, app_data, should_be_ready):
767.     """
768.     arrange: given a deployed discourse charm and some relation data
769.     act: add the redis relation to the charm
770.     assert: the charm should wait for some correct relation data
771.     """
772.     harness = helpers.start_harness(with_postgres=True, with_redis=False)
773.     helpers.add_redis_relation(harness, relation_data, app_data)
774.     assert should_be_ready == harness.charm._are_relations_ready()
775. 
776. 
777. def test_relate_database_at_the_end():
778.     """
779.     arrange: given a deployed discourse charm with redis related
780.     act: relate the database after the pebble ready event
781.     assert: it should activate the charm
782.     """
783.     harness = helpers.start_harness(with_postgres=False, with_redis=True)
784.     harness.container_pebble_ready("discourse")
785.     helpers.add_postgres_relation(harness)
786.     assert harness.model.unit.status == ActiveStatus()
787. 
788. 
789. def test_http_proxy_env(monkeypatch):
790.     """
791.     arrange: given a deployed discourse charm with all the required relations
792.     act: when a juju http_proxy variable is changed
793.     assert: the appropriate configuration values should be present in the created env
794.     """
795.     harness = helpers.start_harness()
796. 
797.     created_env = harness.charm._create_discourse_environment_settings()
798.     assert created_env["HTTP_PROXY"] == ""
799.     assert created_env["http_proxy"] == ""
800.     assert created_env["HTTPS_PROXY"] == ""
```

</details>


---

<sub>⏱️ 14m 57s</sub>

### ℹ️ Info

Operation cancelled by user

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
