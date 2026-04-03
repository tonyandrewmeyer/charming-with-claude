# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `799b6bcf-0bd5-4ba1-aa36-06db65945ca7`  
> - **Started:** 4/2/2026, 6:05:25 AM  
> - **Duration:** 14m 56s  
> - **Exported:** 4/2/2026, 6:20:21 AM  

---

<sub>⏱️ 6s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 13s</sub>

### ✅ `bash`

**Check current ops version**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat pyproject.toml | grep -A5 -i "ops"

<details>
<summary>14 lines</summary>

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 13s</sub>

### ✅ `bash`

**List source files**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && find . -name "*.py" | head -20 && ls src/

<details>
<summary>22 lines</summary>

```
./lib/charms/istio_beacon_k8s/v0/service_mesh.py
./lib/charms/observability_libs/v0/kubernetes_compute_resources_patch.py
./lib/charms/tempo_coordinator_k8s/v0/tracing.py
./lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py
./lib/charms/karma_k8s/v0/karma_dashboard.py
./lib/charms/alertmanager_k8s/v1/alertmanager_dispatch.py
./lib/charms/alertmanager_k8s/v0/alertmanager_remote_configuration.py
./lib/charms/grafana_k8s/v0/grafana_dashboard.py
./lib/charms/grafana_k8s/v0/grafana_source.py
./lib/charms/catalogue_k8s/v1/catalogue.py
./lib/charms/prometheus_k8s/v0/prometheus_scrape.py
./lib/charms/traefik_k8s/v2/ingress.py
./lib/charms/tls_certificates_interface/v4/tls_certificates.py
./src/alertmanager_client.py
./src/alertmanager.py
./src/config_builder.py
./src/charm.py
./tests/integration/test_tls_web.py
./tests/integration/conftest.py
./tests/integration/helpers.py
alertmanager.py  alertmanager_client.py  charm.py  config_builder.py  grafana_dashboards  prometheus_alert_rules
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 19s</sub>

### ✅ `bash`

**Read full pyproject.toml**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat pyproject.toml

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

<sub>⏱️ 20s</sub>

### ✅ `bash`

**Check installed ops version and available versions**

$ pip show ops 2>/dev/null | grep Version; pip index versions ops 2>/dev/null | head -5

<details>
<summary>6 lines</summary>

```
Version: 3.7.0
ops (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 2.20.0, 2.19.4, 2.19.0, 2.18.1, 2.18.0, 2.17.1, 2.17.0, 2.16.1, 2.16.0, 2.15.0, 2.14.1, 2.14.0, 2.13.0, 2.12.0, 2.11.0, 2.10.0, 2.9.0, 2.8.0, 2.7.0, 2.6.0, 2.5.1, 2.5.0, 2.4.1, 2.4.0, 2.3.0, 2.2.0, 2.1.1, 2.1.0, 2.0.0, 1.5.5, 1.5.4, 1.5.3, 1.5.2, 1.5.1, 1.5.0, 1.4.0, 1.3.0, 1.2.0, 1.1.0, 1.0.1, 1.0.0, 0.10.0, 0.9.0, 0.8.0, 0.7.0, 0.6.1, 0.6.0, 0.4.7, 0.4.6, 0.4.5, 0.4.4, 0.4.3, 0.4.2, 0.2.1, 0.2.0, 0.1.0
  INSTALLED: 3.7.0
  LATEST:    3.7.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 29s</sub>

### ✅ `bash`

**Check available versions of ops packages**

$ pip index versions ops 2>/dev/null; pip index versions ops-tracing 2>/dev/null; pip index versions ops-scenario 2>/dev/null

<details>
<summary>13 lines</summary>

```
ops (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 2.20.0, 2.19.4, 2.19.0, 2.18.1, 2.18.0, 2.17.1, 2.17.0, 2.16.1, 2.16.0, 2.15.0, 2.14.1, 2.14.0, 2.13.0, 2.12.0, 2.11.0, 2.10.0, 2.9.0, 2.8.0, 2.7.0, 2.6.0, 2.5.1, 2.5.0, 2.4.1, 2.4.0, 2.3.0, 2.2.0, 2.1.1, 2.1.0, 2.0.0, 1.5.5, 1.5.4, 1.5.3, 1.5.2, 1.5.1, 1.5.0, 1.4.0, 1.3.0, 1.2.0, 1.1.0, 1.0.1, 1.0.0, 0.10.0, 0.9.0, 0.8.0, 0.7.0, 0.6.1, 0.6.0, 0.4.7, 0.4.6, 0.4.5, 0.4.4, 0.4.3, 0.4.2, 0.2.1, 0.2.0, 0.1.0
  INSTALLED: 3.7.0
  LATEST:    3.7.0
ops-tracing (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 0.9.6, 0.9.4, 0.9.3, 0.9.2, 0.9.1, 0.9.0
  INSTALLED: 3.7.0
  LATEST:    3.7.0
ops-scenario (8.7.0)
Available versions: 8.7.0, 8.6.0, 8.5.2, 8.5.1, 8.5.0, 8.4.0, 8.3.1, 8.3.0, 8.2.0, 8.1.0, 8.0.0, 7.23.2, 7.23.1, 7.23.0, 7.22.0, 7.21.1, 7.21.0, 7.20.0, 7.19.4, 7.2.0, 7.1.3, 7.1.2, 7.1.1, 7.0.5, 7.0.4, 7.0.3, 7.0.2, 7.0.1, 7.0.0, 6.1.7, 6.1.6, 6.1.5, 6.1.4, 6.1.3, 6.1.2, 6.1.1, 6.1.0, 6.0.5, 6.0.4, 6.0.3, 6.0.2, 6.0.1, 6.0, 5.8.1, 5.8, 5.7.1, 5.7, 5.6.2, 5.6.1, 5.6, 5.5, 5.4.1, 5.4, 5.3.1, 5.3, 5.2.2, 5.2.1, 5.2, 5.1.3, 5.1.2, 5.1.1, 5.1.0, 5.0, 4.0.4.1, 4.0.4, 4.0.3, 4.0.2, 4.0.1, 4.0, 3.1, 3.0.2, 3.0.1, 2.2, 2.1.3.5, 2.1.3.4, 2.1.3.3, 2.1.3.2, 2.1.3.1, 2.1.3, 2.1.2.5, 2.1.2.4, 2.1.2.3, 2.1.2.2, 2.1.2.1, 2.1.1, 2.1.0, 2.0.5, 2.0.4, 2.0.0
  INSTALLED: 8.7.0
  LATEST:    8.7.0
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

<sub>⏱️ 37s</sub>

### ✅ `bash`

**Check ops version in uv.lock**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep -A3 "name = \"ops\"" uv.lock | head -20

<details>
<summary>21 lines</summary>

```
{ name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.11.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
--
    { name = "ops", extra = ["testing"] },
    { name = "pyright" },
    { name = "pytest" },
    { name = "pytest-httpserver", version = "1.1.1", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
--
    { name = "ops" },
    { name = "ops", extras = ["testing"], marker = "extra == 'dev'" },
    { name = "pydantic", specifier = ">=2" },
    { name = "pyright", marker = "extra == 'dev'", specifier = "<1.1.399" },
    { name = "pytest", marker = "extra == 'dev'" },
--
    { name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.11.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 37s</sub>

### ✅ `bash`

**Check git log**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && git --no-pager log --oneline -10

```
6101e73 (grafted, HEAD, origin/main, origin/HEAD, main) chore: update charm libraries (#394)
<exited with exit code 0>
```


---

<sub>⏱️ 45s</sub>

### ✅ `bash`

**Check ops exact version in uv.lock**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep -B2 -A10 "^name = \"ops\"" uv.lock | head -40

<details>
<summary>13 lines</summary>

```
[[package]]
name = "ops"
version = "2.21.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "importlib-metadata", version = "8.5.0", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "importlib-metadata", version = "8.6.1", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "opentelemetry-api" },
    { name = "pyyaml" },
    { name = "websocket-client" },
]
sdist = { url = "https://files.pythonhosted.org/packages/97/c5/f0098a9b1b72680b3682043227a628a08a7b5b9592fc98ea6efa0d638017/ops-2.21.1.tar.gz", hash = "sha256:4a8190420813ba37e7a0399d656008f99c79015d7f72e138bad7cb1ac403d0b0", size = 496427, upload-time = "2025-05-01T03:03:23.038Z" }
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 0s</sub>

### ✅ `bash`

**Check ops-scenario and ops-tracing versions in lock file**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep -B2 -A5 "^name = \"ops-scenario\"\|^name = \"ops-tracing\"" uv.lock | head -40

<details>
<summary>8 lines</summary>

```
[[package]]
name = "ops-scenario"
version = "7.21.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "ops" },
    { name = "pyyaml" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 8s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.0.0**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/releases/tag/3.0.0",
  "max_length": 15000
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

<sub>⏱️ 1m 8s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.1.0**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/releases/tag/3.1.0",
  "max_length": 10000
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

<sub>⏱️ 1m 14s</sub>

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

<sub>⏱️ 1m 13s</sub>

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

<sub>⏱️ 1m 20s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.4.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/releases/tag/3.4.0"
}
```

</details>

<details>
<summary>77 lines</summary>

```
Contents of https://github.com/canonical/operator/releases/tag/3.4.0:
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
```

</details>


---

<sub>⏱️ 1m 20s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/3.5.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/releases/tag/3.5.0"
}
```

</details>

<details>
<summary>31 lines</summary>

```
Contents of https://github.com/canonical/operator/releases/tag/3.5.0:
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
```

</details>


---

<sub>⏱️ 1m 33s</sub>

### 💬 Copilot

Now let me look at the charm source code and tests to understand what needs to change:

---

<sub>⏱️ 1m 33s</sub>

### ✅ `bash`

**Read charm.py**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat src/charm.py

<details>
<summary>8 lines</summary>

```
Output too large to read at once (26.3 KB). Saved to: /tmp/copilot-tool-output-1775063218850-d4yfb7.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

""
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 33s</sub>

### ✅ `bash`

**List unit test files**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && find tests/unit -name "*.py" | head -10

<details>
<summary>11 lines</summary>

```
tests/unit/test_external_url.py
tests/unit/test_remote_configuration_requirer.py
tests/unit/test_remote_configuration_provider.py
tests/unit/conftest.py
tests/unit/helpers.py
tests/unit/test_charm.py
tests/unit/test_consumer.py
tests/unit/test_push_config_to_workload_on_startup.py
tests/unit/test_self_scrape_jobs.py
tests/unit/test_server_scheme.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 41s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/src/charm.py

```
File too large to read at once (26.0 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


---

<sub>⏱️ 1m 42s</sub>

### ✅ `bash`

**Read test configuration files**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat tests/unit/conftest.py && cat tests/unit/helpers.py

<details>
<summary>102 lines</summary>

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
            Exec(["/usr/bin/amtool", "check-config", "/etc/alertmanager/alertmanager.yml"]),
        },
    )
    state = State(config={"config_file": ""}, containers=[container])
    peer_rel = PeerRelation("replicas")

    state = context.run(context.on.install(), state)

    state = dataclasses.replace(state, relations=[peer_rel])
    state = context.run(context.on.relation_created(peer_rel), state)

    if leader:
        state = dataclasses.replace(state, leader=True)
        state = context.run(context.on.leader_elected(), state)
    else:
        state = dataclasses.replace(state, leader=False)

    state = context.run(context.on.config_changed(), state)

    # state = state.with_can_connect("alertmanger")
    container = dataclasses.replace(container, can_connect=True)
    state = dataclasses.replace(state, containers=[container])
    state = context.run(context.on.pebble_ready(container), state)

    state = context.run(context.on.start(), state)

    return state


def add_relation_sequence(context: Context, state: State, relation: Relation):
    """Helper to simulate a relation-added sequence."""
    # TODO consider adding to scenario.sequences
    state_with_relation = dataclasses.replace(state, relations={*state.relations, relation})
    state_after_relation_created = context.run(context.on.relation_created(relation), state_with_relation)
    state_after_relation_joined = context.run(context.on.relation_joined(relation), state_after_relation_created)
    state_after_relation_changed = context.run(
        context.on.relation_changed(state_after_relation_joined.get_relation(relation.id)),
        state_after_relation_joined,
    )
    return state_after_relation_changed
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 46s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/src/charm.py (lines 1-100)

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

<sub>⏱️ 1m 47s</sub>

### ✅ `bash`

**Read test_charm.py start**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat tests/unit/test_charm.py | head -100

<details>
<summary>82 lines</summary>

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 57s</sub>

### 💬 Copilot

Now let me look at the full charm and remaining tests, then check the ops 2.22 changelog:

---

<sub>⏱️ 1m 57s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/src/charm.py (lines 100-300)

<details>
<summary>201 lines</summary>

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
```

</details>


---

<sub>⏱️ 1m 58s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/releases/tag/2.22.0**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/operator/releases/tag/2.22.0"
}
```

</details>

<details>
<summary>29 lines</summary>

```
Contents of https://github.com/canonical/operator/releases/tag/2.22.0:
## What's Changed

This release improves `ops[tracing]` by adding [Juju topology](https://discourse.charmhub.io/t/juju-topology-labels/8874) resource attributes, including `charm`, `juju_model`, and `juju_unit`.

We've also documented [how to access the Pebble metrics endpoint](https://ops.readthedocs.io/en/latest/howto/manage-metrics.html), which provides metrics for services and health checks in OpenMetrics format.

## Features

*   Add Juju topology labels in [#1744](https://github.com/canonical/operator/pull/1744)

## Fixes

*   Turn on databag access validation in `__init__` in [#1737](https://github.com/canonical/operator/pull/1737)
*   Allow event suffixes to appear in event names in `ops.testing` in [#1754](https://github.com/canonical/operator/pull/1754)

## Documentation

*   Document how to manage metrics in [#1692](https://github.com/canonical/operator/pull/1692)
*   Link to our docs from the top of our README in [#1710](https://github.com/canonical/operator/pull/1710)
*   Update code in K8s tutorial, with source in repo (part 1) in [#1719](https://github.com/canonical/operator/pull/1719)
*   Update links to juju.is/docs in [#1725](https://github.com/canonical/operator/pull/1725)
*   Fix link in breakpoint output, remove link from Harness error message in [#1726](https://github.com/canonical/operator/pull/1726)
*   Update Matrix channel name to Charm Tech in [#1740](https://github.com/canonical/operator/pull/1740)
*   Rename configurations to configuration in [#1746](https://github.com/canonical/operator/pull/1746)
*   Fix typos in code snippets by [@MattiaSarti](https://github.com/MattiaSarti) in [#1750](https://github.com/canonical/operator/pull/1750)

## CI

*   Add `ops[tracing]` integration tests in [#1686](https://github.com/canonical/operator/pull/1686)
*   Pin workflows by hash in [#1721](https://github.com/canonical/operator/pull/1721)
*   Disable alertmanager compatibility tests until upstream fix in [#1745](https://github.com/canonical/operator/pull/1745)
*   Remove explicit scopes and update HACKING.md in [#1748](https://github.com/canonical/operator/pull/1748)
*   Pin trusted workflows by tag in [#1752](https://github.com/canonical/operator/pull/1752)
*   Re-enable `alertmanager-k8s-operator` in observability charm tests in [#1753](https://github.com/canonical/operator/pull/1753)
*   Fix reporting to TIOBE after `ops[tracing]` addition in [#1755](https://github.com/canonical/operator/pull/1755)

## New Contributors

*   [@MattiaSarti](https://github.com/MattiaSarti) made their first contribution in [#1750](https://github.com/canonical/operator/pull/1750)

**Full Changelog**: [2.21.1...2.22.0](https://github.com/canonical/operator/compare/2.21.1...2.22.0)
```

</details>


---

<sub>⏱️ 2m 3s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/src/charm.py (lines 300-500)

<details>
<summary>201 lines</summary>

```
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
```

</details>


---

<sub>⏱️ 2m 4s</sub>

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

<sub>⏱️ 2m 23s</sub>

### 💬 Copilot

Let me look at more files:

---

<sub>⏱️ 2m 23s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/src/charm.py.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/src/charm.py (lines 500-650)

<details>
<summary>151 lines</summary>

```
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
```

</details>


---

<sub>⏱️ 2m 23s</sub>

### ✅ `bash`

**Read tox.ini and charmcraft.yaml**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat tox.ini && cat charmcraft.yaml | head -50

<details>
<summary>104 lines</summary>

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 37s</sub>

### 💬 Copilot

Let me read all remaining unit tests:

---

<sub>⏱️ 2m 37s</sub>

### ✅ `bash`

**Count lines in test files**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat tests/unit/test_charm.py | wc -l && wc -l tests/unit/*.py

<details>
<summary>15 lines</summary>

```
261
   45 tests/unit/conftest.py
   90 tests/unit/helpers.py
  154 tests/unit/test_alertmanager_client.py
   48 tests/unit/test_brute_isolated.py
  261 tests/unit/test_charm.py
  160 tests/unit/test_consumer.py
  122 tests/unit/test_external_url.py
  157 tests/unit/test_push_config_to_workload_on_startup.py
  174 tests/unit/test_remote_configuration_provider.py
  163 tests/unit/test_remote_configuration_requirer.py
   85 tests/unit/test_self_scrape_jobs.py
   97 tests/unit/test_server_scheme.py
 1556 total
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 37s</sub>

### ✅ `bash`

**Find Harness usage and deprecated features**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep -n "Harness\|charm_spec\|SIMULATE_CAN_CONNECT" tests/unit/*.py

<details>
<summary>22 lines</summary>

```
tests/unit/test_charm.py:12:from ops.testing import Harness
tests/unit/test_charm.py:17:ops.testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore
tests/unit/test_charm.py:29:        self.harness = Harness(AlertmanagerCharm)
tests/unit/test_charm.py:181:        self.harness = Harness(AlertmanagerCharm)
tests/unit/test_charm.py:214:        self.harness = Harness(AlertmanagerCharm)
tests/unit/test_consumer.py:12:from ops.testing import Harness
tests/unit/test_consumer.py:14:ops.testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore
tests/unit/test_consumer.py:60:        self.harness = Harness(SampleConsumerCharm, meta=SampleConsumerCharm.metadata_yaml)
tests/unit/test_external_url.py:13:from ops.testing import Harness
tests/unit/test_external_url.py:20:ops.testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore
tests/unit/test_external_url.py:32:        self.harness = Harness(AlertmanagerCharm)
tests/unit/test_push_config_to_workload_on_startup.py:16:from ops.testing import Harness
tests/unit/test_push_config_to_workload_on_startup.py:22:ops.testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore
tests/unit/test_push_config_to_workload_on_startup.py:40:        self.harness = Harness(AlertmanagerCharm)
tests/unit/test_push_config_to_workload_on_startup.py:121:        self.harness = Harness(AlertmanagerCharm)
tests/unit/test_remote_configuration_provider.py:21:testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore
tests/unit/test_remote_configuration_provider.py:87:        self.harness = testing.Harness(RemoteConfigurationProviderCharm, meta=METADATA)
tests/unit/test_remote_configuration_requirer.py:24:testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore
tests/unit/test_remote_configuration_requirer.py:52:        self.harness = testing.Harness(AlertmanagerCharm)
tests/unit/test_self_scrape_jobs.py:8:from ops.testing import Harness
tests/unit/test_self_scrape_jobs.py:22:        self.harness = Harness(AlertmanagerCharm)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 46s</sub>

### ✅ `bash`

**Check if Harness is still available**

$ python3 -c "from ops.testing import Harness; print('Harness available')" 2>&1

```
Harness available
<exited with exit code 0>
```


---

<sub>⏱️ 2m 46s</sub>

### ✅ `bash`

**Check testing module contents**

$ python3 -c "import ops.testing; print(dir(ops.testing))" 2>&1; python3 -c "import ops.testing; print(hasattr(ops.testing, 'SIMULATE_CAN_CONNECT'))" 2>&1

```
['ActionFailed', 'ActionOutput', 'ActiveStatus', 'Address', 'AnyJson', 'AppUnitOrName', 'BindAddress', 'BlockedStatus', 'CharmBase', 'CharmEvents', 'CharmMeta', 'CharmType', 'CheckInfo', 'CloudCredential', 'CloudSpec', 'Container', 'Context', 'DeferredEvent', 'ErrorStatus', 'Exec', 'ExecArgs', 'ExecHandler', 'ExecProcess', 'ExecResult', 'Harness', 'ICMPPort', 'JujuLogLine', 'MaintenanceStatus', 'Manager', 'Model', 'Mount', 'Network', 'Notice', 'PeerRelation', 'Port', 'RawDataBagContents', 'RawSecretRevisionContents', 'ReadableBuffer', 'Relation', 'RelationBase', 'RelationNotFoundError', 'RelationRole', 'Resource', 'Secret', 'State', 'Storage', 'StoredState', 'SubordinateRelation', 'TCPPort', 'UDPPort', 'UnitID', 'UnknownStatus', 'WaitingStatus', 'YAMLStringOrFile', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', '_compatibility_names', 'annotations', 'charm', 'errors', 'framework', 'layer_from_rockcraft', 'model', 'pebble', 'storage']
False
<exited with exit code 0>
```


---

<sub>⏱️ 2m 56s</sub>

### 💬 Copilot

Let me run the existing tests to understand the baseline:

---

<sub>⏱️ 2m 59s</sub>

### ✅ `bash`

**Run unit tests to see baseline failures**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && uv run --frozen --isolated --extra=dev python -m pytest tests/unit -x --tb=short -q 2>&1 | head -100

<details>
<summary>11 lines</summary>

```
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 110 packages in 48ms
/home/ubuntu/.cache/uv/builds-v0/.tmpmrXcjm/lib/python3.12/site-packages/paramiko/pkey.py:82: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  "cipher": algorithms.TripleDES,
/home/ubuntu/.cache/uv/builds-v0/.tmpmrXcjm/lib/python3.12/site-packages/paramiko/transport.py:253: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  "class": algorithms.TripleDES,
ImportError while loading conftest '/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/conftest.py'.
tests/unit/conftest.py:4: in <module>
    from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
E   ModuleNotFoundError: No module named 'charms'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 5s</sub>

### ❌ `bash`

**Run unit tests with proper PYTHONPATH**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && PYTHONPATH="$(pwd):$(pwd)/lib:$(pwd)/src" uv run --frozen --isolated --extra=dev python -m pytest tests/unit -x --tb=short -q 2>&1 | tail -50

```
Command blocked: contains dangerous shell expansion patterns (e.g., parameter transformation, indirect expansion, or nested command substitution) that could enable arbitrary code execution. Please rewrite the command without these expansion patterns.
```


---

<sub>⏱️ 3m 14s</sub>

### ✅ `bash`

**Run unit tests with tox env**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && uv run --frozen --isolated --extra=dev python -m pytest tests/unit -x --tb=short -q --import-mode=importlib 2>&1 | tail -50

<details>
<summary>11 lines</summary>

```
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 110 packages in 47ms
/home/ubuntu/.cache/uv/builds-v0/.tmpOA16dV/lib/python3.12/site-packages/paramiko/pkey.py:82: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  "cipher": algorithms.TripleDES,
/home/ubuntu/.cache/uv/builds-v0/.tmpOA16dV/lib/python3.12/site-packages/paramiko/transport.py:253: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  "class": algorithms.TripleDES,
ImportError while loading conftest '/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/conftest.py'.
tests/unit/conftest.py:4: in <module>
    from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
E   ModuleNotFoundError: No module named 'charms'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 15s</sub>

### ✅ `bash`

**Run unit tests via tox**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && tox -e unit 2>&1 | tail -60

<details>
<summary>53 lines</summary>

```
tests/unit/test_consumer.py::TestConsumer::test_cluster_updated_after_alertmanager_units_join
tests/unit/test_consumer.py::TestConsumer::test_relation_changed
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_consumer.py:60: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(SampleConsumerCharm, meta=SampleConsumerCharm.metadata_yaml)

tests/unit/test_push_config_to_workload_on_startup.py::TestPushConfigToWorkloadOnStartup::test_charm_blocks_on_connection_error
tests/unit/test_push_config_to_workload_on_startup.py::TestPushConfigToWorkloadOnStartup::test_single_unit_cluster
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_push_config_to_workload_on_startup.py:40: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_push_config_to_workload_on_startup.py::TestInvalidConfig::test_charm_blocks_on_invalid_config_changed
tests/unit/test_push_config_to_workload_on_startup.py::TestInvalidConfig::test_charm_blocks_on_invalid_config_on_startup
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_push_config_to_workload_on_startup.py:121: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_config_with_templates_updates_both_alertmanager_config_and_alertmanager_templates_in_the_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_config_without_templates_updates_only_alertmanager_config_in_the_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_empty_config_file_clears_relation_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_invalid_config_clears_relation_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_invalid_config_emits_remote_configuration_broken_event
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_remote_configuration_provider.py:87: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = testing.Harness(RemoteConfigurationProviderCharm, meta=METADATA)

tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_configs_available_from_both_relation_data_bag_and_charm_config_block_charm
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_invalid_config_pushed_to_the_relation_data_bag_does_not_update_alertmanager_config
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_templates_pushed_to_relation_data_bag_are_saved_to_templates_file_in_alertmanager
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_valid_config_pushed_to_relation_data_bag_updates_alertmanager_config
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_remote_configuration_requirer.py:52: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = testing.Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_no_peers
tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_self_scrape_jobs.py:22: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/.cache/uv/builds-v0/.tmpuQC9Uo/lib/python3.12/site-packages/ops/_private/harness.py:1112: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/1'.
    warnings.warn(

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/.cache/uv/builds-v0/.tmpuQC9Uo/lib/python3.12/site-packages/ops/_private/harness.py:1112: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/2'.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====== 57 passed, 3 skipped, 4 xfailed, 311 warnings in 106.71s (0:01:46) ======
unit: commands[1]> uv run --frozen --isolated --extra=dev coverage report
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 110 packages in 41ms
Name                                                                  Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------------------------------------
lib/charms/alertmanager_k8s/v0/alertmanager_remote_configuration.py     124     15     20      2    88%   52-54, 184, 228-229, 377, 385, 405-406, 417, 449-451, 471-472
lib/charms/alertmanager_k8s/v1/alertmanager_dispatch.py                  98      8     16      4    89%   114, 123-132, 222->exit, 233->232, 239-241, 245
src/alertmanager.py                                                     133     22     28     11    78%   41, 45, 129, 144, 152, 161, 169-170, 230, 240-241, 257, 265-266, 277-278, 283-284, 297, 324, 336-337
src/alertmanager_client.py                                              124     30     10      3    74%   55, 73-74, 84, 114, 121-122, 162-167, 193-202, 314-323, 345-354
src/charm.py                                                            270     39     50     10    83%   278, 324-329, 332, 335-339, 343-352, 358, 381-382, 414-416, 470-472, 482->499, 486-493, 506->512, 527-529, 536, 575, 593, 598-599, 635, 670
src/config_builder.py                                                    67      3     16      2    92%   73->75, 133-135
-----------------------------------------------------------------------------------------------------------------
TOTAL                                                                   816    117    140     32    83%
  unit: OK (111.01=setup[0.03]+cmd[110.71,0.26] seconds)
  congratulations :) (111.02 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 53s</sub>

### 💬 Copilot

Good - all 57 tests pass with only deprecation warnings. Now let me read the test files that need to be migrated:

---

<sub>⏱️ 5m 54s</sub>

### ✅ `bash`

**Read test_charm.py**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat tests/unit/test_charm.py

<details>
<summary>213 lines</summary>

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
        # now it (correctly) raises pebble.PathError as per the real system,
        # so catch both.
        # TODO: update to just pebble.PathError when ops 2.1 is released.
        with self.assertRaises((pebble.PathError, FileNotFoundError)):
            self.harness.charm.container.pull(self.harness.charm._templates_path)

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    @patch.object(AlertmanagerCharm, "_update_ca_certs", lambda *a, **kw: None)
    def test_templates_section_added_if_user_provided_templates(self, *unused):
        new_config = yaml.dump({"route": {"group_by": ["alertname", "juju_model"]}})
        self.harness.update_config({"config_file": new_config})
        templates = '{{ define "some.tmpl.variable" }}whatever it is{{ end}}'
        self.harness.update_config({"templates_file": templates})
        updated_templates = self.harness.charm.container.pull(self.harness.charm._templates_path)
        self.assertEqual(templates, updated_templates.read())

        updated_config = yaml.safe_load(
            self.harness.charm.container.pull(self.harness.charm._config_path)
        )
        self.assertEqual(updated_config["templates"], [f"{self.harness.charm._templates_path}"])


class TestWithoutInitialHooks(unittest.TestCase):
    container_name: str = "alertmanager"

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    @patch("lightkube.core.client.GenericSyncClient")
    def setUp(self, *unused):
        self.harness = Harness(AlertmanagerCharm)
        self.addCleanup(self.harness.cleanup)

        self.relation_id = self.harness.add_relation("alerting", "otherapp")
        self.harness.add_relation_unit(self.relation_id, "otherapp/0")
        self.harness.set_leader(True)

        self.harness.begin()
        self.harness.add_relation("replicas", "alertmanager")

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    @patch.object(WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0"))
    def test_unit_status_around_pebble_ready(self, *unused):
        # before pebble_ready, status should be "maintenance"
        self.assertIsInstance(self.harness.charm.unit.status, ops.model.MaintenanceStatus)

        # after pebble_ready, status should be "active"
        self.harness.container_pebble_ready(self.container_name)
        self.assertIsInstance(self.harness.charm.unit.status, ops.model.ActiveStatus)

        self.assertEqual(self.harness.model.unit.name, "alertmanager-k8s/0")


class TestActions(unittest.TestCase):
    container_name: str = "alertmanager"

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @patch("socket.getfqdn", new=lambda *args: "fqdn")
    @k8s_resource_multipatch
    @patch("lightkube.core.client.GenericSyncClient")
    @patch.object(WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0"))
    def setUp(self, *unused):
        self.harness = Harness(AlertmanagerCharm)
        self.addCleanup(self.harness.cleanup)

        self.harness.set_leader(True)
        self.harness.begin_with_initial_hooks()

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    @patch.object(WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0"))
    def test_show_config(self, *_unused):
        tls_paths = {
            self.harness.charm._server_cert_path,
            self.harness.charm._ca_cert_path,
            self.harness.charm._key_path,
        }

        # GIVEN an isolated charm (see setUp, decorator)
        # WHEN the "show-config" action runs
        results = self.harness.run_action("show-config").results

        # THEN the result is a dict some keys
        self.assertEqual(results.keys(), {"path", "content", "configs"})

        # AND configs DOES NOT contain cert-related entries
        # results.configs is a list of dicts, [{"path": ..., "content": ...}, {...}, ...].
        paths_rendered = {d["path"] for d in yaml.safe_load(results["configs"])}
        for filepath in tls_paths:
            self.assertNotIn(filepath, paths_rendered)

        # AND GIVEN a tls relation is in place
        rel_id = self.harness.add_relation("certificates", "ca")
        self.harness.add_relation_unit(rel_id, "ca/0")
        # AND cert files are on disk
        for filepath in tls_paths:
            self.harness.model.unit.get_container("alertmanager").push(
                filepath, "test", make_dirs=True
            )

        # WHEN the "show-config" action runs
        results = self.harness.run_action("show-config").results

        # THEN the result is a dict with the same keys as before
        self.assertEqual(results.keys(), {"path", "content", "configs"})

        # AND configs contains cert-related entries
        paths_rendered = {d["path"] for d in yaml.safe_load(results["configs"])}
        for filepath in tls_paths:
            self.assertIn(filepath, paths_rendered)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 54s</sub>

### ✅ `bash`

**Read test_external_url.py**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat tests/unit/test_external_url.py

<details>
<summary>100 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import unittest
from typing import Optional
from unittest.mock import patch

import ops
import yaml
from helpers import cli_arg, k8s_resource_multipatch
from ops.testing import Harness

from alertmanager import WorkloadManager
from charm import AlertmanagerCharm

logger = logging.getLogger(__name__)

ops.testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore
CONTAINER_NAME = "alertmanager"
SERVICE_NAME = AlertmanagerCharm._service_name


class TestExternalUrl(unittest.TestCase):
    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @patch("socket.getfqdn", new=lambda *args: "fqdn")
    @k8s_resource_multipatch
    @patch("lightkube.core.client.GenericSyncClient")
    @patch.object(WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0"))
    def setUp(self, *unused):
        self.harness = Harness(AlertmanagerCharm)
        self.harness.set_model_name(self.__class__.__name__)
        self.addCleanup(self.harness.cleanup)
        self.harness.set_leader(True)

        # Peer relation
        self.app_name = "alertmanager-k8s"
        self.peer_rel_id = self.harness.add_relation("replicas", self.app_name)

        # Regular relation
        self.rel_id = self.harness.add_relation("alerting", "otherapp")
        self.harness.add_relation_unit(self.rel_id, "otherapp/0")

        self.harness.begin_with_initial_hooks()
        self.fqdn_url = f"http://fqdn:{self.harness.charm.api_port}"

    def get_url_cli_arg(self) -> Optional[str]:
        plan = self.harness.get_container_pebble_plan(CONTAINER_NAME)
        return cli_arg(plan, "--web.external-url")

    def get_cluster_args(self):
        plan = self.harness.get_container_pebble_plan(CONTAINER_NAME).to_dict()
        args = plan.get("services", {}).get(SERVICE_NAME, {}).get("command", "").split()
        cluster_args = filter(lambda s: s.startswith("--cluster.peer="), args)
        cluster_args = sorted((s.split("=")[1] for s in cluster_args))
        return cluster_args

    def is_service_running(self) -> bool:
        # service = plan.services.get(self.harness.charm._service_name)
        service = self.harness.model.unit.get_container(CONTAINER_NAME).get_service(SERVICE_NAME)
        return service.is_running()

    @unittest.skip("https://github.com/canonical/operator/issues/736")
    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @patch("socket.getfqdn", new=lambda *args: "fqdn")
    @k8s_resource_multipatch
    def test_traefik_overrides_fqdn(self):
        """The config option for external url must override all other external urls."""
        # GIVEN a charm with the fqdn as its external URL
        self.assertEqual(self.get_url_cli_arg(), self.fqdn_url)
        self.assertTrue(self.is_service_running())
        self.assertEqual(self.harness.charm._external_url, self.fqdn_url)

        # WHEN a relation with traefik is formed but ingress isn't ready
        rel_id = self.harness.add_relation("ingress", "traefik-app")
        self.harness.add_relation_unit(rel_id, "traefik-app/0")

        # THEN there is no change to the cli arg
        self.assertEqual(self.get_url_cli_arg(), self.fqdn_url)
        self.assertTrue(self.is_service_running())
        self.assertEqual(self.harness.charm._external_url, self.fqdn_url)

        # WHEN ingress becomes available
        external_url_ingress = "http://foo.bar.ingress:80/path/to/mdl-alertmanager-k8s"
        app_data = {"ingress": yaml.safe_dump({"url": external_url_ingress})}
        self.harness.update_relation_data(rel_id, "traefik-app", app_data)

        # THEN the external url from the ingress relation overrides the fqdn
        self.assertEqual(self.get_url_cli_arg(), external_url_ingress)
        self.assertTrue(self.is_service_running())

        # NOTE intentionally not emptying out relation data manually
        # FIXME: figure out if we do or do not need to manually empty out relation-data
        #   before relation-broken is emitted.
        #   https://github.com/canonical/operator/issues/888
        app_data = {"ingress": ""}
        self.harness.update_relation_data(rel_id, "traefik-app", app_data)

        # AND WHEN the traefik relation is removed
        self.harness.remove_relation_unit(rel_id, "traefik-app/0")
        self.harness.remove_relation(rel_id)

        # THEN the fqdn is used as external url
        self.assertEqual(self.get_url_cli_arg(), self.fqdn_url)

    @unittest.skip("https://github.com/canonical/operator/issues/736")
    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @patch("socket.getfqdn", new=lambda *args: "fqdn-0")
    @k8s_resource_multipatch
    def test_cluster_addresses(self, *_):
        # GIVEN an alertmanager charm with 3 units in total
        for u in [1, 2]:
            unit_name = self.app_name + f"/{u}"
            self.harness.add_relation_unit(self.peer_rel_id, unit_name)
            self.harness.update_relation_data(
                self.peer_rel_id, unit_name, {"private_address": f"http://fqdn-{u}:9093"}
            )

        # THEN the `--cluster.peer` args are made up of the hostname and HA port
        cluster_args = self.get_cluster_args()
        self.assertEqual(cluster_args, ["fqdn-1:9094", "fqdn-2:9094"])  # cluster is on ha-port
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 1s</sub>

### ✅ `bash`

**Read remaining Harness tests**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat tests/unit/test_push_config_to_workload_on_startup.py && cat tests/unit/test_self_scrape_jobs.py

<details>
<summary>197 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import unittest
from unittest.mock import patch

import hypothesis.strategies as st
import ops
import validators
import yaml
from helpers import k8s_resource_multipatch
from hypothesis import given
from ops.model import ActiveStatus, BlockedStatus
from ops.testing import Harness

from alertmanager import WorkloadManager
from charm import AlertmanagerCharm

logger = logging.getLogger(__name__)
ops.testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore
CONTAINER_NAME = "alertmanager"


@patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("0.0.0", ""))
@patch("subprocess.run")
class TestPushConfigToWorkloadOnStartup(unittest.TestCase):
    """Feature: Push config to workload on startup.

    Background: Charm starts up with initial hooks.
    """

    @patch("subprocess.run")
    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("0.0.0", ""))
    @k8s_resource_multipatch
    @patch("lightkube.core.client.GenericSyncClient")
    @patch.object(WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0"))
    def setUp(self, *_):
        self.harness = Harness(AlertmanagerCharm)
        self.addCleanup(self.harness.cleanup)

        # self.harness.charm.app.name does not exist before .begin()
        # https://github.com/canonical/operator/issues/675
        self.app_name = "alertmanager-k8s"
        self.peer_rel_id = self.harness.add_relation("replicas", self.app_name)
        self.harness.begin_with_initial_hooks()

    @given(st.booleans())
    def test_single_unit_cluster(self, is_leader, _):
        """Scenario: Current unit is the only unit present."""
        # WHEN only one unit is
        self.assertEqual(self.harness.model.app.planned_units(), 1)
        self.harness.set_leader(is_leader)

        # THEN amtool config is rendered
        amtool_config = yaml.safe_load(
            self.harness.charm.container.pull(self.harness.charm._amtool_config_path)
        )
        self.assertTrue(validators.url(amtool_config["alertmanager.url"], simple_host=True))

        # AND alertmanager config is rendered
        am_config = yaml.safe_load(
            self.harness.charm.container.pull(self.harness.charm._config_path)
        )
        self.assertGreaterEqual(am_config.keys(), {"global", "route", "receivers"})

        # AND path to config file is part of pebble layer command
        command = (
            self.harness.get_container_pebble_plan(self.harness.charm._container_name)
            .services[self.harness.charm._service_name]
            .command
        )
        self.assertIn(f"--config.file={self.harness.charm._config_path}", command)

        # AND peer clusters cli arg is not present in pebble layer command
        self.assertNotIn("--cluster.peer=", command)

    @unittest.skip("https://github.com/canonical/operator/issues/736")
    @k8s_resource_multipatch
    def test_multi_unit_cluster(self, *_):
        """Scenario: Current unit is a part of a multi-unit cluster."""
        self.harness.set_leader(False)

        # WHEN multiple units are present
        num_units = 3
        for i in range(1, num_units):
            self.harness.add_relation_unit(self.peer_rel_id, f"{self.app_name}/{i}")
            self.harness.update_relation_data(
                self.peer_rel_id,
                f"{self.app_name}/{i}",
                {"private_address": f"http://fqdn-{i}"},
            )

        self.assertEqual(self.harness.model.app.planned_units(), num_units)

        # THEN peer clusters cli arg is present in pebble layer command
        command = (
            self.harness.get_container_pebble_plan(self.harness.charm._container_name)
            .services[self.harness.charm._service_name]
            .command
        )
        self.assertIn("--cluster.peer=", command)

    def test_charm_blocks_on_connection_error(self, *_):
        self.assertIsInstance(self.harness.charm.unit.status, ActiveStatus)
        self.harness.set_can_connect(CONTAINER_NAME, False)
        self.harness.update_config({"templates_file": "doesn't matter"})
        self.assertNotIsInstance(self.harness.charm.unit.status, ActiveStatus)


@patch("subprocess.run")
class TestInvalidConfig(unittest.TestCase):
    """Feature: Charm must block when invalid config is provided.

    Background: alertmanager exits when config is invalid, so this must be guarded against,
    otherwise pebble will keep trying to restart it, resulting in an idle crash-loop.
    """

    def setUp(self):
        self.harness = Harness(AlertmanagerCharm)
        self.addCleanup(self.harness.cleanup)

        self.harness.handle_exec("alertmanager", ["update-ca-certificates", "--fresh"], result="")

    @k8s_resource_multipatch
    @patch("lightkube.core.client.GenericSyncClient")
    @patch.object(WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0"))
    def test_charm_blocks_on_invalid_config_on_startup(self, *_):
        # GIVEN an invalid config file
        self.harness.update_config({"config_file": "templates: [wrong]"})

        # WHEN the charm starts
        self.harness.begin_with_initial_hooks()

        # THEN the charm goes into blocked status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

    @k8s_resource_multipatch
    @patch("lightkube.core.client.GenericSyncClient")
    @patch.object(WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0"))
    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("0.0.0", ""))
    def test_charm_blocks_on_invalid_config_changed(self, *_):
        # GIVEN a valid configuration
        self.harness.update_config({"config_file": "templates: []"})

        # WHEN the charm starts
        self.harness.begin_with_initial_hooks()

        # THEN the charm goes into active status
        self.assertIsInstance(self.harness.charm.unit.status, ActiveStatus)

        # AND WHEN the config is updated and invalid (mocked below)
        self.harness.update_config({"config_file": "templates: [wrong]"})

        # THEN the charm goes into blocked status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)
#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
import unittest
from unittest.mock import PropertyMock, patch

from helpers import k8s_resource_multipatch
from ops.testing import Harness

from alertmanager import WorkloadManager
from charm import AlertmanagerCharm


class TestWithInitialHooks(unittest.TestCase):
    container_name: str = "alertmanager"

    @patch("lightkube.core.client.GenericSyncClient")
    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    @patch.object(WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0"))
    def setUp(self, *unused):
        self.harness = Harness(AlertmanagerCharm)
        self.addCleanup(self.harness.cleanup)

        self.harness.set_leader(True)
        self.app_name = "am"
        # Create the peer relation before running harness.begin_with_initial_hooks(), because
        # otherwise it will create it for you and we don't know the rel_id
        self.peer_rel_id = self.harness.add_relation("replicas", self.app_name)

        self.harness.begin_with_initial_hooks()

    @patch.object(AlertmanagerCharm, "_internal_url", new_callable=PropertyMock)
    @patch.object(AlertmanagerCharm, "_scheme", new_callable=PropertyMock)
    def test_self_scraping_job_with_no_peers(self, _mock_scheme, _mock_internal_url):
        scheme = "https"
        _mock_scheme.return_value = scheme
        url_no_scheme = f"test-internal.url:{self.harness.charm._ports.api}"
        _mock_internal_url.return_value = f"{scheme}://{url_no_scheme}"
        jobs_expected = [
            {
                "metrics_path": "/metrics",
                "scheme": scheme,
                "static_configs": [{"targets": [url_no_scheme]}],
            }
        ]

        jobs = self.harness.charm.self_scraping_job
        self.assertEqual(jobs, jobs_expected)

    @patch.object(WorkloadManager, "check_config")
    @patch.object(AlertmanagerCharm, "_internal_url", new_callable=PropertyMock)
    @patch.object(AlertmanagerCharm, "_scheme", new_callable=PropertyMock)
    def test_self_scraping_job_with_peers(
        self, _mock_scheme, _mock_internal_url, _mock_check_config
    ):
        scheme = "https"
        _mock_scheme.return_value = scheme

        targets = [
            f"test-internal-0.url:{self.harness.charm._ports.api}",
            f"test-internal-1.url:{self.harness.charm._ports.api}",
            f"test-internal-2.url:{self.harness.charm._ports.api}",
        ]
        metrics_path = "/metrics"
        _mock_internal_url.return_value = f"{scheme}://{targets[0]}"

        jobs_expected = [
            {
                "metrics_path": metrics_path,
                "scheme": scheme,
                "static_configs": [{"targets": targets}],
            }
        ]

        # Add peers
        for i, target in enumerate(targets[1:], 1):
            unit_name = f"{self.app_name}/{i}"
            self.harness.add_relation_unit(self.peer_rel_id, unit_name)
            self.harness.update_relation_data(
                self.peer_rel_id, unit_name, {"private_address": f"{scheme}://{target}"}
            )

        jobs = self.harness.charm.self_scraping_job
        self.assertEqual(jobs_expected, jobs)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 9s</sub>

### ✅ `bash`

**Read consumer and remote config tests**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat tests/unit/test_consumer.py && cat tests/unit/test_remote_configuration_requirer.py | head -100

<details>
<summary>215 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

import textwrap
import unittest

import ops
from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerConsumer
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.testing import Harness

ops.testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore


class SampleConsumerCharm(CharmBase):
    """Mimic bare functionality of AlertmanagerCharm needed to test the consumer."""

    # define custom metadata - without this the harness would parse the metadata.yaml in this repo,
    # which would result in expressions like self.harness.model.app.name to return
    # "alertmanager-k8s", which is not what we want in a consumer test
    metadata_yaml = textwrap.dedent(
        """
        name: SampleConsumerCharm
        containers:
          consumer-charm:
            resource: consumer-charm-image
        resources:
          consumer-charm-image:
            type: oci-image
        requires:
          alerting:
            interface: alertmanager_dispatch
        peers:
          replicas:
            interface: consumer_charm_replica
        """
    )
    _stored = StoredState()

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        # relation name must match metadata
        self.alertmanager_lib = AlertmanagerConsumer(self, relation_name="alerting")

        self.framework.observe(
            self.alertmanager_lib.on.cluster_changed, self._on_alertmanager_cluster_changed
        )

        self._stored.set_default(alertmanagers=[], cluster_changed_emitted=0)

    def _on_alertmanager_cluster_changed(self, _):
        self._stored.cluster_changed_emitted += 1
        self._stored.alertmanagers = self.alertmanager_lib.get_cluster_info()


class TestConsumer(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(SampleConsumerCharm, meta=SampleConsumerCharm.metadata_yaml)
        self.addCleanup(self.harness.cleanup)
        self.harness.set_leader(True)
        self.harness.begin_with_initial_hooks()

    def _relate_to_alertmanager(self) -> int:
        """Create relation between 'this app' and a hypothetical (remote) alertmanager."""
        rel_id = self.harness.add_relation(relation_name="alerting", remote_app="am")
        return rel_id

    def _add_alertmanager_units(self, rel_id: int, num_units: int, start_with=0):
        for i in range(start_with, start_with + num_units):
            remote_unit_name = f"am/{i}"
            self.harness.add_relation_unit(rel_id, remote_unit_name)
            self.harness.update_relation_data(
                rel_id, remote_unit_name, {"public_address": f"10.20.30.{i}"}
            )

        return rel_id

    def test_cluster_updated_after_alertmanager_units_join(self):
        # before
        self.assertEqual(set(), self.harness.charm.alertmanager_lib.get_cluster_info())
        num_events = self.harness.charm._stored.cluster_changed_emitted

        # add relation
        rel_id = self._relate_to_alertmanager()
        self._add_alertmanager_units(rel_id, num_units=2)

        # after
        self.assertGreater(self.harness.charm._stored.cluster_changed_emitted, num_events)
        self.assertSetEqual(
            {"http://10.20.30.0", "http://10.20.30.1"},
            self.harness.charm.alertmanager_lib.get_cluster_info(),
        )

        num_events = self.harness.charm._stored.cluster_changed_emitted

        # add another unit
        self._add_alertmanager_units(rel_id, num_units=1, start_with=2)
        self.assertGreater(self.harness.charm._stored.cluster_changed_emitted, num_events)
        self.assertSetEqual(
            {"http://10.20.30.0", "http://10.20.30.1", "http://10.20.30.2"},
            self.harness.charm.alertmanager_lib.get_cluster_info(),
        )

    def test_cluster_updated_after_alertmanager_unit_leaves(self):
        num_events = self.harness.charm._stored.cluster_changed_emitted

        # add relation
        rel_id = self._relate_to_alertmanager()
        self._add_alertmanager_units(rel_id, num_units=4)
        self.assertGreater(self.harness.charm._stored.cluster_changed_emitted, num_events)
        before = self.harness.charm.alertmanager_lib.get_cluster_info()
        self.assertEqual(len(before), 4)

        num_events = self.harness.charm._stored.cluster_changed_emitted

        # remove alertmanager units
        self.harness.remove_relation_unit(rel_id, "am/3")
        self.harness.remove_relation_unit(rel_id, "am/2")
        self.assertGreater(self.harness.charm._stored.cluster_changed_emitted, num_events)
        after = self.harness.charm.alertmanager_lib.get_cluster_info()
        self.assertSetEqual(after, {"http://10.20.30.0", "http://10.20.30.1"})

        num_events = self.harness.charm._stored.cluster_changed_emitted

        # remove all remaining units
        self.harness.remove_relation_unit(rel_id, "am/1")
        self.harness.remove_relation_unit(rel_id, "am/0")
        self.assertGreater(self.harness.charm._stored.cluster_changed_emitted, num_events)
        after = self.harness.charm.alertmanager_lib.get_cluster_info()
        self.assertGreater(self.harness.charm._stored.cluster_changed_emitted, num_events)
        self.assertSetEqual(after, set())

    def test_cluster_is_empty_after_relation_breaks(self):
        # add relation
        rel_id = self._relate_to_alertmanager()
        self._add_alertmanager_units(rel_id, num_units=4)
        before = self.harness.charm.alertmanager_lib.get_cluster_info()
        self.assertEqual(len(before), 4)

        num_events = self.harness.charm._stored.cluster_changed_emitted

        # remove relation
        self.harness.remove_relation(rel_id)
        after = self.harness.charm.alertmanager_lib.get_cluster_info()
        self.assertGreater(self.harness.charm._stored.cluster_changed_emitted, num_events)
        self.assertSetEqual(set(), after)

    def test_relation_changed(self):
        # add relation
        rel_id = self._relate_to_alertmanager()
        self._add_alertmanager_units(rel_id, num_units=2)

        # update remote unit's relation data (emulates upgrade-charm)
        self.harness.update_relation_data(rel_id, "am/1", {"public_address": "90.80.70.60"})
        self.assertSetEqual(
            {"http://10.20.30.0", "http://90.80.70.60"},
            self.harness.charm.alertmanager_lib.get_cluster_info(),
        )
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import json
import logging
import unittest
from typing import cast
from unittest.mock import patch

import yaml
from charms.alertmanager_k8s.v0.alertmanager_remote_configuration import (
    DEFAULT_RELATION_NAME,
)
from deepdiff import DeepDiff  # type: ignore[import]
from helpers import k8s_resource_multipatch
from ops import testing
from ops.model import BlockedStatus

from alertmanager import WorkloadManager
from charm import AlertmanagerCharm

logger = logging.getLogger(__name__)

testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore

TEST_ALERTMANAGER_CONFIG_FILE = "/test/rules/dir/config_file.yml"
TEST_ALERTMANAGER_DEFAULT_CONFIG = """route:
  receiver: placeholder
receivers:
- name: placeholder
"""
TEST_ALERTMANAGER_REMOTE_CONFIG = """receivers:
- name: test_receiver
route:
  receiver: test_receiver
  group_by:
  - alertname
  group_wait: 1234s
  group_interval: 4321s
  repeat_interval: 1111h
"""


@patch("subprocess.run")
class TestAlertmanagerRemoteConfigurationRequirer(unittest.TestCase):
    @patch("subprocess.run")
    @patch("lightkube.core.client.GenericSyncClient")
    @patch.object(AlertmanagerCharm, "_update_ca_certs", lambda *a, **kw: None)
    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    def setUp(self, *_) -> None:
        self.harness = testing.Harness(AlertmanagerCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.set_leader(True)

        self.harness.handle_exec("alertmanager", ["update-ca-certificates", "--fresh"], result="")
        self.harness.handle_exec(
            "alertmanager",
            [WorkloadManager._amtool_path, "check-config", AlertmanagerCharm._config_path],
            result="",
        )

        # TODO: Once we're on ops 2.0.0+ this can be removed as begin_with_initial_hooks()
        # now does it.
        self.harness.set_can_connect("alertmanager", True)

        # In ops 2.0.0+, we need to mock the version, as begin_with_initial_hooks() now triggers
        # pebble-ready, which attempts to obtain the workload version.
        patcher = patch.object(
            WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0")
        )
        self.mock_version = patcher.start()
        self.addCleanup(patcher.stop)

        self.harness.begin_with_initial_hooks()

        self.relation_id = self.harness.add_relation(
            DEFAULT_RELATION_NAME, "remote-config-provider"
        )
        self.harness.add_relation_unit(self.relation_id, "remote-config-provider/0")

    @k8s_resource_multipatch
    def test_valid_config_pushed_to_relation_data_bag_updates_alertmanager_config(
        self,
        *_,
    ):
        expected_config = remote_config = yaml.safe_load(TEST_ALERTMANAGER_REMOTE_CONFIG)
        # add juju topology to "group_by"
        route = cast(dict, expected_config.get("route", {}))
        route["group_by"] = list(
            set(route.get("group_by", [])).union(
                ["juju_application", "juju_model", "juju_model_uuid"]
            )
        )
        expected_config["route"] = route

        self.harness.update_relation_data(
            relation_id=self.relation_id,
            app_or_unit="remote-config-provider",
            key_values={"alertmanager_config": json.dumps(remote_config)},
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 34s</sub>

### ✅ `bash`

**Check git status and current branch**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && git --no-pager status && git --no-pager branch

```
HEAD detached at 6101e73
nothing to commit, working tree clean
* (HEAD detached at 6101e73)
  main
<exited with exit code 0>
```


---

<sub>⏱️ 6m 34s</sub>

### ✅ `bash`

**Read test_remote_configuration_provider.py**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat tests/unit/test_remote_configuration_provider.py

<details>
<summary>141 lines</summary>

```
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import json
import logging
import unittest
from unittest.mock import PropertyMock, patch

import yaml
from charms.alertmanager_k8s.v0.alertmanager_remote_configuration import (
    DEFAULT_RELATION_NAME,
    ConfigReadError,
    RemoteConfigurationProvider,
)
from ops import testing
from ops.charm import CharmBase, CharmEvents
from ops.framework import EventBase, EventSource, StoredState

logger = logging.getLogger(__name__)

testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore

TEST_APP_NAME = "provider-tester"
METADATA = f"""
name: {TEST_APP_NAME}
provides:
  {DEFAULT_RELATION_NAME}:
    interface: alertmanager_remote_configuration
"""
TEST_ALERTMANAGER_CONFIG_WITHOUT_TEMPLATES_FILE_PATH = "./tests/unit/test_config/alertmanager.yml"
TEST_ALERTMANAGER_CONFIG_WITH_TEMPLATES_FILE_PATH = (
    "./tests/unit/test_config/alertmanager_with_templates.yml"
)
TEST_ALERTMANAGER_INVALID_CONFIG_FILE_PATH = "./tests/unit/test_config/alertmanager_invalid.yml"
TEST_ALERTMANAGER_TEMPLATES_FILE_PATH = "./tests/unit/test_config/test_templates.tmpl"
TESTER_CHARM = "test_remote_configuration_provider.RemoteConfigurationProviderCharm"


class AlertmanagerConfigFileChangedEvent(EventBase):
    pass


class AlertmanagerConfigFileChangedCharmEvents(CharmEvents):
    alertmanager_config_file_changed = EventSource(AlertmanagerConfigFileChangedEvent)


class RemoteConfigurationProviderCharm(CharmBase):
    ALERTMANAGER_CONFIG_FILE = TEST_ALERTMANAGER_CONFIG_WITHOUT_TEMPLATES_FILE_PATH

    on = AlertmanagerConfigFileChangedCharmEvents()  # pyright: ignore
    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self._stored.set_default(configuration_broken_emitted=0)

        alertmanager_config = RemoteConfigurationProvider.load_config_file(
            self.ALERTMANAGER_CONFIG_FILE
        )
        self.remote_configuration_provider = RemoteConfigurationProvider(
            charm=self,
            alertmanager_config=alertmanager_config,
            relation_name=DEFAULT_RELATION_NAME,
        )

        self.framework.observe(self.on.alertmanager_config_file_changed, self._update_config)
        self.framework.observe(
            self.remote_configuration_provider.on.configuration_broken,
            self._on_configuration_broken,
        )

    def _update_config(self, _):
        try:
            alertmanager_config = RemoteConfigurationProvider.load_config_file(
                self.ALERTMANAGER_CONFIG_FILE
            )
            self.remote_configuration_provider.update_relation_data_bag(alertmanager_config)
        except ConfigReadError:
            logger.warning("Error reading Alertmanager config file.")

    def _on_configuration_broken(self, _):
        self._stored.configuration_broken_emitted += 1


class TestAlertmanagerRemoteConfigurationProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = testing.Harness(RemoteConfigurationProviderCharm, meta=METADATA)
        self.addCleanup(self.harness.cleanup)
        self.harness.set_leader(True)
        self.harness.begin_with_initial_hooks()

    def test_config_without_templates_updates_only_alertmanager_config_in_the_data_bag(self):
        with open(TEST_ALERTMANAGER_CONFIG_WITHOUT_TEMPLATES_FILE_PATH, "r") as config_yaml:
            expected_config = yaml.safe_load(config_yaml)

        relation_id = self.harness.add_relation(DEFAULT_RELATION_NAME, "requirer")
        self.harness.add_relation_unit(relation_id, "requirer/0")

        self.assertEqual(
            json.loads(
                self.harness.get_relation_data(relation_id, TEST_APP_NAME)["alertmanager_config"]
            ),
            expected_config,
        )
        self.assertEqual(
            json.loads(
                self.harness.get_relation_data(relation_id, TEST_APP_NAME)[
                    "alertmanager_templates"
                ]
            ),
            [],
        )

    @patch(f"{TESTER_CHARM}.ALERTMANAGER_CONFIG_FILE", new_callable=PropertyMock)
    def test_config_with_templates_updates_both_alertmanager_config_and_alertmanager_templates_in_the_data_bag(  # noqa: E501
        self, patched_alertmanager_config_file
    ):
        patched_alertmanager_config_file.return_value = (
            TEST_ALERTMANAGER_CONFIG_WITH_TEMPLATES_FILE_PATH
        )
        with open(TEST_ALERTMANAGER_TEMPLATES_FILE_PATH, "r") as templates_file:
            expected_templates = templates_file.readlines()
        relation_id = self.harness.add_relation(DEFAULT_RELATION_NAME, "requirer")
        self.harness.add_relation_unit(relation_id, "requirer/0")

        self.harness.charm.on.alertmanager_config_file_changed.emit()

        self.assertEqual(
            json.loads(
                self.harness.get_relation_data(relation_id, TEST_APP_NAME)[
                    "alertmanager_templates"
                ]
            ),
            expected_templates,
        )

    @patch(f"{TESTER_CHARM}.ALERTMANAGER_CONFIG_FILE", new_callable=PropertyMock)
    def test_invalid_config_emits_remote_configuration_broken_event(
        self, patched_alertmanager_config_file
    ):
        num_events = self.harness.charm._stored.configuration_broken_emitted
        patched_alertmanager_config_file.return_value = TEST_ALERTMANAGER_INVALID_CONFIG_FILE_PATH
        relation_id = self.harness.add_relation(DEFAULT_RELATION_NAME, "requirer")
        self.harness.add_relation_unit(relation_id, "requirer/0")

        self.harness.charm.on.alertmanager_config_file_changed.emit()

        self.assertGreater(
            self.harness.charm._stored.configuration_broken_emitted,
            num_events,
        )

    @patch(f"{TESTER_CHARM}.ALERTMANAGER_CONFIG_FILE", new_callable=PropertyMock)
    def test_invalid_config_clears_relation_data_bag(self, patched_alertmanager_config_file):
        patched_alertmanager_config_file.return_value = TEST_ALERTMANAGER_INVALID_CONFIG_FILE_PATH
        relation_id = self.harness.add_relation(DEFAULT_RELATION_NAME, "requirer")
        self.harness.add_relation_unit(relation_id, "requirer/0")

        self.harness.charm.on.alertmanager_config_file_changed.emit()

        with self.assertRaises(KeyError):
            _ = self.harness.get_relation_data(relation_id, TEST_APP_NAME)["alertmanager_config"]

    @patch(f"{TESTER_CHARM}.ALERTMANAGER_CONFIG_FILE", new_callable=PropertyMock)
    def test_empty_config_file_clears_relation_data_bag(self, patched_alertmanager_config_file):
        test_config_file = "./tests/unit/test_config/alertmanager_empty.yml"
        patched_alertmanager_config_file.return_value = test_config_file
        relation_id = self.harness.add_relation(DEFAULT_RELATION_NAME, "requirer")
        self.harness.add_relation_unit(relation_id, "requirer/0")

        self.harness.charm.on.alertmanager_config_file_changed.emit()

        with self.assertRaises(KeyError):
            _ = self.harness.get_relation_data(relation_id, TEST_APP_NAME)["alertmanager_config"]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 53s</sub>

### 💬 Copilot

Let me look at the existing Context-based tests to understand the patterns:

---

<sub>⏱️ 6m 53s</sub>

### ✅ `bash`

**Read existing Context-based tests**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat tests/unit/test_brute_isolated.py && cat tests/unit/test_server_scheme.py | head -80

<details>
<summary>102 lines</summary>

```
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest
from helpers import add_relation_sequence, begin_with_initial_hooks_isolated
from ops.testing import Context, Relation, State

"""Some brute-force tests, so that other tests can remain focused."""


def test_startup_shutdown_sequence(context: Context):
    state = begin_with_initial_hooks_isolated(context)
    state = context.run(context.on.update_status(), state)

    for peer_rel in state.get_relations("replicas"):
        state = context.run(context.on.relation_departed(peer_rel, remote_unit=2), state)

    state = context.run(context.on.stop(), state)
    context.run(context.on.remove(), state)


@pytest.mark.parametrize("fqdn", ["localhost", "am-0.endpoints.cluster.local"])
@pytest.mark.parametrize("leader", [True, False])
class TestAlertingRelationDataUniformity:
    """Scenario: The charm is related to several different prometheus apps."""

    @pytest.fixture
    def post_startup(self, context, fqdn, leader) -> State:
        with patch("socket.getfqdn", new=lambda *args: fqdn):
            state = begin_with_initial_hooks_isolated(context, leader=leader)

            # Add several relations TODO: how to obtain the next rel_id automatically?
            prom_rels = [Relation("alerting", id=rel_id) for rel_id in (10, 11, 12)]
            for prom_rel in prom_rels:
                state = add_relation_sequence(context, state, prom_rel)
            return state

    def test_relation_data_is_the_same_for_all_related_apps(self, post_startup, fqdn):
        # GIVEN an isolated alertmanager charm after the startup sequence is complete
        state = post_startup

        # THEN the "alerting" relation data has the same contents for all related apps
        relations = state.get_relations("alerting")
        for i in range(1, len(relations)):
            assert relations[0].local_unit_data == relations[i].local_unit_data
            assert relations[0].local_app_data == relations[i].local_app_data
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Feature: The workload's scheme is reflected in the pebble command and in relation data.

This feature spans:
- manifest generation (pebble layer)
- schema generation (alertmanager_dispatch provider)

The alertmanager server can serve over HTTP or HTTPS. The requirer side of the relation may be
design to take URL parts rather than a full URL. Prometheus takes URL parts and would need to
generate its "alertmanagers" config section differently depending on the scheme.
"""

import json
from unittest.mock import patch

import pytest
from helpers import add_relation_sequence, begin_with_initial_hooks_isolated
from ops.testing import Relation, State


@pytest.mark.parametrize("fqdn", ["localhost", "am-0.endpoints.cluster.local"])
@pytest.mark.parametrize("leader", [True, False])
class TestServerScheme:
    """Scenario: The workload is deployed to operate in HTTP mode, then switched to HTTPS."""

    @pytest.fixture
    def initial_state(self, context, fqdn, leader) -> State:  # pyright: ignore
        """This is the initial state for this test class."""
        # GIVEN an isolated alertmanager charm after the startup sequence is complete

        # No "tls-certificates" relation, no config options
        with patch("socket.getfqdn", new=lambda *args: fqdn):
            state = begin_with_initial_hooks_isolated(context, leader=leader)

            # Add relation
            prom_rel = Relation("alerting", id=10)
            state = add_relation_sequence(context, state, prom_rel)
            yield state  # keep the patch active for so long as this fixture is needed  # pyright:ignore

    def test_initial_state_has_http_scheme_in_pebble_layer(self, context, initial_state, fqdn):
        # THEN the pebble command has 'http' and the correct hostname in the 'web.external-url' arg
        container = initial_state.get_container("alertmanager")
        command = container.layers["alertmanager"].services["alertmanager"].command
        assert f"--web.external-url=http://{fqdn}:9093" in command

    @pytest.mark.xfail
    def test_pebble_layer_scheme_becomes_https_if_tls_relation_added(
        self, context, initial_state, fqdn
    ):
        # WHEN a tls_certificates relation joins
        ca = Relation(
            "certificates",
            id=100,
            remote_app_data={
                "certificates": json.dumps(
                    [
                        {
                            # fixme: the problem is: instead of "placeholder" here we need a forward ref to the
                            #  CSR that AM will generate on certificates_relation_joined.
                            #  Otherwise, as it stands, charms/tls_certificates_interface/v2/tls_certificates.py:1336 will not find
                            #  this csr and ignore it. Hence no handlers are triggered.
                            "certificate": "placeholder",
                            "certificate_signing_request": "placeholder",
                            "ca": "placeholder",
                            "chain": ["first", "second"],
                        }
                    ]
                )
            },
        )  # TODO figure out how to easily figure out structure of remote data
        state = add_relation_sequence(context, initial_state, ca)
        # TODO figure out why relation-changed observer in tls_certificates is not being called

        # THEN the pebble command has 'https' in the 'web.external-url' arg
        container = state.get_container("alertmanager")
        command = container.layers["alertmanager"].services["alertmanager"].command
        assert f"--web.external-url=https://{fqdn}:9093" in command
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 59s</sub>

### 💬 Copilot

Now I have enough context. Let me create the git branch and start making changes:

---

<sub>⏱️ 6m 59s</sub>

### ✅ `bash`

**Create upgrade-ops branch**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && git checkout -b upgrade-ops

```
Switched to a new branch 'upgrade-ops'
<exited with exit code 0>
```


---

<sub>⏱️ 7m 7s</sub>

### 💬 Copilot

Now let me update `pyproject.toml` and `tox.ini`:

---

<sub>⏱️ 7m 7s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 7m 7s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 7m 7s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 7m 7s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 7m 13s</sub>

### 💬 Copilot

Now update `tox.ini` to add `SCENARIO_BARE_CHARM_ERRORS=true`:

---

<sub>⏱️ 7m 13s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tox.ini.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tox.ini

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tox.ini updated with changes.
```


---

<sub>⏱️ 7m 19s</sub>

### 💬 Copilot

Now let me update the uv.lock file to use the new ops version:

---

<sub>⏱️ 7m 24s</sub>

### ✅ `bash`

**Update uv.lock file**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && tox -e lock 2>&1 | tail -20

<details>
<summary>21 lines</summary>

```
Updated requests v2.32.3 -> v2.33.1
Updated rpds-py v0.20.1, v0.25.1 -> v0.30.0
Removed rsa v4.9.1
Updated ruff v0.11.11 -> v0.15.8
Updated sh v1.14.3, v2.2.2 -> v2.2.2
Removed sniffio v1.3.1
Updated tenacity v9.0.0, v9.1.2 -> v9.1.4
Removed tomli v2.2.1
Updated typing-extensions v4.13.2 -> v4.15.0
Updated typing-inspection v0.4.1 -> v0.4.2
Updated urllib3 v2.2.3, v2.4.0 -> v2.6.3
Updated validators v0.34.0, v0.35.0 -> v0.35.0
Updated wcwidth v0.2.13 -> v0.6.0
Updated websocket-client v1.8.0 -> v1.9.0
Updated websockets v8.1, v9.1, v13.1 -> v13.1
Updated werkzeug v3.0.6, v3.1.3 -> v3.1.7
Removed wrapt v1.17.2
Updated zipp v3.20.2, v3.21.0 -> v3.23.0
  lock: OK (4.06=setup[0.03]+cmd[4.03] seconds)
  congratulations :) (4.07 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 30s</sub>

### ✅ `bash`

**Verify ops version in updated lock file**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep -A5 "^name = \"ops\"$" uv.lock | head -10

<details>
<summary>7 lines</summary>

```
name = "ops"
version = "2.23.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "importlib-metadata" },
    { name = "opentelemetry-api" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 41s</sub>

### ✅ `bash`

**Check ops versions in lock file**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep "^version = " uv.lock | sort | uniq -c | head -5; grep -c "name = \"ops\"" uv.lock; grep -B1 -A5 "name = \"ops\"" uv.lock | head -40

<details>
<summary>46 lines</summary>

```
1 version = "0.0"
      1 version = "0.10"
      1 version = "0.13.0"
      1 version = "0.13.13"
      1 version = "0.15.8"
8
    { name = "opentelemetry-exporter-otlp-proto-http" },
    { name = "ops" },
    { name = "pydantic" },
    { name = "pyyaml" },
    { name = "tenacity" },
]

--
    { name = "juju" },
    { name = "ops", extra = ["testing"] },
    { name = "pyright" },
    { name = "pytest" },
    { name = "pytest-httpserver" },
    { name = "pytest-interface-tester" },
    { name = "pytest-operator" },
--
    { name = "opentelemetry-exporter-otlp-proto-http", specifier = ">=1.21.0" },
    { name = "ops" },
    { name = "ops", extras = ["testing"], marker = "extra == 'dev'" },
    { name = "pydantic", specifier = ">=2" },
    { name = "pyright", marker = "extra == 'dev'" },
    { name = "pytest", marker = "extra == 'dev'" },
    { name = "pytest-httpserver", marker = "extra == 'dev'" },
    { name = "pytest-interface-tester", marker = "extra == 'dev'", specifier = ">0.3" },
--
dependencies = [
    { name = "ops" },
    { name = "pydantic" },
]
sdist = { url = "https://files.pythonhosted.org/packages/b9/b1/01f400a87af69198f90abfd74d4f9e53878fb015e6ccb61ebbc4370dcf6b/charmed_service_mesh_helpers-0.6.0.tar.gz", hash = "sha256:2a606679c467c68744d439641aa8fe9fc533eebfaea97fc3662e87266fd0d786", size = 16869, upload-time = "2026-03-17T12:19:59Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/b9/57/f3432cace60a3116bb7f9b98aae42638278777da3fdf78aa49e974d43920/charmed_service_mesh_helpers-0.6.0-py3-none-any.whl", hash = "sha256:7160e5c1585efd2e369ccc6257c8e5964bbc52bce21a053ccba010e29b1fb12a", size = 16436, upload-time = "2026-03-17T12:19:59.667Z" },
--
dependencies = [
    { name = "ops" },
    { name = "pydantic" },
    { name = "pyyaml" },
    { name = "tenacity" },
    { name = "typing-extensions" },
]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 47s</sub>

### ✅ `bash`

**Check ops package definition in lock file**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep -B2 -A15 "^name = \"ops\"$" uv.lock | head -30

<details>
<summary>17 lines</summary>

```
[[package]]
name = "ops"
version = "2.23.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "importlib-metadata" },
    { name = "opentelemetry-api" },
    { name = "pyyaml" },
    { name = "websocket-client" },
]
sdist = { url = "https://files.pythonhosted.org/packages/93/98/84789a5e15ad76e043301bbd70b4d39cffaa717ae6eecb662fd0dd0cc7af/ops-2.23.2.tar.gz", hash = "sha256:a69b0c5bc65ebd91720fc96459e81b969df851f3a6c9c855ee73de7004205987", size = 528074, upload-time = "2026-02-11T03:58:15.565Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/e0/00/65da7c96d0f9e13c4de3bdd2e3717259fe723ff4bd4e5dc714164f851032/ops-2.23.2-py3-none-any.whl", hash = "sha256:9cab0c6bc46eeff2e96777128200c3ef872b55641b12f07dc4fd6fe3103954be", size = 188415, upload-time = "2026-02-11T03:58:13.693Z" },
]

[package.optional-dependencies]
testing = [
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 2s</sub>

### ✅ `bash`

**Check ops 3.7.0 wheel requirements**

$ pip show ops 2>/dev/null | grep -E "Version|Requires-Python"; pip download ops==3.7.0 --no-deps -d /tmp/ops-check 2>&1 | tail -5; ls /tmp/ops-check/ 2>/dev/null

<details>
<summary>8 lines</summary>

```
Version: 3.7.0
Collecting ops==3.7.0
  Using cached ops-3.7.0-py3-none-any.whl.metadata (7.2 kB)
Using cached ops-3.7.0-py3-none-any.whl (211 kB)
Saved /tmp/ops-check/ops-3.7.0-py3-none-any.whl
Successfully downloaded ops
ops-2.21.0-py3-none-any.whl  ops-3.7.0-py3-none-any.whl
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 12s</sub>

### ✅ `bash`

**Check ops 3.7.0 metadata and python requirements**

$ pip show ops 2>/dev/null | grep -E "^Requires\b"; python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/ops-check/ops-3.7.0-py3-none-any.whl'); meta=[f for f in z.namelist() if 'METADATA' in f]; print(z.read(meta[0]).decode()[:1000])"

<details>
<summary>25 lines</summary>

```
Requires: opentelemetry-api, PyYAML, websocket-client
Metadata-Version: 2.4
Name: ops
Version: 3.7.0
Summary: The Python library behind great charms
Author: The Charm Tech team at Canonical Ltd.
License-Expression: Apache-2.0
Project-URL: Homepage, https://documentation.ubuntu.com/ops/latest/
Project-URL: Repository, https://github.com/canonical/operator
Project-URL: Issues, https://github.com/canonical/operator/issues
Project-URL: Documentation, https://documentation.ubuntu.com/ops/latest/
Project-URL: Changelog, https://github.com/canonical/operator/blob/main/CHANGES.md
Classifier: Programming Language :: Python :: 3
Classifier: Development Status :: 5 - Production/Stable
Classifier: Intended Audience :: Developers
Classifier: Intended Audience :: System Administrators
Classifier: Operating System :: MacOS :: MacOS X
Classifier: Operating System :: POSIX :: Linux
Requires-Python: >=3.10
Description-Content-Type: text/markdown
License-File: LICENSE.txt
Requires-Dist: PyYAML==6.*
Requires-Dist: websocket-client==1.*
Requires-Dist: opentel
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 21s</sub>

### ✅ `bash`

**Check if ops 3.x can be installed**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && uv pip install --dry-run "ops>=3.0.0" 2>&1 | head -20

```
error: No virtual environment found; run `uv venv` to create an environment, or pass `--system` to install into a non-virtual environment
<exited with exit code 0>
```


---

<sub>⏱️ 8m 28s</sub>

### ✅ `bash`

**Check uv.lock requires-python**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat uv.lock | grep "^requires-python"

```
requires-python = ">=3.12"
<exited with exit code 0>
```


---

<sub>⏱️ 8m 34s</sub>

### ✅ `bash`

**Check for ops 2.23.2 constraints**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep -B5 "ops.*2.23.2" uv.lock | head -20

<details>
<summary>9 lines</summary>

```
{ name = "importlib-metadata" },
    { name = "opentelemetry-api" },
    { name = "pyyaml" },
    { name = "websocket-client" },
]
sdist = { url = "https://files.pythonhosted.org/packages/93/98/84789a5e15ad76e043301bbd70b4d39cffaa717ae6eecb662fd0dd0cc7af/ops-2.23.2.tar.gz", hash = "sha256:a69b0c5bc65ebd91720fc96459e81b969df851f3a6c9c855ee73de7004205987", size = 528074, upload-time = "2026-02-11T03:58:15.565Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/e0/00/65da7c96d0f9e13c4de3bdd2e3717259fe723ff4bd4e5dc714164f851032/ops-2.23.2-py3-none-any.whl", hash = "sha256:9cab0c6bc46eeff2e96777128200c3ef872b55641b12f07dc4fd6fe3103954be", size = 188415, upload-time = "2026-02-11T03:58:13.693Z" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 43s</sub>

### ✅ `bash`

**Check cosl package requirements**

$ pip show cosl 2>/dev/null | grep -E "Version|Requires"; pip download cosl --no-deps -d /tmp/cosl-check 2>&1 | tail -5 && ls /tmp/cosl-check/

<details>
<summary>11 lines</summary>

```
Version: 1.6.1
                           Version 2.0, January 2004
   Licensed under the Apache License, Version 2.0 (the "License");
Requires: ops, pydantic, pyyaml, tenacity, typing-extensions
Collecting cosl
  Downloading cosl-1.9.1-py3-none-any.whl.metadata (15 kB)
Downloading cosl-1.9.1-py3-none-any.whl (38 kB)
Saved /tmp/cosl-check/cosl-1.9.1-py3-none-any.whl
Successfully downloaded cosl
cosl-1.9.1-py3-none-any.whl
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 50s</sub>

### ✅ `bash`

**Check cosl version in lock file**

$ grep -B2 -A10 "^name = \"cosl\"" /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/uv.lock | head -20

<details>
<summary>13 lines</summary>

```
[[package]]
name = "cosl"
version = "1.9.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "ops" },
    { name = "pydantic" },
    { name = "pyyaml" },
    { name = "tenacity" },
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/7b/f1/6bc646976c499e9bb7a048ef17b6295f23b145f11f1cee4207ce10494342/cosl-1.9.1.tar.gz", hash = "sha256:80d899b5f278bf64252eb94bfb1bbd03dade5073c2cbc0ea43e9abc68be9ee1e", size = 150395, upload-time = "2026-03-31T12:50:20.064Z" }
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 57s</sub>

### ✅ `bash`

**Check ops-scenario version in lock file**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep -B2 -A10 "^name = \"ops-scenario\"" uv.lock | head -20; grep -B2 -A10 "^name = \"ops-tracing\"" uv.lock | head -20

<details>
<summary>13 lines</summary>

```
[[package]]
name = "ops-scenario"
version = "7.23.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "ops" },
    { name = "pyyaml" },
]
sdist = { url = "https://files.pythonhosted.org/packages/ee/e7/1514b9c27b9364ec1d04791b0fb76d1a629c8cc73f90fbf6dd867457c914/ops_scenario-7.23.2.tar.gz", hash = "sha256:327dda8b3c871ccf16246ed4f8c7e093526af42093549976596cede58cbc8488", size = 70017, upload-time = "2026-02-11T03:58:16.553Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/01/15/3b59993cad1b2838c9bb20f6f2ed5297fcf490025b1ffecc27d06be1daba/ops_scenario-7.23.2-py3-none-any.whl", hash = "sha256:024b638e0ea94e8f2e3c642d4f96031b0c7ac4f39117b97107dc9a09503651b4", size = 64328, upload-time = "2026-02-11T03:58:14.916Z" },
]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 10s</sub>

### ✅ `bash`

**Check for ops version constraints in lock file**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep -r "ops" uv.lock | grep "specifier" | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 9m 17s</sub>

### ✅ `bash`

**Check ops-scenario and ops-tracing in lock**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep "ops-scenario\|ops-tracing" uv.lock | head -10

```
{ name = "ops-scenario" },
name = "ops-scenario"
    { name = "ops-scenario" },
<exited with exit code 0>
```


---

<sub>⏱️ 9m 29s</sub>

### ✅ `bash`

**Check ops 3.7.0 optional deps**

$ python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/ops-check/ops-3.7.0-py3-none-any.whl'); meta=[f for f in z.namelist() if 'METADATA' in f]; print(z.read(meta[0]).decode())" | grep -i "testing\|scenario\|optional"

<details>
<summary>12 lines</summary>

```
Provides-Extra: testing
Requires-Dist: ops-scenario==8.7.0; extra == "testing"
The `ops` library is a Python framework for developing and testing Kubernetes and machine [charms](https://charmhub.io/). While charms can be written in any language, `ops` defines the latest standard, and charmers are encouraged to use Python with `ops` for all charms. The library is an official component of the Charm SDK, itself a part of [the Juju universe](https://canonical.com/juju).
- The `tests/unit/test_charm.py` file imports `ops.testing` and uses it to set up a unit test:
from ops import testing
    ctx = testing.Context(OpsExampleCharm)
    container = testing.Container("httpbin", can_connect=True)
    state_in = testing.State(containers={container})
    assert state_out.unit_status == testing.ActiveStatus()
> See more: [`ops.testing`](https://documentation.ubuntu.com/ops/latest/reference/ops-testing/)
> See [Juju | Tear things down](https://documentation.ubuntu.com/juju/3.6/howto/manage-your-juju-deployment/tear-down-your-juju-deployment-local-testing-and-development/). <br> Choose the automatic track.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 38s</sub>

### ✅ `bash`

**Check ops-scenario 7.23.2 metadata**

$ pip download ops-scenario==7.23.2 --no-deps -d /tmp/scenario-check 2>&1 | tail -5 && ls /tmp/scenario-check/ && python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/scenario-check/ops_scenario-7.23.2-py3-none-any.whl'); meta=[f for f in z.namelist() if 'METADATA' in f]; print(z.read(meta[0]).decode()[:500])"

<details>
<summary>17 lines</summary>

```
Collecting ops-scenario==7.23.2
  File was already downloaded /tmp/scenario-check/ops_scenario-7.23.2-py3-none-any.whl
Successfully downloaded ops-scenario
ops_scenario-7.23.2-py3-none-any.whl
Metadata-Version: 2.4
Name: ops-scenario
Version: 7.23.2
Summary: Python library providing a state-transition testing API for Operator Framework charms.
Author-email: Pietro Pasotti <pietro.pasotti@canonical.com>
Maintainer: The Charm Tech team at Canonical Ltd.
License: Apache-2.0
Project-URL: Homepage, https://github.com/canonical/operator
Project-URL: Bug Tracker, https://github.com/canonical/operator/issues
Keywords: juju,test
Classifier: Development Status :: 5 - Production/Stable
Classifie
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 44s</sub>

### ✅ `bash`

**Check ops-scenario 7.23.2 requires**

$ python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/scenario-check/ops_scenario-7.23.2-py3-none-any.whl'); meta=[f for f in z.namelist() if 'METADATA' in f]; print(z.read(meta[0]).decode())" | grep -i "requires\|python\|ops"

<details>
<summary>32 lines</summary>

````
Name: ops-scenario
Summary: Python library providing a state-transition testing API for Operator Framework charms.
Requires-Python: >=3.8
Requires-Dist: ops==2.23.2
Requires-Dist: PyYAML>=6.0.1
# ops-scenario, the unit testing framework for ops charms
`ops-scenario` is a Python library that provides state-transition testing for
[Ops](https://documentation.ubuntu.com/ops/2.x/) charms. These tests are higher level than
```python
from ops import testing
```python
from ops import testing
ops in your unit testing environment. For example, in `pyproject.toml`:
test = ['ops[testing]<4.0']
Ops checks if `ops-scenario` is installed, and, if so, makes the classes
(such as `Context`, `State`, and `Relation`) available in the `ops.testing`
namespace. Use `from ops import testing` rather than importing the `scenario`
`ops-scenario` supports the same platforms and Python versions as ops itself.
 * To get started, work through our ['Write your first Kubernetes charm' tutorial](https://ops.readthedocs.io/en/latest/tutorial/from-zero-to-hero-write-your-first-kubernetes-charm/create-a-minimal-kubernetes-charm.html#write-unit-tests-for-your-charm), following the instructions for adding
 * When you need to write a test that involves specific ops functionality,
   refer to our [how-to guides](https://ops.readthedocs.io/en/latest/howto/index.html)
   which all conclude with examples of tests of the ops functionality.
 * Use our extensive [reference documentation](https://ops.readthedocs.io/en/latest/reference/ops-testing.html#ops-testing) when you need to know how each `testing` object works. These
   docs are also available via the standard Python `help()` functionality and in
[**Read the full documentation**](https://documentation.ubuntu.com/ops/2.x/)
`ops-scenario` is a member of the Charming family. It's an open source project
  for all Ops-related discussions, including around testing.
Anyone can contribute to ops and `ops-scenario`. It's best to start by
contribute to `ops-scenario`.
Currently, releases of `ops-scenario` are done in lockstep with releases of ops
itself, with matching minor and bugfix release numbers. The ops documentation
<exited with exit code 0>
````

</details>


---

<sub>⏱️ 10m 4s</sub>

### 💬 Copilot

I need to explicitly constrain ops to \>=3.0 since uv is selecting 2.23.2 (which ops-scenario 7.x pins to exactly):

---

<sub>⏱️ 10m 4s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml.**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/pyproject.toml updated with changes.
```


---

<sub>⏱️ 10m 14s</sub>

### ✅ `bash`

**Re-lock with ops>=3.0 constraint**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && tox -e lock 2>&1 | tail -20

<details>
<summary>9 lines</summary>

```
lock: commands[0]> uv lock --upgrade --no-cache
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Resolved 108 packages in 3.04s
Updated charmed-service-mesh-helpers v0.6.0 -> v0.2.0
Updated ops v2.23.2 -> v3.7.0
Updated ops-scenario v7.23.2 -> v8.7.0
  lock: OK (3.26=setup[0.00]+cmd[3.26] seconds)
  congratulations :) (3.28 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 21s</sub>

### 💬 Copilot

Now let me verify ops 3.7.0 is in the lock and run tests to see what fails:

---

<sub>⏱️ 10m 22s</sub>

### ✅ `bash`

**Verify ops versions in lock**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep -A3 "^name = \"ops\"$" uv.lock | head -5; grep -A3 "^name = \"ops-scenario\"$" uv.lock | head -5

<details>
<summary>9 lines</summary>

```
name = "ops"
version = "3.7.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
name = "ops-scenario"
version = "8.7.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 27s</sub>

### 💬 Copilot

Now let's run tests to see what fails:

---

<sub>⏱️ 12m 27s</sub>

### ✅ `bash`

**Run tests with new ops version**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && tox -e unit 2>&1 | tail -80

<details>
<summary>69 lines</summary>

```
tests/unit/test_charm.py::TestWithInitialHooks::test_topology_is_not_added_if_user_provided_config_with_ellipsis
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_charm.py:29: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_charm.py::TestWithoutInitialHooks::test_unit_status_around_pebble_ready
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_charm.py:181: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_charm.py::TestActions::test_show_config
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_charm.py:214: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_charm.py::TestActions::test_show_config
tests/unit/test_server_scheme.py::TestServerScheme::test_pebble_layer_scheme_becomes_https_if_tls_relation_added[True-am-0.endpoints.cluster.local]
tests/unit/test_server_scheme.py::TestServerScheme::test_pebble_layer_scheme_becomes_https_if_tls_relation_added[False-localhost]
tests/unit/test_server_scheme.py::TestServerScheme::test_pebble_layer_scheme_becomes_https_if_tls_relation_added[False-am-0.endpoints.cluster.local]
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/lib/charms/tls_certificates_interface/v4/tls_certificates.py:1289: DeprecationWarning: generate_private_key() is deprecated. Use PrivateKey.generate() instead.
    warnings.warn(

tests/unit/test_consumer.py::TestConsumer::test_cluster_is_empty_after_relation_breaks
tests/unit/test_consumer.py::TestConsumer::test_cluster_updated_after_alertmanager_unit_leaves
tests/unit/test_consumer.py::TestConsumer::test_cluster_updated_after_alertmanager_units_join
tests/unit/test_consumer.py::TestConsumer::test_relation_changed
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_consumer.py:60: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(SampleConsumerCharm, meta=SampleConsumerCharm.metadata_yaml)

tests/unit/test_push_config_to_workload_on_startup.py::TestPushConfigToWorkloadOnStartup::test_charm_blocks_on_connection_error
tests/unit/test_push_config_to_workload_on_startup.py::TestPushConfigToWorkloadOnStartup::test_single_unit_cluster
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_push_config_to_workload_on_startup.py:40: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_push_config_to_workload_on_startup.py::TestInvalidConfig::test_charm_blocks_on_invalid_config_changed
tests/unit/test_push_config_to_workload_on_startup.py::TestInvalidConfig::test_charm_blocks_on_invalid_config_on_startup
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_push_config_to_workload_on_startup.py:121: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_config_with_templates_updates_both_alertmanager_config_and_alertmanager_templates_in_the_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_config_without_templates_updates_only_alertmanager_config_in_the_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_empty_config_file_clears_relation_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_invalid_config_clears_relation_data_bag
tests/unit/test_remote_configuration_provider.py::TestAlertmanagerRemoteConfigurationProvider::test_invalid_config_emits_remote_configuration_broken_event
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_remote_configuration_provider.py:87: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = testing.Harness(RemoteConfigurationProviderCharm, meta=METADATA)

tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_configs_available_from_both_relation_data_bag_and_charm_config_block_charm
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_invalid_config_pushed_to_the_relation_data_bag_does_not_update_alertmanager_config
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_templates_pushed_to_relation_data_bag_are_saved_to_templates_file_in_alertmanager
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_valid_config_pushed_to_relation_data_bag_updates_alertmanager_config
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_remote_configuration_requirer.py:52: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = testing.Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_no_peers
tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4/tests/unit/test_self_scrape_jobs.py:22: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/.cache/uv/builds-v0/.tmpgFiTH2/lib/python3.12/site-packages/ops/_private/harness.py:1109: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/1'.
    warnings.warn(

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/.cache/uv/builds-v0/.tmpgFiTH2/lib/python3.12/site-packages/ops/_private/harness.py:1109: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/2'.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====== 57 passed, 3 skipped, 4 xfailed, 311 warnings in 105.57s (0:01:45) ======
unit: commands[1]> uv run --frozen --isolated --extra=dev coverage report
Installed 106 packages in 50ms
Name                                                                  Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------------------------------------
lib/charms/alertmanager_k8s/v0/alertmanager_remote_configuration.py     124     15     20      2    88%   52-54, 184, 228-229, 377, 385, 405-406, 417, 449-451, 471-472
lib/charms/alertmanager_k8s/v1/alertmanager_dispatch.py                  98      8     16      4    89%   114, 123-132, 222->exit, 233->232, 239-241, 245
src/alertmanager.py                                                     133     22     28     11    78%   41, 45, 129, 144, 152, 161, 169-170, 230, 240-241, 257, 265-266, 277-278, 283-284, 297, 324, 336-337
src/alertmanager_client.py                                              124     30     10      3    74%   55, 73-74, 84, 114, 121-122, 162-167, 193-202, 314-323, 345-354
src/charm.py                                                            270     39     50     10    83%   278, 324-329, 332, 335-339, 343-352, 358, 381-382, 414-416, 470-472, 482->499, 486-493, 506->512, 527-529, 536, 575, 593, 598-599, 635, 670
src/config_builder.py                                                    67      3     16      2    92%   73->75, 133-135
-----------------------------------------------------------------------------------------------------------------
TOTAL                                                                   816    117    140     32    83%
  unit: OK (117.00=setup[0.01]+cmd[116.72,0.27] seconds)
  congratulations :) (117.01 seconds)
<command with shellId: 48 is still running after 120 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 12m 59s</sub>

### 💬 Copilot

All tests pass. Now let me migrate the Harness-based tests to Context-based testing using a general-purpose agent:

---

<sub>⏱️ 12m 59s</sub>

### ✅ `sql`

**Create todos for test migration**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create todos for test migration",
  "query": "INSERT INTO todos (id, title, description, status) VALUES\n  ('migrate-test-charm', 'Migrate test_charm.py', 'Migrate TestWithInitialHooks, TestWithoutInitialHooks, TestActions from Harness to Context-based testing', 'pending'),\n  ('migrate-test-consumer', 'Migrate test_consumer.py', 'Migrate TestConsumer (SampleConsumerCharm) from Harness to Context-based testing', 'pending'),\n  ('migrate-test-external-url', 'Migrate test_external_url.py', 'Migrate TestExternalUrl from Harness to Context-based testing (most tests are skipped)', 'pending'),\n  ('migrate-test-push-config', 'Migrate test_push_config_to_workload_on_startup.py', 'Migrate TestPushConfigToWorkloadOnStartup and TestInvalidConfig from Harness to Context-based testing', 'pending'),\n  ('migrate-test-remote-provider', 'Migrate test_remote_configuration_provider.py', 'Migrate TestAlertmanagerRemoteConfigurationProvider from Harness to Context-based testing', 'pending'),\n  ('migrate-test-remote-requirer', 'Migrate test_remote_configuration_requirer.py', 'Migrate TestAlertmanagerRemoteConfigurationRequirer from Harness to Context-based testing', 'pending'),\n  ('migrate-test-self-scrape', 'Migrate test_self_scrape_jobs.py', 'Migrate TestWithInitialHooks from Harness to Context-based testing', 'pending'),\n  ('cleanup-simulate-can-connect', 'Remove SIMULATE_CAN_CONNECT', 'Remove ops.testing.SIMULATE_CAN_CONNECT = True from all test files', 'pending')"
}
```

</details>

```
8 row(s) inserted. Last inserted row ID: 8.
```


---

<sub>⏱️ 12m 59s</sub>

### ℹ️ Notification

Shell "Run tests with new ops version" completed

---

<sub>⏱️ 14m 39s</sub>

### ✅ `task`

**Migrate Harness tests to Context**

<details>
<summary>Arguments</summary>

````json
{
  "name": "migrate-harness-tests",
  "description": "Migrate Harness tests to Context",
  "agent_type": "general-purpose",
  "mode": "background",
  "prompt": "\nYou are working in a git repository at /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 on branch \"upgrade-ops\".\n\n## Background\n\nThe project has been upgraded from ops 2.21.1 to ops 3.7.0 (and ops-scenario from 7.21.1 to 8.7.0). With the new version, `Harness` is deprecated and emits `PendingDeprecationWarning`. The new recommended approach is using `ops.testing.Context` + `ops.testing.State`.\n\n`SCENARIO_BARE_CHARM_ERRORS=true` is set in tox.ini for the unit env.\n\n## Task\n\nMigrate ALL remaining Harness-based tests to the new Context/State-based testing API. Remove `ops.testing.SIMULATE_CAN_CONNECT = True` from all test files (this attribute no longer exists in ops 3.x).\n\n## Existing patterns in this codebase\n\nLook at `tests/unit/helpers.py` for existing helpers:\n- `begin_with_initial_hooks_isolated(context, leader=True)` - simulates full startup sequence\n- `add_relation_sequence(context, state, relation)` - simulates relation-added sequence\n\nLook at `tests/unit/conftest.py` - it provides:\n- `alertmanager_charm` fixture - patches KubernetesComputeResourcesPatch, WorkloadManager.check_config, WorkloadManager._alertmanager_version, subprocess.run, lightkube\n- `context` fixture - `Context(charm_type=alertmanager_charm)`\n\nLook at existing Context-based tests: `tests/unit/test_brute_isolated.py`, `tests/unit/test_server_scheme.py`, `tests/unit/test_self_scrape_jobs.py` (wait - this one is still Harness-based, see below).\n\n## Key Context/State API facts\n\n```python\nfrom ops.testing import Context, State, Container, Relation, PeerRelation, Exec, Secret\n\n# Run an event\nstate_out = context.run(context.on.config_changed(), state_in)\nstate_out = context.run(context.on.pebble_ready(container), state_in)\nstate_out = context.run(context.on.relation_created(rel), state_in)\nstate_out = context.run(context.on.relation_joined(rel), state_in)\nstate_out = context.run(context.on.relation_changed(rel), state_in)\nstate_out = context.run(context.on.leader_elected(), state_in)\nstate_out = context.run(context.on.install(), state_in)\nstate_out = context.run(context.on.start(), state_in)\nstate_out = context.run(context.on.update_status(), state_in)\nstate_out = context.run(context.on.upgrade_charm(), state_in)\n\n# Run an action\naction_out = context.run(context.on.action(\"show-config\"), state_in)\naction_out.results  # dict of action results\n\n# State is immutable - use dataclasses.replace() or state.replace() to modify\nimport dataclasses\nnew_state = dataclasses.replace(state, leader=True, config={\"key\": \"value\"})\n\n# Access container in output state\ncontainer = state_out.get_container(\"alertmanager\")\ncontainer.get_filesystem(context)  # get a TempFS\n\n# Access relations\nrel = state_out.get_relation(\"alerting\")  # or by id\nrelations = state_out.get_relations(\"alerting\")\n\n# Container layers\ncontainer.layers  # dict of layer name -> Layer object\nservice_command = container.layers[\"alertmanager\"].services[\"alertmanager\"].command\n\n# Pebble plan\ncontainer.get_plan()  # combined plan\nplan = container.get_plan()\nservice = plan.services[\"alertmanager\"]\nservice.command  # the command string\n\n# State.unit_status, State.app_status\nassert state_out.unit_status == ops.ActiveStatus()\nassert isinstance(state_out.unit_status, ops.BlockedStatus)\n\n# Relation local data\nrel.local_unit_data  # dict\nrel.local_app_data  # dict\n\n# For actions\nstate_out = context.run(context.on.action(\"show-config\"), state_in)\n# access results - but for actions, context.run returns a State but also\n# you need to use context.run_action to get action output:\naction_out = context.run_action(\"show-config\", state_in)\n# Actually in ops.testing 3.x, actions work as:\nwith context(context.on.action(\"show-config\"), state_in) as mgr:\n    mgr.run()\n    action_output = mgr.output  # ActionOutput object\n# OR just:\naction_state = context.run(context.on.action(\"show-config\"), state_in)\n# but to get results you need context.manager\n```\n\nActually, the correct way to check action results:\n```python\nctx = context\nwith ctx(ctx.on.action(\"show-config\"), state_in) as manager:\n    charm = manager.charm  # if you need to inspect the charm\n    state_out = manager.run()\n# After context manager, check results from the context\nassert ctx.action_results == {\"key\": \"value\"}\n# OR use context.run_action:\naction_output = ctx.run(ctx.on.action(\"show-config\"), state_in)\n# This is a State, but you can check ctx.action_results\n```\n\nActually, the proper API in ops-scenario 8.x for actions:\n```python\n# For an action that returns results:\nstate_out = context.run(context.on.action(\"show-config\"), state_in)\n# To inspect what the action did, use:\n# context.run returns State; the output from set_results is in context's history\n```\n\nActually the cleanest approach in ops.testing for actions is:\n```python\nctx = Context(AlertmanagerCharm)\nwith ctx(ctx.on.action(\"action-name\"), state) as mgr:\n    mgr.run()\n# After the context manager, access action output via the ctx object\n```\n\nBUT the simplest pattern actually is just checking that things don't raise, or using patches to verify calls.\n\n## Files to migrate\n\n### 1. tests/unit/test_charm.py\n\nThree test classes to migrate:\n\n**TestWithInitialHooks** - setUp: `begin_with_initial_hooks()` with alerting relation. Tests:\n- test_num_peers: checks `charm.peer_relation.units` is empty\n- test_pebble_layer_added: checks pebble plan has expected command args and service is running\n- test_relation_data_provides_public_address: checks alerting relation data has url, public_address, scheme\n- test_topology_added_if_user_provided_config_without_group_by: update_config, check config file\n- test_topology_added_if_user_provided_config_with_group_by: similar\n- test_topology_is_not_added_if_user_provided_config_with_ellipsis: similar\n- test_charm_blocks_if_user_provided_config_with_templates: update config, check blocked status\n- test_templates_file_not_created_if_user_provides_templates_without_config: check pebble.PathError\n- test_templates_section_added_if_user_provided_templates: update config and templates, check files\n\n**TestWithoutInitialHooks** - setUp: `begin()` + add replicas relation manually. Tests:\n- test_unit_status_around_pebble_ready: checks maintenance before pebble_ready, active after\n\n**TestActions** - setUp: `begin_with_initial_hooks()` no alerting relation. Tests:\n- test_show_config: runs show-config action, checks results\n\n### 2. tests/unit/test_consumer.py\n\nTests `SampleConsumerCharm` with `AlertmanagerConsumer`. Uses `StoredState` to track events. Tests:\n- test_cluster_updated_after_alertmanager_units_join: adds 2 units, checks cluster info\n- test_cluster_updated_after_alertmanager_unit_leaves: adds 4, removes 2, checks\n- test_cluster_is_empty_after_relation_breaks: adds 4, removes relation, checks empty\n- test_relation_changed: updates relation data, checks result\n\nThe `SampleConsumerCharm` needs a custom metadata yaml. Use `Context(SampleConsumerCharm, meta=...)`.\n\nFor accessing StoredState in state-transition tests: You need to access `context.charm` using the `with context(event, state) as manager` pattern.\n\n### 3. tests/unit/test_external_url.py\n\nAlmost all tests are `@unittest.skip`-ped. The only potentially active test... check the file.\nActually, ALL non-skipped tests in `test_external_url.py` should be confirmed. If none run, you can just delete the file or leave a minimal stub with a comment. ACTUALLY, keep the file but since all tests are skipped, just clean up Harness references.\n\nWait, looking at the file again - there are 2 tests total: `test_traefik_overrides_fqdn` and `test_cluster_addresses`, both with `@unittest.skip`. So nothing actually runs. Just remove the Harness usage and `SIMULATE_CAN_CONNECT`.\n\n### 4. tests/unit/test_push_config_to_workload_on_startup.py\n\n**TestPushConfigToWorkloadOnStartup** - class-level patch for `subprocess.run` and `check_config`. Tests:\n- test_single_unit_cluster (parametrized via hypothesis with is_leader bool): checks amtool config, am config, pebble layer command\n- test_multi_unit_cluster: @unittest.skip\n- test_charm_blocks_on_connection_error: set_can_connect(False), check not ActiveStatus\n\n**TestInvalidConfig** - Tests:\n- test_charm_blocks_on_invalid_config_on_startup: config \"templates: [wrong]\" before begin, then begin\n- test_charm_blocks_on_invalid_config_changed: valid config, begin, then invalid config, check blocked\n\n### 5. tests/unit/test_remote_configuration_provider.py\n\nTests `RemoteConfigurationProviderCharm` which is a custom charm class. Uses `StoredState`.\n\n**TestAlertmanagerRemoteConfigurationProvider** - Tests:\n- test_config_without_templates_updates_only_alertmanager_config_in_the_data_bag\n- test_config_with_templates_updates_both_alertmanager_config_and_alertmanager_templates_in_the_data_bag\n- test_invalid_config_emits_remote_configuration_broken_event\n- test_invalid_config_clears_relation_data_bag\n- test_empty_config_file_clears_relation_data_bag\n\n### 6. tests/unit/test_remote_configuration_requirer.py\n\nTests `AlertmanagerCharm` with remote configuration. Tests:\n- test_valid_config_pushed_to_relation_data_bag_updates_alertmanager_config\n- test_invalid_config_pushed_to_the_relation_data_bag_does_not_update_alertmanager_config\n- test_templates_pushed_to_relation_data_bag_are_saved_to_templates_file_in_alertmanager\n- test_configs_available_from_both_relation_data_bag_and_charm_config_block_charm\n\n### 7. tests/unit/test_self_scrape_jobs.py\n\n**TestWithInitialHooks** - Tests:\n- test_self_scraping_job_with_no_peers\n- test_self_scraping_job_with_peers (adds peer units with private_address)\n\n## Important notes for migration\n\n1. The conftest.py `context` fixture uses `alertmanager_charm` fixture which patches `KubernetesComputeResourcesPatch`, `WorkloadManager.check_config`, `WorkloadManager._alertmanager_version`, and `subprocess.run`, and `lightkube.core.client.GenericSyncClient`. Leverage this fixture for AlertmanagerCharm tests.\n\n2. For tests that use `socket.getfqdn`, patch it in the test function: `with patch(\"socket.getfqdn\", return_value=\"fqdn\"):` or as pytest fixture.\n\n3. For accessing container file contents in Context tests, use `container.get_filesystem(context)` which returns a temp filesystem path object:\n```python\nfs = state_out.get_container(\"alertmanager\").get_filesystem(context)\nconfig_path = fs / \"etc/alertmanager/alertmanager.yml\"\ncontent = yaml.safe_load(config_path.read_text())\n```\n\n4. For checking if a service is running:\n```python\ncontainer = state_out.get_container(\"alertmanager\")\nplan = container.get_plan()\n# Check service is in the plan\nservice = plan.services.get(\"alertmanager\")\n# Note: in Context tests, you check the plan, but service.is_running() is different\n```\nActually service running status in ops.testing: check `container.service_statuses`:\n```python\ncontainer = state_out.get_container(\"alertmanager\")\ncontainer.service_statuses  # dict of service_name -> ServiceStatus\nfrom ops.pebble import ServiceStatus\ncontainer.service_statuses[\"alertmanager\"] == ServiceStatus.ACTIVE\n```\n\n5. For `PeerRelation`, `context.run(context.on.relation_joined(peer_rel), state)` etc.\n\n6. For the `TestConsumer` tests that track `StoredState`, you need to access the charm instance:\n```python\nwith context(context.on.relation_changed(rel), state) as mgr:\n    state_out = mgr.run()\n    stored = mgr.charm._stored  # access stored state\n    # but note: mgr.charm is only valid inside the context manager\n```\nActually better: inspect the output state and check the stored state via `state_out.stored_state`:\nActually in ops.testing, StoredState changes are reflected in `state_out.stored_state`:\n```python\nfrom ops.testing import StoredState\n# state.stored_state is a set of StoredState objects\n# StoredState(owner_path=\"SampleConsumerCharm\", name=\"_stored\", content={\"alertmanagers\": [...], ...})\n```\n\n7. For `RemoteConfigurationProviderCharm` which has custom events:\n```python\nstate_out = context.run(context.on.custom_event(\"alertmanager-config-file-changed\"), state_in)\n```\nActually the proper way: \n```python\nstate_out = context.run(context.on.action(\"...\"), state_in)  # for actions\n# For custom events emitted by the charm:\nstate_out = context.run(context.on.event(\"alertmanager_config_file_changed\"), state_in)\n```\n\n8. For accessing relation data in output state:\n```python\nrel_out = state_out.get_relation(\"remote-configuration\")\nrel_out.local_app_data  # what the app databag has\n```\n\n9. For tests that need `harness.get_relation_data(rel_id, app_name)`, use:\n```python\nrel_out = state_out.get_relation(id=rel_id)  # or by name\nrel_out.local_app_data  # for app data\n```\n\n10. IMPORTANT: `begin_with_initial_hooks_isolated` in helpers.py already handles the standard startup sequence. Use it as the base for most tests.\n\n11. For the `test_self_scrape_jobs.py` tests that access `harness.charm.self_scraping_job`:\nUse the context manager pattern to access the charm instance:\n```python\nwith context(context.on.config_changed(), state) as mgr:\n    state_out = mgr.run()\n    # Can't access charm after context exits\n# Actually, to test a property, you need to call it during event handling\n# Better: just call the property through a custom event or check the output state\n```\nActually, for testing properties of the charm, you could run update_status and then inspect the relation/container data. OR you could use context as a context manager and access `mgr.charm.property_name`:\n```python\nwith context(context.on.update_status(), state) as mgr:\n    jobs = mgr.charm.self_scraping_job  # access BEFORE run\n    state_out = mgr.run()\n```\n\n## Key imports\n\n```python\nfrom ops.testing import Context, State, Container, Relation, PeerRelation, Exec\nimport dataclasses\nimport ops\n```\n\n## Instructions\n\n1. Read each test file carefully\n2. Rewrite each test file to use the Context/State API\n3. Remove `ops.testing.SIMULATE_CAN_CONNECT = True` from all files\n4. Remove `from ops.testing import Harness` where no longer needed\n5. Prefer pytest functions/classes over unittest.TestCase where easy\n6. Keep the same test logic/assertions - just change the testing framework\n7. Run `tox -e unit` after all migrations are done to verify all tests pass\n8. Fix any failures\n\n## Context about conftest.py\n\nThe existing `conftest.py` (tests/unit/conftest.py) already has:\n- `alertmanager_charm` fixture: patches KubernetesComputeResourcesPatch, WorkloadManager.check_config, WorkloadManager._alertmanager_version, subprocess.run, lightkube\n- `context` fixture: `Context(charm_type=alertmanager_charm)` \n\nFor tests that need a different setup (like test_consumer.py with SampleConsumerCharm), they can create their own Context directly.\n\nFor tests that need socket.getfqdn patched, patch it within the test using `with patch(\"socket.getfqdn\", return_value=\"fqdn\"):` etc.\n\nIMPORTANT: `WorkloadManager._alertmanager_version` is patched to return \"0.0.0\" in the existing alertmanager_charm fixture. The check_config is also patched. This is important because these are called during startup.\n\n## Guidance on tricky parts\n\n### test_charm.py - accessing container file content\n\nTo check what was written to `/etc/alertmanager/alertmanager.yml`, use:\n```python\ncontainer = state_out.get_container(\"alertmanager\")\nfs = container.get_filesystem(context)\n# fs is a pathlib.Path to a temp dir that mirrors the container's filesystem\ncontent = yaml.safe_load((fs / \"etc/alertmanager/alertmanager.yml\").read_text())\n```\n\n### test_charm.py - config updates\n\nAfter `begin_with_initial_hooks_isolated`, run config-changed with new config:\n```python\nstate = begin_with_initial_hooks_isolated(context)\nstate = dataclasses.replace(state, config={\"config_file\": yaml_string})\nstate = context.run(context.on.config_changed(), state)\n```\n\n### test_consumer.py - tracking StoredState\n\n```python\nfor stored in state_out.stored_state:\n    if stored.owner_path == \"SampleConsumerCharm\" and stored.name == \"_stored\":\n        alertmanagers = stored.content[\"alertmanagers\"]\n        events_count = stored.content[\"cluster_changed_emitted\"]\n```\n\nActually there may also be:\n```python\nstate_out.stored_state  # set of StoredState objects\n# or access via mgr.charm._stored inside a context manager\n```\n\n### test_remote_configuration_provider.py - custom events\n\nFor emitting `on.alertmanager_config_file_changed`:\n```python\nfrom ops.testing import Context\n# Just use context.on.event(\"alertmanager_config_file_changed\") \n# Actually, check the ops.testing docs for custom events\n# In ops.testing, you can emit any event that's defined on the charm:\nstate_out = context.run(context.on.custom_event(\"alertmanager_config_file_changed\"), state_in)\n```\nWait, in ops.testing 8.x the way to emit custom events from outside is through relation events or by using `context.on.custom_event`. Check carefully.\n\nActually, in ops-scenario 8.x / ops 3.7.0 testing framework, custom events are supported as follows. Look at the ops.testing docs.\n\nActually the simplest approach for custom events: use `context.run(context.on.event(custom_event_name), state)` where `custom_event_name` is the snake_case event name. But actually if the charm has an `on` attribute with custom events, you'd call them differently.\n\nThe safest approach: skip migrating test_remote_configuration_provider.py for now if it's too complex and the tests can stay as Harness (Harness still works, just with deprecation warnings). Focus on migrating the main charm tests and the simpler ones.\n\nActually no - migrate all of them. For custom events in test_remote_configuration_provider.py, look at how to use `context.on.action` or find the custom event support.\n\nThe correct API for custom events in ops.testing 8.x:\n```python\n# Custom events - use the event name\nctx.run(ctx.on.event(\"alertmanager_config_file_changed\"), state)\n```\n\n### test_remote_configuration_requirer.py\n\nFor accessing files from the container during testing, in ops.testing you can pre-populate the container's filesystem using `Container(mounts=...)` or by using the `Exec` class to handle `exec` calls.\n\nFor checking files written TO the container by the charm, use `container.get_filesystem(context)`.\n\n### Service running status\n\nIn new ops.testing, to check if a service is running after pebble_ready:\n```python\ncontainer = state_out.get_container(\"alertmanager\")\n# The service status is tracked in container.service_statuses\nfrom ops.pebble import ServiceStatus\nassert container.service_statuses.get(\"alertmanager\") == ServiceStatus.ACTIVE\n```\n\n## Steps\n\n1. Migrate test_self_scrape_jobs.py (simplest - testing charm properties)\n2. Migrate test_external_url.py (mostly skipped tests - easy)\n3. Migrate test_charm.py (most tests, but well-supported by existing helpers)\n4. Migrate test_push_config_to_workload_on_startup.py\n5. Migrate test_consumer.py  \n6. Migrate test_remote_configuration_provider.py\n7. Migrate test_remote_configuration_requirer.py\n8. Run tests and fix failures\n\n## Verification\n\nAfter migrating, run:\n```bash\ncd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && tox -e unit\n```\n\nAll 57 tests should pass (same count or more) with NO Harness deprecation warnings. Fix any failures you encounter.\n"
}
````

</details>

```
Agent started in background with agent_id: migrate-harness-tests. You can use read_agent tool with this agent_id to check status and retrieve results. Instruct the user to use /tasks to manage the background agent.
```


---

<sub>⏱️ 14m 55s</sub>

### 💬 Copilot

While the migration agent runs, let me also review the remaining portion of the test files and check other aspects:

---

<sub>⏱️ 14m 56s</sub>

### ✅ `bash`

**Read rest of test_remote_configuration_requirer.py**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && cat tests/unit/test_remote_configuration_requirer.py | tail -100

<details>
<summary>87 lines</summary>

```
# now does it.
        self.harness.set_can_connect("alertmanager", True)

        # In ops 2.0.0+, we need to mock the version, as begin_with_initial_hooks() now triggers
        # pebble-ready, which attempts to obtain the workload version.
        patcher = patch.object(
            WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0")
        )
        self.mock_version = patcher.start()
        self.addCleanup(patcher.stop)

        self.harness.begin_with_initial_hooks()

        self.relation_id = self.harness.add_relation(
            DEFAULT_RELATION_NAME, "remote-config-provider"
        )
        self.harness.add_relation_unit(self.relation_id, "remote-config-provider/0")

    @k8s_resource_multipatch
    def test_valid_config_pushed_to_relation_data_bag_updates_alertmanager_config(
        self,
        *_,
    ):
        expected_config = remote_config = yaml.safe_load(TEST_ALERTMANAGER_REMOTE_CONFIG)
        # add juju topology to "group_by"
        route = cast(dict, expected_config.get("route", {}))
        route["group_by"] = list(
            set(route.get("group_by", [])).union(
                ["juju_application", "juju_model", "juju_model_uuid"]
            )
        )
        expected_config["route"] = route

        self.harness.update_relation_data(
            relation_id=self.relation_id,
            app_or_unit="remote-config-provider",
            key_values={"alertmanager_config": json.dumps(remote_config)},
        )
        config = self.harness.charm.container.pull(self.harness.charm._config_path)

        self.assertEqual(
            DeepDiff(yaml.safe_load(config.read()), expected_config, ignore_order=True),
            {},
        )

    @k8s_resource_multipatch
    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    def test_configs_available_from_both_relation_data_bag_and_charm_config_block_charm(
        self,
        *_,
    ):
        sample_remote_config = yaml.safe_load(TEST_ALERTMANAGER_REMOTE_CONFIG)
        self.harness.update_relation_data(
            relation_id=self.relation_id,
            app_or_unit="remote-config-provider",
            key_values={"alertmanager_config": json.dumps(sample_remote_config)},
        )
        self.harness.update_config({"config_file": TEST_ALERTMANAGER_DEFAULT_CONFIG})

        self.assertEqual(
            self.harness.charm.unit.status, BlockedStatus("Multiple configs detected")
        )

    @patch("config_builder.default_config", yaml.safe_load(TEST_ALERTMANAGER_DEFAULT_CONFIG))
    @k8s_resource_multipatch
    def test_invalid_config_pushed_to_the_relation_data_bag_does_not_update_alertmanager_config(
        self,
        *_,
    ):
        invalid_config = yaml.safe_load("some: invalid_config")

        self.harness.update_relation_data(
            relation_id=self.relation_id,
            app_or_unit="remote-config-provider",
            key_values={"alertmanager_config": json.dumps(invalid_config)},
        )
        config = self.harness.charm.container.pull(self.harness.charm._config_path)

        self.assertNotIn("invalid_config", yaml.safe_load(config.read()))

    @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
    @k8s_resource_multipatch
    def test_templates_pushed_to_relation_data_bag_are_saved_to_templates_file_in_alertmanager(
        self,
        *_,
    ):
        sample_remote_config = yaml.safe_load(TEST_ALERTMANAGER_REMOTE_CONFIG)
        test_template = '{{define "myTemplate"}}do something{{end}}'

        self.harness.update_relation_data(
            relation_id=self.relation_id,
            app_or_unit="remote-config-provider",
            key_values={
                "alertmanager_config": json.dumps(sample_remote_config),
                "alertmanager_templates": json.dumps([test_template]),
            },
        )
        updated_templates = self.harness.charm.container.pull(self.harness.charm._templates_path)

        self.assertEqual(updated_templates.read(), test_template)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 14m 56s</sub>

### ✅ `bash`

**Check for Python 3.8 compatibility patterns in source**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__set-ports__C4 && grep -rn "importlib-metadata\|python_requires\|typing_extensions" src/ lib/ 2>/dev/null | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 14m 56s</sub>

### ℹ️ Info

Operation cancelled by user

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
