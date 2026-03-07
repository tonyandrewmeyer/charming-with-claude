# 🤖 Copilot CLI Session

> **Session ID:** `e5d721d2-c04c-47e7-82a0-ea8f30899b35`
> **Duration:** 2m 49s

<sub>⏱️ 4s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

Before starting, read the jubilant documentation, particularly the migration guide, at https://documentation.ubuntu.com/jubilant. The reference documentation covers the full API.

---

<sub>⏱️ 12s</sub>

### 📦 task (Completed)

### ✅ `bash`

**List all Python files in integration tests directory**

$ find /tmp/saml-integrator-L2-sonnet/tests/integration -type f -name "*.py" | head -20

```
/tmp/saml-integrator-L2-sonnet/tests/integration/conftest.py
/tmp/saml-integrator-L2-sonnet/tests/integration/test_charm.py
/tmp/saml-integrator-L2-sonnet/tests/integration/any_charm.py
/tmp/saml-integrator-L2-sonnet/tests/integration/__init__.py
<exited with exit code 0>
```


### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tests/integration**

/tmp/saml-integrator-L2-sonnet/tests/integration

```
__init__.py
any_charm.py
conftest.py
test_charm.py
```


### ✅ `glob`

**/tmp/saml-integrator-L2-sonnet/tests/integration/**/*.py**

"/tmp/saml-integrator-L2-sonnet/tests/integration/**/*.py"

```
No files matched the pattern.
```


### 💬 Copilot

Now let me read all the test files and config files:

### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L2-sonnet/tests/integration/conftest.py

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


### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L2-sonnet/tests/integration/test_charm.py

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


### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tests/integration/any_charm.py**

/tmp/saml-integrator-L2-sonnet/tests/integration/any_charm.py

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


### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tests/integration/__init__.py**

/tmp/saml-integrator-L2-sonnet/tests/integration/__init__.py

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
```


### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/pyproject.toml**

/tmp/saml-integrator-L2-sonnet/pyproject.toml

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


### ✅ `bash`

**Find tox configuration files**

$ find /tmp/saml-integrator-L2-sonnet -name "tox.ini" -o -name "tox.toml" | head -5

```
/tmp/saml-integrator-L2-sonnet/tox.toml
<exited with exit code 0>
```


### 💬 Copilot

Now let me read the tox.toml file:

### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tox.toml**

/tmp/saml-integrator-L2-sonnet/tox.toml

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


### 💬 Copilot

Perfect! Let me create a comprehensive summary document. First, let me check if there are any other test-related files or helper modules I might have missed:

### ✅ `bash`

**List all test Python files**

$ find /tmp/saml-integrator-L2-sonnet/tests -type f -name "*.py" | sort

<details>
<summary>14 lines</summary>

```
/tmp/saml-integrator-L2-sonnet/tests/__init__.py
/tmp/saml-integrator-L2-sonnet/tests/conftest.py
/tmp/saml-integrator-L2-sonnet/tests/integration/__init__.py
/tmp/saml-integrator-L2-sonnet/tests/integration/any_charm.py
/tmp/saml-integrator-L2-sonnet/tests/integration/conftest.py
/tmp/saml-integrator-L2-sonnet/tests/integration/test_charm.py
/tmp/saml-integrator-L2-sonnet/tests/interface/conftest.py
/tmp/saml-integrator-L2-sonnet/tests/interface/test_saml.py
/tmp/saml-integrator-L2-sonnet/tests/unit/__init__.py
/tmp/saml-integrator-L2-sonnet/tests/unit/test_charm.py
/tmp/saml-integrator-L2-sonnet/tests/unit/test_charm_state.py
/tmp/saml-integrator-L2-sonnet/tests/unit/test_library_saml.py
/tmp/saml-integrator-L2-sonnet/tests/unit/test_saml.py
<exited with exit code 0>
```

</details>


### 💬 Copilot

Let me also check the main conftest.py in tests/ and the lib structure:

### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tests/conftest.py**

/tmp/saml-integrator-L2-sonnet/tests/conftest.py

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


### ✅ `bash`

**Check library directory structure**

$ ls -la /tmp/saml-integrator-L2-sonnet/lib/charms/saml_integrator/v0/ 2>/dev/null || echo "Directory not found"

```
total 20
drwxrwxr-x 2 ubuntu ubuntu  4096 Mar  7 11:51 .
drwxrwxr-x 3 ubuntu ubuntu  4096 Mar  7 11:51 ..
-rw-rw-r-- 1 ubuntu ubuntu 11673 Mar  7 11:51 saml.py
<exited with exit code 0>
```


### 💬 Copilot

Now let me check the library file that's used in integration tests:

### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/lib/charms/saml_integrator/v0/saml.py**

/tmp/saml-integrator-L2-sonnet/lib/charms/saml_integrator/v0/saml.py (lines 1-100)

<details>
<summary>100 lines</summary>

````
1. #!/usr/bin/env python3
2. 
3. # Copyright 2025 Canonical Ltd.
4. # Licensed under the Apache2.0. See LICENSE file in charm source for details.
5. 
6. """Library to manage the relation data for the SAML Integrator charm.
7. 
8. This library contains the Requires and Provides classes for handling the relation
9. between an application and a charm providing the `saml`relation.
10. It also contains a `SamlRelationData` class to wrap the SAML data that will
11. be shared via the relation.
12. 
13. ### Requirer Charm
14. 
15. ```python
16. 
17. from charms.saml_integrator.v0 import SamlDataAvailableEvent, SamlRequires
18. 
19. class SamlRequirerCharm(ops.CharmBase):
20.     def __init__(self, *args):
21.         super().__init__(*args)
22.         self.saml = saml.SamlRequires(self)
23.         self.framework.observe(self.saml.on.saml_data_available, self._handler)
24.         ...
25. 
26.     def _handler(self, events: SamlDataAvailableEvent) -> None:
27.         ...
28. 
29. ```
30. 
31. As shown above, the library provides a custom event to handle the scenario in
32. which new SAML data has been added or updated.
33. 
34. ### Provider Charm
35. 
36. Following the previous example, this is an example of the provider charm.
37. 
38. ```python
39. from charms.saml_integrator.v0 import SamlDataAvailableEvent, SamlRequires
40. 
41. class SamlRequirerCharm(ops.CharmBase):
42.     def __init__(self, *args):
43.         super().__init__(*args)
44.         self.saml = SamlRequires(self)
45.         self.framework.observe(self.saml.on.saml_data_available, self._on_saml_data_available)
46.         ...
47. 
48.     def _on_saml_data_available(self, events: SamlDataAvailableEvent) -> None:
49.         ...
50. 
51.     def __init__(self, *args):
52.         super().__init__(*args)
53.         self.saml = SamlProvides(self)
54. 
55. ```
56. The SamlProvides object wraps the list of relations into a `relations` property
57. and provides an `update_relation_data` method to update the relation data by passing
58. a `SamlRelationData` data object.
59. Additionally, SamlRelationData can be used to directly parse the relation data with the
60. class method `from_relation_data`.
61. """
62. 
63. # The unique Charmhub library identifier, never change it
64. LIBID = "511cdfa7de3d43568bf9b512f9c9f89d"
65. 
66. # Increment this major API version when introducing breaking changes
67. LIBAPI = 0
68. 
69. # Increment this PATCH version before using `charmcraft publish-lib` or reset
70. # to 0 if you are raising the major API version
71. LIBPATCH = 11
72. 
73. # pylint: disable=wrong-import-position
74. # ruff: noqa: E402
75. import re
76. import typing
77. 
78. import ops
79. from pydantic import AnyHttpUrl, BaseModel, Field, TypeAdapter
80. 
81. DEFAULT_RELATION_NAME = "saml"
82. 
83. 
84. class SamlEndpoint(BaseModel):
85.     """Represent a SAML endpoint.
86. 
87.     Attrs:
88.         name: Endpoint name.
89.         url: Endpoint URL.
90.         binding: Endpoint binding.
91.         response_url: URL to address the response to.
92.     """
93. 
94.     name: str = Field(..., min_length=1)
95.     url: typing.Optional[AnyHttpUrl] = None
96.     binding: str = Field(..., min_length=1)
97.     response_url: typing.Optional[AnyHttpUrl] = None
98. 
99.     def to_relation_data(self) -> typing.Dict[str, str]:
100.         """Convert an instance of SamlEndpoint to the relation representation.
````

</details>


### 💬 Copilot

Perfect! Now I have all the information needed. Let me create a comprehensive summary:

## Integration Tests Exploration - Complete Analysis

### 1. **Directory Structure - Integration Tests Files**

```
/tmp/saml-integrator-L2-sonnet/tests/integration/
├── __init__.py                    (empty, just copyright header)
├── conftest.py                    (pytest fixtures for integration tests)
├── test_charm.py                  (main integration test suite)
└── any_charm.py                   (helper script for testing with any-charm)
```

---

### 2. **Complete Content of Integration Test Files**

#### **conftest.py** (Lines 1-58)
```python
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the SAML Integrator charm integration tests."""

import json
from pathlib import Path

import pytest_asyncio
import yaml
from pytest import Config, fixture
from pytest_operator.plugin import OpsTest


@fixture(scope="module", name="app_name")
def app_name_fixture():
    """Provide app name from the metadata."""
    metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
    yield metadata["name"]


@pytest_asyncio.fixture(scope="module")
async def app(ops_test: OpsTest, pytestconfig: Config, app_name: str):
    """SAML Integrator charm used for integration testing.

    Build the charm and deploy it along with Anycharm.
    """
    charm = pytestconfig.getoption("--charm-file")
    assert ops_test.model
    application = await ops_test.model.deploy(
        f"./{charm}",
        application_name=app_name,
    )
    yield application


@pytest_asyncio.fixture(scope="module")
async def any_charm(ops_test: OpsTest):
    """SAML Integrator charm used for integration testing.

    Build the charm and deploy it along with Anycharm.
    """
    path_lib = "lib/charms/saml_integrator/v0/saml.py"
    saml_lib = Path(path_lib).read_text(encoding="utf8")
    any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
    src_overwrite = {
        "saml.py": saml_lib,
        "any_charm.py": any_charm_script,
    }
    assert ops_test.model
    application = await ops_test.model.deploy(
        "any-charm",
        application_name="any",
        channel="beta",
        config={"python-packages": "pydantic\>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
    )
    yield application
```

**Fixtures Summary:**
- `app_name_fixture`: Loads charm name from metadata.yaml (module scope)
- `app`: Deploys the SAML Integrator charm via ops_test (module scope)
  - Takes `--charm-file` from pytest config
  - Uses `ops_test.model.deploy()` to deploy the charm
- `any_charm`: Deploys any-charm from Charmhub for relation testing (module scope)
  - Injects SAML library and any_charm.py script via `src-overwrite` config
  - Requires `pydantic\>=2.12.5` 
  - Uses beta channel

---

#### **test_charm.py** (Lines 1-52)
```python
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator charm integration tests."""

import ops
import pytest
from pytest_operator.plugin import OpsTest


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_active(ops_test: OpsTest, app: ops.Application):
    """Check that the charm is active.

    Assume that the charm has already been built and is running.
    """
    await app.set_config(  # type: ignore[attr-defined]
        {
            "entity_id": "https://login.staging.ubuntu.com",
            "fingerprint": "",
            "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
        }
    )
    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
    assert ops_test.model
    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
    assert app.units[0].workload_status == status_name  # type: ignore


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_relation(ops_test: OpsTest, app: ops.Application, any_charm: ops.Application):
    """Check that the charm is active once related to another charm.

    Assume that the charm has already been built and is running.
    """
    relation_name = f"{app.name}:saml"
    assert ops_test.model
    await ops_test.model.add_relation(f"{any_charm.name}:require-saml", relation_name)
    await app.set_config(  # type: ignore[attr-defined]
        {
            "entity_id": "https://login.staging.ubuntu.com",
            "fingerprint": "",
            "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
        }
    )
    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
    assert app.units[0].workload_status == status_name  # type: ignore
```

**Tests Summary:**
1. **test_active** (Lines 14-29):
   - Tests charm activation with SAML config
   - Sets config: entity_id, fingerprint, metadata_url
   - Verifies workload reaches `ActiveStatus`
   - Uses `@pytest.mark.abort_on_fail` to stop on failure

2. **test_relation** (Lines 32-51):
   - Tests charm activation when related to another charm
   - Deploys any-charm and creates relation on saml interface
   - Verifies charm reaches `ActiveStatus` with relation active
   - Also uses `@pytest.mark.abort_on_fail`

---

#### **any_charm.py** (Lines 1-29)
```python
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# pylint: disable=import-error,consider-using-with,no-member

"""This code snippet is used to be loaded into any-charm which is used for integration tests."""

from any_charm_base import AnyCharmBase

import saml


class AnyCharm(AnyCharmBase):  # pylint: disable=too-few-public-methods
    """Execute a simple charm workload to test the saml relation.

    Attrs:
        saml: The attribute that mimics a real SAML relation.
    """

    def __init__(self, *args, **kwargs):
        """Init function for the class.

        Args:
            args: Variable list of positional arguments passed to the parent constructor.
            kwargs: Variable list of positional keyword arguments passed to the parent constructor.
        """
        super().__init__(*args, **kwargs)
        self.saml = saml.SamlRequires(self)
```

**Purpose:** Test helper that loads into any-charm charm instance
- Extends `AnyCharmBase` 
- Uses `SamlRequires` from the SAML library to test the requires side of the relation
- Gets injected via src-overwrite in conftest fixture

---

#### **tests/conftest.py** (Lines 1-15)
```python
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Test fixtures."""

import pytest


def pytest_addoption(parser: pytest.Parser):
    """Add test arguments.

    Args:
        parser: pytest parser.
    """
    parser.addoption("--charm-file", action="store")
```

**Purpose:** Root conftest for all tests
- Adds custom pytest option: `--charm-file` to specify the charm file path to deploy

---

### 3. **Testing Dependencies - pyproject.toml**

#### **Dependency Groups (Lines 59-66):**
```toml
integration = [
   "allure-pytest\>=2.8.18",
   "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
   "juju",
   "pytest",
   "pytest-asyncio",
   "pytest-operator",
]
```

**Key Dependencies:**
- **pytest-operator**: Provides `OpsTest` fixture for Juju charm deployment & testing
- **juju**: Python Juju library for model management
- **pytest-asyncio**: Async test support (all fixtures use `@pytest_asyncio.fixture`)
- **pytest**: Base testing framework
- **allure-pytest**: Test reporting/allure integration

#### **Lint Dependencies (Lines 29-42):**
```toml
lint = [
   "codespell",
   "mypy",
   "ops-scenario",
   "pep8-naming",
   "pytest",
   "pytest-asyncio",
   "pytest-operator",
   "requests",
   "ruff",
   "types-mock",
   "types-pyyaml",
   "types-requests",
]
```

---

### 4. **Testing Configuration - tox.toml**

#### **Integration Environment (Lines 129-144):**
```toml
[env.integration]
description = "Run integration tests"
commands = [
  [
    "pytest",
    "-v",
    "--tb",
    "native",
    "--ignore={[vars]tst_path}unit",
    "--ignore={[vars]tst_path}interface",
    "--log-cli-level=INFO",
    "-s",
    { replace = "posargs", extend = "true" },
  ],
]
dependency_groups = [ "integration" ]
```

**Run Command:**
```bash
pytest -v --tb native --ignore=tests/unit --ignore=tests/interface --log-cli-level=INFO -s tests/integration
```

#### **Key Variables (Lines 162-167):**
```toml
[vars]
src_path = "{toxinidir}/src/"
tst_path = "{toxinidir}/tests/"
lib_path = "{toxinidir}/lib/charms/saml_integrator"
all_path = [ "{toxinidir}/src/", "{toxinidir}/tests/", "{toxinidir}/lib/charms/saml_integrator" ]
```

---

### 5. **Patterns & Key Design Elements**

#### **Fixtures Pattern:**
- **Module-scoped fixtures**: Both `app` and `any_charm` are module-scoped (deploy once, use in all tests)
- **Async fixtures**: All use `@pytest_asyncio.fixture` with `async def`
- **Parametrization**: Fixtures use `ops_test` (pytest-operator provided), `pytestconfig` for CLI args

#### **Testing Pattern:**
- **Async tests**: All tests are `async def` with `@pytest.mark.asyncio`
- **Abort on fail**: Uses `@pytest.mark.abort_on_fail` to fail fast
- **Config-driven**: Tests set charm config and verify state transitions
- **Relation testing**: Tests create relations and verify behavior with related charms

#### **Configuration Pattern:**
- Charm config set via `app.set_config(dict)` 
- SAML config parameters:
  - `entity_id`: IdP entity identifier
  - `fingerprint`: Certificate fingerprint (empty in tests)
  - `metadata_url`: SAML metadata endpoint

#### **Deployment Pattern:**
- **Main charm**: Deployed from local charm file via `--charm-file` CLI option
- **Test charm**: Uses `any-charm` from Charmhub (beta channel)
- **Code injection**: SAML library & test code injected via `src-overwrite` config

#### **Fixture Dependencies:**
```
test_active(ops_test, app) \<- app(ops_test, pytestconfig, app_name)
                                                 ^
                                          app_name(file.read)

test_relation(ops_test, app, any_charm) \<- app(...)
                                       \<- any_charm(ops_test)
```

#### **Helper Functions in conftest:**
- None - pure fixture definitions, no helper utility functions

---

### 6. **Summary Table**

| Aspect | Details |
|--------|---------|
| **Test Files** | 1 test file: `test_charm.py` with 2 tests |
| **Fixtures** | 3 fixtures: `app_name`, `app`, `any_charm` (all module-scoped) |
| **Test Types** | 2 async integration tests with status checks |
| **Key Library** | SAML charm relation library (v0) at `lib/charms/saml_integrator/v0/saml.py` |
| **Core Dependencies** | pytest-operator, juju, pytest-asyncio, pytest |
| **Config Method** | CLI option `--charm-file` + pytestconfig |
| **Test Patterns** | Async/await, fixture injection, relation testing, status verification |


---

<sub>⏱️ 13s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://documentation.ubuntu.com/jubilant",
  "max_length": 20000
}
```

</details>

<details>
<summary>23 lines</summary>

```
Contents of https://documentation.ubuntu.com/jubilant:
Jubilant is a Python library that wraps the [Juju](https://juju.is/) CLI, primarily for use in charm integration tests. It provides methods that map 1:1 to Juju CLI commands, but with a type-annotated, Pythonic interface.

You should consider switching to Jubilant if your integration tests currently use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) (and they probably do). Jubilant has an API you’ll pick up quickly, and it avoids some of the pain points of [python-libjuju](https://github.com/juju/python-libjuju/), such as websocket failures and having to use `async`. Read our [design goals](explanation/design-goals/).

Jubilant 1.0.0 was released in April 2025. We will avoid making breaking changes to the API after this point.

The library provides:

*   The main [`jubilant.Juju`](reference/jubilant/#jubilant.Juju "jubilant.Juju") class, with methods such as [`deploy`](reference/jubilant/#jubilant.Juju.deploy "jubilant.Juju.deploy") and [`integrate`](reference/jubilant/#jubilant.Juju.integrate "jubilant.Juju.integrate")
    
*   The [`Juju.wait`](reference/jubilant/#jubilant.Juju.wait "jubilant.Juju.wait") method, which waits for a condition such as “all apps active”
    
*   Status helpers such as [`jubilant.all_active`](reference/jubilant/#jubilant.all_active "jubilant.all_active"), for use with `Juju.wait`
    
*   Context managers such as [`jubilant.temp_model`](reference/jubilant/#jubilant.temp_model "jubilant.temp_model"), for use in test setup and teardown
    

## In this documentation[¶](#in-this-documentation "Link to this heading")

**Start here**: a hands-on introduction to Jubilant, including how to write a charm integration test

## Releases[¶](#releases "Link to this heading")

[Jubilant releases](https://github.com/canonical/jubilant/releases) are tracked on GitHub, and use [semantic versioning](https://semver.org/). To get notified when there’s a new release, watch the [Jubilant repository](https://github.com/canonical/jubilant).

## Project and community[¶](#project-and-community "Link to this heading")

Jubilant is a member of the Ubuntu family. It’s an open source project ([Apache license](https://www.apache.org/licenses/LICENSE-2.0)) that warmly welcomes community contributions, suggestions, fixes and constructive feedback.

*   [Report a bug](https://github.com/canonical/jubilant/issues)
    
*   [Contribute](https://github.com/canonical/jubilant?tab=readme-ov-file#contributing-and-developing)
    
*   [Code of conduct](https://ubuntu.com/community/ethos/code-of-conduct)
    

For support, join [Charm Development](https://matrix.to/#/#charmhub-charmdev:ubuntu.com) on Matrix. You’ll be able to chat with the maintainers of Jubilant (the Canonical Charm Tech team) and a friendly community of charm developers!

## Looking for more?[¶](#looking-for-more "Link to this heading")

The Ops repository has several [demo charms](https://github.com/canonical/operator/tree/main/examples) that you can experiment with. The demo charms use Jubilant for their integration tests.

To follow along with updates and tips about charm development, join our [Discourse forum](https://discourse.charmhub.io/).

[Learn more about the Juju ecosystem](https://juju.is/docs)
```

</details>


---

<sub>⏱️ 1m 0s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/",
  "max_length": 20000
}
```

</details>

<details>
<summary>243 lines</summary>

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
    old \= juju.model\_config()\['update-status-hook-interval'\]
    juju.model\_config({'update-status-hook-interval': '10s'})
    try:
        yield
    finally:
        juju.model\_config({'update-status-hook-interval': old})

## See more[¶](#see-more "Link to this heading")

*   [Jubilant’s API reference](../../reference/jubilant/)
    
*   [This discourse-k8s migration PR](https://github.com/canonical/discourse-k8s-operator/pull/326) shows how we migrated a real charm’s integration tests
```

</details>


---

<sub>⏱️ 1m 1s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant/reference/jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://documentation.ubuntu.com/jubilant/reference/jubilant/",
  "max_length": 20000
}
```

</details>

<details>
<summary>324 lines</summary>

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

Run the command on the remote target specified.

You must specify either _machine_ or _unit_, but not both.

Note: this method does not support running a command on multiple units at once. If you need that, let us know, and we’ll consider adding it with a new `exec_multiple` method or similar.

Parameters:

*   **command** – Command to run. Because the command is executed using the shell, arguments may also be included here as a single string, for example `juju.exec('echo foo', ...)`.
    
*   **args** – Arguments of the command.
    
*   **machine** – ID of machine to run the command on, for example `0`, `"0"`, or `"0/lxd/0"`.
    
*   **unit** – Name of unit to run the command on, for example `mysql/0` or `mysql/leader`.
    
*   **wait** – Maximum time to wait for command to finish; `TimeoutError` is raised if this is reached. Juju’s default is to wait 5 minutes.
    

Returns:

The task created to run the command, including logs, failure message, and so on.

Raises:

*   **ValueError** – if the machine or unit doesn’t exist.
    
*   [**TaskError**](#jubilant.TaskError "jubilant.TaskError") – if the command failed.
    
*   **TimeoutError** – if _wait_ was specified and the wait time was reached.
    

grant\_secret(

_identifier: str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")_,

_app: str | Iterable\[str\]_,

) → None[¶](#jubilant.Juju.grant_secret "Link to this definition")

Grant access to a secret for one or more applications.

Parameters:

*   **identifier** – The name or URI of the secret to grant access to.
    
*   **app** – Name or names of applications to grant access to.
    

integrate(

_app1: str_,

_app2: str_,

_\*_,

_via: str | Iterable\[str\] | None \= None_,

) → None[¶](#jubilant.Juju.integrate "Link to this definition")

Integrate two applications, creating a relation between them.

The order of _app1_ and _app2_ is not significant. Each of them should be in the format `<application>[:<endpoint>]`. The endpoint is only required if there’s more than one possible integration between the two applications.

To integrate an application in the current model with an application in another model (cross-model), prefix _app1_ or _app2_ with `<model>.`. To integrate with an application on another controller, _app1_ or _app2_ must be an offer endpoint. See `juju integrate --help` for details.

Parameters:

*   **app1** – One of the applications (and endpoints) to integrate.
    
*   **app2** – The other of the applications (and endpoints) to integrate.
    
*   **via** – Inform the offering side (the remote application) of the source of traffic, to enable network ports to be opened. This is in CIDR notation, for example `192.0.2.0/24`.
    

model: str | None[¶](#jubilant.Juju.model "Link to this definition")

If not None, operate on this Juju model, otherwise use the current Juju model.

If the model is in another controller, prefix the model name with `<controller>:`; for example, `juju = jubilant.Juju(model='mycontroller:my-model')`.

model\_config() → Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\][¶](#jubilant.Juju.model_config "Link to this definition")

model\_config(

_values: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\]_,

_\*_,

_reset: str | Iterable\[str\] \= ()_,

) → None

model\_config(_\*_, _reset: str | Iterable\[str\]_) → None

Get or set the configuration of the model.

If called with no arguments, get the model config and return it.

If called with the _values_ or _reset_ arguments, set the model config values and return None, and reset any keys in _reset_ to their defaults.

Parameters:

*   **values** – Mapping of model config names to values to set, for example `{'update-status-hook-interval': '10s'}`.
    
*   **reset** – Key or list of keys to reset to their defaults.
    

model\_constraints() → Mapping\[str, bool | int | float | str\][¶](#jubilant.Juju.model_constraints "Link to this definition")

model\_constraints(

_constraints: Mapping\[str, bool | int | float | str\]_,

) → None

Get or set machine constraints on a model.

If called with no arguments, get the model constraints. If called with the _constraints_ argument, set the model constraints and return None.

Parameters:

**constraints** – Model constraints to set, for example, `{'mem': '8G', 'cores': 4}`.

offer(

_app: str_,

_\*_,

_controller: str | None \= None_,

_endpoint: str | Iterable\[str\]_,

_name: str | None \= None_,

) → None[¶](#jubilant.Juju.offer "Link to this definition")

Offer application endpoints for use in other models.

Examples:

juju.offer('mysql', endpoint\='db')
juju.offer('mymodel.mysql', endpoint\=\['db', 'log'\], name\='altname')

Parameters:

*   **app** – Application name to offer endpoints for. May include a dotted model name, for example `mymodel.mysql`.
    
*  

<note>Content truncated. Call the fetch tool with a start_index of 20000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 7s</sub>

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

<sub>⏱️ 1m 6s</sub>

### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/pyproject.toml**

/tmp/saml-integrator-L2-sonnet/pyproject.toml

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

<sub>⏱️ 1m 6s</sub>

### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tox.toml**

/tmp/saml-integrator-L2-sonnet/tox.toml

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

<sub>⏱️ 1m 11s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant/reference/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://documentation.ubuntu.com/jubilant/reference/"
}
```

</details>

```
Contents of https://documentation.ubuntu.com/jubilant/reference/:
Copyright © 2026, Canonical Ltd.

Last updated on Nov 13, 2025
```


---

<sub>⏱️ 1m 15s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant/how-to/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://documentation.ubuntu.com/jubilant/how-to/"
}
```

</details>

<details>
<summary>6 lines</summary>

```
Contents of https://documentation.ubuntu.com/jubilant/how-to/:
[Back to top](#)

These guides walk you through various tasks you can perform with Jubilant.

## Migrate from pytest-operator to Jubilant[¶](#migrate-from-pytest-operator-to-jubilant "Link to this heading")

This guide shows how to migrate your existing charm integration tests from [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) and [python-libjuju](https://github.com/juju/python-libjuju) to Jubilant.

*   [Migrate from pytest-operator to Jubilant](migrate-from-pytest-operator/)
```

</details>


---

<sub>⏱️ 1m 15s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/pytest-jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://pypi.org/project/pytest-jubilant/"
}
```

</details>

```
Contents of https://pypi.org/project/pytest-jubilant/:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 1m 19s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/jubilant/blob/main/README.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/jubilant/blob/main/README.md"
}
```

</details>

<details>
<summary>61 lines</summary>

````
Contents of https://github.com/canonical/jubilant/blob/main/README.md:
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

<sub>⏱️ 1m 23s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/pytest-jubilant**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://github.com/canonical/pytest-jubilant"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/pytest-jubilant - status code 404
```


---

<sub>⏱️ 1m 38s</sub>

### ✅ `web_search`

**pytest-jubilant package charm integration tests canonical**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest-jubilant package charm integration tests canonical"
}
```

</details>

````
{"type":"text","text":{"value":"The `pytest-jubilant` package does not exist as a separate package; instead, integration tests for Canonical charms are now recommended to use the `jubilant` library in combination with `pytest`. Jubilant is a modern, Pythonic wrapper around the Juju CLI, specifically designed to make integration testing of charms straightforward. Its main features are:\n\n- 1:1 mapping to Juju CLI commands, but with a more Pythonic interface.\n- Type annotations and simple API (no async programming required).\n- Automatic setup and teardown of temporary Juju models for test isolation.\n- Avoids common pitfalls from previous libraries (like `python-libjuju`'s websocket issues).\n- Designed as a drop-in replacement for `pytest-operator` when writing Juju charm integration tests.\n\n## Example: Integration Test Using Jubilant\n\nHere's a typical integration test setup as recommended by Canonical:\n\n**conftest.py**\n```python\nimport pytest\nimport jubilant\n\n@pytest.fixture(scope='module')\ndef juju():\n    with jubilant.temp_model() as juju:\n        yield juju\n```\n\n**test_deploy.py**\n```python\nimport jubilant\nimport requests\n\ndef test_deploy(juju: jubilant.Juju):\n    juju.deploy('snappass-test')  # Deploy the charm (any charm name)\n    status = juju.wait(jubilant.all_active)  # Wait until deployment is 'active'\n    address = status.apps['snappass-test'].units['snappass-test/0'].address\n    response = requests.get(f'http://{address}:5000/', timeout=10)\n    response.raise_for_status()\n    assert 'snappass' in response.text.lower()\n```\n\n- The `juju` fixture ensures tests are run in isolated, ephemeral Juju models.\n- The API is intentionally similar to the Juju CLI for familiarity.\n- You still use pytest as the test runner, with all the features of `pytest` (assertions, fixtures, setup/teardown, etc.).\n\n## Migration from pytest-operator\n\nCanonical provides migration guides for moving from `pytest-operator` and `python-libjuju` to `jubilant` due to its simpler, more reliable API and improved developer experience【3:2†How-to guides - Jubilant documentation】【3:9†Jubilant documentation】【3:4†How to migrate from pytest-operator to Jubilant】.\n\n## Further Resources\n\n- [Jubilant GitHub page with usage examples](https://github.com/canonical/jubilant)【3:0†GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...】\n- [Official documentation and how-to guides](https://documentation.ubuntu.com/jubilant/how-to/)\n- [Migration from pytest-operator](https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/)\n\n**Recommendation:** If you’re writing or updating charm integration tests at Canonical, use the `jubilant` package in your test suite. Install it with `pip install jubilant`, then follow the documented approach using pytest and jubilant’s fixtures【3:1†jubilant · PyPI】.","annotations":[{"text":"【3:2†How-to guides - Jubilant documentation】","start_index":2007,"end_index":2051,"url_citation":{"title":"How-to guides - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/how-to/"}},{"text":"【3:9†Jubilant documentation】","start_index":2051,"end_index":2079,"url_citation":{"title":"Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/"}},{"text":"【3:4†How to migrate from pytest-operator to Jubilant】","start_index":2079,"end_index":2132,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/"}},{"text":"【3:0†GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...】","start_index":2240,"end_index":2320,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:1†jubilant · PyPI】","start_index":2788,"end_index":2809,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}}]},"bing_searches":[{"text":"pytest-jubilant package charm integration tests canonical","url":"https://www.bing.com/search?q=pytest-jubilant+package+charm+integration+tests+canonical"}],"annotations":null}
````


---

<sub>⏱️ 1m 45s</sub>

### 💬 Copilot

Now I have a clear picture. `pytest-jubilant` doesn't exist as a separate package — `jubilant` is the library to use (it provides pytest integration directly). Let me now implement the migration.

---

<sub>⏱️ 1m 45s</sub>

### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L2-sonnet/tests/integration/conftest.py

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

<sub>⏱️ 1m 45s</sub>

### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L2-sonnet/tests/integration/test_charm.py

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

<sub>⏱️ 1m 45s</sub>

### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tests/conftest.py**

/tmp/saml-integrator-L2-sonnet/tests/conftest.py

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

<sub>⏱️ 1m 57s</sub>

### 💬 Copilot

Now I have everything I need. Let me make all the changes:

---

<sub>⏱️ 1m 57s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L2-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L2-sonnet/tests/integration/conftest.py

```
File /tmp/saml-integrator-L2-sonnet/tests/integration/conftest.py updated with changes.
```


---

<sub>⏱️ 2m 8s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L2-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L2-sonnet/tests/integration/test_charm.py

```
File /tmp/saml-integrator-L2-sonnet/tests/integration/test_charm.py updated with changes.
```


---

<sub>⏱️ 2m 13s</sub>

### 💬 Copilot

Now update the root `conftest.py` to add `--keep-models` option and keep `--charm-file`:

---

<sub>⏱️ 2m 13s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L2-sonnet/tests/conftest.py**

/tmp/saml-integrator-L2-sonnet/tests/conftest.py

```
File /tmp/saml-integrator-L2-sonnet/tests/conftest.py updated with changes.
```


---

<sub>⏱️ 2m 20s</sub>

### 💬 Copilot

Now update `pyproject.toml` to replace `juju`, `pytest-asyncio`, and `pytest-operator` with `jubilant` in both `integration` and `lint` dependency groups:

---

<sub>⏱️ 2m 20s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L2-sonnet/pyproject.toml**

/tmp/saml-integrator-L2-sonnet/pyproject.toml

```
File /tmp/saml-integrator-L2-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 2m 25s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L2-sonnet/pyproject.toml**

/tmp/saml-integrator-L2-sonnet/pyproject.toml

```
File /tmp/saml-integrator-L2-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 2m 29s</sub>

### 💬 Copilot

Now let's run the linter to verify the changes are clean:

---

<sub>⏱️ 2m 29s</sub>

### ✅ `bash`

**Lint the changed test files**

$ cd /tmp/saml-integrator-L2-sonnet && uv run --group lint ruff check tests/integration/ tests/conftest.py 2>&1

<details>
<summary>6 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: .venv
⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ allure-pytest-collection-report==0.1.0                                                                                ⠙ lxml==6.0.2                                                                                                           ⠙ ops==3.6.0                                                                                                            ⠙ pydantic==2.12.5                                                                                                      ⠙ signxml==4.3.0                                                                                                        ⠙ pydantic-core==2.41.5                                                                                                 ⠙ coverage==7.12.0                                                                                                      ⠙ coverage==7.12.0                                                                                                      ⠙ pytest==9.0.1                                                                                                         ⠙ ruff==0.14.6                                                                                                          ░░░░░░░░░░░░░░░░░░░░ [0/0] Installing wheels...                                                                         ░░░░░░░░░░░░░░░░░░░░ [0/41] Installing wheels...                                                                        ░░░░░░░░░░░░░░░░░░░░ [0/41] iniconfig==2.3.0                                                                            ░░░░░░░░░░░░░░░░░░░░ [1/41] iniconfig==2.3.0                                                                            ░░░░░░░░░░░░░░░░░░░░ [1/41] pluggy==1.6.0                                                                               ░░░░░░░░░░░░░░░░░░░░ [2/41] pluggy==1.6.0                                                                               ░░░░░░░░░░░░░░░░░░░░ [2/41] annotated-types==0.7.0                                                                      █░░░░░░░░░░░░░░░░░░░ [3/41] annotated-types==0.7.0                                                                      █░░░░░░░░░░░░░░░░░░░ [3/41] types-requests==2.32.4.20250913                                                             █░░░░░░░░░░░░░░░░░░░ [4/41] types-requests==2.32.4.20250913                                                             █░░░░░░░░░░░░░░░░░░░ [4/41] pydantic-core==2.41.5                                                                       ██░░░░░░░░░░░░░░░░░░ [5/41] pydantic-core==2.41.5                                                                       ██░░░░░░░░░░░░░░░░░░ [5/41] charset-normalizer==3.4.4                                                                   ██░░░░░░░░░░░░░░░░░░ [6/41] charset-normalizer==3.4.4                                                                   ██░░░░░░░░░░░░░░░░░░ [6/41] packaging==25.0                                                                             ███░░░░░░░░░░░░░░░░░ [7/41] packaging==25.0                                                                             ███░░░░░░░░░░░░░░░░░ [7/41] pytest==9.0.1                                                                               ███░░░░░░░░░░░░░░░░░ [8/41] pytest==9.0.1                                                                               ███░░░░░░░░░░░░░░░░░ [8/41] urllib3==2.5.0                                                                              ████░░░░░░░░░░░░░░░░ [9/41] urllib3==2.5.0                                                                              Installed 41 packages in 14ms
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 35s</sub>

### ✅ `bash`

**Type-check the changed test files**

$ cd /tmp/saml-integrator-L2-sonnet && uv run --group lint mypy tests/integration/ tests/conftest.py 2>&1

```
Success: no issues found in 5 source files
<exited with exit code 0>
```


---

<sub>⏱️ 2m 39s</sub>

### 💬 Copilot

All checks pass. Let me verify the final state of all changed files:

---

<sub>⏱️ 2m 39s</sub>

### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L2-sonnet/tests/integration/conftest.py

<details>
<summary>64 lines</summary>

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
10. import pytest
11. import yaml
12. 
13. 
14. @pytest.fixture(scope="module", name="app_name")
15. def app_name_fixture():
16.     """Provide app name from the metadata."""
17.     metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
18.     yield metadata["name"]
19. 
20. 
21. @pytest.fixture(scope="module")
22. def juju(request: pytest.FixtureRequest):
23.     """Provide a Juju instance with a temporary model."""
24.     keep_models = bool(request.config.getoption("--keep-models"))
25. 
26.     with jubilant.temp_model(keep=keep_models) as juju:
27.         juju.wait_timeout = 10 * 60
28. 
29.         yield juju
30. 
31.         if request.session.testsfailed:
32.             log = juju.debug_log(limit=1000)
33.             print(log, end="")
34. 
35. 
36. @pytest.fixture(scope="module")
37. def app(juju: jubilant.Juju, pytestconfig: pytest.Config, app_name: str):
38.     """Deploy the SAML Integrator charm for integration testing."""
39.     charm = pytestconfig.getoption("--charm-file")
40.     juju.deploy(
41.         f"./{charm}",
42.         app_name,
43.     )
44.     yield app_name
45. 
46. 
47. @pytest.fixture(scope="module")
48. def any_charm(juju: jubilant.Juju):
49.     """Deploy any-charm for integration testing of the SAML relation."""
50.     path_lib = "lib/charms/saml_integrator/v0/saml.py"
51.     saml_lib = Path(path_lib).read_text(encoding="utf8")
52.     any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
53.     src_overwrite = {
54.         "saml.py": saml_lib,
55.         "any_charm.py": any_charm_script,
56.     }
57.     juju.deploy(
58.         "any-charm",
59.         "any",
60.         channel="beta",
61.         config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
62.     )
63.     yield "any"
64.
```

</details>


---

<sub>⏱️ 2m 39s</sub>

### ✅ `view`

**/tmp/saml-integrator-L2-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L2-sonnet/tests/integration/test_charm.py

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
25.     juju.wait(jubilant.all_active, error=jubilant.any_error)
26.     status = juju.status()
27.     assert status.apps[app].units[app + "/0"].is_active
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
45.     juju.wait(jubilant.all_active, error=jubilant.any_error)
46.     status = juju.status()
47.     assert status.apps[app].units[app + "/0"].is_active
48.
```

</details>


---

<sub>⏱️ 2m 49s</sub>

### 💬 Copilot

The migration is complete. Here's a summary of all changes made:

### Changes made

**`tests/integration/conftest.py`**
- Replaced `pytest_asyncio`, `pytest_operator.OpsTest` imports with `jubilant` and `pytest`
- Replaced `@pytest_asyncio.fixture` + `async def` with `@pytest.fixture` + sync `def`
- Added `juju` fixture using `jubilant.temp_model()` context manager (10-min timeout, debug log on failure, `--keep-models` support)
- `app` fixture now takes `juju: jubilant.Juju` and calls `juju.deploy()`, yielding the app name string
- `any_charm` fixture similarly uses `juju.deploy()` and yields the string `"any"`

**`tests/integration/test_charm.py`**
- Removed `ops`, `OpsTest` imports; removed `@pytest.mark.asyncio` and `async`/`await`
- Tests now take `juju: jubilant.Juju` and `app: str` / `any_charm: str`
- `app.set_config()` → `juju.config(app, {...})`
- `model.wait_for_idle(status='active')` → `juju.wait(jubilant.all_active, error=jubilant.any_error)`
- `model.add_relation()` → `juju.integrate()`
- Status checks use `juju.status().apps[app].units[...].is_active`

**`tests/conftest.py`**
- Added `--keep-models` CLI option (used by the `juju` fixture)

**`pyproject.toml`**
- `integration` group: removed `juju`, `pytest-asyncio`, `pytest-operator`; added `jubilant`
- `lint` group: removed `pytest-asyncio`, `pytest-operator`; added `jubilant`

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
