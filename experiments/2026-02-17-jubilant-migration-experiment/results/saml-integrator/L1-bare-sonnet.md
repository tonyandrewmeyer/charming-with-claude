# 🤖 Copilot CLI Session

> **Session ID:** `b5a36295-5c45-40e2-935e-7a66c69eacb8`
> **Started:** 7 Mar 2026, 11:47:25 AM
> **Duration:** 3m 24s
> **Exported:** 7 Mar 2026, 11:50:49 AM

<sub>⏱️ 4s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

---

<sub>⏱️ 8s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-sonnet**

/tmp/saml-integrator-L1-sonnet

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

<sub>⏱️ 8s</sub>

### ✅ `glob`

**/tmp/saml-integrator-L1-sonnet**

"tests/**/*" in /tmp/saml-integrator-L1-sonnet

<details>
<summary>18 matches</summary>

```
/tmp/saml-integrator-L1-sonnet/tests/__init__.py
/tmp/saml-integrator-L1-sonnet/tests/unit/test_saml.py
/tmp/saml-integrator-L1-sonnet/tests/unit/__init__.py
/tmp/saml-integrator-L1-sonnet/tests/unit/test_charm_state.py
/tmp/saml-integrator-L1-sonnet/tests/unit/test_library_saml.py
/tmp/saml-integrator-L1-sonnet/tests/unit/files/metadata_signed_tampered.xml
/tmp/saml-integrator-L1-sonnet/tests/unit/files/metadata_unsigned.xml
/tmp/saml-integrator-L1-sonnet/tests/unit/files/metadata_default_namespaces.xml
/tmp/saml-integrator-L1-sonnet/tests/unit/files/metadata_signed.xml
/tmp/saml-integrator-L1-sonnet/tests/unit/files/non_utf8_metadata_unsigned.xml
/tmp/saml-integrator-L1-sonnet/tests/unit/test_charm.py
/tmp/saml-integrator-L1-sonnet/tests/interface/test_saml.py
/tmp/saml-integrator-L1-sonnet/tests/interface/conftest.py
/tmp/saml-integrator-L1-sonnet/tests/integration/__init__.py
/tmp/saml-integrator-L1-sonnet/tests/integration/any_charm.py
/tmp/saml-integrator-L1-sonnet/tests/integration/test_charm.py
/tmp/saml-integrator-L1-sonnet/tests/integration/conftest.py
/tmp/saml-integrator-L1-sonnet/tests/conftest.py
```

</details>


---

<sub>⏱️ 12s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L1-sonnet/tests/integration/conftest.py

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

<sub>⏱️ 12s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L1-sonnet/tests/integration/test_charm.py

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

<sub>⏱️ 12s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-sonnet/tests/conftest.py**

/tmp/saml-integrator-L1-sonnet/tests/conftest.py

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

<sub>⏱️ 12s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-sonnet/tox.toml**

/tmp/saml-integrator-L1-sonnet/tox.toml

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

<sub>⏱️ 12s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-sonnet/pyproject.toml**

/tmp/saml-integrator-L1-sonnet/pyproject.toml

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

<sub>⏱️ 21s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-sonnet/tests/integration/any_charm.py**

/tmp/saml-integrator-L1-sonnet/tests/integration/any_charm.py

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

<sub>⏱️ 31s</sub>

### ✅ `web_search`

**jubilant pytest-jubilant juju charm integration tests API usage examples**

<details>
<summary>Arguments</summary>

```json
{
  "query": "jubilant pytest-jubilant juju charm integration tests API usage examples"
}
```

</details>

````
{"type":"text","text":{"value":"Here’s how you can use the Jubilant library (formerly called `pytest-jubilant`) for writing Juju charm integration tests, with concrete API usage examples and integration with `pytest`:\n\n---\n\n## What is Jubilant?\nJubilant is a Python library designed specifically to wrap the Juju CLI, providing Pythonic and type-annotated access for charm integration tests. It replaces tools like `pytest-operator` and `python-libjuju`, offering a more stable, synchronous experience by executing actual Juju CLI commands under the hood【3:0†source】【3:2†source】【3:1†source】.\n\n---\n\n## Installing Jubilant\n\n```bash\npip install jubilant\n# or, if you use uv:\nuv add jubilant\n```\n\nYou also need to have Juju installed, as Jubilant directly calls the Juju CLI.\n\n---\n\n## Basic API Usage Example\n\n```python\nimport jubilant\n\njuju = jubilant.Juju()\njuju.deploy('snappass-test')\njuju.wait(jubilant.all_active)\n\n# Deploy just certain apps\njuju.wait(lambda status: jubilant.all_active(status, 'snappass-test', 'another-app'))\n```\n\n---\n\n## Sample Integration Test with Pytest\n\n### Add a Fixture (`conftest.py`):\n\n```python\nimport jubilant\nimport pytest\n\n@pytest.fixture(scope='module')\ndef juju():\n    with jubilant.temp_model() as juju:\n        yield juju\n```\n\n### Test Example (`test_deploy.py`):\n\n```python\nimport requests\ndef test_deploy(juju: jubilant.Juju):\n    juju.deploy('snappass-test')\n    status = juju.wait(jubilant.all_active)\n\n    # Test the workload by hitting the HTTP endpoint\n    address = status.apps['snappass-test'].units['snappass-test/0'].address\n    response = requests.get(f'http://{address}:5000/', timeout=10)\n    response.raise_for_status()\n    assert 'snappass' in response.text.lower()\n```\n\n---\n\n## Recommended Pytest Integration\n\n- Use module-scoped fixtures to create/destroy temporary models per test module (file).\n- Add a `--keep-models` option if you want to retain models after test runs (for debugging).\n- On test failure, you can capture Juju logs via `juju.debug_log()` for diagnosis.\n\n### Example Fixture with `--keep-models` and Debug Log\n\n```python\n@pytest.fixture(scope='module')\ndef juju(request: pytest.FixtureRequest):\n    keep_models = bool(request.config.getoption('--keep-models'))\n    with jubilant.temp_model(keep=keep_models) as juju:\n        juju.wait_timeout = 10 * 60\n        yield juju\n        if request.session.testsfailed:\n            log = juju.debug_log(limit=1000)\n            print(log, end='')\ndef pytest_addoption(parser):\n    parser.addoption('--keep-models', action='store_true', default=False,\n                     help='keep temporarily-created models')\n```\n\n---\n\n## Why Use Jubilant?\n- **Synchronous, Pythonic API**: No async/await headaches.\n- **Less brittle**: Avoids websocket timeouts seen in `python-libjuju`.\n- **CLI compatibility**: Maps closely to what charm and Juju CLI users do.\n- **pytest recommended**: Structured setup/teardown, powerful assertion system【3:0†source】【3:1†source】【3:6†source】.\n\n---\n\n## Additional Information\n\n- Jubilant’s API covers core Juju commands and supports advanced assertions or status checks via Python callables.\n- Migration guides from `pytest-operator` are provided in the official docs, making transition straightforward【3:1†source】.\n\nFor more details and further API docs, check [Jubilant’s documentation](https://documentation.ubuntu.com/jubilant/), the [PyPI page](https://pypi.org/project/jubilant/), or the [GitHub repository](https://github.com/canonical/jubilant).\n\n---\n\n**References:**\n- Official docs and usage:【3:0†source】【3:1†source】【3:2†source】【3:3†source】【3:6†source】","annotations":[{"text":"【3:0†source】","start_index":522,"end_index":534,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:2†source】","start_index":534,"end_index":546,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:1†source】","start_index":546,"end_index":558,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:0†source】","start_index":2911,"end_index":2923,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:1†source】","start_index":2923,"end_index":2935,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:6†source】","start_index":2935,"end_index":2947,"url_citation":{"title":"The Juju Insider #2 - juju - Charmhub","url":"https://discourse.charmhub.io/t/the-juju-insider-2/17964"}},{"text":"【3:1†source】","start_index":3207,"end_index":3219,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:0†source】","start_index":3507,"end_index":3519,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:1†source】","start_index":3519,"end_index":3531,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:2†source】","start_index":3531,"end_index":3543,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:3†source】","start_index":3543,"end_index":3555,"url_citation":{"title":"jubilant - Jubilant documentation","url":"https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/"}},{"text":"【3:6†source】","start_index":3555,"end_index":3567,"url_citation":{"title":"The Juju Insider #2 - juju - Charmhub","url":"https://discourse.charmhub.io/t/the-juju-insider-2/17964"}}]},"bing_searches":[{"text":"jubilant pytest-jubilant juju charm integration tests API usage examples","url":"https://www.bing.com/search?q=jubilant+pytest-jubilant+juju+charm+integration+tests+API+usage+examples"}],"annotations":null}
````


---

<sub>⏱️ 34s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/",
  "max_length": 10000
}
```

</details>

<details>
<summary>151 lines</summary>

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

It’s usually best to wait on workload status with the `all_*` and `any_*` helpers. However, if you want to wait specifically for unit agent status to be idle, you can use [`jubilant.all_agents_idle`](../../reference/jubilant/#jubilant.all_agents_idle "jubilant.all_agents_idl

<note>Content truncated. Call the fetch tool with a start_index of 10000 to get more content.</note>
```

</details>


---

<sub>⏱️ 46s</sub>

### ✅ `web_search`

**pytest-jubilant package pypi juju fixture**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest-jubilant package pypi juju fixture"
}
```

</details>

````
{"type":"text","text":{"value":"The `pytest-jubilant` package provides a pytest plugin for writing Juju integration tests using the `jubilant` library. It's designed to make the transition from `pytest-operator` easier and adds features on top of what you may be familiar with from `pytest-operator`【3:0†source】【3:1†source】.\n\n### The `juju` Fixture\n\n`pytest-jubilant` offers a special `juju` fixture with module (and model)-scoped behavior. By default, this fixture:\n\n- Uses a temporary Juju model for each test module.\n- Tears down (removes) the model automatically after the tests complete.\n\nYou use it like this in your test files:\n\n```python\nfrom jubilant import Juju, all_active\n\ndef test_deploy(juju: Juju):\n    juju.deploy(\"./foo.charm\", \"foo\")\n    juju.wait(lambda status: all_active(status, \"foo\"), timeout=1000)\n```\n\n#### Customizing Model Usage\n\nThe plugin offers command-line options for controlling model behavior:\n\n- `--model` lets you override the model name (helpful for debugging).\n- `--keep-models` prevents teardown, so temporary models stick around.\n- `--no-teardown` disables automatic teardown for an existing model you care about.\n- `--switch` switches you to the active test model in your Juju CLI during tests (useful for live status checks).\n\n#### temp_model_factory\n\nIf you need multiple models (for example, for cross-model relations), use the `temp_model_factory` fixture, which works under the hood of the main `juju` fixture. This lets you manage and control multiple concurrent models as needed:\n\n```python\nimport pytest\nfrom jubilant import Juju, all_active\n\n@pytest.fixture\ndef istio(temp_model_factory):\n    yield temp_model_factory.get_juju(suffix=\"istio\")\n\ndef test_cmr(juju: Juju, istio: Juju):\n    istio.deploy(\"istio-k8s\", \"istio\")\n    istio.wait(lambda status: all_active(status, \"istio\"), timeout=1000)\n    juju.deploy(\"./foo.charm\", \"foo\")\n    juju.wait(lambda status: all_active(status, \"foo\"), timeout=1000)\n    juju.cli(\"offer\", \"foo:bar\")\n    istio.cli(\"consume\", f\"{juju.model}:foo\")\n    istio.cli(\"relate\", \"istio\", \"foo:bar\")\n```\n\nThis test example will spin up two temporary Juju models, each with predictable names if you use custom suffixes, and will clean up by default after running the tests except if relevant command-line flags are passed【3:0†source】【3:3†source】.\n\n#### Usage with Pytest\n\nSimply install `pytest-jubilant` and `jubilant` from PyPI, and ensure Juju is installed on your system. Then, structure your tests around the provided fixtures for easy setup and teardown of models and deployments. More details and scenarios are provided in the official docs and GitHub repo【3:0†source】【3:1†source】【3:3†source】【3:6†source】.\n\n---\n\n#### Further Reading\n\n- [pytest-jubilant on PyPI](https://pypi.org/project/pytest-jubilant/)\n- [Jubilant documentation](https://documentation.ubuntu.com/jubilant/tutorial/getting-started/)\n- [Jubilant GitHub](https://github.com/canonical/jubilant/)\n\nLet me know if you need a more in-depth example or a deeper dive into custom waiting conditions and advanced usage!","annotations":[{"text":"【3:0†source】","start_index":267,"end_index":279,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:1†source】","start_index":279,"end_index":291,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:0†source】","start_index":2264,"end_index":2276,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:3†source】","start_index":2276,"end_index":2288,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}},{"text":"【3:0†source】","start_index":2606,"end_index":2618,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:1†source】","start_index":2618,"end_index":2630,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:3†source】","start_index":2630,"end_index":2642,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}},{"text":"【3:6†source】","start_index":2642,"end_index":2654,"url_citation":{"title":"Integration Tests | canonical/git-ubuntu-operator | DeepWiki","url":"https://deepwiki.com/canonical/git-ubuntu-operator/6.2.2-integration-tests"}}]},"bing_searches":[{"text":"pytest-jubilant package pypi juju fixture","url":"https://www.bing.com/search?q=pytest-jubilant+package+pypi+juju+fixture"}],"annotations":null}
````


---

<sub>⏱️ 1m 10s</sub>

### ✅ `web_fetch`

**https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/",
  "max_length": 8000
}
```

</details>

<details>
<summary>132 lines</summary>

```
Contents of https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/:
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
    
*   **include\_model** – If true and [`model`](#jubilant.

<note>Content truncated. Call the fetch tool with a start_index of 8000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 14s</sub>

### ✅ `web_fetch`

**https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 5000,
  "url": "https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/",
  "start_index": 8000
}
```

</details>

<details>
<summary>86 lines</summary>

```
Contents of https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/:
Juju.model "jubilant.Juju.model") is set, insert the `--model` argument after the first argument in _args_.
    
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
    
*   **overlays** – File paths of bundles to overlay on

<note>Content truncated. Call the fetch tool with a start_index of 13000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 50s</sub>

### 💬 Copilot

Now I have enough information to make the migration. Let me implement the changes:

---

<sub>⏱️ 1m 50s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-sonnet/uv.lock**

/tmp/saml-integrator-L1-sonnet/uv.lock (lines 1-30)

<details>
<summary>30 lines</summary>

```
1. version = 1
2. revision = 3
3. requires-python = ">=3.10"
4. resolution-markers = [
5.     "python_full_version >= '3.11'",
6.     "python_full_version < '3.11'",
7. ]
8. 
9. [[package]]
10. name = "allure-pytest"
11. version = "2.15.0"
12. source = { registry = "https://pypi.org/simple" }
13. dependencies = [
14.     { name = "allure-python-commons" },
15.     { name = "pytest" },
16. ]
17. sdist = { url = "https://files.pythonhosted.org/packages/44/f7/f0941b53dcf0fcac7a16a0c4e85985dbab2d2488423c33c757aacf16fcef/allure_pytest-2.15.0.tar.gz", hash = "sha256:b8f464d3bfeb6cb5e6a77e70eacd1aa3762133677cabece57a07c9f3bcd4b1e8", size = 17682, upload-time = "2025-07-22T11:12:17.735Z" }
18. wheels = [
19.     { url = "https://files.pythonhosted.org/packages/e5/e5/0bc588f0a1605435cd8811696c17d78e82fb84cc3933d57edda10bea4b5c/allure_pytest-2.15.0-py3-none-any.whl", hash = "sha256:f33c6ad242995bd27d2b467ee685772904d6941a6a6c9877657e0b8fe97a0ede", size = 12448, upload-time = "2025-07-22T11:12:16.583Z" },
20. ]
21. 
22. [[package]]
23. name = "allure-pytest-collection-report"
24. version = "0.1.0"
25. source = { git = "https://github.com/canonical/data-platform-workflows?subdirectory=python%2Fpytest_plugins%2Fallure_pytest_collection_report&rev=v24.0.0#8ec5cc7242d90d7ae1e125755297a97402e54584" }
26. dependencies = [
27.     { name = "allure-pytest" },
28.     { name = "pytest" },
29. ]
30.
```

</details>


---

<sub>⏱️ 1m 58s</sub>

### 💬 Copilot

Now let me make all the changes:

---

<sub>⏱️ 1m 58s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L1-sonnet/pyproject.toml**

/tmp/saml-integrator-L1-sonnet/pyproject.toml

```
File /tmp/saml-integrator-L1-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 1m 58s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L1-sonnet/pyproject.toml**

/tmp/saml-integrator-L1-sonnet/pyproject.toml

```
File /tmp/saml-integrator-L1-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 2m 12s</sub>

### 💬 Copilot

Now rewrite the integration conftest.py:

---

<sub>⏱️ 2m 12s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L1-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L1-sonnet/tests/integration/conftest.py

```
File /tmp/saml-integrator-L1-sonnet/tests/integration/conftest.py updated with changes.
```


---

<sub>⏱️ 2m 24s</sub>

### 💬 Copilot

Now rewrite the integration test file:

---

<sub>⏱️ 2m 24s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L1-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L1-sonnet/tests/integration/test_charm.py

```
File /tmp/saml-integrator-L1-sonnet/tests/integration/test_charm.py updated with changes.
```


---

<sub>⏱️ 2m 29s</sub>

### 💬 Copilot

Now update `uv.lock` by running `uv lock`:

---

<sub>⏱️ 2m 36s</sub>

### ✅ `bash`

**Update uv.lock with new dependencies**

$ cd /tmp/saml-integrator-L1-sonnet && uv lock 2>&1 | tail -20

<details>
<summary>21 lines</summary>

```
Removed pure-eval v0.2.3
Removed pyasn1 v0.6.1
Removed pyasn1-modules v0.4.2
Removed pymacaroons v0.13.0
Removed pynacl v1.6.1
Removed pyrfc3339 v1.1
Removed pytest-asyncio v0.21.2
Added pytest-jubilant v1.1
Removed pytest-operator v0.43.2
Removed python-dateutil v2.9.0.post0
Removed pytz v2025.2
Removed requests-oauthlib v2.0.0
Removed rsa v4.9.1
Removed six v1.17.0
Removed stack-data v0.6.3
Removed toposort v1.10
Removed traitlets v5.14.3
Removed typing-inspect v0.9.0
Removed wcwidth v0.2.14
Removed websockets v15.0.1
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 41s</sub>

### ✅ `bash`

**Verify new packages in lockfile**

$ cd /tmp/saml-integrator-L1-sonnet && grep -E "jubilant|pytest-jubilant|juju" uv.lock | grep "^name" | head -20

```
name = "jubilant"
name = "pytest-jubilant"
<exited with exit code 0>
```


---

<sub>⏱️ 2m 45s</sub>

### 💬 Copilot

Good. Now let's verify the lint check passes on the modified files:

---

<sub>⏱️ 3m 0s</sub>

### ✅ `bash`

**Run ruff lint on integration tests**

$ cd /tmp/saml-integrator-L1-sonnet && uv run --group lint ruff check tests/integration/ tests/conftest.py 2>&1

<details>
<summary>7 lines</summary>

```
Output too large to read at once (156.9 KB). Saved to: /tmp/copilot-tool-output-1772837412705-1rudw9.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: .venv
⠋ Prepa
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 4s</sub>

### ✅ `bash`

**Check for lint errors**

$ cd /tmp/saml-integrator-L1-sonnet && uv run --group lint ruff check tests/integration/ tests/conftest.py 2>&1 | grep -E "error|warning|tests/" | head -30

```
warning: Selection `CPY` has no effect because preview is not enabled.
<exited with exit code 0>
```


---

<sub>⏱️ 3m 10s</sub>

### ✅ `bash`

**Run mypy on integration tests**

$ cd /tmp/saml-integrator-L1-sonnet && uv run --group lint mypy tests/integration/ 2>&1 | tail -20

```
Success: no issues found in 4 source files
<exited with exit code 0>
```


---

<sub>⏱️ 3m 15s</sub>

### 💬 Copilot

All checks pass. Let me do a final review of the changed files:

---

<sub>⏱️ 3m 15s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L1-sonnet/tests/integration/conftest.py

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

<sub>⏱️ 3m 15s</sub>

### ✅ `view`

**/tmp/saml-integrator-L1-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L1-sonnet/tests/integration/test_charm.py

<details>
<summary>44 lines</summary>

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
25.     juju.wait(jubilant.all_active, error=jubilant.any_error)
26. 
27. 
28. @pytest.mark.abort_on_fail
29. def test_relation(juju: jubilant.Juju, app: str, any_charm: str):
30.     """Check that the charm is active once related to another charm.
31. 
32.     Assume that the charm has already been built and is running.
33.     """
34.     juju.integrate(f"{any_charm}:require-saml", f"{app}:saml")
35.     juju.config(
36.         app,
37.         {
38.             "entity_id": "https://login.staging.ubuntu.com",
39.             "fingerprint": "",
40.             "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
41.         },
42.     )
43.     juju.wait(jubilant.all_active, error=jubilant.any_error)
44.
```

</details>


---

<sub>⏱️ 3m 24s</sub>

### 💬 Copilot

The migration is complete. Here's a summary of all changes made:

**`pyproject.toml`** (dependency groups):
- `integration`: removed `juju`, `pytest-asyncio`, `pytest-operator`; added `jubilant`, `pytest-jubilant`
- `lint`: removed `pytest-asyncio`, `pytest-operator`; added `jubilant`, `pytest-jubilant`

**`tests/integration/conftest.py`**:
- Removed `pytest_asyncio` and `OpsTest` imports; added `jubilant`
- Converted `async` fixtures to sync `@fixture` functions
- Replaced `ops_test: OpsTest` with `juju: jubilant.Juju` (provided by `pytest-jubilant`)
- Fixtures now yield app name strings instead of `ops.Application` objects

**`tests/integration/test_charm.py`**:
- Removed `ops`, `OpsTest` imports; added `jubilant`
- Removed `async`/`await` and `@pytest.mark.asyncio`
- Replaced `app: ops.Application` → `app: str`, `any_charm: ops.Application` → `any_charm: str`
- Replaced `app.set_config(...)` → `juju.config(app, {...})`
- Replaced `model.wait_for_idle(status=..., raise_on_error=True)` → `juju.wait(jubilant.all_active, error=jubilant.any_error)`
- Replaced `model.add_relation(...)` → `juju.integrate(...)`
- Removed manual workload status assertions (covered by `juju.wait`)

**`uv.lock`**: regenerated to reflect updated dependencies.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
