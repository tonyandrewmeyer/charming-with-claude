# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `152ca948-a87b-4f0e-af76-edd83ce8807c`  
> - **Started:** 4/3/2026, 12:19:54 PM  
> - **Duration:** 14m 57s  
> - **Exported:** 4/3/2026, 12:34:52 PM  

---

<sub>⏱️ 5s</sub>

### 👤 User

There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

---

<sub>⏱️ 20s</sub>

### ✅ `bash`

**Check current requirements and charmcraft config**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat requirements.txt && echo "---" && cat charmcraft.yaml | head -50

<details>
<summary>61 lines</summary>

```
# pin importlib-metadata version else charmcraft pack will fail to resolve the dependencies for the pydeps-installed otlp library
importlib-metadata~=6.0.0
ops
jsonschema==4.17.0
lightkube==0.11.0
lightkube-models==1.24.1.4
tenacity==8.2.3

# PYDEPS
# lib/charms/tempo_k8s/v1/charm_tracing.py
opentelemetry-exporter-otlp-proto-http==1.21.0

# lib/charms/tls_certificates_interface/v2/tls_certificates.py
jsonschema
cryptography
# lib/charms/tempo_k8s/v1/tracing.py
pydantic>=2
# lib/charms/prometheus_k8s/v0/prometheus_scrape.py
cosl
---
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
name: tempo-k8s
type: charm

assumes:
  - k8s-api

  # Juju 3.4.0 needed for pebble notify
  - juju >= 3.4.0

description: |
  Tempo is a distributed tracing backend by Grafana, supporting Jaeger,
  Zipkin, and OpenTelemetry protocols.

summary: |
  Tempo is a distributed tracing backend by Grafana.

links:
  documentation: https://discourse.charmhub.io/t/tempo-k8s-docs-index/14005
  website:
    - https://charmhub.io/tempo-k8s
  source:
    - https://github.com/canonical/tempo-k8s-operator
  issues:
    - https://github.com/canonical/tempo-k8s-operator/issues

containers:
  tempo:
    resource: tempo-image
    mounts:
      - storage: data
        location: /tmp/tempo

resources:
  tempo-image:
    type: oci-image
    description: OCI image for Tempo
    # Included for simplicity in integration tests
    # see https://hub.docker.com/r/grafana/tempo/tags
    upstream-source: grafana/tempo:2.4.0

provides:
  grafana-dashboard:
    interface: grafana_dashboard
    description: |
      Forwards the built-in grafana dashboard(s) for monitoring Tempo.
  grafana-source:
    interface: grafana_datasource
    description: |
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 20s</sub>

### ✅ `task`

**Exploring charm structure**

<details>
<summary>Arguments</summary>

```json
{
  "name": "explore-charm",
  "agent_type": "explore",
  "description": "Exploring charm structure",
  "prompt": "Explore the charm codebase at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4. I need to understand:\n1. The main charm class and what it does (src/ directory)\n2. All ops library usage patterns (event handlers, StatusBase subclasses, testing patterns, etc.)\n3. What version of ops is currently being used\n4. Any use of ops.testing or scenario testing\n5. Any use of tracing/ops-tracing\n6. The test files structure\n7. Any deprecation warnings or patterns that might be affected by ops upgrades\n\nPlease read all files in src/, tests/, and lib/ directories and give me a comprehensive overview.",
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

**Check current and latest ops versions**

$ pip show ops 2>/dev/null | grep Version && pip index versions ops 2>/dev/null | head -5

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

<sub>⏱️ 35s</sub>

### ✅ `web_search`

**ops Python charm library latest release notes changelog 2024 2025**

<details>
<summary>Arguments</summary>

```json
{
  "query": "ops Python charm library latest release notes changelog 2024 2025"
}
```

</details>

```
{"type":"text","text":{"value":"Here’s a summary of the latest release notes and changelog information for the Ops Python Charm Library (\"ops\") across 2024 and 2025:\n\n### Latest Ops Library Releases\n- **Ops 3.6.0** (Released Feb 2026): This is currently the latest version and requires Python 3.10 or above. It's part of the Charm SDK ecosystem for building Kubernetes and machine charms. Notable for its robustness and updated features for integrating with Juju. For tutorials and detailed documentation, see the [official PyPI page]【3:0†source】.\n\n### Key Features and Changelog (2024–2025)\n\n#### **Ops 3.0+ Series (2024–2025)**\n- **Major Milestones:**\n  - Dropped support for Python 3.8 in mainline releases.\n  - Added new low-level APIs closely matching Juju hook commands, with internal refactoring to support these changes.\n  - Introduction of ops 2.23 for Ubuntu 20.04 support, providing feature parity and ongoing security fixes for environments not yet on Python 3.10+【3:4†source】.\n\n#### **Ops 3.5.0** (Late 2025)\n- **New features:**\n  - Introduced an environment variable to control how unhandled exceptions are reported.\n  - Deprecated `ops.testing.Context.charm_spec`.\n  - Updated integration test charms with an improved test plugin.\n  - Cleanups and expanded type annotations in scenario tests.\n- **Ecosystem:** Multiple associated projects released compatible updates, such as Jubilant, Concierge, and Pebble.\n- **Maintenance improvements:** Continued ecosystem work on code ownership, testability, and metadata surfacing for interfaces【3:7†source】.\n\n#### **Ops 3.4.0 Beta Series**\n- **Preview API:** Beta releases featured a new low-level API compatible with Juju hook commands, aiming to improve charm compatibility and extensibility.\n- **Feedback sought:** Community asked to test integration for robust backward compatibility checks【3:5†source】【3:1†source】.\n\n#### **Ops 2.16.0 / 2.17.0 (Late 2024)**\n- Focused on robust parsing of all `JUJU_*` environment variables within a new internal dataclass.\n- Improvements in testing, CI, and documentation infrastructure【3:6†source】【3:8†source】.\n\n### Documentation and Resources\n- [Official Documentation (ops.readthedocs.io)](https://ops.readthedocs.io/en/)\n- [Canonical/operator GitHub repository with CHANGES.md for full changelog](https://github.com/canonical/operator)\n- [Charm Tech Pulse reports on Charmhub](https://discourse.charmhub.io/tag/charm-tech-pulse)\n\n### How to Stay Updated\n- For the most up-to-date changelogs and precise version history, consult:\n  - [GitHub CHANGES.md](https://github.com/canonical/operator/blob/main/CHANGES.md)\n  - [Charmhub’s \"Charm Tech Pulse\" reports](https://discourse.charmhub.io/search?q=Charm%20Tech%20pulse)\n  - [PyPI release log for ops](https://pypi.org/project/ops/)\n\nIf you need a changelog for a specific version or want full diffs, check the CHANGES.md file on the canonical/operator GitHub or the official documentation, which are updated with every release【3:2†source】【3:3†source】【3:7†source】【3:6†source】【3:4†source】.","annotations":[{"text":"【3:0†source】","start_index":502,"end_index":514,"url_citation":{"title":"ops · PyPI","url":"https://pypi.org/project/ops/"}},{"text":"【3:4†source】","start_index":944,"end_index":956,"url_citation":{"title":"Charm Tech pulse 2025#13 - charm - Charmhub","url":"https://discourse.charmhub.io/t/charm-tech-pulse-2025-13/18164"}},{"text":"【3:7†source】","start_index":1518,"end_index":1530,"url_citation":{"title":"Charm Tech pulse 2025#25 - charm - Charmhub","url":"https://discourse.charmhub.io/t/charm-tech-pulse-2025-25/19584"}},{"text":"【3:5†source】","start_index":1818,"end_index":1830,"url_citation":{"title":"Charm Tech pulses 2025#22 & 23 - charm - Charmhub","url":"https://discourse.charmhub.io/t/charm-tech-pulses-2025-22-23/19352"}},{"text":"【3:1†source】","start_index":1830,"end_index":1842,"url_citation":{"title":"Charm Tech pulse 2025#21 - charm - Charmhub","url":"https://discourse.charmhub.io/t/charm-tech-pulse-2025-21/19121"}},{"text":"【3:6†source】","start_index":2048,"end_index":2060,"url_citation":{"title":"ops library 2.16.0 released: parsing all `JUJU_*` env vars in one place ...","url":"https://discourse.charmhub.io/t/ops-library-2-16-0-released-parsing-all-juju-env-vars-in-one-place-and-other-improvements/15367"}},{"text":"【3:8†source】","start_index":2060,"end_index":2072,"url_citation":{"title":"ops · PyPI · Python 包索引","url":"https://pypi.ac.cn/project/ops/"}},{"text":"【3:2†source】","start_index":2940,"end_index":2952,"url_citation":{"title":"Pure Python framework for writing Juju charms. - GitHub","url":"https://github.com/canonical/operator"}},{"text":"【3:3†source】","start_index":2952,"end_index":2964,"url_citation":{"title":"The ops library documentation","url":"https://ops.readthedocs.io/en/"}},{"text":"【3:7†source】","start_index":2964,"end_index":2976,"url_citation":{"title":"Charm Tech pulse 2025#25 - charm - Charmhub","url":"https://discourse.charmhub.io/t/charm-tech-pulse-2025-25/19584"}},{"text":"【3:6†source】","start_index":2976,"end_index":2988,"url_citation":{"title":"ops library 2.16.0 released: parsing all `JUJU_*` env vars in one place ...","url":"https://discourse.charmhub.io/t/ops-library-2-16-0-released-parsing-all-juju-env-vars-in-one-place-and-other-improvements/15367"}},{"text":"【3:4†source】","start_index":2988,"end_index":3000,"url_citation":{"title":"Charm Tech pulse 2025#13 - charm - Charmhub","url":"https://discourse.charmhub.io/t/charm-tech-pulse-2025-13/18164"}}]},"bing_searches":[{"text":"ops Python charm library latest release notes changelog 2024 2025","url":"https://www.bing.com/search?q=ops+Python+charm+library+latest+release+notes+changelog+2024+2025"}],"annotations":null}
```


---

<sub>⏱️ 41s</sub>

### ✅ `web_fetch`

**https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://raw.githubusercontent.com/canonical/operator/main/CHANGES.md",
  "max_length": 20000
}
```

</details>

<details>
<summary>386 lines</summary>

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

* Add a docs link

<note>Content truncated. Call the fetch tool with a start_index of 20000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 4s</sub>

### ✅ `bash`

**Check ops-tracing and ops-scenario versions**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && pip show ops-tracing ops-scenario 2>/dev/null && echo "---" && pip index versions ops-tracing 2>/dev/null | head -3 && pip index versions ops-scenario 2>/dev/null | head -3

<details>
<summary>29 lines</summary>

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
---
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
ops-tracing (3.7.0)
Available versions: 3.7.0, 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 0.9.6, 0.9.4, 0.9.3, 0.9.2, 0.9.1, 0.9.0
  INSTALLED: 3.7.0
ops-scenario (8.7.0)
Available versions: 8.7.0, 8.6.0, 8.5.2, 8.5.1, 8.5.0, 8.4.0, 8.3.1, 8.3.0, 8.2.0, 8.1.0, 8.0.0, 7.23.2, 7.23.1, 7.23.0, 7.22.0, 7.21.1, 7.21.0, 7.20.0, 7.19.4, 7.2.0, 7.1.3, 7.1.2, 7.1.1, 7.0.5, 7.0.4, 7.0.3, 7.0.2, 7.0.1, 7.0.0, 6.1.7, 6.1.6, 6.1.5, 6.1.4, 6.1.3, 6.1.2, 6.1.1, 6.1.0, 6.0.5, 6.0.4, 6.0.3, 6.0.2, 6.0.1, 6.0, 5.8.1, 5.8, 5.7.1, 5.7, 5.6.2, 5.6.1, 5.6, 5.5, 5.4.1, 5.4, 5.3.1, 5.3, 5.2.2, 5.2.1, 5.2, 5.1.3, 5.1.2, 5.1.1, 5.1.0, 5.0, 4.0.4.1, 4.0.4, 4.0.3, 4.0.2, 4.0.1, 4.0, 3.1, 3.0.2, 3.0.1, 2.2, 2.1.3.5, 2.1.3.4, 2.1.3.3, 2.1.3.2, 2.1.3.1, 2.1.3, 2.1.2.5, 2.1.2.4, 2.1.2.3, 2.1.2.2, 2.1.2.1, 2.1.1, 2.1.0, 2.0.5, 2.0.4, 2.0.0
  INSTALLED: 8.7.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 2s</sub>

### ✅ `bash`

**List test files**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && find . -name "*.py" -path "*/tests/*" | head -20 && echo "---" && ls tests/

<details>
<summary>23 lines</summary>

```
./tests/integration/test_tls.py
./tests/integration/conftest.py
./tests/integration/helpers.py
./tests/integration/test_scaling_monolithic.py
./tests/integration/test_ingressed_tls.py
./tests/integration/tester-grpc/src/resources/webserver.py
./tests/integration/tester-grpc/src/charm.py
./tests/integration/test_integration.py
./tests/integration/tester/src/resources/webserver.py
./tests/integration/tester/src/charm.py
./tests/interface/conftest.py
./tests/interface/test_tracing.py
./tests/unit/test_charm.py
./tests/unit/test_tempo.py
./tests/scenario/test_ingressed_tracing.py
./tests/scenario/test_tls.py
./tests/scenario/conftest.py
./tests/scenario/helpers.py
./tests/scenario/test_charm.py
./tests/scenario/test_a_charm_tracer_multi_import_warning.py
---
integration  interface	manual	scenario  unit
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 10s</sub>

### ✅ `bash`

**Check git history**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && git log --oneline -10

```
16d9d06 (grafted, HEAD, origin/main, origin/HEAD, main) deprecation notice in readme (#173)
<exited with exit code 0>
```


---

<sub>⏱️ 1m 10s</sub>

### ✅ `bash`

**Read scenario test setup files**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat tests/scenario/conftest.py && echo "===" && cat tests/scenario/helpers.py

<details>
<summary>22 lines</summary>

```
from unittest.mock import patch

import pytest
from scenario import Context

from charm import TempoCharm


@pytest.fixture
def tempo_charm():
    with patch("charm.KubernetesServicePatch"):
        with patch("lightkube.core.client.GenericSyncClient"):
            yield TempoCharm


@pytest.fixture(scope="function")
def context(tempo_charm):
    return Context(charm_type=tempo_charm)
===
from pathlib import Path

import scenario
import yaml

from tempo import Tempo


def get_tempo_config(container: scenario.Container, context: scenario.Context):
    fs = container.get_filesystem(context)
    cfg_path = Path(str(fs) + Tempo.config_path)
    return yaml.safe_load(cfg_path.read_text())
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 14s</sub>

### ✅ `bash`

**Read main scenario tests**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat tests/scenario/test_charm.py

<details>
<summary>170 lines</summary>

```
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml
from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
from charms.tempo_k8s.v2.tracing import TracingRequirerAppData
from ops import pebble
from scenario import Container, Mount, Relation, State
from scenario.sequences import check_builtin_sequences
from scenario.state import Notice, _BoundNotice

from tempo import Tempo
from tests.scenario.helpers import get_tempo_config

TEMPO_CHARM_ROOT = Path(__file__).parent.parent.parent


@pytest.fixture(params=(True, False))
def base_state(request):
    return State(
        leader=request.param,
        containers=[Container("tempo", can_connect=True)],
    )


def test_builtin_sequences(tempo_charm, base_state):
    with charm_tracing_disabled():
        check_builtin_sequences(tempo_charm, template_state=base_state)


def test_start(context, base_state):
    # verify the charm runs at all with and without leadership
    with charm_tracing_disabled():
        context.run("start", base_state)


@pytest.mark.parametrize("requested_protocol", ("otlp_grpc", "zipkin"))
def test_tempo_restart_on_ingress_v2_changed(context, tmp_path, requested_protocol):
    # GIVEN
    # an initial configuration with an otlp_http receiver
    container, tempo = _tempo_mock_with_initial_config(tmp_path)

    # the remote end requests an otlp_grpc endpoint
    ingress = Relation(
        "tracing",
        remote_app_data=TracingRequirerAppData(receivers=[requested_protocol]).dump(),
    )

    # WHEN
    # the charm receives an ingress(v2) relation-changed requesting an otlp_grpc receiver
    state = State(leader=True, containers=[tempo], relations=[ingress])
    context.run(ingress.changed_event, state)

    # THEN
    # Tempo pushes a new config to the container filesystem
    new_config = get_tempo_config(tempo, context)
    expected_config = Tempo(container).generate_config(
        ["otlp_http", requested_protocol],
    )
    assert new_config == expected_config
    # AND restarts the pebble service.
    assert (
        context.output_state.get_container("tempo").service_status["tempo"]
        is pebble.ServiceStatus.ACTIVE
    )


def _tempo_mock_with_initial_config(tmp_path, tempo_ready_svc_exists: bool = True):
    tempo_config = tmp_path / "tempo.yaml"
    container = MagicMock()
    container.can_connect = lambda: True
    # prevent tls_ready from reporting True
    container.exists = lambda path: (
        False if path in [Tempo.tls_cert_path, Tempo.tls_key_path, Tempo.tls_ca_path] else True
    )
    initial_config = Tempo(container).generate_config(["otlp_http"])
    tempo_config.write_text(yaml.safe_dump(initial_config))
    layer_raw = {
        "summary": "tempo layer",
        "description": "foo",
        "services": {
            "tempo": {"startup": "enabled"},
        },
    }
    if tempo_ready_svc_exists:
        layer_raw["services"]["tempo-ready"] = {"startup": "disabled"}

    tempo = Container(
        "tempo",
        can_connect=True,
        layers={
            "tempo": pebble.Layer(
                layer_raw,
            ),
        },
        service_status={
            # we don't have a way to check if the service has been restarted: all that scenario does ATM is set it to
            # 'active'.
            # so as a way to check that it's been restarted, we must set it to inactive here.
            "tempo": pebble.ServiceStatus.INACTIVE,
        },
        mounts={
            "data": Mount("/etc/tempo/tempo.yaml", tempo_config),
        },
    )
    return container, tempo


def test_tempo_tracing_created_before_pebble_ready(context, tmp_path):
    # GIVEN there is no plan yet
    tempo = Container(
        "tempo",
        can_connect=True,
    )

    # WHEN
    # the charm receives a tracing-relation-created requesting an otlp_grpc receiver
    tracing = Relation(
        "tracing",
        remote_app_data={"receivers": '["otlp_http"]'},
        local_app_data={
            "receivers": '[{"protocol": {"name": "otlp_grpc", "type": "grpc"} , "url": "foo.com:10"}, '
            '{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://foo.com:11"}, ',
        },
    )
    state = State(leader=True, containers=[tempo], relations=[tracing])
    state_out = context.run(tracing.created_event, state)

    # THEN
    # tempo still has no services
    tempo_out = state_out.get_container("tempo")
    assert not tempo_out.services


def test_tracing_storage_is_configured_to_local_without_relation(context, tmp_path):
    # GIVEN tempo mock
    container, tempo = _tempo_mock_with_initial_config(tmp_path)

    # WHEN any event comes in
    state = State(leader=True, containers=[tempo], relations=[])
    context.run("update-status", state)

    # THEN tempo's config has a local storage configured
    config = get_tempo_config(tempo, context)
    expected_config = Tempo(container).generate_config(["otlp_http"])
    assert config == expected_config
    assert config["storage"]["trace"]["backend"] == "local"


@pytest.mark.parametrize(
    "relation_data",
    (
        {},
        {
            "access-key": "key",
            "bucket": "tempo",
            "endpoint": "http://1.2.3.4:9000",
            "secret-key": "soverysecret",
        },
    ),
)
def test_tracing_storage_is_configured_to_s3_if_s3_relation_filled(
    context,
    tmp_path,
    relation_data,
):
    # GIVEN tempo mock
    container, tempo = _tempo_mock_with_initial_config(tmp_path)

    # WHEN a charm receives an s3 relation
    s3_relation = Relation(
        "s3",
        remote_app_data=relation_data,
        local_app_data={"bucket": "tempo"},
    )

    state = State(leader=True, containers=[tempo], relations=[s3_relation])
    context.run(s3_relation.changed_event, state)

    # THEN
    # Tempo's config contains the data from the relation
    new_config = get_tempo_config(tempo, context)
    expected_config = Tempo(container).generate_config(["otlp_http"], relation_data)
    assert new_config == expected_config


def test_ready_check_on_resume(context, tmp_path, caplog, monkeypatch):
    # GIVEN the charm has no tempo-ready service
    container, tempo = _tempo_mock_with_initial_config(tmp_path, tempo_ready_svc_exists=False)

    state = State(leader=True, containers=[tempo])

    # WHEN we receive a custom-notice event
    with caplog.at_level("DEBUG"):
        monkeypatch.setenv("SCENARIO_SKIP_CONSISTENCY_CHECKS", "1")
        # scenario doesn't play nice in this very edge case
        context.run(_BoundNotice(Notice(Tempo.tempo_ready_notice_key), tempo).event, state)
        monkeypatch.delenv("SCENARIO_SKIP_CONSISTENCY_CHECKS")

    # THEN we get a debug-log but the charm doesn't error
    assert "`tempo-ready` service cannot be stopped at this time (probably doesn't exist)." in {
        r.message for r in caplog.records
    }
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 14s</sub>

### ✅ `bash`

**Read main charm file**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat src/charm.py

<details>
<summary>17 lines</summary>

```
Output too large to read at once (23.8 KB). Saved to: /tmp/copilot-tool-output-1775172068738-o8utlt.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charmed Operator for Tempo; a lightweight object storage based tracing backend."""

import logging
import re
import socket
from pathlib import Path
from typing import Optional, Set, Tuple

import ops
from charms.data_platform_libs.v0.s3 import S3Requirer
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.grafana_k8s.v0.grafana_source import GrafanaSourceProvi
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 21s</sub>

### ✅ `bash`

**Read full charm.py**

$ cat /tmp/copilot-tool-output-1775172068738-o8utlt.txt

<details>
<summary>17 lines</summary>

```
Output too large to read at once (23.8 KB). Saved to: /tmp/copilot-tool-output-1775172075433-34tfxm.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charmed Operator for Tempo; a lightweight object storage based tracing backend."""

import logging
import re
import socket
from pathlib import Path
from typing import Optional, Set, Tuple

import ops
from charms.data_platform_libs.v0.s3 import S3Requirer
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.grafana_k8s.v0.grafana_source import GrafanaSourceProvi
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 21s</sub>

### ✅ `bash`

**Read other scenario tests**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat tests/scenario/test_tls.py && echo "===" && cat tests/scenario/test_ingressed_tracing.py

<details>
<summary>198 lines</summary>

```
import socket
from unittest.mock import patch

import pytest
from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
from charms.tempo_k8s.v2.tracing import TracingProviderAppData, TracingRequirerAppData
from scenario import Container, Relation, State

from charm import Tempo


@pytest.fixture
def base_state():
    return State(leader=True, containers=[Container("tempo", can_connect=False)])


def update_relations_tls_and_verify(
    base_state,
    context,
    has_ingress,
    local_has_tls,
    local_scheme,
    relations,
    remote_scheme,
    tracing,
):
    state = base_state.replace(relations=relations)
    with charm_tracing_disabled(), patch.object(Tempo, "tls_ready", local_has_tls):
        out = context.run(tracing.changed_event, state)
    tracing_provider_app_data = TracingProviderAppData.load(
        out.get_relations(tracing.endpoint)[0].local_app_data
    )
    actual_url = tracing_provider_app_data.receivers[0].url
    expected_url = f"{remote_scheme if has_ingress else local_scheme}://{socket.getfqdn() if not has_ingress else 'foo.com.org'}:4318"
    assert actual_url == expected_url
    return out


@pytest.mark.parametrize("remote_has_tls", (True, False))
@pytest.mark.parametrize("local_has_tls", (True, False))
@pytest.mark.parametrize("has_ingress", (True, False))
def test_tracing_endpoints_with_tls(
    context, base_state, has_ingress, local_has_tls, remote_has_tls
):
    tracing = Relation(
        "tracing",
        remote_app_data=TracingRequirerAppData(receivers=["otlp_http"]).dump(),
    )
    relations = [tracing]

    local_scheme = "https" if local_has_tls else "http"
    remote_scheme = "https" if remote_has_tls else "http"

    if has_ingress:
        relations.append(
            Relation(
                "ingress",
                remote_app_data={"scheme": remote_scheme, "external_host": "foo.com.org"},
            )
        )

    update_relations_tls_and_verify(
        base_state,
        context,
        has_ingress,
        local_has_tls,
        local_scheme,
        relations,
        remote_scheme,
        tracing,
    )


@pytest.mark.parametrize("has_ingress", (True, False))
def test_tracing_endpoints_tls_added_then_removed(context, base_state, has_ingress):
    tracing = Relation(
        "tracing",
        remote_app_data=TracingRequirerAppData(receivers=["otlp_http"]).dump(),
    )
    relations = [tracing]

    local_scheme = "http"
    remote_scheme = "http"

    if has_ingress:
        relations.append(
            Relation(
                "ingress",
                remote_app_data={"scheme": remote_scheme, "external_host": "foo.com.org"},
            )
        )

    result_state = update_relations_tls_and_verify(
        base_state, context, has_ingress, False, local_scheme, relations, remote_scheme, tracing
    )

    # then we check the scenario where TLS gets enabled

    local_scheme = "https"
    remote_scheme = "https"

    if has_ingress:
        # as remote_scheme changed, we need to update the ingress relation
        relations.pop()
        relations.append(
            Relation(
                "ingress",
                remote_app_data={"scheme": remote_scheme, "external_host": "foo.com.org"},
            )
        )

    result_state = update_relations_tls_and_verify(
        result_state, context, has_ingress, True, local_scheme, relations, remote_scheme, tracing
    )

    # then we again remove TLS and compare the same thing

    local_scheme = "http"
    remote_scheme = "http"

    if has_ingress:
        # as remote_scheme changed, we need to update the ingress relation
        relations.pop()
        relations.append(
            Relation(
                "ingress",
                remote_app_data={"scheme": remote_scheme, "external_host": "foo.com.org"},
            )
        )

    update_relations_tls_and_verify(
        result_state, context, has_ingress, False, local_scheme, relations, remote_scheme, tracing
    )
===
from unittest.mock import patch

import pytest
import yaml
from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
from scenario import Container, Relation, State

from tempo import Tempo


@pytest.fixture
def base_state():
    return State(leader=True, containers=[Container("tempo", can_connect=False)])


def test_external_url_present(context, base_state):
    # WHEN ingress is related with external_host
    tracing = Relation("tracing", remote_app_data={"receivers": "[]"})
    ingress = Relation("ingress", remote_app_data={"external_host": "1.2.3.4", "scheme": "http"})
    state = base_state.replace(relations=[tracing, ingress])

    with charm_tracing_disabled():
        out = context.run(getattr(tracing, "created_event"), state)

    # THEN external_url is present in tracing relation databag
    tracing_out = out.get_relations(tracing.endpoint)[0]
    assert tracing_out.local_app_data == {
        "receivers": '[{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://1.2.3.4:4318"}]',
    }


@patch("socket.getfqdn", lambda: "1.2.3.4")
def test_ingress_relation_set_with_dynamic_config(context, base_state):
    # WHEN ingress is related with external_host
    ingress = Relation("ingress", remote_app_data={"external_host": "1.2.3.4", "scheme": "http"})
    state = base_state.replace(relations=[ingress])

    with patch.object(Tempo, "is_ready", lambda _: False):
        out = context.run(ingress.joined_event, state)

    expected_rel_data = {
        "http": {
            "routers": {
                f"juju-{state.model.name}-tempo-k8s-jaeger-thrift-http": {
                    "entryPoints": ["jaeger-thrift-http"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-jaeger-thrift-http",
                },
                f"juju-{state.model.name}-tempo-k8s-otlp-http": {
                    "entryPoints": ["otlp-http"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-otlp-http",
                },
                f"juju-{state.model.name}-tempo-k8s-tempo-http": {
                    "entryPoints": ["tempo-http"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-tempo-http",
                },
                f"juju-{state.model.name}-tempo-k8s-zipkin": {
                    "entryPoints": ["zipkin"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-zipkin",
                },
                f"juju-{state.model.name}-tempo-k8s-otlp-grpc": {
                    "entryPoints": ["otlp-grpc"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-otlp-grpc",
                },
                f"juju-{state.model.name}-tempo-k8s-tempo-grpc": {
                    "entryPoints": ["tempo-grpc"],
                    "rule": "ClientIP(`0.0.0.0/0`)",
                    "service": f"juju-{state.model.name}-tempo-k8s-service-tempo-grpc",
                },
            },
            "services": {
                f"juju-{state.model.name}-tempo-k8s-service-jaeger-thrift-http": {
                    "loadBalancer": {"servers": [{"url": "http://1.2.3.4:14268"}]}
                },
                f"juju-{state.model.name}-tempo-k8s-service-otlp-http": {
                    "loadBalancer": {"servers": [{"url": "http://1.2.3.4:4318"}]}
                },
                f"juju-{state.model.name}-tempo-k8s-service-tempo-http": {
                    "loadBalancer": {"servers": [{"url": "http://1.2.3.4:3200"}]}
                },
                f"juju-{state.model.name}-tempo-k8s-service-zipkin": {
                    "loadBalancer": {"servers": [{"url": "http://1.2.3.4:9411"}]}
                },
                f"juju-{state.model.name}-tempo-k8s-service-otlp-grpc": {
                    "loadBalancer": {"servers": [{"url": "h2c://1.2.3.4:4317"}]},
                },
                f"juju-{state.model.name}-tempo-k8s-service-tempo-grpc": {
                    "loadBalancer": {"servers": [{"url": "h2c://1.2.3.4:9096"}]}
                },
            },
        },
    }

    # THEN dynamic config is present in ingress relation
    ingress_out = out.get_relations(ingress.endpoint)[0]
    assert yaml.safe_load(ingress_out.local_app_data["config"]) == expected_rel_data
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 30s</sub>

### ✅ `bash`

**Read charm.py content**

$ cat /tmp/copilot-tool-output-1775172075433-34tfxm.txt | head -200

<details>
<summary>176 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charmed Operator for Tempo; a lightweight object storage based tracing backend."""

import logging
import re
import socket
from pathlib import Path
from typing import Optional, Set, Tuple

import ops
from charms.data_platform_libs.v0.s3 import S3Requirer
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.grafana_k8s.v0.grafana_source import GrafanaSourceProvider
from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
from charms.observability_libs.v0.kubernetes_service_patch import KubernetesServicePatch
from charms.observability_libs.v1.cert_handler import CertHandler
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from charms.tempo_k8s.v1.charm_tracing import trace_charm
from charms.tempo_k8s.v2.tracing import (
    ReceiverProtocol,
    RequestEvent,
    TracingEndpointProvider,
)
from charms.traefik_route_k8s.v0.traefik_route import TraefikRouteRequirer
from ops.charm import (
    CharmBase,
    CollectStatusEvent,
    PebbleNoticeEvent,
    RelationEvent,
    WorkloadEvent,
)
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus
from ops.pebble import APIError

from tempo import Tempo

logger = logging.getLogger(__name__)


@trace_charm(
    tracing_endpoint="tempo_otlp_http_endpoint",
    server_cert="server_cert",
    extra_types=(Tempo, TracingEndpointProvider),
)
class TempoCharm(CharmBase):
    """Charmed Operator for Tempo; a distributed tracing backend."""

    def __init__(self, *args):
        super().__init__(*args)
        self.tempo = tempo = Tempo(
            self.unit.get_container("tempo"),
            external_host=self.hostname,
            # we need otlp_http receiver for charm_tracing
            enable_receivers=["otlp_http"],
        )

        # TODO:
        #  ingress route provisioning a separate TCP ingress for each receiver if GRPC doesn't work directly
        self.ingress = TraefikRouteRequirer(self, self.model.get_relation("ingress"), "ingress")  # type: ignore

        self.cert_handler = CertHandler(
            self,
            key="tempo-server-cert",
            sans=[self.hostname],
        )

        self.s3_requirer = S3Requirer(self, Tempo.s3_relation_name, Tempo.s3_bucket_name)

        # configure this tempo as a datasource in grafana
        self.grafana_source_provider = GrafanaSourceProvider(
            self,
            source_type="tempo",
            source_url=self._external_http_server_url,
            refresh_event=[
                # refresh the source url when TLS config might be changing
                self.on[self.cert_handler.certificates_relation_name].relation_changed,
                # or when ingress changes
                self.ingress.on.ready,
            ],
        )
        # # Patch the juju-created Kubernetes service to contain the right ports
        external_ports = tempo.get_external_ports(self.app.name)
        self._service_patcher = KubernetesServicePatch(self, external_ports)
        # Provide ability for Tempo to be scraped by Prometheus using prometheus_scrape
        self._scraping = MetricsEndpointProvider(
            self,
            relation_name="metrics-endpoint",
            jobs=[{"static_configs": [{"targets": [f"*:{tempo.tempo_http_server_port}"]}]}],
        )
        # Enable log forwarding for Loki and other charms that implement loki_push_api
        self._logging = LogProxyConsumer(
            self, relation_name="logging", log_files=[self.tempo.log_path], container_name="tempo"
        )
        self._grafana_dashboards = GrafanaDashboardProvider(
            self, relation_name="grafana-dashboard"
        )

        self.tracing = TracingEndpointProvider(self, external_url=self._external_url)

        if not self.is_consistent():
            logger.error(
                f"Inconsistent deployment. {self.unit.name} will be shutting down. "
                "This likely means you need to add an s3 integration. "
                "This charm will be unresponsive and refuse to handle any event until "
                "the situation is resolved by the cloud admin, to avoid data loss."
            )
            self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)

            if self.tempo.is_tempo_service_defined:
                self.tempo.shutdown()

            return  # refuse to handle any other event as we can't possibly know what to do.

        self.framework.observe(
            self.on["ingress"].relation_created, self._on_ingress_relation_created
        )
        self.framework.observe(
            self.on["ingress"].relation_joined, self._on_ingress_relation_joined
        )
        self.framework.observe(self.on.leader_elected, self._on_leader_elected)
        self.framework.observe(self.on.leader_settings_changed, self._on_leader_settings_changed)
        self.framework.observe(self.ingress.on.ready, self._on_ingress_ready)

        self.framework.observe(self.on.tempo_pebble_ready, self._on_tempo_pebble_ready)
        self.framework.observe(
            self.on.tempo_pebble_custom_notice, self._on_tempo_pebble_custom_notice
        )
        self.framework.observe(self.on.update_status, self._on_update_status)
        self.framework.observe(
            self.s3_requirer.on.credentials_changed, self._on_s3_credentials_changed
        )
        self.framework.observe(self.s3_requirer.on.credentials_gone, self._on_s3_credentials_gone)
        self.framework.observe(self.tracing.on.request, self._on_tracing_request)
        self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)
        self.framework.observe(self.on.list_receivers_action, self._on_list_receivers_action)
        self.framework.observe(self.cert_handler.on.cert_changed, self._on_cert_handler_changed)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.tracing.on.broken, self._on_tracing_broken)
        self.framework.observe(
            self.on.tempo_peers_relation_created, self._on_tempo_peers_relation_created
        )
        self.framework.observe(
            self.on.tempo_peers_relation_changed, self._on_tempo_peers_relation_changed
        )

    @property
    def _external_http_server_url(self) -> str:
        """External url of the http(s) server."""
        return f"{self._external_url}:{self.tempo.tempo_http_server_port}"

    @property
    def _external_url(self) -> str:
        """Return the external url."""
        if self.ingress.is_ready():
            ingress_url = f"{self.ingress.scheme}://{self.ingress.external_host}"
            logger.debug("This unit's ingress URL: %s", ingress_url)
            return ingress_url

        # If we do not have an ingress, then use the pod hostname.
        # The reason to prefer this over the pod name (which is the actual
        # hostname visible from the pod) or a K8s service, is that those
        # are routable virtually exclusively inside the cluster (as they rely)
        # on the cluster's DNS service, while the ip address is _sometimes_
        # routable from the outside, e.g., when deploying on MicroK8s on Linux.
        return self._internal_url

    @property
    def _internal_url(self) -> str:
        scheme = "https" if self.tls_available else "http"
        return f"{scheme}://{self.hostname}"

    @property
    def tls_available(self) -> bool:
        """Return True if tls is enabled and the necessary certs are found."""
        return (
            self.cert_handler.enabled
            and (self.cert_handler.server_cert is not None)
            and (self.cert_handler.private_key is not None)
            and (self.cert_handler.ca_cert is not None)
        )

    @property
    def _s3_config(self) -> Optional[dict]:
        if not self.s3_requirer.relations:
            return None
        s3_config = self.s3_requirer.get_s3_connection_info()
        if (
            s3_config
            and "bucket" in s3_config
            and "endpoint" in s3_config
            and "access-key" in s3_config
            and "secret-key" in s3_config
        ):
            return s3_config
        return None
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 30s</sub>

### ✅ `bash`

**Read tox config**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat tox.ini

<details>
<summary>99 lines</summary>

```
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

[tox]
skipsdist=True
skip_missing_interpreters = True
envlist = lint, unit, scenario, static-charm, static-lib

[vars]
src_path = {toxinidir}/src/
tst_path = {toxinidir}/tests/
lib_path = {toxinidir}/lib/charms/tempo_k8s
all_path = {[vars]src_path} {[vars]tst_path} {[vars]lib_path}

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
    ruff
    isort
commands =
    isort {[vars]all_path}
    black {[vars]all_path}
    ruff check {[vars]all_path} --fix

[testenv:lint]
description = Check code against coding style standards
deps =
    black
    ruff
    codespell<2.3.0 # https://github.com/codespell-project/codespell/issues/3430
commands =
    codespell {[vars]all_path}
    ruff check {[vars]all_path}
    black --check --diff {[vars]all_path}

[testenv:unit]
description = Run unit tests
deps =
    pytest<8.2.0 # https://github.com/pytest-dev/pytest/issues/12263
    coverage[toml]
    .[lib_pydeps]
    -r{toxinidir}/requirements.txt
commands =
    coverage run --source={[vars]src_path} \
        -m pytest  -v --tb native -s {posargs} {[vars]tst_path}unit
    coverage report

[testenv:scenario]
description = Run scenario tests
deps =
    pytest<8.2.0 # https://github.com/pytest-dev/pytest/issues/12263
    coverage[toml]
    ops-scenario>=4.0.3,<7.0.0
    .[lib_pydeps]
    -r{toxinidir}/requirements.txt
commands =
    coverage run --source={[vars]src_path} \
        -m pytest  -v --tb native -s {posargs} {[vars]tst_path}scenario
    coverage report

[testenv:integration]
description = Run integration tests
deps =
    pytest<8.2.0 # https://github.com/pytest-dev/pytest/issues/12263
    # see https://github.com/juju/python-libjuju/issues/1025
    juju<=3.3.0,>=3.0
    pytest-operator
    requests
    -r{toxinidir}/requirements.txt
    # tracegen
    opentelemetry-exporter-otlp-proto-grpc
commands =
    pytest -v --tb native --log-cli-level=INFO {[vars]tst_path}integration -s {posargs}

[testenv:interface]
description = Run interface tests
deps =
    pytest<8.2.0 # https://github.com/pytest-dev/pytest/issues/12263
    -r{toxinidir}/requirements.txt
    .[lib_pydeps]
    pytest-interface-tester
    # git+https://github.com/canonical/pytest-interface-tester
commands =
    pytest -v --tb native --log-cli-level=INFO -s {posargs} {[vars]tst_path}interface


[testenv:static-{charm,lib}]
description = Static code checking
deps =
    # pydeps
    .[lib_pydeps]
    pyright==1.1.340
    -r{toxinidir}/requirements.txt
commands =
    charm: pyright --pythonversion 3.8 {[vars]src_path}
    lib: pyright --pythonversion 3.8 {[vars]lib_path}
    lib: /usr/bin/env sh -c 'for m in $(git diff main --name-only {[vars]lib_path}); do if git ls-tree -r HEAD --name-only | grep -q "^$m$"; then  if ! git diff main $m | grep -q "+LIBPATCH\|+LIBAPI"; then echo "You forgot to bump the version on $m!"; exit 1; fi; fi; done'
allowlist_externals = /usr/bin/env
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 53s</sub>

### ✅ `bash`

**Read remaining test files**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat tests/scenario/test_a_charm_tracer_multi_import_warning.py && echo "===" && cat tests/unit/test_charm.py | head -80

<details>
<summary>106 lines</summary>

```
# WARNING ensure that this test module runs before any other scenario test file, else the
# imports from previous tests will pollute the sys.modules and cause this test to fail.
# I know this is horrible but yea, couldn't find a better way to fix the issue. Tried:
# - delete from sys.modules all modules containing 'charms.tempo_k8s'
# - delete from sys.modules all modules containing 'otlp_http'


from unittest.mock import patch

# this test file is intentionally quite broken, don't modify the imports
# import autoinstrument from charms.[...]
from charms.tempo_k8s.v1.charm_tracing import _autoinstrument as autoinstrument
from ops import CharmBase
from scenario import Context, State

# import trace from lib.charms.[...]
from lib.charms.tempo_k8s.v1.charm_tracing import trace


@trace
def _my_fn(foo):
    return foo + 1


class MyCharmSimpleEvent(CharmBase):
    META = {"name": "margherita"}

    def __init__(self, fw):
        super().__init__(fw)
        fw.observe(self.on.start, self._on_start)

    def _on_start(self, _):
        _my_fn(2)

    @property
    def tempo(self):
        return "foo.bar:80"


autoinstrument(MyCharmSimpleEvent, "tempo")


def test_charm_tracer_multi_import_warning(caplog, monkeypatch):
    """Check that we warn the user in case the test is importing tracing symbols from multiple paths.

    See https://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html#the-double-import-trap
    for a great explanation of what's going on.
    """
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmSimpleEvent, meta=MyCharmSimpleEvent.META)
        with caplog.at_level("WARNING"):
            ctx.run("start", State())

        spans = f.call_args_list[0].args[0]
        assert [span.name for span in spans] == [
            # we're only able to capture the _my_fn span because of the fallback behaviour
            "function call: _my_fn",
            "method call: MyCharmSimpleEvent._on_start",
            "event: start",
            "margherita/0: start event",
        ]
        assert "Tracer not found in `tracer` context var." in caplog.records[0].message
===
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import socket
import unittest
from unittest.mock import patch

from ops.model import ActiveStatus
from ops.testing import Harness

from charm import TempoCharm

CONTAINER_NAME = "tempo"


class TestTempoCharm(unittest.TestCase):
    @patch("charm.KubernetesServicePatch", lambda x, y: None)
    def setUp(self):
        self.harness = Harness(TempoCharm)
        self.harness.set_model_name("testmodel")
        self.addCleanup(self.harness.cleanup)
        self.harness.set_leader(True)
        self.harness.begin_with_initial_hooks()
        self.maxDiff = None  # we're comparing big traefik configs in tests

    def test_tempo_pebble_ready(self):
        service = self._container.get_service("tempo")
        self.assertTrue(service.is_running())
        self.assertEqual(self.harness.model.unit.status, ActiveStatus())

    def test_entrypoints_are_generated_with_sanitized_names(self):
        expected_entrypoints = {
            "entryPoints": {
                "tempo-http": {"address": ":3200"},
                "tempo-grpc": {"address": ":9096"},
                "zipkin": {"address": ":9411"},
                "otlp-grpc": {"address": ":4317"},
                "otlp-http": {"address": ":4318"},
                "jaeger-thrift-http": {"address": ":14268"},
            }
        }
        self.assertEqual(self.harness.charm._static_ingress_config, expected_entrypoints)

    def test_tracing_relation_updates_protocols_as_requested(self):
        self.harness.set_leader(True)
        self.harness.container_pebble_ready("tempo")

        tracing_rel_id = self.harness.add_relation("tracing", "grafana")
        self.harness.add_relation_unit(tracing_rel_id, "grafana/0")
        self.harness.update_relation_data(
            tracing_rel_id, "grafana", {"receivers": '["otlp_http"]'}
        )

        rel_data = self.harness.get_relation_data(tracing_rel_id, self.harness.charm.app.name)
        logging.warning(rel_data)
        self.assertEqual(
            rel_data["receivers"],
            f'[{{"protocol": {{"name": "otlp_http", "type": "http"}}, "url": "http://{socket.getfqdn()}:4318"}}]',
        )

    @property
    def _container(self):
        return self.harness.model.unit.get_container(CONTAINER_NAME)

    @property
    def _plan(self):
        return self.harness.get_container_pebble_plan(CONTAINER_NAME)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 53s</sub>

### ✅ `bash`

**Check scenario API**

$ python3 -c "import scenario; print(scenario.__version__); import inspect; print(dir(scenario))" 2>/dev/null && python3 -c "from scenario.state import _BoundNotice; print('_BoundNotice exists')" 2>/dev/null || echo "_BoundNotice not found"

```
_BoundNotice not found
<exited with exit code 0>
```


---

<sub>⏱️ 1m 59s</sub>

### ✅ `bash`

**Check Notice API in new scenario**

$ python3 -c "import scenario; print([x for x in dir(scenario) if 'notice' in x.lower() or 'Notice' in x])"

```
['Notice']
<exited with exit code 0>
```


---

<sub>⏱️ 1m 59s</sub>

### ✅ `bash`

**Check ops.testing Notice API**

$ python3 -c "import ops.testing; print([x for x in dir(ops.testing) if 'notice' in x.lower() or 'Notice' in x])"

```
['Notice']
<exited with exit code 0>
```


---

<sub>⏱️ 2m 6s</sub>

### ✅ `bash`

**Check Notice API details**

$ python3 -c "import scenario; help(scenario.Notice)" 2>/dev/null | head -40

<details>
<summary>40 lines</summary>

```
Help on class Notice in module scenario.state:

class Notice(builtins.object)
 |  Notice(key: 'str', *, id: 'str' = <factory>, user_id: 'int | None' = None, type: 'pebble.NoticeType | str' = <NoticeType.CUSTOM: 'custom'>, first_occurred: 'datetime.datetime' = <factory>, last_occurred: 'datetime.datetime' = <factory>, last_repeated: 'datetime.datetime' = <factory>, occurrences: 'int' = 1, last_data: 'Mapping[str, str]' = <factory>, repeat_after: 'datetime.timedelta | None' = None, expire_after: 'datetime.timedelta | None' = None) -> None
 |
 |  A Pebble notice.
 |
 |  Methods defined here:
 |
 |  __delattr__(self, name)
 |      Implement delattr(self, name).
 |
 |  __eq__(self, other)
 |      Return self==value.
 |
 |  __hash__(self)
 |      Return hash(self).
 |
 |  __init__(self, key: 'str', *, id: 'str' = <factory>, user_id: 'int | None' = None, type: 'pebble.NoticeType | str' = <NoticeType.CUSTOM: 'custom'>, first_occurred: 'datetime.datetime' = <factory>, last_occurred: 'datetime.datetime' = <factory>, last_repeated: 'datetime.datetime' = <factory>, occurrences: 'int' = 1, last_data: 'Mapping[str, str]' = <factory>, repeat_after: 'datetime.timedelta | None' = None, expire_after: 'datetime.timedelta | None' = None) -> None
 |      Initialize self.  See help(type(self)) for accurate signature.
 |
 |  __post_init__(self)
 |
 |  __repr__(self)
 |      Return repr(self).
 |
 |  __setattr__(self, name, value)
 |      Implement setattr(self, name, value).
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |
 |  __dict__
 |      dictionary for instance variables
 |
 |  __weakref__
 |      list of weak references to the object
 |
 |  ----------------------------------------------------------------------
 |  Data and other attributes defined here:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 6s</sub>

### ✅ `bash`

**Explore Notice-Container API**

$ python3 -c "from scenario import Container, Notice; c = Container('tempo', can_connect=True, notices=[Notice('custom', 'foo')]); print(c); events = [e for e in dir(c) if 'notice' in str(e).lower()]; print(events)"

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
TypeError: Notice.__init__() takes 2 positional arguments but 3 were given
<exited with exit code 1>
```


---

<sub>⏱️ 2m 17s</sub>

### ✅ `bash`

**Explore container notice events API**

$ python3 -c "
from scenario import Container, Notice
# Find how to get notice event from container
notice = Notice('foo.bar/key')
container = Container('tempo', can_connect=True, notices=[notice])
print(dir(container))
" 2>&1 | head -20

```
['__annotations__', '__class__', '__dataclass_fields__', '__dataclass_params__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__match_args__', '__module__', '__ne__', '__new__', '__post_init__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_base_plan', '_render_checks', '_render_log_targets', '_render_services', 'can_connect', 'check_infos', 'execs', 'get_check_info', 'get_filesystem', 'layers', 'mounts', 'name', 'notices', 'plan', 'service_statuses', 'services']
<exited with exit code 0>
```


---

<sub>⏱️ 2m 17s</sub>

### ✅ `bash`

**Look for notice event attributes**

$ python3 -c "
from scenario import Container, Notice
notice = Notice('foo.bar/key')
container = Container('tempo', can_connect=True, notices=[notice])
# Check for notice-related event access
for attr in dir(container):
    if 'notice' in attr.lower() or 'event' in attr.lower():
        print(attr)
"

```
notices
<exited with exit code 0>
```


---

<sub>⏱️ 2m 17s</sub>

### ℹ️ Notification

Background agent "Exploring charm structure" (explore) completed

<details>
<summary>Detail</summary>

Explore the charm codebase at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4. I need to understand:
1. The main charm class and what it does (src/ directory)
2. All ops library usage patterns (event handlers, StatusBase subclasses, testing patterns, etc.)
3. What version of ops is currently being used
4. Any use of ops.testing or scenario testing
5. Any use of tracing/ops-tracing
6. The test files structure
7. Any deprecation warnings or patterns that might be affected by ops upgrades

Please read all files in src/, tests/, and lib/ directories and give me a comprehensive overview.

</details>

---

<sub>⏱️ 2m 22s</sub>

### ✅ `read_agent`

**Explore agent (Exploring charm structure)**

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "explore-charm"
}
```

</details>

<details>
<summary>362 lines</summary>

````
Agent completed. agent_id: explore-charm, agent_type: explore, status: completed, description: Exploring charm structure, elapsed: 122s, total_turns: 0, duration: 114s

Perfect! Now I have comprehensive information. Let me create a detailed summary:

## Comprehensive Charm Codebase Analysis: tempo-k8s-operator

### 1. **Main Charm Class and Purpose**

**File:** `/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/src/charm.py`

The `TempoCharm` class (inherits from `CharmBase`) is a Kubernetes operator for **Tempo**, a lightweight object storage-based tracing backend by Grafana. It provides:

- **Distributed tracing backend** with support for multiple receiver protocols (OTLP, Jaeger, Zipkin, OpenCensus)
- **Scalable monolithic deployment** with optional S3 storage for distribution
- **TLS support** via certificate handling
- **Ingress integration** with Traefik
- **Metrics collection** (Prometheus integration)
- **Log forwarding** (Loki integration)
- **Grafana dashboards** and data source provisioning
- **Charm-level tracing** via OpenTelemetry

**Key Components:**
- `Tempo` class (in `src/tempo.py`): Manages workload configuration, pebble layer planning, TLS, S3 storage, receiver configuration
- Multiple relation providers/requirers for integrations (S3, Traefik, Grafana, Prometheus, Loki, TLS certificates, tracing)

---

### 2. **Ops Library Usage Patterns**

#### **A. Event Handlers**
The charm uses `framework.observe()` extensively with various event types:

```python
# Core lifecycle events
self.framework.observe(self.on.leader_elected, self._on_leader_elected)
self.framework.observe(self.on.leader_settings_changed, self._on_leader_settings_changed)
self.framework.observe(self.on.config_changed, self._on_config_changed)
self.framework.observe(self.on.update_status, self._on_update_status)

# Workload events
self.framework.observe(self.on.tempo_pebble_ready, self._on_tempo_pebble_ready)
self.framework.observe(self.on.tempo_pebble_custom_notice, self._on_tempo_pebble_custom_notice)

# Relation events
self.framework.observe(self.on["ingress"].relation_created, self._on_ingress_relation_created)
self.framework.observe(self.on["ingress"].relation_joined, self._on_ingress_relation_joined)
self.framework.observe(self.s3_requirer.on.credentials_changed, self._on_s3_credentials_changed)
self.framework.observe(self.tracing.on.request, self._on_tracing_request)
self.framework.observe(self.tracing.on.broken, self._on_tracing_broken)

# Status collection (new pattern)
self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)

# Action events
self.framework.observe(self.on.list_receivers_action, self._on_list_receivers_action)

# Custom library events
self.framework.observe(self.cert_handler.on.cert_changed, self._on_cert_handler_changed)
```

**Event Types Used:**
- `PebbleNoticeEvent` (custom Pebble events)
- `WorkloadEvent` (pebble-ready)
- `RelationEvent` (relation-created, relation-joined)
- `CollectStatusEvent` (new status collection event)
- `ActionEvent` (action invocation)
- `LeaderElectedEvent`, `LeaderSettingsChangedEvent`
- Custom events from libraries (e.g., `RequestEvent` from tracing library)

---

#### **B. StatusBase Subclasses**
Located in: `/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/src/charm.py` (lines 508-520)

The charm uses the new **`CollectStatusEvent` pattern** (ops 2.1+):

```python
def _on_collect_unit_status(self, e: CollectStatusEvent):
    """Collect and aggregate unit status."""
    if not self.is_consistent():
        e.add_status(BlockedStatus("Unit *disabled*. Cannot scale Tempo without adding an s3 integration."))
    if not self.tempo.container.can_connect():
        e.add_status(WaitingStatus("Tempo container not ready"))
    if not self.tempo.is_ready():
        e.add_status(WaitingStatus("Tempo API not ready just yet..."))
    e.add_status(ActiveStatus())
```

**Status Classes Used:**
- `ActiveStatus()` - Running normally
- `BlockedStatus(msg)` - Scaled deployment without S3 integration
- `WaitingStatus(msg)` - Container or API not ready
- `MaintenanceStatus(msg)` - During reconfiguration

Traditional status setting is also used:
```python
self.unit.status = MaintenanceStatus("reconfiguring Tempo...")
self.unit.status = ActiveStatus()
```

---

#### **C. Container/Pebble Interaction**
The charm manages the Tempo workload container:

```python
container = self.unit.get_container("tempo")
container.can_connect()  # Check connectivity
container.push(path, content, make_dirs=True)  # Push config files
container.pull(path)  # Fetch files
container.get_service(name)  # Check service status
container.start/stop/restart(service_name)  # Control services
container.exec(cmd)  # Execute commands
```

---

#### **D. Model and Relations**
Relations are retrieved and manipulated:

```python
self.model.relations["tracing"]  # Get all relations by name
self.model.get_relation("tempo-peers")  # Get specific relation
relation.data[unit]  # Access relation databag
relation.units  # Get related units
self.unit.is_leader()  # Leadership check
self.model.get_binding("tempo-peers")  # Get network binding
```

---

#### **E. Framework and Object Storage**
Uses `framework.observe()` for event handling, with decorators in libraries:

```python
from ops.framework import EventSource, Object, ObjectEvents, StoredState

class CustomEvents(ObjectEvents):
    cert_changed = EventSource(CertChanged)
```

---

### 3. **Ops Library Version**

**File:** `/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/requirements.txt`

```
ops
```

**Version Status:** **Pinned but unspecified** - The requirements.txt lists just `ops` with no version constraint, meaning it uses whatever version is latest during installation.

This is potentially problematic for reproducible builds. Modern practice would be to pin to a specific version like `ops>=2.1.0,<3.0.0`.

---

### 4. **Ops.testing Usage**

**File:** `/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/unit/test_charm.py`

```python
from ops.testing import Harness

class TestTempoCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(TempoCharm)
        self.harness.set_model_name("testmodel")
        self.addCleanup(self.harness.cleanup)
        self.harness.set_leader(True)
        self.harness.begin_with_initial_hooks()
```

**Usage Patterns:**
- `Harness` for unit testing with mocked framework
- `set_leader()`, `set_model_name()`, `begin_with_initial_hooks()`
- `container_pebble_ready()`, `add_relation()`, `update_relation_data()`
- `get_container_pebble_plan()`, `get_relation_data()`

This is the **traditional ops.testing approach** for charm unit testing.

---

### 5. **Scenario Testing Usage**

**Files:** 
- `/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/`
- Multiple test files: `test_charm.py`, `test_charm_tracing.py`, `test_tls.py`, `test_ingressed_tracing.py`, etc.

The charm has **extensive scenario testing** (modern testing approach):

```python
from scenario import Context, State, Container, Relation
from scenario.sequences import check_builtin_sequences

@pytest.fixture(scope="function")
def context(tempo_charm):
    return Context(charm_type=tempo_charm)

def test_tempo_restart_on_ingress_v2_changed(context, tmp_path):
    container = Container(
        "tempo",
        can_connect=True,
        layers={"tempo": pebble.Layer(...)},
        service_status={"tempo": pebble.ServiceStatus.ACTIVE},
    )
    state = State(leader=True, containers=[container], relations=[ingress])
    context.run(ingress.changed_event, state)
    new_config = get_tempo_config(container, context)
    assert new_config == expected_config
```

**Scenario Features Used:**
- `State` for test state definition
- `Container` with pebble layers, service status
- `Relation` for relation state
- `Context` for running events
- `check_builtin_sequences()` for sequence validation
- Custom notices/pebble events

The scenario tests include:
- `test_charm.py` - Core charm behavior
- `test_charm_tracing.py` - Tracing instrumentation
- `test_tls.py` - TLS configuration
- `test_charm_scaling.py` - Peer relation scaling
- `test_tracing_provider.py` - Tracing relation provider
- `test_ingressed_tracing.py` - Traefik ingress integration

---

### 6. **Tracing/Ops-Tracing Usage**

**Files:**
- `/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/lib/charms/tempo_k8s/v1/charm_tracing.py`
- `/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/lib/charms/tempo_k8s/v1/tracing.py`
- `/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/lib/charms/tempo_k8s/v2/tracing.py`

The charm uses **built-in charm tracing** via OpenTelemetry:

```python
# In src/charm.py
@trace_charm(
    tracing_endpoint="tempo_otlp_http_endpoint",
    server_cert="server_cert",
    extra_types=(Tempo, TracingEndpointProvider),
)
class TempoCharm(CharmBase):
    ...

# Methods providing tracing endpoints
def server_cert(self):
    """For charm tracing."""
    self._update_server_cert()
    return self.tempo.server_cert_path

def tempo_otlp_http_endpoint(self) -> Optional[str]:
    """Endpoint at which the charm tracing information will be forwarded."""
    if self.tempo.is_ready():
        return f"{self._internal_url}:{self.tempo.receiver_ports['otlp_http']}"
    return None
```

**Dependencies:**
```
opentelemetry-exporter-otlp-proto-http==1.21.0
```

The charm provides a **tracing endpoint provider** for other charms to send traces to Tempo:

```python
from charms.tempo_k8s.v2.tracing import (
    ReceiverProtocol,
    RequestEvent,
    TracingEndpointProvider,
)

self.tracing = TracingEndpointProvider(self, external_url=self._external_url)
```

**Tracing Relations:**
- Library versions: v1 (legacy) and v2 (current)
- Event types: `RequestEvent`, `BrokenEvent`
- Methods: `publish_receivers()`, `requested_protocols()`

---

### 7. **Test Files Structure**

```
tests/
├── unit/
│   ├── test_charm.py          # Unit tests with Harness
│   └── test_tempo.py          # Tempo workload tests
├── scenario/
│   ├── conftest.py            # Pytest fixtures
│   ├── helpers.py             # Test helpers
│   ├── test_charm.py          # Core charm scenarios
│   ├── test_charm_tracing.py  # Tracing instrumentation tests
│   ├── test_tls.py            # TLS configuration tests
│   ├── test_charm_scaling.py  # Peer relation scaling tests
│   ├── test_tracing_provider.py
│   ├── test_tracing_requirer.py
│   ├── test_tracing_legacy.py
│   ├── test_ingressed_tracing.py
│   └── test_a_charm_tracer_multi_import_warning.py
├── interface/
│   ├── conftest.py
│   └── test_tracing.py        # Tracing interface tests
└── integration/
    ├── test_integration.py
    ├── test_scaling_monolithic.py
    ├── test_tls.py
    ├── test_ingressed_tls.py
    ├── tester/                 # Test charm
    └── tester-grpc/            # GRPC test charm
```

**Test Statistics:**
- Unit tests: 2 files
- Scenario tests: 8+ files
- Integration tests: Multiple test files
- Total test Python files: 13+ in main testing directories

---

### 8. **Deprecation Warnings and Ops Upgrade Concerns**

#### **A. Potential Issues for Ops Upgrades**

1. **E402 Linting Suppression** (pyproject.toml, line 68):
   ```python
   "lib/charms/tempo_k8s/v1/charm_tracing.py" = ["E402"]
   ```
   This indicates code that does some import-time side effects that violate PEP 8. Comment notes: *"Remove charm_tracing.py E402 when _remove_stale_otel_sdk_packages() is removed from the library"* - This is a **deprecated cleanup function** that should be addressed.

2. **Deprecated JuJuTopology Library** (lib/charms/observability_libs/v0/juju_topology.py):
   ```python
   DEPRECATED: This class is deprecated. Use `pip install cosl` and ...
   ```
   The codebase has deprecated observability libs that should be updated.

3. **PebbleNoticeEvent Usage** (new in ops 2.1):
   ```python
   from ops.charm import PebbleNoticeEvent
   ```
   This requires ops >= 2.1. The charm uses custom Pebble notices which are relatively new.

4. **CollectStatusEvent Usage** (new in ops 2.1+):
   ```python
   from ops.charm import CollectStatusEvent
   e.add_status(BlockedStatus(...))
   ```
   The new deferred status collection pattern requires ops >= 2.1.

5. **Mixed Status Patterns**:
   - Uses both old `self.unit.status = ...` AND new `e.add_status(...)`
   - Should migrate fully to `CollectStatusEvent` pattern for ops 2.1+

6. **RelationRole Usage** (in lib/charms/parca/v0/parca_scrape.py):
   ```python
   if expected_relation_role == ops.RelationRole.provides:
   ```
   This is still valid but the enum should be checked for any deprecations in newer ops versions.

7. **Container.exists() with Pebble paths**:
   ```python
   container.exists(tls_path)  # May have issues with symlinks in newer versions
   ```

8. **APIError vs RuntimeError Exception Handling**:
   ```python
   try:
       self.tempo.container.stop("tempo-ready")
   except (APIError, RuntimeError):  # ops.testing raises RuntimeError
       pass
   ```
   Comment notes testing library differences - may need adjustment in ops upgrades.

#### **B. Positive Patterns (Compatible)**

1. ✅ Uses `CharmBase` correctly
2. ✅ Uses `framework.observe()` with proper event handlers
3. ✅ Uses standard status classes from `ops.model`
4. ✅ Relation databag access is standard
5. ✅ Pebble layer definition is correct
6. ✅ Model binding usage is appropriate
7. ✅ Container interaction patterns are standard

---

### 9. **Library Dependencies Structure**

The charm has **15 library files** across multiple charm libraries:

```
lib/charms/
├── observability_libs/v0/
│   ├── juju_topology.py           (DEPRECATED - use cosl)
│   └── kubernetes_service_patch.py
├── observability_libs/v1/
│   └── cert_handler.py            (Certificate handling)
├── tempo_k8s/v1/
│   ├── charm_tracing.py           (OpenTelemetry tracing)
│   └── tracing.py                 (Legacy v1 interface)
├── tempo_k8s/v2/
│   └── tracing.py                 (Current tracing interface)
├── tls_certificates_interface/v3/
│   └── tls_certificates.py        (TLS cert requests)
├── traefik_k8s/v2/
│   └── ingress.py
├── traefik_route_k8s/v0/
│   └── traefik_route.py           (Ingress routing)
├── data_platform_libs/v0/
│   └── s3.py                      (S3 storage)
├── loki_k8s/v0/
│   └── loki_push_api.py           (Log forwarding)
├── grafana_k8s/v0/
│   ├── grafana_dashboard.py
│   └── grafana_source.py
├── prometheus_k8s/v0/
│   └── prometheus_scrape.py       (Metrics collection)
└── parca/v0/
    └── parca_scrape.py
```

**Key observations:**
- Uses multiple versions of same libraries (v1 and v2 of tracing)
- EventBase and EventSource patterns used throughout libraries
- Custom event definitions in cert_handler, parca_scrape, etc.

---

### 10. **Summary of Key Findings**

| Aspect | Status | Notes |
|--------|--------|-------|
| **Ops Version** | Unspecified | Should pin to >= 2.1.0 |
| **Main Testing** | Harness + Scenario | Good coverage with both approaches |
| **Status Pattern** | Mixed (old+new) | Uses both `self.unit.status` and `CollectStatusEvent` |
| **Event Handling** | Comprehensive | 20+ event handlers, proper framework.observe() usage |
| **Container/Pebble** | Modern | Uses pebble layers, notices, services correctly |
| **Tracing** | Enabled | OpenTelemetry integration, trace_charm decorator |
| **Relations** | Multiple | S3, TLS certs, Traefik, Grafana, Prometheus, Loki, Tracing |
| **Deprecations** | Few | E402 suppression, deprecated JujuTopology reference |
| **Ops Compatibility** | ≥2.1 | Requires ops >= 2.1 for CollectStatusEvent, PebbleNoticeEvent |

---

### **Recommendations for Ops Upgrade**

1. **Pin ops version** in requirements.txt (e.g., `ops>=2.1.0,<3.0.0`)
2. **Remove E402 suppression** by addressing `_remove_stale_otel_sdk_packages()` in charm_tracing.py
3. **Migrate to cosl** instead of deprecated juju_topology library
4. **Unify status patterns** - use CollectStatusEvent exclusively or old pattern, not both
5. **Test with scenario testing** extensively to catch breaking changes
6. **Review exception handling** in pebble operations for ops 3.0+ changes
7. **Check RelationRole** enum usage for any deprecation warnings in target ops version
````

</details>


---

<sub>⏱️ 2m 23s</sub>

### ✅ `bash`

**Try to get notice event from Notice object**

$ python3 -c "
from scenario import Container, Notice
notice = Notice('foo.bar/key')
container = Container('tempo', can_connect=True, notices=[notice])
# Try the notice event
try:
    ev = notice.event
    print('notice.event:', ev)
except AttributeError as e:
    print('no notice.event:', e)
" 2>&1

```
no notice.event: 'Notice' object has no attribute 'event'
<exited with exit code 0>
```


---

<sub>⏱️ 2m 32s</sub>

### ✅ `bash`

**Check Context.run signature**

$ python3 -c "
from scenario import Container, Notice
# Let's look at how to run notice events  
import inspect
# Look at what context.run accepts
from scenario import Context
sig = inspect.signature(Context.run)
print('Context.run signature:', sig)
"

```
Context.run signature: (self, event: '_Event', state: 'State') -> 'State'
<exited with exit code 0>
```


---

<sub>⏱️ 2m 33s</sub>

### ✅ `bash`

**Check ops.testing Context methods**

$ python3 -c "
import scenario
# look for how to trigger notice events
import inspect
src = inspect.getsource(scenario.state.Container)
" 2>&1 | head -5
python3 -c "
from scenario import Container, Notice
c = Container('tempo', can_connect=True, notices=[Notice('foo.bar/key')])
# check if there's a way to get the notice event
import ops.testing
ctx_help = [x for x in dir(ops.testing.Context) if not x.startswith('__')]
print('Context methods:', ctx_help)
"

```
Context methods: ['_get_container_root', '_get_storage_root', '_record_status', '_run', '_set_output_state', 'charm_spec', 'run', 'run_action']
<exited with exit code 0>
```


---

<sub>⏱️ 2m 42s</sub>

### ✅ `bash`

**Check scenario event types**

$ python3 -c "
import scenario
# Let's look at Event classes
events = [x for x in dir(scenario) if 'Event' in x or 'event' in x.lower()]
print('Events:', events)
# Look for pebble_notice
pebble = [x for x in dir(scenario) if 'pebble' in x.lower() or 'Pebble' in x]
print('Pebble:', pebble)
"

```
Events: ['CharmEvents', 'DeferredEvent']
Pebble: []
<exited with exit code 0>
```


---

<sub>⏱️ 2m 42s</sub>

### ✅ `bash`

**Check notice event access**

$ python3 -c "
from scenario import Container, Notice
# Try the new way to access container pebble notice event
n = Notice('foo.bar/key')
c = Container('tempo', can_connect=True, notices=[n])
# check what attributes exist
print('Notice attrs:', [x for x in dir(n) if not x.startswith('_')])
# Try accessing event through container
notice_event = c.pebble_custom_notice_event
print('notice event:', notice_event)
" 2>&1

```
Notice attrs: ['expire_after', 'first_occurred', 'id', 'key', 'last_data', 'last_occurred', 'last_repeated', 'occurrences', 'repeat_after', 'type', 'user_id']
Traceback (most recent call last):
  File "<string>", line 9, in <module>
AttributeError: 'Container' object has no attribute 'pebble_custom_notice_event'
<exited with exit code 1>
```


---

<sub>⏱️ 2m 50s</sub>

### ✅ `bash`

**Look at Event class in ops.testing**

$ python3 -c "
# Look at the ops.testing module to understand notice events
import ops.testing as t
# Look at the _Event type
import inspect
src = inspect.getsource(t)
" 2>&1 | head -5
# Let's look at how events work in ops.testing
python3 -c "
import ops.testing
# Check _Event
from ops.testing._ops_testing import _Event
print(dir(_Event))
" 2>&1 | head -10

```
Traceback (most recent call last):
  File "<string>", line 4, in <module>
ModuleNotFoundError: No module named 'ops.testing._ops_testing'; 'ops.testing' is not a package
<exited with exit code 0>
```


---

<sub>⏱️ 2m 49s</sub>

### ❌ `bash`

**Find scenario source files**

$ find /home/ubuntu/.local/lib -name "*.py" -path "*scenario*" | grep -v __pycache__ | head -20

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 2m 55s</sub>

### ❌ `bash`

**Find scenario source files**

$ find /usr -name "*.py" -path "*scenario*" 2>/dev/null | grep -v __pycache__ | head -20 && find / -maxdepth 8 -name "state.py" -path "*scenario*" 2>/dev/null | head -5

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 3m 1s</sub>

### ✅ `bash`

**Find scenario package location**

$ python3 -c "import scenario; import os; print(os.path.dirname(scenario.__file__))"

```
/home/ubuntu/.local/lib/python3.12/site-packages/scenario
<exited with exit code 0>
```


---

<sub>⏱️ 3m 12s</sub>

### ❌ `bash`

**Search Notice API in scenario state.py**

$ ls /home/ubuntu/.local/lib/python3.12/site-packages/scenario/ && grep -n "pebble_custom_notice\|_BoundNotice\|Notice" /home/ubuntu/.local/lib/python3.12/site-packages/scenario/state.py | head -40

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 3m 17s</sub>

### ✅ `bash`

**Search Notice-related code in scenario.state**

$ python3 << 'EOF'
import scenario
import inspect

# Find notice-related methods
src = inspect.getsource(scenario.state)
# Search for BoundNotice patterns
lines = src.split('\n')
for i, line in enumerate(lines):
    if 'notice' in line.lower() or 'BoundNotice' in line:
        print(f"{i}: {line}")
EOF

<details>
<summary>42 lines</summary>

```
106: _PEBBLE_CUSTOM_NOTICE_EVENT_SUFFIX = '_pebble_custom_notice'
842: _next_notice_id_counter = 1
845: def _next_notice_id(*, update: bool = True):
846:     """Get the ID the next Pebble notice to be created will get.
851:     global _next_notice_id_counter
852:     cur = _next_notice_id_counter
854:         _next_notice_id_counter += 1
859: class Notice:
860:     """A Pebble notice."""
863:     """The notice key, a string that differentiates notices of this type.
866:     ``canonical.com/postgresql/backup`` or ``example.com/mycharm/notice``.
871:     id: str = dataclasses.field(default_factory=_next_notice_id)
872:     """Unique ID for this notice."""
875:     """UID of the user who may view this notice (None means notice is public)."""
877:     type: pebble.NoticeType | str = pebble.NoticeType.CUSTOM
878:     """Type of the notice."""
881:     """The first time one of these notices (type and key combination) occurs."""
884:     """The last time one of these notices occurred."""
887:     """The time this notice was last repeated.
889:     See Pebble's `Notices documentation <https://documentation.ubuntu.com/pebble/reference/notices/>`_
894:     """The number of times one of these notices has occurred."""
897:     """Additional data captured from the last occurrence of one of these notices."""
903:     """How long since one of these last occurred until Pebble will drop the notice."""
908:     def _to_ops(self) -> pebble.Notice:
909:         return pebble.Notice(
1092:     notices: Sequence[Notice] = dataclasses.field(default_factory=list)
1093:     """Any Pebble notices that already exist in the container."""
1551:     constraint is unnecessarily strict since a charm will only notice that a
2181:         if s.endswith(_PEBBLE_CUSTOM_NOTICE_EVENT_SUFFIX):
2182:             return _PEBBLE_CUSTOM_NOTICE_EVENT_SUFFIX, _EventType.WORKLOAD
2223:     notice: Notice | None = None
2224:     """If this is a Pebble notice event, the notice it refers to."""
2334:         The framework simulates the ops notice queue. The queue is responsible
2336:         can verify that if the charm triggers with this and that notice in its
2385:             if self.notice:
2386:                 if hasattr(self.notice.type, 'value'):
2387:                     notice_type = cast('pebble.NoticeType', self.notice.type).value
2389:                     notice_type = str(self.notice.type)
2392:                         'notice_id': self.notice.id,
2393:                         'notice_key': self.notice.key,
2394:                         'notice_type': notice_type,
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 26s</sub>

### ✅ `bash`

**Find _Event class definition**

$ python3 << 'EOF'
import scenario
import inspect

# Look at _Event class and how to create notice events
src = inspect.getsource(scenario.state)
lines = src.split('\n')

# Find _Event class
in_event_class = False
for i, line in enumerate(lines):
    if 'class _Event' in line or in_event_class:
        in_event_class = True
        print(f"{i}: {line}")
        if in_event_class and i > 2200 and line.strip() == '':
            # Stop after some context
            break
    if i > 2450:
        break
EOF

<details>
<summary>80 lines</summary>

```
2125: class _EventType(str, Enum):
2126:     FRAMEWORK = 'framework'
2127:     BUILTIN = 'builtin'
2128:     RELATION = 'relation'
2129:     ACTION = 'action'
2130:     SECRET = 'secret'  # noqa: S105  # This is not an actual secret.
2131:     STORAGE = 'storage'
2132:     WORKLOAD = 'workload'
2133:     CUSTOM = 'custom'
2134: 
2135: 
2136: class _EventPath(str):
2137:     if TYPE_CHECKING:  # pragma: no cover
2138:         name: str
2139:         owner_path: list[str]
2140:         suffix: str
2141:         prefix: str
2142:         is_custom: bool
2143:         type: _EventType
2144: 
2145:     def __new__(cls, string: str):
2146:         string = _normalise_name(string)
2147:         instance = super().__new__(cls, string)
2148: 
2149:         instance.name = name = string.split('.')[-1]
2150:         instance.owner_path = string.split('.')[:-1] or ['on']
2151: 
2152:         instance.suffix, instance.type = _EventPath._get_suffix_and_type(name)
2153:         instance.prefix = string.removesuffix(instance.suffix)
2154:         instance._is_custom = instance.suffix == ''
2155: 
2156:         return instance
2157: 
2158:     @staticmethod
2159:     def _get_suffix_and_type(s: str) -> tuple[str, _EventType]:
2160:         for suffix in _RELATION_EVENTS_SUFFIX:
2161:             if s.endswith(suffix):
2162:                 return suffix, _EventType.RELATION
2163: 
2164:         if s.endswith(_ACTION_EVENT_SUFFIX):
2165:             return _ACTION_EVENT_SUFFIX, _EventType.ACTION
2166: 
2167:         if s in _SECRET_EVENTS:
2168:             return s, _EventType.SECRET
2169: 
2170:         if s in _FRAMEWORK_EVENTS:
2171:             return s, _EventType.FRAMEWORK
2172: 
2173:         # Whether the event name indicates that this is a storage event.
2174:         for suffix in _STORAGE_EVENTS_SUFFIX:
2175:             if s.endswith(suffix):
2176:                 return suffix, _EventType.STORAGE
2177: 
2178:         # Whether the event name indicates that this is a workload event.
2179:         if s.endswith(_PEBBLE_READY_EVENT_SUFFIX):
2180:             return _PEBBLE_READY_EVENT_SUFFIX, _EventType.WORKLOAD
2181:         if s.endswith(_PEBBLE_CUSTOM_NOTICE_EVENT_SUFFIX):
2182:             return _PEBBLE_CUSTOM_NOTICE_EVENT_SUFFIX, _EventType.WORKLOAD
2183:         if s.endswith(_PEBBLE_CHECK_FAILED_EVENT_SUFFIX):
2184:             return _PEBBLE_CHECK_FAILED_EVENT_SUFFIX, _EventType.WORKLOAD
2185:         if s.endswith(_PEBBLE_CHECK_RECOVERED_EVENT_SUFFIX):
2186:             return _PEBBLE_CHECK_RECOVERED_EVENT_SUFFIX, _EventType.WORKLOAD
2187: 
2188:         if s in _BUILTIN_EVENTS:
2189:             return '', _EventType.BUILTIN
2190: 
2191:         return '', _EventType.CUSTOM
2192: 
2193: 
2194: @dataclasses.dataclass(frozen=True)
2195: class _Event:  # type: ignore
2196:     """A Juju, ops, or custom event that can be run against a charm."""
2197: 
2198:     path: str
2199:     """The name of the event.
2200: 
2201:     For example: ``start``, ``config_changed``, ``my_relation_joined``, or
2202:     ``custom.MyConsumer.lib_changed``.
2203:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 32s</sub>

### ✅ `bash`

**Look at _Event definition more fully**

$ python3 << 'EOF'
import scenario
import inspect
src = inspect.getsource(scenario.state)
lines = src.split('\n')
# Show lines 2195-2350
for i, line in enumerate(lines[2195:2410], start=2195):
    print(f"{i}: {line}")
EOF

<details>
<summary>216 lines</summary>

```
2195: class _Event:  # type: ignore
2196:     """A Juju, ops, or custom event that can be run against a charm."""
2197: 
2198:     path: str
2199:     """The name of the event.
2200: 
2201:     For example: ``start``, ``config_changed``, ``my_relation_joined``, or
2202:     ``custom.MyConsumer.lib_changed``.
2203: 
2204:     This is converted to an _EventPath object on instantiation.
2205:     """
2206: 
2207:     storage: Storage | None = None
2208:     """If this is a storage event, the storage it refers to."""
2209:     relation: RelationBase | None = None
2210:     """If this is a relation event, the relation it refers to."""
2211:     relation_remote_unit_id: int | None = None
2212:     relation_departed_unit_id: int | None = None
2213: 
2214:     secret: Secret | None = None
2215:     """If this is a secret event, the secret it refers to."""
2216: 
2217:     # if this is a secret-removed or secret-expired event, the secret revision it refers to
2218:     secret_revision: int | None = None
2219: 
2220:     container: Container | None = None
2221:     """If this is a workload (container) event, the container it refers to."""
2222: 
2223:     notice: Notice | None = None
2224:     """If this is a Pebble notice event, the notice it refers to."""
2225: 
2226:     check_info: CheckInfo | None = None
2227:     """If this is a Pebble check event, the check info it provides."""
2228: 
2229:     action: _Action | None = None
2230:     """If this is an action event, the :class:`Action` it refers to."""
2231: 
2232:     custom_event: ops.BoundEvent | None = None
2233:     """If this is a custom event, the bound event it refers to.
2234: 
2235:     The charm object *must* have an attribute that is an instance of the same
2236:     emitter type.
2237:     """
2238: 
2239:     custom_event_args: Iterable[Any] = dataclasses.field(default_factory=tuple)
2240:     """If this is a custom event, the arguments to pass to the event."""
2241: 
2242:     custom_event_kwargs: Mapping[str, Any] = dataclasses.field(default_factory=dict)
2243:     """If this is a custom event, the keyword arguments to pass to the event."""
2244: 
2245:     _owner_path: list[str] = dataclasses.field(default_factory=list)
2246: 
2247:     def __post_init__(self):
2248:         path = _EventPath(self.path)
2249:         # bypass frozen dataclass
2250:         object.__setattr__(self, 'path', path)
2251:         # This is the event name as Juju provides it, with dashes not underscores.
2252:         object.__setattr__(self, '_juju_name', f'{path.prefix}{path.suffix.replace("_", "-")}')
2253: 
2254:     @property
2255:     def _path(self) -> _EventPath:
2256:         # we converted it in __post_init__, but the type checker doesn't know about that
2257:         return cast('_EventPath', self.path)
2258: 
2259:     @property
2260:     def name(self) -> str:
2261:         """Full event name.
2262: 
2263:         Consists of a 'prefix' and a 'suffix'. The suffix denotes the type of the event, the
2264:         prefix the name of the entity the event is about.
2265: 
2266:         "foo-relation-changed":
2267:          - "foo"=prefix (name of a relation),
2268:          - "-relation-changed"=suffix (relation event)
2269:         """
2270:         return self._path.name
2271: 
2272:     @property
2273:     def owner_path(self) -> list[str]:
2274:         """Path to the ObjectEvents instance owning this event.
2275: 
2276:         If this event is defined on the toplevel charm class, it should be ['on'].
2277:         """
2278:         return self._path.owner_path
2279: 
2280:     @property
2281:     def _is_relation_event(self) -> bool:
2282:         """Whether the event name indicates that this is a relation event."""
2283:         return self._path.type is _EventType.RELATION
2284: 
2285:     @property
2286:     def _is_action_event(self) -> bool:
2287:         """Whether the event name indicates that this is a relation event."""
2288:         return self._path.type is _EventType.ACTION
2289: 
2290:     @property
2291:     def _is_secret_event(self) -> bool:
2292:         """Whether the event name indicates that this is a secret event."""
2293:         return self._path.type is _EventType.SECRET
2294: 
2295:     @property
2296:     def _is_storage_event(self) -> bool:
2297:         """Whether the event name indicates that this is a storage event."""
2298:         return self._path.type is _EventType.STORAGE
2299: 
2300:     @property
2301:     def _is_workload_event(self) -> bool:
2302:         """Whether the event name indicates that this is a workload event."""
2303:         return self._path.type is _EventType.WORKLOAD
2304: 
2305:     @property
2306:     def _is_custom_event(self) -> bool:
2307:         """Whether the event name indicates that this is a custom event."""
2308:         return self.custom_event is not None
2309: 
2310:     # this method is private because _CharmSpec is not quite user-facing; also,
2311:     # the user should know.
2312:     def _is_builtin_event(self, charm_spec: _CharmSpec[CharmType]) -> bool:
2313:         """Determine whether the event is a custom-defined one or a builtin one."""
2314:         event_name = self.name
2315: 
2316:         # simple case: this is an event type owned by our charm base.on
2317:         if hasattr(charm_spec.charm_type.on, event_name):
2318:             return hasattr(CharmEvents, event_name)
2319: 
2320:         # this could be an event defined on some other Object, e.g. a charm lib.
2321:         # We don't support (yet) directly emitting those, but they COULD have names that conflict
2322:         # with events owned by the base charm. E.g. if the charm has a `foo` relation, the charm
2323:         # will get a  charm.on.foo_relation_created. Your charm lib is free to define its own
2324:         # `foo_relation_created`  custom event, because its handle will be
2325:         # `charm.lib.on.foo_relation_created` and therefore be  unique and the Framework is happy.
2326:         # However, our Event data structure ATM has no knowledge of which Object/Handle it is
2327:         # owned by. So the only thing we can do right now is: check whether the event name,
2328:         # assuming it is owned by the charm, LOOKS LIKE that of a builtin event or not.
2329:         return self._path.type is not _EventType.CUSTOM
2330: 
2331:     def deferred(self, handler: Callable[..., Any], event_id: int = 1) -> DeferredEvent:
2332:         """Construct a deferred event from this event.
2333: 
2334:         The framework simulates the ops notice queue. The queue is responsible
2335:         for keeping track of the deferred event handlers. On the input side, you
2336:         can verify that if the charm triggers with this and that notice in its
2337:         queue (they would be there because they had been deferred in the
2338:         previous run), then the output state is valid. For example::
2339: 
2340:             class MyCharm(ops.CharmBase):
2341:                 def __init__(self, framework: ops.Framework):
2342:                     super().__init__(framework)
2343:                     framework.observe(self.on.update_status, self._on_update_status)
2344:                     framework.observe(self.on.start, self._on_start)
2345: 
2346:                 def _on_update_status(self, event: ops.UpdateStatusEvent):
2347:                     event.defer()
2348: 
2349:                 def _on_start(self, event: ops.StartEvent):
2350:                     event.defer()
2351: 
2352:             def test_start_on_deferred_update_status():
2353:                 ctx = Context(MyCharm)
2354:                 state_in = State(
2355:                     deferred=[
2356:                         ctx.on.update_status().deferred(handler=MyCharm._on_update_status)
2357:                     ]
2358:                 )
2359:                 state_out = ctx.run(ctx.on.start(), state_in)
2360:                 assert len(state_out.deferred) == 2
2361:                 assert state_out.deferred[1].name == 'start'
2362:         """
2363:         handler_repr = repr(handler)
2364:         handler_re = re.compile(r'<function (.*) at .*>')
2365:         match = handler_re.match(handler_repr)
2366:         if not match:
2367:             raise ValueError(
2368:                 f'cannot construct DeferredEvent from {handler}; please create one manually.',
2369:             )
2370:         owner_name, handler_name = match.groups()[0].split('.')[-2:]
2371:         handle_path = f'{owner_name}/on/{self.name}[{event_id}]'
2372: 
2373:         # Many events have no snapshot data: install, start, stop, remove, config-changed,
2374:         # upgrade-charm, pre-series-upgrade, post-series-upgrade, leader-elected,
2375:         # leader-settings-changed, collect-metrics
2376:         snapshot_data: dict[str, Any] = {}
2377: 
2378:         # fixme: at this stage we can't determine if the event is a builtin one or not; if it is
2379:         #  not, then the coming checks are meaningless: the custom event could be named like a
2380:         #  relation event but not *be* one.
2381:         if self._is_workload_event:
2382:             # Enforced by the consistency checker, but for type checkers:
2383:             assert self.container is not None
2384:             snapshot_data['container_name'] = self.container.name
2385:             if self.notice:
2386:                 if hasattr(self.notice.type, 'value'):
2387:                     notice_type = cast('pebble.NoticeType', self.notice.type).value
2388:                 else:
2389:                     notice_type = str(self.notice.type)
2390:                 snapshot_data.update(
2391:                     {
2392:                         'notice_id': self.notice.id,
2393:                         'notice_key': self.notice.key,
2394:                         'notice_type': notice_type,
2395:                     },
2396:                 )
2397:             elif self.check_info:
2398:                 snapshot_data['check_name'] = self.check_info.name
2399: 
2400:         elif self._is_relation_event:
2401:             # Enforced by the consistency checker, but for type checkers:
2402:             assert self.relation is not None
2403:             relation = self.relation
2404:             if isinstance(relation, PeerRelation):
2405:                 # FIXME: relation.unit for peers should point to <this unit>, but we
2406:                 #  don't have access to the local app name in this context.
2407:                 remote_app = 'local'
2408:             elif isinstance(relation, (Relation, SubordinateRelation)):
2409:                 remote_app = relation.remote_app_name
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 49s</sub>

### ✅ `bash`

**Check Context.on attribute**

$ python3 << 'EOF'
import scenario
import inspect

# Look at Context.on
src = inspect.getsource(scenario.context)
lines = src.split('\n')
# Find on-related stuff
for i, line in enumerate(lines):
    if 'class.*On' in line or 'def on' in line or '.on.' in line or 'CharmEvents' in line:
        print(f"{i}: {line}")
EOF

<details>
<summary>22 lines</summary>

```
69:         with ctx(ctx.on.start(), State()) as manager:
154: class CharmEvents:
160:         ctx.run(ctx.on.config_changed(), state)
162:     This behaves similarly to the :class:`ops.CharmEvents` class but is much
383:                     framework.observe(self.db.on.ready, self._on_db_ready)
387:             ctx.run(ctx.on.custom(
388:                 DatabaseRequirer.on.ready, 1, 2, foo='bar'
404:                 'example: ctx.run(ctx.on.relation_changed(relation), state)'
457:             state_out = ctx.run(ctx.on.update_status(), State())
469:             with ctx(ctx.on.start(), State()) as mgr:
504:         state_out = ctx.run(ctx.on.start(), State())
521:         state_out = ctx.run(ctx.on.start(), State())
545:         ctx.run(ctx.on.start(), State())
571:             deferred = ctx.on.update_status().deferred(MyCharm._on_foo)
572:             ctx.run(ctx.on.start(), State(deferred=[deferred]))
619:     on: CharmEvents
755:         self.on = CharmEvents()
798:             with ctx(ctx.on.start(), State()) as manager:
815:             f'call with `ctx.run`, like `ctx.run(ctx.on.action({action!r})` '
826:             specify the event; for example: ``ctx.on.start()``.
869:                 f'call with an event from `ctx.on`, like `ctx.on.{suggested}`',
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 49s</sub>

### ✅ `bash`

**Explore ctx.on attributes**

$ python3 -c "
from scenario import Context, State, Container, Notice
from ops import CharmBase

class MyCharm(CharmBase):
    META = {'name': 'test', 'containers': {'c': {}}}
    def __init__(self, fw):
        super().__init__(fw)

ctx = Context(MyCharm, meta=MyCharm.META)
print(dir(ctx.on))
"

```
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'action', 'collect_app_status', 'collect_unit_status', 'config_changed', 'custom', 'install', 'leader_elected', 'pebble_check_failed', 'pebble_check_recovered', 'pebble_custom_notice', 'pebble_ready', 'post_series_upgrade', 'pre_series_upgrade', 'relation_broken', 'relation_changed', 'relation_created', 'relation_departed', 'relation_joined', 'remove', 'secret_changed', 'secret_expired', 'secret_remove', 'secret_rotate', 'start', 'stop', 'storage_attached', 'storage_detaching', 'update_status', 'upgrade_charm']
<exited with exit code 0>
```


---

<sub>⏱️ 4m 0s</sub>

### ✅ `bash`

**Check pebble_custom_notice signature**

$ python3 -c "
from scenario import Context, State, Container, Notice
from ops import CharmBase

class MyCharm(CharmBase):
    META = {'name': 'test', 'containers': {'c': {}}}
    def __init__(self, fw):
        super().__init__(fw)

ctx = Context(MyCharm, meta=MyCharm.META)
# Check signature for pebble_custom_notice
import inspect
print(inspect.signature(ctx.on.pebble_custom_notice))
"

```
(container: 'Container', notice: 'Notice')
<exited with exit code 0>
```


---

<sub>⏱️ 4m 17s</sub>

### ✅ `bash`

**Test new scenario API**

$ python3 -c "
from scenario import Context, State, Container, Notice
from ops import CharmBase

class MyCharm(CharmBase):
    META = {'name': 'test', 'containers': {'c': {}}}
    def __init__(self, fw):
        super().__init__(fw)

ctx = Context(MyCharm, meta=MyCharm.META)
# Test pebble_custom_notice
c = Container('c', can_connect=True)
n = Notice('foo.bar/key')
event = ctx.on.pebble_custom_notice(container=c, notice=n)
print('Notice event created:', event)

# Check if output_state still exists
print('Context has output_state:', hasattr(ctx, 'output_state'))

# Check State.replace
s = State(leader=True)
print('State has replace:', hasattr(s, 'replace'))
" 2>&1

```
Notice event created: _Event(path='c_pebble_custom_notice', storage=None, relation=None, relation_remote_unit_id=None, relation_departed_unit_id=None, secret=None, secret_revision=None, container=Container(name='c', can_connect=True, _base_plan={}, layers={}, service_statuses={}, mounts={}, execs=frozenset(), notices=[], check_infos=frozenset()), notice=Notice(key='foo.bar/key', id='1', user_id=None, type=<NoticeType.CUSTOM: 'custom'>, first_occurred=datetime.datetime(2026, 4, 2, 23, 24, 12, 336940, tzinfo=datetime.timezone.utc), last_occurred=datetime.datetime(2026, 4, 2, 23, 24, 12, 336946, tzinfo=datetime.timezone.utc), last_repeated=datetime.datetime(2026, 4, 2, 23, 24, 12, 336946, tzinfo=datetime.timezone.utc), occurrences=1, last_data={}, repeat_after=None, expire_after=None), check_info=None, action=None, custom_event=None, custom_event_args=(), custom_event_kwargs={}, _owner_path=[])
Context has output_state: False
State has replace: False
<exited with exit code 0>
```


---

<sub>⏱️ 4m 17s</sub>

### ✅ `bash`

**Check if check_builtin_sequences still exists**

$ python3 -c "
from scenario.sequences import check_builtin_sequences
print('check_builtin_sequences available')
" 2>&1

```
Traceback (most recent call last):
  File "<string>", line 2, in <module>
ModuleNotFoundError: No module named 'scenario.sequences'
<exited with exit code 1>
```


---

<sub>⏱️ 4m 29s</sub>

### ✅ `bash`

**Check how to replace State**

$ python3 -c "
from scenario import State
s = State(leader=True)
# check how to 'replace' a state  
print([x for x in dir(s) if 'replace' in x.lower() or 'copy' in x.lower()])
# Check if it's a dataclass
import dataclasses
print('is dataclass:', dataclasses.is_dataclass(s))
import dataclasses as dc
s2 = dc.replace(s, leader=False)
print('dataclasses.replace works:', s2)
"

```
[]
is dataclass: True
dataclasses.replace works: State(config={}, relations=frozenset(), networks=frozenset(), containers=frozenset(), storages=frozenset(), opened_ports=frozenset(), leader=False, model=Model(name='B4ZFn5156O5YNw36GuiM', uuid='fd585cf3-2b42-4086-b8ff-828343ae9c47', type='kubernetes', cloud_spec=None), secrets=frozenset(), resources=frozenset(), planned_units=1, deferred=[], stored_states=frozenset(), app_status=UnknownStatus(), unit_status=UnknownStatus(), workload_version='')
<exited with exit code 0>
```


---

<sub>⏱️ 4m 28s</sub>

### ✅ `bash`

**Check new scenario module structure**

$ python3 << 'EOF'
# Check how scenario tests run now and what replaced check_builtin_sequences
import scenario
import inspect
# Look for sequences or similar
print(dir(scenario))
# Look for what's in the scenario module
src = inspect.getsource(scenario)
for line in src.split('\n')[:100]:
    print(line)
EOF

<details>
<summary>86 lines</summary>

```
['ActionFailed', 'ActiveStatus', 'Address', 'AnyJson', 'BindAddress', 'BlockedStatus', 'CharmEvents', 'CharmType', 'CheckInfo', 'CloudCredential', 'CloudSpec', 'Container', 'Context', 'DeferredEvent', 'ErrorStatus', 'Exec', 'ICMPPort', 'JujuLogLine', 'MaintenanceStatus', 'Manager', 'Model', 'Mount', 'Network', 'Notice', 'PeerRelation', 'Port', 'RawDataBagContents', 'RawSecretRevisionContents', 'Relation', 'RelationBase', 'Resource', 'Secret', 'State', 'StateValidationError', 'Storage', 'StoredState', 'SubordinateRelation', 'TCPPort', 'UDPPort', 'UnitID', 'UnknownStatus', 'WaitingStatus', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '_charmcraft_extensions', '_runtime', 'annotations', 'context', 'errors', 'layer_from_rockcraft', 'logger', 'state']
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm state-transition testing SDK for Ops charms.

Write tests that declaratively define the Juju state all at once, define the
Juju context against which to test the charm, and fire a single event on the
charm to execute its logic. The tests can then assert that the Juju state has
changed as expected.

These tests are 'state-transition' tests, a way to test isolated units of charm
functionality (how the state changes in reaction to events). They are not
necessarily tests of individual methods or functions (but might be, depending on
the charm's event observers); they are testing the 'contract' of the charm: given
a certain state, when a certain event happens, the charm should transition to a
certain (likely different) state. They do not test against a real Juju
controller and model, and focus on a single Juju unit, unlike integration tests.
For simplicity, we refer to them as 'unit' tests in the charm context.

Writing these tests should nudge you into thinking of a charm as a black-box
input->output function. The input is the union of an `Event` (why am I, charm,
being executed), a `State` (am I leader? what is my relation data? what is my
config?...) and the charm's execution `Context` (what relations can I have?
what containers can I have?...). The output is another `State`: the state after
the charm has had a chance to interact with the mocked Juju model and affect the
state.

.. image:: https://raw.githubusercontent.com/canonical/ops-scenario/main/resources/state-transition-model.png
   :alt: Transition diagram, with the input state and event on the left, the context
         including the charm in the centre, and the state out on the right

Writing unit tests for a charm, then, means verifying that:

- the charm does not raise uncaught exceptions while handling the event
- the output state (as compared with the input state) is as expected.

When the testing framework runs the event, the input state isn't modified. Instead, the output
state is a new `State` object. `State` objects are generally immutable - but be careful when
working with `dict` attributes, as they don't enforce immutability.

A test consists of three broad steps:

- **Arrange**:
    - declare the context
    - declare the input state
- **Act**:
    - select an event to fire
    - run the context (i.e. obtain the output state, given the input state and the event)
- **Assert**:
    - verify that the output state (as compared with the input state) is how you expect it to be
    - verify that the charm has seen a certain sequence of statuses, events, and `juju-log` calls
    - optionally, you can use a context manager to get a hold of the charm instance and run
      assertions on APIs and state internal to it.

The most basic scenario is one in which all is defaulted and barely any data is
available. The charm has no config, no relations, no leadership, and its
status is `unknown`. With that, we can write the simplest possible test:

.. code-block:: python

    def test_base():
        ctx = Context(MyCharm)
        out = ctx.run(ctx.on.start(), State())
        assert out.unit_status == UnknownStatus()
"""

from __future__ import annotations

from ops._private.harness import ActionFailed  # For backwards compatibility.

from .context import CharmEvents, Context, Manager
from .errors import StateValidationError  # For backwards compatibility.
from .state import (
    ActiveStatus,
    Address,
    AnyJson,
    BindAddress,
    BlockedStatus,
    CharmType,
    CheckInfo,
    CloudCredential,
    CloudSpec,
    Container,
    DeferredEvent,
    ErrorStatus,
    Exec,
    ICMPPort,
    JujuLogLine,
    MaintenanceStatus,
    Model,
    Mount,
    Network,
    Notice,
    PeerRelation,
    Port,
    RawDataBagContents,
    RawSecretRevisionContents,
    Relation,
    RelationBase,
    Resource,
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 49s</sub>

### 💬 Copilot

Now let me do a comprehensive search of all the patterns that need updating:

---

<sub>⏱️ 4m 50s</sub>

### ✅ `bash`

**Find all deprecated API usage**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && grep -rn "_BoundNotice\|output_state\|check_builtin_sequences\|\.replace(\|SCENARIO_SKIP_CONSISTENCY_CHECKS\|charm_spec" tests/ --include="*.py"

<details>
<summary>13 lines</summary>

```
tests/integration/tester-grpc/src/resources/webserver.py:38:APP_NAME = os.environ.get("APP_NAME").replace("-", "_")
tests/scenario/test_ingressed_tracing.py:20:    state = base_state.replace(relations=[tracing, ingress])
tests/scenario/test_ingressed_tracing.py:36:    state = base_state.replace(relations=[ingress])
tests/scenario/test_tls.py:27:    state = base_state.replace(relations=relations)
tests/scenario/test_charm.py:10:from scenario.sequences import check_builtin_sequences
tests/scenario/test_charm.py:11:from scenario.state import Notice, _BoundNotice
tests/scenario/test_charm.py:29:        check_builtin_sequences(tempo_charm, template_state=base_state)
tests/scenario/test_charm.py:64:        context.output_state.get_container("tempo").service_status["tempo"]
tests/scenario/test_charm.py:196:        monkeypatch.setenv("SCENARIO_SKIP_CONSISTENCY_CHECKS", "1")
tests/scenario/test_charm.py:198:        context.run(_BoundNotice(Notice(Tempo.tempo_ready_notice_key), tempo).event, state)
tests/scenario/test_charm.py:199:        monkeypatch.delenv("SCENARIO_SKIP_CONSISTENCY_CHECKS")
tests/scenario/test_tracing_legacy.py:16:    state = base_state.replace(relations=[tracing])
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 50s</sub>

### ✅ `bash`

**Check specific deprecated patterns in test_charm.py**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat tests/scenario/test_charm.py | grep -n "output_state\|replace\|_BoundNotice\|check_builtin\|SCENARIO"

<details>
<summary>8 lines</summary>

```
10:from scenario.sequences import check_builtin_sequences
11:from scenario.state import Notice, _BoundNotice
29:        check_builtin_sequences(tempo_charm, template_state=base_state)
64:        context.output_state.get_container("tempo").service_status["tempo"]
196:        monkeypatch.setenv("SCENARIO_SKIP_CONSISTENCY_CHECKS", "1")
198:        context.run(_BoundNotice(Notice(Tempo.tempo_ready_notice_key), tempo).event, state)
199:        monkeypatch.delenv("SCENARIO_SKIP_CONSISTENCY_CHECKS")
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 3s</sub>

### ✅ `bash`

**Check tracing legacy test**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat tests/scenario/test_tracing_legacy.py | head -50 && echo "===" && ls tests/scenario/

<details>
<summary>24 lines</summary>

```
import socket

import pytest
from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
from scenario import Container, Relation, State


@pytest.fixture
def base_state():
    return State(leader=True, containers=[Container("tempo", can_connect=False)])


@pytest.mark.parametrize("evt_name", ("changed", "created", "joined"))
def test_tracing_v2_endpoint_published(context, evt_name, base_state):
    tracing = Relation("tracing", remote_app_data={"receivers": "[]"})
    state = base_state.replace(relations=[tracing])

    with charm_tracing_disabled():
        with context.manager(getattr(tracing, f"{evt_name}_event"), state) as mgr:
            assert len(mgr.charm._requested_receivers()) == 1
            out = mgr.run()

    tracing_out = out.get_relations(tracing.endpoint)[0]
    assert tracing_out.local_app_data == {
        "receivers": f'[{{"protocol": {{"name": "otlp_http", "type": "http"}}, "url": "http://{socket.getfqdn()}:4318"}}]',
    }
===
conftest.py				     test_charm.py	    test_ingressed_tracing.py  test_tracing_provider.py
helpers.py				     test_charm_scaling.py  test_tls.py		       test_tracing_requirer.py
test_a_charm_tracer_multi_import_warning.py  test_charm_tracing.py  test_tracing_legacy.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 3s</sub>

### ✅ `bash`

**Run scenario test collection to see current failures**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && python3 -m pytest tests/scenario/ --collect-only 2>&1 | tail -30

```
ImportError while loading conftest '/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/conftest.py'.
tests/scenario/conftest.py:6: in <module>
    from charm import TempoCharm
E   ModuleNotFoundError: No module named 'charm'
<exited with exit code 0>
```


---

<sub>⏱️ 5m 12s</sub>

### ✅ `bash`

**Run scenario test collection with correct PYTHONPATH**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && PYTHONPATH=lib:src python3 -m pytest tests/scenario/ --collect-only 2>&1 | tail -40

<details>
<summary>38 lines</summary>

```
<Function test_invalid_data[data2]>
        <Function test_invalid_data[data3]>
        <Function test_broken>
        <Function test_requested_not_yet_replied>
        <Function test_not_requested_raises>

==================================== ERRORS ====================================
________________ ERROR collecting tests/scenario/test_charm.py _________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/scenario/test_charm.py:10: in <module>
    from scenario.sequences import check_builtin_sequences
E   ModuleNotFoundError: No module named 'scenario.sequences'
____________ ERROR collecting tests/scenario/test_charm_tracing.py _____________
ImportError while importing test module '/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_tracing.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/scenario/test_charm_tracing.py:20: in <module>
    from scenario.runtime import UncaughtCharmError
E   ModuleNotFoundError: No module named 'scenario.runtime'
=============================== warnings summary ===============================
<frozen importlib._bootstrap>:488
  <frozen importlib._bootstrap>:488: DeprecationWarning: Type google._upb._message.MessageMapContainer uses PyType_Spec with a metaclass that has custom tp_new. This is deprecated and will no longer be allowed in Python 3.14.

<frozen importlib._bootstrap>:488
  <frozen importlib._bootstrap>:488: DeprecationWarning: Type google._upb._message.ScalarMapContainer uses PyType_Spec with a metaclass that has custom tp_new. This is deprecated and will no longer be allowed in Python 3.14.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
ERROR tests/scenario/test_charm.py
ERROR tests/scenario/test_charm_tracing.py
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
==================== 32 tests collected, 2 errors in 0.16s =====================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 19s</sub>

### ✅ `bash`

**Read charm_tracing test file**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat tests/scenario/test_charm_tracing.py

<details>
<summary>479 lines</summary>

```
import functools
import logging
import os
from unittest.mock import patch

import pytest
import scenario
from charms.tempo_k8s.v1.charm_tracing import CHARM_TRACING_ENABLED, get_current_span, trace
from charms.tempo_k8s.v1.charm_tracing import _autoinstrument as autoinstrument
from charms.tempo_k8s.v2.tracing import (
    ProtocolType,
    Receiver,
    TracingEndpointRequirer,
    TracingProviderAppData,
    TracingRequirerAppData,
)
from ops import EventBase, EventSource, Framework
from ops.charm import CharmBase, CharmEvents
from scenario import Context, State
from scenario.runtime import UncaughtCharmError

os.environ[CHARM_TRACING_ENABLED] = "1"

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def cleanup():
    # if any other test module disabled it...
    os.environ[CHARM_TRACING_ENABLED] = "1"

    def patched_set_tracer_provider(tracer_provider, log):
        import opentelemetry

        opentelemetry.trace._TRACER_PROVIDER = tracer_provider

    with patch("opentelemetry.trace._set_tracer_provider", new=patched_set_tracer_provider):
        yield


class MyCharmSimple(CharmBase):
    META = {"name": "frank"}

    @property
    def tempo(self):
        return "foo.bar:80"


autoinstrument(MyCharmSimple, "tempo")


def test_base_tracer_endpoint(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmSimple, meta=MyCharmSimple.META)
        ctx.run("start", State())
        # assert "Setting up span exporter to endpoint: foo.bar:80" in caplog.text
        assert "Starting root trace with id=" in caplog.text
        span = f.call_args_list[0].args[0][0]
        assert span.resource.attributes["service.name"] == "frank-charm"
        assert span.resource.attributes["compose_service"] == "frank-charm"
        assert span.resource.attributes["charm_type"] == "MyCharmSimple"


class SubObject:
    def foo(self):
        return "bar"


class MyCharmSubObject(CharmBase):
    META = {"name": "frank"}

    def __init__(self, framework: Framework):
        super().__init__(framework)
        self.subobj = SubObject()
        framework.observe(self.on.start, self._on_start)

    def _on_start(self, _):
        self.subobj.foo()

    @property
    def tempo(self):
        return "foo.bar:80"


autoinstrument(MyCharmSubObject, "tempo", extra_types=[SubObject])


def test_subobj_tracer_endpoint(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmSubObject, meta=MyCharmSubObject.META)
        ctx.run("start", State())
        spans = f.call_args_list[0].args[0]
        assert spans[0].name == "method call: SubObject.foo"


class MyCharmInitAttr(CharmBase):
    META = {"name": "frank"}

    def __init__(self, framework: Framework):
        super().__init__(framework)
        self._tempo = "foo.bar:80"

    @property
    def tempo(self):
        return self._tempo


autoinstrument(MyCharmInitAttr, "tempo")


def test_init_attr(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmInitAttr, meta=MyCharmInitAttr.META)
        ctx.run("start", State())
        # assert "Setting up span exporter to endpoint: foo.bar:80" in caplog.text
        span = f.call_args_list[0].args[0][0]
        assert span.resource.attributes["service.name"] == "frank-charm"
        assert span.resource.attributes["compose_service"] == "frank-charm"
        assert span.resource.attributes["charm_type"] == "MyCharmInitAttr"


class MyCharmSimpleDisabled(CharmBase):
    META = {"name": "frank"}

    @property
    def tempo(self):
        return None


autoinstrument(MyCharmSimpleDisabled, "tempo")


def test_base_tracer_endpoint_disabled(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmSimpleDisabled, meta=MyCharmSimpleDisabled.META)
        ctx.run("start", State())

        # assert "quietly disabling charm_tracing for the run." in caplog.text
        assert not f.called


@trace
def _my_fn(foo):
    return foo + 1


class MyCharmSimpleEvent(CharmBase):
    META = {"name": "frank"}

    def __init__(self, fw):
        super().__init__(fw)
        span = get_current_span()
        assert span is None  # can't do that in init.
        fw.observe(self.on.start, self._on_start)

    def _on_start(self, _):
        span = get_current_span()
        span.add_event(
            "log",
            {
                "foo": "bar",
                "baz": "qux",
            },
        )
        _my_fn(2)

    @property
    def tempo(self):
        return "foo.bar:80"


autoinstrument(MyCharmSimpleEvent, "tempo")


def test_base_tracer_endpoint_event(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmSimpleEvent, meta=MyCharmSimpleEvent.META)
        ctx.run("start", State())

        spans = f.call_args_list[0].args[0]
        span0, span1, span2, span3 = spans
        assert span0.name == "function call: _my_fn"

        assert span1.name == "method call: MyCharmSimpleEvent._on_start"

        assert span2.name == "event: start"
        evt = span2.events[0]
        assert evt.name == "start"

        assert span3.name == "frank/0: start event"

        for span in spans:
            assert span.resource.attributes["service.name"] == "frank-charm"


def test_juju_topology_injection(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmSimpleEvent, meta=MyCharmSimpleEvent.META)
        state = ctx.run("start", State())

        spans = f.call_args_list[0].args[0]

        for span in spans:
            # topology
            assert span.resource.attributes["juju_unit"] == "frank/0"
            assert span.resource.attributes["juju_application"] == "frank"
            assert span.resource.attributes["juju_model"] == state.model.name
            assert span.resource.attributes["juju_model_uuid"] == state.model.uuid


class MyCharmWithMethods(CharmBase):
    META = {"name": "frank"}

    def __init__(self, fw):
        super().__init__(fw)
        fw.observe(self.on.start, self._on_start)

    def _on_start(self, _):
        self.a()
        self.b()
        self.c()

    def a(self):
        pass

    def b(self):
        pass

    def c(self):
        pass

    @property
    def tempo(self):
        return "foo.bar:80"


autoinstrument(MyCharmWithMethods, "tempo")


def test_base_tracer_endpoint_methods(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmWithMethods, meta=MyCharmWithMethods.META)
        ctx.run("start", State())

        spans = f.call_args_list[0].args[0]
        span_names = [span.name for span in spans]
        assert span_names == [
            "method call: MyCharmWithMethods.a",
            "method call: MyCharmWithMethods.b",
            "method call: MyCharmWithMethods.c",
            "method call: MyCharmWithMethods._on_start",
            "event: start",
            "frank/0: start event",
        ]


class Foo(EventBase):
    pass


class MyEvents(CharmEvents):
    foo = EventSource(Foo)


class MyCharmWithCustomEvents(CharmBase):
    on = MyEvents()

    META = {"name": "frank"}

    def __init__(self, fw):
        super().__init__(fw)
        fw.observe(self.on.start, self._on_start)
        fw.observe(self.on.foo, self._on_foo)

    def _on_start(self, _):
        self.on.foo.emit()

    def _on_foo(self, _):
        pass

    @property
    def tempo(self):
        return "foo.bar:80"


autoinstrument(MyCharmWithCustomEvents, "tempo")


def test_base_tracer_endpoint_custom_event(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmWithCustomEvents, meta=MyCharmWithCustomEvents.META)
        ctx.run("start", State())

        spans = f.call_args_list[0].args[0]
        span_names = [span.name for span in spans]
        assert span_names == [
            "method call: MyCharmWithCustomEvents._on_foo",
            "event: foo",
            "method call: MyCharmWithCustomEvents._on_start",
            "event: start",
            "frank/0: start event",
        ]
        # only the charm exec span is a root
        assert not spans[-1].parent
        for span in spans[:-1]:
            assert span.parent
            assert span.parent.trace_id
        assert len({(span.parent.trace_id if span.parent else 0) for span in spans}) == 2


class MyRemoteCharm(CharmBase):
    META = {"name": "charlie", "requires": {"tracing": {"interface": "tracing", "limit": 1}}}
    _request = True

    def __init__(self, framework: Framework):
        super().__init__(framework)
        self.tracing = TracingEndpointRequirer(
            self, "tracing", protocols=(["otlp_http"] if self._request else [])
        )

    def tempo(self):
        return self.tracing.get_endpoint("otlp_http")


autoinstrument(MyRemoteCharm, "tempo")


@pytest.mark.parametrize("leader", (True, False))
def test_tracing_requirer_remote_charm_request_response(leader):
    # IF the leader unit (whoever it is) did request the endpoint to be activated
    MyRemoteCharm._request = True
    ctx = Context(MyRemoteCharm, meta=MyRemoteCharm.META)
    # WHEN you get any event AND the remote unit has already replied
    tracing = scenario.Relation(
        "tracing",
        # if we're not leader, assume the leader did its part already
        local_app_data=(
            TracingRequirerAppData(receivers=["otlp_http"]).dump() if not leader else {}
        ),
        remote_app_data=TracingProviderAppData(
            host="foo.com",
            receivers=[
                Receiver(
                    url="http://foo.com:80", protocol=ProtocolType(name="otlp_http", type="http")
                )
            ],
        ).dump(),
    )
    with ctx.manager("start", State(leader=leader, relations=[tracing])) as mgr:
        # THEN you're good
        assert mgr.charm.tempo() == "http://foo.com:80"


@pytest.mark.parametrize("leader", (True, False))
def test_tracing_requirer_remote_charm_no_request_but_response(leader):
    # IF the leader did NOT request the endpoint to be activated
    MyRemoteCharm._request = False
    ctx = Context(MyRemoteCharm, meta=MyRemoteCharm.META)
    # WHEN you get any event AND the remote unit has already replied
    tracing = scenario.Relation(
        "tracing",
        # empty local app data
        remote_app_data=TracingProviderAppData(
            # but the remote end has sent the data you need
            receivers=[
                Receiver(
                    url="http://foo.com:80", protocol=ProtocolType(name="otlp_http", type="http")
                )
            ],
        ).dump(),
    )
    with ctx.manager("start", State(leader=leader, relations=[tracing])) as mgr:
        # THEN you're lucky, but you're good
        assert mgr.charm.tempo() == "http://foo.com:80"


@pytest.mark.parametrize("relation", (True, False))
@pytest.mark.parametrize("leader", (True, False))
def test_tracing_requirer_remote_charm_no_request_no_response(leader, relation):
    """Verify that the charm errors out (even with charm_tracing disabled) if the tempo() call raises."""
    # IF the leader did NOT request the endpoint to be activated
    MyRemoteCharm._request = False
    ctx = Context(MyRemoteCharm, meta=MyRemoteCharm.META)
    # WHEN you get any event
    if relation:
        # AND you have an empty relation
        tracing = scenario.Relation(
            "tracing",
            # empty local and remote app data
        )
        relations = [tracing]
    else:
        # OR no relation at all
        relations = []

    # THEN self.tempo() will raise on init
    # FIXME: non-leader units should get a permission denied exception,
    # but it won't fire due to https://github.com/canonical/operator/issues/1378
    with pytest.raises(UncaughtCharmError, match=r"ProtocolNotRequestedError"):
        ctx.run("start", State(relations=relations, leader=leader))


class MyRemoteBorkyCharm(CharmBase):
    META = {"name": "charlie", "requires": {"tracing": {"interface": "tracing", "limit": 1}}}
    _borky_return_value = None

    def tempo(self):
        return self._borky_return_value


autoinstrument(MyRemoteBorkyCharm, "tempo")


@pytest.mark.parametrize("borky_return_value", (True, 42, object(), 0.2, [], (), {}))
def test_borky_tempo_return_value(borky_return_value, caplog):
    """Verify that the charm exits 1 (even with charm_tracing disabled) if the tempo() call returns bad values."""
    # IF the charm's tempo endpoint getter returns anything but None or str
    MyRemoteBorkyCharm._borky_return_value = borky_return_value
    ctx = Context(MyRemoteBorkyCharm, meta=MyRemoteBorkyCharm.META)
    # WHEN you get any event
    # THEN the self.tempo getter will raise and charm exec will exit 1

    # traceback from the TypeError raised by _get_tracing_endpoint
    with pytest.raises(
        UncaughtCharmError,
        match=r"MyRemoteBorkyCharm\.tempo should resolve to a tempo "
        r"endpoint \(string\); got (.*) instead\.",
    ):
        ctx.run("start", State())


class MyCharmStaticMethods(CharmBase):
    META = {"name": "jolene"}

    def __init__(self, fw):
        super().__init__(fw)
        fw.observe(self.on.start, self._on_start)
        fw.observe(self.on.update_status, self._on_update_status)

    def _on_start(self, _):
        for o in (OtherObj(), OtherObj):
            for meth in ("_staticmeth", "_staticmeth1", "_staticmeth2"):
                assert getattr(o, meth)(1) == 2

    def _on_update_status(self, _):
        # super-ugly edge cases
        OtherObj()._staticmeth3(OtherObj())
        OtherObj()._staticmeth4(OtherObj())
        OtherObj._staticmeth3(OtherObj())
        OtherObj._staticmeth4(OtherObj(), foo=2)

    @property
    def tempo(self):
        return "foo.bar:80"


class OtherObj:
    @staticmethod
    def _staticmeth(i: int, *args, **kwargs):
        return 1 + i

    @staticmethod
    def _staticmeth1(i: int):
        return 1 + i

    @staticmethod
    def _staticmeth2(i: int, foo="bar"):
        return 1 + i

    @staticmethod
    def _staticmeth3(abc: "OtherObj", foo="bar"):
        return 1 + 1

    @staticmethod
    def _staticmeth4(abc: int, foo="bar"):
        return 1 + 1


autoinstrument(MyCharmStaticMethods, "tempo", extra_types=[OtherObj])


def test_trace_staticmethods(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmStaticMethods, meta=MyCharmStaticMethods.META)
        ctx.run("start", State())

        spans = f.call_args_list[0].args[0]

        span_names = [span.name for span in spans]
        assert span_names == [
            "method call: OtherObj._staticmeth",
            "method call: OtherObj._staticmeth1",
            "method call: OtherObj._staticmeth2",
            "method call: OtherObj._staticmeth",
            "method call: OtherObj._staticmeth1",
            "method call: OtherObj._staticmeth2",
            "method call: MyCharmStaticMethods._on_start",
            "event: start",
            "jolene/0: start event",
        ]

        for span in spans:
            assert span.resource.attributes["service.name"] == "jolene-charm"


def test_trace_staticmethods_bork(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmStaticMethods, meta=MyCharmStaticMethods.META)
        ctx.run("update-status", State())


class SuperCharm(CharmBase):
    def foo(self):
        return "bar"


class MyInheritedCharm(SuperCharm):
    META = {"name": "godcat"}

    def __init__(self, framework: Framework):
        super().__init__(framework)
        framework.observe(self.on.start, self._on_start)

    def _on_start(self, _):
        self.foo()

    @property
    def tempo(self):
        return "foo.bar:80"


autoinstrument(MyInheritedCharm, "tempo")


def test_inheritance_tracing(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyInheritedCharm, meta=MyInheritedCharm.META)
        ctx.run("start", State())
        spans = f.call_args_list[0].args[0]
        assert spans[0].name == "method call: SuperCharm.foo"


def bad_wrapper(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def good_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class MyCharmWrappedMethods(CharmBase):
    META = {"name": "catgod"}

    def __init__(self, fw):
        super().__init__(fw)
        fw.observe(self.on.start, self._on_start)

    @good_wrapper
    def a(self):
        pass

    @bad_wrapper
    def b(self):
        pass

    def _on_start(self, _):
        self.a()
        self.b()

    @property
    def tempo(self):
        return "foo.bar:80"


autoinstrument(MyCharmWrappedMethods, "tempo")


def test_wrapped_method_wrapping(caplog):
    import opentelemetry

    with patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter.export"
    ) as f:
        f.return_value = opentelemetry.sdk.trace.export.SpanExportResult.SUCCESS
        ctx = Context(MyCharmWrappedMethods, meta=MyCharmWrappedMethods.META)
        ctx.run("start", State())
        spans = f.call_args_list[0].args[0]
        assert spans[0].name == "method call: MyCharmWrappedMethods.a"
        assert spans[1].name == "method call: @bad_wrapper(MyCharmWrappedMethods.b)"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 31s</sub>

### ✅ `bash`

**Check UncaughtCharmError location**

$ python3 -c "
from scenario.errors import UncaughtCharmError
print('UncaughtCharmError from scenario.errors works')
" 2>&1
python3 -c "
from scenario import Context, State
from ops import CharmBase
import pytest

class BadCharm(CharmBase):
    META = {'name': 'test'}
    def __init__(self, fw):
        super().__init__(fw)
        fw.observe(self.on.start, self._on_start)
    def _on_start(self, _):
        raise ValueError('test error')

ctx = Context(BadCharm, meta=BadCharm.META)
try:
    ctx.run(ctx.on.start(), State())
except Exception as e:
    print(type(e).__name__, type(e).__module__)
" 2>&1

```
UncaughtCharmError from scenario.errors works
UncaughtCharmError scenario.errors
<exited with exit code 0>
```


---

<sub>⏱️ 5m 31s</sub>

### ✅ `bash`

**Check ops.testing error classes**

$ python3 -c "
# Check what's the right import for UncaughtCharmError in ops 3.7.0
import ops
print('ops.testing has ActionFailed:', hasattr(ops.testing, 'ActionFailed'))
# scenario re-exports it from ops._private.harness
from ops._private.harness import ActionFailed
print('ActionFailed:', ActionFailed)
# What about UncaughtCharmError? 
import ops
for attr in dir(ops):
    if 'Uncaught' in attr or 'Error' in attr:
        print(attr)
" 2>&1

```
Traceback (most recent call last):
  File "<string>", line 4, in <module>
AttributeError: module 'ops' has no attribute 'testing'
<exited with exit code 1>
```


---

<sub>⏱️ 5m 43s</sub>

### 💬 Copilot

Now I have a clear picture. Let me look at a few remaining files, then plan and implement all fixes:

---

<sub>⏱️ 5m 44s</sub>

### ✅ `bash`

**Check more context in test_charm.py**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && grep -n "replace\|output_state\|context\." tests/scenario/test_charm.py | head -30

<details>
<summary>8 lines</summary>

```
35:        context.run("start", base_state)
53:    context.run(ingress.changed_event, state)
64:        context.output_state.get_container("tempo").service_status["tempo"]
128:    state_out = context.run(tracing.created_event, state)
142:    context.run("update-status", state)
179:    context.run(s3_relation.changed_event, state)
198:        context.run(_BoundNotice(Notice(Tempo.tempo_ready_notice_key), tempo).event, state)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 44s</sub>

### ✅ `bash`

**Check remaining test files for deprecated patterns**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && grep -n "\.replace(\|output_state\|context\." tests/scenario/test_charm_scaling.py tests/scenario/test_tracing_provider.py tests/scenario/test_tracing_requirer.py 2>/dev/null | head -30

<details>
<summary>18 lines</summary>

```
tests/scenario/test_charm_scaling.py:9:    state_out = context.run(
tests/scenario/test_charm_scaling.py:16:    state_out = context.run(
tests/scenario/test_charm_scaling.py:28:    state_out = context.run(
tests/scenario/test_charm_scaling.py:58:    state_out = context.run(
tests/scenario/test_tracing_provider.py:39:        with context.manager(tracing_grpc.broken_event, state) as mgr:
tests/scenario/test_tracing_requirer.py:48:        with context.manager(tracing.changed_event, state) as mgr:
tests/scenario/test_tracing_requirer.py:57:    rchanged, epchanged = context.emitted_events
tests/scenario/test_tracing_requirer.py:77:        with context.manager(tracing.changed_event, state) as mgr:
tests/scenario/test_tracing_requirer.py:86:    rchanged, epchanged = context.emitted_events
tests/scenario/test_tracing_requirer.py:106:        with context.manager(tracing.changed_event, state) as mgr:
tests/scenario/test_tracing_requirer.py:121:    rchanged, epchanged = context.emitted_events
tests/scenario/test_tracing_requirer.py:159:        context.run(tracing.changed_event, state, post_event=post_event)
tests/scenario/test_tracing_requirer.py:161:    emitted_events = context.emitted_events
tests/scenario/test_tracing_requirer.py:173:        context.run(tracing.broken_event, state)
tests/scenario/test_tracing_requirer.py:175:    emitted_events = context.emitted_events
tests/scenario/test_tracing_requirer.py:187:        with context.manager(tracing.created_event, state) as mgr:
tests/scenario/test_tracing_requirer.py:198:        with context.manager(tracing.created_event, state) as mgr:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 52s</sub>

### ✅ `bash`

**Check context.emitted_events in new API**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && python3 -c "
from scenario import Context, State
# Check emitted_events - is it still available on Context?
import inspect
src = inspect.getsource(Context)
for line in src.split('\n'):
    if 'emitted' in line.lower():
        print(line)
"

<details>
<summary>13 lines</summary>

```
"""Testing context in which events are emitted.
    - :attr:`emitted_events`
            assert len(ctx.emitted_events) == 4
            assert isinstance(ctx.emitted_events[3], MyCustomEvent)
    emitted_events: list[ops.EventBase]
    -  `capture_deferred_events`: If you want to include re-emitted deferred events.
        def test_emitted():
            assert len(ctx.emitted_events) == 5
            assert [e.handle.kind for e in ctx.emitted_events] == [
        # config for what events to be captured in emitted_events.
        self.emitted_events: list[ops.EventBase] = []
        """Context manager to introspect live charm object before and after the event is emitted.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 52s</sub>

### ✅ `bash`

**Check Context attributes in new version**

$ python3 -c "
from scenario import Context, State
from ops import CharmBase
ctx = Context(CharmBase, meta={'name': 'test'})
print('emitted_events attr:', hasattr(ctx, 'emitted_events'))
print('output_state attr:', hasattr(ctx, 'output_state'))
# Check context manager usage
import inspect
print('Context attrs:', [x for x in dir(ctx) if not x.startswith('__')])
"

```
emitted_events attr: True
output_state attr: False
Context attrs: ['_action_failure_message', '_availability_zone', '_charm_spec', '_get_container_root', '_get_storage_root', '_machine_id', '_output_state', '_principal_unit', '_record_status', '_run', '_set_output_state', '_tmp', 'action_logs', 'action_results', 'app_name', 'app_status_history', 'app_trusted', 'capture_deferred_events', 'capture_framework_events', 'charm_root', 'charm_spec', 'emitted_events', 'exec_history', 'juju_log', 'juju_version', 'on', 'removed_secret_revisions', 'requested_storages', 'run', 'run_action', 'trace_data', 'unit_id', 'unit_status_history', 'workload_version_history']
<exited with exit code 0>
```


---

<sub>⏱️ 6m 0s</sub>

### ✅ `bash`

**Check Context.run and __call__ signatures**

$ python3 -c "
from scenario import Context
import inspect
sig = inspect.signature(Context.run)
print('Context.run signature:', sig)
sig2 = inspect.signature(Context.__call__)
print('Context.__call__ signature:', sig2)
"

```
Context.run signature: (self, event: '_Event', state: 'State') -> 'State'
Context.__call__ signature: (self, event: '_Event', state: 'State') -> 'Manager[CharmType]'
<exited with exit code 0>
```


---

<sub>⏱️ 6m 5s</sub>

### ✅ `bash`

**Check post_event usage in test_tracing_requirer.py**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat tests/scenario/test_tracing_requirer.py | head -170 | tail -50

<details>
<summary>44 lines</summary>

```
rchanged, epchanged = context.emitted_events
    assert isinstance(epchanged, EndpointChangedEvent)
    assert epchanged.receivers[0].protocol.name == "otlp_grpc"


@pytest.mark.parametrize(
    "data",
    (
        {
            "ingesters": '[{"protocol": "otlp_grpc", "port": 9999}]',
            "bar": "baz",
        },
        {
            "host": "foo.com",
            "bar": "baz",
        },
        {
            "ingesters": '[{"burp": "barp", "port": 3200}]',
            "host": "foo.com",
        },
        {
            "ingesters": '[{"protocol": "tempo", "burp": "borp"}]',
            "host": "foo.com",
        },
    ),
)
def test_invalid_data(context, data):
    tracing = Relation(
        "tracing",
        remote_app_data=data,
    )
    state = State(leader=True, relations=[tracing])

    def post_event(charm: MyCharm):
        rel = charm.model.get_relation("tracing")
        assert not charm.tracing.is_ready(rel)

    with charm_tracing_disabled():
        context.run(tracing.changed_event, state, post_event=post_event)

    emitted_events = context.emitted_events
    assert len(emitted_events) == 2
    rchanged, rremoved = emitted_events
    assert isinstance(rchanged, RelationChangedEvent)
    assert isinstance(rremoved, EndpointRemovedEvent)


def test_broken(context):
    tracing = Relation("tracing")
    state = State(leader=True, relations=[tracing])
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 15s</sub>

### ✅ `bash`

**Check Context.run implementation**

$ python3 << 'EOF'
import scenario
import inspect

src = inspect.getsource(scenario.context.Context.run)
print(src)
EOF

<details>
<summary>61 lines</summary>

```
def run(self, event: _Event, state: State) -> State:
        """Trigger a charm execution with an event and a State.

        Calling this function will call ``ops.main`` and set up the context according to the
        specified :class:`State`, then emit the event on the charm.

        :arg event: the event that the charm will respond to. Use the :attr:`on` attribute to
            specify the event; for example: ``ctx.on.start()``.
        :arg state: the :class:`State` instance to use as data source for the hook command
            calls that the charm will invoke when handling the event.
        """
        # Help people transition from Scenario 6:
        if isinstance(event, str):
            event = event.replace('-', '_')  # type: ignore
            if event in (
                'install',
                'start',
                'stop',
                'remove',
                'update_status',
                'config_changed',
                'upgrade_charm',
                'pre_series_upgrade',
                'post_series_upgrade',
                'leader_elected',
                'collect_app_status',
                'collect_unit_status',
            ):  # type: ignore
                suggested = f'{event}()'
            elif event in ('secret_changed', 'secret_rotate'):  # type: ignore
                suggested = f'{event}(my_secret)'
            elif event in ('secret_expired', 'secret_remove'):  # type: ignore
                suggested = f'{event}(my_secret, revision=1)'
            elif event in (
                'relation_created',
                'relation_joined',
                'relation_changed',
                'relation_departed',
                'relation_broken',
            ):  # type: ignore
                suggested = f'{event}(my_relation)'
            elif event in ('storage_attached', 'storage_detaching'):  # type: ignore
                suggested = f'{event}(my_storage)'
            elif event == 'pebble_ready':
                suggested = f'{event}(my_container)'
            elif event == 'pebble_custom_notice':
                suggested = f'{event}(my_container, my_notice)'
            else:
                suggested = 'event()'
            raise TypeError(
                f'call with an event from `ctx.on`, like `ctx.on.{suggested}`',
            )
        if callable(event):
            raise TypeError(
                'You should call the event method. Did you forget to add parentheses?',
            )

        with self._run(event=event, state=state) as ops:
            ops.run()
        # We know that the output state will have been set by this point,
        # so let the type checkers know that too.
        assert self._output_state is not None
        return self._output_state
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 24s</sub>

### ✅ `bash`

**Check Manager class implementation**

$ python3 << 'EOF'
import scenario
import inspect

src = inspect.getsource(scenario.context.Manager)
print(src[:3000])
EOF

<details>
<summary>63 lines</summary>

```
class Manager(Generic[CharmType]):
    """Context manager to offer test code some runtime charm object introspection.

    This class should not be instantiated directly: use a :class:`Context`
    in a ``with`` statement instead, for example::

        ctx = Context(MyCharm)
        with ctx(ctx.on.start(), State()) as manager:
            manager.charm.setup()
            manager.run()
    """

    def __init__(
        self,
        ctx: Context[CharmType],
        arg: _Event,
        state_in: State,
    ):
        self._ctx = ctx
        self._arg = arg
        self._state_in = state_in

        self._emitted: bool = False

        self.ops: Ops[CharmType] | None = None

    @property
    def charm(self) -> CharmType:
        """The charm object instantiated by ops to handle the event.

        The charm is only available during the context manager scope.
        """
        if self.ops is None or self.ops.charm is None:
            raise RuntimeError(
                'you should __enter__ this context manager before accessing this',
            )
        return self.ops.charm

    @property
    def _runner(self):
        return self._ctx._run

    def __enter__(self):
        self._wrapped_ctx = wrapped_ctx = self._runner(self._arg, self._state_in)
        self.ops = wrapped_ctx.__enter__()
        return self

    def run(self) -> State:
        """Emit the event and proceed with charm execution.

        This can only be done once.
        """
        if self._emitted:
            raise AlreadyEmittedError('Can only run once.')
        if not self.ops:
            raise RuntimeError(
                'you should __enter__ this context manager before running it',
            )
        self._emitted = True
        self.ops.run()

        # wrap up Runtime.exec() so that we can gather the output state
        self._wrapped_ctx.__exit__(None, None, None)

        assert self._ctx._output_state is not None
        return self._ctx._output_state

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        if not self._emitted:
            logger.debug(
                "user didn't emit the event within the context manager scope. "
                'Doing so implicitly upon exit...',
            )
            self.run()
        if exc_type is not None:
            self._wrapped_ctx.__exit__(exc_type, exc_val, exc_tb)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 43s</sub>

### ✅ `bash`

**Test if charm is accessible after mgr.run()**

$ python3 << 'EOF'
from scenario import Context, State
from ops import CharmBase

class MyCharm(CharmBase):
    META = {'name': 'test'}
    def __init__(self, fw):
        super().__init__(fw)
        fw.observe(self.on.start, self._on_start)
    def _on_start(self, _):
        pass

ctx = Context(MyCharm, meta=MyCharm.META)

# Test if charm is accessible after mgr.run()
with ctx(ctx.on.start(), State()) as mgr:
    state_out = mgr.run()
    try:
        print('charm accessible after run:', mgr.charm)
    except Exception as e:
        print('charm not accessible after run:', e)
EOF

```
charm accessible after run: <__main__.MyCharm object at 0x7de8b9c9d1c0>
<exited with exit code 0>
```


---

<sub>⏱️ 7m 18s</sub>

### ✅ `bash`

**Find all context.run and context.manager calls**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && grep -n 'context\.run\|context\.manager\|ctx\.run\|ctx\.manager' tests/scenario/*.py | grep -v "^.*:.*context\.(run|manager)\(ctx\." | head -50

```
grep: Unmatched ( or \(
<exited with exit code 0>
```


---

<sub>⏱️ 7m 17s</sub>

### ✅ `bash`

**Find all test run/manager calls**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && grep -n 'context\.run\|context\.manager\|\.run(\|\.manager(' tests/scenario/*.py | head -60

<details>
<summary>41 lines</summary>

```
tests/scenario/test_a_charm_tracer_multi_import_warning.py:57:            ctx.run("start", State())
tests/scenario/test_charm.py:35:        context.run("start", base_state)
tests/scenario/test_charm.py:53:    context.run(ingress.changed_event, state)
tests/scenario/test_charm.py:128:    state_out = context.run(tracing.created_event, state)
tests/scenario/test_charm.py:142:    context.run("update-status", state)
tests/scenario/test_charm.py:179:    context.run(s3_relation.changed_event, state)
tests/scenario/test_charm.py:198:        context.run(_BoundNotice(Notice(Tempo.tempo_ready_notice_key), tempo).event, state)
tests/scenario/test_charm_scaling.py:9:    state_out = context.run(
tests/scenario/test_charm_scaling.py:16:    state_out = context.run(
tests/scenario/test_charm_scaling.py:28:    state_out = context.run(
tests/scenario/test_charm_scaling.py:58:    state_out = context.run(
tests/scenario/test_charm_tracing.py:60:        ctx.run("start", State())
tests/scenario/test_charm_tracing.py:101:        ctx.run("start", State())
tests/scenario/test_charm_tracing.py:129:        ctx.run("start", State())
tests/scenario/test_charm_tracing.py:156:        ctx.run("start", State())
tests/scenario/test_charm_tracing.py:203:        ctx.run("start", State())
tests/scenario/test_charm_tracing.py:229:        state = ctx.run("start", State())
tests/scenario/test_charm_tracing.py:278:        ctx.run("start", State())
tests/scenario/test_charm_tracing.py:332:        ctx.run("start", State())
tests/scenario/test_charm_tracing.py:389:    with ctx.manager("start", State(leader=leader, relations=[tracing])) as mgr:
tests/scenario/test_charm_tracing.py:412:    with ctx.manager("start", State(leader=leader, relations=[tracing])) as mgr:
tests/scenario/test_charm_tracing.py:440:        ctx.run("start", State(relations=relations, leader=leader))
tests/scenario/test_charm_tracing.py:469:        ctx.run("start", State())
tests/scenario/test_charm_tracing.py:530:        ctx.run("start", State())
tests/scenario/test_charm_tracing.py:559:        ctx.run("update-status", State())
tests/scenario/test_charm_tracing.py:593:        ctx.run("start", State())
tests/scenario/test_charm_tracing.py:648:        ctx.run("start", State())
tests/scenario/test_ingressed_tracing.py:23:        out = context.run(getattr(tracing, "created_event"), state)
tests/scenario/test_ingressed_tracing.py:39:        out = context.run(ingress.joined_event, state)
tests/scenario/test_tls.py:29:        out = context.run(tracing.changed_event, state)
tests/scenario/test_tracing_legacy.py:19:        with context.manager(getattr(tracing, f"{evt_name}_event"), state) as mgr:
tests/scenario/test_tracing_legacy.py:21:            out = mgr.run()
tests/scenario/test_tracing_provider.py:39:        with context.manager(tracing_grpc.broken_event, state) as mgr:
tests/scenario/test_tracing_requirer.py:48:        with context.manager(tracing.changed_event, state) as mgr:
tests/scenario/test_tracing_requirer.py:77:        with context.manager(tracing.changed_event, state) as mgr:
tests/scenario/test_tracing_requirer.py:106:        with context.manager(tracing.changed_event, state) as mgr:
tests/scenario/test_tracing_requirer.py:159:        context.run(tracing.changed_event, state, post_event=post_event)
tests/scenario/test_tracing_requirer.py:173:        context.run(tracing.broken_event, state)
tests/scenario/test_tracing_requirer.py:187:        with context.manager(tracing.created_event, state) as mgr:
tests/scenario/test_tracing_requirer.py:198:        with context.manager(tracing.created_event, state) as mgr:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 30s</sub>

### ✅ `bash`

**Verify relation.event still works**

$ python3 -c "
from scenario import Relation
r = Relation('test')
print(type(r.changed_event))
print(r.changed_event)
# check created_event
print(type(r.created_event))
"

```
Traceback (most recent call last):
  File "<string>", line 4, in <module>
AttributeError: 'Relation' object has no attribute 'changed_event'
<exited with exit code 1>
```


---

<sub>⏱️ 7m 30s</sub>

### ✅ `bash`

**Test that relation events still work**

$ python3 -c "
from scenario import Context, State, Relation
from ops import CharmBase

class MyCharm(CharmBase):
    META = {'name': 'test', 'requires': {'foo': {'interface': 'bar'}}}
    def __init__(self, fw): super().__init__(fw)

ctx = Context(MyCharm, meta=MyCharm.META)
r = Relation('foo')
state = State(relations=[r])
# Test that relation events still work
out = ctx.run(r.changed_event, state)
print('relation.changed_event works:', out)
" 2>&1

```
Traceback (most recent call last):
  File "<string>", line 13, in <module>
AttributeError: 'Relation' object has no attribute 'changed_event'
<exited with exit code 1>
```


---

<sub>⏱️ 7m 38s</sub>

### ✅ `bash`

**Check Relation attributes**

$ python3 -c "
from scenario import Relation
r = Relation('test')
print([x for x in dir(r) if not x.startswith('_')])
"

```
['endpoint', 'id', 'interface', 'limit', 'local_app_data', 'local_unit_data', 'relation_id', 'remote_app_data', 'remote_app_name', 'remote_model_uuid', 'remote_units_data']
<exited with exit code 0>
```


---

<sub>⏱️ 7m 49s</sub>

### ✅ `bash`

**Test new event API**

$ python3 -c "
from scenario import Context, State, Relation
from ops import CharmBase

class MyCharm(CharmBase):
    META = {'name': 'test', 'requires': {'foo': {'interface': 'bar'}}}
    def __init__(self, fw): super().__init__(fw)

ctx = Context(MyCharm, meta=MyCharm.META)
r = Relation('foo')
state = State(relations=[r])

# Test ctx.on.relation_changed
out = ctx.run(ctx.on.relation_changed(r), state)
print('ctx.on.relation_changed works')

# Test context manager
with ctx(ctx.on.relation_changed(r), state) as mgr:
    out2 = mgr.run()
print('context manager works')

# Does context.manager also work?
print('context.manager:', hasattr(ctx, 'manager'))
" 2>&1

<details>
<summary>6 lines</summary>

```
This scenario is probably inconsistent. Double check, and ignore this warning if you're sure. The following warnings were found: 'foo_relation_changed' is implicitly using 0 as the remote unit. Consider passing `remote_unit` explicitly.
ctx.on.relation_changed works
This scenario is probably inconsistent. Double check, and ignore this warning if you're sure. The following warnings were found: 'foo_relation_changed' is implicitly using 0 as the remote unit. Consider passing `remote_unit` explicitly.
context manager works
context.manager: False
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 24s</sub>

### ✅ `bash`

**Check Container.get_filesystem signature**

$ python3 -c "
from scenario import Container
import inspect
sig = inspect.signature(Container.get_filesystem)
print('get_filesystem signature:', sig)
" 2>&1

```
get_filesystem signature: (self, ctx: 'Context[Any]') -> 'pathlib.Path'
<exited with exit code 0>
```


---

<sub>⏱️ 8m 30s</sub>

### ✅ `bash`

**Check Container field names**

$ python3 -c "
# Check if service_status or service_statuses is used in new State
from scenario import Container, State
import dataclasses
# Check what field name is used
fields = dataclasses.fields(Container)
for f in fields:
    print(f.name, f.type)
"

<details>
<summary>10 lines</summary>

```
name str
can_connect bool
_base_plan Mapping[str, Any]
layers Mapping[str, pebble.Layer]
service_statuses Mapping[str, pebble.ServiceStatus]
mounts Mapping[str, Mount]
execs Iterable[Exec]
notices Sequence[Notice]
check_infos Iterable[CheckInfo]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 40s</sub>

### ✅ `bash`

**Test service_statuses vs service_status**

$ python3 -c "
from scenario import Container
import ops.pebble as pebble
# Test service_statuses
c = Container('test', can_connect=True, service_statuses={'svc': pebble.ServiceStatus.ACTIVE})
print('service_statuses:', c.service_statuses)
# Try old service_status
try:
    c2 = Container('test', service_status={'svc': pebble.ServiceStatus.ACTIVE})
    print('old service_status works:', c2.service_statuses)
except Exception as e:
    print('old service_status fails:', e)
" 2>&1

```
service_statuses: {'svc': <ServiceStatus.ACTIVE: 'active'>}
old service_status fails: Container.__init__() got an unexpected keyword argument 'service_status'
<exited with exit code 0>
```


---

<sub>⏱️ 8m 47s</sub>

### ✅ `bash`

**Find all service_status usages**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && grep -rn "service_status" tests/scenario/ --include="*.py"

```
tests/scenario/test_charm.py:64:        context.output_state.get_container("tempo").service_status["tempo"]
tests/scenario/test_charm.py:97:        service_status={
<exited with exit code 0>
```


---

<sub>⏱️ 8m 54s</sub>

### ✅ `bash`

**Test Container services and State.get_container**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && python3 -c "
# Check if 'services' property was renamed too
from scenario import Container, State
import ops.pebble as pebble

# Let's try to access plan-computed services
c = Container('test', can_connect=True, layers={'l': pebble.Layer({'services': {'svc': {'startup': 'enabled'}}})})
try:
    print('services:', c.services)
except AttributeError as e:
    print('no .services:', e)
# The old State.get_container method - still available?
s = State(containers=[c])
print('get_container:', s.get_container('test'))
" 2>&1

```
services: {'svc': ServiceInfo(name='svc', startup=ServiceStartup.ENABLED, current=ServiceStatus.INACTIVE)}
get_container: Container(name='test', can_connect=True, _base_plan={}, layers={'l': Layer({'services': {'svc': {'startup': 'enabled'}}})}, service_statuses={}, mounts={}, execs=frozenset(), notices=[], check_infos=frozenset())
<exited with exit code 0>
```


---

<sub>⏱️ 9m 16s</sub>

### ✅ `bash`

**Check State.get_relations signature**

$ python3 -c "
from scenario import State, Relation
s = State(relations=[Relation('tracing')])
print('get_relations:', hasattr(s, 'get_relations'))
print('get_relation:', hasattr(s, 'get_relation'))
# check get_relation signature
import inspect
print('get_relations sig:', inspect.signature(s.get_relations))
try:
    r = Relation('tracing')
    print('get_relation by id:', hasattr(s, 'get_relation'))
    sig2 = inspect.signature(s.get_relation)
    print('get_relation sig:', sig2)
except Exception as e:
    print('error:', e)
" 2>&1

<details>
<summary>6 lines</summary>

```
get_relations: True
get_relation: True
get_relations sig: (endpoint: 'str') -> 'tuple[RelationBase, ...]'
get_relation by id: True
get_relation sig: (relation: 'int | RelationBase', /) -> 'RelationBase'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 39s</sub>

### ✅ `bash`

**Read charm_scaling and tracing_provider tests**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat tests/scenario/test_charm_scaling.py && echo "===" && cat tests/scenario/test_tracing_provider.py | head -60

<details>
<summary>114 lines</summary>

```
from unittest.mock import patch

import ops
import pytest
from scenario import Container, PeerRelation, Relation, State


def test_monolithic_status_no_s3(context):
    state_out = context.run(
        "start", State(unit_status=ops.ActiveStatus(), containers=[Container("tempo")])
    )
    assert state_out.unit_status.name == "waiting"


def test_scaled_status_no_s3(context):
    state_out = context.run(
        "start",
        State(
            relations=[PeerRelation("tempo-peers", peers_data={1: {}, 2: {}})],
            unit_status=ops.ActiveStatus(),
            containers=[Container("tempo")],
        ),
    )
    assert state_out.unit_status.name == "blocked"


def test_scaled_status_with_s3(context):
    state_out = context.run(
        "start",
        State(
            relations=[
                PeerRelation("tempo-peers", peers_data={1: {}, 2: {}}),
                Relation(
                    "s3",
                    remote_app_data={
                        "access-key": "key",
                        "bucket": "tempo",
                        "endpoint": "http://1.2.3.4:9000",
                        "secret-key": "soverysecret",
                    },
                    local_unit_data={"bucket": "tempo"},
                ),
            ],
            unit_status=ops.ActiveStatus(),
            containers=[Container("tempo")],
        ),
    )
    assert state_out.unit_status.name == "waiting"


@pytest.mark.parametrize("leader", (True, False))
@patch("tempo.Tempo.is_ready", new=lambda _: True)
def test_scaled_status_with_s3_and_container_ready(context, leader):
    container = Container(
        name="tempo",
        can_connect=True,
    )
    state_out = context.run(
        container.pebble_ready_event,
        State(
            leader=leader,
            relations=[
                PeerRelation("tempo-peers", peers_data={1: {}, 2: {}}),
                Relation(
                    "s3",
                    remote_app_data={
                        "access-key": "key",
                        "bucket": "tempo",
                        "endpoint": "http://1.2.3.4:9000",
                        "secret-key": "soverysecret",
                    },
                    local_unit_data={"bucket": "tempo"},
                ),
            ],
            unit_status=ops.ActiveStatus(),
            containers=[container],
        ),
    )
    assert state_out.unit_status.name == "active"
    assert state_out.get_container("tempo").services["tempo"].is_running()
===
import pytest
from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
from charms.tempo_k8s.v2.tracing import ProtocolType, TracingProviderAppData
from scenario import Container, Context, Relation, State


@pytest.fixture
def context(tempo_charm):
    return Context(
        charm_type=tempo_charm,
    )


def test_receivers_removed_on_relation_broken(context):
    tracing_grpc = Relation(
        "tracing",
        remote_app_data={"receivers": '["otlp_grpc"]'},
        local_app_data={
            "receivers": '[{"protocol": {"name": "otlp_grpc", "type": "grpc"} , "url": "foo.com:10"}, '
            '{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://foo.com:11"}, '
        },
    )
    tracing_http = Relation(
        "tracing",
        remote_app_data={"receivers": '["otlp_http"]'},
        local_app_data={
            "receivers": '[{"protocol": {"name": "otlp_grpc", "type": "grpc"} , "url": "foo.com:10"}, '
            '{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://foo.com:11"}, '
        },
    )

    state = State(
        leader=True,
        relations=[tracing_grpc, tracing_http],
        containers=[Container("tempo", can_connect=False)],
    )

    with charm_tracing_disabled():
        with context.manager(tracing_grpc.broken_event, state) as mgr:
            charm = mgr.charm
            assert charm._requested_receivers() == ("otlp_http",)

    state_out = mgr.output
    r_out = [r for r in state_out.relations if r.relation_id == tracing_http.relation_id][0]
    # "otlp_grpc" is gone from the databag
    assert [r.protocol for r in TracingProviderAppData.load(r_out.local_app_data).receivers] == [
        ProtocolType(name="otlp_http", type="http")
    ]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 47s</sub>

### ✅ `bash`

**Check container.pebble_ready_event replacement**

$ python3 -c "
from scenario import Container, Context
from ops import CharmBase

# Check container attributes
c = Container('tempo', can_connect=True)
print([x for x in dir(c) if not x.startswith('_')])
# Check how to get pebble_ready event
ctx = Context(CharmBase, meta={'name': 'test', 'containers': {'tempo': {}}})
print('pebble_ready:', ctx.on.pebble_ready)
import inspect
print('sig:', inspect.signature(ctx.on.pebble_ready))
"

```
['can_connect', 'check_infos', 'execs', 'get_check_info', 'get_filesystem', 'layers', 'mounts', 'name', 'notices', 'plan', 'service_statuses', 'services']
pebble_ready: <function CharmEvents.pebble_ready at 0x70983ee20220>
sig: (container: 'Container')
<exited with exit code 0>
```


---

<sub>⏱️ 9m 54s</sub>

### ✅ `bash`

**Check context.manager availability**

$ python3 -c "
from scenario import Context
from ops import CharmBase
ctx = Context(CharmBase, meta={'name': 'test'})
# Try context.manager
try:
    m = ctx.manager('start', None)
    print('context.manager works')
except AttributeError as e:
    print('context.manager gone:', e)
except TypeError as e:
    print('context.manager TypeError:', e)
" 2>&1

```
context.manager gone: 'Context' object has no attribute 'manager'
<exited with exit code 0>
```


---

<sub>⏱️ 10m 0s</sub>

### ✅ `bash`

**Read full test_tracing_requirer.py**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && cat tests/scenario/test_tracing_requirer.py

<details>
<summary>165 lines</summary>

```
import socket

import pytest
from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
from charms.tempo_k8s.v2.tracing import (
    EndpointChangedEvent,
    EndpointRemovedEvent,
    ProtocolNotRequestedError,
    TracingEndpointRequirer,
)
from ops import CharmBase, Framework, RelationBrokenEvent, RelationChangedEvent
from scenario import Context, Relation, State

from tempo import Tempo


class MyCharm(CharmBase):
    def __init__(self, framework: Framework):
        super().__init__(framework)
        self.tracing = TracingEndpointRequirer(self, protocols=["otlp_grpc"])
        framework.observe(self.tracing.on.endpoint_changed, self._on_endpoint_changed)

    def _on_endpoint_changed(self, e):
        pass


@pytest.fixture
def context():
    return Context(
        charm_type=MyCharm,
        meta={"name": "jolly", "requires": {"tracing": {"interface": "tracing", "limit": 1}}},
    )


def test_requirer_api(context):
    host = socket.getfqdn()
    tracing = Relation(
        "tracing",
        remote_app_data={
            "receivers": f'[{{"protocol": {{"name": "otlp_grpc", "type": "grpc"}}, "url": "{host}:4317"}}, '
            f'{{"protocol": {{"name": "otlp_http", "type": "http"}}, "url": "http://{host}:4318"}}, '
            f'{{"protocol": {{"name": "zipkin", "type": "http"}}, "url": "http://{host}:9411" }}]',
        },
    )
    state = State(leader=True, relations=[tracing])

    with charm_tracing_disabled():
        with context.manager(tracing.changed_event, state) as mgr:
            charm = mgr.charm
            assert charm.tracing.get_endpoint("otlp_grpc") == f"{host}:4317"
            assert charm.tracing.get_endpoint("otlp_http") == f"http://{host}:4318"
            assert charm.tracing.get_endpoint("zipkin") == f"http://{host}:9411"

            rel = charm.model.get_relation("tracing")
            assert charm.tracing.is_ready(rel)

    rchanged, epchanged = context.emitted_events
    assert isinstance(epchanged, EndpointChangedEvent)
    assert epchanged.receivers[0].protocol.name == "otlp_grpc"
    assert epchanged.receivers[1].protocol.name == "otlp_http"
    assert epchanged.receivers[2].protocol.name == "zipkin"


def test_requirer_api_with_internal_scheme(context):
    host = socket.getfqdn()
    tracing = Relation(
        "tracing",
        remote_app_data={
            "receivers": f'[{{"protocol": {{"name": "otlp_grpc", "type": "grpc"}} , "url": "{host}:4317"}}, '
            f'{{"protocol": {{"name": "otlp_http", "type": "http"}}, "url": "https://{host}:4318"}}, '
            f'{{"protocol": {{"name": "zipkin", "type": "http"}}, "url":  "https://{host}:9411"}}]',
        },
    )
    state = State(leader=True, relations=[tracing])

    with charm_tracing_disabled():
        with context.manager(tracing.changed_event, state) as mgr:
            charm = mgr.charm
            assert charm.tracing.get_endpoint("otlp_grpc") == f"{host}:4317"
            assert charm.tracing.get_endpoint("otlp_http") == f"https://{host}:4318"
            assert charm.tracing.get_endpoint("zipkin") == f"https://{host}:9411"

            rel = charm.model.get_relation("tracing")
            assert charm.tracing.is_ready(rel)

    rchanged, epchanged = context.emitted_events
    assert isinstance(epchanged, EndpointChangedEvent)
    assert epchanged.receivers[0].protocol.name == "otlp_grpc"


def test_ingressed_requirer_api(context):
    # WHEN external_url is present in remote app databag
    external_url = "http://1.2.3.4"
    tracing = Relation(
        "tracing",
        remote_app_data={
            "receivers": f'[{{"protocol": {{"name": "otlp_grpc", "type": "grpc"}}, "url": "{external_url.split("://")[1]}:4317" }}, '
            f'{{"protocol": {{"name": "otlp_http", "type": "http"}} , "url": "{external_url}:4318" }}, '
            f'{{"protocol": {{"name": "zipkin", "type": "http"}} , "url": "{external_url}:9411" }}]',
        },
    )
    state = State(leader=True, relations=[tracing])

    # THEN get_endpoint uses external URL instead of the host
    with charm_tracing_disabled():
        with context.manager(tracing.changed_event, state) as mgr:
            charm = mgr.charm
            assert (
                charm.tracing.get_endpoint("otlp_grpc")
                == f"{external_url.split('://')[1]}:{Tempo.receiver_ports['otlp_grpc']}"
            )
            for proto in ["otlp_http", "zipkin"]:
                assert (
                    charm.tracing.get_endpoint(proto)
                    == f"{external_url}:{Tempo.receiver_ports[proto]}"
                )

            rel = charm.model.get_relation("tracing")
            assert charm.tracing.is_ready(rel)

    rchanged, epchanged = context.emitted_events
    assert isinstance(epchanged, EndpointChangedEvent)
    assert epchanged.receivers[0].protocol.name == "otlp_grpc"


@pytest.mark.parametrize(
    "data",
    (
        {
            "ingesters": '[{"protocol": "otlp_grpc", "port": 9999}]',
            "bar": "baz",
        },
        {
            "host": "foo.com",
            "bar": "baz",
        },
        {
            "ingesters": '[{"burp": "barp", "port": 3200}]',
            "host": "foo.com",
        },
        {
            "ingesters": '[{"protocol": "tempo", "burp": "borp"}]',
            "host": "foo.com",
        },
    ),
)
def test_invalid_data(context, data):
    tracing = Relation(
        "tracing",
        remote_app_data=data,
    )
    state = State(leader=True, relations=[tracing])

    def post_event(charm: MyCharm):
        rel = charm.model.get_relation("tracing")
        assert not charm.tracing.is_ready(rel)

    with charm_tracing_disabled():
        context.run(tracing.changed_event, state, post_event=post_event)

    emitted_events = context.emitted_events
    assert len(emitted_events) == 2
    rchanged, rremoved = emitted_events
    assert isinstance(rchanged, RelationChangedEvent)
    assert isinstance(rremoved, EndpointRemovedEvent)


def test_broken(context):
    tracing = Relation("tracing")
    state = State(leader=True, relations=[tracing])

    with charm_tracing_disabled():
        context.run(tracing.broken_event, state)

    emitted_events = context.emitted_events
    assert len(emitted_events) == 2
    rchanged, ebroken = emitted_events
    assert isinstance(rchanged, RelationBrokenEvent)
    assert isinstance(ebroken, EndpointRemovedEvent)


def test_requested_not_yet_replied(context):
    tracing = Relation("tracing")
    state = State(leader=True, relations=[tracing])

    with charm_tracing_disabled():
        with context.manager(tracing.created_event, state) as mgr:
            charm = mgr.charm
            charm.tracing.request_protocols(["otlp_http"])
            charm.tracing.get_endpoint("otlp_http")


def test_not_requested_raises(context):
    tracing = Relation("tracing")
    state = State(leader=True, relations=[tracing])

    with charm_tracing_disabled():
        with context.manager(tracing.created_event, state) as mgr:
            charm = mgr.charm
            with pytest.raises(ProtocolNotRequestedError):
                charm.tracing.get_endpoint("otlp_http")
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 28s</sub>

### 💬 Copilot

Now I have a complete picture. Let me create a branch and implement all the fixes:

---

<sub>⏱️ 10m 29s</sub>

### ✅ `bash`

**Create upgrade branch**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && git checkout -b upgrade-ops-3.7.0

```
Switched to a new branch 'upgrade-ops-3.7.0'
<exited with exit code 0>
```


---

<sub>⏱️ 10m 29s</sub>

### ✅ `sql`

**Create upgrade todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create upgrade todos",
  "query": "INSERT INTO todos (id, title, description) VALUES\n('tox-ini', 'Update tox.ini ops-scenario pin and pytest pin', 'Change ops-scenario>=4.0.3,<7.0.0 to ops-scenario (no upper bound). Remove pytest<8.2.0 pin.'),\n('test-charm', 'Fix tests/scenario/test_charm.py', 'Remove scenario.sequences import, _BoundNotice import; add dataclasses; delete test_builtin_sequences; fix string events; fix output_state; fix service_status->service_statuses; fix notice event with new API; remove SCENARIO_SKIP_CONSISTENCY_CHECKS'),\n('test-charm-tracing', 'Fix tests/scenario/test_charm_tracing.py', 'Fix UncaughtCharmError import (scenario.runtime->scenario.errors); fix all string events ctx.run(\"start\",...)->ctx.run(ctx.on.start(),...); fix ctx.manager->ctx()'),\n('test-charm-scaling', 'Fix tests/scenario/test_charm_scaling.py', 'Fix string events context.run(\"start\",...)->context.on.start(); fix container.pebble_ready_event->context.on.pebble_ready(container)'),\n('test-ingressed', 'Fix tests/scenario/test_ingressed_tracing.py', 'Fix state.replace()->dataclasses.replace(); fix getattr(tracing,\"created_event\")->context.on.relation_created(tracing); fix ingress.joined_event->context.on.relation_joined(ingress)'),\n('test-tls', 'Fix tests/scenario/test_tls.py', 'Fix state.replace()->dataclasses.replace(); fix tracing.changed_event->context.on.relation_changed(tracing)'),\n('test-legacy', 'Fix tests/scenario/test_tracing_legacy.py', 'Fix state.replace()->dataclasses.replace(); fix context.manager()->context(); fix getattr(tracing,event)->context.on.relation_X(tracing)'),\n('test-provider', 'Fix tests/scenario/test_tracing_provider.py', 'Fix context.manager()->context(); fix broken_event->context.on.relation_broken(); fix mgr.output->mgr.run() return value'),\n('test-requirer', 'Fix tests/scenario/test_tracing_requirer.py', 'Fix all context.manager()->context(); fix all relation events; fix post_event to context manager approach'),\n('test-multi-import', 'Fix tests/scenario/test_a_charm_tracer_multi_import_warning.py', 'Fix ctx.run(\"start\",...)->ctx.run(ctx.on.start(),...)'),\n('verify', 'Run tests and verify all pass', 'Run tox scenario and unit tests to verify changes work');"
}
```

</details>

```
11 row(s) inserted. Last inserted row ID: 11.
```


---

<sub>⏱️ 10m 36s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tox.ini.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tox.ini

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tox.ini updated with changes.
```


---

<sub>⏱️ 10m 41s</sub>

### ✅ `bash`

**Check remaining pytest pins in tox.ini**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && grep -n "pytest<8\|pytest<" tox.ini

```
50:    pytest<8.2.0 # https://github.com/pytest-dev/pytest/issues/12263
75:    pytest<8.2.0 # https://github.com/pytest-dev/pytest/issues/12263
89:    pytest<8.2.0 # https://github.com/pytest-dev/pytest/issues/12263
<exited with exit code 0>
```


---

<sub>⏱️ 10m 47s</sub>

### ✅ `bash`

**Remove all pytest version pins**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && sed -i 's/    pytest<8\.2\.0 # https:\/\/github\.com\/pytest-dev\/pytest\/issues\/12263/    pytest/g' tox.ini && grep "pytest" tox.ini

<details>
<summary>12 lines</summary>

```
pytest
        -m pytest  -v --tb native -s {posargs} {[vars]tst_path}unit
    pytest
        -m pytest  -v --tb native -s {posargs} {[vars]tst_path}scenario
    pytest
    pytest-operator
    pytest -v --tb native --log-cli-level=INFO {[vars]tst_path}integration -s {posargs}
    pytest
    pytest-interface-tester
    # git+https://github.com/canonical/pytest-interface-tester
    pytest -v --tb native --log-cli-level=INFO -s {posargs} {[vars]tst_path}interface
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 51s</sub>

### 💬 Copilot

Now let me fix all the test files. Starting with the most complex one:

---

<sub>⏱️ 10m 51s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py

<details>
<summary>205 lines</summary>

```
1. from pathlib import Path
2. from unittest.mock import MagicMock
3. 
4. import pytest
5. import yaml
6. from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
7. from charms.tempo_k8s.v2.tracing import TracingRequirerAppData
8. from ops import pebble
9. from scenario import Container, Mount, Relation, State
10. from scenario.sequences import check_builtin_sequences
11. from scenario.state import Notice, _BoundNotice
12. 
13. from tempo import Tempo
14. from tests.scenario.helpers import get_tempo_config
15. 
16. TEMPO_CHARM_ROOT = Path(__file__).parent.parent.parent
17. 
18. 
19. @pytest.fixture(params=(True, False))
20. def base_state(request):
21.     return State(
22.         leader=request.param,
23.         containers=[Container("tempo", can_connect=True)],
24.     )
25. 
26. 
27. def test_builtin_sequences(tempo_charm, base_state):
28.     with charm_tracing_disabled():
29.         check_builtin_sequences(tempo_charm, template_state=base_state)
30. 
31. 
32. def test_start(context, base_state):
33.     # verify the charm runs at all with and without leadership
34.     with charm_tracing_disabled():
35.         context.run("start", base_state)
36. 
37. 
38. @pytest.mark.parametrize("requested_protocol", ("otlp_grpc", "zipkin"))
39. def test_tempo_restart_on_ingress_v2_changed(context, tmp_path, requested_protocol):
40.     # GIVEN
41.     # an initial configuration with an otlp_http receiver
42.     container, tempo = _tempo_mock_with_initial_config(tmp_path)
43. 
44.     # the remote end requests an otlp_grpc endpoint
45.     ingress = Relation(
46.         "tracing",
47.         remote_app_data=TracingRequirerAppData(receivers=[requested_protocol]).dump(),
48.     )
49. 
50.     # WHEN
51.     # the charm receives an ingress(v2) relation-changed requesting an otlp_grpc receiver
52.     state = State(leader=True, containers=[tempo], relations=[ingress])
53.     context.run(ingress.changed_event, state)
54. 
55.     # THEN
56.     # Tempo pushes a new config to the container filesystem
57.     new_config = get_tempo_config(tempo, context)
58.     expected_config = Tempo(container).generate_config(
59.         ["otlp_http", requested_protocol],
60.     )
61.     assert new_config == expected_config
62.     # AND restarts the pebble service.
63.     assert (
64.         context.output_state.get_container("tempo").service_status["tempo"]
65.         is pebble.ServiceStatus.ACTIVE
66.     )
67. 
68. 
69. def _tempo_mock_with_initial_config(tmp_path, tempo_ready_svc_exists: bool = True):
70.     tempo_config = tmp_path / "tempo.yaml"
71.     container = MagicMock()
72.     container.can_connect = lambda: True
73.     # prevent tls_ready from reporting True
74.     container.exists = lambda path: (
75.         False if path in [Tempo.tls_cert_path, Tempo.tls_key_path, Tempo.tls_ca_path] else True
76.     )
77.     initial_config = Tempo(container).generate_config(["otlp_http"])
78.     tempo_config.write_text(yaml.safe_dump(initial_config))
79.     layer_raw = {
80.         "summary": "tempo layer",
81.         "description": "foo",
82.         "services": {
83.             "tempo": {"startup": "enabled"},
84.         },
85.     }
86.     if tempo_ready_svc_exists:
87.         layer_raw["services"]["tempo-ready"] = {"startup": "disabled"}
88. 
89.     tempo = Container(
90.         "tempo",
91.         can_connect=True,
92.         layers={
93.             "tempo": pebble.Layer(
94.                 layer_raw,
95.             ),
96.         },
97.         service_status={
98.             # we don't have a way to check if the service has been restarted: all that scenario does ATM is set it to
99.             # 'active'.
100.             # so as a way to check that it's been restarted, we must set it to inactive here.
101.             "tempo": pebble.ServiceStatus.INACTIVE,
102.         },
103.         mounts={
104.             "data": Mount("/etc/tempo/tempo.yaml", tempo_config),
105.         },
106.     )
107.     return container, tempo
108. 
109. 
110. def test_tempo_tracing_created_before_pebble_ready(context, tmp_path):
111.     # GIVEN there is no plan yet
112.     tempo = Container(
113.         "tempo",
114.         can_connect=True,
115.     )
116. 
117.     # WHEN
118.     # the charm receives a tracing-relation-created requesting an otlp_grpc receiver
119.     tracing = Relation(
120.         "tracing",
121.         remote_app_data={"receivers": '["otlp_http"]'},
122.         local_app_data={
123.             "receivers": '[{"protocol": {"name": "otlp_grpc", "type": "grpc"} , "url": "foo.com:10"}, '
124.             '{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://foo.com:11"}, ',
125.         },
126.     )
127.     state = State(leader=True, containers=[tempo], relations=[tracing])
128.     state_out = context.run(tracing.created_event, state)
129. 
130.     # THEN
131.     # tempo still has no services
132.     tempo_out = state_out.get_container("tempo")
133.     assert not tempo_out.services
134. 
135. 
136. def test_tracing_storage_is_configured_to_local_without_relation(context, tmp_path):
137.     # GIVEN tempo mock
138.     container, tempo = _tempo_mock_with_initial_config(tmp_path)
139. 
140.     # WHEN any event comes in
141.     state = State(leader=True, containers=[tempo], relations=[])
142.     context.run("update-status", state)
143. 
144.     # THEN tempo's config has a local storage configured
145.     config = get_tempo_config(tempo, context)
146.     expected_config = Tempo(container).generate_config(["otlp_http"])
147.     assert config == expected_config
148.     assert config["storage"]["trace"]["backend"] == "local"
149. 
150. 
151. @pytest.mark.parametrize(
152.     "relation_data",
153.     (
154.         {},
155.         {
156.             "access-key": "key",
157.             "bucket": "tempo",
158.             "endpoint": "http://1.2.3.4:9000",
159.             "secret-key": "soverysecret",
160.         },
161.     ),
162. )
163. def test_tracing_storage_is_configured_to_s3_if_s3_relation_filled(
164.     context,
165.     tmp_path,
166.     relation_data,
167. ):
168.     # GIVEN tempo mock
169.     container, tempo = _tempo_mock_with_initial_config(tmp_path)
170. 
171.     # WHEN a charm receives an s3 relation
172.     s3_relation = Relation(
173.         "s3",
174.         remote_app_data=relation_data,
175.         local_app_data={"bucket": "tempo"},
176.     )
177. 
178.     state = State(leader=True, containers=[tempo], relations=[s3_relation])
179.     context.run(s3_relation.changed_event, state)
180. 
181.     # THEN
182.     # Tempo's config contains the data from the relation
183.     new_config = get_tempo_config(tempo, context)
184.     expected_config = Tempo(container).generate_config(["otlp_http"], relation_data)
185.     assert new_config == expected_config
186. 
187. 
188. def test_ready_check_on_resume(context, tmp_path, caplog, monkeypatch):
189.     # GIVEN the charm has no tempo-ready service
190.     container, tempo = _tempo_mock_with_initial_config(tmp_path, tempo_ready_svc_exists=False)
191. 
192.     state = State(leader=True, containers=[tempo])
193. 
194.     # WHEN we receive a custom-notice event
195.     with caplog.at_level("DEBUG"):
196.         monkeypatch.setenv("SCENARIO_SKIP_CONSISTENCY_CHECKS", "1")
197.         # scenario doesn't play nice in this very edge case
198.         context.run(_BoundNotice(Notice(Tempo.tempo_ready_notice_key), tempo).event, state)
199.         monkeypatch.delenv("SCENARIO_SKIP_CONSISTENCY_CHECKS")
200. 
201.     # THEN we get a debug-log but the charm doesn't error
202.     assert "`tempo-ready` service cannot be stopped at this time (probably doesn't exist)." in {
203.         r.message for r in caplog.records
204.     }
205.
```

</details>


---

<sub>⏱️ 10m 59s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 11m 6s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 11m 14s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 11m 22s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 11m 27s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 11m 34s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 11m 38s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 11m 52s</sub>

### 💬 Copilot

Now fix the notice test - add notice to the container's notices list and use the new event API:

---

<sub>⏱️ 11m 52s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm.py updated with changes.
```


---

<sub>⏱️ 11m 57s</sub>

### 💬 Copilot

Now fix `test_charm_tracing.py`:

---

<sub>⏱️ 11m 57s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_tracing.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_tracing.py updated with changes.
```


---

<sub>⏱️ 12m 4s</sub>

### 💬 Copilot

Now fix all `ctx.run("start", ...)` and `ctx.run("update-status", ...)` in test_charm_tracing.py. Since there are many occurrences, let me do it with sed:

---

<sub>⏱️ 12m 5s</sub>

### ✅ `bash`

**Find all ctx.run and ctx.manager calls in test_charm_tracing.py**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && grep -n 'ctx\.run\|ctx\.manager' tests/scenario/test_charm_tracing.py

<details>
<summary>17 lines</summary>

```
60:        ctx.run("start", State())
101:        ctx.run("start", State())
129:        ctx.run("start", State())
156:        ctx.run("start", State())
203:        ctx.run("start", State())
229:        state = ctx.run("start", State())
278:        ctx.run("start", State())
332:        ctx.run("start", State())
389:    with ctx.manager("start", State(leader=leader, relations=[tracing])) as mgr:
412:    with ctx.manager("start", State(leader=leader, relations=[tracing])) as mgr:
440:        ctx.run("start", State(relations=relations, leader=leader))
469:        ctx.run("start", State())
530:        ctx.run("start", State())
559:        ctx.run("update-status", State())
593:        ctx.run("start", State())
648:        ctx.run("start", State())
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12m 12s</sub>

### ✅ `bash`

**Fix string event calls in test_charm_tracing.py**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && \
  sed -i \
    -e 's/ctx\.run("start", State())/ctx.run(ctx.on.start(), State())/g' \
    -e 's/ctx\.run("start", State(relations=relations, leader=leader))/ctx.run(ctx.on.start(), State(relations=relations, leader=leader))/g' \
    -e 's/ctx\.run("update-status", State())/ctx.run(ctx.on.update_status(), State())/g' \
    tests/scenario/test_charm_tracing.py && \
  grep -n 'ctx\.run\|ctx\.manager' tests/scenario/test_charm_tracing.py

<details>
<summary>17 lines</summary>

```
60:        ctx.run(ctx.on.start(), State())
101:        ctx.run(ctx.on.start(), State())
129:        ctx.run(ctx.on.start(), State())
156:        ctx.run(ctx.on.start(), State())
203:        ctx.run(ctx.on.start(), State())
229:        state = ctx.run(ctx.on.start(), State())
278:        ctx.run(ctx.on.start(), State())
332:        ctx.run(ctx.on.start(), State())
389:    with ctx.manager("start", State(leader=leader, relations=[tracing])) as mgr:
412:    with ctx.manager("start", State(leader=leader, relations=[tracing])) as mgr:
440:        ctx.run(ctx.on.start(), State(relations=relations, leader=leader))
469:        ctx.run(ctx.on.start(), State())
530:        ctx.run(ctx.on.start(), State())
559:        ctx.run(ctx.on.update_status(), State())
593:        ctx.run(ctx.on.start(), State())
648:        ctx.run(ctx.on.start(), State())
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12m 18s</sub>

### 💬 Copilot

Now fix `ctx.manager(...)` calls:

---

<sub>⏱️ 12m 18s</sub>

### ✅ `bash`

**Fix ctx.manager calls in test_charm_tracing.py**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && sed -i \
  's/with ctx\.manager("start", State(leader=leader, relations=\[tracing\])) as mgr:/with ctx(ctx.on.start(), State(leader=leader, relations=[tracing])) as mgr:/g' \
  tests/scenario/test_charm_tracing.py && \
grep -n 'ctx\.manager' tests/scenario/test_charm_tracing.py

```

<exited with exit code 1>
```


---

<sub>⏱️ 12m 24s</sub>

### ✅ `bash`

**Check remaining ctx.manager calls**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && grep -n 'ctx\.manager' tests/scenario/test_charm_tracing.py

```

<exited with exit code 1>
```


---

<sub>⏱️ 12m 30s</sub>

### ✅ `bash`

**Check manager calls in test_charm_tracing.py**

$ cd /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4 && grep -n 'manager' tests/scenario/test_charm_tracing.py

```

<exited with exit code 1>
```


---

<sub>⏱️ 12m 35s</sub>

### ✅ `bash`

**Check test_charm_tracing.py for manager**

$ grep -n 'manager' /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_tracing.py

```

<exited with exit code 1>
```


---

<sub>⏱️ 12m 41s</sub>

### ✅ `bash`

**Check grep result**

$ grep -c 'manager' /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_tracing.py; echo "exit: $?"

```
0
exit: 1
<exited with exit code 0>
```


---

<sub>⏱️ 12m 48s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_tracing.py (lines 385-420)

<details>
<summary>36 lines</summary>

```
385.                 )
386.             ],
387.         ).dump(),
388.     )
389.     with ctx(ctx.on.start(), State(leader=leader, relations=[tracing])) as mgr:
390.         # THEN you're good
391.         assert mgr.charm.tempo() == "http://foo.com:80"
392. 
393. 
394. @pytest.mark.parametrize("leader", (True, False))
395. def test_tracing_requirer_remote_charm_no_request_but_response(leader):
396.     # IF the leader did NOT request the endpoint to be activated
397.     MyRemoteCharm._request = False
398.     ctx = Context(MyRemoteCharm, meta=MyRemoteCharm.META)
399.     # WHEN you get any event AND the remote unit has already replied
400.     tracing = scenario.Relation(
401.         "tracing",
402.         # empty local app data
403.         remote_app_data=TracingProviderAppData(
404.             # but the remote end has sent the data you need
405.             receivers=[
406.                 Receiver(
407.                     url="http://foo.com:80", protocol=ProtocolType(name="otlp_http", type="http")
408.                 )
409.             ],
410.         ).dump(),
411.     )
412.     with ctx(ctx.on.start(), State(leader=leader, relations=[tracing])) as mgr:
413.         # THEN you're lucky, but you're good
414.         assert mgr.charm.tempo() == "http://foo.com:80"
415. 
416. 
417. @pytest.mark.parametrize("relation", (True, False))
418. @pytest.mark.parametrize("leader", (True, False))
419. def test_tracing_requirer_remote_charm_no_request_no_response(leader, relation):
420.     """Verify that the charm errors out (even with charm_tracing disabled) if the tempo() call raises."""
```

</details>


---

<sub>⏱️ 12m 52s</sub>

### 💬 Copilot

Good. Now fix `test_charm_scaling.py`:

---

<sub>⏱️ 12m 52s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_scaling.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_scaling.py

<details>
<summary>81 lines</summary>

```
1. from unittest.mock import patch
2. 
3. import ops
4. import pytest
5. from scenario import Container, PeerRelation, Relation, State
6. 
7. 
8. def test_monolithic_status_no_s3(context):
9.     state_out = context.run(
10.         "start", State(unit_status=ops.ActiveStatus(), containers=[Container("tempo")])
11.     )
12.     assert state_out.unit_status.name == "waiting"
13. 
14. 
15. def test_scaled_status_no_s3(context):
16.     state_out = context.run(
17.         "start",
18.         State(
19.             relations=[PeerRelation("tempo-peers", peers_data={1: {}, 2: {}})],
20.             unit_status=ops.ActiveStatus(),
21.             containers=[Container("tempo")],
22.         ),
23.     )
24.     assert state_out.unit_status.name == "blocked"
25. 
26. 
27. def test_scaled_status_with_s3(context):
28.     state_out = context.run(
29.         "start",
30.         State(
31.             relations=[
32.                 PeerRelation("tempo-peers", peers_data={1: {}, 2: {}}),
33.                 Relation(
34.                     "s3",
35.                     remote_app_data={
36.                         "access-key": "key",
37.                         "bucket": "tempo",
38.                         "endpoint": "http://1.2.3.4:9000",
39.                         "secret-key": "soverysecret",
40.                     },
41.                     local_unit_data={"bucket": "tempo"},
42.                 ),
43.             ],
44.             unit_status=ops.ActiveStatus(),
45.             containers=[Container("tempo")],
46.         ),
47.     )
48.     assert state_out.unit_status.name == "waiting"
49. 
50. 
51. @pytest.mark.parametrize("leader", (True, False))
52. @patch("tempo.Tempo.is_ready", new=lambda _: True)
53. def test_scaled_status_with_s3_and_container_ready(context, leader):
54.     container = Container(
55.         name="tempo",
56.         can_connect=True,
57.     )
58.     state_out = context.run(
59.         container.pebble_ready_event,
60.         State(
61.             leader=leader,
62.             relations=[
63.                 PeerRelation("tempo-peers", peers_data={1: {}, 2: {}}),
64.                 Relation(
65.                     "s3",
66.                     remote_app_data={
67.                         "access-key": "key",
68.                         "bucket": "tempo",
69.                         "endpoint": "http://1.2.3.4:9000",
70.                         "secret-key": "soverysecret",
71.                     },
72.                     local_unit_data={"bucket": "tempo"},
73.                 ),
74.             ],
75.             unit_status=ops.ActiveStatus(),
76.             containers=[container],
77.         ),
78.     )
79.     assert state_out.unit_status.name == "active"
80.     assert state_out.get_container("tempo").services["tempo"].is_running()
81.
```

</details>


---

<sub>⏱️ 13m 3s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_scaling.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_scaling.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_charm_scaling.py updated with changes.
```


---

<sub>⏱️ 13m 9s</sub>

### 💬 Copilot

Now fix `test_ingressed_tracing.py`:

---

<sub>⏱️ 13m 9s</sub>

### ❌ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py

```
No match found
```


---

<sub>⏱️ 13m 13s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py (lines 1-10)

<details>
<summary>10 lines</summary>

```
1. from unittest.mock import patch
2. 
3. import pytest
4. import yaml
5. from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
6. from scenario import Container, Relation, State
7. 
8. from tempo import Tempo
9. 
10.
```

</details>


---

<sub>⏱️ 13m 18s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py updated with changes.
```


---

<sub>⏱️ 13m 23s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py updated with changes.
```


---

<sub>⏱️ 13m 28s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py (lines 18-45)

<details>
<summary>28 lines</summary>

```
18.     # WHEN ingress is related with external_host
19.     tracing = Relation("tracing", remote_app_data={"receivers": "[]"})
20.     ingress = Relation("ingress", remote_app_data={"external_host": "1.2.3.4", "scheme": "http"})
21.     state = dataclasses.replace(base_state, relations=[tracing, ingress])
22. 
23.     with charm_tracing_disabled():
24.         out = context.run(getattr(tracing, "created_event"), state)
25. 
26.     # THEN external_url is present in tracing relation databag
27.     tracing_out = out.get_relations(tracing.endpoint)[0]
28.     assert tracing_out.local_app_data == {
29.         "receivers": '[{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://1.2.3.4:4318"}]',
30.     }
31. 
32. 
33. @patch("socket.getfqdn", lambda: "1.2.3.4")
34. def test_ingress_relation_set_with_dynamic_config(context, base_state):
35.     # WHEN ingress is related with external_host
36.     ingress = Relation("ingress", remote_app_data={"external_host": "1.2.3.4", "scheme": "http"})
37.     state = base_state.replace(relations=[ingress])
38. 
39.     with patch.object(Tempo, "is_ready", lambda _: False):
40.         out = context.run(ingress.joined_event, state)
41. 
42.     expected_rel_data = {
43.         "http": {
44.             "routers": {
45.                 f"juju-{state.model.name}-tempo-k8s-jaeger-thrift-http": {
```

</details>


---

<sub>⏱️ 13m 33s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py updated with changes.
```


---

<sub>⏱️ 13m 39s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_ingressed_tracing.py updated with changes.
```


---

<sub>⏱️ 13m 44s</sub>

### 💬 Copilot

Now fix `test_tls.py`:

---

<sub>⏱️ 13m 44s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tls.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tls.py (lines 1-35)

<details>
<summary>35 lines</summary>

```
1. import socket
2. from unittest.mock import patch
3. 
4. import pytest
5. from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
6. from charms.tempo_k8s.v2.tracing import TracingProviderAppData, TracingRequirerAppData
7. from scenario import Container, Relation, State
8. 
9. from charm import Tempo
10. 
11. 
12. @pytest.fixture
13. def base_state():
14.     return State(leader=True, containers=[Container("tempo", can_connect=False)])
15. 
16. 
17. def update_relations_tls_and_verify(
18.     base_state,
19.     context,
20.     has_ingress,
21.     local_has_tls,
22.     local_scheme,
23.     relations,
24.     remote_scheme,
25.     tracing,
26. ):
27.     state = base_state.replace(relations=relations)
28.     with charm_tracing_disabled(), patch.object(Tempo, "tls_ready", local_has_tls):
29.         out = context.run(tracing.changed_event, state)
30.     tracing_provider_app_data = TracingProviderAppData.load(
31.         out.get_relations(tracing.endpoint)[0].local_app_data
32.     )
33.     actual_url = tracing_provider_app_data.receivers[0].url
34.     expected_url = f"{remote_scheme if has_ingress else local_scheme}://{socket.getfqdn() if not has_ingress else 'foo.com.org'}:4318"
35.     assert actual_url == expected_url
```

</details>


---

<sub>⏱️ 13m 49s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tls.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tls.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tls.py updated with changes.
```


---

<sub>⏱️ 13m 54s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tls.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tls.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tls.py updated with changes.
```


---

<sub>⏱️ 14m 0s</sub>

### 💬 Copilot

Now fix `test_tracing_legacy.py`:

---

<sub>⏱️ 14m 0s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_legacy.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_legacy.py

<details>
<summary>27 lines</summary>

```
1. import socket
2. 
3. import pytest
4. from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
5. from scenario import Container, Relation, State
6. 
7. 
8. @pytest.fixture
9. def base_state():
10.     return State(leader=True, containers=[Container("tempo", can_connect=False)])
11. 
12. 
13. @pytest.mark.parametrize("evt_name", ("changed", "created", "joined"))
14. def test_tracing_v2_endpoint_published(context, evt_name, base_state):
15.     tracing = Relation("tracing", remote_app_data={"receivers": "[]"})
16.     state = base_state.replace(relations=[tracing])
17. 
18.     with charm_tracing_disabled():
19.         with context.manager(getattr(tracing, f"{evt_name}_event"), state) as mgr:
20.             assert len(mgr.charm._requested_receivers()) == 1
21.             out = mgr.run()
22. 
23.     tracing_out = out.get_relations(tracing.endpoint)[0]
24.     assert tracing_out.local_app_data == {
25.         "receivers": f'[{{"protocol": {{"name": "otlp_http", "type": "http"}}, "url": "http://{socket.getfqdn()}:4318"}}]',
26.     }
27.
```

</details>


---

<sub>⏱️ 14m 9s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_legacy.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_legacy.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_legacy.py updated with changes.
```


---

<sub>⏱️ 14m 13s</sub>

### 💬 Copilot

Now fix `test_tracing_provider.py`:

---

<sub>⏱️ 14m 13s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_provider.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_provider.py

<details>
<summary>49 lines</summary>

```
1. import pytest
2. from charms.tempo_k8s.v1.charm_tracing import charm_tracing_disabled
3. from charms.tempo_k8s.v2.tracing import ProtocolType, TracingProviderAppData
4. from scenario import Container, Context, Relation, State
5. 
6. 
7. @pytest.fixture
8. def context(tempo_charm):
9.     return Context(
10.         charm_type=tempo_charm,
11.     )
12. 
13. 
14. def test_receivers_removed_on_relation_broken(context):
15.     tracing_grpc = Relation(
16.         "tracing",
17.         remote_app_data={"receivers": '["otlp_grpc"]'},
18.         local_app_data={
19.             "receivers": '[{"protocol": {"name": "otlp_grpc", "type": "grpc"} , "url": "foo.com:10"}, '
20.             '{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://foo.com:11"}, '
21.         },
22.     )
23.     tracing_http = Relation(
24.         "tracing",
25.         remote_app_data={"receivers": '["otlp_http"]'},
26.         local_app_data={
27.             "receivers": '[{"protocol": {"name": "otlp_grpc", "type": "grpc"} , "url": "foo.com:10"}, '
28.             '{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://foo.com:11"}, '
29.         },
30.     )
31. 
32.     state = State(
33.         leader=True,
34.         relations=[tracing_grpc, tracing_http],
35.         containers=[Container("tempo", can_connect=False)],
36.     )
37. 
38.     with charm_tracing_disabled():
39.         with context.manager(tracing_grpc.broken_event, state) as mgr:
40.             charm = mgr.charm
41.             assert charm._requested_receivers() == ("otlp_http",)
42. 
43.     state_out = mgr.output
44.     r_out = [r for r in state_out.relations if r.relation_id == tracing_http.relation_id][0]
45.     # "otlp_grpc" is gone from the databag
46.     assert [r.protocol for r in TracingProviderAppData.load(r_out.local_app_data).receivers] == [
47.         ProtocolType(name="otlp_http", type="http")
48.     ]
49.
```

</details>


---

<sub>⏱️ 14m 20s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_provider.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_provider.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_provider.py updated with changes.
```


---

<sub>⏱️ 14m 28s</sub>

### 💬 Copilot

Now fix `test_tracing_requirer.py` - the most complex one:

---

<sub>⏱️ 14m 28s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_requirer.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_requirer.py updated with changes.
```


---

<sub>⏱️ 14m 32s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_requirer.py (lines 68-130)

<details>
<summary>63 lines</summary>

```
68.         remote_app_data={
69.             "receivers": f'[{{"protocol": {{"name": "otlp_grpc", "type": "grpc"}} , "url": "{host}:4317"}}, '
70.             f'{{"protocol": {{"name": "otlp_http", "type": "http"}}, "url": "https://{host}:4318"}}, '
71.             f'{{"protocol": {{"name": "zipkin", "type": "http"}}, "url":  "https://{host}:9411"}}]',
72.         },
73.     )
74.     state = State(leader=True, relations=[tracing])
75. 
76.     with charm_tracing_disabled():
77.         with context.manager(tracing.changed_event, state) as mgr:
78.             charm = mgr.charm
79.             assert charm.tracing.get_endpoint("otlp_grpc") == f"{host}:4317"
80.             assert charm.tracing.get_endpoint("otlp_http") == f"https://{host}:4318"
81.             assert charm.tracing.get_endpoint("zipkin") == f"https://{host}:9411"
82. 
83.             rel = charm.model.get_relation("tracing")
84.             assert charm.tracing.is_ready(rel)
85. 
86.     rchanged, epchanged = context.emitted_events
87.     assert isinstance(epchanged, EndpointChangedEvent)
88.     assert epchanged.receivers[0].protocol.name == "otlp_grpc"
89. 
90. 
91. def test_ingressed_requirer_api(context):
92.     # WHEN external_url is present in remote app databag
93.     external_url = "http://1.2.3.4"
94.     tracing = Relation(
95.         "tracing",
96.         remote_app_data={
97.             "receivers": f'[{{"protocol": {{"name": "otlp_grpc", "type": "grpc"}}, "url": "{external_url.split("://")[1]}:4317" }}, '
98.             f'{{"protocol": {{"name": "otlp_http", "type": "http"}} , "url": "{external_url}:4318" }}, '
99.             f'{{"protocol": {{"name": "zipkin", "type": "http"}} , "url": "{external_url}:9411" }}]',
100.         },
101.     )
102.     state = State(leader=True, relations=[tracing])
103. 
104.     # THEN get_endpoint uses external URL instead of the host
105.     with charm_tracing_disabled():
106.         with context.manager(tracing.changed_event, state) as mgr:
107.             charm = mgr.charm
108.             assert (
109.                 charm.tracing.get_endpoint("otlp_grpc")
110.                 == f"{external_url.split('://')[1]}:{Tempo.receiver_ports['otlp_grpc']}"
111.             )
112.             for proto in ["otlp_http", "zipkin"]:
113.                 assert (
114.                     charm.tracing.get_endpoint(proto)
115.                     == f"{external_url}:{Tempo.receiver_ports[proto]}"
116.                 )
117. 
118.             rel = charm.model.get_relation("tracing")
119.             assert charm.tracing.is_ready(rel)
120. 
121.     rchanged, epchanged = context.emitted_events
122.     assert isinstance(epchanged, EndpointChangedEvent)
123.     assert epchanged.receivers[0].protocol.name == "otlp_grpc"
124. 
125. 
126. @pytest.mark.parametrize(
127.     "data",
128.     (
129.         {
130.             "ingesters": '[{"protocol": "otlp_grpc", "port": 9999}]',
```

</details>


---

<sub>⏱️ 14m 44s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_requirer.py

```
File /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_requirer.py updated with changes.
```


---

<sub>⏱️ 14m 51s</sub>

### 💬 Copilot

Now fix the `test_invalid_data` test with `post_event` and `test_broken`, `test_requested_not_yet_replied`, `test_not_requested_raises`:

---

<sub>⏱️ 14m 51s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_requirer.py.**

/tmp/ops-upgrade-experiment/tempo-k8s-operator__all__C4/tests/scenario/test_tracing_requirer.py (lines 145-210)

<details>
<summary>58 lines</summary>

```
145.     ),
146. )
147. def test_invalid_data(context, data):
148.     tracing = Relation(
149.         "tracing",
150.         remote_app_data=data,
151.     )
152.     state = State(leader=True, relations=[tracing])
153. 
154.     def post_event(charm: MyCharm):
155.         rel = charm.model.get_relation("tracing")
156.         assert not charm.tracing.is_ready(rel)
157. 
158.     with charm_tracing_disabled():
159.         context.run(tracing.changed_event, state, post_event=post_event)
160. 
161.     emitted_events = context.emitted_events
162.     assert len(emitted_events) == 2
163.     rchanged, rremoved = emitted_events
164.     assert isinstance(rchanged, RelationChangedEvent)
165.     assert isinstance(rremoved, EndpointRemovedEvent)
166. 
167. 
168. def test_broken(context):
169.     tracing = Relation("tracing")
170.     state = State(leader=True, relations=[tracing])
171. 
172.     with charm_tracing_disabled():
173.         context.run(tracing.broken_event, state)
174. 
175.     emitted_events = context.emitted_events
176.     assert len(emitted_events) == 2
177.     rchanged, ebroken = emitted_events
178.     assert isinstance(rchanged, RelationBrokenEvent)
179.     assert isinstance(ebroken, EndpointRemovedEvent)
180. 
181. 
182. def test_requested_not_yet_replied(context):
183.     tracing = Relation("tracing")
184.     state = State(leader=True, relations=[tracing])
185. 
186.     with charm_tracing_disabled():
187.         with context.manager(tracing.created_event, state) as mgr:
188.             charm = mgr.charm
189.             charm.tracing.request_protocols(["otlp_http"])
190.             charm.tracing.get_endpoint("otlp_http")
191. 
192. 
193. def test_not_requested_raises(context):
194.     tracing = Relation("tracing")
195.     state = State(leader=True, relations=[tracing])
196. 
197.     with charm_tracing_disabled():
198.         with context.manager(tracing.created_event, state) as mgr:
199.             charm = mgr.charm
200.             with pytest.raises(ProtocolNotRequestedError):
201.                 charm.tracing.get_endpoint("otlp_http")
202.
```

</details>


---

<sub>⏱️ 14m 57s</sub>

### ℹ️ Info

Operation cancelled by user

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
