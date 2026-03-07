# 🤖 Copilot CLI Session

> **Session ID:** `c819af2b-cbd3-4765-b2b8-be714ead93ab`
> **Started:** 3/7/2026, 11:51:14 AM
> **Duration:** 3m 36s
> **Exported:** 3/7/2026, 11:54:51 AM

<sub>⏱️ 4s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

---

<sub>⏱️ 10s</sub>

### 💬 Copilot





---

<sub>⏱️ 10s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-opus**

/tmp/saml-integrator-L1-opus

<details>
<summary>28 lines</summary>

```
.git
.github
.gitignore
.jujuignore
.licenserc.yaml
.vale
.vale.ini
.woke.yaml
CHANGELOG.md
CODEOWNERS
CONTRIBUTING.md
LICENSE
Makefile
Makefile.docs
README.md
SECURITY.md
charmcraft.yaml
config.yaml
docs
lib
metadata.yaml
pyproject.toml
renovate.json
src
terraform
tests
tox.toml
uv.lock
```

</details>


---

<sub>⏱️ 10s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-opus/tests**

/tmp/saml-integrator-L1-opus/tests

```
__init__.py
conftest.py
integration
interface
unit
```


---

<sub>⏱️ 10s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-opus/tox.toml**

/tmp/saml-integrator-L1-opus/tox.toml

<details>
<summary>167 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. skipsdist = true
5. skip_missing_interpreters = true
6. envlist = [ "lint", "unit", "static", "interface", "coverage-report" ]
7. requires = [ "tox>=4.21" ]
8. no_package = true
9. 
10. [env_run_base]
11. passenv = [ "PYTHONPATH", "CHARM_BUILD_DIR", "MODEL_SETTINGS" ]
12. runner = "uv-venv-lock-runner"
13. 
14. [env_run_base.setenv]
15. PYTHONPATH = "{toxinidir}:{toxinidir}/lib:{[vars]src_path}"
16. PYTHONBREAKPOINT = "ipdb.set_trace"
17. PY_COLORS = "1"
18. 
19. [env.fmt]
20. description = "Apply coding style standards to code"
21. commands = [
22.   [
23.     "ruff",
24.     "check",
25.     "--fix",
26.     "--select",
27.     "I",
28.     { replace = "ref", of = [
29.       "vars",
30.       "all_path",
31.     ], extend = true },
32.   ],
33.   [
34.     "ruff",
35.     "format",
36.     { replace = "ref", of = [
37.       "vars",
38.       "all_path",
39.     ], extend = true },
40.   ],
41. ]
42. dependency_groups = [ "fmt" ]
43. 
44. [env.lint]
45. description = "Check code against coding style standards"
46. commands = [
47.   [
48.     "codespell",
49.     "{toxinidir}",
50.   ],
51.   [
52.     "ruff",
53.     "format",
54.     "--check",
55.     "--diff",
56.     { replace = "ref", of = [
57.       "vars",
58.       "all_path",
59.     ], extend = true },
60.   ],
61.   [
62.     "ruff",
63.     "check",
64.     { replace = "ref", of = [
65.       "vars",
66.       "all_path",
67.     ], extend = true },
68.   ],
69.   [
70.     "mypy",
71.     { replace = "ref", of = [
72.       "vars",
73.       "all_path",
74.     ], extend = true },
75.   ],
76. ]
77. dependency_groups = [ "lint" ]
78. 
79. [env.unit]
80. description = "Run unit tests"
81. commands = [
82.   [
83.     "coverage",
84.     "run",
85.     "--source={[vars]src_path},{[vars]lib_path}",
86.     "-m",
87.     "pytest",
88.     "--ignore={[vars]tst_path}integration",
89.     "--ignore={[vars]tst_path}interface",
90.     "-v",
91.     "--tb",
92.     "native",
93.     "-s",
94.     { replace = "posargs", extend = "true" },
95.   ],
96.   [
97.     "coverage",
98.     "report",
99.   ],
100. ]
101. dependency_groups = [ "unit" ]
102. 
103. [env.coverage-report]
104. description = "Create test coverage report"
105. commands = [ [ "coverage", "report" ] ]
106. dependency_groups = [ "coverage-report" ]
107. 
108. [env.static]
109. description = "Run static analysis tests"
110. commands = [ [ "bandit", "-c", "{toxinidir}/pyproject.toml", "-r", "{[vars]src_path}", "{[vars]tst_path}" ] ]
111. dependency_groups = [ "static" ]
112. 
113. [env.interface]
114. description = "Run unit tests"
115. commands = [
116.   [
117.     "pytest",
118.     "-v",
119.     "--tb",
120.     "native",
121.     "{[vars]tst_path}/interface",
122.     "--log-cli-level=INFO",
123.     "-s",
124.     { replace = "posargs", extend = "true" },
125.   ],
126. ]
127. dependency_groups = [ "interface" ]
128. 
129. [env.integration]
130. description = "Run integration tests"
131. commands = [
132.   [
133.     "pytest",
134.     "-v",
135.     "--tb",
136.     "native",
137.     "--ignore={[vars]tst_path}unit",
138.     "--ignore={[vars]tst_path}interface",
139.     "--log-cli-level=INFO",
140.     "-s",
141.     { replace = "posargs", extend = "true" },
142.   ],
143. ]
144. dependency_groups = [ "integration" ]
145. 
146. [env.lint-fix]
147. description = "Apply coding style standards to code"
148. commands = [
149.   [
150.     "ruff",
151.     "check",
152.     "--fix",
153.     "--fix-only",
154.     { replace = "ref", of = [
155.       "vars",
156.       "all_path",
157.     ], extend = true },
158.   ],
159. ]
160. dependency_groups = [ "lint" ]
161. 
162. [vars]
163. src_path = "{toxinidir}/src/"
164. tst_path = "{toxinidir}/tests/"
165. lib_path = "{toxinidir}/lib/charms/saml_integrator"
166. all_path = [ "{toxinidir}/src/", "{toxinidir}/tests/", "{toxinidir}/lib/charms/saml_integrator" ]
167.
```

</details>


---

<sub>⏱️ 10s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-opus/pyproject.toml**

/tmp/saml-integrator-L1-opus/pyproject.toml

<details>
<summary>151 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. [project]
5. name = "saml-integrator-operator"
6. version = "0.0.0"
7. description = "SAML Integrator to abstract SAML IdP details."
8. readme = "README.md"
9. requires-python = ">=3.10"
10. classifiers = [
11.   "Programming Language :: Python :: 3 :: Only",
12.   "Programming Language :: Python :: 3.10",
13.   "Programming Language :: Python :: 3.11",
14.   "Programming Language :: Python :: 3.12",
15.   "Programming Language :: Python :: 3.13",
16.   "Programming Language :: Python :: 3.14",
17. ]
18. dependencies = [
19.   "lxml==6.0.2",
20.   "ops==3.6.0",
21.   "pydantic==2.12.5",
22.   "signxml==4.3.0",
23. ]
24. 
25. [dependency-groups]
26. fmt = [
27.   "ruff",
28. ]
29. lint = [
30.   "codespell",
31.   "mypy",
32.   "ops-scenario",
33.   "pep8-naming",
34.   "pytest",
35.   "pytest-asyncio",
36.   "pytest-operator",
37.   "requests",
38.   "ruff",
39.   "types-mock",
40.   "types-pyyaml",
41.   "types-requests",
42. ]
43. unit = [
44.   "coverage[toml]",
45.   "pytest",
46. ]
47. coverage-report = [
48.   "coverage[toml]",
49.   "pytest",
50. ]
51. static = [
52.   "bandit[toml]",
53. ]
54. interface = [
55.   "ops-scenario",
56.   "pytest",
57.   "pytest-interface-tester",
58. ]
59. integration = [
60.   "allure-pytest>=2.8.18",
61.   "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
62.   "juju",
63.   "pytest",
64.   "pytest-asyncio",
65.   "pytest-operator",
66. ]
67. 
68. [tool.uv]
69. package = false
70. 
71. [tool.ruff]
72. target-version = "py310"
73. line-length = 99
74. 
75. # enable ruff linters:
76. #   A flake8-builtins
77. #   B flake8-bugbear
78. # CPY flake8-copyright
79. #   D pydocstyle
80. # E/W pycodestyle
81. #   F Pyflakes
82. #   I isort
83. #   N pep8-naming
84. # RUF Ruff-specific rules
85. #   S flake8-bandit
86. # SIM flake8-simplify
87. #  TC flake8-type-checking
88. #  UP pyupgrade
89. lint.select = [ "A", "B", "C", "CPY", "D", "E", "F", "I", "N", "RUF", "S", "SIM", "TC", "UP", "W" ]
90. lint.ignore = [
91.   "B904",
92.   "D107",
93.   "D203",
94.   "D204",
95.   "D205",
96.   "D213",
97.   "D215",
98.   "D400",
99.   "D404",
100.   "D406",
101.   "D407",
102.   "D408",
103.   "D409",
104.   "D413",
105.   "E501",
106.   "S105",
107.   "S603",
108.   "TC002",
109.   "TC006",
110.   "UP006",
111.   "UP007",
112.   "UP035",
113.   "UP045",
114. ]
115. lint.per-file-ignores."tests/*" = [ "B011", "D100", "D101", "D102", "D103", "D104", "D212", "D415", "D417", "S" ]
116. lint.flake8-copyright.author = "Canonical Ltd."
117. lint.flake8-copyright.min-file-size = 1
118. lint.flake8-copyright.notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
119. lint.mccabe.max-complexity = 10
120. lint.pydocstyle.convention = "google"
121. 
122. [tool.codespell]
123. skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.coverage,htmlcov,uv.lock,grafana_dashboards"
124. 
125. [tool.pytest.ini_options]
126. minversion = "6.0"
127. log_cli_level = "INFO"
128. markers = [ "requires_secrets: mark tests that require external secrets" ]
129. pythonpath = [
130.   "lib",
131.   "src"
132. ]
133. 
134. [tool.coverage.run]
135. branch = true
136. 
137. [tool.coverage.report]
138. fail_under = 99
139. show_missing = true
140. 
141. [tool.mypy]
142. ignore_missing_imports = true
143. explicit_package_bases = true
144. namespace_packages = true
145. 
146. [tool.bandit]
147. exclude_dirs = [ "/venv/" ]
148. 
149. [tool.bandit.assert_used]
150. skips = [ "*/*test.py", "*/test_*.py", "*tests/*.py" ]
151.
```

</details>


---

<sub>⏱️ 15s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-opus/tests/integration**

/tmp/saml-integrator-L1-opus/tests/integration

```
__init__.py
any_charm.py
conftest.py
test_charm.py
```


---

<sub>⏱️ 15s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-opus/tests/conftest.py**

/tmp/saml-integrator-L1-opus/tests/conftest.py

<details>
<summary>16 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Test fixtures."""
5. 
6. import pytest
7. 
8. 
9. def pytest_addoption(parser: pytest.Parser):
10.     """Add test arguments.
11. 
12.     Args:
13.         parser: pytest parser.
14.     """
15.     parser.addoption("--charm-file", action="store")
16.
```

</details>


---

<sub>⏱️ 18s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-opus/tests/integration/conftest.py**

/tmp/saml-integrator-L1-opus/tests/integration/conftest.py

<details>
<summary>58 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Fixtures for the SAML Integrator charm integration tests."""
5. 
6. import json
7. from pathlib import Path
8. 
9. import pytest_asyncio
10. import yaml
11. from pytest import Config, fixture
12. from pytest_operator.plugin import OpsTest
13. 
14. 
15. @fixture(scope="module", name="app_name")
16. def app_name_fixture():
17.     """Provide app name from the metadata."""
18.     metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
19.     yield metadata["name"]
20. 
21. 
22. @pytest_asyncio.fixture(scope="module")
23. async def app(ops_test: OpsTest, pytestconfig: Config, app_name: str):
24.     """SAML Integrator charm used for integration testing.
25. 
26.     Build the charm and deploy it along with Anycharm.
27.     """
28.     charm = pytestconfig.getoption("--charm-file")
29.     assert ops_test.model
30.     application = await ops_test.model.deploy(
31.         f"./{charm}",
32.         application_name=app_name,
33.     )
34.     yield application
35. 
36. 
37. @pytest_asyncio.fixture(scope="module")
38. async def any_charm(ops_test: OpsTest):
39.     """SAML Integrator charm used for integration testing.
40. 
41.     Build the charm and deploy it along with Anycharm.
42.     """
43.     path_lib = "lib/charms/saml_integrator/v0/saml.py"
44.     saml_lib = Path(path_lib).read_text(encoding="utf8")
45.     any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
46.     src_overwrite = {
47.         "saml.py": saml_lib,
48.         "any_charm.py": any_charm_script,
49.     }
50.     assert ops_test.model
51.     application = await ops_test.model.deploy(
52.         "any-charm",
53.         application_name="any",
54.         channel="beta",
55.         config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
56.     )
57.     yield application
58.
```

</details>


---

<sub>⏱️ 18s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-opus/tests/integration/test_charm.py**

/tmp/saml-integrator-L1-opus/tests/integration/test_charm.py

<details>
<summary>52 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2025 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """SAML Integrator charm integration tests."""
6. 
7. import ops
8. import pytest
9. from pytest_operator.plugin import OpsTest
10. 
11. 
12. @pytest.mark.asyncio
13. @pytest.mark.abort_on_fail
14. async def test_active(ops_test: OpsTest, app: ops.Application):
15.     """Check that the charm is active.
16. 
17.     Assume that the charm has already been built and is running.
18.     """
19.     await app.set_config(  # type: ignore[attr-defined]
20.         {
21.             "entity_id": "https://login.staging.ubuntu.com",
22.             "fingerprint": "",
23.             "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
24.         }
25.     )
26.     status_name = ops.ActiveStatus.name  # type: ignore[has-type]
27.     assert ops_test.model
28.     await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
29.     assert app.units[0].workload_status == status_name  # type: ignore
30. 
31. 
32. @pytest.mark.asyncio
33. @pytest.mark.abort_on_fail
34. async def test_relation(ops_test: OpsTest, app: ops.Application, any_charm: ops.Application):
35.     """Check that the charm is active once related to another charm.
36. 
37.     Assume that the charm has already been built and is running.
38.     """
39.     relation_name = f"{app.name}:saml"
40.     assert ops_test.model
41.     await ops_test.model.add_relation(f"{any_charm.name}:require-saml", relation_name)
42.     await app.set_config(  # type: ignore[attr-defined]
43.         {
44.             "entity_id": "https://login.staging.ubuntu.com",
45.             "fingerprint": "",
46.             "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
47.         }
48.     )
49.     status_name = ops.ActiveStatus.name  # type: ignore[has-type]
50.     await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
51.     assert app.units[0].workload_status == status_name  # type: ignore
52.
```

</details>


---

<sub>⏱️ 18s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-opus/tests/integration/any_charm.py**

/tmp/saml-integrator-L1-opus/tests/integration/any_charm.py

<details>
<summary>29 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. # pylint: disable=import-error,consider-using-with,no-member
5. 
6. """This code snippet is used to be loaded into any-charm which is used for integration tests."""
7. 
8. from any_charm_base import AnyCharmBase
9. 
10. import saml
11. 
12. 
13. class AnyCharm(AnyCharmBase):  # pylint: disable=too-few-public-methods
14.     """Execute a simple charm workload to test the saml relation.
15. 
16.     Attrs:
17.         saml: The attribute that mimics a real SAML relation.
18.     """
19. 
20.     def __init__(self, *args, **kwargs):
21.         """Init function for the class.
22. 
23.         Args:
24.             args: Variable list of positional arguments passed to the parent constructor.
25.             kwargs: Variable list of positional keyword arguments passed to the parent constructor.
26.         """
27.         super().__init__(*args, **kwargs)
28.         self.saml = saml.SamlRequires(self)
29.
```

</details>


---

<sub>⏱️ 22s</sub>

### 💬 Copilot

Now let me research jubilant and pytest-jubilant to understand the API.

---

<sub>⏱️ 34s</sub>

### ✅ `web_search`

**jubilant juju pytest-jubilant Python library charm testing migration from pytest-operator**

<details>
<summary>Arguments</summary>

```json
{
  "query": "jubilant juju pytest-jubilant Python library charm testing migration from pytest-operator"
}
```

</details>

````
{"type":"text","text":{"value":"Here's a practical summary for migrating from `pytest-operator` to the new `jubilant` library (`pytest-jubilant`) in Python for Juju charm integration testing:\n\n---\n\n## Why Migrate?\n\nJubilant is Canonical’s new recommended library for charm integration tests. It provides a more stable, Pythonic API over the Juju CLI, avoids the websocket/asyncio issues with `python-libjuju`, and is actively maintained. It’s designed as a drop-in replacement for most uses of `pytest-operator` and is especially strong for modern charm workloads【3:1†source】【3:2†source】【3:0†source】.\n\n---\n\n## Migration Steps\n\n1. **Update your test dependencies**\n   - Add Jubilant to your `tox.ini` or `pyproject.toml`, and remove `juju` (`python-libjuju`), `pytest-operator`, and `pytest-asyncio`.\n   - Example (`tox.ini` diff):\n     ```\n     deps =\n         ...\n         jubilant~=1.0\n         pytest\n         - pytest-operator\n         - pytest-asyncio\n         ...\n     ```\n\n2. **Add fixtures to `conftest.py`**\n   - Jubilant does not provide built-in fixtures, so you should add your own.\n   - Example of a module-scoped fixture:\n     ```python\n     import jubilant\n     import pytest\n\n     @pytest.fixture(scope='module')\n     def juju(request: pytest.FixtureRequest):\n         keep_models = bool(request.config.getoption('--keep-models'))\n         with jubilant.temp_model(keep=keep_models) as juju:\n             juju.wait_timeout = 10 * 60\n             yield juju\n             if request.session.testsfailed:\n                 log = juju.debug_log(limit=1000)\n                 print(log, end='')\n\n     def pytest_addoption(parser):\n         parser.addoption('--keep-models', action='store_true', default=False,\n                          help='keep temporarily-created models')\n     ```\n\n3. **Update your tests**\n   - Replace your use of `ops_test` or other `pytest-operator`-provided fixtures with the new `juju` fixture.\n   - Example:\n     ```python\n     def test_active(juju: jubilant.Juju):\n         juju.deploy('mycharm')\n         juju.wait(jubilant.all_active)\n     ```\n   - For more advanced waiting:  \n     `juju.wait(lambda status: jubilant.all_active(status, 'mycharm'))`\n\n4. **Execute your tests**\n   - Run them as normal with `pytest`; if using tox, keep the configuration simple.\n\n---\n\n## Key Differences and Notes\n\n- **Jubilant calls the `juju` CLI using Python’s `subprocess`**, making it more robust to network issues and Juju upgrade changes. All operations are synchronous and simple to debug【3:4†source】.\n- **You no longer need to deal with asyncio**; the API is synchronous and blocking, which simplifies test writing.\n- **Debug output and log extraction**: Add helpers in your fixture (see above) to pull debug logs automatically on failure.\n- **Can run both frameworks side-by-side** during migration if needed, by having both fixtures available and migrating tests incrementally【3:0†source】.\n- **Documentation and code samples**: The Jubilant documentation is available online, and the library is open source and type-annotated for best IDE support【3:0†source】【3:2†source】.\n\n---\n\n## References and Further Reading\n\n- [Official migration guide: pytest-operator ➔ Jubilant](https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/)【3:0†source】\n- [Jubilant on PyPI](https://pypi.org/project/jubilant/)【3:1†source】\n- [Jubilant GitHub repository](https://github.com/canonical/jubilant)【3:2†source】\n- [How-to guides: Jubilant](https://canonical-jubilant.readthedocs-hosted.com/how-to/)【3:3†source】\n- [Deep technical dive: Jubilant vs python-libjuju](https://benhoyt.com/writings/jubilant/)【3:4†source】\n\n---\n\nIf you need further examples (e.g., secrets, SSH actions, complex deployments), the Jubilant docs and its GitHub repo provide additional recipes and an API reference. The transition should be relatively straightforward for most charm test suites.","annotations":[{"text":"【3:1†source】","start_index":531,"end_index":543,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:2†source】","start_index":543,"end_index":555,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:0†source】","start_index":555,"end_index":567,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:4†source】","start_index":2485,"end_index":2497,"url_citation":{"title":"Don’t fear Python subprocess or Go codegen","url":"https://benhoyt.com/writings/jubilant/"}},{"text":"【3:0†source】","start_index":2876,"end_index":2888,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:0†source】","start_index":3046,"end_index":3058,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:2†source】","start_index":3058,"end_index":3070,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:0†source】","start_index":3249,"end_index":3261,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:1†source】","start_index":3318,"end_index":3330,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:2†source】","start_index":3400,"end_index":3412,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:3†source】","start_index":3499,"end_index":3511,"url_citation":{"title":"How-to guides - Jubilant documentation","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/"}},{"text":"【3:4†source】","start_index":3603,"end_index":3615,"url_citation":{"title":"Don’t fear Python subprocess or Go codegen","url":"https://benhoyt.com/writings/jubilant/"}}]},"bing_searches":[{"text":"jubilant juju pytest-jubilant Python library charm testing migration from pytest-operator","url":"https://www.bing.com/search?q=jubilant+juju+pytest-jubilant+Python+library+charm+testing+migration+from+pytest-operator"}],"annotations":null}
````


---

<sub>⏱️ 38s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/",
  "max_length": 15000
}
```

</details>

<details>
<summary>236 lines</summary>

```
Contents of https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/:
Many charm integration tests use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) and [python-libjuju](https://github.com/juju/python-libjuju). This guide explains how to migrate your integration tests from those libraries to Jubilant.

To get help while you’re migrating tests, please keep the [API reference](../../reference/jubilant/) handy, and make use of your IDE’s autocompletion – Jubilant tries to provide good type annotations and docstrings.

Migrating your tests can be broken into three steps:

1.  Update your dependencies
    
2.  Add fixtures to `conftest.py`
    
3.  Update the tests themselves
    

Let’s look at each of these in turn.

## Update your dependencies[¶](#update-your-dependencies "Link to this heading")

The first thing you’ll need to do is add `jubilant` as a dependency to your `tox.ini` or `pyproject.toml` dependencies.

You can also remove the dependencies on `juju` (python-libjuju), `pytest-operator`, and `pytest-asyncio`.

If you’re using `tox.ini`, the diff might look like:

 \[testenv:integration\]
 deps =
     boto3
     cosl
\-    juju>=3.0
\+    jubilant~=1.0
     pytest
\-    pytest-operator
\-    pytest-asyncio
     -r{toxinidir}/requirements.txt

If you’re migrating a large number of tests, you may want to do it in stages. In that case, keep the old dependencies in place till the end, and migrate tests one at a time, so that both pytest-operator and Jubilant tests can run together.

## Add fixtures to `conftest.py`[¶](#add-fixtures-to-conftest-py "Link to this heading")

The pytest-operator library includes pytest fixtures, but Jubilant does not include any fixtures, so you’ll need to add one or two fixtures to your `conftest.py`.

### A `juju` model fixture[¶](#a-juju-model-fixture "Link to this heading")

Jubilant expects that a Juju controller has already been set up, either using [Concierge](https://github.com/jnsgruk/concierge) or a manual approach. However, you’ll want a fixture that creates a temporary model. We recommend naming the fixture `juju`:

\# tests/integration/conftest.py

import jubilant
import pytest

@pytest.fixture(scope\='module')
def juju(request: pytest.FixtureRequest):
    keep\_models \= bool(request.config.getoption('--keep-models'))

    with jubilant.temp\_model(keep\=keep\_models) as juju:
        juju.wait\_timeout \= 10 \* 60

        yield juju  \# run the test

        if request.session.testsfailed:
            log \= juju.debug\_log(limit\=1000)
            print(log, end\='')

def pytest\_addoption(parser):
    parser.addoption(
        '--keep-models',
        action\='store\_true',
        default\=False,
        help\='keep temporarily-created models',
    )

In your tests, use the fixture like this:

\# tests/integration/test\_charm.py

def test\_active(juju: jubilant.Juju):
    juju.deploy('mycharm')
    juju.wait(jubilant.all\_active)

    \# Or wait for just 'mycharm' to be active (ignoring other apps):
    juju.wait(lambda status: jubilant.all\_active(status, 'mycharm'))

A few things to note about the fixture:

*   It includes a command-line parameter `--keep-models`, to match pytest-operator. If the parameter is set, the fixture keeps the temporary model around after running the tests.
    
*   It sets [`juju.wait_timeout`](../../reference/jubilant/#jubilant.Juju.wait_timeout "jubilant.Juju.wait_timeout") to 10 minutes, to match python-libjuju’s default `wait_for_idle` timeout.
    
*   If any of the tests fail, it uses `juju.debug_log` to display the last 1000 lines of `juju debug-log` output.
    
*   It is module-scoped, like pytest-operator’s `ops_test` fixture. This means that a new model is created for every `test_*.py` file, but not for every test.
    

### An application fixture[¶](#an-application-fixture "Link to this heading")

If you don’t want to deploy your application in each test, you can add a module-scoped `app` fixture that deploys your charm and waits for it to go active.

The following fixture assumes that the charm has already been packed with `charmcraft pack` in a previous CI step (Jubilant has no equivalent of `ops_test.build_charm`):

\# tests/integration/conftest.py

import pathlib

import jubilant
import pytest

@pytest.fixture(scope\='module')
def app(juju: jubilant.Juju):
    juju.deploy(
        charm\_path('mycharm'),
        'mycharm',
        resources\={
            'mycharm-image': 'ghcr.io/canonical/...',
        },
        config\={
            'base\_url': '/api',
            'port': 80,
        },
        base\='ubuntu@20.04',
    )
    \# ... do any other application setup here ...
    juju.wait(jubilant.all\_active)

    yield 'mycharm'  \# run the test

def charm\_path(name: str) \-> pathlib.Path:
    """Return full absolute path to given test charm."""
    \# We're in tests/integration/conftest.py, so parent\*3 is repo top level.
    charm\_dir \= pathlib.Path(\_\_file\_\_).parent.parent.parent
    charms \= \[p.absolute() for p in charm\_dir.glob(f'{name}\_\*.charm')\]
    assert charms, f'{name}\_\*.charm not found'
    assert len(charms) \== 1, 'more than one .charm file, unsure which to use'
    return charms\[0\]

In your tests, you’ll need to specify that the test depends on both fixtures:

\# tests/integration/test\_charm.py

def test\_active(juju: jubilant.Juju, app: str):
    status \= juju.status()
    assert status.apps\[app\].is\_active

## Update the tests themselves[¶](#update-the-tests-themselves "Link to this heading")

Many features of pytest-operator and python-libjuju map quite directly to Jubilant, except without using `async`. Here is a summary of what you need to change:

*   Remove `async` and `await` keywords, and replace `pytest_asyncio.fixture` with `pytest.fixture`
    
*   Replace introspection of python-libjuju’s `Application` and `Unit` objects with [`juju.status`](../../reference/jubilant/#jubilant.Juju.status "jubilant.Juju.status")
    
*   Replace `model.wait_for_idle` with [`juju.wait`](../../reference/jubilant/#jubilant.Juju.wait "jubilant.Juju.wait") and an appropriate _ready_ callable
    
*   Replace `unit.run` with [`juju.exec`](../../reference/jubilant/#jubilant.Juju.exec "jubilant.Juju.exec"); note the different return type and error handling
    
*   Replace `unit.run_action` with [`juju.run`](../../reference/jubilant/#jubilant.Juju.run "jubilant.Juju.run"); note the different return type and error handling
    
*   Replace other python-libjuju methods with equivalent [`Juju`](../../reference/jubilant/#jubilant.Juju "jubilant.Juju") methods, which are normally much closer to the Juju CLI commands
    

Let’s look at some specifics in more detail.

### Deploying a charm[¶](#deploying-a-charm "Link to this heading")

To migrate a charm deployment from pytest-operator, drop the `await`, change `series` to `base`, and replace `model.wait_for_idle` with [`juju.wait`](../../reference/jubilant/#jubilant.Juju.wait "jubilant.Juju.wait"):

\# pytest-operator
postgres\_app \= await model.deploy(
    'postgresql-k8s',
    channel\='14/stable',
    series\='jammy',
    revision\=300,
    trust\=True,
    config\={'profile': 'testing'},
)
await model.wait\_for\_idle(apps\=\[postgres\_app.name\], status\='active')

\# jubilant
juju.deploy(
    'postgresql-k8s',
    channel\='14/stable',
    base\='ubuntu@22.04',
    revision\=300,
    trust\=True,
    config\={'profile': 'testing'},
)
juju.wait(lambda status: jubilant.all\_active(status, 'postgresql-k8s'))

### Fetching status[¶](#fetching-status "Link to this heading")

A python-libjuju model is updated in the background using websockets. In Jubilant you use ordinary Python function calls to fetch updates:

\# pytest-operator
async def test\_active(app: Application):
    assert app.units\[0\].workload\_status \== ActiveStatus.name

\# jubilant
def test\_active(juju: jubilant.Juju, app: str):
    status \= juju.status()
    assert status.apps\[app\].units\[app + '/0'\].is\_active

### Waiting for a condition[¶](#waiting-for-a-condition "Link to this heading")

However, instead of calling `status` directly, it’s usually better to wait for a certain condition to be true. In python-libjuju you used `model.wait_for_idle`; in Jubilant you use [`juju.wait`](../../reference/jubilant/#jubilant.Juju.wait "jubilant.Juju.wait"), which has a simpler and more consistent API.

The `wait` method takes a _ready_ callable, which takes a [`Status`](../../reference/jubilant/#jubilant.Status "jubilant.Status") object. Internally, `wait` polls `juju status` every second and calls the _ready_ callable, which must return `True` three times in a row (this is configurable).

You can optionally provide an _error_ callable, which also takes a `Status` object. If the _error_ callable returns `True`, `wait` raises a [`WaitError`](../../reference/jubilant/#jubilant.WaitError "jubilant.WaitError") immediately.

Jubilant provides helper functions to use for the _ready_ and _error_ callables, such as [`jubilant.all_active`](../../reference/jubilant/#jubilant.all_active "jubilant.all_active") and [`jubilant.any_error`](../../reference/jubilant/#jubilant.any_error "jubilant.any_error"). These check whether the workload status of all (or any) applications and their units are in a given state.

For example, here’s a simple `wait` call that waits for all applications and units to go “active” and raises an error if any go into “error”:

\# pytest-operator
async def test\_active(model: Model):
    await model.deploy('mycharm')
    await model.wait\_for\_idle(status\='active')  \# implies raise\_on\_error=True

\# jubilant
def test\_active(juju: jubilant.Juju):
    juju.deploy('mycharm')
    juju.wait(jubilant.all\_active, error\=jubilant.any\_error)

It’s usually best to wait on workload status with the `all_*` and `any_*` helpers. However, if you want to wait specifically for unit agent status to be idle, you can use [`jubilant.all_agents_idle`](../../reference/jubilant/#jubilant.all_agents_idle "jubilant.all_agents_idle"):

\# pytest-operator
async def test\_idle(model: Model):
    await model.deploy('mycharm')
    await model.wait\_for\_idle()

\# jubilant
def test\_active(juju: jubilant.Juju):
    juju.deploy('mycharm')
    juju.wait(jubilant.all\_agents\_idle)

It’s common to use a `lambda` function to customize the callable or compose multiple checks. For example, to wait specifically for `mysql` and `redis` to go active and `logger` to be blocked:

juju.wait(
    lambda status: (
        jubilant.all\_active(status, 'mysql', 'redis') and
        jubilant.all\_blocked(status, 'logger'),
    ),
)

The `wait` method also has other options (see [`juju.wait`](../../reference/jubilant/#jubilant.Juju.wait "jubilant.Juju.wait") for details):

juju.deploy('mycharm')
juju.wait(
    ready\=lambda status: jubilant.all\_active(status, 'mycharm'),
    error\=jubilant.any\_error,
    delay\=0.2,    \# poll "juju status" every 200ms (default 1s)
    timeout\=60,   \# set overall timeout to 60s (default juju.wait\_timeout)
    successes\=7,  \# require ready to return success 7x in a row (default 3)
)

For more examples, see [Tutorial | Use a custom wait condition](../../tutorial/getting-started/#use-a-custom-wait-condition).

### Integrating two applications[¶](#integrating-two-applications "Link to this heading")

To integrate two charms, remove the `async`\-related code and replace `model.add_relation` with [`juju.integrate`](../../reference/jubilant/#jubilant.Juju.integrate "jubilant.Juju.integrate"). For example, to integrate discourse-k8s with three other charms:

\# pytest-operator
await asyncio.gather(
    model.add\_relation('discourse-k8s', 'postgresql-k8s:database'),
    model.add\_relation('discourse-k8s', 'redis-k8s'),
    model.add\_relation('discourse-k8s', 'nginx-ingress-integrator'),
)
await model.wait\_for\_idle(status\='active')

\# jubilant
juju.integrate('discourse-k8s', 'postgresql-k8s:database')
juju.integrate('discourse-k8s', 'redis-k8s')
juju.integrate('discourse-k8s', 'nginx-ingress-integrator')
juju.wait(jubilant.all\_active)

### Executing a command[¶](#executing-a-command "Link to this heading")

In `pytest-operator` tests, you used `unit.run` to execute a command. With Jubilant (as with Juju 3.x) you use [`juju.exec`](../../reference/jubilant/#jubilant.Juju.exec "jubilant.Juju.exec"). Jubilant’s `exec` returns a [`jubilant.Task`](../../reference/jubilant/#jubilant.Task "jubilant.Task"), and it also checks errors for you:

\# pytest-operator
unit \= model.applications\['discourse-k8s'\].units\[0\]
action \= await unit.run('/bin/bash -c "..."')
await action.wait()
logger.info(action.results)
assert action.results\['return-code'\] \== 0, 'Enable plugins failed'

\# jubilant
task \= juju.exec('/bin/bash -c "..."', unit\='discourse-k8s/0')
logger.info(task.results)

### Running an action[¶](#running-an-action "Link to this heading")

In `pytest-operator` tests, you used `unit.run_action` to run an action. With Jubilant, you use [`juju.run`](../../reference/jubilant/#jubilant.Juju.run "jubilant.Juju.run"). Similar to `exec`, Jubilant’s `run` returns a [`jubilant.Task`](../../reference/jubilant/#jubilant.Task "jubilant.Task") and checks errors for you:

\# pytest-operator
app \= model.applications\['postgresl-k8s'\]
action \= await app.units\[0\].run\_action('get-password', username\='operator')
await action.wait()
password \= action.results\['password'\]

\# jubilant
task \= juju.run('postgresql-k8s/0', 'get-password', {'username': 'operator'})
password \= task.results\['password'\]

### The `cli` fallback[¶](#the-cli-fallback "Link to this heading")

Similar to how you could call `ops_test.juju`, with Jubilant you can call [`juju.cli`](../../reference/jubilant/#jubilant.Juju.cli "jubilant.Juju.cli") to execute an arbitrary Juju command. The `cli` method checks errors for you and raises a [`CLIError`](../../reference/jubilant/#jubilant.CLIError "jubilant.CLIError") if the command’s exit code is nonzero:

\# pytest-operator
return\_code, \_, scp\_err \= await ops\_test.juju(
    'scp',
    '--container',
    'postgresql',
    './testing\_database/testing\_database.sql',
    f'{postgres\_app.units\[0\].name}:.',
)
assert return\_code \== 0, scp\_err

\# jubilant
juju.cli(
    'scp',
    '--container',
    'postgresql',
    './testing\_database/testing\_database.sql',
    'postgresql-k8s/0:.',
)

### A `fast_forward` context manager[¶](#a-fast-forward-context-manager "Link to this heading")

Pytest-operator has a `fast_forward` context manager which temporarily speeds up `update-status` hooks to fire every 10 seconds (instead of Juju’s default of every 5 minutes). Jubilant doesn’t provide this context manager, as we don’t recommend it for new tests. If you need it for migrating existing tests, you can define it as:

@contextlib.contextmanager
def fast\_forward(juju: jubilant.Juju):
    """Context manager that temporarily speeds up update-status hooks to fire every 10s."""
    old \= juju.model\_config()\['update

<note>Content truncated. Call the fetch tool with a start_index of 15000 to get more content.</note>
```

</details>


---

<sub>⏱️ 48s</sub>

### ✅ `web_search`

**pytest-jubilant PyPI package juju charm testing fixtures conftest**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest-jubilant PyPI package juju charm testing fixtures conftest"
}
```

</details>

````
{"type":"text","text":{"value":"The pytest-jubilant PyPI package provides seamless integration between the Jubilant library (a modern, type-annotated Python wrapper for the Juju CLI focused on charm integration testing) and the pytest framework. The package is designed to make it easier to migrate from pytest-operator/pytest-asyncio to Jubilant for Juju charm testing and comes with convenient fixtures for use in your testing setup.\n\n### Key Points About pytest-jubilant and Fixtures\n\n- **pytest-jubilant**: This is a pytest plugin that integrates with Jubilant, providing fixtures and CLI options for Juju model management, making charm integration testing more convenient and robust compared to using python-libjuju or pytest-operator directly. It helps manage Juju models for tests, sets up and tears down temporary models as needed, and supports options like keeping models on failure for debugging purposes【3:6†source】.\n\n- **Jubilant**: The core library wraps the Juju CLI, providing a Pythonic interface to deploy, manage, and test charms, while avoiding some pain points of python-libjuju such as async complexity and websocket failures【3:0†source】【3:1†source】.\n\n### Example Fixture in `conftest.py`\n\nThe standard approach is to define a fixture (typically named `juju`) in `conftest.py` that manages the Juju model lifecycle for your tests. For example:\n\n```python\n# conftest.py\nimport pytest\nimport jubilant\n\n@pytest.fixture(scope='module')\ndef juju(request):\n    keep_models = bool(request.config.getoption('--keep-models'))\n    with jubilant.temp_model(keep=keep_models) as juju:\n        juju.wait_timeout = 10 * 60  # e.g., 10 minute wait timeout for model to settle\n        yield juju\n    if request.session.testsfailed:\n        log = juju.debug_log(limit=1000)\n        print(log, end='')\n        \ndef pytest_addoption(parser):\n    parser.addoption('--keep-models', action='store_true', default=False,\n                     help='keep temporarily-created models')\n```\n\nThen in your test files, you'd use:\n\n```python\ndef test_deploy(juju: jubilant.Juju):\n    juju.deploy('mycharm')\n    juju.wait(jubilant.all_active)\n```\n\n- The fixture uses `jubilant.temp_model()` to create and clean up models automatically.\n- The `--keep-models` CLI flag is supported for debugging.\n- If a test fails, it prints the Juju debug log for that model【3:2†source】【3:8†source】.\n\n### pytest-jubilant-specific Fixtures\n\npytest-jubilant provides:\n\n- `juju`: A module- and model-scoped fixture, using temporary models by default and supporting CLI flags like `--model`, `--keep-models`, and `--no-teardown` for model management. This is especially useful for integration tests that require a fresh model for isolation.\n- `temp_model_factory`: For advanced tests (like CMR and multiple models), lets you manage and access several models during your test session.\n\nExample (from pytest-jubilant docs):\n\n```python\nfrom jubilant import Juju, all_active\n\ndef test_deploy(juju: Juju):\n    juju.deploy(\"./foo.charm\", \"foo\")\n    juju.wait(lambda status: all_active(status, \"foo\"), timeout=1000)\n```\nOr for multiple models:\n\n```python\n@pytest.fixture\ndef istio(temp_model_factory):\n    yield temp_model_factory.get_juju(suffix=\"istio\")\n\ndef test_cmr(juju: Juju, istio: Juju):\n    # ... test logic ...\n```\nCLI options let you customize how models are reused or torn down, aiding debugging and CI integration【3:6†source】.\n\n---\n\n### Conclusion\n\n- **pytest-jubilant** is the recommended way to run integration tests for Juju charms using pytest.\n- You implement a `juju` fixture in `conftest.py` (or use the ones provided), and write tests that marshal charm deployments, relations, and assertions against Juju model/application state.\n- Migration from older libraries (pytest-operator, python-libjuju) is straightforward, and the included fixtures give you fine-grained control over model handling.\n\nFor more examples and migration techniques, consult the official documentation and see package readmes:\n- [PyPI: jubilant](https://pypi.org/project/jubilant/)\n- [PyPI: pytest-jubilant](https://pypi.org/project/pytest-jubilant/)\n- [Migration guide](https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/)【3:6†source】【3:2†source】【3:8†source】.","annotations":[{"text":"【3:6†source】","start_index":882,"end_index":894,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:0†source】","start_index":1114,"end_index":1126,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:1†source】","start_index":1126,"end_index":1138,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:2†source】","start_index":2313,"end_index":2325,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:8†source】","start_index":2325,"end_index":2337,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}},{"text":"【3:6†source】","start_index":3354,"end_index":3366,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:6†source】","start_index":4172,"end_index":4184,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:2†source】","start_index":4184,"end_index":4196,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:8†source】","start_index":4196,"end_index":4208,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}}]},"bing_searches":[{"text":"pytest-jubilant PyPI package juju charm testing fixtures conftest","url":"https://www.bing.com/search?q=pytest-jubilant+PyPI+package+juju+charm+testing+fixtures+conftest"}],"annotations":null}
````


---

<sub>⏱️ 54s</sub>

### 💬 Copilot

Let me get more detail on the pytest-jubilant API and what it provides out of the box.

---

<sub>⏱️ 54s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/pytest-jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://pypi.org/project/pytest-jubilant/",
  "max_length": 10000
}
```

</details>

```
Contents of https://pypi.org/project/pytest-jubilant/:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 54s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant/reference/jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://documentation.ubuntu.com/jubilant/reference/jubilant/",
  "max_length": 15000
}
```

</details>

<details>
<summary>251 lines</summary>

```
Contents of https://documentation.ubuntu.com/jubilant/reference/jubilant/:
Jubilant is a Pythonic wrapper around the Juju CLI.

exception jubilant.CLIError(_returncode_, _cmd_, _output\=None_, _stderr\=None_)[¶](#jubilant.CLIError "Link to this definition")

Bases: `CalledProcessError`

Subclass of `CalledProcessError` that includes stdout and stderr in the `__str__`.

class jubilant.Juju(

_\*_,

_model: str | None \= None_,

_wait\_timeout: float \= 180.0_,

_cli\_binary: str | Path | None \= None_,

)[¶](#jubilant.Juju "Link to this definition")

Bases: `object`

Instantiate this class to run Juju commands.

Most methods directly call a single Juju CLI command. If a CLI command doesn’t yet exist as a method, use [`cli()`](#jubilant.Juju.cli "jubilant.Juju.cli").

Example:

juju \= jubilant.Juju()
juju.deploy('snappass-test')

Parameters:

*   **model** – If specified, operate on this Juju model, otherwise use the current Juju model. If the model is in another controller, prefix the model name with `<controller>:`.
    
*   **wait\_timeout** – The default timeout for [`wait()`](#jubilant.Juju.wait "jubilant.Juju.wait") (in seconds) if that method’s _timeout_ parameter is not specified.
    
*   **cli\_binary** – Path to the Juju CLI binary. If not specified, uses `juju` and assumes it is in the PATH.
    

add\_credential(

_cloud: str_,

_credential: str | Path | Mapping\[str, Any\]_,

_\*_,

_client: Literal\[True\]_,

_controller: None \= None_,

_region: str | None \= None_,

) → None[¶](#jubilant.Juju.add_credential "Link to this definition")

add\_credential(

_cloud: str_,

_credential: str | Path | Mapping\[str, Any\]_,

_\*_,

_client: bool \= False_,

_controller: str_,

_region: str | None \= None_,

) → None

Add a credential for a cloud.

Parameters:

*   **cloud** – Name of the cloud to add credentials for.
    
*   **credential** – Path to a YAML file containing credential to add, or a mapping representing the parsed credential YAML (`{'credentials': ...}`).
    
*   **client** – Set to true to save credentials on the client, meaning controllers created later will have access to them. You must specify `client=True` or provide _controller_ (or both).
    
*   **controller** – If specified, save credentials to the named controller.
    
*   **region** – Cloud region that the credential is valid for.
    

add\_model(

_model: str_,

_cloud: str | None \= None_,

_\*_,

_controller: str | None \= None_,

_config: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\] | None \= None_,

_credential: str | None \= None_,

) → None[¶](#jubilant.Juju.add_model "Link to this definition")

Add a named model and set this instance’s model to it.

To avoid interfering with CLI users, this won’t switch the Juju CLI to the newly-created model. However, because [`model`](#jubilant.Juju.model "jubilant.Juju.model") is set to the name of the new model, all subsequent operations on this instance will use the new model.

Parameters:

*   **model** – Name of model to add.
    
*   **cloud** – Name of cloud or region (or cloud/region) to use for the model.
    
*   **controller** – Name of controller to operate in. If not specified, use the current controller.
    
*   **config** – Model configuration as key-value pairs, for example, `{'image-stream': 'daily'}`.
    
*   **credential** – Name of cloud credential to use for the model.
    

add\_secret(

_name: str_,

_content: Mapping\[str, str\]_,

_\*_,

_info: str | None \= None_,

) → [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")[¶](#jubilant.Juju.add_secret "Link to this definition")

Add a new named secret and return its secret URI.

Parameters:

*   **name** – Name for the secret.
    
*   **content** – Key-value pairs that represent the secret content, for example `{'password': 'hunter2'}`.
    
*   **info** – Description for the secret.
    

add\_ssh\_key(_\*keys: str_) → None[¶](#jubilant.Juju.add_ssh_key "Link to this definition")

Add one or more SSH keys to the model.

The SSH keys are added to all current and future machines in the model.

Parameters:

**keys** – SSH public key or keys to add. Each key should be the full SSH public key string (for example, `ssh-rsa AAAAB3... user@host`).

add\_unit(

_app: str_,

_\*_,

_attach\_storage: str | Iterable\[str\] | None \= None_,

_num\_units: int \= 1_,

_to: str | Iterable\[str\] | None \= None_,

)[¶](#jubilant.Juju.add_unit "Link to this definition")

Add one or more units to a deployed application.

Parameters:

*   **app** – Name of application to add units to.
    
*   **attach\_storage** – Existing storage(s) to attach to the deployed unit, for example, `foo/0` or `mydisk/1`. Not available for Kubernetes models.
    
*   **num\_units** – Number of units to add.
    
*   **to** – Machine or container to deploy the unit in (bypasses constraints). For example, to deploy to a new LXD container on machine 25, use `lxd:25`.
    

bootstrap(

_cloud: str_,

_controller: str_,

_\*_,

_bootstrap\_base: str | None \= None_,

_bootstrap\_constraints: Mapping\[str, str\] | None \= None_,

_config: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\] | None \= None_,

_constraints: Mapping\[str, str\] | None \= None_,

_credential: str | None \= None_,

_force: bool \= False_,

_model\_defaults: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\] | None \= None_,

_storage\_pool: Mapping\[str, str\] | None \= None_,

_to: str | Iterable\[str\] | None \= None_,

) → None[¶](#jubilant.Juju.bootstrap "Link to this definition")

Bootstrap a controller on a cloud environment.

To avoid interfering with CLI users, this does not switch the Juju CLI to the newly-created controller. In addition, `self.model` is not updated.

If you want to create a new controller with a model, use [`add_model()`](#jubilant.Juju.add_model "jubilant.Juju.add_model") after calling this method, which will set `self.model` for future commands:

juju \= jubilant.Juju()
juju.bootstrap('lxd', 'myctrl')
juju.add\_model('mymodel', controller\='myctrl')
\# self.model will be 'myctrl.mymodel' here

Parameters:

*   **cloud** – Name of cloud to bootstrap on. Initialization consists of creating a “controller” model and provisioning a machine to act as controller.
    
*   **controller** – Name for the controller.
    
*   **bootstrap\_base** – Specify the base of the bootstrap machine, for example `"24.04"`.
    
*   **bootstrap\_constraints** – Specify bootstrap machine constraints, for example, `{'mem': '8G'}`. If used, its values will also apply to any future controllers provisioned for high availability (HA).
    
*   **config** – Controller configuration options. Model config keys only affect the controller model.
    
*   **constraints** – Set model constraints, for example, `{'mem': '8G', 'cores': '4'}`. If used, its values will be set as the default constraints for all future workload machines in the model, exactly as if the constraints were set with `juju set-model-constraints`.
    
*   **credential** – Name of cloud credential to use when bootstrapping.
    
*   **force** – If true, allow bypassing of checks such as supported bases.
    
*   **model\_defaults** – Configuration options to set for all models.
    
*   **storage\_pool** – Options for an initial storage pool as key-value pairs. `name` and `type` are required, plus any additional attributes.
    
*   **to** – Placement directive indicating an instance to bootstrap.
    

cli(

_\*args: str_,

_include\_model: bool \= True_,

_stdin: str | None \= None_,

) → str[¶](#jubilant.Juju.cli "Link to this definition")

Run a Juju CLI command and return its standard output.

Parameters:

*   **args** – Command-line arguments (excluding `juju`).
    
*   **include\_model** – If true and [`model`](#jubilant.Juju.model "jubilant.Juju.model") is set, insert the `--model` argument after the first argument in _args_.
    
*   **stdin** – Standard input to send to the process, if any.
    

cli\_binary: str[¶](#jubilant.Juju.cli_binary "Link to this definition")

Path to the Juju CLI binary. If None, uses `juju` and assumes it is in the PATH.

config(

_app: str_,

_\*_,

_app\_config: bool \= False_,

) → Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\][¶](#jubilant.Juju.config "Link to this definition")

config(

_app: str_,

_values: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\]_,

_\*_,

_reset: str | Iterable\[str\] \= ()_,

) → None

config(_app: str_, _\*_, _reset: str | Iterable\[str\]_) → None

Get or set the configuration of a deployed application.

If called with only the _app_ argument, get the config and return it.

If called with the _values_ or _reset_ arguments, set the config values and return None, and reset any keys in _reset_ to their defaults.

Parameters:

*   **app** – Application name to get or set config for.
    
*   **values** – Mapping of config names to values to set.
    
*   **app\_config** – When getting config, set this to true to get the (poorly-named) “application-config” values instead of charm config.
    
*   **reset** – Key or list of keys to reset to their defaults.
    

consume(

_model\_and\_app: str_,

_alias: str | None \= None_,

_\*_,

_controller: str | None \= None_,

_owner: str | None \= None_,

) → None[¶](#jubilant.Juju.consume "Link to this definition")

Add a remote offer to the model.

Examples:

juju.consume('othermodel.mysql', 'sql')
juju.consume('othermodel.mysql', controller\='ctrl2', owner\='admin')

Parameters:

*   **model\_and\_app** – Dotted application and model name to offer endpoints for, for example `othermodel.mysql`.
    
*   **alias** – A local alias for the offer, for use with [`integrate()`](#jubilant.Juju.integrate "jubilant.Juju.integrate"). Defaults to the application name.
    
*   **controller** – Remote offer’s controller. Defaults to the current controller.
    
*   **owner** – Remote model’s owner. Defaults to the user that is currently logged in to the controller providing the offer.
    

debug\_log(_\*_, _limit: int \= 0_) → str[¶](#jubilant.Juju.debug_log "Link to this definition")

Return debug log messages from a model.

For example, to create a pytest fixture which shows the last 1000 log lines if any tests fail:

@pytest.fixture(scope\='module')
def juju(request: pytest.FixtureRequest):
    with jubilant.temp\_model() as juju:
        yield juju  \# run the test
        if request.session.testsfailed:
            log \= juju.debug\_log(limit\=1000)
            print(log, end\='')

Parameters:

**limit** – Limit the result to the most recent _limit_ lines. Defaults to 0, meaning return all lines in the log.

deploy(

_charm: str | Path_,

_app: str | None \= None_,

_\*_,

_attach\_storage: str | Iterable\[str\] | None \= None_,

_base: str | None \= None_,

_bind: Mapping\[str, str\] | str | None \= None_,

_channel: str | None \= None_,

_config: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\] | None \= None_,

_constraints: Mapping\[str, str\] | None \= None_,

_force: bool \= False_,

_num\_units: int \= 1_,

_overlays: Iterable\[str | Path\] \= ()_,

_resources: Mapping\[str, str\] | None \= None_,

_revision: int | None \= None_,

_storage: Mapping\[str, str\] | None \= None_,

_to: str | Iterable\[str\] | None \= None_,

_trust: bool \= False_,

) → None[¶](#jubilant.Juju.deploy "Link to this definition")

Deploy an application or bundle.

Parameters:

*   **charm** – Name of charm or bundle to deploy, or path to a local file (must start with `/` or `.`).
    
*   **app** – Custom application name within the model. Defaults to the charm name.
    
*   **attach\_storage** – Existing storage(s) to attach to the deployed unit, for example, `foo/0` or `mydisk/1`. Not available for Kubernetes models.
    
*   **base** – The base on which to deploy, for example, `ubuntu@22.04`.
    
*   **bind** – Either a mapping of endpoint-to-space bindings, for example `{'database-peers': 'internal-space'}`, or a single space name, which is equivalent to binding all endpoints to that space.
    
*   **channel** – Channel to use when deploying from Charmhub, for example, `latest/edge`.
    
*   **config** – Application configuration as key-value pairs, for example, `{'name': 'My Wiki'}`.
    
*   **constraints** – Hardware constraints for new machines, for example, `{'mem': '8G'}`.
    
*   **force** – If true, bypass checks such as supported bases.
    
*   **num\_units** – Number of units to deploy for principal charms.
    
*   **overlays** – File paths of bundles to overlay on the primary bundle, applied in order.
    
*   **resources** – Specify named resources to use for deployment, for example: `{'bin': '/path/to/some/binary'}`.
    
*   **revision** – Charmhub revision number to deploy.
    
*   **storage** – Constraints for named storage(s), for example, `{'data': 'tmpfs,1G'}`.
    
*   **to** – Machine or container to deploy the unit in (bypasses constraints). For example, to deploy to a new LXD container on machine 25, use `lxd:25`.
    
*   **trust** – If true, allows charm to run hooks that require access to cloud credentials.
    

destroy\_model(

_model: str_,

_\*_,

_destroy\_storage: bool \= False_,

_force: bool \= False_,

_no\_wait: bool \= False_,

_release\_storage: bool \= False_,

_timeout: float | None \= None_,

) → None[¶](#jubilant.Juju.destroy_model "Link to this definition")

Terminate all machines (or containers) and resources for a model.

If the given model is this instance’s model, also sets this instance’s [`model`](#jubilant.Juju.model "jubilant.Juju.model") to None.

Parameters:

*   **model** – Name of model to destroy.
    
*   **destroy\_storage** – If true, destroy all storage instances in the model.
    
*   **force** – If true, force model destruction and ignore any errors.
    
*   **no\_wait** – If true, rush through model destruction without waiting for each step to complete.
    
*   **release\_storage** – If true, release all storage instances in the model. This is mutually exclusive with _destroy\_storage_.
    
*   **timeout** – Maximum time (in seconds) to wait for each step in the model destruction. This option can only be used with _force_.
    

exec(

_command: str_,

_\*args: str_,

_machine: int | str_,

_wait: float | None \= None_,

) → [Task](#jubilant.Task "jubilant._task.Task")[¶](#jubilant.Juju.exec "Link to this definition")

exec(

_command: str_,

_\*args: str_,

_unit: str_,

_wait: float | None \= None_,

) → [Task](#jubilant.Task "jubilant._task.Task")

Run the command on

<note>Content truncated. Call the fetch tool with a start_index of 15000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 0s</sub>

### ❌ `web_fetch`

**https://documentation.ubuntu.com/jubilant/reference/pytest-jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://documentation.ubuntu.com/jubilant/reference/pytest-jubilant/"
}
```

</details>

```
Error: Failed to fetch https://documentation.ubuntu.com/jubilant/reference/pytest-jubilant/ - status code 404
```


---

<sub>⏱️ 1m 10s</sub>

### ✅ `web_search`

**pytest-jubilant reference documentation fixtures API site:documentation.ubuntu.com OR site:github.com/canonical**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest-jubilant reference documentation fixtures API site:documentation.ubuntu.com OR site:github.com/canonical"
}
```

</details>

````
{"type":"text","text":{"value":"Based on the specified sources, there is currently no official documentation page for the `pytest-jubilant` plugin on either documentation.ubuntu.com or github.com/canonical. In fact, there is no major reference or API listing for a tool named `pytest-jubilant` on these sites. This suggests either the package is very new/obscure, not widely documented publicly yet, or the name may be incorrect.\n\nHowever, if you’re looking for general reference documentation on how to use pytest fixtures as part of writing tests—which is a common feature in most pytest plugins—the best practices and API reference for fixtures can be summarized as follows:\n\n- **Defining fixtures:** Use the `@pytest.fixture` decorator to define setup code that can be reused across multiple tests. \n- **Using fixtures:** Declare fixture names as arguments in your test functions; pytest will automatically inject the fixture’s value.\n- **Scopes:** Fixtures can have different lifecycles (`function`, `class`, `module`, `session`) set with the `scope=` parameter.\n- **Yield vs Return:** You can use `yield` in a fixture to implement teardown logic after the test runs.\n- **Automatic use:** The `autouse=True` option will inject the fixture into all tests without needing to be explicitly named in test signatures.\n- **Shared fixtures:** The `conftest.py` file allows sharing fixtures across an entire directory of tests.\n\nExample:\n```python\nimport pytest\n\n@pytest.fixture\ndef user():\n    return {\"name\": \"Alice\", \"role\": \"admin\"}\n\ndef test_user_is_admin(user):\n    assert user[\"role\"] == \"admin\"\n```\n\nPytest’s fixture API is widely discussed and officially documented, with robust support for modular setup, teardown, and configuration sharing between tests【3:0†Pytest Like a Pro: Fixtures, Mocks, and Patterns That Actually Work†https://dev.to/_85e8844dcca5f98bfa936/pytest-like-a-pro-fixtures-mocks-and-patterns-that-actually-work-1d8n】【3:2†Pytest Fixtures & Testing Patterns | Claude Code Skill†https://mcpmarket.com/tools/skills/pytest-fixtures-testing-patterns】.\n\nIf you wanted information specifically about a canonical pytest plugin used in the Ubuntu SNAP or Canonical ecosystem, it may be best to raise an issue or make an inquiry directly on Canonical’s official GitHub repositories or Ubuntu documentation channels, as nothing was found under these domains for \"pytest-jubilant\".\n\nFor most needs regarding writing or using fixtures in pytest, the official pytest documentation and community tutorials provide comprehensive coverage. If you need assistance with another, perhaps similarly named plugin associated with Canonical, please provide more details and I can help you track it down!","annotations":[{"text":"【3:0†Pytest Like a Pro: Fixtures, Mocks, and Patterns That Actually Work†https://dev.to/_85e8844dcca5f98bfa936/pytest-like-a-pro-fixtures-mocks-and-patterns-that-actually-work-1d8n】","start_index":1729,"end_index":1910,"url_citation":{"title":"Pytest Like a Pro: Fixtures, Mocks, and Patterns That Actually Work","url":"https://dev.to/_85e8844dcca5f98bfa936/pytest-like-a-pro-fixtures-mocks-and-patterns-that-actually-work-1d8n"}},{"text":"【3:2†Pytest Fixtures & Testing Patterns | Claude Code Skill†https://mcpmarket.com/tools/skills/pytest-fixtures-testing-patterns】","start_index":1910,"end_index":2038,"url_citation":{"title":"Pytest Fixtures & Testing Patterns | Claude Code Skill","url":"https://mcpmarket.com/tools/skills/pytest-fixtures-testing-patterns"}}]},"bing_searches":[{"text":"pytest-jubilant reference documentation fixtures API site=documentation.ubuntu.com OR site=github.com/canonical","url":"https://www.bing.com/search?q=pytest-jubilant+reference+documentation+fixtures+API+site%3Ddocumentation.ubuntu.com+OR+site%3Dgithub.com%2Fcanonical"}],"annotations":null}
````


---

<sub>⏱️ 1m 14s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/jubilant**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/jubilant"
}
```

</details>

<details>
<summary>61 lines</summary>

````
Contents of https://github.com/canonical/jubilant:
## Jubilant, the joyful library for driving Juju

[](#jubilant-the-joyful-library-for-driving-juju)

Jubilant is a Python library that wraps the [Juju](https://juju.is/) CLI, primarily for use in charm integration tests. It provides methods that map 1:1 to Juju CLI commands, but with a type-annotated, Pythonic interface.

You should consider switching to Jubilant if your integration tests currently use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) (and they probably do). Jubilant has an API you'll pick up quickly, and it avoids some of the pain points of [python-libjuju](https://github.com/juju/python-libjuju/), such as websocket failures and having to use `async`. Read our [design goals](https://documentation.ubuntu.com/jubilant/explanation/design-goals).

Jubilant 1.0.0 was released in April 2025. We'll avoid making breaking changes to the API after this point.

[**Read the full documentation**](https://documentation.ubuntu.com/jubilant/)

## Using Jubilant

[](#using-jubilant)

Jubilant is published to PyPI, so you can install and use it with your favorite Python package manager:

```
$ pip install jubilant
# or
$ uv add jubilant
```

Because Jubilant calls the Juju CLI, you'll also need to [install Juju](https://documentation.ubuntu.com/juju/3.6/howto/manage-juju/index.html#install-juju).

To use Jubilant in Python code:

import jubilant

juju \= jubilant.Juju()
juju.deploy('snappass-test')
juju.wait(jubilant.all\_active)

\# Or only wait for specific applications:
juju.wait(lambda status: jubilant.all\_active(status, 'snappass-test', 'another-app'))

Below is an example of a charm integration test. First we define a module-scoped [pytest fixture](https://docs.pytest.org/en/stable/explanation/fixtures.html) named `juju` which creates a temporary model and runs the test with a `Juju` instance pointing at that model. Jubilant's`temp_model` context manager creates the model during test setup and destroys it during teardown:

\# conftest.py
@pytest.fixture(scope\='module')
def juju():
    with jubilant.temp\_model() as juju:
        yield juju

\# test\_deploy.py
def test\_deploy(juju: jubilant.Juju):        \# Use the "juju" fixture
    juju.deploy('snappass-test')             \# Deploy the charm
    status \= juju.wait(jubilant.all\_active)  \# Wait till the app and unit are 'active'

    \# Hit the Snappass HTTP endpoint to ensure it's up and running.
    address \= status.apps\['snappass-test'\].units\['snappass-test/0'\].address
    response \= requests.get(f'http://{address}:5000/', timeout\=10)
    response.raise\_for\_status()
    assert 'snappass' in response.text.lower()

You don't have to use pytest with Jubilant, but it's what we recommend. Pytest's `assert`\-based approach is a straight-forward way to write tests, and its fixtures are helpful for structuring setup and teardown.

## Contributing and developing

[](#contributing-and-developing)

Anyone can contribute to Jubilant. It's best to start by [opening an issue](https://github.com/canonical/jubilant/issues) with a clear description of the problem or feature request, but you can also [open a pull request](https://github.com/canonical/jubilant/pulls) directly.

Jubilant uses [`uv`](https://docs.astral.sh/uv/) to manage Python dependencies and tools, so you'll need to [install uv](https://docs.astral.sh/uv/#installation) to work on the library. You'll also need `make` to run local development tasks (but you probably have `make` installed already).

After that, clone the Jubilant codebase and use `make all` to run various checks and the unit tests:

```
$ git clone https://github.com/canonical/jubilant
Cloning into 'jubilant'...
...
$ cd jubilant
$ make all
...
========== 107 passed in 0.26s ==========
```

To contribute a code change, write your fix or feature, add tests and docs, then run `make all` before you push and create a PR. Once you create a PR, GitHub will also run the integration tests, which takes several minutes.

## Doing a release

[](#doing-a-release)

To create a new release of Jubilant:

1.  Update the `__version__` field in [`jubilant/__init__.py`](https://github.com/canonical/jubilant/blob/main/jubilant/__init__.py) to the new version you want to release.
2.  Push up a PR with this change and get it reviewed and merged.
3.  Create a [new release](https://github.com/canonical/jubilant/releases/new) on GitHub with good release notes. The tag should start with a `v`, like `v1.2.3`. Once you've created the release, the [`publish.yaml` workflow](https://github.com/canonical/jubilant/blob/main/.github/workflows/publish.yaml) will automatically publish it to PyPI.
4.  Once the publish workflow has finished, check that the new version appears in the [PyPI version history](https://pypi.org/project/jubilant/#history).
````

</details>


---

<sub>⏱️ 1m 19s</sub>

### ✅ `github-mcp-server-search_repositories`

**pytest-jubilant org:canonical**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest-jubilant org:canonical"
}
```

</details>

```
{"total_count":0,"incomplete_results":false,"items":[]}
```


---

<sub>⏱️ 1m 33s</sub>

### ✅ `web_search`

**pypi pytest-jubilant package canonical juju**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pypi pytest-jubilant package canonical juju"
}
```

</details>

````
{"type":"text","text":{"value":"The `pytest-jubilant` package is a plugin for `pytest` designed to ease the transition from `pytest-operator` to `jubilant`, with additional features on top. It is closely related to Canonical's Juju ecosystem, specifically for charm integration testing.\n\n## What is `pytest-jubilant`?\n\n- **Purpose**: A pytest plugin for running Juju charm integration tests using the Jubilant library.\n- **Fixtures**: Provides easy-to-use fixtures, notably `juju`, which sets up a temporary Juju model for the scope of your tests and tears it down automatically. There's also a `temp_model_factory` for more advanced cases, like running tests that require multiple models.\n- **Command-line options**: Supports options like `--model` to use a specific Juju model, `--keep-models` to skip teardown, and `--no-teardown` to prevent model destruction after tests—helpful for debugging.\n\n### Example usage\n\n```python\nfrom jubilant import Juju, all_active\n\ndef test_deploy(juju: Juju):\n    juju.deploy(\"./foo.charm\", \"foo\")\n    juju.wait(lambda status: all_active(status, \"foo\"), timeout=1000)\n```\n\nFor tests using more than one model:\n\n```python\nimport pytest\nfrom jubilant import Juju, all_active\n\n@pytest.fixture\ndef istio(temp_model_factory):\n    yield temp_model_factory.get_juju(suffix=\"istio\")\n\ndef test_cmr(juju: Juju, istio: Juju):\n    istio.deploy(\"istio-k8s\", \"istio\")\n    istio.wait(lambda status: all_active(status, \"istio\"), timeout=1000)\n    juju.deploy(\"./foo.charm\", \"foo\")\n    juju.wait(lambda status: all_active(status, \"foo\"), timeout=1000)\n    juju.cli(\"offer\", \"foo:bar\")\n    istio.cli(\"consume\", f\"{juju.model}:foo\")\n    istio.cli(\"relate\", \"istio\", \"foo:bar\")\n```\n\n## About `jubilant` (Canonical package)\n\n- **Jubilant** is a Python library that wraps the Juju CLI for charm integration testing. It aims to offer a more stable and user-friendly API than `python-libjuju`, avoiding websocket failures and async requirements. It supports methods that directly map to Juju CLI commands with typed, Pythonic interfaces【3:1†source】【3:4†source】【3:9†source】.\n- **Migration**: Canonical recommends migrating from `pytest-operator` (and `python-libjuju`) to Jubilant for greater stability and ease of use. Migration guides are available in the official documentation【3:2†source】【3:3†source】【3:7†source】.\n- **Installation**: Install via PyPI: `pip install pytest-jubilant` or `pip install jubilant`.\n\n## Further resources\n\n- [pytest-jubilant PyPI page with usage examples and options](https://pypi.org/project/pytest-jubilant/)【3:0†source】\n- [Jubilant GitHub repository for in-depth API and development](https://github.com/canonical/jubilant)【3:1†source】\n- [Official documentation and migration guides](https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/)【3:2†source】【3:3†source】\n- [Jubilant on PyPI](https://pypi.org/project/jubilant/)【3:4†source】\n\nIf you're developing or testing Juju charms, using `pytest-jubilant` and `jubilant` should streamline the process, especially as Canonical continues to invest in these tools for the charm ecosystem.","annotations":[{"text":"【3:1†source】","start_index":2016,"end_index":2028,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:4†source】","start_index":2028,"end_index":2040,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:9†source】","start_index":2040,"end_index":2052,"url_citation":{"title":"Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/"}},{"text":"【3:2†source】","start_index":2259,"end_index":2271,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/"}},{"text":"【3:3†source】","start_index":2271,"end_index":2283,"url_citation":{"title":"How-to guides - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/how-to/"}},{"text":"【3:7†source】","start_index":2283,"end_index":2295,"url_citation":{"title":"How-to guides - Jubilant documentation","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/"}},{"text":"【3:0†source】","start_index":2519,"end_index":2531,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:1†source】","start_index":2634,"end_index":2646,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:2†source】","start_index":2782,"end_index":2794,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/"}},{"text":"【3:3†source】","start_index":2794,"end_index":2806,"url_citation":{"title":"How-to guides - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/how-to/"}},{"text":"【3:4†source】","start_index":2863,"end_index":2875,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}}]},"bing_searches":[{"text":"pypi pytest-jubilant package canonical juju","url":"https://www.bing.com/search?q=pypi+pytest-jubilant+package+canonical+juju"}],"annotations":null}
````


---

<sub>⏱️ 2m 5s</sub>

### 💬 Copilot

Now I have a clear understanding of the migration. Let me create a plan and implement it.

---

<sub>⏱️ 2m 5s</sub>

### ✅ `create`

**/home/ubuntu/.copilot/session-state/c819af2b-cbd3-4765-b2b8-be714ead93ab/plan.md**

/home/ubuntu/.copilot/session-state/c819af2b-cbd3-4765-b2b8-be714ead93ab/plan.md

```
Created file /home/ubuntu/.copilot/session-state/c819af2b-cbd3-4765-b2b8-be714ead93ab/plan.md with 548 characters
```


---

<sub>⏱️ 2m 12s</sub>

### 💬 Copilot

Now let me make all the changes. I'll edit the files in parallel where possible.

---

<sub>⏱️ 2m 12s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L1-opus/pyproject.toml**

/tmp/saml-integrator-L1-opus/pyproject.toml

```
File /tmp/saml-integrator-L1-opus/pyproject.toml updated with changes.
```


---

<sub>⏱️ 2m 16s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L1-opus/pyproject.toml**

/tmp/saml-integrator-L1-opus/pyproject.toml

```
File /tmp/saml-integrator-L1-opus/pyproject.toml updated with changes.
```


---

<sub>⏱️ 2m 32s</sub>

### 💬 Copilot

Now update the integration conftest.py:

---

<sub>⏱️ 2m 32s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L1-opus/tests/integration/conftest.py**

/tmp/saml-integrator-L1-opus/tests/integration/conftest.py

```
File /tmp/saml-integrator-L1-opus/tests/integration/conftest.py updated with changes.
```


---

<sub>⏱️ 2m 47s</sub>

### 💬 Copilot

Now update the test file:

---

<sub>⏱️ 2m 47s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L1-opus/tests/integration/test_charm.py**

/tmp/saml-integrator-L1-opus/tests/integration/test_charm.py

```
File /tmp/saml-integrator-L1-opus/tests/integration/test_charm.py updated with changes.
```


---

<sub>⏱️ 2m 51s</sub>

### 💬 Copilot

Now let me update the lockfile and verify linting passes:

---

<sub>⏱️ 2m 52s</sub>

### ✅ `bash`

**Regenerate uv.lock after dependency changes**

$ cd /tmp/saml-integrator-L1-opus && uv lock 2>&1 | tail -5

<details>
<summary>6 lines</summary>

```
Removed toposort v1.10
Removed traitlets v5.14.3
Removed typing-inspect v0.9.0
Removed wcwidth v0.2.14
Removed websockets v15.0.1
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 56s</sub>

### 💬 Copilot

Good. Now let me verify the changes look correct:

---

<sub>⏱️ 2m 56s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-opus/tests/integration/conftest.py**

/tmp/saml-integrator-L1-opus/tests/integration/conftest.py

<details>
<summary>55 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Fixtures for the SAML Integrator charm integration tests."""
5. 
6. import json
7. from pathlib import Path
8. 
9. import jubilant
10. import yaml
11. from pytest import Config, fixture
12. 
13. 
14. @fixture(scope="module", name="app_name")
15. def app_name_fixture():
16.     """Provide app name from the metadata."""
17.     metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
18.     yield metadata["name"]
19. 
20. 
21. @fixture(scope="module")
22. def app(juju: jubilant.Juju, pytestconfig: Config, app_name: str):
23.     """SAML Integrator charm used for integration testing.
24. 
25.     Build the charm and deploy it along with Anycharm.
26.     """
27.     charm = pytestconfig.getoption("--charm-file")
28.     juju.deploy(
29.         f"./{charm}",
30.         app_name,
31.     )
32.     yield app_name
33. 
34. 
35. @fixture(scope="module")
36. def any_charm(juju: jubilant.Juju):
37.     """SAML Integrator charm used for integration testing.
38. 
39.     Build the charm and deploy it along with Anycharm.
40.     """
41.     path_lib = "lib/charms/saml_integrator/v0/saml.py"
42.     saml_lib = Path(path_lib).read_text(encoding="utf8")
43.     any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
44.     src_overwrite = {
45.         "saml.py": saml_lib,
46.         "any_charm.py": any_charm_script,
47.     }
48.     juju.deploy(
49.         "any-charm",
50.         "any",
51.         channel="beta",
52.         config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
53.     )
54.     yield "any"
55.
```

</details>


---

<sub>⏱️ 2m 56s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-opus/tests/integration/test_charm.py**

/tmp/saml-integrator-L1-opus/tests/integration/test_charm.py

<details>
<summary>48 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2025 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """SAML Integrator charm integration tests."""
6. 
7. import jubilant
8. import pytest
9. 
10. 
11. @pytest.mark.abort_on_fail
12. def test_active(juju: jubilant.Juju, app: str):
13.     """Check that the charm is active.
14. 
15.     Assume that the charm has already been built and is running.
16.     """
17.     juju.config(
18.         app,
19.         {
20.             "entity_id": "https://login.staging.ubuntu.com",
21.             "fingerprint": "",
22.             "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
23.         },
24.     )
25.     juju.wait(lambda status: jubilant.all_active(status, app))
26.     status = juju.status()
27.     assert status.apps[app].units[f"{app}/0"].is_active
28. 
29. 
30. @pytest.mark.abort_on_fail
31. def test_relation(juju: jubilant.Juju, app: str, any_charm: str):
32.     """Check that the charm is active once related to another charm.
33. 
34.     Assume that the charm has already been built and is running.
35.     """
36.     juju.integrate(f"{any_charm}:require-saml", f"{app}:saml")
37.     juju.config(
38.         app,
39.         {
40.             "entity_id": "https://login.staging.ubuntu.com",
41.             "fingerprint": "",
42.             "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
43.         },
44.     )
45.     juju.wait(lambda status: jubilant.all_active(status, app))
46.     status = juju.status()
47.     assert status.apps[app].units[f"{app}/0"].is_active
48.
```

</details>


---

<sub>⏱️ 3m 1s</sub>

### 💬 Copilot

Now let's run the linter to verify our changes pass:

---

<sub>⏱️ 3m 4s</sub>

### ✅ `bash`

**Run linter to verify changes**

$ cd /tmp/saml-integrator-L1-opus && tox -e lint 2>&1 | tail -30

<details>
<summary>14 lines</summary>

```
lint: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/saml-integrator-L1-opus/.tox/lint
lint: uv-sync> uv sync --locked --python-preference system --no-default-groups --group lint -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
lint: commands[0]> codespell /tmp/saml-integrator-L1-opus
lint: commands[1]> ruff format --check --diff /tmp/saml-integrator-L1-opus/src/ /tmp/saml-integrator-L1-opus/tests/ /tmp/saml-integrator-L1-opus/lib/charms/saml_integrator
warning: Selection `CPY` has no effect because preview is not enabled.
17 files already formatted
lint: commands[2]> ruff check /tmp/saml-integrator-L1-opus/src/ /tmp/saml-integrator-L1-opus/tests/ /tmp/saml-integrator-L1-opus/lib/charms/saml_integrator
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
lint: commands[3]> mypy /tmp/saml-integrator-L1-opus/src/ /tmp/saml-integrator-L1-opus/tests/ /tmp/saml-integrator-L1-opus/lib/charms/saml_integrator
Success: no issues found in 17 source files
  lint: OK (3.36=setup[0.16]+cmd[0.08,0.01,0.01,3.10] seconds)
  congratulations :) (3.38 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 8s</sub>

### 💬 Copilot

All linting passes. Let me also run unit tests to make sure nothing else is broken:

---

<sub>⏱️ 3m 10s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/saml-integrator-L1-opus && tox -e unit 2>&1 | tail -15

<details>
<summary>15 lines</summary>

```
with importlib.resources.open_text(pkg_name, schema_file) as schema_fh:

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 20 passed, 11 warnings in 0.61s ========================
unit: commands[1]> coverage report
Name                                    Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------
lib/charms/saml_integrator/v0/saml.py      97      1     16      2    97%   111->113, 309
src/charm.py                               40      0      4      0   100%
src/charm_state.py                         46      0      4      0   100%
src/saml.py                                55      0      6      0   100%
-----------------------------------------------------------------------------------
TOTAL                                     238      1     30      2    99%
  unit: OK (1.34=setup[0.18]+cmd[1.09,0.07] seconds)
  congratulations :) (1.36 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 14s</sub>

### 💬 Copilot

All passing. Now let me commit the changes:

---

<sub>⏱️ 3m 14s</sub>

### ✅ `bash`

**Check git diff stats**

$ cd /tmp/saml-integrator-L1-opus && git --no-pager diff --stat

<details>
<summary>6 lines</summary>

```
pyproject.toml                  |   9 +-
 tests/integration/conftest.py   |  25 ++-
 tests/integration/test_charm.py |  36 ++--
 uv.lock                         | 825 ++------------------------------------------------------------------------------
 4 files changed, 48 insertions(+), 847 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 23s</sub>

### ✅ `bash`

**Commit migration changes**

$ cd /tmp/saml-integrator-L1-opus && git add -A && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace pytest-operator (python-libjuju) with jubilant and pytest-jubilant
for integration tests:

- Update dependency groups in pyproject.toml: remove juju, pytest-asyncio,
  and pytest-operator; add jubilant and pytest-jubilant
- Rewrite tests/integration/conftest.py: replace async fixtures using
  OpsTest with sync fixtures using jubilant.Juju
- Rewrite tests/integration/test_charm.py: remove async/await, use
  juju.config(), juju.wait(), juju.integrate(), and juju.status()
- Regenerate uv.lock

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

<details>
<summary>9 lines</summary>

```
Author identity unknown

*** Please tell me who you are.

Run

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"

to set your account's default identity.
Omit --global to set the identity only in this repository.

fatal: unable to auto-detect email address (got 'ubuntu@jubilant-migration.(none)')
<exited with exit code 128>
```

</details>


---

<sub>⏱️ 3m 29s</sub>

### ✅ `bash`

**Commit with git config**

$ cd /tmp/saml-integrator-L1-opus && git config user.email "copilot@github.com" && git config user.name "Copilot" && git add -A && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace pytest-operator (python-libjuju) with jubilant and pytest-jubilant
for integration tests:

- Update dependency groups in pyproject.toml: remove juju, pytest-asyncio,
  and pytest-operator; add jubilant and pytest-jubilant
- Rewrite tests/integration/conftest.py: replace async fixtures using
  OpsTest with sync fixtures using jubilant.Juju
- Rewrite tests/integration/test_charm.py: remove async/await, use
  juju.config(), juju.wait(), juju.integrate(), and juju.status()
- Regenerate uv.lock

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[main 24c5f74] Migrate integration tests from pytest-operator to jubilant
 4 files changed, 48 insertions(+), 847 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 3m 36s</sub>

### 💬 Copilot

Migration complete. Here's what was changed:

1. **`pyproject.toml`** — Replaced `juju`, `pytest-asyncio`, `pytest-operator` with `jubilant` and `pytest-jubilant` in both `integration` and `lint` dependency groups.

2. **`tests/integration/conftest.py`** — Converted async fixtures to sync; replaced `OpsTest`/`pytest_asyncio` with `jubilant.Juju` from the `juju` fixture provided by `pytest-jubilant`; fixtures now yield app name strings instead of `ops.Application` objects.

3. **`tests/integration/test_charm.py`** — Removed all `async`/`await`/`@pytest.mark.asyncio`; replaced `ops_test.model.wait_for_idle` → `juju.wait(jubilant.all_active)`, `app.set_config` → `juju.config()`, `model.add_relation` → `juju.integrate()`, and status checks use `juju.status()`.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
